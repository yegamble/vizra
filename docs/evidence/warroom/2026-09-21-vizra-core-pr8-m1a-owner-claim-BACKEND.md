# vizra-core PR #8 (M1-A owner claim, VZ-INSTALL-003) — CODE review by the `vizra-core` backend seat, with the chair's consolidated ruling

- **PR:** yegamble/vizra-core#8, branch `feat/m1-owner-claim`
- **Reviewed SHA:** `32b616dcd6d9ed3ea8d05020e1d66dae25c0e8ed`
- **Reviewer:** `vizra-core` council seat (agent `aec2b3f79317ff17c`, the same seat that reviewed the plan), read-only; could not re-run live DDL probes this round (stated in its header)
- **Date:** 2026-09-21
- **Kind:** specialist review of the code against the chair's plan rulings. Not a verifier verdict. The security seat's code review is `2026-09-21-vizra-core-pr8-m1a-owner-claim-SECURITY.md`.

## Chair ruling on both seats' code reviews (2026-09-21, tick 105)

**PR #8 is HELD: seven blocking specialist findings are open** (backend F1–F6; security N-1, which is the same defect as backend F3). Both seats call the implementation faithful and unusually complete; none of the findings changes the schema's shape. Fix round 1 of 2, consolidated with the verifier's verdict when it arrives:

1. **F3 / N-1** — no per-request `already_claimed` audit row: refuse from the monotonic claimed cache before touching the pool (the in-transaction `AnyUserExists` stays the authoritative gate) and DROP the row (a refusal on a permanently closed endpoint is not a security event). Test + mutation.
2. **F4 + N-4** — restructure `Claim`: read phase with no transaction (`AnyUserExists` → token row → constant-time compare → **liveness pre-check** → hash), then one explicit READ COMMITTED transaction containing only the authoritative gate, `ClaimOwner` and the audit insert. No connection is held while hashing; a correct-but-dead token costs zero derivations. Tests + mutations (MUT-29, liveness pre-check).
3. **F2 / N-5** — the live-token decision moves INSIDE the advisory lock (`onlyIfNoLiveToken`); concurrent boots in `stderr` mode leave one token at generation 1 and exactly one printed credential. The chair's ruling row 2 described this behaviour, so it is blocking, as the backend seat rates it. While `Mint` is open: **N-6 / F-2** — `MintOwnerClaimToken` gains `WHERE NOT EXISTS (SELECT 1 FROM users)` so "never mint on a claimed instance" is a property of the statement (query-level, no schema change); **F-3** — delete the dead supersede call or emit the `superseded` audit row for the generation a re-mint kills.
4. **F1** — an infrastructure sentinel (`ErrUnavailable`) mapped to 503 `unavailable`; every status the OpenAPI operation declares is produced by a test and none it does not declare is reachable; an integration test with a stated mechanism for the downed database.
5. **F5** — evidence integrity: the clock test asserts `minted_at = expires_at - ttl` (one statement's `now()`), with a mutation stamping from the application clock; the out-of-band-owner test is renamed to what it proves OR made to fire `users_one_owner` through the `Deps.InstanceClaimed` seam; every mutation id cited in a transcript exists in the harness (MUT-17).
6. **F6, F-5, F-6** — frozen text, so it lands now: the down file states that re-applying 0005 fails 23503 on any database that recorded a user-actor audit event and that the supported recovery is restore; the up header records the ASCII-only username as a DECISION (homograph risk; `display_name` carries Unicode identity) and the `DROP EXPRESSION` escape for the generated fold columns. No change to the up file's DDL.
7. **N-2 / R-A** — `claim-status` served from the monotonic cache and under the hard ceiling; the comment that claimed otherwise corrected. **N-3** — origins compared NORMALISED (scheme and host lowercased, default port elided, trailing slash and trailing dot stripped, IDN in A-label form), normalised once at config load; the `vizra doctor` origin check the plan ruling named; consider refusing a trailing slash at boot.
8. **N-7** (pre-existing: the HTTP error handler logs `err.Error()` unredacted; no redaction-coverage test for `internal/httpapi`) → core hardening sweep, not this PR.
9. Accepted as built: `Content-Type` with a `charset` parameter (the security seat worked the parser adversarially and would keep it); in-place token overwrite rather than row-per-mint (the backend seat's four reasons; the unreachable `superseded_at IS NULL` predicate stays as defence in depth); `415 → unsupported_media_type` added to `httpCodeName` beyond the ruling's "409 only".

The seat's report follows verbatim.

---

# Code review at 32b616d — `vizra-core` PR #8 (M1-A owner claim, VZ-INSTALL-003)

**Reviewer:** `vizra-core` backend seat · **Date:** 2026-09-21
**Tree:** `/Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim`, HEAD `32b616dcd6d9ed3ea8d05020e1d66dae25c0e8ed`, `git status --porcelain` empty, one commit on `5eb2829`.
**Scope:** schema, queries, transaction design, contract correctness. Test *reproduction* belongs to the verifier; I judge whether the tests *can* fail.

**UNVERIFIED this round:** I could not re-run live DDL probes. The only reachable PostgreSQL 18 is the verifier's `vzv8-pg` on `:55811`, which requires a password I do not have, and I will not start a container. My earlier probes on PostgreSQL 18.6 already established the load-bearing semantics used below (generated `lower()` fold columns + partial unique index; `ALTER TYPE … ADD VALUE … BEFORE` accepted in a transaction with `55P04` on same-transaction use; enum sort order; single-statement owner swap against a partial unique index). Migration application and the suite on PG 18.6 are the verifier's to reproduce against `docs/evidence/m1a-owner-claim/01-integration-pg18.txt`.

---

## Status of B-1…B-6 and B-R1…B-R12

| ID | Status | Evidence |
|---|---|---|
| **B-1** live-owner predicate | **CLOSED** | `migrations/0005_users_credentials_owner_claim.up.sql:97-98` `WHERE role = 'owner' AND tombstoned_at IS NULL`; `internal/integration/owner_claim_test.go:382,401`; MUT-2, MUT-2b (`docs/evidence/m1a-owner-claim/demonstrate.sh:137,141`) |
| **B-2** RESTRICT + trigger deadlock | **CLOSED as ruled** | header `0005…up.sql:28-45` carries all four dictated sentences incl. the `CREATE OR REPLACE FUNCTION` escape; FK `:165-167`; triggers `:177-191`; tests `owner_claim_test.go:546,565,579`; MUT-9, MUT-9b, MUT-19 |
| **B-2.1** drop `consumed_by` | **CLOSED** | `0005…up.sql:132-159` — no `consumed_by`, no pair CHECK |
| **B-3** spec/DDL byte-vs-rune, no 5xx | **CLOSED** | Go byte bound `internal/ownerclaim/ownerclaim.go:76,142`; `TestValidatorsMatchTheMigration` reads the migration's bytes (`ownerclaim_test.go:34`); spec `api/openapi.yaml` `email: maxLength: 254` + "At most 254 BYTES"; 23514→400 backstop `internal/httpapi/setup.go:382-389`; `owner_claim_test.go:980` |
| **B-4** explicit READ COMMITTED | **CLOSED** | `ownerclaim.go:300`; `TestOwnerClaimRaceYieldsExactlyOneOwnerUnderEveryServerDefaultIsolation` (`owner_claim_test.go:285`, 32 claimants × 3 server defaults); MUT-16 |
| **B-5** boot minting | **PARTIAL** | default `off`, generation in every line, doctor check, degraded-not-fatal all present (`internal/ownerclaim/announce.go`, `cmd/api/main.go`, `internal/httpapi/probes.go:166-175`). **The live-token check is outside the advisory lock** → FINDING 2 |
| **B-6** bound the anonymous writer | **PARTIAL** | 429 writes nothing and the transition row is budgeted (`setup_limits.go:101-145`, `owner_claim_test.go:1152`, MUT-11b). **`already_claimed` is unbounded on every claimed instance** → FINDING 3 |
| **B-R1** generated folds | **CLOSED** | `0005…up.sql:57,59`; absent from the INSERT list (`store/queries/owner_claim.sql:82`); `owner_claim_test.go:1359` |
| **B-R2** partial email index | **CLOSED** | `0005…up.sql:85` |
| **B-R3** enum / text+CHECK split | **CLOSED** | `0005…up.sql:52` enum, `:117` `credentials_kind` text CHECK; `TestUserRoleEnumOrderMatchesAuthzRanking` (`owner_claim_test.go:516`) |
| **B-R4** complete error map | **PARTIAL** | `TestClaimErrorMapping` (`setup_test.go:131`) covers 23505×3, 23514, `ErrAlreadyClaimed`, `ErrBusy`. **Infrastructure failures fall through to 500** → FINDING 1. **The integration half is mislabelled** → FINDING 5 |
| **B-R5** normalise → shape → compare | **CLOSED** | `ownerclaim.go:112,134-137`; `ownerclaim_test.go:58,85`; `owner_claim_test.go:794` |
| **B-R6** `credentials` scope + bound | **CLOSED** | `0005…up.sql:100-108,123-127` |
| **B-R7** advisory-lock literal + registry | **CLOSED** | `ownerclaim.go:43-54` — no `hashtext()` |
| **B-R8** PG 18 evidence, no `uuidv7()` | **PARTIAL / UNVERIFIED** | ids Go-minted (`ownerclaim.go:337,341`), no `uuidv7()` in the tree. The PG 18.6 transcript exists; I could not re-run it (see header) |
| **B-R9** structural guard + route walk | **CLOSED** | `internal/httpapi/server.go` `e.Use(s.requireClaimedMiddleware())`; `setup.go:100-142`; `setup_test.go:27,51`; `owner_claim_test.go:1325`; MUT-12, MUT-27 |
| **B-R10** `/api/v1` group, probes unprefixed | **CLOSED** | `server.go` group registration with the stated reason |
| **B-R11** explicit casts, typed sqlc params | **CLOSED** | `store/queries/owner_claim.sql:75-95`; `internal/store/sqlcgen/owner_claim.sql.go:72-79` — `ClaimOwnerParams` is `[]byte`/`uuid.UUID`/`string` throughout, **no `interface{}`** |
| **B-R12** one explicit transaction | **PARTIAL** | One explicit tx, "implicit transaction" prose gone. **argon2id runs inside it** → FINDING 4 |

---

## The two questions the chair asked me to decide

### In-place overwrite vs row-per-mint — **KEEP IN-PLACE.** It freezes correctly.

`MintOwnerClaimToken` (`store/queries/owner_claim.sql:38-47`) upserts the singleton row, bumping `generation` and clearing both terminal columns.

1. **The singleton PK makes "at most one owner-creating credential exists, ever" a schema fact.** Row-per-mint replaces that with an application-maintained predicate — "which rows are still redeemable" — which is precisely the class of invariant `AGENTS.md` requires to be a database constraint. One missed `superseded_at` write in a future slice would leave two live credentials with nothing to catch it.
2. **Invalidation is atomic and total.** The old digest ceases to exist at commit. Row-per-mint retains a second copy of a credential verifier at rest forever, for no operational benefit.
3. **The concurrent-redeem window is already correct.** A redeemer reads the old digest, hashes, then the redeem CTE matches `token_sha256 = <old digest>` against the *committed* row under READ COMMITTED. Mint-first → zero rows → 403. That is right.
4. **Audit is sufficient without it.** `generation` is monotonic and `setup.owner_claim.minted` carries it, so the mint history exists with zero secret material. (But see FOLLOW-UP F-3: a CLI re-mint currently emits no `superseded` row for the generation it killed.)

**Keep the unreachable `superseded_at IS NULL` predicate.** The builder is right that it is dead today — the only writer of `superseded_at` is `SupersedeLive`, which boot calls only when `AnyUserExists` is already true, in which state `Claim` returns `ErrAlreadyClaimed` before reading the token. It costs one predicate and becomes live the moment a slice supersedes without minting on an unclaimed instance. Record it in the query comment as defence-in-depth, which it nearly does.

**One hardening the in-place design should take, query-level, no schema change** (see FOLLOW-UP F-2): the resurrection property of `ON CONFLICT DO UPDATE … consumed_at = NULL` currently depends on a preceding read (`Mint(refuseIfUsersExist=true)`, `announce.go:59`). The claim transaction does not take the mint advisory lock, so a CLI mint that reads `AnyUserExists=false` immediately before a claim commits can land a live token on a just-claimed instance. Not exploitable — `Claim`'s gate refuses it, and the next boot supersedes it — but it contradicts the invariant the code states. Make it a property of the statement:

```sql
-- name: MintOwnerClaimToken :one
INSERT INTO owner_claim_tokens (id, token_sha256, generation, expires_at)
SELECT true, sqlc.arg('token_sha256')::bytea, 1, now() + sqlc.arg('ttl')::interval
 WHERE NOT EXISTS (SELECT 1 FROM users)
ON CONFLICT (id) DO UPDATE ...
```

Zero rows → `pgx.ErrNoRows` → the CLI's existing `ErrHasUsers` message.

### Can a second owner reach the claim path after a tombstone? — **No. Confirmed in SQL, inside the transaction.**

`ownerclaim.go:309` calls `q.AnyUserExists(ctx)` on the transaction's `Queries`, before the token row is read, and the SQL is `SELECT EXISTS (SELECT 1 FROM users)` (`store/queries/owner_claim.sql:12`) — **not** the index. Tombstoning sets `tombstoned_at`; it deletes nothing, and the row cannot be deleted (`audit_events_actor_user_fk … ON DELETE RESTRICT`). So `AnyUserExists` is monotonic-true and every later claim gets `ErrAlreadyClaimed` → 409 before any token examination. A stale token does not help: it is never read. The CLI refuses (`cmd/vizra/claimtoken.go`, `Mint(…, true)` → `ErrHasUsers`, `owner_claim_test.go:779`). Boot with users present supersedes and never mints (`announce.go:63-72`, `owner_claim_test.go:755`). **My tombstone predicate opens no hole**, exactly because the index is not the gate.

One consequence M1-B must inherit, stated so nobody rediscovers it: the gate is `EXISTS(users)`, so *any* first user closes the claim endpoint permanently, owner or not. That is the ledger's "implicitly claimed" sentence and is intended — but it means M1-B must never register a user-creating route in `claimExemptRoutes`. `TestClaimExemptRoutesAreExactlyTheProbesAndSetup` (`setup_test.go:51`) is what enforces it; do not widen it.

---

## BLOCKING-BEFORE-MERGE

```
FINDING 1: PostgreSQL unreachable answers 500, while the frozen contract promises 503
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:338-402 (mapClaimError), internal/ownerclaim/ownerclaim.go:300-303,374-376,
             api/openapi.yaml (claimOwner "503": "The database was unreachable, or hashing capacity was exhausted."),
             internal/httpapi/setup_test.go:131-168
  requirements: VZ-INSTALL-003, ADR-003 ("A database outage returns 503, never 401")

Observed:
  `ownerclaim.Claim` wraps a BeginTx failure as
  `fmt.Errorf("ownerclaim: beginning claim: %w", err)` (ownerclaim.go:302) and a
  Commit failure the same way (:375). `mapClaimError` has no branch for a
  connection-class failure: `pgconn.ConnectError` is not a `*pgconn.PgError`, so
  `errors.As(err, &pgErr)` at setup.go:369 does not match, the deadline branch at
  :397 does not match, and the function falls through to `return err` at :401 —
  a 500 through the shared handler.
  `TestClaimErrorMapping` (setup_test.go:131) has no infrastructure case, and
  `TestNoClaimErrorMapsToAnUnhandledFiveHundred` (:163) iterates only "23505" and
  "23514". There is no integration test for a claim against a downed database —
  the plan's #18. `TestClaimGuardReturns503WhenTheStateCannotBeRead` (:91) covers
  the MIDDLEWARE, not the claim handler.

Failure:
  On the one endpoint an operator cannot skip, a database outage returns
  `{"error":{"code":"internal_error","message":"an internal error occurred"}}`.
  The operator is told nothing; the diagnosis they need ("the database is
  unreachable") is in the server log only. The published contract says 503 and is
  frozen for vizra-user's generated client, so this is silent contract drift —
  `openapi-verify` checks route↔operation, never status codes.

Perspective: operator, instance-admin

Recommendation:
  Give ownerclaim an infrastructure sentinel and map it once.

    // ownerclaim.go
    var ErrUnavailable = errors.New("ownerclaim: the database is unavailable")
    // wrap BeginTx, Commit, and any query error that is NOT a *pgconn.PgError:
    return Result{}, fmt.Errorf("%w: %v", ErrUnavailable, err)

    // setup.go, in mapClaimError's switch, beside ErrBusy:
    case errors.Is(err, ownerclaim.ErrUnavailable):
        return newCodedError(http.StatusServiceUnavailable, "unavailable",
            "the instance state could not be read")

Acceptance criteria:
  - With PostgreSQL unreachable, POST /api/v1/setup/claim-owner answers 503
    `unavailable`, never 500, and never 403 (a database error must not be
    laundered into "token not accepted").
  - Every status the OpenAPI operation declares is produced by some test, and no
    status it does not declare is reachable.

Tests:
  `TestClaimErrorMapping` gains a `&pgconn.ConnectError{}` (or a plain net error)
  case expecting 503/unavailable. Integration: `TestOwnerClaimAnswers503WhenTheDatabaseIsDown`
  — state the mechanism, as TestAClaimSucceedsWhileTheCacheIsStopped already does
  for the cache (it dials redis://127.0.0.1:1/0); the database equivalent is a
  pool pointed at a closed port, or `pool.Close()` before the request.
  Mutation MUT-28: delete the ErrUnavailable branch → the new test goes red.

Cross-repo implications:
  user: a generated client that switches on 503 to show "the server is having
  trouble, retry" gets a 500 instead and shows the generic error screen.

Challenge:
  "500 is honest — the server failed." It is not honest enough: 503 is the
  contract's own word for it, ADR-003 names the rule, and the distinction is what
  tells an operator to look at PostgreSQL rather than at the claim code.
```

```
FINDING 2: Boot's live-token check sits outside the advisory lock, so concurrent boots both mint
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/ownerclaim/announce.go:74-91, internal/ownerclaim/ownerclaim.go:184-234,
             internal/integration/owner_claim_test.go:691-750
  requirements: VZ-INSTALL-003 recovery case; PLAN-RULINGS row 2

Observed:
  The chair's ruling row 2 reads, verbatim: "N replicas: under the advisory lock
  the first mints, the rest find a live token and print the command only."
  The code reads the token state WITHOUT the lock —
    state, err := State(ctx, q)            // announce.go:74, no lock
    if state.Live { announceCommand(...); return ... }   // :83
    raw, generation, err := Mint(ctx, pool, ttl, false)  // :88
  and `Mint` takes `pg_advisory_xact_lock(1)` (ownerclaim.go:191) but then
  UNCONDITIONALLY supersedes and upserts (:206-219). It never re-reads liveness
  under the lock. `refuseIfUsersExist` guards only "are there users", not "is
  there already a live token".
  `TestARestartDoesNotInvalidateALiveToken` (owner_claim_test.go:691) boots three
  times SEQUENTIALLY. There is no concurrent-boot test, and MUT-14 ("re-mint
  unconditionally at boot") mutates the sequential path only.

Failure:
  Two api replicas cold-starting with VIZRA_OWNER_CLAIM_ANNOUNCE=stderr both read
  "no live token", both enter Mint, and serialise: replica A mints generation N+1
  and prints it; replica B mints N+2 and prints it, overwriting A's digest in
  place. Two byte-identical-looking 64-hex lines are in the log and one of them is
  dead. The operator who picks the wrong one gets the deliberately uninformative
  "that claim token was not accepted", which by design tells them nothing. This is
  exactly the B-5 operator failure the chair ruled against, and the ruling's own
  sentence describes behaviour the code does not have.

Perspective: operator

Recommendation:
  Move the liveness decision inside the lock. ~8 lines, Go only, no schema change.

    // ownerclaim.go
    var ErrLiveTokenExists = errors.New("ownerclaim: a live token already exists")

    func Mint(ctx, pool, ttl, refuseIfUsersExist, onlyIfNoLiveToken bool) (...) {
        ... pg_advisory_xact_lock(advisoryLockMint) ...
        if refuseIfUsersExist { ... }
        if onlyIfNoLiveToken {
            st, err := State(ctx, q)     // re-read UNDER the lock
            if err != nil { return ... }
            if st.Live { return "", st.Generation, ErrLiveTokenExists }
        }
        ...
    }

  Boot passes `onlyIfNoLiveToken=true` and, on ErrLiveTokenExists, calls
  announceCommand with the returned generation. `vizra claim-token` passes false —
  a deliberate re-mint must still always supersede.

Acceptance criteria:
  - Two concurrent Boot calls in stderr mode against one unclaimed database leave
    exactly one token row at generation 1, and exactly one of the two writers
    printed a 64-hex value.
  - A boot that finds a live token prints the command and that token's generation,
    and never a credential.

Tests:
  `TestConcurrentBootsMintExactlyOneToken` — two goroutines, two strings.Builder
  sinks, assert exactly one `out.Minted`, `count(*) FROM owner_claim_tokens` = 1,
  `generation` = 1, and exactly one sink matching hex64.
  Mutation MUT-14b: move the liveness re-read back outside the lock → red.

Cross-repo implications:
  meta: README / COMMANDS.md need no change once the behaviour matches the text.

Challenge:
  "The default is `off`, so boot never mints." True, and that is why this is a
  narrow window — but `stderr` is a documented, supported mode, the ruling
  explicitly describes multi-replica behaviour under it, and the fix is eight
  lines while the instance is still the only consumer of Mint.
```

```
FINDING 3: Every already-claimed refusal writes an immutable audit row, forever, on every claimed instance
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:340-342 (ErrAlreadyClaimed → recordClaimRefusal),
             internal/httpapi/setup_limits.go:101-132, internal/httpapi/setup.go:40 (claimHardCeiling = 600),
             migrations/0005_users_credentials_owner_claim.up.sql:177-191 (DELETE and TRUNCATE refused)
  requirements: VZ-INSTALL-003; PLAN-RULINGS "S-5 / B-6"

Observed:
  The ErrAlreadyClaimed branch calls `s.recordClaimRefusal(c, audit.ReasonAlreadyClaimed)`
  unconditionally. The pgx.ErrNoRows→409 branch (setup.go:351-360) and the
  users_one_owner→409 branch (:371-377) correctly write nothing. The only bound on
  the ErrAlreadyClaimed branch is `allowClaimRequest` at 600 requests per 15-minute
  window (setup.go:40, setup_limits.go:64-72) — the *hard ceiling*, not the failure
  budget, because `refuseToken` (which spends failure budget) is never reached on
  this path. There is no test asserting any bound on `already_claimed` rows:
  `grep -rn "already_claimed|ReasonAlreadyClaimed" internal cmd` returns exactly two
  lines, both production code.

Failure:
  After day one every Vizra instance is claimed, so every anonymous POST to
  /api/v1/setup/claim-owner writes one row into a table this same migration makes
  undeletable — no DELETE, no TRUNCATE, no retention path (the chair took the
  strict trigger and recorded the retention debt). The ceiling permits 600 per
  15 minutes per site: ~57,600 immutable rows per day, from an unauthenticated
  caller, indefinitely, each costing a pooled connection, a BeginTx, an
  AnyUserExists, a rollback, and a second connection for the INSERT. The row
  carries no information after the first one: the response is a constant.
  This is the failure shape B-6 exists to prevent, moved from the unclaimed
  instance (where it is bounded by the instance being claimed within hours) to the
  claimed instance (where it is unbounded for the product's life).

Perspective: operator

Recommendation:
  Two changes in handleClaimOwner, both small.
  1. Refuse from the monotonic cache before touching the pool. The bit is already
     memoised and can never go back (setup.go:61-93); the route is exempt from the
     middleware, so nothing consults it today:

       if claimed, fresh := s.claimed.get(s.deps.Now()); fresh && claimed {
           return newCodedError(http.StatusConflict, "conflict", claimedMessage)
       }

     The authoritative in-transaction AnyUserExists at ownerclaim.go:309 stays —
     it is the gate and must not move.
  2. Drop the `already_claimed` audit row, or gate it on the same one-per-window
     budget `claimLimitTransition` already provides for `rate_limited`
     (setup_limits.go:137-145). My recommendation is to drop it: a refusal on a
     permanently closed endpoint is not a security event, and the first one is
     already indistinguishable from the ten-thousandth.

Acceptance criteria:
  - 200 POSTs to a claimed instance produce at most 1 audit row and at most 1
    database round trip after the bit is cached.
  - Every 409 still carries code `conflict` and the same message.

Tests:
  `TestRepeatedClaimsOnAClaimedInstanceDoNotGrowTheAuditTrail` — claim once, POST
  100 more times, assert `count(*) FROM audit_events WHERE action='setup.owner_claim.refused'`
  ≤ 1 and every response is 409/conflict.
  Mutation MUT-11c: restore the unconditional recordClaimRefusal → red.

Cross-repo implications: none.

Challenge:
  "600/window is bounded, and the ceiling exists for exactly this." The ceiling
  bounds *requests*; the problem is that the bounded thing accumulates forever in
  a table with no delete. A bound that integrates to unbounded over the life of an
  instance is not a bound.
```

```
FINDING 4: argon2id runs inside the claim transaction, pinning a connection for the derivation and the semaphore wait
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/ownerclaim/ownerclaim.go:300-335 (BeginTx at :300, hasher.Hash at :332),
             internal/credential/credential.go:111-129 (the semaphore), :64-66 (ErrBusy)
  requirements: PLAN-RULINGS "B-R10 / B-R11 / B-R12" — "one explicit transaction
                (ClaimOwner → audit insert → commit)"; the backend plan review §5

Observed:
  The transaction opens at ownerclaim.go:300 and the password is hashed at :332 —
  inside it. The hasher's admission control is
    select { case h.sem <- struct{}{}: ...; case <-ctx.Done(): return ErrBusy }
  (credential.go:115-120), so a caller that loses the semaphore race holds its
  pooled connection, idle in transaction, until the REQUEST DEADLINE expires.
  Measured cost of one derivation in the builder's own phase-1 evidence: 25.7 ms
  on an M2, estimated 50–80 ms on the 2 vCPU floor host.
  This is not a schema or contract freeze. It is a pattern freeze: credential's own
  package doc says "M1-B's sign-in is the real multi-caller and must import this
  package" (credential.go:6-9), so M1-B will copy this call shape.

Failure:
  Today: with the 32-claimant race test, up to `pool_size` connections sit idle in
  transaction through a 26–80 ms derivation plus semaphore queueing, and the pool —
  not the CPU — becomes the limit. No deadlock (the semaphore needs no connection),
  so this is occupancy, not a hang.
  Tomorrow, and this is the real cost: M1-B's sign-in is the same shape with
  unbounded callers. At `DefaultConcurrency()` = 4 and 50 ms per derivation, a
  login endpoint that holds a connection across the hash caps out at ~80 logins/s
  while holding 4+ connections hostage — and the diagnosis ("idle in transaction")
  points at the database, not at the hasher. Fixing the pattern now costs ~15 lines
  in one caller; fixing it after M1-B copies it costs two slices.

Perspective: operator, developer

Recommendation:
  Split the read phase off the write phase. The read phase needs no transactional
  consistency: the gate, the redeem CTE's row guard and users_one_owner are the
  enforcers, and the redeem re-matches the row's digest against the COMMITTED row
  under READ COMMITTED regardless.

    q := sqlcgen.New(pool)                     // no transaction
    if claimed, _ := q.AnyUserExists(ctx); claimed { return ErrAlreadyClaimed }
    row, err := q.GetOwnerClaimToken(ctx)      // ErrNoRows -> ErrTokenNotAccepted
    if subtle.ConstantTimeCompare(Digest(normalized), row.TokenSha256) != 1 {
        return ErrTokenNotAccepted
    }
    hash, err := hasher.Hash(ctx, in.Password) // NO connection held here
    tx, err := pool.BeginTx(ctx, pgx.TxOptions{IsoLevel: pgx.ReadCommitted})
    defer tx.Rollback(ctx)
    qtx := sqlcgen.New(tx)
    if claimed, _ := qtx.AnyUserExists(ctx); claimed { return ErrAlreadyClaimed } // the authoritative gate
    res, err := qtx.ClaimOwner(ctx, ...)
    audit.Emit(ctx, qtx, ...)
    tx.Commit(ctx)

  The transaction is then exactly what the ruling names: gate → ClaimOwner →
  audit → commit. Nothing about the race, the ordering, the 409/403 mapping or
  the hash-after-token property changes; `TestNoPasswordHashingOccursWithoutAValidToken`
  (owner_claim_test.go:1029) still passes unchanged.

Acceptance criteria:
  - No database connection is checked out during a call to Hasher.Hash.
  - The claim transaction contains only AnyUserExists, ClaimOwner and the audit
    insert.
  - The race test's results are unchanged across all three server isolation
    defaults.

Tests:
  `TestNoConnectionIsHeldWhileHashing` — inject a Hasher whose Hash asserts
  `pool.Stat().AcquiredConns() == 0` (or records the value for the test to assert),
  driven through the real handler with a valid token.
  Mutation MUT-29: move the Hash call back inside the transaction → red.

Cross-repo implications:
  core: M1-B's sign-in inherits whichever shape merges here.

Challenge:
  "Only a request with the valid token ever reaches the hasher, and there is one
  valid token, so exposure is one operator." True for M1-A — which is exactly why
  this is the cheapest moment to fix it. The blocking case is not this endpoint;
  it is the pattern M1-B is instructed to import.
```

```
FINDING 5: Two tests cannot fail against the mutation they are named for, and one overstates what it proves
Severity:    BLOCKER (evidence integrity)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/integration/owner_claim_test.go:1270-1287 (TestMintTimestampsComeFromTheDatabaseClock),
             internal/integration/owner_claim_test.go:1238-1265 (TestOwnerInsertConflictMapsTo409NotFiveHundred),
             docs/evidence/m1a-owner-claim/demonstrate.sh:260 and 02-mutations.txt:507 (a reference to "MUT-17")
  requirements: AGENTS.md — "Tests must challenge the implementation"; PLAN-RULINGS S-15

Observed:
  1. `TestMintTimestampsComeFromTheDatabaseClock` asserts
       if d := dbNow.Sub(mintedAt); d < 0 || d > 5*time.Second { fail }
     A `minted_at` stamped from the Go host clock passes this on any machine whose
     clocks agree within five seconds — which is every machine. It also carries
     `before := time.Now()` … `_ = before`, dead code. The repository's own
     precedent, TestRunAfterComesFromTheDatabaseClockNotTheApplicationHost, detects
     a 1–2 MICROSECOND divergence (docs/evidence/warroom/2026-09-20-vizra-core-pr2-stabilise-VERIFY.md:106).
     There is no clock mutation in demonstrate.sh's case list at all.
  2. `TestOwnerInsertConflictMapsTo409NotFiveHundred` inserts an owner out of band
     and then claims. Its own comment concedes the race "is not reproducible
     deterministically" and then says "Instead assert the mapper directly against
     the real constraint" — but the out-of-band owner makes AnyUserExists true, so
     the handler returns ErrAlreadyClaimed at ownerclaim.go:313 and users_one_owner
     never fires. The test's name, its comment and the ruling it discharges
     ("an integration test forces users_one_owner to fire through the handler")
     all claim more than it does. The mapper IS covered, by the synthetic
     *pgconn.PgError case in setup_test.go:139-140 — but a verifier reading the
     integration test's name will believe both halves are proven end to end.
  3. `demonstrate.sh:260` justifies not mutating the redeem row guard with "the
     mapper [is proven] by MUT-17" — and there is no MUT-17 in the harness
     (`run_case` declares MUT-1, 2, 2b, 3, 5b, 6, 8, 9, 9b, 10, 10b, 11b, 12, 13,
     14, 15, 16, 18, 19, 24, 25, 26, 27).

Failure:
  Three of the clean-evidence properties this repository is built around fail at
  once: a test that cannot go red, a test whose name misdescribes its coverage,
  and a mutation transcript that cites a case that does not exist. Each of them
  would, on its own, be a false-positive CI signal. Together they are the exact
  thing AGENTS.md's "false-positive CI" and "unsupported readiness claims" lines
  name in the code-review rules.

Perspective: developer, operator (who inherits the untested behaviour)

Recommendation:
  1. Assert both timestamps came from the SAME now(). No query change needed:
       SELECT minted_at = expires_at - $1::interval FROM owner_claim_tokens
     is true iff minted_at and expires_at were computed by one statement's now(),
     and false the moment minted_at is stamped in Go. Add MUT-30 "stamp minted_at
     from the application clock" and prove it red. Delete the `_ = before` line.
  2. Either rename the test to what it does
     (`TestAClaimAgainstAnOutOfBandOwnerIs409NotFiveHundred`) and state that the
     mapper's users_one_owner branch is covered by setup_test.go's synthetic case,
     or make it really fire the index by injecting a Deps.InstanceClaimed that
     returns false while an owner row exists — the seam already exists
     (server.go Deps.InstanceClaimed) and is explicitly "NOT a bypass".
  3. Add the missing MUT-17 (delete the `users_one_owner` case from mapClaimError,
     assert the corresponding test goes red) or correct the transcript's citation.
     A transcript that references a case that was never run is worse than one that
     says "review-only", which is how the other three are handled, correctly.

Acceptance criteria:
  - Every mutation ID referenced in 02-mutations.txt exists in demonstrate.sh.
  - Every named test either has a mutation that turns it red, or appears in the
    review-only list with its reason. The clock test is not currently in either.

Tests: as above.

Cross-repo implications: none.

Challenge:
  "The verifier will catch this." The verifier reproduces what the harness
  declares; a mutation that is never declared is never reproduced, and a test with
  a five-second tolerance passes for the verifier exactly as it passes here.
```

```
FINDING 6: The down file freezes on merge and does not say that re-applying 0005 will fail
Severity:    REQUIRED  (blocking because the file's bytes freeze)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0005_users_credentials_owner_claim.down.sql:1-15,
             migrations/manifest.sha256 (last two lines — the DOWN file is hashed too),
             migrations/0005_users_credentials_owner_claim.up.sql:165-167
  requirements: ADR-002 § Rollback floor; VZ-INSTALL-003

Observed:
  The down file drops the triggers, the function, the FK, the three tables and the
  type, and its header states that surviving audit rows keeping dangling
  actor_user_id values "is correct". It is silent about the consequence: the up
  file's `ALTER TABLE audit_events ADD CONSTRAINT audit_events_actor_user_fk
  FOREIGN KEY (actor_user_id) REFERENCES users (id)` VALIDATES existing rows, so on
  a database that ever recorded an `actor_kind='user'` event — which is every
  database that was ever claimed — down-then-up raises 23503 and 0005 can never be
  re-applied.
  `manifest.sha256` hashes `0005_…down.sql` (line 3 from the end), so this file's
  bytes are frozen by the append-only lane on merge.

Failure:
  An operator or a developer who rolls 0005 back on a claimed database is left
  with a schema that cannot be rolled forward again, and discovers it from a raw
  23503 with no guidance. The migration says the opposite is fine.

Perspective: operator, developer

Recommendation:
  Two sentences in the down file, now, because the bytes freeze:

    -- CONSEQUENCE, stated because these bytes freeze on merge: re-applying 0005
    -- after this down will FAIL with 23503 on any database that recorded an
    -- actor_kind='user' audit event, because audit_events_actor_user_fk validates
    -- existing rows and their actor_user_id no longer resolves. This down exists
    -- for a development database that was never claimed. On a claimed instance
    -- the documented rollback is a restore from backup, not this file.

  I deliberately do NOT recommend `ADD CONSTRAINT … NOT VALID` in the up file: it
  would weaken the constraint's guarantee on a fresh database to buy a rollback
  path for a case ADR-002 already routes through restore.

Acceptance criteria:
  - The down file names the 23503 and names the supported recovery.
  - No change to the up file.

Tests: none needed; this is a frozen comment.

Cross-repo implications:
  meta: COMMANDS.md / the runbook should repeat the sentence when it documents
  migration rollback.

Challenge:
  "A comment is not a control." Correct — but the file freezes on merge, and a
  frozen file that asserts a rollback is safe when it is not is the one class of
  defect that cannot be corrected later without a new migration.
```

---

## REQUIRED-IN-THIS-SLICE (not merge-blocking)

**R-A — `GET /api/v1/setup/claim-status` bypasses the monotonic cache and carries no ceiling.**
`internal/httpapi/setup.go:192-200` calls `s.lookupClaimed(c)` (the uncached path) rather than `s.instanceClaimed(c)`, and `allowClaimRequest` (`setup.go:226`) is applied only to the POST. So an unauthenticated, unlimited GET performs one `SELECT EXISTS (SELECT 1 FROM users)` per request, forever, on an instance where the answer has been a constant `true` since day one and is already memoised (`setup.go:61-93`). Two one-line fixes: use `s.instanceClaimed(c)`, and apply `allowClaimRequest` to the status route too. Test: `TestClaimStatusIsConstantCostOnceClaimed` — 100 GETs after a claim, assert `pool.Stat()` query count grows by ≤ 1.

---

## FOLLOW-UPS, by slice

**F-1 (M1-B)** — The gate is `EXISTS(users)`, so any first user closes the claim endpoint permanently. `claimExemptRoutes` (`setup.go:100-107`) must never gain a user-creating route; `TestClaimExemptRoutesAreExactlyTheProbesAndSetup` is the control. Also inherited, already recorded by the chair: `VIZRA_TRUSTED_PROXIES` (`clientIPPrefix`, `setup_limits.go:42-47`, returns nil whenever a forwarded header is present); enumeration-safe registration against `users_email_fold_key`; reserved usernames; the per-field envelope; `Set-Cookie` on `claimOwner`.

**F-2 (M1-B)** — The SQL hardening of `MintOwnerClaimToken` described above (`WHERE NOT EXISTS (SELECT 1 FROM users)`), so "never mint on a claimed instance" stops depending on a preceding read. Query-level only; no schema change; can land with M1-B.

**F-3 (M1-B)** — `Mint` calls `SupersedeLiveOwnerClaimToken` (`ownerclaim.go:206`) and then the upsert clears `superseded_at` in the same transaction, so the supersede is a dead statement and a CLI re-mint emits `setup.owner_claim.minted` only — no `superseded` row for the generation it killed. Either delete the dead call or emit `ActionOwnerClaimSuperseded` for the previous generation before minting. The audit trail is still adequate (generation is monotonic), so this is tidiness plus one missing history row.

**F-4 (M2)** — Audit retention and user erasure, per the chair's new ledger ID. The 0005 header (`:42-45`) correctly records that `CREATE OR REPLACE FUNCTION` is not matched by migrate-lint's destructive pattern, so the widening is additive.

**F-5 (owner / later)** — `users_username_shape` (`0005…up.sql:70`) is ASCII-only and forever, unless an annotated-destructive CHECK swap. Against VZ-I18N-001 and a global photo community this is a real long-horizon constraint; it is also the conventional choice for a value that appears in `/u/{username}` (homograph risk), and `display_name` carries the Unicode identity. Record it as a decision rather than an accident.

**F-6 (developer note, no action)** — The generated fold expressions cannot be `ALTER`ed. Changing the folding rule later needs `ALTER TABLE users ALTER COLUMN email_fold DROP EXPRESSION` (PG 13+) plus a backfill — which migrate-lint's destructive pattern does NOT match, so an additive escape exists. Worth one line in the header's FOLDING RULE paragraph so the next writer does not assume they are stuck.

---

## What the real files show that the plan could not — the DDL as a foundation

I read `0005…up.sql` and `.down.sql` line by line against what M1-B, M1-C and M2 must add.

**Nothing in this DDL forces M1-B or M1-C into a destructive migration.** Sessions, api_keys, oauth_identities and step-up rows are new tables. Profile, preference, `email_verified_at` and `password_changed_at` columns are `ADD COLUMN`. `ALTER COLUMN email DROP NOT NULL` for an email-less OAuth identity is additive and the email index is already partial (`:85`). Role change and owner transfer are plain `UPDATE`s — I measured previously on PG 18.6 that a single-statement owner swap succeeds against a partial unique index of exactly this shape, in both row orders.

**M2 has exactly one destructive step, and it is the cheap reversible kind the ruling chose deliberately:** widening `credentials_kind` to `('password','totp')` is `DROP CONSTRAINT` + `ADD CONSTRAINT` in one annotated migration with a working down file. Had this been an enum, it would have been a value that can never be removed, in its own migration, with `-- no-down:`. The `kind <> 'password' OR …` form of `credentials_password_is_argon2id` (`:123-124`) means a `totp` row passes without touching that CHECK, and the 1024-octet bound (`:127`) leaves room for an envelope-encrypted secret plus KEK metadata. This is right.

**Constraint names are stable and the mapper keys on them correctly.** `CREATE UNIQUE INDEX users_one_owner` (`:97`) produces an index named `users_one_owner` — not the `users_one_owner_idx` the phase-1 transcript showed — and `mapClaimError` (`setup.go:371`) matches that literal, with `TestOwnerIndexNameMatchesTheMapper` (`owner_claim_test.go:505`) reading the name from the live database. `users_username_fold_key`, `users_email_fold_key`, `users_email_shape` are all matched by name in `setup_test.go:141-147`. Good.

**The `ip_prefix` writer lives in Go, not SQL** (`internal/audit/audit.go:90-124`), is total against the frozen 0003 grammar, compiles that grammar from the migration's own bytes in the test (`audit_test.go:18`), and re-validates immediately before the INSERT (`audit.go:164-169`). The loopback case the builder found — masking `::1` to `::/64`, which 0003's CHECK refuses, inside the claim's own transaction — is genuinely the kind of defect that would have made an instance permanently unclaimable from `[::1]`. It is handled and tested (`owner_claim_test.go:1214`). This discharges S-1 and the 0003 debt properly.

**Both triggers are correct.** The function no longer dereferences `OLD.id` (`:172`), which is what makes it legal for the statement-level `BEFORE TRUNCATE` trigger where `OLD` does not exist. The `-- allow-destructive:` annotation on `:190` is sitting on the line immediately above the one-line `CREATE TRIGGER`, which is what migrate-lint's line-above rule requires, and its reason is accurate: the statement names TRUNCATE only in order to refuse it.

---

## The contract and the Makefile

The OpenAPI delta is consistent with the DDL and with the handler: `additionalProperties: false` on every new schema and enforced at runtime by `DisallowUnknownFields` (`setup.go:245`), the email bound documented as BYTES with the Go validator enforcing bytes, the 201 body reduced to `{username, role}` per ruling row 6, `security: []` on both operations, `/api/v1` as a group with probes deliberately unprefixed. `httpCodeName` gained `409 → conflict` **and** `415 → unsupported_media_type` (`middleware.go:185,190`) — the second is beyond the ruling's "409 only", but 415 is a status this slice actually returns and leaving it mapped to `internal_error` would have been the defect; I accept it. The password `maxLength: 256` runes makes the 1024-byte cap unreachable, and the spec's description says "at most 256, and at most 1024 BYTES" — honest, and `credential.Hash` re-checks the byte bound for M1-B's benefit. Fine.

The single Makefile edit moves `TestM0ContractIsTheFourProbes` to `TestPublicContractIsTheProbesPlusTheSetupOperations` in `openapi-verify`'s `-run` regex. That is exactly right and exactly the thing that must not be forgotten: renaming a test named in a `-run` regex silently drops it from the lane. Nothing else in the diff is outside this slice's ownership.

---

**BLOCKING FINDINGS OPEN AT 32b616d:** FINDING 1 (database-unreachable returns 500 where the contract promises 503), FINDING 2 (boot's live-token check outside the advisory lock — concurrent boots both mint), FINDING 3 (unbounded `already_claimed` audit rows on every claimed instance), FINDING 4 (argon2id inside the claim transaction), FINDING 5 (clock test cannot go red; conflict test mislabelled; MUT-17 cited but absent), FINDING 6 (the frozen down file does not state that re-applying 0005 fails 23503).

---

## Chair note on the backend seat's re-review at `59a19c5` (2026-09-21, tick 114)

All six of the seat's blockers (F1–F6) and its follow-ups F-2, F-3, F-5, F-6 are CLOSED; it would change nothing else in migration 0005 before it freezes and traced every interleaving of the restructured claim to the declared 409/403. **One NEW blocker, introduced by the round itself:** NEW-1 — the hard ceiling added to `GET /setup/claim-status` makes it able to answer 429, but `api/openapi.yaml` declares only 200 and 503 for that operation, and the status-coverage test written this round inspects the POST only. The contract is this PR's to freeze, so it blocks. Taken in the same round because the branch is open: NEW-2 (the 409-vs-403 re-read launders a database error into "token not accepted" and charges the failure budget → 503), NEW-3 (`t.Skipf` in the DB-down test → `t.Fatalf`; core PR #9 will make any skip red by name), FU-1 (`Boot` maps a benign `ErrHasUsers` race to Degraded → Claimed), FU-3 (score MUT-6 and MUT-1b by calling the generated `ClaimOwner` query directly). FU-2 (the "implicitly claimed" invariant as `AND NOT EXISTS (SELECT 1 FROM users)` in the redeem CTE) is query-only and cheap — taken now too, since M1-B's registration route is the first thing that could race it. Consolidated with the security seat's re-review and the verifier's verdict as fix round 2 of 2. The seat's re-review follows verbatim.

---

# Re-review at 59a19c5 — `vizra-core` PR #8 (M1-A owner claim, VZ-INSTALL-003)

**Reviewer:** `vizra-core` backend seat · **Date:** 2026-09-21
**Tree:** `/Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim`, `git rev-parse HEAD` = `59a19c5cc7eeef4154c5e39b6d13ab84f60b5290`, `git status --porcelain` empty, `59a19c5` on top of `32b616d`, no force-push.

**UNVERIFIED:** no PostgreSQL 18 reachable to me this round (no credentials for the verifier's container; I will not start one). I did not run `sqlc generate`, `sqlc diff`, `make ci` or the suite. Test *execution*, `sqlc-verify` and the PG 18 transcripts are the verifier's. Everything below is read from the bytes at this SHA.

---

## Status table

| # | Status | Reason (file:line) |
|---|---|---|
| **F1** DB-unreachable → 503 not 500 | **CLOSED** | `ErrUnavailable` + the `unavailable()` wrapper (`internal/ownerclaim/ownerclaim.go:96-118`), applied to BeginTx, the lock, both read-phase queries, the mint, the redeem's non-PgError branch and both Commits; mapper branch `internal/httpapi/setup.go:390-396`; `TestOwnerClaimAnswers503WhenTheDatabaseIsDown` (`owner_claim_test.go:1789`, mechanism stated: a pool pointed at `127.0.0.1:1`); `TestNoClaimErrorMapsToAnUnhandledFiveHundred` extended to the sentinel classes (`setup_test.go:185-205`); MUT-28 (`demonstrate.sh:257`). The `*pgconn.PgError` carve-out at `ownerclaim.go:110-113` is correct — a server that answered is not an outage |
| **F2** boot liveness outside the lock | **CLOSED** | Liveness read is now inside `Mint` after `pg_advisory_xact_lock` (`ownerclaim.go:249-255`); `Boot` no longer decides (`announce.go:75-77,87-95`) and announces the live generation on `ErrLiveTokenExists`; `TestConcurrentBootsMintExactlyOneToken` (`owner_claim_test.go:1671`) is deterministic via a third connection holding lock id 1, and asserts minted=1, printed=1, generation=1, one `minted` audit row; MUT-14b (`demonstrate.sh:247`) |
| **F3** unbounded `already_claimed` rows | **CLOSED** | The audit call is gone and replaced by `s.claimed.set(true, …)` (`setup.go:374-380`); a cached-true 409 short-circuits before the pool (`setup.go:241-256`); `TestRepeatedClaimsOnAClaimedInstanceDoNotGrowTheAuditTrail` (`owner_claim_test.go:1584`); MUT-11c, MUT-11d (`demonstrate.sh:231,235`) |
| **F4** argon2id inside the transaction | **CLOSED** | Read phase on the pool with no transaction, then `BeginTx(ReadCommitted)` → authoritative `AnyUserExists` → `ClaimOwner` → audit → commit (`ownerclaim.go:368-500`); `TestNoConnectionIsHeldWhileHashing` observes `e.srvPool.Stat().AcquiredConns()` (`owner_claim_test.go:1640-1668`), the fix the builder describes; MUT-29 (`demonstrate.sh:239`) |
| **F5** tests that cannot go red / mislabelled / phantom MUT-17 | **CLOSED** | Clock test now asserts `minted_at = expires_at - ttl` on **both** the INSERT and the ON CONFLICT path (`owner_claim_test.go:1438-1471`) with MUT-30; `TestUsersOneOwnerFiresThroughTheHandler` forces a real 23505 through the handler with an **uncommitted** concurrent owner insert (`:1905-1962`) and pins the message, not just the status; the old test is renamed honestly to `TestAClaimAgainstAnOutOfBandOwnerIs409NotFiveHundred` (`:1401`); MUT-17 exists (`demonstrate.sh:227`); every review-only entry now carries a MEASUREMENT and a reason (`demonstrate.sh:296-356`) |
| **F6** frozen down-file sentence | **CLOSED** | `migrations/0005_users_credentials_owner_claim.down.sql:8-24` — names the 23503, names the up file's validating `ADD CONSTRAINT`, scopes the file to a never-claimed development database, routes a claimed instance to restore, and states why `NOT VALID` was rejected. Accurate on all four counts |
| **R-A** claim-status cached + ceilinged | **PARTIAL** | Both taken (`setup.go:194-203`), `TestClaimStatusIsServedFromTheMonotonicCacheOnceClaimed` (`:1839`), `TestClaimStatusIsBoundedByTheHardCeiling` (`:1872`), MUT-33/MUT-34. **But the ceiling makes the GET able to return 429 and the contract declares only 200/503** → NEW-1 |
| **F-1** M1-B: `claimExemptRoutes` must never gain a user-creating route | open as a **follow-up (M1-B)** | Unchanged; the control is `TestClaimExemptRoutesAreExactlyTheProbesAndSetup` (`setup_test.go:53`) |
| **F-2** mint guard in SQL | **CLOSED, taken now** | `store/queries/owner_claim.sql:49-51` `SELECT … WHERE NOT EXISTS (SELECT 1 FROM users) ON CONFLICT …`; `ownerclaim.go:279-285` maps `pgx.ErrNoRows` → `ErrHasUsers`; `TestMintIsRefusedByTheDatabaseOnAClaimedInstance` calls the generated query **directly** (`owner_claim_test.go:1748`); MUT-32 |
| **F-3** dead supersede call / missing `superseded` row | **CLOSED** | The dead `SupersedeLiveOwnerClaimToken` call is gone; `prior.Live` now emits `ActionOwnerClaimSuperseded` with the generation it kills (`ownerclaim.go:257-275`); `TestASupersedingRemintRecordsTheGenerationItKilled` (`:1768`) |
| **F-4** M2 erasure/retention ledger ID | **follow-up (M2)** | Chair's queue; the 0005 header carries the debt |
| **F-5** ASCII-only username as a decision | **CLOSED** | `0005…up.sql:77-85` — states the homograph reason, names `display_name` as the Unicode carrier, cites VZ-I18N-001, and says the widening is an annotated-destructive CHECK swap |
| **F-6** generated-fold escape | **CLOSED** | `0005…up.sql:22-27` — `ALTER TABLE users ALTER COLUMN email_fold DROP EXPRESSION` (PG 13+). I re-checked `scripts/migrate-lint.sh`'s pattern: `DROP EXPRESSION` is not in the `DROP (TABLE\|COLUMN\|CONSTRAINT\|INDEX\|TYPE\|SCHEMA\|VIEW\|SEQUENCE)` alternation and the `ALTER COLUMN … TYPE` clause does not match either. The sentence is true |
| **B-5** boot minting | **CLOSED** | via F2 |
| **B-6** bound the anonymous writer | **CLOSED** | via F3 |
| **B-R4** complete error map | **CLOSED** | via F1 + MUT-17 + `TestEveryStatusTheContractDeclaresIsProducedAndNoOtherIs` (`setup_test.go:213-246`). Deadline → **503 `unavailable`**, both via the explicit `ctxDeadline`/`ctxCanceled` branch (`setup.go:404-407`) and via `unavailable()` wrapping a deadline-failed query — same answer either way, and 503 is declared |
| **B-R12** one explicit transaction | **CLOSED** | via F4; the transaction now contains exactly gate → ClaimOwner → audit → commit |
| **B-R8** PG 18 acceptance evidence | **PARTIAL / UNVERIFIED by me** | No PG 18 reachable this round; transcripts regenerated (`01-integration-pg18.txt` +352/−…, `02-mutations.txt` +661), verifier owns reproduction. No `uuidv7()` anywhere; ids stay `uuid.NewV7()` |

---

## The things only the restructure could show

**The read-phase / transaction split is correct.** Traced every interleaving of two claimants that both pass the read phase:

- Winner commits before the loser's in-transaction `qtx.AnyUserExists` — under READ COMMITTED that statement takes a fresh snapshot, sees the row, returns `ErrAlreadyClaimed` → **409**.
- Both pass the gate — the loser's redeem CTE blocks on the winner's row lock on the singleton token row, then re-evaluates `consumed_at IS NULL` against the **committed** version: zero rows in `consumed` → zero in `owner` → zero in `cred` → zero from the final `SELECT … FROM owner, cred` → `pgx.ErrNoRows` → re-read → **409**.
- With `consumed_at IS NULL` removed (MUT-1b), the loser instead blocks on `users_one_owner` and raises 23505 → **409** with the same message — which is why that mutation is green, and the transcript says so with a measurement (`demonstrate.sh:341-356`). `TestUsersOneOwnerFiresThroughTheHandler` proves the index path independently.
- Nothing read in the read phase is trusted: the gate re-runs in the transaction, the CTE re-matches the row's own digest against the committed row, `users_one_owner` is the final arbiter. A stale read can only route a request into a transaction that then refuses.

**One ordering does produce something other than 409/403** — see NEW-2: if the database dies between the redeem and the 409-vs-403 re-read, the loser gets 403 rather than 503.

**The wasted derivation is correctly bounded.** N claimants holding the valid token perform N derivations, N−1 wasted. The bound is `credential.DefaultConcurrency()` = `min(GOMAXPROCS,4)` simultaneous (`internal/credential/credential.go:87-92`), ≤76 MiB transient, and a waiter fails on the request context with `ErrBusy` → 503, never an unbounded queue (`credential.go:115-120`). Only a holder of the valid token reaches the hasher at all — now proven twice, by `TestNoPasswordHashingOccursWithoutAValidToken` and by the new `TestACorrectButDeadTokenCostsNoDerivation` (`owner_claim_test.go:1124`). That second one is a genuine improvement nobody asked for: before the liveness pre-check, a *correct but dead* token cost 26 ms while a wrong one cost nothing, which was itself a small oracle. The pre-check removes it.

**The mint statement traces correctly, and I verified both arms.** `WHERE NOT EXISTS (SELECT 1 FROM users)` gates the **source** rows, so when users exist the INSERT has nothing to insert, the `ON CONFLICT` arm is never reached, `RETURNING` yields zero rows, sqlc `:one` scans into `pgx.ErrNoRows`, and `ownerclaim.go:279-285` converts it to `ErrHasUsers` — the CLI's existing refusal text, unchanged. Residual worth stating precisely: the `NOT EXISTS` is evaluated in the mint statement's own READ COMMITTED snapshot, so a claim that commits *during* that statement is not seen. The window shrinks from a full round trip to one statement, and the mint holds the advisory lock while the claim does not — a reduction, not an elimination. It is not exploitable (a token minted after a claim is refused by `AnyUserExists` before it is ever read) and the next boot supersedes it. The comment at `store/queries/owner_claim.sql:36-45` claims exactly this much and no more, which is the right strength.

**Keeping the inner predicates as unobservable defence-in-depth is right.** MUT-6 (`expires_at > now()` in the redeem CTE): the Go pre-check reads `live`, which is itself computed **in SQL with the database clock** (`owner_claim.sql:30`), so expiry has not moved into Go — only its observability has. The CTE predicate remains the only thing that makes expiry atomic with consumption across the ~26 ms hash. Keep it. MUT-1c (`superseded_at IS NULL`): correctly kept and correctly labelled — the predicate guards a path that does not exist yet.

**Is any invariant now defended only in Go where it belongs in SQL?** One, and it is the same one as before the round: **"an instance with users is implicitly claimed"** is a Go decision over a SQL read (`ownerclaim.go:403-410`). Every other claim invariant is a constraint — one live owner (`users_one_owner`), one redemption (`consumed_at IS NULL` + the row lock), never mint on a claimed instance (now the statement), one token row (the singleton PK), argon2id-only secrets (now with its own negative test, `TestTheCredentialsCheckRefusesEveryNonArgon2idSecret`, `:1971`). See the M1-B follow-up for the cheapest way to close it; it is a query change, not a schema change, so it does not freeze here.

**sqlc:** the generated diff is exactly the new statement text plus doc comments propagated from the `.sql` source, with the `Code generated by sqlc / DO NOT EDIT / sqlc v1.31.1` header intact and `Querier` regenerated in step. Consistent with a regenerate, not a hand edit. **UNVERIFIED** — `sqlc diff` is the verifier's `sqlc-verify` lane.

---

## Migration 0005 — last look at the bytes

`git diff 32b616d..59a19c5 -- migrations/` is comments plus the manifest, exactly as stated. I read the frozen sentences and they are accurate and complete: the folding rule and its `DROP EXPRESSION` escape, the password raw-bytes rule, the erasure/retention debt with the `CREATE OR REPLACE FUNCTION` escape, the ASCII-username decision, the `credentials` scope note, the down file's 23503 consequence and its `NOT VALID` rationale.

**I would change nothing else before it freezes.** The extension paths hold: M1-B adds `sessions` as a new table and `ALTER COLUMN email DROP NOT NULL` additively against an already-partial `users_email_fold_key`; M1-C's role change and owner transfer are plain `UPDATE`s against `users_one_owner … WHERE role='owner' AND tombstoned_at IS NULL` (I measured a single-statement swap succeeding against a partial unique index of this shape on PG 18.6 in the plan round); M2 adds `api_keys` and `oauth_identities` as their own tables and widens `credentials_kind` in **one annotated, reversible** migration — which is the whole reason that column is `text + CHECK` and `user_role` is an enum.

---

## OPEN / NEW findings

```
FINDING NEW-1: claim-status can answer 429, and the contract declares only 200 and 503
Severity:    BLOCKER (contract drift, introduced by this round)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:194-199 (the ceiling added for R-A),
             api/openapi.yaml — getSetupClaimStatus declares "200" and "503" only
             (unchanged this round: `git diff --name-only 32b616d..59a19c5 -- api/` is empty),
             internal/httpapi/setup_test.go:215 (the coverage test reads only
             `spec.Paths.Find("/api/v1/setup/claim-owner").Post`)
  requirements: VZ-INSTALL-003; B-R4; the chair's F1 ruling

Observed:
  R-A's fix put the hard ceiling on the GET:
      if !s.allowClaimRequest(c) {
          return newCodedError(http.StatusTooManyRequests, "rate_limited", ...)
      }
  The spec's getSetupClaimStatus lists two responses. `TestEveryStatusTheContractDeclaresIsProducedAndNoOtherIs`
  — written this round precisely to stop this class of drift — inspects the POST
  operation only, so it cannot see the GET. `openapi-verify` checks
  route<->operation and never status codes.

Failure:
  The same defect F1 was about, one operation to the left, created by the fix to
  R-A and guarded by nothing. vizra-user generates its client from this file; a
  consumer that switches exhaustively on the declared statuses meets an
  undeclared 429 and falls to its default branch. `api/openapi.yaml` is the
  product contract, and this PR is the one that creates the /api/v1 surface.

Perspective: developer (vizra-user), operator

Recommendation:
  1. Add the response to the spec, mirroring the POST's wording:

       "429":
         description: The hard request ceiling for the setup routes was reached.
         content:
           application/json:
             schema:
               $ref: "#/components/schemas/Error"

  2. Make the coverage test a table over BOTH setup operations rather than one
     hardcoded `.Post`, so the next route added to the group is covered by
     construction:

       for _, tc := range []struct{ path, method string; produced map[string]string }{
           {"/api/v1/setup/claim-owner",  "POST", map[string]string{...}},
           {"/api/v1/setup/claim-status", "GET",  map[string]string{
               "200": "handleClaimStatus success",
               "429": "hard ceiling",
               "503": "instanceClaimed lookup failure"}},
       } { ... }

Acceptance criteria:
  - Every status either setup operation can return is declared, and every
    declared status is produced.
  - Adding a status to either handler without the spec turns a named test red.

Tests:
  `TestEveryStatusTheContractDeclaresIsProducedAndNoOtherIs`, extended.
  Mutation MUT-41: delete the "429" response from getSetupClaimStatus → red.

Cross-repo implications:
  user: the generated client gains the 429 case on claim-status.

Challenge:
  "429 is a generic transport status, clients handle it anyway." Then the POST
  need not declare it either — and it does, in this same file, for this same
  limiter. Either the contract enumerates statuses or it does not; half is the
  only option that is actually wrong.
```

```
FINDING NEW-2: the 409-vs-403 re-read launders a database error into "token not accepted"
Severity:    SHOULD  (not merge-blocking)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:398-408 (the pgx.ErrNoRows branch),
             internal/ownerclaim/ownerclaim.go:102-108 (ErrUnavailable's own doc:
             "It must never be returned for a bad token: a database error
             laundered into 'token not accepted' is worse than either answer alone")
  requirements: ADR-003 ("a database outage returns 503, never 401"); B-R4

Observed:
  The loser path is
      if pool, perr := s.poolFor(c); perr == nil {
          if owner, oerr := ownerclaim.LiveOwnerExists(...); oerr == nil && owner { ... 409 }
      }
      return s.refuseToken(c)
  Both `perr != nil` and `oerr != nil` fall through to a 403 with the uniform
  "that claim token was not accepted" — and `refuseToken` additionally charges
  the caller's failure budget for a failure that was the server's.

Failure:
  A database that dies between the redeem and the re-read answers 403 on a
  request whose token was correct, and spends the operator's failure budget doing
  it. Narrow — the re-read is one cheap query on a pool that worked milliseconds
  earlier — and safe, but it is the exact rule this round's own sentinel exists
  to enforce, contradicted three lines below where it is enforced.

Perspective: operator

Recommendation:
  Distinguish the two fall-throughs. Three lines, the same sentinel:

    case errors.Is(err, pgx.ErrNoRows):
        pool, perr := s.poolFor(c)
        if perr != nil {
            return newCodedError(http.StatusServiceUnavailable, "unavailable",
                "the instance state could not be read")
        }
        owner, oerr := ownerclaim.LiveOwnerExists(c.Request().Context(), sqlcgen.New(pool))
        if oerr != nil {
            return newCodedError(http.StatusServiceUnavailable, "unavailable",
                "the instance state could not be read")
        }
        if owner {
            s.claimed.set(true, s.deps.Now())
            return newCodedError(http.StatusConflict, "conflict", claimedMessage)
        }
        return s.refuseToken(c)

Acceptance criteria:
  - A lookup failure on the 409-vs-403 re-read answers 503, never 403, and
    consumes no failure budget.

Tests:
  `TestClaimErrorMapping` gains a case driving the ErrNoRows branch with an
  unreachable pool. Mutation MUT-42: restore the `oerr == nil &&` fall-through → red.

Cross-repo implications: none.

Challenge:
  "The window is microseconds." Agreed — which is why this is SHOULD and not a
  blocker. It is three lines in a file that is not frozen, and the chair can take
  it here or in M1-B; I would take it here while the branch is open.
```

```
FINDING NEW-3: a required integration test can skip itself
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/integration/owner_claim_test.go:1796-1798 (t.Skipf),
             internal/db/db.go:39 (pgxpool.NewWithConfig), internal/integration/integration.go:46-55
             ("mustEnv fails rather than skips. A skipped required lane is not a pass.")
  requirements: AGENTS.md — a skipped required test is not PASS

Observed:
  TestOwnerClaimAnswers503WhenTheDatabaseIsDown guards `db.Open` with
  `t.Skipf("the pool refused to open against a closed port, ...")`. `db.Open` uses
  `pgxpool.NewWithConfig`, which is LAZY — it does not dial — so the skip is
  unreachable today and the test really runs. But it is a skip in the one test
  that discharges F1, in a repository whose own harness fatals rather than skips
  for exactly this reason, and it would become live the day anyone adds an eager
  ping to db.Open.

Recommendation: `t.Fatalf` instead of `t.Skipf`. One word.

Tests: none needed.
Cross-repo implications: none.
Challenge: "It can never fire." Then failing is free.
```

---

## Follow-ups

**FU-1 (M1-B, from NEW-2's neighbourhood)** — `Boot` maps `ErrHasUsers` to `Degraded` (`announce.go:96-98` falls through to `if err != nil { BootOutcome{Degraded: true} }`). If a user appears between `Boot`'s `AnyUserExists` and the mint statement, boot reports degraded readiness and logs an error for a benign race whose correct outcome is "claimed". Add an `errors.Is(err, ErrHasUsers)` branch returning `BootOutcome{Claimed: true}`.

**FU-2 (M1-B)** — the "implicitly claimed" invariant is the one claim invariant with no database constraint. The cheapest place to make it one, consistent with what this round did for the mint, is the redeem CTE's guarded UPDATE:

```sql
     WHERE id
       AND token_sha256  = sqlc.arg('token_sha256')::bytea
       AND consumed_at   IS NULL
       AND superseded_at IS NULL
       AND expires_at    > now()
       AND NOT EXISTS (SELECT 1 FROM users)   -- pre-statement snapshot; the sibling
                                              -- CTE's INSERT is not visible to it
```

Keep the Go gate for the *answer* (409 vs 403); this is the *guarantee*. Query-only, no schema change, so it does not freeze here — but M1-B's registration route is the first thing that could ever race it.

**FU-3 (M1-A if cheap, else M1-B)** — convert MUT-6 and MUT-1b from review-only to scored, using the technique this round already established in `TestMintIsRefusedByTheDatabaseOnAClaimedInstance`: call `sqlcgen.New(pool).ClaimOwner(...)` **directly**, bypassing the Go pre-check, against (a) a row with `expires_at` in the past and (b) a row already consumed, asserting `pgx.ErrNoRows` both times. ~20 lines, fully deterministic, and it turns the two honest "MEASURED: nothing reddens" entries into two red-on-mutation cases. The review-only notes are correct as written; this just makes two of them unnecessary.

**FU-4 (M2)** — unchanged: audit retention and user erasure, per the 0005 header's recorded debt and the chair's new ledger ID.

---

**BLOCKING FINDINGS OPEN AT 59a19c5:** NEW-1 (`getSetupClaimStatus` can return 429 but `api/openapi.yaml` declares only 200 and 503, and `TestEveryStatusTheContractDeclaresIsProducedAndNoOtherIs` covers only the POST).

---

## Chair note (2026-09-23, tick 136)

Two blockers open at `56504c1`, both cheap. NEW-A (0005 cites a ledger ID for audit retention that does not exist) is made TRUE without touching core: the chair dispatched a meta PR adding the ledger entry through the generator; core #8 merges only after it. NEW-B (`internal/integration` floor 40 vs 165 measured, `internal/httpapi` 26 vs 56) → the closing builder stages regenerated floors plus a demonstration; with the security seat's F-2 doc NIT. NEW-C left (0005 bytes final). The seat's re-review follows verbatim.

---

# Re-review at 56504c1: `vizra-core` PR #8 (M1-A owner claim, VZ-INSTALL-003)

**Reviewer:** `vizra-core` backend seat · **Date:** 2026-09-23
**Tree:** HEAD is `56504c14683224cfd1fce0ecd7b826dcbf6de88d` and the worktree is clean. Commits since my last look at `59a19c5`: `655f46a` (fix round 2), `a42ca76` (closing slice), `8b54916` (merge of main `eeeea06`), `c79c4d2` (floors), `b2f0d22` and `56504c1` (evidence only).

**Could not check:** I had no access to a PostgreSQL 18 and did not run `make ci`, `sqlc diff` or either suite. Everything below comes from reading the files at this SHA plus two local checks: a comparison of the migration SQL with comments stripped, and the floor formula.

**Verdict:** the transaction design is right and there is exactly one place that decides 409 versus 403. Two blockers remain, both cheap. One is a frozen sentence in 0005 that is currently false and can be fixed in the meta repo alone. The other is two per-package test floors that were not regenerated.

---

## Status table

| Item | Status | Evidence |
|---|---|---|
| **NEW-1** claim-status 429 not declared | **CLOSED** | `api/openapi.yaml` now declares `"429"` on `getSetupClaimStatus`. The status-coverage test now walks every `/api/v1/setup/` operation in the spec against a per-path map of produced statuses (`internal/httpapi/setup_test.go:257-300`). The two routes have separate ceilings, `claimStatusCeiling = 3000` and `claimOwnerCeiling = 600`, so a flood of status reads cannot use up the claim's budget. |
| **NEW-2** the 409-vs-403 re-read turned a database error into a 403 | **CLOSED (superseded)** | The handler's re-read is deleted. `classifyRefusal` wraps every lookup failure, including a `*pgconn.PgError`, as `ErrUnavailable`, which answers 503 and charges nothing (`internal/ownerclaim/ownerclaim.go:600-609`). `ownerclaim.IsServerUnavailable` also sends server-side unavailability codes to 503. Test: `TestAFailedClassificationReadAnswers503AndChargesNothing`. |
| **NEW-3** `t.Skipf` in a required test | **CLOSED** | There is no `Skip` left in `internal/integration/owner_claim_test.go` or `claimtoken_cli_test.go`. |
| **FU-1** Boot reported `ErrHasUsers` as degraded | **CLOSED** | `internal/ownerclaim/announce.go:89-95` now returns `BootOutcome{Claimed: true}`. |
| **FU-2** "users exist" guard in the redeem SQL | **CLOSED** | `store/queries/owner_claim.sql` adds `AND NOT EXISTS (SELECT 1 FROM users)` to the redeem, and the generated code has it at `internal/store/sqlcgen/owner_claim.sql.go:58`. Test: `TestTheRedeemStatementRefusesAClaimedInstance` (`owner_claim_test.go:2247`). Mutations: MUT-46, MUT-54. |
| **FU-3** MUT-6 and MUT-1b scored | **CLOSED** | `TestTheRedeemStatementRefusesADeadToken` (`owner_claim_test.go:2193`) calls the generated `ClaimOwner` directly, bypassing the Go pre-check. Both are now real cases (`demonstrate.sh:327,331`). |
| Migration 0005 citations corrected | **PARTIAL** | Four corrections are accurate. One frozen claim is still false; see NEW-A. |
| Merge `8b54916` | **CLOSED** | `git show --cc 8b54916` shows only `README.md` differing from both parents, and that resolution keeps both sides whole: main's "Reproducing what CI asserts" section and this PR's "Claiming a new instance". Everything else came in from one side unchanged. |
| The three new floors (`c79c4d2`) | **CLOSED as generated, but incomplete** | They match the generator's formula `max(1, n − max(2, round(0.15·n)))` exactly: audit 17→14, credential 6→4, ownerclaim 19→16 (measured in `06-unit.txt:20,24,31`). But the packages whose counts moved were not regenerated; see NEW-B. |
| **B-R8** evidence taken on PostgreSQL 18 | **not checked by me** | `07-race-stress.txt` records PostgreSQL 18.6, Valkey 9.1.2 and Redis 7.2.16. Reproducing it is the verifier's job. |

---

## How the classification behaves inside and outside transactions

**1. The fresh `AnyUserExists` is a separate statement outside any transaction. That is correct.**
`classifyRefusal(ctx, q)` is called with `q := sqlcgen.New(pool)`, which is bound to the pool, not the transaction, at both call sites (`ownerclaim.go:443,499`). So the re-read is its own autocommit `SELECT EXISTS (SELECT 1 FROM users)` on a pooled connection. That is the right design for three reasons:
- **It is as fresh as possible.** The question is "is this instance claimed now". An autocommit statement reads the latest committed state as of the moment it starts.
- **A transaction would add nothing.** A READ COMMITTED transaction would also take a new snapshot per statement.
- **It cannot run inside the claim transaction anyway.** After a failed redeem, that transaction is unusable.

**2. What the stated snapshot residual actually permits.**
The builder's wording in `AGENTS.md:277` is accurate. Tracing it through:
- **A loser holding the valid token can never get a 403 because of the winner.** The winner marks the token consumed and inserts the owner in one transaction (`ClaimOwner` plus the audit insert, then commit), so both become visible at the same instant. A loser whose token read saw the token consumed read after that commit. Its classification statement runs later in the same request, so it also sees the user row and answers 409. PostgreSQL makes a commit visible to every later snapshot on every connection, so it does not matter which pooled connection runs the re-read.
- **What the residual does permit** is a 403 for a token that was genuinely bad (wrong, malformed, expired, superseded or never minted) when a winner commits after the re-read. That answer was true when it was decided, and it matches running the loser just before the winner. The audit row and the budget charge are correctly the caller's.
- **It cannot produce a wrong 409**, because the claimed state only ever goes from false to true.

**3. The post-redeem path rolls back before it classifies. Correct.**
When the redeem returns no rows, the code calls `_ = tx.Rollback(ctx)` and then `classifyRefusal(ctx, q)` (`ownerclaim.go:498-499`).
- Rolling back first releases the claim transaction's connection before a second one is taken. No request ever holds one pooled connection while waiting for another, which would be a deadlock risk on a small pool.
- The deferred second `Rollback` returns `ErrTxClosed` and is ignored.

The empty-redeem cases all come out right:
- a concurrent winner committed (the loser waited on the row lock, then re-checked `consumed_at IS NULL` against the committed row) → 409;
- the redeem's own `NOT EXISTS users` check fired → 409;
- the token expired or was re-minted during the hash → 403 (`TestATokenSupersededDuringTheHashIsTheUniform403`).

**4. There is now exactly one place that chooses between 409 and 403. Confirmed.**
`ErrTokenNotAccepted` is created in only two places:
- `Validate` (`ownerclaim.go:196`). Its only caller is `examineToken` (`:548`), which turns it into `accepted = false`; `grep -rn '\.Validate()' internal cmd` finds no other caller.
- `classifyRefusal` (`:608`).

The handler's old empty-redeem branch is gone, and `mapClaimError` just passes `ErrTokenNotAccepted` on to `refuseToken`.

The other 409 sources — the handler's claimed check, the read-phase check, the in-transaction check, and a unique-index violation on `users_one_owner` — each come from direct evidence that a user or owner exists, so none of them could ever answer 403. That is the right meaning of "one decision point": the one function that turns an *ambiguous* refusal into an answer. `examineToken` never returns `ErrTokenNotAccepted` itself, so an unclassified refusal cannot escape.

**The test seam.** `afterClaimedCheck` is an `atomic.Pointer[func()]`. In production builds it is always nil, so each claim pays one atomic load. Its only setter is in `seam_integration.go`, which is compiled only under `//go:build integration`. `TestTheClaimSeamCannotBeSetFromAProductionBuild` checks both that the setter lives only in a file production builds exclude, and that no production-compiled file contains `afterClaimedCheck.Store(`. MUT-58 covers it.

The tests that use the seam are deterministic and cover every read-phase refusal path:
- `TestAReadPhaseRefusalOnAnInstanceThatBecameClaimedAnswers409` asserts 409, no audit row, no budget charge, no password hash, and that the claimed bit was set.
- `TestAReadPhaseRefusalOnAnUnclaimedInstanceIsStillTheUniform403` is the negative half, and stops the classification from quietly becoming "always 409".

**The stress evidence holds together** (`07-race-stress.txt`):
- `655f46a` reproduces the CI defect: 2 failures in 200 iterations, with the same "unexpected 403" lines.
- `a42ca76` passes 200 of 200 in each of four runs (Valkey and Redis, with and without 16 busy-loop processes), plus 20 of 20 in each of two `-race` runs.
- The file states that product and test code are identical between `a42ca76` and `c79c4d2`.

---

## Migration 0005: last look

**Only comments changed since I reviewed `59a19c5`, and I checked the bytes.** With comments and trailing whitespace stripped, the up file hashes to `a9eae820…` at both `59a19c5` and HEAD, and the down file to `bac9e4d2…` at both. `migrations/manifest.sha256` matches the files on disk (`49ad3a9c…` up, `3fafacb3…` down). The migration's statements are the ones I already reviewed.

Four of the corrections are accurate and improve the file:
- **`display_name`** is now "a future `display_name` (VZ-ACCOUNT-001)". This fixes a false sentence: 0005 has no such column.
- **`credentials`**: ADR-003 reserves TOTP tables (`ADR-003…md:158-159`), so whether TOTP ever becomes a credential kind is left to that slice. This also corrects my own earlier assumption. OAuth is cited to VZ-AUTH-006, and the 1024-octet bound is now justified by what the column actually holds.
- **Down file**: the unsupported ADR-002 citation is gone (ADR-002 § Rollback floor is about image and schema versions, not restore). What remains is the file's own statement of its scope, which is fine.
- **TRUNCATE comment**: it now reads "no production code path truncated this table", which is true. The old "no TRUNCATE appears in any Go, SQL or shell source" was not: migrate-lint's own pattern contains the word.

One sentence is still false (NEW-A below). Otherwise I would change nothing before it freezes. The extension paths I traced for M1-B, M1-C and M2 still hold.

---

## Open findings

```
FINDING NEW-A: a frozen sentence in 0005 cites a ledger ID that does not exist
Severity:    BLOCKER (the migration's bytes freeze on merge; the fix needs no core change)
Confidence:  high

Affected:
  repo:      vizra (meta); vizra-core
  files:     vizra-core migrations/0005_users_credentials_owner_claim.up.sql, ERASURE AND
             RETENTION paragraph: "The audited retention / anonymisation path is still owed
             and carries its own ledger ID."
             vizra docs/quality/features.json at meta HEAD 96fa7a6
             vizra docs/plans/WARROOM-BOARD.md:120 (owner inbox 8c: "the chair will add a
             ledger ID for it")
  requirements: none yet. Propose VZ-AUDIT-001 (audit retention + actor anonymisation);
             VZ-ACCOUNT-002 ("Account export (all data) and deletion") is the neighbouring
             user-facing obligation.

Observed:
  A search of every ledger entry's id, title and outcome for "audit", "retention",
  "erasure" and "anonymis" finds no entry for the audit retention / anonymisation
  path. The board still records it as a promise. The builder corrected four other
  citations in this migration; this is the one left.

Failure:
  0003's own house rule says a header promising something that does not exist is
  worse than no header. If this merges first and the ledger entry never follows,
  the one place that ties the append-only trigger to its owed retention path
  points at nothing. That obligation is also what M2's erasure design depends on.

Perspective: developer, instance-admin

Recommendation:
  Preferred, no vizra-core change: the chair adds the ledger entry through the
  generator BEFORE merging PR #8. The sentence is then true as written. The entry
  should state: retention and anonymisation of audit_events, added additively by
  CREATE OR REPLACE FUNCTION audit_events_append_only(); erasure is
  scrub-and-tombstone of users; depends on VZ-ACCOUNT-002.
  Only if the chair will not add it before merge: change the sentence to
  "...is still owed (owner inbox 8c; the chair has committed to a ledger ID)" and
  regenerate the manifest. That costs a new commit in core.

Acceptance criteria:
  - At the merge SHA, features.json has an entry for audit retention/anonymisation,
    or the 0005 sentence no longer claims one exists.

Tests: none. This is ledger state.
Cross-repo implications: meta: one generator run. core: none on the preferred path.
Challenge:
  "It is a comment." It is a comment in the one file that can never be edited
  again, making a verifiable claim about another file. Making the claim true costs
  one ledger entry.
```

```
FINDING NEW-B: the floors of the two packages that grew were not regenerated, so the whole M1-A integration suite can be deleted with every floor green
Severity:    BLOCKER (cheap: two numbers in one JSON file)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/test-floors.json: "internal/integration": 40 and
             "internal/httpapi": 26, unchanged by c79c4d2 ("No other floor changed");
             docs/evidence/m1a-owner-claim/01-integration-pg18.txt:30 ("internal/integration:
             165 test(s) (floor: 40)"); 06-unit.txt:28 ("internal/httpapi: 56 test(s)
             (floor: 26)"); scripts/go-test-report.py:205-211 (the formula)
  requirements: VZ-INSTALL-003 evidence_required; AGENTS.md (no false-positive CI)

Observed:
  - The floors file's own maintenance note says that in round 3 "only the packages
    whose counts moved were regenerated", and gives the procedure "to regenerate
    after the suites grow".
  - This PR moves internal/integration from 45 measured on main to 165 (it adds
    owner_claim_test.go with 68 test functions and claimtoken_cli_test.go with 5).
    It moves internal/httpapi to 56.
  - Only the three new packages got floors.
  - The same file cites PR#9's FINDING 7: packages sitting inside the headroom,
    internal/httpapi included, is exactly the defect per-package floors exist to catch.

Failure:
  Delete owner_claim_test.go and claimtoken_cli_test.go and internal/integration
  drops to about 45 test events, still above its floor of 40. The whole-suite
  floors (981 integration, 943 unit) are also far below the measured 1349 and
  1184. Every test the council required for the one migration that freezes would
  vanish with every floor green: the three-isolation race, users_one_owner, the
  audit triggers, the 503 path, the classification seam tests. The same is true of
  setup_test.go's route walk, error mapping and status coverage in internal/httpapi.

Perspective: developer, operator

Recommendation:
  Regenerate the floors for the packages that grew, with --emit-floors, following
  the file's own procedure (floors only rise):
      "github.com/yegamble/vizra-core/internal/integration": 140    // measured 165
      "github.com/yegamble/vizra-core/internal/httpapi":     48    // measured 56, in both blocks
  Raise both whole-suite min_tests the same way from the same measured runs.
  Record the measurement in the file's _why notes as round 3 did.

Acceptance criteria:
  - Deleting owner_claim_test.go makes the integration lane red on its
    per-package floor.
  - Deleting setup_test.go makes the unit lane red on internal/httpapi's floor.

Tests:
  A demonstrate.sh case: "delete owner_claim_test.go" → the integration floor goes
  red. The report script already prints the floor verdict.

Cross-repo implications: none.
Challenge:
  "Floors exist to catch a package being emptied, not to pin churn." Losing about
  120 of 165 tests, including every test this PR exists to add, is emptying in
  every sense that matters, and the file's own practice is to regenerate a package
  whose count moved.
```

```
FINDING NEW-C: a 0005 section heading undercounts what 0003 deferred
Severity:    NIT (not blocking; fix only if 0005 is being edited anyway)
Confidence:  high

Affected: migrations/0005_users_credentials_owner_claim.up.sql, the heading "The two
          obligations 0003_audit_events deferred to M1: the users FK and the
          immutability trigger." Compare migrations/0003_audit_events.up.sql:22,29,53,84-93.

Observed:
  0003 deferred four things to M1: the users foreign key, the immutability trigger,
  the audited retention path paired with it, and the ip_prefix writer. Two of those
  are schema changes discharged here. The ip_prefix writer is Go (internal/audit).
  The retention path is still owed, and the header's own ERASURE AND RETENTION
  paragraph already says so.

Recommendation: "The two SCHEMA obligations…". Worth taking only in a commit that
  touches 0005 for another reason. NEW-A's preferred path does not.
```

---

## Checked and correct

- The handler now uses `s.instanceClaimed(c)` instead of peeking at a warm cache. A freshly started process on a claimed instance therefore answers 409 without entering `Claim`, and the unclaimed answer is cached for only 1 second (MUT-50).
- The new `s.unavailable` helper logs the cause through `obs.Redact`.
- `examineToken` now runs `Validate` after the read-phase claimed check. On a claimed instance a malformed body gets 409, consistent with "the claimed check strictly precedes any token examination" (OQ-4). On an unclaimed one, a bad username, email or password still gets 400 before the digest compare, so it reveals nothing about the token.
- A malformed token costs two identical `EXISTS` reads, the read-phase check and the classification. That is the price of freshness, bounded by the ceiling and the failure budget. Fine.

BLOCKING FINDINGS OPEN AT 56504c1: NEW-A (0005 header asserts a ledger ID for the audit retention/anonymisation path that does not exist in features.json; the chair can close it without touching core by adding the ledger entry before merge), NEW-B (`scripts/test-floors.json` leaves internal/integration at 40 against 165 measured and internal/httpapi at 26 against 56, so the M1-A integration and setup suites can be deleted with every floor green; regenerate to 140 and 48).
