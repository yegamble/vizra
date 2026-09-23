# Workflow sweep 2026-09-23: W-OP-2, W-OP-3, W-DEV-1

Sentinel: `vizra-sentinel-workflows`. Scope: W-OP-2 (first-run owner claim), W-OP-3 (health and diagnosis), W-DEV-1 (core developer loop).

## Environment and SHAs

`main` had not moved from the dispatch SHAs. Fresh `git clone` of each repo into a `mktemp -d` under the session scratchpad (`sentw.lFaIX0`):

| Repo | SHA |
|---|---|
| vizra | `b2c5b96c8dc19d7f6b4f55b5dd649a75461dbf71` |
| vizra-core | `96d19b31af8a5bd34af812e32ada0b67fa9103f4` |
| vizra-user | `783483f3c5f207d3370e6f1a79766f840e36472f` |
| vizra-search | `4810048a5c7c65c6b5134d0ec2fd0dacd5f884c6` |

Host: darwin/arm64, 8 cores, GNU Make 3.81, host Go go1.26.2 (fetched go1.27.1 through `toolchain`), sqlc v1.31.1, Python 3.9.6 + PyYAML 6.0.3, Docker 29.8.0. Services came from the digests the CI workflows use: `postgres@sha256:86c951e0…` (18.6), `valkey/valkey@sha256:c123e371…` (9.1.2) and `redis@sha256:06379549…` (7.2.16). The containers were named `sentw-*` and removed with `docker rm -f -v`. **The host was heavily loaded by other agents during the sweep** (load average 91 to 161 on 8 cores). That matters for finding F6.

Operator runs used a copy of `.env.example` with `DATABASE_URL`, `VIZRA_CACHE_URL`, `VIZRA_LISTEN_ADDR`, `VIZRA_METRICS_ADDR` and `VIZRA_PUBLIC_ORIGIN` changed to point at the sweep's containers and free ports (127.0.0.1:28080, 127.0.0.1:29090). `op.env` below means that file, loaded with `set -a; . ./op.env; set +a`.

---

## Findings (10 CONFIRMED: 0 BLOCKER, 4 MAJOR, 4 MINOR, 2 NIT)

### F1. `vizra healthcheck worker` reports ready with no worker running
- dedupe key: `vizra-core:W-OP-3:healthcheck-worker-ready-with-no-worker`
- severity: MAJOR
- workflow / doc: `vizra healthcheck worker` as a readiness probe. `AGENTS.md:13` ("`healthcheck` cannot pass while the service it probes is broken"), `AGENTS.md:477-514`, `internal/healthcheck/healthcheck.go:12-14`. The collision comes from the shared default `VIZRA_METRICS_ADDR=127.0.0.1:9090` (`internal/config/keys.go:45`, `.env.example:25`). Both `cmd/api` and `cmd/worker` bind that one key.
- expected: exit 1 when no worker is running, or when the worker's readiness listener is not its own.
- observed: in the README flow, api and worker run on one host from one `.env`, so they share the default metrics address. The api binds it first. The api's metrics server answers **every path** with Prometheus text (`cmd/api/main.go:146-148`, `promhttp.HandlerFor` as the whole handler), so `GET /readyz` on it is `HTTP 200 text/plain`. The probe treats a non-JSON 2xx as ready (`healthcheck.go:309`) and reports `ready — HTTP 200` with **no worker process at all**. A worker started on the same address loses the bind, logs `level=ERROR msg="metrics listener stopped" … bind: address already in use` (`cmd/worker/main.go:102-103`) and **keeps running with no readiness endpoint**.
- reproducer (core `96d19b3`, after `make build`, with the api from `op.env` running and its metrics on 127.0.0.1:29090):
  ```
  curl -s -o /dev/null -w '%{http_code} %{content_type}\n' http://127.0.0.1:29090/readyz
  #  200 text/plain; version=0.0.4; charset=utf-8; escaping=underscores
  VIZRA_METRICS_ADDR=127.0.0.1:29090 ./bin/vizra healthcheck worker; echo $?
  #  vizra healthcheck worker: ready — HTTP 200 (127.0.0.1:29090/readyz, 20ms)   exit 0   <- no worker exists
  (set -a; . ./op.env; set +a; ./bin/vizra-worker &)   # logs "metrics listener stopped … address already in use", keeps running
  kill <worker pid>; VIZRA_METRICS_ADDR=127.0.0.1:29090 ./bin/vizra healthcheck worker; echo $?   # still exit 0
  ```
- impact: in compose each container has its own loopback, so the collision does not occur there. It does occur in any single-host (bare-metal, systemd, local development) run that uses the documented single env file. The probe's headline guarantee does not hold there.
- smallest plausible fix (vizra-core): (a) the probe requires a JSON body whose `status` is one it knows (this is board queue item B4, "probe checks the readiness BODY"); (b) the api's metrics server serves `/metrics` only, not `/`; (c) the worker exits non-zero, or reports not-ready by some other route, when its readiness listener cannot bind; (d) either give api and worker distinct defaults, or document that they must differ.
- confidence: high. Executed 3 times (no worker, colliding worker, killed worker), all exit 0.

### F2. After the cache recovers, readiness stays `degraded` until something calls the rate limiter
- dedupe key: `vizra-core:W-OP-3:readyz-cache-degraded-sticks-after-recovery`
- severity: MAJOR
- workflow / doc: readiness with the cache down, and its recovery. `AGENTS.md:490-497`, `internal/httpapi/probes.go:178-189`, `internal/cache/ratelimit.go:55-59` ("Degraded reports whether the most recent decision came from the fallback").
- expected: once Valkey answers PING again, `/readyz` returns to `ok`, or at worst it reports a statement that is still true.
- observed: any setup request during the outage sets `FallbackLimiter.degraded=true`. Only the next limiter decision clears it, and in M1-A only the two `/api/v1/setup/*` routes consult the limiter. `/readyz` therefore reports `degraded` with detail **"rate limiting is running on the in-process fallback"** for as long as nobody calls a setup route. On a claimed instance that can be indefinitely. The statement is false: the next call would use the cache. One `GET /api/v1/setup/claim-status` flips readiness back to `ok`.
- reproducer (api from `op.env` on :28080, cache container `sentw-opcache`):
  ```
  docker stop sentw-opcache; curl -s http://127.0.0.1:28080/api/v1/setup/claim-status >/dev/null
  docker start sentw-opcache; until docker exec sentw-opcache valkey-cli ping | grep -q PONG; do sleep .5; done; sleep 15
  curl -s http://127.0.0.1:28080/readyz     # "degraded" … "rate limiting is running on the in-process fallback"
  curl -s http://127.0.0.1:28080/api/v1/setup/claim-status >/dev/null; sleep 3
  curl -s http://127.0.0.1:28080/readyz     # "ok"
  ```
  Observed degraded at +15 s, +25 s and +35 s after PONG on the first run, and again at +15 s on runs 2 and 3 (3/3).
- impact: `vizra healthcheck api` still exits 0, so rotation is unaffected. Monitoring that alerts on `degraded` fires for an outage that ended, and the detail text misleads the operator reading it.
- smallest plausible fix (vizra-core): have readiness probe the cache directly (it already PINGs it) and not report a stale "most recent decision" flag. Or give `Degraded()` a TTL, or let a successful PING clear it. Add a test: outage, then recovery, then readiness `ok` with no setup traffic.
- confidence: high (3/3).

### F3. The README's getting-started steps do not boot: `.env.example`'s `DATABASE_URL` is not a DSN, and a test that says the template boots overwrites that value
- dedupe key: `vizra-core:W-DEV-1:env-example-does-not-boot-getting-started`
- severity: MAJOR
- workflow / doc: `README.md:29-39` (`cp .env.example .env  # development defaults` … `./bin/vizra doctor`), `.env.example:32` (`DATABASE_URL=CHANGE-ME-generate-with-openssl-rand-base64-32`), `.env.example:12` ("Generate real ones: openssl rand -base64 32"), `internal/config/template_test.go:89-95`.
- expected: the README calls the file "development defaults", and `TestTemplateBootsInDevelopment` claims `.env.example` boots in development mode, so the literal steps should give a doctor run with checks in it.
- observed: (1) no binary reads `.env`. `./bin/vizra doctor` reads the process environment and prints `FAIL config: DATABASE_URL must be set` (2 checks, exit 1). (2) Loading the unmodified copy (`--env .env`, or sourcing it) is refused by `vizra doctor`, `vizra-api`, `vizra migrate` and `vizra claim-token` alike: `DATABASE_URL: must be a postgres:// or postgresql:// DSN`, exit 1. (3) `TestTemplateBootsInDevelopment` sets `env["DATABASE_URL"] = "postgres://…"` before checking, so it passes on a template that does not boot. The test name claims more than it checks (R1, R11). The placeholder tells the operator to generate a DSN with `openssl rand`, which is not possible.
- reproducer (core `96d19b3`):
  ```
  cp .env.example .env && make build
  ./bin/vizra doctor; echo $?                     # FAIL config: DATABASE_URL must be set — exit 1
  ./bin/vizra doctor --env .env; echo $?          # FAIL config: DATABASE_URL must be a postgres:// or postgresql:// DSN — exit 1
  (set -a; . ./.env; set +a; ./bin/vizra-api; echo $?)   # "vizra-api refused to start … DATABASE_URL: must be a postgres:// …" exit 1
  sed -n 89,95p internal/config/template_test.go  # the test overwrites DATABASE_URL
  ```
- smallest plausible fix (vizra-core): ship a development DSN that matches the README's `docker run` line (`postgres://vizra:vizra@127.0.0.1:55432/vizra_test?sslmode=disable`, or a dev database), which production already refuses as a known value. Make the test check the template's values unmodified. Have the README say `./bin/vizra doctor --env .env` (or export the file) and give the DSN placeholder its own text instead of the `openssl` hint.
- confidence: high.

### F4. The claim page that the README and `vizra claim-token` send the operator to does not exist
- dedupe key: `vizra-core:W-OP-2:claim-page-does-not-exist`
- severity: MAJOR
- workflow / doc: `README.md:104-113` ("Then open `/setup/claim`, paste the token, and create the owner account"). `cmd/vizra/claimtoken.go:68-71` prints "Paste it into the claim page at <VIZRA_PUBLIC_ORIGIN>/setup/claim".
- expected: `/setup/claim` serves a form that redeems the token.
- observed: the api answers `GET /setup/claim` with `403 {"error":{"code":"instance_unclaimed","message":"this instance has no owner yet; every other route is refused until it is claimed",…}}`. vizra-user `783483f` has no such route: `app/` holds only `page.tsx`, `health/page.tsx` and `layout.tsx`, with no middleware and no rewrites. The claim works only through `POST /api/v1/setup/claim-owner` with a hand-built JSON body. No operator document gives that path; it appears only in `api/openapi.yaml`. The design exists (board: Figma D2, "owner claim"), but the page has not been built.
- reproducer (api from `op.env`, freshly migrated database):
  ```
  ./bin/vizra claim-token 2>&1 >/dev/null | sed -n 2p   # "Paste it into the claim page at http://localhost:28080/setup/claim"
  curl -s -w ' %{http_code}\n' http://127.0.0.1:28080/setup/claim   # 403 instance_unclaimed
  find vizra-user/app -type f                                       # no setup/claim route at 783483f
  ```
- smallest plausible fix: until vizra-user ships the page, the core README and the CLI's stderr text document the `curl` redemption (Content-Type, the four fields, the 201/403/409 meanings) and say the page is coming. Owners: vizra-core for the docs and CLI text, vizra-user for the page (VZ-INSTALL-003's UI surface).
- confidence: high.

### F5. `vizra doctor` silently drops the checks it did not run and reports "0 not run"
- dedupe key: `vizra-core:W-OP-3:doctor-omits-dependent-checks-reports-0-not-run`
- severity: MINOR (the exit code is still 1 and the causing FAIL is named, but the summary says less was skipped than was)
- workflow / doc: `README.md:38` ("real checks only; a missing prerequisite is SKIP, never OK"), `README.md:124` ("`vizra doctor` reports whether the instance is claimed"), `cmd/vizra/doctor.go:192-195, 199-229, 232-244`, `internal/doctor/doctor.go:306`.
- expected: a check whose prerequisite failed is listed as SKIP and counted in "not run".
- observed (3 cases, all with `N check(s): 1 failed, 0 not run.`):
  - config invalid: 2 checks are printed. Database, schema, owner claim, cache, cache floor, public origin and search are missing.
  - PostgreSQL down: 7 checks. `database version`, `schema` and `owner claim` are missing, so the claimed/unclaimed line that README:124 promises is absent.
  - cache down: 9 checks. `cache version floor` is missing.
- reproducer:
  ```
  env -i PATH=$PATH ./bin/vizra doctor                                   # 2 check(s): 1 failed, 0 not run.
  (set -a; . ./op.env; set +a; docker stop sentw-opcache; ./bin/vizra doctor)   # 9 check(s): 1 failed, 0 not run.
  (… DATABASE_URL pointed at a stopped PostgreSQL …; ./bin/vizra doctor)       # 7 check(s): 1 failed, 0 not run.
  ```
- smallest plausible fix (vizra-core): `collect()` emits a SKIP result, with the reason, for every dependent check it does not reach. A test asserts that the set of check names is the same on every path.
- confidence: high.

### F6. Flaky: `internal/fixtures` hits `go test`'s default 10-minute timeout inside the integration suite, and leaks its shared corpus directory when it does
- dedupe key: `vizra-core:W-DEV-1:fixtures-default-timeout-in-integration-suite`
- severity: MINOR (flaky; host-load dependent)
- workflow / doc: `README.md:41-55` / `Makefile:167` (`make test-integration` = `go test -race -count=1 -tags=integration ./...`, no `-timeout`), and the direct CI form in `docs/quality/COMMANDS.md:157-163`.
- expected: the suite passes on a developer machine.
- observed: **2 of 3 integration runs failed**, both with `panic: test timed out after 10m0s` in `TestManifestDetectsEveryClassOfDrift`. `internal/fixtures` ran 602.8 s and 612.6 s, alongside `internal/integration` (489 s / 422 s) in the same `./...` run. The Redis run passed with fixtures at 342 s. `make ci`'s `test-race` passed with fixtures at 398 s, already two thirds of the budget. The timed-out process never reaches `TestMain`'s `RemoveAll`, so each timeout left a `vizra-fixtures-shared-*` directory in `$TMPDIR` (2/2; the sweep deleted both by exact path). This is the same class as S-0001, from a different test. **Caveat:** the host's load average was 91 to 161 on 8 cores, from other agents. `docs/quality/COMMANDS.md:237` records the same timeout from an earlier session and calls it an infrastructure timeout. This is a flaky report under load, not a proven defect on an idle machine.
- reproducer: services as in the README, then `VIZRA_TEST_DATABASE_URL=… VIZRA_TEST_CACHE_URL=… make test-integration` on a loaded host. Runs: Valkey `make` exit 2 (fixtures timeout), Redis 7.2 `make` exit 0, Valkey direct plus `go-test-report.py` exit 1 (fixtures timeout; the report correctly failed closed, citing both the panic and the per-package floor of 14 < 36).
- smallest plausible fix (vizra-core): give the test lanes an explicit `-timeout` sized to the measured runtime, or cut the fixtures package's cost under `-race` (it regenerates the corpus several times). Clean the shared directory from a path that survives a timeout (a deterministic per-run directory under `t.TempDir`'s parent, swept on the next run).
- confidence: medium (flaky, 2/3, load-dependent).

### F7. CLI subcommand lists disagree with the binary
- dedupe key: `vizra-core:W-OP-3:cli-subcommand-docs-drift`
- severity: MINOR
- workflow / doc: `AGENTS.md:13` says `cmd/vizra` is "setup, doctor, migrate, backup, restore, **healthcheck**". `README.md:19` says "version, doctor, migrate", which omits `healthcheck` and `claim-token`, both on main.
- observed: `vizra setup`, `vizra backup` and `vizra restore` each print `vizra: unknown command` and exit 2. The binary's own usage text is correct: those commands are "arriving with later slices".
- reproducer: `for c in setup backup restore; do ./bin/vizra $c; echo $?; done`, then read `README.md:19`.
- smallest plausible fix (vizra-core): make both lists match `cmd/vizra/main.go`'s usage and mark future commands as future.
- confidence: high.

### F8. Meta compose comments still say core has no `healthcheck` subcommand and only three subcommands
- dedupe key: `vizra:W-OP-3:compose-comments-deny-core-healthcheck`
- severity: MINOR
- workflow / doc: meta `docker-compose.yml:250-252` ("vizra-core has no `healthcheck` subcommand"), `docker-compose.yml:89` ("`vizra` has three subcommands (version, doctor, migrate)").
- observed: vizra-core `96d19b3` ships `vizra healthcheck api|worker` (exit 0/1 as documented; see "Workflows that worked") and `vizra claim-token`. The probe swap itself is board queue item 2k. Line 89 is a separate stale sentence, in the MFA-key comment, that 2k does not obviously cover.
- reproducer: `sed -n 89p docker-compose.yml; sed -n 250,252p docker-compose.yml` at meta `b2c5b96`, against `./bin/vizra --help` at core `96d19b3`.
- smallest plausible fix (meta): fold both sentences into the 2k follow-up PR.
- confidence: high.

### N1. `vizra claim-token` on an unmigrated database prints a raw SQL error with no next step
- dedupe key: `vizra-core:W-OP-2:claim-token-unmigrated-raw-sql-error`
- severity: NIT
- observed: `vizra claim-token could not mint a token: ownerclaim: checking for users: ERROR: relation "users" does not exist (SQLSTATE 42P01)`, exit 1. `vizra doctor` on the same database does say "(`vizra migrate`)".
- reproducer: create an empty database, point `op.env` at it, and run `./bin/vizra claim-token`.
- fix (vizra-core): map SQLSTATE 42P01 on this path to "the schema is behind; run `vizra migrate`". Confidence: high.

### N2. `vizra-api` logs "listening" before it has bound, then exits on the bind error
- dedupe key: `vizra-core:W-OP-3:listening-logged-before-bind`
- severity: NIT
- observed: with the port taken, the log is `msg="vizra-api listening" addr=127.0.0.1:18080` followed by `listen tcp 127.0.0.1:18080: bind: address already in use`, exit non-zero (`cmd/api/main.go`, the log call precedes `ListenAndServe` in the goroutine).
- reproducer: run `./bin/vizra-api` with `VIZRA_LISTEN_ADDR` set to an occupied port.
- fix (vizra-core): `net.Listen` first, log, then `Serve`. Confidence: high.

---

## Workflows that WORKED (core `96d19b3` unless stated)

| Workflow | Command | Result |
|---|---|---|
| W-DEV-1 gate | `make ci` (fresh clone, `.env` copied) | exit 0, 7 m 20 s; all 10 lanes; `make-integrity-guard: passed (8 gate target(s); make ran 18 time(s)…)`; test-race 17 ok / 8 no-test-files |
| W-DEV-1 integration, Redis 7.2.16 | `VIZRA_TEST_DATABASE_URL=… VIZRA_TEST_CACHE_URL=redis://…:56579/0 VIZRA_TEST_CACHE_FLAVOUR=redis make test-integration` | exit 0, 5 m 55 s; every package ok (`internal/integration` 146 s) |
| W-DEV-1 integration, Valkey 9.1.2, CI form | `go test -race -count=1 -tags=integration -json ./...` + `go-test-report.py --suite integration` | 1469 executed, 1469 passed, **0 skipped**, floor 1150; `internal/integration` 169 tests passed. The only failure was the F6 fixtures timeout (report exit 1, failed closed as designed) |
| sqlc-verify can fail | hand-edit `internal/store/sqlcgen/sites.sql.go`; separately, add a query to `store/queries/audit.sql` without regenerating | both `make sqlc-verify` exit 2 |
| migrate-lint can fail | edit `0001_*.up.sql`; add gap `0007`; add `DROP TABLE users` in `0006` (manifest regenerated) | exit 2 for each, each naming its cause (`manifest`, `version gap: 0006 is missing before 0007`, `destructive statement in an up migration`); control: a benign `0006` passes (exit 0) |
| openapi-verify can fail | rename `/version` in `api/openapi.yaml` | exit 2; `TestEveryRouteHasASpecOperation`, `TestEverySpecOperationHasARoute` and `TestPublicContractIsTheProbesPlusTheSetupOperations` FAIL |
| fixtures-verify can fail | flip one digest nibble in `fixtures/manifest.json` | exit 2 (`the corpus does not match the committed manifest`) |
| Integration fails, does not skip | `make test-integration` without `VIZRA_TEST_DATABASE_URL`; a cache test without `VIZRA_TEST_CACHE_URL` | exit 2 "BLOCKED, not passed"; `--- FAIL` "BLOCKED, not skipped" |
| W-OP-2 claim, end to end over the API | `vizra migrate` then `vizra-api`; `claim-status` → `{"claimed":false}`; `vizra claim-token` (token alone on stdout, 65 bytes with newline; instructions on stderr); a re-mint supersedes it (the old token → 403 `forbidden`); new token → 201 `{"username":…,"role":"owner"}`; same request again → 409 `conflict`; `claim-status` → `{"claimed":true}`; `vizra claim-token` → refused, exit 1 | all as documented |
| W-OP-2 rate limit | 62 wrong-token claims from loopback → 60 × 403 then 2 × 429 (global budget 60/15 min; the per-origin bucket is NULL for loopback by design); then the valid token → 201 | as documented at `AGENTS.md:406` ("valid token is never 429 by the failure limiter") |
| W-OP-3 doctor | before migrate: `FAIL owner claim … (vizra migrate)`; after: `WARN owner claim unclaimed and no token is live; run vizra claim-token`; after claim: `OK owner claim this instance has an owner`; cache down: `FAIL cache unreachable…` exit 1; PostgreSQL down: `FAIL database PostgreSQL is unreachable` exit 1 | as documented (see F5 for the omitted lines) |
| W-OP-3 healthcheck / readiness | healthy: api and worker exit 0 `ok`; cache down: `/readyz` 200 `degraded` (cache named), `healthcheck api` exit 0 printing `degraded`; PostgreSQL down: `/readyz` 503 `unavailable`, `healthcheck api` and `healthcheck worker` both exit 1 `NOT READY — HTTP 503`; after PostgreSQL restarts both exit 0; `healthcheck bogus` exit 64 | as documented, except for F1 and F2 |

## Unconfirmed leads (not findings)

1. **R9 on the limiter.** `FallbackLimiter.Allow` (`internal/cache/ratelimit.go:93-95`) sets `degraded=true` on any `Exec` error, including a cancelled request context, and F2 means the flag then sticks. A client that disconnects mid-limiter call could leave readiness `degraded` on a healthy cache. Not reproduced; the timing would need a crafted cancel.
2. **R9 in worker logs.** On SIGTERM the worker logs `level=WARN msg="jobs: claim failed" … error="context canceled"`. Observed once. Whether it touches health or budgets was not checked; left to the bug sentinel.
3. **R10.** go-redis writes unstructured `redis: … pool.go:762: … dial tcp 127.0.0.1:56679: connect: connection refused` lines to the stderr of `vizra-api` and `vizra doctor`, bypassing `obs.Redact`. Only host:port was seen. Whether any go-redis path can echo a password-bearing URL was not tested.
4. `vizra claim-token` and `vizra migrate` run on `context.Background()` with no deadline, so a blackholed DSN host might hang until the OS connect timeout. Not run.
5. The per-origin failure budget is NULL for loopback clients and for any request carrying `X-Forwarded-For`/`Forwarded`, so in the shipped Caddy topology only the global 60/15-minute bucket ever applies. It is documented for proxies (`AGENTS.md` "What is deliberately absent"), but not for loopback.
6. `$TMPDIR` holds further `vizra-fixtures-shared-*` and `vizra-healthcheck-bin-*` directories from other concurrent sessions (not attributable to this sweep and not touched).

## Not run, and why

- **W-OP-2 and W-OP-3 through the meta compose** (`docker compose exec api vizra claim-token`, compose `healthcheck:` lines): no core, user or search images are published at these SHAs, and `deploy/Caddyfile.local` is generated by `vizra setup`, which does not exist. That is W-OP-1's scope. NOT RUN.
- **The README unit-suite reproduction** (`go test -race -json ./…` + `go-test-report.py --suite unit`): NOT RUN, because of time on a host at load average above 100. The unit suite ran under `make ci` (exit 0) without per-test counts.
- **Redis 7.2 counts through `go-test-report.py`**: only the `make test-integration` form ran on Redis (exit 0), so per-test and skip counts exist for Valkey only.
- `make test-integration-shuffle`, GNU Make 4.3 (the host has 3.81), and the claim page in a browser (it does not exist; see F4).

## Interference and hygiene notes (recorded, not hidden)

- **The sweep paused its own `sentw-pg` for about 9 s** (14:46:33 to 14:46:42 EDT) during the Valkey `make test-integration` run, by mistake while setting up a PostgreSQL-down probe. The PostgreSQL-down probe was then redone on a separate container (`sentw-pg2`). In that run `internal/integration` passed (489 s); the run's failure was the F6 fixtures timeout, which does not use PostgreSQL. The direct Valkey re-run, with no interference, reproduced the same timeout.
- A mutation step briefly wrote a scratch file at `/tmp/x` instead of the scratchpad. It was deleted.
- Cleanup done: api and worker processes killed; `sentw-pg`, `sentw-pg2`, `sentw-valkey`, `sentw-redis72` and `sentw-opcache` removed with `docker rm -f -v`; this sweep's own leaked temp directories deleted by exact path (`vizra-healthcheck-bin-3420024366`, `-1153068444`, `-31310674`; `vizra-fixtures-shared-1047789429`, `-649011985`), each attributed by an embedded clone path or by package start time; minted claim tokens deleted; the scratch clones removed. Disk free stayed between 17 and 22 GiB throughout.
