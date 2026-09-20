# Execution plan: VZ-FOUND-002 — vizra-user PR1 "skeleton"

## Context
- Repository: `yegamble/vizra-user` (private). Checkout
  `/Users/yosefgamble/github/vizra/vizra-user`, base commit `9baafb2`
  ("Initial commit", README-only) on `main`, clean. Branch: `feat/m0-skeleton`.
- Issue: `docs/issues/VZ-ISSUE-001.md` (filed as
  <https://github.com/yegamble/vizra/issues/1>). Ledger entry: `VZ-FOUND-002`
  in `docs/quality/features.json`.
- Slice: item 3 of the VZ-ISSUE-001 PR sequence in
  `docs/plans/2026-09-15-prompt01-architecture.md` (lines 139–143).
- Binding decisions read before editing: meta `AGENTS.md`; ADR-001 (stack pins
  and licences), ADR-002 (contracts, CI fan-in, required-checks manifest),
  ADR-003 (sessions/CSRF → the two SSR fetch helpers and the lint rule),
  ADR-009 (acceptance platform: GitHub-hosted `ubuntu-24.04`, amd64;
  the owner's arm64 laptop is not a substitute for the amd64 rehearsal).
  All nine ADRs were Accepted by the owner on 2026-09-20.
- Prior art consulted, not copied wholesale: the owner's Vidra frontend
  `~/github/vidra/vidra-user` (codegen/drift, `ci-required` fan-in,
  `required-checks.txt`, standalone Dockerfile). Nothing was taken from
  `~/github/goimg/goimg-user/catalyst-ui-kit/` (paid, non-redistributable) and
  no mock-data layer was carried over from either.

## Acceptance
VZ-FOUND-002 (ledger): "OpenAPI is the API source; TypeScript client is
generated and drift-checked." This PR owns the `vizra-user` half — the
generated client, its drift check, and the skeleton strict enough that later
pages cannot hand-write API types or mock data. The `vizra-core` half
(route↔spec both directions) is that repo's PR1.

Observable, per the slice brief:
1. Next.js 16.3.x App Router skeleton in TypeScript, Tailwind at the ADR-001
   pin with a minimal config (no tokens — that is a later PR).
2. `npm run ci` = lint, typecheck, test, build; it fails on a type error
   (*demonstrated*).
3. The TypeScript client is generated from `vizra-core/api/openapi.yaml` into
   one committed file; a hand-edited generated client fails the drift check
   (*demonstrated*).
4. `publicFetch` / `viewerFetch` (ADR-003 "SSR identity") plus an ESLint rule
   forbidding identity headers (cookie / authorization) on a revalidated or
   cached fetch; a fetch that does so fails lint (*demonstrated*), and the rule
   has unit tests.
5. Production Dockerfile (Next standalone) that builds.
6. A health page.
7. `.github/required-checks.txt` and a `ci-required` workflow on
   `pull_request` **and** `merge_group`, GitHub-hosted `ubuntu-24.04`, every
   third-party action pinned by 40-character SHA.
8. The repository's own `AGENTS.md` and `CLAUDE.md` (which imports `AGENTS.md`).

Non-goals for this PR (they stay in the ledger, unreduced): design tokens, the
app shell, the typed icon registry, any product page, and the Playwright
browser harness (PR2 / VZ-FOUND-008). `lucide-react` is therefore **not**
installed here — it arrives with the icon registry, at the ADR-001 pin.

## Implementation

### Cross-repo contract (ADR-002 is silent on the fetch mechanism)
ADR-002 fixes *what*: "The TypeScript client is generated into one committed
file in `vizra-user` with byte-for-byte drift CI." It does not say how this
repository's CI obtains `vizra-core/api/openapi.yaml`. Vidra's precedent
(`U/.github/workflows/contract-ci.yml`) checks out `vidra-core@main` — which
works because that repo is public. `yegamble/vizra-core` is **private**, so a
cross-repo `actions/checkout` needs a PAT that does not exist and that this
session is not authorized to mint.

Per the slice brief's fallback, the spec is therefore **vendored**:
- `contracts/vizra-core/api/openapi.yaml` — a byte copy.
- `contracts/manifest.json` — source repo, path, the core commit SHA the copy
  was taken from, the copy's sha256, and the date.
- `scripts/check-contract.mjs` fails when (a) the vendored file's sha256 does
  not match the manifest, or (b) regenerating the client from the vendored spec
  produces a different file than the committed one.

Follow-up owed to the chair, not silently dropped: once a read-only token for
`yegamble/vizra-core` exists, contract-ci should additionally compare the
vendored copy against core's `main`, so a stale vendor is red rather than
invisible. Recorded in the repo `AGENTS.md` and in the PR body.

### Files
- `package.json` / `package-lock.json` (npm, lockfile committed), `.nvmrc`.
- `next.config.ts` (`output: "standalone"`, `poweredByHeader: false`),
  `tsconfig.json`, `postcss.config.mjs`, `eslint.config.mjs`,
  `vitest.config.mts` (`.mts` so Vite loads it as ESM without a warning).
- `app/layout.tsx`, `app/page.tsx`, `app/globals.css` (bare
  `@import "tailwindcss"`), `app/health/page.tsx` + its test.
- `lib/config.ts`, `lib/api/fetch.ts` (`publicFetch`, `viewerFetch`),
  `lib/api/types.ts` (re-exports the generated types only),
  `lib/api/generated.ts` (generated; committed; never hand-edited).
- `eslint-rules/`: `no-identity-headers-in-cached-fetch.mjs`,
  `no-raw-fetch.mjs`, `index.mjs`, and a RuleTester suite per rule.
- `scripts/codegen.mjs`, `scripts/vendor-contract.mjs`, `scripts/check-contract.mjs`,
  `scripts/ci/require-checks.sh` (+ its regression suite),
  `scripts/ci/check-required-manifest.sh`.
- `Dockerfile`, `.dockerignore`, `.gitignore`.
- `.github/required-checks.txt`, `.github/workflows/{frontend-ci, contract-ci,
  ci-required, ci-guard, docker-build}.yml`.
- `AGENTS.md`, `CLAUDE.md`.

### Pins (each verified on the npm registry on 2026-09-20 before use)
Recorded in "Progress and evidence" below with the observed `dist-tags.latest`.

## Verification
- `npm ci` then `npm run ci` (= `lint`, `typecheck`, `test`, `build`) locally
  on darwin/arm64 Node 22.14.0, and in CI on GitHub-hosted `ubuntu-24.04`.
- `npm run check:contract` against the vendored spec.
- `bash scripts/ci/require-checks_test.sh` (the fan-in's own regression suite;
  needs bash ≥ 4 — `/opt/homebrew/bin/bash` 5.3.9 locally, bash 5 in CI).
- `docker build` of the production Dockerfile, native linux/arm64 locally
  (ADR-009: arm64 is developer-only, no support claim; the amd64 build is the
  `docker-build` CI lane on `ubuntu-24.04`).
- Three red/green demonstrations (transcripts kept under
  `docs/evidence/warroom/VZ-FOUND-002/`):
  D1 hand-edited `lib/api/generated.ts` → `npm run check:contract` red, restore → green.
  D2 identity headers on a revalidated fetch → `npm run lint` red, restore → green.
  D3 a type error → `npm run ci` red, restore → green.
- NOT run in this slice, and not claimed: any browser/E2E check (PR2), any
  request against a live `vizra-core` (no API exists yet), and the amd64
  `install.sh` rehearsal (ADR-009 — needs a disposable amd64 VM).

## Progress and evidence

### Pins, each verified on the npm registry on 2026-09-20 before it was written
Observed `dist-tags.latest` and the declared licence/engines were read from
`https://registry.npmjs.org/<pkg>` in this session.

| Package | Pinned | Observed latest | Why this pin |
|---|---|---|---|
| `next` | 16.3.5 | 16.3.5 (MIT, engines node ≥ 20.9) | ADR-001 "Next.js 16.3.x" |
| `react` / `react-dom` | 19.3.0 | 19.3.0 | ADR-001 "matching React"; satisfies next's peer range |
| `typescript` | 5.9.3 | **7.0.2** | NOT the latest, deliberately: `eslint-config-next` 16.3.5 depends on `typescript-eslint` ^8.46, whose supported-TypeScript range is the 5.x line. ADR-001 leaves TypeScript as `[pin at PR time; verify]`; 5.9.3 is the head of that line |
| `tailwindcss` / `@tailwindcss/postcss` | 4.3.3 | 4.3.3 (MIT) | ADR-001 `[pin at PR time; verify]`; minimal config only, tokens land later |
| `openapi-typescript` | 7.13.0 | 7.13.0 (MIT) | ADR-001 "openapi-typescript 7.13.x" |
| `eslint` | 10.11.0 | 10.11.0 (engines ≥ 20.19/22.13/24) | current; `eslint-config-next` declares `eslint >= 9`. The Next preset's sub-plugins still declare `^9` peers, so npm prints ERESOLVE overrides — the same situation as the owner's Vidra frontend. Lint runs clean over all 17 files; `settings.react.version` is pinned because plugin version detection crashes under ESLint 10 |
| `eslint-config-next` | 16.3.5 | 16.3.5 | matches `next` |
| `vitest` | 5.0.1 | 5.0.1 (engines ^22.12 ‖ ^24 ‖ ≥ 26) | current |
| `@types/node` | 22.20.4 | 26.6.2 | matches the pinned Node line, not the newest types |
| Node | 22.14.0 (`.nvmrc`, `engines.node >= 22.13.0`, `node:22.14.0-alpine`) | — | the builder machine's runtime, and inside every pinned dependency's engines range. One pin, read by CI (`node-version-file`) and by the Dockerfile |
| `lucide-react` | **not installed** | 1.47.0 | out of scope here; it arrives with the typed icon registry, at ADR-001's 1.46.x pin |

Actions pinned by SHA, each resolved from the GitHub tags API this session:
`actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1),
`actions/setup-node@820762786026740c76f36085b0efc47a31fe5020` (v7.0.0).
No other third-party action is used; `docker-build` uses the runner's own Docker.

### Cross-repo contract, as consumed
`git -C ../vizra-core log -1 --format=%H -- api/` →
`b0dbeb6dc27294fe793492ea60bc18b6aed4b042` ("feat(api): add canonical OpenAPI
contracts (probes + core<->search internal)"), on core's `feat/m0-foundation`
branch, **not yet merged to core `main`**. Vendored to
`contracts/vizra-core/api/openapi.yaml`, sha256
`128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d`, provenance
in `contracts/manifest.json`. Only the public `api/openapi.yaml` was taken —
core keeps the core↔search internal contract in a separate file precisely so
this client never gains internal HMAC operations.

### Commands (final tree, after `rm -rf node_modules .next next-env.d.ts`)
| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | 410 packages from the committed lockfile |
| `npm run ci` | 0 | lint clean over 17 files; `tsc --noEmit` clean; **5 test files, 50 tests passed, 0 skipped**; production build of 3 routes |
| `npm run check:contract` | 0 | spec matches manifest; client byte-identical |
| `bash scripts/ci/require-checks_test.sh` | 0 | 45 cases, 52 assertions, 0 failed |
| `bash scripts/ci/check-required-manifest.sh` | 0 | 4 manifest entries, all defined |
| `bash -n` + `shellcheck -x` over `scripts/ci/*.sh` | 0 | clean (shellcheck 0.11.0) |
| `docker build --tag vizra-user:dev .` | 0 | native linux/arm64, ~36 s |
| container smoke on a free port (3317) | — | `GET /health` 200 with `data-testid="health-status">ok<`; `GET /` 200 |

### Demonstrations
Transcripts: `docs/evidence/warroom/VZ-FOUND-002/` (`README.md` indexes them).
- **D1** hand-edited `lib/api/generated.ts` → `check:contract` exit 1, while
  `typecheck` and `test` still exit 0 — which is exactly why the byte-for-byte
  check exists. A hand-edited vendored spec fails on sha256. Restored → exit 0.
- **D2** identity headers on a revalidated fetch → `npm run lint` exit 1, both
  when `viewerFetch` itself is weakened and when a page fetches on its own
  (two rules fire). Restored → exit 0.
- **D3** a type error → `npm run ci` exit 2. Restored → exit 0.

**A real finding, kept rather than tidied away:** the first version of the lint
rule did *not* catch the weakened `viewerFetch`, because that helper passes its
headers by variable and the rule only read object literals at the call site.
The mutation exposed it; the rule now resolves the identifier through scope and
tracks `headers["cookie"] = …` writes, with four added RuleTester cases. D2's
transcript is against the strengthened rule.

### Deviations from the brief, and why
- **`ci-guard` and `docker-build` lanes were added** beyond the brief's list.
  ADR-002 asks the fan-in guard to reject `continue-on-error` on a required
  lane and to reject an empty test selection; `ci-guard` does the first (plus
  SHA pins, `npm ci`, a manifest naming only real jobs, shellcheck, and the
  fan-in's own suite) and `vitest.config.mts` (`passWithNoTests: false`) does
  the second. `docker-build` is the only place the Dockerfile is built on the
  ADR-009 acceptance platform. Neither is claimed as closing VZ-CI-001.
- **`scripts/ci/require-checks.sh` and its suite are adapted from Vidra**, the
  precedent ADR-002 cites. The rename introduced a hazard — a blind
  `vidra`→`vizra` substitution turned Vidra's recorded incidents into fake
  Vizra history — which was corrected: those comments now name Vidra
  explicitly, and the "TWIN" claims say *intended*, since no sibling repo
  carries the file yet.
- **No `lucide-react`** (icon registry is a later PR) and no design tokens.

### First CI run (head `5672bfdb5718cf9916174ddb6c25cd5ac39e5f88`)
PR <https://github.com/yegamble/vizra-user/pull/1>. All lanes' first execution,
GitHub-hosted `ubuntu-24.04`: `frontend` pass 38s (50 tests, 0 skipped),
`contract` pass 29s, `guard` pass 13s (fan-in suite 52 assertions),
`docker-build` pass 57s (linux/amd64 image built, container served `/health`),
`ci-required` pass 1m39s ("OK: every required check on 5672bfd… concluded
success"). Full table in `docs/evidence/warroom/VZ-FOUND-002/README.md`.

## Blockers and handoff
- **Not blocking this PR.** Nothing external stopped the work.
- **Owed, and recorded in the repo's `AGENTS.md` and the PR body:** the
  `contract` lane cannot detect a *stale* vendored spec, because
  `yegamble/vizra-core` is private and this repository holds no token to read
  it. When a read-only token exists, add a step comparing the vendored copy
  against core's default branch. Until then, freshness rests on review of
  `contracts/manifest.json` and on core's own route↔spec test.
- **For the chair:** the vendored contract is pinned to a commit on core's
  `feat/m0-foundation` branch. If that branch is rebased or the spec changes
  before core's PR1 merges, this repository must re-vendor
  (`node scripts/vendor-contract.mjs --from ../vizra-core`) and commit the spec,
  manifest and regenerated client together. Re-vendoring after core merges is a
  small follow-up, not a redesign.
- **Owner action after this lands (ADR-002 items 9–10):** apply the `main`
  ruleset requiring the `ci-required` context, block force-push and deletion,
  require linear history, and add CODEOWNERS over `.github/**` and
  `scripts/ci/**`. Until protection is confirmed applied, no ledger entry may
  reach VERIFIED on CI evidence alone.
- **Next concrete action:** PR2 / VZ-FOUND-008 — the Playwright harness against
  the production build, which is the first slice that can make any browser,
  accessibility or viewport claim.
