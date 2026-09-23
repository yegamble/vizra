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
- Measured on main 3994893: `internal/fixtures` dominates every lane (93-163s one lane, 230s with two lanes at once, 270s at load ~70); `TestManifestDetectsEveryClassOfDrift` 146s, serial, 6 corpus generations (3 only to put files on disk). CI (4 runs): fixtures 84.8-139.5s, integration 56.7-93.6s. Every integration run leaves a 74-75 MB `vizra-healthcheck-bin-*`.
- Cut: mutations copy the shared corpus; drift cases parallel; the 4 heavy fixtures tests parallel (package generations 9 -> 6). New `internal/testtmp` (one root per test binary, TMPDIR pointed at it, removed at exit, dead-PID roots swept by the next run); TestMain in fixtures and integration. Leak tests `TestTheFixturesTestsLeaveNoTemporaryEntry` (normal + SIGKILL of the process group + next run) and `TestTheIntegrationTestsLeaveNoTemporaryEntry` (normal run), each with a TMPDIR only it owns; `TestTheEntryPointsBuild`. Floors: `internal/testtmp` 1 in both suites.
- `-timeout 8m` on Makefile test/test-race/test-integration/test-integration-shuffle and the 3 pinned direct steps (pinned-steps.yml, build-test.yml, 74 guard fixtures in lockstep); Makefile re-pinned; grammar fits (64/11/25/25/72). Sizing: CI worst 139.5s pre / 112.5s post; local worst after 201.2s (load ~44); CI step offsets make 8m print the goroutine dump before the 20m/15m job kill.
- Evidence `vizra-core/docs/evidence/test-stability/`: timings.txt, R0-red-on-main (both leak tests red on 3994893), T1-T4 mutations red then green.
- Merged main a6bc77d as `888a003` (conflict: test-floors `_why` only). Lanes on 888a003 (own containers, digests pinned): make ci 0 (153s), unit 0 (1566/0/0), integration valkey 0 and redis 7.2 0 (1737/0/0), 0 leftover entries. Scripts tests ok; both anchors 0; ci-required-guard 0.
- PR https://github.com/yegamble/vizra-core/pull/15, head `96b8999e99d801aa38da84aef4792952f14ff9f0`. CI on 96b8999: ci-required, build-test, cache-matrix (+ both legs), fixtures, govulncheck, append-only, docker-build, GitGuardian pass; image-scan (not required) fail as on main.

## Blockers and handoff
None. State: READY_FOR_REVIEW. Next: independent verifier on #15.
