# ADR-006: Derivatives, metadata policy, codec boundary

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` forbids trusting client MIME, filenames or EXIF, requires bounded
decoder and subprocess resources, and forbids private metadata reaching public
surfaces or logs. For a photo community, orientation, colour, transparency and
EXIF policy are correctness, not polish. Q-034 fixes the codec boundary: the
worker decodes, the api does not, and only libvips output may produce derivative
or hash evidence.

## Decision
### Representations
Representations live in
`asset_files(asset_id, kind, storage_location_id, object_key, width, height, bytes, sha256, content_type, processing_version, created_at)`
with `UNIQUE (asset_id, kind, processing_version)`. `assets.processing_version`
bumps on reprocess; the old version keeps serving until the new set is complete,
after which a job deletes the old files.

| Kind | Produced by | Purpose | Metadata | Serving |
|---|---|---|---|---|
| `original` | upload, byte-for-byte | archive, download, reprocess source | kept unless strip-on-upload | proxied when not public |
| `display` | libvips, max long edge (setting, default `[to confirm in M0]`) | photo page | stripped except keep-list | public: CDN-cacheable with `?v=` |
| `medium` | libvips, fixed width or height | embeds, cards | stripped except keep-list | as `display` |
| `thumbnail` | libvips, sizes are settings (defaults `[to confirm in M0]`) | grids, library | stripped except keep-list | as `display` |
| `poster` | ffmpeg frame | video still | stripped | as `display` |
| `playback` | bounded browser-native derivative only (Q-009) | video playback | stripped | as `display` |

Derivative work happens only in the worker, through govips. Orientation is applied
from the EXIF orientation tag; ICC profiles are honoured and derivatives converted
to sRGB; transparency is preserved for PNG, WebP and AVIF; animation is preserved
for GIF, WebP and AVIF as a first-frame thumbnail plus an animated display where
configured. Originals are preserved losslessly and never rewritten. There is no
transcoding ladder for video (Q-009).

### Metadata policy
Metadata is extracted once — EXIF, XMP, IPTC and an ICC summary — into
`asset_metadata` as jsonb, and serves display and search facets.

| Field class | Original | Derivative | Display | Search |
|---|---|---|---|---|
| EXIF technical (camera, lens, exposure, ISO, focal length) | kept unless strip-on-upload | stripped by default, unless on the operator keep-list | shown on the Exif tab when allowed | facet |
| EXIF orientation | kept | absent — the rotation is baked into pixels | not shown | not indexed |
| ICC profile | kept | converted to sRGB | colour-managed rendering | not indexed |
| GPS | kept unless strip-on-upload | **never present** | only if the owner's geo-privacy setting allows (Q-038) | excluded in core; in full, geo facets (VZ-SEARCH-002, VZ-GEO-001) receive location only where the owner's geo-privacy setting allows, under the same rule as display |
| XMP/IPTC descriptive (title, caption, keywords, creator, rights) | kept | stripped by default | shown | facet |
| Maker notes and other private tags | kept | never present | never shown | never indexed |

**Geo-privacy default (Q-038).** The geo-privacy setting's default value is
**"only me"**: a newly uploaded asset's location is visible to its owner (and to
staff in an audited context) and to nobody else until the owner widens it. Every
row above that says "only if the owner's geo-privacy setting allows" therefore
denies by default, and the map view, geofences and the EXIF-location import policy
of VZ-GEO-001 inherit that default rather than setting their own. Geotag features
are full-profile (VZ-GEO-001) with self-hostable tiles or a configurable provider;
core keeps GPS out of derivatives and out of search regardless of the setting.

### Bounds and the codec boundary
Maximum pixels and maximum dimensions are checked from the header before any
decode. The libvips operation cache is capped, worker concurrency is 1 on the
minimum host, the worker container has a memory limit, and every job has a
wall-clock timeout. Video uses `ffprobe`/`ffmpeg` subprocesses in their own
process group with a wall-clock timeout and stdout/stderr redaction, producing a
poster frame and a bounded browser-native playback derivative only.

The format matrix is VZ-MEDIA-002; the api rejects an unsupported format at
session create, from the loader list the running image reports (Q-034). No lane
that produces derivative or hash evidence may use a non-libvips decoder.

## Consequences
Positive: one processing-version counter makes reprocessing safe and observable;
the metadata table means a facet never re-reads an original; stripping by default
makes a privacy leak an explicit opt-in; rejecting unsupported formats at session
create means such an upload never occupies a job. Negative: sRGB conversion loses
wide-gamut fidelity on capable displays, a deliberate trade; untouched originals
keep whatever the camera wrote, including GPS, so download authorization carries
real weight. Risks: a keep-list mistake could publish GPS, so the assertion is
"GPS never present" and is tested on the GPS fixture; animation is the easiest
place to lose frames silently, so the animated fixtures are correctness fixtures.
Later milestones must not break: no decode in the api, the representation
uniqueness constraint, old-version serving during reprocess, GPS never in a
derivative, libvips-only evidence, and subprocesses in a process group with a
timeout.

## Precedent
Copied from Vidra (survey citations): the kind-widened representation table with
per-row hashes (`C/migrations/0060_media_extras.up.sql:16`; base `0008`; sha256 in
`0106`), reprocessing behind a generation counter with versioned trees and a cache
key so the old generation keeps serving
(`C/migrations/0136:26`;
`C/internal/mediaroute/mediaroute.go:41`; `C/internal/httpapi/replace.go:21`), the
single publication gate that validates before publishing
(`C/internal/video/service.go:1094-1212`), a downstream fence that serves only
public and published content (`:532`;
`C/migrations/0006:24`), argv built by pure exported-for-test
functions with no shell anywhere and stderr redacted because it echoes presigned
URLs (`C/internal/media/ffprobe.go:63,93`;
`C/internal/media/hls.go:553`), and process-group handling where it exists
(`C/internal/ytdlp/exec.go:38`).

Unlike Vidra: orientation, EXIF, ICC and metadata handling are effectively absent
there — no rotation, no `-map_metadata`, no stripping code, only two comments
(`C/internal/media/cmaf.go:177`; `C/internal/media/hls.go:549`) — and image
uploads are validated by an extension allowlist with no `image.DecodeConfig` in
the photo or avatar path (`C/internal/media/imagetype.go:22`). Subprocesses are
bounded by context only: `C/internal/ytdlp/exec.go:38` is the single `Setpgid`
site across roughly thirteen exec sites, and only the encoder probe has a timeout
(`C/internal/media/codec.go:413`). HLS segments carry no representation rows and
are therefore hash-less and invisible to the integrity backfill
(`C/internal/mediahash/service.go:13-19`), and storyboard generation failed
silently until a give-up ledger was added
(`C/migrations/0117`).

## Evidence and ratification
Q-009 (store plus poster plus bounded native playback, no ladder), Q-010 (HEIC
decode only, never x265), Q-034 (worker-only decode, api rejects unsupported
formats, libvips-only evidence) and Q-038 (geo-privacy default) in the
`docs/OPEN_QUESTIONS.md` ratification record;
`docs/evidence/research-2026-09-15/ratification-facts.md` §5 for the codec matrix.

## Ledger IDs
VZ-MEDIA-001, VZ-MEDIA-002, VZ-MEDIA-003, VZ-MEDIA-004, VZ-MEDIA-005,
VZ-MEDIA-009, VZ-MEDIA-010, VZ-UPLOAD-013, VZ-GEO-001.

## M0 obligations
M0 owns none of the derivative behaviour, which lands in M1 (VZ-MEDIA-001,
VZ-MEDIA-003, VZ-MEDIA-004). M0 must not preclude it: the worker image carries
libvips with its loader list on `/version` (ADR-001), the worker process exists
with per-job timeouts and process groups (ADR-004), and the deterministic fixture
corpus these assertions need is built in M0 (ADR-009, VZ-FOUND-007).

Reservation only: `asset_files`, `asset_metadata` and `assets.processing_version`
are schema reservations created with the M1 media slice; watermarks
(VZ-MEDIA-007), 360° (VZ-MEDIA-006), the full format matrix (VZ-MEDIA-002), HEIC
(VZ-MEDIA-010) and reprocessing tools (VZ-MEDIA-009) are M3 or later and must fit
the table above.

