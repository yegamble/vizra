# Verify: meta PR #10, the self-test fixture must not depend on a file staying off main (queue 2x)

- Repo: `yegamble/vizra` (meta). PR #10, branch `fix/m1-selftest-fixture`.
- Head verified: `33d435cf8c8bb99bf76a581a1565969121667192`. `gh api repos/yegamble/vizra/pulls/10` returned this head at the start and at the end of the run. Base `608ffbfc09b23d04e1797a64cd2f923b0d17877d`, which equals `origin/main` and is the merge-base.
- Verifier: an independent war-room verifier that did not write the change, working in a fresh clone under the scratchpad (`mktemp -d …/vzv-meta-pr10-XXXXXX`). Worktrees at the base and at the head were used for mutations. Nothing was committed or pushed, and the scratch directory was deleted at the end.
- Environment: macOS (Darwin 25.5.0) arm64, Python 3.9.6, gh 2.98.0, Docker 29.8.0, Compose 5.5.1, PyYAML 6.0.3. `GH_TOKEN` came from `gh auth token` and was never printed. `gh api rate_limit` showed an authenticated core limit of 5000, so the run was not rate-limited.
- Date: 2026-09-23.

## 1. Diff scope

`git diff 608ffbf..33d435c`: one commit, one file, `scripts/testdata/ledger-status/remote-cases.json`, with 3 insertions and 3 deletions. Only the case `evidence-not-on-meta-main` changed, in three fields:
- `why`: text rewritten;
- `expect[0]`: `…/2026-09-21-vizra-core-pr8-m1a-owner-claim-VERIFY.md` changed to `…/SELF-TEST-FIXTURE-NEVER-ON-MAIN-VERIFY.md`;
- `records_doc.records[0].merges[0].evidence_file`: the same path change.

The PR changes no checker code, workflow, manifest, CODEOWNERS or baseline. **Held.**

## 2. Red before, green after

| Tree | Command | Exit | Result |
|---|---|---|---|
| base `608ffbf` | `./scripts/check-ledger-status-remote.py --self-test` | 1 | `self-test: 9/10`. `evidence-not-on-meta-main: … MISSING […owner-claim-VERIFY.md] in []`: no error at all, because the file is now on main with identical bytes |
| head `33d435c` | same | 0 | `self-test: 10/10`. `evidence-not-on-meta-main`: red, every reason named. It is the only error in that case: `EVIDENCE NOT ON META MAIN — docs/evidence/warroom/SELF-TEST-FIXTURE-NEVER-ON-MAIN-VERIFY.md could not be read … {"message":"Not Found"…` |

No other error appears in the head case. So the `why` claim of "true merge and CI facts" for core#8 holds today: the merge, head, merge commit and `ci-required` checks produce no error. **Held.**

## 3. The case can still fail (R11)

All mutations were made in a scratch worktree at the head against the real GitHub API unless stated otherwise. Each one was restored, and `git status` was clean afterwards.

| # | Mutation | Exit | Self-test | Why it went red |
|---|---|---|---|---|
| M1 | `expect` changed to name `…/SOME-OTHER-PATH-VERIFY.md` | 1 | 9/10 | `MISSING […SOME-OTHER-PATH…]`. The real error names the reserved path |
| M3 | case pointed at `…pr8-m1a-owner-claim-VERIFY.md` (`evidence_file` and `expect`), a file on main (blob `7c40ba4`) and byte-identical in the tree | 1 | 9/10 | `MISSING […] in []`. The online rule-6 check finds the file on main, so the expected failure does not happen |
| M4 | M3, plus the local copy altered (one line appended) | 1 | 9/10 | the error is `EVIDENCE DIFFERS FROM META MAIN`, not the expected `NOT ON META MAIN` |
| M5 | M3, plus the local copy deleted | 1 | 9/10 | the error is `… is on meta main but missing from this tree`, not the expected string |
| M6 | checker mutated in scratch: the `check_evidence_on_main(...)` call in `check_doc` replaced with `pass` | 1 | 9/10 | `MISSING […reserved path…]`. This shows the online evidence-on-main check alone makes the case red |
| M0 | all restored | 0 | 10/10 | — |

**Builder's scratch driver (M2): judged sound, and reproduced independently.** `check_evidence_on_main` looks up the module-global `gh_api` at call time. Replacing `chk.gh_api` on the loaded module therefore reaches the real code path, and every other call still passes through to the real API. My own driver (`driver.py` in scratch, not committed) did the same with a pass-through for everything except the `contents/<reserved path>` call:
- control, pass-through: exit 0, 10/10;
- M7b, reserved path "present on main" and absent from the tree: exit 1, 9/10, `… is on meta main but missing from this tree`;
- M7a, reserved path "present on main" and a byte-identical local file created: exit 1, 9/10, no error at all.

M3, M4 and M5 cover the same three states with a real on-main file and no wrapper. The state of "the fixture path appears on main" is therefore covered both by simulation and by real API facts. **Held.**

One more probe, **M7e**: the driver returned a transient non-404 error, `HTTP 500`, for the reserved-path contents call. The result was exit 0, 10/10: the case passes. See FINDING 1. This behaviour predates the PR and is not introduced by it.

## 4. Full validate lane at the head (local, `33d435c`)

| Command | Exit | Counts |
|---|---|---|
| `./scripts/ci-required-guard.sh` | 0 | manifest `[validate]`; 2 workflows parsed; 4 action refs pinned; fixtures 6/6, 7/7, 10/10 at their floors |
| `./scripts/check-generated-ledger.sh` | 0 | 192 requirements; the ledger reproduces byte-for-byte under UTF-8 and C/POSIX |
| `./scripts/check-ledger-status-output.py` | 0 | 192 entries, 0 carry a status, 0 records |
| `(cd docs/evidence/ledger-generator && python3 -m unittest -v test_status)` | 0 | Ran 38 tests, OK, 0 skipped |
| `python3 scripts/test_ledger_status_remote.py -v` | 0 | Ran 13 tests, OK, 0 skipped |
| `./scripts/check-ledger-status-remote.py --self-test` | 0 | 10/10 |
| `./scripts/check-ledger-status-remote.py` (records) | 0 | 0 status records, so there is no merge to prove |
| `bash docs/evidence/ledger-status/demo.sh` | 0 | `demo: 61 passed, 0 failed` |
| `./scripts/check-quality-json.py` | 0 | 4 JSON files; 192 ids; 204 distinct references resolve |
| `./scripts/check-doc-links.py` | 0 | 18 relative links across 152 markdown files; 8 external URLs recorded and not fetched |
| `./scripts/compose-render.py --all --out build/compose-models` | 0 | 13 shapes |
| `./scripts/check-compose-topology.py build/compose-models` | 0 | 13 shapes; 27 rules, 0 violations; 2 known-false probes named |
| `./scripts/check-config-coverage.py build/compose-models` | 0 | 34 component keys, 58 template keys, 0 violations |
| `./scripts/check-template-claims.py` | 0 | 10 files, 16 references |
| `bash docs/evidence/compose-topology/demo.sh` | 0 | `RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`; "tree is clean - every mutation was reverted" |

No step was skipped. The word "skip" does not occur in the transcript.

## 5. GitHub CI on `33d435c`

`gh api repos/yegamble/vizra/commits/33d435cf8c8bb99bf76a581a1565969121667192/check-runs` reports `total_count` 3:
- `validate`: completed/success, app `github-actions`, check-run 107409888604 (run 35928705232);
- `ci-required`: completed/success, app `github-actions`, check-run 107409888657 (run 35928705324);
- `GitGuardian Security Checks`: success.

The validate log records `PR head SHA … 33d435c…`, `PR base SHA … 608ffbf…`, `Ran 38 tests`, `Ran 13 tests`, `self-test: 10/10`, `demo: 61 passed, 0 failed` and `RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`.

The `ci-required` log reads the manifest `.github/required-checks.txt` = `[validate]`, polls until `validate: success`, then prints `ci-required: every required check succeeded on 33d435cf…`. The manifest lane `validate` actually ran on this SHA. It is not a listed-but-absent lane. **Held.**

## 6. R24: fixtures must not depend on mutable facts

Note: at the time of this run, `docs/sentinel/RULES.md` has no R24 row. The file ends at R23, both on this checkout and in the file as committed. I applied the brief's definition.

- **Can the reserved path become true silently?** No, not for the case's purpose. The checker reads only `contents/<path>?ref=main`, and `git log --all` shows the path has never existed on any ref. If the path were committed to main in any form (identical, differing, or not in the tested tree), the self-test goes red, as shown by M3, M4, M5, M7a and M7b. A commit on another branch cannot affect a `ref=main` read. Nothing enforces "never committed", but the failure it would cause is loud, not silent.
- **Residual exposure within the changed case:** the case passes on any failure of that one contents read, not only on a 404 (M7e). See FINDING 1. The case's other facts (core#8 merged, head `0cc906e`, merge `f1972e8`, `ci-required` green) are immutable, short of a force-push, and extra errors are tolerated in a red case, so they cannot make the case vacuous.
- **Outside this diff, for the chair and not held against this PR:**
  - `pr-never-merged` depends on `yegamble/vizra-user#4` staying unmerged. It is closed, not merged, and could in principle be reopened.
  - `core8-verified-true-facts` depends on `2026-09-21-meta-pr3-validate-lane-VERIFY.md` staying byte-identical between the tree and main. A later edit to that file on main turns the case red for stale local branches. CI tests the merge ref, so CI would see identical bytes.
  - `no-ci-required-on-the-head` also cites the owner-claim file that is now on main. Its expected reason is unaffected.
  - The builder says the other mutable fixtures were reported to the chair as a list. UNVERIFIED: I did not see that list.

## 7. R1: `why` text and PR body

- The `why` claims that the first version "named a real records-branch file, which went stale when queue 2u landed it on main (meta #7)". Confirmed: meta #7 merged as `608ffbf`, and `git show --stat 608ffbf` adds `…pr8-m1a-owner-claim-VERIFY.md`.
- "must never be committed anywhere" is normative, not a claim of enforcement. It is acceptable given the loud failure shown above.
- The PR body says validate went red for every meta PR, first seen on #8, run 35926922450. Confirmed: that run is `failure` on head `3572218…`, which is #8's head, and its failed log shows `self-test: 9/10` on this case.
- Before and after 9/10 → 10/10: reproduced. M1 red at 9/10: reproduced. M2a/M2b red and the control at 10/10: reproduced by my own driver and by real on-main facts.
- The local lane table (38/13 tests, 61/0, 95/0, 27 rules/0 violations, 192 entries): reproduced, including the compose demo's 95/0.
- "So a future commit to the reserved path turns the self-test red. It cannot make the case silently vacuous." This holds as worded, for a commit. It does not cover a transient read error (FINDING 1), and the body does not claim that it does.

## Findings

```
FINDING 1: evidence-not-on-meta-main passes on ANY failed contents read, not only on "Not Found"
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra
  files:     scripts/check-ledger-status-remote.py:163-168 (check_evidence_on_main), scripts/testdata/ledger-status/remote-cases.json:296-298 (expect)
  requirements: none yet (ledger-status self-test hygiene)

Observed:
  The checker emits the same "EVIDENCE NOT ON META MAIN — <path> could not be read … (<err>)" for any gh_api
  error. The case's expect pins only that prefix and the path. A scratch driver that made the reserved-path
  contents call return "HTTP 500" gave `self-test: 10/10`, exit 0 (M7e).

Failure:
  If that one read fails transiently (5xx, timeout), the case reports that it behaved as expected. This is
  harmless for the product rule, which stays default-deny and refuses, but the case does not then prove the
  404 branch. It was true before this PR and is not introduced by it.

Perspective:
  developer

Recommendation:
  In a follow-up, add a second expect string for the 404, e.g. "\"message\":\"Not Found\"", or "HTTP 404"
  if the gh output is stable, so that only a genuine absence satisfies the case.

Acceptance criteria:
  With the driver returning HTTP 500 for the reserved-path contents call, the self-test is red at 9/10.
  Against the real API it is 10/10.

Tests:
  scripts/check-ledger-status-remote.py --self-test, plus a driver that wraps gh_api (see §3 M7e).

Cross-repo implications:
  core: none | user: none | search: none | meta: fixture only

Challenge:
  The self-test's job is to show the checker refuses. A 500 is also a refusal, so pinning 404 adds a
  dependency on gh's error-text format, which is itself a mutable fact (R24).
```

No blocking or required finding. No privacy leak, secret, skip, weakened assertion, generated-file edit or manifest change was found in the diff.

## What did not run

- No browser or UI check: this is not a UI slice.
- The builder's own M2 driver was not re-run. It is not in the PR or the tree. I reproduced its three states with my own driver and with real on-main facts.

## Verdict

PASS. Every in-scope check reproduced; CI `validate` and `ci-required` are green on this SHA; the head did not move; the one finding is a NIT, not blocking, and not introduced by this PR.

FINAL VERDICT: PASS — SHA 33d435cf8c8bb99bf76a581a1565969121667192
