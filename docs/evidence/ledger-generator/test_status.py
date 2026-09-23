"""Unit tests for status.py — the offline half of "a status only with evidence".

Run from this directory:  python3 -m unittest -v test_status
Each case builds its own throwaway tree (issues + evidence) so it never reads or
writes the real ledger. The red/green demonstrations against the REAL generator
and the REAL GitHub facts are docs/evidence/ledger-status/demo.sh.
"""
import copy
import json
import os
import tempfile
import unittest

import status

HEAD = "0cc906ed35b804b18acac5dc74f0c9f2fda57e94"
MERGE = "f1972e8226e42a2bf837bd45e12f5f447dd3a92f"
OTHER = "66b3f3d50c56499432cbf6174661cbaa6bacbfea"
EVID = "docs/evidence/warroom/x-VERIFY.md"

ISSUE = """# VZ-ISSUE-900: test

**Ledger IDs:** VZ-TEST-001, VZ-TEST-003 (VZ-TEST-003…005)

## Outcome
- not an acceptance bullet

## Acceptance (observable)
- the thing works (demonstrated)
- the other thing fails closed

## Verification
- not an acceptance bullet either
"""


def req(rid, ui=(), api=()):
    return {"id": rid, "surfaces": {"api": list(api), "ui": list(ui), "cli": []},
            "implementation_status": "PLANNED", "verification_status": "UNVERIFIED",
            "merge_status": "NOT_STARTED", "release_status": "NOT_RELEASED", "evidence": [], "test_ids": []}


def record(status_="IMPLEMENTED", rid="VZ-TEST-001", **merge_over):
    m = {"repo": "vizra-core", "pr": 8, "verified_head": HEAD, "merge_commit": MERGE}
    if status_ == "VERIFIED":
        m["evidence_file"] = EVID
    m.update(merge_over)
    return {"id": rid, "status": status_, "rationale": "because",
            "acceptance": [{"issue": "docs/issues/VZ-ISSUE-900.md", "bullet": "the thing works (demonstrated)"}],
            "merges": [m]}


class Tree(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "docs/issues"))
        os.makedirs(os.path.join(self.root, "docs/evidence/warroom"))
        self.write("docs/issues/VZ-ISSUE-900.md", ISSUE)
        self.write(EVID, "body\nFINAL VERDICT: FAIL — SHA " + OTHER + "\n\nFINAL VERDICT: PASS (local; CI BLOCKED) — SHA " + HEAD + "\n\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def load(self, records):
        path = os.path.join(self.root, "records.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"schema": 1, "github_owner": "yegamble", "records": records}, fh)
        return status.load_records(path)

    def run_all(self, records, reqs=None):
        reqs = reqs if reqs is not None else [req("VZ-TEST-001"), req("VZ-TEST-002")]
        doc, errors = self.load(records)
        if errors:
            return reqs, errors
        return reqs, status.apply_records(reqs, doc, self.root)

    def assertRefused(self, errors, needle):
        self.assertTrue(any(needle in e for e in errors), f"{needle!r} not in {errors}")


class DslDefaults(Tree):
    def test_clean_dsl_passes(self):
        self.assertEqual(status.check_dsl_defaults([req("VZ-TEST-001")]), [])

    def test_hand_asserted_verified_in_a_section_is_refused(self):
        r = req("VZ-TEST-001"); r["implementation_status"] = "VERIFIED"
        self.assertRefused(status.check_dsl_defaults([r]), "HAND-ASSERTED implementation_status 'VERIFIED'")

    def test_str_subclass_that_compares_equal_is_refused(self):
        # meta PR #6 verify, probe 2d: `!=` is overridable; the check must not use it.
        class _S(str):
            def __ne__(self, other):
                return False

            def __eq__(self, other):
                return True
        r = req("VZ-TEST-001"); r["implementation_status"] = _S("VERIFIED")
        self.assertRefused(status.check_dsl_defaults([r]), "HAND-ASSERTED implementation_status")

    def test_core_req_keys_equal_the_output_checks_allowlist(self):
        # The out-of-process output check hard-codes the key set core.req emits;
        # this keeps the two in step so neither can drift silently.
        import importlib.util
        import core
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts",
                            "check-ledger-status-output.py")
        spec = importlib.util.spec_from_file_location("output_check", path)
        out = importlib.util.module_from_spec(spec); spec.loader.exec_module(out)
        before = len(core.REQS)
        core.req("VZ-KEYSET-999", "t", "o", "a", core.SAFE, [], success=["s"], evidence=["e"])
        try:
            emitted = core.REQS[-1]
            self.assertEqual(tuple(emitted), out.FEATURE_KEYS)
            self.assertEqual(tuple(emitted["cases"]), out.CASES_KEYS)
            self.assertEqual(tuple(emitted["surfaces"]), out.SURFACES_KEYS)
        finally:
            del core.REQS[before:]
            core.SEEN.discard("VZ-KEYSET-999")

    def test_hand_asserted_release_status_is_refused(self):
        r = req("VZ-TEST-001"); r["release_status"] = "RELEASED"
        self.assertRefused(status.check_dsl_defaults([r]), "HAND-ASSERTED release_status")

    def test_list_subclass_evidence_is_refused(self):
        # the `ev != []` form is overridable exactly like the str case
        class _L(list):
            def __ne__(self, other):
                return False
        r = req("VZ-TEST-001"); r["evidence"] = _L([{"x": 1}])
        self.assertRefused(status.check_dsl_defaults([r]), "HAND-ASSERTED evidence")

    def test_hand_asserted_test_ids_are_refused(self):
        r = req("VZ-TEST-001"); r["test_ids"] = ["VERIFIED"]
        self.assertRefused(status.check_dsl_defaults([r]), "HAND-ASSERTED test_ids")

    def test_duplicate_keys_in_the_records_file_are_refused(self):
        path = os.path.join(self.root, "dup.json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write('{"schema": 1, "github_owner": "yegamble", "records": [], "records": []}')
        _, errors = status.load_records(path)
        self.assertRefused(errors, "duplicate key(s) ['records']")

    def test_hand_asserted_evidence_is_refused(self):
        r = req("VZ-TEST-001"); r["evidence"] = [{"x": 1}]
        self.assertRefused(status.check_dsl_defaults([r]), "HAND-ASSERTED evidence")


class RecordShape(Tree):
    def test_unknown_status_is_refused_by_name(self):
        for bad in ("IN_PROGRESS", "DONE", "verified", "VERIFIED_AT_SHA", "MERGED", "", None):
            _, errors = self.run_all([record(status_=bad)])
            self.assertRefused(errors, f"status {bad!r} is REFUSED")

    def test_verified_with_no_evidence_is_refused(self):
        rec = record("VERIFIED"); del rec["merges"][0]["evidence_file"]
        _, errors = self.run_all([rec])
        self.assertRefused(errors, "VERIFIED with NO EVIDENCE")

    def test_implemented_with_an_evidence_file_is_refused(self):
        _, errors = self.run_all([record(evidence_file=EVID)])
        self.assertRefused(errors, "IMPLEMENTED carries an evidence_file")

    def test_abbreviated_sha_is_refused(self):
        _, errors = self.run_all([record(merge_commit=MERGE[:7])])
        self.assertRefused(errors, "is not a full 40-character lowercase SHA")

    def test_unknown_key_is_refused(self):
        rec = record(); rec["release_status"] = "RELEASED"
        _, errors = self.run_all([rec])
        self.assertRefused(errors, "unknown key(s) ['release_status']")

    def test_no_merges_is_refused(self):
        rec = record(); rec["merges"] = []
        _, errors = self.run_all([rec])
        self.assertRefused(errors, "a status needs a merge")

    def test_two_records_for_one_id_are_refused(self):
        _, errors = self.run_all([record(), record()])
        self.assertRefused(errors, "a second record for VZ-TEST-001")

    def test_missing_records_file_is_refused(self):
        _, errors = status.load_records(os.path.join(self.root, "nope.json"))
        self.assertRefused(errors, "MISSING STATUS RECORDS")

    def test_unknown_repo_is_refused(self):
        _, errors = self.run_all([record(repo="vizra-core-fork")])
        self.assertRefused(errors, "repo 'vizra-core-fork' is not one of")


class Evidence(Tree):
    def test_verified_passes_and_is_written(self):
        reqs, errors = self.run_all([record("VERIFIED")])
        self.assertEqual(errors, [])
        r = reqs[0]
        self.assertEqual((r["implementation_status"], r["verification_status"], r["merge_status"], r["release_status"]),
                         ("VERIFIED", "VERIFIED_AT_SHA", "MERGED", "NOT_RELEASED"))
        self.assertEqual(r["evidence"][1]["final_verdict"], "FINAL VERDICT: PASS (local; CI BLOCKED) — SHA " + HEAD)
        self.assertEqual(reqs[1]["implementation_status"], "PLANNED")

    def test_implemented_passes_and_is_written(self):
        reqs, errors = self.run_all([record()])
        self.assertEqual(errors, [])
        self.assertEqual((reqs[0]["implementation_status"], reqs[0]["verification_status"]), ("IMPLEMENTED", "UNVERIFIED"))

    def test_verdict_sha_mismatch_is_refused(self):
        _, errors = self.run_all([record("VERIFIED", verified_head=OTHER)])
        self.assertRefused(errors, "VERDICT SHA MISMATCH")

    def test_fail_as_final_line_is_refused(self):
        self.write(EVID, "FINAL VERDICT: PASS — SHA " + HEAD + "\nFINAL VERDICT: FAIL — SHA " + HEAD + "\n")
        _, errors = self.run_all([record("VERIFIED")])
        self.assertRefused(errors, "does not END with a PASS verdict")

    def test_pass_not_on_the_final_line_is_refused(self):
        self.write(EVID, "FINAL VERDICT: PASS — SHA " + HEAD + "\nA later note.\n")
        _, errors = self.run_all([record("VERIFIED")])
        self.assertRefused(errors, "does not END with a PASS verdict")

    def test_abbreviated_verdict_sha_is_refused(self):
        self.write(EVID, "FINAL VERDICT: PASS — SHA " + HEAD[:8] + "…\n")
        _, errors = self.run_all([record("VERIFIED")])
        self.assertRefused(errors, "does not END with a PASS verdict")

    def test_free_text_qualifier_is_refused(self):
        # meta PR #6 verify, FINDING 4: a qualifier can negate the PASS it decorates.
        for q in ("superseded \u2014 FAIL on re-run", "NOT; retracted", "local; CI green", "local"):
            self.write(EVID, "FINAL VERDICT: PASS (" + q + ") \u2014 SHA " + HEAD + "\n")
            _, errors = self.run_all([record("VERIFIED")])
            self.assertRefused(errors, "is NOT ALLOWLISTED")

    def test_unqualified_pass_is_admitted(self):
        self.write(EVID, "FINAL VERDICT: PASS \u2014 SHA " + HEAD + "\n")
        _, errors = self.run_all([record("VERIFIED")])
        self.assertEqual(errors, [])

    def test_hyphen_instead_of_em_dash_is_refused(self):
        self.write(EVID, "FINAL VERDICT: PASS - SHA " + HEAD + "\n")
        _, errors = self.run_all([record("VERIFIED")])
        self.assertRefused(errors, "does not END with a PASS verdict")

    def test_missing_evidence_file_is_refused(self):
        os.remove(os.path.join(self.root, EVID))
        _, errors = self.run_all([record("VERIFIED")])
        self.assertRefused(errors, "MISSING EVIDENCE FILE")

    def test_evidence_outside_warroom_is_refused(self):
        _, errors = self.run_all([record("VERIFIED", evidence_file="docs/issues/VZ-ISSUE-900.md")])
        self.assertRefused(errors, "must be a relative path under docs/evidence/warroom/")
        _, errors = self.run_all([record("VERIFIED", evidence_file="docs/evidence/warroom/../../issues/VZ-ISSUE-900.md")])
        self.assertRefused(errors, "must be a relative path under docs/evidence/warroom/")

    def test_symlinked_evidence_is_refused(self):
        self.write("elsewhere.md", "FINAL VERDICT: PASS — SHA " + HEAD + "\n")
        os.symlink(os.path.join(self.root, "elsewhere.md"), os.path.join(self.root, "docs/evidence/warroom/link.md"))
        _, errors = self.run_all([record("VERIFIED", evidence_file="docs/evidence/warroom/link.md")])
        self.assertRefused(errors, "is a symlink or escapes")

    def test_nothing_is_written_when_any_record_fails(self):
        reqs, errors = self.run_all([record(), record(rid="VZ-TEST-002", merge_commit="nope")])
        self.assertTrue(errors)
        self.assertEqual(reqs[0]["implementation_status"], "PLANNED")


class Floors(Tree):
    def test_ui_surface_needs_a_user_merge(self):
        _, errors = self.run_all([record()], [req("VZ-TEST-001", ui=["/setup/claim"])])
        self.assertRefused(errors, "names no vizra-user merge")

    def test_api_surface_needs_a_core_merge(self):
        _, errors = self.run_all([record(repo="vizra-user")], [req("VZ-TEST-001", api=["GET /x"])])
        self.assertRefused(errors, "names no vizra-core merge")

    def test_every_scheduling_issue_must_be_cited(self):
        self.write("docs/issues/VZ-ISSUE-901.md", "**Ledger IDs:** VZ-TEST-001\n\n## Acceptance (observable)\n- later part\n")
        _, errors = self.run_all([record()])
        self.assertRefused(errors, "docs/issues/VZ-ISSUE-901.md schedules VZ-TEST-001")

    def test_tagged_bullet_must_name_this_requirement(self):
        self.write("docs/issues/VZ-ISSUE-902.md", "**Ledger IDs:** VZ-TEST-002\n\n## Acceptance (observable)\n"
                   "- Part one (VZ-TEST-001): not this one\n- Part two (VZ-TEST-002): this one\n")
        rec = record(rid="VZ-TEST-002")
        rec["acceptance"] = [{"issue": "docs/issues/VZ-ISSUE-902.md", "bullet": "Part one (VZ-TEST-001): not this one"}]
        _, errors = self.run_all([rec])
        self.assertRefused(errors, "the cited bullet does not name VZ-TEST-002")
        rec["acceptance"][0]["bullet"] = "Part two (VZ-TEST-002): this one"
        _, errors = self.run_all([rec])
        self.assertEqual(errors, [])

    def test_bullet_must_be_verbatim_and_in_acceptance(self):
        rec = record(); rec["acceptance"][0]["bullet"] = "not an acceptance bullet"
        _, errors = self.run_all([rec])
        self.assertRefused(errors, "not found verbatim")

    def test_unknown_requirement_is_refused(self):
        _, errors = self.run_all([record(rid="VZ-TEST-999")])
        self.assertRefused(errors, "no requirement VZ-TEST-999")

    def test_ledger_ids_ranges_expand(self):
        self.assertEqual(status.issue_ledger_ids(ISSUE),
                         {"VZ-TEST-001", "VZ-TEST-003", "VZ-TEST-004", "VZ-TEST-005"})
        self.assertEqual(status.issue_ledger_ids("**Ledger IDs:** VZ-CI-001/002/004\n"),
                         {"VZ-CI-001", "VZ-CI-002", "VZ-CI-004"})


if __name__ == "__main__":
    unittest.main()
