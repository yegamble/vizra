# Verify round 2: vizra-search PR #8, ADR-001 stack pins (VZ-FOUND-001 negative), verdict 4 of 4

- PR: https://github.com/yegamble/vizra-search/pull/8. SHA verified: 4c0867c9233d4cd1fee8a7c7f11faf410bcfba90. The PR head matched this SHA when checked.
- Verifier: independent and fresh. I did not write this code or the round-1 verdict. Environment: darwin/arm64, go1.27.4, GOTOOLCHAIN=local. Fresh clone at /tmp/vzv-search-pr8b-Lq4dwY, deleted afterwards.
- Scope of the fix: round-1 FINDING 1, the Dockerfile build-stage check that a comment could satisfy.

## Baseline
`go test -count=1 -run TestStackPins ./scripts/` exits 0. Dockerfile:19 reads `FROM golang:1.27.4-bookworm@sha256:4fa7c968ba93f1635670522dbb01a2c78150443e1385746924566079f36570ea AS build`. The only other FROM is `FROM scratch` at line 47.

## Dockerfile mutations
For each row I applied the mutation, ran the test, then ran `git checkout .`.

| Mutation | Exit | Reason |
|---|---|---|
| Changed only the FROM line to `FROM golang:1.26 AS build` (the round-1 blocker) | 1 | build stage image "golang:1.26" is not golang:1.27.4-<variant>@sha256:<digest> |
| Restored | 0 | |
| Tag 1.27.3, same digest | 1 | image is not golang:1.27.4-… |
| `FROM --platform=$BUILDPLATFORM` with the correct ref | 0 | |
| Comment-only change (comment now mentions golang:1.26) | 0 | |
| Second `FROM golang:1.26 AS build` added | 1 | want exactly one `FROM ... AS build`, found 2 |
| Lowercase `from golang:1.26 as build` | 1 | image "golang:1.26"… (lowercase is parsed, so it does not bypass the check) |
| `FROM golang:1.26 as build` | 1 | same |
| `AS Build` with golang:1.26 | 1 | same |
| Duplicate stage named `Build` alongside the correct one | 1 | found 2 |
| Correct ref with lowercase `as build` | 0 | |
| Tag without a digest (`golang:1.27.4-bookworm AS build`) | 1 | not …@sha256 |
| `docker.io/library/` prefix with the correct ref | 0 | |
| `evil.io/golang:1.27.4-bookworm@sha256:…` | 1 | rejected |
| Line continuation `FROM golang:1.26 \` / `AS build` | 1 | found 0 (fails closed) |

## Digest
`docker buildx imagetools inspect golang:1.27.4-bookworm` returns Name docker.io/library/golang:1.27.4-bookworm, MediaType OCI image index, Digest sha256:4fa7c968ba93f1635670522dbb01a2c78150443e1385746924566079f36570ea. This matches Dockerfile:19.

## Round-1 mutations re-run
| Mutation | Exit | Reason |
|---|---|---|
| go.mod toolchain go1.27.3 | 1 | `toolchain` line is go1.27.3, want go1.27.4 |
| First setup-go set to `go-version: stable` | 1 | ci.yml job fmt: setup-go go-version "stable" |
| GO_VERSION set to 1.27.5 | 1 | every job reports "1.27.5; want exactly 1.27.4" |
| New direct dep github.com/example/x v0.1.0 | 1 | no ADR-001 row and is not in adrUnlisted |
| go.sum removed | 1 | package [setup failed] |
| Final restore | 0 | clean tree |

## CI on this SHA
- `gh run list --commit 4c0867c…`: run 43280742768 `ci-required` success and run 43280742722 `ci` success, both with headSha equal to this SHA.
- All 11 ci jobs succeeded: fmt, vet, build, tidy-check, test, test-noskip, govulncheck, contract-drift, echo-containment, vendor-contract-selftest, docker-build.
- Go versions in the logs: `grep -oE 'go1\.[0-9]+\.[0-9]+'` finds only go1.27.4 (23 occurrences).

## Findings
- BLOCKING: none.
- New follow-ups: none. Round-1 F-2 to F-4 stay as already recorded and are not re-raised.
- Still outside this PR's claim: the Dependabot half of VZ-FOUND-004.

## Judgement
In vizra-search, VZ-FOUND-001's negative case "A missing lockfile or unpinned toolchain fails CI" is now closed for all four places:
- the go.sum lockfile
- the go.mod go and toolchain lines
- every CI setup-go step
- the Dockerfile build-stage toolchain, checked by tag and digest

FINAL VERDICT: PASS — SHA 4c0867c9233d4cd1fee8a7c7f11faf410bcfba90
