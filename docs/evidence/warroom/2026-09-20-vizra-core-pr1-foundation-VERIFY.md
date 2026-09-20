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
