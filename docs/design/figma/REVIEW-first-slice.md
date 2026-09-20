# Review — first slice (D1 library + D2a auth/system + D2b library/viewer/albums)

**Verdict: FIX FIRST.** Do not put this in front of the owner as one product yet.

| | |
|---|---|
| **Reviewer** | Independent; built none of D1, D2a or D2b |
| **Figma file** | `JXgRItauynmT0g8vSJB3oR` — read-only access confirmed (`whoami` → `yegamble@gmail.com`, team `984598513556028019`) |
| **Reviewed** | Pages `4:28`, `4:32`, `26:6`, `27:2` (46 frames), `32:2` (22 frames) |
| **Date** | 2026-09-20 |
| **Nothing was edited.** | Read methods only: `get_metadata`, `get_screenshot`, `get_variable_defs`, `search_design_system` |

## Method

Screenshots rendered and visually inspected: `4:28`, `4:32`, `8:104`, `26:6`, `31:86`, `33:65`,
`37:301`, `37:632`, `38:2168`, `39:1707`, `41:1050`, `41:1175`, `42:1078`, `42:1159`, `42:3331`,
`43:3000`, `43:3061`, `43:3307`, `44:3869`, `44:3920`, `46:1576`, `47:1649`, `48:1877`, `50:1860`,
`52:2320`, `53:2468`, `54:2680`, `54:2808`. Pixel measurements were taken from the rendered PNGs;
colour claims were resolved through `get_variable_defs` on the specific node, not from the token
tables. A parent-relative geometry audit was run over every node on both product pages.

**Node ids spot-checked: 28 of 28 correct** (`30:935`, `30:191`, `28:585`, `12:263` by metadata;
the rest by successful render at the stated name and size). The hand-offs' node references are
reliable — that part of the hand-off is trustworthy.

**Verdict rationale.** The thinking is better than the drawing. The copy, the privacy semantics, the
error and partial-failure patterns, and the destructive-confirmation content are the strongest part
of this work and mostly ready. But the two pages are not one product — they ship two different
application shells — and three controls on the file's own critical path (zoom, selection, the
storage meter) are drawn wrong in a way an owner will see in the first two minutes. Those are
mechanical fixes, not redesigns. Expect one focused fix round, not a rebuild.

---

## What is genuinely good

Stated plainly, not to soften what follows.

1. **The privacy and refusal semantics are the best thing in the file.** `47:1649` band C draws a
   byte-identical 404 for anonymous and signed-in members and says so; `53:2468`'s password dialog
   reveals nothing about the album before the password is entered and gives the same answer for a
   revoked link as for one that never existed; the asset-visibility dialog states the *consequences*
   of each level at the point of choice rather than in help text elsewhere. This is genuinely
   designed, not styled.
2. **Destructive confirmations (`54:2680`) are excellent.** Each names the object by its title,
   states the blast radius in counts, states what *survives*, says it cannot be undone, and puts the
   initial focus ring on the safe button with a label that restates the safe outcome ("Keep the
   photo", not "Cancel"). The partial-failure dialog names the item that did not delete and does not
   claim success.
3. **The upload queue (`33:65`) treats failure as a first-class state.** Seven row states, each with
   its own reason string and its own recovery control, no toast, no auto-dismiss, and copy that says
   what was *not* changed ("Nothing was added to your library and your storage was released").
4. **Aspect ratio is honoured where it matters.** `47:1649` band D demonstrates a panorama bounded by
   stage width and a tall frame bounded by stage height, neither cropped; the 1440 library grid
   (`38:2168`) shares a row height and varies card width, which is the right model.
5. **Two empty states, not one.** `41:1050` distinguishes genuinely-empty from filtered-to-zero with
   different copy and different recovery actions.
6. **"Feature unavailable" is marked, not implied.** `43:3000`'s account banner and `38:670`'s
   registration-closed banner name what is missing and why, instead of leaving dead controls. The
   `RESERVED — NOT IN M1` block on `44:3869` marks where favourite and rating will sit without
   drawing them as working controls — Favorite and Rating are correctly absent from every M1 frame.
7. **D2a's page is geometrically clean**: the parent-relative audit found **0** overflows and **0**
   sub-44px interactive controls across all 46 frames.
8. **Dark mode is authored, not inverted**, and `41:1175` holds up: the accent moves up the ramp, the
   status colours remain legible, and nothing reads as a tinted screenshot of the light theme.

---

## (a) FIX BEFORE THE OWNER SEES IT

Ordered by severity.

### A1 — Two different application shells. D2b uses the pre-M1 nav D2a deliberately replaced

**Frames:** all nine 1440 frames and all five 390 frames on page `32:2`; compare page `27:2`.
**Component evidence:** instance census of page `32:2` → `TopNav` ×11, `TabBar` ×5, `AppBar / M1` ×0.
Census of page `27:2` → `TopNav / M1` ×14, `AppBar / M1` ×9, `TabBar / M1` ×7.

**What I saw.** On `4:28` the two nav families now sit side by side. On the left, D1's originals:
`TopNav` (`15:74`) with a full-width "Search photos, albums and people" field, an "Explore" link, a
notifications bell **carrying a red unread dot**, and an empty avatar; `TabBar` (`15:32`) labelled
**Home / Search / Upload / You**. On the right, D2a's replacements: `TopNav / M1` (`30:770`) —
wordmark, Library, Albums, upload — and `TabBar / M1` (`30:935`) — **Library / Albums / Upload /
Account**.

D2b used the left-hand pair on every frame. `38:2168`, `41:1175`, `44:3869`, `47:1649`, `50:1860`,
`51:2031`, `32:3`, `33:65`, `36:332`, `36:514` all render the search field, "Explore", and the belled
red dot. `42:3331` (library at 390) renders a tab bar reading **Home / Search / Upload / You** under
a page titled "Library" — the selected tab does not match the page it is on. `48:1714` and `51:2276`
do the same.

At 390 there is a **third** top bar: `42:3331` composes a local app bar ("Library" + a search icon
button + an upload icon button) that is neither D1's `TopNav` nor D2a's `AppBar / M1`, and carries
no skip link.

**Why it matters.** This is the single reason the two pages do not read as one product. It also
breaks three hard rules at once: navigation leads to four destinations that do not exist at M1
(search `VZ-SEARCH-001` M3, explore `VZ-EXPLORE-001` M3, notifications `VZ-NOTIFY-001` M2, public
profile `VZ-PROFILE-001` M2); the red dot on the bell is a **fabricated metric** implying unread
notifications on an instance with no notification system; and D2a's written rationale for cloning the
component — "an instance cannot remove a child from a component" — is exactly why this cannot be
papered over at implementation time.

**Fix.** Swap every `TopNav` instance on page `32:2` for `TopNav / M1`, every `TabBar` instance for
`TabBar / M1`, and replace the local 390 bar in `42:3331` with `AppBar / M1`. Then rename D1's
`TopNav`/`TabBar` to `TopNav (M2+, not for M1)` / `TabBar (M2+, not for M1)` so the next agent cannot
pick them up by accident.

### A2 — Zoom in and zoom out are invisible and indistinguishable in light mode

**Frames:** `44:3920` (V1 zoom cluster, 1440), `48:1747` (V4 zoom cluster, 390).

**What I saw.** Rendered at 4× and inspected: the two buttons at the bottom right of the photo stage
are **identical** — a bare white magnifier ring with a stub handle, with no `+` and no `−` visible in
either. Neither button communicates its direction, and the pair cannot be told apart.

**Root cause, measured.** `get_variable_defs` on `44:3920` and `48:1747` both return
`--vz-on-media: #ffffff` **and** `--vz-ink: #0e1218`. `icon/ZoomIn` (`5:106`) resolves only
`--vz-ink`. The glyph's ring is overridden to `color/on-media` inside the `On media` IconButton
variant, but the `+`/`−` bar remains bound to the **theme-dependent** `color/ink`. On the
theme-invariant `color/on-media-scrim` chip (`#05070c` @ 88%), light-mode `color/ink` (`#0e1218`)
computes to **1.07:1** — invisible. The same instances read correctly on `46:1649` only because V2 is
forced to Dark, where `color/ink` resolves to `#f4f5f8`. The icons themselves are fine: on `4:32`
both glyphs show their `+`/`−` clearly.

**Why it matters.** This is the product's centrepiece control, it fails in the default theme, and the
failure is silent — the dark-mode frame that was inspected during the build renders correctly. It
also disproves the general assumption in `41:1175`'s design note: a control is only safe on media if
*every* paint inside it uses the on-media tokens.

**Fix.** Bind every vector inside the `On media` IconButton variant to `color/on-media`, then sweep
all 37 icons for multi-vector glyphs used in that variant (`ZoomIn`, `ZoomOut`, `FolderPlus`,
`CircleCheck`, `CircleAlert`, `Info`, `Images` are the likely set) and re-render `44:3869` and
`48:1714` in Light.

### A3 — The selection checkbox's off state is not perceivable in light mode

**Frames:** `38:2168` vs `41:1175`; component `SelectionCheckbox` (`28:81`).

**What I saw.** Cropped the same pixel region from both frames at 3×. In **light** mode the unchecked
box is a solid near-black rounded square with **no boundary and no interior** — it reads as a smudge,
not a control. In **dark** mode the identical component shows a clear 2px white ring and is
unmistakably a checkbox. The checked state has a white border in dark and none in light.

The cause is visible in the crop: the ring is `color/on-media` white with an outside stroke align, so
on a light card (and on any light photograph) it sits on near-white and disappears, leaving only the
near-black fill.

**Why it matters.** The design note on `41:1175` asserts "the visibility marker and the selection
checkbox look identical in both themes". They do not, and the claim is what stopped this being
caught. Over real photographs the control will flicker between "black blob on a light photo" and
"white ring on a dark photo" with no stable reading, and the off state — the one a person has to
recognise before they can select anything — is the weaker of the two.

**Fix.** Give the resting box the same dual ring D1 §4 already specifies for focus on media
(`0 0 0 2px on-media-scrim, 0 0 0 4px on-media`, or its Figma equivalent), then re-render over a pure
white and a pure black backing and record both.

### A4 — The storage meter draws roughly half of what it says

**Frames:** `42:1078` (near limit), `42:1159` (full); component `Meter` (`31:86`).

**What I saw.** Measured from the rendered PNGs by scanning the fill run against the track run:

| Frame | Label states | Bar draws |
|---|---|---|
| `42:1078` | "18.2 GB of 20 GB" · "Nearly full — 1.8 GB free" | **44%** |
| `42:1159` | "20 GB of 20 GB" · "Storage is full." | **48%** |

The `Meter` component set at `31:86` is correct at its natural width (62% / 91% / 100% render
accurately). The instances on the quota pages are resized to 670 wide and the fill does not scale
with the track.

**Why it matters.** This is the same Figma instance-resize trap D2b hit and documented (their §6
defect 2: "a bar labelled 62% drew 30%"). D2a's audit checked overflow, clipping, collapsed layout
and unbound paints, but never checked that a data bar draws its own number. A meter that says "full"
while drawing half is the definition of a fake metric, and it is on the frame most likely to be
screenshotted into a release note.

**Fix.** Make the drawn fraction part of the `Level` variant at the width actually used, or set the
fill width explicitly on each instance; then re-measure all six quota frames (`42:1012`, `42:1078`,
`42:1159`, `42:1238`, `42:1325`, `42:1450`). Add "drawn fraction equals stated fraction" to the audit
list — D2b already runs this check on `ProgressBar`.

### A5 — The 390 bottom sheets contradict their own stated rule and draw focus around the wrong box

**Frame:** `54:2808`.

**What I saw.** The frame's own design note reads: *"Every control in a sheet is full width and at
least 44px tall."* Every button drawn is **natural width, left-aligned**: "Save" ≈ 85px, "Cancel"
≈ 130px, "Keep the album" ≈ 175px, "Delete album" ≈ 160px — each sitting inside a **full-width
(390px) focus/hit wrapper**, so the 2px focus ring encloses a band three times wider than the
control it indicates. "Create a new album" is also indented ~30px further left than the checkbox
rows and the buttons, so nothing in the sheet shares a left edge.

Separately, the destructive sheet titles itself **"Delete album "Casa Barragán"?" in `color/danger`
red with no icon**, while the same dialog at 1440 (`54:2680`) uses `color/ink` plus a red
`TriangleAlert`. At 390 the destructive signal is carried by colour alone.

**Why it matters.** The focus/hit mismatch is precisely the defect D2a found and repaired on its own
page (their §9 defect 3). A focus ring that does not outline the focused control is a WCAG 2.4.7
failure in practice, and the colour-only destructive title breaks the "nothing relies on colour
alone" rule on the one dialog where it matters most.

**Fix.** Make every sheet button fill the sheet width, stack them, align every element to one left
edge, and give the 390 destructive title the same icon-plus-ink treatment as `54:2680`.

### A6 — Three frames are clipped; the overflow audits measured the wrong box

**Frames:** `53:2468`, `52:2320`, `48:1877`.

**What I saw.** A parent-relative geometry audit (every node against its *immediate* parent, not
against the top-level frame) found:

| Node | Name | Overflows parent by |
|---|---|---|
| `53:2638` | dialog: Asset visibility — applying and failed | **+24px horizontal** (parent `53:2471`, w=1344) |
| `52:2543` | dialog: Add to album — narrower album | **+24px horizontal** (parent `52:2467`) |
| `48:1904` | actions sheet (focus trapped, Esc / swipe down closes) | **+16px vertical** (parent `48:1878`, the 390 × 844 viewport) |
| `51:2118`, `51:2142`, `51:2189`, `51:2216` | cover col | +2px horizontal each |

Rendered and cropped `53:2638` at 3×: the dialog has **no right border**, the error banner runs off
the edge, and the "Try again" button is cut. `48:1904` means the bottom of the V5 actions sheet —
the area holding "Delete" and the safe-area inset — sits **below the 844px fold**.

**Why it matters.** Both hand-offs claim "0 offenders" for horizontal overflow. Both audits compared
descendants against the *top-level frame's* box, which every one of these passes (48 + 928 + 440 =
1416 < 1440). Neither checked intermediate containers, so nothing caught it. The published
verification claim is therefore wrong, which matters as much as the clipping.

**Fix.** Widen the rows (`53:2471`, `52:2467`) to 1368 or reduce the dialog gap; raise `48:1878` or
shorten the sheet; re-run the audit **parent-relative** and restate both §Verification sections.

### A7 — The phone lightbox has no zoom control at all

**Frame:** `48:1877`. Metadata confirms **no `zoom-cluster` node exists** in V5, while V4
(`48:1714`) has one at `48:1747` and V2 (`46:1576`) has one at `46:1649`.

**What I saw.** The 390 lightbox offers Close, prev, next, a "More actions" affordance and a sheet
containing Edit details / Add to album / Change visibility / Download original / Show Exif / Delete.
There is no zoom in, zoom out, reset, fit, or zoom-level chip anywhere, so the zoom state is never
stated on a phone either.

**Why it matters.** `DESIGN_BRIEF.md` requires "viewer zoom/pan … understandable on small screens",
and `vizra-design` names "a viewer control that disappears on a phone" as a hunt-for failure class.
Pinch is described in D2b §4.2, but WCAG 2.5.7 requires a single-pointer alternative to a
multi-point/drag gesture — the `+`/`−`/`0` buttons *are* that alternative and they are the thing that
was dropped.

**Fix.** Put the zoom cluster and the zoom-level chip into `48:1877`, on the stage, at 44×44, and
state the reset path in the chip as V2 does.

### A8 — Implementation notes are drawn inside real components, where a builder will ship them

**Frames:** `33:65`, `39:1707`, `50:1860`, `47:1649`, `41:1050`.

**What I saw.**
- `33:65` — the live-region banner's body text reads
  `aria-live="polite" · announces start, each 25% step of the batch, every completion and every failure — never a per-tick percentage.`
  That string is inside the `Banner`, styled as product copy.
- `39:1707` — the password field's **helper text** reads "Initial focus lands here, not on a button.
  Enter submits.", and the dialog's footnote reads "Escape closes this dialog and returns focus to
  the control you were using; a persistent 'You are signed out' banner then replaces it…".
- `50:1860` — the breadcrumb's last crumb is literally "Casa Barragán **(you are here)**".
- `47:1649` — "prompt 03: 'Surface processing failure instead of leaving an endless spinner.'" is
  drawn on the canvas, quoting an internal prompt file.

**Annotation styling is also inconsistent three ways**, which is why this happened: D2a uses a dashed
box headed `DESIGN NOTE — NOT PRODUCT UI` (`42:1078`); D2b uses solid `accent-soft` blocks
(`38:2168`); and `33:65` puts an annotation (`EVERY ROW IS OPERABLE`) in a **white bordered card
visually identical to the real `STORAGE` card beside it**.

**Why it matters.** `DESIGN_BRIEF.md` makes the Figma file the design source once approved. Every one
of these strings is inside a component a builder will implement from, and `(you are here)` is a
literal instruction to render text that `aria-current` should carry.

**Fix.** Move all four strings out of components into annotations, and adopt one annotation style —
D2a's dashed `NOT PRODUCT UI` box is the clearest — across both pages.

### A9 — Delete is consistently the most prominent control on the page

**Frames:** `44:3869`, `50:1860`, `46:1576`, `48:1877`.

**What I saw.**
- `44:3869` — five owner actions; "Edit details", "Add to album", "Change visibility" and
  "Download original" are outlined Secondary, and **"Delete" is the only filled button on the whole
  photo page**.
- `50:1860` — the album action row is `Add photos` (blue) + four Secondary + **`Delete album` filled
  red**, so the two loudest controls on an album are "add" and "destroy".
- `46:1576` — the lightbox top bar is seven **unlabelled** icon buttons in a row; the trash sits
  immediately beside download with no separation, no chip, no grouping.
- `48:1877` — "Delete" is the bottom-most control in the sheet, i.e. the one nearest the thumb.

**Why it matters.** Every one of these is confirmed, so it is recoverable — but visual hierarchy is
the first line of defence, and here it points at the destructive action on four separate surfaces.

**Fix.** Make Delete a `Quiet`/`Danger-quiet` treatment on the page, separated from the constructive
cluster (a divider or an overflow menu); give the lightbox icon row a separated destructive slot;
move Delete off the thumb-resting position in the 390 sheet.

### A10 — Duplicate and near-duplicate components across the two pages

| Concept | D2a built | D2b built | Problem |
|---|---|---|---|
| Standing quota | `Meter` (`31:86`), 3 `Level` variants, documented `role="meter"` | `ProgressBar` (`28:58`) with `Near limit (92%)` and `Full (100%)` variants | Two components for one job, with a semantic argument (`meter` vs `progressbar`) written into only one of them. On `33:65` the storage bar is **visually identical to the in-flight upload bar** — a standing quantity and an operation in flight look the same |
| Visibility indicator | — | `VisibilityBadge` (`26:80`), 80×28 | D1's `visibility marker`, 73×26, is used on library cards (`38:2168` ×10, `41:1175` ×10, `42:3331` ×6); `VisibilityBadge` is used in albums, viewer and dialogs. Two badges 2px apart, in one product, sometimes **in the same frame** (`44:3869`, `50:1860`, `51:2276`) |
| Selection control | — | `SelectionCheckbox` (`28:81`) | Coexists with D1 `Checkbox` (`10:66`); both appear on page `32:2` |
| Where M1 additions live | appended to D1's own pages `4:28`, `4:30`, `4:32` | a new page `Components · M1 additions (D2b)` (`26:6`) | Two homes for one library layer |

Also orphaned: **D1's `PhotoCard` (`12:263`, 9 variants incl. `Sensitive` and `Loading`) is
instantiated zero times on page `32:2`.** D2b built its own card instead — reasonably, since
PhotoCard's aspects are 3:2 / 1:1 / 4:5 and the grid needs 3:2 / 2:3 / 1:1 / 16:9 / 3:1 — but nothing
records that, and PhotoCard's `Sensitive` safety-blur state therefore appears nowhere in the slice.

**Fix.** Pick one component per concept, delete or clearly deprecate the other, and give the quota
bar a visual treatment that is not the upload bar. Either extend `PhotoCard` to the five aspects and
use it, or mark it superseded and record where the `Sensitive` state now lives.

### A11 — "Quiet" controls read as static text, including navigation and one destructive action

**Frames:** `37:301`, `37:632`, `39:1707`, `38:2168`, `33:65`, `44:3869`, `53:2468`, `42:3331`,
`50:1860`, `47:1649`.

**What I saw.** The Quiet button variant renders as `color/ink` text with no underline, no border, no
accent and no icon — visually identical to the body copy beside it. Drawn this way: "Show password"
and **"Create an account"** (`37:301`, `37:632`); **"Sign out"** and "Not you?" (`39:1707`);
"Clear selection" (`38:2168`); "Retry all failed" and "View" (`33:65`); "Show more" and
**"Back to your library"** (`44:3869`); **"Revoke"** (`53:2468`); "Done" (`42:3331`); "Done
reordering" (`50:1860`); "Go to the home page" (`47:1649`).

On `37:301`, "New to this instance?" (grey) and "Create an account" (black) differ only in tint —
there is nothing to tell a person the second one is clickable.

**Why it matters.** `DESIGN_BRIEF.md`: "Native buttons for actions, links for navigation… Do not rely
on hover-only tooltips, color alone, or an unlabeled clickable div." Several of these are
navigation and should be accent-coloured links; "Revoke" is destructive and currently has the weakest
affordance on its surface; "Back to your library" is the only exit from the photo page.

**Fix.** Give Quiet a real resting affordance (accent colour for navigation, a hairline or tint for
actions), and re-classify the navigation ones as links.

### A12 — Numbers and states that contradict what is drawn

| Frame | Says | Shows |
|---|---|---|
| `33:65` | header "6 files · 2 finished · **1 needs your attention**" | footer of the same frame: "2 of 6 finished · **1 failed · 1 rejected**" — two rows need attention |
| `46:1576` | zoom chip "**200%** · arrows pan · 0 resets" | the photo is drawn **smaller than fit** — ~420 × 630 inside a ~1230 × 720 stage, with ~510px of dead black on each side. The one frame that demonstrates zoom does not demonstrate zoom |
| `33:65` | file rows "6240 × 4160", "48000 × 3000" | every queue thumbnail placeholder is labelled **"1:1"** |

**Why it matters.** The third one breaks the brief's headline rule ("preserve the image's aspect
ratio") in the easiest possible place; the first is a fabricated count; the second means the viewer's
core interaction is asserted rather than drawn anywhere in the file.

**Fix.** Correct the count; redraw `46:1576` with the photo actually overflowing the stage at 200% and
a pan position implied; use ratio-correct placeholders in the queue.

### A13 — There is no designed signed-out public photo page

**Frames:** `43:3307`, `43:2982` — content area is a **dashed placeholder rectangle** with the caption
"main#content — a public or unlisted photo page". Every viewer frame on page `32:2` is labelled
"owner"; `47:1649` band C covers only the *unavailable* case.

**Why it matters.** At M1 the only surface a signed-out visitor can reach is a public or unlisted
photo page. It is the product's entire public face and the destination of every share link, and no
one has drawn it. It is also where the on-media contrast, the absent owner actions and the sign-in
prompt all have to work together.

**Fix.** Draw it at 1440 and 390, public and unlisted, signed out — or state explicitly in both
hand-offs that the first slice excludes it, so the owner accepts that knowingly.

### A14 — The control matrices do not cover what is drawn

Spot-checked two frames exhaustively against the hand-off matrices.

- **`43:3000` (D2a) — clean.** Nine visible controls, all nine present in D2a §3.7.
- **`38:2168` (D2b) — nine controls with no row anywhere in D2b §3**: skip link, wordmark, the
  TopNav search field, "Explore", "Albums", the upload icon button, the notifications bell, the
  avatar/account button, and the page's own "Upload" primary button (top right). Four of those nine
  lead to milestones that do not exist.

The gap follows directly from A1: D2b's matrix assumes the shell belongs to D2a, but D2b drew D1's
shell instead, so nobody's matrix covers what is on the canvas.

**Fix.** After A1, re-audit every frame on `32:2` against §3 and add the shell rows (or cite D2a's).

---

## (b) Fine to fix after acceptance

Craft, consistency and coverage. None of these will embarrass the work in front of the owner.

**Layout and optical balance**

1. `44:3869` — the stage is 828 × 560 in a 1418-tall frame; the entire bottom-left quadrant
   (~850 × 500px) is empty while the right column runs to y≈1210. On the photo page, the photograph
   should be the largest thing on screen and currently is not.
2. `48:1877` — the 2:3 photo is drawn ~245 × 370 in a ~390 × 440 stage, leaving ~75px of black gutter
   on each side. It is fitted to neither axis.
3. `38:2168` / `41:1175` — the grid's right edge is ragged: row 1 ends at x≈1124, row 2 at x≈1224,
   row 3 at x≈856, against a content width of ~1240. Either justify the rows or cap the raggedness.
4. `42:3331` — the 390 grid is a two-column masonry whose captions land on different baselines across
   columns, while the 1440 grid uses a shared row height. Two grid models for one surface.
5. `41:1050` — the empty, filtered-to-zero and error cards are ~285px wide and left-aligned in a 1440
   frame; they should be centred in the content column. Skeleton row 2 also lacks the caption bars
   that row 1 has.
6. `44:3869`, `48:1877` — owner-action clusters wrap to ragged widths (106 / 116 / 137 / 149 px),
   producing a staircase. Equalise or grid them.
7. `52:2320` — "Create and select" is vertically centred against a label+field+helper stack and sits
   ~21px above the field's centre.
8. `43:3000`, `43:3061`, `42:1078` — content ends around y≈475–760 in 900–1100px frames. System pages
   are legitimately sparse, but at present they read as unfinished rather than calm.

**Consistency**

9. Badge placement differs: library cards put visibility top-left (`38:2168`); album cards put the
   order number top-left and visibility **bottom**-left (`50:1860`).
10. Card titles are accent-coloured links in albums (`50:1860`, `51:2031`) and plain ink in the
    library (`38:2168`).
11. `54:2680` — three dialogs use a red `TriangleAlert` in the title and no footer band; the
    partial-failure dialog uses no icon and a grey footer band with a divider. One pattern, two
    anatomies, in one frame.
12. `54:2680` — the "Kept: …" strip, whose entire content is reassurance about what **survives**, is
    painted in `color/danger-soft` pink. The semantics are inverted; use `bg-tint`.
13. Dialog presentation: `52:2320` and `39:1707` render a scrim over the page behind; `53:2468` and
    `54:2680` render on the bare page background. Decide one and note that the others are exhibits.
14. `53:2468` — album privacy is ordered Public, Private, Link only, Password, breaking the
    widest→narrowest order used for assets (Public, Unlisted, Private) in the dialog immediately
    beside it.
15. `53:2468` — "SHARE LINKS (GUEST PASSES)" introduces "guest passes", a term used nowhere else in
    either copy deck.
16. `26:6` — `MetadataRow`'s `Mono value` variant still carries the default label "Camera" while
    showing an exposure value.

**Icons and target size**

17. `icon/Lock` does three unrelated jobs: the *value* "Private" (`53:2468`), the *action* "Change
    visibility" (`46:1576`, `44:3869`), and "Sessions and devices" (`43:3000`). `icon/Link` is both
    "Unlisted" and "Link only" (`26:6`). A typed semantic registry cannot express that; one of each
    pair needs a different glyph.
18. 52 interactive nodes on page `32:2` are under the project's own 44px target: chips 40px (`All`,
    `Public`, `Unlisted`, `Private`, `Not in an album`, `Needs attention`, `Link only`, `Password`),
    radios 40px, checkbox rows 40px, tabs 42px. These still pass WCAG 2.2 SC 2.5.8 (24px minimum),
    but they contradict D2b §4.6's claim that "every control drawn here is at least 44×44 by
    construction" and D1's `size/touch-min` = 44. Page `27:2` has **zero** such nodes.
19. `51:2118`, `51:2142`, `51:2189`, `51:2216` — `cover col` overflows its mosaic parent by 2px,
    clipping a hairline on four album covers in `51:2031`.

**Semantics and copy**

20. `43:3000`, `43:3061` — "Sign out" is drawn in `color/danger` red with a `LogOut` icon. Signing out
    is not destructive; reserve danger for deletion.
21. Both pages draw the skip link **permanently visible** at 1440 as a bright blue pill in the top
    bar. It is a defensible choice but it currently competes with the wordmark on every desktop
    frame and makes the product read as a wireframe. Worth an explicit decision.
22. `38:2168` and elsewhere — page ledes read as documentation ("everything you own, whatever its
    visibility. Only you and an administrator acting in an audited context can see this page").
    Accurate, but a copy pass should decide how much of the threat model belongs on the page.
23. `44:3869` — the `RESERVED — NOT IN M1` block is placed *inside the content column*, styled as a
    dashed card where a real component will go. Correct intent; move it outside the page bounds like
    the other annotations so it cannot be mistaken for UI.

**Coverage the hand-offs already record, restated so the owner sees it in one place**

24. No 320px reflow frame and no 200% zoom frame anywhere (D2a §10.2, D2b §9.2).
25. Dark mode drawn only for sign-in, the shell, the library and the lightbox. Upload, albums and
    every dialog are Light-only (D2b §9.3).
26. No real photographs anywhere; the on-media contrast figures are computed worst-case bounds, not
    measurements over images (D1 §10.6, D2b §9.6).
27. No motion specification — tokens only, no curves, no per-component map (D1 §10.7).
28. `/settings/sessions` is linked from the shell and shows "3 signed in", but the list is not
    designed (D2a §10.5).
29. The dismissed-re-auth "You are signed out" banner is described but not drawn (D2a §10.7).
30. Hover and pressed states were not drawn for any of D2b's seven new components (D2b §9.5).
31. The file is a **draft, not a published library** — I confirmed `search_design_system` returns
    empty for every query against this file key. Any builder or agent must work inside this file.
32. Lucide export names remain unverified; seven of forty are flagged as renamed (D1 §10.1,
    D2b O-15).
33. No screenshots are archived under `docs/evidence/` (both hand-offs). If the war room needs
    durable visual evidence, it must be re-captured and committed.

---

## (c) Questions only the owner can answer

Merged from D2a §7 (Q-D2a-1…10) and D2b §7 (O-1…15), de-duplicated, ordered by consequence.

1. **Which shell is canonical?** *(new — arises from A1, and supersedes nothing)* Confirm
   `TopNav / M1` + `AppBar / M1` + `TabBar / M1` as the M1 shell, with D1's `TopNav`/`TabBar` held for
   M2+. This determines whether 14 frames get rebuilt. Folds in **Q-D2a-7** (no tab bar for a
   signed-out visitor at 390) and **Q-D2a-8** ("Account" rather than "You" for the fourth tab).
2. **O-1 — `Download original`: M1 or M3?** It is drawn in `44:3869`, `48:1714`, `46:1576` and
   `48:1877`. `GAPS.md` and the ledger put `VZ-DOWNLOAD-001` in M3. Keep it and implement the
   permission model plus audited count now, or remove it from all four frames. It must never ship as
   a dead control.
3. **Q-D2a-3 — duplicate email at sign-up.** With no email verification at M1 (`VZ-AUTH-002` is M2),
   sign-up cannot be made enumeration-safe. Allow duplicate emails, accept the enumeration surface,
   or pull `VZ-AUTH-002` forward. The frames currently duck it by showing only a username error.
4. **Q-D2a-4 — no password recovery at M1.** A member who forgets their password is locked out with
   no path back, and the copy says so plainly. Accept, or pull `VZ-AUTH-002` / `VZ-ADMIN-USERS-001`
   forward.
5. **One vocabulary for visibility.** *(new)* Assets use Public / **Unlisted** / Private; albums use
   Public / Private / **Link only** / Password. "Unlisted" and "Link only" carry near-identical
   consequence text and **the same link icon** (`53:2468`, `26:6`). Are these deliberately two
   concepts, or one word used twice? Folds in **O-5** (confirm Private as the shipped default for new
   uploads, which the frames assert).
6. **O-11 — the theme-invariant near-black photo stage.** `GAPS.md` demands this light/dark decision
   be made deliberately. Sign off or reject; A2 and A3 both depend on the answer.
7. **O-7 — deleting an album with sub-albums.** The confirmation on `54:2680` asserts sub-albums are
   **re-parented to the grandparent**, not deleted. ADR-007 does not rule on it, and the copy cannot
   be trusted until it does.
8. **Q-D2a-5 — pending action resubmitted after re-authentication.** `39:1707` promises the
   interrupted action is replayed automatically. That is a real implementation cost. Confirm, or the
   copy must change.
9. **O-2 / O-3 — quota and derivative numbers.** 20 GB per user, 100 MB per file, 50 files per batch,
   "shown at 720 × 480". ADR-005 and ADR-006 both record these as `[to confirm in M0]`. They appear
   as facts on eight frames.
10. **O-6 — geo-privacy control in M1.** `44:3869` states there is **no control to widen** location in
    this release. Confirm, or the metadata panel needs an owner control.
11. **Q-D2a-6 — near-limit quota threshold.** Drawn at 90%. Confirm the number, and whether it is an
    instance setting.
12. **O-8 — share-grant expiry in M1.** A grant is drawn with "expires 30 Sep"; `VZ-ALBUM-002` names
    creation, listing and revocation but not expiry.
13. **O-9 — is the album password set in the same dialog?** Drawn as a radio whose consequence text
    says the password is set here and never shown again; the set-password field itself is not drawn.
14. **O-4 — album depth limit.** ADR-007 fixes 5 for collections and `[to confirm in M0]` for albums.
    The breadcrumb and sub-album cards assume at least 3.
15. **O-10 — selection mode at 390.** Explicit Select → Done (`42:3331`), versus long-press.
16. **O-12 — Exif as a tab or a section.** Drawn as `About` / `Exif` tabs per `VZ-MEDIA-004`.
17. **Q-D2a-9 — session wording.** "30 days" is taken from ADR-003; should the 180-day absolute cap be
    mentioned to a member too?
18. **Q-D2a-1 / Q-D2a-2 — claim-token refusal.** One message for mistyped / used / superseded (it
    would otherwise be an oracle), and **409 Conflict** for a claim against an already-claimed
    instance — neither is settled by an ADR.
19. **Q-D2a-10 — no live password-strength meter.** A stated minimum instead of a client-side
    estimator with no ledger entry.
20. **O-13 / O-14 — ledger gaps.** The `Needs attention` library filter has **no ledger id**; so do
    `Show more`, full screen (`F`) and the details toggle (`I`). Add rows to `features.json` /
    `ui-controls.json`, or drop the controls.
21. **O-15 — Lucide export names.** Seven of the forty proposed names were renamed in recent releases
    and none is verified against a pinned package. The typed registry must not ship until
    `vizra-user` resolves them.

---

## Punch list

Executable without further judgement. Items 1–14 are the (a) list.

**Shell**

1. On page `32:2`, replace all 11 `TopNav` instances with `TopNav / M1` (`30:770`), matching
   `State = Signed in`.
2. On page `32:2`, replace all 5 `TabBar` instances with `TabBar / M1` (`30:935`), setting `Selected`
   per frame: `42:3331`→Library, `48:1714`→Library, `51:2276`→Albums, `37:1977`→Upload,
   `37:2151`→Upload.
3. In `42:3331`, delete the locally composed 390 top bar and insert `AppBar / M1` (`30:814`),
   `State = Signed in`.
4. Rename `TopNav` (`15:74`) → `TopNav (M2+ — not for M1)` and `TabBar` (`15:32`) →
   `TabBar (M2+ — not for M1)`; append the reason to each Figma description.

**Media-surface colour**

5. In `icon/ZoomIn` (`5:106`) and `icon/ZoomOut` (`5:111`), and in every other multi-vector icon used
   by the `IconButton` `On media` variant, bind **every** vector to `color/on-media` instead of
   `color/ink`. Verify by re-running `get_variable_defs` on `44:3920` and `48:1747` and confirming
   `--vz-ink` no longer appears.
6. In `SelectionCheckbox` (`28:81`), give the resting box the D1 §4 dual ring
   (`on-media-scrim` inner + `on-media` outer) so it is perceivable on any backing. Re-render
   `38:2168` and `41:1175` and crop the same region from both.
7. Delete the sentence "the visibility marker and the selection checkbox look identical in both
   themes" from the design note in `41:1175`, or restate it correctly once 6 is done.

**Data bars**

8. Fix `Meter` (`31:86`) so the fill draws the stated fraction at the instance width used
   (670 / 308). Re-measure `42:1012`, `42:1078`, `42:1159`, `42:1238`, `42:1325`, `42:1450` and record
   drawn % vs stated % for each.
9. Give the storage bar a visual treatment distinct from the in-flight upload bar on `33:65`, or
   replace `quota-progress` there with `Meter`.

**Geometry**

10. Widen `53:2471` and `52:2467` to at least 1368 (or reduce the inter-dialog gap by 24px) so
    `53:2638` and `52:2543` stop clipping. Raise `48:1878` or shorten `48:1904` by 16px.
11. Re-run both overflow audits **parent-relative** rather than against the top-level frame, and
    restate D2a §9 and D2b §6.

**390**

12. In `54:2808`, make every sheet button fill the sheet width, stack them, and align all children to
    one left edge; give the destructive sheet title the icon-plus-ink treatment used in `54:2680`.
13. Add a zoom cluster (`Zoom out`, `Zoom in`, zoom-level chip) at 44×44 to `48:1877`.

**Hand-off hygiene**

14. Move these strings out of components into annotations: the `aria-live` sentence in `33:65`; the
    two focus/Escape sentences in `39:1707`; "(you are here)" in `50:1860`; the `prompt 03` quotation
    in `47:1649`. Re-style the `EVERY ROW IS OPERABLE` block in `33:65` and all `accent-soft`
    annotation blocks on page `32:2` to D2a's dashed `NOT PRODUCT UI` treatment.
15. Fix the count on `33:65`: "6 files · 2 finished · **2 need your attention**".
16. Redraw `46:1576` so the photo actually exceeds the stage at the stated 200%, or change the chip
    to the state that is drawn.
17. Replace the "1:1" queue thumbnails in `33:65` with ratio-correct placeholders matching each
    file's stated dimensions.
18. Demote Delete from filled to quiet-danger and separate it from the constructive cluster in
    `44:3869` and `50:1860`; separate the trash from download in `46:1576`; move Delete off the
    bottom of the sheet in `48:1877`.
19. Choose one component per duplicated concept (`Meter` vs `ProgressBar` for quota;
    `VisibilityBadge` vs `visibility marker`; `SelectionCheckbox` vs `Checkbox`), deprecate the
    other by rename + description, and consolidate the M1 additions onto one set of pages.
20. Record in D2b's hand-off that `PhotoCard` (`12:263`) is unused and why, and say where the
    `Sensitive` safety-blur state now lives.
21. Give the `Quiet` Button variant a resting affordance, and convert the navigation instances listed
    in A11 to link styling.
22. Draw the signed-out public photo page at 1440 and 390 (public and unlisted), or state its
    exclusion explicitly in both hand-offs.
23. Re-audit every frame on `32:2` against D2b §3 and add the nine missing shell rows for `38:2168`
    (and the equivalents on the other frames).
24. Add to both hand-offs' verification sections: parent-relative overflow, drawn-fraction-equals-
    stated-fraction for every data bar, and a light-mode render of every on-media control.

---
---

# Re-check after the fix pass

**Verdict: READY FOR OWNER REVIEW**, with two things I would fix first (§R5) and a disclosure list
the owner must be given (§R4).

| | |
|---|---|
| **Re-checked** | 2026-09-20, after `docs/design/figma/FIXES-first-slice.md` |
| **Scope** | The twelve fix-before findings (A1…A14 in my numbering; the fixer's A1…A12 map to the same items), plus a regression sweep |
| **Method** | Read-only. Treated the fixer's hand-off as claims; re-rendered 24 frames/components, re-ran the instance census and the parent-relative geometry audit from scratch, re-measured every `Meter` fill from the rendered pixels, and re-resolved `get_variable_defs` on the nodes whose colour bindings were the root causes. Nothing was edited. |
| **Chair rulings honoured in my judgement** | M1 shell canonical; owner questions stay as drawn (`Download original` deliberately retained); component-level fixes; additive/corrective only, so the absent rename of `TopNav`/`TabBar` is not counted against the round. |

## R1 — Per-finding status

### A1 · Two application shells — **FIXED**

Census re-run on both pages from fresh metadata: page `32:2` now has `TopNav` **0**, `TabBar` **0**,
`TopNav / M1` **11**, `icon/Bell` **0**, `icon/Search` **0**. Page `27:2` unchanged (`TopNav / M1`
×14, `AppBar / M1` ×9, `TabBar / M1` ×7).

Verified by render, not by name. `38:2168`, `33:65`, `44:3869`, `50:1860` and `41:1175` all now show
the same bar as `43:3000`: skip link, wordmark, Library, Albums, upload, **MO** avatar — no search
field, no "Explore", no bell, no unread dot. `42:3331` shows `AppBar / M1` (`62:2862`) above a
title-only band, and `TabBar / M1` with **Library** active; `37:1977` shows the same tab bar with
**Upload** active. It reads as one product with the auth pages.

Four residuals, all minor:

- **Three tab-bar instances still carry the pre-fix layer name** — `37:2121`, `37:2264`, `42:3502`
  are still called `TabBar (fixed to the bottom of the viewport)`. The component beneath is
  `TabBar / M1` (confirmed by render), but a name-based census reads them as unswapped, which is how
  I first mis-counted them. Rename the layers so the next audit is not misled.
- **`42:3331` is mildly a second header.** The demoted `page-title (Library)` band keeps its own
  bottom divider directly under the app bar's divider, so the phone library opens with two stacked
  rules. D2a's `43:3320` has none — its page title is simply the first content element. Cosmetic, but
  it is a visible difference from the auth pages at the same width.
- **`37:1978` / `37:2152` (U5, U6) still wear a local `mobile-header` back-bar on a tab root.** With
  the Upload tab selected at the bottom, the page offers a "←" and no wordmark. `48:1715` (V4) and
  `51:2277` (A3) are genuine sub-pages where a back-bar is correct; U5/U6 are not. The fixer records
  this honestly.
- **The hidden superseded bar is confirmed as a trap** — see A6.

### A2 · Zoom glyphs invisible in Light — **FIXED**

`get_variable_defs` on `44:3920` now returns **only** `--vz-on-media` plus geometry tokens;
`--vz-ink` is gone. Rendered `44:3920` at 4×: the left button shows a clear white `−` and the right a
clear white `+`, and the two are unmistakably different controls. Dark (`46:1649`) unchanged and
correct.

I recomputed the contrast independently rather than taking the number: white `#ffffff` against the
composited `color/on-media-scrim` chip on the theme-invariant stage is **20.1:1**, and against the
worst possible backing (the chip over a pure-white photograph, compositing to ≈`#22252a`) is
**≈15.8:1**. The claimed 19.7 / 20.1 is sound.

**Checked the rest of the stage for the same mistake, as asked.** `get_variable_defs` on the whole
V1 stage `44:3907` resolves no `--vz-ink` at all — prev, next, the ratio chip and the visibility
badge are clean. The only theme tokens on the stage (`--vz-ink-3`, `--vz-bg-tint`, `--vz-line-2`)
belong to the grey `AspectPlaceholder`, not to a control. Close, prev/next and details in the
lightbox render correctly in both themes. No second instance of the defect.

### A3 · SelectionCheckbox off-state — **FIXED**

Cropped the same pixel region from `38:2168` (Light) and `41:1175` (Dark) as in the first review. In
both, the unchecked box now reads unambiguously as a checkbox: dark fill → white ring → dark halo.
The light-mode "black smudge" is gone.

The misleading design note is corrected, and correctly: `41:1285` now says the two on-media tokens
*render the same* in both themes and that this "is not the same as being readable on every backing",
then records the dual ring and its 15.4:1.

One caveat the owner should hear: this is still **computed, not observed**. There are no photographs
in the file, so the dual ring has been verified on a light card and a dark card, not over a real
image. The geometry is sound and should hold; it is not evidence.

### A4 · Storage meter drew half its value — **FIXED**

Re-measured from the rendered pixels myself, fill run against track run:

| Instance | Frame | Stated | **I measured** |
|---|---|---|---|
| `42:1035` | `42:1012` | 62% | **61.9%** |
| `42:1110` | `42:1078` | 91% | **90.9%** |
| `42:1191` | `42:1159` | 100% | **99.9%** |
| `42:1348` | `42:1325` (390) | 91% | **90.6%** |

Correct within rounding. The fixer's table is accurate.

**On the `Meter fit (fill width)` collection — flag it, do not mirror it.** It is a Figma-only
workaround, not a design token, and it needs saying louder than a component description.
`get_variable_defs` on `42:1110` returns `"meter/fill-91": "608"` **inside the same payload as the
real tokens**. The one thing separating it from them is that it carries no `var(--vz-…)` code syntax
— which is exactly the signal a builder or an agent mirroring variables into Tailwind is most likely
to miss. It also hard-codes three percentages against three column widths, so any other value or
column silently draws wrong again. Add an explicit "never mirrored; production computes
`width: used/allowed`" line to the mirroring section of the D1 hand-off (§8), not only to the
component.

### A5 · 390 sheets — **FIXED**

Rendered `54:2808` and `48:1877`. Every sheet button is now full width with matching left and right
edges; the focus ring on "Cancel" and "Keep the album" outlines the control itself rather than a
390px band. The destructive sheet now carries a red `TriangleAlert` beside an ink-coloured title,
matching `54:2680` — the destructive signal is no longer colour alone. Safe action on top, holding
focus. The six V5 sheet buttons got the same fix.

Residual: the frame's design note still ends "so the thumb's resting position is never on Delete",
which is false for this sheet — Delete is the bottom-most control. Correct the sentence or the
layout; right now the note contradicts the drawing.

### A6 · Clipped frames — **FIXED** (audit claim slightly off)

Rendered `53:2638` and `52:2543`: both dialogs now have their right border, their padding and both
footer buttons fully inside the frame. `48:1904` ends on the 844 fold.

My independent parent-relative audit:

| Page | Nodes I scanned | Offenders before | **Offenders now** |
|---|---|---|---|
| `27:2` | 887 | 1 | **0** |
| `32:2` | 1,397 | 7 | **3** |

The fixer claims 1 remaining on `32:2`. I find **3**: the deliberate `46:1633` photo (correct, it is
the 200% demonstration), plus **`42:3334` and `42:3339` overflowing `page-title (Library)` by +9px
each** — the two hidden, superseded controls inside the demoted bar. Nothing renders them, so the
visual impact is nil, but the discrepancy confirms the point the fixer itself raises: a hidden node
with two dead controls in it is a trap. Delete it when a rename/delete round is authorised.

(My node counts are lower than the fixer's because `get_metadata` does not expand inside instances.
The two audits cover different scopes and agree where they overlap.)

### A7 · No zoom in the phone lightbox — **FIXED**

`48:1877` now carries the cluster `69:4961`: zoom out, zoom in and a "Fit · press 0 to reset" chip,
44×44 each, glyphs legible (they inherit the A2 fix).

Residual introduced: the cluster is drawn **over the lower part of the photograph**, not in a stage
gutter as it is on V1. It is on an 88% scrim so it stays legible, but the same frame's note says
"nothing sits over the image except the close, visibility and step controls". Either move the cluster
below the image or update the note.

### A8 · Spec text rendered as product copy — **FIXED for all six named strings**

Verified by render: the U2 banner now reads "Uploading 6 files. 2 finished, 2 need your attention.";
the U5 banner is product copy; the reauth helper is "Press Enter to sign in and continue." and its
footnote "Press Escape to close this. You stay on the page you were on, and a banner at the top will
say you are signed out."; the breadcrumb is "Casa Barragán" with no "(you are here)"; the V3 prompt
quotation is gone. The `aria-live` contract is preserved in the bottom design note. `33:376` is now a
dashed, unfilled `DESIGN NOTE — NOT PRODUCT UI` box, clearly distinct from the real `STORAGE` card
beside it.

Residual of the same class, not on my original list: **`53:2638`'s dialog body still reads
"In flight: the confirm button is the busy control (aria-busy, stable name), the radios are disabled,
and Cancel stays available. Under prefers-reduced-motion…"** — a specification sentence inside a real
dialog. Same treatment needed. The remaining `accent-soft` annotation blocks are still a second
annotation style; cosmetic.

### A9 · Destructive prominence — **PARTLY FIXED**

Fixed where it was named: `44:3869`, `50:1860`, `48:1714` and `48:1877` now put Delete behind a
full-width divider as a quiet button with a red label, and `46:1576` separates the trash from
download with a visible rule. Rendered and confirmed on V1, A1, V2 and V5.

Not fixed: **the BulkBar Delete is still a filled red button** on `38:2168`, `41:1175` and
`42:3331`. The library page now has exactly two filled buttons — "Upload" (blue) and "Delete" (red)
— so the destructive action is still co-equal with the primary on the surface the owner will spend
most time on. See §R5. V5's Delete is still bottom-most, deliberately.

### A10 · Duplicate components — **NOT FIXED** (deferred by ruling, honestly recorded)

Census confirms all three duplications survive: `visibility marker` ×38 and `VisibilityBadge` ×41
still coexist, sometimes in the same frame; `quota-progress` ×5 (ProgressBar) still does quota duty
on `32:2` while `Meter` ×6 does it on `27:2`; on `33:65` the storage bar remains visually identical
to the blue upload bars directly above it. Deprecation contracts were written into the descriptions.
Acceptable as a deferral, since resolving it needs a rename or a delete.

### A11 · Quiet controls read as static text — **FIXED, with one regression**

Fixed at the component level and verified on `37:301`, `39:1707`, `33:65`, `44:3869`, `38:2168` and
`42:3331`: "Show password", "Create an account", "Sign out", "Not you?", "Clear selection", "Retry
all failed", "View", "Show more", "Back to your library" and "Done" all now carry a hairline and read
as controls. See §R2 for the regression.

Navigation instances are still buttons rather than accent links — acknowledged and deferred.

### A12 · Facts that contradicted the drawing — **FIXED except the API-blocked item**

- Header count: `33:65` now reads "6 files · 2 finished · **2 need your attention**", matching its
  own footer. Fixed.
- 200% zoom: `46:1633` is now 980×1472 in a 1440×900 stage and genuinely overflows it, so
  "200% · arrows pan · 0 resets" states what is drawn. Fixed — see §R2 for what it cost.
- Queue thumbnails: **still "1:1"** beside rows stating 6240×4160 and 48000×3000. The API block is
  real and the reproducer is specific and credible (`relative-transform` cannot be overridden inside
  an instance). Genuinely BLOCKED, not skipped — but see §R5 for the cheap partial fix.

### A13 · No signed-out public photo page — **NOT FIXED**, stated for knowing acceptance

Correct call. It is a new surface, not a repair. It belongs in the owner's decision list, not the
defect list.

### A14 · Control matrices — **NOT FIXED**, out of scope

Correctly scoped out; the two hand-off documents were not in this round. The fixer's observation is
right: now that every M1 frame instances D2a's shell, the rows `32:2` needs are exactly D2a §3.7.

## R2 — Regressions

I looked specifically at spacing, alignment, dark mode and the things I called genuinely good. The
privacy semantics, the destructive-confirmation content, the upload failure states, the two empty
states and the aspect-ratio proof in `47:1649` are all untouched and intact. Dark mode (`41:1175`,
`46:1576`, `48:1877`) holds up with no new defects.

Five regressions, one with product impact:

1. **`Kind=Quiet` has converged on `Kind=Secondary`.** *(product impact)* Quiet is now 1px
   `color/line` with no fill; Secondary is 1.5px with a `bg-elevated` fill. At normal viewing
   distance they read the same. Where three button weights used to exist in one row, two now
   collapse: the bulk bar at 1440 and 390 shows three near-identical outlined buttons plus a filled
   Delete; `33:65`'s footer shows "Retry all failed" and "Cancel remaining" as near-twins; V1's right
   column stacks "Show more", four Secondary and a quiet Delete at nearly equal mass. The fix was
   right; the treatment needs to be further from Secondary — a tint, a weight change, or accent for
   the navigation instances. This flattens hierarchy on exactly the surfaces A9 set out to fix.
2. **`46:1576`'s stage is now a large featureless rectangle.** Drawing 200% honestly means a flat
   grey placeholder fills the centre, and the enlarged photo now covers most of the library grid that
   used to show behind the lightbox. It is geometrically correct and no longer lies, but it has
   stopped demonstrating a photograph. This is the cost of having no real images; it is not a reason
   to revert.
3. **`48:1877`'s new zoom cluster overlaps the photograph** (A7 residual).
4. **Two design notes are now false relative to what is drawn** — `54:2808` "the thumb's resting
   position is never on Delete", and `48:1877` "nothing sits over the image except the close,
   visibility and step controls".
5. **`42:3331` opens with two stacked header rules** where D2a's 390 pages have none.

## R3 — Verdict

**READY FOR OWNER REVIEW.**

Every finding I raised as blocking is closed or honestly deferred, and the two that mattered most —
the split shell and the invisible on-media controls — are fixed at the root, in the component, not
patched per frame. The fixer's claims held up against independent measurement: the census, the four
meter fills, the contrast recomputation and the clipping repairs all check out. Where a claim was
slightly wrong (three geometry offenders rather than one), the difference is invisible and the fixer
had already flagged the underlying cause itself. The round did not break anything I had called good.

What stops this being unqualified: one component-level regression (R2.1), one destructive-hierarchy
surface left untouched (A9, the bulk bar), and a documented hole in coverage (no signed-out public
photo page). None is grounds for another full round before the owner sees it.

## R4 — What the owner must be told is knowingly imperfect

The fixer's own list, with my assessment of each.

| # | Item | Show the owner? |
|---|---|---|
| 1 | **Delete is the bottom-most control in the V5 actions sheet** — demoted and separated, still nearest the thumb | Yes, with disclosure. Moving a destructive action to the top of a non-confirming sheet is its own hazard; this is a defensible trade |
| 2 | **The bulk-bar Delete is still filled red**, so the loudest control on the library page is the destructive one | **No — fix first.** See §R5 |
| 3 | **Queue thumbnails are square** while their rows state 6240×4160 and 48000×3000 | **No — fix the label first.** See §R5 |
| 4 | **No signed-out public photo page anywhere in the first slice** | Yes — and it belongs in the decision list, not the defect list. It is the destination of every share link and the whole public face of M1 |
| 5 | **No real photographs anywhere in the file.** Every on-media contrast figure is a computed worst-case bound, not a measurement; the 200% demonstration is a flat rectangle | Yes, prominently. It is the single largest gap between "this is designed" and "this is proven" |
| 6 | **A hidden, superseded bar survives in `42:3331`** with two dead controls inside it | Yes, as a note to the next agent rather than to the owner |

Add two of my own:

| # | Item | |
|---|---|---|
| 7 | **`Quiet` and `Secondary` now look alike** (R2.1) | Tell the owner the affordance problem is fixed and the weight separation is a follow-up |
| 8 | **`Meter fit` is a Figma-only workaround** that must never be mirrored into Tailwind | Tell the builder, not the owner |

## R5 — The two I would not show an owner without fixing

1. **The filled-red `BulkBar` Delete** (`38:2168`, `41:1175`, `42:3331`). A9 was accepted and fixed
   on five surfaces, then left on the one the owner opens first and looks at longest. The library
   page currently has exactly two filled buttons: "Upload" and "Delete". It is a single variant
   change inside one component — `Kind=Danger` → `Kind=Quiet` with a `color/danger` label, plus the
   divider the other five surfaces already have. It is the difference between "we fixed the
   hierarchy" and "we fixed it everywhere it did not show".
2. **The "1:1" labels on the queue thumbnails** (`33:65`, `37:1977`, `37:2151`). The geometry is
   genuinely API-blocked and I accept that. The *text* is not: the placeholder states a ratio that
   contradicts the file dimensions printed two lines above it, on the upload page, breaking the
   brief's headline rule in the most visible possible way. Either delete the "1:1" string from the
   nested placeholder, or change the sample files' stated dimensions to square ones. If neither is
   reachable, the owner must be told in one line rather than left to notice.

Everything else in §R4 is fine to show with disclosure.

## R6 — Owner questions, merged and final

Most consequential first. Each is phrased to be answerable in one line. The shell question from my
first review is gone — the chair settled it.

1. **`Download original` in the viewer: keep it in M1, or remove it from the four frames?** The
   ledger puts `VZ-DOWNLOAD-001` in M3; if it stays, the permission model and the audited count ship
   now, because it must never be a dead control.
2. **Should the first slice include a signed-out public photo page?** It is the destination of every
   share link and the only surface a logged-out visitor can reach at M1, and none is drawn.
3. **Duplicate email at sign-up: allow duplicates, accept the enumeration leak, or pull
   `VZ-AUTH-002` forward?** Without verification at M1 there is no fourth option.
4. **No password recovery at M1 — accept that a member who forgets their password is locked out
   until an admin intervenes?** `VZ-AUTH-002` and `VZ-ADMIN-USERS-001` are both M2.
5. **One vocabulary for visibility, or two?** Assets say "Unlisted", albums say "Link only", they
   carry near-identical consequence text and the same link icon.
6. **Confirm the theme-invariant near-black photo stage in both light and dark themes.**
7. **When an album with sub-albums is deleted, are the sub-albums re-parented to the grandparent?**
   The confirmation copy asserts it; ADR-007 does not rule on it.
8. **Confirm Private as the shipped default visibility for new uploads.**
9. **Confirm that an action interrupted by session expiry is resubmitted automatically after
   re-authentication** — it is a real implementation cost, and the copy promises it.
10. **Fix the quota and derivative numbers** — 20 GB per user, 100 MB per file, 50 files per batch,
    display long edge, thumbnail size. All are `[to confirm in M0]` and all appear as facts on eight
    frames.
11. **Confirm there is no owner control to widen photo location in M1** — the viewer says so
    explicitly.
12. **Confirm the near-limit quota threshold of 90%, and whether it is an instance setting.**
13. **Is share-grant expiry in M1?** A grant is drawn with "expires 30 Sep"; `VZ-ALBUM-002` names
    creation, listing and revocation only.
14. **Is the album password set in the same dialog?** It is offered as a radio whose consequence text
    says so; the field itself is not drawn.
15. **Confirm the album depth limit** — ADR-007 fixes 5 for collections and `[to confirm in M0]` for
    albums; the breadcrumb assumes at least 3.
16. **Confirm selection at 390 is an explicit Select → Done mode** rather than long-press.
17. **Confirm Exif is a tab rather than a continuous section.**
18. **Confirm the session copy says "30 days"** — should the 180-day absolute cap be mentioned to a
    member too?
19. **Confirm one refusal message for a bad claim token** (mistyped / used / superseded are
    indistinguishable to the server), **and 409 Conflict for a claim against a claimed instance.**
20. **Confirm no live password-strength meter** — a stated minimum instead of a client-side estimator
    with no ledger entry.
21. **Add or drop the un-ledgered controls**: the `Needs attention` library filter, `Show more`, full
    screen (`F`) and the details toggle (`I`) have no ledger id.
22. **Authorise verification of the 40 proposed Lucide export names** against a pinned
    `lucide-react` before the typed icon registry ships — seven were renamed in recent releases.
