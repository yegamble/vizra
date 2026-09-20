# Execution plan: vizra-core PR2 "stabilise" — V-1, V-2 and the `attempts` note

## Context

| | |
|---|---|
| Repo | `yegamble/vizra-core` (private) |
| Checkout | `/Users/yosefgamble/github/vizra/vizra-core` |
| Base commit | `415a6d19cfc0acedd8ad84c1857c95db0ed63627` (main; PR #1 merged 2026-09-20) |
| Branch | `fix/m0-stabilise` |
| Meta issue | `yegamble/vizra#1` |
| Evidence in-repo | `docs/evidence/pr2/` |

Source findings, all non-blocking at PR #1 merge:

- **V-1** — `docs/evidence/warroom/2026-09-20-vizra-core-pr1-foundation-VERIFY.md` § "Re-verification at b5f8f6a", FINDING V-1. `TestHeartbeatRequiresStillHoldingTheLease` and `TestSweepReclaimsOnlyElapsedLeases` fail intermittently in the full integration suite (3/6 full runs at `4f8d0fc`, 1/6 at `b5f8f6a`), pass 8/8 alone. The verifier's mechanism was recorded **UNVERIFIED** with a leading candidate of `DROP SCHEMA` / `FOR UPDATE SKIP LOCKED` inter-test interference.
- **V-2** — same file, FINDING V-2. `internal/jobs/worker.go` "exhausted attempts" and "terminal failure" log the raw handler error and depend entirely on `cmd/api` / `cmd/worker` installing the redacting slog handler.
- **`attempts` note** — `…-BACKEND.md` final closure section: "a future `vizra jobs retry` must reset `attempts` or it recreates the unclaimable-queued zombie — is recorded nowhere greppable. Add one line to `SweepExpiredLeases`' comment in `store/queries/jobs.sql`."

Non-goals for this slice: the public search contract; the image scan lane and clean runtime stage; the nonce store; V-3 (`Value.Resolve`, `secretKeys` stems, expected-ruleset, `cmd/worker` tests). **No migration may be touched** — 0001–0004 are frozen and `append-only` fails on any edit. No change under `api/`.

## Acceptance

**V-1.**
1. The mechanism is *reproduced and identified*, not guessed, with measurements.
2. The pre-fix failure rate is recorded from at least 20 full integration runs.
3. After the fix, the full integration suite passes **30 consecutive times on each cache leg** with `-count=1`, and again with `-shuffle=on`.
4. A CI step and a make target run the integration suite with `-shuffle=on`, so order dependence is caught in future.
5. No sleep, retry, `t.Skip`, longer timeout or whole-suite serialisation is used as the fix unless it is shown to be the root cause. No existing test is weakened or deleted.

**V-2.**
6. A `Worker` constructed with a **plain, non-redacting** `slog` handler emits no credential material for a handler error carrying the value classes of `internal/obs/log_test.go`. Demonstrated RED before the fix.

**`attempts` note.**
7. The rule is greppable in `store/queries/jobs.sql` at `SweepExpiredLeases`. If the text lands inside a query block, sqlc is regenerated and `sqlc diff` is clean.

## Implementation

### V-1 — root cause (established, see Progress)

`internal/jobs/jobs.go:155-157` stamps `run_after` from the **application host clock**:

```go
runAfter := j.RunAfter
if runAfter.IsZero() {
        runAfter = time.Now()     // host clock
}
```

`ClaimJob` (`store/queries/jobs.sql`) tests eligibility against the **database clock**:

```sql
WHERE state = 'queued' AND run_after <= now() AND ...
```

Every other timestamp in the job lifecycle (`created_at`, `leased_until`, `RetryJob.run_after`, the sweep's `leased_until < now()`, `finished_at`) is assigned by the database. `run_after` at enqueue is the **only** cross-clock comparison in the system. When the database clock trails the host clock by more than the enqueue→claim round trip, a job whose intent is "run now" is not yet claimable and `ClaimJob` returns `pgx.ErrNoRows` — exactly the observed symptom.

Fix: **the database is the single clock authority for "now"**. `EnqueueJob` resolves an absent `run_after` with `COALESCE(@run_after::timestamptz, now())`; `jobs.Enqueue` passes SQL `NULL` when `NewJob.RunAfter` is zero instead of `time.Now()`. An explicit caller-supplied `RunAfter` (a deliberate future time) is unchanged. sqlc regenerated; `sqlc diff` clean.

Defence in depth, from the verifier's recommendation and **not** the root cause: `NewWorker` registers `KindNoop` unconditionally (`worker.go:131`), so *every* worker in the suite polls `noop`; five tests start a worker with `go func() { _ = w.Run(ctx) }()` and never wait for it. Under `-shuffle=on` that is a live route to cross-test theft. Give each of those tests the `stopped`-channel wait that `TestGracefulShutdown…` already uses.

### V-2

`internal/jobs/worker.go`: apply the existing `safeError` (= `truncate(obs.Redact(s))`, the same path `last_error` uses) to the handler error at the log call sites that currently pass it raw.

### `attempts` note

Comment text above `SweepExpiredLeases` in `store/queries/jobs.sql`.

## Verification

Services (non-default host ports, torn down at the end):

| Service | Image (digest from `.github/workflows/build-test.yml`) | Port | Container |
|---|---|---|---|
| PostgreSQL 18 | `postgres@sha256:86c951e0…` | 55433 | `vizra-pr2-pg` |
| Valkey 9.1.2 | `valkey/valkey@sha256:c123e371…` | 56380 | `vizra-pr2-valkey` |
| Redis 7.2 | `redis@sha256:06379549…` | 56381 | `vizra-pr2-redis` |

```
VIZRA_TEST_DATABASE_URL=postgres://vizra@127.0.0.1:55433/vizra_test?sslmode=disable
VIZRA_TEST_CACHE_URL=redis://127.0.0.1:56380/0      # 56381 for the redis leg
```

| Lane | Command |
|---|---|
| Whole gate | `make ci` |
| Unit | `go test ./...` |
| Integration | `make test-integration` |
| Shuffle (new) | `make test-integration-shuffle` |
| sqlc drift | `make sqlc-verify` |
| 30× loop, per leg | `scripts` loop recorded in `docs/evidence/pr2/` |

`append-only` and `docker-build` run only in CI.

## Progress and evidence

### 1. Reproduction — BEFORE any change, at `415a6d1`

20 consecutive full integration runs, valkey leg, `-race -count=1`:
**3 of 20 runs failed (15%)** — runs 4, 8, 16. Transcript:
`docs/evidence/pr2/BEFORE-valkey-20runs.txt`.

Failures are exactly the two named tests, both at a `ClaimJob` immediately following a
successful `enqueue`:

```
golden_test.go:369: no rows in result set   TestHeartbeatRequiresStillHoldingTheLease
golden_test.go:412: no rows in result set   TestSweepReclaimsOnlyElapsedLeases
```

### 2. Mechanism — measured, not guessed

A temporary diagnostic (`internal/integration/zz_diag_test.go`, reverted after use;
retained at `docs/evidence/pr2/DIAGNOSTIC-zz_diag_test.go.txt`) dumped the `jobs`
table, the server clock and `pg_stat_activity` at the instant of failure.

At the failing claim the row is present and perfectly eligible, and **only one backend
is connected to the database** — refuting inter-test interference, leaked workers and
`SKIP LOCKED` contention:

```
DIAG heartbeat/claim: err=no rows in result set hostNow=2026-09-20T20:51:43.612713Z
                      dbClock=2026-09-20T20:51:43.610732Z skew(db-host)=-1.987ms
DIAG heartbeat/claim: row kind=noop state=queued attempts=0/5
                      run_after=…43.610365Z eligible=true leased_by=- corr=c
                      created=…43.608356Z
DIAG heartbeat/claim: 1 rows in jobs
DIAG heartbeat/claim: backend pid=1419 …   (the diagnostic's own connection, and no other)
```

`run_after` (…610365Z, host clock) is **2.0 ms later than `created_at`** (…608356Z,
database clock) although it was sampled *earlier* in real time — the database clock
trails the host clock.

Skew is steady at ≈ −1 ms, identically whether the two tests run alone or in the suite,
so skew alone is not the variable:

```
DIAGSKEW TestHeartbeatRequiresStillHoldingTheLease: skew(db-host)=-975.25µs  (in suite)
DIAGSKEW TestHeartbeatRequiresStillHoldingTheLease: skew(db-host)=-984µs     (alone)
```

The variable is the **margin** `now() - run_after` measured by the database immediately
before the claim — the enqueue→claim round trip minus the skew:

| | margin, 8 samples |
|---|---|
| test alone (passes 20/20) | 847µs, 642µs, 733µs, 885µs, 618µs, 757µs, 1.153ms, 589µs |
| full suite (fails ~15%) | 462µs, 415µs, **23µs**, 474µs, **−7µs**, 329µs, 75µs, 1ms |

The margin is a sub-millisecond race against a ~1 ms clock skew, and it goes negative.
That is the whole mechanism. It is not test-only: in production the API and PostgreSQL
are different containers or hosts, and ordinary NTP skew makes a freshly enqueued
"run now" job invisible to the claim loop for the duration of the skew.

### 3. The fix, and RED before GREEN

Commit `4f02e18f555935e4d95c6427a953f4d0362ba899`.

- `store/queries/jobs.sql` — `EnqueueJob` run_after becomes
  `COALESCE(sqlc.narg(run_after)::timestamptz, now())`, with the reasoning in the
  comment. sqlc regenerated; the params struct is unchanged, so no caller churn.
  `sqlc diff` clean (`make sqlc-verify` exit 0).
- `internal/jobs/jobs.go` — a zero `RunAfter` is no longer resolved with `time.Now()`;
  `toTimestamptz` already maps a zero time to a NULL `pgtype.Timestamptz`.
- `internal/jobs/worker.go` — `safeError` at **three** error log sites. The verifier
  named `jobs: exhausted attempts` and `jobs: terminal failure`; `jobs: retrying`
  passes the identical raw handler error and is fixed too (mutation M4 proves the
  two-site fix still leaks).
- `store/queries/jobs.sql` — the `attempts` contract on `SweepExpiredLeases`.
- `internal/integration/golden_test.go` — two new tests, and `startWorker` replacing
  the five leaked worker starts. **The only deleted lines in the file are those five
  `go func() { _ = w.Run(ctx) }()` lines** (`git diff main -- …golden_test.go | grep '^-'`).
- `Makefile` + `.github/workflows/build-test.yml` — `test-integration-shuffle`, run in
  CI on both cache flavours.

RED: `docs/evidence/pr2/RED-v1-v2.txt`. GREEN: `…/GREEN-v1-v2.txt`.

### 4. Determinism — 30 consecutive full runs per leg, ordered and shuffled

`go test -race -count=1 [-shuffle=on] -tags=integration ./...`, 30 runs each:

| Leg | Order | Result | Transcript |
|---|---|---|---|
| Valkey 9.1.2 | source | **0 / 30 failed** | `AFTER-valkey-30runs.txt` |
| Valkey 9.1.2 | `-shuffle=on` | **0 / 30 failed** | `AFTER-valkey-30runs-shuffle.txt` |
| Redis 7.2.16 | source | **0 / 30 failed** | `AFTER-redis-30runs.txt` |
| Redis 7.2.16 | `-shuffle=on` | **0 / 30 failed** | `AFTER-redis-30runs-shuffle.txt` |

120 full runs, zero failures, against 3 in 20 before.

### 5. Controlled mutations — `docs/evidence/pr2/MUTATIONS.md`

| # | Mutation | Killed by |
|---|---|---|
| M1 | `jobs.go` resolves a zero `RunAfter` with the host clock again | `TestRunAfterComesFromTheDatabaseClockNotTheApplicationHost` — "differ by 1640 µs" |
| M2 | drop `COALESCE(…, now())` from `EnqueueJob`, regenerate | same test — `null value in column "run_after" … violates not-null constraint` |
| M3 | all three log sites back to the raw handler error | `TestAWorkerWithAPlainHandlerLogsNoCredentials` — leaked the bearer token |
| M4 | fix only the **two** sites the verifier named | same test — leaked the presigned URL credential via `jobs: retrying` |
| M5 | remove the `attempts` note from the source query without regenerating | `make sqlc-verify` exit 2, with the generated diff |

### 6. Required lanes — `docs/evidence/pr2/FINAL-LANES.txt`

| Lane | Exit |
|---|---|
| `make ci` (fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, test-race) | 0 |
| `go test -count=1 ./...` | 0 |
| `make tidy-check` | 0 |
| `go mod verify` | 0 |
| `make sqlc-verify` | 0 |
| `make test-integration` [valkey] | 0 |
| `make test-integration-shuffle` [valkey] | 0 |
| `make test-integration` [redis] | 0 |
| `make test-integration-shuffle` [redis] | 0 |

`go test -count=1 -tags=integration -v ./...` — **919 pass, 0 fail, 0 skip** (917 at
PR #1, plus the two new tests).

`append-only` and `docker-build` run only in CI. `migrations/` and `api/` are untouched
(`git diff main -- migrations/ api/` is empty), so `append-only` has nothing to object to.

## Blockers and handoff

No blockers. Containers `vizra-pr2-pg`, `vizra-pr2-valkey`, `vizra-pr2-redis` removed at
the end of the session.

**Reported to the chair, deliberately not fixed here:** `obs.Redact`'s presigned-URL
rule is anchored on the query separator, so a **bare** `X-Amz-Credential=…` outside a
URL is not redacted. Same family as the verifier's still-open V-3(b) (`secretKeys` is
exact-match, so `session_secret` and `search_hmac_key` are uncovered). It belongs in a
slice that reviews `internal/obs` patterns as a whole.

**Cross-repo:** `vizra-search` shares the `freshDatabase` fixture shape and carries a
twin logger. If it enqueues jobs with an application-side "now", it has the same
cross-clock defect; worth a look when that repo's next slice lands. No contract change
is needed from another owner for this PR.

**Next concrete action:** independent verification, then `ci-required` green on the
verified SHA.
