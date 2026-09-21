# Execution plan: vizra-user PR1b — hardening (security F4/F5/F6, verifier F6/F7)

## Context
- Repo: `yegamble/vizra-user` (private). Checkout `/Users/yosefgamble/github/vizra/vizra-user`.
- Base: `main` at `752253cb13409de251c7ec7ea896af2eba579095` (PR #1 squash-merge).
- Branch: `chore/m0-hardening`. PR against `main`, references `yegamble/vizra#1`.
- Findings source (meta repo `docs/evidence/warroom/`):
  - `2026-09-20-vizra-user-pr1-skeleton-SECURITY.md` — FINDING 4 (server-only),
    FINDING 5 (supply chain), FINDING 6 (`$ref` in the vendored spec), plus the
    FLOOR note in the closure section.
  - `2026-09-20-vizra-user-pr1-skeleton-VERIFY.md` — FINDING 6 (`globalThis["fetch"]`),
    FINDING 7 (`FLOOR=" "` passes vacuously).
- Acceptance bullets = each finding's own "Acceptance criteria" block.

## Acceptance

**A1 — security FINDING 4 (`server-only`)**
- `server-only` is a dependency at a version verified on the npm registry.
- `import "server-only";` at the top of `lib/api/fetch.ts` and `lib/config.ts`;
  `assertServer` kept unchanged and still covered.
- A Client Component importing `viewerFetch` or `internalApiBaseUrl` fails
  `npm run build`, demonstrated.
- No chunk under `.next/static` contains `INTERNAL_API_BASE_URL` or the
  `PUBLIC_ORIGIN` value; asserted in CI.

**A2 — security FINDING 5 (supply chain)**
- Every `FROM` in the Dockerfile carries an `@sha256:` digest for the node tag
  already in use; the digest is recorded next to the `.nvmrc` note.
- `ci-guard` asserts every `FROM` is digest-pinned, red against a controlled
  mutation and green restored.
- Bumping `.nvmrc` without touching the Dockerfile fails the same check.
- A dependency scan and an image scan run on `pull_request` and `merge_group`
  and publish results as an artifact. No `continue-on-error` (ci-guard forbids
  it). The lanes stay OUT of `.github/required-checks.txt`; the PR body reports
  the baseline by severity and says what would make them required.

**A3 — security FINDING 6 (contract input)**
- A vendored spec containing a non-local `$ref` (`https://…`, `./file.yaml#/x`)
  fails with a named error **before** the generator runs, on `pull_request` and
  `merge_group`.
- The current spec passes unchanged; `npm run check:contract` still passes and
  `lib/api/generated.ts` is unchanged.

**A4 — verifier FINDING 6 (computed-member fetch)**
- `globalThis["fetch"](…)`, `window["fetch"](…)`, `globalThis[\`fetch\`](…)` are
  `rawFetch` outside the allow-list; as a *value* they are `aliasedFetch` in
  every file including `lib/api/fetch.ts`.
- A genuinely dynamic `globalThis[name]` — decision recorded: **reported**, a
  new `dynamicGlobalMember` messageId, fail-closed, symmetrical with the
  identity rule's `unreadable`.
- `client["fetch"](…)` and `client[name]` on unrelated objects stay clean
  (valid cases).

**A5 — verifier FINDING 7 (`FLOOR`)**
- `FLOOR=" "` and `FLOOR=""` either enforce the default or exit non-zero;
  neither prints OK with an empty floor list. Suite case added.

**Non-goals (explicit):** security response headers / CSP (app-shell PR),
verifying `contracts/manifest.json`'s `source_commit` (needs a cross-repo token
the owner has not granted), Playwright, tokens, pages, re-vendoring the
contract (vizra-core PR1 has not merged).

## Implementation
No migrations, no OpenAPI change, no UI. Files:
- `package.json`, `package-lock.json` — `server-only` dependency.
- `lib/api/fetch.ts`, `lib/config.ts` — `import "server-only";`.
- `Dockerfile` — digest-pinned `FROM` in all three stages.
- `eslint-rules/no-raw-fetch.mjs` + `.test.mjs` — computed-member access.
- `scripts/ci/check-required-floor.sh` — blank-`FLOOR` guard.
- `scripts/ci/check-image-pins.sh` (new) + cases in `require-checks_test.sh`.
- `scripts/ci/check-client-bundle.sh` (new) — `.next/static` leak grep.
- `scripts/ci/demo-server-only-boundary.sh` (new) — scripted failing build.
- `scripts/check-spec-refs.mjs` (new) + `scripts/check-spec-refs.test.mjs`,
  called from `scripts/codegen.mjs` before the generator runs.
- `.github/workflows/ci-guard.yml` — image-pin step.
- `.github/workflows/frontend-ci.yml` — bundle-leak + server-only boundary steps.
- `.github/workflows/contract-ci.yml` — explicit `$ref` step.
- `.github/workflows/supply-chain.yml` (new) — `deps-scan`, `image-scan`.
- `docs/evidence/2026-09-20-pr1b-hardening.md` — red/green transcripts, in-repo.

## Verification
Commands that exist today: `npm run lint`, `npm run typecheck`, `npm run test`,
`npm run build`, `npm run ci`, `npm run check:contract`,
`bash scripts/ci/require-checks_test.sh`, `bash scripts/ci/check-required-floor.sh`.
New: `bash scripts/ci/check-image-pins.sh`, `bash scripts/ci/check-client-bundle.sh`,
`bash scripts/ci/demo-server-only-boundary.sh`, `node scripts/check-spec-refs.mjs`.

Each *demonstrated* bullet gets a controlled mutation: red transcript, restore,
green transcript, both kept in `docs/evidence/` inside the repo.

Environment: darwin arm64, node v22.14.0, npm 10.9.2, docker 29.8.0 (daemon up),
gh 2.98.0, jq 1.7.1, shellcheck 0.11.0. CI lane: ubuntu-24.04 (the one that counts).

## Progress and evidence

**IMPLEMENTED, READY_FOR_REVIEW.** Branch `chore/m0-hardening`, head
`6b0ba871d3ccdda9f3d054398335138b08e84fd8`, PR
https://github.com/yegamble/vizra-user/pull/2 (base `main`, refs yegamble/vizra#1).

In-repo evidence: `vizra-user/docs/evidence/pr1b/` (index in its `README.md`).
Every *demonstrated* bullet has a red transcript against a controlled mutation
and a green transcript with it restored.

### Local gate (darwin arm64, node v22.14.0, npm 10.9.2, shellcheck 0.11.0, jq 1.7.1, Trivy 0.70.0)
Full transcript: `vizra-user/docs/evidence/pr1b/gate-local.txt`.

| Command | Exit | Counts |
|---|---|---|
| `npm run lint` | 0 | |
| `npm run typecheck` | 0 | |
| `npx vitest run` | 0 | 6 files, 147 passed, 0 skipped (was 116) |
| `npm run build` | 0 | |
| `npm run check:contract` | 0 | spec sha256 `128d0509238a…` |
| `node scripts/check-spec-refs.mjs` | 0 | 9 refs, all local |
| `bash scripts/ci/require-checks_test.sh` | 0 | 70 cases, 77 assertions, 0 failed (was 55/62) |
| `bash scripts/ci/check-required-floor.sh` | 0 | |
| `bash scripts/ci/check-image-pins.sh` | 0 | 3 FROM lines pinned |
| `bash scripts/ci/check-client-bundle.sh` | 0 | 10 chunks, no leak |
| `bash scripts/ci/check-server-only-boundary.sh` | 0 | build failed with 4 server-only diagnostics |
| `shellcheck -x scripts/ci/*.sh` | 0 | |

### Did not run locally
The linux/amd64 docker build (ADR-009's acceptance platform). This machine is
arm64 with ~14 GiB free; emulated amd64 builds are not run here. The image was
built and scanned **natively on arm64**; CI's `docker-build` and `image-scan`
lanes are the amd64 evidence. `npm audit` is architecture-independent.

### Supply-chain baseline
`npm audit`: 0 at every severity. Image scan **before**: 53 findings (3
CRITICAL, 35 HIGH, 12 MEDIUM, 3 LOW), 0 in Alpine packages, 0 in the app's
bundled `node_modules`, all 53 inside the base image's npm CLI. The runner
stage installs nothing, so npm/npx/yarn/corepack are removed there (assertion
in the same `RUN`, so a moved path fails the build). Image scan **after**: 0.
Image still serves `/health` 200 as `uid=1001(nextjs) gid=1001(nodejs)`.

### Two things the mutations caught
1. The reviewer's `$ref` reachability claim was UNVERIFIED. Driving
   openapi-typescript 7.13.0 at a poisoned spec with no guard crashes it with
   `Can't resolve $ref: fetch failed` — the outbound request really happened.
2. The first version of the server-only guard was wrong and its own red run
   said so: grepping for `server-only` anywhere matched Next's code frames
   (`assertServer`'s message, `fetch.ts`'s docblock) and `fetch.ts` fails on
   `next/headers` regardless, so it "passed" with both imports deleted. It now
   matches Next's diagnostic sentences exactly, strips ANSI first, and requires
   attribution to each module via its own probe route.

### Decisions recorded for the verifier
- `globalThis[name]` is **reported** (`dynamicGlobalMember`), the fail-closed
  option verifier F6 left open; `client["fetch"]` / `registry[name]` stay clean.
- `FLOOR`'s env override is **kept, blank rejected**, because the suite uses it.
- vitest aliases `server-only` to the package's own `empty.js` (the file its
  `react-server` condition selects); the boundary itself is bundler-only and is
  asserted by `check-server-only-boundary.sh`.
- Removing the base image's package managers goes slightly beyond F5's literal
  text; it is what takes the image baseline from 53 to 0.

### No test weakened
116 → 147 vitest tests, 55 → 70 shell cases, 0 skipped. No valid case removed,
no assertion loosened, no lane demoted, no budget changed.

### Cleanup
Local images `vizra-user:pr1b-scan`, `vizra-user:pr1b-scan2`,
`aquasec/trivy:0.70.0` and container `vizra-user-pr1b` removed; the build cache
this session created was pruned (2.685 GB + 4.09 GB reclaimed). Probe routes
and every mutation reverted; `git status` clean apart from the commit.

## Blockers and handoff
No blockers. Preflight found every required tool present.

Remaining gate: `ci-required` on `6b0ba87`, then independent verification. The
builder did not merge and did not verify its own work.

Next action for the chair: read CI on `6b0ba87` and dispatch a verifier that
did not write this code.
