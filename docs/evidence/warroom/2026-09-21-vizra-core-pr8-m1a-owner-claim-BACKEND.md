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
