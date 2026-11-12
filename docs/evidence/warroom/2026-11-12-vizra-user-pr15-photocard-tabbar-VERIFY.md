# VERIFY — vizra-user PR #15 (VZ-DESIGN-001: PhotoCard 12:263, TabBar Item 15:31, TabBar 15:32)

- SHA: 4f9918682eba78afcc6c0187d0d5b447506d13f6 (PR head checked at start and end, unchanged; draft)
- Verifier: independent vizra-verifier (did not write the code). Date 2026-11-12.
- Environment: darwin, Node v24.21.0 (nvm), fresh clone in mktemp dir, `npm ci` exit 0, only ./node_modules/.bin binaries.

## Commands
| Command | Exit | Result |
|---|---|---|
| git diff origin/main...HEAD --stat | 0 | 5 files: PhotoCard.tsx, TabBar.tsx, components4.test.ts, design/CATALOG.md, design/HANDOFF.md |
| npm run lint | 0 | clean |
| tsc --noEmit | 0 | clean |
| vitest run | 0 | 27 files, 883 tests passed, 0 skipped |
| npm run check:hygiene | 0 | 348 sources OK, 17 mutation digests match |
| npm run build | 0 | built |
| own leak probe (as any; src, srcSet, style backgroundImage, href, alt; sensitive+loading x 3 aspects) | 0 | 1/1 pass: no SECRET, <img, <link, srcset, background-image in markup |
| M1 Sensitive renders <img> | red | 3 failed / 14; restored |
| M2 drop aria-current | red | 2 failed / 14; restored |
| M3 optional onClick with `?? (() => {})` default | GREEN (survived) | 14/14 pass, tsc 0; restored |

## Results
A. Scope PASS: no dependency, lockfile, workflow, harness or AGENTS.md change.
B. Spec PASS: PhotoCard Aspect {landscape 3:2, square, portrait 4:5} x State {default, sensitive, loading} = 9, all tested; none invented. Departure 1 (actions in a figcaption bar, no hover overlay), 2 (object-contain, cover/fill asserted absent), 3 (favourite aria-pressed; rating not drawn). PRIVACY: the only <img> is inside the `state === "default"` branch; no prop spread onto DOM, so casting extra src props into a sensitive/loading card still leaks nothing (own probe). Reveal goes through the caller's onReveal. Loading = Skeleton, aria-busy, no image. Blank alt throws; @ts-expect-error type tests for missing alt / sensitive src. Actions are IconButton (native button) with required label + required onClick. TabBar Item Selected x State (focus-visible ring) = 4; `<a>` with aria-current="page" only when selected; TabBar = `<nav aria-label>`, 72px; min-h/min-w-touch-min (44px); token classes only (h-[72px]/backdrop-blur-[20px] are Figma dimensions).
C. All lanes green; M1, M2 caught; M3 not caught (follow-up).
D. CI on exact SHA: ci-required, frontend, contract, e2e = success; GitGuardian success; deps-scan/image-scan failure (red on main, not in manifest, lockfile unchanged).
E. Ledger: with #11, #13 and #15 every section-5 component has a file in components/ui (or shell); TopNav 15:74 is superseded by TopNav/M1 30:770 → components/shell/TopBar.tsx, which HANDOFF.md:49 marks PARTIAL (wordmark only). The 1-5 rating control is NOT a section-5 component (only the `rating` icon, HANDOFF.md:76, and departure 3); it is not owed by VZ-DESIGN-001. Remaining besides the brand mark (owner inbox 20): TopBar PARTIAL, and no production route renders PhotoCard or TabBar yet (CATALOG.md:124) — components are presentational, not product-proven, so VZ-DESIGN-001 should not go VERIFIED on its outcome until used in a route.

## Findings
- BLOCKING: none.
- FOLLOW-UP (vizra-user): no test pins "no no-op default action" — M3 (optional onClick with no-op fallback) survives tests and tsc; add a @ts-expect-error for a missing onClick.

## Not run
Production-mode browser/screenshot pass (no route renders these components); Figma pixel comparison.

FINAL VERDICT: PASS — SHA 4f9918682eba78afcc6c0187d0d5b447506d13f6
