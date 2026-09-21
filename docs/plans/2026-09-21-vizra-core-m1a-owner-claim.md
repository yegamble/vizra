# Execution plan: VZ-INSTALL-003 (M1-A) — secure one-time owner claim

**Revision 2 (2026-09-21), phase 2.** Revised against the chair's consolidated rulings
(`docs/evidence/warroom/2026-09-21-vizra-core-m1a-owner-claim-PLAN-RULINGS.md`) and the two seat
reviews (`…-PLAN-REVIEW-security.md`, findings **S-n**; `…-PLAN-REVIEW-backend.md`, findings **B-n**,
required items **B-Rn**). The rulings file wins wherever the seats disagreed. Revision 1 was the
phase-1 plan-only draft; §12 records what changed and why.

## Context

| | |
|---|---|
| Ledger ID | `VZ-INSTALL-003` — "Secure one-time owner claim" |
| Issue | `docs/issues/VZ-ISSUE-005.md` (M1: owner claim, sessions, roles) |
| Slice position | **first of three**. M1-B = `VZ-AUTH-001`; M1-C = `VZ-AUTH-004`. |
| Repo / branch | `vizra-core`, `feat/m1-owner-claim` |
| Worktree | `/Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim` |
| Base | `4a80a1e3f36b8001c2954d0568bea29268e739fe` (`origin/main`) |
| Binding inputs | the rulings file (above) and both seat reviews |

The main `vizra-core` checkout belongs to another builder (`feat/m0-healthcheck-runtime-image`,
adding a `healthcheck` subcommand, worker health, Dockerfile/workflow changes). Shared files —
`cmd/vizra/main.go`'s subcommand switch, `internal/httpapi/server.go`, `internal/doctor` — get
minimal additive edits here; whichever PR merges second rebases. This slice owns `migrations/0005*`
and the `api/openapi.yaml` delta.

### Preflight

| Dependency | Result |
|---|---|
| `go version` | `go1.26.2 darwin/arm64` — OK |
| `sqlc version` | **`v1.31.1` installed** — OK (matches CI's pin) |
| PostgreSQL | **18.6** in container `vizra-m1a-pg18` (`127.0.0.1:55438`) — matches the CI digest pin's major |
| Cache | Valkey **9.1.2** in container `vizra-m1a-valkey` (`127.0.0.1:63799`), `PONG` |
| `docker` / `gh` | 29.8.0 / 2.98.0 — OK |

**Harness question answered before code (rulings row 4):** `git grep -in truncate` over tracked files
returns **no `TRUNCATE` in any Go, SQL or shell source** — `freshDatabase` resets with
`DROP SCHEMA public CASCADE; CREATE SCHEMA public;` (`internal/integration/golden_test.go:91`). A
statement-level `BEFORE TRUNCATE` trigger on `audit_events` therefore breaks nothing, and the strict
form of the ruling is adopted.

---

## 1. Scope

**In scope.** An unclaimed instance obtains a one-time 256-bit owner-claim token —
minted on demand by `vizra claim-token`, or at boot only under an explicit opt-in — stores only its
SHA-256 digest, and exchanges it once via `POST /api/v1/setup/claim-owner` for **the** owner account,
with "at most one live owner" enforced by a PostgreSQL constraint. It also discharges the two
obligations migration `0003_audit_events` deferred to "the first M1 writer": the `ip_prefix` masking
function and the `audit_events` immutability trigger plus its `users` foreign key.

**Explicitly NOT in scope:** sessions, sign-in/out, session revocation, registration, CSRF
middleware (M1-B); the role matrix and `PATCH /admin/users/{id}/role` (M1-C); API keys, TOTP,
password reset, user erasure and audit retention (M2); the `/setup/claim` UI (a `vizra-user` slice);
wiring `sites.privacy_mode` → `authz.Options.SitePrivate`.

**Hand-offs M1-B and M1-C inherit.** These are contracts, not folklore (S-6b/c, S-10, B-R6):

1. `users` with `role`, `disabled_at`, `tombstoned_at` — M1-B re-reads all three per request.
2. `credentials` holds **at most one verifier secret per (user, kind)** — `password` now, `totp`
   later. `api_keys`, `oauth_identities` and step-up rows are **their own tables** (B-R6).
3. **Email folding is PostgreSQL's `lower()`, in SQL, on write and on every later lookup. Never
   Go-side.** `email_fold` is `GENERATED ALWAYS`, so divergence is unrepresentable.
4. **Passwords are hashed as raw UTF-8 bytes with no Unicode normalisation**, and bounded in bytes
   (≤ 1024 octets) as well as characters. M1-A writes the hash; M1-B verifies it; a silent
   divergence is an owner lockout.
5. `user_role` is an ordered native enum whose order M1-C's matrix test depends on.
6. `internal/credential` — the injectable hasher **and the one process-wide semaphore** bounding
   concurrent argon2 derivations. M1-B's sign-in must import this, not create a second bound.
7. `internal/audit` — the emitter, the action grammar, the total `ip_prefix` writer.
8. The structural unclaimed guard and its route classification sets.
9. A per-route `http.MaxBytesReader` helper.

---

## 2. Rulings applied

| Ruling / finding | Where this plan handles it |
|---|---|
| Row 1, **B-1** tombstone predicate | §3.1 DDL `users_one_owner … AND tombstoned_at IS NULL`; tests T-11a/T-11b; MUT-2 |
| Row 2, **S-3 / B-5 / OQ-11** boot mint | §4.1 mint table; T-04, T-05, T-25; MUT-14 |
| Row 3, **S-2** announce default `off` | §4.4; §9 config; T-08, T-09; MUT-5, MUT-5b |
| Row 4, **S-5 / B-2** strict audit trigger | §3.1 trigger (UPDATE, DELETE **and** TRUNCATE); header text; T-14, T-14b, T-15; MUT-9, MUT-9b |
| Row 5, **S-6a / B-R6** credentials CHECK | §3.1 `secret LIKE '$argon2id$%'`, 1–1024; T-17 pins parameters in Go |
| Row 6, **S-F9** 201 body | §5.2 `{username, role}` only |
| **S-1** total `ip_prefix` writer | §6.4; T-20, T-21; MUT-10, MUT-10b |
| **S-4 / B-R9** structural guard | §5.4; T-22, T-23, T-24; MUT-12 |
| **S-5 / B-6** 429 writes no audit row | §6.3; T-18; MUT-11b |
| **S-7** limit failures not attempts | §6.1; T-16, T-16b, T-16c; MUT-15 |
| **S-6b/c** fold + password rules in the header | §3.1 header; §1 hand-offs 3–4; T-19, T-26 |
| **B-R1 / B-R2** generated folds, partial email index | §3.1; §11 sqlc preflight; T-27, T-28 |
| **B-3 / S-11** no spec-accepted input yields 5xx | §5.3; T-12; MUT-8b |
| **B-4** explicit ReadCommitted | §5.5; T-02 under three server defaults; MUT-16 |
| **B-R4 / S-9** complete error map, index name pinned | §5.3 table; T-13, T-13b, T-29; MUT-17 |
| **B-R5** token normalise → shape → compare, 403 for all | §4.2; T-03d |
| **S-8** request posture | §5.1; T-06, T-07, T-07b, T-07c, T-07d; MUT-18 |
| **S-10** injectable hasher + shared semaphore | §5.6; T-10, T-10b; MUT-13 |
| **S-12** CLI refuses on a claimed instance | §4.3; T-05b, T-25 |
| **B-R3** `user_role` enum, `credential_kind` text+CHECK | §3.1 |
| **B-R7 / S-13** advisory-lock constant | §4.1; no `hashtext` |
| **S-14** enum ↔ authz drift test | T-30 |
| **B-2.1** drop `consumed_by` | §3.1 |
| **B-R8 / S-F8** PG 18 acceptance evidence | §10; the 17.11 transcript is labelled design validation |
| **B-R10** `/api/v1` group, probes unprefixed | §5.1 |
| **B-R11** explicit casts in the CTE | §5.5; §11 preflight |
| **B-R12** one explicit transaction | §5.5 |
| **S-15 + backend invariant table** | §8 — every row has a named test and a mutation, or sits beside MUT-4 as review-only |

---

## 3. Migration `0005`

Files `migrations/0005_users_credentials_owner_claim.{up,down}.sql`, then `make migrations-manifest`
and `make migrate-lint`. The up file is additive, so no `-- allow-destructive:` annotation is needed.

### 3.1 Up file

```sql
-- 0005: the owner account, its password credential, and the one-time claim token
-- that creates it (VZ-INSTALL-003, ADR-003 §Credentials, ADR-007 §Entities and keys).
--
-- Invariants that are DATABASE facts here, not application conventions:
--   1. users_one_owner        — at most one LIVE row with role 'owner'.
--   2. owner_claim_tokens PK  — at most one claim-token row, ever.
--   3. audit_events_append_only — UPDATE, DELETE and TRUNCATE are all refused.
--
-- No site_id or tenant_id column: isolation under tenancy is database-per-tenant
-- (ADR-007), so "one owner per site" IS "one owner per database".
--
-- FOLDING RULE (frozen here; M1-B inherits it). username_fold and email_fold are
-- GENERATED ALWAYS AS (lower(...)) STORED. Folding is PostgreSQL's lower(), in
-- SQL, on write AND on every later lookup. Never fold in Go: strings.ToLower and
-- PostgreSQL's lower() are not the same function for non-ASCII, and `email`
-- accepts UTF-8. A sign-in that folds Go-side can lock the owner out of the only
-- privileged account on the instance.
--
-- PASSWORD RULE (frozen here; M1-B inherits it). The password is hashed as the
-- RAW UTF-8 BYTES of the submitted field, with NO Unicode normalisation, and is
-- bounded in bytes (<= 1024 octets) as well as in characters. M1-A writes the
-- hash and M1-B verifies it; a silent divergence is the same lockout.
--
-- ERASURE AND RETENTION (0003 deferred the trigger and its retention path as a
-- pair; this migration lands the trigger only, by chair ruling). Deleting a user
-- row is IMPOSSIBLE while audit rows name it: audit_events_actor_user_fk is
-- ON DELETE RESTRICT, because the frozen audit_events_actor_identified CHECK
-- makes ON DELETE SET NULL illegal. Erasure is therefore scrub-and-tombstone of
-- `users`, never DELETE. Consequently audit `before`, `after` and `actor_label`
-- must NEVER carry an email address or any PII beyond the username, and every
-- later emitter inherits that rule. The audited retention/anonymisation path is
-- still owed and carries its own ledger ID; it can be added ADDITIVELY, because
-- migrate-lint's destructive pattern does not match CREATE OR REPLACE FUNCTION.

-- Rank order is load-bearing: it must equal authz.Role's ranking for the five
-- STORED roles ('anonymous' is deliberately absent — it is never a stored
-- principal). A future role is added with ALTER TYPE ... ADD VALUE in its own
-- migration carrying `-- no-down:` (an enum value cannot be removed).
CREATE TYPE user_role AS ENUM ('guest', 'member', 'manager', 'admin', 'owner');

CREATE TABLE users (
    id             uuid        PRIMARY KEY,              -- uuidv7, minted in Go
    username       text        NOT NULL,
    username_fold  text        GENERATED ALWAYS AS (lower(username)) STORED,
    email          text        NOT NULL,
    email_fold     text        GENERATED ALWAYS AS (lower(email)) STORED,
    role           user_role   NOT NULL DEFAULT 'member',
    disabled_at    timestamptz NULL,
    tombstoned_at  timestamptz NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    updated_at     timestamptz NOT NULL DEFAULT now(),

    -- 3..30 characters, letters/digits/hyphen/underscore, leading alphanumeric.
    -- The Go validator compiles THIS literal, cross-checked by a test that reads
    -- this file's bytes, so the two can never drift (B-3/S-11).
    CONSTRAINT users_username_shape CHECK (username ~ '^[A-Za-z0-9][A-Za-z0-9_-]{2,29}$'),
    -- Bounds are BYTES. JSON Schema maxLength counts characters, so the spec and
    -- this CHECK would otherwise disagree on any non-ASCII address (B-3).
    CONSTRAINT users_email_shape CHECK (
        email ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'
        AND octet_length(email) BETWEEN 3 AND 254)
);

CREATE UNIQUE INDEX users_username_fold_key ON users (username_fold);
-- Partial from day one: VZ-AUTH-006 declares an email-less social signup as a
-- future state, and `ALTER COLUMN email DROP NOT NULL` is additive while
-- `DROP INDEX` is annotated-destructive (B-R2).
CREATE UNIQUE INDEX users_email_fold_key ON users (email_fold) WHERE email_fold IS NOT NULL;

-- THE invariant of this slice. Every row with role 'owner' and no tombstone
-- carries the same key, so a second one raises 23505. This decides a concurrent
-- claim race — not an advisory lock, not SELECT ... FOR UPDATE, not a Go mutex.
-- The tombstone predicate is deliberate (B-1): without it, tombstoning the owner
-- would brick the instance forever — the key stays held, ADR-003 forbids
-- demotion, the claim gate is EXISTS(users) so no token can be minted, and the
-- row cannot be deleted because audit_events RESTRICTs it. Tombstoning does NOT
-- reopen the claim endpoint, because that gate is EXISTS(users), not this index.
CREATE UNIQUE INDEX users_one_owner ON users (role)
    WHERE role = 'owner' AND tombstoned_at IS NULL;

-- `credentials` holds at most ONE VERIFIER SECRET PER (user, kind) — 'password'
-- now, 'totp' later. api_keys (many per user, scoped, revocable), oauth_identities
-- ((provider, subject) unique) and step-up rows are their own tables per ADR-003
-- and ADR-007; do not widen this table into them.
-- text + CHECK rather than an enum: credential_kind has no ordering semantics,
-- and a text CHECK widens in one reversible annotated migration (B-R3).
CREATE TABLE credentials (
    id          uuid        PRIMARY KEY,
    user_id     uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    kind        text        NOT NULL,
    secret      text        NOT NULL,   -- a verifier, never a reversible value
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT credentials_kind CHECK (kind IN ('password')),
    -- The CHECK's job is "never plaintext, never another scheme". The exact
    -- parameters (v=19, m=19456,t=2,p=1, 16-byte salt, 32-byte tag) are pinned by
    -- a Go unit test, which can move when ADR-003's parameters are raised; a
    -- narrower CHECK would make a parameter raise a schema fight.
    CONSTRAINT credentials_password_is_argon2id CHECK (
        kind <> 'password' OR secret LIKE '$argon2id$%'),
    -- 1024 leaves room for an envelope-encrypted TOTP secret plus KEK metadata.
    CONSTRAINT credentials_secret_bounded CHECK (octet_length(secret) BETWEEN 1 AND 1024)
);

CREATE UNIQUE INDEX credentials_one_per_user_per_kind ON credentials (user_id, kind);

CREATE TABLE owner_claim_tokens (
    -- Boolean primary key pinned TRUE by the CHECK: at most one row, ever, so
    -- "the live claim token" is a schema fact and a re-mint is an upsert on a
    -- fixed key.
    id            boolean     PRIMARY KEY DEFAULT true,
    -- SHA-256 of the normalised raw token. The raw token is NEVER stored, never
    -- returned, and unrecoverable by design: a lost token is re-minted.
    token_sha256  bytea       NOT NULL,
    -- Increments on every mint. Audit rows and operator-facing output reference
    -- the GENERATION, so a claim is traceable with no secret material.
    generation    bigint      NOT NULL DEFAULT 1,
    minted_at     timestamptz NOT NULL DEFAULT now(),
    expires_at    timestamptz NOT NULL,
    consumed_at   timestamptz NULL,
    -- Set when a boot or the CLI retires a token without consuming it.
    superseded_at timestamptz NULL,

    CONSTRAINT owner_claim_tokens_singleton  CHECK (id),
    CONSTRAINT owner_claim_tokens_digest_len CHECK (octet_length(token_sha256) = 32),
    CONSTRAINT owner_claim_tokens_ttl        CHECK (expires_at > minted_at),
    CONSTRAINT owner_claim_tokens_generation CHECK (generation >= 1),
    CONSTRAINT owner_claim_tokens_one_terminal_state CHECK (
        consumed_at IS NULL OR superseded_at IS NULL)
);

-- ---------------------------------------------------------------------------
-- The two obligations 0003_audit_events deferred to "the first M1 writer".
-- ---------------------------------------------------------------------------

ALTER TABLE audit_events
    ADD CONSTRAINT audit_events_actor_user_fk
    FOREIGN KEY (actor_user_id) REFERENCES users (id) ON DELETE RESTRICT;

CREATE FUNCTION audit_events_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'audit_events is append-only (attempted % )', TG_OP
        USING ERRCODE = '42501';
END;
$$;

CREATE TRIGGER audit_events_no_update_or_delete
    BEFORE UPDATE OR DELETE ON audit_events
    FOR EACH ROW EXECUTE FUNCTION audit_events_append_only();

-- Statement-level, because a row trigger does not fire on TRUNCATE and would let
-- one statement destroy the whole trail. Verified safe: no TRUNCATE exists in any
-- Go, SQL or shell source in this repository; the integration harness resets with
-- DROP SCHEMA public CASCADE.
CREATE TRIGGER audit_events_no_truncate
    BEFORE TRUNCATE ON audit_events
    FOR EACH STATEMENT EXECUTE FUNCTION audit_events_append_only();
```

### 3.2 Down file

```sql
DROP TRIGGER IF EXISTS audit_events_no_truncate ON audit_events;
DROP TRIGGER IF EXISTS audit_events_no_update_or_delete ON audit_events;
DROP FUNCTION IF EXISTS audit_events_append_only();
ALTER TABLE audit_events DROP CONSTRAINT IF EXISTS audit_events_actor_user_fk;
DROP TABLE IF EXISTS owner_claim_tokens;
DROP TABLE IF EXISTS credentials;
DROP TABLE IF EXISTS users;
DROP TYPE IF EXISTS user_role;
```

---

## 4. Token lifecycle

### 4.1 Minting

Under `pg_advisory_xact_lock(advisoryLockOwnerClaimMint)` where that is a **registered constant**,
not `hashtext` (B-R7/S-13):

```go
// Advisory lock id registry. Every advisory lock the product takes is listed
// here so a future user of the mechanism can see what is taken.
//   1 — owner-claim mint (M1-A, VZ-INSTALL-003)
const advisoryLockOwnerClaimMint int64 = 1
```

**Boot (`cmd/api`).** Never fatal; a failure is a redacted log + degraded readiness + a `doctor` FAIL
(S-12, B-5a/b).

| Observed state | Action |
|---|---|
| any user exists | **supersede** any live token; mint nothing; announce nothing. An implicitly claimed instance must never hold a live owner-creating credential. |
| unclaimed, `ANNOUNCE=off` (default) | mint **nothing**. Print the command line only (§4.4). |
| unclaimed, `ANNOUNCE=stderr`, a live token exists | mint nothing; print the command line and the current generation. **A restart does not invalidate a token the operator is holding** (S-3). |
| unclaimed, `ANNOUNCE=stderr`, no live token | mint, announce the token and its generation once on stderr. |

**`vizra claim-token`.** **Always** supersedes any live token and mints a fresh one, printing it to
stdout with its generation. **Refuses, non-zero, when any user exists** (S-12) — minting an
owner-creating credential on a running claimed instance would be a standing escalation path.

This is the ruled departure from the ledger's "Restart re-mints; old token invalid" — see §13.

**Entropy and encoding.** 32 bytes from `crypto/rand`, **64 lowercase hex characters** (256 bits).
Hex matches the approved copy and survives a terminal copy without `-`/`_`/`=` losses.

**Hash at rest.** `sha256.Sum256` of the normalised token, stored `bytea(32)`. Not argon2: 256 bits
of uniform randomness has nothing to grind, and a slow KDF on an unauthenticated endpoint is a CPU
amplifier handed to the attacker (both seats concur).

**TTL.** `VIZRA_OWNER_CLAIM_TTL`, default **1h**, evaluated in SQL against PostgreSQL's clock. The
security seat asked for a shorter default without naming one. One hour is justified by the new
lifecycle: the token is now minted *on demand* by an operator who is about to use it, so the window
only has to cover reading the claim page, choosing a password and one retry — not an unattended
instance waiting to be discovered. Re-minting is one command, so a short TTL costs nothing, while a
long one keeps a live credential in terminal scrollback.

### 4.2 Verification order (B-R5)

`trim` → `lowercase` → **shape** → `sha256` → fetch the single row → `subtle.ConstantTimeCompare`.
A token that fails the shape check gets the **same 403 and the same message** as a wrong one —
otherwise "one message, because four causes are indistinguishable" is contradicted by a 400 that
says "your token is the wrong length". The redeem statement is passed **the row's own digest**, never
the presented value, so attacker-controlled bytes never reach SQL.

**Five indistinguishable causes of the single 403** (S-12c): mistyped, already consumed, superseded,
expired, **and no token row ever minted**.

### 4.3 `vizra claim-token`

Takes the advisory lock; refuses non-zero if any user exists; supersedes + mints; prints to
**stdout** — which for `docker compose exec` is the operator's terminal and is *not* part of the api
container's captured log stream. That property is the whole point (§4.4).

### 4.4 How the operator obtains the token

`AGENTS.md` forbids logging credentials and mechanises it; `VZ-INSTALL-003`'s privacy case says
"Token never appears in HTTP responses or **non-local** logs". Docker's json-file driver — and
journald, fluentd, gelf, awslogs, splunk — capture stdout **and** stderr of PID 1. An unstructured
line is not field-extracted but is still stored, shipped, retained and searchable, and
`docker compose logs` is the single most-pasted artefact in issue trackers.

**Ruled (row 3): default `off`.** The boot line prints a **command, not a credential**:

```
vizra: this instance is unclaimed. Get a claim token:
         docker compose exec api vizra claim-token
```

`VIZRA_OWNER_CLAIM_ANNOUNCE=stderr` is an explicit opt-in for a single VPS with no aggregation, and
its `.env.example` Doc text says in terms that it writes a credential to the container log. The
structured logger (`obs.NewLogger` → slog) is **never** used for either line: `obs`'s `secretKeys`
includes `token`, so an honest key name yields `[redacted]`, and any key name that survives redaction
ships a JSON field a log shipper will index. The announcement writer is a plain `io.Writer`
defaulting to `os.Stderr`.

`vizra doctor` prints the same command and the current generation (never a secret).

### 4.5 After a successful claim

Minting stops permanently. `POST …/claim-owner` answers **409 `conflict`**; `GET …/claim-status`
answers `{"claimed": true}`. 409 rather than 404 because the status endpoint must keep answering for
the approved "already claimed" screen, so concealing only the POST leaks the identical bit next
door; and rather than 403 because 403 is already taken for the opposite condition. The claimed check
strictly precedes any token examination (OQ-4).

### 4.6 The claim does not sign the owner in

No session exists until M1-B and faking one would be mock data in a production path. `vizra-user`
redirects to `/login`. M1-B adds `Set-Cookie` to the same operation, a non-breaking addition.

---

## 5. Endpoints, contract and handler

### 5.1 Routing and request posture (B-R10, S-8)

`/api/v1` is registered as an Echo **group** in `New()`; the four probes deliberately stay
unprefixed, because they are infrastructure surfaces, not API surfaces, and their paths are already
frozen in `api/openapi.yaml`.

Request posture for `POST /api/v1/setup/claim-owner`, enforced in this order:

1. **Media type** must be `application/json`, else **415**. Parameters (`; charset=utf-8`) are
   permitted — they do not change the parse. Anything else, including urlencoded and multipart,
   is refused. *(The ruling says "exactly `application/json`"; permitting a charset parameter is my
   reading of that, stated here so a seat can object.)*
2. **`http.MaxBytesReader(w, req.Body, 8 KiB)`** — on the body, not a `Content-Length` check, which a
   chunked request bypasses. Over the limit → **413**.
3. **`json.Decoder` with `DisallowUnknownFields`**, never `c.Bind` — Echo's binder accepts
   urlencoded and multipart and silently skips fields lacking a `form` tag. Unknown field → **400**.
   Empty body → **400**, before any database read.
4. **Origin posture.** If `Origin` is present it must equal `VIZRA_PUBLIC_ORIGIN`; if
   `Sec-Fetch-Site` is present it must be `same-origin` or `none`. **Absence of both is allowed**, so
   curl and the CLI keep working — the credential is in the body, not ambient. A mismatch returns
   **403 with the distinct code `origin_mismatch`**, so a misconfigured public origin is diagnosable
   rather than looking like a bad token.

`vizra doctor` compares the configured public origin against reality where it can.

### 5.2 OpenAPI delta

`TestM0ContractIsTheFourProbes` fails the moment a fifth operation exists and is **amended in this
diff** to enumerate the four probes plus the two setup operations. No assertion is weakened — it
still enumerates the complete expected set.

`GET /api/v1/setup/claim-status` → `getSetupClaimStatus`, `security: []`:

```yaml
SetupClaimStatus:
  type: object
  additionalProperties: false
  required: [claimed]
  properties: { claimed: { type: boolean } }
```

**The privacy case:** an unauthenticated caller learns **exactly one bit**. Never `minted_at`,
`expires_at`, `generation`, a "token is live" flag, a user count, or the owner's identity.

`POST /api/v1/setup/claim-owner` → `claimOwner`, `security: []`:

```yaml
ClaimOwnerRequest:
  type: object
  additionalProperties: false
  required: [token, username, email, password]
  properties:
    token:    { type: string, pattern: '^[0-9a-fA-F]{64}$' }
    username: { type: string, minLength: 3, maxLength: 30, pattern: '^[A-Za-z0-9][A-Za-z0-9_-]{2,29}$' }
    email:    { type: string, maxLength: 254, pattern: '^[^\s@]+@[^\s@]+\.[^\s@]+$',
                description: 'At most 254 BYTES; the server bound is octet_length.' }
    password: { type: string, minLength: 12, maxLength: 256,
                description: 'At most 1024 BYTES; hashed as raw UTF-8 with no normalisation.' }

ClaimOwnerResponse:      # {username, role} only — ruling row 6
  type: object
  additionalProperties: false
  required: [username, role]
  properties:
    username: { type: string }
    role:     { type: string, enum: [owner] }
```

The internal uuid is **not** returned: ADR-007 separates internal from public identifiers and gives
`users` no public key, so the username is the public handle. A field can be added later; a required
field cannot be removed.

### 5.3 Complete error map (B-R4)

Unit-tested as a table over synthetic `*pgconn.PgError{Code, ConstraintName}` values.

| Condition | Status | `error.code` |
|---|---|---|
| Success | 201 | — |
| Media type not `application/json` | 415 | `unsupported_media_type` |
| Body over 8 KiB (incl. chunked) | 413 | `payload_too_large` |
| Unknown field, empty body, malformed JSON | 400 | `bad_request` |
| Username/email/password outside its bound | 400 | `bad_request` (message names the first offending field in prose) |
| `Origin` / `Sec-Fetch-Site` mismatch | 403 | `origin_mismatch` |
| Token: mistyped, malformed, consumed, superseded, expired, never minted | 403 | `forbidden` (one message) |
| Instance already claimed | 409 | `conflict` |
| `pgx.ErrNoRows` from ClaimOwner | re-read claimed state → 409 if an owner exists, else 403 | |
| 23505 `users_one_owner` | 409 | `conflict` |
| 23505 `users_username_fold_key` / `users_email_fold_key` | 409 | `conflict` |
| 23514 (any CHECK) — backstop, never 500 | 400 | `bad_request` |
| 23503 `audit_events_actor_user_fk` | 500 | `internal_error` — a real defect; logged |
| 40001 | unreachable once §5.5 pins ReadCommitted; asserted | |
| Failure budget exhausted, invalid token | 429 | `rate_limited` |
| Hard ceiling exceeded | 429 | `rate_limited` |
| Database unreachable, `context.DeadlineExceeded` | 503 | `unavailable` |

`httpCodeName` gains `409 → conflict` and `415 → unsupported_media_type`. `422` is **not** added —
no operation needs it. `origin_mismatch` is carried by a typed error the error handler recognises,
since the existing handler derives the code from the status alone.

**No input the OpenAPI schema accepts may produce a 5xx** (B-3/S-11). Go validates with the *same
literals* the DDL enforces; a test reads the migration's bytes and asserts the regexes are identical,
the idiom the repo already uses for the search contract.

### 5.4 The unclaimed guard is structural (S-4 / B-R9)

**One server-wide middleware.** While the instance is unclaimed, only an explicit allowlist is
reachable; everything else is 403, **including the router's 404 path**. At M1-A nothing can legitimately
exist before an owner does, so this cannot be wrong; narrowing it later is a one-line allowlist edit
with a test that notices.

- Allowlist: `/healthz`, `/readyz`, `/version`, `/schemaz`, `GET /api/v1/setup/claim-status`,
  `POST /api/v1/setup/claim-owner`. Sign-in joins in M1-B.
- The claimed bit is **monotonic** (`users_one_owner` plus the `EXISTS(users)` gate make false→true
  one-way), so it is cached in-process **permanently once true**; while false it is cached for a
  bounded moment so a flood costs no database work.
- A lookup **error** is **503** — never 403, never allow.

**Route-walk test.** Two hand-maintained sets, `claimExempt` and `claimGuarded`; the test walks
`Server.Routes()` and fails on any route in neither. At M1-A `claimGuarded` is empty; in M1-B
`POST /api/v1/auth/register` fails the test until its author classifies it consciously. The mutation
is "add a route without touching either set".

### 5.5 The claim transaction (B-4, B-R11, B-R12)

**One explicit transaction:** `pool.BeginTx(ctx, pgx.TxOptions{IsoLevel: pgx.ReadCommitted})` →
`ClaimOwner` → `InsertAuditEvent` → `Commit`. **No retry** — under READ COMMITTED the loser's answer
is deterministic (zero rows), so there is nothing to retry, and a retry would mask a serialization
failure that should not occur.

Pinning the isolation level explicitly is not ceremony: `default_transaction_isolation` is a server
GUC that an operator, a managed provider or a pooler can set, and under REPEATABLE READ every losing
claimant gets `40001` instead of zero rows — which the handler would map to 500, making test T-02's
"zero 5xx" a false pass that only fails in production.

```sql
-- name: ClaimOwner :one
WITH consumed AS (
    UPDATE owner_claim_tokens
       SET consumed_at = now()
     WHERE id
       AND token_sha256  = sqlc.arg('token_sha256')::bytea
       AND consumed_at   IS NULL
       AND superseded_at IS NULL
       AND expires_at    > now()            -- PostgreSQL's clock (ADR-004)
    RETURNING generation
),
owner AS (
    INSERT INTO users (id, username, email, role)
    SELECT sqlc.arg('user_id')::uuid, sqlc.arg('username')::text,
           sqlc.arg('email')::text, 'owner'
      FROM consumed
    RETURNING id, username, role
),
cred AS (
    INSERT INTO credentials (id, user_id, kind, secret)
    SELECT sqlc.arg('credential_id')::uuid, owner.id, 'password',
           sqlc.arg('password_hash')::text
      FROM owner
    RETURNING id
)
SELECT owner.id, owner.username, owner.role,
       (SELECT generation FROM consumed) AS token_generation
  FROM owner, cred;
```

The guarded `UPDATE` must be the CTE the `INSERT` selects from: a data-modifying CTE always executes,
so if the insert came first and the guarded update matched nothing, the owner row would still be
written. `owner` selecting `FROM consumed` forces the redeem to produce a row before any user exists.
Crash between the two is impossible — one statement inside one explicit transaction.

### 5.6 The hasher is an injectable dependency (S-10)

`internal/credential` exports the hasher interface, the argon2id implementation with ADR-003's pinned
parameters, and **the one process-wide semaphore** bounding concurrent derivations
(`min(GOMAXPROCS, 4)`, so peak transient memory ≤ 76 MiB). Waiters honour `c.Request().Context()` and
fail **503**, never queuing unbounded. M1-B's sign-in imports this rather than creating a second
unbounded bound.

The hasher carries a **call counter**, so "argon2 runs only after the token compares" stops being
prose and becomes an assertion: tests assert **zero derivations** on the 415, 413, 400, 403, 409 and
429 paths. This is the same seam `PingDatabase`/`PingCache` already use.

---

## 6. Abuse and failure

### 6.1 Rate limiting: failures, not attempts (S-7)

The old design let any stranger lock the operator out: 60 junk requests exhausted a shared bucket and
the operator's **correct** token was then answered 429 for fifteen minutes, at two requests per minute
of attacker cost.

- **Failure budget** — consumed **only by a rejected attempt**. Per-origin (masked prefix)
  10 / 15 min; global 60 / 15 min. **A request presenting the valid token is never answered 429 by
  this limiter**, whatever the budget says.
- **Hard ceiling** — 600 / 15 min across *all* requests to the two setup routes, protecting the pool
  from a flood of one-row SELECTs. A flood past this is a network-level DoS and is out of scope for
  an application limiter; that is stated rather than implied. The ceiling *can* 429 a valid token;
  the failure limiter cannot.
- **Attribution.** When a forwarded header is **present** and no trusted-proxy configuration exists,
  `ip_prefix` is NULL and the per-origin bucket **is not used** — the proxy's private prefix is never
  written as if it were the client. `VIZRA_TRUSTED_PROXIES` is M1-B.
- **Cache outage.** ADR-003 governs: `FallbackLimiter` flips to the per-process `MemoryLimiter` and
  readiness is marked degraded. Fail-open is right here because the blast radius is bounded by a
  different mechanism entirely — the endpoint can succeed exactly once in the lifetime of the
  instance, enforced by `users_one_owner`. Failing closed would turn a cache outage into "the
  operator cannot claim their new instance".

### 6.2 Other cases

| Case | Behaviour |
|---|---|
| Replay | First wins; later attempts find `consumed_at IS NOT NULL` → no row → 403. |
| Reuse after success | Instance is claimed → **409** before the token is examined. |
| Concurrent claims | Exactly one 201, N−1 declared errors, one live owner. Loser: no row → re-read claimed state → 409 if an owner exists, else 403. |
| Out-of-band owner + live token | 23505 `users_one_owner` → **409**, no 5xx, no orphan credential, token unconsumed (S-9). |
| Crash mid-claim | Impossible — one statement, one transaction. |
| Clock | PostgreSQL's `now()` for every timestamp and for the expiry predicate (ADR-004). |
| Database down | 503, never 403 (ADR-003). Repository errors are returned, never swallowed into "invalid token". |

### 6.3 Audit events

Grammar `<domain>.<object>.<verb-past>`, lowercase snake_case.

| `action` | `actor_kind` | `subject_type` | `subject_id` | `after` |
|---|---|---|---|---|
| `setup.owner_claim.minted` | `system` | `owner_claim_token` | generation | `{"expires_at": …}` |
| `setup.owner_claim.superseded` | `system` | `owner_claim_token` | generation | `null` |
| `setup.owner_claim.refused` | `anonymous` | `owner_claim_token` | `null` | `{"reason":"token_not_accepted"\|"already_claimed"}` |
| `setup.owner_claim.rate_limited` | `anonymous` | `owner_claim_token` | `null` | `{"bucket":…}` |
| `setup.owner_claim.succeeded` | `user` | `user` | owner uuid | `{"username":…,"role":"owner"}` |

**A 429 writes no audit row** (S-5/B-6). An unauthenticated endpoint must not be an unbounded append
path into a table nothing can delete: the 429 is the mechanism meant to *stop* the flood, so having
it write the row means rate limiting causes the write instead of bounding it. Exactly one
`rate_limited` row is written **on the transition into the limited state**, per bucket per window;
rejections themselves are a metric. `minted`, `superseded` and `succeeded` are bounded by boots and
by "exactly once".

**Never recorded:** the token, its digest, the password, the password hash, or the **email**.
`username` is a public identifier and is fine. Because erasure is scrub-and-tombstone (§3.1 header),
this PII rule binds every later emitter.

### 6.4 The `ip_prefix` writer is total (S-1)

`0003`'s frozen CHECK accepts IPv6 only as `^[0-9a-f]{1,4}(:[0-9a-f]{1,4}){0,3}::(/(48|64))?$` — at
least one hex group before `::`. The natural writer produces exactly `::/64` for `::1` and for `::`,
and `netip.Prefix.String()` returns the literal `"invalid Prefix"` for a zero Prefix. Each of those
violates the CHECK, and because the audit INSERT shares the claim's transaction, a 23514 there
**aborts the claim**: the owner is not created, the token is not consumed, the client gets a 500, and
the operator retries from the same address forever. A claim over IPv6 loopback would make the
instance permanently unclaimable.

So the writer is **total by construction**:

1. `netip.ParseAddr` → `Unmap()` first.
2. NULL for unparseable, zoned, unspecified, loopback and zero addresses.
3. Mask /24 (IPv4) or /64 (IPv6); format lowercase.
4. **Validate the produced string against the frozen grammar** — the regex compiled from
   `0003_audit_events.up.sql`'s own bytes in the test — and return NULL on any mismatch.
5. Belt as well as braces: the same validation runs in Go immediately before the INSERT.

**No SAVEPOINT around the audit insert** — that would trade an unclaimable instance for an unaudited
claim, which is worse at exactly the moment the trail matters.

---

## 7. Test plan

Integration on **real PostgreSQL 18 and real Valkey** via the existing harness (`//go:build
integration`, `VIZRA_TEST_DATABASE_URL`, `VIZRA_TEST_CACHE_URL`, `freshDatabase`, `mustEnv` which
**fatals rather than skips**). New files `internal/integration/owner_claim_test.go` and unit tests
beside their packages.

| ID | Test | Level |
|---|---|---|
| T-01 | `TestOwnerClaimCreatesExactlyOneOwnerAndConsumesTheToken` | int |
| T-02 | `TestOwnerClaimRaceYieldsExactlyOneOwnerUnderEveryServerDefaultIsolation` — 32 goroutines × {read committed, repeatable read, serializable} | int |
| T-03 | `TestOwnerClaimRejectsAReusedToken` | int |
| T-03d | `TestAMalformedTokenIsRefusedLikeAWrongToken` (same status, same body) | int |
| T-04 | `TestARestartDoesNotInvalidateALiveToken` | int |
| T-05 | `TestClaimTokenCLIRemintsAndSupersedesThePrevious` | int |
| T-05b | `TestClaimTokenCLIRefusesOnAClaimedInstance` | int |
| T-06 | `TestClaimRefusesANonJSONContentType` (urlencoded + multipart → 415, no owner) | int |
| T-07 | `TestClaimRefusesAnUnknownField` | int |
| T-07b | `TestClaimRefusesACrossOriginRequest` (403 `origin_mismatch`) | int |
| T-07c | `TestClaimAcceptsAHeaderlessCLIRequest` | int |
| T-07d | `TestClaimBodyLimitAppliesToAChunkedRequest` | int |
| T-08 | `TestOwnerClaimTokenNeverReachesTheStructuredLog` (plain handler + buffer) | int |
| T-09 | `TestBootAnnouncementPrintsACommandNotACredential` + registry default is `off` | unit |
| T-10 | `TestNoPasswordHashingOccursWithoutAValidToken` (counter-backed, every non-201 path) | int |
| T-10b | `TestConcurrentHashingIsBounded` | unit |
| T-11a | `TestASecondLiveOwnerIsRefusedByTheDatabase` | int |
| T-11b | `TestATombstonedOwnerDoesNotPermanentlyBlockOwnership` | int |
| T-12 | `TestMalformedFieldsYield400AndDoNotConsumeTheToken` (short username, leading hyphen, 31 chars, dotless email, 255-byte email, 11-char password, 1 KiB astral password) | int |
| T-13 | `TestOwnerInsertConflictMapsTo409NotFiveHundred` (owner inserted out of band, then a valid token) | int |
| T-13b | `TestClaimErrorMapping` — unit table over synthetic `*pgconn.PgError` | unit |
| T-14 | `TestAuditEventsCannotBeUpdatedOrDeleted` | int |
| T-14b | `TestAuditEventsCannotBeTruncated` | int |
| T-15 | `TestAUserWithAuditRowsCannotBeDeleted` (23503) | int |
| T-16 | `TestRateLimitCountsFailuresNotSuccesses` | int |
| T-16b | `TestAValidTokenIsNeverRateLimitedByTheFailureLimiter` (exhaust, then claim → 201) | int |
| T-16c | `TestForwardedHeaderWithoutTrustedProxyYieldsNullIPPrefix` | int |
| T-17 | `TestStoredPasswordFormatIsTheFrozenArgon2idParameters` | unit |
| T-18 | `TestARateLimitedClaimWritesNoAuditRow` (≤ 1 row past the transition) | int |
| T-19 | `TestEmailFoldIsProducedByPostgresOnEveryPath` (non-ASCII address) | int |
| T-20 | `TestIPPrefixWriterOutputAlwaysSatisfiesTheFrozenCheck` (table; regex from 0003's bytes) | unit |
| T-21 | `TestOwnerClaimSucceedsFromIPv6Loopback` | int |
| T-22 | `TestEveryRouteIsEitherUnclaimedAllowlistedOrGuarded` | unit |
| T-23 | `TestUnclaimedInstanceRefusesANonAllowlistedRoute` (incl. the 404 path) | int |
| T-24 | `TestClaimGuardReturns503WhenTheDatabaseIsDown` — mechanism: `pools.Close()` before the request | int |
| T-25 | `TestBootMintFailureIsDegradedNotFatal` (api booted at schema 4) | int |
| T-26 | `TestPasswordIsHashedWithoutNormalisation` (byte identity) | unit |
| T-27 | `TestCaseVariantUsernameAndEmailAreRejectedAsDuplicates` | int |
| T-28 | `TestASecondPasswordCredentialForOneUserIsRefused` | int |
| T-29 | `TestOwnerIndexNameMatchesTheMapper` — reads `pg_indexes` | int |
| T-30 | `TestUserRoleEnumOrderMatchesAuthzRanking` — reads `enum_range` | int |
| T-31 | `TestClaimStatusRevealsOnlyTheClaimedBit` (exactly one key) | int |
| T-32 | `TestOwnerClaimTokenNeverAppearsInAnyResponseBodyOrHeader` | int |
| T-33 | `TestOwnerClaimAuditEventsCarryNoSecretMaterial` (token, digest, password, hash, email) | int |
| T-34 | `TestClaimTokenIsStoredOnlyAsASHA256Digest` | int |
| T-35 | `TestMintTimestampsComeFromTheDatabaseClock` — mirrors `TestRunAfterComesFromTheDatabaseClockNotTheApplicationHost` | int |
| T-36 | `TestTokenSingletonAndTerminalStateChecks` (second row; both terminal columns set) | int |
| T-37 | `TestAClaimSucceedsWhileTheCacheIsStopped` (limiter fail-open, §6.1) | int |
| T-38 | `TestOwnerClaimAnswers503WhenTheDatabaseIsDown` — mechanism: `pools.Close()` | int |

---

## 8. Mutation matrix

Every invariant in the backend seat's table and in security FINDING 15 has a named test and a
mutation that turns it red, **or** is recorded here as review-only. A mutation that does not change
the tree is a **harness failure**, not a pass.

| ID | Controlled mutation | Must turn RED |
|---|---|---|
| MUT-1 | Drop `AND consumed_at IS NULL` from the redeem CTE | T-02 |
| MUT-2 | Remove `AND tombstoned_at IS NULL` from `users_one_owner` | T-11b |
| MUT-2b | `DROP INDEX users_one_owner` | T-11a |
| MUT-3 | Store/compare the raw token instead of its SHA-256 | T-34 |
| MUT-5 | Announce through `deps.Logger` instead of the dedicated writer | T-08 |
| MUT-5b | Flip the `VIZRA_OWNER_CLAIM_ANNOUNCE` registry default to `stderr` | T-09 |
| MUT-6 | Remove `expires_at > now()` | T-03 (expired leg) |
| MUT-7 | Add `minted_at` to the claim-status response | T-31 |
| MUT-8 | Remove `MaxBytesReader` | T-07d |
| MUT-8b | Revert the Go email bound to a rune count | T-12 |
| MUT-9 | Drop the UPDATE/DELETE trigger | T-14 |
| MUT-9b | Drop the TRUNCATE trigger | T-14b |
| MUT-10 | Mask IPv4 to /32 | T-20 + existing `TestAuditEventsRefusesAFullIPAddress` |
| MUT-10b | Remove the output-grammar validation from the writer | T-20 (`::1` leg) |
| MUT-11 | Include `email` in the audit `after` blob | T-33 |
| MUT-11b | Emit an audit row on every refusal including 429 | T-18 |
| MUT-12 | Add a route without touching `claimExempt`/`claimGuarded` | T-22 |
| MUT-13 | Hash the password before comparing the token | T-10 |
| MUT-14 | Re-mint unconditionally at boot | T-04 |
| MUT-15 | Consume failure budget on success too | T-16b |
| MUT-16 | Drop the explicit `TxOptions` | T-02 (repeatable-read leg) |
| MUT-17 | Delete the `users_one_owner` case from the error mapper | T-13, T-13b |
| MUT-18 | Use `c.Bind` instead of the strict decoder | T-06, T-07 |
| MUT-19 | Change the audit FK to `NO ACTION` | T-15 |
| MUT-20 | Stamp `minted_at` from Go | T-35 |
| MUT-21 | Drop `credentials_one_per_user_per_kind` | T-28 |
| MUT-22 | Drop `users_email_fold_key` | T-27 |
| MUT-23 | Make the limiter fail closed | T-37 |
| MUT-24 | Drop `owner_claim_tokens_one_terminal_state` | T-36 |

**Review-only (no test can observe these; stated rather than implied):**

- **MUT-4** — replacing `subtle.ConstantTimeCompare` with `bytes.Equal`. Behaviourally identical; a
  timing difference is not observable from a Go test.
- **MUT-4b** (security FINDING 15 item 17) — passing the *presented* digest rather than the row's own
  digest to the redeem statement. Identical results; the property is defence against a future
  index-probing change and is a code-review obligation.

---

## 9. Operations and docs

| Item | Change |
|---|---|
| `VIZRA_OWNER_CLAIM_ANNOUNCE` | new key, `off` (default) \| `stderr`; Doc text says `stderr` writes a credential to the container log |
| `VIZRA_OWNER_CLAIM_TTL` | new key, default `1h` |
| Both | three coordinated edits or CI fails: `keys.go` `Registry`, parsing in `LoadFrom`, a `# <Doc>` + `NAME=value` block in `.env.example` |
| `cmd/vizra` | new `claim-token` subcommand (additive to the switch the other builder also touches) |
| `vizra doctor` | unclaimed check: names the current generation and the exact command; boot-mint failure is a FAIL |
| `README` / `docs/quality/COMMANDS.md` | how an operator gets the token; the aggregation-safe path |
| `AGENTS.md` | assurance rows only at the strength of their controls |
| `NOTICE` | unchanged — `golang.org/x/crypto v0.57.0` already listed; added to `go.mod` via `go get` at that version |
| `vizra-user` | re-vendors the client; **no session cookie at M1-A**; must tolerate 403 on every non-allowlisted route while unclaimed |

---

## 10. Evidence

Acceptance evidence is taken on **PostgreSQL 18.6** (CI pins 18 by digest). The revision-1 transcript
on 17.11 is retained as **design validation only** and is labelled so — never "measured" without its
version. Transcripts and the mutation harness live in `docs/evidence/m1a-owner-claim/`;
`demonstrate.sh` refuses a dirty tree, records the target file's sha256 **before and after** and
aborts if they are equal, asserts RED, reverts, asserts GREEN.

Nothing credential-shaped is committed: demo markers are assembled at runtime, never written as
literals in a transcript or script.

---

## 11. Preflight gates before handler code

1. `sqlc generate` on the real `ClaimOwner` query: **generated columns must not appear in the INSERT
   column list**, and the casted parameters must type as `[]byte`/`uuid.UUID`/`string`, not
   `interface{}`. If sqlc emits generated columns, **stop and report** — do not hand-edit generated
   code.
2. `sqlc diff` clean afterwards.
3. Migration applies and rolls back on PG 18.6.

---

## 12. What changed from revision 1

Tombstone predicate added to `users_one_owner`; boot minting made conditional and the announce
default inverted to `off` with a command-not-credential line; the audit trigger made strict and
extended to TRUNCATE; the `credentials` CHECK loosened to `$argon2id$%` with the parameters pinned in
Go; `consumed_by` dropped; fold columns made `GENERATED ALWAYS` with a partial email index;
`credential_kind` demoted from enum to text+CHECK; the 201 body reduced to `{username, role}`; the
`ip_prefix` writer made total; `requireClaimed` made structural with a route-walk test; rate limiting
re-keyed to failures with a separate hard ceiling; 429 stripped of its audit row; isolation level
pinned; the error map completed; the request posture made explicit; the hasher made injectable with a
call counter and a shared semaphore; the advisory-lock key made a constant; TTL shortened to 1h;
evidence moved to PG 18. Test count 19 → 38; mutations 12 → 24 plus two review-only.

Corrected from revision 1: widening a CHECK constraint is **annotated** by `migrate-lint`
(`-- allow-destructive:`), not refused — revision 1 said refused, and that error was part of the
argument for an enum. The enum is kept for `user_role` on the ADR-003 "ordered enum" ground.

---

## 13. Deviations from the ledger, stated

These are recorded in the PR body, not silently absorbed.

1. **Recovery case.** `VZ-INSTALL-003` says *"Restart re-mints; old token invalid."* Under the
   chair's ruling (row 2) a restart **does not** re-mint when a live token exists, and with the
   default `announce=off` a boot does not mint at all. The recovery *purpose* — a lost token is
   recoverable — is met by `vizra claim-token`, which always supersedes and mints. The schema
   supports either behaviour, so the choice is reversible in code. **OWNER ratification pending.**
2. **Success case.** `VZ-INSTALL-003` says *"Claim with valid token yields owner role; admin surface
   returns 200."* The second clause is **not demonstrable at M1-A** — there is no admin surface and
   no session. Evidence is owed by M1-C (`VZ-AUTH-004`). The first clause is demonstrated here.
3. **Surfaces.** `surfaces.api` lacks `GET /api/v1/setup/claim-status` and `surfaces.cli` is `[]`
   while this slice adds `vizra claim-token`. The chair updates both through the generator.

---

## 14. Progress and evidence

**Phase 1 (2026-09-21).** Plan written; design mechanics validated on PostgreSQL 17.11 (design
validation only). PLAN_READY.

**Phase 2 (2026-09-21).** Revision 2 written against the rulings. Preflight: Go 1.26.2, sqlc v1.31.1,
PostgreSQL 18.6, Valkey 9.1.2 — all present.

**Preflight gates (§11), both PASSED before any handler code:**

- `sqlc generate` put **no generated column** in any INSERT column list, and the explicit casts in the
  `ClaimOwner` CTE produced fully typed parameters (`[]byte`, `uuid.UUID`, `string`) rather than
  `interface{}`. `sqlc diff` clean. The B-R1/B-R11 risk did not materialise.
- Migration 0005 applies and rolls back on PostgreSQL 18.6; every invariant probed directly
  (second live owner → 23505 `users_one_owner`; tombstoned owner → replacement **succeeds**;
  audit UPDATE/DELETE/TRUNCATE → 42501; user named by an audit row → 23503; plaintext and bcrypt
  refused by `credentials_password_is_argon2id`; second password credential → 23505; token
  singleton and terminal-state CHECKs fire).

**Rebased onto `origin/main` 5eb2829 (PR #7, `vizra healthcheck`)** before any push. One conflict, in
`cmd/vizra/main.go`'s subcommand switch, resolved **additively** — both `healthcheck` and
`claim-token` are registered. All evidence below was retaken after the rebase; the pre-rebase runs
are discarded.

| Lane | Command | Result |
|---|---|---|
| Gate | `make ci` | **exit 0** — all 10 lanes |
| Integration | `go test -tags=integration -race -count=1 -v ./internal/integration/` | **exit 0** — 102 run, 102 passed, **0 failed, 0 skipped** |
| Shuffle | `make test-integration-shuffle` | **exit 0** |
| Mutations | `docs/evidence/m1a-owner-claim/demonstrate.sh` | 23 cases, 0 failed, 0 harness-fail |

Environment: darwin/arm64, go1.27.1 toolchain, PostgreSQL **18.6** (container `vizra-m1a-pg18`),
Valkey **9.1.2** (container `vizra-m1a-valkey`). Artifacts in `vizra-core` under
`docs/evidence/m1a-owner-claim/`.

**Two harness defects the before/after digest gate caught in itself**, both fixed and recorded rather
than quietly patched: the restore covered the mutated `.sql` but not the sqlc-generated Go beside it
(so a following GREEN run failed for an unrelated reason), and MUT-27's pattern had stopped matching
(reported `HARNESS-FAIL`, never as a pass).

**Three properties are review-only, measured rather than assumed** — listed in the transcript beside
MUT-4 instead of being implied as covered: the constant-time comparison; passing the row's own digest
rather than the presented one; and the `consumed_at` / `superseded_at` predicates in the redeem CTE.
The last is the interesting one: dropping `consumed_at IS NULL` leaves the race test **green**,
because `users_one_owner` plus the 23505→409 mapper produce exactly the answer the row guard would
have. That is defence in depth working, and it is reported as such.

## 15. Blockers and handoff

No external blocker. `VIZRA_TRUSTED_PROXIES` does not exist, so `ip_prefix` is NULL behind a proxy and
the per-origin failure bucket is inert there — stated in the PR body so it is not mistaken for
working. M1-B owns it.
