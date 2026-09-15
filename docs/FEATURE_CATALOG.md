# Seed feature catalog — NOT an exhaustive or verified parity inventory

This is a proposed organization of work. Prompt 00 must expand it into atomic requirements and reconcile the entire current official baseline. No item is implemented or tested by this kit. The categories below combine the user's explicit requirements, researched reference capabilities, and recommended safeguards; they are not a copied competitor checklist.

## F0 — installable foundation
One versioned release, secure setup/owner claim, development and production boot, API contracts, migration discipline, generated clients, real test fixtures, browser environment, diagnostics, required-check enforcement, and a clean-target test path. Define native AMD64 support first; separately qualify any ARM64 claim.

## F1 — identity and permissions
Registration/sign-in/out, account verification/recovery, roles, session revocation, two-factor authentication, profiles, account settings/export/deletion, optional identity providers, rate limits, API credentials, operator account management, and site/tenant boundaries. Decide private/unlisted/public asset, album, profile, and share-grant semantics before social features spread access logic.

## F2 — reliable media ingestion
Device uploads and accessible alternatives; progress, batching, resumability, retry/cancel; configurable guest behavior; quotas; duplicate handling; secure remote import; durable processing; format/decoder matrix; correct orientation and color; original and derivative storage; metadata display/stripping policy; expiration/deletion; resource bounds; browser decode and integrity checks. Retain audited video/360 obligations separately instead of quietly discarding them [CHEV-COMPARE].

## F3 — photography and organization
Personal library, public exploration, image viewer/zoom, metadata/captions/alt text, original/derivative downloads, albums/sub-albums, ordering/covers, collections, many-to-many membership, tags/categories, bulk changes, and private sharing. Proposed richer Flickr-like workflows include curated galleries, groups/discussions, and photographic metadata filters; confirm their exact scope rather than assuming a 'Flickr clone' is self-defining [FLICKR].

## F4 — community
Native comments/replies with edit/delete/report/moderation; numeric ratings; favorites; separate public-like semantics if retained; following/activity feed; notifications/preferences; anti-spam/blocking; public/private profile behavior; search/discovery and count accuracy; social action concurrency/idempotency. The user's explicit native comments and ratings requirements remain even when a competitor's mechanism differs.

## F5 — hosting, branding, and extension surfaces
Owner-defined theme/branding/pages, configurable navigation and terminology, embeds/oEmbed and generated share formats, API/desktop uploader integrations, controlled embedded uploader, watermarks, upload moderation, configurable registration/discovery/download behavior, and operator security controls. Preserve advanced integrations and tenant/operator capabilities from the baseline. Restrict privileged customization and unsafe features rather than exposing raw code execution [CHEV-FEATURES, CHEV-SERVICES].

## F6 — providers and imports
Local, S3/AWS/Backblaze, multiple storage locations, migration/reconciliation, private access, and CDN behavior. The full parity audit must account for native GCS, Azure, OSS, Swift, SFTP, FTP, and legacy B2 where still required; do not equate them automatically with S3. Qualify each advertised adapter. Import pipelines need dry runs, source mapping, permission preservation, checkpoints, resumability, reconciliation, and missing-data reports. Scope filesystem, Chevereto, Flickr, and other retained source adapters individually [CHEV-COMPARE, CHEV-IMPORT].

## F7 — search and analytics
Permission-aware search of the approved entities, relevance/filtering/facets, pagination, indexes/query-plan checks, cache invalidation, and realistic catalog tests. Basic local stats plus optional event-based ClickHouse dashboards with documented metric semantics, lag, replay/deduplication, retention, privacy, and service failure behavior. No analytics dependency on normal gallery transactions.

## F8 — open-network integrations
ActivityPub S2S profile and peer qualification. AT identity linking, optional Bluesky publication, and native Vizra records/indexing as separate deliverables. Public IPFS distribution with consent, pin/availability management, integrity, and explicit deletion limits. These are optional to run but mandatory to finish when retained in the full product manifest.

## F9 — operator-grade reliability
Managed/external/off service topology, safe installer rerun, doctor, health/readiness, logs/metrics/tracing, job administration, maintenance mode, backup and restore, prior-version upgrades, documented rollback/forward-recovery, security scanning, dependency maintenance, capacity/performance budgets, accessibility, visual quality, and support/runbooks. Retained operator features must have actual CLI/UI behavior and tests.

## Audit boundary
A few hundred acceptance cases may emerge; that is not a reason to open a few hundred vague issues at once. Keep the ledger complete and the active issue queue small. Each broad capability expands into independent observable cases. A feature can have supporting unit/integration/browser/provider tests without pretending that one test proves all behavior.
