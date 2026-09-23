# Execution plan: vizra-core hardening B3 — observability redaction on the HTTP path (N-7, F-1, NEW-2 coverage test, L-2)

## Context
- Repo: `vizra-core`. Worktree `/Users/yosefgamble/github/vizra/.claude/worktrees/core-b3`, branch `chore/m1-httpapi-redaction`, base `origin/main` = `f1972e8` (includes the merged M1-A owner claim, core #8).
- Out of bounds (owned by core #10/#11): `scripts/` except `scripts/test-floors.json`, the `Makefile`, `.github/pinned-makefiles.yml`.
- Findings, all from the `vizra-security` seat:
  - N-7 and F-1: `/Users/yosefgamble/github/vizra/docs/evidence/warroom/2026-09-21-vizra-core-pr8-m1a-owner-claim-SECURITY.md`. F-1 is the same defect as N-7's 500 half, re-raised at `56504c1`: the generic 500 log line in `internal/httpapi/middleware.go` logs `err.Error()` raw, and `internal/httpapi` has no redaction-coverage test. The recommendation is to wrap that attribute in `obs.Redact` and add `TestEveryErrorLogSiteInTheAPIIsRedacted`. That is redaction, so it is built here and not reported back.
  - L-2: `/Users/yosefgamble/github/vizra/docs/evidence/warroom/2026-09-23-vizra-core-pr8-limiter-SECURITY.md`. A cancelled request context flips `cache.FallbackLimiter` to `Degraded()` and charges the in-process fallback.
- Requirement: VZ-OPS-005 as stated in `internal/obs/log.go` and the repo `AGENTS.md` ("No credential, signed URL, session id or API key ever reaches a log line").
- The twin: `internal/jobs/logsites_test.go` `TestEveryErrorLogSiteInTheWorkerIsRedacted`.

## Acceptance
1. **N-7 / F-1 behaviour.** A 500 whose cause carries a DSN with a password, a presigned-URL signature and credential, and whose request path carries an API key, logs none of them, even when the process logger is a plain `slog` JSON handler rather than `obs.NewLogger` (`New` falls back to `slog.Default()`). The client still gets only the canned message and the request id. Red first on `f1972e8`.
2. **Coverage test.** `TestEveryLogSiteInTheAPIIsRedacted` walks every non-test file in `internal/httpapi` and requires every slog call's value to be a literal or an `obs.Redact(...)` call (package constants were considered and rejected: syntactic resolution cannot rule out a local shadow); the message must be a literal; the key must be a literal (no `slog.Attr` constructors, which would hide a raw value). It pins the number of log sites so it cannot pass vacuously, and forbids the other ways out of the package (`log`, `fmt.Print*`/`Fprint*`, `print`/`println`). A companion test plants unredacted calls in synthetic source and requires the checker to flag each one. A planted unredacted call in real package code turns the coverage test red.
3. **L-2.** `FallbackLimiter.Allow` returns `(false, 0)` when the context is already done, before touching the cache, the fallback counter or the degraded flag, and does the same when `Exec` fails because the context ended mid-flight. Tests: a pre-cancelled context and a context cancelled while the request is in flight; both leave `Degraded()` false and the fallback budget unspent. A live context against the same dead server still flips degraded (control, so the test cannot pass because nothing ever flips). Red first on `f1972e8`.
4. Non-goals: F-2 (a doc NIT, not routed here), L-1 and L-3 (documentation, owner inbox), redaction in other packages.

## Implementation
- `internal/httpapi/middleware.go`: the 500 log line redacts every value (`error`, `request_id`, `path`, `method`).
- `internal/httpapi/setup.go`, `internal/httpapi/setup_limits.go`: the remaining log sites wrap their non-literal values in `obs.Redact` so the rule has no exceptions.
- `internal/httpapi/logsites_test.go`: coverage test, checker self-test, behaviour test.
- `internal/cache/ratelimit.go`: `ctx.Err()` early return, before and after `Exec`.
- `internal/cache/ratelimit_test.go`: the three L-2 tests (pre-cancelled against a dead cache with a live-context control, cancelled mid-command, and pre-cancelled with no cache configured).
- `scripts/test-floors.json`: only if `--emit-floors` from the measured runs calls for a rise. Never lowered.
- No migration, no OpenAPI change, no sqlc change.

## Verification
- Focused: `go test -race -count=1 ./internal/httpapi/ ./internal/cache/`.
- Gate: `make ci`.
- Unit counts: `go test -race -count=1 -json ./...` then `python3 scripts/go-test-report.py --suite unit ... [--emit-floors]`.
- Integration on both cache images, own containers (`vizra-b3-pg`, `vizra-b3-valkey`, `vizra-b3-redis72`), `go test -race -count=1 -tags=integration -json ./...` with the report script, plus the shuffled run.
- Demonstrations: red on base for N-7 behaviour and L-2; planted-call mutation for the coverage test; revert of each fix turns its test red again.

## Progress and evidence
State: IMPLEMENTED, READY_FOR_REVIEW (not verified, not merged).

- Branch `chore/m1-httpapi-redaction`, commits `38088a7` (fix + tests + AGENTS.md rows), `7e56a79` (test cleanup hardening), `6edaf83` (floors). Head **`6edaf83cc3035f3e5ae270556082897b527893dd`**. PR: https://github.com/yegamble/vizra-core/pull/12
- Files: `internal/httpapi/{middleware.go,setup.go,setup_limits.go,logsites_test.go}`, `internal/cache/{ratelimit.go,ratelimit_test.go}`, `AGENTS.md`, `scripts/test-floors.json`.
- Environment: darwin/arm64, go1.27.1, PostgreSQL 18.6 (`postgres@sha256:86c951e0…`), Valkey 9.1.2 (`valkey/valkey@sha256:c123e371…`), Redis 7.2.16 (`redis@sha256:06379549…`), containers `vizra-b3-{pg,valkey,redis72}-<n>`.
- Transcripts: scratch dir `/private/tmp/claude-501/-Users-yosefgamble-github-vizra/7321b930-95d2-4a95-ba2e-61ef2ce3c13c/scratchpad/b3.z49k/` (session scratch, not durable). Files: `red-n7-coverage-base.txt`, `red-l2-base.txt`, `mut-M1…M7*`, `make-ci*.txt`, `*-events.json`, `*-report.txt`, `*-emit.txt`.

| Command | Rev | Exit | Result |
|---|---|---|---|
| `go test -count=1 -v -run 'TestEveryLogSiteInTheAPIIsRedacted\|TestTheLogSiteChecker\|TestTheErrorHandlerRedacts' ./internal/httpapi/` (new tests only) | f1972e8 | 1 | RED: 10 unredacted values at 5 sites; DSN password, signature, credential, API key in the log line |
| `go test -count=1 -v -run Cancelled ./internal/cache/` (base limiter) | f1972e8 limiter | 1 | RED: degraded flips on 3/3 cancelled calls; fallback charged; mid-command flips |
| same two, fixed tree | 38088a7 | 0 | GREEN |
| `go test -race -count=20 -run Cancelled ./internal/cache/` | 7e56a79 | 0 | 20 × 3 pass |
| `make ci` | 7e56a79 | 0 | all lanes passed |
| `go test -race -count=1 -json ./...` + `go-test-report.py --suite unit` | 7e56a79 | 0/0 | 1209 executed, 17 pkgs, 0 unexpected skips |
| `go test -race -count=1 -tags=integration -json ./...` Valkey | 7e56a79 | 0/0 | 1378 executed, 18 pkgs, 0 skips |
| same `-shuffle=on`, Valkey | 7e56a79 | 0/0 | 1378 |
| same, Redis 7.2.16 | 7e56a79 | 0/0 | 1378 |
| same `-shuffle=on`, Redis 7.2.16, attempt 1 | 7e56a79 | 1/1 | NOT a test failure: `ld: write() failed, errno=28 (No space left on device)` linking httpapi.test and jobs.test (360 MiB free) |
| same `-shuffle=on`, Redis 7.2.16, attempt 2 | 7e56a79 | 0/0 | 1378 |
| `--emit-floors` on unit and Valkey integration runs | 7e56a79 | — | calls for httpapi 48→66, cache 4→7 (both suites), unit 1006→1028, integration 1150→1171; applied in 6edaf83; all five event streams re-judged against the new floors: ok |
| `make ci` | 6edaf83 | 0 | all lanes passed |

Mutations on the fixed tree (each restored with `git checkout -- .`):
- M1: 500 line reverted to raw values. Coverage test red (4 values) and behaviour test red.
- M2: an unredacted `Logger.Info` planted in `probes.go`. Coverage test red on the value and on the count (7 ≠ 6).
- M3: `obs.Redact` removed at `setup_limits.go:145`. Coverage test red, with the count unchanged.
- M4: `slog.Any("error", cause)` in `setup.go`. Coverage test red on the non-literal key.
- M5: L-2 pre-check removed. `TestACancelledRequestDoesNotChargeTheInProcessLimiter` red.
- M6: L-2 post-Exec check removed. `TestARequestCancelledMidCommandDoesNotFlipTheLimiterToDegraded` red.
- M7: `logsites_test.go` moved aside, whole unit suite run. The report is red at `internal/httpapi` 56 < 66. Against the old floors, the same events pass.

## Blockers and handoff
- No blocker. The remaining gate is an independent verifier.
- CI on PR #12, head `6edaf83` (merge ref against main `96d19b3`, which includes core #10/#11; `git merge-tree` is clean). Not re-run:
  - Passed: `ci-required`, `build-test`, `cache-matrix` (both legs), `append-only`, `fixtures`, `govulncheck`, `docker-build`, GitGuardian.
  - build-test's own reports: unit 1306 executed (floor 1028); integration 1475 and 1475 shuffled (floor 1171); 0 unexpected skips. These counts are higher than the local ones because the merge ref carries the tests from #10/#11.
  - `image-scan` (NOT required) failed on 49 HIGH Debian 13.7 base-image OS CVEs, for example CVE-2025-69720 (ncurses) and CVE-2026-16742 (systemd libs). The scan itself is valid. This PR changes no Dockerfile or dependency.
- Cleanup:
  - Containers `vizra-b3-{pg,valkey,redis72}-23727` removed. They were removed without `-v`, so their anonymous volumes may remain among the host's dangling volumes. I could not attribute one to them with certainty, so I deleted none.
  - Worktree removed.
  - The scratch transcripts are kept at the path above for the verifier.
- Finding outside this slice: `internal/integration/healthcheck_test.go:55` `os.MkdirTemp("", "vizra-healthcheck-bin-")` is never removed. That leaks about 74 MB per integration run; 88 had accumulated in `$TMPDIR` on this host, and that caused the ENOSPC above. I removed only the five my runs created.
