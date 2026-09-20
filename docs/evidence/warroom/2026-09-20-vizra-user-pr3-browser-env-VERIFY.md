# Independent verification — vizra-user PR #3 "browser environment" (VZ-FOUND-008)

**Verdict: FAIL** — two blocking findings. Every acceptance-bullet demonstration
reproduced; `ci-required` green on the verified SHA; but the harness can be made
to report green on a page that 404s and throws, by a one-line spec that passes
the entire gate, in a directory no CODEOWNER reviews.

| | |
|---|---|
| PR | https://github.com/yegamble/vizra-user/pull/3 |
| Head SHA verified | `112291e71cc269934c9aa87b69c021170c557f91` (confirmed unmoved at verification time) |
| Base | `1a952b50b07ec081d43b7e11b2ee010192fa8a5d`, branch `feat/m0-browser-env`, 2 commits, 60 files, +3891 −7 |
| Acceptance | VZ-FOUND-008 — "the Playwright harness runs in CI against the production build image on desktop and mobile projects, and a console or network error fails the lane (demonstrated)" (`docs/issues/VZ-ISSUE-001.md:21`) |
| Scope | item 4 of `docs/plans/2026-09-15-prompt01-architecture.md`; ADR-009 § "M0 obligations" |
| Verifier | independent; did not write any of this code |
| Verification date | 2026-09-20 |

## Environment

```
macOS Darwin 25.5.0, arm64 (NOT the ADR-009 acceptance platform)
Node v22.14.0, npm 10.9.2
@playwright/test 1.63.0 (lockfile-pinned; npm dist-tags.latest = 1.63.0)
Chromium chromium-1243 / chromium_headless_shell-1243 (Chrome for Testing 153.0.8010.12)
  — ALREADY PRESENT in ~/Library/Caches/ms-playwright before this verification.
    I installed no browser and removed none.
Docker available; 17 GiB free at start (above the 8 GiB threshold), so the local
  image build DID run.
Clean clone: <scratch>/vizra-user-verify, checked out at the head SHA, deleted on completion.
```

## Commands and results

All from the clean clone at `112291e7`. Exit codes captured, not inferred.

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `npm ci` | 0 | lockfile consistent; `npm ci --dry-run` re-checked → 0 |
| 2 | `npm run ci` (lint, typecheck, vitest, `next build`) | 0 | — |
| 3 | `npm run test` (vitest) | 0 | **8 files / 177 tests / 0 skipped** — matches the builder's claim exactly |
| 4 | `bash scripts/ci/require-checks_test.sh` | 0 | **73 cases / 80 assertions / 0 failed** — matches the builder's claim exactly |
| 5 | `bash scripts/ci/check-e2e-lane.sh` | 0 | OK |
| 6 | `bash scripts/ci/check-required-floor.sh` | 0 | OK — floor `frontend contract e2e` |
| 7 | `npm run e2e` against the standalone production server | 0 | **18 passed, 0 skipped, 0 flaky**; `e2e coverage floor: OK (desktop-chromium-1440=9 mobile-chromium-390=9)` |
| 8 | `npm run e2e:demos` (with Docker) | 0 | **18 halves passed, 0 blocked, 0 failed** |
| 9 | `npx playwright install --dry-run chromium` | 0 | revision `chromium-1243`, already installed |

Local production Docker image build: **RAN** (`vizra-user:verify`, native arm64,
no support claim — ADR-009's acceptance platform is GitHub `ubuntu-24.04`
linux/amd64). Both images I created were deleted afterwards; no other agent's
containers, images or volumes were touched.

## Demonstrations — reproduced by me, red then green

Every RED half exited non-zero with the named diagnostic and every GREEN half
exited 0, from my own clone. Not read from the builder's transcripts.

| # | Demonstration | RED | GREEN |
|---|---|---|---|
| D1 | `console.error` on a page fails | exit 1, "browser error(s) that no allow-list entry covers" | exit 0, "1 passed" |
| D2 | a 404 sub-resource fails | exit 1, "http 404" | exit 0, "1 passed" |
| D3 | an uncaught exception fails | exit 1, "pageerror" | exit 0, "1 passed" |
| D4a | zero tests collected fails | exit 1, "did not satisfy its coverage floor" | exit 0, "e2e coverage floor: OK" |
| D4b | a missing project fails | exit 1, "is not in the resolved Playwright configuration" | exit 0, "e2e coverage floor: OK" |
| D5 | pointing at `next dev` fails | exit 1, "this is not a production build" | exit 0, "4 passed" |
| D6 | the image carries no harness file or fixture token | exit 1, "contains browser-harness files" (mutant image) | exit 0, "contains no browser-harness path and no fixture token" (real image) |
| D7 | a weakened `e2e` workflow fails the guard | exit 1, "no longer uploads artifacts" | exit 0, "still drives the built image" |
| D8 | a spec bypassing the guarded `test` fails | exit 1, "imports values from @playwright/test directly" | exit 0 |

### D5 extension — the five production markers, mutated ONE AT A TIME

The builder's D5 trips all five markers at once (against `next dev`), which
cannot distinguish five live markers from one live marker and four dead ones. I
mutated each independently against the **real production server** and asserted
each produced **exactly one** problem:

| Marker | Injected fault (production server otherwise unmodified) | Problems returned |
|---|---|---|
| 1 dev-only bundles | a request for `/hmr-client.js` | 1 — "development-only bundles" |
| 2 HMR WebSocket | one `new WebSocket(...)` from the page | 1 — "WebSocket(s)" |
| 3 dev overlay | `document.body.appendChild(<nextjs-portal>)` | 1 — "nextjs-portal" |
| 4 flight build id | route-rewrite the document's `"b":"…"` to `"development"` | 1 — `build id is "development"` |
| 5 immutable caching | route-rewrite `/_next/static/**` `cache-control` to `no-cache, must-revalidate` | 1 — "not immutably cached" |
| 5b | abort every `/_next/static/**` response | 1 — "immutable-caching marker could not be checked" |
| control | nothing | **0** |

**All five markers are independently live and non-redundant.** This is the
strongest single result in the PR.

## GitHub CI on the verified SHA

```
ci-required    success  2026-09-20T20:04:15Z
contract       success
deps-scan      success
docker-build   success
e2e            success  2026-09-20T20:03:51Z
frontend       success
guard          success
image-scan     success
GitGuardian Security Checks   FAILURE
```

`ci-required` (run 35534195534) log, verbatim:

```
  - frontend
  - contract
  - ?guard
  - ?docker-build
  - e2e
waiting: frontend (in_progress) contract (in_progress) guard (in_progress) docker-build (in_progress) e2e (in_progress)
waiting: frontend (in_progress) docker-build (in_progress) e2e (in_progress)
waiting: e2e (in_progress)
OK: every required check on 112291e71cc269934c9aa87b69c021170c557f91 concluded success.
```

**The manifest matches the jobs that actually ran.** `e2e` is enumerated as a
non-optional required lane, `ci-required` waited 140 s for it, and it concluded
`success` at 20:03:51 before `ci-required` concluded at 20:04:15. No listed lane
failed to execute. The CI `e2e` job log independently confirms: pinned Chromium
`chromium-1243` downloaded, image built, `OK: 'vizra-user:e2e' contains no
browser-harness path and no fixture token`, `18 passed (11.4s)`,
`e2e coverage floor: OK (desktop-chromium-1440=9 mobile-chromium-390=9)` — the
same counts I obtained locally.

## Answers to the specific questions

**1. Can the D1–D3 fixture routes ship? No — there are no routes.** The faults
are injected with `page.addInitScript` against the unmodified production server
(`e2e/demos/console-error.demo.ts:25`, `failed-request.demo.ts:25`,
`uncaught-exception.demo.ts:22`). D2's 404 is the production server's own 404 for
`/__vizra_e2e_fixture__/missing-on-purpose.png`. There is no `app/` route, no env
flag and nothing to exclude from the build. `check-no-test-fixtures-in-image.sh`
asserts the claim against `docker export` of the flattened image rather than
trusting `.dockerignore`, on both paths and the `__vizra_e2e_fixture__` token. I
reproduced both halves. **Not a finding.**

**2. `e2e` required and non-path-filtered? Yes, on both counts, and `ci-required`
waited for it.** `.github/required-checks.txt:52` lists bare `e2e` (not `?e2e`);
`scripts/ci/check-required-floor.sh:50` sets `FLOOR="frontend contract e2e"`;
`.github/workflows/e2e.yml:23-27` triggers on `push: [main]`, `pull_request:`
and `merge_group:` **with no `paths:` filter**. Confirmed by the fan-in log
above. The new `require-checks_test.sh` cases drive the *default* floor, so
dropping `e2e` from both the manifest and the floor default is caught.

**3. URL redaction covers the harness's own output only — traces leak.** See
FINDING 4. Reproduced with a `?X-Amz-Signature=…&X-Amz-Expires=60` URL: redacted
in every harness line, in `formatFailure` output and in the `browser-signals.json`
attachment; **present verbatim** inside `trace.zip` members `1-trace.network` and
`1-trace.trace`, which the workflow uploads as a 14-day CI artifact on failure.

**4. AGENTS.md +78/−3 is all authored contract text; the −3 is legitimate; no
generated block remains.** The three removed lines are two rewritten lines in the
required-floor paragraph (`frontend`, `contract` → `frontend`, `contract`, `e2e`)
and one rewritten line in the Pins section (to insert the Playwright pin before
"Node is pinned once"). Nothing was deleted. `grep` for `nextjs-agent-rules` and
Next's managed-block markers over `AGENTS.md` and `CLAUDE.md` at HEAD: **none**.
`next.config.ts:24` sets `agentRules: false`, and I ran `next dev` (via the D5
demonstration) from the clean clone — the tree was still clean afterwards
(`git status --porcelain` empty). Claim verified.

**5. The −2 in `scripts/ci/require-checks_test.sh` is a STRENGTHENING, ruled
legitimate.** The removed lines are the title and the invocation of the
"real manifest satisfies its own floor" case, which previously pinned
`FLOOR="frontend contract"` as an override. Under that override the case would
have passed even if `e2e` were dropped from both the manifest *and* the floor's
default. The replacement drops the override so the committed manifest must
satisfy the real default floor including `e2e`. No assertion was weakened, no
case deleted; +49 adds three new cases (`e2e: missing`, `e2e: marked optional`,
and a passing three-lane manifest). Suite still: 73 cases / 80 assertions / 0
failed.

**6. GitGuardian: not a credential; nothing credential-shaped at HEAD; a
squash-merge drops the commit.** The flagged value is
`ws://127.0.0.1:3212/_next/hmr?id=<opaque>` — a loopback Next dev-server HMR
session id, bound to a dev server on the builder's own machine that no longer
exists, granting no access to anything. GitGuardian read the *shape* correctly
(opaque high-entropy query value) and was right to; the value itself is not a
secret. At HEAD the string survives only as `?<redacted: 1 parameter(s)>` in the
transcripts, as the literal placeholder `<opaque>` in prose
(`docs/evidence/VZ-FOUND-008/README.md:85`), and as
`const opaque = "PLACEHOLDER-not-a-real-id"` in `e2e/harness/redact.test.ts:26`.
I scanned the whole HEAD tree for credential-shaped strings and found none.
The check scanned "2 commits in your pull request"; `951f18b` is dropped by a
squash-merge, so the finding does not follow the change onto `main`.
**Not a blocker — but the check must be dismissed deliberately by the owner, not
merged past.**

**7. Pins are correct and consistent.** `@playwright/test` `1.63.0` exact (no
range) in `package.json`; `npm view` confirms the version exists and is
`dist-tags.latest`; `package-lock.json` adds exactly three packages
(`@playwright/test`, `playwright`, `playwright-core`) all at 1.63.0 with
integrity hashes; `npm ci` and `npm ci --dry-run` both exit 0. ADR-001 pins no
browser tooling (confirmed by grep), which is why AGENTS.md pins it locally — an
honest resolution, and the recorded browser revision (`chromium-1243`) matches
what both my machine and the CI runner resolved.

## Attempts to make the harness LIE

Everything below was run from the clean clone against the real production build.
"Green" means the harness reported success on a page that was misbehaving.

### Caught (the guard held)

| Attempt | Result |
|---|---|
| `console.error` from an **inline script in `<head>`**, before any test code runs | **caught** — `[console] console.error: VERIFIER_EARLY_HEAD_ERROR` |
| `console.error` inside a **web worker** | **caught** — `[console]`, located at the blob URL |
| uncaught throw inside a **web worker** | **caught** — `[pageerror]` |
| `console.error` inside a **same-origin iframe** | **caught** — `[console]`, located at `about:srcdoc` |
| uncaught throw inside a **same-origin iframe** | **caught** — `[pageerror]` |
| request **aborted** rather than answered | **caught** — `[requestfailed] … net::ERR_CONNECTION_REFUSED` |
| a **4xx on a `fetch` the page catches and swallows** | **caught** — `[response] http 404` + `[console]` |
| cross-origin fetch the browser refuses | **caught** — `[requestfailed]` + `[console]` |
| error on the **mobile project only** | **caught on mobile, correctly silent on desktop** |
| `test.skip()` called **inside the body after** the page already errored | **caught** — the guard still fails the test |
| a **bare two-element array** `test.use` policy | **refused** — see below |
| **flaky pass on retry** hiding a first-attempt error | **run fails** — see below |
| `test.only` | `forbidOnly: !!process.env.CI` errors in CI |
| `--grep` selecting nothing | **caught** by the coverage floor (D4a) |
| `test.skip` / `test.fixme` / `describe.skip` on *every* test | **caught** by the coverage floor (count 0 < 1) |

**Bare-array policy (question (c), second half) — the builder's claim is
confirmed, precisely.** `test.use({ browserErrorPolicy: [a, b] })` where both are
objects is read by Playwright 1.63.0 as a `[value, options]` fixture tuple: the
fixture arrived as `a` alone, i.e. `{kind, match, reason}`. `validatePolicy`
therefore rejected it on the *second* branch —
`browserErrorPolicy.allow must be an array of { kind, match, reason } entries.` —
not the first. Either way it **fails closed**, and a bare array of any other
length is refused by the first branch (`got an array`). The two-entry **object**
form was also checked: both entries survive. Claim verified.

**Retries (question (g)) — a flaky pass does NOT hide a first-attempt error.**
With `CI=1` (the real lane: `retries: 1`, `failOnFlakyTests: true`), a test
producing a `console.error` on attempt 0 and clean on attempt 1 is reported
`1 flaky` and the process **exits 1**. Same locally with `--retries=1`. So
`retries: 1` does not weaken the policy assertions, and the coverage reporter
additionally counts only `outcome() === "expected"` && `status === "passed"`, so
a flaky test does not feed the floor.

### NOT caught (the harness stayed green)

Three, all reproducible; two are blocking.

1. **`import * as pw from "@playwright/test"` in a spec** — full gate green on a
   broken page. See FINDING 1.
2. **`import { expect, test } from '@playwright/test'` (single quotes)** — passes
   the bypass guard and ESLint. See FINDING 1.
3. **An allow-list entry with `match: /.*/` and `reason: "x"`** — accepted. There
   is no breadth check and no minimum on the reason beyond non-blank. See
   FINDING 3's Challenge; I judged this SHOULD rather than BLOCKER because the
   entry is at least visible in the spec's diff.

Two workflow mutations also passed `check-e2e-lane.sh`: see FINDING 2.

Mixed-content blocking was **not testable** and is not claimed: the lane drives
`http://127.0.0.1`, and browsers only block mixed content on an `https` page.
UNVERIFIED, by construction rather than by omission.

---

## Findings

```
FINDING 1: a spec can bypass the browser-error guard with two common import spellings, and go green through the whole gate on a page that 404s and throws
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/browser-errors.test.ts:187
             e2e/harness/test.ts:7-10
             AGENTS.md (the "Default-deny on browser errors" paragraph added by this PR)
             .github/CODEOWNERS:33-34
  requirements: VZ-FOUND-008

Observed:
  The structural guard is a single regex over each spec's source:

      const bareImports = source.match(/^\s*import\s+\{[^}]*\}\s+from\s+"@playwright\/test";?$/gm) ?? [];

  It requires braces AND double quotes AND the `from` clause on the matched
  line-run. I wrote two specs into e2e/specs/ in the clean clone and ran the
  real gate:

    (a) import * as pw from "@playwright/test";
        const test = pw.test;
    (b) import { expect, test } from '@playwright/test';   // single quotes

  For (a), whose body makes the page request /VERIFIER_EV3_MISSING.png (404)
  and throw an uncaught Error on every load:

      npm run ci      -> exit 0   (eslint clean, tsc clean, vitest 178 passed)
      npm run e2e     -> exit 0   20 passed
                                  e2e coverage floor: OK (desktop=10 mobile=10)

  The identical spec body, with only the import changed to the harness, fails:

      [response]   http 404: GET http://127.0.0.1:3213/VERIFIER_EV3_MISSING.png
      [console]    console.error: Failed to load resource: … 404 (Not Found)
      [pageerror]  pageerror: VERIFIER_EV3_UNCAUGHT
      -> exit 1

  For (b): `npx eslint` exit 0, bypass guard exit 0 (23 passed). The repository
  has no quote-style lint rule, so single quotes are not caught downstream.

  Only the single-line double-quoted named-brace form is caught. (A multi-line
  `import {\n test,\n} from "@playwright/test";` IS caught — the negated class
  and `\s+` span newlines — so that spelling is safe.)

  AGENTS.md, added by this PR, states the opposite: "Never import `test` from
  `@playwright/test` in a spec — that bypasses the guard, and
  `e2e/harness/browser-errors.test.ts` fails the `frontend` lane if a spec
  does." That sentence is false for spellings (a) and (b).

Failure:
  The one control the entire slice exists to provide — "no spec can pass while
  the page is logging errors, throwing, or 404-ing its own resources"
  (e2e/harness/test.ts:6-8) — is removable by one line, in e2e/specs/, which
  .github/CODEOWNERS does NOT cover (it covers /e2e/harness/ and
  /playwright.config.ts only). Every later UI slice — the app shell, the
  owner's Search page, the M1 golden path — adds its specs to exactly that
  unreviewed directory, and each will be declared VERIFIED on this harness. The
  failure is silent: the lane prints "20 passed" and "coverage floor: OK".
  This is the third instance of the defect class the PR body itself names:
  "Two earlier pull requests in this repository each shipped a guard that
  passed while testing nothing."

Perspective:
  developer (a later slice is declared VERIFIED on a broken page), and through
  them visitor and member, who receive the broken page.

Recommendation:
  Stop pattern-matching import syntax; assert the imported binding instead.
  Smallest change that closes it: in e2e/harness/browser-errors.test.ts, fail
  a spec whose source contains the substring "@playwright/test" at all unless
  every occurrence is on a line beginning with `import type`. That is
  quote-agnostic, namespace-agnostic, require()-agnostic and one line. The
  three legitimate type-only importers already live in e2e/harness/ and
  e2e/demos/ uses `import("@playwright/test").Page` inline — so either narrow
  the sweep to e2e/specs/ (the lane's own testMatch) or allow the inline
  `import(...)` type position explicitly.
  Additionally add `/e2e/specs/` to .github/CODEOWNERS, so a spec that opts out
  of the guard is at least an owner-reviewed diff.

Acceptance criteria:
  - A spec in e2e/specs/ written as `import * as pw from "@playwright/test"`
    fails `npm run test` by name.
  - The same with single quotes fails `npm run test` by name.
  - The same with `const { test } = require("@playwright/test")` fails.
  - `import type { Page } from "@playwright/test"` in e2e/harness/ still passes.
  - `npm run test` on the unmodified tree still passes with no new skips.
  - .github/CODEOWNERS covers /e2e/specs/.

Tests:
  e2e/harness/browser-errors.test.ts, describe "specs use the guarded test".
  Add table-driven cases over the four spellings above, written to a temp file
  under e2e/specs/ and swept, so the guard is tested rather than asserted.
  Then extend scripts/e2e/demonstrate.sh D8 to run the namespace spelling as a
  second RED half, so the demonstration covers what the guard now covers.
  The harness to run this already exists; no new tooling is needed.

Cross-repo implications:
  core: none | user: as above | search: none
  meta: docs/quality/features.json VZ-FOUND-008 must not reach VERIFIED until
  this is closed — every later UI slice's evidence inherits it.

Challenge:
  "Nobody would write the namespace form; the editor autocompletes the named
  form, which IS caught." Two answers. First, the single-quote spelling is the
  named form and is not caught, and nothing in this repository enforces quote
  style. Second, the whole architecture of this PR is the refusal to rely on
  what people would plausibly do — check-required-floor.sh, the coverage
  reporter and check-e2e-lane.sh all exist precisely because "the gate was
  editable by the change it was gating". This gate is too, and the fix is one
  line.
```

```
FINDING 2: check-e2e-lane.sh never asserts the workflow actually RUNS the lane; deleting the step leaves the guard green and the `e2e` check green
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-e2e-lane.sh:37-80
             .github/workflows/e2e.yml:102-105
  requirements: VZ-FOUND-008, VZ-CI-001

Observed:
  The guard's own header claims: "The browser lane's value rests on three
  properties … None of those is observable from a passing run. `ci-guard` runs
  this so that removing one is a named red failure rather than a quiet loss."
  It greps for `docker build`, `docker run`, `E2E_BASE_URL`, `upload-artifact`,
  `playwright-report`, `test-results`, `check-no-test-fixtures-in-image.sh`,
  `merge_group`, `pull_request`, and for `validatePolicy` / `unallowedRecords`
  in e2e/harness/test.ts. It never greps for the step that runs Playwright.

  Three mutations of .github/workflows/e2e.yml, each run through
  `bash scripts/ci/check-e2e-lane.sh <mutant>`:

    m1  delete the `run: npm run e2e` line          -> exit 0  "OK: … still drives the built image"
    m2  replace it with `run: echo skipping`         -> exit 0  "OK: … still drives the built image"
    m3  add `if: false` to the `e2e:` job            -> exit 0  "OK: … still drives the built image"

  control (unmodified workflow)                      -> exit 0

  m3 is caught downstream: a job with `if: false` reports a *skipped*
  check-run, and require-checks.sh fails a required lane that concludes
  anything but `success`. m1 and m2 are NOT caught by anything: the `e2e` job
  still runs, still builds and starts the image, still passes the fixture
  guard, and concludes `success` — having driven no browser. `ci-required`
  then reports "every required check … concluded success", exactly as it did
  on this SHA.

Failure:
  The named defence against a weakened browser lane does not defend against
  the most direct weakening there is. A pull request that deletes five lines
  from e2e.yml produces a fully green `ci-required` on a repository where no
  browser has been opened. The builder's D7 demonstration exercises only the
  artifact-upload mutation, so this gap is invisible in the evidence as filed.

Perspective:
  developer, operator

Recommendation:
  Add two greps to scripts/ci/check-e2e-lane.sh, against the
  comment-stripped copy it already builds ($uncommented):

    grep -qE '(npm run e2e|playwright test)' "$uncommented" \
      || add "it no longer runs the browser lane."
    grep -qE '^\s*if:' "$uncommented" && grep -qE '^\s*if:\s*false' "$uncommented" \
      && add "the e2e job is disabled with \`if: false\`."

  The first is the one that matters; the second is belt-and-braces over the
  case require-checks.sh already catches.

Acceptance criteria:
  - A copy of .github/workflows/e2e.yml with the `npm run e2e` step deleted
    fails `bash scripts/ci/check-e2e-lane.sh` by name, exit 1.
  - The same with the step replaced by `echo` fails by name.
  - The unmodified workflow still passes, exit 0.
  - `bash scripts/ci/require-checks_test.sh` still reports 0 failed.

Tests:
  scripts/e2e/demonstrate.sh, D7. It currently runs one mutation
  (grep -v 'upload-artifact'). Add the lane-step deletion as a second RED half
  — it is the same three lines of shell as the existing one — so the
  demonstration covers the property the guard is supposed to protect.

Cross-repo implications:
  core: none | user: as above | search: none
  meta: scripts/ci/check-e2e-lane.sh is declared a "TWIN (intended)" pattern in
  check-required-floor.sh; if vizra-core and vizra-search grow a browser lane
  they must not copy this gap.

Challenge:
  "`.github/` is under CODEOWNERS, so an owner reviews any change to e2e.yml
  anyway." True, and that is why this is not an immediate exploit. But the
  script exists *because* review alone was judged insufficient for this class
  — the same argument applied to required-checks.txt produced
  check-required-floor.sh, and the same argument applied to the Playwright
  exit code produced the coverage reporter. A guard whose header says "removing
  one is a named red failure" while the most obvious removal is silent is worse
  than no guard, because reviewers trust it.
```

```
FINDING 3: the coverage floor is 1 test per project, not 9; deleting eight of the nine tests keeps the lane green
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/required-projects.ts:27-30
             e2e/harness/coverage-reporter.ts:79-86
             .github/CODEOWNERS:33
  requirements: VZ-FOUND-008

Observed:
      export const REQUIRED_PROJECTS: ReadonlyMap<string, number> = new Map([
        [DESKTOP_PROJECT, 1],
        [MOBILE_PROJECT, 1],
      ]);

  The green line `e2e coverage floor: OK (desktop-chromium-1440=9
  mobile-chromium-390=9)` is a REPORT of what ran, not the floor that was
  enforced. Measured against the real lane:

      npx playwright test --grep "reports liveness"
        -> exit 0
           2 passed
           e2e coverage floor: OK (desktop-chromium-1440=1 mobile-chromium-390=1)

      npx playwright test --grep "__matches_nothing__"
        -> exit 1  "did not satisfy its coverage floor"   (correct)

Failure:
  Wholesale vacuity is caught; attrition is not. A pull request that deletes
  or skips eight of the nine tests per project — or narrows testMatch, or
  renames e2e/specs/ leaving one file — reports `coverage floor: OK` and exits
  0. The floor file itself IS owner-reviewed (CODEOWNERS covers /e2e/harness/),
  but e2e/specs/ is not, so the deletion needs no owner at all. The number the
  chair was told to check ("desktop=9 mobile=9") is therefore not a floor and
  should not be relied on as one.

Perspective:
  developer

Recommendation:
  Raise the two minima from 1 to the count the lane actually runs today, and
  say in the comment that the number is a ratchet:
      [DESKTOP_PROJECT, 9],
      [MOBILE_PROJECT, 9],
  The file is already in a CODEOWNERS path, so lowering it becomes an
  owner-reviewed diff — which is the mechanism the file's own header claims.

Acceptance criteria:
  - `npx playwright test --grep "reports liveness"` (one test per project)
    exits non-zero naming the shortfall.
  - The full lane still exits 0 with `coverage floor: OK (desktop=9 mobile=9)`.
  - Adding a test raises the count without failing; the minima are a floor, not
    an equality.

Tests:
  scripts/e2e/demonstrate.sh, D4. Add a third half (D4c) that runs the lane
  with a --grep selecting one test per project and asserts exit 1, alongside
  the existing zero-collected case.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  "A hard-coded 9 will churn on every PR that adds a test." It will not — it is
  a minimum, not an equality, so adding tests never fails it; only deleting
  below the line does, which is the event we want visible. The real cost is
  updating the number when tests are legitimately consolidated, and that is a
  one-line owner-reviewed diff, which is the point.
```

```
FINDING 4: URL redaction covers the harness's own output only; Playwright traces carry raw query strings and are uploaded as CI artifacts
Severity:    REQUIRED  (before any signed URL exists — i.e. before M1 media)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/redact.ts:30-63
             playwright.config.ts:88-91 (trace/screenshot/video: retain-on-failure)
             .github/workflows/e2e.yml:114-124 (uploads playwright-report/ and test-results/)
             AGENTS.md ("Nothing the harness prints carries a query string")
  requirements: VZ-FOUND-008; meta AGENTS.md § Engineering guardrails
                ("Never log credentials, private signed URLs, or raw private metadata")

Observed:
  I drove the production server with a page that fetched
  /media/photo.jpg?X-Amz-Signature=<value>&X-Amz-Expires=60 and searched every
  artifact the run produced for <value>:

    harness failure message      REDACTED  "http 404: GET …/media/photo.jpg?<redacted: 2 parameter(s)>"
    console message passthrough  REDACTED  (redactUrlsInText rewrote the embedded URL)
    browser-signals.json         REDACTED
    playwright-report/ (HTML)    clean in this run
    test-results/**/trace.zip    LEAK — member `1-trace.network`
    test-results/**/trace.zip    LEAK — member `1-trace.trace`

  The trace is Playwright's own recording, written by the browser driver before
  any harness code sees it; redact.ts cannot reach it. The `e2e` workflow
  uploads `test-results/` wholesale on failure with `retention-days: 14`.

Failure:
  From M1, when vizra-core issues signed media URLs (ADR-005 storage
  capabilities), the first red browser lane on a page holding one will publish
  that signed URL, in full, as a downloadable GitHub artifact for 14 days. That
  is precisely what the meta AGENTS.md forbids, and it is the same shape as the
  defect GitGuardian already caught once on this branch. Nothing is leaking
  today: there is no vizra-core, no signed URL and no private media, and the
  VZ-FOUND-008 ledger entry's `privacy` case list is empty. The exposure
  arrives with M1, not with this PR.

  Secondary: the AGENTS.md sentence "Nothing the harness prints carries a query
  string" is narrowly true (the harness does not print the trace) and broadly
  misleading to a reader deciding whether it is safe to attach a trace.

Perspective:
  member, photographer (their private media URL), operator, developer

Recommendation:
  Two small changes, neither of which needs new tooling:
  (a) Correct the AGENTS.md paragraph to say what is and is not covered:
      harness output and attachments are redacted; Playwright traces, videos
      and screenshots are raw browser recordings and are not.
  (b) Record the M1 precondition in the ledger rather than in prose — the
      options are `trace: "off"` once real signed URLs exist, or a
      post-processing step that rewrites query strings in trace.zip members
      before upload, or scoping the artifact upload to playwright-report/ only.
      Choosing between them is an M1 decision; naming the deadline is this PR's.

Acceptance criteria:
  - AGENTS.md states which artifacts are redacted and which are not.
  - docs/quality/features.json VZ-FOUND-008 carries a privacy case:
    "a signed media URL must not reach an uploaded trace artifact", with
    status UNVERIFIED and a named dependency on the first slice that produces
    one.
  - Before the first slice that renders a signed URL merges, a test proves a
    signed-URL-shaped query string does not survive into any uploaded artifact.

Tests:
  New case in e2e/harness/redact.test.ts is NOT sufficient (it tests the
  function, which is already correct). The honest test is a lane-level one:
  run a spec that fails while the page holds a query-string URL, then assert no
  member of the produced trace.zip contains the value. That harness does not
  exist yet; the smallest change is a bash step in scripts/e2e/demonstrate.sh
  that unzips the trace and greps it, added when M1 gives it a real URL to use.

Cross-repo implications:
  core: none yet — but the first signed-URL slice in vizra-core is the trigger.
  user: as above | search: none
  meta: add the privacy case to the VZ-FOUND-008 ledger entry.

Challenge:
  "This is an M1 problem and does not belong in an M0 PR's findings." Half
  right — it is correctly out of scope to FIX here, which is why it is not a
  blocker. It is in scope to RECORD here, because this PR is the one that
  introduces the artifact upload and the one that asserts in owner-reviewed
  contract text that query strings do not escape. An unrecorded precondition
  discovered by the slice that violates it is how the GitGuardian incident
  happened the first time.
```

```
FINDING 5: the CI artifact-upload path has never executed, and would fail silently if its paths were wrong
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     .github/workflows/e2e.yml:114-124
  requirements: VZ-FOUND-008 (evidence_required: "CI artifact links; retained
                traces for a deliberately failing spec")

Observed:
  Both `e2e` workflow runs in this repository's history concluded success
  (35534195373 at 112291e7, 35533903875 at 951f18b4). The upload step is
  `if: failure()`, so it has never run. Querying the artifacts of both runs
  returns an empty list. The step also sets `if-no-files-found: warn`, so a
  wrong path would warn rather than fail.

  The paths are correct as read (`playwright-report/`, `test-results/`,
  `playwright-browsers.txt` all match playwright.config.ts's `outputDir` and
  `outputFolder`), and I confirmed locally that a failing run does produce
  trace.zip, video.webm, test-failed-1.png and error-context.md under
  test-results/. So the risk is small — but "read the workflow" is the only
  evidence available, and the ledger asks for CI artifact links.

Failure:
  The ledger's evidence_required for VZ-FOUND-008 is not yet satisfiable from
  CI. Nobody has seen this lane produce a downloadable trace.

Perspective:
  developer

Recommendation:
  Nothing in this PR. When the next slice's lane goes red in CI for a real
  reason, link that run's artifact into the ledger entry and mark the
  evidence_required item satisfied. Alternatively change `if-no-files-found`
  to `error` so a wrong path is loud when the day comes.

Acceptance criteria:
  - The VZ-FOUND-008 ledger entry records a CI artifact link from a genuinely
    failing e2e run before it is marked VERIFIED, or records explicitly that
    the requirement is deferred and why.

Tests:
  n/a — this is an evidence-collection item, not a code defect.

Cross-repo implications:
  core: none | user: none | search: none | meta: ledger evidence field.

Challenge:
  "upload-artifact is a pinned, standard action and the paths obviously match."
  Agreed, which is why this is a NIT and not a finding that blocks anything.
  It is recorded so the chair does not mark evidence_required satisfied on a
  workflow that has never run it.
```

---

## What I could not check

- **linux/amd64.** My clone ran on macOS arm64. The CI `e2e` and `docker-build`
  lanes cover the ADR-009 acceptance platform and both are green on this SHA; I
  read their logs and the counts match mine exactly. The local image build I ran
  is arm64 and carries no platform claim.
- **Mixed-content blocking.** Not reachable: the lane drives `http://127.0.0.1`,
  and browsers only block mixed content on `https` pages. UNVERIFIED by
  construction.
- **Cross-origin (opaque) iframe errors.** I tested same-origin `srcdoc` iframes
  (both caught). A genuinely cross-origin iframe's console output is not
  delivered to `page.on("console")` in Chromium; there is no such iframe in this
  application and none is claimed. UNVERIFIED, low risk, worth re-testing when
  embeds land (VZ-… embed slice).
- **Branch protection / CODEOWNERS enforcement.** `.github/CODEOWNERS` is
  committed but, as the file itself says, does nothing until an owner applies a
  ruleset requiring Code Owner review. That is an owner action outside any PR.
  Findings 1 and 3 both lean on CODEOWNERS coverage, and that coverage is
  currently aspirational on **all** paths, not just the ones I name.

## Verdict

**FAIL.**

The engineering here is, with the two exceptions below, the best-defended lane I
have verified in this repository. All five production markers trip independently
and non-redundantly. The guard catches web workers, iframes, pre-navigation head
scripts, aborted requests, swallowed 4xx fetches, mobile-only errors and a
mid-body `test.skip()`. A flaky pass does not hide a first-attempt error. The
bare-array policy collapse the builder documented is real and is refused. The
fixtures genuinely cannot ship, because there are no routes to ship. `ci-required`
enumerated `e2e`, waited for it, and concluded success on this exact SHA with a
manifest that matches the jobs that ran. Every one of the builder's 18
demonstration halves reproduced from my clean clone, and every evidence claim I
checked in the PR body and README was accurate — including the honest platform
caveat and the honest list of what is not claimed.

It fails on two things, both small and both in the same class the PR was written
to defeat:

- **FINDING 1** — the guard every later UI slice depends on is removable by one
  line, in a directory no CODEOWNER covers, and the PR's own contract text
  asserts that it is not. I demonstrated a spec that 404s and throws passing
  `npm run ci` (exit 0) and `npm run e2e` (exit 0, floor OK).
- **FINDING 2** — the guard that is supposed to make a weakened lane "a named
  red failure" passes when the lane step is deleted outright.

Both are a handful of lines. Neither requires rethinking the design. Findings 3
and 4 should be addressed in the same round (3 is one line; 4 is a doc correction
plus a ledger entry). Finding 5 is a note for the chair, not work for the builder.

PASS is not a merge and not VERIFIED; neither is FAIL a rejection of the
approach. VZ-FOUND-008 must not reach VERIFIED until Findings 1 and 2 are closed
and re-verified, because every later UI slice's evidence is only as good as this
harness's inability to lie.

---

# Re-verification at 44dac20

**Verdict: FAIL** — one blocking finding, narrowed to a single line. Four of my
five findings are CLOSED with evidence I reproduced myself. Finding 1 is OPEN by
a much smaller margin than before, and one new finding (fail-open on the
redactor's own failure) is REQUIRED but not blocking.

| | |
|---|---|
| Head SHA verified | `44dac201c120e2a6d0c689cf53aafb218ca341a3` — confirmed unmoved at start and finish |
| Ancestry | `git merge-base --is-ancestor 112291e… HEAD` → **yes**; 2 commits on top (`9a362f7`, `44dac20`) |
| Delta from my FAIL | 74 files, +2694 −651 |
| Environment | macOS arm64, Node v22.14.0, @playwright/test 1.63.0, Chromium `chromium-1243` (already in the cache — I installed no browser); Docker available, 16 GiB free, so the local image build **ran** |
| Clone | fresh, `<scratch>/verify-44dac20/vizra-user`, deleted on completion |

## 1. Commands — every claim matched

| Command | Exit | Result | Builder's claim |
|---|---|---|---|
| `npm ci` | 0 | lockfile consistent | — |
| `npm run ci` | 0 | — | — |
| `npm run test` | 0 | **9 files / 206 tests / 0 skipped** | 9 / 206 / 0 — **matches** |
| `bash scripts/ci/require-checks_test.sh` | 0 | **86 cases / 93 assertions / 0 failed** | 86 / 93 — **matches** |
| `npm run e2e` | 0 | **18 passed, 0 skipped**; `coverage floor: OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9)` | — |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | `OK … (desktop=9/9 mobile=9/9)` | — |
| `npm run e2e:demos` (Docker) | 0 | **39 halves passed, 0 blocked, 0 failed** | 39 halves — **matches** |
| `npx vitest run eslint-rules/no-unguarded-playwright-import.test.mjs` | 0 | 33 tests (the +1 file, +29 tests) | — |

Both images I built were deleted; no other agent's images, containers or volumes
were touched.

## 2. FINDING 1 — the bypass. **OPEN**, narrowed to one line.

The regex became an AST rule (`eslint-rules/no-unguarded-playwright-import.mjs`)
that bans any reference to the package and restricts `test`/`expect` to the
harness entry. I put 19 spellings through the **real** ESLint configuration.

**Caught (14)** — named double-quote; named single-quote; namespace; default;
side-effect; `require()`; dynamic `import()`; `import type { test }` (smuggling);
plain template literal; `@playwright/test/lib/index`; `playwright/test` named
form; `import pw = require(...)`; `createRequire`; and (correctly allowed)
`import type { Page }` and inline `import("@playwright/test").Page`.

My two original bypasses are both dead: the namespace form and the
single-quoted named form are now errors. The vitest sweep additionally lints
every real spec with the repository's own config and asserts the rule is
severity 2 for `e2e/specs/`, and `/e2e/specs/` and `/e2e/demos/` are now in
CODEOWNERS.

**Lint-level gaps (4), of which one is a working exploit.** I ran each to
ground — lint, then TypeScript, then Playwright, then the full lane:

| Spelling | Lint | Runs? | Lane |
|---|---|---|---|
| `import * as pw from "playwright/test"` (unscoped package) | passes | yes, spec passes on the broken page | **red overall** — loads a second runner copy and fails all 18 real tests. Loud, not silent. |
| `require("@playwright" + "/test")` (concatenated specifier) | passes | yes, spec passes on the broken page | **`npm run ci` exit 2** — TypeScript `TS7031: Binding element 'page' implicitly has an 'any' type`. Caught incidentally by `noImplicitAny`. |
| `` await import(`@playwright/${part}`) `` | passes | **no** — `require() cannot be used on an ESM graph with top-level await` | n/a |
| `/* eslint-disable vizra/no-unguarded-playwright-import */` | passes | yes | **GREEN. The harness lies.** |

The last one, measured on the pristine tree with one added spec whose page
404s a sub-resource and throws an uncaught `Error` on every load:

```
e2e/specs/__b2.spec.ts
  /* eslint-disable vizra/no-unguarded-playwright-import */
  import { test } from "@playwright/test";

npm run ci                                   -> exit 0   (9 files / 206 tests)
npx playwright test (full lane, floor armed) -> exit 0   20 passed
                                                e2e coverage floor: OK (desktop=10/9 mobile=10/9)
node scripts/ci/check-coverage-floor-ran.mjs -> exit 0
bash scripts/ci/check-e2e-lane.sh            -> exit 0
```

`eslint.config.mjs` sets neither `linterOptions.noInlineConfig` nor
`reportUnusedDisableDirectives`, and the directive is *used*, so the latter
would not help anyway. The vitest sweep lints through the same ESLint, so it
inherits the suppression.

**Why this is still blocking, and why it is much less bad than before.** The
comment names the rule it defeats, so it is self-incriminating in a diff, and
`/e2e/specs/` is now owner-reviewed — a real improvement. But AGENTS.md now
states as contract that "a spec may not reach `@playwright/test` at all", and
that remains defeasible by one comment with every automated gate green. The fix
is one line: `linterOptions: { noInlineConfig: true }` on the `e2e/specs/**`,
`e2e/demos/**` config block. (`playwright/test` should also be added to the
rule's package list, and the unscoped-namespace case asserted, so the defence is
the rule rather than a module-loading accident.)

## 3. FINDING 2 — the lane guard. **CLOSED.**

`check-e2e-lane.sh` now delegates to `check-e2e-lane.mjs`, which **parses** the
workflow with the pinned `yaml` package and asserts the step graph. I ran 18
mutations; **17 are red by name**, and the unmodified control passes.

| Mutation | Result |
|---|---|
| delete the `npm run e2e` step | red — "no step runs the browser lane" |
| replace it with `echo skipping` | red — same, and it names the closest step |
| `npm run e2e \|\| true` | red |
| `npm run e2e; true` | red |
| `if: false` on the step | red |
| `continue-on-error: true` / `"true"` / `${{ expression }}` | red (all three) |
| multi-line `run: \|` with the command buried after `exit 0` | red |
| `shell: python` | red |
| `E2E_BASE_URL` at a port no `docker run --publish` exposes | red |
| `if: false` on the **job** | red |
| remove the floor re-check step | red |
| remove the redaction step | red |
| `if-no-files-found` back to `warn` | red |
| second job named `e2e` (shadow) | red — YAML duplicate-key parse error, fails closed |
| add a `paths:` filter to `pull_request` | red |

**Residual, non-exploitable:** `working-directory: docs` on the lane step passes
the guard. It is not a silent bypass — the only `package.json` outside
`node_modules`/`.next` is the repository root's, and `.next` does not exist on
the runner (the workflow builds a Docker image, not a local build), so the step
would fail loudly with a missing script. Worth adding for defence in depth;
not a finding.

## 4. FINDING 3 — the coverage floor. **CLOSED.**

Minima moved to `e2e/harness/required-projects.json` (9/9, CODEOWNERS-covered),
read by both the in-process reporter and a new out-of-process CI step.

**Every filtered form is refused**, which is stronger than raising the numbers:

```
--grep "reports liveness"   red — the run was FILTERED (--grep)
-g "reports liveness"       red — (-g)
--grep-invert               red — (--grep-invert)
--grep=reports              red — (--grep)
e2e/specs/health.spec.ts    red — file filter "e2e/specs/health.spec.ts"
--project=desktop-…         red — (--project)
--shard=1/2                 red — (--shard)
--last-failed               red — (--last-failed)
no filter                   exit 0, coverage floor: OK (9/9 9/9)
```

**Deleting a test goes red.** I removed one test from `home.spec.ts`: the lane
exited 1 with `ran 8 passing test(s), and the floor is 9` from the in-process
reporter, and the out-of-process step named the same shortfall for both
projects.

**The stale-report attack does not work.** I wrote a good 18-test report, then
deleted the `json` reporter from `playwright.config.ts` (the edit the PR being
gated could make) and ran a short filtered run. Playwright clears
`playwright-report/` at run start, so the checker got ENOENT and failed closed —
"A lane whose report is missing did not run; that is a failure, not a silence."
Exit 1 (verified with a clean exit-code capture: full run → 0, missing report →
1). Both directories are gitignored (`.gitignore:16,20`) and CI checks out
fresh, so no stale file can be present there either.

## 5. FINDING 4 — privacy. **The query-string case is CLOSED. A scope statement is still owed, and there is a new fail-open.**

### The headline case, clean

I re-ran my original test with the sentinel appearing **only** as a URL query
value — no `page.evaluate` parameter, no body, no header:

```
page.goto("/media/photo.jpg?X-Amz-Signature=PUREQUERYzz9911&X-Amz-Expires=60")

before redaction:  3 members contain the sentinel
                   (1-trace.network, 1-trace.trace, test.trace)
after  redaction:  0 members contain the sentinel
                   path "media/photo.jpg" still readable in 6 members
```

### The real CI artifact

Better than my local run: I downloaded the artifact from run **35536837315**
(item 6) and unpacked every nested archive. In the bytes GitHub actually served:

```
239 occurrences of "?<redacted>"
  0 absolute URLs carrying a live query
  0 relative URLs carrying a live query
  0 non-empty "queryString" arrays
host and path intact, e.g. http://127.0.0.1:3000/__vizra_e2e_fixture__/media/photo.jpg
```

The redaction demonstrably ran in CI on a genuinely uploaded artifact.

### Per-channel coverage, measured

I built a failing run carrying a distinct sentinel in eleven channels, ran
`redact-artifacts.sh`, and swept every member of every archive.

| Channel | Covered? |
|---|---|
| URL query string | **yes** (clean test above) |
| URL fragment | **yes** |
| `Location` response header (it is a URL) | **yes** |
| `Authorization` request header | no — survives in `1-trace.network` |
| `Cookie` request header | no — survives in `1-trace.network` |
| `x-amz-security-token` request header | no — survives in `1-trace.network` |
| `Set-Cookie` response header | no — survives in `1-trace.network` |
| POST body | no — survives in `resources/*.txt` (script header says bodies are out of scope) |
| response body | no — same |
| console message (a bare token, not a URL) | no — survives in `*-trace.trace` |
| DOM snapshot / attachment | no — survives |
| **Playwright call parameters** (`page.evaluate`/`page.fill` arguments) | no — survives in `*-trace.trace`; named by nobody, and the channel a real login spec would use |

**Correction to my own method:** my first multi-channel probe passed all eleven
sentinels through one `page.evaluate` argument, which put every one of them into
the trace as a call parameter regardless of channel. That is why "query string"
appeared to survive. The clean re-run above is the one that counts. The header
results stand independently, because they land in `1-trace.network`, which
records the real wire headers.

**None of this can leak anything today** — nothing authenticates, there is no
vizra-core, no session cookie and no signed URL, and the VZ-FOUND-008 ledger
entry's privacy case list is empty. All of it becomes live at M1.

**What AGENTS.md says.** Lines 197–218 claim "**No URL query string leaves this
repository, in any artifact**" — literally true and now verified — and state the
`.png`/`.webm` exclusion. They do **not** say that headers, cookies, bodies or
Playwright call parameters are uncovered; worse, "keeping origin, path,
**headers** and timings readable" is presented as a feature, which a reader
could mistake for safety. That scope statement is still owed.

### New: the upload is fail-open on the redactor's own failure

`redact-artifacts.sh` handles an unparseable archive correctly — I fed it a
corrupt `.zip` and it warned and **deleted** the file rather than uploading
unredacted bytes, exit 0, sentinel gone. Fail-closed, verified.

But the redact step and the upload step both carry `if: failure()` and nothing
links them. `failure()` is true when *any* prior step failed, so if the redactor
itself exits non-zero — exit 2 on a missing `perl`/`unzip`/`zip`, exit 1 on a
repack failure — the upload still runs and publishes the **unredacted** tree.
See FINDING 7.

## 6. Item 6 — the artifact proof. **Confirmed, and FINDING 5 is CLOSED.**

```
run 35536837315  workflow e2e  conclusion FAILURE
  branch chore/e2e-artifact-upload-proof, sha 0401d5ea, event pull_request
  title "THROWAWAY — prove the e2e artifact path executes (do not merge)"
artifact playwright-artifacts-35536837315-1, 1,251,268 bytes,
  expired false, expires 2026-10-04 (14 days)
PR #4: state closed, merged false
branches now: feat/m0-browser-env, main   <- chore/e2e-artifact-upload-proof deleted
```

`if-no-files-found: error` is set in the workflow and enforced by the parser
(mutation m16 is red). The ledger's `evidence_required` — "CI artifact links;
retained traces for a deliberately failing spec" — is now satisfiable from a
real run, and I verified the artifact's contents rather than its existence.

## 7. Item 7 — test changes and the two CI fixes. **All sound.**

**`browser-errors.test.ts` −20/+62.** The removed `it.each` regex assertion is
replaced by two strictly stronger ones: (a) run the repository's real ESLint
config over every real spec and demo, assert zero violations of the rule **and**
assert the sweep actually covered every file (so a file ESLint declined to lint
cannot pass silently); (b) assert the rule fires at severity 2 for a path under
`e2e/specs/`, using a spelling the old regex missed. The `files.length >= 4`
vacuity check is retained; the `readFileSync` import removal is consequential.
**Nothing was weakened.**

**The two D4a transcripts.** Regenerated machine output, not assertions: the
floor label changed (`required-projects.ts` → `.json`), the minimum changed
(1 → 9), and the new `the run was FILTERED (--grep)` diagnostic appears. Strictly
more informative, faithful to the code. **Legitimate.**

**`ci-guard` never ran `npm ci`.** Fixed by adding `setup-node` + `npm ci`, and —
correctly — by adding `package.json` and `package-lock.json` to the job's path
filter, so a lockfile change triggers the guard that now depends on it. The
missing `yaml` package failed loudly (13 named failures), which is the right
failure mode; it is now simply not missing.

**ESLint was linting `playwright-report/`.** Now ignored, along with
`test-results/`. `git ls-files` shows **no tracked file** under either path and
both are gitignored, so the ignore cannot hide a real source file. Sound.

## 8. Item 8 — CI on 44dac20

```
ci-required   success 20:59:01      contract  success      docker-build success
e2e           success 20:58:37      frontend  success      guard        success
deps-scan     success               image-scan success
GitGuardian Security Checks         FAILURE
```

`ci-required` log on this SHA:

```
  - frontend
  - contract
  - ?guard
  - ?docker-build
  - e2e
waiting: frontend … contract … guard … docker-build … e2e (in_progress)
waiting: docker-build (in_progress) e2e (in_progress)
waiting: e2e (in_progress)
OK: every required check on 44dac201c120e2a6d0c689cf53aafb218ca341a3 concluded success.
```

Every manifest lane executed and concluded `success`; `e2e` is required,
non-optional, and `ci-required` waited for it.

**GitGuardian**: still "2 secrets … from the scan of **4** commits" — the same
two historical findings from `951f18b`, rescanned across the now-four-commit PR.
I diffed `112291e..44dac20` for credential-shaped additions and for live query
strings: **none**. The only `hmr?id=` occurrences at this head are the prose
example in `redact.ts` and the `PLACEHOLDER-not-a-real-id` constant in
`redact.test.ts`. A squash-merge drops `951f18b`. The check still needs
deliberate owner dismissal rather than being merged past.

---

## Findings

```
FINDING 6: one `eslint-disable` comment still opts a spec out of the browser-error guard, with every automated gate green
Severity:    BLOCKER
Confidence:  high
Supersedes:  FINDING 1 (the two import spellings I reported are both closed)

Affected:
  repo:      vizra-user
  files:     eslint.config.mjs:29-45 (no `linterOptions`)
             eslint-rules/no-unguarded-playwright-import.mjs:53 (PACKAGE list)
             e2e/harness/browser-errors.test.ts:204-224 (the sweep lints through the same ESLint)
             AGENTS.md (the "A spec may not reach `@playwright/test` at all" paragraph)
  requirements: VZ-FOUND-008

Observed:
  On the pristine tree at 44dac20, one added spec:

      /* eslint-disable vizra/no-unguarded-playwright-import */
      import { test } from "@playwright/test";
      test("…", async ({ page }) => {
        await page.addInitScript(() => { … 404 a sub-resource, then throw … });
        await page.goto("/"); await page.waitForLoadState("networkidle");
      });

      npm run ci                                   exit 0  (9 files / 206 tests)
      npx playwright test  (full lane, floor armed) exit 0  20 passed
                                                     coverage floor: OK (desktop=10/9 mobile=10/9)
      node scripts/ci/check-coverage-floor-ran.mjs  exit 0
      bash scripts/ci/check-e2e-lane.sh             exit 0

  eslint.config.mjs sets neither `linterOptions.noInlineConfig` nor
  `reportUnusedDisableDirectives`. The directive is USED, so the latter would
  not catch it regardless. The vitest sweep in browser-errors.test.ts calls the
  same ESLint, so the suppression applies there too — it reported no violation.

  Separately, the rule's PACKAGE constant is `@playwright/test` only, so the
  unscoped `playwright/test` (which node_modules/playwright/test.js re-exports)
  is not a package reference. `import * as pw from "playwright/test"` passes
  lint and runs; it happens to fail the lane only because loading a second
  runner copy breaks all 18 real tests. That is a module-loading accident, not a
  control.

Failure:
  The guard every later UI slice depends on is still optional, at the cost of
  one comment. AGENTS.md states as reviewed contract that "a spec may not reach
  `@playwright/test` at all"; that is false while an inline directive can turn
  the rule off for a file.

Perspective:
  developer, and through them visitor and member, who receive the broken page.

Recommendation:
  Two lines, in the config block that already exists:

      files: ["e2e/specs/**/*.ts", "e2e/demos/**/*.ts"],
      linterOptions: { noInlineConfig: true },
      rules: { "vizra/no-unguarded-playwright-import": ["error", { … }] },

  and add "playwright/test" to the rule's package list (a second constant beside
  PACKAGE, matched the same way).

Acceptance criteria:
  - A spec in e2e/specs/ carrying
    `/* eslint-disable vizra/no-unguarded-playwright-import */` fails
    `npm run ci`.
  - So does `// eslint-disable-next-line vizra/no-unguarded-playwright-import`.
  - So does `/* eslint-disable */` with no rule named.
  - `import * as pw from "playwright/test"` fails lint by name.
  - The unmodified tree still passes `npm run ci` with 206 tests and no new skips.

Tests:
  eslint-rules/no-unguarded-playwright-import.test.mjs for the `playwright/test`
  cases (RuleTester, the harness exists). For the disable directive, RuleTester
  cannot express it — add a case to browser-errors.test.ts alongside the existing
  "the rule is configured as an error" test, linting text that carries the
  directive and asserting the violation still reports. Then add a RED half to
  scripts/e2e/demonstrate.sh D8 for the directive, matching the five that are
  already there.

Cross-repo implications:
  core: none | user: as above | search: none
  meta: VZ-FOUND-008 must not reach VERIFIED until this is closed.

Challenge:
  "The comment names the rule it defeats, and /e2e/specs/ is now owner-reviewed —
  a reviewer cannot miss it." That is the strongest argument and it is why this
  is a one-line fix rather than a redesign. But every other control in this PR
  was built on the principle that review is not the mechanism: CODEOWNERS covers
  .github/ and the workflow parser was still written. A control that is off by
  default for any file that asks is not default-deny, and `noInlineConfig` costs
  one line.
```

```
FINDING 7: if the artifact redactor fails, the unredacted artifacts are uploaded anyway
Severity:    REQUIRED  (not blocking for this PR — nothing authenticates yet)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     .github/workflows/e2e.yml:122-124 (redact step, `if: failure()`)
             .github/workflows/e2e.yml:136-137 (upload step, `if: failure()`)
             scripts/ci/redact-artifacts.sh:57-62 (exit 2), :151-155 (exit 1)
             scripts/ci/check-e2e-lane.mjs:222-249
  requirements: VZ-FOUND-008; meta AGENTS.md § Engineering guardrails

Observed:
  Both steps are gated on bare `if: failure()`, and nothing links them. GitHub's
  `failure()` is true when ANY earlier step in the job failed, so a redactor that
  itself exits non-zero does not stop the upload — it satisfies its condition.

  redact-artifacts.sh has two hard-failure paths:
    exit 2  `perl`, `unzip` or `zip` missing (lines 57-62)
    exit 1  a repack failure after the original archive was already removed (151-155)

  In both cases `test-results/` and `playwright-report/` are left partially or
  wholly unredacted and the next step publishes them for 14 days.

  The unparseable-archive path IS fail-closed, and I verified it: given a corrupt
  `.zip`, the script warned, deleted the file, exited 0, and the sentinel was
  gone from the tree.

  check-e2e-lane.mjs requires the redact step to exist and to precede the upload
  (mutation m15 is red) but does not require the upload to be conditional on the
  redaction having succeeded.

Failure:
  From M1 a runner missing one of three tools, or one corrupt repack, publishes
  signed media URLs and session cookies as a downloadable artifact. Today the
  artifacts contain nothing private, so nothing leaks now.

Perspective:
  member, photographer, operator

Recommendation:
  Give the redact step an `id` and gate the upload on it:

      - name: Redact URL query strings in the artifacts
        id: redact
        if: failure()
        run: bash scripts/ci/redact-artifacts.sh test-results playwright-report

      - name: Upload Playwright artifacts
        if: failure() && steps.redact.outcome == 'success'

  and add the corresponding assertion to check-e2e-lane.mjs, where every other
  property of this step graph is already asserted.

Acceptance criteria:
  - A workflow whose upload step is gated on bare `failure()` fails
    `check-e2e-lane.sh` by name.
  - The committed workflow passes.
  - A run in which the redactor exits non-zero uploads nothing.

Tests:
  scripts/e2e/demonstrate.sh D7 — a mutation that removes the
  `steps.redact.outcome` condition, asserted red, beside the existing five.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  "ubuntu-24.04 ships perl, unzip and zip; this cannot happen." Probably true
  today, and it is why this is REQUIRED rather than BLOCKER. But the runner image
  is not this repository's to pin, the repack path is reachable on a full disk,
  and the whole point of `if-no-files-found: error` — added in this same round —
  was that a privacy control which has never executed must fail loudly rather
  than quietly.
```

```
FINDING 8: AGENTS.md's redaction section does not state which credential channels are uncovered
Severity:    SHOULD  (must-fix before M1)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md:197-218
             scripts/ci/redact-artifacts.sh:36-48
  requirements: VZ-FOUND-008 (propose a privacy case on the ledger entry)

Observed:
  AGENTS.md:197 reads "**No URL query string leaves this repository, in any
  artifact.**" — literally true, and I verified it end to end, including in the
  real CI artifact from run 35536837315. Line 214 names the deliberate
  `.png`/`.webm` exclusion.

  It does not name the other uncovered channels. I measured them against a
  failing run: `Authorization`, `Cookie`, `x-amz-security-token` and `Set-Cookie`
  survive in `1-trace.network`; POST and response bodies survive in
  `resources/*.txt`; a bare (non-URL) token in a console message, in a DOM
  snapshot, and — the one nobody has named — in a **Playwright call parameter**
  (`page.evaluate`/`page.fill` arguments) survives in `*-trace.trace`. File and
  directory names are never rewritten at all; they derive from test titles.

  AGENTS.md:211-212 presents "keeping origin, path, **headers** and timings
  readable" as a feature, which reads as reassurance about the very channel that
  is uncovered.

Failure:
  A later slice's author reads "no query string leaves this repository" plus
  "headers readable" and concludes it is safe to let an authenticated page reach
  a red lane. Nothing leaks today; the first authenticated slice is where this
  is discovered, which is how the GitGuardian incident happened the first time.

Perspective:
  developer, member, photographer

Recommendation:
  Add four lines to the existing section naming what is NOT covered — request
  and response headers (Authorization, Cookie, Set-Cookie, and bearer-ish
  vendor headers), request and response bodies, Playwright call parameters, and
  artifact file names — and record the M1 precondition on the ledger rather than
  in prose.

Acceptance criteria:
  - AGENTS.md names each uncovered channel.
  - docs/quality/features.json VZ-FOUND-008 carries a privacy case:
    "no session cookie, Authorization header or signed URL reaches an uploaded
    artifact", status UNVERIFIED, with a named dependency on the first slice
    that authenticates.
  - Before that slice merges, a demonstration proves it, using
    scripts/e2e/sweep-artifacts.sh, which already does exactly this search.

Tests:
  scripts/e2e/demonstrate.sh D9 already produces a failing run and sweeps every
  member for a sentinel. Extend it with a header-channel sentinel when the first
  authenticated slice gives it a real credential to use; the harness exists.

Cross-repo implications:
  core: the first signed-URL / session slice in vizra-core is the trigger.
  user: as above | search: none | meta: add the privacy case to the ledger entry.

Challenge:
  "The section is about query strings and says so; it is not wrong." Agreed — it
  is accurate, which is why this is SHOULD and not a correctness finding. The
  objection is that a reader deciding whether a red lane is safe will read this
  section and nothing else, and the sentence that follows tells them headers are
  kept.
```

## Status of my five original findings

| # | Finding | Status |
|---|---|---|
| 1 | spec can bypass the guard | **OPEN** — both my spellings closed; superseded by FINDING 6 (the `eslint-disable` directive) |
| 2 | lane guard does not assert the lane runs | **CLOSED** — 17/18 mutations red by name; the one that passes fails loudly at runtime |
| 3 | floor is 1 per project, not 9 | **CLOSED** — 9/9 in a CODEOWNERS-covered JSON, every filter form refused, deletion red, re-checked out of process, stale report fails closed |
| 4 | traces carry raw query strings | **CLOSED for query strings** — verified locally (3→0, path readable) and in the real uploaded CI artifact (239 `?<redacted>`, 0 live queries). Residual scope statement → FINDING 8; new fail-open → FINDING 7 |
| 5 | artifact upload path never executed | **CLOSED** — run 35536837315 uploaded 1.25 MB, `if-no-files-found: error` set and enforced, PR #4 closed unmerged, branch deleted |

## What I could not check

- **linux/amd64.** Verified on macOS arm64; the CI `e2e` and `docker-build` lanes
  cover the ADR-009 acceptance platform and are green on this SHA, and the CI
  artifact I unpacked was produced there.
- **Branch protection.** CODEOWNERS now covers `/e2e/specs/` and `/e2e/demos/`,
  which FINDING 6 partly leans on — but as the file itself says, it does nothing
  until an owner applies a ruleset. Still aspirational on every path.
- **Nested archives inside a trace member.** `redact-artifacts.sh` byte-rewrites
  a `.zip` found inside an extracted tree rather than recursing into it, and
  `sweep-artifacts.sh` enumerates archives once. No Playwright artifact nests
  archives today, so this is theoretical; I did not construct one.

## Verdict at 44dac20

**FAIL**, on FINDING 6 alone.

This round closed four of my five findings with work that is better than what I
asked for: a real AST rule instead of a better regex, a YAML parser instead of a
better grep, a floor that refuses every filtered run rather than just a higher
number, and an artifact-redaction path proven on a genuinely uploaded CI
artifact rather than argued. Fourteen of nineteen bypass spellings are now
errors, seventeen of eighteen workflow mutations are red by name, eight of eight
filter forms are refused, and 39 of 39 demonstration halves reproduced from my
clean clone. Every count the builder claimed matched mine exactly.

What stops it is one line of configuration. `eslint.config.mjs` permits inline
directives, so `/* eslint-disable vizra/no-unguarded-playwright-import */` still
buys a spec an exemption from the one control this entire slice exists to
provide, with `npm run ci`, the full lane, the coverage floor, the out-of-process
floor re-check and the lane guard all green on a page that 404s and throws. The
remedy is `linterOptions: { noInlineConfig: true }` on a config block that
already exists, plus adding `playwright/test` to the rule's package list so the
unscoped namespace form is refused by the rule rather than by a module-loading
accident.

FINDING 7 should be fixed in the same round (two lines in the workflow and one
assertion in the parser). FINDING 8 is a documentation and ledger change, not
code.

VZ-FOUND-008 must not reach VERIFIED until FINDING 6 is closed and
re-verified. PASS is not a merge and FAIL is not a rejection of the approach —
the approach is now sound.
