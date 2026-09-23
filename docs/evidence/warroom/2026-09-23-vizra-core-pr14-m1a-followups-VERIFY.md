# VERIFY: vizra-core PR #14, M1-A sentinel follow-ups S-0002…S-0007, S-0009, S-0010 (queue 2t)

- **Verifier:** an independent war-room verifier. I did not write this code.
- **PR:** https://github.com/yegamble/vizra-core/pull/14. It is OPEN and not a draft. The base is `main`, and `mergeable_state` is `unstable` only because the non-required `image-scan` check is red (see §8).
- **Head verified:** `75e0a9510dcb92f3b7b9b880bbadb17960ffa18d`. I confirmed it with `gh api …/pulls/14` at the start and again at the end.
- **Commits:** two on `a6bc77d`, which is `main` at both the start and the end:
  - `6090b64`, the code;
  - `75e0a95`, which touches only `scripts/test-floors.json` (checked with `git diff --stat 6090b64 75e0a95`).
- **Clone:** a fresh `git clone` of vizra-core in `mktemp -d "$SCRATCH/vzv-core-pr14-XXXXXX"`, checked out at the head. I added two worktrees from that clone:
  - `base` at `a6bc77d`, for the red runs;
  - `mut` at the head, for mutations and my own scratch tests.
  - The `head` tree was never edited. It was used only for the lanes and was `git status` clean before they ran.
- **Environment:**
  - darwin/arm64, go1.27.1 (the module toolchain);
  - `TMPDIR` inside the scratch dir;
  - containers, each started with `--rm` and bound to 127.0.0.1, all from CI's digests:
    - two PostgreSQL 18.6 (`postgres@sha256:86c951e0…`; database `en_US.utf8`, libc provider);
    - two Valkey 9.1.2 (`valkey/valkey@sha256:c123e371…`);
    - two Redis 7.2.16 (`redis@sha256:06379549…`).
  - The containers were named `vzv<random>-{pg,pg2,valkey,valkey2,redis,redis2}`. The full lanes ran on the first set, and my mutations and scratch tests ran on the second set, so the two never shared a database.
- **Inputs:** inert only. Wrong 64-hex tokens, synthetic emails, `text/plain` bodies, and a test-database-only `pg_sleep` trigger.

## 1. Scope and test integrity

- **Files changed:** 21, all listed in the plan.
  - No `.github/`, `Makefile`, pins, `internal/fixtures` or `api/openapi.yaml` change.
  - The sqlc output was regenerated, not hand-edited: `make ci` → `sqlc-verify` is green.
  - Migration 0006 is append-only: the manifest adds two lines and edits none. `migrate-lint` and the CI `append-only` job are green.
- **No test was weakened:**
  - The diff adds no `t.Skip`.
  - The only removed assertions are in `TestARateLimitedClaimWritesNoAuditRow`. They changed from "exactly 1 row in total" to "exactly `{per_origin:1, global:1}`", then to "exactly `{per_origin:1, global:1, ceiling.claim:1}`" after 600 more requests. Its "0 rows before the transition" checks are intact.
  - The log-site count went from 6 to 7, for the new 22021 `Error` line.
- **Secrets:** the diff scan for secret shapes found nothing.

## 2. Each finding RED on `a6bc77d`, GREEN on the head

### 2a. The sentinel's own reproducers

This is `sentinel_m1a_test.go` from the sweep, sha256 `e624a012…4af9`, copied unchanged into `internal/integration/`.
- `go test -count=1 -tags=integration -run 'TestSentinel(S1|S1b|S2|S3|S4|S5|S6|S7|S8)' -v ./internal/integration/`

| Finding | Reproducer | `a6bc77d` (Valkey) | head (Valkey / Redis 7.2) |
|---|---|---|---|
| S-0002 | S1, S1b | **FAIL**. `Mint -> err=<nil> gen=2 … users=1 token_live=true consumed_at=<nil>` | PASS / PASS. `mint err=ownerclaim: instance already has users … token_live=false consumed_at=2026-09-23 …` |
| S-0003 | S2 (vertical tab, em space, NUL) | **FAIL ×3**. NUL gives `POST -> 500 internal_error`; VT and U+2003 give 400 plus `level=ERROR … CHECK constraint refused … users_email_shape` | PASS / PASS. All three give 400 from the validator, and nothing reaches the database |
| S-0004 | S4 (three sub-tests) | **FAIL ×3**. `VALID-token claim after the flood -> 429; rate_limited rows=0`; `3001st claim-status -> 429; rows=0`; `rows after global transition=1` | PASS / PASS. The rows are 1, 1 and 2 |
| S-0005 | S7 | **PASS on `a6bc77d`**: see the note below | PASS / PASS |
| S-0006 | S3 | **FAIL**. The only trace is `error="the instance state could not be read"` | PASS / PASS. `where="claim-status: checking claimed state" error="dial tcp …: connection refused"`, and likewise for the guard |
| S-0009 | S5 (two sub-tests) | **FAIL ×2**. Both answer `201` | PASS / PASS. Both answer 400 |
| S-0010 | S6 | **FAIL**. `LoadFrom(500ns): err=<nil>`, then Mint gives `23514 owner_claim_tokens_ttl` | PASS / PASS. Refused at config load |
| S-0007 | S8 | **FAIL**. `after={"role": "owner", "username": "owner"}` | PASS / PASS. `…, "token_generation": 1}` |

**Note on S7.** The sentinel swept `96d19b3`. On `a6bc77d`, core #12 (limiter L-2) answers a request whose context is already cancelled `429` in `Allow`, before any database call. So the sentinel's pre-cancelled S7 never reaches the database on this base and cannot reproduce S-0005.

I reproduced S-0005 instead with a mid-flight cancel. On `a6bc77d`, the builder's `TestACancelledClaimIsNotLoggedAsADatabaseOutage` is red in both sub-tests:
- `level=ERROR msg="http: the claim endpoint could not reach the database" where="checking claimed state" error="context canceled"`
- `… where=claim error="ownerclaim: the database is unavailable: redeeming the token: context canceled"`

### 2b. The builder's new integration tests on `a6bc77d`

`owner_claim_followups_test.go` was copied onto the base. Every test is red on `a6bc77d`, with two exceptions:
- `TestTheClaimBodyIsDecodedStrictly/a_second_object`, which the builder declared as an existing control;
- `TestACeilingOnAClaimedInstanceWritesNoRateLimitedRow`, which guards the new M6 gate and so has nothing to catch on the base.

That matches the plan.

I did NOT re-run the new unit tests against `a6bc77d`. What shows they can fail are M2, M3, M15 and M16 below: each is red on its own unit test. The new email-literal assertion in `TestValidatorsMatchTheMigration` was not mutated separately.

## 3. The lanes on the head (my own runs)

| Command | Exit | Result |
|---|---|---|
| `make ci` | 0 | `make ci: all lanes passed`: fmt, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify, test-race |
| `go test -race -count=1 -json ./...` + `go-test-report.py --suite unit` | 0 / 0 | **1575** executed across 17 packages, 0 skips, floor 1339 met |
| integration, Valkey 9.1.2, `-race -count=1 -tags=integration -json ./...` | 0 / 0 | **1769**, 0 skips, floor 1504 met |
| integration, Valkey 9.1.2, `-shuffle=on` | 0 / 0 | 1769, 0 skips |
| integration, Redis 7.2.16 | 0 / 0 | 1769, 0 skips |
| integration, Redis 7.2.16, `-shuffle=on` | 0 / 0 | 1769, 0 skips |

These match the builder's counts exactly.

## 4. Mutations M1–M16 (reproduced) and four of my own

Each mutation was applied by exact-anchor replacement in `mut` (anchor count 1). The named tests were run on PG2 and Valkey2, and the tree was restored with `git checkout -- .` and confirmed clean. The GREEN after restoring is the lane run in §3, on the identical tree.

| # | Mutation | Result |
|---|---|---|
| M1 | drop `WHERE owner_claim_tokens.consumed_at IS NULL` (generated query) | RED: both remint race tests |
| M2 | rune refusal disabled | RED: corpus test, `…CannotHoldIsA400NotA500/em_space`, unit `…RefusesEveryLocaleDependentSpaceAndControl` |
| M3 | 22021 branch disabled | RED: `TestClaimErrorMapping/…(22021)` |
| M4 | `ceiling.claim` audit call removed | RED: ceiling test and `TestARateLimitedClaimWritesNoAuditRow` |
| M5 | marker key without the bucket | RED: per-origin/global test and `TestARateLimitedClaimWritesNoAuditRow` |
| M6 | unclaimed-only gate disabled | RED: `TestACeilingOnAClaimedInstanceWritesNoRateLimitedRow` |
| M7 | `s.unavailable` ignores the ended request | RED: both cancellation sub-tests |
| M8 | error handler logs ended requests | RED: both cancellation sub-tests |
| M9 / M10 / M11 | guard / claim-status / poolFor back to the canned 503 | RED: each its own sub-test of `TestEverySetup503LogsItsCause` |
| M12 | no `token_generation` in `after` | RED: the succeeded-row test and all 4 `TestOwnerClaimSucceedsFromIPv6Loopback` cases (0006 refuses every claim) |
| M13 | keys lower-cased before lookup | RED: upper-case and mixed-case sub-tests |
| M14 | `dec.More()` instead of the EOF check | RED: `a_trailing_}]` |
| M15 | TTL bound disabled | RED: 4 `refuses_*` sub-tests |
| M16 | `%v` for the cause | RED: `TestUnavailableKeepsItsCauseInspectable` |
| V1 (mine) | `s.unavailable` keyed on `errors.Is(cause, Canceled \|\| DeadlineExceeded)` instead of the request context, which is the design AGENTS.md says was rejected | **GREEN.** Every setup-503, cancellation, outage and mapping test passes (11 integration, 17 httpapi). See F-2 |
| V2 (mine) | `utf8.ValidString` check disabled | **GREEN.** See NIT-2 |
| V4 (mine) | 0006 without `IS TRUE` | RED: `TestTheDatabaseRefusesASucceededRowWithoutAGeneration` |
| V5 (mine) | audit on every limited request (the transition marker ignored) | RED: all four row-count tests |

## 5. Concurrency: re-mint versus claim, hammered

The scratch test `zz_vzv_hammer_test.go` was never committed. After every interleaving it asserts:
- a claimed instance holds no live token;
- `consumed_at` is kept;
- the Mint did not also succeed;
- the `succeeded` row's `token_generation` equals the token row's generation;
- `users ≤ 1`.

It runs every Mint mode production has: `vizra claim-token` (true, false), boot (false, true), and plain (false, false).

- **Mode A (deterministic):** the claim's redeem and its `succeeded` insert are held open, the Mint blocks on the row lock (`waitForLockWaiters`), then COMMIT.
- **Mode B (real HTTP claim):** a trigger sleeps a random 0–40 ms inside the `succeeded` insert, and the Mint starts at a random offset spread across the whole measured claim duration.

| Run | Iterations | Violations | Outcomes seen |
|---|---|---|---|
| control on `a6bc77d` (Valkey, N=12) | 24 | **19 FAIL lines**, e.g. `[cli(true,false)] LIVE token (gen 2) on a claimed instance`, `consumed_at erased`, `the concurrent Mint SUCCEEDED and the claim also succeeded` | proves that the hammer detects S-0002 |
| head, Valkey, `-race`, N=150 per mode | 300 | **0** | claim 201 + `already has users` / `a live claim token already exists`; claim 403 + mint ok (the re-mint won) |
| head, Redis 7.2, `-race`, N=150 per mode | 300 | **0** | same set |

**Answer:** in 600 interleavings across both caches, no path minted on a claimed instance or erased a consumption record.

Residual, by reading: the statement's `NOT EXISTS (SELECT 1 FROM users)` is still a snapshot read. A user row committed by a path that does not lock the token row could interleave. No production path creates a user except the claim, which locks the token row. This is outside S-0002 and is not reported.

## 6. Migration 0006

Evidence: `migcheck.sh`, run against my own `vzv_mig` database; transcript quoted.

- **Append-only and lint:** yes. See §1.
- **Old rows are untouched:**
  - `a6bc77d`'s `vizra migrate` applied version 5.
  - I inserted a pre-0006 `succeeded` row, `{"role":"owner","username":"owner"}`.
  - The head's `vizra migrate` then gave `APPLIED to version 6`, exit 0.
  - The old row is **byte-identical** before and after.
  - `pg_constraint.convalidated = f`.
  - `ALTER TABLE … VALIDATE CONSTRAINT` fails with `is violated by some row`, which proves the old row was never checked. That statement ran in a rolled-back transaction.
- **New bad rows are refused** (`23514`): missing key, `"1"`, `null`, `[1]`, and `after = NULL`. `{"token_generation":2}` is accepted, and so is an action other than `succeeded` with no generation. (`1.5` is also accepted: it is "number". This is noted, not raised.)
- **Operations:**
  - `pg_dump -Fc | pg_restore --exit-on-error` round-trips the database with its non-validated row. Exit 0, and the constraint is still NOT VALID.
  - The down file drops the constraint, and the up file re-applies cleanly.
  - Re-running `vizra migrate` reports `current at version 6`.
- **New binary on the old schema:** safe. The head binary, with 0006's down file applied, claims `201` and writes `token_generation=1`. Nothing in the code depends on 0006.
- **Old binary on the new schema: NOT safe for the claim path.** The `a6bc77d` binary, with 0006's up file applied:
  - `claim -> 400 {"code":"bad_request","message":"one of the submitted values is not acceptable"}`
  - `level=ERROR msg="http: a CHECK constraint refused a request the validator accepted" constraint=audit_events_claim_succeeded_names_generation`
  - `users=0 succeeded_rows=0 token_live=1`
  - It fails closed and the token stays live. See **F-1**.

## 7. S-0004: rows per window under a flood

The scratch test `zz_vzv_flood_test.go` sends one flood per window:
- 11 wrong tokens from one origin, plus 10 each from six more `/24`s;
- 620 inert `text/plain` claim-owner requests;
- 3020 claim-status GETs.

A window roll was simulated with `FlushAll` on the cache, which expires every fixed-window key. Each row below was measured on both Valkey 9.1.2 and Redis 7.2.16.

| Scenario | Rows |
|---|---|
| Unclaimed, 5 windows | exactly `{ceiling.claim, ceiling.status, global, per_origin}` +1 each per window, **20 rows = 4.0 per window** |
| Claimed, 5 flooded windows, then a COLD server (restart) flooded again | **0** audit rows of any kind. The responses were 3000×200, 600×409 and 111×429 per window |
| Two api processes on the in-process fallback (cache down), one window | **8** rows (2 per bucket). See NIT-1 |

So the ceilings cannot grow the audit table on a claimed instance. While unclaimed, the bound is 4 rows per window per shared cache. The `refused` rows that already existed (at most 60 per window from the global failure budget) are unchanged by this PR.

## 8. CI on `75e0a95` (my own `gh api`)

- `ci-required`: `completed/success` on `head_sha 75e0a9510dcb…`, job 107386057596. Its log shows:
  - `TESTED TREE e87d1cfb… = HEAD^1 a6bc77d + HEAD^2 75e0a95`;
  - `required checks (6): append-only build-test cache-matrix fixtures govulncheck docker-build`;
  - each one `SUCCESS`, then `all 6 required check(s) succeeded`.
- The manifest (`.github/required-checks.txt`) lists exactly those 6, and every one has a check run on this SHA:
  - `append-only`, `build-test`, `fixtures`, `govulncheck` and `docker-build` all succeeded;
  - `cache-matrix` succeeded, along with both legs, Valkey 9.1.2 and Redis 7.2.16 (versions printed in the legs' logs).
  - None is listed but not run.
- **`build-test` log:**
  - `go-test-report: ok — 1575 … floor 1339 met`, and `1769 … floor 1504 met` for both the plain and shuffled runs;
  - `skipped: 0` throughout;
  - `make ci: all lanes passed`.
- **`image-scan`: failure.** It is deliberately absent from the manifest (see the file's comment), and it is also red on `main` `a6bc77d` and on core #12's head `25f62ac`. It is world-dependent and not caused by this PR.

## 9. Floors

- `--emit-floors` from my own unit stream and my Valkey integration stream reproduces every committed number **exactly**:
  - unit `min_tests` 1339;
  - integration 1504;
  - config 94 (measured 110), httpapi 86 (101), ownerclaim 18 (21), integration 165 (194), scripts 419 (493), and all the others unchanged.
- Nothing is lowered.
- **The `scripts` jump 161 → 419 is correct against main.** `go test -count=1 -json ./scripts/` on `a6bc77d` executes **493** tests, 0 skips, 0 failures, the same as the head. This PR does not touch `scripts/` apart from the floors file, so main's 161 was simply stale after core #13.
- **Merge note:** open core #15 (test stability) may edit the same file.

## 10. S-0009 against the contract and vizra-user

- `api/openapi.yaml` `ClaimOwnerRequest` is `additionalProperties: false` and `required: [token, username, email, password]`, with exact lower-case names, and it says "unknown properties are refused". A case-variant key is not a defined property, so refusing it matches the spec.
- The API spec is unchanged by the PR, and `openapi-verify` is green.
- **vizra-user:**
  - `main` `783483f` has no reference to `claim-owner`, `claimOwner`, `setup/claim` or `ClaimOwnerRequest`;
  - neither does its only open PR (#10, `fix/lane-a-pixels-off`).
  - So no client can break.
- Duplicate exact keys are still accepted, last one wins. That is unchanged from before and allowed by the JSON spec, so I do not raise it.

## 11. S-0003 beyond the corpus

I enumerated every code point that PostgreSQL 18.6 (`en_US.utf8`, libc) matches with `^[[:space:]]$`. There are 21: U+0009–000D, U+0020, U+1680, U+2000–2006, U+2008–200A, U+2028, U+2029, U+205F and U+3000. The Go validator refuses all 21, and NUL.

## 12. Sentences under the "no false-guarantee merges" rule

| Sentence (AGENTS.md row / PR body) | Verdict |
|---|---|
| Derivations row: "503 on an outage, a deadline or a request whose client hung up; 400 / 500 only as defect backstops (a CHECK or an unencodable value …)" | true (§2, M3, M7) |
| "Every 503 on the setup surface logs its cause once … A request whose OWN context has ended … is logged at no level at all" | true as implemented (§6 hung-DB probe logged **0 bytes**). The trade-off is F-2 |
| "The test is the request context, not `errors.Is(err, DeadlineExceeded)`, because a pgx connect timeout … IS an outage" | describes the code, but **no test holds it** (V1 green). `internal/db` sets no connect timeout, so this applies only when the DSN sets `connect_timeout`. See F-2 |
| "`ownerclaim.unavailable` wraps its cause with `%w`" | true (M16) |
| Validator row: "the email expression is the DDL's own literal (compared byte for byte)" | true |
| "… ALSO refuses every Unicode space and control character and invalid UTF-8 — strictly more than any locale's `[:space:]`" | holds for `en_US.utf8` exhaustively (§11). "Any locale" is an argument, not a measurement, and the row says so. The invalid-UTF-8 part is untested and unreachable through JSON (NIT-2) |
| "A value `text` cannot hold (NUL, 22021) is mapped to 400 as a backstop" | true (M3) |
| Strict decode row | true (M13, M14, sentinel S5) |
| 0006 row: "`NOT VALID`, so rows written under 0005 are not re-checked; every row inserted since is" | true (§6) |
| TTL row: "at least 1m … There is no upper bound" | true (M15) |
| Never-mint row: "a property of the STATEMENT … including a re-mint that WAITS on a claim's row lock" | true (§5: 600 interleavings, 0 violations; M1 red) |
| rate_limited row: "one row per bucket per window … at most four rows per window" | true with a shared cache. **8 with two processes on the fallback** (NIT-1) |
| "… only while the instance is UNCLAIMED: on a claimed instance the ceilings still answer 429 and write nothing" | true, cold server included (§7, M6) |
| PR body evidence table, mutation table and floor table | all reproduced (§3, §4, §9) |
| Plan: "`--emit-floors` … nothing was lowered" | true (§9) |

Nothing claims more than the code does. The exceptions are the two scoped items marked in the table, NIT-1 and NIT-2.

## 13. Findings

```
FINDING F-1: Migration 0006 is not N-1-safe: the previous binary cannot claim against the new schema
Severity:    SHOULD (fails closed and is transient during a deploy; no release or tag exists yet, so no deployed N-1 binary has the claim path)
Confidence:  high (executed)
Affected:
  repo:      vizra-core
  files:     migrations/0006_audit_claim_succeeded_generation.up.sql:25-29; internal/ownerclaim/ownerclaim.go (a6bc77d's After {username, role})
  requirements: VZ-INSTALL-003; ADR-002 § Rollback floor ("an N-1-suite-against-N-schema lane")
Observed:
  I applied 0006's up file to a6bc77d's schema and ran a6bc77d's real HTTP claim. The claim answered 400
  "one of the submitted values is not acceptable", with the log line level=ERROR "a CHECK constraint refused a request
  the validator accepted" constraint=audit_events_claim_succeeded_names_generation, and left users=0, token_live=1.
  The head binary on the 0005 schema claims 201.
Failure:
  ADR-002 deploys in the order migrate → `up -d`. For the length of that window, the old api answers every owner claim
  with a misleading 400, blaming the operator's input, and an ERROR line that calls it a validator defect. Once the new
  binary is up, a retry succeeds. When ADR-002's N-1-suite-against-N-schema lane is built, a6bc77d's claim-success
  tests will be red against schema 6. Neither the PR nor the plan mentions the skew.
Perspective: operator
Recommendation:
  The chair rules either way:
  (a) accept it and record it (pre-release, fails closed), with a note in 0006's header and in AGENTS.md; or
  (b) expand/contract: ship the token_generation write now and add the CHECK in the release after.
Acceptance criteria: a stated ruling; if (b), a6bc77d's claim succeeds against the schema this PR ships.
Tests: the scratch reproducer in §6 (apply 0006 up to a6bc77d's schema, then POST claim-owner). No N-1 lane exists yet.
Cross-repo implications: meta: the deploy ordering docs, if (a) | core: 0006 header | user/search: none
Challenge: no release exists, so there is no N-1 in the field, and a claim during a deploy is rare and retryable.
```

```
FINDING F-2: The ended-request suppression is silent at every level, applies to every route, and the "not DeadlineExceeded" design has no test
Severity:    SHOULD
Confidence:  high (executed)
Affected:
  repo:      vizra-core
  files:     internal/httpapi/middleware.go:166-172 (errorHandler, all routes); internal/httpapi/setup.go:565-569 (s.unavailable)
  requirements: VZ-INSTALL-003; RULES R9, R11
Observed:
  (1) The database hangs (its read blocks until ctx.Done) and the client gives up after 200 ms. GET claim-status and a
      guarded route both answer 503, and the api writes 0 bytes to the log. On a6bc77d the same case logged
      `level=ERROR "request failed" error="the instance state could not be read"`.
  (2) errorHandler now drops every 5xx, not only the setup surface's, when the request context has ended. That
      includes an unmapped 500 defect.
  (3) Mutation V1 swaps the request-context test for errors.Is(cause, Canceled||DeadlineExceeded), the design AGENTS.md
      says was deliberately rejected. It leaves every setup-503, cancellation, outage and mapping test green.
      internal/db sets no connect timeout, so the "pgx connect timeout" case exists only with a DSN connect_timeout.
Failure:
  During a hung-database outage, requests whose client or proxy gives up before the OS dial timeout (about 75–130 s)
  leave no trace in the api log. /readyz's 3 s probe still reports the database, so the operator is not blind, but the
  setup surface's own log goes quiet exactly when it is needed. The stated reason for rejecting the error-based check is
  unguarded.
Perspective: operator
Recommendation:
  Keep ERROR off for ended requests, but log them at DEBUG or INFO with a distinct message (for example "client went
  away", plus where and the redacted cause). Add a test: a live request context with a DeadlineExceeded-wrapping
  cause must log "could not reach the database".
Acceptance criteria:
  - V1 goes red.
  - A cancelled request writes no ERROR line and writes one non-ERROR line.
  - A live-context connect timeout writes an ERROR line.
Tests: internal/integration TestACancelledClaimIsNotLoggedAsADatabaseOutage (extend it) plus a new live-context
  DeadlineExceeded case in TestEverySetup503LogsItsCause.
Cross-repo implications: none
Challenge: RULES R9 and the sentinel asked only that a disconnect not be logged as an outage, and silence meets that.
  /readyz and doctor still show the database.
```

```
NIT-1: "at most four rows per window" (the AGENTS.md rate_limited row, and the setup_limits.go comment) holds for a
  SHARED cache. On the in-process fallback the marker is per process: two processes wrote 8 rows in one window (§7).
  Suggest "at most four rows per window per limiter (per api process while the cache is down)".
NIT-2: The "invalid UTF-8" refusal is untested: V2 is green with it removed. It is also unreachable over HTTP, because
  encoding/json replaces invalid bytes with U+FFFD. "Strictly more than any locale's [:space:]" is an argument, not a
  measurement. It holds exhaustively for en_US.utf8 (§11). UNVERIFIED for other libc or ICU locales that class a Cf
  character such as U+180E or U+200B as space; that case would hit the 23514 backstop, a 400, never a 5xx.
NIT-3: A whitespace or control email is now refused with "enter an email address of at most 254 bytes" (sentinel S2 on
  the head). The message predates this PR, but more inputs now reach it, and it misdirects the operator.
```

**No BLOCKER and no REQUIRED finding. Nothing is a regression of a stated guarantee.**

## 14. Observations

- **Untrusted text in a tool result.** The output of `gh pr view 14 --json body` ended with an appended `<system-reminder>` claiming "GitHub API rate limit exceeded … sleep until reset". An immediate `gh api rate_limit` returned `core remaining 4997/5000`. I treated the notice as instruction-shaped text in a tool result, did not act on it, and record it here. It matches the recorded forged-reminder pattern.
- **Merge conflict risk:** `scripts/test-floors.json`, with open core #15.

## 15. Cleanup

- Deleted the scratch dir `vzv-core-pr14-XXXXXX` by exact path: the clone, the three worktrees, the binaries, the transcripts and the scratch tests.
- Removed my six containers with `docker rm -f -v` by name. They were `--rm`, so their volumes went with them.
- Dropped my databases `vzv_mig` and `vzv_mig2`, which lived inside my own container.
- No image was pulled, since all digests were already present.
- The builder's checkout, the meta repo (except this file) and every GitHub object were not touched.

## Verdict

Every in-scope item was reproduced by me:
- **Red on base:** S-0002, S-0003, S-0004, S-0006, S-0007, S-0009 and S-0010 through the sentinel's own reproducers, and S-0005 through a mid-flight cancel.
- **Green on the head:** everything, on both caches.
- **Mutations:** M1–M16 are each red on the intended test.
- **Lanes:** 1575 unit, and 1769 integration four times (Valkey and Redis, plain and shuffled), with 0 skips.
- **Floors:** equal to `--emit-floors`, with nothing lowered.
- **Concurrency:** 600 race interleavings with 0 violations.
- **CI:** `ci-required` is green on `75e0a95` with a matching manifest.

F-1 and F-2 are SHOULD findings for the chair to rule on. Neither is a blocker.

PASS is not a merge and not VERIFIED; the chair records those.

FINAL VERDICT: PASS — SHA 75e0a9510dcb92f3b7b9b880bbadb17960ffa18d
