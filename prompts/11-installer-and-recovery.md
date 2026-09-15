# Prompt 11 — installer, deployment, upgrades, and recovery addendum
Use with Prompt 04 for one acceptance item at a time; introduce these tests early.

Implement the next operator acceptance item with the goal that a non-developer can install, inspect, upgrade, back up, and recover Vizra using published instructions alone. Follow the approved architecture; Go CLI handles privileged orchestration, not an Internet-facing web process with unrestricted Docker-socket access.

Implement local storage by default. PostgreSQL and Redis support managed or external modes. ClickHouse/IPFS are optional with OFF/EXTERNAL/MANAGED modes. Enabling an optional service without an external endpoint creates the pinned managed container. An external endpoint suppresses that local container. Invalid external configuration is an actionable error, not fallback to new local data. Test rendered Compose topology and running containers, not only environment variables.

Include preflight, clear resource/port/DNS/TLS checks, secure one-time owner claim, bounded retries, idempotent rerun, interrupted installation recovery, protected secrets, health/readiness, and doctor diagnostics. Production images are pinned; database/admin ports are not public; migrations are a discrete fail-closed step from the matching release image. Support local-only development HTTP separately from the production HTTPS path.

Backups need an application-consistent database/media manifest, checksums, configuration, protected keys, retention, encryption/access policy, and inventory of enabled managed/external services. Do not treat S3 versioning or IPFS pinning as an independent backup. External services require explicit backup ownership and recovery evidence; missing permissions must be reported. Redis cache can be rebuilt only because durable state exists elsewhere. Enabled analytics must be restored or correctly reconstructed from sufficient retained events.

Rehearse restoring to a different clean server with no old volumes, including original-byte integrity, derivatives, accounts/permissions, comments/ratings, federation identities, optional-service configuration, and working uploads after restore. Measure recovery time and loss window against approved objectives. Test backup failure, disk exhaustion, missing key, corrupt archive, storage loss, and database migration failure.

Test upgrade with real data from the previous supported release. Use expand/contract migrations when required; binary rollback is safe only inside a documented compatibility window. Otherwise prove forward recovery or backup restoration. Never pretend an arbitrary schema downgrade is safe. Record exact source/images and go/no-go evidence. No production mutation or paid provisioning without authorization.
