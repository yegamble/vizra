from core import *

# ---------------------------------------------------------------- F1 identity and permissions
req("VZ-AUTH-001","Registration with email + password, sign-in, sign-out, session revocation",
    "Member: registers (when open), signs in, signs out everywhere; sessions are server-side revocable; CSRF-safe cookie sessions.",
    "identity", EXPLICIT, [{"source":"CATALOG-F1"},{"source":"CHEV-FEATURES","note":"registration with email address + password"}], edition="all",
    deps=["VZ-FOUND-003"], success=["Signup → verify (if required) → sign in → sign out; revoked session denied"], negative=["Wrong password rate-limited; enumeration-safe errors","CSRF token missing → 403"],
    privacy=["Password hash parameters documented; no email in logs"], recovery=["Session store loss forces re-login, no data loss"], api=["POST /api/v1/auth/register|login|logout","GET /api/v1/auth/sessions","DELETE /api/v1/auth/sessions/{id}"], ui=["/signup","/login","/settings/sessions"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-AUTH-002","Email verification and password recovery",
    "Member: verifies email when required; resets password via single-use expiring link; SMTP failure surfaces to admin without leaking to attacker.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"User email confirmation (Lite/Pro)"},{"source":"CHEV-USERS-SETTINGS","note":"Require email confirmation"}], edition="Lite",
    deps=["VZ-AUTH-001","VZ-EMAIL-001"], success=["Link works once; expired link rejected"], negative=["Reset for unknown email returns same response"], privacy=["Tokens hashed at rest"], api=["POST /api/v1/auth/verify","POST /api/v1/auth/password-reset"], ui=["/verify","/reset"], evidence=EV_API+EV_NEG)
req("VZ-AUTH-003","Two-factor authentication (TOTP) with recovery codes",
    "Member: enrolls TOTP, verifies at login, uses recovery codes; secrets encrypted with a KEK.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"Two-Factor Authentication (2FA); Encrypt secrets"}], edition="all",
    deps=["VZ-AUTH-001"], success=["Enroll/verify/disable; recovery code single-use"], negative=["Replay of a used code rejected within window"], privacy=["Secret sealed by KEK; rotation documented"], recovery=["Lost device → recovery codes; admin reset audited"], api=["POST /api/v1/auth/2fa/*"], ui=["/settings/security"], evidence=EV_API+EV_NEG)
req("VZ-AUTH-004","Roles: owner, admin, manager, member, guest",
    "Owner: role model with owner (single), admin, manager (content management without settings), member, guest; server-side enforcement on every route; browser-only checks never trusted.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"Roles available: admin, manager & user"},{"source":"AGENTS","note":"never trust browser-only role checks"}], edition="all",
    deps=["VZ-AUTH-001"], success=["Matrix test per route per role"], negative=["Manager cannot change settings; member cannot moderate"], privacy=["Role change audited"], api=["PATCH /api/v1/admin/users/{id}/role"], ui=["/admin/users"], evidence=EV_API+EV_NEG)
req("VZ-AUTH-005","Registration policy: open, approval, invite, closed; minimum age; consent screen",
    "Owner: chooses policy; approval queue; invite links; minimum age required; optional age-gate consent screen with cover image.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"User sign up; Consent screen (age gate) Lite/Pro; User min age required Lite/Pro; User notify sign up"}], edition="Lite",
    deps=["VZ-AUTH-001","VZ-ADMIN-002"], success=["Each policy tested; owner notified on signup when enabled"], negative=["Closed policy: signup 403; approval: account inactive until approved"], api=["PATCH /api/v1/admin/settings/registration","GET/POST /api/v1/admin/registrations"], ui=["/admin/settings/registration","/admin/registrations"], evidence=EV_API+EV_UI)
req("VZ-AUTH-006","OAuth2 social login providers",
    "Member: signs up/in with configured OAuth2 providers; owner enables providers from the admin UI; email required for social signup when configured; connected providers visible in settings.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"OAuth2 login providers (Amazon, Google, Discord, etc) Lite/Pro"},{"source":"CHEV-LOGIN-PROVIDERS","note":"30 providers listed"}], edition="Lite",
    deps=["VZ-AUTH-001"], success=["Google, GitHub, Discord live-tested; generic OIDC provider supported"], negative=["State/PKCE mismatch rejected; email collision handled explicitly"],
    privacy=["Provider tokens encrypted; scopes minimal"], api=["GET /api/v1/auth/oauth/{provider}/start|callback"], ui=["/login","/settings/connections","/admin/settings/login-providers"], evidence=EV_API+["live provider evidence per advertised provider"], decided=["Q-012"],
    mechanism="Chevereto lists 30 named providers. Proposed equivalent: a generic OAuth2/OIDC adapter plus first-class configs for the most used providers; each advertised provider needs live evidence before it is claimed.")
req("VZ-AUTH-007","Sign in with an AT Protocol identity",
    "Member: links or signs in with a DID-anchored AT identity via the OAuth profile (PKCE, PAR, DPoP, ES256); handle changes do not break the link.",
    "identity", INTEG, [{"source":"AT-OAUTH","note":"PKCE+PAR+DPoP required"},{"source":"PROMPT-09","note":"family A"}],
    deps=["VZ-AUTH-001"], success=["Login against a reference PDS; identity mismatch rejected"], negative=["Expired/revoked token → re-auth; issuer mismatch rejected"], privacy=["DID stored, handle display only"], recovery=["PDS migration re-resolved from DID"], api=["/api/v1/auth/atproto/*"], ui=["/login","/settings/connections"], evidence=["PDS interoperability evidence"])
req("VZ-AUTH-008","API keys per user and guest API key",
    "Member: creates/revokes personal API keys; owner sets a guest upload key; keys hashed; scopes at least upload/read/manage.",
    "identity", CHEV, [{"source":"CHEV-API-V4","note":"X-API-Key; user keys at /settings/api; admin guest key"},{"source":"CHEV-COMPARE","note":"Guest API key all editions"}], edition="all",
    deps=["VZ-AUTH-001"], success=["Key used on upload API; revoked key 401"], negative=["Key leaked in logs test"], privacy=["Scopes limit damage"], api=["GET/POST/DELETE /api/v1/me/api-keys","admin guest key setting"], ui=["/settings/api","/admin/settings/api"], evidence=EV_API+EV_NEG,
    mechanism="Chevereto documents no scopes or rate limits for keys; Vizra adds scopes and rate limits (Q-033).", decided=["Q-033"])
req("VZ-AUTH-009","Rate limits on auth, upload, comments, search, federation inbox and password reset",
    "Operator: bounded per-IP/per-account limits with Redis-backed counters; configurable; documented; flood reports to admin email optional.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"Flood protection (Pro)"},{"source":"CHEV-FEATURES","note":"limits by minute/hour/week/month; flood reports by email"}], edition="Pro",
    deps=["VZ-AUTH-001","VZ-TOPOLOGY-003"], success=["Limits enforced with 429 and Retry-After"], negative=["Redis down → conservative fallback, no fail-open on auth brute force"], api=["all mutating endpoints"], ui=["/admin/settings/limits"], evidence=EV_API+["load test transcript"], decided=["Q-024"])
req("VZ-ACCOUNT-001","Profile: username, display name, bio, website, avatar, background, language, timezone, privacy",
    "Member: edits profile fields; avatar/background size limits set by admin; private profile hides content from non-followers/anonymous.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"User profiles; Private user profiles; User avatar/background max file size"},{"source":"CHEV-FEATURES","note":"Website and Bio fields; Avatar and profile background images"}], edition="all",
    deps=["VZ-AUTH-001","VZ-MEDIA-001"], success=["Profile renders publicly per privacy"], negative=["Oversized avatar rejected with message"], privacy=["Private profile: username not leaked on JSON endpoints (Chevereto 4.5.4 CVE class)"], api=["GET/PATCH /api/v1/me","GET /api/v1/users/{username}"], ui=["/settings/profile","/u/{username}"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-ACCOUNT-002","Account export (all data) and deletion",
    "Member: requests an export archive (originals, metadata, albums, comments, ratings, favorites, follows) and can delete the account; deletion cascades or anonymizes per policy; remote copies disclaimed honestly.",
    "identity", EXPLICIT, [{"source":"CATALOG-F1","note":"account settings/export/deletion"},{"source":"CHEV-COMPARE","note":"Export user"}], edition="all",
    deps=["VZ-AUTH-001","VZ-JOBS-001"], success=["Export job produces archive with manifest; deletion removes media, revokes sessions, unpins IPFS best-effort"], negative=["Deletion requires re-auth; export link expires"], privacy=["Export accessible only to the owner"], recovery=["Deletion job resumable"], api=["POST /api/v1/me/export","DELETE /api/v1/me"], ui=["/settings/account"], evidence=EV_API+EV_UI)
req("VZ-ACCOUNT-003","User content deletion toggle",
    "Owner: toggle whether members may delete their own content.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"User content delete (all editions)"}], edition="all",
    deps=["VZ-ADMIN-002"], success=["Toggle off: delete controls hidden and API 403"], api=["settings"], ui=["/admin/settings/users"], evidence=EV_API+EV_UI)
req("VZ-ACCOUNT-004","Notification preferences and newsletter opt-in",
    "Member: chooses which events notify in-app/email; newsletter opt-in field exists for owner exports.",
    "identity", CHEV, [{"source":"CHEV-FEATURES","note":"Newsletter subscription option"},{"source":"CATALOG-F4","note":"notifications/preferences"}], edition="all",
    deps=["VZ-NOTIFY-001"], success=["Preference honored per channel"], api=["PATCH /api/v1/me/preferences"], ui=["/settings/notifications"], evidence=EV_API+EV_UI)
req("VZ-ADMIN-USERS-001","Operator user management",
    "Owner/admin: list/search users, create users, suspend/restore, change role, reset password, delete with content handling, view quota usage and storage location. Owner: transfers the single owner role to another live user; an instance whose only owner account is tombstoned is recoverable and never left ownerless.",
    "identity", CHEV, [{"source":"CHEV-COMPARE","note":"User management; Create users from admin"}], edition="all",
    deps=["VZ-AUTH-004","VZ-ADMIN-001"],
    success=["Each action audited; suspended user cannot sign in",
             "Owner transfer: the owner, after step-up re-authentication, hands the owner role to a live, non-disabled user in ONE transaction; afterwards exactly one live owner exists, the previous owner holds the role the transfer names, and one audit row records both usernames",
             "Tombstoned-owner recovery: when the only owner account is tombstoned, an operator-side, host-authenticated, audited path assigns the owner role to a live user; the claim endpoint stays closed throughout (its gate is EXISTS(users), not the owner index)"],
    negative=["Cannot demote the last owner",
              "'Cannot demote the last owner' is enforced APPLICATION-SIDE: the users_one_owner partial unique index (WHERE role = 'owner' AND tombstoned_at IS NULL, vizra-core migration 0005) permits at most one LIVE owner — it refuses a second, never zero — so a named test proves the application refuses demoting the only live owner outside the transfer path, and a controlled mutation removing that check turns it red",
              "A transfer requested by anyone other than the owner is refused; a transfer to a tombstoned, disabled or unknown user is refused with no role change; two concurrent transfers leave exactly one live owner (the index decides, 23505 maps to 409, never 5xx)"],
    privacy=["Owner transfer and owner recovery audit rows carry usernames only, never an email (VZ-AUDIT-001)"],
    recovery=["A transfer that fails mid-transaction leaves the previous owner in place; the tombstoned-owner recovery path is idempotent when re-run"],
    api=["/api/v1/admin/users*"], ui=["/admin/users"], evidence=EV_API+EV_UI+EV_NEG,
    notes="Owner-transfer and tombstoned-owner recovery obligations added 2026-09-23 from the war-room chair's M1-A plan rulings (docs/evidence/warroom/2026-09-21-vizra-core-m1a-owner-claim-PLAN-RULINGS.md, row 1: 'Owner transfer stays a later slice'). The users_one_owner predicate counts only live owners so a tombstoned owner does not brick the instance. ADR-003 says the owner 'is single and cannot be demoted'; this entry reads that as 'no other actor demotes the owner' and the owner's own transfer as the only way the role moves — the implementing slice's plan review confirms that reading. The operator recovery surface (CLI or other) is chosen by that slice and is not named here.")
req("VZ-AUDIT-001","Audit-trail retention and actor anonymisation; user erasure by scrub-and-tombstone",
    "Owner/operator: audit_events rows are retained for a bounded period and then removed or anonymised, and an erased user's identity is anonymised in the rows that name them, only through one reviewed, audited path; erasure scrubs and tombstones the users row and never deletes it; audit rows never carry PII beyond the username.",
    "identity", SAFE, [{"source":"AGENTS","note":"never log credentials, private signed URLs, or raw private metadata; append-only migrations; explicit retry/recovery"},{"source":"CATALOG-F1","note":"account settings/export/deletion; operator account management"}],
    deps=["VZ-ACCOUNT-002"],
    success=["The retention/anonymisation path is added ADDITIVELY: a later migration widens audit_events_append_only() with CREATE OR REPLACE FUNCTION, which migrate-lint's destructive pattern does not match, so the migration needs no -- allow-destructive: annotation and the row trigger and statement-level TRUNCATE trigger stay in place",
             "A retention sweep removes or anonymises rows older than the retention window only through that path, in batches, and writes one audit row per run naming the window and the count, never row contents",
             "Account erasure (VZ-ACCOUNT-002) scrubs and tombstones the users row — email NULLed, credentials removed, tombstoned_at set — and anonymises that user's username in the audit rows that name them; actor_user_id still references the tombstoned row, so the audit chain stays intact"],
    negative=["Every UPDATE or DELETE on audit_events other than the retention/anonymisation shape is still refused by the trigger, and TRUNCATE is still refused; a controlled mutation that widens the function to accept any UPDATE turns a named test red",
              "DELETE FROM users for a user named by an audit row fails (audit_events_actor_user_fk is ON DELETE RESTRICT, 23503); the erasure path never issues DELETE on users, and a test asserts it",
              "No API route exposes arbitrary audit mutation; the retention and erasure jobs are the only callers of the anonymisation path"],
    privacy=["audit before, after and actor_label never carry an email address or any PII beyond the username; a test scans every audit kind the suite writes for email-shaped values and fails on any",
             "Anonymisation also clears ip_prefix; after erasure the user's username, email and credentials are not reachable from the audit read surface, exports or logs"],
    recovery=["The erasure job is resumable and idempotent: a crash between scrub and tombstone re-runs to the same end state, and re-running on a tombstoned user is a no-op",
              "An interrupted retention sweep resumes without skipping or double-counting; each batch and its audit row commit in one transaction",
              "Tombstoning the owner leaves the instance recoverable (users_one_owner counts only live owners; recovery path under VZ-ADMIN-USERS-001)"],
    api=["DELETE /api/v1/me","GET /api/v1/admin/audit"], ui=["/admin/audit"],
    evidence=EV_API+EV_NEG+["migration test on real PostgreSQL: the widened function still refuses every non-retention UPDATE/DELETE and TRUNCATE","migrate-lint transcript showing the widening is not classed destructive","audit PII scan test output"],
    notes="Owed by the war-room chair's M1-A plan rulings (docs/evidence/warroom/2026-09-21-vizra-core-m1a-owner-claim-PLAN-RULINGS.md, row 4 and OQ-7). vizra-core migration 0005_users_credentials_owner_claim.up.sql lands the strict audit_events_append_only() trigger (UPDATE, DELETE and TRUNCATE refused) and audit_events_actor_user_fk ON DELETE RESTRICT, and says the audited retention/anonymisation path 'carries its own ledger ID' — this entry. 0003_audit_events deferred the trigger and the retention path as a pair. ADR-007 § audit_events.")
