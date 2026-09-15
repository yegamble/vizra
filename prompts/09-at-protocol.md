# Prompt 09 — AT Protocol addendum
Use with Prompt 04 for one acceptance item at a time.

Read current official AT Protocol architecture, OAuth, Lexicon, blob, and sync documentation [AT, AT-OAUTH, AT-LEXICON]. Do not reuse an ActivityPub design and rename its endpoints. Before implementation, preserve these separate acceptance families:
A. Account linking/authentication with an AT identity.
B. Optional Bluesky-compatible publication using Bluesky's actual schemas and constraints.
C. Native Vizra public photo/album records, with Vizra's own Lexicons and indexing/client behavior.
A Share-to-Bluesky button alone does not satisfy the full native requirement. A complete reimplementation of a PDS or relay is not required merely to build an AT application; use approved existing implementations where appropriate.

Implement one dependency-ready family item. Anchor identities to verified DIDs, not mutable handles. Follow the current OAuth profile with PKCE/PAR/DPoP, authority/issuer/subject validation, current scopes, secure credential storage, nonce/refresh behavior, revocation, and hardened discovery HTTP clients. Prefer maintained verified Go libraries; document any missing capability rather than hand-rolling security without review.

Define which system owns each fact: local private gallery records stay authoritative in PostgreSQL; public native AT records live in the user's selected PDS with a local projection and explicit write/reconciliation state. Handle a successful remote write followed by a local timeout without duplicate records. Model blobs, record URIs, CIDs, deletions, account/handle/PDS changes, backfill, checkpoints, cursor gaps, and tombstones. Do not upload private originals, EXIF secrets, or private album contents into public repositories.

Use a controlled namespace the project actually owns for custom Lexicons. Confirm current PDS validation and interoperability requirements. Custom records do not automatically appear in Bluesky's UI: implement the Vizra read/index path and document what other applications can actually consume. Constrain indexing to the required data instead of consuming an unbounded network firehose by default.

Test with an authorized reference/self-hosted PDS and an external service when that interoperability is advertised. Cover login expiry/revocation, identity mismatch, missing blobs, retry/reconnect, duplicate events, remote deletes, and restart/backfill. Record concrete evidence and remaining limitations. Keep all three families visible in the ledger until completed; do not downgrade native support to cross-posting to obtain a green report.
