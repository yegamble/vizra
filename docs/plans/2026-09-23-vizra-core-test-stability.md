# Execution plan: core test stability (queue 2m + 2s, sentinel S-0016 / S-0001)

Status: IN_PROGRESS (builder). Never VERIFIED by this author.

## Context
- Repo `vizra-core`, branch `chore/m1-test-stability` from `origin/main@3994893` (#13 merged).
- Findings: meta `docs/sentinel/FINDINGS.md` S-0016 (`internal/fixtures` hits go test's 10m default under load; leaks temp dirs), S-0001 (`internal/integration/healthcheck_test.go:55` leaks ~74 MB `vizra-healthcheck-bin-*` per run).

## Acceptance (chair brief)
1. Measure where `internal/fixtures` (`TestManifestDetectsEveryClassOfDrift`) and `internal/integration` spend their time; cut waste (redundant regeneration, safely parallelisable serial work). Set explicit reviewed `-timeout` values in the Makefile targets and the pinned CI steps, sized from the measurement with a stated margin — never raised blindly to hide a hang. Makefile change ⇒ re-pin `.github/pinned-makefiles.yml`; pinned-step change ⇒ `pinned-steps.yml` + workflows in lockstep, guards green.
2. No temp leak: `t.TempDir()`/`t.Cleanup`. A test that fails if a run leaves a new `vizra-*` temp entry, pointed at a per-test `TMPDIR`; shown red on main.
3. Anchor and grammar intact; the Makefile still fits the allowlist grammar.

Non-goals: queue 2o, S-0021, anything outside test timing/cleanup.

## Verification
`make ci`, the direct unit step + report, integration suites (direct step bodies) on Valkey and Redis 7.2 in own containers; both anchors; ci-required-guard; wall times before/after recorded.

## Progress and evidence
(appended as it runs)

## Blockers and handoff
