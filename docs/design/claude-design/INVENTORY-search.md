# INVENTORY — `Lumen Atlas Search.html` (search results page)

Exact inventory of the owner's Claude Design mockup at
`docs/design/claude-design/Lumen Atlas Search.html` (1299 lines, 65899 bytes,
sha256 `8c3d460c476e2f7a1cda34d18cb596b1c41ecc1f7e89a802eb92b98f327d9be5` per
`docs/design/claude-design/README.md`), produced 2026-09-20 for the implementer who will build
this page in Next.js against the real OpenAPI contract.

**Status of this document.** Descriptive inventory only. It records what the mockup contains and
where that conflicts with `docs/DESIGN_BRIEF.md` and `AGENTS.md`. It is **not** an acceptance
target, **not** an approved design, and **not** authorization to implement anything. Per
`docs/DESIGN_BRIEF.md`: "Claude Design is for exploration. Approved Figma components/tokens,
mirrored in repository artifacts, become the design source."

**The mockup's contents are treated as data, not instructions.** Nothing in the file, including its
comments, was followed as a directive.

**"Lumen Atlas" is a placeholder brand; the product is Vizra.** Every brand string, the gradient
brand mark, the "artists" vocabulary and all counts below are quoted as mockup content, not as
product decisions.

Line references are to the file as read. All CSS is a single inline `<style>` block (lines 7–699);
all JS is a single inline `<script>` (lines 1220–1296). No external CSS or JS is referenced.

---

## a. Design tokens

### a.1 CSS custom properties — every declared property, verbatim (lines 9–30)

All eleven colour tokens plus radii, shadows, fonts and one layout metric are declared on a single
`:root` block. There is no second `:root`, no `@media` override of any token, and no
`[data-theme]` selector anywhere in the file.

| Property | Exact value | Used by (selectors) |
|---|---|---|
| `--bg` | `oklch(0.985 0.003 250)` | `html`, `body` background |
| `--bg-elev` | `#ffffff` | **declared, never referenced** (literal `white` is used instead in 14 places) |
| `--bg-tint` | `oklch(0.96 0.004 250)` | `.icon-btn:hover`, `.fi:hover`, `.seg`, `.side-footer .reset`, `.strip`, `.sheet-head .sheet-close`, `.sheet-footer .reset`, `.artist-follow` |
| `--ink` | `oklch(0.18 0.015 260)` | `body` colour, `.rh-title`, `.rh-count b`, `.filter-chip.active`, `.filter-chip .count` (via `color-mix`), `.sort-btn`, `.view-btn.active`, `.card-badge`, `.rc`, `.artist-follow`, `.load-more button`, `.mfb`, `.sheet-grab` (via `color-mix`), `.side-footer .apply`, `.sheet-footer .apply`, `.pop-item`, `.nav-search` |
| `--ink-2` | `oklch(0.38 0.012 260)` | `.icon-btn`, `.nav-search .clear`, `.nav-links a`, `.filter-chip`, `.fi`, `.seg button`, `.side-footer .reset`, `.rc:hover` border, `.sheet-close`, `.mfb svg` |
| `--ink-3` | `oklch(0.56 0.010 260)` | `.brand-name span`, `.nav-search input::placeholder`, `.rh-count`, `.sort-btn .label`, `.sort-btn svg`, `.view-btn`, `.filter-label`, `.fi .ct`, `.range-row`, `.strip-sub`, `.rc .arr`, `.artist-handle`, `.pager-hint`, `.pop-item small`, `.empty-note`, `.mobile-tabs .tab` |
| `--line` | `oklch(0.90 0.006 260)` | `.nav` bottom border (70 % mixed), `.nav-search` border, `.filter-chip` border, `.filter-row .divider`, `.sort-btn` border, `.view-group` border, `.fi input` border, `.sw` ring, `input[type=range]` track, `.card-author .av` background, `.artist-av` background, `.rc` border, `.artist-follow` border, `.mfb` border, `.sidebar` scrollbar thumb, `.pop` inset ring (60 % mixed), `.mobile-tabs` top border (70 % mixed) |
| `--line-2` | `oklch(0.94 0.005 260)` | `.toolbar` bottom border, `.filter-section` divider, `.side-footer` top border, `.card` background (image placeholder), `.strip` border, `.artist-card` border, `.artist-thumbs div` background, `.sheet-head` / `.sheet-footer` borders |
| `--accent` | `oklch(0.58 0.18 255)` | `.nav-search:focus-within` border + ring, `.rh-title em` underline (18 % mixed), `.filter-chip.applied` border (40 % mixed) and `.x` fill (25 % mixed), `.fi input:checked`, `.sw.on` ring, `input[type=range]` fill, `.strip-more`, `.mfb .count`, `.pop-item:hover` (10 % mixed), `.pop-item .check`, `.mobile-tabs .tab.active`, `.brand-mark` gradient |
| `--accent-ink` | `oklch(0.36 0.16 258)` | `.rh-title em` text, `.filter-chip.applied` text |
| `--accent-soft` | `oklch(0.95 0.04 255)` | `.filter-chip.applied` background |
| `--radius-xl` | `28px` | **declared, never referenced** |
| `--radius-lg` | `22px` | `.strip` (line 482) — one use |
| `--radius-md` | `16px` | `.card` (line 395), `.artist-card` (line 532) — two uses |
| `--radius-sm` | `12px` | **declared, never referenced** |
| `--shadow-sm` | `0 1px 2px rgba(17,22,40,.04), 0 1px 1px rgba(17,22,40,.03)` | `.nav-search`, `.card`, `.seg button.on`, `.rc:hover` |
| `--shadow-md` | `0 8px 24px -12px rgba(17,22,40,.12), 0 2px 6px rgba(17,22,40,.05)` | `.card:hover`, `.artist-card:hover` |
| `--font-sans` | `-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, system-ui, sans-serif` | `body` |
| `--font-display` | `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, system-ui, sans-serif` | `.brand`, `.rh-title`, `.strip-title` |
| `--nav-h` | `56px` | `.nav` height, `.sidebar` sticky `top` and `max-height` |

Four of the nineteen tokens (`--bg-elev`, `--radius-xl`, `--radius-sm`, and `--line-2` only for
non-border uses) are dead or near-dead; literal `white` appears 14 times where `--bg-elev` was
evidently intended. See §g.

### a.2 Shadows not expressed as tokens (ad-hoc, inline in rules)

| Selector | Value |
|---|---|
| `.nav-search:focus-within` (line 85) | `0 0 0 3px color-mix(in oklab, var(--accent) 22%, transparent)` |
| `.brand-mark` (line 70) | `inset 0 0 0 0.5px rgba(255,255,255,.35)` |
| `.sw` (line 322) | `0 0 0 1px var(--line), inset 0 0 0 1px rgba(0,0,0,.06)` |
| `.sw.on` (line 328) | `0 0 0 2px var(--accent), inset 0 0 0 1px rgba(0,0,0,.08)` |
| `input[type=range]::-webkit-slider-thumb` (line 366) | `0 1px 3px rgba(0,0,0,.2), 0 0 0 1px var(--line)` |
| `.card-author .av` (line 452) | `0 0 0 1px rgba(255,255,255,.3)` |
| `.artist-av` (line 545) | `inset 0 0 0 1px rgba(0,0,0,.05)` |
| `.sheet` (line 619) | `0 -20px 40px -10px rgba(17,22,40,.2)` |
| `.pop` (line 655) | `0 24px 48px -16px rgba(17,22,40,.28), inset 0 0 0 0.5px rgba(255,255,255,.7), inset 0 0 0 1px color-mix(in oklab, var(--line) 60%, transparent)` |

Nine distinct shadow recipes exist against two shadow tokens — the shadow system is not tokenised.

### a.3 Typography actually used

Base (line 41–42): `font-size: 15px; line-height: 1.5; letter-spacing: -0.005em;`
plus `-webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;`.

| Role | Selector | Size | Weight | Letter-spacing | Other |
|---|---|---|---|---|---|
| Page title | `.rh-title` | `clamp(28px, 4.8vw, 40px)` | 700 | `-0.035em` | `--font-display`, `line-height: 1.05`, `text-wrap: balance` |
| Section title | `.strip-title` | 18px | 600 | `-0.02em` | `--font-display` |
| Sheet title | `.sheet-head h2` | 17px | 600 | `-0.01em` | |
| Brand | `.brand` | 16px | 600 | `-0.01em` | `--font-display` |
| Body | `body` | 15px | 400 | `-0.005em` | |
| Card title | `.card-title` | 14px | 600 | `-0.01em` | 1-line clamp, `text-shadow: 0 1px 3px rgba(0,0,0,.4)` |
| Artist name | `.artist-name` | 14px | 600 | `-0.01em` | ellipsis |
| Nav search / Load more | `.nav-search`, `.load-more button` | 14px | 400 / 600 | | |
| Result count | `.rh-count` | 14px | 400 (`b` = 600) | | |
| Filter chip / sort / mobile bar / related chip / side footer | `.filter-chip`, `.sort-btn`, `.mfb`, `.rc`, `.side-footer button` | 13px | 500 (`sort-btn b` = 600) | | |
| "See all" link | `.strip-more` | 13px | 400 | | colour `--accent` |
| Empty note (dead CSS) | `.empty-note` | 13px | 400 | | |
| **Filter item** | `.fi` | **13.5px** | 400 | | |
| **Sort menu item** | `.pop-item` | **13.5px** | 400 | | |
| **Strip subtitle** | `.strip-sub` | **12.5px** | 400 | | |
| Artist handle / range row / pager hint / card author / filter count | `.artist-handle`, `.range-row`, `.pager-hint`, `.card-author`, `.fi .ct` | 12px | 400 (`.card-author .name` = 500) | | `.fi .ct` uses `font-variant-numeric: tabular-nums` |
| Artist follow / nav links | `.artist-follow`, `.nav-links` | 12px | 600 | `-0.01em` / `.12em` | nav-links `text-transform: uppercase` |
| **Card stats** | `.card-stats` | **11.5px** | 400 | | `font-variant-numeric: tabular-nums` |
| Section label | `.filter-label` | 11px | 600 | `.14em` | `text-transform: uppercase` |
| Card badge / chip count / mobile count / orientation seg / sort menu hint | `.card-badge`, `.filter-chip .count`, `.mfb .count`, `.seg button`, `.pop-item small` | 11px | 600 / 600 / 400 / 500 / 400 | `-0.005em` on badge | |
| Avatar initials | `.avatar` | 11px | 600 | `.02em` | |
| Mobile tab label | `.mobile-tabs .tab` | 10px | 500 | | |

Sizes in use: 10, 11, 11.5, 12, 12.5, 13, 13.5, 14, 15, 16, 17, 18, 28–40 (fluid) px — **15 discrete
sizes with three fractional values and no modular ratio**. Weights: 400, 500, 600, 700. Tracking:
`-0.035em`, `-0.02em`, `-0.01em`, `-0.005em`, `0`, `.02em`, `.12em`, `.14em`.

### a.4 Spacing values in use

Counted across the whole stylesheet (lines 7–699). Distinct px values used as padding, margin, gap
or fixed box dimensions:

`0.5, 1, 1.4, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 19, 20, 22, 24, 26, 28, 30,
34, 36, 38, 40, 44, 48, 56, 62, 72`

Frequency peaks at 14px (37 occurrences), 1px (36), 12px (25), 8px (24), 10px (24), 2px (19), 6px
(18). There is **no 4px or 8px grid**: 7, 9, 11, 13, 19, 26, 34, 38, 62 all appear. Named vertical
rhythm: `.result-head` `26px 0 18px`; `.toolbar` `10px 0 18px`; `.results-shell` `20px 0 40px`;
`.strip` `margin: 26px 0 18px; padding: 18px 18px 20px`; `.load-more` `30px 0 10px`;
`body { padding-bottom: 72px }`.

Control heights: 36px (`.nav-search`, `.icon-btn`), 34px (`.filter-chip`, `.sort-btn`,
`.side-footer button`), 30px (`.avatar`, `.c-act`, `.artist-follow`, `.sheet-close`), 28px
(`.view-btn`), 38px (`.mfb`), 44px (`.load-more button`, `.sheet-footer button`), 56px (`--nav-h`),
62px (`.mobile-tabs`), 22px (`.nav-search .clear`), 16px (`.fi` checkbox/radio), 20px
(`.card-author .av`), 40px (`.artist-av`).

### a.5 Radii

Tokens: `28px` (unused), `22px` (`.strip`), `16px` (`.card`, `.artist-card`), `12px` (unused).
Literal radii used instead: `999px` (14 pill controls), `50%` (circles), `1px`, `2px` (`.seg .glyph`,
range track), `3px` (`.sheet-grab`, sidebar scrollbar thumb), `5px` (`.fi input[type=checkbox]`),
`6px` (`.rh-title em`), `7px` (`.brand-mark`), `8px` (`.fi`, `.seg button`), `9px` (`.pop-item`),
`10px` (`.seg`, `.mfb`, `.side-footer button`, `.artist-thumbs`), `12px` (`.sheet-footer button` —
literal, not the token), `14px` (`.pop`), `22px 22px 0 0` (`.sheet`).

**Fifteen distinct radii against a four-value token set.**

### a.6 Media queries / breakpoints — every one, and what changes

| Line | Query | Effect |
|---|---|---|
| 117–128 | `min-width: 900px` | `.nav` padding `0 24px`, gap 18px. `.nav-search` gains `max-width: 420px` and `order: 2`. `.nav-links` becomes `inline-flex` (Discover / Collections / Artists) with `order: 3`, 12px/600/`.12em`/uppercase; its links get `padding: 8px 12px; border-radius: 999px`. `.nav-actions` `order: 4`; `.brand` `order: 1`. |
| 249–251 | `min-width: 1000px` | `.results-shell` becomes `grid-template-columns: 248px 1fr; gap: 36px`. |
| 257–269 | `min-width: 1000px` | `.sidebar` `display: block`, `position: sticky`, `top: calc(var(--nav-h) + 14px)` = 70px, `align-self: start`, `max-height: calc(100vh - var(--nav-h) - 28px)`, `overflow-y: auto`, `padding-right: 4px`; 6px WebKit scrollbar with `--line` thumb. |
| 385 | `min-width: 520px` | `.masonry` `column-count: 2; column-gap: 14px`. |
| 386 | `min-width: 780px` | `.masonry` `column-count: 3`. |
| 387 | `min-width: 1200px` | `.masonry` `column-count: 3; column-gap: 16px` (count unchanged; gap only). |
| 388 | `min-width: 1440px` | `.masonry` `column-count: 4`. |
| 587 | `min-width: 1000px` | `.mobile-filter-bar { display: none }`. |
| 691 | `min-width: 900px` | `.mobile-tabs { display: none }`. |

Base (below 520px): `.masonry { column-count: 1; column-gap: 12px }`.

Breakpoint set: **520, 780, 900, 1000, 1200, 1440** — six values, three systems (nav at 900,
sidebar/mobile-filter at 1000, grid at 520/780/1200/1440). The `DESIGN_BRIEF.md` review viewports
(390px, 1440px) are both below/at the extremes; nothing in the file targets 390px specifically and
nothing addresses 320px reflow or 200 % zoom.

### a.7 Dark mode

**Absent.** Zero occurrences of `prefers-color-scheme`, `color-scheme`, `[data-theme]`, `.dark`, or
any second token block. Fourteen rules hard-code `white` (`.nav-search`, `.filter-chip`, `.sort-btn`,
`.view-group`, `.fi input`, `.sw` border, range thumb, `.seg button.on`, `.rc`, `.artist-card`,
`.mfb`), three hard-code `color-mix(in oklab, white …%, transparent)` (`.nav` 82 %, `.sheet` 94 %,
`.pop` 94 %, `.mobile-tabs` 90 %), and `.filter-chip.active` / `.view-btn.active` /
`.side-footer .apply` / `.sheet-footer .apply` / `.load-more button` hard-code `color: white` on
`--ink`. A dark theme requires re-authoring every one of these, not only the token block.
`DESIGN_BRIEF.md` requires "excellent light/dark modes" and `VZ-DESIGN-001` requires "light/dark".

### a.8 Transitions and animations

No `@keyframes`, no `animation` property, no `prefers-reduced-motion` block anywhere.

| Selector | Transition |
|---|---|
| `.nav-search` (82) | `border-color .15s, box-shadow .15s` |
| `.icon-btn` (104) | `background .15s, color .15s` |
| `.filter-chip` (182) | `all .15s` |
| `.fi input[type=checkbox], .fi input[type=radio]` (295) | `all .12s` |
| `.sw` (325) | `transform .15s` (`:hover { transform: scale(1.08) }`) |
| `.card` (399) | `transform .25s, box-shadow .25s` (`:hover { translateY(-2px) }`) |
| `.card img` (404) | `transform .6s ease` (`.card:hover img { scale(1.03) }`) — **Ken-Burns zoom on every result image** |
| `.card-overlay` (413) | `opacity .2s` |
| `.c-act` (429) | `background .15s` |
| `.rc` (514) | `all .15s` (`:hover { translateY(-1px) }`) |
| `.artist-card` (536) | `box-shadow .2s, transform .2s` (`:hover { translateY(-2px) }`) |
| `.load-more button` (578) | `transform .15s` (`:hover { translateY(-1px) }`) |
| `.sheet-scrim` (606) | `opacity .2s` |
| `.sheet` (617) | `transform .3s cubic-bezier(.2,.9,.3,1.1)` — **overshoot curve** |
| `.pop` (660) | `opacity .16s, transform .18s cubic-bezier(.2,.9,.3,1.05)` — overshoot |

Two of these (the `.card img` 0.6 s scale and the two overshoot curves) are motion that
`DESIGN_BRIEF.md`'s "reduced motion" requirement and `VZ-A11Y-001` ("reduced motion") oblige to be
gated; none is.

### a.9 Z-index layers

| Layer | `z-index` | Selector |
|---|---|---|
| Sticky top nav | `50` | `.nav` (line 51) |
| Sort popover | `40` | `.pop` (line 656) |
| Mobile tab bar | `40` | `.mobile-tabs` (line 689) |
| Filter sheet scrim | `99` | `.sheet-scrim` (line 606) |
| Filter sheet | `100` | `.sheet` (line 615) |

Also stacking-relevant without `z-index`: `.pop-wrap { position: relative }`, `.card { position:
relative }`, `.card-overlay { position: absolute; inset: 0 }`, `.sw { position: relative }`,
`.sidebar { position: sticky }`.

**Defect:** the sort popover (`z-index: 40`) is *below* the sticky nav (`z-index: 50`). The toolbar
sits directly under the nav; once the page scrolls, the open popover paints behind the nav.

---

## b. Shared shell

### b.1 Top nav — `<header class="nav">` (lines 704–733)

Sticky, `top: 0`, `height: 56px`, `display: flex; align-items: center; gap: 12px; padding: 0 16px`,
background `color-mix(in oklab, white 82%, transparent)`, `backdrop-filter: saturate(180%)
blur(22px)` (+ `-webkit-` prefix), bottom border `1px solid color-mix(in oklab, var(--line) 70%,
transparent)`. At ≥900px: `padding: 0 24px`, `gap: 18px`, and flex `order` is reassigned
(brand 1, search 2, links 3, actions 4).

| # | Control | Element | Visible label / content | Evident intent |
|---|---|---|---|---|
| 1 | Brand | `<a class="brand" href="Lumen Atlas Gallery.html">` (705) | `<span class="brand-mark" aria-hidden="true">` (22×22, radius 7px, radial + linear gradient) + `<b>Lumen</b> <span>Atlas</span>` | Home / gallery |
| 2 | Search field | `<label class="nav-search" aria-label="Search">` (710) wrapping an inline `Search` SVG + `<input id="searchInput" value="mountain light">` | Pre-filled value `mountain light`; placeholder styled but no `placeholder` attribute present | Issue a query. **No `type`, no `name`, no `<form>`, no submit affordance, no Enter handler** — see §f |
| 3 | Clear query | `<button class="clear" aria-label="Clear">` (713), 22×22 circle, `X` SVG 11×11, inside the `<label>` | icon only | Empty and refocus the field |
| 4 | Discover | `<a href="Lumen Atlas Gallery.html">` (719) | `Discover` | Explore / gallery. Hidden <900px |
| 5 | Collections | `<a href="#">` (720) | `Collections` | Collections index. Hidden <900px. Dead href |
| 6 | Artists | `<a href="#">` (721) | `Artists` | People directory. Hidden <900px. Dead href |
| 7 | Notifications | `<button class="icon-btn" aria-label="Notifications">` (725) | icon only (Bell) | Notification panel. No badge, no unread count |
| 8 | Upload | `<button class="icon-btn" aria-label="Upload">` (728) | icon only (Upload) | Start an upload |
| 9 | Account | `<span class="avatar" aria-label="Your profile">MK</span>` (731) | Initials `MK`, 30×30 gradient circle | Account menu. **A `<span>`, not a button or link — not focusable, not activatable** |

Not present in the nav: sign-in / sign-out, theme toggle, language selector, admin entry, skip link.

### b.2 Mobile tab bar — `<nav class="mobile-tabs" aria-label="Mobile navigation">` (lines 1201–1218)

`position: fixed; bottom: 0; left: 0; right: 0; height: 62px`, background `color-mix(in oklab,
white 90%, transparent)`, `backdrop-filter: saturate(180%) blur(22px)`, top border `1px solid
color-mix(in oklab, var(--line) 70%, transparent)`, `justify-content: space-around`,
`padding: 0 10px env(safe-area-inset-bottom, 0)`, `z-index: 40`. Hidden at ≥900px. Tabs are
`flex-column`, icon 20×20 over a 10px/500 label, colour `--ink-3`; `.tab.active` colour `--accent`.

| # | Control | Element | Label | Intent |
|---|---|---|---|---|
| 1 | Home | `<a class="tab" href="Lumen Atlas Gallery.html" aria-label="Home">` | `Home` | Gallery |
| 2 | Search | `<button class="tab active" aria-label="Search">` | `Search` | Current page — marked with a class, **no `aria-current`** |
| 3 | Saved | `<button class="tab" aria-label="Saved">` | `Saved` | Saved / bookmarks listing. **`<button>` with no handler — dead** |
| 4 | You | `<button class="tab" aria-label="Profile">` | `You` | Own profile. **Dead** |

Every tab carries both an `aria-label` and identical visible text (except "You" / "Profile", where
the two disagree — the accessible name is "Profile" while the visible label is "You", which breaks
WCAG 2.5.3 Label in Name).

`body { padding-bottom: 72px }` (line 43) reserves room for the 62px bar, but that padding is never
removed at ≥900px where `.mobile-tabs` is `display: none` — **72px of dead space at the bottom of
every desktop viewport**.

### b.3 Footer

**There is no footer.** No `<footer>` element, no legal/attribution/licence links, no Lucide
attribution (which `DESIGN_BRIEF.md` requires be preserved), no instance branding block.

---

## c. The page, region by region

Outer container: `<div class="page">` (736) — `max-width: 1440px; margin: 0 auto; padding: 0 16px`.
**It is a `<div>`, not `<main>`; the document has no `main` landmark.**

### C1. Result header — `.result-head` (lines 738–760)

Layout: `flex-column; gap: 14px; padding: 26px 0 18px`. Inner `.rh-top` is `flex-column; gap: 10px`.

**Data shown**

| Field | Mockup value | Element |
|---|---|---|
| Query echo | `"mountain light"` inside `<em>` | `<h1 class="rh-title">Results for <em>"mountain light"</em></h1>` (740) |
| Photo count | `48,214` | `<b>` in `.rh-count` |
| Artist count | `312` | `<b>` |
| Collection count | `26` | `<b>` |
| Freshness | `refreshed moments ago` | plain text |

Full string (741): `<b>48,214</b> photos · <b>312</b> artists · <b>26</b> collections · refreshed
moments ago`. The `<em>` is styled `font-style: normal; color: var(--accent-ink)` with a
`linear-gradient(180deg, transparent 62%, color-mix(in oklab, var(--accent) 18%, transparent) 62%)`
highlighter underline, `padding: 0 6px; border-radius: 6px`.

Only three of the four result-type scopes are counted here; "Series" (9) appears only in the tab row.

### C2. Result-type / applied-filter chip row — `.filter-row` (lines 745–759)

`display: flex; align-items: center; gap: 8px; overflow-x: auto; overflow-y: hidden; padding: 4px 0
10px; scrollbar-width: none` with `::-webkit-scrollbar { display: none }` — a horizontally scrolling
strip with **no visible scrollbar and no scroll-affordance**. Declared `role="tablist"
aria-label="Result type"`.

Two chip families share the row, separated by `<span class="divider">` (1px × 22px, `--line`):

**Scope tabs** (`.filter-chip`, height 34px, radius 999px, white on `--line` border, 13px/500,
`--ink-2`; `.active` = `--ink` background, white text):

| Label | Count badge | State |
|---|---|---|
| Photos | `48.2k` | `.active` |
| Artists | `312` | — |
| Collections | `26` | — |
| Series | `9` | — |

**Applied-filter chips** (`.filter-chip.applied`: `--accent-soft` background, border
`color-mix(in oklab, var(--accent) 40%, var(--line))`, text `--accent-ink`, trailing 14×14 `.x`
circle with an 8×8 `X` glyph):

| Label | Removal |
|---|---|
| `Landscape` | `.x` circle |
| `Past year` | `.x` circle |

Neither applied chip names its facet ("Landscape" is the Orientation facet; "Past year" is the Date
taken facet) and neither corresponds to the sidebar's own state — the sidebar Orientation segment
has `Any` selected, not `Land`.

Count badge styling: `.count` = `color-mix(in oklab, var(--ink) 8%, transparent)` pill, 11px/600;
on `.active` it becomes `rgba(255,255,255,.18)` / white.

### C3. Mobile filter bar — `.mobile-filter-bar` (lines 763–772)

`display: flex; gap: 8px; padding: 8px 0 4px`; hidden at ≥1000px. Two 38px-tall `.mfb` buttons,
`flex: 1`, white on `--line`, radius 10px, 13px/500.

| Control | id | Content | Intent |
|---|---|---|---|
| Filters | `openSheet` | `ListFilter`-shaped icon + `Filters` + `<span class="count">2</span>` (accent pill, white text, 11px) | Open the bottom sheet |
| Sort | `openSortMobile` | sort icon + `Relevant` | Open a sort picker — **the id is never referenced by the script; the button is dead** |

The "2" is hard-coded and does not track the applied chips.

### C4. Toolbar — `.toolbar` (lines 775–802)

`display: flex; justify-content: space-between; gap: 12px; padding: 10px 0 18px; border-bottom: 1px
solid var(--line-2)`.

**Sort control** — `<div class="pop-wrap">` with `<button class="sort-btn" id="sortBtn"
aria-haspopup="listbox" aria-expanded="false">`: sort icon + `<span class="label">Sort by</span>` +
`<b id="sortLabel">Relevant</b>` + `ChevronDown`. Height 34px, radius 999px, white on `--line`.

**Sort popover** — `<div class="pop" id="sortPop" role="listbox">`, `position: absolute; top:
calc(100% + 8px); right: 0; min-width: 220px`, background `color-mix(in oklab, white 94%,
transparent)` + `blur(28px)`, radius 14px, `z-index: 40`, `padding: 5px`. Closed state:
`opacity: 0; transform: translateY(-4px) scale(.98); pointer-events: none`.

Five `<button class="pop-item" data-v="…">` options, each with a leading 14px check slot
(`opacity: 0` unless `.sel`):

| `data-v` | Label | Secondary |
|---|---|---|
| `Relevant` | Relevant | `<small>Recommended</small>` |
| `Recent` | Recent | — |
| `Interesting` | Interesting | — |
| `Most loved` | Most loved | — |
| `Most viewed` | Most viewed | — |

**View switcher** — `<div class="view-group" role="tablist" aria-label="View">`, white pill,
`padding: 3px`, three 34×28 `.view-btn`:

| `aria-label` | Glyph | State |
|---|---|---|
| `Grid` | 4 equal squares | — |
| `Masonry` | 4 uneven rects | `.active` (`--ink` bg, white) |
| `Large` | 2 full-width rects | — |

The view switcher has no JS handler at all — clicking it does nothing, not even the class toggle.

### C5. Results shell — `.results-shell` (lines 805–1177)

`display: grid; grid-template-columns: 1fr; gap: 24px; padding: 20px 0 40px`. At ≥1000px:
`grid-template-columns: 248px 1fr; gap: 36px`.

### C6. Filter sidebar — `<aside class="sidebar" id="sidebar">` (lines 808–891)

`display: none` below 1000px. Six `.filter-section` blocks (`padding: 6px 0 14px`; each after the
first adds `border-top: 1px solid var(--line-2); padding-top: 16px`), each headed by a
`<p class="filter-label">` (11px/600/`.14em`/uppercase/`--ink-3`) — **a `<p>`, not a heading, and
not programmatically associated with its group** (no `<fieldset>`/`<legend>`, no `role="group"` +
`aria-labelledby`).

Row pattern `.fi` = `<label>` containing a custom-styled `<input>` + `<span class="label">` +
optional `<span class="ct">` count. `display: flex; gap: 10px; padding: 6px 8px; border-radius:
8px; font-size: 13.5px`. Inputs use `appearance: none`, 16×16, radius 5px (checkbox) / 50 %
(radio), `1.5px solid var(--line)` border, checked fill `--accent` with a CSS-drawn white tick
(`::after`, 9×5, two 2px borders, `rotate(-45deg)`).

| § | `filter-label` | Control type | Options (label → count) | Preset state |
|---|---|---|---|---|
| 1 | `Content` | checkboxes | `Photos` → 48.2k; `Videos` → 1.1k; `Editorial series` → 9; `Public domain` → 3.4k | `Photos` checked |
| 2 | `Color palette` | 12 `<button class="sw">` in `grid-template-columns: repeat(6, 1fr); gap: 6px`, each `aspect-ratio: 1`, circular | `Midnight` `oklch(0.3 0.06 250)`; `Azure` `oklch(0.62 0.15 250)`; `Sky` `oklch(0.85 0.10 230)`; `Sunset` `oklch(0.55 0.14 25)`; `Gold` `oklch(0.78 0.14 80)`; `Ivory` `oklch(0.92 0.04 90)`; `Forest` `oklch(0.55 0.13 145)`; `Sage` `oklch(0.80 0.07 150)`; `Umber` `oklch(0.42 0.07 30)`; `Ink` `oklch(0.22 0.01 260)`; `Paper` `oklch(0.95 0.008 260)`; `Any` (135° gradient `oklch(0.6 0.18 30)`→`oklch(0.6 0.18 300)`) | `Midnight` and `Sunset` have `.on` |
| 3 | `Orientation` | `.seg` segmented, `grid-template-columns: repeat(4, 1fr); gap: 2px`, `--bg-tint` track, radius 10px, `padding: 3px`; buttons 11px/500 with a CSS-drawn rectangle `glyph` | `Any` (12×12 `sq`); `Land` (16×12); `Port` (9×14 `port`); `Pano` (20×8 `pano`) | `Any` has `.on` |
| 4 | `Minimum size` | `<input type="range" min="0" max="100" value="65">`, 4px track, 18px white thumb | end labels `Any` / `Large · 4K+` | value 65 |
| 5 | `Date taken` | radios, `name="date"` | `Anytime`; `Past week`; `Past month`; `Past year`; `Custom range…` | `Past year` checked |
| 6 | `License` | checkboxes | `All licenses` (no count); `Creative Commons` → 12.3k; `Commercial use` → 4.8k; `No derivatives` (no count) | `Creative Commons` checked |
| 7 | `Camera` | checkboxes | `Leica` → 912; `Fujifilm` → 2.1k; `Hasselblad` → 404; `Analog / Film` → 1.4k | none |

Sidebar footer `.side-footer` (887–890): `border-top: 1px solid var(--line-2); padding-top: 10px;
display: flex; gap: 6px`; two `flex: 1`, 34px, radius 10px, 13px/500 buttons — `Reset`
(`--bg-tint` / `--ink-2`) then `Apply` (`--ink` / white). Visual order is Reset-then-Apply while the
sheet's footer uses the same order; neither has a handler beyond closing the sheet.

Sticky behaviour at ≥1000px: `top: 70px`, `max-height: calc(100vh - 84px)`, own scroll area.

### C7. Masonry results — `.masonry#masonry` (lines 897–1092)

CSS **multi-column** masonry (`column-count` / `column-gap`), not CSS grid: 1 column <520px, 2 at
≥520px (gap 14px), 3 at ≥780px, gap 16px at ≥1200px, 4 at ≥1440px. Cards use `break-inside: avoid;
margin: 0 0 14px`.

Column layout means results flow **top-to-bottom within a column, then to the next column** — DOM
order and visual reading order diverge, and appending results on "Load more" reflows every column.

`.card` = `<a class="card" href="#">`: `position: relative; border-radius: 16px; overflow: hidden;
background: var(--line-2)` (the placeholder colour while the image loads), `box-shadow:
var(--shadow-sm)`. `.card img { width: 100%; height: auto }` with `loading="lazy"`.

**19 cards are present**, although the source comment at line 898 says "24 cards" and the pager
says "Showing 1–24". Card 1 carries a dead `style="grid-row: span 20"` (meaningless in a
multi-column container) and `style="aspect-ratio: 4/5;"` on its `<img>` — with the default
`object-fit: fill` that **distorts** the image rather than cropping it.

`.card-overlay` = `position: absolute; inset: 0; opacity: 0`, revealed by `.card:hover` **or**
`.card:focus-within`; `background: linear-gradient(180deg, rgba(0,0,0,.28) 0%, transparent 30%,
transparent 60%, rgba(0,0,0,.65) 100%)`; `pointer-events: none` with `> * { pointer-events: auto }`.

**Fields per card**

| Field | Element / attribute | Present on |
|---|---|---|
| Permalink | `<a class="card" href="#">` | all 19 (all `#`) |
| Image URL | `<img src="https://images.unsplash.com/…?auto=format&fit=crop&w=900&q=80">` | all 19 |
| Alt text | `alt="…"` | cards 1–3 only (`Snowy peaks at dawn`, `Lake reflection`, `Morning ridge`); **16 cards have `alt=""`** |
| Intrinsic aspect | not transmitted (only card 1 has an inline `aspect-ratio`) | — |
| Badge | `<span class="card-badge">` (white 85 % pill, blur, `--ink`, 11px/600) or `.card-badge.video` (`rgba(0,0,0,.55)`, white) | `Featured` + Star (card 1); `1:42` + Play (card 3, `.video`); `RAW` (card 7); `4K` (card 14); `CC-BY` (card 19) |
| Save action | `<button class="c-act" aria-label="Save">` + Bookmark icon | 17 cards |
| Love action | `<button class="c-act" aria-label="Love">` + Heart icon (filled when `.on`) | cards 1, 2, 11; `.on` on cards 1 and 11 |
| Title | `<h3 class="card-title">` | all 19 |
| Author avatar | `<span class="av">` with `background-image: url(…)` or a flat `oklch(...)` | all 19 |
| Author name | `<span class="name">` | all 19 |
| Favorite count | `.card-stats span` with Heart icon | cards 1 (`4.2k`), 2 (`1.8k`) |
| View count | `.card-stats span` with Eye icon | card 1 (`38k`) |

Card titles in DOM order: `Cascades, Blue Hour` · `Lake Louise, First Light` · `Alpenglow Timelapse`
· `Dolomites Summit Glow` · `Grandeur` · `Valley of Mist` · `Above the Clouds` · `Golden Ridge` ·
`Silent Passage` · `Torres del Paine` · `Ridge Study No. 4` · *[refine strip]* · `Quiet Morning` ·
`Fjord Morning` · `Trail to Nowhere` · `Last Snow` · `Westerly Wind` · `Reflections, Plateau` ·
`Pine and Peak` · `North Face, Early`.

Author names: `Marie Okafor`, `Rhea Sandoval`, `Hana Mori`, `P. Lindqvist`, `K. Abellán`,
`L. Yamamoto`, `T. Nakano`, `S. Kowalski`, `M. Becker`, `E. Vogel`, `A. Rivera`, `J. Saaristo`,
`I. Strand`, `C. Beaumont`, `D. Ahmadi`, `N. Laurent`, `O. Petrov`, `R. Vasquez`, `H. Brun`.

The badge slot is **semantically overloaded**: it carries an editorial flag (Featured), a media
duration (1:42), a source format (RAW), a resolution class (4K) and a licence (CC-BY) with one
visual treatment and no accessible distinction.

`.c-act` buttons: 30×30 circle, `rgba(255,255,255,.22)` + `blur(12px)`, `0.5px solid
rgba(255,255,255,.25)`, white icon 14×14; `.on` = white background, icon `oklch(0.55 0.18 25)`.
**They are `<button>`s nested inside an `<a>`** — invalid HTML and an activation conflict.

### C8. "Refine your search" strip — `.strip` inline in the masonry (lines 1033–1050)

Placed as the 12th masonry child, so at 3–4 columns it lands mid-column, not full width. Styling:
`--bg-tint` background, radius 22px, `1px solid var(--line-2)`, `padding: 18px 18px 20px`,
`margin: 26px 0 18px` overridden inline to `margin-bottom: 14px`, plus inline
`break-inside: avoid`.

- `<h2 class="strip-title">Refine your search</h2>`
- `<p class="strip-sub">Common ways photographers narrow results for <em>mountain light</em></p>`
- `.related-chips` — `flex-wrap: wrap; gap: 8px`, eight `<a class="rc" href="#">` pills (8px 14px,
  radius 999px, white on `--line`, 13px/500):
  `alpenglow` (with a literal `›` character in `<span class="arr">`, the only chip that has one),
  `golden hour ridge`, `low cloud mountain`, `dolomites sunrise`, `blue hour cascades`,
  `fog layers`, `storm light`, `moonlight peaks`.

No "see all" link; no indication whether these are query rewrites, tags, or both.

### C9. "Artists who shoot this" strip — `<section class="strip">` (lines 1095–1165)

`aria-label="Photographers matching"` (which disagrees with the visible `<h2>`).

- `<h2 class="strip-title">Artists who shoot this</h2>`
- `<p class="strip-sub">Photographers whose work matches <em>mountain light</em></p>`
- `<a class="strip-more" href="#">See all 312 <ArrowRight/></a>` — 13px, `--accent`

`.artist-scroll`: `display: flex; gap: 14px; overflow-x: auto; padding: 4px 2px 8px;
scrollbar-width: none` + hidden WebKit scrollbar. Four `.artist-card` at `flex: 0 0 auto; width:
200px`, white, radius 16px, `1px solid var(--line-2)`, `padding: 14px`.

**Fields per artist card**

| Field | Element | Values |
|---|---|---|
| Avatar | `.artist-av`, 40×40 circle, `background-image` (card 4 uses a gradient instead) | 4 |
| Display name | `.artist-name` (14px/600, ellipsis) | `Marie Okafor`, `Rhea Sandoval`, `Hana Mori`, `Johan Saaristo` |
| Handle · photo count | `.artist-handle` (12px, `--ink-3`, ellipsis) | `@mokafor · 1.2k photos`, `@rhea.light · 844 photos`, `@hanamori · 612 photos`, `@saaristo · 1.5k photos` |
| Preview thumbnails | `.artist-thumbs` — `grid-template-columns: repeat(3, 1fr); gap: 3px; border-radius: 10px; overflow: hidden`, each child `aspect-ratio: 1; background-size: cover` (**square crop**) | 3 per card |
| Follow | `<button class="artist-follow">Follow</button>` — 30px, radius 999px, `--bg-tint`, 12px/600 | 4 |

**The artist card itself is a `<div>`, not a link.** The avatar, name, handle and all three
thumbnails are inert — the only reachable control is the Follow button. No follower count, no
"following" state, no profile route.

### C10. Pagination — `.load-more` (lines 1168–1174)

`text-align: center; padding: 30px 0 10px`.

- `<button>Load more results <ArrowDown/></button>` — 44px, radius 999px, `--ink` on white text,
  14px/600, `:hover { translateY(-1px) }`. No handler.
- `<div class="pager-hint">Showing 1–24 of 48,214 · Page 1 of 2,009</div>` — 12px, `--ink-3`.

So the mockup describes **a hybrid**: a "Load more" button (append semantics) alongside a page
counter (classic-pagination semantics), with no numbered pager, no prev/next, no infinite-scroll
sentinel and no `aria-live` announcement of appended results. 24 items/page × 2,009 pages is
internally consistent with 48,214 but **19 cards are actually rendered**.

### C11. Mobile filter sheet — `.sheet-scrim` + `.sheet` (lines 1182–1198)

Scrim: `position: fixed; inset: 0; background: rgba(17,22,40,.3); backdrop-filter: blur(6px);
z-index: 99; opacity: 0; pointer-events: none`.

Sheet: `position: fixed; left/right: 0; bottom: 0; max-height: 88vh`, background
`color-mix(in oklab, white 94%, transparent)` + `saturate(180%) blur(30px)`, `border-radius: 22px
22px 0 0`, `z-index: 100`, `transform: translateY(100%)` when closed,
`role="dialog" aria-modal="true" aria-labelledby="sheetTitle"`.

| Part | Content |
|---|---|
| `.sheet-grab` | 40×5 rounded bar — a **drag affordance with no drag behaviour** |
| `.sheet-head` | `<h2 id="sheetTitle">Filters</h2>` + `<button class="sheet-close" id="closeSheet" aria-label="Close">` (30×30, `X`) |
| `.sheet-body#sheetBody` | Empty in source; populated at open time by cloning the sidebar's `.filter-section` nodes (see §d) |
| `.sheet-footer` | `<button class="reset">Reset</button>` + `<button class="apply" id="applySheet">Show 48,214 results</button>` — two `flex: 1`, 44px, radius 12px, 600 weight |

The `Show 48,214 results` label is a hard-coded string; it does not recompute as filters change.

---

## d. What the inline script does (lines 1220–1296)

Five IIFEs/handlers, ~75 lines, **no data, no fetch, no state model**. Every effect is a CSS class
toggle or a text swap. There is no mock data object, no array of results, no template — the 19
cards and all counts are hand-written HTML literals.

**1. Sort popover** (1222–1235)
`sortBtn` click `stopPropagation()`s and toggles `.open` on `#sortPop`, mirroring it into
`aria-expanded`. A document-level click listener closes it when the click is outside both nodes.
Each `.pop-item` click clears `.sel` from all items, sets it on the clicked one, copies
`it.dataset.v` into `#sortLabel` textContent, and closes. **No Escape handler, no arrow-key
navigation, no focus move into the list, no focus return, no result change.**

**2. Colour swatches** (1238)
`document.querySelectorAll('#swatches .sw')` → each click toggles `.on`. Pure visual multi-select.

**3. Orientation segment** (1241–1248)
Within `#seg`, a click clears `.on` from all four buttons and sets it on the clicked one. Single-select.

**4. Result-type chips** (1251–1256)
`.filter-row .filter-chip:not(.applied)` — a click clears `.active` from all non-applied chips and
sets it on the clicked one. **The result grid never changes**: switching to "Artists" or
"Collections" still shows the same 19 photo cards.

**5. Applied-chip removal** (1258)
`.filter-chip.applied` → click calls `c.remove()`, deleting the node. The whole chip is the button,
so clicking the label removes the filter exactly as the `.x` does; the `.x` is decorative. There is
no undo and the sidebar/sheet state is not updated.

**6. Mobile sheet** (1261–1289)
`openSheet` click calls `populate()` then `setOpen(true)`. `populate()` empties `#sheetBody`, then
for every `.filter-section` in `#sidebar` appends `s.cloneNode(true)`, then re-binds swatch and
segment handlers on the clones. `setOpen(o)` toggles `.open` on sheet and scrim and sets
`document.body.style.overflow = o ? 'hidden' : ''`. Close, scrim click and Apply all call
`setOpen(false)`. **Apply performs no query.**

Defects this creates:
- `cloneNode(true)` duplicates `id="swatches"` and `id="seg"` into the document — **duplicate IDs**;
  `document.getElementById('seg')` and `#swatches` become ambiguous, and because the `#seg` handler
  was bound at load, the original sidebar segment still works only by that stale binding.
- Cloned radios keep `name="date"`, joining the **same radio group** as the sidebar's — selecting a
  date in the sheet silently deselects it in the sidebar.
- `populate()` re-clones on every open, so sheet state is discarded each time it is closed.
- No Escape handler, no focus trap, no focus move into the dialog, no focus return, no `inert`/
  `hidden` when closed (the closed sheet's contents remain in the tab order off-screen).

**7. Clear search** (1292–1295)
`.nav-search .clear` click sets `#searchInput.value = ''` and focuses the input.

**Never wired:** `#openSortMobile`, `.view-btn` (all three), `.load-more button`, `.side-footer`
Reset/Apply, `.sheet-footer .reset`, `.c-act` Save/Love, `.artist-follow`, `.rc` related chips,
`.strip-more`, `input[type=range]`, `.fi` checkboxes/radios (no change listener), the search input
(no `keydown`/submit), and all nine nav/tab-bar controls.

**Mock-data shape:** none. The page is static HTML; the closest thing to a data contract is the
per-card field set in §C7 and the per-artist set in §C9, which is what §i reconstructs.

---

## e. States

### e.1 Present in the mockup

| State | Where | How |
|---|---|---|
| Hover | `.icon-btn`, `.filter-chip`, `.fi`, `.sw`, `.card`, `.card img`, `.c-act`, `.rc`, `.artist-card`, `.artist-follow`, `.pop-item`, `.load-more button` | background / transform / shadow / border colour |
| Focus (partial) | `.nav-search:focus-within` only | accent border + `0 0 0 3px` accent-22 % ring |
| Focus-revealed | `.card:focus-within .card-overlay { opacity: 1 }` | overlay appears when a nested control is focused |
| Selected (scope) | `.filter-chip.active` | `--ink` fill, white text |
| Selected (facet) | `.fi input:checked`, `.sw.on`, `.seg button.on`, `.view-btn.active`, `.pop-item.sel`, `.mobile-tabs .tab.active` | accent fill / white pill / ink fill / check opacity / accent colour |
| Applied filter | `.filter-chip.applied` | accent-soft chip with removal affordance |
| Toggled-on action | `.c-act.on` | white circle, red-orange icon |
| Open (overlay) | `.pop.open`, `.sheet.open`, `.sheet-scrim.open` | opacity/transform |
| Image placeholder | `.card { background: var(--line-2) }` behind a lazy image | a flat grey block, not a skeleton |

### e.2 Absent — and required

`DESIGN_BRIEF.md` requires documenting "loading/empty/error/success/disabled states, light/dark
modes, 200% zoom, reduced motion, keyboard navigation, and responsive behavior", and
`VZ-A11Y-001` adds visible focus, focus trap/return, labels on icon-only controls and `aria-live`.

| Missing state | Consequence for the implementer |
|---|---|
| **Loading / skeleton** | No result-grid skeleton, no card placeholder ratio, no spinner on "Load more", no pending state on Apply |
| **No-results** | `.empty-note` exists in CSS (line 676) but appears in no markup. No zero-result illustration, no "did you mean", no suggestion to relax filters |
| **Empty (no query)** | Undefined — the page presumes a query is present |
| **Error** | No search-service-unavailable state. `VZ-SEARCH-004` explicitly requires a visible degraded path when vizra-search is down and core falls back to SQL |
| **Success / confirmation** | Favourite and Follow have an on-state but no optimistic/settled distinction, no failure revert, no toast |
| **Disabled** | No disabled treatment on any control (Apply with no changes, Load more at the last page, Follow while a request is in flight) |
| **Pressed / busy** | No `:active`, no `aria-busy`, no `aria-pressed` anywhere |
| **Focus-visible** | No `:focus-visible` rule in the file; see §f |
| **Dark mode** | §a.7 |
| **Reduced motion** | §a.8 |
| **Blurred / safety-gated result** | `VZ-NSFW-001` requires blur and a viewer-side safety filter in listings and search; nothing in the mockup |
| **Private / unlisted marker** | `VZ-PRIVACY-001/002` — no visibility indicator on a card |
| **Authenticated vs anonymous** | The page shows a signed-in avatar, Save/Love and Follow with no anonymous variant; `VZ-SEARCH-001` is permission-aware and the page must render for logged-out visitors |

---

## f. Accessibility observations

### f.1 Non-button click targets and interactive-nesting

| Issue | Location |
|---|---|
| `<button class="c-act">` nested inside `<a class="card">` | every card (17 Save + 3 Love buttons). Invalid HTML; activation and keyboard semantics are undefined |
| `<button class="clear">` nested inside `<label class="nav-search">` | line 713. Clicking the button also triggers the label's focus behaviour |
| `<span class="avatar" aria-label="Your profile">` | line 731. A non-interactive span presented as the account control: not focusable, not activatable, and `aria-label` on a role-less `span` is ignored by most assistive technology |
| `.artist-card` is a `<div>` | lines 1104, 1119, 1134, 1149. Avatar, name, handle and three thumbnails look tappable and are inert |
| `.artist-thumbs div` | 12 background-image divs — no `img`, no alt, no link |
| `.sheet-grab` | a drag handle with no drag |
| `.filter-chip.applied` whole chip removes the filter | the inner `.x` looks like the removal target but is a decorative `<span>` |
| `<a href="#">` on all 19 cards and 8 related chips, 2 nav links and the "See all" link | dead links; `DESIGN_BRIEF.md` explicitly rejects "dead links, no-op handlers" |

### f.2 Missing names, roles and states

- **The search input has no accessible name.** `<input id="searchInput" value="mountain light">` has
  no `type`, `name`, `placeholder`, `aria-label` or associated label *text*. The wrapping
  `<label class="nav-search" aria-label="Search">` labels *itself*, not the input — a `label`'s
  accessible name does not propagate to its control, and the label's text content is empty.
- **No `<form>` and no submit.** There is no way to run a search by keyboard or by any control.
- `role="tablist"` on `.filter-row` (745) and `.view-group` (791) with **children that have no
  `role="tab"`**, no `aria-selected`, no `aria-controls`, no roving `tabindex`, and no
  `role="tabpanel"` anywhere. Invalid ARIA that is worse than no ARIA.
- `role="listbox"` on `.pop` (782) with `<button>` children that have **no `role="option"`** and no
  `aria-selected`; `aria-haspopup="listbox"` with no `aria-controls` / `aria-activedescendant`.
- **No `aria-pressed`** on any toggle: `.sw` swatches, `.seg` orientation, `.view-btn`,
  `.filter-chip`, `.c-act` Save/Love, `.artist-follow`. `DESIGN_BRIEF.md`: "Use stable toggle labels
  plus programmatic pressed state where suitable."
- **No `aria-current`** on `.mobile-tabs .tab.active`.
- `<p class="filter-label">` used as a group heading with no `<fieldset>/<legend>` or
  `role="group" aria-labelledby`.
- `<input type="range">` (851) has **no label, no `aria-label`, no `aria-valuetext`**, and its
  displayed fill is a hard-coded `linear-gradient(... 65% ...)` that never tracks the value.
- `alt=""` on 16 of 19 result images (§C7); the card's accessible name then falls back to the
  overlay text, which is visually hidden by `opacity: 0` but still in the accessibility tree.
- "You" tab: visible text `You`, `aria-label="Profile"` — WCAG 2.5.3 Label in Name failure.
  `aria-label="Photographers matching"` on the section headed "Artists who shoot this" is the same
  class of mismatch.
- No `aria-live` region for result counts, applied-filter changes, or appended results —
  `VZ-A11Y-001` requires `aria-live` for progress.
- No skip link; no `<main>`; the only landmarks are `header`, `nav` ×2, `aside`, `section` ×1.
- All 52 inline `<svg>` elements lack `aria-hidden="true"`. `DESIGN_BRIEF.md`: "keep its redundant
  decorative SVG hidden from assistive technology."

### f.3 Focus visibility

**No `:focus-visible` rule exists in the file.** Worse, three rules actively remove focus indication:

- `.pop-item { all: unset; }` (line 664) — resets `outline` along with everything else, so the five
  sort options have **no focus ring at all**.
- `input[type=range] { outline: none; }` (line 361).
- `.fi input[type=checkbox], .fi input[type=radio] { appearance: none; -webkit-appearance: none; }`
  (287–296) with no replacement focus style — 12 custom checkboxes and 5 radios have no visible
  focus.
- `* { -webkit-tap-highlight-color: transparent; }` (line 32) removes the touch activation hint.

Everything else relies on the UA default ring, which on a 999px pill against `--bg` is low-contrast
and is not designed. `VZ-A11Y-001` requires "visible focus".

### f.4 Contrast — computed

sRGB values and WCAG 2.x contrast ratios computed from the OKLCH token declarations (OKLab → linear
sRGB → gamma-encode → relative luminance):

| Token | sRGB hex | Relative luminance |
|---|---|---|
| `--bg` | `#f9fafc` | 0.9559 |
| `--bg-tint` | `#f0f2f4` | 0.8851 |
| `--ink` | `#0e1218` | 0.0058 |
| `--ink-2` | `#3f4349` | 0.0549 |
| `--ink-3` | `#71757a` | 0.1757 |
| `--line` | `#dcdee2` | 0.7291 |
| `--line-2` | `#e9ebef` | 0.8307 |
| `--accent` | `#1779e1` | 0.1917 |
| `--accent-ink` | `#00358e` | 0.0450 |
| `--accent-soft` | `#ddf0ff` | 0.8520 |

| Pair | Ratio | AA verdict |
|---|---|---|
| `--ink` on `--bg` | **18.02:1** | pass |
| `--ink` on white | **18.81:1** | pass |
| `--ink-2` on `--bg` | **9.59:1** | pass |
| `--ink-2` on white | **10.01:1** | pass |
| **`--ink-3` on `--bg`** | **4.46:1** | **FAIL** (needs 4.5:1) |
| **`--ink-3` on `--bg-tint`** | **4.14:1** | **FAIL** |
| `--ink-3` on white | 4.65:1 | pass, by 0.15 |
| **`--ink-3` on `--accent-soft`** | **4.00:1** | **FAIL** |
| **`--accent` on white** | **4.34:1** | **FAIL** for text |
| **`--accent` on `--bg`** | **4.16:1** | **FAIL** for text |
| **white on `--accent`** | **4.34:1** | **FAIL** for text |
| `--accent-ink` on white | 11.06:1 | pass |
| `--accent-ink` on `--accent-soft` | 9.50:1 | pass |
| white on `--ink` | 18.81:1 | pass |
| **`--line` on white** | **1.35:1** | **FAIL** (1.4.11 needs 3:1) |
| **`--line` on `--bg`** | **1.29:1** | **FAIL** |
| **`--line-2` on white** | **1.19:1** | **FAIL** |

Concretely:

1. **`--ink-3` on the page background fails at 4.46:1** and it is the colour of `.rh-count` (the
   result counts), `.filter-label` (11px uppercase section headings), `.fi .ct` (facet counts),
   `.strip-sub`, `.artist-handle`, `.pager-hint`, `.range-row`, `.pop-item small`, `.sort-btn
   .label`, `.view-btn` (unselected), `.mobile-tabs .tab` (10px) and the input placeholder. On
   `--bg-tint` (inside `.strip`) it drops to 4.14:1.
2. **`--line` at 1.29–1.35:1 fails 1.4.11 Non-text Contrast (3:1) everywhere it carries meaning** —
   the unchecked checkbox and radio borders (`1.5px solid var(--line)`, the *only* indication of the
   unchecked state), the `.nav-search` field boundary, `.filter-chip`, `.sort-btn`, `.view-group`,
   `.rc`, `.mfb` and `.artist-follow` borders, and the `.sw` swatch ring.
3. **`--accent` on white/`--bg` fails 4.5:1 for text** and is used for `.strip-more` ("See all 312",
   13px) and `.mobile-tabs .tab.active` (10px). It also fails as the `.mfb .count` background with
   white 11px text (4.34:1).
4. The accent focus ring is `color-mix(in oklab, var(--accent) 22%, transparent)` against white —
   roughly `#d0e4f9`, about **1.28:1 against white**. Not a perceivable focus indicator.
5. All card text (`.card-title`, `.card-author .name`, `.card-stats`, badges) is white over a
   photograph with a `rgba(0,0,0,.28)→transparent→transparent→rgba(0,0,0,.65)` scrim and a
   `text-shadow`. Contrast is **unmeasurable and image-dependent**; the top-of-card `.card-badge`
   sits in a 0.28-alpha region and a bright sky will fail. `VZ-A11Y-001` requires "contrast ≥ 4.5:1
   text / 3:1 UI **over real backings**".

### f.5 Keyboard traps, order and reduced motion

- **No trap in the literal sense** (the sheet has no trap at all), but the inverse defect exists:
  the closed `.sheet` is only `transform: translateY(100%)`, never `hidden`/`inert`/`display:none`,
  so its close button, Reset and Apply are in the tab order off-screen on every viewport, including
  desktop where the sheet is unreachable by design.
- The sort popover is `pointer-events: none` when closed but its five buttons remain focusable
  (`opacity: 0` does not remove focusability), so Tab passes through five invisible options.
- The `.card-overlay` reveals on `:focus-within`, which is the one genuinely good keyboard decision
  in the file — but the Save/Love buttons inside an `<a>` still produce ambiguous activation.
- Multi-column masonry makes **tab order follow DOM order while the eye follows columns**.
- `.filter-row`, `.artist-scroll` and `.sidebar` are horizontal/vertical scroll containers with
  `scrollbar-width: none` and no keyboard scroll affordance and no `tabindex="0"` — content can be
  unreachable by keyboard when it overflows.
- **No `prefers-reduced-motion` block.** The 0.6 s image scale on hover, two overshoot cubic-beziers,
  and six translate-on-hover effects all run regardless.
- 200 % zoom / 320px reflow is untested by the file: `.artist-card` is a fixed `width: 200px` and
  `.swatches` is a fixed `repeat(6, 1fr)`; the 248px sidebar is simply hidden below 1000px rather
  than reflowed, so at 200 % zoom on a 1440px screen (effective 720px) **the entire desktop filter
  sidebar disappears** and only the mobile sheet route remains.

---

## g. Conflicts with `docs/DESIGN_BRIEF.md` and `AGENTS.md`

| # | Conflict | Evidence in the mockup | Rule |
|---|---|---|---|
| G1 | **Font stack names SF Pro** | `--font-sans` and `--font-display` both list `"SF Pro Text"` / `"SF Pro Display"` (lines 27–28) | `DESIGN_BRIEF.md`: "Use a system font stack or properly licensed web font. Do not distribute Apple fonts, logos, or SF Symbols by assumption." Naming the faces in a stack is not distribution, but the two-token split exists *only* to reach SF Pro Display; on non-Apple platforms both tokens collapse to the same fallback and the display/text distinction vanishes. Resolve to a licensed display face or drop `--font-display`. |
| G2 | **52 hand-inlined SVG icons instead of the typed Lucide registry** | every `<svg viewBox="0 0 24 24">` in the file, plus one `data:image/svg+xml` check in `.sw.on::after` (line 333) and one literal `›` character in `.rc .arr` (line 1041) — **three** icon mechanisms | `DESIGN_BRIEF.md`: "Use one consistent licensed icon family, preferably Lucide… named, statically imported SVG components behind a typed semantic registry. Verify actual exports in the pinned package; do not invent icon names." `VZ-DESIGN-001` requires "an icon registry test that every name exists in the pinned package". See §g.1 for the mapping. |
| G3 | **Hotlinked Unsplash images** | 37 `https://images.unsplash.com/…` URLs (19 card images, 4 card avatars, 3 artist avatars, 12 artist thumbnails) | `AGENTS.md`: "no… mock data in production paths"; `README.md` standing note 2: "not assets to ship, bundle, cache or use as fixtures". Also a third-party hotlink on a self-hosted page is a privacy leak (every visitor's IP reaches Unsplash) and a CSP problem. |
| G4 | **Destructive cropping by default** | every image URL carries `&fit=crop&w=900`; `.artist-thumbs div { aspect-ratio: 1; background-size: cover }`; card 1's `<img style="aspect-ratio: 4/5">` with default `object-fit: fill` **distorts** rather than crops | `DESIGN_BRIEF.md`: "Preserve the image's aspect ratio; do not default to destructive cropping." The masonry itself is correct here (`height: auto`); the crop is in the URLs, the artist thumbnails and card 1's inline override. |
| G5 | **Fake metrics** | `48,214` photos, `312` artists, `26` collections, `Page 1 of 2,009`, facet counts `48.2k / 1.1k / 9 / 3.4k / 12.3k / 4.8k / 912 / 2.1k / 404 / 1.4k`, per-card `4.2k` loves and `38k` views, `1.2k / 844 / 612 / 1.5k photos` per artist, `Show 48,214 results`, `refreshed moments ago` — **all hard-coded, none derived, and 19 cards are rendered against a claimed 24-per-page** | `DESIGN_BRIEF.md`: "Reject… fake metrics." `AGENTS.md`: "Do not fabricate outputs." Every count must be a permission-aware server value (`VZ-SEARCH-001`: "authorization inside the query for results, **counts, facets** and suggestions"). |
| G6 | **`RAW` badge** | card 7 (line 1009) | `VZ-MEDIA-002`: "**RAW is declined** unless the owner adds it." The badge advertises a capability the ledger explicitly excludes. |
| G7 | **No dark mode** | §a.7 | `DESIGN_BRIEF.md`: "excellent light/dark modes"; `VZ-DESIGN-001`: "light/dark". |
| G8 | **No reduced-motion handling** | §a.8 | `DESIGN_BRIEF.md`; `VZ-A11Y-001`. |
| G9 | **Dead controls and dead links** | 19 card hrefs + 8 related chips + 2 nav links + "See all" = `href="#"`; `#openSortMobile`, all 3 view buttons, Load more, both Apply and both Reset, 20 Save/Love buttons, 4 Follow buttons, the range input and 17 checkboxes/radios have no handler | `DESIGN_BRIEF.md`: "Reject dead links, no-op handlers, decorative substitutes for controls." |
| G10 | **Missing mobile actions** | `.card-overlay` is `opacity: 0` and only revealed by `:hover` / `:focus-within` — on touch there is no hover, so Save, Love, the title, the author and all stats are **invisible and unreachable on phones** | `DESIGN_BRIEF.md`: "Reject… missing mobile actions"; `VZ-RESPONSIVE-001`: "viewer actions reachable on phones". |
| G11 | **Favourite and "Save" are visually and semantically near-identical** | two 30×30 white-glass circles side by side, `aria-label="Save"` (Bookmark) and `aria-label="Love"` (Heart), with no visible labels and no tooltips | `DESIGN_BRIEF.md`: "Favorites and ratings must not be visually or semantically indistinguishable" — the same hazard, and worse here because "Save" maps to no ledger entry at all (§h). |
| G12 | **Hover-only meaning** | the entire card metadata layer (title, author, counts, badges are always visible; actions are not) plus the `.filter-chip.applied` `.x` | `DESIGN_BRIEF.md`: "Do not rely on hover-only tooltips, color alone, or an unlabeled clickable div." |
| G13 | **"Artists" vocabulary** | nav link `Artists`, tab `Artists`, `Artists who shoot this`, `.artist-card` | Vizra's ledger vocabulary is *members*, *photographers*, *users* (`VZ-PROFILE-001`, `VZ-FOLLOW-001`). A vocabulary decision is an owner call, not an implementer's; flag it rather than adopting it. |
| G14 | **"Lumen Atlas" brand and gradient mark** | `.brand-mark` (lines 65–71), `<b>Lumen</b> <span>Atlas</span>` | `README.md` standing note 3; the Vizra brand mark is "an original, separately reviewed asset". |
| G15 | **`.page` is not `<main>`; no skip link; no footer** | line 736 | `VZ-A11Y-001` (WCAG 2.2 AA); `DESIGN_BRIEF.md` icon attribution must live somewhere. |
| G16 | **Invalid ARIA (`tablist` without `tab`, `listbox` without `option`)** | §f.2 | `VZ-A11Y-001`. |
| G17 | **No token discipline** | 4 of 19 tokens unused; `white` literal 14×; 15 radii vs 4 tokens; 9 shadow recipes vs 2 tokens; 15 font sizes incl. 11.5/12.5/13.5px; spacing on no grid | `VZ-DESIGN-001`: "approved tokens (spacing/type/radii/shadows/semantic colors)". |
| G18 | **Backdrop blur over photography** | `.nav` blur(22px), `.mobile-tabs` blur(22px), `.sheet` blur(30px), `.pop` blur(28px), `.c-act` blur(12px), `.card-badge` blur(10px), `.sheet-scrim` blur(6px) | `DESIGN_BRIEF.md`: "Avoid… glass effects that reduce photo or text legibility." The `.c-act` and `.card-badge` glass sits directly on the photograph. |
| G19 | **Sort popover below the sticky nav** | `.pop` `z-index: 40` vs `.nav` `z-index: 50` | rendering defect (§a.9). |
| G20 | **Duplicate IDs and shared radio-group names injected at runtime** | `cloneNode(true)` of `#swatches`, `#seg` and `name="date"` (line 1278) | invalid DOM; `VZ-A11Y-001`. |
| G21 | **72px of dead space on desktop** | `body { padding-bottom: 72px }` never reset at ≥900px | layout defect. |
| G22 | **Prototype presented with fixtures only** | no fetch, no state, no API shape | `DESIGN_BRIEF.md`: "Prototypes may use fixtures; **shipping UI must use real APIs**." Acceptable for a mockup — recorded so it is not mistaken for evidence. `README.md`: "no control here is evidence of working behaviour." |

### g.1 Icon inventory → closest `lucide-react` export

**Every name below is marked TO VERIFY against the pinned `lucide-react` version.** Lucide has
renamed exports across releases (`Home`→`House`, `Rows`→`Rows2`, `SortAsc`/`SortDesc` deprecated in
favour of `ArrowUpNarrowWide`/`ArrowDownWideNarrow`), and `VZ-DESIGN-001` requires a test asserting
every registry name exists in the pinned package. Do not import any of these without that check.

| # | Mockup use | Path (abbreviated) | Proposed semantic registry key | Closest `lucide-react` export | Note |
|---|---|---|---|---|---|
| 1 | Nav search field (711), mobile Search tab (1207) | `circle 11,11 r7` + `m20 20-3.5-3.5` | `search` | `Search` | TO VERIFY |
| 2 | Clear query (714), applied-chip `.x` (753, 757), sheet close (1188) | `M6 6l12 12M18 6l-12 12` | `dismiss` | `X` | TO VERIFY |
| 3 | Notifications (726) | bell + clapper | `notifications` | `Bell` | TO VERIFY |
| 4 | Upload (729) | `M12 3v13` + chevron + baseline | `upload` | `Upload` | TO VERIFY |
| 5 | Mobile Filters button (765) | `M3 6h18 / M6 12h12 / M10 18h4` | `filter` | `ListFilter` | TO VERIFY — Lucide's `ListFilter` is `M3 6h18 / M7 12h10 / M10 18h4`; `Filter` is a funnel outline. Geometry differs slightly |
| 6 | Sort trigger (778) and mobile sort (769) | `M3 6h13 / M3 12h9 / M3 18h5 / m17 8 4 4-4 4` | `sort` | `ArrowDownWideNarrow` | TO VERIFY — the mockup's arrow is horizontal; Lucide's sort glyphs use a vertical arrow. May need a registry-local custom mark, which `DESIGN_BRIEF.md` treats as a separately reviewed original asset |
| 7 | Sort trigger chevron (780) | `m6 9 6 6 6-6` | `disclosure-down` | `ChevronDown` | TO VERIFY |
| 8 | Sort option check (783–787), swatch check (333), | `M5 12l5 5L20 7` | `selected` | `Check` | TO VERIFY |
| 9 | View: Grid (793) | 4 equal `rect rx=1` | `view-grid` | `LayoutGrid` | TO VERIFY |
| 10 | View: Masonry (796) | 4 uneven `rect` | `view-masonry` | `LayoutDashboard` | TO VERIFY — no exact Lucide masonry glyph; candidates `LayoutDashboard`, `LayoutPanelLeft`, `Columns3` |
| 11 | View: Large (799) | 2 full-width `rect` | `view-large` | `Rows2` | TO VERIFY — formerly `Rows`; also consider `LayoutPanelTop` |
| 12 | Featured badge (905) | filled 5-point star | `featured` | `Star` | TO VERIFY — `fill="currentColor"`; Lucide is stroke-only, needs a `fill` prop or a `StarIcon` + CSS |
| 13 | Save action (909 et al.) | `M19 21 12 16l-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2Z` | `save` / `bookmark` | `Bookmark` | TO VERIFY — also used for the mobile "Saved" tab (1211). **This control has no ledger ID; see §h** |
| 14 | Love action (910, 935), love count (919, 944) | `M12 21s-7-4.5-9-9a5 5 0 0 1 9-3 5 5 0 0 1 9 3c-2 4.5-9 9-9 9Z` | `favorite` | `Heart` | TO VERIFY — needs distinct filled/unfilled variants; `VZ-FAVORITE-001` |
| 15 | View count (920) | `M2 12s4-7 10-7…` + `circle r3` | `views` | `Eye` | TO VERIFY |
| 16 | Video badge (957) | `M8 5v14l11-7z` filled triangle | `video` | `Play` | TO VERIFY — filled; see note on #12 |
| 17 | "See all 312" (1101) | `M5 12h14M13 5l7 7-7 7` | `forward` | `ArrowRight` | TO VERIFY — needs RTL mirroring per `DESIGN_BRIEF.md` |
| 18 | Load more (1171) | `M12 5v14` + `m6 13 6 6 6-6` | `load-more` | `ArrowDown` | TO VERIFY |
| 19 | Mobile Home tab (1203) | `m3 11 9-8 9 8 / M5 10v10h14V10` | `home` | `House` | TO VERIFY — renamed from `Home`; both may exist as aliases depending on version |
| 20 | Mobile You tab (1215) | `circle 12,8 r4` + shoulders | `account` | `User` | TO VERIFY |
| 21 | Related-chip arrow (1041) | literal `›` text character | `disclosure-right` | `ChevronRight` | TO VERIFY — currently not an icon at all |
| 22 | Orientation glyphs (841–844) | CSS-drawn bordered boxes, 4 sizes | `orientation-any` / `-landscape` / `-portrait` / `-panorama` | `Square`, `RectangleHorizontal`, `RectangleVertical`, `RectangleHorizontal` | TO VERIFY — no Lucide panorama glyph; the four-way distinction may need original marks |

Stroke rules observed and inconsistent: `stroke-width` values used are `1.7` (nav actions), `1.8`
(filters, sort), `1.9` (mobile tabs), `2` (most), `2.2` (sheet close), `2.4` (sort checks), `2.5`
(clear/dismiss), `3` (swatch check data-URI), `1.4px` CSS border (orientation glyphs). Sizes: 8, 11,
12, 13, 14, 16, 19, 20 px. A registry must fix one stroke and a small size set.

---

## h. Control-to-action matrix

Action IDs follow the dotted convention already used in `docs/quality/ui-controls.json`
(`surface.component.verb`). **Proposed** means proposed by this inventory — none of these exists in
`ui-controls.json` yet except where the "Existing control ID" column names one. Milestones are from
`docs/MILESTONES.md`; where a control's ledger IDs span milestones, the **latest** governs when the
control can be fully honest.

`NO LEDGER ID` means: this control implies a capability that no entry in `docs/quality/features.json`
covers. Per the task brief, none has been invented.

### h.1 Shell

| # | Control (visible label) | Element | Proposed action ID | Existing control ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|---|
| 1 | Brand → home | `<a class="brand">` | `shell.brand.home` | — | `VZ-EXPLORE-001`, `VZ-BRAND-001` (site name/logo) | M3 / M5 |
| 2 | Search field | `<input id="searchInput">` | `search.query.submit` | `shell.nav.search` | `VZ-SEARCH-001` | **M3** |
| 3 | (implied) typeahead suggestions | *absent from the mockup* | `search.query.suggest` | — | `VZ-SEARCH-003` | **M3** |
| 4 | Clear | `<button class="clear">` | `search.query.clear` | — | `VZ-SEARCH-001` | M3 |
| 5 | Discover | `<a>` | `shell.nav.explore` | `shell.nav.explore` | `VZ-EXPLORE-001` | M3 |
| 6 | Collections | `<a href="#">` | `shell.nav.collections` | — | `VZ-COLLECTION-001` | **M5** (full profile only) |
| 7 | Artists | `<a href="#">` | `shell.nav.people` | — | `VZ-EXPLORE-001` (users listing) | M3 |
| 8 | Notifications | `<button class="icon-btn">` | `shell.nav.notifications` | `shell.nav.notifications` | `VZ-NOTIFY-001` | M2 |
| 9 | Upload | `<button class="icon-btn">` | `shell.nav.upload` | `shell.nav.upload` | `VZ-UPLOAD-001`, `VZ-UPLOAD-005` | M1 / M3 |
| 10 | Account avatar `MK` | `<span class="avatar">` | `shell.nav.account` | `shell.nav.account` | `VZ-AUTH-001`, `VZ-ACCOUNT-001` | M1 / M2 |
| 11 | Mobile tab: Home | `<a class="tab">` | `shell.tabbar.home` | — | `VZ-EXPLORE-001` | M3 |
| 12 | Mobile tab: Search | `<button class="tab active">` | `shell.tabbar.search` | `shell.nav.search` | `VZ-SEARCH-001` | M3 |
| 13 | Mobile tab: Saved | `<button class="tab">` | `shell.tabbar.saved` | — | `VZ-FAVORITE-001` **if** "Saved" means the favourites listing; if it means a separate bookmark list → **NO LEDGER ID** | M2 / n/a |
| 14 | Mobile tab: You | `<button class="tab">` | `shell.tabbar.profile` | — | `VZ-PROFILE-001` | M2 |

### h.2 Result header and scope

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 15 | Result counts (`48,214 photos · 312 artists · 26 collections`) — display, not a control, but must be a real permission-aware value | `.rh-count` | `search.counts.render` | `VZ-SEARCH-001` (counts inside the authorized query) | M3 |
| 16 | `refreshed moments ago` | text | `search.freshness.render` | `VZ-SEARCH-004` (index freshness is an admin surface there, not a public one) — **as a public freshness label: NO LEDGER ID** | M3 / n/a |
| 17 | Scope tab: **Photos** | `<button class="filter-chip active">` | `search.scope.photos` | `VZ-SEARCH-001` | M3 |
| 18 | Scope tab: **Artists** | `<button class="filter-chip">` | `search.scope.users` | `VZ-SEARCH-001`, `VZ-PROFILE-001` | M3 |
| 19 | Scope tab: **Collections** | `<button class="filter-chip">` | `search.scope.collections` | `VZ-SEARCH-001` covers "photos, albums, users and tags" — **collections are not in its scope list**; `VZ-COLLECTION-001` is the entity | **M5** |
| 20 | Scope tab: **Series** | `<button class="filter-chip">` | `search.scope.series` | **NO LEDGER ID** — no "series" entity exists. Nearest neighbours are `VZ-COLLECTION-001` (album grouping) and `VZ-GALLERY-001` (curated sets of others' photos); neither is "editorial series" | n/a |
| 21 | Scope tab (missing): **Albums** | *absent* | `search.scope.albums` | `VZ-SEARCH-001` names albums explicitly — **the mockup omits the albums scope** | M3 |
| 22 | Scope tab (missing): **Tags** | *absent* | `search.scope.tags` | `VZ-SEARCH-001`, `VZ-TAG-001` | M3 |
| 23 | Applied chip: `Landscape` (remove) | `<button class="filter-chip applied">` | `search.filter.remove` | `VZ-SEARCH-002` (orientation) | **M5** |
| 24 | Applied chip: `Past year` (remove) | `<button class="filter-chip applied">` | `search.filter.remove` | `VZ-SEARCH-002` (date taken) | **M5** |

### h.3 Toolbar

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 25 | Open sort menu | `<button id="sortBtn">` | `search.sort.open` | `VZ-SEARCH-001` (the ledger does not enumerate sort orders — the **option set below** is where the gaps are) | M3 |
| 26 | Sort: **Relevant** | `.pop-item[data-v=Relevant]` | `search.sort.relevance` | `VZ-SEARCH-001` (FTS ranking) | M3 |
| 27 | Sort: **Recent** | `.pop-item[data-v=Recent]` | `search.sort.recent` | `VZ-SEARCH-001`; cf. `VZ-EXPLORE-001` "recent" | M3 |
| 28 | Sort: **Interesting** | `.pop-item[data-v=Interesting]` | `search.sort.interesting` | `VZ-EXPLORE-003` (interestingness ranking) — full profile, and it is an *Explore* feature, not a search sort. **As a search sort: NO LEDGER ID** | **M6** |
| 29 | Sort: **Most loved** | `.pop-item[data-v="Most loved"]` | `search.sort.favorites` | `VZ-FAVORITE-001` supplies the count; no ledger entry makes favourites a **search sort order** → **NO LEDGER ID** for the sort itself | M2 (data) / n/a (sort) |
| 30 | Sort: **Most viewed** | `.pop-item[data-v="Most viewed"]` | `search.sort.views` | `VZ-STATS-001` ("per-item views count (definition documented)") supplies the count; sort order → **NO LEDGER ID** | M3 (data) / n/a (sort) |
| 31 | View: **Grid** | `<button class="view-btn" aria-label="Grid">` | `search.view.grid` | `VZ-LISTING-001` is an **owner** setting ("fixed/fluid grid, columns per device"), not a per-viewer toggle → **NO LEDGER ID** for a viewer-level density switch | M3 (owner setting) / n/a |
| 32 | View: **Masonry** | `<button class="view-btn active">` | `search.view.masonry` | same as #31 | same |
| 33 | View: **Large** | `<button class="view-btn" aria-label="Large">` | `search.view.large` | same as #31 | same |
| 34 | Mobile: open filter sheet | `<button id="openSheet">` | `search.filters.sheet.open` | `VZ-SEARCH-002`, `VZ-RESPONSIVE-001` | **M5** / M1 |
| 35 | Mobile: open sort | `<button id="openSortMobile">` | `search.sort.open` | as #25 | M3 |

### h.4 Filter sidebar and sheet (identical control set — the sheet clones it)

**Every row in this block is `VZ-SEARCH-002`, which is `full` profile only and lands in M5 — two
milestones after the search page itself (`VZ-SEARCH-001`, M3).**

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 36 | Content: **Photos** | `.fi input[type=checkbox]` | `search.filter.media_type.photo` | `VZ-SEARCH-002` (media type) | **M5** |
| 37 | Content: **Videos** | checkbox | `search.filter.media_type.video` | `VZ-SEARCH-002`, `VZ-MEDIA-005` | **M5** / M3 |
| 38 | Content: **Editorial series** | checkbox | `search.filter.media_type.series` | **NO LEDGER ID** (as #20) | n/a |
| 39 | Content: **Public domain** | checkbox | `search.filter.license.public_domain` | `VZ-LICENSE-001`, `VZ-SEARCH-002` | **M5** |
| 40 | Colour swatch ×12 (`Midnight`…`Any`) | `<button class="sw">` | `search.filter.color` | `VZ-SEARCH-002` (colour) | **M5** |
| 41 | Orientation: `Any` / `Land` / `Port` / `Pano` | `.seg button` ×4 | `search.filter.orientation` | `VZ-SEARCH-002` (orientation) | **M5** |
| 42 | Minimum size slider | `<input type="range">` | `search.filter.min_size` | `VZ-SEARCH-002` (min size) | **M5** |
| 43 | Date taken: `Anytime` / `Past week` / `Past month` / `Past year` | `.fi input[type=radio]` | `search.filter.date_taken` | `VZ-SEARCH-002` (date taken/uploaded) | **M5** |
| 44 | Date taken: `Custom range…` | radio | `search.filter.date_taken.custom` | `VZ-SEARCH-002`; the radio implies a date-picker dialog that the mockup does not draw | **M5** |
| 45 | License: `All licenses` | checkbox | `search.filter.license.any` | `VZ-LICENSE-001`, `VZ-SEARCH-002` | **M5** |
| 46 | License: `Creative Commons` | checkbox | `search.filter.license.cc` | same | **M5** |
| 47 | License: `Commercial use` | checkbox | `search.filter.license.commercial` | same | **M5** |
| 48 | License: `No derivatives` | checkbox | `search.filter.license.nd` | same | **M5** |
| 49 | Camera: `Leica` / `Fujifilm` / `Hasselblad` | checkbox ×3 | `search.filter.camera_make` | `VZ-SEARCH-002` (camera/lens/EXIF, "camera finder pages by brand/model from EXIF"), `VZ-MEDIA-004` (EXIF read) | **M5** / M1 |
| 50 | Camera: `Analog / Film` | checkbox | `search.filter.camera.analog` | **NO LEDGER ID** — "analog/film" is not an EXIF camera make/model facet; no ledger entry defines a film/analogue classification | n/a |
| 51 | Sidebar `Reset` | `<button class="reset">` | `search.filters.reset` | `VZ-SEARCH-002` | **M5** |
| 52 | Sidebar `Apply` | `<button class="apply">` | `search.filters.apply` | `VZ-SEARCH-002` | **M5** |
| 53 | Sheet `Reset` | `.sheet-footer .reset` | `search.filters.reset` | as #51 | **M5** |
| 54 | Sheet `Show 48,214 results` | `<button id="applySheet">` | `search.filters.apply` | as #52; the live count is `VZ-SEARCH-001` (facet counts inside the authorized query) | **M5** / M3 |
| 55 | Sheet `Close` | `<button id="closeSheet">` | `search.filters.sheet.close` | `VZ-RESPONSIVE-001`, `VZ-A11Y-001` | M1 |
| 56 | Sheet scrim dismiss | `#sheetScrim` click | `search.filters.sheet.close` | same | M1 |
| — | **Filters the ledger requires that the mockup omits** | — | — | `VZ-SEARCH-002` also names **safety level** (`VZ-NSFW-001`), **content type** (`VZ-PRIVACY-003`), **tags-only**, **in-gallery** (`VZ-GALLERY-001`), **group** (`VZ-GROUP-002`), **geo** (`VZ-GEO-001`), and **date uploaded** separately from date taken. None appears in the mockup. `VZ-SEARCH-001` also requires an **advanced dialog** with all-words / exact-phrase / none-of-these and a category operator (`VZ-CATEGORY-001`) — absent | — | **M5** |

### h.5 Result card

| # | Control / field | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 57 | Open photo | `<a class="card" href="#">` | `search.result.open` | `VZ-VIEWER-001`, `VZ-SHARE-003` (route shape) | M1 / M3 |
| 58 | **Save** | `<button class="c-act" aria-label="Save">` | `search.result.save` | **NO LEDGER ID as a distinct control.** Vizra has favourites (`VZ-FAVORITE-001`), albums (`VZ-ALBUM-001`), collections (`VZ-COLLECTION-001`) and galleries (`VZ-GALLERY-001`) — but no bookmark/read-later primitive. Either it is a duplicate of Love, or it is add-to-album/gallery under the wrong affordance. **Owner decision required** | n/a |
| 59 | **Love** | `<button class="c-act" aria-label="Love">` | `search.result.favorite` | `VZ-FAVORITE-001` | **M2** |
| 60 | `Featured` badge | `.card-badge` | `search.result.featured.render` | `VZ-EXPLORE-003` (featured/interestingness, `full`) or operator curation under `VZ-ADMIN-002` | **M6** |
| 61 | `1:42` video badge | `.card-badge.video` | `search.result.duration.render` | `VZ-MEDIA-005` | M3 |
| 62 | `RAW` badge | `.card-badge` | — | **CONFLICT: `VZ-MEDIA-002` declines RAW** | n/a |
| 63 | `4K` badge | `.card-badge` | `search.result.resolution.render` | `VZ-SEARCH-002` (min size) supplies the facet; a per-card resolution badge → **NO LEDGER ID** | **M5** / n/a |
| 64 | `CC-BY` badge | `.card-badge` | `search.result.license.render` | `VZ-LICENSE-001` | **M5** |
| 65 | Author name / avatar (not a link in the mockup) | `.card-author` | `search.result.author.open` | `VZ-PROFILE-001` | **M2** |
| 66 | Love count (`4.2k`) | `.card-stats span` | `search.result.favorites.render` | `VZ-FAVORITE-001` ("public count") | M2 |
| 67 | View count (`38k`) | `.card-stats span` | `search.result.views.render` | `VZ-STATS-001` ("per-item views count (definition documented)"); per-item stats over time is `VZ-STATS-002` (`full`) | M3 / **M6** |
| — | **Card affordances the ledger expects and the mockup omits** | — | — | safety-level blur (`VZ-NSFW-001`), visibility marker (`VZ-PRIVACY-001/002`), rating (`VZ-RATING-001`), comment count (`VZ-COMMENT-001`), download (`VZ-DOWNLOAD-001`), share (`VZ-SHARE-001`), report (`VZ-REPORT-001`), add-to-album (`VZ-ALBUM-001`) | — |

### h.6 Strips and pagination

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 68 | Related-query chip ×8 (`alpenglow`…`moonlight peaks`) | `<a class="rc">` | `search.related.apply` | **NO LEDGER ID** if these are *related queries*. `VZ-SEARCH-003` is typeahead **suggestions** for tags/users/albums, not post-hoc query refinement. If they are tags, `VZ-TAG-001` (tag pages) applies. **Owner/search-owner decision** | n/a / M3 |
| 69 | `See all 312` | `<a class="strip-more">` | `search.scope.users` | `VZ-SEARCH-001` (users scope) | M3 |
| 70 | Artist card (inert in the mockup; must be a link) | `.artist-card` | `search.result.user.open` | `VZ-PROFILE-001` | **M2** |
| 71 | Artist thumbnail ×3 per card (inert) | `.artist-thumbs div` | `search.result.user.preview` | `VZ-PROFILE-001` | **M2** |
| 72 | `Follow` ×4 | `<button class="artist-follow">` | `search.result.user.follow` | `VZ-FOLLOW-001`; approval flow is `VZ-FOLLOW-002` (`full`) | **M2** / **M5** |
| 73 | `Load more results` | `<button>` | `search.page.more` | `VZ-SEARCH-001` ("bounded pagination"), `VZ-LISTING-001` ("classic/endless pagination" is an **owner** setting) | M3 |
| 74 | `Showing 1–24 of 48,214 · Page 1 of 2,009` | `.pager-hint` | `search.page.position.render` | `VZ-SEARCH-001` (bounded pagination — an unbounded "Page 1 of 2,009" contradicts it) | M3 |

### h.7 Summary — controls with NO LEDGER ID

1. **Save** (card bookmark, 17 instances) and the **mobile "Saved" tab** — #58, #13 — no bookmark
   primitive exists.
2. **"Series" scope tab** and the **"Editorial series" content filter** — #20, #38.
3. **View-density switcher** (Grid / Masonry / Large) as a *viewer* control — #31–33.
4. **"Most loved" and "Most viewed" as search sort orders** — #29, #30 (the counts have ledger IDs;
   the sort orders do not).
5. **"Interesting" as a search sort order** — #28 (`VZ-EXPLORE-003` is an Explore ranking).
6. **"Analog / Film" camera facet** — #50.
7. **Per-card `4K` resolution badge** — #63.
8. **Public "refreshed moments ago" index-freshness label** — #16.
9. **Related-query chips** if they are query rewrites rather than tags — #68.
10. **`RAW` badge** — #62, which is worse than absent: it contradicts `VZ-MEDIA-002`.

### h.8 Summary — controls whose backend lands after M3

The page itself is M3 (`VZ-SEARCH-001/003/004`). These controls cannot be honest at M3:

- **All 21 sidebar/sheet facet controls** (#36–#56) — `VZ-SEARCH-002`, **M5**, `full` profile.
- Both applied-filter chips (#23, #24) — `VZ-SEARCH-002`, **M5**.
- Collections scope (#19) and the Collections nav link (#6) — `VZ-COLLECTION-001`, **M5**.
- `CC-BY` badge (#64) and the licence facets — `VZ-LICENSE-001`, **M5**.
- `Featured` badge (#60) — `VZ-EXPLORE-003`, **M6**.
- Per-item view count (#67) beyond the basic `VZ-STATS-001` count — `VZ-STATS-002`, **M6**.
- Follow-request semantics behind the Follow button (#72) — `VZ-FOLLOW-002`, **M5**.

M2 dependencies (before the page, so these are safe by M3 but are *not* part of `VZ-SEARCH-001`):
Love (#59), Follow (#72 base), artist/profile links (#65, #70, #71), notifications (#8), safety
filtering (`VZ-NSFW-001`).

---

## i. Draft search API response fields

**DRAFT FOR THE OpenAPI OWNER — not a contract.** Field *names* only, derived strictly from what the
page renders; no semantics, types, nullability, units, pagination style or authorization behaviour
are proposed here. `vizra-core` owns the canonical OpenAPI (`AGENTS.md`); this list exists so the
contract owner can see what the page would need and decide what actually exists. Several entries
correspond to controls with no ledger ID (§h.7) and must not be added on the strength of a mockup.

### i.1 Envelope

```
query
scope                    (photos | users | albums | tags | collections? | series?)
sort
page | cursor
next_cursor
per_page
total                    (bounded per VZ-SEARCH-001)
total_pages
counts_by_scope          { photos, users, albums, tags, collections?, series? }
applied_filters
facets                   (per facet key → [{ value, label, count }])
results
related_queries          [{ query }]          ← NO LEDGER ID (§h.7 #9)
suggested_users          (the "Artists who shoot this" strip)
generated_at             ← the "refreshed moments ago" label, NO LEDGER ID (§h.7 #8)
```

### i.2 Photo result item

```
id
url
title
alt_text
width
height
aspect_ratio
thumb_url
thumb_srcset
placeholder_color        (the .card { background: var(--line-2) } slot)
media_type
duration                 (video badge)
license_code
license_label
featured                 ← VZ-EXPLORE-003 (M6)
safety_level             ← required by VZ-NSFW-001; the mockup shows no field for it
visibility               ← required by VZ-PRIVACY-001; the mockup shows no field for it
content_type             ← VZ-PRIVACY-003
taken_at
uploaded_at
orientation
camera_make
camera_model
dominant_colors
owner { id, username, display_name, avatar_url, url }
counts { favorites, views }
viewer_state { favorited }
viewer_state { saved }   ← NO LEDGER ID (§h.7 #1)
```

Note for the contract owner: the mockup's single `card-badge` slot carries five unrelated values
(`featured`, `duration`, `RAW`, `4K`, `CC-BY`). Modelling it as one string field would encode a
design defect into the contract.

### i.3 User ("artist") result item

```
id
username
display_name
handle
avatar_url
url
photo_count
preview_photos [{ id, thumb_url, alt_text, url }]
viewer_state { following }
```

The mockup shows no follower count, no bio, no verified/role marker, and no follow-request state.

### i.4 Facet keys implied by the sidebar

```
media_type              (photos | videos | series?)
license                 (public_domain | cc | commercial | no_derivatives | all)
color
orientation             (any | landscape | portrait | panorama)
min_size
date_taken              (anytime | past_week | past_month | past_year | custom{from,to})
camera_make             (+ an unmodelled "analog/film" value — NO LEDGER ID)
```

`VZ-SEARCH-002` additionally requires facets the mockup never draws: `date_uploaded`,
`safety_level`, `content_type`, `tags_only`, `in_gallery`, `group`, `geo`. Every facet **count**
must be computed inside the same authorized query as the results (`VZ-SEARCH-001`), not from a
cached global tally, or the counts leak the existence of private content.

---

## Appendix — verification notes

Contrast figures in §f.4 were computed from the OKLCH declarations by OKLab → linear sRGB →
sRGB gamma → WCAG relative luminance → `(L1+0.05)/(L2+0.05)`. They are **approximate**: the browser
resolves `oklch()` and `color-mix(in oklab, …)` itself, gamut-maps out-of-range values, and composites
translucent layers over whatever is behind them. Treat these as screening values that identify which
pairs need measurement in the running production build, per `AGENTS.md` ("Do not fabricate outputs")
and `VZ-A11Y-001` ("contrast … over real backings").

Counts in this document (19 cards, 37 Unsplash URLs, 52 inline SVGs, 6 breakpoints, 15 radii, 9
shadow recipes, 15 type sizes) were taken by direct enumeration of the file at the sha256 recorded in
`docs/design/claude-design/README.md`. If that hash changes, re-derive them.
