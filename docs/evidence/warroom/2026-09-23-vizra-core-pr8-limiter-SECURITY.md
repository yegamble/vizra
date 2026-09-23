# vizra-core PR #8: security-seat review of the fixed-window rate limiter (verifier R4-A)

- **Date:** 2026-09-23
- **Seat:** `vizra-security`
- **Head reviewed:** `385fc51245f34cf8a04ea069c8c3769f7bda5c66`. The worktree `.claude/worktrees/core-m1-owner-claim` was at this SHA and clean before and after the review.
- **Change under review:** `085d78b`, `fix(cache): make the rate limiter a true fixed window`. Product code changed only in `internal/cache/ratelimit.go` (`FallbackLimiter.Allow`: `INCR` + `EXPIRE key window NX` in one `TxPipeline`) and a comment in `internal/httpapi/setup_limits.go`. It also adds `internal/integration/ratelimit_test.go`, rows in `AGENTS.md`, and raised floors in `scripts/test-floors.json`. Every floor change is a raise: `cmd/vizra` 8→10, `internal/config` 82→86, `internal/httpapi` 26→48, `internal/integration` 40→144.
- **Method:** read-only code review, plus measurements against my own scratch containers (`vzsec-r62` redis:6.2.24, `vzsec-r72` redis:7.2.16, `vzsec-vk` valkey 9.1.2). I built no exploit payloads. My measurement test was injected with `go test -overlay`, so no file in the worktree was written. All containers, both pulled images and the scratch directory were removed afterwards.

## Evidence taken

**E1: raw server behaviour, `MULTI / INCR k / EXPIRE k 900 NX / EXEC`**

| Server | Fresh key | Existing key with no TTL (`SET j 700` first) | Second call, `EXPIRE k 5 NX` over a live TTL |
|---|---|---|---|
| redis 6.2.24 | `ERR wrong number of arguments for 'expire'` at queue time, then `EXECABORT`. `EXISTS k` = 0, so **nothing was applied** | `EXECABORT`; `j` untouched | `EXECABORT` |
| redis 7.2.16 | `1`, `1`; TTL 900 | `701`, `1`; **TTL 900** (healed) | `2`, `0`; TTL still 900 (**not moved**) |
| valkey 9.1.2 | same as 7.2 | same as 7.2 | same as 7.2 |

**E2: the builder's four new integration tests**, run with `VIZRA_TEST_CACHE_URL=<scratch> go test -tags=integration -count=1 -race -run 'TestTheCache' -v ./internal/integration/`. All four passed on both redis 7.2.16 and valkey 9.1.2 (`ok … 18.161s` and `ok … 18.301s`):
- `TestTheCacheLimiterDoesNotRefreshTheTTLWithinTheWindow`
- `TestTheCacheLimiterReopensWhenTheWindowRolls`
- `TestTheCacheLimiterGivesATTLToAKeyFoundWithoutOne`
- `TestTheCacheAndFallbackLimitersAgreeOnFixedWindowSemantics`

**E3: overlay measurements through the real `cache.FallbackLimiter`**

| Probe | Result |
|---|---|
| M1: call with an already-cancelled request context | `allowed=true degraded=true`; the next healthy call gives `degraded=false` |
| M2: Redis 6.2, limit 5, 8 calls | `allowed=5/8 degraded=true key_exists=0`. Every call fell back to the in-process counter, and no counter key was created in Redis |
| M3: limit 60, window 2 s, burst, wait for the roll, burst again | accepted 60 then 60, across a 2.061 s span |
| M4: count reaches the limit on the cache path, then the cache client is closed | cache path refused the 6th call; the fallback then allowed **5 more** (`degraded=true`) |

## 1. Is the fixed window correct, atomic and crash-safe? Yes.

**No path can leave a key without a TTL that the limiter then consults. So a permanent lockout is not reachable.**
- On Redis/Valkey ≥ 7.0 every successful call runs `EXPIRE … NX` in the same `EXEC` as the `INCR`. A key found with no TTL gets one on its next call (E1, E2 `…GivesATTLToAKeyFoundWithoutOne`). A key never called again is never consulted, so it cannot lock anything.
- On a server that rejects `NX`, the whole transaction aborts at queue time, so `INCR` is not applied either (E1, redis 6.2: `EXECABORT`, `EXISTS`=0). `Exec` returns an error, so every decision comes from the in-process fixed window (E3 M2).
- A hypothetical RESP server that accepted the arity but rejected `NX` at run time would apply the `INCR` without a TTL. But `Exec` would still return the per-command error, so the decision comes from the fallback and the TTL-less key is never read.
- **Client retry.** A go-redis retry after a lost `EXEC` reply can at most double-count, which is conservative. Each attempt is a complete MULTI carrying its own `EXPIRE NX`, so a retry cannot drop the TTL. *UNVERIFIED by measurement* (reasoned from the transaction shape).
- **Failover.** The two commands propagate as one `EXEC` block. Asynchronous replication can lose the last few increments on promotion, a small bounded budget gain, but it cannot produce a TTL-less key; and even if it did, the next call heals it. *UNVERIFIED by measurement.*
- **Resetting or extending a window.** No code path extends one: `EXPIRE NX` never moves a live TTL (E1 column 3; E2 `…DoesNotRefreshTheTTLWithinTheWindow`). Only the operator's cache configuration can reset one early: a `maxmemory-policy` that evicts volatile keys under memory pressure, or a wall-clock step on the cache host. An attacker cannot drive either (see §4 on memory). *Not a finding.*
- **TTL edges.** Every caller uses `claimRateWindow = 15 * time.Minute` (`internal/httpapi/setup.go:33`), so go-redis's whole-second rounding in `ExpireNX` never applies.

## 2. Does the fixed window create a new attack? No: the token-guessing bound is irrelevant against the entropy.

The fixed window admits up to 2 × limit in a short span across a boundary (E3 M3: 60 + 60 in 2.06 s).

The claim token is `TokenBytes = 32`, i.e. **256 bits**. It is presented as 64 lowercase hex characters (`internal/ownerclaim/ownerclaim.go:58-64`), is single use, and has a 1 h TTL (`VIZRA_OWNER_CLAIM_TTL` default). Against it:

| Budget | Boundary burst | Sustained per day | Chance per day against 2^256 |
|---|---|---|---|
| Global failure budget, 60 / 15 min (`setup.go:35`) | 120 | 5,760 | ≈ 2^-243 |
| Claim-owner hard ceiling, 600 / 15 min (every request, not just failures) | 1,200 | 57,600 | ≈ 2^-240 |

The failure budget was never the entropy defence. It bounds audit-row volume and log noise, and it still does: at most 60 `refused` rows per window, only while the instance is unclaimed. Per-process fallback × N replicas changes none of these orders of magnitude.

## 3. Is the semantic change safe for every caller and bucket? Yes.

| Bucket (`internal/httpapi/setup_limits.go`, `setup.go`) | Limit / 15 min | Effect of fixed versus sliding | Verdict |
|---|---|---|---|
| `ceiling.claim` | 600 | A lockout now ends at most 15 min after the window opened. The operator's own retries no longer extend it. | Safe; strictly better. Residual in L-1. |
| `ceiling.status` | 3000 | Same | Safe; residual in L-1 |
| Per-origin failure budget | 10 | 2× at a boundary; charged only on the unclaimed 403 | Safe (§2) |
| Global failure budget | 60 | Same | Safe (§2) |
| `audited` transition | 1 | **Now truly one `rate_limited` row per 15-minute window.** Under the sliding expiry, a continuous flood kept this key alive, so the whole attack produced a single row, which under-reported it. Now a sustained flood writes at most 96 rows a day, and only while unclaimed, because `refuseToken` is reachable only via `classifyRefusal` → still unclaimed. | Safe; matches ruling S-5 |

A valid token is still never checked against the failure budgets. `refuseToken` is the only charging path.

## 4. Cache down (in-process fallback) versus cache up

- **Consistent semantics.** Both are fixed windows that start at the first request. The builder's `TestTheCacheAndFallbackLimitersAgreeOnFixedWindowSemantics` runs one script through both and passed on both images (E2).
- **Stated weakenings.** The fallback is per process, so N replicas allow N × limit. Switching to the fallback also starts from a **fresh in-process count** (E3 M4: 5 more after the cache path had refused). The first is in the `Limiter` doc comment; the second is not written anywhere. Both are surfaced by readiness (`probes.go:185-188`, "rate limiting is running on the in-process fallback"). `vizra doctor` also FAILs a cache below the 7.2 floor (`internal/doctor/doctor.go:152-160`), which catches the redis-6.2 "permanently on fallback" case.
- **Can an attacker force the fallback to gain budget? No.** The fallback engages only when `Exec` errors.
  - The attacker cannot make the cache OOM or fail. Cache keys at M1-A are only the limiter's: four fixed keys, plus one per-origin key per /24 or /64 that submits a *failure*, which is capped by the claim ceiling at ≤ 600 new keys per window.
  - The one attacker-reachable way to make `Exec` error is to disconnect mid-request. That cancels the request context (E3 M1), and the resulting fallback "allow" goes to a request that is already dead: its database calls fail on the same context. No budget is gained. The side effect is a transient false `degraded` on readiness; see L-2.

## 5. The residual statement

`AGENTS.md` (the "hard ceiling" row) says: "an attacker who sends **600 claim-owner requests in every 15-minute window** (about 0.67 per second, sustained) holds claim-owner closed to everyone, the operator included, for as long as they keep it up."

That is **accurate**. It is **not complete enough for the owner to accept as written**; see L-1.

---

## Findings

### L-1 — The ceiling residual is accurate but incomplete, and needs an owner-inbox entry and an operator recovery line before release

- **Severity:** REQUIRED. Not merge-blocking: this commit makes the behaviour strictly better. It is release-blocking until the owner has decided.
- **Confidence:** high
- **Where:** `AGENTS.md` (hard-ceiling row); `internal/httpapi/setup_limits.go:67-78`; `internal/httpapi/setup.go:51,56`
- **Evidence:** §1 and §3; E3 M3 shows the window arithmetic the attacker relies on. The route has no in-product bypass. A restart does not help, because the counter lives in Valkey. The only exits are network-level or a manual key delete.
- **What the statement omits:**
  1. **Scale and targeting.** It is anonymous, costs about 0.67 requests per second per instance, and is scanner-scale. `GET /api/v1/setup/claim-status` returns `claimed:false`, which tells the attacker exactly which instances to hold.
  2. **The operator's window is effectively zero.** The attacker does not need an even 0.67/s. They poll; the first non-429 marks a new window, which they fill at once. The operator's valid token is admitted only if it lands in the gap between the window rolling and the attacker's burst.
  3. **Claim-status has the same shape at 3000 / 15 min (about 3.3/s).** Holding it closed breaks the claim page's form-versus-already-claimed choice. The "accepted residual" sentence names only claim-owner.
  4. **Recovery is not documented.** Restarting the api does nothing. What works:
     - put the listener behind a firewall or allowlist during first-run setup; or
     - delete the counter: `valkey-cli DEL '<ns>:rl:<ns>:rl:setup.claim:ceiling.claim'` (with the default namespace, `default:rl:default:rl:setup.claim:ceiling.claim`), then claim at once.
  5. **The fresh budget on a switch to the fallback** (§4) is not stated.
- **Recommendation:**
  - Record an owner-inbox entry: "first-run claim can be held closed indefinitely by an anonymous party at ~0.67 req/s until M1-B's concurrency bound; recovery = firewall during setup or `DEL` the ceiling key". Accepting availability risk on the headline install path is the owner's decision, like the restart-re-mint deviation.
  - Add the recovery line to the README "Claiming a new instance" section and to `vizra doctor`'s unclaimed WARN detail.
  - Extend the `AGENTS.md` residual sentence with points 1 to 3 and 5.
  - Optionally, in M1-B, give the operator an exec-level path that does not depend on the public route's budget (the same trust level as `vizra claim-token`). That is a new CLI surface, so it is the owner's call.
- **Acceptance:** an owner-inbox row exists and is dated. The README and the doctor WARN name the recovery. The `AGENTS.md` residual names the status route, the targeting and the fallback reset.
- **Tests:** documentation; no code test. Doctor's detail string is covered by the existing doctor verdict tests once it changes.

### L-2 — A cancelled request context flips the limiter to "degraded" and is decided by the fallback

- **Severity:** NIT
- **Confidence:** high (measured, E3 M1)
- **Where:** `internal/cache/ratelimit.go` `FallbackLimiter.Allow`: any `Exec` error, including `context.Canceled`, runs `setDegraded(true)` and `fallback.Allow`.
- **Evidence:** a call with a cancelled context gave `allowed=true degraded=true`; the next healthy call gave `degraded=false`. A client that disconnects mid-request therefore flips `/readyz` to degraded ("rate limiting is running on the in-process fallback") until the next healthy call. It also increments an in-process counter for a request that is already dead.
- **Impact:** readiness noise only. Degraded is still HTTP 200, and no budget is gained (§4). It does make the degraded signal less trustworthy for an operator.
- **Recommendation:** at the top of `Allow`, `if ctx.Err() != nil { return false, 0 }`, without touching `degraded` or the fallback. Treat only cache errors as cache errors.
- **Tests:** a unit test with a cancelled context asserting `Degraded()` is unchanged.

### L-3 — Switching to the fallback grants a fresh per-process budget, and that is not written down

- **Severity:** NIT
- **Confidence:** high (measured, E3 M4)
- **Where:** `internal/cache/ratelimit.go` (the `Limiter` doc comment states "N replicas allow N times the limit", but not the reset at the moment of the switch)
- **Evidence:** the cache path refused the 6th call at limit 5; after the cache client was closed, the fallback allowed 5 more.
- **Impact:** at most one extra window of budget per process, per cache outage. An attacker cannot force it (§4). Readiness already reports it.
- **Recommendation:** one sentence in the doc comment and in the L-1 residual text. No code change.

## Answers in one line each

1. **Correct, atomic, crash-safe?** Yes. No reachable TTL-less key, and no path extends or resets a window (E1, E2, E3 M2).
2. **New attack from the fixed window?** A 2× boundary burst exists (E3 M3), but it is irrelevant against a 256-bit, single-use, 1 h token (`TokenBytes = 32`).
3. **Every bucket safe?** Yes, including `audited`, which now correctly writes one row per window instead of one per whole flood.
4. **Fallback consistent, and can it be forced for budget?** Consistent. It cannot be forced for budget; only the transient readiness flip in L-2 is reachable.
5. **Residual complete?** Accurate but incomplete. It needs an owner-inbox entry and a documented recovery (L-1).

SEAT VERDICT: NO BLOCKER — SHA 385fc51245f34cf8a04ea069c8c3769f7bda5c66
