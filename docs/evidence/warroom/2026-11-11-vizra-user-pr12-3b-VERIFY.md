# vizra-user PR #12 (slice 3b, VZ-FOUND-002 user half) — independent verification

- PR: https://github.com/yegamble/vizra-user/pull/12
- SHA verified: a3b8f942d566513b155971384bd2ee6b161d4520 (PR head at start: same; at end: a3b8f942d566513b155971384bd2ee6b161d4520)
- vizra-core main at verification: 5f615d74e840b23d2201b1d78dd89abfef07701b (not moved; equals manifest source_commit)
- Date: 2026-11-11. Verifier did not write this code. Fresh clone in a private mktemp dir, deleted afterwards.

## Environment
- macOS (darwin 25.5.0), local Node **v25.9.0** / npm 11.12.1. `.nvmrc` says **22.14.0**; no Node 22 is installed on this machine, so local runs are on a different major (vitest 5.0.1 printed EBADENGINE for 25.x). CI lanes use `node-version-file: .nvmrc`; the CI frontend log is the on-version evidence.
- `npm ci` from the lockfile: exit 0, 416 packages. Binaries run from ./node_modules/.bin only.

## Commands (clean tree at the SHA)
| Command | Exit | Result |
|---|---|---|
| `git diff origin/main...HEAD --stat` | 0 | 4 files, +567/-9: contracts/manifest.json, contracts/vizra-core/api/openapi.yaml, lib/api/contract-operations.test.ts, lib/api/generated.ts |
| `cmp` vendored spec vs core@5f615d7:api/openapi.yaml | 0 | byte-identical, no normalisation; sha256 2ac3280056871c48477b0238a398dc23afbd3afec5ff0ad170b27c5cc373c1d6, 18521 bytes, blob 8bab7e9d518511a1cae864459f1ff8e177ccb3b1 — all three equal the manifest |
| `node scripts/vendor-contract.mjs --from ../core` (ref main = 5f615d7) then `npm run codegen` | 0 / 0 | `git status --short` empty after each (S2) |
| `npm run lint` | 0 | clean |
| `./node_modules/.bin/tsc --noEmit` | 0 | clean |
| `./node_modules/.bin/vitest run` | 0 | 23 files, 818 tests passed, 0 skipped, 0 failed |
| `npm run check:hygiene` | 0 | 324 sources, 17 mutation-digest lines match |
| `npm run check:contract` | 0 | matches manifest and generator 7.13.0 |
| `node scripts/check-spec-refs.mjs`, `node scripts/check-manifest.mjs` | 0 / 0 | |

## Results
**A — PASS.** Exactly the four claimed files. No change to package.json, lockfile, .github, scripts, harness or AGENTS.md. Only additions to the test surface; nothing weakened.

**B — PASS.** See table. Re-vendoring from my own core clone and regenerating leaves no diff. (One verifier slip, not a finding: a first run with `--ref <sha>` wrote source_ref=<sha> into the manifest as the tool documents; stashed and re-run with the default ref.)

**C — PASS (mutations mine, each restored, tree clean and green afterwards).**
| # | Mutation | check:contract | new test (vitest) | tsc |
|---|---|---|---|---|
| 1 | delete `/api/v1/setup/claim-owner` block (84 lines) from vendored spec, no regen | exit 1 "openapi.yaml is not the blob the manifest names" | exit 1, 1 failed | 0 |
| 2 | hand-edit one line of lib/api/generated.ts (N1) | exit 1 "generated.ts is not what the contract generates" | exit 1, 1 failed | 0 |
| 3a | remove getSchemaz from EXPECTED_OPERATIONS | 0 (not its job) | exit 1, 3 failed | exit 2, TS2322 at line 46 |
| 3b | add a seventh (GET /api/v1/photos listPhotos) | 0 | exit 1, 3 failed | exit 2, TS2322 at line 48 |
| 4 | collection | — | `frontend` lane runs `npm run ci` → `vitest run`; vitest.config include `**/*.test.ts`, `passWithNoTests: false`. CI log of frontend job 130663895770 on this SHA shows `✓ lib/api/contract-operations.test.ts (4 tests)`, 23 files / 818 tests. Not a false green. | |

**D — PASS (hard gate).** The diff contains no fetch, no credential, no claim token, no signed URL. grep for claimOwner / getSetupClaimStatus / claim-owner / claim-status outside node_modules finds only lib/api/generated.ts and the new test; no product code or e2e calls either operation.

**E — PASS locally** (Node 25.9.0, see environment caveat).

**F — NOT GREEN.** Check-runs on a3b8f942:
| Check | Conclusion | Required? |
|---|---|---|
| frontend | success | yes |
| contract | success | yes |
| e2e | **failure** | yes (never path-filtered) |
| guard | did not run (path-filtered, no .github/scripts/ci change) | ?optional-if-absent |
| docker-build | did not run (path-filtered) | ?optional-if-absent |
| ci-required | **failure** | the single required status |
| deps-scan | failure | no (also failure on main 33633d4) |
| image-scan | failure | no (also failure on main 33633d4) |
| GitGuardian | success | no |

e2e (run 43061188734) failed in the step "Install the pinned Chromium": apt "Some index files failed to download", "Installation process exited with code: 100". No Playwright test ran; the later redact step then failed because test-results did not exist. This is a runner/apt infrastructure failure, not caused by the four files in the diff — but a required lane that did not run its tests is not a pass, and ci-required is red on the verified SHA. deps-scan / image-scan: red on main too, no dependency or Dockerfile change here, so not made worse (I did not diff the scan reports).

## Findings
| # | Class | Finding |
|---|---|---|
| 1 | BLOCKED input (not a defect in the PR) | `ci-required` is failure on a3b8f942 because `e2e` died installing Chromium (apt exit 100). Needs a re-run of run 43061188734 (and ci-required 43061188775) to green on the same SHA. |
| 2 | FOLLOW-UP | Nothing in any CI checks the vendored contract's freshness against core main (documented as owed; needs a read token for private vizra-core). The new exact-set test only pins the list, it cannot see core. |
| 3 | FOLLOW-UP | Mutations 1 and 2 leave `tsc` green; the type-level checks only bite on list/client disagreement. Covered by check:contract and the runtime test, so no gap today. |
| 4 | FOLLOW-UP | No Node 22 on the verifier machine; local lanes ran on 25.9.0. |

## VZ-FOUND-002 per-case
| Case | State on vizra-user main + this PR | Missing |
|---|---|---|
| S1 route without spec fails; spec without route fails | Not in this repo. vizra-core (#18) — not verified here. | Independent verification of vizra-core #18 and its CI output. |
| S2 generated client diff is empty after regeneration | Proven: `contract` lane (check:contract + `git diff --exit-code`), success on this SHA; reproduced locally by re-vendoring from core 5f615d7 + codegen → no diff. New exact-set test adds "vendored set = expected six" in `frontend`. | Only against the vendored copy: no CI compares it to core main, so staleness (the 4-of-6 state this PR fixes) can recur undetected. |
| N1 hand-edited generated file rejected by a drift check | Proven: mutation 2 → check:contract exit 1; the `contract` lane runs that command and is in required-checks.txt. | A CI job run showing the red on a deliberate mutation was not produced for this PR (local mutation only). |

evidence_required "CI job output showing both-direction drift failure on a deliberate mutation, then green": not satisfied by this PR — the red runs are local (builder's and mine), not CI job output, and "both-direction" route↔spec drift is core's S1.

Ledger: after this PR and vizra-core #18 merge, the id can be recorded **IMPLEMENTED**. Not **VERIFIED** until: (a) an independent PASS on vizra-core #18 covering S1 both directions, (b) CI job output (not local transcripts) of the deliberate-mutation red then green, (c) this PR's ci-required green on its SHA; and the freshness-vs-core-main gap stays recorded as owed.

## Not run
- e2e locally (Playwright/Docker) — not attempted in the time box; CI e2e ran no tests.
- `next build`, check-client-bundle, check-server-only-boundary locally (CI frontend lane ran them, success).
- Scan-report diff for deps-scan/image-scan vs main.
- vizra-core #18 (S1).
- No Node 22.14.0 run locally.

~~FINAL VERDICT: BLOCKED — SHA a3b8f942d566513b155971384bd2ee6b161d4520~~ (first verifier's verdict; SUPERSEDED by the completion section below — result F and finding 1 are resolved by attempt 2 of the same runs on the same SHA)

## Completion by a second independent verifier (2026-11-11)

Scope: only the one open item (result F / finding 1: `e2e` red in "Install the pinned Chromium", so `ci-required` red). I did not write the code, did not re-run CI, and changed nothing but this file. Results A–E above are the first verifier's and were not repeated.

### Commands
| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `gh pr view 12 -R yegamble/vizra-user --json headRefOid,state` | 0 | headRefOid a3b8f942d566513b155971384bd2ee6b161d4520, state OPEN (head unmoved; re-checked after writing this section, see end) |
| 2a | `gh run view 43061188734 -R yegamble/vizra-user --json status,conclusion,headSha,attempt` (e2e) | 0 | attempt 2, completed / success, headSha a3b8f942… |
| 2b | `gh run view 43061188775 -R yegamble/vizra-user --json status,conclusion,headSha,attempt` (ci-required) | 0 | attempt 2, completed / success, headSha a3b8f942… |
| 2c | `gh run view 43061188734 -R yegamble/vizra-user --log` (attempt 2), grepped for `Running N tests` and the Playwright summary lines, plus every `✓/✘ [project]` line | 0 | see Playwright counts |
| 2d | `gh run view 43061188734 -R yegamble/vizra-user --attempt 1 --log-failed \| tail -30` | 0 | see first-attempt failure |
| 3a | `gh api 'repos/yegamble/vizra-user/contents/.github/required-checks.txt?ref=a3b8f942…' -q .content \| base64 -d` | 0 | frontend, contract, ?guard, ?docker-build, e2e |
| 3b | `gh pr checks 12 -R yegamble/vizra-user` | 1 (non-zero only because the non-required deps-scan / image-scan are red) | see lane table |
| 3c | `gh api …/contents/.github/workflows/{ci-guard,docker-build,e2e}.yml?ref=a3b8f942…` — the `on:` blocks | 0 | see lane table |
| 3d | `gh pr view 12 -R yegamble/vizra-user --json files` | 0 | contracts/manifest.json, contracts/vizra-core/api/openapi.yaml, lib/api/contract-operations.test.ts, lib/api/generated.ts |

### Playwright counts — e2e run 43061188734, attempt 2 (job 130672010132)
Step "Browser lane (desktop 1440, mobile 390)": `Running 42 tests using 2 workers` → `42 passed (18.9s)`. Playwright printed no failed / skipped / flaky / "did not run" line for this step (it prints those only when non-zero), and I counted the per-test lines: 42 `✓`, numbered 1–42, no `✘`, no `-`.

| Project | Passed | Failed | Skipped | Flaky |
|---|---|---|---|---|
| desktop-chromium-1440 | 21 | 0 | 0 | 0 |
| mobile-chromium-390 | 21 | 0 | 0 | 0 |
| total | 42 | 0 | 0 | 0 |

Specs in each project: health (3), home (4), production-build (2), security-headers (5), shell (7).

Step "The harness still fails a broken page (canary)": four separate one-test runs, each `1 failed` — that is the step's intent (fault-injection fixtures that must go red), and it ended `OK: the harness canary failed all 4 fault-injection fixtures, each with the exact set of record kinds it demonstrates and no others`. These four are not product tests and are not counted above. The steps "The coverage floor was actually satisfied" and "The image contains no browser-harness file or fixture" also ran on attempt 2 (log lines present, job success); I did not read their bodies.

So the passing attempt really ran the lane's tests; it is not a green from zero tests.

### First-attempt failure (attempt 1)
The failed steps were "Install the pinned Chromium" — apt `Temporary failure resolving 'azure.archive.ubuntu.com'`, `E: Unable to fetch some archives`, `Failed to install browsers`, `Error: Installation process exited with code: 100` — and then "Redact URL query strings in the artifacts" (exit 3: `'test-results' is not a directory`), a consequence of no test having run. No Playwright test failed on attempt 1; none ran. Runner DNS/apt infrastructure failure, as the first verifier said (the precise cause is DNS resolution of the apt mirror rather than "index files").

### Lane table (required-checks.txt at a3b8f942 vs what ran on a3b8f942)
| Manifest entry | Manifest meaning | Ran on this SHA? | Conclusion | Should it have run for this diff? |
|---|---|---|---|---|
| `frontend` | must exist and succeed | yes (run 43061188696) | success | yes — ran |
| `contract` | must exist and succeed | yes (run 43061188658) | success | yes — ran |
| `?guard` | required only if it ran; manifest: "Path-filtered … so it is optional-if-absent" | no | absent | no. ci-guard.yml `pull_request.paths`: .github/workflows/**, .github/required-checks.txt, scripts/ci/**, vitest.config.mts, playwright.config.ts, e2e/harness/**, Dockerfile, .nvmrc, package.json, package-lock.json. None of the four changed files matches. |
| `?docker-build` | required only if it ran; manifest: "Path-filtered to the files that can break it" | no | absent | no. docker-build.yml `pull_request.paths`: Dockerfile, .dockerignore, package.json, package-lock.json, .nvmrc, next.config.ts, .github/workflows/docker-build.yml. None of the four changed files matches. |
| `e2e` | must exist and succeed; "NOT path-filtered, on purpose" (e2e.yml `pull_request:` has no paths) | yes (run 43061188734, attempt 2) | success, 42 passed | yes — ran |
| `ci-required` (the fan-in, the single required status) | — | yes (run 43061188775, attempt 2) | success | — |

Not in the required set, by the manifest's own "DELIBERATELY ABSENT" section: `deps-scan` fail, `image-scan` fail (the first verifier records both red on main 33633d4 too; I did not re-check main or diff the reports), GitGuardian pass.

No required lane that should have run is missing. The first verifier's "optional if absent" reading of guard and docker-build is what the manifest says, and the workflow path filters agree for a PR touching only contracts/ and lib/api/.

Note, not a finding against this PR: the manifest comment describes ci-guard's filter as ".github/** and scripts/ci/**", while the workflow's actual list is longer (also vitest/playwright config, e2e/harness, Dockerfile, .nvmrc, package files). The actual list is the wider one, so the comment understates rather than overstates when guard runs. Candidate for the vizra-user follow-up batch.

### Outcome
(1) head unchanged and PR open — holds. (2) e2e and ci-required both completed/success on the PR head at attempt 2; the e2e attempt ran 42 tests, 42 passed, 0 failed / skipped / flaky; attempt 1 died in the apt/Chromium install, not in a test — holds. (3) every required lane that should run for this diff ran and succeeded; the two absent lanes are `?`-prefixed and correctly path-filtered out — holds.

Unchanged from the first verifier and still true: this is a PASS for the PR only. VZ-FOUND-002 is not VERIFIED by it (vizra-core #18 / S1, CI-job output of the deliberate-mutation red, and the freshness-vs-core-main gap remain owed); follow-ups 2–4 stand. Not done by me: results A–E, local e2e, any Node 22 run, scan-report diff.

FINAL VERDICT: PASS — SHA a3b8f942d566513b155971384bd2ee6b161d4520
