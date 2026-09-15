# VZ-ISSUE-006: M1 — upload session, real-byte validation, quota, durable jobs, local storage

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-UPLOAD-001, VZ-UPLOAD-003, VZ-QUOTA-001, VZ-JOBS-001, VZ-STORAGE-001, VZ-FOUND-007
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Photographer: file picker/drop/paste upload → quota reservation → session → quarantine → sniff/limits → idempotent finalize → outbox job → atomic publication; local storage under a named volume; private objects only via authorized handlers; fixture corpus with hashes.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- JPEG/PNG fixtures upload and survive restart
- Wrong type, oversized, polyglot SVG, truncated rejected with tests
- Duplicate finalize returns one asset; crash between object write and finalize leaves no visible orphan
- Concurrent uploads cannot exceed quota
- Anonymous GET of original/thumbnail 403/404

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- integration tests; fault-injection transcript (worker kill)
- fixture manifest committed

## Dependencies / blockers
Q-028 budgets proposed

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
