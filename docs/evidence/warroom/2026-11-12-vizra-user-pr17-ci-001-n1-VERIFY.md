# VERIFY — vizra-user PR #17, VZ-CI-001 N1 (vizra-user part): a skipped required test fails the job

- PR: https://github.com/yegamble/vizra-user/pull/17 — head `e6748c22015368bcaf77e579440febb91af4f0d1` (matched `gh pr view --json headRefOid`, state OPEN)
- Verifier: independent (did not write the code). 5th of 6 VZ-CI-001 verdicts.
- Environment: macOS darwin, Node v24.21.0 (nvm), fresh clone in `/tmp/vzv-user-pr17-abymgH` (deleted after).

## Clean-clone runs at e6748c2
| Command | Result |
|---|---|
| `npm ci` | exit 0 |
| `npm run test` | exit 0, JSON report written to test-results/vitest-results.json |
| `npm run check:skips` | exit 0 — "898 vitest test(s), none skipped/todo/fixme" |
| `npx vitest run scripts/ci/check-no-skipped-tests.test.mjs` | 1 file, **15 passed** (15), 0 skipped |
| `npm run check:hygiene` | exit 0 (352 sources, 17 mutation-digest lines match) |

## Mutations (each applied in the clone, then restored; `git status` clean afterwards)
| Mutation | vitest exit | check:skips exit | Reason printed |
|---|---|---|---|
| (a) `it.skip(` on a test | 0 | **1** | `1 of 898 ... skipped: ... passes a clean report` |
| `it.todo(` | 0 | **1** | `todo: ...` |
| (b) `it.skipIf(true)(` | 0 | **1** | `skipped: ...` |
| (b) `describe.skip(` | 0 | **1** | `8 of 898 ... skipped: ...` |
| (b) `test.todo("vzv todo")` in a new file | 0 | **1** | `1 of 900 ... todo: scripts/ci/vzv.test.mjs > vzv todo` |
| (c) Playwright **fixture** report (hand-written JSON, not a real e2e run): 1 expected + 1 `skipped` | — | **1** | `skipped/fixme: [chromium] b.spec.ts > sk` |
| (c) same fixture with both `expected` | — | 0 | green control |
| (c) fixture `{"suites":[]}` | — | **1** | zero tests: lane did not really run |
| (d) drop `check:skips` from `ci` | read, not run | — | `.github/workflows/frontend-ci.yml` step "No unit test was skipped (VZ-CI-001 N1)" runs `node scripts/ci/check-no-skipped-tests.mjs vitest test-results/vitest-results.json` in job `frontend` (required, `frontend` in required-checks.txt), after `npm run ci`, no `if:` / `continue-on-error`. The GREEN log shows the check printed twice (npm script + extra step). |

Playwright wiring: `check-coverage-floor-ran.mjs` spawns the checker on the report and exits 1 on non-zero; e2e.yml step "The coverage floor was actually satisfied" runs it. Allowlist `scripts/ci/skip-allowlist.json` is `[]`.

## GitHub CI
- RED run 43245135598 (frontend-ci, headSha 3f8077e3…, failure): log shows `check-no-skipped-tests: 1 of 898 vitest test(s) did not run ... skipped: lib/health.test.ts > healthPayload claims no dependency readiness ...` then `exit code 1`. Confirmed.
- GREEN at e6748c2: contract-ci, frontend-ci (43245351685), e2e (43245351787), ci-guard, supply-chain, ci-required (43245351838), docker-build — all completed success. frontend log: 898 vitest, none skipped (×2). e2e log: `42 playwright test(s), none skipped/todo/fixme`, floor 21/9 per project.
- ci-required manifest: frontend, contract, ?guard, ?docker-build, e2e — every one ran on this SHA and succeeded; ci-required ended `OK: every required check on e6748c22… concluded success` (15:16:09, after e2e finished 15:16:01). No listed lane missing.

## Diff audit
Six files: workflow step added, package.json (`test` adds json reporter, `ci` adds check:skips), checker + 15-case test, empty allowlist, floor script spawns checker. No assertion removed or weakened, no skips, no generated files, no secrets. `test-results/` is gitignored (no stale committed report).

## Findings
BLOCKING: none.

FOLLOW-UP F-1 (low): the Playwright skip check is only reached through `check-coverage-floor-ran.mjs`; an edit removing the spawn there drops N1 for e2e with no second enforcer (unlike the vitest lane's extra workflow step). Not exploitable in today's tree; hardening only.

FINAL VERDICT: PASS — SHA e6748c22015368bcaf77e579440febb91af4f0d1
