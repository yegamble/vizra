# VERIFY — vizra-user PR 11 — VZ-DESIGN-001

- Subject: https://github.com/yegamble/vizra-user/pull/11, head `505fb281cd9fb4dd89f76aae7317a5bf8d9593c6` (confirmed with `gh pr view` at start).
- Environment: macOS arm64, fresh clone in a `mktemp -d` scratch dir. `.nvmrc` = 22.14.0, engines `>=22.13.0`; no Node 22 on this machine, so Node **v24.21.0** was used (deviation). The first `npm ci` under the shell default v19.9.0 gave a broken install and is discarded.

## Commands so far

| Command | Exit | Result |
|---|---|---|
| `npm ci` (Node 24.21.0) | 0 | |
| `npm run lint` | 0 | clean |
| `npx tsc --noEmit` | 0 | clean |
| `npx vitest run` | 0 | 22 files, 814 passed, 0 skipped, 0 failed |
| `node scripts/ci/check-source-hygiene.mjs` | 0 | OK |
| `npm run build` (local, macOS) | **1** | NOT REPRODUCED locally: Turbopack `Cannot find native binding` from `@tailwindcss/oxide` while evaluating `app/globals.css`, although `node -e "require('@tailwindcss/oxide')"` loads. Treated as a local-environment failure, not yet proven either way; CI `frontend` (which runs the build) is success on this SHA. Docker daemon is not running on this machine, so the image build could not be used either. |
| `./node_modules/.bin/next build --webpack` | 0 | builds; all routes dynamic, `Proxy (Middleware)` present. Used ONLY to serve the app for check C; it is not the bundler CI ships. |

## B. Demonstrations (my own mutations, each restored, tree clean afterwards)

| # | Mutation | Result |
|---|---|---|
| B1 | `components/icons/registry.ts`: `Heart` -> `HeartZzzNope as Heart` | `npx vitest run components/icons` exit 1, 3 failed (`favorite is an export of the installed package`, canonical-export, canonical-names); tsc also TS2305. REPRODUCED |
| B2 | `icon.typecheck.tsx`: `IconName = "sparkles"` -> `"favorite"` under its `@ts-expect-error` | `npx tsc --noEmit` exit 2, `TS2578: Unused '@ts-expect-error' directive` at line 21. REPRODUCED (unknown name is a type error) |
| B3 | `lib/security/headers.ts`: removed the `X-Content-Type-Options` entry | `npx vitest run lib/security` exit 1, 3 failed / 16 passed. REPRODUCED |

After restore: `git status --short` empty, tsc 0, the two suites 104 passed.

## F. CI on the exact SHA (check-runs API)

`ci-required` success; `frontend`, `contract`, `e2e`, `guard`, `docker-build` all completed/success on 505fb281 — every entry of `.github/required-checks.txt` ran and passed. `deps-scan` and `image-scan` failure; both are DELIBERATELY ABSENT from the required manifest (stated in the manifest itself).

- deps-scan (`npm audit --audit-level=high`): 17 vulnerabilities (12 moderate, 4 high, 1 critical) in `next` (critical), `sharp`, `source-map-js`, `vite`, `vitest`/`@vitest/mocker`, `minimatch`, `launch-editor`, `zod`. None names `lucide-react`.
- image-scan (trivy HIGH,CRITICAL): `next` 5, `sharp` 1; nothing else in the image summary rows read.
- The PR's lockfile diff is exactly one added package (`lucide-react` 1.46.0, with `integrity`), so every flagged package version is identical on main. Main's latest supply-chain run (35898972397, 2026-09-23, 783483f3) was green: the advisories were published since, they are not introduced by this PR. FOLLOW-UP (pre-existing, but `next` 16.3.5 critical/high advisories reach shipped code on main and need an owner-visible bump).

## C. Security headers on a running production build (`next start -p 3977`, webpack build, see above)

`curl -sI /` and `/health`: HTTP 200; header is `content-security-policy` (no `-Report-Only`); `script-src 'self' 'nonce-<22 chars>==' 'strict-dynamic'`; the nonce differed between the two requests (`mZBxxQ3x...` vs `jrIHKsh/...`) and a third GET; no `unsafe-inline` / `unsafe-eval` anywhere; `x-content-type-options: nosniff`, `referrer-policy: strict-origin-when-cross-origin`, `permissions-policy` present; no `x-powered-by`. Every `<script>` in the HTML carried a nonce. Server killed by exact PID. REPRODUCED.

`'strict-dynamic'` and DOM-created scripts: expected CSP3 behaviour. A script that is already trusted (nonced) may add non-parser-inserted scripts; parser-inserted un-nonced markup stays blocked. On this head nothing renders user content, there is no `dangerouslySetInnerHTML` and no runtime string reaches an icon or script, so I found no route for attacker-controlled markup to execute. With `'strict-dynamic'` present the `'self'` source is ignored by CSP3 browsers (it is only a fallback) — fine.

`e2e/specs/security-headers.spec.ts` (read, not run): the enforcement test parses two scripts through an `iframe srcdoc` (inherits the policy), one un-nonced and one with the response nonce, and asserts `noncedRan === true` and `plainRan === false`. The control makes the negative assertion capable of failing; a policy with `'unsafe-inline'` and no nonce would also trip the exact `script-src` regex and the `not.toMatch(/unsafe-/)` assertion in the header test. I judge it not a false-green by reading, and CI `e2e` is success on this SHA. The mutation run itself (add `'unsafe-inline'`, watch the spec go red) is **NOT RUN**: session time, and the canonical local build did not work.

## D / E. Gate and diff audit

- No spec authenticates, fills a credential or touches a signed URL: grep of both new specs for `fill(`, password, credential, login, cookie, Authorization, signed, `.skip/.only/.fixme` returned nothing relevant.
- Harness not loosened: `git diff origin/main HEAD --stat -- e2e/harness playwright.config.ts vitest.config.ts eslint.config.mjs lib/api scripts .github` is empty; the only e2e changes are the two added spec files. The one new allow-list entry is scoped with `test.use` to the CSP negative test and matches only the CSP console error.
- 22 files, +1694/-19. package.json/lockfile: only `lucide-react` `1.46.0` exact, lockfile entry has `resolved` + sha512 `integrity`. No generated client touched, no deleted or weakened assertion, no skip.
- Shell: skip link is a real `<a href="#content">` to `<main id="content" tabIndex=-1>`; no buttons, no dead controls; the wordmark is text and commented as not a brand mark. No mock data. Keyboard behaviour in a browser: NOT RUN by me (CI `e2e` shell.spec covers it).
- The two plain `<a>` (TopBar `/`, home `/health`) with one `eslint-disable-next-line @next/next/no-html-link-for-pages`: nothing broken that I could reproduce. FOLLOW-UP.

## Ledger cases of VZ-DESIGN-001

- success "Token file + component catalog + icon registry test that every name exists in the pinned package": token file `design/tokens.css` and `design/CATALOG.md` exist, registry test exists and B1 proves it bites. PROVEN for the icon registry and token file; the "component catalog" is a document, not a set of components.
- negative "Unknown icon name fails typecheck": PROVEN (B2).
- Not delivered against the entry's outcome / evidence_required: components with variants and states (only the shell), the brand mark (text placeholder), the Figma mirror with revision references and the "design handoff record with node references" (`registry.ts` refers to `design/HANDOFF.md`, which is not in this diff), accepted first-slice screens. The id is a PART; I would not record it IMPLEMENTED on this PR alone.

## Findings

| # | Class | Finding |
|---|---|---|
| 1 | FOLLOW-UP | `deps-scan`/`image-scan` red on advisories in `next` 16.3.5 (critical), `sharp`, `vite`, `vitest`, `minimatch`, `zod`, `source-map-js`, `launch-editor`; pre-existing versions, same on main, not required lanes. `next`/`sharp` ship in the image: needs its own bump PR. |
| 2 | FOLLOW-UP | Plain `<a>` instead of `next/link` in TopBar and home page, with an eslint-disable; root cause (RSC request aborted) not investigated. |
| 3 | FOLLOW-UP | `registry.ts` comment points to `design/HANDOFF.md`, absent from the diff; ledger `evidence_required` is unmet. |
| 4 | FOLLOW-UP | `npm run build` (Turbopack) fails on this macOS arm64 / Node 24 machine with an `@tailwindcss/oxide` native-binding error; not shown to be the PR's fault (main not compared). |

No BLOCKING finding.

## Not run

- `npm run build` with Turbopack locally (exit 1, environment; CI `frontend` and `docker-build` green on the SHA).
- Playwright e2e locally, including the `'unsafe-inline'` mutation of the header builder (C) and the browser pass at 390/1440 px light/dark (G).
- Docker image build (daemon not running).
- Main's `npm audit` today was not executed; the scan conclusion rests on the lockfile diff.
- Node 22.14.0 (.nvmrc) not available; Node 24.21.0 used.

Head at end of session: `505fb281cd9fb4dd89f76aae7317a5bf8d9593c6`.

FINAL VERDICT: PASS — SHA 505fb281cd9fb4dd89f76aae7317a5bf8d9593c6
