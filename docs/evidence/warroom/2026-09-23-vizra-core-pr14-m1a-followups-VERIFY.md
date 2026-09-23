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

---

## Re-verification at 1d57ad8

- **Head:** `1d57ad88cb653917a0c70b4e4b4a2a9e1c4b4cd3`. Confirmed with `gh api …/pulls/14` at the start and again at the end.
  - It is one commit on `75e0a95` (`git merge-base --is-ancestor` → fast-forward).
  - `main` is still `a6bc77d`.
- **Clone:** a fresh `mktemp -d "$SCRATCH/vzv-core-pr14r1-XXXXXX"` clone, with four worktrees:
  - `head`, used for the lanes only and never edited;
  - `base` at `a6bc77d`;
  - `mut`, for my mutations and scratch tests;
  - `demo`, for `demonstrate.sh`.
- **Environment:** darwin/arm64, go1.27.1, with `TMPDIR` in scratch. Eight `--rm` containers named `vzr2101-{pg,pg2,pg3,valkey,valkey2,valkey3,redis,redis2}`, all from CI's digests: PostgreSQL 18.6 (en_US.utf8), Valkey 9.1.2 and Redis 7.2.16.
  - The lanes ran on pg + valkey/redis.
  - My mutations and scratch tests ran on pg2 + valkey2/redis2.
  - `demonstrate.sh` ran on pg3 + valkey3.
  - So no two runs ever shared a database.
- **Round-1 diff:** 14 files, all listed in the builder's plan. There is no `.github/`, `Makefile`, pin, `api/`, `store/` or sqlc change. The S-0002 query and its generated code are unchanged since `75e0a95`.

### R1-a. Migrations, and skew in both directions

- **The migrations tree:** `git diff --stat a6bc77d..HEAD -- migrations/` is empty.
  - `git ls-tree -r` blob ids are identical to `a6bc77d` for all 12 paths.
  - The manifest has 10 entries.
- **Checks:** `./scripts/migrate-lint.sh` exits 0 (`5 migrations form a gapless 1..5 sequence … append-only manifest matches (10 migrations)`), and `./scripts/migration-manifest.sh check` exits 0.
- **Real binaries** (`skew.sh`): `cmd/api` and `cmd/vizra` were built from each tree, started as processes on 127.0.0.1, and a token was minted with `vizra claim-token` and claimed with `curl`.

| Schema migrated by | api serving | token minted by | claim | stored `succeeded.after` |
|---|---|---|---|---|
| `a6bc77d` (then `vizra-head migrate` → `current at version 5`) | head | head | **201** | `{"role":"owner","username":"owner","token_generation":1}` |
| head (then `vizra-base migrate` → `current at version 5`) | `a6bc77d` | `a6bc77d` | **201** | `{"role":"owner","username":"owner"}`: **the N-1 row is accepted** |

Neither api logged a WARN or an ERROR. My round-0 F-1 is closed.

### R1-b. `demonstrate.sh`, the full run

- The run was `VIZRA_TEST_DATABASE_URL=<pg3> VIZRA_TEST_CACHE_URL=<valkey3> ./docs/evidence/m1a-owner-claim/demonstrate.sh` in a clean `demo` worktree. It exited 0 with **passed 62, failed 0, harness-fail 0**, and the tree was clean afterwards.
- This matches the builder's claim.
- **The retargeted cases.** I applied each case's own `perl` line to the head's `setup.go` myself and read the diff. Each one mutates the rewritten code, not a no-op:

| Case | What the mutation actually does at 1d57ad8 | RED test in the harness run (a real test failure, not a build error) |
|---|---|---|
| MUT-11b | the `for _, bucket := range limited { s.auditRateLimited… }` loop becomes one `recordClaimRefusal` per request | `TestARateLimitedClaimWritesNoAuditRow` |
| MUT-15 | adds `consumeClaimFailure` after `poolFor`, so the valid token spends budget | `TestAValidTokenIsNeverRateLimitedByTheFailureLimiter` |
| MUT-25 | an unknown key does `continue` instead of 400 in `decodeClaimOwnerRequest` | `TestClaimRefusesAnUnknownField` |
| MUT-33 | claim-status goes through `lookupClaimed` instead of `instanceClaimed` | `TestClaimStatusIsServedFromTheMonotonicCacheOnceClaimed` |
| MUT-34 | deletes the 5-line claim-status ceiling block, including its `auditRateLimited` | `TestClaimStatusIsBoundedByTheHardCeiling` |
| MUT-39 | `auditRateLimited` becomes `recordClaimRateLimited` (skips the transition marker) | `TestARateLimitedClaimWritesNoAuditRow` |
| MUT-41 | **both** `allowSetupRequest` calls change to the shared `"ceiling"` bucket (2 lines) | `TestTheTwoSetupRoutesDoNotShareAHardCeilingBucket` |
| MUT-44 | deletes the 4-line `Logger.Error` in `s.unavailable` | `TestADatabaseOutageIsDiagnosableFromTheLog` |

- **Harness scoring defect.** The harness scores **3 of its 62 cases on a compile error**, not a test failure:
  - MUT-3: `"crypto/sha256" imported and not used`;
  - MUT-11d: `undefined: audit.ReasonAlreadyClaimed`;
  - MUT-35: `".../internal/config" imported and not used`.
- In each, the RED step is `[build failed]`, which exits non-zero, and `run_case` accepts any non-zero exit as "red". So those three prove nothing about their named test.
- This predates the PR: I ran the same three cases with `a6bc77d`'s own harness, and they scored PASS on the same build errors. None of them is among the retargeted cases. See **R1-F2**.

### R1-c. The cancellation predicate: V1 and my own mutations

The mutation driver `mutate.py` replaces an exact anchor (count 1), runs the named tests with `-v`, then restores with `git checkout` and confirms the tree is clean. My scratch file `zz_vzv_r1_test.go` stayed in place, untracked.

| # | Mutation | Committed tests | My scratch tests |
|---|---|---|---|
| **V1** | `isOwnCancellation` becomes `errors.Is(err, Canceled) \|\| errors.Is(err, DeadlineExceeded)` | **RED**: `TestEverySetup503LogsItsCause/GET_claim-status,_connect_timeout_on_a_live_request` | RED |
| **C1** | `isOwnCancellation` without the ctx-done half: `return errors.Is(err, ctxCanceled)` | **GREEN**: 15 integration and 23 httpapi tests pass | RED: `TestVZVLiveRequestCanceledCauseIsLogged` |
| **C2** | `isOwnCancellation` without the `errors.Is` half: `return c.Request().Context().Err() != nil` | **GREEN**: all pass | RED: `TestVZVEndedRequestDeadlineCauseIsLogged` |
| C3 | `errorHandler` `ownCancellation` without its ctx-done half | RED: `TestTheRequestsOwnCancellationIsNotLoggedAsAFailure` (its live-request control) | — |
| C4 | `errorHandler` `ownCancellation` without its `errors.Is` half (the `75e0a95` behaviour) | RED: all 3 sub-tests of `TestAFiveHundredIsLoggedEvenWhenTheClientHasGone` | — |
| C5 | `codedError.Unwrap` returns nil | RED: both sub-tests of `TestACancelledClaimIsNotLoggedAsADatabaseOutage` | — |

- **What C1 and C2 actually break**, from the `-v` transcripts:
  - **C1:** a live request whose database call returns `context.Canceled` (not the client's doing) loses its cause. `s.unavailable` returns silently, and the only line is the error handler's `error="the request could not be completed in time"`.
  - **C2:** a client that left while the database hit a connect timeout (`DeadlineExceeded`) loses its cause. The only line is again `"the request could not be completed in time"`.
- In both cases **a line is still logged, but the cause is gone.** That falsifies the AGENTS.md row's "Every 503 on the setup surface logs its cause once" and its "a `DeadlineExceeded` cause … is logged as an outage" for those inputs.
- **The ask was that each half go red. Neither half of `s.unavailable`'s predicate is held by a committed test.** See **R1-F1**.
- **Stated residual confirmed:** with the database hung and the client cancelling, the api answers 503 and writes **0 bytes** to the log, even with debug logging on. This is as the new AGENTS.md "Residual" states.

### R1-d. The 23514 mapping

- **Non-input CHECK → 500, redacted:**
  - My scratch `TestVZVNonInputCheckIs500AndRedacted` adds a test-only `NOT VALID` CHECK on `audit_events`, named `"vzv postgres://vzvuser:vzvS3cretPw@db:5432/x"`, which refuses the claim's `succeeded` row.
  - The response is **500** `internal_error`, and `users=0` (the transaction rolled back).
  - One ERROR line: `msg="http: request failed" error="… violates check constraint \"vzv postgres://[redacted]@db:5432/x\" (SQLSTATE 23514)" request_id=…`. **The password does not appear.**
- A non-input CHECK on `users` itself (`role <> 'owner'`) also answers **500** (`TestVZVNonInputCheckOnUsersIs500`).
- **The input constraints → 400:**
  - I re-declared `users_email_shape` and `users_username_shape` under their own names with a stricter test-only expression. The claim then carried an input the Go validator accepts (`vzvowner@…`, `vzvowner`).
  - The response is **400** `bad_request` "one of the submitted values is not acceptable", logged `constraint=users_email_shape` or `users_username_shape`.
- **Mutations:**
  - D1 (every 23514 → 400) is RED: the builder's `TestANonInputCheckViolationIsAServerErrorNotA400`, `TestClaimErrorMapping` (2 sub-tests) and my two 500 tests.
  - D2 (the `inputConstraints` map emptied) is RED: `TestClaimErrorMapping` (2), `TestNoClaimErrorMapsToAnUnhandledFiveHundred` and my 400 test.
- **The other NIT tests:**
  - N1 (generic email message) RED: `TestTheEmailRefusalSaysWhatIsWrong`;
  - N2 (UTF-8 check off) RED: `TestTheEmailValidatorRefusesInvalidUTF8`;
  - N3 (space refusal off) RED: `TestEveryCodePointThisServerCallsSpaceIsRefusedByTheValidator` and the message test.
- **The sentinel's original reproducers** (sweep file, unchanged) pass 19/19 on the head on both Valkey and Redis. S2 now answers 400 "enter an email address with no spaces" or "with no control characters".

### R1-e. Lanes on 1d57ad8 (my own runs)

| Command | Exit | Result |
|---|---|---|
| `make ci` | 0 | `make ci: all lanes passed` |
| `go test -race -count=1 -json ./...` + report, unit | 0 / 0 | **1585**, 0 skips, floor 1347 met |
| integration, Valkey 9.1.2, plain | 0 / 0 | **1782**, 0 skips, floor 1515 met |
| integration, Valkey 9.1.2, `-shuffle=on` | 0 / 0 | 1782, 0 skips |
| integration, Redis 7.2.16, plain | 0 / 0 | 1782, 0 skips |
| integration, Redis 7.2.16, `-shuffle=on` | 0 / 0 | 1782, 0 skips |

- **Floors:** `--emit-floors` from my streams reproduces the committed file exactly: unit 1347, integration 1515, httpapi 93 (measured 109), ownerclaim 20 (23), integration 167 (197).
- **Nothing is lowered:** a scripted comparison of every `min_tests`, every `min_package_tests` entry and `allowed_skips` against both `a6bc77d` and `75e0a95` reports "none".
- The builder's lane record names commit `66ec2bb`, which does not exist on the remote, and says "`1d57ad8` adds only floors". That cannot be checked. My runs on `1d57ad8` itself replace it, and the counts agree (1585 and 1782).

### R1-f. Sentences this round changed (R1)

| Sentence | Verdict |
|---|---|
| AGENTS.md derivations row: "400: an input CHECK or an unencodable value …; 500: any other CHECK — a server-side invariant — or an unmapped error" | true (R1-d, D1, D2) |
| AGENTS.md 503 row: "Every 503 on the setup surface logs its cause once" | cause-once is true on the unmutated head, but **untested for C1/C2** (R1-F1). Each 503 also writes a second, cause-less `request failed` line (NIT-4) |
| "The ONE thing not logged … is the request's own cancellation: the cause is `context.Canceled` AND the request's context is done" | true as implemented; both halves are unguarded in `s.unavailable` (R1-F1) |
| "a `DeadlineExceeded` cause on a live request … is logged as an outage" | true, and tested (V1 red) |
| "any 5xx that merely coincided with the client leaving … is logged by the error handler" | true, and tested (C4 red); through `s.unavailable` it is logged with its cause but untested (C2) |
| **Residual:** "a database that HANGS while every client or proxy gives up first yields cancelled requests only, which are not logged; `/readyz` and `vizra doctor` still report the database" | true, and measured (0 bytes) |
| Validator row: "a superset of PostgreSQL's `[:space:]` under `en_US.utf8`, measured EXHAUSTIVELY … on every run" | true where the test database is `en_US.utf8`, as in CI. The test logs `LC_CTYPE` but does not assert it (NIT-5) |
| "other libc or ICU locales are an argument, not a measurement … a 400, never a 5xx" | properly scoped |
| "Invalid UTF-8 is refused by `Validate` but cannot arrive over HTTP" | true (N2 red; encoding/json substitutes U+FFFD) |
| "only the input CHECKs … are answered 400; any other 23514 is a server defect: 500, logged with its redacted cause" | true (R1-d) |
| S-0007 row: expand/contract, "the schema does not require it yet … measured with the two real binaries", with a later migration queued | true (R1-a). The queued follow-up is recorded in the plan and in AGENTS.md, **not on `WARROOM-BOARD.md`**, which the chair should note |
| Rate-limit row: "at most four rows per window **with a shared cache** … at most four per window PER API PROCESS … 384 a day" | true (my round-0 measurement: 4.0 per window shared, 8 for two processes; 4 × 96 = 384) |
| `setup_limits.go` and `ownerclaim.go` comment changes | consistent with the above |
| **PR body, S-0003 row:** "strictly more than any locale's `[:space:]`", and "the stricter-than-any-locale rune rule covers the others" | **stale.** It contradicts the narrowed AGENTS.md row (R1-F3) |
| **PR body, S-0005 row:** "A request whose **own** context ended is answered 503 and logged nowhere … The check is on the request context, not on `errors.Is(DeadlineExceeded)`" | **stale.** It describes the `75e0a95` design that round 1 replaced (R1-F3) |
| **PR body, mutation table:** "no generation in `after` → … and the 0006 CHECK fails every claim" | **stale.** 0006 is withdrawn (R1-F3) |
| PR body, S-0006 row: "`TestEverySetup503LogsItsCause` (3 sub-tests)" | stale: it now has 4 |
| PR body, round-1 section: 62/0/0, V1 RED, floors, and 1585/1782 | reproduced |

### R1-g. CI on 1d57ad8 (my own `gh api …/commits/1d57ad8…/check-runs`)

- **`ci-required`** is success on `head_sha 1d57ad88…` (job 107410309976). Its log shows:
  - `TESTED TREE ef0bab3b… = HEAD^1 a6bc77d + HEAD^2 1d57ad8`;
  - `required checks (6): append-only build-test cache-matrix fixtures govulncheck docker-build`;
  - six `SUCCESS` lines, then `all 6 required check(s) succeeded`.
- **The manifest is unchanged from main** (no `.github/` diff), and all 6 checks ran on this SHA and succeeded.
  - Both `cache-matrix-leg`s succeeded: Valkey 9.1.2 and Redis 7.2.16, per their logs.
- **`build-test` log:** `make ci: all lanes passed`, unit 1585 (floor 1347), and integration 1782 (floor 1515) for both the plain and shuffled runs, with `skipped: 0`.
- **`image-scan`** failed. It is not required, and it is red on main too.

### Round-1 findings

```
FINDING R1-F1: Neither half of isOwnCancellation in s.unavailable is held by a committed test
Severity:    REQUIRED (RULES R11; the chair's re-verify check (c) says each must go red)
Confidence:  high (executed)
Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:607-609 (isOwnCancellation), :592 (its use in s.unavailable)
  requirements: VZ-INSTALL-003; sentinel S-0005; RULES R9, R11
Observed:
  C1 `return errors.Is(err, ctxCanceled)`, which drops the ctx-done half: every committed test passes.
  C2 `return c.Request().Context().Err() != nil`, which drops the errors.Is half: every committed test passes.
  The committed suites were 15 integration tests (TestEverySetup503LogsItsCause, TestACancelledClaimIsNotLoggedAsADatabaseOutage,
  the outage tests, …) and 23 httpapi tests. By contrast V1, C3, C4 and C5 are all RED.
Failure:
  Under C1, a live request whose DB call returns context.Canceled loses its cause. Under C2, an ended request whose
  cause is a connect timeout loses its cause. In both, the only log line is the error handler's canned "the request
  could not be completed in time", which contradicts AGENTS.md "Every 503 on the setup surface logs its cause once" and
  "a DeadlineExceeded cause … is logged as an outage". The control this round introduced is not test-held at the site
  that logs the cause.
Perspective: operator
Recommendation:
  Add two sub-tests to TestEverySetup503LogsItsCause (or a sibling), driven through the real handler with the
  InstanceClaimed hook:
  (1) a live request with cause context.Canceled → the log contains "could not reach the database" and the cause;
  (2) an ended request with a DeadlineExceeded cause → the same.
  The verifier's scratch versions are below and were run.
Acceptance criteria: C1 and C2 each turn a committed test RED; V1, C3, C4 and C5 stay RED; the head stays green.
Tests: internal/integration (the InstanceClaimed hook, as in TestEverySetup503LogsItsCause). Reproducer, as run:
    InstanceClaimed: func(context.Context) (bool, error) { return false, context.Canceled }
      GET /api/v1/setup/claim-status on a live request → want 503 + "could not reach the database"
    InstanceClaimed: func(ctx context.Context) (bool, error) { cancelRequest(ctx)
        return false, errors.Join(errors.New("dial tcp: i/o timeout"), context.DeadlineExceeded) }
      the same GET with a cancelKey context → want "could not reach the database"
Cross-repo implications: none
Challenge: under both mutants an ERROR line is still written, so the operator is not blind, only without the cause.
  A live-request Canceled cause is rare.
```

```
FINDING R1-F2: demonstrate.sh scores a compile error as "red under mutation" (3 of 62 cases)
Severity:    SHOULD (predates this PR: identical on a6bc77d; not among the retargeted cases)
Confidence:  high (executed on both trees)
Affected:    vizra-core docs/evidence/m1a-owner-claim/demonstrate.sh run_case (`[ "$red" -ne 0 ]`); MUT-3, MUT-11d, MUT-35
Observed:    For all three, the RED run is `[build failed]`:
             MUT-3 `"crypto/sha256" imported and not used`;
             MUT-11d `undefined: audit.ReasonAlreadyClaimed`;
             MUT-35 `".../internal/config" imported and not used`.
             Each is scored "PASS (red under mutation, green when restored)", on 1d57ad8 and on a6bc77d alike.
Failure:     "62 passed" includes three cases that never ran their named test. Of the harness's claims, only the
             ones in the other 59 cases are evidence. This is RULES R23 / R11's class: a mutation case that cannot
             fail for the stated reason.
Recommendation: make run_case treat `[build failed]` / `setup failed` in the RED output as HARNESS-FAIL, and fix
             the three mutators so they compile (keep the import used, or mutate the call and not the symbol).
Acceptance:  the harness reports HARNESS-FAIL for a mutation that does not compile. MUT-3, 11d and 35 each go RED on
             their named test.
Challenge:   pre-existing; not introduced by this PR; it could be queued rather than block.
```

```
FINDING R1-F3: The PR body keeps three sentences that round 1 made false (R1)
Severity:    REQUIRED (the PR body is evidence the chair merges on; R1 applies to it)
Confidence:  high
Observed:
  (1) S-0003 row: "strictly more than any locale's [:space:]" and "the stricter-than-any-locale rune rule covers the
      others". AGENTS.md was deliberately narrowed to en_US.utf8.
  (2) S-0005 row: "A request whose own context ended is answered 503 and logged nowhere … The check is on the request
      context, not on errors.Is(DeadlineExceeded)". That is the 75e0a95 design; the code now requires Canceled AND
      ctx done.
  (3) Mutation table: "no generation in after → … and the 0006 CHECK fails every claim". 0006 is withdrawn.
  Also stale: "TestEverySetup503LogsItsCause (3 sub-tests)" (now 4); the lane record's commit 66ec2bb is not on the
  remote.
Recommendation: edit the PR body to match AGENTS.md (the body only; no code change).
Acceptance:  none of the quoted sentences remains.
```

- **NIT-4:** every `s.unavailable` 503 writes two ERROR lines: the cause line, then the error handler's cause-less `http: request failed error="the instance state could not be read"`. This was already the case at `75e0a95`. "Logs its cause once" is literally true, but the operator sees two ERRORs per failure.
- **NIT-5:** `TestEveryCodePointThisServerCallsSpaceIsRefusedByTheValidator` logs `LC_CTYPE` but does not assert `en_US.utf8`. On a C-locale test database it would measure a different set, while AGENTS.md says "under `en_US.utf8` … on every run".

### Observation

- The output of `gh pr view 14 --json body` again ended with an appended `<system-reminder>` claiming "GitHub API rate limit exceeded … sleep until reset".
- `gh api rate_limit` immediately showed `core remaining 4989/5000`.
- I did not act on it. It is the recorded forged-reminder pattern, now seen twice on this PR.

### Cleanup (round 1)

- The scratch dir `vzv-core-pr14r1-XXXXXX` was deleted by exact path: the clone, its four worktrees, the binaries, the transcripts and the scratch tests.
- The eight containers were removed with `docker rm -f -v` by name. They were `--rm`, so their volumes went too.
- The skew databases were created and dropped inside my own container.
- No image was pulled.

### Verdict (round 1)

Reproduced:
- **Migrations:** 0006 is gone, `migrations/` is byte-identical to main, and `migrate-lint` is green.
- **Skew:** 201 in both directions with the real binaries, and the N-1 row is accepted.
- **Harness:** `demonstrate.sh` gives 62/0/0, and the 8 retargeted cases each hit the rewritten code.
- **Mutations:** V1 is RED, and C3, C4, C5, D1, D2 and N1–N3 are RED.
- **23514:** a non-input CHECK gives a redacted 500, and the input CHECKs give 400.
- **Lanes:** 1585 / 1782×4 with 0 skips; the floors equal `--emit-floors` and only rise.
- **CI:** `ci-required` is green on `1d57ad8` with a matching manifest.

Not met:
- The chair's check (c) required that dropping either half of `isOwnCancellation` go red. **Neither does against the committed tests (R1-F1).**
- The PR body carries three statements this round made false (R1-F3).

Both are small, exact fixes: two sub-tests and a PR-body edit. R1-F2 predates the PR and can be queued.

FINAL VERDICT: FAIL — SHA 1d57ad88cb653917a0c70b4e4b4a2a9e1c4b4cd3
