# VERIFY — vizra-core PR #17, /readyz storage component (VZ-FOUND-005, storage part)

- PR: https://github.com/yegamble/vizra-core/pull/17
- SHA verified: 17aca39dbfc510d9d2d1355f8afee6a2bbe01e37 (PR head at start and at end; OPEN, MERGEABLE)
- Verifier: independent vizra-verifier, did not write the code. Fresh clone in a private mktemp dir; mutations and my own test files lived only in a second scratch copy, never pushed.
- Environment: macOS Darwin 25.5 arm64, go1.27.4, ordinary (non-root) uid, 2026-11-10. No PostgreSQL/Redis locally: the integration suite was NOT run by me (CI `build-test` only).

## Commands

| # | Command (clean clone at SHA) | Exit | Result |
|---|---|---|---|
| 1 | `go test -count=1 -race -run 'Readyz\|StorageProbe' ./internal/httpapi/ -v` | 0 | 13 run, 13 PASS, 0 SKIP, 0 FAIL |
| 2 | `make ci` | 0 | "make ci: all lanes passed"; 20 `ok` packages, 0 FAIL/SKIP lines |
| 3 | `make openapi-verify` | 0 | ok |
| 4 | `make config-template-check` | 0 | ok |
| 5 | `./scripts/ci-required-guard.sh` | 0 | "passed (6 required check(s))" |
| 6 | MUTATION (scratch copy): probes.go `s.deps.CheckStorage(ctx)` replaced by `error(nil)`; rerun #1 | 1 | RED: TestReadyzStorageRootMissingIs503, ...NotADirectoryIs503, ...NotWritableIs503, TestReadyzStorageRecoversWithoutRestart, TestReadyzStorageRootUnconfiguredIs503, each "/readyz = 200 ok, want 503 unavailable" |
| 7 | `git checkout internal/httpapi/probes.go`; rerun #1 | 0 | green |
| 8 | Own test (scratch) through the real handler and real filesystem: root missing / root is a file / 0555 dir | 0 | 503 each; storage detail "the storage root does not exist or cannot be read" / "is not a directory" / "is not writable"; body carries neither the temp path nor the dir name; the file used as root still holds its content |
| 9 | Own test: 64 goroutines x 50 raw `checkStorageRoot` on a root holding user files named `.vizra-readyz-`, `.vizra-readyz-1`, `.vizra-readyz-*`, `photo.jpg` | 0 | 3200/3200 ok; all four user files byte-identical; no leftover probe file |
| 10 | Own test: config.LoadFrom with VIZRA_STORAGE_ROOT = "", "  ", "relative/media", "./x", "/abs/ok" in development and production | 0 | every non-absolute/empty value reports a VIZRA_STORAGE_ROOT problem in both modes; "/abs/ok" does not |
| 11 | Own stress: 64 goroutines x 20 `/readyz` on a healthy root with a fake clock that expires the cache on nearly every call | 1 | 5 of 1280 answered 503 on a healthy root (see F-1). Second run 0 of 1280 |
| 12 | `go test -count=3000 -race -cpu 1,8 -run 'TestReadyzStorageRecoversWithoutRestart\|TestReadyzHealthy$'` | 0 | 0 failures in 12000 executions: the shipped tests do not flake from F-1 |

## Result per claim

- **A scope — PASS.** 11 files, +306/-5, exactly as described; AGENTS.md, workflows, manifest, migrations, generated files untouched. Test diffs: probes_test.go only adds a temp StorageRoot to the helper, one extra storage==ok assertion and a comment; golden_test.go only adds `VIZRA_STORAGE_ROOT -> t.TempDir()` to the lookup; healthcheck_test.go only adds one env entry. No assertion removed or loosened, no skip added. The not-writable test fails (not skips) when it cannot build its precondition.
- **B tests — PASS.** Rows 1-5.
- **C demonstration — PASS.** Rows 6-8, plus recovery: TestReadyzStorageRecoversWithoutRestart uses ONE server, 503 -> mkdir -> clock past the 2 s cache -> 200, red under my mutation. Behaviour was exercised at the unit seam with the real filesystem check through the Echo handler; the built binary was not run (needs PostgreSQL).
- **D probe safety — PASS, two follow-ups.** Errors are five fixed sentinels; the os.PathError is discarded, so the body cannot carry the path (row 8) and probes.go / storage_probe.go contain no log call at all. Probe file is `os.CreateTemp(root, ".vizra-readyz-*")`: O_RDWR|O_CREATE|O_EXCL, mode 0600, random suffix, and only the name it returned is removed — it cannot open, truncate or delete an existing file (row 9). Bounded: one stat, one create, one remove, no walk. Deadline: computeReadiness has a 3 s context; the check runs in a goroutine, the handler returns at the deadline, and an atomic busy flag stops a second check starting while one is stuck, so a hung mount costs ONE goroutine, not one per probe (TestStorageProbeIsBoundedByTheContext asserts calls==1). No goroutine pile-up reproduced or reachable. Concurrent probes cannot share a probe file (random O_EXCL names) and /readyz is single-flight anyway.
- **E config — PASS.** Row 10. Key is in keys.go Registry (default /var/lib/vizra/media, not secret) and .env.example; `make config-template-check` exit 0. An explicitly empty value is a boot refusal in production and development; an UNSET value takes the default, which the Dockerfile creates (uid 10001, 0750). Chair note: the meta compose tree does not pass VIZRA_STORAGE_ROOT but mounts `media_data:/var/lib/vizra/media` (docker-compose.yml:236, :274) which equals the default, so it works as long as nobody changes one side only.
- **F CI — PASS.** `ci-required` green on the exact SHA; table below.
- **G healthcheck — PASS (by reading + existing tests), not run against a container.** `vizra healthcheck api` exits 0 on any 2xx from /readyz and 1 on non-2xx (internal/healthcheck/healthcheck.go:67-69, :107), and the Dockerfile HEALTHCHECK calls it (Dockerfile:230). So an unusable media root now makes the container unhealthy. That is the fail-closed behaviour the ledger outcome asks for ("/readyz fails when DB/Redis/storage unavailable"). I did not start a container with a broken root.

## Findings

| ID | Class | Finding |
|---|---|---|
| F-1 | FOLLOW-UP | storage_probe.go: the goroutine clears `busy` in a `defer`, i.e. AFTER sending the result. A Check that starts in that gap sees busy==true and returns "the storage root did not answer in time" -> a false 503 on a healthy root. Reproduced only with a fake clock that defeats the 2 s cache (row 11: 5/1280). In production the next computation is >= 2 s later, so it is not reachable today; shipped tests 0/12000 (row 12). False-red, not false-green. Fix: clear the flag before the send. |
| F-2 | FOLLOW-UP | Stale prose: internal/healthcheck/healthcheck.go:30-31 and its usage text (:173) still say /readyz is 503 "for exactly one condition — PostgreSQL unreachable". |
| F-3 | FOLLOW-UP | No committed test for the VIZRA_STORAGE_ROOT absolute-path validation (behaviour correct, row 10). |
| F-4 | FOLLOW-UP | While a check hangs past 3 s, or if the client aborts the request that owns the computation, "did not answer in time" is cached for 2 s; same shape as the existing database ping. |
| F-5 | FOLLOW-UP (meta) | Compose does not set VIZRA_STORAGE_ROOT; mount path and default agree only by coincidence of two literals. A rendered-compose assertion should pin it. |

No BLOCKING finding. No instruction-shaped text found in tool output.

## VZ-FOUND-005 case by case (main + this PR)

| Case | Proven by | State |
|---|---|---|
| /healthz, /version, migration-state probe exist | TestHealthzIsLivenessOnly, TestVersionReportsBuildIdentity, TestSchemazIsAlways200 (httpapi, lane build-test) + openapi-verify | proven |
| /readyz 200 when all reachable | TestReadyzHealthy (now asserts storage ok) ; integration TestHealthcheckApiIsZeroWhenReadyAndNonZeroWhenPostgresStops (real process) | proven |
| non-200 when DB unreachable | TestReadyzDatabaseDownIs503 | proven |
| non-200 when storage root unusable | TestReadyzStorageRootMissingIs503 / NotADirectoryIs503 / NotWritableIs503 / UnconfiguredIs503 (this PR) | proven (unit seam, real fs) |
| non-200 when **Redis** unreachable | NONE — TestReadyzCacheDownIs200Degraded asserts the opposite (200 `degraded`, ADR-002 § Probes) | **ledger text and ADR disagree; not satisfied as written** |
| "schema is current" / fails closed when schema behind | /readyz has no schema component; the API refuses to START on a schema behind (cmd/api/main.go:113) and /schemaz reports it. I did not find a test asserting /readyz non-200 on a behind schema, and did not run the boot-refusal tests | **not proven as a /readyz property; boot refusal not verified by me** |
| negative: stopping PostgreSQL -> non-200 within the interval | integration TestHealthcheckApiIsZeroWhenReadyAndNonZeroWhenPostgresStops (TCP proxy cut, real vizra-api), lane build-test; not run locally | proven by CI only |
| recovery without restart | storage: TestReadyzStorageRecoversWithoutRestart (this PR). Database: I did not confirm a test that restores PostgreSQL and sees 200 again on the same process | storage proven; DB recovery unconfirmed |

Chair: after merge the id can be recorded IMPLEMENTED for DB + storage, but NOT VERIFIED: (1) the Redis clause contradicts ADR-002 and needs an owner decision or ledger wording change, (2) schema-behind is enforced at boot, not by /readyz, and needs its named test cited, (3) DB recovery needs a named test, (4) `evidence_required` still lacks both items: a command transcript with exit codes on the declared clean target (a real compose stack: stop postgres / break the media volume -> `vizra healthcheck api` non-zero -> restore -> zero), and a rendered compose model assertion (`docker compose config` showing the media volume at the VIZRA_STORAGE_ROOT path and the healthcheck command).

## Not run

- Integration suite (`make test-integration`) locally: no PostgreSQL/Redis; relied on CI `build-test`.
- Built binary / container with a broken media root; Docker HEALTHCHECK end to end.
- A real hung network mount.

## CI on 17aca39dbfc510d9d2d1355f8afee6a2bbe01e37

Read with `gh pr checks 17 -R yegamble/vizra-core` at 19:31:40Z, head still 17aca39 (30 s polls, no --watch).

| Check | In manifest | Result |
|---|---|---|
| ci-required | fan-in | pass (6m38s) |
| append-only | yes | pass |
| build-test | yes | pass (6m24s; carries the integration suite) |
| cache-matrix (+ legs redis, valkey) | yes | pass / pass / pass |
| fixtures | yes | pass |
| govulncheck | yes | pass |
| docker-build | yes | pass |
| image-scan | no (deliberately absent; red on main too) | fail — not a gate |
| GitGuardian | no | pass |

All six manifest lanes ran and passed on this SHA; none skipped.

PASS with follow-ups (F-1..F-5). PASS is for this PR's storage slice; it does not make VZ-FOUND-005 VERIFIED (see the case table).

FINAL VERDICT: PASS — SHA 17aca39dbfc510d9d2d1355f8afee6a2bbe01e37
