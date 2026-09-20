# Execution plan: vizra-core PR1 "foundation" — VZ-FOUND-001…006

## Context
- Repository `yegamble/vizra-core`, checkout `/Users/yosefgamble/github/vizra/vizra-core`,
  branch `feat/m0-foundation`, base commit `33e1669` ("Initial commit", README-only).
- Issue: `docs/issues/VZ-ISSUE-001.md` = <https://github.com/yegamble/vizra/issues/1>.
- Scope source: `docs/plans/2026-09-15-prompt01-architecture.md`
  § "VZ-ISSUE-001 PR sequence", **item 1** (lines 100–132). That list is the
  acceptance target and is not narrowed here.
- Binding decisions: ADR-001 (pins/licences), ADR-002 (repo/process/config seam,
  core↔search boundary, CI fan-in), ADR-003 (identity/authz surface),
  ADR-004 (jobs table), ADR-005 (storage_locations, key grammar),
  ADR-007 (site seam, frozen surface × visibility matrix), ADR-009 (platform).
  All Accepted by the owner 2026-09-20.
- Ledger: VZ-FOUND-001, VZ-FOUND-002, VZ-FOUND-003, VZ-FOUND-004, VZ-FOUND-005,
  VZ-FOUND-006 in `docs/quality/features.json`.
- Out of scope (later PRs, not narrowed): the fixture corpus VZ-FOUND-007
  (core PR2), the browser environment VZ-FOUND-008 (`vizra-user` PR2), compose
  topology / installer / boot lane (VZ-ISSUE-002…004), auth endpoints, any table
  beyond the four M0 migrations, the public search endpoint.

### Preflight (2026-09-20, owner's machine, darwin/arm64)
| Tool | Found | Needed | Verdict |
|---|---|---|---|
| Go | `go1.26.2 darwin/arm64` | 1.27.x pin | OK via `toolchain go1.27.1` (`GOTOOLCHAIN=auto`) |
| sqlc | `v1.31.1` | 1.31.1 (ADR-001) | OK |
| libvips | `vips-8.18.2` | 8.18.x (ADR-001) | OK for local use; image builds 8.18.6 from tarball |
| Docker | `29.8.0 arm64/linux` | native arm64 only | OK — **no emulated amd64 builds** |
| gh | `2.98.0`, authenticated as `yegamble` | PR creation | OK |
| jq, make, git, curl, shasum, openssl, psql, redis-cli | present | | OK |
| `yq` | **absent** | — | not used; YAML is parsed in Go/python3 |
| `exiftool` | **absent** (recorded in VZ-ISSUE-001) | fixture corpus | **BLOCKED** for VZ-FOUND-007 — out of this PR's scope |
| Free disk | ~21 GiB | libvips-from-tarball image build | at risk; see Blockers |
| Foreign container | `refpin-spike-kubo` (not mine) | — | left alone |

### Version pins verified against the live registry, 2026-09-20
Each checked directly, not recalled. `[pin at PR time; verify]` cells of
ADR-001's licence table are filled by this PR.

| Pin | Value | Where confirmed |
|---|---|---|
| Go toolchain | `go1.27.1` | `https://go.dev/dl/?mode=json&include=all` — 1.27.1 is the newest 1.27 patch; 1.27.0 and rc1–3 also present |
| `github.com/labstack/echo/v5` | `v5.3.1` | `proxy.golang.org/.../@v/list` (newest) |
| `github.com/labstack/echo-contrib/v5` | `v5.0.1` | proxy list (newest) |
| `github.com/redis/go-redis/v9` | `v9.22.0` | proxy list (newest stable; v9.23.0-beta.1 rejected) |
| `github.com/jackc/pgx/v5` | `v5.11.0` | proxy list |
| `github.com/golang-migrate/migrate/v4` | `v4.20.1` | proxy list |
| `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp` | `v0.71.0` | proxy list |
| `go.opentelemetry.io/otel/sdk` | `v1.46.0` | proxy list (v1.47.0-rc.1 rejected) |
| `github.com/davidbyttow/govips/v2` | `v2.18.0` | proxy list |
| `github.com/minio/minio-go/v7` | `v7.3.0` | proxy list |
| `golang.org/x/crypto` | `v0.57.0` | proxy list |
| `github.com/google/uuid` | `v1.6.0` | proxy list |
| `github.com/prometheus/client_golang` | `v1.24.1` | proxy list |
| `github.com/stretchr/testify` | `v1.12.1` | proxy list |
| `github.com/getkin/kin-openapi` | `v0.149.0` | proxy list |
| `gopkg.in/yaml.v3` | `v3.0.1` | proxy list |

ADR-001 deviation check: 1.27 releases exist, so no ADR-001 deviation is raised
on the Go line.

### Internal search contract placement (decision recorded per the brief)
ADR-002 (Q-001) says "the internal contract is written in core's canonical
OpenAPI and drift-checked in both repos" — it fixes the **repository**, not the
file. It is written to `vizra-core/api/search-internal.openapi.yaml`, beside
`api/openapi.yaml`, and is excluded from core's route↔spec check. Reasons:

1. core is the **client** of `/internal/v1/*` and never serves them. Inside
   `api/openapi.yaml` the spec-without-route direction would fail permanently and
   the only way to green would be weakening the check, which `AGENTS.md` forbids.
2. `vizra-user` generates its browser TypeScript client from `api/openapi.yaml`;
   internal HMAC operations must not enter it.

This is a possible ADR-002 amendment and is reported to the chair rather than
decided silently. `vizra-search` vendors a byte-identical copy and drift-checks it.

## Acceptance
From the PR-sequence item 1, each mapped to evidence below.

| # | Acceptance | Ledger |
|---|---|---|
| A1 | `go.mod` at the ADR-001 pins; `toolchain go1.27.1` | VZ-FOUND-004 |
| A2 | `make ci` = fmt-check, vet, lint-imports, migrate-lint, openapi-verify, sqlc-verify, test-race | VZ-FOUND-001 |
| A3 | `internal/config` with `Load`/`LoadFrom`/`CheckEnv`, collecting `validate()`, fail-secure production: dev secret, short secret, wildcard CORS, plain-http origin, each named escape hatch | VZ-FOUND-006 |
| A4 | `cmd/api` on Echo v5 + `otelhttp` + route middleware setting `http.route`; `/healthz`, `/readyz`, `/version`, `/schemaz` | VZ-FOUND-005 |
| A5 | Valkey wiring: `go-redis` v9, cache readiness probe, two-image matrix lane (Valkey + Redis 7.2.x), in-memory rate-limit fallback marking readiness degraded | VZ-FOUND-004 |
| A6 | `internal/search`: `Searcher{Search,Suggest,Publish}`, `remote` HMAC client treating `not_indexed` as fallback, `sql` returning empty, contract at `api/search-internal.openapi.yaml` with drift check, readiness `search: off\|ok\|degraded` | VZ-FOUND-001 |
| A7 | `cmd/worker`: jobs loop, claim/lease/heartbeat/sweep, one `noop` kind, three metrics, compile-time transaction-only `Enqueue` | VZ-FOUND-003 |
| A8 | `cmd/vizra`: `version`, `doctor` (real checks only), `migrate` | VZ-FOUND-001 |
| A9 | Migrations `0001_sites`, `0002_jobs`, `0003_audit_events`, `0004_storage_locations`, embedded, append-only checksum manifest, migrate-lint | VZ-FOUND-003 |
| A10 | `internal/authz` evaluator, default-deny, table-driven test whose fixture is ADR-007's frozen 21-row surface × visibility matrix | VZ-FOUND-001 |
| A11 | sqlc config + generated code + `sqlc diff` guard | VZ-FOUND-003 |
| A12 | `api/openapi.yaml` probe operations + both-direction contract test | VZ-FOUND-002 |
| A13 | Dockerfile: digest-pinned Debian 13, libvips 8.18.6 from checksummed tarball **below** the Go binary layer, loader list emitted at build | VZ-FOUND-004 |
| A14 | `.github/workflows`: build-test, govulncheck, docker-build, `required-checks.txt`, `ci-required` on `pull_request` **and** `merge_group`, ubuntu-24.04, third-party actions pinned by commit SHA | VZ-CI-001 |
| A15 | Repo `AGENTS.md` + `CLAUDE.md` (imports AGENTS.md) | VZ-FOUND-001 |

**Demonstrations (red against a controlled mutation, then green).**
D1 route-without-spec fails · D2 spec-without-route fails · D3 hand-edited sqlc
output fails · D4 production boot refuses dev secrets · D5 an edited merged
migration fails the manifest check · D6 the golden path passes after `FLUSHALL`.

## Implementation
See the repository tree on `feat/m0-foundation`. Commit 1 (`b0dbeb6`) is `api/`
alone, pushed first because `vizra-user` PR1 and `vizra-search` PR1 consume it.

## Verification
Recorded in "Progress and evidence" below with exact commands and exit codes.

## Progress and evidence
- 2026-09-20: preflight table above. Registry pins verified (table above).
- 2026-09-20: head `2d51dad7557d7a1e36d82ec3befbf8871edf57be` on `feat/m0-foundation`.
- 2026-09-20: commit `b0dbeb6dc27294fe793492ea60bc18b6aed4b042` —
  `api/openapi.yaml`, `api/search-internal.openapi.yaml`, `api/README.md` —
  pushed to `origin/feat/m0-foundation` to unblock the two parallel builders.
  Both documents parse (`python3 -c "import yaml; yaml.safe_load(...)"`, exit 0);
  operations enumerated: core 4 probes; search 3 probes + 3 internal.


### Commands run (owner's machine, darwin/arm64, 2026-09-20)
Source SHA `2d51dad7557d7a1e36d82ec3befbf8871edf57be` unless stated. Every exit code below was observed, not inferred.

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `make fmt-check` | 0 | gofmt-clean |
| 2 | `make vet` | 0 | clean |
| 3 | `make lint-imports` | 0 | 4 boundary checks ok |
| 4 | `make migrate-lint` | 0 | 4 migrations, gapless 1..4, manifest matches (8 files) |
| 5 | `make config-template-check` | 0 | 30 keys, both directions |
| 6 | `make openapi-verify` | 0 | both directions + internal contract |
| 7 | `make sqlc-verify` (`sqlc diff`, sqlc v1.31.1) | 0 | generated output matches |
| 8 | `make ci-guard` (`scripts/ci-required-guard.sh`) | 0 | 4 floor lanes, 4 required checks |
| 9 | `make test-race` | 0 | 8 packages ok, **0 skips**; authz 315 matrix cases |
| 10 | `make ci` (all of the above in order) | 0 | "make ci: all lanes passed" |
| 11 | `make tidy-check` (`go mod tidy -diff`) | 0 | tidy |
| 12 | `make build` | 0 | bin/vizra-api, bin/vizra-worker, bin/vizra |
| 13 | `./bin/vizra version` | 0 | `go1.27.1`, schema 4 embedded |
| 14 | `make test-integration` vs PostgreSQL 18.6 + **Valkey 9.1.2** | 0 | integration 6.6s, no skips |
| 15 | `go test -race -tags=integration` vs PostgreSQL 18.6 + **Redis 7.2.16** | 0 | matrix leg 2 |
| 16 | `docker buildx build --platform linux/arm64` | 0 | image built natively; 943 MB |
| 17 | image assertions: `vizra version --json` | 0 | libvips 8.18.6, **80 loaders**, uid 10001, no x265/heif/heic |

Environment: Go 1.27.1 (auto-downloaded via the `toolchain` directive; local
default is 1.26.2), sqlc 1.31.1, Docker 29.8.0 linux/arm64.
Services run on non-default host ports 55432 (PostgreSQL), 56379 (Valkey),
56380 (Redis 7.2) and torn down at the end; the owner's `refpin-spike-kubo`
container was left alone.

**Native arm64 only.** No emulated amd64 image was built locally, per ADR-009
and the slice brief. The `linux/amd64` release image is proved by the
`docker-build` lane on `ubuntu-24.04`, not by this machine.

### Demonstrations — red against a controlled mutation, then green
Full transcripts are reproduced inline below; each was captured by applying the
mutation, running the check, then `git checkout --` and re-running.

**D1 route without spec.** Mutation: `e.GET("/stats", …)` added to
`internal/httpapi/server.go` with no operation in `api/openapi.yaml`.
- RED `make openapi-verify` exit **2**:
  `TestEveryRouteHasASpecOperation: cmd/api serves 1 route(s) that api/openapi.yaml does not describe: GET /stats`
- GREEN after restore, exit **0**.

**D2 spec without route.** Mutation: a `/stats` operation added to
`api/openapi.yaml` that `cmd/api` does not serve.
- RED exit **2**: `TestEverySpecOperationHasARoute: api/openapi.yaml describes 1 operation(s) cmd/api does not serve: GET /stats`, plus `TestM0ContractIsTheFourProbes`.
- GREEN after restore, exit **0**.

**D3 hand-edited sqlc output.** Mutation: `run_after <= now()` widened to
`now() + interval '1 hour'` directly in `internal/store/sqlcgen/jobs.sql.go`.
- RED `make sqlc-verify` exit **2**, printing the exact diff hunk.
- GREEN after restore, exit **0**.

**D4 production boot refuses dev secrets.** Two halves.
- Rules: `go test -v -run 'TestProductionRefuses…|TestEveryEscapeHatchIsRefusedInProduction'`
  exit **0**, 7 dev-secret values + 7 escape hatches enumerated from the registry.
- The real binary: `./bin/vizra-api` with `VIZRA_MODE=production`, a `changeme…`
  session secret, a `dev-…` KEK, `VIZRA_CORS_ALLOWED_ORIGINS=*` and
  `VIZRA_DEV_DISABLE_AUTH=true` exits **1** printing all four problems at once:
  ```
  vizra-api refused to start.
  configuration is invalid (4 problem(s)):
    - VIZRA_CORS_ALLOWED_ORIGINS: production refuses the wildcard origin '*'; list exact origins
    - VIZRA_DEV_DISABLE_AUTH: is a development-only escape hatch and must not be set in production
    - VIZRA_MFA_KEY_KEK: production refuses a known development value
    - VIZRA_SESSION_SECRET: production refuses a known development value
  ```
- GREEN control: the same binary with real 40-byte secrets boots in production
  mode and logs `"vizra-api listening"` (exit 124 = the 20 s `timeout`).

**D5 an edited merged migration.** Mutation: `max_attempts … DEFAULT 5` changed
to `DEFAULT 10` in `migrations/0002_jobs.up.sql`.
- RED `make migrate-lint` exit **2**, printing the changed hash for
  `0002_jobs.up.sql` and "A CHANGED hash for an existing migration is an
  append-only violation".
- GREEN after restore, exit **0**.

**D6 the golden path after `FLUSHALL`.**
- GREEN: `TestGoldenPathPassesAfterFlushAll` exit **0** — probes, schema ledger,
  durable job and rate limiting all pass before and after `FLUSHALL`.
- RED control: the mutation moves the durable job ledger INTO the cache (an
  `SADD` before the flush, `SCARD` after), which is exactly what `allkeys-lru`
  destroys. Exit **1**:
  `1 golden-path jobs survived FLUSHALL, want 2: durable work must not live in the cache`.
- GREEN after restore, exit **0**.

**Additional demonstrations not required by the brief but run anyway.**

*Chair's Finding 2 — the gate cannot shrink itself.* Four mutations of
`.github/`, each exit **1** with a named error:
1. deleting `build-test` from the manifest → "required lane 'build-test' is MISSING … Deleting a manifest line does not shrink the gate; it turns this lane red."
2. commenting it out → "required lane 'build-test' is COMMENTED OUT … it cannot be made optional by the pull request it gates."
3. `continue-on-error: true` on build-test → "A required lane that cannot fail is not a gate."
4. `actions/checkout@v7` instead of a SHA → "A moving tag is a supply-chain hole."
GREEN after each restore, exit **0**.

*The frozen privacy matrix bites.* Mutation: the listing rule relaxed from
`vis != VisibilityPublic` to `vis == VisibilityPrivate && !owner && !staff` —
the plausible "simplification" that leaks unlisted items into listings.
`TestFrozenMatrix` exit **1** with 14+ named failures citing the fixture line,
e.g. `ADR-007 matrix (testdata/adr007_matrix.tsv:65) says deny for
profile_grid/unlisted/A; Decide returned allow`. GREEN after restore, exit **0**.

*migrate-lint destructive rule.* Mutation: `ALTER TABLE jobs DROP COLUMN
last_error;` appended to an up migration. Exit **2**:
`0004_storage_locations.up.sql:38 destructive statement in an up migration`.
GREEN after restore, exit **0**.

### What did NOT run
| Item | Status | Why |
|---|---|---|
| `make govulncheck` locally | **NOT RUN** | it downloads `golang.org/x/vuln` at run time; the `govulncheck` lane on `ubuntu-24.04` is the evidence |
| `linux/amd64` image build | **NOT RUN locally** | arm64 machine; emulated amd64 is forbidden by the brief. The `docker-build` lane is the proof |
| `merge_group` trigger | **NOT EXERCISED** | there is no merge queue until the ruleset is applied; the workflow declares the event |
| `ci-required` fan-in polling | **NOT EXERCISED locally** | it queries the GitHub check-runs API; the CI run on the PR is the evidence |
| Ruleset / branch protection | **NOT APPLIED** | owner action after this PR lands (ADR-002 item 9). Until then no ledger entry may reach VERIFIED on CI evidence alone (item 10) |
| Fixture corpus (VZ-FOUND-007) | OUT OF SCOPE | core PR2; `exiftool` is also absent locally |
| Browser environment (VZ-FOUND-008) | OUT OF SCOPE | `vizra-user` PR2 |

### Contract changes needed from another owner
1. **ADR-001 licence table.** Every `[pin at PR time; verify]` cell this PR
   fills is recorded in `vizra-core/AGENTS.md` and `vizra-core/NOTICE`, because
   `docs/adr/` is the meta repository and not this builder's checkout. Meta PR1
   must copy them into ADR-001's table: pgx v5.11.0, golang-migrate v4.20.1,
   OpenTelemetry otelhttp v0.71.0 / otel v1.46.0, `golang.org/x/crypto` v0.57.0,
   PostgreSQL 18 digest `sha256:86c951e0…`, Valkey 9.1.2 digest
   `sha256:c123e371…`, Redis 7.2 digest `sha256:06379549…`, Debian 13 digest
   `sha256:a99cfc51…`, libvips 8.18.6 tarball sha256 `3c41e1d5…`.
   `govips` v2.18.0 and `minio-go` v7.3.0 are NOT in `go.mod`: nothing in M0
   links them and an unused require fails `go mod tidy -diff`. They enter with
   VZ-MEDIA-001 and VZ-STORAGE-002.
2. **ADR-001 AVIF/HEIC split needs a ruling before M1 media work.** ADR-001 says
   "HEIC decode via libheif + libde265 exists only when the HEIC option image is
   selected … AVIF uses dav1d/aom". In libvips, AVIF is decoded THROUGH libheif;
   `libdav1d`/`libaom` are libheif's backends, not an independent libvips path.
   So excluding libheif from the default image — which this Dockerfile does, and
   which the loader-list assertion enforces — also excludes AVIF. The built
   image's 80 loaders contain no `heifload`/`avifload`. M0 owns no media so
   nothing is blocked today, but the ADR-001 sentence is not implementable as
   written and needs an owner ruling before VZ-MEDIA-001.
3. **ADR-002 internal-contract path.** Recorded above under "Internal search
   contract placement": a separate `api/search-internal.openapi.yaml` rather
   than paths inside `api/openapi.yaml`. Possible ADR-002 amendment.


### CI runs (the real gate)
| Run | Head SHA | Result |
|---|---|---|
| 1 | `2d51dad7557d7a1e36d82ec3befbf8871edf57be` | `build-test` green; **`govulncheck`, `docker-build`, `ci-required` RED** — three real defects, all in the CI configuration, none in the product code |
| 2 | `2b9c540e81960954ee39e6a2aeec027e0f764a67` | all four required checks **green** |
| 3 | `e45e78454f101ebbf814dbdcaeef0117ec9a30e0` | all four required checks **green** (head) |

The three run-1 defects and their fixes, recorded because a verifier should see
that the first CI run found real problems rather than being a formality:

1. **`govulncheck` crashed**: `panic: unexpected expr: *ast.KeyValueExpr`.
   `x/vuln` v1.1.4 cannot parse the Go 1.27 AST. A crashed scanner is not a
   clean scan, so the lane was right to fail. Pinned to v1.8.0, verified against
   the live proxy and run against this tree locally (`No vulnerabilities found`).
2. **`docker-build`'s layer-order assertion was a false positive.** It grepped
   the rebuild log for `meson compile`; buildx echoes a CACHED step's full
   command text, so the pattern matched even though the log said `#9 CACHED`.
   Now it finds the libvips step number and requires `#N CACHED` — and fails
   loudly if it cannot find the step at all, rather than passing vacuously.
3. **`cache-matrix` could never be found by the fan-in.** GitHub names a matrix
   job's check runs with the matrix values appended, so a check literally named
   `cache-matrix` never existed and `ci-required` would have waited for it until
   timeout. The legs now run as `cache-matrix-leg` and an aggregate job named
   `cache-matrix` requires `needs.cache-matrix-leg.result == 'success'`, with
   `if: always()` so a cancelled or skipped matrix fails rather than skipping.

Run 3's `ci-required` log shows the fan-in working:
`required checks (4): build-test cache-matrix govulncheck docker-build` →
`SUCCESS` for each.

### GitGuardian — a non-required check that is still red, honestly
`GitGuardian Security Checks` is a third-party app on the repository. It is NOT
in `.github/required-checks.txt` and does not gate `ci-required`. It reports 7
findings, all in **historical commits of this branch**, none at HEAD:

| Commit | File | What it was |
|---|---|---|
| `fe6101f` | `internal/config/config_test.go` | 32-byte literal test secrets |
| `fe6101f` | `internal/obs/log_test.go` | a fake bearer token in a redaction test |
| `fe6101f`, `2b9c540` | `.github/workflows/build-test.yml` | the CI database password |

None was ever a credential. All three causes are fixed at HEAD rather than
suppressed: the test values are now **built** (`strings.Repeat`) instead of
written as random-looking literals, and the CI database has **no password at
all** (`POSTGRES_HOST_AUTH_METHOD=trust` on a loopback-only container that lives
for one job and holds an empty schema).

The historical hits persist because GitGuardian scans every commit in the pull
request. Clearing them needs either a history rewrite — which would break the
`api/` SHA `b0dbeb6` that `vizra-user` and `vizra-search` already vendored from —
or the owner resolving them in the GitGuardian dashboard. **Owner decision; not
taken here.** No `.gitguardian.yaml` exclusion was added: silencing a scanner is
not a fix.

### Security findings from sibling reviews, fixed on this branch
**vizra-user PR1 Finding 2 (the gate could shrink itself).** Addressed by
`scripts/ci-required-guard.sh` FLOOR_LANES; four red/green demonstrations above.
`.github/CODEOWNERS` committed; the ruleset that enforces it is an owner action.

**vizra-search PR1 Findings 1 and 2 (the HMAC scheme).** Both live in core's
copy, and core owns `api/`, so both are fixed here.

*Finding 1 — the timestamp window did not close.* `Verify` derived a
`time.Time` from the header, subtracted and folded the sign. `time.Unix()` wraps
on a huge seconds value and a `Duration` of `math.MinInt64` is its own negation,
so a validly signed request with an out-of-range timestamp never expired — and
at M0 there is no nonce store, so this window is the only replay bound.
`TestTimestampWindowAcrossTheMagnitudeRange` (23 rows, both directions,
including `math.MinInt64`, `math.MaxInt64` and the Duration-overflow values) was
written first and run **RED** against the previous code:

```
--- FAIL: .../just_past_the_Duration_overflow,_ahead
    timestamp 11089000000 was ACCEPTED with a valid signature.
--- FAIL: .../far_beyond_the_Duration_overflow
    timestamp 1001789000000 was ACCEPTED with a valid signature.
--- FAIL: .../year_10000
    timestamp 253402300799 was ACCEPTED with a valid signature.
```

Fixed: the magnitude is validated against `1000000000 .. 4102444800` **before**
any arithmetic, the skew is computed on plain int64 seconds, and a verifier
whose own clock is out of range fails closed. **GREEN**, exit 0.

*Finding 2 — the two implementations agreed on accept and disagreed on reject.*
`CanonicalString` now uses every field verbatim; the shape rules refuse
non-canonical input instead of rewriting it (uppercase method, bare decimal
timestamp, lowercase-hex nonce, exactly one of each header).
`api/search-hmac-testvectors.json` gained **24 negative vectors**, each with a
genuine signature over its own fields and the rule written out, judged against a
fixed `verifier_now_unix`. `TestHMACNegativeTestVectors` consumes them and
`TestNegativeVectorSignaturesAreGenuine` proves each signature is real, so a
vector cannot "pass" for the wrong reason.

Load-bearing demonstrated twice: relaxing the timestamp rule to `TrimSpace`
turns **5** vectors red; the pre-fix verifier turns **9** red, including
`nonce-uppercase-hex`, `timestamp-duplicated-header` and `timestamp-year-10000`.
The rules are now normative prose in the contract's `securitySchemes`, with the
M0 replay limitation stated rather than implied.

*Item 3 (look, do not necessarily change): `search_schema_version`.* **Confirmed
intended**, and the reason is now written into the contract. `/readyz` is the
authoritative report. `SearchResponse` echoes it because hits are the only
response contents core interprets against an index schema; a suggestion is a
bare string and an event acknowledgement is a count, so neither can be misread
because of schema skew, and adding the field there would imply a check with
nothing to check. Revisit with VZ-SEARCH-001 (M3).

**The `api/` SHA to re-vendor from: `2b9c540e81960954ee39e6a2aeec027e0f764a67`.**
That is the last commit touching `api/`; `e45e784` follows it and changes only
`.github/`.


## Review round 1 — backend seat, security seat, independent verifier

Head after the round: `4f8d0fc207f94a2a516607d167fcf69abd7a2148`. **`api/` last touched by `866eeb8c2028b18e68eec86fcce36ea545d1af55`** — `vizra-user`
and `vizra-search` re-vendor from that SHA.

All five required checks green on `4f8d0fc207f94a2a516607d167fcf69abd7a2148`: `append-only`, `build-test`,
`cache-matrix` (both legs), `govulncheck`, `docker-build`, and the `ci-required`
fan-in. **900 tests, 0 skips** (`go test -count=1 -tags=integration -v ./...`,
exit 0), of which 315 are the frozen authz matrix.

### Blockers

**Security 1 — the evaluator was default-ALLOW on an unset visibility.**
`Decide` normalised `""` to `VisibilityPublic`, so a zero-valued `Resource`
granted an anonymous viewer `item_page`, `original_download`, `derivative_url`,
`embed`, `search`, `explore`, `shared_cache`, `federation_outbound` and
`count_contribution`. The verifier's mutant "any unrecognised visibility →
public" survived both `make ci` and `make test-integration`.

RED transcript `R2-authz-red.txt`, with the new tests against the
normalisations still in place:

```
--- FAIL: TestUnknownVisibilityDenies/item_page/""
    item_page with visibility "" ALLOWED for viewer class A (reason "public").
--- FAIL: TestUnknownVisibilityDenies/federation_outbound/""
--- FAIL: TestUnknownVisibilityDenies/ipfs_publication/""
```

The fix removes both `"" →` normalisations and denies with
`ReasonVisibilityUnknown`. `TestUnknownVisibilityDenies` drives 21 Actions × 8
unknown values (`""`, `PUBLIC`, `Public`, `scheduled`, `moderated`, `deleted`,
`" public"`, `"public\n"`) × 5 viewer classes; `TestZeroResourceDeniesEverySurface`
kills the verifier's exact mutant directly. `HideExistence` now hides anything
not public/unlisted. **The 315-case frozen matrix is unchanged** (re-counted:
315 PASS). `DownloadSetting` keeps its permissive default with the asymmetry
explained in the struct field.

**Backend 1 — a crash-looping job wedged the queue.** RED transcript
`R2-crashloop-red.txt` reproduces the reviewer's own failure against the
pre-fix queries:

```
cycle 3: ClaimJob failed: ERROR: new row for relation "jobs" violates
check constraint "jobs_attempts_bounded" (SQLSTATE 23514)
```

`ClaimJob` now filters `attempts < max_attempts`; `SweepExpiredLeases`
dead-letters an exhausted row in one statement with a `last_error` naming lease
exhaustion and `finished_at` set. `attempts` is documented as counting CLAIMS,
with the reasoning. GREEN in `R2-crashloop-green.txt`.

**Backend 2 — the append-only guarantee was not enforced.** Proven with two
throwaway PRs against `feat/m0-foundation` (not `main`: the rule bites only for
migrations that exist on the BASE branch, and these four are not on main yet, so
basing on this branch is the faithful simulation of an edit after merge).

| | PR | Run | `append-only` JOB | RUN conclusion |
|---|---|---|---|---|
| negative — edit `0002`, regenerate the manifest | [#2](https://github.com/yegamble/vizra-core/pull/2) | [35532576593](https://github.com/yegamble/vizra-core/actions/runs/35532576593) | **failure**, naming the file | failure |
| positive — only ADD `0005` | [#3](https://github.com/yegamble/vizra-core/pull/3) | [35532590902](https://github.com/yegamble/vizra-core/actions/runs/35532590902) | **success** | **failure** |

**Correction, round 2.** The round-1 write-up said run 35532590902 "PASSED". It
did not: the RUN concluded `failure`. What passed was the `append-only` JOB —
`append-only: ok (2 migration file hash(es) added, none removed or changed)`.
The run failed in `build-test`, on `make ci` → `sqlc-verify`, because the
throwaway branch added migration `0005` without regenerating the sqlc output,
which is unrelated to the append-only control. Verified from the API:
`run conclusion: failure`; jobs `append-only success`, `build-test failure`.

The distinction matters: the positive control's job is to show that the
append-only gate does not block a purely additive migration, and it does show
that. It does not show that such a PR is otherwise mergeable, and the earlier
wording implied it did.

```
##[error]a migrations/manifest.sha256 line was REMOVED or CHANGED.
    -af8405894ae1c130235453835ddbefef872b551115963da3fe525d3a1c74de07  0002_jobs.up.sql
```
```
append-only: ok (2 migration file hash(es) added, none removed or changed)
```

`migrate-lint` was GREEN on the negative branch before it was pushed — the
regeneration restored self-consistency, which is exactly the laundering the CI
job exists to catch. Both PRs closed, both branches deleted; `git ls-remote`
shows only `main` and `feat/m0-foundation`. CODEOWNERS gains `migrations/**` and
`api/**`; `migration-manifest.sh`'s header now names all three layers and claims
only controls that exist.

**Verifier 2 — `vizra doctor` had zero tests.** The verdicts moved to
`internal/doctor` as pure functions (`cmd/vizra` does only I/O). All three
mutants go red — transcript `R2-doctor-mutants.txt`:

| Mutant | Result |
|---|---|
| M8a schema-drift reports `statusOK` | RED — 3 sub-tests, "A doctor that reports OK on a drifted schema actively misdirects the investigation" |
| M8b cache floor check deleted | RED — `no check named "cache version floor"` |
| M8c invalid config reports `statusOK` | RED — 5 keys, plus "an invalid configuration exits 0; `vizra doctor && deploy` would proceed" |

Coverage: schema current/behind/ahead/dirty/unreadable; cache flavour, version
floor (12 cases including fail-closed on unparseable); database unreachable and
not leaking the DSN; invalid config; compose floor (10 cases); search off vs
configured-unreachable. Every case asserts the STATUS and the EXIT CODE.

### Schema, still editable and frozen on merge

Backend 3 `jobs_claim` is now `(priority, run_after) WHERE state = 'queued'`;
`TestClaimPlanDoesNotSortTheBacklog` asserts no Sort node at 10k queued rows and
`TestClaimIndexExcludesTerminalRows` asserts the partial predicate.
Backend 4 CHECK bounds on `payload` (64 KiB), `kind`, `correlation_id`,
`last_error`; `ErrPayloadTooLarge` in Go AND the raw-INSERT rejection asserted,
which is the half that proves the bound is in the database.
Backend 5 `CREATE UNIQUE INDEX sites_singleton ON sites ((true))`, and
`GetDefaultSite` drops `ORDER BY`/`LIMIT`.
Backend 6 `audit_events_ip_prefix_shape` refuses a full IPv4/IPv6 address
(accepts `203.0.113.0/24`, `2001:db8::/48`, NULL). Per the chair's ruling the
UPDATE/DELETE trigger waits for M1; the migration header now separates what the
schema ENFORCES from what it only asks for.

### Ride-alongs

Backend 7 outcome writes use a detached 10 s context and the drain is bounded by
`DrainGrace`; `TestGracefulShutdownRecordsTheOutcomeOfAnInFlightJob` asserts the
job reaches `succeeded` and the sweep reclaims nothing. Backend 8 a real ladder
walk at `MaxAttempts 3` asserting `run_after` moves out, plus worker-level crash
recovery; the misleading comment is gone. Backend 9 `Priority` 0 documented as
unset, `PriorityUrgent`/`PriorityBackground` added.
Security 5 `safeError` = `truncate(obs.Redact(...))` at every `last_error` write,
with a straddling-boundary test. Security 6 `CheckRedirect` returns
`http.ErrUseLastResponse` on both the call path and `ping`; the two-server test
asserts the second host received **no request and no `X-Vizra-*` header**.
Security 8 the guard is now Python parsing YAML: `continue-on-error` present at
all, any spelling, on a floor lane's job or steps, plus "is this floor lane
triggered on `pull_request`"; 13 fixture workflows under `scripts/testdata/guard/`.
Security 9 one hardening-headers middleware asserted by iterating `Routes()` and
through the 404 path, plus `ReadTimeout`/`WriteTimeout`.
Security 2/3 production refuses by EXACT value anything this repository
publishes — the test reads `key_utf8` from the vectors file at test time — and a
value-bearing hatch is refused on PRESENCE (`alice`, `0`, `false`, whitespace).
Security 4 `.gitguardian.yaml` with five per-path exclusions each carrying a
written reason, under CODEOWNERS, no `*_test.go` glob; `.gitignore` gains
`*.env`, `.env.*` and `env/*.env` with `!.env.example`.

### Verifier 3 — claims made true rather than kept

a. The guard's test-selection check now reads the **Makefile**. Demonstrated in
`R2-scripts-mutants.txt`: `PKGS := ./internal/buildinfo/` → `FAIL PKGS is
'./internal/buildinfo/', not './...'`; an emptied `-run` → `FAIL 1 -run
pattern(s) are empty`.
b. `VIZRA_MAX_INTERNAL_BODY_BYTES` is REMOVED from core's registry and template.
Core is the client; the contract now states that `vizra-search` configures and
enforces it, and that core bounds the response direction at a fixed 8 MiB.
`config-template-check` still passes.

### Verifier 3 — the shell scripts gained negative cases

`scripts/scripts_test.go` drives migrate-lint, the gate guard and the import lint
against `scripts/testdata/` (30 fixtures). Mutant M6 — removing `COLUMN` from the
destructive alternation — now goes RED:

```
--- FAIL: TestMigrateLintFixtures/drop-column
    exit 0 (failed=false), want failed=true.
```

### GitGuardian — still red, still not a required check

7 findings, **all in historical commits** (`fe6101f`, `2b9c540`), none at
`4f8d0fc207f94a2a516607d167fcf69abd7a2148`. No real credential; nothing to rotate. Causes fixed at HEAD, and the
exclusions are now committed with per-path reasons. Clearing the history needs
either a rewrite — which breaks the `api/` SHA `b0dbeb6` already vendored — or
the owner resolving them in the dashboard. Owner decision.


## Review round 2 — the last round

Head `b5f8f6aa0584d11a502e0415113ce5b52159d548`. **`api/` untouched** — it is
still `866eeb8c2028b18e68eec86fcce36ea545d1af55`, which is what `vizra-user` and
`vizra-search` vendor.

All five required checks green: `append-only`, `build-test`, `cache-matrix`
(both legs), `govulncheck`, `docker-build`, plus the `ci-required` fan-in.
**917 tests, 0 skips**, 315 of them the frozen matrix. Transcripts are now
durable in the repository under `docs/evidence/pr1-round1/` and
`docs/evidence/pr1-round2/`, not a session scratchpad.

### 1. BLOCKER — `audit_events_ip_prefix_shape` accepted a /96 and a /112

The IPv6 branch's group repetition was unbounded. Before touching the
migration, the whole named case list was checked against both grammars:

```
value                                    want   current  frozen
2001:db8:1234:5678:9abc:def0::           False  True     False    <-- CURRENT IS WRONG
2001:db8:1234:5678:9abc:def0:1234::      False  True     False    <-- CURRENT IS WRONG
a:b:c:d:e:f:1::                          False  True     False    <-- CURRENT IS WRONG
2001:db8:1234:5678:9abc:def0::/48        False  True     False    <-- CURRENT IS WRONG
999.999.999.0                            False  True     False    <-- CURRENT IS WRONG
2001:DB8::                               False  False    False
...
frozen grammar: all 14 cases correct
```

`999.999.999.0` was a second, smaller hole in the same constraint: the IPv4
branch used `[0-9]{1,3}`, which is not an octet.

The new subtest is RED against the old regex (`01-ip-prefix-RED.txt`, all five
values accepted) and green after (`02-ip-prefix-GREEN.txt`, five subtests). The
frozen grammar is exactly as ruled; the `/len` suffix is deliberately not
cross-checked against the group count, and the reason is in the migration. The
M1 writer's contract — Unmap() first, mask to /24 and /64, lowercase, NULL when
there is no usable address — is written into 0003's header. `manifest.sha256`
regenerated in the same commit; `append-only` green.

### 2. REQUIRED — `truncate` cut UTF-8 runes in half

Unit RED (`03-truncate-RED.txt`): a dangling `c3` byte at pad 1991.

End-to-end RED (`05-lasterror-utf8-RED.txt`), which is the failure that matters:

```
msg="jobs: recording dead-letter failed" rows=0
    error="ERROR: invalid byte sequence for encoding \"UTF8\": 0xe6 0xe2 0x80 (SQLSTATE 22021)"
```

The row stayed `leased` with `last_error` NULL — the cause lost, and the sweep
about to re-run it. GREEN: 2014 bytes stored, valid UTF-8, redacted, message
preserved.

The integration fixture pads to exactly 1999 bytes so a 3-byte rune starts at
byte 2000; a first attempt left the alignment to chance and passed under the
bug, which is worth recording because a red that depends on luck is not a red.

**A second defect found while doing this, fixed in the same commit:** the three
`recording X failed` log lines logged only the row count and swallowed the
error, so this failure printed `rows=0` and nothing about why. That silence is
what made the bug invisible; they now log the cause.

### 3. REQUIRED — the two surviving verifier mutants

`07-verifier-mutants-R1-R2.txt`.

**R-1** — deleting the `doctor.CheckSchema` call site:

```
--- FAIL: TestDoctorReportsEveryCheck
    `vizra doctor` does not report "schema".
    reported: configuration, docker compose, database, database version, cache, cache version floor, search
--- and internal/doctor's own tests still pass, which is exactly why this mutant survived before ---
ok  github.com/yegamble/vizra-core/internal/doctor
```

That second line is the point: the verdicts were always covered, the WIRING was
not. `cmd/vizra/doctor.go` now takes its I/O through an injectable `probes`
struct, and `doctor_test.go` runs the REAL `collect()` against fakes — asserting
every check appears, and that each of six real defects both FAILs and exits
non-zero.

**R-2** — removing the timeouts:

```
--- FAIL: TestAPIServerBoundsEveryPhaseOfAConnection
    ReadTimeout is zero. In net/http zero means NO LIMIT, not a sensible default.
    WriteTimeout is zero. ...
    ReadHeaderTimeout (10s) exceeds ReadTimeout (0s); the header budget would never bite
```

### 4. WORDING

Corrected in the round-1 section above and on the PR. Confirmed from the API:
run 35532590902 concluded `failure`; jobs `append-only success`,
`build-test failure`.

### Not done, deliberately

Nothing outside the four items. `api/`, `0001`, `0002` and `0004` untouched; no
queued item started.

## Blockers and handoff
- Free disk ~21 GiB. The libvips-from-tarball image build is the heaviest local
  step; if it cannot complete locally it is run in CI on `ubuntu-24.04` and the
  CI run is the evidence, recorded as such rather than skipped.
- `exiftool` absent — affects VZ-FOUND-007 only (core PR2), not this PR.
