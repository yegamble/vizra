# Execution plan: vizra-core hardening sweep B2 — `vizra healthcheck` and the runtime image

## Context

- Repo `vizra-core`, branch `feat/m0-healthcheck-runtime-image` from `origin/main` @ `4a80a1e3f36b8001c2954d0568bea29268e739fe`.
- Drivers:
  - `docs/evidence/warroom/2026-09-21-meta-pr4-compose-topology-INFRASTRUCTURE.md`
    **FINDING 3** — api/worker healthchecks are `["CMD","/usr/local/bin/vizra","version"]`,
    a probe that cannot fail while the service is broken, and `frontend` gated on it.
    Chair ruling (tick 76, item 3): **no `/dev/tcp` bridge** — it would bake a bash
    dependency into the runtime image that queue 2d rebuilds from a clean base. The
    durable fix is queue **2h**: a `vizra healthcheck` subcommand in core.
  - Same file **FINDING 5** — the image creates `/var/lib/vizra` but not
    `/var/lib/vizra/media`, which compose mounts. Docker creates an absent
    mountpoint `root:root`; the container runs as uid 10001, so the first upload
    would fail with `EACCES`. Queued to 2d.
  - `docs/plans/WARROOM-BOARD.md` queue row **2d** (the two image items only:
    runtime stage from a clean digest-pinned base instead of the builder stage,
    no `|| true` on the purge; image scan lane failing on scanner error) and row
    **2h** (`vizra healthcheck`).
- Shape to mirror: `vizra-search`'s `healthcheck` subcommand
  (`vizra-search/cmd/vizra-search/main.go`, ~line 79) — read-only, another repo.

## Acceptance

### A1 — `vizra healthcheck`, a probe that cannot pass while the service is broken

- `vizra healthcheck api` requests the local listener's **readiness** endpoint and
  exits 0 only on a ready answer. Non-zero on connection refused, timeout, non-2xx.
- `degraded` mapping, **decided and documented, not silently stricter**: core's
  `/readyz` 503s on PostgreSQL only; cache down, search unreachable and a stale
  queue yield **200 `degraded`** so a degraded instance keeps serving reads instead
  of being pulled from rotation (`internal/httpapi/probes.go:74-82`, ADR-002 §Probes).
  The probe keeps exactly that semantics: **any 2xx → exit 0**, and it prints the
  reported status so `degraded` is visible in `docker inspect`'s health log. It does
  not invent a stricter rule; a stricter probe would take a site down when Redis blips.
- `vizra healthcheck worker` — the worker has no API listener. It gains a **real**
  readiness signal on the existing metrics listener (`VIZRA_METRICS_ADDR`):
  `/readyz`, reporting per site (a) PostgreSQL reachability measured **at probe
  time**, and (b) the claim loop's last progress against a staleness bound.
  Not "the process exists", not `vizra version`.
- Bounded: `--timeout` default **2s** (well under the 3s Docker healthcheck timeout
  in the compose lines below), context propagated, **no retries inside the probe**
  (Docker's `--interval`/`--retries` already supply them), no secrets or DSNs in the
  output, documented exit codes.
- Address comes from the config keys the services already read —
  `VIZRA_LISTEN_ADDR` / `VIZRA_METRICS_ADDR`. **No new operator-facing key.**
- *demonstrated* on real processes with real PostgreSQL (integration lane):
  api healthy → 0; PostgreSQL stopped → non-zero within the deadline; listener
  absent → non-zero; worker healthy → 0; worker with the database unreachable →
  non-zero; worker with the loop stalled past the bound → non-zero.
  Mutation: probe returns 0 unconditionally → the tests go red by name.

### A2 — runtime image

- Runtime stage `FROM` a clean digest-pinned base, **not** `FROM vips`; no toolchain
  carried over; **no `|| true`** on any purge/cleanup step (the purge disappears —
  there is nothing to purge from a clean base).
- `/var/lib/vizra/media` exists and is owned by uid 10001.
- *demonstrated in CI on the built image*: run as the default user, write into
  `/var/lib/vizra/media` and read back; `vizra`, `vizra-api`, `vizra-worker` present;
  `vizra healthcheck --help` runs; toolchain absent.
- libvips runtime libraries still work — proved by a check that **loads** them, and
  the existing loader-list assertion is kept, not weakened.
- Image size before/after reported.

### A3 — image scan lane

- Fails on **scanner error**, not only on findings, and cannot pass vacuously:
  no image scanned, empty/`null` results, undetected OS, wrong artifact, malformed
  JSON, swallowed exit.
- *demonstrated* by the smallest mutation that makes the scanner error or the report
  empty → red by name.

### Non-goals (queued elsewhere, not started here)

The PR #6 verifier's guard fixes (workflow-line make flags, zero-test refusal,
append-only provenance, FLOOR_LANES vs the required loop); the `internal/obs`
redaction review; `vizra setup` / deploy; any compose file; any migration; anything
under `api/`.

## Implementation

| Area | Change |
|---|---|
| `internal/healthcheck/` (new) | the probe: target table, bind→dial address mapping, bounded single-shot HTTP GET, exit codes, message formatting with no secrets |
| `cmd/vizra/main.go`, `cmd/vizra/healthcheck.go` (new) | the `healthcheck` subcommand and its usage line |
| `internal/jobs/health.go` (new) | `Health` tracker + `/readyz` handler for the worker |
| `internal/jobs/worker.go` | claim loop records progress; the semaphore wait is bounded so a saturated worker still ticks |
| `cmd/worker/main.go` | metrics listener gains `/readyz` (and `/healthz`); promhttp stays mounted at `/` so nothing that scrapes it today changes |
| `internal/config/keys.go` | `DefaultFor(name)` helper only — **no new key** |
| `Dockerfile` | runtime stage from the pinned `debian@sha256:…` base; runtime shared-library set derived mechanically from `ldd`+`dpkg-query` in a metadata stage rather than hand-typed; `/var/lib/vizra/media` owned by 10001; `HEALTHCHECK` → `vizra healthcheck api` |
| `.github/workflows/docker-build.yml` | image assertions: media write/read as the default user, three binaries, `healthcheck --help`, toolchain absent, runtime `vips -l` equals the baked-in loader list, image size |
| `scripts/image-scan-verdict.py` (new) + `scripts/testdata/imagescan/` | the scan verdict and its anti-vacuity assertions, unit-tested from fixtures |
| `.github/workflows/image-scan.yml` (new) | Trivy over the built image, calling that script |

Interfaces shared with other workstreams: the compose `healthcheck:` lines meta
consumes (reported, not edited here — `api/openapi.yaml` and compose are other
owners').

## Verification

| Lane | Command |
|---|---|
| gate | `make ci` |
| tidy | `make tidy-check` |
| guards | `./scripts/make-integrity-guard.sh`, `python3 scripts/ci-required-guard.py` |
| integration | `make test-integration` and `make test-integration-shuffle` with `VIZRA_TEST_DATABASE_URL` / `VIZRA_TEST_CACHE_URL` against local PostgreSQL 18 + Valkey 9.1.2 (same digests CI pins) |
| focused | `go test -race -tags=integration ./internal/integration/ -run Healthcheck` |
| scan verdict | `go test ./scripts/ -run ImageScan` |
| image | CI `docker-build` + `image-scan` on ubuntu-24.04/linux-amd64 (the acceptance platform; this machine is arm64) |

Services: PostgreSQL 18 and Valkey 9.1.2 as local containers named `vzhcb-*`
(only those are removed at the end; `vidra-*` containers belong to another project).

## Progress and evidence

### 2026-09-21 — implemented, pushed, PR open

- Branch `feat/m0-healthcheck-runtime-image`, head **`68292851e768dd77516c6e49b7831507e4757919`**, one commit.
- PR: https://github.com/yegamble/vizra-core/pull/7 — **READY_FOR_REVIEW**, not verified.
- Files: 57 changed, +5154 −21. `api/` and `migrations/` byte-identical to main
  (`git status --short -- api/ migrations/` empty). No new config key.

#### Local lanes, source SHA `6829285`, darwin/arm64, go1.27.1

| command | exit | counts |
|---|---|---|
| `make ci` | 0 | 14 packages ok, 6 `[no test files]`, 0 skips |
| `make tidy-check` | 0 | — |
| `python3 scripts/ci-required-guard.py` | 0 | 9/9 checks, 6/6 floor lanes |
| `./scripts/make-integrity-guard.sh` | 0 | 8 gate targets |
| `make test-integration` | 0 | 0 skips |
| `make test-integration-shuffle` | 0 | 0 skips |
| `go test -race -tags=integration ./internal/integration/` | 0 | 31 tests, 0 skips |
| `go test ./scripts/ -run ImageScan` | 0 | 16 fixtures |

Services: PostgreSQL 18 (`postgres@sha256:86c951e0…`) and Valkey 9.1.2
(`valkey/valkey@sha256:c123e371…`) as local containers `vzhcb-postgres` /
`vzhcb-cache`, removed at the end.

#### Demonstrations — `vizra-core/docs/evidence/healthcheck-runtime-image/`

Harness refuses to score a mutation that did not apply (sha256 before/after,
restore verified byte-identical). All six: red under mutation, green restored.

| mutation | red by name |
|---|---|
| M1 probe returns 0 unconditionally | 11 tests, incl. all five real-process ones |
| M2 staleness bound never applied | `TestAClaimLoopStalledPastTheBoundIsNotReady`, `TestHealthcheckWorkerIsNonZeroWhenTheClaimLoopStallsWhilePostgresIsFine` |
| M3 PostgreSQL assumed reachable | 4 tests incl. `TestHealthcheckWorkerIsZeroWhenTheLoopIsRunningAndNonZeroWhenPostgresStops` |
| M4 unrecognised OS accepted | `…/no-os-detected` |
| M5 scanner exit ignored | `…/scanner-error`, `…/scanner-crashed` |
| M6 Dockerfile drops the media directory | exactly one image assertion |

Image size, **linux/arm64, local**: 942 759 402 B (899 MiB) → 232 051 189 B
(221 MiB), −677 MiB. The old `|| true` purge did remove 80 packages from the
final filesystem and the image was still 899 MiB — a removed file still ships
in the earlier layer. It also left `pkgconf-bin` (providing `/usr/bin/pkg-config`),
`linux-libc-dev` and `/src` (the `vips` stage's `WORKDIR /src` is inherited and
Docker recreates it at container start, undoing the `rm -rf /src`).

A data race in my own test (`hits++` across goroutines) was caught by the race
detector on the first `make ci` and fixed with `atomic.Int32`.

#### What did not run

- **Every image measurement is linux/arm64, local.** CI `ubuntu-24.04` /
  `linux/amd64` is the acceptance platform (ADR-009); this machine cannot build
  an emulated amd64 image with the disk it has.
- **`image-scan` has never executed anywhere.** `trivy` is not installed
  locally — BLOCKED, not a pass. Its verdict logic is demonstrated from
  committed fixtures; its Trivy invocation and CI wiring are unproven until the
  first CI run. Flags confirmed against the pinned image's own `--help`.
- The new `docker-build` steps have not run on amd64 — same caveat.

#### Pins confirmed against the real registry, 2026-09-21

| pin | how |
|---|---|
| `golang@sha256:433790e5…`, `debian@sha256:a99cfc51…` | `docker manifest inspect` — OCI indexes with linux/amd64 + linux/arm64 |
| `aquasec/trivy@sha256:be1190af…` = 0.70.0 | Docker Hub tag API **and** `docker manifest inspect` (amd64 `sha256:85e87be1…`); `--version` from the image |
| `actions/checkout@3d3c42e5…`, `actions/upload-artifact@043fb46d…` | the SHAs already pinned in this repository |

#### The compose lines meta should consume (reported, not edited here)

```yaml
  api:
    healthcheck:
      test: ["CMD", "/usr/local/bin/vizra", "healthcheck", "api"]
      interval: 15s
      timeout: 3s
      start_period: 30s
      retries: 3

  worker:
    healthcheck:
      test: ["CMD", "/usr/local/bin/vizra", "healthcheck", "worker"]
      interval: 15s
      timeout: 3s
      start_period: 30s
      retries: 3
```

#### A guard heuristic worth knowing about (NOT changed)

`scripts/ci-required-guard.py`'s ANCHOR check treats a bare `make` token
anywhere in a floor lane's `run:` as a make invocation and demands the
make-integrity anchor before it. A toolchain denylist that merely MENTIONS
`make` trips it. The heuristic fails CLOSED and is right to; the list moved to
`scripts/runtime-toolchain-denylist.txt` instead. Neither guard was edited.

## Blockers and handoff

`trivy` is not installed locally → the scan lane's own execution is CI-only;
its verdict logic is demonstrated locally from committed fixtures. That is
BLOCKED for the local lane, never a pass.

Next concrete action: read the check-runs on `6829285` — in particular the
FIRST-EVER run of `image-scan` and the new `docker-build` assertions on amd64 —
then hand to an independent verifier. Nothing here is VERIFIED.
