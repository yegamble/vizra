from core import *

# ---------------------------------------------------------------- F6 storage providers
req("VZ-STORAGE-001","Local filesystem storage with atomic publication and private access",
    "Operator: default local storage under a named volume; quarantine → atomic move; private objects served only through authorized handlers or short-lived signed URLs; never directly by the proxy.",
    "storage", EXPLICIT, [{"source":"CHARTER","note":"local disk without S3"},{"source":"CHEV-COMPARE","note":"Local storage"}], edition="all",
    deps=["VZ-FOUND-001"], success=["Original survives restart; private object 403 without auth"], negative=["Path traversal in filename rejected"], privacy=["Static serving cannot bypass authorization"], recovery=["Interrupted move leaves no partial public file"], evidence=EV_API+EV_NEG)
req("VZ-STORAGE-002","S3-compatible adapter qualified against an emulator (MinIO) with capability flags",
    "Operator: STORAGE_BACKEND=s3 with endpoint/region/bucket/keys/path-style; multipart, presigned PUT (not POST), checksums configurable per provider, range GET, delete, CORS documented; adapter contract tests.",
    "storage", EXPLICIT, [{"source":"CHEV-COMPARE","note":"S3 compatible"},{"source":"B2-S3","note":"presigned POST unsupported on Backblaze"},{"source":"AWS-CHECKSUM","note":"CRC64NVME default"}],
    deps=["VZ-STORAGE-001"], success=["Contract suite green on MinIO"], negative=["Credential failure, timeout, cancellation mapped to errors; no partial publish"], privacy=["Bucket private; signed URL TTL bounded"], recovery=["Abort multipart on failure; lifecycle rule documented"], evidence=["contract test output"])
req("VZ-STORAGE-003","AWS S3 real-provider qualification",
    "Operator: the adapter passes the contract suite against a real AWS bucket/region; evidence names region and endpoint style without credentials.",
    "storage", EXPLICIT, [{"source":"CHARTER","note":"S3 including AWS"},{"source":"AWS-MPU","note":"multipart limits"}],
    deps=["VZ-STORAGE-002"], success=["Live run recorded"], evidence=["provider lane output"], profiles=("full",))
req("VZ-STORAGE-004","Multiple storage locations with routing and per-location settings",
    "Owner: define several locations (local/S3) with name, capacity, URL/CDN mapping; choose default; assets remember their location.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"External storage servers API"},{"source":"CHEV-UPLOAD-STORAGE","note":"Name, Bucket, Key, Secret, Storage capacity, URL"}], edition="all",
    deps=["VZ-STORAGE-002"], success=["Second location added; new uploads route; old assets unchanged"], negative=["Deleting a location with assets refused"], api=["/api/v1/admin/storage-locations"], ui=["/admin/storage"], evidence=EV_API+EV_UI)
req("VZ-STORAGE-005","Storage migration between locations with reconciliation",
    "Operator: migrate assets between locations in a restartable job with integrity checks; source deleted only after reconciliation; records keep stable IDs.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"migrate records"},{"source":"PROMPT-05","note":"restartable, integrity-checked"}], edition="all",
    deps=["VZ-STORAGE-004","VZ-JOBS-001"], success=["Migration of a fixture library verified by checksum"], negative=["Kill mid-migration → resume without loss"], cli=["vizra storage migrate"], ui=["/admin/storage"], evidence=["transcript"])
req("VZ-STORAGE-006","Backblaze B2 via S3-compatible API real-provider qualification",
    "Operator: contract suite passes against Backblaze with SigV4, presigned PUT, versioned-bucket delete semantics, checksum mode verified or documented UNVERIFIED.",
    "storage", EXPLICIT, [{"source":"CHARTER","note":"Backblaze"},{"source":"B2-S3","note":"unsupported: ACLs, IAM, tagging, presigned POST"}],
    deps=["VZ-STORAGE-002"], success=["Live run recorded"], negative=["Delete on versioned bucket documented"], evidence=["provider lane output"], profiles=("full",), unresolved=["Q-016"])
req("VZ-STORAGE-007","Backblaze B2 native (legacy) API adapter",
    "Operator: native B2 API adapter as a separate parity obligation (Pro), or an approved decision to satisfy it via S3-compatible only.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"Backblaze B2 (legacy) Pro"}], edition="Pro",
    deps=["VZ-STORAGE-004"], success=["Adapter contract suite or approved substitution"], evidence=["provider lane or owner decision"], profiles=("full",), unresolved=["Q-030"],
    mechanism="Chevereto keeps a legacy native B2 adapter. Proposed: satisfy via S3-compatible unless owner requires native.")
req("VZ-STORAGE-008","Google Cloud Storage native adapter", "Operator: GCS adapter with JSON key auth passing the contract suite against a real bucket.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"Google Cloud Storage Pro"}], edition="Pro", deps=["VZ-STORAGE-004"], success=["Live run"], evidence=["provider lane"], profiles=("full",), unresolved=["Q-031"])
req("VZ-STORAGE-009","Microsoft Azure Blob native adapter", "Operator: Azure adapter passing the contract suite against a real account.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"Microsoft Azure Pro"}], edition="Pro", deps=["VZ-STORAGE-004"], success=["Live run"], evidence=["provider lane"], profiles=("full",), unresolved=["Q-031"])
req("VZ-STORAGE-010","Alibaba Cloud OSS native adapter", "Operator: OSS adapter passing the contract suite (endpoint required).",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"Alibaba Cloud OSS Pro"}], edition="Pro", deps=["VZ-STORAGE-004"], success=["Live run or S3-compatible qualification"], evidence=["provider lane"], profiles=("full",), unresolved=["Q-031"])
req("VZ-STORAGE-011","OpenStack Swift native adapter", "Operator: Swift adapter (identity URL, service name, credentials) passing the contract suite.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"OpenStack Swift Pro"}], edition="Pro", deps=["VZ-STORAGE-004"], success=["Live run"], evidence=["provider lane"], profiles=("full",), unresolved=["Q-031"])
req("VZ-STORAGE-012","SFTP storage adapter", "Operator: SFTP adapter (host, path, user, key/password) with a public URL mapping; disabled in multi-tenant mode.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"SFTP Pro"},{"source":"CHEV-RELEASES","note":"4.5.3 removed FTP/SFTP in SaaS environments"}], edition="Pro", deps=["VZ-STORAGE-004"], success=["Contract suite against a test SFTP server"], negative=["Host key verification enforced"], evidence=["provider lane"], profiles=("full",), unresolved=["Q-031"])
req("VZ-STORAGE-013","FTP storage adapter", "Operator: FTP adapter as a parity obligation with an explicit insecure-transport warning; disabled in multi-tenant mode.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"FTP Pro"}], edition="Pro", deps=["VZ-STORAGE-004"], success=["Contract suite against a test FTP server"], negative=["Plain FTP requires explicit acknowledgement"], evidence=["provider lane"], profiles=("full",), unresolved=["Q-031"])
req("VZ-STORAGE-014","CDN / custom URL mapping per location and universal CDN support",
    "Owner: map a location to a CDN or custom hostname; private assets never cacheable publicly; cache keys include visibility version.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"Universal CDN support"},{"source":"CHEV-UPLOAD-STORAGE","note":"URL mapped to the storage"}], edition="all",
    deps=["VZ-STORAGE-004"], success=["Public asset served via CDN URL"], privacy=["Private asset not fetchable via CDN URL; visibility change invalidates"], evidence=EV_API+EV_NEG)
req("VZ-STORAGE-015","Asset storage (site assets: avatars, logos, backgrounds) on the same location model",
    "Owner: site and user assets use the location model with Local/S3 in core and all adapters in full.",
    "storage", CHEV, [{"source":"CHEV-COMPARE","note":"Asset storage API Local, S3 / All"}], edition="all",
    deps=["VZ-STORAGE-004"], success=["Avatar stored on S3 location"], evidence=EV_API)

# ---------------------------------------------------------------- imports / exports
req("VZ-IMPORT-001","Filesystem bulk importer with dry run, mapping, checkpoints, resume and report",
    "Operator: import a directory tree with three parse modes (top folder = user; top folders = albums for guest; flat); JSON sidecars for image/album/user metadata; UTF-8; dry run; checkpoint/resume; idempotent rerun; missing-data report; cron-able; lock file.",
    "import", CHEV, [{"source":"CHEV-BULK-IMPORTER","note":"parse modes, JSON sidecars, lock, cron"}], edition="all",
    deps=["VZ-UPLOAD-001","VZ-JOBS-001","VZ-ALBUM-001"], success=["Fixture tree imports; rerun imports nothing new"], negative=["Corrupt sidecar reported, not fatal"], privacy=["Album privacy from sidecar preserved"], recovery=["Kill mid-import → resume from checkpoint"], cli=["vizra import fs"], ui=["/admin/import"], evidence=["transcript + report"])
req("VZ-IMPORT-002","Chevereto instance import (database + storage) preserving users, albums, categories, tags, privacy, timestamps",
    "Operator: import from a Chevereto MySQL export and its storage; dry run and mapping report; password hashes never assumed valid (users get reset flow); missing comments not invented.",
    "import", CHEV, [{"source":"CHEV-FEATURES","note":"Preserves users, albums, categories, tags, and file data"},{"source":"PROMPT-06","note":"imports"}], edition="all",
    deps=["VZ-IMPORT-001"], success=["Fixture export imports with mapping report"], negative=["Unknown schema version refused with guidance"], evidence=["transcript"], profiles=("full",), unresolved=["Q-035"])
req("VZ-IMPORT-003","Flickr data export import (photos, albums, favorites, tags, descriptions, dates, privacy)",
    "Photographer: imports a Flickr account export archive; dry run; mapping report; privacy mapped conservatively (default private on ambiguity).",
    "import", FLICKR, [{"source":"FLICKR-HELP","note":"account data download"},{"source":"CATALOG-F6","note":"Flickr source adapter"}],
    deps=["VZ-IMPORT-001"], success=["Fixture archive imports"], privacy=["Ambiguous privacy → private"], evidence=["transcript"], profiles=("full",))
req("VZ-EXPORT-001","Site-level export for migration away",
    "Operator: export all users/media/albums/metadata to a documented open format with manifest and checksums.",
    "import", SAFE, [{"source":"CHARTER","note":"real ownership"},{"source":"CHEV-COMPARE","note":"Export user"}],
    deps=["VZ-ACCOUNT-002"], success=["Export re-imports via VZ-IMPORT-001 losslessly"], cli=["vizra export"], evidence=["round-trip transcript"], profiles=("full",))

# ---------------------------------------------------------------- open-network integrations
req("VZ-AP-001","ActivityPub actor per user with WebFinger discovery and signed fetches",
    "Visitor on a peer: discovers @user@instance; actor document with inbox/outbox/followers/publicKey; HTTP signatures (draft-cavage, RSA-SHA256) on requests; secure-mode compatible.",
    "activitypub", INTEG, [{"source":"AP","note":"actor inbox/outbox"},{"source":"MASTODON-SECURITY","note":"HTTP Signatures"}],
    deps=["VZ-AUTH-001","VZ-JOBS-001"], success=["Mastodon and Pixelfed test instances resolve the actor"], negative=["Unsigned inbox POST rejected; forged keyId rejected"], privacy=["Private profiles not federated"], api=["/.well-known/webfinger","/ap/users/{name}","inbox/outbox"], ui=["/settings/federation"], evidence=["peer interoperability evidence with versions"], profiles=("full",))
req("VZ-AP-002","Publish public photos as Create(Note) with Image attachments, alt text, sensitive flag and blurhash",
    "Photographer: opts in per instance/account; public photos federate to followers with alt text (attachment name/summary), sensitive flag for NSFW, blurhash, focal point; private/unlisted/password content never exported.",
    "activitypub", INTEG, [{"source":"PIXELFED-AP","note":"Note with Image attachments; name=alt; sensitive"},{"source":"MASTODON-AP","note":"summary=alt; as:sensitive; blurhash"}],
    deps=["VZ-AP-001","VZ-MEDIA-004"], success=["Post appears on Mastodon and Pixelfed with alt text"], negative=["Privacy change racing queued delivery → delivery cancelled or Delete sent"], privacy=["GPS-stripped public representation only"], recovery=["Unavailable peer retried with bounded backoff"], evidence=["peer screenshots + activity IDs"], profiles=("full",))
req("VZ-AP-003","Follow/Accept/Reject/Undo and inbound Like/Announce/Reply/Delete/Update/Flag handling",
    "Member: remote users follow; remote likes/replies shown as remote reactions distinct from native ratings; deletes and updates honored; Flag routed to moderation.",
    "activitypub", INTEG, [{"source":"MASTODON-AP","note":"Create Delete Like Announce Update Undo Flag"}],
    deps=["VZ-AP-001","VZ-COMMENT-001"], success=["Follow from Mastodon accepted; reply appears"], negative=["Duplicate/out-of-order activities idempotent; oversized objects rejected"], privacy=["Remote content sanitized"], evidence=["peer evidence"], profiles=("full",))
req("VZ-AP-004","Federation policy: instance allow/block lists, per-user opt-out, best-effort remote deletion",
    "Owner: block instances; members opt out; deletion sends Delete but the UI states remote copies may persist.",
    "activitypub", INTEG, [{"source":"PROMPT-08","note":"moderation/blocking; best-effort deletion"}],
    deps=["VZ-AP-001"], success=["Blocked instance activities dropped"], api=["/api/v1/admin/federation"], ui=["/admin/federation"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-AT-001","Cross-post public photos to Bluesky (app.bsky.feed.post with embed.images)",
    "Photographer: opt-in cross-post with up to 4 images ≤ 2,000,000 bytes each, alt text, aspect ratio, text ≤ 300 graphemes; blob uploaded before record; remote write vs local timeout reconciled without duplicates.",
    "atproto", INTEG, [{"source":"BSKY-LEXICON","note":"images maxLength 4, blob maxSize 2000000, text 300 graphemes"},{"source":"AT-BLOB","note":"upload before record"}],
    deps=["VZ-AUTH-007","VZ-MEDIA-004"], success=["Post visible on Bluesky with alt text"], negative=["Oversized image resized to fit or refused with message"], privacy=["Only public, GPS-stripped representation"], recovery=["Timeout after remote success → no duplicate record"], evidence=["live Bluesky evidence"], profiles=("full",))
req("VZ-AT-002","Native Vizra AT records (photo/album) under an owned Lexicon namespace with local indexing",
    "Photographer: public photos/albums published as native records in the user's PDS under a Vizra-owned NSID; Vizra indexes its own records from the firehose/sync scoped to its namespace; lexicon versioned by NSID.",
    "atproto", INTEG, [{"source":"AT-LEXICON","note":"lexicons never change constraints"},{"source":"AT-SYNC","note":"subscribeRepos; limits"}],
    deps=["VZ-AT-001"], success=["Record written and read back via Vizra index"], negative=["Cursor gap/backfill handled"], privacy=["No private originals or album contents"], recovery=["Restart resumes from cursor"], evidence=["reference PDS evidence"], profiles=("full",), unresolved=["Q-036"])
req("VZ-IPFS-001","Opt-in public IPFS publication of approved public representations with pin management",
    "Photographer/owner: instance enablement + per-publication consent with a persistence warning; publish only the sanitized public representation; CID mapping stored; pin status, retries, availability checks; unpin on delete/privacy change with honest limits.",
    "ipfs", INTEG, [{"source":"IPFS-PRIVACY","note":"all traffic public"},{"source":"IPFS-PERSISTENCE","note":"pinning vs GC"}],
    deps=["VZ-TOPOLOGY-005","VZ-MEDIA-004","VZ-JOBS-001"], success=["Add/pin/retrieve integrity verified from a second node"], negative=["Privacy flip racing queued publish → publish cancelled"], privacy=["Private content never enqueued (checked at request and again before publish)"], recovery=["Pin inventory rebuilt after restore"], api=["POST /api/v1/photos/{id}/ipfs"], ui=["viewer share → IPFS"], evidence=["two-node evidence"], profiles=("full",))
req("VZ-IPFS-002","Pinning service (remote) support",
    "Operator: EXTERNAL mode via IPFS Pinning Service API (bearer token; queued/pinning/pinned/failed) as an alternative to a managed node.",
    "ipfs", INTEG, [{"source":"IPFS-PINNING","note":"API 1.0.0"}],
    deps=["VZ-IPFS-001"], success=["Pin lifecycle via a test pinning service"], evidence=["transcript"], profiles=("full",))
