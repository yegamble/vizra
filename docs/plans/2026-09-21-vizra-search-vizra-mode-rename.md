# Execution plan: vizra-search runtime mode is `VIZRA_MODE` — one operator-facing name per concept

## Context

- Repo: `yegamble/vizra-search`, checkout `/Users/yosefgamble/github/vizra/vizra-search`.
- Base: `origin/main` @ `3619fed873fc194130f02cc85577de10414ade39` (clean).
- Branch: `chore/m0-vizra-mode-rename`.
- Chair's ruling, board queue 2h 2026-09-21: ONE operator-facing name per
  concept. `vizra-core` reads `VIZRA_MODE` = `development|production` (runtime
  mode) and `VIZRA_SEARCH_MODE` = `off|managed|external` (search TOPOLOGY).
  `vizra-search` read `VIZRA_SEARCH_MODE` as `development|production` — the same
  name with an incompatible vocabulary, so a shared env file would stop search
  booting or silently pick a mode. `vizra-search` adopts `VIZRA_MODE`.
- Precedent mirrored for shape, tests and refusal wording: `vizra-core`'s
  `SEARCH_HMAC_KEY` rename — `internal/config/keys.go` (`RetiredKeys`) and the
  production block in `internal/config/config.go`, verified at
  `docs/evidence/warroom/2026-09-21-vizra-core-pr6-hardening-a-VERIFY.md` §3.
  (`vizra-core` is READ-ONLY for this slice; read via `git show origin/main:…`.)
- Out of scope: the CI-guard debts (guard dying on an emptied manifest,
  make-flag overrides on workflow lines, selftest as a lane, `source_ref_tip`
  validation); any contract or vendored file; any behaviour change beyond the
  rename.

## Acceptance

1. Runtime mode is read from `VIZRA_MODE` (`development|production`);
   `production` stays the DEFAULT when unset; every mode-dependent behaviour is
   unchanged, proven by the existing tests with none weakened.
2. `VIZRA_SEARCH_MODE` is no longer read as a runtime mode, and the refusal is
   precise — after this change a shared env file legitimately carries core's
   topology value there:
   - old runtime vocabulary (`development` / `production`, case- and
     whitespace-insensitive) → **refuse to boot by name in every mode**, naming
     `VIZRA_MODE` as the replacement, echoing no value;
   - topology value (`off` / `managed` / `external`) → **ignored silently** (it
     is core's);
   - completely empty value (`VIZRA_SEARCH_MODE=`) → tolerated as a template
     tombstone, mirroring core's retired-key rule;
   - any OTHER value (including whitespace-only) → **refused** (decision: it is
     neither vocabulary; documented, with the forward-compatibility cost).
   - Danger closed: `VIZRA_SEARCH_MODE=development` with no `VIZRA_MODE` must
     NOT silently become production-with-a-dev-key or development — it is the
     refusal. Inverse: `VIZRA_MODE=development` + `VIZRA_SEARCH_MODE=managed`
     boots in development.
3. *demonstrated*: a boot matrix on the REAL binary — unset/unset → production;
   `VIZRA_MODE=development`; old name with old vocabulary alone → refused by
   name; both set with old vocabulary → refused; old name with topology value +
   new name → boots in the new name's mode; garbage for each. Mutations (digest
   before/after, red for the DECLARED reason, harness refuses an unapplied
   mutation): old name read as a fallback → named test red; refusal dropped →
   red; default flipped to development → red.
4. Every place that SETS the variable moves in the same PR: `Dockerfile`,
   `Makefile`, `.github/workflows/ci.yml`, `README.md`, `AGENTS.md`. The
   `ci:` target and the CI guards stay semantically unchanged; workflow edits
   minimal; `required-checks.txt` and the guard stay in agreement.
5. Docs at the strength of the control: the `AGENTS.md` configuration table and
   the "production is the default" paragraph updated, plus a dated note that
   `VIZRA_SEARCH_MODE` now means topology product-wide and is owned by core.

Non-goals: any change to the HMAC boundary, the contract, the lanes, or to what
the modes DO.

## Implementation

- `internal/config/config.go`
  - `EnvMode = "VIZRA_MODE"`.
  - New `EnvSearchTopology = "VIZRA_SEARCH_MODE"` + `SearchTopologyValues`
    (`off|managed|external`, core's vocabulary) + `retiredModeValues`
    (`development|production`, this service's old one).
  - New `(*validator).searchTopology()` classifying the old name, run in EVERY
    mode (unlike core's retired-key check, which sits in the production block:
    here the wrong name changes the MODE ITSELF, so development cannot be the
    mode in which the check is skipped).
- Tests (`internal/config/config_test.go`, `cmd/vizra-search/main_test.go`):
  new cases for each branch; existing cases reference `config.EnvMode` and move
  with it, so the unchanged behaviour is re-proven, not re-written.
- Harness `scripts/boot-matrix.sh` + `make boot-matrix`: real binary, 8 cases,
  three named mutations with digest before/after and an applied-mutation check.
- Setters: `Dockerfile` ENV, `Makefile run`, `ci.yml` docker-build lane (two
  `-e` flags), `README.md`, `AGENTS.md`.
- Meta (NOT edited here, reported to the chair): meta's compose file must
  deliver `VIZRA_MODE` to the search service instead of `VIZRA_SEARCH_MODE`.

## Verification

| Command | Lane |
|---|---|
| `make fmt-check` `make vet` `make echo-containment` `make build` | shape |
| `make contract-drift` | contract |
| `make test` (`go test -race -count=1 ./...`) | behaviour |
| `make test-noskip` | 0 skips |
| `make tidy-check` `make govulncheck` | deps |
| `make ci` | the complete local gate |
| `./scripts/boot-matrix.sh` | boot matrix, real binary |
| `./scripts/boot-matrix.sh --mutate <name>` | the three red demonstrations |
| `./scripts/ci-required-guard.sh` + `scripts/check-workflows.py` | CI guards |
| GitHub `ci-required` on the PR head | acceptance platform (ubuntu-24.04) |

`docker-build` is a CI lane on ubuntu-24.04 (amd64); locally arm64 only, so the
local run carries no acceptance claim (ADR-009 / Q-027).

## Progress and evidence

READY_FOR_REVIEW, fix round 1 of 2 applied. PR
https://github.com/yegamble/vizra-search/pull/4, head
`6a02ab2975a6f5c4da49b5af62b9822ead2e885e`. Round 1 verdict was FAIL at
`852b38291c3ec8109f27ebd924ef48eec3b11a9d` on acceptance bullet 5 only — see
"Fix round 1" below. Base `3619fed`. Host
darwin/arm64, go1.27.1, Docker 29.8.0, gh 2.98.0 — all present at preflight;
nothing was BLOCKED.

### TDD order (transcripts in the session scratchpad, superseded by the committed ones)

1. Tests added first → build failure `undefined: config.EnvSearchTopology`.
2. Constants only, no refusal → behavioural red, including the danger case
   itself: with `VIZRA_SEARCH_MODE=development` alone the process booted
   **production** and the only error was the dev key's, never naming the mode
   variable.
3. `(*validator).searchTopology()` added → green.

### Lanes (exit codes recorded without a pipe)

| Command | Exit | Result |
|---|---|---|
| `make ci` (fmt-check, vet, echo-containment, build, contract-drift, test -race, test-noskip, tidy-check) | 0 | contract-drift 346 tests / 4 packages / 0 deselected; `test-noskip` 371 pass events, **0 skips** |
| `govulncheck ./...` (v1.8.0) | 0 | No vulnerabilities found |
| `./scripts/ci-required-guard.sh` | 0 | floor intact, anchor present, 6 workflow fixtures exercised, base images pinned |
| `python3 scripts/check-workflows.py …` | 0 | 2 workflows parsed, no `continue-on-error` |
| `make vendor-contract-check` | 0 | every vendored file matches the manifest (untouched by this slice) |
| `shellcheck scripts/boot-matrix.sh` | 0 | clean |
| `./scripts/boot-matrix.sh` | 0 | 14 passed, 0 failed |
| `./scripts/boot-matrix.sh --mutate fallback-to-the-old-name` | 0 (red as required) | 11 passed, 3 failed |
| `./scripts/boot-matrix.sh --mutate drop-the-refusal` | 0 (red as required) | 7 passed, 7 failed |
| `./scripts/boot-matrix.sh --mutate default-to-development` | 0 (red as required) | 11 passed, 3 failed |

Transcripts: `vizra-search/docs/evidence/pr4/` (`README.md` maps each mutation
to the boot cases and the named tests it turns red). Every mutation run records
config.go's sha256 before and after, refuses an unapplied patch, and ends by
restoring the pre-mutation digest
`538ba2729e53b66fcc83e9e5416dfa49637a0a92f37182ceb410d98c935b631d`.

### Did NOT run locally

- `docker-build` — the image build is a CI lane on ubuntu-24.04/amd64 (ADR-009 /
  Q-027) and this host is arm64 with little free disk. The Dockerfile `ENV`
  rename and the new "the image refuses the retired runtime-mode name" step are
  verified only by `ci-required` on the PR head.
- `make vendor-contract` / `vendor-contract-selftest` — out of scope; nothing
  vendored changed.

### Fix round 1 (verifier FAIL at `852b382`, acceptance bullet 5 only)

Verdict evidence: `docs/evidence/warroom/2026-09-21-vizra-search-pr4-vizra-mode-rename-VERIFY.md`.
Everything behavioural reproduced; all three findings were documentation
standing stronger than its controls. New head `6a02ab2`, commits on top of
`852b382` (no amend, no force-push).

- **FINDING 2 / chair's ruling (reverses the brief's recommendation).**
  `SearchTopologyValues`, `TestTheTopologyVocabularyIsPinnedToCore` and every
  sentence about pinning or a vocabulary shared with core are deleted.
  `VIZRA_SEARCH_MODE` is now refused ONLY for the old runtime vocabulary; every
  other value — core's, unknown, whitespace-only, empty — is ignored in
  silence. The accepted cost (a typo boots PRODUCTION, the strict mode) is
  stated in AGENTS.md and held by
  `TestNoValueInTheOldNameCanEverProduceDevelopment`,
  `TestAnUnknownRetiredNameValueBootsProduction`, two matrix rows and the new
  mutation `unknown-value-as-development`.
- **FINDING 1.** `TestNoRefusalEchoesTheSuppliedValue` drives every refusal path
  in the loader with a runtime-assembled marker (and checks `Config.String()` /
  `LogValue()` for an ignored value); every matrix refusal row greps the process
  output for the value it supplied, with the two vocabulary words exempt exactly
  as spelled — hence the `  DeVeLoPmEnT  ` row. New mutation `echo-the-value`
  turns both red, by name.
- **FINDING 3 (NIT).** The `docker-build` retired-name step now requires the
  container output to name both variables; the exit-0 and exit-124 branches are
  unchanged.

Matrix grew 13 → 20 boot cases. Lanes re-run: `make ci` 0 (contract-drift 356
tests / 4 pkgs / 0 deselected; test-noskip **384 pass events, 0 skips**),
`govulncheck` 0, `ci-required-guard.sh` 0, `check-workflows.py` 0, `shellcheck`
0, boot matrix 21/21, five mutations red for their declared reasons, restore
digest `84f2c1fe25e5c49dd46d6428bb530f92c6c1c64d1891b45572938c19e226fc73`.

Sentences removed (all were stronger than their controls): "core adding a
topology value must update it here in the same release … is where the list is
pinned"; the `off | managed | external` enumeration in `AGENTS.md`'s table, the
`README.md` line, the `EnvSearchTopology` doc comment and both refusal messages;
"anything else, whitespace-only included → boot refusal"; and the original
decision 2 in the PR body.

## Blockers and handoff

No blocker in this repository. One **cross-repo dependency** the chair must
route, because it is not mine to edit:

`vizra/docker-compose.yml` sets the **search service's** environment literally
to `VIZRA_SEARCH_MODE: production` (recorded at line 329 in
`docs/evidence/warroom/2026-09-21-meta-pr4-compose-topology-VERIFY.md` § "The
`VIZRA_SEARCH_MODE` clash"). Once this PR merges, that key on the search service
becomes a **boot refusal** — which is the designed behaviour, and exactly why
the refusal is loud. Meta must deliver **`VIZRA_MODE: production`** to the
search service instead. Core's own `${VIZRA_SEARCH_MODE:-off}` on the api and
worker services (line 87) is correct as it stands and must not change: that is
the topology, and it is now the only meaning of the name.
