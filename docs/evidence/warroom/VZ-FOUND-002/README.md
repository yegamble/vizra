# VZ-FOUND-002 — vizra-user PR1 "skeleton": evidence index

**State: READY_FOR_REVIEW. Not verified, not merged.** A verifier that did not
write this code must reproduce it from a clean clone of the PR head.

- Repository: `yegamble/vizra-user`, branch `feat/m0-skeleton`, base `9baafb2`.
- Slice: item 3 of the PR sequence in
  `docs/plans/2026-09-15-prompt01-architecture.md`.
- Execution plan: `docs/plans/2026-09-20-vizra-user-pr1-skeleton.md`.
- Builder environment: darwin/arm64 (Apple silicon), node v22.14.0, npm 10.9.2,
  Docker 29.8.0 (aarch64), bash 5.3.9 for the fan-in suite, shellcheck 0.11.0.
- Contract consumed: `yegamble/vizra-core@b0dbeb6dc27294fe793492ea60bc18b6aed4b042`
  `api/openapi.yaml`, sha256
  `128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d`, vendored
  at `contracts/vizra-core/api/openapi.yaml` with `contracts/manifest.json`.
  That commit is on core's `feat/m0-foundation` branch and had not merged to
  core `main` when this was taken.

## Local commands (all on the final tree, after `rm -rf node_modules .next`)

| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | 410 packages from the committed lockfile |
| `npm run ci` (lint, typecheck, test, build) | 0 | 5 test files, **50 tests passed, 0 skipped**; production build of 3 routes |
| `npm run check:contract` | 0 | vendored spec matches its manifest; generated client byte-identical |
| `bash scripts/ci/require-checks_test.sh` | 0 | 45 cases, 52 assertions, 0 failed |
| `bash scripts/ci/check-required-manifest.sh` | 0 | all 4 manifest entries map to a defined job |
| `bash -n` + `shellcheck -x` on `scripts/ci/*.sh` | 0 | clean |
| `docker build --tag vizra-user:dev .` | 0 | native linux/arm64, ~36 s |
| container smoke: `GET /health` | 200 | `<dd data-testid="health-status">ok</dd>`; `GET /` 200 |

## Demonstrations (red against a controlled mutation, then green)

| File | Shows |
|---|---|
| `D1-generated-client-drift.md` | a hand-edited `lib/api/generated.ts` fails `check:contract` (exit 1) while typecheck and tests still pass; a hand-edited vendored spec fails on sha256; both restored → exit 0 |
| `D2-identity-headers-lint.md` | identity headers on a revalidated fetch fail `npm run lint` (exit 1) — both when `viewerFetch` itself is weakened and when a page fetches on its own; restored → exit 0 |
| `D3-ci-type-error.md` | `npm run ci` fails on a type error (exit 2), restored → exit 0 |

D2 also records a real finding: the first version of the lint rule did **not**
catch the weakened `viewerFetch`, because the headers were passed by variable.
The rule was strengthened (scope resolution plus member-assignment tracking)
and four RuleTester cases were added; the transcript is against the
strengthened rule.

## Not run, and therefore not claimed
- **The amd64 build and the CI lanes themselves** — the builder's machine is
  arm64. `docker-build`, `frontend`, `contract`, `guard` and `ci-required` are
  first exercised by the PR's own CI run on GitHub-hosted `ubuntu-24.04`
  (ADR-009 acceptance platform). The PR body records that run.
- **Any browser/E2E check** — VZ-FOUND-008, PR2. No Playwright harness exists
  in this repository yet, so no accessibility, viewport or console-error claim
  is made.
- **Any request against a live `vizra-core`** — no API is running; the fetch
  helpers are covered by unit tests with a stubbed `fetch`, which is not
  provider acceptance.
- **Branch protection / the `ci-required` ruleset** — an owner action after
  this PR lands (ADR-002 item 9). Until it is applied, no ledger entry may
  reach VERIFIED on CI evidence alone (ADR-002 item 10).
- **Freshness of the vendored contract against core's `main`** — impossible
  without a read-only token for the private `vizra-core`; recorded as owed in
  the repository's `AGENTS.md` and in the PR body.

## First CI run on the PR head (added after the PR opened)
PR: <https://github.com/yegamble/vizra-user/pull/1>, head
`5672bfdb5718cf9916174ddb6c25cd5ac39e5f88`. Runner: GitHub-hosted
`ubuntu-24.04`. Every lane's first-ever execution.

| Check | Result | Duration | Run |
|---|---|---|---|
| `frontend` (`npm run ci`) | pass | 38s | 35527037104 — 417 packages via `npm ci`, **5 test files / 50 tests passed**, build of 3 routes |
| `contract` | pass | 29s | 35527037095 — vendored spec ↔ manifest ↔ generated client, then `git diff --exit-code` |
| `guard` | pass | 13s | 35527037191 — shellcheck, SHA pins, no `continue-on-error`, `npm ci`, manifest names real jobs, `passWithNoTests: false`, **fan-in suite 45 cases / 52 assertions / 0 failed** |
| `docker-build` | pass | 57s | 35527037102 — linux/amd64 production image built and `/health` served `ok` from the container |
| `ci-required` (fan-in) | pass | 1m39s | 35527037045 — "OK: every required check on 5672bfd… concluded success." |
| GitGuardian Security Checks | pass | 2s | repository-level app, not part of the manifest |

The fan-in's log shows it waiting on each lane in turn
(`waiting: frontend (in_progress) contract (in_progress) guard (in_progress)
docker-build (in_progress)`) before concluding — it is polling real check runs,
not passing vacuously.

Still true after this run: nothing here is VERIFIED. The `ci-required` ruleset
is not applied yet (owner action, ADR-002 items 9–10), and ADR-002 item 10 says
no ledger entry may reach VERIFIED on CI evidence alone until it is.
