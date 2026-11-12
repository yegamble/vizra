# Verify — vizra-core PR #28 (VZ-OPS-003) — 2nd verdict of 4

- SHA: 135934b71b41e295dd15f72bbfe79ece2093d3fa (PR head confirmed via `gh pr view 28 --json headRefOid`, unmoved)
- Previous PASS: d83f1434a9b75efc656229d0a9311bb52ec8351f (findings/follow-ups there stand; not re-raised)
- Env: darwin, Go (homebrew); fresh clone /tmp/vzv-core-pr28b-srVkm9 (deleted after run)
- Verifier: independent, wrote none of this code.

## Checks
1. `git diff d83f143..135934b --stat` → `.gitignore | 1 +`, `vizra | Bin 37689874 -> 0 bytes`; 2 files. .gitignore adds only `/vizra`. Nothing else changed. PASS.
2. `git diff --numstat origin/main...HEAD | awk -F'\t' '$1=="-"'` → no output (no binary files). Changed files: .gitignore, cmd/vizra/{main,ops,ops_test}.go, docs/evidence/ops-003/* (5 text files), internal/ops/{ops,ops_test}.go, scripts/test-floors.json (12 files, +978/-3). `git ls-tree HEAD --name-only | grep -x vizra` → none. Squash will not contain root `vizra`. PASS.
3. `git check-ignore -v cmd/vizra/main.go cmd/vizra/ops.go` → no output, exit 1; `git check-ignore -v vizra` → `.gitignore:22:/vizra` (root-anchored). PASS.
4. `go build ./...` → exit 0. `go test ./internal/ops ./cmd/vizra` → both `ok`.
   Mutation: internal/ops/ops.go:63 `a = append(a, "-f", f)` → `_ = f`: RED — TestArgvIsExactEnvDerivedChain, TestLogsArgsBoundedAndValidated, TestRestartRefusesUnknownAndOneShot, TestRestartExecsChainAndRefusesUnknownAndOneShot, TestLogsExecsBoundedArgs, TestStatusQueueDepthBlockedNeverZero FAIL. Restored (`git checkout`) → both `ok`; `git status` clean. PASS.
5. `gh pr checks 28` (head 135934b): ci-required pass; build-test, append-only, docker-build, fixtures, govulncheck, cache-matrix (redis, valkey), GitGuardian pass. image-scan fail (not required; same as prior verdict). PASS.

## Findings
No new findings. No BLOCKING findings. Prior FINDING 1 (committed binary) is resolved by this SHA.

FINAL VERDICT: PASS — SHA 135934b71b41e295dd15f72bbfe79ece2093d3fa
