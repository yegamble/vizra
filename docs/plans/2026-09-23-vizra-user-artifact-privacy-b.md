# Execution plan: VZ-FOUND-008 artifact privacy II, PR B — the authenticated lane

**State: PLANNED (phase 1 — plan only).** No branch and no code exist. This slice is
privacy-critical, so the `vizra-security` seat reviews this plan before any code is written.
PR B additionally gets the seat's review of the code before merge (tick-97 ruling 4).

**Lane B's gate stays CLOSED until item 1 (the per-run stamp key, V-D) lands.** No
authenticated spec runs before then. PR B builds and proves the lane's machinery against a
localhost fixture with runtime-minted synthetic markers. It does **not** lift the "no spec may
authenticate, fill a credential or touch a signed URL" rule for real credentials (§ The gate).

## Context

| | |
|---|---|
| Repo | `vizra-user` (`yegamble/vizra-user`) |
| Base | `main` @ `7a3a572b5a518a88da4f503ad171956336b11ed5` (PR A, #8, squash-merged 2026-09-23) |
| Phase-2 branch | `fix/m0-artifact-privacy` in its own worktree, created only after this plan is approved |
| Board row | `docs/plans/WARROOM-BOARD.md` queue **2f** (PR B) |
| Requirement | VZ-FOUND-008 (privacy case, currently `cases.privacy: []`); meta `AGENTS.md`: "Never log credentials, private signed URLs, or raw private metadata" and "Preserve traces for failures" |
| Prior plan (binding) | `docs/plans/2026-09-21-vizra-user-artifact-privacy.md`: Decisions 1, 2 and 5, the threat table, § "Implementation — PR B" |
| Binding review | `docs/evidence/warroom/2026-09-21-vizra-user-artifact-privacy-PLAN-REVIEW-security.md`, the chair's tick-97 rulings: FINDINGS 1, 2, 3(2,3), 4, 5, 6, 7, 11, 12, 14, 15, 16, 17, 18, 20, 21, 22 and O-1, O-2, O-4, O-5, O-6 are PR B's |
| Chair rulings for this plan (2026-09-23) | (1) Item 1 is scoped to the measured read route. (2) After two classifier stops on item 1's design, item 1 is a **placeholder** and its design goes to the **owner inbox**. (3) Items 2–4 are written in full. (4) The visibility sentence is fixed in a separate, immediate docs PR, not here. |

### Classifier stops, recorded

Two phase-1 attempts were stopped by a safety classifier while item 1's design was being worked
out. Each was recorded and reported, not continued. The chair ruled that item 1's design goes to
the owner and is **not** re-routed to another agent. This plan writes nothing further on item 1
than the placeholder below.

### Preflight (2026-09-23, macOS arm64)

| Thing | State |
|---|---|
| node | v22.14.0 via nvm (the `.nvmrc` pin). The shell default is v24.4.1, so every command in this slice runs with the nvm 22 binary first on `PATH` |
| `@playwright/test` | 1.63.0 (`node_modules/playwright/package.json`) |
| browsers | `chromium-1243`, `chromium_headless_shell-1243` installed |
| `perl`, `unzip`, `zip`, `jq`, `shellcheck`, `gh` | present (used by PR A's lanes) |
| disk | **2.4 GiB free**. No image builds beyond what `e2e:demos` already does. Scratch clones symlink `node_modules` |
| CI | Actions ran again at tick 195 (repositories public). Phase 2 records CI on the pushed SHA |
| BLOCKED | nothing for items 2–4. Everything is localhost: no vizra-core, no real credential, no network. Item 1 is BLOCKED on the owner (see the placeholder) |

### Read at source (installed Playwright 1.63.0), for items 2–3

| Fact | Where |
|---|---|
| `trace`, `screenshot` and `video` accept `"off"`; `outputDir` is also a per-project option | `playwright/types/test.d.ts` (prior plan M1) |
| `error-context.md` is written whenever a test has errors, with no config option to gate it; its `# Page snapshot` is gated only by `PLAYWRIGHT_NO_COPY_PROMPT` | `playwright/lib/index.js:657-658, :700-716` (prior plan M6, corrected) |
| `.last-run.json` is written to the **first filtered project's `outputDir`**, unless `--last-failed-file` or `PLAYWRIGHT_LAST_RUN_OUTPUT_FILE` overrides it | `LastRunReporter` constructor in `playwright/lib/runner/index.js`; `playwright/lib/program.js:203` |
| Reporters are global to an invocation, so the HTML and JSON reporters aggregate every project in a run | prior plan Decision 2 |
| `Request.headers()` and `Response.headers()` omit cookie headers; `allHeaders()` and `headersArray()` include them and are async | `playwright-core/types/types.d.ts:22245, :22309-22322, :22572-22576` (security seat, FINDING 1). Re-read and recorded at phase 2 before use |
| The context `request` event does not fire for `APIRequestContext` traffic | `types.d.ts:9386-9395, :10991-10993, :5836-5842` (FINDING 2). Re-read at phase 2 |

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
- **Residual:** code that runs in the Playwright main process during collection is trusted-by-review.

---

## Acceptance (items 2–4)

| ID | Observable outcome | Demonstrated by |
|---|---|---|
| **B-2** | A spec in the authenticated lane produces **no** trace, screenshot or video. Its output directory, stdout log, JSON report, taint file and `.last-run.json` all sit under `.vizra-e2e/out/`, which is in **no** upload path. Its **only** uploaded artifact is `e2e-auth-summary/summary.json`, a summary of allowlisted structured fields. | D19 (privacy canary, positive control first) |
| **B-3** | The authenticated lane (Lane B) is a **separate Playwright invocation**: `playwright.auth.config.ts`, selected only by a byte-pinned `scripts["e2e:auth"]` and run only by byte-pinned workflow steps. The lane guard parses the configuration and asserts the privacy-relevant keys. | `require-checks_test.sh`, D19 |
| **B-4** | In the **unauthenticated** lane (Lane A), a request-side credential **fails the test**, naming only an allowlisted name (FINDINGS 1, 2; O-6). A response-side `Set-Cookie` **taints** Lane A's run and **withholds the upload** with a named message, without failing an honest test (FINDING 6). | D20 |
| **B-5** | A Lane-B context or `APIRequestContext` cannot reach a host outside a compiled allowlist. The refusal is **recorded**, so `try/catch` does not hide it (FINDING 11). | D21 |
| **B-6** | The artifact scanner fails closed and nothing uploads, in every case in its failure table (FINDINGS 3, 15, 16, 21). | `scan-artifacts_test.mjs`, D22 |
| **B-7** | Workflow order is **write → scan → print → upload**. The scan runs `if: always()`. The summary is printed only after a successful scan; otherwise one fixed sentence is printed. Lane B's stdout goes to a file and never to the log (FINDING 5; O-4). | `require-checks_test.sh` |
| **B-8** | `AGENTS.md` states what PR B does at its measured strength. Every clause maps to a demonstration ID (FINDING 20). The hard rule is **kept** (§ The gate). | the mapping table in the PR body |
| **B-9** | The ledger privacy case is **drafted** (§ Item 4) for the chair to route to a meta builder (O-5). Not edited here. | — |

### Explicitly NOT in scope

- **Item 1**, beyond the placeholder: owner inbox.
- **Lifting the gate.** That means a real credential source for `vizraCredentials`, a real
  authenticated spec, and replacing the hard-rule sentence. It is a later reviewed change after
  item 1 lands.
- No product code, no vizra-core, no network beyond localhost. No trace redactor for Lane B
  (Decision 1, FINDING 23). No new URL shapes for Lane A's redactor: PR A covered the scheme-less
  subtitle, and PR B only adds it as a scanner and canary row.
- No change to the four guarded signal kinds, the brand, the existing creation-guard patches,
  the 250 ms settle, Lane A's floor, `required-checks.txt` or the floor file.
- The visibility sentence (separate docs PR, chair ruling 4).
- The meta ledger edit (B-9).

---

## Item 2 — authenticated specs: nothing produced, nothing uploaded

### Decision: not produced and not uploaded, rather than redacted, because it fails closed

**Redaction fails open.** Each missed shape leaks, and the history is four rounds of missed URL
shapes plus the base64 report copy (PR A, M8). The channels the board names are not URLs:
- a `fill()` value is prose inside a step title (prior plan M5);
- a body is an opaque `resources/<sha>` member;
- DOM text is a snapshot;
- a header value has no shape of its own.

Redacting them means knowing the secret's value, which CI may not hold in any script. A redactor
that misses a channel reports success.

**Not producing, plus a path the upload step cannot name, fails closed.**
- A recorder that is off writes nothing.
- A file written under `.vizra-e2e/out/` cannot be uploaded: the upload path list is a pinned
  literal allowlist, and `.vizra-e2e` is refused in every workflow.
- The scanner is the backstop, and it fails the run rather than passing when it cannot finish
  (§ Scanner).

**Cost:** a red Lane B is diagnosed from the summary plus a local re-run, not from a trace.

**For Lane A**, O-1 stands (keep uploading, redacted, for M0 only). Its safety rests on B-4:
Lane A cannot carry a credential without failing, or tainting and withholding. It does not rest
on redaction of the channels below.

### Threat model, channel by channel

Controls: **NP** = not produced; **NU** = produced only under `.vizra-e2e/out/`, in no upload
path; **S** = the scanner, which fails closed (the backstop, never the primary control); **G** =
Lane A's runtime auth guard (B-4); **R** = PR A's URL redaction.

| # | Channel (board item 2) | Where it lands today (PR A measurements) | Lane B | Lane A |
|---|---|---|---|---|
| T1 | `Authorization` request header | `1-trace.network` | NP (trace off) + S | G fails the test |
| T2 | `Cookie` request header | `1-trace.network` | NP + S | G fails the test |
| T3 | `Set-Cookie` response header | `1-trace.network` | NP + S | G taints the run and the upload is withheld |
| T4 | `x-amz-security-token` and vendor token headers | `1-trace.network` | NP + S | G taints the run (allowlisted response-header name) |
| T5 | request body (login POST) | `resources/*` | NP + S | G fails the test (credential-shaped parameter **name**) |
| T6 | response body (token in JSON) | `resources/*` | NP + S | **not detected by G**: residual R-4. Shape scan (S) over the upload set |
| T7 | a non-URL token in a console message | `*-trace.trace`; harness failure messages | NP + NU (stdout goes to a log file) + S | residual R-4; S shape scan |
| T8 | DOM snapshots in the trace; `error-context.md` `# Page snapshot` | `*-trace.trace`, `error-context.md` | NP (trace off) + NU (`error-context.md` under `.vizra-e2e/out/`) + S | `PLAYWRIGHT_NO_COPY_PROMPT` + the upload gate's snapshot refusal (PR A) |
| T9 | Playwright call parameters (`fill`, `evaluate` arguments, step titles) | `test.trace`, `*-trace.trace` | NP + S | G fails a credential that crosses the wire; residual R-4 otherwise |
| T10 | scheme-less `host:port/path?query` in step subtitles | `test.trace` | NP + S | R (PR A's authority-relative program) + S |
| T11 | screenshots, video, screencast frames | `.png`, `.webm`, `screencast/*.jpeg` | NP; the canary asserts **no** image or video file exists under Lane B's output | residual R-5 (pixels) |
| T12 | the assertion's received value, error message, stack, locator | `error-context.md`, the JSON report, stdout | NU + the summary carries **no** free text (FINDING 4) | as today |
| T13 | `# Test source` code frame and the `list` reporter's excerpt | `error-context.md`, stdout | NU + no `list` reporter in Lane B | as today |
| T14 | artifact file and directory names (from test titles) | everywhere | NU; the scanner checks **names** as well as bytes | S |
| T15 | the HTML report's embedded base64 archive | `playwright-report/index.html` | NP (no `html` reporter in Lane B) | not uploaded (PR A); S decodes base64 → archive |
| T16 | `.last-run.json` | the first project's `outputDir` | NU (Lane B's single top-level `outputDir`); asserted after the run | hidden file, not uploaded (`include-hidden-files` default `false`, PR A M9) |
| T17 | the job log | the run page, not recallable | Lane B's stdout goes to `.vizra-e2e/out/auth-lane.log`; the summary is printed only after the scan | as today (Lane A carries no credential, by G) |

### What item 2 changes, file by file

| File | Change |
|---|---|
| `playwright.auth.config.ts` (new) | Lane B, specified in item 3 |
| `e2e/harness/private-summary-reporter.ts` (new) | Writes `e2e-auth-summary/summary.json` by serialising a typed object with a **fixed key set** per failed or flaky test: `project`, `file`, `line`, `titlePath`, `status`, `retry`, `durationMs`, `errorCount`, `errorClass`, `timedOut`, `reproduce`. `errorClass` is `Error.name` or a matcher name, validated against a compiled allowlist; anything else becomes `"Other"`. `reproduce` is a fixed-form hint naming the local script. No message, stack, locator, URL, attachment or stdout (FINDINGS 4, 12). It deletes a stale file in `onBegin` and writes the new one in `onEnd`. It prints nothing. |
| `scripts/ci/scan-artifacts.mjs` (new) | The scanner (§ Scanner) |
| `scripts/ci/artifact-privacy-canary.mjs` (new) | The canary (§ Canary) |
| `scripts/e2e/privacy-fixture-server.mjs` (new) | Localhost-only Node `http` server on a **literal** port. It serves, per invocation and from runtime-minted markers only: a page with DOM, console and password-input markers; a signed-URL-shaped image; a `/api/login` that takes a form body and answers `Set-Cookie` plus a JSON token; a response with an `x-amz-security-token` header. It counts the requests it serves, for the vacuity guard |
| `playwright.auth.canary.config.ts` (new) | `{ ...auth, testMatch: "**/*.canary.ts" }`: overrides **only** `testMatch` (FINDING 7) |
| `playwright.auth.positive.config.ts` (new) | Overrides **only** `use.trace`, `use.screenshot`, `use.video` (on) and `outputDir` (`.vizra-e2e/out/canary-positive`): the positive control's scratch run |
| `e2e/authenticated/privacy.canary.ts` (new) | Exercises T1–T17 against the fixture and fails deliberately. Collected **only** by the canary config |
| `e2e/authenticated/session.auth.ts` (new) | The Lane-B floor test (O-2: ≥ 1 per project). It signs in to the **fixture** with synthetic credentials from `vizraCredentials` and passes |
| `e2e/harness/required-projects.json` / `.ts` | Adds the two Lane-B projects at minimum **1** each (O-2) |
| `e2e/harness/private-summary-reporter.test.ts`, `scripts/ci/scan-artifacts_test.mjs`, `e2e/harness/auth-configs.test.ts` (new) | Unit and deep-equality tests (below) |

### Tests — red against `main`, then green

Every red half is either (a) the property measured **false on `main` `7a3a572`**, or (b) a
controlled mutation of the new control. Digests are recorded in `mutation-digests.txt`, and a
mutation that does not change the file is refused (PR A's discipline).

| ID | Test | Red | Green |
|---|---|---|---|
| D19a | **Positive control first.** The canary spec under `playwright.auth.positive.config.ts` (recorders on). The scanner must find **every** marker in `.vizra-e2e/out/canary-positive/`. Printed as `found N/N` | (a) On `main` there is no Lane B, so `npm run e2e:auth` fails with a missing script: the absence is recorded as the starting fact. (b) A canary with one channel's plant removed goes red, naming the channel: "plant did not land" | all found |
| D19b | **Shipped configuration.** The canary under the canary config. The scanner over the **would-be upload set** (the pinned upload paths plus the summary) finds **0/N**. The summary still names project, file and title. No `.png`/`.webm`/`.jpeg` exists anywhere under `.vizra-e2e/out/`. Nothing under `test-results/` or `playwright-report/` was created or changed by the Lane-B invocation (sha256 inventory before and after). `.vizra-e2e/out/auth-results/.last-run.json` exists | (a) The same spec run under `playwright.config.ts` (Lane A's recorders and paths, a scratch copy in no upload path) has markers in `test-results/`: the measured statement that `main`'s only lane leaks these channels. (b) The mutations M1–M8 below | 0 markers; all assertions hold |
| D19c | **Vacuity guards.** Tests run > 0, fixture requests served > 0, output files > 0, all asserted before any absence check | `--mutate=fixture-unreachable` → red "planted nothing"; `--mutate=spec-skipped` → red | restored → green |

**Mutations: ~8, one per distinct control (FINDING 22).** Each goes red naming its rows, then
green when restored.

| Mutation | Control it removes | Rows |
|---|---|---|
| M1 | `use.trace` → `"retain-on-failure"` in the auth config | T1–T10 |
| M2 | `use.screenshot` → `"only-on-failure"` | T11 |
| M3 | `outputDir` → `test-results` | T8, T12, T13, T16 |
| M4 | a `list` reporter added to the auth config | T13, T17 |
| M5 | the scanner reads contents only, not names | T14 |
| M6 | the scanner skips the base64 decode | T15 |
| M7 | the scanner's archive depth capped at 1 | nested zip |
| M8 | the summary reporter emits `error.message` | T12 |

**Unit tests.**
- `private-summary-reporter.test.ts`:
  - A synthetic `TestResult` whose message, stack, snippet, attachments and stdout all carry a marker yields a summary **byte-identical** to one from a marker-free result.
  - Adding a key to the summary type fails the test.
  - A path-token URL (`/reset/<40 hex>`) appears nowhere in the summary (FINDING 12).
  - Red on the mutation "emit `message`".
- `auth-configs.test.ts`: the canary and positive configs deep-equal the auth config on every key except the one each overrides. Red on a mutation that adds a reporter to the canary config.

### Residuals (item 2)

- **R-2** (verbatim, FINDING 23): the scanner proves the absence of known markers, not the absence of secrets. It is a canary, not a classifier. In a real run it has no markers, only shapes.
- **R-3:** `.vizra-e2e/out/` exists on the runner for the rest of the job and is readable by every later step. Deleting it is **not** proposed as a control (Decision 5). Not producing it is what keeps it thin.
- **R-4:** credentials that never cross the wire are outside G: `page.localStorage`, `sessionStorage`, IndexedDB, WebSocket frames, service-worker requests, a value held in a variable and printed (FINDING 17). A response-body token and a non-URL console token are likewise not detected by G in Lane A. The lint early warning refuses `page.localStorage` and `document.cookie` via `evaluate` in `e2e/specs/**`; runtime coverage is **not** claimed.
- **R-5:** pixels. Lane A keeps screenshots and video. FINDING 18's trigger is recorded in `AGENTS.md` ("the first spec that renders media moves its project to screenshot and video off"). See open question Q3.
- **R-6:** path-segment secrets (reset, verify, invite, share, CID) survive Lane A's URL redactor by design. Lane B's summary has no URL at all.
- **R-7:** a marker split across two JSON fields, two members or a line wrap is not found.

---

## Item 3 — Lane B: a separate invocation, gated in CI and not by convention

### The gate: CLOSED until item 1 lands

Enforced mechanically, not by convention:

1. `vizraCredentials` (`e2e/harness/authenticated.ts`) yields **synthetic** credentials only: it
   signs up with the privacy fixture server using runtime-minted markers. It has **no** source of
   real credentials. The extended tripwire (FINDING 14) asserts that the file contains no
   `process.env` access and no credential-shaped literal, **and** that `e2e.yml` references no
   `secrets.` context. The lane guard gains a refusal of `secrets.` anywhere in `e2e.yml`. There
   is therefore no route for a real credential to reach a spec.
2. The hard-rule paragraph in `vizra-user/AGENTS.md` **stays**. It is amended to name the two
   fixture specs as the only authenticating code, and to say the gate opens only after item 1
   lands and a reviewed change adds a real credential source.
3. `no-credentials-in-specs.test.ts` keeps sweeping every `.ts` under `e2e/` except the harness.
   `e2e/authenticated/**` gets **per-file** entries only: `privacy.canary.ts` and
   `session.auth.ts`, each naming its acceptance ID and a reason. No directory entry exists
   (FINDING 14). A third authenticating file is red.

### What Lane B may do, exactly

| May | May not |
|---|---|
| sign in, set cookies, fill credential fields, request signed-URL-shaped resources, **against the privacy fixture server only** | reach any host outside the compiled egress allowlist (B-5) |
| hold an authenticated context in memory | write `storageState` to disk; attach files for upload (attachments stay under `.vizra-e2e/out/`) |
| fail, with the failure recorded as allowlisted summary fields | print to the job log: stdout goes to `.vizra-e2e/out/auth-lane.log` |
| run locally with full recorders through `npm run e2e:auth:local` | run with recorders on in CI. The local configuration is selected by **script name**, never by an environment variable; the prior plan's `VIZRA_E2E_LOCAL_TRACE` switch is **dropped**, because strictness is never chosen by the environment |

### `playwright.auth.config.ts` (asserted by the parsed-config guard)

- `testDir: "./e2e/authenticated"`, `testMatch: "**/*.auth.ts"`.
- Two projects: `auth-desktop-chromium-1440` and `auth-mobile-chromium-390`, each with **no**
  `outputDir` or `use` recorder override.
- Top-level `use.trace: "off"`, `use.screenshot: "off"`, `use.video: "off"`.
- `outputDir: ".vizra-e2e/out/auth-results"`, a string literal. It is the first project's
  output directory, so `.last-run.json` lands there. `--last-failed-file` is refused by the
  byte-pinned script, and `PLAYWRIGHT_LAST_RUN_OUTPUT_FILE` by the existing refusal of every
  `PLAYWRIGHT_*` key but one, re-asserted by a `require-checks` case.
- `reporter`, **exactly**:
  - `./e2e/harness/private-summary-reporter.ts`;
  - `["json", { outputFile: ".vizra-e2e/out/auth-report.json" }]`;
  - the coverage reporter;
  - the stamp reporter.

  No `list`, `line`, `dot`, `html`, `blob` or `github`.
- `webServer`: the privacy fixture server on a literal `127.0.0.1` port.
  `baseURL` is that literal. The configuration contains **no** `E2E_BASE_URL` identifier.
- No `globalSetup` or `globalTeardown`. `workers` and `retries` are literals.
- It imports `./e2e/harness/authenticated`. This **seals the lane** at configuration load
  (`sealLane("authenticated")`, one-shot, in `e2e/harness/lane.ts`). `playwright.config.ts`
  seals `"unauthenticated"`. An unsealed lane fails closed at the first test, and a spec that
  calls `sealLane` gets a throw. Lane identity therefore comes from the configuration **file**,
  never from the environment. `check-e2e-lane.mjs` requires a genuine CALL of `sealLane` in each
  configuration (`ts-source-facts`).
- `vizraCredentials` throws unless all three hold: the lane is sealed `"authenticated"`, the
  project is in `AUTH_PROJECTS`, and `testInfo.file` is under `e2e/authenticated/`.

### `package.json` (byte-pinned in `REQUIRED_SCRIPTS`)

```
"e2e:auth":       "playwright test --config=playwright.auth.config.ts"
"e2e:auth:local": "playwright test --config=playwright.auth.local.config.ts"
```

`playwright.auth.local.config.ts` imports the auth config and overrides **only** the three
recorders and `outputDir` (`.vizra-e2e/out/local-traces`). The lane guard refuses any mention
of `auth.local` or `e2e:auth:local` in any workflow.

### Workflow steps — every new step is a byte-pinned role in `.github/e2e-pinned-steps.yml`

The order is asserted by pin index. Steps 1–11 are today's order; new or changed steps are in
bold.

| # | Role | Key content (exact in the pin) |
|---|---|---|
| 9 | `lane` | unchanged |
| 10 | `floor` | unchanged |
| 11 | `canary` | unchanged |
| **12** | **`privacy_canary`** | `run: node scripts/ci/artifact-privacy-canary.mjs`. No `if:`, no `env:`. It runs D19a then D19b and removes its own summary afterwards, so the only summary left is the real lane's |
| **13** | **`auth_lane`** | `run: \|` `mkdir -p .vizra-e2e/out` / `npm run e2e:auth > .vizra-e2e/out/auth-lane.log 2>&1` (O-4: no `\|\|`, no exit-code handling; the default `bash -e` preserves the exit code) |
| **14** | **`auth_floor`** | `run: node scripts/ci/check-coverage-floor-ran.mjs --lane auth`. The argument is pinned; the lane is not chosen by environment |
| 15 | container logs | unchanged (unpinned `always()`, as today) |
| 16 | `redact` | unchanged run; `if: failure()` |
| **17** | **`scan`** | `id: scan`, `if: always()`, `run: node scripts/ci/scan-artifacts.mjs` |
| **18** | **`auth_summary_print`** | `if: always() && steps.scan.outcome == 'success'`, `run: node scripts/ci/print-auth-summary.mjs`. It prints the allowlisted fields and fails if the file is absent |
| **19** | **`auth_summary_withheld`** | `if: always() && steps.scan.outcome != 'success'`, `run: echo "the authenticated lane summary was withheld because the artifact scan did not pass"` |
| **20** | `upload` (changed) | `if: failure() && steps.redact.outcome == 'success' && steps.scan.outcome == 'success'`. `path:` gains the literal `e2e-auth-summary/summary.json` |

**Lane-guard changes (`scripts/ci/check-e2e-lane.mjs`).**
- **Roles and pins.** `ROLES` gains the six roles. The pins-file invariants gain each role's
  exact `run:` and `if:`.
- **Refusal-direction mentions only.** `MENTIONS` gains `e2e:auth`, `playwright.auth`,
  `artifact-privacy-canary`, `scan-artifacts`, `print-auth-summary`, `e2e-auth-summary` and
  `steps.scan`. A step carrying one must **be** that pin. No substring ever identifies a step.
- **Ordering.** "Upload immediately follows redaction" becomes
  `redact` → `scan` → `auth_summary_print` → `auth_summary_withheld` → `upload`, each
  immediately after the last. `privacy_canary` → `auth_lane` → `auth_floor` follow `canary`.
- **Upload allowlist.** `ALLOWED_UPLOAD_PATHS` gains `e2e-auth-summary/summary.json` **in the
  same commit** as the pinned upload change that uses it. Nothing is allowlisted before its step
  exists (PR A rule).
- **Configurations.** `CONFIG_FILES` gains the four new configuration files. The parsed-config
  assertions above fail closed on a spread (except an imported, checked configuration), a
  computed key or a non-literal value.
- **Refusals.** `secrets.` is refused in `e2e.yml`. `scripts["e2e:auth"]` and
  `scripts["e2e:auth:local"]` must be byte-equal to their literals, with no `pre`/`post` hooks.

### Lane A's runtime auth guard (B-4) and Lane B's egress allowlist (B-5)

- **`e2e/harness/worker-guard.ts` gains two records.** Both land in the existing append-only
  buffer and are charged to tests by the existing windows.
  - A `request` record reads `request.headersArray()`, which is async. The 250 ms settle is what
    lets it land before the test's window closes; this is stated in the file and in `AGENTS.md`,
    and D20 has a case at the edge.
  - The same listener records `postDataBuffer()` parameter **names**, for form and JSON bodies.
  - A `response` record reads `response.headersArray()` for `set-cookie` and the vendor-token
    names.
  - Names come from a **fixed allowlist**:
    - headers: `authorization`, `cookie`, `proxy-authorization`, `set-cookie`, `x-amz-security-token`;
    - body parameters: `password`, `passwd`, `secret`, `token`, `otp`, `code`, `client_secret`, `refresh_token`.

    Any other name is never echoed (O-6).
- **`e2e/harness/creation-guard.ts` patches `APIRequestContext.prototype.fetch`** at module
  load, with the same discipline as the existing prototype patches. The same name-only records
  apply to it, and so does the egress allowlist in Lane B (FINDING 2). The method names are
  confirmed in the installed types at phase 2 before use. If the patch proves fragile, the
  fallback is to refuse `APIRequestContext` in Lane A outright; the choice and the reason are
  stated in the PR (FINDING 2's ruling).
- **Consequences by lane (FINDING 6).**
  - Lane A, request side (credential header, credential body name, `addCookies`,
    `storageState`, `APIRequestContext` carrying either): the test **fails**, naming the
    allowlisted name.
  - Lane A, response side (`set-cookie`, vendor token): the test passes, and the run is
    **tainted**.
  - Lane B: all of it is permitted and recorded.
- **Taint.** Each lane's stamp reporter writes `.vizra-e2e/out/taint.<lane>.json` in `onEnd`,
  **always**: `clean`, or tainted with allowlisted reason names. The scanner requires
  `taint.unauthenticated.json` to be present and clean before it passes the Lane-A upload set.
  Missing, unparseable or tainted is a FAIL with the named message "artifacts withheld — an
  authentication signal was observed in the unauthenticated lane".
- **Egress (B-5).** For Lane-B contexts the worker guard installs
  `context.route("**", …)`. It aborts any request whose host:port is not in the allowlist
  compiled from the auth configuration's literal `baseURL`, and **records** the abort, so
  `try/catch` does not hide it. The `APIRequestContext` patch applies the same allowlist.

### Scanner (`scripts/ci/scan-artifacts.mjs`)

- **Scope.** The `with.path` list of the `upload` pin in `.github/e2e-pinned-steps.yml`, read
  as literals (the pin is byte-equal to the workflow, which the guard asserts), plus
  `e2e-auth-summary/summary.json`. Nothing is inferred.
- **Walk.** Every file's bytes **and** its name. Archives are read with `unzip` as a bounded
  subprocess with a deadline, and with `node:zlib` for gzip. Every `;base64,` or long base64 run
  is decoded; when its magic is ZIP or gzip it is recursed into. Depth ≤ **4**.
- **Detectors.**
  - Canary markers, when a marker file is given; the canary always gives one.
  - Credential **shapes**, always (FINDING 16):
    - `authorization:\s*(bearer|basic)`;
    - `set-cookie:`;
    - `__Host-` and `__Secure-` cookie names;
    - `X-Amz-(Signature|Security-Token|Credential)`;
    - JWT;
    - `-----BEGIN [A-Z ]*PRIVATE KEY`.

    Each shape has one true-positive and one false-positive case, recorded in
    `scripts/ci/scan-artifacts.corpus.json`, so tuning is a reviewed diff.
- **Reports.** Counts and **member names** only; never a matching line or a value.
- **Bounds.** Sized in phase 2 from measured artifacts, at 4× the largest observed trace, member
  count and inflated size. Exceeding one exits with its **own** code and message, so it is never
  mistaken for a leak (FINDING 21).

**Failure table.** Every row exits non-zero, and nothing uploads.

| Condition | Exit |
|---|---|
| any scope path resolves under `.vizra-e2e` | 1, naming the path, before a byte is read (FINDING 15) |
| scope path listed but absent (the summary on a run where Lane B never started is the one allowed absence, and is named) | 1 |
| zero files or zero bytes scanned | 1 |
| an archive that cannot be opened | 1 |
| a bound exceeded | 4 |
| a taint file missing, unparseable or tainted for the lane it gates | 1 |
| a canary run given a marker file that is missing, empty, or holds a marker shorter than 16 characters | 1 |
| a marker or credential shape found | 1, naming members |
| the scanner throws | 1 |

**`scan-artifacts_test.mjs`**, about 30 cases:
- a marker plain, in a zip, in a zip in a zip, in gzip;
- a marker base64-embedded in HTML: an archive within HTML, the PR A M8 case;
- a marker in a **file name**;
- one true positive and one false positive per shape;
- one case per failure-table row.

Each is shown red against a scanner mutated to lack that capability.

### `.vizra-e2e` layout (FINDING 15)

- `.vizra-e2e/secret/` (mode 0700): canary marker files. The stamp-key file's location belongs
  to item 1 and is **not** moved in PR B.
- `.vizra-e2e/out/`: Lane B's output, log, JSON report, taint files and the canary scratch
  directories.

### Tests (item 3) — red against `main`, then green

| ID | Test | Red on `main` `7a3a572` | Green |
|---|---|---|---|
| RC-1 | A workflow step `run: npm run e2e:auth`, plus `scripts["e2e:auth"] = "playwright test --config=playwright.auth.config.ts --trace on"` | the `main` guard **exits 0**. Its lane mention uses `e2e(?![\w:-])`, so `e2e:auth` is not claimed, and `REQUIRED_SCRIPTS` has no `e2e:auth` (to be demonstrated at phase 2 in a throwaway tree) | refused by name |
| RC-2 | the pinned `auth_lane` with ` \|\| true` appended; the scan on `if: failure()`; the print before the scan; the upload gate without `steps.scan` | n/a on `main` (no such pins). Red against the new guard **with** each check mutated off | each refused by name |
| RC-3 | `.vizra-e2e/out/auth-lane.log` in an upload `path:` | refused on `main` already (the `.vizra-e2e` sweep): recorded as a **retained** red | still refused |
| RC-4 | auth config: `trace: "on"`; a per-project `outputDir`; an extra `list` reporter; an `E2E_BASE_URL` read; `globalSetup`; a spread of an unchecked object | `main` does not read the file: exit 0 | each refused by name |
| RC-5 | `e2e:auth:local` named in any workflow step | `main`: exit 0 | refused |
| RC-6 | `secrets.X` in `e2e.yml`; `PLAYWRIGHT_LAST_RUN_OUTPUT_FILE` in a step `env:` | the first is not refused on `main` (to be confirmed at phase 2); the second is refused on `main` (retained red) | refused |
| RC-7 | `e2e-auth-summary/summary.json` added to `ALLOWED_UPLOAD_PATHS` with no pinned upload using it | n/a | the pins-file invariant refuses an allowlist entry no pin uses |
| D20a | Lane-A demo: a form POST with a `password` field to the fixture | on `main` the test **passes** (no body-name signal) | fails, naming `password` only |
| D20b | Lane-A demo: the fixture answers `Set-Cookie` on an anonymous page | on `main` it passes and the upload is not withheld | passes, run tainted, upload withheld with the named message |
| D20c | Lane-A demo: `page.request.post` with a `password` body | on `main` it passes (not a browser request) | fails, naming `password` |
| D20d | Lane-A demo: `Authorization` via `setExtraHTTPHeaders` | on `main` it passes | fails, naming `authorization` |
| D20e | inverse control: an honest Lane-A test; Lane B green alongside it | — | Lane A uploads on failure; per-lane taint does not cross over (FINDING 6) |
| D20f | the settle edge: the async header read lands inside the window | controlled mutation: settle 0 → the record misses | lands |
| D21a | Lane-B demo: `page.goto` to a non-allowlisted host, wrapped in `try/catch` | n/a on `main`. Mutation: route not installed → it passes | fails, naming the host |
| D21b | the same through `page.request` | mutation: patch without the allowlist → passes | fails |
| D22 | the scanner's failure table end to end in the workflow shape | mutation per row | fails closed, nothing uploaded |
| T-ls | the tripwire: a third file under `e2e/authenticated/` using `.fill(` | refused on `main` already (retained red) | still refused; the two named files pass |

Demonstration specs under `e2e/demos/` that handle fixture credentials get per-file tripwire
entries, each with its acceptance ID and reason (FINDING 14). `npm run ci` is recorded green at
**every** commit boundary.

### Residuals (item 3)

- **R-1** (item 1's residual, unchanged): code that runs in the Playwright main process during
  collection is trusted-by-review. It applies to Lane B as much as to Lane A, which is one reason
  the gate stays closed.
- **R-8:** pinning a step fixes its bytes, not what they run. An earlier `run:` step or a
  dependency install script can rewrite a script in the workspace. This is the stated `run:`
  class, and review is its control. So is exfiltration by an arbitrary `run:` step.
- **R-9:** `.github/CODEOWNERS` enforces nothing until an owner applies a ruleset.
- **R-10:** Chromium only.

---

## Item 4 — the ledger privacy case (DRAFT for the chair to route; meta is another owner)

Target: `docs/evidence/ledger-generator/s0_foundation.py`, the `req("VZ-FOUND-008", …)` call,
adding the keyword `privacy=[…]`. Then regenerate `docs/quality/features.json` with the
generator; never hand-edit it. It lands through a meta builder **after** PR B is independently
verified (O-5).

The text is the seat's O-5 wording, trimmed per FINDING 20:
- no "every byte of every path the workflow would upload";
- no claim about non-wire channels;
- no claim about the stamp key (item 1).

It adds the Lane-A clause, which has its own demonstration (D20):

```
privacy=["An authenticated browser spec publishes no credential and no page content in an uploaded CI artifact or in the job log: it runs only in the separate authenticated lane, whose projects record no trace, screenshot or video, whose output directory, log and report are in no upload path, and whose only uploaded artifact is a summary of allowlisted structured fields with no error message, stack, locator or URL. Proved by an end-to-end canary with runtime-minted markers, positively controlled (every marker found with recorders on) and negatively controlled (none found in the files of the allowlisted upload paths in the shipped configuration), and by a credential-shape scan of those files. In the unauthenticated lane a request-side credential fails the test and a response Set-Cookie withholds that lane's upload."]
```

Status stays UNVERIFIED until the independent verifier returns PASS on PR B. The case describes
the lane's machinery. It does **not** say a real credential has ever been exercised, because the
gate stays closed until item 1.

---

## Files touched (PR B)

- **New:**
  - `playwright.auth.config.ts`, `playwright.auth.canary.config.ts`,
    `playwright.auth.positive.config.ts`, `playwright.auth.local.config.ts`;
  - `e2e/authenticated/session.auth.ts`, `e2e/authenticated/privacy.canary.ts`;
  - `e2e/harness/authenticated.ts`, `e2e/harness/lane.ts`,
    `e2e/harness/private-summary-reporter.ts`, plus tests;
  - `scripts/ci/scan-artifacts.mjs`, its test and its corpus;
  - `scripts/ci/artifact-privacy-canary.mjs`, `scripts/ci/print-auth-summary.mjs`;
  - `scripts/e2e/privacy-fixture-server.mjs`;
  - new demos under `e2e/demos/`.
- **Changed:**
  - `playwright.config.ts` (the `sealLane` call);
  - `e2e/harness/worker-guard.ts`, `creation-guard.ts`, `stamp-reporter.ts` (the taint file only;
    **no** key change), `required-projects.*`, `no-credentials-in-specs.test.ts`,
    `collection.test.ts` (pins the new roots);
  - `eslint-rules/**` (`vizraCredentials` and `sealLane` harness-owned; `page.localStorage` and
    `document.cookie` via `evaluate` refused as early warnings);
  - `scripts/ci/check-e2e-lane.mjs`, `scripts/ci/require-checks_test.sh`,
    `scripts/ci/check-coverage-floor-ran.mjs` (`--lane auth`);
  - `.github/workflows/e2e.yml`, `.github/e2e-pinned-steps.yml`;
  - `package.json` (two scripts), `.gitignore` (already covers `.vizra-e2e`);
  - `scripts/e2e/demonstrate.sh` (D19–D22);
  - `docs/evidence/VZ-FOUND-008/**`;
  - `vizra-user/AGENTS.md` (written **last**).
- **Not touched:** `e2e/harness/stamp.ts` (item 1), `required-checks.txt`, the floor file,
  `contracts/`, product code.

## Verification

Commands marked **(new)** are implemented by this slice first.

| Lane | Command | Expected |
|---|---|---|
| gate | `npm run ci` | exit 0 at every commit boundary; 0 skipped |
| lane guard | `bash scripts/ci/check-e2e-lane.sh` | exit 0 |
| lane-guard suite | `bash scripts/ci/require-checks_test.sh` | exit 0; today 233 cases / 240 assertions, grows by the RC cases; 0 failed |
| floors, pins, contract | `bash scripts/ci/check-required-floor.sh`, `bash scripts/ci/check-image-pins.sh`, `npm run check:contract` | exit 0 each |
| Lane A | `npm run e2e` (local production server) | 18 passed, floor 9/9 9/9, 18 stamps |
| Lane A out-of-process | `node scripts/ci/check-coverage-floor-ran.mjs` | exit 0 |
| harness canary | `node scripts/ci/harness-canary.mjs` | 4/4 fixtures fail for their own kinds |
| privacy canary **(new)** | `node scripts/ci/artifact-privacy-canary.mjs` | `positive: found N/N`; `shipped: 0/N`; summary names project, file and title; no image or video files; no Lane-A path changed |
| Lane B **(new)** | `mkdir -p .vizra-e2e/out && npm run e2e:auth > .vizra-e2e/out/auth-lane.log 2>&1` | exit 0; 1 passed per project |
| Lane B out-of-process **(new)** | `node scripts/ci/check-coverage-floor-ran.mjs --lane auth` | floor 1/1 1/1 and stamps verified |
| scanner **(new)** | `node scripts/ci/scan-artifacts.mjs`; `node scripts/ci/scan-artifacts_test.mjs` | exit 0 on a clean tree; about 30 cases, 0 failed |
| demonstrations | `npm run e2e:demos` | today 149 halves, plus D19–D22 red and green halves; 0 blocked, 0 failed; the ledger is byte-identical on a rerun |
| shellcheck | `shellcheck scripts/ci/*.sh scripts/e2e/*.sh` | exit 0 |
| CI | `gh api repos/yegamble/vizra-user/commits/<sha>/check-runs` | `ci-required`, `e2e` and every lane success on the pushed SHA, including a **deliberately red** run on a throwaway branch whose uploaded artifact is downloaded and swept (the first real upload of the new set) |

- **Fixtures, services and credentials:** a localhost Node server and the installed Chromium. No
  credential and no network.
- **Platform:** ADR-009's `ubuntu-24.04`. Local macOS arm64 runs carry no platform claim.

## Open questions for the security seat

- **Q1.** Is "gate CLOSED" as defined above sufficient? It means synthetic-only
  `vizraCredentials`, no `secrets.` in `e2e.yml`, per-file tripwire entries, and the hard rule
  kept. Or should PR B land **without** `e2e/authenticated/session.auth.ts` and the canary spec
  until item 1 lands, at the cost of O-2's floor being unproven in CI until then?
- **Q2.** One upload step with a combined gate means a tainted Lane A also withholds Lane B's
  summary (fail closed, one pin). The alternative is two pinned upload steps, one per lane. I
  recommend one.
- **Q3.** FINDING 18, pixels: keep the written trigger, or turn Lane A's
  `screenshot`/`video` off now so the trigger cannot be missed? The public repository raises the
  cost of a missed trigger. I lean to off now, and ask the seat.
- **Q4.** A shape hit in the scanner fails the `e2e` job, because the scan step fails and
  `continue-on-error` is forbidden. FINDING 16 preferred "suppress the upload rather than fail the
  product lane". Is a red job acceptable here?
- **Q5.** The canary runs **before** Lane B and deletes its summary, so the real lane's summary
  is the only one printed or uploaded. Is that ordering, rather than a separate summary path for
  the canary, acceptable? A separate path would mean the canary no longer tests the shipped path.
- **Q6.** `E2E_COVERAGE_FLOOR=off` is an existing **environment-chosen** strictness switch in the
  coverage reporter, refused in the workflow. Should the auth configuration's floor ignore it
  entirely, or should PR B replace it repo-wide with a script-selected local configuration? This
  is the recurring defect class.
- **Q7.** `APIRequestContext.prototype.fetch` patch versus refusing `APIRequestContext` in
  Lane A outright (FINDING 2). The plan measures the patch first. Does the seat want refuse-outright
  as the default instead?

## Progress and evidence

- 2026-09-23, phase 1: M-VD measured. Two classifier stops recorded; item 1 moved to the owner
  inbox by the chair.
- The visibility-sentence docs PR is separate (chair ruling 4); its number and SHA are recorded
  in the war-room board, not here.

## Blockers and handoff

- **Item 1:** owner inbox. Lane B's gate stays closed until it lands.
- **Items 2–4:** no blocker. **Next action:** the security seat reviews this plan; phase 2 starts
  only after its rulings.
