# ADR-003: Identity, sessions, CSRF, authorization

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` requires default-deny authorization over originals, derivatives,
search, counts, exports, embeds, feeds, federation and caches, and forbids
trusting browser-only role checks. `docs/PRODUCT_SPEC.md` §5 makes every read
surface enforce one decision, and Q-039 requires the precedence order and the
surface × visibility matrix written before code. Every later slice depends on
these three mechanisms.

## Decision
**Sessions.** Unlike Vidra's JWT access token plus rotating refresh token and
optional cookie, Vizra uses opaque server-side sessions. The cookie is
`__Host-vizra_session`, `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`; the id is
256 bits of randomness and only its SHA-256 is stored in a `sessions` table in
PostgreSQL, never in the cache. Expiry rolls over 30 days with a 180-day absolute
cap. Users see a per-device session list and can revoke one device or all, and
`revoked_reason` is recorded. Every authenticated request re-reads session ⋈ user
(role, disabled, tombstoned) with no in-process cache, because replicas cannot
invalidate each other. A database outage returns 503, never 401. There is no JWT:
the per-request database read is required anyway, and a JWT would add a second
credential and a signing key for nothing.

**API keys.** Programmatic clients use API keys (Q-033): `vzk_` plus 256 bits of
randomness, shown once, stored as SHA-256, with scopes `upload`, `read`, `manage`,
per-key and per-user rate limits, `last_used`, revocation and optional expiry.
They are presented as `Authorization: Bearer`. The Chevereto-compatible `key`
parameter on the API v1 upload endpoint resolves against the same store
(VZ-UPLOAD-010).

**CSRF.** Cookie sessions are defended by `SameSite=Lax` plus a same-origin check
on every state-changing request, and there is no double-submit token.

| Request class | Credential | Required header/check | Result |
|---|---|---|---|
| GET/HEAD/OPTIONS | session cookie or bearer | none | allow (authorization still applies) |
| State-changing JSON | session cookie, `Origin` present | `Origin` equals the configured public origin **and** `Content-Type: application/json` | allow |
| State-changing JSON | session cookie, `Origin` present but different | — | deny 403 |
| State-changing JSON | session cookie, no `Origin` | `Sec-Fetch-Site` is `same-origin` or `none` **and** `Content-Type: application/json` | allow |
| State-changing JSON | session cookie, no `Origin`, no `Sec-Fetch-Site` | — | deny 403 |
| Multipart upload (chunk, finalize) | session cookie | the origin check above **and** `X-Vizra-Upload: 1` | allow |
| Any state-changing | API key as `Authorization: Bearer` | none — no ambient credential exists | allow (scope and authorization apply) |
| API v1 upload with `key` parameter | API key in the request | none | allow (VZ-UPLOAD-010) |
| Setup wizard | none (pre-claim) | loopback bind **and** one-time `X-Setup-Token` **and** Host allowlist | allow |

OAuth and AT Protocol login state rides in HMAC-sealed state cookies.

**Credentials.** Passwords use argon2id from `golang.org/x/crypto` with the OWASP
parameters pinned here: memory **19 MiB (19456 KiB)**, iterations **2**,
parallelism **1**, a **16-byte** random salt and a **32-byte** tag. The stored hash
string is the standard encoding prefixed `$argon2id$v=19$…` and carries a Vizra
version tag, so parameters can be raised later and old hashes re-derived on next
sign-in without a second column.
TOTP secrets are envelope-encrypted under `MFA_KEY_KEK` with a re-wrap job on
rotation. Step-up tokens are single-use database rows, not tokens. Owner claim
copies Vidra: a 256-bit token minted at boot, printed once, only its hash stored,
every sign-up path refusing until it is redeemed, and redemption atomic and
exactly once.

**Rate limits.** Counters live in Valkey; if Valkey is unreachable the api falls
back to a per-process in-memory limiter and marks readiness degraded.

**SSR identity.** `vizra-user` has exactly two fetch helpers: `publicFetch`, which
is anonymous by construction, cacheable and keyed on visibility-versioned URLs,
and `viewerFetch`, which forwards the session cookie, always sets
`cache: 'no-store'` and is never called inside a revalidated cache. A lint rule
forbids identity headers in revalidated fetches.

**Authorization.** One evaluator package, `internal/authz`, exposes

```go
func (e *Evaluator) Decide(ctx context.Context, subject Subject, action Action, resource Resource) (Decision, Reason)
```

It is default-deny and is called by every read surface: the API, derivative and
original serving, counts, search hydration, feeds, embeds and exports. Resources
carry visibility, owner, album privacy and share grants — and audiences in the
full profile. Roles are an ordered enum on `users.role`: owner > admin >
manager > member > guest, exactly the set VZ-AUTH-004 and `docs/PRODUCT_SPEC.md`
define (manager = content management without settings; owner is single and
cannot be demoted; "moderator" is not a role label), with `user_groups`
(Chevereto parity, M2+) as an additive permission set. Private resources return
404 to non-viewers, hiding existence. The Q-039 surface × visibility matrix is a
table-driven test inside this package; the matrix itself — viewer classes,
precedence order and every surface row — is frozen in
`docs/adr/ADR-007-domain-model-assets-albums-privacy-social-site.md`
§ "Frozen surface × visibility matrix", which is that test's fixture. Sessions, API keys and authorization
decisions are audit-evented.

## Consequences
Positive: one credential type per client class, one revocation point, and one
place a reviewer reads to learn what a role may do; revocation, disablement and
role change bite within one request. Negative: one indexed session read per
authenticated request, and the surface × visibility matrix must be extended
whenever a surface is added. Risks: a new read surface that forgets
`authz.Decide` fails open, so the matrix test is an exhaustive enumeration with
DENY for anything absent; an unset `MFA_KEY_KEK` must be a boot refusal, never a
warning. Later milestones must not break: the single evaluator, 404-for-private,
default deny for an unlisted surface, no in-process session cache, bearer requests
never gaining ambient-credential behaviour, and `publicFetch` never learning
identity.

## Precedent
Copied from Vidra (survey citations): session-bound credentials with the role
re-read per request and no in-process cache
(`C/internal/auth/sessionauth.go:29-35,42-76`), the 503-not-401 rule
(`C/internal/httpapi/auth_middleware.go:49-63`), SHA-256-only token storage
(`C/internal/auth/refresh.go:16,29`), HMAC-sealed state cookies with
constant-time compare (`C/internal/httpapi/statecookie.go:44,60,80,88-103`), the
setup-wizard triad of loopback bind, one-time `X-Setup-Token` and Host allowlist
(`C/internal/setupweb/guard.go:16-58`), owner claim
(`C/internal/auth/ownerclaim.go:19-48`), envelope-encrypted TOTP secrets
(`C/internal/auth/mfa.go:21-30`), single-use step-up rows
(`C/migrations/0144_step_up_tokens.up.sql:13-26`), cache-backed rate limiting
(`C/internal/ratelimit/redis.go`), and anonymous-by-construction SSR reads with
the ban on per-request headers in revalidated fetches
(`U/lib/server-json.ts:50-56,74-79`).

Unlike Vidra: Vidra's credential is a JWT access token bound to a session
(`C/internal/auth/jwt.go:20,70`) with an opt-in refresh cookie
(`C/internal/httpapi/auth_cookie.go:16-28,40`), and its CSRF defence is
`SameSite=Lax` plus path scoping plus bearer-only mutations, with no `Origin`
check anywhere in the API (survey §1). Vidra has no API keys at all — only
`bearerAuth` (`C/api/openapi.yaml:15993`) with bespoke HMAC for service calls
(`C/internal/searchclient/client.go:188`); no per-device session list, only
logout-all (`C/api/openapi.yaml:738`); a three-value role CHECK enum with no
groups (`C/migrations/0002_users_sessions.up.sql:12`); per-resource authorization
as three hand-written helpers and a per-handler default-deny convention
(`C/internal/httpapi/channel_members.go:23,33,39`, `comments.go:370`); and KEK
rotation that is destructive with no re-wrap job, where an unset MFA KEK yields
plaintext TOTP behind a log warning
(`M/docs/productionization/risks.md:122`).

## Evidence and ratification
Q-033 (API key scopes and limits), Q-039 (one evaluator, precedence, visibility
version, surface matrix, 404-for-private), Q-040 (private profiles, no
follower-only level in core) and Q-032 (VERIFIED restriction) in the
`docs/OPEN_QUESTIONS.md` ratification record. No dependency version is asserted
here; versions live in ADR-001.

## Ledger IDs
VZ-AUTH-001, VZ-AUTH-003, VZ-AUTH-004, VZ-AUTH-008, VZ-AUTH-009, VZ-INSTALL-003,
VZ-PRIVACY-001, VZ-SECURITY-003, VZ-UPLOAD-010, VZ-ADMIN-USERS-001.

## M0 obligations
M0 owns none of the identity behaviour, which lands in M1 and M2 (VZ-AUTH-001 in
M1; VZ-AUTH-003 and VZ-AUTH-008 in M2). M0 must not preclude it: an
`internal/authz` package every read surface calls, `users.role` as an ordered
enum, no package-global handles that would hide the subject, and audit events
from the first migration (ADR-007).

Reservation only: `sessions`, `api_keys`, `user_groups`, step-up and TOTP tables
are schema reservations created with their slices; the surface × visibility matrix
test is written with VZ-PRIVACY-001 in M1.

