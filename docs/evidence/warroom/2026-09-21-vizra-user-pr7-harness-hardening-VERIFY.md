# Independent verification — yegamble/vizra-user PR #7 (VZ-FOUND-008 harness hardening)

**Verdict: FAIL** (one blocking finding — FINDING 1; F12 CLOSED, F14 CLOSED. Full verdict at the end.)

| | |
|---|---|
| PR | https://github.com/yegamble/vizra-user/pull/7 |
| Head SHA verified | `77305009a7ae5b20411134ce5497f88d824e68ce` |
| Base | `main` @ `90896beb9669a3b305269a298d507fd7a9e27aa4` |
| Branch | `fix/m0-harness-hardening` |
| Verifier | independent agent; did not write any of this code |
| Date | 2026-09-21 |

Head SHA re-confirmed with `gh api repos/yegamble/vizra-user/pulls/7` at the start of
this session and again after a machine restart: unchanged at `7730500`.

## Environment

Fresh clone, never the builder's checkout:
`/private/tmp/claude-501/-Users-yosefgamble-github-vizra/7321b930-95d2-4a95-ba2e-61ef2ce3c13c/scratchpad/verify7/repo`
(`git clone` → `git checkout 77305009a7ae5b20411134ce5497f88d824e68ce`, `git status --porcelain` empty).

| Need | Value |
|---|---|
| Platform | macOS (Darwin 25.5.0), **arm64 native** |
| Node | v22.14.0 |
| npm | 10.9.2 |
| `npx playwright --version` | Version 1.63.0 |
| Docker | server 29.8.0, running |
| Disk free at start | 36 GiB |

## 1. Counts — baseline lanes

| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | clean install from lockfile |
| `npm run ci` (lint + typecheck + vitest + build) | 0 | **14 files / 341 tests / 0 skipped**; `next build` OK |
| `npx playwright test` | 0 | **18 passed (5.5 s)**; `e2e coverage floor: OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9)`; `e2e harness stamp: OK (18 succeeding result(s) verified)` |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | floor 9/9 9/9 from the report; 18 stamps verified out-of-process |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | lane-integrity guard green |
| `bash scripts/ci/require-checks_test.sh` | 0 | **102 cases, 109 assertions, 0 failed** |
| `node scripts/ci/harness-canary.mjs` | 0 | **failed all 4** fault-injection fixtures, each with its exact kind set |

Every number the builder claimed in item 1 reproduces exactly. No skips anywhere.

The fourth canary fixture is a **genuine failed request, not an HTTP error** — recorded kind
set measured from my own run:

```
[requestfailed] requestfailed: GET http://127.0.0.1:3210/__vizra_e2e_fixture__/aborted-on-purpose.bin — net::ERR_CONNECTION_REFUSED
[console]       console.error: Failed to load resource: net::ERR_CONNECTION_REFUSED (…)
```

`[response]` is in that fixture's `forbid` list and is absent — which is the whole point:
a 404 is a completed response, so the `response` listener cannot stand in for `requestfailed`.

## 2. F12 — the three import-free routes, reproduced verbatim

Four specs written by me, placed in `e2e/specs/`, each importing **only** the
harness `test`. The fault body is the one the previous verification used: a
sub-resource that 404s **and** an uncaught exception, on every load.

A control first, because a fault body that does not bite proves nothing:

| Spec | Result |
|---|---|
| `vzr0-control` — the ordinary `page` fixture on that body | **RED**, 3 records: `[response] http 404`, `[console]`, `[pageerror] VZ-VERIFIER-UNCAUGHT-EXCEPTION` |

### Lint state before the runtime layer is exercised

`npx tsc --noEmit` exit **0** for all four specs — every attack is **type-green**.

| Spec | Route | Lint under the **shipped** config |
|---|---|---|
| `vzr1` | `Object.getPrototypeOf(browser).newContext.call(browser)` | **green** — `newContext` is not in `bannedMethods`, by design |
| `vzr2` | `browser.browserType().launch()` | RED (`browserType`, `launch`) |
| `vzr3` | `playwright.chromium.launchPersistentContext(dir)` | RED (`launchPersistentContext`) |

To isolate the **runtime** layer I wrote my own mutant config
(`eslint.mutant.config.mjs`, a copy of `eslint.config.mjs` with
`bannedMethods: []`). Under it all four specs pass ESLint, **exit 0** — the
state the previous verifier measured. Then:

| Spec | Runtime result | Guard message |
|---|---|---|
| `vzr1` | **RED** | 3 browser errors recorded — the context was **guarded**, although it was created *and closed* inside the body |
| `vzr2` | **RED** | ``vizra harness: `chromium.launch` was called during a test`` + `1 attempt(s) to create a browser or context the harness was never handed` |
| `vzr3` | **RED** | ``vizra harness: `chromium.launchPersistentContext` …`` + the same teardown assertion |

**All three routes are closed at runtime with lint forced off.** The lint ban is
the early warning, exactly as claimed.

### Attacking each layer separately

| Configuration | `vzr1` (context **closed** in body) | `vzr1b` (context left **open**) |
|---|---|---|
| both layers intact | RED (3 records) | RED (3 records) |
| **creation-time registration cut** (`active?.registerContext(...)` removed from `creation-guard.ts`) | **PASSED** — the hole the builder describes | RED: `1 context(s) the harness was never handed are open on this browser` |
| **teardown stray assertion cut** (`unguardedContexts(...)` → `[]` in `test.ts`) | RED (3 records) | RED (3 records) |

This reproduces the builder's rationale precisely: the teardown layer alone
cannot see a context created and closed inside the body, which is why the
prototype route is **guarded** rather than merely detected; and the creation
layer alone is sufficient for both shapes. Neither layer is redundant.

`vzr2s` — the refusal throw wrapped in `try { … } catch {}` — is still **RED**
via the teardown violation list. A swallowed throw does not buy a green test.

### Going past the builder: routes it does not claim to close

Each probe is a spec in `e2e/specs/` importing only the harness `test`.
"Silent" means the test **passed** on a page that 404s and throws.

| Probe | Lint (shipped) | Type | Runtime | Verdict |
|---|---|---|---|---|
| `page.context().browser()?.browserType().launch()` | RED | green | refused (`chromium.launch`) | **REFUSED** |
| worker fixture: `playwright.chromium.launch()` via `test.extend(..., {scope:"worker"})` | RED | green | refused | **REFUSED** |
| `playwright._electron.launch()` | RED | green | refused | **REFUSED** |
| `browser._innerNewContext.call(browser)` (private internal) | **green** | **green** | not patched | **SILENT** — disclosed in AGENTS.md |
| `browser.newBrowserCDPSession()` → `Target.createTarget` | **green** | **green** | not patched, target invisible to `browser.contexts()` (measured `before=1 after=1`) | **SILENT** — *not* disclosed |
| **a page opened and navigated in `test.beforeAll`** | **green** | **green** | not observed | **SILENT** — *not* disclosed (see FINDING 1) |
| out-of-tree spec `e2e/other/*.spec.ts` importing the harness | green | green | **not collected** by the lane (0 tests) | closed by `testDir` |

Worth recording: the worker-fixture route being **refused** is stronger than I
expected — Playwright resolves the auto fixture (which arms the guard) before
the test-function's worker fixture, so the launch happens while armed.

The `beforeAll` probe is the one that matters. Its own
`browser-signals.json` attachment, from my run:

```json
{ "contextsGuarded": 2, "contextsUnguarded": 0, "creationViolations": [], "records": [] }
```

The context **was** registered and **was not** a stray — so every control in
this PR reports success — yet the guard recorded **nothing**, because the page
had already 404'd and thrown before the per-test fixture attached its
listeners. The identical spec that navigates *again* in the body
(`p1c`) is **RED** with all three records, which proves the fault body works and
isolates the cause to *when* the listeners attach.

## 3. Honest use stays green — no false positives

Four legitimate shapes, healthy pages, run under the shipped config:

| Shape | Result | `contextsGuarded` / `unguarded` / `records` |
|---|---|---|
| overridden `context` fixture for locale `en-GB` + viewport | **PASS** | 1 / 0 / 0 |
| `browser.newContext()` in the body for a second signed-out user | **PASS** | 2 / 0 / 0 |
| a context created with a **`storageState`** option | **PASS** | 2 / 0 / 0 |
| a context created with **`recordVideo`** (video file produced) | **PASS** | 2 / 0 / 0 |

The creation guard breaks neither `storageState` nor `recordVideo`, and every
honestly-created context is guarded rather than merely tolerated.

**Stability.** The real 18-test lane, `--workers=2`:

- 10 consecutive runs, idle machine: **10/10 `18 passed`**, floor 9/9 9/9, 18 stamps, 6.9–7.0 s.
- 10 consecutive runs under **full 8-core CPU contention** (8 × `yes > /dev/null`, stopped afterwards by exact PID): **10/10 `18 passed`**, 18 stamps, 9.1–10.1 s.

20/20 deterministic. The fixed 250 ms sleep introduces no flake under load.

## 4. F14 — the fourth canary kind

Baseline: `node scripts/ci/harness-canary.mjs` exit **0**, all four fixtures
failed with their exact kind sets.

Neutering each listener in `e2e/harness/browser-errors.ts`, one at a time
(commenting out the `context.on(...)` line), restoring between each:

| Listener neutered | Canary | Named by |
|---|---|---|
| `console` | **exit 1** | `console-error.demo.ts … PASSED` |
| `weberror` | **exit 1** | `uncaught-exception.demo.ts … PASSED` |
| `requestfailed` | **exit 1** | `aborted-request.demo.ts … did not fail for its own reason: … "[requestfailed]"` |
| `response` | **exit 1** | `failed-request.demo.ts … did not fail for its own reason: … "http 404"` |

Restored → canary exit **0** again. **All four guarded kinds are now covered**;
before this slice `requestfailed` left the canary green.

Fault-type swaps, each caught by *both* halves of the kind assertion:

| Swap | Canary |
|---|---|
| `aborted-request`: `route.abort("connectionrefused")` → `route.fulfill({status:404})` | **exit 1** — missing `[requestfailed]` **and** "failed for the WRONG reason: the guard recorded `[response]`" |
| `uncaught-exception`: `throw` → `console.error` | **exit 1** — missing `[pageerror]` **and** "recorded `[console]`" |

The new fixture is a **genuine failed request**, not an HTTP error — see §1.

**F14: CLOSED.**

## 5. The 250 ms settle

My own six-delay probe (`e2e/demos/vz-window.demo.ts`, written by me, removed
after), faults scheduled 0 / 50 / 150 / 250 / 400 / 600 ms after the body returns:

| Settle | Caught (test RED) | Missed (test GREEN) |
|---|---|---|
| **250 ms (shipped)** | 0, 50, 150, 250 | 400, 600 |
| 0 ms (`SETTLE_MS` forced to 0) | 0 | 50, 150, 250, 400, 600 |

Both rows reproduce the AGENTS.md table **exactly**, including the previous
verifier's 0 ms measurement.

**Cost**, real 18-test lane at `--workers=2` on this machine:

| `SETTLE_MS` | Wall |
|---|---|
| 0 | 4.5 / 4.5 / 4.6 s |
| 250 (shipped) | 6.9–7.0 s (10 runs) |

≈ +2.4 s ≈ 250 ms × 9 tests per worker. The builder reported 4.8 s → 6.9 s;
mine is 4.5 s → 7.0 s. Same shape, same mechanism, ordinary machine variance —
the claim is honest.

**Can the settle HIDE something it used to catch?** Two probes:

| Probe | Result |
|---|---|
| throw at 50 ms, **page closed** at 120 ms (inside the settle) | **RED** — `[pageerror]` recorded |
| throw at 50 ms, **whole context closed** at 120 ms | **RED** — `[pageerror]` recorded |

Records are pushed by the listener at the moment of the event, so closing the
page or context during the settle destroys nothing. A test-timeout landing in
teardown fails the test either way (fails closed). No hiding found.

## 6. The builder's own reported defect — `includes()` in `check-e2e-lane.mjs`

Reproduced for `guardBrowser` (`scripts/ci/check-e2e-lane.mjs:440`). Mutation:
keep the import, replace `const guard = guardBrowser(browser);` in
`e2e/harness/test.ts` with an inert guard object and `void guardBrowser;`.

| Check | Result |
|---|---|
| `npx tsc --noEmit` | exit 0 |
| `bash scripts/ci/check-e2e-lane.sh` | **exit 0 — the weakness is real** |
| `npx playwright test --workers=2` | **exit 0, `18 passed` — the lane itself is a false green** |
| `node scripts/ci/harness-canary.mjs` | **exit 1 — all 4 fixtures PASSED**, i.e. caught |

So the weak check is real and the lane alone would not catch a fully neutered
guard — but the **canary does**, and the canary is a step in the required `e2e`
lane. The two checks this PR *added* (`check-e2e-lane.mjs:470,479`) already use
the call-requiring form `/armCreationGuard\s*\(/`; only the four pre-existing
ones are weak. Ruling in FINDING 3.

## 7. Regression canaries for the earlier findings

| Earlier finding | Mutation | Result |
|---|---|---|
| import bypass | `import * as pw from "@playwright/test"` | lint **RED** |
| import bypass | `require("playwright/test")` | lint **RED** |
| inline suppression | `/* eslint-disable vizra/no-unguarded-playwright-import */` | lint **RED** (`noInlineConfig`) |
| inline suppression | `// eslint-disable-next-line …` | lint **RED** |
| out-of-tree spec | `e2e/other/m3a.spec.ts` importing `@playwright/test` | lint **RED** |
| out-of-tree spec | `e2e/other/m3b.spec.ts` importing the harness | lint green, but **`playwright test --list` collects 0** from `e2e/other` |
| fixture override | `test.extend({ vizraHarnessGuard: … })` | lint **RED** |
| fixture override | `test.extend({ ...extra })` (unreadable) | lint **RED** (fails closed) |
| lane guard | `guardBrowser` call removed, import kept | lane guard **exit 0** (FINDING 3); canary **exit 1** |
| lane guard | `stamp-reporter` line deleted from `playwright.config.ts` | lane guard **exit 1** |
| floor | filtered run (`--grep`) | lane **RED** — filter detection fires independently of the numbers |
| floor | both project floors lowered 9 → 1 | no script refuses it (by design: CODEOWNERS-reviewed file, stated as such in `required-projects.json`) |
| redactor | 404 sub-resource with `?sig=SECRET_SIGNATURE_VALUE&exp=99` | record reads `…/x.bin?<redacted:…`; **`SECRET_SIGNATURE_VALUE` appears 0 times** in the output |

### Stamp-forge attempts (5)

| Attempt | Result |
|---|---|
| read `VIZRA_E2E_STAMP_KEY` from `process.env` in a spec | **absent** (deleted at config load) |
| a child process spawned by a spec inherits the key | **absent** |
| recover the key from the test's own stamp annotation | not recoverable; stamp is a signature |
| push a duplicate stamp annotation | allowed, but it is the same valid stamp for the same test — no bypass |
| read `.vizra-e2e/stamp-key.json` from disk mid-run | **readable (123 bytes)** — but it holds the **previous** run's key; the key **rotates every run** (verified across 3 runs), the file is gitignored, no workflow caches or uploads it, so in CI it does not exist at all on the first run. Forging fails. Doc nit → FINDING 4 |

### Key hygiene and weakening

- Per-run key (64 hex chars) appears in **0** files under `playwright-report/`, `test-results/`, and 0 of the lane/canary logs.
- `git diff --numstat` over every `*.test.ts`, `*.test.mjs`, `e2e/specs/**`, `e2e/demos/**`, `eslint-rules/**`: **every file is +N/−0**.
- `git diff --diff-filter=D`: **no file deleted anywhere in the PR**.
- `d12-requestfailed-listener-neutered-GREEN.txt` is **kept** (unchanged from `main`) and the new red half `d12d-requestfailed-listener-neutered-RED.txt` is added — exactly as the builder claimed.
- No `.skip` / `.only` / `.fixme` anywhere in the tree.

## 8. CI on `7730500`

All **8** check-runs `completed` / `success`; none skipped, cancelled or timed out:

```
ci-required  success  01:32:48 → 01:36:00
contract     success  01:32:48 → 01:33:17
deps-scan    success  01:32:48 → 01:33:16
e2e          success  01:32:51 → 01:35:17
frontend     success  01:32:47 → 01:33:49
guard        success  01:32:48 → 01:33:29
image-scan   success  01:32:47 → 01:34:27
GitGuardian  success  01:32:44 → 01:32:45
```

`ci-required` finished **after** `e2e` — it waited for it.

Manifest (`.github/required-checks.txt`) vs what ran: `frontend` ✓, `contract` ✓,
`?guard` ✓, `e2e` ✓. `?docker-build` did **not** run; it is `?`-optional and
path-filtered, and this PR touches no Dockerfile path — and the `e2e` lane
builds the image itself (`docker build --tag vizra-user:e2e .` present in the
log), so the Dockerfile is exercised regardless. **No listed-but-unexecuted
required lane.**

The `e2e` job log (1035 lines) carries, from the container run:

```
18 passed
coverage floor: OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9)
harness stamp: OK (18 succeeding result(s) …
OK: the browser lane satisfied its coverage floor from the report (…9/9 …9/9).
OK: the harness canary failed all 4 fault-injection fixtures, each with the exact
    set of record kinds it demonstrates and no others — one per guarded kind
    ([console] / [response]+http 404 / [pageerror] / [requestfailed]).
```

## 9. `npm run e2e:demos`

`env -u E2E_BASE_URL npm run e2e:demos` → exit **0**:
`halves passed: 104, halves blocked: 0, halves failed: 0` (D13 contributes 23
halves, D14 contributes 2), ending `OK: every demonstration that ran went red on
the mutation and green on restore.` The builder's count reproduces exactly.

The builder's accompanying claim "tree clean afterwards" does **not** reproduce:
the run rewrites **95** transcripts under `docs/evidence/VZ-FOUND-008/`. I
classified every modified line — all of it is absolute-path, wall-clock and
record-ordering noise (13 files differ by more than path/timing, and in each
case it is a `Start at HH:MM:SS`, a `test-failed-1.png` vs `-2.png`, or the
arrival order of the same `[pageerror]` record). **No demonstration changed its
red/green verdict.** The claim is best read as "I committed the regenerated
transcripts"; it cannot be used as a check, because the transcripts embed the
checkout's absolute path. NIT, recorded in FINDING 5.

## Findings

```
FINDING 1: the guard sees nothing a page does before the per-test fixture attaches —
           a spec that navigates in `test.beforeAll` passes on a broken page
Severity:    REQUIRED  (blocking for this PR's acceptance item 4)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/test.ts:142-191 (the `vizraHarnessGuard` auto fixture, test-scoped)
             e2e/harness/browser-errors.ts:266 (`for (const context of browser.contexts()) guardContext(context)`)
             e2e/harness/creation-guard.ts:69 ("not from `beforeAll`")
             AGENTS.md:205-212 ("over every page the test creates … whichever page produced it")
             AGENTS.md:620-746 (§ Residuals — rewritten by this PR, does not name this)
  requirements: VZ-FOUND-008

Observed:
  A spec in `e2e/specs/` importing ONLY the harness `test`:

      let shared: import("@playwright/test").Page;
      test.beforeAll(async ({ browser }) => {
        shared = await browser.newPage();
        await makeBroken(shared);              // 404 sub-resource + uncaught throw
        await shared.goto(`${BASE}/`);
      });
      test("…", async () => {
        await expect(shared.getByRole("heading", { level: 1, name: "Vizra" })).toBeVisible();
      });

  `npx tsc --noEmit` exit 0. `npx eslint` under the SHIPPED config: 0 errors.
  `npx playwright test` → **1 passed**. The fixture's own attachment:

      { "contextsGuarded": 2, "contextsUnguarded": 0,
        "creationViolations": [], "records": [] }

  The identical spec that navigates AGAIN inside the body is RED with all three
  records, so the fault body is sound; the difference is only WHEN the listeners
  attach. The `beforeAll` context is swept and registered by `guardBrowser`'s
  existing-contexts loop, so it is neither a stray nor a violation — every
  control this PR adds reports success.

Failure:
  The harness guarantee the war room relies on is "a test that passes ran under
  the guard". Here the test ran under the guard and the guard observed nothing,
  because everything the page did happened before the test-scoped fixture set
  up. `test.beforeAll(async ({ browser }) => { page = await browser.newPage() })`
  is the idiom Playwright's own documentation uses for sharing a page across
  tests; nobody writing it is trying to evade anything. A later UI slice that
  uses it gets a green lane, a valid stamp, a satisfied coverage floor and an
  out-of-process check that agrees — on a page that 404s and throws. That is
  the exact defect class this harness has been failed for four times.

  AGENTS.md compounds it in two directions. § "The browser lane" says the guard
  fails a test on any such signal "whether or not the test body looked, and
  whichever page produced it" — unqualified, and not true here. And
  `creation-guard.ts:69` says a spec cannot hold an unpatched Browser prototype
  "not from `beforeAll`", which is true about the PROTOTYPE and reads as
  reassurance about `beforeAll` generally.

Perspective: developer (every later UI slice's author and reviewer)

Recommendation:
  Smallest coherent fix, either one:
  (a) CONTRACT ONLY — add a Residuals bullet stating the early edge of the
      window, symmetrically with the flush bullet's late edge: "the guard
      attaches when the per-test fixture sets up; anything a page does in
      `beforeAll`/`beforeEach` before that is not observed", and qualify the
      "whichever page produced it" sentence. Cheapest, honest, in scope.
  (b) CONTRACT + CONTROL — additionally make the teardown assert that no page
      on a guarded context has a non-`about:blank` URL whose load the guard
      never saw, or refuse `Browser.prototype.newPage`/`newContext` while
      unarmed outside worker setup. This needs its own demonstrations and is
      arguably the next slice, not this one.

Acceptance criteria:
  - A demonstration half (D13-style) that pins the current behaviour: the
    `beforeAll` spec above either FAILS (if (b)), or PASSES with the AGENTS.md
    bullet naming it as a documented limit (if (a)) and goes red if that bullet
    stops matching the code.
  - No sentence in AGENTS.md asserts coverage of a page navigated in a hook.

Tests:
  `e2e/demos/` — a `before-all-fault.demo.ts` in the same shape as
  `late-fault.demo.ts`, which pins the early edge exactly as D14 pins the late
  edge. The harness to run it already exists.

Cross-repo implications:
  core: none | user: as above | search: none | meta: the ledger note for
  VZ-FOUND-008 must not claim hook-time coverage.

Challenge:
  This hole is PRE-EXISTING — it is not introduced by this PR, and blocking a
  net improvement over it delays a strictly better harness. The counter is that
  this PR's own acceptance item 4 is "AGENTS.md Residuals — every sentence true
  after the change", the Residuals section was rewritten here and declares
  itself route-by-route, and remedy (a) is a few lines of prose.
```

```
FINDING 2: `browser.newBrowserCDPSession()` reaches a page no control can see,
           and is named nowhere
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/creation-guard.ts:214-220 (REFUSED_BROWSER_TYPE_METHODS)
             eslint-rules/no-unguarded-playwright-import.mjs:100-107 (BANNED_METHODS)
             AGENTS.md:646-655 (the route table)
  requirements: VZ-FOUND-008

Observed:
  From a spec importing only the harness `test`:
      const session = await browser.newBrowserCDPSession();
      await session.send("Target.createTarget", { url: `${BASE}${MISSING}` });
  `tsc` exit 0; `eslint` under the shipped config: 0 errors; the test PASSES.
  Measured in the same spec: `browser.contexts().length` is 1 before and 1
  after, so the created target is in no Playwright context — neither the guard's
  listeners nor `unguardedContexts()` can ever see it. `grep -rn
  newBrowserCDPSession` over the repository returns no hit: it is in neither
  ban list nor in the Residuals table.

Failure:
  The Residuals table presents itself as the route-by-route statement of what
  produces "a context or browser the harness was never handed". This route is
  lint-green, type-green and silent, and is absent from it.

Perspective: developer

Recommendation:
  Add `newBrowserCDPSession` to the lint `bannedMethods` and refuse it at
  runtime alongside the BrowserType methods (it is a `Browser.prototype`
  method, patched in the same place as `newContext`/`newPage`) — or, if that is
  judged out of scope, add one row to the Residuals table saying it is open.

Acceptance criteria:
  Either a spec calling `browser.newBrowserCDPSession()` fails with the named
  refusal, or AGENTS.md's table lists it as open with the reason.

Tests:
  `e2e/harness/creation-guard.test.ts` — one case, in the idiom of the existing
  `launchServer` / `_electron` cases.

Cross-repo implications: core: none | user: as above | search: none | meta: none

Challenge:
  A CDP-created target is not a Playwright `Page`, so no honest test can assert
  against it — the practical exploitability is near zero, and this may be noise
  in a table that is already long.
```

```
FINDING 3: the four pre-existing `includes()` name checks in check-e2e-lane.mjs
           pass with the CALL removed and the import left
Severity:    SHOULD  (next slice, not this one)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-e2e-lane.mjs:429 (validatePolicy), :430 (unallowedRecords),
             :433 (claimSigner / STAMP_ANNOTATION), :440 (guardBrowser)
  requirements: VZ-FOUND-008

Observed:
  Reported by the builder itself rather than hidden. Reproduced for
  `guardBrowser`: keep the import in `e2e/harness/test.ts`, replace
  `const guard = guardBrowser(browser);` with an inert guard object plus
  `void guardBrowser;`. Then `npx tsc --noEmit` exit 0,
  `bash scripts/ci/check-e2e-lane.sh` **exit 0**, and
  `npx playwright test --workers=2` **exit 0, `18 passed`** with the guard
  entirely inert. `node scripts/ci/harness-canary.mjs` **exit 1** — all four
  fixtures PASSED — so the required `e2e` lane still goes red.
  The two checks this PR ADDS (:470 `armCreationGuard\s*\(`, :479
  `unguardedContexts\s*\(`) already require a call and are not affected.

Failure:
  The lane guard advertises itself as "the cheap early warning for an outright
  deletion" and would miss a deletion that leaves the identifier on an import
  line. It is not a false green at the gate, because the canary catches it.

Perspective: developer

Recommendation:
  Change the four to the call-requiring form the builder already used, e.g.
  `/guardBrowser\s*\(/`. Four one-line edits plus a demonstration half.

Acceptance criteria:
  With the call removed and the import kept, `check-e2e-lane.sh` exits non-zero
  and names the symbol, for each of the four.

Tests:
  `scripts/ci/require-checks_test.sh` (102 cases today) gains four cases.

Cross-repo implications: core: none | user: as above | search: none | meta: none

Challenge:
  It should NOT block this PR: the weakness is pre-existing and unchanged here,
  the builder disclosed it rather than silently fixing a gate file mid-slice
  (which AGENTS.md discourages), and the canary — strengthened to all four
  kinds in this very PR — is the control that actually catches a neutered
  guard.
```

```
FINDING 4: stamp.ts overstates the key file's unreadability
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/stamp.ts:42-45
  requirements: VZ-FOUND-008

Observed:
  The comment says the reporter writes `.vizra-e2e/stamp-key.json` "only in
  `onEnd` … so the out-of-process check can verify while no running spec can
  read it." A spec CAN read it: mine did, mid-run, 123 bytes. What it gets is
  the PREVIOUS run's key — the key rotates every run (verified across three
  consecutive runs), the file is gitignored, no workflow caches or uploads it,
  and on a fresh CI checkout it does not exist at all. Forging therefore fails.

Failure:
  The security property holds; the sentence as written does not. File not
  touched by this PR.

Perspective: developer
Recommendation: reword to "no running spec can read THIS RUN'S key".
Acceptance criteria: the sentence matches the measured behaviour.
Tests: none needed.
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge: pure prose; arguably below the noise floor.
```

```
FINDING 5: the demo transcripts are not reproducible across checkouts, so
           "tree clean afterwards" is not a usable check
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/e2e/demonstrate.sh, docs/evidence/VZ-FOUND-008/*.txt
  requirements: VZ-FOUND-008

Observed:
  `npm run e2e:demos` exit 0, 104/104 halves — and 95 transcripts modified
  afterwards. Every modified line is absolute-path, wall-clock or
  record-ordering noise; no verdict changed.

Failure:
  A verifier cannot use `git status` after the demos as a check, and the
  transcripts embed the builder's home directory.

Perspective: developer
Recommendation: normalise the checkout path and elapsed times when writing a transcript.
Acceptance criteria: two runs from two different checkouts produce byte-identical transcripts.
Tests: run the suite twice from different paths and diff.
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge: cosmetic; the demonstrations themselves are sound and self-asserting.
```

## Residuals, split as the chair asked

**Accepted by design — reachable only by editing a reviewed gate file, or only
by deliberately reaching for a private internal.**

| Residual | Why it is accepted |
|---|---|
| `e2e/harness/**`, `playwright.config.ts`, `eslint-rules/**`, `.github/**`, `scripts/ci/**` can weaken the guard | `.github/CODEOWNERS` paths; and the canary makes a neutered listener a named `e2e` failure — I verified the fully-inert-guard mutation is caught by the canary |
| the coverage floor numbers in `required-projects.json` can be lowered | CODEOWNERS file that says so in its own `$comment`; no script refuses it, by design; the *filtered-run* detection still fires independently, verified |
| `playwright._connection`, `BrowserType.prototype._connect`, `browser._innerNewContext` | disclosed in AGENTS.md; I confirmed `_innerNewContext` is reachable lint-green and type-green via `as unknown as { … }` — no `@ts-expect-error`, no `as any` — but writing it is a deliberate reach for an underscore-prefixed client channel, not an idiom anyone produces innocently |
| `browser[name]()` with a variable key | disclosed; lint cannot read it, the runtime prototype patch catches it whatever the spelling |
| the `request` fixture (`APIRequestContext`) | disclosed; not a browser signal |
| the flush window's LATE edge (400 ms+) | disclosed, measured, and pinned from both ends by D14 |

**Real holes — reachable from an honest-looking, lint-green, type-green spec
under `e2e/specs/`.**

| Hole | Finding |
|---|---|
| a page opened and navigated in `test.beforeAll` (or any hook before the test-scoped fixture) is never observed; the test passes on a page that 404s and throws | **FINDING 1** — the only one I would call blocking |
| `browser.newBrowserCDPSession()` → a target in no Playwright context | FINDING 2 — lint-green and type-green, but not drivable by an honest test, so low practical risk |

## Verdict

**FAIL** — narrowly, and on one ground only.

- **F12: CLOSED.** All three import-free routes reproduce as RED at runtime with
  the lint ban forced off, by my own mutant config; each layer was cut
  separately and behaves exactly as the builder describes; the swallowed-throw
  case still fails; honest overrides, `storageState` and `recordVideo` all stay
  green and guarded; 20/20 deterministic lane runs including 10 under full CPU
  contention.
- **F14: CLOSED.** All four listeners now turn the canary red by name —
  including `requestfailed`, which was silent before this slice — and both
  fault-type swaps are caught by both halves of the kind assertion. The new
  fixture is a genuine failed request, not an HTTP error.
- **Flush window:** the 250 ms table reproduces exactly, in both directions, as
  does the 0 ms "before" row; the cost is as claimed; nothing is hidden by the
  settle; no flake under load.
- **CI on `7730500`:** all 8 check-runs success, nothing skipped or cancelled,
  `ci-required` waited for `e2e`, the manifest matches what ran, and the `e2e`
  log carries the floor, the 18 stamps and the four-fixture canary line.
- **No weakening anywhere:** every test/spec/demo/rule file is +N/−0, no file
  deleted, no skips, the old green transcript kept, per-run key absent from
  every report, artifact and log.

The FAIL is **acceptance item 4** — "AGENTS.md Residuals: every sentence true
after the change". Everything written there is true, but the section was
rewritten in this PR, declares itself route-by-route, and omits a route I
measured: a page navigated in `test.beforeAll` is not observed at all, and the
headline sentence "whichever page produced it" is unqualified. That is a silent
false green reachable from a textbook Playwright idiom with no lint error and no
type error — the defect class this harness has been failed for four times, and
the harness decides whether every later UI slice is VERIFIED.

**The code in this PR needs no change to reach PASS.** The minimum remedy is
FINDING 1 recommendation (a): a Residuals bullet naming the early edge of the
window symmetrically with the late edge the flush bullet already states
honestly, plus qualifying the one unqualified sentence. FINDINGS 2–5 are not
blocking and are named for the chair's scheduling.

### Reproductions

Every mutation above was applied in a throwaway clone at
`/private/tmp/claude-501/-Users-yosefgamble-github-vizra/7321b930-95d2-4a95-ba2e-61ef2ce3c13c/scratchpad/verify7/repo`
and restored; `git status --porcelain` is empty at the end of this verification.
The FINDING 1 reproduction is the spec quoted in that finding: drop it in
`e2e/specs/`, start the production server, and run
`npx playwright test --project=desktop-chromium-1440 <file>` — it passes.
