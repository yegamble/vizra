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

---
---

# Re-verification at `e219fc6`

**Verdict: PASS.** Findings 1, 2 and 4 **CLOSED**. Finding 3 **OPEN (narrowed, non-blocking)**.
Two new non-blocking findings (5, 6).

| field | value |
|---|---|
| Head SHA verified | `e219fc6b9f64d04d2adde87b830b2e9a4f388b5d` (unchanged before and after) |
| Previous verdict | FAIL at `1772270` |
| Ancestry | `1772270` **is** an ancestor of `e219fc6`; two commits since: `562bb99`, `e219fc6` |
| Verifier checkout | fresh clone, `…/scratchpad/vfy-r2/sc` (deleted after) |
| Environment | darwin/arm64, go1.26.2, **GNU Make 3.81**, uid 501; 16 GiB free |

## 0. Provenance carries over — not re-verified, and it did not need to be

`git diff --stat 1772270..e219fc6 -- api/` is **empty**. Blob ids at `e219fc6` are
`848503cca45d…` and `6548d87e1811…` — identical to core `main`@`415a6d1` as established above,
and `api/CONTRACT-SOURCE.json` is byte-unchanged. **The provenance section of this record stands
in full for `e219fc6`.**

## 1. Lanes at `e219fc6`

| command | exit | result |
|---|---|---|
| `make ci` | **0** | all eight lanes green, 23.3 s |
| `make contract-drift` | **0** | `contract-drift lane: 4 package(s) selected with no test-selecting flag` / `contract-drift: 315 tests ran across 4 package(s), 0 failures, none deselected` |
| `make test-noskip` | **0** | **338 pass events, 0 skips** |
| `make tidy-check` | **0** | `tidy-check: tidy` |
| `./scripts/ci-required-guard.sh` | **0** | `6 fixtures exercised, floor 6` |

Both builder claims reproduce **exactly**: 338 / 0 skips, and the 315-test contract-drift line
verbatim. CI runs `make contract-drift` directly (`.github/workflows/ci.yml:87-88`), so the lane
I exercised is the lane that gates.

## 2. FINDING 1 — **CLOSED**

The control now runs as recipe steps outside `go test`: `contract-drift-guard.py recipe` before,
`… ran <report>` after, with `go test … || true` between (the `ran` step is the pass/fail
authority and does check failures — verified at P17, where a drifted file still went red).

My exact round-1 case, re-run with an in-place edit of `api/search-internal.openapi.yaml`
underneath:

```
recipe: go test -count=1 -json -run 'TestVerifier' ./internal/httpapi/ … || true
$ make contract-drift
CONTRACT-DRIFT LANE REFUSED: the contract-drift lane carries -run.
exit 2   ← RED
```

Every additional attack on the flag surface is refused:

| probe | `make contract-drift` (all with a real vendored-file edit underneath) |
|---|---|
| P1 `-run 'TestVerifier'` — my round-1 case | **RED** — `carries -run` |
| P8 `-count=0` | **RED** — `unexpected flag '-count=0'` |
| P9 `-list .*` | **RED** — `unexpected flag '-list'` |
| P10 `-run` via `-args` | **RED** — `carries -args` |
| P11 package path matching nothing | **RED** — coverage check names the dropped package |
| P20 a listed package that runs **zero** tests | **RED** — `package … ran ZERO tests` |

The allowlist design (`ALLOWED_FLAGS = {-count=1, -json}`, everything else refused by name) is the
right shape: a flag invented after the guard was written cannot quietly deselect a guard.

## 3. FINDING 3 — **OPEN (narrowed)**. 4 of my 5 survivors closed

| round-1 survivor | now |
|---|---|
| `-run` in `$(TESTFLAGS)` | **RED** — `carries -run` |
| `GOFLAGS=-run=…` as a recipe env prefix | **RED** — `prefixed with the environment assignment` |
| `GOFLAGS=-run=…` **exported in the environment** | **RED** — `GOFLAGS in the environment carries -run` |
| `-run` in an **included** makefile | **RED** — `carries -run` |
| `go test` behind a **wrapper script** | **RED** — `the lane runs './scripts/w.sh' instead of go test` |
| **a duplicate `contract-drift:` target** | **still SURVIVES — exit 0** (see FINDING 5) |

Asking `make --dry-run` instead of parsing the Makefile text closed four of five in one move.

### Attacks on the guard itself

| probe | `make contract-drift` | caught by the Go shape test? |
|---|---|---|
| P12 the `recipe` guard line deleted | **RED** (shape test fails; `ran` surfaces it) | yes |
| P13 the `ran` guard line deleted | **RED** — `LAST command must be … ran <report>` | yes |
| P14 **both** guard lines deleted | SURVIVOR exit 0 | **yes** — `TestTheContractDriftLaneIsGuardedFromOutsideGoTest` fails |
| P15 `-` prefix on the guard lines | SURVIVOR exit 0 | **NO — 0 shape failures** |
| P16 `\|\| true` on the guard lines | SURVIVOR exit 0 | **NO — 0 shape failures** |
| P17 `.ONESHELL:` added | **RED** — drift still caught | n/a |
| P18 `SHELL := /usr/bin/true` | SURVIVOR — and `make test`, `test-noskip`, `ci` **all** exit 0 | no |
| P19 `make -i` / `MAKEFLAGS=-i` | SURVIVOR | n/a — CI runs plain `make contract-drift`, so this needs a workflow edit |

**P14 is the builder's documented residual and it holds as documented**: two edits, and the shape
test goes red on its own. **P15 and P16 are not** — see FINDING 6.

P18 (`SHELL :=` pointed at a no-op) disables every make-based lane at once. That is a generic
property of any make-driven gate, is equally true of the base branch, and is not a regression from
this PR; recorded as a limit of the design, not a finding against it.

## 4. Make-version portability — **handled, and robust for the right reason**

`562bb99` matched literal markers `("overriding commands for target", "ignoring old commands for
target")` — make 3.81 wording only, which is why it was red in CI on ubuntu (make 4.x).
`e219fc6` replaces them with
`re.compile(r"(overriding|ignoring old)\s+(commands|recipe)\s+for\s+target", re.I)`.

Tested directly against all four wordings:

```
new:MATCH  old:MATCH   overriding commands for target   (make 3.81)
new:MATCH  old:MISS    ignoring old commands for target (make 3.81)
new:MATCH  old:MISS    overriding recipe for target     (make 4.x)
new:MATCH  old:MISS    ignoring old recipe for target   (make 4.x)
```

I confirmed the 3.81 wording empirically on this machine. **The make-4.x path I can only judge
from the regex and the CI log** — no make 4.x is installed here; the builder states the same
limitation in `docs/evidence/pr2/F7-round2-make-version-portability.txt` rather than implying they
tested it.

**Is warning-text parsing robust?** The regex itself is not the durable part — a future wording
would miss it. What makes it acceptable is the **catch-all immediately after**: any line containing
`warning:` in make's stderr while resolving the lane is refused outright. That fails closed on
wordings nobody anticipated, which is the correct design. The coordinator's suggested alternative —
compare the dry-run recipe against the expected shape — is *already* implemented as
`check_structure`. So the fragility is **not** in the wording. It is that both checks live inside a
recipe step the duplicate target removes (FINDING 5).

## 5. FINDING 2 — **CLOSED**

`check-workflows.py` now returns 0 clean / 1 VIOLATION / **2 UNEVALUABLE**, the guard requires
exit **1 exactly** from a reject fixture, checks readability and non-emptiness *before* running the
checker, and each reject fixture declares the rule it must trip (`fixture|at|key|value`) which must
appear verbatim in the checker's `VIOLATION` line.

All eight required reds are **named failures**:

| probe | result |
|---|---|
| unreadable **reject** fixture | **RED** — `UNUSABLE FIXTURE: … exists but is not readable.` |
| unreadable **accept** fixture | **RED** — `UNUSABLE FIXTURE: …` |
| **emptied** reject fixture | **RED** — `UNUSABLE FIXTURE: … is empty.` |
| **invalid YAML** in a reject fixture | **RED** — `UNEVALUABLE FIXTURE: … (exit 2). Nothing was checked.` |
| fixture edited to trip a **different** rule | **RED** — `WRONG RULE TRIPPED: … not for the rule it declares` |
| fixture made **valid** | **RED** — `the workflow checker ACCEPTED …` |
| fixture **directory missing** | **RED** — `MISSING FIXTURES: …` |
| **glob empty** | **RED** — `MISSING FIXTURE: …` named one by one |

Both round-1 survivors (unreadable reject fixture; emptied fixture) are now red by name. The three
extra probes requested:

- a fixture tripping **two** rules (declared + another) → exit 0. **Correct**, not a defect: the
  declared rule is still tripped, so the fixture still proves what it was written to prove.
- a new fixture with **no declaration** that is still rejected → exit 0, `7 fixtures exercised,
  floor 6`. **Correct** — the floor is a minimum. A new undeclared fixture that is **clean** is
  **RED** (`ACCEPTED …`), so a decorative fixture cannot be added.
- a fixture's **declaration row removed** from `reject_fixtures` → exit 0, floor silently drops to
  5. See FINDING 7.

## 6. Tests since `1772270` — **strengthened, nothing weakened**

Census **163 → 168**. One function removed —
`TestTheContractDriftLaneSelectsEveryVendoredFileGuard` — and six added.

**Ruling on the rewrite: acceptable, and an improvement.** The removed function was *added by this
same PR* (it does not exist at base `581d79d`), so **no pre-existing test was touched**. Its single
property was split into three, and three self-tests of the new guard were added:

```
TestTheContractDriftLaneIsGuardedFromOutsideGoTest
TestTheContractDriftLaneCarriesNoTestSelectingFlag
TestTheContractDriftLaneRunsEveryPackageHoldingAVendoredFileGuard
TestTheLaneGuardAcceptsAWellFormedLane          (positive control)
TestTheLaneGuardRefusesEveryKnownBypass         (negative control)
TestTheLaneGuardRefusesAFlagFromAnIncludedMakefile
```

Against base `581d79d` the census is 162 → 168 with **zero** removals. No `t.Skip`,
`testing.Short` or build-tag exclusion added. No production Go changed.

## 7. CI on `e219fc6` — **PASS**

`total_count: 12`, every check-run `completed` / `success`: fmt, vet, echo-containment, build,
contract-drift, test, test-noskip, tidy-check, govulncheck, docker-build, ci-required,
GitGuardian. All 10 manifest lanes executed; the manifest matches the jobs that ran; `ci-required`
ran on this SHA.

The `contract-drift` job log on `e219fc6` shows **both** guard steps with real counts:

```
./scripts/contract-drift-guard.py recipe
contract-drift lane: 4 package(s) selected with no test-selecting flag (internal/config, internal/contract, internal/hmacauth, internal/httpapi)
./scripts/contract-drift-guard.py ran .contract-drift-report.json
contract-drift: 315 tests ran across 4 package(s), 0 failures, none deselected
```

315 matches my local run exactly.

## 8. Claims audit — **FINDING 4 CLOSED**, one sentence now false

`docs/evidence/pr2/README.md` now states correctly that core's `api/` changed in **three** files
and that only two are vendored — my round-1 NIT is fixed. The README also voluntarily records that
round 1's `-run` demo "went red for an accidental reason", which is an unusually honest correction.

One sentence is now false: `scripts/contract-drift-guard.py:32-36` and `AGENTS.md:330` state that
escaping "takes a second deliberate edit — the shape test goes red on its own". True for P14 and
P2; **false for P15 and P16** (FINDING 6).

---

## Findings at `e219fc6`

```
FINDING 5: a duplicate `contract-drift:` target that omits the guard is a
           one-edit bypass; the duplicate-detection cannot run to catch it
Severity:    SHOULD
Confidence:  high
Status:      round-1 FINDING 3, item 1 — still OPEN (narrowed)

Affected:
  repo:      vizra-search
  files:     scripts/contract-drift-guard.py:126-148 (DUPLICATE_TARGET_RE,
             check_make_warnings) ; Makefile:92-96
  requirements: F7

Observed:
  make runs the LAST definition of a target. A second `contract-drift:` target
  therefore REPLACES the recipe — including the two guard lines — so the guard
  is never invoked and its duplicate-detection never executes:

      $ cat >> Makefile <<'EOF'
      .PHONY: contract-drift
      contract-drift:
      	go test -count=1 -json -run TestNothingAtAll $(DRIFT_PKGS) > $(DRIFT_REPORT) || true
      EOF
      $ printf '\n# UNAUTHORISED EDIT\n' >> api/search-internal.openapi.yaml
      $ make contract-drift
      Makefile:152: warning: overriding commands for target `contract-drift'
      go test … -run TestNothingAtAll … || true
      exit 0                                   ← contract drifted, lane green

  The builder's RED 5 demonstration appended a duplicate that KEPT the guard
  line, so `contract-drift-guard.py recipe` ran and refused it. That is the
  same narrowing as round 1's self-selecting `-run` regex: the transcript is
  honest about what it did, but the natural form of the bypass — a duplicate
  that simply supplies its own recipe — is not covered.

  It IS caught one lane over: an unfiltered `go test ./internal/httpapi/` fails
  TestTheContractDriftLaneIsGuardedFromOutsideGoTest and
  TestTheContractDriftLaneCarriesNoTestSelectingFlag, so CI's required `test`
  and `test-noskip` lanes go red and nothing reaches main.

Failure:
  `make contract-drift` reports success with the vendored contract edited in
  place. That is F7's original complaint — the drift dies only in a broader
  lane, not the one whose name says it checks drift — reachable now only by a
  deliberate Makefile edit rather than by an accidental rename.

Perspective:
  developer, operator

Recommendation:
  No in-recipe control can survive its own recipe being replaced, so put the
  duplicate check where it still runs: have `check_make_warnings` keep the
  catch-all (it is sound), and add a cheap text scan — a second line matching
  `^contract-drift:` in the Makefile — to the Go shape test, which already
  catches this case and is the layer that actually bites. Then correct the
  README row and AGENTS.md to say the duplicate target is caught by the shape
  test in `test`/`test-noskip`, not by the lane guard.

Acceptance criteria:
  - A duplicate `contract-drift:` target that omits the guard makes at least one
    REQUIRED lane red, and the documentation names which lane.
  - The guard's own duplicate-detection keeps working for a duplicate that does
    invoke it (already true).

Tests:
  internal/httpapi/lane_selection_test.go — add the omit-the-guard duplicate to
  TestTheLaneGuardRefusesEveryKnownBypass. The harness exists.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: none

Challenge:
  The strongest counterargument: `make contract-drift` is not a merge gate on
  its own — `ci-required` is, and it requires `test` and `test-noskip`, both of
  which are red here. So no drifted contract can merge, and this is cosmetic
  about which lane reports it. I keep it at SHOULD rather than dropping it
  because the whole point of F7 was that the lane named for drift must be the
  lane that catches drift.
```

```
FINDING 6: `-` or `|| true` on a guard recipe line silently disarms the lane in
           ONE edit, and the shape test does not notice — contradicting the
           documented "escaping needs two edits"
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/contract-drift-guard.py:32-36 (the claim),
             :247-270 (check_structure) ; AGENTS.md:330 ;
             internal/httpapi/lane_selection_test.go (shape test)
  requirements: F7

Observed:
  Two one-edit mutations leave `make contract-drift` at exit 0 with a vendored
  file edited in place, AND leave the Go shape test green (0 shape-test
  failures, measured):

    P15   -./scripts/contract-drift-guard.py recipe
          -./scripts/contract-drift-guard.py ran $(DRIFT_REPORT)
    P16   ./scripts/contract-drift-guard.py recipe || true
          ./scripts/contract-drift-guard.py ran $(DRIFT_REPORT) || true

  For P15 the reason is precise and worth stating: `make --dry-run` PRINTS THE
  COMMAND WITHOUT THE `-` PREFIX. Both check_structure and the shape test read
  the dry-run output, so the `-` is invisible to both while make silently
  ignores the step's exit status:

      $ make --dry-run --no-print-directory contract-drift
      ./scripts/contract-drift-guard.py recipe            ← the '-' is gone
      go test -count=1 -json … || true
      ./scripts/contract-drift-guard.py ran .contract-drift-report.json

  For P16 the `|| true` IS visible in the dry-run, but check_structure only
  asserts `commands[0].startswith(GUARD)` and `" recipe" in commands[0]`, both
  of which a trailing `|| true` satisfies.

  Contrast P14 (both guard lines deleted), where the shape test DOES fail — the
  documented residual holds there, and only there.

Failure:
  The guard still prints its REFUSED message, but the lane exits 0, so the
  failure is invisible to CI and to anyone reading the exit code. The
  documentation in scripts/contract-drift-guard.py:32-36 and AGENTS.md:330 tells
  the reader escaping "takes a second deliberate edit — the shape test goes red
  on its own". For these two mutations that is not true, and a reader relying on
  that sentence would believe the lane is protected when it is not. As with
  FINDING 5, CI's `test`/`test-noskip` lanes still catch the drift, so nothing
  merges.

Perspective:
  developer, operator

Recommendation:
  The dry-run cannot see `-`, so this one needs the Makefile TEXT. Smallest
  change: in the shape test (which already reads the Makefile), reject a
  contract-drift recipe line that begins with `-`, `@-`, or ends with `|| true`
  / `|| :`. Tighten check_structure at the same time so a guard command with
  anything appended after it is refused rather than prefix-matched.
  Then either make the "two edits" sentence true, or soften it to name what is
  actually guaranteed.

Acceptance criteria:
  - `-` prefixed on either guard line -> at least one REQUIRED lane red,
    naming the line.
  - `|| true` appended to either guard line -> same.
  - P14 (both lines deleted) still red in the shape test.
  - The sentence in scripts/contract-drift-guard.py and AGENTS.md matches what
    is enforced.

Tests:
  internal/httpapi/lane_selection_test.go — add both spellings to
  TestTheLaneGuardRefusesEveryKnownBypass.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: none

Challenge:
  The strongest counterargument: anyone typing `-` in front of the guard line is
  deliberately disarming a control they can see, in an owner-reviewed file, and
  no in-recipe check can stop that — `SHELL := /usr/bin/true` (P18) disables
  every lane in this repository with one edit and always could. On that reading
  the only real defect is the documentation sentence, and the code needs no
  change. I keep it at SHOULD because the fix is three lines and because the
  claim is currently load-bearing for reviewers.
```

```
FINDING 7: deleting a fixture's declaration row lowers the fixture floor
           silently, from 6 to 5
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/ci-required-guard.sh (the `reject_fixtures` table and
             `floor_count`)
  requirements: F8

Observed:
  floor_count is computed from the same `reject_fixtures` table that supplies
  the per-fixture rule declarations. Removing one row removes the fixture from
  the floor, removes its rule check, and lowers the floor in one edit:

      $ # delete the wf-quoted-key.yml row from reject_fixtures
      $ ./scripts/ci-required-guard.sh
      … (6 fixtures exercised, floor 5)     exit 0

  The fixture is still exercised through the glob and must still be rejected,
  so a fixture that stops being rejected at all is still caught; what is lost is
  the binding to the RULE it must trip.

Failure:
  The same "the floor lives in the file it guards" limitation the script already
  acknowledges for lanes, now applying to fixtures. It is visible in the output
  (`floor 5`) but nothing fails.

Perspective:
  developer

Recommendation:
  Make the floor a literal, e.g. `expected_floor=6` asserted against
  `floor_count`, so lowering the table without lowering the literal is a named
  failure — the same shape as the lane floor.

Acceptance criteria:
  Removing any row from `reject_fixtures` makes the guard exit non-zero.

Tests:
  The script is runnable outside Actions; add the mutation to the round-2
  transcript.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: none

Challenge:
  CODEOWNERS covers /scripts/ under the `*` rule, the change is visible in the
  diff and in the output line, and the fixture is still required to be rejected.
  This is a NIT and should not hold the PR.
```

---

## Verdict at `e219fc6`: **PASS**

| round-1 finding | status |
|---|---|
| FINDING 1 — `-run` deselects the guard that forbids `-run` | **CLOSED** — my exact case is RED; the control now runs outside `go test`; every flag probe refused |
| FINDING 2 — unevaluable fixture counted as "correctly rejected" | **CLOSED** — all eight required reds are named failures |
| FINDING 3 — Makefile-parser bypasses | **OPEN, narrowed** — 4 of 5 closed; the duplicate target survives the lane (FINDING 5), non-blocking |
| FINDING 4 — core `api/` file count in the plan | **CLOSED** — README now states it correctly |

Both findings that drove the round-1 FAIL are closed, and closed properly rather than patched: the
control was moved out of `go test`'s selection space, it asks `make --dry-run` instead of parsing
text, it checks the environment, and it verifies afterwards that the packages it claims to cover
actually ran tests. `make ci` is green with 338 pass events and 0 skips; `contract-drift` reports
315 tests across 4 packages with none deselected; all 12 CI check-runs are green on this SHA with
`ci-required` present and the guard's two lines visible in the job log with real counts.

No blocking finding remains. FINDINGS 5, 6 and 7 are SHOULD/NIT hardening: every one needs a
deliberate edit to an owner-reviewed file, and in every case CI's required `test` and `test-noskip`
lanes still catch a drifted contract, so no drifted contract can merge.

**One item I would put to the chair as a merge condition rather than a follow-up**: the sentence in
`scripts/contract-drift-guard.py:32-36` and `AGENTS.md:330` claiming escaping "takes a second
deliberate edit" is false for the `-` and `|| true` spellings (FINDING 6). It is a documentation
correction of a few words, and leaving a stated guarantee stronger than the control is the species
of claim that produced the round-1 FAIL.

PASS is not a merge and does not make the ledger entry VERIFIED — the chair records those. Head SHA
`e219fc6b9f64d04d2adde87b830b2e9a4f388b5d` had not moved at the time of writing.

*Verifier scratch clone `…/scratchpad/vfy-r2/` was deleted after this record was written. Nothing
outside this evidence file was created or modified in the meta repo, and nothing was pushed.*

---
---

# Re-verification at `7babbd3`

**Verdict: PASS.** Findings **5, 6, 7 all CLOSED**. **The merge condition is still OPEN** — two
sentences in the shipped prose overstate the guarantee, falsified by two one-line Makefile edits I
measured. Docs-only; the controls themselves are verified.

| field | value |
|---|---|
| Head SHA verified | `7babbd396a1fcf1a2940c45a8eeeb9d9d2854331` (unchanged before and after) |
| Ancestry | `e219fc6` **is** an ancestor; one commit since: `7babbd3` |
| `api/` since `e219fc6` | **byte-unchanged** — blob ids still `848503cca45d…` / `6548d87e1811…`, `CONTRACT-SOURCE.json` `2f83646e…`. **Provenance stands.** |
| Environment | darwin/arm64, go1.26.2, GNU Make 3.81, uid 501; 14 GiB free |

## 1. Counts — both claims reproduce exactly

| command | exit | result |
|---|---|---|
| `make ci` | **0** | all lanes green |
| `make contract-drift` | **0** | **`324 tests ran across 4 package(s), 0 failures, none deselected`** |
| `make test-noskip` | **0** | **347 pass events, 0 skips** |
| `./scripts/ci-required-guard.sh` | **0** | `6 fixtures exercised, floor 6` + `workflow anchor: …` |

## 2. FINDINGS 5 and 6 — **CLOSED**, read across four signals

Every mutation applied with python3 and the file's sha256 printed before/after, so a mutation that
failed to apply could not masquerade as a pass. Each carries an in-place edit of
`api/search-internal.openapi.yaml` underneath. `CI job` = the anchor step, then `make contract-drift`.

| mutation | make lane | out-of-make guard | **CI job** | `go test ./internal/httpapi/` |
|---|---|---|---|---|
| baseline (no mutation, no drift) | 0 | 0 | 0 | 0 |
| **F6a** `-` on the `recipe` guard line | **2** | **1** | **1** | **1** |
| **F6b** `-` on the `ran` guard line | **2** | **1** | **1** | **1** |
| **F6c** `\|\| true` on the `recipe` guard line | **2** | **1** | **1** | **1** |
| **F6d** `\|\| true` on the `ran` guard line | **2** | **1** | **1** | **1** |
| **F5** duplicate target **replacing** the recipe, no guard lines | 0 | **1** | **1** | **1** |

**FINDING 6 is closed outright** — red at *every* signal including the make lane, because `recipe`
now reads the Makefile **text** (`check_makefile_text`), which is the only place a `-` is visible;
`make --dry-run` prints the command without it, exactly as the guard's own comment says.

**FINDING 5 is closed at the job**, which is what the finding asked for. `make contract-drift`
alone remains green for a duplicate target — the guard cannot run when the duplicate has replaced
the recipe — and that limit is now **disclosed accurately** in the guard docstring and AGENTS.md.

### The workflow anchor

| mutation to `.github/workflows/ci.yml` | `guard workflow` | `ci-required-guard.sh` | `go test ./internal/httpapi/` |
|---|---|---|---|
| anchor step **deleted** | **1** — `does not run … as its own step` | **1** | **1** |
| anchor made **conditional** (`if:`) | **1** — `is conditional (\`if\`), so it can be skipped` | **1** | **1** |
| anchor marked **continue-on-error** | **1** — `carries \`continue-on-error\`` | **1** | **1** |
| anchor **moved after** `make contract-drift` | **1** — `runs AFTER \`make contract-drift\` … must run first` | **1** | **1** |

Three independent signals on every one. **No case where all signals were green.**

## 3. Transcript spot-check — the `perl` delimiter trap

The two rows most exposed to the reported `perl -0pi -e "s|…|…|"` collision are the `|| true`
rows, since the replacement text itself contains `|`. I re-applied both mutations myself with
python3, printing the file digest before and after:

```
mutation applied: 5dfbbeeea3e2 -> d16173e55485   (|| true on the recipe guard line)
mutation applied: 5dfbbeeea3e2 -> c8bafe32973e   (|| true on the ran guard line)
```

Both genuinely changed the file, and both went red at all four signals — matching the new
transcript. The `-`-prefix rows likewise applied and went red. The transcript's `L` / `W` / `JOB`
columns agree with my measurements, and its GREEN 0 baseline (`324 tests`) matches mine.

I hit the same class of failure myself: two of my own workflow mutations silently did not apply
because I guessed the step's name wrong (`the lane's own shape check` vs the real
`the lane's own shape, checked outside make`). My harness printed `MUTATION DID NOT APPLY` and I
re-ran them with the exact text — which is the whole point of the builder's correction, and it is
the right correction.

## 4. FINDING 7 — **CLOSED**

`expected_reject_fixtures=5` is pinned and compared against the declared rows. Deleting one row:

```
FIXTURE FLOOR CHANGED: 4 reject-fixture rule(s) are declared;
  expected_reject_fixtures says 5.
exit=1
```

## 5. Tests since `e219fc6` — nothing weakened

Census **168 → 170**; **zero removed**; two added (`TestTheLaneGuardIsAnchoredInTheWorkflow`,
`TestThisRepositoryPassesItsOwnLaneGuard`). `internal/httpapi/lane_selection_test.go` `+87 −2`, the
only test file touched. No `t.Skip`/`testing.Short` added. Against base `581d79d`: 162 → 170, zero
removals.

## 6. CI on `7babbd3` — **PASS**

12 check-runs, all `success`; all 10 manifest lanes ran; `ci-required` on this SHA. The
`contract-drift` job log shows the anchor as **its own step before make**:

```
contract-drift | the lane's own shape, checked outside make | Run ./scripts/contract-drift-guard.py recipe
contract-drift | the lane's own shape, checked outside make | contract-drift lane: 4 package(s) selected with no test-selecting flag (…)
```

and `ci-required` logs the anchor assertion:

```
workflow anchor: .github/workflows/ci.yml:jobs.contract-drift runs `./scripts/contract-drift-guard.py recipe`
unconditionally at step 2, before `make contract-drift` at step 3
```

CI runs ubuntu-24.04 (GNU make 4.x), so the make-4 path is exercised green there; I can still only
judge it from that log, not locally.

## 7. THE MERGE CONDITION — **OPEN**

Most of the new prose is exact, and `cmd_workflow`'s own docstring is exactly right:

> "a single Makefile edit that replaces or disarms that line — a duplicate target supplying its own
> recipe, `SHELL := /usr/bin/true`, `MAKEFLAGS` — removes the check along with the lane"

But the headline claim, in the module docstring and repeated in `AGENTS.md`, contradicts it — see
FINDING 8. Every other sentence I checked is true as written, including the duplicate-target
residual and the "second file, second diff" description of the ci.yml path.

---

```
FINDING 8: the shipped guarantee "what one edit to /Makefile can no longer do"
           is falsified by two one-line Makefile edits, and the residual's
           stated backstop does not hold
Severity:    REQUIRED  (documentation accuracy; no code change needed)
Confidence:  high
Status:      the round-2 merge condition, still OPEN

Affected:
  repo:      vizra-search
  files:     scripts/contract-drift-guard.py:56-58 and :60-63 (module docstring)
             AGENTS.md (the "What one edit to /Makefile can no longer do" and
             "What is not covered" paragraphs)
  requirements: F7

Observed:
  Claim A, in both files:
    "What one edit to /Makefile can no longer do: leave the `contract-drift` CI
     job green with a vendored file edited in place."
  Claim B, the disclosed residual:
    "`SHELL := /usr/bin/true` … makes every recipe a no-op, so `make
     contract-drift` and the job built on it go green. The drift is still
     caught, because `test` and `test-noskip` run `go test` directly."

  Measured at this SHA, each a SINGLE line changed in /Makefile, each with a
  vendored file edited in place, mutation verified by sha256:

    SHELL := /usr/bin/true    CI job = 0   make test = 0   make test-noskip = 0
    MAKEFLAGS += -i           CI job = 0   make test = 0   make test-noskip = 0

  Claim A is therefore false — twice, and `MAKEFLAGS += -i` is not named as a
  residual anywhere outside cmd_workflow's docstring.

  Claim B's backstop is also false. CI does not run `go test` directly:
  .github/workflows/ci.yml runs `- run: make test` and `run: make test-noskip`.
  Both are make recipes, so a SHELL override or `MAKEFLAGS += -i` no-ops them
  too. Only a direct `go test ./internal/httpapi/` (which nothing in CI runs)
  goes red. `.SHELLFLAGS` neutering, by contrast, IS caught (exit 2 everywhere).

Failure:
  AGENTS.md is the engineering contract. It currently tells a reviewer that no
  single Makefile edit can leave the drift lane green, and that `test` and
  `test-noskip` backstop the one disclosed exception. A reviewer applying that
  rule would under-weight exactly the two one-line diffs that disable every
  required lane at once. This is the "unsupported readiness claim" AGENTS.md
  itself says to hunt, and it is the same species of overstatement that produced
  the round-1 FAIL and the round-2 merge condition.

  Scope, stated plainly: the underlying exposure is generic to any make-driven
  gate, is equally true of the base branch, and is NOT a regression introduced
  by this PR. What is wrong is only the claim about it.

Perspective:
  developer, operator

Recommendation:
  Documentation only — no code change, and no re-verification of the controls.
  Replace Claim A with what was actually measured, e.g.: "No single Makefile
  edit to the `contract-drift` recipe itself — a `-` prefix, `|| true`, or a
  duplicate target — can leave the CI job green with a vendored file edited in
  place." Then extend the residual list to say that a `SHELL` override or
  `MAKEFLAGS += -i` no-ops every recipe in the repository, that CI invokes
  `test` and `test-noskip` THROUGH make so they are no-opped too, and that the
  only backstop is human review of the Makefile diff under CODEOWNERS —
  advisory until the owner's ruleset exists.

Acceptance criteria:
  - No sentence in scripts/contract-drift-guard.py, AGENTS.md, the Makefile
    comments or docs/evidence/pr2/README.md asserts a guarantee that
    `SHELL := /usr/bin/true` or `MAKEFLAGS += -i` falsifies.
  - The residual paragraph names both, and does not claim `test`/`test-noskip`
    catch them.
  - Verifiable by reading the two paragraphs; no lane needs re-running.

Tests:
  None required — prose. If the team wants it enforced, the smallest mechanical
  option is a `contract-drift-guard.py` text check refusing a `SHELL`
  assignment or `MAKEFLAGS` override anywhere in the Makefile, which would make
  Claim A true rather than merely corrected; that is a larger change and I do
  not recommend it as a condition of this PR.

Cross-repo implications:
  core: none | user: none | search: this PR | meta: AGENTS.md wording only

Challenge:
  The strongest counterargument: the exposure is disclosed in the same file, in
  cmd_workflow's docstring, in the correct form; the headline sentence is a
  topic sentence immediately qualified by "Measured for `-`, `|| true`, and a
  duplicate target"; nobody can stop an owner editing their own Makefile; and
  the real engineering — three findings closed, verified across four signals —
  is done. On that reading this is a NIT and the PR should merge. I keep it at
  REQUIRED for one reason only: the chair made "every sentence exactly true" the
  explicit merge condition for this round, and two sentences are not.
```

---

## Verdict at `7babbd3`: **PASS**, with the merge condition OPEN

| item | status |
|---|---|
| FINDING 5 — duplicate target replacing the recipe | **CLOSED** — red at the CI job and in `test` via the out-of-make anchor; the make-lane-only limit is now disclosed accurately |
| FINDING 6 — `-` / `\|\| true` on a guard line | **CLOSED** — red at all four signals, including the make lane |
| FINDING 7 — fixture floor | **CLOSED** — `FIXTURE FLOOR CHANGED`, exit 1 |
| **Merge condition — every sentence exactly true** | **OPEN** — FINDING 8 |

The engineering is verified and is genuinely good: the control is anchored outside make, asserted
from two independent places (`ci-required-guard.sh` and a Go test), the Makefile-text checks close
the `-` blind spot that no dry-run scan could see, and all four workflow-anchor attacks are red on
three signals each. Counts reproduce exactly (324 / 347 / 0 skips), CI is green on this SHA with
the anchor visible in both job logs, and no test was weakened, deleted, renamed or skipped.

What remains is two sentences. Under the war-room merge rule ("no blocking specialist finding is
open"), FINDING 8 blocks merge until they are corrected — but it is docs-only: **the chair can
clear it by reading the corrected paragraphs; no lane or demonstration needs re-running, and no
further verification round is required from me.**

PASS is not a merge and does not make the ledger entry VERIFIED — the chair records those. Head SHA
`7babbd396a1fcf1a2940c45a8eeeb9d9d2854331` had not moved at the time of writing.

*Verifier scratch clone `…/scratchpad/vfy-r3/` was deleted after this record was written. Nothing
outside this evidence file was created or modified in the meta repo, and nothing was pushed.*
