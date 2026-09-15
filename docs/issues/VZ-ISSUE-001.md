# VZ-ISSUE-001: M0 — create component repositories, pin the toolchain, record ADRs

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-FOUND-001, VZ-FOUND-002, VZ-FOUND-003, VZ-FOUND-004, VZ-FOUND-005, VZ-FOUND-006
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Developer: `vizra-core`, `vizra-user` and `vizra-search` exist with AGENTS.md, lockfiles, pinned Go 1.27.x / Echo v5 / sqlc 1.31.1 / PostgreSQL 18 / Next.js 16.3.x / lucide-react 1.46.x, an OpenAPI source with both-direction drift check, sqlc verify, append-only migrations compiled into the binary with migrate-lint, health/readiness/version probes, and fail-secure production config validation.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Repositories created (needs owner authorization for GitHub writes)
- ADR-001 stack pins and licenses (Echo v5 Q-003, Valkey/Redis Q-004, govips/libvips LGPL Q-034)
- `make ci` in core/search and `npm run ci` in user execute real checks
- Route-without-spec and spec-without-route both fail CI (demonstrated)
- Hand-edited sqlc output fails drift check (demonstrated)
- Production boot refuses dev secrets (demonstrated)

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- Clean-clone build transcript per repo with SHA and exit codes
- CI run links showing deliberate breakage → red → restore → green

## Dependencies / blockers
Q-001…Q-004, Q-034 ratified; GitHub org/owner and repo names confirmed

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
