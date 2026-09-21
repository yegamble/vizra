# Ratification facts — live verification for Q-003, Q-004, Q-010, Q-017, Q-034 (fetched 2026-09-15)

Produced by an Opus 5 research pass on 2026-09-15 for the open-questions ratification. Every claim carries the URL fetched and the string observed. UNVERIFIED items are labelled; nothing below was filled from memory. Nothing was written to any repository by the research pass.

## 1. Echo web framework (labstack/echo)

FINDING. Echo v5 is stable and released: `github.com/labstack/echo/v5` is at v5.3.1 (2026-07-21), a non-prerelease GitHub release, and v5.0.0 shipped 2026-01-18. Both v5.3.1 and v4.15.4 declare `go 1.25.0` in go.mod. The docs site presents v5 as current ("Echo v5.3.1 — now released", install `go get github.com/labstack/echo/v5`). Latest v4 is v4.15.4 (2026-06-15); upstream states v4 gets security and bug fixes until 2026-12-31, and the "wait until after 2026-03-31 before upgrading" caution has already lapsed.

EVIDENCE.
- https://proxy.golang.org/github.com/labstack/echo/v5/@latest → `{"Version":"v5.3.1","Time":"2026-07-21T16:09:02Z",...,"Ref":"refs/tags/v5.3.1"}`
- https://api.github.com/repos/labstack/echo/releases?per_page=8 → `tag: v5.3.1 | prerelease: False | draft: False | published: 2026-07-21T16:10:56Z`
- https://proxy.golang.org/github.com/labstack/echo/v5/@v/v5.3.1.mod → `module github.com/labstack/echo/v5` / `go 1.25.0`
- https://api.github.com/repos/labstack/echo/releases/tags/v5.0.0 → published 2026-01-18T16:19:13Z; body: "Echo `v5` is a maintenance release with major breaking changes"; "`Context` is now struct instead of interface"; "Drops old logging interface and uses moderm `log/slog` instead"; "Echo `v4` is supported with security updates and bug fixes until 2026-12-31"; "If you are using Echo in a production environment, it is recommended to wait until after 2026-03-31 before upgrading."
- https://proxy.golang.org/github.com/labstack/echo/v4/@latest → `{"Version":"v4.15.4","Time":"2026-06-15T18:23:04Z",...}`; v4.15.4.mod → `go 1.25.0`
- https://pkg.go.dev/github.com/labstack/echo/v5 → `Version: v5.3.1 … Latest … Published: Jul 21, 2026 License: MIT`; "Latest version of Echo supports last four Go major releases and might work with older versions"
- https://echo.labstack.com/ → "Echo v5.3.1 — now released"; `go get github.com/labstack/echo/v5`
- Security context: releases v5.2.0, v4.15.3, v5.2.1, v4.15.4 all fix GHSA-vfp3-v2gw-7wfq — "an encoded path separator (`%2F` or `%5C`) in a static file URL could bypass route-level middleware (e.g. authentication on a sibling route) and disclose static files"

CONFIDENCE: VERIFIED.

## 2. Go toolchain

FINDING. Latest stable is go1.27.1 (released 2026-09-01). Under Go's published policy, two lines are supported: 1.27 (1.27.1) and 1.26 (1.26.8). Echo v5/v4 and all Echo satellite modules require `go 1.25.0`.

EVIDENCE.
- https://go.dev/dl/?mode=json → first entry `"version": "go1.27.1", "stable": true`
- https://go.dev/dl/?mode=json&include=all → `go1.27.1 stable=True`, `go1.27.0 stable=True`, `go1.26.8 stable=True`
- https://go.dev/doc/devel/release → "go1.27.1 (released 2026-09-01)"; policy: "Each major Go release is supported until there are two newer major releases."

CONFIDENCE: VERIFIED.

## 3. Redis vs Valkey — licensing and compatibility

### 3a. Redis licensing
FINDING. Redis 8.x is offered under a tri-license: RSALv2, SSPLv1, or AGPLv3. Redis 7.2 and earlier is BSD-3-Clause. Redis 7.4 is RSALv2 or SSPLv1 (no AGPL option).
EVIDENCE. https://redis.io/legal/licenses/ → "Redis 8 in Redis Open Source and later versions are available under our tri-license … RSALv2, SSPLv1, and AGPLv3."; table rows "7.2 and earlier | Redis | BSD-3-Clause" and "7.4 | Redis Community Edition | RSALv2 or SSPLv1"; "we plan to keep Redis Open Source under the AGPLv3 license".
CONFIDENCE: VERIFIED.

### 3b. Valkey
FINDING. Valkey is BSD-3-Clause; latest stable is 9.1.2 (2026-09-01), with 9.0.6, 8.1.10 and 8.0.11 also maintained. Valkey "was forked from the open source Redis project right before the transition to their new source available licenses"; its first release was 7.2.5. No first-party page states an explicit RESP/API-compatibility or drop-in-replacement claim. Official image `valkey/valkey` (named on the project's download page); there is no Docker Official Image (`library/valkey` → 404).
EVIDENCE.
- https://api.github.com/repos/valkey-io/valkey → `license: {"spdx_id": "BSD-3-Clause"}`
- https://raw.githubusercontent.com/valkey-io/valkey/unstable/COPYING → "BSD 3-Clause License / Copyright (c) 2024-present, Valkey contributors / Copyright (c) 2006-2020, Redis Ltd."
- https://api.github.com/repos/valkey-io/valkey/releases?per_page=6 → `9.1.2 | prerelease: False | 2026-09-01T00:01:31Z`; `9.0.6` (2026-09-01), `8.1.10`, `8.0.11` (2026-08-31)
- https://valkey.io/ → "Valkey is an open source (BSD) high-performance key/value datastore"; "Version 9.1.2, released September 1, 2026"
- https://raw.githubusercontent.com/valkey-io/valkey/unstable/README.md → "This project was forked from the open source Redis project right before the transition to their new source available licenses."; "For compatibility with Redis, we create symlinks from the Redis names (`redis-server`, `redis-cli`, etc.) to the Valkey binaries"
- https://valkey.io/topics/history/ → "the first release, Valkey 7.2.5"
- https://valkey.io/download/ → "Docker Hub ( valkey/valkey ) Tags: valkey/valkey:9.1.2 …"
- https://hub.docker.com/v2/repositories/library/valkey → HTTP 404
CONFIDENCE: PARTIAL — licence, version, image name and fork narrative VERIFIED; an explicit first-party protocol/API-compatibility claim is UNVERIFIED.

### 3c. Go clients and Valkey support
FINDING. `github.com/redis/go-redis/v9` (latest v9.22.0) does not mention Valkey at all (zero README occurrences; support statement covers Redis CE 8.0–8.10). `github.com/valkey-io/valkey-go` (latest v1.0.78) is the Valkey project's own client. `github.com/redis/rueidis` documents Valkey-specific server behaviour without a formal support statement.
EVIDENCE.
- https://raw.githubusercontent.com/redis/go-redis/master/README.md → grep -i valkey: 0 matches; "In `go-redis` we are aiming to support the last three releases of Redis … Redis 8.0 … 8.10"
- https://proxy.golang.org/github.com/redis/go-redis/v9/@latest → `{"Version":"v9.22.0","Time":"2026-08-03T17:39:49Z"}`
- https://raw.githubusercontent.com/valkey-io/valkey-go/main/README.md → "A fast Golang Valkey client that does auto pipelining and supports server-assisted client-side caching."
- https://proxy.golang.org/github.com/valkey-io/valkey-go/@latest → `{"Version":"v1.0.78","Time":"2026-09-15T03:45:49Z"}`
- https://raw.githubusercontent.com/redis/rueidis/main/README.md → "Starting from Valkey 8.1, Valkey server provides the `availability-zone` information …"; "AWS ElastiCache for Valkey 7.2+"
CONFIDENCE: VERIFIED for go-redis and valkey-go; PARTIAL for rueidis.

## 4. Docker Compose `!reset` / `!override`

FINDING. `!override` is officially gated at Docker Compose 2.24.4 and later (docs.docker.com, the docs repo's version-metadata file, and the compose-spec badge). `!reset` carries no documented minimum version on docs.docker.com or the compose-spec, and no Compose release note (285 scanned) mentions it; source tracing puts its first shipping version at Compose v2.18.0 (`ResetProcessor` appears in compose-go v1.13.5, 2023-05-16; Compose v2.17.3 pins v1.13.4, v2.18.0 pins v1.13.5). Compose has left the 2.x line: latest is v5.5.1 (2026-09-03); the last 2.x release was v2.40.3 (2025-10-30).

EVIDENCE.
- https://docs.docker.com/reference/compose-file/merge/ → "Replace value — Requires: Docker Compose 2.24.4 and later"; no version string near "Reset value"
- https://raw.githubusercontent.com/docker/docs/main/data/summary.yaml → `Compose replace file: requires: Docker Compose [2.24.4] and later`; no `reset` entry
- https://raw.githubusercontent.com/compose-spec/compose-spec/main/13-merge.md → badge `compose-v2.24.4` above "### Replace value"; none above "### Reset value"
- https://api.github.com/repos/compose-spec/compose-spec/commits?path=13-merge.md → `2023-04-17 91a00539 introduce ability for override to reset value to null`; `2024-01-26 2865b07b introduce !override`
- compose-go v1.13.4 loader.go: no `reset`; v1.13.5 loader.go line 153 `processor := ResetProcessor{target: &cfg}`; v1.13.5.info → 2023-05-16
- docker/compose v2.17.3 go.mod → compose-go v1.13.4; v2.18.0 go.mod → compose-go v1.13.5 (released 2023-05-16)
- https://api.github.com/repos/docker/compose/releases/latest → `tag: v5.5.1 published: 2026-09-03`; `v5.0.0 | 2025-12-02`; last 2.x `v2.40.3 | 2025-10-30`; 285 release bodies scanned for `!reset` → 0 hits
CONFIDENCE: VERIFIED for `!override` = 2.24.4 and for current/last-2.x versions; PARTIAL for `!reset` (v2.18.0 is a source-traced inference).

## 5. libvips / govips — HEIC/HEIF and AVIF

FINDING. libvips gains HEIC and AVIF via libheif, which must itself be built with codec plugins: HEIC decode = libde265, HEIC encode = x265; AVIF decode = dav1d or aom, AVIF encode = aom / SVT-AV1 / rav1e. Latest libvips is 8.18.6 (2026-08-25); latest govips is v2.18.0, MIT. Neither README contains the word "patent". The transitive licensing constraint: libvips LGPL-2.1-or-later, govips MIT, but the HEIC encoder plugin pulls in x265, which Debian records as GPL-2+. Distro libvips is built with libheif; in Debian 13 and Ubuntu 24.04 HEIC decode (libde265) is a hard dependency while HEIC encode (x265) is only Recommends (Debian 13) or Suggests (Ubuntu 24.04). Distro libvips versions: Ubuntu 24.04 8.15.1 (universe), Debian 13 8.16.1, Ubuntu 26.04 8.18.0.

EVIDENCE.
- https://raw.githubusercontent.com/libvips/libvips/master/README.md → "### libheif / If available, libvips can load and save HEIC and AVIF images. Your libheif (in turn) needs to be built with the correct decoders and encoders."; "HEIC decoders: - libde265 … AVIF decoders: - dav1d … - aom …"; "HEIC encoders: - x265 … AVIF encoders: - aom … - svt … - rav1e"; "libvips is licensed under the [LGPL-2.1-or-later]"; grep -i patent → no match
- https://api.github.com/repos/libvips/libvips/releases?per_page=6 → `v8.18.6 | 2026-08-25`
- https://api.github.com/repos/davidbyttow/govips/releases?per_page=6 → `v2.18.0 | 2026-04-01`; repo licence MIT; https://proxy.golang.org/github.com/davidbyttow/govips/v2/@latest → v2.18.0
- Debian trixie Packages.xz → `libvips42t64 8.16.1-1+deb13u1 Depends: … libheif1 (>= 1.17.0)`; `libheif1 1.19.8-1+deb13u1 Depends: … libheif-plugin-dav1d | libheif-plugin-aomdec, libheif-plugin-libde265; Recommends: libheif-plugin-x265, libheif-plugin-aomenc`
- Ubuntu noble Packages.xz → `libheif1 1.17.6-1ubuntu4 Depends: … libheif-plugin-aomdec | libheif-plugin-dav1d, libheif-plugin-libde265; Recommends: libheif-plugin-aomenc; Suggests: libheif-plugin-x265`; `libvips42t64 8.15.1-1.1build4` (universe)
- https://packages.ubuntu.com/ → libvips-dev: noble 8.15.1-1.1build4, questing 8.16.1-1, resolute (26.04) 8.18.0-1build1, all universe
- https://metadata.ftp-master.debian.org/changelogs/main/x/x265/x265_4.2-3_copyright → `License: GPL-2+`
CONFIDENCE: VERIFIED for codec matrix, versions, licences and distro packaging; UNVERIFIED for any upstream patent caveat (none stated).

## 6. Echo v5 middleware ecosystem

FINDING. `otelecho` has no Echo v5 support and is deprecated: its latest release v0.71.0 (2026-08-26) requires `echo/v4 v4.15.4`, its go.mod header reads "Deprecated: Use github.com/labstack/echo-opentelemetry instead", and no `/v5` module path exists. The replacement `github.com/labstack/echo-opentelemetry` targets v5 but is pre-1.0 (v0.0.3, 2026-07-12). `echo-contrib/v5` (v5.0.1: casbin, echoprometheus, jaegertracing, pprof, session, zipkintracing) and `echo-jwt/v5` (v5.0.2) publish real v5 modules importing `echo/v5`.

EVIDENCE.
- https://proxy.golang.org/go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho/@latest → v0.71.0 (2026-08-26); its .mod → `// Deprecated: Use github.com/labstack/echo-opentelemetry instead.` / `github.com/labstack/echo/v4 v4.15.4`
- …/otelecho/v5/@latest → `not found`
- opentelemetry-go-contrib issues 9003, 9088, 8799, 8457 (Echo v5 support) — all closed
- https://proxy.golang.org/github.com/labstack/echo-opentelemetry/@latest → v0.0.3 (2026-07-12); .mod → `github.com/labstack/echo/v5 v5.2.1` / `go.opentelemetry.io/otel v1.44.0`
- https://proxy.golang.org/github.com/labstack/echo-contrib/v5/@latest → v5.0.1 (2026-02-19); .mod → `github.com/labstack/echo/v5 v5.0.4`; tree: casbin, echoprometheus, jaegertracing, pprof, session, zipkintracing
- https://proxy.golang.org/github.com/labstack/echo-jwt/v5/@latest → v5.0.2 (2026-07-12); .mod → `github.com/labstack/echo/v5 v5.2.1` / `github.com/golang-jwt/jwt/v5 v5.3.1`
CONFIDENCE: VERIFIED.

## 7. Redis 7.2.x / 7.4.x support status

FINDING. Both the 7.2 and 7.4 open-source lines are still receiving security fixes: 7.2.16 and 7.4.11 shipped 2026-08-17 flagged `SECURITY` (ACL key-permission bypass in SORT/GEORADIUS/XREAD; 7.4.11 also fixes an RDB SLOT_INFO memory corruption "which may lead to Remote Code Execution"). The redis.io lifecycle page found covers Redis Software (Enterprise), not Redis Open Source; no OSS-specific EOL policy page was found.

EVIDENCE.
- https://api.github.com/repos/redis/redis/releases/tags/7.2.16 → published 2026-08-17; "Update urgency: `SECURITY`"
- https://api.github.com/repos/redis/redis/releases/tags/7.4.11 → published 2026-08-17; "Update urgency: `SECURITY`"
- Release scan → 7.2.16, 7.2.15, 7.2.14; 7.4.11, 7.4.10, 7.4.9; 8.10.1, 8.8.2, 8.6.6, 8.4.6 (all 2026-08-17)
- https://redis.io/docs/latest/operate/rs/installing-upgrading/product-lifecycle/ → "Redis Software product lifecycle"; "7.4 … November 30, 2026"; "7.2 … February 28, 2026" (Enterprise, not OSS)
CONFIDENCE: VERIFIED that 7.2 and 7.4 still receive OSS security releases; UNVERIFIED: an official Redis Open Source EOL date for 7.2.

## 8. Valkey packaging

FINDING. Ubuntu 24.04 LTS ships valkey-server 7.2.12/7.2.13 (universe); Debian 13 ships valkey 8.1.1+dfsg1-3+deb13u2; Ubuntu 26.04 carries 9.0.x. `valkey/valkey` on Docker Hub publishes linux/amd64, linux/arm64, linux/arm/v7 and linux/ppc64le; it is not a Docker Official Image.

EVIDENCE.
- https://packages.ubuntu.com/search?keywords=valkey → noble (24.04LTS) universe 7.2.12+dfsg1-0ubuntu0.1 [security]; noble-updates 7.2.13; questing 8.1.6/8.1.7; resolute (26.04LTS) 9.0.3 / 9.0.4
- https://api.ftp-master.debian.org/madison?package=valkey&text=1 → `valkey | 8.1.1+dfsg1-3+deb13u2 | stable`; `9.1.1-1 | testing`; `9.1.2-1 | unstable`
- https://hub.docker.com/v2/repositories/valkey/valkey/tags?page_size=100 → `9.1.2 -> ['linux/amd64', 'linux/arm/v7', 'linux/arm64', 'linux/ppc64le']`
- https://valkey.io/download/ → "Docker Hub ( valkey/valkey ) … docker run --rm valkey/valkey:9.1.2"
- https://hub.docker.com/v2/repositories/library/valkey → HTTP 404
CONFIDENCE: VERIFIED.

## Implications for decisions (factual)
- Echo v5 is a legitimate foundation choice: v5.3.1 is a stable tag eight months past v5.0.0, past the upstream-advised production-wait date; v4 security support ends 2026-12-31.
- The Echo v5 gap is observability: `otelecho` is deprecated and v4-only; the v5 path is pre-1.0 `echo-opentelemetry` or in-house middleware (e.g. `otelhttp` at the server boundary).
- `echo-contrib/v5` and `echo-jwt/v5` exist and import `echo/v5`.
- Go 1.26 and 1.27 are the supported lines; Echo requires `go 1.25.0`.
- Redis 8.x is RSALv2/SSPLv1/AGPLv3; 7.4 has no OSI option; ≤ 7.2 is BSD-3; 7.2 and 7.4 still receive OSS security releases. Valkey is BSD-3.
- go-redis makes no Valkey claim; valkey-go is the project's own client; Valkey publishes no explicit RESP/API-compatibility guarantee.
- Ubuntu 24.04 ships Valkey 7.2.x and Debian 13 ships 8.1.x; the `valkey/valkey` image (amd64/arm64) is the way to get a current server on an LTS host.
- `!override` may be required at ≥ 2.24.4 (documented); `!reset` has no documented minimum; Compose is at 5.5.1 and 2.x ended at 2.40.3.
- HEIC encode (x265, GPL-2+) is the packaging trap; HEIC decode (libde265) is a hard dependency of distro libheif.
