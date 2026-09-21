from core import *

# ---------------------------------------------------------------- F2 uploads
req("VZ-UPLOAD-001","Authenticated device upload of JPEG/PNG with real-byte validation and durable processing",
    "Photographer: picks or drops files; upload session created after quota reservation; bytes sniffed and bounded; finalize is idempotent; processing enqueued durably; original and thumbnail visible after completion and after restart.",
    "upload", EXPLICIT, [{"source":"CHARTER","note":"upload a real photograph"},{"source":"ARCH","note":"media workflow"},{"source":"OWASP-UPLOAD"}],
    deps=["VZ-AUTH-001","VZ-STORAGE-001","VZ-JOBS-001","VZ-QUOTA-001"], success=["JPEG and PNG fixtures upload; thumbnail decodes to expected dimensions; survives restart"],
    negative=["Wrong MIME/extension mismatch rejected by sniff","Oversized file rejected at declared limit","Duplicate finalize returns the same asset once","Polyglot/active SVG rejected"],
    privacy=["Asset private-by-default per setting; anonymous GET of original/thumbnail 403/404 before publish"],
    recovery=["Worker crash after object write and before finalize leaves no orphan visible; cleanup job removes quarantine"],
    api=["POST /api/v1/uploads (create session)","PUT /api/v1/uploads/{id}/parts","POST /api/v1/uploads/{id}/finalize"], ui=["/upload","library drop zone"], evidence=EV_API+EV_UI+EV_NEG+["decoded thumbnail hash"])
req("VZ-UPLOAD-002","Chunked/resumable uploads with progress, cancel and retry",
    "Photographer: large files upload in parts; connection drop resumes; per-file progress; cancel discards parts; retry does not duplicate.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"Chunked uploads"},{"source":"CATALOG-F2","note":"resumability"}], edition="all",
    deps=["VZ-UPLOAD-001"], success=["Interrupted upload resumes from last part"], negative=["Out-of-order/duplicate part handled; expired session cleaned"], recovery=["Abandoned sessions expire and release quota"], api=["PUT parts; GET /api/v1/uploads/{id}"], ui=["/upload progress list"], evidence=EV_API+EV_UI)
req("VZ-UPLOAD-003","Multiple sources: file picker, drag-and-drop, clipboard paste, device camera",
    "Photographer: any of these starts the same pipeline; keyboard/file-picker alternative always present.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"device file browser, drag and drop, on-the-fly device camera, clipboard"}], edition="all",
    deps=["VZ-UPLOAD-001"], success=["Each source tested in browser"], negative=["Drop without picker fallback is a defect"], ui=["/upload"], evidence=EV_UI)
req("VZ-UPLOAD-004","Upload from remote URL with SSRF protection",
    "Photographer/guest (if allowed): supplies a URL; server fetches with scheme/port allowlist, DNS re-check after redirects, private/link-local/metadata ranges blocked, size/time limits; owner toggle.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"Upload (URL) toggle"},{"source":"OWASP-SSRF"}], edition="all",
    deps=["VZ-UPLOAD-001"], success=["Public URL fetched and processed"], negative=["169.254.169.254, localhost, redirect-to-private, oversized all rejected with tests"], api=["POST /api/v1/uploads/from-url"], ui=["/upload URL tab"], evidence=EV_API+EV_NEG)
req("VZ-UPLOAD-005","Guest (anonymous) uploads with owner controls",
    "Owner: enables guest uploads; guest file-size limit; guest albums; auto-delete guest uploads after N; moderation mode for guests; disabled by default.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"User uploads, guest uploads; Guest uploads auto delete; Upload max file size (users and guest)"},{"source":"CHEV-RELEASES","note":"4.5.5 guest uploads disabled by default"}], edition="all",
    deps=["VZ-UPLOAD-001","VZ-MOD-001"], success=["Guest upload with delete link; auto-delete job runs"], negative=["Disabled → 403; captcha required when configured"], privacy=["Guest uploads never attributed to a member"], api=["POST /api/v1/uploads (guest key)"], ui=["/upload for guests","/admin/settings/uploads"], evidence=EV_API+EV_UI)
req("VZ-UPLOAD-006","Upload page options: title, description, tags, album, category, privacy, NSFW flag, expiration",
    "Photographer: sets metadata during upload; batch apply; category optional; NSFW checkbox toggle owner-controlled.",
    "upload", CHEV, [{"source":"CHEV-API-V1","note":"title, description, tags, album_id, category_id, nsfw, expiration"},{"source":"CHEV-COMPARE","note":"Upload NSFW checkbox toggle"}], edition="all",
    deps=["VZ-UPLOAD-001","VZ-ALBUM-001","VZ-TAG-001"], success=["Metadata persisted and shown"], negative=["Invalid expiration rejected"], api=["finalize body fields"], ui=["/upload form"], evidence=EV_API+EV_UI)
req("VZ-UPLOAD-007","Duplicate detection",
    "Owner: toggle duplicate acceptance; duplicates detected by content hash (and optionally per-user/day/IP); user informed; deduplication never reveals another user's private media.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"Duplicate media detection; Upload duplication toggle"},{"source":"CHEV-FEATURES","note":"Daily + IP + hash"}], edition="all",
    deps=["VZ-UPLOAD-001"], success=["Same bytes twice → configured behavior"], privacy=["Cross-user duplicate returns no information about the other asset"], api=["finalize response"], ui=["/upload"], evidence=EV_API+EV_NEG)
req("VZ-UPLOAD-008","Time-based expiring uploads and file delete links",
    "Photographer/guest: chooses expiration (ISO-8601 duration); expired assets deleted by job; guest uploads get a delete link.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"Time-based auto-remove uploads; File delete link; Upload expiration toggle"}], edition="all",
    deps=["VZ-UPLOAD-001","VZ-JOBS-001"], success=["Asset gone after expiry; delete link works once"], negative=["Delete link unguessable"], api=["expiration field; DELETE via token"], ui=["upload result panel"], evidence=EV_API+EV_UI, decided=["Q-015"])
req("VZ-UPLOAD-009","Upload UI mode: on-page container or dedicated /upload route; redirect after single upload; embed codes on complete",
    "Owner: chooses uploader UI mode; redirect behavior; embed codes shown on completion when enabled.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"Upload user interface (container, page); Upload redirection; Embed codes on upload complete"}], edition="all",
    deps=["VZ-UPLOAD-001","VZ-SHARE-002"], success=["Both modes tested"], ui=["/upload","/admin/settings/uploads"], evidence=EV_UI)
req("VZ-UPLOAD-010","Upload API (v1-compatible shape) and ShareX/desktop tool support",
    "Photographer: uploads via API key with source (file/base64/URL), title, description, tags, album, category, width, expiration, nsfw, format json|txt|redirect; ShareX custom uploader config downloadable.",
    "upload", CHEV, [{"source":"CHEV-API-V1","note":"file upload API parameters"},{"source":"CHEV-COMPARE","note":"API uploading (ShareX, etc)"}], edition="all",
    deps=["VZ-AUTH-008","VZ-UPLOAD-001"], success=["ShareX config uploads a file"], negative=["Bad key 401; oversized 413"], api=["POST /api/v1/upload (compat) and native"], ui=["/settings/api ShareX snippet"], evidence=EV_API+["ShareX transcript"])
req("VZ-UPLOAD-011","Embedded uploader plugin for third-party sites",
    "Owner: embeddable uploader script (postMessage) for other sites/forums; origin allowlist; guest key; XenForo/Discourse/MyBB/phpBB/bbPress/IPB-style integrations documented as adapters.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"Upload plugin (PUP.js, postMessage)"},{"source":"CHEV-FEATURES","note":"XenForo, Discourse & MyBB plugins; bbPress, Discuz!, IPB, phpBB"}], edition="all",
    deps=["VZ-UPLOAD-010"], success=["Embedded on a test page with allowed origin"], negative=["Disallowed origin refused; CSP documented"], api=["guest key"], ui=["/admin/settings/uploader-plugin"], evidence=EV_UI+EV_NEG, decided=["Q-029"],
    mechanism="Chevereto ships PHP forum plugins. Proposed equivalent: one embeddable uploader plus a documented plugin contract; per-forum plugins are separate optional deliverables.")
req("VZ-UPLOAD-012","Upload moderation queue (disabled | guest | all)",
    "Owner: uploads held for approval per mode; moderators approve/reject with reason; uploader notified; hidden from every read surface until approved.",
    "upload", CHEV, [{"source":"CHEV-COMPARE","note":"Upload moderation (Lite/Pro)"},{"source":"CHEV-FILE-UPLOADS","note":"Moderate uploads: Disabled, Guest, All"}], edition="Lite",
    deps=["VZ-UPLOAD-001","VZ-MOD-001"], success=["Pending asset invisible in listings/search/embeds/API/direct object link"], negative=["Approve twice safe"], privacy=["Pending originals not fetchable"], api=["/api/v1/admin/moderation/uploads"], ui=["/admin/moderation"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-UPLOAD-013","Upload limits: file size per role, max pixel dimensions, threads, allowed formats",
    "Owner: configures max upload size (users/guests), maximum image dimension (auto-downscale), simultaneous threads, enabled formats from the supported set.",
    "upload", CHEV, [{"source":"CHEV-FILE-UPLOADS","note":"settings page fields"},{"source":"CHEV-COMPARE","note":"Uploadable file extensions; Upload threads; Upload maximum image size"}], edition="all",
    deps=["VZ-UPLOAD-001"], success=["Settings enforced server-side"], negative=["Client bypass of limits rejected"], api=["settings"], ui=["/admin/settings/uploads"], evidence=EV_API+EV_NEG)

# ---------------------------------------------------------------- F2 media processing
req("VZ-MEDIA-001","Derivatives: thumbnail, medium (fixed width or height), display; originals preserved losslessly",
    "Photographer: three sizes generated by a libvips-backed worker with bounded resources; original bytes untouched (except policy-driven EXIF strip); processing version recorded.",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"Generate thumbs & medium sized images; Lossless media handling"},{"source":"RES-PROTOCOLS","note":"libvips 8.18 / govips 2.18.0"}], edition="all",
    deps=["VZ-UPLOAD-001","VZ-JOBS-001"], success=["Derivatives exist and decode for every fixture"], negative=["Decoder bomb hits pixel/memory/time limits and fails safely"], recovery=["Reprocess job regenerates derivatives idempotently"], api=["GET /api/v1/photos/{id} representations"], ui=["viewer"], evidence=EV_API+["decoded output hashes"], decided=["Q-034"],
    notes="Q-034 decided 2026-09-15: libvips build pinned by digest with loader list recorded; API never decodes; unsupported formats rejected at upload.")
req("VZ-MEDIA-002","Format matrix: JPEG, PNG, GIF (animated), WebP (animated), AVIF, BMP; HEIC/HEIF decode is VZ-MEDIA-010 (full); RAW declined",
    "Photographer: every advertised format uploads, decodes, derives correctly; animation preserved where advertised; HEIC/HEIF decode-to-JPEG/AVIF is VZ-MEDIA-010 (full profile, Q-010 decided 2026-09-15); RAW is declined unless the owner adds it.",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"image/avif jpeg gif png webp bmp"},{"source":"CHEV-FILE-UPLOADS","note":"AVIF JPG JPEG PNG BMP GIF WEBP MOV MP4 WEBM — no HEIC/TIFF/SVG"}], edition="all",
    deps=["VZ-MEDIA-001","VZ-FOUND-007"], success=["Per-format fixture passes"], negative=["Unsupported format rejected with clear message"], evidence=["fixture matrix results"], decided=["Q-010"])
req("VZ-MEDIA-010","HEIC/HEIF decode-to-JPEG/AVIF on upload (config-gated, OFF by default, licence-reviewed build)",
    "Photographer (full): when the operator enables it, an iPhone HEIC/HEIF upload is converted to JPEG or AVIF on ingest with correct orientation and colour; the running image reports whether HEIC decode is available; HEIC is never written (no x265 in the image); RAW remains declined.",
    "media", FLICKR, [{"source":"FLICKR-UPLOAD-REQ","note":"Flickr converts HEIC to JPEG in-app; RAW unsupported"},{"source":"RATIFICATION-FACTS","note":"libvips/libheif HEIC decode via libde265; x265 encode is GPL-2+ and excluded; Q-010 decided 2026-09-15"}], profiles=("full",),
    deps=["VZ-MEDIA-002","VZ-FOUND-004"], success=["HEIC fixture with EXIF orientation converts to JPEG/AVIF upright with ICC honoured; derivative hashes recorded"], negative=["With HEIC decode absent from the build or the option disabled, a HEIC upload is rejected at the API naming the format; no job is enqueued"], privacy=["EXIF/GPS policy applies to the converted output"], recovery=["Reprocess regenerates the converted output idempotently"],
    api=["POST /api/v1/uploads (HEIC accepted only when enabled)"], ui=["uploader format hint","/admin/settings/uploads HEIC toggle"], cli=["vizra doctor (reports HEIC decode availability)"], evidence=["fixture conversion results","image loader list in releases/<tag>.json","licence review record for libheif/libde265"], decided=["Q-010"],
    notes="Q-010 decided 2026-09-15: decode only (libheif + libde265), never encode; OFF by default; full profile; RAW declined unless the owner adds it.")
req("VZ-MEDIA-003","Orientation, color profile and transparency correctness",
    "Photographer: EXIF orientation applied in derivatives; ICC profiles preserved or converted deliberately; transparency retained; no destructive default cropping.",
    "media", SAFE, [{"source":"CHEV-COMPARE","note":"JPEG auto-orientation"},{"source":"DESIGN-BRIEF","note":"preserve aspect ratio"}],
    deps=["VZ-MEDIA-001"], success=["Rotated fixture renders upright; wide-gamut fixture within tolerance"], evidence=["pixel comparison report"])
req("VZ-MEDIA-004","EXIF read, display, strip policy and GPS privacy",
    "Photographer/owner: EXIF read and shown on an Exif tab when allowed; owner policy to strip on upload; member option to keep EXIF; GPS and private tags never in public derivatives, embeds, feeds, federation, IPFS by default; camera auto-tagging optional.",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"EXIF data (read, strip); Show Exif data; Upload EXIF removal; EXIF camera model auto-tagging"},{"source":"AGENTS","note":"never log raw private metadata"}], edition="all",
    deps=["VZ-MEDIA-001"], success=["Exif tab shows camera fields; strip policy removes from derivatives"], negative=["GPS present in original never appears in any public representation (test per surface)"], privacy=["Owner sees what is stripped"], api=["GET /api/v1/photos/{id}/exif"], ui=["viewer Exif tab","/admin/settings/uploads"], evidence=EV_API+EV_NEG)
req("VZ-MEDIA-005","Video uploads (MP4, MOV, WebM): store, poster frame, bounded playback derivative",
    "Photographer: uploads video within limits; poster frame generated; playback in viewer; scoped to parity (no live streaming, no HLS ladder unless approved).",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"video/quicktime, video/mp4, video/webm; Generate video frame image"},{"source":"CATALOG-F2","note":"retain audited video obligations"}], edition="all",
    deps=["VZ-MEDIA-001"], success=["Fixture video uploads; poster decodes; plays in browser"], negative=["Oversized/long video rejected at declared limits"], evidence=EV_API+EV_UI, decided=["Q-009"],
    mechanism="Chevereto accepts video files and generates a frame image; transcoding depth undocumented. Vizra scope: store + poster + browser-native playback; transcoding is a separate decision.")
req("VZ-MEDIA-006","Equirectangular 360° image viewing",
    "Visitor: 360 images detected (XMP/aspect) and viewable in a pannable viewer with keyboard control.",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"Equirectangular 360° images"},{"source":"CHEV-FEATURES","note":"360 images (equirectangular, gopro)"}], edition="all",
    deps=["VZ-VIEWER-001"], success=["360 fixture opens in pano viewer"], ui=["viewer"], evidence=EV_UI)
req("VZ-MEDIA-007","Watermarks",
    "Owner: watermark image, opacity, position, percentage, margin, minimum image size; per role (guest/user/admin); GIF option; applied to display derivatives, never originals.",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"Watermark image uploads (Lite/Pro)"},{"source":"CHEV-FEATURES","note":"opacity, position, percentage, margin, min size, per user group"}], edition="Lite",
    deps=["VZ-MEDIA-001"], success=["Watermarked derivative hash differs; original unchanged"], negative=["Small image below min size unwatermarked"], api=["settings"], ui=["/admin/settings/watermark"], evidence=EV_API+["visual evidence"])
req("VZ-MEDIA-008","Storage layout and file naming options",
    "Owner: date folders or direct layout; naming original/random/mixed/ID; asset IDs independent of paths so options can change without breaking existing records.",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"Auto file-naming options; Storage modes (date, direct)"}], edition="all",
    deps=["VZ-STORAGE-001"], success=["Changing option affects new uploads only"], evidence=EV_API)
req("VZ-MEDIA-009","Reprocessing and integrity tools",
    "Operator: regenerate derivatives, verify checksums, find orphans, repair missing derivatives; stats regeneration.",
    "media", CHEV, [{"source":"CHEV-COMPARE","note":"Upload storage tools (regen stats, migrate records)"}], edition="all",
    deps=["VZ-MEDIA-001","VZ-JOBS-001"], success=["Deleting a thumbnail then running repair restores it"], cli=["vizra media verify|reprocess"], ui=["/admin/storage tools"], evidence=["transcript"])
req("VZ-QUOTA-001","Storage quotas per user/role with safe reservation",
    "Owner: per-role default quota and per-user override; quota reserved before upload and released on failure; usage shown to member; no double charge under retries.",
    "media", CHEV, [{"source":"CHEV-FEATURES","note":"Individual storage and access limits"},{"source":"ARCH","note":"reserve quota"}], edition="all",
    deps=["VZ-AUTH-001","VZ-FOUND-003"], success=["Upload beyond quota rejected before transfer; usage accurate after delete"], negative=["Concurrent uploads cannot exceed quota (race test)"], recovery=["Crashed upload releases reservation"], api=["GET /api/v1/me/quota"], ui=["/settings/storage","/admin/users/{id}"], evidence=EV_API+EV_NEG, decided=["Q-007"])
req("VZ-QUOTA-002","Per-storage-location capacity",
    "Owner: each storage location declares capacity; new uploads route to a location with space; full location alarms.",
    "media", CHEV, [{"source":"CHEV-UPLOAD-STORAGE","note":"Storage capacity e.g. 20 GB"}], edition="all",
    deps=["VZ-STORAGE-004"], success=["Capacity honored"], ui=["/admin/storage"], evidence=EV_API)
req("VZ-JOBS-001","Durable outbox/jobs with leases, retries, idempotency and dead letters",
    "Developer/operator: every side effect (processing, notifications, search projection, federation, analytics, IPFS, imports, expiration) is a job row written in the business transaction; workers lease, retry with backoff, dead-letter, and are safe to run twice; multi-replica safe.",
    "media", SAFE, [{"source":"ARCH","note":"durable work and consistency"}],
    deps=["VZ-FOUND-003"], success=["Kill worker mid-job → job completes after restart without duplicate side effect"], negative=["Poison job dead-letters after N attempts"], recovery=["Backlog retention and disk pressure behavior defined"], cli=["vizra jobs"], evidence=["fault-injection tests"])
