# Independent verification — vizra-core PR #4 "stabilise" (V-1, V-2, `attempts` note)

| | |
|---|---|
| Repo / PR | `yegamble/vizra-core` — https://github.com/yegamble/vizra-core/pull/4 |
| Branch | `fix/m0-stabilise` |
| **Head SHA verified** | `1a6d8bd4ef4c621c39887e158e8cf0b8b9175a71` |
| Base | `415a6d19cfc0acedd8ad84c1857c95db0ed63627` (main) |
| Head moved during verification? | **No** — re-checked at start and end |
| Verifier | independent; did not write this code |
| Date | 2026-09-20 |
| **Verdict** | **FAIL** |

## Verdict summary

| Item | State | Note |
|---|---|---|
| **V-1** (intermittent integration failure) | **CLOSED** | Flake reproduced at base; mechanism independently proven; fix proven on the real code path |
| **V-2** (worker log redaction at the call site) | **CLOSED** | All three sites proven by individual mutation, including the one the earlier verifier did not name |
| **`attempts` note** | **CLOSED** | Present, greppable, carried into generated doc, wording correct, protected by `sqlc-verify` |
| **Did I reproduce the original flake?** | **YES** | 3 of 20 full runs at base `415a6d1` under `-shuffle=on`, seeds recorded below |
| Blocking finding | **FINDING 1** | The PR introduces a **new** intermittent failure in its own new test, at ~1/30 in the required integration lane |

The three assigned findings are genuinely closed and the engineering is good. The PR
nevertheless **FAILs** because the slice whose entire purpose is to remove an
intermittent failure from a required lane ships a new one — reproduced by me three times
across two cache legs and made deterministic with a diagnostic. It is a small, local fix.

---

## Environment

| | |
|---|---|
| Host | macOS Darwin 25.5.0, arm64 |
| Go | `go1.27.1 darwin/arm64` (`go.mod` declares `go 1.26.0`) |
| sqlc | `v1.31.1` (the version ADR-001 pins) |
| python3 | present (`ci-required-guard.py` runs) |
| Docker | linux/arm64 |
| PostgreSQL | `postgres@sha256:86c951e05bf56c93d95d397747fb8820ac76cc3bedb78f43abd83eedbe3666ae` — the CI digest — container `vzverify-pg`, host port **55533** |
| Valkey | `valkey/valkey@sha256:c123e3715db63d06d4ad6964884037aa0d5d4d703939b9929954112889708e1d` — `vzverify-valkey` :56580, `vzverify-valkey2` :56582 |
| Redis | `redis@sha256:0637954999d01b7c9ce9167db2da50656e2590d3b884f1c600c5f63bb6e6773c` — `vzverify-redis` :56581 |
| Checkout | fresh clone under the verifier scratch directory; worktrees `base` (415a6d1), `core`/`mut`/`diag` (1a6d8bd). **Not** the builder's checkout. |

No image was built. Containers `vizra-pr2-*` (builder) and `vidra-*` (owner's other
project) were not touched. Every container and database I created is named `vzverify-*` /
`vizra_test_[a-e]` / `vizra_mut*` / `vizra_diag` and was removed at the end.

---

## 1. Reproducing the PRE-fix flake at base `415a6d1`

Command, per run: `go test -race -count=1 [-shuffle=on] -tags=integration ./...`

| Leg | Runs | Failed |
|---|---|---|
| valkey, source order | 20 | **0** |
| valkey, `-shuffle=on` | 20 | **3** |

**REPRODUCED.** The three shuffled failures, with seeds:

```
run 16  EXIT 1  -test.shuffle 1789945671899539000
  --- FAIL: TestAJobWhoseWorkerDiedIsReclaimedAndCompleted   golden_test.go:1196: no rows in result set
  --- FAIL: TestSweepReclaimsOnlyElapsedLeases               golden_test.go:412:  no rows in result set
run 17  EXIT 1  -test.shuffle 1789945684274174000
  --- FAIL: TestAJobWhoseWorkerDiedIsReclaimedAndCompleted   golden_test.go:1196: no rows in result set
  --- FAIL: TestSweepReclaimsOnlyElapsedLeases               golden_test.go:412:  no rows in result set
  --- FAIL: TestHeartbeatRequiresStillHoldingTheLease        golden_test.go:369:  no rows in result set
run 18  EXIT 1  -test.shuffle 1789945696507488000
  --- FAIL: TestAJobWhoseWorkerDiedIsReclaimedAndCompleted   golden_test.go:1196: no rows in result set
  --- FAIL: TestHeartbeatRequiresStillHoldingTheLease        golden_test.go:369:  no rows in result set
```

Two observations the builder's evidence does not contain:

- The rate matches the builder's `BEFORE-valkey-20runs.txt` (3/20) exactly, and the
  signature is identical (`no rows in result set` at a claim following an enqueue).
- A **third** test carries the same defect — `TestAJobWhoseWorkerDiedIsReclaimedAndCompleted`
  (`golden_test.go:1196`). Neither the earlier verifier nor this PR names it. It is fixed
  by the same change, so this is an accuracy note, not a gap.

On this machine the failure appears only under `-shuffle=on`. That is itself an argument
for the new shuffled lane: the ordered lane alone would never have caught it here.

## 2. Proving the mechanism independently of the builder

I did not take the builder's diagnostic. I wrote two throwaway programs that talk to
PostgreSQL through `pgx` directly.

### 2a. Clock delta and the two query shapes — no repo code at all

```
CLOCK host-vs-db delta (db - host), 200 samples: min=-1641us p50=-1623us max=-1527us

PRE-FIX  run_after = Go time.Now()         400/400 NOT claimable on the next statement   margin now()-run_after: min=-1395us p50=-1368us max=-367us
POST-FIX run_after = COALESCE(NULL, now())   0/400 NOT claimable on the next statement   margin now()-run_after: min=185us  p50=211us   max=524us
PRE-FIX  host ahead by 500µs               100/100 NOT claimable   margin p50=-1811us
POST-FIX host ahead by 500µs                 0/100 NOT claimable   margin p50=226us
PRE-FIX  host ahead by 2ms                 100/100 NOT claimable   margin p50=-3359us
POST-FIX host ahead by 2ms                   0/100 NOT claimable   margin p50=201us
PRE-FIX  host ahead by 50ms                100/100 NOT claimable   margin p50=-51354us
POST-FIX host ahead by 50ms                  0/100 NOT claimable   margin p50=216us
```

The database clock on this machine trails the host by a steady **≈1.6 ms**. Writing
`run_after` from the host clock and testing `run_after <= now()` in the database is
therefore a comparison between two clocks that differ by more than the round trip.
`COALESCE(NULL, now())` removes the comparison entirely, at every injected skew.

### 2b. The same experiment on the real `jobs.Enqueue` → `ClaimJob` path

300 cycles of exactly what the flaky tests do — `jobs.Enqueue` inside a transaction,
commit, then `sqlcgen.ClaimJob`:

| Worktree | margin `now() - run_after` | negative | **`ClaimJob` returned `pgx.ErrNoRows`** |
|---|---|---|---|
| **415a6d1** (pre-fix) | min −304 µs, p50 **−175 µs**, max 15.5 ms | **252 / 300** | **175 / 300** |
| **1a6d8bd** (post-fix) | min +419 µs, p50 **+559 µs**, max 2.9 ms | **0 / 300** | **0 / 300** |

This is the mechanism, measured on the production code path, at both SHAs. The builder's
central claim — that the flake is a cross-clock comparison and **not** inter-test
interference — is **confirmed**. The earlier verifier's `DROP SCHEMA` / `SKIP LOCKED`
interference hypothesis is **refuted**: my 300-cycle loop is single-threaded against an
otherwise idle database and still fails 175 times.

### 2c. Every other timestamp

I checked every place a timestamp is written or compared with `now()`
(`store/queries/*.sql`, plus `time.Now()` across non-test Go):

| Site | Clock | Cross-clock? |
|---|---|---|
| `EnqueueJob` `run_after` (no caller delay) | **database** after this PR (was application) | fixed |
| `EnqueueJob` `run_after` (explicit) | caller's deliberate wall clock, stored verbatim; never compared as "now" | no |
| `ClaimJob` `leased_until = now() + @lease_duration::interval` | database (only the *interval* comes from Go) | no |
| `ExtendLease` (heartbeat) `leased_until = now() + …` | database | no |
| `RetryJob` `run_after = now() + @backoff::interval` | **database** (only the *backoff interval* comes from Go) | no |
| `SweepExpiredLeases` `leased_until < now()`, `finished_at = now()` | database | no |
| `CompleteJob` / `FailJob` `finished_at`, `updated_at` | database | no |
| `audit.sql` `now()` | database | no |
| `internal/cache/ratelimit.go:104` `time.Now()` | application, against Redis — never compared with PostgreSQL `now()` | no |
| `internal/search/remote.go:159` `SignRequest(…, time.Now())` | application, HMAC timestamp sent over the wire | no |

**The retry ladder is safe**: the backoff *deadline* is computed by PostgreSQL
(`now() + interval`); only the duration comes from Go. The builder's claim that enqueue
was the only cross-clock comparison holds after this audit.

## 3. Post-fix determinism at `1a6d8bd`

`go test -race -count=1 [-shuffle=on] -tags=integration ./...`, per leg.

| Leg | Order | Runs | Failed | Failing test |
|---|---|---|---|---|
| PostgreSQL 18 + Valkey | source | 30 | **1** (run 11) | `TestAWorkerWithAPlainHandlerLogsNoCredentials` |
| PostgreSQL 18 + Valkey | `-shuffle=on` | 30 | 0 | — |
| PostgreSQL 18 + Redis 7.2 | source | 30 | **1** (run 19) | `TestAWorkerWithAPlainHandlerLogsNoCredentials` |
| PostgreSQL 18 + Redis 7.2 | `-shuffle=on` | 30 | 0 | — |
| **Total** | | **120** | **2** | |

**The two V-1 tests — `TestHeartbeatRequiresStillHoldingTheLease` and
`TestSweepReclaimsOnlyElapsedLeases` — and the third one I found,
`TestAJobWhoseWorkerDiedIsReclaimedAndCompleted`, did not fail once in 120 runs at
head.** V-1 is fixed.

Every failure at head is the PR's own new test. See FINDING 1.

Caveat, stated plainly: to fit the time budget I ran two legs concurrently on one
machine, which is a heavier load than the builder's serial runs and than CI. That makes a
green run a *stronger* result and a red run *easier* to hit. The flake in FINDING 1 also
reproduces with nothing else running (1 of 40 standalone) and is made deterministic by a
diagnostic, so it is not an artefact of my parallelism.

## 4. Demonstrations — every mutation reproduced by me

Applied in my own throwaway worktree at `1a6d8bd`, restored after each. Baseline green.

| # | Mutation | Result | Message |
|---|---|---|---|
| M1 | `jobs.Enqueue` resolves a zero `RunAfter` with the host clock again | **RED** | `run_after … is not created_at …: they differ by 1170 µs` |
| M2 | drop `COALESCE(…, now())` from `EnqueueJob`, `sqlc generate` | **RED** | `null value in column "run_after" … violates not-null constraint (SQLSTATE 23502)` |
| M3 | all three log sites back to the raw handler error | **RED** | leaked the cache URL password `"s3cr3tpw"` |
| M4a | **only** `jobs: exhausted attempts` raw | **RED** | leaked `"SuperSecretSignatureMaterial0123456789"` |
| M4b | **only** `jobs: retrying` raw — the site the earlier verifier did **not** name | **RED** | leaked the DSN password `"hunter2"` |
| M4c | **only** `jobs: terminal failure` raw | **RED** | leaked the DSN password `"hunter2"` |
| M5 | remove the `attempts` note from the source query, do not regenerate | **RED** | `make sqlc-verify` exit **2**, prints the generated diff |
| **M6** (mine) | `COALESCE(now(), sqlc.narg(run_after))` — the database always wins, discarding the caller's delay | **RED** | `an explicit RunAfter was not stored verbatim: stored …23:07:29Z, asked for …01:07:29Z` |

Restored after each mutation: green. M4b independently confirms the builder's claim that
`jobs: retrying` carried the same defect and that the two-site fix the earlier verifier
described would have left it leaking. M6 is my own addition and confirms the explicit-delay
semantics the brief asked me to test: a caller that passes a future `run_after` still gets
exactly that delay, is not claimable, and gets the value back verbatim; a past `run_after`
is not pushed forward either.

`safeError` is `truncate(obs.Redact(s))` (`internal/jobs/worker.go:473`) — **redact
before truncate**, so a secret straddling the 4096-byte cut is replaced before the cut.
The database cause survives: the test asserts `"upload failed"` is still present, and
`last_error` is written through the same `safeError` as before.

## 5. No fix-by-masking

Ruled on each pattern, over the whole diff (`*.go`, `Makefile`, `.github/`):

| Pattern | Added? | Ruling |
|---|---|---|
| `time.Sleep` | none | clean |
| `t.Skip` | none | clean |
| `t.Parallel` removed | none | clean |
| `Eventually`-style polling added to the two flaky tests | none | clean |
| longer timeout | only inside the **new** V-2 test (`60s` ctx, `10s` lease/timeout) — not on the flaky tests | clean |
| `-p 1` / suite serialisation | none | clean |
| retries | none | clean |

**The two flaky tests were not modified at all.** The diff hunks in `golden_test.go` touch
`TestWorkerRunsAndCompletesAJob`, `TestRetryLadderAndTerminalFailure`,
`TestRetryLadderActuallyWalksTheLadder`, `TestAJobWhoseWorkerDiedIsReclaimedAndCompleted`
and `TestAMultibyteErrorIsStoredInLastError` (the five `go func(){ _ = w.Run(ctx) }()` →
`startWorker` swaps) plus two new test functions. `TestHeartbeatRequiresStillHoldingTheLease`
and `TestSweepReclaimsOnlyElapsedLeases` are byte-identical to `main` and now pass. That is
the strongest possible evidence that the fix is in the product, not in the test.

The new `startWorker` helper is a strengthening, not a masking: it *fails* the test if the
worker goroutine does not return within 30 s.

### The new `-shuffle=on` lane

`make test-integration-shuffle` exists (`Makefile`) and fails BLOCKED rather than skipping
when `VIZRA_TEST_DATABASE_URL` is unset. It runs in CI in **three** places, and all three
**executed and succeeded on this SHA** (workflow run `35538878879`):

```
JOB: build-test [success]
    step: Integration tests, shuffled order (PostgreSQL 18 + Valkey) -> success
JOB: cache-matrix-leg (valkey, …) [success]
    step: Integration tests against valkey, shuffled order -> success
JOB: cache-matrix-leg (redis, …) [success]
    step: Integration tests against redis, shuffled order -> success
```

## 6. No existing test weakened, deleted, renamed or skipped

`git diff --numstat 415a6d1 1a6d8bd -- '*_test.go'`:

```
275   5   internal/integration/golden_test.go
```

Five removed lines, all five identical and all five the leaked-goroutine start:

```
-	go func() { _ = w.Run(ctx) }()      (×5)
```

No other test file changed. No test renamed, no assertion relaxed, no case deleted, no
skip added. Full suite at head: **919 pass, 0 fail, 0 skip** (`go test -count=1
-tags=integration -v ./...`, exit 0) — 917 at PR #1 plus the two new tests, as claimed.

## 7. Generated code, migrations, lanes

| Check | Command | Exit | Result |
|---|---|---|---|
| sqlc drift | `make sqlc-verify` | 0 | `internal/store/sqlcgen matches store/queries + migrations` |
| generated code hand-edited? | as above | 0 | No — M5 shows the check bites |
| migrations touched? | `git diff --stat 415a6d1 1a6d8bd -- migrations/ api/` | — | **empty** |
| `migrations/manifest.sha256` | `git diff … -- migrations/manifest.sha256` | — | **unchanged** |
| manifest self-check | `./scripts/migration-manifest.sh check` | 0 | `append-only manifest matches (8 migrations)` |
| `append-only` in CI | GitHub, this SHA | — | **success** |
| ci-guard | `make ci-guard` | 0 | 5 floor lanes present, non-optional, pinned, ubuntu-24.04 |
| whole gate | `make ci` | **0** | `make ci: all lanes passed` |

`EnqueueJobParams` is unchanged by the switch to named parameters — the only diff in
`internal/store/sqlcgen/` is the `COALESCE($7::timestamptz, now())` line and the two doc
comments carried from the SQL. No caller churn.

## 8. GitHub CI on `1a6d8bd`

`.github/required-checks.txt` lists exactly the five `FLOOR_LANES` of
`scripts/ci-required-guard.py`, and every one ran and succeeded on this SHA:

| Check | Conclusion | completed |
|---|---|---|
| `append-only` | success | 21:30:02Z |
| `build-test` | success | 21:34:02Z |
| `cache-matrix` | success | 21:31:23Z |
| `cache-matrix-leg (valkey, …)` | success | 21:31:16Z |
| `cache-matrix-leg (redis, …)` | success | 21:31:09Z |
| `govulncheck` | success | 21:30:35Z |
| `docker-build` | success | 21:33:15Z |
| **`ci-required`** | **success** | **21:34:08Z** |
| `GitGuardian Security Checks` | **failure** | 21:29:54Z — not a required check |

`ci-required` completed **last** (21:34:08Z, after `build-test` at 21:34:02Z), so the
fan-in genuinely waited rather than passing before its dependencies — no false positive.
Nothing skipped, cancelled or missing.

**Caveat for the chair:** CI ran the integration suite six times on this SHA and all six
were green. At the ~1-in-30 rate I measured in FINDING 1, six green runs have roughly an
82 % chance of occurring even with the flake present. CI green on this SHA is therefore
**not** evidence of determinism.

## 9. GitGuardian triage (red; not a required check)

GitGuardian reports **exactly one** finding:

| id | type | commit | file | line |
|---|---|---|---|---|
| 37481217 | Generic Password | `4f02e18` | `internal/integration/golden_test.go` | **1572** |

Line 1572 is `"cache URL password": "s3cr3tpw",` — an entry in the `secrets` map of
`TestAWorkerWithAPlainHandlerLogsNoCredentials`, i.e. **an input the test feeds to the
worker in order to assert it never reaches a log line.** It is load-bearing: deleting it
deletes the coverage.

Every credential-shaped literal **added** in `415a6d1..1a6d8bd`:

| Literal | Where | What it is | Real? |
|---|---|---|---|
| `hunter2` | `golden_test.go`, `RED-v1-v2.txt`, `MUTATIONS.md` | synthetic DSN password, same value already excluded for `internal/obs/log_test.go` | no |
| `s3cr3tpw` | same | synthetic cache password — **the GitGuardian hit** | no |
| `abc123def456` | same | synthetic `X-Amz-Signature` | no |
| `AKIAIOSFODNN7EXAMPLE` | same | **AWS's own published documentation example** access key ID; non-functional | no |
| `SuperSecretSignatureMaterial0123456789` | same | self-evidently synthetic | no |
| `eyJhJhJhJhJhJhJhJhJhZyI6MQ` (`"ey"+"Jh"×9+"ZyI6MQ"`) | same | not a structurally valid JWT (no `.`-separated segments) | no |
| `vzk_Nn4Pp7Nn4Pp7Nn4Pp7Nn4Pp7Nn4Pp7` (`"vzk_"+"Nn4Pp7"×5`) | same | repeated-pattern fake Vizra key | no |

A scan of every added line for real credential formats — `AKIA/ASIA`, `gh[pousr]_`,
`glpat-`, `sk-`, `xox*-`, PEM private-key headers, structurally valid JWTs — matches
**only** `AKIAIOSFODNN7EXAMPLE`, the AWS documentation example.

**Nothing real is present. Nothing needs rotating.** See FINDING 3 for the process gap.

---

## Findings

```
FINDING 1: the PR that removes an intermittent integration failure introduces a new one in its own new test
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/integration/golden_test.go:1625-1634 (the waitFor condition in
             TestAWorkerWithAPlainHandlerLogsNoCredentials)
             store/queries/jobs.sql — ClaimJob: `attempts = attempts + 1`
  requirements: verifier FINDING V-1's own acceptance ("the full integration suite passes
             30 consecutive times on each cache leg"); AGENTS.md "a required test that is
             skipped, missing, cancelled, timed out, or not collected is not PASS"

Observed:
  TestAWorkerWithAPlainHandlerLogsNoCredentials waits with:

      c, err3 := q.GetJob(ctx, retrying.ID)
      return … && a.State == "dead" && b.State == "failed" && c.Attempts >= 1

  `attempts` is incremented by ClaimJob, in the same UPDATE that sets state='leased' —
  the query's own comment says so: "`attempts` counts CLAIMS, not failures: it is
  incremented here, at claim time". So `c.Attempts >= 1` becomes true the instant the
  retry job is CLAIMED — before the handler returns, before RetryJob runs, and before
  `jobs: retrying` is written to the log buffer the test then asserts against.

  I observed it three times in my own runs at 1a6d8bd:
    HEAD valkey, source order, run 11 of 30  — EXIT 1
    HEAD redis,  source order, run 19 of 30  — EXIT 1
    the test alone (no suite), 1 of 40 runs  — EXIT 1
  i.e. 2 of 120 full integration runs, and 1 of 40 standalone runs — always the same
  message:
    golden_test.go:1643: the worker never logged "jobs: retrying", so this test proved
    nothing about it:

  Made DETERMINISTIC by widening the claim→log window. In a throwaway worktree at
  1a6d8bd I added `time.Sleep(3 * time.Second)` to the "leaky-retry" handler only:
    3 of 3 runs FAILED with exactly that message.

Failure:
  A required lane (`build-test` and both `cache-matrix-leg`s, each now running the
  integration suite twice) goes red at random roughly 1 run in 30. That is precisely the
  condition this slice exists to remove, and the condition AGENTS.md and this PR's own
  Makefile comment identify as corrosive: "a lane that can go red at random gets re-run
  until green, and at that point it has stopped being evidence."

  The test is fail-safe rather than pass-vacuous — it asserts the branch logged, so a
  lost race is a red, never a silent false pass. That bounds the damage to CI noise,
  which is why it is a BLOCKER on the lane and not a correctness hole in the product.

Perspective:
  developer, operator

Recommendation:
  Wait on the thing the test actually asserts — the log buffer — rather than on a
  database column that moves earlier than the log line. Verified working: with the 3 s
  diagnostic sleep STILL in place, 3 of 3 runs green after:

      l := workerLog.String()
      return err1 == nil && err2 == nil && err3 == nil &&
          a.State == "dead" && b.State == "failed" && c.Attempts >= 1 &&
          strings.Contains(l, "jobs: exhausted attempts") &&
          strings.Contains(l, "jobs: terminal failure") &&
          strings.Contains(l, "jobs: retrying")

  (`strings` and `workerLog` are already in scope. The three `strings.Contains` checks
  that follow the wait then become redundant but should stay — they turn a timeout into
  a named message.)

Acceptance criteria:
  - With `time.Sleep(3*time.Second)` temporarily added to the "leaky-retry" handler, the
    test passes 3/3. (Today: fails 3/3.)
  - 30 consecutive full integration runs per cache leg, ordered and shuffled, with zero
    failures — re-measured after the change, not carried over.
  - No sleep, retry or lengthened timeout is used as the fix.

Tests:
  internal/integration/golden_test.go, TestAWorkerWithAPlainHandlerLogsNoCredentials.
  The harness exists. The slow-handler diagnostic above is the red case and should be
  run once by hand; it must not be committed.

Cross-repo implications:
  core: this PR. | user: none. | search: none. | meta: the ledger entry for V-1 cannot be
  VERIFIED until the lane is actually deterministic.

Challenge:
  "One run in thirty is the residual noise of any real integration suite, and the test
  fails safe — merge it and fix it in the next slice." I reject that here specifically
  because this is the stabilise slice: its acceptance bullet is 30 consecutive green runs
  per leg, and it did not meet its own bar. The fix is four lines and I have already run
  it green against a deterministic reproduction.
```

```
FINDING 2: AGENTS.md claims safeError is applied "at every error log site"; eight error log sites still pass unredacted text
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md (the row added by this PR)
             internal/jobs/worker.go:192, 293, 308, 324, 338, 365, 384, 388
             internal/jobs/worker.go:518-523 (errText)

Observed:
  The PR adds this row to the mechanical-rules table in AGENTS.md:

    | A worker leaks no credential into its OWN log whichever slog handler it was built
      with — redaction is at the call site, not in the process wiring |
      `internal/jobs/worker.go` `safeError` at every error log site, … |

  `grep -n 'log\.\(Error\|Warn\)' internal/jobs/worker.go` finds eleven error-bearing log
  sites. Three use safeError (316, 329, 342). The other eight pass `err.Error()` or
  `errText(derr)`, and `errText` does not redact:

      func errText(err error) string {
          if err == nil { return "none (the statement matched no row)" }
          return err.Error()
      }

Failure:
  A future reviewer auditing this contract by grep will find the claim false and will not
  know whether the eight sites are an oversight or a deliberate exclusion. I verified
  they carry pgx/driver errors rather than handler-supplied text, and that pgx does NOT
  echo the DSN password — a live check against a bad-password DSN returned
  `failed to connect to `user=vizra database=vizra`` with the password absent — so there
  is no live leak today. The defect is the contract line, not the code.

Perspective:
  developer

Recommendation:
  Narrow the claim to what the code does and says why, e.g. "`safeError` at every site
  that logs a HANDLER error (the three in `run`/`finishFailed`); driver errors elsewhere
  are pgx-generated and carry no handler-supplied text."

Acceptance criteria:
  - The AGENTS.md row describes exactly the set of sites that use safeError.
  - The exclusion of driver-error sites is stated with its reason.

Tests:
  None needed; this is a documentation-accuracy fix. If the team prefers the strong form,
  the test would be an extension of TestAWorkerWithAPlainHandlerLogsNoCredentials driving
  a database failure with a credential-bearing DSN, which would first require the
  pgx-redaction question to be settled deliberately rather than relied on.

Cross-repo implications:
  core: this PR. | user: none. | search: none. | meta: none.

Challenge:
  "The row is about the V-2 class — handler errors — and reads fine in context." Perhaps,
  but the AGENTS.md table is explicitly the list of rules "that are mechanical, and where
  they are enforced", which invites exactly the grep audit that finds it false.
```

```
FINDING 3: GitGuardian is left red with no triage recorded in the PR, against the repo's own written policy
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .gitguardian.yaml
             internal/integration/golden_test.go:1566-1578
             docs/evidence/pr2/RED-v1-v2.txt, docs/evidence/pr2/MUTATIONS.md

Observed:
  The PR adds seven synthetic credential fixtures to internal/integration/golden_test.go
  and echoes them into two evidence transcripts. `.gitguardian.yaml` excludes
  README.md, internal/obs/log_test.go, internal/site/site_test.go,
  internal/search/search_test.go and api/search-hmac-testvectors.json — it does NOT cover
  internal/integration/golden_test.go or docs/evidence/pr2/. GitGuardian therefore fails
  on this SHA with one hit (Generic Password, golden_test.go:1572, "s3cr3tpw").

  Neither the PR body nor the execution plan mentions GitGuardian at all.

  `.gitguardian.yaml`'s own preamble argues against this state: "Neither is a scanner
  that is red forever: an alert nobody reads is an alert that will not be read on the day
  it matters."

  I enumerated every credential-shaped literal added in the range against real credential
  formats. NOTHING REAL IS PRESENT; nothing needs rotating. See § 9 above.

Failure:
  The check stays red. The next PR's author sees a red GitGuardian, learns that red is
  normal, and stops reading it. The exclusion list — the repo's deliberate mechanism for
  exactly this case, with one path and one written reason per entry — is bypassed by
  simply ignoring the result.

Perspective:
  developer, operator

Recommendation:
  Either (a) add internal/integration/golden_test.go to `.gitguardian.yaml` with a written
  reason in the file's established style, naming the values and why they are load-bearing
  test inputs — and docs/evidence/pr2/ likewise, or drop the raw log transcripts' secret
  material from the committed evidence; or (b) record the triage verdict explicitly in the
  PR body so the red is a known, dated decision rather than an unread alert. (a) is
  cheaper and matches the file's existing pattern.

Acceptance criteria:
  - GitGuardian is green on the PR head, OR the PR body carries a dated triage verdict
    naming each hit, its value class, and why it is synthetic.
  - No blanket `*_test.go` glob is added — the file explicitly forbids one.

Tests:
  None; this is a CI-configuration and process item.

Cross-repo implications:
  core: this PR. | user: none. | search: none. | meta: the chair should note GitGuardian
  is advisory, not required, so this never blocks a merge on its own.

Challenge:
  "GitGuardian is not a required check and the values are provably fake, so a red is
  harmless." True for this PR in isolation; the cost is cumulative and is the exact
  failure mode `.gitguardian.yaml` was written to prevent.
```

```
FINDING 4: a third test carries the V-1 defect and is named nowhere
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/integration/golden_test.go:1196
             (TestAJobWhoseWorkerDiedIsReclaimedAndCompleted)

Observed:
  In my pre-fix reproduction at 415a6d1 under `-shuffle=on`, all three failing runs
  included TestAJobWhoseWorkerDiedIsReclaimedAndCompleted failing at golden_test.go:1196
  with the same "no rows in result set" signature as the two named tests. The earlier
  verifier's FINDING V-1, this PR's body and the execution plan all name only two tests.

Failure:
  Nothing is broken — the same one-line change fixes all three, and the test passes at
  head in all of my runs. But the written record understates the blast radius of the
  defect, which matters if anyone later reasons about whether the fix was complete.

Perspective:
  developer

Recommendation:
  One sentence in the ledger entry / evidence record: three integration tests were
  affected, not two, and all three are green after the fix.

Acceptance criteria:
  - The V-1 ledger entry names TestAJobWhoseWorkerDiedIsReclaimedAndCompleted alongside
    the other two.

Tests:
  Already covered; no new test needed.

Cross-repo implications:
  core: record-keeping only. | user: none. | search: none. | meta: ledger wording.

Challenge:
  "It is a documentation nit on a closed finding." Agreed — hence NIT.
```

---

## Evidence claims in the PR body and plan, checked

| Claim | Verdict |
|---|---|
| "3 of 20 full runs red before the fix" | **Confirmed** — I measured 3/20 (shuffled leg) with the same tests and signature |
| "the interference candidate is refuted" | **Confirmed independently** — 175/300 ErrNoRows in a single-connection loop against an idle database |
| "`run_after` at enqueue was the only cross-clock comparison" | **Confirmed** — full audit in § 2c |
| "an explicit caller-supplied `RunAfter` is stored verbatim, past or future" | **Confirmed** — and my mutation M6 shows the assertion bites |
| "`sqlc diff` clean / generated code not hand-edited" | **Confirmed** — `make sqlc-verify` exit 0; M5 shows it bites |
| "`migrations/` and `api/` are untouched" | **Confirmed** — empty diff; manifest unchanged; `append-only` green |
| "three log sites, not two; `jobs: retrying` had the same defect" | **Confirmed** — M4b |
| "919 pass, 0 fail, 0 skip" | **Confirmed** exactly |
| "No sleep, retry, `t.Skip`, lengthened timeout or suite serialisation" | **Confirmed** — and the two flaky tests are byte-identical to main |
| "No existing test weakened or deleted" | **Confirmed** — 5 removed lines, all the leaked `go func` starts |
| "transcripts are in the repo under `docs/evidence/pr2/`" | **Confirmed** — 13 files committed, not scratch-only |
| **"30 consecutive full runs per leg, 120 runs, zero failures"** | **NOT reproduced** — same 120-run protocol, **2 failures**, both the PR's own new test (FINDING 1). The V-1 tests were green 120/120. |
| `make ci` exit 0 | **Confirmed** |
| "Reported to the chair, not fixed here: `obs.Redact`'s presigned rule is anchored on the query separator" | **Confirmed as stated** — the new test deliberately places `X-Amz-Credential` inside a URL query, and the test comment says so. Honest disclosure, correctly scoped out. |

## Cleanup

Removed by exact name: containers `vzverify-pg`, `vzverify-valkey`, `vzverify-valkey2`,
`vzverify-redis`; the verifier clone and its worktrees under the scratch directory. No
image was built or deleted. `vizra-pr2-*` and `vidra-*` containers untouched.

---

## Verdict: **FAIL**

- **V-1 — CLOSED.** Flake reproduced at base (3/20 shuffled, seeds recorded). Mechanism
  proven independently on the real code path (175/300 → 0/300). Fix is in the product;
  the two failing tests are unmodified and green.
- **V-2 — CLOSED.** All three log sites proven individually by mutation, including the
  one the earlier verifier did not name. Redact-before-truncate confirmed; the database
  cause survives redaction.
- **`attempts` note — CLOSED.** Present above `SweepExpiredLeases`, greppable, carried
  into the generated doc comment, wording correct, and protected by `sqlc-verify` (M5).
- **Original flake REPRODUCED: yes.**

FAIL on **FINDING 1** alone: a new ~1-in-30 intermittent failure in a required lane,
reproduced three times and made deterministic, in the slice whose acceptance bullet is 30
consecutive green runs per leg. The fix is four lines and I have run it green against the
deterministic reproduction. Findings 2-4 are non-blocking.

PASS is not a merge and not VERIFIED; this is a FAIL and the chair records neither.

---
---

# Re-verification at `bfd2d5f`

| | |
|---|---|
| **Head SHA verified** | `bfd2d5f3f550c249f33f0834b97558646a8b67e5` |
| Previous verdict | FAIL at `1a6d8bd` (FINDING 1) |
| Commits added | `2f0688c` fix(test): wait on the log buffer, not on a claim-time counter · `bfd2d5f` docs(evidence): round-1 transcripts |
| `1a6d8bd` an ancestor of `bfd2d5f`? | **Yes** (`git merge-base --is-ancestor` → true) — nothing was rewritten |
| Head moved during re-verification? | **No** — re-checked at start and end |
| Checkout | **fresh clone**, new scratch tree, new containers (`vzv2-pg` :55633, `vzv2-valkey` :56680, `vzv2-redis` :56681), same pinned CI digests |
| **Verdict** | **PASS** |

| Finding | State |
|---|---|
| **FINDING 1** — new flake in the PR's own test | **CLOSED** |
| **FINDING 2** — AGENTS.md overclaim on `safeError` | **CLOSED** |
| **FINDING 3** — GitGuardian red, no triage | **CLOSED**, with a correction the owner needs (below) |
| **FINDING 4** — third affected test unrecorded | **CLOSED** |

## Frozen paths

`git diff --stat 415a6d1 bfd2d5f` is **empty** for all of `migrations/`, `api/`, `go.mod`
and `go.sum`. `migrations/manifest.sha256` unchanged; `./scripts/migration-manifest.sh
check` → `ok append-only manifest matches (8 migrations)`; `append-only` green in CI.

Delta `1a6d8bd..bfd2d5f`: `.gitguardian.yaml` +22, `AGENTS.md` 1/1, `internal/jobs/worker.go`
8/8, `internal/integration/golden_test.go` +37/−10, **new** `internal/jobs/logsites_test.go`
+99, plus evidence transcripts. No product logic outside `worker.go` changed.

## FINDING 1 — CLOSED

The fix is exactly the one I proposed: the wait now requires all three log lines in the
buffer, and keeps the database conditions as necessary-but-not-sufficient.

**My own red/green, using my round-1 diagnostic** (`time.Sleep(3*time.Second)` in the
`leaky-retry` handler only, never committed):

| Configuration | Result |
|---|---|
| **New** wait (log buffer) + 3 s diagnostic sleep | **GREEN 3 / 3** |
| **Old** proxy wait (`c.Attempts >= 1`) restored + same sleep | **RED 3 / 3** — `golden_test.go:1662: the worker never logged "jobs: retrying"` |

That is a controlled mutation in both directions: the old condition is deterministically
red under the diagnostic and the new one is deterministically green.

**Volume, all at `bfd2d5f`, `go test -race -count=1 … -tags=integration ./...`:**

| Leg | Mode | Runs | Failed |
|---|---|---|---|
| PostgreSQL 18 + Valkey | source order | 20 | **0** |
| PostgreSQL 18 + Valkey | `-shuffle=on` | 20 | **0** |
| PostgreSQL 18 + Valkey | explicit seeds ×10 | 10 | **0** |
| PostgreSQL 18 + Redis 7.2 | source order | 20 | **0** |
| PostgreSQL 18 + Redis 7.2 | `-shuffle=on` | 20 | **0** |
| PostgreSQL 18 + Redis 7.2 | explicit seeds ×10 | 10 | **0** |
| **Total full suite** | | **100** | **0** |
| `TestAWorkerWithAPlainHandlerLogsNoCredentials` standalone | `-race` | **60** | **0** |

At `1a6d8bd` the same standalone loop failed 1 of 40 and the suite 2 of 120. Here: 0 of 60
and 0 of 100.

Recorded seeds (explicit `-shuffle=<seed>`, both legs, all exit 0):
`11111111, 22222222, 33333333, 44444444, 55555555, 66666666, 77777777, 88888888,
99999999, 12345678`.

**Honest limitation:** my 40 `-shuffle=on` runs carry no seeds, because `go test` prints
`-test.shuffle <seed>` only for a *failing* package — the repo's own Makefile comment says
so. That is why I added the 20 explicitly-seeded runs. The builder's transcripts use
explicit per-run seeds throughout, which is the better practice and is reproducible.

### Audit of every other wait in `internal/integration` — done independently

The builder claims an audit of the 8 waits it added or touched. I was asked to spot-check
three; I checked **all seven** others plus the helper, by reading each wait and the
assertions that follow it. The rule applied: *the wait must be on the observable the
assertion reads, or on a value the database writes in the same statement as the state
waited for.*

| line | Test | Waits on | Assertions after | Verdict |
|---|---|---|---|---|
| 596 | `TestWorkerRunsAndCompletesAJob` | both jobs `succeeded` | none — the wait *is* the assertion | safe |
| 627 | `TestRetryLadderAndTerminalFailure` | `state='dead'` | — | safe (`RecordDeadLetter` writes state + `last_error` in one statement) |
| 632 | `TestRetryLadderAndTerminalFailure` | `state='failed'` | `Attempts`, `LastError` | safe (`FailJob` writes state + `last_error` + `finished_at` in one statement; `attempts` was set earlier at claim) |
| 1254 | `TestRetryLadderActuallyWalksTheLadder` | `state='queued' && Attempts==1` | `RunAfter` in the future, `LastError` | safe — and notably **not** the round-1 mistake: `queued && attempts==1` is uniquely the post-`RetryJob` state (enqueue is `queued/0`, claim is `leased/1`), and `RetryJob` writes state + `run_after` + `last_error` in one statement |
| 1278 | `TestRetryLadderActuallyWalksTheLadder` | `state='dead'` | `calls >= 3` | safe — `calls++` is at handler *entry* (`golden_test.go:1243-1245`), so it precedes the state change |
| 1320 | `TestAJobWhoseWorkerDiedIsReclaimedAndCompleted` | `state='succeeded'` | none | safe |
| 1498 | `TestAMultibyteErrorIsStoredInLastError` | terminal state | `LastError` | safe (same statement) |
| helper | `startWorker` | the `stopped` channel | that the goroutine returned | the observable itself; fails the test after 30 s |

**No other wait in `internal/integration` waits on `attempts`, a row count, or a state
that becomes true before the asserted observable.** My table and the builder's
`ROUND1-wait-on-the-observable.md` agree line for line; I reached it independently.

The three `time.Sleep` calls in the file (lines 814, 1190, 1276) all **pre-date this PR
entirely** — they are present verbatim at base `415a6d1` — so none is a masking change
introduced here.

## FINDING 2 — CLOSED

All eight previously-raw sites now pass `safeError(...)`: `worker.go:192, 293, 308, 324,
338, 365, 384, 388`, joining 316, 329 and 342. The AGENTS.md row no longer claims a bare
"every error log site"; it now names the behaviour test and the coverage test separately,
and the coverage claim ("**all 11**") is mechanically enforced rather than asserted.

`internal/jobs/logsites_test.go` parses `worker.go`'s AST and requires every `"error"`
attribute value to be a `safeError(...)` call, with a hard count guard. My mutations:

| Mutation | Result |
|---|---|
| unwrap one site (`jobs: heartbeat failed`) | **RED** — `logsites_test.go:68: worker.go:365:49: the "error" value is err.Error(...), not safeError(...)` — names file:line:col |
| add a **twelfth raw** error log site | **RED** — names `worker.go:385:54`, **and** `checked 12 … expected 11` |
| add a twelfth site that **is** `safeError`-wrapped | **RED** — `checked 12 … expected 11` (the drift guard bites even when the new site is correct) |

The test cannot pass vacuously: the count guard fires if the attribute key is renamed or
the calls restructured.

**Diagnostic value is intact.** I checked that redacting database causes destroys nothing.
`obs.Redact` is a complete **no-op** on every realistic driver error shape:

```
UNCHANGED  ERROR: null value in column "run_after" of relation "jobs" violates not-null constraint (SQLSTATE 23502)
UNCHANGED  ERROR: new row for relation "jobs" violates check constraint "jobs_attempts_bounded" (SQLSTATE 23514)
UNCHANGED  ERROR: duplicate key value violates unique constraint "jobs_idem" (SQLSTATE 23505) Detail: Key (kind, idempotency_key)=(noop, abc) already exists.
UNCHANGED  ERROR: canceling statement due to user request (SQLSTATE 57014)
UNCHANGED  ERROR: could not serialize access due to concurrent update (SQLSTATE 40001)
UNCHANGED  timeout: context deadline exceeded
```

Live pgx errors against a real server likewise pass through untouched, SQLSTATE, relation
name and dial diagnostics preserved:

```
RAW/REDACTED identical: ERROR: relation "no_such_table_here" does not exist (SQLSTATE 42P01)
RAW/REDACTED identical: failed to connect to `user=vizra database=x`: 127.0.0.1:1 … connection refused
```

And the hypothetical the new test exists to guard against **is** caught:

```
RAW:      failed to connect to postgres://vizra:hunter2@db:5432/vizra: connection refused
REDACTED: failed to connect to postgres://[redacted]@db:5432/vizra: connection refused
```

So the belt-and-braces has zero diagnostic cost and real defence-in-depth value. My
round-1 argument — that the eight sites were safe *because pgx happens to redact today* —
is exactly the kind of third-party-behaviour dependency the new test removes. The stronger
fix is the right one.

*Residual, not a finding:* the AST test keys on the literal attribute name `"error"`. A
future site logging a cause under a different key (`"cause"`, `"detail"`) would not be
checked. The count guard limits the blast radius and nothing today does this.

## FINDING 3 — CLOSED, and the builder's correction **holds**

`.gitguardian.yaml` gains two per-path entries with written reasons and no glob:
`internal/integration/golden_test.go` (naming the flagged literal and why deleting it
would delete VZ-OPS-005's coverage) and `docs/evidence/pr2/` (scoped to this one slice's
directory, explicitly so a future slice cannot hide a real secret under a standing
exclusion). The triage table is in the PR body.

**The builder further claims `.gitguardian.yaml` is decorative for this red check. I
verified it, and it is true.** This matters for what the owner must do:

| Evidence | Result |
|---|---|
| `grep -rn "ggshield\|gitguardian\|GitGuardian" .github/` | **one hit only**: `.github/CODEOWNERS:38:/.gitguardian.yaml @yegamble`. No workflow runs ggshield. |
| `grep -rn "ggshield" .` (excluding the config itself) | **none** |
| `.pre-commit-config.yaml` | **does not exist** |
| Failing check's app | `app_slug: gitguardian`, `app_name: GitGuardian` — the **GitHub App**, scanning server-side, not a workflow |
| Reported count at `1a6d8bd` | `1 secret uncovered!` — "scan of 2 commits" |
| Reported count at `bfd2d5f` | `1 secret uncovered!` — "scan of 4 commits" |
| Flagged occurrence at both SHAs | **identical** — incident `37481217`, occurrence `298761579`, commit `4f02e18`, `internal/integration/golden_test.go` line R1572 |

Adding the exclusion changed the App's verdict by **nothing at all**. `.gitguardian.yaml`
configures the ggshield CLI, which nothing in this repository runs. **Consequence for the
owner:** GitGuardian will stay red on this PR no matter what is committed. Clearing it
requires an action in the GitGuardian dashboard (resolve incident `37481217` as a false
positive, or add a server-side ignore), or removing the literals — which would remove the
redaction coverage. GitGuardian is **not** a required check and does not gate the merge.

The committed `.gitguardian.yaml` entries are still worth having — they document the
triage next to the values and cover ggshield if anyone runs it locally — but they are not
the remedy, and the PR body now says so rather than implying the red is fixed.

## FINDING 4 — CLOSED

`TestAJobWhoseWorkerDiedIsReclaimedAndCompleted` is recorded as the third affected test in
the PR body (line 45), in the meta execution plan (line 270), and in the wait-audit table
of `docs/evidence/pr2/ROUND1-wait-on-the-observable.md`.

## Regression canaries — all still die

| Canary | Result |
|---|---|
| **M1** — resolve a zero `RunAfter` with the host clock again | **RED** — `run_after … is not created_at …: they differ by 1961 µs` |
| **M3** — the three handler-error sites back to raw | **RED** — leaked the Vizra API key; **and** `TestEveryErrorLogSiteInTheWorkerIsRedacted` named 2 sites |
| **M6** (mine) — `COALESCE(now(), …)`, explicit delay discarded | **RED** — `an explicit RunAfter was not stored verbatim: stored …00:06:41Z, asked for …02:06:41Z` |

Restored after each: green.

## No masking, no test weakened

Masking patterns **added** in `1a6d8bd..bfd2d5f` across `*.go`, `Makefile`, `.github/`:
`time.Sleep` **none**, `t.Skip` **none**, `t.Parallel` **none**, `-p 1`/serialisation
**none**, `Eventually` **none**, retries **none**, timeouts/deadlines changed **none**
(the only `deadline` hit is a comment).

`git diff --numstat 1a6d8bd bfd2d5f -- '*_test.go'` → `37 10 golden_test.go`,
`99 0 logsites_test.go`. **All ten removed lines** are the old wait condition and the old
inline `[]string{…}` literal; both are replaced by strictly stronger versions — the wait
gained the three log-line checks, and the literal was hoisted to `lines` and is still
iterated by the post-wait `Fatalf` loop, which is retained deliberately so a timeout names
*which* branch never logged. No assertion lost, no test renamed, deleted or skipped.

## Lanes and CI at `bfd2d5f`

| Check | Command / source | Result |
|---|---|---|
| Full suite | `go test -count=1 -tags=integration -v ./...` | exit 0 — **920 pass, 0 fail, 0 skip** (claim matched exactly) |
| AST coverage test | in the above | `logsites_test.go:88: 11 error log sites in worker.go, all going through safeError` |
| Whole gate | `make ci` | **exit 0** — `make ci: all lanes passed` |
| sqlc drift | `make sqlc-verify` | exit 0 |
| manifest | `./scripts/migration-manifest.sh check` | exit 0, 8 migrations |

GitHub, this SHA — every required lane executed and green, nothing skipped or cancelled:

| Check | Conclusion | completed |
|---|---|---|
| `append-only` | success | 23:55:37Z |
| `build-test` | success | 23:59:46Z |
| `cache-matrix` | success | 23:57:13Z |
| `cache-matrix-leg (valkey, …)` | success | 23:56:50Z |
| `cache-matrix-leg (redis, …)` | success | 23:57:08Z |
| `govulncheck` | success | 23:56:05Z |
| `docker-build` | success | 23:58:52Z |
| **`ci-required`** | **success** | **2026-09-21T00:00:08Z** |
| `GitGuardian Security Checks` | failure | 23:55:38Z — **not a required check**, see FINDING 3 |

`ci-required` completed **last**, after `build-test` — the fan-in genuinely waited. The
manifest `.github/required-checks.txt` still matches `FLOOR_LANES` exactly (5 lanes). All
three `-shuffle=on` steps ran and succeeded on this SHA:

```
JOB build-test [success]                       Integration tests, shuffled order (PostgreSQL 18 + Valkey) -> success
JOB cache-matrix-leg (valkey, …) [success]     Integration tests against valkey, shuffled order -> success
JOB cache-matrix-leg (redis, …)  [success]     Integration tests against redis, shuffled order -> success
```

## Builder's round-1 evidence, checked

| Claim | Verdict |
|---|---|
| `ROUND1-wait-on-the-observable.md`: RED 3/3 old wait, GREEN 3/3 new wait under the 3 s diagnostic | **Reproduced exactly** |
| Audit of all 8 waits, only the V-2 test was a proxy | **Confirmed independently**, all seven others plus the helper |
| Four `AFTER-*-30runs*.txt`, 120 runs, 0 failures, explicit per-run seeds | **Consistent with my 100 runs, 0 failures.** Their headers say `source SHA: 2f0688c … tree clean: 2 modified` / `4 modified` — the modified files are the transcripts being written; I did not rely on them, which is the point of independent measurement |
| `FINAL-LANES.txt` / 920 pass, 0 fail, 0 skip | **Confirmed exactly** |
| `.gitguardian.yaml` is decorative for the App's red | **Confirmed** — identical incident and occurrence before and after |

## Cleanup

Removed by exact name: containers `vzv2-pg`, `vzv2-valkey`, `vzv2-redis`; the
re-verification clone and its worktrees under the scratch directory. No image was built or
deleted. `vizra-pr2-*` and `vidra-*` containers untouched.

---

## Re-verification verdict: **PASS**

- **FINDING 1 — CLOSED.** The proxy wait is replaced by a wait on the log buffer. Red 3/3
  with the old condition and green 3/3 with the new one under my deterministic diagnostic;
  0 failures in 100 full suite runs across both cache legs (ordered, `-shuffle=on`, and
  explicitly seeded) and 0 in 60 standalone runs, against 2/120 and 1/40 before.
- **FINDING 2 — CLOSED.** All 11 error log sites go through `safeError`, enforced by an
  AST test with a count guard that I broke three different ways. AGENTS.md is now exactly
  true. Redaction costs no database diagnostic.
- **FINDING 3 — CLOSED**, with a correction the owner needs: `.gitguardian.yaml` does not
  and cannot change the GitHub App's verdict. GitGuardian will remain red until the
  incident is resolved in the dashboard. It is not a required check.
- **FINDING 4 — CLOSED.**
- V-1, V-2 and the `attempts` note remain CLOSED; all round-1 canaries still die.
- No migration, API contract, `go.mod` or `go.sum` change. No masking. No test weakened.
- `ci-required` green on `bfd2d5f`, all five required lanes executed, fan-in completing
  last.

PASS is not a merge and not VERIFIED — the chair records those.
