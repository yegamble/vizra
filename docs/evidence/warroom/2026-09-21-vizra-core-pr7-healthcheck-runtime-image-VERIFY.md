# Independent verification — vizra-core PR #7, `vizra healthcheck` + clean-base runtime image + image-scan lane

**Repo:** `yegamble/vizra-core` · **PR:** https://github.com/yegamble/vizra-core/pull/7
**Head SHA verified:** `68292851e768dd77516c6e49b7831507e4757919`
**Branch:** `feat/m0-healthcheck-runtime-image` · 1 commit · 57 files · +5154 / −21
**Base:** `4a80a1e3f36b8001c2954d0568bea29268e739fe` (= current `main` tip; main has not moved)
**Merge commit CI tested:** `3e30533a27c614a51baa4e6c5035d27a162aafe9` (= the PR's current `merge_commit_sha`)
**Verifier:** independent — did not write this code, did not edit the branch, did not push.
**Date:** 2026-09-21

Head confirmed unmoved at the start and at the end of this verification
(`gh api repos/yegamble/vizra-core/pulls/7 --jq .head.sha`).

---

## Environment

| | |
|---|---|
| Host | darwin 25.5.0, arm64 (Apple silicon), 8 cores |
| Go | `go1.27.1 darwin/arm64` |
| Docker | Docker Desktop, linux/arm64 engine. **amd64 cannot be built here** (no emulation, disk at 96 %) |
| PostgreSQL | `postgres@sha256:86c951e05bf56c93d95d397747fb8820ac76cc3bedb78f43abd83eedbe3666ae` (the digest `build-test.yml:108` pins), container `vzv7pr7-pg`, port **55501** |
| Cache | `valkey/valkey@sha256:c123e3715db63d06d4ad6964884037aa0d5d4d703939b9929954112889708e1d`, container `vzv7pr7-cache`, port **63901** |
| Ports | Chosen to avoid the concurrent `core-m1-owner-claim` worktree's `vizra-m1a-pg18` (55438) and `vizra-m1a-valkey` (63799) — `docker ps` checked first. |
| Clones | Three fresh clones under my own `mktemp -d` scratch dirs (`vzv-core-pr7-*`); the builder's checkout was never touched. |
| Containers/images created | `vzv7pr7-pg`, `vzv7pr7-cache`, `vzv7pr7-runtime:verify`, `vzv7pr7-nouser:verify`, `vzv7pr7-nomedia:verify`, `vzv7pr7-base:verify` — all removed by exact name at the end. No global prune. |

---

## 1. The repo's documented CI entry point, from a clean clone at the SHA

```
$ make ci
…
make-integrity-guard: passed (8 gate target(s))
==> fixtures-verify
fixtures-verify: ok — 12 fixtures, 1791508 bytes, generator 1 (4ff582ba6959), toolchain go1.27.1
==> test-race
ok  github.com/yegamble/vizra-core/cmd/api           1.362s
ok  github.com/yegamble/vizra-core/cmd/vizra         1.575s
ok  github.com/yegamble/vizra-core/internal/authz    1.765s
ok  github.com/yegamble/vizra-core/internal/cache    2.081s
ok  github.com/yegamble/vizra-core/internal/config   2.237s
ok  github.com/yegamble/vizra-core/internal/doctor   2.428s
ok  github.com/yegamble/vizra-core/internal/fixtures 76.121s
ok  github.com/yegamble/vizra-core/internal/healthcheck 3.033s
ok  github.com/yegamble/vizra-core/internal/httpapi  2.010s
ok  github.com/yegamble/vizra-core/internal/jobs     5.006s
ok  github.com/yegamble/vizra-core/internal/obs      1.906s
ok  github.com/yegamble/vizra-core/internal/search   1.836s
ok  github.com/yegamble/vizra-core/internal/site     1.864s
ok  github.com/yegamble/vizra-core/scripts           6.714s
make ci: all lanes passed
EXIT=0
```

14 packages `ok`, **8** `[no test files]` (see FINDING 5), 0 FAIL.

Guards, run read-only by me:

```
$ bash scripts/ci-required-guard.sh        → EXIT 0   "ci-required-guard: passed (6 required check(s))"
$ bash scripts/make-integrity-guard.sh     → EXIT 0   "make-integrity-guard: passed (8 gate target(s))"
$ make config-template-check               → EXIT 0
```

### Per-package skip counts (measured with `-v`, which CI never uses)

| package | PASS | SKIP | FAIL |
|---|---|---|---|
| `internal/healthcheck` | 12 | **0** | 0 |
| `internal/jobs` | 30 | **0** | 0 |
| `scripts` (incl. `imagescan_test.go`) | 81 | **0** | 0 |
| `internal/integration` (`-tags=integration`) | 31 (+14 subtests) | **0** | 0 |

The builder's "31 tests, 0 skips" for `internal/integration` is confirmed. Note
that **CI cannot corroborate skip counts** — no lane runs `go test -v`, and a
non-verbose `go test` prints nothing for a skipped test. The counts above are my
own local `-v` runs, which is why they are recorded here.

`make test-integration` refuses rather than skips when the DB URL is absent
(`Makefile`: `echo "  FAIL  VIZRA_TEST_DATABASE_URL is not set. This lane is
BLOCKED, not passed."; exit 1`), and `mustEnv` in
`internal/integration/golden_test.go:47` calls `t.Fatalf`, not `t.Skip`. There
is no silent-skip path.

### Flake hunt (the 1-in-30 the brief warned about)

10 consecutive runs of the healthcheck integration suite, `-race -shuffle=on
-count=1`, **under deliberate CPU contention** (8 busy-loop processes pinned for
the duration):

```
RUN 1 EXIT=0   RUN 2 EXIT=0   RUN 3 EXIT=0   RUN 4 EXIT=0   RUN 5 EXIT=0
RUN 6 EXIT=0   RUN 7 EXIT=0   RUN 8 EXIT=0   RUN 9 EXIT=0   RUN 10 EXIT=0
FAIL / DATA RACE / panic: 0 occurrences
```

**10/10 clean.** No flake observed.

---

## 2. Acceptance bullet 1 — `vizra healthcheck` on REAL processes

All five integration tests run the **shipped binaries as separate processes**
(`exec.Command(.../vizra)`, `.../vizra-api`, `.../vizra-worker`) and read exit
codes. "PostgreSQL stopped" is a real TCP-level stop via a test-owned proxy.
My run, verbatim (abridged):

```
--- PASS: TestHealthcheckApiIsZeroWhenReadyAndNonZeroWhenPostgresStops (9.10s)
      healthy:          exit 0 — "ready — HTTP 200 ok (127.0.0.1:51363/readyz, 11ms)"
      proxy stopped:    exit 1 — "NOT READY — HTTP 503 unavailable (…, 1ms)"
--- PASS: TestHealthcheckApiIsNonZeroWhenTheListenerIsAbsent (0.01s)
      exit 1 — "NOT READY — dial: connect: connection refused"
--- PASS: TestHealthcheckWorkerIsZeroWhenTheLoopIsRunningAndNonZeroWhenPostgresStops (0.58s)
      exit 0 then exit 1 — "NOT READY — HTTP 503 unavailable"
--- PASS: TestHealthcheckWorkerIsNonZeroWhenTheClaimLoopStallsWhilePostgresIsFine (2.06s)
      loop cancelled, PostgreSQL proven still pingable, probe → exit 1,
      body claim_loop="stalled", database="ok"
--- PASS: TestHealthcheckUsageErrorsAreDistinctFromAVerdict (0.02s)
      exit 64 for both `nonsense` and `api --nosuchflag`
ok  github.com/yegamble/vizra-core/internal/integration  13.224s
```

Every acceptance case in the brief reproduced: **healthy → 0; PostgreSQL stopped
→ non-zero within the deadline; listener absent → non-zero; worker with DB
unreachable → non-zero; worker with the loop stalled past the bound → non-zero.**

### Adversarial probing (brief item a) — attacks I ran myself

| attack | result | verdict |
|---|---|---|
| api accepts the TCP connection then **never answers** (wedged handler) | `exit 1`, elapsed **2.003 s** — "the probe timed out before the service answered" | correct, and inside Docker's 3 s |
| listener with **backlog 0 that never accepts** | `exit 1`, elapsed **2.002 s** | correct |
| `HTTP_PROXY`/`http_proxy`/`HTTPS_PROXY`/`ALL_PROXY` pointed at a server that answers **200 to everything**, with nothing on the target port | `exit 1` — "dial: connect: connection refused" | **proxy cannot hijack the probe.** `probe()` builds its own `http.Transport` and leaves `Proxy` nil (`internal/healthcheck/healthcheck.go:294-299`), so `ProxyFromEnvironment` is never consulted |
| redirect (`301`) | `exit 1` (unit `TestANonSuccessStatusExitsNonZero`) — `CheckRedirect` returns `http.ErrUseLastResponse`, so the 3xx is the verdict | correct |
| `VIZRA_LISTEN_ADDR=":8080"` | dialled `127.0.0.1:8080` | correct |
| `"0.0.0.0:8080"` | dialled `127.0.0.1:8080` | correct |
| `"[::]:8080"` | dialled `127.0.0.1:8080` | correct |
| `"localhost:8080"` | dialled `localhost:8080` | correct |
| `"example.invalid:8080"` (hostname) | `exit 1` — "dial: lookup example.invalid: no such host" | correct |
| `"8080"` (no host) | `exit 64` — usage, not a verdict | correct |
| `"/run/vizra.sock"` (unix socket) | `exit 64` — "missing port in address" | correct: refuses rather than guessing |
| unset | falls back to the registry default `:8080` → `127.0.0.1:8080` | correct |
| an **unrelated process** answering `200` + HTML on the target port | `exit 0` — "ready — HTTP 200" | see FINDING 6 |
| `--timeout=30s` (above Docker's 3 s) | accepted; ran the full 30 s | see FINDING 7 |
| zombie/defunct children | `ENTRYPOINT ["/usr/bin/tini","--"]` is PID 1 in the runtime image, so healthcheck children are reaped | correct |

### Worker readiness — what records "progress", false red and false green

Read at `internal/jobs/health.go` and `internal/jobs/worker.go:196-240`. The
signal lives **in process memory** on the worker (`Health.sites`), served on the
worker's own metrics listener; nothing else can write it and, at the default
`VIZRA_METRICS_ADDR=127.0.0.1:9090` (`internal/config/keys.go:45`, also baked
into the image `ENV`), nothing off-loopback can read it. Confirmed in the built
image: `ENV=[… VIZRA_METRICS_ADDR=127.0.0.1:9090]`.

I wrote throwaway probes against the shipped package (deleted afterwards; the
clone's `git status` was clean after each):

* **Idle worker, empty queue → READY, not stalled.** `claim` returning no rows
  still calls `ClaimOK`, so an empty queue records progress every poll interval.
  No false-red restart loop. Measured: `ready=true … claim_loop:ok`.
* **Permanently saturated worker → READY indefinitely.** Measured:
  `ready=true status=ok … ClaimLoop:ok … Saturated:true`. See FINDING 4.
* **Clock source.** `h.now` is `time.Now` in production and the value is stored
  unmodified in `lastProgress`, so `now.Sub(p.lastProgress)` uses Go's
  **monotonic** reading; a wall-clock/NTP step cannot move the verdict, and Go's
  `CLOCK_MONOTONIC` does not advance across suspend, so a laptop sleep biases
  toward *healthy*, never toward a false stall. Correct by construction, but
  **not covered by a test**: my "wrong clock" mutation (below) is the check that
  is missing.
* **Probe-time ping is bounded**: `healthProbeTimeout = 1500ms`
  (`health.go:63`), applied with `context.WithTimeout` per site and cancelled
  immediately after (`health.go:241-243`). `TestTheHandlerBoundsAHangingPing`
  covers it and I saw it take exactly 1.51 s. The ping is `pgxpool.Ping`, which
  **acquires from the pool** rather than always dialling anew — at a 15 s Docker
  interval an idle pool may have to re-dial, which is one connection per
  container per interval at worst. Bounded and not a `max_connections` hazard at
  this scale.

### Secrets / private data in probe output

Probe stderr/stdout carries only the target, the HTTP code and a `sanitiseStatus`'d
status word (`healthcheck.go:323-333`, 32 chars, `[A-Za-z_-]` only). `classify`
deliberately unwraps `*url.Error` so the full request URL is not echoed.

I tested the worker `/readyz` body with a DSN carrying a password:

```
DSN under test: postgres://vizrauser:SuperSecret123@127.0.0.1:1/vizra?sslmode=disable
HTTP 503
{"ready":false,"status":"unavailable",…,"database_detail":
 "failed to connect to `user=vizrauser database=vizra`: 127.0.0.1:1 (127.0.0.1):
  dial error: dial tcp 127.0.0.1:1: connect: connection refused", …}
```

**The password does not appear.** Username, database name and host:port do —
acceptable on a loopback-only listener (see FINDING 6's sibling note).

---

## 3. Acceptance bullet 2 — the runtime image

I could not build amd64 (arm64 host, no emulation, disk at 96 %). I did two
things instead: judged the amd64 assertions from the CI job log on this SHA, and
**built and exercised the linux/arm64 image locally**.

### Local arm64 image, built from the clean clone at this SHA

```
$ docker build --platform linux/arm64 --target runtime -t vzv7pr7-runtime:verify .   → EXIT 0
$ docker image inspect vzv7pr7-runtime:verify --format '{{.Size}}'
232051323 bytes (221 MiB), linux/arm64
USER=10001:10001   WORKDIR=(none, i.e. /)
ENTRYPOINT=["/usr/bin/tini","--"]
CMD=["/usr/local/bin/vizra-api"]
HEALTHCHECK={"Test":["CMD","/usr/local/bin/vizra","healthcheck","api"],
             "Interval":15s,"Timeout":3s,"StartPeriod":20s,"Retries":3}
ENV=[… VIZRA_LISTEN_ADDR=:8080  VIZRA_METRICS_ADDR=127.0.0.1:9090]
EXPOSED={"8080/tcp":{}}
```

The builder reported **232 051 189 bytes**; I measured **232 051 323 bytes** — a
134-byte difference explained by the `RELEASE`/`COMMIT` ldflags (they passed
build args, I did not). Same 221 MiB. Claim accurate.

Every CI image assertion, re-run by me on the arm64 image:

```
media dir write+read as the default user:  rc=0, out="vizra-media-probe"
id:                                        uid=10001(vizra) gid=10001(vizra)
ls -ld /var/lib/vizra/media:               drwxr-x--- 2 vizra vizra   (0750, uid 10001)  ✅ F5
binaries:                                  ok vizra / ok vizra-api / ok vizra-worker
vizra healthcheck --help:                  exit 0, prints usage incl. "Exit codes"
vizra healthcheck api (nothing listening):  exit 1  ✅ F3 — the probe fails inside the image
vips --version:                            vips-8.18.6      vips -l: 333 lines
toolchain denylist (18 names, gcc cc g++ cpp ld as ar make cmake meson ninja
  pkg-config pkgconf curl wget xz go git):  NONE present
-dev packages:                             (none)
/src:                                      absent
/usr/local/bin contents:                   vips vipsedit vipsheader vipsthumbnail
                                           vizra vizra-api vizra-worker   (nothing else)
```

### Runtime stage really copies nothing but binaries and required libraries

Read at `Dockerfile:160-195`. Every `COPY` into `runtime`:
`vipsmeta:/out/runtime-packages.txt` (deleted at line 169), `vips:/usr/local/lib/`,
`vips:/usr/local/bin/`, three build-metadata files, `LICENSE`, `NOTICE`, and the
three Go binaries from `build`. Nothing from the Go toolchain reaches runtime.
The shared-library list is **ldd-derived, not hand-typed** (`Dockerfile:86-101`),
with `test -s` on every intermediate so an empty derivation fails the build.
`|| true` appears nowhere in the Dockerfile — only inside the comment that
explains its removal (lines 142, 145). `find … -name '*.a' -delete` / `'*.la'`
/ `rm -rf …/pkgconfig` then `ldconfig; vips --version; vips -l > /dev/null` is a
build-time proof the copied libraries load.

### Digest pins resolve against the real registry

`docker buildx imagetools inspect` (read-only) on each:

| ref | exists | resolves to |
|---|---|---|
| `golang@sha256:433790e5…` | yes | OCI index, `org.opencontainers.image.version: 1.27.1-trixie` |
| `debian@sha256:a99cfc51…` | yes | OCI index, `org.opencontainers.image.version: trixie-slim` (Debian 13-slim) |
| `aquasec/trivy@sha256:be1190af…` | yes | amd64 child `sha256:85e87be1…` — the digest `image-scan.yml:86` pins |

The `vips` stage and the `runtime` stage use the **same** debian digest, which is
what makes the `ldd`-derived package list valid. Confirmed in both the Dockerfile
and the CI log.

### CI (amd64), from the `docker-build` job log on this SHA

`platforms: linux/amd64`, `runs-on: ubuntu-24.04`, conclusion **success** (2m54s).
Every assertion genuinely executed against a running container:

```
  ok   golang@sha256:433790e5…  /  debian@sha256:a99cfc51…  (x2)  — every FROM digest-pinned
  image uid: 10001
  wrote and read back /var/lib/vizra/media as vizra
  drwxr-x--- 2 vizra vizra 4096 … /var/lib/vizra/media
  ok   /usr/local/bin/vizra  /  vizra-api  /  vizra-worker
  vizra healthcheck api: NOT READY — dial: connect: connection refused (127.0.0.1:8080/readyz, 0s)
    ok   healthcheck exits 1 with no listener
  the runtime loader list matches the recorded one (79 entries)
  no excluded codec is present
  checking for: gcc cc g++ … git    →  no build tooling on PATH
  no -dev packages installed   /   no /src
  #8 CACHED — a Go-only change reused the libvips layers
vizra-core:ci — 149109021 bytes (142 MiB), linux/amd64
```

**142 MiB amd64 confirmed** — exactly the PR body's number.

---

## 4. Acceptance bullet 3 — the image-scan lane

I read `scripts/image-scan-verdict.py` in full and enumerated its exits: **17
distinct refusal conditions all reach `die()` → exit 3**; exit 1 only for
findings at or above `--fail-on`; exit 0 only after the whole gate chain. There
is no bare `except`, no `sys.exit(0)`, and no path that converts an exception
into a pass. `TestEveryImageScanFixtureIsExercised` additionally fails if a
fixture directory exists that no test reads, so a check cannot be dropped by
orphaning its fixture.

### The lane is RED on this SHA, and the red is a TRUE signal

Verified from the CI log **and** from the published artifact, which I downloaded
and re-counted independently:

| builder claim | verdict | my evidence |
|---|---|---|
| first-ever run | **TRUE** | `gh run list --workflow=image-scan.yml` returns exactly one row — this PR. Never ran on `main`. |
| 0 CRITICAL / 48 HIGH | **TRUE** | verdict printed `HIGH: 48`, no CRITICAL line; JSON re-count agrees (`UNKNOWN 3, LOW 72, MEDIUM 52, HIGH 48, TOTAL 175`) |
| none with a `FixedVersion` | **TRUE** | 0 of 48 HIGH — in fact 0 of all 175 |
| 13 distinct CVEs in Debian 13 base packages | **TRUE** | exactly 13 IDs, all in the `os-pkgs` / `debian 13.7` result. The three Go binaries report **0** vulnerabilities. |
| no threshold weakening, no ignore file | **TRUE** | scanner collects `--severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL --ignore-unfixed=false`; verdict `--fail-on HIGH,CRITICAL`. `find . -iname '*trivyignore*'` → nothing. The only mentions of `.trivyignore.yaml` in the diff are prose describing what a *future owner-reviewed promotion PR* would need. `main` has **no image scan at all**, so nothing was weakened — this is net-new coverage. |
| lane not in the required manifest | **TRUE** | `.github/required-checks.txt` active lines are exactly `append-only build-test cache-matrix fixtures govulncheck docker-build`; `FLOOR_LANES` in `scripts/ci-required-guard.py:116` is the identical six and **was not edited**. |

The verdict exited **1** (findings), not 3 — the correct code. The lane is red
for real, unfixed, upstream CVEs.

**Are these regressions this PR introduced?** No. I scanned the **bare pinned
Debian base** (`debian@sha256:a99cfc51…`, the same digest `main`'s Dockerfile
resolves through its `vips` stage) with the same pinned Trivy:

```
HIGH/CRITICAL in the BARE PINNED BASE: 43 findings, 8 distinct CVEs, 0 with a FixedVersion
CVE-2025-69720, CVE-2026-16742, CVE-2026-54369, CVE-2026-76642,
CVE-2026-78408, CVE-2026-78409, CVE-2026-78410, CVE-2026-9538
packages: bsdutils libacl1 libblkid1 liblastlog2-2 libmount1 libsmartcols1
          libsystemd0 libtinfo6 libudev1 libuuid1 login mount ncurses-base
          ncurses-bin perl-base util-linux
```

**8 of the 13 are demonstrably in the base image `main` already ships**; the
remaining 5 (CVE-2026-36849, -52490, -66046, -76956, -76957) sit in `libtiff6`,
`libexpat1` and friends — packages `main`'s `FROM vips` runtime stage also
carried, in `-dev` form as well. I did not build `main`'s 899 MiB image, so I
record the last five as **UNVERIFIED-but-highly-likely pre-existing**, and the
first eight as verified pre-existing. Nothing in the PR contradicts the chair's
standing position: no threshold was weakened and no ignore file was added.

---

## 5. Demonstrations I reproduced myself

Harness: my own script, in a throwaway clone. It records the target file's
sha256 before and after, **aborts if the digest did not change**, runs the check,
restores with `git checkout --`, and **aborts if the restored digest is not
byte-identical**. Every line below was produced by that harness.

### The builder's six

| # | mutation | RED | GREEN | verdict |
|---|---|---|---|---|
| **M1** | `healthcheck.Run` returns `ExitReady` unconditionally | exit 1 — 7 unit tests by name (`TestAReadyAnswerExitsZero`, `TestADegradedButServingApiExitsZeroAndSaysSo`, `TestANonSuccessStatusExitsNonZero`, `TestConnectionRefusedExitsNonZero`, `TestATimeoutIsEnforcedAndTheProbeNeverRetries`, `TestUsageErrorsDoNotCollideWithDockersReservedCode`, `TestHelpExitsZeroAndNamesBothTargets`, `TestTheCallersContextIsPropagated`) | exit 0 | **reproduced** |
| **M2** | staleness bound never applied (`case false:`) | exit 1 — `TestAClaimLoopStalledPastTheBoundIsNotReady`: "a claim loop last alive 15.001s ago reported READY against a 15s bound" | exit 0 | **reproduced** |
| **M3** | PostgreSQL assumed reachable instead of pinged at probe time | exit 1 (`declared and not used: pinger` — the ping is structurally load-bearing) | exit 0 | **reproduced** |
| **M4** | unrecognised OS no longer refuses | exit 1 — `TestImageScanVerdictRefusesEveryVacuousPass/no-os-detected`: "exited 0, want 3" | exit 0 | **reproduced** |
| **M5** | scanner's own exit code no longer judged | exit 1 — `…/scanner-error` and `…/scanner-crashed`, both "exited 0, want 3" | exit 0 | **reproduced** |
| **M6** | runtime image no longer declares `/var/lib/vizra/media` | image rebuilt; assertion `rc=2 out="sh: 1: cannot create /var/lib/vizra/media/probe.txt: Directory nonexistent"` | unmutated image writes+reads `vizra-media-probe` | **reproduced** |

All six restored byte-identical. **Every demonstration the PR claims, I reproduced.**

### Six mutations of my own

| # | mutation | result |
|---|---|---|
| **V1** | probe **ignores the HTTP status** (`if false` instead of `code < 200 \|\| code > 299`) | **RED** — `TestANonSuccessStatusExitsNonZero`: 503/500/404/301 all "gave exit 0, want 1" |
| **V2** | staleness compared with the **wrong clock** | **NOT CAUGHT** — see FINDING 8. Production behaviour is correct by construction (monotonic), but no test pins the clock source. |
| **V3** | worker health handler **always answers 200** | **RED** — `TestTheHandlerAnswers503WhenTheWorkerIsNotReady` and `TestTheHandlerBoundsAHangingPing`, both "HTTP 200, want 503" |
| **V4** | Dockerfile **`USER` dropped** | image rebuilt → `image uid: 0` → the non-root assertion (`docker-build.yml:126-130`) goes **RED**. Worth noting: the *media* assertion still passes as root, so it is not the control for `USER` — the uid assertion is, and it exists. |
| **V5** | base image **digest replaced by a tag** (`FROM debian:13-slim AS runtime`) | **CAUGHT** — `docker-build.yml:43-56` prints `::error::FROM debian:13-slim is not digest-pinned` and exits 1 |
| **V6** | scan step given a **non-existent image ref** | **CAUGHT** — real pinned Trivy exited **1**; the verdict script printed `THE SCANNER FAILED: trivy exited 1 … This is exit 3: THE LANE DID NOT PRODUCE A VALID SCAN. It is NOT a statement that the image is clean.` |

---

## 6. CI-guard class (brief item f)

* `scripts/ci-required-guard.sh` and `scripts/ci-required-guard.py` — **zero diff**
  at this SHA. `scripts/make-integrity-guard.*` — not in the diffstat at all.
* `FLOOR_LANES` unchanged: `["append-only","build-test","cache-matrix","fixtures","govulncheck","docker-build"]`.
* `.github/required-checks.txt` changes are **+20 lines, −0**, all comment-only
  and all after the last check name. No check name removed, renamed or
  commented out. Manifest and `FLOOR_LANES` agree.
* Both guards exit 0 when I run them.
* `docker-build.yml` and `image-scan.yml` **invoke no `make` at all**, so no
  integrity anchor is required — and the guard says so itself in its own log:
  `ok  floor lane 'docker-build' invokes no `make`, so it needs no make-integrity anchor`.
  The denylist was moved to `scripts/runtime-toolchain-denylist.txt` precisely so
  the bare token `make` on line 23 does not trip the guard's fail-closed ANCHOR
  heuristic — a correct response to the constraint, not a dodge.
* `continue-on-error:` — **zero** in both new/changed workflows. `if:` — zero in
  `docker-build.yml`; exactly one in `image-scan.yml` (`if: always()` on the
  report-upload step, which *widens* execution and carries
  `if-no-files-found: error`).
* The new tests run in **required lanes**: `internal/healthcheck`,
  `internal/jobs` and `scripts` in `build-test`'s `go test -race ./...` (run
  twice, once via `make ci` and once **directly without make**);
  `internal/integration` in `build-test`'s `make test-integration` +
  `make test-integration-shuffle` against real PostgreSQL 18 + Valkey, and again
  in both `cache-matrix` legs.
* Denylist cannot pass vacuously: I replayed the extraction
  (`grep -v '^#' … | grep -v '^$' | tr '\n' ' '` under `set -euo pipefail`) with
  an empty file, a missing file and a comments-only file — **all three exit 1**
  and kill the step.

---

## 7. Frozen paths and config keys (brief item g)

```
$ git diff --stat origin/main..68292851 -- migrations/ api/ sqlcgen/
(no output)
$ git diff --stat 4a80a1e..68292851 -- migrations/manifest.sha256
(no output)
```

**Byte-identical to main.** The manifest (`migrations/manifest.sha256`, 4
migration pairs) is unchanged; `append-only` passed on this SHA with
`0 migration file hash(es) added, none removed or changed`.

`internal/config/keys.go` gains exactly one function — `DefaultFor`, a read-only
lookup over the existing `Registry` — and **no Registry entry**. The diff hunk
starts after the closing brace of `RetiredKeys`. `make config-template-check`
passes. **No new operator-facing key.** `Options.HealthStaleAfter` is a library
field documented as "NOT an operator-facing configuration key" and is set only
from `HealthStaleBound` in production and from tests.

---

## 8. CI on `6829285` (brief item i)

11 check runs, all `status: completed`. **Nothing skipped, cancelled, timed_out,
neutral or pending.**

| lane | conclusion | duration |
|---|---|---|
| `ci-required` | **success** | 11m25s |
| `append-only` | success | 6s |
| `build-test` | success | 11m4s |
| `cache-matrix` (+ both legs) | success | 4s (legs 4m59s / 5m4s) |
| `fixtures` | success | 2m12s |
| `govulncheck` | success | 35s |
| `docker-build` | success | 2m54s |
| `image-scan` | **failure** (by design, not required) | 3m17s |
| GitGuardian Security Checks | success | 1s |

`ci-required`'s own collection step, verbatim:

```
required checks (6): append-only build-test cache-matrix fixtures govulncheck docker-build
head sha: 68292851e768dd77516c6e49b7831507e4757919
  SUCCESS   append-only
  SUCCESS   build-test
  SUCCESS   cache-matrix
  SUCCESS   fixtures
  SUCCESS   govulncheck
  SUCCESS   docker-build
all 6 required check(s) succeeded
```

Its shell treats *everything* other than `success` as failure, including
never-run: `# Everything else — failure, cancelled, timed_out, skipped, neutral,
action_required, stale — is NOT a pass.` **The manifest it enforced matches the
jobs that actually ran** — six names, six check runs, six successes. No lane is
listed-but-unexecuted.

**Provenance.** Every run is `event: pull_request`, so every lane tested the
merge commit. The repo prints it:

```
provenance
  ref:                              refs/pull/7/merge
  TESTED TREE (git rev-parse HEAD):  3e30533a27c614a51baa4e6c5035d27a162aafe9
  base actually merged in (HEAD^1):  4a80a1e3f36b8001c2954d0568bea29268e739fe
  head actually merged in (HEAD^2):  68292851e768dd77516c6e49b7831507e4757919
  checked: HEAD^2 == the PR head SHA, so this really is the merge ref.
```

The tested merge SHA equals the PR's current `merge_commit_sha`; the base equals
the current `main` tip. **The tree CI tested is current.**

---

## 9. Truthfulness audit (brief item h)

| claim | where | verdict |
|---|---|---|
| "142 MiB amd64 from CI" | PR body | **TRUE** — `149109021 bytes (142 MiB), linux/amd64` in the `docker-build` log |
| "899 → 221 MiB is arm64-local only" | PR body, evidence README | **TRUE and correctly caveated.** I measured 221 MiB arm64 myself. The README states the platform caveat in bold before the number. |
| "nothing is gated on these probes end to end yet" | PR body "What did NOT run" | **TRUE.** The meta repo has no compose file on `main`; meta PR #4 (which would introduce one) is still `OPEN`, `mergedAt: null`. No container gates on these probes anywhere. |
| "`image-scan` has never executed anywhere" | PR body | **TRUE** |
| "no `\|\| true` anywhere in the `Dockerfile`" | `AGENTS.md`, PR body | **TRUE of the Dockerfile** — but see FINDING 1, the new *workflow* has three |
| "16 fixtures under `scripts/testdata/imagescan/`" | `AGENTS.md` | **TRUE** — 16 directories |
| "No `CMD-SHELL`, no `/dev/tcp`, no `curl`" | `AGENTS.md` | **TRUE** — `HEALTHCHECK` is exec-form `["CMD","/usr/local/bin/vizra","healthcheck","api"]`; I confirmed it in the built image's config |
| "The staleness bound is 15s (5 × poll, floor 15s)" | `AGENTS.md` | **TRUE** — `HealthStaleBound`, `health.go:78-85` |
| "`degraded` → 0 because /readyz 503s on PostgreSQL only per ADR-002" | `AGENTS.md`, package doc | **TRUE and documented in three places**; `TestADegradedButServingApiExitsZeroAndSaysSo` pins it, and the status word is printed rather than flattened |
| "`api/` and `migrations/` byte-identical to main" | PR body | **TRUE** |
| "31 tests, 0 skips" (`internal/integration`) | PR body | **TRUE** — I measured 31 PASS / 0 SKIP with `-v` |
| "`make ci` → 14 packages ok, **6** `[no test files]`" | PR body evidence table | **FALSE in the second number** — 14 ok is right, `[no test files]` is **8**. See FINDING 5. |
| "published as the `trivy-image-6829285` artifact" | PR body | **FALSE** — the artifact is `trivy-image-3e30533a27c614a51baa4e6c5035d27a162aafe9`. See FINDING 5. |
| "`FLOOR_LANES` unchanged and the two existing guards untouched" | PR body | **TRUE** |
| pinned digests "resolved from the live registry, not recalled" | `AGENTS.md`, PR body | **TRUE** — all three resolve; the Trivy amd64 child digest matches exactly |

`README.md` and `docs/quality/COMMANDS.md` are not touched by this PR; the only
README in the diff is the new evidence README, which is accurate.

---

## Findings

```
FINDING 1: the new docker-build toolchain assertions swallow a `docker run` failure
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .github/workflows/docker-build.yml:189, :197, :205
  requirements: none yet — propose VZ-OPS-CI-00x (CI controls must fail closed)

Observed:
  docker-build.yml:185-190
      present=$(docker run --rm -e TOOLS="$tools" vizra-core:ci sh -c '
        for t in $TOOLS; do
          command -v "$t" >/dev/null 2>&1 && echo "$t"
        done
        true') || true
      if [ -n "$present" ]; then
  The inner script already ends with `true`, so the container exits 0 on the
  happy path; the trailing `|| true` is therefore load-bearing ONLY when
  `docker run` itself fails. Line 197 (`… || true` around a dpkg-query) and
  line 205 (`if docker run --rm vizra-core:ci test -e /src; then … fi`, which
  takes the else branch on any docker failure) share the shape.

Failure:
  If `docker run` fails for a reason unrelated to the assertion — no shell in
  the image, exec-format error, daemon gone — `present` is empty, the `if` is
  skipped, and the step prints "no build tooling on PATH" and PASSES. The lane
  reports the toolchain absent without having looked. This is the same control
  shape the PR's own Dockerfile comment (lines 141-146) argues against, and the
  PR text claims "no `|| true` anywhere in the `Dockerfile`" — true — without
  noting that the workflow it added has three.

Perspective:
  developer, operator

Recommendation:
  Drop `|| true` on line 189 and let `set -euo pipefail` kill the step; for 197
  keep the in-container `|| true` (grep-no-match is legitimate) but capture the
  `docker run` exit separately; for 205 capture `rc` explicitly and fail on any
  value other than 0 or 1.

Acceptance criteria:
  With the runtime image replaced by one that has no `/bin/sh`, the
  toolchain-absence step FAILS rather than printing "no build tooling on PATH".

Tests:
  No harness exists for asserting a workflow step's behaviour under a broken
  image. The smallest change is to extract the three assertions into a script
  under scripts/ and give it a testdata case in scripts/scripts_test.go's idiom,
  the way image-scan-verdict.py is already tested.

Cross-repo implications:
  core: this PR | user: none | search: none | meta: none

Challenge:
  Six earlier steps in the same job already ran `docker run vizra-core:ci`
  successfully, so a docker failure at line 185 is close to impossible in
  practice — this is defence in depth, not a live hole. That is why it is
  SHOULD and not REQUIRED.
```

```
FINDING 2: an empty --fail-on silently disarms the image-scan findings verdict
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/image-scan-verdict.py:75-78
  requirements: none yet — propose VZ-OPS-SCAN-00x

Observed:
  scripts/image-scan-verdict.py:75-78
      fail_on = {s.strip().upper() for s in args.fail_on.split(",") if s.strip()}
      unknown = fail_on - set(SEVERITY_ORDER)
      if unknown:
          die(...)
  An empty set has no unknown members, so validation passes, and `sev in fail_on`
  is then never true. Measured against the repo's own `findings` fixture, which
  carries a CRITICAL:
      $ python3 scripts/image-scan-verdict.py --report .../findings/trivy-image.json \
          --scanner-exit-code-file .../findings/trivy-exit-code.txt \
          --image-ref vizra-core:scan --fail-on ''
        CRITICAL: 1
        TOTAL: 3
      A valid scan of vizra-core:scan found nothing at or above [].
      exit 0

Failure:
  The one script in the repository whose entire thesis is "a scan lane must not
  pass vacuously" has an unguarded vacuous-pass of its own. It is not reachable
  today — image-scan.yml:126 hardcodes `--fail-on HIGH,CRITICAL` — but a
  one-character workflow edit turns the lane green over a CRITICAL, and no test
  covers it.

Perspective:
  operator, developer

Recommendation:
  Add `if not fail_on: die("--fail-on is empty; a verdict with no failing
  severities cannot fail")` immediately after line 78.

Acceptance criteria:
  `--fail-on ''` and `--fail-on ','` both exit 3 with a named reason, and the
  `findings` fixture with an empty --fail-on does not exit 0.

Tests:
  scripts/imagescan_test.go, a new subtest in
  TestImageScanVerdictRefusesEveryVacuousPass reusing the existing `findings`
  fixture with `--fail-on ''`. No new fixture directory needed, so
  TestEveryImageScanFixtureIsExercised stays satisfied.

Cross-repo implications:
  core: this PR | user: none | search: none | meta: none

Challenge:
  Unreachable code paths are not defects, and the workflow is
  CODEOWNERS-protected, so the edit that would reach this needs owner review
  anyway. Counter: so does every other refusal in this script, and the script
  refuses those cases regardless.
```

```
FINDING 3: a permanently saturated worker reports READY indefinitely
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/jobs/health.go:189-191, internal/jobs/worker.go:199-215
  requirements: none yet — propose VZ-OPS-WORKER-00x

Observed:
  `Health.touch` sets `p.lastProgress = h.now()` unconditionally, and
  `Saturated()` goes through it (health.go:189-191). claimLoop wakes once per
  poll interval when no slot is free and calls `w.health.Saturated(s.Handle)`
  (worker.go:211-213). Measured with a throwaway probe against the shipped
  package:
      h := NewHealth([]string{"default"}, 15*time.Second, nil)
      for i := 0; i < 20; i++ { h.Saturated("default") }
      → ready=true status=ok sites=[{Database:ok ClaimLoop:ok
                                     LastProgressAge:0s Saturated:true}]

Failure:
  A worker whose every handler goroutine is deadlocked — a handler that ignores
  its context, a lock cycle, an unbounded network read with no deadline — is
  indistinguishable from a worker legitimately busy on long jobs. Both record
  Saturated once per poll interval forever, and the probe stays green. Job
  progress has stopped; nothing restarts the container and nothing alerts. The
  intended mitigation is Options.Timeout (5 min) cancelling the job context,
  which only works for handlers that honour cancellation.

Perspective:
  operator

Recommendation:
  The report already carries `saturated: true`. Smallest closure: track
  continuous saturation and report NOT ready once a site has been saturated
  without a single completed job for longer than Options.Timeout plus a margin —
  i.e. longer than any legitimate job could hold every slot. That reuses the
  existing lastClaimOK field, which is recorded but currently never read.

Acceptance criteria:
  A worker with concurrency 1 whose handler blocks forever reports NOT ready
  after Options.Timeout + margin, while a worker with concurrency 1 running a
  4-minute job that completes stays READY throughout.

Tests:
  internal/jobs/health_test.go — a case that drives Saturated() past the
  proposed bound with no ClaimOK and asserts 503; and its negative twin that
  interleaves a ClaimOK and asserts 200.

Cross-repo implications:
  core: this PR | user: none | search: none | meta: the compose probe would
  then restart a genuinely wedged worker rather than leaving it green

Challenge:
  This is a deliberate, documented trade-off, argued at length in
  internal/jobs/health.go:36-45, and it is strictly better than the
  `vizra version` probe it replaces. `lastClaimOK` being recorded-but-unread
  suggests the builder considered exactly this and stopped short. The counter
  is that "cannot pass while the service it probes is broken" is the slice's
  own stated property, and a deadlocked worker is broken.
```

```
FINDING 4: two numbers in the PR body's evidence table do not reproduce
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     PR #7 body, "Verification" table and the appended CI section
  requirements: AGENTS.md § Completion and evidence

Observed:
  (a) The body states `make ci` gave "14 packages ok, 6 `[no test files]`, 0
      skips". My local run and the CI log both show 14 ok and **8**
      `[no test files]` (cmd/fixturegen, cmd/loadcorpusgen, cmd/worker,
      internal/buildinfo, internal/db, internal/migrate, internal/store/sqlcgen,
      migrations).
  (b) The body says the scan report is "published as the `trivy-image-6829285`
      artifact". The artifact on this SHA is
      `trivy-image-3e30533a27c614a51baa4e6c5035d27a162aafe9` — named after the
      merge SHA (artifact id 10627119404, 106 888 bytes).

Failure:
  Immaterial to correctness, but a reviewer following (b) will not find the
  artifact by the name given, and (a) is a number in an evidence table that
  neither CI nor a clean local run reproduces. AGENTS.md requires recorded
  evidence to match what was run.

Perspective:
  developer

Recommendation:
  Correct both numbers in the PR body. No code change.

Acceptance criteria:
  The evidence table's `[no test files]` count matches a clean `make ci`, and
  the artifact name matches `gh api .../artifacts`.

Tests:
  None — this is a document correction.

Cross-repo implications:
  core: this PR | user: none | search: none | meta: none

Challenge:
  Both are typos in prose, not claims about behaviour, and everything the PR
  says about behaviour checked out. Recording them anyway because the chair has
  held six PRs for text that promised more than the control.
```

```
FINDING 5: the probe accepts any 2xx on the readiness path without checking it is a readiness answer
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/healthcheck/healthcheck.go:257-264, :310-317
  requirements: none

Observed:
  `probe` parses the body best-effort for a `status` word and explicitly treats a
  non-JSON body as "not itself a failure, the HTTP code is the verdict"
  (healthcheck.go:310-311). Measured against an unrelated process on the target
  port answering 200 with an HTML page:
      $ VIZRA_LISTEN_ADDR=127.0.0.1:19003 vizra healthcheck api
      vizra healthcheck api: ready — HTTP 200 (127.0.0.1:19003/readyz, 2ms)
      exit=0

Failure:
  If anything other than vizra-api holds that loopback port, the probe reports
  ready. Inside a container with one process per container this is close to
  unreachable, and the image's ENV pins the port — so the blast radius is an
  operator running two things in one container.

Perspective:
  operator

Recommendation:
  Require the 2xx body to parse as JSON with a non-empty `status` field, and
  report NOT READY otherwise. That is one condition and it cannot produce a
  false red against the real /readyz, which always returns that shape.

Acceptance criteria:
  A 200 with an HTML body on the readiness path exits 1 with a named reason; a
  200 `{"status":"ok"}` and a 200 `{"status":"degraded"}` both still exit 0.

Tests:
  internal/healthcheck/healthcheck_test.go, alongside
  TestANonSuccessStatusExitsNonZero.

Cross-repo implications:
  core: this PR | user: none | search: none | meta: none

Challenge:
  This is arguably out of scope: the probe's stated design principle is "it does
  not decide readiness itself; /readyz is the service's verdict", and demanding
  a body shape is a step toward duplicating that rule. A reasonable chair could
  decline this.
```

```
FINDING 6: --timeout has no upper clamp against the container healthcheck timeout
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/healthcheck/healthcheck.go:218, :227-230
  requirements: none

Observed:
  `--timeout` is validated only for being positive. Measured:
      $ VIZRA_LISTEN_ADDR=127.0.0.1:19001 vizra healthcheck api --timeout=30s
      → exit 1 after 30.002s
  The image's own HEALTHCHECK passes no --timeout, so the 2s default applies and
  sits correctly under Docker's 3s (Dockerfile:230). The hazard is only an
  operator overriding it in a compose file.

Failure:
  A probe deadline above the runtime's own `--timeout` means the runtime kills
  the probe before it can report, and every answer becomes "unhealthy" with no
  message — exactly the failure the package comment at healthcheck.go:75-79
  warns about, unenforced.

Perspective:
  operator

Recommendation:
  Warn on stderr (not fail) when --timeout exceeds, say, 10s, or document the
  ceiling next to the flag. The --help text already says "Keep it well under the
  container healthcheck timeout"; making it observable is the small step.

Acceptance criteria:
  `--timeout=30s` still runs but prints a one-line warning naming the risk.

Tests:
  internal/healthcheck/healthcheck_test.go, a case asserting the warning text.

Cross-repo implications:
  core: this PR | user: none | search: none | meta: the compose healthcheck
  block in AGENTS.md sets no --timeout, so it is correct as written

Challenge:
  The image default is correct and documented, and clamping an operator's
  explicit flag is arguably worse than honouring it. This is a documentation
  nit dressed as a behaviour nit.
```

### Recorded observations (not findings)

* **`--min-results` counts result *sections*, not packages**, while its own
  comment (`image-scan-verdict.py:70-72`) argues from package counts and the
  module docstring (`:37`) advertises a `--min-packages N` flag that does not
  exist. A report with a single `os-pkgs` section covering zero packages passes
  cleanly. Partly unavoidable — the lane does not pass `--list-all-pkgs`, so
  there is no package inventory to count. The defect is the comment, not the
  code.
* **`image-scan` builds its own image** with a bare `docker build --tag
  vizra-core:scan .` (no `--platform`, no `RELEASE`/`COMMIT` build args), so the
  scanned image (`sha256:a6675bc0…`, 149 108 587 B) is a different build from the
  asserted `vizra-core:ci` (149 109 021 B) — 434 bytes apart, same Dockerfile and
  tree. Representative, not byte-identical.
* **`build-test`'s "Upload the test log" step uploads `bin/`** (3 compiled
  binaries, 37.7 MB) under the artifact name `build-test-logs`. There is no test
  log published. Pre-existing, not introduced by this PR.
* **`append-only` and `cache-matrix` are pull_request-only**, so two of the six
  required lanes never run on `main` itself. Pre-existing; relevant only if the
  chair ever relies on a main-branch green.
* **V2 (wrong clock) was not caught by any test.** The shipped code is correct —
  `h.now` is `time.Now`, the value is stored with its monotonic reading intact,
  so `now.Sub(lastProgress)` is monotonic and immune to NTP steps and DST — but
  nothing pins that. A future refactor storing `.UTC()` would silently switch the
  comparison to the wall clock with no test going red.
* **This PR both introduces `image-scan` and writes, in the same diff, the
  manifest comment explaining why it is not required.** `ci-required` genuinely
  does not consume it and `FLOOR_LANES` is genuinely unchanged, and the reasoning
  in the file is sound. It is nonetheless a judgment call the chair should make
  deliberately rather than inherit, and it is flagged here for that reason — not
  as a defect.

---

## Cleanup

All containers, images and scratch directories I created were removed by exact
name: `vzv7pr7-pg`, `vzv7pr7-cache`, `vzv7pr7-runtime:verify`,
`vzv7pr7-nouser:verify`, `vzv7pr7-nomedia:verify`, `vzv7pr7-base:verify`, and the
three `vzv-core-pr7-*` scratch clones. No global prune was run; the `vidra-*`
containers, the `vizra-m1a-*` containers belonging to the concurrent worktree,
and the 42 pre-existing volumes were not touched.

---

## Verdict

Every in-scope acceptance bullet reproduced from a clean clone at this SHA:

1. **`vizra healthcheck` cannot pass while the service it probes is broken** —
   proven on real processes with real PostgreSQL for all five stated cases, and
   held up under twelve adversarial attacks including proxy hijack, a wedged
   listener, a full accept queue, redirects and every documented address form.
   Bounded (2 s default, under Docker's 3 s), context-propagating, no retries, no
   secrets in output, exit codes 0/1/64 documented and tested, no new config key.
2. **Runtime image** — clean digest-pinned base (digests resolve against the live
   registry), toolchain provably absent, no `|| true` in the Dockerfile,
   `/var/lib/vizra/media` present and writable by uid 10001 (proven by a real
   write, both in CI on amd64 and locally on arm64). Sizes as stated.
3. **Image-scan lane fails on scanner error and cannot pass vacuously** — 17
   refusal conditions, all fixture-tested; the lane's red on this SHA is a true
   signal over unfixed upstream Debian CVEs, 8 of 13 of which I demonstrated are
   already in the pinned base `main` ships. No threshold weakened, no ignore file.

All six builder mutations reproduced; four of my six additional mutations were
caught by the existing controls, one (V2) revealed an untested-but-correct
property, and one (V6) confirmed the scanner-error refusal end to end.
`ci-required` is green on this SHA with a manifest that matches the jobs that
ran, over a merge commit that is current. Frozen paths are byte-identical.
No guard was edited or weakened.

The six findings are all SHOULD or NIT. **None is blocking:** FINDING 1 and 2
are defence-in-depth gaps in controls that work today, FINDING 3 is a documented
trade-off that is strictly better than what it replaces, and FINDINGS 4-6 are
prose corrections and small hardening suggestions.

FINAL VERDICT: PASS — SHA 68292851e768dd77516c6e49b7831507e4757919
