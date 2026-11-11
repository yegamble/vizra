# Execution plan: VZ-DESIGN-001 — tokens, typed icon registry, app shell, security headers (vizra-user)

## Context
- Repo `yegamble/vizra-user`, worktree `.claude/worktrees/user-design-001`, branch `feat/design-system-tokens-shell` from `origin/main` `783483f`. Queue 14. Meta checkout read at `e5a5715`.
- Sources read: `features.json` entry VZ-DESIGN-001; `docs/DESIGN_BRIEF.md`; `docs/issues/VZ-ISSUE-008.md` (outcome line); `docs/design/figma/README.md` (D1, in full), `FIRST-SLICE-auth-system.md` §2.7 / §3.7 / §4 / §5.7 / §6 (shell), `FIXES-first-slice.md` header and chair rulings; `OWNER-DECISIONS.md` 2026-11-10 #1 (design accepted); `FOLLOWUPS.md` queue row 5 (security F3 headers); ADR-001 (lucide-react 1.46.x, ISC).
- Budget at start: verdicts 0/4, fix rounds 0/2, re-plans 0/1, ticks 0/12.

## Acceptance
- Success (ledger): "Token file + component catalog + icon registry test that every name exists in the pinned package".
- Negative (ledger): "Unknown icon name fails typecheck".
- Queue row 5: nonce-based CSP with no `unsafe-inline`/`unsafe-eval` in `script-src`, `frame-ancestors 'none'`, Referrer-Policy, nosniff, Permissions-Policy — enforcing, proven by a negative test, asserted on the production image (CI `e2e` lane).
- Hard gate (queue 2f): no spec authenticates, fills a credential or touches a signed URL.
- Non-goals: the other 17 Figma component sets (Button, Dialog, …), the signed-in shell (nav, tab bar, account menu), the signed-out CTAs — their routes do not exist in this repo and a dead link is a defect. They stay in the ledger.

## Implementation
1. `lucide-react` pinned exactly at 1.46.0 (ADR-001 1.46.x; ledger provenance 1.46.0).
2. `design/tokens.css` — `--vz-*` custom properties mirrored from Figma README §2–§3 (light on `:root`, the 36 colour roles redefined for dark under `[data-theme="dark"]` and `prefers-color-scheme`), wired into Tailwind v4 by `@theme inline` in `app/globals.css`; focus-visible and reduced-motion base rules.
3. `components/icons/` — typed semantic registry over static named imports, `Icon` component (decorative, `aria-hidden`), vitest check against the installed package, type-level fixture in the `tsc` lane.
4. `components/shell/` — skip link, sticky frosted top bar with the wordmark, `main#content`; wired in `app/layout.tsx`.
5. `lib/security/headers.ts` + `proxy.ts` (per-request nonce CSP) + `next.config.ts` `headers()` (static headers); unit tests and an e2e spec that reads the real response and proves an un-nonced inline script is blocked.
6. `design/CATALOG.md` + `design/HANDOFF.md` (node references, revision, icon-name verification), with a test tying the catalog to the files.

## Verification
`npm run ci` (lint, typecheck, vitest, build, hygiene); `npm run check:contract`; `bash scripts/ci/check-client-bundle.sh`; `bash scripts/ci/check-e2e-lane.sh`; `npm run e2e` against the local standalone production server; guard scripts under `scripts/ci`. Docker image lanes (`docker-build`, the image half of `e2e`) need a Docker daemon.

## Progress and evidence
### Preflight (2026-11-10)
- Node: `.nvmrc` pins 22.14.0, which is NOT installed here (nvm has 19.9.0, 24.21.0, 26.12.0). Local runs use **24.21.0** (satisfies `engines >=22.13.0`); CI is the 22.14.0 run.
- Docker: daemon not running (`failed to connect to the docker API`) → image build and image-based checks are BLOCKED locally; CI runs them.
- Playwright Chromium `chromium-1243` present in the local cache. `gh` authenticated.
- `npm view lucide-react@1.46.0` → version 1.46.0, licence ISC, peer `react ^16.5.1 || ^17 || ^18 || ^19`, integrity `sha512-Bv+FZXgZ…LJQRAA==` (matches `package-lock.json`). `latest` is 1.71.0; not taken — ADR-001 pins 1.46.x.

## Blockers and handoff
(filled in at the end)

## Demonstrations, red then green (builder session 2, 2026-11-10T19:16:35Z, source 854db27 + lint fix, node v24.21.0)

### D1 icon registry: an entry naming an export lucide-react 1.46.0 does not have
```
mutation: components/icons/registry.ts import 'Bell,' -> 'BellZzz as Bell,'
 2 files changed, 1 insertion(+), 2 deletions(-)
RED

$ npx vitest run components/icons
TypeError: Cannot read properties of undefined (reading 'displayName')
 ❯ components/icons/registry.test.ts:84:93
     82|       .map((part) => part.trim())
     83|       .filter((part) => part !== "" && !part.startsWith("type "));
     84|     const canonical = entries.map(([, component]) => (component as { d…
       |                                                                                             ^
     85|     expect([...imported].sort()).toEqual([...canonical].sort());
     86|     expect(source).not.toMatch(/import \* as|DynamicIcon|lucide-react\…
 ❯ components/icons/registry.test.ts:84:31
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[3/3]⎯
 Test Files  1 failed (1)
      Tests  3 failed | 82 passed (85)
   Start at  14:16:36
   Duration  308ms (tests 58%, import 31%, transform 10%, worker 1%)
exit=1
Updated 1 path from the index
GREEN after restore

$ npx vitest run components/icons
 RUN  v5.0.1 /Users/yosefgamble/github/vizra/.claude/worktrees/user-design-001
 ✓ components/icons/registry.test.ts (85 tests) 149ms
 Test Files  1 passed (1)
      Tests  85 passed (85)
   Start at  14:16:37
   Duration  496ms (tests 59%, import 30%, transform 10%, worker 1%)
exit=0
```

### D2 @ts-expect-error fixture: tsc fails when the expected error is absent
```
mutation: components/icons/icon.typecheck.tsx unknownName = "sparkles" -> "favorite"
 2 files changed, 1 insertion(+), 2 deletions(-)
RED

$ npx tsc --noEmit
components/icons/icon.typecheck.tsx(21,1): error TS2578: Unused '@ts-expect-error' directive.
exit=2
Updated 1 path from the index
GREEN after restore

$ npx tsc --noEmit
exit=0
```

### D3 security headers: one header removed
```
mutation: lib/security/headers.ts Referrer-Policy entry deleted
 2 files changed, 2 deletions(-)
RED

$ npx vitest run lib/security
     89|     const got = new Map(STATIC_SECURITY_HEADERS.map(({ key, value }) =…
     90|     expect([...got.keys()].sort()).toEqual(Object.keys(REQUIRED_STATIC…
       |                                    ^
     91|     for (const [key, pattern] of Object.entries(REQUIRED_STATIC)) expe…
     92|   });
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/3]⎯
 FAIL  lib/security/headers.test.ts > the static security headers > are applied by next.config.ts to every path
TypeError: .toMatch() expects to receive a string, but got undefined
 ❯ lib/security/headers.test.ts:100:67
     98|     const got = new Map((rules?.[0]?.headers ?? []).map(({ key, value …
     99|     for (const [key, pattern] of Object.entries(REQUIRED_STATIC)) {
    100|       expect(got.get(key), `next.config.ts does not send ${key}`).toMa…
       |                                                                   ^
    101|     }
    102|   });
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[2/3]⎯
 FAIL  lib/security/headers.test.ts > proxy.ts > also carries every static header
TypeError: .toMatch() expects to receive a string, but got object
 ❯ lib/security/headers.test.ts:139:76
    137|     const response = run();
    138|     for (const [key, pattern] of Object.entries(REQUIRED_STATIC)) {
    139|       expect(response.headers.get(key), `the proxy response lacks ${ke…
       |                                                                            ^
    140|     }
    141|   });
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[3/3]⎯
 Test Files  1 failed (1)
      Tests  3 failed | 16 passed (19)
   Start at  14:16:41
   Duration  214ms (import 43%, transform 33%, tests 22%, worker 2%)
exit=1
Updated 1 path from the index
GREEN after restore

$ npx vitest run lib/security
 RUN  v5.0.1 /Users/yosefgamble/github/vizra/.claude/worktrees/user-design-001
 ✓ lib/security/headers.test.ts (19 tests) 19ms
 Test Files  1 passed (1)
      Tests  19 passed (19)
   Start at  14:16:41
   Duration  182ms (import 39%, transform 36%, tests 23%, worker 2%)
exit=0
```

git status after:
```
 M app/page.tsx
```
