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

(appended as it runs)

## Blockers and handoff

(none yet)
