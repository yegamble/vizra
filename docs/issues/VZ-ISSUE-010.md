# VZ-ISSUE-010: M1 — backup, restore on a clean host, deploy ordering, rollback scaffolding

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-OPS-001, VZ-BACKUP-001, VZ-BACKUP-002
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Operator: `vizra deploy` with dump → pull → gated migrate → up → probes; `vizra backup` produces DB dump + media manifest with checksums + config/keys archive + service inventory with retention; `vizra restore` on a second clean host reproduces accounts, albums, privacy and originals with 100% checksum match and a working upload afterwards; RTO/RPO measured.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Restore rehearsal record with timings and checksum report
- Failed dump aborts deploy before pull
- Missing KEK → clear failure naming the key

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- transcripts with exit codes on both hosts

## Dependencies / blockers
Second clean host; Q-028 RTO stated for host-local restore of the declared corpus

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
