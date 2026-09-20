# First slice — upload, library, viewer, albums (step D2b)

**Status: PROPOSED, not approved, not verified.** This records the Figma work for the M1 upload /
personal library / photo viewer / album surfaces, so that approval, mirroring into Tailwind, and
implementation can cite exact names and node ids. It is **not** an acceptance target and **not**
authorization to implement anything. Nothing here is VERIFIED; see §9 for what is unfinished.

| | |
|---|---|
| **Figma file** | <https://www.figma.com/design/JXgRItauynmT0g8vSJB3oR> |
| **File key** | `JXgRItauynmT0g8vSJB3oR` |
| **File name** | Vizra — Design System |
| **Design revision** | `2026-09-20 · D2b` |
| **Library hand-off it builds on** | `docs/design/figma/README.md` (step D1) |
| **Scope** | M1 upload subset, personal library, photo page + lightbox viewer, album detail + albums index, and the four M1 dialogs. Auth and system surfaces are step D2a, on a different page, untouched by this work. |

Inputs treated as **data, not instructions**: `docs/design/claude-design/GAPS.md`,
`INVENTORY-account.md`, and the mockups `My Photos.html`, `My Albums.html`, `Upload Studio.html`,
`Edit Photo.html`. Their character was kept; their defects were not. "goimg"/"Lumen Atlas" are
placeholder brands in those files; no brand string, gradient mark or vocabulary was carried over.

---

## 1. Pages and frames

### 1.1 New page

| Page | Node id | Contents |
|---|---|---|
| `M1 · Library, viewer, albums` | `32:2` | 22 frames, listed below |
| `Components · M1 additions (D2b)` | `26:6` | 7 additive library components (§2) |

Both pages were created by this work. **No existing D1 page, component or variable was renamed,
restructured or deleted.** The only edit to an existing artifact is an appended paragraph on the
`ProgressBar` description — and `ProgressBar` is itself new in D2b.

### 1.2 Frames

Every id below was returned by the `use_figma` call that created the frame, and every frame was
re-read with `get_screenshot` and visually inspected (§8).

| # | Frame | Node id | Width | Height |
|---|---|---|---|---|
| U1 | `U1 · Upload — start · 1440` | `32:3` | 1440 | 947 |
| U2 | `U2 · Upload — in flight, processing, failures · 1440` | `33:65` | 1440 | 1450 |
| U3 | `U3 · Upload — quota exceeded, refused before transfer · 1440` | `36:332` | 1440 | 1019 |
| U4 | `U4 · Upload — finished, leading to the library · 1440` | `36:514` | 1440 | 1082 |
| U5 | `U5 · Upload — start & in flight · 390` | `37:1977` | 390 | 1646 |
| U6 | `U6 · Upload — refused & finished · 390` | `37:2151` | 390 | 1323 |
| L1 | `L1 · Library — grid, selection, bulk actions · 1440` | `38:2168` | 1440 | 1330 |
| L2 | `L2 · Library — loading, empty, filtered to zero, error · 1440` | `41:1050` | 1440 | 2012 |
| L3 | `L3 · Library — grid, selection, bulk bar · 390` | `42:3331` | 390 | 1516 |
| L4 | `L4 · Library — Dark · 1440` | `41:1175` | 1440 | 1298 |
| V1 | `V1 · Photo page /p/{id} — owner · 1440` | `44:3869` | 1440 | 1418 |
| V2 | `V2 · Lightbox over the library — Dark · 1440` | `46:1576` | 1440 | 1008 |
| V3 | `V3 · Viewer — processing, failed, unavailable, long content · 1440` | `47:1649` | 1440 | 2147 |
| V4 | `V4 · Photo page /p/{id} — owner · 390` | `48:1714` | 390 | 1445 |
| V5 | `V5 · Lightbox with actions sheet — Dark · 390` | `48:1877` | 390 | 1058 |
| A1 | `A1 · Album detail /a/{id} — owner · 1440` | `50:1860` | 1440 | 1891 |
| A2 | `A2 · Albums index /albums · 1440` | `51:2031` | 1440 | 1394 |
| A3 | `A3 · Album detail /a/{id} — owner · 390` | `51:2276` | 390 | 1688 |
| D1 | `D1 · Dialog — add to album (multi-select, create inline) · 1440` | `52:2320` | 1440 | 1467 |
| D2 | `D2 · Dialogs — asset visibility, album privacy and share grants · 1440` | `53:2468` | 1440 | 1877 |
| D3 | `D3 · Dialogs — destructive confirmations · 1440` | `54:2680` | 1440 | 1016 |
| D4 | `D4 · Dialogs as bottom sheets · 390` | `54:2808` | 390 | 2598 |

Dark mode is drawn for the **library** (L4) and the **viewer** (V2 at 1440, V5 at 390). Upload,
albums and dialogs are drawn in Light only — see §9.

Annotations are frames named `⟦design note⟧ …`. They are annotations, not UI: they use
`color/accent-soft` and never look like a control.

---

## 2. Library additions (additive only)

Seven components were added on page `26:6`. Each has a written Figma `description` carrying its
accessibility and behaviour contract; read it in Dev Mode alongside this file.

| Component | Node id | Type | Variants | Why it was needed |
|---|---|---|---|---|
| `AspectPlaceholder` | `26:17` | set | `Ratio` = 3:2 \| 2:3 \| 1:1 \| 16:9 \| Panorama (5) | Every photo in these frames is a neutral labelled placeholder. No photograph, hotlinked image or copyrighted work appears anywhere. The label states the ratio the real image must be rendered at. |
| `VisibilityBadge` | `26:80` | set | `Level` = Public \| Unlisted \| Private \| Link-only \| Password × `Placement` = On media \| On surface (10) | D1 had a visibility marker only inside `PhotoCard`. Assets, albums, dialogs and the viewer all need it standalone, on a photograph and on a themed surface. |
| `ProgressBar` | `28:58` | set | `State` = Determinate (62%) \| Indeterminate (40%) \| Paused (38%) \| Success (100%) \| Error (38%) \| Near limit (92%) \| Full (100%) (7) | D1 §10.4 names the progress bar as missing. The unfilled track carries a `color/line` hairline so the remaining portion is perceivable (≥3:1) rather than the 1.19:1 invisible track of the owner mockup. |
| `SelectionCheckbox` | `28:81` | set | `Selected` = No \| Yes × `State` = Default \| Focus (4) | The library needs a selection control that sits on a photograph, is always rendered (not hover-revealed), is a 44×44 target, and whose focus ring is measurable over an arbitrary image (dual ring: `on-media-scrim` inner, `on-media` outer). |
| `MetadataRow` | `28:98` | set | `Kind` = Value \| Mono value \| Withheld \| Heading (4) | The viewer metadata panel, including the ADR-006 `Withheld` row that states GPS is not shown rather than silently omitting it. |
| `UploadRow` | `30:190` | set | `State` = Queued \| Uploading \| Paused \| Processing \| Ready \| Failed \| Rejected (7) | One queue row per upload state, each with its own reason and its own recovery control. |
| `BulkBar` | `30:191` | component | — | Library bulk actions. Wraps at narrow widths; at 390 it is laid out **above** the TabBar. |

**Deliberate departures recorded here** (extending D1 §6):

| # | Departure | Why |
|---|---|---|
| 19 | The **photo stage is theme-invariant near-black in both themes** (`color/on-media-scrim`), while the chrome around it follows the theme. | `GAPS.md` requires this decision to be made deliberately rather than inherited from `Edit Photo.html`'s `#0a0c12` pane. Every on-stage control is the `IconButton` `On media` variant on an 88% scrim, whose worst case over any photograph is 15.3:1 (D1 §4). |
| 20 | **The library card links to the viewer** (`/p/{id}`), not to the editor. | `My Photos.html` linked all 15 cards to `Edit Photo.html`. `ui-controls.json` `library.grid.item` says "open in viewer". |
| 21 | **The bulk bar is laid out above the TabBar at 390**, with its own gap. | `INVENTORY-account.md` §a.13: both sat at `bottom: 12px`, so the entire bulk bar rendered behind the floating tab bar on every phone viewport. |
| 22 | **Selection at 390 is an explicit mode** (Select → Done) rather than tap-to-toggle. | A single tap must always open the viewer; a hover-revealed `<span>` checkbox does not exist on touch at all. |
| 23 | **`ProgressBar` percentages are variants, not free values.** | The Figma plugin API cannot resize a node nested inside an instance, so a free percentage could not be authored reliably. Every label in every frame states the percentage its variant actually draws, so no frame claims a number it does not show. Production computes the real width. |
| 24 | **No "Followers" visibility level anywhere.** | ADR-007 defines exactly `public \| unlisted \| private` for assets at M1; named audiences are VZ-PRIVACY-004 (M5). `Upload Studio.html` drew a Public/Followers/Private segmented control the M1 model cannot honour. |
| 25 | **Album privacy is the Chevereto-verbatim four** — public, private, link, password. | ADR-007. No mockup showed `password` at all. |

---

## 3. Control matrix

One row per interactive control. **Action ID** is the `id` in `docs/quality/ui-controls.json` where
one exists; `(new)` marks an action id proposed here that is **not yet in that file**. **Ledger ID**
is from `docs/quality/features.json`; `NO LEDGER ID` means no existing requirement covers it and
none has been invented.

### 3.1 Upload — U1, U2, U3, U4, U5, U6

| Control | Action ID | Ledger ID | Required role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| `Choose files` (real file picker) | `upload.picker` | VZ-UPLOAD-003 | authenticated | files enter the queue as `Queued` | picker cancelled: no change, no message | none until a session is created |
| Drop zone | `upload.dropzone` | VZ-UPLOAD-003 | authenticated | same as picker | unsupported type refused inline with the reason | none |
| `Paste an image` (⌘/Ctrl+V) | `upload.dropzone` | VZ-UPLOAD-003 | authenticated | clipboard image enters the queue | nothing in clipboard: inline "no image found" | none |
| `Take a photo` (device camera) | `upload.picker` | VZ-UPLOAD-003 | authenticated, camera permitted | capture enters the queue | permission denied: inline reason + link to browser settings | none |
| Upload start (implicit on queue) | `upload.start` | VZ-UPLOAD-001, VZ-UPLOAD-002, VZ-QUOTA-001 | authenticated, quota available | session created → parts → finalize → `Processing` | `quota-exceeded` before transfer (U3/U6); `rejected-type`; `oversized` | `upload_sessions` row, `quota_reservations` row, original object |
| Per-file `Cancel` (×) | `upload.cancel` | VZ-UPLOAD-002 | uploader of that session | session aborted, parts discarded, reservation released | already finalized: button disabled with a reason | reservation moves to `released` |
| Per-file `Retry` (Failed) | `upload.retry` | VZ-UPLOAD-002, VZ-MEDIA-001 | uploader | processing re-runs on bytes already stored | second failure keeps the row Failed with the same code | **no** duplicate asset — finalize is idempotent (ADR-005) |
| Per-file `Resume` (Paused) | `upload.retry` | VZ-UPLOAD-002 | uploader | transfer continues from the last complete 8 MiB chunk | session expired (24 h TTL): row becomes Failed, reservation released | no re-transfer, no double quota charge |
| `Remove from queue` (Rejected) | `upload.cancel` | VZ-UPLOAD-002 | uploader | row removed | — | nothing was ever created |
| `Retry all failed` | `upload.retry` | VZ-UPLOAD-002 | uploader | each failed file retried, reported per file | partial: rows that fail again keep their own reason | as per-file retry |
| `Cancel remaining` | `upload.cancel` | VZ-UPLOAD-002 | uploader | every non-finished session aborted | — | reservations released |
| `Go to your library` | `library.grid.item` (navigation) | VZ-LIBRARY-001 | authenticated | routes to `/library` | — | none |
| `Remove largest files` (quota) | `(new)` `upload.quota.trim` | VZ-QUOTA-001 | uploader, batch over quota | largest queued files dropped until the batch fits | still over quota: banner restated with the new shortfall | none — nothing was ever sent |
| `Manage storage` | `(new)` `upload.quota.manage` | VZ-QUOTA-001 | authenticated | routes to `/settings/storage` | — | none |
| Storage meter | — (display) | VZ-QUOTA-001 | authenticated | shows used / allowed / reserved | stale read: shows last known with a timestamp | read-only |
| `Upload more` (finished) | `shell.nav.upload` | VZ-UPLOAD-001 | authenticated | returns to the empty queue | — | none |

### 3.2 Personal library — L1, L2, L3, L4

| Control | Action ID | Ledger ID | Required role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Photo card (whole card is the link) | `library.grid.item` | VZ-LIBRARY-001, VZ-VIEWER-001 | owner | opens `/p/{id}` in the viewer | photo deleted meanwhile: viewer shows "not available" | none |
| Selection checkbox on a card | `library.select.all` (per-item) | VZ-LIBRARY-001 | owner | item added to the selection; bulk bar appears | — | client-side only |
| `Select all` (`.`) / `Clear` (`Z`) | `library.select.all` | VZ-LIBRARY-001 | owner | whole filtered set selected / cleared | — | client-side only |
| `Add to album` (bulk) | `library.bulk.album` | VZ-LIBRARY-001, VZ-ALBUM-001 | owner of every selected photo | membership rows created; reported per photo | partial failure named per photo; successes are not rolled back | `album_items` rows |
| `Set visibility` (bulk) | `library.bulk.privacy` | VZ-LIBRARY-001, VZ-PRIVACY-001 | owner | visibility applied to all; caches purged | partial failure named per photo | `assets.visibility` + `visibility_version` bump + purge job |
| `Delete` (bulk) | `library.bulk.delete` | VZ-LIBRARY-001 | owner | destructive confirm → assets removed, cleanup job queued | partial failure names the photo that survived and why | assets removed; storage returned after cleanup |
| `Clear selection` | `library.select.all` | VZ-LIBRARY-001 | owner | selection emptied; bulk bar removed | — | none |
| Search field | `(new)` `library.search` | VZ-LIBRARY-001 | owner | grid filters; zero matches → filtered-to-zero state | request failed: error state with retry, filter preserved | none (URL query only) |
| Sort select | `(new)` `library.sort` | VZ-LIBRARY-001 | owner | grid reorders | — | user preference (proposed) |
| Filter chips (All / Public / Unlisted / Private / Not in an album) | `(new)` `library.filter` | VZ-LIBRARY-001 | owner | grid filters; chip shows the count | — | none |
| Filter chip `Needs attention` | `(new)` `library.filter.attention` | **NO LEDGER ID** | owner | shows processing-failed and stuck items | — | none — see open question O-13 |
| `Retry processing` on a failed card | `upload.retry` | VZ-MEDIA-001 | owner | processing re-runs | fails again: card keeps the reason | no duplicate asset |
| Error state `Try again` | `(new)` `library.list.retry` | VZ-LIBRARY-001 | owner | listing re-fetched | still failing: same state, count of attempts not shown | nothing was changed by the failed read |
| Empty state `Upload photos` | `shell.nav.upload` | VZ-UPLOAD-001 | owner | routes to `/upload` | — | none |
| Filtered-to-zero `Clear search and filters` | `(new)` `library.filter.clear` | VZ-LIBRARY-001 | owner | filters reset, full grid returns | — | none |

### 3.3 Photo page and lightbox viewer — V1, V2, V3, V4, V5

| Control | Action ID | Ledger ID | Required role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| `Close` / `Back to your library` (Esc) | `photo.viewer.close` | VZ-VIEWER-001 | anyone who may view | lightbox closes, focus returns to the originating thumbnail | — | none |
| `Previous` / `Next` (← →) | `photo.viewer.next` | VZ-VIEWER-001 | anyone who may view | moves within the list you arrived from | at either end: control disabled with a reason, not silently inert | none |
| Zoom in / out (`+` `−`), reset (`0`), fit | `photo.viewer.zoom` | VZ-VIEWER-001 | anyone who may view | scale changes; chip states the level and the arrow-key mode | derivative missing: falls back to the next-largest and says so | none |
| Pan (arrows when zoomed, drag, one-finger drag) | `photo.viewer.zoom` | VZ-VIEWER-001 | anyone who may view | image pans within bounds | — | none |
| Full screen (`F`) | `(new)` `photo.viewer.fullscreen` | **NO LEDGER ID** | anyone who may view | browser full-screen | refused by the browser: control reverts, no error toast | none |
| Details panel toggle (`I`) | `photo.exif.tab` | VZ-MEDIA-004 | anyone who may view, when EXIF is shown | panel opens / closes | EXIF hidden by policy: control absent, not disabled | none |
| `About` / `Exif` tabs | `photo.exif.tab` | VZ-MEDIA-004 | anyone who may view | panel switches | EXIF fetch failed: inline error inside the panel only | none |
| `Edit details` | `photo.edit` | VZ-LIBRARY-002 | owner | routes to `/p/{id}/edit` | — | none here |
| `Add to album` | `photo.add-to-album` | VZ-ALBUM-001 | owner | opens the add-to-album dialog | — | none until the dialog confirms |
| `Change visibility` | `photo.privacy` | VZ-PRIVACY-001 | owner | opens the asset privacy dialog | — | none until the dialog confirms |
| `Download original` | `photo.download` | VZ-DOWNLOAD-001 (**M3** per GAPS.md) | per owner/site permission | original streams | not permitted: control is absent, never a dead button | audited count — see open question O-1 |
| `Delete` | `photo.delete` | VZ-LIBRARY-001 | owner or moderator | destructive confirm → asset removed | refused (still processing): dialog stays open and names the reason | asset + derivatives removed; cleanup job; storage returned |
| `Show more` (long description) | `(new)` `photo.description.expand` | **NO LEDGER ID** | anyone who may view | text expands in place, panel scrolls, image does not move | — | none |
| `Retry processing` (state B) | `upload.retry` | VZ-MEDIA-001 | owner | processing re-runs | fails again: same state, same code | no duplicate asset |
| `Sign in` (not-available page) | — (`shell.nav.account` adjacent) | VZ-AUTH-001, VZ-AUTH-004 | anonymous | routes to `/login` with a return path | — | none |
| Visibility marker | — (display) | VZ-PRIVACY-001 | anyone who may view | states the level in words + icon | — | read-only |
| Metadata `Location` row | — (display) | VZ-MEDIA-004 | owner / audited staff only | states that it is withheld, per ADR-006 | — | read-only; GPS never enters a derivative |

**Reserved and deliberately absent from every viewer frame**, marked only as an annotation block:
favourite (VZ-FAVORITE-001, M2), rating (VZ-RATING-001, M2), comments (VZ-COMMENT-001, M2), share
and embed (VZ-SHARE-001/002, M3), report (VZ-REPORT-001, M2). None is drawn as a working control.

### 3.4 Albums — A1, A2, A3

| Control | Action ID | Ledger ID | Required role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| `New album` / `Create your first album` | `album.create` | VZ-ALBUM-001 | authenticated | album created (Private), routes to it | name empty: field error, dialog stays open | `albums` row |
| Album card / album title (both are the link) | `(new)` `album.open` | VZ-ALBUM-001 | anyone who may see the album | routes to `/a/{id}` | revoked grant: "not available" page | none |
| `Actions for the album “…”` (⋯) | `(new)` `album.menu` | VZ-ALBUM-001 | owner | menu with edit / privacy / cover / delete | — | none |
| `Add photos` | `(new)` `album.items.add` | VZ-ALBUM-001 | album owner | picker of own library → membership rows | partial failure named per photo | `album_items` rows |
| `Edit album` | `(new)` `album.edit` | VZ-ALBUM-001 | album owner | title/description saved | validation error inline | `albums` row |
| `Privacy & sharing` | `album.privacy` + `album.share-grant` | VZ-ALBUM-002 | album owner | opens the album privacy dialog | — | none until saved |
| `Set cover` | `album.cover` | VZ-ALBUM-001 | album owner | cover set | chosen photo is private while the album is public: refused with the reason | `albums.cover_media_id` |
| `Create sub-album` | `album.sub.create` | VZ-ALBUM-001 | album owner | sub-album created under this album | cycle or depth limit: refused with the reason | `albums.parent_id`, cycle-checked |
| `Move earlier` / `Move later` (per photo) | `album.reorder` | VZ-ALBUM-001 | album owner | position changes, saved immediately, announced | save failed: position reverts and says so | `album_items.position` |
| Drag reorder | `album.reorder` | VZ-ALBUM-001 | album owner | as above | — | as above |
| `Sort: manual` / sort select | `(new)` `album.sort` | VZ-ALBUM-001 | album owner | sort mode changes | — | `albums.sort_mode` |
| `Delete album` | `album.delete` | VZ-ALBUM-001 | album owner | destructive confirm → album removed, **photos kept**, sub-albums re-parented | refused: dialog stays open with the reason | album + memberships removed; **no asset deleted**; grants stop working |
| Breadcrumb links | `(new)` `album.breadcrumb` | VZ-ALBUM-001 | anyone who may see each ancestor | routes up the tree | ancestor not visible to this viewer: it is not rendered | none |
| Sub-album card | `(new)` `album.open` | VZ-ALBUM-001 | anyone who may see it | routes to the sub-album | — | none |
| Privacy filter chips | `(new)` `album.filter` | VZ-ALBUM-002 | owner | list filters | — | none |
| Empty-album `Add photos` | `(new)` `album.items.add` | VZ-ALBUM-001 | album owner | as above | — | as above |

### 3.5 Dialogs — D1, D2, D3, D4

| Control | Action ID | Ledger ID | Required role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Album checkbox (multi-select) | `photo.add-to-album` | VZ-ALBUM-001 | owner of the photo and of the album | album toggled in the pending set | — | none until confirm |
| `Filter your albums` | `(new)` `album.dialog.filter` | VZ-ALBUM-001 | owner | list narrows | — | none; it creates nothing |
| `Create and select` / `Create and add` | `album.create` | VZ-ALBUM-001 | authenticated | album created (Private) and pre-selected | name empty or duplicate: field error, dialog stays open | `albums` row |
| `Add to N albums` | `photo.add-to-album` | VZ-ALBUM-001 | owner | membership rows created, reported per album | partial: the failed album is named; successes stand | `album_items` rows |
| `Add anyway` (narrower album) | `photo.add-to-album` | VZ-ALBUM-001, VZ-PRIVACY-001 | owner | membership created; **photo visibility unchanged** | — | `album_items` only |
| Visibility radios — Public / Unlisted / Private | `photo.privacy` | VZ-PRIVACY-001 | owner | pending value set | — | none until Apply |
| `Apply` / `Apply to N photos` | `photo.privacy`, `library.bulk.privacy` | VZ-PRIVACY-001 | owner | visibility written, `visibility_version` bumped, purge queued | 409 or refusal: selection reverts to the stored value and says so | `assets.visibility`, caches/embeds/federation/IPFS reconciled |
| Album privacy radios — Public / Private / Link only / Password | `album.privacy` | VZ-ALBUM-002 | album owner | pending value set | — | none until Save |
| `Create link` (share grant) | `album.share-grant` | VZ-ALBUM-002 | album owner | grant created, URL shown once | — | `share_grants` row |
| `Revoke` | `album.share-grant` | VZ-ALBUM-002 | album owner | grant revoked; the link 404s immediately, cached responses included | — | `share_grants.revoked_at` |
| Album password entry (`Open album`) | `album.privacy` (recipient side) | VZ-ALBUM-002 | grant holder | album opens for this session | wrong password: field error + rate limit stated; same answer as a link that never existed | session capability only |
| `Cancel` / `Keep the photo` / `Keep the album` / `Keep them` | — (dialog dismiss) | VZ-A11Y-001 | anyone in the dialog | dialog closes, nothing changed, focus returns | — | none |
| `Delete photo` / `Delete album` / `Delete N photos` | `photo.delete`, `album.delete`, `library.bulk.delete` | VZ-LIBRARY-001, VZ-ALBUM-001 | owner | the stated deletion happens | partial failure names what survived and why; the dialog stays open | as §3.2 / §3.4 |
| Dialog close (×) | — (dialog dismiss) | VZ-A11Y-001 | anyone in the dialog | as Cancel | — | none |

---

## 4. Interaction notes

### 4.1 Viewer keyboard map (drawn in V2 as an on-canvas panel)

| Key | Action |
|---|---|
| `←` `→` | previous / next photo, within the list you arrived from |
| `+` `−` | zoom in / out (Fit → 100% → 200% → 400%) |
| `0` | reset to Fit |
| `F` | toggle full screen |
| `Esc` | close the lightbox and **return focus to the thumbnail that opened it** |
| `I` | show / hide the details panel |
| arrows **when zoomed past Fit** | pan |
| `Shift` + arrows **when zoomed** | change photo (the zoom chip states which mode is active) |
| `Tab` | cycles **inside** the lightbox only; the page behind is `inert` and `aria-hidden` |

### 4.2 Zoom and pan model

- **Pointer**: wheel or trackpad pinch zooms about the cursor; click-drag pans when zoomed past Fit;
  double-click toggles 100%.
- **Touch**: two-finger pinch zooms about the midpoint; one-finger drag pans when zoomed; double-tap
  toggles 100%. One-finger drag at Fit does **not** change photo — the prev/next buttons do, because
  a swipe that is also a pan is ambiguous.
- **Keyboard**: every one of the above has the equivalent in §4.1. `ui-controls.json`
  `photo.viewer.zoom` requires the keyboard alternative in terms (WCAG 2.5.7).
- The mode change (arrows pan vs arrows change photo) is **announced in the zoom chip**, never
  silent.
- The image is laid out `contain` at its intrinsic ratio. A panorama is bounded by stage width with
  top/bottom gutters; a very tall frame is bounded by stage height with side gutters (drawn in V3
  band D). `object-fit: cover` / `fill` and fixed `aspect-ratio` boxes are forbidden.

### 4.3 Focus order, trap and return

- **Photo page (V1/V4)**: skip link → TopNav → back / context → stage controls (prev, zoom −, zoom +,
  next) → title → owner actions → tabs → metadata → reserved annotation (not focusable).
- **Lightbox (V2/V5)**: focus moves to `Close` on open. Order: Close → counter (not focusable) →
  action cluster → prev → next → zoom − → zoom + → details. `Tab` wraps inside. `Esc` closes and
  focus returns to the exact originating thumbnail.
- **Dialogs (D1–D4)**: `role="dialog" aria-modal="true"`, labelled by its title. Focus moves in on
  open and is trapped; `Esc` closes; background `inert` + `aria-hidden`. **Initial focus is on
  Cancel**, never on the confirming or destructive action — drawn as the `Focus` Button variant in
  every dialog footer. Focus returns to the control that opened the dialog.
- **Bottom sheets (D4, V5)**: identical semantics. The sheet is anchored to the viewport bottom plus
  the safe-area inset and does **not** share the 12px offset occupied by the floating TabBar; the
  TabBar is inert while a sheet is open. In a destructive sheet the **safe** action is on top and
  keeps the initial focus, so the thumb's resting position is never on Delete.
- **Library grid**: arrows move between cards, `Space` toggles selection, `Shift`+arrow extends,
  `Enter` opens the viewer, `.` selects all, `Z` clears.
- **Album reorder**: `Alt`+`←`/`→` on a focused card, plus the two Move buttons, plus drag — three
  routes, so drag is never the only one.

### 4.4 Live regions

| Where | Politeness | What is announced |
|---|---|---|
| Upload batch | `polite` | start; each 25% step of the **batch**; every per-file completion; every failure; the final result. **Never a per-tick percentage.** |
| Per-file progress | — | `role="progressbar"` with `aria-valuenow` / `min` / `max` and an accessible name naming the file. Indeterminate omits `aria-valuenow`. |
| Processing → ready | `polite` | "Processing finished" when a card or the photo page updates itself. |
| Library selection | `polite` | "N photos selected" when the bulk bar appears. Focus is **not** stolen from the grid. |
| Library loading | `polite` | "Loading your library" once, then the result count. Grid carries `aria-busy`. |
| Bulk action result | `polite` | per-item outcome, e.g. "2 of 3 changed. 'Salt flats' was not changed because it is being processed." |
| Viewer photo change | `polite` | new photo's accessible name and position ("4 of 312"). |

No failure auto-dismisses. Assertive regions are not used: an upload is not an emergency.

### 4.5 Reduced motion (`prefers-reduced-motion: reduce`)

- Skeleton shimmer → a static tint. No pulse, no sweep.
- Indeterminate progress → a static 40% bar; the text label carries the state.
- Button `Loading` spinner → a static indicator; the accessible name stays stable.
- Lightbox: no cross-fade between photos, no Ken-Burns, no zoom easing — the image is swapped and
  the scale applied instantly. (`My Photos.html` scaled every thumbnail 1.04 on hover and
  `Upload Studio.html` scaled the drop zone; both are dropped rather than gated.)
- Drop zone drag-over: border colour and background tint only, no scale, no bounce.
- Bottom sheets and dialogs appear without a slide; the scrim appears without a fade.
- Card hover lift (`translateY(-2px)` in `My Albums.html`) is not reproduced at all.

### 4.6 200% zoom and 320px reflow

- At 200% browser zoom on 1440: the viewer top bar wraps to two rows, the caption clamps to one
  line, the owner-action cluster wraps (it is already a wrapping auto-layout), and the metadata
  panel stacks under the stage. Nothing is clipped and nothing scrolls horizontally.
- At 320px: the library grid falls to one column with the same shared row height; the album ordered
  grid does the same; the toolbar chips wrap; every dialog is a full-width sheet. **Not drawn** —
  see §9.
- Every control drawn here is at least 44×44 by construction (the `IconButton` root is 44×44 with a
  2px transparent focus pad around a 40×40 pill; `SelectionCheckbox` is 44×44 around a 24×24 box).
  `.btn-sm` at 30px and `.toggle` at 26px from the owner mockups are not reproduced.

---

## 5. Copy deck

Strings as drawn. They are proposals, not approved copy.

**Upload**
- "Upload photos" · "JPEG and PNG in this release. Every file is checked by its real bytes, not by
  its name or its type header."
- "Drag photos here" / "or" / "Choose files"
- "'Choose files' is a real file picker and the primary way in — reach it with Tab, open it with
  Enter or Space. You can also paste an image with Ctrl/⌘+V, or take one with your device camera.
  Dropping is an extra route, never the only one."
- "Accepted now: JPEG · PNG. Anything else is refused with the reason stated, before any bytes are
  sent."
- "This release accepts JPEG and PNG / RAW, TIFF, HEIC and WebP are later milestones. They are
  refused with that reason rather than being silently dropped."
- Queue states: "Waiting — 3 files ahead of this one" · "Uploading" · "Paused" + "Connection lost at
  38%. Resume continues from the last complete chunk — it does not start the transfer again." ·
  "Processing — building thumbnail, medium and display sizes" · "Ready — in your library" ·
  "Processing failed: the decoder stopped at the pixel bound (E_PIXEL_LIMIT). Nothing was added to
  your library and your storage was released." · "Rejected before upload: the name ends .jpg but the
  bytes are a PDF. Only real JPEG and PNG files are accepted in this release."
- Quota: "This batch needs 2.6 GB and you have 0.4 GB left" / "No upload session was created, no
  bytes were transferred and no storage was reserved. Remove some files from this batch, free space
  in your library, or ask an administrator to raise your limit." · "Held — this file was never
  started. Remove it from the batch or free space first." · "Your limit comes from your role and can
  be overridden per person by an administrator. It is never raised automatically and Vizra has no
  paid plan to upgrade to."
- Finished: "6 photos added" / "All six decoded, were given a thumbnail, medium and display size,
  and are stored. They will still be there after a restart." / "All six are Private, which is this
  instance's default for new uploads."

**Library**
- "Your library" / "312 photos · 12.4 GB · everything you own, whatever its visibility. Only you and
  an administrator acting in an audited context can see this page."
- Card states: "Processing / Thumbnail and display sizes are being made. This card updates itself."
  · "Could not be processed / The decoder stopped at the pixel bound. The original is safe; nothing
  else was changed." + "Retry processing"
- Empty: "Your library is empty / Upload a JPEG or PNG and it will appear here — private by default,
  and still here after a restart."
- Filtered to zero: "No photos match 'rooftop' in Unlisted / You have 312 photos. Clear the search,
  or switch back to All, to see them again." + "Clear search and filters"
- Error: "We could not load your library / The server did not answer in time. Nothing was deleted,
  moved or changed — this is a read that failed." + "Try again" / "What we tried"
- Selecting at 390: "Selecting — tap a photo to select it, tap Done to open photos again"

**Viewer**
- "Photo 4 of 312 · sorted by date taken · arrows move within this list"
- "6240 × 4160 · 3:2 · shown at 720 × 480" · "Fit · press 0 to reset" · "200% · arrows pan · 0 resets"
- "Only you can open this photo, its original and its thumbnails."
- "Location — Not shown — GPS is never published" / "Location is stored with your original and is
  never written into a thumbnail, display size, embed, feed or federated copy. It stays 'only me'
  until you widen it, and there is no control to widen it in this release."
- Processing: "Still being processed / Your original is stored and safe. The thumbnail and display
  sizes are being built and this page will show them as soon as they exist — it will not spin
  forever. If processing fails you will be told why."
- Failed: "This photo could not be processed / The decoder stopped at the pixel bound
  (E_PIXEL_LIMIT) after three attempts. Your original is stored and unchanged, and its storage is
  still counted. Nothing was published."
- Not available (identical for anonymous and for another member): "This page is not available / The
  link may be wrong, or the photo may have been removed. If you have an account on this instance,
  signing in may give you access."

**Albums**
- "Casa Barragán" / "24 photos · 2 sub-albums · updated 3 days ago"
- "Link only: anyone with the address can open this album page. It is excluded from listings,
  search, feeds, sitemaps and federation — and it still shows each viewer only the photos they are
  allowed to see."
- "Manual order — drag a photo, or use its Move earlier / Move later buttons, or focus a photo and
  press Alt+← / Alt+→. Every change saves immediately and says so."
- Empty album: "This album has no photos yet / Empty albums are allowed and keep their cover,
  description and sharing link."
- Empty index: "You have no albums yet / An album groups photos without copying them, and can hold
  sub-albums. Photos keep their own visibility inside it."

**Dialogs**
- Add to album: "'Stairwell, Casa Barragán' can be in as many albums as you like — it is not copied.
  Adding never changes what a photo is allowed to show: a private photo stays private inside a
  public album." · "Add to 2 albums" · "Added to 1 of 2 albums / 'Mexico Modern' was updated.
  'Client — Ortega' was not: you are no longer its owner. Nothing else changed."
- Asset visibility: "Who can see this photo?" · Public — "Anyone can find it: listings, search,
  explore, tags, feeds, the sitemap and federation." · Unlisted — "Anyone with the link can open it.
  Kept out of listings, search, explore, tags, feeds, the sitemap, federation and IPFS. Its
  thumbnails are never cached by a CDN." · Private — "Only you, and an administrator acting in an
  audited context." · Warning — "Making it narrower takes effect everywhere / Caches and CDN copies
  are purged, embeds stop resolving, any federated copy is withdrawn, and it disappears from other
  people's favourites views. Copies someone already downloaded cannot be recalled."
- Album privacy: "Privacy & sharing — 'Casa Barragán'" · "Album privacy controls who can open THIS
  album page and its listing. It never changes what each photo is allowed to show." · Password —
  "Anyone with the address AND the password. Attempts are rate limited; the password is stored
  hashed and is never shown again after you set it." · "Revoking a link stops it immediately,
  including cached responses."
- Destructive: "Delete 'Stairwell, Casa Barragán'? / This removes the photo, its original file and
  every size made from it. It is removed from the 2 albums it is in — those albums and their other
  photos are kept. Its storage is returned once the cleanup job has run. This cannot be undone." +
  "Keep the photo" / "Delete photo".
  "Delete album 'Casa Barragán'? / This deletes the album only. All 24 photos in it stay in your
  library with their own visibility unchanged… Its 2 sub-albums are NOT deleted — they move up to
  'Mexico Modern'. Every share link for this album stops working immediately." + "Keep the album" /
  "Delete album".

---

## 6. Verification performed

- **Structural audit** over all 22 frames on `32:2`, run against the live file after the last edit:
  **0** nodes overflowing their frame horizontally, **0** collapsed auto-layout containers,
  **0** unbound solid paints (every fill and stroke resolves through a `Color` variable).
- **Text overflow audit** over every `TEXT` node inside an instance: after two fixes, no text node
  exceeds its field. The remaining equal-width rows are `FILL`-width labels, not overflow.
- **Percentage audit**: every `ProgressBar` instance's drawn fill fraction equals the percentage its
  label states (62/62, 38/38, 62/62 in U2; variant-fixed elsewhere).
- **Screenshots taken and visually inspected** (short-lived `get_screenshot` URLs, inspected
  in-session): U1, U2, U3, U4, U5, U6, L1, L2, L3, L4, V1, V2, V3, V4, V5, A1, A2, A3, D1, D2, D3,
  D4, plus the new component sets.

Defects found by looking and then fixed:

1. `U1` content column collapsed to 10px — `resize()` had pinned `layoutSizingVertical` to FIXED.
   Repaired on 12 containers.
2. `ProgressBar` fill did not scale with a widened track, so a bar labelled 62% drew 30%. Repaired
   with `constraints: SCALE`, then — because the plugin API cannot resize a node nested inside an
   instance — every percentage was made a **variant** and every label rewritten to match what its
   variant draws.
3. `VisibilityBadge` "On media" icons were dark on the dark scrim chip. Recoloured to
   `color/on-media`.
4. `SelectionCheckbox` box boundary at 1.5px was not perceivable at 1:1. Raised to 2px
   (`stroke/focus`); the unchecked edge is now unambiguous in both themes.
5. `U4` result grid was a ragged wrap with two identical filenames. Rebuilt as a justified row of
   uniform-height, ratio-preserving thumbnails with distinct names.
6. `L1` sort field helper text collided with the search field's helper. Field widened to its natural
   280.
7. `V1` stage and the photo placeholder were both `color/bg-tint`, so the photo had no edge. Stage
   changed to the theme-invariant near-black decided in departure 19.
8. `V3` "Back to library" was a Quiet button on the near-black stage and was effectively invisible.
   Swapped to Secondary.
9. Long-content demonstrations clamped to one line because `textTruncation` was set after
   `maxLines`. Order corrected; clamps now render at 2 / 3 / 4 lines as specified.
10. `V5` actions sheet overlapped and clipped the photograph. The image is now fitted to the space
    above the sheet.
11. `D3` destructive dialogs inherited the component's "The albums themselves are not deleted."
    strip on all three uses. Each now states what survives that specific deletion.
12. Two `TextField` helper strings were long enough to be clipped by the dialog's `clipsContent`.
    Shortened.

---

## 7. Open questions for the owner

| # | Question |
|---|---|
| O-1 | **`Download original` in the viewer.** The D2b brief asks for it; `GAPS.md` and the ledger place `VZ-DOWNLOAD-001` in **M3**. It is drawn in V1/V4/V2/V5. Keep it in M1 (and implement the permission model and audited count now), or remove it from these frames? It must never ship as a dead control. |
| O-2 | **Quota numbers.** The frames use 20 GB per user, 100 MB per file, 50 files per batch as placeholders. ADR-005 records the real defaults as `[to confirm in M0]`. |
| O-3 | **Derivative sizes.** "shown at 720 × 480" and the thumbnail sizes are placeholders; ADR-006 records display long-edge and thumbnail sizes as `[to confirm in M0]`. |
| O-4 | **Album depth limit.** ADR-007 sets a depth limit of 5 for collections and `[to confirm in M0]` for albums. The breadcrumb and sub-album cards assume at least 3 levels. |
| O-5 | **Default visibility for new uploads.** The frames say Private and call it "this instance's default". Confirm the shipped default of the setting `VZ-UPLOAD-001` refers to. |
| O-6 | **Geo-privacy control in M1.** ADR-006 Q-038 defaults location to "only me". The viewer states there is **no control to widen it in this release**. Confirm that is right, or the metadata panel needs an owner control. |
| O-7 | **Deleting an album with sub-albums.** The confirmation asserts sub-albums are **re-parented to the grandparent**, not deleted. ADR-007 does not rule on this. Needs a ruling before the copy is trusted. |
| O-8 | **Share-grant expiry in M1.** A grant is drawn with "expires 30 Sep". `VZ-ALBUM-002` names creation, listing and revocation but not expiry. Is expiry in M1? |
| O-9 | **Album password: is it set in the same dialog?** Drawn as a radio option whose consequence text says the password is set here and never shown again. The set-password field itself is not drawn. |
| O-10 | **Selection mode at 390.** Drawn as an explicit Select → Done mode. Confirm, versus long-press to enter selection. |
| O-11 | **The theme-invariant near-black photo stage** (departure 19). This is the light/dark decision `GAPS.md` demands be made deliberately. Sign off or reject. |
| O-12 | **Exif as a tab or a section.** Drawn as `About` / `Exif` tabs per `VZ-MEDIA-004` ("Exif tab"). Confirm rather than one continuous panel. |
| O-13 | **The `Needs attention` library filter** (processing-failed / stuck items) has **NO LEDGER ID**. `VZ-LIBRARY-001` lists untagged, not-in-album, private, NSFW, media type, date range. Add it to the ledger, or drop the chip. |
| O-14 | **`Show more`, full screen (`F`) and the details toggle (`I`)** have **NO LEDGER ID**. Add rows to `ui-controls.json`, or drop them. |
| O-15 | **Lucide export names are still unverified** (carried from D1 §10.1). Seven of the 37 were renamed in recent releases. `vizra-user` must resolve them against the pinned package before the typed registry ships. |

---

## 8. Ledger coverage

| Ledger ID | Where it is designed | Not covered here |
|---|---|---|
| VZ-UPLOAD-001 | U1–U6 | server-side validation, idempotent finalize |
| VZ-UPLOAD-003 | U1, U5 (picker, paste, camera, drop) | — |
| VZ-QUOTA-001 | U1–U6 quota meter, U3/U6 refusal | `/settings/storage` page (D2a / later) |
| VZ-MEDIA-001 | U2 processing rows, L1 processing card, V3 bands A/B | — |
| VZ-MEDIA-003 | V1/V4 "Dimensions · 3:2", V3 band D | ICC and transparency are pipeline facts, not UI |
| VZ-MEDIA-004 | V1/V4 metadata panel, `MetadataRow Kind=Withheld` | `/admin/settings/uploads` strip policy |
| VZ-VIEWER-001 | V1–V5 | album strip inside the viewer; share/embed tabs (M3) |
| VZ-LIBRARY-001 | L1–L4, D3 | bulk edit panel (VZ-LIBRARY-002, M3) |
| VZ-ALBUM-001 | A1–A3, D1 | — |
| VZ-ALBUM-002 | A1, D2, D4 | `/settings/shares` listing across all albums |
| VZ-PRIVACY-001 | D2, D4, every visibility marker, V3 band C | `/settings/privacy` defaults |
| VZ-A11Y-001 | §4 throughout; focus states drawn on cards, checkboxes and dialog Cancel | axe run and manual screen-reader review (implementation) |
| VZ-RESPONSIVE-001 | 390 and 1440 for every surface | 320px reflow and 200% zoom frames not drawn |
| VZ-CONTROLS-001 | §3 control matrix | `ui-controls.json` not edited by this work |

---

## 9. What is not finished, and what I could not verify

Recorded honestly.

1. **Nothing here is approved or reviewed.** Single-pass build by one agent. `AGENTS.md` requires
   independent review. Status **PROPOSED**.
2. **No 320px reflow frame and no 200% zoom frame were drawn.** Both behaviours are described in
   §4.6 and the layouts are built from wrapping auto-layout, but neither is demonstrated.
3. **Dark mode is drawn for the library (L4) and the viewer (V2, V5) only.** Upload, albums and
   dialogs are Light-only. They are token-bound and should resolve, but that is an assumption, not a
   capture.
4. **`ProgressBar` percentages are variant-fixed** because the Figma plugin API silently refuses to
   resize a node nested inside an instance. Production must compute the real fill width. Every label
   in this file matches what its variant draws, but the component cannot express an arbitrary value.
5. **Hover and pressed states were not drawn for the new components.** `SelectionCheckbox` has
   Default and Focus only; `UploadRow`, `BulkBar`, `MetadataRow`, `VisibilityBadge` and
   `AspectPlaceholder` have no interaction states. The D1 primitives they contain do.
6. **No real photographs.** Every image is an `AspectPlaceholder`. The on-media contrast figures are
   the worst-case computed bounds from D1 §4 (15.3:1 over a pure-white photograph); they have **not**
   been confirmed against actual photographs, and `VZ-A11Y-001` asks for contrast "over real
   backings".
7. **Motion is still only tokenised.** `motion/fast|base|slow` exist; there is no easing curve set
   and no per-component transition map. §4.5 says what must *not* animate; it does not say how the
   permitted motion moves.
8. **No prototype wiring.** No frame links to another; the flows are documented, not clickable.
9. **Screenshots are not archived under `docs/evidence/`.** They were inspected in-session through
   short-lived URLs. If the war room needs durable visual evidence it must be re-captured and
   committed.
10. **The 44×44 target claim is by construction, not measured** on every composed control. The
    `IconButton` and `SelectionCheckbox` roots are 44×44; chips, tabs and text links were not
    individually measured.
11. **The password-album success state is not drawn** — only the entry field and its error.
12. **Search and filter interactions are not designed** beyond the resting state: no typeahead, no
    recent searches, no per-facet removal affordance.
13. **The file is still a draft, not a published Figma library** (D1 §10.8 unchanged). D2a and D2b
    work in the same file; `search_design_system` will not find these components from another file.
14. **Icon glyphs remain D1 stand-ins**, not Lucide's own paths. The contract is the name, size,
    stroke and semantic role; do not export these vectors into the codebase.
15. **`docs/quality/ui-controls.json` was not edited.** Eleven action ids in §3 are marked `(new)`
    and four controls carry **NO LEDGER ID**. Reconciling that file is a separate, owner-authorized
    change.
