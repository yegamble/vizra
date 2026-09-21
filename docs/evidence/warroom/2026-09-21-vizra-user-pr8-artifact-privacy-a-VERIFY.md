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
