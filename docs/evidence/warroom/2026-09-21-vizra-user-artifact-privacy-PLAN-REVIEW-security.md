# vizra-user artifact privacy II — PLAN review by the `vizra-security` seat, with the chair's rulings

- **Reviewed:** the builder's phase-1 plan `docs/plans/2026-09-21-vizra-user-artifact-privacy.md` (no code exists yet), against vizra-user `main@6bf0a0e` and the installed Playwright 1.63.0
- **Reviewer:** `vizra-security` council seat (agent `a5c8c6dd5ceced131`), read-only; did not run Playwright
- **Date:** 2026-09-21
- **Kind:** specialist review of a PLAN before code. Not a verifier verdict.

## Chair rulings (2026-09-21, tick 97) — binding input to phase 2

The seat's verdict: the architecture survives intact (Lane A / Lane B split by Playwright INVOCATION; "not produced" as the control; "path, not option"), and eight things must change before code. **Every finding is adopted.** Rulings and the one structural change the chair adds:

1. **Two PRs, not one.** This harness area has failed independent verification five times; a single PR carrying both the debts and a new authenticated lane is too large to verify well.
   - **PR A — "close today's gaps in the lane that exists"** (no new lane, the hard rule still stands): debts (a) `worker-guard.ts:70-71` + ledger regeneration, (b) tokenising lane check incl. the seat's shadowed-callee addition, (c) `globalSetup`/`globalTeardown` refusal; FINDING 3(1) drop `playwright-report/index.html` from the upload set and record in the VZ-FOUND-008 evidence README that the earlier "0 live queries" measurement never searched its base64-embedded archive; FINDING 8 the workflow-FILE-wide assertions (literal upload paths from a fixed allowlist, `uses:` allowlist incl. `actions/cache`, no reusable workflows, no `$GITHUB_STEP_SUMMARY` in the e2e job, `include-hidden-files` absent/false — verify the pinned action's default, `.vizra-e2e` in no `path:` of ANY workflow); FINDING 9 `package.json` scripts byte-equal to documented literals + refused `DEBUG`/`PWDEBUG`/`PLAYWRIGHT_*` env keys; FINDING 10 `PLAYWRIGHT_NO_COPY_PROMPT=1` at job level, asserted; FINDING 13 one sanitiser for externally-sourced text (CR/LF, leading `::`, length cap) beside the URL redaction; `redact.ts` and `redact-artifacts.sh` fixed for scheme-less and authority-relative URLs (F13 of the PR #3 review / FINDING 4's second half); FINDING 19 retention ≤ 3 days, visibility stated (all four repositories are PRIVATE — chair checked with `gh repo view` on 2026-09-21 — so artifacts and logs are readable by collaborators, not the world; say exactly that).
   - **PR B — "the authenticated lane"** (lifts the hard rule): Lane B config + structural rule; FINDING 1 (`headersArray()`, credential-shaped body parameter NAMES, the settle-window dependency made explicit), FINDING 2 (patch `APIRequestContext.prototype.fetch`; the interim refuse-outright option only if the patch proves fragile — say which and why), FINDING 6 (per-invocation taint; request-side credential FAILS the test, response-side `Set-Cookie` TAINTS and suppresses the upload with a named message), FINDING 11 (egress allowlist via `context.route` + the APIRequestContext patch; the auth config never reads `E2E_BASE_URL`), FINDING 4 (summary = allowlisted structured fields, no free text), FINDING 5 (write → scan → print; scan `if: always()`), FINDING 12 (summary URLs reduced below path level; residual stated), FINDING 15 (`.vizra-e2e/secret/` vs `.vizra-e2e/out/`), FINDING 3(2,3) + 16 + 21 (scanner: base64 → archive recursion, credential-SHAPE detectors with a recorded false-positive corpus, bounds sized from measured artifacts with their own exit code, depth 4), FINDING 7 + 22 (one config; positive control — every marker FOUND with recorders on in a scratch dir before asserting absence; vacuity guards; ~8 unique mutations), FINDING 14 (per-file tripwire exemptions with acceptance IDs, `npm run ci` green at every commit boundary, sweep extended to `e2e/harness/authenticated.ts`), FINDING 20 (the AGENTS.md sentence written LAST, every clause mapped to a demonstration ID), FINDINGS 17/18 stated as residuals with the named trigger (first spec rendering media moves its project to screenshot/video off).
2. **O-1** Lane A keeps uploading for M0 only, under the four mechanical conditions the seat lists. **O-2** floor ≥ 1 per Lane-B project, pinned by the canary. **O-3** refuse `void f()`, general call-and-discard review-only, plus the shadowed-callee refusal. **O-4** no exception: redirect to a file (`> .vizra-e2e/out/auth-lane.log 2>&1`), scan and print as separate ordered `if: always()` steps. **O-5** the chair lands the seat's trimmed ledger text through the generator once PR B is verified. **O-6** names only from a fixed allowlist; never echo an arbitrary observed header or body-parameter name.
3. The builder's disagreement with the chair's brief (Lane B recorders `off` rather than "retained on the runner") is ACCEPTED — the seat agrees an unuploaded trace is still reachable by every later step.
4. Both PRs get an independent verifier; PR B additionally gets this seat's review of the code before any merge.

The seat's report follows verbatim.

---

I read the plan in full, the meta and component `AGENTS.md`, the e2e workflow, `check-e2e-lane.mjs`, `redact-artifacts.sh`, `sweep-artifacts.sh`, `redact.ts`, `browser-errors.ts`, `worker-guard.ts`, `no-credentials-in-specs.test.ts`, `playwright.config.ts`, and the installed Playwright 1.63.0 (types + `playwright/lib/index.js`, `errorContext.js`, `runner/index.js`, `program.js`). I did not run Playwright, did not create a branch, and wrote nothing into either repo.

Verdict up front: the plan's **shape** is right — default-deny on artifact *content*, per-invocation split, path as the control rather than an option — and Decision 1 and Decision 5 are correct. But the piece the plan calls "THE CONTROL" (Decision 3.2, the worker guard observing authentication on the wire) **cannot detect a sign-in on the installed Playwright**, and the plan's own summary step reintroduces exactly the redaction-of-free-text it declines for traces. Plus there is a leak channel in the tree today that neither the redactor nor `sweep-artifacts.sh` can reach and that the 22-row table has no row for.

---

# BLOCKING-BEFORE-CODE

```
FINDING 1: the "credential on the wire" control cannot see a sign-in — the two
           header reads it relies on omit cookies by API contract, and a login
           POST carries no header at all
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     docs/plans/2026-09-21-vizra-user-artifact-privacy.md:266-299 (Decision 3.2),
             :538-567 (the AGENTS.md replacement sentence),
             node_modules/playwright-core/types/types.d.ts:22309-22315 (Request.headers),
             :22572-22576 (Response.headers), :22245 (allHeaders), :22322 (headersArray)
             e2e/harness/browser-errors.ts:112-119 (today's listeners)
  requirements: VZ-FOUND-008

Observed:
  The installed 1.63.0 types say, for Request.headers():
    "Note that this method does not return security-related headers, including
     cookie-related ones. You can use request.allHeaders() … for complete list of
     headers that include `cookie` information."
  The identical sentence appears for Response.headers() at :22572. `allHeaders()`
  and `headersArray()` both return a Promise. The plan's guard is described as
  reading "response headers it already receives" synchronously in a `request` /
  `response` listener.

Failure:
  Three of the four signals the control is built on are unreachable the way the
  plan describes them:
  - `Cookie` on a request  — omitted by `headers()`;
  - `Set-Cookie` on a response — omitted by `headers()`;
  - and the canonical authenticated action, a sign-in, has NEITHER. `POST /login`
    with `{email, password}` carries no Authorization header, no Cookie (there is
    no session yet) and no signature-shaped query parameter. It is a request BODY,
    and request bodies are not in the plan's signal list at all. The only signal a
    login produces is the `Set-Cookie` on the response — the one `headers()` drops.
  So a Lane-A spec that signs in the ordinary way passes the guard, and its
  password, its session cookie and the whole authenticated page land in a trace
  that Lane A uploads for 14 days. The AGENTS.md replacement sentence asserts the
  opposite ("all four end with a credential on the wire … so they are all red"),
  and would be published as a control that does not exist.

Perspective: developer, then member (the first real session cookie published)

Recommendation:
  1. Read headers through `request.headersArray()` / `response.headersArray()`
     (async) and land the result in the same append-only worker buffer the guard
     already uses — the 250 ms settle window in browser-errors.ts is what makes an
     async record still chargeable to the right test; make that dependency explicit
     rather than incidental.
  2. Add request `postData` / `postDataBuffer` to the signal list, matched by
     PARAMETER NAME only (`password`, `passwd`, `secret`, `token`, `otp`, `code`,
     `client_secret`, `refresh_token`) plus `Content-Type: …/x-www-form-urlencoded`
     or JSON with such a key. Record the key name, never the value.
  3. Restate the AGENTS.md sentence to claim only what is implemented (see
     FINDING 20).

Acceptance criteria:
  - A Lane-A spec that POSTs a form with a `password` field to the fixture server
    FAILS, naming the field name and not its value.
  - A Lane-A spec that receives a `Set-Cookie` FAILS or taints (per FINDING 6),
    demonstrated with a fixture that sets one.
  - A unit test asserts the guard never calls `request.headers()`/`response.headers()`
    for a credential decision (grep-level is fine as an early warning; the runtime
    demonstration is the control).

Tests:
  e2e/harness/browser-errors.test.ts: new cases for headersArray-sourced records.
  New red halves in npm run e2e:demos: "login POST in Lane A", "Set-Cookie in Lane A".
  The harness to run these exists.

Cross-repo implications:
  core: none. user: as above. search: none. meta: the ledger privacy case (O-5)
  must not claim header/cookie detection until this lands.

Challenge:
  "The control is not the guard, it is the path — Lane B writes nothing into an
  upload path, so a missed signal costs nothing." True for Lane B. It is false for
  Lane A, which is where the guard is the ONLY thing standing between an
  accidental sign-in and a published trace, and Lane A is the lane the plan keeps
  uploading (O-1).
```

```
FINDING 2: the guard is blind to APIRequestContext, and the trace is not — a
           Lane-A spec can authenticate through `page.request` with nothing red
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     node_modules/playwright-core/types/types.d.ts:9386-9395 (BrowserContext
             'request' — "Emitted when a request is issued from any pages created
             through this context"), :10991-10993 (context.request), :5836-5842
             (page.request); vizra-user/AGENTS.md § Residuals ("The `request`
             fixture is out of the guard's scope, by design")
             plan:266-299 (Decision 3.2), plan:194 (AP-4)
  requirements: VZ-FOUND-008

Observed:
  The context `request` event is documented as firing for requests issued FROM
  PAGES in that context. `context.request` / `page.request` is an APIRequestContext;
  its traffic is not a page request. The repository already records this as a known
  residual for the 404 case. The plan adds a `request` listener at the same
  BrowserContext level and then claims the resulting control is structural.

Failure:
  `await page.request.post('/login', { data: { password } })` followed by
  `page.goto('/')` gives a spec a real session in Lane A: cookies from an
  APIRequestContext are shared with the context (types.d.ts:10991), so the page is
  authenticated. The guard sees no request, no Set-Cookie, no addCookies, no
  storageState. Playwright DOES record APIRequestContext calls in the trace. So the
  one path that produces zero guard signals produces a full artifact — and AP-4's
  demonstration list (the tripwire's four measured evasions) does not include it,
  so the slice would ship believing it covered.

Perspective: developer, member

Recommendation:
  Patch `APIRequestContext.prototype.fetch` (and the get/post/put/… sugar that
  routes through it) in `e2e/harness/creation-guard.ts`, using exactly the
  prototype-patch-at-module-load discipline that file already uses for
  `BrowserType.prototype` and `Browser.prototype`, and record the same
  name-only signals. In a Lane-A project, a credential-shaped APIRequestContext
  call fails the test; in Lane B it is permitted and recorded.
  Cheaper interim if that proves fragile: REFUSE `context.request`/`page.request`
  in Lane-A projects outright (nothing in e2e/specs uses it today — verify before
  choosing this), and say so in AGENTS.md.

Acceptance criteria:
  - A Lane-A spec that authenticates via `page.request.post` is RED at runtime, by
    name, with a transcript.
  - The same spec under a Lane-B project is green.
  - AP-4's evasion list gains this route and the `document.cookie`-via-evaluate and
    `page.localStorage.setItem` routes (types.d.ts:5831 — `page.localStorage` exists
    in 1.63.0 and never touches the wire).

Tests:
  e2e/harness/creation-guard.test.ts (unit, prototype identity), plus a D-numbered
  red/green pair. Harness exists.

Cross-repo implications: none.

Challenge:
  "APIRequestContext is a testing tool; no honest spec would authenticate with it."
  Honest specs will: seeding an owner account before a UI test is exactly what
  `request.post` is for, and M1's owner-claim slice is the first customer. This is
  the idiom-not-evasion case the beforeAll finding already taught this repo.
```

```
FINDING 3: playwright-report/index.html carries a base64 ZIP of the entire report
           dataset; the redactor and the sweep are both blind to it, and the
           threat table has no row for it
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     node_modules/playwright/lib/runner/index.js:3704-3712 (_writeReportData)
             scripts/ci/redact-artifacts.sh:138-163 (unpacks `*.zip` only)
             scripts/e2e/sweep-artifacts.sh:61 (raw `grep -ral`, no decoding)
             .github/workflows/e2e.yml:176-186 (uploads playwright-report/)
             plan:339-362 (T20 names only playwright-report/data/*.zip)
  requirements: VZ-FOUND-008

Observed:
  Verified in the working tree, from a GREEN local run:
    playwright-report/index.html contains
      <template id="playwrightReportBase64">data:application/zip;base64,…</template>
    decoding it yields 13,965 bytes, magic 504b0304, four members:
      760d72a3746ac5132f88.json, d318381359a9b96acb1e.json,
      6b4388e26f27a8edc554.json, report.json
    report.json begins {"metadata":…,"files":[{"fileName":"health.spec.ts","tests":
      [{…"annotations":[{"type":"vizra-harness-stamp","description":"affc83b4…"}]…
      "results":[{"attachments":[{"name":"browser-…
  On a FAILING run these per-file JSONs carry the error messages, the step titles
  and subtitles (F13's channel), stdout/stderr and inline attachment bodies.
  `redact-artifacts.sh` runs perl over index.html as text — it rewrites the
  plaintext and cannot touch the base64 payload; it unpacks `*.zip` FILES only.
  `sweep-artifacts.sh` greps raw bytes of a copy with `.zip` files unpacked — it
  cannot see base64 either.

Failure:
  Every "verified end to end" claim about redaction was measured with a search
  blind to this file. AGENTS.md's "239 `?<redacted>`, zero live queries" and D9's
  "3 members → 0" are therefore true of the channels searched and unproven for this
  one. Today nothing private exists, so this is not a live incident — it is a fifth
  URL shape after four rounds, and it is the shape the plan's own scanner must be
  designed for BEFORE code, not after the first miss.

Perspective: developer now; member from M1

Recommendation:
  1. Add a threat row T23: "the HTML report's base64-embedded report archive inside
     index.html". Control for Lane A: either drop `playwright-report/index.html`
     from the upload set (the `data/` trace zips remain diagnosable via
     `npx playwright show-trace`), or teach the redactor to decode → unzip →
     redact → rezip → re-encode. Prefer dropping it; per Decision 1's own logic, a
     re-encode step is a fifth prediction.
  2. The scanner MUST treat "decoded bytes whose magic is an archive" as an archive
     and recurse — the plan's recursion is over archives found as FILES, and gzip
     magic only. A base64 run that decodes to `PK\x03\x04` is the measured case.
  3. `sweep-artifacts.sh` is the tool AGENTS.md names for "the first authenticating
     spec proves its coverage". It must gain the same decode-then-recurse, or stop
     being named as that proof.

Acceptance criteria:
  - A planted marker in an assertion message is found by the new scanner inside
    index.html's base64 payload (red half), and is absent after the control (green).
  - `bash scripts/ci/check-e2e-lane.sh` fails if an upload path includes
    `playwright-report/index.html` while the redactor has no decode stage.

Tests:
  scripts/ci/scan-artifacts_test.mjs: "marker inside a base64-embedded zip inside an
  HTML file" — a case the plan's ≈22 does not currently contain.

Cross-repo implications:
  meta: the VZ-FOUND-008 evidence README should record that the earlier "0 live
  queries" measurement did not search this channel.

Challenge:
  "The base64 blob is just a copy of results.json, which is already in the upload
  set, so it adds no new leak." Correct as of today's reporter list — but
  results.json is REDACTED in place and the base64 copy is not, so after redaction
  they disagree, and the unredacted one is the one nobody looks at.
```

```
FINDING 4: the generated summary is redacted free text, which is the exact control
           Decision 1 rejects — and it inherits F13 through redact.ts
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     plan:392 (inventory step 3), plan:357 (T17), plan:259
             e2e/harness/redact.ts:58-63 (`(?:https?|wss?|ftp)://` only)
             node_modules/playwright/lib/errorContext.js:47-98 (what an error message
             and its code frame contain)
  requirements: VZ-FOUND-008

Observed:
  Step 3 writes "the error message through redact.ts + the marker/secret scrubber,
  URLs with query and fragment dropped". `redact.ts:62` matches only scheme-ful
  URLs — the same defect as F13, in the module the summary depends on, and the
  plan's commit (d) fixes only `scripts/ci/redact-artifacts.sh`. Separately, a
  Playwright error message is free text that routinely contains: the assertion's
  received value verbatim; the locator, which for `getByText('…')` is page text; the
  navigation URL on a goto failure, with its query; and a call log.

Failure:
  The plan argues at length (Decision 1) that value-shaped redaction is undecidable
  without knowing the value — and then makes the ONLY file Lane B uploads a
  value-shaped redaction of attacker-adjacent free text. A single `expect(token).
  toBe('…')` in an authenticated spec puts a live credential into the one artifact
  the design promises is clean, and the scanner only catches it when a canary
  marker happens to be that value.

Perspective: developer, member

Recommendation:
  Make the summary an ALLOWLIST of structured fields, with no free text at all:
    project, spec path, line, full title path, status, retry, duration_ms,
    error_count, error_class (matcher name or Error.name only, itself validated
    against a compiled allowlist), timed_out (bool), and a reproduce hint
    (`npm run e2e:auth:local -g "<title>"`).
  No message, no stack, no locator, no URL. If a URL is judged indispensable later,
  it goes in as `origin + path-depth` (not the path — see FINDING 12), and that is a
  separate, reviewed change.
  Fix `redact.ts` for the scheme-less and authority-relative forms in the same
  commit as (d) regardless, because the harness still prints messages in Lane A.

Acceptance criteria:
  - The summary file is produced by serialising a typed object with a fixed key set;
    a unit test asserts that adding a key fails the test, and that no value in the
    file originates from `TestError.message`, `.stack`, `.snippet` or an attachment
    body.
  - The canary asserts the summary still names project, file and title (the existing
    inverse control from sweep-artifacts.sh) AND contains no marker even when every
    marker is placed in an assertion's received value.

Tests:
  e2e/harness/private-summary-reporter.test.ts (vitest, new): feed a synthetic
  TestResult whose message, stack and attachments all contain a marker; assert the
  emitted summary is byte-identical to one produced from a marker-free result.

Cross-repo implications: none.

Challenge:
  "A status-only summary makes a red authenticated lane undebuggable." It makes it
  reproducible-only-locally, which is precisely what Decision 1 and the
  `e2e:auth:local` story already decided. Error CLASS plus title plus line is
  enough to know which test and which assertion; the value never was the thing CI
  was allowed to show you.
```

```
FINDING 5: the summary is printed to the unredactable GitHub log BEFORE it is
           scanned, and on a green run it is printed with no scan at all
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     plan:388-399 (inventory steps 3, 5, 6): step 3 `if: always()` "Then
             prints that file and exits the captured code"; step 5 (`id: scan`)
             `if: failure()`; plan:361 (T21)
  requirements: VZ-FOUND-008

Observed:
  The order in the inventory is: 3 summarise+print (always) → 4 redact (failure) →
  5 scan (failure) → 6/7 upload (gated on scan). The scanner is the backstop for
  the summary (T17 says so: "a marker in a message is caught by S over the summary")
  but it runs two steps after the summary has already been written into the job log.

Failure:
  The one artifact that cannot be recalled — the GitHub job log, which for a public
  repository is world-readable and is also captured in the runner diagnostic log
  archive — receives the summary before any check has looked at it. And when the job
  is GREEN, `failure()` is false, so the scan never runs and step 3 still prints.
  The backstop is behind the thing it backs.

Perspective: developer, member, operator

Recommendation:
  - Step ordering: write → scan → print. The scan step becomes `if: always()`.
  - Printing happens in a step AFTER the scanner, gated on
    `steps.scan.outcome == 'success'`, exactly as the uploads are.
  - If scanning fails, print one fixed sentence ("the authenticated lane failed;
    its summary was withheld because the artifact scan did not pass") and nothing
    derived from the run.
  - `check-e2e-lane.mjs` asserts the index ordering and the gate, with a
    require-checks_test.sh mutation that moves the print before the scan (RED).

Acceptance criteria:
  A workflow mutation that prints the summary before the scan step, and one that
  leaves the scan on `if: failure()`, are each RED in require-checks_test.sh.

Tests: scripts/ci/require-checks_test.sh, two new cases.
Cross-repo implications: none.

Challenge:
  "The scan can't fail on the summary anyway, because the summary is allowlisted
  (FINDING 4)." Defence in depth is the whole argument of this slice; and the
  ordering bug costs one line to fix.
```

```
FINDING 6: one global taint file makes Lane B's normal operation permanently gate
           Lane A's uploads — and, once M1 ships session middleware, an honest
           Lane-A test fails on the app's own Set-Cookie
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     plan:300-319 (Decision 4), plan:487 (scanner fails closed if
             `.vizra-e2e/taint.json` says tainted), plan:284-291 (the Set-Cookie signal)
  requirements: VZ-FOUND-008

Observed:
  "the worker guard writes `.vizra-e2e/taint.json` whenever any auth signal is
  observed in any lane" and "the scanner fails closed if that file says tainted".
  Lane B is authenticated by construction, so Lane B always produces auth signals.
  One file, two lanes, same directory.

Failure:
  Two distinct failure modes, and they pull in opposite directions:
  (a) Lane B runs → taint=true → the scanner fails closed → nothing uploads, ever,
      including the summary that Lane B exists to produce. The predictable repair
      under time pressure is "don't write taint in Lane B", which deletes the signal
      for the case it was built for.
  (b) `Set-Cookie` as a test-failing signal conflates "this test authenticated" with
      "the application under test set a cookie". M1 ships sessions, CSRF and
      locale/preference cookies on anonymous pages. Every honest Lane-A test then
      fails, and the repair under pressure is to delete the Set-Cookie signal.

Perspective: developer, then everyone (a control that gets deleted protects nothing)

Recommendation:
  1. Taint is PER INVOCATION: `.vizra-e2e/taint.<lane>.<runId>.json`, written by
     every lane always (including "clean"), and the scanner requires the file for
     the lane whose artifacts it is about to gate. A missing file is still FAIL.
  2. Split the two consequences that the plan merges:
     - a request-side credential (Authorization / Cookie / credential-shaped body /
       storageState / addCookies) in Lane A FAILS THE TEST — that is authorship;
     - a response-side `Set-Cookie` from the app in Lane A TAINTS the run and
       suppresses the Lane-A upload with a named message, and does not fail the
       test — that is the app's behaviour, not the spec's.
  3. The named message matters: "artifacts withheld — an authentication signal was
     observed in this run" is diagnosable; a silent empty artifact is not.

Acceptance criteria:
  - Lane B green + Lane A red ⇒ Lane A's artifacts still upload (the canary proves
    this; it is the case a single taint file breaks).
  - A fixture that returns `Set-Cookie` on an anonymous page ⇒ Lane A test PASSES,
    upload SUPPRESSED, message names the reason.
  - A Lane-A spec sending `Authorization` ⇒ test RED.

Tests:
  New red/green halves in e2e:demos for each of the three rows above.

Cross-repo implications:
  core: when core ships an anonymous CSRF cookie, this rule decides whether the
  frontend lane can keep uploading traces at all — worth one line in the ADR-003
  notes so it is not discovered in CI.

Challenge:
  "Set-Cookie on an anonymous page IS a privacy event — the cookie value is in the
  trace." Yes, which is why it still suppresses the upload. What it must not do is
  fail a test the author wrote correctly; a control that punishes honest work is
  removed within two sprints.
```

```
FINDING 7: the canary proves a third config, and "zero markers found" is
           indistinguishable from "nothing was planted"
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     plan:413-448 (the canary), plan:531 (commit (e) creates
             `playwright.canary.config.ts`), plan:191 (AP-1 says "running the
             authenticated lane"), plan:252-262 (Lane B is playwright.auth.config.ts)
  requirements: VZ-FOUND-008

Observed:
  AP-1 claims the acceptance is about "the authenticated lane". Commit (e) adds a
  separate `playwright.canary.config.ts`, and the canary spec lives in `e2e/canary/`
  while Lane B's testDir is `./e2e/authenticated`. So the artifacts the scanner
  walks are produced by a configuration that is NOT the one that ships.
  Separately, every assertion in the canary is an ABSENCE assertion (zero markers,
  no .png/.webm/.jpeg). error-context.md is only written when
  `this._testInfo.errors.length > 0` (playwright/lib/index.js:700), so a canary spec
  that accidentally passes, is skipped, or never reaches the fixture server produces
  almost nothing and scans clean.

Failure:
  This is the failure mode this repository has hit repeatedly: a demonstration that
  demonstrates a neighbour of the thing. A divergence between the canary config and
  the auth config — a reporter, an outputDir, `trace` — makes AP-1 a true statement
  about a file nobody runs. And a vacuous green canary is a green light for every
  M1 auth slice.

Perspective: developer, verifier

Recommendation:
  1. One config. `playwright.canary.config.ts` must `import` the auth config and
     override ONLY `testDir`/`testMatch`, or — better — the canary spec lives under
     `e2e/authenticated/` with a `.canary.ts` suffix and is selected by testMatch.
     A unit test asserts the two configs are deep-equal on the privacy-relevant keys
     (`use.trace`, `use.screenshot`, `use.video`, `outputDir`, `reporter`,
     `globalSetup`, `globalTeardown`), and `check-e2e-lane.mjs` refuses a config it
     was not told about.
  2. POSITIVE CONTROL, and this is the part that is missing entirely: the canary
     must first prove the plant WORKED. Run the identical spec once with
     trace/screenshot/video ON into a scratch directory that is in no upload path,
     and assert that EVERY marker IS found there. Only then run the shipped config
     and assert none is in the would-be-upload set. Without the first half, "0
     markers in N files" is a sentence about a spec that may have done nothing.
  3. Fail-closed on vacuity: the canary asserts a non-zero count of tests run, a
     non-zero count of fixture-server requests served, and a non-zero count of
     produced output files, before it evaluates any absence.

Acceptance criteria:
  - `--mutate=fixture-unreachable` (the fixture server not started) ⇒ canary RED,
    naming "planted nothing".
  - `--mutate=spec-skipped` (test.skip) ⇒ RED.
  - The recorders-on run finds 22/22 markers; the shipped-config run finds 0/22 in
    the upload set; both counts are printed.

Tests: scripts/ci/artifact-privacy-canary.mjs's own mutation set.
Cross-repo implications: none.

Challenge:
  "The per-row mutations (AP-2) already prove each control is load-bearing." They
  prove the CONTROL is load-bearing when the plant works. They do not prove the
  plant works in the shipped configuration, which is the one property AP-1 asserts.
```

```
FINDING 8: "the scanner reads the upload paths out of the workflow" is not
           default-deny — globs, expressions, `actions/cache`, step summaries and
           hidden-file inclusion all sit outside it
Severity:    BLOCKER
Confidence:  medium-high

Affected:
  repo:      vizra-user
  files:     plan:457-460 (scanner inputs), plan:394, plan:402
             scripts/ci/check-e2e-lane.mjs:110 (UPLOADER = /(upload|artifact)@/i),
             :160 (`workflow?.jobs?.e2e` — one job of one file), :375-388
             .github/workflows/supply-chain.yml:89,157 ($GITHUB_STEP_SUMMARY),
             :102-105,:177-180 (two more uploaders, another workflow)
  requirements: VZ-FOUND-008

Observed:
  - The scanner derives its scope from the same regex and the same single job the
    lane guard parses. `actions/cache` matches NEITHER `upload` nor `artifact`, and
    a cache is a publisher: its blob is readable by other workflow runs in the repo.
  - `actions/upload-artifact`'s `path:` accepts multi-line globs and `!` exclusions.
    A path of `.` or `**` or `test-*` cannot be disproved to contain `.vizra-e2e`
    by a prefix check; the plan's AP-5 assertion is a prefix check
    ("provably not inside any upload path… by path prefix").
  - `${{ }}` in a `path:` is not resolvable at parse time.
  - `$GITHUB_STEP_SUMMARY` and `::error::`/`::notice::` annotations publish to the
    run page and the Checks API and are in no `path:` list at all.
  - `actions/upload-artifact` v4 excludes hidden files by default
    (`include-hidden-files: false`), which is the only reason `test-results/.last-run.json`
    is not published today. UNVERIFIED: I did not read the pinned action's source,
    only its documented default — the builder must check before relying on it.

Failure:
  The scanner's scope is derived from a data structure an author can widen in ways
  the derivation cannot read. The result is a scanner that reports "0 markers in the
  paths I understood" while a path it did not understand publishes the tree.

Recommendation:
  Invert it. `check-e2e-lane.mjs` asserts, for the whole workflow FILE (every job,
  not `jobs.e2e`):
   a. every `with.path` entry of every uploader is a LITERAL from a fixed allowlist
      — no glob metacharacter (`*?[]!`), no `${{`, no `.`, no `..`;
   b. no step `uses:` anything outside a pinned allowlist (this also catches
      composite actions and `actions/cache`);
   c. no `jobs.*.uses` (reusable workflow) in this file;
   d. no step writes `$GITHUB_STEP_SUMMARY` in the e2e job;
   e. `include-hidden-files` is absent or `false`;
   f. `.vizra-e2e` appears in no `path:` in ANY workflow in `.github/workflows/`
      (a deny-list sweep across files, cheap, and it is where the stamp key lives —
      see FINDING 15).
  The scanner then consumes that literal allowlist rather than inferring it.

Acceptance criteria:
  require-checks_test.sh mutations, each RED: a glob in `path:`; a `${{ }}` in
  `path:`; `include-hidden-files: true`; an `actions/cache` step whose path is
  `.vizra-e2e`; a `$GITHUB_STEP_SUMMARY` write in the e2e job; a second job in
  e2e.yml with an uploader.

Tests: scripts/ci/require-checks_test.sh (six cases).
Cross-repo implications:
  meta: the same six assertions belong in whatever CI fan-in vizra-core grows.

Challenge:
  "An author who adds `actions/cache` for `.vizra-e2e` is doing something deliberate
  and review catches it." Review is the stated control for `run:` exfiltration
  because no parser can close it. A `uses:` allowlist IS closable by a parser, so
  leaving it to review is a choice to be weaker than necessary.
```

---

# REQUIRED-IN-THIS-SLICE

```
FINDING 9: the lane's argv is unchecked — `--trace on`, `--output test-results`
           and `--reporter html` defeat the entire design from package.json
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     node_modules/playwright/lib/program.js:207 (`--output <dir>`), :220
             (`--trace <mode>`), :213 (`--reporter <reporter>`)
             package.json:15 ("e2e": "playwright test")
             scripts/ci/check-e2e-lane.mjs:178-192 (matches `run: npm run e2e` exactly
             and never reads package.json)
  requirements: VZ-FOUND-008

Observed:
  The lane guard's strongest assertion is that one step's `run` is EXACTLY
  `npm run e2e`. What `npm run e2e` expands to is in package.json, which the guard
  never opens. `playwright test --trace on --output test-results` is a one-word edit
  to a file no gate reads, and it re-enables every recorder and moves Lane B's
  output into the upload path.

Failure:
  The plan's whole Lane-B guarantee is "outputDir is not in an upload path" and
  "trace is off". Both are overridable from a file outside every check.

Recommendation:
  `check-e2e-lane.mjs` reads package.json and asserts `scripts.e2e`,
  `scripts["e2e:auth"]`, `scripts["e2e:auth:local"]` and `scripts["e2e:demos"]` are
  byte-equal to documented literals — in particular that the auth script is exactly
  `playwright test --config=playwright.auth.config.ts` with no other flag. Also
  refuse `DEBUG`, `PWDEBUG`, `PLAYWRIGHT_HTML_REPORT` and `PLAYWRIGHT_*` env keys in
  the e2e job except an allowlist (a single `DEBUG=pw:api` turns Lane B's stdout
  into a full protocol dump with headers and fill values).

Acceptance criteria:
  require-checks_test.sh: appending `--trace on` to `scripts.e2e:auth` is RED;
  appending `--output test-results` is RED; adding `DEBUG: pw:api` to a step's env
  is RED.

Tests: scripts/ci/require-checks_test.sh, three cases.
Cross-repo implications: none.
Challenge: "package.json is a CODEOWNERS path." So is everything else this
  repository asserts in CI anyway; the point of the parser is that the property is
  invisible in a green run.
```

```
FINDING 10: PLAYWRIGHT_NO_COPY_PROMPT=1 removes the worst half of error-context.md,
            and the plan states it is ungated
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     node_modules/playwright/lib/index.js:657-671 (_takePageSnapshot:
             `if (process.env.PLAYWRIGHT_NO_COPY_PROMPT) return;` then
             `page.ariaSnapshot({mode:"ai"})`), :700-716 (the write)
             node_modules/playwright/lib/errorContext.js:74-118 (# Page snapshot,
             # Test source, buildCodeFrame with linesAbove/linesBelow = 100)
             plan:120-156 (M6: "No configuration option gates it")
  requirements: VZ-FOUND-008

Observed:
  M6 is right that no Playwright CONFIG option gates error-context.md, and right
  that the file is still written with trace/screenshot/video off. It is wrong that
  nothing gates its contents: the `# Page snapshot` section — the aria snapshot
  carrying every DOM text node and every input's CURRENT VALUE, i.e. the channel
  that captured the typed password in the builder's own measurement — is skipped
  entirely when `PLAYWRIGHT_NO_COPY_PROMPT` is set. Also worth correcting: the
  `# Test source` code frame is not "the spec source around the failure", it is
  ±100 lines read from `errorLocation.file` at run time, which for an error raised
  inside a helper is the HELPER's source.

Failure:
  Lane A keeps uploading `test-results/**/error-context.md` under O-1. Its page
  snapshot is the single richest private-data channel in the upload set — it is
  literally every text node of the rendered page, and the page is the product. A
  one-line env var removes it, and the plan does not use it because the measurement
  concluded the file was ungated.

Recommendation:
  Set `PLAYWRIGHT_NO_COPY_PROMPT: "1"` at JOB level in `.github/workflows/e2e.yml`
  (both lanes), never locally. `check-e2e-lane.mjs` asserts it is set, in the same
  idiom as the `E2E_COVERAGE_FLOOR` / `VIZRA_E2E_STAMP_KEY` assertions. Add a
  threat row: "error-context.md `# Page snapshot`" with this as its Lane-A control
  and the outputDir path as its Lane-B control (unchanged).

Acceptance criteria:
  A red Lane-A run in CI produces an error-context.md with no `# Page snapshot`
  section; the demonstration shows the section present without the variable and
  absent with it. Removing the variable from the workflow is RED in the lane guard.

Tests: e2e:demos, one red/green pair; require-checks_test.sh, one mutation.
Cross-repo implications: none.
Challenge: "It is an undocumented env var; Playwright may remove it." Then the
  demonstration goes red on the next bump, which is the correct outcome and is why
  it gets a demonstration rather than a comment.
```

```
FINDING 11: nothing constrains where Lane B may send the credential — no egress
            allowlist, and E2E_BASE_URL is an environment variable
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     playwright.config.ts:54-56 (baseURL from E2E_BASE_URL)
             plan:252-262 (Lane B), plan:591-597 ("no network beyond localhost" —
             asserted, not enforced)
  requirements: VZ-FOUND-008; propose VZ-FOUND-008b

Observed:
  Lane B is the first place in this repository that will hold a real credential.
  Nothing in the design stops a Lane-B spec from `page.goto('https://…')`, from
  `page.request.post` to an external host, or from an image `src` on a third-party
  origin — and nothing stops `E2E_BASE_URL` being pointed off-box. The plan's
  "localhost only" is a property of the fixture server, not of the browser.

Failure:
  The threat model here is not only "the artifact leaks". It is "the CI job, which
  will hold a session for the instance owner account, makes an outbound request".
  That is the outbound-fetch boundary, on the CI side, and it is unguarded. A
  dependency-confusion or compromised-action scenario turns one `page.goto` into
  credential exfiltration with no artifact involved at all.

Recommendation:
  In the worker guard (which already wraps every context creation), install a
  `context.route('**', …)` that ABORTS any request whose host is not in a compiled
  allowlist (`127.0.0.1`, `localhost`, `::1`, plus the baseURL host) and RECORDS
  the refusal as a guard signal, so `try/catch` does not hide it — the same
  discipline creation-guard.ts already uses (D13n). Note the known hole and state
  it: `context.route` does not intercept APIRequestContext, so FINDING 2's
  prototype patch must carry the same allowlist.
  Separately, `playwright.auth.config.ts` must NOT read `E2E_BASE_URL`; it pins the
  fixture server's ephemeral port from its own webServer block.

Acceptance criteria:
  - A Lane-B spec navigating to a non-allowlisted host is RED, naming the host.
  - The same via `page.request` is RED.
  - `check-e2e-lane.mjs` fails if the Lane-B step sets `E2E_BASE_URL`.

Tests: two D-numbered red/green pairs + one lane-guard mutation.
Cross-repo implications:
  core: the same allowlist question arises for core's integration tests once they
  hold tokens — worth one line in the meta AGENTS.md.
Challenge: "A route handler on every request slows the lane." Measured cost is one
  handler invocation per request against a localhost fixture; the existing 250 ms
  settle dominates it.
```

```
FINDING 12: a secret in a URL PATH segment is preserved by every redactor here, by
            design — and M1's reset/verify links are path secrets
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/redact.ts:22-27 ("origin and path survive"), :29-48
             scripts/ci/redact-artifacts.sh:88-92 (relative program keeps `$1$2`)
             plan:392 (summary keeps "origin and path")
  requirements: VZ-FOUND-008

Observed:
  Both redactors are query-and-fragment only, explicitly and for a good stated
  reason (the path is what makes a failure diagnosable). `redact.ts`'s own header
  names "a password-reset or invite link" as the hazard it exists for — and a
  password-reset link is `/reset/<token>`, a path.

Failure:
  The plan inherits this into the one file Lane B uploads and into the AGENTS.md
  sentence ("every URL reduced to origin and path"). For ADR-005 signed URLs the
  query is the secret; for reset, verify, invite, unsubscribe, share-link and
  IPFS-CID URLs the PATH is the secret. The published sentence would overclaim.

Recommendation:
  For the SUMMARY (the strict surface): reduce a URL to `origin + path segment
  count` or `origin + first segment`, never the full path. For the harness redactor
  and the artifact redactor: do not attempt path redaction (it would destroy the
  diagnosis Lane A exists for); instead state the residual precisely in AGENTS.md
  and make the shape scanner of FINDING 16 look for high-entropy path segments.

Acceptance criteria:
  A summary produced from an error whose URL is `/reset/<40 hex>` contains neither
  the token nor the path. AGENTS.md § Residuals gains a "path-segment secrets"
  bullet naming reset/verify/invite/share/CID.

Tests: private-summary-reporter unit test with a path-token URL.
Cross-repo implications:
  core: whether reset tokens go in the path or the body is core's call; a body
  token is strictly better for every log in the system. Worth raising in the M1
  auth slice.
Challenge: "No such URL exists yet." Correct — which is why this is a required
  sentence in the contract now and not a fix later.
```

```
FINDING 13: page-controlled text reaches the GitHub Actions log unsanitised —
            workflow-command injection, and the product's whole point is rendering
            other people's content
Severity:    REQUIRED
Confidence:  medium
Affected:
  repo:      vizra-user
  files:     e2e/harness/browser-errors.ts:104-110 (describeConsole copies
             `message.text()` through URL-only redaction into the failure message),
             :112-119; playwright.config.ts:91 (`list` reporter → stdout → job log)
  requirements: VZ-FOUND-008

Observed:
  A console message from the page under test is copied into a Playwright failure
  message, which the `list` reporter writes to stdout, which is the GitHub log.
  GitHub interprets `::workflow-command::` sequences at the start of a line in step
  output. The text passes through `redactUrlsInText` only.

Failure:
  Two classes. (1) Injection: page text containing a newline followed by
  `::add-mask::` / `::stop-commands::<token>` / `::error file=…::` manipulates the
  run's own log and annotations. (2) Content: from M1 this text is product content;
  from federation it is a remote instance's attacker-controlled display name,
  caption or error string. The E2E harness would be the first place Vizra prints
  remote content into a durable, world-readable log.

Perspective: operator, developer

Recommendation:
  One sanitiser applied to every externally-sourced string the harness prints or
  attaches: strip CR/LF, refuse a leading `::`, cap length (e.g. 200 chars), and
  escape `%0A`/`%0D`/`%25`. Apply it in `redact.ts` beside the URL redaction so
  there is one place. Unit-test it.

Acceptance criteria:
  A demo page whose console message begins with `::error::` produces a harness
  failure message in which that text is inert, demonstrated red/green.

Tests: e2e/harness/redact.test.ts + one demo pair.
Cross-repo implications:
  core: the same rule belongs in core's structured logging for remote actor fields.
Challenge: "The page under test is our own build." Today. The first federation
  test fixture makes it not ours, and by then the harness is load-bearing.
```

```
FINDING 14: the credential tripwire will go red on the canary and the authenticated
            specs, and the proposed repair is a directory-wide exemption the file
            itself forbids
Severity:    REQUIRED
Confidence:  high
Affected:
  repo:      vizra-user
  files:     e2e/harness/no-credentials-in-specs.test.ts:57-71 ("Nothing is exempt
             by being in a particular directory"), :111-123 (walks every .ts under
             e2e/ except harness/)
             plan:292-294 (Decision 3.3: "gains e2e/authenticated/** as an *allowed*
             directory"), plan:531 (the canary lives in e2e/canary/)
  requirements: VZ-FOUND-008

Observed:
  The sweep covers every `.ts` under `e2e/` except `e2e/harness/**` and has exactly
  one allow entry, per FILE, per PATTERN, with a written reason. The canary spec
  (e2e/canary/all-channels.canary.ts) plants `.fill(`, `Authorization`,
  `Set-Cookie`, `X-Amz-*` by design and is not in `e2e/authenticated/**`, so commit
  (e) turns `npm run ci` red before commit (g) exists.

Failure:
  The plan's ordering guarantees a red gate mid-slice, and the cheapest repair
  under pressure is the directory blanket — which converts a per-file, reasoned
  exemption into "anything under these two directories may do anything", and
  `e2e/authenticated/**` is precisely where the real credentials will live.

Recommendation:
  Keep the exemption per-file with a reason, add entries for the canary and for
  each authenticated spec as it is written, and require the reason to name the
  acceptance ID. Additionally: extend the sweep INTO `e2e/harness/**` for the new
  `authenticated.ts` (the existing harness exclusion is a stated evasion route, and
  this slice is the one that puts a credential fixture there) — at minimum assert
  that `e2e/harness/authenticated.ts` contains no literal credential and reads its
  values only from the environment.

Acceptance criteria:
  `npm run ci` is green at every commit boundary (a), (b)…(j) — demonstrated by
  running it at each, and recorded. No directory-wide allow entry exists.

Tests: the sweep's own vitest cases.
Cross-repo implications: none.
Challenge: "Per-file entries are churn." They are the mechanism by which adding an
  authenticated spec is a reviewed act, which is the slice's whole thesis.
```

```
FINDING 15: .vizra-e2e now holds the per-run stamp key, the markers, the taint file,
            the lane log and Lane B's output — one wrong path publishes the key that
            makes stamps forgeable
Severity:    REQUIRED
Confidence:  high
Affected:
  repo:      vizra-user
  files:     .vizra-e2e/stamp-key.json (present in the tree, mode 0600)
             .gitignore:/.vizra-e2e
             vizra-user/AGENTS.md (the stamp key "is written to .vizra-e2e/stamp-key.json
             only in onEnd"); plan:258, :391, :424, :487
  requirements: VZ-FOUND-008

Observed:
  The plan concentrates five different sensitivities in one directory that is
  currently protected by a single negative fact — it appears in no `path:`.

Failure:
  The blast radius of a single mistaken upload path is no longer "some traces". It
  is the per-run HMAC key, at which point the runtime stamp — the control this whole
  harness rests on — becomes forgeable for that run, and the markers become known,
  and the scanner's own inputs become attacker-visible.

Recommendation:
  - Separate the secret from the merely-private: keep `stamp-key.json` and
    `privacy-markers.json` in `.vizra-e2e/secret/` with 0700, and Lane B's output
    and log in `.vizra-e2e/out/`.
  - Deny-list `.vizra-e2e` across ALL workflow files (FINDING 8f), not just e2e.yml.
  - The scanner treats "any upload path that resolves under `.vizra-e2e`" as FAIL
    before it scans a byte, and says which path.

Acceptance criteria:
  A workflow mutation adding `.vizra-e2e/` to any upload path in any workflow is
  RED in the lane guard AND in the scanner, independently.

Tests: require-checks_test.sh + scan-artifacts_test.mjs, one case each.
Cross-repo implications: none.
Challenge: "Two directories is ceremony." The ceremony is the point: it makes
  "upload `.vizra-e2e/out`" survivable and "upload `.vizra-e2e`" impossible.
```

```
FINDING 16: in a real CI run the scanner proves nothing — there are no markers to
            find
Severity:    REQUIRED
Confidence:  high
Affected:
  repo:      vizra-user
  files:     plan:388-399 (uploads gated on `steps.scan.outcome == 'success'`),
             plan:457-495 (the scanner), plan:616-619 (Residuals, which says this
             quietly), scripts/e2e/sweep-artifacts.sh (the shape search that exists)
  requirements: VZ-FOUND-008

Observed:
  Markers are minted by the canary. A real PR run of the e2e lane has no canary
  markers in its artifacts. The scanner's own rule "marker file missing ⇒ exit 1"
  means the real run must be handed a marker file; whatever is in it will not be in
  the artifacts; the scan passes by construction.

Failure:
  The inventory presents the scan step as the gate on every upload. Read literally,
  a reviewer will believe a green scan means "these artifacts were checked for
  secrets". It means "the taint file said clean and none of today's canary markers
  appeared". The residual says so; the workflow does not, and the workflow is what
  people read.

Recommendation:
  Give the real run a non-vacuous job. The scanner gains SHAPE detectors, run over
  the same byte stream: `authorization:\s*(bearer|basic)`, `set-cookie:`,
  `__Host-`/`__Secure-` cookie names, `X-Amz-(Signature|Security-Token|Credential)`,
  `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.` (JWT), `-----BEGIN [A-Z ]*PRIVATE KEY`,
  and a high-entropy path/query segment heuristic. A hit FAILS the lane and prints
  the member NAME only. This is `sweep-artifacts.sh`'s existing discipline promoted
  into the gate, and it is what catches a secret in an UNMARKED channel.
  Then say plainly, in the step name: "Scan the would-be-upload set for canary
  markers and credential shapes".

Acceptance criteria:
  - A trace containing a Set-Cookie header fails the scan in a run with no markers.
  - The self-test covers one true positive and one false positive per shape, and
    the false-positive set is recorded so the shapes can be tuned rather than
    deleted the first time the lane goes red.

Tests: scripts/ci/scan-artifacts_test.mjs, ~14 more cases.
Cross-repo implications:
  meta: this is the same detector set a repo-wide secret scan would use; keep it in
  one file if it ever moves up.
Challenge: "Shape detection will false-positive and someone will disable it." Which
  is why the false-positive corpus is part of the acceptance, and why a hit
  suppresses the UPLOAD rather than failing the product lane.
```

---

# FOLLOW-UPS (with the slice they belong to)

```
FINDING 17: credential channels that never cross the wire are outside the control,
            and one of them is new in 1.63.0
Severity:    SHOULD
Confidence:  high
Affected: repo: vizra-user; files: node_modules/playwright-core/types/types.d.ts:5821-5831
  (`page.localStorage: WebStorage` — a first-class API in this version), plan:642-645
Slice: the M1 authenticated-UI slice (first spec under e2e/authenticated/).
Observed/Failure:
  `page.localStorage.setItem('token', …)`, `sessionStorage`, IndexedDB, a WebSocket
  frame and a service-worker-initiated request (Chromium-only reporting, gated on
  `serviceWorkers: 'allow'`; types.d.ts:22290, :22427-22431) all carry credentials
  without producing any of the guard's signals. The plan's residual says this in one
  sentence about "a credential held in a variable"; it is broader than that.
Recommendation: state each channel by name in § Residuals; add `page.localStorage`
  and `document.cookie`-via-evaluate to the ESLint early warning for e2e/specs/**;
  do not claim runtime coverage for them.
Acceptance: AGENTS.md lists the five channels; lint refuses the two spellable ones.
Tests: eslint-rules tests.
Cross-repo: none.
Challenge: "The scanner catches them in the canary." Only for marked channels —
  which is exactly the residual.
```

```
FINDING 18: the pixel channel — Lane A keeps screenshots, and a screenshot of a
            private photo is not greppable
Severity:    SHOULD
Confidence:  high
Affected: repo: vizra-user; files: scripts/ci/redact-artifacts.sh:42-48,:109-110
  (png/jpg/webm deliberately excluded), playwright.config.ts:117-118, plan:351 (T11
  covers Lane B only)
Slice: the first slice that renders any non-public media (M1 upload/photo page).
Observed/Failure: Lane A's `screenshot: only-on-failure` and `video:
  retain-on-failure` publish rendered pixels of whatever the page showed. From M1
  that includes a photo, an email address, an EXIF/GPS string. No scanner, no
  redactor and no marker reaches it; the canary's image channel proves only that
  marker BYTES in a PNG are found, not that a rendered secret is.
Recommendation: when the first private-media page exists, Lane A drops `video`
  entirely and `screenshot` becomes `off` for any spec touching media, or Lane A
  joins Lane B as summary-only (see O-1). Record now as the trigger condition.
Acceptance: a written trigger in AGENTS.md: "the first spec that renders media
  moves its project to screenshot/video off".
Tests: none until then.
Cross-repo: none.
Challenge: "Screenshots are the most useful artifact there is." Yes — locally.
```

```
FINDING 19: artifact visibility and retention are unstated
Severity:    SHOULD
Confidence:  medium
Affected: repo: vizra-user; files: .github/workflows/e2e.yml:185 (retention-days: 14)
Slice: this one if cheap, otherwise the M1 auth slice.
Observed: UNVERIFIED — I could not establish from the checkout whether
  `yegamble/vizra-user` is public. If it is, every uploaded artifact and every job
  log is world-readable for 14 days, and so is the log archive.
Failure: the AGENTS.md sentence should say who can read these, because "uploaded"
  reads as "available to the team" and may mean "available to everyone".
Recommendation: reduce Lane A retention to the shortest useful window (1–3 days) and
  state the visibility explicitly in the contract sentence.
Acceptance: retention-days ≤ 3 for the trace artifact; a sentence naming visibility.
Tests: require-checks_test.sh asserts the retention ceiling.
Cross-repo: meta — same question for core's CI artifacts.
Challenge: "14 days helps a slow review." A trace nobody downloaded in 3 days is a
  trace nobody needed.
```

```
FINDING 20: the proposed AGENTS.md sentence is stronger than the design
Severity:    REQUIRED (blocking for commit (j), not for (a)-(i))
Confidence:  high
Affected: repo: vizra-user; files: plan:538-567
Observed/Failure: four claims in the sentence are not true of the design as written:
  1. "…observes an Authorization, Cookie, Proxy-Authorization or Set-Cookie header …
     on the wire" — FINDING 1: `headers()` omits cookie headers, and a sign-in POST
     has none of these.
  2. "so the four evasions … are all red, because all four end with a credential on
     the wire" — false for a password in a request BODY (FINDING 1) and for
     `page.request` (FINDING 2).
  3. "walks every byte of every path the workflow would upload" — FINDING 8: it
     walks the paths it could parse, in one job of one file.
  4. "every URL reduced to origin and path" — FINDING 12: the path IS the secret for
     reset/verify/invite/share URLs.
Recommendation: rewrite after (a)-(i) land, claiming only what has a red
  demonstration, and append a residual paragraph naming: APIRequestContext (if not
  patched), non-wire channels (FINDING 17), pixels (FINDING 18), path-segment
  secrets, the scanner's canary-not-classifier limit, the world-readability of
  artifacts and logs, and that CODEOWNERS enforces nothing without a ruleset.
  The house style for this is already in § Residuals; match it.
Acceptance: every clause of the final sentence maps to a demonstration ID in
  docs/evidence/VZ-FOUND-008/.
Tests: none (documentation), but the mapping table is the review artifact.
Cross-repo: meta — the ledger case (O-5) must be trimmed the same way.
Challenge: "Hedged prose is weaker prose." This repository's own history is that
  the overstated sentence is the one that gets believed and then falsified.
```

---

# RULINGS ON O-1 … O-6

**O-1 — Lane A uploads traces?** Conditionally yes for M0 only, and the condition must be mechanical, not a promise: keep Lane A uploads, but (i) drop `playwright-report/index.html` from the upload set (FINDING 3), (ii) set `PLAYWRIGHT_NO_COPY_PROMPT=1` (FINDING 10), (iii) the per-lane taint gate self-closes Lane A the moment a session cookie or auth signal appears (FINDING 6), and (iv) FINDING 18's trigger moves Lane A to summary-only at the first private-media page. That is "yes" with an expiry date the CI enforces, which is the only form of "yes" I will sign.

**O-2 — coverage floor 0 for the two Lane-B projects?** Register them, but not at 0: the canary is a real Lane-B invocation, so pin it as the floor (≥1 per auth project) and keep the ratchet rule. A floor of 0 makes a Lane B that collects nothing exit 0 and report success, which is the vacuity mode this repo has already been bitten by twice.

**O-3 — call-and-discard: refuse or review-only?** Refuse the `void` form, record the general case as review-only — accept the builder's recommendation verbatim, including its honest sentence. Add one thing: the AST matcher must also refuse a call whose callee is shadowed by a local binding of the same name, or it trades a string defeat for a scope defeat.

**O-4 — allowlist the capture-and-re-raise shape?** Decline the exception; it is unnecessary. `run: npm run e2e:auth > .vizra-e2e/out/auth-lane.log 2>&1` preserves the exit code with no `||`, no `exit "$code"`, and no laundering shape to allowlist; the scan and the print become separate `if: always()` steps ordered after it (FINDING 5). The absolute "no exit-code handling in a lane step" rule stays absolute, which is worth more than the convenience.

**O-5 — the ledger privacy case text.** Accept the mechanism (meta builder lands it), trim the text to what will be demonstrated: *"VZ-FOUND-008 — no credential the harness holds, and no page content from an authenticated session, reaches an uploaded CI artifact or the job log: authenticated specs record no trace, screenshot or video, their output directory appears in no upload path, and the only artifact is a structured summary of allowlisted fields. Proved by an end-to-end canary with runtime-minted markers, positively controlled (markers demonstrated present with recorders on) and negatively controlled (absent in the shipped configuration), plus a credential-shape scan of every byte of every allowlisted upload path."* Status UNVERIFIED until the independent verifier returns PASS. Do not include "every byte of every path the workflow would upload" (FINDING 8) or any claim about non-wire channels.

**O-6 — record header names?** Keep the names, from a FIXED allowlist of the names the guard is looking for — never echo an arbitrary observed header name, because an echoed name is untrusted text going into the job log (FINDING 13) and because an unbounded name list is itself request metadata. `Cookie`, `Authorization`, `Proxy-Authorization`, `Set-Cookie` and the signature-parameter names are not sensitive; the value is, and the plan is already right about that. Body parameter names (FINDING 1) get the same treatment: allowlisted names only.

---

# NOT WORTH DOING

```
FINDING 21: decoder breadth and depth-8/512 MiB bounds are theatre relative to
            their cost and their risk
Severity:    NIT
Confidence:  medium
Affected: plan:461-472, :476-488
Reasoning:
  - Depth 8 and 512 MiB: a real trace.zip is single-digit MB. A bound set 100×
    above the measured maximum is not a bound; it is a number that will be raised
    when the lane goes red, and "bound exceeded ⇒ FAIL ⇒ upload nothing" converts a
    product failure into an undiagnosable one. Size the bounds from the measured
    artifact (say 4× the largest observed) and give "bound exceeded" its own exit
    code and message so nobody mistakes it for a leak.
  - Depth 2 covers every observed case (zip in report-data zip; base64→zip in
    index.html). Keep depth 4 as slack; 8 buys nothing and doubles the DoS surface.
  - UTF-16LE/BE, HTML entities and double percent-decoding: not one of these appears
    in any measured channel (M8 says so). They are cheap, so keep them — but do NOT
    add hex, base32, deflate-raw-in-PNG-tEXt, or PDF stream parsing. Those are the
    "fifth prediction" the plan rightly refuses elsewhere.
  - What IS required, and is missing: base64 → ARCHIVE recursion (FINDING 3).
Recommendation: trade the breadth for the one decode that is measured, and for the
  shape detectors of FINDING 16, which cover unmarked channels — the thing markers
  structurally cannot.
```

```
FINDING 22: 22 mutations for ~6 distinct controls inflates the demonstration set
            without adding evidence
Severity:    NIT
Confidence:  high
Affected: plan:339-362 (12 of the 22 rows have the identical mutation, "set
  trace:'retain-on-failure' on the auth projects"), plan:588 (e2e:demos grows to
  ≈175 halves)
Reasoning: twelve identical mutations produce one fact twelve times, at twelve
  browser launches. The distinct controls are: trace off, screenshot/video off,
  outputDir outside the upload set, no html/list/json reporter, name-scanning, and
  archive recursion. Demonstrate each control once, with the row list it covers
  named in the transcript. Keep per-row mutations only where the control differs
  (T8/T9 redaction, T11 absence-of-image-files, T19 names, T20 embedded copies,
  T22 nesting, and the new T23 base64 archive).
Recommendation: ~8 mutations, each unique. Spend the saved runtime on FINDING 7's
  positive control, which is evidence the current set does not contain.
```

```
FINDING 23: do not build a trace redactor, do not claim the scanner proves absence
            of secrets, and do not remove .vizra-e2e at the end of Lane B
Severity:    NIT
Confidence:  high
Reasoning: three things the plan already declines, and I am recording agreement so
  that phase 2 is not re-litigated: Decision 1 (no binary/trace redaction) is
  correct and FINDING 3 strengthens it; the Residuals sentence "the scanner proves
  the absence of known markers, not the absence of secrets" is the right sentence
  and must survive review verbatim; and Decision 5's refusal to treat "delete the
  directory afterwards" as a control (it is a claim about step ordering) is right.
```

---

## Two things I could not check

- **UNVERIFIED:** the builder's M2 (21 trace members), M3 (per-channel survival) and M7 (stdout contents) — I did not run Playwright. The parts I could check independently (M1's option types, M5's premise that a fill value reaches a step title, M6's producer at `playwright/lib/index.js:700-716` and `errorContext.js`) hold, with the one correction in FINDING 10. M8's "no marker survived only in an encoded form" is contradicted in principle by FINDING 3 and should be re-measured with a decode-then-recurse scanner before it is cited again.
- **UNVERIFIED:** whether `yegamble/vizra-user` is public (FINDING 19) and whether the pinned `actions/upload-artifact@ea165f8…` really defaults `include-hidden-files` to false (FINDING 8) — both are one lookup for the builder and both change a sentence in AGENTS.md.

## The one-line summary for the chair

The plan may proceed to phase 2 **after** FINDINGS 1–8 are folded into it: the wire-signal control does not detect a sign-in (1) or an APIRequestContext call (2); `playwright-report/index.html` carries an unredactable base64 copy of the whole report (3); the summary must be an allowlist, not redacted prose (4); the summary is printed before it is scanned (5); one global taint file deadlocks the two lanes (6); the canary proves a different config and cannot distinguish clean from empty (7); and the upload-path derivation is not default-deny (8). None of these changes the architecture — the Lane A/Lane B split, "not produced" as the control, and "path, not option" all survive intact.
