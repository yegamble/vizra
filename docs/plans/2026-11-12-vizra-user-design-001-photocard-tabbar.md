# Execution plan: VZ-DESIGN-001: PhotoCard, TabBar Item, TabBar (presentational)

## Context
yegamble/vizra-user, base origin/main 0bb8dc6, branch `feat/design-001-photocard-tabbar` (worktree user-design-001c), PR #15. Design: docs/design/figma/README.md (PhotoCard `12:263`, TabBar Item `15:31`, TabBar `15:32`, §6 departures 1-3).

## Acceptance
Every Aspect×State variant of PhotoCard; caller-supplied src/alt (non-empty)/dimensions/actions (named native buttons, persistent bar below the image); Sensitive renders no <img>/src until the caller reveals it; Loading is a Skeleton with no image request. TabBar items are <a> with aria-current=page when selected; the nav is named; 44px targets. Non-goals: no route renders these yet; rating radiogroup; brand mark (owner inbox 20); TopNav (replaced by the shell TopBar).

## Implementation
components/ui/PhotoCard.tsx, components/ui/TabBar.tsx, components/ui/components4.test.ts; design/HANDOFF.md and design/CATALOG.md statuses.

## Verification
Through quiet.sh: tsc --noEmit, vitest run, npm run lint, npm run check:hygiene, npm run build. Controlled mutation: Sensitive renders an <img>.

## Progress and evidence
Commit 4f99186, Node 24.21.0, darwin: tsc PASS; vitest 27 files / 883 tests PASS; lint PASS; hygiene PASS; build PASS. Mutation: 3 failed / 11 passed, then 14 passed after revert. State: IMPLEMENTED, not verified; CI pending on PR #15.

## Blockers and handoff
None for this slice. Next: an independent verifier, then CI green, then ready for review.
