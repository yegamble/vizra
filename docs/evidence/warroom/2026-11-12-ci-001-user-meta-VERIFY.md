# VZ-CI-001 — vizra-user#14 + vizra#27 independent verification (2026-11-12)

Verifier: vizra-verifier (independent; wrote none of this). Heads checked at start and end via `gh pr view --json headRefOid`: user 50b1cd1417aa82a8b6a60285ced123f794ab0ae8, meta cb500ae55a455bac7e6ce4fb8d446c976cc467cf. Fresh clones in a mktemp dir, macOS bash 3.2. Base = merge-base with origin/main (user 0bb8dc6…, meta e91e28e…), passed as BASE_SHA the way the workflows pass it.

## A. Diff scope
- user: 4 files (+182/-0): guard script, 7 test cases, ci-guard.yml step (BASE_SHA = PR base / merge_group base / before), manifest header. No lane removed or loosened. `?name` removal, demotion name->?name and rename of `?` lanes are all covered (cases 7, 7b).
- meta: 11 files (+279/-3): guard, runner, 3 test scripts, ci-required.yml step, validate.yml now uses run-unittest-noskip.py for both unittest invocations (`grep -n unittest .github/workflows` shows only lines 183-185; no other python test call). The runner fails on skips, xfail, unexpected success and 0 tests run, and on failures. Both demo.sh files fail when PASSED=0.

## B. Mutations (exit code of the guard as CI runs it)
| # | user | meta |
|---|---|---|
|baseline|0 OK|0 OK|
|1 delete required line|1 "contract: removed … without a tombstone"|1 "REMOVED WITHOUT TOMBSTONE: validate"|
|2 valid tombstone|0 (?docker-build)|0 (synthetic base lane `extra`, --base-file); deleting `extra` with no tombstone -> 1|
|2b floor lane tombstone|1 e2e floor|1 FLOOR LANE validate|
|3 tombstone with no reason|1|1|
|4 comment out|1 contract|1 validate|
|5 delete earlier tombstone|1 "earlier tombstone was deleted"|1 TOMBSTONE DELETED|
|6 shallow depth=1, no env, origin unreachable|1 BASE MANIFEST UNAVAILABLE|1 BASE MANIFEST UNAVAILABLE|
|7 frontend -> ?frontend|1 demoted|n/a|
|7b rename ?guard -> ?guard2|1|n/a|
|8 rename required job|1 check-required-manifest.sh "contract" undefined|1 ci-required-guard.sh "validate" has no job|
|9 continue-on-error: true on required job|1 (ci-guard grep step matches contract-ci.yml:44)|1 ci-required-guard.sh rejects it|
|10 @unittest.skip in test_status.py, exact validate command|n/a|1 "noskip: FAIL skipped: …"|

## C. N1 / R1
- user N1: vitest `passWithNoTests:false`, Playwright `forbidOnly` in CI; an `it.skip` is caught only by count floors. The PR body says outright that this gap is **open** ("vitest .skip gap | open"), so it does not claim N1 for skip -> FOLLOW-UP, not blocking. No skip mutation was run (time limit).
- R1: user require-checks_test.sh covers the empty manifest (l.492), the empty FLOOR (l.572), CHECK_SHA length and the stale-copy check (l.747). meta: test_ci_required_select.sh (11 cases) and test_run_unittest_noskip.sh empty-discover / no-args.

## D. Tests
- meta: test_required_tombstones 16/16, test_ci_required_select 11/11, test_run_unittest_noskip 8/8, all exit 0.
- user: run locally without node_modules it failed 149 (ERR_MODULE_NOT_FOUND typescript). That is an environment gap on my side, not a test result. The CI guard job at head reports `require-checks_test: 235 cases, 242 assertions, 0 failed`.

## E. CI
- user head 50b1cd1: ci-required, frontend, contract, guard, e2e all success; ?docker-build did not run (path-filtered); deps-scan/image-scan failed (not in the manifest).
- meta head cb500ae: ci-required success, validate success. The noskip runner reported 38 tests and then 13, with 0 skipped.
- Breakage: user red job 131240724894 shows "?docker-build: removed from the manifest without a tombstone" at the step "Retired lanes carry a tombstone"; green job 131241794089 shows OK at that step (5 base lanes). Meta red run 43236941621 (48c455f) shows "REMOVED WITHOUT TOMBSTONE: validate" at the tombstone step; green restore 43237088814 (321a060) passed.

## Findings
- BLOCKING: none.
- FOLLOW-UP (user): a vitest/Playwright `.skip` is caught only by count floors. FOLLOW-UP (meta): test_run_unittest_noskip.sh has no unexpected-success case; the code handles it.

PR VERDICT vizra-user#14: PASS — SHA 50b1cd1417aa82a8b6a60285ced123f794ab0ae8
PR VERDICT vizra#27: PASS — SHA cb500ae55a455bac7e6ce4fb8d446c976cc467cf
FINAL VERDICT: PASS — SHA 50b1cd1417aa82a8b6a60285ced123f794ab0ae8 cb500ae55a455bac7e6ce4fb8d446c976cc467cf
