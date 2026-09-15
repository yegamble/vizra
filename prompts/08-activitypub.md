# Prompt 08 — ActivityPub federation addendum
Use with Prompt 04 for one acceptance item at a time.

Implement Vizra's next ActivityPub acceptance item as a real server-to-server federation capability, not merely external sharing. Read the current W3C ActivityPub specification and the declared peers' current implementation documentation [AP, MASTODON]. Record the chosen interoperability profile and test peer versions. Do not imply every gallery concept, rating, or album hierarchy has a universal interoperable mapping.

Scope and verify actors/discovery, inbox/outbox, stable object IDs, follow/accept/reject/undo, public image publishing with alt text, supported replies/likes/announces, edits/deletes, and moderation/blocking according to the approved profile. Choose appropriate ActivityStreams representations and verify actual display on the intended peers, such as a controlled Pixelfed and Mastodon instance. Signatures and discovery conventions need implementation-specific tests; the base specification alone is not a complete peer compatibility recipe.

Verify delivery authentication/actor authority, replay/idempotency, bounded fanout/retries, queue recovery, safe remote fetches, HTML sanitization, moderation, blocked instances, and cache behavior. Treat remote content and actor documents as hostile inputs. Test forged activity authorship, duplicate/out-of-order events, unavailable peers, worker restart, and a local privacy change racing with queued delivery.

Public-only outbound publication is the safe initial profile. Private/unlisted/secret-link content must not be exported without an explicitly approved model and tests. Distinguish best-effort remote deletion from guaranteed deletion; never promise control over another server's copies. Keep protocol actor/object IDs stable across backup/restore and upgrades.

Provide protocol fixtures plus real peer interoperability evidence from authorized test accounts. Record peer versions, source SHA, event IDs, and observed behavior. A canned JSON response or mock inbox is insufficient to mark live federation verified. External failures must not corrupt or block local gallery actions. Produce a user-facing capability/limitation document alongside the working controls.
