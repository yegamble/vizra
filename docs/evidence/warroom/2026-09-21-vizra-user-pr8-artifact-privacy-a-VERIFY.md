# vizra-user PR #8 — "artifact privacy, PR A" — INDEPENDENT VERIFICATION

- **Repo / PR:** `yegamble/vizra-user` #8, `fix/m0-artifact-privacy-a`
- **SHA verified:** `e0960539f20d2a484e430dab70718d2e3dd49c7c` (confirmed unmoved via
  `gh api repos/yegamble/vizra-user/pulls/8` at the start and end of this run;
  base `6bf0a0e6d7302a1e3c655dd10eae1f3f406d7196`, 6 commits, 39 files, +2290 −302)
- **Verifier:** war-room independent verifier. I did not write this code and did not
  review the plan. Read-only on every repository; I edited nothing, pushed nothing,
  and the only file I wrote is this one.
- **Binding spec:** chair's rulings item 1 ("PR A") at the top of
  `docs/evidence/warroom/2026-09-21-vizra-user-artifact-privacy-PLAN-REVIEW-security.md`,
  with security-seat FINDINGS 3, 8, 9, 10, 13, 19 and the `redact.ts` half of 4.
- **Inherited debts:** PR #7 verification FINDINGS 6 and 7, and re-confirmation item 3 (C4).

## Environment

```
macOS Darwin 25.5.0 arm64      node v22.14.0      npm 10.9.2
@playwright/test 1.63.0        chromium-1243 / chromium_headless_shell-1243
clean clones at the SHA under a private mktemp -d; node_modules from `npm ci` (415 packages, exit 0)
```

Three working trees, all mine, all deleted at the end:
`…/scratchpad/vzv-vizra-user-pr8-AH5x3U/{repo,mutsbx}` (verification + mutation sandbox)
and `…/scratchpad/vzv-pr8a-demos-kj8CDP/repo` (the demonstration run, kept quiescent).
The builder's `…/scratchpad/vzap-probe-ZNSCIV` was not touched.

---

## 1. The base64 channel, end to end — the headline result

I produced my own RED Lane-A run with the **shipped** configuration and four
runtime-minted markers (random hex from `crypto.randomBytes`, nothing committed,
localhost-only fixture server, no credential of any kind): a scheme-less
signed-URL query value, a `page.fill` typed value, an assertion's received value,
a page-controlled `console.error`, and a page `<title>`.

**Positive control** (before any redaction, whole tree): all five markers found,
including inside `playwright-report/index.html::base64[0]::zip:0969a537…json`.
The probe channel is real.

Then I ran the **shipped** `bash scripts/ci/redact-artifacts.sh test-results playwright-report`
(reported `OK: redacted … 23 file(s) and 2 archive(s)`, exit 0) and scanned
**exactly what the workflow now uploads** — `test-results/`,
`playwright-report/results.json`, `playwright-browsers.txt` — with my own scanner
that decodes base64 and recurses into archives.

### What Lane A still publishes after this PR (measured, not inferred)

| Marker (channel) | Survives the upload set? | Where |
|---|---|---|
| scheme-less signed-URL query value | **NO** — redacted everywhere | — |
| `page.fill` typed value | **YES** | `trace.zip::1-trace.trace`, `trace.zip::test.trace` |
| assertion's received value | **YES** | `error-context.md`, `trace.zip::attachments/…`, `trace.zip::test.trace`, **`playwright-report/results.json`** |
| page-controlled console text | **YES** | `error-context.md`, `trace.zip::1-trace.trace`, `::attachments/…`, `::resources/….html`, `::test.trace`, `results.json` |
| page `<title>` (DOM snapshot) | **YES** | `trace.zip::1-trace.trace`, `::resources/….html` |

Every surviving row is named in AGENTS.md's "NOT covered" table (Playwright call
parameters; DOM snapshots and attachments; a non-URL token in a console message).
Two précising notes in §9.

### The dropped file, and why dropping it was the right call

Scanning `playwright-report/index.html` **after** the redactor reported success:

```
signed    YES   index.html::base64[0]::zip:0969a537533b608caea8.json
typed     YES   index.html::base64[0]::zip:0969a537533b608caea8.json
asserted  YES   index.html::base64[0]::zip:0969a537533b608caea8.json
console   YES   index.html::base64[0]::zip:0969a537533b608caea8.json
raw grep of index.html for each marker: 0 hits
```

The scheme-less signed-URL value that the redactor **successfully removed from
every other artifact** is still live inside that base64 payload, and a raw grep
cannot see it. FINDING 3 reproduces exactly. `index.html` is absent from the
upload set at this SHA, and `check-e2e-lane.mjs` refuses to re-add it (case A6
below). `playwright-report/data/*.zip` are likewise not uploaded — only
`playwright-report/results.json` is.

### The sweep, old vs new, on the identical tree

```
NEW  searched: 48 file(s), 2 archive(s) unpacked, 1 base64 payload(s) decoded
     members containing the sentinel: 1   -> .decoded-0.bin.unzipped/0969a537….json
     ::error::the sentinel survives into the artifacts that CI would upload      [exit 1]

OLD (6bf0a0e's sweep-artifacts.sh, same bytes)
     searched: 45 file(s), 1 archive(s) unpacked
     members containing the sentinel: 0
     OK: the sentinel appears in no member                                        [exit 0 — FALSE PASS]
```

This is the clearest single result in the round: the old sweep returned a green
verdict on a tree that was leaking. The retraction in
`docs/evidence/VZ-FOUND-008/README.md` and in AGENTS.md is accurate and required.

### `error-context.md` with and without `PLAYWRIGHT_NO_COPY_PROMPT` (my own red/green pair)

Same spec, same config, one variable:

```
PLAYWRIGHT_NO_COPY_PROMPT unset:  # Instructions  # Test info  # Error details  # Page snapshot   (39 lines)
                                  # Page snapshot contains: "- textbox [active] [ref=f1e2]: TYPD5135ECFE0AF2525478"
PLAYWRIGHT_NO_COPY_PROMPT=1    :  # Instructions  # Test info  # Error details                    (30 lines)
                                  typed marker occurrences in error-context.md: 0
```

F10's control is real, and it removes the richest channel. What remains in the
file is the assertion message (with the received value) and the harness's own
guard message. **`# Test source` did not appear in either run** — Playwright emits
it only when the last meaningful error has a parseable stack location whose file
it can read (`errorContext.js:86,99-113`); see §9 for the doc consequence.

---

## 2. My own mutations against the new lane-guard rules

Driven with `bash scripts/ci/check-e2e-lane.sh` on a sandbox copy, one mutation at
a time, restored between cases; baseline green before and after the whole battery.
**RED = refused by name.**

| Case | Result |
|---|---|
| A1 `path:` glob `test-*` | RED |
| A2 `path:` `${{ github.workspace }}` | RED |
| A3 `path:` `.` | RED |
| A4 multi-line `path:` with a `!` exclusion | RED (names the glob/exclusion metacharacter) |
| A5 `path:` `..` | RED |
| A6 `playwright-report/index.html` re-added | RED (names the base64 ZIP in the message) |
| A7 `path:` `**` | RED |
| B1 uploader forked to `someone/upload-artifact@<same sha>` | RED |
| B2 `actions/cache` whose path is `.vizra-e2e` | RED (`uses:` allowlist) |
| B3 third-party `docker/login-action` | RED |
| B4 same action at `@v4` instead of the pinned SHA | RED |
| B5 a **second job** in `e2e.yml` with an uploader of `.` | RED |
| B7 a **second workflow file** uploading `.vizra-e2e` | RED (repo-wide deny sweep) |
| B8 reusable workflow (`jobs.<id>.uses`) | RED |
| C1 `>>"$GITHUB_STEP_SUMMARY"` | RED |
| C2 `\| tee -a "$GITHUB_STEP_SUMMARY"` | RED |
| C4 `> "${GITHUB_STEP_SUMMARY:-/dev/null}"` | RED |
| D1/D2 `include-hidden-files: true` / `'true'` | RED |
| D3 `include-hidden-files: false` | green (correct — the allowed value) |
| D4 `retention-days: 14` | RED |
| D5 `retention-days` removed | RED |
| E1–E4 `scripts.e2e` + `--trace on` / `--output` / `--reporter html` / `--config` | RED, each by name |
| F1 `DEBUG: pw:api` at **job** level | RED |
| F2 `DEBUG: pw:api` at **step** level | RED |
| F4/F5/F6 `PLAYWRIGHT_NO_COPY_PROMPT` removed / `"0"` / `""` at job level | RED |
| F8 `PLAYWRIGHT_HTML_REPORT` at step level | RED |
| G1/G2/G5 `globalSetup`/`globalTeardown` literal or string key | RED |
| G3 `globalSetup` spread from another object | RED (`unreadable-spread` — fails closed) |
| G4 `globalSetup` as a computed key | RED (`computed-key`) |
| G7 lane step `npm run e2e -- --config=other.ts` | RED |
| G8 `PLAYWRIGHT_CONFIG` at step level | RED |

**Not caught (green):** B6, B9, B10, C3, E5, E6, F3, F7, G6 — analysed as findings
in §8 or classified as stated residuals.

---

## 3. The tokenising call check (debt b)

Probed `hasGenuineCall()` in `scripts/ci/ts-source-facts.mjs` directly, 24 shapes:

| Shape | Verdict |
|---|---|
| a real call | GREEN (baseline) |
| trailing line comment `void 0; // f(a,b)` — prev. verifier defeat 1 | **RED** `absent` |
| string literal `const s = "f(";` — prev. verifier defeat 2 | **RED** `absent` |
| block comment / JSDoc | **RED** `absent` |
| `void f(a,b)` — prev. verifier defeat 3 | **RED** `void-discarded` |
| `void (f(a,b))`, `cond ? void f() : 0` | **RED** `void-discarded` |
| shadowed local `const formatOrphans = () => {}` | **RED** `shadowed` |
| shadowed in a block scope | **RED** `shadowed` |
| shadowed as a function parameter | **RED** `shadowed` |
| re-assigned alias `const g = f; g()` | **RED** `absent` (fails closed) |
| tagged template ``f`x` `` | **RED** `absent` (fails closed) |
| `new f()` | **RED** `absent` (fails closed) |
| `obj.f()` | **RED** `absent` (fails closed) |
| `const _ = f()` | GREEN — **review-only** |
| `f();` result dropped | GREEN (a genuine call) |
| `if (false) f()` | GREEN — **review-only** |
| inside a nested function never called | GREEN — **review-only** |
| dead code after `return` | GREEN — **review-only** |
| `f?.()` | GREEN (genuinely calls) |
| inside a template expression / a `throw` | GREEN (genuinely calls) |

All three previously-measured defeats are closed **by construction**, `void` and
shadowing are refused with distinct named reasons, and every over-strict case
fails closed. AGENTS.md § Residuals states the review-only class as
"whether a call's RESULT is used in a way that matters — `const _ = f(…)` and a
call inside a branch that never runs both satisfy the check". That is accurate;
it under-enumerates (a nested never-called function and dead code after `return`
are the same class and are not listed) but names the class correctly and claims
nothing more.

## 4. `globalSetup` refusal (debt c)

G1–G5, G7, G8 above: every spelling I could construct is refused, and the two
unreadable spellings (spread, computed key) **fail closed** rather than being
waved through. A setup **project** remains allowed, which is correct — the
previous verifier established setup projects are fully guarded. A stray second
config file (G6) is green but inert: it is only selected via argv or env, and
both of those are RED (G7, G8).

## 5. The sanitiser and the redactors

**Sanitiser** (`sanitiseExternalText`, probed directly, markers minted at runtime):

| Input | Result |
|---|---|
| `LF` + `::error::` | collapsed to `⏎`; no real CR/LF survives |
| `CRLF` + `::set-output::` | collapsed |
| bare `CR` | collapsed |
| leading `::` with no newline | prefixed with U+200B — inert |
| `%0A` / `%0D` / `%25` / `%250A` | escaped (`%25` first, so no double-escape bug) |
| bare `ESC`, `NUL` | replaced with U+FFFD |
| 300 chars | capped at 200 + a "(100 more character(s) dropped)" suffix |
| 200 chars exactly | untouched |
| **leading whitespace then `::`** (`"  ::error::…"`) | **not** escaped — see FINDING 5 |

Demonstrated end to end on the running lane, not only in a unit test: the probe
page's `console.error("\n::error::injected …")` appears in the real
`error-context.md` as `[console] console.error: ⏎::error::injected CNSL…` — the
newline is gone, so the injected workflow command can no longer start a log line.

**URL redaction** — identical results from `e2e/harness/redact.ts` and from
`scripts/ci/redact-artifacts.sh` (they really do carry the same three programs):

| Shape | Redacted? |
|---|---|
| `https://h/p?q`, `ws://h/p?q` | yes |
| `host.example:3219/p?q` (dotted + port) | yes |
| `host:3219/p?q` — **the PR #3 F13 string, verbatim** | **yes** |
| `localhost/p?q`, `localhost:3000/p?q` | yes |
| `127.0.0.1:3987/media/p.jpg?q` | yes |
| `//host.example/p?q` (authority-relative, no port) | yes |
| `/media/p.jpg?q`, `/media/p.jpg#frag` | yes |
| HAR `"queryString":[…]` | emptied |
| query-less URL; `see step 3/4?` | untouched (correct) |
| secret in a **path segment** | not redacted — **by design and documented** |
| `myhost/p?q` (undotted, no port) | not redacted — **documented exactly** |
| `//host.example:8443/p?q` | **NOT redacted** — FINDING 4 |
| `[::1]:3000/p?q`, `[2001:db8::1]/p?q` | **NOT redacted** — FINDING 4 |
| `{"u":"https:\/\/h\/p?q"}` (JSON-escaped slashes) | **NOT redacted** — FINDING 4 |
| `HTTPS://h/p?q` (uppercase scheme) | **NOT redacted** — FINDING 4 |

**Control bytes.** `redact.ts` contains no NUL and no other C0 control byte. I
swept every `e2e/**/*.ts`, `scripts/**/*.mjs` and `scripts/**/*.sh` at this SHA
for bytes outside `\t \n \r` + printable: **zero files**. The NUL incident the
builder declared is cleaned up. **No check would catch a recurrence** — see
FINDING 6.

## 6. Debt (a) — `worker-guard.ts` and the digest ledger

`e2e/harness/worker-guard.ts:70-71` no longer says deleting the assertion "is not
silent". The replacement text states what the check now does, names all three
measured defeats, and ends by pointing at `AGENTS.md § Residuals` — which closes
the "not adequate at the point of use" half of C4.

`docs/evidence/VZ-FOUND-008/mutation-digests.txt` was regenerated. **Every
BEFORE/RESTORED digest matches the file at this SHA** — I recomputed all five:

```
f336c5ca…  e2e/harness/browser-errors.ts     ✓
03ba7ec5…  e2e/demos/console-error.demo.ts   ✓
a86c8557…  e2e/harness/creation-guard.ts     ✓
4ed1b86d…  e2e/harness/test.ts               ✓
4469d8f8…  e2e/harness/worker-guard.ts       ✓
```

The debt is paid **at this SHA**. It was not paid commit-by-commit — see FINDING 7.

## 7. Lanes at this SHA (all run by me, in my own clone)

| Lane | Result |
|---|---|
| `npm run ci` | exit 0 — **16 files / 409 tests / 0 skipped**; 1 eslint **warning** (below) |
| `bash scripts/ci/require-checks_test.sh` | exit 0 — **141 cases, 148 assertions, 0 failed** |
| `bash scripts/ci/check-e2e-lane.sh` | exit 0 |
| `bash scripts/ci/check-required-floor.sh` | exit 0 (`frontend contract e2e`) |
| `bash scripts/ci/check-image-pins.sh` | exit 0 (3 FROM lines @sha256-pinned) |
| `npm run check:contract` | exit 0 |
| `npx playwright test` | exit 0 — **18 passed**, floor OK (9/9 9/9), **18 stamps** |
| `node scripts/ci/harness-canary.mjs` | exit 0 — failed all 4 fault-injection fixtures, each for its own kind |
| `npm run e2e:demos` (quiescent tree) | exit 0 — **123 halves passed, 0 blocked, 0 failed** (matches the PR; see FINDING 1 for the loaded-machine run) |
| credential tripwire (`no-credentials-in-specs.test.ts`) | exit 0, 10 tests passed |

**Commit boundaries.** `npm run ci` is green (exit 0) at all six commits and at the
base. The **counts** are not what the PR claims — see FINDING 7.

**Credentials.** No credential-shaped string in any added line across the six
commits (swept for `ghp_`, `github_pat_`, `AKIA…`, `-----BEGIN`, JWT shapes:
zero hits). GitGuardian is `success` on this SHA. No spec authenticates, fills a
credential or touches a signed URL; the tripwire passes.

## 8. CI on `e0960539…`

All **8** check-runs `completed` / `success`:
`ci-required` (09:12:14, last — after `e2e` at 09:11:28), `frontend`, `contract`,
`guard`, `e2e`, `deps-scan`, `image-scan`, `GitGuardian Security Checks`.

Manifest `.github/required-checks.txt` at this SHA declares `frontend`,
`contract`, `?guard`, `?docker-build`, `e2e`. What actually ran: `frontend` ✓
`contract` ✓ `guard` ✓ `e2e` ✓; `?docker-build` is optional-if-absent and
path-filtered with no Dockerfile touched. No skipped/cancelled/timed-out lane in
the required set. The manifest matches the jobs that ran.

`e2e` job log for this SHA carries `18 passed`,
`e2e coverage floor: OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9)`,
`e2e harness stamp: OK (18 succeeding result(s) verified)`,
`PLAYWRIGHT_NO_COPY_PROMPT: 1` in the step env, and the canary's
`failed all 4 fault-injection fixtures` line.

**There is no RED run on this SHA**, so the uploaded-artifact set was never
exercised in CI here — the upload step is `if: failure() && steps.redact.outcome == 'success'`
and a green run publishes nothing. I do not infer it; I reproduced it locally
instead (§1).

---

## 9. Truthfulness audit

Checked every claim in AGENTS.md's artifact-privacy section, its "NOT covered"
tables, § Residuals, the visibility/retention sentence, the VZ-FOUND-008 README
retraction, and the PR body against what I measured.

**Accurate and reproduced:**

- The FINDING 3 retraction — "every 'verified end to end' redaction measurement
  was made with a search blind to this file", including the "239 `?<redacted>`,
  zero live queries" figure and D9's "3 members → 0". Reproduced in §1.
- "`playwright-report/` is no longer uploaded … enforced by `check-e2e-lane.mjs`
  across every job of the file, with globs, `${{ }}`, `.` and `..` all refused."
  Reproduced: A1–A7, A6, B5.
- "`sweep-artifacts.sh` decodes then recurses." Reproduced; direction confirmed
  (a false pass becomes a named red). The specific "1 member → 5" figure is from
  the builder's probe tree, not reproducible against mine (I measure 0 → 1 over
  `playwright-report/` alone); the claim is about their tree and I do not dispute it.
- "`PLAYWRIGHT_NO_COPY_PROMPT: "1"` at job level … `check-e2e-lane.mjs` asserts it
  is set." True at job level (F4/F5/F6 RED). But see FINDING 2.
- The three-programs claim for both redactors — true, including that both carry the
  same gaps.
- The over-redaction price (`1:23/foo?x=y`) and the undotted-host limit — stated
  exactly as implemented.
- Retention 3 days, enforced (D4/D5 RED); the visibility sentence names PRIVATE
  repositories and "readable by collaborators, not the public", and adds the
  correct nuance that "not public is not not-published". `gh` confirms the four
  repositories are private.
- The `run:`-exfiltration residual is **stated, not claimed away**: "An arbitrary
  `run:` step can still exfiltrate — `gh release upload`, `curl`, anything. No
  workflow parser can close that." My B9/B10 are green, which is exactly what that
  bullet predicts. Correctly handled.
- § Residuals' six-row defeat table and the review-only sentence match my §3.
- The PR body's "What did NOT change" section is accurate: no authenticated lane,
  the hard rule intact, the uncovered channels still uncovered and still uploaded.
- The plan's two retracted phase-1 claims (M6 "no configuration option gates it";
  M8 on `# Test source`) are retracted in the PR body and in AGENTS.md.

**Sentences stronger than their control** (each is a finding below):

1. AGENTS.md: "**Covered** — query strings and fragments on URLs that carry a
   scheme or start at `/`". `//host:8443/p?q` starts at `/` and is **not**
   covered; `HTTPS://h/p?q` carries a scheme and is **not** covered; an IPv6
   literal authority is not covered. → FINDING 4.
2. AGENTS.md's ALLOWLIST is quoted as three paths
   (`test-results/`, `playwright-report/results.json`, `playwright-browsers.txt`);
   `ALLOWED_UPLOAD_PATHS` in the code actually permits a **fourth**,
   `e2e-failure-summary/`, which nothing uploads today and which belongs to the
   unlanded PR B. → FINDING 3.
3. AGENTS.md's "NOT covered" table maps "a non-URL token in a console message" to
   `*-trace.trace` only. I measured it surviving additionally in
   `error-context.md`, in trace `attachments/` and `resources/*.html`, and in
   **`playwright-report/results.json`** — which is uploaded. Likewise the
   assertion's received value reaches `results.json`, and no row names
   `results.json` at all. The table under-states *where*, not *whether*. → FINDING 8.
4. AGENTS.md describes `error-context.md` as carrying "a `# Test source` code
   frame (±100 lines of `errorLocation.file`)". Neither of my two runs produced
   that section. The mechanism exists in Playwright but is conditional
   (`errorContext.js:86,99-113`). Over-description in the *safe* direction; noted,
   not a finding.
5. The PR body claims `npm run ci` is "**16 files / 409 tests / 0 skipped** at
   EVERY commit boundary". It is not. → FINDING 7.

**Reproduced after an initial failure to do so:** the PR's "**123 halves passed /
0 blocked / 0 failed**". My first run measured 121/0/2 with two inverse controls
red; my second, on a clean tree with nothing else running, measured exactly
123/0/0, exit 0. The claim stands; what does not is the suite's ability to say
which of the two situations you are in → FINDING 1.

**On the two declared deviations.**

- **F10 (unit test + require-checks mutation instead of a demonstrate.sh red/green
  pair): adequate on the control, thin on the ledger.** I produced the red/green
  pair myself in §1 and the control works exactly as claimed. But this repository's
  own standard is that the compensating control gets a committed demonstration, and
  F10's acceptance criterion in the binding spec is explicit — "the demonstration
  shows the section present without the variable and absent with it". No such
  transcript exists in `docs/evidence/VZ-FOUND-008/`. The require-checks mutation
  proves the *workflow key* is asserted; it proves nothing about what the variable
  *does*. Recorded as FINDING 9 (SHOULD), not a blocker, because I reproduced the
  behaviour and it holds.
- **F13 (URL fix demonstrated against the verbatim string through the shipped
  `redact-artifacts.sh` rather than a new D9 `page.goto` half): adequate.** The
  verbatim PR #3 string redacts in both redactors, and I additionally observed the
  sanitiser working on a real running lane through a real page-controlled console
  message. A `page.goto` half would add reachability evidence that my §1 probe has
  now supplied independently.

---

## Findings

```
FINDING 1: `e2e:demos` reproduces on a quiescent tree, but under machine load two
           INVERSE controls fail for an infrastructure reason that is reported as
           "a demonstration did not demonstrate"
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/e2e/demonstrate.sh (the :3211 production server lifecycle;
             D15i, D15k)
  requirements: VZ-FOUND-008

Observed:
  TWO runs at e0960539 in a dedicated clone of the PR head, and the difference
  between them is the point:

  Run 1 — started immediately after the production build, with other verification
  work of mine running concurrently on the same machine (the tree also reported
  `tree state: 2 modified/untracked path(s)` at start):

      halves passed: 121 | blocked: 0 | failed: 2        [exit 1]
      FAIL d15i-before-phase-accounting-cut-GREEN: exit 1, wanted 0
      FAIL d15k-honest-beforeAll-stays-GREEN:      exit 1, wanted 0

      Both transcripts carry, in the orphan list that fired:
        [requestfailed] requestfailed: GET http://127.0.0.1:3211/ — net::ERR_CONNECTION_REFUSED

  Run 2 — `git checkout -- . && git clean -qfd`, `git status --porcelain` empty,
  nothing else of mine running:

      halves passed: 123 | blocked: 0 | failed: 0        [exit 0]

  **The builder's claim of 123/0/0 reproduces.** Nothing was listening on :3211
  before or after either run (`lsof -nP -iTCP:3211` empty), and
  `server-production.log` shows a normal start in both.

Failure:
  Not a defect in the controls, and I withdraw any suggestion that the PR's
  number is wrong — it is right. What is worth fixing is the DIAGNOSIS: when the
  demonstration's own server becomes unreachable mid-suite, the failure surfaces
  as two inverse-control halves going red with a generic orphan-accounting
  message, and the suite's verdict line reads "a demonstration did not
  demonstrate. That is a failure, not a formality." An operator reading that
  transcript would reasonably conclude the harness had regressed. The suite fails
  CLOSED, which is right; it fails UNINFORMATIVELY, which costs a verifier a full
  re-run (~15 minutes, no subset mode) to tell an infrastructure fault from a
  real one — and in the other direction, a genuine regression in D15 could be
  dismissed as "probably the server again".

Perspective: developer

Recommendation:
  1. Health-check :3211 immediately before each half (or detect
     `ERR_CONNECTION_REFUSED` against the demo server in the transcript) and emit
     `BLOCKED: the demonstration server went away` rather than FAIL. `BLOCKED` is
     already a first-class outcome in this suite and is exactly the right one.
  2. Give `demonstrate.sh` a way to run one group (`D15`), so re-testing a
     suspected flake does not cost the whole suite.
  3. Record in the README that the suite needs a quiescent machine, since the
     builder independently hit the same class of problem (it declared two runs
     discarded for concurrent edits).

Acceptance criteria:
  Killing the :3211 server mid-suite yields `BLOCKED`, naming the server, rather
  than a FAIL on an inverse control.

Tests: the suite itself.
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge:
  "It passed on the clean run, so there is nothing to fix." The clean run is why
  this is SHOULD and not a blocker. The fix is about what the suite says when it
  is wrong, which is the only time anybody reads it closely.
```

```
FINDING 2: F10's own control can be removed at STEP level while the lane guard
           stays green — `PLAYWRIGHT_NO_COPY_PROMPT: ""` on the lane step
           restores the page snapshot
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-e2e-lane.mjs:1032 (REQUIRED_JOB_ENV, job scope only)
             scripts/ci/check-e2e-lane.mjs:1033 (ALLOWED_PLAYWRIGHT_ENV exempts the key),
             :1038-1049 (the required check reads `laneJob.env` only), :1059 (the refusal)
             .github/workflows/e2e.yml (job env), AGENTS.md (the F10 paragraph)
  requirements: VZ-FOUND-008

Observed:
  The guard checks `PLAYWRIGHT_NO_COPY_PROMPT` in exactly one place — the `e2e`
  job's own `env:` map — and separately refuses `PLAYWRIGHT_*` keys EXCEPT the
  ones on `ALLOWED_PLAYWRIGHT_ENV`, which contains this key. So a step-level
  entry on the lane step is neither required-to-be-"1" nor refused.

  Mutation F7, applied to the lane step:

      - name: Browser lane (desktop 1440, mobile 390)
        env:
          E2E_BASE_URL: http://127.0.0.1:3000
          PLAYWRIGHT_NO_COPY_PROMPT: ""        # <- added
        run: npm run e2e

      bash scripts/ci/check-e2e-lane.sh   ->   exit 0, "OK: …"

  A step-level `env:` overrides the job-level value in GitHub Actions, and the
  gate in Playwright is truthiness, not presence:

      playwright/lib/index.js:657-659
        async _takePageSnapshot(context) {
          if (process.env.PLAYWRIGHT_NO_COPY_PROMPT) return;

      node: PLAYWRIGHT_NO_COPY_PROMPT=""  -> truthy: false   (snapshot IS taken)
            PLAYWRIGHT_NO_COPY_PROMPT="0" -> truthy: true    (still suppressed)

  And I measured what comes back when it is falsy, on the real lane (§1):
  `# Page snapshot` returns, carrying a `page.fill` value verbatim
  (`- textbox [active] [ref=f1e2]: TYPD5135ECFE0AF2525478`).

Failure:
  F10's acceptance criterion is "Removing the variable from the workflow is RED
  in the lane guard". Removing it from the JOB is red (F4). Neutralising it at
  the STEP — the same file, one line, the same reviewer surface, and the more
  natural place for someone to put a lane-local variable — is GREEN, and it
  restores "the single richest private-data channel in what this lane uploads"
  (AGENTS.md's own words). The guard's job-level check is not a control over the
  effective value; it is a control over one of the two places the value is set.

  This is the exact defect class the chair flagged for this area: a control
  described more strongly than it is. AGENTS.md says "`check-e2e-lane.mjs`
  asserts it is set", which a reader will take as "the snapshot is off in CI,
  asserted" — and it is not, for a one-line edit that no check names.

Perspective: developer, then member (from M1 the snapshot is the product page)

Recommendation:
  Assert the EFFECTIVE value, not the job-level one. Smallest correct fix in
  `check-e2e-lane.mjs`: after the existing job-level check, refuse any STEP-level
  `PLAYWRIGHT_NO_COPY_PROMPT` in the `e2e` job whose value is not exactly "1"
  (or refuse a step-level occurrence outright — nothing needs one). While there,
  the same reasoning applies to a step-level re-definition of any key the job
  sets for a privacy reason.

Acceptance criteria:
  `require-checks_test.sh` gains three cases, each RED by name:
  `PLAYWRIGHT_NO_COPY_PROMPT: ""` at step level; `: "0"` at step level;
  the key present at step level with any value other than "1".

Tests: scripts/ci/require-checks_test.sh.
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge:
  "Editing `.github/workflows/e2e.yml` is a CODEOWNERS path and a reviewer would
  see it." The same is true of removing it from the job env — and that case was
  judged worth asserting. The whole point of this guard, in its own words, is
  that "these properties are invisible in a green run"; a step-level empty string
  is more invisible than a deletion, not less.
```

```
FINDING 3: the workflow-level `env:` scope is unchecked, so `DEBUG: pw:api` at
           the top of the file turns on the protocol dump with the guard green
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-e2e-lane.mjs:1051-1057 (`envScopes` = job env + the
             e2e job's step envs; the workflow's own top-level `env:` is never read)
  requirements: VZ-FOUND-008

Observed:
  Mutation F3 — a top-level `env:` block added beside `permissions:` in
  `.github/workflows/e2e.yml`:

      env:
        DEBUG: pw:api

      permissions:
        contents: read

      bash scripts/ci/check-e2e-lane.sh   ->   exit 0, "OK: …"

  Compare F1 (the identical key at job level) and F2 (at step level): both RED.
  Workflow-level `env:` is inherited by every job, so the effective environment
  of the lane step is the same in all three cases.

Failure:
  FINDING 9's stated purpose is that "a single `DEBUG=pw:api` turns Lane B's
  stdout into a full protocol dump with headers and fill values" into the GitHub
  log, "which no post-hoc redactor can reach because the log is streamed as it is
  written". The guard closes two of the three scopes GitHub offers and does not
  name the third. Nothing in AGENTS.md or § Residuals says the workflow scope is
  unchecked, so the refusal reads as complete.

Perspective: developer, operator

Recommendation:
  Add the workflow's own top-level `env:` to `envScopes` in
  `check-e2e-lane.mjs` — one line, and it is the same map shape the other two
  scopes already use.

Acceptance criteria:
  `require-checks_test.sh`: `DEBUG: pw:api` in a top-level `env:` is RED by name;
  `PWDEBUG` and an unlisted `PLAYWRIGHT_*` key there are RED too.

Tests: scripts/ci/require-checks_test.sh, three cases.
Cross-repo implications: core: none | user: as above | search: none | meta: the
  same three scopes apply to any CI fan-in vizra-core grows.
Challenge:
  "No workflow here has a top-level `env:`, so there is nothing to check."
  That is precisely the condition under which adding one is invisible.
```

```
FINDING 4: four URL shapes are not redacted by either redactor, and AGENTS.md's
           "Covered" sentence names two of them as covered
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/redact.ts:86-96 (authorityRelative), :97-100 (path-relative),
             :62 (absolute, no `i` flag)
             scripts/ci/redact-artifacts.sh (ABSOLUTE_PROGRAM, RELATIVE_PROGRAM,
             AUTHORITY_PROGRAM — the same three shapes, the same gaps)
             AGENTS.md § "Artifact privacy", the "Covered" paragraph
  requirements: VZ-FOUND-008

Observed:
  Runtime-minted marker, both redactors, identical results:

      //host.example:8443/p?sig=<M>      NOT redacted
      [::1]:3000/p?sig=<M>               NOT redacted
      [2001:db8::1]/p?sig=<M>            NOT redacted
      {"u":"https:\/\/host/p?sig=<M>"}   NOT redacted   (JSON-escaped slashes)
      HTTPS://host.example/p?sig=<M>     NOT redacted   (uppercase scheme)

  Mechanism: the authority alternatives are `(?:[\w-]+\.)+[\w-]+(?::\d+)?`,
  `[\w-]+:\d{1,5}` and `localhost` — a bracketed IPv6 literal matches none of
  them; the path-relative program's character class `[A-Za-z0-9._~%/+-]` excludes
  `:` and `\`, so `//host:8443/p?` and `https:\/\/h\/p?` both fall out of it; and
  the absolute program is case-sensitive.

  AGENTS.md's covered-claim reads: "query strings and fragments on URLs that
  carry a scheme or start at `/`". `//host:8443/p?q` starts at `/`.
  `HTTPS://h/p?q` carries a scheme. Both are named as covered and are not.

Failure:
  This is the fifth round in which a URL shape was missed, and the section's own
  argument is that predicting shapes is the wrong control. The defect that
  matters is not the four regexes — none of these shapes is reachable from
  today's lane, which drives `127.0.0.1` over lowercase `http` with standard
  JSON — it is that the sentence describing the coverage is broader than the
  coverage. A reader deciding whether a red lane is safe to share reads that
  sentence.

Perspective: developer, then member

Recommendation:
  Two things, and the second matters more than the first.
  1. Cheap and worth doing: add the `i` flag to the absolute program in both
     redactors (one character, closes the uppercase case), and add a bracketed
     IPv6 authority alternative `\[[0-9A-Fa-f:.]+\](?::\d{1,5})?`.
  2. Required regardless: narrow the AGENTS.md sentence to what the three
     programs actually match, and add the unmatched shapes to the "NOT covered"
     table — `//host:port/…`, IPv6-literal authorities, and backslash-escaped
     schemes — in the same voice the undotted-host limit is already stated in.
     Do NOT widen the claim again without a measurement.

Acceptance criteria:
  `e2e/harness/redact.test.ts` gains a case per shape, asserting the CURRENT
  behaviour explicitly (redacted, or pinned as known-not-covered), so the next
  round cannot re-discover them; the AGENTS.md sentence maps clause-by-clause to
  a test.

Tests: e2e/harness/redact.test.ts, five cases.
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge:
  "These shapes cannot occur in this lane." True today, and I say so above. The
  finding is about the sentence, which is read by people deciding what to share,
  and about the precedent: four rounds of adding one shape at a time is what the
  section itself argues against.
```

```
FINDING 5: the sanitiser escapes a leading `::` but not a leading-whitespace `::`
Severity:    SHOULD
Confidence:  medium
Affected:
  repo: vizra-user; files: e2e/harness/redact.ts:145 (`if (out.startsWith("::"))`)
  requirements: VZ-FOUND-008
Observed:
  sanitiseExternalText("  ::error::<M>")  ->  "  ::error::<M>"   (unchanged)
  sanitiseExternalText("::stop-commands::<M>") -> "​::stop-commands::<M>"  (escaped)
Failure:
  The GitHub Actions runner matches a workflow command after trimming the line,
  so a leading-whitespace `::` is the same command as a bare one. Reachability is
  LOW and I say so plainly: every place the harness prints this text today
  prefixes it (`[console] console.error: …`), so the sanitised string is never at
  the start of a log line, and the CR/LF collapse — which I verified works on the
  real lane — already prevents the text from starting a line of its own. This is
  a gap in the belt, not in the braces.
Perspective: operator
Recommendation: test the trimmed string — `if (out.trimStart().startsWith("::"))`
  — and keep the ZWSP where it is.
Acceptance criteria: a redact.test.ts case for `"  ::error::x"`.
Tests: e2e/harness/redact.test.ts, one case.
Cross-repo: core: the same rule belongs in structured logging of remote actor fields.
Challenge: "It is unreachable." Today. The bullet above it in this very file is
  about a control that was unreachable until it was not.
```

```
FINDING 6: nothing in any lane would catch another NUL-byte incident, and nothing
           validates the digest ledger against the tree
Severity:    SHOULD
Confidence:  high
Affected:
  repo: vizra-user
  files: package.json (`ci` = lint && typecheck && test && build)
         scripts/e2e/demonstrate.sh (the only writer of mutation-digests.txt)
  requirements: VZ-FOUND-008
Observed:
  (a) The builder declared that a Write briefly put literal NUL bytes into
      `redact.ts`, caught by hand with `od`. I confirm the tree is clean now —
      zero control bytes in every `e2e/**/*.ts`, `scripts/**/*.mjs`,
      `scripts/**/*.sh` at this SHA. I also confirm that `tsc`, `eslint` and
      `vitest` were green ON the NUL-bearing file, as the builder said: nothing
      in `npm run ci` reads for control bytes.
  (b) `docs/evidence/VZ-FOUND-008/mutation-digests.txt` is WRITE-ONLY evidence.
      `demonstrate.sh` overwrites it; nothing reads it back, diffs it, or exits
      non-zero on a mismatch. `git grep mutation-digests` at this SHA hits three
      files: the writer, the README prose, and a recorded transcript. No script
      under `scripts/ci/`, no workflow, no package.json entry. A stale ledger is
      invisible.
  (c) Residual note: `AGENTS.md` stopped mentioning `mutation-digests` at bbc8882.
Failure:
  Two evidence-integrity controls that this repository relies on rhetorically are
  not enforced anywhere. (b) is what made FINDING 7 possible and undetectable.
Recommendation:
  A five-line `scripts/ci/check-source-bytes.sh` in the `guard` lane refusing any
  C0 control byte outside \t\n\r under `e2e/**` and `scripts/**`; and a mode of
  `demonstrate.sh` (or a tiny checker) that COMPARES the regenerated ledger with
  the committed one and exits non-zero on a difference.
Acceptance criteria: a planted NUL is RED in `guard`; a hand-edited digest line
  is RED in whatever lane owns the comparison.
Tests: scripts/ci/require-checks_test.sh.
Cross-repo: core: same byte rule for generated Go/SQL.
Challenge: "`od` caught it." A person did, once, because they were looking.
```

```
FINDING 7: the digest ledger committed at 5553142 describes a tree that did not
           exist until 5dcb123, and the "16 files / 409 tests at EVERY commit
           boundary" claim is false
Severity:    SHOULD
Confidence:  high
Affected:
  repo: vizra-user
  files: docs/evidence/VZ-FOUND-008/mutation-digests.txt (committed at 5553142)
         PR #8 body ("`npm run ci` … at every commit boundary")
  requirements: VZ-FOUND-008
Observed:
  (a) Commit 5553142's message says the ledger "is regenerated in THIS commit
      because it pins this file's bytes". It records
      `D12 browser-errors.ts BEFORE/RESTORED f336c5ca…`. But
      `e2e/harness/browser-errors.ts` is `caa78ffe…` at 5553142, 5c53287 and
      58f20a6, and only becomes `f336c5ca…` at 5dcb123 — two commits later:

          commit    browser-errors.ts   ledger's D12 entry
          6bf0a0e   caa78ffe            caa78ffe    consistent
          5553142   caa78ffe            f336c5ca    INCONSISTENT
          5c53287   caa78ffe            f336c5ca    INCONSISTENT
          58f20a6   caa78ffe            f336c5ca    INCONSISTENT
          5dcb123   f336c5ca            f336c5ca    consistent
          e096053   f336c5ca            f336c5ca    consistent  <- the verified SHA

      So the ledger was produced from a tree equal to the FINAL one and
      back-committed into the first commit (a rebase or amend), and for three
      commit boundaries the repository carried a digest ledger asserting a digest
      no file in it had. Nothing would have noticed — see FINDING 6(b).
  (b) `npm run ci` is green (exit 0) at all six commits and the base, but the
      counts are: 15 files/355 tests at 5553142; 16/394 at 5c53287 and 58f20a6;
      16/409 at 5dcb123, bbc8882, e096053. 0 skipped everywhere (no `.skip`/
      `.todo` anywhere; `vitest.config.mts` sets `passWithNoTests: false`).
  (c) On ONE cold run at e096053 during this verification, `npm run ci` exited 1:
      `e2e/harness/browser-errors.test.ts > applies the guarded-import rule to
      every one of them — Test timed out in 5000ms` (1 failed | 408 passed).
      Provenance and confidence, stated plainly: that observation comes from the
      delegated commit-boundary sweep, on a cold checkout. I then tried to
      reproduce it myself — five consecutive runs of that file (53 passed each
      time) and two full `npm run ci` runs — and could NOT. So: one observation,
      not reproduced, confidence MEDIUM. The mechanism is real and checkable
      without reproducing the flake: that case constructs `new ESLint({ cwd:
      repoRoot })` and lints in-process (`browser-errors.test.ts:484-487`; the file builds 13 such in-process ESLint
      instances in all), and
      `vitest.config.mts` sets no `testTimeout`, so it runs under vitest's 5 s
      default. A cold or loaded GitHub runner can therefore turn `ci-required`
      red at this SHA for a reason unrelated to the change.
Failure:
  (a) and (b) are both "evidence that is stronger than the measurement". Neither
  changes the state AT the verified SHA — the ledger matches the tree at e096053,
  which is what the debt required, and every boundary is green — but the PR body
  asserts a specific reproducible number that does not reproduce, and a reader
  auditing commit 5553142 in isolation would be reading a false ledger.
  (c) is a live flake on the merge candidate.
Recommendation:
  1. Correct the PR body to the per-commit counts, or drop the per-boundary claim
     and keep "green at every boundary", which is true.
  2. Say in the 5553142 commit message (or the README) that the ledger reflects
     the branch tip, since regenerating it per-commit is not practical.
  3. Give that one vitest case an explicit `testTimeout` — it is an in-process
     ESLint run on a 5 s default.
Acceptance criteria: the body's numbers match a run; `npm run ci` green on ten
  consecutive cold runs at the head.
Tests: none new beyond the timeout.
Cross-repo: none.
Challenge: "The ledger matches at the head, which is what was asked." Agreed, and
  that is why this is SHOULD and not a blocker.
```

```
FINDING 8: the "NOT covered" table under-states WHERE the uncovered channels
           survive, and never names `playwright-report/results.json`
Severity:    SHOULD
Confidence:  high
Affected:
  repo: vizra-user; files: AGENTS.md § "Artifact privacy", the "NOT covered" table
  requirements: VZ-FOUND-008
Observed:
  Measured on my red run, in the upload set, after redaction:
    - a page-controlled console token: table says `*-trace.trace`; I measured it
      in `error-context.md`, `trace.zip::attachments/*`,
      `trace.zip::resources/*.html`, `trace.zip::1-trace.trace`,
      `trace.zip::test.trace` AND `playwright-report/results.json`.
    - an assertion's received value: reaches `error-context.md`,
      `trace.zip::attachments/*`, `trace.zip::test.trace` AND `results.json`.
  `playwright-report/results.json` is on the upload allowlist and appears in no
  row of the table.
Failure:
  The table is the thing AGENTS.md tells a reader to consult "before you decide a
  red lane is safe to share". Someone reading "a non-URL token in a console
  message | *-trace.trace" may reason that not uploading traces would be enough.
  It would not: `results.json` alone carries it.
Recommendation: add a `Where it survives` entry for `playwright-report/results.json`
  and widen the two console/assertion rows to `error-context.md`, the trace
  members and `results.json`. The *whether* is right; only the *where* is short.
Acceptance criteria: each row's locations reproduce against a red probe run.
Tests: none (documentation), but the probe in §1 is the method.
Cross-repo: none.
Challenge: "The table is about channels, not file inventories." It has a "Where it
  survives" column.
```

```
FINDING 9: F10 and the upload allowlist have no committed demonstration, and the
           documented allowlist is one entry shorter than the enforced one
Severity:    SHOULD
Confidence:  high
Affected:
  repo: vizra-user
  files: scripts/ci/check-e2e-lane.mjs:804-810 (ALLOWED_UPLOAD_PATHS, four entries)
         AGENTS.md (quotes three paths); docs/evidence/VZ-FOUND-008/ (no F10 pair)
  requirements: VZ-FOUND-008
Observed:
  (a) `ALLOWED_UPLOAD_PATHS` permits FOUR literals — `test-results/`,
      `playwright-report/results.json`, `playwright-browsers.txt` and
      `e2e-failure-summary/`. AGENTS.md and the PR body both quote three. The
      fourth belongs to the unlanded PR B; nothing uploads it today, so it is
      latent rather than live, but the enforced allowlist is wider than the
      documented one and a `e2e-failure-summary/` upload would pass unremarked.
  (b) The binding spec's F10 acceptance is "the demonstration shows the section
      present without the variable and absent with it". No such transcript exists
      under docs/evidence/VZ-FOUND-008/. I produced the pair myself (§1) and it
      holds, so this is a ledger gap, not a control gap.
Failure:
  (a) is a doc-vs-control mismatch of exactly the kind this round is hunting;
  (b) leaves the strongest new privacy control with no committed red/green half.
Recommendation:
  (a) Either drop `e2e-failure-summary/` until PR B lands, or document it in the
      same sentence with "reserved for the authenticated lane; nothing writes it".
  (b) Add one D-half to demonstrate.sh for F10 when the demos suite is next
      touched (it is being touched anyway for FINDING 1).
Acceptance criteria: the documented allowlist and ALLOWED_UPLOAD_PATHS are
  byte-comparable; an F10 red/green pair exists.
Tests: scripts/ci/require-checks_test.sh already covers the enforcement.
Cross-repo: none.
Challenge: "The fourth path is harmless." It is. It is also undocumented, and the
  allowlist's whole value is that it is the reviewed list.
```

```
FINDING 10: npm lifecycle scripts (`pree2e`/`poste2e`) are neither pinned nor
            refused, so the pinned `scripts.e2e` can be bypassed
Severity:    SHOULD
Confidence:  high
Affected:
  repo: vizra-user; files: scripts/ci/check-e2e-lane.mjs:982-1001 (REQUIRED_SCRIPTS)
  requirements: VZ-FOUND-008
Observed:
  REQUIRED_SCRIPTS pins `e2e`, `e2e:install`, `e2e:demos` byte-for-byte (E1–E4 all
  RED). It does not enumerate what else `scripts` may contain. Adding
      "pree2e": "playwright test --trace on --output test-results"
  leaves `bash scripts/ci/check-e2e-lane.sh` at exit 0, and npm runs it: confirmed
  empirically —
      > vizra-user@0.0.0 pree2e
      PRE-SCRIPT RAN: this is where --trace on would go
      > vizra-user@0.0.0 e2e
  so a second Playwright invocation with every recorder on can write into
  `test-results/`, which IS uploaded. `poste2e` behaves the same.
Failure:
  FINDING 9's stated purpose is to close "what `npm run e2e` actually expands to".
  `npm run e2e` expands to `pree2e && e2e && poste2e`; the guard reads one third
  of it.
Recommendation:
  In the same loop, refuse any `scripts` key matching /^(pre|post)(e2e|e2e:.*)$/.
  Three lines, and it is the same file the check already parses.
Acceptance criteria: `require-checks_test.sh`: a `pree2e` key is RED by name; a
  `poste2e` key is RED by name.
Tests: scripts/ci/require-checks_test.sh, two cases.
Cross-repo: none.
Challenge: "package.json is reviewed." So is `scripts.e2e`, which is pinned anyway.
```

```
FINDING 11: an uploader in a DIFFERENT workflow file is unconstrained except for
            the `.vizra-e2e` name
Severity:    NIT
Confidence:  high
Affected:
  repo: vizra-user; files: scripts/ci/check-e2e-lane.mjs:823 (`allJobs` is e2e.yml only)
  requirements: VZ-FOUND-008
Observed:
  A new `.github/workflows/zz-probe.yml` whose job uploads `path: .` with
  `retention-days: 90` leaves the guard at exit 0 (mutation B6). Only clause (f),
  the `.vizra-e2e` deny sweep, crosses files — and that one IS red (B7).
Failure:
  None against the binding spec, which scoped clauses (a)–(e) to "the whole
  workflow FILE" and only (f) to "ANY workflow". Recorded because AGENTS.md's
  sentence — "enforced by `check-e2e-lane.mjs` across every job of the file" — is
  precise, and a reader could still generalise it. Note `include-hidden-files`
  defaults to false, so `path: .` would not itself sweep up `.vizra-e2e`.
Recommendation: one clause in § Residuals naming the file scope, or extend the
  `uses:`/`path:` allowlist sweep to every workflow in the directory.
Acceptance criteria: either the residual bullet exists, or B6 is RED.
Tests: scripts/ci/require-checks_test.sh, one case if the control is chosen.
Cross-repo: none.
Challenge: "Out of scope for PR A." Agreed — hence NIT.
```

---

## What I did NOT verify

- No RED CI run exists on this SHA, so the **uploaded artifact set in GitHub** was
  never observed; I reproduced the equivalent locally and say so rather than
  inferring it.
- `actions/upload-artifact@ea165f8d…`'s `include-hidden-files: false` default — the
  builder read it from the action's `action.yml` at the pinned SHA via the API. I
  did not re-fetch it; the guard's behaviour on the mutation is verified either way.
- The builder's "1 member → 5" sweep figure, which is about their probe tree.
- No UI surface changed in this PR, so no browser/viewport/keyboard pass was owed.

## Verdict

This is the strongest work this area has produced. The headline result is real and
I reproduced it independently, end to end, from a clean clone: FINDING 3's
base64-embedded report archive survives the shipped redactor verbatim, a raw grep
cannot see it, the old sweep returns a **false pass** on the exact bytes where the
new sweep goes red, and the PR closes it by removal rather than by a fifth
URL-shape prediction. Every earlier "zero live queries" figure is retracted in the
two places a reader would look. The tokenising call check closes all three
previously-measured defeats **by construction** and fails closed on every
over-strict shape I could invent. `globalSetup` is refused in every spelling I
could write, including the two unreadable ones. The sanitiser demonstrably
neutralises a real page-controlled workflow-command injection on a running lane —
I watched `\n::error::` become `⏎::error::` in a real `error-context.md`.
Retention, visibility, the `run:` residual and the review-only limits of the call
matcher are all stated exactly as implemented. 30 of my 41 workflow mutations are
refused by name, `require-checks_test.sh` is 141/148/0, the lane is 18/9-9/18
stamps, the canary fails all four fixtures, `e2e:demos` is 123/0/0 on a quiescent
tree, and CI is green on this SHA with a manifest that matches the jobs that ran.

I am nonetheless returning **FAIL**, on two findings that are the same defect
class the chair sent me to find, and nothing else.

**FINDING 2 (blocking) — a check that can be satisfied without the thing it
checks.** F10 is the headline new privacy control. `check-e2e-lane.mjs` requires
`PLAYWRIGHT_NO_COPY_PROMPT: "1"` in the `e2e` job's `env:`, and separately exempts
that key from its `PLAYWRIGHT_*` refusal. Adding `PLAYWRIGHT_NO_COPY_PROMPT: ""`
to the lane STEP — one line, same file, same reviewer surface, and the more
natural place to put a lane-local variable — leaves the guard at exit 0. Playwright
gates on truthiness, so the empty string restores `# Page snapshot`, and I measured
that half too: the section comes back carrying a `page.fill` value verbatim.
AGENTS.md publishes "`check-e2e-lane.mjs` asserts it is set". For that edit, it does
not. I record plainly that the PR **does** satisfy the security seat's literal
acceptance criterion ("Removing the variable from the workflow is RED"); my
objection is that the published sentence and the control diverge, which is the
thing this round exists to catch. The fix is roughly three lines and three test
cases.

**FINDING 4 (required) — a control described more strongly than it is.** AGENTS.md
says the redaction covers "query strings and fragments on URLs that carry a scheme
or start at `/`". `//host:8443/p?q` starts at `/` and is not covered.
`HTTPS://h/p?q` carries a scheme and is not covered. Bracketed IPv6 authorities
and backslash-escaped schemes are not covered either. None is reachable from
today's lane and I say so; the defect is the sentence, which is what a person
reads when deciding whether a red lane is safe to share — and one-shape-per-round
is exactly what that section argues against.

FINDINGS 3 and 10 are one-to-three-line gaps in the same F9 control (the workflow
`env:` scope is unread; `pree2e`/`poste2e` bypass the byte-pinned `scripts.e2e`).
FINDINGS 1, 5–9 and 11 are honest-limits, diagnosis-quality and
evidence-hygiene items that do not block.

Nothing I found is a live disclosure. Nothing in this repository authenticates,
the hard rule stands, it is asserted, and the tripwire passes 10/10. No credential
appears in any added line across the six commits and GitGuardian is green.

PASS is not a merge and not VERIFIED; FAIL here is not a judgement on the quality
of the work, which is high. It is that two published sentences are stronger than
the controls behind them, and this area does not get the benefit of the doubt on
that any more.

FINAL VERDICT: FAIL — SHA e0960539f20d2a484e430dab70718d2e3dd49c7c

---
---

# Re-verification at `4158b10` (2026-09-21 → 2026-09-22)

- **SHA verified:** `4158b10f8291e23cd726e2499db760aead195f4a` — seven commits on top of
  `e096053` (`bcc3bb4 1647f19 d818527 2bb8cb7 b0a9adb cf3753a 4158b10`), no amend, no
  force-push (`e096053` is still an ancestor in the PR's commit list). Confirmed unmoved
  via `gh api …/pulls/8` at the start, again after a machine restart, and at the end.
- **Interrupted once.** The machine restarted part-way through. Measurements taken before
  the restart are recorded below as such; my scratch clone did not survive, so everything
  after it was re-done from a NEW clean clone at the same SHA. Docker was restarted
  underneath me; I created no containers or images in this round, so there was nothing of
  mine to remove (the exited `vizra-m1a-*`, `vzb2-*`, `vzv9-*`, `vidra-*` containers are
  not mine and were left alone).
- **Environment:** macOS Darwin 25.5.0 arm64, node v22.14.0, npm 10.9.2, Playwright 1.63.0,
  clean clones under a private `mktemp -d`, `npm ci` exit 0 (415 packages).

## R2-1. `npm run ci` at the head (before the restart)

`npm run ci` exit 0 — **16 files / 423 tests / 0 skipped**. Matches the claim.

## R2-2. My mutation table against the new head (before the restart)

Same method as §2: `bash scripts/ci/check-e2e-lane.sh` on a sandbox copy, one mutation
at a time, restored between cases, baseline exit 0 before and after.

### The 11 that were green at `e096053`

| Case | At `e096053` | At `4158b10` |
|---|---|---|
| step-level `PLAYWRIGHT_NO_COPY_PROMPT: ""` (my FINDING 2) | green | **RED** — "also sets … may appear at JOB level and nowhere else" |
| workflow-level `env: DEBUG: pw:api` (FINDING 3) | green | **RED** — "the workflow sets `DEBUG` … refused at every scope" |
| `pree2e` script (FINDING 10) | green | **RED** — "npm runs as part of `npm run e2e`" |
| `poste2e` script (FINDING 10) | green | **RED** |
| `$GITHUB_STEP_SUMMARY` via a shell variable **inside** `run:` (`S="$GITHUB_STEP_SUMMARY"; echo >> "$S"`) | green* | **RED** |
| `$GITHUB_STEP_SUMMARY` via an **`env:` map** (`env: S: ${{ env.GITHUB_STEP_SUMMARY }}`, then `echo >> "$S"`) — at step AND at job level | green | **GREEN** — see R2-FINDING A |
| uploader in a DIFFERENT workflow file, `path: .` | green | green — **named in § Residuals** with bounds; bounds checked below |
| `gh release upload` in `run:` | green | green — stated residual |
| `curl --upload-file` in `run:` | green | green — stated residual |
| `$GITHUB_STEP_SUMMARY` written by a helper script | green | green — **named in § Residuals** |
| stray second Playwright config with `globalSetup` | green | green — **named in § Residuals** as inert; checked below |

\* my e096053 case C3 used the `env:`-map spelling; the in-`run:` shell-variable spelling
is the one the builder closed, and it is closed.

### Checking the four review-only bounds by measurement

- **A second workflow file with an uploader.** `path: .` in `zz-probe.yml` → green, as
  § Residuals says. But the ruling's cross-file clause holds: `path: .vizra-e2e` in a
  second file → **RED**, and `.vizra-e2e/stamp-key.json` buried in a multi-line `path:`
  of a second file → **RED**. So "outside every assertion" is NOT what the bullet
  claims, and it is not the case: the deny sweep crosses files; clauses (a)–(e) do not.
  The bullet says exactly that. Accurate.
- **A stray second config is unselectable.** Read Playwright 1.63.0's own resolution
  (`playwright/lib/common/index.js:1467-1485`, `resolveConfigFile2`): with no `--config`,
  it takes the FIRST of `[".ts", ".js", ".mts", ".mjs", ".cts", ".cjs"]` that exists in
  cwd. `playwright.config.ts` is first, so `playwright.config.mts` / `.js` beside it
  cannot win (my `.mts` and `.js` cases are guard-green and **inert**). There is no
  `package.json` `playwright` key read by `resolveConfigLocation` (it takes only the
  `--config` argument or cwd), so that case is inert too. `--config=…` / `-c` on the lane
  step → **RED** (the step must be exactly `npm run e2e`); `PLAYWRIGHT_CONFIG` → **RED**;
  `PW_TEST_*` → **RED**; `npm_config_*` → **RED**; an `.npmrc` line only becomes an
  `npm_config_*` variable, which Playwright does not read — inert. **The residual is
  accurate.**
- **`run:` exfiltration and helper-script summary writes.** Green as stated.

### F2 — the effective-value logic, attacked

| Case | Guard | Real effect in Actions | Classification |
|---|---|---|---|
| job-level `1` as a YAML **int** | green | Actions stringifies to `"1"`, truthy | **green, harmless** |
| job-level `'1'` single-quoted | green | `"1"` | **green, harmless** |
| job-level `"1 "` (trailing space) | **RED** | truthy — over-strict, safe | red |
| job-level `true` | **RED** | `"true"` truthy — over-strict, safe | red |
| key duplicated in one mapping (`"1"` then `""`) | **RED** (the `yaml` parser rejects the duplicate) | — | red |
| YAML **alias** `*snap` injecting the key at step level | **RED** | — | red |
| YAML **merge key** `<<: *envbase` injecting `PLAYWRIGHT_NO_COPY_PROMPT: ""` at step level | **green** | see note | green — see R2-FINDING B |
| another step writes `PLAYWRIGHT_NO_COPY_PROMPT=` to `$GITHUB_ENV` | **green** | depends on `$GITHUB_ENV` vs job-`env:` precedence | green — see R2-FINDING B |
| NO_COPY_PROMPT at WORKFLOW level instead of job | **RED** | — | red |
| `unset` / `export VAR=` / `env -u` / `VAR= npm run e2e` / `VAR=0 npm run e2e` / `declare -x VAR=` / a sourced file / a computed name | all **RED** | — | red — but NOT for the reason the four greps give: the lane step's `run:` must be EXACTLY `npm run e2e`, so every spelling on the lane step is already refused by that older rule. The four greps matter only on OTHER steps, where an unset does not reach the lane step anyway (each `run:` is its own shell) — except via `$GITHUB_ENV`, which they do not see. |

### Regression — every case that was red at `e096053` is still red

`path:` glob; `index.html` re-added (names the base64 ZIP); `actions/cache`; retention 14;
`include-hidden-files: true`; `scripts.e2e --trace on`; `globalSetup`; reusable workflow;
a second job uploading `.`; `DEBUG` at job and step level; `--config`; `PLAYWRIGHT_CONFIG`;
`PW_TEST_*`; `npm_config_*`. All **RED** by name.

### Re-confirmed after the restart, in a new clone at the same SHA

```
dup key in the job env map                         RED   (the yaml parser rejects the duplicate)
merge key `<<: *envbase` at the lane step          GREEN
$GITHUB_ENV write (echo) on a step before the lane GREEN
$GITHUB_ENV write (printf) on a step before lane   GREEN
unset on a DIFFERENT step (the new grep)           RED   "removes … with `unset`"
export VAR= on a different step                    RED   "… with an empty `export`"
summary via a STEP env map                         GREEN
summary via a JOB env map                          GREEN
restored baseline                                  exit 0
```

`ALLOWED_UPLOAD_PATHS` now has exactly three entries; `e2e-failure-summary/` is gone, with
a comment giving the right reason ("nothing is allowlisted before it exists"). My round-1
FINDING 9(a) is closed.

`grep -c GITHUB_ENV` = **0** in `check-e2e-lane.mjs`, in `AGENTS.md` and in the evidence
README. The guard has no model of that channel at all.

## R2-3. The redactors — 33 shapes through BOTH shipped redactors (after the restart)

Runtime-minted marker. `redact.ts` compiled from the file at this SHA with the repo's own
`typescript`; `redact-artifacts.sh` run as shipped on one file per shape.

| Shape | Claimed? | `redact.ts` | `redact-artifacts.sh` |
|---|---|---|---|
| my round-1 #1 `//host.example:8443/p?q` | yes | redacted | redacted |
| my #2 `[::1]:3000/p?q`, `[2001:db8::1]/p?q` | yes | redacted | redacted |
| my #3 **fully** JSON-escaped `{"u":"https:\/\/host.example\/p?q"}` | yes ("optional backslash-escaped slashes") | redacted | **SURVIVES** |
| AGENTS.md's own example `{"u":"https:\/\/h/p?q"}` (only the scheme slashes escaped) | yes | redacted | redacted |
| realistic `{"u":"https:\/\/host.example\/media\/p.jpg?X-Amz-Signature=…"}` | yes | redacted | **SURVIVES** |
| my #4 `HTTPS://…?q` | yes | redacted | redacted |
| builder's shapes: absolute, `host:3219/…` (PR #3 F13 verbatim), dotted `host:port`, `localhost:3000`, IPv4:port, `//host/p?q`, `/path?q`, `ws://` | yes | all redacted | all redacted |
| uppercase `//HOST.EXAMPLE:8443/p?q` | implied | redacted | redacted |
| userinfo `https://u:pw@host/p?q` | implied | redacted | redacted |
| URL followed by `.` / inside `( )` / `[ ]` / `' '` / followed by `,` | implied | all redacted | all redacted |
| fragment-only secret `https://h/cb#access_token=…`, `/cb#access_token=…`, `host:3000/cb#…` | yes (fragments) | all redacted | all redacted |
| double-escaped `https:\\/\\/h\\/p?q` (JSON inside JSON) | no | survives | survives |
| IPv6 with zone id `[fe80::1%25eth0]:3000/p?q`, `[fe80::1%eth0]/p?q` | "bracketed IPv6" | survives | survives |
| scheme-less userinfo `user@host.example:3000/p?q` | no | survives | survives |
| `%3F` (a path, not a query) | by design | survives | survives |
| secret in a path segment | by design, stated residual | survives | survives |
| undotted host, no port `myhost/p?q` | by design, stated | survives | survives |
| query-less URL; `see step 3/4? yes`; `what? /usr/bin is fine` | must be untouched | **byte-identical** | **byte-identical** |

**The two redactors are NOT the same program for the escaped shape.** The mechanism:

```
redact-artifacts.sh:78   ((?:https?|wss?|ftp):(?:\\?/){2}[^\s"'<>\\)\]]*?)[?\#]…   /gi
redact.ts:67             \b(?:https?|wss?|ftp):(?:\\?\/){2}[^\s'"<>()[\]]+          /gi
```

Both accept `\/\/` after the scheme. But the shell's host/path class **excludes backslash**
(`\\`), so it stops at the first `\/` in the PATH and then needs `?` or `#` immediately —
which is not there — and the whole match fails. `redact.ts`'s class allows backslash. The
test that pins this shape (`e2e/harness/redact.test.ts:188`) uses
`'{"u":"https:\\/\\/host/p?sig=' + M + '"}'` — escaped scheme slashes, **unescaped path
slash** — the one spelling where the two agree. A serializer that escapes `/` escapes every
`/` (PHP's `json_encode` default; Go's and JS's encoders do not escape `/` at all), so the
pinned spelling is not one any serializer produces, and the realistic one survives the
redactor that touches UPLOADED bytes. → R2-FINDING C.

**ReDoS — none found.** `redact.ts` on eight pathological 1 MB single-line inputs
(repeated `a.`, a 1 MB label then `:1/?`, `/a` with no `?`, `[:`, `https:\/`, `//a:1`,
`a-`, and 12 000 realistic URLs in JSON): **19–35 ms** each. The shell redactor
(all five perl passes, whole script) on nine such 1 MB lines: **0.16–1.13 s** each, all
exit 0. Linear enough; not a finding.

## R2-4. `check-source-hygiene.mjs` (after the restart)

**Baseline:** `OK: 274 text source(s) carry no literal control bytes, and 13
mutation-digest line(s) match this tree.` — matches the claim.

**Is it in a REQUIRED lane? Yes.** `package.json` `ci` is now
`npm run check:hygiene && npm run lint && npm run typecheck && npm run test && npm run build`,
and `frontend-ci.yml` (required, NOT path-filtered) runs `npm run ci`. `ci-guard`
(optional, path-filtered) additionally runs its unit cases via `require-checks_test.sh`.

**Planted into a TRACKED `.ts`, `.mjs` and `.sh`** (`redact.ts`, `check-e2e-lane.mjs`,
`redact-artifacts.sh`), one at a time, restored between, `git status` clean after:

| Byte | `.ts` | `.mjs` | `.sh` |
|---|---|---|---|
| NUL 0x00 | **RED** by name, with count | **RED** | **RED** |
| BEL 0x07 | **RED** | **RED** | **RED** |
| ESC 0x1B | **RED** | **RED** | **RED** |
| VT 0x0B | **RED** | **RED** | **RED** |
| DEL 0x7F | **RED** | **RED** | **RED** |
| lone CR 0x0D (not part of CRLF) | green | green | green |
| UTF-8 BOM prefix | green | green | green |
| U+2028 LINE SEPARATOR | green | green | green |

CR is allowed on purpose (tab/LF/CR are the script's stated exceptions), and BOM / U+2028
are not C0 bytes, so these three are inside the script's stated scope — recorded, not
findings. (A lone CR is the same "rewrite the terminal line" class the sanitiser exists
to stop in page text; a NIT at most.)

**The ledger half:**

| Mutation | Result |
|---|---|
| one digest changed by one hex character | **RED** — names the label, both digests, the file |
| a byte-pinned file (`worker-guard.ts`) edited, ledger left stale | **RED** — names the label and both digests |
| the ledger FILE deleted | **RED** ("is missing") |
| the ledger's first LINE deleted | **green** — "12 mutation-digest line(s) match" |
| the ledger EMPTIED (0 bytes) | **green** — "**0** mutation-digest line(s) match this tree" |

The script carries its own vacuity guard —
`if (ledgerLines.length > 0 && checked === 0) add("… it would have passed vacuously.")` —
and it does not fire for an empty file, because `ledgerLines.length` is 0. So the check
refuses a ledger that CONTRADICTS the tree but accepts one that has stopped describing
it, and the cheapest way to turn its red back to green after editing a pinned file is to
delete that file's ledger lines. The README's "verifies every `BEFORE`/`RESTORED` digest
against the file at the current revision" is true of the lines present. → R2-FINDING D.

## R2-5. End-to-end survivor scan on a red Lane-A run (after the restart)

Same method as §1, with probe files rebuilt from scratch (the originals were lost in the
restart): localhost-only fixture server, markers from `crypto.randomBytes`, the SHIPPED
config, `PLAYWRIGHT_NO_COPY_PROMPT=1`, lane exit 1 as intended. One marker added this
round — `escsigned`: the spec prints a signed-URL-shaped string whose slashes are
backslash-escaped (what a slash-escaping JSON serializer emits), to test whether
R2-FINDING C is reachable through the real lane.

**Positive control:** all seven markers found before redaction, including inside
`index.html::base64` and `playwright-report/data/*.zip`.

Shipped `redact-artifacts.sh test-results playwright-report` → `OK … 23 file(s) and 2
archive(s)`, exit 0. Then **only the upload set** (`test-results/`,
`playwright-report/results.json`):

| Marker | Survives the upload set? | Where |
|---|---|---|
| scheme-less signed URL (`page.goto`) | **no** | — |
| **slash-escaped signed URL printed by the spec** | **YES** | `playwright-report/results.json`, `trace.zip::test.trace` |
| `page.fill` value | YES | `trace.zip::1-trace.trace`, `::test.trace` |
| assertion's received value | YES | `error-context.md`, `trace.zip::attachments/…`, `::test.trace`, `results.json` |
| page console text | YES | `error-context.md`, `trace.zip::1-trace.trace`, `::attachments/…`, `::resources/….html`, `::test.trace`, `results.json` |
| page `<title>` | YES | `trace.zip::1-trace.trace`, `::resources/….html` |
| plain stdout token | YES | `trace.zip::test.trace`, `results.json` |

The surviving bytes, marker masked, from the two UPLOADED files:

```
results.json          "text": "{\"u\":\"https:\\/\\/host.example\\/media\\/p.jpg?X-Amz-Signature=<MARKER>
trace.zip::test.trace "text":"{\"u\":\"https:\\/\\/host.example\\/media\\/p.jpg?X-Amz-Signature=<MARKER>
```

Playwright JSON-encodes captured text, so a URL printed with `\/` lands on disk as
`\\/` — the double-escaped shape that NEITHER redactor handles (R2-3). **R2-FINDING C
is therefore reachable, not hypothetical**: any slash-escaped URL a spec or page prints
reaches two uploaded files with its query intact. Reachability today is low — no spec
authenticates, and vizra-core's Go `encoding/json` does not escape `/` — but PHP's
`json_encode` does by default, and the charter includes Chevereto (PHP) import and
federation with other instances' content.

`playwright-report/index.html` and `playwright-report/data/*.zip` still carry every
marker and are still **not** uploaded — FINDING 3's fix holds.

`error-context.md` sections: `# Instructions`, `# Test info`, `# Error details` — **no
`# Page snapshot`** (F10 holds) and, again, **no `# Test source`** (see R2-8).

**Does AGENTS.md's new "WHAT A RED LANE A ACTUALLY PUBLISHES" table say exactly this?**
Very nearly, and far better than before: it names `results.json` (with the assertion's
received value and captured stdout/stderr), says `trace.zip` carries headers, bodies, DOM
snapshots, console text and `fill()` values with "URLs only" redacted, says the page
snapshot is suppressed, and says `playwright-report/` is not uploaded. Two gaps: its
"Redacted? — URLs only" cell for `results.json` and `trace.zip` is not true of
slash-escaped URLs (R2-FINDING C), and it still lists a `# Test source` section that
has not appeared in any of my four red runs across both rounds (over-description in the
safe direction; not a finding).

## R2-6. CI on `4158b10` (read with `gh`, after the restart)

All **9** check-runs `completed` / `success`: `frontend`, `contract`, `guard`,
`docker-build`, `e2e`, `deps-scan`, `image-scan`, `GitGuardian Security Checks`, and
`ci-required` — which finished **last** (10:26:39Z, after `e2e` at 10:26:22Z).

`.github/required-checks.txt` at the head has git blob `f2f23454…`, **identical** to
main's — unchanged. It declares `frontend`, `contract`, `?guard`, `?docker-build`, `e2e`;
all five ran and succeeded (`docker-build` ran this time because `package.json` changed,
which is in its path filter). Manifest matches the jobs that ran; nothing skipped,
cancelled or timed out.

`e2e` run `35588546930` (attempt 1, success) log: `18 passed (12.6s)`,
`e2e coverage floor: OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9)`,
`e2e harness stamp: OK (18 succeeding result(s) verified)`,
`PLAYWRIGHT_NO_COPY_PROMPT: 1` in every step's env, and
`OK: the harness canary failed all 4 fault-injection fixtures, each with the exact set of
record kinds it demonstrates and no others`. Artifacts on the run: **0** — correct for a
green run. **There is still no RED run on any SHA of this PR**, so the uploaded set has
never been observed in GitHub; R2-5 is my local reproduction of it.

## R2-7. Regression sweep of what I confirmed at `e096053` (after the restart)

| Item | At `4158b10` |
|---|---|
| `index.html` not uploaded, and re-adding it refused | holds — K2 RED naming the base64 ZIP; R2-5 shows it still carries every marker and is not in the upload set |
| F10 red/green: `# Page snapshot` absent with `PLAYWRIGHT_NO_COPY_PROMPT=1` | holds (R2-5); the job env still sets it, and the CI log shows it in every step |
| sanitiser on a live lane | holds — plus round-1 FINDING 5 is **closed**: `"  ::"`, `"\t::"`, NBSP-`::` and U+3000-`::` are all broken with U+200B; `"Foo::bar"` mid-line untouched; CR/LF → `⏎`; `%0A` → `%250A`; 300 chars → capped |
| tokenising call check vs the three old defeats | holds — trailing comment RED `absent`, string RED `absent`, `void f()` RED `void-discarded`, shadowed RED `shadowed`; `const _ = f()` and `if (false) f()` GREEN, the stated review-only class |
| `globalSetup` refusal | holds (K7 RED) |
| tripwire `no-credentials-in-specs.test.ts` | 10/10 passed |
| no spec or demo changed in round 2 | `git diff --name-only e096053..4158b10 -- e2e/specs e2e/demos` is empty |
| no credential-shaped literal in the 7 commits | 0 hits (`ghp_`, `github_pat_`, `gh[ousr]_`, `AKIA`/`ASIA`, PEM, JWT, Slack, `sk-`, Google API key), and no long `X-Amz-Signature=` value; GitGuardian `success` |
| e2e 18 passed, floor 9/9 9/9, 18 stamps, canary 4/4 | holds in CI on this SHA (R2-6); my local run is in R2-10 |

**`.npmrc`** — the guard now reads it. `script-shell=…` and `ignore-scripts=true` →
**RED** by name, as the PR body says. `playwright_trace=on` → green and inert
(Playwright does not read `npm_config_*`). **`node-options=--require ./x.js` → green** —
examined in R2-FINDING E.

## R2-8. `npm run ci` at every one of the seven new commits (after the restart)

A separate clone; for each commit `git checkout --force`, `git clean -fdx -e node_modules`,
`rm -rf node_modules/.vite node_modules/.cache` (cold), then `npm run ci`. No lockfile
change in round 2, so `node_modules` was reused. **The machine was NOT quiet:** load
averages 58–75 from other work on this host throughout (only this one run of mine was
active).

| Commit | Exit | Files | Tests | Notes |
|---|---|---|---|---|
| `bcc3bb4` | 0 | 16 | 409 | no hygiene check yet |
| `1647f19` | 0 | 16 | 423 | no hygiene check yet |
| `d818527` | **1** | 1 failed \| 15 passed | 1 failed \| 422 passed | `browser-errors.test.ts > … applies the guarded-import rule to every one of them — Test timed out in 5000ms`; hygiene OK (274 / 13) |
| `2bb8cb7` | 0 | 16 | 423 | the shared-ESLint commit |
| `b0a9adb` | 0 | 16 | 423 | |
| `cf3753a` | 0 | 16 | 423 | **declared red by the builder; green in my run** |
| `4158b10` | 0 | 16 | 423 | the timeout commit |

0 skipped everywhere. Lint at every commit, head included: **1 warning** —
`e2e/harness/redact.ts:156:5 Unused eslint-disable directive (no problems were reported
from 'no-control-regex')`, the leftover I reported at `e096053`; still there (NIT).

**The truth per commit:** every commit before `4158b10` carries the same timing flake,
and whether it shows is a matter of load — the builder saw it at `cf3753a`, I saw it at
`d818527`. The honest statement is "`4158b10` is the first commit that is not flaky under
load", not "green at every boundary except `cf3753a`". The PR body's "Counts, honestly"
section says round 2 is "**green at all five new commit boundaries**" — there are
**seven**, and the same body's own "Two things I got wrong" section says `cf3753a` was
pushed with `npm run ci` exit 1. The retraction is plain and honest; the counts sentence
above it was not updated to match it. No evidence file in the tree claims green at every
boundary (`grep -rn "every commit\|all five\|cf3753a\|green at all"` over `docs/` and
`AGENTS.md`: no hits). → part of R2-FINDING F.

## R2-9. The ESLint flake at `4158b10` (after the restart)

A true "quiet" condition was not available: other work on this host held the 1-minute
load average between 34 and 100 before I added anything. So: 10 cold runs at that
**ambient** load, then 10 cold runs with **eight additional `yes > /dev/null` busy
loops** of mine (killed by exact PID afterwards; `pgrep -x yes` = 0). Cold = `git clean
-fdx -e node_modules` and `rm -rf node_modules/.vite node_modules/.cache` before each run.

| Condition | Runs | Exit 0 | Tests | Timeouts | 1-min load average | Wall time |
|---|---|---|---|---|---|---|
| ambient | 10 | **10** | 423/423 each | **0** | 34 – 100 | 38 – 85 s |
| ambient + 8 busy loops | 10 | **10** | 423/423 each | **0** | 49 – 242 | 77 – 192 s |

**20/20 green, zero timeouts,** at a far heavier load than either the builder's 46 or the
condition that produced my round-1 observation.

**Is 30 s hiding a hang?** Five further cold runs of `browser-errors.test.ts` alone
(`--reporter=json`) with the eight busy loops, load ~145–153:

```
max ms   min ms   case
 10764     7853   applies the guarded-import rule to every one of them   <- builds the shared ESLint, lints every spec
   291       47   … overriding `page`, `context` or `browser` stays legal
   258       39   e2e/harness stays exempt
   (every other case under 0.3 s; all 265 case-results passed)
```

No. The one slow case is the one that constructs the shared instance and lints every
spec; its time is real and bounded (8–11 s at load ~150), and every other ESLint case
reuses the instance and takes under 0.3 s. A hang would still exceed 30 s and fail. The
timeout is scoped to the nine ESLint cases, as claimed. One précising note: my worst
case gives the 30 s ceiling **2.8×** headroom, not the builder's "≈4× the worst
cold-contended run observed" — at a load average ~3× theirs. Not a finding.

**The builder's two declared process failures, weighed.** (1) Publishing "the mechanism is
removed" on ten quiet runs, then retracting it within the hour: the retraction is in
`4158b10`'s own commit message ("RETRACTION. … That claim was FALSE") and in the PR body,
not amended away — handled correctly, and the final fix measures well above the load it
was tested at. (2) Pushing `cf3753a` with `npm run ci` exit 1: declared plainly in the PR
body; the only defect is the stale counts sentence (R2-8, R2-FINDING F).

## R2-10. F2's control, switched off by one line in a file the guard now reads (after the restart)

The guard now parses the committed `.npmrc` and refuses `script-shell` and
`ignore-scripts` "because [they change] how every `npm run` in this lane is executed",
and it refuses `NODE_OPTIONS` in the workflow/job/step env at every scope. It does not
refuse the `.npmrc` key that becomes `NODE_OPTIONS` for every `npm run` script:
`node-options`.

**One committed line, no other file:**

```
.npmrc:  node-options=--import=data:text/javascript,process.env.PLAYWRIGHT_NO_COPY_PROMPT=%22%22

bash scripts/ci/check-e2e-lane.sh                                     -> exit 0
node scripts/ci/check-source-hygiene.mjs                              -> exit 0
inside a process npm starts:  NODE_OPTIONS="--import=data:…"  PLAYWRIGHT_NO_COPY_PROMPT=""
```

**End to end, the exact lane script, with `PLAYWRIGHT_NO_COPY_PROMPT=1` in the
environment exactly as the `e2e` job sets it** (probe spec, localhost fixture server,
runtime marker; filtered to one spec for speed — the injection does not depend on the
filter):

```
with the .npmrc line:   error-context.md sections: # Instructions  # Test info  # Error details  # Page snapshot
                        - textbox [active] [ref=f1e2]: <TYPED-MARKER>         (typed marker: 1 occurrence)
control, no .npmrc:     error-context.md sections: # Instructions  # Test info  # Error details
                        (typed marker: 0 occurrences)
```

A two-file variant (`node-options=--require ./zz-preload.cjs` + a two-line preload) gives
the same result, also guard-green and hygiene-green. Sandbox restored and `git status`
clean after each.

What is written about it: the guard's source comment says "The FILE half is checked only
for this one key, because a committed `.npmrc` is a reviewed file and enumerating
everything npm reads from it is a different job" — a disclosure, in a source comment. But
the same file's F2 block says the new rule "**has no shape where the guard is green and
the variable is not "1"**", the PR body says "the **effective value** is computed",
`AGENTS.md` still says "`check-e2e-lane.mjs` asserts it is set", and `AGENTS.md` does not
mention `.npmrc` or `node-options` anywhere (`grep -ci` = 0). → R2-FINDING E.

## R2-11. Lanes at `4158b10`, run by me (after the restart)

| Lane | Result |
|---|---|
| `npm run ci` | exit 0 — 16 files / 423 tests / 0 skipped (plus 20 more cold runs in R2-9, all exit 0) |
| `bash scripts/ci/require-checks_test.sh` | exit 0 — **164 cases, 171 assertions, 0 failed** (matches the claim) |
| `bash scripts/ci/check-e2e-lane.sh` | exit 0 |
| `bash scripts/ci/check-required-floor.sh` | exit 0 |
| `bash scripts/ci/check-image-pins.sh` | exit 0 |
| `npm run check:contract` | exit 0 |
| `node scripts/ci/check-source-hygiene.mjs` | exit 0 — 274 sources, 13 ledger lines (the PR body says 273; stale by one — NIT) |
| `npx playwright test` (production build, `PLAYWRIGHT_NO_COPY_PROMPT=1`) | exit 0 — **18 passed**, floor OK (9/9 9/9), **18 stamps** |
| `node scripts/ci/harness-canary.mjs` | exit 0 — failed all 4 fault-injection fixtures, each for its own kind |
| credential tripwire | 10/10 |

## R2-12. `npm run e2e:demos` at `4158b10` (after the restart)

Two full runs in a dedicated clone, production build per the script's own instruction,
tree reset (`git checkout -- . && git clean -fd`) before the second, **nothing else of mine
running and nothing edited during either run**. The host was NOT quiet: other work held
the load averages high throughout.

| Run | Load (1, 5, 15) at start → end | Passed | Blocked | Failed | Exit |
|---|---|---|---|---|---|
| 1 | 43.8 86.6 114.6 → 62.5 92.4 103.0 | 122 | 0 | 1 | **1** |
| 2 | 35.6 81.8 98.6 → 40.0 75.8 112.7 | 121 | 0 | 2 | **1** |

The failing halves:

- **`d14-late-fault-600ms-is-the-LIMIT-GREEN` — failed in BOTH runs.** This GREEN half
  demonstrates a *documented limit*: a fault fired 600 ms after the test body returns is
  MISSED, so the test passes. Under load the worker is slower to tear down, the fault
  lands while the worker guard is still listening, and the late-edge orphan assertion
  catches it: `1 browser signal(s) were produced AFTER THE LAST TEST in this worker
  finished … [pageerror] … late fault demonstration (D14)` → exit 1. The builder's
  committed transcript for the same half ends `1 passed … [exit 0]`. So the guard caught
  MORE than its documented limit — the safe direction — and the demonstration of the limit
  is timing-dependent.
- **`d11f-in-process-reporter-deleted-GREEN` — run 2 only.** A product spec inside the
  half (`home`, mobile-chromium-390) hit `TimeoutError: locator.click: Timeout 10000ms
  exceeded` under load: `1 failed | 19 passed`. Load-induced; nothing to do with the
  control the half demonstrates.

Neither failure is infrastructure in the new script's sense — the production server was
answering, so the liveness discriminator correctly did not call them BLOCKED — and neither
indicates a weaker control. But **I could not reproduce the claimed 123 / 0 / 0.** The
builder ran at load average 46 and calls that "the exact condition that produced the
verifier's misclassification"; at the loads this host carried today (5-minute averages
76–92), the suite fails two timing-dependent halves and reports "a demonstration did not
demonstrate". → R2-FINDING G.

Not measured: whether a TRANSIENT server stall (down, then back before the post-failure
liveness probe runs) is classified BLOCKED. By reading `demonstrate.sh:254-262`, the probe
runs once, after the half has failed; a server that has already recovered is "alive", so
such a half would be FAIL, not BLOCKED — which was the shape of my round-1 run, where later
halves passed. Stated as a reading, not a measurement.

Also still open from round 1: **no committed F10 red/green demonstration** (my round-1
FINDING 9(b); `grep -n NO_COPY_PROMPT scripts/e2e/demonstrate.sh` → nothing). The PR body
does not claim it was added.

## Status of my round-1 findings at `4158b10`

| # | Round-1 finding | At `4158b10` |
|---|---|---|
| 1 | demos: infrastructure reported as a failed demonstration | **partly closed** — a liveness probe now yields BLOCKED (exit 2) for a server that stays down; load-induced timing failures are still reported as failed demonstrations (R2-FINDING G) |
| 2 | step-level `PLAYWRIGHT_NO_COPY_PROMPT: ""` (BLOCKER) | **closed for every env-map shape I tried** (step, workflow, alias, duplicate, `"1 "`, `true`); **re-opened by a different route**: one `.npmrc` line (R2-FINDING E) |
| 3 | workflow-level `env:` unread | **closed** |
| 4 | five URL shapes named as covered and not | **closed for those five shapes**; a sixth (fully escaped JSON) and a divergence between the two redactors remain (R2-FINDING C) |
| 5 | leading-whitespace `::` | **closed** |
| 6 | no control-byte check, ledger never read back | **closed** for control bytes and for contradicting digests; an emptied or trimmed ledger still passes (R2-FINDING D) |
| 7 | ledger ordering; "409 at every boundary" false; ESLint flake | **closed** — README note; body corrected for round 1; flake fixed and holds at load 242 (R2-9). Round 2's own counts sentence is stale (R2-FINDING F) |
| 8 | NOT-covered table never named `results.json` | **closed** — the new file-by-file table is accurate apart from R2-FINDING C |
| 9 | (a) `e2e-failure-summary/` allowlisted; (b) no F10 demo pair | (a) **closed**; (b) **open**, not claimed |
| 10 | `pree2e`/`poste2e` | **closed** |
| 11 | other workflow files | **closed** — named in § Residuals with bounds, and the bounds are accurate |

## Findings at `4158b10`

```
R2-FINDING E: F2's control is switched off by ONE line in the committed `.npmrc` —
              a file the guard now parses — and the guard stays green
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-e2e-lane.mjs:1046-1062 (the `.npmrc` loop refuses only
             `script-shell` and `ignore-scripts`), :1090 (REFUSED_ENV has NODE_OPTIONS,
             env maps only), and the F2 block's claim that the rule "has no shape where
             the guard is green and the variable is not "1""
             AGENTS.md ("`check-e2e-lane.mjs` asserts it is set"; no mention of `.npmrc`)
  requirements: VZ-FOUND-008

Observed:
  Committed `.npmrc`, one line, no other file:
      node-options=--import=data:text/javascript,process.env.PLAYWRIGHT_NO_COPY_PROMPT=%22%22

      bash scripts/ci/check-e2e-lane.sh          -> exit 0
      node scripts/ci/check-source-hygiene.mjs   -> exit 0
      inside any process `npm run` starts:  NODE_OPTIONS="--import=data:…"  PLAYWRIGHT_NO_COPY_PROMPT=""

  End to end, `npm run e2e` (the exact lane script) with PLAYWRIGHT_NO_COPY_PROMPT=1 in
  the environment exactly as the e2e job sets it, on a failing probe spec:
      with the line:   error-context.md has "# Page snapshot" and
                       "- textbox [active] [ref=f1e2]: <TYPED-MARKER>"
      without it:      no "# Page snapshot", typed marker absent
  A two-file variant (`node-options=--require ./preload.cjs`) behaves identically.

Failure:
  This is round-1 FINDING 2's outcome — the page snapshot restored, a `fill()` value
  verbatim in an uploaded file, the guard green — reached through a different door. The
  fix computes the value the YAML DECLARES, not the value the Playwright process SEES.
  The guard already knows both halves of this attack: it refuses `NODE_OPTIONS` in every
  env map, and it reads `.npmrc` to refuse keys that "change how every `npm run` in this
  lane is executed". `node-options` is exactly such a key and is what npm turns into
  NODE_OPTIONS. The source comment says other `.npmrc` keys are not enumerated; but the
  same file says the rule has "no shape where the guard is green and the variable is not
  "1"", the PR body says "the effective value is computed", and AGENTS.md says nothing
  about `.npmrc` at all.

Perspective: developer, then member

Recommendation:
  1. Refuse `node-options` in the committed `.npmrc` (same loop, one more key). Better:
     refuse ANY key in a committed `.npmrc` that is not on a short allowlist — the repo
     has no `.npmrc` today, so an allowlist of zero keys costs nothing and is default-deny,
     which is how every other part of this guard now works.
  2. Correct the F2 block's "no shape where the guard is green" sentence to say what is
     computed: the declared value across the three YAML scopes.
  3. Consider asserting the variable where it takes effect: the harness itself can refuse
     to start in CI (`process.env.CI`) unless PLAYWRIGHT_NO_COPY_PROMPT is truthy in the
     worker. That is the only check that sees the value Playwright reads, whatever route
     changed it — and it is one line in a file the stamp already guards.

Acceptance criteria:
  require-checks_test.sh: `.npmrc` `node-options=…` RED by name; any unlisted `.npmrc`
  key RED (if the allowlist route is chosen). If (3) is done: a demonstration half in
  which `.npmrc` blanks the variable and the lane FAILS by name.

Tests: scripts/ci/require-checks_test.sh (+ one demonstrate.sh half if (3)).
Cross-repo implications: core: none | user: as above | search: none | meta: none
Challenge:
  "A committed `.npmrc` is a reviewed file." So is `e2e.yml`, where the same outcome
  was ruled a blocker one round ago; and the line above does not read like a privacy
  change to a reviewer who does not know what `node-options` does.
```

```
R2-FINDING C: the shell redactor — the one that touches uploaded bytes — does not
              redact a fully slash-escaped URL, though AGENTS.md says both redactors
              carry the same programs; and the real lane produces that shape
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/redact-artifacts.sh:78 (host/path class excludes backslash)
             e2e/harness/redact.ts:67 (does not) ; e2e/harness/redact.test.ts:188 (pins
             the one half-escaped spelling where the two agree)
             AGENTS.md "Covered" table (absolute: "with optional backslash-escaped slashes";
             "Both redactors carry the same four programs")
  requirements: VZ-FOUND-008

Observed:
  {"u":"https:\/\/h/p?sig=M"}                        both redact (AGENTS.md's example, the pinned test)
  {"u":"https:\/\/h\/p?sig=M"}                       redact.ts redacts; redact-artifacts.sh: SURVIVES
  {"u":"https:\/\/host.example\/media\/p.jpg?X-Amz-Signature=M"}   same
  "https:\\/\\/h\\/p?sig=M" (double-escaped)         both: SURVIVE
  Through the real lane (R2-5): a spec that prints a slash-escaped URL -> Playwright
  JSON-encodes it -> the double-escaped form, with the query intact, in
  playwright-report/results.json AND trace.zip::test.trace — both uploaded — after the
  shipped redactor reported OK.
Failure:
  The table's claim is broader than the shell program, the two redactors are not the
  same program, and the test pins the one spelling no slash-escaping serializer emits.
  Same class as round-1 FINDING 4. Reachability today is low (no spec authenticates; Go
  and JS encoders do not escape "/"), but PHP's json_encode does, and Chevereto import is
  in the charter.
Recommendation:
  Allow `\\` in the shell's host/path class as redact.ts does, and accept one or two
  backslashes before each `/`; pin the fully-escaped and double-escaped forms in
  redact.test.ts AND in a require-checks case that runs the SHIPPED shell script; or
  narrow the table to "escaped scheme slashes only". Also: the table says "bracketed IPv6"
  and `[fe80::1%25eth0]:3000/p?q` (a zone id) survives both — name it or cover it.
Acceptance criteria: the fully-escaped and double-escaped forms redact through the
  shipped shell script, asserted by a test that runs that script.
Tests: e2e/harness/redact.test.ts, scripts/ci/require-checks_test.sh.
Cross-repo: core: none | user: as above | search: none | meta: none
Challenge: "Nothing emits `\/` today." The lane emits `\\/` the moment anything prints
  `\/`, and the section's own rule is "do not widen this claim again without a
  measurement".
```

```
R2-FINDING A: `$GITHUB_STEP_SUMMARY` through an `env:` map is green, and § Residuals
              says the indirect form is refused
Severity:    SHOULD
Confidence:  high
Affected: vizra-user; scripts/ci/check-e2e-lane.mjs (the refusal greps `run:` text only);
  AGENTS.md § Residuals, "A `run:` step that writes through a HELPER SCRIPT is not seen"
Observed:
  `env: { S: ${{ env.GITHUB_STEP_SUMMARY }} }` at step or job level, then
  `run: echo hi >> "$S"`  -> guard exit 0.
  `S="$GITHUB_STEP_SUMMARY"; echo >> "$S"` inside `run:` -> RED (the builder's case).
  The bullet says: "writing the summary from an inline command — even indirectly, via a
  shell variable — is refused". The env-map spelling is an inline command writing via a
  shell variable, and it is not refused.
Recommendation: also scan env-map VALUES in the e2e job for `GITHUB_STEP_SUMMARY`, or
  narrow the sentence to "a shell variable assigned inside the same `run:`".
Acceptance: a require-checks case for the env-map spelling, or the narrowed sentence.
Challenge: "It is the run: class." Then the sentence should not say it is refused.
```

```
R2-FINDING B: `$GITHUB_ENV` — the one `run:` channel that crosses into the lane step —
              is not modelled or named; the four unset greps sit on channels that cannot
Severity:    SHOULD
Confidence:  high (guard behaviour); medium (Actions precedence for the same key)
Affected: vizra-user; scripts/ci/check-e2e-lane.mjs (`grep -c GITHUB_ENV` = 0);
  AGENTS.md (0), the evidence README (0)
Observed:
  - `echo "PLAYWRIGHT_NO_COPY_PROMPT=" >> "$GITHUB_ENV"` on an earlier step -> exit 0.
    Whether this overrides the JOB-level `env:` value for later steps depends on Actions'
    precedence, which I did not measure (I cannot run Actions from here).
  - `echo 'NODE_OPTIONS=--import=data:…PLAYWRIGHT_NO_COPY_PROMPT=%22%22' >> "$GITHUB_ENV"`
    on an earlier step -> exit 0. No precedence question here — NODE_OPTIONS is refused in
    every env map, so nothing competes with it — and R2-FINDING E shows what that value
    does inside the lane.
  - The four new unset greps (`unset`, empty `export`, `env -u`, `VAR= cmd`) fire on
    OTHER steps (verified). But every `run:` is its own shell, so an unset on another step
    cannot reach the lane step; and on the lane step every spelling is already refused by
    the older "the lane's `run` must be exactly `npm run e2e`" rule.
  - YAML merge key `<<: *anchor` injecting `PLAYWRIGHT_NO_COPY_PROMPT: ""` at step level
    -> exit 0. The guard's `yaml` parser does not expand merge keys; whether Actions does,
    I did not measure.
Failure: this is inside the stated `run:` class, so not a blocker — but the four greps are
  presented as early warnings for the unset route, and the route that actually works is
  the one they do not see.
Recommendation: refuse `GITHUB_ENV` writes that name PLAYWRIGHT_*, NODE_OPTIONS, DEBUG or
  PWDEBUG in any e2e-job `run:` (same grep style); refuse `<<` in env maps (or measure);
  name `$GITHUB_ENV` in § Residuals.
Acceptance: require-checks cases for the three spellings, or a residual bullet naming them.
```

```
R2-FINDING D: the digest-ledger check passes an EMPTIED or TRIMMED ledger, and its own
              vacuity guard does not fire
Severity:    SHOULD
Confidence:  high
Affected: vizra-user; scripts/ci/check-source-hygiene.mjs:158-160; README "verifies every
  BEFORE/RESTORED digest"; PR body "Refuses to pass vacuously"
Observed: one digest altered -> RED; pinned file edited, ledger stale -> RED; ledger file
  deleted -> RED; first line deleted -> green ("12 … match"); file emptied -> green
  ("0 mutation-digest line(s) match this tree"). The guard is
  `if (ledgerLines.length > 0 && checked === 0)`, which an empty file skips.
Failure: the cheapest way to clear a stale-ledger red is to delete the stale lines; and
  "refuses to pass vacuously" is false for the most vacuous input there is.
Recommendation: fail on `checked === 0` unconditionally, and pin the expected set of
  labels (or a minimum count) so a trimmed ledger is red.
Acceptance: empty ledger RED; a deleted line RED.
Tests: require-checks_test.sh, two cases.
```

```
R2-FINDING G: `e2e:demos` does not reproduce 123/0/0 on a loaded host; the D14 LIMIT
              half is timing-dependent and fails 2 of 2 runs
Severity:    SHOULD
Confidence:  high
Affected: vizra-user; scripts/e2e/demonstrate.sh:1625 (d14 LIMIT half), e2e/demos/late-fault.demo.ts
Observed: two clean runs at 5-minute load averages 76–92: 122/0/1 and 121/0/2, exit 1 both.
  `d14-late-fault-600ms-is-the-LIMIT-GREEN` failed both times — the late-edge assertion
  CAUGHT the 600 ms fault it is documented to miss; `d11f` failed once on a product-spec
  `locator.click: Timeout 10000ms` inside the half.
Failure: both in the fail-closed direction; neither weakens a control. But the PR body
  presents load 46 as proof of robustness to "the exact condition" of my round-1 run, and
  at the loads this host carried, the suite reports "a demonstration did not demonstrate"
  for timing reasons again.
Recommendation: make the LIMIT half assert what is invariant (the fault is either missed,
  or caught only as an ORPHAN — never charged to the test) or give it a margin that holds
  under load, and say in the README that the documented limit is a fast-machine number.
Acceptance: two consecutive runs exit 0 at a load average above 80, or the half rewritten
  so its outcome does not depend on teardown speed.
```

```
R2-FINDING F: the PR body's round-2 counts sentence is stale
Severity:    NIT
Confidence:  high
Observed: "green at all five new commit boundaries" — there are seven, the same body's
  "Two things I got wrong" says cf3753a was pushed with exit 1, and under load I measured
  d818527 red (cf3753a was green for me): every pre-4158b10 commit carries the flake.
  Also: hygiene "273 sources" (I measure 274); the round-1 lint warning at
  redact.ts:156 (unused eslint-disable) is still present at every commit; the new
  file-by-file table lists a `# Test source` section no red run of mine has produced.
Recommendation: say "4158b10 is the first commit that is not flaky under load; every
  earlier one may go red on the ESLint timeout, and cf3753a did". Fix the lint warning.
```

## Verdict at `4158b10`

A substantial round. Of my eleven round-1 findings, six are fully closed, two are closed
for every shape they named (2 and 4), and three are partly closed (1, 6, 9) — each
verified by measurement, not by reading: the effective-value
rule survives every YAML env-map attack I built (step, workflow, alias, duplicate key,
`"1 "`, `true`); workflow-level `env:` and the npm lifecycle hooks are refused; the five
URL shapes redact in both redactors and nothing regressed; the sanitiser handles every
leading-whitespace `::`; the new hygiene check is in the required `frontend` lane and
refuses every C0 byte I planted in `.ts`, `.mjs` and `.sh`; the ESLint flake is fixed and
held through 20 cold runs at load averages up to 242, with the one slow case measured at
8–11 s, not hung; the file-by-file publication table is honest; the four review-only
bounds in § Residuals are accurate — I checked Playwright's own config resolution order
to confirm a stray config is inert; the two declared process failures are disclosed
plainly and not amended away. CI is green on this SHA (9/9, `ci-required` last, manifest
unchanged and matched). No redactor has a ReDoS path on 1 MB inputs. No credential-shaped
literal was added, and no spec was touched.

I am returning **FAIL** on one blocker, which is round-1 FINDING 2 again, through a
different door. **R2-FINDING E:** one committed `.npmrc` line
(`node-options=--import=data:…`) empties `PLAYWRIGHT_NO_COPY_PROMPT` inside every process
`npm run` starts. Both the lane guard and the hygiene check stay green, and on a red lane
`# Page snapshot` comes back with a `fill()` value verbatim — I drove that end to end with
the variable set exactly as CI sets it. The guard already refuses `NODE_OPTIONS` in every
env map and already reads `.npmrc` for keys that change how `npm run` executes; it misses
the key that is literally `NODE_OPTIONS`. The file also claims the rule "has no shape
where the guard is green and the variable is not '1'". I held round 1 to this standard
and I hold round 2 to it: the published sentence is stronger than the control.

**R2-FINDING C** (required) is round-1 FINDING 4's class again: the two redactors are not
the same program on a fully slash-escaped URL, and the real lane puts such a URL,
double-escaped with its query intact, into `results.json` and `trace.zip` after the
shipped redactor reports OK. FINDINGS A, B, D and G are should-fix; F is a nit.

Nothing I found is a live disclosure: nothing authenticates, the hard rule stands and is
asserted, the tripwire passes 10/10, and no red CI run has ever uploaded anything for this
PR.

FAIL is not a judgement on the quality of this round, which is high. It is that the
headline privacy control can still be switched off without the guard noticing, and that
is the one thing this area is not allowed to ship.

FINAL VERDICT: FAIL — SHA 4158b10f8291e23cd726e2499db760aead195f4a

---
---

# Re-verification at `11f8975` (2026-09-23) — fix round 2 of 2

- **SHA verified:** `11f8975ae6af08a5a0790546efd63151f5c1d6ae` — four commits on top of
  `4158b10` (`8cc6984 38f22f3 b998d72 11f8975`), no force-push (`4158b10` still in the
  PR's commit list). Confirmed unmoved at start and end.
- **Environment:** macOS arm64, node v22.14.0, npm 10.9.2, Playwright 1.63.0; fresh clone
  under a private `mktemp -d`; `npm ci` exit 0. **Host load at start: 1/5/15-min
  101 / 219 / 296** from other work. I created no containers or images.

## R3-1. `npm run ci` at the head

exit 0 — **18 files / 527 tests / 0 skipped**; hygiene `OK: 289 text source(s) … 13
mutation-digest line(s)`; **no lint warning** (the `redact.ts` leftover is gone).

## R3-2. Layer 1 (static) — 38 mutations of mine, sandbox copy, restored between cases

Refused by name (**RED**): my round-2 `.npmrc` `node-options=…` line; any other `.npmrc`
key (`registry=`); `NODE_OPTIONS`, `NPM_CONFIG_NODE_OPTIONS`, `npm_config_userconfig`,
`NPM_CONFIG_USERCONFIG`, `CI: ''`, `CI: false` in env maps; `$GITHUB_ENV` in `run:`,
through a shell variable, and through an env-map value `${{ env.GITHUB_ENV }}`;
`$GITHUB_PATH`; the round-2 env-map `$GITHUB_STEP_SUMMARY` indirection (my R2-FINDING A —
**closed**); a YAML merge key in `e2e.yml` **and in another workflow file** (R2-B —
**closed**); a duplicate key; `pree2e --require`; `continue-on-error` on the redact step;
the upload gated on `conclusion` or `always()`. Regressions from earlier rounds all still
RED: step-level `PLAYWRIGHT_NO_COPY_PROMPT: ""`, workflow `DEBUG`, `index.html`
re-added, `globalSetup`, retention 14.

Green, classified:

| Mutation | Classification |
|---|---|
| `.npmrc` with a comment only | harmless |
| `node_options` / `Node_Options` in an env map | harmless on the `ubuntu-24.04` runner — Node reads only `NODE_OPTIONS`, and it is case-sensitive there |
| `package.json` `config` key | harmless — becomes `npm_package_config_*`, which neither Node nor Playwright reads |
| `XDG_CONFIG_HOME` | harmless — npm does not read it |
| `use.launchOptions.env` in the Playwright config | harmless — that is the BROWSER's environment, not the worker's |
| `HOME` in a job or step env map (+ a committed `.ci-home/.npmrc`) | static-green; npm WOULD read `$HOME/.npmrc`, but the pinned browsers live under the original `$HOME` cache, so the lane cannot launch; layer 2 would still catch it if it did. Not a finding; worth one line in § Residuals |
| `$GITHUB_ENV` whose NAME is built at runtime (`printenv | grep`) | the stated `run:` class |
| top-level `process.env` mutation in `playwright.config.ts` | static-green — examined at runtime in R3-3 |
| **redact step `run:` laundered or replaced** | **R3-FINDING H below** |

### The redaction step is recognised by a substring

`check-e2e-lane.mjs:320`: `const redactStep = steps.find((step) => runOf(step).includes(REDACT_SCRIPT));`
with `REDACT_SCRIPT = "redact-artifacts.sh"`. Every one of these is **guard-green**:

```
run: bash scripts/ci/redact-artifacts.sh test-results playwright-report || true
run: bash scripts/ci/redact-artifacts.sh test-results playwright-report; exit 0
run: set +e; bash scripts/ci/redact-artifacts.sh test-results playwright-report; true
run: bash scripts/ci/redact-artifacts.sh test-results playwright-report > /dev/null 2>&1 || echo skipped
run: bash scripts/ci/redact-artifacts.sh test-result playwright-reports     # typo: "does not exist, nothing to redact", exit 0
run: bash scripts/ci/redact-artifacts.sh test-results                      # results.json (uploaded) never redacted or gated
run: bash scripts/ci/redact-artifacts.sh /tmp/empty
run: echo redact-artifacts.sh                                              # the redactor never runs at all
```

Each leaves `steps.redact.outcome == 'success'`, so the upload — correctly gated on
that — publishes whatever the lane wrote, with no URL redaction and **no page-snapshot
gate**. The same guard already refuses `continue-on-error` on this step, with the reason
"would report `success` however it exited — the gate below would then always…"; the
spellings above have exactly that effect. The substring match is identical at
`6bf0a0e`, `e096053`, `4158b10` and `11f8975` — it **predates this round, and I missed it
in rounds 1 and 2.** It matters more now because this round's answer to the R2-E class
names the upload gate as the layer that "does not depend on the variable at all, so for
the page snapshot specifically it still holds". → R3-FINDING H.

## R3-3. Layer 2 (runtime) — eight variants in a probe spec, `CI=1` and `PLAYWRIGHT_NO_COPY_PROMPT=1` set as the job sets them

Localhost fixture server, runtime markers, shipped config; then the SHIPPED
`redact-artifacts.sh` (layer 3) on the result.

| Variant (inside a spec under `e2e/specs/`) | Layer 2 | `# Page snapshot` written | typed value on disk | Layer 3 (redactor exit) |
|---|---|---|---|---|
| (z) control, untouched | silent (correct) | no | no | 0 |
| (a) module scope: `PLAYWRIGHT_NO_COPY_PROMPT = ""` | **fires at worker start**, before any page | no | no | 0 |
| (d) body blanks it, restores `"1"` before the end | silent | no — the recorder read `"1"` | no | 0 (harmless) |
| (c) body blanks it | fires "after the test body" | **yes (2 files)** | **yes** | **1 — blocks** |
| (e) `test.afterEach` blanks it | fires "after the test body" | **yes** | **yes** | **1 — blocks** |
| (g) `test.extend` auto fixture blanks it in teardown | fires "after the test body" | **yes** | **yes** | **1 — blocks** |
| (b) module scope: `delete process.env.CI` + blank | **silent** | **yes** | **yes** | **1 — blocks** |
| (f) body: `delete process.env.CI` + blank | **silent** | **yes** | **yes** | **1 — blocks** |

Two things this establishes that AGENTS.md does not say:

1. **Layer 2 after the body is detection, not prevention.** For (c), (e) and (g) it
   fails the run by name, but the snapshot has already been written by the time the
   context closes — and a failed run is exactly the condition under which the workflow
   uploads. For every route after worker start, **layer 3 alone** protects the artifact.
2. **Layer 2 is off whenever `CI` is unset, and a spec can unset it.**
   `pageSnapshotProblem` begins `if (!env.CI) return undefined;`. A spec under
   `e2e/specs/` with
   ```ts
   delete process.env.CI;
   process.env.PLAYWRIGHT_NO_COPY_PROMPT = "";
   ```
   passes `eslint` (exit 0), the credential tripwire (11/11), `tsc`, the lane guard and
   the hygiene check, and layer 2 never fires. This is not the stated residual ("code
   that runs BEFORE the harness module loads … that replaces `process.env` itself, or
   patches Playwright's recorder"): it runs after the harness loads and replaces nothing.
   AGENTS.md's "Anything but exactly `"1"` fails the run by name, **whatever route
   changed it**" is false for it.

## R3-4. All three layers, defeated together — every check green

A faithful local simulation of the job, one step at a time, with the probe spec (b)
committed under `e2e/specs/` and ONE edit to `.github/workflows/e2e.yml`:
`run: bash scripts/ci/redact-artifacts.sh test-results playwright-report || true`.

```
1. static:   check-e2e-lane exit=0   eslint exit=0   hygiene exit=0
2. lane:     CI=1 PLAYWRIGHT_NO_COPY_PROMPT=1 npx playwright test …   exit 1  (failure() is true)
             runtime-assertion lines in the log: 0
3. redact:   bash -e -c 'bash scripts/ci/redact-artifacts.sh test-results playwright-report || true'
             exit 0  -> steps.redact.outcome == 'success' -> the upload runs
             (the gate DID print "a PAGE SNAPSHOT is present" — and `|| true` discarded it)
4. upload set: 2 files with a '# Page snapshot' line under test-results/
               error-context.md:25   - textbox [active] [ref=e2]: <TYPED-MARKER>
```

I did not run GitHub Actions; steps 1–3 are the job's own commands and conditions, run
as the runner runs them (`bash -e`). Sandbox restored, `git status` clean.

## R3-5. Layer 3's own precision

The gate is `grep -rlxF -- '# Page snapshot'` over the plain tree and over every unpacked
`*.zip`. Planted into a `test-results/` copy and run through the shipped script:

| Planted | Gate |
|---|---|
| `# Page snapshot` as its own line — what Playwright writes (`errorContext.js:78`) | **exit 1** |
| `# page snapshot`, `## Page snapshot`, trailing space, CRLF, heading inside a JSON string | exit 0 |
| the exact heading in a zip nested inside a zip; in a `.gz` | exit 0 |

The gate is exact to what Playwright writes, and that heading is pinned against
Playwright's source (`redaction-corpus.test.ts:121` reads `errorContext.js` and expects
`"# Page snapshot"`), so a Playwright rename turns a test red. Playwright produces none
of the other forms, so these are not findings. In my runs the snapshot was always in
`error-context.md` and its trace attachment, and never in `results.json`. **The gate is
sound when it runs; R3-FINDING H is that nothing guarantees it runs.**

## R3-6. The shared redaction programs

**One source, confirmed.** `redact.ts:50` imports `./redaction-patterns.json` and builds
`new RegExp(pattern, flags)` from it. `redact-artifacts.sh` decodes the same file with
perl's core `JSON::PP` (it exits 2, BLOCKED, if the file or `JSON::PP` is missing). No
URL program is duplicated inline in either redactor; the shell's separate HAR
`queryString` program is not a URL shape. `redaction-corpus.test.ts` runs as part of
`npm run ci` (527/527 green).

**Out-of-corpus shapes** — runtime marker, BOTH shipped redactors, identical results
every time (they really are one program now):

| Shape | Both redactors | In the NOT-covered list? |
|---|---|---|
| `&` for `&` (Go), `&amp;` for `&`, `&#63;` for `?`, `%20` in the query, mixed-case `Https`, URL in backticks, after `|`, after `url:` | redacted | — |
| `//host?q` (no path) | redacted | listed as NOT covered — safe direction |
| `host:3000?q` (no path), `myhost/p?q` (single label) | survive | **listed** |
| query split by a line wrap (`…?a=1&s⏎ig=<M>`) or before `?` | survive | the list names splits "across two JSON fields or two archive members", not a wrap within one field — adjacent |
| **`https://h.example/p?q`** (`\u`-escaped slashes) | **survive** | **no** — and the Covered text says "a `\uXXXX` escape may appear inside the URL" |
| **`…/p?sig=<M>`** (`\u`-escaped `?`) | **survive** | **no** — same sentence |
| `https:%2F%2Fh%2Fp?q`, a fully percent-encoded URL standing alone, `\x2F`, `&#47;`, `&#x2F;`, `&sol;` | survive | no |
| `url:h.example:3000/p?q`, `GET:/p?q`, `a;/p?q` (a `:` or `;` just before a scheme-less or relative URL) | survive | no |

The programs allow `\uXXXX` in the host, path and query body, but not in place of the
`//` after the scheme, nor as the `?` separator. The Covered sentence is broader than
that. Reachability is low — Go, JS, PHP (default) and Python do not emit `/` or
`?` — so this is not the round-1/round-2 class at blocking strength. → R3-FINDING I.

## R3-7. Per-commit truth, and my round-2 FINDING D

`npm run ci` cold at each new commit (separate clone; `git clean -fdx -e node_modules`;
caches removed; no lockfile change in this round). Load averages 163–209 throughout.

| Commit | Exit | Files | Tests | Skipped | Lint |
|---|---|---|---|---|---|
| `8cc6984` | 0 | 17 | 518 | 0 | clean |
| `38f22f3` | 0 | 18 | 526 | 0 | clean |
| `b998d72` | 0 | 18 | 527 | 0 | clean |
| `11f8975` | 0 | 18 | 527 | 0 | clean |

These match the builder's claim exactly (17/518, 18/526, 18/527, 18/527).

**Round-2 FINDING D — closed.** The expected labels are now read from `demonstrate.sh`:
an emptied ledger, a deleted first line, a label renamed `D12 → D99` and a zeroed digest
are each **RED by name**. A duplicated *valid* line passes ("14 lines match") —
harmless.

## R3-8. `npm run e2e:demos` — two consecutive runs, clean quiescent tree

Dedicated clone, production build (`PUBLIC_ORIGIN=http://127.0.0.1:3211`), tree reset
between runs, nothing else of mine running, nothing edited during either run. The host
was far from quiet (other work).

**Run 1:** 01:57:56 → 02:38:38, load (1/5/15) 130 / 169 / 205 → 159 / 235 / 265 —
**133 passed, 0 blocked, 0 failed, exit 0.** Among them:

```
ok   d14-late-fault-150ms-RED                                   (exit 1, 'late fault demonstration (D14)')
ok   d14-late-fault-after-the-window-is-not-charged-GREEN       (exit 0, '1 passed')
ok   d11f-in-process-reporter-deleted-GREEN                     (exit 0, '20 passed')
ok   d16a-page-snapshot-without-the-variable-RED                (exit 1, 'PAGE SNAPSHOT is present')
ok   d16a-no-page-snapshot-with-the-variable-GREEN              (exit 0, 'and no page snapshot is present')
ok   d16b-npmrc-node-options-refused-by-the-lane-guard-RED      (exit 1, '.npmrc sets `node-options`')
ok   d16b-npmrc-node-options-refused-at-RUNTIME-RED             (exit 1, 'PLAYWRIGHT_NO_COPY_PROMPT is not')
ok   d16c-variable-blank-in-the-environment-RED / -unset-RED   (exit 1)
ok   d16c-variable-exactly-1-with-CI-set-GREEN                  (exit 0, 'harness stamp: OK')
ok   d16d-escaped-url-reaches-the-upload-set-RED                (exit 1)
ok   d16d-escaped-url-redacted-by-the-shipped-path-GREEN        (exit 0, 'members containing the sentinel: 0')
ok   d16d-error-context-carries-test-source-GREEN               (exit 0, '# Test source')
```

(The last line answers the `# Test source` nit I carried from round 1: the section IS
written when the failing error's stack points at a readable file, and AGENTS.md now says
exactly that. Closed.)

**Run 2** (immediately after, tree reset): 02:38:38 → 03:14:18, load 159 / 235 / 265 →
195 / 162 / 212 — **133 passed, 0 blocked, 0 failed, exit 0.** `d14-late-fault-150ms-RED`,
`d14-late-fault-after-the-window-is-not-charged-GREEN` and
`d11f-in-process-reporter-deleted-GREEN` all passed again.

**The builder's 133 / 0 / 0 reproduces, twice in a row, at load averages above anything
in earlier rounds.** My round-2 FINDING G is closed.

**D14, stated honestly.** The LIMIT half no longer demonstrates "a late fault is missed";
it fires the fault 20 s after the body and asserts only that such a fault is **not charged
to the test**. That is an invariant as long as worker teardown finishes inside 20 s. It
did in all four of my D14 runs, at loads up to 265. It is a margin, not a proof — the
builder says the same ("teardown > 20 s" would break it), and I agree with that wording.

## R3-9. Lanes at `11f8975`, run by me

| Lane | Result |
|---|---|
| `npm run ci` | exit 0 — 18 files / 527 tests / 0 skipped; 0 lint warnings; hygiene 289 / 13 |
| `bash scripts/ci/require-checks_test.sh` | exit 0 — **182 cases, 189 assertions, 0 failed** (matches) |
| `check-e2e-lane.sh`, `check-required-floor.sh`, `check-image-pins.sh`, `check:contract` | exit 0 each |
| `CI=1 PLAYWRIGHT_NO_COPY_PROMPT=1 npx playwright test` | exit 0 — **18 passed**, floor OK (9/9 9/9), **18 stamps** — so layer 2 is active and quiet on the honest lane |
| `node scripts/ci/harness-canary.mjs` (same env) | exit 0 — failed all 4 fault-injection fixtures, each for its own kind |
| tripwire + `redaction-corpus.test.ts` | 105/105 |
| `npm run e2e:demos` | 133 / 0 / 0, twice (R3-8) |

**Regression:** tokenising call check — trailing comment RED `absent`, string RED `absent`,
`void` RED, shadowed RED, real call GREEN. Sanitiser — `"  ::"` and `"\t::"` broken with
U+200B, `\n` → `⏎`, `%0A` → `%250A`, `Foo::bar` untouched. `index.html` re-add,
`globalSetup`, retention 14, step-level and workflow-level env — all RED (R3-2). F10 pair —
D16a. No credential-format literal in the four commits' added lines (0 hits); the one spec
change (`home.spec.ts`) is a `networkidle` and visibility wait — nothing that
authenticates, fills a credential or touches a signed URL. The hard rule stands.

## R3-10. CI on `11f8975` (read with `gh`)

All **9** check-runs `completed` / `success`; `ci-required` finished last (05:31:57Z,
after `e2e` at 05:31:27Z). `.github/required-checks.txt` blob `f2f23454…` — byte-identical
to main's; `frontend`, `contract`, `?guard`, `?docker-build`, `e2e` all ran and succeeded.
`e2e` run `35822597458`: `18 passed`, floor OK 9/9 9/9, `harness stamp: OK (18 …)`, canary
4/4; artifacts **0** (a green run). **There has still never been a RED CI run on any SHA of
this PR**, so the upload path has never been exercised in GitHub.

## R3-11. Truthfulness — sentences stronger than their control

1. AGENTS.md (layer 3) and the PR body: "`redact-artifacts.sh` refuses — exits non-zero,
   **so the gated upload publishes nothing**" and "Layer 3 does not depend on the variable
   at all, **so for the page snapshot specifically it still holds**". True of the script;
   not of the lane, whose guard accepts a redaction step that does not run the script, or
   discards its exit code. → R3-FINDING H.
2. AGENTS.md's Commands table: the guard ensures "EVERY upload step is gated on the
   redaction having succeeded". The upload is gated on a step whose `run:` merely
   CONTAINS `redact-artifacts.sh`. → R3-FINDING H.
3. AGENTS.md and the PR body (layer 2): "Anything but exactly `"1"` fails the run by
   name, **whatever route changed it**". Not when the route also deletes `CI`. And the
   stated residual ("code that runs BEFORE the harness module loads … that replaces
   `process.env` itself, or patches Playwright's recorder") does not describe that route.
   → R3-FINDING J.
4. AGENTS.md: "a `\uXXXX` escape may appear inside the URL". Not in place of the `//` or
   the `?`. → R3-FINDING I.

Accurate, and verified: the four-program table and its examples; "one program in
behaviour, by construction"; the NOT-covered list (every item on it measured as stated,
one in the safe direction); the file-by-file publication table; D16a–d as described; the
per-commit counts; the D14 wording; the two process notes in the PR body; "0 warnings"; 289 sources.

## Status of my round-2 findings at `11f8975`

| # | Round-2 finding | At `11f8975` |
|---|---|---|
| E | `.npmrc` `node-options` blanks the variable, guard green (BLOCKER) | **closed as stated** — any committed `.npmrc` key is refused (my line is RED), `NODE_OPTIONS`/`npm_config_*`/`CI` refused in every env map, and layer 2 catches it at runtime (D16b, and my own probes). The CLASS is not closed: R3-FINDING H and J below |
| C | shell redactor ≠ `redact.ts`; realistic escaped URL survives | **closed** — one pattern file, one behaviour, measured identical on 26 out-of-corpus shapes; D16d reproduces my real-lane survivor and its fix. A residue of sentence breadth is R3-FINDING I |
| A | `$GITHUB_STEP_SUMMARY` via an env map | **closed** |
| B | `$GITHUB_ENV` unmodelled; merge keys | **closed** — refused in `run:` text and env values, and merge keys refused in every workflow; a runtime-built NAME remains the stated `run:` class |
| D | empty/trimmed ledger passes | **closed** |
| G | demos not reproducible under load; D14 timing | **closed as far as I can measure** — see R3-8 |
| F | stale counts, lint warning, sources count | **closed** — per-commit counts match exactly; 0 lint warnings; 289 sources |
| round-1 9(b) | no F10 red/green pair | **closed** — D16a |

## Findings at `11f8975`

```
R3-FINDING H: the redaction step is recognised by a SUBSTRING, so the upload gate —
              and all URL redaction — can be switched off with the guard green
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-e2e-lane.mjs:320
               const redactStep = steps.find((step) => runOf(step).includes(REDACT_SCRIPT));
             (REDACT_SCRIPT = "redact-artifacts.sh"; the step's `run:` text is otherwise unread)
             AGENTS.md: "EVERY upload step is gated on the redaction having succeeded";
             "redact-artifacts.sh refuses — exits non-zero, so the gated upload publishes
             nothing"; "Layer 3 does not depend on the variable at all, so for the page
             snapshot specifically it still holds". PR body: layer 3 "so the gated upload
             publishes nothing".
  requirements: VZ-FOUND-008

Observed:
  Guard-green spellings of the redaction step (each leaves steps.redact.outcome ==
  'success', so the correctly-gated upload runs):
      run: bash scripts/ci/redact-artifacts.sh test-results playwright-report || true
      run: bash scripts/ci/redact-artifacts.sh test-results playwright-report; exit 0
      run: set +e; bash scripts/ci/redact-artifacts.sh …; true
      run: bash scripts/ci/redact-artifacts.sh … > /dev/null 2>&1 || echo skipped
      run: bash scripts/ci/redact-artifacts.sh test-result playwright-reports   (typo -> "nothing to redact", exit 0)
      run: bash scripts/ci/redact-artifacts.sh test-results                     (results.json never redacted or gated)
      run: echo redact-artifacts.sh                                             (the redactor never runs)
  The same guard refuses `continue-on-error` on this step BECAUSE it "would report
  `success` however it exited". Every spelling above has that effect.

  End to end (R3-4): a two-line spec under e2e/specs/
      delete process.env.CI; process.env.PLAYWRIGHT_NO_COPY_PROMPT = "";
  plus `|| true` on the redaction step. Lane guard exit 0, eslint exit 0, hygiene exit 0,
  tripwire 11/11. The lane fails (so the upload condition is met), layer 2 never fires,
  the shipped gate prints "a PAGE SNAPSHOT is present" and `|| true` discards it (step
  exit 0), and the upload set holds 2 files with a `# Page snapshot` line —
  error-context.md:25 `- textbox [active] [ref=e2]: <TYPED-MARKER>`.

Failure:
  All three layers of the answer to the R2-E class fail together, and every check this
  repository runs stays green. Separately from the page snapshot, `run: echo
  redact-artifacts.sh` turns off ALL URL redaction on a red lane — the control this
  whole lineage (PR #3 onward) exists for. The substring match predates PR #8
  (identical at 6bf0a0e, e096053, 4158b10 and 11f8975) and I missed it in rounds 1 and 2;
  it becomes blocking now because this round names layer 3 as the backstop that "still
  holds" when layers 1 and 2 do not.

Perspective: developer, then member (from M1 the page is the product)

Recommendation:
  Pin the redaction step's `run:` EXACTLY, as the guard already does for the lane step
  (`npm run e2e`) and the canary: `bash scripts/ci/redact-artifacts.sh test-results
  playwright-report` and nothing else. That one change closes every spelling above.
  Keep the existing continue-on-error, if:, id and ordering checks.

Acceptance criteria:
  require-checks_test.sh: each of the seven spellings above is RED by name, and the
  exact literal stays green.

Tests: scripts/ci/require-checks_test.sh (seven cases).
Cross-repo implications: core: none | user: as above | search: none | meta: the same
  exact-match rule for any privacy-bearing step in a future CI fan-in.
Challenge:
  "It needs an edit to e2e.yml, a CODEOWNERS path." So did round-1 FINDING 2 (a
  step-level env line) and round-2 FINDING E (a committed `.npmrc` line), both ruled
  blockers on the same reasoning: the guard exists because these properties are
  invisible in a green run, and it already refuses `continue-on-error` here for exactly
  this outcome.
```

```
R3-FINDING J: layer 2 is off whenever `CI` is unset, a spec can unset it, and after the
              body it detects rather than prevents
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     e2e/harness/ci-environment.ts (`if (!env.CI) return undefined;`)
             eslint config / e2e/harness/no-credentials-in-specs.test.ts (neither refuses
             `process.env` writes in e2e/specs)
             AGENTS.md: "Anything but exactly "1" fails the run by name, whatever route
             changed it"; the stated residual ("code that runs BEFORE the harness module
             loads … that replaces `process.env` itself, or patches Playwright's recorder")
  requirements: VZ-FOUND-008

Observed (R3-3):
  - `delete process.env.CI; process.env.PLAYWRIGHT_NO_COPY_PROMPT = "";` at a spec's
    module scope or in its body: layer 2 silent; snapshot and typed value written.
    eslint exit 0, tripwire 11/11, tsc exit 0, lane guard exit 0.
  - Blanking the variable in the body, in `afterEach`, or in a `test.extend` fixture's
    teardown: layer 2 fires by name "after the test body" — but the snapshot has already
    been written (2 files, typed value present). A failed run is precisely when the
    workflow uploads, so for every route after worker start, only layer 3 protects.
  - Blanking at module scope is caught at worker start, before any page opens (the one
    route where layer 2 prevents).
Failure:
  The residual is misstated (this route runs AFTER the harness loads and replaces
  nothing), "whatever route changed it" is false for a route that changes `CI`, and the
  layer's after-body check is described as if it stopped the snapshot.
Recommendation:
  - Capture `CI` and the variable once, at harness module load (config evaluation), and
    compare the worker's live values against that capture — deleting `CI` later is then
    itself a failure.
  - Refuse writes to `process.env` in e2e/specs/** and e2e/demos/** (lint rule or the
    tripwire), with the harness exempt.
  - Say in AGENTS.md that the after-body check makes the run red with the snapshot
    already on disk, and that the upload gate is what keeps it off the runner.
Acceptance criteria: the probe spec above FAILS at runtime by name (or is refused by
  lint); AGENTS.md's sentence matches.
Tests: e2e/harness/ci-environment.test.ts; one demonstrate.sh half.
Challenge: "Layer 3 catches it." Only while R3-FINDING H stays open — which is the point
  of defence in depth.
```

```
R3-FINDING I: the Covered text says a `\uXXXX` escape may appear inside the URL; a
              `\u`-escaped `//` or `?` survives both redactors
Severity:    SHOULD
Confidence:  high
Affected: vizra-user; e2e/harness/redaction-patterns.json; AGENTS.md "JSON escaping, at up
  to three levels … and a `\uXXXX` escape may appear inside the URL"; the NOT-covered list
Observed (R3-6), identical in both shipped redactors:
  survive: `https://h.example/p?q`, `…/p?sig=`, `%2F`-encoded slashes,
  a fully percent-encoded URL standing alone, `\x2F`, `&#47;`, `&#x2F;`, `&sol;`,
  `url:host:3000/p?q` / `GET:/p?q` / `a;/p?q` (`:` or `;` just before a scheme-less or
  relative URL), and a query split by a line wrap inside one field.
  None of these is in the NOT-covered list. Low reachability: Go, JS, PHP (default)
  and Python do not emit `/` or `?`.
Recommendation: narrow the sentence to "`\uXXXX` inside the host, path or query", and add
  the unmatched shapes to the NOT-covered list, in the same voice as the no-path ones.
Acceptance: each shape either redacts in the corpus, or is named in the list.
```

```
R3-FINDING K: a user-level npmrc via `HOME` is not refused statically
Severity:    NIT
Observed: `HOME: …` in a job or step env map is guard-green, and npm reads `$HOME/.npmrc`.
  In practice the lane cannot launch Chromium under a changed HOME (the browsers live in
  the original HOME's cache), and layer 2 would catch the blanked variable at worker start
  if it did. One line in § Residuals, or add HOME to the refused env keys.
```

## Verdict at `11f8975`

This round did a great deal right. Every finding I raised in round 2 is closed as stated:

- **E** — my `.npmrc` line and every sibling spelling are refused, and layer 2 catches the
  line at runtime.
- **C** — the two redactors are genuinely one program; I measured 26 out-of-corpus shapes
  with byte-identical behaviour.
- **A, B, D, F** — closed.
- **G** — the demo suite reproduced **133 / 0 / 0 twice in a row** at load averages up to 265.
- The F10 red/green pair is committed at last (D16a).

The per-commit counts match exactly, CI is green 9/9 with the manifest unchanged, and
nothing credential-shaped was added.

I am nonetheless returning **FAIL**, on one blocker of the same class as the previous two.

**R3-FINDING H.** The guard recognises the redaction step by
`run.includes("redact-artifacts.sh")`. So seven guard-green spellings all leave
`steps.redact.outcome == 'success'` and let the upload run:

- `… || true`
- `…; exit 0`
- `set +e; …`
- output discarded with `|| echo`
- a typo'd directory
- dropping `playwright-report`
- `echo redact-artifacts.sh`

With any of them, the upload publishes with **no URL redaction and no page-snapshot
gate**. Together with the two-line spec of R3-FINDING J, which deletes `CI`, I drove all
three layers to fail at once, with every check this repository runs green. A page snapshot
carrying a typed value lands in the upload set.

The guard already refuses `continue-on-error` on this very step for exactly this outcome.
The fix is one line: match the step's `run:` exactly, as it already does for `npm run e2e`
and the canary.

In fairness, the substring match is older than this PR, and I missed it in rounds 1 and 2.
It is blocking now because this round's answer to the R2-E class names layer 3 as the
backstop that "still holds" when layers 1 and 2 do not. It does not, while the step that
runs it can be rewritten unseen.

**R3-FINDING J** (required): layer 2 is off whenever `CI` is unset, and a spec can unset
it. After the test body, layer 2 detects rather than prevents. The docs overstate both
points.

**R3-FINDING I** (should-fix): the `\uXXXX` sentence is broader than the programs.

**R3-FINDING K** (nit): changing `HOME` in an env map is not refused.

Nothing I found is a live disclosure. Nothing authenticates, the hard rule stands and is
asserted, and no RED CI run has ever uploaded anything for this PR.

FINAL VERDICT: FAIL — SHA 11f8975ae6af08a5a0790546efd63151f5c1d6ae
