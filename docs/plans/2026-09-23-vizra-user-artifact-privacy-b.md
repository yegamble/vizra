# Execution plan: VZ-FOUND-008 artifact privacy II, PR B — the authenticated lane

**State: PLANNED (phase 1 — plan only), REVISION 5.** The `vizra-security` seat reviewed revision 1
(`docs/evidence/warroom/2026-09-23-vizra-user-artifact-privacy-b-PLAN-REVIEW-security.md`) and
returned **PLAN APPROVED WITH REQUIRED CHANGES**. The chair's tick-204 rulings accept F1–F11 in
full, F12–F14 and NITs 1–2 into PR B, and the seat's Q1–Q7 answers. This revision applies all of
them. Every changed section carries **[AMENDED r2: …]** naming its findings, so the seat can
re-check quickly. No branch and no code for PR B exist.

**Revision 3** applies the seat's confirmation pass on revision 2 (tick 208, recorded at the end of
the same review file): C1–C6, NITs 1–2 and the answers to Q-r2-1…3, all accepted by the chair.
Sections changed in r3 carry **[AMENDED r3: …]** or **[NEW r3: …]**. The seat checks C1–C4 only.
Phase 2 starts after that check **and** after user #10 merges, on the chair's word.

**Revision 4** applies the seat's check of revision 3 (tick 209, "Seat check of plan revision 3"
in the review file). The seat confirmed C1 and C4; C2 and C3 each had one gap left (R3-1, R3-2).
The chair confirms R3-1 and R3-2 in this text, with no further seat pass. Sections changed in r4
carry **[AMENDED r4: …]** or **[NEW r4: …]**. **R3-1 is written in a form that differs from the
literal wording, for a measured reason; see § Deviation for the chair (R3-1).** Still no code;
phase 2 waits for the chair's go and for user #10 to merge.

**Revision 5** applies the seat's check of revision 4 (tick 211, "Seat check of plan revision 4"
in the review file). The seat **accepted** the R3-1 deviation (one screened launch per worker) on
three conditions, and **confirmed** R3-2. R4-1, R4-2 and the schema NIT are applied here. Sections
changed in r5 carry **[AMENDED r5: …]** or **[NEW r5: …]**. The chair confirms them in the text.

**Lane B's gate stays CLOSED until V-D is closed and D18 is green** (ruling 4). No authenticated
spec with a real credential runs before then. PR B builds and proves the lane's machinery against
a loopback fixture, using runtime-minted synthetic markers only (§ The gate).

## Revision 5 — change log **[NEW r5]**

| Item | Severity | Where it is applied |
|---|---|---|
| R4-1 — the launch screen must read the EFFECTIVE merged options, not the call's arguments | REQUIRED | § Egress, launches in Lane B (superseding r4's key screen); § Deviation (the seat's three conditions); D21h |
| R4-2 — spec-level `test.use` is a second options surface | REQUIRED | § Effective-option assertion (new); § Lint early warnings; D21i |
| NIT — the record schema | accepted | § Taint records, the field list |

## Revision 4 — change log **[NEW r4]**

| Item | Severity | Where it is applied |
|---|---|---|
| R3-1 — a spec's overriding `browser`/`context` fixture could launch with unscreened options | REQUIRED | B-5; § Egress, option surfaces; § Deviation for the chair (R3-1); D21h extended |
| R3-2 — `worker-end` counted records WRITTEN | REQUIRED | § Taint records; the scanner's rule and failure table; D20h third half |
| NIT 1 — bind the C1 outcome record to the inventory's nonce | accepted | the `lane_a_inventory` and `lane_a_inventory_check` steps; the scanner's failure table |
| NIT 2 — `markerTitle` never mints | accepted | the canary spec row |
| NIT 3 — `routeFromHAR(…, { update: true })` | accepted | § Lint early warnings |
| NIT 4 — Lane-B and canary workers write start/end pairs too | accepted: **YES** | § Taint records, with the cost stated |
| Q-r3-1 — a benign-header list? | answered: **no**, this is O-1's expiry | § Answers adopted; R-13; the `AGENTS.md` § Residuals text PR B adds |

## Revision 3 — change log **[NEW r3]**

| Item | Severity | Where it is applied |
|---|---|---|
| C1 — the inventory was compared after `redact` rewrote `test-results/` | REQUIRED | B-10; the `lane_a_inventory` and new `lane_a_inventory_check` steps; the scanner's failure table; RC-10a/10b; D19d |
| C2 — F3 still open: WebSocket, `unroute`/`unrouteAll`, option surfaces | REQUIRED | B-5; § Egress; the auth config's `use` key allowlist; Lane B creation-guard refusals; D21f, D21g; RC-4 rows; R-11 |
| C3 — worker-side taint had no closing record | REQUIRED | § Taint records (`worker-start`/`worker-end`), bounded await of pending reads, the paired-record rule, failed write throws; D20h |
| C4 — the T14 marker sat in the failing test's title | REQUIRED | threat row T14; the canary spec; the literal-title lint exemption; D19b |
| C5 — stems over-match header names | SHOULD, accepted | § Credential names; B-4; the scanner's header-pair detector; the false-positive corpus |
| C6 — a local `-u` run could write authenticated baselines | SHOULD, accepted | B-11; `.gitignore`; the runtime `updateSnapshots` assertion |
| NIT 1 — precision edit to the F8 text | accepted | § Item 4 (the seat's own amendment, marked) |
| NIT 2 — T18's positive control is M10, and M10 restores cleanly | accepted | the mutations table |
| Q-r2-1…3 | answered by the seat | § Answers adopted |

## Revision 2 — change log **[AMENDED r2]**

| Review item | Severity | Where it is applied |
|---|---|---|
| F1 — every guard signal taints: sticky, worker-side, window-independent | BLOCKER | B-4, § Lane A's runtime auth guard, § Taint, D20a/c/d/g, M9 |
| F2 — taint per invocation, append-only | REQUIRED | § Taint, the scanner's failure table, Q5 |
| F3 — egress bypass by ordinary idioms | REQUIRED | B-5, § Egress, D21c/d/e, RC-8, R-11 |
| F4 — "no screenshot" is only true of automatic capture | REQUIRED | B-2 wording, B-10, the `lane_a_inventory` step, lint |
| F5 — T18, snapshot baselines written into the source tree | REQUIRED | B-11, threat row T18, the auth config, lint, tripwire, M10 |
| F6 — Lane-B-derived text reaching the log | REQUIRED | B-12, `--lane auth` output, the scanner's output rule |
| F7 — R-1 wording, "(V-D open)", precondition to open | REQUIRED | the item 1 placeholder (R-1 sentence only), § The gate, the stamp output lines |
| F8 — the ledger text claims too much | REQUIRED | § Item 4: the seat's verbatim text, supplied by the chair at tick 207 (Q-r2-4 closed) |
| F9 — positive-control derivation, summary deletion, `*.canary.ts` refusal, T14 plant | REQUIRED | § Canary configs, D19a, the scan and print steps |
| F10 — shape detectors against the real trace encodings | REQUIRED | § Scanner detectors and decoding |
| F11 — the `secrets.` backstop | REQUIRED | § The gate, RC-6b/6c/6d |
| F12 — normalised credential-name matching | SHOULD, accepted | § Credential names |
| F13 — link-safe walk, realpath, schema, print allowlist, literal titles | SHOULD, accepted | § Scanner walk, lint |
| F14 — R-5 undercounted pixel channels | SHOULD, accepted | R-5, and the separate PR "Lane A pixel channels off" (Q3) |
| NIT 1 — env refusal prefix `^PW` | accepted | the lane guard, RC-9 |
| NIT 2 — Lane B literals, atomic summary | accepted | the auth config, the summary reporter |
| NIT 3 — sequence after the visibility PR | satisfied | user #9 merged `783483f` |
| Q1–Q7 | answers adopted | § Answers adopted |

## Context

| | |
|---|---|
| Repo | `vizra-user` (`yegamble/vizra-user`) |
| Base | `main` @ `783483f` (user #9 merged). **[AMENDED r2]** PR B also sequences **after** the separate "Lane A pixel channels off" PR (user **#10**, see Q3). Both touch `playwright.config.ts`, `check-e2e-lane.mjs`, `require-checks_test.sh` and `AGENTS.md`, so PR B branches from `main` once #10 is merged |
| Phase-2 branch | `fix/m0-artifact-privacy` in its own worktree, created only after the seat confirms this revision |
| Board row | `docs/plans/WARROOM-BOARD.md` queue **2f** (PR B). Q6's repo-wide fix is queue **2r**, not here |
| Requirement | VZ-FOUND-008 (privacy case, currently `cases.privacy: []`); meta `AGENTS.md`: "Never log credentials, private signed URLs, or raw private metadata" and "Preserve traces for failures" |
| Binding reviews | the 2026-09-21 plan review (FINDINGS 1–23, O-1…O-6) and the 2026-09-23 PR B plan review (F1–F14, NITs, Q1–Q7), both with the chair's rulings |
| Item 1 | owner inbox 10. It stays a placeholder (chair) |

### Classifier stops, recorded

Two phase-1 attempts were stopped by a safety classifier while item 1's design was being worked
out. Each was recorded and reported, not continued. The chair ruled that item 1's design goes to
the owner and is not re-routed to another agent.

### Preflight (2026-09-23, macOS arm64)

| Thing | State |
|---|---|
| node | v22.14.0 via nvm (the `.nvmrc` pin). The shell default is v24.4.1, so every command runs with the nvm 22 binary first on `PATH` |
| `@playwright/test` | 1.63.0, with `chromium-1243` and `chromium_headless_shell-1243` installed |
| `perl`, `unzip`, `zip`, `jq`, `shellcheck`, `gh` | present |
| disk | about 25 GiB free at the time of revision 2. It fell to 377 MiB earlier the same day because of other agents' work, so each phase-2 step checks free space first |
| CI | running (repositories public) |
| BLOCKED | nothing for items 2–4. Item 1: owner |

### Read at source (installed Playwright 1.63.0), for items 2–3

| Fact | Where |
|---|---|
| `trace`, `screenshot`, `video` accept `"off"`; `trace.screenshots?: boolean` exists; `outputDir` is also per-project | `playwright/types/test.d.ts:7196` and prior plan M1 |
| `error-context.md` is written whenever a test has errors, with no config option to gate it; its `# Page snapshot` is gated only by `PLAYWRIGHT_NO_COPY_PROMPT` | `playwright/lib/index.js:657-658, :700-716` |
| `.last-run.json` is written to the first filtered project's `outputDir`, unless `--last-failed-file` or `PLAYWRIGHT_LAST_RUN_OUTPUT_FILE` overrides it | `LastRunReporter` in `playwright/lib/runner/index.js`; `program.js:203` |
| Reporters are global to an invocation | prior plan Decision 2 |
| `headers()` omits cookie headers; `allHeaders()` and `headersArray()` include them and are async | `playwright-core/types/types.d.ts:22245, :22309-22322, :22572-22576` (FINDING 1); re-read at phase 2 |
| The context `request` event does not fire for `APIRequestContext` traffic | `types.d.ts:9386-9395, :10991-10993, :5836-5842` (FINDING 2) |
| **[AMENDED r2: F3, Q7]** `route.fetch()` and the `APIRequestContext` methods reach a shared internal `_innerFetch` (`coreBundle.js:59742`); routes run in reverse registration order | the seat's F3. The builder re-reads both at phase 2 and records the line numbers before relying on them. A missing `_innerFetch` makes the harness **throw** at load, not skip |
| None of the 207 device descriptors in 1.63.0 sets `screenshot`, `video` or `trace` | measured 2026-09-23 while building user #10 |

---

## Item 1 — the per-run stamp key (V-D): PLACEHOLDER

- **Measured fact (M-VD, 2026-09-23).** A probe spec imported the harness `test`. At module
  scope and in its test body it printed only its process role and whether `VIZRA_E2E_STAMP_KEY`
  is a non-empty string, never the value. The scratch config's only relevant line was the lane's
  own `import "…/e2e/harness/test"`, and the harness was byte-identical to `main` `7a3a572`. Both
  commands ran on node 22.14.0 with Playwright 1.63.0.
  - `npx playwright test --list -c <probe>/playwright.config.ts` exited 0.
    - Main-process module scope: `stampKeyDefined=true`.
  - `npx playwright test -c <probe>/playwright.config.ts` exited 0 with 1 passed.
    - Main-process module scope: `stampKeyDefined=true`.
    - Worker module scope: `stampKeyDefined=false`.
    - Worker test body: `stampKeyDefined=false`.
- **Future red/green demonstration (D18), approved by the chair, in exactly this probe shape.**
  - **Red:** today's `main` prints `stampKeyDefined=true` in the main process.
  - **Green:** the fix prints `false` in both the main process and the worker.
  - No other probe.
- **Design authorship: owner inbox (two agent classifier stops on this design).**
- **Residual [AMENDED r2: F7]:** code that runs in the Playwright main process during collection
  runs outside the worker guard, the egress allowlist and the stamp, and is trusted-by-review.

---

## Answers adopted (Q1–Q7) **[AMENDED r2]**

| Q | Ruling | Effect on this plan |
|---|---|---|
| Q1 | Land both synthetic specs now, with F11 hardening. The amended hard rule names V-D and a green D18 as the precondition for opening the gate; opening also requires the CODEOWNERS ruleset (R-9) | § The gate |
| Q2 | One upload step. On a Lane-B-only failure, `test-results/` holds the harness canary's demo outputs, and they are uploaded too | § Workflow; the note is recorded in `AGENTS.md` |
| Q3 | Lane A's pixel channels off, now, in its own PR: user **#10** (`fix/lane-a-pixels-off`). Not part of PR B | Context (sequencing); R-5 |
| Q4 | A red job on a credential-shape hit, with its own exit code and fixed message. The match is never printed. False positives are resolved only by a reviewed corpus diff | § Scanner |
| Q5 | The canary-then-lane ordering is acceptable, with F2 and F9 applied | § Taint; § Canary |
| Q6 | Lane B ignores the environment entirely: the coverage floor is a **reporter option** and every other strictness value is a literal. The repo-wide fix is queue 2r | § The auth config |
| Q7 | Refuse `APIRequestContext` outright in Lane A. Place the refusal, and Lane B's allowlisted patch, at the shared `_innerFetch`; throw if it is missing | § Lane A's runtime auth guard; § Egress |
| **Q-r2-1 [NEW r3]** | Yes: a request-side signal outside every test's window fails the **run** (orphan rule). The protection is the taint, which C3 makes reliable | § Lane A's runtime auth guard |
| **Q-r2-2 [NEW r3]** | `session`, `sessionid` and `sessid` match **exactly**; `assertion` stays a stem, for **body** names only | § Credential names |
| **Q-r2-3 [NEW r3]** | A distinct exit code plus the fixed plain line is enough. An annotation is optional, and if ever added is built only from the fixed lists | § Scanner |
| **Q-r3-1 [NEW r4]** | **No** benign-header list. A CSRF scheme brings a response `Set-Cookie`, which taints Lane A anyway, and a list would be the first fail-open exception in this control. This is O-1's expiry: at M1, Lane A becomes summary-only | R-13; the `AGENTS.md` § Residuals text; the ADR-003 note is the chair's to route |

---

## Acceptance (items 2–4)

| ID | Observable outcome | Demonstrated by |
|---|---|---|
| **B-2 [AMENDED r2: F4, F5]** | A spec in the authenticated lane has **no automatic** trace, screenshot or video capture, and writes no snapshot baseline (B-11). Its output directory, stdout log, JSON report, taint records and `.last-run.json` all sit under `.vizra-e2e/out/`, which is in no upload path. Its **only** uploaded artifact is `e2e-auth-summary/summary.json`, a summary of allowlisted structured fields. A spec that **writes** into the Lane-A upload set by other means is caught by B-10, not prevented | D19 |
| **B-3** | Lane B is a separate Playwright invocation, `playwright.auth.config.ts`, selected only by a byte-pinned script and run only by byte-pinned steps. The lane guard parses the configuration and asserts its privacy-relevant keys | `require-checks_test.sh`, D19 |
| **B-4 [AMENDED r2: F1, F12, Q7] [AMENDED r3: C3, C5]** | In Lane A, **every** guard auth signal **taints** the invocation: a sticky, worker-side, append-only record written when the signal is observed, whatever the test windows are, including late records and teardown. Each worker's records are closed by a `worker-end` record carrying its signal count, and a missing pair withholds (C3). A tainted Lane-A invocation withholds the whole upload with a named message. **Request-side** signals also **fail the test** (or the run when no test owns them): a header on the **exact** credential-header list read via `headersArray()`, a body parameter name matching a body stem or exact name, `addCookies`, `storageState`. A header matching **only by stem** taints but does not fail (C5). `APIRequestContext` use in Lane A is **refused outright**. Names are echoed only as normalised names from the fixed lists | D20 |
| **B-5 [AMENDED r2: F3] [AMENDED r3: C2]** | In Lane B, **browser, WebSocket and `APIRequestContext` traffic** cannot reach a host outside a compiled allowlist, including via `route.continue({ url })`, a spec's own later `route`, `route.fetch()`, `context.unroute`/`unrouteAll`, and a service worker (blocked). The guard installs its own `routeWebSocket`, which closes non-allowlisted URLs; a spec's `routeWebSocket` is refused. The option surfaces that re-route or record traffic (`proxy`, `recordHar`, `recordVideo`, `serviceWorkers` other than `"block"`, `BrowserType.connect`/`connectOverCDP`) are refused at runtime, and the auth config's `use` has an exact key allowlist. **[AMENDED r4: R3-1]** A spec that overrides the `browser` or `context` fixture cannot bring those options either: in Lane B, `launchPersistentContext` and `launchServer` are refused at any time after configuration load, and `launch` is allowed exactly once per worker, with screened options. Refusals are recorded, so `try/catch` does not hide them. Node-level egress from spec code is **not** covered (R-11) | D21 |
| **B-6 [AMENDED r2: F2, F10, F13]** | The scanner fails closed and nothing uploads, in every case in its failure table | `scan-artifacts_test.mjs`, D22 |
| **B-7** | Write → scan → print → upload. The scan runs `if: always()`. Print only after a successful scan, otherwise one fixed sentence. Lane B's stdout goes to a file | `require-checks_test.sh` |
| **B-8 [AMENDED r2: F7, Q1]** | `AGENTS.md` states PR B at measured strength, every clause mapped to a demonstration ID. The hard rule is **kept and amended**: the gate opens only when V-D is closed, D18 is green, and the CODEOWNERS ruleset exists | mapping table in the PR body |
| **B-9 [AMENDED r2: F8]** | The ledger privacy case uses the seat's replacement text, verbatim (§ Item 4). Not edited here | — |
| **B-10 [NEW r2: F4] [AMENDED r3: C1]** | In the **real** CI run, a sha256 inventory of the Lane-A upload set, **excluding** `e2e-auth-summary/summary.json`, is taken after the harness canary and before any Lane-B-shaped invocation. It is compared by a pinned `lane_a_inventory_check` step right after `auth_floor` and **before `redact`** rewrites `test-results/`, which writes an outcome record. `scan` requires the outcome `unchanged`, or `missing-allowed`: the inventory is missing and no Lane-B-shaped (auth or privacy-canary) invocation left a `start` record. Anything else withholds the upload with a named message | D19d, RC-10a/10b |
| **B-11 [NEW r2: F5] [AMENDED r3: C6]** | No snapshot baseline can be written by Lane B. `updateSnapshots: "none"` is asserted in the auth config with no project override, **and at runtime**: Lane B's harness fixture throws unless `testInfo.config.updateSnapshots === "none"`, so a local `-u`/`--update-snapshots` run is refused (C6). `toHaveScreenshot`, `toMatchSnapshot` and `toMatchAriaSnapshot` are refused by lint in `e2e/authenticated/**`. `.gitignore` gains `e2e/authenticated/**/*-snapshots/` and `e2e/authenticated/**/*.aria.yml`. The tripwire refuses tracked `*-snapshots/**` and `*.aria.yml` under `e2e/` | D19 row T18, M10, tripwire case, runtime unit test |
| **B-12 [NEW r2: F6]** | Nothing derived from a Lane-B run reaches the job log except (a) the summary's allowlisted fields, printed after the scan, and (b) **fixed-form** lines: counts, project names from the configuration, and error class from a fixed list. `check-coverage-floor-ran.mjs --lane auth` prints no `error.message`, no title and no parse-error text. The scanner prints no member names | unit tests with markers; D22 |

### Explicitly NOT in scope

- **Item 1**, beyond the placeholder.
- **Lifting the gate** (§ The gate).
- **Q6's repo-wide environment-strictness fix** (queue 2r).
- **Lane A's pixel channels** (user #10).
- No product code, no vizra-core, no network beyond loopback.
- No trace redactor for Lane B (FINDING 23).
- No change to the four guarded signal kinds, the brand, the existing creation-guard patches, the
  250 ms settle, Lane A's floor, `required-checks.txt` or the floor file.
- The meta ledger edit.

---

## Item 2 — authenticated specs: nothing produced, nothing uploaded

### Decision: not produced and not uploaded, rather than redacted, because it fails closed (unchanged)

**Redaction fails open.** Each missed shape leaks. The channels in scope are not URLs: a
`fill()` value is prose in a step title, a body is an opaque `resources/<sha>`, DOM text is a
snapshot, and a header value has no shape. Redacting them means knowing the secret's value.

**Not producing, plus a path the upload step cannot name, fails closed.** The scanner is the
backstop, and it fails rather than passes when it cannot finish.

**Cost:** a red Lane B is diagnosed from the summary plus a local re-run.

**Lane A** keeps uploading for M0 under O-1. Its safety rests on B-4 and B-10, and on user #10
for pixels. It does not rest on redaction of the channels below.

### Threat model, channel by channel **[AMENDED r2: F1, F4, F5, F14]**

Controls:
- **NP**: not produced.
- **NU**: produced only under `.vizra-e2e/out/`, in no upload path.
- **S**: the scanner, which fails closed. It is the backstop, never the primary control.
- **G-fail**: Lane A's guard fails the test **and** taints the invocation.
- **G-taint**: Lane A's guard taints the invocation only.
- **INV**: the Lane-A upload-set inventory (B-10).
- **R**: PR A's URL redaction.

Under F1, every G signal withholds Lane A's entire upload.

| # | Channel | Where it lands | Lane B | Lane A |
|---|---|---|---|---|
| T1 | `Authorization` request header | `1-trace.network` | NP + S | G-fail |
| T2 | `Cookie` request header | `1-trace.network` | NP + S | G-fail |
| T3 | `Set-Cookie` response header | `1-trace.network` | NP + S | G-taint |
| T4 | `x-amz-security-token` and vendor token headers | `1-trace.network` | NP + S | G-taint (normalised names, F12) |
| T5 | request body (login POST) | `resources/*` | NP + S | G-fail (credential-named parameter) |
| T6 | response body token | `resources/*` | NP + S | not detected by G (R-4); S shape scan |
| T7 | non-URL console token | `*-trace.trace`, harness messages | NP + NU + S | R-4; S |
| T8 | DOM snapshots; `error-context.md` `# Page snapshot` | trace, `error-context.md` | NP + NU + S | `PLAYWRIGHT_NO_COPY_PROMPT` + the upload gate (PR A) |
| T9 | Playwright call parameters | `test.trace`, `*-trace.trace` | NP + S | G-fail when the value crosses the wire; R-4 otherwise |
| T10 | scheme-less `host:port/path?query` subtitle | `test.trace` | NP + S | R + S |
| T11 | **automatic** screenshots, video, screencast | `.png`, `.webm`, `screencast/*` | NP; the canary asserts none exists under `.vizra-e2e/out/` | off since user #10 |
| T11b **[NEW r2: F4]** | **spec-written** files: `page.screenshot({ path })`, `tracing.start/stop`, `fs` writes into `test-results/` | wherever the spec wrote them | INV withholds the upload; lint warning | INV (Lane A's own spec writing into its own output is R-12) |
| T12 | assertion value, error message, stack, locator | `error-context.md`, JSON report, stdout | NU + a summary with no free text | as today |
| T13 | `# Test source` frame; `list` excerpt | `error-context.md`, stdout | NU; no `list` reporter | as today |
| T14 **[AMENDED r3: C4]** | artifact file and directory names | everywhere | NU; the scanner reads names too. **Planted** in a **PASSING** canary test: a marker in its **title**, and a second marker in the **name** of a file it attaches. The failing canary test's title stays a literal (C4) | S |
| T15 | the HTML report's base64 archive | `playwright-report/index.html` | NP (no `html` reporter) | not uploaded (PR A); S decodes base64 |
| T16 | `.last-run.json` | the first project's `outputDir` | NU; asserted after the run | hidden, not uploaded |
| T17 | the job log | the run page | the stdout file; fixed-form lines only (B-12) | as today |
| **T18 [NEW r2: F5]** | **snapshot baselines** written into the source tree (`e2e/authenticated/*-snapshots/`, `*.aria.yml`) | the working tree, one `git add` from publication | NP (`updateSnapshots: "none"`) + lint + tripwire | n/a (no authenticated content) |

### Files (item 2) **[AMENDED r2: F9, F10, NIT 2]**

| File | Change |
|---|---|
| `e2e/harness/private-summary-reporter.ts` (new) | A typed object with a fixed key set: `project`, `file`, `line`, `titlePath`, `status`, `retry`, `durationMs`, `errorCount`, `errorClass`, `timedOut`, `reproduce`. `errorClass` comes from a compiled allowlist, anything else becomes `"Other"`. No message, stack, locator, URL, attachment or stdout. **Written atomically** (temp file plus rename, NIT 2). Deletes a stale file in `onBegin`. Prints nothing |
| `scripts/ci/scan-artifacts.mjs` (new) | § Scanner |
| `scripts/ci/artifact-privacy-canary.mjs` (new) | § Canary |
| `scripts/ci/print-auth-summary.mjs` (new) | Validates the summary against its schema, then prints **by allowlist** (F13). Refuses a summary naming a `*.canary.ts` file (F9) |
| `scripts/e2e/privacy-fixture-server.mjs` (new) | Loopback-only (`127.0.0.1`, NIT 2) on a literal port. Serves runtime-minted markers (lowercase hex, F10) through every channel T1–T18. Counts the requests it served |
| `playwright.auth.canary.config.ts` (new) | `{ ...auth, testMatch: "**/*.canary.ts" }`: overrides **only** `testMatch` |
| `playwright.auth.positive.config.ts` (new) **[AMENDED r2: F9]** | Derives from the **canary** configuration, not the auth one, so its `testMatch` selects the canary. Overrides **only** `use.trace`, `use.screenshot`, `use.video` (on) and `outputDir` (`.vizra-e2e/out/canary-positive`) |
| `e2e/authenticated/privacy.canary.ts` (new) **[AMENDED r3: C4]** | Two tests. (1) A **failing** test, with a **literal** title, exercising T1–T13 and T15–T18. (2) A **passing** test whose title is computed from a runtime marker (T14) and which attaches a file whose name carries a second T14 marker. The literal-title lint rule carries **one** exemption: this file, this one test, identified by its title being the single call to the harness helper `markerTitle(…)`. **[AMENDED r4: NIT 2]** `markerTitle` **reads** the canary-minted marker from `.vizra-e2e/secret/` and throws if it is absent; it never mints one. It is configured in the rule's options, because `noInlineConfig` forbids inline disables in `e2e/**`. Collected only by the canary configs |
| `e2e/authenticated/session.auth.ts` (new) | The Lane-B floor test (O-2): signs in to the fixture with synthetic `vizraCredentials` and passes |
| `e2e/harness/required-projects.json` / `.ts` | The two Lane-B projects at minimum 1 each |
| unit tests (new) | `private-summary-reporter.test.ts`, `scan-artifacts_test.mjs`, `auth-configs.test.ts`, `print-auth-summary.test.mjs` |

### Canary **[AMENDED r2: F2, F9]**

The canary never invokes a Lane-A configuration (F2). Its steps, in order:

1. Delete `e2e-auth-summary/summary.json`, at **start and in `finally`** (F9).
2. **D19a, positive control first.** Run under `playwright.auth.positive.config.ts`. The scanner
   must find **every** marker (`found N/N`) in `.vizra-e2e/out/canary-positive/`.
3. **D19b.** Run under the canary config. Over the would-be upload set, the scanner finds
   **0/N**, including both T14 markers of the passing test (C4), and all of these hold:
   - the summary names project, file and title;
   - no `.png`, `.webm` or `.jpeg` exists under `.vizra-e2e/out/`;
   - the inventory of `test-results/` and `playwright-report/` is unchanged;
   - `.vizra-e2e/out/auth-results/.last-run.json` exists;
   - no `*-snapshots/` directory or `*.aria.yml` was created in the working tree (T18).
4. **D19c, vacuity guards.** Tests run > 0, fixture requests served > 0, output files > 0.
   `--mutate=fixture-unreachable` and `--mutate=spec-skipped` are each red.
5. **D19d [NEW r3: C1], the inventory in the workflow shape.** Run as the pinned steps run it:
   - **inverse control:** a **red Lane A** (one deliberately failing Lane-A demo in the set) with a
     **green Lane B** still uploads. The check runs before `redact`, so redaction's in-place rewrite
     is not a change;
   - **red:** a Lane-B write into `test-results/` gives outcome `changed`, and the scan withholds;
   - **red:** with the check moved after `redact` (mutation), every red Lane A withholds, which is
     the defect C1 names.

**Mutations: about 10, one per distinct control.** Each goes red naming its rows, then green when
restored. Digests go to `mutation-digests.txt`.

| Mutation | Control it removes | Rows |
|---|---|---|
| M1 | `use.trace` on in the auth config | T1–T10 |
| M2 | `use.screenshot` on | T11 |
| M3 | `outputDir` → `test-results` | T8, T12, T13, T16 |
| M4 | a `list` reporter added | T13, T17 |
| M5 | the scanner reads contents only | T14 |
| M6 | the scanner skips the base64 decode | T15 |
| M7 | the scanner's depth capped at 1 | nested zip |
| M8 | the summary reporter emits `error.message` | T12 |
| **M9 [NEW r2: F1]** | the request side does not taint | D20a goes red: the test fails **but the upload is not withheld** |
| **M10 [NEW r2: F5] [AMENDED r3: NIT 2]** | `updateSnapshots: "missing"`, with the canary calling `toMatchAriaSnapshot` | T18. **M10 is T18's positive control**: the baseline really is written into the source tree under the mutation. M10's **restore step deletes the baseline it wrote**, and the canary asserts that it is gone before the green half runs |

**Unit tests.**
- The summary reporter: a synthetic `TestResult` whose message, stack, snippet, attachments and
  stdout all carry markers yields a summary byte-identical to one from a marker-free result.
  Adding a key fails. A path token appears nowhere.
- `auth-configs.test.ts`: the canary config deep-equals the auth config except `testMatch`; the
  positive config deep-equals the **canary** config except the three recorders and `outputDir`.
  Red on a reporter added to either.

### Residuals (item 2) **[AMENDED r2: F4, F14]**

- **R-2** (verbatim, FINDING 23): the scanner proves the absence of known markers, not the
  absence of secrets. It is a canary, not a classifier.
- **R-3:** `.vizra-e2e/out/` is readable by later steps in the job. Deleting it is not a control.
- **R-4:** credentials that never cross the wire are outside G: `page.localStorage`,
  `sessionStorage`, IndexedDB, WebSocket frames, service-worker requests, and values held and
  printed. So are response-body and non-URL console tokens in Lane A. Lint warns; runtime coverage
  is not claimed.
- **R-5 [AMENDED r2: F14]:** Lane A's pixel channels.
  - **Screenshots, video and trace screencast frames:** turned off by user #10, measured 2 PNG,
    2 WebM and 3 + 2 frames before, 0 after.
  - **Still present:** image bytes the page fetched (`resources/*`), and DOM snapshots the trace
    viewer re-renders.
  - FINDING 18's trigger still applies to those two channels.
- **R-6:** path-segment secrets survive Lane A's URL redactor. Lane B's summary has no URL.
- **R-13 [NEW r4: Q-r3-1], the expected end of Lane A's trace uploads.** There is no benign-header
  list, by ruling. The first anonymous CSRF or session cookie or header that vizra-core serves
  taints every Lane-A run: a response `Set-Cookie` taints under F1, and an `x-csrf-token` taints by
  the `token` stem under C5. From then on, every Lane-A upload is withheld. **The response is to
  make Lane A summary-only, not to add an exception list.** PR B adds this sentence to
  `vizra-user/AGENTS.md` § Residuals, verbatim: "the first anonymous CSRF or session cookie or
  header from core ends Lane A trace uploads; the response is summary-only, not an exception
  list". The matching note in the ADR-003 notes is for the chair to route.
- **R-7:** a marker split across fields, members or a line wrap is not found.
- **R-12 [NEW r2: F4]:** a Lane-A spec writing into Lane A's own output during Lane A is inside
  the inventory's "before" state and is not detected. Lint warns on `page.screenshot({ path })`,
  `tracing.start` and `fs` writes in `e2e/**`.

---

## Item 3 — Lane B: a separate invocation, gated in CI and not by convention

### The gate: CLOSED until V-D is closed and D18 is green **[AMENDED r2: F7, F11, Q1]**

1. **Synthetic credentials only.** `vizraCredentials` (`e2e/harness/authenticated.ts`) yields
   synthetic credentials from the loopback fixture only. The extended tripwire (FINDING 14)
   asserts that it contains no `process.env` access and no credential-shaped literal.
2. **No secret can reach the workflow** (F11). The lane guard refuses all of these:
   - any `${{ }}` expression anywhere in `e2e.yml` that references the `secrets` context
     (`secrets.X`, `secrets['X']`, `toJSON(secrets)`, and any other spelling that names the
     context) or `github.token` (RC-6b, RC-6c);
   - `e2e.yml` `permissions` other than exactly `contents: read`, at workflow level, and any
     job-level `permissions`;
   - Lane-B tokens (`e2e:auth`, `playwright.auth`, `artifact-privacy-canary`, `scan-artifacts`,
     `e2e-auth-summary`) in **every other** workflow file, and anywhere in `e2e.yml` except its
     pinned steps (RC-6d).
3. **The hard rule is kept and amended** (Q1, F7). The two fixture specs are the only
   authenticating code. The gate opens only in a later reviewed change, once all of these hold:
   - V-D is closed;
   - D18 is green (the approved probe prints `false` in main and worker);
   - the CODEOWNERS ruleset exists on `main` (R-9).
4. **Per-file tripwire entries only**, each naming its acceptance ID: `privacy.canary.ts` and
   `session.auth.ts`. A third authenticating file is red.
5. **"(V-D open)" on every stamp-verified line** (F7). The stamp reporter's
   `harness stamp: OK (N verified)` and `check-coverage-floor-ran.mjs`'s stamp line gain the
   suffix `(V-D open)` until D18 is green. A unit test pins the suffix. Removing it is part of
   item 1's change, not of PR B.

### What Lane B may do, exactly **[AMENDED r2: F3, F4, F5, F13]**

| May | May not |
|---|---|
| sign in, set cookies, fill credential fields and request signed-URL-shaped resources, **against the loopback fixture only** | reach any non-allowlisted host via browser or `APIRequestContext` traffic (B-5); use `routeWebSocket`; register service workers (`serviceWorkers: "block"`) |
| hold an authenticated context in memory | write `storageState` to disk; write snapshot baselines (B-11); write into `test-results/` or `playwright-report/` (B-10 withholds the upload) |
| fail, with the failure recorded as allowlisted summary fields | print anything to the job log (stdout goes to a file); use a non-literal test title (lint, F13) |
| run locally with full recorders through `npm run e2e:auth:local`, selected by **script name** | run with recorders on in CI; take strictness from the environment (Q6) |

### `playwright.auth.config.ts` (asserted by the parsed-config guard) **[AMENDED r2: F3, F5, NIT 2, Q6]**

**Collection.** `testDir: "./e2e/authenticated"`, `testMatch: "**/*.auth.ts"`.

**Projects.** `auth-desktop-chromium-1440` and `auth-mobile-chromium-390`. A project `use` may
spread only `devices["…"]`, and no project may override a key asserted below. The same reader as
user #10 checks this.

**Top-level `use`.** Each value is a literal:
- `trace: "off"`, `screenshot: "off"`, `video: "off"`;
- `serviceWorkers: "block"` (F3);
- `baseURL`: the fixture's literal loopback URL.

**[NEW r3: C2] An exact `use` key allowlist**, read from the parsed config:
- top level: exactly `baseURL`, `trace`, `screenshot`, `video`, `serviceWorkers`,
  `actionTimeout`, `navigationTimeout`;
- per project: exactly `viewport`, plus the one `devices["…"]` spread;
- any other key is refused by name. That includes `proxy`, `recordHar`, `recordVideo`,
  `httpCredentials`, `extraHTTPHeaders`, `storageState`, `launchOptions`, `contextOptions`,
  `connectOptions` and `ignoreHTTPSErrors`.

**Literals elsewhere in the config.**
- `updateSnapshots: "none"` (F5).
- `outputDir: ".vizra-e2e/out/auth-results"`. It is the only output directory, so `.last-run.json`
  lands there.
- `forbidOnly: true`, `retries: 0`, `workers: 1` (NIT 2, Q6). No `process.env` reference
  anywhere in the file; the lane guard refuses the identifier `process` in it.

**Reporters, exactly:**
- `./e2e/harness/private-summary-reporter.ts`;
- `["json", { outputFile: ".vizra-e2e/out/auth-report.json" }]`;
- `["./e2e/harness/coverage-reporter.ts", { floor: "required" }]` (Q6: the floor is a reporter
  option, and `E2E_COVERAGE_FLOOR` is ignored when it is set);
- the stamp reporter.

**`webServer`.** The fixture server, bound to `127.0.0.1` on a literal port, with
`reuseExistingServer: false` (NIT 2). No `E2E_BASE_URL`, no `globalSetup`, no `globalTeardown`.

**Lane identity.** The config imports `./e2e/harness/authenticated`, which seals the lane
(`sealLane("authenticated")`, one-shot, in `e2e/harness/lane.ts`). `playwright.config.ts` seals
`"unauthenticated"`. An unsealed lane fails closed, and a spec that calls `sealLane` throws. The
lane guard requires a genuine CALL in each config.

**`vizraCredentials`** throws unless the lane is `"authenticated"`, the project is in
`AUTH_PROJECTS`, and `testInfo.file` is under `e2e/authenticated/`.

**Two further literal checks.** The lane guard also refuses `.last-run.json` overrides:
`--last-failed-file` (the script is pinned) and `PLAYWRIGHT_LAST_RUN_OUTPUT_FILE` (the `^PW`
refusal, NIT 1). And the chosen literal port is recorded; phase 2 checks it is free before use.

### `package.json` (byte-pinned in `REQUIRED_SCRIPTS`)

```
"e2e:auth":       "playwright test --config=playwright.auth.config.ts"
"e2e:auth:local": "playwright test --config=playwright.auth.local.config.ts"
```

`playwright.auth.local.config.ts` overrides only the three recorders and `outputDir`. No workflow
may mention `auth.local` or `e2e:auth:local`.

### Workflow steps, every new step a byte-pinned role **[AMENDED r2: F4, F6, F9]**

The order is asserted by pin index.

| # | Role | Key content (exact in the pin) |
|---|---|---|
| 9 | `lane` | unchanged |
| 10 | `floor` | unchanged |
| 11 | `canary` | unchanged (harness canary; its demos write into `test-results/`, Q2) |
| **12** | **`lane_a_inventory`** (F4) **[AMENDED r3: C1]** | `run: node scripts/ci/inventory-upload-set.mjs --write` (sha256 of every file in the upload allowlist **except `e2e-auth-summary/summary.json`**, to `.vizra-e2e/out/lane-a-inventory.json`, together with a random **nonce** minted by this step, **[AMENDED r4: NIT 1]**) |
| **13** | **`privacy_canary`** | `run: node scripts/ci/artifact-privacy-canary.mjs` |
| **14** | **`auth_lane`** | `mkdir -p .vizra-e2e/out` then `npm run e2e:auth > .vizra-e2e/out/auth-lane.log 2>&1` (O-4) |
| **15** | **`auth_floor`** | `run: node scripts/ci/check-coverage-floor-ran.mjs --lane auth` (fixed-form output, F6) |
| **15a [NEW r3: C1]** | **`lane_a_inventory_check`** | `if: always()`, `run: node scripts/ci/inventory-upload-set.mjs --check`. It runs **before `redact`**. It writes `.vizra-e2e/out/lane-a-inventory.outcome.json` = `unchanged` \| `changed` \| `missing` \| `missing-allowed`, **plus the inventory's nonce** (or `null` when the inventory is missing) **[AMENDED r4: NIT 1]**, and exits 0 in every case: the verdict is the record, and `scan` enforces it |
| 16 | container logs | unchanged |
| 17 | `redact` | unchanged; `if: failure()` |
| **18** | **`scan`** **[AMENDED r3: C1, C3]** | `id: scan`, `if: always()`, `run: node scripts/ci/scan-artifacts.mjs`. It **reads** the inventory outcome record rather than re-comparing (the comparison happened before `redact`), and applies the taint and worker-pair rules (F1, F2, C3) |
| **19** | **`auth_summary_print`** | `if: always() && steps.scan.outcome == 'success'`, `run: node scripts/ci/print-auth-summary.mjs` |
| **20** | **`auth_summary_withheld`** | `if: always() && steps.scan.outcome != 'success'`, `run: echo "the authenticated lane summary was withheld because the artifact scan did not pass"` |
| 21 | `upload` (changed) | `if: failure() && steps.redact.outcome == 'success' && steps.scan.outcome == 'success'`. `path:` gains the literal `e2e-auth-summary/summary.json` |

**Lane-guard changes.**
- **Roles and pins.** `ROLES` gains the eight roles (r3 adds `lane_a_inventory_check`). The
  pins-file invariants gain each role's exact `run:` and `if:`.
- **Refusal-direction mentions only.** `MENTIONS` gains the Lane-B tokens and `steps.scan`. A
  step carrying one must **be** that pin. No step is identified by a substring.
- **Ordering [AMENDED r3: C1].** Redact, scan, print, withheld and upload are each immediately
  after the last. `lane_a_inventory`, `privacy_canary`, `auth_lane`, `auth_floor` and
  `lane_a_inventory_check` follow `canary` in that order, and `lane_a_inventory_check` must come
  **before** `redact`.
- **Upload allowlist.** `ALLOWED_UPLOAD_PATHS` gains `e2e-auth-summary/summary.json` in the same
  commit as the pinned upload that uses it.
- **Configurations.** `CONFIG_FILES` gains the four new configs, with the literal assertions
  above.
- **Refusals.** The F11 refusals. The environment refusal widens to any key matching `^PW`
  (NIT 1: `PWTEST_*`, `PWDEBUGIMPL`, `PWPAUSE`), beside the existing `PLAYWRIGHT_*` refusal.
- **Scripts.** Byte-pinned, with no `pre`/`post` hooks.

### Lane A's runtime auth guard **[AMENDED r2: F1, F12, Q7]**

**`e2e/harness/worker-guard.ts`** records these auth signals into the worker's append-only buffer:
- request `headersArray()`, which is async (the 250 ms settle dependency is stated);
- request body parameter names, form and JSON;
- response `headersArray()` names.

**Credential names (F12) [AMENDED r3: C5, Q-r2-2].** Names are normalised: lowercased, with `-`
and `_` removed.
- **Headers use an EXACT normalised list only:** `authorization`, `proxyauthorization`,
  `cookie`, `setcookie`, `xapikey`, `xauthtoken`, `dpop`, `xamzsecuritytoken`.
  - A request header on this list **fails the test and taints**.
  - A response header on it (`setcookie`, `xamzsecuritytoken`) **taints**.
  - A header that matches **only a body stem** below **taints but does not fail the test**, and
    its record names the stem.
- **Body parameter names use stems and exact names:**
  - **Strong stems match by substring:** `password`, `passwd`, `secret`, `token`, `apikey`,
    `authorization`, `cookie`, `credential`, `privatekey`, `dpop`, `assertion`.
  - **Exact names only:** `code`, `otp`, `pin`, `key`, `sig`, `session`, `sessionid`, `sessid`
    (Q-r2-2).
  - **OAuth, DPoP and API-key names** are covered: `clientsecret`, `refreshtoken`,
    `accesstoken`, `idtoken`, `codeverifier`, `clientassertion`.
- Only the matched **normalised name or stem** is ever echoed (O-6).

**Taint: every signal, sticky, worker-side (F1).**
- The first auth signal a Lane-A worker observes, at **any** time (a hook, the body, late after
  the window, fixture teardown, or after the last test), makes the worker write its taint record
  **synchronously at observation time**. It does not wait for per-test accounting.
- The record is append-only (§ Taint). Later signals append further records.
- A record is never removed or rewritten.

**Test consequences by signal side.**
- **Request side** (credential header, credential-named body parameter, `addCookies`,
  `storageState`): taint **and** fail the test that owns the window. If no test owns it, the run
  fails, as the orphan rule already does.
- **Response side** (`set-cookie`, vendor token): taint only. An honest test passes, but the
  upload is withheld.

**`APIRequestContext` in Lane A is refused outright (Q7).**
- `e2e/harness/creation-guard.ts` patches the shared internal `_innerFetch` at module load. In
  Lane A every call throws, is recorded, and taints.
- If `_innerFetch` is absent from the installed prototype, the harness **throws at
  configuration load**, and the error names the version.
- The patch's location is confirmed and recorded at phase 2.

### Egress in Lane B (B-5) **[AMENDED r2: F3]**

- **Context route.** The worker guard installs `context.route("**", …)` on Lane-B contexts. It
  aborts, and records, any request whose host:port is not in the allowlist compiled from the auth
  config's literal `baseURL`.
- **`Route.prototype.continue`** is patched at module load to check the **final** URL: the
  request's URL, or `options.url` when given. This closes both a spec's later
  `page.route('**', r => r.continue())`, which runs first, and
  `route.continue({ url: elsewhere })`.
- **`_innerFetch`** is patched in Lane B with the same allowlist. This covers `APIRequestContext`
  and `route.fetch()`. The harness throws at load if `_innerFetch` is missing.
- **WebSocket [AMENDED r3: C2a].** The guard installs its **own** `context.routeWebSocket("**", …)`
  on every Lane-B context. It closes (`WebSocketRoute.close()`) and records a connection to a
  non-allowlisted URL, and calls `connectToServer()` for an allowlisted one. A **spec's**
  `routeWebSocket` on `BrowserContext.prototype` or `Page.prototype` stays refused and recorded,
  so it cannot pre-empt the guard's handler. Both APIs were confirmed in the installed types:
  `types.d.ts:4557, :10482, :18513-18578`.
- **`unroute` / `unrouteAll` [NEW r3: C2b].** In Lane B, `BrowserContext.prototype.unrouteAll` is
  refused and recorded. `BrowserContext.prototype.unroute(url)` **without** a handler argument is
  refused and recorded. A handler-specific `unroute(url, handler)` is allowed, because the guard's
  handler is module-private and no spec can name it. `types.d.ts:10763, :10772`.
- **Option surfaces [NEW r3: C2c].** The Lane-B creation guard refuses, records and throws:
  - `browser.newContext` or `browser.newPage` options carrying `proxy`, `recordHar` or
    `recordVideo`;
  - `serviceWorkers` other than `"block"`;
  - `BrowserType.connect` and `connectOverCDP` **at any time** after configuration load, not only
    while a test is running.
- **Launches in Lane B [NEW r4: R3-1].** `creation-guard.ts` on `main` treats a launch outside an
  armed test as sanctioned (lines 32–44), so an overriding `browser` or `context` fixture could
  launch with options no one screens. In Lane B, from configuration load onward:
  - `BrowserType.launchPersistentContext` and `launchServer` are **refused** (throw and record) at
    any time. Playwright's built-in fixtures never call either;
  - `BrowserType.launch` is allowed **exactly once per worker**, and only when its **effective**
    options pass the screen. **[AMENDED r5: R4-1; supersedes r4's key screen and the chair's
    deep-equality-on-arguments proposal]**
    - **Why effective, not arguments.** The runner's built-in `browser` fixture calls `launch()`
      with **no arguments**. Its options travel in `playwright._defaultLaunchOptions`, which the
      `_browserOptions` auto fixture sets (`playwright/lib/index.js:196-205, :231`), and
      `BrowserType.launch` merges them itself: `options = { ...this._playwright._defaultLaunchOptions, ...options }`
      (`playwright-core/lib/coreBundle.js:63301`, read in the installed 1.63.0;
      `launchServer` :63317 and `launchPersistentContext` :63323 do the same). A screen over the
      arguments would pass the runner's launch unconditionally, and with it a spec's
      `test.use({ launchOptions: { proxy, args } })`.
    - **The screen.** The patched `launch` computes
      `{ ...this._playwright._defaultLaunchOptions, ...args }` exactly as the original does, and
      requires it to **deep-equal** this literal:

      ```
      { handleSIGINT: false,
        artifactsDir: path.join(<project outputDir>, ".playwright-artifacts-" + workerIndex),
        tracesDir: path.join(<artifactsDir>, "traces"),
        headless: <boolean> }
      ```

      The sources are `runner/index.js:5466` and `workerProcessEntry.js:530`. Only `headless`
      varies (either boolean is accepted). `channel` must be **absent**. The user part
      (`use.launchOptions` and the call's own arguments) must contribute **nothing**: `{}`. A key
      added by a future Playwright version fails the deep equality, so the screen **fails
      closed** on a version bump, and the pin is re-measured then.
    - **The slot.** The once-per-worker slot is **consumed before** calling through, so a throwing
      or rejected launch cannot be retried. It is held **per worker process** (module state) and
      **shared across browser types** (`chromium`, `firefox`, `webkit` share one prototype, as
      measured for PR #7).
  - any second `launch` in the worker, or a first one that fails the screen, is refused, recorded
    and thrown;
  - the one allowed launch supplies the worker's browser, whether the built-in fixture or a spec's
    override made the call. Every context on it passes the `newContext`/`newPage` option screen
    above;
  - Lane A is **unchanged**: D13g's sanctioned override keeps working there.
- **`serviceWorkers: "block"`** is a literal asserted in the auth config (RC-8).

### Effective-option assertion in Lane B **[NEW r5: R4-2]**

**The gap.** Spec-level `test.use({ … })` is a second options surface that the configuration's
`use` key allowlist (C2c) never sees.

**The assertion.** The Lane-B harness fixtures read the **effective** value of each option
fixture and require it to **deep-equal** the value the project configures. Any difference throws
before the test body and is recorded, so `try/catch` cannot hide it. The fixtures checked are:
- `trace`, `screenshot`, `video`;
- `launchOptions`, `connectOptions`, `contextOptions`, `proxy`, `serviceWorkers`;
- `baseURL`, `storageState`, `httpCredentials`, `extraHTTPHeaders`, `ignoreHTTPSErrors`.

**Where the configured values come from.** They are read from the resolved `testInfo.project.use`,
so the assertion needs no second copy of the configuration. The configuration itself is held to
its literals by the lane guard.

**Scope.** This applies in Lane B only; in Lane A, `test.use` for a viewport or locale stays
legitimate.

**Early warning.** `test.use(` in `e2e/authenticated/**` is a lint warning.

### Deviation for the chair (R3-1) **[NEW r4]**

- **R3-1's literal fix:** "refuse `launch`/`launchPersistentContext`/`launchServer` at ANY time
  after configuration load".
- **Taken literally, that refuses the lane's own browser.** The Playwright runner launches the
  worker's browser through the same patched `BrowserType.prototype.launch`, unarmed, after
  configuration load. Read from `creation-guard.ts` on `main`:
  - lines 82–83: "Unarmed, every patch is a plain delegation … which is what lets the runner
    launch its own";
  - lines 297–299: "The Browser the RUNNER launches … comes back through here, unarmed".

  Lane B could then never start.
- **This plan keeps the property R3-1 protects** (no browser in Lane B carries unscreened
  options):
  - `launchPersistentContext` and `launchServer` are refused at any time, exactly as written;
  - `launch` is allowed once per worker, with screened options;
  - `connect` and `connectOverCDP` stay refused at any time.
- **The chair confirms or rejects this form** when checking R3-1 in the text. If rejected, the
  alternative needs a way for Lane B to obtain its browser that does not go through `launch`, and
  this plan has not found one.
- **[AMENDED r5] ACCEPTED by the seat (tick 211), on three conditions, all applied above:**
  1. the screen reads the **effective** merged options (R4-1);
  2. the slot is consumed **before** calling through;
  3. the slot is **per worker process** and **shared across browser types**.

  The seat also notes that a `browser` override which runs first gains nothing under R4-1, because
  its launch meets the same screen.

### Taint records **[AMENDED r2: F1, F2] [AMENDED r4: R3-2, NIT 4]**

**Location.** `.vizra-e2e/out/taint.d/`, created with `O_EXCL` under a unique name, and **never
overwritten**. A record is JSON with these fields:
- `config`: the config file's basename;
- `outputDir`;
- `lane`;
- `pid`;
- **[AMENDED r5: NIT]** `kind`: `start` \| `end` (per invocation) \| `worker-start` \| `worker-end` (per worker) \| `signal`;
- **[NEW r5: NIT]** `token`: the worker's random token, on `worker-start`, `worker-end` and every `signal`;
- **[NEW r5: NIT]** `signal` records only: `readKind`, one of `header`, `body`, `cookie-api`, `storage-state`, `api-request`, `unresolved-read`, `failed-read`;
- **[NEW r5: NIT]** `worker-end` only: `signals` (N observed) and `writeFailures` (F);
- `stems`: allowlisted names or stems only;
- `at`.

**Writers.**
- Each invocation's stamp reporter writes `start` in `onBegin` and `end` in `onEnd`.
- Workers write `signal` records at observation time.
- **[NEW r3: C3] Worker-level pairs.**
  - Each worker writes `worker-start` in the worker fixture's setup.
  - It writes `worker-end` in its teardown, carrying `signals: N` and `writeFailures: F`.
    **[AMENDED r4: R3-2]** N is the number of signals the worker **observed**, from an in-memory
    counter incremented **synchronously, before** the write is attempted. It is not the number of
    records written. F counts writes that failed.
  - **[NEW r4: R3-2]** Every `signal` record carries the worker's random **token** (minted at
    `worker-start`), so the scanner counts records per worker exactly.
  - Teardown first **awaits every pending `headersArray()` / body read** the guard started,
    bounded at 2 000 ms. A read still unresolved at the bound is written as a `signal` record of
    kind `unresolved-read`, and counted. **[AMENDED r4: R3-2]** A read that **rejects** is counted
    and written the same way, as kind `failed-read`.
  - Every record write uses `O_EXCL`. A failed write is **counted first** (F), then thrown, which
    fails the worker and the run; it is never swallowed. If the throw lands in an async listener
    and takes the worker down, the missing `worker-end` withholds the upload anyway.
- **[NEW r4: NIT 4] Which workers write pairs: every one.** Lane-A workers (including the harness
  canary's demo workers), Lane-B workers, and the privacy canary's workers all write
  `worker-start`/`worker-end`, and the scanner requires every pair from every invocation. **Cost,
  stated:** a crashed Lane-B or canary worker withholds the whole upload, Lane A's artifacts
  included. That is accepted as the fail-closed direction.

**The scanner's rule [AMENDED r3: C3].** It fails and withholds if any of these holds:
- any record has `lane: "unauthenticated"` and a `signal` kind, from **any** Lane-A invocation.
  That includes the harness canary's demo runs under `playwright.demos.config.ts`;
- there is no `start`/`end` pair for `config: "playwright.config.ts"` with
  `outputDir: "test-results"`, or the pair is incomplete;
- any `worker-start` has no matching `worker-end` (same `pid` and random token);
- **[AMENDED r4: R3-2]** a `worker-end`'s `signals` (N, observed) differs from the number of
  `signal` records on disk carrying that worker's token, **or** its `writeFailures` is above zero.
  A worker killed after a signal-bearing request withholds, and so does a signal whose record
  failed to write.

**Cost, stated:** a Lane-A worker that crashes, and so writes no `worker-end`, withholds the
upload for that run. That is the fail-closed direction C3 asks for.

The privacy canary never invokes a Lane-A config. Locally, stale records fail closed. The
documented remedy is `rm -rf .vizra-e2e/out`.

### Scanner (`scripts/ci/scan-artifacts.mjs`) **[AMENDED r2: F2, F4, F6, F10, F13, Q4]**

**Scope.** The `with.path` literals of the pinned `upload` step in `.github/e2e-pinned-steps.yml`,
plus the summary. Before any byte is read, each path's **realpath** is refused if it resolves
under `.vizra-e2e` (F13).

**Walk (F13).**
- `lstat` every entry. Symlinks, and regular files with `nlink > 1`, are refused, because the
  pinned upload action follows symlinks.
- File **names** are scanned as well as bytes.
- Archives are opened with `unzip` as a bounded subprocess with a deadline, or `node:zlib` for
  gzip.

**Decoding (F10).**
- Every base64 run of **24 or more characters** is decoded and scanned **always**, and recursed
  into when its magic is ZIP or gzip.
- JSON `\uXXXX` and `\/` unescaping.
- Depth ≤ 4.

**Detectors (F10).**
- Canary markers: lowercase hex, when a marker file is given.
- Credential shapes, including the encodings Playwright actually writes:
  - a trace header pair `{"name":"<header name>","value":…}` where the normalised name is on
    the **exact** credential-header list (C5), not a stem;
  - `authorization:\s*(bearer|basic)`;
  - `set-cookie:`;
  - `__Host-` and `__Secure-` cookie names;
  - `X-Amz-(Signature|Security-Token|Credential)`;
  - JWT;
  - PEM private-key headers.
- Corpus true positives are **taken from D19a's measured artifacts**, recorded in
  `scan-artifacts.corpus.json`. Each shape also has a recorded false positive.
  **[AMENDED r3: C5]** The false-positive corpus includes CSRF and CORS header names:
  `x-csrf-token`, `x-xsrf-token`, `access-control-allow-credentials`,
  `access-control-allow-headers` with `authorization` in its value, and
  `access-control-expose-headers`. None of them is a hit.

**Output (F6, Q4, Q-r2-3).** Fixed-form output only:
- counts;
- the upload-path **root** a hit was found under;
- a **detector id**.

It never prints a member name, a matched line, a value, or a JSON-parse error's text; parse errors
print a fixed sentence. A credential-shape hit exits with its own code and fixed message. The job
goes red, and a false positive is resolved only by a reviewed corpus diff.

**Summary schema (F13).** Validated at scan time: exact key set, value types, and `file` not
matching `*.canary.ts` (F9).

**Bounds.** Sized at phase 2 from measured artifacts, at 4× the largest seen. Exceeding one exits
with its own code.

**Failure table.** Every row is non-zero, and nothing uploads.

| Condition | Exit |
|---|---|
| a scope path whose realpath is under `.vizra-e2e` | 1 |
| a symlink, or a hard-linked regular file (`nlink > 1`), anywhere in the walk | 1 |
| a scope path listed but absent (the summary on a run where Lane B never started is the one named exception) | 1 |
| zero files or zero bytes | 1 |
| an unopenable archive | 1 |
| a bound exceeded | 4 |
| Lane-A taint (§ Taint) | 1, fixed message "artifacts withheld — an authentication signal was observed in the unauthenticated lane" |
| **[AMENDED r3: C1]** the `lane_a_inventory_check` outcome record is missing, or is neither `unchanged` nor `missing-allowed` (B-10) | 1, fixed message naming the upload-path root only |
| **[NEW r3: C3] [AMENDED r4: R3-2, NIT 4]** a `worker-start` without its `worker-end`, from **any** invocation; N (observed) ≠ that token's `signal` records on disk; or `writeFailures` > 0 | 1, fixed message |
| **[NEW r4: NIT 1]** the inventory outcome record's `nonce` differs from the inventory's `nonce` (a stale outcome from an earlier run) | 1, fixed message |
| a summary failing its schema, or naming a `*.canary.ts` file | 1 |
| a canary marker file missing, empty, or holding a marker shorter than 16 characters | 1 |
| a canary marker found | 1 |
| a credential shape found | 5, fixed message |
| the scanner throws | 1 |

**`scan-artifacts_test.mjs`**, about 40 cases:
- markers in plain text, zip, a zip within a zip, gzip, base64-in-HTML, a base64 attachment in a
  JSON report, a 24-character base64 run, and a file name;
- each shape, including the trace name/value pair, true and false positive;
- each failure row;
- symlink and hard-link refusal;
- a realpath resolving under `.vizra-e2e`;
- output contains no marker, member name or parse text.

Each is red against a scanner mutated to lack that capability.

### `check-coverage-floor-ran.mjs --lane auth` **[NEW r2: F6]**

The argument is pinned. It reads `.vizra-e2e/out/auth-report.json` and prints only:
- per-project counts;
- the configured project names;
- `stamps verified: N (V-D open)`;
- on failure, a fixed sentence plus the error class from the allowlist.

JSON-parse failures print a fixed sentence. Unit tests feed a report whose titles, messages and
malformed bytes carry markers, and assert that the output holds none.

### `.vizra-e2e` layout (FINDING 15)

- `.vizra-e2e/secret/` (mode 0700) holds the canary marker files. The stamp-key file is item 1's
  and is **not** moved in PR B.
- `.vizra-e2e/out/` holds Lane-B output, the log, the report, `taint.d/`, the inventory and the
  canary scratch directories.

### Lint early warnings (not controls) **[AMENDED r2: F3, F4, F5, F13]**

**In `e2e/authenticated/**`:**
- `toHaveScreenshot`, `toMatchSnapshot` and `toMatchAriaSnapshot` (F5);
- `page.screenshot`, `tracing.start` and `fs`/`node:fs` imports (F4);
- **[NEW r4: NIT 3]** `routeFromHAR(…, { update: true })`, and any `routeFromHAR` whose `update`
  option is not the literal `false` or absent, since that writes a HAR of live traffic;
- **[NEW r5: R4-2]** `test.use(`, as an early warning. The control is the runtime
  effective-option assertion;
- `node:net`, `node:http(s)`, `node:dgram`, `node:child_process` and `fetch` (F3/R-11);
- a test title that is not a string literal (F13).

**In `e2e/specs/**`:** `page.localStorage`, and `document.cookie` via `evaluate` (R-4).

### Tests (item 3), red against `main` or a controlled mutation, then green **[AMENDED r2]**

| ID | Test | Red | Green |
|---|---|---|---|
| RC-1 | a workflow step `npm run e2e:auth` plus the script with `--trace on` | `main`'s guard **exits 0** (its `e2e(?![\w:-])` mention does not claim `e2e:auth`; no `REQUIRED_SCRIPTS` entry), shown at phase 2 in a throwaway tree | refused by name |
| RC-2 | `auth_lane` with `\|\| true`; scan on `if: failure()`; print before scan; upload gate without `steps.scan`; the inventory step moved after `privacy_canary` | red against the new guard with each check mutated off | refused |
| RC-3 | `.vizra-e2e/out/…` in an upload path | refused on `main` (retained red) | refused |
| RC-4 **[AMENDED r3: C2c]** | auth config: `trace: "on"`; a project `outputDir`; an extra `list`; an `E2E_BASE_URL` or `process` reference; `globalSetup`; a foreign spread; `updateSnapshots: "missing"`; `forbidOnly` non-literal; `reuseExistingServer: true`; **and, new in r3, a `use` key off the allowlist at top level or in a project: `proxy`, `recordHar`, `recordVideo`, `launchOptions`, `contextOptions`, `connectOptions`, `extraHTTPHeaders`, `httpCredentials`** | `main` does not read the file: exit 0 | each refused by name |
| RC-5 | `e2e:auth:local` in a workflow | `main`: exit 0 | refused |
| **RC-6b/6c/6d [NEW r2: F11]** | `${{ secrets.X }}`, `${{ secrets['X'] }}` and `${{ toJSON(secrets) }}` in any `e2e.yml` position; `${{ github.token }}`; a Lane-B token in `frontend-ci.yml` | each **exits 0 on `main`** (to be shown at phase 2) | refused by name |
| RC-7 | the summary allowlisted with no pin using it | n/a | refused |
| **RC-8 [NEW r2: F3]** | `serviceWorkers` removed or `"allow"` in the auth config | n/a | refused |
| **RC-9 [NEW r2: NIT 1]** | `PWTEST_X`, `PWDEBUGIMPL`, `PWPAUSE` at each env scope | shown at phase 2 on `main` | refused |
| **RC-10 [NEW r2: F4]** | the `lane_a_inventory` pin missing, duplicated or reordered | n/a | refused |
| **RC-10a [NEW r3: C1]** | `lane_a_inventory_check` placed **after** `redact` | n/a | refused by name |
| **RC-10b [NEW r3: C1]** | `lane_a_inventory_check` missing, or without `if: always()` | n/a | refused by name |
| D20a **[AMENDED r2: F1]** | Lane-A demo: a form POST with a `password` field | on `main` it **passes** and the artifact holds the body | fails naming the stem **and** the upload is withheld (the scan exits 1, fixed message) |
| D20b | `Set-Cookie` on an anonymous page | on `main` it passes and the upload is not withheld | passes, and the upload is withheld |
| D20c **[AMENDED r2: F1, Q7]** | `page.request.post` in Lane A | on `main` it passes | **refused** (throws, recorded, fails) **and** the upload is withheld |
| D20d **[AMENDED r2: F1]** | `Authorization` via `setExtraHTTPHeaders` | on `main` it passes | fails **and** the upload is withheld |
| D20e | inverse control: an honest Lane-A test beside a green Lane B | — | Lane A uploads on failure; Lane-B records do not taint Lane A |
| D20f | the settle edge for the async header read | mutation: settle 0 → the test is not failed | fails |
| **D20g [NEW r2: F1]** | a credential request fired **after** the test's window (late, and in `afterAll`) | on `main` it passes. Mutation "taint only via test accounting" → the upload is not withheld | the upload is withheld |
| **D20h [NEW r3: C3]** | a Lane-A worker ends while a signal-bearing header read is still pending, and separately a worker that writes no `worker-end` | mutations: (1) teardown does not await pending reads → `worker-end` says 0 signals and the upload is **not** withheld; (2) the scanner does not require `worker-start`/`worker-end` pairs → the upload is not withheld | (1) the read is awaited or counted as `unresolved-read`, and the upload is withheld; (2) the missing `worker-end` withholds; **(3) [NEW r4: R3-2]** a forced write failure (the demo makes `.vizra-e2e/out/taint.d/` unwritable after `worker-start`): N = 1 observed, 0 records on disk, `writeFailures` = 1, so the upload is withheld. Red under the mutation "`worker-end` carries the WRITTEN count and no failure count", where N = 0 matches the disk and the upload is **not** withheld |
| **D20i [NEW r3: C5]** | a Lane-A request carrying `x-csrf-token` only | on the mutation "stems apply to headers" it **fails** the test (the over-match) | it passes, taints, and the upload is withheld; the corpus records the name |
| D21a | Lane B `page.goto` to a foreign host inside `try/catch` | mutation: route not installed → passes | fails, naming the host |
| D21b | the same via `page.request` | mutation: `_innerFetch` allowlist off → passes | fails |
| **D21c [NEW r2: F3]** | a spec's own `page.route('**', r => r.continue())` then a foreign request | mutation: `Route.prototype.continue` unpatched → passes | fails |
| **D21d [NEW r2: F3]** | `route.continue({ url: foreign })` | mutation as D21c → passes | fails |
| **D21e [NEW r2: F3]** | `route.fetch()` to a foreign host | mutation: `_innerFetch` unpatched → passes | fails |
| **D21f [NEW r3: C2b]** | Lane B `context.unroute("**")` and `context.unrouteAll()`, then a foreign request | mutation: `unroute`/`unrouteAll` unpatched → the guard's route is gone and the request passes | refused and recorded; the foreign request still aborts |
| **D21g [NEW r3: C2a]** | a Lane-B page opens `new WebSocket("ws://<foreign host>")` inside `try/catch` | mutation: the guard's `routeWebSocket` not installed → the connection is attempted and nothing is recorded | closed by the guard and recorded; the test fails |
| **D21h [NEW r3: C2c] [AMENDED r4: R3-1]** | Lane B `browser.newContext({ proxy: … })`, `({ recordHar: … })`, `({ serviceWorkers: "allow" })`, and `browserType().connect(…)` during a hook. **r4 adds two fixture-override specs:** (i) a `browser` fixture override that calls `playwright.chromium.launch({ proxy: … })`; (ii) a `context` fixture override that calls `launchPersistentContext(dir, { recordHar: …, serviceWorkers: "allow" })`. **Inverse control:** a `browser` override calling `launch()` with no options is allowed once and guarded, the Lane-B analogue of D13g. **[AMENDED r5: R4-1] r5 adds two cases with NO fixture override:** (iii) `test.use({ launchOptions: { proxy: … } })`; (iv) `test.use({ launchOptions: { args: [<a proxy-server switch>] } })`. Both reach the runner's own no-argument `launch()` through `_defaultLaunchOptions` | mutation: the option refusals off → each is accepted; **mutation "Lane-B launch refusal off"** → both override specs are accepted; **mutation "screen reads call arguments only" [NEW r5]** → (iii) and (iv) are both accepted, which is the defect R4-1 names | each refused, recorded, and the test or run fails; the inverse control stays green. Unit cases in `creation-guard.test.ts` as well, including one per effective-option key added or changed |
| **D21i [NEW r5: R4-2]** | a Lane-B spec with `test.use({ trace: "on" })`, and one with `test.use({ extraHTTPHeaders: { … } })` | mutation "fixture assertion off" → both run, and the first records a trace | both refused before the body, naming the fixture and never its value |
| D22 | the scanner's failure table in the workflow shape | mutation per row | fails closed |
| T-ls | the tripwire: a third authenticating file; a tracked `*-snapshots/` file or `*.aria.yml` under `e2e/` | the first is refused on `main`; the snapshot case is **not** refused on `main` | both refused |
| **U-C6 [NEW r3: C6]** | Lane B run with `--update-snapshots` locally (`npx playwright test --config=playwright.auth.config.ts -u`) | on the mutation "no runtime assertion" the test runs | refused at fixture setup, naming the setting; a unit test pins the assertion |
| **L-C4 [NEW r3: C4]** | the literal-title lint: a second computed title in `privacy.canary.ts`, or one in `session.auth.ts` | n/a | refused; the single exempt test passes |

`npm run ci` is recorded at every commit boundary.

### Residuals (item 3) **[AMENDED r2: F3, F7]**

- **R-1** (item 1's residual): code that runs in the Playwright main process during collection
  runs outside the worker guard, the egress allowlist and the stamp, and is trusted-by-review.
  R-1 persists after item 1 lands. The gate is closed because **V-D is open**, not because of R-1
  (F7).
- **R-8:** pinning a step fixes its bytes, not what they run (the `run:` class; review).
- **R-9:** CODEOWNERS enforces nothing until the owner applies a ruleset. Opening the gate
  requires it (Q1).
- **R-10:** Chromium only.
- **R-11 [NEW r2: F3] [AMENDED r3: C2]:** Node-level egress from spec code (`net`, `http`,
  `child_process`, global `fetch` in the worker) is **outside** B-5. Lint warns. The runtime
  allowlist covers browser HTTP, **WebSocket** and `APIRequestContext` traffic.

---

## Item 4 — the ledger privacy case **[AMENDED r2: F8]**

**Target:** `docs/evidence/ledger-generator/s0_foundation.py`, the `req("VZ-FOUND-008", …)` call,
keyword `privacy=[…]`. Then regenerate `docs/quality/features.json`. A meta builder lands it
**after** PR B is independently verified (O-5).

**Text: the seat's F8 replacement, verbatim** (copied by script from the recorded review's section "F8 replacement ledger text — verbatim from the seat's hand-back", added by the chair at tick 207), **with one amendment by the seat itself [AMENDED r3: NIT 1]:** in the confirmation pass the seat changed "fails the test" to "fails the test, or the run when no test owns the request". Nothing else in the text differs from the recorded verbatim quote:

> An authenticated browser spec publishes no credential and no page content in an uploaded CI artifact or in the job log: it runs only in the separate authenticated lane, whose projects configure no trace, screenshot or video and write no snapshot baseline, whose output directory, log and report are in no upload path, whose writes into an upload path withhold the upload, and whose only contribution to the uploaded artifact is a summary of allowlisted structured fields with no error message, stack, locator or URL. Demonstrated against a loopback fixture with synthetic credentials by an end-to-end canary with runtime-minted markers, positively controlled (every marker found with recorders on) and negatively controlled (none found in the files of the allowlisted upload paths in the shipped configuration). Every run is backstopped by a credential-shape scan that withholds the upload on a hit; that scan detects known shapes and does not prove the absence of secrets. In the unauthenticated lane, a request carrying a header or body parameter from a fixed list of credential names fails the test, or the run when no test owns the request, and any such signal, or a response Set-Cookie or vendor token header, withholds that lane's upload.

As the generator keyword, with the text unchanged:

```
privacy=["An authenticated browser spec publishes no credential and no page content in an uploaded CI artifact or in the job log: it runs only in the separate authenticated lane, whose projects configure no trace, screenshot or video and write no snapshot baseline, whose output directory, log and report are in no upload path, whose writes into an upload path withhold the upload, and whose only contribution to the uploaded artifact is a summary of allowlisted structured fields with no error message, stack, locator or URL. Demonstrated against a loopback fixture with synthetic credentials by an end-to-end canary with runtime-minted markers, positively controlled (every marker found with recorders on) and negatively controlled (none found in the files of the allowlisted upload paths in the shipped configuration). Every run is backstopped by a credential-shape scan that withholds the upload on a hit; that scan detects known shapes and does not prove the absence of secrets. In the unauthenticated lane, a request carrying a header or body parameter from a fixed list of credential names fails the test, or the run when no test owns the request, and any such signal, or a response Set-Cookie or vendor token header, withholds that lane's upload."]
```

Revision 1's draft is withdrawn. F8 found that it claims more than its controls.

Status stays UNVERIFIED until the verifier PASSes PR B.

---

## Files touched (PR B) **[AMENDED r2]**

**New:**
- configs: `playwright.auth.config.ts`, `playwright.auth.canary.config.ts`,
  `playwright.auth.positive.config.ts`, `playwright.auth.local.config.ts`;
- specs: `e2e/authenticated/session.auth.ts`, `e2e/authenticated/privacy.canary.ts`;
- harness: `e2e/harness/authenticated.ts`, `e2e/harness/lane.ts`,
  `e2e/harness/private-summary-reporter.ts`, plus tests;
- scripts: `scripts/ci/scan-artifacts.mjs` with its test and corpus,
  `scripts/ci/artifact-privacy-canary.mjs`, `scripts/ci/print-auth-summary.mjs` with its test,
  `scripts/ci/inventory-upload-set.mjs`, `scripts/e2e/privacy-fixture-server.mjs`;
- demos under `e2e/demos/`.

**Changed:**
- `playwright.config.ts` (`sealLane` only; the recorders are user #10's);
- harness: `e2e/harness/worker-guard.ts` (auth records, sticky taint),
  `e2e/harness/creation-guard.ts` (`_innerFetch`, `Route.prototype.continue`, `routeWebSocket`),
  `e2e/harness/stamp-reporter.ts` (taint `start`/`end` records, the "(V-D open)" suffix; **no
  key change**), `e2e/harness/coverage-reporter.ts` (the `floor` option, Q6),
  `required-projects.*`, `no-credentials-in-specs.test.ts`, `collection.test.ts`;
- `eslint-rules/**`;
- scripts: `scripts/ci/check-e2e-lane.mjs`, `scripts/ci/require-checks_test.sh`,
  `scripts/ci/check-coverage-floor-ran.mjs`, `scripts/ci/ts-source-facts.mjs` (reused readers);
- workflow: `.github/workflows/e2e.yml`, `.github/e2e-pinned-steps.yml`;
- `package.json`;
- `scripts/e2e/demonstrate.sh` (D19–D22);
- `docs/evidence/VZ-FOUND-008/**`;
- `AGENTS.md` (last, and it records Q2's note).

**Not touched:** `e2e/harness/stamp.ts`, `required-checks.txt`, the floor file, `contracts/`,
product code.

## Verification **[AMENDED r2]**

| Lane | Command | Expected |
|---|---|---|
| gate | `npm run ci` | exit 0 at every commit boundary; 0 skipped |
| lane guard | `bash scripts/ci/check-e2e-lane.sh` | exit 0 |
| lane-guard suite | `bash scripts/ci/require-checks_test.sh` | exit 0; the count after user #10 (242 / 249) plus the RC cases; 0 failed |
| floors, pins, contract | `bash scripts/ci/check-required-floor.sh`, `bash scripts/ci/check-image-pins.sh`, `npm run check:contract` | 0 each |
| Lane A | `npm run e2e` | 18 passed, floor 9/9 9/9, `harness stamp: OK (18 verified) (V-D open)` |
| Lane A out-of-process | `node scripts/ci/check-coverage-floor-ran.mjs` | 0 |
| harness canary | `node scripts/ci/harness-canary.mjs` | 4/4 fixtures fail for their own kinds; taint records `clean` |
| upload-set inventory **(new)** | `node scripts/ci/inventory-upload-set.mjs --write`, then `--check` | 0; `--check` exits 1 after any file is added, removed or changed |
| privacy canary **(new)** | `node scripts/ci/artifact-privacy-canary.mjs` | `positive: found N/N`; `shipped: 0/N`; every D19b assertion holds |
| Lane B **(new)** | `mkdir -p .vizra-e2e/out && npm run e2e:auth > .vizra-e2e/out/auth-lane.log 2>&1` | 0; 1 passed per project |
| Lane B out-of-process **(new)** | `node scripts/ci/check-coverage-floor-ran.mjs --lane auth` | 0; fixed-form lines only |
| scanner **(new)** | `node scripts/ci/scan-artifacts.mjs`; `node scripts/ci/scan-artifacts_test.mjs` | 0 on a clean tree; about 40 cases, 0 failed |
| demonstrations | `npm run e2e:demos` | 149 halves plus D19–D22 (including D20g, D21c–e, M9, M10); 0 blocked, 0 failed; ledger byte-identical on rerun |
| shellcheck | `shellcheck scripts/ci/*.sh scripts/e2e/*.sh` | 0 |
| CI | `gh api repos/yegamble/vizra-user/commits/<sha>/check-runs` | every lane success on the pushed SHA, plus a deliberately red run on a throwaway branch whose artifact is downloaded and swept with the new scanner |

- **Fixtures, services and credentials:** a loopback Node server and the installed Chromium.
  No credential, no network.
- **Platform:** ADR-009's `ubuntu-24.04`. Local macOS arm64 runs carry no platform claim.

## Open questions (revision 2's are answered; see § Answers adopted) **[AMENDED r3]**

- **Q-r2-1. ANSWERED (tick 208):** yes; the taint is the protection.
- **Q-r2-2. ANSWERED (tick 208):** `session`, `sessionid`, `sessid` exact; `assertion` a body stem.
- **Q-r2-3. ANSWERED (tick 208):** a distinct exit code plus the fixed line is enough.
- **Q-r3-1 [NEW r3]. ANSWERED (tick 209): no list; this is O-1's expiry (R-13).** The question as asked: Under C5, a header that
  matches only a body stem **taints**, and `x-csrf-token` matches the stem `token`. Once vizra-core
  ships a CSRF header on anonymous pages (M1), every Lane-A run will be tainted and its uploads
  withheld. That fails closed. It also means Lane A uploads nothing from then on, until the header
  is either added to a reviewed benign list or Lane A becomes summary-only (O-1's expiry). The
  plan does **not** add a benign list now. Does the seat want one, or is this the intended expiry
  mechanism?
- **Q-r2-4. CLOSED (tick 207).** The chair appended the seat's verbatim F8 text to the recorded review, and § Item 4 now carries it unchanged.

## Progress and evidence

- 2026-09-23, phase 1, revision 1: M-VD measured; two classifier stops recorded; item 1 to the
  owner inbox.
- 2026-09-23: the visibility PR merged as user #9, `783483f`.
- 2026-09-23, revision 2: the seat's review applied. The "Lane A pixel channels off" PR (Q3) was
  opened separately as user **#10**; its evidence is recorded in that PR and on the board.
- 2026-09-23, tick 207: F8's verbatim text supplied and placed in § Item 4.
- 2026-09-23, revision 3: the seat's confirmation pass (tick 208) applied: C1–C6, NITs 1–2 and
  the answers to Q-r2-1…3. The API names C2 uses were confirmed in the installed 1.63.0 types.
- 2026-09-23, revision 4: the seat's check of r3 (tick 209) applied: C1 and C4 confirmed; R3-1,
  R3-2, NITs 1–4 and the answer to Q-r3-1. R3-1 is written as "launch once, screened" rather
  than "launch refused at any time", because the runner's own browser launch goes through the
  same patched method (`creation-guard.ts:82-83, :297-299` on `main`); see § Deviation.
- 2026-09-23, revision 5: the seat's check of r4 (tick 211) applied. The deviation was accepted on
  three conditions; R3-2 was confirmed. R4-1 (the effective-option screen) is applied, with
  `coreBundle.js:63301` re-read in the installed 1.63.0 and quoted. R4-2 (the effective-option
  assertion) and the schema NIT are applied.

## Blockers and handoff

- **Item 1:** owner inbox 10. The gate stays closed until V-D is closed and D18 is green.
- **F8's verbatim text:** supplied at tick 207 and placed in § Item 4 (Q-r2-4 closed).
- **Next action [AMENDED r5]:** the chair confirms R4-1, R4-2 and the schema NIT in this text.
  Phase 2 starts only after that **and** after user #10 merges, on the chair's word.
