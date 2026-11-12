# VERIFY — vizra-core PR #23 (QUEUE-readyz-flake): storageProbe busy cleared before result send

- Verifier: independent vizra-verifier (did not write the code). Date 2026-11-12.
- Subject: https://github.com/yegamble/vizra-core/pull/23, head 9a4fc393d44d92d578d9b8b5f02c20f10edcb9e9 (checked at start and end: 9a4fc393d44d92d578d9b8b5f02c20f10edcb9e9). Base origin/main 3f1def3.
- Environment: darwin (macOS 26.5), local Go toolchain, fresh clones in a mktemp scratch dir (deleted after).

## Commands
| Command | Tree | Exit | Result |
|---|---|---|---|
| `go test -race -count=5 -cpu 1,2,8 -run ^TestStorageProbeBackToBackNeverFalseTimeout$ ./internal/httpapi/` | main 3f1def3 + new test copied in | 1 | RED: 8 of 15 runs FAIL (the expected result) |
| same as above plus my own TestZZVerifierHungSingleFlight, `-count=10 -cpu 1,2,8` | head | 0 | 30/30 + 30/30 PASS |
| `go test -race -count=300 -cpu 1,2,8 -run ^TestReadyzStorageRecoversWithoutRestart$` | head | 0 | 900/900 PASS, 0 skips |
| `make ci` (my scratch test removed; clean tree) | head | 0 | "all lanes passed", 20 packages ok, 0 --- FAIL |
| `./scripts/ci-required-guard.sh` | head | 0 | passed (6 required checks) |

(My first `make ci` exited 2, but only because my own scratch test file was not gofmt-clean. I removed the file and ran it again on the clean tree, which is the run in the table.)

## A. Scope — PASS
Diff 3f1def3..head touches 2 files (+17/-2): storage_probe.go (busy store moved ahead of the send) and storage_probe_test.go (one test added). No test was removed, loosened, skipped or retried. The readiness cache and single-flight code are untouched.

## B. Reasoning — PASS
- (i) No concurrent filesystem probe: busy is cleared only after p.check() returns, so the next CAS can succeed only once the previous check has finished. Single-flight holds.
- (ii) A hung check stays bounded: while check() is blocked, busy stays true, so each new Check returns errStorageTimeout without starting a goroutine. My deterministic test proves it: a fake check blocks on a channel, 200 Checks with a 1 ms deadline give exactly 1 start, peak concurrency 1, no goroutine growth, and after release busy clears and the next Check returns nil.
- (iii) No leak: done is buffered (cap 1), so the send never blocks even when the caller has already left on ctx.Done.
- Panic: checkStorageRoot takes a string (no pointer to be nil), guards "", and its os.Stat, CreateTemp, Close and Remove calls return errors rather than panicking. An unrecovered panic in that goroutine would crash the process anyway, not leave a permanent 503. Not reachable in today's tree.

## C. Red/green — PASS (see table)

## D. Local gates — PASS (see table)

## E. CI on the exact SHA — PASS
ci-required success with headSha 9a4fc393…. The six manifest lanes (append-only, build-test, cache-matrix [valkey and redis legs], fixtures, govulncheck, docker-build) all succeeded. image-scan failed, but it is deliberately absent from required-checks.txt.

## Findings
- BLOCKING: none.
- FOLLOW-UP: none new.

## Not run
- Production-mode UI: not applicable (backend only).
- The CI valkey leg was not reproduced locally; CI's green leg on this SHA is the evidence for it.

FINAL VERDICT: PASS — SHA 9a4fc393d44d92d578d9b8b5f02c20f10edcb9e9
