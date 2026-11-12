# Execution plan: VZ-FOUND-003 — S1 (migrate up from the release image) and R1 (dirty ledger reported, not repaired)

## Context
Repo yegamble/vizra-core, branch `feat/release-image-migrate-lane`, draft PR https://github.com/yegamble/vizra-core/pull/19. Final head 37a6d55b6e3447902444ee7e5caeb1dd4d8078c9. Continued from a prior builder session.

## Acceptance
- S1: `vizra migrate` from the image built by docker-build.yml (the single-target Dockerfile; no separate release workflow exists yet, so this is the image the release would build) against digest-pinned postgres:18, on an asserted-empty DB; first run must print `APPLIED to version <head>` and leave ledger `<head> false`; second run must print `current at version <head>` and leave the ledger unchanged. Fails closed: `set -euo pipefail`, `migrate | tee` under pipefail (missing binary / non-zero exit fails), exact ledger string compare (dirty fails).
- R1: `internal/integration/migrate_dirty_test.go` TestDirtyLedgerIsReportedNotRepaired: dirty ledger -> Apply errors naming the version, reports nothing applied, Probe says dirty, row unchanged.
- Non-goal: "compatibility window" case — no such mechanism exists; stays open, not invented.

## Implementation
- `.github/workflows/docker-build.yml` step "Assert migrate up from the image applies cleanly on an empty database".
- `internal/integration/migrate_dirty_test.go`.
No migration, OpenAPI or sqlc change in the final diff (manifest equals main).

## Verification
CI only (build-test runs `make ci` incl. integration tests on pinned postgres; docker-build runs S1). Locally: `./scripts/migration-manifest.sh generate`, `make migrate-lint` (passed, 5 migrations, 10 manifest entries).

## Progress and evidence
- R1 RED (commit bd26b16, migrate.go mutated to auto-repair): https://github.com/yegamble/vizra-core/actions/runs/43228490310/job/131217791460 — `--- FAIL: TestDirtyLedgerIsReportedNotRepaired` / `migrate_dirty_test.go:30: migrate up on a dirty ledger returned no error; it must refuse`.
- S1 GREEN on bd26b16: https://github.com/yegamble/vizra-core/actions/runs/43228490805/job/131217792218 (prior session).
- S1 RED (commit 32999a0, temporary 0006_broken): https://github.com/yegamble/vizra-core/actions/runs/43229691824/job/131221389383 — `default FAIL migrate: applying: migration failed: syntax error at or near "TABLEE" ... (SQLSTATE 42601)`, `Process completed with exit code 1`. (build-test on that commit stopped at sqlc-verify on the same file, so R1 green is taken from the final head, not 32999a0.)
- S1 GREEN on final head 37a6d55: https://github.com/yegamble/vizra-core/actions/runs/43230273315/job/131223440387 — `head version in migrations/: 5`, `APPLIED to version 5`, `ledger: 5 false`, `current at version 5`, `ledger: 5 false`, `applied to 5, clean, idempotent`.
- R1 GREEN on final head: https://github.com/yegamble/vizra-core/actions/runs/43230273284/job/131223440785 — artifact build-test-events-b7802e62…: `{"Action":"pass","Test":"TestDirtyLedgerIsReportedNotRepaired"}` in both the ordered and shuffled integration runs (172 integration tests, 0 skipped).
- Final head 37a6d55: append-only, build-test, cache-matrix (redis+valkey), fixtures, govulncheck, docker-build, ci-required all pass.
- image-scan fails (world CVEs, also red on main; deliberately not required per .github/required-checks.txt).
- Mutation commits bd26b16 and 32999a0 remain in branch history (no force-push); squash-merge removes them.

## Blockers and handoff
Did not run locally: Docker, PostgreSQL, integration tests (arm64 host, CI is the target). Independent verifier needed.
