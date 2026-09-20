# ADR-001: Stack pins and licences

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` requires reviewed dependency versions and lockfiles. Vizra ships
images and a compose topology to self-hosters, so a licence obligation inside an
image is one Vizra imposes on operators, and `docs/DEFINITION_OF_DONE.md`
requires the notices preserved. No `go.mod` can be written until the majors, the
tracing path, the cache flavour and the image build are fixed.

## Decision
**Go and HTTP.** Go toolchain line 1.27 (supported lines 1.26 and 1.27). Echo v5
(`github.com/labstack/echo/v5`) ≥ v5.3.1. Satellites: `echo-contrib/v5` v5.0.1 for
`echoprometheus` and `pprof`; its `session` package is not used; `echo-jwt` is not
used at all, because Vizra issues no JWT (ADR-003). Tracing is `otelhttp`
(`go.opentelemetry.io/contrib`) wrapping the Echo server handler plus an in-house
Echo middleware of at most 40 lines setting `http.route` from the matched route;
`labstack/echo-opentelemetry` is adopted only at ≥ 1.0. Echo types stay inside
`internal/http`, and `make ci` greps for `echo.` imports outside it, so the major
version is replaceable in one package.

**Data.** sqlc 1.31.1; golang-migrate with migrations embedded in the binary;
PostgreSQL 18 managed and digest-pinned, EXTERNAL PostgreSQL ≥ 16 accepted and
documented.

**Cache (Q-004, as ratified).** The MANAGED cache container is **Valkey**
(BSD-3-Clause; official image `valkey/valkey`, published for linux/amd64 and
linux/arm64; not a Docker Official Image), pinned by digest on the current stable
line (9.1.x as of 2026-09-15), unconditionally. EXTERNAL is any RESP-compatible
server ≥ 7.2: Valkey ≥ 7.2 (Ubuntu 24.04 ships 7.2.x, Debian 13 ships 8.1.x),
Redis ≥ 7.2, or a managed cloud equivalent; Vizra uses only the Redis 7.2 /
Valkey 7.2 command set and no modules. The client is `go-redis/v9` (v9.22.x,
Vidra precedent). Because go-redis publishes no Valkey support statement and
Valkey publishes no formal protocol-compatibility guarantee, core's `integration`
lane runs as a **two-image matrix** — pinned Valkey plus Redis 7.2.x, which still
receives OSS security releases (7.2.16 on 2026-08-17), the second image switching
to Redis 8 if 7.2 stops receiving fixes — from the first Redis-using code, for
the life of the project. Compose sets `maxmemory` and `allkeys-lru` with a comment
stating why eviction is safe (durable work lives in PostgreSQL); the golden path
must pass after `FLUSHALL`; `backup.sh` refuses to back up the cache and says so;
`doctor` prints the server flavour and version it found.

**Cache licence note (Q-004).** Recorded here as a note, not as a pin: Redis 8 is
RSALv2/SSPLv1/AGPLv3; Redis 7.4 is RSALv2/SSPLv1 only; Redis ≤ 7.2 is BSD-3;
Valkey is BSD-3. The load-bearing reasons for Valkey are BSD-3 across the shipped
topology, distro and cloud availability, and imposing no licence choice on
operators — not a performance or feature claim.

**Image and video.** libvips 8.18.x built from a checksummed source tarball into a
digest-pinned Debian 13 base, because distribution packages cannot pin 8.18;
`govips` v2.18.0 binds it; the loader list (`vips -l`) is recorded in `/version`
and `releases/<tag>.json`. HEIC decode via libheif + libde265 exists only when the
HEIC option image build is selected — one image, flag-gated — and x265 is never in
any image; AVIF uses dav1d/aom. A pinned LGPL `ffmpeg`/`ffprobe` distribution
package serves video poster and probe only. Two builds of one commit must resolve
identical library versions, and the versions each build resolved are recorded in
`releases/<tag>.json` beside the loader list. The libvips layer sits **below** the
Go binary layer in the image, so a Go change never rebuilds libvips and the
codec surface of a tag is stable across rebuilds. No lane that produces derivative
or hash evidence may use a non-libvips decoder; a pure-Go decoder path exists only
to generate fixtures. HEVC patent exposure is recorded as an owner/legal note, not
as an upstream claim — neither libvips nor govips states a patent caveat (Q-034).

**Frontend, clients, host.** Next.js 16.3.x with matching React, TypeScript and
Tailwind; `lucide-react` 1.46.x; `openapi-typescript` 7.13.x for codegen.
`minio-go` v7 is the S3-compatible client; `aws-sdk-go-v2` is not used; the
checksum algorithm is per-provider configurable. Docker Compose ≥ 2.24.4 is the
floor and the installer installs current Docker Engine and the Compose plugin
(5.x).

**Bump policy.** Dependabot, `govulncheck` and `npm audit` lanes propose changes; a
pin changes only through a reviewed PR updating the table below in the same diff.

### Licence table
One row per runtime dependency. Version cells come from two observed sources:
the 2026-09-15 facts file (Go, Echo and its satellites, Valkey, Redis, libvips,
govips, Compose) and `docs/SOURCE_REGISTER.md` §D (sqlc 1.31.1, Next.js 16.3.x,
lucide-react 1.46.x, PostgreSQL 18, observed 2026-09-15); openapi-typescript
7.13.x follows the Vidra pin (`U/scripts/codegen.mjs:40`). Every other version
cell carries `[pin at PR time; verify]`. SPDX ids are not taken from either
source: the **SPDX verification** column records that no SPDX id below is
asserted as verified — each is re-read from the upstream `LICENSE` file when
the pin lands.
Nothing AGPL or GPL is shipped.

| Component | Version | SPDX | SPDX verification | Notice obligation | In image |
|---|---|---|---|---|---|
| Go toolchain | 1.27.x (1.27.1) | BSD-3-Clause | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | none (not distributed) | no |
| `echo/v5` | ≥ v5.3.1 | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| `echo-contrib/v5` | v5.0.1 | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| sqlc | 1.31.1 | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | none (not distributed) | no |
| `pgx` | `[pin at PR time; verify]` | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| golang-migrate | `[pin at PR time; verify]` | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| `go-redis/v9` | v9.22.x | BSD-2-Clause | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| OpenTelemetry Go (`otelhttp`, SDK) | `[pin at PR time; verify]` | Apache-2.0 | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text + NOTICE | yes |
| `minio-go/v7` | `[pin at PR time; verify]` | Apache-2.0 | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text + NOTICE | yes |
| `golang.org/x/crypto` | `[pin at PR time; verify]` | BSD-3-Clause | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| PostgreSQL | 18, digest-pinned `[pin at PR time; verify]` | PostgreSQL | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | upstream notice | yes (MANAGED) |
| Valkey | 9.1.x (9.1.2), digest-pinned | BSD-3-Clause | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes (MANAGED) |
| Redis (CI matrix second image only) | 7.2.x (7.2.16) | BSD-3-Clause | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | none (not shipped) | no |
| libvips | 8.18.x (8.18.6), source tarball | LGPL-2.1-or-later | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | LGPL notice, text, relink/source offer | yes |
| `govips/v2` | v2.18.0 | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| libheif (HEIC decode) | `[pin at PR time; verify]` | LGPL-3.0-or-later | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | LGPL notice, text, relink/source offer | HEIC option image only |
| libde265 (HEIC decode) | `[pin at PR time; verify]` | LGPL-3.0-or-later | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | LGPL notice, text, relink/source offer | HEIC option image only |
| dav1d (AVIF decode) | `[pin at PR time; verify]` | BSD-2-Clause | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| libaom (AVIF encode) | `[pin at PR time; verify]` | BSD-2-Clause with patent grant | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text + patent grant | yes |
| ffmpeg / ffprobe | pinned distro package `[pin at PR time; verify]` | LGPL-2.1-or-later (LGPL build) | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | LGPL notice + text | yes |
| x265 | — | GPL-2+ | not applicable — excluded by decision | — | **never** |
| Debian base | 13, digest-pinned `[pin at PR time; verify]` | per-package (aggregate) | per-package copyright files re-read at pin time (PR1) | Debian copyright files | yes |
| Next.js | 16.3.x | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| React | matching `[pin at PR time; verify]` | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| Tailwind CSS | `[pin at PR time; verify]` | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| `lucide-react` | 1.46.x | ISC | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text | yes |
| `openapi-typescript` | 7.13.x | MIT | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | none (not distributed) | no |
| TypeScript | `[pin at PR time; verify]` | Apache-2.0 | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | none (not distributed) | no |
| Caddy | `[pin at PR time; verify]` | Apache-2.0 | SPDX to be re-verified from the upstream LICENSE file at pin time (PR1) | copyright + text + NOTICE | yes |
| Docker Engine + Compose | floor 2.24.4; 5.x installed | `[pin at PR time; verify]` | host prerequisite, not shipped | host prerequisite | no |

## Consequences
Positive: a BSD/MIT/LGPL-only shipped topology imposes no licence choice on
operators; one digest-pinned libvips makes derivative and hash evidence
reproducible; Echo v5 avoids a forced migration when v4 security support ends
2026-12-31. Negative: source-built libvips lengthens builds and makes Vizra, not
Debian, responsible for libvips CVEs; the route middleware is Vizra's code until
`echo-opentelemetry` reaches 1.0; the cache matrix is permanent, because Valkey
publishes no compatibility guarantee and `go-redis` makes no Valkey claim. Risks:
an unpinned transitive codec could add x265 silently, and the loader-list
assertion is the only detector; an unfilled `[pin at PR time; verify]` cell is a
licence gap. Later milestones must not break: no pixel decode in the api, no x265
in any image, no Echo type outside `internal/http`, no pin changed without this
table, HEIC never default-on.

## Precedent
Copied (survey citations; prefixes per `docs/adr/README.md`): generated code
committed only for sqlc and guarded by `sqlc diff`, and the `make ci` composition
(`C/Makefile:107,190`); the pinned codegen dependency
`openapi-typescript ^7.13.0` (`U/scripts/codegen.mjs:40`).

Unlike Vidra, which records no ADRs — its substitute is a risk register that went
stale (`M/docs/productionization/risks.md:161`) — no Vidra pin traces to a
decision. Vidra validates images by extension allowlist
(`C/internal/media/imagetype.go:22`) with `ffprobe` optional at boot
(`C/cmd/api/main.go:913`) and bounds decoder subprocesses by context alone
(`C/internal/ytdlp/exec.go:38`, its only `Setpgid` site).

## Evidence and ratification
Q-003, Q-004, Q-009, Q-010, Q-017, Q-027, Q-034 in the `docs/OPEN_QUESTIONS.md`
ratification record; versions from
`docs/evidence/research-2026-09-15/ratification-facts.md` §§1–8 and
`docs/SOURCE_REGISTER.md` §D as attributed in the licence table; SPDX ids are
unverified until the pin lands (see the table's verification column).

## Ledger IDs
VZ-FOUND-001, VZ-FOUND-004, VZ-MEDIA-002, VZ-MEDIA-005, VZ-MEDIA-010,
VZ-TOPOLOGY-001, VZ-OPS-005.

## M0 obligations
The M0 foundation issue implements `go.mod` at these pins; the Echo v5 +
`otelhttp` + route-middleware spike with its transcript (one traced route,
`go build`, a span carrying the route); the `internal/http` import guard in
`make ci`; the Dockerfile with libvips from a checksummed tarball and the loader
list emitted at build and served by `/version`, with the libvips layer below the
Go binary layer; the `go-redis` v9 client wiring with a cache readiness probe, the
two-image cache integration matrix (pinned Valkey + Redis 7.2.x) and the
golden-path-after-`FLUSHALL` assertion (Q-004); the frontend pins; `govulncheck`
and dependency-audit lanes. Every `[pin at PR time; verify]` cell is filled there,
not later. Reservation only: the HEIC option image and its licence review
(VZ-MEDIA-010, M3), ffmpeg lanes (VZ-MEDIA-005, M3) and per-provider checksum
configuration (Q-016, BLOCKED).

