# Execution plan: VZ-ISSUE-002 — meta compose topology + rendered-model assertions

Ledger IDs: VZ-TOPOLOGY-001, VZ-TOPOLOGY-002, VZ-TOPOLOGY-003, VZ-TOPOLOGY-006,
VZ-TOPOLOGY-007, VZ-CI-002, VZ-OPS-008.

## Context

- Repo: `yegamble/vizra` (meta). Worktree: `/Users/yosefgamble/github/vizra/.claude/worktrees/meta-compose`
  (gitignored), branch `feat/m0-compose-topology`, base `origin/main` = `6b8158c3280ecd17a32efbb009ab06d04da42260`.
- The main checkout at `/Users/yosefgamble/github/vizra` sits on the war-room
  chair's records branch and is **not** touched by this slice. This plan file is
  the one write outside the worktree.
- Issue: `docs/issues/VZ-ISSUE-002.md`. Design: `docs/META_REPO.md` §1–§2, §7.
  Rulings: Q-017 (Compose floor 2.24.4; base publishes no ports), Q-001
  (`SEARCH_MODE=off|managed|external`, off by default before M3), Q-004 (Valkey
  MANAGED / RESP ≥ 7.2 EXTERNAL), Q-027 (amd64-only runtime images).
  ADR-001 (pins), ADR-002 (config seam, deploy ordering, release record, compose).

## Acceptance (from VZ-ISSUE-002, verbatim)

- `validate` lane renders default, external-TLS, worker, all-optional, external
  PG, external Redis, both, bundle-without-checkouts.
- Port-closure, restart-policy, log-cap, one-shot no-build, config-key coverage
  assertions pass.
- Invalid external DSN fails render/boot with an actionable message.

Non-goals (stay in the ledger, not narrowed here): `install.sh`, `vizra setup`,
the bundle builder, the `boot` lane (VZ-ISSUE-004), backup/restore, publishing
images, any change to a component repo.

## Implementation

Deliverables in the worktree:

| Path | Purpose |
|---|---|
| `docker-compose.yml` | base; **publishes nothing**; all services, profiles, healthchecks, restart, log caps |
| `docker-compose.override.yml` | dev-only; auto-loaded by bare `docker compose`; loopback port maps |
| `docker-compose.dev.yml` | builds from the nested component checkouts |
| `docker-compose.prod.yml` | production overlay; release-record image vars; no build; loopback for api/frontend; caddy on `edge` |
| `docker-compose.external-postgres.yml` | EXTERNAL PostgreSQL: suppress container, require `DATABASE_URL` |
| `docker-compose.external-redis.yml` | EXTERNAL cache: suppress container, require `REDIS_URL`/`SEARCH_REDIS_URL` |
| `docker-compose.external-clickhouse.yml` | placeholder overlay, renders OFF |
| `docker-compose.external-ipfs.yml` | placeholder overlay, renders OFF |
| `env/*.env.example` | operator templates covering every declared component config key |
| `env/registry/*.json` | per-component key snapshots at a recorded component SHA |
| `scripts/compose-render.py` | render entry point: validate DSNs → `docker compose config --format json` |
| `scripts/check-compose-topology.py` | all rendered-model assertions |
| `scripts/check-config-coverage.py` | template ⟷ component-registry coverage, both directions |
| `scripts/compose-shapes.json` | the declared shape matrix + floor |
| `.github/workflows/validate.yml` | `compose` steps added to the existing required `validate` job |

Design decisions recorded:

1. Assertions parse `docker compose config --format json`. No YAML grepping.
   The only YAML parsing is the **diagnostic locator** that names which source
   file declared an offending key after the JSON assertion has already failed.
2. `SEARCH_HMAC_KEY` is the contract name on both sides. vizra-core still reads
   `VIZRA_SEARCH_HMAC_KEY`; compose feeds both from the single operator value
   `SEARCH_HMAC_KEY`. The coverage checker carries exactly one documented alias.
3. Config-key coverage runs against a checked-in registry snapshot so it works
   in the bundle shape (checkouts absent). Snapshot⟷live-registry drift is a
   separate local check; CI cannot run it (no cross-repo checkout token) and the
   lane does not claim to.
4. Compose floor: `!override` support is proven **from the rendered model** (the
   external overlays only suppress the bundled datastore if the tag was
   honoured); the version *number* floor is additionally checked with a
   fail-closed parser that accepts major > 2 (Q-017).

## Verification

Commands (all exist after this slice; none listed that does not):

```
./scripts/compose-render.py --list
./scripts/compose-render.py --all --out build/compose-models
./scripts/check-compose-topology.py build/compose-models
./scripts/check-config-coverage.py
./scripts/ci-required-guard.sh
```

Demonstrations required (red then green, digest printed before and after each
mutation): ports on postgres / cache / search in base and in an overlay; api on
0.0.0.0; caddy outside `edge`; missing restart / log cap / healthcheck; `build:`
on a one-shot in a production shape; `latest`/untagged image in a production
shape; registry key with no template entry and the reverse; invalid external
DSN; production shape with checkouts absent (green); a shape removed from the
list (red).

## Progress and evidence

Head SHA `69e197e1583d9adb90b0130b4a7c28d78b0878a3` on `feat/m0-compose-topology`,
PR https://github.com/yegamble/vizra/pull/4.

CI on that head: `validate` success, `ci-required` success, `GitGuardian
Security Checks` success. State is READY_FOR_REVIEW — not VERIFIED.
Environment: macOS arm64, Python 3.9.6, PyYAML 6.0.3, Docker 29.8.0,
Docker Compose v5.5.1. No image was pulled or built.

Local run — `docs/evidence/compose-topology/local-run.txt`:

| Command | Exit | Result |
|---|---|---|
| `./scripts/check-generated-ledger.sh` | 0 | 191 requirements reproduce byte-for-byte (UTF-8 and C/POSIX) |
| `./scripts/check-quality-json.py` | 0 | 4 JSON files, 191 ids, 287 references resolve |
| `./scripts/check-doc-links.py` | 0 | 94 markdown files, 7 external URLs recorded and not fetched |
| `./scripts/ci-required-guard.sh` | 0 | 6 + 7 + 10 negative fixtures exercised at their floors |
| `./scripts/compose-render.py --all` | 0 | 12 shapes rendered |
| `./scripts/check-compose-topology.py` | 0 | 12 shapes, 19 rules, 0 violations |
| `./scripts/check-config-coverage.py` | 0 | 34 component keys, 47 template keys, 47 interpolated variables, 2 aliases, 0 violations |

Red/green — `docs/evidence/compose-topology/demo-transcript.txt`, 32 assertions,
0 failures, tree byte-identical afterwards. Each case prints a sha256 either
side of its mutation and refuses to score one that did not apply. Cases: ports
on postgres (base), on the cache (overlay) and on search (base); api on
0.0.0.0; caddy outside `edge`; missing restart / log cap / healthcheck; a
`build:` reintroduced on the one-shot in a production shape; `:latest` and an
untagged image; a registry key with no template entry and a template key with
no consumer; an invalid and a missing external DSN; the bundle shape green with
no checkouts; a shape removed from the list.

Note on case 7: deleting `build: !reset null` from the production overlay
changes nothing, because the base file carries no `build:` at all — it lives
only in `docker-compose.dev.yml`, which the production chain never loads. The
first attempt at that mutation went green and was recorded as a FAIL by the
harness; the mutation was corrected to an overlay *reintroducing* a build,
which is the failure actually being modelled.

Drift — `docs/evidence/compose-topology/drift-transcript.txt`: BLOCKED (exit 2)
with the checkouts absent, clean (exit 0) against vizra-core c043df7,
vizra-user 7730500, vizra-search 808a549.

### CI findings on the first head (`aa9af5d`), both fixed

1. `validate` failed: `ModuleNotFoundError: No module named 'yaml'`. The lane
   runs on `actions/setup-python` 3.12.14, not the runner's system Python, and
   PyYAML is preinstalled only on the latter. `COMMANDS.md` had asserted "the
   runner image ships it" — true of an interpreter these scripts do not run on.
   Fixed with the same install-if-absent step and pin `ci-required.yml` uses;
   `check-compose-topology.py` now also treats PyYAML as optional (it is used
   only to name a source file in a failure message) and says so on stderr.
   Degradation verified: with `yaml` blocked, the checker still reports
   `rule=never-published service=postgres` and exits 1, losing only `file=`.
2. GitGuardian reported 1 secret: "PostgreSQL Credentials",
   `scripts/compose-shapes.json`, commit `aa9af5d`. The CI placeholder DSNs
   were written `postgres://user:password@host` — a credential-shaped string
   in a tracked file, which a scanner is right to flag and which a reviewer
   should not have to adjudicate. They only ever had to satisfy the DSN
   validator (scheme + host), so the credentials are gone.
   Fixing it at the head was **not enough**: GitGuardian scans every commit in
   the pull request, so the check stayed red on a clean head. The branch was
   therefore squashed to one commit so the string is absent from its history.
   Superseded SHAs: `aa9af5d`, `67526fd`, `864f77f`, `b206d51`. The branch had
   no review and nothing was based on it; `main` was never touched, and the
   force-push carried `--force-with-lease` pinned to the previous head.
3. The demonstration step failed with **all 32 assertions passing**: the
   generated-ledger step earlier in the same job runs the ledger generator,
   which leaves `docs/evidence/ledger-generator/__pycache__/` untracked, and
   the closing "the tree is byte-identical" assertion counted that as a restore
   that had not landed. The assertion is right to be strict — it is the only
   thing proving the mutations were reverted and it cannot tell a failed
   restore from a stray file — so the byproduct is gitignored rather than the
   check loosened, and the message now names the offending paths.
4. A fourth bug was found before CI could hit it: the lane stages models into
   `ci-report/`, which was not gitignored, so the demonstration script's
   "tree is byte-identical" assertion would have failed for a reason unrelated
   to any guard. Now ignored.

Pins verified at source, not copied: postgres 18, valkey/valkey 9.1.2,
caddy 2.11.4-alpine, clickhouse-server 25.8 and ipfs/kubo v0.39.0 digests from
`docker buildx imagetools inspect`; `actions/upload-artifact` v7.0.1 =
043fb46d1a93c77aae656e7c1c64a875d1fc6a0a from the GitHub API.

## Blockers and handoff

1. **The ledger cannot record implementation status.**
   `docs/evidence/ledger-generator/build.py:20` asserts every requirement is
   `PLANNED`/`UNVERIFIED`, so the seven IDs stay PLANNED. Relaxing it to the
   rule the file's own notice states is an owner/chair decision, not a change
   to make in the PR that would benefit from it.
2. **`.github/required-checks.txt` carries a now-stale comment** ("there is no
   compose file"). Not edited here: AGENTS.md forbids changing the required-
   check manifest in the same PR as the thing it guards.
3. **Contract changes needed from other owners** (none made here): vizra-core
   needs a `healthcheck` subcommand like vizra-search's before a compose
   healthcheck can gate readiness; `VIZRA_SEARCH_MODE` is read by core and
   search with incompatible vocabularies; `VIZRA_PUBLIC_ORIGIN`/`PUBLIC_ORIGIN`
   is a second alias of the same shape as the HMAC one and has not been ruled
   on; `SEARCH_REDIS_URL` and `REDIS_URL` in META_REPO §3 and VZ-TOPOLOGY-003
   name keys no service reads.

Next action: CI on the head SHA, then independent verification.
