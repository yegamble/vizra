# VERIFY — vizra-core PR #25 (VZ-FOUND-006) — 2026-11-12

- PR: https://github.com/yegamble/vizra-core/pull/25, branch `feat/found-006-boot-refusal`
- SHA verified: `52b4326b7d1ed4d20919ceca3a64501d024b6516`. I checked the PR head before starting and again at the end, and it had not moved.
- Verifier: an independent war-room verifier that did not write this code. This is the 3rd of 4 verdicts for VZ-FOUND-006.
- Environment: darwin, go1.27.4, a fresh clone at `/tmp/vzv-core-pr25-dcglS4` (deleted after the run). The test points the DB and Redis at unreachable `127.0.0.1:1`, so I started no containers.
- Diff: 2 test files (`internal/integration/bootrefusal_test.go`, `internal/obs/signedurl_test.go`) and 5 evidence files. No product code changed. The diff deletes nothing, so no assertion was removed or weakened.

## 1. Manual boot-refusal transcript (real binaries, run by me)
I built `go build ./cmd/api` and `./cmd/worker`. I ran each with `env -i`, `VIZRA_MODE=production` and an otherwise valid config, then changed one key per run:

| binary | case | exit | stderr (named error) |
|---|---|---|---|
| vizra-api | session = `changeme-…` (35 B) | 1 | `VIZRA_SESSION_SECRET: production refuses a known development value` |
| vizra-api | blank session | 1 | `VIZRA_SESSION_SECRET: must be set in production` |
| vizra-api | blank MFA KEK | 1 | `VIZRA_MFA_KEY_KEK: must be set in production` |
| vizra-api | `http://` origin | 1 | `VIZRA_PUBLIC_ORIGIN: production refuses a plain-http origin; …` |
| vizra-api | valid config | 124 (my 20 s timeout) | got past config: `starting mode=production`, owner-claim DB dial error, `listening :8080` |
| vizra-worker | same 4 cases | 1 each | same named errors |
| vizra-worker | valid config | 141 (SIGPIPE, `head`) | got past config: `running`, then `jobs: claim failed … connection refused` (DB missing) |

`grep -c changeme-changeme transcript` = 0, so the refused secret never appears in the output. The valid-config runs get past validation and then fail on the missing DB, as expected.

## 2. Integration test plus mutation
- Green: `go test -count=1 -tags=integration -run TestProductionBootRefusesDevSecrets -v ./internal/integration/` returned exit 0 in 52.8 s. That is 10 subtests: 4 cases plus a control, for each of the 2 binaries.
- Red: I changed the fail-secure block in `internal/config/config.go` from `if production {` to `if false && production {`. The run then exited FAIL with 6 subtests red: the dev, blank-session and blank-KEK cases for both api and worker. The plain-http cases stayed green, which is correct because that check lives outside the block. The reason was "booted in production" (each process ran until the 20 s context timeout).
- Restore: `git checkout`, re-ran, exit 0 (`ok … 94.9s`).

## 3. Log denylist plus mutation
- `go test -count=1 -run TestDenylist -v ./internal/obs/` passed: TestDenylistEveryKeyClass, TestDenylistErrorStrings and TestDenylistSignedURLs.
- Coverage: the existing `denylist_test.go` covers tokens (bearer/JWT-shaped `fakeToken`) and passwords (DSN password, cache-URL password, `password` attribute). The new test covers signed URLs: SigV4 (signature, credential, security token), GCS V4 (signature, credential) and CloudFront (`Signature`). Each URL is logged through 5 paths: attribute, group, WithGroup/With, message and wrapped error.
- Red: I removed `|sig|signature|…|x-(?:amz|goog)-signature` from the value regex in `internal/obs/log.go`. TestDenylistSignedURLs then failed with `awssig7Q`, `goosig7Q` and `cfsig7Q` leaked, and TestDenylistErrorStrings also failed. Restored: `ok`.

## 4. Audit
- The committed evidence under `docs/evidence/found-006-boot-refusal/` holds only test fixture values (`*7Q`, `changeme-…`). It contains no real credentials and no private URLs.
- No skips, no generated files, and no change to production code.

## 5. CI on the SHA
`ci-required` passed. Every lane in `.github/required-checks.txt` ran and passed: append-only, build-test, cache-matrix (with both the redis and valkey legs), fixtures, govulncheck and docker-build.
- build-test unit suite: 1731 passed, 0 failed, 0 skipped.
- build-test integration suite (`-tags=integration ./...`, which includes `internal/integration`): 1914 passed, 0 failed, 0 skipped.
- `image-scan` failed the same way it does on main (the base-image CVEs, inbox 9). It is not in the required manifest.

## Ledger cases
- success "Every key read by config.Load reaches api and worker": proven elsewhere (meta #17). This PR does not touch it.
- success "Every key `vizra setup` writes exists in the template": proven elsewhere (meta #33).
- negative "Production boot with dev JWT/session secret fails": closed here (sections 1 and 2).
- negative "A key added to config without template/compose consumer fails CI": proven elsewhere (meta side, #17/#33). Not exercised here.
- privacy "Log denylist proves tokens/passwords/signed URLs never appear": closed here (section 3).
- evidence_required "boot-refusal transcript": closed here (section 1). "CI assertion outputs": closed here for the core side (section 5). The meta-side outputs are in meta #17/#33.

## Findings
- BLOCKING: none.
- FOLLOW-UP F-1: in each control subtest the api keeps listening with no DB and only stops at the 20 s context timeout. That adds about 20–40 s per run. The control could use a shorter deadline, or treat the `listening` line as "got past config" and stop the process there.

FINAL VERDICT: PASS — SHA 52b4326b7d1ed4d20919ceca3a64501d024b6516
