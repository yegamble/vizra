# VZ-CI-004 (vizra-search govulncheck lane) — independent VERIFY of yegamble/vizra-search#7

- SHA: da2614e1619fdc7c7486381bdda8d40ee9849491 (PR head checked at start and end: da2614e1619fdc7c7486381bdda8d40ee9849491)
- Base: origin/main 4810048
- Environment: Darwin 25.5.0 arm64, fresh clone in mktemp dir (deleted), govulncheck v1.8.0 (repo pin), Go toolchain auto-downloaded per go.mod; 2026-11-12
- Verifier: vizra-verifier (did not write the code). Checklist: 2026-11-10-vizra-core-pr16-govulncheck-VERIFY.md

## Commands
| Command | Exit | Result |
|---|---|---|
| git diff origin/main...HEAD --stat | 0 | 6 files, +15/-13: ci.yml, AGENTS.md, Dockerfile, go.mod, go.sum, scripts/scripts_test.go |
| govulncheck ./... @4810048 | 3 | GO-2026-6873/6876/6877/6879/6881/6883 (echo) + stdlib 6859/6613/6617/6809 and 6603..6612 |
| govulncheck ./... @head | 0 | "No vulnerabilities found." |
| go mod verify | 0 | all modules verified |
| go list -m -versions github.com/labstack/echo/v5 | 0 | v5.4.4 is listed |
| curl go.dev/dl/?mode=json&include=all, grep go1.27.4 | 0 | found |
| docker buildx imagetools inspect golang:1.27.4-bookworm | 0 | sha256:4fa7c968ba93f1635670522dbb01a2c78150443e1385746924566079f36570ea = Dockerfile FROM |
| make ci (timeout 85) | 124 | cut off by the 90 s tool cap during `test`; before that config, contract, hmacauth, httpapi (+cmd, buildinfo run separately) ok, no FAIL |
| gh pr checks 7 | 0 | all 11 required lanes pass, ci-required pass |
| gh api .../commits/<SHA>/check-runs | 0 | ci-required success, head_sha = da2614e… |

## Results
- A PASS. Diff is pin-only. ci.yml changes only GO_VERSION and its comment; scripts_test.go changes only the version string; the AGENTS.md diff touches only the Go, Echo and build-image rows of the pin table (owner decision #11). govulncheck job (`govulncheck ./...`, v1.8.0), Makefile and required-checks.txt are unchanged; there is no ignore list and no `|| true`.
- B PASS. Red on main (exit 3, the named advisories), green on the head (exit 0).
- C PASS. Pins exist and agree. Every remaining 1.27.1 / v5.3.1 is history: dated evidence transcripts, the test-floors.json measurement note, and the ADR floor "≥ v5.3.1" in AGENTS.md:983.
- D PASS. Search uses Echo only for routing, the Context, NewHTTPError/HTTPErrorHandler, AcquireContext/ReleaseContext and ResolveResponseStatus. c.Body, BodySHA, BodyUTF and BodyLimit are the repo's own helpers. The HMAC body is read by repo code (internal/httpapi/server.go:364, io.ReadAll(io.LimitReader)), so Echo's binding and body middleware are not on that path. The hmacauth and httpapi suites pass on the head, locally and in CI test/test-noskip.
- E PASS. ci-required succeeded on the exact SHA, and every lane in required-checks.txt ran and passed.

## Findings
- BLOCKING: none.
- FOLLOW-UP: none new.

## Not run
- The full local `make ci` did not finish because of the tool time cap (scripts package and later targets). The same lanes ran and passed in CI on the exact SHA.
- The Echo changelog was not re-audited beyond the search-specific body/header/error path (core #16 verifier covered it).

FINAL VERDICT: PASS — SHA da2614e1619fdc7c7486381bdda8d40ee9849491
