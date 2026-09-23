#!/usr/bin/env python3
"""The ONLINE half of "a ledger status only with evidence".

`docs/evidence/ledger-generator/status.py` (run by the generator) proves what the
tree can prove: the record's shape, the acceptance bullets it quotes and, for
VERIFIED, that the verifier's evidence file ENDS with a PASS on the recorded
verified head. What only GitHub knows is proved here, with `gh api`, for every
merge in every record of `docs/evidence/ledger-generator/status_records.json`:

  IMPLEMENTED and VERIFIED
    1. the PR is MERGED, into `main`;
    2. GitHub's head for that PR is the record's `verified_head` — the commit the
       verifier judged is the commit that was merged;
    3. GitHub's merge commit for that PR is the record's `merge_commit`;
    4. that merge commit is ON the component repo's `main` now
       (`compare/<merge_commit>...main` is `ahead` or `identical`, behind by 0).
  VERIFIED, additionally
    5. the latest `ci-required` check-run on `verified_head`, created by the
       GitHub Actions app, is `completed` / `success`. A verifier's
       "PASS (local; CI BLOCKED)" never stands in for this: VERIFIED requires CI.

Why a committed record checked online, rather than the generator calling git or
the API: the generator must be reproducible offline and byte-identical under two
locales (scripts/check-generated-ledger.sh), and the component repositories are
not checked out in this lane. A committed record is reviewable in the PR diff,
and this script re-proves it against GitHub on every run, so a record that was
true when written and later became false (a force-pushed main, a deleted PR)
turns the lane red instead of staying green.

DEFAULT-DENY. An API error, a 404, an unparseable reply, a missing `gh`, more
check-runs than one page returns, or a record the shared loader refuses — each
is a named failure and a non-zero exit. Nothing is skipped.

`--self-test` runs the committed cases in scripts/testdata/ledger-status/
against REAL GitHub facts and asserts each outcome: one record that must pass
and several that must fail for a named reason. It exists so that this checker is
never vacuous — while status_records.json holds few or no records, the
self-test is what shows the lane still refuses a bad one.

Usage:
    scripts/check-ledger-status-remote.py [--records PATH]
    scripts/check-ledger-status-remote.py --self-test
Needs `gh` authenticated (in CI: GH_TOKEN=${{ github.token }}; the component
repositories are public, so read access is enough).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "evidence", "ledger-generator"))
import status  # noqa: E402  (shared record loader: one definition of a record)

DEFAULT_RECORDS = os.path.join(ROOT, "docs", "evidence", "ledger-generator", "status_records.json")
SELF_TEST = os.path.join(ROOT, "scripts", "testdata", "ledger-status", "remote-cases.json")
TIMEOUT = 60


def gh_api(path):
    """Returns (data, error). Never raises for an API-level failure."""
    try:
        p = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github+json", path],
                           capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, f"gh api {path}: timed out after {TIMEOUT}s"
    if p.returncode != 0:
        msg = (p.stdout.strip() or p.stderr.strip()).replace("\n", " ")[:300]
        return None, f"gh api {path}: exit {p.returncode}: {msg}"
    try:
        return json.loads(p.stdout), None
    except ValueError:
        return None, f"gh api {path}: reply is not JSON"


def prove_auth():
    """Refuse to run unauthenticated, even with nothing to check.

    An unauthenticated `gh api` still reads public repositories, at 60 requests
    an hour per IP. The run would then fail later, on the rate limit, or it would
    pass only because there was nothing to ask. `rate_limit` does not count
    against the limit, and it reports 60 for an anonymous caller.
    """
    rl, err = gh_api("rate_limit")
    if err:
        return f"NOT AUTHENTICATED: {err}"
    limit = ((rl.get("resources") or {}).get("core") or {}).get("limit")
    if not isinstance(limit, int) or limit <= 60:
        return (f"NOT AUTHENTICATED: gh api rate_limit reports a core limit of {limit!r}, which is the "
                f"anonymous limit. Set GH_TOKEN (in CI: GH_TOKEN=${{{{ github.token }}}}).")
    return None


def check_merge(owner, rec_status, m, where):
    errors, notes = [], []
    repo = f"{owner}/{m['repo']}"
    head, merge = m["verified_head"], m["merge_commit"]

    pr, err = gh_api(f"repos/{repo}/pulls/{m['pr']}")
    if err:
        errors.append(f"{where}: could not read {repo}#{m['pr']}: {err}")
    else:
        if pr.get("merged") is not True:
            errors.append(f"{where}: {repo}#{m['pr']} was NOT MERGED (state {pr.get('state')!r})")
        base = (pr.get("base") or {}).get("ref")
        if base != "main":
            errors.append(f"{where}: {repo}#{m['pr']} targets {base!r}, not main")
        gh_head = (pr.get("head") or {}).get("sha")
        if gh_head != head:
            errors.append(f"{where}: {repo}#{m['pr']} head is {gh_head}, but the record's verified_head is "
                          f"{head}; the verified head must be the head that was merged")
        if pr.get("merge_commit_sha") != merge:
            errors.append(f"{where}: {repo}#{m['pr']} merge_commit_sha is {pr.get('merge_commit_sha')}, but the "
                          f"record says {merge}")

    cmp_, err = gh_api(f"repos/{repo}/compare/{merge}...main")
    if err:
        errors.append(f"{where}: could not place merge commit {merge} relative to {repo} main: {err}")
    else:
        st, behind = cmp_.get("status"), cmp_.get("behind_by")
        if st in ("ahead", "identical") and behind == 0:
            notes.append(f"{merge[:12]} is on {repo} main (compare: {st}, main ahead by {cmp_.get('ahead_by')})")
        else:
            errors.append(f"{where}: merge commit {merge} is NOT on {repo} main (compare {merge[:12]}...main: "
                          f"{st}, behind_by {behind})")

    if rec_status == "VERIFIED":
        runs, err = gh_api(f"repos/{repo}/commits/{head}/check-runs?check_name=ci-required&filter=latest&per_page=100")
        if err:
            errors.append(f"{where}: could not read ci-required on {head}: {err}")
        else:
            total = runs.get("total_count")
            items = [r for r in runs.get("check_runs", []) if (r.get("app") or {}).get("slug") == "github-actions"]
            if not isinstance(total, int) or total > len(runs.get("check_runs", [])):
                errors.append(f"{where}: ci-required on {head}: {total} runs reported, more than one page; refused")
            elif not items:
                errors.append(f"{where}: no ci-required check-run from GitHub Actions on {head}; VERIFIED requires "
                              f"ci-required green on the verified head")
            else:
                latest = max(items, key=lambda r: (r.get("started_at") or "", r.get("id") or 0))
                if latest.get("status") != "completed" or latest.get("conclusion") != "success":
                    errors.append(f"{where}: latest ci-required on {head} (check-run {latest.get('id')}) is "
                                  f"{latest.get('status')}/{latest.get('conclusion')}, not completed/success")
                else:
                    notes.append(f"ci-required on {head[:12]}: completed/success (check-run {latest.get('id')})")
    return errors, notes


def check_doc(doc):
    errors, notes = [], []
    owner = doc["github_owner"]
    for i, rec in enumerate(doc["records"]):
        label = f"status record #{i} ({rec['id']} {rec['status']})"
        for j, m in enumerate(rec["merges"]):
            e, n = check_merge(owner, rec["status"], m, f"{label}: merges[{j}] {m['repo']}#{m['pr']}")
            errors += e
            notes += [f"{label}: {x}" for x in n]
    return errors, notes


def load(path):
    doc, errors = status.load_records(path)
    return doc, errors


def run_records(path):
    doc, errors = load(path)
    if errors:
        print("\n".join(errors))
        print(f"REFUSED: {path} does not load; nothing was checked against GitHub.")
        return 1
    if not doc["records"]:
        print(f"0 status records in {os.path.relpath(path, ROOT)}: no entry claims IMPLEMENTED or VERIFIED, "
              f"so there is no merge to prove. (The self-test step exercises this checker.)")
        return 0
    errors, notes = check_doc(doc)
    for n in notes:
        print("ok  " + n)
    if errors:
        print("\n".join(errors))
        print(f"FAIL: {len(errors)} problem(s) across {len(doc['records'])} record(s)")
        return 1
    print(f"OK: {len(doc['records'])} status record(s) proved against GitHub")
    return 0


def run_self_test():
    with open(SELF_TEST, encoding="utf-8") as fh:
        cases = json.load(fh)["cases"]
    failed = 0
    import tempfile
    for case in cases:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(case["records_doc"], tf)
            path = tf.name
        try:
            doc, errors = load(path)
        finally:
            os.unlink(path)
        if errors:
            print(f"SELF-TEST {case['name']}: FAIL — the case itself does not load: {errors}")
            failed += 1
            continue
        errors, _notes = check_doc(doc)
        expect = case["expect"]
        if expect == "pass":
            ok = not errors
            print(f"SELF-TEST {case['name']}: expected pass, got {'pass' if ok else 'RED'}"
                  + ("" if ok else f" — {errors}"))
        else:
            missing = [s for s in expect if not any(s in e for e in errors)]
            ok = bool(errors) and not missing
            print(f"SELF-TEST {case['name']}: expected red naming {expect}; "
                  + ("red, every reason named" if ok else f"MISSING {missing} in {errors}"))
            for e in errors:
                print(f"    {e}")
        failed += 0 if ok else 1
    print(f"self-test: {len(cases) - failed}/{len(cases)} cases behaved as expected")
    return 1 if failed else 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--records", default=DEFAULT_RECORDS)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if shutil.which("gh") is None:
        print("BLOCKED: `gh` is not installed; the merge facts cannot be proved, and an unproved status is refused.")
        return 2
    auth = prove_auth()
    if auth:
        print(auth)
        return 2
    return run_self_test() if args.self_test else run_records(args.records)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
