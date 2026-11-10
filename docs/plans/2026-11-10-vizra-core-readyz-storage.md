# Execution plan: VZ-FOUND-005 — /readyz fails closed on an unusable storage root

## Context
Repo yegamble/vizra-core, branch `feat/readyz-storage-check` from origin/main ce805b4, PR https://github.com/yegamble/vizra-core/pull/17. Head at evidence time: 95a72b0807d5bfb386286d2a5fc3a82ba0789612. Environment: darwin/arm64, local worktree; no Docker/PostgreSQL lanes run locally.

Brief premises that did not hold in the tree (decided, not hidden):
- `internal/storelocation` does not exist; no storage code has landed (AGENTS.md "No media tables, no upload").
- No storage-root config key existed (`VIZRA_STORAGE_PREFIX` is a key prefix, not a path). Added `VIZRA_STORAGE_ROOT`, default `/var/lib/vizra/media` — the path the Dockerfile already creates and chowns for the compose volume, so the image is ready with no compose change.
- vizra-core has no compose file (VZ-ISSUE-002..004 own it), so there is no compose consumer to add here; `.env.example` + the key registry are the homes `make config-template-check` enforces.
- `api/openapi.yaml` already listed `storage` in the component enum; only the /readyz prose changed.

## Acceptance
/readyz is 200 only when the storage root exists, is a directory and is writable; otherwise 503 with component `storage` = `unavailable`. Recovers without restart. Detail never carries the path. Non-goals: DB/Redis probe changes, compose, refactors.

## Implementation
- `internal/httpapi/storage_probe.go`: `checkStorageRoot` (stat, IsDir, create+remove one `.vizra-readyz-*` file; no walk) and `storageProbe` (deadline wrapper: fs calls are not cancellable; a stuck check is not stacked).
- `internal/httpapi/server.go`: `Deps.CheckStorage` seam, same pattern as PingDatabase/PingCache; default is the real check, fail-closed when no root is configured.
- `internal/httpapi/probes.go`: storage component, 503 on failure, under the existing 3 s readiness deadline.
- `internal/config`: `VIZRA_STORAGE_ROOT` (must be absolute), `.env.example`.
- `internal/integration/healthcheck_test.go`: the api process gets a temp `VIZRA_STORAGE_ROOT` (otherwise the new check would 503 it on a CI runner).

Writability decision: INCLUDED. The api writes nothing to disk today, but the root is the default `local` location, the DB forbids a read-only default (`storage_locations_default_writable`), and the Dockerfile comment names the failure this prevents (EACCES on first upload). The unwritable test uses a 0555 dir, or `/proc` when euid 0 on linux; it never skips.

## Verification
See evidence. Docker and PostgreSQL integration lanes: NOT RUN locally; CI is their evidence.

## Progress and evidence
State: IMPLEMENTED, READY_FOR_REVIEW (not VERIFIED).

| command | exit | result |
|---|---|---|
| `go test -count=1 -race -v -run 'Readyz|StorageProbe' ./internal/httpapi/` | 0 | 13 pass, 0 skip |
| `make ci` | 0 | all lanes passed (61s) |
| `make openapi-verify` | 0 | PASS |
| `make config-template-check` | 0 | PASS |
| `./scripts/ci-required-guard.sh` | 0 | passed (6 required checks) |
| `go vet -tags integration ./internal/integration/` | 0 | compile/vet only |

### Demonstration — controlled mutation (storage check removed from computeReadiness)
RED:
```
    probes_test.go:116: readiness body has no component "storage": map[checked_at:2026-11-10T19:17:50.697831Z components:[map[name:database status:ok] map[name:cache status:ok] map[name:search status:off]] status:ok]
--- FAIL: TestReadyzHealthy (0.00s)
    storage_probe_test.go:55: /readyz = 200 ok, want 503 unavailable
--- FAIL: TestReadyzStorageRootMissingIs503 (0.00s)
    storage_probe_test.go:63: /readyz = 200 ok, want 503 unavailable
--- FAIL: TestReadyzStorageRootNotADirectoryIs503 (0.00s)
    storage_probe_test.go:94: /readyz = 200 ok, want 503 unavailable
--- FAIL: TestReadyzStorageRootNotWritableIs503 (0.00s)
    storage_probe_test.go:106: /readyz = 200 ok, want 503 unavailable
--- FAIL: TestReadyzStorageRecoversWithoutRestart (0.00s)
    storage_probe_test.go:167: /readyz with no storage root = 200 map[checked_at:2026-11-10T19:17:50.703533Z components:[map[name:database status:ok] map[name:cache status:ok] map[name:search status:off]] status:ok], want 503 with storage unavailable
--- FAIL: TestReadyzStorageRootUnconfiguredIs503 (0.00s)
FAIL
FAIL	github.com/yegamble/vizra-core/internal/httpapi	0.392s
FAIL
red exit 1
```
GREEN (restored with `git checkout internal/httpapi/probes.go`):
```
--- PASS: TestReadyzHealthy (0.00s)
--- PASS: TestReadyzStorageRootMissingIs503 (0.00s)
--- PASS: TestReadyzStorageRootNotADirectoryIs503 (0.00s)
--- PASS: TestReadyzStorageRootNotWritableIs503 (0.00s)
--- PASS: TestReadyzStorageRecoversWithoutRestart (0.00s)
--- PASS: TestStorageProbeIsBoundedByTheContext (0.05s)
--- PASS: TestReadyzStorageRootUnconfiguredIs503 (0.00s)
ok  	github.com/yegamble/vizra-core/internal/httpapi	0.440s
green exit 0
```

## Blockers and handoff
- vizra-core `AGENTS.md` (§ container healthcheck, "503s for exactly one condition") and comments in `internal/healthcheck/healthcheck.go`, `internal/db/db.go` still say PostgreSQL is the only 503. The brief forbade editing AGENTS.md in this PR; needs a follow-up. Consequence to review: `vizra healthcheck api` now reports NOT READY when the media root is unusable.
- A dev machine without `/var/lib/vizra/media` gets 503 from /readyz until `VIZRA_STORAGE_ROOT` is set (fail-closed by design).
- The meta compose tree should pass/mount `VIZRA_STORAGE_ROOT` (default already matches the image path).
- Integration lane (healthcheck_test with real PostgreSQL) not run locally.
