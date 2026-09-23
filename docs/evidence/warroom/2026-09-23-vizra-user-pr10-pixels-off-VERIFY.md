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
