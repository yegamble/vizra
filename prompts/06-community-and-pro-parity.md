# Prompt 06 — community, organization, import, and parity addendum
Use with Prompt 04 for one acceptance item at a time.

Select one dependency-ready requirement from the audited community/organization/pro-parity milestone. Do not implement all features at once or call the milestone done after completing one item.

Preserve explicit Vizra features: profiles, follows, native threaded/moderatable comments, numeric ratings, favorites, notifications, albums/sub-albums, multi-album membership, tags/categories, discovery, search, sharing, and personal organization. Define the semantics of favorites versus public likes versus ratings. For a rating, test valid range, one current vote per user, change/removal, aggregate correctness, concurrent updates, authorization, and refresh persistence. For comments, test edit/delete/reply/report, sanitization, pagination, notifications, permissions, and retry duplication.

Albums and collections need ordering, cover choice, cycle prevention, bulk membership changes, and explicit privacy/share rules. Public placement never silently grants access to a private asset. Test every read surface—thumbnails, metadata, search counts, embeds, export, API, direct links—not just the main photo page.

For audited Chevereto obligations, implement original Go-native equivalents with recorded mappings. Retain native non-S3 storage adapters, watermarks, upload tooling, configurable branding/pages, moderation and external service integrations, APIs, tenant administration, and operator utilities in the full ledger. Restricted services need credentials/contracts and approved test fixtures; mocks alone do not establish live support. Privileged custom code, insecure transports, and debugger-like tooling need an explicit safe deployment boundary, not an unreviewed public control. Never silently substitute a different feature and claim parity.

For imports, build a dry run, checkpoint/resume, mapping report, integrity validation, idempotent rerun, and cancellation. Start with filesystem/metadata imports; add actual Chevereto/Flickr/other retained source adapters as separately testable items. Preserve available owners/albums/privacy/tags/descriptions/timestamps; report source-export omissions. Never invent missing comments, migrate unsupported password hashes as if valid, or require manually fixing the database after import.

Include the full API/UI/operator journey, allowed/denied role cases, real persisted data, migration/recovery effects, and browser evidence. Emit any unresolved source limitation as BLOCKED/UNVERIFIED instead of erasing the requirement.
