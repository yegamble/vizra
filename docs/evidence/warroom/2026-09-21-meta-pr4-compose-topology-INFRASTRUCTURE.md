# meta PR #4 (compose topology) — `vizra-infrastructure` seat review

- **PR:** yegamble/vizra#4, branch `feat/m0-compose-topology`
- **Reviewed SHA:** `69e197e1583d9adb90b0130b4a7c28d78b0878a3`
- **Reviewer:** `vizra-infrastructure` council seat (agent `a6b0af00083da9181`), read-only; rendered the all-optional production model with `docker compose … config --format json` (Compose v5.5.1), started nothing
- **Date:** 2026-09-21
- **Kind:** specialist review, not a verifier verdict. The independent verifier's file for this SHA is separate.

## Chair ruling (2026-09-21, tick 76)

**PR #4 is HELD — four blocking specialist findings are open (merge condition 4).**

1. **F1 (retired key delivered by compose) — BLOCKING, and it fixes the merge order.** `SEARCH_HMAC_KEY` is already ruled canonical on both sides. Order: vizra-core PR #6 (which retires `VIZRA_SEARCH_HMAC_KEY` and refuses it in production on presence) merges first if its verifier passes; meta PR #4 then delivers `SEARCH_HMAC_KEY` only, deletes alias entry 1, bumps `env/registry/core.json.source_commit` to the core `main` commit that declares the key, and gains the `retired_keys` checker rule with its red demonstration. PR #4 does not merge while the two spellings disagree with the core commit it names. Never both names.
2. **F2 (template promises `vizra setup --rotate`) — BLOCKING** under the standing "no false guarantee merges" ruling: a template sentence that invites an operator to destroy every MFA secret is the exact class that ruling exists for. Replace with the truth; add the template-claims check with a red demonstration.
3. **F3 (healthcheck that cannot fail gates `frontend`) — BLOCKING.** Chair's choice between the seat's two options: **no `/dev/tcp` bridge.** It would bake a bash dependency into the runtime image that queue 2d is about to rebuild from a clean base. Instead, in this PR: `frontend → api` becomes `service_started` + `required: false` (also closes F8b); the `vizra version` probes are registered as known-false in `compose-shapes.json`; `check-compose-topology.py` gains `probe_gates_readiness` — it fails any `service_healthy` edge onto a known-false probe and prints every liveness-only probe by name on every run. The durable fix stays queue 2h (`vizra healthcheck` in core); the known-false list must be empty before the boot lane (VZ-ISSUE-004) lands.
4. **F4 (worker default contradicts its comment; no memory limits) — BLOCKING** as the seat argues: the installer copies this template verbatim. Default 2, corrected comment, `mem_limit` on every long-running production service via `${…:-default}`, `missing-mem-limit` rule with a red demonstration.
5. **Cheap follow-ups folded into the same fix round** (one-line or doc-only, no new mechanism): F6 `stop_grace_period` on postgres/clickhouse; F9 the dangling `env/external-postgres.env.example` pointer; F10 the amd64-only line in the production template; F5 the comment stating the media volume has no writer until VZ-MEDIA-001. **Queued, not in this PR:** F5's core Dockerfile `mkdir`/`chown` (→ queue 2d), F6's grace-ordering assertion, F7 (declared network name + external-TLS instructions + forwarded-header question → VZ-ISSUE-004 and a core question), F8a digests in release records (→ VZ-ISSUE-004 / VZ-UPGRADE-002), F11 rotation runbook (→ VZ-ISSUE-004).
6. The fix round is sent once, consolidated with the independent verifier's findings on `69e197e` when that verdict arrives. Round 1 of 2.

The seat's report follows verbatim.

---

Confirmed `git -C /Users/yosefgamble/github/vizra/.claude/worktrees/meta-compose rev-parse HEAD` = `69e197e1583d9adb90b0130b4a7c28d78b0878a3` on `feat/m0-compose-topology`. I rendered the all-optional production model read-only (`docker compose … config --format json`, Compose v5.5.1, dummy env in the scratchpad) — nothing was started.

## What is well built

The deploy ordering is right and it is the hard part. `postgres → migrate(one-shot, `restart: "no"`) → api` with `service_completed_successfully` is exactly the Vidra shape, and the `required: false` on `worker → migrate` is a genuinely subtle fix for the split topology that most people discover only after Compose rejects the project. A cold `up` with a 40-second PostgreSQL is fine: `start_period: 30s` + 10×10s gives ~130 s of headroom, migrate waits, api waits behind migrate, and a failed migration leaves the *previous* api running rather than a half-upgraded stack. `build: !reset null` on every buildable service — including the one-shot — is the thing that makes a checkout-free bundle host possible and stops a Go toolchain compiling mid-deploy; the reasoning comment on it is better than most production runbooks. Splitting `migrate` into a separate `vizra` binary rather than argv on `vizra-api` structurally eliminates Vidra's worst deploy bug (`deploy/deploy.sh:118-126`, the one-shot that starts an API server and never exits). Search is genuinely not a hard dependency: `search` has no `depends_on`, nothing depends on it, and core defaults to `off`. Ports match the claim under every optional profile: only `caddy` 80/443 and IPFS 4001 face the network; postgres, redis and search publish nothing in any shape, including dev. The external overlays really do delete the container (`profiles: !override`) and really do cut the `depends_on` edges, and the `!override`-vs-`!reset` reasoning is correct and non-obvious. Digest-pinned third-party images, capped logs on one-shots too, `no-new-privileges` in the *base* rather than only prod, `create_host_path: false` on the Caddyfile bind, and the refusal to invent `CLICKHOUSE_URL`/`IPFS_API_URL`/`SEARCH_REDIS_URL` keys that no process reads — all correct calls.

## Where it fails the operator

Four things are cheap now and expensive once `install.sh`, `vizra setup` and the boot lane build on them: a rename landmine that will dead-stop every core container the moment a sibling PR merges, a template sentence that will silently destroy MFA secrets, a healthcheck that is a lie *and* is used as a gate, and a worker default that contradicts its own comment on the minimum supported host with no memory limit to contain it.

---

# BLOCKING-BEFORE-MERGE

```
FINDING 1: the compose files inject a variable vizra-core is about to refuse by name
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docker-compose.yml:89-98; env/registry/aliases.json:6-20;
             docs/META_REPO.md §2a (alias paragraph);
             vizra-core/internal/config/keys.go:85-99;
             vizra-core/internal/config/config.go:335-357
  requirements: VZ-TOPOLOGY-001, VZ-INSTALL-002

Observed:
  docker-compose.yml:98 delivers the shared secret to api, worker and migrate as
      VIZRA_SEARCH_HMAC_KEY: ${SEARCH_HMAC_KEY:?SEARCH_HMAC_KEY must be set ...}
  and only under that spelling (confirmed in the rendered model: api has
  VIZRA_SEARCH_HMAC_KEY=True, SEARCH_HMAC_KEY=False).
  vizra-core `main` is c043df7, where VIZRA_SEARCH_HMAC_KEY is still the name
  core reads — so the file is correct against main today.
  vizra-core `chore/m0-hardening-a` (HEAD f56dc03, commit 2ceac77, IN FLIGHT NOW)
  moves it to `RetiredKeys` (keys.go:92-99) and config.go:347-357 refuses it in
  production ON PRESENCE with any non-empty value:
      "was renamed to SEARCH_HMAC_KEY and is NO LONGER READ ... production will
       not boot believing a key is configured when none is."
  The chair has already ruled SEARCH_HMAC_KEY canonical.

Failure:
  The instant core's hardening PR merges and an operator pulls a core image built
  from it, `vizra migrate`, `vizra-api` and `vizra-worker` all refuse to boot. The
  deploy fails at the migrate one-shot. The refusal message names
  VIZRA_SEARCH_HMAC_KEY — a string that appears NOWHERE in the operator's
  env/production.env, because compose injects it. The operator greps their env
  file, finds SEARCH_HMAC_KEY set exactly as the template told them, and has no
  path forward without reading docker-compose.yml. That is the 3am scenario.
  Secondary: with the retired name refused, core also has no search key at all.

Perspective: operator

Recommendation:
  Land the two renames as one gated change. Either (a) hold this PR until core's
  rename merges, then flip docker-compose.yml:98 to
  `SEARCH_HMAC_KEY: ${SEARCH_HMAC_KEY:?...}` and delete alias entry 1 from
  env/registry/aliases.json in the same commit; or (b) merge this PR now with a
  recorded merge-order constraint in docs/META_REPO.md §2a and
  `env/registry/core.json` `source_commit` bumped, and make core's hardening PR
  blocked-on this flip. Do not attempt to set both names — the retired one is
  refused on presence, so a "belt and braces" map is a guaranteed boot refusal.

Acceptance criteria:
  - The rendered production model delivers exactly one of the two spellings, and
    it is the one the pinned core image reads.
  - `env/registry/core.json.source_commit` names a core commit that actually
    declares the key the compose file sends.
  - `scripts/check-config-coverage.py --drift` FAILS (not passes, not skips)
    against a core checkout where the spellings disagree.
  - Negative case: rendering against a core snapshot listing the name as retired
    is a checker failure, not a green run.

Tests:
  `scripts/check-config-coverage.py` gains a `retired_keys` list in
  env/registry/core.json and fails when a compose `environment:` map delivers a
  retired name. Red demo: add VIZRA_SEARCH_HMAC_KEY to the snapshot's retired
  list and show the checker fail; remove it and show it pass. Harness exists
  (the validate lane); the retired-key concept does not.

Cross-repo implications:
  core: must publish the rename in a release note; consider keeping the retired
        entry for two releases so the message is reachable. user: none.
        search: none — it already reads SEARCH_HMAC_KEY. meta: alias floor 2 → 1.

Challenge:
  "core main doesn't have the rename, so this PR is correct as merged." True
  today. The finding is that the two repos are one merge apart from a dead
  instance, and nothing in either repo enforces the order. The cost of recording
  the constraint now is one paragraph.
```

```
FINDING 2: the env template promises MFA-key rotation that nothing implements
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     env/production.env.example:69-72, 5-6; docker-compose.yml:85
  requirements: VZ-INSTALL-002, VZ-BACKUP-001

Observed:
  env/production.env.example:70-72 reads:
      # ROTATING THIS RE-SEALS STORED MFA SECRETS. `vizra setup --rotate` requires
      # --yes-i-know for exactly this key.
      VIZRA_MFA_KEY_KEK=
  `vizra setup` does not exist. `vizra` at core HEAD has exactly three
  subcommands: version, doctor, migrate (vizra-core/cmd/vizra/main.go:33-39).
  docker-compose.yml:85 passes the KEK straight through as an environment value.

Failure:
  An operator reads "rotating this re-seals stored MFA secrets", edits
  env/production.env, and restarts. Nothing re-seals anything: every TOTP secret
  in the database is still sealed under the OLD key and is now permanently
  undecryptable. Every MFA-enrolled member is locked out with no recovery path
  short of admin-disabling MFA per account. The sentence that caused it is the
  one the operator trusted. This is the single most destructive action the
  template currently invites, and it is invited in a file whose whole job is to
  be edited by hand.

Perspective: operator, member

Recommendation:
  Replace the sentence with the truth, in the template and in docker-compose.yml:85's
  `:?` message:
      # DO NOT CHANGE THIS VALUE BY HAND AFTER FIRST BOOT. It seals stored MFA
      # secrets; editing it here does NOT re-seal them and every enrolled member
      # is permanently locked out. Re-sealing rotation arrives with
      # `vizra setup --rotate` (VZ-ISSUE-004). Back this file up with the database.
  Same treatment for VIZRA_SESSION_SECRET: say plainly that changing it signs
  every session out.

Acceptance criteria:
  - No template line claims a capability with no implementation; grep for
    "--rotate"/"setup" in env/*.example returns only text marked as future.
  - The warning names the consequence (locked-out members), not the mechanism.
  - When `vizra setup --rotate` lands, the template line changes in the same PR.

Tests:
  Doc-level. Smallest harness: extend scripts/check-doc-links.py (or a new
  scripts/check-template-claims.py) with a deny-list of command names that must
  exist in env/registry/*.json `commands` before a template may reference them.
  Red demo: reintroduce the current sentence and show the checker fail.

Cross-repo implications:
  core: `vizra setup --rotate` must, when it lands, re-encrypt MFA rows inside a
        transaction and refuse without --yes-i-know. user/search/meta: none.

Challenge:
  "It documents the target state, which the section header already frames as
  future." It does not — lines 25-35 carefully list what is NOT yet carried, and
  the KEK line is not in that list, so it reads as current behaviour.
```

```
FINDING 3: api/worker healthchecks always pass, and `frontend` gates on one
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docker-compose.yml:215-227 (api), 258-264 (worker), 291-293
             (frontend depends_on api: service_healthy);
             scripts/check-compose-topology.py:325-333;
             vizra-core/Dockerfile:141-142; vizra-core/internal/httpapi/probes.go:63-82
  requirements: VZ-OPS-001, VZ-OPS-002, VZ-TOPOLOGY-001

Observed:
  Both probes are `["CMD", "/usr/local/bin/vizra", "version"]` — a CLI that
  prints build info and exits 0 without opening a socket or touching PostgreSQL.
  The builder says so honestly at docker-compose.yml:216-222 and in META_REPO §2a.
  The rendered model shows frontend gated on it:
      frontend depends_on: {"api": {"condition": "service_healthy", "required": true}}
  check-compose-topology.py:325-333 REQUIRES a healthcheck on every long-running
  service with the reason "cannot gate a depends_on" — so the gate rewards the
  placeholder. core does have the real probes (/healthz liveness, /readyz that
  503s only on PostgreSQL and reports `degraded` with the component named).

Failure:
  api wedged with PostgreSQL unreachable, or listening but deadlocked: Docker
  reports `healthy`, `docker compose ps` reports `healthy`, frontend starts and
  serves errors, and VZ-ISSUE-004's boot lane and `vizra deploy`'s probe step
  will read the same green. A probe that returns healthy while the API is dead is
  worse than no probe, and it is the specific failure this council was told to
  catch. It also means the `service_healthy` edge on frontend buys nothing while
  costing a frontend-only topology (required: true — see finding 8).

Recommendation (smallest, entirely inside this repo, no core change needed):
  The runtime image is debian-based (vizra-core/Dockerfile:25,105) and has bash,
  so probe the real listener without curl:
      test: ["CMD-SHELL", "exec 3<>/dev/tcp/127.0.0.1/8080 && printf 'GET /readyz HTTP/1.0\\r\\n\\r\\n' >&3 && head -1 <&3 | grep -q ' 200'"]
  and for worker, which has no listener, drop to `["CMD-SHELL", "exec 3<>/dev/tcp/127.0.0.1/9090 && ..."]` against VIZRA_METRICS_ADDR.
  If bash-in-image is judged too fragile, the alternative is the documented one:
  ask vizra-core for a `vizra healthcheck` subcommand identical to
  vizra-search's (which already has exactly that — docker-compose.yml:338-340) —
  but then the `service_healthy` gate on frontend must become `service_started`
  in THIS PR, and the placeholder must be registered as a known-false probe that
  check-compose-topology.py names in its output, so the boot lane cannot inherit
  it silently.

Acceptance criteria:
  - No `depends_on: {condition: service_healthy}` edge in the tree points at a
    service whose probe cannot fail while the service is broken.
  - The topology checker either asserts the probe reaches the service's own
    listener, or emits a named WARN listing every liveness-only probe, and that
    list is empty by the time the boot lane lands.
  - Negative case: with PostgreSQL stopped, the api container reports unhealthy
    within 3 intervals. (Boot lane, VZ-ISSUE-004.)

Tests:
  scripts/check-compose-topology.py gains a `probe_gates_readiness` rule with a
  known-false allow-list read from compose-shapes.json. Red demo: point the rule
  at `vizra version` and show it fail. The boot-lane proof does not exist and is
  named as VZ-ISSUE-004's.

Cross-repo implications:
  core: `vizra healthcheck` subcommand (mirroring vizra-search) is the durable
        answer; the /dev/tcp form is the bridge. user: none. search: already correct.

Challenge:
  "Nothing boots in M0, so a fake probe harms nobody yet." It harms the next
  slice: the boot lane and `vizra deploy` will both be written against
  `--wait`/`ps --status healthy`, and a green that cannot go red is how a false
  gate becomes permanent.
```

```
FINDING 4: worker default contradicts its own minimum-host comment, with no memory limit anywhere
Severity:    REQUIRED  (blocking-before-merge: the installer will copy this template verbatim)
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     env/production.env.example:172-173; docker-compose.yml (no mem_limit
             on any service); rendered model: every service mem_limit=None,
             cpus=None, deploy.resources=None
  requirements: VZ-OPS-007, VZ-OPS-008, VZ-INSTALL-001
  precedent: /Users/yosefgamble/github/vidra/docker-compose.prod.yml:346-350 (api
             cpus/mem_limit/stop_grace_period), :398-403 (worker), :546-547 (ipfs)

Observed:
      # 1 on the minimum supported host (2 vCPU / 4 GB). libvips is memory-hungry.
      VIZRA_WORKER_CONCURRENCY=4
  The comment prescribes 1; the shipped value is 4. No service in the rendered
  production model declares mem_limit, cpus or deploy.resources. Vidra — the
  precedent the owner asked to be mirrored — sets all three on api, worker and ipfs.

Failure:
  On the 2 vCPU / 4 GB host the installer targets, four concurrent libvips
  decodes of large originals exhaust RAM. With no cgroup limit on any container,
  the kernel OOM killer picks by badness score, and on a Docker host that is
  routinely PostgreSQL (largest RSS, shared memory). The operator's symptom is
  not "uploads are slow" — it is PostgreSQL killed mid-write, crash recovery on
  restart, and an instance that looks broken for reasons that have nothing to do
  with the upload they were processing. `restart: unless-stopped` then brings it
  back and the cycle repeats under load.

Perspective: operator, photographer

Recommendation:
  Two lines and one default:
  - env/production.env.example: VIZRA_WORKER_CONCURRENCY=2 with the comment
    corrected to say 1 on 4 GB, 4 from 8 GB up.
  - docker-compose.prod.yml: `mem_limit: ${VIZRA_WORKER_MEM_LIMIT:-1500m}` on
    worker and `${VIZRA_API_MEM_LIMIT:-768m}` on api (mirroring Vidra's shape,
    scaled to the documented floor host), with the two keys in the template.
  A limit that OOM-kills the worker is recoverable; one that OOM-kills PostgreSQL
  is not.

Acceptance criteria:
  - No template comment prescribes a value different from the value it ships.
  - Every long-running service in the production model declares mem_limit;
    check-compose-topology.py fails if one does not (same shape as the existing
    missing-log-cap rule).
  - The limits are named in a capacity note so VZ-OPS-007 has a starting budget.

Tests:
  New `missing-mem-limit` rule in scripts/check-compose-topology.py, red-demoed
  by deleting one mem_limit. Same harness as the log-cap rule.

Cross-repo implications:
  core: none (the knob exists). user/search/meta: none.

Challenge:
  "Limits are host-specific; guessing wrong throttles a big instance." That is
  what the `${…:-default}` indirection is for — and Vidra already made this call
  in production, so the argument has been tested.
```

---

# FOLLOW-UPS (named slice)

```
FINDING 5: the media volume has no consumer, so "originals are backed up" will be false
Severity:    REQUIRED
Confidence:  high
Slice:       VZ-MEDIA-001 / VZ-BACKUP-001 (VZ-ISSUE-004's backup.sh)

Affected:
  repo:      vizra (meta)
  files:     docker-compose.yml:204-205 (api), 242-243 (worker), 435-441 (volumes);
             vizra-core/internal/config/keys.go:50 (only VIZRA_STORAGE_PREFIX);
             vizra-core/Dockerfile:130-135 (USER 10001, no /var/lib/vizra/media)
  requirements: VZ-BACKUP-001, VZ-BACKUP-002

Observed:
  `media_data:/var/lib/vizra/media` is mounted on api and worker. vizra-core's
  config registry has no storage-root key at all — only VIZRA_STORAGE_PREFIX
  ("key prefix ... never a hardcoded root"). Nothing in core reads that path.
  vizra-core/Dockerfile creates /var/lib/vizra (home, uid 10001) but not
  /var/lib/vizra/media, and the container runs as USER 10001:10001.

Failure:
  Two, one now and one later.
  (a) Now: an operator who follows META_REPO §6 and backs up `vizra_media_data`
      archives an empty volume and believes their originals are safe. The volume
      exists, has a plausible name, and is empty for a reason no operator can see.
  (b) When the storage slice lands: Docker creates a mountpoint absent from the
      image as root:root, so a process running as uid 10001 cannot write to it.
      First upload on a fresh host fails with EACCES, on first boot, in front of
      the owner. UNVERIFIED — I did not boot a container to confirm Docker's
      ownership behaviour for this path; the fix is correct either way.

Recommendation:
  Keep the volume (re-mounting later is worse), but say what it is: a comment at
  docker-compose.yml:204 stating that no process writes here until VZ-MEDIA-001,
  and a line in env/production.env.example's "what this file does not yet carry"
  block. Separately, ask vizra-core for
  `RUN mkdir -p /var/lib/vizra/media && chown 10001:10001 /var/lib/vizra/media`
  in the runtime stage now, so the storage slice does not discover it on a host.

Acceptance criteria:
  - The volume's emptiness is documented where an operator planning a backup reads it.
  - A restore rehearsal (VZ-BACKUP-002) with the media volume populated produces
    byte-identical originals and a bootable instance.
  - The image declares the media directory with the runtime uid before any code
    writes to it.

Tests:  Boot lane (VZ-ISSUE-004): write a file as the container user into
        /var/lib/vizra/media and read it back. Harness does not exist yet.

Cross-repo implications:
  core: Dockerfile mkdir+chown; a storage-root key when VZ-MEDIA-001 lands.
  user/search/meta: none.

Challenge:
  "A volume with nothing in it harms nobody." It harms the person who checks
  their backup by looking at the file list rather than restoring it.
```

```
FINDING 6: PostgreSQL and ClickHouse get Docker's 10-second default stop grace
Severity:    REQUIRED
Confidence:  medium
Slice:       VZ-ISSUE-004 (deploy/restart runbook)

Affected:
  repo:      vizra (meta)
  files:     docker-compose.yml:118-143 (postgres), 351-372 (clickhouse);
             docker-compose.prod.yml:47-57, 106-107
  requirements: VZ-OPS-001, VZ-UPGRADE-001

Observed:
  Rendered model: api grace=30s, worker grace=30s, postgres/redis/clickhouse/
  caddy/ipfs grace=None → Docker's 10 s default, then SIGKILL.

Failure:
  `vizra deploy`, `compose restart` or a host reboot sends the stop signal to
  PostgreSQL; if a checkpoint or a long client transaction is in flight it is
  SIGKILLed at 10 s. Next start runs crash recovery — minutes of downtime on a
  large database at exactly the moment the operator is already anxious, and the
  fsync guarantees hold but nothing tells the operator why boot is slow. Worse on
  ClickHouse, which flushes on shutdown.

Recommendation:
  `stop_grace_period: 60s` on postgres and clickhouse in docker-compose.prod.yml.
  Also make api/worker's 30 s derived rather than fixed: core's DrainGrace is
  cfg.ShutdownGrace (vizra-core/cmd/worker/main.go:92) and
  VIZRA_SHUTDOWN_GRACE is operator-settable, so an operator who raises it to 60 s
  gets SIGKILLed at 30 s mid-drain with jobs' leases swept
  (vizra-core/internal/jobs/worker.go:222-224). Either spell it
  `stop_grace_period: ${VIZRA_STOP_GRACE:-30s}` with a template note that it must
  exceed VIZRA_SHUTDOWN_GRACE, or have check-compose-topology.py assert the
  inequality from the rendered model.

Acceptance criteria:
  - Every stateful service declares stop_grace_period explicitly.
  - Rendered stop_grace_period > VIZRA_SHUTDOWN_GRACE for api and worker, asserted.
  - A stop during a running job records the job's outcome (boot lane).

Tests:  New checker rule (grace ordering) + a boot-lane stop/restart case.

Cross-repo implications: core: none. meta: one checker rule.

Challenge:
  "The postgres image uses STOPSIGNAL SIGINT (fast shutdown), so 10 s is plenty."
  Usually true, and that is why this is REQUIRED and not a BLOCKER — but 10 s is
  not plenty on a 100 GB database mid-checkpoint, and an explicit number costs
  one line.
```

```
FINDING 7: external-TLS assumes the operator's proxy runs on the host, not in a container
Severity:    REQUIRED
Confidence:  high
Slice:       VZ-TOPOLOGY-006 / VZ-ISSUE-004

Affected:
  repo:      vizra (meta)
  files:     docker-compose.prod.yml:28-32, 76-81, 96-97;
             rendered model networks: {"default": {"name": "vizra_default"}}
  requirements: VZ-TOPOLOGY-006, VZ-INSTALL-002

Observed:
  docker-compose.prod.yml:30-31 states the loopback binds exist "so an external
  nginx can proxy them when VIZRA_TLS_MODE=external". The rendered model binds
  api to 127.0.0.1:8080 and frontend to 127.0.0.1:3000. The project declares no
  named network; Compose synthesises `vizra_default`.

Failure:
  The most common shape of "I bring my own proxy" in 2026 is nginx-proxy /
  Traefik / Caddy running as a container. From inside that container, 127.0.0.1
  is its OWN loopback — the Vizra api is unreachable, and the symptom is a
  connection-refused the operator will spend an hour attributing to Vizra. Their
  escape hatches are `docker network connect vizra_default <proxy>` or
  `networks: {vizra_default: {external: true}}` — both requiring a network name
  that is documented nowhere, is derived from the project name, and silently
  changes if they ever pass `-p`.
  Second half: nothing in the tree carries a trusted-proxy / forwarded-header
  setting. core's CSRF check compares against VIZRA_PUBLIC_ORIGIN
  (vizra-core/internal/config/keys.go:43), so an operator terminating TLS
  upstream must set VIZRA_PUBLIC_ORIGIN to the https origin while api receives
  plain http — whether core requires X-Forwarded-Proto handling for that to work
  is UNVERIFIED here and must be settled before the external-TLS path is offered.

Recommendation:
  Declare the network explicitly so its name is a contract, not an artefact:
      networks:
        default:
          name: ${VIZRA_NETWORK_NAME:-vizra_default}
  and add an "external TLS" block to env/production.env.example naming both
  options (join the network, or use host networking on the proxy) with the exact
  `docker network connect` command. Ask core whether the external-TLS shape needs
  a trusted-proxy key, and add it to the template in the slice that adds the reader.

Acceptance criteria:
  - The compose network name is stable, declared, and quoted in the external-TLS
    instructions.
  - An operator following the external-TLS instructions with a containerised
    proxy reaches the API, proven in the boot lane.
  - The CSRF/forwarded-header question has a recorded answer before
    VIZRA_TLS_MODE=external is offered by `vizra setup`.

Tests:  Boot lane: start the prod chain without `--profile edge`, attach a
        throwaway proxy container to the network, and curl through it.

Cross-repo implications:
  core: confirm forwarded-header/trusted-proxy behaviour behind a TLS-terminating
        proxy. user: PUBLIC_ORIGIN must match. meta: one network stanza + docs.

Challenge:
  "Host-installed nginx is the documented case and loopback is correct for it."
  Correct for it, and silently wrong for the other half of operators — which is
  why the answer is a documented network name, not a port change.
```

```
FINDING 8: rollback names a mutable tag, not a digest, and the frontend cannot run alone
Severity:    SHOULD
Confidence:  high
Slice:       VZ-UPGRADE-002 / VZ-TOPOLOGY-008

Affected:
  repo:      vizra (meta)
  files:     docker-compose.prod.yml:60,71,85,93,100 (`${VIZRA_*_TAG:?}` +
             pull_policy: always); docker-compose.yml:291-293 (frontend
             depends_on api required:true) vs 421-427 (caddy required:false)
  requirements: VZ-UPGRADE-001, VZ-UPGRADE-002, VZ-TOPOLOGY-008

Observed:
  (a) VZ-UPGRADE-002 is titled "Release records pin image DIGESTS and schema
      versions". The overlay pins mutable tags and forces `pull_policy: always`,
      so `VIZRA_CORE_TAG=v0.1.0` today and the same string next month are not
      guaranteed to be the same bytes. Third-party images ARE digest-pinned —
      the Vizra ones are not.
  (b) The rendered model shows frontend → api as `required: true`, while caddy's
      two edges are `required: false`. A frontend-only host is therefore an
      invalid compose project, by the same rule the worker edge was fixed for.

Failure:
  (a) A rollback re-pulls a tag that may have been re-pushed; the operator
      believes they restored a known artefact and did not. The release record
      cannot prove what ran.
  (b) The split topology VZ-TOPOLOGY-008 anticipates is only half renderable.

Recommendation:
  (a) Add optional `VIZRA_CORE_DIGEST` etc. to the release record and prefer
      `image: repo@${VIZRA_CORE_DIGEST}` when present, tag otherwise — or record
      the resolved digest in releases/<tag>.json at deploy time and have
      `vizra doctor` compare the running container's digest to it. Either closes
      VZ-UPGRADE-002; the second is cheaper and belongs to VZ-ISSUE-004.
  (b) `required: false` on frontend → api, matching caddy.

Acceptance criteria:
  - A rollback to the previous release starts a container whose image digest
    matches the one the release record names, asserted not assumed.
  - The prod chain with `--profile frontend` alone renders.

Tests:  A `prod-frontend-only` shape in scripts/compose-shapes.json (harness
        exists — this is one JSON entry). Digest assertion belongs to the boot lane.

Cross-repo implications: core: release workflow must emit digests. meta: shapes + overlay.

Challenge:
  "Vidra ships tags too." It does, and Vidra's ledger does not claim digests.
  Vizra's VZ-UPGRADE-002 does.
```

```
FINDING 9: the external-PostgreSQL path points at a file that does not exist, and accepts sslmode=disable
Severity:    SHOULD
Confidence:  high
Slice:       VZ-ISSUE-004 (`vizra doctor`) / VZ-BACKUP-003

Affected:
  repo:      vizra (meta)
  files:     docker-compose.external-postgres.yml:37-48, 59;
             env/production.env.example:87-104; `ls env/` (two .example files only)
  requirements: VZ-TOPOLOGY-002, VZ-BACKUP-003

Observed:
  The overlay header says "env/external-postgres.env.example therefore ships
  POSTGRES_PASSWORD with a placeholder that says so in its own value." That file
  does not exist; env/ contains only development.env.example and
  production.env.example. The production template does cover it (lines 87-90), so
  the behaviour is right and only the pointer is wrong.
  The `:?` message recommends `sslmode=require` but nothing enforces it, and the
  overlay's own header correctly notes that backup ownership moves to the
  provider — while the runbook that must say so does not exist yet.

Failure:
  An operator with managed PostgreSQL on a private network follows the header,
  looks for env/external-postgres.env.example, does not find it, and cannot tell
  whether they are missing a file or reading stale docs. Separately, a DSN
  pasted from a provider console with `sslmode=disable` is accepted silently —
  on a private network that is usually survivable, and it is exactly the kind of
  thing an operator wants told rather than discovered.
  What such an operator actually has to set today, and it should be stated in one
  place: DATABASE_URL (full DSN with sslmode), a non-empty placeholder in
  POSTGRES_PASSWORD, `-f docker-compose.external-postgres.yml` appended to the
  chain, and their own snapshot/PITR schedule because backup.sh will refuse.

Recommendation:
  Fix the pointer to env/production.env.example:87-90. Add a short "external
  PostgreSQL: what you must set" block to the production template listing the
  four items above. Make `sslmode=disable` on an external DSN a `vizra doctor`
  WARN when the host is not a compose-network name — VZ-ISSUE-004's job, named here.

Acceptance criteria:
  - No compose header references a file that does not exist
    (scripts/check-doc-links.py should cover compose comments, not just docs).
  - The external-PostgreSQL checklist is reachable from the template without
    reading a compose file.
  - VZ-BACKUP-003's restore rehearsal proves the provider path.

Tests:  Extend scripts/check-doc-links.py to scan docker-compose*.yml comments
        for `env/…`/`deploy/…` paths. Red demo: the current line.

Cross-repo implications: core: doctor check. meta: docs.

Challenge:
  "It's a comment." It is the comment an operator reads at the exact moment they
  are deciding whether their database is configured.
```

```
FINDING 10: amd64-only is stated in the one file an operator never opens
Severity:    SHOULD
Confidence:  high
Slice:       VZ-INSTALL-001

Affected:
  repo:      vizra (meta)
  files:     docker-compose.dev.yml:22-23; env/production.env.example:39-49
             (release record block, silent on architecture); docs/META_REPO.md §3
  requirements: VZ-INSTALL-001, VZ-INSTALL-004

Observed:
  "Apple Silicon: these are native arm64 builds for development only, with no
  support claim (Q-027). Published runtime images are linux/amd64." — in
  docker-compose.dev.yml, a file the production chain never loads and a
  production operator has no reason to read. The digest-pinned third-party
  images are multi-arch OCI indexes; only the three Vizra images are amd64-only.

Failure:
  An operator on an arm64 VPS (Ampere/Graviton/Hetzner ARM — cheap and common)
  fills in the production template, runs the chain, and gets
  `no matching manifest for linux/arm64/v8 in the manifest list entries` from
  the migrate one-shot, with PostgreSQL and Valkey already started and healthy.
  Everything upstream of the failure worked, which is the most confusing possible
  place to learn your host is unsupported.

Recommendation:
  One line at the top of env/production.env.example's release-record block:
  "Vizra images are published for linux/amd64 only (Q-027). An arm64 host is not
  supported; install.sh refuses one by name." Repeat it in README's install
  section when that lands.

Acceptance criteria:
  - The architecture constraint appears in the file an operator edits.
  - install.sh (VZ-ISSUE-001/004) refuses a non-amd64 server host by name before
    it pulls anything.

Tests:  Installer preflight test, VZ-ISSUE-004.
Cross-repo implications: core: release workflow may later add arm64. meta: docs.
Challenge: "META_REPO §3 already says it." §3 is a design document; the env
  template is the operator-facing surface and it is silent.
```

```
FINDING 11: no rotation or restart-order runbook for the three secrets the template mints
Severity:    SHOULD
Confidence:  high
Slice:       VZ-ISSUE-004 (`vizra setup --rotate`) / VZ-OPS-003

Affected:
  repo:      vizra (meta)
  files:     env/production.env.example:64-77; docker-compose.yml:84-85, 98, 332
  requirements: VZ-INSTALL-002, VZ-OPS-003

Observed:
  Three secrets are delivered as plain `environment:` values. The template says
  of SEARCH_HMAC_KEY "core and search must hold the same value at the same
  instant — there is no rotation window", which is accurate and is also the whole
  problem: it implies an atomic restart of two services and does not say how.
  Nothing states what rotating VIZRA_SESSION_SECRET does (signs every member out).
  VIZRA_MFA_KEY_KEK is covered by finding 2.

Failure:
  An operator responding to a suspected key leak at 3am has no documented order.
  Rotating the HMAC key by restarting core first produces a window of 401s from
  search; restarting search first produces the same in the other direction. With
  search off by default this is theoretical at M0 and stops being theoretical at M3.

Recommendation:
  A short "rotating a secret" section in the template (or docs/quality/COMMANDS.md)
  giving, per key: what it protects, what breaks during rotation, the restart
  order, and whether `vizra setup --rotate` will own it. For SEARCH_HMAC_KEY the
  honest answer at M0 is "stop both, change both, start both — search is off by
  default so this is a maintenance window, not a rolling change."

Acceptance criteria:
  - Every secret in the template names its rotation consequence and order.
  - The order is exercised once in the boot lane when that exists.

Tests:  Boot lane, VZ-ISSUE-004. No harness today.
Cross-repo implications: core: `--rotate` semantics. search: must document that it
  has no dual-key acceptance window. meta: docs.
Challenge: "Rotation is VZ-ISSUE-004's." The mechanism is; the sentence saying
  what breaks costs nothing and belongs beside the key.
```

---

# WHAT VZ-ISSUE-004 WILL NEED THAT IS NOT HERE

Not findings — inputs the next slice must supply, none of which forces a redesign of this PR:

- **`deploy/` does not exist.** `caddy` bind-mounts `./deploy/Caddyfile.local` with `create_host_path: false`, so `--profile edge` cannot `up` until `vizra setup` renders it. Correct sequencing, but the Caddyfile *template* and the nginx example for `--tls-mode external` are both still owed.
- **The engine that turns answers into `-f`/`--profile` arguments.** Today topology is selected by hand. `VIZRA_TLS_MODE`, `VIZRA_EXTERNAL_POSTGRES`, `VIZRA_EXTERNAL_REDIS`, `ANALYTICS_MODE`, `IPFS_MODE` have no reader and were deliberately left out of the template — the right call, but it means the wizard must own the whole mapping and the template must grow those keys in the same PR that gives them a reader.
- **`backup.sh` / `restore.sh` have nothing to enumerate.** The enabled-service inventory the operator's checklist requires (which profiles, which overlays, which volumes) is not written anywhere at deploy time. Record it in `releases/<tag>.json` or a `.vizra-topology` file during `vizra deploy`, or a restore onto a clean host cannot know whether ClickHouse was on.
- **The pre-deploy dump gate.** This topology supports the sacred ordering (`run --rm migrate` works because `build: !reset null` makes the one-shot non-buildable), but note that `up -d` will *also* run migrate via the `service_completed_successfully` edge. That is a safe belt-and-braces — a failed migration leaves the old api running — but `deploy.sh` must still take its dump before the discrete migrate step, and must warn-and-continue on external PostgreSQL exactly as Vidra's does (`/Users/yosefgamble/github/vidra/deploy/deploy.sh:604-608`).
- **`vizra doctor` already exists in core** (`cmd/vizra/doctor.go`, and it shells out to `docker compose version --short` at line 199) — it is the natural home for the Compose-floor assertion, the `sslmode=disable` warning, and the search-misconfigured FAIL that ruling Q-001 requires.

# NOT WORTH DOING

- **Docker secrets / `*_FILE` indirection instead of `environment:`.** Real exposure (`docker inspect`, `compose config`), but for a single-host self-hosted product it trades a familiar failure mode for an unfamiliar one, and the builder already redacts secrets from the CI-uploaded models. `vizra-security`'s call, not an operability blocker.
- **Splitting `postgres`/`redis` onto their own profiles so an external deploy needs no `POSTGRES_PASSWORD` placeholder.** The interpolation-before-profiles behaviour is a Compose fact, the builder diagnosed it correctly, and the placeholder is documented in the template. Fixing it properly means a second base file; not worth it.
- **Asserting the Compose version string.** Already correctly rejected — `compose-render.py` refuses below the floor and the checker proves the merge tags were honoured from the rendered model, which is the stronger test.
- **PostgreSQL tuning knobs (`shared_buffers` etc.) mirroring Vidra.** PostgreSQL 18's defaults are fine on the floor host; add them when VZ-OPS-007 measures a budget, not before.
- **A `search-migrate` one-shot.** Correctly deviated — `vizra-search` owns no migrations at M0 and the service is on the never-published list, so the slice that adds migrations cannot add it open.

---

## Chair ruling on the re-review (2026-09-21, tick 87)

The seat reports **no blocking finding open at `3261ad3`**: F1, F5, F6, F8b, F9, F10 CLOSED; F2, F3, F4 PARTIAL. Merge condition 4 (no blocking specialist finding) is therefore met on this SHA. **The PR is nevertheless held under the standing "no false guarantee merges" ruling**, because three operator-facing statements are untrue as written: `backup.sh` is described in the PRESENT tense in two files though no such script exists (F2); `env/production.env.example:242` says the caps are sized for `VIZRA_WORKER_CONCURRENCY=1` while line 222 ships 2 (F4a — the very defect F4 was raised for); and nothing an operator reads says that `docker compose ps` reports api and worker `healthy` whatever their state (F3). These go to the builder as round 2 of 2, consolidated with the verifier's verdict on `3261ad3`: the template-claims checker learns script names (`unmarked-future-script`, red-demonstrated), the three `backup.sh` lines become future tense with the slice id, the "IGNORE THE healthy COLUMN" paragraph lands in the production template and README (deleted in the PR that empties the known-false list), line 242 is corrected, `VIZRA_CADDY_MEM_LIMIT` 96m → 160m, `shm_size: ${VIZRA_POSTGRES_SHM_SIZE:-256m}` on postgres with the error string in the template comment, and the capacity note gains the postgres-cap-means-crash-recovery, swapless-host and /dev/shm-counts-against-the-cap sentences. The seat's re-review follows verbatim.

---

# Re-review at 3261ad3 — `vizra-infrastructure` seat

- **PR:** yegamble/vizra#4, branch `feat/m0-compose-topology`
- **Re-reviewed SHA:** `3261ad3edd63684855ff9d2346895a70522b5a8b` (was `69e197e`; fix round = `a96f188`, `df55226`, `bb8163f` + two evidence commits)
- **Method:** fresh `git archive 3261ad3 | tar -x` into a private `mktemp -d` under the scratchpad (never the builder's worktree). Read-only. Rendered 13 shapes with `compose-render.py --all` and by hand with `docker compose … config --format json` (Compose v5.5.1). Ran `check-compose-topology.py`, `check-config-coverage.py`, `check-template-claims.py`. **Independently red-demonstrated all four new rules** in a throwaway mutant copy. Started no container. Deleted every directory and file I created; the shared scratchpad root is otherwise untouched.
- **Cross-repo fact confirmed:** `vizra-core` `origin/main` = `4a80a1e`, `keys.go:62` declares `SEARCH_HMAC_KEY`, `keys.go:92-99` lists `VIZRA_SEARCH_HMAC_KEY` in `RetiredKeys`, `config.go:347-357` refuses it in production on presence.

## Verdict table

| Finding | State | One-line reason |
|---|---|---|
| **F1** retired key delivered by compose | **CLOSED** | Rendered model delivers `SEARCH_HMAC_KEY` only to api/worker/migrate/search; retired name absent everywhere; `core.json.source_commit = 4a80a1e` matches core `main`; alias floor 2→1; I re-injected the old spelling and `retired-key-delivered` went red 34× with the right message. |
| **F2** template promises rotation that does not exist | **PARTIAL** | The MFA/session text is now excellent and the `check-template-claims.py` mechanism works (I restored the old sentence; it failed by name). But the checker only scans backticked `vizra …` subcommands, and `` `backup.sh` refuses … and says so `` survives in **present tense** in two operator-facing files for a script that does not exist. |
| **F3** healthcheck that cannot fail | **PARTIAL** | Machine side fully closed — `frontend → api` is `service_started`/`required: false`, nothing consumes the fake healthy state, `probe-gates-readiness` went red when I re-added the edge, and both probes are named on every green run. Human side open: `docker compose ps` will say `(healthy)` next to a dead api and **no operator-facing file says so** (README has zero diagnostic content). |
| **F4** concurrency default + no memory limits | **PARTIAL** | Numbers are defensible and I would ship them; containment now works in both OOM mechanisms. Two defects: the template's caps block says "sized for … `VIZRA_WORKER_CONCURRENCY=1`" (line 242) while the shipped default is 2 (line 222) — the same comment-contradicts-value trap F4 was; and `caddy` at 96m is the one number I would change. |
| **F5** media volume has no writer | **CLOSED** | Stated in `docker-compose.yml:210-223` *and* in the file operators read (`env/production.env.example:36-41`), including the "you will archive an empty volume" consequence and the queued core `mkdir`/`chown`. |
| **F6** stop grace on postgres/clickhouse | **CLOSED** | Both render `1m0s`; reasoning names crash recovery. |
| **F8b** frontend-only host unrenderable | **CLOSED** | `prod-frontend-only` shape exists and renders `frontend` alone with no volumes. |
| **F9** dangling `env/external-postgres.env.example` pointer | **CLOSED** | Pointer replaced; the four-item "EXTERNAL PostgreSQL: WHAT YOU MUST SET" block is in the template at lines 130-140; `check-doc-links.py:51,194` now scans compose comments for `env/`+`deploy/` paths. |
| **F10** amd64-only | **CLOSED** | In the release-record block of the production template, with the exact failure text an arm64 operator will see. |
| **NEW-1** PostgreSQL `/dev/shm` is 64 MiB | **OPEN (new, SHOULD)** | Pre-existing at `69e197e` — my miss, not a regression from this round. |
| **NEW-2** `backup.sh` claimed in present tense, outside the checker's scope | **OPEN (new, SHOULD)** | Same class as F2; folded into the F2 PARTIAL finding below. |

## Nothing was broken by the fix round

I checked each thing the coordinator named, from rendered models:

- **Cold-start ordering is byte-identical for the critical path.** `migrate → postgres:service_healthy`; `api → {postgres healthy, redis healthy, migrate completed_successfully(required:true)}`; `worker → {postgres healthy, redis healthy, migrate completed(required:false)}`. The mem limits touched nothing in `depends_on`. The 40-second-PostgreSQL case still has ~130 s of headroom.
- **The `frontend → api` downgrade is not a real behaviour change.** Under the old `service_healthy` edge the gate cleared within seconds anyway, because the probe was the fake one. Frontend and caddy now both start in parallel with api and serve errors for the same ~30 s they already did.
- **`prod-worker-split` still renders alone**: `worker` only, `media_data` only, no ports, mem_limit 1500m intact.
- **External overlays still delete the container and cut the edges**: `prod-external-both` renders `api, caddy, frontend, migrate, worker` with `postgres_data` correctly dropped from the volume set; `prod-external-ipfs` and `prod-external-clickhouse` render no `ipfs`/`clickhouse` service and no 4001. Fail-early still fires: rendering the external-PostgreSQL chain with a blank `DATABASE_URL` aborts with the actionable message rather than falling back.
- **Ports are exactly as claimed** with every optional profile on: `caddy 0.0.0.0:80,443`, `ipfs 0.0.0.0:4001/tcp+udp`, `api 127.0.0.1:8080`, `frontend 127.0.0.1:3000`, everything else empty.
- Both checkers green on the unmutated tree: topology `13 shapes, 23 rules, 0 violations, 2 known-false probes named`; coverage `34 component keys, 57 template keys, 1 alias, 1 retired key refused, 0 violations`; template-claims `9 command references, 0 violations`.

The `stale-known-false-probe` rule (`check-compose-topology.py:127`) is a genuinely good addition nobody asked for: it stops the exemption list rotting into permanent cover. So is `profile-not-enumerated`. The `MARKER_WINDOW = 2` reasoning in `check-template-claims.py` — that a correct sentence five lines away *launders* a false one rather than qualifying it — is the sharpest thing in the round.

---

```
FINDING F2 (PARTIAL): the false-guarantee checker cannot see the shell scripts, and one present-tense claim survives
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     env/production.env.example:154; docker-compose.external-postgres.yml:50;
             env/production.env.example:140; scripts/check-template-claims.py:64
             (BACKTICKED = re.compile(r"`(vizra|vizra-search)\s+([a-z][a-z0-9-]*)"))
  requirements: VZ-INSTALL-002, VZ-BACKUP-003

Observed:
  The blocking half is CLOSED and closed well. The MFA block now reads
  "*** DO NOT CHANGE THIS VALUE BY HAND AFTER FIRST BOOT ***", names the
  consequence (permanently undecryptable TOTP secrets, every enrolled member
  locked out, admin must disable MFA account by account), states that nothing
  re-seals them today, names the three subcommands that do exist, and commits to
  changing the block in the PR that implements rotation. VIZRA_SESSION_SECRET
  gets the parallel treatment with "Recoverable: people log in again." The
  compose `:?` messages carry the same text. I restored the original sentence in
  a mutant copy and check-template-claims.py failed with
  `rule=unmarked-future-command at=env/production.env.example:102`, exit 1.

  What the checker does NOT scan is any script name. Its regex matches only
  backticked `vizra <sub>` / `vizra-search <sub>`. Three survivors:
    env/production.env.example:154
      "`backup.sh` refuses to back the cache up, and says so."   ← PRESENT TENSE
    docker-compose.external-postgres.yml:50
      "`backup.sh` refuses to back up a database it does not manage"  ← PRESENT TENSE
    env/production.env.example:140
      "`backup.sh` will REFUSE to dump a database it does not manage"  ← future, unmarked
  No backup.sh, restore.sh, install.sh or deploy.sh exists in this tree.

Failure:
  Less destructive than the MFA line — it cannot lose data by itself — but the
  same class, and it lands on the operator at the worst moment. Someone standing
  up an instance with managed PostgreSQL reads item 4 of the external-PostgreSQL
  checklist, sees that `backup.sh` "refuses to dump a database it does not manage
  and will say so", and reasonably concludes that a backup tool exists and is
  handling the boundary. They defer setting up provider snapshots until they have
  "checked what backup.sh does". There is nothing to check. The gap is only
  visible the first time they need a restore.

Perspective: operator

Recommendation:
  Two lines and one regex. Extend BACKTICKED (or add a second pattern) to
  `(?:^|\s|`)((?:backup|restore|install|bootstrap|deploy)\.sh)` and declare the
  scripts in env/registry as future artefacts pointing at VZ-ISSUE-004, exactly
  as `vizra setup` is declared. Then fix the three lines to future tense with the
  slice id inside MARKER_WINDOW — e.g. "backup.sh (VZ-ISSUE-004) will refuse …".
  The checker's own docstring already argues this is the right rule; it just
  stops at one noun class.

Acceptance criteria:
  - check-template-claims.py fails on a present-tense reference to a *.sh that
    does not exist in the tree, demonstrated red.
  - No operator-facing line describes backup.sh behaviour in the present tense.
  - The external-PostgreSQL checklist's item 4 stands on its own ("your snapshot
    schedule is yours") without depending on a script to enforce it.

Tests:
  scripts/check-template-claims.py, new rule `unmarked-future-script`, red-demoed
  by reverting env/production.env.example:154. Harness exists and is already wired
  into the validate lane.

Cross-repo implications:
  core: none — `vizra backup`/`vizra restore` are already declared future.
  user: none. search: none. meta: one regex, one registry entry, three lines.

Challenge:
  "`backup.sh` is a meta-repo script, not a component command, so it is out of a
  checker whose registries describe components." True of the implementation, not
  of the operator: they cannot tell a Go subcommand from a shell script, and the
  failure the checker exists to prevent is about belief, not provenance.
```

```
FINDING F3 (PARTIAL): the machine no longer trusts the fake probe; the operator still will
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docker-compose.yml:309-330 (the `service_started` block),
             :220-232 (api probe), :263-269 (worker probe);
             scripts/compose-shapes.json known_false_probes[];
             scripts/check-compose-topology.py:127,155,626;
             docs/quality/COMMANDS.md:347; docs/META_REPO.md §2a "constraint 2";
             README.md (87 lines, no diagnostic content — checked);
             env/production.env.example (no mention of probes — checked)
  requirements: VZ-OPS-002, VZ-OPS-003, VZ-TOPOLOGY-001

Observed:
  The chair's ruling is implemented completely and I verified each part:
   - frontend renders `{"api": {"condition": "service_started", "required": false}}`;
     caddy unchanged at service_started/required:false; nothing else gates on health.
   - Both probes are declared known-false in compose-shapes.json with `why_false`,
     `real_probe_exists` and `emptied_by`.
   - Every green run PRINTS them: "KNOWN-FALSE PROBES: 2 service(s) carry a
     healthcheck that CANNOT GO RED while the service is broken."
   - I re-added `condition: service_healthy` to frontend→api in a mutant copy;
     `check-compose-topology.py` exited 1 with 11 × `rule=probe-gates-readiness`
     and a message that names the shape, the service and why the probe is false.
   - `stale-known-false-probe` prevents the list outliving the probes.
   - No `--wait` and no `ps --status healthy` exists anywhere in this repo yet, so
     nothing machine-side consumes the state.

  What no file tells the operator: `docker compose ps` reports `Up (healthy)` for
  api and worker whatever their actual state. The three places that say so are
  META_REPO §2a, COMMANDS.md §5, and compose comments — all developer surfaces.
  README has no operational content at all; env/production.env.example never
  mentions a probe.

Failure:
  3am, uploads stopped, site erroring. The operator's first command is
  `docker compose ps`. api: healthy. worker: healthy. frontend: healthy. They
  conclude the containers are fine and start looking at DNS, Caddy, their
  firewall — everything except the wedged api, which is the thing that is broken.
  `docker compose up -d --wait`, which Compose's own help suggests, returns
  success against the same wedged api. The tooling is now safe; the human is not,
  and the human is the one on call.

Perspective: operator

Recommendation:
  One paragraph, in the two files an operator actually opens, and no new
  mechanism. In env/production.env.example (near the loopback-port block, which
  is what makes it actionable) and in README:

    # DIAGNOSING THIS RELEASE: IGNORE THE `healthy` COLUMN.
    # `docker compose ps` reports api and worker healthy whenever the binary can
    # execute - their probe is `vizra version`, which never touches PostgreSQL.
    # Ask the API itself instead; the loopback publish exists for this:
    #     curl -fsS http://127.0.0.1:8080/healthz   # liveness
    #     curl -fsS http://127.0.0.1:8080/readyz    # 503 = PostgreSQL unreachable;
    #                                               # 200 "degraded" names the component
    # Real probes land with `vizra healthcheck` (vizra-core, queued).

  This is worth doing in THIS PR because the readyz path already works today —
  docker-compose.prod.yml:115 publishes api on 127.0.0.1 precisely so an operator
  can curl it — so the workaround is complete, not aspirational.

Acceptance criteria:
  - An operator-facing file states that the `healthy` column is not trustworthy
    for api and worker, and gives the command that is.
  - The paragraph is deleted in the same PR that empties known_false_probes.
  - check-compose-topology.py's known-false output cross-references that file, so
    the two cannot drift.

Tests:
  Doc-level now. The durable proof is VZ-ISSUE-004's boot lane: with PostgreSQL
  stopped, `/readyz` returns 503 and the documented command shows it while
  `docker compose ps` still says healthy. That harness does not exist.

Cross-repo implications:
  core: `vizra healthcheck` (queue 2h) is what deletes both the list and the
  paragraph. user: frontend's probe is liveness-only too and is not declared
  known-false — defensible, since nothing gates on it, but it lies in the same
  `ps` output and the paragraph should name it. search: already has a real probe.

Challenge:
  "VZ-ISSUE-004 owns the operator runbook; this PR should not grow one." It is
  not a runbook, it is the disclosure that belongs beside a known-false probe the
  moment that probe ships. The chair already ruled the admission must be standing
  rather than filed once — this is the half of that audience that is not CI.
```

```
FINDING F4 (PARTIAL): the caps are right; the template still contradicts itself, and 96m for the edge is the one number I would change
Severity:    SHOULD
Confidence:  medium

Affected:
  repo:      vizra (meta)
  files:     env/production.env.example:222 (VIZRA_WORKER_CONCURRENCY=2) vs :242
             ("Defaults are sized for 2 vCPU / 4 GB with VIZRA_WORKER_CONCURRENCY=1");
             docker-compose.prod.yml:129-133 ("Sized for the shipped
             VIZRA_WORKER_CONCURRENCY=2"); docs/quality/COMMANDS.md:375-412;
             docker-compose.prod.yml:184 (caddy 96m)
  requirements: VZ-OPS-007, VZ-OPS-008

Observed — my judgement on the arithmetic, which the coordinator asked for:
  Default shape caps: postgres 768 + redis 384 + api 768 + worker 1500 +
  frontend 512 + caddy 96 = 4028 MiB, confirmed from the rendered prod-default
  model. Add migrate 256 transiently during a deploy = 4284.

  The oversubscription argument is CORRECT and I would ship these numbers.
  Realistic concurrent peak on this shape is nowhere near the cap sum: postgres
  ~250 (shared_buffers 128 + a handful of backends), valkey ~320 at its 256m
  maxmemory plus fragmentation, api 100-200 (CGO off, no pixel decode), frontend
  150-250, caddy 30-60, worker 800-1200 at concurrency 2 with an AVIF encode in
  the derivative set — roughly 2300 MiB against ~3500 MiB usable after Ubuntu
  24.04 + dockerd. Headroom is real.

  Which container dies first, in both mechanisms:
   - cgroup-local OOM (a container hits its own memory.max): the worker, at 1500m,
     is the only one that realistically gets there. Killed inside its own cgroup,
     job lease swept and retried (ADR-004). That is the intended victim.
   - global OOM (host exhausted before any cgroup hits its cap): the kernel picks
     largest RSS, which in every scenario I can construct is still the worker.
  So the goal — "a limit that OOM-kills the worker is recoverable; one that
  OOM-kills PostgreSQL is not" — is actually achieved, not just asserted.

  PostgreSQL's 768m IS compatible with the defaults: shared_buffers 128 MiB is
  charged to the cgroup, leaving 640 for backends at work_mem 4 MB. Comfortable.

What is still wrong:
  (a) env/production.env.example:242 says the caps are sized for
      VIZRA_WORKER_CONCURRENCY=1; :222 ships 2; docker-compose.prod.yml:131 says
      the worker cap is sized for 2. This is precisely the defect F4 raised — a
      comment prescribing a value different from the one shipped — reintroduced
      40 lines below the line that was fixed. An operator sizing a bigger host
      from the wrong sentence under-provisions the worker.
  (b) caddy 96m. It is the only container whose death is total site downtime, and
      it is the tightest cap in the stack. Caddy idles at 25-40 MiB but with
      HTTP/2, TLS session state and a few hundred concurrent connections it
      reaches 80-150 MiB. Saving 64 MiB on a 4 GB host is not worth an OOM of the
      edge. I would ship `VIZRA_CADDY_MEM_LIMIT=160m`. Every other number stands.
  (c) Unstated: what happens if the postgres cap IS hit. The cgroup OOM killer
      kills a postgres process, the postmaster treats that as a crash, terminates
      every backend and runs crash recovery — the exact outcome the caps exist to
      avoid, now merely much less likely. An operator who later raises
      max_connections or work_mem without raising the cap walks into it.
  (d) Unstated: `mem_limit` without `memswap_limit` leaves swap unbounded, so on
      a host WITH swap the worker thrashes before it is killed and a 2 vCPU box
      becomes unresponsive. Most VPS images ship no swap, so the clean kill is
      the common case — which is exactly why it deserves one sentence rather
      than a mechanism.

Perspective: operator

Recommendation:
  - Delete "with VIZRA_WORKER_CONCURRENCY=1" from env/production.env.example:242,
    or change it to 2. One of the two sentences must go.
  - VIZRA_CADDY_MEM_LIMIT 96m → 160m.
  - Two sentences in the COMMANDS.md capacity note: hitting the postgres cap
    means crash recovery, so raise it with any tuning change; and these caps
    assume a swapless host.

Acceptance criteria:
  - No two lines in the tree state a different sizing assumption for the same
    default.
  - The capacity note names the consequence of each cap being reached, not only
    the reason it was chosen.

Tests:
  The `missing-mem-limit` rule already works — I deleted api's cap and it failed
  with 9 violations and a message that names badness score. Nothing here needs a
  new rule; the consistency of two comments is not mechanisable at sane cost.
  Calibration belongs to VZ-OPS-007's first boot-lane run, which the note already
  says is what these numbers await.

Cross-repo implications: none.

Challenge:
  "96m is fine; Caddy on a small instance never sees hundreds of connections."
  Probably true on day one, and the cost of being wrong is asymmetric: the worker
  dying loses a derivative job, the edge dying loses the site. 64 MiB is cheap
  insurance on the one container with no redundancy.
```

```
FINDING NEW-1: PostgreSQL gets Docker's 64 MiB /dev/shm, so parallel queries fail at runtime
Severity:    SHOULD
Confidence:  medium
Slice:       this PR (one line) or VZ-OPS-007

Affected:
  repo:      vizra (meta)
  files:     docker-compose.yml:118-143 (postgres service — no shm_size);
             docker-compose.prod.yml:66-79 (mem_limit + stop_grace_period, still
             no shm_size); confirmed absent: `grep -rn shm_size docker-compose*.yml
             env/ docs/quality/COMMANDS.md` → no match;
             rendered prod-default model: postgres shm_size = None
  requirements: VZ-OPS-002, VZ-OPS-007

Observed:
  Docker gives every container a 64 MiB /dev/shm unless `shm_size` says otherwise.
  PostgreSQL's `dynamic_shared_memory_type` defaults to `posix`, which allocates
  dynamic shared memory segments in /dev/shm. `shared_buffers` is NOT affected —
  it has used anonymous mmap since 9.3, which is why the cluster starts fine and
  why this is easy to miss — but parallel sequential scans and parallel hash
  joins are, and PostgreSQL 18 chooses parallel plans once a table exceeds
  min_parallel_table_scan_size (8 MB) with max_parallel_workers_per_gather=2 by
  default.

  This is PRE-EXISTING: it was equally true at 69e197e and I did not catch it in
  round 1. It is not a regression introduced by this round, and I am raising it
  here because "recover after a PostgreSQL problem" is my checklist item and this
  is the most common Docker-specific PostgreSQL failure there is.

Failure:
  Months after install, once the assets or jobs table is large enough for the
  planner to go parallel, a query fails with
      ERROR: could not resize shared memory segment "/PostgreSQL.NNNNNNN" to
      NNNNNN bytes: No space left on device
  The operator sees an intermittent 500 on one page, "No space left on device" in
  the logs, and goes looking at disk — which is fine, with gigabytes free. It is
  plan-dependent, so it comes and goes with the statistics, which is the worst
  possible diagnostic signature. Nothing in Vizra's logs, doctor output or
  runbook points at /dev/shm.

Perspective: operator

Recommendation:
  One line on the postgres service:
      shm_size: ${VIZRA_POSTGRES_SHM_SIZE:-256m}
  with the key in env/production.env.example beside the memory caps and a comment
  naming the error string, so a search for it lands on the answer. Note the
  interaction with F4: /dev/shm usage is charged to the container's memory cgroup
  under cgroup v2, so this shares the 768m postgres cap — which is fine, since
  DSM is transient and bounded by the parallel-worker settings, but it should be
  said in the capacity note rather than discovered.
  Do it in this PR if the round is reopened anyway; otherwise VZ-OPS-007.

Acceptance criteria:
  - The rendered postgres service declares a shm_size above 64 MiB.
  - The capacity note states that /dev/shm counts against the postgres cap.
  - Negative case (boot lane, VZ-ISSUE-004): a forced parallel hash join over the
    fixture corpus completes rather than erroring.

Tests:
  A `postgres-shm-floor` rule in scripts/check-compose-topology.py would be
  cheap and mirrors `missing-mem-limit`, but a single line with a comment is
  probably enough — this is a value, not a policy. The runtime proof needs the
  boot lane, which does not exist.

Cross-repo implications:
  core: none. meta: one line + one template key.

Challenge:
  "At M0 there is no data, so no parallel plan will ever be chosen." Correct —
  which is exactly why it will not be found by any test we can write this quarter,
  and why the one-line fix is worth taking now rather than in an incident.
```

**BLOCKING FINDINGS OPEN AT 3261ad3: none.**
