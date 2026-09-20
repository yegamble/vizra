# Vizra product specification — baseline of 2026-09-15

**Status:** PLANNED / UNVERIFIED. This document defines what Vizra must be; it describes no existing code. The atomic obligations live in `docs/quality/features.json` (190 requirements, IDs `VZ-<AREA>-<NNN>`); the release claims live in `docs/quality/release-profiles/{core,full}.json`; the UI-control inventory in `docs/quality/ui-controls.json`; evidence sources in `docs/SOURCE_REGISTER.md`; unresolved decisions in `docs/OPEN_QUESTIONS.md`; the install/CI/topology design in `docs/META_REPO.md`. Where this prose and the ledger differ, the ledger governs and the difference is a defect to fix.

## 1. Product statement

Vizra is an original, self-hosted photo community: Flickr-like community workflows, the audited functional union of Chevereto Free, Lite and Pro (4.5.7, 2026-08-20), and optional S3/AWS/Backblaze storage, ActivityPub federation, AT Protocol identity/publication and IPFS distribution. Stack: Go/Echo/PostgreSQL/sqlc/Redis/Docker; Next.js/TypeScript/Tailwind; Go/PostgreSQL/Redis search with optional ClickHouse analytics. Repository shape: a Vidra-style meta repo tying together `vizra-core`, `vizra-user` and `vizra-search`.

Vizra has **no billing**. Every capability a reference product paywalls (Chevereto Lite/Pro features; Flickr Pro: mature content, stats, originals, long video, group caps, API keys, unlimited storage) is provided ungated under instance-operator policy and quotas (Q-019).

## 2. The two claims

| | `core` | `full` |
|---|---|---|
| Requirements | 141 | 191 (every requirement) |
| Users can | install with one command and a wizard, claim the owner account, upload photos (JPEG/PNG/GIF/WebP/AVIF/BMP; MP4/MOV/WebM store+poster), get correct derivatives with EXIF/GPS policy, organize into nested albums with per-item visibility, album privacy and share grants, tag/categorize, comment/rate/favorite, follow, get notified, explore/search permission-safely, moderate uploads and reports, brand the site, use local or S3-compatible storage, restart/backup/restore/upgrade | everything in core plus live-qualified AWS/Backblaze, native GCS/Azure/OSS/Swift/SFTP/FTP (or approved substitutions), multi-location storage migration, imports (filesystem/Chevereto/Flickr), site export, ActivityPub, AT Protocol (login, Bluesky cross-post, native records), IPFS, ClickHouse analytics and member stats, groups/pools/discussions, galleries, collections, notes, people tags, geo/map, licensing, content types, messages, multitenancy, external CAPTCHA/anti-spam/moderation/CSAM services, banners, i18n |
| Topology | PostgreSQL/Redis managed or external; ClickHouse and IPFS OFF (must render, must not start) | all OFF/EXTERNAL/MANAGED shapes |
| Not claimed | anything listed under full-only; ARM64 (Q-027 decided 2026-09-15: not claimed; CLI built for arm64) | nothing accepted may be deferred; a deferral is an owner decision in OPEN_QUESTIONS |

A core-only release is never described as the completed application. Both claims are frozen per `docs/RELEASE_ACCEPTANCE.md` before any rehearsal.

## 3. Actors and roles

Visitor (anonymous) · Member (`member`) · Photographer (a member acting on own content) · Manager (content moderation, no settings) · Admin · Owner (single; cannot be demoted) · Guest uploader (anonymous uploader when enabled) · Operator (host/CLI) · Tenant operator (full profile) · Remote actor (ActivityPub/AT peer, untrusted). Authorization is server-side and default-deny on every read surface (VZ-AUTH-004, VZ-PRIVACY-001).

## 4. Domain model

- **Asset** (photo or video): stable internal ID; public non-enumerable ID; owner; visibility; safety level; content type; title, description, **alt text**, tags, category, license, dates (taken, uploaded); EXIF (stored; display and stripping per policy); checksum; provenance; processing version; storage location; quota accounting; expiration. Never tied to an object key, URL or CID.
- **Representation**: original; display; medium (fixed width or height); thumbnail; optional video poster/playback derivative; 360 flag. Large derivatives of restricted originals are served via unguessable, authorization-checked paths.
- **Album**: owner; parent (cycle-safe); many-to-many membership; cover; description; sort mode (date taken/uploaded asc/desc, alphabetical, random, manual); privacy public/private/link-only/password; CTA buttons. An album never widens an asset's visibility; deleting an album never deletes assets; empty albums are allowed.
- **Share grant**: revocable capability (link, password, named member, audience) on an asset or album; listed and expirable by the owner.
- **Audience** (full): owner-maintained lists (e.g. followers, friends/family-style labels) usable as visibility targets.
- **Collection** (full): tree of own albums or sub-collections, depth 5. **Gallery** (full): curated set of other members' public safe assets (≤500) with creator opt-out. **Group** (full): privacy public/invite-only/private, roles admin/moderator/member, pool with approval and explicit visibility grants, discussions with sticky/locked topics.
- **Tag** (user-defined, phrase-capable, renamable, machine tags in full) · **Category** (admin-defined, URL key).
- **Favorite**: unique (user, asset|album); personal listing; public count; notification. **Rating**: one current 1–5 vote per user per asset; aggregate average/count/distribution. **Comment**: threaded one level; sanitized allow-list formatting; edit/delete/report. Likes are unified with favorites (Q-018, decided 2026-09-15).
- **Follow** (asymmetric) · **Block** (retroactive cleanup) · **Report** · **Notification** · **Message** (full).
- **User**: roles; profile (avatar, background, bio, website, privacy); preferences (defaults for new uploads, EXIF keep, notifications, language, timezone, NSFW display); API keys (scoped, hashed); 2FA; sessions.
- **Storage location**: type local/s3/…; capacity; URL/CDN mapping; capability flags. **Job/outbox**: durable, leased, idempotent. **Setting**: registry-backed runtime configuration with audit. **Audit event**. **Tenant** (full). **Remote publication**: AP object IDs, AT record URIs/CIDs, IPFS CIDs kept separate from local records.

## 5. Visibility and authorization semantics

Asset visibility: **public**, **unlisted** (reachable by link; excluded from listings, search, explore, tags, feeds, sitemap, federation, IPFS), **private** (owner, admins with audit, and holders of an explicit grant). Album privacy adds container-level gating and grants; site privacy mode can force login for everything. Safety level (safe/moderate/restricted) and content type are orthogonal axes with a viewer-side filter defaulting to safe for visitors and operator policy for what may be published.

Every read surface enforces the same decision: photo page, lightbox, thumbnails and derivatives, original download, metadata/EXIF, album listings and counts, tag pages and counts, search results, facets, suggestions, explore, feeds, notifications, oEmbed/OG, sitemap, exports, API listings, ActivityPub objects, AT records, IPFS publication, caches. Tightening visibility invalidates caches, removes the item from others' favorites views, cancels queued external deliveries, sends Delete/unpin best-effort, and never fails open. Counts of private items are never revealed. Group pools and people tags are explicit grants, never silent overrides.

## 6. Upload and media pipeline

Authorize → reserve quota → create upload session → transfer (chunked/resumable; file picker, drop, paste, camera, URL with SSRF defenses, API/ShareX, embedded plugin) → quarantine → sniff real bytes and enforce limits (size, pixels, frames, decompression, decoder time/memory, temp disk) → finalize idempotently with the full metadata/permission envelope → durable processing (libvips/govips; orientation, ICC, transparency, animation; thumbnails/medium/display; poster for video; watermark per policy; EXIF/GPS stripping per policy) → atomic publication → orphan cleanup. Guest uploads, moderation queue (disabled/guest/all), duplicates, expiration, delete links, storage layout/naming, quotas per role/user and per location, reprocessing tools. See VZ-UPLOAD-*, VZ-MEDIA-*, VZ-QUOTA-*, VZ-JOBS-001.

## 7. Organization and community

Library with negative-space filters and bulk actions; edit metadata, dates and time shift; replace/rotate; viewer with keyboard shortcuts; downloads with owner/site permission and bounded zips; albums/sub-albums/collections/galleries; tags/categories; links, embeds (HTML/Markdown/BBCode matrix), oEmbed photo type, OG/Twitter cards for public pages only; SEO routes; licensing; geo with geo-privacy and geofences; content type incl. AI declaration. Community: native comments, numeric ratings, favorites, follows, activity feed, notifications with preferences and a separate moderation-duty queue, blocks, reports, moderation queue with audit, safety levels, profiles, groups, notes, people tags, messages, anti-abuse thresholds. See VZ-LIBRARY-*, VZ-VIEWER-*, VZ-ALBUM-*, VZ-COLLECTION-*, VZ-GALLERY-*, VZ-TAG-*, VZ-CATEGORY-*, VZ-SHARE-*, VZ-LICENSE-*, VZ-GEO-*, VZ-PRIVACY-*, VZ-COMMENT-*, VZ-RATING-*, VZ-FAVORITE-*, VZ-FOLLOW-*, VZ-FEED-*, VZ-NOTIFY-*, VZ-BLOCK-*, VZ-REPORT-*, VZ-MOD-*, VZ-NSFW-*, VZ-PROFILE-*, VZ-GROUP-*, VZ-NOTES-*, VZ-PEOPLE-*, VZ-MESSAGE-*, VZ-SPAM-*.

## 8. Discovery, search and analytics

Explore (recent/trending/popular/following; tabs; random; guest/member toggles) with decayed trending and an interestingness-style featured set; permission-aware PostgreSQL full-text + trigram search with advanced operators and the Flickr-derived filter set; suggestions with privacy-safe caches; `vizra-search` as an internal ranked-ID service with SQL fallback (Q-001); operator statistics from authoritative counts; member stats and ClickHouse analytics as optional, never on the transaction path, with dedup keys, replay and backup/replay responsibility; sitemaps/hreflang for public content only. See VZ-EXPLORE-*, VZ-SEARCH-*, VZ-STATS-*, VZ-ANALYTICS-*, VZ-SEO-001.

## 9. Administration, branding, services

Admin console (dashboard, files, albums, tags, users; bulk actions; audit log); runtime settings registry (website, content, uploads, users, listings, theme, logo, homepage, pages, semantics, routing, languages, email, services, limits, federation, IPFS policy); branding with sanitized CSS and typed extension points instead of raw JS/PHP (Q-014); consent/age gate, cookie notice, banners with a safe boundary; email with provider presets and test tool; CAPTCHA, Akismet/StopForumSpam, moderation-API and CSAM-detection adapters; IP bans, stop words, flood protection, secrets sealing/rotation; tools; update check with CLI-executed upgrades; multitenancy with signed tenant API (full). See VZ-ADMIN-*, VZ-BRAND-*, VZ-PAGE-*, VZ-I18N-*, VZ-LISTING-*, VZ-CONSENT-*, VZ-BANNER-*, VZ-EMAIL-*, VZ-SERVICES-*, VZ-SECURITY-*, VZ-TOOLS-*, VZ-UPDATE-*, VZ-TENANT-*.

## 10. Providers, imports, exports

Local storage by default; S3-compatible adapter with per-provider capability flags (presigned PUT only, configurable checksum algorithm, versioned-bucket deletes); AWS and Backblaze live lanes; native non-S3 adapters as separate full-profile obligations; multiple locations, capacity, CDN mapping with private assets never cacheable, migration with reconciliation; imports from filesystem (Chevereto-compatible layout and sidecars), Chevereto instances and Flickr exports with dry run/checkpoints/reports; account and site export. See VZ-STORAGE-*, VZ-IMPORT-*, VZ-EXPORT-001, VZ-ACCOUNT-002.

## 11. Open-network integrations (full)

ActivityPub: actors, WebFinger, HTTP signatures, Create(Note)+Image attachments with alt text in both Mastodon (`summary`) and Pixelfed (`name`) conventions, `sensitive`, blurhash, focal point; Follow/Accept/Undo, Like/Announce/Reply/Delete/Update/Flag; instance blocks; best-effort deletion; public content only. AT Protocol: DID-anchored login via OAuth (PKCE/PAR/DPoP); Bluesky cross-post within lexicon limits (4 images ≤2,000,000 bytes, 300 graphemes); native Vizra records under an owned NSID with scoped indexing. IPFS: opt-in public representation only, per-publication consent with persistence warning, managed Kubo node (RPC loopback) or pinning service, pin inventory, unpin limits. See VZ-AP-*, VZ-AT-*, VZ-IPFS-*.

## 12. Installation, topology, operations, CI

Defined in `docs/META_REPO.md`: one-command installer → bundle → `vizra` CLI → `vizra setup` interview/web wizard; compose base + production overlay + external overlays; OFF/EXTERNAL/MANAGED for ClickHouse, IPFS, scanners, tracing; sacred deploy ordering; backup with media manifest and keys; restore on a clean host; rollback within the schema window; release records; `ci-required` fan-in with checked-in manifests; meta `validate`/`bundle`/`boot` lanes. See VZ-INSTALL-*, VZ-TOPOLOGY-*, VZ-OPS-*, VZ-BACKUP-*, VZ-UPGRADE-*, VZ-CI-*.

## 13. Parity reconciliation summary

| Source section | Reconciled into | Notes |
|---|---|---|
| Chevereto compare §1.1–1.2 files/uploading | VZ-UPLOAD-001…013, VZ-MEDIA-001…009 | all rows mapped; moderation/watermarks Lite+ |
| §1.3 storage APIs | VZ-STORAGE-001…015 | Pro adapters separate obligations (Q-030/Q-031, decided 2026-09-15) |
| §1.4–1.8 content/organization/tags/albums/sharing | VZ-LISTING-001, VZ-ALBUM-*, VZ-TAG-*, VZ-CATEGORY-001, VZ-SHARE-*, VZ-EXPLORE-* | album privacy modes verbatim; per-item privacy added (Q-039, decided 2026-09-15) |
| §1.9–1.10 users/social | VZ-AUTH-*, VZ-ACCOUNT-*, VZ-PROFILE-001, VZ-FOLLOW-001, VZ-FAVORITE-001, VZ-NOTIFY-001, VZ-BRAND-004, VZ-EXPLORE-002 | likes unified with favorites (Q-018, decided 2026-09-15) |
| §1.11 security | VZ-AUTH-003, VZ-SECURITY-001…003 | |
| §1.12–1.13 admin features/toggles | VZ-ADMIN-*, VZ-BRAND-*, VZ-PAGE-001, VZ-CONSENT-001, VZ-BANNER-001, VZ-SERVICES-*, VZ-I18N-001, VZ-SHARE-003, VZ-MEDIA-004/007, VZ-VIEWER-002, VZ-UPLOAD-005…013 | custom JS/PHP become sanitized equivalents (Q-014); Disqus → native + allowlist (Q-011) |
| §1.14–1.15 system/tooling | VZ-TENANT-*, VZ-MEDIA-001, VZ-BRAND-001, VZ-UPDATE-001, VZ-OPS-004, VZ-EMAIL-001, VZ-SECURITY-003, VZ-ACCOUNT-002, VZ-OPS-005, VZ-JOBS-001, VZ-MEDIA-009, VZ-TOOLS-001 | xrDebug/REPL declined (Q-026) |
| Chevereto API v1/v4, tenants | VZ-AUTH-008, VZ-UPLOAD-010, VZ-TENANT-001/002 | scopes/rate limits added (Q-033, decided 2026-09-15) |
| Chevereto admin manual (29 settings pages) | VZ-ADMIN-002 registry + per-area entries above | every setting name captured in the register |
| Chevereto user manual | VZ-VIEWER-*, VZ-LIBRARY-*, VZ-ALBUM-003, VZ-UPLOAD-003/006/009, VZ-EXPLORE-*, VZ-SEARCH-001, VZ-UPLOAD-010/011 | shortcuts preserved |
| Chevereto NOT SHIPPED (V5 API, tags badge) | excluded / Q-006, decided 2026-09-15 | |
| Flickr organize/albums/collections/galleries | VZ-LIBRARY-*, VZ-ALBUM-001, VZ-COLLECTION-001, VZ-GALLERY-001 | desktop-only and empty-album deletion not copied |
| Flickr groups | VZ-GROUP-001…003 | pool visibility as explicit grant |
| Flickr faves/comments/notes/tags/people/geo | VZ-FAVORITE-001, VZ-COMMENT-001, VZ-NOTES-001, VZ-TAG-001/002, VZ-PEOPLE-001, VZ-GEO-001 | |
| Flickr privacy/safety/content type/EXIF/download/licensing/guest passes | VZ-PRIVACY-001…003, VZ-NSFW-001, VZ-MEDIA-004, VZ-DOWNLOAD-001, VZ-LICENSE-001, VZ-ALBUM-002 | paywalls removed (Q-019, decided 2026-09-15) |
| Flickr following/feed/mail/notifications | VZ-FOLLOW-001, VZ-FEED-001, VZ-MESSAGE-001, VZ-NOTIFY-001 | |
| Flickr explore/search/stats/upload limits/sizes | VZ-EXPLORE-003, VZ-SEARCH-002, VZ-STATS-002, VZ-UPLOAD-013, VZ-MEDIA-001 | impression vs view (Q-020, decided 2026-09-15) |
| Flickr block/report/rules/deletion/export | VZ-BLOCK-001, VZ-REPORT-001, VZ-MOD-001, VZ-SPAM-001, VZ-ACCOUNT-002, VZ-EXPORT-001 | |
| Flickr API (39 namespaces) | vocabulary only; VZ-AUTH-008 scopes read/write/delete-style | OAuth 1.0a not copied |
| Requested integrations | VZ-STORAGE-003/006, VZ-AP-*, VZ-AT-*, VZ-IPFS-* | |
| Vidra meta mechanisms | VZ-INSTALL-*, VZ-TOPOLOGY-*, VZ-OPS-*, VZ-BACKUP-*, VZ-UPGRADE-*, VZ-CI-* | reimplemented; self-merge hook not carried |

## 14. Baseline-completeness gate

| Check | Status 2026-09-15 |
|---|---|
| Every Chevereto compare-page section reconciled (16/16) | DONE (ledger provenance) |
| Every admin-manual page (39/39) and user-manual page (34/34, 1 broken link) reconciled | DONE; broken link recorded FAILED |
| Flickr Help Center index enumerated (157) and workflow articles reconciled (76 fetched) | DONE; 25 documented gaps listed in the register |
| Roadmap/unreleased items excluded | DONE (V5 API, tags badge) |
| Paid/demo/private sources not inspected | CONFIRMED |
| Ambiguous behavior resolved or explicitly blocked | 43 questions: 38 DECIDED 2026-09-15 (Q-028 method only, numbers provisional), 1 OWNER ACTION (Q-032), 4 BLOCKED (Q-016 provider lane, Q-021/Q-022 credentials, Q-036 owner domain) |
| No unapproved scope reduction | CONFIRMED: videos, non-S3 storage, embedded uploader, imports, moderation integrations, multitenancy, operator features, forum plugins, banners, i18n all present in the full manifest; declines are listed for owner decision only |
| Ledger validity | 191 entries, unique IDs, dependencies resolve, no cycles, core closure holds (core never depends on full-only), all PLANNED/UNVERIFIED |
| Verification | UNVERIFIED — no test has run; the gate passes only when an independent reviewer re-reads the register against the live sources |

## 15. Smallest first runnable slice — `VZ-SLICE-01` (golden path)

**Outcome:** on a clean Ubuntu 24.04 amd64 host, an operator runs the installer, answers the wizard, boots the stack, claims the owner account, signs in, uploads a real JPEG and PNG, sees decoded thumbnails, opens the viewer, creates an album, adds the photos, sets the album to private, restarts the stack, and sees persisted state; a second account and an anonymous visitor cannot read the private original, derivatives, metadata, album contents or a cached response; the owner still can; a backup and a restore on a second clean host reproduce the state with matching checksums.

**Requirement IDs:** VZ-FOUND-001…008, VZ-CI-001…003, VZ-INSTALL-001…004, VZ-TOPOLOGY-001…003/006/007, VZ-OPS-001/002, VZ-BACKUP-001/002, VZ-AUTH-001/004, VZ-INSTALL-003, VZ-UPLOAD-001/003, VZ-QUOTA-001, VZ-JOBS-001, VZ-STORAGE-001, VZ-MEDIA-001/003/004, VZ-VIEWER-001, VZ-LIBRARY-001, VZ-ALBUM-001/002, VZ-PRIVACY-001, VZ-DESIGN-001, VZ-A11Y-001, VZ-RESPONSIVE-001, VZ-CONTROLS-001.

**Exact information its tests need (to be supplied or created before implementation):**
1. Target host: one disposable Ubuntu 24.04 amd64 VM (2 vCPU/4 GB minimum supported host; Q-028 numbers provisional until the first M0 run) with Docker Engine + Compose ≥ 2.24.4 or installer permission to install them; a second identical host for the restore rehearsal; SSH access; no production DNS.
2. Domain/TLS: a lab hostname with `VIZRA_TLS_MODE=internal` or `plain-http` (documented as lab-only); ACME not required.
3. Fixtures with recorded sha256 and license: one JPEG with EXIF orientation 6 and GPS tags; one PNG with alpha; one truncated JPEG; one oversized-dimension image; one polyglot/active SVG; one animated GIF (VZ-FOUND-007 manifest).
4. Accounts: owner (claimed via token), member B, anonymous session; the claim token read from the API log.
5. Budgets to assert: upload-to-thumbnail ≤ 30 s p95 on the reference host; restore checksum match 100%; RTO measured and recorded (Q-028 provisional targets; calibrated once by the first M0 run, then frozen).
6. Commands that must exist and be recorded in `docs/quality/COMMANDS.md`: install, setup (non-interactive answers file), deploy, doctor, backup, restore, the browser E2E command, and the compose render assertions.
7. Evidence to retain: install/deploy transcripts with exit codes, rendered compose model, `/readyz` responses, decoded thumbnail hashes, browser traces and 390/1440 light/dark screenshots, privacy negative-test output (member B and anonymous → 403/404 on every surface incl. object URLs and cached responses), backup manifest and restore checksum report, source SHA and image digests.

Non-goals of the slice: S3, comments/ratings/favorites, search, federation, analytics, imports, moderation queue, branding. They remain in the ledger and the milestone plan.
