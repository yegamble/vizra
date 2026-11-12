# ADR-010: AVIF through libheif with AV1 codecs only (amends ADR-001)

## Status
Accepted (owner) 2026-11-12, decision #9 (`docs/warroom/OWNER-DECISIONS.md`, "2026-11-12" item 9; question in `docs/warroom/OWNER-INBOX.md` under "### 4a"). This ADR **amends** ADR-001 in part. ADR-001 stays Accepted and is not edited. Where the two disagree, this ADR wins.

## Date
2026-11-12

## Context
ADR-001 ("libvips" paragraph and its licence table) treats AVIF and HEIC as two separate paths. It says "HEIC decode via libheif + libde265 exists only when the HEIC option image build is selected" and "AVIF uses dav1d/aom". The vizra-core image build therefore leaves out libheif and fails if `vips -l` lists a heif loader. That cannot work: libvips has **no** AVIF path of its own. It reads and writes AVIF only through its `heifload`/`heifsave` operations, which use libheif, and dav1d and libaom are libheif's codec plugins, not a separate libvips path. So the image ADR-001 describes has no AVIF at all, and VZ-MEDIA-001 cannot be built as written. The vizra-core builder found this at M1 (inbox 4a).

The charter still needs AVIF in the default image. `AGENTS.md` and ADR-001 still need HEVC (libde265 decode, x265 encode) kept out of the default image, for patent and licence reasons. x265 is GPL and stays out of every image.

## Decision
1. **libheif is in the default image, built from source with AV1 codecs only.** It is built from the checksummed upstream release tarball (`strukturag/libheif`, release `v1.23.7` published 2026-10-26 was the newest when this was written; the exact version and SHA-256 are pinned in the vizra-core PR that builds it, `[pin at PR time; verify]`), below the Go layer, the same way libvips is built.
2. **The libheif codec set is fixed.** The CMake options below were checked in `CMakeLists.txt` at tag `v1.23.7`:
   - on: `WITH_DAV1D` (AV1 **decode** through dav1d) and `WITH_AOM_ENCODER` (AV1 **encode** through libaom);
   - off: `WITH_LIBDE265`, `WITH_X265`, `WITH_KVAZAAR`, `WITH_FFMPEG_DECODER` and every other HEVC or VVC codec option (`WITH_UVG266`, `WITH_VVDEC`, `WITH_VVENC`);
   - off: `WITH_AOM_DECODER`, so dav1d is the only AV1 decoder.
   - The encoder is **libaom**, not SVT-AV1. Both are packaged for Debian 13 (trixie): `libaom-dev 3.12.1-1+deb13u1` and `libsvtav1enc-dev 2.3.0+dfsg-1`, checked on packages.debian.org on 2026-11-12. The image already installs `libaom-dev` and `libdav1d-dev` (`libdav1d-dev 1.5.1-1`), and their versions are recorded in the image's `apt-versions.txt`. One encoder is enough, and ADR-001's licence table already covers libaom. SVT-AV1 is not added.
3. **Debian's libheif package is not used.** In trixie, `libheif1 1.23.6-2~deb13u1` hard-depends on `libheif-plugin-libde265` and recommends `libheif-plugin-x265` (packages.debian.org, checked 2026-11-12). Installing it would bring HEVC decode into the default image.
4. **Defaults: AVIF on, HEIC/HEVC off.** The default image decodes and encodes AVIF. It cannot decode HEIC/HEVC. HEIC is still opt-in under VZ-MEDIA-010: libde265 is added only in the HEIC option image (one image, flag-gated, as ADR-001 says). x265 is in **no** image (ADR-001 unchanged).
5. **The image check changes.** It was "no heif loader". It is now "**heif loader present, no HEVC codec**". The build fails if `vips -l` has no `heifload`/`heifsave`. It also fails if the libheif build lists any HEVC (or VVC) decoder or encoder, or if a libde265 or x265 library is linked into or installed in the default image. Both results are written beside the loader list in `/version` and `releases/<tag>.json`.
6. **Licence table.** libheif (LGPL-3.0-or-later; upstream `COPYING` says "distributed under the terms of the GNU Lesser General Public License") moves from "HEIC option image only" to **every image**. Its obligations are the ones ADR-001 already lists (LGPL notice, text, relink/source offer). libde265 stays "HEIC option image only". dav1d and libaom stay "yes", now as libheif plugins.

## Consequences
- Positive: AVIF works in the default image. HEVC stays out of it, and an image check enforces that instead of just stating it.
- Negative: libheif is built from source, so the vips stage takes longer to build and there is one more checksummed tarball to bump. The LGPL relink/source duty for libheif now applies to every image.
- Risk: a future libheif release could switch a codec on by default. The image check in Decision 5 fails the build if that happens. Later milestones must not switch on any HEVC or VVC option in the default image, and must not add x265 anywhere.

## Precedent
None from Vidra. The precedent survey records no AVIF/HEIC codec split in Vidra. This decision comes from the vizra-core image build (`Dockerfile`, vips stage, `vips -l` check) and the libheif and Debian sources cited above.

## Evidence and ratification
Q-034 (libvips/govips LGPL, digest-pinned build, loader list), as amended here. Owner decision 2026-11-12 #9. Facts checked on 2026-11-12: libheif releases (`gh api repos/strukturag/libheif/releases`), `CMakeLists.txt` plugin options at `v1.23.7`, Debian trixie package pages for `libheif1`, `libaom-dev`, `libdav1d-dev`, `libsvtav1enc-dev`.

## Ledger IDs
VZ-MEDIA-001, VZ-MEDIA-010.

## M0 obligations
None; this is an M1 decision. The vizra-core PR for VZ-MEDIA-001 builds libheif as in Decision 1–3, replaces the "no heif" check with the check in Decision 5, and updates the licence table entries in the image's notices.
