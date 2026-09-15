# Vizra — Source Register: Protocols & Providers

**Observation date (all entries): 2026-09-15**
**Method:** WebFetch / WebSearch against live public documentation. Page-reported titles, dates and versions are recorded verbatim where the page showed them; `not shown on page` means the page displayed no such field. FAILED entries stay FAILED — they were not substituted with recalled knowledge.

---

## 1. ActivityPub (W3C)

| Field | Value |
|---|---|
| Exact URL | https://www.w3.org/TR/activitypub/ |
| Title | ActivityPub |
| Status / date shown | **W3C Recommendation 23 January 2018**; "Latest published version" = https://www.w3.org/TR/activitypub/ |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

Facts relevant to a photo-sharing implementation:
- Media upload is explicitly out of scope: "Servers _MAY_ support uploading document types to be referenced in activites, such as images, video or other binary data, but the precise mechanism is out of scope for this version of ActivityPub."
- Posting model is Create-wrapped: "The `Create` activity is used when posting a new object."
- Server must mint IDs for client-posted objects: "a server receiving an object posted to the outbox with no specified `id` _SHOULD_ allocate an object ID in the actor's namespace".
- Every actor needs two endpoints — an "`inbox:` How they get messages from the world" and an "`outbox:` How they send messages to others."
- Actors expose "A link to an ActivityStreams collection of the actors that follow this actor" (followers), plus following/liked collections.
- Trust posture: "Servers should not trust client submitted content"; client auth may use "OAuth 2.0 bearer tokens".

**Implication for Vizra:** ActivityPub alone does not define how a photo gets uploaded or how alt text / sensitivity travels. Those conventions must be taken from Mastodon and Pixelfed (items 2 and 3), not from the W3C REC.

---

## 2. Mastodon — ActivityPub profile & HTTP Signatures

### 2a. ActivityPub

| Field | Value |
|---|---|
| Exact URL | https://docs.joinmastodon.org/spec/activitypub/ |
| Title | ActivityPub - Mastodon documentation |
| Last updated shown | **March 30, 2026** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Attachments are typed objects in `attachment`; `Image`, `Audio` and `Video` are handled, with "some other Object types are converted as best as possible".
- Image attachment shape includes `"type": "Image"`, `"mediaType": "image/png"` and `"url"`.
- Alt text rides on the attachment's `summary` field (used as the media description).
- Blurhash extension is carried inline, e.g. `"blurhash": "UBL_:rOpGG-oBUNG,qRj2so|=eE1w^n4S5NH"`, to generate "colorful preview thumbnails".
- Focal point extension: `"focalPoint": [-0.55, 0.43]` — floats between -1.0 and 1.0.
- Content warnings use `"as:sensitive"`; media attached to such a post "will be hidden by default".
- Status-level activities processed: `Create`, `Delete`, `Like`, `Announce`, `Update`, `Undo`, `Flag`.
- Secure mode: "When a Mastodon server runs in secure mode, all cross-server HTTP requests to it must be signed" — including GETs for public resources.

### 2b. Security / HTTP Signatures

| Field | Value |
|---|---|
| Exact URL | https://docs.joinmastodon.org/spec/security/ |
| Title | Security - Mastodon documentation |
| Last updated shown | **July 20, 2026** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Signature scheme is the `draft-cavage-http-signatures` draft, being superseded by RFC 9421, but "This version of HTTP Signatures is still required for compatibility with older Mastodon versions."
- `Signature:` header carries `keyId`, `headers` and `signature`; for GET the headers list is typically `"(request-target) host date"`.
- For POST: "The `Digest:` header must also be included within the `headers` parameter of the `Signature:` header."
- Algorithm is RSA-SHA256, described as "RSASSA-PKCS1-v1_5 with SHA-256".
- Key discovery is via the actor's `publicKey` object: `id` (the keyId), `owner`, and `publicKeyPem`.
- Linked Data Signatures: "For this reason, it is not advised to implement support for LD Signatures" — still used for self-destruct and relays.

---

## 3. Pixelfed — federation / ActivityPub

### 3a. PRIMARY DOC — FAILED

| Field | Value |
|---|---|
| Exact URL | https://docs.pixelfed.org/technical-documentation/activitypub.html |
| Title | — |
| Status/date | — |
| Observed | 2026-09-15 |
| HTTP result | **FAILED — HTTP 404 Not Found** |

| Field | Value |
|---|---|
| Exact URL | https://raw.githubusercontent.com/pixelfed/docs/dev/src/spec/ActivityPub.md |
| Observed | 2026-09-15 |
| HTTP result | **FAILED — HTTP 404 Not Found** (attempted as a raw-source fallback for the above) |

### 3b. Reachable substitute

| Field | Value |
|---|---|
| Exact URL | https://docs.pixelfed.org/spec/ActivityPub.html |
| Title | ActivityPub \| Pixelfed Docs |
| Version / last updated shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Posts use `"type": "Note"` as the primary object type — **not** `Image`. Images are carried in `attachment`.
- Attachment shape observed: `{"type": "Image", "mediaType": "image/jpeg", "url": "https://pixelfed.test/storage/m/image.jpeg", "name": null}`.
- Alt text is the attachment `name` field — examples show `"name": "Night sky"` and `"name": "Sunrise at dawn"`; `null` when absent.
- Blurhash is included on attachments, e.g. `"blurhash": "UEE:0k_2oexa~pIVtRM{oH%L?bM{9F4nWB~W"`.
- Content warning flag is a plain boolean on the Note: `"sensitive": false`.
- Group activities address a collection target: `"target": {"type": "Collection", "id": "https://pixelfed.test/groups/.../wall"}`; docs note Pixelfed supports "federated Groups, allowing users to create and join communities".

| Field | Value |
|---|---|
| Exact URL | https://docs.pixelfed.org/ |
| Title | Pixelfed Docs |
| Version shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |
| Note | Only three top-level sections rendered: Introduction, Installation Guide, ActivityPub Documentation. **No dedicated Collections/Albums federation page was found.** |

**Albums / Collections — UNVERIFIED.** WebSearch results (2026-09-15) describe Pixelfed as shipping "albums, stories, collections, hashtags and a Mastodon-compatible API" and note that the ActivityPub federation documentation "is not yet finished". No official Pixelfed page reachable on 2026-09-15 documented an ActivityPub representation for Albums or Collections beyond the Groups `target: Collection` example above. **Do not assume Collections federate.** Treat Vizra albums as a local construct unless/until a Pixelfed or FEP source is found.

---

## 4. AT Protocol / Bluesky

### 4a. Protocol overview

| Field | Value |
|---|---|
| Exact URL | https://atproto.com/guides/overview |
| Title | Protocol Overview - AT Protocol |
| Status/date shown | © Copyright 2026; **no last-updated date shown** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- PDS role: "Personal Data Servers are your home in the cloud. They host your data, distribute it, manage your identity, and orchestrate requests to other services."
- Relay role: "Relays collect data updates from many servers in to a single firehose."
- AppView role: "App Views provide aggregated application data for the entire network."
- Data model: "User data is exchanged in signed data repositories. These repositories are collections of records which include posts, comments, likes, follows, etc."
- Identity: "Users in AT Protocol have permanent decentralized identifiers (DIDs) for their accounts" plus "a configurable domain name, which acts as a human-readable handle."
- Schemas: "A global schemas network called Lexicon is used to unify the names and behaviors of the calls across the servers."

### 4b. OAuth

| Field | Value |
|---|---|
| Exact URL | https://atproto.com/specs/oauth |
| Title | OAuth - AT Protocol |
| Status shown | Authoritative specification (not an implementation guide); the referenced client-metadata standard was still an **Internet Draft as of August 2024**; some security requirements may evolve with IETF drafts |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- "PKCE and PAR are required for all client types and Authorization Servers." S256 method only; `plain` prohibited.
- "Authorization Servers must support PAR and clients of all types must use PAR for Authorization Requests"; servers set `require_pushed_authorization_requests` true.
- "DPoP (with mandatory server issued nonces) is required to bind auth tokens to specific client software instances." ES256 mandatory for all parties.
- `client_id` must be "a fully-qualified web URL from which the client-metadata JSON document can be fetched" — HTTPS, no port, `http://localhost` dev exception; conventional path `oauth-client-metadata.json`.
- Token lifetimes: access tokens under 30 minutes (5–15 min preferred if non-revocable); public-client sessions capped at 2 weeks; confidential clients may run unlimited sessions with a 180-day refresh-token limit.

### 4c. Lexicon

| Field | Value |
|---|---|
| Exact URL | https://atproto.com/guides/lexicon |
| Title | Lexicons - AT Protocol |
| Status/date shown | © 2026; **no explicit status date** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- NSIDs use "reverse-DNS format", e.g. `app.bsky.feed.post`, `app.bsky.feed.like`.
- Frozen contract rule: "Once a Lexicon is published, it can never change its constraints."
- Only widening is allowed — you may "only add optional constraints to previously unconstrained fields."
- Breaking changes require a fork: "publish as a new lexicon under a new NSID."

**Implication for Vizra:** if Vizra publishes its own lexicon namespace for photo records, the schema is immutable at launch. Version the NSID, not the fields.

### 4d. Blobs

| Field | Value |
|---|---|
| Exact URL | https://atproto.com/specs/blob |
| Title | Blobs - AT Protocol |
| Status/date shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Blob reference shape: `$type: blob`, `ref` with `$link` (the CID), `mimeType`, `size`.
- Upload endpoint: `"com.atproto.repo.uploadBlob"` on the user's PDS; returns verified metadata.
- Size/mime limits are per-lexicon, but: "Servers may have their own generic limits...separate from any Lexicon-defined constraints."
- Ordering is mandatory — blobs must be uploaded before the record that references them; uploaded blobs sit in temporary, non-public storage.
- GC: "Servers should 'garbage collect' (delete) un-referenced temporary blobs", with "at least one hour a firm lower bound" grace period; a blob is deleted when no record references it, and one blob may be referenced by several records.
- CID form: CIDv1, `raw` codec (0x55), SHA-256, base32 with `b` prefix, e.g. `bafkreibjfgx2gprinfvicegelk5kosd6y2frmqpqzwqkg7usac74l3t2v4`.

### 4e. Sync / firehose

| Field | Value |
|---|---|
| Exact URL | https://atproto.com/specs/sync |
| Title | Sync - AT Protocol |
| Status/date shown | © 2026 Bluesky Social PBC; **no last-updated date shown** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Firehose endpoint: `"com.atproto.sync.subscribeRepos"`.
- Event types: `#commit` (CAR-format diffs), `#sync` (asserts current repo state), `#identity` (DID doc / handle change), `#account` (hosting status active/inactive).
- Ordering rule: "stream events can be processed concurrently across accounts, but they should be processed sequentially in-order for any given account."
- CAR usage: full repo export via `com.atproto.sync.getRepo`; `#commit` carries a "CAR slice" diff.
- Hard limits: max WebSocket frame "5 MBytes, measured as WebSocket frames"; commit events limited to 200 record operations; individual records capped at 1,000,000 bytes; `blocks` field max 2,000,000 bytes.

### 4f. Bluesky lexicon constraints (authoritative source files)

| Field | Value |
|---|---|
| Exact URL | https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/embed/images.json |
| Title | app.bsky.embed.images (lexicon JSON, `main` branch) |
| Version/date shown | **not shown** (repository `main` branch as of 2026-09-15) |
| Observed | 2026-09-15 |
| HTTP result | 200 OK (via 302 from github.com/.../raw/... → raw.githubusercontent.com) |

- `images` array **maxLength: 4** — four images per post maximum.
- `alt` field description: "Alt text description of the image, for accessibility."
- `aspectRatio` is `app.bsky.embed.defs#aspectRatio`.
- Image blob **maxSize: 2000000** bytes (~2 MB) with **accept: `["image/*"]`**.

| Field | Value |
|---|---|
| Exact URL | https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/embed/defs.json |
| Observed | 2026-09-15 · HTTP 200 OK |

- `aspectRatio` is an object, `required: [width, height]`, both integers with `minimum: 1`.
- "width:height represents an aspect ratio. It may be approximate, and may not correspond to absolute dimensions in any given unit."

| Field | Value |
|---|---|
| Exact URL | https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/post.json |
| Observed | 2026-09-15 · HTTP 200 OK (via 302 from github.com raw redirect) |

- `text`: **maxLength 3000** bytes, **maxGraphemes 300**.
- `langs`: maxLength 3.
- `tags`: max 8 items; each tag maxLength 640, maxGraphemes 64.
- `embed` union refs: `app.bsky.embed.images`, `app.bsky.embed.video`, `app.bsky.embed.gallery`, `app.bsky.embed.external`, `app.bsky.embed.record`, `app.bsky.embed.recordWithMedia`.
- Record key type: `tid`.

### 4g. docs.bsky.app — FAILED

| Field | Value |
|---|---|
| Exact URL | https://docs.bsky.app/ |
| Observed | 2026-09-15 |
| HTTP result | **FAILED — 301 Moved Permanently to https://bsky.network/ ; follow-up fetch returned empty body** |

| Field | Value |
|---|---|
| Exact URL | https://docs.bsky.app/docs/advanced-guides/posts |
| Observed | 2026-09-15 |
| HTTP result | **FAILED — 301 Moved Permanently to https://bsky.network/docs/advanced-guides/posts ; follow-up fetch returned empty body (twice)** |

**Note:** the numeric constraints in 4f come from the lexicon source files in `bluesky-social/atproto@main`, which are the normative definitions. The narrative developer guide could not be read on 2026-09-15.

---

## 5. IPFS

### 5a. Privacy and encryption

| Field | Value |
|---|---|
| Exact URL | https://docs.ipfs.tech/concepts/privacy-and-encryption/ |
| Title | Privacy and encryption \| IPFS Docs |
| Last updated shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- "All traffic on IPFS is public, including the contents of files themselves, unless they're encrypted."
- "DHT queries happen in public" and "it's possible that third parties could be monitoring this traffic to determine what CIDs are being requested, when, and by whom."
- Nodes publicly advertise the CIDs they hold, exposing PeerIDs in the DHT.
- IPFS encrypts transport between nodes but not content; implementers "choose whichever method is best for your project".
- Deanonymisation warning: "It's possible to do a DHT lookup on your PeerID and...find your IP address"; mitigations listed are "disabling reproviding, encrypting sensitive content, or running a private IPFS network."

**Hard constraint for Vizra:** this page alone satisfies the AGENTS.md rule that "Private media must never reach public IPFS". Only public, already-public-by-authorization originals/derivatives may be pinned to a public IPFS network.

### 5b. Persistence

| Field | Value |
|---|---|
| Exact URL | https://docs.ipfs.tech/concepts/persistence/ |
| Title | Persistence \| IPFS Docs |
| Last updated shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Core caveat: "IPFS guarantees that any content on the network is discoverable, it doesn't guarantee that any content is persistently available."
- Pinning is the mechanism that protects data from garbage collection; GC "attempts to reclaim memory occupied by objects that are no longer in use."
- MFS is offered as an alternative: "When working with files and directories, a better way may be to add them to the local Mutable File System (MFS)."
- Remote pinning services named on the page: 4EVERLAND Bucket, Filebase, Pinata.
- The page did **not** enumerate direct/recursive/indirect pin types — that distinction is NOT sourced here.

### 5c. Kubo RPC API

| Field | Value |
|---|---|
| Exact URL | https://docs.ipfs.tech/reference/kubo/rpc/ |
| Title | Kubo RPC API \| IPFS Docs |
| Version shown | **Generated from kubo v0.43.1** |
| Last updated shown | **2026-09-15** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Binds to `localhost` by default: "You should never expose it to the public internet, just like you would never expose a SQL database or other backend service."
- "NEVER EXPOSE THE RPC API TO THE PUBLIC INTERNET" — it exposes admin surface including `/api/v0/config`.
- The RPC API "grants admin-level access to your Kubo IPFS node."
- POST-only; GET requests return 405. Browser callers are subject to same-origin policy; CORS is configured via `API.HTTPHeaders.Access-Control-Allow-Origin`.
- Auth is bearer token: `Authorization: Bearer <secret>`.
- For anything internet-facing the docs recommend the implementation-agnostic HTTP Gateway instead.

### 5d. Pinning Services API

| Field | Value |
|---|---|
| Exact URL | https://ipfs.github.io/pinning-services-api-spec/ |
| Observed | 2026-09-15 |
| HTTP result | **PARTIAL — 200 OK but ReDoc SPA returned only the title "IPFS Pinning Service API"; no spec body rendered.** Content below was read from the raw OpenAPI source instead. |

| Field | Value |
|---|---|
| Exact URL | https://raw.githubusercontent.com/ipfs/pinning-services-api-spec/main/ipfs-pinning-service.yaml |
| Title | IPFS Pinning Service API |
| Version shown | **1.0.0** (OpenAPI `info.version`) |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Paths: `GET /pins`, `POST /pins`, `GET /pins/{requestid}`, `POST /pins/{requestid}` (replace), `DELETE /pins/{requestid}`.
- Pin status enum: `queued`, `pinning`, `pinned`, `failed`.
- Auth: bearer token — `Authorization: Bearer <access-token>`.
- `origins` = client-supplied multiaddrs of known sources, to speed initial transfer; `delegates` = service-supplied multiaddrs of temporary retrieval peers.
- Pagination: default limit 10, max 1000, latest-to-oldest by creation time, cursor via `before`/`after`.

---

## 6. Object storage — Backblaze B2 and AWS S3

### 6a. Backblaze S3-compatible API

| Field | Value |
|---|---|
| Exact URL | https://www.backblaze.com/docs/cloud-storage-s3-compatible-api |
| Title | S3-Compatible API |
| Last updated shown | **2025-12-10T18:42:43Z** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Unsupported list, verbatim: "The S3-Compatible API does not currently support the following features: ACLs, IAM Roles, Object Tagging, Website Configuration, Browser-based uploads to pre-signed URLs using POST".
- Object-level ACLs absent: "Object-level ACLs are not supported. A Get Object ACL call returns the ACL for the bucket containing the object."
- Put Bucket ACL is limited to `private` and `public-read` only.
- Presigned URLs supported for download and upload: "You can generate pre-signed URLs using the AWS CLI, AWS Tools for PowerShell, s3cmd, and AWS SDKs." — **but browser POST form uploads to a presigned URL are NOT supported** (see unsupported list). This directly constrains Vizra's direct-to-bucket browser upload design: use presigned PUT, not presigned POST.
- SSE-B2 and SSE-C supported; Copy Object supported; IPv6 supported.
- Get Object Tagging "returns a set of empty tags" for compatibility.

| Field | Value |
|---|---|
| Exact URL | https://www.backblaze.com/apidocs/introduction-to-the-s3-compatible-api |
| Title | Introduction to the S3-Compatible API |
| Last updated shown | **December 11, 2025** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- "Buckets in Backblaze B2 are versioned by default. Because buckets are versioned, when a file is deleted by referencing the name, only the most recent version of that file is deleted."
- "The S3-Compatible API supports only v4 signatures for authentication, and v2 signatures are not supported at this time."
- "IAM roles, Object Tagging, and Website configuration are not currently supported." Also "SSE-KMS encryption is not currently supported."
- Multipart part-size limits, max object size, and checksum-header behaviour are **not stated on this page**.

| Field | Value |
|---|---|
| Exact URL | https://www.backblaze.com/docs/cloud-storage-large-files |
| Title | Cloud Storage Large Files |
| Last updated shown | **August 29, 2023** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Part size: "Each part can be anywhere from 5 MB to 5 GB".
- File size: "Large files can range in size from 5 MB to 10 TB" (max 10 TB, vs AWS 48.8 TiB).
- "Each large file must consist of at least two parts"; no maximum part count stated.
- Per-part integrity is mandatory in the B2 Native large-file flow: "When you upload a file part, you must provide a SHA-1 checksum". Whole-file: "Large files do not require SHA-1 checksums on the entire file, but Backblaze recommends that you add one".
- **Caveat:** this page describes B2 Native large files, not the S3-compatible multipart path; the S3-compatible checksum header matrix was not found on any reachable Backblaze page on 2026-09-15 — record as UNVERIFIED.

| Field | Value |
|---|---|
| Exact URL | https://www.backblaze.com/docs/cloud-storage-enable-object-lock-with-the-s3-compatible-api |
| Title | How to Enable Object Lock with the Backblaze B2 S3-Compatible API |
| Last updated shown | **June 28, 2023** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Object Lock IS supported via the S3-compatible API — "compliance and governance lock modes", retention periods, legal hold, and default bucket retention.
- Enabling on an existing bucket requires the `x-amz-bucket-object-lock-token` header with value `1` on Put Object Lock Configuration.

| Field | Value |
|---|---|
| Exact URL | https://www.backblaze.com/docs/cloud-storage-s3-compatible-api-supported-operations |
| Observed | 2026-09-15 |
| HTTP result | **FAILED — HTTP 404 Not Found** (guessed path for a consolidated supported-operations table; no such page) |

### 6b. AWS S3 multipart upload

| Field | Value |
|---|---|
| Exact URL | https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html |
| Title | Uploading and copying objects using multipart upload in Amazon S3 |
| Version/date shown | "latest" userguide; **no date on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Threshold: "It's a best practice to use multipart upload for objects that are 100 MB or larger instead of uploading them in a single operation."
- No expiry on an initiated upload — "After you initiate a multipart upload, there is no expiry; you must explicitly complete or stop the multipart upload."
- Cost leak: "you must either complete or stop the multipart upload to stop incurring charges for storage of the uploaded parts." Mitigation: "configure a lifecycle rule to delete incomplete multipart uploads after a specified number of days by using the `AbortIncompleteMultipartUpload` action."
- **Trap for checksummed uploads:** "the part numbers for each part upload (in the multipart upload) must use consecutive part numbers and begin with 1" — non-consecutive part numbers with checksums cause "an `HTTP 500 Internal Server` error".
- If no checksum is specified, "Amazon S3 automatically uses the CRC-64/NVME (`CRC64NVME`) checksum algorithm."
- Mismatch on a full-object checksum fails the request with a `BadDigest` error.
- Completion ETag is not an MD5: "This ETag is not necessarily an MD5 hash of the object data" — a checksum of checksums.

| Field | Value |
|---|---|
| Exact URL | https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html |
| Title | Amazon S3 multipart upload limits |
| Observed | 2026-09-15 · HTTP 200 OK |

| Item | Specification |
|---|---|
| Maximum object size | 48.8 TiB |
| Maximum number of parts per upload | 10,000 |
| Part numbers | 1 to 10,000 (inclusive) |
| Part size | 5 MiB to 5 GiB; "There is no minimum size limit on the last part" |
| Max parts returned per list parts request | 1000 |
| Max multipart uploads returned per list request | 1000 |

### 6c. AWS S3 object integrity / checksums

| Field | Value |
|---|---|
| Exact URL | https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html |
| Title | Checking object integrity in Amazon S3 |
| Observed | 2026-09-15 · HTTP 200 OK |

- Supported algorithms: `CRC64NVME`, `CRC32`, `CRC32C`, `SHA1`, `SHA256`, `MD5`, `XXHASH64`, `XXHASH3`, `XXHASH128`, `SHA512`.
- Default: "The `CRC64NVME` checksum algorithm is the default checksum algorithm used for checksum calculations."
- Server-side verification: S3 "independently calculates a checksum value of the object on the server-side, and validates it with the provided value before storing the object".
- MD5 is client-supplied only: "You can provide a precalculated MD5 checksum using the `x-amz-checksum-md5` header. AWS SDKs do not automatically calculate MD5 checksums."
- "The legacy `Content-MD5` header remains available for single part uploads using SSE-S3 encryption."
- Checksum **type** matters for multipart: full-object (CRC64NVME, CRC32, CRC32C) vs composite (SHA-1/SHA-256/MD5/XXHash/SHA-512 — every part-level checksum must be sent in `CompleteMultipartUpload`).

**Portability note for Vizra:** the AWS default `CRC64NVME` and the `x-amz-checksum-*` family are not confirmed supported on Backblaze (see 6a — UNVERIFIED). Any S3 abstraction must let the checksum algorithm be configured per-provider and must not hard-code presigned POST.

---

## 7. ClickHouse

### 7a. Backup and restore

| Field | Value |
|---|---|
| Exact URL | https://clickhouse.com/docs/operations/backup |
| Title | Backup and restore in ClickHouse |
| Last updated / version shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- SQL-native: `BACKUP TABLE test.table TO Disk('backups', 'filename.zip')`, with matching `RESTORE`; sync or async execution.
- Targets tables, databases, dictionaries, views, temporary tables, with optional renaming.
- Destinations: local `File()`, configured `Disk()`, `S3()` endpoint (S3 or S3-compatible), and `AzureBlobStorage()`.
- Incremental backups via the `base_backup` setting pointing at a previous backup; reduces time and storage.
- Other settings: compression method, password protection for ZIP archives, concurrency control in server config.
- Operational directive: "Whatever backup approach you choose, make sure to automate the restore process as well, and practice it on a spare ClickHouse cluster regularly."
- `allow_backup_broken_tables`, filesystem-snapshot guidance and `clickhouse-backup` were **not present** on this page.

### 7b. ReplacingMergeTree deduplication

| Field | Value |
|---|---|
| Exact URL | https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree |
| Title | ReplacingMergeTree table engine |
| Last updated shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Timing is non-deterministic: "Data deduplication occurs only during a merge. Merging occurs in the background at an unknown time, so you can't plan for it."
- Dedup key: "Uniqueness of rows is determined by the `ORDER BY` table section, not `PRIMARY KEY`."
- `ver` column (UInt*, Date, DateTime, DateTime64) — retains the max version, or the most recently inserted row on ties.
- `is_deleted` (UInt8, 1 = deleted, 0 = state) marks tombstones during merge; requires `ver`.
- Correctness caveat: "Queries can, therefore, produce incorrect answers due to update and delete rows being considered in queries." `FINAL` is required for correctness.
- Blunt warning: "Thus, `ReplacingMergeTree` is suitable for clearing out duplicate data in the background in order to save space, but it does not guarantee the absence of duplicates."

**Implication for Vizra:** ReplacingMergeTree must NOT be treated as an idempotency guarantee for analytics counts (views, favourites). Any count exposed in a UI or authorization decision must be either `FINAL`-qualified or reconciled from PostgreSQL, which "owns transactional truth".

---

## 8. Core stack versions

### 8a. Next.js self-hosting

| Field | Value |
|---|---|
| Exact URL | https://nextjs.org/docs/app/guides/self-hosting |
| Title | How to self-host your Next.js application |
| Version shown | **version: 16.3.5** (page frontmatter) |
| lastUpdated shown | **2026-08-25** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Reverse proxy recommended over direct exposure — it handles "malformed requests, slow connection attacks, payload size limits, rate limiting, and other security concerns".
- `next/image` optimization "works self-hosted with zero configuration when deploying using `next start`"; on glibc Linux it "may require additional configuration to prevent excessive memory usage" (sharp memory allocator).
- Env vars: "By default, environment variables are only available on the server"; `NEXT_PUBLIC_` vars "will be inlined into the JavaScript bundle during `next build`".
- ISR/page cache defaults to local disk per instance; multi-instance requires a custom `cacheHandler` plus `cacheMaxMemorySize: 0`, and `refreshTags()` for cross-instance tag invalidation.
- Multi-instance also requires a shared `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` (base64, 16/24/32 bytes) or you get "Failed to find Server Action" errors, plus a `deploymentId` for version-skew protection.
- Streaming behind nginx needs `X-Accel-Buffering: no`; graceful shutdown on SIGINT/SIGTERM with a 10–30s drain for `after()` callbacks.

### 8b. Echo

| Field | Value |
|---|---|
| Exact URL | https://echo.labstack.com/docs |
| Observed | 2026-09-15 |
| HTTP result | **REDIRECT — page body is only "Redirecting to: /guide/quickstart/"; no content.** Resolved below. |

| Field | Value |
|---|---|
| Exact URL | https://echo.labstack.com/guide/quickstart/ |
| Title | Quickstart \| Echo |
| Version shown | **v5** — import path `github.com/labstack/echo/v5` |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- "Echo requires **Go 1.25 or newer**".
- Install: `go get github.com/labstack/echo/v5`.
- **Conflict with repo contract:** `AGENTS.md`/council agent definitions reference **Echo v4**. The live docs site now presents **v5** as current. This is a decision Vizra must make explicitly (pin v4 and document why, or migrate) — do not let it drift silently.

### 8c. sqlc

| Field | Value |
|---|---|
| Exact URL | https://docs.sqlc.dev/en/latest/ |
| Title | sqlc Documentation — sqlc |
| Version shown | "latest" in URL only; **no version number on the landing page** |
| Observed | 2026-09-15 · HTTP 200 OK |
| Facts | Generates "fully type-safe idiomatic Go code" from SQL; engines documented: MySQL, PostgreSQL, SQLite; plugin support documented under "Using plugins". |

| Field | Value |
|---|---|
| Exact URL | https://docs.sqlc.dev/en/latest/reference/changelog.html |
| Title | Changelog — sqlc |
| Version shown | **v1.31.1, "released 2026-04-22"** (top of changelog) |
| Observed | 2026-09-15 · HTTP 200 OK |

### 8d. PostgreSQL — full text search

| Field | Value |
|---|---|
| Exact URL | https://www.postgresql.org/docs/current/textsearch-intro.html |
| Title | PostgreSQL: Documentation: 18: 12.1. Introduction |
| Version shown | **PostgreSQL 18 (current)** |
| Observed | 2026-09-15 · HTTP 200 OK |

- Types: `tsvector` (preprocessed document), `tsquery` (processed query); `@@` returns true on match.
- Functions: `to_tsvector()`, `plainto_tsquery()`, `phraseto_tsquery()`.
- Query operators: `&` AND, `|` OR, `!` NOT, `<->` FOLLOWED BY, `<N>` generalized FOLLOWED BY.
- "GIN and GiST indexes accelerate full text searches".
- Language handling is configuration-driven — stop words, synonyms and parsing come from text search configurations; `default_text_search_config` selects the default.

### 8e. PostgreSQL — pg_trgm

| Field | Value |
|---|---|
| Exact URL | https://www.postgresql.org/docs/current/pgtrgm.html |
| Title | F.35. pg_trgm — support for similarity of text using trigram matching |
| Version shown | **PostgreSQL 18** |
| Observed | 2026-09-15 · HTTP 200 OK |

- `similarity(text, text)` → real, 0 (dissimilar) to 1 (identical).
- `word_similarity(text, text)` "Returns a number that indicates the greatest similarity between the set of trigrams in the first string and any continuous extent of an ordered set of trigrams in the second string"; `strict_word_similarity` forces word boundaries.
- Thresholds: `%` uses `pg_trgm.similarity_threshold` (default 0.3); `<%`/`%>` use `pg_trgm.word_similarity_threshold` (default 0.6); `<<%`/`%>>` use `pg_trgm.strict_word_similarity_threshold` (default 0.5).
- Index support: GIN `gin_trgm_ops`; GiST `gist_trgm_ops` with `siglen` 1–2024 bytes, default 12 — e.g. `CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops(siglen=32));`
- Accelerates `LIKE`, `ILIKE`, `~`, `~*` and `=`.
- Performance caveat: "A pattern with no extractable trigrams will degenerate to a full-index scan" — matters for short tag/username autosuggest queries.

### 8f. Redis

| Field | Value |
|---|---|
| Exact URL | https://redis.io/docs/latest/ |
| Observed | 2026-09-15 |
| HTTP result | **FAILED — HTTP 404 Not Found** |

| Field | Value |
|---|---|
| Exact URL | https://redis.io/docs/latest/get-started/ |
| Title | Open Source (Redis docs, "Get started with Redis Open Source") |
| Version shown | **not shown on page** |
| Observed | 2026-09-15 · HTTP 200 OK |
| Facts | Describes Redis as in-memory data store / cache / vector DB / document DB / streaming engine / message broker; built-in replication and on-disk persistence; core repo at github.com/redis/redis. No version or license string on this page. |

| Field | Value |
|---|---|
| Exact URL | https://github.com/redis/redis/releases |
| Title | Releases · redis/redis |
| Version shown | **8.10.1**, released **August 17** (16:44 UTC), flagged "Update urgency: `SECURITY`: There are security fixes in the release." |
| Observed | 2026-09-15 · HTTP 200 OK |

| Field | Value |
|---|---|
| Exact URL | https://redis.io/legal/licenses/ |
| Title | Licenses \| Redis |
| Date shown | **not shown** (page referenced an event dated "Sep. 09, 2026") |
| Observed | 2026-09-15 · HTTP 200 OK |

- Tri-license from Redis 8: "A user may select one of the following three license options to use Redis Open Source (starting with Redis 8) and subsequent versions: the Redis Source Available License v2 (RSALv2), the Server Side Public License v1 (SSPLv1), and the GNU Affero General Public License v3 (AGPLv3)."
- Version → license table on the page: `<= 7.2` → `BSD-3-Clause`; `7.4.x – 7.8.x` (Redis Community Edition) → `RSALv2 or SSPLv1`; `>= 8.0.0` (Redis Open Source) → `RSALv2 or SSPLv1 or AGPLv3`.

**Licensing note for a self-hosted product:** Redis >= 8 is NOT BSD. For Vizra's "self-hosted photo-community application" distribution, AGPLv3 is the only OSI-approved option of the three, and it is a network-copyleft licence. If Vizra ships Redis in its Compose topology this needs a deliberate legal decision (or a BSD-licensed fork such as Valkey — **not verified in this pass**).

### 8g. Go

| Field | Value |
|---|---|
| Exact URL | https://go.dev/doc/devel/release |
| Title | Release History - The Go Programming Language |
| Version shown | **go1.27.0, released 2026-08-19**; latest minor **go1.27.1, released 2026-09-01** |
| Observed | 2026-09-15 · HTTP 200 OK |

- Support policy: "Each major Go release is supported until there are two newer major releases."
- go1.27.1 fixes cover cgo, the compiler, the runtime, `go fix`, and packages including `database/sql`, `debug/elf`, `encoding/json`, `net/http`, `os`, `simd`, `simd/archsimd`.
- Cross-check: Echo v5 requires Go 1.25 or newer — satisfied by go1.27.x.

### 8h. libvips and Go bindings

| Field | Value |
|---|---|
| Exact URL | https://www.libvips.org/ |
| Title | libvips – A fast image processing library with low memory needs |
| Version shown | **libvips 8.18, released December 4, 2025** |
| Observed | 2026-09-15 · HTTP 200 OK |

- License: **LGPL-2.1-or-later**.
- Formats listed: JPEG, JPEG 2000, JPEG XL, TIFF, PNG, WebP, **HEIC, AVIF**, FITS, Matlab, OpenEXR, PDF, SVG, HDR, PPM/PGM/PFM, **GIF**, Analyze, NIfTI, DeepZoom, OpenSlide (DICOM via ImageMagick/GraphicsMagick).
- "demand-driven, horizontally threaded"; "libvips runs quickly and uses little memory".
- "around 300 operations" spanning arithmetic, histograms, convolution, morphology, colour, resampling, statistics.

| Field | Value |
|---|---|
| Exact URL | https://github.com/davidbyttow/govips and https://github.com/davidbyttow/govips/releases |
| Title | govips — "A lightning fast image processing and resizing library for Go" |
| Version shown | **v2.18.0, published 01 Apr** (year not rendered on the releases list; observed 2026-09-15) |
| Observed | 2026-09-15 · HTTP 200 OK |

- License: **MIT**. Required libvips: **8.14+** (raised from 8.10 in v2.18.0).
- Formats handled: JPEG, PNG, WebP, **AVIF**, **HEIF/HEIC**, GIF, TIFF, PDF; "193+ operations".
- v2.18.0 notes: new leak detector (`OpenImageRefs()`, `AssertNoLeaks(t)`), `ImageRef` decomposed into eight files, **WebP shrink-on-load** and **animated AVIF detection**, memory-leak fixes, panics replaced with error returns.
- Claim on the page: libvips is "generally 4-8x faster than other graphics processors such as GraphicsMagick and ImageMagick".

| Field | Value |
|---|---|
| Exact URL | https://github.com/h2non/bimg (metadata via api.github.com/repos/h2non/bimg) |
| Title | bimg — "Go package for fast high-level image processing powered by libvips C library" |
| Version shown | latest tag **v1.1.9** |
| Last push | **2025-01-23T09:51:09Z** |
| Observed | 2026-09-15 · HTTP 200 OK |
| Facts | License MIT; archived: **false**; ~3,031 stars. Last code push is ~20 months before observation date — lower maintenance velocity than govips (v2.18.0, libvips 8.14+). |

| Field | Value |
|---|---|
| Exact URL | https://github.com/disintegration/imaging (metadata via api.github.com/repos/disintegration/imaging) |
| Title | imaging — "Imaging is a simple image processing package for Go" / "Package imaging provides basic image processing functions (resize, rotate, crop, brightness/contrast adjustments, etc.)." |
| Version shown | latest tag **v1.6.2** |
| Last push | **2023-09-21T02:16:10Z** |
| Observed | 2026-09-15 · HTTP 200 OK |
| Facts | License MIT; archived: **false** (but no code push in ~3 years — effectively dormant); ~5,754 stars; pure Go, stdlib-based. Repo page showed JPEG and PNG examples; **no AVIF/HEIC/animated support documented**. |

**Decision input for Vizra:** libvips-backed govips is the only observed option covering AVIF/HEIC/animated and shrink-on-load. `imaging` is pure Go but dormant and format-limited — usable as a fallback for JPEG/PNG only, not as the primary derivative pipeline. Note the libvips LGPL-2.1-or-later obligation when distributing container images.

---

## 9. OWASP cheat sheets

| Field | Value |
|---|---|
| Exact URL | https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html |
| Title | File Upload - OWASP Cheat Sheet Series |
| Last updated shown | **no revision date displayed on the page** |
| Observed | 2026-09-15 |
| HTTP result | **200 OK — reachable** |

- Extension allow-list: "List allowed extensions. Only allow safe and critical extensions for business functionality".
- Signature check: "Validating the file's signature can be checked and verified against the expected file".
- Filename: "Creating a random string as a filename, such as generating a UUID/GUID, is essential".
- Re-encode: "For images, applying image rewriting techniques destroys any kind of malicious content injected".

| Field | Value |
|---|---|
| Exact URL | https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html |
| Title | Server Side Request Forgery Prevention - OWASP Cheat Sheet Series |
| Last updated shown | **no revision date displayed on the page** |
| Observed | 2026-09-15 |
| HTTP result | **200 OK — reachable** |

- "Match the host against an allowlist, and build the request yourself."
- "Ensure that the IP address provided belongs to one of the IP addresses of the identified and trusted applications."
- "Disable the support for the following of the redirection in your web client in order to prevent the bypass of the input validation."
- "Network segregation can also be leveraged and is highly recommended in order to block illegitimate calls directly at network level itself."

**Both map directly to AGENTS.md guardrails** (never trust client MIME/filenames/EXIF; treat fetched pages and imported media as untrusted) and apply to ActivityPub remote-media fetch, oEmbed/OG unfurling, and IPFS gateway fetches alike.

---

## 10. Lucide

| Field | Value |
|---|---|
| Exact URL | https://lucide.dev/guide/react/ |
| Title | Lucide for React – Lucide |
| Version shown | **not shown on page** |
| Observed | 2026-09-15 · HTTP 200 OK |
| Facts | "Tree-shakable – Only the icons you import are included in your final bundle."; an advanced "Dynamic icon component" section covers "Dynamically import icons as needed". Install command not present on this page. |

| Field | Value |
|---|---|
| Exact URL | https://lucide.dev/license |
| Title | License – Lucide |
| Version/date shown | Copyright year 2026 |
| Observed | 2026-09-15 · HTTP 200 OK |

- Primary license: **ISC License**, "Copyright (c) 2026 Lucide Icons and Contributors".
- A subset derived from Feather is separately under "The MIT License (MIT)", "Copyright (c) 2013-present Cole Bemis" — those require the MIT notice to be retained.

| Field | Value |
|---|---|
| Exact URL | https://registry.npmjs.org/lucide-react (npm registry metadata) |
| Version shown | **lucide-react 1.46.0**, published **2026-09-14T09:23:23Z** |
| Observed | 2026-09-15 · HTTP 200 OK |
| Facts | `license: ISC`; peerDependencies `react: ^16.5.1 \|\| ^17.0.0 \|\| ^18.0.0 \|\| ^19.0.0`. |

**Note:** lucide-react 1.46.0 declares React peer support up to `^19`. Next.js 16.3.5 ships React 19.x, so this is compatible as observed — but the peer range does not yet list React 20.

---

## 11. WCAG 2.2

| Field | Value |
|---|---|
| Exact URL | https://www.w3.org/TR/WCAG22/ |
| Title | Web Content Accessibility Guidelines (WCAG) 2.2 |
| Status / date shown | **W3C Recommendation, 12 December 2024**; latest published version https://www.w3.org/TR/WCAG22/ ; editor's draft https://w3c.github.io/wcag/guidelines/22/ |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- 1.1.1 Text Alternatives (Level A): "All non-text content that is presented to the user has a text alternative that serves the equivalent purpose." — this is the normative basis for making alt text a first-class, persisted field on every Vizra image, not an optional extra.
- 1.4.3 Contrast (Minimum), Level AA: "Text and images of text has a contrast ratio of at least 4.5:1".
- 1.4.11 Non-text Contrast, Level AA: "Visual presentation of user interface components and graphical objects have a contrast ratio of at least 3:1 against adjacent color(s)" — applies to icon-only controls over photo thumbnails.
- 2.5.8 Target Size (Minimum) is a Level AA criterion in WCAG 2.2 — relevant to gallery/lightbox touch controls.
- Conformance levels: A, AA, AAA.

---

## 12. Docker Compose

| Field | Value |
|---|---|
| Exact URL | https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/ |
| Title | Merge Compose files |
| Date shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Order matters: files are processed "in the order they're specified on the command line. Subsequent files may merge, override, or add to their predecessors."
- Merge rules by field type: single-value fields (image, command) replace; multi-value fields (ports, expose, dns) concatenate; key-value fields (environment, labels) override per key; volume/device mounts key off the container mount path.
- Path resolution trap: "All paths in the files are relative to the base Compose file (the first Compose file specified with `-f`)" — relative paths in an override file do NOT resolve relative to that file's own directory.
- This page did **not** document `!reset` / `!override`.

| Field | Value |
|---|---|
| Exact URL | https://docs.docker.com/reference/compose-file/merge/ |
| Title | Merge Compose files (Compose file reference) |
| Date shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- `!reset` removes elements — "An override Compose file can be used to remove elements from your application model", setting the attribute to its default or `null`. Syntax: `ports: !reset []` and `environment:\n  FOO: !reset null`.
- `!override` lets you "fully replace an attribute, bypassing the standard merge rules". Syntax: `ports: !override\n  - "8443:443"`.
- **Minimum Compose version for `!reset` / `!override`: NOT STATED on the page — UNVERIFIED.** Two different Docker doc pages were read on 2026-09-15 and neither gave a version floor. Vizra must pin and test a minimum Compose version empirically rather than cite one.

| Field | Value |
|---|---|
| Exact URL | https://docs.docker.com/compose/how-tos/profiles/ |
| Title | Using profiles with Compose |
| Date shown | **not shown on page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Assignment: services take a `profiles` attribute accepting "an array of profile names", e.g. `profiles: [debug]`.
- Activation: `docker compose --profile debug up`, or `COMPOSE_PROFILES=debug docker compose up`; multiples via repeated flags or comma-separated `COMPOSE_PROFILES=frontend,debug`.
- Services with no profile "are always enabled and automatically started" — the core topology.
- `depends_on` targets start automatically when a profiled service is explicitly named; if those dependencies carry their own profiles they must share the profile, be started separately, or have no profile.
- **Minimum Compose version: NOT STATED — UNVERIFIED.**

---

## 13. Embed / share formats

| Field | Value |
|---|---|
| Exact URL | https://oembed.com/ |
| Title | oEmbed |
| Version / date shown | **Version 1.0**; no publication date shown |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Four response types: **photo** — "used for representing static photos"; **video** — "used for representing playable videos"; **link** (generic data, no url/html required); **rich** — "used for rich HTML content that does not fall under one of the other categories".
- Photo type required fields: `url` — "The source URL of the image. Consumers should be able to insert this URL into an `<img>` element."; `width` — "The width in pixels of the image specified in the `url` parameter."; `height` — corresponding height.
- Discovery: `<link rel="alternate" type="application/json+oembed" href="..."/>` in the document head.
- Request params: required `url` — "The URL to retrieve embedding information for."; optional `maxwidth`, `maxheight`, `format`.
- Consumer-side security: "When a consumer displays any URLs, they will probably want to filter the URL scheme to be one of `http`, `https` or `mailto`"; and "consumers display the HTML in an `iframe`, hosted from another domain."

**Vizra fit:** the `photo` type maps cleanly onto a single-image permalink and avoids shipping consumer-executed HTML. Prefer `photo` over `rich` for single images; `rich` only where an album carousel genuinely requires it, and never emit HTML that a consumer would run same-origin.

| Field | Value |
|---|---|
| Exact URL | https://ogp.me/ |
| Title | The Open Graph protocol |
| Version / date shown | **no version number or date displayed on the page** |
| Observed | 2026-09-15 |
| HTTP result | 200 OK |

- Four required properties: `og:title` — "The title of your object as it should appear within the graph"; `og:type` — "The type of your object, e.g., 'video.movie'"; `og:image` — "An image URL which should represent your object within the graph"; `og:url` — "The canonical URL of your object that will be used as its permanent ID".
- Image structured properties: `og:image:url` (identical to og:image), `og:image:secure_url` — "An alternate url to use if the webpage requires HTTPS", `og:image:type`, `og:image:width` — "The number of pixels wide", `og:image:height` — "The number of pixels high", `og:image:alt` — "A description of what is in the image".
- RDFa prefix required on the html element: `<html prefix="og: https://ogp.me/ns#">`.
- Multiple images: "The first tag (from top to bottom) is given preference during conflicts"; structured properties attach to the most recently declared root tag.

**Vizra fit:** `og:image:alt` gives the same alt-text field WCAG 1.1.1 and the Mastodon/Pixelfed attachment conventions all demand — one alt-text value should feed the DB, the AP attachment (`summary` for Mastodon-style, `name` for Pixelfed-style), the ATProto `alt`, and `og:image:alt`. Private/authorization-gated photos must not emit `og:image` at all.

---

## Version pins observed

| Technology | Version / date seen | URL |
|---|---|---|
| ActivityPub (W3C) | W3C Recommendation, 23 January 2018 | https://www.w3.org/TR/activitypub/ |
| Mastodon ActivityPub doc | last updated 30 March 2026 | https://docs.joinmastodon.org/spec/activitypub/ |
| Mastodon Security doc (HTTP Signatures) | last updated 20 July 2026; `draft-cavage-http-signatures` | https://docs.joinmastodon.org/spec/security/ |
| Pixelfed ActivityPub spec | no version/date shown on page | https://docs.pixelfed.org/spec/ActivityPub.html |
| Pixelfed technical federation doc | **FAILED — HTTP 404** | https://docs.pixelfed.org/technical-documentation/activitypub.html |
| AT Protocol overview | © 2026, no date shown | https://atproto.com/guides/overview |
| AT Protocol OAuth profile | authoritative spec; client-metadata standard an Internet Draft as of August 2024 | https://atproto.com/specs/oauth |
| AT Protocol Lexicon guide | © 2026, no date shown | https://atproto.com/guides/lexicon |
| AT Protocol Blobs spec | no date shown; CIDv1 / raw 0x55 / SHA-256 | https://atproto.com/specs/blob |
| AT Protocol Sync spec | © 2026; 5 MB frame, 200 ops/commit, 1 MB/record | https://atproto.com/specs/sync |
| app.bsky.embed.images lexicon | `main` branch @ 2026-09-15; max 4 images, blob maxSize 2000000, accept image/* | https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/embed/images.json |
| app.bsky.feed.post lexicon | `main` branch @ 2026-09-15; text 3000 bytes / 300 graphemes | https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/post.json |
| docs.bsky.app | **FAILED — 301 to bsky.network, empty body** | https://docs.bsky.app/ |
| IPFS privacy & encryption | no date shown | https://docs.ipfs.tech/concepts/privacy-and-encryption/ |
| IPFS persistence | no date shown | https://docs.ipfs.tech/concepts/persistence/ |
| Kubo RPC API | **kubo v0.43.1**; page last updated 2026-09-15 | https://docs.ipfs.tech/reference/kubo/rpc/ |
| IPFS Pinning Service API | OpenAPI **1.0.0** | https://raw.githubusercontent.com/ipfs/pinning-services-api-spec/main/ipfs-pinning-service.yaml |
| Backblaze S3-Compatible API | last updated **2025-12-10** | https://www.backblaze.com/docs/cloud-storage-s3-compatible-api |
| Backblaze S3 API introduction | last updated **11 December 2025**; SigV4 only; versioned by default | https://www.backblaze.com/apidocs/introduction-to-the-s3-compatible-api |
| Backblaze large files | last updated **29 August 2023**; parts 5 MB–5 GB, files 5 MB–10 TB | https://www.backblaze.com/docs/cloud-storage-large-files |
| Backblaze Object Lock (S3 API) | last updated **28 June 2023**; compliance + governance modes | https://www.backblaze.com/docs/cloud-storage-enable-object-lock-with-the-s3-compatible-api |
| AWS S3 multipart limits | max object 48.8 TiB, 10,000 parts, parts 5 MiB–5 GiB | https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html |
| AWS S3 object integrity | default checksum **CRC64NVME** | https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html |
| ClickHouse backup | no version/date shown | https://clickhouse.com/docs/operations/backup |
| ClickHouse ReplacingMergeTree | no version/date shown | https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree |
| Next.js | **16.3.5**, page lastUpdated **2026-08-25** | https://nextjs.org/docs/app/guides/self-hosting |
| Echo | **v5** (`github.com/labstack/echo/v5`), requires **Go 1.25+** | https://echo.labstack.com/guide/quickstart/ |
| sqlc | **v1.31.1**, released **2026-04-22** | https://docs.sqlc.dev/en/latest/reference/changelog.html |
| PostgreSQL (textsearch) | **18** (current) | https://www.postgresql.org/docs/current/textsearch-intro.html |
| PostgreSQL pg_trgm | **18**; similarity_threshold 0.3 default | https://www.postgresql.org/docs/current/pgtrgm.html |
| Redis | **8.10.1**, released **17 August** (security release) | https://github.com/redis/redis/releases |
| Redis licensing | `>= 8.0.0` → **RSALv2 or SSPLv1 or AGPLv3**; `<= 7.2` → BSD-3-Clause | https://redis.io/legal/licenses/ |
| Go | **go1.27.0** (2026-08-19); minor **go1.27.1** (2026-09-01) | https://go.dev/doc/devel/release |
| libvips | **8.18**, released **4 December 2025**; LGPL-2.1-or-later | https://www.libvips.org/ |
| govips | **v2.18.0** (published 01 Apr); MIT; requires libvips **8.14+** | https://github.com/davidbyttow/govips/releases |
| bimg | **v1.1.9**; MIT; last push **2025-01-23** | https://github.com/h2non/bimg |
| imaging (pure Go) | **v1.6.2**; MIT; last push **2023-09-21** (dormant) | https://github.com/disintegration/imaging |
| OWASP File Upload Cheat Sheet | reachable 200 OK; **no revision date shown** | https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html |
| OWASP SSRF Prevention Cheat Sheet | reachable 200 OK; **no revision date shown** | https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html |
| lucide-react | **1.46.0**, published **2026-09-14**; ISC | https://registry.npmjs.org/lucide-react |
| Lucide license | **ISC** (Feather subset **MIT**) | https://lucide.dev/license |
| WCAG | **2.2, W3C Recommendation, 12 December 2024** | https://www.w3.org/TR/WCAG22/ |
| Docker Compose merge tags | `!reset` / `!override` documented; **minimum version NOT STATED** | https://docs.docker.com/reference/compose-file/merge/ |
| Docker Compose profiles | documented; **minimum version NOT STATED** | https://docs.docker.com/compose/how-tos/profiles/ |
| oEmbed | **Version 1.0**, no date shown | https://oembed.com/ |
| Open Graph protocol | **no version or date shown** | https://ogp.me/ |

---

## Failed / unverified fetches (2026-09-15)

| URL | Result |
|---|---|
| https://docs.pixelfed.org/technical-documentation/activitypub.html | FAILED — HTTP 404 Not Found |
| https://raw.githubusercontent.com/pixelfed/docs/dev/src/spec/ActivityPub.md | FAILED — HTTP 404 Not Found (raw-source fallback) |
| https://docs.bsky.app/ | FAILED — 301 → https://bsky.network/ ; follow-up returned empty body |
| https://docs.bsky.app/docs/advanced-guides/posts | FAILED — 301 → https://bsky.network/docs/advanced-guides/posts ; two follow-up fetches returned empty body |
| https://redis.io/docs/latest/ | FAILED — HTTP 404 Not Found (worked at /docs/latest/get-started/) |
| https://www.backblaze.com/docs/cloud-storage-s3-compatible-api-supported-operations | FAILED — HTTP 404 Not Found (no consolidated operations table exists at that path) |
| https://echo.labstack.com/docs | REDIRECT ONLY — body was "Redirecting to: /guide/quickstart/"; resolved at https://echo.labstack.com/guide/quickstart/ |
| https://ipfs.github.io/pinning-services-api-spec/ | PARTIAL — 200 OK, ReDoc SPA returned title only; substance read from the raw OpenAPI YAML |

**Open UNVERIFIED items requiring a later pass:**
1. Pixelfed's ActivityPub representation of Albums/Collections — no official page found.
2. Backblaze S3-compatible multipart part-size limits and `x-amz-checksum-*` header support — not documented on any reachable Backblaze page.
3. Minimum Docker Compose version for `!reset` / `!override` and for `profiles` — not stated in Docker's docs.
4. Bluesky's narrative post/image guide (rate limits, client-side resize behaviour) — docs site unreachable; only lexicon constraints captured.
