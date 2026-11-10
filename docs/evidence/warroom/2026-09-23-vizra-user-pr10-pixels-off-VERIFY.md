# VERIFY: vizra-user PR #10, "Lane A pixel channels off"

- **PR:** https://github.com/yegamble/vizra-user/pull/10, branch `fix/lane-a-pixels-off`
- **Verified SHA:** `a01a396bcaa3820e2bd89537461bc587aabc452b`, one commit on main `783483f3c5f207d3370e6f1a79766f840e36472f`. The head was confirmed with `gh api repos/yegamble/vizra-user/pulls/10` at the start and again at the end, and it had not moved.
- **Verifier:** an independent war-room verifier that did not write this code. It worked in a fresh clone under the session scratchpad (`vzv-user-pr10-XXXXXX`, created with `mktemp -d`). The clone, both worktrees, the local server and the one Docker image created (`vzv-pr10-a01a396:demonstrate`) were all removed afterwards.
- **Environment:** macOS (Darwin 25.5.0, arm64); Node v22.14.0, which matches `.nvmrc`; npm 11.4.2; Playwright 1.63.0 with Chromium 1243 (Chrome for Testing 153.0.8010.12); Docker 29.8.0.
- **Scope source:** security seat plan review `2026-09-23-vizra-user-artifact-privacy-b-PLAN-REVIEW-security.md`, Q3 and F14, and chair ruling 3 at tick 204.

## 1. Lanes

| Command (PR head, clean clone) | Exit | Result |
|---|---|---|
| `npm ci` | 0 | 415 packages |
| `npm run ci` (lint, typecheck, vitest, build, hygiene) | 0 | 19 files, **637 passed**, 0 skipped; hygiene: 308 sources, 17 mutation-digest lines match |
| `bash scripts/ci/check-e2e-lane.sh .github/workflows/e2e.yml` | 0 | OK |
| `bash scripts/ci/require-checks_test.sh` | 0 | **242 cases, 249 assertions, 0 failed**; cases 110–118 all `ok` |
| `E2E_LOCAL_PORT=3871 npm run e2e` (Lane A, local production server) | 0 | **18 passed**; coverage floor 9/9 and 9/9; 18 stamps verified |
| `npm run e2e:demos` with `DEMO_IMAGE=vzv-pr10-a01a396:demonstrate` and default ports 3211/3212 | 0 | **149 halves passed, 0 blocked, 0 failed**; D6 ran with Docker |

**The new cases go red against the old guard.** I copied `main`'s `check-e2e-lane.mjs` and `ts-source-facts.mjs` over the PR tree and ran the PR's `require-checks_test.sh`:
- the result was 242 cases and **8 failed**: exactly 110–117, each failing with `exit 0, want 1`;
- 118, the inverse control, stayed `ok`.

**`main`'s guard accepts `main`'s pixels-on config.** In the `main` clone, `check-e2e-lane.sh` exits 0 with `screenshot: "only-on-failure"`, `video: "retain-on-failure"` and the trace screencast on. This reproduces the PR's "red on main" claim.

**Reader unit mutations**, run with `npx vitest run scripts/ci/ts-source-facts.test.mjs`:
- **U1:** `ownProperty` changed to `continue` on a spread. Result: **1 failed / 48 passed**, "is UNREADABLE when a spread could supply the key".
- **U2:** the `importedFrom(…) === "@playwright/test"` line removed from `isDeviceDescriptor`. Result: **1 failed / 48 passed**, "refuses a devices spread when devices is NOT the @playwright/test import".
- **Restored:** 49/49. The file's sha256 starts `28e6a4497c0a7474` before and after, which matches the PR's `28e6a449…`.

**Device descriptors:** `node -e` over `devices` returns 207 descriptors, and 0 of them carry `screenshot`, `video` or `trace`. Confirmed.

## 2. The measured channel, `main` against this head

Command, run in each clone with `test-results/` removed first:

```
E2E_LOCAL_PORT=3872 npx playwright test --config playwright.demos.config.ts e2e/demos/failed-request.demo.ts
```

"Screencast frames" counts the `"type":"screencast-frame"` events in each `*.trace` member and the image members of `trace.zip`, which gave the same numbers.

| | `main` 783483f | PR a01a396 |
|---|---|---|
| exit | 1 (by design) | 1 (by design) |
| `.png` in `test-results/` | **2** | **0** |
| `.webm` | **2** | **0** |
| screencast frames (desktop / mobile trace.zip) | **2 / 3** | **0 / 0** |
| `trace.zip` and `error-context.md` | present | present |

**CI corroborates this.** In the `e2e` job log, the canary's four failing fixtures print their attachments:
- on this SHA (run 35899992772) only `attachment #3: trace (application/zip)` appears, 4 times;
- on `main` (run 35898972342) `video (video/webm)` ×4, `screenshot (image/png)` ×4 and `trace` ×4 appear.

## 3. Mutations: each asserted literal and each refusal

Each mutation was a byte edit in a scratch worktree at the head, with the guard (`check-e2e-lane.sh`) run twice: once mutated, then again after a `git checkout` restore.

| ID | Mutation | Mutated | Restored |
|---|---|---|---|
| L1 | `screenshot: "on"` | rc 1, `use.screenshot must be exactly "off" (read: "on")` | rc 0 |
| L2 | `video: "on"` | rc 1, `use.video … (read: "on")` | rc 0 |
| L3 | trace `mode: "on"` | rc 1, `use.trace must be exactly …` | rc 0 |
| L4 | trace `sources: true` | rc 1, by name | rc 0 |
| L5 | trace `screenshots: true` | rc 1, by name | rc 0 |
| L6/L7/L8 | screenshot / video / trace line deleted | rc 1, `(read: undefined)` | rc 0 |
| L9 | `trace: "retain-on-failure"` (string form) | rc 1, by name | rc 0 |
| L10 | extra `snapshots: true` key in trace | rc 1, by name | rc 0 |
| L11 | `video: { mode: "off" }` | rc 1, by name | rc 0 |
| L12 | duplicate key `video: "off", video: "on"` | rc 1, `(read: "on")` | rc 0 |
| R1 | `...{ video: "on" }` spread in `use` | rc 1, all three `not a literal this guard can read` | rc 0 |
| R2 | computed key in `use` | rc 1, all three unreadable | rc 0 |
| R3 | `video: process.env.E2E_VIDEO === "1" ? "on" : "off"` (env-driven) | rc 1, unreadable | rc 0 |
| R4 | template literal `${"off"}` | rc 1, unreadable | rc 0 |
| R5 | `get video() { return "on" }` | rc 1, unreadable | rc 0 |
| R6 | project #2 `use` sets `video` | rc 1, `project #2's use sets video` | rc 0 |
| R7 | project #2 `use` sets `"trace"` (string key) | rc 1, by name | rc 0 |
| R8 | project #2 `use` computed `["video"]` | rc 1, `has a computed key` | rc 0 |
| R9 | `...devices["Pixel" + " 5"]` | rc 1, `spreads something other than a device descriptor` | rc 0 |
| R10 | project-level `...{ use: { video: "on" } }` | rc 1, `project #2 has a spread or computed key` | rc 0 |
| R11 | project-level `screenshot: "on"` outside `use` | rc 1, `sets screenshot outside use` | rc 0 |
| R12 | project `use` with `...{ video: "on" }` after the devices spread | rc 1, by name | rc 0 |
| R13 | demos `use: { ...base.use, video: "on" }` | rc 1, `demos.config.ts declares use` | rc 0 |
| R14 | demos `projects: [...]` | rc 1, `declares projects` | rc 0 |
| R15 | demos computed `["u"+"se"]` | rc 1, `via computed-key` | rc 0 |
| R16 | demos `...{ use: … }` | rc 1, `via unreadable-spread` | rc 0 |
| R17 | demos `"use":` string key | rc 1, by name | rc 0 |
| R18 | `export default { ...demosConfig, use: … }` | rc 1, `via unreadable-spread` | rc 0 |
| E3 | `use: { ...sharedUse }` imported from another file | rc 1, unreadable | rc 0 |
| S1 | `scripts.e2e = "playwright test --trace on"` | rc 1, by name | rc 0 |
| S2 | `scripts.e2e = "playwright test -c playwright.lane.config.ts"` | rc 1, by name | rc 0 |
| S3 | `scripts.e2e = "PWTEST_X=1 playwright test"` | rc 1, by name | rc 0 |
| S4 | lane pin `npm run e2e -- --trace on` | rc 1, by name | rc 0 |

**Env route.** A grep of Playwright 1.63.0's `lib/` finds no environment variable that sets `screenshot`, `video` or `trace`. An env-driven value inside the config is UNREADABLE (R3), and `PLAYWRIGHT_*`, `CI` and step env are already default-deny in the workflow guard. **Caught.**

### Routes that set a pixel channel back on, with the guard GREEN

Each route below was driven end to end: guard, then a run against a production server I started from the PR build on port 3874, then an artifact count.

| ID | Route | Guard | tsc / eslint | Pixels produced |
|---|---|---|---|---|
| **E1** | `defineConfig` wrapper: `defineConfig({…}, { use: { screenshot: "on", video: "on", trace: { mode: "on", screenshots: true } } })` | **rc 0** | 0 / 0 | demo: **1 png, 1 webm, 3 frames** |
| **E2** | `const config = defineConfig({…}); config.use = { ...config.use, screenshot: "on", … }; export default config;` | **rc 0** | tsc 0 | demo: **1 png, 1 webm, 3 frames** |
| **E4** | demos config: `Object.assign(base.use ?? {}, { screenshot: "on", video: "on", trace: {…} })` before `const demosConfig` | **rc 0** | — | demo: **1 png, 1 webm, 4 frames** |
| **E5** | `e2e/harness/required-projects.ts` (imported by the config): `Object.assign(pwDevices["Desktop Chrome"], { screenshot: "on", … })` | **rc 0** | — | demo: **1 png, 1 webm, 3 frames** |
| **E6** | **one line in a spec**, `e2e/specs/health.spec.ts`: `test.use({ screenshot: "on", video: "on", trace: { mode: "on", sources: false, screenshots: true } })` | **rc 0** | 0 / 0 | **Lane A itself: 18 passed, 6 png, 6 webm, 3–4 frames in each of 6 traces** |
| **S6** | a second config referenced by a script: `harness-canary.mjs` pointed at a new `playwright.canary.config.ts` (`{ ...demos, use: { …recorders on } }`) | **rc 0** | — | canary: **rc 0**, 1 png, 1 webm, 4 frames in `test-results/` |
| S5 | `harness-canary.mjs` adds `--trace on` | rc 0 | — | 0 png, 0 webm, 0 frames: the CLI keeps `screenshots: false`. Guard-green, but no pixel effect measured |

Spec-level captures outside the recorder settings, both eslint-clean:
- `expect(page).toHaveScreenshot()` with no baseline writes `test-results/…/home-actual.png`, plus a baseline under `e2e/specs/*-snapshots/`;
- `browser.newContext({ recordVideo: { dir: testInfo.outputPath("v") } })` writes a `.webm` under `test-results/`, and the test passes.

In CI, `test-results/` is the uploaded path, whole. The canary's demos run with this configuration in CI, and their output is what `test-results/` holds when the upload fires.

## 4. AGENTS.md at measured strength

| Sentence (AGENTS.md at a01a396) | Verdict |
|---|---|
| `playwright.config.ts` sets the three values; the demos config inherits them | **True, measured** (§2) |
| The before/after table (2 / 2 / "3 and 2" → 0 / 0 / 0) | **True, reproduced exactly** |
| "reads all three values as LITERALS … and refuses any other value, a value it cannot read (a spread or a computed key in `use`), a project whose `use` sets … and a demos configuration that declares `use` or `projects`" | Each named refusal reproduced (L1–L12, R1–R18). "**refuses … a value it cannot read**" is **overstated**: a second `defineConfig` argument (E1) and an assignment after the declaration (E2) are values it cannot read, and it answers OK. The reader reads only `arguments[0]` of any call and the initializer of an identifier. |
| "none of the 207 installed descriptors sets a recorder" | True as a statement about the package. The object is mutable from any module the config imports (E5). |
| "Nine cases in `require-checks_test.sh` are red by name." | **Inaccurate:** 8 are red; case 118 is an inverse control that expects exit 0 |
| "What this does NOT stop": `resources/*` image bytes, DOM snapshots re-rendered, a spec's own `page.screenshot({ path })` | True as far as it goes. **Incomplete:** `test.use({ screenshot, video, trace })` in any spec restores all three recorders in Lane A itself (E6). `recordVideo` on a spec's context and a failing `toHaveScreenshot` also write pixels into `test-results/`. None of these is stated. |
| Upload table: `test-failed-1.png`, `video.webm` "not produced" | True for the shipped config |
| "Screenshots, video and trace screencast frames are no longer recorded **at all**" (§ What PR A's controls still guarantee, "nothing new is claimed here") | **Overstated:** E6, the one-line spec, records all three with every check green |
| "The demos configuration inherits them and may not override `use`" (config header) | Overstated: the demos config can mutate the imported `base.use` (E4) |

**Does anything still capture pixels in Lane A as shipped?** No. The lane shows 0 png, 0 webm and 0 frames, and the canary in CI prints only trace attachments. Pixels come back only through the unstated routes above.

## 5. `npm run e2e:demos` and the transcripts

- **Result:** exit 0, 149 halves passed, 0 blocked, 0 failed. This confirms the PR's claim that no demonstration asserts on a screenshot, a video or a screencast frame.
- **Digest ledger:** `docs/evidence/VZ-FOUND-008/mutation-digests.txt` is **byte-identical** after the run (`git diff --quiet` passes).
- **Transcripts:** the run changed 60 files. The regenerated transcripts drop every `attachment #n: video (video/webm)` and `screenshot (image/png)` block, for example in `d2-failed-request-RED.txt`.
  - **Committed at a01a396:** 44 transcript files show pixel attachments.
  - **After regeneration:** 3 still do, and none of the three is rewritten by the script (`round6-lane-local.txt`, `round7-lane-local.txt`, `d12-requestfailed-listener-neutered-GREEN.txt`).
  - **Other changes:** some diffs are pre-existing drift unrelated to this PR, e.g. `d16c-*` quotes `ci-environment.ts:264` where the file (unchanged by this PR, last changed in 7a3a572) now has line 268. There is also build-log and timing noise.
- **Is the stale transcript a false statement?** Not strictly. `environment.txt` attributes the committed transcripts to `4db7dce` on `fix/m0-artifact-privacy-a`, so they are attributed historical records, and the PR body discloses that `e2e:demos` was not run. But at a01a396 the tree holds two contradictory statements about the same demo: AGENTS.md says `failed-request.demo.ts` produces no PNG or WebM, while `d2-failed-request-RED.txt` shows both. A reader of the evidence directory at this SHA is misled. I regenerated the transcripts and they would reconcile. SHOULD, not blocking on its own.

## 6. CI on a01a396, read with my own `gh api`

Check-runs on the head, `total_count` 8, all `completed/success`:
- GitGuardian Security Checks
- e2e
- deps-scan
- guard
- frontend
- image-scan
- ci-required
- contract

Workflow runs on `head_sha`, all `pull_request`, attempt 1, `success`: frontend-ci, contract-ci, e2e, supply-chain, ci-guard, ci-required.

**`ci-required`** (run 35899992393) printed "OK: every required check on a01a396… concluded success". Its manifest, `.github/required-checks.txt`, lists `frontend`, `contract`, `?guard`, `?docker-build` and `e2e`:
- frontend, contract, guard and e2e each ran as a check-run on this SHA;
- `docker-build` is `?`-optional and reported "(not triggered, optional-if-absent)". No listed-but-never-executed lane was counted as a pass.

The `e2e` job log shows the lane at "18 passed" with "coverage floor: OK (9/9 9/9)", and the canary OK on all 4 fixtures.

## 7. Diff audit

- **Test lines:** no test line deleted (`--numstat`: require-checks_test.sh +41/−0, ts-source-facts.test.mjs +73/−0), and no assertion weakened.
- **No new skips**, no generated-file edits, no new dependency, no secrets.
- **API claim:** `trace.screenshots` is a real Playwright 1.63 option. Measured: setting it false removes the screencast frames.

## Findings

```
FINDING 1: The config reader is fail-open outside the object literal — a second defineConfig argument or a post-declaration assignment turns every recorder back on with the guard green
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/ts-source-facts.mjs (defaultExportedObject: `expression = expression.arguments[0]`, identifier → initializer), scripts/ci/check-e2e-lane.mjs (PIXELS_OFF block), AGENTS.md "refuses … a value it cannot read", playwright.demos.config.ts header "may not override `use`"
  requirements: VZ-FOUND-008 (security seat Q3/F14)

Observed:
  E1  export default defineConfig({ …unchanged… }, { use: { screenshot: "on", video: "on", trace: { mode: "on", screenshots: true } } });
      check-e2e-lane.sh rc 0; tsc 0; eslint 0; failing demo → 1 png, 1 webm, 3 screencast frames.
  E2  const config = defineConfig({…}); config.use = { ...config.use, screenshot: "on", video: "on", trace: {…} }; export default config;
      guard rc 0; tsc 0; same pixels.
  E4  playwright.demos.config.ts: Object.assign(base.use ?? {}, { screenshot: "on", … }) — guard rc 0; 1 png, 1 webm, 4 frames.
  E5  e2e/harness/required-projects.ts: Object.assign(devices["Desktop Chrome"], { screenshot: "on", … }) — guard rc 0; 1 png, 1 webm, 3 frames.
  (The PR's reader is advertised as fail-closed: "a guard that asserts a value must be able to read all of it, or it must not say yes".)

Failure:
  The guard asserts the literal it can see, not the configuration Playwright loads. A one-line, type-correct edit
  republishes pixels in a public artifact while every check is green — the exact false-positive CI the ruling exists to prevent.

Perspective:
  operator | developer

Recommendation:
  Smallest static fix: require the exact shape `export default defineConfig(<one object literal>)` — refuse a call with
  ≠ 1 argument or a callee other than the imported `defineConfig`, and refuse an identifier export; in the demos config refuse
  any reference to `base` other than the one top-level spread. Stronger and cheaper to keep true: a RUNTIME assertion in the
  harness (an auto fixture in e2e/harness/test.ts that reads the resolved `screenshot`, `video` and `trace` option fixtures and
  throws unless they equal the three literals) — it closes E1, E2, E4, E5, E6 and S6 at once, whatever the source spelling.

Acceptance criteria:
  E1, E2, E4 and E5 above each make the lane guard or the lane red by name; the unmodified tree is green; AGENTS.md states
  which layer (static or runtime) refuses each.

Tests:
  require-checks_test.sh harness_expect cases for E1 and E2 (perl byte edits of playwright.config.ts) and E4 (demos config);
  if the runtime fixture is chosen, a demonstrate.sh half: a spec with test.use({ video: "on" }) is RED by name.

Cross-repo implications:
  core: none | user: this PR | search: none | meta: none

Challenge:
  Every route needs an edit to a reviewed file; Q3 asked only that the three literals be "asserted by the parsed-config guard".
  But the PR claims more than Q3 asked — fail-closed reading — and E1 is a one-line, idiomatic Playwright spelling.
```

```
FINDING 2: A spec's `test.use({ screenshot, video, trace })` restores all three recorders in Lane A itself; the stated residuals omit it and AGENTS.md says pixels are "no longer recorded at all"
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md ("What this does NOT stop" paragraph; "Screenshots, video and trace screencast frames are no longer recorded at all"; the NOT-covered table row), e2e/harness/test.ts (test.use is the documented per-file option path), eslint-rules/
  requirements: VZ-FOUND-008

Observed:
  E6  e2e/specs/health.spec.ts, one added line after the import:
        test.use({ screenshot: "on", video: "on", trace: { mode: "on", sources: false, screenshots: true } });
      npx eslint e2e → 0; tsc → 0; check-e2e-lane.sh → 0; Lane A (E2E_BASE_URL=http://127.0.0.1:3874 npx playwright test) → 18 passed,
      test-results/ holds 6 .png, 6 .webm, and 3–4 screencast frames in each of 6 trace.zip.
  Also eslint-clean: expect(page).toHaveScreenshot() (failing, no baseline) → test-results/…/home-actual.png;
  browser.newContext({ recordVideo: { dir: testInfo.outputPath("v") } }) → a .webm under test-results/, test passes.
  The upload path is `test-results/` whole.

Failure:
  The residual list names only `page.screenshot({ path })`. A reader is told the recorders are off "at all" and that only a
  spec's explicit screenshot call remains; in fact any spec can switch the lane's own recorders back on declaratively,
  unrefused. Q3 said "completely".

Perspective:
  operator | developer

Recommendation:
  Either (a) the runtime option assertion from FINDING 1, which refuses test.use recorder overrides at run time, or (b) a lint
  refusal of `screenshot`/`video`/`trace` keys in any `.use({…})` / `.extend({…})` under e2e/**, plus `recordVideo` and the
  screenshot matchers — and in every case state what remains (the spec-level capture APIs) in AGENTS.md and delete "at all".

Acceptance criteria:
  E6 is RED by name (lint or runtime); AGENTS.md's residual list names every spec-level pixel API that remains unrefused;
  no sentence says pixels are not recorded "at all" unless E6, recordVideo and toHaveScreenshot are all refused.

Tests:
  require-checks or demonstrate.sh case: E6 spec → red; inverse control: test.use({ browserErrorPolicy }) stays green.

Cross-repo implications:
  core: none | user: this PR, and PR B (Lane B's config is the same shape) | search: none | meta: none

Challenge:
  A spec author who writes test.use({ video: "on" }) is as deliberate as one who writes page.screenshot(); arguably the
  residual sentence covers "a spec's own" capture in spirit. It does not name the mechanism, and the "at all" sentence is
  flatly contradicted by a measurement.
```

```
FINDING 3: The canary's Playwright configuration is not pinned; a second config file referenced from harness-canary.mjs publishes pixels in CI with the guard and the canary green
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/harness-canary.mjs:133-146 (args `--config playwright.demos.config.ts`), scripts/ci/check-e2e-lane.mjs (pins the canary's `run:` only)
  requirements: VZ-FOUND-008

Observed:
  S6  harness-canary.mjs `"playwright.demos.config.ts"` → `"playwright.canary.config.ts"`, new file
      `export default { ...demos, use: { ...demos.use, screenshot: "on", video: "on", trace: { mode: "on", screenshots: true } } }`.
      check-e2e-lane.sh rc 0; `node scripts/ci/harness-canary.mjs` rc 0 ("failed all 4 fault-injection fixtures");
      test-results/ holds 1 png, 1 webm, 4 frames — the directory the red-lane upload publishes.
  (S5, `--trace on` added to the canary args, is also guard-green but produced 0 pixels.)

Failure:
  The canary's demos are the files that populate test-results/ at upload time in CI, and which config they run under is
  decided by an unpinned script.

Perspective:
  operator

Recommendation:
  Assert the canary's argv literal (config path) from the parsed harness-canary.mjs, or rely on the runtime assertion of FINDING 1.

Acceptance criteria:
  S6 is red by name; the unmodified tree is green.

Tests:
  require-checks_test.sh harness_expect case mutating scripts/ci/harness-canary.mjs.

Cross-repo implications:
  core: none | user: this PR | search: none | meta: none

Challenge:
  Needs two edits, one creating a new config file; a reviewer would likely see it. But so would every other route this guard exists for.
```

```
FINDING 4: The committed demonstration transcripts contradict AGENTS.md at this SHA
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     docs/evidence/VZ-FOUND-008/d2-failed-request-RED.txt:26-31 (and 43 other transcripts), docs/evidence/VZ-FOUND-008/environment.txt
  requirements: VZ-FOUND-008

Observed:
  At a01a396, 44 committed transcripts print `attachment #n: video (video/webm)` / `screenshot (image/png)`; AGENTS.md now
  says those files are "not produced". `npm run e2e:demos` at this head: exit 0, 149/0/0, digest ledger byte-identical, and
  the regenerated transcripts drop every pixel attachment (3 files the script does not rewrite still show them).
  environment.txt attributes the committed set to 4db7dce, and the PR body discloses the skip.

Failure:
  Not a false statement — the records are attributed to a past SHA — but the evidence directory at this SHA contradicts the
  contract at this SHA, and part of that set was already stale on main (d16c quotes ci-environment.ts:264, now :268).

Perspective:
  developer

Recommendation:
  Regenerate with `npm run e2e:demos` on the fix round and commit the transcripts with environment.txt at that SHA.

Acceptance criteria:
  `git grep -l 'attachment #.*: (screenshot|video)' docs/evidence/VZ-FOUND-008` names only the round6/round7 historical logs
  (or those are labelled historical); mutation-digests.txt unchanged.

Tests:
  none beyond the regeneration.

Cross-repo implications:
  core: none | user: this PR | search: none | meta: none

Challenge:
  They are dated, attributed records; rewriting them every PR is churn. The contradiction on one demo at one SHA is still the cheaper thing to remove.
```

```
FINDING 5: "Nine cases … are red by name" — eight are; case 118 is an inverse control
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md (Lane A records NO PIXELS paragraph), scripts/ci/require-checks_test.sh case 118 (`harness_expect 0 …`)
  requirements: VZ-FOUND-008

Observed:
  Old guard + new suite: exactly 110–117 fail; 118 passes (it expects exit 0).

Failure:
  Count overstated by one.

Perspective:
  developer

Recommendation:
  "Eight cases are red by name, and one inverse control stays green."

Acceptance criteria:
  The sentence matches the suite.

Tests:
  none.

Cross-repo implications:
  core: none | user: this PR | search: none | meta: none

Challenge:
  Trivial; the PR body itself states 8 + 1 correctly.
```

## Verdict

The PR does what Q3 asked in the shipped configuration:
- the three literals are set and asserted;
- every named refusal goes red by name and green on restore;
- the pixel channel measurement reproduces exactly (2/2/5 → 0/0/0);
- CI is 8/8 green on this SHA, with `ci-required` green and its manifest honest;
- the lanes reproduce: 637/0, 242/249/0, Lane A 18 passed, and demos 149/0/0 with the digest ledger byte-identical.

It FAILS on its own claims of strength. The reader it calls fail-closed says OK to a second `defineConfig` argument and to a post-declaration assignment, each of which turns every recorder back on (FINDING 1). A single `test.use` line in any spec turns all three back on inside Lane A with lint, typecheck, the guard and the lane green. The residuals omit this, and AGENTS.md says pixels are "no longer recorded at all" (FINDING 2). One runtime option assertion in the harness would close both, plus FINDING 3.

This is not a merge and not VERIFIED in the ledger.

FINAL VERDICT: FAIL — SHA a01a396bcaa3820e2bd89537461bc587aabc452b

---

## Re-verification at 96dd3ff

- **Verified SHA:** `96dd3ff553e1e230c62ad0e48d2d0b6a1261a5ed`, fix round 1, one commit on `a01a396`.
- **Head:** confirmed with `gh api repos/yegamble/vizra-user/pulls/10` at the start and again at the end. It had not moved.
- **Clone:** fresh, under the scratchpad (`vzv-user-pr10r1-XXXXXX`, via `mktemp -d`).
- **Environment:** as before (Node 22.14.0, Playwright 1.63.0, Chromium 1243, Docker 29.8.0, macOS arm64).
- **Cleanup:** the clone, the worktree, the local server on port 3894 and the image `vzv-pr10r1-96dd3ff:demonstrate` were all removed afterwards.

### R1. Lanes

| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | — |
| `npm run ci` | 0 | 20 files, **647 passed**, 0 skipped; hygiene 316 sources, 19 digest lines match |
| `bash scripts/ci/require-checks_test.sh` | 0 | **246 cases, 253 assertions, 0 failed**; 110–122 all `ok` (118 = `recorderProblems` call, 119–121 = S6, 122 = inverse control) |
| `bash scripts/ci/check-e2e-lane.sh .github/workflows/e2e.yml` | 0 | OK |
| `E2E_LOCAL_PORT=3891 npm run e2e` | 0 | **18 passed**; floor 9/9 and 9/9; 18 stamps |
| `npm run e2e:demos` (`DEMO_IMAGE=vzv-pr10r1-96dd3ff:demonstrate`, ports 3211/3212) | 0 | **155 halves passed, 0 blocked, 0 failed** |

**D23, as recorded by my run:**
- `d23a`: E6 refused by name; `pixel files: png=0 webm=0 screencast-frames=0`.
- `d23b`: with the check off, `1 passed` and `png=1 webm=1 screencast-frames=3`.
- `d23c`: restored, refused again, with 0 pixels.

**Digest ledger.** After my `e2e:demos` run, `mutation-digests.txt` is byte-identical to the committed file.
- The committed change `a01a396..96dd3ff` is `+9/−6`. Six `test.ts` lines move from `a0650a88…` to `c6fa94b9…`: D13q BEFORE/RESTORED, D15i BEFORE/MUTATED/RESTORED and D15j RESTORED.
- Three `D23b recorders.ts` lines are new.
- Every other line is byte-identical.
- `c6fa94b9…` and `439262c1…` equal the sha256 of `test.ts` and `recorders.ts` at `96dd3ff`.

**Transcripts.** After regeneration, the only files that show `attachment #n: screenshot|video` are the three that carry the "HISTORICAL, pre-#10" header:
- `round6-lane-local.txt`;
- `round7-lane-local.txt`;
- `d12-requestfailed-listener-neutered-GREEN.txt`.

My re-run changed 80 transcript files, but only in noise. The builder recorded on port 3391; mine used the default 3211. The remaining differences are build and timing noise, with no content change.

**CI.** Read with my own `gh api`:
- **Check-runs:** `total_count` 8, all `completed/success`: deps-scan, image-scan, contract, guard, e2e, frontend, ci-required, GitGuardian.
- **Workflow runs**, all `pull_request`, attempt 1: contract-ci, frontend-ci, supply-chain, e2e (35913526543), ci-required (35913526413), ci-guard.
- **`ci-required`** printed "OK: every required check on 96dd3ff… concluded success". Its manifest lists frontend, contract, ?guard, ?docker-build and e2e; `docker-build` is optional and was not triggered.
- **`e2e` log:** lane "18 passed", floor OK, canary OK on all 4. The canary's attachments are `trace` ×4 only.

### R2. My earlier routes, re-run end to end

Each route was re-run against a production server on port 3894, followed by a pixel count.

| Route | Lane guard | Run | Pixels |
|---|---|---|---|
| E1, second `defineConfig` argument | rc 0 (the early-warning reader still cannot see it) | demo red: `Lane A records NO PIXELS, but in this worker … screenshot, video, trace` | **0 / 0 / 0** |
| E2, `config.use = …` | rc 0 | red by name | **0 / 0 / 0** |
| E4, demos `Object.assign(base.use, …)` | rc 0 | red by name | **0 / 0 / 0** |
| E5, `devices[…]` mutated in `required-projects.ts` | rc 0 | red by name | **0 / 0 / 0** |
| E6, one `test.use` line in `health.spec.ts` | rc 0 | Lane A: 6 failed by name, 12 passed | **0 / 0 / 0** |
| S6, canary pointed at a second config | **rc 1**, by name (twice) | canary red by name | **0 / 0 / 0** |
| `--trace on` on the CLI | — | 3 failed by name | 0 |

**Result: all six earlier routes are closed.**

### R3. New routes around the runtime check

**N1: disguised option values (`toJSON`), which ESCAPES.**

`recorders.ts` compares `canonical(value)`, and `canonical` is `JSON.stringify` with a replacer. `JSON.stringify` calls a value's own `toJSON()` BEFORE the replacer. So the check compares what the object says about itself, while Playwright reads `.mode` and spreads the fields: `normalizeScreenshotMode`, `normalizeVideoMode`, and `Tracing.startIfNeeded` in `workerProcessEntry.js`. This spec is lint- and typecheck-clean:

```ts
import { expect, test } from "../harness/test";
const screenshot = { mode: "on" as const, toJSON: () => "off" };
const video = { mode: "on" as const, toJSON: () => "off" };
const trace = { mode: "on" as const, sources: false, screenshots: true,
  toJSON: () => ({ mode: "retain-on-failure", sources: false, screenshots: false }) };
test.use({ screenshot, video, trace });
test("home renders", async ({ page }) => { await page.goto("/"); await expect(page.getByRole("heading", { level: 1 })).toBeVisible(); });
```

Measured outcome:
- `npx eslint` 0, `npx tsc --noEmit` 0, lane guard 0.
- **Alone:** 1 passed and stamped; `test-results/` holds `test-finished-1.png`, `video.webm` and a `trace.zip` with 2 screencast frames.
- **Inside the full Lane A (`npx playwright test`):**
  - **20 passed**, floor OK (10/9, 10/9), 20 stamps verified;
  - `node scripts/ci/check-coverage-floor-ran.mjs` exit 0;
  - **2 PNG, 2 WebM**, plus screencast frames.
- **Publication:** any red lane then uploads `test-results/` whole, pixels included.

**N2: getters, no `toJSON`, which also ESCAPES.** A plain trace object whose getters for `mode` and `screenshots` return the Lane A values when the call stack includes `recorders`, and `"on"`/`true` otherwise. `test.use({ trace })` gives:
- lint 0, typecheck 0, guard 0;
- 1 passed and stamped;
- `trace.zip` retained for a PASSING test, with **2 screencast frames**.

So swapping `JSON.stringify` for a structural compare would not close the class. The checked value and the value Playwright uses are two separate reads of an object the spec controls.

**Fixture replacement and direct import: the lane goes RED, and the pixels are produced anyway.**
- **R-a, fixture replacement.** A spec replaces both branded fixtures through `harnessTest.extend({ vizraWorkerGuard: no-op, vizraHarnessGuard: no-op })` and adds `test.use({ …recorders on })`.
  - lint 1, tsc 2 (my typing), lane guard 0;
  - the run goes red, "succeeded WITHOUT the harness stamp";
  - `test-results/` holds **1 png, 1 webm, 3 frames**.
- **R-b, direct import.** A spec does `import { expect, test } from "@playwright/test"` with the same `test.use`.
  - eslint 1 ("must not reference `@playwright/test`"), tsc 0, lane guard 0;
  - the run goes red, unstamped;
  - **1 png, 1 webm, 3 frames**.
- **Why this matters.** The upload runs precisely `if: failure()` after a redaction that passes pixels, and ESLint runs in the separate `frontend` job. So "costs the stamp" makes the lane red and **publishes** these pixels. The redaction step refuses page snapshots, not images.

**R-c, worker-option timing: CAUGHT.** In a serial pair, test 1 does `Object.assign(trace, { mode: "on", screenshots: true })` after its own check. Test 2's per-test check refuses it by name, and test 2 produces 0 pixels: the harness throws before any page exists.

**Removing only one of the two calls.** Removing only the worker-scoped `recorderProblems` call leaves the lane guard at rc 0, because one genuine call remains. E6 is then still refused by the per-test check, with 0 pixels. The two-call design holds, but case 118 only proves that removing BOTH calls is red.

**The demos config** is covered by the runtime check (E4 above).

**A project whose fixtures bypass `test.ts`:** a project cannot declare fixtures. Its specs must import a `test`, so this reduces to R-b.

### R4. AGENTS.md and the config header, under "no false-guarantee merges"

| Sentence | Verdict |
|---|---|
| Config header: the runtime check "refuses any RESOLVED value other than these three, **however it was produced**" | **False.** N1 and N2 produce recording values the check accepts. |
| "The runtime check refuses each of them, whatever the spelling, because every one changes the RESOLVED value" (E1–E6, S6) | True for the six routes named (R2) |
| Fixture table: `vizraWorkerGuard` "refuses the worker if the RESOLVED … options are not Lane A's no-pixels values" | **Overstated:** it compares a serialisation the value controls (N1) |
| "replacing either fixture to drop the check costs the stamp" | True, and incomplete. The run is red, but the pixels are produced and the red-lane upload publishes them (R-a, R-b). "What this does NOT stop" does not say so. |
| "The cost: a developer can no longer turn the recorders on locally with `--trace on`, **`--video on`** or `test.use`" | `--trace on` and `test.use` are refused (measured). **Playwright 1.63.0 has no `--video` option:** `npx playwright test --video on` prints `error: unknown option '--video'`. The sentence names a nonexistent flag. |
| The residual list: `resources/*` image bytes, DOM snapshots, `page.screenshot({ path })`, failing `toHaveScreenshot`, `recordVideo` on a spec's context | Accurate as far as it goes. **Incomplete:** N1/N2, and a spec outside the harness (R-a, R-b) |
| "eight of its cases are red by name and one inverse control stays green" | Corrected; matches the suite |
| "There are sixteen: fifteen that require a genuine CALL …" | Not independently counted; not load-bearing for this slice. UNVERIFIED |
| The stray-config paragraph ("the one other CI script … has its `--config` pinned") | True: S6 is red by name (cases 119–121 and my S6) |
| The upload table: test-failed PNG and WebM "not produced by the recorders: the RESOLVED options are checked at runtime" | **Overstated** per N1: `test-finished-1.png` and `video.webm` were produced by the recorders with the check green |

### R5. Findings at 96dd3ff

Status of the earlier findings:
- **FINDINGS 1 and 3: closed** at runtime. E1, E2, E4, E5 and S6 each produce 0 pixels, and S6 is also red at the guard.
- **FINDING 2: closed for E6** (0 pixels, red by name), but see FINDING 6.
- **FINDING 4: closed.** The transcripts are regenerated and the historical logs are labelled.
- **FINDING 5: closed.**

```
FINDING 6: The runtime recorder check compares a value's self-serialisation, not what Playwright reads — a spec's disguised test.use turns every recorder back on with lint, typecheck, guard, floor and stamps green
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/recorders.ts (canonical → JSON.stringify; recorderProblems), e2e/harness/test.ts:148 and :234, playwright.config.ts header ("however it was produced"), AGENTS.md fixture table, upload table and "The control is a RUNTIME check on the RESOLVED values"
  requirements: VZ-FOUND-008 (security seat Q3/F14)

Observed:
  N1 (toJSON) in e2e/specs/: eslint 0, tsc 0, check-e2e-lane 0; full Lane A 20 passed, floor-ran 0, 20 stamps;
  test-results/ holds 2 PNG (test-finished-1.png), 2 WebM, screencast frames in trace.zip.
  N2 (stack-aware getters on the trace object, no toJSON): 1 passed, trace.zip with 2 screencast frames.
  Playwright reads normalizeScreenshotMode(v) = v.mode, normalizeVideoMode(v) = v.mode, and Tracing.startIfNeeded spreads
  the object; the check reads JSON.stringify(v), which calls v.toJSON() first.

Failure:
  The control the PR now names as THE control is satisfied by an object that reports the literals when asked and records
  when used. Any red lane then publishes the pixels. The same spec-author reach that E6 needed.

Perspective:
  operator | developer

Recommendation:
  Do not trust the option object's self-report. Either
  (a) accept only primitives for `screenshot`/`video` (`typeof v === "string" && v === "off"`) and, for `trace`, only a
      plain object — Object.getPrototypeOf === Object.prototype, every own property a DATA descriptor (no get/set), no
      `toJSON`, exact key set — and then make Playwright read the object you checked (for example, fail unless
      Object.isFrozen(trace) and the config freezes it); a Proxy still defeats this, so add (b); or
  (b) the effect-based backstop: refuse, in redact-artifacts.sh (the upload gate that already refuses `# Page snapshot`),
      any `*.png`, `*.webm` or screencast/`resources/*.jpeg` member under the uploaded paths — "not produced" becomes
      "not published", whatever the spelling, and it also covers R-a/R-b and the spec capture APIs this PR lists as open.
  (b) alone closes the privacy outcome; (a) keeps the lane's red-by-name signal honest.

Acceptance criteria:
  N1 and N2 as written above are red (lint, runtime or upload gate), and in a failing run with either present nothing
  under the upload paths is a PNG, WebM or screencast frame; the unmodified lane stays green; AGENTS.md states which
  layer refuses each.

Tests:
  a demonstrate.sh half per route (N1, N2) mirroring D23, and a redact-artifacts test fixture tree carrying a .png, a
  .webm and a trace.zip with a screencast member, each refused with a distinct exit code.

Cross-repo implications:
  core: none | user: this PR and PR B (Lane B's recorder literals have the same shape) | search: none | meta: none

Challenge:
  N1/N2 are deliberate evasions, and a deliberate spec author can already call page.screenshot(), which AGENTS.md lists as
  open. But this PR's text says the recorder options are refused "however it was produced", and the builder's own control
  was written because the previous one checked the text rather than the effect; this one checks the object's self-report
  rather than the effect.
```

```
FINDING 7: A spec that leaves the harness still records with the recorders on, and "costs the stamp" means the red-lane upload publishes those pixels — not stated
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md ("It sits inside the two BRANDED fixtures, so replacing either fixture to drop the check costs the stamp"; "What this does NOT stop"), .github/e2e-pinned-steps.yml (upload `if: failure() && steps.redact.outcome == 'success'`)
  requirements: VZ-FOUND-008

Observed:
  R-a (both branded fixtures replaced + test.use recorders on): run red "succeeded WITHOUT the harness stamp"; 1 png, 1 webm, 3 frames.
  R-b (direct `@playwright/test` import + same test.use): eslint 1, tsc 0, run red unstamped; 1 png, 1 webm, 3 frames.
  ESLint runs in the `frontend` job; the `e2e` job's upload fires on its own failure.

Failure:
  The stamp turns the lane red, and red is exactly when test-results/ is published; the pixels go with it.

Perspective:
  operator

Recommendation:
  State it in "What this does NOT stop", or close it with FINDING 6's upload-gate refusal (which closes it outright).

Acceptance criteria:
  Either the sentence exists, or R-a/R-b in a red run leave no PNG/WebM/screencast frame in the uploaded paths.

Tests:
  as FINDING 6 (b).

Cross-repo implications:
  core: none | user: this PR | search: none | meta: none

Challenge:
  Pre-existing class (true of any spec that leaves the harness since PR #3), and two layers go red. Still, red is the
  publishing condition, so "costs the stamp" is not a pixel guarantee and should not read like one.
```

```
FINDING 8: AGENTS.md names a CLI flag Playwright does not have
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md ("with `--trace on`, `--video on` or `test.use`")
  requirements: VZ-FOUND-008

Observed:
  `npx playwright test --video on` → `error: unknown option '--video'`; lib/program.js has only `--trace <mode>`.

Failure:
  An invented API in a contract document.

Perspective:
  developer

Recommendation:
  "with `--trace on` or `test.use`".

Acceptance criteria:
  The sentence names only options that exist in the installed Playwright.

Tests:
  none.

Cross-repo implications:
  core: none | user: this PR | search: none | meta: none

Challenge:
  Trivial.
```

### Re-verification verdict

**What passed:**
- The fix round closes every route I reported: E1, E2, E4, E5, E6 and S6 all produce 0 pixels, and S6 is also red at the guard.
- The lanes reproduce: 647/0, 246/253/0, Lane A 18 passed, and demos 155/0/0.
- The digest ledger change is exactly as stated.
- The transcripts are reconciled.
- CI is 8/8 green, with `ci-required` green and its manifest honest.

**Why it still fails:** the new control is not what the PR says it is. A spec's `test.use` whose values serialise as the literals but record when Playwright reads them (N1 `toJSON`, N2 getters) passes the check. With lint, typecheck, guard, floor and stamps all green, Lane A then writes PNG, WebM and screencast frames into the uploaded directory (FINDING 6). The sentences "however it was produced" and "refuses the worker if the RESOLVED options are not…" are false as written.

FINAL VERDICT: FAIL — SHA 96dd3ff553e1e230c62ad0e48d2d0b6a1261a5ed

---

## Re-verification at b68294b

- **Verified SHA:** `b68294b027965b6df57e3705d3b15631bafd4873`, fix round 2 of 2, one commit on `96dd3ff`.
- **Head:** confirmed with `gh api repos/yegamble/vizra-user/pulls/10` at the start and again at the end. It had not moved.
- **Clone:** fresh, under the scratchpad (`vzv-user-pr10r2-XXXXXX`, via `mktemp -d`).
- **Environment:** as before (Node 22.14.0, Playwright 1.63.0, Chromium 1243, Docker 29.8.0, macOS arm64).
- **Cleanup:** the clone, the worktree, the local server on port 3904, the image `vzv-pr10r2-b68294b:demonstrate` and the detached writer process were all removed.

### G1. Lanes, demos, ledger, CI

| Command | Exit | Result |
|---|---|---|
| `npm ci` / `npm run ci` | 0 / 0 | 21 files, **660 passed**, 0 skipped; hygiene 332 sources, 23 digest lines match |
| `bash scripts/ci/require-checks_test.sh` | 0 | 246 cases, 253 assertions, 0 failed |
| `bash scripts/ci/check-e2e-lane.sh .github/workflows/e2e.yml` | 0 | OK |
| `E2E_LOCAL_PORT=3901 npm run e2e` | 0 | **18 passed**; floor 9/9 and 9/9; 18 stamps |
| `npm run e2e:demos` (`DEMO_IMAGE=vzv-pr10r2-b68294b:demonstrate`) | 0 | **170 halves passed, 0 blocked, 0 failed**; all 16 D24 halves `ok` (d24a–f as the builder lists) |

**The builder's unit claim, reproduced.**
- With `96dd3ff`'s `recorders.ts` swapped into the head, `recorders.test.ts` gives **6 failed / 7 passed**: N1, the N1 variant, N2, Proxy, "class instance, null prototype…", and "does not use Array.prototype.filter".
- Restored, `recorders.test.ts` and `upload-gate-pixels.test.ts` give **19/19**.
- I also mutated the gate's `pixel_magic "$file"` to `false`. `upload-gate-pixels.test.ts` then gives **2 failed / 4 passed**: "an image whose name hides it is refused by its bytes" and "a trace archive with an image resource is refused, even with no extension".

**Digest ledger.**
- After my demos run, `mutation-digests.txt` is **byte-identical** to the committed file.
- The committed change `96dd3ff..b68294b` is `+15/−9`:
  - six `test.ts` lines move to `78db5fbe…`, and D15i MUTATED moves to `d9052eea…`;
  - three `D23b recorders.ts` lines move to `4a260678…` / `5e63f733…`;
  - seven new lines cover D24d `recorders.ts` and D24e `redact-artifacts.sh`, with `97627fe1…` before and restored.
- `78db5fbe…`, `4a260678…` and `97627fe1…` are the sha256 of `test.ts`, `recorders.ts` and `redact-artifacts.sh` at b68294b.
- Every other line is byte-identical. The change is as stated.

**CI**, read with my own `gh api`:
- **Check-runs:** `total_count` 8, all `completed/success`: ci-required, e2e, deps-scan, frontend, image-scan, guard, contract, GitGuardian.
- **Workflow runs**, all `pull_request`, attempt 1: contract-ci, frontend-ci, e2e (35921131961), ci-guard, supply-chain, ci-required (35921132010).
- **`ci-required`** printed "OK: every required check on b68294b… concluded success"; `docker-build` is optional and was not triggered.
- **`e2e` log:** lane "18 passed", floor OK, canary OK on all 4.

### G2. N1, N2 and R-a end to end, through the pinned gate

Each spec was run against a local production server (port 3904), then `bash scripts/ci/redact-artifacts.sh test-results playwright-report`.

| Route | Run | Pixel files before the gate | Gate | Pixels in the upload set |
|---|---|---|---|---|
| N1 (`toJSON`) | red: `resolved recorder option(s) screenshot, video, trace are not exactly …` | 0 png, 0 webm; `trace.zip` has no image member | rc 0 | **0** (the upload runs, carrying no pixels) |
| N2 (getters) | red by name, `trace` | 0 / 0 | rc 0 | **0** |
| R-a (both branded fixtures replaced, recorders on) | red, "succeeded WITHOUT the harness stamp" | **1 png, 1 webm**, `trace.zip` with `screencast/page@….jpeg` | **rc 4**, names the paths | **0: the upload is skipped** |

FINDINGS 6 and 7 are closed in code: N1 and N2 are refused at runtime, and R-a's pixels are refused at the gate. FINDING 8 is closed: `--video on` was removed, and the docs note that 1.63.0 has no such flag.

### G3. Trying to get pixels past the gate

**Method.**
- I used a byte-identical copy of the head's `redact-artifacts.sh`, verified with `cmp`, plus `redaction-patterns.json`.
- Each case ran over a fresh `test-results/` + `playwright-report/results.json` tree.
- Fixtures were a real 16×16 PNG and a `sips`-converted JPEG, a BMP, a TIFF and an ICO. `file` confirms each.
- "CAUGHT" = non-zero exit, so nothing uploads.

| Case | rc | Result |
|---|---|---|
| clean tree (inverse control) | 0 | passes, as it should |
| `a.png` by name | 4 | CAUGHT |
| PNG renamed `a.dat` (signature) | 4 | CAUGHT |
| trace.zip member `resources/frame`, JPEG with no extension | 4 | CAUGHT |
| trace.zip member renamed `page@x-1.bin` | 4 | CAUGHT |
| deflate-compressed member inside a `.zip` | 4 | CAUGHT (the gate unzips) |
| `results.json` attachment typed `image/png` with a base64 body | 4 | CAUGHT |
| **PNG with 1 leading byte**, `a.dat` | 0 | **ESCAPED** |
| **JPEG with 1 leading byte**, `a.dat` | 0 | **ESCAPED** |
| **zip-in-zip**: `outer.zip` > `inner.zip` > `a.png` | 0 | **ESCAPED**: members named `*.zip` are skipped and never recursed into |
| **a zip named `a.dat`** / **`trace.zip.bak`** holding `a.png` | 0 / 0 | **ESCAPED**: only `-name '*.zip'` is opened |
| **gzip** `a.png.gz`, `a.dat.gz`; **tar** `a.tar` | 0 / 0 / 0 | **ESCAPED** |
| **data-URI base64 PNG** in `error-context.md` | 0 | **ESCAPED** |
| **base64 PNG in `results.json` stdout** | 0 | **ESCAPED** |
| **`results.json` attachment typed `application/octet-stream`** with a base64 PNG body | 0 | **ESCAPED**: only `image/*` and `video/*` are checked |
| **SVG with an embedded raster** (`<image href="data:image/png;base64,…">`) | 0 | **ESCAPED** |
| **trace member with 1 leading byte** | 0 | **ESCAPED** |
| **BMP renamed `.dat`**, **TIFF `.tif`**, **ICO `.ico`** | 0 / 0 / 0 | **ESCAPED**: no BMP, TIFF or ICO signature; `.tif` and `.ico` are not in the name list |
| **symlink** `test-results/t1/s.dat` → a PNG outside the tree; **symlinked directory** | 0 / 0 | **ESCAPED**: `find -type f` skips links. The pinned `actions/upload-artifact@ea165f8…` (v4.6.2) uses `followSymbolicLinks = true` by default (`dist/upload/index.js:9721`, `:9770`), so the upload would carry the target's bytes |
| hex dump of a PNG in `a.txt` | 0 | ESCAPED |

**End to end, two routes that need no obfuscation step.**
- **An image inlined as a data URI in page content.** This is the shape a `next/image` `placeholder="blur"` or any inline image produces. A harness spec serves an HTML document with `<img src="data:image/png;base64,…">` through `page.route`, then fails.
  - The lane is red, and the gate prints **rc 0**, "no image or video is present". The upload would run.
  - The full PNG is recoverable byte for byte, as base64, from `trace.zip::1-trace.trace` (the DOM snapshot) and `trace.zip::resources/<sha1>.html` (the response body).
  - It is also in an attachment and in `error-context.md`, via the spec's own source frame.
  - The app renders no image today, so a normal red run carries none. From the first slice that inlines one, it will.
- **A file written after the gate.**
  - A harness spec starts a detached `sh -c 'sleep 20; cp <png> test-results/late.bin'`, with eslint 0, and fails.
  - The gate finishes at +11 s with rc 0.
  - At +24 s, `test-results/late.bin` is a PNG.
  - GitHub Actions kills orphan processes only at job end, and the upload step runs right after the gate. So this is a timing race the spec controls.

**How the gate's scope should be stated.** The gate is a strong control for what Playwright and Chromium write. That covers the recorder PNGs, WebMs and JPEG screencast frames, `page.screenshot`, `toHaveScreenshot`, `recordVideo`, and a fetched PNG, JPEG, GIF, WebP or MP4 resource: refused by name or by signature, in files and first-level `.zip` members. It is **not** a detector of "any image or video". A precise statement:

> The gate refuses the upload if a regular file under the uploaded directories, or a member of a `.zip` among them (one level), is named as an image or video (`.png .jpg .jpeg .webp .gif .avif .bmp .webm .mp4 .mov`), is a zip member whose path contains `screencast`, or begins with a PNG, JPEG, GIF, WebP, Matroska/WebM or ISO-BMFF signature; or if the JSON report types an attachment `image/*` or `video/*`. That covers everything Playwright's recorders and capture APIs write. It does not detect image data encoded as text (a `data:` URI or base64 — in a DOM snapshot, an HTML response in `resources/`, `results.json` or a log), SVG, BMP, TIFF, ICO or JPEG XL by content, archives nested in archives or not named `.zip`, gzip or tar streams, signatures not at byte 0, symbolic links (which the pinned upload action follows), or files written after it runs. It is a check on known shapes, not a proof that no pixels are present.

### G4. The docs under "no false-guarantee merges"

| Sentence at b68294b | Verdict |
|---|---|
| The upload table: `test-failed-1.png`, `video.webm`, "and any other image or video: **never uploaded** … if any image or video file, trace screencast frame or image resource is present, **whatever produced it**" | **False as written.** Data-URI images (measured end to end), other formats, encodings, nested or non-`.zip` archives, symlinks and post-gate writes are uploaded (G3) |
| § "What PR A still guarantees": "Images and video are NOT published: the gate refuses the upload (exit 4) if any image or video file … is present, whatever produced it" | **False as written**, same evidence |
| NOT-covered table: "DOM snapshots the trace viewer re-renders as the page's structure and text (**image bytes, whether fetched, screenshotted or recorded, are refused** at the upload gate)" and "a DOM snapshot … **with no image bytes behind it**" | **False** for inline (data-URI) images: the bytes are in `1-trace.trace` and `resources/*.html` after the gate |
| "It does not ask how the pixels were produced, so it holds for a recorder turned on by any spelling, for a spec that leaves the harness, and for a spec's own capture API" | True for what those produce: recorder output, `page.screenshot`, `toHaveScreenshot`, `recordVideo` and R-a are all caught, by signature or name. It would be accurate with "for the files those write" added |
| The runtime check: plain values only, N1 and N2 refused, stated as the early control with its in-process residual | **True, measured** (unit red on the old code, then green; runtime refused by name; 0 pixels) |
| "What this does NOT stop": R-a and spec capture APIs write pixels on the runner, and the gate refuses them in uploaded paths | True for the shapes they write. It omits G3's encoded, nested, symlinked and late shapes |
| "the app ships no raster image today, so a normal red run carries none" | True. It also means that from the first image slice, a red run that fetched any image will upload **nothing**, because the gate refuses the whole set. That diagnosability cost is implied, not stated |
| `--video` removed; "Playwright 1.63.0 has no `--video` flag" | True, measured |

### G5. Findings at b68294b

Earlier findings 1–8 are all closed in code. FINDINGS 6 and 7 are closed by the plain-value runtime check and the gate; FINDING 8 by the edit.

```
FINDING 9: The upload gate is documented as refusing "any image or video … whatever produced it"; it detects known file shapes, and pixels in other shapes are uploaded — including inline data-URI images, the shape a photo app's pages produce
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md (upload table row "never uploaded … whatever produced it"; § What PR A still guarantees "Images and video are NOT published"; NOT-covered row "image bytes, whether fetched, screenshotted or recorded, are refused"; "a DOM snapshot … with no image bytes behind it"), scripts/ci/redact-artifacts.sh (PIXEL_NAME_RE, pixel_magic, refuse_pixels `find -type f ! -name '*.zip'`, archives only `-name '*.zip'`)
  requirements: VZ-FOUND-008 (security seat Q3/F14)

Observed:
  End to end: a harness spec serving `<img src="data:image/png;base64,…">` and failing → gate rc 0 → full PNG byte-for-byte
  (as base64) in trace.zip::1-trace.trace and trace.zip::resources/<sha1>.html.
  A detached writer started by a spec lands a PNG in test-results/ 13 s after the gate returned 0.
  Fixture trees, gate rc 0: PNG/JPEG with 1 leading byte; zip-in-zip; zip named .dat / .zip.bak; .png.gz; .tar; base64 in
  error-context.md / results.json stdout / an octet-stream attachment; SVG with embedded raster; BMP/TIFF/ICO; symlinked
  file and directory (actions/upload-artifact v4.6.2 follows symlinks by default); hex dump.
  Caught, rc 4: named PNG, renamed PNG, extension-less and renamed trace members, deflated members, image/* attachment, R-a.

Failure:
  Three sentences promise that no image is published whatever produced it. The control is signature-based and first-level.
  Most escapes need deliberate encoding by spec code (the stated `run:` class), but the data-URI one needs only a page that
  inlines an image — a normal Next.js shape (blur placeholders), and the first image slice will produce it.

Perspective:
  operator | photographer

Recommendation:
  Docs (required): replace the three sentences with the scope statement in G3, and state the diagnosability consequence (once
  the app fetches any raster, a red run's upload is refused whole).
  Code (optional, small): also refuse any file or archive member containing `data:image/` or `data:video/` (zero hits in
  today's tree), recurse into nested archives or refuse them, and refuse symbolic links under the uploaded paths
  (`find -type l`). Post-gate writes are the `run:` class and belong in § Residuals.

Acceptance criteria:
  No sentence says "any image", "never uploaded" or "whatever produced it" unless each G3 case is refused; the data-URI
  end-to-end case is either refused (rc ≠ 0) or named as an uncovered channel in the NOT-covered table.

Tests:
  upload-gate-pixels.test.ts: add the data-URI-in-trace, symlink and nested-zip trees as refused cases if the code option is
  taken, or as named residual cases asserting rc 0 if only the docs change.

Cross-repo implications:
  core: none | user: this PR and PR B (Lane B's upload rides the same gate) | search: none | meta: none

Challenge:
  Q3 asked for the recorders off, asserted; that is delivered and then some, and every escape but one needs spec code that
  deliberately hides pixels — which a spec can always do. True; but the PR's contract text claims the stronger property,
  and the one escape that needs no intent is the one a photo site will hit first.
```

### Re-verification verdict

**What passed:**
- Every code finding from both earlier rounds is closed.
- The runtime check refuses N1 and N2, and the unit tests are red on the old code.
- The gate refuses every pixel file Playwright's recorders and capture APIs write, R-a included. D24 reproduces (170/0/0).
- The ledger change is exactly as stated.
- The lanes reproduce (660/0, 246/253/0, Lane A 18).
- CI is 8/8 green, with `ci-required` green and its manifest honest.

**Why it still fails:** AGENTS.md states the gate's scope as "any image or video … never uploaded … whatever produced it". That is a guarantee the gate does not provide. Measured end to end, an inline data-URI image survives the gate byte for byte in the trace, and so do several other shapes. The blocking item is a documentation change: the G3 scope statement plus the data-URI row. An optional ~10-line gate addition would close the data-URI and symlink cases. No other code change is required for Q3.

FINAL VERDICT: FAIL — SHA b68294b027965b6df57e3705d3b15631bafd4873

## Re-verification at 5c5c971

- **Verified SHA:** `5c5c971ea8980c1ae44a3716f2d0b73ee54fe50b`. It is two fast-forward commits on `b68294b`: `03baf75` (the gate additions, AGENTS.md, 9 unit cases, D25) and `5c5c971` (comment-only rescoping in `recorders.ts` and `test.ts`, with 12 digest lines).
- **Head:** confirmed with `gh api repos/yegamble/vizra-user/pulls/10` at the start and again at the end (`.head.sha`). It had not moved.
- **Verifier:** a fresh, independent verifier. I did not write this code or any earlier round of it.
- **Clone:** fresh, from GitHub, under the scratchpad (`vzv-user-pr10r3-XXXXXX`, via `mktemp -d`). A detached side worktree of the same clone was used for red/green runs and probes, so the demos run was never disturbed.
- **Environment:** Node 22.14.0 (nvm, matching `.nvmrc`), Playwright 1.63.0, Chromium from `npx playwright install`, Docker 29.8.0, macOS arm64 (Darwin 25.5). The userland is BSD: Info-ZIP Zip 3.0 and UnZip 6.00 (Apple builds) and perl 5.34.1. CI runs on GNU/ubuntu-24.04. Every escape below follows from the gate's own logic (which signatures and which arguments it reads), not from BSD behaviour.
- **Ports:** 3961 (Lane A), 3962 (canary), 3963/3964 (demos), 3965 (my probes).
- **Images:** `vzv-pr10r3-5c5c971:demonstrate` and `…:demonstrate-with-fixtures`. The pre-existing `vizra-user:demonstrate` image belongs to someone else and was not touched.
- **Cleanup:** see the end of this section.

### H1. Lanes

| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | 0 vulnerabilities |
| `npm run ci` | 0 | 21 files, **670 passed**, 0 skipped; hygiene: 340 sources, 25 digest lines match this tree |
| `bash scripts/ci/require-checks_test.sh` | 0 | 246 cases, 253 assertions, 0 failed |
| `bash scripts/ci/check-e2e-lane.sh .github/workflows/e2e.yml` | 0 | OK |
| `E2E_LOCAL_PORT=3961 npm run e2e` (Lane A) | 0 | **18 passed**; floor 9/9 and 9/9; 18 stamps |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | OK; 18 stamps verified |
| `E2E_LOCAL_PORT=3962 node scripts/ci/harness-canary.mjs` | 0 | all 4 fixtures failed, each with its exact kind set |
| `npm run e2e:demos` (`DEMO_PROD_PORT=3963 DEMO_DEV_PORT=3964 DEMO_IMAGE=vzv-pr10r3-5c5c971:demonstrate`) | 0 | **176 halves passed, 0 blocked, 0 failed**; all 15 D24 and 6 D25 halves `ok` |

No test was skipped in any lane.

### H2. Red/green: the 9 new unit cases, and D25

**The builder's unit claim, reproduced.**
- With `b68294b`'s gate (sha256 `97627fe1…`) copied over the head's, `npx vitest run e2e/harness/upload-gate-pixels.test.ts` exits 1: **9 failed / 7 passed**.
- All 9 failures are the 9 new cases. Each one is an assertion failure, not an error: "expected +0 to be 4" (the 4 data-URI cases) or "expected +0 to be 5" (the 5 exit-5 cases). The old gate exits 0 on every one of those trees.
- Restored (sha256 `bf820b0e…`, the committed file), the same file plus `redaction-corpus.test.ts` gives **162/162**.

**Each new branch is load-bearing.** I made seven mutations of my own to the head gate. Each one turns the unit file red, on the case that names it:

| Mutation | Result |
|---|---|
| `refuse_data_uris` returns 0 | 4 failed: all four data-URI cases |
| exemption applied to every root, not only `playwright-report` | 1 failed: "the HTML reporter's own viewer is the ONLY exemption" |
| `DATA_URI_RE` without `\\*` | 1 failed: the case/escape/video case |
| `grep` without `-i` | 1 failed: the same case |
| `archive_magic` returns 1 | 2 failed: nested archives, unopened archives |
| no `refuse_uninspectable … member` call | 2 failed: link inside a trace, nested archives |
| no `! -type f ! -type d` scan | 3 failed: all three link cases |

**D25, reproduced by me in the side worktree.** I extracted the D25 spec byte for byte from `demonstrate.sh` and ran it against a local production server with `PLAYWRIGHT_NO_COPY_PROMPT=1`, followed by the pinned gate command.

| Half | Spec | `data:image/` members in the traces | Gate | Upload |
|---|---|---|---|---|
| a, gate as committed | exit 1, 1 failed | 2 | **rc 4**, naming `1-trace.trace` and `resources/<sha1>.html`; no base64 in stdout or stderr | skipped: 0 uploaded |
| b, mutation `refuse_data_uris() { return 0` (sha256 `83a85e46…`, the ledger's D25b MUTATED) | exit 1 | 2 | rc 0 | **runs, and carries 2 members with the image** |
| c, restored (sha256 `bf820b0e…`, byte-identical to the commit) | exit 1 | 2 | rc 4 | skipped |

**The exemption, on a real red run.** A plain failing spec run under the main configuration, with the HTML reporter, writes `data:image/` only in `playwright-report/index.html` and `playwright-report/trace/assets/codeMirrorModule-*.js`. The gate passes it: **rc 0**. That reproduces the builder's measurement. So the exemption is what keeps an ordinary red run diagnosable.

### H3. The b68294b G3 escape table against the new gate

I rebuilt each G3 case as a fresh `test-results/` + `playwright-report/results.json` tree and ran the head gate with the pinned arguments.

| G3 case | rc now | Status |
|---|---|---|
| clean tree (inverse control) | 0 | passes, as it should |
| PNG with 1 leading byte, `a.dat` | 0 | listed as not detected ("a signature not at byte 0") |
| JPEG with 1 leading byte | 0 | listed, same bullet |
| zip-in-zip | **5** | refused |
| zip named `a.dat` / `trace.zip.bak` | **5 / 5** | refused |
| gzip `a.png.gz`, `a.dat.gz`; tar `a.tar` | **5 / 5 / 5** | refused |
| data-URI PNG in `error-context.md` | **4** | refused |
| base64 PNG in `results.json` stdout | 0 | listed ("base64 with no `data:` prefix") |
| `results.json` attachment typed `application/octet-stream` | 0 | listed |
| SVG with an embedded `data:image/png` raster | **4** | refused |
| trace member with 1 leading byte | 0 | listed ("a signature not at byte 0") |
| BMP bytes `.dat`, TIFF `.tif`, ICO `.ico` | 0 / 0 / 0 | listed |
| symlink to a PNG outside; symlinked directory | **5 / 5** | refused |
| hex dump | 0 | listed |
| end to end: an inline data-URI image (D25) | **4** | refused (H2) |
| a file written after the gate | n/a | listed (§ Residuals, the `run:` class) |

**Every G3 escape is now either refused or listed exactly under "What the gate refuses, exactly".** FINDING 9's acceptance criteria are met.

### H4. Attacking the new code

All fixtures were synthetic: a generated 1×1 PNG (70 bytes) and 16-byte header stubs. No safety classifier stopped anything, so there are no NOT RUN rows.

**Unrecognised archives and compressed streams.** Each held the synthetic PNG.

| Case | rc |
|---|---|
| lz4, brotli, `compress` (`.Z`, magic `1f9d`), lzma-alone, cpio (newc), `ar`, a zlib stream, raw deflate, each renamed `x.dat` at top level | **0** for all 8 |
| `.lz4`, `.Z`, `.lzma`, `.cpio`, `.ar` under their own names | **0** for all 5 (not in `ARCHIVE_NAME_RE`) |
| trace member `resources/77ab` holding a zlib stream, a cpio or an lz4 | **0** for all 3 (not refused as "an archive inside an archive") |
| stored zip with 1 leading byte, `a.dat`, at top level and as a trace member | **0 / 0** |
| v7 (pre-POSIX) tar with no name | 0 (this one is listed) |

**data: URIs that the literal does not match.**

| Case | rc |
|---|---|
| `data:application/octet-stream;base64,<PNG>` | **0** |
| `data:;base64,<PNG>` (no media type) | **0** |
| `data:ima\nge/png` (the URL parser strips the newline) | 0 |
| `data:image%2Fpng`, `data:image/png` | 0 / 0 |
| UTF-16LE `data:video/` | 0 |
| double-escaped `data:image\\\/png`, upper-case `DATA:IMAGE/` | **4 / 4** |

- **Chromium renders all of these as images.** I set `<img src=…>` with the synthetic PNG under `data:image/png`, `data:application/octet-stream`, `data:;base64` and `data:text/plain`, and got `naturalWidth` = 1 for every one.
- **End to end, through the harness.** A probe spec (scratch only, eslint 0) serves `<img src="data:application/octet-stream;base64,…">` and asserts `naturalWidth === 1`, which passes. It then fails on a heading.
  - The trace keeps the base64 PNG in `trace.zip::1-trace.trace` and `resources/<sha1>.html`.
  - The pinned gate prints OK, **rc 0**, and both members are still in the upload set.
- This is the shape `FileReader.readAsDataURL` produces for an untyped Blob, for example an upload preview.

**An uploaded path the gate never reads.** The upload's `path:` is `test-results/`, `playwright-report/results.json` and **`playwright-browsers.txt`**. The gate is run as `redact-artifacts.sh test-results playwright-report`, and `playwright-browsers.txt` is written by the record step, BEFORE the lane (`e2e.yml:85` against `:125`).
- A probe spec (eslint 0) copies the synthetic PNG over `playwright-browsers.txt`, then fails: the gate gives **rc 0**, and the file is a PNG.
- The same spec, replacing the file with a **symbolic link** to a PNG outside the tree: gate **rc 0**, and `file -L` reports a PNG. The pinned `upload-artifact` follows links (G3).

**The exemption.**

| Case | rc |
|---|---|
| exempt `playwright-report/index.html` and `trace/` | 0; they are not uploaded (the path allowlist, `check-e2e-lane.mjs:444`) |
| `playwright-report/Index.html`, `playwright-report/Trace/v.js` | 4 / 4 |
| `test-results/playwright-report/{index.html,trace/v.js}` | 4 (the root is `test-results`) |
| a hard link from the exempt `trace/` into `test-results/` | 4 |
| a symlink from `test-results/` into the exempt `trace/` | 5 |
| the argument `./playwright-report` | 0 (exempt, correctly) |
| the argument `playwright-report/` (trailing slash) | 4 on BSD `find` (`//` in paths), so it over-refuses and stays closed. The pinned step has no slash |

- `..` cannot occur, because the paths come from `find`.
- No spec output can reach the exempt paths AND the upload, because the upload never names them. **The exemption is sound.**

**Signatures, truncation, names, bounds.**
- A zero-byte file passes (0), as does a zero-byte or corrupt `x.zip` (0: removed with a warning, not uploaded).
- A 3-byte truncated PNG or zip signature passes (0). There is nothing to carry.
- A bare 2-byte `1f8b` is refused (5), which over-refuses and stays closed.
- A PNG named `a b⏎c.dat` or `x.png⏎`: 4. A link in a directory whose name holds a space and a newline: 5.
- A 150-deep tree with a PNG: 4.
- 2,000 small files: rc 0 in **253 s** on this machine, about 10 process spawns per file. The step has no timeout. A timeout would skip the upload, so this is closed but slow.

**Fail-closed.**

| Case | rc | Result |
|---|---|---|
| unreadable file (mode 000) holding a PNG | **2** | "a file this gate cannot read is not a clean file" |
| trace member extracted with mode 000 | **2** | closed |
| unreadable DIRECTORY (mode 000) holding `a.png` | **0** | "OK … no image or video is present". `find`'s EACCES is swallowed by every `< <(find …)` loop |
| read-only directory (555) holding `error-context.md` with `https://h.example/p?X-Amz-Signature=VZSECRET123` | **0** | the value survives: `perl -pi` prints "Can't do inplace edit" and exits 0, and `n=$(redact_tree …)` would hide a non-zero anyway. Pre-existing (redact_tree dates from `f49bca4`, #3) |

### H5. R1: absolute claims, judged by me

I grepped `5c5c971` outside `docs/evidence` for "any image", "never uploaded", "whatever produced", "refuses any", "holds regardless", "archive it does not open", "any archive", "whatever it is called", "of any kind", "unopened archive", "at any depth", "anywhere in what would be uploaded", "everything Playwright" and "image a page inlines". I also read the PR body and the builder's PR comment.

| Sentence | Verdict |
|---|---|
| AGENTS.md:822 "anything is a symbolic link or another non-regular file, at any depth, the named directory itself included" | True for the two named directories. The named directory is refused as `.` |
| AGENTS.md:826 "an archive is nested in an archive, **of any kind**, or an archive not named `.zip` … recognised by name or by a zip, gzip, bzip2, xz, zstd, 7z, rar or `ustar` signature" | **False as written.** cpio, lz4, zlib and friends are not refused (H4), and "of any kind" contradicts the list after it. The not-detected list names only the pre-POSIX tar |
| AGENTS.md:830-831 "That covers … **an image a page inlines as a `data:` URI**" | **False as written.** Only a URI typed `image/` or `video/` is refused. `data:application/octet-stream` and `data:;base64` render in Chromium and pass, end to end (H4). They are not in the not-detected list either: "base64 with no `data:` prefix" does not cover them |
| AGENTS.md:774 (upload table) "refuses the WHOLE upload … if **what would be uploaded** holds an image or video file … a symbolic link, or **an archive it does not open**" | **False** on two counts: `playwright-browsers.txt` is uploaded and never read (H4), and unrecognised archives |
| AGENTS.md:182 (COMMANDS) "REFUSE — exit 5 — a symbolic link or other non-regular file **anywhere in what would be uploaded**, an archive inside an archive, and an archive not named `.zip`" | **False**, same two counts |
| AGENTS.md:1062-1064 (§ What PR A still guarantees) "… a symbolic link, or **an archive it does not open**" | **False** for unrecognised archives |
| AGENTS.md:214 (`vizraWorkerGuard` row, from `b68294b`) "the upload gate is the one that **holds regardless**" | **Unscoped.** This is the exact phrase the chair's ruling had rescoped in `recorders.ts` and `test.ts`, and the builder's own grep for "holds regardless" missed it |
| `redact-artifacts.sh:216-219` "Images inlined as `data:` URIs, links and archives this script does not open are refused by the two gates after this one" | **False**: non-image-typed data URIs and unrecognised archives |
| `redact-artifacts.sh:353-358` "an ARCHIVE INSIDE AN ARCHIVE … refused … whatever it is called"; "**Any archive not named `*.zip` is refused.**" | **False** as written (H4) |
| `redact-artifacts.sh:417-418` "a link or an unopened archive **anywhere in what would be uploaded** refuses the whole set" | **False**: `playwright-browsers.txt`, and unrecognised archives |
| `redact-artifacts.sh:465`, the OK line: "… and **no link or unopened archive is present**" | **False** when it prints over a cpio, lz4 or zlib payload (H4) |
| `upload-gate-pixels.test.ts:261` "an archive inside an archive, **whatever its name or kind**, is refused" | **False**: the case tests zip, gzip and tar only |
| PR body, § "1. The control that holds regardless: the upload gate refuses pixels", and "The upload gate is the control that holds regardless" | **Unscoped, and live.** The body has no section at all for `03baf75` or `5c5c971`; the 03baf75 evidence exists only as a PR comment, and there is nothing for `5c5c971` |
| PR comment (03baf75): "An archive nested inside an archive." / "An archive not named `.zip`, found by name or by signature." | Overstated in the same way as AGENTS.md:826 |
| `recorders.ts:43-48`, `test.ts:148-151`, `playwright.config.ts:26-33,134` "refuses … in the shapes it knows" | **Accurate** |
| AGENTS.md:832-846, the not-detected list; :852-860, "The cost"; :872-877, D25; :963-969 | Accurate as far as they go; they are incomplete for the H4 shapes above |
| AGENTS.md:703 and `ci-environment.ts:94`, "layer 3 … holds regardless" (the page-snapshot gate, from #8) | Out of this slice. Noted only: a `# Page snapshot` inside a cpio or zlib payload would pass too |

### H6. The mutation-digests ledger

- `git diff 03baf75 5c5c971 -- …/mutation-digests.txt`: **exactly 12 lines changed**. They are the six `test.ts` lines (D13q BEFORE/RESTORED; D15i BEFORE/MUTATED/RESTORED; D15j RESTORED) and the six `recorders.ts` lines (D23b ×3; D24d BEFORE/MUTATED/RESTORED).
- **Every other line is byte-identical**, by position and by content. There are 32 lines, so **20** are unchanged, not the 17 the plan and brief state (NIT).
- The new hashes:
  - `6237e614…` is the sha256 of `test.ts` at 5c5c971;
  - `85d8d686…` is `recorders.ts` at 5c5c971;
  - `c8de74f9…` is `test.ts` with D15i's `perl` mutation applied, recomputed by me;
  - `eca56a69…` is `recorders.ts` with the D23b/D24d mutation applied, recomputed by me.
- `03baf75..5c5c971` changes code only inside comment blocks of those two files. The rest of the commit is evidence transcripts.
- After my own `npm run e2e:demos`, the regenerated `mutation-digests.txt` is **byte-identical** to the committed file (`git diff --quiet` exit 0), so every BEFORE/MUTATED/RESTORED hash, D24e and D25b included, is what the demonstrations produce on this tree.

### H7. CI on 5c5c971, read with my own `gh api`

- **`check-runs`:** `total_count` 8, all `completed/success` on `5c5c971`: ci-required, e2e, frontend, guard, contract, deps-scan, image-scan, GitGuardian.
- **Workflow runs**, all `pull_request`, attempt 1: ci-required 35928751782, e2e 35928751808, contract-ci, supply-chain, frontend-ci 35928927649, ci-guard.
- **`ci-required`** started 22:30:52Z and completed 22:34:49Z, after the last lane (guard, 22:34:45Z). Its log: "manifest .github/required-checks.txt … OK: every required check on 5c5c971… concluded success".
- **The manifest** is `frontend`, `contract`, `?guard`, `?docker-build`, `e2e`. The first four of those ran; `docker-build` is optional and was not triggered. No listed lane was left unexecuted.
- **frontend log:** 670 passed, with `upload-gate-pixels.test.ts` at 16 tests.
- **e2e log:** "18 passed", floor 9/9 and 9/9, 18 stamps, canary OK on all 4.
- The gate step itself did not run, because the lane was green. The unit file is what exercises it in CI.

### H8. R14, public-repo exposure of what the PR adds

- **Tokens:** a scan of every added line (`b68294b..5c5c971`) for `gh*_`, `github_pat_`, `AKIA`, PEM, `xox`, `sk-` found none.
- **Pixel data:** none, beyond the D25 spec's synthetic 1×1 PNG literal (70 bytes, generated) in `demonstrate.sh` and the unit test's 8-byte signature stubs. No transcript carries base64 image data: there is no run of 200 or more base64 characters.
- **Local paths:** the regenerated `d16d-*` transcripts carry `/var/folders/f0/<id>/T/tmp.*` temp paths. The same shape is on `main` and at `b68294b`, so this is pre-existing churn, not new here. There is no `/Users/`, user name or `/private/tmp`.
- **Out of scope, noted:** `e2e.yml`'s comment above the upload still says "`yegamble/vizra-user` is a PRIVATE repository". `gh api repos/yegamble/vizra-user` returns `visibility: public`.

### H9. Findings at 5c5c971

FINDING 9 is closed in code and in its acceptance criteria (H3, H2). The new text introduced new guarantees that the control does not keep.

```
FINDING 10: The archive refusal is documented as "of any kind" / "any archive not named .zip" / "no unopened archive is present"; it recognises eight signatures, and cpio, ar, lz4, brotli, .Z, lzma, zlib and raw-deflate payloads pass
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md:182, :774, :826, :1062-1064; scripts/ci/redact-artifacts.sh:216-219, :353-358, :365 (ARCHIVE_NAME_RE),
             :366-381 (archive_magic), :465 (OK line); e2e/harness/upload-gate-pixels.test.ts:261 (title)
  requirements: VZ-FOUND-008 (security seat Q3/F14)

Observed:
  With the pinned arguments, each tree holding the synthetic PNG: lz4, brotli, compress(.Z), lzma, cpio, ar, zlib, raw
  deflate renamed x.dat -> rc 0 (8/8); .lz4 .Z .lzma .cpio .ar under their own names -> rc 0 (5/5); a zlib, cpio or lz4
  payload as trace member resources/77ab -> rc 0 (3/3); a stored zip with one leading byte, top level and as a member ->
  rc 0. The OK line then says "no link or unopened archive is present".

Failure:
  The sentences promise that any archive the gate does not open is refused. It refuses archives it RECOGNISES. The
  "What the gate refuses, exactly" list names only the pre-POSIX tar as unrecognised, so a reader takes the rest as
  closed.

Perspective:
  operator | photographer

Recommendation:
  Docs (required): say "an archive recognised by name (list) or by signature (list)" everywhere, drop "of any kind",
  "whatever it is called", "any archive" and "no unopened archive"; add to the not-detected list: other archive and
  compression formats (cpio, ar, lz4, brotli, compress, lzma, zlib/deflate streams) and an archive signature not at byte 0.
  Code (optional): add the lz4 (04224d18), compress (1f9d), lzma (5d0000), cpio (070701/070707/c771), ar (!<arch>),
  zlib (78 01/5e/9c/da) signatures and names.

Acceptance criteria:
  No sentence in AGENTS.md, the script or the test titles says "any archive", "of any kind", "whatever it is called",
  "whatever its name or kind" or "no unopened archive" unless each case above exits non-zero; each case above is either
  refused or named in the not-detected list.

Tests:
  upload-gate-pixels.test.ts: if code: one tree per added signature, rc 5. If docs only: rename the test title to the
  kinds it builds (zip, gzip, tar).

Cross-repo implications:
  core: none | user: this PR (and PR B's upload rides the same gate) | search: none | meta: none

Challenge:
  Every one of these needs a spec to deliberately compress pixels in an odd format, which the `run:` class already
  admits. True; the finding is the sentence, and it is new in this round.
```

```
FINDING 11: "That covers … an image a page inlines as a data: URI" — only a data: URI typed image/ or video/ is refused; a page inlining a PNG as data:application/octet-stream (what FileReader.readAsDataURL gives an untyped Blob) renders, is kept by the trace, and passes
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md:830-831, :963-969, :986 (NOT-covered row "inlined as a data: URI"), :1063;
             scripts/ci/redact-artifacts.sh:216-219, :285-294, :309 (DATA_URI_RE)
  requirements: VZ-FOUND-008 (security seat Q3/F14)

Observed:
  Chromium 1.63.0's build: <img src="data:application/octet-stream;base64,<synthetic PNG>"> -> naturalWidth 1; same for
  "data:;base64," and "data:text/plain;base64,". End to end: a harness probe spec serving the octet-stream form, asserting
  naturalWidth === 1 (passes), then failing -> trace.zip::1-trace.trace and ::resources/<sha1>.html carry the base64 PNG
  -> pinned gate rc 0, "OK … no image or video is present in the shapes this gate reads" -> both members in the upload set.

Failure:
  The doc says the inlined-image route is covered. It is covered for one labelling of it. The octet-stream label is the
  natural output of reading an untyped File/Blob in the browser — an uploader preview in a photo app.

Perspective:
  photographer | operator

Recommendation:
  Docs (required): scope to "a data: URI typed image/* or video/*" and list "a data: URI with another or no media type,
  which Chromium still renders in an <img>" as not detected.
  Code (optional, small): also refuse `data:[^,]{0,100};base64,` followed by the base64 of a known signature
  (`iVBORw0KGgo` PNG, `/9j/` JPEG, `R0lGOD` GIF, `UklGR` RIFF, `GkXfo` WebM), any case.

Acceptance criteria:
  Either the octet-stream probe exits non-zero at the gate, or AGENTS.md no longer says the data-URI route is covered
  without the image/video qualifier, and names the other-typed form as not detected.

Tests:
  upload-gate-pixels.test.ts: a tree with `data:application/octet-stream;base64,<PNG b64>` in a trace member — rc 4 if
  the code option is taken, or a named residual case asserting rc 0.

Cross-repo implications:
  core: none | user: this PR; any future upload-preview slice | search: none | meta: none

Challenge:
  A server-rendered photo page would label its data URIs correctly; the untyped case needs a client-side preview. The
  first uploader slice is exactly that.
```

```
FINDING 12: playwright-browsers.txt is uploaded but never gated; a spec can replace it with PNG bytes or a link to one, and the gate prints OK
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     .github/workflows/e2e.yml:85-89 (record step, BEFORE the lane at :125), :191 (gate args), :243-246 (upload
             paths); AGENTS.md:182 ("anywhere in what would be uploaded"), :774 ("if what would be uploaded holds"), :777
             ("nothing sensitive"); scripts/ci/redact-artifacts.sh:417-418
  requirements: VZ-FOUND-008 (security seat Q3/F14)

Observed:
  Probe spec (eslint 0) `copyFileSync(<synthetic PNG>, "playwright-browsers.txt")`, then fails -> `redact-artifacts.sh
  test-results playwright-report` rc 0; `file playwright-browsers.txt` = PNG image data. Same spec with
  `symlinkSync(<PNG outside the tree>, "playwright-browsers.txt")` -> rc 0; the file is a link (the pinned upload action
  follows links).

Failure:
  Two sentences promise that the gate reads everything that would be uploaded; one of the three uploaded paths is outside
  it. "What the gate refuses, exactly" says "under the uploaded directories", which is accurate, but its residual line
  "anything outside the uploaded paths, which is not uploaded either" does not cover an uploaded path outside the gate.

Perspective:
  operator

Recommendation:
  Either gate the file (record the browser revision after the lane, or have the gate take the file as an argument and
  refuse a link / non-text there — a pinned-step change, with its pin), or scope both sentences to "under test-results/
  and playwright-report/" and name playwright-browsers.txt as ungated in the not-detected list.

Acceptance criteria:
  The two probe routes above exit non-zero at the gate, or no sentence says "what would be uploaded" for the gate's scope
  and the file is named as not read.

Tests:
  If code: upload-gate-pixels.test.ts (or a require-checks case) with playwright-browsers.txt as a link and as PNG bytes,
  refused. If docs: none beyond the wording.

Cross-repo implications:
  core: none | user: this PR and PR B | search: none | meta: none

Challenge:
  A spec that writes PNG bytes into a text file is deliberate, the same class as encoding pixels; the doc already
  concedes deliberate shapes. It concedes shapes it does not recognise; this is a recognised shape in a place it does
  not look, and the COMMANDS row says it looks everywhere.
```

```
FINDING 13: "The upload gate … holds regardless" survives in AGENTS.md:214 and in the live PR body; the PR body has no section for 03baf75 or 5c5c971
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md:214 (vizraWorkerGuard row: "the upload gate is the one that holds regardless"); PR #10 body
             § "1. The control that holds regardless: the upload gate refuses pixels" and "The upload gate is the control
             that holds regardless"
  requirements: VZ-FOUND-008

Observed:
  git grep -n 'holds regardless' 5c5c971 -- AGENTS.md -> :214 (added in b68294b) and :703 (page-snapshot layer, #8).
  The chair's ruling rescoped this exact phrase in recorders.ts and test.ts; the plan's grep lists "holds regardless" and
  reports only ci-environment.ts:94 among gate claims. The PR body was last written for b68294b; the 03baf75 summary is
  a PR comment, and 5c5c971 has none.

Failure:
  The fixture table and the PR description (the squash-merge text by default) still state the unscoped guarantee the
  round was opened to remove.

Perspective:
  operator | developer

Recommendation:
  Rescope AGENTS.md:214 as recorders.ts was ("the control that does not depend on how the pixels were produced, for the
  shapes it knows"); update the PR body with a 03baf75/5c5c971 section and rescope its § 1 heading and § 3 bullet.

Acceptance criteria:
  `git grep -n 'holds regardless'` shows no gate-for-pixels claim; the PR body describes the current head and uses the
  scoped wording.

Tests:
  none (wording). Note AGENTS.md is not in the digest ledger, so no ledger churn.

Cross-repo implications:
  core: none | user: this PR | search: none | meta: none

Challenge:
  The row points at § Artifact privacy, which is now scoped. A reader of the fixture table does not follow the pointer.
```

```
FINDING 14: The gate reports OK over what it could not read or could not rewrite: an unreadable directory (find errors swallowed) and a read-only directory (perl -pi exits 0 without redacting)
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/redact-artifacts.sh:162-167 (redact_tree), :458 (n=$(redact_tree …)), every `done < <(find …)`
             loop (:258, :275, :330, :392, :407, :454)
  requirements: VZ-FOUND-008 (sentinel R5)

Observed:
  test-results/t/locked (mode 000) holding a.png -> "find: Permission denied" ×N, rc 0, "OK … no image or video is
  present". test-results/t/ro (mode 555) holding error-context.md with `?X-Amz-Signature=VZSECRET123` -> "Can't do
  inplace edit … Permission denied", rc 0, value still present (count 1). `perl -0777 -pi` exits 0 on that error
  (measured). An unreadable FILE is correctly refused (rc 2).

Failure:
  Fail-open on error in the same script the upload trusts. The unreadable-directory case needs a later chmod to leak (the
  documented `run:` class), but the read-only case uploads an unredacted query string with no further step. The
  redact_tree half predates this PR (f49bca4, #3).

Perspective:
  operator

Recommendation:
  Collect `find` output into a file and check `find`'s status before the loop (or `wait $!` on the process
  substitution); make redact_tree verify each rewrite (perl `-i` with an explicit `open … or die`, or compare output) and
  run it outside `$(…)` so set -e applies.

Acceptance criteria:
  Both trees above exit non-zero; the 670-test suite and D-rows stay green.

Tests:
  upload-gate-pixels.test.ts or redaction-corpus.test.ts: a mode-000 directory and a mode-555 directory case, each
  expecting a non-zero exit (skip-proof: assert the chmod took effect first, since root ignores modes).

Cross-repo implications:
  core: none | user: this gate; register the redact_tree half with the sentinel if it is ruled out of this slice |
  search: none | meta: none

Challenge:
  A spec has to chmod its own output to reach either; that is deliberate. R5 says the check fails closed on the
  unreadable regardless of intent, and the new data-URI gate already does so for files.
```

```
FINDING 15: Bookkeeping: "17 lines byte-identical" is 20; environment.txt at 5c5c971 records head 03baf75
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user (and meta docs/plans/2026-09-23-user-pr10-close-gate-scope.md)
  files:     docs/evidence/VZ-FOUND-008/mutation-digests.txt (32 lines), docs/evidence/VZ-FOUND-008/environment.txt
  requirements: none

Observed:
  32 ledger lines, 12 changed, 20 identical (the invariant holds; the count is misstated). environment.txt: "head sha:
  03baf75…" in the 5c5c971 tree, because the demos ran on the uncommitted comment edits.

Failure:
  Evidence text disagrees with the evidence.

Perspective:
  developer

Recommendation:
  Say 20; note that the transcripts were generated on 03baf75 plus the uncommitted 5c5c971 edits.

Acceptance criteria:
  The numbers match the files.

Tests:
  none

Cross-repo implications:
  none

Challenge:
  Cosmetic. Recorded because R1 applies to evidence too.
```

### Re-verification verdict

**What passed:**
- The lanes reproduce: 670/0; 246/253/0; Lane A 18; floor and canary OK; demos 176/0/0.
- The 9 new unit cases are red on `b68294b`'s gate as assertion failures, and green on the head. Seven mutations of my own each turn a named case red.
- I reproduced D25a/b/c myself.
- Every G3 escape is refused or listed.
- The exemption is sound: exact, not reachable from the upload, and pinned.
- The 12-line ledger delta is exact, with 4 hashes recomputed by me.
- CI is 8/8 green on `5c5c971`, `ci-required` is green, and its manifest is honest.
- There are no tokens and no pixel data.

**Why it fails:** the gate got stronger, and the new sentences claim more than it does.
- It refuses the archives it recognises, but the docs, comments, test title and OK line say "any archive … of any kind" (FINDING 10).
- It refuses `data:image/` and `data:video/`, but the docs say it covers "an image a page inlines as a `data:` URI". The untyped form renders and passes, end to end (FINDING 11).
- It reads two of the three uploaded paths, but the docs say "anywhere in what would be uploaded" (FINDING 12).
- "Holds regardless" remains in AGENTS.md:214 and in the PR body, which also does not describe the current head (FINDING 13).

The blocking items are wording under R1, plus small optional code for 10 to 12. FINDING 14 is a fail-open worth scheduling; the `redact_tree` half predates this slice.

**Cleanup:** the probe specs were deleted from the side worktree; my image `vzv-pr10r3-5c5c971:demonstrate` was removed (the mutant image had already been removed by the script); ports 3961-3965 are free; the clone and worktree directory `vzv-user-pr10r3-*` is deleted after this file is written. Containers `vzv-pr15r1-*` and the image `vizra-user:demonstrate` belong to others and were not touched. Head re-checked at the end: `5c5c971ea8980c1ae44a3716f2d0b73ee54fe50b`, unchanged.

FINAL VERDICT: FAIL — SHA 5c5c971ea8980c1ae44a3716f2d0b73ee54fe50b
