# VERIFY — meta PR #17 (queue 3c, VZ-FOUND-006: compose delivers core's new config keys)

- Verifier: independent vizra-verifier (did not write the code). Date 2026-11-11.
- Subject: https://github.com/yegamble/vizra/pull/17 head `ad86e2436a94fd137cd9b30e51bc6f4a7cc8d92c` (gh headRefOid equal at start and at end). Base origin/main `f990008bd693e991a3ab38d317b2d7b54dffcab6`.
- Core read at `5f615d74e840b23d2201b1d78dd89abfef07701b` (fresh clone).
- Environment: macOS (Darwin 25.5.0), Docker Compose v5.6.1, python3; fresh clones in a private `mktemp -d` scratch dir, deleted at the end.

## Commands and exit codes

| # | Command (in the meta clone at the SHA) | Exit | Result |
|---|---|---|---|
| 1 | `git diff origin/main...HEAD --stat` | 0 | 7 files, +302/-10 (see A) |
| 2 | `./scripts/compose-render.py --all --out $D/models` | 0 | 13 shapes rendered |
| 3 | own script `tbl.py` over rendered models | 0 | table in B |
| 4 | `python3 scripts/check-config-coverage.py $D/models` | 0 | 37 component keys, 60 template keys, 13 shapes, 0 violations |
| 5 | `python3 scripts/check-config-coverage.py` (no dir, no build/) | 2 | UNEVALUABLE, fails closed (needs models dir) |
| 6 | `python3 scripts/check-config-coverage.py --drift` (core symlinked as `vizra-core`) | 2 | BLOCKED: vizra-user and vizra-search checkouts absent; script is all-or-nothing, prints no core lines. NOT a pass. |
| 7 | `python3 scripts/check-compose-topology.py $D/models` | 0 | 13 shapes, 28 rules, 0 violations, 2 known-false probes named |
| 8 | `python3 scripts/check-compose-topology.py` (no dir) | 2 | usage, fails closed |
| 9 | `python3 scripts/check-doc-links.py` | 0 | 32 links resolve |
| 10 | `python3 scripts/check-quality-json.py` | 0 | 192 ids, all references resolve |
| 11 | `bash scripts/check-generated-ledger.sh` | 0 | byte-for-byte, statuses PLANNED:192 |

## A. Diff scope — OK
Files: docker-compose.yml, docs/plans/2026-11-11-meta-3c-compose-config-keys.md, env/development.env.example, env/production.env.example, env/registry/core.json, scripts/check-compose-topology.py, scripts/check-config-coverage.py. No workflow, required-checks, AGENTS.md, .claude/, docs/issues, docs/adr or ledger change. Both script diffs are additions only (+38, +22): one rule name added to each RULES set, one new function/block, one new call; no existing rule removed or loosened. core.json also moves `vizra healthcheck` from future_commands to commands and adds `vizra claim-token` (both shipped at core 5f615d7 per the snapshot note; not independently checked against cmd/vizra/main.go beyond healthcheck.go existing).

## B. Independent key count — OK
- Core `internal/config/keys.go` at 5f615d7: 32 distinct `Name:` entries = 25 non-dev keys + 7 `VIZRA_DEV_*` hatches. `config.Load` = `LoadFrom(os.LookupEnv)` (config.go:131); no other `os.Getenv` in non-test core code outside healthcheck/doctor passing LookupEnv.
- `env/registry/core.json` at PR head: `keys` = 25 names, `escape_hatches` = the same 7 `VIZRA_DEV_*`. `comm -3` of core's 25 vs registry's 25: empty. Identical sets.
- Rendered-model delivery (own script, 25 non-dev core keys vs each service `environment`):

| Shape | api absent | worker absent | STORAGE_ROOT / media_data mount (api, worker) | ANNOUNCE / TTL |
|---|---|---|---|---|
| bundle-no-checkouts | 0 | 0 | /var/lib/vizra/media = /var/lib/vizra/media | off / 1h |
| dev-build-from-checkouts | 0 | 0 | equal | off / 1h |
| dev-default | 0 | 0 | equal | off / 1h |
| prod-all-optional | 0 | 0 | equal | off / 1h |
| prod-default | 0 | 0 | equal | off / 1h |
| prod-external-both | 0 | 0 | equal | off / 1h |
| prod-external-clickhouse | 0 | 0 | equal | off / 1h |
| prod-external-ipfs | 0 | 0 | equal | off / 1h |
| prod-external-postgres | 0 | 0 | equal | off / 1h |
| prod-external-redis | 0 | 0 | equal | off / 1h |
| prod-external-tls | 0 | 0 | equal | off / 1h |
| prod-frontend-only | not rendered | not rendered | n/a | n/a |
| prod-worker-split | not rendered | 0 | equal (worker) | off / 1h |

No core key is absent wherever api or worker is rendered. (The 7 dev hatches are deliberately not delivered in production; not counted.)

## C. Values — OK
- Core defaults: keys.go:72 `VIZRA_OWNER_CLAIM_ANNOUNCE` default `off`; keys.go:73 `VIZRA_OWNER_CLAIM_TTL` default `1h`; keys.go:51 `VIZRA_STORAGE_ROOT` default `/var/lib/vizra/media`. Validation: config.go:263 `mustDuration` for TTL; config.go:264-269 ANNOUNCE lower-cased, must be `off` or `stderr`; config.go:287-289 storage root must be absolute. Compose values pass all three.
- Override: compose uses `${VIZRA_OWNER_CLAIM_ANNOUNCE:-off}` / `${VIZRA_OWNER_CLAIM_TTL:-1h}`. Rendering prod-default with `VIZRA_OWNER_CLAIM_ANNOUNCE=stderr VIZRA_OWNER_CLAIM_TTL=30m VIZRA_STORAGE_ROOT=/x` gave api and worker `stderr`, `30m`, and STORAGE_ROOT still `/var/lib/vizra/media` (literal, not operator-settable, as claimed). x-core-env is shared by every shape, so the form is the same in all.
- Security meaning: `stderr` writes the live owner-claim token to the container log (keys.go:72 doc; internal/ownerclaim/announce.go:83 `if mode != AnnounceStderr` and :111). Compose default and both templates ship `off`, which is core's own default: production does not announce a token unless the operator opts in. No auth finding.
- STORAGE_ROOT literal equals the `media_data` mount target on api and worker in all 12 shapes that render them (table B).

## D. Mutations (mine; each restored with `git checkout`, tree clean afterwards)

| # | Mutation | Checker | Exit | Rule that fired |
|---|---|---|---|---|
| M1 | delete VIZRA_OWNER_CLAIM_TTL from the worker `environment` only, in the rendered models (api and worker share one YAML anchor, so it cannot be done in the source without restructuring) | check-config-coverage.py | 1 | `service-key-missing` subject `<shape>/worker/VIZRA_OWNER_CLAIM_TTL` |
| M2 | delete VIZRA_OWNER_CLAIM_ANNOUNCE line from env/production.env.example | check-config-coverage.py | 1 | `registry-key-untemplated` env/production.env.example/VIZRA_OWNER_CLAIM_ANNOUNCE (1 violation) |
| M3 | compose `VIZRA_STORAGE_ROOT: /var/lib/vizra/elsewhere`, re-render all | check-compose-topology.py | 1 | `storage-root-mount` api and worker, every shape |
| M4 | worker mount `media_data:/srv/media` (docker-compose.yml:284), re-render prod-default | check-compose-topology.py | 1 | `storage-root-mount` service=worker (1) |
| M5 | add `VIZRA_FAKE_VERIFIER_KEY` to env/registry/core.json with no consumer (N2) | check-config-coverage.py | 1 | `service-key-missing` for api, worker, migrate in every shape |
| M6 | delete VIZRA_OWNER_CLAIM_TTL from env/development.env.example only | check-config-coverage.py | 1 | `registry-key-untemplated` env/development.env.example/VIZRA_OWNER_CLAIM_TTL — RED |

CI wiring: .github/workflows/validate.yml:271 renders all shapes, :289 runs `./scripts/check-compose-topology.py build/compose-models`, :297 runs `./scripts/check-config-coverage.py build/compose-models`. Both are steps of the `validate` job; `.github/required-checks.txt` lists `validate` (the floor lane). The new rules run inside a required lane: not a false green.

## F. CI on the exact SHA — green
`gh run list --commit ad86e24…`: `validate` run 43061735494 completed/success headSha ad86e2436a94fd137cd9b30e51bc6f4a7cc8d92c; `ci-required` run 43061735569 completed/success, same headSha. `gh pr checks 17`: ci-required pass, validate pass, GitGuardian pass.

## Findings

| # | Class | Finding |
|---|---|---|
| — | BLOCKING | none |
| F1 | FOLLOW-UP | `check-config-coverage.py --drift` is all-or-nothing: with vizra-core present and user/search absent it exits 2 without comparing core, so a core-only drift check cannot be run on its own. |
| F2 | FOLLOW-UP | N2 limit: CI checks the snapshot env/registry/core.json; a key added to core after 5f615d7 is invisible to meta CI until someone re-snapshots (drift check cannot run in CI). |
| F3 | FOLLOW-UP | M1 can only be made on rendered models; `api-worker-asymmetry`/`service-key-missing` cover it, fine — recorded only so the demonstration is not read as a source mutation. |

## Per-case table, VZ-FOUND-006

| Case | State after this PR | Proof / what is missing |
|---|---|---|
| S1 every key config.Load reads reaches api and worker (rendered compose) | Proven statically for core 5f615d7 | Table B (own script) + `service-key-missing` red in M1/M5 + `validate` green. Limit: against the snapshot, not a booted container. |
| S2 every key `vizra setup` writes exists in the template | MISSING | `vizra setup` does not exist (core commands: version, doctor, migrate, healthcheck, claim-token). Nothing to assert. |
| N1 production boot with dev JWT/session secret fails | NOT PROVEN HERE | Not touched by this PR and not run by me; no boot-refusal transcript (evidence_required). Belongs to core's config tests / a booted stack. |
| N2 a key added to config without template/compose consumer fails CI | Proven for the meta side | M5 red (no compose consumer), M2 and M6 red (missing from either template), in the required `validate` lane. Missing: a key added in core later is invisible until the snapshot is refreshed (F2). |
| P1 log denylist test proves tokens/passwords/signed URLs never appear | MISSING | The two integration tests were not run; this PR adds none. Only the config default (`off`) was verified. |

Ledger: VZ-FOUND-006 cannot be recorded IMPLEMENTED or VERIFIED after this merge. Missing: S2 (no `vizra setup`), N1 boot-refusal transcript, P1 integration tests; N2 carries the snapshot limit. S1 and the meta half of N2 are the parts this PR delivers.

## Not run
- `--drift` core comparison via the repo script (BLOCKED, row 6); replaced by my own set comparison in B.
- No stack booted; no core tests run; user/search drift out of scope.
- `vizra claim-token` presence in core cmd/vizra/main.go not read.
- FOLLOWUPS.md not appended (brief restricts writes to this file); follow-ups are F1-F3 above.

FINAL VERDICT: PASS — SHA ad86e2436a94fd137cd9b30e51bc6f4a7cc8d92c
