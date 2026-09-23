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
