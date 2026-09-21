# Independent verification — vizra-core PR #8, M1-A secure one-time owner claim (VZ-INSTALL-003)

- **Verifier:** war-room independent verifier (did not write this code)
- **Date:** 2026-09-21
- **PR:** https://github.com/yegamble/vizra-core/pull/8
- **Head SHA verified:** `32b616dcd6d9ed3ea8d05020e1d66dae25c0e8ed`
- **Branch:** `feat/m1-owner-claim`, ONE commit, rebased on `main@5eb2829`, 43 files +6043 −15
- **Binding spec:** `docs/evidence/warroom/2026-09-21-vizra-core-m1a-owner-claim-PLAN-RULINGS.md` and the two seat reviews it cites
- **Status at start of run:** branch had NOT moved (`gh pr view 8 --json headRefOid` = `32b616dc…`)

> This file is written incrementally. Findings use `.claude/council/finding-format.md`.

## 0. Environment

| Item | Value |
|---|---|
| Clone | fresh `git clone` into `$SCRATCH/vzv-core-pr8-8vKWhf/src`, checked out at the SHA, `git status` clean |
| Host | darwin 25.5.0, arm64 |
| Go | go1.27.1 darwin/arm64 |
| sqlc | v1.31.1 (ADR-001 pin) |
| Docker | 29.8.0 |
| PostgreSQL | `postgres:18` → **PostgreSQL 18.6** (Debian 18.6-1.pgdg13+2), container `vzv8-pg`, port 55811, `max_connections=400` |
| Cache | `valkey/valkey:9.1.2`, container `vzv8-cache`, port 63811 |
| Isolation | own `mktemp -d`; own container name prefix `vzv8-`; ports not used by `vzb1-*`, `vizra-m1a-*` or `vidra-*` |

CI pins PostgreSQL by digest `postgres@sha256:86c951e05bf5…` and Valkey by
`valkey/valkey@sha256:c123e3715db6…`; the local `postgres:18` and
`valkey/valkey:9.1.2` images resolve to those same image ids
(`86c951e05bf5`, `c123e3715db6` per `docker ps` image column).

## 1. GitHub CI on this SHA — VERIFIED GREEN

`gh api repos/yegamble/vizra-core/commits/32b616dc…/check-runs`:

| Check | Status | Conclusion |
|---|---|---|
| `append-only` | completed | success |
| `build-test` | completed | success |
| `cache-matrix` | completed | success |
| `cache-matrix-leg (redis, …)` | completed | success |
| `cache-matrix-leg (valkey, …)` | completed | success |
| `docker-build` | completed | success |
| `fixtures` | completed | success |
| `govulncheck` | completed | success |
| `GitGuardian Security Checks` | completed | success |
| **`ci-required`** | **completed** | **success** |
| `image-scan` | completed | **failure** (NOT required — see below) |

`ci-required` job log (run 35579471414, job 106268738827, head_sha
`32b616dc…`) ends with:

```
  SUCCESS   append-only
  SUCCESS   build-test
  SUCCESS   cache-matrix
  SUCCESS   fixtures
  SUCCESS   govulncheck
  SUCCESS   docker-build

all 6 required check(s) succeeded
```

`.github/required-checks.txt` lists exactly those six non-comment lines. **The
manifest matches the jobs that actually ran — no listed-but-unexecuted lane.**

`image-scan`: red on this SHA **and red on `main@5eb2829eb4f830206029f8e2a836f93a44a93a02`**
(verified by check-runs on main). It is deliberately absent from
`required-checks.txt` with a documented rationale. `git diff 5eb2829 HEAD --
.github/ Dockerfile scripts/` is **EMPTY** — this PR touches no workflow, no
Dockerfile and no CI script, so it did not change that lane.

## 2. Local lane set

(section filled in as lanes complete)

All lanes run from the clean clone at `32b616dc…`, PostgreSQL 18.6 + Valkey 9.1.2.

| Lane | Command | Exit | Result |
|---|---|---|---|
| `make ci` (10 lanes) | `make ci` | **0** | `make ci: all lanes passed` — fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify, test-race |
| tidy | `make tidy-check` | **0** | `go mod tidy -diff` clean |
| sqlc verify | `sqlc diff` | **0** | `internal/store/sqlcgen` matches `store/queries` + migrations — **generated, not hand-edited** |
| CI guard 1 | `scripts/ci-required-guard.sh` (inside `ci-guard`) | **0** | floor lanes present, runners/actions pinned |
| CI guard 2 | `scripts/make-integrity-guard.sh` (inside `ci-guard`) | **0** | `passed (8 gate target(s))` |
| fixtures | `make fixtures-verify` | **0** | 12 fixtures, 1 791 508 bytes, byte-identical |
| integration (slice) | `go test -tags=integration -race -count=1 -json ./internal/integration/` | **0** | **72 top-level tests / 72 pass / 0 fail / 0 skip** |
| integration (all) | `go test -race -count=1 -tags=integration -json ./...` (= `make test-integration`) | **0** | **284 top-level / 284 pass / 0 fail / 0 skip** (1 160 incl. subtests) |
| shuffled | `go test -race -count=1 -shuffle=on -tags=integration -json ./...` | **0** | **284 / 284 / 0 fail / 0 skip** |

Counts are mine, computed from `-json` by counting `Action ∈ {pass,fail,skip}` events
with no `/` in `Test`. **Zero skips anywhere.** The builder's transcript claim of
"102 run / 102 passed / 0 skipped" is the `-v` transcript of
`./internal/integration/` and matches its own file
(`01-integration-pg18.txt`: 102 `=== RUN`, 102 `--- PASS`, 0 SKIP) — that count
includes subtests; my top-level count for the same package is 72. Both are true;
neither over-claims.

### Migration 0005 — up → down → up on a fresh PostgreSQL 18 database

Applied 0001…0005 to a virgin database, then 0005 down, then 0005 up again. All
five applied with `ON_ERROR_STOP=1`; the down dropped exactly the 0005 objects
(`users`, `credentials`, `owner_claim_tokens`, `user_role`, both triggers, the
function, the FK) and the re-apply succeeded. Live schema, read back from the
database:

- generated columns present: `username_fold ALWAYS lower(username)`, `email_fold ALWAYS lower(email)`
- `users_one_owner` → `CREATE UNIQUE INDEX users_one_owner ON public.users USING btree (role) WHERE ((role = 'owner'::user_role) AND (tombstoned_at IS NULL))` — **the tombstone predicate is present and the index name matches `mapClaimError`'s literal**
- `users_email_fold_key` partial (`WHERE email_fold IS NOT NULL`), `users_username_fold_key` total
- `user_role` enum order: `guest, member, manager, admin, owner`
- `migrations/manifest.sha256`: all ten digests recomputed by me and **identical**
- `git diff 5eb2829 HEAD -- migrations/` touches only the two 0005 files and the manifest — **0001–0004 byte-identical to main**

Audit trigger, exercised directly against the live table:

```
[update audit_events set action='y'] -> ERROR:  audit_events is append-only (attempted UPDATE)
[delete from audit_events]           -> ERROR:  audit_events is append-only (attempted DELETE)
[truncate audit_events]              -> ERROR:  audit_events is append-only (attempted TRUNCATE)
```

`credentials` CHECKs, exercised directly (control confirmed working — see FINDING 5
for the missing test):

```
'hunter2plaintext'          -> ERROR: violates check constraint "credentials_password_is_argon2id"
'$2y$10$bcryptstyle'        -> ERROR: violates check constraint "credentials_password_is_argon2id"
'$scrypt$x'                 -> ERROR: violates check constraint "credentials_password_is_argon2id"
'$argon2id$v=19$m=…'        -> INSERT 0 1
1025-octet secret           -> ERROR: violates check constraint "credentials_secret_bounded"
kind='totp'                 -> ERROR: violates check constraint "credentials_kind"
```

## 3. The single-owner race, measured by me on the real HTTP path

My own probe (`TestVZV_RaceTable`, not the builder's), n=24 concurrent valid
claims through `Server.Handler()`, after asserting `SHOW default_transaction_isolation`
actually equals the level under test:

| server `default_transaction_isolation` | 201 | 409 `conflict` | 403 | 5xx | users | live owners | credentials | consumed tokens | token rows | `succeeded` audit rows |
|---|---|---|---|---|---|---|---|---|---|---|
| read committed  | **1** | **23** | 0 | **0** | 1 | 1 | 1 | 1 | 1 | 1 |
| repeatable read | **1** | **23** | 0 | **0** | 1 | 1 | 1 | 1 | 1 | 1 |
| serializable    | **1** | **23** | 0 | **0** | 1 | 1 | 1 | 1 | 1 | 1 |

Every loser gets the *same* declared answer (409 / `conflict`) at every level.
Ruling B-4 satisfied. The builder's own `TestOwnerClaimRaceYieldsExactlyOneOwnerUnderEveryServerDefaultIsolation`
(n=32 × 3 levels) also passed in every run above.

### Out-of-band owner (S-9) and the `users_one_owner` mapper branch

The builder's `TestOwnerInsertConflictMapsTo409NotFiveHundred` inserts a
**committed** owner and then claims. That request is caught by
`AnyUserExists` → `ErrAlreadyClaimed` and **never reaches `ClaimOwner`**, so
`users_one_owner` does not fire (see FINDING 9). I forced it deterministically
instead: a second connection holds an **uncommitted** owner insert, the claim
passes the claimed check, blocks on the unique index inside `ClaimOwner`, and the
out-of-band transaction then commits:

```
claim against a concurrently-committed out-of-band owner: HTTP 409 code="conflict"
users = 1, credentials = 0, consumed tokens = 0
```

**409, zero 5xx, no orphan credential, token unconsumed.** The ruling's substance holds.

### Tombstone (B-1) and "can a stale token ever mint a second owner?"

Reproduced `TestASecondLiveOwnerIsRefusedByTheDatabase` and
`TestATombstonedOwnerDoesNotPermanentlyBlockOwnership` green, and read the gate
myself. The claim gate is `SELECT EXISTS (SELECT 1 FROM users)`
(`store/queries/owner_claim.sql:12`), which is **monotonic**: `users` rows are
never deleted (`audit_events_actor_user_fk … ON DELETE RESTRICT`, and the
`succeeded` audit row always names the owner), and tombstoning does not remove
the row. So on a claimed instance — tombstoned owner or not — `Claim` returns
`ErrAlreadyClaimed` **before any token is examined**. A consumed or stale token
can never mint a second owner. Confirmed by mutation V11 below.

On MUT-1b (dropping `consumed_at IS NULL` from the redeem CTE): I verified the
builder's reasoning is not merely convenient. `consumed_at` is set only inside the
one statement that also inserts the owner, in one transaction, so **`consumed_at IS NOT NULL` ⟺ a user row exists**;
there is no state in which a consumed token meets an unclaimed gate, including
after tombstoning. The property is genuinely unobservable. Declaring it
review-only is correct.

## 4. The builder's 23 mutations — ALL REPRODUCED

`docs/evidence/m1a-owner-claim/demonstrate.sh`, run by me from the clean clone:

```
passed:       23
failed:       0
harness-fail: 0
```

MUT-1, 2, 2b, 16, 3, 6, 14, 5b, 9, 9b, 19, 11b, 10, 10b, 24, 13, 18, 8, 25, 26,
15, 12, 27 — every one RED under its mutation and GREEN when restored, with the
before/after digest gate satisfied in all 23.

**Byte-identical restore verified, including sqlc-generated files.** After the
run: `git status --porcelain` empty, `git diff --stat HEAD` empty,
`git diff --name-only HEAD -- internal/store/sqlcgen/` empty, `HEAD` unchanged.
The `EXTRA_RESTORE` mechanism the builder added after its harness once missed a
generated file does work.

## 5. My own mutations — 13 cases, independent of the builder's harness

Each digest-gated; each must turn a **named** test red. `RED`/`GREEN` is what I required.

| id | mutation | expected | observed |
|---|---|---|---|
| V1 | compare the PRESENTED RAW token against the stored digest | RED | **RED** |
| V1b | `subtle.ConstantTimeCompare` → hand-rolled non-constant-time compare | GREEN (builder declares review-only) | inconclusive — my edit left `crypto/subtle` unused, so the package failed to *compile*. Not a behavioural observation; the builder's declaration stands on inspection |
| V2 | **mint at boot when announce is `off`** | RED | **RED** (`TestBootMintsOnlyUnderTheStderrOptIn`) |
| V3 | **`vizra claim-token` mints on a CLAIMED instance** (drop `refuseIfUsersExist`) | RED | **STAYED GREEN → FINDING 2** |
| V4 | **ip_prefix emits a prefix for loopback** (`::1` → `::/64`) | RED | **RED** (`TestIPPrefix…`) |
| V5 | **echo the token and password into a log line / audit row** | RED | **RED** (log-scrape + audit-scrape both fire) |
| V6 | skew `minted_at` on the **re-mint** path | RED | stayed green — my mutation hit only the `ON CONFLICT` branch, which no test exercises (FINDING 11) |
| V6b | skew `minted_at` **column default** (application-clock proxy) | RED | **RED** — `minted_at is 10m0.0032s from the database clock; it must be stamped by now()` |
| V7 | **loosen `credentials_password_is_argon2id` to `LIKE '%'`** | RED | **STAYED GREEN → FINDING 5** |
| V7b | tighten `credentials_secret_bounded` to 1..50 octets | RED | **RED** |
| V8 | **map 23514 → 500** (B-3) | RED | **RED** (`TestClaimErrorMapping`, `TestNoClaimErrorMapsToAnUnhandledFiveHundred`) |
| V9 | remove the `23505`/`users_one_owner` branch from `mapClaimError` | RED | stayed green — both branches answer 409/`conflict` (FINDING 10) |
| V10 | **remove the server-wide `requireClaimedMiddleware`** (guard becomes opt-in) | RED | **RED** |
| V11 | **examine the token BEFORE the claimed check** (claimed instance becomes a token oracle) | RED | **RED** |

`add a route with no allowlist decision` (S-4/B-R9 route walk) is the builder's
MUT-12, reproduced RED above.

## 6. B-3 boundary fuzz — no input the schema accepts yields a 5xx

19 cases driven through the real handler. **Zero 5xx.**

```
email-254-chars-non-ascii            -> 400 bad_request      (487 octets; byte bound, not a 23514)
email-300-bytes                      -> 400 bad_request
email-exactly-254-bytes              -> 201
email-255-bytes                      -> 409 conflict
email-minimum-3-bytes                -> 400 bad_request
username-2-chars / 31-chars          -> 400 / 400
username-3-chars / 30-chars          -> accepted shape
username-leading-hyphen              -> 400 bad_request
username-non-ascii                   -> 400 bad_request
password-11-runes                    -> 400 bad_request
password-256-astral-runes (1024 B)   -> accepted shape
password-257-astral-runes            -> 400 bad_request
empty-everything                     -> 403 forbidden        (token shape first, single message)
token-63-hex / 65-hex                -> 403 / 403            (same message as a wrong token)
token-uppercase-valid                -> accepted (Normalize lowercases)
```

The 1024-byte password cap: `MaxPasswordRunes = 256`, `MaxPasswordBytes = 1024`,
both compared with strict `>`; 256 × `utf8.UTFMax` (4) = exactly 1024, so a
256-rune string is at most 1024 bytes and the byte branch in `Validate` can never
reject. **The arithmetic checks out and the docs say exactly that**
(`internal/ownerclaim/ownerclaim_test.go:146-171`: *"the byte check inside Validate
is unreachable through this path … This test asserts the implication rather than
pretending to exercise a branch it cannot reach"*). Documented, not faked. One
weakness: that guard compares **mirrored literals** (`credentialMaxRunes = 256`
at `ownerclaim_test.go:21`) rather than `credential.MaxPasswordRunes`, so raising
the real constant would not trip it (FINDING 12).

## 7. The two readings the builder flagged

**Content-Type.** The ruling says "exactly `application/json` (415)". Measured, all
12 forms through the real handler:

| Content-Type | result |
|---|---|
| `application/json` | accepted |
| `application/json; charset=utf-8` | **accepted** |
| `APPLICATION/JSON` | **accepted** |
| `Application/Json; Charset=UTF-8` | **accepted** |
| `application/json, text/plain` | 415 |
| `application/jsonx` | 415 |
| `application/json+x` | 415 |
| `text/plain` | 415 |
| `application/x-www-form-urlencoded` | 415 |
| `multipart/form-data; boundary=x` | 415 |
| `application/json; boundary=x; type=text/html` (parameter smuggling) | 415 |
| absent | 415 |

So `charset=utf-8` is **not** the only extra form accepted: the match is
`mime.ParseMediaType` + case-insensitive type/subtype comparison, i.e. any
parameter set `ParseMediaType` accepts. That is the standards-correct reading of
a media type and the handler comment says so (`setup.go:303-304`). No bypass
follows — the body is still strict-decoded with `DisallowUnknownFields`, and
every non-`application/json` type is 415, including the parameter-smuggling case.
**Reported for the seats to rule on; I found no exploitable consequence.**

**`superseded_at IS NULL` in the redeem CTE.** I confirmed the builder's measurement
and its reason: `MintOwnerClaimToken` UPSERTs a new digest onto the fixed key, so
a superseded-and-replaced token no longer matches on digest and never reaches the
predicate; the only supersede-without-remint path is `Boot` on an instance that
already has accounts, where `AnyUserExists` answers 409 first. **Unreachable today,
correctly declared review-only.**

## 8. CLI and boot — driven as REAL BINARIES

`go build -o bin/vizra ./cmd/vizra`, `go build -o bin/vizra-api ./cmd/api`,
against dedicated databases `vzv8_cli` / `vzv8_b4`.

| Scenario | Observed |
|---|---|
| `vizra claim-token`, unclaimed, migrated | exit **0**. **stdout = exactly one 64-hex line and nothing else.** stderr = `Owner claim token (generation 1), valid for 1h0m0s.` + paste/re-mint guidance. **Zero JSON/structured-logger lines on either stream.** |
| `vizra claim-token`, **claimed** (S-12) | exit **1**, `this instance already has accounts, so it is already claimed. No token was minted.` Token rows afterwards: `1|1` — **generation unchanged, nothing minted** |
| `vizra claim-token`, schema behind 0005 | exit **1**, names the missing relation, no credential |
| `vizra doctor`, schema 4 | exit **1**; `FAIL schema  database at 4, this binary embeds 5: run 'vizra migrate'` and `FAIL owner claim  could not read the owner-claim state; … the schema may be behind ('vizra migrate')` |
| `vizra doctor`, unclaimed + live token | `WARN owner claim  unclaimed; a claim token is live (generation 1). 'vizra claim-token' mints a new one and invalidates it` — **names the generation, prints no secret (0 × 64-hex in the whole output)** |
| `vizra-api` boot, **unreachable database** | **process stays up**; `/healthz` 200; `/readyz` **503** with `{"name":"owner_claim","status":"degraded","detail":"the owner-claim bootstrap did not complete; run 'vizra doctor'"}`; claim-status and every other route **503** (never 403, never allow — S-4); **0 occurrences of the database password in the log** |
| `vizra-api` boot, **schema 4** | **process stays up**, `/readyz` `"status":"degraded"` with the same `owner_claim` component |
| `vizra-api` boot, migrated + unclaimed, default `announce=off` | boot line is `vizra: this instance is unclaimed. Get a claim token with: docker compose exec api vizra claim-token` — **a COMMAND, not a credential. 0 × 64-hex in the whole api log.** |

Structural unclaimed guard over the **real server**, unclaimed instance:

```
/healthz 200   /readyz 200   /version 200   /schemaz 200
/api/v1/setup/claim-status 200
/nope 403      /api/v1/anything 403      /metrics 403
POST /api/v1/setup/claim-owner -> 403 (token refusal: the route itself is reachable)
```

Exactly the four probes plus the two setup operations. **404 path and `/metrics`
are 403.**

**Two concurrent boots in `stderr` mode — see FINDING 1. Reproduced on 1 of 3 runs.**

## 9. Makefile, contract, GitGuardian, provenance

- **Makefile**: one changed line, the `openapi-verify` `-run` regex. Old and new both
  name 7 tests; the single difference is the rename
  `TestM0ContractIsTheFourProbes` → `TestPublicContractIsTheProbesPlusTheSetupOperations`
  (the old name exists at `5eb2829:internal/httpapi/openapi_contract_test.go:147` and
  nowhere at HEAD). Every one of the 31 top-level `func Test…` in
  `internal/httpapi/*_test.go` was classified: the 7 the new regex selects are a
  **strict superset** of the still-existing old set; the 24 it does not select
  were not selected at base either and all run under `make test-race`, which is in
  `make ci`. **No deselection.**
- **CI guards unedited**: `git diff 5eb2829 HEAD -- .github/ Dockerfile scripts/` is **empty**. Both guards green locally.
- **`api/openapi.yaml`**: purely additive (186 insertions, no `-` lines). Exactly two
  new operations under `/api/v1/setup/`. `ClaimOwnerResponse` is
  `required: [username, role]`, `additionalProperties: false` — **no uuid, no
  `created_at`** (ruling row 6 honoured). 409 declared. All eight declared codes on
  claim-owner are emitted by the handler and every emitted code is declared. The
  new operations reuse the pre-existing `Error` component.
  `api/search-internal.openapi.yaml` diff is **empty (byte-identical)**.
- **Bounds**: spec `maxLength: 254` on `email` counts characters; the DDL counts
  octets. `ownerclaim.go:76,142` closes it with `len()` (bytes) against the same
  literal `254`, and `TestValidatorsMatchTheMigration` reads the frozen migration's
  bytes. Confirmed by my fuzz table above.
- **GitGuardian**: green on this SHA (`No secrets detected ✅`). PR is **exactly one
  commit**. No credential-shaped literal is **added** by this diff (the only 64-hex
  additions are the two migration digests in `manifest.sha256`); the argon2id PHC
  and test passphrase fixtures are assembled at runtime
  (`credential_test.go:171`, `owner_claim_test.go` `testPassphrase`/`fakeVerifier`).
- **Provenance**: `ci-required` ran on head_sha `32b616dc…` and the branch has not
  moved (re-checked at the end of this run: still `32b616dc…`).

---

# Findings

FINDING 1: two concurrent boots in `stderr` mode both mint, and one announced token is already dead
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/ownerclaim/announce.go:74-100, internal/ownerclaim/ownerclaim.go:184-234
  requirements: VZ-INSTALL-003

Observed:
  The chair's ruling row 2 states: "N replicas: under the advisory lock the
  first mints, the rest find a live token and print the command only."
  `Boot` reads liveness OUTSIDE the lock — `state, err := State(ctx, q)`
  (announce.go:74), `if state.Live { announceCommand… }` (announce.go:83) —
  and then calls `Mint`, which takes `pg_advisory_xact_lock(1)` and
  UNCONDITIONALLY supersedes and mints (ownerclaim.go:191-219). There is no
  liveness re-check inside the lock.
  Reproduced with my probe `TestVZV_TwoConcurrentBootsInStderrMode`, 1 of 3 runs:
    boot A: minted=true generation=2
    boot B: minted=true generation=1
    boots that MINTED: 2 (the ruling wants 1)
    tokens announced to operators: 2
      announced token …5e6d3fe8 is currently redeemable: true
      announced token …8293b466 is currently redeemable: false
  No test in the repository covers concurrent boots; `grep -rniE
  'concurrent.*boot|two boots|replica'` over internal/ and cmd/ finds nothing
  for ownerclaim.

Failure:
  With two or more api replicas and `VIZRA_OWNER_CLAIM_ANNOUNCE=stderr`, the
  operator's log contains two 64-hex credentials. One is already superseded.
  Picking the wrong one returns the deliberately uninformative "that claim
  token was not accepted" (ownerclaim.go:411), which by design tells them
  nothing — so the operator cannot diagnose it, and the extra dead credential
  is a second secret written to a shipped, retained log for no benefit.

Perspective:
  operator

Recommendation:
  Move the liveness decision inside the lock: have `Mint` take a
  `onlyIfNoLiveToken bool` (or add a `MintIfAbsent`) that re-reads
  `GetOwnerClaimToken` after `pg_advisory_xact_lock` and returns a sentinel
  when a live token already exists; `Boot` then calls `announceCommand` on
  that sentinel. `vizra claim-token` keeps passing the always-supersede path.

Acceptance criteria:
  With N concurrent `Boot(mode=stderr)` calls against one unclaimed database:
  exactly one returns `Minted: true`; every other writes only the command
  line; every 64-hex value that appears in any boot output is redeemable at
  the end of the run; `owner_claim_tokens` holds exactly one row.

Tests:
  `internal/integration`, a new `TestConcurrentBootsMintExactlyOneToken` in the
  idiom of my probe: two goroutines calling `ownerclaim.Boot` with separate
  `io.Writer`s, then extract every 64-hex token from the combined output and
  assert each one is live. Harness exists; no change needed.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  Only one token is ever live, no second owner is possible, and the default
  announce mode is `off`, so this needs a multi-replica deployment that has
  also opted into the mode the docs warn against. One could argue the ruling's
  N-replica sentence was descriptive rather than binding. Against that: the
  ruling adopted the security seat's S-3 "denial-of-claim" finding precisely to
  stop a boot silently invalidating a token an operator is holding, and this is
  that failure, one restart later.

FINDING 2: `vizra claim-token` has NO test coverage; S-12's refusal is unobserved
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     cmd/vizra/claimtoken.go:28-71, internal/integration/owner_claim_test.go:779-792
  requirements: VZ-INSTALL-003 (surfaces.cli, OQ-9)

Observed:
  `grep -rn runClaimToken` finds only its definition and the dispatch in
  cmd/vizra/main.go:51. Nothing calls it from a test.
  `TestClaimTokenCLIRefusesOnAClaimedInstance` (owner_claim_test.go:779) is
  named for the CLI but calls the LIBRARY: `ownerclaim.Mint(t.Context(),
  e.pool, e.cfg.OwnerClaimTTL, true)`. It never constructs the command.
  My mutation V3 changed `ownerclaim.Mint(ctx, pools.Default(),
  cfg.OwnerClaimTTL, true)` to `…, false)` in cmd/vizra/claimtoken.go — i.e.
  made the CLI mint on a claimed instance, exactly the escalation path S-12
  forbids — and the whole integration suite **stayed green**.
  The repo already has the real-binary idiom from PR #7:
  internal/integration/healthcheck_test.go:69 builds binaries with `go build
  -o` and :192 runs `exec.Command(filepath.Join(binaries(t), "vizra"), …)`.
  This slice does not use it, for the CLI or for `cmd/api`'s boot wiring.

Failure:
  The stdout/stderr split (the whole privacy argument for the CLI over a boot
  line), the generation naming, the refusal message and the non-zero exit are
  all untested. A future edit that logs the token through the structured
  logger, prints it on stdout together with the prose, or drops the
  claimed-instance refusal would ship green. Driving the real binary myself I
  confirmed all four behaviours are currently CORRECT — the defect is the
  absence of a control, not the behaviour.

Perspective:
  operator, developer

Recommendation:
  One integration test that builds `cmd/vizra` with the existing
  `binaries(t)` helper and runs `vizra claim-token` twice: once on an
  unclaimed migrated database (exit 0; stdout matches `^[0-9a-f]{64}\n$`
  exactly; stderr contains "generation"; neither stream contains a `{` JSON
  line) and once after inserting a user (exit non-zero; no new token row;
  `owner_claim_tokens.generation` unchanged).

Acceptance criteria:
  Flipping `refuseIfUsersExist` to `false` in cmd/vizra/claimtoken.go turns a
  named test red. Printing the token to stderr instead of stdout turns a named
  test red.

Tests:
  `internal/integration`, `TestClaimTokenCLIOnTheRealBinary`. Harness exists
  (`binaries(t)`, healthcheck_test.go:60-80); no harness change needed.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  The library function it delegates to IS tested, and the CLI is a thin
  wrapper. Against that: everything S-12 and the privacy case actually turn on
  — which stream the credential goes to, and that the command refuses — lives
  in the wrapper, not the library, and the PR's own README and AGENTS.md make
  claims about exactly those lines.

FINDING 3: AGENTS.md states "a rate-limited claim writes no audit row"; a 429 does write one
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md:173, internal/httpapi/setup.go:424-425, internal/httpapi/setup_limits.go:148-161, internal/integration/owner_claim_test.go:1152-1171
  requirements: VZ-INSTALL-003 (S-5 / B-6)

Observed:
  AGENTS.md:173 (added by this PR): "| A rate-limited claim writes no audit
  row, so an anonymous flood is not an unbounded writer into an undeletable
  table | `TestARateLimitedClaimWritesNoAuditRow` |"
  setup.go:424-425, inside the 429 branch:
    `if s.claimLimitTransition(c) { s.recordClaimRateLimited(c, "failure") }`
  which emits a `rate_limited` row (setup_limits.go:148-161).
  The cited test asserts only `if rateRows > 1` — it PERMITS the row.
  The source comment (setup.go:420-423) states the truth correctly: "Exactly
  one `rate_limited` row is written, on the transition into the limited state."
  The PR body repeats the unqualified form: "A 429 writes no audit row."

Failure:
  The repository's invariant table — the document a reviewer consults to learn
  what is guaranteed — is stronger than the control and stronger than the test
  named as its evidence. The design is right and deliberate; the sentence
  describing it is false. This is the class the chair has held eight PRs for.

Perspective:
  developer

Recommendation:
  Rewrite the row as: "A rate-limited claim writes no `refused` audit row;
  exactly one `rate_limited` row is written per bucket per window, on the
  transition." Rename the test to `TestARateLimitedClaimWritesAtMostOneAuditRow`
  and make the same correction in the PR body.

Acceptance criteria:
  No sentence in AGENTS.md or the PR body asserts that a 429 writes zero audit
  rows. The test name describes what the test asserts.

Tests:
  Existing `TestARateLimitedClaimWritesNoAuditRow` already asserts the true
  property; only the name and the prose need to move.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  "No audit row" could be read as shorthand for "no row per request". It is
  not qualified that way, it sits in a table of invariants, and the test it
  cites was written to permit the row — so the shorthand reading is the one a
  future author would rely on and be wrong about.

FINDING 4: AGENTS.md states the claim token "never reaches … a log line"; this PR ships a mode that prints it to the log
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md:171, internal/ownerclaim/announce.go:92-99, cmd/api/main.go:126-127, .env.example:93
  requirements: VZ-INSTALL-003 (privacy case)

Observed:
  AGENTS.md:171 (added by this PR): "| The owner-claim token is stored only as
  a SHA-256 digest and **never reaches a response, a header or a log line** |
  `TestClaimTokenIsStoredOnlyAsASHA256Digest`,
  `TestOwnerClaimTokenNeverReachesTheStructuredLogOrAResponse` |"
  With `VIZRA_OWNER_CLAIM_ANNOUNCE=stderr` the raw token IS printed to the api
  process's stderr at boot: announce.go:92-99 `fmt.Fprintf(w, "… %s …", …, raw)`
  wired to `os.Stderr` at cmd/api/main.go:126-127. The PR's own .env.example
  says that mode "WRITES A LIVE CREDENTIAL to the container log, which every
  log driver captures, ships and retains."
  Both cited tests exercise only the HTTP path under the default config; I
  confirmed by running the real binary in `stderr` mode that the token appears
  in the process's captured output.

Failure:
  The unqualified "never" in the invariant table is contradicted by a mode this
  same commit adds, on the flagship privacy property of the slice. A reader of
  AGENTS.md would conclude no configuration can put the token in a log; one
  environment variable does.

Perspective:
  operator, developer

Recommendation:
  Qualify the row: "…never reaches a response, a header, or the structured
  logger; the only path that prints it is the opt-in
  `VIZRA_OWNER_CLAIM_ANNOUNCE=stderr` boot line, whose own template text says
  so."

Acceptance criteria:
  The AGENTS.md row names the one path that prints the token. No unqualified
  "never" about log lines survives.

Tests:
  `TestBootMintsOnlyUnderTheStderrOptIn` already asserts the default prints no
  64-hex value and the opt-in does; it is the evidence for the corrected
  sentence.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  "Log line" might be read as "structured log line", which is what the cited
  tests check and what the source comments carefully say. But the row itself
  draws no such distinction, and `docker compose logs` does not either — which
  is precisely the threat model the announce default was set to `off` for.

FINDING 5: the `credentials_password_is_argon2id` CHECK has no negative test
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0005_users_credentials_owner_claim.up.sql:116-118, internal/credential/credential_test.go:38
  requirements: VZ-INSTALL-003 (chair ruling row 5)

Observed:
  Ruling row 5 defines the CHECK's job as "never plaintext, never another
  scheme". The only assertion about it in the suite is POSITIVE:
  credential_test.go:38 `if !strings.HasPrefix(phc, "$argon2id$") { … }` —
  i.e. "what we write would be accepted".
  My mutation V7 loosened the constraint to
  `kind <> 'password' OR secret LIKE '%'` — accepting plaintext and every other
  scheme — and the integration suite **stayed green**.
  The control itself is correct; I verified it directly against the live table:
  `'hunter2plaintext'`, `'$2y$10$bcryptstyle'` and `'$scrypt$x'` are each
  refused with `violates check constraint "credentials_password_is_argon2id"`.

Failure:
  The migration freezes on merge. If a later slice widens this CHECK (adding
  'totp' is anticipated in the header) and gets the predicate wrong, nothing
  turns red. The one database fact standing between the product and a
  plaintext password column is untested in the direction that matters.

Perspective:
  developer, instance-admin

Recommendation:
  Three lines in the existing integration file: insert a credential with a
  plaintext secret, a bcrypt-shaped secret and a 1025-octet secret, and assert
  each raises 23514 naming the expected constraint.

Acceptance criteria:
  Loosening `credentials_password_is_argon2id` to `LIKE '%'` turns a named
  test red. Widening `credentials_secret_bounded` past 1024 turns a named test red.

Tests:
  `internal/integration`, `TestTheCredentialsCheckRefusesAnythingButArgon2id`,
  beside the existing `TestASecondPasswordCredentialForOneUserIsRefused`
  (owner_claim_test.go:468) which already inserts through the same path.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  The application only ever writes `credential.Encode` output, which is tested
  to match the frozen argon2id grammar, so the CHECK is redundant today. That
  is exactly the argument for testing it: its whole purpose is the writer that
  does not exist yet, and after merge the DDL cannot be corrected in place.

FINDING 6: the PR body drops the "by the failure limiter" qualifier the code comment insists on
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     PR #8 body, internal/httpapi/setup.go:34-40, internal/httpapi/setup_limits.go:59-72
  requirements: VZ-INSTALL-003 (S-7)

Observed:
  PR body: "Rate limiting counts failures, not attempts (S-7), so a stranger
  cannot flood the endpoint until the operator's correct token is answered 429."
  setup.go:226 applies `allowClaimRequest` — the `claimHardCeiling = 600` per
  15-minute window — as the FIRST statement in `handleClaimOwner`, before the
  media-type check. setup_limits.go:62-63 says so verbatim: "Unlike the failure
  budget, this one **can refuse a request carrying a valid token** — a fact
  stated rather than hidden."
  AGENTS.md:174 and the test name are correctly narrowed ("by the failure
  limiter"); only the PR body drops it. The cited test sends 40 attempts,
  far below 600, so it cannot detect the difference.

Failure:
  The PR body claims an absolute property the code deliberately does not have
  and documents that it does not have. A reader reconciling the PR body with
  the source finds the source more honest than the summary.

Perspective:
  operator, developer

Recommendation:
  Add four words: "…is answered 429 **by the failure limiter**", and name the
  hard ceiling (600 requests / 15 min) as the one limiter that can.

Acceptance criteria:
  No sentence in the PR body asserts that a valid token can never be 429ed.

Tests:
  None needed; the existing comment and AGENTS.md row are already correct.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  600 requests in 15 minutes from a single unauthenticated origin is far beyond
  plausible operator use, so the case is theoretical. It is still an unqualified
  "cannot" over a control that can.

FINDING 7: the mutation transcript justifies a review-only declaration by citing MUT-17, which does not exist
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     docs/evidence/m1a-owner-claim/demonstrate.sh:259-260, docs/evidence/m1a-owner-claim/02-mutations.txt:506-507
  requirements: VZ-INSTALL-003 (S-15 + the backend seat's invariant table)

Observed:
  Justifying MUT-1b as review-only, the transcript says: "The index is proven
  by MUT-2b and **the mapper by MUT-17**; the row guard's own contribution is
  redundancy."
  `grep -oE 'run_case (MUT-[0-9a-z]+)' demonstrate.sh` yields exactly 23 ids —
  MUT-1, 2, 2b, 16, 3, 6, 14, 5b, 9, 9b, 19, 11b, 10, 10b, 24, 13, 18, 8, 25,
  26, 15, 12, 27. **MUT-17 is not among them**, and `grep -rn "MUT-17"` over
  the whole repository returns only these two self-references.

Failure:
  A reader auditing whether the review-only declaration is honest is pointed at
  a demonstration that was never run. The transcript's own strength — "the
  harness refuses to score a mutation that did not apply" — is undermined by a
  citation to a mutation that does not exist.

Perspective:
  developer

Recommendation:
  Either add the case (mutating the 23505 mapper branch) or cite the control
  that actually exists: `TestClaimErrorMapping` /
  `TestNoClaimErrorMapsToAnUnhandledFiveHundred` in internal/httpapi/setup_test.go.
  I verified the underlying claim holds — my mutation V8 (map 23514 to 500)
  turns both of those red.

Acceptance criteria:
  Every MUT-n referenced in `02-mutations.txt` appears as a `run_case` in
  `demonstrate.sh` and has a RESULT line in the transcript.

Tests:
  n/a — evidence-document correction.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  The conclusion the citation supports is true and independently verified, so
  nothing technical is wrong. But an evidence file whose cross-references do
  not resolve is exactly the kind of artefact that stops being checkable.

FINDING 8: `claimHardCeiling` is documented as covering "the setup routes"; it covers one of them
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:35-40, internal/httpapi/setup_limits.go:59-60, internal/httpapi/setup.go:192-200
  requirements: VZ-INSTALL-003 (S-7)

Observed:
  setup.go:35-38: "claimHardCeiling bounds TOTAL requests to the setup routes,
  not just failures, **so a flood of one-row SELECTs cannot exhaust the pool.**"
  setup_limits.go:59-60: "allowClaimRequest applies the hard ceiling to **EVERY
  request to the setup routes**."
  `grep -rn allowClaimRequest` finds exactly one call site: setup.go:226, in
  `handleClaimOwner`. `handleClaimStatus` (setup.go:192-200) does not call it —
  and it is the unauthenticated one-row-SELECT endpoint the comment names as
  the threat.

Failure:
  The pool-exhaustion argument is written against `claim-status` and applied to
  `claim-owner`. An anonymous caller can drive `GET /api/v1/setup/claim-status`
  without any ceiling; each call runs `lookupClaimed` against the pool while the
  instance is unclaimed (the negative cache TTL is 1s, so at most ~1 query/s per
  process, which bounds it in practice — but not by the mechanism the comment
  credits).

Perspective:
  operator

Recommendation:
  Either apply `allowClaimRequest` to `handleClaimStatus` too, or narrow both
  comments to say the ceiling covers `claim-owner` and that `claim-status` is
  bounded by the 1-second negative cache instead.

Acceptance criteria:
  No comment claims a control over a route that does not have it.

Tests:
  If the ceiling is extended, `api/openapi.yaml` must gain a 429 response on
  `getSetupClaimStatus` and the contract test will enforce it.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  `claimedNegativeTTL = 1s` already bounds database work from this route to one
  query per second per process, so there is no real exhaustion path. The finding
  is about the comment, not the risk.

FINDING 9: `TestOwnerInsertConflictMapsTo409NotFiveHundred` does not reach the branch it is named for
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/integration/owner_claim_test.go:1238-1265, internal/ownerclaim/ownerclaim.go:309-315
  requirements: VZ-INSTALL-003 (B-R4 / S-9)

Observed:
  Ruling B-R4/S-9 required "an integration test forces `users_one_owner` to fire
  through the handler (owner inserted out of band, then a valid token)".
  The test inserts a COMMITTED owner (`insertOwner`, :1249) and then claims. In
  `Claim`, `q.AnyUserExists` (ownerclaim.go:309) sees that row and returns
  `ErrAlreadyClaimed` at :314 — the request never reaches `ClaimOwner`, so
  `users_one_owner` never fires. The test's own comment claims otherwise:
  "Instead assert the mapper directly against the real constraint by inserting
  an owner and claiming with a valid token."
  I forced the branch deterministically with an UNCOMMITTED concurrent insert
  (probe `TestVZV_UsersOneOwnerFiresThroughTheHandler`): HTTP 409, code
  `conflict`, users=1, credentials=0, consumed tokens=0. **The substance the
  ruling wanted is true**; the test that claims to show it does not.

Failure:
  A reviewer reading the test believes the 23505/`users_one_owner` mapper branch
  is exercised end-to-end. It is not; only the already-claimed path is.

Perspective:
  developer

Recommendation:
  Either correct the comment to say it asserts the already-claimed path, or
  replace the body with the uncommitted-insert technique above (deterministic,
  ~1.5 s).

Acceptance criteria:
  The test's name and comment match the code path it drives.

Tests:
  `internal/integration`, reusing the probe shape in this evidence file.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  `TestClaimErrorMapping` covers the mapper over a synthetic
  `*pgconn.PgError{Code:"23505", ConstraintName:"users_one_owner"}`, and
  `TestOwnerIndexNameMatchesTheMapper` pins the name from the live database, so
  the pair is arguably equivalent. The ruling nonetheless asked for it through
  the handler, and the test's comment asserts it does that.

FINDING 10: removing the `users_one_owner` mapper branch turns no test red, and is not declared review-only
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/setup.go:371-377, internal/httpapi/setup_test.go:131-158
  requirements: VZ-INSTALL-003 (S-15)

Observed:
  Mutation V9 deleted the `case pgErr.Code == "23505" && pgErr.ConstraintName
  == "users_one_owner"` branch; `go test -run
  'TestClaimErrorMapping|TestNoClaimErrorMapsToAnUnhandledFiveHundred'
  ./internal/httpapi/` stayed GREEN. The fall-through `case pgErr.Code ==
  "23505"` answers 409/`conflict` too, and the test asserts only status and
  code name — not the message, which changes from "this instance already has
  an owner" to "that username or email address is already taken".
  S-15 requires every listed invariant to have "a named test and a mutation
  that turns it red, **or** be recorded beside MUT-4 as review-only". This one
  is neither.

Failure:
  Nothing breaks (both branches give 409), but the honest mutation matrix the
  ruling asked for has an undeclared hole, and the operator-facing message for
  the two-owners case is unpinned.

Perspective:
  developer

Recommendation:
  Add `wantMessage` to `TestClaimErrorMapping`'s table, or record the property
  beside MUT-4/MUT-1b as review-only with the same MEASURED note.

Acceptance criteria:
  Either deleting the branch turns a named test red, or `02-mutations.txt`
  lists it as measured-green with the reason.

Tests:
  `internal/httpapi`, extend `TestClaimErrorMapping`.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  It is genuinely defence in depth, the same category the builder handled
  honestly for MUT-1b and MUT-1c — which is the argument for listing it there
  rather than for adding a test.

FINDING 11: `TestMintTimestampsComeFromTheDatabaseClock` never exercises the re-mint path
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/integration/owner_claim_test.go:1270-1292, store/queries/owner_claim.sql:40-46
  requirements: VZ-INSTALL-003 (ADR-004)

Observed:
  The test calls `e.mint(t)` once on a fresh database, which takes the INSERT
  branch; `minted_at` there comes from the COLUMN DEFAULT, not from the
  `ON CONFLICT DO UPDATE SET minted_at = now()` at owner_claim.sql:43.
  Mutation V6 skewed only the ON CONFLICT branch by 10 minutes: suite stayed
  GREEN. V6b skewed the column default instead and the test went RED
  ("minted_at is 10m0.0032s from the database clock"), confirming the test is
  real but covers only one of the two write paths.

Failure:
  A re-mint (the `vizra claim-token` path, which is the PRIMARY path by ruling
  row 2) could start stamping `minted_at` from anywhere without a test
  noticing, and `owner_claim_tokens_ttl CHECK (expires_at > minted_at)` is the
  only thing that would eventually complain.

Perspective:
  developer

Recommendation:
  Call `e.mint(t)` twice in that test and assert the database-clock property on
  the second (generation 2) row as well.

Acceptance criteria:
  Skewing `minted_at` in the `ON CONFLICT` branch turns a named test red.

Tests:
  `internal/integration`, existing test, two extra lines.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  Both branches use the same `now()` literal, so drift between them is
  implausible. Cheap to close regardless.

FINDING 12: three smaller precision defects in prose and one weakened drift guard
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md:170, migrations/0005_users_credentials_owner_claim.up.sql:183-185, internal/ownerclaim/ownerclaim_test.go:21-23, docs/evidence/m1a-owner-claim/README.md
  requirements: VZ-INSTALL-003

Observed:
  (a) AGENTS.md:170 — "a route in neither classification set **fails the build**".
      setup_test.go:42-45 calls `t.Errorf`; the package compiles, the
      `test-race` lane goes red. The source comment (setup.go:113-117) says
      "fails the test" and is correct.
  (b) migration header :183-185 — "Verified before adding this: **no TRUNCATE
      appears in any Go, SQL or shell source in this repository**". The same
      commit adds `TRUNCATE audit_events` at owner_claim_test.go:568 (to assert
      the refusal). The load-bearing conclusion — the harness resets with
      `DROP SCHEMA public CASCADE` (golden_test.go:91) — still holds.
  (c) ownerclaim_test.go:21-23 defines `credentialMaxRunes = 256` and
      `credentialMaxBytes = 1024` as MIRRORED literals, so the guard at :157
      compares mirrors, not `credential.MaxPasswordRunes` /
      `MaxPasswordBytes`. Raising the real constant to 512 without touching the
      mirror leaves the guard green while its own failure message
      ("the rune cap no longer implies the byte cap") becomes true.
  (d) docs/evidence/m1a-owner-claim/README.md says "**Three** properties have no
      mutation…" then describes four (MUT-4, MUT-4b, MUT-1c, MUT-1b) and refers
      to "**both** of which are measured".

Failure:
  Individually trivial; collectively they are the class of imprecision this
  repository's contract is written against.

Perspective:
  developer

Recommendation:
  (a) "fails the `test-race` lane"; (b) narrow to "no TRUNCATE of
  `audit_events` exists in any production path"; (c)
  `credentialMaxRunes = credential.MaxPasswordRunes` and likewise for bytes;
  (d) "Four properties" / "each of which is measured".

Acceptance criteria:
  Each sentence is true as written.

Tests:
  (c) is the only one with a test consequence and is a one-line change.

Cross-repo implications:
  core: as above | user: none | search: none | meta: none

Challenge:
  All four are text; none affects behaviour. They are listed because the chair
  has held PRs for exactly this and because (c) silently weakens a guard.

---

## What I could not fault

For the record, so the seats do not re-derive it: the race is decided by the
database in both directions and I could not make it produce two owners, a 5xx,
an orphan credential or a double-consumed token under any of the three server
isolation defaults; the token is never stored raw and never appears in a
response, a header or the structured logger; zero argon2id derivations occur on
any non-201 path; the unclaimed guard is genuinely structural over the real
server including the 404 path and `/metrics`; every one of the builder's 23
mutations reproduces with a byte-identical restore; the ip_prefix writer is
total against the frozen 0003 grammar and returns NULL for loopback and for a
forwarded header with no trusted-proxy configuration; boot never crash-loops and
readiness names the degraded component; migration 0005 round-trips cleanly and
freezes a schema I could not find a correctness defect in.

## Verdict

CI is green on this SHA with a matching manifest, every lane I ran passed with
zero skips, all 23 builder mutations reproduced, and the central security
properties hold under my own adversarial probes. The PR nonetheless carries one
ruling requirement that is not implemented and not tested (FINDING 1), one
command-line surface with no test at all whose S-12 refusal a mutation shows is
unobserved (FINDING 2), and two invariant-table sentences stronger than their
controls, one of them contradicted by a mode this same commit ships
(FINDINGS 3 and 4). Under the AGENTS.md rule that assurances must not exceed
their controls, and given that migration 0005 freezes on merge, these are
REQUIRED rather than advisory.

FINAL VERDICT: FAIL — SHA 32b616dcd6d9ed3ea8d05020e1d66dae25c0e8ed
