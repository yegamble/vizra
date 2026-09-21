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
(appended below as it happens)

## Blockers and handoff
(none yet)
