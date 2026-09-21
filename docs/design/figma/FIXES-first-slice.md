# Fix round — first slice (response to `REVIEW-first-slice.md`)

**Status: FIXED IN FIGMA, not approved, not verified by anyone but me.** This records the edits made
to the Figma file in response to the fresh-eyes review's section (a) and punch list, so the owner is
asked to accept one coherent product rather than two. It is **not** an acceptance target and **not**
authorization to implement anything. Nothing here is VERIFIED.

| | |
|---|---|
| **Figma file** | <https://www.figma.com/design/JXgRItauynmT0g8vSJB3oR> |
| **File key** | `JXgRItauynmT0g8vSJB3oR` |
| **Pages edited** | `M1 · Library, viewer, albums` (`32:2`), `M1 · Auth & system` (`27:2`), `Navigation` (`4:28`), `Button` (`4:21`), `IconButton` (`4:22`), `PhotoCard` (`4:26`), `Feedback` (`4:30`), `Icons` (`4:32`), `Components · M1 additions (D2b)` (`26:6`) |
| **Date** | 2026-09-20 |
| **Access** | `whoami` → `yegamble@gmail.com`, team `984598513556028019` |
| **Method** | `use_figma` writes, each returning success and node ids; every group of fixes re-rendered with `screenshot()` and visually inspected; geometry and contrast re-measured after the fact, not assumed |

**Chair rulings this round worked under**, which settle what the review left open:
the M1 shell is `TopNav / M1` + `AppBar / M1` + `TabBar / M1`; owner questions stay exactly as drawn
(`Download original` untouched, sign-up duplicate-email copy untouched); defects in a component are
fixed in the component; additive and corrective only — no frame deleted, no existing component or
variable renamed, no instance detached.

---

## 1. What was fixed

One row per review finding addressed.

| # | Finding | What changed | How it was checked |
|---|---|---|---|
| **A1** | Two application shells; page `32:2` used D1's pre-M1 nav | 11 `TopNav` instances swapped to `TopNav / M1` `State=Signed in` (`30:750`): `32:4`, `33:66`, `36:333`, `36:515`, `38:2169`, `41:1051`, `41:1176`, `44:3870`, `47:1650`, `50:1861`, `51:2032`. 5 `TabBar` instances swapped to `TabBar / M1` with the `Selected` the frame is on: `37:2121`→Upload, `37:2264`→Upload, `42:3502`→Library, `48:1847`→Library, `51:2458`→Albums. No label invented; the M1 shell's own Library / Albums / Upload / Account are used throughout. | Instance census of `32:2` re-run after the swap: `TopNav` **0**, `TabBar` **0**, `TopNav / M1` **11**, `TabBar / M1` **5**, `icon/Bell` **0** (was 11). Rendered `38:2168` (1440 Light) and `42:3331` (390): wordmark, Library, Albums, upload, avatar — no search field, no Explore, no bell, no unread dot. |
| **A1** | Third top bar at 390 in `42:3331` | `AppBar / M1` `State=Signed in` inserted as child 0 → new node **`62:2862`**. The locally composed bar was **not deleted**: it is renamed `page-title (Library)` and keeps only the page title; its search icon button (`42:3334`, `VZ-SEARCH-001` is M3) and its upload icon button (`42:3339`, duplicated by the Upload tab) are set `visible = false`. The frame hugs to 1554 tall. | Rendered `42:3331`: app bar (skip link in DOM order, wordmark, account) → "Library" → content → `TabBar / M1` with Library selected. `AppBar / M1` census on `32:2` = **1**. |
| **A2** | Zoom in / zoom out invisible and indistinguishable in Light | Root cause in the icon components. All 7 vectors rebound from `color/ink` to `color/on-media`: `icon/ZoomIn` `5:102`, `5:103`, `5:104`, `5:105`; `icon/ZoomOut` `5:108`, `5:109`, `5:110`. | Rendered `44:3920` at 6× in **Light** and `46:1649` at 6× in **Dark**: the `−` and the `+` are both plainly visible and the two buttons are now distinguishable. Recomputed against the composited `color/on-media-scrim` chip on the theme-invariant stage: **19.7:1 in Light, 20.1:1 in Dark** (was 1.05:1 in Light). `get_variable_defs`-level check: the glyph no longer resolves `color/ink` at all. |
| **A3** | `SelectionCheckbox` off state not perceivable on a light card | Root cause in the component. `ring-inner` of the two resting variants — `28:61` (`Selected=No, State=Default`) and `28:69` (`Selected=Yes, State=Default`) — given a 2px **INSIDE** `color/on-media-scrim` stroke, which lands immediately outside the box's white ring. Reading outward the control is now dark fill → white ring → dark halo → backing, so the white ring is bounded by dark on both sides whatever the photo does. | Rendered `38:2261` at 4× (light card) and `41:1195` at 4× (dark card): in both the box reads as a checkbox, not a smudge. White ring vs its dark neighbours **15.4:1**, identical in both themes because both tokens are theme-invariant; the dark halo vs a light card is **13.5:1**. |
| **A3 / punch 7** | The design note asserting the claim that stopped this being caught | `41:1285` restated: the two on-media tokens *render the same* in both themes, which is **not** the same as being readable on every backing; the note now records the dual ring and its 15.4:1. | Read back after the edit; visible in the rendered `41:1175`. |
| **A4** | Storage meter drew roughly half of what it says | The fill is now bound to a width that survives instance resizing. New variable collection **`Meter fit (fill width)`** (`VariableCollectionId:67:1772`) with modes `Natural 320` / `Column 670` / `Column 308` and three FLOAT variables `meter/fill-62`, `meter/fill-91`, `meter/fill-100` scoped `WIDTH_HEIGHT`. `meter-fill.width` bound on all three `Meter` variants (`31:54`, `31:63`, `31:77`); each of the six instances set to the mode matching its column with `setExplicitVariableModeForCollection`. Master fractions also corrected to exact percentages of the 318px track interior. | **Every instance re-measured, drawn vs stated**: `42:1035` 62/62 · `42:1110` 91/91 · `42:1191` 100/100 · `42:1260` 100/100 · `42:1348` 90.8/91 · `42:1463` 100/100. Rendered `42:1110` at 2×: the bar visibly fills ~91% of its track under "18.2 GB of 20 GB". This also removed the +13px `meter-fill` overflow inside `42:1450`. |
| **A5** | 390 sheets contradict their own rule; focus ring around the wrong box | Inner `surface` set to `FILL` (and label centred) on all nine footer buttons in `54:2808` — `54:2857`, `54:2865`, `54:2873`, `54:2927`, `54:2933`, `54:3004`, `54:3010`, `54:3021`, `54:3027` — **and** on the six buttons of the V5 actions sheet, which has the same defect: `48:1909`, `48:1915`, `48:1921`, `48:1927`, `48:1933`, `48:1939`. | Measured before → after: every visible control went from 63–187px to **354px inside a 358px wrapper**, i.e. the 2px focus pad each side that the library's Button is designed around — the ring now outlines the control. Rendered `54:3016` at 2× and `48:1878` at 1.1×. |
| **A5** | 390 destructive title carried by colour alone | `54:3019` moved into a new row **`69:2859`** with a `TriangleAlert` instance **`69:2860`** whose vectors are bound to `color/danger`; the title text itself rebound to `color/ink`, matching `54:2680`. | Rendered `54:3016` at 2×: red triangle + ink title + full-width stacked buttons, safe action on top holding the focus ring. |
| **A6** | Three frames clipped; audits measured the wrong box | `53:2471` and `52:2467` inter-dialog gap 24 → **12** (440×3 + 12×2 = 1344, exactly the row's own width). Cover mosaics `51:2115`, `51:2139`, `51:2186`, `51:2213` gap 4 → **2** (174 + 2 + 88 = 264). `48:1904` raised so the sheet ends exactly on the 844 fold. | Per-node re-check: `53:2638` +0, `52:2543` +0, `51:2118` +0, `48:1904` +0. **Full parent-relative audit re-run over both pages** — see §4. |
| **A7** | Phone lightbox had no zoom control at all | Zoom cluster cloned from `44:3920` into the V5 viewport `48:1878` → new node **`69:4961`** (`69:4962` zoom out, `69:4963` zoom in, `69:4964` chip "Fit · press 0 to reset"). Cloned rather than rebuilt so the 44×44 targets, the `IconButton On media` variant and every variable binding are inherited exactly. | Rendered `48:1878` at 1.1×: both buttons and the chip sit on the stage above the sheet, 44×44 each, glyphs legible (they inherit the A2 fix). Sheet and cluster re-fitted after A9 changed the sheet height: cluster 365–409, sheet 417–**844** = the fold. |
| **A8** | Implementation notes drawn inside real components | Six strings replaced with product copy, and the contract kept as an annotation rather than lost: `I33:97;17:35` (Banner) → "Uploading 6 files. 2 finished, 2 need your attention."; `I37:2023;17:35` (Banner, 390) → "Uploading your photos. You will be told when each one finishes or fails."; `I39:1766;9:22` and `I39:1979;9:22` (TextField helper) → "Press Enter to sign in and continue."; `39:1788`, `39:1875`, `39:1999` (dialog footnote) → "Press Escape to close this. You stay on the page you were on, and a banner at the top will say you are signed out."; `50:1894` → "Casa Barragán" (the literal "(you are here)" is gone); `47:1711` → "Processing failure is surfaced with its reason, instead of an endless spinner." (the internal prompt quotation is gone). The `aria-live` contract was appended to the annotation `33:381`. The annotation card that looked like the real `STORAGE` card beside it (`33:376`) is now dashed, unfilled, headed `DESIGN NOTE — NOT PRODUCT UI · EVERY ROW IS OPERABLE`. | Each edit returns its before/after string; read back after writing. Verbatim originals are preserved in §3 so nothing is lost. |
| **A9** | Delete is the most prominent control on the page | The four page-level Delete buttons demoted from filled `Kind=Danger` to **quiet-danger** — `Kind=Quiet` plus a `color/danger` label — and separated from the constructive cluster by a divider: `44:3991` (V1, divider `73:2883`), `50:1954` (A1, divider `73:2887`), `48:1805` (V4, divider `73:2891`), `48:1939` (V5 sheet, divider `73:2895`). In `46:1576` the trash is separated from download/details by a divider `73:2896`. The confirmation dialogs keep their filled danger button, which is correct there. | Rendered `44:3966` at 2× and `50:1860`: the constructive cluster is outlined Secondary, a full-width rule then separates a quiet red "Delete" / "Delete album". Rendered `46:1590` at 2×: the trash now sits after a visible separator. |
| **A11** | "Quiet" reads as static text | Root cause in the component. All six `Button` `Kind=Quiet` variants (`7:75`, `7:81`, `7:87`, `7:93`, `7:99`, `7:105`) given a 1px `color/line` hairline, `INSIDE`. Distinct from Secondary, which is `bg-elevated` fill + 1.5px. | Visible on `44:3966`, `50:1860`, `48:1878`. `color/line` is D1's measured ≥3:1 boundary token: **3.49:1 Light / 4.11:1 Dark** on `color/bg` (D1 §4), so the resting affordance clears the non-text floor. |
| **A12** | Header count contradicted the footer | `33:96` → "6 files · 2 finished · **2** need your attention", matching "1 failed · 1 rejected". | Read back after the edit. |
| **A12** | The one frame demonstrating zoom did not demonstrate zoom | `46:1633` resized 420×630 → **980×1472** and positioned x 230, y −296, i.e. 200% of fit-to-stage-height with a pan implied; it is also moved **below** the chrome in z-order so the top bar, prev/next and bottom bar render over the media as they should. | Rendered `46:1577` at 0.7×: the photo now exceeds the stage and is clipped top and bottom, so "200% · arrows pan · 0 resets" states what is drawn. |
| **A12 follow-on** | Regression I introduced: the enlarged photo left the lightbox counter without a backing | `46:1590` given an 88% `color/on-media-scrim` fill (the bottom bar already had one); `46:1596` counter rebound to `color/on-media`. | Rendered `46:1590` at 1.4×: white counter on the scrim bar, same worst case as the chip, **19.7:1**. |
| **A10** | Duplicate / near-duplicate components | **Descriptions only — nothing renamed** (chair ruling 4). Appended usage and deprecation contracts to `Meter` (`31:86`), `ProgressBar` (`28:58`), `VisibilityBadge` (`26:80`), `SelectionCheckbox` (`28:81`), and to `PhotoCard` (`12:263`), which now records that it is unused in the first slice, why, and that its `Sensitive` safety-blur state is consequently exercised nowhere. | Read back: each description written, 700–1460 chars. |
| **A1 / punch 4** | Stopping the next agent picking up the D1 shell | The review asked for a **rename**; the chair forbade it. Instead `TopNav` (`15:74`) and `TabBar` (`15:32`) carry a description beginning **"M2+ ONLY — NOT FOR M1"**, naming the M1 replacement and the milestone each missing destination belongs to. The components themselves are untouched. | Read back after writing. |
| — | Side-effect of A2, prevented | The zoom glyphs are now on-media-only and would have been white-on-grey on the Icons reference board. Added a labelled near-black backing **`76:2`** behind `5:106` and `5:111` on page `4:32`. | Rendered `76:2` at 4× with `contentsOnly: false`: both glyphs legible, `+` and `−` clear. |

---

## 2. What was NOT fixed, and why

| # | Finding | Why not |
|---|---|---|
| **A12** | Ratio-correct queue thumbnails in `33:65` | **Blocked by the Figma API, with a reproducer.** The seven thumbnails are `AspectPlaceholder` instances nested inside `UploadRow` instances. `resize()` on a node inside an instance does not apply, and `x` throws `This property cannot be overridden in an instance: relative-transform` — the same wall D2b hit on `ProgressBar`. Swapping only the `Ratio` variant would change the label to "3:2" while the box stayed 56×56, i.e. a label contradicting the drawing, which is worse. The only remaining route is editing the shared `UploadRow` master, which would impose one file's aspect ratio on every instance of that state everywhere. Left for a builder, where the real ratio is computed. |
| **A13** | No designed signed-out public photo page | Not drawn. This is a **new surface**, not a repair, and the review itself offers stating the exclusion as the alternative. **Stated here explicitly so the owner accepts it knowingly: the first slice contains no signed-out public or unlisted photo page.** It is the only surface a signed-out visitor can reach at M1 and the destination of every share link. |
| **A14** | Control matrices do not cover what is drawn | Requires editing `FIRST-SLICE-library-viewer-albums.md` §3 and `FIRST-SLICE-auth-system.md` §9. This round was scoped to the Figma file plus this one document. The shell rows that are now needed on `32:2` are exactly D2a's §3.7 rows, since every M1 frame now instances D2a's shell. |
| **A9 (part)** | Delete off the thumb-resting position in `48:1877` | Delete is demoted and separated but is **still the bottom-most control in the sheet**. Moving a destructive action to the top of a non-confirming actions sheet is its own hazard, and adding a Cancel row below it re-broke the 844 fold. Left as a deliberate open item. |
| **A9 (part)** | `BulkBar` Delete and `47:1729` | The bulk-bar Delete is inside the `BulkBar` component and is a confirm *trigger*; `47:1729` "Delete this photo" sits on a failed-processing band. Neither was named in A9's frame list and neither was changed. |
| **A11 (part)** | Re-classifying navigation instances as accent links | The component now has a resting affordance, but "Create an account", "Back to your library", "Go to the home page" etc. are still buttons rather than accent-coloured links. That is a per-instance semantic decision across ~12 controls and touches copy classification. |
| **A8 (part)** | One annotation style across both pages | `33:376` was re-styled because it was visually identical to a real card beside it. The remaining `color/accent-soft` annotation blocks on `32:2` are still accent-soft rather than D2a's dashed box — cosmetic, and they never look like controls. |
| **A10 (part)** | Picking one component per concept | Deprecation is recorded in descriptions only. Actually removing `ProgressBar`-as-quota / the `visibility marker` / `Checkbox`-on-media duplication, and giving the quota bar a treatment different from the in-flight upload bar on `33:65` (punch 9), were not done: both need a deletion or a rename, which the chair forbade this round. |
| **(c)** | Every owner question | Untouched by ruling: `Download original` is still drawn in `44:3869`, `48:1714`, `46:1576` and `48:1877`; the sign-up duplicate-email copy is unchanged; the theme-invariant near-black stage, quota numbers, album depth, share-grant expiry and the rest are exactly as drawn. |
| **(b)** | Fine-to-fix-after-acceptance list | Out of scope for this round, except where an item overlapped a ruling: the 2px `cover col` clipping (b19) was fixed as part of A6. |

---

## 3. Strings moved out of components (preserved verbatim)

Nothing was lost. These were drawn inside product components where a builder would have shipped them.

| Node | Original string | Now |
|---|---|---|
| `I33:97;17:35` | `aria-live="polite" · announces start, each 25% step of the batch, every completion and every failure — never a per-tick percentage.` | Moved into the annotation `33:381`; the Banner carries real copy |
| `I37:2023;17:35` | `aria-live="polite". Never a per-tick percentage.` | Same contract, already recorded in D2b §4.4 |
| `I39:1766;9:22`, `I39:1979;9:22` | `Initial focus lands here, not on a button. Enter submits.` | Contract already recorded in D2a §4.4; helper is now product copy |
| `39:1788`, `39:1875`, `39:1999` | `Escape closes this dialog and returns focus to the control you were using; a persistent "You are signed out" banner then replaces it at the top of the page. Background content is inert while the dialog is open.` | Contract already recorded in D2a §4.4 and §5.4 (`reauth.escape`) |
| `50:1894` | `Casa Barragán (you are here)` | The current page is `aria-current="page"`, not rendered text |
| `47:1711` | `prompt 03: "Surface processing failure instead of leaving an endless spinner."` | Re-worded as an exhibit caption; the prompt file is not quoted on the canvas |

---

## 4. Verification performed

### Shell census — page `32:2`, after the fix

| Component | Before | After |
|---|---|---|
| `TopNav` (D1, M2+) | 11 | **0** |
| `TabBar` (D1, M2+) | 5 | **0** |
| `TopNav / M1` | 0 | **11** |
| `TabBar / M1` | 0 | **5** |
| `AppBar / M1` | 0 | **1** |
| `icon/Bell` (the fabricated unread dot) | 11 | **0** |
| `icon/Search` | 17 | **1**, and that one is inside the hidden, superseded page-title control in `42:3331`; it renders nowhere |

Page `27:2` is unchanged in shell terms: `TopNav / M1` ×14, `AppBar / M1` ×9, `TabBar / M1` ×7.

### Parent-relative overflow audit — every node against its *immediate* parent

This is the audit both hand-offs got wrong; it is re-run here parent-relative, not against the
top-level frame.

| Page | Nodes scanned | Offenders before | Offenders after |
|---|---|---|---|
| `27:2` — M1 · Auth & system (46 frames) | 2,670 | **1** (`meter-fill` overflowing `meter-track` by 13px in `42:1450`) | **0** |
| `32:2` — M1 · Library, viewer, albums (22 frames) | 4,207 | **7** (`48:1904` +16 vertical; `53:2638` +24; `52:2543` +24; four `cover col` +2 each) | **1** |

The single remaining offender on `32:2` is **`46:1633`, the V2 photo, and it is deliberate**: it is
the 200% zoom demonstration, drawn larger than the stage and clipped by `46:1577` so that the zoom
chip states what is drawn. It is the fix for A12, not a defect. Every other offender is closed.

### Contrast re-measured (composited, against the real backing — not against a convenient canvas)

| Pair | Before | Light | Dark |
|---|---|---|---|
| Zoom `+`/`−` glyph on the `on-media-scrim` chip over the stage | **1.05:1 (Light)** | **19.7:1** | **20.1:1** |
| `SelectionCheckbox` resting white ring vs its dark neighbours | ring invisible on a light card | **15.4:1** | **15.4:1** |
| `SelectionCheckbox` scrim halo vs a light card | — | **13.5:1** | n/a |
| Lightbox counter on the new scrim bar | lost its backing when the photo grew | **19.7:1** | **19.7:1** |
| `Button Kind=Quiet` hairline (`color/line`) on `color/bg` | no boundary at all | **3.49:1** | **4.11:1** |

### Meter — drawn fraction vs stated fraction, every instance

| Instance | Frame | Stated | Drawn before | Drawn after |
|---|---|---|---|---|
| `42:1035` | `42:1012` | 62% | 29.6% | **62.0%** |
| `42:1110` | `42:1078` | 91% | 43.6% | **91.0%** |
| `42:1191` | `42:1159` | 100% | 47.9% | **100%** |
| `42:1260` | `42:1238` | 100% | 47.9% | **100%** |
| `42:1348` | `42:1325` | 91% | 95.1% | **90.8%** |
| `42:1463` | `42:1450` | 100% | 104.6% (overflowed the track) | **100%** |

### Screenshots rendered and visually inspected this round

`38:2168` (1440 Light), `42:3331` (390), `41:1175` (1440 Dark), `50:1860` (1440 Light),
`38:2261` and `41:1195` at 4× (checkbox, both themes), `44:3920` at 6× (Light) and `46:1649` at 6×
(Dark) (zoom cluster, both themes), `42:1110` at 2× (meter), `53:2471` (the previously clipped
dialog row), `54:3016` at 2× (destructive 390 sheet), `48:1878` at 1.1× (V5 lightbox),
`44:3966` at 2× (owner actions), `46:1577` at 0.7× and `46:1590` at 1.4× (V2), `76:2` at 4× (icons
board). They were inspected in-session through short-lived URLs and inline renders and are **not**
archived under `docs/evidence/`.

---

## 5. New node ids a builder needs

| Node | What it is |
|---|---|
| `62:2862` | `AppBar / M1` instance at the top of `42:3331` (the 390 library) |
| `69:4961` | V5 zoom cluster in `48:1878`; `69:4962` zoom out, `69:4963` zoom in, `69:4964` zoom-level chip |
| `69:2859` / `69:2860` | Destructive 390 sheet title row and its `TriangleAlert` |
| `73:2883`, `73:2887`, `73:2891`, `73:2895`, `73:2896` | Dividers separating the destructive action from the constructive cluster in V1, A1, V4, V5 and the V2 lightbox top bar |
| `76:2` | On-media backing behind `icon/ZoomIn` / `icon/ZoomOut` on the Icons board — a reminder that those two glyphs are on-media-only |
| `VariableCollectionId:67:1772` | `Meter fit (fill width)`; modes `Natural 320` / `Column 670` / `Column 308`; variables `meter/fill-62`, `meter/fill-91`, `meter/fill-100` |
| `42:3332` | Renamed `page-title (Library)`; `42:3334` and `42:3339` inside it are hidden, superseded controls, not deleted |

---

## 6. What still looks wrong

Honest, after looking at the renders.

1. **`Download original` is still drawn on four frames** and the ledger puts `VZ-DOWNLOAD-001` in M3.
   Untouched by ruling — but it is still a control that must never ship dead, and it now sits in a
   full-width row in the V5 sheet where it reads as a first-class action.
2. **Delete is still the bottom-most control in the V5 actions sheet** — demoted and separated, but
   still nearest the thumb.
3. **The bulk-bar Delete is still a filled red button** on `38:2168`, `41:1175` and `42:3331`, so the
   loudest control on the library page is still the destructive one.
4. **`Kind=Quiet` now looks close to `Kind=Secondary`** — 1px `color/line` and no fill versus 1.5px
   and a `bg-elevated` fill. It is a real affordance and it is measurable, but a designer may prefer
   an accent-link treatment for the navigation instances, which was not done.
5. **The queue thumbnails in `33:65` are still square** while their rows state 6240×4160 and
   48000×3000. This is the brief's headline rule broken in the easiest possible place, and the API
   blocked the repair — see §2.
6. **`U5`/`U6`/`V4`/`A3` still carry a local `mobile-header`** rather than `AppBar / M1`. These are
   contextual back-bars for sub-pages (Back + title + one action) and are a legitimate pattern, but
   `U5`/`U6` are an Upload **tab root** wearing a back-bar, which is inconsistent with `L3` now
   wearing the app bar. Worth an explicit decision.
7. **`42:3331` carries a hidden, superseded bar.** Nothing renders it, but a hidden node with two
   dead controls inside it is a trap for the next agent. It is hidden rather than deleted because
   the ruling was additive-and-corrective only.
8. **The V2 photo is a large neutral placeholder.** Drawing 200% correctly means the stage is now
   mostly one flat near-black rectangle labelled "2:3". It is geometrically honest and it makes the
   chip true, but it is not a persuasive demonstration of a photograph at 200%. With a real image it
   would read properly; **there are still no real photographs anywhere in the file**.
9. **`Meter`'s correctness now depends on a builder picking the right mode.** If a Meter is placed in
   a column that is neither 670 nor 308, the drawn fraction will be wrong again. The component
   description says so; production must compute the real width.
10. **Nothing here has been reviewed.** This is a single-pass fix round by one agent, checked against
    its own screenshots. `AGENTS.md` requires independent review, and the owner has not approved any
    of it. Status remains **PROPOSED**.

---
---

# Second pass — response to "Re-check after the fix pass"

Scope: the two things the re-check would not show an owner (§R5), the one regression the first pass
introduced (§R2.1), the tidy list, and the `Meter fit` disclosure. Same rulings: M1 shell canonical,
owner questions stay as drawn, fix in the component, additive/corrective only, look at every change
in **both themes** before claiming it.

## S1 — `BulkBar` Delete, and the V5 sheet's Delete

**Fixed in the component, so all three instances inherit.** `BulkBar` (`30:191`) is a single
component; its `btn:Delete` (`30:205`) went from `Kind=Danger` (filled red) to **`Kind=Quiet` with a
`color/danger` label and a leading `icon/Trash2`** (`Leading icon#7:75` = true, `Icon#7:100` =
`5:32`, 5 glyph vectors rebound to `color/danger`), preceded by a new divider **`78:5032`** so the
destructive action is separated from the constructive pair — the same treatment the other five
surfaces already had. The filled danger style is now reserved for the confirm button inside the
destructive-confirmation dialogs (`54:2684`, `54:2715`, `54:2740`, `54:3027`) and nowhere else.

The four Deletes demoted in the first pass — `44:3991` (V1), `50:1954` (A1), `48:1805` (V4),
`48:1939` (V5) — **also gained the `Trash2` glyph**, so no demoted destructive control anywhere is
carried by colour alone: it is word + glyph + colour + separation.

**Checked:** rendered `38:2460` (L1, **Light**) and `41:1282` (L4, **Dark**) at 1.6×. In both, the
bar reads "3 photos selected · [Add to album] [Set visibility] │ 🗑 Delete … Clear selection" — two
outlined Secondary buttons, a rule, a red-glyph-plus-red-label quiet Delete, and an accent quiet
"Clear selection". The library page's only filled button is now "Upload".

**V5 sheet Delete — position fixed too.** `48:1904` was reordered so the benign control is the
thumb-resting one: `… Download original › divider (73:2895) › Delete › divider (78:5087) ›
Show Exif and file details`. Delete now sits between two rules and is no longer bottom-most.

Because that added 9px, the whole V5 stage was re-fitted (this also closes the re-check's A7
residual, below): photo `48:1892` → **187 × 280 at (102, 68)**, zoom cluster `69:4961` → y 356–400,
sheet `48:1904` → y 408, ending **exactly on 844**; step controls `48:1894` / `48:1899` re-centred on
the new photo at y 186. Measured after the move: `overlapPhotoCluster: false`,
`overlapClusterSheet: false`.

**Checked:** rendered `48:1878` at 1.1× (Dark): the zoom cluster sits in the gutter **below** the
photograph, nothing overlaps, Delete is fenced by two rules, "Show Exif and file details" is last.

**Still wrong:** the photograph is now 187 × 280 in a 390 viewport — small. That is the honest cost
of a six-action sheet plus a zoom cluster plus a 44px-target rule on an 844-tall phone; I chose a
smaller photo over an overlapping control. No `Close`/`Cancel` row was added at the bottom of the
sheet (the canonical iOS answer) because it would have forced the photo down to roughly 152 × 228.

## S2 — The "1:1" labels on the queue thumbnails

**Choice: the label is removed from the queue previews, and the reason is stated on the canvas.**

Reason, against the brief: `DESIGN_BRIEF.md` forbids destructive cropping **of the photograph**
("Preserve the image's aspect ratio; do not default to destructive cropping"). A 56 × 56 row preview
in an upload queue is a list affordance, not the photograph — the original is untouched, and the
library grid and the viewer are where the brief's rule bites. Re-labelling the square preview "3:2"
would have been worse than leaving it: the *drawing* would still be square, so the label would
contradict the pixels rather than the copy. So the ratio claim is withdrawn, not falsified.

`ratio-label` set `visible = false` on **17** queue previews across six frames — 7 in `33:65`, 4 in
`37:1977`, 2 in `37:2151`, 4 in `36:332` — every 56 × 56 `AspectPlaceholder` inside an `UploadRow`.
Visibility *is* overridable inside an instance even though geometry is not, which is why this worked
where the resize did not.

The design note of every upload frame (`33:381`, `37:2120`, `37:2263`, `36:513`, `36:652`, `32:100`)
now ends with: *"Queue rows use a 56×56 centre-cropped PREVIEW of the file, so no ratio is stated on
them — a list preview is not the photograph. The photograph itself is never cropped: the library
grid draws 3:2 / 2:3 / 1:1 / 16:9 / 3:1 cells at their real ratio and the viewer stage is
contain-fitted."*

**Checked:** rendered `37:1977` at 0.42× and `33:65`: the queue rows now show plain neutral previews
with no ratio claim beside "6240 × 4160".

**Still wrong:** the previews are square placeholders, so the *centre-crop* itself is asserted rather
than drawn. Nested-instance geometry remains blocked (`relative-transform` cannot be overridden); the
reproducer from the first pass stands.

## S3 — REGRESSION: `Quiet` had converged on `Secondary`

**Cause:** the first pass gave `Kind=Quiet` a 1px `color/line` hairline. `Secondary` is 1.5px
`color/line` plus a `bg-elevated` fill — at normal viewing distance, the same thing.

**Fix, at the component.** The hairline is removed from all six Quiet surfaces (`7:75`, `7:81`,
`7:87`, `7:93`, `7:99`, `7:105`) and the affordance is carried by colour-of-type instead: Quiet's
label is now `color/accent` (`7:79` Default, `7:97` Focus, `7:109` Loading), `color/accent-hover`
(`7:85`) and `color/accent-pressed` (`7:91`). `Disabled` (`7:103`) stays `color/ink-3`. The existing
`color/bg-tint` hover and pressed **surfaces** are untouched, so a quiet button still lifts under the
pointer, and `Kind=Quiet, State=Focus` still carries its 2px `color/focus-ring` root stroke — the
visible focus state that motivated A11 is intact.

Three ranks now differ on **two** axes each, not one:

| Rank | Surface | Border | Label |
|---|---|---|---|
| Primary | `color/accent` fill | none | `color/on-accent` |
| Secondary | `color/bg-elevated` fill | 1.5px `color/line` | `color/ink` |
| Quiet | none (tint on hover/pressed) | none | `color/accent` |

**Checked side by side in both themes, as asked.** Built a standing board
**`78:10` — `⟦hierarchy check⟧ Primary / Secondary / Quiet — Light and Dark`** on the Button page
(`4:21`), rows `78:11` (Light) and `78:38` (Dark, via `setExplicitVariableModeForCollection` on the
`Color` collection), and rendered it at 3×. Solid blue / outlined white / blue text, unmistakably
three weights in **both** rows. Contrast is D1's own measured pair: accent as label **4.72:1 on
`color/bg` and 4.93:1 on `color/bg-elevated` (Light), 7.70:1 (Dark)** — above 4.5:1 without the
hairline doing any work.

Re-checked the three surfaces the re-check named as flattened: `38:2460` / `41:1282` (bulk bar,
both themes), `42:3331` (390 bulk bar) and `44:3966` (V1 action column). Hierarchy reads in all of
them.

**Still wrong:** Quiet is now closer to a link than to a button, which is the trade for separating it
from Secondary. It is the treatment the original review itself proposed ("accent colour for
navigation"), but a designer may want a tint chip for the *action* instances rather than accent for
all of them. Nothing relies on the accent colour alone to convey meaning — every quiet control is
labelled in words.

## S4 — Tidy

| Item | What changed | Checked |
|---|---|---|
| Two false design notes | `54:3035` — "so the thumb's resting position is never on Delete" → "so the destructive action never holds focus on open. It is still the bottom-most control in the destructive sheet — a deliberate trade, recorded in FIXES-first-slice.md." (first attempt silently failed on a curly apostrophe; retried and confirmed `changed: true`). `48:1947` — "nothing sits over the image except the close, visibility and step controls" → "nothing sits over the image at all: the close and visibility controls are in the top bar, the step controls sit in the side gutters, and the zoom cluster sits in the gutter between the image and the sheet", which the re-fit in S1 made true. | Both read back after writing |
| `42:3331` two stacked header rules | `42:3332` bottom stroke removed (1 stroke → 0), so the phone library opens with the app bar's rule only, like D2a's `43:3320`. | Rendered `42:3331` at 0.5×: one rule |
| U5 / U6 wore a back-bar on a tab root | `AppBar / M1` `State=Signed in` inserted at index 0 of `37:1977` (**`80:2929`**) and `37:2151` (**`80:2937`**); the local bars `37:1978` / `37:2152` renamed `page-title (Upload)` with their bottom rules removed; their Back buttons moved out (see below). Frames hug to 1793 / 1470. | Rendered `37:1977` at 0.42×: wordmark + account, "Upload" title, no back arrow, Upload tab active — the same shell as `42:3331` and the auth pages |
| Three stale tab-bar layer names | `37:2121`, `37:2264`, `42:3502` renamed **`TabBar / M1 (fixed to the bottom of the viewport)`**. Layer names only; no component or variable renamed. | Read back; a name-based census no longer mis-reads them |
| The surviving A8-class string | `53:2655` ("In flight: the confirm button is the busy control (aria-busy, stable name)…") moved out of the live dialog body `53:2646` into the frame's annotation `53:2848`, renamed `moved out of the dialog: in-flight contract`. Dialog `53:2638` shrank 398 → 322 and still overflows its row by **0**. | Moved and re-measured |
| V2's featureless stage | `46:1633` re-panned to y **100**, so the photograph's **top edge is visible inside the stage** and the image runs off the bottom — a real pan position rather than an edge-to-edge field, with the library grid still showing in the side gutters. Placeholder label set to "2:3 · shown at 200%". | Rendered `46:1577` at 0.66× (Dark) |
| V5 zoom cluster overlapping the photo | Closed by the S1 re-fit — cluster in the gutter, measured `overlapPhotoCluster: false`. | Rendered `48:1878` |

## S5 — `Meter fit` marked as Figma-only

In Figma: the collection `Meter fit (fill width)` (`VariableCollectionId:67:1772`) now carries
`hiddenFromPublishing = true` and a description beginning **"DO NOT MIRROR INTO CODE."**; all three
variables (`meter/fill-62`, `meter/fill-91`, `meter/fill-100`) are likewise
`hiddenFromPublishing = true` with the same warning in their descriptions. Both properties were
accepted by the API (`collectionHidden: true`, `collectionDescription: set`).

In the repository: a new **§8.1 "DO NOT MIRROR INTO CODE — `Meter fit (fill width)`"** in
`docs/design/figma/README.md`, inside the mirroring section where a builder will actually be
standing, naming the collection, its modes, its variables, and the rule that a mirroring script
should key on the presence of `var(--vz-…)` code syntax rather than on "every local variable".

**Still wrong:** `get_variable_defs` on a Meter instance will still return `meter/fill-91` in the
same payload as the real tokens — publishing flags are not visible there. The README rule and the
absent code syntax are the defence.

## S6 — Parent-relative overflow audit, re-run on `32:2`

**Should hidden nodes count? Yes — and rather than argue it, I removed the cause.** A hidden node
whose geometry no longer fits its parent is exactly the stale-layout signal an audit exists to
catch, so this run counts hidden and visible nodes separately. The re-check's two extra offenders
were `42:3334` and `42:3339`, the superseded search and upload controls left hidden inside
`page-title (Library)`. They are no longer hidden inside a product frame: together with the two U5/U6
Back buttons they were **moved out** into a dashed, labelled page-level holder
**`80:2927` — `⟦superseded⟧ Local 390 bar controls — replaced by AppBar / M1`** and made visible
there. `42:3332` now contains exactly one child, `header-title`.

| Page | Nodes scanned | Offenders (hidden included) | Offenders (visible only) |
|---|---|---|---|
| `32:2` | 4,258 across 23 top-level nodes | **1** | **1** |

The single offender is `46:1633` — the V2 photograph, deliberately larger than the 1440 × 900
viewport so that "200% · arrows pan · 0 resets" states what is drawn. It is the fix for A12, not a
defect. Both counts now agree, and both agree with the re-check once its two hidden offenders are
accounted for.

## S7 — What still looks wrong after the second pass

1. **The V5 photograph is small** (187 × 280) — the cost of a non-overlapping zoom cluster plus a
   six-action sheet on an 844-tall phone. No `Close` row was added for the same reason.
2. **V5's Delete is off the bottom but still reachable**; "Show Exif and file details" is now the
   thumb-resting control.
3. **`Quiet` now reads as a link more than a button** — the price of separating it from Secondary.
4. **The V2 stage is still a flat placeholder.** A visible top edge and a truthful chip are as far as
   this can go with **no real photographs anywhere in the file** — still the single largest gap
   between "designed" and "proven".
5. **Queue previews assert a centre crop they do not draw** (nested-instance geometry, still blocked).
6. **`Meter` correctness still depends on a builder picking the right mode**, and `get_variable_defs`
   still surfaces those values beside real tokens.
7. **The duplicated components survive** (`visibility marker` vs `VisibilityBadge`, `ProgressBar` vs
   `Meter` for quota, `Checkbox` vs `SelectionCheckbox`) — deprecation is in the descriptions only,
   because resolving them needs a rename or a delete.
8. **No signed-out public photo page**, unchanged, and correctly the owner's decision rather than a
   defect.
9. **Still nothing independently verified.** Two passes by one agent, checked against its own
   screenshots. Status remains **PROPOSED**.
