# Plan — vizra-user VZ-DESIGN-001 remainder (queue 14)

- Repo/branch: yegamble/vizra-user `feat/design-001-components` from 53a39a8; PR #13 (draft).
- Acceptance: VZ-DESIGN-001 — evidence_required "design handoff record with node references".
- Source: meta docs/design/figma/README.md §1/§2/§5/§7, FIRST-SLICE-auth-system.md; file key JXgRItauynmT0g8vSJB3oR rev 2026-09-20, accepted 2026-11-10.

## Steps
1. design/HANDOFF.md — tokens/components/icons with copied node ids. IMPLEMENTED.
2. components/ui Button (7:146), IconButton (8:104), TextField (9:42). IMPLEMENTED. Remaining 18 components PLANNED.
3. Brand mark — not defined in the accepted design (README §6 #14, Q-002). Owner item.
4. Unit tests components/ui/components.test.ts: 16 tests; mutation (drop Primary hover/pressed classes + aria-busy) → 2 failed/14 passed; restored → 16 pass.
5. Browser pass + CSP mutation — see PR #13 body.

## Environment
Local Node v19.9.0 default; gates run with Node v24.21.0 (.nvmrc says 22.14.0, not installed).

## Session 2 (2026-11-12, worktree user-design-001b, branch feat/design-001-components)

Built (components/ui/, tests in components/ui/components2.test.ts): Textarea, Select, Checkbox (off/on/mixed via DOM `indeterminate`), RadioGroup (fieldset/legend), Switch (native checkbox + role=switch: native checked state, Space, form submit and disabled with no script), Chip (button aria-pressed + check icon), Tabs (tablist, roving tabindex, Left/Right/Home/End via pure `nextTabIndex`). HANDOFF.md and CATALOG.md updated.

Controlled mutation (before Select): Textarea `aria-invalid={error ? true : undefined}` → `aria-invalid={undefined}`: `vitest run components/ui/components2.test.ts` → 1 failed | 2 passed (Error state test). Restored → `vitest run components/ui` 19 passed.

| Command (Node 24.21.0) | Exit | Result |
|---|---|---|
| `./node_modules/.bin/tsc --noEmit` | 0 | — |
| `./node_modules/.bin/vitest run components/ui` | 0 | 37 passed |
| `npm run lint` | 0 | — |
| `./node_modules/.bin/vitest run` | 0 | 25 files, 855 passed |
| `npm run check:hygiene` | 0 | OK, 337 sources |
| `npm run build` | 0 | compiled, routes listed |

Remains: PhotoCard, Avatar, TabBar Item/TabBar, TopNav, Dialog, Toast/Inline status, Banner, Skeleton, EmptyState, ErrorState. Not browser-exercised this session (SSR markup + pure-function tests only; no jsdom in deps). Follow-ups: Chip uses h-control-sm (check 44px target vs Figma); Tab keyboard handler is tested via `nextTabIndex`, not a DOM event; Checkbox indeterminate tested via `applyMixed`, not in a browser.

## Session 3 (2026-11-12, vizra-user feat/design-001-components)
- Chip: design draws the pill at 32px (`size/control-sm`); kept visual size, hit area extended to 44px (`min-h-touch-min`) like IconButton. Commit bcbc9d5.
- Built Avatar (14:56), Skeleton (17:72), EmptyState (17:95), ErrorState (17:96), Banner (17:68), Toast/Inline status (17:40) — 3c1af27; Dialog (16:43, native `<dialog>`+`showModal()`) — fa99ca3.
- Mutation: dropped `aria-live` from Toast success/info → vitest components/ui 1 failed / 48 passed; restored → 49 passed.
- Not built: TabBar Item/TabBar (need routes that do not exist), PhotoCard (Sensitive/Loading states need a data/moderation contract; deferred). TopNav superseded by shell TopBar.
- Browser pass: existing `e2e/specs/shell.spec.ts` already asserts landmarks, skip link and dark/light body background at 1440 and 390 (both required projects); no new spec added. Component-level browser pass (Dialog focus return/Escape) is NOT possible without a test-only route — chair to decide.
- Local: full vitest 26 files / 869 passed; check:hygiene 0; check:contract 0; build see PR. Playwright not run locally.
