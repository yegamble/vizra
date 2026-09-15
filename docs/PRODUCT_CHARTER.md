# Product charter — proposed baseline, 15 September 2026

## Outcome
A person other than the author can install Vizra on a clean supported server, claim the owner account, upload a real photograph, organize and share it with correct privacy, interact with other users, search, restart, upgrade, and recover from backup using only published instructions.

Vizra should feel calm, precise, image-first, and polished, taking inspiration from Apple's restraint rather than copying Apple's assets or reducing the application to a marketing-page mockup. Administration and bulk organization must remain information-dense enough to use productively.

## Non-negotiable scope
The user's requested stack is Go, Echo, PostgreSQL, sqlc, Redis, Docker; Next.js, TypeScript, Tailwind; Go/PostgreSQL/Redis search and ClickHouse analytics. Include uploads, comments, ratings, albums, tags, favorites, and a robust multi-user Flickr-like community. Target the audited functional union of Chevereto Free, Lite, and Pro, plus S3 including AWS and Backblaze, ActivityPub, AT Protocol, and IPFS.

Paid Chevereto editions mean their application capabilities are in scope; they do not automatically imply that Vizra users need subscriptions, payment processing, or paywalls. Do not invent a SaaS billing project.

## Scope discipline
The seed catalog is not an exhaustive parity certification. Prompt 00 must enumerate current public requirements, identify externally unverified behavior, and create atomic acceptance IDs. Preserve every candidate until independently resolved. A future release label cannot claim complete parity while required features remain missing, deferred, or unverified.

Use equivalent Go-native behavior where a competitor's feature is specific to PHP or its internal tools. Record the original capability and the proposed equivalent; require explicit approval for an intentional difference. Original implementation and original branding only. Source code reuse requires an actual license review and preserved notices; a public repository is not automatically permission to copy.

## Release profiles
`core`: a useful independently tested local/private gallery and community baseline, defined explicitly before its release.
`full`: every accepted product requirement, audited parity obligation, provider adapter, and advertised integration.

These profiles express claims, not loopholes. An optional-at-installation integration can still be required for full feature completion. Disabled means disabled, not implemented or verified. A core-only release is never called the completed application requested here.

## Operating ethos
Simple managed defaults, professionally capable controls, progressive scaling. Local disk without S3. Managed PostgreSQL/Redis by default or external services with no unnecessary local containers. ClickHouse and IPFS off by default; when enabled choose managed or external. A configured but invalid external service must not silently fall back to a fresh local database or storage destination.

No promises of infinite scale, zero bugs, universal provider support, guaranteed remote deletion, or production readiness without recorded evidence. Choose the supported deployment baseline early and exercise it throughout development.
