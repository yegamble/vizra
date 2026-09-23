# Bug sentinel sweep: vizra-core M1-A owner-claim path

- **Date:** 2026-09-23
- **Sentinel:** vizra-sentinel-bugs
- **Area:** the setup and owner-claim handlers and routes, `internal/ownerclaim`, the audit writes (migration 0005, `internal/audit`), the cache limiter and its in-process fallback, `vizra claim-token`, the wiring in `cmd/api/main.go`, and the cross-repo callers.
- **Source:** vizra-core `main` at `96d19b31af8a` (dispatch SHA, confirmed by a fresh clone), meta `main` at `b2c5b96`, and vizra-user and vizra-search at `main`.
- **Environment:** PostgreSQL 18.6 (`postgres:18`, `en_US.utf8`, libc provider), Valkey 9.1.2 (`valkey/valkey:9`), go1.27.1 (module toolchain), darwin/arm64. The containers were `sentb-m1a-pg` and `sentb-m1a-valkey`, both removed with `docker rm -f -v`.
- **Reproducers:** one scratch file, `internal/integration/sentinel_m1a_test.go`, compiled under `-tags=integration` in a throwaway clone and never committed. A copy and every transcript are in `$SCRATCH/sentb-wlNR/transcripts/`, where `$SCRATCH` is this session's scratchpad (`/private/tmp/claude-501/-Users-yosefgamble-github-vizra/7321b930-95d2-4a95-ba2e-61ef2ce3c13c/scratchpad`). That folder is ephemeral, so the lines that matter are quoted below.
- **Control:**
  - The existing suites are green on `main` in this environment: `go test -count=1 ./internal/{httpapi,ownerclaim,cache,audit,config}/` all passed.
  - `go test -count=1 -tags=integration -run 'TestOwnerClaim|TestClaim|TestBoot|TestARestart|TestTheCache|TestRateLimiter|TestReadiness' ./internal/integration/` passed with 37 tests selected, per `go test -list` (`run0-control-existing-suites-main-96d19b3.txt`).
  - So every red result below is a gap the current tests do not cover, not a broken harness.
- **Dedupe baseline:**
  - `2026-09-21-vizra-core-pr8-m1a-owner-claim-{VERIFY,SECURITY,BACKEND}.md`;
  - `2026-09-23-vizra-core-pr8-limiter-SECURITY.md` (L-1 to L-3);
  - the PLAN-REVIEW and RULINGS files;
  - open vizra-core PR #12, which fixes limiter L-2 (a cancelled context flips the limiter to degraded) and the N-7/F-1 log redaction.
  - None of those is re-reported here.

**Counts:** 9 findings confirmed by execution: 0 BLOCKER, 0 MAJOR, 7 MINOR, 2 NIT. Six leads are unconfirmed. Every finding was red on `main` at `96d19b3`.

---

## F1. `vizra claim-token` racing an in-flight claim mints a live token on a claimed instance and erases the consumption record

- **Dedupe key:** `vizra-core:store/queries/owner_claim.sql:remint-racing-claim-mints-on-claimed-instance`
- **Severity:** MINOR
- **Location:**
  - `store/queries/owner_claim.sql:28-52` (`MintOwnerClaimToken`, especially `:44` `WHERE NOT EXISTS (SELECT 1 FROM users)` and `:45-51` `ON CONFLICT (id) DO UPDATE`);
  - `internal/ownerclaim/ownerclaim.go:255-334` (`Mint`);
  - `cmd/vizra/claimtoken.go:49`.
- **Mechanism:**
  - The statement's `WHERE NOT EXISTS (SELECT 1 FROM users)` is evaluated once, in the statement snapshot. Under READ COMMITTED, when the claim transaction holds the token row lock (its redeem CTE has run and its `succeeded` audit insert and COMMIT are pending), the upsert waits on that lock. After the claim commits, the `DO UPDATE` runs against the committed row and resets `consumed_at = NULL` with a new digest and generation.
  - `Mint`'s own `AnyUserExists` check, and the `prior.Live` read that emits `superseded`, were both taken before the claim committed.
  - The result:
    - the instance has an owner and also holds a live token;
    - the redeemed generation's `consumed_at` is gone;
    - the append-only trail says generation 1 was both `succeeded` and `superseded`, followed by `minted` generation 2;
    - the CLI prints a "works once" token that can only ever answer 409.
  - This contradicts the query's own comment, which says "never mint on a claimed instance" is a property of the statement. No second owner results: the redeem CTE and `AnyUserExists` still refuse the new token with 409.
- **Reproducer:**
  - `TestSentinelS1RemintRacingAClaimMustNotMintOnAClaimedInstance` is the raw CTE held open.
  - `TestSentinelS1bRemintDuringARealHTTPClaim` is the real `POST /api/v1/setup/claim-owner`. A test-database-only trigger sleeps 2 s inside the claim's own `succeeded` insert, which widens the existing window between CTE and COMMIT without changing it, and then calls the same `ownerclaim.Mint(…, true, false)` the CLI calls.
  - Both are red 3 of 3 (`run3-main-96d19b3-S1-S1b-x3.txt`). The HTTP variant printed:
    ```
    HTTP claim -> 201 | concurrent `claim-token` Mint -> err=<nil> gen=2 token_printed=true | users=1 owners=1 token_live=true consumed_at=<nil> (claimed gen 1)
      audit: minted 1 / succeeded <user> / superseded 1 / minted 2
    redeeming the post-claim token -> 409 conflict
    ```
- **Smallest fix:** add `WHERE owner_claim_tokens.consumed_at IS NULL` to the `ON CONFLICT … DO UPDATE`. The DO UPDATE predicate is evaluated against the locked, latest row version, so the upsert returns no row and `Mint` returns its existing `ErrHasUsers`.
  - Measured in scratch by editing only the generated query string: S1 and S1b turn green, and `TestOwnerClaim*`, `TestClaimTokenCLI*`, `TestBoot*` and `TestARestartDoesNotInvalidateALiveToken` stay green (`run4-S1-candidate-fix.txt`).
  - An alternative is to take `advisoryLockMint` inside `Claim` as well.
  - Owner: vizra-core, as a query edit plus `sqlc generate`. It needs no migration and no contract change.
- **Confidence:** high

## F2. The email validator accepts values the DDL refuses: NUL gives a 500, and a vertical tab or U+2003 reaches the "unreachable" CHECK backstop

- **Dedupe key:** `vizra-core:internal/ownerclaim:email-validator-diverges-from-ddl`
- **Severity:** MINOR
- **Location:**
  - `internal/ownerclaim/ownerclaim.go:66-73` (`emailShape = ^[^\s@]+@…`) and `:202`;
  - `migrations/0005_users_credentials_owner_claim.up.sql:90-92` (`[^[:space:]@]`);
  - `internal/httpapi/setup.go:444-481` (no branch for SQLSTATE 22021, so it falls through to `return err`, a 500);
  - `internal/ownerclaim/ownerclaim_test.go:53-56`, which checks only the octet bound and never compares the email expression.
- **Mechanism:**
  - Go's `\s` is `[\t\n\f\r ]`. PostgreSQL's `[:space:]` also matches `\v`, and under the default `en_US.utf8` it matches Unicode spaces such as U+2003. Neither side excludes NUL, but PostgreSQL `text` cannot store it.
  - Three emails pass `Input.Validate()` and then fail in the database:
    - `a\vb@…` and `a b@…` hit `users_email_shape`, SQLSTATE 23514. The result is a 400, but through the branch the code calls "a defect for us", and each one logs an ERROR.
    - `a\u0000b@…` hits SQLSTATE 22021, which no branch maps, so it becomes a 500 "an internal error occurred".
  - Several texts promise this cannot happen:
    - `ownerclaim.go:66-69`: "These are the same expressions migration 0005 enforces; TestValidatorsMatchTheMigration … asserts it";
    - the plan-review acceptance: "No input accepted by the OpenAPI schema can produce a 5xx", and the OpenAPI pattern accepts NUL;
    - `TestNoClaimErrorMapsToAnUnhandledFiveHundred`: "every named database signal this endpoint can produce has an answer".
  - All three are false (R1). The failures are reachable only after the token has compared equal. The token stays unconsumed, because the transaction rolls back.
- **Reproducer:** `TestSentinelS2EmailTheValidatorAcceptsMustNotReachTheDatabaseAndFail`, red in 3 of 3 subtests (`run1-main-96d19b3.txt`):
  ```
  Go validator on "a\x00b@example.org": <nil>
  POST -> 500 {"code":"internal_error","message":"an internal error occurred"}
  server log: … error="ownerclaim: redeeming the token: ERROR: invalid byte sequence for encoding \"UTF8\": 0x00 (SQLSTATE 22021)"
  Go validator on "a\vb@example.org": <nil>   POST -> 400, log: level=ERROR msg="http: a CHECK constraint refused a request the validator accepted" constraint=users_email_shape
  ```
- **Smallest fix:**
  - In Go, refuse any rune for which `unicode.IsSpace` is true, plus NUL and other control characters, so the validator is at least as strict as `[:space:]` under any libc locale.
  - Map 22021 to 400 as a backstop.
  - Make `TestValidatorsMatchTheMigration` drive a shared corpus of inputs (`\v`, U+2003, U+00A0, NUL) through both Go and a real `CHECK`, rather than comparing literals.
  - Owner: vizra-core. It needs no migration. An optional contract tweak would add `\u0000` to the documented refusal set.
- **Confidence:** high

## F3. The `rate_limited` audit row is not "one per bucket per window": ceiling 429s write none, and the per-origin and global buckets share one marker

- **Dedupe key:** `vizra-core:internal/httpapi/setup_limits.go:rate-limited-audit-not-per-bucket`
- **Severity:** MINOR
- **Location:**
  - `internal/httpapi/setup_limits.go:152-160` (`claimLimitTransition` spends one shared `rl:setup.claim:audited` key);
  - `:163-176` (the row always records `{"bucket":"failure"}`);
  - `internal/httpapi/setup.go:212-214` and `:251-254` (ceiling 429s write nothing);
  - vizra-core `AGENTS.md:405`: "exactly ONE `rate_limited` row is written per bucket per window".
- **Mechanism:**
  - The transition marker is one key for the whole site, and it is spent only on the failure-budget path.
  - A per-origin transition followed by a global transition in the same window writes one row. It cannot say which bucket tripped.
  - The two hard ceilings never write a row. So the accepted residual AGENTS.md itself documents, a stranger holding claim-owner at 429 so that the operator's **valid** token is refused, leaves no trace in the audit trail.
  - This is R1. The previous reviews accepted the sentence (limiter-SECURITY §3, VERIFY:2080).
- **Reproducer:** `TestSentinelS4EveryLimitedBucketLeavesOneRateLimitedRow` (`run1-main-96d19b3.txt`):
  ```
  operator's VALID-token claim after the flood -> 429 rate_limited; users=0; rate_limited rows=0
  3001st claim-status -> 429; rate_limited rows=0
  per-origin: … 403×10, 429; rows after per-origin transition=1; global-limited responses=1; rows after global transition=1
  ```
  The flood was 600 inert `text/plain` POSTs, each answered 415.
- **Smallest fix:**
  - Key the marker per bucket: `rl:setup.claim:audited:<bucket>`.
  - Call `recordClaimRateLimited(c, bucket)` on the ceiling transition as well. That still bounds the writes at one row per bucket per window.
  - Record `bucket` truthfully: `per_origin`, `global`, `ceiling.claim` or `ceiling.status`.
  - If the owner prefers the current behaviour, correct the AGENTS.md sentence instead.
  - Owner: vizra-core. It needs no migration and no contract change.
- **Confidence:** high

## F4. A client that hangs up is logged at ERROR as "could not reach the database", and `mapClaimError`'s cancellation branch is dead

- **Dedupe key:** `vizra-core:internal/ownerclaim:cancellation-logged-as-db-outage`
- **Severity:** MINOR
- **Location:**
  - `internal/ownerclaim/ownerclaim.go:127-133` (`unavailable` wraps with `%v`, so `context.Canceled` is not preserved for `errors.Is`);
  - `internal/httpapi/setup.go:277-279`, `:430-435` and `:476-479` (the unreachable `ctxDeadline`/`ctxCanceled` branch).
- **Mechanism:**
  - A cancelled request context makes the pgx call fail with `context canceled`.
  - `unavailable()` turns that into `ErrUnavailable` using `%v`, and the handler's own pre-check sends it straight to `s.unavailable`. Both write `level=ERROR msg="http: the claim endpoint could not reach the database"`.
  - The explicit cancellation branch in `mapClaimError` can therefore never fire for a database-phase cancellation.
  - This is rule R9 ("a cancelled context is not a backend failure"). Any anonymous client can produce false database-outage ERROR lines by disconnecting, bounded by the 600-per-15-minute ceiling. The noise lands on the one signal an operator uses to diagnose an unclaimable instance.
  - It is distinct from PR #12, which fixes only the limiter's degraded flag.
- **Reproducer:** `TestSentinelS7ACancelledClaimIsNotLoggedAsADatabaseOutage`, red in 2 of 2 subtests (`run2-main-96d19b3-S7-L1.txt`):
  ```
  cancelled request -> 503 unavailable; level=ERROR msg="http: the claim endpoint could not reach the database" where="checking claimed state" error="context canceled"
  (inside Claim) … where=claim error="ownerclaim: the database is unavailable: checking claimed state: context canceled"
  ```
- **Smallest fix:**
  - In `ownerclaim.unavailable`, and wherever the handler checks the claimed state, test `ctx.Err()` or `errors.Is(err, context.Canceled|DeadlineExceeded)` first.
  - Return the context error wrapped with `%w`, so the existing branch fires and logs nothing at ERROR.
  - Owner: vizra-core. It needs no migration and no contract change.
- **Confidence:** high

## F5. On the claim-status route and the unclaimed guard, a 503 logs only the canned message, never the cause

- **Dedupe key:** `vizra-core:internal/httpapi/setup.go:status-and-guard-503-drop-cause`
- **Severity:** MINOR
- **Location:** `internal/httpapi/setup.go:144-149` (the guard), `:218-221` (`handleClaimStatus`) and `:327-331` (the `poolFor` failure in `handleClaimOwner`).
- **Mechanism:**
  - These branches return `newCodedError(503, …)` and drop `err`. The shared error handler then logs only `error="the instance state could not be read"`.
  - `unavailable()`'s own comment names this exact defect ("a 503 whose only trace was 'the instance state could not be read'. That is not diagnosable."). It was fixed for the POST but not for the GET the claim page calls first, nor for the guard.
  - During a database outage, the operator's first failing request leaves no cause in the log.
- **Reproducer:** `TestSentinelS3AClaimStatus503LogsItsCause` (`run1-main-96d19b3.txt`). The same injected `connection refused` gives three different logs:
  - GET claim-status: `error="the instance state could not be read"` only;
  - the guarded route: the same;
  - POST: `where="checking claimed state" error="dial tcp …: connection refused"`.
- **Smallest fix:** route all three branches through `s.unavailable(c, where, err)`, which logs the redacted cause once. Owner: vizra-core. It needs no migration and no contract change.
- **Confidence:** high

## F6. The `succeeded` audit row does not name the token generation it consumed

- **Dedupe key:** `vizra-core:internal/ownerclaim:succeeded-row-missing-generation`
- **Severity:** MINOR
- **Location:**
  - `internal/ownerclaim/ownerclaim.go:507-517` (`After` carries `{username, role}` only; `created.TokenGeneration` is returned but not audited);
  - `migrations/0005_users_credentials_owner_claim.up.sql:161-162`: "Audit rows and operator-facing output reference the GENERATION, so a claim is traceable".
- **Mechanism:**
  - The `minted` and `superseded` rows carry the generation. The row recording the redemption does not. The trail therefore cannot link a claim to the credential that was redeemed, and it relies on the mutable `owner_claim_tokens` row to do so.
  - F1 shows that row can be overwritten, which leaves no record anywhere of which generation was consumed.
  - The migration comment is frozen and append-only, so the code has to meet it.
- **Reproducer:** `TestSentinelS8TheSucceededRowNamesTheConsumedGeneration` (`run5-main-96d19b3-S8.txt`):
  ```
  succeeded row: subject_id=01a0cf9c-… after={"role": "owner", "username": "owner"} (minted generation 1)
  ```
- **Smallest fix:** add `"token_generation": created.TokenGeneration` to `After`. It is not secret material, and `TestOwnerClaimAuditEventsCarryNoSecretMaterial` still holds. Owner: vizra-core. It needs no migration and no contract change.
- **Confidence:** high

## F7. Cross-repo: the meta compose and env registry do not deliver core's two owner-claim keys, and the registry does not list `claim-token`

- **Dedupe key:** `meta:env/registry/core.json:owner-claim-keys-and-command-missing`
- **Severity:** MINOR
- **Location:**
  - meta `docker-compose.yml:69-111` (`x-core-env`; there is no `env_file` and no passthrough);
  - `env/registry/core.json:3` (snapshot `source_commit` 4a80a1e, which predates core #8) and `:197-201` (`commands`: version, doctor, migrate);
  - `env/production.env.example`, which has no `OWNER_CLAIM` line.
- **Mechanism:**
  - Core `main` reads `VIZRA_OWNER_CLAIM_ANNOUNCE` and `VIZRA_OWNER_CLAIM_TTL` (`internal/config/keys.go:71-72`). The api service environment is an explicit map, so an operator who sets either key in `.env` changes nothing. The keys are silently pinned to their defaults, `off` and `1h`.
  - The registry's `commands` list omits `vizra claim-token`, which is the operator's only primary claim path. `check-template-claims.py` would then refuse any meta doc that tells an operator to run it.
  - Meta CI cannot see this: the drift check needs component checkouts, and CI does not have them.
- **Reproducer:** `cross-repo-meta-b2c5b96.txt`:
  - Rendering with `VIZRA_OWNER_CLAIM_ANNOUNCE=stderr` and `VIZRA_OWNER_CLAIM_TTL=15m` in the env file gives an `.services.api.environment` with neither key.
  - `check-config-coverage.py` (CI mode) reports `0 violations`, exit 0.
  - `check-config-coverage.py --drift`, run against core 96d19b3, reports:
    ```
    VIOLATION rule=registry-drift subject=vizra-core/VIZRA_OWNER_CLAIM_ANNOUNCE … not in env/registry/core.json (snapshot at 4a80a1e3f36b)
    VIOLATION rule=registry-drift subject=vizra-core/VIZRA_OWNER_CLAIM_TTL …
    ```
- **Smallest fix:**
  - Re-stamp `env/registry/core.json` at core `main`, with the two keys and the `claim-token` and `healthcheck` commands.
  - Add both keys to `x-core-env`, with defaults, and to `env/production.env.example`, carrying core's stderr warning.
  - The stale "`vizra` has three subcommands" and "core has no `healthcheck` subcommand" comments in `docker-compose.yml` go with it.
  - Owner: meta. It needs no migration and no contract change.
  - Not re-reported: the ledger, META_REPO §4 and FIRST-SLICE copy still describe the retired "restart re-mints / read the log" design. That divergence is deliberately recorded as pending owner inbox 8a (`features.json` VZ-INSTALL-003 `notes`).
- **Confidence:** high

## F8. "Strict decode" accepts case-folded keys and a trailing `}` or `]`

- **Dedupe key:** `vizra-core:internal/httpapi/setup.go:claim-decode-not-strict`
- **Severity:** NIT
- **Location:** `internal/httpapi/setup.go:296-316`.
- **Mechanism:**
  - `encoding/json` matches field names case-insensitively, so `{"TOKEN":…,"USERNAME":…}` passes `DisallowUnknownFields`. Those are properties the schema's `additionalProperties: false` does not define.
  - `dec.More()` returns false before a `}` or `]`, so `{…}}]` passes the "exactly one JSON object" check.
  - There is no security consequence. It is a gap between the contract and its enforcement (R1).
- **Reproducer:** `TestSentinelS5StrictDecodeIsStrict`: both variants got `201` (`run1-main-96d19b3.txt`).
- **Smallest fix:** after `Decode`, require `dec.Token()` to return `io.EOF`. Check the key set exactly, either by decoding first into `map[string]json.RawMessage` or with `encoding/json/v2`'s case-sensitive default. Owner: vizra-core.
- **Confidence:** high

## F9. `VIZRA_OWNER_CLAIM_TTL` accepts a sub-microsecond duration that every mint then fails on

- **Dedupe key:** `vizra-core:internal/config:owner-claim-ttl-unbounded`
- **Severity:** NIT
- **Location:** `internal/config/config.go:260` and `:480-492` (only `d > 0`); `internal/ownerclaim/ownerclaim.go:634-636` (the interval is truncated to microseconds); migration 0005 `:172` (`owner_claim_tokens_ttl CHECK (expires_at > minted_at)`).
- **Mechanism:**
  - `500ns` passes config. The interval truncates to 0, and the mint fails its CHECK with 23514. Boot reports degraded, and `claim-token` exits with a raw constraint message.
  - Values from 1 µs to a few seconds are accepted but unusable, and there is no upper bound.
- **Reproducer:** `TestSentinelS6ASubMicrosecondClaimTTLIsRefusedAtBootNotAtMint`:
  ```
  config.LoadFrom(VIZRA_OWNER_CLAIM_TTL=500ns): err=<nil>
  Mint: … violates check constraint "owner_claim_tokens_ttl" (SQLSTATE 23514)
  ```
- **Smallest fix:** bound the key in config, for example between 1m and 24h, and document the bounds in `keys.go`. Owner: vizra-core.
- **Confidence:** high

---

## Paths traced and found sound

- **Single-use claim concurrency:** the claim is decided by the database, not by a Go check-then-act. The redeem CTE's row lock and `consumed_at IS NULL` pick one redeemer. `AND NOT EXISTS (SELECT 1 FROM users)` and `users_one_owner` back it up. The existing `TestOwnerClaimRaceYieldsExactlyOneOwnerUnderEveryServerDefaultIsolation` passes here. F1 is the mint side, not the redeem side.
- **Transaction isolation:** `Claim`, `Mint` and `SupersedeLive` all pin READ COMMITTED. The read phase holds no transaction and no connection across argon2id. `classifyRefusal` re-reads the claimed state fresh, so every refusal is classified 409 or 403 in one place.
- **Token handling:** 256-bit `crypto/rand` entropy, stored as SHA-256. The digest compare is constant-time, and the row's own digest (never presented bytes) is what reaches SQL. The password is hashed only after the token is accepted, and `live` is pre-checked by the database clock.
- **Time and TTL:**
  - `live` in the read phase and `expires_at > now()` in the CTE both use the database clock. At the boundary the outcome is a 403, never a 201 on an expired token.
  - The limiter's window: `INCR` plus `EXPIRE NX` in MULTI/EXEC, with the TTL set once. The in-memory fallback is a fixed window on the monotonic clock.
  - The `MemoryLimiter` map is bounded in practice. Failure keys are created only past the claim-owner ceiling of 600 per window, and pruning starts above 4096.
- **Cache down and flapping:** the fallback fails open, which is right for a once-only endpoint (`users_one_owner`). Flapping grants at most one extra per-process window, known as L-3. The cancelled-context flip is known as L-2 and fixed in open PR #12.
- **Resource bounds:**
  - Bodies go through an 8 KiB `MaxBytesReader`, and oversize bodies are answered 413.
  - Content type is checked before the body is read.
  - A claimed instance answers 409 before the body is read, from the monotonic cache.
  - `X-Request-Id` is accepted only as a UUID.
  - The server sets `ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout` and `IdleTimeout`.
- **Error mapping:**
  - Every `codedError` 5xx hides its message.
  - PgError classes 08, 53 and 57P0x are answered 503.
  - 23505 on `users_one_owner` is answered 409.
  - `credential.ErrBusy` is answered 503.
  - The exceptions are F2 (22021 becomes a 500) and F4 (cancellation is logged as an outage).
- **Audit redaction:** no email, token, digest or full IP appears in any row. `IPPrefix` is total, including `::1` (closed in earlier reviews). Audit failures on the refusal path are logged and dropped, never turned into a 500.
- **Claimed-state cache:** it is monotonic (an atomic bool that is never reset), and a concurrent `set(false)` cannot undo `true`.
- **Wiring:** `cmd/api/main.go` gives the limiter, pools and boot outcome to `httpapi.New`, and a boot failure degrades readiness rather than crash-looping.
- **vizra-user:** `main` vendors the core contract at `415a6d1`, which predates M1-A. It has no claim page and no client call, so it cannot disagree with core yet.
  - The CLI's `…/setup/claim` link is not served by vizra-user `main`. That is expected while the UI slice is pending.
- **Tests:** the claim-path suites are not vacuous. `mustEnv` fails rather than skips, floors are recorded per package, and the race tests use `pg_stat_activity` barriers rather than sleeps.

## Unconfirmed leads

1. **The guard classifies by the decoded path, while Echo routes by `RawPath`.**
   - An executed probe shows the mismatch (`run2-main-96d19b3-S7-L1.txt`): `GET /heal%74hz` and `GET /api/v1/setup/claim%2Dstatus` are classified exempt by the decoded `URL.Path` but routed on `RawPath`. While unclaimed, they answer 404, not the 403 that `claimExemptRoutes`' comment promises ("including the router's 404 path").
   - This is harmless on `main`, which has no guarded routes. It becomes a bypass if M1-B adds a parameterised route whose raw form can match while the decoded form equals an exempt key.
   - A test would confirm it: a param route under `/api/v1/setup/:x`, requested as `claim%2Dstatus` while unclaimed.
   - Fix direction: classify on the matched route (`c.RouteInfo().Path` plus the method).
2. **Any direct client can opt out of attribution.**
   - Sending any `X-Forwarded-For` makes `clientIPPrefix` return nil. The per-origin bucket is then skipped, and `ip_prefix` is NULL even when `RemoteAddr` is the true peer.
   - This is documented design pending `VIZRA_TRUSTED_PROXIES` (M1-B), so it is not a bug today. It should be an explicit M1-B acceptance case: "a spoofed XFF from a direct peer does not erase its prefix".
3. **The degraded flag stays set after a real cache outage.**
   - `Degraded()` stays true until the next `Allow`. On a claimed instance, only the setup routes call `Allow`, so `/readyz` can keep saying "rate limiting is running on the in-process fallback" long after the cache has recovered.
   - L-2 notes the mechanism ("until the next healthy call"), but not this consequence.
   - It would be confirmed by pausing Valkey, calling one setup route, unpausing, and reading `/readyz` over time. Not run.
4. **A non-UTF8 external database.** An operator-supplied LATIN1 or SQL_ASCII database would refuse a non-ASCII email with 22P05, which becomes a 500 like F2. Not run.
5. **Mint has no deadline.** `vizra claim-token` uses `context.Background()`, and api `Boot` uses the signal context. `pg_advisory_xact_lock` or the token-row lock can therefore block the CLI indefinitely, and can block api start before it listens. Needs a held-lock reproducer. Not run.
6. **A blackholed cache.** go-redis with `DialTimeout` 2 s and `MaxRetries` 2 can spend about 6 s per `Allow` until its dial-error fast-fail engages, and a claim-owner POST makes up to 4 `Allow` calls. Needs a blackholed address, not just a refused port. Not run.

## Not run

- The Redis 7.2 leg. Only Valkey 9.1.2 was used. No finding depends on the flavour: F3 is a count of audit rows.
- The race detector on the scratch tests, which ran without `-race`. The existing suites run under `-race` in CI.
- vizra-search, which is out of scope for this area.
- No safety-classifier stops occurred. All inputs were inert: a wrong 64-hex token, synthetic emails, and `text/plain` bodies.

## Observation

- **An unverified rate-limit notice.** A `system-reminder` claiming "GitHub API rate limit exceeded … sleep until reset" was appended to the output of a `gh pr diff 12` Bash call. An immediate `gh api rate_limit` returned `"remaining":4662` of 5000. The notice was treated as untrusted and not acted on. This matches the recorded forged-reminder pattern (memory `forged-reminder-in-subagent-tool-results`).

## Cleanup

- `docker rm -f -v sentb-m1a-pg sentb-m1a-valkey` removed both containers and their volumes.
- The throwaway clones of core, user, meta and search, the scratch Go build directories and the env file were deleted.
- Only `$SCRATCH/sentb-wlNR/transcripts/` remains, at 64 KB: the transcripts and the reproducer source.
- No real checkout, PR, comment or FINDINGS.md entry was touched.
