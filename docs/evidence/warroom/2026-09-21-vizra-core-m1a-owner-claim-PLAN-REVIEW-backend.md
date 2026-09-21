# vizra-core M1-A (owner claim, VZ-INSTALL-003) — PLAN review by the `vizra-core` backend seat

- **Reviewed:** the builder's phase-1 plan `docs/plans/2026-09-21-vizra-core-m1a-owner-claim.md` (no code exists yet), against vizra-core `main@4a80a1e`
- **Reviewer:** `vizra-core` council seat (agent `aec2b3f79317ff17c`), read-only; three DDL probes on PostgreSQL 18.6 in rolled-back transactions
- **Date:** 2026-09-21
- **Kind:** specialist review of a PLAN before code, by chair ruling for security-critical, schema-freezing slices. Not a verifier verdict. The `vizra-security` seat's review is a separate file; the chair's consolidated rulings are recorded in the plan-review ruling file once both are in.

The seat's report follows verbatim.

---

I read the plan, both `AGENTS.md`, ADR-003/004/007, the three ledger entries, migrations 0001–0004, `scripts/migrate-lint.sh`, `sqlc.yaml`, `store/queries/*`, `internal/{authz,httpapi,config,obs,cache,site,migrate,integration}`, `cmd/vizra`, `api/openapi.yaml`, and ran three read-only DDL probes against the live PostgreSQL **18.6** on `127.0.0.1:55432` (all in rolled-back transactions / with verified cleanup — `zz_ro_probe*` schemas confirmed gone).

---

# BLOCKING-BEFORE-CODE

```
FINDING 1: users_one_owner without a tombstone predicate makes a tombstoned owner an unrecoverable instance
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     docs/plans/2026-09-21-vizra-core-m1a-owner-claim.md:162-165 (the index),
             docs/adr/ADR-003-identity-sessions-csrf-authorization.md:84-86 ("owner is single and cannot be demoted"),
             features.json VZ-ADMIN-USERS-001 cases.negative ("Cannot demote the last owner")
  requirements: VZ-INSTALL-003, VZ-ADMIN-USERS-001, VZ-AUTH-004

Observed:
  Plan: `CREATE UNIQUE INDEX users_one_owner ON users (role) WHERE role = 'owner';`
  with the comment "Deliberately NOT filtered on tombstoned_at: 'exactly one owner,
  EVER'." The plan simultaneously ships `audit_events_actor_user_fk ON DELETE
  RESTRICT` and a BEFORE UPDATE OR DELETE trigger on audit_events, and mints the
  owner-claim token only when `NOT EXISTS (SELECT 1 FROM users)`.
  Measured on PG 18.6: the partial unique index does enforce one owner, and a
  single-statement role swap (`UPDATE ... SET role = CASE ...`) succeeds in both
  row orders, so transfer itself is not the problem.

Failure:
  Tombstone the owner — an admin deletes the wrong account, a compromised-owner
  containment, a GDPR request — and the instance has no route back. The index
  still holds the 'owner' key, so no second owner can be created. ADR-003 says the
  owner cannot be demoted, so no transfer path exists. The claim token cannot be
  re-minted because users exist. The row cannot be deleted because audit_events
  RESTRICTs it and this slice's own trigger blocks the UPDATE that would release
  it. The only recovery is hand-written SQL by someone with DATABASE_URL, against
  a table the product forbids editing. "An operator cannot recover" is the
  council's own BLOCKER definition.

Perspective: instance-admin, operator

Recommendation:
  Add the tombstone predicate. It changes nothing about the claim race (a freshly
  claimed owner is never tombstoned) and MUT-2 is unaffected:

    -- At most one LIVE owner. A tombstoned owner releases the key so an instance
    -- whose owner account was deleted is recoverable by the M2 owner-transfer
    -- route rather than by hand-written SQL.
    CREATE UNIQUE INDEX users_one_owner
        ON users (role) WHERE role = 'owner' AND tombstoned_at IS NULL;

Acceptance criteria:
  - Two live owner rows are impossible (23505 on users_one_owner).
  - With the single owner tombstoned, inserting a new owner row SUCCEEDS.
  - The claim endpoint still answers 409 on a claimed instance (that gate is
    `EXISTS (SELECT 1 FROM users)`, not the index), so tombstoning the owner does
    not reopen the claim endpoint.

Tests:
  internal/integration/owner_claim_test.go —
  `TestASecondLiveOwnerIsRefusedByTheDatabase` and
  `TestATombstonedOwnerDoesNotPermanentlyBlockOwnership`. Mutation: remove
  `AND tombstoned_at IS NULL` → the second test goes red.

Cross-repo implications:
  core: index predicate freezes on merge. user: none. search: none.
  meta: the owner-transfer route is a new ledger obligation under VZ-ADMIN-USERS-001.

Challenge:
  "Exactly one owner ever" is a stronger, simpler invariant and the plan states it
  deliberately. My answer: the ledger never asks for it (VZ-INSTALL-003 says
  "race between two claimers yields one owner"), and the stronger invariant buys
  nothing the live-owner predicate does not, while converting a routine admin
  mistake into a dead instance.
```

```
FINDING 2: ON DELETE RESTRICT plus the append-only trigger makes every user row permanently undeletable
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0003_audit_events.up.sql:21-28 (the deferral, and "the audited
             retention path it has to coexist with"),
             plan §2.2 (the FK, the trigger), plan §9 OQ-7
  requirements: VZ-ADMIN-USERS-001 ("delete with content handling"), VZ-INSTALL-003

Observed:
  0003 froze `CONSTRAINT audit_events_actor_identified CHECK ((actor_kind = 'user')
  = (actor_user_id IS NOT NULL))`, so ON DELETE SET NULL is genuinely impossible —
  the plan is right about that. But the plan then adds, in the SAME migration, a
  trigger that raises on any UPDATE or DELETE of audit_events, and a second
  RESTRICT FK from `owner_claim_tokens.consumed_by`. 0003's header explicitly said
  the trigger lands in M1 "alongside ... the audited retention path it has to
  coexist with". The plan ships the trigger and no retention path, and justifies
  RESTRICT with "Users are tombstoned ..., not hard-deleted, so RESTRICT costs
  nothing real" — a product decision this slice does not own, contradicted by
  VZ-ADMIN-USERS-001 whose outcome is literally "delete with content handling".

Failure:
  After merge there is no statement any Vizra code can execute that removes a user
  row, and no statement that anonymises its audit trail. M2's admin delete, GDPR
  erasure and audit retention all require a later annotated-destructive migration
  to DROP the trigger and/or the FK — which is exactly the "expensive to add
  later" failure 0003's header exists to prevent. Worse, nothing in the plan tells
  the next writer this, so it will be discovered by an M2 builder at the point of
  implementation.

Perspective: instance-admin, member (erasure), developer

Recommendation:
  Three changes, all in this migration:
  1. Drop `consumed_by` and `owner_claim_tokens_consumed_pair` entirely. The
     `setup.owner_claim.succeeded` audit row already ties generation → owner id.
     The FK buys one more deletion blocker and nothing else.
  2. Carve the anonymisation shape into the trigger NOW, so erasure is possible
     without a destructive migration and so it has a test today:

       CREATE FUNCTION audit_events_append_only() RETURNS trigger
       LANGUAGE plpgsql AS $$
       BEGIN
           -- The ONE permitted mutation: erasure anonymisation. Everything the
           -- row says about WHAT happened is immutable; only WHO may be erased,
           -- and only by clearing it completely.
           IF TG_OP = 'UPDATE'
              AND NEW.actor_kind = 'anonymous' AND NEW.actor_user_id IS NULL
              AND NEW.actor_label IS NULL
              AND OLD.actor_kind = 'user'
              AND (NEW.id, NEW.occurred_at, NEW.action, NEW.subject_type,
                   NEW.subject_id, NEW.before, NEW.after, NEW.correlation_id,
                   NEW.ip_prefix)
                IS NOT DISTINCT FROM
                  (OLD.id, OLD.occurred_at, OLD.action, OLD.subject_type,
                   OLD.subject_id, OLD.before, OLD.after, OLD.correlation_id,
                   OLD.ip_prefix)
           THEN
               RETURN NEW;
           END IF;
           RAISE EXCEPTION 'audit_events is append-only (attempted % on id %)',
               TG_OP, OLD.id USING ERRCODE = '42501';
       END;
       $$;

     If the chair or the security seat prefers the strict form, the minimum is a
     header sentence naming the escape: `CREATE OR REPLACE FUNCTION` is NOT matched
     by migrate-lint's destructive regex (`DROP (TABLE|COLUMN|CONSTRAINT|INDEX|
     TYPE|SCHEMA|VIEW|SEQUENCE)|... |TRUNCATE`, scripts/migrate-lint.sh), so a
     later migration can widen the function additively. Say so, or M2 will assume
     it cannot.
  3. Header sentence: "Deleting a user row is impossible while audit rows name it.
     Erasure is anonymise-then-tombstone, never DELETE. Retention deletion of
     audit rows is a separate decision and is not possible under this trigger."

Acceptance criteria:
  - `DELETE FROM users WHERE id = <an audited actor>` fails with 23503, and a test
    asserts exactly that (the test IS the documentation).
  - An UPDATE that changes `action`, `after` or `occurred_at` fails with 42501.
  - An UPDATE that only clears actor_kind/actor_user_id/actor_label succeeds
    (if the carve-out is adopted) or fails with 42501 (if not) — either way there
    is a named test, so M2 cannot change it by accident.

Tests:
  `TestAuditEventsCannotBeUpdatedOrDeleted` (#14) extended with the anonymisation
  case; new `TestAUserWithAuditRowsCannotBeDeleted`. Mutations: change the FK to
  NO ACTION → the delete test goes red; remove the shape check from the trigger →
  the tamper test goes red.

Cross-repo implications:
  core: the FK, the trigger body and the audit grammar freeze here.
  meta: VZ-ADMIN-USERS-001's "delete" becomes "anonymise + tombstone"; that is a
  ledger clarification the chair owns.

Challenge:
  The carve-out is an application-reachable mutation path on an audit table and
  the security seat will call it a hole. I accept that framing — but the
  alternative is an audit table that makes GDPR erasure impossible, and the
  carve-out permits exactly one shape that destroys identity and preserves every
  fact. If the chair rejects it, the header sentence is not optional.
```

```
FINDING 3: The OpenAPI bounds and the SQL CHECKs disagree, so a legal request becomes a 500
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §4.2 (ClaimOwnerRequest), plan §2.2 (users_email_shape),
             internal/httpapi/ (middleware.go, modules.go, probes.go, server.go —
             there is NO request-validation middleware in the package)
  requirements: VZ-INSTALL-003, VZ-AUTH-001

Observed:
  Spec: `email: { type: string, format: email, minLength: 3, maxLength: 254 }`.
  DDL:  `CHECK (email ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'
         AND octet_length(email) BETWEEN 3 AND 254)`.
  `maxLength` in JSON Schema counts CHARACTERS; `octet_length` counts BYTES.
  RFC 6531 internationalised addresses are legal UTF-8. `format: email` is
  advisory in OpenAPI and nothing in internal/httpapi validates it — there is no
  validator wired anywhere in the package.

Failure:
  A 200-character address with non-ASCII, or any address that satisfies
  `format: email` but not the POSIX regex (e.g. `a@b` — no dot; quoted local
  parts; a trailing dot), passes every declared bound, reaches the INSERT, raises
  23514, and — with no CHECK-violation mapping in the plan's error table — becomes
  a 500 on the instance's one-and-only setup endpoint. The operator sees
  "an internal error occurred" and cannot claim the instance.

Perspective: operator, instance-admin

Recommendation:
  1. Validate in Go with the SAME rule the DDL enforces, before the token
     comparison, and express the spec bound in bytes:
     `email: { type: string, maxLength: 254, pattern: '^[^\s@]+@[^\s@]+\.[^\s@]+$' }`
     with a `description` stating the limit is 254 bytes. Drop `format: email`
     or keep it only as documentation.
  2. Map 23514 (any CHECK) → 400 `bad_request` as a backstop, never 500, and test
     it with a deliberately DDL-violating value that the Go validator is mutated
     to let through.

Acceptance criteria:
  - No input accepted by the OpenAPI schema can produce a 5xx.
  - A 300-byte / 254-character UTF-8 address yields 400, not 500.
  - The Go validator's regex and the DDL's regex are the same literal, asserted by
    a test that reads the migration bytes (the repo already does this for the
    search contract: TestTheContractAndTheLoaderNameTheSameVariable).

Tests:
  `TestEveryRequestTheSpecAcceptsNeverYields5xx` (table over boundary values);
  mutation: revert the Go byte-length check to a rune count → red.

Cross-repo implications:
  user: the generated client's field constraints change if the spec is fixed
  later instead of now — fix it now.

Challenge:
  "254 characters is close enough." It is not: the gap is silent, lands on the
  one endpoint an operator must use before anything else works, and the spec text
  freezes on merge for vizra-user's generated client.
```

```
FINDING 4: The transaction's isolation level is unstated; under REPEATABLE READ the race test's "zero 5xx" is false
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §3.6, plan §6 test #2, plan §5.2 "Concurrent claims"
  requirements: VZ-INSTALL-003 cases.negative ("race between two claimers yields one owner")

Observed:
  The plan names no isolation level anywhere. Its whole race argument — "1 ×
  INSERT 0 1, 23 × INSERT 0 0 (no row)" — is READ COMMITTED semantics: the
  guarded UPDATE blocks on the row lock, then re-evaluates `consumed_at IS NULL`
  against the committed version (EvalPlanQual). Under REPEATABLE READ the same
  losers get 40001 `could not serialize access due to concurrent update`, not
  zero rows.

Failure:
  `default_transaction_isolation` is a server GUC an operator, a managed provider
  or a connection pooler can set. On such an instance every losing claimant gets
  a 40001 the handler does not map → 500. The measured evidence in §7 was taken
  on a default server and would not reproduce. Test #2's assertion "zero 5xx" is
  then a false pass, and the failure only appears in production.

Perspective: operator, developer

Recommendation:
  Pin it on the transaction, one line, and stop depending on the server default:
  `tx, err := pool.BeginTx(ctx, pgx.TxOptions{IsoLevel: pgx.ReadCommitted})`.
  Retry policy: NONE — correct, and say so in the plan. Under READ COMMITTED the
  loser's answer is deterministic (zero rows), so there is nothing to retry.

Acceptance criteria:
  - The claim transaction begins with an explicit READ COMMITTED isolation level.
  - The race test passes with the server's `default_transaction_isolation` set to
    `repeatable read` and to `serializable`.

Tests:
  `TestOwnerClaimRaceYieldsExactlyOneOwnerUnderEveryServerDefaultIsolation` —
  #2 parameterised over the three server defaults. Mutation: drop the explicit
  TxOptions → red under the repeatable-read leg. This is the mutation that is
  currently missing for the plan's headline invariant.

Cross-repo implications: none.

Challenge:
  "Nobody sets that GUC." Some managed PostgreSQL offerings and some pgbouncer
  configurations do. The fix is one struct literal; the failure is a 500 on the
  claim race in production.
```

```
FINDING 5: Boot minting on N api replicas prints N indistinguishable tokens, N−1 of them dead
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §3.1 (the advisory lock and the mint table), plan §3.4
  requirements: VZ-INSTALL-003 cases.recovery ("Restart re-mints; old token invalid"),
                privacy ("Token never appears in ... non-local logs")

Observed:
  §3.1: "Inside one transaction holding pg_advisory_xact_lock(...) so two replicas
  cannot interleave a lost update", with the rule "NOT EXISTS users → mint". The
  lock serialises the WRITE. It does not change the fact that each replica, in
  turn, mints a fresh digest, bumps `generation`, and prints its own line.

Failure:
  With 2+ api replicas (the compose/deploy shape is VZ-ISSUE-002/004, so this is
  an operator reality, not a hypothetical), a cold start prints 2+ 64-hex lines,
  only the highest generation verifies, and the lines are byte-indistinguishable.
  The operator copies one, gets 403 with the single undifferentiated message the
  plan's own §4.2 mandates ("mistyped, already used, superseded, or expired"), and
  has no way to tell which. A rolling restart makes it worse: a replica restarting
  for an unrelated reason silently invalidates a token the operator is mid-paste.

  Two further gaps in the same mechanism:
  (a) The plan does not say what happens if the schema is BEHIND (0005 not
      applied — cmd/api can boot against a behind database; that is what /schemaz
      exists for) or if PostgreSQL is unreachable at boot. If the mint error
      crashes cmd/api, an unreachable database becomes a boot loop. If it is
      swallowed, the instance runs forever with no token and no way to get one
      except another restart.
  (b) The worker and `vizra migrate` explicitly never mint, which is right, but
      the plan does not say the api skips minting when `role` is not yet a column.

Perspective: operator

Recommendation:
  Smallest change that keeps the ledger's recovery sentence intact:
  1. The announcement line carries the generation, in plain text:
     `vizra: instance unclaimed. claim token (generation 3): <64 hex>`
     and `vizra doctor`'s unclaimed check prints the CURRENT generation, so the
     operator can match line to instance without any secret being re-displayed.
  2. The plan states explicitly: "On N api replicas, N tokens are printed on a
     cold start and only the highest generation verifies. `docker compose exec api
     vizra claim-token` is the deterministic path and is the documented primary."
  3. Mint failure is logged and readiness-degraded, never fatal, and is RETRIED on
     the next successful database touch (or the instance is unclaimable until the
     next restart — say which, and test it).
  4. If the chair prefers "mint only when no live token exists" — which removes
     the ambiguity entirely — that is a change to VZ-INSTALL-003's recovery case
     and belongs to the chair, not the builder. Raise it as OQ-11.

Acceptance criteria:
  - Two concurrent boots against one unclaimed database leave exactly one live
    token row, and the highest announced generation is the one that verifies.
  - A boot against a database at schema version 4 logs a named warning and does
    not crash, and does not report ready-with-no-explanation.
  - `vizra doctor` on an unclaimed instance names the current generation and the
    exact command to mint.

Tests:
  `TestTwoConcurrentBootsLeaveOneLiveTokenAndTheAnnouncedGenerationIsTheValidOne`
  (integration, two mint calls in goroutines);
  `TestMintIsSkippedWhenTheSchemaIsBehindAndTheProcessStillBoots`.
  Mutation: remove the advisory lock → the first test must go red (it will:
  two upserts can interleave and the surviving digest may not be the announced one).

Cross-repo implications:
  meta: README / COMMANDS.md must document the multi-replica behaviour.

Challenge:
  "M1 has one api replica." True today, and the compose file does not exist yet —
  which is precisely why the behaviour must be decided here rather than discovered
  by VZ-ISSUE-002. The generation line costs one printf.
```

```
FINDING 6: Every refused and every rate-limited claim writes an audit row that can never be deleted
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     plan §5.3 (the audit grammar, `setup.owner_claim.refused` with
             `{"reason": ... |"rate_limited"}`), plan §5.1, plan §2.2 (the trigger)
  requirements: VZ-INSTALL-003, VZ-SECURITY-002 (flood protection)

Observed:
  §5.3 records `setup.owner_claim.refused` with `actor_kind='anonymous'` for
  every refusal, INCLUDING `reason: "rate_limited"`. §5.1 fails the limiter OPEN
  to a per-process MemoryLimiter when Valkey is down (per ADR-003). §2.2's trigger
  blocks DELETE on audit_events.

Failure:
  An unauthenticated endpoint is given an unbounded append path into a table with
  no deletion path. The 429 response — the mechanism that is supposed to stop the
  flood — is itself the thing that writes the row, so rate limiting does not bound
  the write, it causes it. With the limiter failed open and N replicas, the bound
  is N × per-process. There is no retention path (FINDING 2), so this is permanent
  growth on an instance that is not yet in service.

Perspective: operator

Recommendation:
  - A 429 writes NO audit row. Rate-limit rejections are a metric
    (`vizra_ratelimit_rejected_total{route}`), not audit history.
  - `setup.owner_claim.refused` is emitted at most ONCE per (ip_prefix bucket,
    window) — the limiter already holds that counter; emit the audit row only on
    the transition into the limited state, or only for the first N refusals per
    window.
  - `setup.owner_claim.minted` and `.superseded` and `.succeeded` stay
    unconditional; they are bounded by boots and by "exactly once".

Acceptance criteria:
  - 50 rapid claim attempts from one prefix produce ≤ 2 audit rows and ≥ 1
    rate-limit metric increment.
  - No audit row carries `reason: "rate_limited"`.

Tests:
  `TestARateLimitedClaimWritesNoAuditRow` — currently there is no such test and
  no mutation. Mutation: emit on every refusal → red.

Cross-repo implications: none.

Challenge:
  "Refusals are exactly what an audit trail is for." Agreed for authenticated
  actions. For an unauthenticated pre-claim endpoint, an attacker choosing how
  many immutable rows to write is a resource decision, not an audit decision.
```

---

# REQUIRED-IN-THIS-SLICE

**R1 — `username_fold` / `email_fold` must be `GENERATED ALWAYS ... STORED`, not a writer-supplied column with an equality CHECK.**
Measured on PG 18.6 (rolled-back probe): `email_fold text GENERATED ALWAYS AS (lower(email)) STORED` + `CREATE UNIQUE INDEX ON u (email_fold)` accepted; `'Owner@Example.COM'` stored fold `owner@example.com`; the second insert of `owner@example.com` raised `23505 duplicate key ... u_email_fold_key`. The plan's form (`email_fold text NOT NULL` + `CHECK (email_fold = lower(email))`) makes every INSERT and every future email/username UPDATE responsible for supplying the fold, and the CHECK only catches it after the fact. A generated column makes divergence unrepresentable and removes `lower(sqlc.arg(...))` from the ClaimOwner query. Drop `users_username_fold` and `users_email_fold` CHECKs — they become tautologies. **Phase-2 risk to preflight: sqlc 1.31.1 must not emit generated columns in an INSERT column list — verify with `sqlc diff` before writing the rest of the queries. UNVERIFIED (sqlc is not installed here).**

**R2 — Make `users_email_fold_key` partial from day one.** `CREATE UNIQUE INDEX users_email_fold_key ON users (email_fold) WHERE email_fold IS NOT NULL;` Costs nothing today (`email` stays `NOT NULL`), and it is the difference between "one additive `ALTER COLUMN email DROP NOT NULL`" and "an annotated-destructive DROP INDEX" when VZ-AUTH-006 lands ("email required for social signup **when configured**" — so an email-less OAuth user is a declared future state). `ALTER COLUMN ... DROP NOT NULL` is not matched by migrate-lint's destructive regex; `DROP INDEX` is. Keep `users_username_fold_key` non-partial — `/u/{username}` and `GET /api/v1/users/{username}` (VZ-ACCOUNT-001) make username mandatory forever.

**R3 — `credential_kind` should be `text + CHECK`, not a native enum; `user_role` should stay an enum. See OQ-1 ruling.** Measured on PG 18.6: `ALTER TYPE r ADD VALUE 'manager' BEFORE 'admin'` inside a transaction block is **accepted**, and using the value in the same transaction raises `ERROR: unsafe use of new value "manager" of enum type ... HINT: New enum values must be committed before they can be used.` After commit, `'manager'::r < 'admin'::r` is `t`. So enum widening works but forces a migration file that adds the value and **nothing else**, with no down file (`-- no-down:` — enum values cannot be removed). `credential_kind` has no ordering semantics and one value; text+CHECK matches `sites.privacy_mode`, `jobs.state`, `storage_locations.kind` and can be widened and used in one reversible migration.

**R4 — The error-mapping table must be complete and directly tested.** The plan's §4.2 table covers the happy paths. Missing, and each one is a 500 today:

| Postgres signal | Answer |
|---|---|
| `pgx.ErrNoRows` from ClaimOwner | re-read claimed state → 409 `conflict` if an owner exists, else 403 `forbidden` |
| 23505 / `users_one_owner` | 409 `conflict` |
| 23505 / `users_username_fold_key` or `users_email_fold_key` | 409 `conflict` (never 500) |
| 23514 (any CHECK) | 400 `bad_request` |
| 23503 / `audit_events_actor_user_fk` | 500 — a real defect; must log and alert |
| 40001 | must be unreachable once FINDING 4 is fixed; assert it |
| `context.DeadlineExceeded` | say which: 503 `unavailable` or 504 |

Test this as a **unit** table over the mapper with synthetic `*pgconn.PgError{Code, ConstraintName}` values (the plan's §7 item 8 already confirmed `pgconn.PgError` carries both, without promoting `pgerrcode`). Today the only mutation for 23505→409 is MUT-1, which proves the SQL guard, not the mapper.

**R5 — Token normalisation must precede shape validation, and a malformed token must answer 403, not 400.** §3.1 says presented tokens are trimmed and lowercased before hashing; §4.2's spec `pattern: '^[0-9a-fA-F]{64}$'` rejects a trailing newline. Order: trim → lowercase → shape → constant-time compare. And a token that fails the shape must get the SAME 403 and the SAME message as a wrong token — otherwise the plan's own "One message for all four ... four messages would be a lie and an oracle" is contradicted by a 400 that says "your token is the wrong length". Keep 400 for username/email/password only.

**R6 — Fix the `credentials` extension story and its bound.** ADR-007's entity table lists `sessions, api_keys | id | ADR-003` as their own entities, and ADR-003 gives API keys scopes, per-key limits, `last_used`, revocation and optional expiry. A user has MANY api keys, which `credentials_one_per_user_per_kind` forbids; OAuth identities need `(provider, subject)` uniqueness. The plan's §1 item 2 ("M2 adds `totp` as a new enum value, additively") is only true for TOTP. Change the plan's prose and the migration header to: *`credentials` holds at most one verifier secret per (user, kind) — `password` now, `totp` later. `api_keys`, `oauth_identities` and step-up rows are their own tables (ADR-003, ADR-007).* Also raise `credentials_secret_bounded` to `BETWEEN 1 AND 1024` so an envelope-encrypted TOTP secret plus KEK metadata fits without a destructive CHECK swap, and widen the argon2 CHECK so a future argon2 version is not a schema migration:

```sql
CONSTRAINT credentials_password_is_argon2id CHECK (
    kind <> 'password' OR secret LIKE '$argon2id$v=%$m=%,t=%,p=%$%$%'),
CONSTRAINT credentials_secret_bounded CHECK (octet_length(secret) BETWEEN 1 AND 1024)
```

**R7 — `pg_advisory_xact_lock(hashtext('vizra.owner_claim.mint'))` should use a literal.** `hashtext` is an undocumented internal function with no stability contract across major versions. Use a registered constant with a comment (`-- advisory lock ids: 1 = owner-claim mint`) so a future `hashtext` change cannot silently split the lock into two.

**R8 — Prove the migration and the race on PostgreSQL 18, not 17.11.** `.github/workflows/build-test.yml:107` pins `postgres:18` by digest; a 18.6 server is what my probes ran on. Nothing in this DDL behaves differently between 17 and 18 (generated columns are PG 12+; partial unique indexes and the enum semantics above were measured on 18.6) — but §7's evidence was taken on 17.11 and must be retaken, or the evidence file will not match the lane that gates the merge.

**R9 — `requireClaimed` must be group middleware with a route-walk test, not a per-route opt-in.** §4.3 describes a guard M1-B "attaches". MUT-12 removes the guard and turns the unit table test red, which proves the function, not its attachment — and attachment is the thing that fails in M1-B. Ship, now, a test that walks `s.e.Router().Routes()` (the repo already does this in `openapi_contract_test.go`) and asserts every route is in exactly one of two named sets: `claimExempt` (the four probes + the two setup operations) or "carries `requireClaimed`". At M1-A the second set is empty; in M1-B, `POST /api/v1/auth/register` fails the test unless the builder consciously classifies it. That is the default-deny shape AGENTS.md asks for, and it gives FINDING/MUT coverage to the attachment: add a fake account-creating route without the guard → red.

**R10 — Name the `/api/v1` prefix decision.** The four existing routes are `/healthz`, `/readyz`, `/version`, `/schemaz` (server.go:120-123); there is no `/api/v1` group. VZ-INSTALL-003's `surfaces.api` says `POST /api/v1/setup/claim-owner`, so this slice creates the convention every later slice inherits. Register it as an Echo group in `New`, and say in the plan that probes deliberately stay unprefixed.

**R11 — sqlc parameter typing in the ClaimOwner CTE is a phase-2 blocker risk.** `INSERT INTO users (...) SELECT sqlc.arg('username'), ... FROM consumed` gives sqlc no column context to infer parameter types from (the values come from a `SELECT` list, not a `VALUES` row matched to the target columns). sqlc's inference in this shape historically degrades to `interface{}`. Preflight `sqlc generate` on the real query before writing the handler; if the params are untyped, add explicit casts (`sqlc.arg('username')::text`, `sqlc.arg('user_id')::uuid`). Here is the query with FINDING 2's `consumed_by` removed and R1's generated columns applied:

```sql
-- name: ClaimOwner :one
WITH consumed AS (
    UPDATE owner_claim_tokens
       SET consumed_at = now()
     WHERE id
       AND token_sha256  = sqlc.arg('token_sha256')::bytea
       AND consumed_at   IS NULL
       AND superseded_at IS NULL
       AND expires_at    > now()
    RETURNING generation
),
owner AS (
    INSERT INTO users (id, username, email, role)
    SELECT sqlc.arg('user_id')::uuid, sqlc.arg('username')::text,
           sqlc.arg('email')::text, 'owner'
      FROM consumed
    RETURNING id, username, role, created_at
),
cred AS (
    INSERT INTO credentials (id, user_id, kind, secret)
    SELECT sqlc.arg('credential_id')::uuid, owner.id, 'password',
           sqlc.arg('password_hash')::text
      FROM owner
    RETURNING id
)
SELECT owner.id, owner.username, owner.role, owner.created_at,
       (SELECT generation FROM consumed) AS token_generation
  FROM owner, cred;
```

**R12 — §3.6 contradicts itself on the transaction boundary.** "Crash between the owner insert and the token consumption is impossible: they are one statement in one **implicit** transaction" and "The audit event is inserted in the *same* **explicit** transaction immediately after". Pick one and write it once: one explicit `BeginTx(ReadCommitted)` → ClaimOwner → InsertAuditEvent → Commit. The implicit-transaction argument is then redundant and should go.

---

# TEST PLAN — which invariants have no mutation that turns a test red

The plan's mutation matrix is unusually honest (MUT-4 and MUT-2 are both declared as non-reddening). These invariants have **no** test and **no** mutation at all:

| Invariant | Missing test | Missing mutation |
|---|---|---|
| Isolation level (FINDING 4) | race under `repeatable read` server default | remove explicit `TxOptions` |
| 23505 → 409 **mapping** (not the SQL guard) | unit table over `*pgconn.PgError` | delete the `users_one_owner` case from the mapper |
| `credentials_one_per_user_per_kind` | second password row for one user | drop the index |
| `users_username_fold_key` / `users_email_fold_key` | case-variant duplicate rejected | drop either index |
| `audit_events_actor_user_fk` exists | audit insert with an unknown actor fails 23503 | change FK to NO ACTION / drop it |
| `owner_claim_tokens_singleton` and the terminal-state CHECKs | second token row fails; `consumed_at` + `superseded_at` both set fails | drop the CHECK |
| `minted_at`/`expires_at` come from the **database** clock, not `time.Now()` | mirror `TestRunAfterComesFromTheDatabaseClockNotTheApplicationHost` | stamp `minted_at` from Go |
| `requireClaimed` **attachment** (R9) | route-walk classification test | add an unclassified account-creating route |
| 429 writes no audit row (FINDING 6) | 50 attempts → ≤ 2 rows | audit on every refusal |
| Limiter-down still permits the claim (§5.1's fail-open decision) | claim succeeds with the cache stopped | make the limiter fail closed |

Two named tests need their mechanism stated or they will quietly become skips: **#18 (503 when the database is down)** — say how (close the pool / point the DSN at a dead port / `pg_terminate_backend`), and **#12 (rate limited)** — say which bucket, and assert both.

Everything else — the race on real PostgreSQL, the log-scrape with a plain handler, the audit-secret scrape, the single-bit status body, the trigger, the /24//64 masking — is the right shape and the right harness (`freshDatabase`, `mustEnv` fatals rather than skips, integration.go:46-55). The `demonstrate.sh` sha256-before/after gate is exactly right and should be kept.

---

# FOLLOW-UPS, by slice

**M1-B (VZ-AUTH-001)**
- Per-field error envelope — safe to defer, see OQ-8.
- `VIZRA_TRUSTED_PROXIES`; until it exists, `ip_prefix` is NULL behind a proxy and the per-origin rate-limit bucket is inert. Say this in the PR body so it is not mistaken for working.
- **Enumeration-safe registration given the unique `email_fold` index.** VZ-AUTH-001's negative case is "enumeration-safe errors" and VZ-AUTH-002's is "Reset for unknown email returns same response". A unique email index plus a synchronous 409 is an enumeration oracle. The schema is right; the *contract* obligation lands with the registration endpoint and needs the verification-email flow to answer identically either way. Flag it now so M1-B does not design a 409.
- Add `Set-Cookie` to the same `claimOwner` operation (backward-compatible).
- A test pinning the DB enum order against `authz.roleRank` (internal/authz/authz.go:39-41) so the two cannot drift.

**M1-C (VZ-AUTH-004)**
- `PATCH /admin/users/{id}/role` is the first place a `user_role` enum value crosses pgx as a **parameter**. Verify sqlc's enum codegen and pgx's OID resolution then; it is fine in M1-A because `'owner'` is an SQL literal.
- "Cannot demote the last owner" (VZ-ADMIN-USERS-001) — with FINDING 1's predicate the index enforces at most one live owner but not at least one; that check is application-side and needs its own constraint or test.
- Owner transfer. Measured on PG 18.6: a single-statement `UPDATE users SET role = CASE ...` swapping owner↔member succeeds against the partial unique index in both row orders, so transfer does not need two statements. Good news; record it.

**M2**
- User erasure / anonymisation path and audit retention (FINDING 2).
- `api_keys`, `oauth_identities`, TOTP tables (R6).
- **Tombstoned identifiers.** `username_fold` and `email_fold` stay occupied forever after a tombstone, so a deleted account's email can never re-register. The tombstone path must rewrite `email` — note the DDL regex requires a dotted domain, so `deleted+<uuid>@deleted.invalid` passes and `deleted+<uuid>@invalid` does not.

**Later**
- `vizra doctor` check for the PostgreSQL server major version. Nothing in core refuses a pre-18 server — I grepped `internal/` for `server_version`/`version()`: no hits. The pin exists only in `.github/workflows/build-test.yml` and the Dockerfile. This is the reason not to reach for PG 18's native `uuidv7()`.
- **Keyset pagination rule:** never `ORDER BY (created_at, id)` when `id` is a Go-minted uuidv7 and `created_at` is `now()`. That is the same cross-clock comparison the repo already fixed once (`AGENTS.md:153`, `TestRunAfterComesFromTheDatabaseClockNotTheApplicationHost`, evidence `docs/evidence/warroom/2026-09-20-vizra-core-pr2-stabilise-VERIFY.md:106-107`). Pick one source per ordering.

---

# OQ RULINGS — one line each

- **OQ-1 (enum vs text+CHECK):** **Split.** `user_role` = native enum (ADR-003 says "ordered enum on `users.role`"; measured: `ALTER TYPE ADD VALUE ... BEFORE` works in a tx on 18.6, the value is unusable until commit → widening needs its own migration with `-- no-down:`); `credential_kind` = `text + CHECK` matching house style, because it has no ordering and text CHECKs widen in one reversible annotated migration. Correct the plan's claim that widening a CHECK is refused by migrate-lint — it is *annotated*, not refused (`scripts/migrate-lint.sh` §4, `-- allow-destructive:`).
- **OQ-2 (`VIZRA_OWNER_CLAIM_ANNOUNCE` default):** Backend concurs with `stderr` default + `vizra claim-token` as documented primary; and the CLI's database access is already consistent — `cmd/vizra/migrate.go:20` and `cmd/vizra/doctor.go:80` both use `config.Load()`, and `doctor.go:127` already opens a pool. No new config plumbing. Security seat owns the default.
- **OQ-3 (`GET /setup/claim-status` not in surfaces.api):** **Add it** to VZ-INSTALL-003's `surfaces.api` — the approved "already claimed" frame cannot exist without it, and one bit is the right payload. Chair owns the ledger edit.
- **OQ-4 (409 for already-claimed):** **Accept 409**, and add `case http.StatusConflict: return "conflict"` to `httpCodeName` (internal/httpapi/middleware.go:162-183). Do not add 422 speculatively.
- **OQ-5 (claim does not sign in):** **Accept.** No session at M1-A; M1-B adds `Set-Cookie` to the same operation, which is a non-breaking spec addition. Chair must tell the `vizra-user` builder to redirect to `/login`.
- **OQ-6 (the "Vizra version tag" on the argon2id hash):** **Reasonable reading, adopt the plain PHC string — record as an ADR-003 clarification, not an amending ADR.** The embedded `m,t,p` fully serve the ADR's stated *purpose* ("so parameters can be raised later and old hashes re-derived on next sign-in without a second column"): parse them, compare to the configured target, rehash on login. The `$argon2id$` identifier also covers a future algorithm change. If the chair wants strict literalism, PHC's standard `keyid=` parameter field is the compliant slot — but x/crypto encodes and parses nothing, so you hand-roll either way. With R6's widened CHECK, the schema does not need to change for a parameter raise.
- **OQ-7 (audit FK `ON DELETE RESTRICT`):** **RESTRICT is forced and correct** — SET NULL violates the frozen `audit_events_actor_identified` CHECK. But it is **not** cost-free (FINDING 2): drop `owner_claim_tokens.consumed_by`, add the anonymisation carve-out or the header sentence, and add the "user with audit rows cannot be deleted" test. Trusted-proxy config in M1-B: agreed.
- **OQ-8 (per-field error envelope deferred):** **Safe to defer, with one condition.** Adding an optional `fields` property to the inner `error` object is a non-breaking OpenAPI change even under `additionalProperties: false` (the constraint binds *response* instances, and no M1-A response would carry it), so vizra-user's generated client gains an optional field and nothing breaks. Condition: the M1-A 400 `message` must name the single first offending field in prose, and the claim form validates client-side against the regexes the spec already carries — that delivers the approved "2 problems" screen with no contract change.
- **OQ-9 (`vizra claim-token` CLI surface):** **Accept** and record it on VZ-INSTALL-003's `surfaces.cli`. It is the only aggregation-safe path and costs one file in an existing command tree.
- **OQ-10 (does ADR-003's "Setup wizard" CSRF row bind this endpoint?):** **Backend concurs with the builder: no.** The row's own Precedent citation is `C/internal/setupweb/guard.go` — a separate setup web server, not the claim API — and VZ-INSTALL-003's `surfaces.ui` is `/setup/claim`, a browser page at the public origin. The loopback reading also contradicts ADR-007's precedence rule naming owner claim as a surface an anonymous visitor keeps on a private site. Final call is the security seat's; I concur and ask the chair to record the interpretation in writing, because a later reader will hit the same row.
- **OQ-11 (new, from FINDING 5):** does boot mint unconditionally while unclaimed (N replicas → N tokens, ledger sentence intact) or only when no live token exists (deterministic, changes VZ-INSTALL-003's recovery case)? Chair's call; I recommend unconditional + generation in the announcement as the smallest change.

---

# NOT WORTH DOING

- **`citext`.** An extension dependency, per-database install, unavailable on some managed PostgreSQL, and it buys nothing over the generated fold column I measured working on 18.6.
- **Hiding the claimed state behind 404.** The plan's reasoning is right: the status endpoint must keep answering for the approved "already claimed" screen, so concealing only the POST leaks the same bit next door.
- **argon2 on the claim token.** Correct as-is: 256 bits of uniform randomness has nothing to grind, and a slow KDF on an unauthenticated endpoint is a CPU amplifier.
- **A `users.public_key` column now.** ADR-007's entity table gives `public_key` to assets, albums, collections, galleries and groups — not users. `/u/{username}` and `GET /api/v1/users/{username}` make username the profile key.
- **Dropping `users_one_owner` because MUT-2 does not turn test #2 red.** Keep it. The row guard holds *this* path; the index is the only defence the day a second writer (admin create-user, an import, a restore) exists. The plan is right to report the non-reddening mutation rather than hide it, and right to give the index its own direct test.
- **A retry loop on the claim transaction.** Unnecessary once FINDING 4 pins READ COMMITTED; a retry would only mask a serialization failure that should not occur.
- **PG 18's native `uuidv7()` for this slice.** Consistent with nothing else in the tree (`uuid.NewV7()` at `internal/jobs/jobs.go:164` and `internal/httpapi/middleware.go:28`), and nothing in core refuses a pre-18 server, so it would split the repo silently. Revisit only behind a `doctor` server-version check.
- **Adding `422` to `httpCodeName`.** No operation needs it; an unused code is a future disagreement.

---

**Position summary.** The plan's core mechanics are right — constraint-decided race, SHA-256-only token storage, hash-after-verify ordering, the honest mutation matrix, the single-bit status body — and I would not re-litigate any of them. What must change before code is six things that freeze: the `users_one_owner` predicate (an owner tombstone currently bricks the instance), the RESTRICT-plus-immutable-trigger deadlock on user deletion, the byte/character mismatch between the OpenAPI email bound and the SQL CHECK, the unstated isolation level, multi-replica boot minting, and the unauthenticated write path into an undeletable audit table. What would change my mind on FINDING 1 is an owner-transfer design that works without releasing the index key; on FINDING 2, an owner ruling that Vizra performs no user erasure, ever.
