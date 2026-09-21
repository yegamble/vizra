# Vizra meta repo — install, CI/CD and topology design (target, not implemented)

Decided 2026-09-15 by the owner: Vizra is organised like Vidra — a **meta
repo** (`vizra`) that ties together component repositories, ships the
deployment tree, the installer and the operator CLI hand-off, and carries the
product contract and evidence. This document specifies what milestone M0/M1
must build. **Nothing described here exists yet.** Every mechanism below is
PLANNED/UNVERIFIED until a ledger entry (`VZ-INSTALL-*`, `VZ-TOPOLOGY-*`,
`VZ-CI-*`, `VZ-BACKUP-*`, `VZ-UPGRADE-*`) records evidence.

Mechanisms are mirrored from `~/github/vidra` (read 2026-09-15: `install.sh`,
`bootstrap.sh`, `docker-compose*.yml`, `deploy/`, `.github/workflows/`,
`releases/`, `vidra-core/cmd/vidra`). They are reimplemented for Vizra, not
copied byte-for-byte: the trade-offs Vidra recorded as incidents are kept, the
video-specific parts are dropped, and the photo-specific services are added.

## 1. Repositories

| Repo | Role | Notes |
|---|---|---|
| `vizra` (this) | meta: `AGENTS.md`, `docs/`, compose files, `deploy/`, `env/*.env.example`, `install.sh`, `bootstrap.sh`, `tests/`, `releases/`, `.github/` | component checkouts nested, gitignored, pinned detached at release tags on hosts |
| `vizra-core` | Go/Echo API + worker + `vizra` operator CLI; `api/openapi.yaml`; sqlc; migrations compiled into the binary | publishes `ghcr.io/yegamble/vizra-core:<tag>`, the CLI binaries, checksums and the deployment bundle |
| `vizra-user` | Next.js/TypeScript/Tailwind application | publishes `ghcr.io/yegamble/vizra-user:<tag>` |
| `vizra-search` | internal Go search service (PostgreSQL FTS/trigram + Redis) | publishes `ghcr.io/yegamble/vizra-search:<tag>` from M0 as a real minimal service; SEARCH_MODE=off default before M3 (Q-001 decided 2026-09-15) |
| `vizra-branding` (proposed) | brand mark, tokens, Figma references | not created; tokens in `vizra-user/packages/ui`, brand assets in meta `brand/` after Prompt 02 (Q-002 decided 2026-09-15) |

`bootstrap.sh` clones or fast-forwards the component checkouts; `VIZRA_REF=<tag>`
pins all of them detached. Compose files here `include:` the component compose
files, so the meta repo is the full-stack definition.

## 2. Compose topology

Files: `docker-compose.yml` (base, dev-friendly, builds from checkouts),
`docker-compose.override.yml` (dev defaults, auto-loaded only by bare
`docker compose`), `docker-compose.dev.yml` (hot reload), `docker-compose.prod.yml`
(production overlay, explicit `-f` chain only), `docker-compose.external-postgres.yml`,
`docker-compose.external-redis.yml`, `docker-compose.external-clickhouse.yml`,
`docker-compose.external-ipfs.yml`.

Services and profiles (target):

| Service | Profile | Mode model | Off-host port |
|---|---|---|---|
| `postgres` | core | MANAGED (bundled) or EXTERNAL via overlay | none |
| `redis` | core | valkey (MANAGED, image `valkey/valkey` digest-pinned) or EXTERNAL RESP-compatible ≥ 7.2 (Q-004 decided 2026-09-15) | none |
| `migrate` (one-shot, `vizra-core` image, `migrate up`) | core | always | none |
| `api` (`vizra-core`, role api) | core | always | loopback only |
| `worker` (`vizra-core`, role worker) | core (or `worker` for split topology) | always | none |
| `frontend` (`vizra-user`) | frontend | always | loopback only |
| `search` + `search-migrate` (`vizra-search`) | core | `SEARCH_MODE=off` (default before M3) / `managed` (default from M3) / `external`; never a hard dependency; misconfiguration = doctor FAIL + degraded readiness (Q-001) | none |
| `clickhouse` | analytics | OFF (default) / MANAGED / EXTERNAL via overlay | none |
| `ipfs` (Kubo) | ipfs | OFF (default) / MANAGED / EXTERNAL (remote node or pinning service) | 4001 swarm only, gated in cloud firewall |
| `minio` | storage | dev/QA emulator only; never a production substitute for provider qualification | none |
| `clamav` | scan | OFF / MANAGED / EXTERNAL | none |
| `otel-collector`, `jaeger` | otel | OFF / MANAGED / EXTERNAL | none |
| `caddy` | edge (added by the engine unless `VIZRA_TLS_MODE=external`) | always for acme/internal/plain-http modes | 80, 443 |

Rules carried over from Vidra and asserted in CI, not assumed:

1. **OFF creates no container. EXTERNAL suppresses the local container
   (`profiles: !override ["external-disabled"]`, `depends_on: {svc: !reset null}`)
   and requires the DSN (`${VAR:?…}`). MANAGED starts the pinned container.**
   Invalid external configuration fails the render or the boot; it never
   falls back to a fresh local database, cache or store.
   The base file publishes no ports; developer port mappings live in
   `docker-compose.override.yml` bound to 127.0.0.1, so the merge tags are
   never the only thing closing a port (Q-017).
2. **Compose ≥ 2.24.4** for the production overlay; the version check stays.
3. **Only caddy 80/443 and the IPFS swarm port face the network.** Every other
   service publishes nothing or loopback, asserted with every optional
   profile enabled.
4. Every long-lived service: `restart: unless-stopped` and capped logging.
   One-shots never restart.
5. Images are pulled by immutable tag with `pull_policy: always`;
   migration one-shots carry no `build:` in the rendered production model.
6. Storage: `STORAGE_BACKEND=local` by default; `s3` with provider settings;
   additional native adapters (GCS, Azure, OSS, Swift, SFTP, FTP, legacy B2)
   are separate ledger obligations and separate qualification lanes.

## 3. Installer and wizard (`install.sh` → `vizra setup`)

`install.sh` (POSIX sh, `curl … | sh`-safe, idempotent, resumable):

1. detect platform (Ubuntu 24.04 amd64 first; separate ARM64 qualification); refuse non-amd64 server hosts by name; the CLI is built for linux/darwin × amd64/arm64 (Q-027);
2. privileges; 3. survey and confirmation (`--yes` for unattended);
4. install Docker Engine + Compose v2 (≥ 2.24.4) if missing;
5. resolve the release (`--ref`), unpack the checksum-verified deployment
   **bundle** (`vizra-bundle_<tag>.tar.gz`) into `/opt/vizra` — no git needed;
   `--git` clones instead; a release without a bundle falls back to clone, out
   loud;
6. download and checksum-verify the `vizra` CLI from `vizra-core` release
   assets into `/usr/local/bin`;
7. hand over to `vizra setup --template env/production.env.example
   --release-tag <tag>` with a terminal attached, and stop.

It **never** writes or overwrites `env/production.env` (that file holds the
KEKs that seal data), never runs `compose up`, never opens ports or edits sshd.

`vizra setup` (in `vizra-core/cmd/vizra`): the interview, the same questions
as a loopback-only `--web` wizard with a one-time link, `--non-interactive`
with flags/`--answers` file, `--check <env>`, `--rotate <VAR>` (a `*_KEK`
additionally needs `--yes-i-know`). Questions (target set; every answer must
land on a template key, asserted in CI):

| Question | Env keys |
|---|---|
| Domain, DNS points here?, TLS mode (acme / acme-staging / internal / plain-http / external), ACME email | `PUBLIC_BASE_URL`, `VIZRA_TLS_MODE`, `VIZRA_ACME_EMAIL` |
| Instance name | `INSTANCE_NAME` |
| Release tag | `VIZRA_CORE_TAG`, `VIZRA_USER_TAG`, `VIZRA_SEARCH_TAG` |
| Media storage backend (local / s3) + S3 endpoint, region, bucket, keys, path-style | `STORAGE_BACKEND`, `STORAGE_S3_*` |
| External PostgreSQL? + DSN | `VIZRA_EXTERNAL_POSTGRES`, `DATABASE_URL` |
| External Redis? + DSN | `VIZRA_EXTERNAL_REDIS`, `REDIS_URL`, `SEARCH_REDIS_URL` |
| Analytics: off / managed ClickHouse / external ClickHouse DSN | `ANALYTICS_MODE`, `CLICKHOUSE_URL` |
| IPFS: off / managed node / external node or pinning service | `IPFS_MODE`, `IPFS_API_URL`, `IPFS_PINNING_*` |
| Optional components: upload scanner, tracing | profiles `scan`, `otel` |
| SMTP now? | `MAIL_ENABLED`, `SMTP_*` |
| Registration: open? require approval? guest uploads? | `REGISTRATION_*`, `GUEST_UPLOAD_*` |
| Import source now? (filesystem / Chevereto / Flickr export) — recorded only, run later from the admin UI | `IMPORT_*` |

Secrets are minted by the engine (never blank in a generated file), can be
given via `@file`, `-` (stdin) or `VIZRA_SETUP_*`, and are read without echo.
`deploy/Caddyfile.local` is rendered from the template; `--tls-mode external`
writes an nginx example instead.

## 4. First boot and owner claim

`vizra deploy` (wraps `deploy/deploy.sh`): release-record check → pre-deploy
dump (abort on failure) → pull → `migrate up` as an exit-code-gated one-shot
from the release image → `up -d --no-build` → Caddy reload → probes
(`/healthz`, `/readyz`, frontend, edge). The api mints a one-time owner-claim
token at boot while unclaimed and prints it to its log; every signup path
answers 403 until the owner is claimed at `/setup/claim`. Only the token hash
is stored; a restart re-mints.

## 5. Operator CLI (`vizra`)

`setup` · `doctor` (real checks: Docker/Compose version, env file, rendered
topology, ports closed, DNS/TLS, disk, database/redis/storage reachability,
migration ledger, backup freshness, optional-service health) · `status` ·
`logs` · `restart <service>` · `update` · `deploy` · `rollback <tag>` ·
`backup` · `restore` · `release`. The CLI wraps `deploy/*.sh` 1:1 with
`ENV_FILE` injected; the scripts remain the source of truth. The web/API
process never gets unrestricted Docker-socket access.

## 6. Backup, restore, rollback, upgrade

- `backup.sh`: application-consistent `pg_dump -Fc` → gzip → **media
  manifest with checksums** (originals + required objects for local storage;
  provider inventory for S3) → config archive (env file, `Caddyfile.local`,
  protected keys) → enabled-service inventory (ClickHouse/IPFS mode) →
  optional off-site → retention (14 daily + 8 weekly) → success marker.
  External datastores: the script refuses and the runbook assigns backup
  ownership to the provider; the restore rehearsal must still be evidenced.
- `restore.sh` (destructive, `--yes`/typed confirmation): stop, drop,
  recreate, `pg_restore`, restore originals and verify checksums, migrate,
  probe. Rehearsed on a **separate clean host** per `docs/RELEASE_ACCEPTANCE.md`.
- `rollback.sh <tag>`: rewrite `VIZRA_*_TAG`, pull, restart, re-probe — app
  only, safe only inside the one-release schema-compatibility window enforced
  by `migrate-lint` (no destructive statements in `*.up.sql`).
- Upgrade: previous supported release with data; expand/contract migrations;
  forward recovery or backup restore proven, never an arbitrary downgrade.
- `releases/<tag>.json`: per-release image digests, commits and schema
  versions; `deploy.sh` refuses an unpaired tag triple.

## 7. CI/CD

Every repo carries **one required status check, `ci-required`**, which reads
`.github/required-checks.txt` (the checked-in definition of "required") and
fails when a listed lane failed, was cancelled, timed out or **never ran**.
Removing an entry fails unless the file carries `# retired: <name> — <reason>`.
External actions are pinned to 40-character commit SHAs. Skipped required
tests fail the job.

| Repo | Required lanes (target) |
|---|---|
| meta | `validate` (action pins, ignored env files, shellcheck on every script, `node --check` on smoke drivers, installer unit tests, Python deploy-script unit tests with skip-fails, Caddy pin parity, migrator floor parity, every compose render incl. OFF/EXTERNAL/MANAGED shapes, port closure, image pins, config-key coverage, `vizra setup` answer coverage, bootstrap idempotency) · `bundle` (bundle built twice byte-identical, manifest schema version matches migrations, production matrix renders with no checkouts on disk) · `boot` (full stack booted in production mode from source, `/readyz` 200, migration one-shots run from the service images, real JPEG upload → decoded thumbnail smoke) |
| core | `build-test` (`make ci`: fmt, vet, migrate-lint, openapi-verify, sqlc-verify, race unit tests) · `integration` (real PostgreSQL, Redis, image processor, MinIO, ClamAV; no-silent-skip audit) · `openapi` · `govulncheck` · `?guard` · `?docker-build` · `?prev-migrator-against-new-schema` · `?prev-release-against-new-schema` · provider lanes (AWS, Backblaze) on credentials and release · federation/AT/IPFS interoperability lanes when those slices exist |
| user | `frontend-ci` (typecheck, lint, icon lint, vitest, production build) · `contract-ci` (generated client matches core's spec) · `e2e-backed` (production build against a real backend, axe as a hard gate) · `dependency-audit` · `?guard` · `?docker-build` |
| search | `search-ci` · `search-integration` · `openapi` · `govulncheck` · `?guard` · `?docker-build` · `?rollback-floor` |

Releases: `vizra release <tag>` cuts tags in the component repos, watches
`publish-container`, verifies GHCR images, builds and uploads the deployment
bundle, then adds `releases/<tag>.json` with evidence. Merge queue and
branch-protection settings are recorded as required configuration; if the
agent lacks permission to set them, enforcement is recorded UNVERIFIED.

## 8. What this run did not do

No compose file, script, workflow, CLI or image exists. This document is the
target; `docs/quality/features.json` carries the obligations; issues
`VZ-ISSUE-001…` under `docs/issues/` carry the first slices.
