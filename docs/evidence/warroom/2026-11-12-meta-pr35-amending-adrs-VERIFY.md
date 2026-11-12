# Verify: vizra (meta) PR #35 — amending ADR-010 / ADR-011

- PR: https://github.com/yegamble/vizra/pull/35 (branch `docs/amending-adrs-2026-11-12`)
- SHA verified: `71d8a553636b9607d4e1de696557d92f57331d9c` (matches `gh pr view 35 --json headRefOid`)
- Verifier: independent (did not write the PR). Budget label: QUEUE-owner-rulings
- Environment: macOS (darwin), fresh clone `/tmp/vzv-vizra-pr35-bUuv7G` (deleted afterwards), 2026-11-12 ~17:10–17:30Z
- Sources: owner text `origin/chore/warroom-records-2026-11-12d:docs/warroom/OWNER-DECISIONS.md` lines 48–49; inbox `OWNER-INBOX.md` "### 4a" / "### 8b" (Closed)

## (1) Scope fidelity
- ADR-011 Decision 1–3 match decision #10 and the inbox 8b row text word for word (`docs/adr/ADR-011-…md` Decision §2 table row matches the inbox text exactly). Saying "deny 403" for a cross-site request is the obvious other half of the "must not be cross-site" rule, and it matches how ADR-003's table already words denials. Re-deriving on sign-in is already in ADR-003 "Credentials". The "must not apply to cookie/API-key requests" consequence is a scope limit on the row the owner approved, not a new rule. FAITHFUL.
- ADR-011 Ledger IDs (VZ-INSTALL-003, VZ-AUTH-001, VZ-SECURITY-003) are a subset of ADR-003's own index row (`docs/adr/README.md` ADR-003 row). That is bookkeeping, not a new binding. FAITHFUL.
- ADR-010 matches decision #9 and the chair recommendation the owner ticked ("dav1d decode, aom or svt encode", without libde265/x265, assertion changed to "heif loader present, no HEVC codec"). Picking libaom over SVT-AV1 is a choice inside the option set the owner approved. Turning `WITH_AOM_DECODER` off and "not using Debian's libheif package" are needed to carry out "AV1 only", and §3 explains why. The ledger IDs VZ-MEDIA-001/010 are the ones the owner and inbox name. The `[pin at PR time; verify]` placeholder follows ADR-001's own licence-table convention (ADR-001 lines 108–111). It does not make any gate false-green: Decision 5's check is what the gate enforces. FAITHFUL; small items are listed as follow-ups.

## (2) Technical claims (checked live)
- `packages.debian.org/trixie/libheif1`: version `1.23.6-2~deb13u1`; **dep** `libheif-plugin-dav1d | libheif-plugin-aomdec`, **dep** `libheif-plugin-libde265`, **rec** `libheif-plugin-aomenc`, `libheif-plugin-x265`. ADR-010 §3 TRUE.
- `libaom-dev 3.12.1-1+deb13u1`, `libdav1d-dev 1.5.1-1`, `libsvtav1enc-dev 2.3.0+dfsg-1` on trixie pages. TRUE.
- `gh api repos/strukturag/libheif/releases`: v1.23.7 published 2026-10-26T11:48:19Z, the newest. TRUE.
- libheif `CMakeLists.txt@v1.23.7` `plugin_option(...)`: LIBDE265 (l.136, default ON), X265 (l.143, ON), KVAZAAR, UVG266, VVDEC, VVENC, FFMPEG_DECODER, DAV1D (l.229), AOM_DECODER (l.236, ON), AOM_ENCODER (l.237, ON) all exist, so all the `WITH_*` names in ADR-010 §2 are real. Turning LIBDE265/X265 off is required, because they default to ON; the ADR says so explicitly. TRUE.
- `COPYING@v1.23.7`: "The library `libheif` is distributed under the terms of the GNU Lesser General Public License." TRUE.
- libvips reaches AVIF only through heifload/heifsave (libheif). This is well-established upstream libvips behaviour. TRUE.
No false claim that would break the image build or the assertion. No BLOCKING.

## (3) Immutability and conventions
- `git diff origin/main...71d8a55 -- docs/adr/ADR-001* docs/adr/ADR-003*` → 0 lines. PASS.
- Numbering continues from ADR-009 → 010, 011. Both ADRs have Status/Date/Context/Decision/Consequences/Precedent/Evidence/Ledger IDs/M0 sections, plus index rows. ADR-001/003 index status now says "amended by ADR-0xx", as the README's amendment rule requires. PASS.

## (4) Files changed
`git diff --stat origin/main...HEAD`: only `docs/adr/ADR-010-…md` (+41), `docs/adr/ADR-011-…md` (+40), `docs/adr/README.md` (+4/−2). No product code. PASS.

## (5) Meta checks (in the clone at the SHA)
- `python3 -I scripts/check-doc-links.py` → exit 0
- `python3 -I scripts/check-quality-json.py` → exit 0
- `python3 -I scripts/check-template-claims.py` → exit 0

## (6) CI on the SHA
CI_STATUS_PLACEHOLDER

## Findings
BLOCKING: none.

FOLLOW-UP (non-blocking):
- F-1: ADR-010 §2 does not switch off libheif's other non-AV1 video codec plugins, which default to ON at v1.23.7: `WITH_X264` (AVC encoder, l.203) and `WITH_OpenH264_DECODER` (l.210). Decision 5's check is HEVC/VVC-only, so an AVC codec could ship without anything catching it. That is outside what the owner ruled (HEVC). The vizra-core VZ-MEDIA-001 PR should switch them off or the check should list them.
- F-2: ADR-010 Decision 1 still contains `[pin at PR time; verify]` for the libheif version/SHA-256. This follows ADR-001's convention, and the gate is the vizra-core pin.
- F-3: ADR-011's ledger IDs were chosen by the builder (they are a subset of ADR-003's index). The chair should confirm.

