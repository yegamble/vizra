# Execution plan: VZ-INSTALL-003 (M1-A) — secure one-time owner claim

**Status: PLAN ONLY (phase 1).** No product code, no migration file and no branch push exists for
this slice. Phase 2 begins only after the `vizra-security` and `vizra-core` seats have reviewed this
document and the chair has ruled on the open questions in §9.

## Context

| | |
|---|---|
| Ledger ID | `VZ-INSTALL-003` — "Secure one-time owner claim" |
| Issue | `docs/issues/VZ-ISSUE-005.md` (M1: owner claim, sessions, roles) |
| Slice position | **first of three**. M1-B = `VZ-AUTH-001` (sessions, sign-in/out, CSRF). M1-C = `VZ-AUTH-004` (role matrix). |
| Repo | `vizra-core` (`github.com/yegamble/vizra-core`) |
| Worktree | `/Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim` |
| Branch | `feat/m1-owner-claim` |
| Base | `4a80a1e3f36b8001c2954d0568bea29268e739fe` (`origin/main`) |
| Plan file | this file — the **only** file this slice writes in the meta checkout |

The main `vizra-core` checkout at `/Users/yosefgamble/github/vizra/vizra-core` belongs to another
builder and is never touched by this slice.

### Preflight (run 2026-09-21, before any design work)

| Dependency | Result |
|---|---|
| `go version` | `go1.26.2 darwin/arm64` — OK (repo floor `go 1.26.0`, toolchain `go1.27.1`) |
| `docker version` (server) | `29.8.0` — OK |
| `docker compose version` | `v5.5.1` — OK |
| `psql --version` | `PostgreSQL 16.15` (Homebrew client) — OK |
| Host | arm64, 8 CPU, 24 GiB RAM, 27 GiB free on `/` |
| `gh --version` | `2.98.0` — OK |
| PostgreSQL server for design validation | `postgres:17-alpine` → **17.11** in a scratch container (CI pins postgres 18 by digest) |
| `sqlc` | **NOT CHECKED IN PHASE 1.** `make sqlc-verify` fails hard when sqlc is absent. Phase 2 must verify `sqlc v1.31.1` is installed *before* writing queries, or the lane is **BLOCKED**, never a pass. |
| Cache (Valkey/Redis) for `VIZRA_TEST_CACHE_URL` | **NOT STARTED IN PHASE 1.** Required for `make test-integration`; phase 2 preflights it first. |

Nothing below is claimed as passing. Measurements that were actually taken are marked **measured**
and carry their command.

---

## 1. Scope

**In scope.** An unclaimed `vizra-core` instance mints a one-time 256-bit owner-claim token at API
boot, stores only its SHA-256 digest, and makes it obtainable by the operator without the token
entering the structured log stream. `POST /api/v1/setup/claim-owner` exchanges that token plus a
username, email and password for **the** owner account, exactly once, with the "exactly one owner,
ever" property enforced by a PostgreSQL constraint rather than by application locking. This slice
also discharges two obligations that migration `0003_audit_events` explicitly deferred to "the first
M1 writer": the `ip_prefix` masking function and the `audit_events` immutability trigger plus its
`users` foreign key.

**Explicitly NOT in scope** — none of this is built, stubbed, or faked here:

| Not built | Owner |
|---|---|
| Sessions, the `sessions` table, `__Host-vizra_session`, sign-in, sign-out, session revocation | M1-B (`VZ-AUTH-001`) |
| Open registration / sign-up routes | M1-B |
| CSRF / same-origin middleware (ADR-003's `Origin` + `Sec-Fetch-Site` table) | M1-B |
| The role matrix per route, `PATCH /admin/users/{id}/role`, `user_groups` | M1-C (`VZ-AUTH-004`) |
| API keys, TOTP, step-up tokens, password reset | M2 |
| The `/setup/claim` UI itself | a later `vizra-user` slice; this slice delivers the API it consumes |
| Wiring `sites.privacy_mode` → `authz.Options.SitePrivate` | open seam, not this slice |

**What M1-B and M1-C need from this slice, so the seams are right.** These are the deliberate
hand-offs; §2 builds them now so the later slices are additive:

1. **`users`** with `id`, `username`/`username_fold`, `email`/`email_fold`, `role`, `disabled_at`,
   `tombstoned_at`. M1-B re-reads `role`, `disabled_at` and `tombstoned_at` on every authenticated
   request (ADR-003 §Sessions: "session ⋈ user (role, disabled, tombstoned) with no in-process
   cache"), so those columns must exist from day one; append-only makes adding them later legal but
   forces a second migration for no reason.
2. **`credentials`** keyed `(user_id, kind)` with a `password` kind. M1-B's sign-in verifies against
   it; M2 adds `totp` as a new enum value, additively.
3. **`user_role`** as an ordered PostgreSQL enum whose rank order matches `authz.Role.AtLeast`.
   M1-C's matrix test depends on the order being a schema fact.
4. **`requireClaimed`** — an exported guard M1-B attaches to every account-creating route.
5. **`internal/audit`** — the emitter, the action grammar, and the frozen `ip_prefix` writer. Every
   later slice that audits anything uses it rather than calling `sqlcgen.InsertAuditEvent` directly.
6. **A per-route request-body limit helper.** None exists today; M1-B's login body and M1's upload
   routes both need one, and `cmd/api`'s transport timeouts comment already anticipates per-route
   budgets.

---

## 2. Migration `0005` — DDL in full

File pair, matching `scripts/migrate-lint.sh`'s regex and the gapless 1..N rule:

- `migrations/0005_users_credentials_owner_claim.up.sql`
- `migrations/0005_users_credentials_owner_claim.down.sql`

then `make migrations-manifest` (regenerating `migrations/manifest.sha256`) and `make migrate-lint`.
The up file is purely additive, so it needs no `-- allow-destructive:` annotation; the down file is
destructive by nature, which the linter only polices in up files.

### 2.1 How it fits the database-per-tenant model

ADR-007 §"Site and tenant seam" is explicit: "There is no `tenant_id` column and no per-tenant
schema anywhere in core", and `0001_sites.up.sql`'s own header repeats "There is deliberately NO dsn
column and NO tenant_id column anywhere". Therefore **`users` carries no `site_id` and no
`tenant_id`**, and "exactly one owner, ever, **per site**" is literally "exactly one owner row per
database", because one database *is* one site (`sites_singleton`). Under tenancy (M5) each tenant is
a separate database, so the same unmodified index gives the same guarantee per tenant. This is the
only reading that does not preclude ADR-007's chosen isolation mode.

### 2.2 Up file

```sql
-- 0005: the owner account, its password credential, and the one-time claim token
-- that creates it (VZ-INSTALL-003, ADR-003 §Credentials, ADR-007 §Entities and keys).
--
-- Three invariants are DATABASE facts here, not application conventions:
--   1. users_one_owner        — at most one row with role 'owner' can exist, ever.
--   2. owner_claim_tokens PK  — at most one claim token row can exist, ever.
--   3. audit_events_no_update_or_delete — the audit trail is append-only.
--
-- There is no site_id or tenant_id column: isolation under tenancy is
-- database-per-tenant (ADR-007), so "one owner per site" IS "one owner per
-- database" and needs no discriminator.

-- Rank order is load-bearing: it must equal authz.Role.AtLeast's ranking, and a
-- future role is added with ALTER TYPE ... ADD VALUE, which is additive. A
-- text + CHECK column would make the same change destructive under migrate-lint.
CREATE TYPE user_role AS ENUM ('guest', 'member', 'manager', 'admin', 'owner');

CREATE TYPE credential_kind AS ENUM ('password');

CREATE TABLE users (
    id             uuid        PRIMARY KEY,              -- uuidv7, minted in Go
    username       text        NOT NULL,
    username_fold  text        NOT NULL,                 -- lower(username); the uniqueness key
    email          text        NOT NULL,
    email_fold     text        NOT NULL,
    role           user_role   NOT NULL DEFAULT 'member',
    display_name   text        NULL,
    disabled_at    timestamptz NULL,                     -- M1-B re-reads this per request
    tombstoned_at  timestamptz NULL,                     -- M1-B re-reads this per request
    created_at     timestamptz NOT NULL DEFAULT now(),
    updated_at     timestamptz NOT NULL DEFAULT now(),

    -- 3..30 characters, letters/digits/hyphen/underscore, leading alphanumeric.
    -- Matches the approved claim copy (docs/design/figma/FIRST-SLICE-auth-system.md
    -- key claim.username.help) so the API cannot accept what the form forbids.
    CONSTRAINT users_username_shape CHECK (username ~ '^[A-Za-z0-9][A-Za-z0-9_-]{2,29}$'),
    CONSTRAINT users_username_fold  CHECK (username_fold = lower(username)),
    CONSTRAINT users_email_shape    CHECK (
        email ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'
        AND octet_length(email) BETWEEN 3 AND 254),
    CONSTRAINT users_email_fold     CHECK (email_fold = lower(email)),
    CONSTRAINT users_display_name_bounded CHECK (
        display_name IS NULL OR octet_length(display_name) BETWEEN 1 AND 128)
);

CREATE UNIQUE INDEX users_username_fold_key ON users (username_fold);
CREATE UNIQUE INDEX users_email_fold_key    ON users (email_fold);

-- THE invariant of this slice. A partial unique index over a single-valued
-- expression: every row with role 'owner' carries the same key, so the second
-- one raises 23505. This is what decides a concurrent claim race — not an
-- advisory lock, not SELECT ... FOR UPDATE, not a mutex in Go.
-- Deliberately NOT filtered on tombstoned_at: "exactly one owner, EVER".
-- ADR-003 says the owner cannot be demoted; recovering from a tombstoned owner
-- is an owner-transfer route in a later slice, not a hole in this index.
CREATE UNIQUE INDEX users_one_owner ON users (role) WHERE role = 'owner';

CREATE TABLE credentials (
    id          uuid            PRIMARY KEY,             -- uuidv7
    user_id     uuid            NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    kind        credential_kind NOT NULL,
    -- argon2id PHC string. NEVER a plaintext secret, never a reversible value.
    secret      text            NOT NULL,
    created_at  timestamptz     NOT NULL DEFAULT now(),
    updated_at  timestamptz     NOT NULL DEFAULT now(),

    -- The stored form is asserted in the schema so a regression that writes a
    -- plaintext or bcrypt value fails the INSERT rather than being discovered
    -- by a reader. ADR-003 pins argon2id and the '$argon2id$v=19$' prefix.
    CONSTRAINT credentials_password_is_argon2id CHECK (
        kind <> 'password' OR secret LIKE '$argon2id$v=19$m=%,t=%,p=%$%$%'),
    CONSTRAINT credentials_secret_bounded CHECK (octet_length(secret) BETWEEN 1 AND 512)
);

CREATE UNIQUE INDEX credentials_one_per_user_per_kind ON credentials (user_id, kind);

CREATE TABLE owner_claim_tokens (
    -- Boolean primary key pinned TRUE by the CHECK: the table can hold at most
    -- one row, so "the live claim token" is a schema fact and a re-mint is a
    -- plain upsert on a fixed key. (0001 uses the alternative house idiom,
    -- CREATE UNIQUE INDEX ... ON sites ((true)); both were validated — see §7.)
    id            boolean     PRIMARY KEY DEFAULT true,
    -- SHA-256 of the normalised raw token. The raw token is NEVER stored,
    -- never returned, and unrecoverable by design: a lost token is re-minted.
    token_sha256  bytea       NOT NULL,
    -- Increments on every re-mint. This is what audit events reference, so a
    -- claim can be traced to a generation without any secret material.
    generation    bigint      NOT NULL DEFAULT 1,
    minted_at     timestamptz NOT NULL DEFAULT now(),
    expires_at    timestamptz NOT NULL,
    consumed_at   timestamptz NULL,
    consumed_by   uuid        NULL REFERENCES users (id) ON DELETE RESTRICT,
    -- Set when a boot finds users already present: the leftover token is
    -- retired without minting a replacement (an implicitly claimed instance
    -- must never hold a live credential that creates an owner).
    superseded_at timestamptz NULL,

    CONSTRAINT owner_claim_tokens_singleton  CHECK (id),
    CONSTRAINT owner_claim_tokens_digest_len CHECK (octet_length(token_sha256) = 32),
    CONSTRAINT owner_claim_tokens_ttl        CHECK (expires_at > minted_at),
    CONSTRAINT owner_claim_tokens_generation CHECK (generation >= 1),
    -- A consumed token names the account it created; an unconsumed one names none.
    CONSTRAINT owner_claim_tokens_consumed_pair CHECK (
        (consumed_at IS NULL) = (consumed_by IS NULL)),
    -- A token is consumed or superseded, never both.
    CONSTRAINT owner_claim_tokens_one_terminal_state CHECK (
        consumed_at IS NULL OR superseded_at IS NULL)
);

-- ---------------------------------------------------------------------------
-- The two obligations 0003_audit_events deferred to "the first M1 writer".
-- ---------------------------------------------------------------------------

-- ON DELETE RESTRICT, not SET NULL: audit_events_actor_identified asserts
-- (actor_kind = 'user') = (actor_user_id IS NOT NULL), so nulling the id under
-- a surviving actor_kind='user' row would violate a CHECK that 0003 froze.
-- Users are tombstoned (users.tombstoned_at), not hard-deleted, so RESTRICT
-- costs nothing real and an audit trail never loses its actor.
ALTER TABLE audit_events
    ADD CONSTRAINT audit_events_actor_user_fk
    FOREIGN KEY (actor_user_id) REFERENCES users (id) ON DELETE RESTRICT;

CREATE FUNCTION audit_events_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'audit_events is append-only (attempted % on id %)',
        TG_OP, OLD.id USING ERRCODE = '42501';
END;
$$;

-- Row-level, so TRUNCATE is deliberately still permitted: the integration
-- harness resets a test database by DROP SCHEMA / TRUNCATE, and there is no
-- TRUNCATE path in any production code. UPDATE and DELETE, which are what a
-- tamper looks like, are refused.
CREATE TRIGGER audit_events_no_update_or_delete
    BEFORE UPDATE OR DELETE ON audit_events
    FOR EACH ROW EXECUTE FUNCTION audit_events_append_only();
```

### 2.3 Down file

```sql
DROP TRIGGER IF EXISTS audit_events_no_update_or_delete ON audit_events;
DROP FUNCTION IF EXISTS audit_events_append_only();
ALTER TABLE audit_events DROP CONSTRAINT IF EXISTS audit_events_actor_user_fk;
DROP TABLE IF EXISTS owner_claim_tokens;
DROP TABLE IF EXISTS credentials;
DROP TABLE IF EXISTS users;
DROP TYPE IF EXISTS credential_kind;
DROP TYPE IF EXISTS user_role;
```

`down` returns the schema to exactly the `0004` state: the owner, the credential, the claim token,
the audit FK and the audit immutability trigger all disappear, and `audit_events` rows survive with
`actor_user_id` values that no longer reference anything — which is correct, because a down
migration is a rollback of *schema*, and destroying audit history to satisfy a constraint that no
longer exists would be the worse failure. Drop order is reverse-dependency; `credentials` and
`owner_claim_tokens.consumed_by` both reference `users`, so `users` drops last.

---

## 3. Token lifecycle

### 3.1 Minting

**Who.** `cmd/api` at boot only. The worker never mints (it has no operator-visible console) and
neither does any HTTP path.

**When.** Inside one transaction holding `pg_advisory_xact_lock(hashtext('vizra.owner_claim.mint'))`
so two replicas cannot interleave a lost update:

| Observed state | Action |
|---|---|
| `NOT EXISTS (SELECT 1 FROM users)` | **mint**: upsert a fresh digest, `generation = generation + 1`, clear `consumed_*`/`superseded_at`, set `expires_at = now() + ttl`. Announce once (§3.4). |
| users exist **and** a live token row exists | **supersede**: `superseded_at = now()`, mint nothing, announce nothing. Audit `setup.owner_claim.superseded`. |
| users exist, no live token | **no-op.** The instance is implicitly claimed and must never mint again — the ledger's outcome sentence, verbatim. |

A restart while unclaimed therefore re-mints and the previous token stops verifying, because the
single row's digest was overwritten. That is the ledger's `recovery` case ("Restart re-mints; old
token invalid") and the approved copy's footnote (`claim.footnote`).

The advisory lock guards **minting**, not the claim. This matters: the brief requires the *claim
race* be decided by a constraint, and it is (§3.6). Serialising two boots is a different problem
with no constraint available, since both boots legitimately write the same row.

**Entropy and encoding.** 32 bytes from `crypto/rand`, encoded as **64 lowercase hex characters**
(256 bits). Hex, not base64url, because the approved copy states "The token is 64 hexadecimal
characters" (`claim.help.body`) and because hex has no `-`/`_`/`=` for an operator to lose when
copying out of a terminal. Presented tokens are normalised — surrounding whitespace trimmed, ASCII
lowercased — before hashing, so a paste that picked up a newline still works.

**Hash at rest.** `sha256.Sum256([]byte(normalisedToken))`, stored as `bytea(32)`. Not argon2: the
token is 256 bits of uniform randomness, so there is nothing to grind, and a deliberately slow KDF on
an unauthenticated endpoint would only hand an attacker a CPU amplifier. ADR-003 §Precedent already
pins SHA-256-only storage for this class of credential.

**Expiry.** `expires_at = now() + VIZRA_OWNER_CLAIM_TTL`, default **24h**, evaluated in SQL against
PostgreSQL's clock.

### 3.2 Verification

1. Fetch the single row (`SELECT ... FROM owner_claim_tokens`) — a plain fetch, **never** a lookup
   keyed by the attacker-supplied value, so index-probe timing cannot become an oracle.
2. `subtle.ConstantTimeCompare(sha256(presented), row.TokenSHA256)`.
3. Only if that returns 1, run the redeem statement, and pass **the row's own digest**, never the
   presented one. Attacker-controlled bytes never reach SQL.

### 3.3 After a successful claim

Minting stops permanently (users now exist → the "no-op" row of §3.1). `POST
/api/v1/setup/claim-owner` answers **409 Conflict**, code `conflict`, and `GET
/api/v1/setup/claim-status` answers `{"claimed": true}`.

**Why 409 and not "as if it does not exist" (404).** Concealment buys nothing here: the status
endpoint must keep answering after the claim, because the approved "already claimed" frame
(`35:1280` / `35:1435`) is the screen a returning operator is supposed to see, and an instance with
content is observably claimed anyway. Hiding only the POST would break that designed screen while
leaking the same bit next door. 403 is wrong because the ledger already uses 403 for the opposite
condition — a signup path refused *while unclaimed* — and reusing it would make the two
indistinguishable to `vizra-user`. 409 is the accurate statement: the request conflicts with the
resource's current state. This resolves the design's open question Q-D2a-2 (see §9, OQ-4).

### 3.4 How the operator obtains the token — the hard question

`AGENTS.md` forbids logging credentials, and vizra-core mechanises it
(`TestRedactionOfEveryValueClass`, and the rule row "No credential, signed URL, session id or API key
ever reaches a log line"). But `VZ-INSTALL-003`'s outcome says "prints it to its log", ADR-003 says
"printed once", `PRODUCT_SPEC.md` §15 step 4 makes the golden path "the claim token read from the API
log", and the approved copy tells the operator to run their log command. The privacy case draws the
actual line: "Token never appears in HTTP responses or **non-local** logs."

**Mechanism A — the structured logger (`obs.NewLogger` → slog).** Rejected outright. `internal/obs`'s
`secretKeys` includes `token`, so the honest key name yields `[redacted]` and the operator gets
nothing; any key name that survives redaction ships a JSON field that Loki, Vector or CloudWatch
will index and retain, and `valuePatterns` does not match a bare hex string, so the leak would be
silent. This is the mechanism `AGENTS.md` actually forbids.

**Mechanism B — one plain line written directly to `os.Stderr`, outside the slog handler.**
*For:* it is the only path discoverable from a bare `docker compose up -d` with no installer, which
is exactly M1's reality (`vizra setup` and `install.sh` are VZ-ISSUE-004); it satisfies ADR-003,
the ledger sentence, PRODUCT_SPEC §15 and the approved copy without changing any of them; being
unstructured, no shipper field-extracts it.
*Against:* container stderr is still captured by the log driver, so on an instance with aggregation
the token does reach non-local logs — the privacy case's stated boundary.

**Mechanism C — a host-side `vizra claim-token` subcommand.** `cmd/vizra` already exists (`doctor`,
`migrate`, `version`), so this is one file. It takes the advisory lock, mints a fresh token
(superseding the live one) and writes it to **stdout**. Run as `docker compose exec api vizra
claim-token`, that output goes to the operator's terminal and is *not* part of the api container's
captured log stream — the property Mechanism B cannot have.
*Against:* it must be discovered, and `VZ-INSTALL-003`'s `surfaces.cli` is `[]`.

**Recommendation: C as the documented primary, B as the default-on fallback, A never.**

- `VIZRA_OWNER_CLAIM_ANNOUNCE` = `stderr` (default) | `off`. At `stderr`, `cmd/api` writes exactly
  one line to a dedicated `io.Writer` (`os.Stderr`) that is never the slog handler.
- `vizra claim-token` always works while unclaimed, regardless of that setting.
- README/COMMANDS state: *if you ship this instance's logs, set `VIZRA_OWNER_CLAIM_ANNOUNCE=off` and
  use `docker compose exec api vizra claim-token`.*
- `vizra doctor` gains an "instance unclaimed" check that prints that exact command.

Defaulting to `off` is the more paranoid choice and I am not taking it unilaterally, because it would
break the documented golden path and contradict approved copy at a milestone with no installer. If
the security seat prefers `off`, `PRODUCT_SPEC.md` §15 step 4 and the copy key `claim.help.body` must
change in the same decision — documents this slice does not own. See §9, OQ-2.

The announcement is guarded by tests, not by care: a log-scrape test boots the API with a **plain**
(non-redacting) handler into a mutex-guarded buffer — the existing
`TestAWorkerWithAPlainHandlerLogsNoCredentials` pattern — and asserts the raw token never appears
there, while a second test asserts it appears exactly once on the dedicated writer.

### 3.5 Does the claim sign the owner in?

**No, not at M1-A** — sessions do not exist until M1-B, and faking one would be mock data in a
production path. `201` returns `{"owner": {"id", "username", "role"}}` and the OpenAPI `description`
says in terms that the owner must now sign in, which M1-B delivers. M1-B then adds `Set-Cookie` to
the *same* operation, which is a backward-compatible addition needing no schema change.

This is a real mismatch with the approved design: the control matrix row `setup.claim.submit`
promises "owner row + session cookie → redirect to library". At M1-A `vizra-user` must redirect to
`/login` instead. Flagged as §9, OQ-5 rather than resolved silently.

### 3.6 The claim statement — one transaction, constraint-decided

```sql
-- name: ClaimOwner :one
WITH consumed AS (
    UPDATE owner_claim_tokens
       SET consumed_at = now(), consumed_by = sqlc.arg('user_id')
     WHERE id
       AND token_sha256  = sqlc.arg('token_sha256')   -- the ROW's digest, not the presented one
       AND consumed_at   IS NULL
       AND superseded_at IS NULL
       AND expires_at    > now()                      -- PostgreSQL's clock (ADR-004)
    RETURNING generation
),
owner AS (
    INSERT INTO users (id, username, username_fold, email, email_fold, role)
    SELECT sqlc.arg('user_id'), sqlc.arg('username'), lower(sqlc.arg('username')),
           sqlc.arg('email'), lower(sqlc.arg('email')), 'owner'
      FROM consumed
    RETURNING id, username, role, created_at
),
cred AS (
    INSERT INTO credentials (id, user_id, kind, secret)
    SELECT sqlc.arg('credential_id'), owner.id, 'password', sqlc.arg('password_hash')
      FROM owner
    RETURNING id
)
SELECT owner.id, owner.username, owner.role, owner.created_at,
       (SELECT generation FROM consumed) AS token_generation
  FROM owner, cred;
```

**Crash between the owner insert and the token consumption is impossible**: they are one statement in
one implicit transaction. Either the token is consumed *and* the owner and credential exist, or
nothing happened. The audit event is inserted in the *same* explicit transaction immediately after,
which is also required for correctness — `audit_events_actor_user_fk` means an event naming the new
owner cannot commit unless that owner row commits with it.

**Why the ordering is what it is.** The guarded `UPDATE` must be the CTE the `INSERT` selects from.
A data-modifying CTE always executes; if the insert came first and the guarded update matched
nothing, the owner row would still have been written. Making `owner` select `FROM consumed` forces
the redeem to produce a row before any user exists.

**Two independent enforcers, each with its own test and its own mutation.** Measured behaviour on
real PostgreSQL 17.11, 24 concurrent claims against one valid token (transcript §7):

| Configuration | Result |
|---|---|
| Baseline (guard + `users_one_owner`) | 1 × `INSERT 0 1`, 23 × `INSERT 0 0` (no row → declared error). `owners = 1` |
| `consumed_at IS NULL` removed, index present | 1 × insert, **23 × `23505` on `users_one_owner`**. `owners = 1` — the index is demonstrably load-bearing |
| Guard present, index dropped | 1 × insert, 23 × no row. `owners = 1` — the row guard alone holds *this* path |

So the race is decided at the database in both directions, and §6's mutation matrix names which test
each removal turns red. The third row is reported, not hidden: dropping the index does **not** turn
the HTTP race test red, which is why the index carries its own direct test (`#11`).

---

## 4. Endpoints and the OpenAPI delta

`api/openapi.yaml` is hand-written and is the source; drift fails in both directions
(`TestEveryRouteHasASpecOperation`, `TestEverySpecOperationHasARoute`). It currently holds exactly
four probe operations, no `securitySchemes`, and an `Error` schema that no operation references.

**`TestM0ContractIsTheFourProbes` fails the moment a fifth operation is added and must be amended in
this diff** — renamed to assert the M1-A contract is the four probes plus the two setup operations.
That is a required change to an existing test and is called out here so it is reviewed, not
discovered (`AGENTS.md`: "Explain test changes"). No assertion is weakened: the test keeps
enumerating the complete expected set.

### 4.1 `GET /api/v1/setup/claim-status` — `getSetupClaimStatus`, `security: []`

```yaml
SetupClaimStatus:
  type: object
  additionalProperties: false
  required: [claimed]
  properties:
    claimed: { type: boolean }
```

**The privacy case, stated as a rule:** an unauthenticated caller learns **exactly one bit**. The
response must never carry `minted_at`, `expires_at`, `generation`, a "token is live" flag, a user
count, or the owner's id, username or email. One bit is what the claim page needs to choose between
the form and the "already claimed" screen; everything else is either secret material, a
freshness oracle for a token-guessing attacker, or an enumeration aid. `Cache-Control: no-store` is
already applied by `securityHeadersMiddleware` on every route.

This path is **not** in `VZ-INSTALL-003`'s `surfaces.api` — see §9, OQ-3.

### 4.2 `POST /api/v1/setup/claim-owner` — `claimOwner`, `security: []`

```yaml
ClaimOwnerRequest:
  type: object
  additionalProperties: false
  required: [token, username, email, password]
  properties:
    token:    { type: string, pattern: '^[0-9a-fA-F]{64}$' }
    username: { type: string, minLength: 3,  maxLength: 30, pattern: '^[A-Za-z0-9][A-Za-z0-9_-]{2,29}$' }
    email:    { type: string, format: email, minLength: 3, maxLength: 254 }
    password: { type: string, minLength: 12, maxLength: 256 }

ClaimOwnerResponse:
  type: object
  additionalProperties: false
  required: [owner]
  properties:
    owner:
      type: object
      additionalProperties: false
      required: [id, username, role]
      properties:
        id:       { type: string, format: uuid }
        username: { type: string }
        role:     { type: string, enum: [owner] }
```

| Status | `error.code` | When |
|---|---|---|
| 201 | — | Owner created. **No session cookie at this milestone** (§3.5); the `description` says so. |
| 400 | `bad_request` | Malformed JSON or a field outside its bounds. |
| 403 | `forbidden` | Token not accepted — mistyped, already used, superseded by a restart, or expired. **One message for all four**, per the approved copy `claim.error.body`: the server genuinely cannot distinguish them from a digest comparison, and four messages would be a lie and an oracle (Q-D2a-1). |
| 409 | `conflict` | The instance already has an owner (§3.3). |
| 413 | `payload_too_large` | Body over the 8 KiB route limit. |
| 429 | `rate_limited` | §5.1. |
| 503 | `unavailable` | Database unreachable — ADR-003's "A database outage returns 503, never 401". |

All of them use the existing `Error` schema, which finally acquires references.

**Two shared-middleware changes this forces**, both called out for review:
`httpCodeName` in `internal/httpapi/middleware.go` maps no 409 and no 422, so **409 → `conflict`**
must be added. Field-level error reporting (the design's "There are 2 problems" summary) needs an
envelope the `Error` schema does not have; M1-A uses a single 400 message and the per-field envelope
is deferred to M1-B, where sign-up is the real multi-field case (§9, OQ-8).

**Password handling.** argon2id from `golang.org/x/crypto/argon2`, `IDKey(password, salt, time,
memory, threads, keyLen)`.

- Parameters: **m = 19456 KiB (19 MiB), t = 2, p = 1, 16-byte random salt, 32-byte tag.**
- **These are not mine to propose.** ADR-003 §Credentials already pins them, and an Accepted ADR is
  immutable. The brief's `[to confirm in M0]` marker does not exist for argon2 — `grep -rn "to confirm
  in M0" docs/adr/` returns nine hits, none in ADR-003. I therefore *verified* the pin instead of
  re-deciding it.
- Source, fetched directly rather than taken from the ADR's own citation: the OWASP Password Storage
  Cheat Sheet lists `m=19456 (19 MiB), t=2, p=1` as one of five configurations of equivalent
  security, and states "use the Argon2id variant".
- **Measured on this machine** (`go test -bench`, `golang.org/x/crypto v0.57.0`, Apple M2, `-cpu 1`):
  **25.7 ms/op**. For reference `m=47104, t=1, p=1` measured 33.2 ms/op.
- **Estimate for the 2 vCPU floor host:** argon2id at `p=1` is memory-bandwidth-bound, and a shared
  cloud vCPU typically runs 2–3× slower than an M2 performance core on this workload, giving
  roughly **50–80 ms per derivation**. That is an estimate from a single local measurement, not a
  measurement on the floor host, and is labelled as such. Phase 2 does not upgrade it to a fact.
- Concurrency is bounded by a semaphore of `min(GOMAXPROCS, 4)` derivations, so peak transient
  memory is ≤ 76 MiB; waiters are released or fail on the request deadline, never queued unbounded.
- **Order of work matters more than the parameters:** the password is hashed *only after* the token
  comparison succeeds. An attacker without the token therefore never triggers a single argon2
  derivation, which removes the CPU/memory amplifier that an unauthenticated hashing endpoint would
  otherwise be. The residual timing difference (a valid token costs ~26 ms more) reveals only
  "your token was valid", which the 201 reveals anyway.
- Length bounds: 12–256 characters (12 from the approved copy `claim.password.help`).
- The password never appears in a log, an audit event, an error message or a response body. `obs`'s
  `secretKeys` already covers the key name `password`; a dedicated test scrapes for the literal.

**Request body bound.** `internal/httpapi` has **no** body-limit middleware today and the only size
floor in the system is `jobs.MaxPayloadBytes`. This slice adds a **per-route** helper (8 KiB here),
deliberately not a global one, matching the comment already in `cmd/api/main.go` that M1's upload
routes will set their own budget. Deadlines propagate from `c.Request().Context()` into every
database call and into the argon2 semaphore wait.

### 4.3 "Every signup path answers 403 while unclaimed"

This slice ships the mechanism — an exported `requireClaimed` guard plus its table test — and M1-B
attaches it to register and login. **At M1-A there are no signup routes, so this acceptance bullet
cannot be fully demonstrated here and I will not claim it.** What *is* demonstrable now is the
stronger fact for this milestone: the claim endpoint is the only account-creating path that exists,
and it requires the token, so "registration bots cannot become owner" holds by construction. The
bullet is recorded **PARTIAL, evidence owed by M1-B**, and named as such in the PR body.

---

## 5. Abuse and failure cases

### 5.1 Brute force and rate limiting

A 256-bit token is not guessable; the rate limit exists to bound request volume, log noise and any
future low-entropy override, not to defend the entropy.

- **Where the counter lives:** `cache.Limiter` (`internal/cache/ratelimit.go`), already plumbed into
  `httpapi.Deps` and currently read only for the readiness signal. This slice is its first request-path
  caller. `Allow(ctx, key, limit, window)`.
- **What it keys on:** two buckets, both must pass. Per-origin `site.CacheKey("rl","setup.claim", ipPrefix)`
  at **10 per 15 min**, and a global `site.CacheKey("rl","setup.claim","all")` at **60 per 15 min** so a
  distributed attacker is bounded too. The per-origin key uses the **masked /24 or /64 prefix**, not
  the full address, so the limiter never holds a full IP — the same privacy rule `audit_events`
  enforces in the schema. When the prefix is `NULL` (no usable address, or a forwarded header with no
  trusted-proxy configuration) the request counts only against the stricter global bucket rather than
  sharing a bucket with every other unattributable caller.
- **When Valkey is down:** ADR-003 decides this and I follow it rather than inventing a policy —
  `FallbackLimiter` flips to the per-process `MemoryLimiter` and readiness is marked degraded. So:
  **fail to a local limiter, not closed.** The justification specific to this endpoint is that the
  blast radius of a limiter outage is bounded by a different mechanism entirely: the endpoint can
  succeed *exactly once in the lifetime of the instance*, enforced by `users_one_owner`. A limiter
  outage costs request volume, never a second owner. Failing closed would instead make a cache
  outage into "the operator cannot claim their new instance", which is a worse trade for a bound the
  constraint already provides.

### 5.2 The rest

| Case | Behaviour |
|---|---|
| **Replay** (same token, unclaimed instance) | First wins; later attempts find `consumed_at IS NOT NULL` → no row → 403. |
| **Reuse after success** | The instance is now claimed, so the handler's claimed-check answers **409** before the token is ever examined. Correct screen, and no token oracle on a claimed instance. |
| **Concurrent claims** | N goroutines, real PostgreSQL: exactly one 201, N−1 × the declared error, `count(role='owner') = 1`. Loser mapping: no row returned → re-read claimed state → 409 if an owner now exists, else 403. Measured in §7. |
| **Crash between owner insert and token consumption** | Impossible — one statement, one transaction (§3.6). |
| **Restart** | Re-mint + invalidate (§3.1). |
| **Clock authority** | PostgreSQL's `now()` for `minted_at`, `expires_at`, `consumed_at`, `superseded_at` and the expiry predicate, per ADR-004's jobs ruling. `httpapi.Deps.Now` exists but must never decide token validity. |
| **Database down** | 503 `unavailable`, never 403 — ADR-003. A limiter or database error is returned, never swallowed into "invalid token"; failing open on a repository error is exactly the bug this flow replaces. |

### 5.3 Audit events

No audit-emission package exists and `action` / `subject_type` carry no CHECK, so the grammar is a
design decision this slice makes and later slices inherit. Proposed: **`<domain>.<object>.<verb-past>`,
lowercase snake_case**.

| `action` | `actor_kind` | `subject_type` | `subject_id` | `after` |
|---|---|---|---|---|
| `setup.owner_claim.minted` | `system` | `owner_claim_token` | generation | `{"expires_at": "..."}` |
| `setup.owner_claim.superseded` | `system` | `owner_claim_token` | generation | `null` |
| `setup.owner_claim.refused` | `anonymous` | `owner_claim_token` | `null` | `{"reason":"token_not_accepted"\|"already_claimed"\|"rate_limited"}` |
| `setup.owner_claim.succeeded` | `user` | `user` | owner uuid | `{"username":"…","role":"owner"}` |

- `audit_events_actor_identified` is satisfied in every row: only `succeeded` sets `actor_kind='user'`,
  and it carries the new owner's id.
- **Never recorded:** the token, its digest, the password, the password hash, or the **email**
  (`VZ-AUTH-001`'s privacy case is "no email in logs"; `username` is a public identifier and is fine).
  `subject_id` for a token is the *generation number*, which is exactly the traceability needed with
  zero secret material.
- `correlation_id` = the request id from `requestIDMiddleware`. `ip_prefix` = the new masked writer.

### 5.4 The `ip_prefix` writer

`0003_audit_events.up.sql`'s header froze this contract for "the first M1 writer", which is this
slice: parse with `netip.ParseAddr` and call `Unmap()` **first**; mask to /24 for IPv4 and /64 for
IPv6, never finer; format lowercase; return NULL when there is no usable address. `netip` appears
nowhere in the tree today. It lands in the new `internal/audit` package as one function with the
four named test cases the header requires, and the existing
`TestAuditEventsRefusesAFullIPAddress` becomes its schema-side backstop.

Forwarded headers are **not** trusted at M1-A: there is no trusted-proxy config key, so a request
carrying `X-Forwarded-For` with no such configuration yields `NULL` — the header's own prescribed
answer. Adding `VIZRA_TRUSTED_PROXIES` belongs with M1-B, where sign-in rate limiting makes it
load-bearing (§9, OQ-7).

---

## 6. Test plan

Integration tests run on **real PostgreSQL and real Valkey/Redis** through the existing harness:
`//go:build integration`, `VIZRA_TEST_DATABASE_URL` and `VIZRA_TEST_CACHE_URL`, `freshDatabase(t)`,
and `mustEnv` which **fatals rather than skips**. New file
`internal/integration/owner_claim_test.go` beside `golden_test.go`.

| # | Test | Level |
|---|---|---|
| 1 | `TestOwnerClaimCreatesExactlyOneOwnerAndConsumesTheToken` | integration |
| 2 | `TestOwnerClaimRaceYieldsExactlyOneOwner` — 32 goroutines: exactly one 201, 31 × 409/403, **zero 5xx**, `count(role='owner')=1`, one `succeeded` audit row | integration |
| 3 | `TestOwnerClaimRejectsAReusedToken` | integration |
| 4 | `TestOwnerClaimRejectsATokenSupersededByARestart` | integration |
| 5 | `TestOwnerClaimRejectsAnExpiredToken` | integration |
| 6 | `TestOwnerClaimOnAClaimedInstanceAnswers409` | integration |
| 7 | `TestClaimStatusRevealsOnlyTheClaimedBit` — asserts the decoded body has **exactly one key** | integration |
| 8 | `TestOwnerClaimTokenNeverReachesTheStructuredLog` — plain handler into a mutex-guarded buffer | integration |
| 9 | `TestOwnerClaimTokenNeverAppearsInAnyResponseBodyOrHeader` | integration |
| 10 | `TestOwnerClaimAuditEventsCarryNoSecretMaterial` — scrapes every audit row for token, digest, password, hash, email | integration |
| 11 | `TestASecondOwnerInsertIsRefusedByTheDatabase` — direct store call, expects `23505` on `users_one_owner` | integration |
| 12 | `TestOwnerClaimIsRateLimited` | integration |
| 13 | `TestOwnerClaimBodyIsBounded` — 413 over 8 KiB | integration |
| 14 | `TestAuditEventsCannotBeUpdatedOrDeleted` | integration |
| 15 | `TestIPPrefixMasksIPv4To24AndIPv6To64` + mapped + no-address | unit |
| 16 | `TestPasswordNeverAppearsInALogOrAnError` | unit + integration |
| 17 | `TestClaimTokenIsStoredOnlyAsASHA256Digest` | integration |
| 18 | `TestOwnerClaimAnswers503WhenTheDatabaseIsDown` | integration |
| 19 | `TestSignupPathsAreRefusedWhileUnclaimed` — table test over `requireClaimed`; **route-level evidence owed by M1-B** | unit |

### 6.1 Mutation matrix

Every acceptance bullet marked *demonstrated* gets a named mutation that must turn a named test red.
A mutation that does not change the tree is a **harness failure**, not a pass.

| ID | Controlled mutation | Must turn RED |
|---|---|---|
| MUT-1 | Drop `AND consumed_at IS NULL` from the redeem CTE | #2 — losers raise 23505 → 500, breaking "31 × 409, zero 5xx". **Confirmed on real PostgreSQL in phase 1 (§7).** |
| MUT-2 | `DROP INDEX users_one_owner` | #11. #2 stays GREEN and that is **recorded, not hidden** (§3.6). |
| MUT-3 | Store and compare the raw token instead of its SHA-256 | #17 |
| MUT-4 | Replace `subtle.ConstantTimeCompare` with `bytes.Equal` | **No test goes red** — a timing difference is not observable from a Go test. Recorded as a known limit; the protection is code review plus the fact that the compared values are digests of a 256-bit secret. Listed so the verifier is not told a false story. |
| MUT-5 | Announce the token through `deps.Logger` instead of the dedicated writer | #8 |
| MUT-6 | Remove `expires_at > now()` | #5 |
| MUT-7 | Add `minted_at` to the claim-status response | #7 |
| MUT-8 | Remove the per-route body limit | #13 |
| MUT-9 | Drop the audit immutability trigger | #14 |
| MUT-10 | Mask IPv4 to /32 instead of /24 | #15 and the existing `TestAuditEventsRefusesAFullIPAddress` |
| MUT-11 | Include `email` in the audit `after` blob | #10 |
| MUT-12 | Remove the `requireClaimed` guard | #19 |

**Harness.** Extend the one runnable precedent in the tree, `docs/evidence/fixtures/demonstrate.sh`,
into `docs/evidence/m1a-owner-claim/demonstrate.sh`. It must: refuse a dirty tree; apply exactly one
mutation; **record the target file's sha256 before and after and abort if they are equal** (this is
the "refuses to score a mutation that did not apply" requirement); run the named test and assert
RED; revert; re-run and assert GREEN. Both transcripts, with exit codes and the digest pair, are
committed under `docs/evidence/m1a-owner-claim/`.

### 6.2 Lanes

Focused while iterating, then every required lane: `make ci` — which is exactly `fmt-check vet
lint-imports migrate-lint config-template-check openapi-verify sqlc-verify ci-guard fixtures-verify
test-race` — plus `make test-integration` and `make test-integration-shuffle`. A missing tool
(`sqlc`, a reachable PostgreSQL, a reachable cache) is **BLOCKED** and reported at the top of the PR
body, never counted as a pass.

---

## 7. Phase-1 evidence already taken

Recorded now so phase 2 does not re-litigate settled mechanics. Scratch PostgreSQL:
`postgres:17-alpine` → **17.11**, container `vizra-m1a-plan-pg` (own name prefix; removed at the end
of phase 2).

1. **`CREATE UNIQUE INDEX users_one_owner ON users (role) WHERE role = 'owner'` works.** A second
   `INSERT ... 'owner'` returned
   `ERROR: duplicate key value violates unique constraint "users_one_owner_idx" DETAIL: Key (role)=(owner) already exists.`
2. **Enum rank order works**: `'owner'::user_role > 'admin'::user_role` → `t`.
3. **`CREATE UNIQUE INDEX ... ON t ((true)) WHERE consumed_at IS NULL` is accepted** — the
   alternative singleton idiom, and the one `0001_sites` already uses.
4. **The race, 24 concurrent claims** — the three configurations tabulated in §3.6, each ending with
   `owners=1`, and MUT-1 producing 23 unique violations.
5. **argon2id cost**, `golang.org/x/crypto v0.57.0`, Apple M2, `-cpu 1`, `-benchtime 30x`:
   ADR-003's `19456/t=2/p=1` → **25 682 853 ns/op**; `47104/t=1/p=1` → **33 221 896 ns/op**.
6. **OWASP source fetched directly** (not via the ADR): the Password Storage Cheat Sheet lists
   `m=19456 (19 MiB), t=2, p=1` among five equivalent configurations and recommends Argon2id.
7. **`golang.org/x/crypto` is already pinned at `v0.57.0` in `NOTICE`** (BSD-3-Clause) but is absent
   from `go.mod` and `go.sum`. Adding it is therefore a *pre-approved* pin, not a new licence
   decision — it must land in the same commit as the code that uses it or `make tidy-check` fails.
   Latest upstream is also `v0.57.0` (module proxy, 2026-09-08), so the pin is current.
8. **API signatures confirmed by `go doc`, not memory:**
   `argon2.IDKey(password, salt []byte, time, memory uint32, threads uint8, keyLen uint32) []byte`;
   `uuid.NewV7() (UUID, error)` exists in the pinned `v1.6.0`; `pgconn.PgError` carries `Code` and
   `ConstraintName`, so 23505 can be attributed to `users_one_owner` **without** promoting the
   indirect `jackc/pgerrcode` to a direct dependency.

---

## 8. Operations and docs

| Item | Change |
|---|---|
| `VIZRA_OWNER_CLAIM_ANNOUNCE` | new key, `stderr` \| `off`, default `stderr`, not secret |
| `VIZRA_OWNER_CLAIM_TTL` | new key, default `24h`, not secret |
| Both keys | require **three** coordinated edits or CI fails: `internal/config/keys.go` `Registry`, parsing in `LoadFrom`, and a `# <Doc>` + `NAME=value` block in `.env.example` in template order (`make config-template-check`) |
| `cmd/vizra` | new `claim-token` subcommand (§3.4) |
| `vizra doctor` | new check: instance unclaimed → print the exact command to obtain a token |
| `README` / `docs/quality/COMMANDS.md` | how an operator gets the token, and the aggregation-safe path |
| `NOTICE` | no change needed — `golang.org/x/crypto v0.57.0` is already listed |
| `vizra-user` | re-vendors the generated client after merge; consumes `getSetupClaimStatus` and `claimOwner`; **must not expect a session cookie** at M1-A |
| Ledger | `VZ-INSTALL-003` → IMPLEMENTED / UNVERIFIED with evidence paths; `surfaces.api` needs the new GET (OQ-3) — a meta-repo change this slice does not own |

---

## 9. Open questions for the chair

Only decisions that genuinely change the design. Each carries my recommendation.

**OQ-1 — PostgreSQL native enum for `user_role` / `credential_kind`, against the house `text + CHECK`
style used by `sites.privacy_mode`, `jobs.state` and `storage_locations.kind`.**
*Recommend: enum.* ADR-003 says "Roles are an ordered enum on `users.role`", and only a real enum
makes the rank order a schema fact. Decisively: adding a role later is `ALTER TYPE ... ADD VALUE`,
which is additive, whereas widening a CHECK requires dropping it — destructive under `migrate-lint`
in an append-only repo. Cost: `sqlc` emits a `sqlcgen.UserRole` type that must be mapped to
`authz.Role` at the boundary.

**OQ-2 — Default for `VIZRA_OWNER_CLAIM_ANNOUNCE`.**
*Recommend: `stderr` by default, plus the `vizra claim-token` CLI as the documented primary.*
`off` by default is more paranoid but breaks `PRODUCT_SPEC.md` §15 step 4 ("the claim token read from
the API log") and contradicts approved copy, at a milestone with no installer. If the security seat
wants `off`, that decision must also change those two documents — which this slice does not own.

**OQ-3 — `GET /api/v1/setup/claim-status` is not in `VZ-INSTALL-003`'s `surfaces.api`** (which lists
only the POST). The approved "already claimed" frames require it.
*Recommend: add the endpoint and update the ledger row in the meta repo* — a cross-repo change the
chair owns, not this builder.

**OQ-4 — Status code for a claim against an already-claimed instance** (the design's open Q-D2a-2).
*Recommend: 409 `conflict`*, reasoned in §3.3. This also requires adding `409 → conflict` to
`httpCodeName` in shared middleware.

**OQ-5 — Does the claim sign the owner in?**
*Recommend: no at M1-A;* M1-B adds `Set-Cookie` to the same operation, backward-compatibly. The
approved control matrix promises a session cookie, so `vizra-user` must redirect to `/login` until
M1-B lands. Someone must tell the `vizra-user` builder.

**OQ-6 — ADR-003's "Vizra version tag" on the argon2id hash is under-specified and self-conflicting.**
It requires the standard `$argon2id$v=19$…` encoding, a Vizra version tag, and "without a second
column" — but a standard PHC string has no slot for a vendor tag, and adding a prefix breaks
interoperability with standard verifiers.
*Recommend: store the plain standard PHC string and treat the embedded `m,t,p` as the version*, since
they are self-describing and make a future parameter raise detectable by parsing. **This is a
deviation from a literal reading of an Accepted, immutable ADR and is raised rather than taken.**

**OQ-7 — `audit_events_actor_user_fk` cannot be `ON DELETE SET NULL`** without violating the existing
frozen `audit_events_actor_identified` CHECK.
*Recommend: `ON DELETE RESTRICT`* (users are tombstoned, not hard-deleted). Related: no trusted-proxy
config exists, so `ip_prefix` is `NULL` behind a proxy at M1-A; recommend `VIZRA_TRUSTED_PROXIES`
lands with M1-B.

**OQ-8 — Per-field error envelope.** The approved design shows a multi-field error summary, but the
frozen `Error` schema carries only `code`/`message`/`request_id`.
*Recommend: single-message 400 at M1-A; design the envelope in M1-B* where sign-up is the real
multi-field case — so the contract is extended once, with its actual consumer present.

**OQ-9 — `vizra claim-token` adds a CLI surface** where `VZ-INSTALL-003`'s `surfaces.cli` is `[]`.
*Recommend: accept it* — it is the only log-aggregation-safe delivery path — and record it on the
ledger row.

**OQ-10 — Does ADR-003's "Setup wizard" CSRF row bind the owner-claim endpoint? (raise first.)**
ADR-003's request-class table contains:

> | Setup wizard | none (pre-claim) | loopback bind **and** one-time `X-Setup-Token` **and** Host allowlist | allow |

Read literally as covering `POST /api/v1/setup/claim-owner`, this slice would have to bind the claim
route to loopback, require an `X-Setup-Token` header *in addition to* the claim token, and enforce a
Host allowlist. That directly contradicts three other governing artifacts: `VZ-INSTALL-003`'s
`surfaces.ui` is `/setup/claim`, a browser page; the approved Figma frames draw it at the public
origin in the normal application shell at 1440 and 390; and ADR-007's own precedence rule names
"owner claim" as one of the three surfaces an anonymous visitor keeps **on a private site**, which
is meaningless for a loopback-only route.

*My reading, and my recommendation:* that row describes the **installer wizard** (`vizra setup` /
`install.sh`, VZ-ISSUE-004) — the Vidra mechanism it cites is `C/internal/setupweb/guard.go`, a
separate setup web server, not the claim API — and it does **not** bind
`POST /api/v1/setup/claim-owner`, whose single credential is the claim token itself. I recommend the
chair record that interpretation explicitly, because the alternative reading makes the approved
design unbuildable and the difference is a security boundary, not a detail.

**I am raising this rather than assuming it.** If the security seat reads the row as binding, this
slice's endpoint design changes materially and the approved claim screens must be redrawn — a
decision well above a builder.

---

## 10. Progress and evidence

**Phase 1 (2026-09-21).** Plan written. Worktree created at
`/Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim`, branch `feat/m1-owner-claim`,
HEAD `4a80a1e` — **no commits, no pushes, no product code, no migration file**. Design mechanics
validated against real PostgreSQL 17.11 and a real argon2 benchmark (§7). Status: **PLAN_READY**,
awaiting the `vizra-security` and `vizra-core` seats and the chair's rulings on §9.

**Phase 2** appends here: exact commands, exit codes, test counts, skips, source SHA, environment and
artifact paths; implemented and verified kept separate; every test change explained.

## 11. Blockers and handoff

No external blocker. Phase 2 cannot start until §9 is ruled on, because OQ-1, OQ-4 and OQ-6 change
schema or contract that freezes on merge. Phase 2's first act is to preflight `sqlc v1.31.1` and a
reachable PostgreSQL and cache — each absent one is BLOCKED for its lane, declared up front.
