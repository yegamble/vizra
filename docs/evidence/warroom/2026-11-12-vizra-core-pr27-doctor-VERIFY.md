# VERIFY — vizra-core PR #27 (VZ-OPS-002 `vizra doctor`, first slice)

- PR: https://github.com/yegamble/vizra-core/pull/27, branch `feat/ops-002-doctor`
- SHA verified: b170e521f5f376757c9c17693f347bfa8b9b7891 (head unchanged at start and end)
- Verifier: independent (did not write the code). Verdict 1 of 4 for VZ-OPS-002.
- Environment: darwin/arm64, Go toolchain from go.mod, Docker engine 29.9.2, Compose 5.6.1. Fresh clone `/tmp/vzv-core-pr27-TMZOt4` (deleted afterwards).

## Tests
- `go test -count=1 ./internal/doctor ./cmd/vizra` → exit 0, both packages ok. With `-v`: 77 RUN (56 doctor + 21 cmd/vizra, subtests included), 0 SKIP.
- Floors (`scripts/test-floors.json`): doctor 33→48, cmd/vizra 12→18 in both suites, below the measured 56/21; nothing lowered.

## Verifier mutations (each red, then restored and green; exit codes: red=1, green=0)
| ID | Mutation | Red tests |
|---|---|---|
| V1 | `CheckDockerEngine` returns OK when `docker version` fails | TestCheckDockerEngine, TestDoctorFailsAndExitsNonZeroOnEachRealDefect |
| V2 | `ExitCode` returns ExitOK for BLOCKED-only | TestBlockedIsNeverAPassAndExitsDistinctly, TestExitCodeDistinguishesBlockedFromFail, TestDoctorOnAHealthyInstanceIsOKExceptTheUncheckable, TestDoctorHostCheckThatCannotRunIsBlocked |
| V3 | Delete the `storage root` call site in `collect()` | TestDoctorReportsEveryCheck, TestDoctorFailsAndExitsNonZeroOnEachRealDefect |
| V4 | `CheckTopology` returns OK when docker is not on PATH | TestCheckTopology |

Builder's M1–M6 files in `docs/evidence/ops-002-doctor/` are consistent with these; I re-ran my own instead.

**Test replacement judgement:** old `TestSkipIsNeverAPassButDoesNotFailTheRun` asserted exit 0 and `Report` nil for a SKIP; the new `TestBlockedIsNeverAPassAndExitsDistinctly` asserts exit 3 (ExitBlocked) and a non-nil `Report` error. This is a tightening that implements the ledger negative ("cannot run → BLOCKED, not OK"), not a weakening; V2 proves it bites.

## Real binary (built from this SHA)
(a) `vizra setup --non-interactive --set domain=photos.example.org --set release=v0.1.0` (exit 0, "wrote 15 keys (secrets not shown)"), then `vizra doctor --env env/production.env` → exit 1: `config: DATABASE_URL must be set` FAIL, env file OK, docker engine 29.9.2 OK, compose 5.6.1 OK, rendered topology FAIL (no compose files in temp dir), dns/tls, closed ports, backup freshness BLOCKED with reasons. 8 checks, 2 failed, 3 blocked.

(b) Config keys: core reads `DATABASE_URL` and `VIZRA_CACHE_URL` (internal/config/keys.go:47-48). Doctor gets them through `config.Load` (`cfg.CacheURL`, `db.Open` resolver), so it uses the same keys. Run: `DATABASE_URL=postgres://vz:S3cretPW@127.0.0.1:1/... VIZRA_CACHE_URL=redis://:R3disPW@127.0.0.1:2/0 VIZRA_STORAGE_ROOT=<tmp> vizra doctor` → **exit 1**; database FAIL "PostgreSQL is unreachable"; cache FAIL; go-redis stderr shows it dialled `127.0.0.1:2` (the configured target, not the default 6379). `grep -c 'S3cretPW\|R3disPW'` on the output = 0.

(c) Real PostgreSQL 17 (`vzv-pr27-pg`, 127.0.0.1:55432) + Redis 7.4 (`vzv-pr27-redis`, 127.0.0.1:56379): before migrating, database OK / version 17.11 OK / schema BLOCKED / owner claim FAIL / cache OK redis 7.4.12 / floor OK. After `vizra migrate` (exit 0): database, database version, schema "version 5", cache, cache version floor, storage root, disk free all OK; owner claim WARN; api readiness FAIL (no API running) → exit 1. Password not present in output (grep count 0). Containers and pulled images removed.

**Wrong-target / fake-success audit:** no check reports OK for a target other than the one configured. Disk free falls back to `.` when the storage root does not exist, but names the path it measured and the storage root check FAILs in that case (see F-3). The builder's transcript used `REDIS_URL` (ignored by core) so its "cache FAIL" was against the default `127.0.0.1:6379`, not the target it claimed; that is a transcript error, not a product defect — my run (b) proves the correct key.

## CI on b170e52
`ci-required` success. Manifest lanes append-only, build-test, cache-matrix, fixtures, govulncheck, docker-build: all ran and succeeded on this SHA. `image-scan` failure — not in the required manifest, same base-image CVE failure as main (inbox 9).

## Ledger cases
Closed by this slice (reproduced): Docker engine/Compose versions, env file validity (setup.Check), rendered topology, disk (1 GiB floor), DB/Redis reachability, migration ledger, storage writability, API readiness, exit non-zero on FAIL, BLOCKED ≠ OK (exit 3).
Open: DNS/TLS, closed ports, backup freshness (BLOCKED placeholders only), optional-service health beyond search (IPFS/ClickHouse/federation), transcript-on-a-real-stack evidence. VZ-OPS-003 not in this PR.

## Findings
No BLOCKING findings.

- **F-1 (FOLLOW-UP, low)** `--project-dir D` passes a relative `--env-file` to `docker compose` with `cmd.Dir=D`, so the env file is resolved under D: `vizra doctor --env env/production.env --project-dir /path/to/meta` → FAIL "couldn't find env file: /path/to/meta/env/production.env". Fails closed. Fix: absolutise envFile.
- **F-2 (FOLLOW-UP, low)** Topology FAIL echoes up to 300 chars of `docker compose config` stderr; interpolation errors may quote env values. Not reproduced with a secret; hardening.
- **F-3 (FOLLOW-UP, low)** `diskCheck` silently measures `.` when the storage root is missing; it should say so ("storage root missing; measured .") or report BLOCKED.
- **F-4 (FOLLOW-UP, low)** On an unmigrated database `schema` is BLOCKED ("ledger could not be read"); an empty database is a known state (behind) and could be FAIL with "run vizra migrate". Run still exits 1 via owner claim.
- **F-5 (FOLLOW-UP, info)** Builder transcript `docs/evidence/ops-002-doctor/transcript-real-binary.txt` uses `REDIS_URL`; should be `VIZRA_CACHE_URL`, and should be regenerated at the final SHA (it says built from aae8309).

FINAL VERDICT: PASS — SHA b170e521f5f376757c9c17693f347bfa8b9b7891
