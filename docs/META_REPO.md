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

### 2a. What VZ-ISSUE-002 actually built, and where it deviates

The eight compose files above exist, plus `env/production.env.example`,
`env/development.env.example`, `env/registry/*.json` and four checkers wired
into the required `validate` lane. Every shape in `scripts/compose-shapes.json`
(`./scripts/compose-render.py --list`) is rendered on every run and asserted
from `docker compose config --format json` parsed as JSON — never from
the YAML — and the models are uploaded as a CI artifact. See
`docs/quality/COMMANDS.md` §§4–7 for the commands and, more importantly, for
what a green result does **not** prove.

**Nothing in this repository starts a container.** Every assertion is about a
rendered model. "The port is closed" means the model publishes nothing, not that
a running host was scanned.

Deviations from §1 and §2 above, each deliberate and none of them silent:

| § | Says | Built | Why |
|---|---|---|---|
| §1 | compose files here `include:` the component compose files | services are defined in `docker-compose.yml` | none of the three component repositories ships a compose file (checked at `vizra-core` c043df7, `vizra-user` 7730500, `vizra-search` 808a549; each AGENTS.md says compose wiring is not theirs), and VZ-ISSUE-002 may not add one |
| §2 | `search` on profile `core` | profile `search` | rule 1 of §2 says OFF creates no container and Q-001 makes `off` the default until M3. A service on `core` starts on every invocation, so `core` and "OFF creates no container" cannot both hold. The engine adds `--profile search` when `VIZRA_SEARCH_MODE=managed`, exactly as it adds `edge` unless TLS is external |
| §2 | `search-migrate` one-shot | not defined | `vizra-search` owns no migrations at M0 and reports `search_schema_version: null`. It is still in the never-published list so it cannot arrive with a port |
| §2 | `minio`, `clamav`, `otel-collector`, `jaeger` | not defined | they belong to the storage, scan and otel slices. All four are in the checker's never-published list, so whichever slice adds them cannot add them open |
| §2/§3 | `SEARCH_MODE`, `REDIS_URL`, `SEARCH_REDIS_URL`, `PUBLIC_BASE_URL`, `VIZRA_TLS_MODE`, `VIZRA_EXTERNAL_*`, `ANALYTICS_MODE`, `IPFS_MODE` | `VIZRA_SEARCH_MODE`, `VIZRA_CACHE_URL`, `VIZRA_PUBLIC_ORIGIN`; the rest are absent | the templates carry the names the services **actually read** — a key nobody reads is a lie an operator can act on. The engine-facing keys have no reader until VZ-ISSUE-003/004, so topology is selected with explicit `--profile` and `-f` arguments meanwhile. `SEARCH_REDIS_URL` has no consumer at all: `vizra-search` reads no cache variable at M0 |
| §2 | ClickHouse and IPFS external overlays | present, and they render OFF | they suppress the bundled container and wire no DSN, because no Vizra service reads one yet. For IPFS that is still a real property: no container means no swarm port |

Two operator-facing values feed two differently-spelled service keys, declared
in `env/registry/aliases.json` with a floor so adding a third is a visible edit:
`SEARCH_HMAC_KEY` (the contract's name; `vizra-core` still reads
`VIZRA_SEARCH_HMAC_KEY`, rename queued) and `VIZRA_PUBLIC_ORIGIN`
(`vizra-user` reads `PUBLIC_ORIGIN`) — the second is the same conflict as the
first and has not been ruled on.

`VIZRA_SEARCH_MODE` is read by **both** `vizra-core` (`off|managed|external`)
and `vizra-search` (`production|development`), with incompatible vocabularies.
No service in this tree takes an `env_file:`, which is what keeps them apart;
`vizra-search`'s value is set literally by the compose files.

### Two constraints this topology places on other repositories

**1. The HMAC-key rename — DONE, and here is the order it required.**
`SEARCH_HMAC_KEY` is the canonical contract name. `vizra-core` used to read
`VIZRA_SEARCH_HMAC_KEY`; since **4a80a1e** it reads the contract name and
**refuses the old one in production on presence with any non-empty value**. The
two repositories were one merge apart from a dead instance, in both directions:

| State | What compose must deliver |
|---|---|
| core `main` before 4a80a1e | `VIZRA_SEARCH_HMAC_KEY` only |
| core `main` at/after 4a80a1e | `SEARCH_HMAC_KEY` only |
| either, ever | **never both** — the retired name is refused on presence, so a "belt and braces" map is a guaranteed boot refusal |

So core's rename merged **first**, and this repository then flipped
`docker-compose.yml`, listed the old name in `env/registry/core.json`
`retired_keys`, re-snapshotted that file at the core `main` commit declaring the
key, and deleted the alias (floor 2 → 1) — in one commit, because every
intermediate state is a boot refusal.

What keeps it from coming back is `scripts/check-config-coverage.py`'s
`retired-key-delivered` rule, demonstrated by reintroducing the old spelling
into the compose file and watching it go red by name. Without it, the failure
mode is a 3am one: the refusal names a variable that appears nowhere in the
operator's env file, because compose injects it.

This is the pattern for the next rename, not a one-off: snapshot the component
at a `main` commit, list what it retired, and let the checker own the ordering.

**2. `vizra healthcheck` must exist before the boot lane lands.** `api` and
`worker` declare a healthcheck that runs `vizra version` — the same self-probe
the image ships. It proves the binary runs; it does **not** prove `/readyz`
answers, because the runtime image carries no curl or wget and `vizra-core` has
no `healthcheck` subcommand (`vizra-search` ships exactly that).

Rather than leave that as a comment, both probes are declared **known-false** in
`scripts/compose-shapes.json`. `scripts/check-compose-topology.py` then:

- **refuses** any `depends_on: {condition: service_healthy}` edge pointing at
  one (rule `probe-gates-readiness`) — which is why `frontend → api` is
  `service_started`, `required: false`. That rule's scope is narrow and worth
  stating: it only refuses a gate onto a probe someone has **declared** false,
  and cannot tell a real probe from a fake one nobody declared. The converse is
  `gated-probe-unrecognised` — every `service_healthy` target must be listed in
  `gated_probes` and still invoke the command that makes its probe mean
  something, so swapping `pg_isready` for `["CMD","true"]` is red;
- **names every entry on every run**, pass or fail, so the admission is standing
  rather than filed once;
- **refuses a declaration that matches nothing** (rule
  `stale-known-false-probe`), so the list cannot rot into permanent cover.

The admission also has a **human half**, because the audience that is not CI is
the person typing `docker compose ps` at 3am and reading `healthy` next to a
wedged api. `env/production.env.example` (beside the loopback ports that make it
actionable) and `README.md` both carry a *DIAGNOSING THIS RELEASE: IGNORE THE
`healthy` COLUMN* paragraph giving the `curl` commands that do tell the truth.
Rule `known-false-undisclosed` fails when the list is non-empty and either file
lacks it — and it fails in both directions, so **the list and the paragraphs are
deleted in the same PR**.

**That list must be empty before VZ-ISSUE-004's boot lane lands.** The boot lane
and `vizra deploy` are both written against `--wait` / `ps --status healthy`, and
a green that cannot go red is how a false gate becomes permanent. What empties
it is a `vizra healthcheck` subcommand in `vizra-core` mirroring
`vizra-search`'s — requested from the core owner and on its queue; **not** made
here. A `/dev/tcp` shell bridge was considered and rejected by the chair: it
would bake a bash dependency into a runtime image a queued core slice rebuilds
from a clean base.

### What the checkers close that a reader might assume

- **Every profile is rendered.** A service on a profile no shape enumerates is
  never rendered and therefore never asserted — a `backup` or `debug` profile
  with an open datastore port would have left the lane green. Rule
  `profile-not-enumerated` closes the set: every `profiles:` name in the compose
  files must be covered by at least one shape.
- **Third-party images need a digest, Vizra images need a release tag.**
  ADR-001 pins PostgreSQL and Valkey by digest; the rule now requires
  `@sha256:` for every image that is not a declared release image, so
  `postgres:18` cannot quietly replace a digest.
- **A disabled healthcheck is disabled in every spelling.** `disable: true`,
  `test: ["NONE"]` and `test: NONE` are one state, not two caught and one
  missed.
- **The port allowlist is protocol-aware**, so an entry that reads "may answer
  on 8080" does not also permit 8080/udp.
- **Rendered models are redacted before they are written**, and the leak check
  runs on the object being serialised. `redact_keys` drives the redaction and
  `secret_keys` drives the check; because they are independent lists, deleting a
  key from the first makes the renderer fail rather than write a file that is
  less redacted than its own stamp claims.

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

*(Written 2026-09-15, when nothing existed. Updated 2026-09-21 by VZ-ISSUE-002.)*

The compose topology, the env templates, the component key registries and the
`validate`-lane assertions now exist — see §2a, which also lists every place the
build deviates from §1 and §2 and why.

Still absent, and not to be read as existing anywhere above: `install.sh`,
`bootstrap.sh`, `vizra setup`, `deploy/` and its scripts, the operator CLI's
`doctor`/`deploy`/`backup`/`restore`/`rollback`/`release` subcommands, the
deployment bundle builder, `releases/<tag>.json`, the `bundle` and `boot` lanes,
and any published image. Sections 3–7 remain targets.

`docs/quality/features.json` carries the obligations; issues `VZ-ISSUE-001…`
under `docs/issues/` carry the slices. Every entry in that ledger is still
`PLANNED`/`UNVERIFIED`: the generator (`docs/evidence/ledger-generator/build.py`)
asserts that for every requirement, so no slice can record implementation status
there until its owner relaxes that rule to the one the file's own notice states
("no entry may be marked IMPLEMENTED or VERIFIED without recorded evidence").
Evidence therefore lives under `docs/evidence/` and in `docs/plans/` until then.
