# VERIFY — vizra-core PR #26 (VZ-FOUND-001 negative, VZ-FOUND-004 core part)

- SHA verified: 6b2fd736b091d16db5916ae476af2632eecb5ab7 (PR head checked at start, branch feat/found-001-004-pins)
- Environment: darwin, fresh clone `/tmp/vzv-core-pr26-3UTppx` (deleted), local Go + python3
- Verifier: independent (did not author)

## Commands and results
- `go test -count=1 -run StackPins -v ./scripts` → exit 0; TestStackPinsRealTreePasses PASS, TestStackPinsMutationsFail PASS (13 subtests: baseline, go.sum deleted/emptied, toolchain changed/removed, go line, setup-go `go-version: '1.26'`, go-version-file other, version source removed, echo < v5.4.4, go-redis off 9.22, govips v2.17.0 once present, sqlc v1.30.0). Each subtest asserts exit==1 AND the specific message; the `mutate` helper fails if the mutation target is absent (no vacuous mutation).
- Own mutations against the real tree (`go test -run TestStackPinsRealTreePasses ./scripts`), each restored with `git checkout .` and clean `git status`:
  - `rm go.sum` → FAIL `go.sum is missing or empty`
  - `toolchain go1.27.3` → FAIL `toolchain line is go1.27.3, want go1.27.4`
  - build-test.yml setup-go `go-version: '1.26'` → FAIL at build-test.yml:170 and :406
  - echo/v5 v5.4.2 → FAIL `echo/v5 is v5.4.2, ADR-001 row says >= v5.4.4`
  - sqlc@v1.29.0 → FAIL build-test.yml:191
  - restored → `ok github.com/yegamble/vizra-core/scripts`
- govulncheck reproduced in a scratch module: golang.org/x/text v0.3.7 + `language.ParseAcceptLanguage`, `govulncheck@v1.8.0 ./...` → exit 1, GO-2022-1059; bumped to v0.3.8 → exit 0.
- Network audit: check-stack-pins.py imports only pathlib/re/sys; runPython (scripts/scripts_test.go:14) is a local `python3` exec. No network.

## CI on this SHA
- `ci-required` run 43276175452: success. Manifest (.github/required-checks.txt): append-only, build-test, cache-matrix, fixtures, govulncheck, docker-build.
- build-test run 43276175585 log: `make ci` → `ok github.com/yegamble/vizra-core/scripts 34.317s`; direct unit lane counts `vizra-core/scripts: 609 test(s) (floor: 161)`. Collected in the required lane (Makefile:38 `ci` → `test-race` Makefile:165 `go test -race ./...`).
- image-scan run 43276175540: failure (60 HIGH/CRITICAL Debian base-image CVEs); not in required manifest, not touched by this PR.

## Pins vs ADR-001
| enforced | ADR-001 | match |
|---|---|---|
| toolchain go1.27.4 | row "1.27.x (1.27.4)" l.93; amendment l.177 "Go 1.27.4" | yes |
| go line 1.26.0 | "supported lines 1.26 and 1.27" l.17 | consistent |
| echo/v5 >= v5.4.4 | l.17-18 | yes |
| go-redis/v9 v9.22.x | l.37 | yes |
| govips/v2 v2.18.0 (when present) | l.56 | yes |
| sqlc v1.31.1 | l.27 | yes |
No contradicting pin → nothing BLOCKING.

## Judgement
- VZ-FOUND-001 negative "missing lockfile or unpinned toolchain fails CI": closed for core (reproduced).
- VZ-FOUND-004 core part: "pinned to reviewed releases"/"Lockfiles committed; versions match ADR" reproduced for Go/Echo/go-redis/govips/sqlc in core; negative "audit lane flags vulnerable dependency" reproduced via govulncheck (required lane). Still OPEN: licence notices/SPDX re-verification (ADR table "to be re-verified"), PostgreSQL/Redis/Valkey/Compose pins in meta, vizra-user and vizra-search lockfile/pin parts, echo-contrib v5.0.1 satellite pin not enforced.

## Findings
- F-1 FOLLOW-UP: echo-contrib/v5 v5.0.1 (ADR-001 l.18) is not in the enforced table.
- F-2 FOLLOW-UP: PINS table is duplicated from meta ADR-001 by hand; no cross-repo drift check.
- F-3 FOLLOW-UP: image-scan (non-required) red on this SHA with 60 HIGH/CRITICAL base-image CVEs; pre-existing, not caused by this PR.

No BLOCKING findings.

FINAL VERDICT: PASS — SHA 6b2fd736b091d16db5916ae476af2632eecb5ab7
