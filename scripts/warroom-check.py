#!/usr/bin/env python3
"""War-room loop governors. The chair runs these; it does not grade itself.

    scripts/warroom-check.py stall      no ledger status moved in STALL_TICKS ticks
    scripts/warroom-check.py budget     a slice spent or exceeded its budget
    scripts/warroom-check.py meta-cap   too many builder slots hold non-milestone work
    scripts/warroom-check.py exit       every release gate has a PASS record (GO-CANDIDATE)
    scripts/warroom-check.py board      the board is short enough to read every tick

Input is docs/warroom/ticks.jsonl, one JSON object per tick:

    {"tick": 258, "date": "2026-11-10", "meta_main": "<40-hex origin/main at tick start>",
     "slots": [{"slice": "core-ci-repair", "repo": "vizra-core", "ids": ["VZ-CI-001"]}],
     "ready_undispatched": ["VZ-INSTALL-001"],
     "blocked_ids": {"VZ-MEDIA-001": "owner inbox 4a"},
     "events": [{"type": "verdict", "ids": ["VZ-CI-001"], "result": "FAIL"}]}

`ids` are ledger ids, or QUEUE-<label> for work with no ledger id. Budgets are
counted PER ID, so a re-plan, a "closing slice", a new builder or a new PR for
the same ids inherits the counters. A tick with no event is not a tick.

Ledger movement is read from git (status_records.json at each tick's
`meta_main` and at the ref), never from what a tick line claims. `exit` reads
the gate matrix, the profile and the evidence files from the ref too, so an
uncommitted or unmerged profile proves nothing.

An `owner_grant` event raises a budget only when its `ref` is "<date> #<n>",
that numbered item exists under the "## <date>" heading of OWNER-DECISIONS.md
on the ref, and the item's text names every id the grant covers.

Exit codes: 0 green, 1 red (reason printed), 2 unusable input.
"""
import argparse
import json
import os
import re
import subprocess
import sys

# ---- the numbers (one place)
STALL_TICKS = 15
MAX_VERDICTS = 4
MAX_FIX_ROUNDS = 2
MAX_REPLANS = 1
MAX_SLICE_TICKS = 12
BUILDER_SLOTS = 3
META_SLOTS = 1
BOARD_MAX_LINES = 120
BOARD_MAX_COLS = 300

TICKS = "docs/warroom/ticks.jsonl"
BOARD = "docs/plans/WARROOM-BOARD.md"
DECISIONS = "docs/warroom/OWNER-DECISIONS.md"
STATUS = "docs/evidence/ledger-generator/status_records.json"
MILESTONES = "docs/MILESTONES.md"
GATES = "docs/RELEASE_ACCEPTANCE.md"
PROFILE = "docs/quality/release-profiles/core.json"

EVENT_TYPES = {
    "dispatch", "verdict", "fix_round", "replan", "merge", "ledger", "blocked",
    "owner_grant", "sentinel_sweep", "cleanup", "deploy_rehearsal",
}
NO_ID_EVENTS = {"sentinel_sweep", "cleanup", "deploy_rehearsal"}
WORK_EVENTS = {"dispatch", "verdict", "fix_round", "replan"}
ID_RE = re.compile(r"^(VZ-[A-Z0-9]+(?:-[A-Z]+)*-\d+|QUEUE-[A-Za-z0-9._-]+)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
LEDGER_ID = re.compile(r"\bVZ-[A-Z0-9]+(?:-[A-Z]+)*-\d+\b")
CONTINUATION = re.compile(r"(?:(…|\.\.\.|–|—)|(/))(\d+)(?![\d-])")


class Unusable(Exception):
    pass


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)


def read(root, path):
    try:
        with open(os.path.join(root, path), encoding="utf-8") as handle:
            return handle.read()
    except OSError as error:
        raise Unusable("cannot read %s: %s" % (path, error))


def load_ticks(root, path):
    ticks = []
    for number, line in enumerate(read(root, path).splitlines(), 1):
        if not line.strip():
            continue
        where = "%s:%d" % (path, number)
        try:
            tick = json.loads(line)
        except ValueError as error:
            raise Unusable("%s: not JSON (%s)" % (where, error))
        if not isinstance(tick, dict) or not isinstance(tick.get("tick"), int):
            raise Unusable("%s: needs an integer 'tick'" % where)
        if ticks and tick["tick"] <= ticks[-1]["tick"]:
            raise Unusable("%s: tick numbers must increase" % where)
        if not SHA_RE.match(str(tick.get("meta_main", ""))):
            raise Unusable("%s: 'meta_main' must be a 40-hex SHA" % where)
        slots = tick.setdefault("slots", [])
        events = tick.get("events")
        if not isinstance(events, list) or not events:
            raise Unusable("%s: no events. A wake-up where nothing happened is not a tick" % where)
        for slot in slots:
            check_ids(where, slot.get("ids"), allow_empty=slot.get("kind") == "sentinel")
        for event in events:
            if event.get("type") not in EVENT_TYPES:
                raise Unusable("%s: unknown event type %r" % (where, event.get("type")))
            check_ids(where, event.get("ids", []), allow_empty=event["type"] in NO_ID_EVENTS)
            if event["type"] == "verdict" and event.get("result") not in ("PASS", "FAIL", "BLOCKED"):
                raise Unusable("%s: a verdict needs result PASS, FAIL or BLOCKED" % where)
        check_ids(where, tick.setdefault("ready_undispatched", []), allow_empty=True)
        check_ids(where, list(tick.setdefault("blocked_ids", {})), allow_empty=True)
        ticks.append(tick)
    return ticks


def check_ids(where, ids, allow_empty):
    if not isinstance(ids, list) or (not ids and not allow_empty):
        raise Unusable("%s: 'ids' must be a non-empty list" % where)
    for item in ids:
        if not isinstance(item, str) or not ID_RE.match(item):
            raise Unusable("%s: %r is neither a ledger id nor QUEUE-<label>" % (where, item))


def show(root, ref, path):
    shown = git(root, "show", "%s:%s" % (ref, path))
    if shown.returncode != 0:
        raise Unusable("cannot read %s at %s" % (path, ref))
    return shown.stdout


GRANT_REF = re.compile(r"^(\d{4}-\d{2}-\d{2}) #(\d+)$")


def decision_text(decisions, ref):
    """The text of numbered item <n> under '## <date>', or None."""
    match = GRANT_REF.match(ref if isinstance(ref, str) else "")
    if not match:
        return None
    in_section, item = False, None
    for line in decisions.splitlines():
        if line.startswith("## "):
            if item is not None:
                break
            in_section = line[3:].strip() == match.group(1)
        elif in_section:
            start = re.match(r"^(\d+)\. ", line)
            if start and item is not None:
                break
            if start and start.group(1) == match.group(2):
                item = line
            elif item is not None:
                item += "\n" + line
    return item


def records_at(root, ref):
    """{id: status} recorded at a commit. A missing file is an empty ledger."""
    shown = git(root, "show", "%s:%s" % (ref, STATUS))
    if shown.returncode != 0:
        if git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}").returncode != 0:
            raise Unusable("%s is not a commit in this repository" % ref)
        return {}
    try:
        return {r["id"]: r["status"] for r in json.loads(shown.stdout)["records"]}
    except (ValueError, KeyError, TypeError) as error:
        raise Unusable("%s at %s is unreadable: %s" % (STATUS, ref, error))


def milestone_ids(root):
    """{milestone: [ids]} from the Ledger IDs column, ranges and lists expanded."""
    result = {}
    for line in read(root, MILESTONES).splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6 or not re.match(r"^M\d+$", cells[1]):
            continue
        ids, text, pos = [], cells[4], 0
        while True:
            match = LEDGER_ID.search(text, pos)
            if not match:
                break
            prefix, digits = match.group(0).rsplit("-", 1)
            ids.append(match.group(0))
            last, pos = int(digits), match.end()
            while True:
                more = CONTINUATION.match(text, pos)
                if not more:
                    break
                value = int(more.group(3))
                span = range(last + 1, value + 1) if more.group(1) else [value]
                ids.extend("%s-%0*d" % (prefix, len(digits), n) for n in span)
                last, pos = value, more.end()
        result[cells[1]] = ids
    if not result:
        raise Unusable("%s has no milestone rows" % MILESTONES)
    return result


def slot_summary(ticks):
    held = {}
    for tick in ticks:
        for slot in tick["slots"]:
            key = "%s [%s]" % (slot.get("slice", "?"), ", ".join(slot.get("ids") or ["no id"]))
            held[key] = held.get(key, 0) + 1
    return ["  %2d tick(s)  %s" % (count, key) for key, count in sorted(held.items(), key=lambda kv: -kv[1])] \
        or ["  (no builder slot was held)"]


def cmd_stall(args):
    if args.replay:
        return replay(args)
    ticks = load_ticks(args.root, args.ticks)
    if len(ticks) < STALL_TICKS:
        print("OK: %d tick(s) recorded; the stall rule needs %d" % (len(ticks), STALL_TICKS))
        return 0
    window = ticks[-STALL_TICKS:]
    previous = None
    for tick in window:
        sha = tick["meta_main"]
        if git(args.root, "merge-base", "--is-ancestor", sha, args.ref).returncode != 0:
            raise Unusable("tick %d: meta_main %s is not on %s" % (tick["tick"], sha[:7], args.ref))
        if previous and git(args.root, "merge-base", "--is-ancestor", previous, sha).returncode != 0:
            raise Unusable("tick %d: meta_main goes backwards" % tick["tick"])
        previous = sha
    before, now = records_at(args.root, window[0]["meta_main"]), records_at(args.root, args.ref)
    if before != now:
        moved = sorted(k for k in set(before) | set(now) if before.get(k) != now.get(k))
        print("OK: ledger status moved within the last %d ticks: %s" % (STALL_TICKS, ", ".join(moved)))
        return 0
    print("STALL: no ledger status changed on %s in the last %d ticks (%d-%d). Slots were held by:"
          % (args.ref, STALL_TICKS, window[0]["tick"], window[-1]["tick"]))
    print("\n".join(slot_summary(window)))
    return 1


def replay(args):
    """Old markdown tick log: it has no per-tick SHA, so only the total is judged."""
    numbers = sorted({int(m) for m in re.findall(r"(?m)^- Tick (\d+)\b", read(args.root, args.replay))})
    if not numbers:
        raise Unusable("%s has no '- Tick N' lines" % args.replay)
    log = git(args.root, "log", "--reverse", "--format=%H", args.ref, "--", STATUS)
    if log.returncode != 0:
        raise Unusable("cannot read the history of %s on %s" % (STATUS, args.ref))
    changes, last = 0, {}
    for sha in log.stdout.split():
        current = records_at(args.root, sha)
        changes += current != last
        last = current
    label = "%d ticks logged (%d-%d), %d ledger status change(s) on %s" % (
        len(numbers), numbers[0], numbers[-1], changes, args.ref)
    if changes == 0 and len(numbers) >= STALL_TICKS:
        print("STALL: %s" % label)
        return 1
    print("OK: %s%s" % (label, "; a markdown log cannot place them on ticks" if changes else ""))
    return 0


def cmd_budget(args):
    ticks = load_ticks(args.root, args.ticks)
    decisions = None
    state, problems = {}, []

    def entry(item):
        return state.setdefault(item, {
            "verdicts": 0, "fix_rounds": 0, "replans": 0, "ticks": 0, "last_verdict": None,
            "blocked": False, "merged": False,
            "caps": {"verdicts": MAX_VERDICTS, "fix_rounds": MAX_FIX_ROUNDS,
                     "replans": MAX_REPLANS, "ticks": MAX_SLICE_TICKS}})

    for tick in ticks:
        # Slots first: a slice may be marked BLOCKED in the tick that spends it.
        for item in sorted({i for slot in tick["slots"] for i in slot.get("ids", [])}):
            e = entry(item)
            e["ticks"] += 1
            if e["blocked"]:
                problems.append("%s: holds a slot at tick %d although the slice is BLOCKED" % (item, tick["tick"]))
        for event in tick["events"]:
            kind = event["type"]
            for item in event.get("ids", []):
                e = entry(item)
                if kind == "owner_grant":
                    if decisions is None:
                        decisions = show(args.root, args.ref, DECISIONS)
                    decision = decision_text(decisions, event.get("ref"))
                    if decision is None:
                        raise Unusable("tick %d: owner_grant ref %r is not a numbered decision '<date> #<n>' in %s on %s"
                                       % (tick["tick"], event.get("ref"), DECISIONS, args.ref))
                    if not re.search(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9-])" % re.escape(item), decision):
                        raise Unusable("tick %d: decision %s does not name %s"
                                       % (tick["tick"], event["ref"], item))
                    for key in e["caps"]:
                        e["caps"][key] += int(event.get(key, 0))
                    e["blocked"] = False
                    continue
                if kind in WORK_EVENTS and e["blocked"]:
                    problems.append("%s: %s at tick %d after the slice was BLOCKED" % (item, kind, tick["tick"]))
                if kind == "verdict":
                    e["verdicts"] += 1
                    e["last_verdict"] = event["result"]
                elif kind == "fix_round":
                    e["fix_rounds"] += 1
                    e["last_verdict"] = None
                elif kind == "replan":
                    e["replans"] += 1
                elif kind == "blocked":
                    e["blocked"] = True
                elif kind == "merge":
                    e["merged"] = True

    latest = {i for slot in ticks[-1]["slots"] for i in slot.get("ids", [])} if ticks else set()
    for item in sorted(state):
        e = state[item]
        caps = e["caps"]
        over = [k for k in ("verdicts", "fix_rounds", "replans", "ticks") if e[k] > caps[k]]
        spent = (e["ticks"] >= caps["ticks"]
                 or (e["verdicts"] >= caps["verdicts"] and e["last_verdict"] != "PASS")
                 or (e["fix_rounds"] >= caps["fix_rounds"] and e["last_verdict"] == "FAIL"))
        label = "MERGED" if e["merged"] else "BLOCKED" if e["blocked"] else "OVER" if over else "SPENT" if spent else "ok"
        print("%-22s verdicts %d/%d  fix rounds %d/%d  re-plans %d/%d  ticks %d/%d  %s" % (
            item, e["verdicts"], caps["verdicts"], e["fix_rounds"], caps["fix_rounds"],
            e["replans"], caps["replans"], e["ticks"], caps["ticks"], label))
        for key in over:
            problems.append("%s: %s %d exceeds the budget of %d (counters are per id and never reset)"
                            % (item, key.replace("_", " "), e[key], caps[key]))
        if spent and not over and not e["blocked"] and not e["merged"] and item in latest \
                and e["last_verdict"] != "PASS":
            problems.append("%s: budget spent and it still holds a slot; mark it BLOCKED, keep the PR open, "
                            "put the reproducer in the owner inbox" % item)
    if problems:
        print("BUDGET: " + "\nBUDGET: ".join(problems))
        return 1
    print("OK: every slice is within budget")
    return 0


def cmd_meta_cap(args):
    ticks = load_ticks(args.root, args.ticks)
    if not ticks:
        print("OK: no ticks recorded")
        return 0
    tick = ticks[-1]
    by_milestone = milestone_ids(args.root)
    known = {i for ids in by_milestone.values() for i in ids}
    slots = tick["slots"]
    if len(slots) > BUILDER_SLOTS:
        print("META-CAP: tick %d holds %d builder slots; the limit is %d" % (tick["tick"], len(slots), BUILDER_SLOTS))
        return 1
    meta = [s for s in slots if not known & set(s.get("ids", []))]
    recorded = records_at(args.root, args.ref)
    held = {i for s in slots for i in s.get("ids", [])}
    unaccounted = []
    for name in sorted(by_milestone, key=lambda m: int(m[1:])):
        open_ids = [i for i in by_milestone[name] if recorded.get(i) != "VERIFIED"]
        if open_ids:
            unaccounted = [i for i in open_ids if i not in held and i not in tick["blocked_ids"]
                           and recorded.get(i) != "IMPLEMENTED"]
            break
    ready = sorted(set(tick["ready_undispatched"]) & known) or unaccounted
    if ready and len(meta) > META_SLOTS:
        print("META-CAP: tick %d has %d slot(s) on work with no ledger id in %s while milestone work waits (%s%s). "
              "The limit is %d:" % (tick["tick"], len(meta), MILESTONES, ", ".join(ready[:5]),
                                    ", ..." if len(ready) > 5 else "", META_SLOTS))
        print("\n".join("  %s [%s]" % (s.get("slice", "?"), ", ".join(s.get("ids") or ["no id"])) for s in meta))
        return 1
    print("OK: tick %d - %d of %d slot(s) on non-milestone work, %d milestone id(s) waiting"
          % (tick["tick"], len(meta), len(slots), len(ready)))
    return 0


def cmd_exit(args):
    # Everything is read from the ref: a working-tree profile is only a claim.
    text = show(args.root, args.ref, GATES)
    section = text.split("## Gate matrix", 1)
    if len(section) != 2:
        raise Unusable("%s has no '## Gate matrix' section" % GATES)
    gates = []
    for line in section[1].split("\n## ", 1)[0].splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 4 and cells[1] and cells[1] != "Gate" and not set(cells[1]) <= set("-"):
            gates.append(cells[1])
    if not gates:
        raise Unusable("%s lists no gates" % GATES)
    try:
        profile = json.loads(show(args.root, args.ref, args.profile))
    except ValueError as error:
        raise Unusable("%s at %s: %s" % (args.profile, args.ref, error))
    source = str(profile.get("source_sha") or "")
    frozen = bool(SHA_RE.match(source)) \
        and git(args.root, "cat-file", "-e", source + "^{commit}").returncode == 0 \
        and git(args.root, "merge-base", "--is-ancestor", source, args.ref).returncode == 0
    required = profile.get("required_feature_ids") or []
    passed = set()
    for record in profile.get("evidence") or []:
        if not isinstance(record, dict) or record.get("status") != "PASS":
            continue
        path = str(record.get("evidence_file", ""))
        inside = path.startswith("docs/evidence/") and ".." not in path.split("/")
        committed = inside and git(args.root, "cat-file", "-e", "%s:%s" % (args.ref, path)).returncode == 0
        if committed and frozen and record.get("source_sha") == source:
            passed.add(record.get("gate"))
    open_gates = [g for g in gates if g not in passed]
    recorded = records_at(args.root, args.ref)
    waiting = [i for i in required if recorded.get(i) != "VERIFIED"]
    if not frozen:
        print("OPEN: the %s profile on %s is not frozen (source_sha is not a commit on that ref)"
              % (profile.get("profile"), args.ref))
    if not required:
        print("OPEN: the profile names no required ids")
    if open_gates or waiting or not frozen or not required:
        print("OPEN: %d of %d gates have no PASS record for the frozen profile; first: %s"
              % (len(open_gates), len(gates), open_gates[0] if open_gates else "-"))
        print("OPEN: %d of %d profile ids are not VERIFIED; first: %s"
              % (len(waiting), len(required), waiting[0] if waiting else "-"))
        print("NOT AN EXIT: derive the next slice from the first open item, or stop as OWNER-BLOCKED, STALLED or BUDGET")
        return 1
    print("GO-CANDIDATE: all %d gates carry a PASS record for %s at %s. Stop for the owner's release decision."
          % (len(gates), profile.get("profile"), source[:7]))
    return 0


def cmd_board(args):
    lines = read(args.root, args.board).splitlines()
    problems = []
    if len(lines) > BOARD_MAX_LINES:
        problems.append("%d lines; the limit is %d" % (len(lines), BOARD_MAX_LINES))
    problems += ["line %d is %d characters; the limit is %d" % (n, len(line), BOARD_MAX_COLS)
                 for n, line in enumerate(lines, 1) if len(line) > BOARD_MAX_COLS]
    if problems:
        print("BOARD: %s is too big to be state. Move history to docs/warroom/.\n  %s"
              % (args.board, "\n  ".join(problems[:10])))
        return 1
    print("OK: %s is %d lines, longest %d characters" % (args.board, len(lines), max([len(l) for l in lines] or [0])))
    return 0


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=here, help="meta repo checkout (default: this script's)")
    parser.add_argument("--ref", default="origin/main", help="ref whose ledger is the truth")
    parser.add_argument("--ticks", default=TICKS)
    commands = parser.add_subparsers(dest="command")
    commands.required = True
    stall = commands.add_parser("stall")
    stall.add_argument("--replay", metavar="TICK-LOG.md")
    stall.set_defaults(run=cmd_stall)
    commands.add_parser("budget").set_defaults(run=cmd_budget)
    commands.add_parser("meta-cap").set_defaults(run=cmd_meta_cap)
    leave = commands.add_parser("exit")
    leave.add_argument("--profile", default=PROFILE)
    leave.set_defaults(run=cmd_exit)
    board = commands.add_parser("board")
    board.add_argument("--board", default=BOARD)
    board.set_defaults(run=cmd_board)
    args = parser.parse_args()
    try:
        return args.run(args)
    except Unusable as error:
        print("UNUSABLE: %s" % error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
