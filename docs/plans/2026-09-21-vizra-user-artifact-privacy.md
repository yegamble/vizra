# Execution plan: vizra-user artifact privacy II — nothing private leaves CI in a test artifact

**REVISION 2 — phase 2, after the `vizra-security` plan review and the chair's tick-97
rulings.** The seat's report and the binding rulings are
`docs/evidence/warroom/2026-09-21-vizra-user-artifact-privacy-PLAN-REVIEW-security.md`.
The architecture survived: Lane A / Lane B split by Playwright **invocation**,
"not produced" as the control, "path, not option", and Lane B recorders `off`
rather than "retained on the runner" (explicitly accepted). Eight things changed,
and the chair split the work into **two pull requests**.

| | PR A | PR B |
|---|---|---|
| Branch | `fix/m0-artifact-privacy-a` | `fix/m0-artifact-privacy` (after A merges) |
| Title | close today's gaps in the lane that exists | the authenticated lane |
| New lane? | **no** | yes |
| The hard rule (no spec may authenticate, fill a credential or touch a signed URL) | **still stands; `AGENTS.md` keeps saying so** | **lifted**, replaced by the structural rule |
| Overlapping files | `check-e2e-lane.mjs`, `e2e.yml`, `redact.ts`, `redact-artifacts.sh` — which is why B waits for A to merge | same |
| Review | independent verifier | independent verifier **+** the `vizra-security` seat's code review |

## Rulings applied — where each finding is handled

| Source | What it requires | PR | Where in this plan |
|---|---|---|---|
| Debt (a) | `worker-guard.ts:70-71` corrected + `mutation-digests.txt` regenerated in the SAME commit | **A** | PR A commit 1 |
| Debt (b) / **O-3** | tokenising lane check: comments AND string literals ignored; `void f()` refused; **shadowed callee refused**; general call-and-discard recorded review-only | **A** | PR A commit 2 |
| Debt (c) | `globalSetup`/`globalTeardown` refused, plus the argv and second-config evasions | **A** | PR A commits 3–4 |
| **FINDING 3(1)** | drop `playwright-report/index.html` from the upload set; correct the VZ-FOUND-008 evidence README ("0 live queries" never searched the base64 archive) | **A** | PR A commit 5; measurement **M8 (corrected)** |
| **FINDING 3(2,3)** | scanner decodes base64 → detects archive magic → recurses; `sweep-artifacts.sh` gains the same or stops being named as the proof | **B** | PR B scanner |
| **FINDING 8** | workflow-FILE-wide default-deny: literal `path:` from a fixed allowlist, `uses:` allowlist incl. `actions/cache`, no reusable workflows, no `$GITHUB_STEP_SUMMARY`, `include-hidden-files` absent/false, `.vizra-e2e` in no `path:` of ANY workflow | **A** | PR A commit 6 (six mutations) |
| **FINDING 9** | `package.json` scripts byte-equal to documented literals; `DEBUG`/`PWDEBUG`/`PLAYWRIGHT_*` env keys refused | **A** | PR A commit 4 |
| **FINDING 10** | `PLAYWRIGHT_NO_COPY_PROMPT=1` at job level, asserted, red/green demonstrated; M6's "ungated" corrected | **A** | PR A commit 7; measurement **M6 (corrected)** |
| **FINDING 13** | one sanitiser for externally-sourced text (CR/LF, leading `::`, length cap) beside the URL redaction | **A** | PR A commit 8 |
| **FINDING 4 (2nd half)** / PR#3 **F13** | `redact.ts` + `redact-artifacts.sh` handle scheme-less and authority-relative URLs, demonstrated against the verbatim F13 string | **A** | PR A commit 9 |
| **FINDING 19** | retention ≤ 3 days; visibility stated exactly | **A** | PR A commits 10–11 |
| **FINDING 1** | `headersArray()` not `headers()`; credential-shaped **body parameter names**; the 250 ms settle dependency made explicit | **B** | Decision 3.2 (revised) |
| **FINDING 2** | patch `APIRequestContext.prototype.fetch`; interim refuse-outright only if the patch proves fragile, and say which and why | **B** | Decision 3.2 (revised) |
| **FINDING 5** / **O-4** | write → scan → print as three ordered steps, scan `if: always()`; **no** exit-code-handling exception | **B** | CI inventory (revised) |
| **FINDING 6** | per-invocation taint; a request-side credential FAILS the test, a response-side `Set-Cookie` TAINTS and suppresses the upload with a named message, without failing an honest Lane-A test | **B** | Decision 4 (revised) |
| **FINDING 7 + 22** | the canary runs the SHIPPED config; **positive control first** (every marker FOUND with recorders on, in a scratch dir in no upload path) before asserting absence; vacuity guards; ~8 unique mutations, not 22 | **B** | canary section |
| **FINDING 11** | egress allowlist via `context.route` + the APIRequestContext patch; the auth config never reads `E2E_BASE_URL` | **B** | Lane B config |
| **FINDING 12** | summary URLs reduced below path level; residual stated (the path IS the secret for reset/verify/invite/share links) | **B** | summary reporter |
| **FINDING 14** | per-file tripwire exemptions carrying acceptance IDs; `npm run ci` green at every commit boundary; sweep extended to `e2e/harness/authenticated.ts` | **B** (the ci-at-every-boundary rule applies to **A** as well) | PR B |
| **FINDING 15** | `.vizra-e2e/secret/` vs `.vizra-e2e/out/` | **B** | Lane B paths |
| **FINDING 16 + 21** | credential-SHAPE detectors with a recorded false-positive corpus; bounds sized from measured artifacts with their own exit code; depth **4**, not 8 | **B** | scanner |
| **FINDING 17 / 18** | non-wire channels and the pixel channel stated as residuals with the named trigger (first spec rendering media moves its project to screenshot/video off) | **B** | Residuals |
| **FINDING 20** | the `AGENTS.md` sentence written **LAST**, every clause mapped to a demonstration ID | **B** | PR B final commit |
| **FINDING 23** | agreement recorded: no trace redactor, the "canary not classifier" sentence survives verbatim, "delete the directory afterwards" is not a control | both | Decisions 1, 5; Residuals |
| **O-1** | Lane A keeps uploading for M0 only, under four mechanical conditions | A (i, ii) + B (iii, iv) | CI inventory |
| **O-2** | Lane-B floor **≥ 1 per project**, pinned by the canary — not 0 | **B** | — |
| **O-5** | the chair lands the trimmed ledger text through the generator once PR B is verified | chair | — |
| **O-6** | header and body-parameter names from a **fixed allowlist** only; never echo an arbitrary observed name | **B** | Decision 3.2 |

---

## Context

| | |
|---|---|
| Repo | `vizra-user` (GitHub `yegamble/vizra-user`) |
| Base | `main` @ `6bf0a0e` (`fix(e2e): harness hardening … (#7)`), tree clean |
| Phase-2 branch | `fix/m0-artifact-privacy` |
| Board row | `docs/plans/WARROOM-BOARD.md` queue **2f** |
| Requirement | VZ-FOUND-008 (privacy case); meta `AGENTS.md` — "Never log credentials, private signed URLs, or raw private metadata" **and** "Preserve traces for failures" |
| Findings this slice closes | PR#3 re-verification **F8**, **F13**; PR#7 re-verification **F6**, **F7**; PR#7 re-confirmation **C4** (`worker-guard.ts:70-71`) |
| Blocks | every M1 slice that signs in, claims the owner account, or uploads — the hard rule in `vizra-user/AGENTS.md` stands until this lands |
| Probe directory (phase-1 measurements) | `…/scratchpad/vzap-probe-ZNSCIV` — mine, deleted at slice end |

### Preflight (measured, at plan time)

| Thing | State |
|---|---|
| node | v22.14.0 |
| npm | 10.33.0 |
| `@playwright/test` | **1.63.0** (`node_modules/@playwright/test/package.json`) |
| browsers on this machine | `chromium-1243`, `chromium_headless_shell-1243`, `ffmpeg-1011` |
| `perl` / `unzip` / `zip` / `jq` / `python3` / `docker` | all present |
| `typescript` | **5.9.3, a direct devDependency** — so an AST/tokeniser for commit (b) needs **no new package** |
| `yaml` | 2.9.1, direct devDependency; already how `check-e2e-lane.mjs` parses the workflow |
| `acorn` | 8.18.0 — transitive only; **not** to be depended on |
| **BLOCKED for this slice** | nothing. The whole slice is localhost-only; there is no vizra-core, no credential and no network dependency. `docker` exists but an **amd64** image build is not attempted locally (arm64 host, little disk) — CI `ubuntu-24.04` is the platform claim, as ADR-009 says. |

---

## What I MEASURED (not assumed) about Playwright 1.63.0

Everything in this section came out of a probe I built and ran during phase 1: a
localhost fixture server plus a deliberately-failing spec that plants a distinct
random marker (`VZMK<CHANNEL><hex>`, minted at runtime by `crypto.randomBytes`)
through fourteen channels, then a byte scanner over every produced file with every
`.zip` unpacked. Commands, exit codes and the raw table are reproduced in **Progress
and evidence** below. Nothing here is from documentation or memory.

### M1 — option names and value sets, read out of the installed types

`node_modules/playwright/types/test.d.ts`:

```
7196  trace: TraceMode | 'retry-with-trace' | { mode: TraceMode, snapshots?: boolean | { dom?, aria?, screen? },
                                                screenshots?: boolean, sources?: boolean, attachments?: boolean }
7161  screenshot: ScreenshotMode | { mode: ScreenshotMode } & Pick<PageScreenshotOptions,'fullPage'|'omitBackground'>
7238  video: VideoMode | 'retry-with-video' | { mode: VideoMode, size?, show? }
7241  ScreenshotMode = 'off' | 'on' | 'only-on-failure' | 'on-first-failure'
7242  TraceMode      = 'off' | 'on' | 'retain-on-failure' | 'on-first-retry' | 'on-all-retries'
                     | 'retain-on-first-failure' | 'retain-on-failure-and-retries'
7243  VideoMode      = same set
 421  TestProject.outputDir?: string      <- outputDir IS a per-PROJECT option
```

So `trace/screenshot/video` accept `"off"`, and `outputDir` can differ per project.
`trace` additionally has the granular sub-keys `attachments`, `snapshots.dom`,
`snapshots.aria`, `snapshots.screen`, `sources` — **noted, and deliberately not
relied on**: a granular reduction is a claim about what Playwright chooses to
record, which is exactly the class of claim this slice is supposed to stop making.

### M2 — trace.zip member shape (1.63.0, one failing test, `sources: false`)

21 members: `test.trace`, `0-/1-trace.trace`, `0-/1-trace.network`, `0-/1-trace.stacks`,
`resources/*` (the actual request/response bodies, one file each),
`attachments/<sha>` (error-context.md verbatim), `screencast/*.jpeg` (six frames).
`sources: false` works — there is **no** `src/` member.

### M3 — where each channel survives, with trace/screenshot/video at today's settings

Scan of `test-results/` + `playwright-report/`, zips unpacked. "rep/data/…zip" is the
**second, complete copy of trace.zip that the HTML reporter embeds** — every trace
row below is therefore two files, not one.

| Channel planted | Members carrying it |
|---|---|
| request `Cookie` header | `1-trace.network`, `1-trace.trace` (×2 copies) |
| response `Set-Cookie` | `1-trace.network` (×2) |
| `Authorization` header | `1-trace.network`, `1-trace.trace` (×2) |
| `x-amz-security-token` response header | `1-trace.network` (×2) |
| signed URL reached by **`page.goto`** | `1-trace.network`, `1-trace.trace`, **`test.trace`** (×2) |
| signed URL as a **sub-resource** (`img src`) | `1-trace.network`, `1-trace.trace`, `resources/<sha>.html` (×2) |
| private **image bytes** | `resources/<sha>.png` (×2) |
| **DOM text** of the page | `1-trace.trace`, `attachments/<sha>`, `resources/<sha>.html`, **`test-results/…/error-context.md`**, `rep/data/<sha>.md` |
| **console** message | `1-trace.trace`, `resources/<sha>.html` (×2) |
| **typed password** (`page.fill`) | `1-trace.trace`, `attachments/<sha>`, **`test.trace`**, `error-context.md`, `rep/data/<sha>.md` |
| request **body** token | `1-trace.trace`, `resources/<sha>.json` (×2) |
| response **body** token | `resources/<sha>.json` (×2) |
| `page.evaluate` **argument** | `1-trace.trace` (×2) |
| assertion's **received value** | `test.trace`, `attachments/<sha>`, `error-context.md`, `rep/data/<sha>.md`, **`playwright-report/results.json`**, **and the lane's stdout** |

### M4 — the exact scheme-less form F13 named, quoted from `test.trace`

```
"title":"Navigate","subtitle":"127.0.0.1:3987/media/p.jpg?X-Amz-Signature=VZMK…&X-Amz-Expires=60",
"params":{"url":"http://127.0.0.1:3987/me…
```

Both forms are present in the same record: the `params.url` is absolute (the current
redactor catches it) and the `subtitle` is authority-relative (it does not). F13
reproduces exactly.

### M5 — the typed value is in the step TITLE, not only in params

```
"title":"Fill \"VZMKFILL3F5F1669C8D2\"","subtitle":"locator('#password')","params":{"locator":…
```

A password reaches the trace as **human-readable prose in a title string**. No
URL-shaped redactor can reach that; a value-shaped redactor would need the value,
which in production is a real credential nobody may hand a CI script.

### M6 — **THE LOAD-BEARING MEASUREMENT: `trace/screenshot/video = "off"` IS NOT ENOUGH**

Re-ran the identical spec with `trace:"off", screenshot:"off", video:"off"`. Files
produced, and marker survival:

```
test-results/.last-run.json
test-results/leak-every-channel-desktop/error-context.md      <- STILL WRITTEN
playwright-report/index.html
playwright-report/results.json
playwright-report/data/46f3…md                                 <- a copy of it

dom      2  error-context.md, rep/data/46f3…md
fill     2  error-context.md, rep/data/46f3…md
failmsg  3  error-context.md, rep/data/46f3…md, playwright-report/results.json
(all 11 other channels: 0)
```

`error-context.md` is written by `node_modules/playwright/lib/index.js:709` in
`didFinishTest()` whenever `this._testInfo.errors.length > 0`. **No Playwright
CONFIG option gates it** — not `trace`, not `screenshot`, not `video`. Its content
(`lib/errorContext.js:buildErrorContext`) is:

* `# Test info` — title path and file:line
* `# Error details` — the error message, so the assertion's **received value**
* `# Page snapshot` — an `ariaSnapshot({mode:"ai"})` of the live page: **every DOM
  text node and every input's current value**, which is how the typed password
  landed there
* `# Test source` — a code frame, i.e. the channel `use.trace.sources:false` exists
  to close, re-opened by a different file

The HTML reporter then copies it into `playwright-report/data/` (`lib/runner/index.js:1349`).

**Consequence for the design:** "turn the three recorders off for authenticated
projects" is necessary and *not* sufficient. The only control that holds is that the
authenticated run's output directory is **never inside an upload path**, and that a
scanner proves it.

#### M6 — CORRECTED by the security seat's FINDING 10, and re-read at source

Two things I got wrong, both now verified in the installed package:

1. **The `# Page snapshot` section IS gated** — by an environment variable, not a
   config option. `node_modules/playwright/lib/index.js:657-658`:

   ```js
   async _takePageSnapshot(context) {
     if (process.env.PLAYWRIGHT_NO_COPY_PROMPT)
       return;
   ```

   So `PLAYWRIGHT_NO_COPY_PROMPT=1` removes the single richest private-data channel
   in the Lane-A upload set — every DOM text node and every input's current value —
   while leaving the error details that make the file useful. My sentence "nothing
   gates its contents" was false. **PR A sets it at job level and asserts it**
   (FINDING 10). It remains true that the *file* has no config gate, which is why
   Lane B's control stays the path.
2. **`# Test source` is not "the spec source around the failure".** It is a code
   frame of **±100 lines read from `errorLocation.file` at run time**
   (`lib/errorContext.js`, `buildCodeFrame`, `linesAbove`/`linesBelow` = 100), so
   for an error raised inside a helper it is the **helper's** source, not the
   spec's. The threat row is "whatever file the error was raised in", which is
   wider than I wrote.

### M7 — the GitHub log is a leaking artifact too

With everything off, the `list` reporter printed into stdout:

* the assertion's **received value** verbatim (`Received: "VZMKFAILMSG…"`), and
* a **source excerpt of the spec** around the failing line, and
* the path `Error Context: test-results/…/error-context.md`.

A separate probe (a `page.fill` that times out) showed the **value is not** printed
for a failing action — Playwright's call log names the locator only
(`- waiting for locator('#does-not-exist')`) — but the **spec source excerpt is**.
So: a credential-shaped literal anywhere in an authenticated spec reaches the GitHub
log, which no post-hoc redactor can reach because the log is streamed as it is
written. This is the reason markers must be minted at runtime and the reason the
authenticated lane must not use the `list` reporter.

### M8 — RETRACTED AND RE-MEASURED. Markers DO survive only in an encoded form.

**My phase-1 sentence was wrong**, and the security seat's FINDING 3 was right to
refuse it. The original claim — "no marker survived only in an encoded form" — came
from a scan that never decoded `playwright-report/index.html`. Re-measured:

`node_modules/playwright/lib/runner/index.js:3704-3712` (`_writeReportData`) appends
to `index.html`:

```js
fs.appendFileSync(filePath, '<template id="playwrightReportBase64">data:application/zip;base64,');
… this._dataZipFile.outputStream.pipe(new Base64Encoder()).pipe(fs.createWriteStream(filePath,{flags:"a"}))
fs.appendFileSync(filePath, "</template>");
```

Measured on a failing run of the same probe:

```
decoded bytes: 2612   magic: 504b0304      (a ZIP)
members: 903210ec32f953d9c779.json, report.json

markers surviving ONLY inside that embedded zip:
  gotoquery   (the F13 scheme-less signed URL)   -> 903210ec32f953d9c779.json
  fill        (the typed password)               -> 903210ec32f953d9c779.json
  failmsg     (the assertion's received value)   -> 903210ec32f953d9c779.json

raw grep of index.html for those markers:  NOTHING FOUND
```

And after running the **shipped** `scripts/ci/redact-artifacts.sh` over the tree
(`OK: redacted URL query strings in 23 file(s) and 2 archive(s)`):

```
STILL LIVE AFTER REDACTION: gotoquery, fill, failmsg
```

The redactor rewrites `index.html` as text, so it changes the plaintext and cannot
touch the base64 payload; it unpacks `*.zip` **files** only. `sweep-artifacts.sh`
greps raw bytes of a copy with `.zip` files unpacked and cannot decode base64
either. **Every "verified end to end" redaction claim in `AGENTS.md`, including
"239 `?<redacted>`, zero live queries" and D9's "3 members → 0", was measured with a
search blind to this file.** Nothing private exists today, so this is not a live
incident; it is a fifth URL shape after four rounds, and it is exactly the shape a
scanner must be designed for before code rather than after the first miss.

**PR A's control is the seat's preferred one: drop `playwright-report/index.html`
from the upload set.** Re-encoding would be a fifth prediction, which is the thing
Decision 1 exists to refuse. Traces stay diagnosable — `playwright-report/data/*.zip`
still opens in `npx playwright show-trace`. PR B's scanner additionally treats
"decoded bytes whose magic is an archive" as an archive and recurses.

Trace `postData` is stored as a separate `resources/*.json` file with `"text":""` in
the HAR-shaped member, not base64-inlined — that part of the original measurement
stands.

### M9 — facts the rulings required me to verify at source, not assume

| Fact | How confirmed | Value |
|---|---|---|
| `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02`'s `include-hidden-files` default | `gh api "repos/actions/upload-artifact/contents/action.yml?ref=ea165f8d…"`, decoded and read | **`default: 'false'`** — so `test-results/.last-run.json` is genuinely not published today, and the lane guard may assert absent-or-false |
| repository visibility | `gh repo view yegamble/<r> --json visibility` for all four | `vizra`, `vizra-core`, `vizra-user`, `vizra-search` — **all `PRIVATE`** |

So the FINDING 19 sentence is: artifacts and job logs are readable by **repository
collaborators**, not by the world. That is the exact claim; "world-readable" would
have been wrong and "internal only" would have been vague.

---

## Acceptance

### In scope

| ID | Observable outcome |
|---|---|
| **AP-1** | Running the authenticated lane against the privacy fixture, with a marker planted in **every** channel of the threat table, produces an upload set in which the scanner finds **zero** markers — proved by the scanner walking every byte of exactly the paths the workflow's upload steps name, archives recursed and encodings decoded. |
| **AP-2** | Each threat-table row is **individually demonstrated red**: with that row's protection removed (and only that one), the canary fails and names that channel; with it restored, green. Digest of the mutated file recorded before and after; the harness refuses to record a demonstration whose mutation did not actually change the file. |
| **AP-3** | The lane **fails closed**: scanner crash, missing/empty marker file, zero files scanned, an archive it cannot open, a decode budget exceeded, or an upload path that does not exist ⇒ non-zero exit and **nothing is uploaded**. Demonstrated, one case each. |
| **AP-4** | "Authenticated" is **structural**: credentials are obtainable only from one harness fixture available only in the authenticated projects, and a spec that authenticates outside that structure **fails at runtime** (not by lint, not by a tag). Demonstrated with a spec in `e2e/specs/**` that acquires a session by each route the tripwire already records as an evasion. |
| **AP-5** | `check-e2e-lane.mjs` governs the new shape: every upload step allowlisted by **path**, gated on the scanner step's `outcome == 'success'`, the authenticated output directory provably not inside any upload path, and the authenticated projects provably `trace/screenshot/video: "off"`. Each assertion red-demonstrated in `require-checks_test.sh`. |
| **AP-6** | **F13 closed**: the scheme-less `host[:port]/path?query` form is redacted, and D9 gains a `page.goto` half so the demonstration covers the path it claims to. |
| **AP-7** | **Debt (a)** — `e2e/harness/worker-guard.ts:70-71` corrected and `docs/evidence/VZ-FOUND-008/mutation-digests.txt` regenerated **in the same commit**. |
| **AP-8** | **Debt (b)** — the lane guard's harness checks match on **tokenised/parsed** source: a trailing comment, a string literal and call-and-discard each stay RED. Red-demonstrated for at least `formatOrphans` and `guardBrowser`. |
| **AP-9** | **Debt (c)** — a `globalSetup` / `globalTeardown` key in any Playwright config is refused by the lane guard, red-demonstrated. |
| **AP-10** | The hard rule in `vizra-user/AGENTS.md` is replaced by the structural rule (exact sentence below), and the F8 "NOT covered" table is rewritten to match what the new design actually does. |

### Explicitly NOT in scope

* **No sign-in UI, no owner-claim UI, no upload UI, no product code at all.** This
  slice makes the harness safe for those slices; it does not write them.
* **No real credential, no real signed URL, no vizra-core, no network beyond
  localhost**, in any spec, canary or fixture.
* **No redactor for binary trace contents.** Rejected on the merits — see
  "Decision 1".
* **No promotion of `supply-chain` to required**, no manifest/floor change, no
  CODEOWNERS ruleset (owner action), no contract re-vendor.
* **No change to the four guarded signal kinds, the stamp, the brand, the creation
  guard, the coverage floor or the 250 ms late edge** beyond the two listeners
  AP-4 needs.
* The ledger privacy case named in board row 2f is a **meta-repo** edit (`docs/quality/features.json`), not mine. I will hand the chair the exact case text; a meta builder lands it.

---

## Decisions, and where I disagree with the chair

### Decision 1 — I agree: **do not try to redact traces. Do not produce them.**

The chair asked me to show a mechanism and a proof if I thought redacted traces were
achievable. I do not, and M3/M5/M6 are why:

* the channels are not URLs. A typed password is **prose inside a step title**
  (M5); a response body is an opaque `resources/<sha>.json`; DOM text is an aria
  snapshot. Redacting them means knowing the secret's value, which in production is
  a real credential nobody may pass to a CI shell script.
* the trace exists **twice** — once in `test-results/` and once embedded in
  `playwright-report/data/<sha>.zip` (M3). Any redactor must find both, forever.
* `error-context.md` is produced with **no option to disable it** (M6) and carries
  the page snapshot *and* the spec source, so even a perfect trace redactor leaves a
  file behind.
* the current redactor's own history is the argument: it was `scheme://`-only, then
  relative-only, then missed the HAR `queryString` array, then missed the
  scheme-less subtitle (F13). Four rounds, one shape each. A fifth round is a
  prediction, not a control.

So: **default-deny on artifact content.** For authenticated specs nothing is
recorded and nothing but a generated text summary is uploaded.

### Decision 2 — the split is by **Playwright invocation**, not only by project

The chair's sketch was per-project `use` options. I propose going one step further,
because of M6: reporters are **global to a run**, so the HTML reporter aggregates
authenticated and unauthenticated tests into one `playwright-report/`, and
`error-context.md` from an authenticated test lands in `playwright-report/data/`
regardless of any per-project setting. A per-project split cannot fix that; a
per-invocation split removes the problem instead of guarding it.

| | Lane A — unauthenticated | Lane B — authenticated |
|---|---|---|
| config | `playwright.config.ts` (today's) | `playwright.auth.config.ts` (new) |
| `testDir` | `./e2e/specs` | `./e2e/authenticated` |
| projects | `desktop-chromium-1440`, `mobile-chromium-390` | `auth-desktop-chromium-1440`, `auth-mobile-chromium-390` |
| `use.trace / screenshot / video` | as today (`retain-on-failure`, `only-on-failure`, `retain-on-failure`) | **`"off"` / `"off"` / `"off"`** |
| `outputDir` | `test-results` | **`.vizra-e2e/auth-output`** — never in an upload path |
| reporters | `list`, `html`, `json`, coverage floor, stamp | **`e2e/harness/private-summary-reporter.ts` only** (+ the floor and stamp reporters) — no `list`, no `html`, no `json` |
| what CI may upload | `playwright-report/`, `test-results/`, `playwright-browsers.txt` — redacted, then scanned | **only** `e2e-failure-summary/summary.txt` — generated, redacted, then scanned |
| stdout | as today | only what the private reporter prints (title, project, file, status, redacted message) |

Both lanes keep the branded worker guard, the stamp, the creation guard and the
coverage floor unchanged; the harness `test` object is the same one.

### Decision 3 — "authenticated" is enforced at **runtime by the guard**, three ways

Constraint 3 says the rule must be structural, not a tag. Three layers, and it
matters which is the control:

1. **The only source of credentials is a fixture.** `e2e/harness/authenticated.ts`
   exports a `vizraCredentials` fixture. It throws unless *both* hold:
   `testInfo.project.name ∈ AUTH_PROJECTS` **and** `testInfo.file` is under
   `e2e/authenticated/`. It is branded into the same module-private `WeakSet`
   discipline `createWorkerHarness` already uses, so a spec cannot substitute a
   look-alike and keep its stamp.
2. **THE CONTROL — the worker guard observes authentication and refuses it outside
   Lane B.** The worker-scoped listener already sits at `BrowserContext` level. It
   gains a `request` listener and reads response headers it already receives, and
   records **the fact and the header/param NAME only — never a value**:
   * a request carrying `authorization`, `cookie` or `proxy-authorization`;
   * a response carrying `set-cookie`;
   * a request URL whose query carries a signature-shaped parameter name
     (`x-amz-*`, `signature`, `sig`, `token`, `expires`, `policy`, `se`, `sp`, `sv`);
   * `context.addCookies` / `context.storageState` / `browser.newContext({storageState})`
     (the creation guard already patches those entry points).

   If any of those is observed in a test running in a **Lane-A** project, the test
   **fails** ("authenticated outside the authenticated projects"), and the run is
   marked tainted. This is the structural rule: not "did you label yourself", but
   "did a credential cross the wire".
3. **Early warning, not the control:** `no-credentials-in-specs.test.ts` keeps its
   pattern sweep and gains `e2e/authenticated/**` as an *allowed* directory; the
   ESLint rule gains the `vizraCredentials` fixture name to its harness-owned list.

The existing tripwire's four measured evasions (`pressSequentially`,
`document.cookie` via `evaluate`, `process.env`, a helper inside `e2e/harness/`) are
all caught by layer 2, because all four end with a credential on the wire. That is
the point of moving the control to the runtime.

### Decision 4 — the taint flag, and where I want the chair's ruling

Lane A still uploads redacted traces, because for unauthenticated specs "preserve
traces for failures" is honoured the normal way. But Lane A's uploads must not
publish anything if Lane A *itself* turned out to be authenticated (layer 2 above
fails the test, but the artifacts have already been written). So:

* the worker guard writes `.vizra-e2e/taint.json` whenever any auth signal is
  observed in any lane;
* the scanner **fails closed** if that file says tainted, or is missing, or is
  unparseable, or the run produced no taint file at all;
* therefore the Lane-A upload is gated on `steps.scan.outcome == 'success'` and
  nothing else needs a second condition.

**Open question O-1 (below)** asks whether the chair wants Lane A's traces uploaded
at all. My recommendation is yes, on the grounds that removing them removes the only
CI debuggability the repository has for the 18 specs that cannot authenticate by
construction — but I will implement "never upload traces at all" if the chair prefers
the stricter reading of default-deny, and the design does not otherwise change.

### Decision 5 — where I disagree with constraint 1's phrasing

The chair offered "retained on the runner only and never uploaded" as an alternative
to "off". I recommend **`"off"`, not "retained-but-not-uploaded"**, for Lane B. A
recorded-but-unuploaded trace is a file on a shared runner, inside the job's
workspace, reachable by every later step in the job including any third-party action
— and the residual would then be "no `run:` step exfiltrates it", which `AGENTS.md`
already says no parser can close. Not producing it is strictly stronger and costs
nothing that the local-debugging story does not give back (below).

---

## The threat table — control and proof, row by row

Legend for **Control**: **NP** = not produced · **NU** = produced but never inside an
upload path · **R** = redacted · **S** = scanned (the backstop that fails the lane).
Every row is **S** in addition to its primary control; S alone is never the control.

| # | Channel | Where it lands (measured) | Control (Lane B) | Control (Lane A) | Canary channel | Mutation that must turn it red |
|---|---|---|---|---|---|---|
| T1 | `Authorization` request header | `1-trace.network`, `1-trace.trace` ×2 | **NP** (trace off) + S | unreachable (guard fails the test) + R/S | request sent with `authorization: Bearer <marker>` | set `trace:"retain-on-failure"` on the auth projects |
| T2 | `Cookie` request header | same | **NP** + S | as T1 | `context.addCookies` then navigate | as T1 |
| T3 | `Set-Cookie` response header | `1-trace.network` ×2 | **NP** + S | as T1 | fixture sets `Set-Cookie: vz_session=<marker>` | as T1 |
| T4 | `x-amz-security-token` / any `x-amz-*` signature header | `1-trace.network` ×2 | **NP** + S | as T1 | fixture returns the header on an image | as T1 |
| T5 | request **body** (password in a login POST) | `1-trace.trace`, `resources/*.json` ×2 | **NP** + S | as T1 | `fetch('/api/login',{body:{password:<marker>}})` from the page | as T1 |
| T6 | response **body** (token in JSON) | `resources/*.json` ×2 | **NP** + S | as T1 | fixture returns `{"token":"<marker>"}` | as T1 |
| T7 | private **image bytes** | `resources/*.png` ×2 | **NP** + S | R is impossible (binary) → **NU** | fixture serves PNG bytes containing `<marker>` | as T1 |
| T8 | signed URL via **`page.goto`** — the scheme-less `host:port/path?query` subtitle | `test.trace`, `1-trace.trace`, `1-trace.network` ×2 | **NP** + S | **R** (new authority-relative program) + S | `page.goto(fixtureSignedUrl)` | (Lane A) delete the authority-relative perl program → F13 reproduces |
| T9 | signed URL as a **sub-resource** | `1-trace.network`, `resources/*.html` ×2 | **NP** + S | **R** + S | `<img src=signedUrl>` (today's D9 shape) | delete the relative program |
| T10 | **DOM text** (private caption, email, GPS/EXIF string) | `1-trace.trace`, `attachments/*`, `resources/*.html`, **`error-context.md`**, `rep/data/*.md` | **NP** for the trace; **NU** for `error-context.md` (Lane-B `outputDir` is outside every upload path) + S | R cannot reach it → **NU** for Lane B only; Lane A has no private DOM by construction | fixture page renders `<p>` with `<marker>` | point Lane B's `outputDir` at `test-results` |
| T11 | **screenshots / video** of an authenticated page (pixels, not text) | `test-failed-1.png`, `video.webm`, `screencast/*.jpeg` | **NP** (`screenshot:"off"`, `video:"off"`) + S-by-absence | as today | canary asserts **no `.png`/`.webm`/`.jpeg` file exists** anywhere in Lane B's output | set `screenshot:"only-on-failure"` on the auth projects |
| T12 | **Playwright call parameter** — `fill()` value in the step **title** (M5) | `test.trace`, `1-trace.trace`, `attachments/*`, `error-context.md` | **NP** + **NU** + S | guard fails the test | `page.fill('#password', <marker>)` | as T1 |
| T13 | `page.evaluate` **argument** | `1-trace.trace` ×2 | **NP** + S | as T1 | `page.evaluate(t=>…, <marker>)` | as T1 |
| T14 | **console** message carrying a token | `1-trace.trace`, `resources/*.html` ×2 | **NP** + S | R cannot reach a non-URL token → **NU** | page `console.log("… <marker>")` | as T1 |
| T15 | **page error / stack** carrying a token | `*-trace.trace` | **NP** + S | **R** (harness `redact.ts`) + S | page throws `new Error("<marker>")` | as T1 |
| T16 | **`storageState`** file | wherever the spec wrote it | **NP** — the fixture never writes one; `storageState` on a Lane-A context is an auth signal (Decision 3.2) | guard fails the test | canary spec calls `context.storageState({path:…})` inside Lane B's outputDir | remove the `storageState` observation from the guard |
| T17 | the **assertion's received value** (M3, M7) | `error-context.md`, `results.json`, `test.trace`, **stdout** | **NU** + the private reporter prints only a **redacted** message; a marker in a message is caught by S over the summary and over the captured stdout | as today | canary asserts on a value derived from `<marker>` | drop the redactor from the private reporter |
| T18 | the **spec's own source** (`# Test source` in `error-context.md`, and the `list` reporter's excerpt — M6, M7) | `error-context.md`, `rep/data/*.md`, **stdout** | **NU** + Lane B does not use `list` + the markers rule (no credential-shaped literal ever in the repo) | as today (`use.trace.sources:false`) | canary asserts the summary contains no source excerpt | use `list` as Lane B's reporter |
| T19 | **artifact file and directory names** (derive from test titles) | everywhere | titles in `e2e/authenticated/**` must not embed data; the scanner checks **names as well as contents** | same | a canary test whose *title* contains `<marker>` | make the scanner read contents only |
| T20 | **the HTML report's embedded copies** — `playwright-report/data/<sha>.zip` and `<sha>.md` (M3) | `playwright-report/data/` | **NP** — Lane B has no `html` reporter | R (both copies) + S | the scanner counts the embedded zip as its own file and recurses | make the scanner skip `playwright-report/data/` |
| T21 | **stdout/stderr in the GitHub log** (M7) | the run log, unredactable after the fact | Lane B's stdout is the private reporter's only; the step captures it to a file, scans it, and prints only the redacted summary — then re-raises the captured exit code | as today | markers appear in stdout | print the raw captured log |
| T22 | **anything nested in a zip inside the artifact** | `playwright-report/data/*.zip` today; future nesting | scanner recurses ≥ 8 levels into zip/tar/gz | same | canary plants a marker in a zip inside a zip inside the upload set | cap the scanner's recursion at 1 |

**Rows the chair's list did not name, which the measurement added:**
`error-context.md` as an *independent, un-disableable* channel carrying the page
snapshot **and the spec source** (T10/T17/T18); the **duplicate** trace inside the
HTML report (T20); and the fact that a Lane's **stdout** carries the spec source
excerpt even when it does not carry the value (T21/T18).

---

## CI artifact inventory — before and after

### Before (`main` @ `6bf0a0e`)

| Step | `if:` | Path | Retention |
|---|---|---|---|
| `Redact URL query strings in the artifacts` (`id: redact`) | `failure()` | rewrites `test-results/`, `playwright-report/` in place | — |
| `Upload Playwright artifacts` | `failure() && steps.redact.outcome == 'success'` | `playwright-report/`, `test-results/`, `playwright-browsers.txt` | 14 d |
| `Container logs` | `always()` | printed to the **GitHub log** (`docker logs … \| tail -200`) | — |
| lane stdout | — | printed to the **GitHub log** | — |

Two artifacts today, only one of them named as one: the uploaded tree, and the job
log.

### After

| # | Step | `if:` | Exactly what is uploaded | Retention |
|---|---|---|---|---|
| 1 | `Lane A — browser lane` | unconditional | nothing | — |
| 2 | `Lane B — authenticated lane` | unconditional | nothing; stdout captured to `.vizra-e2e/auth-lane.log`, **not printed** | — |
| 3 | `Summarise the authenticated lane` | `always()` | writes `e2e-failure-summary/summary.txt` — per failed test: project, spec path, title, status, error message through `redact.ts` + the marker/secret scrubber, URLs with **query and fragment dropped entirely** (not `?<redacted>`, dropped). Nothing else. Then prints that file and `exit`s the captured code. | — |
| 4 | `Redact URL query strings` (`id: redact`) | `failure()` | rewrites Lane A's `test-results/`, `playwright-report/` in place, **plus** the new authority-relative program (F13) | — |
| 5 | `Scan every byte that would be uploaded` (`id: scan`) | `failure()` | reads the upload steps' `path:` lists **out of the workflow file itself**, walks every byte, recurses archives, decodes; **fails closed** | — |
| 6 | `Upload failure summary` | `failure() && steps.scan.outcome == 'success'` | `e2e-failure-summary/` **only** | 14 d |
| 7 | `Upload Playwright artifacts (unauthenticated lane)` | `failure() && steps.scan.outcome == 'success'` | `playwright-report/`, `test-results/`, `playwright-browsers.txt` | 14 d |
| 8 | `Container logs` | `always()` | printed to the GitHub log, **through the redactor** | — |
| 9 | `Stop the container` | `always()` | — | — |

`.vizra-e2e/auth-output/` and `.vizra-e2e/auth-lane.log` appear in **no** upload
path. `check-e2e-lane.mjs` asserts that, by path prefix, against the parsed workflow
(AP-5).

**What prints in the GitHub log, stated as constraint 4 asks:** Lane A's `list`
reporter output (unchanged — and it can carry a spec source excerpt, which is why
Lane A specs may not authenticate); the redacted summary from step 3; the scanner's
own counts (files, archives, bytes, markers — **never a matching line**, the existing
`sweep-artifacts.sh` discipline); the redactor's count line; `docker logs` through
the redactor. Lane B's raw stdout prints nowhere.

---

## The canary — the acceptance control

`scripts/ci/artifact-privacy-canary.mjs`, run as a required step in the `e2e`
workflow next to `harness-canary.mjs`.

1. **Fixture server** — `scripts/e2e/privacy-fixture-server.mjs`, Node `http` on
   `127.0.0.1` on an ephemeral port. Serves: a page with a DOM marker, a console
   marker, a password input, an `<img>` at a signed-URL-shaped path; a `/media/*.png`
   that returns marker-carrying bytes and an `x-amz-security-token` header; a
   `/api/login` that echoes a token in JSON and sets `Set-Cookie`. Localhost only,
   no TLS, no outside network.
2. **Markers** — 20+ values minted per invocation by `crypto.randomBytes(9)`, one per
   threat row, shaped `VZMK<ROW>_<hex>`. They are passed to the fixture and the spec
   through the environment and written to `.vizra-e2e/privacy-markers.json`, which is
   git-ignored. **No marker, and no credential-shaped literal, ever exists in a
   committed file** — GitGuardian scans every commit of the PR, and M7 shows a spec's
   source reaches the job log anyway.
3. **The canary spec** — `e2e/canary/all-channels.canary.ts`, run under the Lane-B
   config, deliberately failing, exercising every row of the threat table.
4. **The scanner** runs over the complete would-be-upload set.
5. **Assertions** — zero markers anywhere; **and** the summary still names the spec
   file, the test title and the project (a redaction that destroys diagnosis is a
   failure, the same inverse control `sweep-artifacts.sh` already carries); **and**
   no `.png`/`.webm`/`.jpeg` exists in Lane B's output (T11).
6. **Mutation mode** — `--mutate=<row>` applies exactly one mutation from the table's
   last column, re-runs, and requires the canary to go **red naming that row**. The
   harness computes the file digest before and after and **refuses to record a
   demonstration whose mutation did not change the file** — the discipline
   `scripts/e2e/demonstrate.sh` already has; digests append to
   `docs/evidence/VZ-FOUND-008/mutation-digests.txt`.

Runtime budget: ~2 browser launches for the green run, one per mutation for the red
set. The red set runs in `npm run e2e:demos` (not in the required lane); the green
canary runs in the required lane. Measured comparison point: the existing four-fixture
harness canary is `real 5.77 s`.

---

## The scanner — rules and failure modes

`scripts/ci/scan-artifacts.mjs`.

**Inputs.** (i) the workflow path; it parses it with the same `yaml` package and takes
the `path:` list of every step matching `check-e2e-lane.mjs`'s `UPLOADER` regex — so
the scanner and the upload allowlist cannot drift; (ii) the marker file.

**Walk.** Every file under every upload path, plus the file **names** themselves (T19).

**Archive recursion.** `.zip` via `unzip`; `.tar`, `.tar.gz`, `.tgz`, `.gz` via
`node:zlib` + a tar reader. Depth ≤ **8**. Bounds, because an archive is untrusted
input: ≤ 50 000 members, ≤ 512 MiB inflated in total, ≤ 200 MiB per member. Exceeding
any bound is **FAIL**, not a skip.

**Decoding, per file's raw bytes.** raw; UTF-16LE and UTF-16BE; percent-decoding
(twice); JSON `\uXXXX` / `\xNN` unescaping; HTML entity decoding; base64 — every
base64-ish run ≥ 16 chars decoded at all four alignments; `gzip`/`deflate` streams
found by magic bytes, inflated once, then re-scanned at depth + 1. M8 says none of
these was needed in my probe; they are here because a decoder added after the first
miss is not a control.

**Reporting.** Counts, and the **names** of offending members — never a matching
line, never the marker value.

**Failure modes — every one FAILS CLOSED and the run uploads nothing:**

| Condition | Result |
|---|---|
| scanner throws for any reason | exit 1 |
| marker file missing, empty, or not JSON | exit 1 — "nothing to search for is not a pass" |
| a marker is the empty string or shorter than 8 chars | exit 1 (a short marker would match everywhere or nowhere) |
| zero files scanned, or zero bytes scanned | exit 1 (this is `sweep-artifacts.sh`'s existing exit 2 rule, promoted) |
| an upload path named in the workflow does not exist | exit 1 |
| an archive cannot be opened | exit 1 (today's redactor *deletes* such a file with a warning; for the scanner that is the wrong default) |
| a bound is exceeded | exit 1 |
| `.vizra-e2e/taint.json` says tainted, or is missing/unparseable | exit 1 |
| any marker found, in any form, in any name or byte | exit 1, offending member **names** printed |

**Its own tests.** `scripts/ci/scan-artifacts_test.mjs` — marker plain; in a zip; in a
zip in a zip; in a tar.gz; base64 at each alignment; percent-encoded; JSON-escaped;
UTF-16; in a **file name**; in a gzip stream; plus one case per failure mode above.
Expected: **≈ 22 cases, 0 skips.**

**Residuals of the scanner, stated at the strength they hold** (see § Residuals).

---

## What developers lose in CI, and how they get it back

**Lost, for authenticated specs only:** trace viewer, screenshots, video, DOM
snapshots, network panel, and the error-context page snapshot — none of it reaches
the run page. What a red Lane B gives you is: project, spec file, test title, status,
and the error message with URLs stripped to origin + path.

**Recovered locally, and this is how "preserve traces for failures" is honoured for
authenticated specs:** `npm run e2e:auth:local` runs exactly Lane B's config with
`VIZRA_E2E_LOCAL_TRACE=1`, which turns `trace`, `screenshot` and `video` back on and
writes them to `.vizra-e2e/auth-output/` on the developer's own machine. The
environment variable is refused when `process.env.CI` is set — asserted by a unit
test and by `check-e2e-lane.mjs` (the workflow may never set it, the same rule
`E2E_COVERAGE_FLOOR=off` already has). The meta contract's "preserve traces for
failures" is satisfied where the trace can be preserved safely: on the machine of the
person who is allowed to see the credential.

Documented in `vizra-user/AGENTS.md` and in `README.md`'s command table.

---

## Implementation — PR A: close today's gaps in the lane that exists

Branch `fix/m0-artifact-privacy-a` off `origin/main` (`6bf0a0e`). **No new lane.**
The hard rule stands and `AGENTS.md` keeps saying so. `npm run ci` is run and
recorded at **every** commit boundary (measured baseline: exit 0, 15 files / 355
tests / 0 skipped, 8.3 s — cheap enough that there is no excuse to batch it).

| # | Commit | Files | Red demonstration |
|---|---|---|---|
| **1** | `fix(e2e): correct the retracted claim in worker-guard.ts and regenerate the digest ledger` — debt (a) | `e2e/harness/worker-guard.ts` (lines 70-71: the grep is an **early warning**, defeatable by a trailing comment, a string literal and call-and-discard; add the `AGENTS.md § Residuals` pointer `creation-guard.ts` has and this file lacks), `docs/evidence/VZ-FOUND-008/mutation-digests.txt` **regenerated in the same commit** | the ledger's `worker-guard.ts` digests move from `4fc5c024…` to the new hash in one commit, so the byte-pinned file and its ledger are never out of step |
| **2** | `fix(ci): the lane guard matches tokenised source, not raw text` — debt (b), O-3 | `scripts/ci/check-e2e-lane.mjs`: replace `withoutComments` (:546-550) with a **TypeScript AST** matcher on the existing `typescript@5.9.3` devDependency. A check is satisfied only by a `CallExpression` whose callee is the required identifier, **not** under a `VoidExpression`, and **not** resolving to a local binding that shadows the harness symbol | `require-checks_test.sh`, for `formatOrphans` **and** `guardBrowser`: call removed (RED, existing); + trailing comment (**RED**); + string literal (**RED**); `void f()` (**RED**); **shadowed callee** (**RED**). 5 × 2 = **10 cases**, plus the green control |
| **3** | `fix(ci): refuse globalSetup/globalTeardown in every Playwright config` — debt (c) | `scripts/ci/check-e2e-lane.mjs` (AST over each config the workflow names, so a commented key does not trip it and a computed one fails closed); `AGENTS.md § Residuals` bullet moves from "queued" to "refused" | each key present ⇒ RED by name; a **second config file** reached via `--config` ⇒ RED; clean tree ⇒ green |
| **4** | `fix(ci): the lane guard reads package.json and the job env` — FINDING 9 | `check-e2e-lane.mjs` asserts `scripts.e2e` / `e2e:install` / `e2e:demos` are **byte-equal** to documented literals, and refuses `DEBUG`, `PWDEBUG`, `PLAYWRIGHT_HTML_REPORT` and any other `PLAYWRIGHT_*` key in the e2e job outside an allowlist (`PLAYWRIGHT_NO_COPY_PROMPT` is the allowlisted one, commit 7) | appending `--trace on` to `scripts.e2e` ⇒ RED; appending `--output test-results` ⇒ RED; `DEBUG: pw:api` in a step env ⇒ RED |
| **5** | `fix(ci): drop the HTML report index from the upload set` — FINDING 3(1) | `.github/workflows/e2e.yml` upload `path:` becomes an explicit list that excludes `playwright-report/index.html`; `scripts/e2e/sweep-artifacts.sh` gains a decode-then-recurse stage **or** loses its `AGENTS.md` billing as "the proof" (decided in the commit, stated either way); `docs/evidence/VZ-FOUND-008/README.md` records that the earlier "0 live queries" measurement never searched the base64-embedded archive | M8's transcript is the red half: three markers live inside `index.html` after the shipped redactor, invisible to a raw grep. Green half: the file is not in the upload set and the scan finds nothing |
| **6** | `fix(ci): upload scope is default-deny across the whole workflow file` — FINDING 8 | `check-e2e-lane.mjs` widens from `jobs.e2e` to **every job of the file**, and asserts (a) every uploader `path:` entry is a literal from a fixed allowlist — no `* ? [ ] !`, no `${{`, no `.`/`..`; (b) every `uses:` is in a pinned allowlist, which also catches `actions/cache`; (c) no `jobs.*.uses`; (d) no `$GITHUB_STEP_SUMMARY` write in the e2e job; (e) `include-hidden-files` absent or `false` (**default `'false'` confirmed at the pinned SHA — M9**); (f) `.vizra-e2e` in no `path:` of **any** workflow | **six** `require-checks_test.sh` mutations: a glob in `path:`; a `${{ }}` in `path:`; `include-hidden-files: true`; an `actions/cache` step whose path is `.vizra-e2e`; a `$GITHUB_STEP_SUMMARY` write in the e2e job; a second job in `e2e.yml` with an uploader |
| **7** | `fix(e2e): suppress the error-context page snapshot in CI` — FINDING 10 | `.github/workflows/e2e.yml` sets `PLAYWRIGHT_NO_COPY_PROMPT: "1"` at **job** level (never locally); `check-e2e-lane.mjs` asserts it, in the `E2E_COVERAGE_FLOOR` idiom | one demo pair: without the variable `error-context.md` has a `# Page snapshot` naming the sentinel; with it, the section is absent and the error details remain. Removing it from the workflow ⇒ RED |
| **8** | `fix(e2e): sanitise externally-sourced text before it reaches the log` — FINDING 13 | `e2e/harness/redact.ts` gains one sanitiser beside the URL redaction — strip CR/LF, refuse a leading `::`, escape `%0A`/`%0D`/`%25`, cap length — applied to every externally-sourced string the harness prints or attaches (`describeConsole`, page-error text) | `redact.test.ts` unit cases + one demo pair: a page whose console message begins with `::error::` produces a harness message in which that text is inert |
| **9** | `fix(e2e): redact scheme-less and authority-relative URLs` — PR#3 FINDING 13 / seat FINDING 4 | `scripts/ci/redact-artifacts.sh` third perl program for `host[:port]/path?query`, guarded so prose and `1:23/foo` timestamps are untouched; the same shape in `e2e/harness/redact.ts` | demonstrated against the **verbatim F13 string** `"subtitle":"host:3219/m.jpg?X-Amz-Sig=SENTINELVALUE&e=60"` → `?<redacted>`; plus the D9 `page.goto` half (sentinel 3 members → 0, host and path readable) |
| **10** | `fix(ci): shorten artifact retention` — FINDING 19 | `.github/workflows/e2e.yml` `retention-days: 3`; `check-e2e-lane.mjs` asserts the ceiling | `retention-days: 14` ⇒ RED; absent ⇒ RED |
| **11** | `docs: state what the artifact controls do and do not cover` | `vizra-user/AGENTS.md` (§ Artifact privacy, § Residuals, the command table, the retention/visibility sentence), `docs/evidence/VZ-FOUND-008/README.md` | — |

**The visibility sentence, exactly** (FINDING 19; all four repositories confirmed
`PRIVATE` — M9):

> Uploaded artifacts and the job log are readable by anyone with access to this
> **private** repository — every collaborator, and anyone an owner later adds — not
> by the public. They are retained for **3 days**. "Not public" is not "not
> published": a trace is a durable copy of whatever the lane saw, held by GitHub,
> outside this repository's own access controls.

**What PR A explicitly does NOT do:** no Lane B, no `e2e/authenticated/**`, no
`vizraCredentials`, no scanner, no canary, no taint, no change to the hard rule.
Every one of those is PR B.

## Implementation — PR B: the authenticated lane

Opened only after PR A is **verified and merged**, because the two overlap in
`check-e2e-lane.mjs`, `.github/workflows/e2e.yml`, `redact.ts` and
`redact-artifacts.sh`. Contents, per the ruling: Lane B config and the structural
rule with FINDING 1's `headersArray()` + body-parameter-name detection and the
explicit 250 ms settle dependency; FINDING 2's `APIRequestContext.prototype.fetch`
patch (or the interim refuse-outright, with a written reason if the patch proves
fragile); FINDING 6's per-invocation taint, where a request-side credential **fails**
the test and a response-side `Set-Cookie` **taints and suppresses the upload** with a
named message without failing an honest Lane-A test; FINDING 11's egress allowlist
and an auth config that never reads `E2E_BASE_URL`; FINDING 4's allowlisted
structured summary; FINDING 5 / O-4's write → scan → print as three ordered steps
with the scan `if: always()` and **no** exit-code-handling exception; FINDING 12's
below-path URL reduction with the residual stated; FINDING 15's `.vizra-e2e/secret/`
vs `.vizra-e2e/out/`; FINDING 3(2,3) + 16 + 21's scanner — base64 → archive-magic →
recurse, credential-**shape** detectors with a recorded false-positive corpus, bounds
sized from measured artifacts with their own exit code, depth **4**; FINDING 7 + 22's
canary on the **shipped** config with the **positive control first** (every marker
demonstrated FOUND with recorders on, in a scratch directory in no upload path)
before absence is asserted, vacuity guards, and ~**8** unique mutations rather than
22; FINDING 14's per-file tripwire exemptions carrying acceptance IDs; O-2's floor of
**≥ 1** per Lane-B project pinned by the canary; and FINDING 20's `AGENTS.md`
sentence written **last**, every clause mapped to a demonstration ID.

The exact replacement sentence is **deliberately not drafted here.** FINDING 20
blocks it on the demonstrations existing, and this repository's own history is that
the sentence written first is the one that turns out to be stronger than its control.
The phase-1 draft below is kept only as a record of what it claimed, with the four
clauses the seat falsified struck through in the commit that replaces it.

### The exact replacement sentence for `AGENTS.md`

Replacing the paragraph that today begins "**The rule that follows, and it is a hard
line.**":

> **The rule that follows, and it is structural.** A spec may authenticate, fill a
> credential or touch a signed URL **only** from `e2e/authenticated/**`, running under
> `playwright.auth.config.ts`, whose projects record **no trace, no screenshot and no
> video** and whose `outputDir` is inside `.vizra-e2e/`, which appears in no upload
> path in `.github/workflows/e2e.yml`. Credentials come from exactly one place — the
> branded `vizraCredentials` fixture in `e2e/harness/authenticated.ts`, which throws
> outside those projects and that directory. **The control is not the directory and
> not a tag: it is the worker guard**, which observes an `Authorization`, `Cookie`,
> `Proxy-Authorization` or `Set-Cookie` header, a signature-shaped query parameter,
> `addCookies` or `storageState` *on the wire*, records the header or parameter NAME
> and never its value, and **fails any test in a non-authenticated project that
> produces one** — so the four evasions
> `e2e/harness/no-credentials-in-specs.test.ts` was measured not to catch
> (`pressSequentially`, `document.cookie` via `evaluate`, `process.env`, a helper
> inside `e2e/harness/`) are all red, because all four end with a credential on the
> wire. From an authenticated lane CI uploads **one generated text file** —
> test title, project, spec path, status, and the error message with every URL reduced
> to origin and path — and `scripts/ci/scan-artifacts.mjs` walks every byte of every
> path the workflow would upload, recursing archives and decoding base64, percent and
> JSON-escaped forms, and **fails the lane and uploads nothing** if any runtime-minted
> canary marker survives, or if it cannot complete the search. Full traces,
> screenshots and video for an authenticated spec are available **locally only**, with
> `npm run e2e:auth:local`, which is refused when `CI` is set. That is how
> "preserve traces for failures" is honoured here: on the machine of the person who is
> allowed to see the credential.

---

## Verification

Every command below exists today unless marked **(to be implemented)**.

| Lane | Command | Expected |
|---|---|---|
| gate | `npm run ci` | exit 0; today 15 files / 355 tests / 0 skipped → expect **≈ 18 files / ≈ 400 tests / 0 skipped** |
| contract | `npm run check:contract` | exit 0, untouched by this slice |
| lane guard | `bash scripts/ci/check-e2e-lane.sh` | exit 0 |
| lane-guard suite | `bash scripts/ci/require-checks_test.sh` | today 102 cases / 109 assertions → expect **≈ 125 cases**, 0 failed |
| floor | `bash scripts/ci/check-required-floor.sh` | exit 0 |
| pins | `bash scripts/ci/check-image-pins.sh` | exit 0 |
| Lane A | `npm run e2e` (local production server) | `18 passed`, `coverage floor: OK (9/9 9/9)`, `harness stamp: OK (18)` |
| Lane B | `npm run e2e:auth` **(to be implemented)** | 0 tests until M1 adds one; the lane must still exit 0 and write a taint file |
| harness canary | `node scripts/ci/harness-canary.mjs` | `failed all 4 fault-injection fixtures` |
| **privacy canary** | `node scripts/ci/artifact-privacy-canary.mjs` **(to be implemented)** | `0 markers in N files / M archives / B bytes`; summary still names the spec |
| **scanner self-test** | `node scripts/ci/scan-artifacts_test.mjs` **(to be implemented)** | ≈ 22 cases, 0 failed |
| demonstrations | `npm run e2e:demos` | today 123 halves → expect **≈ 123 + 22 × 2 + 8 = ≈ 175 halves**, 0 blocked, 0 failed; regenerates `mutation-digests.txt` |
| F13 | the D9 `page.goto` half | sentinel 3 members → **0**; path readable |

**Fixtures/services/credentials needed:** none beyond a localhost Node server and the
already-installed Chromium. **No credential, no signed URL, no network.**

**Production-mode browser journey:** unchanged for Lane A (the built image at 1440 px
and 390 px). Lane B and the canary drive the **privacy fixture server**, not the
product — they are testing the harness, and pointing them at the product would make
the marker set depend on the app.

**Negative and regression cases:** listed as the "Mutation" column of the threat table
(22 rows), the scanner's 9 fail-closed modes, AP-5's 5 workflow mutations, and AP-4's
4 evasion shapes. Every one is a red half with a transcript.

**Expected artifacts:** `docs/evidence/VZ-FOUND-008/` gains one RED and one GREEN
transcript per demonstration half, plus the regenerated `mutation-digests.txt`.
Transcripts are normalised by the existing `scripts/e2e/normalise-transcript.mjs`
and, per the `sweep-artifacts.sh` discipline, **never reproduce a marker value**.

**Platform:** ADR-009's acceptance platform is GitHub `ubuntu-24.04`, linux/amd64.
Local runs on this macOS arm64 machine carry no platform claim; no emulated amd64
image is built locally.

---

## Residuals — stated at the strength of their controls

* **The scanner proves the absence of *known markers*, not the absence of secrets.**
  It is a canary, not a classifier. A channel nobody planted a marker in is not
  covered by it — which is exactly why "not produced" is the primary control for
  every Lane-B row and the scanner is the backstop.
* **A marker split across a boundary is not found.** If a future format chunked a
  string across two JSON fields or two zip members, the scanner would miss it. Not
  constructed, not claimed closed.
* **The GitHub job log for Lane A is unredactable after the fact** and carries a spec
  source excerpt for a failing test (M7). Mitigated only by: Lane A specs cannot
  authenticate (Decision 3.2), and no credential-shaped literal is committed. Not a
  technical control.
* **An arbitrary `run:` step can still exfiltrate.** `AGENTS.md` already says so; no
  parser closes it; review is the control.
* **`.vizra-e2e/auth-output/` exists on the runner** for the duration of the job and
  is readable by every later step in that job. Not produced is what keeps it thin
  (no trace, no screenshot, no video); what remains there is `error-context.md` and
  `.last-run.json`. Removing the directory at the end of Lane B is **not** proposed
  as a control — it would be a claim about step ordering, which is review.
* **`error-context.md` cannot be disabled.** Measured (M6): it has no option. The
  control for it is "never inside an upload path", which is a path assertion in
  `check-e2e-lane.mjs`, i.e. as strong as that parser — which is a YAML parse, not a
  grep, and is mutation-tested.
* **`check-e2e-lane.mjs`, `e2e/harness/**`, `scripts/ci/**`, `.github/**` can weaken
  all of this.** They are `.github/CODEOWNERS` paths, and **CODEOWNERS enforces
  nothing until an owner applies a ruleset on `main`** — still true, still an owner
  action outside any pull request.
* **The Lane-A/Lane-B split is enforced at runtime for signals that cross the wire.**
  A credential that never crosses the wire — held in a variable, asserted on, and
  printed into a failure message — is caught by the scanner in the canary and by
  nothing else in a real run. Stated, not closed.
* **Chromium only, no WebKit, no accessibility engine, no visual baselines** —
  unchanged.

---

## Open questions — CLOSED by the chair at tick 97

All six are ruled. The rulings are binding and are reproduced in the "Rulings
applied" table at the top of this file; the full text is in
`docs/evidence/warroom/2026-09-21-vizra-user-artifact-privacy-PLAN-REVIEW-security.md`.

| | My recommendation | Ruling |
|---|---|---|
| **O-1** Lane A still uploads traces? | yes, redacted and scanned | **yes for M0 only**, under four mechanical conditions: drop `index.html` (PR A), `PLAYWRIGHT_NO_COPY_PROMPT=1` (PR A), the per-lane taint self-closes Lane A on the first auth signal (PR B), and FINDING 18's trigger moves Lane A to summary-only at the first private-media page (PR B). "Yes with an expiry date the CI enforces." |
| **O-2** Lane-B floor | register at 0 | **no — ≥ 1 per auth project, pinned by the canary.** A floor of 0 is the vacuity mode this repo has already been bitten by twice |
| **O-3** call-and-discard | refuse `void f()`, general case review-only | **accepted verbatim**, plus: the AST matcher must also refuse a **shadowed callee**, or it trades a string defeat for a scope defeat |
| **O-4** allowlist capture-and-re-raise | allowlist the exact shape | **declined, and unnecessary**: `run: npm run e2e:auth > .vizra-e2e/out/auth-lane.log 2>&1` preserves the exit code with no `\|\|` and no `exit "$code"`. The absolute no-exit-code-handling rule stays absolute |
| **O-5** ledger privacy case | proposed text | **chair lands the seat's trimmed text** through the generator once PR B is verified. My text was trimmed: no "every byte of every path the workflow would upload" (FINDING 8), no claim about non-wire channels |
| **O-6** record header names | keep names, never values | **keep names from a FIXED allowlist only.** Never echo an arbitrary observed header or body-parameter name — an echoed name is untrusted text going into the job log (FINDING 13) and an unbounded name list is itself request metadata |

### Where I was wrong, recorded rather than quietly fixed

Four of my phase-1 claims did not survive review, and three of them I have now
re-measured myself:

1. **M8** — "no marker survived only in an encoded form". **False.** Three do, inside
   `index.html`'s base64 template, and they are still live after the shipped
   redactor runs. Re-measured above.
2. **M6** — "no configuration option gates `error-context.md`'s contents". **False**
   for its worst section: `PLAYWRIGHT_NO_COPY_PROMPT` gates the page snapshot at
   `lib/index.js:657-658`. Re-read at source above.
3. **M6** — "`# Test source` is the spec's source around the failure". **Imprecise:**
   it is ±100 lines of `errorLocation.file`, which for an error raised in a helper is
   the helper.
4. **Decision 3.2** — the wire-signal control as I described it **cannot see a
   sign-in**: `request.headers()` / `response.headers()` omit cookie headers by API
   contract in 1.63.0, and a login POST carries no auth header at all — it is a
   request **body**. And the context `request` event never fires for
   `page.request.post()`. Both are PR B's to fix; both are why the `AGENTS.md`
   sentence is now written last rather than first.
## Progress and evidence

### Phase 1 — plan only (2026-09-21, macOS arm64, `@playwright/test` 1.63.0)

Probe: `…/scratchpad/vzap-probe-ZNSCIV` (created with `mktemp -d`, symlinked to
`vizra-user/node_modules`). Markers minted at runtime by `crypto.randomBytes`;
nothing credential-shaped; nothing committed.

| Run | Command | Exit | Outcome |
|---|---|---|---|
| 1 | `npx playwright test` with `trace:{mode:"retain-on-failure",sources:false}`, `screenshot:"only-on-failure"`, `video:"retain-on-failure"` | 1 (intended) | 21-member `trace.zip` + a **second copy** at `playwright-report/data/<sha>.zip`; **all 14 channels survive** — M3 |
| 2 | same spec, `trace/screenshot/video:"off"` | 1 (intended) | only `error-context.md` (+ its report copy) and `results.json` remain — **3 channels still survive** — M6 |
| 3 | a `page.fill` that times out | 1 (intended) | the value is **not** in stdout (the call log names the locator); the **source excerpt is** — M7 |
| 4 | run 1's config, then `bash scripts/ci/redact-artifacts.sh test-results playwright-report` | redactor exit 0, `23 file(s) and 2 archive(s)` | **three markers still live inside `index.html`'s base64 template**, invisible to a raw grep — M8 (corrected) |

Type-level facts from `node_modules/playwright/types/test.d.ts` (421, 7161, 7196,
7238, 7241-7243). `error-context.md`'s producer and its `PLAYWRIGHT_NO_COPY_PROMPT`
gate from `node_modules/playwright/lib/index.js:657-671, 697-717`; its code frame from
`lib/errorContext.js`; its copy into the report from `lib/runner/index.js:1349`; the
base64 report embed from `lib/runner/index.js:3704-3712`.

### Phase 2 — PR A, on `fix/m0-artifact-privacy-a` off `origin/main` (`6bf0a0e`)

| Command | Exit | Counts |
|---|---|---|
| `npm run ci` (baseline, before any change) | **0** | 15 files / **355 tests** / 0 skipped, 8.3 s |
| `npm run ci` (after the lane-guard work) | **0** | 16 files / **394 tests** / 0 skipped |
| `npm run ci` (after the redaction work) | **0** | 16 files / **409 tests** / 0 skipped |
| `bash scripts/ci/require-checks_test.sh` (baseline) | 0 | 102 cases / 109 assertions |
| `bash scripts/ci/require-checks_test.sh` (now) | **0** | **141 cases / 148 assertions / 0 failed** |
| `bash scripts/ci/check-e2e-lane.sh` | **0** | — |
| `npx vitest run scripts/ci/ts-source-facts.test.mjs` | **0** | 39 tests |
| `npx vitest run e2e/harness/redact.test.ts` | **0** | 24 tests |
| `shellcheck scripts/e2e/sweep-artifacts.sh scripts/ci/redact-artifacts.sh` | **0** | clean |

**Facts verified at source, per the rulings:**

* `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02`'s
  `include-hidden-files` default is **`'false'`** — read from that commit's own
  `action.yml` through the GitHub contents API, not from documentation.
* `yegamble/vizra`, `vizra-core`, `vizra-user`, `vizra-search` are **all
  `PRIVATE`** (`gh repo view --json visibility`). So the contract sentence says
  "readable by collaborators", not "world-readable".

**Red demonstrations driven through the real guard** (each also a permanent case
in `require-checks_test.sh`, whose helper REFUSES a mutation that did not change
the file — "a demonstration that does not mutate proves nothing"):

| Mutation of `e2e/harness/test.ts` | Old string check | Now |
|---|---|---|
| clean tree (inverse control) | green | **green** |
| `formatOrphans` call removed | red | **red** |
| + trailing comment `// formatOrphans(a, b)` | **GREEN — defeated** | **red** |
| + string literal `"formatOrphans("` | **GREEN — defeated** | **red** |
| `void formatOrphans(a, b);` | **GREEN — defeated** | **red** |
| shadowed callee `const formatOrphans = () => "x"` | not reachable then | **red** |

The same six for `guardBrowser` in `worker-guard.ts`; `STAMP_ANNOTATION`
surviving only on its import line; four `globalSetup`/`globalTeardown` cases with
two inverse controls; six FINDING 8 upload-scope mutations; two retention; four
env; four `package.json`.

**F13, driven through the shipped `redact-artifacts.sh`** — the verifier's own
three-line reduction, verbatim:

```
"url":"http://host/m.jpg?X-Amz-Sig=SENTINELVALUE&e=60"       -> ?<redacted>
"path":"/m.jpg?X-Amz-Sig=SENTINELVALUE&e=60"                 -> ?<redacted>
"subtitle":"host:3219/m.jpg?X-Amz-Sig=SENTINELVALUE&e=60"    -> ?<redacted>
"subtitle":"127.0.0.1:3000/media/p.jpg?X-Amz-Signature=…"    -> ?<redacted>
prose: see step 3/4? and a 1:23/foo timestamp                -> UNCHANGED
sentinel survivals: 0
```

The first version of my authority pattern required a DOTTED host and left the
verifier's own `host:3219` line unredacted; the committed pattern accepts any
label with an explicit `:port`. The price is deliberate over-redaction of a
`1:23/foo?x=y`-shaped string.

**FINDING 3, and the sweep's blind spot** — measured against the probe tree
AFTER the shipped redactor reported success:

```
old raw grep for the typed-password marker under playwright-report/ :  1 member
new sweep (decode-then-recurse)                                     :  5 members
  including .decoded-0.bin.unzipped/903210ec32f953d9c779.json
  — the member a raw grep cannot see
```

**Two process failures of my own, recorded rather than smoothed over:**

1. I twice edited files **while `npm run e2e:demos` was executing**. Bash reads a
   script incrementally, so the second run died at `exit 127`
   (`line 680: spec: command not found`) and the first recorded ten bogus
   failures against a `check-e2e-lane.mjs` that was mid-edit. Neither run's
   output means anything; both were discarded and the suite re-run on a quiescent
   tree. No committed transcript comes from either.
2. The `Write` tool's JSON interpreted the `\uXXXX` escapes in a regex character
   class I wrote, so `e2e/harness/redact.ts` briefly contained **literal NUL and
   other C0 bytes** in its source. Caught by dumping the bytes with `od -c`, not
   by any test — `tsc`, `eslint` and `vitest` were all green on it. Replaced with
   source-level escapes; the file is now ASCII apart from the prose em-dashes.

### Phase 2 — PR A, fix round 2 of 2 (after verifier FAIL at `4158b10`)

Blocker R2-E (a committed `.npmrc` `node-options` line blanked
`PLAYWRIGHT_NO_COPY_PROMPT` inside the Playwright process with both static guards
green) was treated as a class: three layers — static refusal of parser-readable
routes (`.npmrc` default-deny, `NODE_OPTIONS`/`npm_config_*`/`CI` in any env map,
`$GITHUB_ENV`/`$GITHUB_PATH`/`$GITHUB_STEP_SUMMARY` in run text and env values,
YAML merge keys), a RUNTIME assertion in the Playwright worker
(`e2e/harness/ci-environment.ts`), and an upload-gate refusal of any
`# Page snapshot` in `redact-artifacts.sh`. R2-C: both redactors read one
`redaction-patterns.json`; a 27-entry shared corpus pins both byte for byte (the
round-1 shell redactor fails 26/95). Found while building it: Go's `\u0026`
escaping of `&` also defeated the old query match. R2-A/B/D/G and 9(b) closed;
details in the PR body and commit messages.

| Commit | `npm run ci` on the commit's own tree (rest stashed) |
|---|---|
| `8cc6984` | exit 0 — 17 files / 518 tests / 0 skipped |
| `38f22f3` | exit 0 — 18 files / 526 tests / 0 skipped |
| `b998d72` | exit 0 — 18 files / 527 tests / 0 skipped |
| `11f8975` | exit 0 — 18 files / 527 tests / 0 skipped |

At `11f8975`: `require-checks_test.sh` 182/189/0; `npm run e2e:demos` 133 passed /
0 blocked / 0 failed at load averages 260–450; corpus 95/95; hygiene 289 sources /
13 ledger lines; ESLint 0 warnings; shellcheck clean.

Own-process findings this round, recorded: the upload gate refused D9's real
trace on the first run (the gate working — D9 now runs as CI does); placing the
hygiene check first in `npm run ci` broke d8 (moved last); the Write tool's JSON
turned a `\u0026` in the PR body into `&` (fixed before report; commit messages
and AGENTS.md verified unaffected).

### Status

PR A: READY_FOR_REVIEW at `11f8975` (fix round 2 of 2). PR B: PLANNED, blocked on PR A being verified and merged.
Nothing is VERIFIED — that is an independent verifier's word, not mine.

---

## Blockers and handoff

**No external blocker.** Everything both PRs need is local: Node, the pinned
Chromium, `perl`/`unzip`/`zip`, and the `typescript` and `yaml` devDependencies
already in the lockfile. No credential, no vizra-core, no network beyond localhost.

**Next concrete action:** land PR A's eleven commits in order, `npm run ci` recorded
at every boundary, each new rule red-demonstrated with the digest before/after and the
unapplied-mutation refusal; push; open the PR; report when CI concludes. **Do not
create PR B's branch until PR A is verified and merged** — they overlap in
`check-e2e-lane.mjs`, `.github/workflows/e2e.yml`, `redact.ts` and
`redact-artifacts.sh`. The PR B half of this plan may be refined while PR A is under
verification.

**Deferred cleanup:** the phase-1 probe directory is mine and is deleted when PR B
finishes, not before — PR B's canary reuses its fixture shape.