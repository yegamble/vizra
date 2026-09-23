<!-- Recorded by the war-room chair, 2026-09-23 (tick 204), from the vizra-security seat's hand-back
     (a fresh read-only seat session). The seat does not write files. The text below is the seat's
     report, condensed only by removing its per-finding boilerplate fields; every finding, severity,
     citation, recommendation and answer is kept. Chair rulings are appended at the end. -->

# vizra-user artifact privacy II (PR B): security seat plan review

- **Plan reviewed:** `docs/plans/2026-09-23-vizra-user-artifact-privacy-b.md`
- **Checked against:** vizra-user `origin/main` `7a3a572`, installed Playwright 1.63.0, and the binding review `docs/evidence/warroom/2026-09-21-vizra-user-artifact-privacy-PLAN-REVIEW-security.md`.
- **Method:** read-only. The only local runs were two `JSON.parse` calls on synthetic strings (F6) and one fetch of the pinned upload-artifact source (F13).
- **Item 1 (stamp-key design):** not reviewed, per the chair's instruction. F7 covers only how R-1 is worded.

**The gate stays CLOSED:** `vizraCredentials` can only hand out synthetic credentials (tripwire-enforced), and the hard rule is kept.

## BLOCKER

**F1: in Lane A, a request-side credential fails the test, and failing is what gets the trace published.**
- The plan only taints the run on the response side (`set-cookie`, vendor token).
- On the request side (Authorization, Cookie, a credential-named body parameter, `addCookies`, `storageState`, `APIRequestContext`) the test only FAILS. But Lane A keeps `trace: retain-on-failure`, and the upload runs on `if: failure()`.
- The failing trace carries the header (`1-trace.network`) and the POST body (`resources/*`). The redactor rewrites only URL queries, and the shape scanner has no form-body password detector.
- Since 2026-09-23 the artifact is public.
- **Fix:** every guard signal taints, request side and response side alike, and the request side also fails the test. Taint is sticky and worker-side, independent of per-test windows (late records and teardown included).
- **Acceptance:**
  - D20a, D20c and D20d show both that the test fails and that the upload is withheld;
  - a late-record case withholds the upload;
  - mutation M9, "request side does not taint", turns D20a red.

## REQUIRED

**F2: taint is keyed by lane, not by invocation.**
- `taint.<lane>.json` is overwritten "clean" by later same-lane runs: `playwright.demos.config.ts` inherits Lane A, and `harness-canary.mjs:128-142` runs it four times after `lane` and `floor`.
- **Fix:** append-only per-invocation records under `.vizra-e2e/out/taint.d/`, naming the config and outputDir. The scanner fails on any tainted Lane-A record, or on a missing record for `playwright.config.ts` plus `test-results`. The privacy canary never invokes a Lane-A config.

**F3: the Lane-B egress allowlist (B-5) can be bypassed by ordinary idioms.**
- Routes run in reverse registration order, so `page.route('**', r => r.continue())` and `route.continue({ url })` skip the allowlist handler.
- `route.fetch()` goes straight to `_innerFetch` (`coreBundle.js:59742`), skipping a patch on `fetch`.
- Service-worker and WebSocket traffic is not seen by `context.route`, and Node-level egress is outside Playwright altogether.
- **Fix:**
  - patch `Route.prototype.continue` (checking the final URL) and the shared `_innerFetch`, and throw if it is missing;
  - add a `routeWebSocket` refusal;
  - put a literal `serviceWorkers: "block"` in the auth config, asserted;
  - state residual R-11 for Node and non-HTTP egress, with lint early warnings;
  - scope B-5 to "browser and APIRequestContext traffic".
- **Acceptance:** D21c, D21d and D21e red, plus a `serviceWorkers` mutation refused.

**F4: B-2 "produces no screenshot" is only true of automatic capture.**
- `page.screenshot({ path })`, `tracing.start/stop`, or `fs` writes into `test-results/` enter the upload set. The only inventory check is D19b's, and it runs in the canary, not the real run.
- **Fix:** take a sha256 inventory of the Lane-A upload set before Lane B in the REAL run, and withhold the upload on any change. Add lint warnings and reword B-2.

**F5: missed channel T18, snapshot baselines written into the source tree.**
- `toHaveScreenshot`, `toMatchSnapshot` and `toMatchAriaSnapshot` default to `updateSnapshots: "missing"` and write under `e2e/authenticated/*-snapshots/`, one `git add` away from publication.
- **Fix:**
  - `updateSnapshots: "none"` asserted in the auth config, and inherited without override;
  - lint refusal of the three matchers;
  - the tripwire refuses tracked `*-snapshots/**` and `*.aria.yml`;
  - canary row T18 and mutation M10.

**F6: Lane-B-derived text reaches the job log without write → scan → print.**
- Node 22's `JSON.parse` error quotes its input (measured).
- `check-coverage-floor-ran.mjs --lane auth` prints `error.message` and titles before the scan, and the scanner prints member names.
- **Fix:** fixed-form output for `--lane auth` (counts, project names, error class); the scanner never prints a matched name; FINDING-13 sanitising; unit tests with markers.

**F7: R-1 is worded incorrectly.**
- R-1 persists after item 1, so it cannot be why the gate is closed; the gate is closed because V-D is open.
- R-1 must say that main-process collection code runs outside the worker guard, the egress allowlist and the stamp.
- "Stamps verified" lines carry "(V-D open)" until D18 is green, and the amended hard rule names V-D and D18 as the precondition for opening.

**F8: the ledger text (item 4) claims more than its controls.** Use the seat's replacement text (full text in the seat's hand-back, recorded in the plan by the builder):
- the shape scan is a backstop that does not prove absence;
- request-side detection covers a fixed name list;
- the summary shares Lane A's artifact;
- it is demonstrated only with synthetic credentials against a loopback fixture.

**F9: the positive control and summary ordering.**
- The positive config must derive from the CANARY config, not the auth config, so `testMatch` hits the canary.
- The canary deletes the summary at start and in `finally`.
- The scan and print steps refuse a summary naming a `*.canary.ts` file.
- State where the T14 marker is planted.

**F10: the shape detectors assume HTTP wire text.**
- Traces store headers as `{"name","value"}` pairs, and the JSON reporter stores attachments as base64.
- **Fix:**
  - take corpus true positives from D19a's measured artifacts;
  - always scan decoded base64, and recurse when it is an archive;
  - set the base64 threshold at or below 24 chars;
  - mint markers in lowercase hex.

**F11: the `secrets.` backstop is spelling-bypassable and covers one file.**
- **Fix:**
  - refuse any `${{ }}` expression that references the `secrets` context or `github.token` anywhere in e2e.yml;
  - e2e.yml `permissions` must be exactly `contents: read`;
  - refuse Lane-B tokens in every workflow except e2e.yml's pins (RC-6b/6c/6d).

## SHOULD

- **F12:** normalised credential-name matching: strong stems by substring, weak ones exact; add OAuth/DPoP/API-key names; echo the stem only.
- **F13:**
  - `lstat` every walked entry, refusing symlinks and hard links with nlink > 1 (the pinned upload-artifact follows symlinks);
  - apply the `.vizra-e2e` refusal to the realpath;
  - validate the summary schema at scan time;
  - print by allowlist;
  - literal titles in `e2e/authenticated/**`.
- **F14:** R-5 undercounts Lane A's pixel channels: screenshot, video, trace screencast and trace resources.

## NIT

- **NIT 1:** widen the env refusal prefix to `^PW` (covers `PWTEST_*`, `PWDEBUGIMPL`, `PWPAUSE`).
- **NIT 2:** Lane B literals: `forbidOnly: true`, `webServer.reuseExistingServer: false`, a fixture bound to `127.0.0.1`; write the summary atomically.
- **NIT 3:** sequence PR B after the visibility docs PR, which is now merged (user #9, `783483f`).

## Not worth doing

- **Two upload steps (Q2):** small gain, costs a pin.
- **A trace redactor, or deleting `.vizra-e2e/out`:** FINDING 23 stands.
- **npm `_logs`:** they record argv and exit codes, not script output.

## Answers to Q1–Q7

- **Q1:** land both synthetic specs now, with F11 hardening. The amended hard rule names V-D and a green D18 as the precondition for opening the gate, and opening should also require the ruleset (R-9).
- **Q2:** one upload step. Note that on a Lane-B-only failure, `test-results/` holds the harness canary's demo outputs.
- **Q3:** turn Lane A's pixel channels off now, completely: `screenshot: "off"`, `video: "off"` and `trace: { mode: "retain-on-failure", sources: false, screenshots: false }`, asserted with mutations. It may go in its own small PR, but must not be deferred.
- **Q4:** a red job on a credential-shape hit is preferred. It gets its own exit code and fixed message, the match is never printed, and false positives are resolved only by a reviewed corpus diff.
- **Q5:** the ordering is acceptable with the F2/F9 conditions.
- **Q6:** Lane B ignores the environment entirely: the floor is a reporter option, and the other strictness values are literals. The repo-wide env-strictness fix goes in a separate follow-up PR queued now.
- **Q7:** refuse outright in Lane A. Put the refusal and Lane B's patch at the shared `_innerFetch`, and throw if it is missing.

**SEAT VERDICT: PLAN APPROVED WITH REQUIRED CHANGES.** F1 (BLOCKER) and F2–F11 go into the plan before phase 2 starts. The architecture holds: the Lane A / Lane B split by invocation, "not produced" as the control, and "path, not option".

---

## Chair rulings (tick 204)

1. **F1–F11 are accepted in full.** The builder amends the plan, and the seat confirms the amended plan before phase 2.
2. **SHOULD items:** F12, F13 and F14 are accepted into PR B. NITs 1 and 2 are accepted. NIT 3 is satisfied (user #9 merged).
3. **Q1–Q7:** adopted as the seat answered them.
   - Q3 ships NOW as its own small vizra-user PR, "Lane A pixel channels off": `screenshot: "off"`, `video: "off"`, and `trace` with `screenshots: false, sources: false`, each asserted by the parsed-config guard with a mutation.
   - Q6's repo-wide env-strictness fix is queued as 2r.
4. **Item 1 (V-D design) stays in owner inbox 10.** Lane B's gate stays closed until V-D is closed and D18 is green.

## F8 replacement ledger text — verbatim from the seat's hand-back (added by the chair, tick 207)

The condensed F8 entry above referred to the seat's hand-back for the full text; the builder correctly asked for it (Q-r2-4). The seat's recommended replacement text, verbatim:

> "An authenticated browser spec publishes no credential and no page content in an uploaded CI artifact or in the job log: it runs only in the separate authenticated lane, whose projects configure no trace, screenshot or video and write no snapshot baseline, whose output directory, log and report are in no upload path, whose writes into an upload path withhold the upload, and whose only contribution to the uploaded artifact is a summary of allowlisted structured fields with no error message, stack, locator or URL. Demonstrated against a loopback fixture with synthetic credentials by an end-to-end canary with runtime-minted markers, positively controlled (every marker found with recorders on) and negatively controlled (none found in the files of the allowlisted upload paths in the shipped configuration). Every run is backstopped by a credential-shape scan that withholds the upload on a hit; that scan detects known shapes and does not prove the absence of secrets. In the unauthenticated lane, a request carrying a header or body parameter from a fixed list of credential names fails the test, and any such signal, or a response Set-Cookie or vendor token header, withholds that lane's upload."

Status stays UNVERIFIED, as the plan says.

## Seat confirmation pass on plan revision 2 (tick 208) — recorded by the chair

**SEAT VERDICT: CHANGES STILL REQUIRED** (C1–C4 are small and local; the architecture holds; the seat can confirm without another full pass once they are in).

**Status of the round-1 findings:**
- Addressed: F1 (except C3), F2, F4 (but see C1), F5, F6, F7, F10, F11, F12–F14, NIT 1, NIT 2.
- Partly addressed: F3 (see C2) and F9 (see C4).
- F8: the text was supplied at tick 207.

**New and remaining items:**

- **C1 (REQUIRED).** The B-10 inventory is compared after the `redact` step has rewritten `test-results/` in place, so every failing run would withhold the upload.
  - Add a pinned `lane_a_inventory_check` step right after `auth_floor`, before `redact`, with `if: always()`. It writes an outcome record, and `scan` requires "unchanged".
  - Exclude the summary path from the inventory.
  - A missing inventory is allowed only when no auth or canary `start` record exists.
  - Tests: RC-10 rows for "check step after redact" and "check step missing"; D19d, where a red Lane A with a green Lane B still uploads.

- **C2 (REQUIRED).** F3 is still open in three places:
  - (a) WebSocket traffic: the guard must install its own `context.routeWebSocket` that closes non-allowlisted URLs, and B-5 covers WebSocket again.
  - (b) `context.unroute('**')` and `unrouteAll()` remove the guard's route: refuse them for the guard's pattern, or reinstall the guard.
  - (c) The option surfaces are open:
    - give the auth config's `use` (top level and per project) an exact key allowlist;
    - in Lane B, creation-guard refuses `proxy`, `recordHar`, `recordVideo`, any `serviceWorkers` other than "block", and `BrowserType.connect`/`connectOverCDP`.
  - Tests: D21f, D21g, and RC-4 rows.

- **C3 (REQUIRED).** Worker-side taint has no closing record, so a signal lost before it is written (async `headersArray()`, a teardown or kill, a write that throws) fails open.
  - Each worker writes `worker-start` and a `worker-end` carrying its signal count.
  - Teardown awaits pending header reads with a bound; a read unresolved at the bound counts as a signal.
  - The scanner requires the start/end pairs.
  - A failed write throws.
  - Test: D20h.

- **C4 (REQUIRED).** The T14 marker sits in the failing canary test's title, which contradicts D19b and the literal-title lint.
  - Plant it in a PASSING canary test's title (or an attachment name).
  - Give only that test a per-file lint exemption.

- **C5 (SHOULD).** Substring stems over-match header names (`x-csrf-token`, `access-control-allow-credentials`).
  - Headers use an exact normalised list: authorization, proxyauthorization, cookie, setcookie, xapikey, xauthtoken, dpop, xamzsecuritytoken.
  - Stems apply to body parameter names only.
  - A header that matches only by stem taints but does not fail the test.
  - Add CSRF and CORS names to the false-positive corpus.

- **C6 (SHOULD).** A local `-u` run can still write authenticated baselines.
  - Add `.gitignore` entries for `e2e/authenticated/**/*-snapshots/` and `*.aria.yml`.
  - Assert `testInfo.config.updateSnapshots === "none"` at runtime.

- **NIT 1.** Paste the F8 text in, with the author's precision edit: "fails the test" → "fails the test, or the run when no test owns the request".
- **NIT 2.** State that T18's positive control is M10, and that M10's restore step deletes the baseline it writes.

**Answers to the builder's questions:**
- **Q-r2-1:** yes. The protection comes from the taint, and C3 makes the taint reliable.
- **Q-r2-2:** `session`, `sessionid` and `sessid` match exactly; `assertion` stays a stem for body names only.
- **Q-r2-3:** a distinct exit code plus the fixed plain line is enough. An annotation is optional, and if added is built only from the fixed lists.

**Chair ruling (tick 208):** C1–C6 and both NITs are accepted, and Q-r2-1…3 are answered as the seat recommends. After the builder amends the plan to revision 3, the seat checks only C1–C4, and phase 2 may then start once user #10 has merged.

## Seat check of plan revision 3, C1–C4 (tick 209) — recorded by the chair

**Result per item:**
- C1 and C4: confirmed.
- C2: confirmed except R3-1.
- C3: confirmed except R3-2.

**Findings:**

- **R3-1 (REQUIRED).** In Lane B, a spec can still supply its own browser through the `browser`/`context` fixture.
  - Before the guard is armed, it can call `chromium.launch({ proxy, args })` or `launchPersistentContext(dir, { recordHar, recordVideo, proxy, serviceWorkers })`. Those options are never screened.
  - (creation-guard.ts on main:32-44 treats an overridden fixture as "sanctioned", and `launch` is refused only while armed.)
  - **Fix:** in Lane B, refuse `launch`/`launchPersistentContext`/`launchServer` at ANY time after configuration load, as `connect` already is. Lane A's D13g is unchanged.
  - **Tests:** D21h is extended with fixture-override specs, including a "Lane-B launch refusal off" mutation.

- **R3-2 (REQUIRED).** `worker-end` counts signal records WRITTEN, so a failed write (unhandled inside an async listener) disappears from both sides of the comparison.
  - **Fix:**
    - N counts signals OBSERVED, incremented synchronously BEFORE the write;
    - write failures are counted in `worker-end`;
    - the scanner withholds if N differs from the records on disk, or the failure count is above zero;
    - every `signal` record carries the worker's token;
    - a read that rejects counts like an unresolved one.
  - **Test:** a third D20h half (a forced write failure, red under the "written count" mutation).

**NITs:**
- **NIT 1:** bind the C1 outcome record to the run's inventory nonce.
- **NIT 2:** `markerTitle` reads the canary-minted marker from `.vizra-e2e/secret/` and never mints its own.
- **NIT 3:** add `routeFromHAR(…, { update: true })` to the Lane-B lint list.
- **NIT 4:** state whether Lane-B and canary workers also write start/end pairs.

**Q-r3-1: no benign-header list; this is O-1's expiry.**
- A CSRF scheme brings a response `Set-Cookie`, which taints Lane A anyway.
- A list would be the first fail-open exception in this control.
- At M1, Lane A becomes summary-only.
- Record this in AGENTS.md § Residuals and in the ADR-003 notes.

**SEAT VERDICT: CHANGES STILL REQUIRED** (R3-1, R3-2 only). The seat states that the chair may confirm both by checking the text, with no further seat pass.

**Chair ruling (tick 209):** R3-1, R3-2 and NITs 1–4 are accepted, and Q-r3-1 is adopted as the seat answered it. The builder amends the plan to revision 4, and the chair confirms R3-1 and R3-2 in the text. Phase 2 starts after that and after user #10 merges.

## Seat check of plan revision 4 — R3-1 deviation, R3-2 (tick 211) — recorded by the chair

**Measured at source (Playwright 1.63.0):** the built-in `browser` fixture calls `launch()` with NO arguments. The options travel in `playwright._defaultLaunchOptions`:
- the `_browserOptions` auto fixture sets them to `{ handleSIGINT: false, ...launchOptions, tracesDir, artifactsDir, headless[, channel] }` (`playwright/lib/index.js:196-205, :231`);
- `BrowserType.launch` merges them itself (`coreBundle.js:63301`; the same for `launchServer` :63317 and `launchPersistentContext` :63323).

So any screen over the call's ARGUMENTS passes the runner's launch unconditionally, and a spec's `test.use({ launchOptions: { proxy, args } })` gets through.

**Answers:**
1. **The once-per-worker form is sound**, and the deviation from the literal R3-1 is accepted, on three conditions: the screen reads the EFFECTIVE options; the slot is consumed before calling through; the counter is per worker process and shared across browser types.
2. **Deep equality on the effective merged options** `{ ...this._playwright._defaultLaunchOptions, ...args }`, against an exact literal:
   - `{ handleSIGINT: false, artifactsDir: path.join(<project outputDir>, ".playwright-artifacts-" + workerIndex), tracesDir: path.join(<artifactsDir>, "traces"), headless: <boolean> }`;
   - sources: `runner/index.js:5466`, `workerProcessEntry.js:530`;
   - only `headless` varies; `channel` is absent; the user part is `{}`;
   - a key added by a future version fails closed.
3. **A `browser` override that runs first gains nothing**, given R4-1.

**Findings:**
- **R4-1 (REQUIRED):** the launch screen reads the effective merged options, not the call's arguments. Tests in D21h:
  - `test.use({ launchOptions: { proxy } })` with no override: refused;
  - `launchOptions.args` carrying a proxy switch: refused;
  - mutation "screen reads call arguments only": both accepted.
- **R4-2 (REQUIRED):** spec-level `test.use` is a second options surface the config `use` allowlist never sees.
  - **Fix:** the Lane-B harness fixtures assert that the effective option fixtures (`trace`, `screenshot`, `video`, `launchOptions`, `connectOptions`, `contextOptions`, `proxy`, `serviceWorkers`, `baseURL`, `storageState`, `httpCredentials`, `extraHTTPHeaders`, `ignoreHTTPSErrors`) deep-equal the project's configured values, and throw and record otherwise. Add a lint warning for `test.use(` in `e2e/authenticated/**`.
  - **Test:** a `test.use({ trace: "on" })` spec is refused; the "fixture assertion off" mutation lets it pass.
- **R3-2:** confirmed.
- **NIT:** update the record schema at plan:584-591: `kind: start|end|worker-start|worker-end|signal`, plus `token`, `signals`, `writeFailures` and the read kinds.

**SEAT VERDICT: CHANGES STILL REQUIRED** (R4-1, R4-2 are text amendments). The chair may confirm them in the text with no further seat pass.

**Chair ruling (tick 211):** accepted. The chair's deep-equality proposal is superseded by R4-1, which applies deep equality to the EFFECTIVE options. The builder amends the plan to revision 5, and the chair confirms R4-1, R4-2 and the NIT in the text.
