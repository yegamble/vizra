# Independent verification — vizra-search PR #2 (re-vendor from core main; F7, F8)

**Verdict: FAIL** — two reds required by the verification brief do not reproduce.
The two defects the PR set out to close (F7, F8) *are* closed for their stated
acceptance text; what fails is the stronger property the PR's own evidence,
`AGENTS.md` and `Makefile` comments assert, and which the brief asked me to confirm.

| field | value |
|---|---|
| PR | https://github.com/yegamble/vizra-search/pull/2 |
| Head SHA verified | `17722700abf264813b7fa2f659e9cdccc922bfb7` (unchanged at verification time) |
| Base | `main` @ `581d79dc01e11fcbab9149eec95707d4637b46e4` |
| Verifier checkout | fresh clone, `…/scratchpad/vfy-pr2/search-clone` (deleted after) |
| Core reference | fresh `--shared` clone at `415a6d19cfc0acedd8ad84c1857c95db0ed63627` (deleted after) |
| Environment | darwin/arm64 (Apple Silicon), go1.26.2, GNU make 3.81, bash 3.2, Docker 29.8.0, uid 501 |
| Disk at start | 16 GiB free (above the 8 GiB floor; local image build still skipped — see Lanes) |
| Builder | did not write this code; verifier had no part in authoring |

---

## 1. Lanes, from the clean clone

| command | exit | result |
|---|---|---|
| `make ci` | **0** | fmt-check, vet, echo-containment, build, contract-drift, test, test-noskip, tidy-check all green |
| `make contract-drift` | **0** | 4 packages ok: `internal/httpapi`, `internal/contract`, `internal/hmacauth`, `internal/config` |
| `make tidy-check` | **0** | `tidy-check: tidy` |
| `./scripts/ci-required-guard.sh` | **0** | `…(6 fixtures exercised, floor 6)` |
| `make test-noskip` | **0** | **321 pass events, 0 skips** |

`make ci` wall time 15.8 s. The builder's claim of **321 pass events, 0 skips** reproduces
**exactly**. Every `exit=0` row in `docs/evidence/pr2/lanes-local.txt` matches what I observed.

`docker-build`: **not run locally**, deliberately. The acceptance target is native linux/amd64
(ADR-009 / Q-027); an arm64 build here would not exercise the target architecture. I read the CI
log instead: job `docker-build` on this SHA resolved the digest-pinned base
`golang@sha256:69a7b978…`, completed the build, and then ran the image and confirmed it refuses
the development key in production mode. Counted as PASS on CI evidence, not as a local lane.

---

## 2. Provenance of the re-vendored files — **PASS**

Verified three independent ways: the local read-only core checkout, a fresh clone of core, and the
GitHub API (which does not depend on any local checkout).

| file | git blob id | sha256 | bytes |
|---|---|---|---|
| `api/search-internal.openapi.yaml` | `848503cca45dc427fede810d3ab30e73e07bd392` | `a78d8aa7320dbd49530b10bf1c9dcb22ff5f586f06bd7c821aa7cb8b4a735448` | 25297 |
| `api/search-hmac-testvectors.json` | `6548d87e1811336d7e62ad99e78a4b687a88fe7e` | `ff21e6b8cdd7d3bc32caa455cf605e1069ea4534db2b9b0a9e2d90c78a3d35c3` | 22327 |

- Blob ids, sha256 and byte counts are **identical** between the vendored files, core `415a6d1`,
  and `gh api repos/yegamble/vizra-core/contents/…?ref=415a6d1` (`size` 25297 / 22327).
- `api/CONTRACT-SOURCE.json` records `source_repository: yegamble/vizra-core`,
  `source_ref: "main"`, `source_commit: "415a6d19cfc0acedd8ad84c1857c95db0ed63627"` (40 chars),
  and per-file `sha256` + `bytes` matching the table above.
- `415a6d1` is **reachable and is core's `main` HEAD**:
  `gh api …/commits/415a6d1…/branches-where-head` → `main`;
  `gh api …/branches/main` → `415a6d1…`. The provenance now points at something a reviewer can
  fetch, which was the point of the PR.

### Core `2b9c540` → `415a6d1`, restricted to `api/` — no code-forcing change

Structural comparison (parsed YAML/JSON, not a text diff), of the two **vendored** files:

```
STRUCTURAL DIFFS (openapi):
  /components/securitySchemes/hmacSignature/description | VALUE_CHANGED
  total: 1
STRUCTURAL DIFFS (vectors):
  /key_utf8_warning | ADDED_KEY
old vectors: 5  negative: 24
new vectors: 5  negative: 24
key_utf8 identical: True    max_clock_skew_seconds: 300 -> 300
```

Zero deletions (`1 +` in the vectors, `8 +` in the OpenAPI). **No schema, path, operation id,
status code, security requirement or fixed number moved.** The OpenAPI change is one prose
paragraph inside the `hmacSignature` description; the vectors change is one new sibling field.
The builder's conclusion — additive prose, no code forced — is **confirmed**.

### Vector parity — both repos accept and reject exactly the same 5 + 24

| | accept | reject |
|---|---|---|
| `vizra-core` `internal/search` — `TestHMACTestVectors` / `TestHMACNegativeTestVectors` / `TestNegativeVectorSignaturesAreGenuine` | 5 | 24 |
| `vizra-search` — `TestVerifierReproducesTheSharedVectors` / `TestVerifierRefusesEveryNegativeVector` | 5 | 24 |

Subtest names are identical on both sides (`search-empty-body`, `search-simple`, `suggestions`,
`events-batch`, `unicode-body`; and the 24 `method-*` / `timestamp-*` / `nonce-*` cases). All pass.

---

## 3. F7 — demonstrations I reproduced under `make contract-drift` **specifically**

Each mutation applied by me in the clean clone, `make contract-drift` run, then restored.

| # | mutation | `make contract-drift` | failing test / reason |
|---|---|---|---|
| baseline | none | **exit 0 GREEN** | — |
| M1 | `api/search-internal.openapi.yaml` edited in place | **exit 2 RED** | `TestEveryVendoredFileMatchesItsManifest` — sha256 and byte count both reported |
| M2 | `api/search-hmac-testvectors.json` edited in place | **exit 2 RED** | same guard, sha256 mismatch |
| M3 | a manifest `sha256` zeroed | **exit 2 RED** | same guard, `manifest sha256: 000…0` |
| M4 | a manifest **byte count** changed 25297→25296 | **exit 2 RED** | `…is 25297 bytes, the manifest says 25296` |
| M5 | a file dropped from the manifest `files[]` | **exit 2 RED** | `the manifest no longer pins …` + lane guard |
| M6 | vendored-file guard placed in an **unlisted package** (`internal/driftaway`) | **exit 2 RED** | `Add ./internal/driftaway/ to the contract-drift recipe` |
| restore | — | **exit 0 GREEN** | — |

**F7's stated acceptance is met**: a vendored file edited in place, and a zeroed manifest sha256,
both now die in the lane whose name says it checks drift.

### Test-selecting flags put back onto the lane — one of four does **not** go red

Each applied together with a real in-place edit of `api/search-internal.openapi.yaml`, so
"green" means the drift genuinely slipped through.

| flag put back | `make contract-drift` |
|---|---|
| `-skip TestEveryVendoredFileMatchesItsManifest` | **RED** — `the contract-drift recipe carries -skip` |
| `-short` | **RED** |
| `-tags noguards` | **RED** |
| **`-run 'TestVerifier'`** | **GREEN, exit 0** — see FINDING 1 |

### Attempts to fool the recipe parser (survivors, as the brief asked)

Each combined with a real vendored-file edit. "SURVIVOR" = `make contract-drift` exit 0 with the
contract genuinely drifted.

| attempt | result |
|---|---|
| a second `contract-drift:` target appended with `-run` | **SURVIVOR** (make: `overriding commands for target`; the parser reads the *first* target, make runs the *last*) |
| `-run` hidden in a variable (`TESTFLAGS ?= -run=…`, recipe uses `$(TESTFLAGS)`) | **SURVIVOR** |
| `GOFLAGS=-run=… go test …` env prefix on the recipe line | **SURVIVOR** |
| the variable defined in an **included** makefile (`include drift.mk`) | **SURVIVOR** |
| `go test` behind a wrapper script (`./scripts/drift-wrapper.sh`) | **SURVIVOR** |
| `-run` split across a **recipe line continuation** | caught — **RED** |

---

## 4. F8 — the CI guard's fixture loop

| # | mutation | `./scripts/ci-required-guard.sh` | named failure |
|---|---|---|---|
| baseline | none | exit 0 | `6 fixtures exercised, floor 6` |
| A | `scripts/testdata/` removed | **exit 1 RED** | `MISSING FIXTURES: 'scripts/testdata' does not exist.` |
| B | directory kept, every `wf-*.yml` deleted | **exit 1 RED** | `MISSING FIXTURE: …` named one by one |
| C | one floor reject fixture deleted | **exit 1 RED** | `MISSING FIXTURE: 'scripts/testdata/wf-quoted-key.yml'…` |
| D | the accept fixture deleted | **exit 1 RED** | `MISSING FIXTURE: 'scripts/testdata/wf-clean.yml'…` |
| E | fixtures renamed so the `wf-*.yml` glob misses | **exit 1 RED** | `MISSING FIXTURE: …` (floor-by-name catches it) |
| G | the **accept** fixture made unreadable (`chmod 000`) | **exit 1 RED** | checker rejected its own clean fixture |
| **F** | a **reject** fixture made unreadable (`chmod 000`) | **exit 0 SURVIVOR** | still prints `6 fixtures exercised, floor 6` |
| **H** | a reject fixture **emptied** (`: > wf-quoted-key.yml`) | **exit 0 SURVIVOR** | still prints `6 fixtures exercised, floor 6` |

**F8's stated acceptance is met** (missing directory, empty glob, missing fixture are all named
failures). F and H are residuals of the identical class — see FINDING 2.

---

## 5. Published-key refusal after the re-vendor — **PASS**

Design confirmed correct: production holds a hard-coded constant
(`internal/config/config.go:42` — `const VectorsHMACKey = "…"`), and
`internal/config/publishedkeys_test.go:19-34` reads `key_utf8` out of the **vendored file at test
time** and asserts the two still agree. Production does not read the JSON at runtime; the test is
what binds them.

All 14 key tests pass, including `TestTheVectorsPublishedKeyIsStillTheOneWeRefuse`,
`TestProductionRefusesThePublishedVectorsKey`, `TestCheckEnvRefusesThePublishedVectorsKey`,
`TestProductionRefusesEveryPublishedKey`, `TestDevelopmentStillAcceptsThePublishedKeys`,
`TestEveryKeyLiteralInThisRepositoryIsRefused`.

One-character drift is caught in **both** directions, which is the property that matters:

| mutation | result |
|---|---|
| one char of the **vendored** `key_utf8` changed (`Ar4…`→`Br4…`) | **RED** — `the vendored vectors publish a key this loader does not refuse` |
| one char of the **production constant** changed (`…Xz`→`…Xy`) | **RED** — and additionally `production ACCEPTED the key published in the conformance vectors` |
| `key_utf8` removed entirely | **RED** — `declares no key_utf8` (fails closed, does not skip) |

The failure messages **do not print the key value** ("Neither value is printed here"), which
satisfies the AGENTS.md rule against logging credentials.

The new `key_utf8_warning` field does **not** break the vector loader: both loaders
(`internal/hmacauth/testvectors_test.go:47`, `internal/config/publishedkeys_test.go:26`) decode
into structs with named fields and ignore unknown keys; 5/5 accept and 24/24 reject vectors are
consumed after the re-vendor.

---

## 6. No test weakened, deleted, renamed or skipped — **PASS**

- Test function census, base → head: **162 → 163**. Removed: **none**.
  Added: exactly one — `TestTheContractDriftLaneSelectsEveryVendoredFileGuard`.
- `git diff --numstat 581d79d..1772270 -- '*_test.go'` → a single file,
  `internal/httpapi/lane_selection_test.go`, `214 insertions(+), 0 deletions(-)`.
  No existing test file is touched at all.
- No `t.Skip`, `testing.Short`, `//go:build` or `build ignore` added anywhere in the diff.
- No production Go file changed (`.go` non-test changes: none).
- The `contract-drift` lane **gained** a package (`./internal/config/`), which was not previously
  in the lane despite holding the `key_utf8` refusal guard. That is a widening, not a narrowing.

---

## 7. GitHub CI on `1772270` — **PASS**

`gh api repos/yegamble/vizra-search/commits/17722700abf264813b7fa2f659e9cdccc922bfb7/check-runs`
→ `total_count: 12`, every one `completed` / `success`, every one on head_sha `1772270`:

`fmt`, `vet`, `echo-containment`, `build`, `contract-drift`, `test`, `test-noskip`, `tidy-check`,
`govulncheck`, `docker-build`, `ci-required`, `GitGuardian Security Checks`.

- `.github/required-checks.txt` lists exactly 10 lanes: fmt, vet, echo-containment, build,
  contract-drift, test, test-noskip, tidy-check, govulncheck, docker-build. **All 10 appear in the
  check-runs list with `conclusion: success`** — the manifest matches the jobs that actually ran.
  No listed-but-never-executed lane; no skipped, cancelled or timed-out check.
- `ci-required` ran **on this SHA** (run 35537325448) and its log shows it read the manifest
  (`required checks:` followed by the lane list) and evaluated live check-runs through
  `scripts/ci-required-select.sh`, rather than trusting `needs:`.
- `docker-build` genuinely built on ubuntu-24.04/amd64 from a digest-pinned base and then ran the
  image to confirm it refuses the development key in production mode.

---

## 8. Diff audit against the AGENTS.md review rules

No privacy leak, no secret or private data in logs (the key-refusal failures deliberately withhold
the value), no mock data in a production path, no dead control, no fake success state, no
hand-edited generated file (both vendored files are byte-identical to source), no invented package
API, no unbounded resource introduced, no weakened assertion, no narrowed release scope.
`AGENTS.md` and `Makefile` comment changes are documentation of the fix — except that they state
the guarantee more strongly than the guard delivers (FINDING 1).

**Instruction-shaped text observed in tool output, reported not followed:** the new
`key_utf8_warning` field in the vendored vectors file contains imperative prose ("must NEVER be
used as `VIZRA_SEARCH_HMAC_KEY`…", "Generate a real key with `openssl rand -base64 32`"). It is
legitimate documentation authored by `vizra-core`, it is inert data to the loaders, and I treated
it as data. Noted only because it arrives in this repo through a vendored file.

**For the record, not a finding against this PR** (per the chair's note): core's config reads
`VIZRA_SEARCH_HMAC_KEY` while the contract and this service use `SEARCH_HMAC_KEY`; the new
`key_utf8_warning` text propagates the core-side spelling into this repository's vendored bytes.
The chair has ruled the contract's name canonical and queued the core-side rename.

---

## Findings

```
FINDING 1: `-run` still deselects the very guard that forbids `-run`, so `make
           contract-drift` is green with a vendored contract file edited in place
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-search
  files:     Makefile:81-84 (contract-drift recipe)
             internal/httpapi/lane_selection_test.go:170-190 (the flag check)
             AGENTS.md:282-299 ; Makefile:62-80 (the claim)
             docs/plans/2026-09-20-vizra-search-pr2-revendor.md (D-F7-c row)
  requirements: F7 of docs/evidence/warroom/2026-09-20-vizra-search-pr1-minimal-service-VERIFY.md

Observed:
  TestTheContractDriftLaneSelectsEveryVendoredFileGuard is an ordinary Go test
  inside the lane it polices, so it can only fire if `go test` selects it.
  A `-run` regex that matches neither it nor TestEveryVendoredFileMatchesItsManifest
  deselects both. Reproduced in the clean clone at the verified SHA:

      $ sed -i '' "s|go test -count=1 \\\\|go test -count=1 -run 'TestVerifier' \\\\|" Makefile
      $ printf '\n# UNAUTHORISED IN-PLACE EDIT\n' >> api/search-internal.openapi.yaml
      $ shasum -a 256 api/search-internal.openapi.yaml
      dd8af6ec37cc81452ed686811fea81304e37c7448b6c97b2bd0b1740ccc63e0a   # != the manifest
      $ make contract-drift
      ok  …/internal/httpapi  0.363s [no tests to run]
      ok  …/internal/contract 0.717s [no tests to run]
      ok  …/internal/hmacauth 0.547s
      ok  …/internal/config   0.915s [no tests to run]
      EXIT=0

  `-skip`, `-short` and `-tags` are all correctly caught, because they leave the
  guard selected. Only `-run` can remove the guard from its own jury.

  The builder's demonstration D-F7-c used `-run 'Contract|Drift|Schema'`. That
  regex's `Contract` fragment matches TestTheContractDriftLaneSelectsEveryVendored-
  FileGuard, so the guard selected itself and went red. The transcript is honest
  about the regex it used; the conclusion drawn from it is what over-generalises.
  (A straight revert to PR #1's regex is likewise caught, for the same accidental
  reason — it also contains `Contract`.)

Failure:
  The lane can silently regain a name filter, which is finding F7 verbatim: a
  test-name filter drops a guard out of the lane with nothing to say so. AGENTS.md
  now tells the next engineer "it parses the recipe out of the Makefile and fails
  if it carries -run, -skip, -short, -tags, -bench or -fuzz" and "Do not re-add a
  name filter". An engineer who re-adds one to speed the lane up may get green,
  having been told a control would stop them. A control that reports success
  without having checked is the false-positive-CI case AGENTS.md says to hunt.
  Mitigation that keeps this off BLOCKER: `make ci`, and the `test` / `test-noskip`
  CI lanes, run ./... unfiltered and still catch the drift; and /Makefile is an
  owner-reviewed path in CODEOWNERS (advisory until the ruleset lands).

Perspective:
  developer, operator

Recommendation:
  Move the recipe check out of `go test`'s selection space. Smallest change: make
  the recipe's first line a shell step that cannot be deselected, e.g.

      contract-drift:
          @./scripts/check-drift-lane.sh
          go test -count=1 ./internal/httpapi/ ./internal/contract/ …

  with the Makefile-parsing logic moved into that script (and kept as a Go test
  too, if desired). Alternative of equal size: have the recipe assert the guard
  actually ran, by running `go test -v` and failing unless the guard's name
  appears in a `--- PASS` line.

Acceptance criteria:
  - `make contract-drift` exits non-zero when the recipe carries `-run <regex>`
    for a regex matching NO test in the lane (e.g. `-run 'TestNothingAtAll'`),
    with a message naming the flag.
  - The same holds with a vendored file simultaneously edited in place.
  - The existing reds (M1-M6 above, `-skip`, `-short`, `-tags`) still reproduce.
  - AGENTS.md's wording matches what the control actually enforces.

Tests:
  Extend internal/httpapi/lane_selection_test.go, or the new shell guard, with a
  case that runs the lane's own recipe-check under a `-run` regex selecting
  nothing and asserts a non-zero exit. The harness exists; no new tooling needed.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: the F7 ledger entry should not
  be closed as fully demonstrated until the `-run` case is red.

Challenge:
  The strongest counterargument: F7's stated acceptance was only ever "make
  contract-drift must fail when a vendored file is edited in place and when a
  manifest sha256 is zeroed", and both reproduce RED. Every survivor needs a
  deliberate edit to an owner-reviewed Makefile, and `make ci` still catches the
  drift, so nothing reaches main un-gated. On that reading this is SHOULD, not
  REQUIRED, and the PR closes F7. I chose REQUIRED because the brief listed the
  `-run` red as a required demonstration, and because the PR ships documentation
  asserting a guarantee it does not have — which is the more durable harm.
```

```
FINDING 2: an unreadable or unparseable reject fixture is still counted as
           "correctly rejected", so the guard prints a fixture count it did not earn
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/ci-required-guard.sh:151-171 (the `case`/`*)` reject branch
             and the `test -f` line above it)
  requirements: F8 of docs/evidence/warroom/2026-09-20-vizra-search-pr1-minimal-service-VERIFY.md

Observed:
  The reject branch treats ANY non-zero exit of check-workflows.py as proof the
  fixture was correctly rejected:

      *)
        if ./scripts/check-workflows.py "$fixture" >/dev/null 2>&1; then
          echo "the workflow checker ACCEPTED $fixture, …"
          exit 1
        fi
        ;;

  A checker that cannot READ or PARSE the file also exits non-zero. The guard
  above it does not close this: `test -f "$fixture"` tests existence, not
  readability, while its message says "is not a readable file".

  Reproduced at the verified SHA (uid 501, not root):
      $ chmod 000 scripts/testdata/wf-plain.yml && ./scripts/ci-required-guard.sh
      … (6 fixtures exercised, floor 6)          exit 0
      $ : > scripts/testdata/wf-quoted-key.yml   && ./scripts/ci-required-guard.sh
      … (6 fixtures exercised, floor 6)          exit 0

  The emptied-fixture case is the reachable one: file modes other than the
  executable bit do not survive a git checkout, but an emptied or truncated
  fixture committed in a PR stays emptied in CI.

  The builder's D row ("a fixture stops discriminating -> RED") used a fixture
  rewritten to clean YAML, which the checker ACCEPTS — the one mutation this
  branch does catch.

Failure:
  This is the exact defect F8 named — "the checker errors, and the *) branch
  reads that as correctly rejected" — surviving one level down. A negative
  fixture can be gutted while the guard keeps printing "6 fixtures exercised,
  floor 6", so the line that exists to prove the checker still catches every
  continue-on-error spelling can assert a count it did not earn. The gate that
  is supposed to stop `continue-on-error` reaching a required lane is then
  resting on fixtures that no longer test anything.

Perspective:
  operator, developer

Recommendation:
  Distinguish "rejected" from "could not be read". Smallest change: require the
  fixture to be readable and non-empty before running the checker, and require
  the checker's rejection to be the expected one:

      [ -r "$fixture" ] && [ -s "$fixture" ] || {
        echo "UNUSABLE FIXTURE: '$fixture' is unreadable or empty"; exit 1; }

  Better still, assert on the rejection reason: require the checker's stderr to
  mention continue-on-error, so a parse error is not mistaken for a detection.

Acceptance criteria:
  - `chmod 000` on any reject fixture -> exit 1 with a message naming that file.
  - Emptying any reject fixture -> exit 1 with a message naming that file.
  - Truncating one to invalid YAML -> exit 1 naming that file, distinct from
    "the workflow checker ACCEPTED …".
  - The existing reds A-E and G above still reproduce; baseline still exits 0.

Tests:
  scripts/ci-required-guard.sh is already runnable outside Actions, so the
  demonstration is the script itself; add the two mutations to the PR's
  docs/evidence transcript. No harness change needed.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: none

Challenge:
  The strongest counterargument: F8 as written asked only that a missing fixture
  directory or an empty glob become a named failure, and A-E all reproduce RED,
  so F8 is closed. chmod 000 cannot reach CI through git at all, and emptying a
  fixture is a visible diff in an owner-reviewed path. On that reading this is
  SHOULD. I chose REQUIRED because the verification brief listed "make one
  fixture unreadable" among the reds to reproduce, and because a guard whose
  final line reports a count it did not earn is the same false-positive class
  the PR exists to remove.
```

```
FINDING 3: the Makefile-recipe parser is bypassed by variable indirection,
           GOFLAGS, a duplicate target, an included makefile, or a wrapper script
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/httpapi/lane_selection_test.go:44-70 (contractDriftRecipe),
             :170-190 (the token scan)
  requirements: F7 (hardening beyond its stated acceptance)

Observed:
  contractDriftRecipe reads ../../Makefile, finds the FIRST line beginning
  "contract-drift:", and scans that recipe's whitespace-separated tokens. Each of
  the following left `make contract-drift` at exit 0 with a vendored file
  genuinely edited in place (all reproduced at the verified SHA):

    1. a SECOND `contract-drift:` target appended. make warns "overriding
       commands for target `contract-drift'" and runs the LAST recipe; the
       parser reads the FIRST.
    2. `TESTFLAGS ?= -run=TestNothingAtAll` with the recipe using `$(TESTFLAGS)`
       — the token `$(TESTFLAGS)` is not `-run`.
    3. `GOFLAGS=-run=TestNothingAtAll go test …` — the token is `GOFLAGS=-run=…`,
       which neither equals `-run` nor starts with `-run=`.
    4. the same variable defined in an included makefile (`include drift.mk`).
    5. `go test` moved behind `./scripts/drift-wrapper.sh`. (The recipe then
       contains no "go test", which the parser DOES reject — but only because of
       the literal-string check, and any wrapper whose name contains "go test"
       would pass.)

  `-run` split across a recipe line continuation IS caught: continuations are
  joined before the scan.

Failure:
  The guard reads a textual approximation of the Makefile rather than asking make
  what it will run, so several ordinary make idioms slip past it. Each needs a
  deliberate edit to /Makefile, which CODEOWNERS assigns to @yegamble (advisory
  until the owner ruleset lands), so none of these happens by accident — this is
  hardening, not an open hole in the merged behaviour.

Perspective:
  developer

Recommendation:
  Ask make what it will run instead of parsing the file: derive the recipe with
  `make --dry-run --no-print-directory contract-drift` and scan THAT, which
  resolves variables, includes and duplicate-target overrides in one move. Fold
  this into the same shell guard proposed in FINDING 1 so there is one control,
  not two. Additionally reject a second `contract-drift:` target outright, and
  refuse `GOFLAGS`/`GOTESTFLAGS` anywhere in the resolved recipe.

Acceptance criteria:
  - Each of the five bypasses above makes `make contract-drift` exit non-zero.
  - The resolved-recipe scan still passes on the current, clean recipe.

Tests:
  Extend the same guard. The five mutations are scripted and cheap to keep as a
  table-driven case.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: none

Challenge:
  Every one of these requires someone to deliberately edit an owner-reviewed
  Makefile to defeat a check they know is there — at which point they could
  equally delete the guard test. A guard is meant to stop accident and drift, not
  a determined author, and against accident the current parser is adequate. That
  is why this is SHOULD and not REQUIRED; only the `-run` case (FINDING 1) is
  reachable by an engineer acting in good faith.
```

```
FINDING 4: the plan understates which core api/ files changed between the two pins
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     docs/plans/2026-09-20-vizra-search-pr2-revendor.md, § "What changed
             in the contract" ; mirrored in docs/evidence/pr2/README.md
  requirements: none

Observed:
  The plan says core's diff between 2b9c540 and 415a6d1 is "two additive prose
  insertions and nothing else (2 files changed, 9 insertions(+), no deletions)".
  Restricted to the two VENDORED files that is exactly right. Core's api/
  directory actually changed in three files:

      29  0  api/README.md
       1  0  api/search-hmac-testvectors.json
       8  0  api/search-internal.openapi.yaml

  api/README.md is not vendored here, so nothing follows from it, and the
  conclusion (additive prose only, no code forced) is unaffected and confirmed.

Failure:
  A reader checking the claim with `git diff 2b9c540 415a6d1 -- api/` gets three
  files and 38 insertions, not two and nine, and has to work out why before
  concluding the evidence is sound.

Perspective:
  developer

Recommendation:
  Say "two files changed among the vendored pair" and note api/README.md changed
  additively but is not vendored.

Acceptance criteria:
  The sentence names the scope of the count.

Tests:
  none — documentation.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: none

Challenge:
  This changes no conclusion and costs a reviewer one command. It is a NIT and
  should not hold the PR.
```

---

## Verdict

**FAIL.**

Reproduced and passing: provenance (byte-identical to core `main`@`415a6d1`, confirmed three ways,
manifest correct, `source_ref: main`, 40-char commit); the additive-only contract diff with no
schema/path/status/security/number moved; 5 + 24 vector parity across both repos; the published-key
refusal including one-character drift in both directions and the harmless new `key_utf8_warning`;
no test weakened, deleted, renamed or skipped (162→163, one file added); `make ci` green with
**321 pass events and 0 skips**, matching the builder's claim exactly; all 12 CI check-runs green
on `1772270` with `ci-required` present and the manifest matching the jobs that actually ran.

Not reproduced — the two reds the brief required:

1. **FINDING 1 (REQUIRED)** — putting `-run` back on the lane does **not** go red when the regex
   misses the guard; `make contract-drift` exits 0 with a vendored file edited in place.
2. **FINDING 2 (REQUIRED)** — an unreadable, and more importantly an **emptied**, reject fixture is
   still counted as "correctly rejected"; the guard exits 0 printing `6 fixtures exercised, floor 6`.

Both are residuals of the exact class the PR exists to remove — a check reporting green without
having checked — and both have fixes of a few lines. The underlying F7 and F8 defects as originally
stated **are** closed, so the chair may reasonably judge this a small fix round rather than a
rejection; that call is the chair's, not mine.

FINDING 3 (SHOULD) and FINDING 4 (NIT) are reported for completeness and do not drive the verdict.

PASS would not have been a merge or a VERIFIED ledger entry; FAIL is likewise only this verifier's
reproduction result. Head SHA `17722700abf264813b7fa2f659e9cdccc922bfb7` had not moved at the time
of writing.

*Verifier scratch clones under `…/scratchpad/vfy-pr2/` were deleted after this record was written.
No file outside this evidence record was created or modified in the meta repo, and nothing was
pushed to any repository.*
