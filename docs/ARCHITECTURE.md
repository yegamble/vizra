# Proposed architecture and decisions to ratify

This is a recommended starting architecture, not a description of existing code. Decisions are frozen in docs/adr/ (ADR-001…009, Proposed 2026-09-15, awaiting owner approval); this document remains the narrative overview and defers to the ADRs where they differ. Keep modular boundaries even when processes share a codebase.

## Repository and runtime
Owner decision 2026-09-15 (supersedes the kit's single-monorepo recommendation): Vizra mirrors the Vidra meta-repo shape. `vizra` is the meta repo (contract, spec, ledgers, compose files, `deploy/`, `env/`, `install.sh`, `bootstrap.sh`, `tests/`, `releases/`, CI fan-in). Component repos are checked out nested, gitignored here, and pinned detached at release tags on operator hosts. See docs/META_REPO.md for the install, topology and CI design.

```
vizra/                       # meta repo (this)
  AGENTS.md  docs/  .claude/  # contract, spec, ledgers, council
  docker-compose*.yml        # base, override, dev, prod overlay, external-* overlays   [planned]
  deploy/  env/  install.sh  bootstrap.sh  tests/  releases/  .github/                 [planned]
  vizra-core/                # nested checkout                                          [planned repo]
    cmd/api/  cmd/worker/  cmd/vizra/   # Echo API; media/import/outbox/analytics workers; installer/doctor/migrate/backup/restore CLI
    internal/  db/migrations/  db/queries/  api/openapi/  deploy/
  vizra-user/                # nested checkout: Next.js + TypeScript + Tailwind, packages/ui tokens + typed icons, generated API client [planned repo]
  vizra-search/              # nested checkout: internal Go search service on PostgreSQL FTS/trigram + Redis [planned repo; created in M0 as a real minimal service, SEARCH_MODE=off until M3 — Q-001 decided 2026-09-15]
```
One Go module per Go repo. Keep API, background worker and CLI as separate entry points sharing one binary/image in `vizra-core`. Search stays an internal service that returns ranked IDs only and is never a hard dependency; it is created in M0 as a real minimal service (`not_indexed` until M3) with the `sql`/`remote` boundary frozen in core's `internal/search` and search-owned tables in PostgreSQL schema `search` (Q-001, decided 2026-09-15). Do not add further services, a distributed queue cluster or Kubernetes without a measured need and owner approval.

## Ownership
PostgreSQL is authoritative for identity, sessions/revocation, authorization, media records, upload sessions, organization, social actions, quotas, moderation, and durable work. sqlc generates typed access from reviewed queries. Redis provides cache/rate-limit/ephemeral acceleration, not the sole copy of important state. ClickHouse stores analytical events/aggregates; it never authorizes media access or becomes necessary to complete an upload.

Next.js renders the application and uses the generated Go API contract. Keep same-origin API routing through the reverse proxy where practical. No second set of business rules or direct PostgreSQL reads in Next.js. Browser/SSR/server-component requests must retain correct identity without sharing private cache entries. Test the production build, runtime configuration, proxy behavior, and multi-instance cache invalidation before claiming scale-out support [NEXT].

## Core model
Media assets have stable internal IDs independent of object keys, slugs, URLs, or CIDs. Store distinct representations: original, sanitized display image, thumbnails, and optional video/360 derivatives. Retain provenance, dimensions, integrity checksum, processing version, and storage location. Separate local records from remote-publication mappings.

Albums have parent relationships with cycle prevention; asset membership is many-to-many. An album must not silently broaden a photo's permissions. Distinguish album-list visibility, asset permissions, and explicit share grants. Document cross-album access semantics before coding. Tags, categories, collections, and curated galleries are separate concepts where their behavior differs.

Likes are unified with favorites (Q-018, decided 2026-09-15); favorites and numeric ratings stay distinct. Use unique constraints and transactional updates for one-user/one-action rules. Tenant/site isolation must be an explicit design decision if multitenancy remains in the parity target; a user account is not a tenant. Decided 2026-09-15 (Q-008): database-per-tenant routed from a tenant registry; no tenant column or per-tenant schema in core; the M0 plumbing checklist is in the OPEN_QUESTIONS ratification record.

## Media workflow
Authorize upload → reserve quota → create upload session → transfer to quarantined storage → validate actual bytes and resource limits → finalize metadata → enqueue durable processing → publish only valid representations. Use bounded streaming, resumability, idempotent completion, checksum verification, atomic local publication, and orphan cleanup. Do not treat MIME headers or an object-store HEAD response as proof that media is safe. Do not equate S3 ETags with a universal content hash.

Use a mature image-processing engine behind a constrained worker adapter; evaluate libvips or another maintained implementation against format, metadata, animation, portability, security, and license needs. Go remains the application backend; external codecs do not justify rewriting the backend. Isolate resource-heavy decoders/subprocesses and test real output files, orientation, color profiles, metadata policy, and corruption. Keep advanced video support scoped to the parity requirement rather than rebuilding all of Vidra.

## Durable work and consistency
Write an outbox/job record in the same PostgreSQL transaction as the business mutation. Worker leases, bounded retries, idempotency keys, and dead-letter inspection must handle process crashes and repeated delivery. Search projections, thumbnails, federation, and analytics must catch up after outages without duplicating user actions. Define backlog retention and disk-pressure behavior; an unbounded queue is not a recovery strategy.

## Storage
Start with local storage and a capability-aware S3 adapter. AWS and Backblaze get real-provider qualification lanes in addition to a local emulator. Treat multipart, signed requests, CORS, endpoint styles, checksums, errors, deletion/versioning, and lifecycle behavior as contract tests, not assumptions of universal compatibility [B2]. Model multiple storage locations and migration jobs without tying an asset ID to a provider URL. Native GCS, Azure, OSS, Swift, SFTP, FTP, and legacy B2 remain separate parity obligations if the audit retains them; S3 is not their automatic substitute [CHEV-COMPARE].

## Optional integrations
ActivityPub is a separately tested server-to-server adapter with a declared interoperability profile, not just a Share button [AP, MASTODON]. AT Protocol is another protocol: distinguish login, Bluesky cross-posting, and native Vizra records/client indexing. Use current OAuth and stable DID identity, with custom Lexicons only in a namespace the operator owns [AT, AT-OAUTH, AT-LEXICON].

IPFS is opt-in public distribution, not an authenticated private-storage replacement. Publish only an explicitly approved public representation; never private originals or hidden metadata. Explain that unpinning cannot revoke copies held by third parties [IPFS, IPFS-PERSISTENCE]. Keep privacy checks authoritative before queue dispatch and again before publishing.

## Operations
The CLI may orchestrate Docker; the web/API process must not gain unrestricted Docker-socket access. Use local, authenticated, single-use installer owner claim and a one-time migration process from the same release image. Support a local-only HTTP development mode and a production HTTPS path. A degraded optional provider must not make the basic gallery unavailable or expose private content.

Backups include PostgreSQL, originals and required objects, manifests/configuration, protected keys, and enabled state that cannot be rebuilt. External services need explicit backup responsibility and verified recovery evidence, not a misleading claim that Vizra snapshots an externally managed database. Redis cache may be rebuilt; durable information must have another source. ClickHouse requires either verified backups or a declared replay source/retention guarantee sufficient to rebuild retained analytics.
