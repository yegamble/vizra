# Execution plan: vizra-core "hardening sweep A"

## Context

- Repo: `yegamble/vizra-core` (private). Checkout `/Users/yosefgamble/github/vizra/vizra-core`.
- Base: `main` at `c043df72f06cc7b5d7237a12d2be4dac25fa788e`, clean (confirmed `git status --porcelain` empty).
- Branch: `chore/m0-hardening-a`. PR against `main`, references `yegamble/vizra#1`.
- Transcripts inside the repo under `docs/evidence/hardening-a/`.

Findings this slice closes (all left open by independent verifiers / the chair):

| Source | Finding | Deliverable |
|---|---|---|
| chair ruling 2026-09-20 | core↔search secret name disagrees with the canonical contract | 1 |
| `docs/evidence/warroom/2026-09-20-vizra-search-pr2-revendor-VERIFY.md` Finding 8 | one Makefile line no-ops every make-driven required lane | 2 |
| `docs/evidence/warroom/2026-09-21-meta-pr3-validate-lane-VERIFY.md` Finding 5 | provenance must name the tree it stands in | 3 |
| `docs/evidence/warroom/2026-09-21-vizra-core-pr5-fixtures-VERIFY.md` V-2 | `fixtures-verify` prints `ok` for 11 or 0 fixtures | 4 |
| same, V-3 | undeclared extra file in `testdata/fixtures` invisible | 4 |
| same, V-4 | AVIF input misattributed to ffmpeg (it was libvips) | 4 |
| same, V-1 residue | `docs/evidence/fixtures/2026-09-21-determinism.md` still says PENDING | 4 |

Out of scope (stated so an absence is not read as an oversight): the public search
endpoint; the `internal/obs` redaction review, image scanning and the clean runtime
stage (sweep B); the nonce store; any migration (0001–0004 are FROZEN).

## Acceptance

1. **NAMING.** `SEARCH_HMAC_KEY` everywhere in `vizra-core`. No compatibility alias.
   Production boot REFUSES, by name, an environment that still sets
   `VIZRA_SEARCH_HMAC_KEY` with a non-empty value. `api/search-hmac-testvectors.json`
   changes exactly one prose string; every positive and negative vector's bytes are
   otherwise unchanged (proved, not asserted).
2. **MAKE INTEGRITY.** (a) An out-of-make workflow step, before any `make` in every
   required lane that invokes make, refuses `SHELL` / `.SHELLFLAGS` /
   `MAKEFLAGS` / `GNUMAKEFLAGS` / `.ONESHELL` overrides and `-`/`@-`-prefixed or
   `|| true`-suffixed recipe lines for the gate targets, in the Makefile AND its
   includes. `ci-required-guard` asserts that anchor step exists, is unconditional
   and is not continue-on-error in each required workflow. (b) At least one REQUIRED
   lane runs `go test ./...` directly, not through make.
   Demonstrated red/green under the real lanes, with a real failing test underneath
   each mutation: SHELL override, `MAKEFLAGS += -i`, an included makefile carrying
   the override, a `-` prefix, `|| true`, a duplicate target replacing a recipe, the
   anchor deleted / made conditional / moved after make.
3. **PROVENANCE.** Every workflow that records the environment prints, each labelled:
   the PR head SHA, the base actually merged in (`git rev-parse HEAD^1` on a
   `pull_request` merge ref — never `github.event.pull_request.base.sha`), and
   `git rev-parse HEAD` (the merge commit tested). `merge_group` and `push` handled.
   Checkout is NOT pinned to the head.
4. **FIXTURES.** `fixtures-verify` (the CLI path, not only the test suite) refuses a
   corpus that is not exactly the twelve ADR-009 items; an undeclared extra file in
   `testdata/fixtures` is reported by name; `internal/fixtures/fixtures.go` names
   libvips and ffmpeg correctly; `docs/evidence/fixtures/2026-09-21-determinism.md`
   carries a dated correction (appended, original text not rewritten).
   Red/green for the count and the extra file.

## Implementation

No migration. No sqlc query. No OpenAPI operation added or removed.

| Area | Files |
|---|---|
| naming | `internal/config/keys.go`, `config.go`, `config_test.go`, `template_test.go`, `.env.example`, `api/README.md`, `api/search-hmac-testvectors.json` (one prose string) |
| make integrity | `scripts/make-integrity-guard.py` (new), `scripts/make-integrity-guard.sh` (new), `scripts/ci-required-guard.py` (anchor checks), `scripts/scripts_test.go`, `scripts/testdata/makeguard/**` (new fixtures), `Makefile`, `.github/workflows/build-test.yml`, `fixtures.yml` |
| provenance | `.github/workflows/*.yml` |
| fixtures | `internal/fixtures/manifest.go`, `fixtures.go` (comment), `internal/fixtures/fixtures_test.go`, `docs/evidence/fixtures/2026-09-21-determinism.md` |
| contract | `AGENTS.md` (the naming rule + the make-integrity row) |

Interface owned by this repo and consumed elsewhere: `api/`. The last-touching `api/`
commit is reported so `vizra-user` and `vizra-search` can re-vendor.

## Verification

Lanes (exact commands, exit codes, counts recorded in "Progress and evidence"):

```
make ci                                  # fmt-check vet lint-imports migrate-lint
                                         # config-template-check openapi-verify
                                         # sqlc-verify ci-guard fixtures-verify test-race
./scripts/make-integrity-guard.sh        # the new out-of-make guard
./scripts/ci-required-guard.sh
go test -race -count=1 ./...             # the direct lane, no make
make test-integration                    # needs PostgreSQL 18 + a RESP server
make test-integration-shuffle
```

Services: PostgreSQL 18 and Valkey/Redis in Docker on non-default host ports, named
`vzha-pg` / `vzha-cache`, removed by name at the end.

Demonstrations: every mutation prints a `sha256` of the mutated file before and after,
so a mutation that failed to apply cannot pass as green; every red is asserted to carry
its DECLARED reason, not merely a non-zero exit.

## Progress and evidence

All transcripts live INSIDE the repo at `vizra-core/docs/evidence/hardening-a/`
(README there explains how to read them). Builder's machine, darwin/arm64,
go1.27.1, GNU Make 3.81 — **not** the ADR-009 acceptance platform.

### Commit

`2ceac77e4cbb30e964335a7adc6cee550fa65485` on `chore/m0-hardening-a`, 82 files,
+3177/-23. No migration, no `api/openapi.yaml` byte, no `sqlcgen` byte.

### Local lanes

| Command | Exit | Notes |
|---|---|---|
| `make ci` | **0** | all ten lanes; 13 packages ok, 8 with no test files, 0 failed, 0 skips |
| `make test-integration` | **0** | PostgreSQL 18.6 (`vzha-pg`, host port 55432) + Valkey (`vzha-cache`, host port 56379) |
| `make test-integration-shuffle` | see `00-lanes.txt` | same suite, `-shuffle=on` |
| `./scripts/make-integrity-guard.sh` | **0** | 8 named gate targets, 17 in the prerequisite closure |
| `./scripts/ci-required-guard.sh` | **0** | 6 required checks; anchors and the direct lane reported on |
| `go test -race -count=1 ./...` (direct) | **0** | via `make ci`'s `test-race`; the workflow now also runs it with no make |

`internal/fixtures` is the slow package under `-race` (102.9 s) — three of the
drift-table cases added here regenerate the corpus. Within the lane's 20-minute
budget, but worth knowing.

### Demonstrations

| File | Mutations | Result |
|---|---|---|
| `D1-retired-name.txt` | delete the `RetiredKeys` refusal loop | red, naming the declared reason; green on restore; digests printed both ways |
| `D2-fixtures-verify.txt` | drop `webm-short` from `Corpus()` + re-pin (V-2); plant `rogue-photograph.jpg` in a full corpus (V-3); plant `.DS_Store` | V-2 and V-3 red by name (both were `ok`, exit 0, at base); the dotfile stays green |
| `D3-make-integrity.txt` | 6 Makefile mutations + 6 workflow mutations, against a clean CLONE, with a real failing test planted underneath | see the file |
| `D4-provenance.txt` | depth-1, depth-2, pinned-to-head, mismatched head, `merge_group`, `push` | pinned-to-head and mismatched-head both exit 1 |

`D3` asserts each mutation's digest MOVED and aborts otherwise. That assertion
earned itself on the first attempt: a `-`-prefix mutation silently failed to
apply (two copies of the demo script were racing on one Makefile) and would
have been reported as a clean red without it.

### Known cost

`internal/fixtures` under `-race` grew from ~60 s to 102.9 s because
`TestManifestDetectsEveryClassOfDrift` gained three cases, two of which
generate the corpus. Not weakened to save time.

## Blockers and handoff

None at plan time. Recorded preflight (2026-09-21, darwin/arm64):
go1.27.1, sqlc v1.31.1, GNU Make 3.81 (system make — note: the runner has GNU Make 4.3,
and the two differ in MAKEFLAGS letter ORDER and in the duplicate-target warning
wording; both were measured, in a container for 4.3, and the guard handles both),
python3 3.9.6 + PyYAML 6.0.3, gh 2.98.0, Docker 29.8.0 with postgres:18, valkey and
redis images present, 34 GiB free.
