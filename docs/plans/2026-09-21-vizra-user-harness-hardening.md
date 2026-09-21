# Execution plan: VZ-FOUND-008 harness hardening (F12, F14, flush window, contract accuracy)

## Context
- Repo `yegamble/vizra-user`, checkout `/Users/yosefgamble/github/vizra/vizra-user`.
- Base: `main` at `90896beb9669a3b305269a298d507fd7a9e27aa4` (clean, confirmed).
- Branch: `fix/m0-harness-hardening`. Issue reference: `yegamble/vizra#1`.
- Source findings: `/Users/yosefgamble/github/vizra/docs/evidence/warroom/2026-09-20-vizra-user-pr3-browser-env-VERIFY.md`,
  sections "Re-verification at c669e40" (FINDING 12, FINDING 14, the flush-window note)
  and "Confirmation at 3b566c3".
- Contract: repo `AGENTS.md` § "Residuals — what is still only as strong as review".
- Evidence lands INSIDE the repo under `docs/evidence/VZ-FOUND-008/` (extend, delete nothing).

## Preflight (done 2026-09-20, before any edit)
| Need | Result |
|---|---|
| Node | v22.14.0 |
| npm | 10.9.2 |
| @playwright/test | 1.63.0; `npx playwright --version` → `Version 1.63.0` |
| Chromium | `chromium-1243` already cached (no new browser revision needed) |
| Docker | running (`docker info` exit 0) |
| Disk | 11 GiB free on the data volume |
| `gh` | authenticated as `yegamble` |
| Production build | `.next/BUILD_ID` present (`kTyu-DjLuc8N57638K8ww`) |
Nothing is BLOCKED.

## Runtime facts, measured against the INSTALLED 1.63.0 (not assumed)
Probe `e2e/demos/__probe.demo.ts` (temporary, deleted before commit), run through
`playwright.demos.config.ts` against the local production server:

- `browser.browserType() === playwright.chromium` → **true** (same instance).
- `chromium`, `firefox`, `webkit` share ONE prototype (`BrowserType2.prototype`);
  `browser.browserType()` has that same prototype.
- `launch`, `launchServer`, `launchPersistentContext`, `connect`, `connectOverCDP`
  are all **prototype** methods — none is an own property of the BrowserType instance.
- `Browser2.prototype` owns `newContext`, `newPage`, `contexts`; its own prototype
  (`ChannelOwner`) has none of them, so there is no second prototype hop to escape to.
- `@playwright/test` re-exports `chromium`/`firefox`/`webkit`/`_electron`/`_android`,
  and each is **identical** (`===`) to the corresponding member of the `playwright`
  test fixture. `_electron`'s prototype has `launch`; `_android`'s has
  `launchServer`, `connect`, `devices`.
- `browser.contexts()` contains the default `page.context()` during a test.

## Acceptance
1. **F12** — the three import-free routes fail the lane by name:
   `Object.getPrototypeOf(browser).newContext.call(browser)`,
   `browser.browserType().launch()`,
   `playwright.chromium.launchPersistentContext(dir)`;
   plus `connect` / `connectOverCDP`. Honest `page`/`context`/`browser` overrides
   stay green; the 18 lane tests stay green five runs in a row.
   Lint rule gains the method names as the early warning.
2. **F14** — a fourth canary fixture produces a genuine `requestfailed`; neutering
   the `requestfailed` listener turns the canary (and therefore the required `e2e`
   lane) red. All four listeners red on neutering; fault-type swap still red.
3. **Flush window** — decided with measured numbers, either a bounded settle with
   its cost and 20-run determinism, or the documented limit left in place.
4. **AGENTS.md Residuals** — every sentence true after the change; "nothing catches
   these today" removed only for what is actually closed.

Non-goals (explicitly out of this slice): artifact privacy / scheme-less URL
redaction (FINDING 13), the no-authenticated-spec rule stands unchanged; NITs from
other verifications.

## Implementation
- `e2e/harness/creation-guard.ts` (new): prototype patches installed at MODULE LOAD
  (the harness entry is imported by `playwright.config.ts`, which every worker
  evaluates before any spec file — so a spec cannot capture an un-patched original):
  - `Browser.prototype.newContext` / `newPage` — when ARMED, register the produced
    context with the active guard. Closes the prototype route by *guarding*, so even
    a context created and closed inside the body has its signals recorded.
  - `BrowserType.prototype.launch` / `launchPersistentContext` / `connect` /
    `connectOverCDP` / `launchServer`, `_electron.launch`, `_android.launchServer` /
    `connect` — when ARMED, record a violation and THROW. A swallowed throw still
    fails the test, because the violation list is asserted in teardown.
  - Unarmed (worker setup, the runner's own browser launch, an overridden worker
    `browser` fixture) → plain delegation.
- `e2e/harness/browser-errors.ts`: `guardBrowser` unchanged in its wrapping; adds
  `registerContext` (idempotent) and `unguardedContexts(browser)` for the teardown
  assertion.
- `e2e/harness/test.ts`: arm/disarm around the test; teardown asserts (a) no
  violation was recorded, (b) no live context on the harness's browser is one the
  guard never registered.
- `eslint-rules/no-unguarded-playwright-import.mjs`: refuse `.browserType(`,
  `.launch(`, `.launchPersistentContext(`, `.connect(`, `.connectOverCDP(` in
  `e2e/specs/**` and `e2e/demos/**` — the early warning, not the control.
- `e2e/demos/aborted-request.demo.ts` (new) + a fourth entry in
  `scripts/ci/harness-canary.mjs`.
- `scripts/e2e/demonstrate.sh`: D13 gains the new red halves; D12 gains the
  `requestfailed` neutering pair.
- `AGENTS.md`: Residuals rewritten to match exactly what now holds.

## Verification
| Command | Lane |
|---|---|
| `npm run ci` (lint + typecheck + vitest + build) | frontend |
| `npx playwright test` (18 tests, 2 projects) | e2e |
| `node scripts/ci/check-coverage-floor-ran.mjs` | e2e |
| `node scripts/ci/harness-canary.mjs` | e2e |
| `bash scripts/ci/check-e2e-lane.sh` | guard |
| `bash scripts/ci/require-checks_test.sh` | guard |
| `npm run e2e:demos` | demonstrations |
| GitHub `ci-required` on the head SHA | merge gate |

## Progress and evidence

### Decision on item 3 (the flush window): a bounded 250 ms settle, ADOPTED

Measured on this machine (macOS arm64, Node v22.14.0, @playwright/test 1.63.0,
Chromium 1243) against the local production server, with faults scheduled at
0 / 50 / 150 / 250 / 400 / 600 ms after the test body returns:

| Settle | Caught | Missed |
|---|---|---|
| 0 ms (the behaviour before this slice) | 0 | 50, 150, 250, 400, 600 |
| 100 ms | 0, 50 | 150, 250, 400, 600 |
| **250 ms (shipped)** | 0, 50, 150, 250 | 400, 600 |
| 400 ms | 0, 50, 150, 250, 400 | 600 |

The 0 ms row reproduces the verifier's measurement exactly (0 caught, 50 and 150
missed). Cost, on the real 18-test lane against the production server:

| Configuration | Before | After | Delta |
|---|---|---|---|
| local worker count | 3.2 s (3 runs: 3.74/3.68/3.71 s wall) | 4.4 s (4.88/4.75/5.39 s wall) | +1.2 s |
| `--workers=2` (the CI shape, 9 tests/worker) | 4.8 s | 6.9 s | +2.1 s ≈ 250 ms × 9 |

Determinism: **20 consecutive runs at `--workers=2`, every one `18 passed`,
`coverage floor: OK (9/9 9/9)`, `harness stamp: OK (18 …)`, exit 0**, 6.3–7.0 s.

**Adopted** because the window it replaces was effectively "whatever the driver
had already delivered" — a Next.js hydration effect or deferred fetch that
throws just after the last assertion was invisible — and the cost is a constant
250 ms per test on a lane that already builds a Docker image. It **widens** the
window; it does not close it. 400 ms is still missed, and D14 pins both ends so
the number in AGENTS.md cannot drift from the code.

### What ran

| Command | Exit | Result |
|---|---|---|
| `npm run ci` | 0 | 14 files / **341 tests** / 0 skipped (baseline on `main`: 13 / 316) |
| `npx playwright test` (local prod server) | 0 | 18 passed, floor OK (9/9 9/9), stamp OK (18) |
| 20× `npx playwright test --workers=2` | 0 ×20 | 18 passed every run |
| `node scripts/ci/harness-canary.mjs` | 0 | failed all **4** fixtures with the exact kind sets |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | — |
| `bash scripts/ci/require-checks_test.sh` | 0 | 102 cases / 109 assertions / 0 failed |
| `npm run e2e:demos` | 0 | see the evidence README for the half count |

### A defect my own demonstration found

The first version of the two new `check-e2e-lane.mjs` checks used
`guard.includes("armCreationGuard")`. D13q's controlled mutation removed the
CALL and left the import — and the check passed (exit 0, measured). Both now
require a call (`/armCreationGuard\s*\(/`). Noted for the chair: the
pre-existing checks in that same block (`guardBrowser`, `validatePolicy`,
`unallowedRecords`, `claimSigner`) have the same weakness, since each name also
appears on an import line. Not changed here — outside this slice — and reported
rather than silently fixed.

## Blockers and handoff
None. Nothing was BLOCKED; every command above ran.
