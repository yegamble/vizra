# Prompt 10 — optional public IPFS distribution addendum
Use with Prompt 04 for one acceptance item at a time.

Implement the next IPFS requirement as optional public content distribution. Review current IPFS privacy/encryption and persistence documentation [IPFS, IPFS-PERSISTENCE]. IPFS is not a replacement for Vizra's private authenticated object access, and unpinning is not global erasure.

Use explicit per-instance enablement and per-publication consent. Publish only the chosen sanitized public representation after authorization/visibility checks at request time and again immediately before job execution. Never publish private originals, hidden metadata/GPS, thumbnails derived from private content, secret share links, or access tokens. The UI must explain persistence and third-party copies before publication.

Support OFF, EXTERNAL, and MANAGED modes with no unused local daemon. Keep node RPC/admin interfaces non-public, use constrained network access, and provide meaningful diagnostics. Implement content/representation-to-CID mappings, pin status, retries, availability checks, unpin jobs, and recovery without making core upload/viewing depend on IPFS availability.

Test actual add/pin/retrieve integrity, daemon/node restart, interrupted pinning, pin failure, gateway failure, duplicate jobs, local delete/unpin, privacy changes racing with queued work, and rebuild of the pin inventory after restore. Distinguish gateway HTTP success from actual byte-integrity and pin persistence. A second independent test node is stronger evidence of distribution than reading back from the same local node alone.

Document the selected pinning provider/node responsibilities, disk limits and cleanup, object retention policy, and deletion limitations. Encryption of payloads must not be presented as hiding all network metadata; private-IPFS designs require their own approved security model rather than an undocumented toggle. Report exactly what was tested, not generic 'IPFS supported'.
