# Verify — vizra-user PR #21 (QUEUE-2f final, VZ-FOUND-008) — 3rd of 4 verdicts

- SHA: e2b8d646520fb683ce3c6f9f55b1531eaef96fe3 (PR head confirmed by `gh pr view`; OPEN)
- Clone: fresh `git clone` + `fetch pull/21/head` in `/tmp/vzv-user-pr21-BCoI7g` (deleted afterwards); `npm ci` exit 0; Node v24.21.0, macOS Darwin 25.5.0
- Verifier: independent, did not write this code.

## Results
| Check | Command | Result |
|---|---|---|
| (1) Playwright strings | `grep` in `node_modules/playwright/lib` | `matchers/expect.js:12072` `Timeout: ${align?" ":""}${timeout}ms`; `worker/workerProcessEntry.js:464,468,474` `Test timeout of ${timeout}ms exceeded.` / `while setting up "${fixture}".` / `while running "${type}" hook.`; `matchers/expect.js:13022`. These are the shapes `MESSAGE_LINE_ALLOW` (`artifact-allowlist.mjs:232-237`) accepts, and the `Timeout: +\d+ms` regex covers the aligned space. PASS |
| (2) unit | `npx vitest run scripts/ci/artifact-allowlist.test.mjs` | 29 passed, 0 skipped, exit 0 |
| (2) | `bash scripts/ci/require-checks_test.sh` | 237 cases, 244 assertions, 0 failed |
| (2) | `bash scripts/ci/check-e2e-lane.sh` | OK, exit 0 |
| (2) | `npm run check:hygiene` | exit 0 |
| ci-required | `gh pr checks 21` | pass (run 43291340314) |

## (3) Filter attack: `node scripts/ci/artifact-allowlist.mjs --filter-log < fixture`
The fixture had 27 sentinels (PWSECRET1..27) in these lines: Expected/Received with a typed password, multi-line Received, `Authorization: Bearer`, `Set-Cookie`, an `X-Amz-Signature` URL, `Timed out waiting for token`, `Timeout: <value>`, `Timeout: 5000ms <value>`, `Test timeout of <value>`, `getByLabel('…')`, `getByText(/…/i)`, a backtick-quoted locator, a quoted locator with an escaped quote, `.fill("…")`, a stack frame with a trailing value, ANSI-coloured Received and expect lines, a 200 KB line, and lines that imitate progress and counts lines (`3 passed SECRET`).
**All of these were withheld or scrubbed:** 1–12, 15, 17–19, 21, 23 and 25–27.
**These survived (stdout):**
- PWSECRET13 `Locator: locator(#PWSECRET13)`
- PWSECRET14 `Locator: getByRole(button, { name: PWSECRET14 })`
- PWSECRET16 `expect(PWSECRET16).toBe(1)`
- PWSECRET20 `✘  2 [chromium] › e2e/a.spec.ts:1:1 › PWSECRET20 imitated progress`
- PWSECRET24 `[chromium] › e2e/a.spec.ts:1:1 › x PWSECRET24`
- PWSECRET22 `::error::PWSECRET22`

Classification: **FOLLOW-UP, not BLOCKING.** None of these shapes carries a runtime value in today's tree:
- Playwright prints Locator arguments quoted, and quoted text is scrubbed.
- Playwright's matcher header is `expect(locator|received)…`, not a value.
- The progress-line titles are test titles from spec source.
- Every `::error::` emitter in `e2e/harness` and `scripts/ci` prints fixed text, environment-change descriptions or file names.

They are still allow-list holes in the filter's own contract. Two things could feed them: a test title built with a runtime value, and container-log (app-controlled) lines shaped like these. The `--filter-log` docstring's claim of default-deny is shape-based, not value-based.

## (4) My mutations of e2e.yml → `check-e2e-lane.sh` (restored → exit 0)
| Mutation | Exit |
|---|---|
| M1 removed the pipe (`npm run e2e`) | 1 |
| M2 `set -eu` (no pipefail) | 1 |
| M3 `… --filter-log \|\| true` | 1 |
| M4 added step `docker logs vizra-user-e2e` unfiltered | 1 |
| M5 added step `npx playwright test` unfiltered | 1 |
| M6 health-failure `docker logs` unfiltered | 1 |
| M7 second `npm run e2e -- --reporter=list` step | 1 |

## (5) CI sentinel runs (`gh run view --log`)
- Run 43290238134 (SHA 37e03f7, e2e **failure**): 137 KB log; `grep -c SENTINEL-abcPW` = 0 and `grep -c abcPW` = 0. The failure is still visible: `✘ 15/30/37/44 … shell.spec.ts:13:7 …` and `expect(locator).toHaveText(expected) failed`.
- Run 43290823132 (SHA 9b020a4, **success**): `grep -c SENTINEL-abcPW` = 0; `42 passed (17.4s)`; the canary still shows `1 failed`.
- Commit 37e03f7 changes only `e2e/specs/shell.spec.ts` (1 line).

## (6) D7 retarget (commit 8a83933)
The old seds anchored `^        run: npm run e2e$`. That pattern matches **0** lines of the new e2e.yml (`grep -c` = 0), so those mutants were byte-identical to the original: the false green the builder described is confirmed.
- The new delete sed changes line 130, and so does the new `echo skipping` sed (checked by diff).
- On GNU sed, `\|` in the `/…/d` address is alternation, but the first alternative is anchored to the lane line, so it still deletes exactly that line.
- The new no-pipefail mutant deletes `set -euo pipefail`.
- I did not re-run `e2e:demos` locally (it needs Docker and the full lane). The 150/0/0 claim rests on the committed transcripts and CI: UNVERIFIED by me. My M1–M7 cover the same guard independently.

## Findings
- **F-C (FOLLOW-UP)** `artifact-allowlist.mjs:233,314-319`: the log filter passes free text in these shapes:
  - unquoted `Locator:`/`expect(` arguments;
  - the progress-line title tail;
  - any `::error::` line.

  Reproducer: the fixture lines above, piped to `--filter-log`. Not emitted with values today. Fix: scrub unquoted call arguments; limit `::error::` to known prefixes; filter container logs with a stricter (counts-only) profile.

No BLOCKING findings.

## Gate judgement
F-A, F-B and 2ac are closed for the shapes Playwright and the harness actually emit, and the lane guard refuses every unfiltered or exit-laundering variant I tried. **The gate can open for authenticated M1 specs**, with two conditions:
- (a) test titles must not interpolate runtime values (credentials, tokens, URLs);
- (b) no new code may emit `::error::` with a value until F-C lands.

F-C should land before specs log app/container output that could carry secrets.

FINAL VERDICT: PASS — SHA e2b8d646520fb683ce3c6f9f55b1531eaef96fe3
