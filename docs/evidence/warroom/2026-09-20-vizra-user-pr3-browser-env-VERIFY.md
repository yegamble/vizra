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

---

# Re-verification at 0ac9fb6

**Verdict: FAIL** — one blocking finding, one line to fix, in the same class as
FINDING 6 but through a different door that this round was not asked to close.
**Findings 6, 7 and 8 are each CLOSED for everything the round was scoped to
do**, and the work is the best of the three rounds.

| | |
|---|---|
| Head SHA verified | `0ac9fb6a820d50ef030f86f053409b967d2beec8` — confirmed unmoved at start and finish |
| Ancestry | `git merge-base --is-ancestor 44dac20… HEAD` → **yes**; 2 commits on top (`edd70cb`, `0ac9fb6`) |
| Delta | 52 files, +1100 −287 |
| Environment | macOS arm64, Node v22.14.0, @playwright/test 1.63.0, Chromium `chromium-1243` (already cached — I installed no browser); Docker available, 16 GiB free, local image build **ran** |
| Clone | fresh, `<scratch>/verify-0ac9fb6/vizra-user`, deleted on completion |

**Scope check.** The delta touches exactly Findings 6, 7 and the wording half of
8: `eslint.config.mjs`, the rule, `browser-errors.test.ts`, the workflow's
redact/upload gate, `check-e2e-lane.mjs`, `AGENTS.md`, the new
`no-credentials-in-specs.test.ts`, `demonstrate.sh`, `require-checks_test.sh`,
and regenerated transcripts. The only thing outside that list is
`e2e/demos/console-error.demo.ts`, where two `eslint-disable-next-line
no-console` comments were replaced by a config-level `no-console: "off"` for
`e2e/demos/**` — a direct and necessary consequence of `noInlineConfig`. Nothing
out of scope.

## 1. Counts — every claim matched

| Command | Exit | Result | Claim |
|---|---|---|---|
| `npm ci` | 0 | lockfile consistent | — |
| `npm run ci` | 0 | — | — |
| `npm run test` | 0 | **10 files / 227 tests / 0 skipped** | 10 / 227 / 0 — **matches** |
| `bash scripts/ci/require-checks_test.sh` | 0 | **92 cases / 99 assertions / 0 failed** | 92 / 99 — **matches** |
| `npm run e2e` | 0 | 18 passed; `coverage floor: OK (9/9 9/9)` | — |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | `OK … (9/9 9/9)` | — |
| `npm run e2e:demos` | 0 | **51 halves passed, 0 blocked, 0 failed** | 51 halves — **matches** |

**A correction against myself.** My first demo run reported 49/51 with D4c red.
That was my own contamination: I ran the attack battery, which repeatedly writes
and deletes `e2e/specs/__atk.spec.ts`, *concurrently* with the demo suite, so
D4c's run saw a tenth spec and D4c-GREEN crashed on the `playwright/lib/index`
probe that happened to be on disk at that moment. Re-run on a pristine tree with
nothing else touching the repository: **51/51, exit 0.** The builder's claim is
correct and my first number was wrong.

## 2. FINDING 6 — **CLOSED.**

`linterOptions: { noInlineConfig: true }` on the `e2e/specs/**`, `e2e/demos/**`
block; `PACKAGES` widened to `["@playwright/test", "playwright/test", "playwright"]`.

**My exact 44dac20 exploit, verbatim, now fails:**

```
/* eslint-disable vizra/no-unguarded-playwright-import */
import { test } from "@playwright/test";      (page 404s a sub-resource and throws)

npm run ci  ->  exit 1
  1:1  warning  '/* eslint-disable … */' has no effect because you have
                'noInlineConfig' setting in your config
  2:1  error    This file must not reference `@playwright/test` …
                vizra/no-unguarded-playwright-import
```

**All twelve spellings I tried are errors** — six inline-directive forms and
four package spellings, plus the two controls:

| Form | Result |
|---|---|
| `/* eslint-disable RULE */` | caught |
| `// eslint-disable-next-line RULE` | caught |
| `// eslint-disable-line RULE` | caught |
| `/* eslint RULE: "off" */` | caught |
| `/* eslint RULE: 0 */` | caught |
| `/* eslint-disable */` (no rule named) | caught |
| `/* global test */` + disable | caught |
| `import { test } from "playwright/test"` | caught |
| `import * as pw from "playwright/test"` | caught |
| `import { chromium } from "playwright"` | caught |
| `import x from "playwright/lib/index"` | caught |
| `import x from "playwright-extra"` | correctly **allowed** — prefix over-match avoided |

**Pinned both ways, and the pin bites.** `browser-errors.test.ts` asserts the
setting via `calculateConfigForFile` *and* the behaviour for four comment forms
*and* the unscoped spelling. Deleting the `linterOptions` line → **5 tests fail**,
naming both the missing setting and each suppressed directive.

**`no-console` for demos moved into config, correctly.** Demos that must log
still can (`e2e/demos/**` → `no-console: "off"`, and the 51-half suite passes);
specs still cannot — a `console.log` in `e2e/specs/**` is an error, and with
`noInlineConfig` a spec can no longer excuse one with a comment either.

## 3. FINDING 7 — **CLOSED.**

`id: redact` on the redactor; upload gated on
`failure() && steps.redact.outcome == 'success'`; the parser asserts it.
**8 of 11 mutations red by name**, including both traps the chair named:

| Mutation | Result |
|---|---|
| upload back to bare `failure()` | red — "not gated on the redaction having SUCCEEDED" |
| `steps.redact.conclusion` instead of `.outcome` | red |
| gate on `always()` | red — "not gated on `failure()`" |
| gate on `outcome != 'skipped'` (ran, not succeeded) | red |
| remove the step `id` | red — "cannot be gated on whether it succeeded" |
| redactor removed | red |
| `continue-on-error` on the redactor | red — "would report `success` however it exits" |
| upload moved before the redactor | red |
| `actions/upload-artifact` replaced by another action | red — "no step uploads artifacts" |

### CI proof — run 35538966116

```
workflow e2e, branch chore/e2e-redactor-failure-proof, sha b87c3b12, conclusion FAILURE

  Browser lane (desktop 1440, mobile 390)      failure
  The coverage floor was actually satisfied    skipped
  Redact URL query strings in the artifacts    FAILURE
  Upload Playwright artifacts                  SKIPPED
  artifacts: { "count": 0, "names": [] }
```

Exactly the behaviour the fix promises: the redactor failed, the upload did not
run, and **zero bytes were published**. PR #5 `state: closed, merged: false`;
branch `chore/e2e-redactor-failure-proof` is gone from the branch list.

## 4. FINDING 8 (wording + guard) — **CLOSED**, with an honest caveat.

**The "NOT covered" table in AGENTS.md matches my measurements channel for
channel** — `Authorization`, `Cookie`, `Set-Cookie`, vendor token headers
(`1-trace.network`); request and response bodies (`resources/*`); non-URL console
tokens, DOM snapshots, and **Playwright call parameters** (`*-trace.trace`);
artifact file and directory names; `.png`/`.webm`. The misleading sentence that
offered "headers … readable" as a feature is **gone**, and the table is
introduced with "Read this list before you decide a red lane is safe to share."
That is a better scope statement than I asked for.

**The tripwire is a tripwire.** `e2e/harness/no-credentials-in-specs.test.ts`
catches all five real patterns I threw at it — `page.fill` on a password field,
`storageState`, `setExtraHTTPHeaders({Authorization})`, `addCookies`, and a
signed-URL shape — and an ordinary spec passes. It is evaded by anything that
isn't in its pattern list:

| Evasion | Result |
|---|---|
| `pressSequentially` instead of `.fill(` | evades |
| `page.evaluate` setting `document.cookie` | evades |
| credentials read from `process.env` | evades |
| a login helper in `e2e/harness/` (outside the swept dirs) | evades |

**Is it described honestly?** Mostly yes, and better than most: AGENTS.md
enumerates the exact patterns it matches rather than claiming coverage, and the
file's own header says "This is a source sweep, not a type check: the point is
to be impossible to satisfy accidentally." The one overstatement is framing —
AGENTS.md says the hard rule is what the test "asserts", where it in fact
*samples*. One sentence ("it catches the accident, not the determined author")
would close it. Not blocking; recorded as a residual.

## 5. Regression sweep — Findings 2, 3, 5 stay **CLOSED**

Three canaries each, all red:

```
F2  delete the lane step           exit 1
    npm run e2e || true            exit 1
    if: false on the job           exit 1
F3  --grep one test                exit 1   (the run was FILTERED)
    --project one project          exit 1
    delete one test                exit 1   (8 < 9)
F5  if-no-files-found: warn        exit 1
    drop playwright-report/        exit 1
    redactor removed               exit 1
```

**Privacy still holds**: a pure query-string sentinel went 3 members → **0**
after `redact-artifacts.sh`, with `media/photo.jpg` still readable.

**No test weakened or deleted since 44dac20.** `browser-errors.test.ts` +77/−0,
`require-checks_test.sh` +45/−0, `no-credentials-in-specs.test.ts` +142 new. The
only removed lines in any test or spec file are the two
`eslint-disable-next-line no-console` comments in the demo (replaced by config,
as `noInlineConfig` requires) and one comment in the rule's test — which was
replaced by a **broader** comment plus two new valid cases (`playwright-extra`,
`playwrightish`), and I confirmed `playwright-extra` is still allowed. The rule
test went +42/−1 and gained the three unscoped-package error cases.

## 6. CI on 0ac9fb6

```
ci-required success 21:40:17   contract success   docker-build success
e2e         success 21:39:55   frontend success   guard        success
deps-scan   success            image-scan success
GitGuardian Security Checks    FAILURE

  - frontend / - contract / - ?guard / - ?docker-build / - e2e
waiting: frontend … contract … guard … docker-build … e2e (in_progress)
waiting: e2e (in_progress)   x2
OK: every required check on 0ac9fb6a820d50ef030f86f053409b967d2beec8 concluded success.
```

On this **green** e2e run: `Redact URL query strings` **skipped**, `Upload
Playwright artifacts` **skipped**, artifact count **0** — correct, and proof the
new gate does not fire spuriously.

**GitGuardian**: still "2 secrets … from the scan of **6** commits" — the same two
historical findings from `951f18b`, rescanned across the now-six-commit PR. The
delta `44dac20..0ac9fb6` adds **no** credential-shaped content and **no** live
query strings. Squash-merge drops `951f18b`; the check still needs deliberate
owner dismissal.

---

## Findings

```
FINDING 9: a spec in any e2e/ directory other than specs/ or demos/ is collected by Playwright but linted by neither guard, and the whole gate stays green on a broken page
Severity:    BLOCKER
Confidence:  high
Class:       the same as FINDING 6, through a different door. Pre-existing at
             44dac20 (the globs are unchanged); this round was not asked to
             close it, and did not.

Affected:
  repo:      vizra-user
  files:     eslint.config.mjs:39  files: ["e2e/specs/**/*.ts", "e2e/demos/**/*.ts"]
             e2e/harness/no-credentials-in-specs.test.ts:99  for (const dir of ["specs", "demos"])
             playwright.config.ts  testDir: "./e2e", testMatch: "**/*.spec.ts"
  requirements: VZ-FOUND-008

Observed:
  Playwright collects `**/*.spec.ts` under `./e2e`. Both guards enumerate
  `e2e/specs` and `e2e/demos`. Any other directory under `e2e/` is therefore
  collected and unguarded.

  On the pristine tree at 0ac9fb6, one file at `e2e/other/__r1.spec.ts`:

      import { test } from "@playwright/test";
      test("R1", async ({ page }) => {
        await page.addInitScript(() => { … 404 a sub-resource, then throw … });
        await page.goto("/"); await page.waitForLoadState("networkidle");
      });

      npx eslint e2e/other/__r1.spec.ts            -> exit 0 (rule not applied)
      npm run ci                                   -> exit 0 (10 files / 227 tests)
      npx playwright test (full lane, floor armed) -> exit 0  20 passed
                                                      coverage floor: OK (10/9 10/9)
        ✓ [desktop-chromium-1440] e2e/other/__r1.spec.ts  R1
        ✓ [mobile-chromium-390]   e2e/other/__r1.spec.ts  R1
      node scripts/ci/check-coverage-floor-ran.mjs -> exit 0
      npx vitest run …/no-credentials-in-specs.test.ts -> 8 passed (never saw the file)

  Other extensions are NOT a hole: `.mts`, `.cts` and `.js` under e2e/specs/ are
  not collected by Playwright at all (testMatch is `**/*.spec.ts`); I confirmed
  each collects 0 tests.

Failure:
  The control the slice exists to provide is optional again — this time with no
  self-incriminating comment. A new directory names nothing and defeats both the
  import guard and the credential tripwire at once. Every later UI slice adds
  specs, and nothing makes the guard's directory list follow the runner's.

Perspective:
  developer, and through them visitor and member, who receive the broken page.

Recommendation:
  Make the ESLint glob cover what Playwright collects, and the credential
  sweep's roots follow it:

      files: ["e2e/**/*.ts"],
      ignores: ["e2e/harness/**"],          // the module that must import the real Playwright

  and in no-credentials-in-specs.test.ts walk `e2eRoot` itself, excluding
  `harness`, rather than a hard-coded ["specs", "demos"].

Acceptance criteria:
  - A spec at e2e/other/x.spec.ts using `@playwright/test` fails `npm run ci` by
    name, as one in e2e/specs/ does.
  - The credential sweep's file list includes it.
  - e2e/harness/**  still lints clean (it imports the real Playwright by design).
  - The unmodified tree still passes npm run ci with 227 tests and no new skips,
    and npm run e2e:demos still reports 51/51.

Tests:
  browser-errors.test.ts already walks e2eRoot for **/*.{spec,demo}.ts and
  asserts ESLint covered every file it found — it found e2e/other/__r1.spec.ts
  and linted it, but the rule was not configured for that path, so it reported
  no violation. Add one assertion beside it: for every file the walk finds, the
  resolved config (calculateConfigForFile) must have
  `rules["vizra/no-unguarded-playwright-import"]` at severity 2 and
  `linterOptions.noInlineConfig === true`. That closes the class rather than the
  directory, and the sweep that finds the files already exists.
  Then add a RED half to demonstrate.sh D8 for a spec outside e2e/specs/.

Cross-repo implications:
  core: none | user: as above | search: none
  meta: VZ-FOUND-008 must not reach VERIFIED until this is closed.

Challenge:
  "A new top-level directory under e2e/ is far more visible in a diff than a
  comment, and CODEOWNERS covers it." Both true — and `* @yegamble` means every
  path in this repository is owner-reviewed, so that was never the
  distinguishing factor for FINDING 6 either. The distinguishing factor is
  whether an automated gate can be made to report green on a broken page without
  touching a file whose job is to be a gate. Here it can, and the fix is one
  glob. The counter-argument I find hardest to dismiss is priority, not
  correctness: this is the third round, everything asked for was delivered, and
  a chair could reasonably take FINDING 9 as a follow-up slice with the ledger
  entry held at IMPLEMENTED rather than VERIFIED. I am recording it as BLOCKER
  because the ledger entry's whole claim is that this harness cannot go green on
  a broken page, and today it still can.
```

```
FINDING 10: the workflow parser checks only the FIRST upload-artifact step; a second, ungated one passes
Severity:    REQUIRED  (not blocking — it only matters when the redactor fails)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-e2e-lane.mjs:229  steps.find(step => usesOf(step).startsWith("actions/upload-artifact@"))
  requirements: VZ-FOUND-008

Observed:
  The parser locates the upload step with `.find(...)` and asserts the gate on
  that one step. I appended a SECOND upload-artifact step at the end of the job,
  on a bare `if: failure()`, publishing the same two directories:

      node scripts/ci/check-e2e-lane.mjs <mutant>  ->  exit 0  "OK: …"

  When the redactor succeeds this is harmless (the bytes are already redacted).
  When the redactor FAILS, the gated upload is skipped and the ungated one
  publishes the unredacted tree — which is precisely the fail-open FINDING 7
  closed for the first step.

  Out of scope, and I am not raising it as a finding: an arbitrary `run:` step
  can exfiltrate by other means (`gh release upload`, `curl`). I confirmed such
  a step passes the parser. No workflow linter can close that, and the
  protection there is review, not parsing.

Failure:
  The FINDING 7 fix is per-step where it needed to be per-job.

Perspective:
  member, photographer, operator

Recommendation:
  Change `.find` to `.filter` and require every upload-artifact step to carry
  the gate and the `if-no-files-found: error`; report by index when one does not.

Acceptance criteria:
  - A workflow with two upload-artifact steps, one ungated, fails
    check-e2e-lane.sh by name.
  - The committed workflow (one upload step) passes.
  - bash scripts/ci/require-checks_test.sh still reports 0 failed.

Tests:
  scripts/e2e/demonstrate.sh D7 — a second-upload mutation, asserted red,
  alongside the four D7 halves already there.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  "Adding a whole second upload step to smuggle artifacts past the redactor is
  not a realistic mistake." Agreed — which is why this is REQUIRED and not
  BLOCKER. It is worth one character (`find` → `filter`) because the parser's
  value is that it answers for the whole job, and a reader will assume it does.
```

## Residuals: accepted-by-design vs real holes

**Accepted by design** (the mechanism is owner review of a file whose job is to
be the gate; I verified each is at least not *silently* removable):

- `eslint.config.mjs`, `eslint-rules/no-unguarded-playwright-import.mjs` —
  `/eslint-rules/` is a CODEOWNERS path, and neutering the rule (`PACKAGES = []`)
  **fails `npm run test`**, so it is not silent.
- `e2e/harness/test.ts` — `/e2e/harness/` is a CODEOWNERS path. Neutering the
  guard while leaving the identifiers present **is** silent in CI (`npm run test`
  exit 0, `check-e2e-lane.sh` exit 0), because the lane guard's harness check is
  string-presence only and `npm run e2e:demos` is not a CI lane. Accepted, but
  worth knowing: the demonstrations, not CI, are what would catch it.
- `e2e/harness/required-projects.json`, `playwright.config.ts` — CODEOWNERS
  paths; both are additionally re-checked out of process.
- Arbitrary `run:` steps in the workflow (`gh`/`curl` exfiltration) — outside
  what any parser can close.

**Real holes** (no gate notices; nothing about the change announces itself):

- **FINDING 9** — a spec outside `e2e/specs/` and `e2e/demos/`. Blocking.
- **FINDING 10** — a second ungated upload step. Required, not blocking.
- The credential tripwire's evasions (`pressSequentially`, `page.evaluate`, env
  vars, a helper in `e2e/harness/`). Not a finding: it is a tripwire by
  construction and says so; the real control is the queued artifact-privacy
  slice.

## Status of all findings

| # | Finding | Status |
|---|---|---|
| 1 | spec bypasses the guard (two import spellings) | CLOSED at 44dac20 |
| 2 | lane guard does not assert the lane runs | **CLOSED** — 3/3 canaries red |
| 3 | floor is a report, not a floor | **CLOSED** — 3/3 canaries red |
| 4 | traces carry raw query strings | **CLOSED** — verified again, 3 → 0 |
| 5 | artifact upload path never executed | **CLOSED** — 3/3 canaries red |
| 6 | `eslint-disable` opts a spec out | **CLOSED** — 12/12 spellings caught, exploit now exit 1, setting and behaviour pinned |
| 7 | upload fail-open on redactor failure | **CLOSED** — 8/11 mutations red, proved in CI run 35538966116 (upload skipped, 0 artifacts) |
| 8 | AGENTS.md does not state what is uncovered | **CLOSED** — table matches my measurements; tripwire added and honestly enumerated |
| 9 | spec outside e2e/specs is unguarded | **OPEN — blocking** |
| 10 | parser checks only the first upload step | **OPEN — required, not blocking** |

## Verdict at 0ac9fb6

**FAIL**, on FINDING 9 alone.

Everything this round was asked to do, it did, and did well. My exact exploit is
dead and ESLint itself now warns that the directive has no effect. All six
inline-directive forms and all four Playwright package spellings are errors,
with `playwright-extra` correctly still allowed — the rule got stricter without
getting sloppier. `noInlineConfig` is pinned twice over, by
`calculateConfigForFile` and by behaviour, and removing it turns five tests red.
The redact/upload gate catches the `conclusion`-vs-`outcome` trap and the
`continue-on-error` trap, and it was proved in CI on a real run where the
redactor failed, the upload was skipped and zero bytes were published. The
"NOT covered" table matches my channel-by-channel measurements exactly,
including the call-parameter channel nobody had named. Nine regression canaries
are red, no test was weakened, 51 of 51 demonstration halves reproduced from my
clean clone, and every count matched.

What stops it is one glob. `eslint.config.mjs` guards `e2e/specs/**` and
`e2e/demos/**`; `playwright.config.ts` collects `**/*.spec.ts` under `e2e/`.
A spec at `e2e/other/x.spec.ts` is therefore run by the lane and linted by
nothing, and I measured `npm run ci` exit 0, the lane exit 0 with
`coverage floor: OK (10/9 10/9)`, the out-of-process floor exit 0 and the
credential sweep blind to it — on a page that 404s a sub-resource and throws on
every load. It is the same class as FINDING 6 and it predates this round; the
fix is `files: ["e2e/**/*.ts"], ignores: ["e2e/harness/**"]` plus the matching
change to the credential sweep's roots, and the assertion that closes the class
rather than the directory already has a sweep to hang on.

FINDING 10 should ride along (one character). The tripwire's evasions are not
findings — it is a tripwire and says so.

VZ-FOUND-008 must not reach VERIFIED until FINDING 9 is closed and re-verified.
If the chair judges FINDING 9 a follow-up slice rather than a blocker for this
PR, the honest disposition is to merge with the ledger entry at IMPLEMENTED and
the finding carried as its own dependency-ready item — not to mark it VERIFIED,
because the claim that entry makes is exactly the one still defeasible.

---

# Re-verification at f6f1f59

**Verdict: FAIL** — one blocking finding, new, and it defeats the *structural*
control rather than the lint layer. **Findings 9 and 10 are CLOSED, and so is
every earlier finding.** The re-plan was the right call and the design is sound;
it proves a slightly narrower proposition than it needs to.

| | |
|---|---|
| Head SHA verified | `f6f1f59a7c15a15e50c052602c3da88a425e5d35` — unmoved at start and finish |
| Ancestry | `git merge-base --is-ancestor 0ac9fb6… HEAD` → **yes**; one commit |
| Delta | 82 files, +3342 −452 (+3676/−452 including evidence) |
| Environment | macOS arm64, Node v22.14.0, @playwright/test 1.63.0, Chromium `chromium-1243` (already cached); Docker available, 13 GiB free, local image build **ran** |
| Clone | fresh, `<scratch>/verify-f6f1f59/vizra-user`, deleted on completion |

## 1. Counts — every claim matched

| Command | Exit | Result | Claim |
|---|---|---|---|
| `npm run ci` | 0 | **12 files / 269 tests / 0 skipped** | 12 / 269 / 0 — **matches** |
| `bash scripts/ci/require-checks_test.sh` | 0 | **102 cases / 109 assertions / 0 failed** | 102 / 109 — **matches** |
| `npx playwright test` | 0 | 18 passed; `coverage floor: OK (9/9 9/9)`; **`e2e harness stamp: OK (18 succeeding result(s) verified)`** | **matches** |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | floor OK + `every succeeding result carried a valid harness stamp (18 verified…)` | — |
| `node scripts/ci/harness-canary.mjs` | 0 | `failed all 3 fault-injection fixtures, each for its own named reason` | — |
| `npm run e2e:demos` | 0 | **74 halves passed, 0 blocked, 0 failed** | 74 — **matches** |

The demo script's two gitignored mutant configs are removed on exit:
`git status --porcelain` was empty after the run, and no
`playwright.config.*mutant*` or `Dockerfile.fixtures-mutant*` remained.

## 2. The three historical doors — all RED at runtime

| Door | Lint | Runtime |
|---|---|---|
| (a) `import * as pw from "@playwright/test"` in `e2e/specs/` | red | **exit 1** — "1 passed", then `__a.spec.ts:3 … succeeded WITHOUT the harness stamp` |
| (b) `/* eslint-disable … */`, run against a **mutant ESLint config with `noInlineConfig` stripped** so lint is genuinely **GREEN** | **green** | **exit 1** — `__b.spec.ts:3 … succeeded WITHOUT the harness stamp` |
| (c) `e2e/other/x.spec.ts` | red | **not collected at all** (`--list` → 0 matches; `npx playwright test e2e/other` → "Error: No tests found"), because `testDir` is now `./e2e/specs` |

Door (b) is the decisive one: with lint fully defeated, the runtime still refused
the run and named the file. That is the property the re-plan was for, and it
holds.

A raw-runner spec inside the **full** lane turns both checks red, naming both
projects — in-process (`lane exit 1`) and out-of-process (`exit 1`),
independently.

## 3. Forging the stamp — 13 attempts, 13 refused

| Attempt | Result |
|---|---|
| read `VIZRA_E2E_STAMP_KEY` at module top-level | REFUSED — undefined (test asserting so passed and verified) |
| read it in the test body / in `beforeAll` | REFUSED — undefined |
| read it from a spawned `child_process` | REFUSED — `"undefined"` |
| `claimSigner()` from a spec (body) | REFUSED — "already been claimed" |
| `claimSigner()` at spec module top-level | REFUSED — "already been claimed" |
| `reporterKeyHex()` from a spec | REFUSED — "not readable from a Playwright worker process" |
| ESM cache-bust re-import `../harness/stamp.ts?vizra=bust` then `claimSigner()` | REFUSED — "already been claimed" |
| `createRequire` + `delete require.cache` + re-require | REFUSED — spec fails to load (`require is not defined`) |
| forge with a **stale** `.vizra-e2e/stamp-key.json` from a previous run | REFUSED — "does not verify against this run's key" |
| **replay** a sibling test's valid stamp onto a raw test | REFUSED — "does not verify against this run's key" (identity-bound) |
| fabricated 64-hex annotation | REFUSED — "does not verify" |
| harness stamp **plus a duplicate** | REFUSED — "carries 2 harness stamps; exactly one is written" |
| `test.fail()` (expected-failure status) on a raw test | REFUSED — counted as success, flagged "WITHOUT the harness stamp" |

`test.skip` / `test.fixme` on a raw test leave no succeeding result and count
zero toward the floor — they hide nothing because they prove nothing.

**The stale-key chain, which is the one I expected to work, fails for a subtle
and correct reason.** With the in-process reporter deleted from the config *and*
a stale key file deliberately left in the workspace, the out-of-process check
reads the stale key — and then **every honest test's stamp fails to verify**,
because those were signed with the new run's key. The run goes red naming the
real specs. A forger who leaves a stale key to sign with must simultaneously
make every genuine test unverifiable. Measured: `out-of-process exit=1`,
"health.spec.ts:16 … carries a harness stamp that does not verify against this
run's key".

**Is the builder's statement of what forging takes honest and complete?**
`e2e/harness/stamp.ts` lists three routes (recover the key; import the sealed
module and call the signer; edit `e2e/harness/**`, `playwright.config.ts` or
`eslint-rules/**`). Routes (a) and (b) I could not breach in eight attempts
each way. Route (c) is correctly named as the residual. It is honest and, for
the threats it contemplates, complete — but it contemplates only *reaching the
signer*. It does not contemplate **keeping the signer and removing the guard**,
which is FINDING 11 below.

## 4. Out-of-process check

- **In-process stamp reporter deleted from the config** → the lane exits 0 (as
  expected, that check is gone) and the out-of-process check exits **1** by
  name: the key file is never written, "its absence means that reporter is no
  longer in playwright.config.ts, so nothing proved the tests went through the
  harness. A lane whose proof is missing did not prove anything."
- **Spec tampering with the report** (`afterAll` writing `{"suites":[]}` to
  `playwright-report/results.json`) → **does not stick**: Playwright's json
  reporter writes after all tests, and the file held 20 tests afterwards.
- **Stale report** → covered by the same fail-closed read as at 44dac20.

## 5. Canary

| Mutation of `e2e/harness/browser-errors.ts` | Canary |
|---|---|
| console listener neutered | **exit 1** |
| pageerror listener neutered | **exit 1** |
| response (HTTP ≥ 400) listener neutered | **exit 1** |
| **`unallowedRecords` body emptied, all identifiers left in place** (the silent case from 0ac9fb6) | **exit 1** |

The silent case is closed — `check-e2e-lane.sh` is still string-presence only on
the harness and stays green on that mutation, but the canary catches it, which
is what the canary is for. A fixture edited to stop being broken is also caught
(canary exit 1). The parser asserts the canary step exists, exactly once, is
unconditional and does not `continue-on-error`.

**One weakness.** The canary does **not** reliably fail when a fixture fails for
the *wrong* reason. Replacing `console.error(token)` in
`e2e/demos/console-error.demo.ts` with a 404 sub-resource leaves the canary
**green**, because Chromium reports the failed load on the console and the
harness formats it as `console.error: Failed to load resource…`, which satisfies
that fixture's expected diagnostic. So the claim in `harness-canary.mjs:160` and
`AGENTS.md:377` that each fixture fails "for its own named reason" is slightly
overstated. It is not a path to a green lane on a broken page — all four
neutering mutations are still red — so it is recorded as a residual, not a
finding.

## 6. FINDING 10 — **CLOSED**

| Mutation | Result |
|---|---|
| second **ungated** `upload-artifact` step | **red by name** — "the artifact upload at step 16 (`actions/upload-artifact@…`)" |
| second **gated** upload (legitimate) | correctly green |
| `actions/upload-artifact` swapped for another action | red — "no step uploads artifacts" |
| upload via a **composite action** (`uses: ./.github/actions/…`) | **not seen** |
| upload via `curl` in a `run:` step | **not seen** |

**What the parser cannot see, plainly:** any `run:` step and any non-`uses:
actions/upload-artifact` publisher. A composite action or a `curl`/`gh` line can
move bytes anywhere, and no workflow parser closes that. AGENTS.md's residuals
section says exactly this ("An arbitrary `run:` step can still exfiltrate … the
protection for the rest is review"), which is the honest framing.

## 7. Regression sweep — Findings 2, 3, 5, 6, 7 all stay **CLOSED**

Two canaries each, all exit 1:

```
F2  delete the lane step 1   |  npm run e2e || true 1
F3  --grep one test      1   |  delete one test      1
F5  if-no-files-found:warn 1 |  redactor removed     1
F6  namespace import     1   |  eslint-disable       1
F7  upload ungated       1   |  redact continue-on-error 1
```

**Privacy still holds**: a query-string sentinel went 3 members → **0** after
`redact-artifacts.sh`, path still readable.

**No test or demonstration weakened or deleted.** Numstat over every test, rule
and spec file: `browser-errors.test.ts` +118/−0, `collection.test.ts` +71/−0
(new), `stamp.test.ts` +155/−0 (new), `require-checks_test.sh` +100/−0,
`no-unguarded-playwright-import.test.mjs` +77/−0,
`no-credentials-in-specs.test.ts` +24/−2, the rule +51/−3. **All five removed
lines are broadenings**, ruled individually:

| Removed | Replaced by |
|---|---|
| `for (const dir of ["specs","demos"]) walk(...)` | `walk(e2eRoot)` skipping only `harness` — **wider** |
| `/\.(spec\|demo)\.ts$/.test(entry)` | `/\.ts$/.test(entry)` — **wider** |
| `properties: { harnessEntry: … }` (one line) | the same property in a multi-line schema that gained another — **wider** |
| two × `if (value !== undefined && referencesPlaywright(value)) reportPackage(...)` | the same guard opened into a block with more logic — **equal or wider** |

**AGENTS.md frames it correctly**: "#### The control is the RUNTIME STAMP. Lint
is the early warning.", a "What forging a stamp would take, stated honestly"
list, and a "Residuals — what is still only as strong as review" section that
names CODEOWNERS being unenforced, arbitrary `run:` exfiltration, the
sealed-module ban being lint, the credential sweep being a tripwire (citing the
four evasions I measured last round, as measured), and the redactor's scope.
That residuals list is accurate against everything I could measure — except that
it does not yet contain FINDING 11.

## 8. CI on f6f1f59

```
ci-required success 22:35:42   contract success   docker-build success
e2e         success 22:35:24   frontend success   guard        success
deps-scan   success            image-scan success
GitGuardian Security Checks    FAILURE

  - frontend / - contract / - ?guard / - ?docker-build / - e2e
waiting: … e2e (in_progress)   ×3
OK: every required check on f6f1f59a7c15a15e50c052602c3da88a425e5d35 concluded success.
```

The `e2e` job log carries all three lines:

```
18 passed (9.6s)
e2e coverage floor: OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9).
e2e harness stamp: OK (18 succeeding result(s) verified).
OK: the browser lane satisfied its coverage floor from the report (9/9 9/9).
OK: every succeeding result carried a valid harness stamp (18 verified, from .vizra-e2e/stamp-key.json).
OK: the harness canary failed all 3 fault-injection fixtures, each for its own named reason…
```

**Key hygiene — verified, not assumed.** The per-run key is 64 hex chars. Locally
it appears **0** times in the lane's stdout/stderr, **0** times under
`playwright-report/`, **0** times under `test-results/`; `.vizra-e2e` is
gitignored (`.gitignore:67`), is **not** in the workflow's upload paths, and has
**0** tracked files. In CI, 38 64-hex strings appear in the `e2e` log — all of
them Docker layer/image digests and npm cache keys, in the image-build and
setup-node steps; **0** in the lane, floor or canary steps, and `0` occurrences
of `VIZRA_E2E_STAMP_KEY`. Zero artifacts on this green run.

**GitGuardian**: 2 secrets across 7 commits — the same historical pair from
`951f18b`. The delta `0ac9fb6..f6f1f59` adds no credential-shaped content and no
live query strings.

---

## Findings

```
FINDING 11: a spec can keep the harness stamp and still remove the guard, by overriding the `page` fixture — the whole gate stays green on a page that 404s and throws
Severity:    BLOCKER
Confidence:  high
Class:       the same family as 6 and 9, but this one defeats the RUNTIME
             control, not the lint layer. New; not a regression from this round.

Affected:
  repo:      vizra-user
  files:     e2e/harness/test.ts:88-108   (`vizraHarnessStamp`, auto, stamps)
             e2e/harness/test.ts:110-147  (`page` override, where the guard lives)
             e2e/harness/stamp.ts:47-65   ("WHAT FORGING THE STAMP WOULD TAKE")
             eslint-rules/no-unguarded-playwright-import.mjs (no rule about `.extend`)
  requirements: VZ-FOUND-008

Observed:
  The guard and the stamp live in DIFFERENT fixtures. The stamp is written by an
  `auto: true` fixture that depends on nothing; the console / pageerror /
  requestfailed / HTTP>=400 guard is in the `page` fixture. Playwright's
  `test.extend` can replace one without the other, and replacing `page` is a
  documented, first-class feature.

  A spec that imports the harness `test` — so the stamp fixture still runs and
  the stamp verifies — and overrides `page`:

      import { test as base } from "../harness/test";
      const test = base.extend({
        page: async ({ browser }, provide) => {
          const ctx = await browser.newContext();
          await provide(await ctx.newPage());
        },
      });
      test("stamped, guard never ran", async ({ page }) => {
        await page.addInitScript(() => {
          globalThis.addEventListener("DOMContentLoaded", () => {
            const i = new Image(); i.src = "/VERIFIER_F6_MISSING.png";
            document.body.appendChild(i);
            setTimeout(() => { throw new Error("VERIFIER_F6_UNCAUGHT"); }, 0);
          });
        });
        await page.goto("/"); await page.waitForLoadState("networkidle");
      });

  Measured on the pristine tree, with the production server rebuilt and
  restarted so nothing was stale:

      npm run ci                                    -> exit 0   (LINT GREEN)
      npx playwright test  (full lane, floor armed) -> exit 0   20 passed
          ✓ [desktop-chromium-1440] __ov.spec.ts  stamped, guard never ran
          ✓ [mobile-chromium-390]   __ov.spec.ts  stamped, guard never ran
          e2e coverage floor: OK (desktop-chromium-1440=10/9 mobile-chromium-390=10/9)
          e2e harness stamp: OK (20 succeeding result(s) verified)
      node scripts/ci/check-coverage-floor-ran.mjs  -> exit 0
          OK: every succeeding result carried a valid harness stamp (20 verified)
      node scripts/ci/harness-canary.mjs            -> exit 0
      bash scripts/ci/check-e2e-lane.sh             -> exit 0
      npx vitest run e2e/harness/                   -> exit 0

  The page really is broken: the identical body through the plain harness `test`
  produces `[pageerror] VERIFIER_F6_UNCAUGHT`,
  `[response] http 404: GET …/VERIFIER_F6_MISSING.png` and the matching
  `[console]` record, and fails.

  An earlier draft of this attack was caught by ESLint — but only by accident:
  `react-hooks/rules-of-hooks` fires on a fixture whose second parameter is
  named `use`. Renaming that parameter to `provide` makes it lint-clean, as
  above. Nothing in the repository mentions `.extend` or fixture override:
  I grepped the rule, `collection.test.ts`, `browser-errors.test.ts`,
  `scripts/ci/*.mjs` and AGENTS.md.

  Overriding the stamp fixture INSTEAD is refused (the guard still runs and
  fails the broken page); overriding BOTH is refused ("WITHOUT the harness
  stamp"). Exactly one combination forges: keep the stamp, replace `page`.

Failure:
  The stamp proves "this test came from the harness `test` object". The property
  the ledger entry claims is "this test ran the guard". Fixture override
  separates the two, and the gap is green in `npm run ci`, in the lane, in both
  floor checks, in the canary and in the workflow parser. Every later UI slice
  is judged through this harness, and one `.extend` in a spec — a normal-looking
  Playwright idiom, not an obvious opt-out — silently exempts it.

Perspective:
  developer, and through them visitor and member, who receive the broken page.

Recommendation:
  Make the fixture that cannot be removed be the fixture that guards. Move the
  listener attachment and the teardown assertion OUT of the `page` override and
  INTO the auto `vizraHarnessStamp` fixture, declaring `page` as its dependency:

      vizraHarnessStamp: [
        async ({ page }, runTest, testInfo) => {
          const records = collectBrowserErrors(page);
          testInfo.annotations.push({ type: STAMP_ANNOTATION, description: signStamp({...}) });
          await runTest();
          await flushBrowserEvents(page);
          ...assert unallowedRecords...
        },
        { auto: true },
      ],

  Then overriding `page` hands the OVERRIDDEN page to the guard rather than
  removing it, and removing the guard means removing the stamp — which both
  checks already refuse. That restores the invariant "stamped ⟹ guarded" with no
  new machinery.

  Add the lint half as the early warning it is meant to be: refuse
  `base.extend({ page: … })` and `.extend({ vizraHarnessStamp: … })` in
  `e2e/specs/**` and `e2e/demos/**`. No spec uses `.extend(` today, so the ban
  costs nothing.

Acceptance criteria:
  - The spec above fails the lane by name, and fails `check-coverage-floor-ran.mjs`.
  - A spec overriding `page` fails `npm run ci` by name (lint early warning).
  - `test.use({ browserErrorPolicy: … })` still works, and the three demos and
    all 18 lane tests still pass, with `harness stamp: OK (18 …)` unchanged.
  - `npm run e2e:demos` still reports 74/74.

Tests:
  A new D11 half in scripts/e2e/demonstrate.sh: the override spec above, asserted
  RED with "WITHOUT the harness stamp" (or the new guard message), plus a GREEN
  half with the override removed. The harness to run it exists — this is the
  same shape as the D11 stamp demonstrations already there.
  Add RuleTester cases for the two banned overrides in
  eslint-rules/no-unguarded-playwright-import.test.mjs.

Cross-repo implications:
  core: none | user: as above | search: none
  meta: VZ-FOUND-008 must not reach VERIFIED until this is closed — every later
  UI slice's evidence runs through this harness.

Challenge:
  "Overriding `page` is a deliberate, visible act in a diff, and `e2e/specs/` is
  a CODEOWNERS path — this is the accepted residual (c) in stamp.ts, edits to
  gate files." It is not: `e2e/specs/` is where every slice legitimately adds
  code, and the spec above touches no gate file, no harness file, no config and
  no workflow. It is four lines of ordinary Playwright in a normal spec, it
  passes lint, and it is the idiom the Playwright documentation teaches for
  customising a fixture. The residual the builder accepted is "someone edits a
  file whose job is to be a gate"; this is not that. The honest counter is
  priority — this is the fourth round — but the fix is a fixture-dependency
  change of about ten lines, and until it lands the ledger entry's central claim
  is still false.
```

## Residuals: accepted-by-design vs real holes

**Accepted by design** — edits to files whose job is to be a gate, all under
`.github/CODEOWNERS` (which, as AGENTS.md correctly says, enforces nothing until
an owner applies a ruleset):

- `e2e/harness/**`, `playwright.config.ts`, `eslint-rules/**`, `.github/**`.
  Each is at least not silent: neutering the rule fails `npm run test`;
  neutering the guard's bodies fails the canary; deleting the stamp reporter
  fails the out-of-process check; every workflow mutation I tried but two is red
  by name.
- Arbitrary `run:` steps and composite actions can exfiltrate; no parser closes
  that, and AGENTS.md says so.
- The credential sweep is a tripwire with four measured evasions, declared.

**Real holes:**

- **FINDING 11** — fixture override keeps the stamp and removes the guard.
  Blocking. Touches no gate file.
- The canary's "each for its own named reason" is overstated for the console
  fixture (a 404 satisfies its diagnostic). Not blocking; worth one line of
  wording or a sharper expected string.

## Status of all findings

| # | Finding | Status |
|---|---|---|
| 1–8 | earlier rounds | CLOSED |
| 9 | spec outside `e2e/specs` unguarded | **CLOSED** — not collected (`testDir: ./e2e/specs`), lint glob widened to `e2e/**` minus harness, and the runtime stamp catches it regardless |
| 10 | parser checks only the first upload step | **CLOSED** — second ungated upload red by name; second gated upload correctly green |
| 11 | fixture override keeps the stamp, drops the guard | **OPEN — blocking** |

## Verdict at f6f1f59

**FAIL**, on FINDING 11 alone.

The re-plan was correct and the execution is the strongest work in this PR. The
guarantee genuinely moved to the runtime: door (b) — my `eslint-disable` exploit
run against a mutant ESLint config with `noInlineConfig` stripped, so lint was
truly green — was still refused by the stamp reporter, by name. Thirteen forge
attempts failed, including the stale-key chain, which fails for the right reason
rather than by luck. The key is unreadable from a worker, from a child process,
from disk during a run, and never appears in a log, a report, an artifact or CI
output. Deleting the in-process reporter fails closed out of process. The canary
closes the silent-guard case that was silent at 0ac9fb6. Findings 9 and 10 are
closed, all nine earlier findings stay closed under two canaries each, no test
was weakened, and all five removed lines are broadenings. Every count matched,
74 of 74 demonstration halves reproduced from my clean clone, and CI on this SHA
shows the floor line, the stamp line and the canary line.

It fails because the stamp proves the wrong proposition by a hair. It certifies
that a test came from the harness `test` object; the claim the ledger makes is
that the test ran the guard. Playwright's `test.extend` separates those two, and
a four-line, lint-clean, entirely ordinary-looking spec that overrides the `page`
fixture keeps its valid stamp while the console/page-error/404 guard never runs —
`npm run ci` exit 0, the lane exit 0 with "20 passed, coverage floor: OK,
harness stamp: OK (20 verified)", the out-of-process check exit 0, the canary
exit 0, the workflow parser exit 0 — on a page that 404s a sub-resource and
throws on every load.

The fix is small and in the spirit of the design already chosen: make the
un-removable auto fixture the one that guards, by giving it `page` as a
dependency, so that overriding `page` feeds the guard instead of deleting it and
"stamped" once again implies "guarded". Add the `.extend` ban as the lint early
warning; no spec uses `.extend(` today.

VZ-FOUND-008 must not reach VERIFIED until FINDING 11 is closed and
re-verified. If the chair judges it a follow-up, the honest disposition is merge
at IMPLEMENTED with FINDING 11 as its own dependency-ready item — not VERIFIED,
because "a test cannot pass without the guard" is precisely the sentence that is
still false.

---

# Re-verification at c669e40

**Verdict: PASS.** **FINDING 11 is CLOSED.** No blocking finding. Three REQUIRED
follow-ups, all narrow, and two sentences in AGENTS.md that are currently false
and should be corrected before the next UI slice.

| | |
|---|---|
| Head SHA verified | `c669e4001738df3f7c7ec3fcf1feaf3c9e41ca4e` — unmoved at start and finish |
| Ancestry | `git merge-base --is-ancestor f6f1f59… HEAD` → **yes**; one commit |
| Delta | 65 files, +2992 −747 |
| Environment | macOS arm64, Node v22.14.0, @playwright/test 1.63.0, Chromium `chromium-1243` (already cached); Docker available, 11 GiB free, local image build **ran** |
| Clone | fresh, `<scratch>/verify-c669e40/vizra-user`, deleted on completion |

## 1. Counts — every claim matched

| Command | Exit | Result | Claim |
|---|---|---|---|
| `npm run ci` | 0 | **12 files / 289 tests / 0 skipped** | 12 / 289 / 0 — **matches** |
| `bash scripts/ci/require-checks_test.sh` | 0 | **102 cases / 109 assertions / 0 failed** | 102 / 109 — **matches** |
| `npx playwright test` | 0 | 18 passed; floor `9/9 9/9`; `harness stamp: OK (18 …)` | **matches** |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | floor + `every succeeding result carried a valid harness stamp (18 verified)` | — |
| `node scripts/ci/harness-canary.mjs` | 0 | `failed all 3 … with the exact set of record kinds it demonstrates and no others` | — |
| `npm run e2e:demos` | 0 | **88 halves passed, 0 blocked, 0 failed** | 88 — **matches** |

`git status --porcelain` was empty after the demo run — the two gitignored
mutant configs are removed on exit.

**No test or demonstration was weakened or deleted.** Numstat over every test,
rule and spec file shows **zero removed lines**: `browser-errors.test.ts`
+240/−0, `no-unguarded-playwright-import.mjs` +79/−0, its test +72/−0,
`require-checks_test.sh` unchanged.

## 2. FINDING 11 — **CLOSED**, and the class with it

My exploit verbatim, and eight more shapes, each on the broken-page body (404
sub-resource + uncaught throw), each with **lint green**:

| Shape | Result |
|---|---|
| **my exploit**: `test.extend` overriding `page` with a fresh context | **RED** |
| a second page in the default context | **RED** |
| `browser.newContext()` + `newPage()` in the body | **RED** |
| `browser.newPage()` | **RED** |
| an overridden `context` fixture | **RED** |
| an overridden `page` that **navigates inside the fixture** before `provide` (the builder's d13e2 case) | **RED** |
| a popup via `window.open` | **RED** |
| an iframe inside a popup | **RED** |
| a page created in `beforeAll` and reused | **RED** |
| an overridden `browser` fixture via the built-in `playwright` fixture | **RED** |
| a context created and **closed before the test ends** | **RED** — records survive the close |

Overriding the merged fixture fails closed at **both** layers, in all three
spellings I tried — plain, computed key, spread variable: lint RED **and**
runtime RED (`succeeded WITHOUT the harness stamp`). "Stamped implies guarded"
now holds.

**No false positives.** An honest `page` override (locale + viewport) on a
healthy page passes; the per-test allow-list still applies on an overridden
page; and the real 18 tests ran **five consecutive times**, all exit 0, 18
passed, 18 stamps, no flake.

## 3. The wrap, and what escapes it

`guardBrowser` wraps `newContext`/`newPage` as **own properties** on the browser
instance and restores the previous descriptor state in `dispose()`. I verified
the prototype is untouched and the instance wrapper is a distinct function
during a test. That restore design is deliberate and correct — and it is also
the escape:

| Attempt | Result |
|---|---|
| `Object.getPrototypeOf(browser).newPage.call(browser)` | **RED** — the prototype's `newPage` calls `this.newContext`, which is the wrapper |
| `Object.getPrototypeOf(browser).newContext.call(browser)` | **GREEN — unguarded** |
| `browser.browserType().launch()` | **GREEN — unguarded** |
| `playwright.chromium.launchPersistentContext(dir)` | **GREEN — unguarded** |

All three need **no Playwright import at all**, so the ESLint rule cannot see
them. Measured against the **complete** gate, each with only that one spec added:

```
                              lint    lane   out-of-proc
prototype newContext          green   0      0     20 passed, floor OK 10/9 10/9, stamp OK (20)
browser.browserType().launch  green   0      0     20 passed, floor OK 10/9 10/9, stamp OK (20)
launchPersistentContext       green   0      0     20 passed, floor OK 10/9 10/9, stamp OK (20)
```

— on a page that 404s a sub-resource and throws on every load (the identical
body on a guarded page yields `[pageerror]`, `[response] http 404`, `[console]`).

**Would patching the prototype or listening for context creation close it?**
Prototype patching would close the first, but the prototype is shared by every
`Browser` in the process and the worker-scoped restore would get harder, not
easier. The cheaper and more complete answer is to **detect rather than
prevent**: at teardown, assert that `browser.contexts()` contains no context the
guard never saw. That closes the prototype route and any future creation path on
a browser the harness holds, and it needs no monkey-patching at all. The two
self-launched-browser routes are outside any such check by construction and
belong to lint: add `.browserType(`, `.launch(` and `.launchPersistentContext(`
to the rule for `e2e/specs/**`.

**Two other gaps, both minor and both stated honestly here rather than found
later:**

- **Late errors.** A fault scheduled `0 ms` after the body returns is caught;
  at `50 ms` and `150 ms` it is missed. The flush window is finite and that is
  inherent — worth a sentence in AGENTS.md, not a redesign.
- **The `request` fixture.** An `APIRequestContext` 404 is not a browser signal
  and is not guarded. I judge that legitimately out of scope — the test asserted
  the 404 itself — but AGENTS.md does not say so, and "any HTTP >= 400 response
  fails the test" reads as if it were covered.

## 4. Canary

| Mutation | Canary |
|---|---|
| console listener neutered | **exit 1** |
| weberror listener neutered | **exit 1** |
| response (HTTP ≥ 400) listener neutered | **exit 1** |
| `unallowedRecords` body emptied, identifiers left in place (the silent case) | **exit 1** |
| **fixture's fault type swapped (`console.error` → a 404)** | **exit 1** — the f6f1f59 weakness is closed by the exact-kind-set assertion |
| **`requestfailed` listener neutered** | **exit 0 — not caught** |

The three fixtures demonstrate `console`, `response`+404 and `pageerror`. None
produces a `requestfailed` record, so one of the four guarded signal kinds has no
canary coverage: the kind that catches aborted requests, connection refused and
DNS failures could be removed from the guard and no lane would notice.

## 5. Privacy — a real gap, reproducible

A query-string sentinel went **3 members → 1** after `redact-artifacts.sh`
(at f6f1f59 the same probe gave 3 → 0; the redactor is unchanged in this delta,
so I treat my earlier `0` as an unreliable measurement rather than asserting a
regression).

The survivor is in `test.trace`, in a step **subtitle**, where Playwright records
the URL **without its scheme**:

```
"subtitle":"127.0.0.1:3219/m.jpg?X-Amz-Sig=PUREQc669e40zz&e=60"
```

Reduced to a three-line unit test against the redactor itself:

```
"url":"http://host/m.jpg?X-Amz-Sig=SENTINELVALUE&e=60"   ->  ?<redacted>      OK
"path":"/m.jpg?X-Amz-Sig=SENTINELVALUE&e=60"             ->  ?<redacted>      OK
"subtitle":"host:3219/m.jpg?X-Amz-Sig=SENTINELVALUE&e=60" ->  UNCHANGED       LEAK
```

The absolute program needs a scheme; the relative program needs the match to
start at `/`. A `host:port/path?query` string satisfies neither.

**Why D9 does not catch it:** its fixture injects the signed URL as a
sub-resource (`new Image(); img.src = url`) and navigates to `/`. A sub-resource
never becomes a Playwright step subtitle. Any `page.goto(signedUrl)` or
`page.request.get(signedUrl)` does.

Nothing leaks today — nothing authenticates and no signed URL exists — but
AGENTS.md's "**No URL query string leaves this repository, in any artifact**" is
false as written.

**Key hygiene is clean**: the per-run key appears 0 times in the lane output, 0
times under `playwright-report/`, 0 times under `test-results/`; `.vizra-e2e` is
gitignored, absent from the upload paths, and has no tracked files.

## 6. Regression sweep — everything stays CLOSED

Fourteen canary mutations, all exit 1:

```
F2  delete lane step 1 | npm run e2e || true 1
F3  --grep one test  1 | --project one        1
F5  if-no-files:warn 1 | redactor removed     1
F6  namespace import 1 | eslint-disable       1
F7  upload ungated   1 | redact cont-on-error 1
F10 2nd ungated upload 1 | canary step deleted 1
F9  raw spec in the full lane 1 | out-of-process 1
```

The five strongest forge attempts, re-run: `claimSigner` → "already been
claimed"; `reporterKeyHex` → "not readable from a Playwright worker";
fabricated annotation → "does not verify against this run"; duplicate stamp →
"carries 2 harness stamps"; raw runner → "WITHOUT the harness stamp".

## 7. CI on c669e40

All nine checks green except GitGuardian; `ci-required` enumerated `e2e`, waited
three polls and concluded `OK: every required check on c669e40… concluded
success.` The `e2e` job log carries all three lines: `coverage floor: OK
(9/9 9/9)`, `harness stamp: OK (18 succeeding result(s) verified)`, and
`the harness canary failed all 3 fault-injection fixtures, each with the exact
set of record kinds it demonstrates`. GitGuardian is the same two historical
findings from `951f18b`, now across 8 commits; the delta adds nothing
credential-shaped.

---

## Findings

```
FINDING 12: three import-free routes reach an unguarded page, and the documented residual names a mitigation that does not cover any of them
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/browser-errors.ts (guardBrowser: own-property wrapping)
             eslint-rules/no-unguarded-playwright-import.mjs (package references only)
             AGENTS.md:521-533 ("A spec that launches its OWN browser…")
  requirements: VZ-FOUND-008

Observed:
  Each of the following, in e2e/specs/, importing ONLY the harness `test`,
  passes lint and passes the complete gate on a page that 404s a sub-resource
  and throws on every load (20 passed, floor OK 10/9 10/9, stamp OK (20),
  out-of-process exit 0):

    const ctx = await Object.getPrototypeOf(browser).newContext.call(browser);
    const own = await browser.browserType().launch();
    const ctx = await playwright.chromium.launchPersistentContext(dir);

  AGENTS.md:521 states the residual as "a browser obtained by **importing a
  Playwright package** and calling `chromium.launch()` directly", and names
  `vizra/no-unguarded-playwright-import` as "What catches that … This is the one
  shape where lint is the only automated control."

  None of the three imports a Playwright package, so the rule sees nothing —
  I confirmed `import { chromium } from "@playwright/test"` is RED while
  `browser.browserType().launch()` is green. `browserType` and
  `launchPersistentContext` appear nowhere in AGENTS.md, the harness, the rule
  or the CI scripts.

  The prototype route is not even "your own browser": it is the harness's own
  browser, escaped because the guard wraps `newContext` as an OWN property and
  leaves the prototype method reachable. (`newPage` via the prototype IS caught,
  because it calls `this.newContext` — the wrapper.)

Failure:
  The residual is documented as narrower than it is, with a mitigation that does
  not apply. A reader who trusts that paragraph will believe lint covers the
  escape hatch; it does not.

Perspective:
  developer, and through them visitor and member

Recommendation:
  1. Detect rather than prevent, for the harness's own browser: in
     `vizraHarnessGuard` teardown, assert that `browser.contexts()` contains no
     context the guard never saw, and fail the test naming it. That closes the
     prototype route and any future creation path, with no monkey-patching.
  2. Extend the lint rule for `e2e/specs/**` and `e2e/demos/**` to refuse
     `.browserType(`, `.launch(` and `.launchPersistentContext(`. These are
     method names, not package references — an AST rule reads them directly.
  3. Correct AGENTS.md:521-533: the shape is "a browser or context the harness
     was never handed", by any route including import-free ones, and lint covers
     it only once (2) lands.

Acceptance criteria:
  - Each of the three specs above fails the lane by name.
  - Each fails `npm run ci` by name.
  - The honest `page`/`context`/`browser` overrides in D13 still pass, and the
    18 lane tests still pass with `harness stamp: OK (18 …)`.
  - AGENTS.md describes the residual in terms of the object, not the import.

Tests:
  scripts/e2e/demonstrate.sh D13 — three more RED halves, one per route, in the
  same shape as the eight already there. RuleTester cases for the three method
  names.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  "All three are conspicuous, deliberate acts in an owner-reviewed path — this
  is the accepted residual, not a hole." Largely right, and it is why this is
  REQUIRED and not a blocker: none is an honest-looking idiom, unlike the `page`
  override that made FINDING 11 blocking. The part that is not right is the
  documentation: the paragraph tells a reader that lint catches this class, and
  for every spelling that needs no import it does not. A residual stated
  inaccurately is worse than one stated plainly, because it is trusted.
```

```
FINDING 13: the artifact redactor misses scheme-less URLs, which is how Playwright records step subtitles
Severity:    REQUIRED  (before M1; nothing leaks today)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/redact-artifacts.sh:78 (ABSOLUTE_PROGRAM), :92 (RELATIVE_PROGRAM)
             e2e/demos/signed-url-artifact.demo.ts (D9's fixture)
             AGENTS.md ("No URL query string leaves this repository, in any artifact")
  requirements: VZ-FOUND-008

Observed:
  A query-string sentinel driven through `page.goto()` survived redaction in
  `test.trace` inside trace.zip:

      "subtitle":"127.0.0.1:3219/m.jpg?X-Amz-Sig=PUREQc669e40zz&e=60"

  Reduced against the redactor directly:

      "url":"http://host/m.jpg?...=SENTINELVALUE&e=60"      -> ?<redacted>
      "path":"/m.jpg?...=SENTINELVALUE&e=60"                -> ?<redacted>
      "subtitle":"host:3219/m.jpg?...=SENTINELVALUE&e=60"   -> UNCHANGED

  The absolute program requires `scheme://`; the relative program requires the
  match to begin at `/`. `host:port/path?query` satisfies neither.

  D9 does not catch it because its sentinel is injected as a sub-resource
  (`img.src = url`) and the test navigates to `/`. A sub-resource never becomes
  a step subtitle; a `page.goto(signedUrl)` always does.

  Measured 3 members -> 1 after redaction. `test-results/` is uploaded as a
  14-day artifact on failure.

Failure:
  From M1, a red lane on a spec that navigates to a signed media URL publishes
  that URL's query string. AGENTS.md's "No URL query string leaves this
  repository, in any artifact" is false as written.

Perspective:
  member, photographer, operator

Recommendation:
  Add a third perl program for authority-relative URLs — an optional
  `host[:port]` before the path — or widen the relative program to accept
  `[A-Za-z0-9.-]+(?::\d+)?` before the leading `/`. Then extend D9 with a second
  fixture that reaches the sentinel through `page.goto()` rather than a
  sub-resource, so the subtitle path is covered by the demonstration that
  claims to cover it.

Acceptance criteria:
  - The three-line reduction above redacts all three forms.
  - A spec that `page.goto`s a signed-URL-shaped URL leaves 0 members carrying
    the sentinel after redaction, with host and path still readable.
  - D9 covers the navigation path as well as the sub-resource path.

Tests:
  scripts/e2e/demonstrate.sh D9 — a second RED/GREEN pair using page.goto;
  scripts/e2e/sweep-artifacts.sh already performs the search.

Cross-repo implications:
  core: the first signed-URL slice is the trigger | user: as above
  search: none | meta: the VZ-FOUND-008 privacy case already proposed at 44dac20

Challenge:
  "Nothing authenticates, so this leaks nothing." True today, and why it is not
  a blocker. But the claim in AGENTS.md is absolute and is relied on when
  deciding whether a red lane is safe to share, and the fix is one regex.
```

```
FINDING 14: the canary has no fixture for `requestfailed`, so that listener can be removed silently
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/harness-canary.mjs (CANARIES: console / response+404 / pageerror)
             e2e/harness/browser-errors.ts (onRequestFailed)
  requirements: VZ-FOUND-008

Observed:
  Neutering each guarded listener in turn and running the canary:

      console      exit 1
      weberror     exit 1
      response     exit 1
      requestfailed exit 0    <- not caught

  The three fixtures demonstrate a console error, an HTTP 404 and an uncaught
  exception. A 404 is a completed response, not a failed request, so no fixture
  produces a `requestfailed` record.

Failure:
  One of the four guarded signal kinds — aborted requests, connection refused,
  DNS failures — could be dropped from the guard with no lane going red. That is
  the exact defect class the canary exists to close, for three kinds out of four.

Perspective:
  developer

Recommendation:
  Add a fourth fixture that requests a closed port (or a route aborted with
  `route.abort()`), with expected kinds `["requestfailed"]`, so the canary's
  exact-kind-set assertion covers all four.

Acceptance criteria:
  - Neutering the `requestfailed` listener fails the canary by name.
  - The canary still passes unmodified, and `npm run e2e:demos` still reports
    its full count.

Tests:
  The canary itself; plus a D12 half asserting the new fixture fails for its own
  kind.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  "`requestfailed` is redundant with `response` — a broken request usually shows
  up on the console too." Usually, not always: a connection refused or an
  aborted request produces no response at all, and my own probes at 112291e
  showed `requestfailed` firing where `response` did not.
```

## Residuals: accepted-by-design vs real holes

**Accepted by design** — a deliberate edit to a file whose job is to be a gate,
all under `.github/CODEOWNERS` (which, as AGENTS.md says, enforces nothing until
a ruleset is applied):

- `e2e/harness/**`, `playwright.config.ts`, `eslint-rules/**`, `.github/**`.
  None is silent: neutering the rule fails `npm run test`; neutering three of
  the four guard listeners fails the canary; replacing the merged fixture costs
  the stamp and fails both floor checks; fourteen workflow mutations are red by
  name.
- Arbitrary `run:` steps and composite actions can exfiltrate — no parser closes
  that, and AGENTS.md says so.
- The credential sweep is a declared tripwire with four measured evasions.

**Real holes, reachable with lint green from a spec in `e2e/specs`:**

- **FINDING 12** — prototype `newContext`, `browser.browserType().launch()`,
  `launchPersistentContext`. Conspicuous, not honest-looking; REQUIRED, not
  blocking.
- **FINDING 13** — scheme-less URLs survive redaction into a 14-day artifact.
  Nothing to leak today.
- **FINDING 14** — `requestfailed` has no canary fixture.
- Errors firing ≥ 50 ms after the body returns are missed (inherent flush
  window). `request`-fixture 404s are out of scope — correctly, but unstated.

## Status of all findings

| # | Finding | Status |
|---|---|---|
| 1–10 | earlier rounds | CLOSED |
| 11 | fixture override keeps the stamp, drops the guard | **CLOSED** — my exploit and ten more shapes all RED; guard and stamp are one fixture attached at the browser |
| 12 | three import-free routes to an unguarded page; residual mis-stated | **OPEN — required, not blocking** |
| 13 | scheme-less URLs survive redaction | **OPEN — required, before M1** |
| 14 | no canary fixture for `requestfailed` | **OPEN — should** |

## Verdict at c669e40

**PASS.**

FINDING 11 is closed, and the chair was right to ask for the class rather than
the door. Merging the guard and the stamp into one automatic fixture attached at
**BrowserContext** level — with the dependency list measured rather than guessed,
and the reasoning for `browser`+`context` written down where the next reader will
find it — closes every ordinary route I could construct: my own exploit, an
overridden `context`, an overridden `browser`, a second page, a new context, a
popup, an iframe inside a popup, a `beforeAll` page, a context closed early, and
the pre-navigating fixture the builder found themselves. Removing the fixture
costs the stamp, in all three spellings I tried, at both layers. There are no
false positives: honest overrides pass, the allow-list still applies on an
overridden page, and the real suite ran five times clean. Every count matched,
88 of 88 demonstration halves reproduced from my clean clone, the tree was clean
afterwards, and CI on this SHA carries the floor, stamp and canary lines.

What remains is genuinely residual. Three routes still reach an unguarded page —
the browser's prototype `newContext`, and two ways to launch a browser the
harness never sees — and all three need no import, so the lint rule named as
their mitigation cannot see them. But none is an honest-looking idiom: each is a
conspicuous act with no innocent reading in a repository that has one app and one
browser. That is a different thing from the `page` override that made FINDING 11
blocking, which was the idiom Playwright's own documentation teaches. The
correct response is to state the residual accurately and add the cheap
detection — a teardown assertion that no unguarded context exists on the
harness's browser, plus three method names in the lint rule — not to hold the
slice.

FINDING 13 should land before anything authenticates; it makes an absolute
sentence in AGENTS.md false today, and it is one regex. FINDING 14 is one more
canary fixture.

PASS is not a merge and not VERIFIED — the chair records those. My recommendation
is that VZ-FOUND-008 may be recorded VERIFIED on this evidence, with findings 12,
13 and 14 carried as dependency-ready follow-ups, and with the two inaccurate
AGENTS.md paragraphs corrected in whichever PR lands first.

---

# Confirmation at 3b566c3

**Verdict: PASS. Docs-only confirmed mechanically. Merge condition CLOSED.**

`c669e40` is an ancestor. Diff is exactly 4 files — `AGENTS.md`,
`docs/evidence/VZ-FOUND-008/README.md`, `e2e/harness/browser-errors.ts`,
`scripts/ci/harness-canary.mjs`. No `.json`, `.yml` or `.sh`.

**1. Nothing executable changed.** Both code files were parsed with the
repository's own TypeScript and re-printed from the AST with
`removeComments: true` (comments are trivia, so the emitted text is executable
content only, formatting-normalised), then compared:

```
browser-errors.ts   IDENTICAL executable content   (218 lines printed, both sides)
harness-canary.mjs  IDENTICAL executable content   ( 92 lines printed, both sides)
```

Independently: every added **and** removed line in those two files is a comment
or blank. Full re-verification is not required.

**2. The corrected sentences are exactly true against what I measured.**

| Claim now made | Against my measurement |
|---|---|
| residual is "a CONTEXT OR BROWSER THE HARNESS WAS NEVER HANDED", own-property wrapping named as the mechanism | exact |
| the three import-free routes, each "unguarded", each passing the complete gate with `20 passed, floor OK (10/9 10/9), stamp OK (20 verified)`, out-of-process 0 | exact, including the numbers |
| prototype `newPage` **is** guarded, because it calls `this.newContext` | exact |
| "**Nothing catches these today**" — not the rule, stamp, floor, canary or parser; review only | exact |
| the previous paragraph ("importing a Playwright package… the rule catches it") is labelled **false** | correct |
| redaction covers "query strings and fragments on URLs that carry a scheme or start at `/`, and `Location`" — **not** scheme-less `host:port/path?query` | exact; the three-line reduction is reproduced verbatim |
| D9 "does not exercise this path, and does not claim to" — sub-resource, never a step subtitle | exact |
| the fix is queued under the existing no-authenticated-spec rule, "Not done here" | correct |
| canary covers three of four kinds; neutering `requestfailed` leaves it green | exact |
| flush window: `0 ms` caught, **50 ms and 150 ms missed**, called inherent | exact |
| `request`-fixture 4xx out of scope, and the guard header re-scoped to "HTTP >= 400 response **observed by a browser context**" | exact, and a genuine tightening |

No sentence overstates. The one absolute that remains on the page (line 379) is
the old claim quoted in order to be called false — correct. One mild
**understatement**: line 612 still says the guard covers "D13, eight shapes";
I measured **eleven** red shapes (the eight plus a page created in `beforeAll`,
an iframe inside a popup, and a context closed before the test ends). Harmless,
worth a number bump whenever that file is next touched.

**3. CI on 3b566c3**: `ci-required`, `contract`, `deps-scan`, `docker-build`,
`e2e`, `frontend`, `guard`, `image-scan` all **success**; `ci-required`
enumerated `e2e`, waited three polls, and logged `OK: every required check on
3b566c3b057a9a9a6748393000b4a3461ded2d49 concluded success.` GitGuardian remains
the two historical findings from `951f18b`.

**Acceptance bullet.** VZ-FOUND-008 — "the Playwright harness runs in CI against
the production build image on desktop and mobile projects, and a console or
network error fails the lane (demonstrated)" — **is met by my own evidence**:
reproduced at c669e40 from a clean clone (18 passed at 1440 px and 390 px
against the built image, floor 9/9 9/9, 18 stamps, 88/88 demonstration halves)
and unchanged here, since nothing executable moved.

Findings 12, 13 and 14 remain OPEN as documented, queued follow-ups — now
stated accurately in the contract rather than contradicted by it.
