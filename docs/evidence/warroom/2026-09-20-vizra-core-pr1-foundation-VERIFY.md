# Independent verification — vizra-core PR #1 "foundation"

**Verdict: FAIL** (2 BLOCKER findings, 9 lesser findings; CI green, all six demonstrations reproduced)

| | |
|---|---|
| PR | https://github.com/yegamble/vizra-core/pull/1 |
| Head SHA verified | `e45e78454f101ebbf814dbdcaeef0117ec9a30e0` (branch `feat/m0-foundation`, 5 commits, 90 files) |
| Head moved during verification? | No — re-checked at start and end, unchanged |
| Acceptance IDs in scope | VZ-FOUND-001, VZ-FOUND-003, VZ-FOUND-004, VZ-FOUND-005, VZ-FOUND-006 (and VZ-FOUND-002 by the route↔spec lane) |
| Verifier | war-room independent verifier; did not write this code |
| Date | 2026-09-20 |

The builder's plan (`docs/plans/2026-09-20-vizra-core-pr1-foundation.md`) was read as claims only.
Everything below was re-run by me from a clean clone.

---

## 1. Environment

Clean clone, not the builder's checkout:

```
git clone https://github.com/yegamble/vizra-core.git core
git checkout e45e78454f101ebbf814dbdcaeef0117ec9a30e0
```

| Component | Value |
|---|---|
| Host | darwin 25.5.0, arm64 (native, no emulation) |
| Go (host) | go1.26.2 darwin/arm64; `toolchain go1.27.1` in go.mod auto-selected → **all lanes ran on go1.27.1** |
| sqlc | v1.31.1 (matches ADR-001) |
| Docker | 29.8.0 |
| PostgreSQL | `postgres@sha256:86c951e0…3666ae` (the digest CI pins), host port **55432** |
| Valkey | `valkey/valkey@sha256:c123e371…708e1d` (9.1.2), host port **56379** |
| Redis | `redis@sha256:06379549…6e6773c` → reported `v=7.2.16`, host port **56379** |

Containers were named `vizra-pr1-verify-*`, run on non-default ports, and torn down at the end.
Nothing named `vidra-*`, `vizra-pr1-*` (builder), `vizra-user:*` or `vizra-search:*` was touched.

---

## 2. Commands and results

| Lane | Command | Exit | Result |
|---|---|---|---|
| Full gate | `make ci` | 0 | **PASS** — fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, test-race |
| Unit counts | `go test -count=1 -json ./...` | 0 | **545 pass, 0 fail, 0 skip**, 8 packages with tests (authz, cache, config, httpapi, jobs, obs, search, site) |
| Tidy | `make tidy-check` | 0 | PASS |
| Module integrity | `go mod verify` | 0 | `all modules verified` |
| Integration (Valkey 9.1.2) | `make test-integration` | 0 | **564 pass, 0 fail, 0 skip** |
| Integration (Redis 7.2.16) | `make test-integration` | 0 | **564 pass, 0 fail, 0 skip** |
| Authz matrix | `go test -run TestFrozenMatrix -v` | 0 | **315 subtests pass** (21 surfaces × 3 visibilities × 5 viewer classes) |
| Build | `make build` | 0 | `bin/vizra-api`, `bin/vizra-worker`, `bin/vizra` |
| Migrate | `./bin/vizra migrate up` | 0 | `default APPLIED to version 4`; 5 tables incl. `schema_migrations` |
| Local image build | `docker buildx build` | — | **NOT RUN.** `df` showed **12 GiB free** with three builders active; a from-source libvips buildx build plus its cache would plausibly consume most of it. All four image assertions were instead verified from the CI `docker-build` log for this SHA (§5). |

The builder's claimed counts (8 packages, 0 skips, 315 authz cases) are **accurate**.

### GitHub CI on this exact SHA

`gh api repos/yegamble/vizra-core/commits/e45e784…/check-runs`:

```
build-test                                      completed  success
cache-matrix                                    completed  success
cache-matrix-leg (redis, redis@sha256:06379…)   completed  success
cache-matrix-leg (valkey, valkey/valkey@sha…)   completed  success
ci-required                                     completed  success
docker-build                                    completed  success
govulncheck                                     completed  success
GitGuardian Security Checks                     completed  failure   ← triaged separately
```

`ci-required` ran on this SHA and is green. The manifest (`.github/required-checks.txt`:
`build-test`, `cache-matrix`, `govulncheck`, `docker-build`) matches four check runs that
**actually executed** — no listed-but-never-run lane. GitGuardian is not in the manifest and is
being triaged by a separate reviewer; see §7 for what I observed at HEAD.

---

## 3. The six required demonstrations — all reproduced, red then green

Each mutation was applied by me in my own clone, the lane run, then reverted with
`git checkout -- .` and the lane re-run.

**D1 — route without spec → RED.** Added `e.GET("/verifier-unspecified-route", …)` to
`internal/httpapi/server.go`:
```
--- FAIL: TestEveryRouteHasASpecOperation
    cmd/api serves 1 route(s) that api/openapi.yaml does not describe:
      GET /verifier-unspecified-route
```
Reverted → `ok github.com/yegamble/vizra-core/internal/httpapi`. **Right reason.**

**D2 — spec without route → RED.** Added a `/verifier-phantom-operation` GET to `api/openapi.yaml`:
```
--- FAIL: TestEverySpecOperationHasARoute
    api/openapi.yaml describes 1 operation(s) cmd/api does not serve:
      GET /verifier-phantom-operation
--- FAIL: TestM0ContractIsTheFourProbes
```
Reverted → green. **Right reason**, and the M0 four-probe assertion fires as a second net.

**D3 — hand-edited sqlc output → RED.** Inserted a comment line into
`internal/store/sqlcgen/sites.sql.go`; `sqlc diff` printed the unified diff and
`make: *** [sqlc-verify] Error 1`. Reverted → `ok internal/store/sqlcgen matches store/queries + migrations`.

**D4 — production boot refuses dev secrets, real binary → RED.** `./bin/vizra-api` with
`VIZRA_MODE=production` and the three `.env.example` placeholder secrets:
```
vizra-api refused to start.
configuration is invalid (3 problem(s)):
  - DATABASE_URL: must be set
  - VIZRA_MFA_KEY_KEK: production refuses a known development value
  - VIZRA_SESSION_SECRET: production refuses a known development value
```
GREEN half: same binary with freshly generated 48-byte secrets **booted and served**:
```
{"level":"INFO","msg":"vizra-api starting","release":"dev","commit":"e45e78454f10","go":"go1.27.1","mode":"production"}
{"level":"INFO","msg":"vizra-api listening","addr":":8080","metrics_addr":"127.0.0.1:9090"}
```
`/healthz` → 200. `/readyz` → real component status (`database ok`, `cache ok`, `search off`,
`worker degraded` before migrations). `/version` → real build info. I grepped the boot log for each
of the three secrets and for the DSN credential: **no leak**.

**D5 — edited already-merged migration → RED.** Appended a comment to `migrations/0001_sites.up.sql`:
```
FAIL  migrations/manifest.sha256 does not match the files on disk.
      < bad52277…  0001_sites.up.sql
      > 7b82247b…  0001_sites.up.sql
      A CHANGED hash for an existing migration is an append-only violation…
```
Additionally (not claimed, checked anyway) a **new** `0005` containing
`ALTER TABLE sites DROP COLUMN handle;` is caught:
```
FAIL  0005_verifier_destructive.up.sql:1 destructive statement in an up migration
```
Reverted → `ok append-only manifest matches (8 migrations)`.

**D6 — golden path after FLUSHALL → GREEN.** `TestGoldenPathPassesAfterFlushAll` passes against
both cache flavours; the test warms 50 limiter keys, issues a real `FLUSHALL`, sleeps past the 2 s
readiness TTL, re-runs the whole path, and then asserts the two enqueued jobs **survived in
PostgreSQL** (`n != 2` → fail). The red control is built into the test as that durable-state
assertion plus `TestReadinessDegradesWhenTheCacheIsUnreachable`, which dials a dead port (not a
mock). This is a real control, not a tautology.

---

## 4. Surviving-mutant hunt — mutants the builder did not list

Each mutant applied by me, `make ci` (and `make test-integration` where relevant) run, then reverted.

| # | Mutant | `make ci` | Assessment |
|---|---|---|---|
| M1 | authz: let `unlisted` appear in listing surfaces | **killed** | 15 matrix cells red (`profile_grid/unlisted/*`, …) |
| M2 | authz: let a non-owner read `private` on item/derivative/notifications | **killed** | `item_page/private/A`, `/M`, `derivative_url/private/*` red |
| M3 | authz: unknown surface → ALLOW | **killed** | `TestUnlistedSurfaceDenies` red |
| **M4** | **authz: unknown/unset visibility → PUBLIC** | **SURVIVED** | **FINDING 1** — also survived `make test-integration` |
| M5 | jobs: `Enqueue` takes a pool instead of `pgx.Tx` | killed | compile-guard `testdata/enqueue/without_tx.go` must not compile; genuine |
| **M6** | **migrate-lint: drop `COLUMN` from the destructive regex** | **SURVIVED** | **FINDING 3** |
| M7a | HMAC: `MaxClockSkew` widened to ~100 y | killed | `TestVerifyRejects/stale_timestamp`, `TestTimestampWindowAcrossTheMagnitudeRange` |
| M7b/c | HMAC: remove the `MinTimestamp`/`MaxTimestamp` magnitude bound (one site, then both) | survived | **Not a finding** — behaviour-equivalent. `WithinWindow` uses pure int64-second arithmetic, and `ValidateTimestamp` already rejects non-digits, leading zeros/signs and >19 digits, so the magnitude bound is redundant defence-in-depth. The window itself is covered by a 23-case table including `math.MaxInt64`, `math.MinInt64`, Duration-overflow values and year 10000. |
| **M8a** | **doctor: schema-drift check reports `statusOK`** | **SURVIVED** | **FINDING 2** |
| **M8b** | **doctor: delete the cache floor check** | **SURVIVED** | **FINDING 2** |
| **M8c** | **doctor: invalid config reports `statusOK`** | **SURVIVED** | **FINDING 2** |

---

## 5. Chair's questions, answered with evidence

**Q1 — Is authz default-DENY for unknown inputs, and is the fixture really ADR-007 cell for cell?**

*Fixture:* **Yes, cell for cell.** I diffed `internal/authz/testdata/adr007_matrix.tsv` against the
ADR-007 table row by row. All 21 surfaces present, in ADR row order, each with all three visibility
columns expanded to 5 viewer classes = 315 expectations — not a subset. Spot-checks where a
convenient subset would have cheated, and did not:
- row 13 `favorite_rating/private` denies **G** as well as A/M (ADR: "visible to O/S only") — the
  strict reading, even though G can see the item;
- row 19 `export` denies **S** (staff=admin) at every visibility (ADR: "site export by owner role") —
  the fixture header pins `staff role = admin, not site owner` as the base condition;
- row 4 `album_page` correctly drives *album* privacy public/link/private in the three columns
  rather than item visibility, exactly as the ADR's "same rule (not split by item visibility)" says.
`TestFixtureCoversEveryFrozenSurfaceExactlyOnce` pins fixture↔`Actions` agreement. The six
conditions held at base values in the table each have a focused test
(`TestSearchOwnLibraryScope`, `TestOriginalDownloadSetting`, `TestPrivateOriginalRequiresDownloadInGrant`,
`TestIPFSRequiresListedOwner`, `TestSiteExportRequiresOwnerRole`, `TestAlbumPrivacy`,
`TestSitePrivateDeniesAnonymousEverySurface`).

*Default-deny:* **Partially — and the gap is FINDING 1.**
- unknown **Action** → `Deny/surface_not_in_matrix` ✅ (tested, M3 killed)
- unknown non-empty **Visibility** (e.g. `"friends_only"`) → Deny ✅
- unknown **AlbumPrivacy** → Deny ✅; unknown **DownloadSetting** → Deny ✅
- **unset/zero Visibility (`""`) → coerced to `public` → ALLOW** ❌

**Q2 — Do both route↔spec directions fail for the right reason, and does excluding the internal
search contract create a blind spot?**

Both directions fail for the right reason (D1, D2 above, with the exact assertion messages).

**No blind spot.** The exclusion is achieved by *omission, not by filtering*: `TestEveryRouteHasASpecOperation`
enumerates **every** route the real Echo router registers (`serverOperations(t)` builds a server and
reads `e.Routes()`) and checks each against `api/openapi.yaml` only. Nothing subtracts paths from that
enumeration, so if core ever registered an `/internal/v1/*` route it would be reported as undescribed —
D1 empirically confirms an arbitrary new route is caught. `api/search-internal.openapi.yaml` states core
is the **client** and never serves those routes; `vizra-search` is the server and runs its own
both-direction check. `TestInternalOperationsAreNotInThePublicContract` additionally asserts the internal
operations stay out of the public contract.

**Q3 — The fan-in: does `ci-required` really require `cache-matrix`?**

**Yes — the name-mangling hypothesis is refuted.** `cache-matrix` is not the matrix job. The matrix
job was deliberately renamed `cache-matrix-leg`, and a separate **non-matrix aggregate job** named
`cache-matrix` (`build-test.yml:200`) does `needs: cache-matrix-leg` / `if: always()` and fails unless
`needs.cache-matrix-leg.result == 'success'`. The live check-run list for this SHA confirms all three
names exist separately. `fail-fast: false` on the matrix means both legs report independently, and
`needs.*.result` is `success` only if every leg succeeded — so a failed leg turns `cache-matrix` red.

`ci-required` polls `gh api …/check-runs` and matches names with `awk '$1==n'` (exact equality), with a
25-minute deadline. Its conclusion handling is default-deny: only the literal string `success` passes;
`failure`, `cancelled`, `timed_out`, `skipped`, `neutral`, `action_required`, `stale` and "never reported"
all fail. A mangled name would have timed the gate out **red**, not green.

Manifest floor guard: `FLOOR_LANES` = the same four lanes. Deletion → `required lane '<x>' is MISSING`;
commenting-out → `is COMMENTED OUT`; both `exit 1`. Empty manifest → explicit failure. Action pinning is
a 40-hex-SHA regex with **no `actions/*` exemption** (all 10 `uses:` in-tree are SHA-pinned). Runners
restricted to `ubuntu-24.04`. Two weaknesses recorded as FINDING 4 and FINDING 5.

**Q4 — Pins.**

| ADR-001 | Repo at this SHA | Match |
|---|---|---|
| Go 1.27.x (1.27.1) | `toolchain go1.27.1`; lanes and image both ran `go1.27.1` | ✅ |
| Echo v5 ≥ v5.3.1 | `labstack/echo/v5 v5.3.1` | ✅ |
| sqlc 1.31.1 | v1.31.1 (verified locally) | ✅ |
| pgx (pin at PR time) | `jackc/pgx/v5 v5.11.0` | ✅ |
| golang-migrate (pin at PR time) | `v4.20.1` | ✅ |
| go-redis v9.22.x | `v9.22.0` | ✅ |
| otelhttp / otel (pin at PR time) | `v0.71.0` / `v1.46.0` | ✅ |
| PostgreSQL 18, digest-pinned | `postgres@sha256:86c951e0…` | ✅ |
| Valkey 9.1.x (9.1.2), digest-pinned | `valkey/valkey@sha256:c123e371…` | ✅ |
| Redis 7.2.x (CI matrix only) | `redis@sha256:06379549…` → 7.2.16 | ✅ |
| libvips 8.18.x from a checksummed tarball | `ARG VIPS_VERSION=8.18.6`, `ARG VIPS_SHA256=3c41e1d5…`, verified with `sha256sum -c -`; image reports `vips-8.18.6` | ✅ |
| Base image digests | every `FROM` carries `@sha256`; CI asserts it (`ok internal stage vips`) | ✅ |

`go mod verify` → `all modules verified`; `make tidy-check` clean.
**Unused dependencies declared ahead of use: none.** `govips` and `minio-go` are absent from both
`go.mod` and `go.sum` — correct, since `lint-imports` enforces that the decoder is not linked into the
API and M0 decodes nothing. `prometheus/client_golang` **is** used (`internal/jobs/metrics.go`, both
`main.go`). The one direct dependency with no production consumer is `getkin/kin-openapi`
(test-only, `openapi_contract_test.go`) — legal Go, does not ship in the binary; recorded as FINDING 10.

**Q5 — Secrets and logs.**

Nothing sensitive is logged by any path that exists today. I traced every `slog` call site; the values
passed are build info, addresses, durations, job IDs and pre-sanitised error strings. `NewLogger`
hardcodes `slog.LevelInfo`, so there is no debug path. pgx v5.11.0 does not embed the password in
connect errors. My D4 green-half boot log was grepped for all three live secrets and the DSN
credential — clean. `.env.example` ships only `CHANGE-ME-…` placeholders and `.gitignore` excludes
`.env`. Two redaction-layer gaps are recorded as FINDING 6 and FINDING 7 (neither is a live leak).

*CI database reachability:* `build-test.yml` uses `POSTGRES_HOST_AUTH_METHOD: trust` with **no
password**, as a GitHub Actions **service container**. Service containers are attached to the job's own
Docker network and their ports are published only on the ephemeral runner's loopback
(`127.0.0.1:5432`); they are destroyed with the job and are not routable from outside it. Passwordless
is therefore acceptable here. UNVERIFIED: I did not attempt to reach the CI database from outside a
job — that would require credentials and network access I do not have; the assessment rests on the
documented GitHub service-container model plus the workflow using `127.0.0.1`.

**Q6 — Resource bounds.** Mixed; see FINDING 8 and FINDING 9. Good: API graceful shutdown is bounded
and correctly ordered (`context.WithTimeout(context.WithoutCancel(ctx), cfg.ShutdownGrace)`); the
search client bounds its response body at 8 MiB and its health-probe read at 4 KiB and sets a client
timeout; `/readyz` bounds its fan-out at 3 s and has a 2 s single-flight cache; `SQLSearcher` checks
`ctx.Err()` on every method. **Context propagation is clean** — I classified every
`context.Background()`/`context.TODO()` occurrence and **none is on a request path** (all are process
start/stop, CLI entry, or tests); sqlc and cache calls all take and use `ctx`.

**Docker image assertions, read from the CI `docker-build` log for this SHA** (local build NOT RUN, §2):
- `libvips   vips-8.18.6` ✅
- loader list: analyze, csv, gif, jpeg, matrix, png, ppm, rad, raw, tiff, vips, webp (+ save/target
  variants). **No `heifload`, no x265, no jxl, no svgload, no pdfload.** Log line: `no excluded codec is present` ✅
- `image uid: 10001` — the workflow asserts `[ "$uid" != "0" ]`; Dockerfile has `USER 10001:10001` ✅
- layer order: `libvips build step is #10` / `#10 CACHED — a Go-only change reused the libvips layers` ✅
  (the assertion fails closed if the step cannot be found)

**GitGuardian at HEAD.** Not my scope beyond a look. The only high-entropy string I found in the tree
at HEAD is `key_utf8` in `api/search-hmac-testvectors.json` — a **deliberately published test-vector
key**, normative for cross-repo signer conformance and consumed by `internal/search/search_test.go`.
That is not a credential. `grep -rnE '"[A-Za-z0-9+/]{32,}={0,2}"'` over non-test Go found nothing.
The 7 GitGuardian hits are described as historical commits and remain for the security reviewer.

---

## 6. Findings

```
FINDING 1: the authz evaluator fails OPEN on an unset visibility
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/authz/authz.go:~250 (the `vis := resource.Visibility; if vis == "" { vis = VisibilityPublic }` coercion)
             internal/authz/authz_test.go (no case pins this)
  requirements: VZ-FOUND-005; ADR-007 ruling 5 / "Frozen surface × visibility matrix"; ADR-003

Observed:
  The package doc states default deny as a load-bearing, tested property:
  "**Default deny.** An Action not in the frozen matrix denies… A new read
  surface that forgets to add itself therefore fails closed, which is the
  opposite of the failure mode that made Vidra fix the same privacy bug four
  times."

  Decide coerces an EMPTY visibility to public:
        vis := resource.Visibility
        if vis == "" {
                vis = VisibilityPublic
        }

  I probed the real evaluator with a temporary test (written, run, deleted;
  tree left clean). With an ANONYMOUS subject and Resource{OwnerID:"owner-1"}
  — i.e. the zero value for Visibility:

    zero-value Resource  item_page           -> allow (public)
    zero-value Resource  original_download   -> allow (public)
    zero-value Resource  derivative_url      -> allow (public)
    zero-value Resource  embed               -> allow (public)
    zero-value Resource  search              -> allow (public)
    zero-value Resource  explore             -> allow (public)
    zero-value Resource  shared_cache        -> allow (public)
    zero-value Resource  federation_outbound -> allow (public)
    zero-value Resource  count_contribution  -> allow (public)

  An unknown NON-empty visibility correctly denies, as do unknown AlbumPrivacy
  and unknown DownloadSetting — the gap is specifically the zero value.

  Mutant M4 (make ANY unrecognised visibility coerce to public) SURVIVED both
  `make ci` and `make test-integration`: no test pins this input class.

Failure:
  The single most likely programming error in M1 — a Resource built field by
  field that misses Visibility, or a row scanned from a query that did not
  select the visibility column — yields ALLOW to an anonymous viewer on every
  surface, including original_download, federation_outbound, ipfs_publication
  and shared_cache. Those are exactly the surfaces AGENTS.md names
  ("Default-deny authorization covers originals, derivatives, search, counts,
  exports, embeds, feeds, federation, and caches") and the ones where a leak is
  irreversible: a private original published to IPFS or federated out cannot be
  recalled. Nothing is exploitable at this SHA because M0 registers only four
  probe routes — which is precisely why ADR-007's M0 obligation puts the
  evaluator in before any route exists. There is no legitimate source of "" at
  M0: no assets table exists yet, so no DB default is being mirrored.

Perspective:
  photographer | visitor | operator

Recommendation:
  Delete the coercion and fail closed on anything not in the frozen set:
        switch resource.Visibility {
        case VisibilityPublic, VisibilityUnlisted, VisibilityPrivate:
        default:
                return Deny, ReasonVisibilityNotInMatrix
        }
  (a new Reason constant, parallel to ReasonSurfaceNotInMatrix). If a default
  is genuinely wanted at a call site, the CALLER states it; the evaluator must
  not guess "public".

Acceptance criteria:
  - Decide(anonymous, ANY action, Resource{}) returns Deny for all 21 surfaces.
  - Decide(anonymous, ANY action, Resource{Visibility:"friends_only"}) returns
    Deny with the not-in-matrix reason, not the private reason.
  - The owner is also denied on an unset visibility: an absent field is a bug,
    not an ownership question.
  - Re-applying mutant M4 turns `make ci` red.

Tests:
  internal/authz/authz_test.go — add TestUnknownVisibilityDenies, mirroring the
  existing TestUnlistedSurfaceDenies: loop `Actions` × {"", "friends_only"} ×
  {A,M,G,O,S} and require Deny. The harness exists; this is ~20 lines.

Cross-repo implications:
  core: the fix. user: none. search: none — the search projection will call this
  evaluator in M1, so fixing it now prevents an index-side leak.
  meta: VZ-FOUND-005 must not reach VERIFIED until this closes.

Challenge:
  "Nothing calls Decide with an unset Visibility today, so this is theoretical."
  True at this SHA — but the whole justification for landing the evaluator in M0
  ahead of any route is that it fails closed when M1 wires it up, and the
  package doc claims that property in writing. A one-line fix plus one test
  closes it now; discovering it after a federation or IPFS route exists is the
  Vidra four-times bug the comment is about.
```

```
FINDING 2: `vizra doctor` has zero test coverage; every check can be deleted or inverted and CI stays green
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     cmd/vizra/doctor.go:1-297 (whole file); cmd/ contains NO *_test.go at all
  requirements: VZ-FOUND-006; the slice scope statement ("config validation and doctor checks")

Observed:
  `find cmd -name '*_test.go'` → 0 files. `make ci` output confirms:
      ?   github.com/yegamble/vizra-core/cmd/vizra   [no test files]
      ?   github.com/yegamble/vizra-core/cmd/api     [no test files]
      ?   github.com/yegamble/vizra-core/cmd/worker  [no test files]

  Three independent mutants, each applied and reverted by me, ALL SURVIVED `make ci`:
    M8a  the schema-drift branch reports statusOK instead of statusFail
         (add("schema", statusOK, "database at %d, binary embeds %d: %s"…))
    M8b  add(cacheFloorCheck(info)) deleted outright
    M8c  an invalid configuration reports add("configuration", statusOK, "fine")

  For contrast, the config half of the same scope item is well covered:
  internal/config has TestEveryKeyHasATemplateEntry, TestTemplateHasNoKeyNothingReads,
  TestTemplateSecretsAreRefusedInProduction, TestTemplateBootsInDevelopment,
  TestEscapeHatchesAreCommentedOutInTheTemplate, all wired into `make ci`.

Failure:
  "Doctor checks" is half of the first named deliverable of this slice and is
  entirely unverified. A doctor that reports OK on a schema-drifted database, a
  too-old cache server, or an invalid configuration is the fake success state
  AGENTS.md forbids — and doctor is the tool an operator runs precisely when
  they already suspect something is wrong, so a false OK sends them the wrong
  way at the worst moment. Per AGENTS.md, a required test that is missing is not
  PASS.

Perspective:
  operator | instance-admin

Recommendation:
  Extract the check bodies from the printing so they are callable, then add a
  table test per check with a fake/failing dependency. Smallest coherent
  version: make each check a function returning (name, status, detail) and test
  the three that the mutants broke — schema drift (including the
  database-newer-than-binary branch), cache floor, and invalid configuration.

Acceptance criteria:
  - `go test ./cmd/vizra/` runs at least one case per doctor check and is in `make ci`.
  - A drifted schema yields statusFail; a database NEWER than the binary yields
    statusFail with its own message; an unreadable ledger yields statusSkip (not OK).
  - A cache below the 7.2 floor yields a failing status.
  - An invalid configuration yields statusFail and doctor's exit code is non-zero.
  - Re-applying M8a, M8b and M8c each turns `make ci` red.

Tests:
  New cmd/vizra/doctor_test.go. The integration harness that already gives
  internal/integration a real PostgreSQL and cache (VIZRA_TEST_DATABASE_URL /
  VIZRA_TEST_CACHE_URL) can supply the live cases; the config and schema-drift
  cases need no server at all.

Cross-repo implications:
  core: the fix. user: none. search: none.
  meta: VZ-FOUND-006 must not reach VERIFIED on doctor evidence that no test pins.

Challenge:
  "doctor is a diagnostic, not a production path — untested output is low risk."
  It is the operator's primary diagnostic and it is named in the slice scope;
  worse, a diagnostic that lies is more dangerous than no diagnostic, because it
  actively redirects the investigation. The config half of the same deliverable
  was held to a much higher bar in this same PR.
```

```
FINDING 3: migrate-lint's destructive-statement detection is itself unprotected
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/migrate-lint.sh:78 (the `destructive=` regex); no test exercises it
  requirements: VZ-FOUND-003 (negative case: "A DROP COLUMN in *.up.sql fails migrate-lint")

Observed:
  The check works TODAY — I demonstrated it (D5): a new 0005 containing
  `ALTER TABLE sites DROP COLUMN handle;` produced
      FAIL  0005_verifier_destructive.up.sql:1 destructive statement in an up migration
  But mutant M6 — removing `COLUMN` from the alternation at scripts/migrate-lint.sh:78 —
  SURVIVED `make ci` and `make test-integration`. No test feeds migrate-lint a
  known-destructive fixture and asserts a non-zero exit. The same is true of
  scripts/ci-required-guard.sh and scripts/lint-imports.sh: three shell scripts
  carry load-bearing CI semantics and none has a meta-test.

Failure:
  VZ-FOUND-003's negative case is satisfied by the current text of a regex, not
  by anything that keeps it satisfied. A future PR that narrows the pattern —
  deliberately or by a careless edit while adding a new statement kind — passes
  every lane, and the append-only guarantee silently stops covering DROP COLUMN.
  The manifest check would still fire for edits to merged files, but a NEW
  destructive migration would land unnoticed.

Perspective:
  operator | developer

Recommendation:
  Add a fixture-driven meta-test: a testdata directory of tiny migration files,
  each with an expected verdict, run scripts/migrate-lint.sh against it and
  assert the exit code and the matched line. Cover at minimum DROP TABLE, DROP
  COLUMN, DROP CONSTRAINT, TRUNCATE, ALTER … RENAME, ALTER COLUMN … TYPE, and
  the `-- allow-destructive:` escape hatch (which must PASS).

Acceptance criteria:
  - A test exists that fails when any one statement kind is removed from the regex.
  - The `-- allow-destructive: <reason>` escape hatch is covered positively, and
    the bare `-- allow-destructive:` form with no reason does NOT satisfy it.
  - Re-applying M6 turns `make ci` red.

Tests:
  scripts/ are shell; the smallest harness is a Go test in a new
  internal/scripts (or migrations) package that shells out to the script with a
  temp dir — the same shape as the existing compile-guard test in
  internal/jobs/jobs_test.go, which already shells out to `go build`.

Cross-repo implications:
  core: the fix. search: vizra-search has a twin migrate-lint and inherits the
  same gap. user: none. meta: worth recording as a shared CI-hygiene item.

Challenge:
  "The regex is correct now and CODEOWNERS protects the script." CODEOWNERS
  makes the edit visible, not impossible, and the guarding ruleset is documented
  as not yet applied (FINDING 11). Visibility depends on a reviewer noticing a
  one-word change inside a long regex.
```

```
FINDING 4: the ci-guard's "no lane runs an empty test selection" check is vacuous
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.sh:129-135; Makefile:18 (PKGS), :113, :122, :81, :86
  requirements: VZ-FOUND-001; ADR-002 § CI fan-in

Observed:
  The guard greps ONLY .github/workflows/*.yml:
      if grep -rnE 'go test( -[^ ]+)* *$' "$WORKFLOWS"/*.yml >/dev/null 2>&1; then
  No workflow file contains the string `go test` at all. Every real test
  selection lives in the Makefile:
      Makefile:18   PKGS := ./...
      Makefile:113  @$(GO) test -race -count=1 $(PKGS)
      Makefile:122  @$(GO) test -race -count=1 -tags=integration ./...
      Makefile:81/86 use -run 'TestX|TestY' selections
  The guard nonetheless prints, in the run I captured:
      ok    no lane runs an empty test selection

Failure:
  The gate prints a reassuring green line for a condition it never tested.
  Setting PKGS to a single trivial package, or narrowing a `-run` pattern in
  config-template-check or openapi-verify, shrinks what CI actually runs while
  the guard keeps saying the selection is fine. This is the false-positive CI
  that AGENTS.md's review rules name explicitly, and it is more harmful than an
  absent check because it is cited as evidence.

Perspective:
  developer | operator

Recommendation:
  Point the check at the Makefile as well as the workflows, and make it assert
  the positive: that the test-race lane's package selection is `./...` and that
  each `-run` lane's pattern is non-empty. Alternatively delete the check and
  the claim, rather than keep a line that asserts more than it verifies.

Acceptance criteria:
  - Changing Makefile PKGS to a single package turns `make ci` red with a named error.
  - Emptying any `-run` pattern turns `make ci` red.
  - The guard no longer prints an `ok` line for a file class it did not read.

Tests:
  Same meta-test harness as FINDING 3.

Cross-repo implications:
  core: the fix. user/search: both repos carry a ci-required-guard twin — check
  whether the same vacuous grep was copied. meta: yes, worth a sweep.

Challenge:
  "It is defence-in-depth; the real protection is CODEOWNERS." Defence-in-depth
  that reports success without testing anything is worse than no layer, because
  the war room reads that `ok` line as evidence.
```

```
FINDING 5: the guard's continue-on-error detection misses the expression form
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.sh:117-124
  requirements: VZ-FOUND-001; ADR-002 § CI fan-in

Observed:
      if grep -rnE '^\s*continue-on-error:\s*true' "$WORKFLOWS"/*.yml
  Literal `true` only. `continue-on-error: ${{ github.event_name == 'pull_request' }}`
  is valid GitHub Actions, evaluates to true on exactly the event the gate runs
  on, and is not matched. Zero occurrences in-tree today, so no live bypass.
  Related, same file: the "resolves to a job" check (:103-113) does NOT verify
  the job's workflow is triggered on pull_request, although the file header
  (:21) claims it does — a lane whose trigger was removed would hang the fan-in
  to its 25-minute timeout rather than produce the named error the guard promises.

Failure:
  A required lane can be made unable to fail, through a form the guard does not
  see, while the guard reports "no continue-on-error on any lane".

Perspective:
  developer | operator

Recommendation:
  Match any non-empty value — `^\s*continue-on-error:\s*\S` — and allow-list the
  literal `false`. Separately, make the resolvable check assert an `on:` block
  containing `pull_request`, or soften the header comment to match the code.

Acceptance criteria:
  - `continue-on-error: ${{ … }}` on any lane turns `make ci` red.
  - `continue-on-error: false` remains accepted.

Tests:
  Same meta-test harness as FINDING 3.

Cross-repo implications:
  core: the fix. user/search: same guard twin. meta: sweep.

Challenge:
  "Nobody would write that." The guard exists precisely for the case where
  somebody does, under deadline pressure, to get a red lane past the gate.
```

```
FINDING 6: slog.LogValuer attributes bypass the redaction layer entirely
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/obs/log.go:85-110 (redactAttr), :3-4 (the claim), internal/obs/log_test.go
  requirements: VZ-FOUND-006 / VZ-OPS-005

Observed:
  The package doc claims the rule is "enforced in the logger so a call site that
  passes a secret cannot put it in a log line." redactAttr switches on
  a.Value.Kind() over KindString, KindGroup and KindAny, then falls through:
        return a          // KindLogValuer lands here, untouched
  Record.Attrs does not resolve LogValuer; the inner JSONHandler resolves it
  AFTER redactAttr has returned the attr unchanged. Reproduced in an isolated
  probe that copies the layer verbatim:
        A control: plain string attr  "dsn_value":"postgres://[redacted]@db.internal:5432/vizra"
        B LogValuer attr              "conn":"postgres://vizra:sup3rs3cret@db.internal:5432/vizra"
        F LogValuer via WithAttrs     "bag":"postgres://vizra:sup3rs3cret@…"
        G LogValuer through With()    "conn":"postgres://vizra:sup3rs3cret@…"
  NO type in the repo implements LogValue today (grep: zero hits), so there is
  no live leak at this SHA.

Failure:
  LogValuer is the idiomatic Go way to attach a credential-bearing value to a
  log line, and it is the one path the layer does not cover. The invariant the
  redaction story rests on is not true as written, and the test named
  TestRedactionOfEveryValueClass does not cover this class despite its name.

Perspective:
  operator | developer

Recommendation:
  One line: `a.Value = a.Value.Resolve()` before the Kind switch, plus a test
  case with a LogValuer type.

Acceptance criteria:
  - A LogValuer whose LogValue() returns a DSN with a password is redacted in
    the emitted JSON, including via With() and WithAttrs().
  - TestRedactionOfEveryValueClass covers KindLogValuer.

Tests:
  internal/obs/log_test.go — extend the existing table with a LogValuer case.

Cross-repo implications:
  core: the fix. search: vizra-search has its own logger; check for the twin.
  user: none. meta: none.

Challenge:
  "No type implements LogValue, so nothing leaks." Correct today; the finding is
  that the guarantee is claimed and does not hold, and the first type that
  implements it will not trip any test.
```

```
FINDING 7: the secret-key redaction list is exact-match and misses the project's own key spellings
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/obs/log.go:20-26 (secretKeys), :85 (exact lookup)
  requirements: VZ-FOUND-006 / VZ-OPS-005

Observed:
  secretKeys lists "secret", "token", "hmac_key", "database_url"; the lookup is
  secretKeys[strings.ToLower(a.Key)] — exact, not substring. From the same probe:
        "session_secret":"kQ9x2Lm7ZrT4pW8vB1nH6jY3cF5dA0sE"
        "search_hmac_key":"kQ9x2Lm7ZrT4pW8vB1nH6jY3cF5dA0sE"
        "access_token":"kQ9x2Lm7ZrT4pW8vB1nH6jY3cF5dA0sE"
  session_secret and search_hmac_key are the natural attribute spellings for
  VIZRA_SESSION_SECRET and VIZRA_SEARCH_HMAC_KEY. The valuePatterns free-text
  fallback cannot help: a raw 32-byte secret matches none of its regexes.

Failure:
  The most likely attribute names for this project's own secrets are not
  covered. No live leak — nothing logs them today — but the layer is one
  log call away from one.

Perspective:
  operator

Recommendation:
  Match on substring against a small set of stems (secret, token, key, password,
  dsn, url-with-credentials), or invert to an allow-list of loggable keys.

Acceptance criteria:
  - session_secret, search_hmac_key, mfa_key_kek and access_token all redact.
  - A deliberately non-secret key such as request_id still logs in full.

Tests:
  internal/obs/log_test.go table extension.

Cross-repo implications:
  core: the fix. search: twin logger. user: none. meta: none.

Challenge:
  "Substring matching will over-redact useful fields like route_key." Real, and
  the answer is the allow-list variant; either way the current list is wrong.
```

```
FINDING 8: the public API server sets no ReadTimeout and no WriteTimeout
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     cmd/api/main.go:113-118; also cmd/api/main.go:102-106 and cmd/worker/main.go:72-76 (metrics servers)
  requirements: VZ-FOUND-006; AGENTS.md ("bound request, file, decoder, subprocess, and queue resources")

Observed:
        apiSrv := &http.Server{
                Addr:              cfg.ListenAddr,
                Handler:           srv.Handler(),
                ReadHeaderTimeout: 10 * time.Second,
                IdleTimeout:       120 * time.Second,
        }
  ReadTimeout absent — the body phase is unbounded. WriteTimeout absent —
  IdleTimeout governs only the gap BETWEEN requests, not an in-flight response.
  MaxHeaderBytes absent (falls back to Go's 1 MB default).

Failure:
  A client that sends headers and then dribbles a body, or that stops reading a
  response, holds a connection and goroutine indefinitely. M0 registers only
  four GET routes with no body reader, so nothing is reachable today — this is a
  foundation-PR hole that the first POST handler inherits silently, which is
  exactly the class of thing a foundation PR exists to get right.

Perspective:
  operator

Recommendation:
  Set ReadTimeout and WriteTimeout (and an explicit MaxHeaderBytes) on all three
  servers, sourced from config so an operator can tune them for large uploads
  when the upload path lands.

Acceptance criteria:
  - apiSrv has non-zero ReadTimeout, WriteTimeout and MaxHeaderBytes.
  - A slow-body client is disconnected within the configured ReadTimeout.

Tests:
  internal/integration — a test that opens a socket, writes headers, then stalls,
  and asserts the connection closes within the budget.

Cross-repo implications:
  core: the fix. search: vizra-search serves the internal contract and needs the
  same audit. user: none. meta: none.

Challenge:
  "No route reads a body yet, so there is nothing to bound." The connection and
  goroutine are consumed regardless of whether a handler reads the body.
```

```
FINDING 9: VIZRA_MAX_INTERNAL_BODY_BYTES is an operator-settable knob that does nothing in core
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/config/config.go:66,195,201-203; internal/config/keys.go:54; .env.example:74;
             api/search-internal.openapi.yaml:297,332; internal/search/remote.go:122,150
  requirements: VZ-FOUND-004 / VZ-FOUND-006

Observed:
  The key is parsed, range-validated (>= 1024) and documented as
      "Cap on an internal search request body, enforced before the body is read."
  and the published internal contract specifies a 413 for exceeding it. But
      grep -rn "MaxInternalBodyBytes"  → only config.go:66,195,201
      grep -rn "BodyLimit|MaxBytesReader" → NONE FOUND
  No middleware enforces any body limit anywhere in core. In core's defence,
  core is the CLIENT of /internal/v1/* and never serves those routes, so the 413
  is vizra-search's obligation; but the knob ships in CORE's template, and core's
  own response cap (8 MiB, remote.go) is hardcoded rather than reading this key.
  Note TestTemplateHasNoKeyNothingReads does not catch this, because the key IS
  read — just never used.

Failure:
  An operator can set this in core's .env, see it validated at boot, and believe
  they changed a limit. Nothing changes. That is the dead-control pattern
  AGENTS.md names.

Perspective:
  operator | instance-admin

Recommendation:
  Pick one: (a) move the key to vizra-search where the 413 is actually served
  and drop it from core's template; or (b) keep it in core and have
  internal/search/remote.go use it as the response-body cap instead of the
  hardcoded 8 MiB. Either way the keys.go doc string must describe what the key
  does in the repo that ships it.

Acceptance criteria:
  - Either the key is absent from core's template, or changing it observably
    changes core's behaviour, proven by a test.
  - The doc string in keys.go and .env.example matches the enforcement that exists.

Tests:
  internal/search — a test that sets the key low and asserts the oversize
  response is refused, if option (b).

Cross-repo implications:
  core: the fix. search: owns the 413 for the server side; confirm it enforces it.
  user: none. meta: none.

Challenge:
  "The contract is shared, so documenting the limit in core is correct." The
  contract can document it; core's own .env template offering a knob that does
  nothing in core is the part that misleads.
```

```
FINDING 10: lesser observations, recorded without individual blocks
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     as listed below
  requirements: VZ-FOUND-004, VZ-FOUND-006

Observed / Failure:
  a) internal/jobs/worker.go:249,261,270,281 — CompleteJob/DeadLetterJob/RetryJob/
     FailJob record outcomes on the CANCELLED parent ctx, while the handler runs
     on context.WithoutCancel. On SIGTERM a job that succeeded fails to record,
     the lease expires and the sweep redelivers it — contradicting the comment
     two lines above the drain Wait(). Handlers are documented idempotent, so this
     is duplicated work, not corruption. No drain test exists.
  b) internal/jobs/worker.go:194-196 — the drain is a bare inFlight.Wait() with no
     deadline and never consults cfg.ShutdownGrace; a SIGTERM can block up to
     VIZRA_JOB_TIMEOUT (default 5m).
  c) internal/db/db.go:31-43 — no MaxConns, no connect timeout, no statement_timeout /
     lock_timeout / idle_in_transaction_session_timeout. The pool ceiling is the
     host's core count and is invisible to the operator; cmd/api boot passes a
     deadline-free signal context, so a blackholed database host can hang boot.
  d) internal/httpapi/probes.go:264-273 — /schemaz runs a DB query per request with
     no cache and no rate limit, while /readyz was given a 2 s single-flight cache
     for exactly that reason. No rate-limiting middleware is registered at all;
     FallbackLimiter.Allow has zero non-test callers.
  e) internal/cache/ratelimit.go:108-116 — the "Bounded memory" comment is false
     within a window: the sweep deletes only EXPIRED entries, so distinct keys
     arriving faster than one window elapses grow the map unboundedly, and the
     sweep re-scans the whole map on every call above 4096.
  f) internal/httpapi/server.go:152 + middleware.go:80-82 — otelhttp is installed
     and routeAttributeMiddleware guards on span.IsRecording(), but no
     TracerProvider is ever configured and otel/sdk is not in go.mod, so
     IsRecording() is always false and the http.route attribute is never set.
     Similarly VIZRA_CORS_ALLOWED_ORIGINS is fail-secure validated but no CORS
     middleware exists.
  g) .env.example:31 — DATABASE_URL=CHANGE-ME-generate-with-openssl-rand-base64-32
     fails config validation ("must be a postgres:// or postgresql:// DSN"), and it
     is wrong advice besides (a DSN is not generated with openssl rand).
     TestTemplateBootsInDevelopment does not catch it because it overwrites the
     value before asserting — the test proves "the template boots once you replace
     its DSN", not what its name says.
  h) internal/authz/authz.go — inside the kindListing branch, the guard
     `if action == ActionSharedCache && vis != VisibilityPublic` is unreachable:
     the preceding `if vis != VisibilityPublic` has already returned. Harmless
     (fails closed) but dead, and ReasonNotSharedCacheable is therefore never
     emitted.
  i) internal/config/config.go:41 — comment says "see Redacted"; there is no
     Redacted method and no String() on Config.
  j) cmd/vizra/doctor.go:251 and cmd/vizra/migrate.go:51 print with fmt.Printf and
     never pass through obs.Redact, although obs.Redact is exported for exactly
     that purpose. internal/migrate/migrate.go:169,183 return unredacted errors,
     and its redact() is an exact substring replace that cannot match a DSN
     already rewritten to pgx5:// by normalizeDSN.
  k) go.mod:12 — getkin/kin-openapi is a direct require with exactly one importer,
     internal/httpapi/openapi_contract_test.go. Legal Go and it does not ship in the
     binary, but it is the only declared dependency with no production consumer;
     a one-line comment in go.mod would save a future reader the search.

Recommendation:
  Address (a) and (c) before the first real job handler and the first real query
  path; the rest can be swept. (a) is the one with a user-visible consequence
  today (duplicated work on every SIGTERM of a busy worker).

Acceptance criteria:
  - (a) outcome recording uses a context that survives shutdown; a drain test
    asserts a job completing during SIGTERM records exactly once.
  - (c) MaxConns and a connect timeout are configurable and defaulted.

Tests:
  internal/jobs — a drain test; internal/integration for the pool settings.

Cross-repo implications:
  core: all of the above. user/search: none.

Challenge:
  Individually each is small; collectively they are the difference between a
  foundation that constrains M1 and one that M1 has to go back and fix.
```

```
FINDING 11: the gate is not yet enforceable against the PR it gates
Severity:    SHOULD (owner action, not a builder defect)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .github/CODEOWNERS (references /.github/expected-ruleset.json, which does not exist)
  requirements: VZ-FOUND-001; ADR-002 § Branch protection items 9-10

Observed:
  CODEOWNERS states plainly that the ruleset making review mandatory "is applied
  by the repository owner after PR1 lands, because ci-required must exist before
  it can be a required check". Consequences at this SHA: ci-required.yml runs
  ./scripts/ci-required-guard.sh FROM THE PR'S OWN CHECKOUT, and the workflows
  are `on: pull_request` (head-supplied), so a PR that rewrites the guard to
  exit 0 defeats the FLOOR, RESOLVABLE, NO-OPT-OUT and NO-EMPTY checks in one
  diff. CODEOWNERS makes that visible; only a ruleset makes it blocking. The
  referenced /.github/expected-ruleset.json is absent, so there is no committed
  artifact to diff the applied protection against.

Failure:
  This is the documented bootstrap order and is not the builder's error. It is
  recorded so the chair does not read green CI on this SHA as tamper-proof, and
  so the ruleset and the expected-ruleset.json artifact are not forgotten after
  merge.

Perspective:
  operator | developer

Recommendation:
  After PR1 merges: apply the branch ruleset requiring ci-required and CODEOWNERS
  review, and commit .github/expected-ruleset.json so drift is diffable.

Acceptance criteria:
  - ci-required is a required status check on the default branch.
  - .github/expected-ruleset.json exists and matches the applied ruleset.

Tests:
  A workflow step diffing `gh api …/rulesets` against the committed file.

Cross-repo implications:
  core / user / search: all three need the same ruleset. meta: chair tracks it.

Challenge:
  "AGENTS.md already forbids VERIFIED on CI evidence alone until the ruleset
  exists, so this is covered." It is covered by policy; recording it keeps the
  policy from being quietly dropped once CI looks green.
```

---

## 7. What I verified as sound (so it is not re-litigated)

- **Authz fixture fidelity** — cell-for-cell transcription of all 21 ADR-007 rows, 315 cases,
  including the strict readings (G denied on private aggregates; admin denied site export).
  Mutants M1, M2, M3 all killed.
- **Route↔spec, both directions**, failing for the right reason; internal search contract excluded
  by omission, not by filtering, so no blind spot for core's own routes.
- **CI fan-in** — `cache-matrix` is a genuine non-matrix aggregate job; a failed leg turns it red;
  `ci-required` default-denies skipped/cancelled/neutral/timed-out/never-ran.
- **Manifest floor guard** — rejects deletion, commenting-out and unpinned actions (no `actions/*`
  exemption); restricts runners to `ubuntu-24.04`.
- **HMAC signer** — window thoroughly covered by a 23-case magnitude table; 24 negative vectors
  published in `api/search-hmac-testvectors.json` and asserted by tests; M7a killed.
- **Job enqueue transactionality** — enforced by the compiler (`Enqueue` takes `pgx.Tx`), with a
  must-not-compile negative fixture that the test suite actually builds.
- **All ADR-001 pins**, `go mod verify`, tidy; **no dependency declared ahead of use**
  (govips and minio-go correctly absent).
- **Secrets** — nothing sensitive in the boot log of the real production binary; no hardcoded
  credentials; no mock data on a production path; `.env` gitignored.
- **Context propagation** — no `context.Background()`/`TODO()` on any request path.
- **Docker image** — libvips 8.18.6 from a checksum-verified tarball, all `FROM`s digest-pinned,
  uid 10001, no heif/x265/jxl/svg/pdf loaders, libvips layer below the Go layer.
- **`/readyz` returning 200 while `degraded`** — I initially flagged this and then withdrew it: it is
  deliberate (Q-028), documented, and tested in both directions
  (`TestReadyzDatabaseDownIs503`, `TestReadyzCacheDownIs200Degraded`,
  `TestReadyzUnavailableBeatsDegraded`). Not a fake success state.

## 8. Cleanup

All mutations reverted; `git status --porcelain` empty and `git rev-parse HEAD` =
`e45e78454f101ebbf814dbdcaeef0117ec9a30e0` at the end of the run. Clone, logs, binaries and the
`vizra-pr1-verify-*` containers removed. No source, test, workflow, manifest, baseline or budget file
was modified in the repository; this evidence file is the only file I wrote.

**Verdict: FAIL.** CI is green on this SHA and all six demonstrations reproduce, but FINDING 1
(authz fails open on an unset visibility, contradicting the evaluator's own documented load-bearing
property, with a surviving mutant proving no test pins it) and FINDING 2 (`vizra doctor`, half of the
slice's first named deliverable, has zero tests and three surviving mutants) are blocking. Neither is
exploitable at this SHA; both are one-file fixes plus tests.

PASS/FAIL here is a verification verdict only. Merge and any ledger transition to VERIFIED are the
chair's to record.

---
---

# Re-verification at 4f8d0fc

**Verdict: PASS.** Both of my blockers are **CLOSED**. CI is green on this SHA. No blocking finding is open.

| | |
|---|---|
| PR | https://github.com/yegamble/vizra-core/pull/1 |
| Head SHA verified | `4f8d0fc207f94a2a516607d167fcf69abd7a2148` (branch `feat/m0-foundation`) |
| Previous verdict | FAIL at `e45e78454f101ebbf814dbdcaeef0117ec9a30e0` — does not carry over |
| Delta verified | `git diff --shortstat e45e784 4f8d0fc` → **117 files, +3706 −435**, 2 commits (`866eeb8`, `4f8d0fc`) — matches the coordinator's figures |
| Head moved during re-verification? | No — re-checked at start and end, unchanged |
| Environment | Fresh clone, second scratch dir. darwin arm64 native. go1.27.1 via `toolchain`. sqlc v1.31.1. `postgres@sha256:86c951e0…` on port 55432; `valkey/valkey@sha256:c123e371…` and `redis@sha256:06379549…` (reported `v=7.2.16`) on port 56379. Containers `vizra-pr1-v2-*`, torn down after. |
| Date | 2026-09-20 |

## R1. Lanes, counts and skips

| Lane | Exit | Result |
|---|---|---|
| `make ci` | 0 | PASS — now 10 lanes; floor is **5** (`append-only` added) |
| `go test ./...` (unit) | 0 | **865 pass, 0 fail, 0 skip** |
| `make tidy-check` | 0 | PASS |
| `go mod verify` | 0 | `all modules verified` |
| `make test-integration` — PostgreSQL 18 + **Valkey 9.1.2** | 0 | **900 pass, 0 fail, 0 skip** |
| `make test-integration` — PostgreSQL 18 + **Redis 7.2.16** | 0 | **900 pass, 0 fail, 0 skip** |
| `TestFrozenMatrix` | 0 | **315 subtests pass** — unchanged |

The builder's claim of **900 tests, 0 skips, 315 matrix cases unchanged** is accurate on both cache flavours.

New test packages since e45e784: `internal/doctor` and `scripts`. `cmd/api`, `cmd/vizra`, `cmd/worker` still carry no test files — see Finding R-1 and R-2.

## R2. My blocker 1 — authz fail-open: **CLOSED**

*Fixture integrity.* `internal/authz/testdata/adr007_matrix.tsv` is **byte-identical** to e45e784:
```
sha256 at 4f8d0fc : 37115e003abf780d69c2c7c6d67f80871f7f7d51e7e98be9b4ea5243421adb92
sha256 at e45e784 : 37115e003abf780d69c2c7c6d67f80871f7f7d51e7e98be9b4ea5243421adb92
```
The 315 frozen expectations were not relaxed to accommodate the fix.

*The fix.* The coercion is gone. `Decide` now switches on visibility and denies anything outside the frozen set with `ReasonVisibilityUnknown`; `AlbumPrivacy` gets the same treatment.

*My own probe* (temporary test, written, run, deleted; tree left clean) — zero-value `Resource{OwnerID:"owner-1"}` and unrecognised `Visibility("scheduled")`, each swept across all 21 Actions × 5 viewer classes:
```
zero-value Resource     : 105/105 cells denied with visibility_unknown
unrecognised visibility : 105/105 cells denied with visibility_unknown
HideExistence("")        = true      HideExistence("scheduled") = true
HideExistence("private") = true      HideExistence("public")    = false
HideExistence("unlisted")= false
unknown album privacy -> deny (visibility_unknown)
UNSET   album privacy -> deny (visibility_unknown)
```
Every one of the nine surfaces that previously allowed an anonymous viewer — `item_page`, `original_download`, `derivative_url`, `embed`, `search`, `explore`, `shared_cache`, `federation_outbound`, `count_contribution` — now denies.

*Mutants, all re-applied by me and reverted:*

| Mutant | Result |
|---|---|
| **M4** unrecognised visibility → public | killed — `TestUnknownVisibilityDenies` |
| **N1** restore `if vis == "" { vis = VisibilityPublic }` | killed — `TestUnknownVisibilityDenies` |
| **N2** restore `if priv == "" { priv = AlbumPublic }` | killed — `TestUnknownAlbumPrivacyDenies` |
| **N3** `HideExistence` returns false for unknown | killed — `TestHideExistenceForAnythingNotPublicOrUnlisted` |

## R3. My blocker 2 — doctor untested: **CLOSED** (one residual)

The decision logic moved to `internal/doctor` (13 test functions, +384 test lines). `cmd/vizra/doctor.go` genuinely calls it — `doctor.CheckConfig`, `CheckDatabase`, `CheckSchema`, `CheckCache`, `CheckSearch`, `CheckCompose`, `doctor.Report` — so these are not tested functions nobody calls.

*Status **and** exit code, verified with the real binary:*
```
BROKEN config → FAIL config: DATABASE_URL must be set
                FAIL config: VIZRA_MFA_KEY_KEK must be at least 32 bytes in production; got 8
                FAIL config: VIZRA_SESSION_SECRET must be at least 32 bytes in production; got 8
                SKIP docker compose  (docker not on PATH — reported as "not run", never as a pass)
                4 check(s): 3 failed, 1 not run.     exit = 1
LIVE good stack → OK configuration / database / database version 18.6 / schema version 4 /
                  cache redis 7.2.16 / cache version floor / search off
                  8 check(s): 0 failed, 1 not run.   exit = 0
```
`Report` returns an error whenever `Failed > 0`; `main.go` maps that to `os.Exit(1)`. `TestSkipIsNeverAPassButDoesNotFailTheRun` pins the SKIP semantics.

*Mutants, all re-applied by me:*

| Mutant | Result |
|---|---|
| **D-M1** schema-drift branch reports `StatusOK` | killed — `TestCheckSchema/behind:_the_code_may_be_reading_columns_that_do_not_exist` |
| **D-M2** cache floor check always OK | killed — `TestCheckCacheFloor/7.1.9`, `/6.2.14` |
| **D-M3** invalid config reports OK | killed — `TestCheckConfigReportsEveryProblemAndFails` |

Residual: see **Finding R-1** — the check *functions* are pinned, but nothing pins that `cmd/vizra` still wires each of them in.

## R4. The other seats' items, as mutation checks

All applied by me in my own clone and reverted. "killed" = the named test went red.

| # | Mutation | Lane | Result |
|---|---|---|---|
| **a1** | `ClaimJob`: drop `AND attempts < max_attempts` | integration | **SURVIVED** — see Finding R-3 |
| **a2** | Sweep: `SET state = 'queued'` always (no dead-lettering) | integration | killed — `TestACrashLoopingJobDeadLettersAndDoesNotBlockTheQueue`, `golden_test.go:855: cycle 2: sweep failed: ERROR: new row for relation "jobs" violates check constraint "jobs_terminal_finished" (SQLSTATE 23514)` |
| **a3** | **both reverted (the chair's prescription)** | integration | killed — same test, **same constraint violation**, exactly as the chair predicted |
| **b** | claim index → `(created_at)`, non-partial | integration | killed — `TestClaimPlanDoesNotSortTheBacklog` **and** `TestClaimIndexExcludesTerminalRows` |
| **c1** | remove `jobs_payload_bounded` | integration | killed — `TestEnqueueRefusesAnUnboundedPayload/a_raw_INSERT_is_rejected_by_the_database` |
| **c2** | remove `jobs_kind_bounded` | integration | killed — `…/an_oversized_kind_and_correlation_id_are_rejected` |
| **c3** | remove `jobs_correlation_bounded` | integration | killed — same subtest |
| **c4** | remove `jobs_last_error_bounded` | integration | killed — `TestSchemaConstraintsAreEnforced` |
| **c5** | remove `sites_singleton` | integration | killed — `TestSitesIsASingleton` |
| **c6** | remove `audit_events_ip_prefix_shape` | integration | killed — `TestSchemaConstraintsAreEnforced` |
| **d** | outcome writes derive from the cancellable `ctx` | integration | killed — `TestGracefulShutdownRecordsTheOutcomeOfAnInFlightJob` |
| **e1** | `knownPublishedSecrets` emptied | ci | killed — `TestProductionRefusesPublishedTestKeys/as_the_search_HMAC_key`, `/as_VIZRA_SESSION_SECRET` |
| **e2** | value-bearing hatch falls back to truthiness | ci | killed — `TestValueBearingEscapeHatchIsRefusedWhenPresent/"alice"`, `/"owner"` |
| **e3a** | `obs.Redact(truncate(s))` — truncate before redact | ci | **SURVIVED** — see Finding R-4 (not load-bearing) |
| **e3b** | redaction removed from `safeError` | ci | killed — `TestLastErrorIsRedactedBeforeItIsStored/DSN_password`, `/presigned_S3_URL` |
| **e4** | search client follows redirects again | ci | killed — `TestARedirectIsNeverFollowedAndNoSignatureLeaks`, `TestPingDoesNotFollowRedirects` |
| **e5** | `securityHeadersMiddleware` removed | ci | killed — `TestEveryRouteCarriesHardeningHeaders/GET_/healthz`, `/readyz` |
| **e6** | `ReadTimeout`/`WriteTimeout` removed | ci | **SURVIVED** — see Finding R-2 |

The 404 path *is* covered: `TestErrorResponsesCarryHardeningHeaders` drives `/does-not-exist` and `/v1/nope/deeper` through the real handler and asserts the headers survive the error handler.

Two mutants I initially mis-built and re-ran correctly, recorded for honesty: `s/recCtx/ctx/g` accidentally shadowed `ctx` with a detached context (preserving the fix); and a first `safeError` mutant failed only on an unused-import vet error. Both were redone so they compiled and exercised the real behaviour, with the results above.

## R5. The append-only lane

*The two throwaway runs, confirmed independently by `gh`:*
```
run 35532576593  branch=throwaway/append-only-negative  head=fa97e3f   job append-only: FAILURE
  ##[error]a migrations/manifest.sha256 line was REMOVED or CHANGED.
    -af8405894ae1c130235453835ddbefef872b551115963da3fe525d3a1c74de07  0002_jobs.up.sql
    ok    append-only manifest matches (8 migrations)      ← self-check green, merge-base diff still red
run 35532590902  branch=throwaway/append-only-positive  head=567acc7   job append-only: SUCCESS
    ok    append-only manifest matches (10 migrations)
    append-only: ok (2 migration file hash(es) added, none removed or changed)
```
Both recorded `merge base: 4f8d0fc…`, the SHA under review. The negative run proves the **merge-base diff**, not the manifest self-check, is what enforces the freeze — the self-check printed `ok` because the throwaway regenerated the manifest. Both branches are now deleted (`gh api …/branches` lists only `feat/m0-foundation` and `main`).

One correction to the builder's wording: run 35532590902's **job** `append-only` passed, but the **run** concluded `failure` because `build-test` failed on `sqlc-verify` drift from the throwaway migration — unrelated to the lane, but "run 35532590902 PASSED" is inaccurate as written (Finding R-9).

*Mechanism.* `.github/workflows/build-test.yml` job `append-only`: `fetch-depth: 0`, `git fetch` the base ref, `base=$(git merge-base origin/$base_ref HEAD)`, then three checks — a removed/changed `manifest.sha256` hash line (`git diff "$base" … | grep -E '^-[0-9a-f]{64} '`), a deleted-or-renamed migration (`--diff-filter=DR`), and `migration-manifest.sh check`.

*Limits, as asked:*
- **Only base-branch migrations are protected.** A migration added *and* edited inside the same PR produces no `-` line and no `DR` entry, so it passes. Defensible (it was never merged), but the freeze begins at merge, and the *final* content is what gets frozen.
- **`merge_group` is in the triggers** of all four workflows. But no merge queue exists: `gh api …/rulesets` returns `403 Upgrade to GitHub Pro or make this repository public`. And on `merge_group` `github.base_ref` is empty, so the fallback resolves to the **default branch `main`**, while all current work targets `feat/m0-foundation` — a latent hole if a queue is ever enabled on a non-default base (Finding R-6).
- **The lane can be edited in the PR it gates.** `on: pull_request` runs workflows from the PR head, and no check inspects whether the workflow, the scripts or the manifest were touched. CODEOWNERS covers the right paths (`/.github/`, `/scripts/`, `/migrations/**`, `/api/**`, `/internal/authz/`, `/internal/config/`, …) but is unenforced — see Finding R-5.
- **A renamed migration fails**, caught twice: `--diff-filter=DR` reports it, and the manifest line is removed-and-re-added. Note `migrate-lint.sh`'s filename regex and sequence check would *not* catch a rename on their own, and `migration-manifest.sh check` would not either once regenerated — the merge-base diff is the control.
- **A deleted migration fails** via the same two checks.
- **Floor list and manifest both include `append-only`** — `FLOOR_LANES` in `scripts/ci-required-guard.py:79` and `.github/required-checks.txt` (`append-only, build-test, cache-matrix, govulncheck, docker-build`). The guard printed `all 5 floor lane(s) are present and non-optional`.

## R6. Migrations changed in place — verified by direct SQL

Applied `0001`–`0004` to a **fresh** PostgreSQL 18 database (`./bin/vizra migrate up` → `APPLIED to version 4`), then asserted by raw SQL. Every rejection is by the **named constraint**, and each group has a passing control:

```
=== sites singleton ===
second sites row                     REJECTED [unique constraint "sites_singleton"]
=== jobs bounds ===
control: a normal job                ACCEPTED
8 MB payload                         REJECTED [check constraint "jobs_payload_bounded"]
5000-char kind                       REJECTED [check constraint "jobs_kind_bounded"]
100k-char correlation_id             REJECTED [check constraint "jobs_correlation_bounded"]
just under 64 KiB payload            ACCEPTED            ← the bound is not over-tight
5000-char last_error                 REJECTED [check constraint "jobs_last_error_bounded"]
=== ip_prefix must REJECT full addresses ===
203.0.113.47, 192.168.1.42, 2001:db8::1,
2001:0db8:abcd:0012:0000:0000:0000:0001,
10.0.0.1/32, 2001:db8::1/128          all REJECTED [audit_events_ip_prefix_shape]
=== ip_prefix must ACCEPT legitimate prefixes ===
203.0.113.0, 203.0.113.0/24, 10.0.0.0/24, 192.168.1.0,
2001:db8::, 2001:db8::/48, 2001:db8:abcd::/48, 2001:db8::/64,
2001:0db8:abcd:0012::, 2001:db8:abcd:1234::/64, fd00::/48,
0.0.0.0, 255.255.255.0/24, 1.2.3.0/24, NULL   all ACCEPTED
```
So the CHECK is **not** too tight for the canonical prefixes a truncation helper emits. It does refuse `::ffff:0:0`, `::`, `/56`, `/25` and **uppercase** (`2001:DB8::/48`). The accepted set (`/24`, `/48`, `/64`, lowercase) is stated verbatim in the migration's own comment, so the narrowing is deliberate and documented — recorded as Finding R-8 only because it is now frozen and constrains the M1 helper.

`0003`'s header no longer overclaims: it states that the application role can still UPDATE or DELETE, that the `BEFORE UPDATE OR DELETE` trigger and retention path land in M1 alongside the users FK, and that `actor_user_id` has no FK yet. That matches what the schema actually enforces.

## R7. Test-change ruling — **no AGENTS.md violation**

Verified independently:
```
$ git diff --numstat e45e784 4f8d0fc -- '*_test.go' | awk '$2>0'
171  3  internal/config/config_test.go        ← the ONLY test file with deletions
$ git diff --diff-filter=D --name-only … -- '*_test.go'      → (empty)
$ git diff … -- '*_test.go' | grep -c '^+.*t\.Skip'          → 0
```
The three removed lines are one fixture literal and two comment lines:
```
-	return strings.Repeat("Aa1Bb2Cc3Dd4", (n/12)+1)[:n]
-			// A falsey value is not a refusal: an operator may leave the key
-			// present and set to 0 in a shared template.
```
- **The literal.** `strings.Repeat("Aa1Bb2Cc3Dd4", 3)[:32]` is the `internal/search` `testKey`, which the new exact-match denylist now refuses. Keeping it as the *passing* production baseline would have made `validProduction()` unloadable and turned every negative test in the file into a vacuous pass. It is replaced by a different literal, guarded by `TestTheTestBaselineIsNotAPublishedSecret`, and — decisively — the old literal is now asserted to be **rejected**: `config.go:176` lists it in `knownPublishedSecrets`, and `config_test.go:337` runs `requireProblem(t, key, strings.Repeat("Aa1Bb2Cc3Dd4", 3)[:32], key)`. Coverage of that string went from "passes" to "must be refused" — strictly stronger.
- **The two comments.** No assertion was removed. The `env[h.Name]="false"` must-boot assertion survives verbatim, now gated on `!h.RefuseIfPresent`. That gating *is* the chair's Finding 3: the old assertion asserted that `VIZRA_DEV_AUTOLOGIN_USER=false` **must** boot, which cemented the hole. It is replaced by `TestValueBearingEscapeHatchIsRefusedWhenPresent`, which refuses ten values including `"0"`, `"false"`, `"off"` and `" "`, while `TestEveryEscapeHatchIsRefusedInProduction` was kept rather than replaced.

Ruling: **legitimate**. No assertion weakened, no case deleted, no skip added, no test file deleted. The other eight test files are pure additions (+1438 / −0).

## R8. Guard evasion — every spelling red

Each injected into the **floor lane `build-test`**, then reverted:

| Mutation | Guard |
|---|---|
| `continue-on-error: true` | RED — `floor lane 'build-test' … carries continue-on-error` |
| `continue-on-error: "true"` | RED |
| `continue-on-error: True` | RED |
| `continue-on-error: on` | RED |
| `continue-on-error: ${{ github.event_name == 'pull_request' }}` | RED |
| `continue-on-error: false` | RED — refused on **presence**, per the chair's item 12 |
| `pull_request` trigger removed | RED — `floor lane 'append-only' … is not triggered on pull_request` |
| `PKGS := ./internal/buildinfo` | RED — `PKGS is './internal/buildinfo', not './...'` |
| `PKGS :=` (emptied) | RED |
| a `-run` pattern emptied | RED — `1 -run pattern(s) are empty` |

This closes my round-1 **FINDING 4** (vacuous "empty test selection" check — the guard now parses the Makefile) and **FINDING 5** (`continue-on-error` spellings). My round-1 **FINDING 3** is also closed: re-applying mutant **M6** (removing `COLUMN` from migrate-lint's destructive regex) is now killed by `TestMigrateLintFixtures/drop-column`; `scripts/scripts_test.go` adds fixture-driven meta-tests for migrate-lint, the guard, and lint-imports.

## R9. CI on 4f8d0fc, and secrets

```
append-only                       completed  success
build-test                        completed  success
cache-matrix                      completed  success
cache-matrix-leg (redis, …)       completed  success
cache-matrix-leg (valkey, …)      completed  success
ci-required                       completed  success
docker-build                      completed  success
govulncheck                       completed  success
GitGuardian Security Checks       completed  failure   ← historical branch commits, triaged
```
All five required lanes **executed** and are green, `ci-required` ran on this SHA, and the manifest and the guard's floor list both contain `append-only`.

*Docker assertions, read from the `docker-build` log for this SHA* (run 35532562186): `libvips vips-8.18.6`; tarball fetched and verified with `sha256sum -c -` against `3c41e1d5458081bfa4a5bc54e116c46259c75c6760a18027764555632b9dda3e`; `no excluded codec is present` (loader list unchanged — jpeg/png/gif/webp/tiff/ppm/rad/raw/csv/matrix/analyze/vips, **no heif, x265, jxl, svg or pdf**); `image uid: 10001`; `libvips build step is #9` / `#9 CACHED — a Go-only change reused the libvips layers`. **Local image build: NOT RUN.** `df` showed 18 GiB free — above the 10 GiB threshold, so it was permitted — but I chose not to run it: a from-source libvips buildx pass plus cache would consume several GiB of a disk shared with three active builders, and every assertion is verifiable from the CI log for this exact SHA.

*`.gitguardian.yaml`* (new): five exclusions, **each a single named file, none a directory or glob, each with a written reason** — `README.md` (loopback `vizra:vizra`), `internal/obs/log_test.go` (redaction inputs), `internal/site/site_test.go` (DSN parser fixture), `internal/search/search_test.go` (port-1 credential URL), `api/search-hmac-testvectors.json` (published vector, with the file stating the exclusion is not the control — `internal/config` refuses the value by exact match). The file explicitly refuses a `*_test.go` glob.

*Nothing credential-shaped is new at this head.* I scanned the added lines of the 117-file delta. The only credential-shaped additions are the two `knownPublishedSecrets` **denylist** entries (values the code now refuses), redaction **test vectors** (`hunter2`, `s3cr3tpw`, a synthetic `X-Amz-Signature=…`), comment prose, SHA-256 file checksums in `manifest.sha256`, and digest/SHA action pins. **No real credential; nothing to rotate.** Note `internal/jobs/jobs_test.go` and `internal/doctor/doctor_test.go` carry redaction fixtures but are *not* in the ignore manifest — under-inclusive (noisy), never hiding.

## R10. Findings at 4f8d0fc

None blocking. My two blockers are closed; these are residuals and carried-forward items.

```
FINDING R-1: the doctor check functions are pinned, but nothing pins that cmd/vizra still calls them
Severity:    SHOULD
Confidence:  high
Affected:    repo vizra-core; cmd/vizra/doctor.go:63,84,94,111,121; cmd/ has no *_test.go
             requirements: VZ-FOUND-006
Observed:    Deleting the CheckSchema call site — `results = append(results, doctor.CheckSchema(
             migrate.Probe(ctx, pools.Default(), embedded)))` — passes `make ci` green. I then
             built the mutated binary and ran it against the live stack: `vizra doctor` output
             contains the string "schema" ZERO times. The check vanishes silently.
             The companion CheckCache deletion died only on gofmt, not on any test.
Failure:     The chair's "a tested function nobody calls is not a fix" concern is closed for the
             functions but not for the wiring. A check can still be dropped from the command with
             CI green — the operator simply stops being told about schema drift.
Perspective: operator | instance-admin
Recommendation: One test in cmd/vizra (or an exported collect() in internal/doctor) asserting the
             set of check NAMES the command produces against an expected list.
Acceptance:  Deleting any doctor call site from cmd/vizra turns `make ci` red naming the check.
Tests:       New cmd/vizra/doctor_wiring_test.go, table of expected check names.
Cross-repo:  core only.
Challenge:   "The functions are the risky part; the call list is obvious on review." The call list
             is exactly what a refactor drops silently, and it is 5 lines to pin.
```

```
FINDING R-2: ReadTimeout/WriteTimeout are set but not pinned by any test
Severity:    SHOULD
Confidence:  high
Affected:    repo vizra-core; cmd/api/main.go:125-126
             requirements: VZ-FOUND-006 (chair's item 13)
Observed:    The fix is present and correct — ReadTimeout: 30s, WriteTimeout: 30s. But removing
             both lines SURVIVES `make ci` (mutant e6). cmd/api has no test files, so the server
             construction is unverified. This is the one item of the round whose code landed but
             whose regression guard did not.
Failure:     The chair required Read/WriteTimeout together with the hardening headers; the headers
             got TestEveryRouteCarriesHardeningHeaders and the timeouts got nothing. A later
             refactor of the server block drops them silently, restoring my round-1 FINDING 8.
Perspective: operator
Recommendation: Move the http.Server construction into a small constructor in internal/httpapi
             and assert the four timeout fields, or add a slow-body integration test.
Acceptance:  Removing ReadTimeout or WriteTimeout turns `make ci` red.
Tests:       internal/httpapi — assert the constructed server's timeout fields are non-zero.
Cross-repo:  search: vizra-search serves the internal contract and wants the same audit.
Challenge:   "Field assertions are tautological." They are — and they are exactly the right shape
             for a value whose only failure mode is going missing.
```

```
FINDING R-3: ClaimJob's attempts guard is redundant-only defence
Severity:    NIT
Confidence:  high
Affected:    repo vizra-core; store/queries/jobs.sql:59
Observed:    Dropping `AND attempts < max_attempts` from ClaimJob alone SURVIVES the integration
             suite (mutant a1). Reverting the sweep alone (a2), and reverting BOTH (a3), each go
             red with `violates check constraint "jobs_terminal_finished"` — the chair's predicted
             failure. So the property is carried by the sweep's dead-lettering; the ClaimJob guard
             is belt-and-braces that no test distinguishes.
Failure:     None today. Recorded so nobody reads a3's red as proof that BOTH halves are pinned.
             The same shape as the HMAC magnitude bound in my round-1 report.
Perspective: developer
Recommendation: Optional — a test that exhausts attempts without the sweep running and asserts
             ClaimJob skips the row. Or accept it as documented redundancy.
Acceptance:  Either a test distinguishes the two halves, or a comment says the guard is redundant.
Tests:       internal/integration, alongside the crash-loop test.
Cross-repo:  none.
Challenge:   "Defence in depth need not be individually tested." Agreed — hence NIT, not a defect.
```

```
FINDING R-4: TestASecretStraddlingTheTruncationBoundaryIsRedacted does not straddle the boundary
Severity:    NIT
Confidence:  high
Affected:    repo vizra-core; internal/jobs/jobs_test.go:151-165
Observed:    The fixture builds prefix = 36 + 1980 + 1 = 2017 bytes before the secret, but
             truncate() cuts at 2000. The secret therefore starts 17 bytes PAST the cut and is
             removed wholesale — it never straddles anything. Consequently mutant e3a
             (obs.Redact(truncate(s)) — truncate BEFORE redact, the ordering the chair explicitly
             required) SURVIVES `make ci`.
             I built a genuinely straddling input (prefix 1940, secret spanning bytes 1977-2031)
             and ran it against both orderings. Neither leaks:
               redact-then-truncate : "…&X-Amz-Signature=[redact… (truncated)"
               truncate-then-redact : "…&X-Amz-Signature=[redacted] (truncated)"
             because obs.Redact's patterns are prefix-anchored and still match a truncated tail.
             So the ordering is genuinely not load-bearing — the code is correct either way.
Failure:     No security consequence. But the test's name asserts more than its fixture proves,
             and the chair's acceptance criterion ("a secret spanning bytes 1995-2010 is redacted,
             not half-stored") is not actually exercised. Per AGENTS.md, a test that claims more
             than it verifies is worth correcting.
Perspective: developer
Recommendation: Change the prefix from 1980 to ~1940 so the secret really spans the cut. Keep the
             assertion as is; it will still pass, and will then mean what it says.
Acceptance:  The fixture's secret starts before byte 2000 and ends after it.
Tests:       internal/jobs/jobs_test.go, one constant.
Cross-repo:  none.
Challenge:   "The ordering doesn't matter, so the test doesn't either." The redaction is correct;
             the claim on the tin is what is wrong, and it costs one number to fix.
```

```
FINDING R-5: the gate cannot be enforced on this repository's current plan
Severity:    SHOULD (owner action — escalates round-1 FINDING 11)
Confidence:  high
Affected:    repo vizra-core; .github/CODEOWNERS:8-11
             requirements: VZ-FOUND-001; ADR-002 items 9-10
Observed:    CODEOWNERS says the ruleset "is applied by the repository owner after PR1 lands".
             But `gh api repos/yegamble/vizra-core/rulesets` returns
               403 "Upgrade to GitHub Pro or make this repository public to enable this feature."
             The repository is private, owner type User, free plan. Branch protection and merge
             queues are unavailable. So there are no required checks, CODEOWNERS is an unenforced
             text file, and `ci-required` — though green — gates nothing mechanically. The lane,
             the guard script and the manifest are all editable by the PR they gate.
Failure:     Not a builder defect and not new code — but stronger than round 1 recorded. It is not
             merely "not applied yet"; on this plan it CANNOT be applied. Per AGENTS.md no ledger
             entry may reach VERIFIED on CI evidence alone while this holds — which is precisely
             why this independent verification exists and why PASS here is not VERIFIED.
Perspective: operator | developer
Recommendation: Owner decision: upgrade the plan, make the repo public, or record explicitly that
             the war-room merge authority rests on independent verification rather than on
             enforced branch protection until then.
Acceptance:  Either rulesets return 200 with ci-required required, or the limitation is recorded
             in CODEOWNERS and the board.
Tests:       A workflow step diffing `gh api …/rulesets` against a committed expectation.
Cross-repo:  user / search: same plan, same limitation.
Challenge:   "AGENTS.md already covers this." It covers the policy; the plan limitation is a new
             fact that makes the policy load-bearing indefinitely rather than until PR1 lands.
```

```
FINDING R-6: the merge_group base fallback resolves to the default branch, not the PR's base
Severity:    NIT (latent)
Confidence:  high
Affected:    repo vizra-core; .github/workflows/build-test.yml (append-only, base_ref fallback)
Observed:    On merge_group, github.base_ref is empty, so the lane falls back to
             github.event.repository.default_branch = main. All current work targets
             feat/m0-foundation. If a merge queue were enabled on a non-default base, every
             migration that landed on feat/m0-foundation since it forked would look like a fresh
             ADD, so edits to them would not be caught.
Failure:     Dormant — no merge queue exists (see R-5). Becomes real the day one is enabled.
Perspective: developer | operator
Recommendation: Derive the base from the merge-queue ref (refs/heads/gh-readonly-queue/<base>/…)
             rather than defaulting to the default branch, or fail loudly when base_ref is empty.
Acceptance:  A merge_group run resolves the same merge base a pull_request run would.
Tests:       scripts/ meta-test over the base-resolution shell, or a fixture run.
Cross-repo:  user / search carry the same lane shape once they adopt it.
Challenge:   "Unreachable today." Yes — recorded so enabling a queue does not silently open it.
```

```
FINDING R-7: lesser observations
Severity:    NIT
Confidence:  high
Affected:    repo vizra-core
Observed / Failure:
  a) .github/expected-ruleset.json is owned by CODEOWNERS but does not exist — so there is still
     no committed artifact to diff applied branch protection against (carried from round 1).
  b) internal/obs/log.go still does not call a.Value.Resolve(), so slog.LogValuer attributes
     bypass redaction (my round-1 FINDING 6, NOT in the chair's checklist, still open). No type
     implements LogValue today, so there is no live leak; the stated invariant remains false.
  c) secretKeys was broadened this round (now covers kek, mfa_key_kek, hmac_key, cache_url,
     session, api_key, authorization, cookie, signature, private_key) but is still EXACT match,
     so the natural spellings `session_secret` and `search_hmac_key` remain uncovered
     (my round-1 FINDING 7 — partially addressed).
  d) The audit_events_ip_prefix_shape CHECK is now frozen and accepts only lowercase /24, /48 and
     /64 forms; 2001:DB8::/48, ::ffff:0:0, :: , /56 and /25 are refused. The accepted set is
     documented in the migration comment, and Go's netip.Prefix.String() emits lowercase, so the
     M1 truncation helper will comply — recorded only because a frozen CHECK is permanent.
  e) jobs.state is NOT NULL with no default, so every INSERT must supply it. Correct but worth
     knowing; it is what made my first raw-SQL control row fail.
Recommendation: (a) commit the file when the ruleset can be applied; (b) one line plus a test case;
  (c) substring stems or an allow-list; (d) and (e) no action.
Acceptance:  As in round 1 for (b) and (c).
Cross-repo:  search carries a twin logger for (b) and (c).
Challenge:   None of these blocks the round; (b) is the one that will bite eventually.
```

```
FINDING R-8: evidence wording — "run 35532590902 PASSED" overstates what passed
Severity:    NIT
Confidence:  high
Affected:    repo vizra (meta); the builder's transcripts and the plan summary
Observed:    gh api confirms run 35532590902 concluded FAILURE. Its append-only JOB succeeded; its
             build-test job failed on sqlc-verify drift caused by the throwaway migration
             (ThrowawayProbe in models.go). The positive proof is sound — but the claim as written
             would not survive a reader checking the run.
Failure:     An evidence claim that is refuted by one gh call weakens the rest of the record.
Perspective: developer
Recommendation: Reword to "the append-only JOB passed in run 35532590902; the run itself failed on
             unrelated sqlc drift from the throwaway migration."
Acceptance:  The plan and transcripts state job-level, not run-level, conclusions.
Tests:       n/a.
Cross-repo:  meta only.
Challenge:   "Pedantic." The whole point of the throwaway pair is that someone can re-check it.
```

## R11. Round-1 findings: disposition

| Round-1 finding | Status at 4f8d0fc |
|---|---|
| **1** authz fails open on unset visibility (BLOCKER) | **CLOSED** — 105/105 + 105/105 deny; 4 mutants die; fixture byte-identical |
| **2** `vizra doctor` zero coverage (BLOCKER) | **CLOSED** — internal/doctor tested, 3 mutants die, exit codes correct; residual R-1 |
| **3** migrate-lint destructive regex unprotected | **CLOSED** — `TestMigrateLintFixtures/drop-column` kills mutant M6 |
| **4** "empty test selection" check vacuous | **CLOSED** — guard parses the Makefile; PKGS and `-run` mutants red |
| **5** `continue-on-error` spellings | **CLOSED** — bare/quoted/capitalised/`on`/expression all red; refused on presence |
| **6** LogValuer bypasses redaction | **OPEN** (not in the chair's checklist) — R-7(b) |
| **7** secretKeys exact-match | **PARTIALLY** — list broadened, still exact-match — R-7(c) |
| **8** no Read/WriteTimeout | **CODE FIXED, UNTESTED** — R-2 |
| **9** `VIZRA_MAX_INTERNAL_BODY_BYTES` dead knob | not in the chair's checklist; unchanged |
| **10** lesser observations (worker ctx, drain, pool) | worker `recCtx` and bounded drain **DONE** (mutant d dies); pool tuning unchanged |
| **11** gate not enforceable | **WORSE THAN RECORDED** — R-5 (403 on this plan) |

## R12. Cleanup

All mutations reverted; `git status --porcelain` empty and `git rev-parse HEAD` = `4f8d0fc207f94a2a516607d167fcf69abd7a2148` at the end of the run. Second clone, logs, binaries, the `fresh` database and the `vizra-pr1-v2-*` containers removed. Nothing named `vidra-*` or belonging to other agents was touched. No source, test, workflow, manifest, migration, baseline or budget file was modified in the repository; this evidence file remains the only file I wrote.

**Verdict for 4f8d0fc: PASS.** Blocker 1 **CLOSED**, blocker 2 **CLOSED**, CI green on this SHA with all five required lanes executed, all six original demonstrations still covered by their tests, every chair-required change reproduced by mutation except the three recorded as R-1/R-2/R-3, and no blocking finding open.

PASS is a verification verdict only. Merge, and any ledger transition to VERIFIED, are the chair's to record — and R-5 means VERIFIED still cannot rest on CI evidence alone.
