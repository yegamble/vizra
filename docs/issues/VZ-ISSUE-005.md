# VZ-ISSUE-005: M1 — owner claim, sessions, roles

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-INSTALL-003, VZ-AUTH-001, VZ-AUTH-004
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Operator/member: unclaimed instance answers 403 on every signup path; one-time token minted at boot, hash stored, claim page creates the owner; email+password registration (when open), sign-in/out, server-side revocable sessions, CSRF; roles owner/admin/manager/member/guest enforced per route.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Claim race yields one owner; reused token rejected; restart re-mints
- Revoked session denied; CSRF missing → 403
- Role matrix test per route

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- integration tests on real PostgreSQL/Redis with counts
- owner_claim_race test output
- negative tests that fail against a controlled mutation

## Dependencies / blockers
none

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
