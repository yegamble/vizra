# VZ-ISSUE-012: M2 — settings registry, admin console, moderation queue with audit

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-ADMIN-001, VZ-ADMIN-002, VZ-MOD-001, VZ-UPLOAD-012, VZ-REPORT-001
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Owner/manager: DB-backed settings registry (validated, effective values, no restart, audited) for website/content/uploads/users; admin listings with bulk actions and shortcuts; moderation queue for reports and pending uploads (disabled/guest/all) with approve/reject/flag and audit; pending assets hidden on every surface until approved.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Settings count test; change effective immediately
- Pending asset invisible in listings/search/embeds/API/object links
- Approve twice safe; manager denied settings; every action has an audit row

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- integration + browser tests; audit query output

## Dependencies / blockers
none

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
