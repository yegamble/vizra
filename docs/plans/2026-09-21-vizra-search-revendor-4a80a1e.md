# Execution plan: vizra-search — re-vendor the internal contract and HMAC vectors from vizra-core `main@4a80a1e`

## Context

- Repo: `yegamble/vizra-search`; checkout `/Users/yosefgamble/github/vizra/vizra-search`.
- Base: `main` @ `808a5499dae1d58971d740f34749c2f35149fa4d` (PR #2 squash-merge), clean.
- Branch: `chore/revendor-core-4a80a1e`.
- Authority: meta `AGENTS.md`; `vizra-search/AGENTS.md` § 2 "This repository does not own the
  contract" — *"If the contract is wrong, say so to the chair. The change lands in `vizra-core`
  first; this repository then re-vendors it and updates the manifest's `source_commit` in the same
  PR."* ADR-002 (Accepted 2026-09-20) and the Q-001 ruling.
- Source of truth: `yegamble/vizra-core` `main`. Read from an **independent clone** made for this
  slice, not from the shared `/Users/yosefgamble/github/vizra/vizra-core` checkout — another
  builder is working in that tree and it is read-only for me.
- Precedent for shape and evidence: `docs/plans/2026-09-20-vizra-search-pr2-revendor.md` and
  `docs/evidence/warroom/2026-09-20-vizra-search-pr2-revendor-VERIFY.md`.

### Why

`api/CONTRACT-SOURCE.json` pins core `415a6d19cfc0acedd8ad84c1857c95db0ed63627`. Core has since
squash-merged PR #6 as `4a80a1e3f36b8001c2954d0568bea29268e739fe`, which changed
`api/search-hmac-testvectors.json`. The pin is stale, so the vendored vectors are no longer core's
bytes. This is a **pin bump, not a behaviour change**: only the non-normative `key_utf8_warning`
prose string differs, and it differs in the direction this repository asked for — the PR #2 handoff
note reported that core's warning named `VIZRA_SEARCH_HMAC_KEY` while both the canonical contract
and this service use `SEARCH_HMAC_KEY`. Core fixed it.

## Acceptance

1. **Re-vendor through this repository's own vendoring command**, never by hand-copying a vendored
   file or hand-editing the manifest. The manifest records a `source_commit` that is **on core's
   `main`**; every vendored file's sha256 and byte count equal core `main`'s bytes, shown side by
   side.
2. *demonstrated*: (a) before the re-vendor, swapping core `main`'s vectors file in makes
   `TestEveryVendoredFileMatchesItsManifest` red **by name** — reproducing the core-PR-#6 verifier's
   observation; (b) after the re-vendor the tree is green; (c) editing one byte of a vendored file
   turns **`make contract-drift` and `make ci`** red by name, restoring turns them green. Digests
   recorded before and after every mutation; the harness refuses to score a mutation that did not
   actually change the file; transcripts committed in-repo.
3. All **5** ACCEPT and **24** REJECT vectors are consumed by this repository's own suite against
   the re-vendored file. Counts and skips recorded; a skip is not a pass.
4. **No other change.** Specifically: no `VIZRA_SEARCH_MODE` / `VIZRA_MODE` rename, no change to
   `scripts/ci-required-guard.sh`, `scripts/contract-drift-guard.py`, `.github/workflows/ci.yml`
   or any CI guard. Both are queued as their own slices.

Non-goals: the nonce store, multi-key rotation, connection caps, the mode-variable rename, the CI
guard hardening, and any handler behaviour change.

## Implementation

- **New** `scripts/vendor-contract.py` + `make vendor-contract`: the repository had **no** vendoring
  command — PR #1 and PR #2 both vendored by hand (`git show … > file`) and hand-edited the
  manifest, which is exactly how a manifest drifts from the bytes it claims to pin. The script is
  the single writer of `api/search-internal.openapi.yaml`, `api/search-hmac-testvectors.json` and
  `api/CONTRACT-SOURCE.json`.
  - It resolves the source commit itself: the last commit **on `<remote>/main`** touching `api/`,
    and refuses a commit that is not an ancestor of that branch tip.
  - It reads bytes with `git show <commit>:<source_path>` — never the source working tree.
  - It rewrites the manifest from the bytes it just wrote (sha256 + byte count computed after the
    write, not before), preserving the prose fields.
  - `--check` re-derives everything and exits non-zero on any mismatch, so the command can also be
    run to prove the tree is already vendored.
- `api/search-hmac-testvectors.json`: replaced wholesale by that script.
- `api/search-internal.openapi.yaml`: already byte-identical; the script rewrites it with the same
  bytes (no diff).
- `api/CONTRACT-SOURCE.json`: `source_commit`, `vendored_at`, and the vectors file's `sha256` /
  `bytes`, all written by the script.
- **New** `scripts/revendor-demo.sh`: the demonstration harness for acceptance 2. It refuses to
  score a mutation whose digest did not move (guarding against the failure mode where a
  demonstration "goes red" for a reason unrelated to the mutation).
- Evidence transcripts under `docs/evidence/pr3/`.
- No production Go code, no test weakened, deleted or skipped.

Interfaces shared with another owner: both vendored files are owned by the `vizra-core` builder.
This repository consumes them at a recorded SHA and does not edit them.

## Verification

Lanes that exist today (`Makefile`, `.github/required-checks.txt`):

- `make fmt-check`, `make vet`, `make echo-containment`, `make build`
- `make contract-drift`, `make test`, `make test-noskip`, `make tidy-check`
- `./scripts/ci-required-guard.sh`, `./scripts/check-workflows.py`
- `make ci` (the complete local gate), `govulncheck ./...`
- `docker-build` and `govulncheck` also run in CI on `ubuntu-24.04`, which is the acceptance
  platform. `docker-build` is deliberately NOT run locally: this is an arm64 machine and the
  image target is amd64 (ADR-009 / Q-027).

Demonstrations (transcripts in `docs/evidence/pr3/`):

- **D-A**: before the re-vendor, core `main`'s vectors file dropped in → `go test -run
  TestEveryVendoredFileMatchesItsManifest ./internal/httpapi/` RED, naming the file and both
  digests; restore → GREEN.
- **D-B**: after the re-vendor, the tree is green on every lane, and `vendor-contract --check`
  exits 0.
- **D-C**: one byte of each vendored file edited in place → `make contract-drift` RED **and**
  `make ci` RED, by name; restore → GREEN. Digests printed before and after each mutation.
- **D-V**: 5 ACCEPT + 24 REJECT vectors consumed, counted from the suite's own output.

## Progress and evidence

### Preflight (all green before any code)

`go1.27.1 darwin/arm64`, GNU Make 3.81 (macOS system make), `python3` 3.9.6, `jq` 1.7.1,
`shasum` 6.02, `git`, `gh` authenticated as `yegamble`, `govulncheck v1.8.0` (the version
`.github/workflows/ci.yml` pins), Docker running, 27 GiB free. Nothing BLOCKED.
`docker-build` not run locally — arm64 host, amd64 acceptance target; CI runs it.

### Provenance — the recorded commit is on core's `main`

Proved from a clone of `https://github.com/yegamble/vizra-core.git` made for this slice
(`git clone` into a private `mktemp -d`), not from the shared checkout:

| question | command | answer |
|---|---|---|
| core `main` tip | `git log -1 --format=%H origin/main` | `4a80a1e3f36b8001c2954d0568bea29268e739fe` |
| last commit on `main` touching `api/` | `git log -1 --format=%H origin/main -- api/` | `4a80a1e3f36b8001c2954d0568bea29268e739fe` |
| is it on `main`? | `git merge-base --is-ancestor 4a80a1e origin/main` | exit 0 |

The core PR branch's last `api/` commit `2ceac77` does **not** exist on `main` after the squash —
recorded in the transcript. `4a80a1e` is the commit this manifest pins.

### What actually changed under `api/`

| file | core `415a6d1` → `4a80a1e` |
|---|---|
| `api/search-internal.openapi.yaml` | **byte-identical** — blob `848503cca45dc427fede810d3ab30e73e07bd392` on both sides |
| `api/search-hmac-testvectors.json` | one line: `key_utf8_warning` prose, `VIZRA_SEARCH_HMAC_KEY` → `SEARCH_HMAC_KEY` |
| `api/README.md` | changed, **not vendored here** |

Not asserted — measured. `jq -cS '.vectors'` and `jq -cS '.negative_vectors'` hash identically on
both sides (`9d7bfdc4…` and `a835c72f…`), and both sides carry 5 / 24. So no vector moved.

| file | core `4a80a1e` sha256 | bytes | vendored after | bytes |
|---|---|---|---|---|
| `api/search-internal.openapi.yaml` | `a78d8aa7320dbd49530b10bf1c9dcb22ff5f586f06bd7c821aa7cb8b4a735448` | 25297 | identical | 25297 |
| `api/search-hmac-testvectors.json` | `f95623b0ad6783818bc73c5b4d516d84ce7b2b6afde01397a6c8b15a422c2862` | 22321 | identical | 22321 |

(Before this PR the vendored vectors were `ff21e6b8cdd7d3bc32caa455cf605e1069ea4534db2b9b0a9e2d90c78a3d35c3`, 22327 bytes.)

### 1. The re-vendor (acceptance 1)

Done through `make vendor-contract CORE=<clone> CORE_REF=origin/main`, which runs
`scripts/vendor-contract.py` — **new in this PR**, because the repository had none. Transcript
`vizra-search/docs/evidence/pr3/revendor-run.txt`. No vendored file and no manifest field was typed
by hand.

Before the re-vendor the command already reported the stale pin (exit 1):
`the manifest pins 415a6d1…, but the current last api/ commit on origin/main is 4a80a1e… — re-vendor`.

The diff is exactly what a pin bump should be: `api/search-hmac-testvectors.json` one prose line,
`api/CONTRACT-SOURCE.json` `source_commit` / `vendored_at` / one `sha256` / one `bytes` (plus a
refreshed `$provenance_note`, passed **in** to the script via `--note` rather than edited after).
`api/search-internal.openapi.yaml` is untouched because it is already byte-identical.

Independent of any digest this repository computes, git agrees:

```
core     api/search-hmac-testvectors.json  1509da859954f65fd5542053332b8417fe4eb8da
vendored api/search-hmac-testvectors.json  1509da859954f65fd5542053332b8417fe4eb8da
core     api/search-internal.openapi.yaml  848503cca45dc427fede810d3ab30e73e07bd392
vendored api/search-internal.openapi.yaml  848503cca45dc427fede810d3ab30e73e07bd392
```

Guards the script enforces, so this cannot regress to PR #1's defect: it refuses a commit that is
not an ancestor of the branch tip, refuses a `--ref` that is not a `main` branch, refuses a
manifest pinning fewer than two files or whose `source_path` differs from `vendored_path`, and
digests the bytes it reads **back off disk** after writing them. It only ever reads the core
checkout (`rev-parse`, `log`, `merge-base`, `show`).

### 2. Demonstrations (acceptance 2)

`scripts/revendor-demo.sh` — also new — refuses to score a mutation it cannot prove happened:
sha256 recorded before and after each write, `MUTATION DID NOT APPLY` abort if the digest did not
move, digest re-checked after restore, restore through an `EXIT` trap, and every red asserted
**by name** rather than by a non-zero exit. Each mutation is a single byte inside a YAML comment or
a non-normative JSON prose string, so both files stay parseable and a parse error cannot
masquerade as a digest failure.

**D-A — before the re-vendor** (`docs/evidence/pr3/D-A-before-revendor-red-green.txt`), run on the
tree at `808a549`:

| state | `go test -run '^TestEveryVendoredFileMatchesItsManifest$' ./internal/httpapi/` |
|---|---|
| as vendored on `main` (stale pin, `ff21e6b8…`) | exit 0 — GREEN |
| core `main`'s bytes in, manifest unchanged (`f95623b0…`) | **exit 1 — RED** |
| restored (`ff21e6b8…`) | exit 0 — GREEN |

The RED names all five things the harness asserts: `TestEveryVendoredFileMatchesItsManifest`,
`the vendored api/search-hmac-testvectors.json does not match its manifest`, both digests, and
`Re-vendor from yegamble/vizra-core`. Harness verdict: 0 unexpected results. This reproduces the
core-PR-#6 verifier's observation and is what makes the re-vendor required.

**D-C — after the re-vendor** (`docs/evidence/pr3/D-C-after-revendor-red-green.txt`):

| state | `make contract-drift` | `make ci` | `vendor-contract --check` |
|---|---|---|---|
| baseline, re-vendored | 0 GREEN | 0 GREEN | 0 GREEN |
| one byte of `search-internal.openapi.yaml`, `a78d8aa7…` → `d8dc196b…` | **2 RED** | **2 RED** | **1 RED** |
| restored, digest re-checked `a78d8aa7…` | 0 GREEN | — | — |
| one byte of `search-hmac-testvectors.json`, `f95623b0…` → `2b4bb7c3…` | **2 RED** | **2 RED** | **1 RED** |
| both restored | 0 GREEN | 0 GREEN | 0 GREEN |

Every RED names `TestEveryVendoredFileMatchesItsManifest` and the specific file. Harness verdict:
0 unexpected results.

### 3. Vectors (acceptance 3)

`docs/evidence/pr3/D-V-vectors-consumed.txt`, against the re-vendored file (`f95623b0…`, 22321
bytes). Counted from `go test -json`, not from reading the text:

- `TestVerifierReproducesTheSharedVectors` — **5/5 ACCEPT** subtests PASS, each named
  (`search-empty-body`, `search-simple`, `suggestions`, `events-batch`, `unicode-body`).
- `TestVerifierRefusesEveryNegativeVector` — **24/24 REJECT** subtests PASS, each named.
- **0 skips, 0 failures** in that run; `make test-noskip` reports **347 pass events, 0 skips**
  across the whole suite.
- `TestTheVendoredVectorsCoverTheContractsWindow`, `TestEveryNamedRejectClassIsCovered`,
  `TestTheVendoredVectorsAreUsable` PASS — the loader has not quietly narrowed.
- The published-key refusal still reads `key_utf8` out of the re-vendored file and still refuses
  it: all six `internal/config` published-key tests PASS.

### 4. Scope (acceptance 4)

`git diff --stat` against `main`, excluding the new evidence directory:

```
AGENTS.md                        | 28 ++++++++++++++++++++++++++++
Makefile                         | 21 +++++++++++++++++++++
api/CONTRACT-SOURCE.json         | 21 +++++++++++----------
api/search-hmac-testvectors.json |  2 +-
scripts/vendor-contract.py       | new
scripts/revendor-demo.sh         | new
```

No `.github/` file, no `scripts/ci-required-guard.sh`, no `scripts/contract-drift-guard.py`, no
`.github/required-checks.txt`, no `VIZRA_SEARCH_MODE` / `VIZRA_MODE` rename, no production Go code,
no test file. The `AGENTS.md` change documents the new command in the section that previously said
"re-vendors it" with no command to name; the `Makefile` change adds the two targets.

**Reported, not fixed (acceptance 4's "report rather than widen"):** the old prose string
`VIZRA_SEARCH_HMAC_KEY` is referenced nowhere else in this repository. `grep -rn` over `*.go`,
`*.md`, `*.json`, `*.yaml`, `*.yml`, `*.py`, `*.sh` and the `Makefile` finds it only inside the
vendored file itself (now replaced) and, descriptively, in PR #2's evidence README — a historical
record, deliberately left alone. Nothing in this repository reads `key_utf8_warning`.

### Lanes

`vizra-search/docs/evidence/pr3/lanes-local.txt`. arm64, go1.27.1, GNU Make 3.81, python 3.9.6,
govulncheck v1.8.0.

| lane | exit |
|---|---|
| `fmt-check`, `vet`, `echo-containment`, `build` | 0 |
| `vendor-contract-check` | 0 |
| `contract-drift` | 0 — `324 tests ran across 4 package(s), 0 failures, none deselected` |
| `test`, `test-noskip` | 0 — **347 pass events, 0 skips** |
| `tidy-check`, `ci-required-guard`, `check-workflows`, `govulncheck` | 0 |
| `make ci` | 0 |
| `docker-build` | **NOT RUN locally** — arm64 host, amd64 image target (ADR-009 / Q-027); CI runs it on `ubuntu-24.04` |

### PR

- Branch `chore/revendor-core-4a80a1e`, head **`aa1c3fb73b1771b91704587bb1d2a25b7cf39396`**
  (`581bffc` is the re-vendor; `aa1c3fb` is the harness cleanup below).
- PR: https://github.com/yegamble/vizra-search/pull/3

### Follow-up commit `aa1c3fb` — the demo harness removes its own pristine copy

Found by inspecting the machine after the first green CI, not by a test: the harness took a
pristine copy of the three `api/` files into a `mktemp -d` directory and restored from it through
an `EXIT` trap, but never removed the directory, so every invocation left one behind — including a
verifier's. Fixed by restoring **first** and dropping the copy **second** (an interrupt between the
two then leaves the repository correct and only a stray temp directory behind, never the reverse),
with the `rm -rf` guarded by a `case` match on the `mktemp` name pattern.

`docs/evidence/pr3/D-C-after-revendor-red-green.txt` is the re-run with the fix: D-C again reports
**0 unexpected results**, every red still names `TestEveryVendoredFileMatchesItsManifest` and the
mutated file, the vendored digests come back to `a78d8aa7…` and `f95623b0…`, and no
`revendor-demo-pristine-*` directory survives the run. `bash -n` clean;
`./scripts/ci-required-guard.sh` exit 0; `make contract-drift` exit 0 with
`324 tests ran across 4 package(s), 0 failures, none deselected`. No vendored file, manifest, lane,
CI guard or Go source changed in that commit.
### CI on head `aa1c3fb73b1771b91704587bb1d2a25b7cf39396` — the head to verify

`gh api repos/yegamble/vizra-search/commits/aa1c3fb…/check-runs` → **12 check runs, unique
conclusions `["success"]`**. Runs: `ci` https://github.com/yegamble/vizra-search/actions/runs/35572658912,
`ci-required` https://github.com/yegamble/vizra-search/actions/runs/35572658849.
PR `OPEN`, `MERGEABLE`, head unmoved since CI ran.

| check | result | duration |
|---|---|---|
| `fmt` | pass | 31s |
| `vet` | pass | 49s |
| `echo-containment` | pass | 16s |
| `build` | pass | 42s |
| `contract-drift` | pass | 46s |
| `test` | pass | 1m18s |
| `test-noskip` | pass | 46s |
| `tidy-check` | pass | 20s |
| `govulncheck` | pass | 58s |
| `docker-build` | pass | 51s — **the lane not runnable locally** |
| `ci-required` | **pass** | 1m28s |
| GitGuardian Security Checks | pass | 2s |

### CI on the earlier head `581bffc4c116af7eee4f41e7f1157e1a1bd8109a` (superseded)

`gh api repos/yegamble/vizra-search/commits/581bffc…/check-runs` → **12 check runs, unique
conclusions `["success"]`**. Runs: `ci` https://github.com/yegamble/vizra-search/actions/runs/35572202252,
`ci-required` https://github.com/yegamble/vizra-search/actions/runs/35572202254.
The head has not moved since CI ran; the PR is `OPEN` and `MERGEABLE`.

| check | result | duration |
|---|---|---|
| `fmt` | pass | 16s |
| `vet` | pass | 47s |
| `echo-containment` | pass | 17s |
| `build` | pass | 39s |
| `contract-drift` | pass | 47s |
| `test` | pass | 1m30s |
| `test-noskip` | pass | 49s |
| `tidy-check` | pass | 19s |
| `govulncheck` | pass | 51s |
| `docker-build` | pass | 55s — **the lane not runnable locally** |
| `ci-required` | **pass** | 1m49s |
| GitGuardian Security Checks | pass | 2s |

Two CI numbers match local exactly, so nothing was deselected or skipped to get green on Linux:

- `contract-drift` job: `contract-drift: 324 tests ran across 4 package(s), 0 failures, none
  deselected`, preceded by the out-of-make anchor `contract-drift lane: 4 package(s) selected with
  no test-selecting flag (internal/config, internal/contract, internal/hmacauth, internal/httpapi)`.
- `test-noskip` job: `test-noskip: 347 pass events, 0 skips`.

## Blockers and handoff

None.

One item for the chair, reported rather than acted on: core's `api/README.md` also changed at
`4a80a1e` and is **not** vendered in this repository, so nothing here follows from it — noted only
so the chair knows the `api/` diff has three files while the vendored pair has one.

Next action: independent verification of PR #3 against head `581bffc`, then the chair's merge
decision. The builder does not verify or merge its own work.
