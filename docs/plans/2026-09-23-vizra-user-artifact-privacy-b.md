# Execution plan: VZ-FOUND-008 artifact privacy II, PR B — the authenticated lane, and the per-run stamp key (V-D)

**State: PLANNED (phase 1 — plan only).** No branch and no code exist. This slice is
privacy-critical, so the `vizra-security` seat reviews this plan before any code is written.
PR B additionally gets the seat's review of the code before merge (tick-97 ruling 4).

## Context

| | |
|---|---|
| Repo | `vizra-user` (`yegamble/vizra-user`) |
| Base | `main` @ `7a3a572b5a518a88da4f503ad171956336b11ed5` (PR A, #8, squash-merged 2026-09-23) |
| Phase-2 branch | `fix/m0-artifact-privacy` (created only after this plan is approved) |
| Board row | `docs/plans/WARROOM-BOARD.md` queue **2f** (PR B), including the tick-152 V-D note |
| Requirement | VZ-FOUND-008 (privacy case, currently `cases.privacy: []`); meta `AGENTS.md`: "Never log credentials, private signed URLs, or raw private metadata" and "Preserve traces for failures" |
| Prior plan (binding) | `docs/plans/2026-09-21-vizra-user-artifact-privacy.md`: § "Implementation — PR B", the threat table, the canary and the scanner |
| Binding review | `docs/evidence/warroom/2026-09-21-vizra-user-artifact-privacy-PLAN-REVIEW-security.md`, the chair's tick-97 rulings: FINDINGS 1, 2, 3(2,3), 4, 5, 6, 7, 11, 12, 14, 15, 16, 17, 18, 20, 21, 22 and O-1, O-2, O-4, O-5, O-6 are all PR B's |
| V-D source | `docs/evidence/warroom/2026-09-23-vizra-user-pr8-closing-VERIFY.md` § V8, FINDING V-D |
| Chair ruling for this plan (2026-09-23) | Option (a). Item 1 is scoped to the **measured** read route and a structural fix for it. What code in the main process could otherwise do is **one named residual, in general terms**, not enumerated. The V-D demonstration is **exactly** the probe shape already run. There is no other probe for item 1. |

### A classifier stop, recorded

In the first phase-1 attempt a safety classifier stopped my session during the stamp-key threat
analysis. Following the chair's rule, I recorded it, did not continue that line, and reported.
The chair then ruled option (a). This plan stays inside that ruling. It contains no analysis of
ways to reach or influence the key beyond the one measured read.

### Preflight (2026-09-23, macOS arm64)

| Thing | State |
|---|---|
| node | v22.14.0 via nvm (the `.nvmrc` pin); the shell default is v24.4.1, so every command in this slice runs with the nvm 22 binary first on `PATH` |
| `@playwright/test` | 1.63.0 (`node_modules/playwright/package.json`) |
| browsers | `chromium-1243`, `chromium_headless_shell-1243` installed |
| disk | **2.4 GiB free**. No local image builds beyond what `e2e:demos` already does, and every scratch clone symlinks `node_modules` |
| vizra-user checkout | clean; on `fix/m0-artifact-privacy-a` @ `c2ff445`, whose tree equals `origin/main` (`git diff --stat c2ff445 origin/main` is empty). Read via `git show origin/main:…` only. Phase 2 works in its own worktree |
| CI | Actions ran again at tick 195 (repositories public). Phase 2 records CI on the pushed SHA |
| BLOCKED for this slice | nothing identified. Everything is localhost; there is no vizra-core, no real credential and no network |

**Visibility has changed.** The board records the repositories as **public** since tick 194.
`vizra-user/AGENTS.md` still says artifacts are readable by "collaborators" of a **PRIVATE**
repository. That sentence is now false. From tick 194, Lane A's uploads and every job log are
world-readable for their retention period. PR B corrects the sentence
(`gh repo view yegamble/vizra-user --json visibility` is re-checked at phase 2 and quoted). It
also raises the stakes of every control below.

## What was measured, and what was read

### M-VD — the V-D read route (measured, 2026-09-23, the probe the chair approved)

- **Probe:** a spec that imports the harness `test`. At module scope and in its test body it
  prints only its process role (`TEST_WORKER_INDEX` unset → `main`) and whether
  `VIZRA_E2E_STAMP_KEY` is a non-empty string. It never prints the value.
- **Configuration:** a scratch config whose only relevant line is the lane's own load-bearing
  `import "…/e2e/harness/test"`. The harness files are byte-identical to `main`.
- **Commands:** `npx playwright test --list -c <probe>/playwright.config.ts`, then the same
  without `--list`, both on node 22.14.0 with Playwright 1.63.0.

| Where | `--list` (exit 0) | run (exit 0, 1 passed) |
|---|---|---|
| module scope, **main** process (collection) | `stampKeyDefined=true` | `stampKeyDefined=true` |
| module scope, worker | — (list mode forks none) | `stampKeyDefined=false` |
| test body, worker | — | `stampKeyDefined=false` |

That is V-D's red half, now measured rather than read. The probe's scratch directory was mine
(`mktemp -d`), and I deleted it. The shared checkout was untouched: `git status` was empty, and
the one file under `.vizra-e2e/` predates the probe.

### Read at source (installed Playwright 1.63.0), cited for the design only

| Fact | Where |
|---|---|
| The CLI run loads spec files **in-process** (`createLoadTask("in-process", …)`); only the test-server paths use `OutOfProcessLoaderHost` | `playwright/lib/runner/index.js:6947-6952`, `:2534`, `:6782/6858/6884` |
| Global setup (and the `webServer` plugin) runs before the load task; the run tasks come after it | `runAllTestsWithConfig`, `index.js:6949-6953` |
| A worker is forked with `env: { ...process.env, ...extraEnv }`, where `extraEnv` is only what setup **projects** produce | `ProcessHost.startRunner`, `index.js:1915-1923`; `WorkerHost`, `:5448-5456`; `:6556-6576` |
| Changes the reporter's `onBegin` makes to `process.env` reach the workers forked afterwards | Measured by PR A: D17b's main-process half (restore in `onBegin`, workers inherit the restored value) |
| `.last-run.json` is written to the **first filtered project's `outputDir`**, unless `--last-failed-file` or `PLAYWRIGHT_LAST_RUN_OUTPUT_FILE` overrides it | `LastRunReporter`, `index.js` (constructor); `program.js:203` |
| `playwright.demos.config.ts` spreads the lane config and lists `./e2e/harness/stamp-reporter.ts` in its reporters | `origin/main:playwright.demos.config.ts` |

## Acceptance

| ID | Observable outcome | Demonstrated by |
|---|---|---|
| **B-1** (V-D) | In **every** Playwright configuration that loads the harness, `VIZRA_E2E_STAMP_KEY` is **absent** from the main process's environment while spec files are collected, and absent in every worker once the configuration has loaded. Stamps still verify in-process and out of process. | D18 (the approved probe, red then green) + the lane's `harness stamp: OK (N verified)` and `check-coverage-floor-ran.mjs` as the inverse control |
| **B-2** | An authenticated spec produces **no** trace, screenshot or video. Its output directory, log, taint file and JSON report are in **no** upload path, and its **only** uploaded artifact is a summary of allowlisted structured fields. | D19, the privacy canary (positive control first) |
| **B-3** | The authenticated lane is a **separate Playwright invocation**. It is selected by a byte-pinned `package.json` script and run by byte-pinned workflow steps. Its configuration is parsed and asserted: recorders `"off"`, a literal `outputDir` under `.vizra-e2e/out/`, an exact reporter list, no `E2E_BASE_URL`, no `globalSetup`/`globalTeardown`. `.last-run.json` provably lands under `.vizra-e2e/out/`. | `require-checks_test.sh` mutations, D19 |
| **B-4** | In the **unauthenticated** lane (Lane A), a **request-side** credential (credential headers read through `headersArray()`, credential-shaped body **parameter names**, `addCookies`, `storageState`, an `APIRequestContext` call carrying either) **fails the test**, naming only an allowlisted name. A **response-side** `Set-Cookie` **taints** Lane A's run and **withholds the upload** with a named message, without failing an honest test (FINDINGS 1, 2, 6; O-6). | D20 |
| **B-5** | An authenticated project cannot send a request to a host outside a compiled allowlist, from a page or from `APIRequestContext`. The refusal is recorded, so `try/catch` cannot hide it (FINDING 11). | D21 |
| **B-6** | The scanner **fails closed and uploads nothing** in each of these cases: any path it would scan resolves under `.vizra-e2e`; its marker file is missing or empty when a canary run requires one; zero files; an archive it cannot open; a bound exceeded (its **own** exit code); a taint file missing or tainted for the lane it gates; a credential **shape** found; a canary marker found. It decodes base64 → archive magic → recurse, to depth 4 (FINDINGS 3, 15, 16, 21). | `scan-artifacts_test.mjs`, D22 |
| **B-7** | Workflow order is **write → scan → print**. The scan runs `if: always()`. The summary is printed only after a successful scan; otherwise one fixed sentence is printed. The authenticated lane's stdout goes to a file, never to the log (FINDING 5; O-4). | `require-checks_test.sh` |
| **B-8** | The "no spec may authenticate…" hard gate is **replaced** by the structural rule. The `AGENTS.md` sentence is written **last**, and every clause maps to a demonstration ID (FINDING 20). The visibility sentence is corrected to "public". | the mapping table in the PR body |
| **B-9** | The ledger privacy case is **drafted** below, for the chair to route to a meta builder (O-5). It is **not** edited here. | — |

### Explicitly NOT in scope

- No sign-in UI, owner claim, upload UI or any product code. No real credential, no vizra-core,
  no network beyond localhost.
- No trace redactor for Lane B (Decision 1, FINDING 23). No new URL shapes for Lane A's redactor:
  PR A covered the scheme-less `host:port/path?query` subtitle, and PR B only adds it as a
  scanner/canary row.
- **No further stamp-key work** beyond B-1 (chair ruling): no other probe, and no analysis of
  other routes. That class is residual **R-1**.
- No change to the four guarded signal kinds, the brand, the creation guard's existing patches,
  the 250 ms settle, the Lane-A coverage floor, `required-checks.txt` or the floor file.
- The meta ledger edit (B-9) is another owner's.

## Item 1 — the per-run stamp key (V-D)

### STOPPED — second safety-classifier stop (2026-09-23)

The first attempt at this section was stopped by a safety classifier. Following the chair's rule,
the stop is recorded here and the section was **not** continued. The rest of the plan (item 1's
design, items 2–4, files, verification, residuals, the ledger draft and the open questions) is
**not written**. This file is INCOMPLETE and is not ready for the security seat's review.

## Blockers and handoff

- **Blocker:** a second classifier stop while evaluating the V-D candidate shapes. Chair action
  needed: decide how item 1's design is authored (for example, by the security seat), or whether
  a builder writes items 2–4 alone with item 1 left as a placeholder.
- **Measured and kept:** M-VD above (red half of V-D, in the approved probe shape).
- **Next concrete action:** the chair's ruling on the above.
