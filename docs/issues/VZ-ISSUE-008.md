# VZ-ISSUE-008: M1 — first-slice UI: shell, sign-in, uploader, library, viewer, album dialog with design system and accessibility

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-DESIGN-001, VZ-VIEWER-001, VZ-LIBRARY-001, VZ-A11Y-001, VZ-RESPONSIVE-001, VZ-CONTROLS-001
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Everyone: approved tokens/components/typed icon registry from Prompt 02; production-build routes for shell, claim/login, upload, library, viewer (Esc/arrows/zoom/focus return), album create/add; every control from docs/quality/ui-controls.json first-slice rows works with loading/error/disabled states; WCAG 2.2 AA with axe + manual review; 390/1440 light/dark screenshots.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Keyboard-only journey recorded
- axe serious/critical zero; manual keyboard/screen-reader review recorded with reviewer
- No unlisted controls; no dead controls (audit)

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- browser traces and screenshots
- control inventory audit report

## Dependencies / blockers
Prompt 02 design acceptance

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
