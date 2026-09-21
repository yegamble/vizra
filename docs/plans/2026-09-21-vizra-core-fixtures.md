# Execution plan: VZ-FOUND-007 — deterministic fixture corpus (`vizra-core` PR "fixtures")

## Context
- Repo `yegamble/vizra-core`, checkout `/Users/yosefgamble/github/vizra/vizra-core`.
- Base commit `9e44d30415c9545aa12e4ce84e4afe6062725e55` on `main`, tree clean at start.
- Branch `feat/m0-fixtures`. Meta issue: `yegamble/vizra#1` (VZ-ISSUE-001).
- Contract: meta `AGENTS.md`, repo `AGENTS.md`, `docs/issues/VZ-ISSUE-001.md`
  (the VZ-FOUND-007 acceptance bullet), `docs/plans/2026-09-15-prompt01-architecture.md`
  item 2, ADR-009 (the twelve M0 fixtures, load corpus, acceptance platform),
  ADR-006 (codec boundary, metadata/GPS policy), ADR-001 (libvips/Go pins,
  licences, "a pure-Go decoder path exists only to generate fixtures").

## Preflight (2026-09-21, darwin/arm64, this machine)
| Tool | Result |
|---|---|
| `go version` | go1.27.1 darwin/arm64 — matches the `toolchain` pin in go.mod |
| `docker` | present |
| `exiftool` | **MISSING** — already recorded as a blocker in VZ-ISSUE-001 |
| `vips` (homebrew) | present — used only to cross-check fixture properties, never to generate |
| `ffmpeg`/`ffprobe` (homebrew) | present |
| `identify` (ImageMagick) | present |
| `python3`, `jq`, `gh` | present |
| free disk (`df`) | 11 GiB — at the brief's 10 GiB floor; no image build attempted |

Consequence: a generator that depends on `exiftool` cannot be verified on this
machine at all, and a generator that depends on libvips encoders cannot produce
byte-identical output across libvips versions or CPU architectures. Both are
designed out (see below).

## Acceptance (observable)
- The pinned generator reproduces the twelve ADR-009 M0 fixtures byte-identically
  against the committed sha256 manifest (VZ-ISSUE-001 acceptance bullet).
- A changed fixture fails the manifest check, naming the file (demonstrated).
- The generator changed without regenerating fails (demonstrated).
- A pinned byte-influencing tool version bumped without updating the manifest
  fails (demonstrated).
- Deleting the lane from `.github/required-checks.txt` turns the guard floor red
  (demonstrated).
- Each fixture is asserted for **what it is for**, not merely hashed.
- Load-corpus generator exists, is parameterised, and its output is not committed
  and not part of the correctness manifest.

Non-goals for this slice: migrations (0001–0004 are FROZEN), anything under
`api/`, the M1 upload/validation pipeline itself, the `boot` lane (VZ-ISSUE-004),
the load corpus *run* (VZ-OPS-007), and the ledger's broader corpus (ICC
wide-gamut standalone, transparent WebP still, animated AVIF, MOV, 360) which
ADR-009 defers to the slices that need them.

## Design decisions (and why)

### D1. Fixture bytes are generated, not committed; the manifest is committed
ADR-009 says the corpus is "synthesised deterministically by a pinned script" and
that "the manifest, with a sha256 per file and the generator version, is
committed" — it does not commit the bytes. The ledger's `evidence_required` says
"fixture manifest committed; hashes verified in CI". So: `testdata/fixtures/` is
gitignored and produced by `make fixtures`; `fixtures/manifest.json` is committed.

### D2. The generator is pure Go, standard library only — no libvips, no exiftool
Byte-identical reproduction is the whole point, and the named tools cannot give
it: libjpeg-turbo/libwebp/libaom emit different bytes across versions and can
differ across SIMD paths, and exiftool stamps its own version and timestamps.
ADR-001 explicitly permits this: "a pure-Go decoder path exists only to generate
fixtures". Every pixel and every metadata tag (EXIF IFD, GPS IFD, PNG chunks,
GIF blocks, RIFF/VP8L bitstream, ISOBMFF boxes) is written by the generator.
This is a recorded refinement of ADR-009's *named tooling*; its *decision*
(synthesised, deterministic, pinned, provenance = the script, no licence needed,
manifest committed) is implemented exactly. Flagged to the chair as an ADR-009
amendment for the meta repo to make — it is not mine to edit.

### D3. Two fixtures need a real codec and are committed as generator inputs
AVIF needs an AV1 encoder and WebM needs VP8/VP9/AV1; neither exists in pure Go,
and both are arithmetic-coded with large default probability tables that cannot
be hand-written responsibly. Those two files were produced once by a recorded
`ffmpeg` invocation over a **generator-produced** PNG, and are committed under
`internal/fixtures/codec/` as embedded generator inputs. They are still entirely
ours — no third-party photograph, no download — and the manifest records the
exact producing command and tool version. Consequence: all twelve outputs
reproduce byte-identically on every platform, including arm64.

### D4. The byte-influencing pin is the Go toolchain
Every encoder is `compress/zlib`, `image/jpeg`, `image/gif`, `image/png` or
generator-written bitstream, so the one external thing that can move the bytes is
the Go toolchain. The manifest records it and `fixtures-verify` fails on a
mismatch with a named message. That is also demonstration 3.

### D5. "Changing the generator without regenerating" is caught by a source digest
The manifest records `generator.source_sha256` over the exact list of generator
source files (same idea as `migrations/manifest.sha256`). Editing the generator
without `make fixtures-manifest` turns the lane red.

## Implementation
- `internal/fixtures/` — corpus definition, writers (JPEG+EXIF/GPS, PNG, GIF,
  RIFF/VP8L animated WebP, ISOBMFF MJPEG MP4, SVG/GIF polyglot), deterministic
  PRNG, manifest model, verifier.
- `internal/fixtures/codec/` — the two committed codec-tier inputs.
- `cmd/fixturegen` — `generate`, `verify`, `manifest`.
- `cmd/loadcorpusgen` — the separate, parameterised load-corpus generator.
- `fixtures/manifest.json` — committed manifest.
- `Makefile`: `fixtures`, `fixtures-verify`, `fixtures-manifest`, `load-corpus`.
- `.github/workflows/build-test.yml`: new `fixtures` job on ubuntu-24.04.
- `.github/required-checks.txt` + `scripts/ci-required-guard.py` FLOOR_LANES
  (**owner-reviewed files** — CODEOWNERS protected).
- `NOTICE` / `README.md`: the licence position of the corpus.
- No migration, no `api/` change.

## Verification
| Command | Where |
|---|---|
| `make fixtures` | local arm64 + CI amd64 |
| `make fixtures-verify` | local arm64 + CI amd64 |
| `go test ./internal/fixtures/...` | property assertions per fixture |
| `make ci` | full local gate |
| `./scripts/ci-required-guard.sh` | floor |
| CI run on the head SHA | acceptance platform of record |

## Progress and evidence
Appended below as it runs; transcripts committed under
`vizra-core/docs/evidence/fixtures/`.

## Blockers and handoff
Recorded as they occur.
