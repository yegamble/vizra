# Execution plan: VZ-CI-001 N1 — a skipped required test fails the job (vizra-user)

## Context
Repo yegamble/vizra-user, base origin/main 9f7c639, branch `fix/ci-001-skip-fails`, PR https://github.com/yegamble/vizra-user/pull/17.
Gap: skips in `frontend` (vitest) and `e2e` (Playwright) were caught only by count floors / `passWithNoTests:false`; one skip under the floor passed.

## Acceptance
- Any vitest `skipped|pending|todo` (it.skip, describe.skip, test.todo, skipIf) fails `frontend`.
- Any Playwright `skipped` outcome (test.skip, test.fixme, conditional) fails `e2e`, unless listed with a reason in `scripts/ci/skip-allowlist.json` (EMPTY).
- Missing / unparseable / zero-test report and unknown status fail closed.
- No new required check name. Non-goal: changing floors.

## Implementation
- `scripts/ci/check-no-skipped-tests.mjs` (vitest|playwright) + `scripts/ci/skip-allowlist.json` (`[]`).
- `package.json`: `test` adds `--reporter=default --reporter=json --outputFile.json=test-results/vitest-results.json` (vitest 5.0.3 `--help` confirms both flags); `check:skips` after `test` in `ci`.
- `frontend-ci.yml`: explicit step after `npm run ci` re-runs the vitest check.
- `e2e`: checker invoked from `scripts/ci/check-coverage-floor-ran.mjs` (existing step) — `.github/workflows/e2e.yml` is digest-pinned by `docs/evidence/VZ-FOUND-008/mutation-digests.txt` (D17c) and its lane guard reserves `playwright-report` in step `run:` for the redact step, so e2e.yml is NOT edited.
- Canary fixtures run via `harness-canary.mjs`, after the floor step, not in `results.json`; no allowlist entry needed.

## Verification
Red-first: checker tests failed 8/15 before the script existed. Commands below via council/quiet.sh.

## Progress and evidence
See PR #17 body for command table, red/green run URLs.

## Blockers and handoff
Verifier budget for VZ-CI-001 spent; awaits owner grant. Playwright red path demonstrated by fixture tests only (no e2e CI red run).
