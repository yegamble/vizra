# vizra-user PR #8 — closing slice — INDEPENDENT VERIFICATION (round 4)

- **Repo / PR:** `yegamble/vizra-user` #8, branch `fix/m0-artifact-privacy-a`
- **SHA verified:** `f0f702eb289f801d93e161717546762b5fa8d51c` (head confirmed with
  `gh pr view 8 -R yegamble/vizra-user --json headRefOid` at start: f0f702e…).
  Five commits on `11f8975`: `5225377 74ff2f7 fbae536 547ec56 f0f702e`.
- **Verifier:** fresh war-room independent verifier. I did not write this code and have
  not seen the builder's reasoning beyond the plan's "Closing slice" section. Read-only
  on every repository; the only file I write is this one.
- **Scope:** R3-FINDINGS H, I, J, K from the previous verifier's round at `11f8975`
  (`2026-09-21-vizra-user-pr8-artifact-privacy-a-VERIFY.md`), the builder's pinned-step
  design, the AGENTS.md prevents/detects table, and the stamp-key observation.
- **CI:** BLOCKED by billing per the chair; not re-run. Verdict is local.

## Environment

(written incrementally below)

```
macOS Darwin 25.5.0 arm64   node v22.14.0 (the .nvmrc pin, via nvm)   npm 10.9.2
@playwright/test 1.63.0     chromium-1243 / chromium_headless_shell-1243 (pre-installed cache)
host load 1/5/15 at start: 252 / 267 / 295 (other work on the machine)
fresh clone of github.com/yegamble/vizra-user, `git checkout f0f702eb289f…` (detached),
`npm ci` exit 0 — all under my private
…/scratchpad/vzv-vizra-user-pr8-TQSeo4/{repo,mut}. `mut/` is a copy of the tracked tree
(own throwaway git repo for restore) with node_modules symlinked to repo/.
```

## V1. Lanes at f0f702e, run by me

| Command (in `repo/`) | Exit | Result |
|---|---|---|
| `npm run ci` | 0 | eslint: no output (0 warnings); tsc 0; vitest **19 files / 624 tests passed, 0 skipped**; `next build` ok; hygiene `OK: 307 text source(s) … 17 mutation-digest line(s)` |
| `bash scripts/ci/require-checks_test.sh` | 0 | **219 cases, 226 assertions, 0 failed** |
| `bash scripts/ci/check-e2e-lane.sh` (in `mut/`, unmutated) | 0 | `OK: … redacts artifacts before EVERY upload step publishes them.` |

Builder's claims 624/0 and 219 reproduce exactly.

## V2. R3-FINDING H — the eight spellings and every pinned step, mutated by me

Driver: `mutate.py` (mine, scratch) applies ONE text mutation to `mut/.github/workflows/e2e.yml`
(or the pins file), runs `bash scripts/ci/check-e2e-lane.sh`, records exit + first refusal
line, then `git checkout -- .` and asserts `git status --porcelain` is empty. Baseline green
before and after each battery.

**The previous verifier's eight redaction spellings — all RED (exit 1), each by name.** Each
produces two lines: `no step runs \`bash scripts/ci/redact-artifacts.sh test-results
playwright-report\` exactly as pinned (redact-artifacts.sh) …` AND `job \`e2e\` step 13 (Redact
URL query strings in the artifacts) mentions \`redact-artifacts.sh\` but is not byte-equal to the
pinned \`redact\` step …: \`run\` differs — the redaction step's \`run:\` must be exactly …`.

| # | `run:` | Guard |
|---|---|---|
| H1 | `… test-results playwright-report \|\| true` | RED |
| H2 | `…; exit 0` | RED |
| H3 | `set +e; …; true` | RED |
| H4 | `… > /dev/null 2>&1 \|\| echo skipped` | RED |
| H5 | `… test-result playwright-reports` | RED |
| H6 | `… test-results` | RED |
| H7 | `… /tmp/empty` | RED |
| H8 | `echo redact-artifacts.sh` | RED |

**Per pinned step (9 roles).** All RED by name unless noted:

| Mutation | build_image | fixture_free | start_image | lane | floor | canary | record_browsers | redact | upload |
|---|---|---|---|---|---|---|---|---|---|
| one byte of the body | RED | RED | RED (`seq 1 31`) | RED (`npm run  e2e`, `npm run e2e;`; `E2E_BASE_URL …:3001`; one byte of `name`) | RED (`node  scripts/…`) | RED | RED | RED (`failure( )`) | RED (`retention-days: 2`) |
| extra key | RED `timeout-minutes` | RED `continue-on-error: false` | RED `shell` | RED `working-directory` | RED `if: success()` | RED `continue-on-error` | RED `if: always()` | RED `shell: bash {0}` | RED `continue-on-error` |
| reordered | RED (after lane) | RED (before build; after lane) | RED (after lane) | — | RED (before lane) | RED (before lane) | RED (after upload) | RED (before lane / floor / canary) | RED (before redact; not immediately after it) |
| laundered look-alike beside the real step | RED | RED | — | RED | RED | RED | RED | RED | RED (`someone/upload-artifact@<same sha>`) |
| exact byte-equal duplicate | RED | — | — | — | RED | RED | — | RED | RED |
| deleted | RED | RED | — | RED | RED | RED | — | RED | — |

(59 + 5 cases; 64 behaved as expected. Two of my first one-byte mutations — a TRAILING space
after `npm run e2e` and after the floor command — stayed green; that is correct: YAML strips
trailing whitespace from a plain scalar, so the parsed step, and what the runner executes, is
identical. Re-done with internal bytes, both RED. Recorded as a control, not a finding.)

## V3. The pins FILE, and the environment around the pinned bodies

**Pins file weakened together with the workflow — all RED by name (22/22):** redaction
`|| true`, `continue-on-error`, `if: always()`, renamed `id`; upload gate `always()` and bare
`failure()`; `playwright-report/` added to the upload paths; retention 14;
`if-no-files-found: warn`; `include-hidden-files: false` present; the uploader at `@v4`; lane
`npm run e2e || true`; lane env gaining `DEBUG`; lane URL on port 4000 while the container
publishes 3000; canary and floor `|| true`; fixture check `; exit 0`. Pin-only edits: one
byte of a pin's name RED; the `floor` pin deleted RED; an unknown pin role RED; a duplicate
key in the pins file exit 2 (BLOCKED — fails closed); `steps:` renamed RED.

**Environment (R3-FINDING K and the default-deny claim) — all RED:** `HOME` at workflow level, at
job level, on the unpinned `npm ci` step, on the pinned lane step, and lowercase `home` at
job level (default-deny). The job-level message names HOME twice: once in the default-deny
refusal and once in the dedicated "refused at every scope (R3-FINDING K)" line. Also RED:
`BASH_ENV` (workflow), `LD_PRELOAD` (job), `NODE_PATH` (unpinned step), `CI: ''` (job),
`PLAYWRIGHT_NO_COPY_PROMPT: ""` (job), `defaults:` at workflow and at job level, `services:`,
`strategy:`, `runs-on: ubuntu-latest`, job `permissions:`, and `$GITHUB_ENV` in an unpinned
`run:`. `env: {}` stays green, which is harmless.

**Green probes, classified.** These are things the pins do not pin:

| Probe (guard exit 0) | Classification |
|---|---|
| pin AND workflow for `record_browsers` both gain `uname -a >> playwright-browsers.txt` | **V-C (SHOULD).** `record_browsers` is the only pinned step whose output is uploaded from OUTSIDE the directories the redactor reads, and the pins file has no invariant for its `run:`. The pins-file header says "Weakening a pin here is therefore a named failure too". That holds for the pins listed in its invariant list, and not for this one. |
| pin AND workflow for `build_image` both gain `\|\| true` (the invariant is only `^docker build`) | fails closed: no image means the fixture check, the start step and the lane all fail. Not a finding |
| `actions/checkout` gains `with: ref: <other sha>` | the pinned bodies then run another tree. This is the stated "pinning fixes bytes, not what they run" class. The residual names `run:` steps; an allowlisted action's `with:` inputs are the same class. NIT |
| an unpinned `if: always()` step with no token between canary and redaction | the stated `run:` class |
| workflow-level `permissions: write-all` | outside artifact privacy; job-level `permissions:` is refused, but workflow level is not. NIT, observation only |
| `package.json` gains a ROOT `"postinstall"` (benign `echo`); the sibling `pree2e` is RED as a control | **V-B (SHOULD).** npm runs root install lifecycle scripts inside the unpinned `npm ci` step. So this is a `package.json` edit — the file FINDING 9 pinned — that runs arbitrary shell before every pinned step. That includes writing `$GITHUB_ENV` in text the `run:` scan never reads. `pre/post` hooks of `e2e*` are refused for exactly this reason; the root install hooks (`preinstall`, `install`, `postinstall`, `prepare`) are not. This repository declares none. |

## V4. R3-FINDING I — encoded separators, through the SHIPPED shell redactor

I minted a runtime marker (`openssl rand`) and fed the previous verifier's R3-6 surviving
shapes to `bash scripts/ci/redact-artifacts.sh`. The run printed `OK: redacted … in 1 file(s)`
and exited 0:

| Shape | Result |
|---|---|
| `/`-escaped slashes; `?` for `?`; `%2F` slashes; fully percent-encoded `https%3A%2F%2F…%3F…`; `\x2F`; `&#47;`; `&#x2F;`; `&sol;`; `&#63;` for `?`; `url:h.example:3000/p?q`; `GET:/p?q`; `a;/p?q` | **all redacted** |
| a query split by a line wrap inside one field | survives — **listed** in AGENTS.md's NOT-covered list |
| `//host?q` (no path) | redacted — listed as NOT covered, which is the safe direction |

`redaction-corpus.test.ts` runs inside `npm run ci` (624/624) and asserts byte equality of
both redactors over the 42-entry corpus. I checked the corpus diff: one expected output went
from a double to a single `<redacted>`, which is a correction and not a weakening. The
narrowed AGENTS.md sentence ("Any OTHER `\uXXXX` or `\xXX` escape may appear inside the host,
the path or the query — not in place of the separators listed here") matches what I
measured. **R3-FINDING I: closed.**

The script's new refusals, measured: a directory that does not exist exits **3**, with the
message "Nothing will be uploaded". A planted `# Page snapshot` line exits **1**.

## V5. R3-FINDING K — closed

HOME is refused at every scope, by name (V3). The residual bullet in AGENTS.md was updated
to match.

## V6. R3-FINDING J — capture, compare, restore

**What did NOT run, and why.** I began my own static probe of the new lint rule. A safety
classifier stopped my session partway through that line of work. Under the chair's rule I
recorded it and did not continue. **I rely on no result from it.** For the same reason I
authored **no** runtime probe of my own for J: no tamper variants, none for the four rows
the builder marked as reasoned, and no stamp-key read probe (V8). My evidence for J is the
code (read) plus the builder's committed D17a–e, re-run by `npm run e2e:demos` in my own
clone (V9).

**By reading `e2e/harness/ci-environment.ts`, `test.ts` and `stamp-reporter.ts` at f0f702e:**

- `CI` and `PLAYWRIGHT_NO_COPY_PROMPT` are captured once, at module evaluation. That module is
  imported by `playwright.config.ts` through `./e2e/harness/test`, so it is evaluated during
  configuration load in the main process and in each worker.
- The capture is frozen and module-private.
- `takeEnvironmentChange` compares the live values with the capture, restores them (deleting a
  key whose captured value was undefined), and returns a named message that echoes no value.
- The check points are: the stamp reporter's `onBegin` (main process); worker start;
  before each test; after the body; the end of the harness fixture; worker teardown.
  `check-e2e-lane.mjs` requires a genuine CALL of each check.
- **The previous verifier's two lines** now fail through the comparison. Deleting `CI` is
  itself the difference.
- `ci-environment.test.ts` pins that behaviour, including a record of the old silent
  behaviour. The two replaced assertions are carried over with the new explicit-capture
  signature, so none is weakened.

**Loader mode, read from the installed Playwright 1.63.0.**
`node_modules/playwright/lib/runner/index.js:6947-6952` shows that the CLI run uses
`createLoadTask("in-process", …)`, and `:2534` selects `InProcessLoaderHost` for it. So spec
module scope really does run in the MAIN process during collection, as the builder's
`stamp-reporter.ts` comment says. The `onBegin` check is placed on the right process.

**J: closed for the route the previous verifier used.** Remaining J-shaped over-claim: **V-A**,
below.

## V7. The prevents/detects table in AGENTS.md (§ Artifact privacy, layer 2) — sentence by sentence

| Row | Label in the doc | What I can say |
|---|---|---|
| module scope, main process during collection | prevents — measured, D17b | Placement confirmed by reading the loader mode (V6). D17b re-run: V9 |
| module scope, re-run when a worker loads the file | prevents — measured, D17b | the worker-start check runs before any hook or test; D17b re-run: V9 |
| test body | prevents — measured, D17e | V9 |
| `afterEach` / `beforeEach` | prevents — `afterEach` measured; `beforeEach` "by the measured fixture order, not separately" | Labelled honestly |
| `test.extend` fixture torn down before the harness fixture | prevents — measured, D17e | V9 |
| `beforeAll`, or late in the previous test | "prevents **for that test's context** — by construction, not separately measured" | Honest, and scoped to that test's context. A context `beforeAll` opens itself closes later, in `afterAll`, where the "detects only" row applies. The scoping sentence covers it. Not measured by me |
| page event handler "while the guard flushes" | prevents — by construction, not measured | Scoped to "while the guard flushes". A handler for an event that fires after the harness fixture's last check (during the close itself) is not in that window. The wording does not claim it. NIT: say so in one clause. Not measured by me |
| `afterAll`; teardown of an overridden `context`/`browser` | **detects only** — stated from fixture order and source, not measured | Honest label. The run fails at worker teardown, and layer 3 is what keeps the snapshot off the runner. Not measured by me |
| the spec closes its own context after an error | **detects only** — stated from source, not measured | Honest label. Not measured by me |

**Every row claims no more than its label, and the four reasoned rows say so in the row.**
The over-claim is not in the table. It is in the policy half of layer 2, and in two
residual sentences that lean on it. That is **V-A** below:

- AGENTS.md:680: the captured-value policy "is what catches a `.npmrc`, `NODE_OPTIONS` or
  `$GITHUB_ENV` route". The same paragraph conditions the policy on "`CI` set at capture".
- AGENTS.md:1207 (unchanged from 11f8975, kept through the J rework): "`$GITHUB_ENV` blanking
  `PLAYWRIGHT_NO_COPY_PROMPT` **by any route** is caught by the runtime assertion inside the
  Playwright worker".
- AGENTS.md:1214-1216 (**new in this PR**): user-level `.npmrc`, runner `NPM_CONFIG_*`, or a
  file a `run:` step writes into the home directory — "Any of them that blanks
  `PLAYWRIGHT_NO_COPY_PROMPT` before the configuration loads is caught by the runtime
  policy check".
- `ci-environment.ts:101-103`: "GitHub sets `CI` for every job, and the lane guard refuses the
  ways the workflow could take it away (`CI` in any env map, `$GITHUB_ENV`, …)". But the
  `$GITHUB_ENV` refusal is a text scan of `run:`, and AGENTS.md:1196-1203 already says it does
  not see a helper script.

`pageSnapshotProblem` starts `if (!env.CI) return undefined;` on the CAPTURED values. So any
pre-load route that empties `CI` as well as the variable leaves the policy silent. The
comparison is also silent, because live equals capture. This is R3-FINDING J's shape, moved
from after the capture to before it. Every route named in those sentences can set `CI` as
easily as it sets the variable. **Layer 3 is unaffected:** the redaction step is pinned (V2),
and its gate still refuses a page snapshot (V4). So this is an over-claim about layer 2, not
a live disclosure.

## V8. The builder's stamp-key observation — judged by reading, probe NOT RUN

- `e2e/harness/stamp.ts` (main-process branch): when `TEST_WORKER_INDEX` is unset, the
  module mints `VIZRA_E2E_STAMP_KEY` into `process.env` and leaves it there, "on purpose:
  that is how forked workers receive it".
- The installed Playwright 1.63.0 CLI run collects spec files with `InProcessLoaderHost`
  (`runner/index.js:2534`, `:6947-6952`). So spec module scope is evaluated IN that main
  process during collection, after `playwright.config.ts` has loaded, while the key is in
  its environment.
- The new lint rule allows exactly "reading one member" of `process.env` in a spec (its
  header says so). The runtime comparison watches only `CI` and `PLAYWRIGHT_NO_COPY_PROMPT`.
- **Judgement: by reading, the per-run key is readable from a spec's module scope in the
  main process.**
  - AGENTS.md:418 says "The key is not readable from a spec".
  - AGENTS.md:434 and `stamp.ts`'s "WHERE THE KEY LIVES, AND WHY A SPEC CANNOT READ IT"
    list only the worker's environment and the disk.
  - Those claims are stronger than the code supports.
- **Whether it is a working stamp FORGERY I did not establish.** That would also need a
  channel from the main process into a worker. I did not construct one, under the chair's
  constraint, and I authored no probe after the classifier stop (V6). The benign
  "is it defined" probe the chair allowed is therefore **NOT RUN**.
- **Scope.** The claim predates this PR: it came in with the stamp in PR #7 and is on
  `main`. It concerns harness-bypass detection, not artifact privacy. → **V-D** (REQUIRED as
  a follow-up; not a blocker of this PR).

## V9. The builder's remaining lanes, reproduced in my clone

| Command | Exit | Result |
|---|---|---|
| `CI=1 PLAYWRIGHT_NO_COPY_PROMPT=1 npx playwright test` (local production server) | 0 | **18 passed**; `e2e coverage floor: OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9)`; `e2e harness stamp: OK (18 …)` |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | floor OK 9/9 9/9; 18 stamps verified from `.vizra-e2e/stamp-key.json` |
| `CI=1 PLAYWRIGHT_NO_COPY_PROMPT=1 node scripts/ci/harness-canary.mjs` | 0 | "failed all 4 fault-injection fixtures, each with the exact set of record kinds it demonstrates" |
| `bash scripts/ci/check-required-floor.sh` / `check-image-pins.sh` / `npm run check:contract` | 0 / 0 / 0 | — |
| `INTERNAL_API_BASE_URL=http://api.sentinel.invalid:8080 PUBLIC_ORIGIN=http://127.0.0.1:3291 npm run build`, then `DEMO_PROD_PORT=3291 DEMO_DEV_PORT=3292 DEMO_IMAGE=vzv-pr8r4:demonstrate DEMO_MUTANT_IMAGE=vzv-pr8r4:demonstrate-mutant npm run e2e:demos` | 0 | **148 passed / 0 blocked / 0 failed**, from 10:25:25Z to 10:49:32Z UTC, with load (1/5/15) ranging from 17/49/146 to 216/203/161. `OK: every demonstration that ran went red on the mutation and green on restore.` The `mutation-digests.txt` it wrote is **byte-identical** to the committed one (`git diff --quiet`). The transcripts differ only because I used my own ports and different timings |

The J demonstrations re-ran, each passing its half:

- D17a: `vizra/no-process-env-write` refuses the two lines.
- D17b: RED, `page-snapshot environment was CHANGED`; GREEN, `heading in the upload set: 0`.
- D17c: the laundered redaction step is refused by the lane guard (RED). Run as the runner
  would run it, it reports success anyway (GREEN), and the combined attack's upload set holds
  no page snapshot (GREEN).
- D17d: the controlled mutation that switches the comparison off brings the page snapshot
  back, with the typed value, in three halves (RED).
- D17e: the body, `afterEach`, and `test.extend` fixture-teardown routes are each refused
  (RED), and each leaves no page snapshot in the upload set (GREEN).
- The earlier demonstrations still pass: D16a–d, and D7b.

**Two notes on these demonstrations.**

- D7b's former GREEN half ("a second correctly gated upload passes") is now a RED half,
  `d7b-second-gated-upload-refused-by-the-pin-RED`. The matching `require-checks_test.sh`
  case was inverted too. **The inversion is justified.** It TIGHTENS the check: a second
  uploader changes what leaves the runner, so it belongs in the reviewed pin. The GREEN
  controls that remain are `d7-lane-guard-GREEN` and require-checks case 1 ("the committed
  e2e workflow passes its own guard"), and they still prove the guard is not red on
  everything. No assertion was weakened.
- **CI on f0f702e (read with `gh api …/commits/f0f702e…/check-runs`).** Every Actions check
  (`e2e`, `ci-required`, `frontend`, `contract`, `guard`, `docker-build`, `deps-scan`,
  `image-scan`) is `completed/failure`, started 10:03:56Z and done 10:03:59Z, each with one
  annotation: "The job was not started because recent account payments have failed or your
  spending limit needs to be increased". GitGuardian: success. **CI is BLOCKED, not
  failed-on-merit and not passed.** I did not re-run it.

## V10. Diff audit against AGENTS.md's review rules (11f8975..f0f702e, 109 files)

- **Weakened or deleted assertions.** None found.
  - The removed lines in the tests are two `assertPageSnapshotSuppressed` assertions,
    re-expressed with an explicit capture argument; each keeps the same expectation.
  - One `redaction-corpus.json` expectation moved from a doubled to a single `<redacted>`.
    That follows from the new idempotence (a correction).
  - `require-checks_test.sh` lost one GREEN case, which became RED on purpose (V9 note), and
    gained 37 cases.
- **Skips.** No `.skip`, `.fixme`, `.only` or `it.todo` was added, and no `eslint-disable`.
  vitest reports 0 skipped.
- **Credentials and private data.**
  - No credential-shaped string in any added line: I searched for `ghp_`, `github_pat_`,
    `AKIA…`, `-----BEGIN`, JWT and `X-Amz-Signature` shapes.
  - No local home path, private tmp path or e-mail address in any added line under
    `docs/evidence/`.
  - Runtime failure messages name keys as set/unset/changed and never echo values
    (`takeEnvironmentChange`, `pageSnapshotProblem`).
- **Generated files.** None touched: no `contracts/`, no OpenAPI and no codegen output in the
  diff. `package.json` and `package-lock.json` are unchanged.
- **Fake success.** None found.
  - The guard's OK line is printed only when `problems` is empty.
  - The redactor's missing-directory path exits 3 with "Nothing will be uploaded".
  - `redact-artifacts.sh`'s gate exits 1 on a page snapshot (V4).
- **Unbounded resources.** R3-I added a linearity bound. The PR states that a 240 KB line took
  25 s on the old boundary, and a corpus test bounds it; that test is inside `npm run ci`
  (624/624). I did not re-time it.

## Status of the round-3 findings at f0f702e

| # | Round-3 finding | At f0f702e |
|---|---|---|
| H (BLOCKER) | the redaction step was recognised by a substring | **closed.** All 8 spellings are RED by name; every pinned step is RED under a one-byte change, an extra key, a reorder, a look-alike and an exact duplicate; weakening the pins file together with the workflow is RED (V2, V3); D17c re-ran |
| J (REQUIRED) | layer 2 was off when `CI` was unset, and a spec could unset it | **closed for the spec routes** (capture, compare, restore; D17b/e re-ran; lint D17a). A pre-capture residue remains in the docs: **V-A** |
| I (SHOULD) | the `\uXXXX` sentence was broader than the programs | **closed** (V4) |
| K (NIT) | `HOME` was not refused | **closed** (V3) |

## Findings at f0f702e

```
FINDING V-A: layer 2's policy is keyed on `CI` AS CAPTURED, so a route that empties `CI`
             before the configuration loads switches it off. Three sentences still say
             such routes are "caught"
Severity:    REQUIRED
Confidence:  high on the code; medium on the platform half (see UNVERIFIED)

Affected:
  repo:      vizra-user
  files:     e2e/harness/ci-environment.ts `pageSnapshotProblem` (`if (!env.CI) return undefined;`,
             judged on CAPTURED); ci-environment.ts:101-103 ("GitHub sets `CI` for every job, and
             the lane guard refuses the ways the workflow could take it away (… `$GITHUB_ENV` …)")
             AGENTS.md:680 ("which is what catches a `.npmrc`, `NODE_OPTIONS` or `$GITHUB_ENV` route")
             AGENTS.md:1207 ("`$GITHUB_ENV` blanking `PLAYWRIGHT_NO_COPY_PROMPT` by any route is
             caught by the runtime assertion"; kept from 11f8975 through the J rework)
             AGENTS.md:1214-1216 (NEW in this PR: "Any of them that blanks
             `PLAYWRIGHT_NO_COPY_PROMPT` before the configuration loads is caught by the runtime
             policy check")
  requirements: VZ-FOUND-008

Observed:
  The capture is taken from whatever environment the Playwright process starts with. The
  policy applies only when the captured `CI` is truthy; the comparison fires only on a change
  AFTER the capture. So an environment that arrives with `CI` empty and the variable empty
  passes both. The routes those sentences name can set `CI` as easily as the variable: a
  `$GITHUB_ENV` write from a helper script (AGENTS.md:1196-1203 already says the static scan
  does not see one), a user-level npmrc, or a root install lifecycle hook (V-B). In a worker,
  the capture is also taken from the environment the worker inherits at fork, after spec
  module scope has run in the main process. That is the same keying, reasoned from the code
  and not measured.
  UNVERIFIED: that GitHub Actions honours `CI=` (empty) written to `$GITHUB_ENV`. Actions is
  BLOCKED by billing; D16c, the builder's own demonstration, simulates `$GITHUB_ENV` the same
  way, as the environment the process starts with.

Failure:
  The docs tell a reviewer that layer 2 catches these routes "by any route". It does not
  when the same route also empties `CI`. That is R3-FINDING J's shape, moved from after the
  capture to before it. The OUTCOME is still protected: the redaction step is now pinned
  (V2), and its gate refuses any `# Page snapshot` (V4, D17c). So this is a false guarantee
  about one layer, not a live disclosure.

Perspective: developer (the reviewer who trusts the sentence), then member from M1

Recommendation (smallest):
  Either narrow the three sentences and the ci-environment.ts comment to "…caught unless the
  same route also empties `CI`, in which case layer 3 alone holds", or anchor the policy on a
  variable a job cannot overwrite. GitHub documents that `GITHUB_*` defaults cannot be
  overwritten through `$GITHUB_ENV`; verify that before relying on it. For example, apply the
  policy when `CI` OR `GITHUB_ACTIONS === "true"` was set at capture.

Acceptance criteria:
  A test runs the policy with a captured `{ CI: "", PLAYWRIGHT_NO_COPY_PROMPT: "" }` (plus the
  chosen anchor) and it fails by name. Or: no AGENTS.md / ci-environment.ts sentence claims
  that layer 2 catches a pre-load route that also empties `CI`.
Tests: e2e/harness/ci-environment.test.ts (one case); D16c gains an "`CI` emptied too" half.
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge: "Layer 3 catches it, so the sentence is harmless." That is the argument R3-FINDING
  H disproved one round ago. Defence in depth is only real if each layer is described at its
  own strength.
```

```
FINDING V-B: root npm install lifecycle scripts are not refused, although `pre/post` hooks
             of `e2e*` are
Severity:    SHOULD
Confidence:  high
Affected: vizra-user; scripts/ci/check-e2e-lane.mjs REQUIRED_SCRIPTS / hook loop; AGENTS.md
  residual "Pinning a step fixes its BYTES…" (names "an earlier `run:` step … e.g. `npm ci`'s
  neighbours", not `npm ci`'s own lifecycle)
Observed: `"postinstall": "echo hello"` added to package.json → `check-e2e-lane.sh` exit 0.
  The control `"pree2e": "echo hello"` → RED. npm runs the root package's
  preinstall/install/postinstall/prepare during `npm ci`, the unpinned step before every
  pinned one. So a package.json edit, in the file FINDING 9 pinned, runs arbitrary shell
  there, including a `$GITHUB_ENV` write that the `run:` text scan never reads.
Failure: this is the stated class (workspace rewritten before the pinned bodies), reached
  through a file the guard already parses and a key the residual does not name.
Recommendation: refuse `preinstall`, `install`, `postinstall`, `prepare` (and their
  pre/post forms) in the same loop that refuses `pree2e`; this repository declares none.
  Or name them in the residual.
Acceptance: require-checks case, `postinstall` → RED by name.
```

```
FINDING V-C: the `record_browsers` pin has no invariant, and its output is uploaded
             un-redacted
Severity:    SHOULD
Confidence:  high
Affected: vizra-user; scripts/ci/check-e2e-lane.mjs pins-file invariants (exact `run:` only
  for lane, floor, canary, fixture_free, redact); .github/e2e-pinned-steps.yml header
  ("Weakening a pin here is therefore a named failure too"; record_browsers comment "the step
  that writes it is pinned and no other step may name it")
Observed: the pin AND the workflow both gain `uname -a >> playwright-browsers.txt`
  → guard exit 0. `playwright-browsers.txt` is on the upload allowlist and outside both
  directories `redact-artifacts.sh` reads.
Failure: "weakening a pin is a named failure" holds for the listed pins, not this one — the
  one pinned step whose output bypasses redaction.
Recommendation: assert its exact `run:` on the pins file like the other literal commands
  (it is a fixed three-line body), or narrow the header sentence to the listed pins.
Acceptance: require-checks case, pin+workflow change to record_browsers → RED.
```

```
FINDING V-D: "The key is not readable from a spec" — by reading, it is readable at spec
             module scope in the Playwright MAIN process during collection
Severity:    REQUIRED (as a follow-up; pre-existing on main since PR #7; not a blocker of THIS PR)
Confidence:  medium (code read; the chair's benign read-only probe was NOT RUN, see V6/V8)
Affected: vizra-user; e2e/harness/stamp.ts (main-process branch keeps VIZRA_E2E_STAMP_KEY in
  process.env; header "WHY A SPEC CANNOT READ IT"); AGENTS.md:418, :434
Observed: Playwright 1.63.0's CLI run collects spec files in-process
  (runner/index.js:2534, :6947-6952), after config load, while the key sits in
  process.env. `vizra/no-process-env-write` allows reading one member.
Failure: the stated forgery analysis lists only the worker's environment and the disk. It
  is silent on the main process, where the builder's own reporter comment places spec
  collection. Whether that yields a working forgery (it would also need a main→worker
  channel) was not established.
Recommendation: state it in AGENTS.md § the stamp and in stamp.ts. As a follow-up, either
  have workers receive the key through a channel spec code cannot read during collection,
  or delete it from the main process's environment once workers have it and re-verify.
Acceptance: the doc sentence matches the code, and a follow-up ledger item exists.
```

```
FINDING V-E (NIT): allowlisted actions' `with:` inputs are unconstrained. `actions/checkout`
  with `ref: <another sha>` is guard-green, and the pinned bodies then run a different tree.
  This is the same class as the "pinning fixes bytes, not what they run" residual; name it
  there. Workflow-level `permissions: write-all` is also green (job level is refused).
  That is outside artifact privacy; noted only.
FINDING V-F (NIT): the "page event handler" row could say, in one clause, that a handler for
  an event that fires during the context close itself is outside the window.
```

## V11. Per-commit truth

I made a `git worktree` at each commit inside my scratch directory, with node_modules
symlinked, and ran `npm run ci` there:

| Commit | lint | tsc | vitest (files / tests / skipped) | hygiene | builder's claim (files / tests) |
|---|---|---|---|---|---|
| `5225377` | 0 | 0 | 18 / 529 / 0 | OK — 290 sources / 13 lines | 18 / 529 |
| `74ff2f7` | 0 | 0 | 19 / 572 / 0 | OK — 292 / 13 | 19 / 572 |
| `fbae536` | 0 | 0 | 19 / 624 / 0 | OK — 292 / 13 | 19 / 624 |
| `547ec56` | 0 | 0 | 19 / 624 / 0 | OK — 292 / 17 | 19 / 624 |

The `next build` step failed in these worktrees with `TurbopackInternalError: Symlink
[project]/node_modules is invalid, it points out of the filesystem root`. That is an artifact
of MY symlinked node_modules, not of the code. The full `npm run ci`, build included, is
green at the head in a real `npm ci` tree (V1). No commit touches `app/`, `lib/`, `next.config.ts`
or the lockfile. The build at the intermediate commits is therefore **NOT RUN by me**; every
other lane matches the builder's counts exactly.

## Head, end of run

`gh pr view 8 … headRefOid` and `git ls-remote … refs/heads/fix/m0-artifact-privacy-a` both
report `f0f702eb289f801d93e161717546762b5fa8d51c`. The head is unmoved.

## What I did NOT verify

- **GitHub CI:** BLOCKED by billing (V9). The pinned workflow has never run on Actions, and
  no RED CI run has ever exercised the upload path of this PR.
- **My own runtime probes:** NOT RUN after a safety-classifier stop (V6). Specifically:
  - J tamper variants of my own;
  - the four reasoned rows of the table;
  - the stamp-key "is it defined" probe;
  - V-A on a runtime.

  V-A and V-D rest on code reading. V-A's new sentence (AGENTS.md:1214-1216) is falsified
  by the code for the npmrc route independently of how GitHub treats `$GITHUB_ENV`: npm's
  `node-options` reaches `NODE_OPTIONS`, which can set `CI` like any other variable.
- **The platform half of V-A:** whether Actions honours an empty `CI` written to `$GITHUB_ENV`.
- **The build step at the four intermediate commits** (V11).
- **Platform:** macOS arm64 only; ADR-009's acceptance platform is ubuntu-24.04 amd64.

## Cleanup

- Removed image `vzv-pr8r4:demonstrate`. The script removes the mutant image itself; I
  confirmed no `vzv-pr8r4` image remains.
- I started no container of my own; the demo suite stops its own.
- The worktrees were removed and pruned.
- The scratch directory `…/scratchpad/vzv-vizra-user-pr8-TQSeo4` is deleted by exact path
  at the end.
- Nothing was pushed, edited in the PR, merged or approved.
- **Instruction-shaped text seen in tool output:** none.

## Verdict

This closing slice does what it set out to do for the class it was dispatched on:

- **R3-FINDING H is closed by construction.** Every one of the previous verifier's eight
  spellings is refused by name. Every pinned step goes red under a one-byte change, an extra
  key, a reorder, a look-alike and an exact duplicate. Weakening a pin together with its
  workflow step is refused for every pin that carries an invariant.
- **I and K are closed.**
- **J is closed for the spec routes** the previous verifier used, with capture, compare and
  restore demonstrated end to end.
- **The builder's local numbers reproduce exactly:**
  - `npm run ci` 624/0;
  - require-checks 219;
  - Playwright 18, with floor and stamps;
  - canary 4/4;
  - `e2e:demos` **148/0/0**, with a byte-identical digest ledger;
  - the per-commit counts.
- The prevents/detects table labels its four reasoned rows honestly.

It does not meet the chair's "no false-guarantee merges" rule. **V-A (REQUIRED):** three
AGENTS.md sentences, one of them new in this PR, and one `ci-environment.ts` comment say that
layer 2 catches routes that act before the configuration loads — "by any route". The policy
is keyed on `CI` as captured, so any such route that also empties `CI` is caught by nothing
in layer 2. That is J's shape, one step earlier.

Nothing leaks as a result: the pinned redaction step and its page-snapshot gate hold. The
fix is a sentence, or one anchor condition and one test. Also open:

- **V-B** (root install hooks) and **V-C** (the `record_browsers` pin has no invariant):
  SHOULD.
- **V-D** (the stamp key is readable in the main process during collection): REQUIRED as a
  follow-up. It is pre-existing on main and not this PR's to block, but the chair should
  route it.
- **V-E and V-F:** NITs.

FINAL VERDICT: FAIL — SHA f0f702eb289f801d93e161717546762b5fa8d51c
