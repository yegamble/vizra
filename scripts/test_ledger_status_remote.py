#!/usr/bin/env python3
"""Unit tests for scripts/check-ledger-status-remote.py with `gh_api` injected.

The self-test (`--self-test`) proves the checker against REAL GitHub facts, but
some guards have no real counterexample to point at. For example, no repository
here has a `ci-required` check-run created by an app other than GitHub Actions.
These tests replace the module-level `gh_api` with a stub, so each guard is
exercised on its own and a deleted guard turns a named test red.

Run from the repository root:  python3 scripts/test_ledger_status_remote.py -v
"""
import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("remote", os.path.join(HERE, "check-ledger-status-remote.py"))
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)

HEAD = "0cc906ed35b804b18acac5dc74f0c9f2fda57e94"
MERGE = "f1972e8226e42a2bf837bd45e12f5f447dd3a92f"
MERGE_ENTRY = {"repo": "vizra-core", "pr": 8, "verified_head": HEAD, "merge_commit": MERGE}


def run(slug, conclusion="success", started="2026-09-23T17:00:00Z", rid=1, status="completed"):
    return {"id": rid, "name": "ci-required", "status": status, "conclusion": conclusion,
            "started_at": started, "app": {"slug": slug}}


class Stub:
    def __init__(self, base="main", runs=None, compare="ahead", rate_limit=5000, total=None, contents=None):
        self.pull = {"merged": True, "state": "closed", "base": {"ref": base}, "head": {"sha": HEAD},
                     "merge_commit_sha": MERGE}
        self.runs = runs if runs is not None else [run("github-actions")]
        self.compare = {"status": compare, "behind_by": 0 if compare in ("ahead", "identical") else 3,
                        "ahead_by": 1}
        self.rate_limit = rate_limit
        self.total = total
        self.contents = contents  # None -> 404; else the blob sha main reports

    def __call__(self, path):
        if path.endswith("/pulls/8"):
            return self.pull, None
        if "/compare/" in path:
            return self.compare, None
        if "/check-runs" in path:
            return {"total_count": self.total if self.total is not None else len(self.runs),
                    "check_runs": self.runs}, None
        if "/contents/" in path:
            if self.contents is None:
                return None, "gh api contents: exit 1: HTTP 404"
            return {"sha": self.contents}, None
        if path == "rate_limit":
            if self.rate_limit is None:
                return None, "gh api rate_limit: exit 1: HTTP 401"
            return {"resources": {"core": {"limit": self.rate_limit}}}, None
        return None, f"unexpected path {path}"


class RemoteGuards(unittest.TestCase):
    def setUp(self):
        self.orig = remote.gh_api

    def tearDown(self):
        remote.gh_api = self.orig

    def check(self, stub, status="VERIFIED"):
        remote.gh_api = stub
        errors, _ = remote.check_merge("yegamble", status, dict(MERGE_ENTRY), "t")
        return errors

    def assertNamed(self, errors, needle):
        self.assertTrue(any(needle in e for e in errors), f"{needle!r} not in {errors}")

    def test_true_facts_pass(self):
        self.assertEqual(self.check(Stub()), [])

    def test_ci_required_from_a_non_actions_app_is_refused(self):
        errors = self.check(Stub(runs=[run("some-other-app")]))
        self.assertNamed(errors, "no ci-required check-run from GitHub Actions")

    def test_non_actions_success_does_not_mask_an_actions_failure(self):
        errors = self.check(Stub(runs=[run("github-actions", "failure", rid=1),
                                       run("some-other-app", "success", "2026-09-23T18:00:00Z", rid=2)]))
        self.assertNamed(errors, "not completed/success")

    def test_latest_actions_run_decides(self):
        errors = self.check(Stub(runs=[run("github-actions", "success", "2026-09-23T10:00:00Z", rid=1),
                                       run("github-actions", "failure", "2026-09-23T11:00:00Z", rid=2)]))
        self.assertNamed(errors, "(check-run 2) is completed/failure")

    def test_in_progress_is_not_success(self):
        errors = self.check(Stub(runs=[run("github-actions", None, status="in_progress")]))
        self.assertNamed(errors, "is in_progress/None")

    def test_base_other_than_main_is_refused(self):
        errors = self.check(Stub(base="chore/m0-meta-baseline"), status="IMPLEMENTED")
        self.assertNamed(errors, "targets 'chore/m0-meta-baseline', not main")

    def test_merge_commit_not_on_main_is_refused(self):
        errors = self.check(Stub(compare="diverged"), status="IMPLEMENTED")
        self.assertNamed(errors, "is NOT on yegamble/vizra-core main")

    def test_implemented_does_not_ask_for_ci(self):
        self.assertEqual(self.check(Stub(runs=[]), status="IMPLEMENTED"), [])

    def test_more_than_one_page_of_check_runs_is_refused(self):
        errors = self.check(Stub(total=150))
        self.assertNamed(errors, "more than one page; refused")

    def test_evidence_must_be_on_meta_main_byte_identical(self):
        rel = "docs/evidence/warroom/2026-09-21-meta-pr3-validate-lane-VERIFY.md"
        blob = remote.git_blob_sha(os.path.join(remote.ROOT, rel))
        remote.gh_api = Stub(contents=None)
        self.assertTrue(any("EVIDENCE NOT ON META MAIN" in e for e in remote.check_evidence_on_main("yegamble", rel, "t")))
        remote.gh_api = Stub(contents="0" * 40)
        self.assertTrue(any("EVIDENCE DIFFERS FROM META MAIN" in e for e in remote.check_evidence_on_main("yegamble", rel, "t")))
        remote.gh_api = Stub(contents=blob)
        self.assertEqual(remote.check_evidence_on_main("yegamble", rel, "t"), [])

    def test_verified_record_consults_the_evidence_check(self):
        doc = {"schema": 1, "github_owner": "yegamble", "records": [{
            "id": "VZ-X-001", "status": "VERIFIED", "rationale": "r",
            "acceptance": [{"issue": "i", "bullet": "b"}],
            "merges": [dict(MERGE_ENTRY, evidence_file="docs/evidence/warroom/nope-VERIFY.md")]}]}
        remote.gh_api = Stub(contents=None)
        errors, _ = remote.check_doc(doc)
        self.assertTrue(any("EVIDENCE NOT ON META MAIN" in e for e in errors), errors)

    def test_main_proves_auth_even_with_zero_records(self):
        # deleting the prove_auth() CALL in main() (not just the function) must be caught
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            json.dump({"schema": 1, "github_owner": "yegamble", "records": []}, tf)
        orig_which = remote.shutil.which
        remote.shutil.which = lambda name: "/stub/gh"
        try:
            remote.gh_api = Stub(rate_limit=60)
            self.assertEqual(remote.main(["--records", tf.name]), 2)
            remote.gh_api = Stub(rate_limit=5000)
            self.assertEqual(remote.main(["--records", tf.name]), 0)
        finally:
            remote.shutil.which = orig_which
            os.unlink(tf.name)

    def test_anonymous_gh_is_refused(self):
        remote.gh_api = Stub(rate_limit=60)
        self.assertIn("NOT AUTHENTICATED", remote.prove_auth() or "")
        remote.gh_api = Stub(rate_limit=None)
        self.assertIn("NOT AUTHENTICATED", remote.prove_auth() or "")
        remote.gh_api = Stub(rate_limit=1000)
        self.assertIsNone(remote.prove_auth())


if __name__ == "__main__":
    unittest.main()
