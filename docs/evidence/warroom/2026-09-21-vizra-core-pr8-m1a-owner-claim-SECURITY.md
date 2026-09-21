# vizra-core PR #8 (M1-A owner claim, VZ-INSTALL-003) — CODE review by the `vizra-security` seat

- **PR:** yegamble/vizra-core#8, branch `feat/m1-owner-claim`
- **Reviewed SHA:** `32b616dcd6d9ed3ea8d05020e1d66dae25c0e8ed`
- **Reviewer:** `vizra-security` council seat (agent `a95ace2c4cf1ebf0d`, the same seat that reviewed the plan), read-only, nothing executed
- **Date:** 2026-09-21
- **Kind:** specialist review of the code against the chair's plan rulings (`…-PLAN-RULINGS.md`). Not a verifier verdict.
- **Result:** one BLOCKING finding open (N-1), three REQUIRED (N-2, N-3, N-4), three follow-ups (N-5 → M1-A/M1-B, N-6 → M1-B, N-7 → core sweep). The chair consolidates these with the backend seat's review and the verifier's verdict into one fix round.

The seat's report follows verbatim.

---

# Code review at `32b616d` — `vizra-security` seat

**Date:** 2026-09-21 · **Head:** `32b616dcd6d9ed3ea8d05020e1d66dae25c0e8ed` (confirmed via `git rev-parse HEAD`; worktree clean, one commit on `5eb2829`) · **Reviewed:** the rulings file, plan rev 2, and the code read-only in `/Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim`. Echo v5.3.1, `net/netip` and `golang.org/x/crypto` read from the module/GOROOT cache. No scratch files created; nothing executed.

This is a faithful, unusually complete implementation of the rulings. The four things I most expected to be got wrong — `ip_prefix` totality, the announce default, the structural guard, and the failure-keyed limiter — are right, and right for the stated reasons. Four things are open.

---

## S-1…S-15 status

| # | Finding | Status | Evidence |
|---|---|---|---|
| S-1 | `ip_prefix` writer total against the frozen 0003 grammar | **CLOSED** | `internal/audit/audit.go:90-124` (zone→nil, `Unmap()` first, loopback/unspecified→nil, self-validates against the grammar at :120); belt-and-braces re-check before the INSERT at `:164-169`; grammar compiled from the migration's bytes `internal/audit/audit_test.go:18`; `TestIPPrefixWriterOutputAlwaysSatisfiesTheFrozenCheck` `:68`; `TestOwnerClaimSucceedsFromIPv6Loopback` `internal/integration/owner_claim_test.go:1214` covers `[::1]`, `[::]`, `[::ffff:127.0.0.1]` and `garbage`. I re-derived the `::/64` and `"invalid Prefix"` hazards against the Go source and cannot construct an input that escapes. |
| S-2 | Announce default `off`; boot prints a command | **CLOSED** | `internal/config/keys.go:71` (`Default: "off"`), `internal/ownerclaim/announce.go:79-86,103-111` (command only), `.env.example` text names the risk in terms; `TestTheAnnounceDefaultIsOff` `internal/httpapi/setup_test.go:177`; `TestBootMintsOnlyUnderTheStderrOptIn` `:719`. The `stderr` line itself (`announce.go:92-99`) tells the operator it just wrote a credential to the log — better than I asked for. |
| S-3 | Boot does not invalidate a held token | **CLOSED** (see N-5 for the replica clause) | `announce.go:83-86`; `TestARestartDoesNotInvalidateALiveToken` `:691` loops three boots. |
| S-4 | Structural unclaimed guard | **CLOSED** | `internal/httpapi/setup.go:95-142`, wired at `internal/httpapi/server.go:152`; two-set classification `:100-118`; `TestEveryRouteIsEitherUnclaimedAllowlistedOrGuarded` / `TestClaimExemptRoutesAreExactlyTheProbesAndSetup` / `TestClaimGuardReturns503WhenTheStateCannotBeRead` / `TestTheClaimedBitIsCachedMonotonically` `setup_test.go:27-130`; 404 path covered `:70` and `integration:1325`. Lookup error → 503 `setup.go:129-134`, never allow. |
| S-5 | A 429 writes no audit row | **PARTIAL → see N-1** | The 429 path is correct and tested (`setup.go:418-429`, transition bucket `setup_limits.go:137-145`, `TestARateLimitedClaimWritesNoAuditRow` `:1152`). The **409 path writes one permanent row per request** (`setup.go:341`), unbounded in time. |
| S-6 | `credentials` CHECK loosened; fold and password rules frozen in the header | **CLOSED** | `migrations/0005…up.sql:123-124` (`LIKE '$argon2id$%'`), `:13-26` (folding and password rules), generated columns `:57,59`; parameters pinned in Go `internal/credential/credential.go:51` + `TestStoredPasswordFormatIsTheFrozenArgon2idParameters`; `TestEmailFoldIsProducedByPostgresOnEveryPath` `integration:1359`. |
| S-7 | Limit failures, not attempts; never write the proxy's prefix | **CLOSED** | One `clientIPPrefix` `setup_limits.go:42-47` used by both the limiter and the audit writer, with the self-found bug fixed; failure budget only on rejection `setup.go:418`; `TestAValidTokenIsNeverRateLimitedByTheFailureLimiter` `:1125`; `TestForwardedHeaderWithoutTrustedProxyYieldsNullIPPrefix` `:1187`; fail-open + degraded readiness retained. I found **no remaining path that trusts a forwarded header**: `c.RealIP()` appears nowhere in product code, and Echo v5 sets no `IPExtractor` (`server.go:104+`), so `RemoteAddr` is the only source and it is gated by `clientIPPrefix`. |
| S-8 | Content-type, strict decode, body bound, origin posture | **PARTIAL → see N-3** | Posture present and tested: `setup.go:231-262` (415 → `MaxBytesReader` → `DisallowUnknownFields` → `dec.More()`), `:296-310`, `:316-332`; `c.Bind` is genuinely unused — `grep -rn "\.Bind(" --include="*.go" internal cmd` returns nothing outside tests. Open: the `Origin` comparison is raw-string equality against an un-normalised `VIZRA_PUBLIC_ORIGIN`, and the ruling's `vizra doctor` origin-vs-reality clause is not implemented. |
| S-9 | Full error mapping; index name pinned; 23505→409 exercised | **CLOSED** | `setup.go:338-402`; `TestClaimErrorMapping` + `TestNoClaimErrorMapsToAnUnhandledFiveHundred` `setup_test.go:131,163`; `TestOwnerIndexNameMatchesTheMapper` `integration:505`; `TestOwnerInsertConflictMapsTo409NotFiveHundred` `:1238`. |
| S-10 | Injectable hasher; zero derivations on every non-201 path | **PARTIAL → see N-4** | Mechanism is right (`internal/credential/credential.go:68-132`, shared semaphore, `ErrBusy`→503 at `setup.go:347`). The invariant is false for one path — a *correct but dead* token — and `TestNoPasswordHashingOccursWithoutAValidToken` `:1029` does not cover it. |
| S-11 | Go validation mirrors the DDL; no input yields 5xx | **CLOSED** | `internal/ownerclaim/ownerclaim.go:64-159`; `TestValidatorsMatchTheMigration` reads the migration bytes `ownerclaim_test.go:34`; 23514 backstop `setup.go:382-389` logs the constraint name only; `TestMalformedFieldsYield400AndDoNotConsumeTheToken` `:980`. |
| S-12 | CLI refuses on a claimed instance; boot failure non-fatal; fifth 403 cause | **CLOSED** | `cmd/vizra/claimtoken.go:47-59` with the check taken **inside** the advisory lock (`ownerclaim.go:191-204`, no TOCTOU); `TestClaimTokenCLIRefusesOnAClaimedInstance` `:779`; non-fatal boot `cmd/api/main.go` + degraded readiness `internal/httpapi/probes.go:166-175` + `doctor.CheckOwnerClaim`; never-minted → same 403 `ownerclaim.go:318-321`, `TestClaimWithNoMintedTokenIsIndistinguishableFromAWrongToken` `:794`. |
| S-13 | Advisory-lock constant, no `hashtext` | **CLOSED** | `ownerclaim.go:43-54` with an ID registry comment. |
| S-14 | Enum ↔ `authz.Role` drift test | **CLOSED** | `TestUserRoleEnumOrderMatchesAuthzRanking` `integration:516`; `anonymous` deliberately absent, stated at `0005…up.sql:47-51`. |
| S-15 | Named test + mutation per invariant | **MOSTLY CLOSED** | 59 new tests; the existing contract test was widened, not weakened (`openapi_contract_test.go` keeps an exhaustive equality list). Remaining gaps are named in N-1…N-4 and in "smaller gaps" below. |

**Judgements you asked for explicitly:**

- **`Content-Type: application/json; charset=utf-8` accepted (deviation from "exactly").** *Safe, and I would keep it.* `requireJSONContentType` (`setup.go:296-310`) uses `mime.ParseMediaType` and compares only the media type, case-insensitively. I worked the parser adversarially: `application/json+x` → 415; `text/plain, application/json` → 415 (no `;`, so the whole string must be a valid token and is not); empty → 415; `application/JSON` → accepted (ParseMediaType lowercases — correct per RFC); a smuggled parameter (`; boundary=…`) changes nothing because the body is never form-parsed. It remains safe against a cross-site form POST for two independent reasons: an HTML form cannot emit a JSON content type at all, and a cross-origin `fetch` with one is preflighted and there is no CORS middleware registered. `c.Bind` is unused, so Echo's urlencoded/multipart branches are unreachable.
- **`Origin: null`** (sandboxed iframe, `data:`, some cross-origin redirects) → non-empty and unequal → 403 `origin_mismatch`. Correct.
- **Same-site subdomain** → `Sec-Fetch-Site: same-site` falls into the `default` branch → 403. Correct and deliberate.
- **Both headers absent** → allowed (`setup.go:316-332`), so curl and the CLI work. Correct.
- **Claimed-bit replica race.** Replica A caches `false` (1 s TTL, `setup.go:74-93`) while replica B completes the claim. In that window A answers 403 `instance_unclaimed` on non-allowlisted routes while `/setup/claim-status` (which reads through to the database) answers `claimed:true`. **Nothing that matters is reachable at M1-A** — there are no non-allowlisted routes — and a second owner is impossible because the claim's own `AnyUserExists` runs inside the claim transaction (`ownerclaim.go:309-315`) behind `users_one_owner`. The cache only ever learns `true` from a real observation, so it cannot open the guard early. Safe; worth re-checking when M1-B puts real routes behind the guard.
- **TTL.** `VIZRA_OWNER_CLAIM_TTL=1h` default (`keys.go:72`). Sane, and the right pairing with mint-on-demand.
- **Token lifecycle.** `crypto/rand` 32 bytes → lowercase hex (`ownerclaim.go:101-108`), SHA-256 at rest with a 32-octet CHECK (`0005:153`), `subtle.ConstantTimeCompare` (`:325`), the row's own digest passed to SQL (`:349`), expiry computed by the database (`store/queries/owner_claim.sql:30,78`). `vizra claim-token` writes the token to stdout and explanation to stderr (`claimtoken.go:64-71`) — never through slog.
- **Secret handling across every early return.** I traced all of them. No path formats the token, the password, the email or the DSN into a response body, header, audit row, error string or panic. `ValidationError.Error()` is field+prose (`ownerclaim.go:98`); the 23514 log line carries only `ConstraintName`; `pgconn.PgError.Error()` omits `Detail`, so no "failing row contains …" reaches a log. `TestOwnerClaimAuditEventsCarryNoSecretMaterial` `:595` scrapes token, password, **email** and `argon2id` out of every row.
- **Timing across the five 403 causes.** Status code, application code and message are byte-identical for all five (`ownerclaim.go:80-84`, `setup.go:404-431`). *Latency* is not uniform: a malformed shape returns before `BeginTx` (no database round trip); a correct-but-dead token costs an extra argon2id derivation. Neither leaks anything to an attacker who does not already hold the value — the shape is public and a dead token is already theirs — so I am not asking for uniform timing. The derivation itself is N-4.

---

## BLOCKING-BEFORE-MERGE

```
FINDING N-1: the already-claimed 409 writes one permanent audit row per anonymous request, forever
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:338-342 (ErrAlreadyClaimed -> recordClaimRefusal -> 409)
             internal/httpapi/setup_limits.go:59-72 (claimHardCeiling = 600 / 15 min, the ONLY bound)
             internal/httpapi/setup.go:100-107 (POST /api/v1/setup/claim-owner is unconditionally allowlisted)
             migrations/0005_users_credentials_owner_claim.up.sql:169-191 (UPDATE, DELETE and TRUNCATE all refused)
  requirements: VZ-INSTALL-003; chair ruling row 4 and the S-5 adoption line

Observed:
  The ruling the builder implemented for the 429 path states the principle exactly:
  "the limiter must bound writes into an undeletable table, not cause them"
  (commit message; setup_limits.go:101-110). It is implemented for 429 — no row, and
  exactly one `rate_limited` row per bucket per window through claimLimitTransition.
  The sibling path did not get the same treatment. On a CLAIMED instance every
  POST to the claim endpoint runs:
    allowClaimRequest -> content type -> body -> decode -> origin -> BeginTx ->
    AnyUserExists -> ErrAlreadyClaimed -> recordClaimRefusal (a SECOND transaction,
    one INSERT into audit_events) -> 409.
  The only bound is the 600-per-15-minute hard ceiling.

Failure:
  Every claimed instance — i.e. every production instance, for the rest of its life —
  exposes an unauthenticated endpoint that converts a request into a permanent row in
  a table this very migration makes undeletable: no DELETE, no UPDATE, no TRUNCATE, and
  the retention path is explicitly still owed (0005 header, lines 42-45). 600 rows per
  15 minutes is 57,600 rows a day, ~21 million a year, plus two database transactions
  per request. The rows carry no information after the first: "this instance is
  claimed" is permanent and identical every time. The operator's only recovery is the
  one the migration forbids.

  This is the same class the council already ruled BLOCKER, on the neighbouring branch.
  I am calling it blocking rather than a follow-up for one reason: the merge is what
  freezes the trigger that makes the rows undeletable, and the fix is six lines of code
  that already exist in the same file.

Perspective: operator (disk, and a trail they cannot prune), instance-admin (real events buried)

Recommendation:
  Do not audit `already_claimed` per request. Either drop the row entirely — a returning
  operator hitting the claim page is not a security event — or gate it exactly as the
  429 path is gated: `if s.claimLimitTransition(c) { s.recordClaimRefusal(...) }`, one row
  per bucket per window. The 409 status, code and message must not change.

Acceptance criteria:
  N POSTs to the claim endpoint on a claimed instance produce at most one
  `setup.owner_claim.refused` row per window, whatever N is. The 409 body is unchanged.

Tests:
  `TestRepeatedClaimsOnAClaimedInstanceDoNotGrowTheAuditTable` (integration, beside
  TestARateLimitedClaimWritesNoAuditRow at owner_claim_test.go:1152 — same shape:
  fire 60, assert count(*) <= 1). Mutation: remove the transition gate -> red.

Cross-repo implications: core | user: none | search: none | meta: none

Challenge:
  "It is bounded by the ceiling, so it is not unbounded." It is bounded per window and
  unbounded over time, into storage that cannot be reclaimed. The 429 path is bounded
  per window too, and the council ruled that insufficient there for the same reason.
```

---

## REQUIRED (this PR preferred — none of these freezes, all are small)

```
FINDING N-2: the claim-status endpoint bypasses the monotonic cache and the hard ceiling, and a comment says otherwise
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:192-200 (handleClaimStatus calls lookupClaimed, not instanceClaimed)
             internal/httpapi/setup.go:144-166 (instanceClaimed is the cache-aware path)
             internal/httpapi/setup_limits.go:59-61 ("applies the hard ceiling to EVERY request to the setup routes")
             internal/httpapi/setup.go:226 (allowClaimRequest is called ONLY from handleClaimOwner)
  requirements: VZ-INSTALL-003; chair adoption line S-4 ("claimed bit cached permanently once true")

Observed:
  `GET /api/v1/setup/claim-status` is allowlisted unconditionally, is never rate limited,
  and executes `SELECT EXISTS (SELECT 1 FROM users)` on every request for the life of the
  instance. It writes the cache (setup.go:198) but never reads it. The comment at
  setup_limits.go:59-61 asserts a coverage the code does not have — and this repository's
  own standard (0003's header: "a header that promises a control the table does not have
  is worse than no header") is the reason I am filing that half.

Failure:
  An anonymous caller can hold a connection-pool's worth of database round trips with a
  plain GET flood, on a route with `Cache-Control: no-store` (middleware.go:117) so nothing
  upstream absorbs it. Post-claim the answer is a constant, so the work is pure waste.

Perspective: visitor/operator (availability)

Recommendation:
  Two lines: call `s.instanceClaimed(c)` in handleClaimStatus, and call
  `s.allowClaimRequest(c)` at the top of it. Then fix the comment, or delete it.

Acceptance criteria:
  After one observed `claimed:true`, further GETs perform no database query. A GET flood
  past the ceiling answers 429.

Tests:
  `TestClaimStatusIsServedFromTheMonotonicCacheOnceClaimed` (unit, counter on
  Deps.InstanceClaimed — the seam already exists), `TestClaimStatusIsBoundedByTheHardCeiling`.

Cross-repo implications: core | user: the claim page polls this endpoint — a 429 must be
  tolerated by whatever `vizra-user` writes
Challenge: "It is one cheap indexed read." It is one per request, unlimited, from anyone,
  forever, on the only unauthenticated read surface the product has.
```

```
FINDING N-3: the Origin check compares raw strings against a value config permits with a trailing slash
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:316-324 (`origin != want`, want = Config.PublicOrigin verbatim)
             internal/config/config.go:285-294 (validation ACCEPTS u.Path == "/" and stores the raw string)
             internal/doctor/doctor.go (no public-origin check exists)
  requirements: VZ-INSTALL-003; chair adoption line S-8, final clause

Observed:
  `VIZRA_PUBLIC_ORIGIN=https://photos.example.org/` passes validation — config.go:290
  rejects only a path that is neither "" nor "/" — and is stored with the slash. Browsers
  never send a trailing slash in `Origin`. The same applies to `HTTPS://Photos.Example.org`
  (url.Parse lowercases u.Scheme for validation, but Config.PublicOrigin keeps the raw text)
  and to an explicit default port (`https://example.com:443` vs the browser's
  `https://example.com`). IDN: a host written in Unicode never equals the browser's
  A-label form. The ruling's `vizra doctor` origin-vs-reality check was not implemented.

Failure:
  A single trailing slash in `.env` turns every browser claim into 403 `origin_mismatch`
  while curl still works, on the one endpoint an operator cannot skip, with no boot-time
  signal. It is recoverable — the distinct code and the CLI path are exactly the mitigations
  I asked for, and they work — but the operator has to find them.

Perspective: operator

Recommendation:
  Compare normalised origins, not strings: parse both, compare lowercased scheme,
  lowercased host (ASCII/punycode, trailing dot stripped) and port with the default elided.
  Simplest equivalent: normalise once in config.LoadFrom and compare against a normalised
  request Origin. Add the doctor check the ruling names (configured origin vs the Host the
  probe actually reached), and consider refusing a trailing slash at boot outright — a
  boot refusal an operator reads beats a 403 they have to diagnose.

Acceptance criteria:
  A configured origin with a trailing slash, an uppercase host, or an explicit default port
  accepts the browser's Origin for the same site. A genuinely cross-origin request is still
  403 `origin_mismatch`.

Tests:
  Table case in `TestClaimAcceptsTheConfiguredOrigin` (owner_claim_test.go:964) over
  `https://h/`, `HTTPS://H`, `https://h:443` vs `Origin: https://h`; plus the existing
  cross-origin case must stay red-on-mutation.

Cross-repo implications: core | meta: the installer must not write a trailing slash
Challenge: "Operators should write it correctly." They will not, and `.env.example` is the
  only thing telling them; the endpoint that breaks is the first one they touch.
```

```
FINDING N-4: a correct-but-dead token still triggers an argon2id derivation, so "zero derivations on every non-201 path" is false and untested
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/ownerclaim/ownerclaim.go:317-335 (GetOwnerClaimToken -> compare -> Hash)
             store/queries/owner_claim.sql:24-32 (the query already RETURNS a `live` column)
             internal/integration/owner_claim_test.go:1029-1051 (covers wrong token and 409 only)
  requirements: chair adoption line S-10 ("ZERO derivations on every non-201 path")

Observed:
  `GetOwnerClaimToken` returns the row whatever its terminal state, and the handler compares
  the digest and then hashes. Liveness is enforced only afterwards, by the redeem CTE's
  guard (`consumed_at IS NULL AND superseded_at IS NULL AND expires_at > now()`), which
  returns no row -> pgx.ErrNoRows -> 403. So an expired, consumed or superseded token that
  is otherwise CORRECT costs a full 19 MiB / ~26 ms derivation before it is refused. The
  `live` flag needed to avoid this is already selected and already used by State().

Failure:
  (a) The invariant the AGENTS.md table and the PR body now assert is not true on that path,
      and no test would go red — the exact "narrated, not asserted" shape this slice exists
      to eliminate. (b) A small amplifier for someone holding a dead token (a superseded one
      after an operator re-mint, or one recovered from a log under the `stderr` opt-in):
      bounded to 60 derivations per 15 minutes by the failure limiter and to 4 concurrent by
      the semaphore, so the availability impact is minor. (c) A ~26 ms timing shoulder that
      confirms "this value was once real" — to someone who already has it.

Perspective: operator (availability), developer (a false invariant)

Recommendation:
  After the constant-time compare and before `hasher.Hash`, refuse when the row is not live,
  returning the same ErrTokenNotAccepted so nothing about the response changes.
  Three lines; `row.Live` is already in hand.

Acceptance criteria:
  A correct-but-expired and a correct-but-superseded token each return the identical 403
  and leave `Derivations()` at zero. The only path that may hash and then lose is the true
  concurrent race.

Tests:
  Extend TestNoPasswordHashingOccursWithoutAValidToken with the expired and superseded
  cases (both fixtures already exist at owner_claim_test.go:658-685). Mutation: remove the
  liveness pre-check -> red.

Cross-repo implications: core; M1-B inherits the ordering for sign-in | user: none
Challenge: "The CTE guard is the real enforcement and it is correct." It is — this is about
  the cost incurred before it, and about an invariant that is currently asserted in prose.
```

---

## REQUIRED-FOLLOW-UP (with the slice)

```
FINDING N-5: two replicas booting with the stderr opt-in both mint and both print — the ruling said otherwise
Severity:    SHOULD
Confidence:  high
Slice:       M1-A (small) or M1-B

Affected:
  repo:      vizra-core
  files:     internal/ownerclaim/announce.go:74-91 (State/liveness read OUTSIDE the lock)
             internal/ownerclaim/ownerclaim.go:184-234 (Mint takes the lock, then supersedes and mints UNCONDITIONALLY)
  requirements: chair ruling row 2 — "N replicas: under the advisory lock the first mints, the rest find a live token and print the command only"

Observed:
  Boot checks liveness before taking the advisory lock, and Mint re-checks nothing but
  `refuseIfUsersExist`. Two api replicas starting together with VIZRA_OWNER_CLAIM_ANNOUNCE=stderr
  and no live token both observe "no live token", both call Mint, and the second supersedes
  the first. The log then holds two tokens, one dead, indistinguishable to the operator.
  (The CLI's own check IS inside the lock — ownerclaim.go:191-204 — so that path is correct.)

Failure: the ruled behaviour is not implemented; an operator with replicas cannot tell which
  announced token is live, and the one they try first gets the deliberately uninformative 403.
Recommendation: move the liveness re-check inside Mint, under the lock (a `skipIfLive` flag,
  mirroring the existing `refuseIfUsersExist`), and have Boot fall back to announceCommand.
Tests: `TestConcurrentBootsMintAtMostOnce` (integration, two Boot calls in goroutines, assert
  one token printed and `generation` advanced once).
Cross-repo implications: core | meta: none
Challenge: "Multi-replica is not an M1 topology." It is not — which is why this is a follow-up
  and not a blocker — but the ruling stated the behaviour and the code differs from it.
```

```
FINDING N-6: "never mint on a claimed instance" is the one invariant in this slice enforced only in Go
Severity:    SHOULD
Confidence:  high
Slice:       M1-B

Affected:
  repo:      vizra-core
  files:     store/queries/owner_claim.sql:34-47 (MintOwnerClaimToken has no users-exist guard)
             internal/ownerclaim/ownerclaim.go:196-204 (CLI), internal/ownerclaim/announce.go:59-72 (boot)

Observed:
  The mint upsert clears consumed_at and superseded_at with no condition. No current caller
  can reach it on a claimed instance — the CLI refuses under the lock, boot branches earlier —
  so there is no live defect. But this slice's whole thesis is that invariants of this class
  belong in the database, and this one is two correct callers away from being false. A future
  owner-transfer or re-claim route is exactly where it breaks.
Recommendation: `INSERT ... SELECT ... WHERE NOT EXISTS (SELECT 1 FROM users)` (or an equivalent
  guarded upsert), so resurrecting a live owner-creating credential on a claimed instance is
  refused by the database rather than by convention.
Tests: `TestMintIsRefusedByTheDatabaseOnAClaimedInstance` (direct store call).
Cross-repo implications: core | meta: none
Challenge: "No caller can do it." Correct today; the guard costs one clause and outlives the callers.
```

```
FINDING N-7: the HTTP error handler logs err.Error() unredacted, and httpapi has no redaction-coverage test
Severity:    SHOULD
Confidence:  medium
Slice:       core hardening sweep B, or M1-B

Affected:
  repo:      vizra-core
  files:     internal/httpapi/middleware.go:154-157 (`log.Error(... "error", err.Error() ...)`) — PRE-EXISTING, not introduced here
             AGENTS.md rule "No credential, signed URL, session id or API key ever reaches a log line"

Observed:
  The worker has both a behaviour test (TestAWorkerWithAPlainHandlerLogsNoCredentials) and a
  COVERAGE test that parses worker.go and asserts all 11 error attributes are safeError(...).
  internal/httpapi has neither, and its 500 path logs the raw error. M1-A is the first slice
  whose 500 path can carry a database connection error raised while handling a credential —
  pgconn connect errors carry host, user and database (not the password, and PgError.Error()
  omits DETAIL, which is why I rate this medium rather than high).
Recommendation: wrap with obs.Redact at that call site, and add the httpapi twin of
  TestEveryErrorLogSiteInTheWorkerIsRedacted so the count cannot drift.
Tests: `TestEveryErrorLogSiteInTheAPIIsRedacted` (AST walk over internal/httpapi).
Cross-repo implications: core | meta: none
Challenge: "Nothing secret reaches it today." I could not construct a leak, which is why it is
  a follow-up — but the worker's equivalent gap was worth closing for the same reason.
```

**Smaller gaps, no separate finding:** no guard test for a non-GET method on an allowlisted path (`POST /healthz`, `GET /api/v1/setup/claim-owner`) or for `HEAD`/`OPTIONS` — while unclaimed these answer 403 rather than 405, which is fail-closed and harmless, and the shipped healthcheck uses `GET /readyz`, so there is no impact (**UNVERIFIED**: whether Echo v5 auto-registers `HEAD` for a `GET` route — I did not chase the router). The guard keys on `c.Request().URL.Path` (`setup.go:124`) rather than the matched route pattern; with `claimGuardedRoutes` empty this can only over-refuse, never under-refuse, but M1-B should revisit it when the guarded set is non-empty (`routeAttributeMiddleware`'s own comment at middleware.go:76-78 explains why `RouteInfo()` is not a drop-in there). `claimedCache.mu` is an `atomic.Int64`, not a mutex — cosmetic.

**Nothing new and unmentioned that I object to.** The additions the plan did not describe — `codedError` plumbed through `errorHandler` (middleware.go:143-151), the `setup` OpenAPI tag documenting the posture, `doctor.CheckOwnerClaim` reporting WARN-not-FAIL for an unclaimed instance and FAIL when it cannot read at all, the `audit_events_refuse_truncation` statement trigger with its `-- allow-destructive:` line, and the `users_email_fold_key` partial index anticipating VZ-AUTH-006 — are all improvements, and each carries its reason in the code.

---

BLOCKING FINDINGS OPEN AT 32b616d: N-1 (already-claimed 409 writes one permanent audit row per anonymous request; `internal/httpapi/setup.go:341`)

---

## Chair note on the security seat's re-review at `59a19c5` (2026-09-21, tick 114)

Everything the seat flagged at `32b616d` is CLOSED (N-1…N-6, S-5, S-8, S-10); the migration delta is comment-only and the frozen object did not move; the restructured claim leaks nothing new and leaves no partial state when `vizra claim-token` supersedes mid-claim; the cache-first 409 cannot be poisoned; `ErrUnavailable` cannot carry the DSN. **One NEW blocker, a regression introduced by the round:** putting `claim-status` under the hard ceiling was right, but it shares ONE counter with the POST — 600 body-less anonymous GETs exhaust the window and the operator's valid token is answered 429 for 15 minutes, repeatable at ~40 requests/minute, on the endpoint that advertises `claimed:false`. Fix: a ceiling key per route, a test that a status flood does not starve the claim (and vice versa), and a mutation collapsing the keys. Taken in the same round: NEW-4 (deny when either origin normalises to ""), and the first half of NEW-2 (log the wrapped cause of a 503 once, through `obs.Redact`, where `ErrUnavailable` is mapped). Queued: NEW-2's httpapi redaction-coverage test → core sweep B3; NEW-3 (the pool guard wants a CONCURRENCY bound, not a fixed-window count that 600 requests can trip into a 15-minute lockout) → M1-B, with the number and the accepted residual recorded on VZ-INSTALL-003 meanwhile. Consolidated with the backend seat's NEW-1 (the same endpoint's undeclared 429 in the OpenAPI contract) and the verifier's verdict as fix round 2 of 2. The seat's re-review follows verbatim.

---

# Re-review at `59a19c5`

**Date:** 2026-09-21 · **Head:** `59a19c5cc7eeef4154c5e39b6d13ab84f60b5290` (confirmed; worktree clean, one commit on `32b616d`, no force-push) · Read-only. I verified the migration delta is **comment-only** — `git diff 32b616d 59a19c5 -- migrations/` contains no DDL line, only the ASCII-username rationale block and the two re-pinned manifest digests. The frozen object did not move.

## Status per finding

| # | Status at 59a19c5 | Reason (file:line) |
|---|---|---|
| **N-1** — per-request `already_claimed` audit row | **CLOSED** | Row removed; the monotonic cache short-circuits 409 before the pool is touched — `internal/httpapi/setup.go:241-256` (cache-first 409), `:375-380` (`ErrAlreadyClaimed` now only sets the bit, no `recordClaimRefusal`). `TestRepeatedClaimsOnAClaimedInstanceDoNotGrowTheAuditTrail` `internal/integration/owner_claim_test.go:1584`. The authoritative in-transaction gate stays (`internal/ownerclaim/ownerclaim.go:441-448`). |
| **N-2** — claim-status bypassed the cache and the ceiling | **CLOSED (with a regression, see NEW-1)** | `setup.go:194-206`: now `allowClaimRequest` + `instanceClaimed`; comment corrected at `internal/httpapi/setup_limits.go:59-69`. `TestClaimStatusIsServedFromTheMonotonicCacheOnceClaimed` `:1839`, `TestClaimStatusIsBoundedByTheHardCeiling` `:1872`. |
| **N-3** — raw-string Origin comparison | **CLOSED** | `internal/config/origin.go:36-85` (case, trailing slash, trailing dot, default port, IPv6 literal bracketing; `""` for path/query/fragment/userinfo/non-ASCII); normalised once at load and **stored** `internal/config/config.go:294-304`; non-ASCII is a boot refusal whose message names a generic punycode example and **does not echo the configured value** (`config.go:297`); `setup.go:345-352` compares values; `vizra doctor` check `internal/doctor/doctor.go:356-386`. Five tests in `internal/config/origin_test.go` including the userinfo, query, fragment and non-ASCII negatives at `:68-83`. |
| **N-4** — correct-but-dead token bought a derivation | **CLOSED** | Liveness pre-check on the column the query already returns — `ownerclaim.go:408-419`, returning the same `ErrTokenNotAccepted`. `TestACorrectButDeadTokenCostsNoDerivation` `:1124`. |
| **N-5** — boot read liveness outside the advisory lock | **CLOSED** | Every decision now inside the lock — `ownerclaim.go:222-251` (`onlyIfNoLiveToken`, `ErrLiveTokenExists`); `announce.go:75-95` announces the command with the live generation instead of minting. `TestConcurrentBootsMintExactlyOneToken` `:1671`, forced deterministically with a third connection holding the lock. |
| **N-6** — mint guard was application-only | **CLOSED** | `store/queries/owner_claim.sql:36-39` — `INSERT … SELECT … WHERE NOT EXISTS (SELECT 1 FROM users)`, so a claimed instance yields `ErrNoRows` → `ErrHasUsers` (`ownerclaim.go:277-284`). `TestMintIsRefusedByTheDatabaseOnAClaimedInstance` `:1748`. |
| **N-7** — `errorHandler` logs `err.Error()` unredacted | **PARTIAL** | Improved by accident and regressed in one way — see NEW-2. `internal/httpapi/middleware.go:154-157` is unchanged. |
| **S-5** — anonymous input is not an unbounded writer into the undeletable table | **CLOSED** | Both sibling paths now hold: 429 writes nothing per request and one row per bucket per window (`setup.go:436-448`); 409 writes nothing (`:375-380`). |
| **S-8** — request posture | **CLOSED** | Content type, `MaxBytesReader`, `DisallowUnknownFields`, `dec.More()`, origin posture and the doctor clause all present (`setup.go:249-289`, `:325-362`; `doctor.go:356-386`). `c.Bind` still unused anywhere. |
| **S-10** — zero derivations on every non-201 path | **CLOSED** | Read phase / write phase split (`ownerclaim.go:360-470`); the one real exception is now stated rather than implied, in `AGENTS.md` and in the code. |

**Nothing I flagged is still OPEN.** Two new items below, one of which I am calling blocking because this round introduced it.

---

## What the restructure changed from the attacker's side

I re-walked the whole path. Answers to the specific questions:

- **Read phase outside a transaction — can anything be learned or amplified?** No new information. A wrong token now returns after two pooled reads with no hash; a *correct but dead* token returns at the same point (`ownerclaim.go:415-419`), so the ~26 ms shoulder I flagged at `32b616d` is gone and the five 403 causes are now close to indistinguishable in latency as well as in status, code and message. The only remaining timing divergence is "correct **and live**" (which then hashes) — and that is knowable from the 201. A stale read cannot do harm: the authoritative `AnyUserExists` re-runs inside the transaction (`:441-448`), the redeem CTE re-matches the digest against the **committed** row under READ COMMITTED, and `users_one_owner` is the final arbiter.
- **Two holders of the valid token both hashing.** Bounded: `credential.Argon2id.sem` at `DefaultConcurrency()` = min(GOMAXPROCS, 4), waiters honour the request context and fail `ErrBusy` → 503 (`internal/credential/credential.go:111-129`, `setup.go:386-388`). Peak transient ≈ 76 MiB. No pooled connection is held during the derivation any more, which removes the worse version of this (idle-in-transaction pool exhaustion).
- **A claimant that passes the read phase while `vizra claim-token` supersedes.** Traced: the CLI's `Mint` overwrites `token_sha256` in place, so the in-flight claimant's `row.TokenSha256` no longer matches the committed row; the redeem CTE's `token_sha256 = $1` predicate matches nothing → empty CTE → `owner` selects from nothing → no rows → `pgx.ErrNoRows` → `LiveOwnerExists` false → uniform 403. The transaction rolls back with **no partial state** — no user, no orphan credential, token not consumed. Correct.
- **Cache-first 409 — can it deny a claim, or let a request through?** No, in both directions. `claimedCache.get` returns `true` only from `claimed.Load()` (`setup.go:76-85`), and `set(true, …)` is reachable only from a real observation that users exist (201, `ErrAlreadyClaimed`, 23505 on `users_one_owner`, `LiveOwnerExists` true, or a real status lookup). There is no path that sets it from attacker input, so a false 409 on an unclaimed instance is unreachable. The reverse is harmless: a cold or stale-`false` cache merely lets the request proceed to `Claim`, whose read-phase and in-transaction gates both answer 409.
- **Origin normalisation edge cases.** userinfo, query, fragment and a path all normalise to `""` and are therefore **boot refusals** (`config.go:294-297`) rather than silently-unmatchable values; `https://h:443` ≡ `https://h`; `http://h:8080` keeps its port; IPv6 literals round-trip with brackets; a trailing dot is stripped; a wildcard host normalises to something no browser can send. The boot-refusal message names a generic `xn--` example and never the operator's value.
- **Does an `ErrUnavailable` `%v` leak the DSN?** No. `unavailable` (`ownerclaim.go:114-120`) formats the driver error, but pgconn already redacts: `ParseConfigError` runs `redactPW` (`pgx/v5@v5.11.0/pgconn/errors.go:143,236`) and `connectError`'s prefix is `failed to connect to \`user=%s database=%s\`` (`errors.go:68`) — no password, no host. And the 503 body is a fixed string (`setup.go:390-396`); the cause never reaches the client.
- **No new logging or printing of secrets.** The diff introduces **zero** new `Logger`/`Fprint` sites in product code (only in `demonstrate.sh` mutations).

---

## BLOCKING-BEFORE-MERGE

```
FINDING NEW-1: the claim-status GET now shares one hard-ceiling bucket with the POST, so a trivial anonymous GET flood denies the operator's claim
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup_limits.go:70-77 — a single key, st.CacheKey("rl","setup.claim","ceiling"), limit 600, window 15m
             internal/httpapi/setup.go:194-200 (handleClaimStatus now calls allowClaimRequest)
             internal/httpapi/setup.go:236-240 (handleClaimOwner calls the same)
             internal/integration/owner_claim_test.go:1872 (TestClaimStatusIsBoundedByTheHardCeiling trips it in 700 GETs and stops there)
  requirements: VZ-INSTALL-003; chair adoption line S-7 — "a request with the valid token is never answered 429 by the failure limiter"

Observed:
  At 32b616d only the POST consumed the ceiling. This round — correctly — put the GET
  under it too, but through the SAME counter. A GET needs no body, no content type, no
  origin header and no token. 600 of them in a few seconds exhaust the shared window, and
  for the remainder of those 15 minutes the operator's POST carrying the correct token is
  answered 429 before it is ever parsed (setup.go:236 runs first). Repeat indefinitely at
  ~40 requests/minute.
  `claim-status` is also the endpoint that advertises `claimed:false`, so a scanner already
  has both the target list and the cheapest possible way to hold every unclaimed instance
  shut.

Failure:
  Denial of claim by an unauthenticated stranger — the exact failure the failure-keyed
  limiter was adopted to remove — reachable more cheaply than before this round, and only
  during the unclaimed window, which is the one window where it matters. It is not a data
  or privacy failure: nothing is lost or exposed, and the endpoint recovers when the window
  rolls. But an operator has no application-level workaround, and the 429 is
  indistinguishable to them from legitimate load.

  I am calling it blocking because it is a REGRESSION this round introduced, not the ruled
  trade being re-litigated: the ruling said the ceiling may refuse a valid token; it never
  said status polling should compete for the operator's budget. (For the record, the
  broader "600 in a fixed window is deliberately trippable by anyone" was already true for
  POSTs at 32b616d and I did not raise it — that half is NEW-3 below, and mine to own.)

Perspective: operator (cannot claim a new instance), business (a scanner-visible first-run failure)

Recommendation:
  Split the bucket: a separate ceiling key per route (…"ceiling.status" and …"ceiling.claim"),
  so a GET flood cannot consume the POST's budget. Three lines and one constant.
  Optionally raise the status ceiling, since after N-2 a claimed instance serves it from
  memory and an unclaimed one performs one trivial read.

Acceptance criteria:
  After exhausting the status ceiling, a POST carrying the valid token still succeeds.
  After exhausting the POST ceiling, claim-status still answers.

Tests:
  `TestAStatusFloodDoesNotStarveTheClaim` (integration: drive claim-status past its ceiling,
  then claim with a valid token -> 201). Extend TestClaimStatusIsBoundedByTheHardCeiling to
  assert the POST is unaffected. Mutation: collapse the two keys back into one -> red.

Cross-repo implications: core | user: if the claim page polls claim-status, its interval must
  be stated so the status ceiling can be chosen against it | search: none | meta: none

Challenge:
  "The ceiling's trade was ruled and stated." It was — for the POST. Nothing ruled that the
  read surface and the write surface share one counter, and the code's own comment
  ("BOTH setup routes call it — which is what the name claims") reads as if sharing were the
  intent rather than a side effect.
```

---

## FOLLOW-UPS

```
FINDING NEW-2: the 503 path now discards the cause, and the 500 path still logs it unredacted
Severity:    SHOULD
Confidence:  high
Slice:       M1-B, or core hardening sweep B

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:390-396 (ErrUnavailable -> codedError with a canned message; the wrapped cause is dropped)
             internal/httpapi/middleware.go:143-157 (a codedError >= 500 logs ce.Error(), i.e. the canned text; a non-coded 500 logs err.Error() raw, unredacted)
  requirements: AGENTS.md "No credential ... ever reaches a log line"; ADR-003 503-not-401

Observed:
  ErrUnavailable is the right fix for F1 and closes the contract gap. Its side effect is that
  a database outage on the claim endpoint now produces a 503 whose ONLY log line is
  "the instance state could not be read" — the pgconn cause is never written anywhere. That
  is a diagnostic regression on the one endpoint an operator cannot skip (readiness and
  doctor still cover it, which is why this is a SHOULD).
  The other half of my N-7 is unchanged: a genuine 500 logs err.Error() with no obs.Redact,
  and internal/httpapi still has no equivalent of the worker's
  TestEveryErrorLogSiteInTheWorkerIsRedacted coverage test. I could construct no leak —
  pgconn redacts the password and omits DETAIL — so this remains a hardening gap, not a defect.

Recommendation: log the wrapped cause once, through obs.Redact, at the point ErrUnavailable
  is mapped; and add the httpapi twin of the worker's redaction-coverage test.
Tests: `TestADatabaseOutageIsDiagnosableFromTheLog`; `TestEveryErrorLogSiteInTheAPIIsRedacted`.
Cross-repo implications: core | meta: none
Challenge: "An operator reads /readyz, not the request log." Usually — but the 503 they were
  handed carries a request id that now resolves to nothing.
```

```
FINDING NEW-3: the hard ceiling is a fixed-window count, so it is trippable on purpose; the pool it guards wants a concurrency bound
Severity:    SHOULD
Confidence:  high
Slice:       M1-B or core hardening sweep B

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup_limits.go:34-40 (claimHardCeiling = 600 / 15 min), :70-77
  requirements: chair adoption line S-7

Observed:
  The control's stated job is "keep a flood of one-row SELECTs from exhausting the connection
  pool" — a CONCURRENCY property. It is implemented as a fixed-window request count, which
  means 600 cheap requests buy a 15-minute lockout of a valid claim. This predates 59a19c5
  (it applied to POSTs at 32b616d) and I did not raise it in round 1; recording it as my miss.
Recommendation: bound in-flight setup requests with a semaphore sized to a slice of the pool,
  and keep the window counter only as a far-above-plausible backstop. A concurrency bound
  protects the pool exactly and can never lock an operator out for a fixed period.
Tests: `TestTheSetupPoolGuardIsAConcurrencyBoundNotALockout`.
Cross-repo implications: core | meta: if the chair prefers to keep the window, record the
  number and the accepted residual on VZ-INSTALL-003 rather than leaving it in a comment.
Challenge: "A flood past it is a network-level DoS anyway." 600 requests in 15 minutes is not
  a flood; it is a cron job.
```

```
FINDING NEW-4: checkOrigin would match on two unnormalisable values — unreachable today, one line to make impossible
Severity:    NIT
Confidence:  high
Slice:       M1-B

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:345-352 (`NormalizeOrigin(origin) != NormalizeOrigin(want)`)
             internal/config/origin.go:34-35 (the doc comment asserts a caller "can never match on
             'both were unparseable'" — that property comes from the BOOT REFUSAL, not from this code)

Observed:
  If Config.PublicOrigin ever normalised to "", an `Origin: null` request (which also
  normalises to "") would pass the check. In production it cannot: LoadFrom refuses such a
  value at boot (config.go:294-297) and stores the normalised form, and
  TestProductionRefusesAnOriginItCannotCompare pins that. So this is unreachable — but the
  comparison itself is fail-open, and a hand-built Deps.Config in a future test or tool would
  reach it.
Recommendation: deny when either side normalises to "". One line, and it makes the doc
  comment true of the code rather than of a neighbouring package.
Tests: add `Origin: null` against an empty configured origin to TestOriginsAreComparedNormalisedNotAsStrings.
Cross-repo implications: none
Challenge: "It is unreachable." It is — which is why this is a NIT and not a finding I would
  hold a merge for.
```

**Residual I accept without a finding, recorded so it is not rediscovered:** `MintOwnerClaimToken`'s `WHERE NOT EXISTS (SELECT 1 FROM users)` is evaluated at statement snapshot under READ COMMITTED, so an operator running `vizra claim-token` at the exact instant a claim commits can leave a live token row on a now-claimed instance. It is inert — the claim gate is `EXISTS(users)`, checked before the token is ever read — and the next boot supersedes it (`announce.go:63-72`). Closing it would need SERIALIZABLE or a lock on `users`; not worth it.

**New things this round introduced that I have no objection to:** the ASCII-username rationale frozen into 0005's header (comment-only, and the homograph reasoning is correct for a URL-bearing handle); `ErrLiveTokenExists` and the `superseded` audit row on re-mint; the `superseded_at` predicate kept and labelled as defence-in-depth with an accurate note that it is unreachable today; `TestUsersOneOwnerFiresThroughTheHandler`'s uncommitted-blocker technique; the CLI driven as a real binary; and the three AGENTS.md rows rewritten to what is true rather than to what was aimed at — including the honest "one exception" on the zero-derivations claim. The round also reported a defect in its own evidence (`TestNoConnectionIsHeldWhileHashing` watched the wrong pool) and declared two mutations review-only with the measurement rather than dropping them. That is the behaviour this process is for.

---

BLOCKING FINDINGS OPEN AT 59a19c5: NEW-1 (claim-status and claim-owner share one hard-ceiling bucket, so an anonymous GET flood answers the operator's valid token 429; `internal/httpapi/setup_limits.go:70-77`)
