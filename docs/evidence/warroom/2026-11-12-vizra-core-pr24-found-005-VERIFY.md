# VERIFY — vizra-core PR #24 (VZ-FOUND-005 core part: /readyz `schema` component, PG stop/recover)

- PR: https://github.com/yegamble/vizra-core/pull/24, branch `feat/found-005-readyz-remainder`, OPEN
- SHA verified: a02610ac596d87676ea100734a3318e0cb43251e (the head matched when I started)
- Verifier: independent war-room verifier (did not write this code). Verdict 2 of 4 for VZ-FOUND-005.
- Environment: darwin, go1.27.4, Docker. Fresh clone `/tmp/vzv-core-pr24-E3W3dU/c` (now deleted).
  Containers `vzv24-pg` (postgres@sha256:86c951e0…, the CI digest in build-test.yml:131) and
  `vzv24-redis` (redis@sha256:06379549…, build-test.yml:377). Both removed by exact name.

## 1. Unit
- `go test -count=1 ./internal/httpapi/` → exit 0, `ok`.
- `go test -count=1 -v -run TestReadyzSchema ./internal/httpapi/` → 7 PASS (5 subtests current/behind/dirty/ahead/unknown, the parent, and DefaultWithoutPoolFailsClosed).
- Mutation `probes.go`: `st.State != migrate.StateCurrent && st.State != migrate.StateBehind` →
  `--- FAIL: TestReadyzSchemaNotCurrentIs503WithComponentNamed/behind … /readyz = 200, want 503` (red for the stated reason). Restored (`git status` clean) → `ok`.
- `TestReadyzCacheDownIs200Degraded` → PASS (Redis down gives 200 `degraded`, matching owner decision 2026-11-12 #8).

## 2. Integration (`-tags=integration -run TestReadyz ./internal/integration/`)
VIZRA_TEST_DATABASE_URL/VIZRA_TEST_CACHE_URL pointed at the containers. Exit 0, `ok 42.076s`:
- `TestReadyzGoesNon200WhenPostgresStopsAndRecoversWithoutRestart` PASS: two rounds, each "PostgreSQL stopped: /readyz 503 after ~2.0s" and "returned: 200 ok after ~2.0s". The 10 s bound (`readyzInterval`) and the same PID are asserted.
- `TestReadyzFailsClosedWhenTheSchemaIsBehind` PASS: 503 after 2.02s, back to 200 after 2.02s.
- Same mutation as above → `schema behind: not reached within the declared 10s (last 200 … schema ok)`, `--- FAIL`, exit FAIL. Restored, clean.

The test simulates "PG stop" with a TCP proxy (restartableProxy), so I added a real check: I built `cmd/api` at this SHA, migrated a fresh database `vzvmanual`, ran the api against the container directly and did a real `docker stop vzv24-pg`:
- before: 200 ok (database, storage, schema, cache ok)
- after the stop: **503 after 2 s**, database=unavailable (schema=unavailable too, worker=degraded)
- `docker start`: **200 ok after 2 s**, the PID was 29638 both before and after (no restart)
- `docker stop vzv24-redis`: **200 degraded**, cache=degraded, everything else ok. This is correct per decision #8.
(The api then exited 1 because I killed it during cleanup, while Redis was already down.)

## 3. Contract
- `api/openapi.yaml` adds `schema` to the `ReadinessComponent.name` enum and documents the 503 case. The handler emits `Name: "schema"` with only ok/unavailable. This is consistent.
- `make ci` was NOT run locally because of time. I rely on CI: every required lane is green on this SHA (below). UNVERIFIED by me: which lane runs the OpenAPI contract test.

## 4. Audit
- The diff deletes no assertions and adds no `t.Skip`. Each detail is a fixed sentence (`schemaReadinessDetail`), so no DSN or driver error reaches the body. Timeouts are bounded: the HTTP client timeout is 5 s, the body is limited to 64 KiB, and the awaits are 10 s and the boot 30 s. A nil pool fails closed (that case is tested).
- The api's process log is printed only when a test fails. It contains the test DSN password, which is a throwaway CI value.

## 5. CI on a02610ac
Check runs: append-only, build-test, cache-matrix (+ redis and valkey legs), fixtures, govulncheck, docker-build, ci-required, GitGuardian: all **success**. image-scan: **failure**.
- `.github/required-checks.txt` lists exactly append-only, build-test, cache-matrix, fixtures, govulncheck and docker-build. Each one ran and passed, and the manifest explicitly documents image-scan as DELIBERATELY ABSENT.
- image-scan also fails on main 46e9a33 (`gh api …/commits/46e9a33/check-runs` → image-scan failure). This is pre-existing (base-image CVEs, owner inbox 9) and not caused by this PR.

## 6. VZ-FOUND-005 coverage
Closed by this PR (core part): schema not current → 503 with `schema` named (behind/dirty/ahead/unknown); PG stop → 503 database=unavailable within the declared 10 s and recovery to 200 without a restart; Redis down → 200 degraded (decision #8).
Still open: the clean-target boot transcript (boot lane **VZ-CI-003**) and the rendered compose model assertion (**meta #39**).

## Findings
No BLOCKING findings.

FINDING 1: PG-stop integration test uses a TCP proxy, not a real server stop
Severity: SHOULD  Confidence: high
Affected: vizra-core internal/integration/readyz_test.go:33-104; VZ-FOUND-005
Observed: restartableProxy closes the listener and connections. A real `docker stop` gave the same 503/200 result in my manual run (above).
Failure: none today. The proxy only approximates a server shutdown (no PG shutdown messages are sent).
Recommendation: let the boot lane (VZ-CI-003) stop the real container.
→ FOLLOW-UP.

FINAL VERDICT: PASS — SHA a02610ac596d87676ea100734a3318e0cb43251e
