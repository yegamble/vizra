# Execution plan: vizra-search PR2 — re-vendor the core contract from `main`, close verifier findings F7 and F8

## Context

- Repo: `yegamble/vizra-search`; checkout `/Users/yosefgamble/github/vizra/vizra-search`.
- Base: `main` @ `581d79dc01e11fcbab9149eec95707d4637b46e4` (PR #1 squash-merge), clean.
- Branch: `chore/revendor-core-main`.
- Meta issue: `yegamble/vizra#1`.
- Authority: meta `AGENTS.md`; `vizra-search/AGENTS.md` § "This repository does not own the contract";
  ADR-002 (Accepted 2026-09-20) and the Q-001 ruling.
- Source of truth for the vendored files: `yegamble/vizra-core` `main` @
  `415a6d19cfc0acedd8ad84c1857c95db0ed63627`. Local read-only checkout at
  `/Users/yosefgamble/github/vizra/vizra-core`.

### Why

PR #1 vendored the two contract files from core commit `2b9c540e81960954ee39e6a2aeec027e0f764a67`,
which lived on core's feature branch `feat/m0-foundation`. That branch was deleted when core's PR
was squash-merged, so the recorded `source_commit` is no longer reachable from any ref in
`yegamble/vizra-core` — the provenance points at nothing a reviewer can fetch. Core's merged bytes
also differ from what was vendored.

## Acceptance

1. **Re-vendor.** `api/search-internal.openapi.yaml` and `api/search-hmac-testvectors.json` are
   byte-identical to `415a6d1:api/<file>` in core, proved by blob id / sha256 agreement.
   `api/CONTRACT-SOURCE.json` records `source_repository`, `source_ref: main`, the 40-char commit,
   and per-file `bytes` + `sha256`. The published-key refusal
   (`TestTheVectorsPublishedKeyIsStillTheOneWeRefuse`, `TestProductionRefusesThePublishedVectorsKey`)
   still refuses `key_utf8` read from the re-vendored file, and the new `key_utf8_warning` field
   does not break the vector loader.
2. **F7.** `make contract-drift` must fail when a vendored file is edited in place, and when a
   manifest sha256 is zeroed. Today it does not: the lane's `-run` regex does not select
   `TestEveryVendoredFileMatchesItsManifest`, so both mutations survive `make contract-drift`
   (they die only under `make ci`). The fix removes the name coupling rather than lengthening the
   regex, and a guard test keeps the lane and the tests from drifting apart again.
3. **F8.** `scripts/ci-required-guard.sh`'s fixture loop (`for fixture in scripts/testdata/wf-*.yml`)
   is green when the directory or the fixtures vanish: with no match, bash passes the literal glob
   to the checker, which errors, and the `*)` branch reads that as "correctly rejected". A missing
   directory or an empty/short glob must be a named failure.

Non-goals (explicitly out of this slice): the nonce store, multi-key rotation, connection caps, and
any handler behaviour change not forced by the contract text.

## Implementation

- `api/search-internal.openapi.yaml`, `api/search-hmac-testvectors.json`: replaced wholesale from
  core `415a6d1`. Never hand-edited.
- `api/CONTRACT-SOURCE.json`: `source_ref`, `source_commit`, both `sha256`, both `bytes`.
- `Makefile` `contract-drift`: lane selection.
- `internal/httpapi/contract_drift_test.go` (or a new test file): the lane-selection guard.
- `scripts/ci-required-guard.sh`: fixture-loop hardening.
- No handler, no `internal/hmacauth`, no `internal/config` production-code change unless the
  contract text forces one.

Interfaces shared with another owner: both vendored files are owned by the `vizra-core` builder.
This repository consumes them at a recorded SHA and does not edit them.

## Verification

Exact lanes (all exist in `Makefile` / `.github/required-checks.txt`):

- `make fmt-check`, `make vet`, `make echo-containment`, `make build`
- `make contract-drift`, `make test`, `make test-noskip`, `make tidy-check`
- `./scripts/ci-required-guard.sh`
- `make ci` (the complete local gate)
- `govulncheck` and `docker-build` run in CI on `ubuntu-24.04`.

Demonstrations, transcripts under `docs/evidence/pr2/` inside the repo:

- **D-F7-a**: edit a vendored file in place → `make contract-drift` RED; restore → GREEN.
- **D-F7-b**: zero a manifest `sha256` → `make contract-drift` RED; restore → GREEN.
- **D-F7-c**: reintroduce a `-run` filter on the lane → the guard test goes RED.
- **D-F8-a**: `scripts/testdata/` removed → `./scripts/ci-required-guard.sh` RED (named failure).
- **D-F8-b**: fixtures deleted but directory present → RED (named failure).
- **D-KEY**: the published-key refusal still refuses `key_utf8` after the re-vendor.

Each demonstration must be shown against the lane named in the finding (`make contract-drift`
specifically for F7, not only `make ci`).

## Progress and evidence

IMPLEMENTED, READY_FOR_REVIEW. Not verified — an independent verifier has not reproduced this.

### Preflight (all green before any code)

`go1.26.2 darwin/arm64` on PATH (module toolchain resolves `go1.27.1`), `make` (GNU 3.81),
`jq`, `shasum`, `git`, `gh` authenticated as `yegamble`, `govulncheck v1.8.0` — the exact version
`.github/workflows/ci.yml` pins — and Docker running. 13 GiB free. Nothing was BLOCKED.
`docker-build` was deliberately **not** run locally: this is an Apple-Silicon machine and the
acceptance target is native amd64, so that lane is left to CI (ADR-009 / Q-027).

### 1. Re-vendor

Both files replaced wholesale from `git -C vizra-core show 415a6d1:api/<file>` — never hand-edited.

| file | core blob id @415a6d1 | vendored blob id | sha256 | bytes |
|---|---|---|---|---|
| `api/search-internal.openapi.yaml` | `848503cca45dc427fede810d3ab30e73e07bd392` | identical | `a78d8aa7320dbd49530b10bf1c9dcb22ff5f586f06bd7c821aa7cb8b4a735448` | 25297 |
| `api/search-hmac-testvectors.json` | `6548d87e1811336d7e62ad99e78a4b687a88fe7e` | identical | `ff21e6b8cdd7d3bc32caa455cf605e1069ea4534db2b9b0a9e2d90c78a3d35c3` | 22327 |

Provenance of the *old* pin, recorded because it is the reason for this PR:
`gh api repos/yegamble/vizra-core/branches/feat/m0-foundation` → **404 Branch not found**;
`gh api repos/yegamble/vizra-core/compare/main...2b9c540…` → **`diverged`**; the remote has only
`refs/heads/main`. Evidence: `vizra-search/docs/evidence/pr2/revendor-provenance.txt`.

**What changed in the contract, and whether it forced code.** Nothing forced a code change.

Core's `api/` directory changed in **three** files between `2b9c540` and `415a6d1` —
`api/README.md` (+29), `api/search-hmac-testvectors.json` (+1) and
`api/search-internal.openapi.yaml` (+8), 38 insertions and 0 deletions in total.
`api/README.md` is **not vendored** here, so nothing follows from it. Restricted to the two
files this repository vendors the diff is `2 files changed, 9 insertions(+)`, no deletions —
two additive prose insertions and nothing else:

- `api/search-hmac-testvectors.json`: one new sibling field `key_utf8_warning` beside `key_utf8`.
  This is the "only the vectors file's warning string changed" case for that file.
- `api/search-internal.openapi.yaml`: an eight-line **"Who enforces what"** paragraph in the
  `hmacSignature` description, saying `MAX_INTERNAL_BODY_BYTES` is configured and enforced by
  `vizra-search` as the server and is deliberately not a core key, and that core bounds the
  response direction at a fixed 8 MiB. So the OpenAPI file changed too — not only the vectors —
  but the change is documentation of an ownership split this repository already implements. No
  schema, path, operation id, status, security requirement or fixed number moved.

Consequences checked rather than assumed: `TestTheContractsFixedNumbersMatchTheImplementation`
still finds `±300 s`, `` `MAX_INTERNAL_BODY_BYTES` (default 1 MiB) ``, `1000000000`, `4102444800`
and `at most 128`; `make contract-drift` and `make test` pass with no production-code edit.

**Published-key refusal after the re-vendor** (`docs/evidence/pr2/revendor-key-and-vectors.txt`):
`TestTheVectorsPublishedKeyIsStillTheOneWeRefuse`, `TestProductionRefusesThePublishedVectorsKey`,
`TestCheckEnvRefusesThePublishedVectorsKey`, `TestProductionRefusesEveryPublishedKey`,
`TestDevelopmentStillAcceptsThePublishedKeys` and `TestEveryKeyLiteralInThisRepositoryIsRefused`
all PASS — the refusal reads `key_utf8` out of the re-vendored file at test time and still refuses
it. The vector loader is unaffected by the new sibling field: 5/5 ACCEPT and 24/24 REJECT vectors
consumed (`TestVerifierReproducesTheSharedVectors`, `TestVerifierRefusesEveryNegativeVector`,
`TestEveryNamedRejectClassIsCovered`, `TestTheVendoredVectorsAreUsable`).

### 2. F7 — the lane no longer selects by test name

Reproduced first (`docs/evidence/pr2/F7-before-the-fix.txt`): with PR #1's recipe,
`go test -list '<the regex>' ./internal/httpapi/` does **not** list
`TestEveryVendoredFileMatchesItsManifest`; `make contract-drift` exits **0** with a vendored file
edited in place, and **0** with a manifest `sha256` zeroed, while the guard run by name exits 1.

Fix: the recipe now names packages and carries **no test-selecting flag** —
`go test -count=1 ./internal/httpapi/ ./internal/contract/ ./internal/hmacauth/ ./internal/config/`.
`internal/config` was not in the old lane at all, though it holds the `key_utf8` refusal guard.
New `internal/httpapi/lane_selection_test.go` holds the property from the other side: it parses the
recipe out of the `Makefile`, fails on `-run`/`-skip`/`-short`/`-tags`/`-bench`/`-fuzz`, and fails
if any package containing a `_test.go` that reads a vendored file (markers derived from the
manifest, not hard-coded) is absent from the list.

Red/green under `make contract-drift` specifically
(`docs/evidence/pr2/F7-after-the-fix-red-green.txt`), exit codes in the transcript:

| mutation | `make contract-drift` |
|---|---|
| none (baseline) | exit 0 — GREEN |
| `api/search-internal.openapi.yaml` edited in place | exit 2 — RED |
| restored | exit 0 — GREEN |
| `api/search-hmac-testvectors.json` edited in place | exit 2 — RED |
| a manifest `sha256` zeroed | exit 2 — RED |
| a file dropped from the manifest's `files` | exit 2 — RED |
| a `-run` filter put back on the lane | exit 2 — RED (the new guard) |
| a vendored-file guard moved to an unlisted package | exit 2 — RED (the new guard) |
| fully restored | exit 0 — GREEN |

### 3. F8 — a missing fixture directory is a named failure

Reproduced first (`docs/evidence/pr2/F8-before-the-fix.txt`): `./scripts/ci-required-guard.sh`
exits **0** with `scripts/testdata/` deleted, **0** with the directory present but every
`wf-*.yml` deleted, and **0** with just `wf-quoted-key.yml` deleted.

Fix: the directory must exist; a floor of fixtures is checked **by name**
(`wf-clean.yml` plus `wf-plain`, `wf-quoted-key`, `wf-capitalised`, `wf-expression`, `wf-false`),
mirroring the lane floor already in that script; the glob is expanded under `nullglob` and an
empty match is refused; and the number actually exercised is counted against the floor.

Red/green (`docs/evidence/pr2/F8-after-the-fix-red-green.txt`):

| mutation | guard | failure |
|---|---|---|
| none | exit 0 — GREEN | `6 fixtures exercised, floor 6` |
| `scripts/testdata/` removed | exit 1 — RED | `MISSING FIXTURES: 'scripts/testdata' does not exist.` |
| directory kept, all `wf-*.yml` deleted | exit 1 — RED | `MISSING FIXTURE: …wf-plain.yml…` (each named) |
| one floor fixture deleted | exit 1 — RED | `MISSING FIXTURE: 'scripts/testdata/wf-quoted-key.yml'…` |
| the accept fixture deleted | exit 1 — RED | `MISSING FIXTURE: 'scripts/testdata/wf-clean.yml'…` |
| a fixture stops discriminating | exit 1 — RED | `the workflow checker ACCEPTED …wf-quoted-key.yml` |

### Lanes (`docs/evidence/pr2/lanes-local.txt`)

`fmt-check`, `vet`, `echo-containment`, `build`, `contract-drift`, `test`, `test-noskip`,
`tidy-check`, `scripts/ci-required-guard.sh`, `scripts/check-workflows.py`, `govulncheck ./...` —
**all exit 0**. `make ci` exit 0. `make test-noskip`: **321 pass events, 0 skips**.
`docker-build`: NOT RUN locally (native-amd64 target; CI runs it).

No existing test was weakened, deleted, renamed or skipped; the only test change is one added file.

### Fix round 2 — verifier FAIL on `1772270`, findings 1, 2, 3 and 4

Verdict: `/Users/yosefgamble/github/vizra/docs/evidence/warroom/2026-09-20-vizra-search-pr2-revendor-VERIFY.md`.
Both REQUIRED findings were residuals of the class this PR exists to remove — a check that
reports green without having checked. Both reproduce; both are now closed.

**FINDING 1 + 3 — `-run` deselected the guard that forbids `-run`.** The recipe check was an
ordinary Go test *inside* the lane it polices, so `go test -run 'TestVerifier'` deselected it:
the lane printed `ok … [no tests to run]` and exited 0 with a vendored file edited in place. My
round-1 `-run` demonstration passed only because the regex I chose (`Contract|Drift|Schema`)
happened to match the guard's own name — the transcript was honest, the conclusion drawn from it
was not.

The control now sits outside `go test`: `scripts/contract-drift-guard.py` is a recipe step.
`recipe` runs before `go test`; `ran` runs after. `recipe` judges the lane by
**`make --dry-run contract-drift`**, not by the Makefile text, which resolves variables,
includes and duplicate targets in one move; it allows only `-count=1` and `-json`, refuses an
environment-assignment prefix, a wrapper in place of `go test`, `GOFLAGS`/`GOTESTFLAGS` carrying
a selecting flag in the environment, and any package holding a vendored-file guard that is
missing. `ran` fails a lane that ran **zero** tests in any listed package. The Go tests are now
the second layer and additionally drive the guard against all twelve bypasses.

Evidence `vizra-search/docs/evidence/pr2/F7-round2-lane-guard-red-green.txt` — every mutation
applied *together with* a real in-place edit of `api/search-internal.openapi.yaml`:

| mutation | `make contract-drift` | refusal |
|---|---|---|
| none | exit 0 GREEN | `315 tests ran … none deselected` |
| **`-run 'TestVerifier'`** (the verifier's exact case) | exit 2 RED | `the contract-drift lane carries -run` |
| `-run 'TestNothingAtAll'` | exit 2 RED | same |
| `-run` via `$(TESTFLAGS)` | exit 2 RED | same |
| `GOFLAGS=-run=…` in the environment | exit 2 RED | `GOFLAGS in the environment carries -run` |
| a duplicate `contract-drift:` target | exit 2 RED | `make reports a DUPLICATE … target` |
| the flag from an included makefile | exit 2 RED | `carries -run` |
| `go test` behind a wrapper script | exit 2 RED | `runs './scripts/drift-wrapper.sh' instead of \`go test\`` |
| the guard step deleted from the recipe | exit 2 RED | second layer: `FIRST command must be …` |
| the in-place edit alone | exit 2 RED | `TestEveryVendoredFileMatchesItsManifest` |
| a manifest `sha256` zeroed | exit 2 RED | same |
| fully restored | exit 0 GREEN | — |

**FINDING 2 — an unevaluable reject fixture counted as "rejected".** The branch read any
non-zero checker exit as proof of rejection, and a checker that cannot read or parse its input
also exits non-zero. `check-workflows.py` now answers three ways (`0` clean, `1` VIOLATION,
`2` UNEVALUABLE) and prints `VIOLATION <path> at=… key=… value=…`; each reject fixture declares
the rule it must trip; the guard requires readable + non-empty *before* running the checker,
exit `1` exactly, and the declared rule.

Evidence `vizra-search/docs/evidence/pr2/F8-round2-fixture-rules-red-green.txt`:

| mutation | guard | named failure |
|---|---|---|
| none | exit 0 GREEN | `6 fixtures exercised, floor 6` |
| reject fixture `chmod 000` | exit 1 RED | `UNUSABLE FIXTURE: '…wf-plain.yml' exists but is not readable.` |
| reject fixture **emptied** | exit 1 RED | `UNUSABLE FIXTURE: '…wf-quoted-key.yml' is empty.` |
| reject fixture truncated to invalid YAML | exit 1 RED | `UNEVALUABLE FIXTURE: the workflow checker could not evaluate …` |
| `wf-false.yml` value changed to `true` | exit 1 RED | `WRONG RULE TRIPPED: … not for the rule it declares` |
| `wf-quoted-key.yml` key unquoted | exit 1 RED | same |
| a reject fixture made actually valid | exit 1 RED | `the workflow checker ACCEPTED …` |
| accept fixture `chmod 000` | exit 1 RED | `UNUSABLE FIXTURE: …` |
| round-1 reds A–E re-run | exit 1 RED each | unchanged |

**FINDING 4 (NIT)** — corrected here, in `docs/evidence/pr2/README.md` and in the PR body:
core's `api/` changed in three files (`api/README.md` +29 is not vendored); the `2 files, 9
insertions` count is the *vendored pair* only.

Round-2 lanes (`vizra-search/docs/evidence/pr2/lanes-local.txt`): every lane exit 0;
`make ci` exit 0; `make test-noskip` **338 pass events, 0 skips** (321 in round 1; +17 new
lane-guard cases, none skipped); `make contract-drift` `315 tests ran across 4 package(s),
0 failures, none deselected`. No existing test weakened, deleted or skipped.

### Round 2b — CI caught a platform-dependent guard, which is the point of CI

`562bb99` was green on every lane **locally** and red on three in CI (`contract-drift`, `test`,
`test-noskip`), all on one subtest:
`TestTheLaneGuardRefusesEveryKnownBypass/a_duplicate_contract-drift_target` —
*"the guard refused the lane, but not for the expected reason."*

The guard detected a duplicate target by matching make's warning text, and the wording is
version-dependent: GNU Make **3.81** (macOS system make, my machine) says `overriding commands
for target`; GNU Make **4.x** (every ubuntu-24.04 runner, the platform that gates merges) says
`overriding recipe for target`. So on Linux that check never fired. The lane still went red in
that test only because the duplicate recipe *also* carried `-run`; a duplicate target that was
otherwise clean would have slipped past on Linux.

The test caught it because it asserts the refusal **reason**, not a non-zero exit — the same
principle as the fixture rules in Finding 2. Fixed in `e219fc6`: both wordings matched
case-insensitively, plus any other make warning during resolution refused. The only code change
between `562bb99` and `e219fc6` is that regex (`git diff --stat`: one script, +24/-?; the rest
is evidence). No make 4.x exists on this machine, so the make-4 path is proven by that subtest
running on ubuntu-24.04 in CI — recorded in
`vizra-search/docs/evidence/pr2/F7-round2-make-version-portability.txt`.

### FINAL CI — head `e219fc6b9f64d04d2adde87b830b2e9a4f388b5d`

`gh api repos/yegamble/vizra-search/commits/e219fc6…/check-runs` → **12 check runs, conclusions
`["success"]`**. Run `https://github.com/yegamble/vizra-search/actions/runs/35539255888`;
`ci-required` run `35539255892`.

| check | result | duration |
|---|---|---|
| `fmt` | pass | 17s |
| `vet` | pass | 48s |
| `echo-containment` | pass | 19s |
| `build` | pass | 39s |
| `contract-drift` | pass | 34s — `315 tests ran across 4 package(s), 0 failures, none deselected` |
| `test` | pass | 1m17s |
| `test-noskip` | pass | 54s — **338 pass events, 0 skips**, identical to local |
| `tidy-check` | pass | 20s |
| `govulncheck` | pass | 55s |
| `docker-build` | pass | 49s |
| `ci-required` | **pass** | 1m28s |
| GitGuardian Security Checks | pass | 1s |

The subtest that failed at `562bb99` is proven to run and pass on make 4.x: the same lane went
from fail to pass with only the regex changed, and reports 338 pass events with 0 skips — so
nothing was deselected or skipped to get there.

READY_FOR_REVIEW at `e219fc6`. Not VERIFIED: the new SHA is re-verified before any merge.

### CI on the round-1 head SHA (superseded)

PR: https://github.com/yegamble/vizra-search/pull/2
Head SHA: `17722700abf264813b7fa2f659e9cdccc922bfb7` (equals the local HEAD; the head has not moved
since CI ran). Run: `https://github.com/yegamble/vizra-search/actions/runs/35537325499`.

`gh api repos/yegamble/vizra-search/commits/1772270…/check-runs` → **12 check runs, conclusions
`["success"]`** (a single unique value). All lanes green on `ubuntu-24.04`:

| check | result | duration |
|---|---|---|
| `fmt` | pass | 23s |
| `vet` | pass | 45s |
| `echo-containment` | pass | 17s |
| `build` | pass | 41s |
| `contract-drift` | pass | 49s |
| `test` | pass | 1m27s |
| `test-noskip` | pass | 46s |
| `tidy-check` | pass | 19s |
| `govulncheck` | pass | 54s |
| `docker-build` | pass | 49s — the lane not runnable locally |
| `ci-required` | **pass** | 1m49s |
| GitGuardian Security Checks | pass | 1s |

`ci-required` is the aggregate gate and it is green on the verified SHA. The PR is `MERGEABLE`
and `OPEN`. It is **READY_FOR_REVIEW, not VERIFIED** — the builder does not verify or merge its
own work.

## Blockers and handoff

None. One observation for the chair, not a blocker and not something this repository may fix:
core's new `key_utf8_warning` string names the environment variable `VIZRA_SEARCH_HMAC_KEY`,
while the canonical contract (line ~233 of the same commit's OpenAPI) and this service both use
`SEARCH_HMAC_KEY`. It is prose in a non-normative field and nothing reads it, so it changes no
behaviour — but if it is a typo it belongs in `vizra-core`, and this repository would re-vendor
after.

Next action: independent verification of PR #2 against its head SHA.
