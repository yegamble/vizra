# VERIFY — vizra-core PR #30, VZ-TOPOLOGY-007 (core part)

- SHA: 6165316b45fd6370bede1102015d791c5b91e6f7 (PR head confirmed unmoved via `gh pr view`; OPEN, branch feat/topology-007-dev-seams)
- Environment: darwin/arm64, Go per go.mod, Docker 29.9.2; fresh clone in `/tmp/vzv-core-pr30-tBHFd6` (deleted after the run)
- Verifier: independent; did not write this code. Verdict 1 of 4 for VZ-TOPOLOGY-007.

## Diff
6 files: `cmd/vizra/doctor.go` (+topologyArgv via `ops.LoadChain`, drops `COMPOSE_FILE`/`COMPOSE_PROFILES` env injection), 3 test files, plan + redgreen evidence. No config code, no generated files, no workflow/manifest/floor change.

## Commands and results
| Command | Exit | Result |
|---|---|---|
| `go test -count=1 ./cmd/vizra ./internal/ops ./internal/setup ./internal/config ./internal/doctor` | 0 | all 5 ok |
| `go test -count=1 -json <same 5>` + `scripts/go-test-report.py --suite unit --floors scripts/test-floors.json --emit-floors` | 0 | measured cmd/vizra 27, config 101, doctor 56, ops 7, setup 28; 0 skips; all above committed floors (18/86/48/4/14) |
| `gh api …/commits/<SHA>/check-runs` | — | ci-required success; append-only, build-test, cache-matrix(+2 legs), fixtures, govulncheck, docker-build success — matches required-checks.txt. image-scan failure: deliberately not required (documented in required-checks.txt); not this PR's gate |

## Mutations (mine), red then green
| ID | Mutation | Red | Restored |
|---|---|---|---|
| V-M1 | `composeBase` += `:docker-compose.override.yml` (internal/setup/topology.go:14) | FAIL TestTopologyComposeGolden (and override check) | green |
| V-M2 | `topologyArgv` on LoadChain error returns bare `docker compose --env-file X config --quiet` (fallback to compose default discovery) | FAIL TestDoctorTopologyArgvHasExplicitFiles: "empty COMPOSE_FILE must be refused" | green |
| V-M3a | refusal loop `continue`s for VIZRA_DEV_FAKE_SEARCH (internal/config/config.go) | FAIL TestEveryEscapeHatchIsRefusedInProduction/VIZRA_DEV_FAKE_SEARCH + realistic-values test | green |
| V-M3b | delete VIZRA_DEV_FAKE_SEARCH from `EscapeHatches` (keys.go) | FAIL TestTemplateHasNoKeyNothingReads (switch then unaccounted) | green |

## Every `docker compose` invocation in core (grep `"compose"`, `Argv(`, `"docker"` over *.go, non-test)
- `internal/ops/ops.go:61` `Chain.Argv` — explicit `-f` per chain entry; used by cmd/vizra/ops.go:125,146, ops.go:159,171 (restart/run via `e.exec`), doctor.go:394.
- `cmd/vizra/ops.go:256`, `cmd/vizra/doctor.go:415` — `docker compose version --short`: loads no project files.
- `cmd/vizra/doctor.go:336` — `docker version`: not compose.
No path invokes compose with default file discovery.

## Live run
Built `cmd/vizra`; project dir with the meta compose files plus a stray `docker-compose.override.yml` defining service `evil`.
- `vizra setup --non-interactive --env env/production.env --set domain=photos.example.test --set release=v0.1.0` → `COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml`, `COMPOSE_PROFILES=core,frontend,edge`.
- `vizra doctor --env env/production.env --project-dir .` → `OK rendered topology COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml …` (no override).
- Doctor's argv with `config --services` → `redis postgres migrate worker api frontend caddy` — no `evil`.
- Before setup (no env): doctor → `BLOCKED rendered topology … has no COMPOSE_FILE` (refuses rather than guessing).

## Claims vs observation
- Production refuses every existing VIZRA_DEV_* seam (7), table-driven over `EscapeHatches`: CONFIRMED (V-M3a/b). Plain-http origin / CORS / secret refusals are core #25 behaviour, unchanged here; covered by the green config suite, not re-mutated.
- Doctor previously relied on COMPOSE_FILE env; now explicit -f, empty refused: CONFIRMED (diff + V-M2 + live).
- Setup never puts override/dev files in the production chain: CONFIRMED (V-M1 + TestProductionChainNeverIncludesOverride).
- Builder M1–M3 in docs/evidence/topology-007/redgreen.txt: independently reproduced by equivalent mutations above.

## Cases
- CLOSED: production refuses every existing dev seam; override never auto-loaded by core (setup chain, doctor, ops).
- OPEN (not claimed by this PR): rate-limit-off and mail-capture seams do not exist in core; `make dev`/`dev-hot` and the meta-side shapes check are meta work.

## Findings
- **F-1 FOLLOW-UP** (floors): generator formula on this head proposes cmd/vizra 18→23, internal/setup 14→24, internal/ops 4→5; floors not raised, so the new tests (and earlier slices') can be deleted with floors green. Not blocking: the product gate itself is proven by tests that do run; floor owner should regenerate.
- No BLOCKING findings.

FINAL VERDICT: PASS — SHA 6165316b45fd6370bede1102015d791c5b91e6f7
