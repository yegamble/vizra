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

---

# Re-verification at `f6d245f` (2026-09-23) — closing slice, fix round 1 of 2

- **SHA verified:** `f6d245f6076b8641cf360ae30a7af1cc8ce00c03` (`gh pr view 8 … headRefOid`
  at start). A fast-forward from `f0f702e`: `git merge-base --is-ancestor f0f702e HEAD` holds.
  Two commits: `4db7dce` (the fix) and `f6d245f` (transcripts). 30 files, +1664 −986.
- **Environment:** as above; a NEW private clone under
  `…/scratchpad/vzv-vizra-user-pr8r5-OvbNMq/{repo,mut}`; `npm ci` exit 0. Load 1/5/15 at start:
  165 / 167 / 139.
- **Classifier:** no stop in this round. Every probe below is either an environment passed
  to the unmodified lane (the same simulation as the builder's D16c) or a byte or file
  mutation of the workflow, the pins file, `package.json` and the harness file.

## R5-1. Lanes

| Command | Exit | Result |
|---|---|---|
| `npm run ci` | 0 | lint 0; tsc 0; **19 files / 627 tests / 0 skipped**; build ok; hygiene `OK: 308 text source(s) … 17 mutation-digest line(s)` |
| `bash scripts/ci/require-checks_test.sh` | 0 | **233 cases, 240 assertions, 0 failed** |
| `CI=1 PLAYWRIGHT_NO_COPY_PROMPT=1 npx playwright test` | 0 | 18 passed; floor 9/9 9/9; 18 stamps |

## R5-2. V-A — red/green, with the pre-fix harness checked out for the red half

The lane was run unmodified under the environment the route produces:
`env -u GITHUB_ACTIONS CI= GITHUB_ACTIONS=true PLAYWRIGHT_NO_COPY_PROMPT= npx playwright test`
(local production server).

| Harness | Exit | Result |
|---|---|---|
| `f6d245f` (new) | **1** | **18 failed**, 18 lines `PLAYWRIGHT_NO_COPY_PROMPT is not "1" …` |
| `f0f702e`'s `ci-environment.ts` checked out over it | **0** | **18 passed**, 0 policy lines — the V-A hole, measured |
| restored (`git status` clean), again | **1** | 18 failed |

Unit tests, `npx vitest run e2e/harness/ci-environment.test.ts`:

- **Old harness: 2 failed / 17 passed.** The two failures are the V-A policy case and the
  "deleting `GITHUB_ACTIONS` is a named change" case. The inverse control passes on both
  harnesses, as it should.
- **New harness: 19/19.**

The builder's "red 2/3, green after" reproduces.

## R5-3. The GitHub documentation quotations — fetched myself (`curl`, HTTP 200, 2026-09-23)

| Quoted in `ci-environment.ts` / AGENTS.md | Page | On the page? |
|---|---|---|
| "Currently you can overwrite the value of the `CI` variable" | `docs.github.com/en/actions/reference/workflows-and-actions/variables` AND `…/workflow-commands` | **verbatim**, followed on both pages by "However, it's not guaranteed that this will always be possible." |
| "You can't overwrite the value of the default environment variables named `GITHUB_*` and `RUNNER_*`" | both pages | **verbatim** |
| an `env:` assignment to a default name "is ignored" | variables page: "If you attempt to override the value of one of these default variables, the assignment is ignored." | **verbatim** |
| (context) `GITHUB_ACTIONS` | variables page: "Always set to `true` when GitHub Actions is running the workflow." | matches the `=== "true"` anchor |
| (context, not quoted by the builder) | workflow-commands page: "Due to security restrictions, GITHUB_ENV cannot be used to set the NODE_OPTIONS environment variable." | the ONLY name GitHub documents as blocked in `$GITHUB_ENV` |

**Is the anchor sound as stated?** It is sound against what the pages say: `env:` and a
`$GITHUB_ENV` write of `GITHUB_ACTIONS` itself. It is NOT sound against everything the new
sentences say. See **R5-FINDING V-A2** (R5-6).

## R5-4. New invariants, mutated by me (`mut/`, one mutation at a time, restored, baseline green before and after)

**33 of 33 cases behaved as expected.** Each RED case matched the finding's own name in the
refusal line:

- **V-B.** Each root hook added to `package.json` scripts as `echo hi` is RED by name
  (`package.json declares \`scripts.<hook>\` … during \`npm ci\``): `preinstall`, `install`,
  `postinstall`, `prepublish`, `preprepare`, `prepare`, `postprepare`, `dependencies`.
  Inverse control: an unrelated `hello` script stays GREEN.
- **V-C.** The pin AND the workflow edited together are RED (`record_browsers` pin must run
  exactly …) for:
  - `uname -a >> playwright-browsers.txt` appended;
  - one byte (`--versiom`);
  - `set -eu` (pipefail dropped).
- **V-E `with:`.** RED:
  - `actions/checkout` with `ref:` added, with `persist-credentials: true`, with `path:`
    added, with the whole `with:` removed, or with `persist-credentials: 'false'` as a string
    (fails closed);
  - `actions/setup-node` with `node-version: 20`, or with an extra `registry-url`.
- **V-E `permissions:`.** RED at workflow level for `write-all`, for `contents: write`, for
  an added `id-token: write`, and for `permissions:` removed. Job-level `permissions:` is
  still RED.
- **Regressions.** Still RED:
  - pin + workflow weakened together: redaction `|| true`, upload gate `always()`,
    lane `|| true`;
  - the H spellings `|| true`, `; exit 0` and `echo redact-artifacts.sh`;
  - `HOME` at job level;
  - `pree2e`.

`require-checks_test.sh` carries the builder's 13 new cases (V-B ×8 + inverse, V-C,
V-E ×4); the run above is green with all of them.

## R5-5. Every changed sentence, against "no false-guarantee merges"

I compared the builder's before/after list (`closing-pr8-fzNI/sentences.md`) with
`git diff -U0 f0f702e HEAD -- AGENTS.md` and the diffs of `ci-environment.ts`, `stamp.ts` and
the pins-file header. The list is complete for AGENTS.md. The code-comment changes in
`ci-environment.ts` and `stamp.ts` and the pins-file header are not on it; I read them too.

| Sentence | Verdict |
|---|---|
| Commands table: the new clauses (checkout/setup-node `with:` exact, `permissions:` exactly `contents: read`, the eight root hooks, the record-revision `run:` in the pins invariants) | **accurate** — R5-4 |
| Pins-file header: invariants now name the fixture check and the browser-revision record | **accurate** — R5-4 |
| Layer 2: "That catches a `.npmrc`, `NODE_OPTIONS` or `$GITHUB_ENV` route that blanks the variable **only while the capture still says "CI"**" | accurate |
| Layer 2: "GitHub documents … CANNOT overwrite `GITHUB_*` defaults through `env:` or `$GITHUB_ENV` … so a route that empties `CI` too **is still caught when it works through those**" + "An IN-PROCESS route … can delete both anchors" | **over-claim** — R5-FINDING V-A2 |
| § Residuals, helper-script bullet: "since `GITHUB_ACTIONS` cannot be overwritten through `$GITHUB_ENV`, emptying `CI` **in the same write** does not switch it off … It is not caught by layer 2 when an **in-process** route deletes both anchors" | the first half is accurate as literally scoped ("in the same write"). The bullet then presents in-process as the only exception, and that is incomplete — V-A2 |
| `ci-environment.ts` header: "So a `$GITHUB_ENV` write or an env map cannot switch the policy off; an IN-PROCESS route … still can" | **over-claim** for `$GITHUB_ENV` — V-A2. Accurate for an env map, because the guard makes env maps default-deny |
| § Residuals, npmrc bullet: "caught … ONLY while the capture still says "CI" …; an npm-driven route runs in-process … can delete both anchors … layer 3 is the control that holds" | accurate |
| "What still gets through": pre-load code "can also delete `CI` and `GITHUB_ACTIONS` (layer 2 then silent)" | accurate |
| V-F table row clause | accurate |
| V-D: "not readable from a spec **running in a worker**", the "NOT in the main process" paragraph, forgery item 1, the `stamp.ts` "NOT CLOSED" note | accurate. All of them describe exactly what I reported and claim nothing more |
| V-D, **unlisted and unchanged**: AGENTS.md:459 "The claim this section makes is therefore precise: **a test cannot pass without the harness**" | still unqualified while the paragraph above it says a main-process read is NOT CLOSED and unestablished. **NIT** (R5-FINDING V-D2): add "subject to the main-process note above" |
| Residual "Pinning a step fixes its BYTES": now names checkout/setup-node `with:` pinned, root lifecycle refused, and "a DEPENDENCY's own install script run by `npm ci`" | accurate, and more candid than before |

## R5-6. Finding at f6d245f

```
FINDING V-A2: the new sentences say a `$GITHUB_ENV` route cannot switch layer 2 off
              and only an IN-PROCESS route can; a `$GITHUB_ENV` write of a non-default
              name (`BASH_ENV`), or a `$GITHUB_PATH` write, reaches the pinned lane
              step's own shell before Playwright starts
Severity:    REQUIRED
Confidence:  high on the documents and on Bash semantics; the Actions behaviour is
             UNVERIFIED (billing)

Affected:
  repo:      vizra-user
  files:     e2e/harness/ci-environment.ts header ("So a `$GITHUB_ENV` write or an env map
             cannot switch the policy off; an IN-PROCESS route … still can")
             AGENTS.md § Artifact privacy layer 2 ("so a route that empties `CI` too is still
             caught when it works through those [`env:` or `$GITHUB_ENV`] … An IN-PROCESS route
             … can delete both anchors")
             AGENTS.md § Residuals, helper-script bullet ("It is not caught by layer 2 when an
             in-process route deletes both anchors")
  requirements: VZ-FOUND-008

Observed (read, not built):
  - GitHub documents exactly ONE name that `$GITHUB_ENV` may not set: `NODE_OPTIONS`
    (workflow-commands page, fetched 2026-09-23). `BASH_ENV` is not a `GITHUB_*` or
    `RUNNER_*` name. `$GITHUB_PATH` "Prepends a directory to the system PATH variable …
    available to all subsequent actions" (same page).
  - The pinned lane step has no `shell:`, so it runs under GitHub's default `bash -e {0}`
    (workflow-syntax page). Bash, running a script non-interactively, reads the file named
    by `BASH_ENV` first (`man bash`: "If this parameter is set when bash is executing a
    shell script, its value is interpreted as a filename containing commands to initialize
    the shell"). And whatever `npm` PATH resolves first is what `npm run e2e` executes.
  - GitHub's "can't overwrite `GITHUB_*`" governs assignment through `env:` and
    `$GITHUB_ENV`. It does not stop the step's own shell, or a wrapper earlier on PATH,
    from removing a variable before it starts Playwright. So such a route can make the
    capture say "not CI" without being in the Playwright process.
  - The lane guard refuses `$GITHUB_ENV` / `$GITHUB_PATH` only in `run:` TEXT and env
    values, and AGENTS.md already states that a helper script's write is not seen. So the
    route is the stated helper-script class. What is new is the sentence that says this
    class "cannot switch the policy off".

Failure:
  The same shape as V-A, one layer out. The fix moved the policy onto an anchor that a direct
  write cannot touch, which is right, and measured (R5-2). But the sentences now partition
  pre-load routes into "`$GITHUB_ENV` / env map → caught" and "in-process → layer 3". The
  indirect `$GITHUB_ENV` (`BASH_ENV`) and `$GITHUB_PATH` routes fall in neither half. For
  those, layer 2 is silent and layer 3 holds. That is true in practice, and it is what the
  docs should say.

Perspective: developer (the reviewer who trusts the sentence)

Recommendation (smallest — sentences only; the code is right):
  In all three places, replace the partition with the general statement `ci-environment.ts`
  already makes in its first new paragraph ("It does NOT hold when the same route also makes
  the capture say 'not CI'; then layer 3 … is what holds"). Scope the `GITHUB_ACTIONS`
  sentence to "a `$GITHUB_ENV` or `env:` assignment of `CI` or `GITHUB_ACTIONS` itself", and
  name `BASH_ENV` via `$GITHUB_ENV`, and `$GITHUB_PATH`, as routes that reach the lane step's
  shell and fall to layer 3.

Acceptance criteria:
  No sentence in AGENTS.md or ci-environment.ts says that a `$GITHUB_ENV` (or `$GITHUB_PATH`)
  route cannot switch layer 2 off. The exceptions named include a route through the lane
  step's own shell or PATH.
Tests: none needed. The controls are unchanged and measured.
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge: "It needs a helper script plus a second file, and layer 3 holds anyway." Both are
  true, and neither changes the sentence. V-A was upheld on exactly this reasoning one round
  ago, and the rule is about what the document claims.
```

```
FINDING V-D2 (NIT): AGENTS.md:459 "a test cannot pass without the harness" is still
  unqualified beside the new "NOT CLOSED" main-process paragraph. Add "subject to the
  main-process note above".
```

## R5-7. Demonstrations, CI, diff audit, head

- **`npm run e2e:demos`** (my ports 3291/3292, image `vzv-pr8r5:demonstrate`), 11:44:50Z →
  12:05:38Z, load 221/202/177 → 44/74/107: exit 0, **149 passed / 0 blocked / 0 failed**.
  `d16c-variable-blank-and-CI-emptied-under-GITHUB_ACTIONS-RED` passed (exit 1, "PLAYWRIGHT_NO_COPY_PROMPT
  is not"), along with the other d16c halves, D17b and D7b. The digest ledger it wrote is
  **byte-identical** to the committed one.
- **CI on f6d245f** (read with `gh api`, not re-run): every Actions check is
  `completed/failure` with the billing annotation ("The job was not started because recent
  account payments have failed…"). GitGuardian: success. **BLOCKED.**
- **Diff audit** (`f0f702e..f6d245f`):
  - no removed line in any test, the require-checks script, `demonstrate.sh` or the corpus;
    additions only (3 unit cases, 13 require-checks cases, 1 demo half);
  - 0 added `.skip`, `.fixme`, `.only`, `it.todo` or `eslint-disable`;
  - 0 credential-shaped additions, and no local path or e-mail in the added evidence;
  - `package.json`, the lockfile and `contracts/` are untouched;
  - failure messages still echo no values.
- **Head at end:** `gh pr view … headRefOid` and `git ls-remote …` both report
  `f6d245f6076b8641cf360ae30a7af1cc8ce00c03`. Unmoved.
- **Cleanup:** removed image `vzv-pr8r5:demonstrate` (the script removes the mutant itself).
  No container of mine remains. The scratch directory `vzv-vizra-user-pr8r5-OvbNMq` is
  deleted by exact path. Nothing was pushed, merged or approved. No instruction-shaped text
  appeared in any tool output.

## Not verified in this round

- GitHub CI (BLOCKED).
- V-A2 on Actions. It follows from GitHub's own pages plus Bash's documented `BASH_ENV`
  behaviour. By the chair's constraint I built no route.
- The four reasoned rows of the prevents/detects table (unchanged).
- Platform: macOS arm64 only.

## Verdict at f6d245f

Every finding from my f0f702e round has its control fixed and measured:

- **V-A (code): closed.** The pre-fix harness passes the "`CI` emptied under
  `GITHUB_ACTIONS`" lane (exit 0, 18 passed); the new harness fails it (exit 1, 18 policy
  failures). The unit tests go red 2 of 3 before the fix and green after. The GitHub quotations
  are verbatim.
- **V-B, V-C, V-E: closed.** 33 of my mutations are red by name, and co-weakening the pins
  file with the workflow is still red.
- **V-D and V-F: stated accurately.**
- **Lanes reproduce exactly:** `npm run ci` 627/0, require-checks 233/240, Playwright 18,
  `e2e:demos` 149/0/0 with the ledger byte-identical.

**One REQUIRED finding remains, and it is again a sentence, not a control.** V-A2: the new
wording says a `$GITHUB_ENV` route cannot switch layer 2 off, and that only an IN-PROCESS
route can. But GitHub documents `NODE_OPTIONS` as the only name `$GITHUB_ENV` refuses. A
`BASH_ENV` or `$GITHUB_PATH` write reaches the pinned lane step's own shell, which can remove
both anchors before Playwright starts. Layer 3 still holds, so nothing leaks.

Under the chair's "no false-guarantee merges" rule this is a FAIL. The fix is three
sentences, and it needs no code change. Also open: V-D2 (NIT).

FINAL VERDICT: FAIL — SHA f6d245f6076b8641cf360ae30a7af1cc8ce00c03

---

# Re-verification at `cf053a3` (2026-09-23) — closing slice, fix round 2 of 2 (last)

- **SHA verified:** `cf053a3f003b251df4c3405edda91560502c458e` (`gh pr view 8 … headRefOid`
  at start). One commit on `f6d245f`; `git merge-base --is-ancestor f6d245f HEAD` holds.
- **Environment:** as above. A NEW private clone under
  `…/scratchpad/vzv-vizra-user-pr8r6-sTTLHS/repo`; `npm ci` exit 0; load 1/5/15 at start
  5 / 22 / 67. No classifier stop.

## R6-1. Scope: comments, docs and the digest ledger only

`git diff --stat f6d245f HEAD` lists six files: AGENTS.md, `mutation-digests.txt`,
`ci-environment.test.ts`, `ci-environment.ts`, `check-e2e-lane.mjs`, `demonstrate.sh`.

- **Every changed line in the four code files is a comment.** I filtered the diff of
  `e2e/` and `scripts/` for `+`/`-` lines that do not start with `*`, `//` or `#`: zero lines.
- No control, assertion, `half` command or matcher changed.
- **Ledger.** Three D17d lines changed, BEFORE/MUTATED/RESTORED for `ci-environment.ts`.
  I recomputed `sha256(git show HEAD:e2e/harness/ci-environment.ts)` = `cc700a6f…2dab`,
  which equals the new BEFORE and RESTORED. The old value `9bac8461…ad85` equals
  `sha256` of f6d245f's copy. So the recomputation is correct, and the hygiene check
  (R6-2) agrees.

## R6-2. Lanes

| Command | Exit | Result |
|---|---|---|
| `npm run ci` | 0 | lint 0; tsc 0; **19 files / 627 tests / 0 skipped**; build ok; hygiene `OK: 308 text source(s) … 17 mutation-digest line(s) match this tree` |
| `bash scripts/ci/require-checks_test.sh` | 0 | **233 cases, 240 assertions, 0 failed** |
| `DEMO_PROD_PORT=3291 DEMO_DEV_PORT=3292 DEMO_IMAGE=vzv-pr8r6:demonstrate … npm run e2e:demos` (after a production build, `PUBLIC_ORIGIN=http://127.0.0.1:3291`) | 0 | **149 passed / 0 blocked / 0 failed**, 12:14:16Z → 12:29:55Z UTC, load 6/18/61 → 19/42/56. Included: d16c ×4 (the `CI`-emptied-under-`GITHUB_ACTIONS` half among them), D17b, and D17d ×3 (the halves that mutate `ci-environment.ts` and write its digests) |

**The ledger `e2e:demos` wrote is byte-identical to the committed one**
(`git diff --quiet -- docs/evidence/VZ-FOUND-008/mutation-digests.txt` → identical). So the
three recomputed D17d lines are exactly what the suite produces at this head.

## R6-3. The eight transcripts whose code-frame line numbers are stale

`grep -oE 'ci-environment\.ts:[0-9]+:[0-9]+'` over the committed transcripts gives
`ci-environment.ts:264:34` (133 occurrences, in d16b, d16c ×3 plus the new d16c half, d17b, and
d17e ×3). My regenerated set gives `:268:34`. The throwing line is now 4 lines lower because
the header comment grew.

I diffed each of the eight, committed against regenerated. I normalised only the
run-volatile fields:
- the `ci-environment.ts:<line>` references and the code-frame gutter numbers;
- my ports (3291/3292) against the builder's (3211/3212);
- the runtime-minted `vz…` markers;
- durations.

**Residual difference: 0 lines in all eight.** So the mismatch is ONLY the line numbers,
plus the fields every run changes.

The other 71 regenerated files that differ do so only in run-volatile fields: attachment
hashes, `mktemp` paths, image names, ports, Next build IDs, the dev server's chunk URLs, a
file count in a sweep (22 against 21) that no matcher reads, and `environment.txt`'s head
SHA (committed `4db7dce`, mine `cf053a3`).

**Do the stale numbers make an evidence claim false? No.**
- The committed transcripts say where they were produced. `environment.txt` reads
  `head sha: 4db7dce…`, and commit `f6d245f` is titled "demonstration transcripts at 4db7dce".
  At 4db7dce, line 264 of `ci-environment.ts` IS the `throw` (`git show 4db7dce:… | sed -n 264p`).
- Between 4db7dce and cf053a3 the file changed only in comments (R6-1), so the code those
  transcripts exercised is the code at this head.
- No `half` matcher, no AGENTS.md sentence, and no evidence README cites a
  `ci-environment.ts` line number (grep: none).
- The ledger — the one artifact the hygiene check ties to THIS tree — is current.

A reader following `:264` at cf053a3 lands 4 lines above the `throw`. That is cosmetic.
**NIT**, disclosed by the builder.

## R6-4. Sentences

I read the builder's eight entries in `sentences-r2.md`, the full `git diff f6d245f HEAD`, and
a repo-wide grep for the strong forms (`whatever route`, `by any route`, `cannot switch`,
`cannot be overwritten`, `in-process route`, `not readable from a spec`, `a spec cannot read`,
`no running spec`, `caught by the runtime`).

| Sentence (cf053a3) | Verdict |
|---|---|
| AGENTS.md layer 2: "So a DIRECT `env:` or `$GITHUB_ENV` assignment of `CI` or `GITHUB_ACTIONS` itself cannot switch the policy off (D16c's "`CI` emptied" half, simulated)" | **accurate** — GitHub's pages (R5-3) and D16c, re-run |
| AGENTS.md layer 2: "Anything that runs code before the configuration loads CAN remove both anchors, and then this layer is silent — layer 3 is the control that holds regardless. Three such routes, named: … an IN-PROCESS preload …; a `BASH_ENV` written to `$GITHUB_ENV` … sourced by the lane step's own default `bash -e {0}` …; and `$GITHUB_PATH` … These three were reasoned from GitHub's pages and the Bash manual (`BASH_ENV`), not built" | **accurate and labelled as reasoned.** It matches what I cited in V-A2: the workflow-commands page lists `NODE_OPTIONS` as the one blocked name; the workflow-syntax page gives the `bash -e {0}` default; `man bash` documents `BASH_ENV`; the `$GITHUB_PATH` wording is from the same page. The general sentence comes first, so "three" names examples rather than bounding the class |
| AGENTS.md § Residuals, helper-script bullet: "a DIRECT `$GITHUB_ENV` assignment of `CI` or `GITHUB_ACTIONS` itself cannot make it say otherwise … A helper's write can still silence layer 2 INDIRECTLY: … `BASH_ENV` … `$GITHUB_PATH` … as can an in-process preload. Then the pinned redaction step's page-snapshot gate (layer 3) is what holds. Reasoned …, not built." | **accurate and labelled** |
| AGENTS.md:459 "a test cannot pass without the harness — subject to the main-process note above, which is NOT CLOSED —" | **accurate** (V-D2 closed) |
| `ci-environment.ts` header, the new V-A2 paragraph | **accurate and labelled** — the same content as AGENTS.md |
| `check-e2e-lane.mjs` .npmrc comment and effective-value comment ("while the capture says CI … regardless") | **accurate** |
| `ci-environment.test.ts` comment ("by a DIRECT … assignment (a `BASH_ENV` or `$GITHUB_PATH` route can still remove it; AGENTS.md)") | **accurate** |
| `demonstrate.sh` D16c comment | **accurate** |
| **NOT changed, not on the list:** `ci-environment.ts:226-229`, inside `pageSnapshotProblem`: "`GITHUB_ACTIONS` is the anchor a job **cannot take away** … An in-process route that runs before the configuration loads can still delete both." | **still the V-A2 partition** in a four-line inline comment. A job CAN take it away by the `BASH_ENV`/`$GITHUB_PATH` routes the header now names. It defers "(see the header)", and the header 100 lines above is correct → **R6-FINDING V-A3, SHOULD** |
| **NOT changed:** `demonstrate.sh:824` "under a per-run key a spec cannot read" | V-D class in a script comment. AGENTS.md and `stamp.ts` now carry the NOT CLOSED qualification → **NIT** |
| `stamp.ts:49`, `stamp-verify.mjs:12` "no running spec can read **this run's** key" / "could have read it" | about the key FILE on disk (written in `onEnd`), and accurate in that context. The main-process note sits above it in `stamp.ts`. Not a finding |
| `browser-errors.ts:437-439`, `creation-guard.ts:68` "any route" / "whatever route" | about context creation, outside this slice, from the earlier verified rounds. Not a finding |

## R6-5. Findings at cf053a3

```
R6-FINDING V-A3: one inline comment still states the V-A2 partition
Severity:    SHOULD
Confidence:  high
Affected: vizra-user; e2e/harness/ci-environment.ts:226-229 (inside `pageSnapshotProblem`):
  "`GITHUB_ACTIONS` is the anchor a job cannot take away … An in-process route that runs
  before the configuration loads can still delete both."
Observed: unchanged since 4db7dce, and not on the builder's list. The same file's header
  (lines ~110-122) and AGENTS.md now say correctly that a `BASH_ENV` via `$GITHUB_ENV`, or a
  `$GITHUB_PATH` entry, can also remove both anchors.
Failure: a reader of the function alone gets the old, stronger claim. The comment itself says
  "(see the header)", and the header is right.
Why SHOULD, not REQUIRED: the guarantee surfaces a reviewer relies on — AGENTS.md § Artifact
  privacy, § Residuals, and this file's header — are accurate and labelled. This is an
  internal pointer that is stale, not the published statement of the control. The chair may
  weigh it differently under "no false-guarantee merges"; I state it so the choice is theirs.
Recommendation: "the anchor a DIRECT `env:`/`$GITHUB_ENV` assignment cannot take away … an
  in-process preload, a `BASH_ENV` or a `$GITHUB_PATH` route can still remove both (see the
  header)". Comment only.
```

```
R6-NIT 1: scripts/e2e/demonstrate.sh:824 "a per-run key a spec cannot read" — add "in a
  worker", matching AGENTS.md:418.
R6-NIT 2: eight committed d16/d17 transcripts show `ci-environment.ts:264` for a `throw` that
  is at :268 at this head (comment growth). Disclosed by the builder; no claim depends on it
  (R6-3). Regenerate with the next transcript refresh.
```

Carried, unchanged and correctly stated as NOT CLOSED: **V-D**, the stamp key in the main
process during collection. It is queued for PR B and is not this PR's to block.

## R6-6. CI, head, cleanup

- **CI on cf053a3** (read with `gh api`, not re-run): every Actions check is
  `completed/failure` with "The job was not started because recent account payments have
  failed…". GitGuardian: success. **BLOCKED.**
- **Head at end:** `gh pr view … headRefOid` and `git ls-remote … refs/heads/fix/m0-artifact-privacy-a`
  both report `cf053a3f003b251df4c3405edda91560502c458e`. Unmoved.
- **Cleanup:** removed image `vzv-pr8r6:demonstrate` (the suite removes the mutant itself).
  No container of mine remains. The scratch directory `vzv-vizra-user-pr8r6-sTTLHS` is
  deleted by exact path. Nothing was pushed, merged or approved. No instruction-shaped text
  appeared in any tool output.

## Not verified in this round

- GitHub CI (BLOCKED by billing). Local evidence cannot substitute for `ci-required`.
- The `BASH_ENV` and `$GITHUB_PATH` routes on Actions. They are reasoned and labelled as such,
  and by the chair's constraint no route was built.
- The four reasoned rows of the prevents/detects table (unchanged since my f0f702e round).
- Any platform other than macOS arm64.

## Verdict at cf053a3

The commit does exactly what it says: comments, docs and the digest ledger, with no control or
assertion touched (0 non-comment lines changed in code files).

- **Lanes reproduce:** `npm run ci` 627/0 with hygiene OK; require-checks 233/240;
  `e2e:demos` 149/0/0 with a ledger byte-identical to the committed one.
- **The stale line numbers are the only content difference** in the eight transcripts
  concerned, and they falsify no claim.
- **V-A2 is closed.** Every published statement of layer 2 now makes the general
  "anything that runs before the configuration loads" statement. It names `BASH_ENV` via
  `$GITHUB_ENV` and `$GITHUB_PATH` accurately against GitHub's pages and the Bash manual,
  labels them "reasoned, not built", and places the guarantee on layer 3 — which is pinned
  and was measured in every round.
- **V-D2 is closed.**

What remains is one stale inline code comment (V-A3, SHOULD) and two NITs. None of them is a
published guarantee stronger than its control.

Across this closing slice, every finding from the four rounds is closed at its control and
stated at its measured strength: H, I, J, K, V-A, V-A2, V-B, V-C, V-D (as NOT CLOSED, queued),
V-E and V-F.

PASS is a verifier verdict, not a merge. The merge rule also requires `ci-required` green on
this SHA, and CI is BLOCKED by billing.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA cf053a3f003b251df4c3405edda91560502c458e

---

# Re-confirmation at `c2ff445` (2026-09-23) — comment-only, for V-A3 and R6-NIT 1

- **SHA:** `c2ff4454b28d3b7887d19fdf2f44742ffb7f55da`. At start and at end, `gh pr view 8 …
  headRefOid` and `git ls-remote … refs/heads/fix/m0-artifact-privacy-a` both report c2ff445.
  One commit on cf053a3; `git merge-base --is-ancestor cf053a3 HEAD` holds.
- **Environment:** as above; a new private clone `…/scratchpad/vzv-vizra-user-pr8r7-gRygN3/repo`,
  `npm ci` exit 0.

## RC-1. Scope

`git diff --stat cf053a3 HEAD` lists three files, +9 −9:

- `e2e/harness/ci-environment.ts` (4 comment lines in `pageSnapshotProblem`);
- `scripts/e2e/demonstrate.sh` (2 comment lines at the D11 header);
- `docs/evidence/VZ-FOUND-008/mutation-digests.txt` (the three D17d lines).

Changed lines in `e2e/` and `scripts/` that are not `*`, `//` or `#` comments: **0**. The line
count of `ci-environment.ts` is unchanged, **269 → 269**, so the code-frame line numbers
from R6-3 do not move again.

## RC-2. The new sentences

- **`ci-environment.ts:226-229`:** "`GITHUB_ACTIONS` cannot be changed by a DIRECT
  `env:`/`$GITHUB_ENV` assignment; anything that runs before the configuration loads (an
  in-process preload, a `BASH_ENV` via `$GITHUB_ENV`, a `$GITHUB_PATH` entry) can remove both
  anchors, and then layer 3 holds — see the header."
  **Accurate.** It now matches the header and AGENTS.md, and the sources I checked in R5-3.
  The "reasoned, not built" label sits in the header it points to. **V-A3 is closed.**
- **`demonstrate.sh:824`:** "under a per-run key a spec in a worker cannot read".
  **Accurate.** It matches AGENTS.md:418. **R6-NIT 1 is closed.**

## RC-3. The D17d ledger lines, recomputed with `demonstrate.sh`'s own mutation

`demonstrate.sh:2210`'s perl program
(`s/return WATCHED_KEYS\.filter\(\(key\) => live\[key\] !== captured\[key\]\);/void live; void captured; return [];/`)
was applied to a COPY of the file. The copy differed from the original, so the mutation
applied, and the tracked file stayed clean (`git status` empty). `shasum -a 256`, as the
script's `digest()` does:

| Line | Recomputed | Ledger at c2ff445 |
|---|---|---|
| BEFORE | `441f0186…2ed5104` | `441f0186…2ed5104` ✓ |
| MUTATED | `091c8f30…c20a517e` | `091c8f30…c20a517e` ✓ |
| RESTORED | `441f0186…2ed5104` | `441f0186…2ed5104` ✓ |

## RC-4. Lanes

| Command | Exit | Result |
|---|---|---|
| `npm run ci` | 0 | lint 0; tsc 0; **19 files / 627 tests / 0 skipped**; build ok; hygiene `OK: 308 text source(s) … 17 mutation-digest line(s) match this tree` |
| `bash scripts/ci/require-checks_test.sh` | 0 | **233 cases, 240 assertions, 0 failed** |

`npm run e2e:demos` was not re-run; the chair did not ask for it. It is not needed for a
comment-only change: RC-3 reproduces its only content-dependent output, the D17d digests,
exactly.

## RC-5. CI, cleanup

- **CI on c2ff445** (read with `gh api`, not re-run): every Actions check is
  `completed/failure` with "The job was not started because recent account payments have
  failed…". GitGuardian: success. **BLOCKED.**
- **Cleanup:** the scratch directory `vzv-vizra-user-pr8r7-gRygN3` is deleted by exact path.
  No image or container was created. Nothing was pushed, merged or approved. No
  instruction-shaped text appeared in any tool output.

## Verdict at c2ff445

The commit is comment-only, as claimed:

- 0 non-comment code lines;
- the line count of `ci-environment.ts` is unchanged;
- the three D17d ledger values equal the sha256 of the new file and of `demonstrate.sh`'s own
  mutation of it;
- `npm run ci` (hygiene included) and `require-checks_test.sh` are green with the counts
  unchanged.

V-A3 and R6-NIT 1 are closed. R6-NIT 2 (the stale `:264` in eight transcripts) stays a NIT.
V-D stays NOT CLOSED and queued for PR B, as documented.

PASS is not a merge. `ci-required` must be green on this SHA, and CI is BLOCKED by billing.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA c2ff4454b28d3b7887d19fdf2f44742ffb7f55da
