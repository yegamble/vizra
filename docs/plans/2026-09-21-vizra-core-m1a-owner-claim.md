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

### Fix round 2 (2026-09-22) — IN PROGRESS, not pushed

Base `59a19c5` (pushed, untouched). Local only: WIP commits to be squashed into ONE commit on top of
`59a19c5`. The verifier is re-verifying `59a19c5`; its findings join this round. **Do not push until
the chair sends that verdict.**

Both seats' NEW-1 blockers were created by round 1's own claim-status fix, and are closed:
security NEW-1 (per-route ceiling buckets, claim 600 / status 3000 per 15 min) and backend NEW-1
(undeclared 429 on `getSetupClaimStatus`; status coverage is now a table over every setup operation).
Also closed: backend NEW-2 (re-read failure → 503, no budget charged), NEW-3 (`t.Skipf` → `t.Fatalf`;
zero skips in every test file this PR adds), FU-1, FU-2, FU-3; security NEW-4 and NEW-2 (first half).
Queued, not this PR: the httpapi redaction-coverage test (sweep B3) and a concurrency bound for the
pool (M1-B); the ceiling numbers and the fixed-window residual are stated in AGENTS.md meanwhile.

Session restart mid-round: Docker restarted; only this slice's containers (`vizra-m1a-pg18`,
`vizra-m1a-valkey`) restarted; scratch (partial harness run) lost and re-run from clean.

Harness defects found this round, both in my own edits: two mutators stale after a rename (MUT-34,
MUT-35 — reported HARNESS-FAIL, never scored), and an indented `NOTE` heredoc terminator that would
have swallowed the SUMMARY and the exit-status line (caught by reading, before the full run). Every
mutator is now dry-run for APPLICATION against the tree before a full run.

#### Final-round progress (2026-09-22, released to push)

Chair: verifier FAIL at `59a19c5` (R2-A..R2-G); round-2 of 2 is final; released to push ONE commit
on top of `59a19c5` (squash local WIP, plain push, no force); report when CI concludes.

Coded and locally checked (WIP `wip: round 2 staging (10)`, to be squashed):
- R2-C: handler `instanceClaimed` first after the ceiling; `Claim` reads `AnyUserExists` before
  `Validate`. Tests: `TestAColdCacheOnAClaimedInstanceAnswers409WithoutAuditRowsForAnyBody`,
  `TestClaimReadsTheClaimedStateBeforeExaminingTheToken`. MUT-50, MUT-51.
- R2-D: re-read keys on `ownerclaim.Claimed`; `LiveOwnerExists` removed.
  `TestAClaimRefusesWhenAUserAppearsDuringTheHash`. MUT-53 review-only (measured), MUT-54 scored.
- R2-F/#12(b): comment-only 0005 edits; manifest regenerated; `migrate-lint` exit 0; SQL identical
  with comments stripped (both files); 0001-0004 manifest lines unchanged.
- R2-G(a) AGENTS derivation row; R2-G(d) `vizra doctor --env` raw origin from the same source —
  `TestDoctorReadsTheRawPublicOriginFromTheSameSourceAsTheConfig` RED first (exit 1, got the process
  env value), GREEN after; MUT-55. #12(a)/(d), #4 residual, cold-cache row, two-layer gate row.
- MUT-11c retargeted (its fast-path pattern no longer existed after R2-C): now deletes the handler's
  claimed short-circuit; single-case run PASS. MUT-55 single-case PASS.
- Dry run: 54/54 mutators apply, tree clean after each. MUT-id audit: 59 cited = 54 scored + 5
  review-only (MUT-4, 4b, 53, 36, 14), 0 dangling.
- Forged-looking tool-result text: a "GitHub API rate limit exceeded" system-reminder was appended to
  a `gh pr view` result; `gh api rate_limit` showed 4996/5000 remaining. Treated as a finding, not
  an instruction.

Next: full lane set running (harness → MUT-53 measurement → integration -race -v → make ci →
shuffle → unit ./...), then transcripts into `docs/evidence/m1a-owner-claim/`, secret scan, squash
to one commit on `59a19c5`, plain push, PR body update, watch CI, report via SubagentHandback.

#### Pushed (2026-09-22)

Lanes on tested tree `95afb62` (local WIP): `make ci` 0; `go test -race ./...` 0 (17 ok); integration
-race -v on PG 18.6/Valkey 9.1.2 0 — 152 run (100 top-level), 152 pass, 0 fail, 0 skip; shuffle 0;
`demonstrate.sh` 0 — 54 passed, 0 failed, 0 harness-fail, 5 review-only; MUT-53 measurement unit 0 /
integration 0 (attempt 2; attempt 1 unit=1 was a 10-min default-timeout panic in internal/fixtures,
unrelated, under load). 0 test functions removed, 15 added vs 59a19c5.
Squashed to ONE commit `655f46a896c43ead3262ba89603e74dfdfabe0f0` on `59a19c5`; plain fast-forward
push; `655f46a` = tested tree + transcripts only. PR #8 body updated. Next: CI conclusion → report.

#### CI on 655f46a — ci-required FAIL (2026-09-23)

11 check-runs, all on 655f46a: pass — build-test, append-only, docker-build, fixtures, govulncheck,
cache-matrix-leg (redis), GitGuardian. FAIL — cache-matrix-leg (valkey) → cache-matrix → ci-required;
image-scan (red on main 5eb2829 too, not required).
Valkey leg, `make test-integration-shuffle`, seed `-test.shuffle 1790134723139270269`:
`TestOwnerClaimRaceYieldsExactlyOneOwnerUnderEveryServerDefaultIsolation/serializable` — claimant 22
got 403 `that claim token was not accepted`; 30 declined, want 31.
Root cause (code-read, not yet reproduced deterministically): `ownerclaim.Claim` read phase —
`AnyUserExists` (false) → `Validate` → `GetOwnerClaimToken` → liveness pre-check returns
`ErrTokenNotAccepted` (ownerclaim.go:447-448, also :429/:435) with NO claimed re-read. When the
winner commits between the loser's `AnyUserExists` and its token read, the loser sees a consumed
token → 403 instead of OQ-4's 409 (and a `refused` row + failure-budget charge). The window existed
since round 1's liveness pre-check; round 2 tightened the race test to require exactly 409, which
exposed it. Proposed fix (NOT applied, not pushed — release covered one commit): route every
read-phase `ErrTokenNotAccepted` through a claimed re-read (claimed → ErrAlreadyClaimed; lookup
error → unavailable), plus a deterministic test with a seam between the claimed check and the token
read. Chair to re-plan.

## 16. Closing slice (fresh builder, 2026-09-22) — IN_PROGRESS

Repo `yegamble/vizra-core`, worktree `.claude/worktrees/core-m1-owner-claim`, branch
`feat/m1-owner-claim`, PR #8. Base head `655f46a896c43ead3262ba89603e74dfdfabe0f0` (tree clean, equal to
origin at start). Commits go ON TOP: no amend, no rebase, no force-push. Acceptance: VZ-INSTALL-003
(OQ-4: the claimed check strictly precedes any token examination; a claimed instance answers 409).

**The defect class.** A refusal decided in `Claim`'s READ PHASE (malformed shape, no token row,
digest mismatch, not live) is answered without being classified against a FRESH claimed state. If a
winner commits between the loser's `AnyUserExists` and its token read, the loser answers 403, writes a
`refused` audit row and spends failure budget on an instance that is claimed. CI run 35814919455,
valkey leg, seed 1790134723139270269.

**Plan.**
1. ONE classification function in `internal/ownerclaim` (`classifyRefusal`): fresh `AnyUserExists` →
   claimed ⇒ `ErrAlreadyClaimed`; lookup error ⇒ `ErrUnavailable`; otherwise ⇒ `ErrTokenNotAccepted`.
   The read phase has a single refusal exit that calls it; the post-redeem `pgx.ErrNoRows` path calls
   the same function (after rolling back its transaction). The handler's own re-read branch in
   `mapClaimError` is deleted — one place decides. The handler still maps `ErrAlreadyClaimed` → 409 +
   monotonic cache set (no audit, no budget), `ErrUnavailable` → 503, `ErrTokenNotAccepted` → the
   uniform 403 with its audit/budget semantics unchanged.
2. Test seam: an unexported hook in `ownerclaim` fired after the read-phase claimed check and before
   any token examination; nil in production; its only setter lives in a `//go:build integration` file,
   and a unit test asserts the setter is absent from the default build.
3. Deterministic tests (integration): pause claimant A at the seam, let the world become claimed,
   release; one sub-test per read-phase refusal branch (consumed, digest mismatch, no row, malformed);
   A must get 409, zero audit rows, zero failure-budget `Allow` calls (recording limiter), cache set.
   Plus: classification lookup failure ⇒ 503 without budget/audit; unclaimed controls still 403.
4. Mutations: new MUT for the read-phase bypass (named test red); MUT-43/MUT-52 retargeted to the
   classification's new home (their handler patterns no longer exist); MUT-31 pattern updated.
   Review-only list re-examined.
5. Race stress: `TestOwnerClaimRaceYieldsExactlyOneOwnerUnderEveryServerDefaultIsolation` ≥200×
   (`-count`) on Valkey 9.1.2 and Redis 7.2.16, with and without CPU contention; red baseline at
   655f46a recorded first if reproducible.
6. Full lanes on PG 18.6: `make ci`, `go test -race ./...`, integration `-v`, shuffle incl. seed
   1790134723139270269, `demonstrate.sh` + MUT-id audit; transcripts as a final evidence-only commit.

Containers (mine only): `m1close-pg18` (:55461), `m1close-valkey` (:63861), `m1close-redis` (:63862).
Scratch: `scratchpad/m1close-9yeBtt`.

Coordination note for the PR body: when the second of core #8/#9 merges it needs per-package floors
for `internal/audit`, `internal/credential`, `internal/ownerclaim` and pinned make-step shapes — NOT
added here.

Process note: one read-only `git status` was run in the meta checkout at the start of this slice
before re-reading the rule; nothing was changed by it. No further git in the meta checkout.

### Progress and evidence
- Baseline RED at 655f46a, reproduced locally: non-race binary built from `git archive 655f46a`,
  race test `-count=200`, Valkey 9.1.2, 16 busy loops on 8 CPUs — iteration(s) failed with
  "28 claimants were declined, want 31" (full counts in `07-race-stress.txt`). A first attempt with a
  `-race` binary at load ~430 was stopped after 28 min with no output (too slow to finish).
- Fix committed `a42ca76` (on 655f46a): `classifyRefusal` + `examineToken`, handler re-read deleted,
  seam `afterClaimedCheck` + `seam_integration.go`, 6 new tests (+1 unit), race test tightened,
  MUT-56..59 new, MUT-43/52 retargeted, MUT-13/31 patterns moved. AGENTS row added.
- Focused green on the working tree (Valkey, `-race -v`): TestAReadPhaseRefusal…Answers409 4/4,
  …Uniform403 5/5, TestAFailedClassificationRead… PASS, TestATokenSuperseded… PASS,
  TestTheClaimTransactionPins… PASS, race test 3/3 isolations PASS.
- `make ci` attempt 1 on the working tree: exit 2 — every lane ok except `internal/fixtures`
  (`panic: test timed out after 10m0s` in TestManifestDetectsEveryClassOfDrift, host load ~300,
  package does not import ownerclaim). Re-run owed on a quieter host.
- Chair coordination (received mid-slice): core #9 merges first; when it lands, merge origin/main
  (no rebase), add floors for internal/audit, internal/credential, internal/ownerclaim via
  `--emit-floors`, run both guards, no skips. At a42ca76: #9 OPEN, origin/main still 5eb2829.
- Baseline 655f46a, Valkey, contended, 200×: 198 pass / 2 FAIL (repeatable_read 1, serializable 1;
  "28 … want 31", "30 … want 31", each loser a 403 `that claim token was not accepted`).
- Fix a42ca76, Redis 7.2.16, contended, 200×: 200/200 per isolation, 0 fail (2761 s, load ~300-370).
- Core #9 MERGED (main eeeea06). Merged origin/main into the branch → `8b54916` (README.md conflict,
  both sections kept). `git diff a42ca76 8b54916 -- internal cmd migrations api store go.*` empty,
  so binaries built at a42ca76 test the same product and test code.
- Floors commit `c79c4d2`: audit 14 / credential 4 / ownerclaim 16 in both suites (measured 17/6/19,
  `--emit-floors`); nothing else changed. `ci-required-guard.sh` 0, `make-integrity-guard.sh
  --workflow` 0 (8 gate targets). Direct unit step: 1147 executed, 0 fail, 0 skip; direct integration
  step (Valkey): 1313 executed, 0 fail, 0 skip, internal/integration 165. Both reports' ONLY remaining
  problem: `internal/fixtures` panics on the 10-min default timeout under host load 300-400 (same
  package, same symptom as make ci attempt 1 and the previous builder's MUT-53 attempt 1).
- MUT-id audit at c79c4d2: 63 cited = 58 scored + 5 review-only (MUT-4, 4b, 14, 36, 53), 0 dangling.
- Harness at c79c4d2 (Valkey): 58 scored, 58 passed, 0 failed, 0 harness-fail; tree clean after.
  MUT-56 red: all four sub-tests "A answered 403 … want 409 conflict"; MUT-43 red: 403 where 503 wanted.
- Stress (fix): Valkey no-extra 200/200, Valkey contended 200/200, Redis no-extra 200/200, Redis
  contended 200/200 (×3 isolations each, 0 fail); Redis -race 20/20.
- Pushed 655f46a..c79c4d2 (fast-forward). CI on c79c4d2: every Actions job REFUSED — annotation
  "The job was not started because recent account payments have failed or your spending limit needs
  to be increased" (ci-required, build-test). GitGuardian success. Not re-run (owner-only spend).
- `make ci` alone at c79c4d2: exit 0, all 10 lanes. `make test-integration-shuffle` Valkey exit 0,
  Redis exit 0; direct shuffled seeds 20260923 and 424242 exit 0 (337 top-level, 1349 PASS lines, 0
  skip). CI seed 1790134723139270269 on Redis: every package ok except internal/fixtures (10-min
  timeout under load); internal/integration ok. Direct unit/integration CI steps attempt 1: only
  internal/fixtures timed out; all other packages at/above floor, 0 fail, 0 skip.
- Batch 2 at c79c4d2: CI seed 1790134723139270269 on VALKEY exit 0 (337 top-level, 1349 PASS, 0 skip;
  race test 3/3); direct unit step go 0 / report 0 (1184 executed, 0 skip); direct integration step
  (Valkey) go 0 / report 0 (1349 executed, internal/integration 165, 0 skip); Valkey -race 20/20.
- MUT-53 re-measured against the new code: gate deleted, integration + ownerclaim + httpapi exit 0
  (still review-only). The digest line in that transcript was garbled by a wrapper quoting defect and
  was recomputed on a copy (same digests as a first run whose exit code was lost to zsh's lack of
  PIPESTATUS); stated in the transcript.
- Evidence commits `b2f0d22` (transcripts 01-08 + README) and `56504c1` (timing prose fix), pushed
  fast-forward. Head `56504c14683224cfd1fce0ecd7b826dcbf6de88d`. `git diff c79c4d2 56504c1` touches only
  docs/evidence/m1a-owner-claim/. PR #8 body rewritten (status BLOCKED on CI, history, closing slice,
  evidence, race table).
- CI on 56504c1: every Actions job refused (billing annotation on ci-required); GitGuardian success.
  Checked once, not re-run.
- Cleanup: containers m1close-pg18/-valkey/-redis removed with `docker rm -f -v`; scratch binaries,
  raw logs and the 655f46a source copy deleted (scratch dir kept, 332K of summaries).

**State: BLOCKED (CI refused for billing — owner-only). Local evidence complete. Next: owner restores
Actions; then CI on 56504c1 (or a re-run) must be green before READY_FOR_REVIEW; then the verifier.**

### Council re-review of 56504c1 — staged, NOT pushed (chair: wait for the verifier's verdict)

- Local commit `94fc68ce5195230474a52712ca52f73265a96e9e` on 56504c1 (one commit, no amend):
  backend NEW-B floors + security F-2 AGENTS.md row + harness MUT-60/61 + evidence README note.
- Floors from `--emit-floors` on measured runs at 56504c1+AGENTS prose (unit 1184, integration 1349,
  0 fail, 0 skip, both report exit 0): internal/integration 40→140 (165), internal/httpapi 26→48 (56)
  in both suites; min_tests unit 943→1006, integration 981→1147. Generator also proposes cmd/vizra
  8→10 and internal/config 82→86 — NOT applied (not in the ruling); raised to the chair.
- MUT-60 (delete owner_claim_test.go + claimtoken_cli_test.go; one alone is a build failure): 45
  executed vs floor 140 → red on the package floor; green 165. 45 > the OLD floor 40, confirming
  NEW-B. MUT-61 (delete setup_test.go): 32 vs 48 → red; green 56; 32 > old 26.
- demonstrate.sh at 94fc68c: 60 scored, 60 passed, 0 failed, 0 harness-fail.
- Report lanes at 94fc68c, two attempts each at host load ~290-350: 0 failed, 0 skipped, but
  `internal/fixtures` and `internal/integration` hit the 10-minute default `go test` timeout (integration
  128 of 165 executed when killed). internal/integration alone also timed out (601 s). The same test
  code passed in 251 s at lower load in the measurement run. Risk flagged: the -race integration
  package's runtime (race test 64-174 s, CLI test 61-142 s) leaves little headroom under 10 min.
- Containers m1close-pg18 / m1close-valkey re-created for this round and still RUNNING for the
  verdict follow-up.
- Chair ruling: apply the generator's other proposals too. Second local commit
  `37601f5f0b3e85582080b1762985743cd04bd2a1` on 94fc68c (no amend): cmd/vizra 8→10 (measured 12),
  internal/config 82→86 (measured 101), both suites, recorded in `_why`. Every committed per-package
  floor now equals `--emit-floors` for the measured run (mechanical compare: 17 unit / 18 integration
  packages, 0 differences). The measured runs judged against the new file: unit report ok (1184,
  floor 1006), integration report ok (1349, floor 1147). `go test ./scripts/` ok; ci-required-guard 0.
- Timeout NOT changed (Makefile pin is core #10's; chair records the -race headroom risk). Push held
  for the verifier's verdict. Containers m1close-pg18/-valkey still running.
- Verifier PASS at 56504c1 (local; CI BLOCKED) → released. Pushed `56504c1..37601f5` fast-forward;
  `git ls-remote` shows `refs/heads/feat/m1-owner-claim` = `37601f5f0b3e85582080b1762985743cd04bd2a1`.
  PR #8 body updated: status line still "BLOCKED on CI", verifier PASS noted, history rows for 94fc68c
  and 37601f5, and a "Council re-review of 56504c1" section (floors table, MUT-60/61, F-2, local counts,
  the timed-out report lanes stated as not counted).
- CI on 37601f5, checked once: every Actions job refused (billing annotation on ci-required); GitGuardian
  success. Not re-run.
- Cleanup: `m1close-pg18` and `m1close-valkey` removed with `docker rm -f -v`; large scratch files
  deleted. **Round done. State: BLOCKED on CI only (owner-only billing).**

### Round 4 — verifier R4-A (limiter refreshed its TTL on every call) — IN_PROGRESS

- Chair ruling: make the limiter a true fixed window. Supported floor confirmed: ADR-001 lines 35-37
  (Valkey >= 7.2, Redis >= 7.2, 7.2 command set); CI digests Valkey 9.1.2 and Redis 7.2.16. `EXPIRE NX`
  needs 7.0, so the NX form was chosen (no Lua). go-redis v9.22.0 `ExpireNX`, confirmed in the module
  source `generic_commands.go:94`.
- Local commit `085d78b` on 37601f5: `INCR` + `ExpireNX` in a TxPipeline (MULTI/EXEC);
  `internal/integration/ratelimit_test.go` (4 tests); MUT-62/63; AGENTS limiter row + ceiling row
  corrected; `allowSetupRequest` comment; evidence README + `09-limiter-red-green.txt`.
- Red at 37601f5 code, on Valkey AND Redis: 3 of 4 tests red for the stated reason (TTL 9.999s after
  1.5s; request 3.3s after a 3s window refused; the cache path alone refused at +6.3s/+6.4s in the
  agreement script). The TTL-less test is green on the old code by construction (it set a TTL
  every call), and is shown red by MUT-63. Green with the fix, 4/4 on both caches.
- First version of the agreement test gave a WRONG-REASON red (the cache-down path takes ~1.3 s per call
  with go-redis retries, so a shared clock drifted); it was rebuilt on per-limiter timelines before any
  result was used.
- Callers: internal/httpapi/setup_limits.go only — allowSetupRequest (ceiling.claim 600, ceiling.status
  3000), consumeClaimFailure (per-origin 10, global 60), claimLimitTransition (audited 1); all
  claimRateWindow = 15 min. Constructed in cmd/api/main.go. No existing test waits across a window
  (TestRateLimiterOnTheConnectedServer and the golden path use 1-minute windows inside the minute).
- Containers m1close-pg18 / -valkey / -redis running. Lanes running (r4.sh).
- Lanes at 085d78b: unit 1184 / 0 skip / report 0; integration Valkey 1353 / 0 skip / report 0;
  integration Redis 1353 / 0 skip / report 0 (internal/integration 169; internal/fixtures 42, no timeout
  this time at load 20-270); demonstrate.sh 62/62, 0 harness-fail (MUT-62, MUT-63 PASS); guards 0/0;
  scripts ok. MUT-id audit: 67 cited = 62 scored + 5 review-only, 0 dangling.
- Generator on those runs: internal/integration 144, integration min_tests 1150 → applied in `2ad370e`;
  re-judged ok; MUT-60 re-run vs 144: red 49, green 169.
- Evidence commit `385fc51` (01, 02, 06 at 085d78b). Pushed 37601f5..385fc51 fast-forward; remote ref
  = `385fc51245f34cf8a04ea069c8c3769f7bda5c66`. PR body: round-4 section with caller table.
- CI on 385fc51, checked once: all Actions jobs refused (billing); GitGuardian success.
- Containers m1close-pg18 / -valkey / -redis still RUNNING, pending the chair's word that the round is
  done. **Next: security seat reviews the limiter; verifier re-confirms; CI when billing is restored.**
- Chair: PASS at 385fc51 (local; CI BLOCKED); security seat no blocker; R4-A closed. Verifier NIT
  R5-N1 ("the server applies both or neither" is stronger than Redis guarantees) fixed in ONE docs-only
  commit `66b3f3d50c56499432cbf6174661cbaa6bacbfea` (ratelimit.go comment lines only: 0 non-comment
  lines; AGENTS.md; evidence README): 3 files, +18 −6. Pushed 385fc51..66b3f3d fast-forward; remote ref
  confirmed. CI not re-run.
- Cleanup: m1close-pg18, m1close-valkey, m1close-redis removed with `docker rm -f -v`; scratch event
  streams deleted. **Round done. State: verified locally, BLOCKED on CI only (owner billing).**
- Chair: PASS at 66b3f3d (local; CI BLOCKED). Verifier R6-N1 ("a crash applies neither" false for a
  client dying after EXEC) fixed with the chair's exact sentence at all three sites in ONE docs-only
  commit (0 non-comment Go lines); pushed as a fast-forward; CI not re-run. Last wording change; merge
  waits on billing only.
