# VZ-ISSUE-003: M0 — `ci-required` fan-in and required-check manifests in every repo

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-CI-001, VZ-CI-004
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Owner: each repo has `.github/required-checks.txt`, `scripts/ci/require-checks.sh` with regression tests, `ci-guard` (SHA pins, no hidden continue-on-error), tombstoned retirement, skip-fails, govulncheck/dependency audit lanes; branch-protection configuration documented.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Deleting a manifest line without tombstone fails
- Renamed job makes ci-required fail
- Skipped required test fails
- Actions pinned to 40-char SHAs

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- CI links; regression test output
- Branch-protection configuration record (enforcement UNVERIFIED if no admin rights, Q-032)

## Dependencies / blockers
Q-032: owner action — apply recorded rulesets after repo creation; add the ruleset drift-check job

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
