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

---

## Chair note on the final re-review (2026-09-21, tick 98)

The seat reports **no blocking finding open at `9c4b5d3`**; F1–F4 and NEW-1 CLOSED. Its NEW-2 is rated NIT, but the chair checked the tree at `9c4b5d3` and the claim the seat disproved is written down in three places — `docs/META_REPO.md:175` ("it fails in both directions"), `docs/quality/COMMANDS.md:352`, and `scripts/check-compose-topology.py:871` ("fails in both directions by construction") — while the seat measured that emptying `known_false_probes` with both paragraphs present exits 0. A documented control that does not exist is exactly what the standing "no false guarantee merges" ruling holds, whatever its severity label. The fix is the seat's four-line `else:` branch (`known-false-stale-disclosure`, red-demonstrated) — making the sentences TRUE rather than softening them — plus NEW-3's three one-line operator-surface edits. It is consolidated with the verifier's verdict on `9c4b5d3`. The seat's healthcheck-values note is carried to the follow-up meta PR that adopts `vizra healthcheck` (core #7 is merged at `5eb2829`): api timeout 5s, start_period 60s (the host-reboot case, where `depends_on` is not re-evaluated), worker timeout 10s, `degraded` = healthy kept, the worker window derived from the poll interval, and the open question for core: what is the claim loop's poll interval and does it back off when idle? The seat's final re-review follows verbatim.

---

# Final re-review at 9c4b5d3 — `vizra-infrastructure` seat, 2026-09-21

- **PR:** yegamble/vizra#4, `feat/m0-compose-topology`
- **SHA:** `9c4b5d3285e1368634bc2042a83a91bfcb7e564b` (round 2 = `7e95989` + evidence `9c4b5d3`)
- **Method:** fresh `git archive 9c4b5d3 | tar -x` into a private `mktemp -d` under the shared scratchpad. Read-only, render-only, no container started. Rendered all 13 shapes; ran `check-compose-topology.py`, `check-config-coverage.py`, `check-template-claims.py`, `check-doc-links.py` — all exit 0. **Independently red-demonstrated four of the five new/claimed rules** in a throwaway copy; the fifth did not fire (see NEW-2). Read `env/production.env.example`, `README.md` and every compose `:?` message end to end. Deleted every file and directory I created; nothing else in the scratchpad was touched.
- **Checker output at this SHA:** topology `13 shapes, 26 rules, 0 violations, 2 known-false probes named`; coverage `34 component keys, 58 template keys, 1 alias, 1 retired key refused, 0 violations`; template-claims `10 files, 16 command references, 5 shipped + 11 future commands, 0 scripts present + 6 declared future, 0 violations`.

## Verdict table

| Finding | State | One-line reason |
|---|---|---|
| **F1** retired key delivered | **CLOSED** (was CLOSED at 3261ad3) | Unchanged and still correct: `SEARCH_HMAC_KEY` only, retired name absent, `core.json` at `4a80a1e`. |
| **F2** false capability promises | **CLOSED** | `env/registry/meta.json` declares six future scripts; I appended a present-tense `backup.sh` line and `unmarked-future-script` fired (exit 1) with the right message. All nine surviving references are future tense with the slice id inside the 2-line marker window. Item 4 of the external-PostgreSQL checklist now stands alone ("Backup ownership is yours and nothing in Vizra takes it back… do not defer it pending a Vizra backup tool"). The round also self-caught two claims I had missed — `bootstrap.sh` mis-attributed to VZ-ISSUE-003, and the arm64 line reading as though a preflight existed. |
| **F3** healthcheck that cannot fail | **CLOSED** | Disclosure is in both files; in the template it sits directly under `VIZRA_HTTP_PORT`/`VIZRA_FRONTEND_PORT`, which is the right place; it names frontend's liveness-only probe and `up -d --wait`; commands match the rendered loopback publishes. `known-false-undisclosed` fired when I deleted the README section. (Its third acceptance criterion — "so the two cannot drift" — is only half met; that is NEW-2, not a regression of F3.) |
| **F4** caps and concurrency | **CLOSED** | Template line 265 now says "at the SHIPPED `VIZRA_WORKER_CONCURRENCY=2`"; caddy 160m; the capacity note gained what happens when *each* cap is reached (worker = intended victim; postgres = postmaster crash recovery, raise with any tuning change; caddy = total downtime), the swapless-host paragraph, and /dev/shm charging. `missing-mem-limit` still red on deletion. **4092 MiB stands — I would not trim** (see below). |
| **NEW-1** PostgreSQL /dev/shm | **CLOSED** | `shm_size: ${VIZRA_POSTGRES_SHM_SIZE:-256m}`; renders 256 MiB on postgres **only**, and only in the six shapes that have postgres (absent in `prod-external-postgres`/`-both`/`-worker-split`/`-frontend-only`). Template quotes the exact error string with "if you are reading this because you searched for that message: this is the setting." I deleted the line and `postgres-shm-floor` fired 9×. |
| **NEW-2** `known-false-undisclosed` enforces one direction only | **OPEN (new, NIT)** | The builder's claim that it "fails in BOTH directions" is not what ships: I emptied `known_false_probes` with both paragraphs still present and topology passed, exit 0. |
| **NEW-3** three small operator-surface nits | **OPEN (new, NIT)** | README hardcodes `8080`/`3000` without naming the variables that change them; `curl -f` on `/readyz` exits 0 on `degraded`; the capacity note calls "4092 on 4096" deliberate when only the oversubscription is. |

## Did the round break anything — no

All from rendered models, not from the YAML:

- **Cold-start ordering byte-identical.** `migrate → postgres:healthy`; `api → {postgres healthy, redis healthy, migrate completed(required:true)}`; `worker → {…, migrate completed(required:false)}`; `frontend → api:started(required:false)`; caddy unchanged. postgres probe still `pg_isready -U vizra -d vizra`, `start_period 30s / interval 10s / retries 10` — the 40-second-PostgreSQL case keeps its ~130 s of headroom. `shm_size` and `mem_limit` touched no edge.
- **`prod-worker-split` renders alone**: one service, `media_data` only, no ports, 1500m cap, migrate edge optional.
- **External overlays still delete the container**: `prod-external-both` = 5 services, `postgres_data` dropped, `shm_size` gone with the service; `prod-external-ipfs` and `-clickhouse` render no such service and no 4001.
- **Ports exactly right** with every optional profile on: `caddy 0.0.0.0:80,443`, `ipfs 0.0.0.0:4001/tcp+udp`, `api 127.0.0.1:8080`, `frontend 127.0.0.1:3000`, nothing else. `prod-external-tls` publishes loopback only; `prod-worker-split` publishes nothing.
- **Production hygiene intact**: `VIZRA_MODE=production`, zero `VIZRA_DEV_*` keys in any production shape.

Two rules I did not ask for and that earn their place: `gated-probe-unrecognised` (I swapped `pg_isready` for `true` and got 27 violations naming why `-U` matters) and the topology checker's new SCOPE paragraph, which states in its own output that `probe-gates-readiness` "cannot tell a real probe from a fake one nobody declared". A checker that publishes its own blind spot is rarer than it should be.

## My call on 4092 MiB / 4096 MiB: ship it, do not trim

Caddy's 96m→160m does **not** tip anything, because the cap sum is not the load-bearing number. Realistic concurrent peak on the default shape is ~2300–2400 MiB (postgres ~250, valkey ~320 at its 256m maxmemory plus fragmentation, api 100–200, frontend 150–250, caddy 30–60, worker 800–1200 at concurrency 2 with an AVIF encode), against ~3500 MiB usable after Ubuntu 24.04 and dockerd. Both OOM mechanisms still select the worker: it is the only service that realistically reaches its own `memory.max`, and in any global-pressure scenario I can construct it is also the largest RSS. If someone insists on a sum under physical RAM, the trim I would take is `frontend` 512m→448m (Next.js standalone idles 120–200 MiB; 448 is still >2× headroom) for 4028 — but I would not spend the churn.

---

```
FINDING NEW-2: the known-false disclosure is gated in the dangerous direction only, not both
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-compose-topology.py:~872-892 (the rule body, guarded
             by `if known_false:`) and :914 (`if known_false:` for the printout);
             README.md:107-111; env/production.env.example:185-188
  requirements: VZ-OPS-002, VZ-OPS-003

Observed:
  The fix round's claim is "a new rule `known-false-undisclosed` fails in BOTH
  directions so the known-false list and the paragraphs are deleted together."
  Direction one is real and I proved it: deleting the README section while
  `known_false_probes` is non-empty gives

    VIOLATION shape=(manifest) rule=known-false-undisclosed service=README.md
    detail=must carry the disclosure 'IGNORE THE `healthy` COLUMN' while
    known_false_probes is non-empty (['api', 'worker']), and does not.

  Direction two is not. I emptied `known_false_probes` to `[]` in
  scripts/compose-shapes.json, leaving both paragraphs in place, re-rendered all
  13 shapes and ran the checker: **exit 0, zero violations**. The rule body sits
  inside `if known_false:`, so an empty list makes it unreachable. What carries
  that direction today is prose in the two files themselves — "if that list is
  empty and this is still here, one of the two is wrong" — which is an
  instruction to a human, not a gate.

Failure:
  Mild and the opposite of dangerous, which is why this is a NIT and not more.
  When vizra-core PR #7 lands `vizra healthcheck` and the meta follow-up swaps
  the probes, whoever does it can delete the declarations and forget the
  paragraphs, and nothing complains. The operator is then told to ignore a
  `healthy` column that has become trustworthy, and to hand-curl `/readyz`
  instead of using the tooling — so they distrust a good signal and keep a
  workaround alive past its usefulness. Stale reassurance, not a false one.
  It matters now precisely because the follow-up PR is the next thing to happen.

Perspective: operator, developer

Recommendation:
  Four lines: an `else:` branch on the existing guard that fails when either
  disclosure marker is still present while `known_false_probes` is empty —

    rule: known-false-stale-disclosure
    detail: carries the disclosure 'IGNORE THE `healthy` COLUMN' while
            known_false_probes is empty. Every probe is real now; telling the
            operator to ignore the healthy column keeps a workaround alive past
            its usefulness. Delete the section.

  Correct the "both directions" sentence wherever it was written down
  (docs/META_REPO.md §2a and the round-2 evidence), so the record matches the
  code. I would take this in THIS PR if it is reopened for any other reason,
  and otherwise as the first commit of the `vizra healthcheck` follow-up, where
  it is the rule that makes that PR's own cleanup checkable.

Acceptance criteria:
  - Emptying `known_false_probes` while either paragraph survives fails the
    topology check, demonstrated red.
  - Deleting the paragraphs while the list is non-empty still fails (unchanged).
  - The `vizra healthcheck` follow-up cannot go green until both sides move.

Tests:
  scripts/check-compose-topology.py, new rule id, red-demoed exactly as I did it:
  set `known_false_probes: []`, re-render, expect exit 1. Harness exists.

Cross-repo implications:
  core: none. meta: four lines and one corrected sentence.

Challenge:
  "The prose in both files already says it, and the follow-up PR is one person
  who has just read the rule." True, and it is why this is a NIT — but the
  entire argument of this slice is that a standing admission beats a note
  somebody is supposed to re-read, and the same argument applies to its removal.
```

```
FINDING NEW-3: three small things on the operator surfaces
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     README.md:101-104; env/production.env.example:180-183;
             docker-compose.prod.yml:115,~150 (`127.0.0.1:${VIZRA_HTTP_PORT:-8080}:8080`,
             `127.0.0.1:${VIZRA_FRONTEND_PORT:-3000}:3000`);
             docs/quality/COMMANDS.md §5a ("sum to 4092 MiB on a 4096 MiB host,
             and that is deliberate")
  requirements: VZ-OPS-002, VZ-OPS-007

Observed and what each costs:

  (a) PORTS HARDCODED IN README. The diagnostic commands name 127.0.0.1:8080 and
      :3000. Those are the DEFAULTS of VIZRA_HTTP_PORT and VIZRA_FRONTEND_PORT,
      confirmed against the rendered model — correct for anyone who left them
      alone. In env/production.env.example this is fine, because the paragraph
      sits two lines under the variables. In README there is no such context, and
      the template explicitly invites changing them ("Change them only if
      something else on the host already owns the port"). An operator who did
      gets connection-refused from the one command they were told to trust.
      Fix: "…:8080 (VIZRA_HTTP_PORT) … :3000 (VIZRA_FRONTEND_PORT)".

  (b) `curl -fsS …/readyz`. `-f` makes curl exit 0 on any 2xx — and /readyz
      returns 200 `degraded` for cache down, search misconfigured or queue age
      over threshold. So `curl -fsS /readyz && echo OK` prints OK on a degraded
      instance. The inline comment explains the semantics, so a reader is warned;
      a copy-paste into a monitoring script is not. `-f` also swallows the 503
      body, though there the status code carries the whole meaning.
      Fix: drop `-f` on the readyz line and show the code —
        curl -sS -o /dev/tmp -w '%{http_code}\n' http://127.0.0.1:8080/readyz
      or simply `curl -sS …/readyz` so the JSON (which names the component) prints.

  (c) "The default-shape caps sum to 4092 MiB on a 4096 MiB host, and that is
      deliberate." The OVERSUBSCRIPTION is deliberate; the sum landing 4 MiB
      under physical RAM is coincidence, and the sentence reads as though the
      numbers were engineered to fit — which is the opposite of the argument the
      same paragraph then makes ("caps on peak, not reservations; nothing is set
      aside"). Someone sizing an 8 GB host from that sentence will scale the
      wrong quantity.
      Fix: "…sum to 4092 MiB on a 4096 MiB host. The oversubscription is
      deliberate; landing just under physical RAM is coincidence, and not the
      number that matters — realistic concurrent peak is roughly 2.3 GB."

Perspective: operator

Recommendation:
  All three are single-line edits on files this PR already touches. Take them
  together in whatever commit next touches these surfaces; none justifies
  reopening the PR on its own.

Acceptance criteria:
  - The README diagnostic names the two variables beside the ports.
  - No documented command exits 0 on `degraded` without the reader being told
    in the same line.
  - No sentence attributes design intent to the 4092/4096 coincidence.

Tests:
  Doc-level; no harness change. (a) and (c) are not mechanisable at sane cost.
  (b) becomes testable in VZ-ISSUE-004's boot lane: with the cache stopped,
  /readyz returns 200 `degraded` and the documented command must not read as OK.

Cross-repo implications: none.

Challenge:
  "These are three nits and the seat was told to cap itself at three." That is
  exactly the cap, and they are bundled as one finding for that reason.
```

## Healthcheck values note — for the `vizra healthcheck` follow-up PR

Core PR #7's proposal, judged before it lands. **UNVERIFIED:** I have not read vizra-core PR #7; this is from the summary relayed to me, and the worker's claim-loop poll interval is the one fact I could not check and that changes one of my numbers.

**`degraded` = exit 0 is right — keep it, and it is the most important decision in the set.** `/readyz` 503s only on PostgreSQL; everything else is 200 `degraded`. If the probe treated degraded as unhealthy, an instance with a job backlog over `VIZRA_QUEUE_AGE_THRESHOLD` (15m) would report api unhealthy, a `service_healthy` gate on frontend would never clear on a cold start, and `up -d --wait` would fail the deploy *because the instance is busy*. A backlogged instance that cannot be deployed is how you get stuck at 3am. Gate semantics should be "is this thing fit to receive traffic", and a degraded Vizra is.

**My values, against theirs:**

| | proposed | mine | why |
|---|---|---|---|
| api `test` | `vizra healthcheck api` | same | correct |
| api `interval` | 15s | 15s | fine |
| api `timeout` | 3s | **5s** | the probe pings PostgreSQL; under the 768m cap on a 2-vCPU box mid-checkpoint, connect + `SELECT 1` can exceed 3s. Three timeouts flip a working api to red. Must stay < interval, so 5s is safe |
| api `start_period` | 30s | **60s** | see below |
| api `retries` | 3 | 3 | fine |
| worker `timeout` | 3s | **10s** | same ping plus loop introspection, on the process that is simultaneously running libvips at its cap |
| worker window | 15s fixed | **derived: max(3 × poll interval, 30s)** | see below |

**`start_period` 30s vs a 40-second PostgreSQL — the answer is "not the case you think, but raise it anyway."** On `up`, api's container does not start until postgres is healthy *and* migrate exited 0, so the start_period clock never races a slow PostgreSQL. The case that does bite is **a host reboot**: Docker restarts containers from `restart: unless-stopped` without re-evaluating `depends_on`, which is an `up`-time ordering only. api can therefore start while PostgreSQL is doing crash recovery, which on a large database runs into minutes. 60s costs nothing when things are fine — the container goes healthy on the first successful probe, whenever that is — and avoids a red that means nothing.

**There is no restart-loop risk from any of these values, and the follow-up PR should say so** rather than tuning against an imagined one: Docker takes no action on `unhealthy`. It does not restart, it does not stop, it only reports. The blast radius of a too-aggressive probe is a false red in `ps`, a blocked `service_healthy` gate and a failed `--wait` — bad, but not a loop. Conversely, nothing self-heals from a correct red either; that needs `vizra deploy`/`doctor` or an external supervisor.

**The worker semantics need one word pinned down before it ships.** "Claim-loop progress within 15 s" must mean *the loop completed an iteration, including a no-op poll* — never *a job moved*. If it means the latter, a healthy idle worker on a quiet instance reports unhealthy at 3am, which is the false-red failure inverted. Ask core to name the field `last_claim_attempt_at`, not "progress". And the window must be **derived from the worker's own poll setting**, not hardcoded at 15: a window equal to `interval` tolerates a single missed poll, and if the loop backs off when idle (as idle loops usually do) any jitter goes red. `max(3 × poll, 30s)`, read from config, so tuning the poll cannot silently break the probe. **This is the question I would put to PR #7's verifier: what is the poll interval, and does it back off when the queue is empty?**

**Do not add a healthcheck to `migrate`.** It is right as it is — "a process that is supposed to exit cannot be healthy".

**What the follow-up meta PR owes beyond swapping four lines:**
1. Delete both `known_false_probes` entries **and** the two disclosure paragraphs in the same commit — with NEW-2's reverse rule landed first, so that is enforced rather than remembered.
2. Restore `frontend → api` to `condition: service_healthy`, **keeping `required: false`** so `prod-frontend-only` still renders. Getting a real probe is the entire point; `probe-gates-readiness` permits it once the declaration is gone.
3. Add the two new probe commands to `gated-probe-unrecognised`'s expected-command table, so a future swap back to `version` is red.
4. **Replace** the disclosure rather than deleting it outright: one sentence saying `healthy` now means "PostgreSQL reachable and the loop is turning", that `degraded` still shows as healthy by design, and pointing at `/readyz`'s body and `vizra doctor` for component detail.

**BLOCKING FINDINGS OPEN AT 9c4b5d3: none.**
