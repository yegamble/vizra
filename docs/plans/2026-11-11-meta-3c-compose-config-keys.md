# Execution plan: VZ-FOUND-006: compose delivers every key vizra-core reads (queue 3c)

## Context
Repo `yegamble/vizra` (meta), branch `fix/compose-config-key-coverage` from origin/main `60a447f`.
Component source read, never edited: vizra-core at `5f615d74e840b23d2201b1d78dd89abfef07701b`
(`git rev-parse HEAD` in the checkout; an ancestor of its `origin/main`).
The audit (docs/plans/2026-11-10-meta-found-002-003-006-audit.md) reproduced that core reads
`VIZRA_OWNER_CLAIM_ANNOUNCE`, `VIZRA_OWNER_CLAIM_TTL` and `VIZRA_STORAGE_ROOT`, and that the meta tree
delivered none of them: `env/registry/core.json` was a snapshot at core `4a80a1e`.

## Acceptance
Ledger entry VZ-FOUND-006, unchanged. This slice works on S1 and the compose half of N2.

| Case | State after this PR |
|---|---|
| S1 every key read by config.Load reaches api and worker | closed here for the reproduced hole: 25 of 25 core keys in every shape that renders the service |
| S2 every key `vizra setup` writes exists in the template | stays open: `vizra setup` does not exist (queue 7) |
| N1 production boot with dev JWT/session secret fails | held before, in vizra-core; not touched |
| N2 a key added to config without template/compose consumer fails CI | compose and template halves closed against the snapshot; the snapshot-staleness limit below stays open |
| P1 log denylist | held before, in vizra-core for the listed value classes; two integration tests not run by the audit; not touched |

Snapshot-staleness limit (open, not hidden): meta CI checks a SNAPSHOT of core's key registry. A key added
in vizra-core after `source_commit` is invisible to meta CI until someone refreshes
`env/registry/core.json`. `--drift` proves currency but needs the component checkouts and cannot run in
meta CI (no token for the private sibling repositories). What would close it: a CI lane that has the
component sources (the future `bundle` lane, or a read token for the component repos) running `--drift`,
or core publishing its key registry as a release artifact that meta CI fetches. Not built here.

Non-goals: `vizra setup`, a cross-repo fetch, refreshing the user and search snapshots.

## Implementation
- `env/registry/core.json`: re-snapshot at core `5f615d7`: +3 keys (none secret: keys.go carries no
  `Secret: true` on any of them, and `--drift` compares that flag), `commands` now lists
  `vizra healthcheck` and `vizra claim-token` (cmd/vizra/main.go), `vizra healthcheck` leaves `future_commands`.
- `docker-compose.yml` `x-core-env` (shared by api, worker and migrate, the existing convention; the
  `api-worker-asymmetry` rule requires identical maps):
  - `VIZRA_STORAGE_ROOT: /var/lib/vizra/media`: a literal, like `VIZRA_LISTEN_ADDR`; core only requires an absolute path.
  - `VIZRA_OWNER_CLAIM_ANNOUNCE: ${...:-off}`: core accepts `off` or `stderr`.
  - `VIZRA_OWNER_CLAIM_TTL: ${...:-1h}`: core requires a Go duration greater than zero.
  No overlay overrides `environment` wholesale, so the anchor reaches every shape.
- `env/production.env.example`, `env/development.env.example`: the two owner-claim keys with core's doc
  text; a comment naming where the storage root is fixed. Stale "no storage-root key at M0" comments corrected.
- `scripts/check-compose-topology.py`: new rule `storage-root-mount`: for api and worker in every shape,
  the rendered `VIZRA_STORAGE_ROOT` equals the target of exactly one `media_data` volume mount.
- `scripts/check-config-coverage.py`: new rule `registry-key-untemplated`. This was a checker hole:
  `variable-untemplated` is satisfied by the UNION of the two templates, so removing an operator key from
  the production template alone stayed green. A registry key that compose interpolates must now be in each template.

Assumption to review: `VIZRA_STORAGE_ROOT` is delivered as a compose literal and is NOT an operator key in
the templates (a template line would be `template-key-unused`, and an operator-set path would break the
mount). Its documented home is the registry entry, the compose comment and a template comment.

## Verification
Environment: darwin arm64, Docker Compose v5.6.1 client (daemon not running; `compose-render.py` needs
only the client, so all 13 shapes rendered locally), python3. Gates run through `.claude/council/quiet.sh`.

| Command | Exit |
|---|---|
| `python3 scripts/compose-render.py --all --out build/compose-models` | 0 (13 shapes) |
| `python3 scripts/check-compose-topology.py build/compose-models` | 0 (13 shapes, 28 rules, 0 violations) |
| `python3 scripts/check-config-coverage.py build/compose-models` | 0 (37 component keys, 60 template keys, 13 shapes, 0 violations) |
| `python3 scripts/check-config-coverage.py --drift` | 0, see the note below |
| `python3 scripts/check-doc-links.py` | 0 |
| `python3 scripts/check-quality-json.py` | 0 |
| `bash scripts/check-generated-ledger.sh` | 0 |
| `python3 scripts/check-template-claims.py` | 0 |
| `python3 scripts/check-lane-integrity.py`, `check-workflows.py`, `check-action-pins.py` | 0, 0, 0 |

Drift note. The exit-0 run used the live core checkout at `5f615d7` plus `git archive` extracts of
vizra-user and vizra-search AT THEIR SNAPSHOT COMMITS (`90896be`, `808a549`), linked into the worktree
for the run and removed after. Against the local user and search checkouts as they stand
(`33633d4`, `4810048`) `--drift` exits 1 with 36 violations, all `vizra-search/*`, none for core: the
search snapshot is behind the local search checkout. That is outside this slice and is reported, not fixed.

Not run locally: `docs/evidence/compose-topology/demo.sh`, the ledger-status steps that call GitHub,
shellcheck (no shell file touched). CI is the evidence for those.

Keys delivered (the three new keys, from the rendered models): api 3/3 in 11 shapes, worker 3/3 in 12
shapes, migrate 3/3 in 11 shapes; `prod-frontend-only` renders no core service, `prod-worker-split`
renders the worker only. Values in every shape: `/var/lib/vizra/media`, `off`, `1h`.

## Progress and evidence

### (a) Red before the fix: snapshot refreshed, tree otherwise at 60a447f
`python3 scripts/check-config-coverage.py` (models rendered from 60a447f): exit 1, 102 violations =
3 keys x 34 rendered core service instances. First and last lines:

```
VIOLATION rule=service-key-missing subject=bundle-no-checkouts/api/VIZRA_OWNER_CLAIM_ANNOUNCE detail=vizra-core reads VIZRA_OWNER_CLAIM_ANNOUNCE (env/registry/core.json at 5f615d74e840) but the rendered environment map does not deliver it, 
VIOLATION rule=service-key-missing subject=bundle-no-checkouts/api/VIZRA_OWNER_CLAIM_TTL detail=vizra-core reads VIZRA_OWNER_CLAIM_TTL (env/registry/core.json at 5f615d74e840) but the rendered environment map does not deliver it, so the ser
VIOLATION rule=service-key-missing subject=bundle-no-checkouts/api/VIZRA_STORAGE_ROOT detail=vizra-core reads VIZRA_STORAGE_ROOT (env/registry/core.json at 5f615d74e840) but the rendered environment map does not deliver it, so the service g
...
VIOLATION rule=service-key-missing subject=prod-worker-split/worker/VIZRA_STORAGE_ROOT detail=vizra-core reads VIZRA_STORAGE_ROOT (env/registry/core.json at 5f615d74e840) but the rendered environment map does not deliver it, so the service 

102 violation(s).
exit=1
```

Per key: 
- VIZRA_STORAGE_ROOT: 34 violations
- VIZRA_OWNER_CLAIM_ANNOUNCE: 34 violations
- VIZRA_OWNER_CLAIM_TTL: 34 violations

### (b) Controlled mutations after the fix, each red then restored
Each step re-renders all 13 shapes, then runs both checkers. Lines are cut at 260 characters.

```
== BASELINE (HEAD 07c3bc6)
render exit=0
check-compose-topology exit=0; check-config-coverage exit=0
violation lines: 0

== M1: remove VIZRA_OWNER_CLAIM_TTL from the worker's compose environment (docker-compose.yml: worker 'environment: *core-env' becomes the same map minus that key)
 1 file changed, 25 insertions(+), 1 deletion(-)
render exit=0
check-compose-topology exit=0; check-config-coverage exit=1
VIOLATION rule=service-key-missing subject=bundle-no-checkouts/worker/VIZRA_OWNER_CLAIM_TTL detail=vizra-core reads VIZRA_OWNER_CLAIM_TTL (env/registry/core.json at 5f615d74e840) but the rendered environment map does not deliver it, so the service gets its bui
VIOLATION rule=service-key-missing subject=dev-build-from-checkouts/worker/VIZRA_OWNER_CLAIM_TTL detail=vizra-core reads VIZRA_OWNER_CLAIM_TTL (env/registry/core.json at 5f615d74e840) but the rendered environment map does not deliver it, so the service gets it
VIOLATION rule=service-key-missing subject=dev-default/worker/VIZRA_OWNER_CLAIM_TTL detail=vizra-core reads VIZRA_OWNER_CLAIM_TTL (env/registry/core.json at 5f615d74e840) but the rendered environment map does not deliver it, so the service gets its built-in de
violation lines: 23
-- restored docker-compose.yml
render exit=0
check-compose-topology exit=0; check-config-coverage exit=0
violation lines: 0

== M2: remove VIZRA_OWNER_CLAIM_ANNOUNCE from env/production.env.example
 1 file changed, 1 deletion(-)
render exit=0
check-compose-topology exit=0; check-config-coverage exit=1
VIOLATION rule=registry-key-untemplated subject=env/production.env.example/VIZRA_OWNER_CLAIM_ANNOUNCE detail=a component reads it and compose interpolates it, so an operator can set it, but this template has no line for it - the other template naming it does n
violation lines: 1
-- restored env/production.env.example
render exit=0
check-compose-topology exit=0; check-config-coverage exit=0
violation lines: 0

== M3: VIZRA_STORAGE_ROOT set to a path that is not the media mount (/var/lib/vizra/elsewhere)
 1 file changed, 1 insertion(+), 1 deletion(-)
render exit=0
check-compose-topology exit=1; check-config-coverage exit=0
VIOLATION shape=dev-default rule=storage-root-mount service=api detail=VIZRA_STORAGE_ROOT='/var/lib/vizra/elsewhere' but the `media_data` volume is mounted at ['/var/lib/vizra/media']. They must be one and the same path, with exactly one such mount: otherwise 
VIOLATION shape=dev-default rule=storage-root-mount service=worker detail=VIZRA_STORAGE_ROOT='/var/lib/vizra/elsewhere' but the `media_data` volume is mounted at ['/var/lib/vizra/media']. They must be one and the same path, with exactly one such mount: otherwi
VIOLATION shape=dev-build-from-checkouts rule=storage-root-mount service=api detail=VIZRA_STORAGE_ROOT='/var/lib/vizra/elsewhere' but the `media_data` volume is mounted at ['/var/lib/vizra/media']. They must be one and the same path, with exactly one such moun
violation lines: 23
-- restored docker-compose.yml
render exit=0
check-compose-topology exit=0; check-config-coverage exit=0
violation lines: 0

== M3b: the mount moves instead (worker media_data target -> /srv/media)
 1 file changed, 1 insertion(+), 1 deletion(-)
render exit=0
check-compose-topology exit=1; check-config-coverage exit=0
VIOLATION shape=dev-default rule=storage-root-mount service=worker detail=VIZRA_STORAGE_ROOT='/var/lib/vizra/media' but the `media_data` volume is mounted at ['/srv/media']. They must be one and the same path, with exactly one such mount: otherwise vizra-core 
VIOLATION shape=dev-build-from-checkouts rule=storage-root-mount service=worker detail=VIZRA_STORAGE_ROOT='/var/lib/vizra/media' but the `media_data` volume is mounted at ['/srv/media']. They must be one and the same path, with exactly one such mount: otherwis
VIOLATION shape=prod-default rule=storage-root-mount service=worker detail=VIZRA_STORAGE_ROOT='/var/lib/vizra/media' but the `media_data` volume is mounted at ['/srv/media']. They must be one and the same path, with exactly one such mount: otherwise vizra-core
violation lines: 12
-- restored docker-compose.yml
render exit=0
check-compose-topology exit=0; check-config-coverage exit=0
violation lines: 0

git status --porcelain: ''
```

M2 is the mutation that was GREEN before `registry-key-untemplated` existed (the union rule); M3 and M3b
exercise `storage-root-mount` from both sides.

## Blockers and handoff
State: READY_FOR_REVIEW. Not verified, not merged.
Follow-ups (not in this PR): add M1 to M3 as cases in `docs/evidence/compose-topology/demo.sh` so CI
re-runs them; refresh `env/registry/search.json` (36 drift lines against local search `4810048`);
prose that still says `vizra` has three subcommands (docker-compose.yml, env/production.env.example) is
stale now that core ships `healthcheck` and `claim-token`; the snapshot-staleness limit above.
