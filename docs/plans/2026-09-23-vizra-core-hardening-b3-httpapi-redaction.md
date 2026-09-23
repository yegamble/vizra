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
2. **Coverage test.** `TestEveryLogSiteInTheAPIIsRedacted` walks every non-test file in `internal/httpapi` and requires every slog call's value to be a literal, a package-level constant, or an `obs.Redact(...)` call; the message must be a literal; the key must be a literal (no `slog.Attr` constructors, which would hide a raw value). It pins the number of log sites so it cannot pass vacuously, and forbids the other ways out of the package (`log`, `fmt.Print*`/`Fprint*`, `print`/`println`). A companion test plants unredacted calls in synthetic source and requires the checker to flag each one. A planted unredacted call in real package code turns the coverage test red.
3. **L-2.** `FallbackLimiter.Allow` returns `(false, 0)` when the context is already done, before touching the cache, the fallback counter or the degraded flag, and does the same when `Exec` fails because the context ended mid-flight. Tests: a pre-cancelled context and a context cancelled while the request is in flight; both leave `Degraded()` false and the fallback budget unspent. A live context against the same dead server still flips degraded (control, so the test cannot pass because nothing ever flips). Red first on `f1972e8`.
4. Non-goals: F-2 (a doc NIT, not routed here), L-1 and L-3 (documentation, owner inbox), redaction in other packages.

## Implementation
- `internal/httpapi/middleware.go`: the 500 log line redacts every value (`error`, `request_id`, `path`, `method`).
- `internal/httpapi/setup.go`, `internal/httpapi/setup_limits.go`: the remaining log sites wrap their non-literal values in `obs.Redact` so the rule has no exceptions.
- `internal/httpapi/logsites_test.go`: coverage test, checker self-test, behaviour test.
- `internal/cache/ratelimit.go`: `ctx.Err()` early return, before and after `Exec`.
- `internal/cache/ratelimit_test.go`: the two L-2 tests.
- `scripts/test-floors.json`: only if `--emit-floors` from the measured runs calls for a rise. Never lowered.
- No migration, no OpenAPI change, no sqlc change.

## Verification
- Focused: `go test -race -count=1 ./internal/httpapi/ ./internal/cache/`.
- Gate: `make ci`.
- Unit counts: `go test -race -count=1 -json ./...` then `python3 scripts/go-test-report.py --suite unit ... [--emit-floors]`.
- Integration on both cache images, own containers (`vizra-b3-pg`, `vizra-b3-valkey`, `vizra-b3-redis72`), `go test -race -count=1 -tags=integration -json ./...` with the report script, plus the shuffled run.
- Demonstrations: red on base for N-7 behaviour and L-2; planted-call mutation for the coverage test; revert of each fix turns its test red again.

## Progress and evidence
(appended below as work proceeds)

## Blockers and handoff
None at start.
