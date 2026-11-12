# Verify: vizra-search PR #8, ADR-001 stack pins (VZ-FOUND-001 negative, VZ-FOUND-004 search part)

- PR: https://github.com/yegamble/vizra-search/pull/8 (branch feat/found-001-004-pins)
- SHA verified: 802776d486088a6835912e632ca9e3e8bfa5e1ad (PR head unchanged when checked)
- Verifier: independent, did not write this code. Environment: darwin/arm64, go1.27.4 local, fresh clone at /tmp/vzv-search-pr8-iYefhN (deleted afterwards).
- Diff: scripts/stackpins_test.go (+308 lines) plus two builder evidence txt files. No product code, workflow, or generated file changed.

## Commands and results
| Check | Command | Result |
|---|---|---|
| Baseline | `go test -count=1 -run TestStackPins -v ./scripts/` | exit 0, 19 PASS (2 tests plus 17 subtests), 0 SKIP |
| Delete go.sum | `mv go.sum …; go test …` | exit 1. `go test` stops at setup (`missing go.sum entry … gopkg.in/yaml.v3`), so the package itself goes red. The in-copy subtests "go.sum deleted" and "go.sum emptied" cover the checker's own path. They pass at baseline. RED, as claimed |
| Empty go.sum | `: > go.sum` | exit 1, setup failed. RED |
| toolchain go1.27.3 | sed go.mod, GOTOOLCHAIN=local | exit 1: "`toolchain` line is go1.27.3, want go1.27.4". RED |
| setup-go `go-version: stable` (first step) | python replace | exit 1: "ci.yml job fmt: setup-go go-version \"stable\"". RED |
| GO_VERSION env 1.27.4→1.27.5 | sed ci.yml | exit 1: every job reports "1.27.5; want exactly 1.27.4". RED |
| Dockerfile comment `golang:1.27.4-bookworm`→`golang:1.26-bookworm` | sed | exit 1: "Dockerfile build stage does not name golang:1.27.4-*". RED |
| **Dockerfile `FROM golang@sha256:… AS build` → `FROM golang:1.26 AS build`, comment untouched** | sed on the FROM line only | **exit 0, GREEN.** See F-1 |
| New direct dep `github.com/example/x v0.1.0` | sed go.mod | exit 1: "no ADR-001 row and is not in adrUnlisted". RED |
| All setup-go → `go-version-file: go.mod` | python replace | TestStackPinsRealTreePasses PASSES. Only mutation subtests fail, as vacuous. See F-2 |
| Restore | `git checkout .` and re-run | exit 0, clean tree |

## CI on this SHA
- `gh run list --commit 802776d…`: run 43279296521 `ci` success; run 43279296555 `ci-required` success. All 12 jobs succeeded: fmt, vet, build, tidy-check, test, test-noskip, govulncheck, contract-drift, echo-containment, vendor-contract-selftest, docker-build.
- Collection: in `test-noskip`, go-test-report shows `github.com/yegamble/vizra-search/scripts: 451 test(s) (floor: 141)` with no skips. `test` (make test) shows `ok github.com/yegamble/vizra-search/scripts 35.342s`. Neither log prints test names, so StackPins collection is inferred from package collection. Because the file sits in package scripts_test, it is compiled and run.
- Go versions in the full run log: `grep -oE go1\.[0-9]+\.[0-9]+` finds only `go1.27.4` (23 occurrences). No other version appears.

## ADR-001 cross-check
- Toolchain 1.27.4 matches ADR row "Go toolchain | 1.27.x (1.27.4)" (l.93) and the 2026-11-11 owner decision (l.177).
- Echo ≥ v5.4.4 matches l.94. go-redis v9.22.x matches l.99. The `go 1.26.0` floor fits "supported lines 1.26 and 1.27" (l.17).
- No enforced version contradicts ADR-001.
- gopkg.in/yaml.v3 has no ADR row and sits on the exception list (follow-up F-3).

## Findings

FINDING 1: The Dockerfile pin check is satisfied by a comment, so an unpinned build toolchain stays green
Severity:    BLOCKER
Confidence:  high
Affected:
  repo: vizra-search
  files: scripts/stackpins_test.go (Dockerfile block: `strings.Contains(df, "golang:"+pinToolchain+"-")`), Dockerfile:15,19
  requirements: VZ-FOUND-001 (negative: unpinned toolchain fails CI), VZ-FOUND-004
Observed:
  The check searches the whole Dockerfile for the substring `golang:1.27.4-`. The only match is the comment on Dockerfile:15. I changed line 19 to `FROM golang:1.26 AS build` and left the comment alone. `go test -run TestStackPins ./scripts/` then reports `ok` (exit 0).
Failure:
  The PR claims "Dockerfile build stage not golang:1.27.4-* fails". That claim is false: the build stage can move to any toolchain, and the required lanes still pass. This is a false-green gate for the VZ-FOUND-001 negative.
Perspective: operator, developer
Recommendation:
  Parse the `FROM … AS build` instruction itself, ignoring comments. Require it to be `golang:1.27.4-<variant>@sha256:<digest>`, or a digest with a same-line tag. Add a mutation subtest that edits only the FROM line.
Reproducer:
  `sed -i '' 's|^FROM golang@sha256:[0-9a-f]* AS build|FROM golang:1.26 AS build|' Dockerfile && go test -count=1 -run TestStackPins ./scripts/` → `ok`.

FINDING 2: `go-version-file: go.mod` is accepted, although the file's own header says that source installs go1.26.0
Severity:    SHOULD (follow-up: today's tree uses the env value 1.27.4; GOTOOLCHAIN=auto would also switch to the toolchain line)
Observed: With every setup-go step changed to `go-version-file: go.mod`, TestStackPinsRealTreePasses passes. The claim was "anything but exactly 1.27.4 fails".

FINDING 3: gopkg.in/yaml.v3 is a direct dependency with no ADR-001 row (exception list)
Severity: SHOULD (follow-up). The ADR needs a row.

FINDING 4: The Dockerfile digest is not checked against the golang:1.27.4 image index
Severity: SHOULD (follow-up). Only the tag text is checked.

Not claimed by the builder: the Dependabot half of the VZ-FOUND-004 negative (no Dependabot config). This remains open.

## Judgement
- In search, the VZ-FOUND-001 negative is closed for the go.sum lockfile, go.mod go/toolchain, and every CI setup-go source.
- It is NOT closed for the Docker build toolchain (F-1).

FINAL VERDICT: FAIL — SHA 802776d486088a6835912e632ca9e3e8bfa5e1ad
