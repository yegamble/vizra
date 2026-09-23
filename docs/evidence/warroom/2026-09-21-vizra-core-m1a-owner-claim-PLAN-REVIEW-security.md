# vizra-core M1-A (owner claim, VZ-INSTALL-003) — PLAN review by the `vizra-security` seat

- **Reviewed:** the builder's phase-1 plan `docs/plans/2026-09-21-vizra-core-m1a-owner-claim.md` (no code exists yet), against vizra-core `main@4a80a1e`
- **Reviewer:** `vizra-security` council seat (agent `a95ace2c4cf1ebf0d`), read-only
- **Date:** 2026-09-21
- **Kind:** specialist review of a PLAN before code. Not a verifier verdict. The backend seat's review is `…-PLAN-REVIEW-backend.md`; the chair's consolidated rulings are `…-PLAN-RULINGS.md`.

The seat's report follows verbatim.

---

Read: the plan (all 11 sections), `AGENTS.md` (meta + `vizra-core`), ADR-003, ADR-007, `VZ-INSTALL-003`, and the base tree at `4a80a1e` in `/Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim` (migrations 0001/0003, `internal/httpapi`, `internal/cache`, `internal/site`, `internal/config`, `internal/authz`, `Dockerfile`), plus Echo v5.3.1 and Go `net/netip` sources in the module/GOROOT cache. Read-only throughout; no scratch files created.

This is a good plan — better than most code. Almost everything below is about the parts that freeze.

---

# BLOCKING-BEFORE-CODE

```
FINDING 1: the ip_prefix writer can abort the claim transaction and leave the instance permanently unclaimable
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0003_audit_events.up.sql:84-99 (frozen CHECK + the writer's contract)
             plan §3.6 ("The audit event is inserted in the SAME explicit transaction"), §5.4
             GOROOT/src/net/netip/netip.go:676-696 (Addr.Prefix), :1303-1312 (PrefixFrom → withoutZone), :1591-1595 (Prefix.String)
  requirements: VZ-INSTALL-003 (recovery), VZ-AUDIT/0003 deferred obligation

Observed:
  The frozen CHECK accepts IPv6 only as `^[0-9a-f]{1,4}(:[0-9a-f]{1,4}){0,3}::(/(48|64))?$` —
  at least one hex group before `::`. 0003's header states plainly: "'::' ... [is] refused".
  The natural writer (`netip.ParseAddr` → `Unmap()` → `Prefix(64)` → `String()`) produces
  exactly `::/64` for `::1` and for `::`, and `netip.Prefix.String()` returns the literal
  string `"invalid Prefix"` for the zero Prefix, which `Addr.Prefix` returns for the zero Addr.
  Both values violate the CHECK. The plan puts the `succeeded` audit INSERT inside the same
  transaction as the redeem+owner+credential statement, "which is also required for
  correctness" (§3.6).

Failure:
  A claim submitted over IPv6 loopback — the operator on the host, `curl -6`, a sidecar,
  an IPv6-loopback proxy, or the integration harness — raises 23514 on the audit INSERT,
  which aborts the whole transaction. The owner is not created, the token is not consumed,
  and the client gets a 500. The operator retries from the same address and fails again,
  forever: the instance cannot be claimed at all. Same outcome for any input that reaches
  the writer as a zero Addr.

Perspective: operator (cannot claim), instance-admin (audit trail silently unwritable)

Recommendation:
  1. The masking function is TOTAL by construction: it validates its own output against the
     frozen grammar before returning and returns NULL on any mismatch; it returns NULL for
     the unspecified and loopback addresses and for any parse failure, rather than emitting
     `::/64`. NULL is what 0003's contract already prescribes for "no usable address".
  2. Belt as well as braces: Go-side validation of the produced string against the same
     regex immediately before the INSERT, so no audit row can ever abort a claim.
  Do not solve this with a SAVEPOINT that swallows audit failures — that trades an
  unclaimable instance for an unaudited claim.

Acceptance criteria:
  A claim from `::1`, from `::`, from `fe80::1%eth0`, from an IPv4-mapped `::ffff:127.0.0.1`,
  and from a caller whose address cannot be parsed all yield 201 with the audit row written
  and `ip_prefix` either a legal prefix or NULL. No input to the writer, of any shape, can
  produce a string the 0003 CHECK refuses.

Tests:
  `TestIPPrefixWriterOutputAlwaysSatisfiesTheFrozenCheck` (unit, table + the 0003 regex
  compiled from the migration file's own bytes — the repo idiom, cf.
  TestTheContractAndTheLoaderNameTheSameVariable reading the contract's bytes), and an
  integration case `TestOwnerClaimSucceedsFromIPv6Loopback`. Neither exists in the plan's
  test list; #15 tests only the three happy shapes named in the 0003 header.

Cross-repo implications: core: yes | user: none | search: none | meta: none

Challenge:
  "Nobody claims over ::1." They do — `docker compose exec`-adjacent curl, host-network
  testing, and any harness that dials `[::1]:8080`. And the cost of the fix is ten lines.
```

```
FINDING 2: announcing the token on stderr by default writes a live owner credential into every log pipeline
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §3.4 (Mechanism B, "default-on fallback"), §8 (`VIZRA_OWNER_CLAIM_ANNOUNCE` default `stderr`)
             Dockerfile:106,127 (cmd/vizra IS in the runtime image at /usr/local/bin/vizra)
  requirements: VZ-INSTALL-003 privacy case — "Token never appears in HTTP responses or non-local logs"

Observed:
  Docker's default json-file driver captures BOTH stdout and stderr of PID 1; every other
  driver (journald, fluentd, gelf, awslogs, splunk) does the same. An unstructured line is
  not field-extracted, but it is still stored, shipped, retained and searchable. The plan
  concedes this: "on an instance with aggregation the token does reach non-local logs — the
  privacy case's stated boundary."

Failure:
  The default configuration violates the ledger's own privacy case on any instance that
  ships logs. Two concrete amplifiers the plan does not consider:
  (a) crash loop — an api that restarts N times while unclaimed re-mints and re-prints N
      times (plan §3.1), so the log holds N tokens of which the last is LIVE, retained for
      the retention period, on a host the attacker may only need read access to;
  (b) support behaviour — `docker compose logs` output is the single most-pasted artefact
      in issue trackers, forums and chat with assistants.
  A leaked live token is a complete instance takeover: owner account, attacker's password.

Perspective: operator, instance-admin, business (a takeover reported against the default config)

Recommendation:
  Invert the default. `VIZRA_OWNER_CLAIM_ANNOUNCE=off` is the default; the boot line says
  only, on stderr:
    "This instance is unclaimed. Get a claim token: docker compose exec api vizra claim-token"
  `stderr` stays available as an explicit opt-in for a single VPS with no aggregation, with
  the template Doc string saying in terms that it writes a credential to the container log.
  `vizra doctor` prints the same command. The CLI already ships in the image, so the
  documented primary path exists today — this is the one mechanism whose output is NOT part
  of the container's captured stream.
  The consequence the builder correctly refuses to take unilaterally — PRODUCT_SPEC.md §15
  step 4 and copy key `claim.help.body` must change — is a chair/owner docs decision, and it
  is cheaper than freezing a secret-to-logs default into `.env.example` and the installer.

Acceptance criteria:
  With no configuration set, booting an unclaimed instance produces no 64-hex string on any
  stream, and the printed line names a command. With `=stderr`, the token appears exactly
  once on stderr and never through the slog handler. `vizra claim-token` works in both.

Tests:
  Extend the plan's #8 to assert the DEFAULT announce mode emits no token-shaped value on
  EITHER writer, plus `TestBootAnnouncementPrintsACommandNotACredential`, plus a config test
  that the registry default is `off` (`config-template-check` covers presence, not value).
  MUT-5 must be joined by MUT-5b: "flip the default to stderr" must turn a named test red.

Cross-repo implications: core: config key + CLI | user: none | search: none |
  meta: PRODUCT_SPEC.md §15 step 4, the approved copy key, README/COMMANDS, installer VZ-ISSUE-004

Challenge:
  "No installer exists, so an operator who cannot find the token is stuck." They are not:
  the CLI is in the image, doctor prints the command, and the boot line prints the command.
  The failure mode of my default is one extra command; the failure mode of the plan's
  default is a retained live credential.
```

```
FINDING 3: unconditional re-mint on every boot is a denial-of-claim and a churn machine
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §3.1 (mint table, row 1), §5.2 ("Restart | Re-mint + invalidate")
  requirements: VZ-INSTALL-003 recovery case — "Restart re-mints; old token invalid"

Observed:
  Row 1 of §3.1 re-mints on EVERY boot while unclaimed, overwriting the digest and resetting
  `expires_at`. The ledger sentence it implements exists so a lost token is recoverable.

Failure:
  (a) Mid-claim DoS. The operator reads a token, opens the claim page, and anything that
      restarts the api — a compose `up -d` after an env edit, an OOM, a health-check flap,
      a watchtower-style updater, `restart: unless-stopped` plus any crash bug — silently
      invalidates the token in their clipboard. They get the uniform 403 ("mistyped, used,
      superseded, or expired"), which by design tells them nothing, and loop.
  (b) Crash-loop churn multiplies FINDING 2: each restart writes a fresh live token to the
      log stream.
  (c) An attacker who can induce a restart (even indirectly) can keep an operator from ever
      completing a claim while the endpoint stays live for whoever holds the current token.

Perspective: operator (blocked and mystified), instance-admin

Recommendation:
  Boot mints only when there is NO live token — absent, expired, consumed or superseded.
  A boot that finds a live unexpired unconsumed token leaves it alone and announces nothing
  new. `vizra claim-token` ALWAYS re-mints (supersede + mint), which is the explicit,
  operator-initiated recovery path that the ledger sentence was standing in for, and it is
  now a better one: it is deliberate rather than incidental.
  This changes the ledger's recovery wording, so it is a chair ruling, not a builder edit.
  Pair it with a shorter default TTL (below).

Acceptance criteria:
  Restarting an unclaimed instance three times does not invalidate a token the operator
  already holds. `vizra claim-token` invalidates it and returns a new one. A token can never
  outlive `expires_at`. There is no state in which an unclaimed instance can never obtain a
  live token.

Tests:
  `TestARestartDoesNotInvalidateALiveToken` (replaces the plan's #4 semantics for the
  restart case; #4 stays as the supersede-because-users-exist case),
  `TestClaimTokenCLIRemintsAndInvalidatesThePrevious`. New mutation: "re-mint
  unconditionally at boot" must turn the first red.

Cross-repo implications: core | meta: VZ-INSTALL-003 recovery sentence (chair ruling)

Challenge:
  "Restart-re-mints is the operator's remediation when a token leaks into a log." With
  FINDING 2's default (`off`), the token is not in the log; and the CLI re-mint is a
  first-class remediation that does not require a restart.
```

```
FINDING 4: `requireClaimed` as an opt-in decorator is fail-open; the ledger bullet says "every signup path"
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §1 hand-off 4, §4.3, test #19, MUT-12
             internal/httpapi/server.go:113-124 (the one place routes and middleware are registered)
             ADR-003 Consequences: "a new read surface that forgets authz.Decide fails open"
  requirements: VZ-INSTALL-003 outcome — "while unclaimed, EVERY signup path answers 403"

Observed:
  The plan ships "an exported `requireClaimed` guard plus its table test — and M1-B attaches
  it to register and login". Attachment is a thing a future author must remember. The
  repository's own house style is the opposite everywhere it matters: the OpenAPI contract is
  checked in BOTH directions, the authz matrix DENIES anything absent, `Routes()` exists
  precisely so enumeration is honest.

Failure:
  M1-B, M2 or an outside contributor adds an account-creating route (invite accept, OAuth
  callback, AT Protocol sign-up, an admin bootstrap) and forgets the decorator. The ledger
  bullet is then false and nothing goes red. This is the exact shape of bug the acceptance
  bullet exists to prevent, and it is cheapest to close now, while the route table is six
  entries long.

Perspective: operator, instance-admin, developer

Recommendation:
  Make it structural, not decorative. One server-wide middleware: while the instance is
  unclaimed, only an explicit allowlist is reachable — `/healthz`, `/readyz`, `/version`,
  `/schemaz`, the two setup operations (and, from M1-B, sign-in). Everything else 403.
  This cannot be wrong at M1-A because nothing can exist before an owner exists. Back it
  with a contract test that walks `Server.Routes()` and fails on any route that is neither
  in the allowlist nor behind the guard — the both-directions idiom the repo already uses.
  Two details that are security-relevant, not performance:
   - the claimed bit is MONOTONIC (`users_one_owner` guarantees false→true, never back), so
     cache it in-process permanently once true; an unclaimed instance may cache it for a
     bounded moment. This is what keeps the guard from adding a DB read per request forever.
   - if the claimed lookup ERRORS, the answer is 503, never 403 and never allow.

Acceptance criteria:
  Adding a route without a decision turns a named test red. An unclaimed instance answers
  403 on every non-allowlisted path including the router's 404 path. A database outage on
  the guard returns 503.

Tests:
  `TestEveryRouteIsEitherUnclaimedAllowlistedOrGuarded` (unit, over `Routes()`),
  `TestUnclaimedInstanceRefusesANonAllowlistedRoute`, `TestClaimGuardReturns503WhenTheDatabaseIsDown`.
  MUT-12 becomes "add a route without touching the allowlist" — which must turn the
  enumeration test red, a strictly stronger mutation than removing the guard.

Cross-repo implications: core | user: the claim page must tolerate 403 on everything else |
  meta: the M1-A PR can record the ledger bullet as demonstrated-at-route-level, not PARTIAL

Challenge:
  "A blanket deny is too big a hammer for M1-A." It is exactly the right size while the API
  is six routes and nothing can exist before an owner; converting it to a narrower rule later
  is a one-line allowlist edit with a test that notices.
```

```
FINDING 5: auditing rate-limited attempts makes an anonymous flood an unbounded writer into an UNDELETABLE table
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §5.3 (`setup.owner_claim.refused` with reason `rate_limited`), §2.2 (the
             immutability trigger), test #14, MUT-9
             migrations/0003_audit_events.up.sql:18-24 — "the BEFORE UPDATE OR DELETE trigger,
             AND THE AUDITED RETENTION PATH IT HAS TO COEXIST WITH, land in M1"
  requirements: VZ-INSTALL-003 negative cases

Observed:
  The audit table gains `BEFORE UPDATE OR DELETE ... FOR EACH ROW` refusing both. The plan
  writes a `refused` row for the `rate_limited` reason. A 429 is, by construction, the
  response to requests that exceed the limiter — i.e. requests with NO upper bound.

Failure:
  An unauthenticated attacker converts a request the limiter was supposed to make cheap into
  a database INSERT into a table that, after this migration, nothing in the product can ever
  delete. Disk fills; the only recoveries are TRUNCATE (permitted by the row-level trigger —
  which destroys the entire trail) or dropping the trigger. The limiter amplifies instead of
  protecting. Separately, the plan discharges the FIRST half of 0003's deferred obligation and
  freezes the second half OUT: with DELETE refused at row level and no retention path, audit
  retention becomes a schema change rather than a job.

Perspective: operator (disk, and a trail they cannot prune), instance-admin

Recommendation:
  1. A 429 writes NO audit row. At most one `setup.owner_claim.rate_limited` row per bucket
     per window, written on the transition into the limited state. Token-rejection rows stay
     — they are already bounded by the limiter.
  2. Do not freeze retention out. Either (a) the trigger refuses UPDATE always and refuses
     DELETE unless a session GUC set only by an audited retention job is present, or (b) the
     trigger stays as written and the migration header states explicitly that retention is a
     named follow-up with a ledger ID, so the next reader does not find a silent hole where
     0003 promised a pair. (a) is the honest discharge of 0003's sentence; (b) is acceptable
     only if the chair records the debt.

Acceptance criteria:
  N requests beyond the limit produce at most one audit row per window. The audit trail can
  be pruned by exactly one audited mechanism, or the absence of that mechanism is recorded on
  the ledger with an ID.

Tests:
  `TestRateLimitedClaimAttemptsDoNotGrowTheAuditTable` (integration: exceed the limit, assert
  `count(*)` unchanged past the first row), and a case for whichever retention shape is
  chosen. Neither exists today; #14 only proves UPDATE/DELETE are refused.

Cross-repo implications: core | meta: a ledger ID for audit retention if option (b)

Challenge:
  "The limiter bounds the audited path, so volume is 5760 rows/day." That is true for the
  REJECTED-token rows and false for the rate_limited rows, which by definition are the ones
  past the bound.
```

```
FINDING 6: the credentials CHECK freezes the full PHC parameter grammar, and the email fold rule is unwritten
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §2.2 — `CHECK (kind <> 'password' OR secret LIKE '$argon2id$v=19$m=%,t=%,p=%$%$%')`,
             `CONSTRAINT users_email_fold CHECK (email_fold = lower(email))`, §3.6 `lower(sqlc.arg('email'))`
  requirements: VZ-INSTALL-003, VZ-AUTH-001 (M1-B verifies against this row), ADR-003 §Credentials

Observed:
  Two frozen facts, both correct in spirit, both slightly wrong in a way only an append-only
  migration makes expensive:
  (a) The CHECK pins the algorithm id, the version AND the parameter grammar. Widening a CHECK
      requires dropping it — destructive under `migrate-lint` — so a future KDF change or a
      PHC field addition becomes a schema fight rather than a code change.
  (b) `email_fold = lower(email)` with folding done in SQL. `lower()` in PostgreSQL is
      collation/ctype dependent for non-ASCII; `strings.ToLower` in Go is not the same
      function. `username` is safe (the shape CHECK restricts it to ASCII); `email` is NOT —
      its shape CHECK is `[^[:space:]@]+@...` and accepts any UTF-8.

Failure:
  (a) The narrow CHECK is a trap the schema cannot exit additively.
  (b) M1-B writes sign-in three weeks from now. If it folds the submitted email in Go and
      looks up `email_fold`, an owner whose address contains a non-ASCII character can be
      locked out of the account this slice created — and the CHECK guarantees the row itself
      is internally consistent, so nothing looks wrong. This is a cross-slice lockout frozen
      by a migration written today.

Perspective: operator (locked out of the only privileged account), developer

Recommendation:
  (a) Loosen the stored-form CHECK to its actual job — "never a plaintext or reversible
      value": `secret LIKE '$argon2id$v=19$%'` plus the existing length bound. Assert the
      full parameter grammar (`m=19456,t=2,p=1`, 16-byte salt, 32-byte tag) in a Go test,
      which is not append-only and can move when parameters are raised.
  (b) Write the folding rule INTO the migration header, where it freezes with the constraint:
      folding is done by PostgreSQL's `lower()` in SQL, on write AND on every later lookup;
      no Go-side folding of email, ever. Add it to the plan's §1 hand-off list so M1-B
      inherits it as a contract, not as folklore.
  (c) While the header is being written: state the password normalisation decision (recommend
      NO Unicode normalisation — hash the raw UTF-8 bytes of the submitted field), because
      M1-A writes the hash and M1-B verifies it, and a silent divergence is the same lockout.
      Bound the password in BYTES (e.g. ≤ 1024 octets) as well as in characters — OpenAPI
      `maxLength: 256` counts code points, and 256 astral characters is 1 KiB.

Acceptance criteria:
  The CHECK refuses a plaintext, a bcrypt and a truncated value; a Go test pins the exact
  parameters and fails if they drift. The migration header states the email-fold rule and the
  password-normalisation rule in terms. A byte bound on the password exists server-side.

Tests:
  `TestStoredPasswordFormatIsTheFrozenArgon2idParameters` (unit),
  `TestEmailFoldIsProducedByPostgresOnEveryPath` (integration, with a non-ASCII address),
  `TestPasswordIsHashedWithoutNormalisation` (unit, byte-identity of the hashed input).

Cross-repo implications: core; M1-B (VZ-AUTH-001) inherits both rules | user: none

Challenge:
  "PostgreSQL's `lower()` is effectively ASCII-lowering for the addresses anyone uses." Often
  true, and irrelevant: the cost of writing the rule down is one paragraph, and the cost of
  being wrong is the owner account.
```

```
FINDING 7: the rate-limit design lets any anonymous caller lock the operator out of claiming, and its per-origin bucket does not exist behind a proxy
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §5.1 (10/15min per masked prefix, 60/15min global; "both must pass"), §5.4
             ("Forwarded headers are NOT trusted at M1-A ... yields NULL")
             echo/v5@v5.3.1/context.go:249-258 — RealIP falls back to RemoteAddr when no
             IPExtractor is set; server.go:104-124 sets none
             internal/cache/ratelimit.go:64-80 (fail-open + degraded)
  requirements: VZ-INSTALL-003, ADR-003 §Rate limits

Observed:
  Echo v5's default RealIP is SAFE (it does not read X-Forwarded-For) — which is the good
  news and also the problem. Behind Caddy on the compose network, `RemoteAddr` is the PROXY's
  container address. So:
   - the plan's stated behaviour, "a request carrying X-Forwarded-For with no trusted-proxy
     configuration yields NULL", is not what the mechanism produces: it produces
     `172.x.0.0/24`, a real-looking but false attribution written into an immutable table;
   - the per-origin bucket collapses to ONE bucket shared by the entire internet.
  The global bucket is 60 requests per 15 minutes for all callers, and a failed claim and a
  successful claim consume the same budget.

Failure:
  Denial of claim. An anonymous attacker sends 60 junk requests and the operator's CORRECT
  token is answered 429 for the next 15 minutes — indefinitely, at two requests per minute
  of attacker cost. Combined with FINDING 3 (restart re-mints) this becomes a loop the
  operator cannot exit. And every audit row from a proxied deployment attributes the attempt
  to the proxy, so the trail cannot distinguish the attacker from the operator.

Perspective: operator (cannot claim their own new instance), instance-admin (useless trail)

Recommendation:
  1. Limit FAILURES, not attempts. The cheap checks run first (they already do: §4.2 hashes
     only after the digest compares), and only a REJECTED attempt consumes limiter budget.
     A request presenting the correct token is never answered 429. This keeps every property
     the plan wanted — bounded volume, bounded log noise, bounded argon2 — and removes the
     lockout entirely.
  2. Keep a separate, much higher hard ceiling on total requests (protecting the pool from a
     flood of one-row SELECTs), well above any operator-plausible use.
  3. Be honest about attribution: when a forwarded header is PRESENT and no trusted-proxy
     configuration exists, `ip_prefix` is NULL and the per-origin bucket is not used — as the
     plan says it wants, but implemented against that condition rather than against RealIP.
     Do not write the proxy's private prefix into the audit table as if it were the client.
  4. The limiter's fail-open on cache outage is correct here and the plan's justification is
     right; keep it, and keep the degraded readiness signal.

Acceptance criteria:
  After N failed attempts from any number of sources, a request carrying the valid token
  still succeeds. Behind a proxy with no trusted-proxy configuration, audit rows carry NULL
  `ip_prefix`, never the proxy's address.

Tests:
  `TestAValidTokenIsNeverRateLimited` (integration: exhaust the bucket, then claim → 201),
  `TestForwardedHeaderWithoutTrustedProxyYieldsNullIPPrefix`,
  `TestRateLimitCountsFailuresNotSuccesses`. The plan's #12 asserts only that a limit exists.

Cross-repo implications: core | meta: strengthens the infra seat's open item — a
  trusted-proxy / X-Forwarded-Proto key must exist before the installer offers
  VIZRA_TLS_MODE=external (WARROOM-BOARD.md row 7, F7)

Challenge:
  "Limiting failures lets an attacker hold a DB connection per request." Bounded by (2) and
  by the pool; and a one-row indexed SELECT is cheaper than the Redis round trip the limiter
  itself costs.
```

---

# REQUIRED-IN-THIS-SLICE

```
FINDING 8: the endpoint's CSRF/content-type posture must be explicit, because today it is closed by accident
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §4.2, §9 OQ-10; ADR-003:40-51 (the request-class table)
             echo/v5@v5.3.1/bind.go:68-110 (BindBody accepts urlencoded and multipart),
             :275-283 (a field with no `form` tag is SKIPPED), :71-73 (ContentLength==0 → nil, no error)
             internal/httpapi/server.go:113-124 (no CORS middleware registered)
             internal/site/site.go:95-108 (ByHost FALLS BACK to the single site for an unknown Host — there is no Host allowlist in core)
  requirements: VZ-INSTALL-003, ADR-003 §CSRF

Observed:
  The builder's reading of OQ-10 is CORRECT and I would have reached it independently:
  ADR-003's "Setup wizard" row cites `C/internal/setupweb/guard.go`, a separate setup web
  server in Vidra; VZ-INSTALL-003's `surfaces.ui` is `/setup/claim`; and ADR-007's precedence
  names "owner claim" as one of exactly three surfaces an anonymous visitor keeps on a
  PRIVATE site — meaningless for a loopback-only route. The row does not bind
  `POST /api/v1/setup/claim-owner`.
  What that leaves is a request class ADR-003's table has NO row for: an unauthenticated
  state-changing POST whose only credential is in the body. Today three accidents close the
  browser paths: Echo skips form fields that lack a `form` tag; no CORS middleware is
  registered, so a cross-origin JSON fetch is preflight-blocked; and `text/plain` yields 415.
  None of those is a decision. `site.ByHost` explicitly does not allowlist Hosts, so DNS
  rebinding against a LAN- or loopback-bound instance is not stopped by the site middleware.

Failure:
  The residual real attack: an attacker who has the token (a shipped log, a pasted
  `docker compose logs`, a screenshot) but CANNOT reach the instance — LAN-bound, VPN-only,
  behind a firewall — drives a browser on that network to POST the claim with their own
  password. A future CORS slice, or a `form` tag added to the request struct by someone
  wiring a non-JSON client, re-opens it silently.

Perspective: operator, instance-admin

Recommendation:
  State the posture and enforce it, in ~5 lines:
   - `Content-Type` must be exactly `application/json` (415 otherwise); decode with
     `json.Decoder` + `DisallowUnknownFields` to honour the spec's `additionalProperties: false`;
     do NOT use `c.Bind`.
   - Bound the body with `http.MaxBytesReader` on `req.Body` — NOT a Content-Length check,
     which a chunked request bypasses.
   - If `Origin` is present it must equal `VIZRA_PUBLIC_ORIGIN`; if `Sec-Fetch-Site` is
     present it must be `same-origin` or `none`. Absence of BOTH is allowed, so curl and the
     CLI keep working — the token is in the body, not ambient, so ADR-003's "no ambient
     credential → allow" logic governs, and the header checks are defence in depth against a
     browser being used as a confused deputy.
   - An empty body binds nothing and must be 400 before any database read.
   - A mismatched Origin returns 403 with a DISTINCT code (e.g. `origin_mismatch`) — it is
     not a token oracle, and a misconfigured `VIZRA_PUBLIC_ORIGIN` must be diagnosable.
  `VIZRA_PUBLIC_ORIGIN` at first boot: it defaults to `http://localhost:8080` and is
  RequiredInProduction (keys.go), and production already refuses a plain-http origin unless
  `VIZRA_ALLOW_INSECURE_PUBLIC_ORIGIN` (config.go:263-264), so the TLS question for
  `VIZRA_TLS_MODE=external` is covered at boot, not at the endpoint. But a WRONG value
  bricks the claim page while curl still works — so `vizra doctor` must compare the
  configured origin against the Host it is actually reached at and say so.

Acceptance criteria:
  A urlencoded or multipart POST carrying a valid token creates no owner and returns 415.
  A JSON POST with an unknown field returns 400. A 9 KiB chunked body returns 413. A POST
  with `Origin: https://evil.example` returns 403 and creates no owner. A curl POST with no
  Origin and no Sec-Fetch-Site succeeds. The chair records the OQ-10 interpretation.

Tests:
  `TestClaimRefusesANonJSONContentType`, `TestClaimRefusesAnUnknownField`,
  `TestClaimRefusesACrossOriginRequest`, `TestClaimAcceptsAHeaderlessCLIRequest`,
  `TestClaimBodyLimitAppliesToAChunkedRequest` (the plan's #13 does not distinguish
  Content-Length from streamed bytes). New mutation: "use c.Bind instead of the strict
  decoder" must turn the first two red.

Cross-repo implications: core | user: the claim form must send JSON and same-origin |
  meta: ADR-003's table has no row for this class — see the OQ-10 ruling below

Challenge:
  "It's already closed, so this is ceremony." It is closed by three coincidences in a
  third-party binder and a not-yet-written CORS slice. Five lines make it a decision.
```

```
FINDING 9: the index name is inconsistent between the DDL and the evidence, and 23505 → 409 has no test
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §2.2 (`CREATE UNIQUE INDEX users_one_owner ...`) vs §7.1 (transcript:
             `violates unique constraint "users_one_owner_idx"`), §7.8 (attribution via
             `pgconn.PgError.ConstraintName`), §5.2 loser mapping, test #2, #11, MUT-2
  requirements: VZ-INSTALL-003 negative case — "race between two claimers yields one owner"

Observed:
  The DDL names the index `users_one_owner`; PostgreSQL would report exactly that name. The
  phase-1 transcript reports `users_one_owner_idx`. One of the two is not what phase 2 will
  build. The handler plans to map 23505 to 409 by matching `ConstraintName`.
  Separately, the builder honestly records that MUT-2 (dropping the index) leaves test #2
  GREEN — the row guard alone wins the HTTP race. The converse is the untested half: there
  is NO test in which `users_one_owner` actually FIRES through the handler, so nothing
  proves 23505 maps to 409 rather than to a 500.

Failure:
  A name mismatch in a string comparison turns the one path the index exists for into an
  unhandled 500, on the exact race the ledger's negative case names. The plan's #2 asserts
  "zero 5xx" but never reaches that branch.

Perspective: operator, developer

Recommendation:
  Pin the name from the live database (phase 2 reads `pg_indexes` and the test asserts the
  name), and add a test that forces the index to fire through the HTTP handler — insert an
  owner out of band, then claim with a valid token — asserting 409, no 5xx, no partial state
  (no orphan `credentials` row, token not consumed). That path also exists in reality: an
  owner created out of band leaves a LIVE token until the next boot supersedes it (§3.1),
  which is a window the plan does not test.

Acceptance criteria:
  `TestOwnerInsertConflictMapsTo409` passes; renaming the index turns it red; no 5xx on any
  concurrent or out-of-band ordering.

Tests:
  `TestOwnerInsertConflictMapsTo409NotFiveHundred` (integration),
  `TestALiveTokenAgainstAnOutOfBandOwnerIsRefused`.

Cross-repo implications: core | user: none
Challenge: "The guard makes 23505 unreachable." Only until someone edits the CTE — which is
  precisely MUT-1, an acknowledged mutation.
```

```
FINDING 10: "cheap check first" is asserted but not enforceable, and the hasher semaphore is not a shared seam
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §4.2 ("the password is hashed only after the token comparison succeeds";
             "semaphore of min(GOMAXPROCS,4)"), §1 hand-off list (body-limit helper is listed;
             the hasher is not)
  requirements: VZ-INSTALL-003, ADR-003 §Credentials

Observed:
  The ordering claim — argon2 only after a successful digest compare — is the single most
  important DoS property of this endpoint (an unauthenticated 19 MiB × 26 ms primitive is a
  gift), and it is asserted in prose with no test and no mutation. §6.1 has no MUT for it.
  The 19456 KiB / t=2 / p=1 pin is correctly treated as ADR-003's, not the builder's; the
  25.7 ms/op measurement and the 50–80 ms floor-host estimate are properly labelled.

Failure:
  A later refactor that binds-and-validates-then-hashes-then-checks-the-token reintroduces
  the amplifier and nothing notices. On the 4 GB / 2 vCPU floor host, four concurrent
  derivations is 76 MiB transient and ~2 cores saturated.

Perspective: operator, visitor (availability)

Recommendation:
  1. Make the ordering observable: the hasher is an injectable dependency with a call
     counter, and tests assert ZERO derivations on the 415, 400, 403 (bad token), 409 and
     429 paths. Add MUT-13: "hash before comparing the token" must turn it red.
  2. Put the concurrency semaphore in a shared package (`internal/credential` or similar),
     not in the claim handler, and add it to §1's hand-off list — M1-B's sign-in is the real
     multi-caller of argon2 and must share the SAME bound, not create a second unbounded one.
     Waiters must respect `c.Request().Context()` and fail with 503, never queue unbounded.

Acceptance criteria:
  Zero argon2 derivations on every non-201 path. One process-wide bound on concurrent
  derivations, in a package M1-B imports.

Tests:
  `TestNoPasswordHashingOccursWithoutAValidToken` (unit+integration, counter-backed),
  `TestConcurrentHashingIsBounded`.

Cross-repo implications: core; M1-B (VZ-AUTH-001) | user: none
Challenge: "The counter is test scaffolding in a production path." It is one function field
  on a struct, the same seam `PingDatabase`/`PingCache` already use (server.go:55-56).
```

```
FINDING 11: field validation must happen in Go before the SQL, or a malformed field becomes a 500
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §2.2 (users_username_shape, users_email_shape, users_display_name_bounded),
             §4.2 (OpenAPI patterns), §3.6 (the claim CTE)
  requirements: VZ-INSTALL-003

Observed:
  `api/openapi.yaml` is hand-written and there is no request-validation middleware in the
  tree — the spec's `pattern`/`minLength` are documentation, not enforcement. If the handler
  passes an unvalidated username or email into the CTE, a CHECK violation (23514) aborts the
  transaction.

Failure:
  A user who types `ab` or `me@localhost` gets a 500 with a request id and no guidance,
  instead of the 400 the design's error copy promises. Worse for the operator: the failure
  looks like a server fault on the one endpoint they cannot skip. (The token is NOT consumed
  — the transaction rolls back — so this is a usability and diagnosis failure, not data loss.)

Perspective: operator

Recommendation:
  Validate in Go against exactly the CHECK expressions before any database work, and return
  400. Compile the username/email regexes from constants that a test cross-checks against the
  migration file's own bytes, so the two can never drift (the repo already does this for the
  search contract: `TestTheContractAndTheLoaderNameTheSameVariable`).

Acceptance criteria:
  Every value the schema would refuse yields 400 with `bad_request`, no 5xx, no transaction,
  and an unconsumed token.

Tests:
  `TestMalformedFieldsYield400AndDoNotConsumeTheToken` (table: short username, leading
  hyphen, 31 chars, no-dot email, 255-byte email, 11-char password, 257-char password,
  1 KiB-of-astral-characters password).

Cross-repo implications: core | user: the form's client-side rules must match
Challenge: "The UI validates." The UI is not the authorization boundary; AGENTS.md says so.
```

```
FINDING 12: `vizra claim-token` must refuse on a claimed instance, and a failed boot mint must be survivable
Severity:    REQUIRED
Confidence:  medium

Affected:
  repo:      vizra-core
  files:     plan §3.4 ("`vizra claim-token` always works while unclaimed"), §3.1 (mint at
             cmd/api boot), §8 (doctor check); Dockerfile:106,127 (the CLI is in the image)
  requirements: VZ-INSTALL-003 outcome — "an instance with users and no token ... never mints again"

Observed:
  The plan says the CLI "always works while unclaimed" but does not say what it does when
  the instance IS claimed, and the boot mint has no stated failure behaviour. `cmd/api` mints
  at boot; if the api container starts before the migrator has applied 0005, the table does
  not exist.

Failure:
  (a) If the CLI mints on a claimed instance it manufactures a live owner-claim credential on
      a running production instance — a standing landmine for any future owner-transfer route,
      and an escalation path for anyone with `docker exec` or the DSN.
  (b) If the boot mint panics or is fatal, a start-order race becomes a crash loop; if it is
      silently swallowed, the instance has no token, `announce=off` prints nothing useful, and
      the operator has no signal.
  (c) A claim against an instance that never minted must not answer differently from a claim
      with a wrong token — the plan lists four indistinguishable reasons for 403 but not this
      fifth one.

Perspective: operator, instance-admin

Recommendation:
  `vizra claim-token` refuses with a non-zero exit and a clear message when ANY user exists.
  A boot mint failure is a redacted error log + degraded readiness + a `vizra doctor` FAIL,
  never a panic and never silent; the CLI remains the recovery. "No token row" joins the
  other four causes of the single uniform 403.

Acceptance criteria:
  CLI exits non-zero on a claimed instance and mints nothing. An api booted against a schema
  without 0005 stays up, reports degraded, and the operator's doctor run says what to do.
  A claim against a never-minted instance is byte-identical to a claim with a wrong token.

Tests:
  `TestClaimTokenCLIRefusesOnAClaimedInstance`, `TestBootMintFailureIsDegradedNotFatal`,
  `TestClaimWithNoMintedTokenIsIndistinguishableFromAWrongToken`.

Cross-repo implications: core | meta: doctor output documented in COMMANDS.md
Challenge: UNVERIFIED — I did not read `cmd/vizra`'s existing subcommand structure, only the
  Dockerfile lines proving the binary ships. The refusal requirement stands regardless.
```

```
FINDING 13: the advisory-lock key should be a constant, not hashtext()
Severity:    SHOULD
Confidence:  medium

Affected:
  repo:      vizra-core
  files:     plan §3.1 — `pg_advisory_xact_lock(hashtext('vizra.owner_claim.mint'))`
  requirements: VZ-INSTALL-003

Observed:
  `hashtext` is an internal PostgreSQL function with no documented stability guarantee across
  major versions, and this is the first advisory lock in the tree. Two api replicas running
  different PostgreSQL client-visible majors during a rolling upgrade would take two
  different locks and both mint.

Failure:
  A lost update during exactly the window the lock exists for; and, later, a silent collision
  between two unrelated lock names nobody can see because the keys are opaque.

Perspective: operator, developer

Recommendation:
  An explicit `const ownerClaimMintLock int64 = <fixed value>` with a short registry comment
  listing every advisory-lock key the product uses, so the next user of the mechanism can see
  what is taken.

Acceptance criteria: no `hashtext` in the tree; one place lists the lock keys.
Tests: covered incidentally by the existing race tests; no new test warranted.
Cross-repo implications: core | user: none
Challenge: "hashtext is stable in practice." Probably — and a constant costs one line.
```

```
FINDING 14: the enum ↔ authz.Role agreement should be a test, since the enum order freezes here
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §2.2 (`CREATE TYPE user_role AS ENUM ('guest','member','manager','admin','owner')`),
             §1 hand-off 3; internal/authz/authz.go:31-44 (roleRank includes RoleAnonymous at 0)
  requirements: VZ-AUTH-004 (M1-C), ADR-003 §Authorization

Observed:
  The plan makes the enum's rank order "a schema fact" that M1-C's matrix test depends on.
  `authz.Role` has SIX values; the enum has five — `anonymous` is deliberately not storable.
  That deliberate asymmetry is currently written only in a Go comment.

Failure:
  A future `ALTER TYPE ... ADD VALUE` in the wrong position, or an `anonymous` label added to
  the enum by someone tidying the asymmetry away, silently breaks the ordering M1-C's matrix
  test assumes — and an `anonymous` row in `users` would be a stored principal with rank 0.

Perspective: developer, instance-admin

Recommendation:
  A test that reads the enum labels from the live database (`enum_range`) and asserts they
  equal `authz`'s ordered stored roles exactly, with `anonymous` absent by intent.

Acceptance criteria: reordering or extending either side without the other turns it red.
Tests: `TestUserRoleEnumOrderMatchesAuthzRanking` (integration).
Cross-repo implications: core; M1-C | user: none
Challenge: "M1-C will write it." M1-C cannot change the enum if it disagrees — it froze here.
```

```
FINDING 15: the consolidated list of attacker-relevant behaviour with no test that would go red
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §6 (tests 1–19), §6.1 (MUT-1…MUT-12)
  requirements: VZ-INSTALL-003 evidence_required — "negative/permission test that fails against a controlled mutation"

Observed / Failure:
  The plan's matrix is unusually honest (MUT-4 is recorded as untestable, MUT-2's green #2 is
  reported rather than hidden). These are the gaps it does not name. Each is a behaviour an
  attacker or a stuck operator reaches, with no test that would go red:

  1. Non-JSON content type accepted (FINDING 8) — no test.
  2. Unknown JSON field accepted (`additionalProperties: false` unenforced) — no test.
  3. Cross-origin POST — no test, no behaviour.
  4. Chunked body over the limit (#13 does not distinguish Content-Length from streamed bytes).
  5. argon2 invoked before the token check (FINDING 10) — no test, no mutation.
  6. 23505 on `users_one_owner` mapping to 409 rather than 500 (FINDING 9) — no test.
  7. Malformed username/email reaching the CHECK as a 500 (FINDING 11) — no test.
  8. `ip_prefix` writer emitting a value the frozen CHECK refuses (FINDING 1) — #15 covers
     only the three happy shapes.
  9. A rate-limited request writing an audit row (FINDING 5) — no test.
 10. A valid token answered 429 (FINDING 7) — no test.
 11. Restart invalidating a token the operator is holding (FINDING 3) — #4 tests the opposite.
 12. Boot announcement default emitting a credential (FINDING 2) — #8 tests the logger path
     only, not the default's value.
 13. `vizra claim-token` on a claimed instance (FINDING 12) — no test.
 14. Expiry decided by the application clock rather than PostgreSQL's. MUT-6 removes the
     predicate; it does not catch replacing `now()` with a Go-supplied timestamp. The repo
     already has the idiom to copy: `TestRunAfterComesFromTheDatabaseClockNotTheApplicationHost`.
 15. A live token surviving beside an out-of-band owner until the next boot (FINDING 9).
 16. A route added without an unclaimed decision (FINDING 4) — #19 tests a helper, not routes.
 17. Presented-digest vs stored-digest in the SQL argument: like MUT-4, NOT observable from a
     test. Record it beside MUT-4 as a code-review-only property rather than implying coverage.

Recommendation:
  Add the named tests from findings 1–14 and record 17 honestly beside MUT-4. Where a
  mutation is genuinely unobservable, saying so is worth more than a test that pretends.

Acceptance criteria:
  Every acceptance bullet the PR marks *demonstrated* has a mutation that turns a NAMED test
  red, and the demonstrate.sh transcript shows the before/after digest pair for each.

Tests: as named in findings 1–14.
Cross-repo implications: core | meta: the evidence files under docs/evidence/m1a-owner-claim/
Challenge: "This doubles the test count." It roughly adds a dozen cases to a slice that
  creates the first credential in the product. That is the correct ratio.
```

---

# FOLLOW-UPS (with the slice they belong to)

- **F1 — `VIZRA_TRUSTED_PROXIES` + `X-Forwarded-Proto` → M1-B (VZ-AUTH-001).** Sign-in rate limiting makes per-client attribution load-bearing; until then FINDING 7's NULL rule holds. This is the same item the infrastructure seat already raised (`docs/plans/WARROOM-BOARD.md` row 7, F7): the installer must not offer `VIZRA_TLS_MODE=external` until core can trust a forwarded header. Agree with the builder's OQ-7 placement.
- **F2 — audited retention path for `audit_events` → propose a new ledger ID (M2).** 0003 deferred the trigger *and* the retention path as a pair (`0003_audit_events.up.sql:18-24`); this slice lands half. Whichever option FINDING 5 takes, the debt must carry an ID rather than a comment.
- **F3 — reserved-username list → M1-B.** `users_username_shape` freezes the *shape* here; nothing stops the owner claiming `admin`, `api`, `setup`, `_next`. It collides with `vizra-user`'s route space the moment profiles live at `/{username}`. Application-side list, not a CHECK.
- **F4 — per-field error envelope → M1-B.** Agree with OQ-8 exactly as the builder framed it: extend the contract once, with sign-up as the real multi-field consumer.
- **F5 — CORS and `/setup/*` → whichever slice adds CORS middleware.** FINDING 8's protections partly rest on no CORS middleware existing. Whoever adds `VIZRA_CORS_ALLOWED_ORIGINS` enforcement must exclude the setup routes and add a test that says why.
- **F6 — owner transfer / tombstoned-owner recovery → later slice.** `users_one_owner` deliberately omits a `tombstoned_at` predicate, so a tombstoned owner permanently blocks any replacement. The builder states this ("recovering ... is an owner-transfer route in a later slice"); it needs a ledger ID, because today it is a recovery hole with no owner.
- **F7 — VZ-INSTALL-003's success case is not demonstrable here.** "Claim with valid token yields owner role; **admin surface returns 200**" cannot be shown at M1-A — there is no admin surface and no session. The plan records the 403-signup bullet as PARTIAL but not this one. Evidence owed by M1-C (VZ-AUTH-004). Name it in the PR body.
- **F8 — PostgreSQL 18 evidence → phase 2.** Nothing in this design differs between 17 and 18 (partial unique indexes, data-modifying CTEs, EvalPlanQual re-check under READ COMMITTED, `ALTER TYPE ... ADD VALUE` are all stable), so the 17.11 transcript is sound as *design validation*. It is not acceptance evidence: CI pins 18 by digest, and phase 2 must cite the integration run on 18. Say "indicative, validated on 17.11" in the evidence file, never "measured" without the version.
- **F9 — the 201 body returns the internal uuid.** ADR-007 §Identifiers separates internal id from public id, and its entity table gives `users` no `public_key` — the public handle is the username. Returning the internal PK in an unauthenticated response freezes it into the contract (removing a required field later is breaking). `{username, role}` is enough for the UI to redirect. Decide now; cheap either way. Severity SHOULD.

---

# RULING RECOMMENDATIONS, OQ-1…OQ-10

- **OQ-1 (native enum)** — **ACCEPT the builder's recommendation**: native `user_role` enum; the append-only argument is decisive (`ALTER TYPE ADD VALUE` is additive, widening a CHECK is not). Add FINDING 14's drift test.
- **OQ-2 (announce default)** — **MODIFY: default `off`.** `stderr` is an explicit opt-in. The ledger's privacy case is an acceptance bullet, and the plan's own analysis shows `stderr` violates it wherever logs are shipped. Chair must order the matching edits to PRODUCT_SPEC §15 step 4 and copy key `claim.help.body`. See FINDING 2.
- **OQ-3 (claim-status endpoint)** — **ACCEPT**: add the GET, one bit only, and update `VZ-INSTALL-003.surfaces.api` in the meta repo. An anonymous caller may learn `claimed` and nothing else; `claimed:false` does advertise a target, but the public `/setup/claim` page and an empty gallery advertise the same bit, so concealment is illusory while the token remains the real control. Add: the bit is monotonic — cache it permanently once true so a flood costs no database work.
- **OQ-4 (409 vs 404/403)** — **ACCEPT 409**, with the builder's reasoning: 403 is already taken for the opposite condition, and the design's "already claimed" screen requires the bit next door anyway. Add `409 → conflict` to `httpCodeName` (confirmed absent, `internal/httpapi/middleware.go:162-183`). Keep the claimed check strictly before the token examination.
- **OQ-5 (claim does not sign in)** — **ACCEPT no session at M1-A.** The interim state is the SAFEST available: a hashed credential exists and no route can authenticate against it. Faking a session would be mock data in a production path. `vizra-user` redirects to `/login`; someone must tell that builder, and F7's evidence gap must be recorded.
- **OQ-6 (PHC string vs "Vizra version tag")** — **ACCEPT plain standard PHC**, recorded as an *interpretation*, not a deviation: ADR-003's stated purpose ("parameters can be raised later and old hashes re-derived ... without a second column") is exactly what embedded `m,t,p` deliver, and a standard PHC string has no vendor slot, so the literal text is self-contradictory. If the owner wants the literal text honoured at zero cost, PHC's optional `keyid=` field is the slot. No ADR amendment needed to proceed; ask the owner to ratify the clarification at the next ADR touch. **But loosen the CHECK** per FINDING 6 — that part freezes.
- **OQ-7 (FK ON DELETE RESTRICT)** — **ACCEPT RESTRICT**; `audit_events_actor_identified` makes SET NULL illegal and users are tombstoned, not deleted. Consequence to record: erasure is therefore tombstone + scrub, so audit `before`/`after` must never carry PII — the plan's rule (username yes, email never) is right and must be inherited by every later emitter.
- **OQ-8 (per-field error envelope)** — **ACCEPT deferral to M1-B**, exactly as argued. Single-message 400 at M1-A.
- **OQ-9 (`vizra claim-token` CLI surface)** — **ACCEPT**, and record it on `VZ-INSTALL-003.surfaces.cli`. Under the OQ-2 ruling it is not merely accepted, it is the *primary* delivery path. Binary confirmed present in the runtime image (`Dockerfile:106,127`). Add FINDING 12's refusal-when-claimed requirement.
- **OQ-10 (does ADR-003's "Setup wizard" row bind the claim endpoint?)** — **The builder's reading is correct; the chair should record it verbatim as the interpretation:** *ADR-003's "Setup wizard" request-class row describes the installer wizard (`vizra setup` / `install.sh`, VZ-ISSUE-004), whose Vidra precedent is a separate setup web server (`C/internal/setupweb/guard.go`); it does not bind `POST /api/v1/setup/claim-owner`, which is a public-origin browser surface per VZ-INSTALL-003 `surfaces.ui`, the approved frames, and ADR-007's precedence rule naming owner claim as one of three surfaces an anonymous visitor keeps on a private site.* The alternative reading makes the approved design unbuildable. **Does the owner have to amend the ADR? Not to unblock this slice — but yes, before M1-B merges**, for one reason: ADR-003's table is the authority on CSRF posture per request class, and after this interpretation the claim endpoint is a request class with *no row*. A one-line amending ADR should (a) rename the row "Installer setup wizard" and (b) add a row: *"Unauthenticated pre-claim JSON POST | credential in body | `Content-Type: application/json`, and `Origin`/`Sec-Fetch-Site` must not be cross-site when present | allow."* Absent that row, the next reader re-litigates this, and the protection is whatever the handler happened to do. What must protect it instead of loopback+`X-Setup-Token`+Host allowlist: **token entropy and single use** (256-bit, SHA-256 at rest, constant-time compare, one-shot by a database constraint — all present in the plan), **failure-keyed rate limiting** (FINDING 7), **the content-type and origin posture of FINDING 8**, **TLS via the existing production refusal of a plain-http `VIZRA_PUBLIC_ORIGIN`** (`internal/config/config.go:263-264` — this already covers `VIZRA_TLS_MODE=external`, since an external terminator still requires an `https://` public origin unless the operator explicitly sets the insecure hatch), and **a `vizra doctor` check for a wrong/unset public origin**, since a mismatch 403s the browser claim while curl still works. Note that core has **no Host allowlist** — `site.ByHost` falls back to the single site for any unknown Host (`internal/site/site.go:95-108`) — so the Origin check, not the Host header, is what stops DNS rebinding against a LAN-bound instance.

---

# NOT WORTH DOING

- **Loopback-binding the claim route, or requiring `X-Setup-Token` in addition to the claim token.** The literal OQ-10 reading. It contradicts three governing artifacts, makes the approved claim screens undrawable, and adds a second secret with the same delivery problem as the first. Declined with reason, per protocol.
- **Timing-uniform responses on `GET /setup/claim-status`.** There is no secret being compared — it is a boolean read of a one-row table. Constant-time machinery here buys nothing and obscures the code. (Constant-time compare on the *token digest* is required and is already in the plan.)
- **argon2 or any slow KDF over the claim token.** The builder is right: 256 bits of uniform randomness has nothing to grind, and a slow KDF on an unauthenticated endpoint is a CPU amplifier handed to the attacker. SHA-256 is correct.
- **Zeroing `token_sha256` after consumption.** It is the digest of a dead 256-bit secret. No attacker gains anything; the migration and the code get more complex.
- **Requiring `Sec-Fetch-Site` or `Origin` to be PRESENT.** It would break curl, the installer and any non-browser claim, for an attack that requires the attacker to already hold the token. Reject when present and cross-site; allow when absent.
- **CAPTCHA, proof-of-work, or a second factor at claim time.** The endpoint can succeed exactly once in the lifetime of the instance and is gated by a 256-bit secret. Every one of these adds a dependency, a failure mode and an accessibility problem to defend a bound the database already provides.
- **Hiding the claimed bit behind a 404.** Argued well by the builder in §3.3 and I agree: it breaks the designed "already claimed" screen while leaking the identical bit from the status endpoint next door.
- **A SAVEPOINT around the audit insert so a claim survives an audit failure.** It converts FINDING 1's loud failure into a silent hole in the trail at exactly the moment the trail matters most. Fix the writer instead.

---

**Position summary.** The design's core is right and unusually well evidenced: constraint-decided race, hash-at-rest, token-before-argon2, one bit on status, 409 for claimed, enum for roles, and an honest mutation matrix that reports its own gaps. Seven things freeze badly or are unsafe as written: the `ip_prefix` writer can permanently brick a claim through a CHECK that is already frozen; the stderr announce default writes a live credential into every log pipeline; unconditional re-mint is a denial-of-claim; `requireClaimed` is fail-open by construction; auditing 429s makes the limiter an unbounded writer into an undeletable table; the credentials CHECK over-freezes and the email-fold rule is unwritten; and the limiter as keyed lets any stranger lock the operator out while attributing every audit row to the proxy. OQ-10's reading is correct — record it, and get the owner to add the missing CSRF-table row before M1-B. What would change my mind: on FINDING 2, evidence that a compose deployment can guarantee a local-only log stream (there is none); on FINDING 3, an owner ruling that the ledger's "restart re-mints" sentence is literal rather than a recovery guarantee.
