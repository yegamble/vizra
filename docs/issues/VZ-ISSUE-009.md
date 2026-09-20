# VZ-ISSUE-009: M1 — albums, sub-albums, per-item visibility, album privacy and share grants across every read surface

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-ALBUM-001, VZ-ALBUM-002, VZ-PRIVACY-001
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Photographer: nested albums (cycle-safe), many-to-many membership, cover, ordering; per-item public/unlisted/private; album public/private/link-only/password; revocable share grants; tightening privacy invalidates caches and removes from others' views; second account and anonymous denied on page, thumbnails, metadata, counts, album listing, direct object links, cached responses.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Visibility × viewer × surface matrix passes
- Album cannot become its own descendant; deleting album keeps photos
- Revoked grant 404s immediately incl. cached responses
- Password brute force rate-limited

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- integration + browser negative tests
- cache invalidation test

## Dependencies / blockers
Q-039 decided 2026-09-15 (core visibilities; audiences in VZ-PRIVACY-004, full)

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
