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

### What was built
- `internal/fixtures/` — the generator: `fixtures.go` (the twelve specs, each
  with purpose, expected decode outcome and assertions), `raster.go` (fixed LCG
  painter), `jpeg.go` (EXIF/GPS IFD writer + independent EXIF reader for the
  assertions), `png.go` (raw chunk writer, the two bombs), `gif.go` (animation +
  the GIF/SVG polyglot), `webp.go` (a hand-written VP8L encoder and an
  independent VP8L reader, plus the RIFF/VP8X/ANIM/ANMF container), `mp4.go`
  (ISOBMFF box tree with MJPEG samples), `codec.go` (the two committed codec
  inputs and their provenance), `manifest.go`, `loadcorpus.go`.
- `cmd/fixturegen` (generate / manifest / verify), `cmd/loadcorpusgen`.
- `fixtures/manifest.json` — committed. `testdata/fixtures/` — gitignored.
- `Makefile`: `fixtures`, `fixtures-verify` (added to `make ci`),
  `fixtures-manifest`, `load-corpus`.
- `.github/workflows/fixtures.yml`; `fixtures` added to
  `.github/required-checks.txt` and to `FLOOR_LANES`; new guard fixture
  `scripts/testdata/guard/fixtures-floor-deleted` with a case in
  `scripts/scripts_test.go`.
- `NOTICE` (licence position), `AGENTS.md` (gate + rules + a Fixtures section).

### Decisions as implemented
D1–D5 as designed above, with one correction: **D4 was wrong as first written.**
The byte difference that broke the codec provenance test came from the Go
TOOLCHAIN (go1.26.2 vs go1.27.1, selected by `GOTOOLCHAIN=auto` on a scratch
module with no `toolchain` line), not from go.mod's language version. With the
toolchain held at go1.27.1, `go 1.26.0` and `go 1.26.2` produced identical bytes
for all twelve fixtures. The toolchain pin is therefore the measured one; the
go.mod directive is still recorded, for the two mechanisms that do hold (GODEBUG
defaults, and toolchain selection under `GOTOOLCHAIN=auto`). Every place that
claimed otherwise was corrected before the PR: `internal/fixtures/manifest.go`,
`AGENTS.md` and the evidence document.

### Commands run (darwin/arm64, go1.27.1)
| Command | Result |
|---|---|
| `go run ./cmd/fixturegen -repo . generate` | 12 fixtures, 1,791,508 bytes |
| `go run ./cmd/fixturegen -repo . verify` | exit 0 |
| `go test -race -count=1 ./internal/fixtures/` | ok, 108 s |
| `make ci` | all lanes passed (transcript in the repo) |
| `./scripts/ci-required-guard.sh` | pass on the real workflows |
| `./docs/evidence/fixtures/demonstrate.sh` | exit 0, 4 red/green pairs, tree restored clean |

### Performance work (no fixture weakened)
The first race-enabled run of the package took **557 s**, which is not
acceptable in a required lane. Three changes brought it to **108 s**, and each
was checked to leave every fixture byte identical (only the generator source
digest moved, which is the `generator-source` check working):
1. the painter rewritten from O(pixels x blocks) to three passes, and its buffer
   narrowed from `[]int32` to `[]uint8`;
2. `rawPNG` now uses `clear(row)` instead of an element-wise reset — that loop
   was 112 million individually instrumented writes;
3. the two large rasters pinned to `zlib.BestSpeed`. Their data is a long run of
   a repeating pattern, level 1 still reaches 920:1 and 1011:1, and **every
   assertion keeps its original threshold** (file under 512 KiB, raster over
   64 MiB, expansion ratio at least 500:1). The file grew 109 KB -> 122 KB.
Plus: the suite now generates the corpus once and shares it, and
`VerifyAgainstManifest` does its cheap checks first and refuses to regenerate
when a pin, the generator source or the on-disk corpus already disagrees.

### Evidence locations (inside the repo)
- `vizra-core/docs/evidence/fixtures/2026-09-21-demonstrations.md`
- `vizra-core/docs/evidence/fixtures/2026-09-21-determinism.md`
- `vizra-core/docs/evidence/fixtures/2026-09-21-external-tool-crosscheck.md`
- `vizra-core/docs/evidence/fixtures/2026-09-21-make-ci.md`
- `vizra-core/docs/evidence/fixtures/demonstrate.sh` (re-runnable)

## Blockers and handoff

1. **ADR-009 amendment owed (meta repo, not mine).** ADR-009 names libvips and
   exiftool as the generator's tools. The generator uses neither, for reasons
   measured and recorded in the determinism document, and under a carve-out
   ADR-001 already grants. The ADR text should be amended to match. I did not
   edit it: it is not this slice's to change.
2. **exiftool is absent on the owner's machine** (already recorded in
   VZ-ISSUE-001). It is no longer on the critical path for this slice, since the
   generator does not use it.
3. **arm64 vs amd64 byte-identity** is asserted by comparing the table in the
   determinism document with the `fixtures` CI job's step summary on the head
   SHA. Until that CI run is read, the cross-architecture claim is PENDING, not
   PASS.
4. **No local container build was attempted.** `df` showed 11 GiB free, at the
   brief's floor, and the final design needs no container at all.
