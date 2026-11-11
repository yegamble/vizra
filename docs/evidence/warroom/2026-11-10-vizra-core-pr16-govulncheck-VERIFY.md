# vizra-core PR #16 — govulncheck green by fixing (VZ-CI-004 part) — independent verification

- PR: https://github.com/yegamble/vizra-core/pull/16 (`fix/govulncheck-green` -> `main`)
- Verified SHA: `d2edaf4487485899eafdbc8bd3fbb875fe80ace8` (read at start and at end with `gh pr view 16 --json headRefOid`; identical both times)
- Base: `27cee5417ac51dad041e6f311ba4ca238246563e` (= merge-base, = `main` tip at the end of the run)
- Acceptance: VZ-CI-004, govulncheck lane, ledger case "A reachable advisory fails the lane"
- Verifier: independent (did not write the code); no source edited, nothing pushed, nothing merged, no GitHub setting changed
- Date: 2026-11-10

## Environment

- darwin/arm64 (Darwin 25.5.0), host `go1.26.2`, `GOTOOLCHAIN=auto`: the toolchain named in `go.mod` was auto-selected (`go1.27.1` in the base worktree, `go1.27.4` in the head clone, both printed by `go version` inside the tree).
- Fresh clone of `https://github.com/yegamble/vizra-core.git` in a private `mktemp -d` scratch directory, checked out at the SHA; base as a `git worktree` of the same clone at `27cee54`. Scratch deleted at the end.
- Docker: the CLI is present (registry queries through `docker buildx imagetools` work) but **no daemon is running**, so no container, PostgreSQL or RESP server was available locally.

## Commands

| # | Command (tree) | Exit | Result |
|---|---|---|---|
| 1 | `git diff 27cee54 HEAD --stat` (head) | 0 | 6 files, +17 −12: `AGENTS.md`, `Dockerfile`, `NOTICE`, `fixtures/manifest.json`, `go.mod`, `go.sum`; 1 commit |
| 2 | `make govulncheck` (base 27cee54, go1.27.1) | 2 (tool `exit status 3`) | RED: "Your code is affected by 16 vulnerabilities from 1 module and the Go standard library"; also 7 package-level and 3 module-level, not called |
| 3 | `make govulncheck` (head, go1.27.4) | 0 | GREEN: "Your code is affected by 0 vulnerabilities"; 0 package-level; 1 module-level, not called |
| 4 | `go run golang.org/x/vuln/cmd/govulncheck@v1.8.0 -show verbose ./...` (head) | 0 | 26 root packages matched (= `go list ./...` count, 26); 30 modules + "the go1.27.4 standard library" scanned, echo listed as `v5.4.4`; Symbol: none; Package: none; Module: GO-2026-5932 only |
| 5 | `curl https://go.dev/dl/?mode=json&include=all` | 0 | `go1.27.4` listed, stable; it is the newest 1.27 patch (1.27.0–1.27.4 listed) |
| 6 | `go list -m -versions github.com/labstack/echo/v5` | 0 | … v5.3.1 v5.4.0 v5.4.1 v5.4.2 v5.4.3 **v5.4.4** (newest) |
| 7 | `go mod verify` (head) | 0 | "all modules verified" |
| 8 | `make tidy-check` (head) | 0 | no diff |
| 9 | `docker buildx imagetools inspect golang:1.27.4-trixie` and registry API `HEAD /v2/library/golang/manifests/1.27.4-trixie` | 0 | both return index digest `sha256:b54b2639…77112d9`, identical to `Dockerfile:22` |
| 10 | `cmp <(git show 27cee54:fixtures/manifest.json \| sed s/go1.27.1/go1.27.4/) fixtures/manifest.json` | 0 | byte-identical apart from the one `toolchain.go` line |
| 11 | `make ci` (head) | 0 | "make ci: all lanes passed" (fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify, test-race); 0 FAIL, 0 SKIP lines; `fixtures-verify: ok — 12 fixtures, 1791508 bytes, generator 1 (4ff582ba6959), toolchain go1.27.4` |
| 12 | `go test -count=1 -json ./internal/httpapi/` (head) | 0 | 100 pass, 0 fail, 0 skip (the package that uses Echo) |
| 13 | `make build` (head) | 0 | `bin/vizra`, `bin/vizra-api`, `bin/vizra-worker`; `go version -m bin/vizra-api` = `go1.27.4`, `echo/v5 v5.4.4` |
| 14 | `./scripts/ci-required-guard.sh` (head) | 0 | "ci-required-guard: passed (6 required check(s))" |
| 15 | `gh pr checks 16`, polled every 30 s | — | see CI table |
| 16 | `gh run view <id> --json headSha,conclusion,jobs` for each required workflow | 0 | all on the verified SHA, see CI table |
| 17 | `gh run view --log` for image-scan runs 42770496103 (main) and 42881058232 (PR) | 0 | see claim F |

## Result per claim

**A. Diff scope and "not weakened" — PASS.** Only the six files named in the slice change. `Makefile`, `.github/workflows/govulncheck.yml`, `.github/required-checks.txt`, every script and every workflow are untouched (`git diff --name-only`). The recipe is still `$(GO) run golang.org/x/vuln/cmd/govulncheck@v1.8.0 ./...` (Makefile:199); there is no ignore list, no `|| true`, no `continue-on-error`, no `-show`/exclude flag and no narrowed package pattern in the Makefile or the workflow. `go.mod` changes only the `toolchain` line, its comment and the echo `require`; `go.sum` swaps the echo hashes and adds `golang.org/x/time v0.15.0` (a dependency in echo's module graph, reached only by `echo/v5.test`; `go mod tidy -diff` is clean).

**B. Red/green — PASS, and the green is real.** Base exits non-zero naming 16 called advisories: GO-2026-6603, 6605, 6607, 6608, 6610, 6611, 6612, 6613, 6617, 6809, 6873, 6876, 6877, 6879, 6881, 6883. Head exits 0. The verbose run shows the tool still matching all 26 packages of `./...`, scanning the go1.27.4 standard library and echo v5.4.4, and finding nothing at symbol or package level. Module level only: **GO-2026-5932** (`golang.org/x/crypto` — the `openpgp` package is unmaintained); vizra-core does not import that package, so it is not called and correctly does not fail the lane. This matches the builder's statement. The GitHub `govulncheck` job reproduced the same on the merge tree (`go version go1.27.4 linux/amd64`, "No vulnerabilities found").

**C. Pins — PASS.** go1.27.4 exists and is the newest stable 1.27 patch. echo v5.4.4 exists and is the newest v5. `go mod verify` and `tidy-check` pass. The Dockerfile digest equals what the registry serves for `golang:1.27.4-trixie` today. Every place that pins the Go version agrees: `go.mod` `toolchain go1.27.4`, `Dockerfile:21-22`, `fixtures/manifest.json`, the AGENTS.md pin table; all four workflows use `go-version-file: go.mod`, and CI logs show "Setup go version spec 1.27.4". Remaining `1.27.1` strings outside `docs/evidence/` are none of them pins: `go.mod:9` and `AGENTS.md:496` ("raised from"), `AGENTS.md:473`, `internal/fixtures/manifest.go:64,76`, `Makefile:185`, `internal/httpapi/logsites_test.go:59`, `scripts/test-floors.json` (6 lines), `docs/quality/COMMANDS.md` (3 lines) are dated measurement notes; `scripts/make-integrity-guard.py:1004` and `api/openapi.yaml:437` (`example: go1.27.1`) are examples. No `5.3.1` string remains except the "raised from" note.

**D. fixtures/manifest.json — PASS.** One line changed (`toolchain.go`); no fixture hash, size or generator field moved (command 10). `make fixtures-verify` regenerates the twelve fixtures under go1.27.4 and matches the unchanged hashes, locally and in the GitHub `fixtures` lane, so the re-pin is truthful and not merely a label.

**E. Local lanes — PASS for what can run here.** `make ci` 0, `make build` 0, `ci-required-guard.sh` 0. `make test-integration`, `test-integration-shuffle` and `docker build` were NOT RUN locally (no Docker daemon, no PostgreSQL); GitHub `build-test`, `cache-matrix` and `docker-build` on this SHA are the evidence for them.

**F. GitHub CI on this SHA — PASS.** `ci-required` run 42881058299: `headSha` = the verified SHA, conclusion success, log ends "all 6 required check(s) succeeded". All six manifest lanes ran as real jobs on the same SHA and passed (table below); none was skipped or absent. The govulncheck job's provenance step records tested tree `aedcf2f` = merge of head `d2edaf4` into base `27cee54`, and `main` is still `27cee54`.
`image-scan` is **not** in `.github/required-checks.txt` (the file says so in a "DELIBERATELY ABSENT" block) and is not counted by `ci-required`. It is red on main and red here, but better here:

| | main run 42770496103 (27cee54) | PR run 42881058232 (d2edaf4) |
|---|---|---|
| CRITICAL | 1 | 0 |
| HIGH | 68 | 54 |
| MEDIUM / LOW / UNKNOWN | 117 / 84 / 3 | 82 / 81 / 3 |
| TOTAL | 273 | 220 |
| HIGH+CRITICAL rows in the Go binaries | 15 | 0 |

The 15 HIGH/CRITICAL rows present only on main are exactly the echo v5.3.1 rows (1 CRITICAL, 2 HIGH) and the stdlib v1.27.1 rows (4 CVEs × 3 binaries). No HIGH/CRITICAL row and no advisory id appears only on the PR. The 54 that remain are all Debian 13.7 OS packages, unchanged from main (owner inbox 9, outside this slice).

**G. Echo v5.3.1 -> v5.4.4 — PASS, nothing reproducible against this repo.** Read: `CHANGELOG.md` in the v5.4.4 module (v5.4.0 and v5.4.4 entries), the GitHub release notes for v5.4.1, v5.4.2 and v5.4.3, and the source diff of the two module trees for `router.go`, `route.go`, `echo.go`, `group.go`, `context.go`, `bind.go`, `json.go`, `httperror.go`.
What vizra-core uses of Echo (non-test code, `internal/httpapi` only): `echo.New`, `e.Pre`, `e.Use`, `e.Group`, `GET`/`POST` on six static routes with no path parameter and no wildcard, `Router().Routes()`, `c.RouteInfo().Path`, `c.JSON`, `echo.NewHTTPError`, `echo.StatusCode`, `HTTPErrorHandler`, `NewContext`/`SetRequest`. It imports **no** `echo/v5/middleware` package and does not call `c.Bind` (setup.go:286 says why), `c.Scheme`, `c.RealIP`, `JSONP`, `Static` or the proxy; client address comes from `req.RemoteAddr` directly (setup_limits.go:47).
Upstream behaviour changes and whether they reach this repo:
- `Context.Scheme()` trusts forwarding headers only from private/loopback peers; MethodOverride, Proxy `X-Real-IP`/`Forwarded`, Static path hardening, trailing-slash redirect encoding, JSONP callback validation, BasicAuth scheme parsing, CSRF empty tokens, BodyDump/BodyLimit/Decompress fixes, `ExtractIPFromRealIPHeader` peer validation — all in APIs or middlewares this repo does not use.
- Router: route parsing was rewritten (escaped colons, inline `:verb` splits, custom methods, `Remove`), and path parameters are now unescaped once. The repo has only static routes; the route table, the unknown-route JSON 404, the unclaimed-instance 403 guard (which keys on `Method + URL.Path` and runs for unmatched routes too), request-id and hardening-header behaviour are all asserted by `internal/httpapi` tests, which pass on the head (100/100 unit; integration in GitHub `build-test`).
- `Bind`/JSON body errors now keep an existing HTTP status instead of forcing 400: not reached (no `c.Bind`).
No public API the repo calls was removed; `make ci` and `make build` compile against v5.4.4.

## Findings

No BLOCKING finding.

| # | Class | Finding | Evidence |
|---|---|---|---|
| F-1 | FOLLOW-UP (meta repo, already reported by the builder; confirmed) | `docs/adr/ADR-001-stack-pins-and-licences.md:93` still reads "Go toolchain 1.27.x (1.27.1)"; lines 18 and 94 read "echo/v5 ≥ v5.3.1". Both ranges still hold; the parenthetical is stale. | `grep -n '1\.27\.1\|v5\.3\.1' docs/adr/ADR-001-stack-pins-and-licences.md` in the meta checkout |
| F-2 | FOLLOW-UP (vizra-core, cosmetic) | `api/openapi.yaml:437` keeps `example: go1.27.1`, and dated measurement comments (`internal/fixtures/manifest.go:64,76`, `Makefile:185`, `scripts/test-floors.json`) still name go1.27.1. Examples and history, not pins. | command in claim C |
| F-3 | FOLLOW-UP (vizra-core, pre-existing, not touched by this PR) | The govulncheck recipe scans `./...` without `-test` and without `-tags=integration`, so test-only dependencies (for example `github.com/getkin/kin-openapi`, absent from the 30 scanned modules) and integration-tagged files are outside the scan. Identical on main; shipped binaries are fully covered. | module list of command 4 |
| F-4 | FOLLOW-UP (vizra-core, standing) | GO-2026-5932 (`golang.org/x/crypto/openpgp`) is reported at module level and not called. Keep it visible: any future import of `x/crypto/openpgp` would turn the lane red. | command 4 |

Observation, not a finding: an upstream note, echo's own `CHANGELOG.md` at v5.4.4 has no entries for v5.4.1–v5.4.3; their notes exist only as GitHub releases (read there).

## CI on d2edaf4487485899eafdbc8bd3fbb875fe80ace8

| Check | In required manifest | Result | Run / job | headSha = verified SHA |
|---|---|---|---|---|
| ci-required | (the fan-in) | pass, 8m42s | 42881058299 / 130057112218 | yes |
| append-only | yes | pass, 6s | 42881058672 / 130057113907 | yes |
| build-test | yes | pass, 8m27s | 42881058672 / 130057113567 | yes |
| cache-matrix | yes | pass | 42881058672 / 130060296273 | yes |
| cache-matrix-leg (redis) | (leg) | pass, 5m17s | 42881058672 / 130057113853 | yes |
| cache-matrix-leg (valkey) | (leg) | pass, 4m6s | 42881058672 / 130057114055 | yes |
| fixtures | yes | pass, 1m28s | 42881058516 / 130057113308 | yes |
| govulncheck | yes | pass, 42s | 42881058314 / 130057112208 | yes |
| docker-build | yes | pass, 4m42s | 42881058229 / 130057112190 | yes |
| image-scan | **no** (deliberately absent) | fail, 54 HIGH (main: 69 HIGH+CRITICAL) | 42881058232 / 130057112867 | yes |
| GitGuardian Security Checks | no | pass | external | — |

## Not run

- `make test-integration`, `make test-integration-shuffle`, `docker build`, any image scan: no Docker daemon and no PostgreSQL/RESP server on this host. GitHub CI on the verified SHA is the only evidence for those lanes.
- No mutation of the lane itself (it is unchanged by this PR); the red/green pair is the base tree against the head tree with the same recipe.
- No running-server differential of echo v5.3.1 against v5.4.4 beyond the repo's own test suites; the audit in G is changelog, release notes, source diff and those suites.
- Follow-up lines were not appended to `docs/warroom/FOLLOWUPS.md`: the brief limits this verifier to this one file outside scratch. F-1 to F-4 are for the chair to record.

FINAL VERDICT: PASS — SHA d2edaf4487485899eafdbc8bd3fbb875fe80ace8
