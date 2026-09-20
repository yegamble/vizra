# Execution plan: VZ-FOUND-008 — browser test environment against the production build

## Context
- **Repo / checkout:** `yegamble/vizra-user` at `/Users/yosefgamble/github/vizra/vizra-user`.
- **Base commit:** `1a952b5` on `main` ("chore: M0 hardening — server-only boundary,
  digest-pinned image + scan lanes, non-local `$ref` guard, computed-member fetch,
  blank FLOOR (#2)"), clean tree at start.
- **Branch:** `feat/m0-browser-env`.
- **Issue:** `yegamble/vizra#1` (VZ-ISSUE-001). Ledger ID **VZ-FOUND-008**
  (`docs/quality/features.json`), acceptance bullet: *"Browser-test environment
  (VZ-FOUND-008): the Playwright harness runs in CI against the production build
  image on desktop and mobile projects, and a console or network error fails the
  lane (demonstrated)"*.
- **Design references:** meta `AGENTS.md` "Required workflow" step 4;
  `docs/adr/ADR-009-acceptance-platform-fixtures-budgets.md` (acceptance platform
  = GitHub-hosted `ubuntu-24.04` / linux-amd64; the browser environment is
  `vizra-user` PR2 of VZ-ISSUE-001 — it is this repository's **PR3** because a
  hardening PR landed between); `docs/DESIGN_BRIEF.md` line 11 (390 px and
  1440 px review viewports); `docs/plans/2026-09-15-prompt01-architecture.md`
  item 4 (exact scope); `docs/adr/ADR-002` (CI fan-in, required-check manifest,
  floor).
- **ADR-001 pins no browser tooling.** ADR-001 was grepped for `playwright`,
  `browser`, `e2e` — no match. A version is therefore pinned here and recorded
  below.

## Acceptance
Deliver exactly item 4 of the Prompt-01 PR sequence.

1. A Playwright harness that drives the **production build** — the built Docker
   image in CI, the standalone server locally. `next dev` is never a valid target.
2. A desktop project at **1440 px** and a mobile project at **390 px**
   (ADR-009 / DESIGN_BRIEF).
3. Capture of **console errors, page errors, failed requests and HTTP ≥ 400
   responses**; each fails the test unless explicitly allow-listed per test with
   a written reason.
4. **Traces, screenshots and the HTML report** preserved as CI artifacts on failure.
5. A **first real journey** against what exists today (the home placeholder and
   `/health`) at both projects.
6. An **`e2e` lane** on `pull_request` and `merge_group` against the built image,
   added to `.github/required-checks.txt` **and** to the floor in
   `scripts/ci/check-required-floor.sh` (owner-reviewed — stated in the PR body).
7. `npm run e2e` documented in this repository's `AGENTS.md`.

### Required demonstrations (red then green, transcripts kept in the repo)
| # | Demonstration |
|---|---|
| D1 | a page that logs `console.error` fails the lane |
| D2 | a page that requests a resource returning 404/500 fails the lane |
| D3 | an uncaught exception in the page fails the lane |
| D4 | the lane fails when ZERO tests are collected, or when a project is missing |
| D5 | the lane fails when pointed at a dev server instead of the production build |

### Non-goals (explicit)
Design tokens, app shell, icon registry, any product page; visual baselines
(`toHaveScreenshot` is not used — approving baselines is reviewed separately);
an accessibility engine (VZ-A11Y-001 is M1 — the seam is documented, not filled);
re-vendoring the contract; Firefox/WebKit projects.

## Implementation
No migrations, no OpenAPI operations, no UI controls. Files:

| Path | Role |
|---|---|
| `playwright.config.ts` | the lane: two projects, `testMatch **/*.spec.ts`, artifacts, `webServer` for local runs |
| `playwright.demos.config.ts` | the demonstrations: same base, `testMatch **/*.demo.ts` — never collected by the lane |
| `e2e/harness/browser-errors.ts` | the guard: console/page/request/response collection + per-test allow-list with a mandatory reason |
| `e2e/harness/production-build.ts` | five independent production-build markers |
| `e2e/harness/test.ts` | the extended `test` every spec must import |
| `e2e/harness/coverage-reporter.ts` | the floor: required projects must exist AND each must run ≥ 1 non-skipped test |
| `e2e/harness/required-projects.ts` | the required project names (owner-reviewed via CODEOWNERS) |
| `e2e/specs/home.spec.ts`, `e2e/specs/health.spec.ts` | the first real journey |
| `e2e/specs/production-build.spec.ts` | asserts the target is a production build |
| `e2e/demos/*.demo.ts` | D1–D3 fault injections |
| `scripts/e2e/serve-production.mjs` | local production server (standalone output, exactly as the image runs it) |
| `scripts/e2e/demonstrate.sh` | runs D1–D5 red and green and writes transcripts |
| `scripts/ci/check-no-test-fixtures-in-image.sh` | proves no harness file or fixture token is in the shipped image |
| `.github/workflows/e2e.yml` | the `e2e` lane |

### Pins (verified, with where)
| Thing | Pin | Verified |
|---|---|---|
| `@playwright/test` | `1.63.0` (exact, no range) | `npm view @playwright/test dist-tags` → `latest: 1.63.0`, 2026-09-20 |
| Chromium build | `chromium-1243` / `chromium_headless_shell-1243` | `npx playwright install chromium` output, 2026-09-20 |
| ffmpeg (bundled) | `ffmpeg-1011` | same |

### Production-build markers (measured, not assumed)
Measured on 2026-09-20 by serving the same commit two ways and diffing:
`next start` on :3100 vs `next dev` on :3101 (Next 16.3.5, Turbopack).

| Marker | production | development |
|---|---|---|
| RSC flight build id (`"b"` in `self.__next_f`) | `qOH9pGJV11s0_G5FluuOi` | `"development"` |
| dev client bundles requested (`hmr-client`, `next-devtools`, `polyfill-nomodule`) | none | present |
| WebSocket opened by the page | none | HMR socket |
| `<nextjs-portal>` in the DOM | absent | present |
| `cache-control` on `/_next/static/**` | `public, max-age=31536000, immutable` | `no-cache, must-revalidate` |

All five are asserted; any one failing fails the spec.

### Why the D1–D3 fixtures cannot ship
They are **not app routes**. Each is a `page.addInitScript` injection written in
`e2e/demos/*.demo.ts`, evaluated in the browser against the real production
server. There is no file under `app/` and no route to delete. Three independent
guarantees are asserted rather than claimed:
1. the fixture token `__vizra_e2e_fixture__` appears only under `e2e/` in the tree;
2. `.dockerignore` excludes `e2e`, `playwright*.config.ts`, `scripts/e2e`;
3. `scripts/ci/check-no-test-fixtures-in-image.sh` greps the **built image's**
   filesystem for harness paths and for the token, and fails if either is found.

## Verification
| Command | Where |
|---|---|
| `npm run lint` / `typecheck` / `test` / `build` (= `npm run ci`) | local + `frontend` lane |
| `npm run e2e` | local (standalone server) + `e2e` lane (built image) |
| `bash scripts/e2e/demonstrate.sh` | local — writes D1–D5 red/green transcripts |
| `bash scripts/ci/require-checks_test.sh` | local + `guard` lane |
| `bash scripts/ci/check-required-floor.sh` | local + `guard` lane |
| `bash scripts/ci/check-no-test-fixtures-in-image.sh` | `e2e` lane (needs a built image) |

Evidence lands in **`docs/evidence/VZ-FOUND-008/`** inside this repository so it
travels with the PR.

## Progress and evidence

### Preflight (2026-09-20, before any code)
| Thing | Result |
|---|---|
| Node | v22.14.0 (matches `.nvmrc`) |
| npm | 10.9.2 |
| Docker | 29.8.0, server aarch64 — available |
| gh | 2.98.0 |
| shellcheck | present (`ci-guard` needs it) |
| Host | Darwin arm64, ~15 GiB free at start |
| ADR-001 Playwright pin | **none** — grepped for `playwright`/`browser`/`e2e`, no match; pinned here instead |

Nothing was BLOCKED. The acceptance platform (linux/amd64 on `ubuntu-24.04`)
cannot be exercised on this machine and is covered by the `e2e` lane in CI.

### Measurements that decided the design
1. **Production vs development markers** (the table under *Implementation*).
   `next start` warns that it "does not work with `output: standalone`", so the
   local server is `node .next/standalone/server.js`, assembled exactly as the
   Dockerfile's runner stage assembles it (`scripts/e2e/serve-production.mjs`).
2. **The build id is only readable from the server's response body.** After
   hydration `self.__next_f` is drained to `[]` and the inline flight scripts
   are gone from the DOM, and the payload arrives backslash-escaped inside a
   `<script>` string. Reading it from the live page silently returned nothing —
   the marker would have degraded to "could not check". It is read from the
   main-frame response body, unescaped first.
3. **`next dev` rewrites the checked-in `AGENTS.md`.** Observed: starting the
   dev server appended a ten-line `nextjs-agent-rules` block to the engineering
   contract as an uncommitted change. `next.config.ts` now sets
   `agentRules: false`.
4. **The harness was copying query strings into committed evidence.** Found by
   the repository's secret scanner on the first push, which flagged
   `ws://…/_next/hmr?id=rnklgYoLPML1LsOv4G3D9` in the D5 transcript. The value
   was an ephemeral Next HMR id, but the shape was right: the harness copied
   opaque query-string values out of a page into failure messages, CI logs and
   committed files, and the next one would be a signed media URL.
   `e2e/harness/redact.ts` now strips query and fragment at capture, keeping
   origin and path; `e2e/harness/redact.test.ts` pins it (9 cases, including
   the triggering value). All transcripts were regenerated.
5. **A two-entry allow-list silently collapsed.** Playwright 1.63.0 parses a
   `test.use` value that is an array of exactly two objects as a
   `[value, options]` fixture tuple, so the second entry vanished. The policy is
   therefore an object (`{ allow: [...] }`), and `validatePolicy` rejects a bare
   array by name. Pinned in vitest (`e2e/harness/browser-errors.test.ts`).

### Commands run (local, 2026-09-20, branch `feat/m0-browser-env`)
| Command | Exit | Result |
|---|---|---|
| `npm run lint` | 0 | clean, no warnings |
| `npm run typecheck` | 0 | clean |
| `npm run test` | 0 | 8 files, **177 tests passed**, 0 skipped |
| `npm run build` | 0 | production build |
| `npm run ci` | 0 | the whole gate |
| `npm run check:contract` | 0 | vendored contract unchanged by this PR |
| `npm run e2e` (local standalone server) | 0 | **18 tests passed**, 9 per project, coverage floor OK |
| `npm run e2e` (against the **built image**, arm64) | 0 | 18 passed — `docs/evidence/VZ-FOUND-008/lane-against-built-image-local.txt` |
| `npm run e2e:demos` | 0 | **18 halves passed, 0 blocked, 0 failed** |
| `bash scripts/ci/require-checks_test.sh` | 0 | 73 cases, 80 assertions, 0 failed (was 70/77 — 3 new floor cases) |
| `bash scripts/ci/check-required-floor.sh` | 0 | floor is now `frontend contract e2e` |
| `bash scripts/ci/check-required-manifest.sh` | 0 | 5 entries, all real jobs |
| `bash scripts/ci/check-image-pins.sh` | 0 | 3 FROM lines pinned |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | the lane still drives the image |
| `bash scripts/ci/check-client-bundle.sh` | 0 | 10 chunks, no config leak |
| `bash scripts/ci/check-server-only-boundary.sh` | 0 | build still fails on a client import |
| `node scripts/check-spec-refs.mjs` | 0 | 9 in-document `$ref`s |
| `shellcheck -x scripts/ci/*.sh scripts/e2e/demonstrate.sh` | 0 | clean |

### Demonstrations (red then green — transcripts in the repo)
All under `vizra-user/docs/evidence/VZ-FOUND-008/`, indexed by that directory's
`README.md`. D1–D5 are the five the brief required; D6–D8 are the guards this
PR's own new machinery needed, held to the same standard.

| # | Red | Green |
|---|---|---|
| D1 console.error | `d1-console-error-RED.txt` | `d1-console-error-GREEN.txt` |
| D2 HTTP 404 sub-resource | `d2-failed-request-RED.txt` | `d2-failed-request-GREEN.txt` |
| D3 uncaught exception | `d3-uncaught-exception-RED.txt` | `d3-uncaught-exception-GREEN.txt` |
| D4a zero tests collected | `d4a-zero-tests-RED.txt` | `d4a-zero-tests-GREEN.txt` |
| D4b a project missing | `d4b-missing-project-RED.txt` | `d4b-missing-project-GREEN.txt` |
| D5 pointed at `next dev` | `d5-dev-server-RED.txt` | `d5-dev-server-GREEN.txt` |
| D6 harness inside the image | `d6-image-fixtures-RED.txt` | `d6-image-fixtures-GREEN.txt` |
| D7 weakened `e2e` workflow | `d7-lane-guard-RED.txt` | `d7-lane-guard-GREEN.txt` |
| D8 spec bypassing the guard | `d8-bypass-guard-RED.txt` | `d8-bypass-guard-GREEN.txt` |

### CI on the head SHA `112291e71cc269934c9aa87b69c021170c557f91`
PR: <https://github.com/yegamble/vizra-user/pull/3>

| Check | Result | Duration |
|---|---|---|
| **`ci-required`** (the gate) | **pass** | 2m27s |
| `e2e` | **pass** | 2m03s |
| `frontend` | pass | 57s |
| `contract` | pass | 27s |
| `guard` | pass | 12s |
| `docker-build` | pass | 1m03s |
| `deps-scan` (not required) | pass | 32s |
| `image-scan` (not required) | pass | 1m33s |
| `GitGuardian Security Checks` (not required, third-party app) | **fail** — see below | 10s |

The `e2e` lane on GitHub-hosted `ubuntu-24.04` / linux-amd64
(run 35534195373) did real work, not a vacuous pass:
- installed Chromium `chromium-1243` and `chromium_headless_shell-1243`
  (Chrome for Testing 153.0.8010.12) at Playwright 1.63.0 — the same revision
  as locally;
- built the production image and asserted
  `OK: 'vizra-user:e2e' contains no browser-harness path and no fixture token`;
- started the container, waited for `/health`;
- ran **18 tests, all passed**, 9 in `desktop-chromium-1440` and 9 in
  `mobile-chromium-390`, ending with
  `e2e coverage floor: OK (desktop-chromium-1440=9 mobile-chromium-390=9)`.

### Open item for the chair: the GitGuardian check is red
**Facts.** GitGuardian scans every commit in the PR, not just the head. The
first commit (`951f18b`) committed the Next **dev server's** HMR WebSocket URL,
`ws://127.0.0.1:3212/_next/hmr?id=<opaque>`, into the D5 transcript. Two
findings, unchanged across both pushes because the first commit still carries
them.

**Risk assessment: not a credential.** The value was an ephemeral Next HMR
session id, issued by a `next dev` process that ran for about twenty seconds on
a loopback port on the builder's laptop and no longer exists. It grants nothing,
reaches nothing, and there is nothing to rotate. No secret, key, token or
signed URL of any Vizra system is in this branch.

**Already fixed forward** (`112291e`): `e2e/harness/redact.ts` strips query and
fragment from every URL the harness records, so the class cannot recur; the
head commit's tree contains no raw query string anywhere, and the flagged
string is not reproduced in the fix, the tests or the evidence.

**What remains is history.** Clearing the check needs either (a) the finding
dismissed in the GitGuardian dashboard — an owner action outside any PR — or
(b) the branch's two commits squashed so the string never appears in any
commit, which means a force-push. **The builder did not force-push**: the branch
is published, a verifier may already have fetched it, and rewriting it is the
chair's call, not a builder's. If the chair wants (b), it is
`git reset --soft main && git commit && git push --force-with-lease` on
`feat/m0-browser-env`; the evidence transcripts and the plan record the story
independently of the discarded commit, so nothing is lost by it. A squash-merge
would also drop the commit, but GitGuardian will stay red on the PR until then.

Note that `ci-required` — the repository's actual gate — is green, and
GitGuardian is not in `.github/required-checks.txt`.

### What did not run
- **linux/amd64** — this machine is arm64 and ADR-009 forbids treating it as the
  acceptance platform. The local image build and lane run are native arm64 and
  carry no support claim. CI on the head SHA is the platform evidence.
- **WebKit / Firefox** — not installed, not configured, not claimed.
- **Accessibility** — no engine installed (VZ-A11Y-001, M1). Seam documented in
  `e2e/harness/test.ts`.
- **Visual baselines** — `toHaveScreenshot` unused; no baseline committed.
- **An API-backed journey** — there is no vizra-core to talk to; the frontend
  runs on sentinel configuration.

### Cleanup
Docker images `vizra-user:e2e-local`, `vizra-user:demonstrate` and
`vizra-user:demonstrate-with-fixtures` removed; `docker builder prune --all`
reclaimed 4.1 GB. Playwright browsers were installed with
`PLAYWRIGHT_BROWSERS_PATH=0`, i.e. inside `node_modules/playwright-core/
.local-browsers` (558 MB) rather than a machine-wide cache, so they are removed
with the checkout. Nothing was written outside the repo and the scratchpad.

## Blockers and handoff
No blockers. Nothing external was missing.

**Contract changes needed from another owner: none.** This slice adds no API
call, changes no OpenAPI operation, and does not re-vendor the contract.

**Owner-reviewed changes in this PR, named so review is not accidental:**
1. `.github/required-checks.txt` gains a required `e2e` lane;
2. `scripts/ci/check-required-floor.sh`'s floor becomes
   `frontend contract e2e`;
3. `.github/CODEOWNERS` gains `/e2e/harness/` and `/playwright.config.ts`.

**Next concrete action:** wait for `ci-required` on the head SHA, then hand to an
independent verifier. VZ-FOUND-008 stays `IMPLEMENTED` / `UNVERIFIED` until that
verifier reproduces the demonstrations from a clean clone.
