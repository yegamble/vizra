# ADR-005: Ingestion, quota, storage

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` requires bounded request, file, decoder and subprocess resources and
default-deny authorization over originals and derivatives, and forbids trusting
client MIME, filenames or remote URLs. `docs/ARCHITECTURE.md` fixes the pipeline
as authorize → reserve quota → create session → quarantine → validate real bytes
→ finalize → enqueue → publish. Quota accounting, key naming and the storage
capability surface cannot be changed cheaply once objects exist.

## Decision
### Upload session state machine
`upload_sessions` has a 24-hour TTL and these transitions:

- `active` → `uploaded`: every fixed-size 8 MiB chunk has been upserted at
  `incoming/<upload_id>/<n>` and finalize was called; the client-declared size
  **and sha256 are verified** at this point.
- `active` → `cancelled`: the client cancelled.
- `active` → `expired`: the TTL elapsed.
- `uploaded` → `validating`: the worker claimed the validation job.
- `validating` → `processing`: sniffing and bounds checks passed.
- `validating` → `failed`: the bytes were refused.
- `processing` → `published`: the derivative set is complete and the publish
  transaction committed.
- `processing` → `failed`: processing exhausted its attempts.
- `cancelled`, `expired`, `failed`: the same job releases the quota reservation and
  sweeps `incoming/<upload_id>/`.

Cross-device resume uses an opaque client `file_fingerprint`, never parsed.
Finalize is idempotent: a state compare-and-set, a partial unique index on the
active job, and a return of the in-flight job rather than a second one.

**Expiring uploads (Q-015) are a different mechanism from the 24-hour upload
session TTL above.** An uploader may set a published asset to expire; the
permitted range is **5 minutes to 1 year**; deletion is performed by a durable job
(ADR-004) **within 15 minutes of expiry**, so expiry is a scheduled deletion and
never a display-time filter; and the guarantee is documented as best-effort for
third-party copies already fetched, embedded or federated (VZ-UPLOAD-008). The
24-hour TTL governs only an unfinished `upload_sessions` row.

### Quota reservation ledger
Unlike Vidra's two point-in-time checks against a live `SUM`, Vizra keeps a
ledger: `quota_reservations(user_id, upload_id, bytes, state reserved|committed|released, expires_at)`.

1. **Reserve** — in the session-create transaction, a row is inserted as
   `reserved` and the session is created only if committed usage plus outstanding
   reservations plus the declared bytes fit the effective quota; otherwise no
   session is created.
2. **Commit** — in the publish transaction, the row moves to `committed` and
   `user_usage(bytes, files)` is incremented. Usage counters are transactional;
   there is no live `SUM`.
3. **Release** — on cancel, expiry or failure the same job moves the row to
   `released` and leaves usage untouched.
4. A reconcile job recomputes usage from the stored representations and alerts on
   drift.

Quotas are per-role defaults with per-user overrides (Q-007; default values
`[to confirm in M0]`). An admin may raise a limit at any time, and may not set one
below current usage without an explicit confirmation.

### Validation (worker only)
The api never decodes (Q-034). The worker performs a magic-byte sniff, a libvips
header read for dimensions and format, pixel, dimension, frame, memory and time
bounds, decoder-bomb refusal, and refusal of SVG and polyglot files — SVG is not
an image upload type — and only then a full decode into derivatives.

### Key grammar
Unlike Vidra, where every media key is a deterministic function of a public UUID,
keys carry unguessable randomness and never derive from the public short id:

- originals: `originals/<yyyy>/<mm>/<asset_uuid>/<128-bit random token>.<ext>`
- derivatives: `derived/<asset_uuid>/<processing_version>/<kind>-<token>.<ext>`
- in-flight chunks: `incoming/<upload_id>/<n>`

All three are rooted at the storage prefix the site resolver supplies (ADR-007).
Unguessability is defence in depth, not the control: authorization is still
per request. Private originals and private derivatives are proxied through the api
with `authz.Decide` and are never presigned. **Unlisted originals and derivatives
are likewise served through the api at token-bearing URLs** — the
`derived/.../<kind>-<token>` form above is already unguessable — with
`Cache-Control: private, no-store`, and they are **never CDN-cacheable** (Q-025).
Presigning is allowed for public derivatives only. Public derivatives may be served
directly or by a CDN with `?v=<visibility_version>` and are purged on any
visibility change. The presign TTL is a configuration key, not a compile-time
constant (default `[to confirm in M0]`).

### Storage adapter
`Backend{Put, Open (ranged), Delete, Exists, Stat}` plus optional capability
interfaces discovered by type assertion: `PrefixDeleter`, `ObjectLister`,
`Presigner`, `SizedPutter` (multipart), `ChecksumMode`
(`none|crc32c|sha256` trailer, per provider — Q-016) and
`BucketOwnershipMarker`. Implementations are local (with traversal-safe resolve)
and S3-compatible (`minio-go` v7; endpoint style, region, SSE flags). AWS and
Backblaze are qualified by live lanes in M4 and native adapters arrive in M5. The
`storage_locations` table is created in M0 by migration `0004_storage_locations`
with one `local` default row; `asset_files.storage_location_id` references that
row and is present in the first migration that creates the media tables, when they
arrive in M1 — multi-location routing itself is M4 (VZ-STORAGE-004).

### Orphans, GC and backups
The upload-expiry job sweeps `incoming/`, unlike Vidra where the uploads tree sits
outside every collector. Media GC ships only with an enable flag, a dry-run mode,
an orphan-ratio breaker, an age grace period and a bucket ownership marker.
Backups of originals are in scope: with local storage `backup.sh` includes the
originals tree and a checksum manifest; with S3 the runbook states that the
provider owns durability and `vizra backup verify` checks a manifest sample
against the bucket. Vizra never claims to snapshot an external bucket.

## Consequences
Positive: quota cannot drift into a silent overshoot, because reservations are
rows and commits are transactional; every leaked object has an owning sweep;
random keys make an enumerated public id useless; a per-request decision protects
private bytes even if a bucket is misconfigured. Negative: a row per upload plus a
reconcile job, and verifying the client sha256 on finalize costs a full read of
the assembled object. Risks: a reservation whose release never runs would hold
quota — hence `expires_at` and the drift alert; a capability interface that
degrades silently can delete a row and leave bytes, so a missing `PrefixDeleter`
must fail the sweep loudly. Later milestones must not break: reserve/commit/
release, no presigned URL for private bytes, keys never derived from public ids,
`storage_location_id` on every representation, GC's flag/dry-run/ratio/age/marker,
and originals in backup.

## Precedent
Copied from Vidra (survey citations): the session state machine, 24-hour TTL and
fixed 8 MiB chunk upsert with a list-based resume contract
(`C/internal/upload/service.go:42,57-79,590`), the opaque fingerprint
(`C/migrations/0080_upload_session_fingerprint.up.sql:13`), idempotent completion
by compare-and-set plus a partial unique index with a compensating delete on a
cancel race (`C/internal/httpapi/uploads.go:337`;
`C/internal/uploadfinalize/service.go:227-243`), capped readers and a dynamic
body limit (`C/internal/upload/service.go:324,624`;
`C/internal/httpapi/bodylimit.go:23`), the capability-by-type-assertion adapter
(`C/internal/storage/storage.go:32-43,52,64,92,189` with compile-time assertions
`C/internal/storage/s3.go:66-73`), traversal-safe local resolve
(`C/internal/storage/local.go:35`), hashing on the write stream
(`C/internal/storage/storage.go:209,224`), the never-presign rule for
credentialed or private delivery
(`C/internal/delivery/resolver.go:346`; `C/internal/httpapi/delivery.go:113`) and
the bucket ownership marker (`C/internal/storage/marker.go:27`).

Unlike Vidra: quotas have no reservation and no release, only two point-in-time
checks tolerating a one-file overshoot over a live `SUM`
(`C/internal/quota/service.go:184-195`; `C/migrations/0041_user_storage_quota.up.sql:7`);
chunk integrity is byte-length only with no client checksum verified end to end
(survey §3); media keys are deterministic functions of public UUIDs, so filenames
were never unguessable (`M/docs/productionization/risks.md:48-72`); the presign
TTL is a compile-time constant (`C/internal/delivery/resolver.go:23`); the uploads
tree is excluded from media GC and chunk-blob deletion is silently skipped when
the backend is not a `PrefixDeleter` while the row is deleted anyway
(`C/internal/mediagc/service.go:396-407`; `C/internal/upload/service.go:574-586`);
GC runs destructively with no age grace and a bypassable disable flag
(`M/docs/productionization/risks.md:24`;
`M/docs/productionization/release-readiness.md:6806,9625`); and originals are not
backed up in-product at all (`M/deploy/backup.sh:24-38`).

## Evidence and ratification
Q-007 (per-role defaults with per-user overrides), Q-015 (expiring uploads),
Q-016 (per-provider checksum configuration, BLOCKED until the Backblaze lane),
Q-025 (private and unlisted assets never CDN-cacheable) and Q-034 (no decode in
the api) in the `docs/OPEN_QUESTIONS.md` ratification record.

## Ledger IDs
VZ-UPLOAD-001, VZ-UPLOAD-002, VZ-UPLOAD-008, VZ-UPLOAD-013, VZ-QUOTA-001,
VZ-QUOTA-002, VZ-STORAGE-001, VZ-STORAGE-002, VZ-STORAGE-004, VZ-STORAGE-014,
VZ-BACKUP-001, VZ-BACKUP-004, VZ-MEDIA-008.

## M0 obligations
M0 owns no upload behaviour; the slice lands in M1 (VZ-UPLOAD-001, VZ-QUOTA-001,
VZ-STORAGE-001). What M0 does own here is migration `0004_storage_locations` — the
fourth and last M0 migration, after `0001_sites`, `0002_jobs` and
`0003_audit_events` — creating `storage_locations` with one `local` default row.
`asset_files.storage_location_id` references that row and is written in the first
media migration when the media tables arrive in M1, not in M0. What M0 must
otherwise reserve so this ADR stays implementable: the jobs table of ADR-004 for
the validation, publish, expiry and reconcile kinds, and the site-resolver storage
prefix.

Reservation only: `upload_sessions`, `quota_reservations`, `user_usage`, the S3
adapter and its capability interfaces, GC, and `vizra backup verify` arrive with
their own issues (VZ-STORAGE-002/004 in M4, GC and reconcile with VZ-MEDIA-009).
