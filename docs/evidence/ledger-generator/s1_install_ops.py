from core import *

# ---------------------------------------------------------------- install / wizard / topology
req("VZ-INSTALL-001","One-command installer that is idempotent and resumable",
    "Operator: `curl … | sh` (or `sh install.sh`) detects the platform, installs Docker+Compose if missing, unpacks the checksum-verified release bundle (or clones with --git), installs the checksum-verified `vizra` CLI, and hands over to `vizra setup`; a second run changes nothing; it never writes env secrets or runs compose up.",
    "install", META, [{"source":"VIDRA-INSTALL","note":"install.sh contract"},{"source":"CHARTER","note":"stranger installs with published instructions"}],
    deps=["VZ-FOUND-001","VZ-INSTALL-002"], success=["Fresh Ubuntu 24.04 amd64 → tree in /opt/vizra + CLI + interview started","--help needs no network/root/clone under /bin/sh"],
    negative=["Checksum mismatch aborts before writing","Non-tty without --yes refuses"], privacy=["Existing env/production.env is never regenerated"],
    recovery=["Interrupted run resumes from the completed step"], cli=["install.sh --yes --ref --dir --owner --git"], evidence=["clean-target transcript; install_test.sh results"], decided=["Q-027"])
req("VZ-INSTALL-002","`vizra setup` interview, loopback web wizard, non-interactive and --check modes write one validated env file",
    "Operator: the interview asks domain/TLS/instance name/release/storage/external PostgreSQL/Redis/analytics/IPFS/optional components/SMTP/registration/import questions; the same engine serves `--web` on loopback with a one-time link; `--non-interactive` with flags/answers file; `--check` validates; secrets minted, never blank; re-run preserves values; `--rotate` explicit; KEK rotation needs --yes-i-know.",
    "install", META, [{"source":"VIDRA-SETUP","note":"setup.go interview and usage"},{"source":"META-REPO","note":"question set"}],
    deps=["VZ-FOUND-006"], success=["Every answer lands on a template key (CI asserted)","Rendered Caddyfile.local for acme/internal/plain-http; nginx example for external"],
    negative=["External datastore answered yes with no DSN is refused","s3 default without credentials is not offered as default"],
    privacy=["Secrets read without echo; @file/stdin/VIZRA_SETUP_* indirections; 0600 file"], recovery=["Re-run keeps every existing value; refuses rewrite without --yes"],
    cli=["vizra setup [--web|--non-interactive|--check|--rotate]"], evidence=["setup unit tests keyed by question; CI answer-coverage assert"])
req("VZ-INSTALL-003","Secure one-time owner claim",
    "Operator: while unclaimed, every signup path answers 403; the API mints a one-time token at boot, prints it to its log, stores only the hash; the claim page creates the owner; an instance with users and no token is implicitly claimed and never mints again.",
    "install", META, [{"source":"VIDRA-DEPLOY-README","note":"owner claim flow"},{"source":"CHARTER","note":"claim the owner account"}],
    deps=["VZ-AUTH-001"], success=["Claim with valid token yields owner role; admin surface returns 200"],
    negative=["Reused/expired token rejected; race between two claimers yields one owner","Registration bots cannot become owner"],
    privacy=["Token never appears in HTTP responses or non-local logs"], recovery=["Restart re-mints; old token invalid"],
    api=["POST /api/v1/setup/claim-owner"], ui=["/setup/claim"], evidence=EV_API+EV_NEG+["owner_claim_race test"])
req("VZ-INSTALL-004","Deployment bundle is deterministic and self-sufficient",
    "Operator: the release bundle contains compose files, overlays, env template, deploy scripts, Caddyfile, systemd units, release record and manifest; excludes bootstrap/override/dev overlay/.git; builds byte-identical twice; renders every production shape without checkouts.",
    "install", META, [{"source":"VIDRA-META-CI","note":"bundle job"}],
    deps=["VZ-TOPOLOGY-001"], success=["cmp of two builds equal; manifest schema version = migrations on disk"], negative=["A missing bind-mount source fails the content check"], evidence=["bundle lane logs"])

req("VZ-TOPOLOGY-001","Base + production overlay + external-datastore overlays render the declared topology",
    "Operator: docker-compose.yml (dev), docker-compose.prod.yml (loopback binds, pinned images, restart, log caps, named volumes, edge), and external overlays for PostgreSQL/Redis/ClickHouse/IPFS; explicit -f chain in production; Compose ≥ 2.24.4 enforced.",
    "topology", META, [{"source":"VIDRA-COMPOSE","note":"!override profiles + !reset depends_on"},{"source":"CHARTER","note":"managed by default or external"}],
    deps=["VZ-FOUND-001"], success=["Every shape in META_REPO.md §2 renders; postgres/redis/search/clickhouse/ipfs RPC publish nothing"],
    negative=["Compose < 2.24.4 (including 2.24.0–2.24.3) refused by install.sh, deploy, rollback, restore and doctor","Bare `docker compose` on a prod host is documented as wrong and compose.sh used instead"],
    evidence=EV_OPS, decided=["Q-017"])
req("VZ-TOPOLOGY-002","PostgreSQL: managed container by default, external DSN suppresses the container",
    "Operator: VIZRA_EXTERNAL_POSTGRES=true + DATABASE_URL disables the bundled service and every depends_on edge; migrations and api/worker/search use the DSN; invalid DSN fails boot, never forks a fresh local DB; backup ownership moves to the provider and the runbook says so.",
    "topology", EXPLICIT, [{"source":"CHARTER","note":"configured but invalid external service must not silently fall back"},{"source":"VIDRA-EXTERNAL-PG","note":"overlay mechanics"}],
    deps=["VZ-TOPOLOGY-001"], success=["Rendered model has no postgres service and no dangling edges","Live test against external PostgreSQL passes upload+restart"],
    negative=["Unreachable DSN: /readyz non-200, no local postgres started","Missing DATABASE_URL fails the render"], recovery=["Provider snapshot/PITR path documented and rehearsed"],
    evidence=EV_OPS+["external-topology rehearsal transcript"])
req("VZ-TOPOLOGY-003","Redis: managed by default, external URL suppresses the container; api and search keyspaces separated",
    "Operator: VIZRA_EXTERNAL_REDIS=true + REDIS_URL (and SEARCH_REDIS_URL on a different logical DB) disables the bundled service; rediss:// documented; Redis loss degrades rate limits/caches without privacy fail-open or data loss.",
    "topology", EXPLICIT, [{"source":"VIDRA-EXTERNAL-REDIS","note":"overlay"},{"source":"ARCH","note":"Redis is acceleration not truth"}],
    deps=["VZ-TOPOLOGY-001"], success=["Render without redis service; live run with external Redis"], negative=["Redis down: uploads/comments still persist; caches rebuild"],
    privacy=["Cache miss never serves another user's private response"], recovery=["Redis flush loses nothing durable"], evidence=EV_OPS+["fault-injection transcript"])
req("VZ-TOPOLOGY-004","ClickHouse: OFF creates nothing; MANAGED starts the pinned container; EXTERNAL uses the DSN",
    "Operator: ANALYTICS_MODE=off|managed|external; enabling without endpoint creates the managed container; endpoint suppresses it; invalid config errors; gallery never depends on ClickHouse.",
    "topology", EXPLICIT, [{"source":"CHARTER","note":"ClickHouse off by default; managed or external"},{"source":"PROMPT-07","note":"OFF/EXTERNAL/MANAGED"}],
    deps=["VZ-TOPOLOGY-001"], success=["Three rendered shapes asserted","Admin status shows mode and lag"], negative=["Bad DSN → error status, uploads unaffected"],
    recovery=["ClickHouse restart: events reconcile without double counting"], evidence=EV_OPS)
req("VZ-TOPOLOGY-005","IPFS: OFF creates nothing; MANAGED runs a Kubo node with RPC on loopback; EXTERNAL uses a remote node or pinning service",
    "Operator: IPFS_MODE=off|managed|external; RPC never public; swarm port documented; disk limits and GC policy configured; core upload/view never waits on IPFS.",
    "topology", INTEG, [{"source":"KUBO-RPC","note":"never expose RPC API"},{"source":"IPFS-PINNING","note":"pinning service API 1.0.0"}],
    deps=["VZ-TOPOLOGY-001"], success=["Three shapes render; RPC 5001 loopback only"], negative=["RPC exposed off-host fails CI assert"], evidence=EV_OPS)
req("VZ-TOPOLOGY-006","TLS modes and edge",
    "Operator: VIZRA_TLS_MODE acme|acme-staging|internal|plain-http|external; caddy on the `edge` profile added by the engine except external; plain-http only for LAN/lab with explicit flag; ACME state in a named volume.",
    "topology", META, [{"source":"VIDRA-COMPOSE-PROD","note":"edge profile; Caddyfile.local"}],
    deps=["VZ-TOPOLOGY-001"], success=["Default render contains caddy; external render does not"], negative=["Missing Caddyfile.local refuses deploy (bind-mount dir trap)"], evidence=EV_OPS)
req("VZ-TOPOLOGY-007","Local-only HTTP development mode separate from production HTTPS",
    "Developer: make dev / dev-hot run the stack without TLS with dev seams (rate limit off, mail capture) that production refuses.",
    "topology", META, [{"source":"VIDRA-ENVIRONMENTS","note":"environment matrix"}],
    deps=["VZ-TOPOLOGY-001"], success=["Dev seams refused when VIZRA_ENV=production"], negative=["Override file never auto-loaded in production chain"], evidence=["boot refusal transcript"])
req("VZ-TOPOLOGY-008","Split api/worker topology",
    "Operator: optional `worker` profile runs the same image with VIZRA_ROLE=worker; external overlays cut its edges too; media processing scales independently.",
    "topology", META, [{"source":"VIDRA-COMPOSE-PROD","note":"worker split"}],
    deps=["VZ-TOPOLOGY-001","VZ-JOBS-001"], success=["Render with worker; jobs processed only by worker when split"], negative=["Two replicas do not double-process a job"], evidence=EV_OPS)

# ---------------------------------------------------------------- deploy / backup / restore / upgrade / operator
req("VZ-OPS-001","`vizra deploy` runs the sacred ordering with fail-closed gates",
    "Operator: release-record check → pre-deploy dump (abort on failure) → pull → migrate one-shot from release image (exit-code gated) → up -d --no-build → Caddy reload → probes; every skip printed; never folds migrations into up.",
    "operations", META, [{"source":"VIDRA-AGENTS","note":"deploy ordering is sacred"}],
    deps=["VZ-TOPOLOGY-001","VZ-FOUND-005"], success=["Deploy transcript shows each gate"], negative=["Failed dump aborts before pull","Unpaired tag triple refused"],
    recovery=["Failed migration leaves prior images serving and a documented forward path"], cli=["vizra deploy"], evidence=EV_OPS)
req("VZ-OPS-002","`vizra doctor` performs real checks",
    "Operator: doctor verifies Docker/Compose versions, env file validity, rendered topology, closed ports, DNS/TLS, disk, DB/Redis/storage reachability, migration ledger, backup freshness, optional-service health; exits non-zero on failure; no fake success.",
    "operations", OPS, [{"source":"CATALOG-F9","note":"doctor"},{"source":"VIDRA-README","note":"doctor 18 checks"}],
    deps=["VZ-TOPOLOGY-001"], success=["Each check has a failing fixture in tests"], negative=["A check that cannot run reports BLOCKED, not OK"], cli=["vizra doctor"], evidence=["doctor unit tests; transcript"])
req("VZ-OPS-003","Status, logs, restart, update commands",
    "Operator: `vizra status` (service health, versions, queue depth), `vizra logs <svc>`, `vizra restart <svc>`, `vizra update` (checks releases, explains floor).",
    "operations", META, [{"source":"VIDRA-CLI","note":"subcommands"}],
    deps=["VZ-OPS-001"], success=["Commands wrap compose.sh with the env-derived chain"], negative=["Bare docker compose usage documented as wrong"], cli=["vizra status|logs|restart|update"], evidence=["unit tests + transcript"])
req("VZ-OPS-004","Maintenance mode",
    "Operator: a maintenance toggle returns a friendly page for visitors while admins can still sign in; uploads paused; queued work retained.",
    "operations", CHEV, [{"source":"CHEV-COMPARE","note":"System features: Maintenance mode"}], edition="all",
    deps=["VZ-ADMIN-002"], success=["Toggle persists; visitors see page; admin works"], negative=["Uploads rejected with clear message, not lost"], api=["PATCH /api/v1/admin/settings"], ui=["/admin/settings"], evidence=EV_API+EV_UI)
req("VZ-OPS-005","Structured logs, metrics and tracing with privacy-safe fields",
    "Operator: JSON logs, Prometheus metrics, optional OpenTelemetry traces (otel profile OFF/MANAGED/EXTERNAL); sensitive-key denylist enforced.",
    "operations", OPS, [{"source":"CATALOG-F9","note":"logs/metrics/tracing"},{"source":"AGENTS","note":"never log credentials or private metadata"}],
    deps=["VZ-FOUND-006"], success=["Metrics endpoint scrapeable; traces exported when enabled"], privacy=["Denylist test"], evidence=["scrape transcript; denylist test"])
req("VZ-OPS-006","Job administration UI/CLI",
    "Owner/operator: view queued/running/failed/dead-letter jobs (processing, imports, federation, analytics, IPFS), retry, cancel, inspect error; stuck jobs visible.",
    "operations", OPS, [{"source":"CATALOG-F9","note":"job administration"},{"source":"CHEV-COMPARE","note":"Background file queue handling"}],
    deps=["VZ-JOBS-001","VZ-ADMIN-001"], success=["Failed job retried from UI; audit event"], negative=["Cancel of a running job is bounded and safe"], api=["GET/POST /api/v1/admin/jobs"], ui=["/admin/jobs"], cli=["vizra jobs"], evidence=EV_API+EV_UI)
req("VZ-OPS-007","Capacity and performance budgets declared and measured",
    "Owner: reference hardware, dataset, request/media mix, p95/p99, error rate, queue drain, RPO/RTO recorded and approved before acceptance; metadata-only vs real-bytes workloads separated; the load corpus is declared here (count, total bytes, megapixel mix; 10k photos proposed) separately from the VZ-FOUND-007 correctness corpus; budgets provisional until the first M0 measurement run, then frozen.",
    "operations", SAFE, [{"source":"RELEASE-ACCEPTANCE","note":"performance and recovery objectives"}],
    deps=["VZ-FOUND-007"], success=["Budgets documented; load run recorded","Declared load corpus (count, total bytes, megapixel mix; 10k photos proposed) recorded with the run","Oldest-pending-job age exposed as a metric and failing doctor/readiness above the declared threshold"], negative=["Budget changed to excuse a failed run is rejected in review"], evidence=["load report with environment"], unresolved=["Q-028"], decided=["Q-028"])
req("VZ-OPS-008","Security posture on the host and images",
    "Operator: non-root containers, no-new-privileges, capped logs, images pinned by tag (digest records), secrets untracked, no Docker socket in web/API process.",
    "operations", SAFE, [{"source":"ARCH","note":"web/API must not gain unrestricted Docker-socket access"},{"source":"VIDRA-COMPOSE-PROD","note":"security_opt"}],
    deps=["VZ-TOPOLOGY-001"], success=["Rendered model assertions"], negative=["A service mounting docker.sock fails CI"], evidence=EV_OPS)

req("VZ-BACKUP-001","Application-consistent backup of database, originals, manifests, configuration and keys",
    "Operator: `vizra backup` produces pg_dump, media manifest with checksums (local originals + required objects; provider inventory for S3), config archive (env, Caddyfile.local, KEKs), enabled-service inventory, retention (14 daily + 8 weekly), success marker; systemd timer nightly.",
    "backup", EXPLICIT, [{"source":"CHARTER","note":"backup/recovery requirements"},{"source":"ARCH","note":"backups include PostgreSQL, originals, manifests, keys, enabled state"}],
    deps=["VZ-OPS-001","VZ-STORAGE-001"], success=["Backup archive lists every original with sha256"], negative=["Disk exhaustion mid-backup fails loudly and leaves prior backups intact","Missing key → backup marked incomplete"],
    privacy=["Backup encryption/access policy documented; secrets not in world-readable archive"], recovery=["Corrupt archive detected by verify step"], cli=["vizra backup"], evidence=["backup transcript; verify output"])
req("VZ-BACKUP-002","Restore on a separate clean target with integrity verification",
    "Operator: `vizra restore` on a fresh host restores DB, originals (checksums verified), derivatives regenerated or restored, keys, config; accounts, permissions, comments, ratings, favorites, federation identities, optional-service config all work; uploads work after restore; RTO/RPO measured.",
    "backup", EXPLICIT, [{"source":"RELEASE-ACCEPTANCE","note":"restore on a separate clean target"},{"source":"PROMPT-11","note":"rehearsal list"}],
    deps=["VZ-BACKUP-001"], success=["Checksum report 100% match; post-restore upload succeeds"], negative=["Restore refuses without typed confirmation","Missing KEK → clear failure naming the key"],
    privacy=["Private assets remain private after restore (visibility test)"], recovery=["Partial restore leaves an inspectable state, not a half-bootable instance"], cli=["vizra restore"], evidence=["rehearsal record with timings"])
req("VZ-BACKUP-003","External datastore and analytics backup ownership is explicit",
    "Operator: with external PostgreSQL/Redis/ClickHouse the tooling refuses to claim a snapshot it cannot take; runbook assigns ownership; ClickHouse has verified backup or declared replay source sufficient for retained history.",
    "backup", SAFE, [{"source":"ARCH","note":"external services need explicit backup responsibility"},{"source":"CH-BACKUP","note":"BACKUP/RESTORE SQL"}],
    deps=["VZ-TOPOLOGY-002","VZ-TOPOLOGY-004"], success=["Doctor reports backup ownership per service"], negative=["backup.sh refuses pg_dump under external overlay and says why"], evidence=["transcript; runbook section"])
req("VZ-BACKUP-004","S3 versioning and IPFS pinning are not treated as backups",
    "Operator: documentation and doctor make clear that provider versioning/pins do not replace the backup; media manifest covers objects regardless.",
    "backup", SAFE, [{"source":"PROMPT-11","note":"do not treat S3 versioning or IPFS pinning as independent backup"},{"source":"B2-INTRO","note":"buckets versioned by default"}],
    deps=["VZ-BACKUP-001"], success=["Docs and doctor wording present"], evidence=["review"])

req("VZ-UPGRADE-001","Upgrade from the previous supported release with data; rollback inside the schema window",
    "Operator: deploy of N+1 over N with real data; expand/contract migrations; `vizra rollback <tag>` is an app-only tag flip safe for one release; irreversible migrations named in the runbook; failed migration path documented and rehearsed.",
    "upgrade", EXPLICIT, [{"source":"RELEASE-ACCEPTANCE","note":"upgrade/recovery gate"},{"source":"VIDRA-RELEASES","note":"release records, floors"}],
    deps=["VZ-OPS-001","VZ-CI-005"], success=["Upgrade transcript; rollback transcript; data intact"], negative=["Rollback across an incompatible migration is refused"], recovery=["Forward recovery or restore proven"], cli=["vizra rollback"], evidence=["rehearsal records"])
req("VZ-UPGRADE-002","Release records pin image digests and schema versions",
    "Operator: releases/<tag>.json per platform release; deploy refuses unpaired triples; digest mismatch refused; fork/mirror registries warn.",
    "upgrade", META, [{"source":"VIDRA-RELEASES","note":"schema_version 1 record"}],
    deps=["VZ-OPS-001"], success=["Record validated strictly; test suite"], negative=["Corrupt record fatal for deploy"], evidence=["unit tests; transcript"])
