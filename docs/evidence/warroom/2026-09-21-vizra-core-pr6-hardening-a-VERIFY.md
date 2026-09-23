# Independent verification — vizra-core PR #6, "hardening sweep A"

**Verdict: PASS**, with four non-blocking findings (one REQUIRED-on-disclosure,
three SHOULD/NIT) that the chair should record rather than merge away.

| | |
|---|---|
| PR | https://github.com/yegamble/vizra-core/pull/6 |
| Head SHA verified | `f56dc03a06533bf0bbf057eb74f62ffd47aafc50` (unchanged at verdict time; `updated_at` 2026-09-21T05:52:26Z) |
| Base | `main` at `c043df72f06cc7b5d7237a12d2be4dac25fa788e` |
| Diff | 83 files, +3554 −23 |
| Verifier | independent; did not write any of this code |
| Builder's plan | `/Users/yosefgamble/github/vizra/docs/plans/2026-09-21-vizra-core-hardening-a.md` |

**Four slice items: all four CLOSED.**

| Item | Verdict |
|---|---|
| 1. `SEARCH_HMAC_KEY` rename, no alias, production refuses the retired name | **CLOSED** |
| 2. Make no-op hole: out-of-make anchor + a direct `go test` lane | **CLOSED** (see FINDING 1 for the residual the PR does not name) |
| 3. CI provenance: head, `HEAD^1`, tested merge commit | **CLOSED** |
| 4. Fixtures follow-ups (V-1 … V-4) | **CLOSED** |

**PASS is not a merge and not VERIFIED in the ledger.** The chair records those.

---

## Environment

Fresh clone from `https://github.com/yegamble/vizra-core.git`, detached at
`f56dc03a…`, under my own scratch directory. Never the builder's checkout.

```
darwin/arm64 (Apple Silicon), macOS 25.5.0
go            go1.27.1  (resolved by GOTOOLCHAIN=auto from go.mod `toolchain go1.27.1`;
                         local base toolchain is go1.26.2)
GNU Make      3.81  (macOS system make — NOT the acceptance platform's 4.3)
python3       3.9.6 + PyYAML
sqlc          v1.31.1
Docker        29.8.0
PostgreSQL    postgres:18-alpine, container `vzv-pg`,    host port 55433
Valkey        valkey/valkey:latest, container `vzv-cache`, host port 56380
```

Containers were created by me under names I chose and are removed by name at the
end. Nothing named `vidra-*` was touched.

**Note on the run.** Partway through, my first scratch directory
(`…/scratchpad/verify/`) was deleted by something outside this session while
`make ci` was running. I re-cloned under `…/scratchpad/vzv-pr6-verify/` and
re-ran every lane from scratch; every result below is from the second,
complete run. Recording it because another agent or a cleanup job appears to be
removing paths under the shared project scratch root, which will silently
destroy other verifiers' work in progress.

---

## 1. Lanes, from a clean clone at `f56dc03a`

| Command | Exit | Detail |
|---|---|---|
| `make ci` | **0** | all 10 lanes: fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify, test-race |
| — `test-race` package tally | | **13 ok, 8 `[no test files]`, 0 SKIP, 0 FAIL** — matches the builder's claim exactly |
| `make tidy-check` | **0** | |
| `make sqlc-verify` | **0** | `internal/store/sqlcgen matches store/queries + migrations` |
| `./scripts/make-integrity-guard.sh` | **0** | `passed (8 gate target(s))`, 17 in the prerequisite closure |
| `./scripts/ci-required-guard.sh` | **0** | `passed (6 required check(s))` |
| `make test-integration` | **0** | 14 ok incl. `internal/integration 9.738s`, 0 SKIP (PostgreSQL 18 + Valkey) |
| `make test-integration-shuffle` | **0** | same suite, `-shuffle=on` |
| `make fixtures-verify` (CLI path) | **0** | `ok — 12 fixtures, 1791508 bytes, generator 1 (4ff582ba6959), toolchain go1.27.1` |

Zero skips anywhere, locally or in CI (`grep -cE '\-\-\- SKIP|no tests to run'`
over the full build-test CI log returns **0**).

### Frozen paths — byte-identical to `main`

```
migrations/                        0 changed files
migrations/manifest.sha256         identical (sha-of-file compared against c043df7)
api/openapi.yaml                   0 changed files
api/search-internal.openapi.yaml   0 changed files
internal/store/sqlcgen/            0 changed files
```

`fixtures/manifest.json` changed **one line only** — `generator.source_sha256`
`a34db2c4…` → `4ff582ba…` — which is expected and correct: `manifest.go` and
`fixtures.go` are listed `GeneratorSourceFiles`. I proved all twelve fixture
entries are byte-identical to `main`:

```
fixture entries: 12 -> 12
every fixture sha256 identical: True
top-level keys whose value differs: ['generator']
```

`append-only` lane: **green on this SHA in CI** (job `append-only`, success,
05:50:40→05:50:44).

---

## 2. THE MAKE NO-OP

### 2a. The defect is real at the base (I reproduced it myself)

At `c043df7`, with a **real failing test** planted
(`internal/buildinfo/zz_planted_test.go`, `t.Fatal("PLANTED FAILURE…")`):

```
control (clean Makefile):     make ci EXIT=2, "PLANTED FAILURE" printed       ← gate is real
SHELL := /usr/bin/true:       make ci EXIT=0, planted failure never ran       ← DEFECT
MAKEFLAGS += -i:              make ci EXIT=0, "make: [test-race] Error 1 (ignored)"
                                             then "make ci: all lanes passed"  ← DEFECT
```

Digests printed before and after each mutation; both moved.

### 2b. At the head: every declared Makefile mutation is red BY NAME

Each mutation applied to a throwaway clone at `f56dc03a` with the same planted
failing test underneath; digest before → after recorded for every one; the
control (no mutation) passes. `anchor` = `./scripts/make-integrity-guard.sh`,
run out of make, which is what the workflow step runs.

| # | Mutation | anchor | `make ci` | Declared reason in the red |
|---|---|---|---|---|
| M1 | `SHELL := /usr/bin/true` | **1** | 0 | `Makefile:14 sets SHELL to something other than the approved value` + `make resolves SHELL to '/usr/bin/true' while resolving \`ci\`` |
| M2 | `MAKEFLAGS += -i` | **1** | 0 | `Makefile:14 assigns MAKEFLAGS` + `make resolves MAKEFLAGS to 'pni'` |
| M3 | `export GNUMAKEFLAGS := -i` | **1** | 2 | `Makefile:14 assigns GNUMAKEFLAGS` |
| M4 | `.SHELLFLAGS := -c` | **1** | 2 | `sets .SHELLFLAGS to something other than the approved value` + resolver |
| M5 | `.ONESHELL:` | **1** | — | `Makefile:14 declares \`.ONESHELL\`` + `is in effect while resolving \`ci\`` |
| M6 | `include inc.mk` where `inc.mk` sets `SHELL := /usr/bin/true` | **1** | 0 | `inc.mk:1 assigns SHELL, but only the root Makefile may` + resolver |
| M7 | `-@` prefix on `test-race` (reached **only through the prerequisite closure**) | **1** | 2 | `Makefile:159 — gate target \`test-race\` has a recipe line prefixed \`-\`` |
| M8 | `\|\| true` on `test-race` | **1** | 2 | `… has a recipe line ending \`\|\| true\`` |
| M8b | `\|\| :` | **1** | — | `… ending \`\|\| :\`` |
| M8c | `; true` | **1** | — | `… ending \`; true\`` |
| M9 | duplicate `test-race:` target replacing the recipe | **1** | 2 | `gate target \`test-race\` is defined 2 times: Makefile:157, Makefile:215` + `make reports a DUPLICATE definition` |
| M10 | recursive `$(MAKE) -f sub.mk` where the sub-makefile carries the override | **1** | 2 | `sub.mk:1 assigns SHELL, but only the root Makefile may` |
| M11 | `SHELL := $(shell echo /usr/bin/true)` (computed at runtime) | **1** | 0 | text reading **and** resolver both catch it |
| M12 | `MAKEFLAGS=-i` in the anchor's own environment | **1** | 0 | `the environment sets MAKEFLAGS='-i', which carries -i` |

**The prerequisite-closure claim holds.** M7/M8 mutate `test-race`, which no CI
lane names — it is reached only through `ci`'s prerequisites. The guard computes
the closure from the rules (17 targets from 8 seeds) and catches it.

**M11 is worth naming:** the guard's own docstring lists "a value computed at
runtime, e.g. through `$(eval …)`" as a blind spot of the TEXT reading. The
RESOLVER reading covers `$(shell …)` — I confirmed both readings fired.

### 2c. At the head: every declared workflow mutation is red BY NAME

Against `./scripts/ci-required-guard.sh`. Control passes (`passed (6 required
check(s))`). Every digest moved.

| Mutation | exit | Declared reason |
|---|---|---|
| anchor step **deleted** from `build-test` | **1** | `floor lane 'build-test' … invokes \`make\` (step 'go.mod and go.sum are tidy') with NO make-integrity-guard step before it` |
| anchor made **conditional** (`if:`) | **1** | `… makes the make-integrity-guard step CONDITIONAL` |
| anchor **moved after** make | **1** | `… runs the make-integrity-guard step at position 7, AFTER \`make\` at position 5` |
| anchor **continue-on-error** | **1** | `… marks the make-integrity-guard step continue-on-error: True` |
| **workflow-level** `defaults.run.shell` | **1** | `sets a workflow-level defaults.run.shell` — fires for `build-test` **and** the `needs:` leg |
| **job-level** `defaults.run.shell` | **1** | `sets a job-level defaults.run.shell` |
| direct `go test` lane **deleted** | **1** | `no required lane runs \`go test ./...\` directly` |
| direct lane **routed through make** (`run: make test-race`) | **1** | same |
| anchor deleted from **`cache-matrix-leg`** (the `needs:` leg) | **1** | `floor lane 'cache-matrix -> needs:cache-matrix-leg' … with NO make-integrity-guard step before it` |
| anchor deleted from **`fixtures.yml`** | **1** | `floor lane 'fixtures' (fixtures.yml) invokes \`make\` (step 'Generate the corpus') with NO …` |
| floor lane removed from `required-checks.txt` | **1** | `required lane 'fixtures' is MISSING from required-checks.txt` |
| floor lane commented out | **1** | `required lane 'fixtures' is COMMENTED OUT` |

The `needs:`-closure claim holds: `cache-matrix` is an aggregate that runs no
make, and the guard follows `needs:` to the leg that runs `make test-integration`.

### 2d. Is the direct lane REQUIRED, same package set, `-race`?

Yes on all three. From the CI log for this SHA:

```
- name: Unit suite, invoked directly (no make)
  run: go test -race -count=1 ./...
```

It is a step of `build-test`, which is in `required-checks.txt` and in
`FLOOR_LANES`. It is not a separate job, so no manifest line is needed. I
diffed the package list of the direct lane against `make ci`'s `test-race` in
the CI log: **identical** — 13 ok, 8 `[no test files]`, same names, same `-race`.

**It does NOT fail on zero tests run** — see FINDING 3.

### 2e. GNU Make 3.81 vs 4.3

Confirmed order-insensitive. I drove the guard's own parsing directly:

```
'pn'                  -> extra=[]     bad=[]                 ok     (3.81, here)
'np'                  -> extra=[]     bad=[]                 ok     (4.3, the runner)
'pni' / 'inp'         -> extra=['i']  bad=[]                 FAIL
'np --ignore-errors'  -> extra=[]     bad=['--ignore-errors'] FAIL
```

It compares letter **sets**, so order cannot matter. The duplicate-target regex
matches all four wordings:

```
overriding commands for target   (3.81)   matched
overriding recipe   for target   (4.x)    matched
ignoring old commands for target          matched
ignoring old recipe   for target          matched
```

**The make-4.3 path is judged from the CI log, as permitted.** The runner
printed `MAKEFLAGS carries nothing beyond this guard's own -pn ('np')` — the
4.3 letter order — for all 8 gate targets, and every guard check printed `ok`.
I did not need the container; none was created, so none was removed.

---

## 3. THE RENAME

### 3a. Every remaining `VIZRA_SEARCH_HMAC_KEY` in the tree

Grepped the whole tree. **Every occurrence is the retired-name refusal, its
test, or a dated historical note.** No occurrence is a live read.

```
internal/config/keys.go:94        RetiredKeys entry
internal/config/config_test.go    4 sites, all in the refusal tests
.env.example:67                   commented tombstone, under a "RETIRED 2026-09-21" note
AGENTS.md:206                     the naming rule, historical prose
docs/evidence/hardening-a/*       transcripts
```

`internal/config/config.go` reads `get("SEARCH_HMAC_KEY")`. `AllKeys()` is
documented as excluding retired names.

### 3b. Production boot matrix (real `cmd/api` binary, not a test)

| Case | Result |
|---|---|
| production, **only the retired name**, non-empty | **REFUSED.** `vizra-api refused to start.` → `VIZRA_SEARCH_HMAC_KEY: was renamed to SEARCH_HMAC_KEY and is NO LONGER READ. There is no compatibility alias, so this value has no effect: … Rename the variable — production will not boot believing a key is configured when none is.` Names the old variable, names the replacement, **never echoes the value** (grepped the output for the value: 0 occurrences) |
| production, **both** names set | **REFUSED**, same message. **This is safe and is the right call**: there is no alias, so a template setting both is a template whose author still believes the old name does something. Refusing forces the cleanup while nothing is deployed. |
| production, retired name present but **completely empty** (`KEY=`) | **boots** — deliberate, so `.env.example` can carry the tombstone. Stated in `config.go` and in `.env.example`. |
| production, retired name = **a single space** | **REFUSED** — the documented fail-secure reading of an ambiguous env file. |
| **development**, only the retired name, `VIZRA_SEARCH_MODE=off` | **boots silently.** Harmless (no search key is needed at all), and the refusal is documented as production-only in `config.go`, `.env.example` and AGENTS.md. |
| **development**, only the retired name, `VIZRA_SEARCH_MODE=managed` | **REFUSED**: `SEARCH_HMAC_KEY: must be at least 32 bytes when VIZRA_SEARCH_MODE is not 'off'` — so the one case where a dev would actually be hurt is still caught, under the new name. |

Development behaviour **is** stated: `config.go`'s block is inside `if
production`, `.env.example` says "production REFUSES to boot", AGENTS.md says
"production **refuses to boot**". No overstatement.

### 3c. Published-test-key refusal, under the new name

```
production, SEARCH_MODE=managed, SEARCH_HMAC_KEY = key_utf8 read from the vectors file
  → REFUSED: "SEARCH_HMAC_KEY: this value is published in this repository
    (api/search-hmac-testvectors.json is a TEST VECTOR, not a configuration value).
    Generate a real key: openssl rand -base64 32"
```

The test reads `key_utf8` **from the file** at test time
(`internal/config/config_test.go:295` `KeyUTF8 string \`json:"key_utf8"\``,
`:301` `t.Fatal("the vectors file has no key_utf8")`), not from a hardcoded
copy, so the constant cannot drift from the file.

`vizra doctor` and `.env.example` use the new name. `internal/doctor/` and
`cmd/vizra/` contain **no** literal key name at all — they read
`config.SearchHMACKey`, so there is nothing to go stale.

### 3d. `api/search-hmac-testvectors.json` — proved, not asserted

```
git diff --numstat:  1  1  api/search-hmac-testvectors.json      ← one line, one hunk
diff | grep -c '^[<>]':  2                                        ← two lines total
```

Structural proof over the parsed documents:

```
top-level keys identical:              True
top-level keys whose VALUE differs:    ['key_utf8_warning']    ← exactly one
positive vectors:  5   negative_vectors: 24   total: 29        ← unchanged
key_utf8 unchanged:                    True
```

So every byte of all 5 positive and 24 negative vectors is unchanged, and the
only change is the one prose string (`… must NEVER be used as
VIZRA_SEARCH_HMAC_KEY …` → `… as SEARCH_HMAC_KEY …`).

**Core's own vector tests pass** (`openapi-verify` in `make ci`, exit 0,
including `TestHMACTestVectorsArePublished`).

**vizra-search agrees on all 29.** I cloned `/Users/yosefgamble/github/vizra/vizra-search`
(read-only checkout, at `808a549`) into scratch — the checkout itself was not
touched — copied core head's vectors file in, and ran search's suite:

```
before swap: search's vendored file == core main's file (sha ff21e6b8…)  ✓
after swap:  sha f95623b0…  (core head's file)

TestVerifierReproducesTheSharedVectors     5 subtests PASS
TestVerifierRefusesEveryNegativeVector    24 subtests PASS
(+ TestTimestampWindowClosesAcrossTheWholeMagnitudeRange 34, and others — 71 total PASS)
ok  github.com/yegamble/vizra-search/internal/hmacauth
```

Both repositories agree on all 29 vectors with the new file. Search's
re-vendor manifest correctly goes red on the swap
(`TestEveryVendoredFileMatchesItsManifest`: "Re-vendor from
yegamble/vizra-core@415a6d1… instead of editing it"), which is the intended
mechanism forcing the chair's re-vendor — see the re-vendor note below.

---

## 4. PROVENANCE

Read from the CI log for `f56dc03a`, job `build-test`:

```
  event:                        pull_request
  ref:                          refs/pull/6/merge
  TESTED TREE (git rev-parse HEAD):  b550f7ba4f33851925fa23d117991404e960641d
      ^ this is what the commands in this job actually ran against
  parent method:                rev-parse
  base actually merged in (HEAD^1): c043df72f06cc7b5d7237a12d2be4dac25fa788e
  head actually merged in (HEAD^2): f56dc03a06533bf0bbf057eb74f62ffd47aafc50
  PR head SHA (github.event.pull_request.head.sha): f56dc03a06533bf0bbf057eb74f62ffd47aafc50
  github.sha:                   b550f7ba4f33851925fa23d117991404e960641d
  checked: HEAD^2 == the PR head SHA, so this really is the merge ref.
```

**Mutually consistent and correct.** The merge commit `b550f7b`'s parents are
exactly the base `c043df7` and the head `f56dc03`. All three are labelled.
`github.event.pull_request.base.sha` is deliberately not printed, with the
reason stated inline.

**Checkout is not pinned to the head**: `ref: refs/pull/6/merge`,
`fetch-depth: 2` (a fetch depth, not a `ref:` pin).

**It is a control, not a printout.** I drove `scripts/provenance.sh` directly:

```
checkout pinned to the head (no HEAD^2)   EXIT=1  "::error::HEAD has no second parent,
                                                   so this checkout is NOT refs/pull/N/merge"
mismatched PR_HEAD_SHA                    EXIT=1
GITHUB_EVENT_NAME=push                    EXIT=0  "On push, HEAD is the pushed commit itself…"
GITHUB_EVENT_NAME=merge_group             EXIT=0  "On merge_group, HEAD is the merge-queue commit…"
```

`merge_group` and `push` are handled in the script with their own cross-checks.
The provenance step is present in all five workflow files. See FINDING 4 for
the one required **lane** that lacks it.

---

## 5. FIXTURES

All through the **CLI path** (`go run ./cmd/fixturegen -repo . verify`), not
`go test`.

| Case | exit | Named? |
|---|---|---|
| control: corpus reproduces byte-identically | **0** | `ok — 12 fixtures, 1791508 bytes, generator 1 (4ff582ba6959), toolchain go1.27.1` |
| **11 fixtures** after dropping `webm-short` from `Corpus()` **and re-pinning** | **1** | `ADR-009 item 12 is missing: the committed manifest lists no fixture for it` (5 problems) |
| **13 fixtures** after adding a spec **and re-pinning** | **1** | `ADR-009 item 12 is claimed 2 times where the committed manifest lists: webm-short-copy.webm, webm-short.webm` |
| undeclared extra file `rogue-photograph.jpg` | **1** | named in full: `rogue-photograph.jpg in testdata/fixtures is a file that no manifest entry declares…` |
| undeclared **directory** `sneaky/` | **1** | `… is a directory that no manifest entry declares…` |
| `.DS_Store` planted | **0** | **still tolerated** |

**The defects were real at the base.** I re-measured at `c043df7`:

```
base, undeclared rogue-photograph.jpg:   verify exit=0  "ok — 12 fixtures"    ← V-3, invisible
base, 11 fixtures after a re-pin:        verify exit=0  "ok — 11 fixtures"    ← V-2, lies
```

**Is the `.DS_Store` tolerance stated?** Yes, in `internal/fixtures/manifest.go:376`:
*"Dotfiles are skipped by name: .DS_Store on a macOS working copy is an editor
turd, not a fixture, and a check that goes red for it is a check people route
around."* It is stated in the code that implements it, not in a user-facing
doc — adequate, and the reasoning is given rather than asserted.

**V-4, the misattributed comment:** fixed. `internal/fixtures/fixtures.go` now
reads *"produced once by recorded libvips and ffmpeg invocations — libvips
heifsave (libheif/aom) for the AVIF, ffmpeg for the WebM"*.

**V-1, the stale PENDING note:** corrected by an **appended dated correction**,
not a rewrite. `git diff --numstat` on
`docs/evidence/fixtures/2026-09-21-determinism.md` is **`52  0`** — 52 added
lines, **zero removed**. The appended section is headed *"Correction,
2026-09-21 (appended; nothing above is rewritten)"*, quotes the verifier's
proof rather than paraphrasing it, and carries a "What this correction does NOT
claim" subsection (one commit; two architectures are not every architecture;
the manifest of record is still the amd64 one). This is the right shape.

---

## 6. COST

Measured from the CI log for this SHA, job `build-test` (timeout 20 min):

```
job start                                05:50:40
  Install sqlc (go install @v1.31.1)     05:51:18 → 05:53:10   1m52s
  Refuse a neutered Makefile (anchor)    05:53:10 →            <1s
  make tidy-check                        05:53:10 → 05:53:13
  make ci                                05:53:13 → 05:55:51   2m38s   (internal/fixtures 105.5s)
  Unit suite, invoked directly (no make) 05:55:51 → 05:57:41   1m50s   (internal/fixtures 104.6s)
  ci-required guard / make build         05:57:41 → 05:57:44
  Integration tests                      05:57:44 → 05:59:40   1m56s
  Integration tests, shuffled            05:59:40 → 06:01:31   1m51s
job end                                  06:01:39              TOTAL 10m59s
```

**The builder's disclosure is accurate.** `internal/fixtures` under `-race` is
105.5 s, and it is paid **twice** (~3m30s of the 11 min) because the direct lane
duplicates it by design. Total 10m59s of a 20-minute timeout. The timeout was
**not** raised — confirmed: `timeout-minutes: 20` is unchanged from `main`.

**Is that headroom a flake risk?** My judgement: **not yet, but the margin is
thinner than 11/20 suggests.** ~9 minutes of headroom is real, but two of the
costs are not test time and can move without any code change: `go install
sqlc@v1.31.1` is uncached and took 1m52s (a cold module proxy or a slow runner
can multiply that), and the Go build cache is warm here. A cold-cache run plus a
slow runner could plausibly add 4–6 minutes, which still lands inside 20. The
structural point for the chair's backlog: the single largest line item
(`internal/fixtures` at ~105 s × 2) is a **corpus-regenerating** test, and it
grows every time a drift case is added. Two more cases of the same shape would
put this lane in flake territory. Worth a watch item, not a change now.

---

## 7. No existing test weakened or deleted

`internal/config/config_test.go` is the **only** test file with removed lines
(`182 / 10`). The other three touched test files are `+N / 0`:

```
182  10  internal/config/config_test.go
 37   0  internal/config/template_test.go
156   0  internal/fixtures/fixtures_test.go
127   0  scripts/scripts_test.go
```

**Ruling on each of the 10 removals — all ten are the rename, none is a
weakening.** Paired against their replacements:

| Removed | Replaced by | Ruling |
|---|---|---|
| `if !ve.Has("VIZRA_SEARCH_URL") \|\| !ve.Has("VIZRA_SEARCH_HMAC_KEY") {` | `… !ve.Has("SEARCH_HMAC_KEY") {` | rename; same assertion, same strength |
| `t.Fatalf("expected both VIZRA_SEARCH_URL and VIZRA_SEARCH_HMAC_KEY problems, got %v", …)` | same with new name | rename of a failure message |
| `env["VIZRA_SEARCH_HMAC_KEY"] = placeholderSecret(32)` | `env["SEARCH_HMAC_KEY"] = …` | rename |
| `env["VIZRA_SEARCH_HMAC_KEY"] = published` | `env["SEARCH_HMAC_KEY"] = published` | rename |
| `if !ok \|\| !ve.Has("VIZRA_SEARCH_HMAC_KEY") {` | `… !ve.Has("SEARCH_HMAC_KEY") {` | rename |
| 5 map-literal lines (`DATABASE_URL`, `VIZRA_SEARCH_MODE`, `VIZRA_SEARCH_URL`, `VIZRA_SEARCH_HMAC_KEY`, `VIZRA_SESSION_SECRET`) | the same 5 keys, one renamed, **gofmt re-aligned** | 4 are pure whitespace realignment forced by the shorter key; 1 is the rename |

**No assertion was weakened, no case deleted, no skip added, no budget or
baseline changed.** The +182 adds `TestTheSearchSecretIsTheNameTheContractUses`,
`TestProductionRefusesARetiredKeyName`,
`TestTheContractAndTheLoaderNameTheSameVariable` and
`TestRetiredKeysAreTombstonedInTheTemplate`.

The 23 removed lines outside tests and evidence are all the rename or the
manifest digest: `.env.example` 2, `api/README.md` 1,
`api/search-hmac-testvectors.json` 1, `fixtures/manifest.json` 1 (the generator
digest), `internal/config/config.go` 4, `internal/config/keys.go` 2,
`internal/fixtures/fixtures.go` 2 (the V-4 comment). No generated file was hand
edited: `sqlcgen/` is untouched and `sqlc diff` is clean.

**Secrets:** no credential, key or token added. Filtered and raw greps over the
`+` side of the diff return 0. **GitGuardian Security Checks: success** on this
SHA.

---

## 8. Truthfulness

I checked AGENTS.md, both guard docstrings, the PR body and
`docs/evidence/hardening-a/README.md` against what I measured.

**Accurate, and carefully scoped where it matters:**

- AGENTS.md's assurance-table row reads *"A **one-line Makefile edit** cannot
  turn every required lane into a no-op"* — scoped to the Makefile, and true.
- The make-integrity-guard docstring's "WHAT THIS GUARANTEES — stated at exactly
  its real strength" is conditional (*"While this program runs as an
  unconditional workflow step before `make` … and its exit status is not
  discarded"*) and every clause held under test.
- The stated residual is present and honest, in three places (AGENTS.md, the
  guard docstring, the PR body): the guard, the workflows and
  `ci-required-guard.py` are all editable in the PR under test, and **CODEOWNERS
  is advisory only** because the ruleset returns 403 on the owner's plan. I did
  not independently re-test the 403; I am accepting the builder's statement of a
  previously-established fact, and it is stated as a limitation rather than
  claimed as a control.
- The evidence README is explicit that the builder's machine is **not** the
  ADR-009 acceptance platform and that none of its transcripts is a verification.
- `D3-make-integrity.txt` volunteers a counterfactual it did **not** measure
  ("at the BASE commit … M4/M5/M6 would have left `make ci` exiting 0 … That
  counterfactual was not re-measured here"). That is the right instinct and it
  is labelled.
- The `02-vectors-AFTER.txt` canonical-digest claim reproduces: I got the same
  result by an independent method.

**Overstatement / understatement found:** four findings below. One is a
disclosure gap the chair asked me to probe (FINDING 1), one is a sentence that
reads broader than it is true (FINDING 2), one is an uncovered case (FINDING 3),
one is a coverage gap (FINDING 4). **One is a plain factual error in the PR
body (FINDING 5).**

---

## 9. CI on `f56dc03a`

Every required lane executed and is green **on this SHA**. Nothing skipped,
cancelled, timed out or missing.

```
append-only    success   05:50:40 → 05:50:44
build-test     success   05:50:40 → 06:01:39
cache-matrix   success   05:55:17 → 05:55:21
  cache-matrix-leg (valkey)  success
  cache-matrix-leg (redis)   success
docker-build   success   05:50:40 → 05:54:14
fixtures       success   05:50:41 → 05:52:53
govulncheck    success   05:50:40 → 05:51:17
ci-required    success   05:50:40 → 06:01:44
GitGuardian Security Checks  success
```

**Manifest and floor agree.** `.github/required-checks.txt` lists exactly
`append-only, build-test, cache-matrix, fixtures, govulncheck, docker-build`;
`FLOOR_LANES` in `ci-required-guard.py` is the same six. The `ci-required` job's
own log shows it resolved all six to real jobs and then waited for and observed
**SUCCESS** for each — not a manifest that lists lanes nobody ran:

```
ci-required-guard: passed (6 required check(s))
…
  SUCCESS   append-only
  SUCCESS   build-test
  SUCCESS   cache-matrix
  SUCCESS   fixtures
  SUCCESS   govulncheck
  SUCCESS   docker-build
```

**The new direct lane is a STEP of `build-test`, not a separate job**, so it
needs no manifest line and none is missing. `ci-required-guard` check 9 asserts
it exists: `ok  required lane 'build-test' runs the suite directly, without
make: 'go test -race -count=1 ./...'`.

---

## Findings

```
FINDING 1: neither guard reads the workflow's own `make` invocation, so one word
           on a workflow line still no-ops every make-driven lane
Severity:    REQUIRED  (as a DISCLOSURE fix; the acceptance bullet itself is met)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py:189 (check_anchor), :282 (check_direct_test_lane)
             scripts/make-integrity-guard.py:50-84 ("WHAT IT DOES NOT GUARANTEE")
             .github/workflows/build-test.yml:  `- name: make ci` / `run: make ci`
             PR #6 body, "What remains, stated rather than implied"
  requirements: the slice's acceptance item 2

Observed:
  The anchor runs its OWN `make -pn TARGET` subprocess and checks its OWN
  environment. It cannot see the argv or the step-level `env:` of a DIFFERENT
  workflow step. ci-required-guard checks the anchor's presence, position,
  conditionality, continue-on-error and defaults.run.shell — it never reads the
  TEXT of a make step's `run:` for flags or variable overrides.

  Measured at f56dc03a, on the unmodified Makefile, with a real failing test
  planted:

    ./scripts/make-integrity-guard.sh          EXIT=0
    make SHELL=/usr/bin/true ci                EXIT=0   planted failure never ran
    make -i ci                                 EXIT=0   planted failure printed, ignored
    make MAKEFLAGS=-i ci                       EXIT=0

  And with the workflow edited so the step reads `run: make -i ci` (or
  `make SHELL=/usr/bin/true ci`, or `make MAKEFLAGS=-i ci`, or the step given
  `env: MAKEFLAGS: -i`), BOTH guards stay green:

    ci-required-guard EXIT=0   make-integrity-guard EXIT=0   (all four variants)

  No artifact in the PR names this. I grepped AGENTS.md, both guard docstrings
  and every file under docs/evidence/hardening-a/ for "command line", "argv",
  "invocation", "make -i": the only hit is the guard explaining that make reads
  the ENVIRONMENT "as if it were on the command line" — which is the case it
  does cover.

Failure:
  The source finding (vizra-search PR2 FINDING 8) was "one line turns every
  make-driven required lane into a no-op". This slice closes that line in the
  Makefile and its includes — genuinely, thirteen ways over, verified above. It
  does not close the same outcome reached by one word on a workflow line. The
  blast radius is smaller than at the base, because the direct `go test` lane
  still runs: a failing UNIT test is still caught. What goes silent is
  everything else `make ci` does — fmt-check, vet, lint-imports, migrate-lint,
  config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify
  — plus `make tidy-check`, `make build`, and both integration lanes in
  build-test and in BOTH cache-matrix legs.

  The harm is not that this is a new hole; it is that the PR's "What remains,
  stated rather than implied" section is written as an exhaustive list of the
  residual, and this is not on it. The chair has held five PRs over guarantees
  stated more strongly than the control. This one is stated at the right
  strength for the Makefile and silent about the adjacent one-word evasion.

Perspective:
  developer, operator

Recommendation:
  Either (a) ~10 lines in ci-required-guard.py: in check_anchor, refuse a floor
  lane's make step whose `run:` carries `-i`/`-k`/`-t`/`-q`/`--ignore-errors`/
  `--keep-going` or a `VAR=value` override before the target, and refuse a
  step-level `env:` that sets MAKEFLAGS/GNUMAKEFLAGS/MFLAGS on a make step; or
  (b) if the chair prefers not to widen the guard now, add one bullet to the
  three "what remains" sections naming it. (a) is cheap and mechanical and I
  would prefer it; (b) is the minimum.

Acceptance criteria:
  - With `.github/workflows/build-test.yml` edited so the make step reads
    `run: make -i ci`, `./scripts/ci-required-guard.sh` exits non-zero and names
    the flag. Same for `make SHELL=/usr/bin/true ci` and for a step-level
    `env: MAKEFLAGS: -i` on a make step.
  - The unmodified tree still exits 0.
  - OR: AGENTS.md, scripts/make-integrity-guard.py's docstring and the PR body
    each name this evasion in their residual list.

Tests:
  scripts/scripts_test.go, alongside the existing scripts/testdata/guard/
  fixtures: add `make-flag-override/` and `make-var-override/` and
  `step-env-makeflags/` workflow fixtures, each expected to fail the guard by
  name. The harness already exists and this is the same shape as the twelve
  fixtures already there.
```

```
FINDING 2: "a real failing test fails a required lane" is true of the UNIT suite
           only; the integration suite runs solely through make
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md (the new "The gate is make-driven" section, control 2)
             scripts/ci-required-guard.py:43 ("a no-opped Makefile cannot make the suite silent")
             PR #6 body, "Layer (b) — a required lane with no make in it"
             .github/workflows/build-test.yml (both integration steps; both cache-matrix legs)
  requirements: the slice's acceptance item 2(b)

Observed:
  The direct lane is exactly `go test -race -count=1 ./...` — no
  `-tags=integration`. Every integration invocation in the repository is
  `make test-integration` / `make test-integration-shuffle`: in build-test and
  in both cache-matrix-leg matrix entries. check_direct_test_lane requires only
  `go test` + `./...` without make, which the unit lane satisfies.

  AGENTS.md says: "build-test runs `go test -race -count=1 ./...` directly, with
  no make, so whatever `make ci` did, a real failing test still fails a required
  lane." The PR body says the same. Read plainly, "a real failing test" includes
  an integration test. It does not.

Failure:
  Under any make neutering that survives the anchor (FINDING 1's route), a
  failing INTEGRATION test — the migration run against real PostgreSQL 18, the
  Valkey/Redis compatibility matrix that ADR-001 Q-004 makes permanent — is
  silent, not red. The sentence tells a reader that layer (b) covers it. The gap
  matters most exactly where the two-image matrix is the only evidence anyone
  has for a compatibility claim nobody upstream guarantees.

Perspective:
  developer, operator

Recommendation:
  One word, or one step. Either narrow the sentence in all three places to "a
  real failing UNIT test", or add `go test -race -count=1 -tags=integration ./...`
  as a second direct step in build-test (it needs the same services that step
  already has up, so the cost is one more suite run — and the chair should weigh
  that against FINDING 6's timing headroom before taking it).

Acceptance criteria:
  - AGENTS.md, ci-required-guard.py's check-9 docstring and any future PR body
    say "unit" where they currently say "the suite"/"a real failing test";
  - OR a required lane runs the integration suite without make, and
    check_direct_test_lane asserts it.

Tests:
  If the second option is taken: scripts/testdata/guard/no-direct-integration-lane/
  in the same shape as the existing no-direct-test-lane/ fixture.
```

```
FINDING 3: the direct lane does not fail on zero tests run
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .github/workflows/build-test.yml ("Unit suite, invoked directly (no make)")
             scripts/ci-required-guard.py:316 (check_makefile_selection)
  requirements: the slice's acceptance item 2(b)

Observed:
  Measured at f56dc03a. I moved all 19 *_test.go files aside and ran the exact
  command the required lane runs:

    go test -race -count=1 ./...     EXIT=0     every package "[no test files]"

  ci-required-guard check 5 asserts PKGS is `./...` and that every `-run` pattern
  is non-empty — both good — but nothing asserts that any test actually EXECUTED.
  (Restored afterwards; `git status --porcelain` clean, 19 test files back.)

Failure:
  The second layer is described as the control for "whatever make did, the suite
  is not silent". It is a control against make being neutered. It is not a
  control against the suite being EMPTIED — deleting the test files leaves it
  green. That path is loud in a diff and already an AGENTS.md violation, so this
  is a gap in coverage rather than a false claim: I found no artifact that claims
  deletion-resistance. Recording it so the chair does not later assume it.

Perspective:
  developer

Recommendation:
  Change the step to `go test -race -count=1 -v ./... 2>&1 | tee /tmp/t.log` and
  assert a floor on `grep -c '^--- PASS' /tmp/t.log`, or use `-json` and count
  `"Action":"pass"` at test level. A hardcoded floor (e.g. "at least 200 tests
  ran") is the cheap version and is in the same spirit as ADR009Count: a constant
  that does not move with the thing it measures.

Acceptance criteria:
  - With every *_test.go removed, the required lane exits non-zero and says how
    many tests ran versus the floor.
  - The unmodified tree passes.

Tests:
  scripts/scripts_test.go if the floor lands in a script; otherwise the step's
  own assertion is the test.
```

```
FINDING 4: `append-only` is a required floor lane that computes a merge base and
           prints SHAs, with no provenance step
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .github/workflows/build-test.yml, job `append-only`
  requirements: the slice's acceptance item 3

Observed:
  Parsed the workflow: of build-test.yml's four jobs, `build-test` and
  `cache-matrix-leg` have a provenance step; `cache-matrix` is a pure aggregate
  with no checkout; `append-only` has NONE. It does `actions/checkout` with
  `fetch-depth: 0`, computes `base="$(git merge-base "origin/${base_ref}" HEAD)"`
  and echoes `merge base: $base` — a SHA, printed by a lane, with no statement of
  which tree it is standing in.

  The PR body and AGENTS.md both say provenance.sh is called by "every required
  WORKFLOW", which is literally true (all five workflow files have it). Neither
  claims every required lane. So this is incompleteness, not overstatement.

Failure:
  meta-PR3 FINDING 5 — the finding this item exists to close — was exactly "a
  step whose job was to record provenance printed a SHA that was not the tree it
  described". `append-only` is the remaining required lane with that shape.

Perspective:
  developer

Recommendation:
  Add the same two-line `- name: Provenance …` / `run: ./scripts/provenance.sh`
  step to `append-only`, after its checkout. It already has full history, so
  HEAD^1/HEAD^2 resolve.

Acceptance criteria:
  - Every job in .github/workflows/ that performs a checkout and prints a SHA
    also runs scripts/provenance.sh.

Tests:
  A check in scripts/ci-required-guard.py that every floor-lane job with an
  actions/checkout step also has a provenance step, with a
  scripts/testdata/guard/ negative fixture.
```

```
FINDING 5: the PR body's re-vendor note names the wrong commit
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     PR #6 body, "`api/` change, and what it is not" → "Re-vendor note"
  requirements: none

Observed:
  The PR body says: "After it, the last commit touching `api/` is this PR's head."

  Measured:
    git log --oneline -3 -- api/
      2ceac77 chore(m0): close the make-no-op hole, rename the shared search secret, …
      415a6d1 feat: M0 foundation — … (#1)

  The head is f56dc03, which touches only docs/evidence/hardening-a/. The last
  commit touching api/ is 2ceac77e4cbb30e964335a7adc6cee550fa65485.

Failure:
  A re-vendor instruction that names the wrong pin. In practice the chair will
  re-vendor from the squash-merge commit on main, so nothing breaks — but the
  builder's plan document is also stale against the head (it records commit
  2ceac77, "82 files, +3177/-23"; the head is f56dc03, 83 files, +3554/-23),
  and a reader reconciling the two has two wrong numbers and one wrong SHA.

Perspective:
  developer

Recommendation:
  Correct the PR body sentence to name 2ceac77 (or, better, to say "re-vendor
  from the squash-merge commit on main once this lands"), and append a dated
  line to docs/plans/2026-09-21-vizra-core-hardening-a.md recording the second
  commit — appended, not rewritten, per the same rule this slice applied to the
  determinism note.

Acceptance criteria:
  - The PR body and the plan agree with `git log -1 --format=%H -- api/` and
    with `git diff --shortstat c043df7..<head>`.

Tests:
  none — documentation.
```

---

## Re-vendor note for the chair

**The last commit touching `api/` is `2ceac77e4cbb30e964335a7adc6cee550fa65485`**
(not the head `f56dc03a…`, which touches only `docs/evidence/hardening-a/`).

Files that moved under `api/`: `api/README.md` and
`api/search-hmac-testvectors.json` only. **`api/openapi.yaml` and
`api/search-internal.openapi.yaml` are byte-identical to `main`.** The vectors
file changed one prose string; all 29 vectors are byte-identical and both
repositories' verifiers agree on all 29 (proved in §3d). So the re-vendor for
`vizra-user` and `vizra-search` is a **pin bump, not a behaviour change** —
but it IS required, because `vizra-search`'s
`TestEveryVendoredFileMatchesItsManifest` goes red on the new bytes (I confirmed
this by swapping the file into a scratch clone of search).

---

## What I did not verify

- **UNVERIFIED: the CODEOWNERS 403.** The PR states the owner's plan returns 403
  on the ruleset that would make CODEOWNERS mandatory. I did not re-test this
  against the GitHub API. It is stated as a limitation, not claimed as a
  control, so it does not affect the verdict.
- **The GNU Make 4.3 path was judged from the CI log, not re-run in a
  container** (explicitly permitted). The runner's own guard output shows the
  4.3 MAKEFLAGS letter order (`'np'`) and all checks green; I additionally drove
  the guard's parsing against both make wordings and both letter orders locally.
  No container image was pulled, so none was removed.
- **Not a UI slice** — no browser work applicable.

## Cleanup

Removed by exact name: containers `vzv-pg`, `vzv-cache`. Scratch clones under
my own scratchpad directory removed by path. Nothing named `vidra-*` was touched,
no shared image list or cache was pruned, and the read-only `vizra-search`
checkout at `/Users/yosefgamble/github/vizra/vizra-search` was cloned from but
never modified.

---

# Re-confirmation at `1c12fd9` — 2026-09-21

The chair held the PASS at `f56dc03` over FINDING 1's disclosure gap and asked
for a docs-and-comments-only commit. The head moved to
`1c12fd9e6eb4b46223a903a004c36d80cb5d8668` (base still `c043df72…`, 83 files,
+3697 −23). This section judges whether the PASS carries. I took nothing on
trust, including the chair's own characterisation of the commit as docs-only.

Fresh clone in a directory created with `mktemp -d`
(`…/scratchpad/vzvrc.rB2SWA5U`), never reused and never named `verify/`.

## R1. Is it really docs-and-comments only?

**Scope.** One commit, `1c12fd9 docs: name the workflow-line evasion, scope
layer (b) to the unit suite, and correct the api/ pin`. Exactly four files, all
`M`, no renames, no mode changes (`git diff --summary` is empty):

```
51   9  AGENTS.md
35   0  docs/evidence/hardening-a/README.md
26   5  scripts/ci-required-guard.py
46   1  scripts/make-integrity-guard.py
```

**Proof that the two Python files changed only in docstrings — my own method,
not a reading of the diff.** I parsed both revisions of each file with Python's
`ast`, removed the docstring statement from every Module/Class/Function node
(comments never reach an AST at all), and compared `ast.dump()`:

```
scripts/ci-required-guard.py
   raw bytes:            22113 -> 23355   (differ: True)
   docstrings stripped:  7 / 7
   AST identical after stripping docstrings: True

scripts/make-integrity-guard.py
   raw bytes:            27925 -> 30375   (differ: True)
   docstrings stripped:  9 / 9
   AST identical after stripping docstrings: True
```

Identical ASTs means **no executable statement, no runtime constant, no regex
pattern and no exit path moved**, and the equal docstring counts (7/7, 9/9) mean
none was added or removed as a statement.

Independently, I tokenised both revisions and classified every line the diff
touches:

```
scripts/ci-required-guard.py    ADDED 26 -> {'string': 26}   REMOVED 5 -> {'string': 5}
scripts/make-integrity-guard.py ADDED 46 -> {'string': 46}   REMOVED 1 -> {'string': 1}
any line classified as CODE:  NONE  (in either file)
```

Every changed line is inside a string literal. Not one is code — and, as it
happens, not one is even a `#` comment.

**Is any docstring consumed at runtime? Yes — one, and it did not move.**
`scripts/make-integrity-guard.py:609` reads
`ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])`, so the
module docstring's **first line** is a runtime value. I extracted it from both
revisions via the AST:

```
BEFORE: make-integrity-guard — refuse a Makefile that has been turned into a no-op.
AFTER : make-integrity-guard — refuse a Makefile that has been turned into a no-op.
=> IDENTICAL
```

`scripts/ci-required-guard.py` does not reference `__doc__` at all. And
`scripts/scripts_test.go` never invokes `--help`/`-h` (grep count 0) — it passes
`--workflows`/`--manifest`/`--skip-makefile`/`--root`/`--targets` — so the
argparse description is not reachable from any test either. **Does not matter,
and did not change anyway.**

**Nothing pinned, generated or fixed moved:**

```
fixtures/manifest.json identical:      YES
migrations/manifest.sha256 identical:  YES
.github/ identical:                    YES
internal/ identical:                   YES
go.mod / go.sum identical:             YES
scripts/testdata/ identical:           YES
scripts/scripts_test.go identical:     YES
api/ , migrations/ : 0 changed files
```

**Lanes from the clean clone at `1c12fd9`:**

| Command | Exit | Detail |
|---|---|---|
| `make ci` | **0** | 10 lanes; test-race **13 ok, 8 `[no test files]`, 0 SKIP, 0 FAIL** — identical to `f56dc03` |
| — `fixtures-verify` | | `ok — 12 fixtures, 1791508 bytes, generator 1 (4ff582ba6959), toolchain go1.27.1` — byte-identical to the `f56dc03` result |
| `./scripts/make-integrity-guard.sh` | **0** | `passed (8 gate target(s))` |
| `./scripts/ci-required-guard.sh` | **0** | `passed (6 required check(s))` |
| `go test -race -count=1 ./scripts/` | **0** | 7 tests, **55 subtests PASS, 0 FAIL, 0 SKIP** — every guard fixture still red for its own reason |

## R2. Truthfulness of the new text

I checked every new factual claim against what I measured at `f56dc03`.

| New claim | My measurement | Verdict |
|---|---|---|
| Four spellings leave both guards at 0: `make -i ci`, `make SHELL=/usr/bin/true ci`, `make MAKEFLAGS=-i ci`, step-level `env: MAKEFLAGS: -i` | exactly those four, each `ci-required-guard EXIT=0` and `make-integrity-guard EXIT=0` | **accurate** |
| Blast radius: fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify, tidy-check, build, both integration lanes incl. both cache-matrix legs; only the unit suite survives | matches the `ci:` prerequisite list and the build-test/cache-matrix-leg steps I read | **accurate** |
| Layer (b) is UNIT only; no `-tags=integration`; every integration invocation goes through make | confirmed from the workflow and from `check_direct_test_lane` | **accurate** |
| Zero tests: `go test -race -count=1 ./...` with every `*_test.go` aside exits 0 on `[no test files]` | I measured exactly this (19 files moved aside, exit 0) | **accurate** |
| `append-only` has no provenance step; "every required workflow FILE is not every required JOB" | confirmed by parsing the workflow: of 4 jobs, only `build-test` and `cache-matrix-leg` have it | **accurate, and the file/job distinction is the right one** |
| README: `D3-make-integrity.txt:9`'s baseline digest `3421fd3e75d321b7` is correct **for `f56dc03`** and is stale at head, deliberately not rewritten | `f56dc03` → `3421fd3e75d321b7`; `1c12fd9` → `ef211589b094c892` | **accurate** — a self-reported digest drift, disclosed instead of quietly re-run |

**The AGENTS.md assurance-table row was the right thing to narrow.** It now
reads "A one-line edit to the **Makefile or its includes** cannot turn every
required lane into a no-op (a one-word edit to a workflow's own `make` line
still can — see …)". That closes the overstatement risk at its source rather
than only in a footnote.

**Nothing new is over-claimed.** Every new bullet is scoped, attributes its
measurement to `f56dc03`, and says "queued for sweep B … deliberately not
implemented here" rather than implying a fix.

### Attacking "This list is meant to be EXHAUSTIVE"

The sentence appears once in `scripts/make-integrity-guard.py` and once in
AGENTS.md. I tried three ways to break it.

**Attempt 1 — can a Makefile make the guard's own probe execute code?** The
guard runs `make -pn TARGET` twice per target, and GNU make executes recipe
lines containing `$(MAKE)` even under `--dry-run`; the guard refuses a `+`
prefix for exactly this reason but never mentions `$(MAKE)`. I planted a
`$(MAKE) -f sub.mk` line in `test-race`'s recipe with an observable side effect
(`touch`). **Hypothesis disproved:** make propagates `-n` to the sub-make, whose
recipes therefore do not run. No side effect. The recursion *does* pollute the
guard's `MAKEFILE_LIST` reading (it then printed "the root Makefile does not
carry BOTH approved assignments" and "gate target `ci` is not defined", which
are false statements about the root Makefile) — but the guard **exits 1**, so it
fails closed. A confusing red is not a hole. **Not a missing residual.**

**Attempt 2 — the `.sh` wrapper.** `scripts/make-integrity-guard.sh` is 16
lines; neutering it to `exit 0` would satisfy `step_is_the_anchor`, which only
checks the `run:` text. But `scripts_test.go` drives the **`.sh`**, and its
fixtures expect non-zero exits, so the neutering is caught — in the direct
`go test ./...` lane, which needs no make. **Covered**, and the residual list's
"there is no mechanical control in this repository that a sufficiently
determined PR cannot also edit" covers the case where the tests are deleted too.

**Attempt 3 — a REQUIRED lane that is not a FLOOR lane. This one lands.** See
FINDING 6 below. It is the one thing I found that belongs on a list claiming to
be exhaustive and is not on it.

## R3. FINDING 5 — closed

**PR body**, now:

> …the pin to re-vendor from is **`2ceac77e4cbb30e964335a7adc6cee550fa65485`** —
> the last commit in this branch that touches `api/`. It is *not* the branch
> head: every later commit here is documentation and evidence only. (Derive it
> yourself with `git log --oneline -1 -- api/`.)

Ground truth from my clone: `git log -1 --format=%H -- api/` →
`2ceac77e4cbb30e964335a7adc6cee550fa65485`. **Matches**, and it now says
explicitly that it is not the head — which was the actual error.

**Plan document**: the stale counts are gone. It now carries a commit table
(`2ceac77` = the slice and the `api/` pin; `f56dc03` = the D3 transcript and
integration lanes; "round 2" = docs and comments only) and states *"Deliberately
**no file/line counts here**: they moved once already"*, replacing them with
`git diff --shortstat main...HEAD`, `git diff --stat f56dc03..HEAD` and
`git log --oneline -1 -- api/`. Nothing left to go stale. **F-5 CLOSED.**

## R4. CI on `1c12fd9`

`build-test` had concluded by the time I read it. Every required lane completed
and succeeded **on this SHA** — nothing pending, skipped, cancelled or timed out:

```
append-only    completed  success
build-test     completed  success      06:43:02 -> 06:54:10  (11m08s of a 20-min timeout)
cache-matrix   completed  success
  cache-matrix-leg (valkey)  completed  success
  cache-matrix-leg (redis)   completed  success
docker-build   completed  success
fixtures       completed  success
govulncheck    completed  success
ci-required    completed  success
GitGuardian Security Checks  completed  success
```

The fan-in read the manifest on this SHA and observed each lane itself — not a
manifest listing lanes nobody ran:

```
required checks (6): append-only build-test cache-matrix fixtures govulncheck docker-build
ci-required-guard: passed (6 required check(s))
  SUCCESS append-only / build-test / cache-matrix / fixtures / govulncheck / docker-build
```

Manifest and `FLOOR_LANES` still agree, six and six. Provenance on this SHA is
correct and mutually consistent:

```
ref:                              refs/pull/6/merge
TESTED TREE (git rev-parse HEAD):  e225a8b18cf1fc79d3b2f04243ea4ba015403d02
base actually merged in (HEAD^1):  c043df72f06cc7b5d7237a12d2be4dac25fa788e
head actually merged in (HEAD^2):  1c12fd9e6eb4b46223a903a004c36d80cb5d8668
PR head SHA:                       1c12fd9e6eb4b46223a903a004c36d80cb5d8668
checked: HEAD^2 == the PR head SHA, so this really is the merge ref.
```

## Findings carried and added

FINDINGS 1–4 are now **disclosed** rather than closed — that was the point of
this round, and the disclosure is accurate and in three places. They remain open
as engineering work, queued by the builder for core hardening sweep B; the chair
should carry them to that slice's brief rather than treat this round as fixing
them. FINDING 5 is **CLOSED**. One new finding:

```
FINDING 6: a lane that is REQUIRED but not in FLOOR_LANES is never anchor-checked,
           continue-on-error-checked or trigger-checked — and the guard prints `ok`
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py:406 (floor loop), :434 (the checks 3/4/8 loop),
             :424 (the `required` loop, which only resolves names)
             scripts/make-integrity-guard.py, "WHAT IT DOES NOT GUARANTEE"
             AGENTS.md, "What these two controls do NOT give you"
  requirements: the slice's acceptance item 2(a)

Observed:
  Checks 3 (pull_request), 4 (no continue-on-error) and 8 (the anchor) are all
  looped over FLOOR_LANES. The loop over `required` does one thing only: assert
  the name resolves to a job. Today required == FLOOR_LANES exactly (6 = 6), so
  nothing is exposed — this is latent.

  Measured at 1c12fd9. I added a seventh line `extra-lane` to
  .github/required-checks.txt and a workflow whose job carries BOTH
  `continue-on-error: true` at job level AND `run: make -i ci` with no anchor
  step before it:

      ci-required-guard      EXIT=0
      make-integrity-guard   EXIT=0
      the only line mentioning it:  "ok  required check 'extra-lane' resolves to a job"

  (Restored; `git status --porcelain` clean.)

Failure:
  The guard prints a reassuring `ok` for a required lane it has not actually
  checked — which is the exact failure mode its own opening paragraph exists to
  prevent: "A guard that reports ok for something it cannot see is the
  false-positive CI that AGENTS.md names." It fails OPEN, not closed. Widening
  the gate by adding a line to required-checks.txt looks virtuous and is the
  low-friction edit most likely to introduce it; the new lane would then be
  exempt from every structural check the other six get.

  It belongs on a list that says "This list is meant to be EXHAUSTIVE. Something
  that belongs on it and is not here is a defect in this docstring, not a
  detail." It is not on it.

Perspective:
  developer, operator

Recommendation:
  Two lines: run checks 3, 4 and 8 over `set(FLOOR_LANES) | set(required)`
  rather than over FLOOR_LANES alone. FLOOR_LANES keeps its separate job — it is
  the floor that cannot be REMOVED; it should not also be the ceiling on what
  gets checked. If the chair prefers no code change in a docs round, add the
  bullet to the three residual lists and take the fix in sweep B with 1–4.

Acceptance criteria:
  - A lane listed in required-checks.txt but absent from FLOOR_LANES, carrying
    continue-on-error or an unanchored make step, turns ci-required-guard red by
    name.
  - The unmodified tree still exits 0 with `passed (6 required check(s))`.

Tests:
  scripts/scripts_test.go, with a scripts/testdata/guard/required-not-floor/
  fixture in the same shape as the twelve already there: a required-checks.txt
  with an extra name and a workflow whose matching job is unanchored.
```

## Does the PASS carry?

Yes. The commit is provably documentation and comments only — executable ASTs
identical, every changed line inside a docstring, the single runtime-consumed
docstring line byte-identical, and no manifest, fixture, workflow, test or
pinned digest moved. Every lane I ran at `f56dc03` I re-ran at `1c12fd9` with
the same results, the guard fixtures still pass (55 subtests, 0 fail, 0 skip),
and `ci-required` plus all six floor lanes are green on this SHA with the
manifest matching the jobs that actually ran. The new text is accurate against
my own measurements and narrows the one row that had been over-broad. FINDING 5
is closed; FINDINGS 1–4 are now honestly disclosed and queued; FINDING 6 is new,
latent, and not blocking.

Head re-checked at the end of this section: still
`1c12fd9e6eb4b46223a903a004c36d80cb5d8668` (`updated_at` 2026-09-21T06:42:56Z).

**PASS is still not a merge and not VERIFIED in the ledger.** The chair records
those, and should carry FINDINGS 1, 2, 3, 4 and 6 into the sweep B brief.

FINAL VERDICT: PASS — SHA 1c12fd9e6eb4b46223a903a004c36d80cb5d8668
