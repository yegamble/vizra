# ADR-007: Domain model: assets, albums, privacy, social, site

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` makes PostgreSQL transactional truth, requires database constraints
for concurrency invariants and default-deny authorization across counts, exports,
embeds and feeds. `docs/PRODUCT_SPEC.md` §§4–5 define the entities and visibility
semantics; Q-039 requires the precedence order and named rulings written here;
Q-008 constrains the site seam. Migrations are append-only, so keys and visibility
columns must be right in the migration that creates them.

## Decision
### Identifiers
Internal primary keys are `uuid` v7 everywhere. Public short ids are a separate
column, `public_key`, random base62 with a length setting defaulting to 8, never
sequential, giving Chevereto-style URLs; slugs are another separate column.
Storage keys never derive from public ids (ADR-005).

### Entities and keys

| Entity | Key | Notes |
|---|---|---|
| `sites` | `id` | exactly one row in core, handle `default`, `base_url` |
| `users` | `id` | `role` ordered enum; profile; preferences |
| `user_groups` | `id` | Chevereto parity, M2+, additive permissions |
| `sessions`, `api_keys` | `id` | ADR-003 |
| `assets` | `id`, unique `public_key` | owner, visibility, `visibility_version`, safety level, licence, content type, title/description, `taken_at`, `uploaded_at`, category, counts as derived caches |
| `tags`, `asset_tags` | `tags.id`, unique tag name; `(asset_id, tag_id)` | user-defined tags created on the fly, phrase tags, rename/delete across items (VZ-TAG-001) |
| `categories` | `id`, unique URL key | admin-defined name, URL key, description; assigned by users (VZ-CATEGORY-001) |
| `collections`, `collection_albums` | `collections.id`, unique `public_key`; `(collection_id, album_id)` + `position` | **full profile** reservation: hierarchical grouping of the owner's own albums, `parent_id` with a depth limit of **5** levels, mosaic cover, share by URL (VZ-COLLECTION-001) |
| `galleries`, `gallery_items` | `galleries.id`, unique `public_key`; `(gallery_id, asset_id)` + `position` | **full profile** reservation: curated sets of other members' public safe photos, at most **500 items**, with creator opt-out held both globally on `users` and per item on `assets` (Q-037, VZ-GALLERY-001) |
| `groups`, `group_members` | `groups.id`, unique `public_key`; `(group_id, user_id)` | **full profile** reservation: group privacy `public|invite-only|private`, join/leave/invite, member role admin/moderator/member (VZ-GROUP-001) |
| `audiences`, `audience_members` | `audiences.id`; `(audience_id, user_id)` | **full profile** reservation: named audiences as the fourth precedence step (VZ-PRIVACY-004) |
| `asset_files`, `asset_metadata` | ADR-006 | representations and extracted metadata |
| `albums` | `id`, unique `public_key` | owner, `parent_id`, privacy, cover, sort mode |
| `album_items` | `(album_id, asset_id)` + `position` | many-to-many |
| `share_grants` | `id` | `(subject asset|album, kind link|password|member|audience, secret hash, expires_at, revoked_at)` |
| `asset_favorites`, `album_favorites` | `(user_id, asset_id)` / `(user_id, album_id)` | Q-018 |
| `asset_ratings` | `(user_id, asset_id)` | `CHECK` 1–5; aggregate maintained transactionally |
| `comments` | `id` | threaded one level |
| `storage_locations` | `id` | ADR-005 |
| `upload_sessions`, `quota_reservations`, `user_usage` | ADR-005 | |
| `jobs`, `job_runs` | ADR-004 | |
| `remote_publications` | `id` | ADR-008; never columns on `assets` |
| `instance_settings` + version counter row | key | ADR-002 |
| `audit_events` | `id` | who, what, when, before, after |

Albums prevent cycles through an application check under a subtree lock **and** a
constraint trigger that walks ancestors; the depth limit is a setting (default
`[to confirm in M0]`). Album privacy is Chevereto's verbatim set — `public`,
`private`, `link`, `password`. Asset visibility is `public`, `unlisted`,
`private`, with `visibility_version int` bumped on every privacy change and
carried in every cache and CDN key (Q-039).

### Visibility and precedence
The precedence order is **site mode → asset visibility → album privacy or share
grant → audience** (audiences are full-profile, VZ-PRIVACY-004). Every read
surface calls `authz.Decide` (ADR-003). The named rulings:

1. Album privacy never widens and never narrows an asset's own visibility: a
   public asset inside a private album stays reachable at its own URL and in
   search, while the album page and its listing stay private.
2. Album and profile counts include only items the viewer may see; counts of
   private items are never revealed.
3. `unlisted` means reachable by link and excluded from listings, search, feeds,
   sitemaps and public federation collections.
4. Hide-from-search (VZ-PRIVACY-002) applies to public items only.
5. Any surface absent from the Q-039 surface × visibility matrix is DENY. That
   matrix is frozen below in § "Frozen surface × visibility matrix".

### Frozen surface × visibility matrix
This section is the Q-039 frozen matrix. It is the authority; ADR-003's
`internal/authz` section points here.

**Viewer classes.** **A** anonymous · **M** signed-in member without a grant ·
**G** holder of a valid grant on the item or on an album containing it (link,
password, named member; audience in the full profile) · **O** owner · **S** staff
(admin/manager) acting in an audited administration or moderation context.

**Precedence, evaluated in order by `authz.Decide`:** (1) **site privacy mode** —
on a private site, A is denied every surface except sign-in, owner claim and public
health; (2) **asset visibility** — `public`: A/M/G/O/S; `unlisted`: reachable only
at its own URL or a token-bearing derivative URL, by A/M/G/O/S, and excluded from
every listing; `private`: O/G/S only; (3) **album privacy and share grants** — a
public album never widens: it shows only items the viewer may see under (2); an
album whose privacy is `link` or `password`, or which carries an explicit grant, is
a capability covering its current items for that grant's holders (this is the
explicit-grant step, not a change of the item's visibility: the item stays
unlisted or private for listing, search, feeds, federation, IPFS and sitemaps);
album privacy never narrows: a public item in a private album stays reachable by
its own URL and in search while the album page and listing are private;
(4) **audiences** (full profile) as a further grant class. **DENY is the answer for
any surface not in the table below.**

| Surface | public | unlisted | private |
|---|---|---|---|
| 1. Item page and API item read | all | all, with the URL | O G S |
| 2. Original download | per the owner's download setting (all, members, nobody), narrowed by (2) | link-holders, per the same setting | O; G when download is in the grant; S |
| 3. Derivative URLs (display, thumbnail) | all; shared-cacheable and CDN-eligible with `?v=<visibility_version>` | token-bearing URL, proxied, `Cache-Control: private, no-store`, never CDN (Q-025) | proxied, O G S only, never CDN |
| 4. Album page | governed by album privacy; items filtered by (2)+(3); count = items the viewer may see | same rule (not split by item visibility) | same rule (not split by item visibility) |
| 5. Album item count, profile counts, tag/category counts | counted for every viewer who may see the item | never contributes to a count shown to A/M | never contributes to a count shown to A/M |
| 6. Owner library | O (and S in an audited admin context) see everything | included — O, and S in an audited admin context | included — O, and S in an audited admin context |
| 7. Profile grid of another user | shown | excluded (public only) | excluded (public only) |
| 8. Explore, random, trending, featured | included, safety-filtered | excluded (public only) | excluded (public only) |
| 9. Search and suggestions | indexed and returned to A/M; hide-from-search (VZ-PRIVACY-002) removes public items only | excluded; O additionally finds own unlisted when searching own library scope; grants do not extend to search | excluded; O additionally finds own private when searching own library scope; grants do not extend to search |
| 10. Tag and category listings | listed | excluded (public only) | excluded (public only) |
| 11. Feeds (RSS/Atom, following feed) | included — the following feed is the public items of followed users; audiences in the full profile | excluded (public only) | excluded (public only) |
| 12. Notifications | delivered only to recipients who may see the item; item titles redacted if access was lost | same rule | same rule |
| 13. Favorite count and rating aggregate | shown to viewers who may see the item | shown only to viewers who may see the item | aggregates of private items visible to O/S only |
| 14. oEmbed, Open Graph, embed codes | all | embed URLs carry the token and are `no-store` | none |
| 15. Sitemap | included | excluded (public only) | excluded (public only) |
| 16. Bulk/zip download | only items the viewer may see | only items the viewer may see | only items the viewer may see |
| 17. Federation outbound (ActivityPub) | published; inbound interactions accepted only on public items | never published; a visibility change away from public emits `Delete` | never published; a visibility change away from public emits `Delete` |
| 18. IPFS publication | eligible only with a listed owner (ADR-008 fence) | never | never |
| 19. Export | O's own everything; site export by owner role, audited | O's own everything; site export by owner role, audited | O's own everything; site export by owner role, audited |
| 20. Admin console and moderation | S sees all, with audit | S sees all, with audit | S sees all, with audit; viewing a private original is an audited action |
| 21. Caches and CDN | every key carries `visibility_version`; only public derivatives are shared-cacheable | every key carries `visibility_version`; not shared-cacheable | every key carries `visibility_version`; not shared-cacheable |

A privacy change bumps `visibility_version` and enqueues a purge (an ADR-004 job
kind), so row 21 holds for every one of the rows above it.

**M0 obligation.** This table is the fixture of a table-driven test in
`internal/authz` from `vizra-core` PR1 — the evaluator exists before any product
route — and VZ-PRIVACY-001 (M1) makes every row pass against real routes.

### Site and tenant seam
`sites` holds exactly one row in core. Isolation mode under tenancy is
**database-per-tenant**: a tenant registry in a control database maps hostname →
DSN, plans/limits and lifecycle, and tenancy is a connection-routing concern. There
is no `tenant_id` column and no per-tenant schema anywhere in core;
schema-per-tenant is rejected, because it collides with the component-owned
`search` schema (Q-001) and the one-`pg_dump` property and multiplies the
migrate-lint matrix (Q-008).

**The DSN source.** In core the site registry is the single `sites` row of the
connected database plus the one `DATABASE_URL` from configuration — **there is no
DSN column**. In the full profile with tenancy (M5), the registry is the control
database mapping hostname → DSN (Q-008). The `site.Resolver` abstracts both and is
the only thing callers see:

```go
type Site struct { Handle, BaseURL, DSN, CacheNamespace, StoragePrefix string }
func (r *Resolver) Sites() []Site
```

Core's implementation returns one entry, built from configuration. The worker and
the migrator iterate `Sites()` and never read a registry table directly (ADR-004).

**The Q-008 M0 plumbing checklist, copied in full.** What M0 must freeze so
database-per-tenant is not precluded:

> "(1) no package-global DB pool, cache client, storage client or search client —
> all handles resolved from one context resolver with a single default
> implementation, enforced in `make ci`; (2) hostname → tenant resolution in
> exactly one middleware; (3) storage key prefix from the resolver (default
> `default`), never a hardcoded root; (4) cache key namespace from the resolver;
> (5) the worker loops a tenant registry (one entry in core), leasing from each
> tenant database; (6) the migrator takes a DSN and applies per DSN with a
> per-database ledger and an explicit partial-failure state; `backup.sh` iterates
> tenants; (7) federation actor derived from the request hostname, not a global
> base-URL constant; (8) `vizra-search` takes one `DATABASE_URL` today, so M5 must
> design N search DSNs or one search instance per tenant — recorded on
> VZ-TENANT-001."

`internal/site` performs item (2) in exactly one middleware; `make ci` enforces
item (1) with a forbidden-import lint test.

`audit_events` exists from M0 and records settings, role, moderation and privacy
changes.

## Consequences
Positive: separating internal id, public id and slug means a URL change never
touches a foreign key and an object key never leaks an identifier;
`visibility_version` makes cache invalidation a data fact rather than a
best-effort purge; two foreign-keyed favorites tables keep the unified Favorite
action honest without a polymorphic target pair. Negative: an extra random column
per public entity, an ancestor-walking trigger on album writes, and counts that
cannot be one cached integer per entity. Risks: an application-only cycle check
would be defeated by concurrency, which is why the trigger exists too; a count
cached without the visibility version leaks the existence of private items. Later
milestones must not break: public ids never sequential and never storage keys,
`visibility_version` in every cache key, the single host middleware and the
no-package-globals lint, audit events for privacy and role changes, the five
rulings above, and deleting an album never deleting assets.

## Precedent
Copied from Vidra (survey citations): a fixed role enum enforced in the schema
(`C/migrations/0002_users_sessions.up.sql:12`), delegation through a membership
table (`C/migrations/0097`), the 404-not-403 convention for
resources a viewer may not see (`C/internal/httpapi/channel_members.go:33`), and
the partial index that fences public, published content out of everything else
(`C/migrations/0006:24`).

Unlike Vidra: there is no single authorization evaluator there — per-resource
authorization is three hand-written helpers
(`C/internal/httpapi/channel_members.go:23,39`;
`C/internal/httpapi/comments.go:370`) and default-deny is a per-handler
convention; the role model is a three-value CHECK enum with no groups and no
permissions table (`C/migrations/0002_users_sessions.up.sql:12`); and viewer-scoped
reads were pushed into the client behind a settled-session hook, the same privacy
bug being fixed four times including a mute/block failure
(`U/lib/use-settled-session.ts:22,41-62`). Vizra's server-side evaluator and
visibility-versioned public reads exist because of that history.

## Evidence and ratification
Q-007 (quota shape on `users`), Q-008 (database-per-tenant, no tenant column, the
M0 plumbing checklist), Q-018 (one Favorite action, two foreign-keyed tables,
ratings distinct), Q-037 (gallery limits and opt-out), Q-039 (precedence,
visibility version, surface matrix, album and count rulings) and Q-040 (private
profiles; no follower-only level in core) in the `docs/OPEN_QUESTIONS.md`
ratification record.

## Ledger IDs
VZ-PRIVACY-001, VZ-PRIVACY-002, VZ-PRIVACY-004, VZ-ALBUM-001, VZ-ALBUM-002,
VZ-SHARE-001, VZ-FAVORITE-001, VZ-RATING-001, VZ-COMMENT-001, VZ-TAG-001,
VZ-CATEGORY-001, VZ-COLLECTION-001, VZ-GALLERY-001, VZ-GROUP-001, VZ-AUTH-004,
VZ-TENANT-001, VZ-ADMIN-002, VZ-FOUND-003.

## M0 obligations
The M0 foundation issue implements migration `0001_sites` with the single default
row, `0003_audit_events`, the `internal/site` resolver with one Host middleware and
its `Sites()` DSN abstraction, the context-resolved handles with the
forbidden-import lint in `make ci`, the resolver-derived storage prefix and cache
namespace, and the `internal/authz` table-driven test whose fixture is the frozen
surface × visibility matrix above.

Reservation only: `assets`, `albums`, `album_items`, `share_grants`, the social
tables, `user_groups` and `remote_publications` are schema and constraint
reservations described here and created with their slices — assets, albums and
privacy in M1 (VZ-PRIVACY-001, VZ-ALBUM-001, VZ-ALBUM-002), social in M2,
collections and galleries with their full-profile slices (VZ-COLLECTION-001,
VZ-GALLERY-001), groups and audiences in M5 (VZ-GROUP-001, VZ-PRIVACY-004). The append-only rule means the columns named above must be
present when each table is first created, not added later.
