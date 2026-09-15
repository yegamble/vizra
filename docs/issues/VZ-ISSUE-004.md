# VZ-ISSUE-004: M0 — installer, `vizra setup` wizard, deployment bundle, boot lane

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-INSTALL-001, VZ-INSTALL-002, VZ-INSTALL-004, VZ-OPS-002, VZ-OPS-003, VZ-CI-003
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Operator: `install.sh` (idempotent, resumable, checksum-verified bundle + CLI, hands to setup, never writes secrets), `vizra setup` (interview, `--web` loopback, `--non-interactive`, `--check`, `--rotate`), `deploy/make-bundle.sh` deterministic, `vizra doctor/status/logs/restart/update`, and the meta `boot` lane that boots production mode from source and runs migration one-shots from service images.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Fresh VM transcript: install → setup answers file → tree + CLI installed; second run changes nothing
- Every wizard answer lands on a template key (CI assert); `--check` validates
- Bundle byte-identical twice; renders with no checkouts
- boot lane: /readyz 200; migrate one-shots exit 0

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- install transcript with exit codes on the declared target
- setup unit tests keyed by question
- boot lane logs artifact

## Dependencies / blockers
Target VM access; lab hostname

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
