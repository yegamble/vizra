# VZ-ISSUE-002: M0 — meta compose topology with production overlay and external-datastore overlays

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-TOPOLOGY-001, VZ-TOPOLOGY-002, VZ-TOPOLOGY-003, VZ-TOPOLOGY-006, VZ-TOPOLOGY-007, VZ-CI-002, VZ-OPS-008
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Operator: `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml`, `docker-compose.external-postgres.yml`, `docker-compose.external-redis.yml` (plus placeholder overlays for ClickHouse/IPFS that render OFF) exist; every shape in docs/META_REPO.md §2 renders; postgres/redis/search publish nothing; api/frontend loopback; caddy on the edge profile; Compose ≥ 2.24.4 asserted by rendered model.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- `validate` lane renders default, external-TLS, worker, all-optional, external PG, external Redis, both, bundle-without-checkouts
- Port-closure, restart-policy, log-cap, one-shot no-build, config-key coverage assertions pass
- Invalid external DSN fails render/boot with an actionable message

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- validate lane logs
- rendered models attached as artifacts

## Dependencies / blockers
Q-017 decided 2026-09-15: Compose floor 2.24.4; base file publishes no ports

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
