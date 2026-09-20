# Execution plan: VZ-FOUND-008 — make the browser harness's guarantee structural (runtime, not lint)

## Context
- Repo `yegamble/vizra-user`, checkout `/Users/yosefgamble/github/vizra/vizra-user`.
- Branch `feat/m0-browser-env`, continuing PR https://github.com/yegamble/vizra-user/pull/3.
- Base for this round: `0ac9fb6a820d50ef030f86f053409b967d2beec8` (clean tree confirmed).
- Chair RE-PLAN after the original builder used both fix rounds. I did not write the
  code under repair.
- Verifier report: `/Users/yosefgamble/github/vizra/docs/evidence/warroom/2026-09-20-vizra-user-pr3-browser-env-VERIFY.md`,
  section "Re-verification at 0ac9fb6" — FINDING 9 (BLOCKER), FINDING 10 (REQUIRED),
  and the accepted-by-design residual that neutering `e2e/harness/test.ts` while
  leaving its identifiers present is silent in CI.

### The defect class
Three verifier rounds, three different doors into the same hole: a spec that does not
go through the guarded harness `test` runs green on a page that 404s and throws.
Door 1 import syntax the regex missed; door 2 an inline `eslint-disable`; door 3 a
spec at `e2e/other/x.spec.ts` (Playwright collects `**/*.spec.ts` under `e2e/`, the
ESLint rule covers only `e2e/specs/**` and `e2e/demos/**`). Each was patched where it
was found. The guarantee rests on LINT, which can always be side-stepped.

## Acceptance
1. **Runtime proof of harness.** The harness `test` stamps every test it runs with a
   value the raw `@playwright/test` `test` cannot produce by accident. A reporter in
   `playwright.config.ts` and the out-of-process check that re-reads the JSON report
   both fail the run when an executed test that PASSED carries no valid stamp, naming
   the file. Demonstrated red/green against all three historical doors verbatim plus
   at least one the verifier has not tried.
2. **Collection closed too.** `testDir` restricted so only `e2e/specs` (lane) and
   `e2e/demos` (demo runner) are collected; the ESLint block covers everything under
   `e2e/` except `e2e/harness`; the credential tripwire's roots follow.
3. **CI self-test of the harness.** A fast canary step in the required `e2e` lane runs
   the three core broken-page fixtures through the harness and REQUIRES each to fail
   for its named reason. `check-e2e-lane.mjs` asserts the step exists, is
   unconditional and is not `continue-on-error`. Demonstrated: neuter the console /
   pageerror / response listener one at a time → the canary turns the lane red.
4. **Finding 10.** Every upload step is checked (`filter`, not `find`); any step that
   uploads artifacts without the redactor-success gate is refused. Fixture workflows
   for a second ungated upload and for a non-`actions/upload-artifact` uploader.
5. **AGENTS.md exactly true.** Runtime stamp described as the control, lint as the
   early warning; residuals listed honestly.

Non-goals: no authenticated spec, credential or signed URL (artifact-privacy slice is
queued separately); no visual baselines; no new browser revision; no Docker D6 pair in
the canary.

## Implementation
| File | Change |
|---|---|
| `e2e/harness/stamp.ts` | NEW. Per-run key: generated in the Playwright main process, handed to workers through the environment, **removed from `process.env` in the worker before any test file loads**. Signs/verifies the per-result stamp. |
| `e2e/harness/stamp-reporter.ts` | NEW. Fails the run when a PASSED result carries no valid stamp, naming the file. Writes the key to `.vizra-e2e/stamp-key` at `onEnd` (after every spec has finished) so the out-of-process check can verify. |
| `e2e/harness/test.ts` | Automatic fixture that stamps every test, before the guard's own throw so a failing test is stamped too. |
| `playwright.config.ts` | `testDir: "./e2e/specs"`; import the stamp module; register the stamp reporter. |
| `playwright.demos.config.ts` | `testDir: "./e2e/demos"`; register the stamp reporter. |
| `scripts/ci/check-coverage-floor-ran.mjs` | Also verify every passed result's stamp from the JSON report; fail closed when the key file is absent (the reporter did not run). |
| `scripts/ci/harness-canary.mjs` | NEW. Runs the three broken-page fixtures and requires each to fail for its named reason. |
| `.github/workflows/e2e.yml` | New canary step after the lane. |
| `scripts/ci/check-e2e-lane.mjs` | Assert the canary step; `filter` over every uploader step; recognise non-`actions/upload-artifact` uploaders. |
| `eslint.config.mjs` | `files: ["e2e/**/*.ts"], ignores: ["e2e/harness/**"]`. |
| `e2e/harness/no-credentials-in-specs.test.ts` | Walk `e2e/` minus `harness/`. |
| `e2e/harness/browser-errors.test.ts` | Assert the resolved config wires the rule at severity 2 with `noInlineConfig` for EVERY collectable file; assert the stamp key is not readable from a spec's process. |
| `e2e/harness/stamp.test.ts` | NEW. Unit cases for the stamp. |
| `scripts/e2e/demonstrate.sh` | D8 extensions (the four doors, red at RUNTIME), D11 (canary vs neutered listeners), D7 extensions (Finding 10). |
| `e2e/harness/required-projects.json` | Unchanged unless collected tests change. |
| `AGENTS.md` | Rewrite the guard paragraph; residual list. |

## Verification
- `npm ci`, `npm run ci`, `npm run test`, `npm run e2e`,
  `node scripts/ci/check-coverage-floor-ran.mjs`, `bash scripts/ci/check-e2e-lane.sh`,
  `bash scripts/ci/require-checks_test.sh`, `bash scripts/ci/check-required-floor.sh`,
  `npm run e2e:demos`, `node scripts/ci/harness-canary.mjs`.
- CI on the pushed head SHA: every lane in `.github/required-checks.txt`.
- Environment: macOS arm64, Node v22.14.0, @playwright/test 1.63.0, Chromium
  `chromium-1243` already in `~/Library/Caches/ms-playwright` (no browser installed).
- Transcripts: `docs/evidence/VZ-FOUND-008/` inside the repo, added to the existing
  index; the previous builder's files are not deleted.

## Progress and evidence

### Preflight (run first, not last)
| Dependency | State |
|---|---|
| Node v22.14.0 / npm 10.9.2 | present |
| `@playwright/test` 1.63.0, Chromium `chromium-1243` | already in `~/Library/Caches/ms-playwright`; **no browser installed by me** |
| Docker 29.8.0, ~13 GiB free | present — D6 ran, not BLOCKED |
| shellcheck | present; `scripts/ci/*.sh` clean |
| `gh` authenticated | present |
Nothing was BLOCKED. Platform is macOS arm64, which ADR-009 says is **not** the
acceptance platform; CI on the head SHA is the platform evidence.

### Head
`f6f1f59a7c15a15e50c052602c3da88a425e5d35` on `feat/m0-browser-env`, pushed
(no force). Parent `0ac9fb6a820d50ef030f86f053409b967d2beec8`, confirmed clean
before editing. 82 files, +3342 −452.

### Commands, exit codes, counts (all on f6f1f59, local, macOS arm64)
| Command | Exit | Result |
|---|---|---|
| `npm ci --dry-run` | 0 | lockfile consistent; no dependency added |
| `npm run ci` | 0 | vitest **12 files / 269 tests / 0 skipped**, `next build` OK |
| `bash scripts/ci/require-checks_test.sh` | 0 | **102 cases / 109 assertions / 0 failed** (was 92/99) |
| `bash scripts/ci/check-required-floor.sh` | 0 | floor `frontend contract e2e` |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | names the canary and "EVERY upload step" |
| `bash scripts/ci/check-image-pins.sh` | 0 | 3 FROM lines `@sha256`-pinned |
| `npx playwright test` | 0 | **18 passed**, floor `9/9 9/9`, `e2e harness stamp: OK (18 verified)` |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | floor OK **and** 18 stamps verified from the report |
| `node scripts/ci/harness-canary.mjs` | 0 | 3 fixtures failed, each for its own named reason (~2.9 s) |
| `npm run e2e:demos` | 0 | **74 halves passed, 0 blocked, 0 failed** (was 51) |
| lane against the built arm64 image | 0 | `docs/evidence/VZ-FOUND-008/lane-against-built-image-local.txt` |

### Demonstrations (transcripts, all inside the repo)
`/Users/yosefgamble/github/vizra/vizra-user/docs/evidence/VZ-FOUND-008/`

| ID | What | Red | Green |
|---|---|---|---|
| D11a | door 1 — namespace import | `d11a-namespace-import-RED.txt` | `d11-clean-tree-lane-GREEN.txt` |
| D11b | door 2 — `eslint-disable`, with `noInlineConfig` stripped by a mutant config so lint genuinely passes | `d11b-eslint-disable-RED.txt` | `d11b-lint-defeated-GREEN.txt` (proves lint let it through) |
| D11c | door 3 — `e2e/other/__r1.spec.ts` | `d11c-outside-refused-by-lint-RED.txt` | `d11c-outside-not-collected-GREEN.txt` (`Total: 18 tests in 3 files`) |
| D11d | NEW — forge via the sealed `e2e/harness/stamp` | `d11d-forge-via-sealed-module-RED.txt` | — |
| D11e | NEW — forge via `process.env.VIZRA_E2E_STAMP_KEY` | `d11e-forge-via-environment-RED.txt` | — |
| D11f | out-of-process, in-process reporter deleted | `d11f-out-of-process-still-RED.txt` | `d11f-in-process-reporter-deleted-GREEN.txt` |
| D12 | canary vs each neutered listener | `d12-{console,pageerror,response}-listener-neutered-RED.txt` | `d12-canary-{GREEN,restored-GREEN}.txt` |
| D7b | Finding 10 — second ungated upload, other uploader | `d7b-second-ungated-upload-RED.txt`, `d7b-other-uploader-ungated-RED.txt` | `d7b-second-gated-upload-GREEN.txt` |
| D7c | the canary step is required | `d7c-*.txt` (4) | — |

D1–D10 all reproduce unchanged; nothing was weakened or deleted.

### Forging the stamp — what it would take
1. Recover the 32-byte per-run key from inside a spec. It is absent from the
   worker's `process.env` (deleted during config load, before any test file is
   evaluated — D11e asserts `undefined` and passes), absent from disk while any
   test runs (`.vizra-e2e/stamp-key.json` is written in `onEnd`), and not
   derivable from the report.
2. Import `e2e/harness/stamp` and call `claimSigner()`. The signer is claimed
   once per worker by the harness entry during config load, so this throws
   (D11d); ESLint also refuses the reference as a sealed module.
3. Edit `e2e/harness/**`, `playwright.config.ts` or `eslint-rules/**`. CODEOWNERS
   paths; `npm run test` fails on a neutered rule or wiring; the D12 canary turns
   the lane red on a neutered guard. No control in this repository forbids it.
Stated in `AGENTS.md` and in the `e2e/harness/stamp.ts` header, not hidden.

### Cleanup
`vizra-user:demonstrate` (the only image I created) removed by exact name; the
`vizra-pr2-*` containers belong to another agent and were not touched. No shared
build cache pruned, deliberately — `docker builder prune` is not scoped to one
creator. No throwaway PR or branch was opened this round.

---

## Fix round 1 of 2 — FINDING 11 (head `c669e40`)

### The hole
The stamp was an `auto` fixture; the guard was a `page` override.
`test.extend` replaces one without the other, so four lines of ordinary,
lint-clean Playwright kept the stamp and removed the guard, and the whole gate
went green on a page that 404s a sub-resource and throws. The stamp proved
"this test came from the harness `test` object"; the claim is "this test ran the
guard".

### What changed
| File | Change |
|---|---|
| `e2e/harness/browser-errors.ts` | `collectBrowserErrors(page)` → `guardBrowser(browser)`: BrowserContext-level `console` / `weberror` / `requestfailed` / `response` listeners, a sweep of existing contexts, and wrapping of `browser.newContext`/`newPage` for the test, restored on dispose by DELETING the own property rather than restoring a bound copy |
| `e2e/harness/test.ts` | one automatic fixture `vizraHarnessGuard` holds the guard **and** the stamp; deps `{ browser, context, browserErrorPolicy }` |
| `eslint-rules/no-unguarded-playwright-import.mjs` | new `harnessFixtures` option: `.extend` may not replace a harness-owned fixture, and an unreadable fixtures object fails closed. `test.extend` is NOT banned |
| `scripts/ci/harness-canary.mjs` | one invocation per fixture; asserts the exact SET of record kinds (present AND absent) |
| `scripts/ci/check-e2e-lane.mjs` | asserts `guardBrowser`, the combined fixture, and that `e2e/harness/test.ts` does not override `page` again |
| `scripts/e2e/demonstrate.sh` | D13 (11 halves), D12e (2 halves), D12 mutations updated to the new listener source, D12d added |
| `e2e/harness/browser-errors.test.ts` | +8 `guardBrowser` cases (including prototype restore) and +4 fixture-override lint cases |
| `AGENTS.md` | "WHY AT THE BROWSER, AND WHY ONE FIXTURE"; corrected canary claim; new residual |

### The dependency list was measured, not chosen
| Fixture depends on | Guard installed | Page at assertion | Result |
|---|---|---|---|
| `browser` | before `page` ✅ | closed (`pages=0`) ❌ | flush a no-op; the failure's trace went 21 members → 8 |
| `browser` + `page` | after an overridden `page` ❌ | open ✅ | a spec navigating inside its own fixture **passed** on a broken page |
| `browser` + `context` | before `page` ✅ | open (`pages=1`) ✅ | both; D13e2 fails with all three records |

### Commands on `c669e40` (local, macOS arm64)
| Command | Exit | Result |
|---|---|---|
| `npm run ci` | 0 | vitest **12 files / 289 tests / 0 skipped** (was 269) |
| `bash scripts/ci/require-checks_test.sh` | 0 | 102 cases / 109 assertions / 0 failed |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | — |
| `bash scripts/ci/check-required-floor.sh` | 0 | floor `frontend contract e2e` |
| `npx playwright test` | 0 | 18 passed, floor 9/9 9/9, `harness stamp: OK (18 verified)` |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | floor OK + 18 stamps verified |
| `node scripts/ci/harness-canary.mjs` | 0 | 3 fixtures, exact kind sets (~6 s) |
| `npm run e2e:demos` | 0 | **88 halves passed, 0 blocked, 0 failed** (was 74) |

**CI on `c669e40`:** `ci-required` pass — "OK: every required check on
c669e4001738df3f7c7ec3fcf1feaf3c9e41ca4e concluded success". All eight lanes
pass; GitGuardian still FAILURE on the same historical pair.

### Residual, stated rather than implied
A spec that launches its OWN browser (importing a Playwright package and calling
`chromium.launch()`) is not guarded at runtime — the harness never sees that
object. Lint and review are the only controls there; the stamp, the floor, the
canary and the parser are not. Note the contrast with D13g: a `browser` fixture
overridden through Playwright's built-in `playwright` fixture needs no import,
so lint cannot see it — and the runtime does catch that one.

## Blockers and handoff
None. Next concrete action: the same independent verifier re-verifies
`c669e4001738df3f7c7ec3fcf1feaf3c9e41ca4e`. GitGuardian remains FAILURE on the
same two historical findings from `951f18b` (an `hmr?id=` loopback dev-server
value); a squash-merge drops that commit, and the check needs deliberate owner
dismissal rather than being merged past.
