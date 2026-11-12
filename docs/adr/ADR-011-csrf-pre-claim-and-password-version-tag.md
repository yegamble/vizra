# ADR-011: CSRF table pre-claim rows and the password version tag (amends ADR-003)

## Status
Accepted (owner) 2026-11-12, decision #10 (`docs/warroom/OWNER-DECISIONS.md`, "2026-11-12" item 10; question in `docs/warroom/OWNER-INBOX.md` under "### 8b"). This ADR **amends** ADR-003 in part. ADR-003 stays Accepted and is not edited. Where the two disagree, this ADR wins.

## Date
2026-11-12

## Context
ADR-003's CSRF table has a row "Setup wizard | none (pre-claim) | loopback bind **and** one-time `X-Setup-Token` **and** Host allowlist | allow". That row was written for the installer's `vizra setup --web` wizard (VZ-ISSUE-004). It could also be read as covering the owner claim page (`POST /api/v1/setup/claim-owner`). Under that reading the claim page cannot be built, because the browser that claims the instance is not on loopback and has no setup token. The table has no row for an unauthenticated JSON POST made before the claim, where the credential travels in the body. Both review seats read the row as installer-only (inbox 8b).

ADR-003 "Credentials" also says the argon2id hash "carries a Vizra version tag … without a second column" but does not say what the tag looks like.

## Decision
1. **Rename the row.** In ADR-003's CSRF table, the row "Setup wizard" now reads **"Installer setup wizard"**. Its other columns stay the same: none (pre-claim) | loopback bind **and** one-time `X-Setup-Token` **and** Host allowlist | allow. It covers only the installer wizard.
2. **Add one row:**

   | Request | Credential | Required | Result |
   |---|---|---|---|
   | Unauthenticated pre-claim JSON POST | credential in body | exact JSON content type; `Origin` / `Sec-Fetch-Site` must not be cross-site when present | allow |

   "Exact JSON content type" means the request's media type is `application/json`. A request whose `Origin` or `Sec-Fetch-Site` header is present and cross-site is denied with 403. Rate limits and the owner-claim failure budget from ADR-003 still apply.
3. **The version tag is the PHC string.** The "Vizra version tag" is the plain, standard PHC string `$argon2id$v=19$m=<KiB>,t=<iterations>,p=<parallelism>$<salt>$<hash>`. The `m`, `t` and `p` values inside it **are** the version. There is no extra Vizra field or prefix. A stored hash whose `m,t,p` differ from the current pins is re-derived on the next successful sign-in.

## Consequences
- Positive: the owner claim page can be built with a stated CSRF rule, and the installer wizard's stricter rule is no longer read as applying to it. Stored hashes stay in standard PHC format and any argon2 tool can read them.
- Negative: an unauthenticated pre-claim endpoint has no token. It depends on content-type and fetch-metadata checks plus rate limits.
- Later milestones must not apply the new row to any request that carries a session cookie or an API key. Those keep their own rows.

## Precedent
None new from Vidra. ADR-003's Precedent section is unchanged.

## Evidence and ratification
Q-032, Q-033 as recorded for ADR-003. Owner decision 2026-11-12 #10.

## Ledger IDs
VZ-INSTALL-003, VZ-AUTH-001, VZ-SECURITY-003.

## M0 obligations
None new. The M1-B claim-page PR implements row 2 with negative tests: wrong content type → 403, cross-site `Origin` → 403, cross-site `Sec-Fetch-Site` → 403. The installer wizard (VZ-ISSUE-004) implements row 1.
