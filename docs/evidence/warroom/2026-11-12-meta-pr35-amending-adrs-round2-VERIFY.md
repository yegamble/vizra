# Verify (round 2): vizra (meta) PR #35 — amending ADR-010 / ADR-011

- PR: https://github.com/yegamble/vizra/pull/35. SHA verified: `71d8a553636b9607d4e1de696557d92f57331d9c` (`gh pr view 35 --json headRefOid` gives the same SHA; state OPEN)
- Verifier: independent fresh verifier, not the builder. Budget label: QUEUE-owner-rulings. This replaces the incomplete round-1 file, which ended BLOCKED with no verdict line.
- Environment: darwin. Fresh clone at `/tmp/vzv-vizra-pr35b-9C0wGa`, deleted afterwards. The round-1 leftover `/tmp/vzv-vizra-pr35-bUuv7G` was removed by exact path; `ls` then reports that it no longer exists.

## (1) Scope
- `git diff --stat origin/main...HEAD` shows 3 files: `docs/adr/ADR-010-avif-via-libheif-av1-only.md` (+41), `docs/adr/ADR-011-csrf-pre-claim-and-password-version-tag.md` (+40), `docs/adr/README.md` (+4/−2). PASS.
- `git diff origin/main...HEAD -- docs/adr/ADR-001* docs/adr/ADR-003* | wc -l` gives 0. PASS.

## (2) Fidelity to owner decisions
- #9: ADR-010 Decision 1–4 says libheif is in the default image, built with AV1 only (dav1d decode, libaom encode), with AVIF on and HEIC/HEVC off by default, and that this unblocks VZ-MEDIA-001. Decision 5 sets the gate "heif loader present, no HEVC codec", and Decision 6 updates the licence table. All of this is needed to carry out the ruling. It adds no new policy. FAITHFUL.
- #10: ADR-011 Decision 1 renames the row to "Installer setup wizard" and leaves its other columns unchanged. Decision 2 adds a row that matches the inbox 8b text word for word: "Unauthenticated pre-claim JSON POST | credential in body | exact JSON content type; Origin / Sec-Fetch-Site must not be cross-site when present | allow". Decision 3 says the version tag is the plain PHC string with no extra prefix. The 403 wording and the cookie/API-key scope limit only restate what the approved row already means. FAITHFUL.

## (3) Live source spot-checks
- packages.debian.org/trixie/libheif1: the dependency list has `dep:` entries, in order: dav1d|aomdec, then `libheif-plugin-libde265`, then svtenc/x265 (rec). ADR-010 §3 is TRUE.
- `raw.githubusercontent.com/strukturag/libheif/v1.23.7/CMakeLists.txt`: line 136 `plugin_option(LIBDE265 "libde265 HEVC decoder" ON OFF)`, line 143 `plugin_option(X265 "x265 HEVC encoder" ON OFF)`. The option names are TRUE. Also found: line 203 `X264` ON, line 210 `OpenH264_DECODER` ON.

## (4) Meta checks (in the clone at the SHA)
`python3 -I scripts/check-doc-links.py` exits 0. `check-quality-json.py` exits 0. `check-template-claims.py` exits 0.

## (5) CI on the SHA
`gh pr checks 35 -R yegamble/vizra`: ci-required pass (run 43266360448), validate pass (run 43266360066), GitGuardian pass. `gh run view` confirms both runs have headSha `71d8a553…` and conclusion success. They were green on the first poll.

## Findings
BLOCKING: none.

F-1 is ruled NOT BLOCKING. The AGENTS.md bar needs a gate that passes falsely **in today's tree**. This PR changes docs only. The "heif loader present, no HEVC codec" check does not exist yet; it will come in the vizra-core VZ-MEDIA-001 PR. So nothing turns green falsely on this head. On substance, owner decision #9 rules out HEVC, and AVC is not HEVC. Leaving X264/OpenH264 on would still break the ADR's own "AV1 codecs only" title, and the vizra-core PR must close that gap. That is follow-up work for the builder, not a defect on this head.

FOLLOW-UP:
- F-1: ADR-010 §2 does not switch off `WITH_X264` (line 203, default ON) or `WITH_OpenH264_DECODER` (line 210, default ON). Decision 5's check only covers HEVC/VVC.
- F-2: ADR-010 Decision 1 still has the `[pin at PR time; verify]` placeholder for the libheif version and SHA-256.
- F-3: the builder chose ADR-011's ledger IDs (VZ-INSTALL-003, VZ-AUTH-001, VZ-SECURITY-003). The chair should confirm them.

FINAL VERDICT: PASS — SHA 71d8a553636b9607d4e1de696557d92f57331d9c
