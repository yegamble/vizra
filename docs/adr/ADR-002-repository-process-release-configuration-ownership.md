# ADR-002: Repository, process, release and configuration ownership

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` fixes the meta-repo shape; `docs/DEFINITION_OF_DONE.md` requires
fail-closed gates, a reviewed required-check manifest, and owner review on
workflows, gate scripts, release manifests, migrations and privacy/auth modules.
Four repositories, one release train and one env file mean ownership of every
contract — API, database, configuration, release record, merge gate — must be
assigned before the first PR, or the same fact ends up defined twice.

## Decision
**Repositories and entry points.** The shape is `docs/META_REPO.md` as decided.
`vizra-core` is one Go module, one image and three entry points: `cmd/api` (never
decodes pixels), `cmd/worker` (runs libvips), and `cmd/vizra`, which orchestrates
compose and runs setup, doctor, migrate, backup and restore.

**Search service and boundary (Q-001).** The ratified ruling is the decision, copied
in full:

> "`vizra-search` is created in M0 as a real minimal service, not a placeholder:
> `/healthz`, `/readyz`, `/version`, and HMAC-verified
> `/internal/v1/search|suggestions|events` that return an explicit `not_indexed`
> status which core treats as fallback; it reports no `search_schema_version` until
> it owns migrations. Its CI lanes test exactly that (nothing skipped or fake). The
> boundary is frozen in core at M0: `internal/search` with a permanent `sql`
> implementation (PostgreSQL FTS/trigram, permission-aware) and a `remote` client;
> the internal contract is written in core's canonical OpenAPI and drift-checked in
> both repos; search-owned tables live in PostgreSQL schema `search` of the core
> database (one DSN, one `pg_dump`) in a migration directory owned by
> `vizra-search`; search never writes core tables and core never reads schema
> `search`. Topology: `SEARCH_MODE=off|managed|external`; `off` is the default until
> VZ-SEARCH-001/003/004 land in **M3**, when `managed` becomes the core-profile
> default (the core release claim keeps VZ-SEARCH-004). A configured but unreachable
> or misconfigured search is a hard `doctor` FAIL and a degraded readiness signal
> while requests are still served from SQL — never a silent fallback. Search is
> never a hard dependency."

**Configuration ownership.** The env file is boot truth. `internal/config`
exposes `Load()`, `LoadFrom(lookup)` and `CheckEnv(map)` so setup, doctor and CI
validate candidate env files with the boot code itself. `validate()` collects all
errors rather than returning the first. Production mode refuses dev secrets, short
secrets, wildcard CORS, plain-http origins unless explicitly allowed, and every
dev escape hatch by name. `setup.Check` forces production mode when the env file
omits it.

**Runtime settings.** A registry table `instance_settings` with snake_case keys
overlays env defaults; the effective value is `setting AND boot`; secrets never
enter a queryable table. Replicas invalidate each other through a version counter
row bumped in the write that persisted the setting and polled every 10 s with
jitter; polling is chosen over `LISTEN/NOTIFY` and cache pub-sub, and the
reasoning is recorded here.

**Probes.** `/healthz` is liveness only. `/readyz` is drain-aware with a 2 s
single-flight cache: PostgreSQL down yields 503, everything else yields 200
`degraded` with the components named — including search misconfigured or
unreachable (Q-001) and worker oldest-queued-job age above threshold (Q-028).
`/version` reports module versions, image digest, the libvips loader list and the
schema ledger version. `/schemaz` always returns 200.

**Release and deploy.** `releases/<tag>.json` at `schema_version` 1 keeps Vidra's
shape — `release`, `meta_commit`, `core_schema_version`, `search_schema_version`,
`components.{core,user,search}.{tag,commit,image.{repository,index_digest,platforms}}`,
`evidence` — and is validated strictly at read. Ordering is enforced in both the
script and compose: core migrate → independent ledger re-read → search migrate →
`up -d --no-build`, with api and worker declaring
`depends_on: migrate: service_completed_successfully`.

**Rollback floor.** One embedded-migrator tag floor `[to confirm in M0]`, asserted
identical across every script by meta CI; `vizra update` refuses an image whose
embedded maximum migration is below live `/schemaz`; restore preflight refuses
too-new or dirty dumps before dropping anything; CI carries an
N-1-migrator-no-op lane and an N-1-suite-against-N-schema lane.

**Migration discipline** goes beyond Vidra: migrate-lint with Vidra's rules, plus
append-only immutability (a checksum manifest of merged migrations, CI failing on
any edit), a filename-format check, sequence gap and duplicate detection, and a
mandatory down file or an explicit `-- no-down: <reason>`.

**Contracts.** The hand-written `vizra-core/api/openapi.yaml` is the API source. A
route↔spec contract test fails in both directions (route without spec, spec
without route), with status and schema contract tests beside it. The TypeScript
client is generated into one committed file in `vizra-user` with byte-for-byte
drift CI, and sqlc output is guarded by `sqlc diff`.

**Compose (Q-017, as ratified).** Compose ≥ **2.24.4** is required — the documented
minimum for `!override`; `!reset` has no documented minimum (source-traced to
2.18.0), so nothing security-relevant may depend on it. The floor is refused at
runtime by `install.sh`, `deploy`, `rollback`, `restore` and `doctor`, failing
closed on an unparseable version string, and the parser must accept major versions
above 2 (Compose is at 5.5.1; the 2.x line ended at 2.40.3). The base
`docker-compose.yml` publishes **no ports at all**; developer port mappings live in
`docker-compose.override.yml` bound to 127.0.0.1; `!reset`/`!override` remain for
`build:` and legacy shapes but are never the only thing closing a port. The
production overlay is an explicit `-f` chain; external-datastore overlays and
`SEARCH_MODE` select topology; Valkey runs with `maxmemory`, `allkeys-lru` and no
persistence.

M0 CI asserts on the rendered production chain: (a) with every optional profile
enabled, zero published ports except Caddy 80/443 (and the IPFS swarm port when
enabled); (b) the same assertion passes with the merge tags stripped from the
files; (c) renders are run on both the floor version and current Compose. SHOULD: a
sub-floor render is shown to be refused.

**CI fan-in and merge queue.** Every repository has one required check,
`ci-required`, reading `.github/required-checks.txt`, where anything other than
success — failure, cancellation, timeout, skip, never-ran — fails. `ci-required`
runs on both `pull_request` and `merge_group` events, so a merge-queue entry is
gated by the same check as the pull request. The rulesets require the
`ci-required` **context**, which means an untriggered workflow leaves the merge
blocked rather than invisibly unchecked. The fan-in guard additionally rejects
`continue-on-error` on any required lane and rejects an empty test selection — the
two VZ-CI-001 negative cases — and the drift job compares the live ruleset against
both checked-in files, `.github/expected-ruleset.json` and
`.github/required-checks.txt`.

**Branch protection and rulesets (Q-032).** The required configuration is:

1. a ruleset on `main` in all four repositories — `vizra`, `vizra-core`,
   `vizra-user`, `vizra-search`;
2. require a pull request before merging;
3. require the status check `ci-required`;
4. block force-pushes;
5. block branch deletion;
6. require linear history;
7. CODEOWNERS requiring owner review for workflows, gate scripts, the required-check
   manifest, migrations, `internal/auth*`, `internal/authz` and `internal/privacy`;
8. a drift-check job comparing the live ruleset against the checked-in
   `.github/expected-ruleset.json` **and** `.github/required-checks.txt`, failing
   on any difference between the live configuration and either file;
9. application happens after PR1 lands, because `ci-required` must exist before it
   can be required;
10. until protection is confirmed applied, no ledger entry may reach VERIFIED on CI
    evidence alone.

**Logging and redaction (cross-cutting rule, VZ-OPS-005).** No process ever logs
credentials, signed URLs, session ids, API keys or raw private metadata. A
redaction layer sits in the logger and in every subprocess stderr capture, so a
tool that echoes a presigned URL cannot put it in a log line. Tests assert the
redaction: a log call carrying each of those value classes is shown to emit the
redacted form, and the subprocess-capture test does the same for stderr. This rule
binds every repository, not only core.

**Self-merge.** With one human, "never self-merge" is satisfied by an independent
verification session — Codex or a fresh Claude session — posting its evidence on
the PR before the owner merges. GitHub rulesets cannot enforce that, and this ADR
states it plainly rather than implying a setting covers it.

## Consequences
Positive: one seam (`LoadFrom`) makes setup, doctor and CI agree with boot; one
required check turns a missing lane into a red merge; the release record keeps its
three-component shape from M0, so no "absent component" path is ever written.
Negative: four repositories multiply the CI surface and the drift job; append-only
immutability means a bad merged migration is fixed only by a newer one. Risks: a
ruleset applied before `ci-required` exists blocks every merge, and a
required-checks manifest edited in the same PR as the code it guards defeats the
gate — hence CODEOWNERS. Later milestones must not break: deploy ordering, the
both-direction OpenAPI test, `sqlc diff`, the append-only manifest, `/schemaz`
always 200, port closure, and "a skipped required lane is not a pass".

## Precedent
Copied from Vidra (survey citations): the config seam
`Load()`/`LoadFrom(lookup)`/`CheckEnv`, the collecting `validate()` and the
fail-secure production block
(`C/internal/config/config.go:1157,1167,1424,1449,1491,1718-1760,2716`);
`setup.Check` forcing production (`C/internal/setup/setup.go:671-682`); the
settings doctrine (`M/docs/productionization/interfaces.md:8-18`) and version
poller (`C/internal/settingsversion/poller.go:25-76`); the probe set
(`C/internal/httpapi/server.go:1427-1430`, `health.go:74`, readiness
`:265,69,285,302-318`, `version.go:23`, `schema.go:63`); the release record
(`M/releases/v0.6.6.json`; `M/deploy/release-record.py:67,150,209`); deploy
ordering (`M/deploy/deploy.sh:14-19,634,650,697-703,708,711,715`;
`C/docker-compose.yml:986,1101`); the rollback floor and schema gate
(`M/.github/workflows/meta-ci.yml:230`; `C/cmd/vidra/update.go:538,572,726`;
`M/deploy/restore.sh:320`); `make ci` with the contract tests and `sqlc diff`
(`C/Makefile:107,120,190`;
`C/internal/httpapi/openapi_contract_test.go:127`); the generated client with
byte-for-byte drift CI (`U/scripts/codegen.mjs:40`;
`U/.github/workflows/contract-ci.yml:52,65-75`); and the fan-in where a skipped
lane never passes (`M/.github/workflows/ci-required.yml`,
`M/.github/required-checks.txt`).

Unlike Vidra, whose migrate-lint has no append-only immutability check, no
filename-format lint, no sequence-gap detection and no required down file — one
migration ships without one (`C/scripts/migrate-lint.sh:130-201`) — Vizra adds all
four.

## Evidence and ratification
Q-001 (search from M0, degraded readiness), Q-002 (no branding repo), Q-008
(tenancy plumbing), Q-017 (Compose floor and port closure), Q-028 (queue-age
threshold feeding readiness) and Q-032 (ruleset mechanism and the VERIFIED
restriction) in the `docs/OPEN_QUESTIONS.md` ratification record; the Compose
floor is verified in `docs/evidence/research-2026-09-15/ratification-facts.md` §4.

## Ledger IDs
VZ-FOUND-001, VZ-FOUND-002, VZ-FOUND-003, VZ-FOUND-005, VZ-FOUND-006, VZ-CI-001,
VZ-CI-002, VZ-CI-005, VZ-TOPOLOGY-001, VZ-OPS-001, VZ-OPS-002, VZ-OPS-005,
VZ-UPGRADE-001, VZ-UPGRADE-002, VZ-SEARCH-004, VZ-ADMIN-002.

## M0 obligations
The M0 foundation issue implements `internal/config` with `LoadFrom` and the
production refusals plus their negative tests, the four probes, `make ci` with
migrate-lint and the append-only manifest, `api/openapi.yaml` with the probe
operations and both-direction contract tests, sqlc with its diff guard, and the
workflows with `required-checks.txt` and `ci-required` on `pull_request` and
`merge_group`.

The Q-001 boundary is M0 work, not a reservation: the `internal/search` package
with the `Searcher` interface (`Search`, `Suggest`, `Publish(event)`); the `remote`
HMAC client that treats an explicit `not_indexed` status as fallback rather than as
an error; a `sql` implementation that returns empty results, because no product
tables exist yet; the internal contract paths under `/internal/v1/` written in
`api/openapi.yaml` and drift-checked in both repositories; and readiness reporting
`search: off|ok|degraded`. `vizra-search` itself ships the minimal real service
with the same contract and its own drift check.

Reservation only: the settings registry and its version counter row are M0 schema
driven from the admin UI in M2 (VZ-ADMIN-002); the release record, deploy
ordering, rollback floor and compose topology are specified here and implemented
under VZ-UPGRADE-001, VZ-UPGRADE-002 and VZ-TOPOLOGY-001; the rulesets are an
owner action after PR1.

