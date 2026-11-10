"""Red and green cases for scripts/warroom-check.py, on throwaway git repos.

    python3 -m unittest discover -s tests/warroom -p 'test_*.py'
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(REPO, "scripts", "warroom-check.py")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
STATUS = "docs/evidence/ledger-generator/status_records.json"
MILESTONES = """| # | Milestone | Exit criterion | Ledger IDs | Depends on |
|---|---|---|---|---|
| M0 | Foundation | x | VZ-FOUND-001…003, VZ-CI-001/004 | Q-001…Q-004 |
| M1 | Golden path | x | VZ-AUTH-001 | M0 |
"""
GATES = """# Release acceptance
## Gate matrix
| Gate | Required proof |
|---|---|
| Clean install | a |
| Backup/restore | b |

## Verdict
"""
SHA = "a" * 40


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="vz-warroom-check-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.git("init", "-q", "-b", "main")
        self.write("docs/MILESTONES.md", MILESTONES)
        self.write("docs/RELEASE_ACCEPTANCE.md", GATES)
        self.write("docs/warroom/OWNER-DECISIONS.md", "2026-11-10 grant G-1\n")
        self.shas = [self.ledger({})]

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), env=ENV, check=True,
                              stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()

    def write(self, path, text):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def ledger(self, records):
        body = {"schema": 1, "github_owner": "x",
                "records": [{"id": k, "status": v} for k, v in sorted(records.items())]}
        self.write(STATUS, json.dumps(body))
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "ledger %d" % len(records))
        return self.git("rev-parse", "HEAD")

    def ticks(self, lines):
        self.write("docs/warroom/ticks.jsonl", "".join(json.dumps(line) + "\n" for line in lines))

    def tick(self, number, sha=None, slots=(), events=None, **extra):
        slot_list = [{"slice": name, "repo": "vizra-core", "ids": ids} for name, ids in slots]
        line = {"tick": number, "meta_main": sha or self.shas[-1], "slots": slot_list,
                "events": events if events is not None else [{"type": "dispatch", "ids": ["QUEUE-x"]}]}
        line.update(extra)
        return line

    def run_check(self, *args):
        done = subprocess.run([sys.executable, SCRIPT, "--root", self.root, "--ref", "main"] + list(args),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return done.returncode, done.stdout + done.stderr


class Stall(Fixture):
    def test_red_fifteen_ticks_and_no_ledger_change(self):
        self.ticks([self.tick(n, slots=[("ci-guard", ["QUEUE-2o"])]) for n in range(1, 16)])
        code, out = self.run_check("stall")
        self.assertEqual(code, 1, out)
        self.assertIn("STALL: no ledger status changed on main in the last 15 ticks (1-15)", out)
        self.assertIn("15 tick(s)  ci-guard [QUEUE-2o]", out)

    def test_green_a_change_inside_the_window(self):
        before = self.shas[-1]
        self.shas.append(self.ledger({"VZ-FOUND-001": "IMPLEMENTED"}))
        self.ticks([self.tick(n, sha=before if n < 10 else self.shas[-1]) for n in range(1, 16)])
        code, out = self.run_check("stall")
        self.assertEqual(code, 0, out)
        self.assertIn("VZ-FOUND-001", out)

    def test_red_a_change_before_the_window_does_not_count(self):
        self.shas.append(self.ledger({"VZ-FOUND-001": "IMPLEMENTED"}))
        self.ticks([self.tick(n) for n in range(1, 17)])
        self.assertEqual(self.run_check("stall")[0], 1)

    def test_green_implemented_to_verified_is_movement(self):
        self.shas.append(self.ledger({"VZ-FOUND-001": "IMPLEMENTED"}))
        self.ticks([self.tick(n) for n in range(1, 16)])
        self.ledger({"VZ-FOUND-001": "VERIFIED"})
        self.assertEqual(self.run_check("stall")[0], 0)

    def test_green_fewer_than_fifteen_ticks(self):
        self.ticks([self.tick(n) for n in range(1, 15)])
        self.assertEqual(self.run_check("stall")[0], 0)

    def test_a_claimed_sha_that_is_not_on_the_ref_is_refused(self):
        self.ticks([self.tick(n, sha=SHA) for n in range(1, 16)])
        code, out = self.run_check("stall")
        self.assertEqual(code, 2, out)
        self.assertIn("is not on main", out)

    def test_an_idle_wake_up_is_not_a_tick(self):
        self.ticks([self.tick(1, events=[])])
        code, out = self.run_check("stall")
        self.assertEqual(code, 2, out)
        self.assertIn("not a tick", out)

    def test_replay_red_then_green(self):
        self.write("LOG.md", "".join("- Tick %d — ci guard\n" % n for n in range(20, 0, -1)))
        code, out = self.run_check("stall", "--replay", "LOG.md")
        self.assertEqual(code, 1, out)
        self.assertIn("20 ticks logged (1-20), 0 ledger status change(s)", out)
        self.ledger({"VZ-FOUND-001": "IMPLEMENTED"})
        self.assertEqual(self.run_check("stall", "--replay", "LOG.md")[0], 0)


class Budget(Fixture):
    IDS = ["VZ-FOUND-001"]

    def event(self, kind, **extra):
        return dict({"type": kind, "ids": self.IDS}, **extra)

    def test_green_within_budget(self):
        self.ticks([
            self.tick(1, slots=[("a", self.IDS)], events=[self.event("dispatch")]),
            self.tick(2, slots=[("a", self.IDS)], events=[self.event("verdict", result="FAIL"), self.event("fix_round")]),
            self.tick(3, events=[self.event("verdict", result="PASS"), self.event("merge")]),
        ])
        code, out = self.run_check("budget")
        self.assertEqual(code, 0, out)
        self.assertIn("verdicts 2/4  fix rounds 1/2  re-plans 0/1  ticks 2/12  MERGED", out)

    def test_red_a_replan_does_not_reset_the_counters(self):
        fail = self.event("verdict", result="FAIL")
        self.ticks([
            self.tick(1, slots=[("a", self.IDS)], events=[fail, self.event("fix_round")]),
            self.tick(2, slots=[("a", self.IDS)], events=[fail, self.event("fix_round")]),
            self.tick(3, slots=[("a-replanned", self.IDS)], events=[fail, self.event("replan")]),
            # A new slice name and a new PR for the same id: a third fix round.
            self.tick(4, slots=[("a-closing-slice", self.IDS)], events=[fail, self.event("fix_round")]),
        ])
        code, out = self.run_check("budget")
        self.assertEqual(code, 1, out)
        self.assertIn("VZ-FOUND-001: fix rounds 3 exceeds the budget of 2", out)

    def test_red_second_replan_fifth_verdict_and_thirteenth_tick(self):
        self.ticks([self.tick(1, events=[self.event("replan"), self.event("replan")])])
        self.assertIn("replans 2 exceeds the budget of 1", self.run_check("budget")[1])
        self.ticks([self.tick(1, events=[self.event("verdict", result="FAIL")] * 5)])
        self.assertIn("verdicts 5 exceeds the budget of 4", self.run_check("budget")[1])
        self.ticks([self.tick(n, slots=[("a", self.IDS)]) for n in range(1, 14)])
        code, out = self.run_check("budget")
        self.assertEqual(code, 1, out)
        self.assertIn("ticks 13 exceeds the budget of 12", out)

    def test_red_spent_slice_still_holding_a_slot(self):
        self.ticks([self.tick(n, slots=[("a", self.IDS)]) for n in range(1, 13)])
        code, out = self.run_check("budget")
        self.assertEqual(code, 1, out)
        self.assertIn("budget spent and it still holds a slot", out)

    def test_green_spent_slice_marked_blocked_then_red_if_worked_again(self):
        lines = [self.tick(n, slots=[("a", self.IDS)]) for n in range(1, 12)]
        lines.append(self.tick(12, slots=[("a", self.IDS)], events=[self.event("blocked")]))
        self.ticks(lines)
        self.assertEqual(self.run_check("budget")[0], 0)
        self.ticks(lines + [self.tick(13, events=[self.event("dispatch")])])
        code, out = self.run_check("budget")
        self.assertEqual(code, 1, out)
        self.assertIn("dispatch at tick 13 after the slice was BLOCKED", out)

    def test_owner_grant_must_cite_a_recorded_decision(self):
        lines = [self.tick(1, events=[self.event("verdict", result="FAIL")] * 4 + [self.event("blocked")])]
        grant = self.event("owner_grant", ref="grant G-1", verdicts=1)
        self.ticks(lines + [self.tick(2, events=[grant, self.event("verdict", result="PASS")])])
        self.assertEqual(self.run_check("budget")[0], 0)
        grant["ref"] = "grant G-404"
        self.ticks(lines + [self.tick(2, events=[grant])])
        self.assertEqual(self.run_check("budget")[0], 2)


class MetaCap(Fixture):
    META = [("guard-a", ["QUEUE-a"]), ("guard-b", ["QUEUE-b"])]

    def test_red_two_meta_slots_while_milestone_work_waits(self):
        self.ticks([self.tick(1, slots=self.META, ready_undispatched=["VZ-FOUND-002"])])
        code, out = self.run_check("meta-cap")
        self.assertEqual(code, 1, out)
        self.assertIn("2 slot(s) on work with no ledger id", out)
        self.assertIn("VZ-FOUND-002", out)

    def test_red_an_empty_ready_claim_is_checked_against_the_milestones(self):
        self.ticks([self.tick(1, slots=self.META)])
        code, out = self.run_check("meta-cap")
        self.assertEqual(code, 1, out)
        self.assertIn("VZ-FOUND-001, VZ-FOUND-002, VZ-FOUND-003, VZ-CI-001, VZ-CI-004", out)

    def test_green_one_meta_slot(self):
        self.ticks([self.tick(1, slots=[self.META[0], ("m0", ["VZ-FOUND-001"])])])
        self.assertEqual(self.run_check("meta-cap")[0], 0)

    def test_green_two_meta_slots_when_everything_open_is_blocked_or_held(self):
        blocked = {i: "owner inbox" for i in ["VZ-FOUND-002", "VZ-FOUND-003", "VZ-CI-001", "VZ-CI-004"]}
        self.ledger({"VZ-FOUND-001": "IMPLEMENTED"})
        self.ticks([self.tick(1, slots=self.META, blocked_ids=blocked)])
        code, out = self.run_check("meta-cap")
        self.assertEqual(code, 0, out)

    def test_red_four_builder_slots(self):
        self.ticks([self.tick(1, slots=[("s%d" % n, ["VZ-FOUND-001"]) for n in range(4)])])
        code, out = self.run_check("meta-cap")
        self.assertEqual(code, 1, out)
        self.assertIn("4 builder slots", out)

    def test_ranges_and_lists_expand_like_the_real_file(self):
        self.ledger({i: "VERIFIED" for i in
                     ["VZ-FOUND-001", "VZ-FOUND-002", "VZ-FOUND-003", "VZ-CI-001", "VZ-CI-004"]})
        self.ticks([self.tick(1, slots=self.META)])
        code, out = self.run_check("meta-cap")
        self.assertEqual(code, 1, out)
        self.assertIn("(VZ-AUTH-001)", out)


class Exit(Fixture):
    def profile(self, evidence, source_sha=SHA):
        self.write("docs/quality/release-profiles/core.json", json.dumps({
            "profile": "core", "source_sha": source_sha, "required_feature_ids": ["VZ-FOUND-001"],
            "evidence": evidence}))

    def record(self, gate, **extra):
        self.write("docs/evidence/release/%s.md" % gate[:5], "x")
        return dict({"gate": gate, "status": "PASS", "source_sha": SHA,
                     "evidence_file": "docs/evidence/release/%s.md" % gate[:5]}, **extra)

    def test_red_an_empty_queue_with_gates_open_is_not_an_exit(self):
        self.profile([self.record("Clean install")])
        code, out = self.run_check("exit")
        self.assertEqual(code, 1, out)
        self.assertIn("1 of 2 gates have no PASS record for the frozen profile; first: Backup/restore", out)
        self.assertIn("NOT AN EXIT", out)

    def test_green_go_candidate(self):
        self.profile([self.record("Clean install"), self.record("Backup/restore")])
        self.ledger({"VZ-FOUND-001": "VERIFIED"})
        code, out = self.run_check("exit")
        self.assertEqual(code, 0, out)
        self.assertIn("GO-CANDIDATE: all 2 gates", out)

    def test_red_records_that_prove_nothing(self):
        self.ledger({"VZ-FOUND-001": "VERIFIED"})
        good = self.record("Clean install")
        for bad in (self.record("Backup/restore", status="UNVERIFIED"),
                    self.record("Backup/restore", evidence_file="docs/evidence/release/missing.md"),
                    self.record("Backup/restore", source_sha="b" * 40)):
            self.profile([good, bad])
            self.assertEqual(self.run_check("exit")[0], 1, bad)
        self.profile([good, self.record("Backup/restore")], source_sha=None)
        self.assertIn("not frozen", self.run_check("exit")[1])

    def test_red_gates_pass_but_a_profile_id_is_not_verified(self):
        self.profile([self.record("Clean install"), self.record("Backup/restore")])
        self.ledger({"VZ-FOUND-001": "IMPLEMENTED"})
        code, out = self.run_check("exit")
        self.assertEqual(code, 1, out)
        self.assertIn("1 of 1 profile ids are not VERIFIED; first: VZ-FOUND-001", out)


class Board(Fixture):
    def test_red_and_green(self):
        self.write("docs/plans/WARROOM-BOARD.md", "ok\n" * 120)
        self.assertEqual(self.run_check("board")[0], 0)
        self.write("docs/plans/WARROOM-BOARD.md", "ok\n" * 121)
        code, out = self.run_check("board")
        self.assertEqual(code, 1, out)
        self.assertIn("121 lines; the limit is 120", out)
        self.write("docs/plans/WARROOM-BOARD.md", "x" * 301 + "\n")
        code, out = self.run_check("board")
        self.assertEqual(code, 1, out)
        self.assertIn("line 1 is 301 characters; the limit is 300", out)


class RealRepository(unittest.TestCase):
    def test_the_real_milestones_expand_to_the_ledger(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("warroom_check", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        counts = {name: len(ids) for name, ids in module.milestone_ids(REPO).items()}
        self.assertEqual(counts, {"M0": 24, "M1": 23, "M2": 25, "M3": 36, "M4": 19, "M5": 51, "M6": 13, "M7": 0})
        with open(os.path.join(REPO, "docs/quality/features.json"), encoding="utf-8") as handle:
            ledger = {f["id"] for f in json.load(handle)["features"]}
        self.assertEqual({i for ids in module.milestone_ids(REPO).values() for i in ids} - ledger, set())


if __name__ == "__main__":
    unittest.main()
