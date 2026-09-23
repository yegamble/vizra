# Spot-check 2026-09-23: workflow sweep MAJORs S-0011 to S-0014

The source is `docs/sentinel/sweeps/2026-09-23-workflows-op2-op3-dev1.md` (F1 to F4). An independent verifier that did not write the sweep ran this check. It tried to disprove each finding and confirmed a finding only after reproducing it. It edited nothing, pushed nothing and merged nothing. The one exception is a temporary one-line mutation to a test in the scratch clone (S-0013), which was restored with `git checkout` before the clone was deleted.

## Summary

| ID | Sweep | Verdict | Severity |
|---|---|---|---|
| S-0011 | F1 | CONFIRMED at a **different severity** | MAJOR → **MINOR**. The mechanism reproduces 3 times out of 3. No documented topology puts api and worker in one network namespace. |
| S-0012 | F2 | CONFIRMED at a **different severity** | MAJOR → **MINOR**. Reproduced 3 times out of 3. Only the status word and detail text are wrong: probe exit codes, rotation and limiter decisions are unaffected, and `doctor` reports the cache correctly. |
| S-0013 | F3 | CONFIRMED at the stated severity | **MAJOR**. The README's literal steps fail, and the test named for this passes only because it substitutes its own DSN (demonstrated by mutation). |
| S-0014 | F4 | CONFIRMED at the stated severity | **MAJOR**. The CLI prints a URL that returns 403 before the claim and 404 after it. No operator document describes a path that works. |

## Environment

| Item | Value |
|---|---|
| vizra-core | `96d19b31af8a5bd34af812e32ada0b67fa9103f4`. `main` **has not moved** since the sweep. |
| vizra-user | `783483f3c5f207d3370e6f1a79766f840e36472f` (unchanged) |
| vizra (meta) | `b2c5b96c8dc19d7f6b4f55b5dd649a75461dbf71` (origin `main`, unchanged) |
| Clones | fresh `git clone` into `mktemp -d …/scratchpad/vzv-core-spotcheck-XXXXXX` (deleted afterwards) |
| PostgreSQL | `spotv-pg`, `postgres@sha256:86c951e0…` → `PostgreSQL 18.6 (Debian 18.6-1.pgdg13+2)` |
| Cache | `spotv-cache`, `valkey/valkey@sha256:c123e371…` → `Valkey server v=9.1.2`, host port fixed at 127.0.0.1:47379 so that a `docker stop`/`start` cannot move it |
| Host | darwin/arm64. Load average about 250 from other agents. `make build` took 3 min 45 s (exit 0). |
| Operator env (`op.env`) | `.env.example` with five keys changed: `DATABASE_URL` set to the spotv-pg DSN, `VIZRA_CACHE_URL` to `redis://127.0.0.1:47379/0`, `VIZRA_LISTEN_ADDR` to `127.0.0.1:47080`, `VIZRA_METRICS_ADDR` to `127.0.0.1:47090` and `VIZRA_PUBLIC_ORIGIN` to `http://localhost:47080`. Loaded with `set -a; . ../op.env; set +a`. `vizra migrate` exit 0, schema version 5. |

---

## S-0011: `vizra healthcheck worker` reports ready with no worker

### Reproduction (3 of 3)
The api was started from `op.env`. `lsof` shows `vizra-api 37531 … TCP 127.0.0.1:47090 (LISTEN)`, which is the api's own metrics listener.

| Case | Command | Output | Exit |
|---|---|---|---|
| no worker process | `./bin/vizra healthcheck worker` | `ready — HTTP 200 (127.0.0.1:47090/readyz, 11ms)` | **0** |
| worker started from the same env | `./bin/vizra-worker &` then probe | worker log: `level=ERROR msg="metrics listener stopped" error="listen tcp 127.0.0.1:47090: bind: address already in use"`. The worker stays alive (pid 37848). Probe prints `ready — HTTP 200` | **0** |
| worker killed | `kill 37848` then probe | `ready — HTTP 200` | **0** |
| control A: distinct address, no worker | `VIZRA_METRICS_ADDR=127.0.0.1:47091 ./bin/vizra healthcheck worker` | `NOT READY — dial: connect: connection refused` | 1 |
| control B: worker on a distinct address | the same, with a worker bound to :47091 | `ready — HTTP 200 ok`; the body is the worker's JSON (`"ready":true,"claim_loop":"ok"`) | 0 |

`curl http://127.0.0.1:47090/readyz` returns `200 text/plain; version=0.0.4 …` with Prometheus text. `cmd/api/main.go:146-148` mounts `promhttp.HandlerFor` as the whole handler. `internal/healthcheck/healthcheck.go:309-316` treats the status word as best effort, so any 2xx passes (`"a non-JSON body is not itself a failure, the HTTP code is the verdict"`). Two signs tell the false ready from the real one. The false ready prints no status word (`HTTP 200`), and the real one prints `HTTP 200 ok`.

### Is this a real single-host operator path? No documented one.
- In the only documented deployment (meta `docker-compose.yml`), api and worker are separate services. Neither sets `network_mode`, so each gets its own loopback, and 127.0.0.1:9090 does not collide. The "single-host" comment at meta `docker-compose.yml:262` means one host running separate containers. The Dockerfile sets `VIZRA_METRICS_ADDR=127.0.0.1:9090` per container (`Dockerfile:214-215`). A worker whose listener fails inside its own container gets connection refused, and the probe fails as it should (control A).
- The meta compose worker still probes with `vizra version` (`docker-compose.yml:289-291`, board item 2k), so `healthcheck worker` is not yet wired into any shipped topology.
- The core README's "Getting started" is a developer loop: build, `make ci`, `doctor`. It never tells anyone to run `vizra-api` and `vizra-worker` together. `grep` over core `README.md`/`AGENTS.md`, meta `README.md`, `docs/META_REPO.md`, `docs/quality/COMMANDS.md` and `docs/adr/` found no bare-metal, systemd or one-namespace instructions.
- The sweep's statement that "in the README flow, api and worker run on one host from one `.env`" is therefore **not supported by the README**. The collision needs an undocumented layout: both binaries on one host (or `network_mode: host`/`service:`), started from the shared template.

### Severity: MINOR, not MAJOR
The sentinel defines MAJOR as "a documented workflow fails or misleads". No documented workflow fails here. The defect is still real and latent. The probe's AGENTS.md invariant ("cannot pass while the service it probes is broken") does not hold in a plausible layout the template makes easy. The api's metrics listener answers every path. A worker that cannot bind its readiness listener keeps running silently. These are worth fixing through B4 (the probe checks the body). The severity should go back up to MAJOR if bare-metal or systemd install docs arrive, or if the compose topology ever shares a namespace.

```
FINDING S-0011: vizra healthcheck worker exits 0 against the api's metrics listener when both share one namespace
Severity:    MINOR (sentinel scale; was MAJOR)
Confidence:  high
Affected:
  repo:      vizra-core
  files:     internal/healthcheck/healthcheck.go:309-316, cmd/api/main.go:146-148, cmd/worker/main.go:92-104, .env.example:25, internal/config/keys.go:45
  requirements: none yet — propose under VZ-OPS (probe honesty)
Observed:  3/3 exit 0 with no worker, a colliding worker, or a killed worker; controls behave correctly.
Failure:   in an undocumented one-namespace layout the worker probe passes with no worker, and a worker whose listener lost the bind runs with no readiness endpoint.
Perspective: operator
Recommendation: the probe requires a JSON body with a known status; the api metrics server serves /metrics only; the worker exits non-zero when its listener cannot bind; the template documents that api and worker metrics addresses must differ on one host.
Acceptance criteria: with the api on VIZRA_METRICS_ADDR and no worker, `vizra healthcheck worker` against that address exits 1; a worker that cannot bind its listener exits non-zero or is reported not ready.
Tests:     healthcheck unit test: a 200 text/plain body is NOT ready; an integration test that starts the api and probes `worker` on its metrics address expects exit 1.
Cross-repo implications: core: probe, api metrics mux, worker bind | user: none | search: none | meta: 2k probe swap should land after the body check
Challenge: compose isolates namespaces, so no supported deployment is affected today.
```

---

## S-0012: after the cache recovers, readiness stays `degraded` until a setup route is called

### Reproduction (3 of 3, plus a re-run of run 1)
The script (`s12.sh`, recorded here) does the following on each run. It stops `spotv-cache` and calls `GET /api/v1/setup/claim-status` once during the outage. It starts the cache and waits for `PONG`. It then reads `/readyz` at +15 s, sends non-setup traffic, and reads again at +25 s and +35 s. Finally it calls `claim-status` once and reads again. Each read happens at least 3 s after the previous action, because `/readyz` is cached for 2 s (`internal/httpapi/server.go:137`, `newReadinessCache(2*time.Second, …)`).

| Run | During the outage | +15 s after PONG | Non-setup traffic (`/healthz` 200, `/version` 200, `/schemaz` 200, `/readyz` ×2 200, `/api/v1/photos` 403, `/setup/claim` 403) | +25 s | +35 s | One `claim-status` (200), then +3 s |
|---|---|---|---|---|---|---|
| 1 | (read inside the 2 s cache TTL, discarded) | degraded, "rate limiting is running on the in-process fallback" | sent | degraded | degraded | (read inside the TTL, discarded) |
| 2 | degraded, "cache unreachable; rate limits are per-process only" | **degraded, "…in-process fallback"** | sent | **degraded** | **degraded** | **ok** |
| 3 | the same | **degraded** | sent | **degraded** | **degraded** | **ok** |
| 1b (re-run) | the same | **degraded** | sent | **degraded** | **degraded** | **ok** |

### Does anything else clear it?
From the code: only `FallbackLimiter.Allow` clears the flag, when a cache decision succeeds (`internal/cache/ratelimit.go:98`). The only callers of `Allow` are in `internal/httpapi/setup_limits.go` (lines 84, 106, 110, 157), used by `GET /api/v1/setup/claim-status` and `POST /api/v1/setup/claim-owner`. `/readyz` PINGs the cache (`probes.go:180`), and the ping succeeds after recovery, but the stale `Degraded()` branch then overrides it (`probes.go:184-187`). Observed: none of the probes, the unclaimed guard (403) or the post-claim 404 cleared it. Restarting the api clears it, because the flag starts false when a cache client exists. **Only a setup-route request or an api restart clears it.**

### Severity: MINOR, not MAJOR
The detail text is false after recovery, and an alert on `degraded` would keep firing. That is misleading. But nothing downstream acts on it:
- `vizra healthcheck api` exits 0 on `degraded` by design (AGENTS.md table), so rotation and compose gating do not change.
- The next rate-limit decision uses the cache again, so no protection is lost.
- `vizra doctor` makes its own PING and reports the cache correctly.

The flag is also set only when a setup request arrives *during* the outage. In short: a stale status word, no failed workflow, and a one-line reproducer. That is MINOR under the sentinel scale ("friction"). It becomes more visible once M1-B routes consult the limiter. Those routes will also clear the flag often, so it is not self-worsening.

```
FINDING S-0012: /readyz keeps a stale limiter "degraded" after the cache recovers
Severity:    MINOR (sentinel scale; was MAJOR)
Confidence:  high
Affected:
  repo:      vizra-core
  files:     internal/httpapi/probes.go:178-189, internal/cache/ratelimit.go:55-59,93-98, internal/httpapi/setup_limits.go:84,106,110,157
  requirements: none yet — readiness semantics under ADR-002 § Probes
Observed:  3/3 degraded at +15/+25/+35 s after PONG, through non-setup traffic; one claim-status → ok.
Failure:   readiness reports a condition that ended; the detail text is false.
Perspective: operator
Recommendation: a successful readiness PING clears the fallback flag (or Degraded() carries a TTL).
Acceptance criteria: outage + one setup request + recovery → /readyz ok within one readiness TTL, with no setup traffic.
Tests:     integration: stop the cache, call claim-status, restart the cache, poll /readyz without setup traffic, expect ok.
Cross-repo implications: core only | user: none | search: none | meta: none
Challenge: an operator alerting on `degraded` treats it as an incident signal; a stuck one costs a page for a healthy system.
```

---

## S-0013: the README's getting-started does not boot

### Following the README literally (`cp .env.example .env`, `make build`, `./bin/vizra doctor`), with a clean `env -i PATH=/usr/bin:/bin HOME=…`

| Step | Output | Exit |
|---|---|---|
| `./bin/vizra doctor` (as the README says) | `FAIL config: DATABASE_URL must be set` · `2 check(s): 1 failed, 1 not run.` | 1 |
| `./bin/vizra doctor --env .env` (not in the README) | `FAIL config: DATABASE_URL must be a postgres:// or postgresql:// DSN` | 1 |
| `.env` sourced, `./bin/vizra-api` | `vizra-api refused to start. … DATABASE_URL: must be a postgres:// or postgresql:// DSN` | 1 |
| `.env` sourced, `./bin/vizra claim-token` | the same refusal | 1 |
| `./bin/vizra migrate --env .env` | `flag provided but not defined: -env` (migrate has no `--env`) | 1 |

No binary reads `.env` on its own. A grep for `".env"`, `godotenv` and `dotenv` in non-test Go found nothing, and the Makefile does not include `.env`. The template's `DATABASE_URL=CHANGE-ME-generate-with-openssl-rand-base64-32` (`.env.example:32`) is not a DSN. The file header's "Generate real ones: openssl rand -base64 32" (`.env.example:12`) cannot produce one. `--env` does not appear anywhere in the README.

### Does `TestTemplateBootsInDevelopment` really substitute a DSN? Yes, demonstrated.
`internal/config/template_test.go:89-95` sets `env["DATABASE_URL"] = "postgres://vizra:vizra@127.0.0.1:5432/vizra?sslmode=disable"` before `CheckEnv`. The line dates from the M0 foundation commit `415a6d1`.
- As shipped: `go test -count=1 -run TestTemplateBootsInDevelopment ./internal/config/` → `--- PASS`.
- Mutation (only that line deleted, so the test checks the template as shipped): `--- FAIL … template_test.go:92: .env.example does not boot in development mode: configuration is invalid (1 problem(s))`.
- Restored with `git checkout`, then green again (`ok … 0.430s`); `git status` clean.

The test's name and comment ("The template as shipped must boot in development") claim more than it checks. It is a false-positive CI signal.

### Severity: MAJOR stands
A step of the documented getting-started path fails with the file the README calls "development defaults". A CI test asserts the opposite and passes only by substituting its own value, which is a false-positive test of the kind AGENTS.md tells reviewers to hunt. Mitigation, for the record: `make ci` and `make test-integration` (the rest of W-DEV-1) do not depend on `.env`, and doctor's FAIL line names the cause. That keeps this below BLOCKER, but it does not make it friction.

```
FINDING S-0013: .env.example does not boot, and the test named for it substitutes a DSN
Severity:    MAJOR (sentinel scale; unchanged)
Confidence:  high
Affected:
  repo:      vizra-core
  files:     README.md:34-39, .env.example:12,32, internal/config/template_test.go:89-95
  requirements: VZ-FOUND-006 (configuration template)
Observed:  literal README steps exit 1; the test's substitution line removed → FAIL.
Failure:   a new contributor's first doctor run fails with the "development defaults"; CI says the template boots.
Perspective: developer, operator
Recommendation: ship a development DSN matching the README's docker run line (production already refuses published values); make the test check the template unmodified; README says `doctor --env .env` or exports the file; give the DSN placeholder its own hint.
Acceptance criteria: with the README's containers up, `cp .env.example .env && ./bin/vizra doctor --env .env` reaches the database check; TestTemplateBootsInDevelopment has no substitution and passes; a mutation that breaks the template DSN turns it red.
Tests:     internal/config/template_test.go (no substitution); a README-step smoke test is optional.
Cross-repo implications: core only | meta: none
Challenge: doctor failing without a database is "honest"; but the failure here is a malformed template value, not a missing service.
```

---

## S-0014: the claim URL leads nowhere

### Reproduction
On a migrated, unclaimed database with the api from `op.env`:
- `curl …/api/v1/setup/claim-status` → `{"claimed":false}`.
- `./bin/vizra claim-token` → exit 0. It prints 65 bytes (the token) on stdout, and on stderr: `It works once. Paste it into the claim page at http://localhost:47080/setup/claim`.
- `GET /setup/claim` on the api → **403** `{"error":{"code":"instance_unclaimed",…}}` (also with `Accept: text/html`, `application/json`).
- vizra-user `783483f`: `git ls-tree` shows `app/globals.css`, `app/health/page.tsx`, `app/layout.tsx` and `app/page.tsx` only. There is no `pages/`, `src/` or `middleware`, and `next.config.ts` has no rewrites. `lib/api/generated.ts` has no claim operation. The Next App Router therefore has no `/setup/claim` route. The user app was not started (heavily loaded host). The file tree settles the question for the App Router.
- In meta, the Caddyfile that would route `/setup/claim` is generated by `vizra setup`, which does not exist (`docker-compose.yml` caddy volume comment). No shipped route reaches a claim page.
- The only working path: `POST /api/v1/setup/claim-owner` with `Content-Type: application/json` and `{token, username, email, password}`, using inert values → **201** `{"username":"spotcheckowner","role":"owner"}`, then `claim-status` → `{"claimed":true}`. After the claim, `GET /setup/claim` → **404** `not_found`.

### Is there ANY documented way for an operator to complete the claim? No operator-facing one.
- The core README (`README.md:104-108`), the CLI text (`cmd/vizra/claimtoken.go:68-71`) and meta `docs/META_REPO.md:277` all say to use `/setup/claim`.
- `POST /api/v1/setup/claim-owner` is described only in `api/openapi.yaml:187-240`. Its description does allow non-browser clients ("absence of both is allowed so non-browser clients work"), so a determined operator could build the request from the contract. Core `AGENTS.md:406-407` mentions claim-owner only for rate-limit ceilings, not as a how-to. No README, runbook or CLI message gives the curl form.
- Context, not mitigation: the OpenAPI says no session is set ("a client must send the new owner to the sign-in page"), and no sign-in page exists yet either. The meta design docs (`docs/design/figma/FIRST-SLICE-auth-system.md` §2.1) specify the page as future M1 work.

### Severity: MAJOR stands
The CLI actively sends the operator to a URL that returns 403 before the claim and 404 after it. The README describes the page in the present tense. Completing the documented first-run step needs knowledge that exists only in the API contract. That is "a documented workflow fails". It is not BLOCKER only because no install path is runnable end to end yet (no published images, and no `vizra setup`), so no real operator can reach this step today.

```
FINDING S-0014: README and `vizra claim-token` direct the operator to a /setup/claim page that does not exist
Severity:    MAJOR (sentinel scale; unchanged)
Confidence:  high
Affected:
  repo:      vizra-core (docs + CLI text); vizra-user (the page)
  files:     vizra-core README.md:104-113, cmd/vizra/claimtoken.go:68-71, api/openapi.yaml:187-240; vizra-user app/ (no setup route); meta docs/META_REPO.md:277
  requirements: VZ-INSTALL-003, VZ-AUTH-004
Observed:  printed URL → 403 unclaimed / 404 claimed; user app has no route; raw POST claim-owner → 201.
Failure:   the operator cannot finish the first-run claim from any operator document.
Perspective: operator, instance-admin
Recommendation: until the page ships, the README and the CLI stderr give the curl redemption (Content-Type, four fields, 201/400/403/409/429 meanings) and say the page is coming; vizra-user builds the page under the M1 UI slice.
Acceptance criteria: following only the README and CLI output, an operator on a fresh instance reaches claim-status {"claimed":true}; once the page ships, GET <origin>/setup/claim serves the form.
Tests:     core: a CLI golden test for the claim-token stderr text; user: e2e for /setup/claim when built.
Cross-repo implications: core: README + CLI text | user: the page | search: none | meta: META_REPO.md:277 wording
Challenge: the page is a scheduled M1 slice and the install path is not runnable yet; the doc is merely ahead of the code.
```

---

## Not run, and why
- **Starting vizra-user in a browser at `/setup/claim`.** The host load average was about 250, and `npm ci` plus `next build` would have taken a long time. The file tree at `783483f`, the lack of middleware and rewrites, and the lack of a generated claim operation settle the absence for the App Router.
- **The meta compose topology.** No images are published at these SHAs, and `vizra setup` does not exist (the same as the sweep). The one-namespace judgement for S-0011 rests on reading `docker-compose.yml`, which sets no `network_mode`.

## Hygiene
- The api and both workers were stopped (pids 37531, 37848, 38574 confirmed gone). `spotv-pg` and `spotv-cache` were removed with `docker rm -f -v`, and ports 47080, 47090, 47091 and 47379 were confirmed free.
- The minted claim token went to a scratch file, which was deleted. The api log mentions only the `claim-token` command, never a token.
- The scratch directory `vzv-core-spotcheck-*` was deleted by exact path. Nothing outside it was touched, and no integration suite ran, so no `vizra-*` temp directories were created.
