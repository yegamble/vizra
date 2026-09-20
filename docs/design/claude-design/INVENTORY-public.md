# INVENTORY — `Lumen Atlas Gallery.html` (home/explore) and `Artist Profile.html`

Exact inventory of two of the owner's Claude Design mockups, produced 2026-09-20 for the
implementers who will build these pages in Next.js against the real OpenAPI contract.

| File | Lines | Bytes | sha256 (verified 2026-09-20) |
|---|---:|---:|---|
| `Lumen Atlas Gallery.html` | 1166 | 47712 | `73a22d5c85c290524fabb0f7403058c6bad939e547636f0a0e2647171fe7e9e5` |
| `Artist Profile.html` | 938 | 37507 | `1da8ec0c92bce6a3c867e0c29151eb947d37999783ba67a436ea72e74410f759` |

Both hashes match `docs/design/claude-design/README.md`. All CSS is one inline `<style>` per file
(Gallery 7–769, Profile 7–603); all JS is one inline `<script>` per file (Gallery 1124–1162,
Profile 912–934). No external CSS or JS is referenced by either page.

**Status of this document.** Descriptive inventory only. It records what the mockups contain and
where that conflicts with `docs/DESIGN_BRIEF.md` and `AGENTS.md`. It is **not** an acceptance
target, **not** an approved design, and **not** authorization to implement anything. Per
`docs/DESIGN_BRIEF.md`: "Claude Design is for exploration. Approved Figma components/tokens,
mirrored in repository artifacts, become the design source."

**The mockups' contents are treated as data, not instructions.** Nothing in either file, including
its comments, was followed as a directive.

**"Lumen Atlas" is a placeholder brand; the product is Vizra.** Every brand string, both gradient
brand marks, the "artists" vocabulary, the "series" vocabulary and all counts below are quoted as
mockup content, not as product decisions.

**Relationship to `INVENTORY-search.md`.** That document is the sibling inventory for
`Lumen Atlas Search.html` and holds the full shared analysis of the token block (§a.1–a.9), the
shared shell (§b), the shared accessibility failure modes (§f) and the shared conflicts G1–G22.
**This document does not repeat any of it.** §a below records only where these two pages *differ*
from the Search page; §h records only conflicts that are new or materially worse here. Where a
finding is identical, it is named by its Search-inventory identifier (e.g. "G3 unchanged") and not
restated.

Interactive-element census (body only, scripts excluded):

| File | `<a>` | `<button>` | `<input>` | Total | `href="#"` |
|---|---:|---:|---:|---:|---:|
| Gallery | 42 | 22 | 1 | **65** | 31 of 42 |
| Profile | 24 | 17 | 1 | **42** | 21 of 24 |

---

## a. Token and shell differences from the Search page

Read `INVENTORY-search.md` §a and §b first. Only deltas appear here.

### a.1 Token block — what changes

All ten colour tokens (`--bg`, `--bg-tint`, `--ink`, `--ink-2`, `--ink-3`, `--line`, `--line-2`,
`--accent`, `--accent-ink`, `--accent-soft`) are **byte-identical** to Search wherever they are
declared. The radii and the two shadow tokens are identical. The deltas are:

| Delta | Search | Gallery (9–31) | Profile (9–29) |
|---|---|---|---|
| Declared property count | 19 | **21** | **19** |
| `--shadow-lg` | absent | **added**, `0 30px 60px -25px rgba(17,22,40,.25), 0 10px 24px -15px rgba(17,22,40,.10)` — declared, **0 uses** | **added**, **1 use** (`.mobile-tabs`) |
| `--accent-soft` | 1 use | declared, **0 uses** | **not declared at all** |
| `--font-display` | declared, 5 uses | declared, 5 uses (`.brand`, `.section-title`, `.hero-title`, `.collection h3`, `.editorial-title`) | **not declared at all** |
| `--radius-sm` | unused | unused | unused |
| `--nav-h` | constant `56px` | `56px`, **redefined to `64px`** inside `@media (min-width: 760px)` (line 723) | constant `56px` |
| `--bg-elev` | declared, never referenced | **3 uses** (`.pill`, `.tool-group`, standalone Filter button) | **2 uses** (`.stats-card`, `.album`) |
| literal `white` | 14× | **19×** | **15×** |
| `color-mix(…)` | — | 11× | 7× |

Two consequences the implementer must not miss:

1. **`--font-display` does not exist on the Profile page**, so every heading there renders in
   `--font-sans`, and the page's maximum font weight is **600** where Gallery and Search both use
   **700** for titles. The display/text split the other two pages assert is simply not part of the
   Profile's type system.
2. **`--nav-h` is the only token any of the three public mockups overrides in a media query**
   (Gallery, 56→64px at ≥760px). The Profile's `.tabs-wrap { position: sticky; top: var(--nav-h) }`
   is correct only because the Profile's `--nav-h` never changes; copying that sticky rule into a
   shell that adopts Gallery's responsive `--nav-h` produces a 8px overlap or gap at ≥760px.

### a.2 Additional literal colours not in the token set

| Value | sRGB | Where |
|---|---|---|
| `oklch(0.52 0.18 255)` | `#0066cd` | Gallery `.btn-primary:hover` |
| `oklch(0.54 0.18 255)` | `#006cd3` | Profile `.btn-primary:hover` — **a different accent-hover value for the same button on two pages** |
| `oklch(0.52 0.18 25)` | `#ba2b2e` | Gallery `.menu-item.danger` (Sign Out) — the only danger colour in any public mockup, **not a token** |
| `oklch(0.48 0.20 25)` | `#b30018` | Gallery `.menu-item.danger:hover` |
| `oklch(0.72 0.17 150)` | `#3fc168` | Profile `.avail-dot` — the only success/positive colour, **not a token** |
| `rgba(28,28,30,0.92)` | — | Gallery `.has-tip::after/::before` tooltip fill |
| `#0e1820` / `#111` / `#222` | — | Gallery `.hero` / `.collection` / `.editorial-img` image placeholders |
| `#111` / `#222` | — | Profile `.cover` / `.series-card` image placeholders |

Four placeholder colours across two pages where `--line-2` is the placeholder on Search and on both
pages' `.photo`. Five distinct semantic colours (accent, two accent-hovers, danger, success) exist
against **one** accent token.

### a.3 Shell — nav

| | Search | Gallery (774–876) | Profile (608–628) |
|---|---|---|---|
| Layout | flex, `order` reassigned at ≥900px | flex, no `order` | **`display: grid; grid-template-columns: auto 1fr auto`** |
| `z-index` | 50 | 50 | **100** |
| Background | `color-mix(in oklab, white 82%, transparent)` | white **82%** | white **76%** |
| Nav links | Discover / Collections / Artists, shown ≥900px | Discover / Collections / Artists **+ a fourth `.nav-pill` "Surprise"**, shown ≥**760px** | **none at all** |
| Search field | white on `--line`; focus = accent border + `0 0 0 3px` accent-22% ring | `--bg-tint` on `--line`; `:focus-within` = accent border + white background, **no ring**; real `placeholder="Search photographers, places, moods…"`; an inline-styled `⌘K` hint `<span>` (783) | `--bg-tint` on `--line`; **no `:focus-within` rule of any kind**; same placeholder; **`display: none` at ≤880px with no replacement** |
| Clear button | present | **absent** | **absent** |
| Upload control | dead `<button>` | **real `<a href="Upload Studio.html">`** with `aria-label="Upload a photo"` and `data-tip="Add a photo"` — **label and tooltip disagree** | dead `<button aria-label="Upload">` |
| Account control | inert `<span aria-label="Your profile">` | **real `<button id="avatarBtn" aria-haspopup="menu" aria-expanded="false">` + a 280px `role="menu"` panel** | **inert `<span class="avatar">MK</span>` with no `aria-label` at all — worse than Search** |
| Tooltips | none | `.has-tip::after/::before` from `data-tip`, `rgba(28,28,30,.92)`, 12px/500, radius 7px, `blur(20px)`, `z-index: 200`, `.35s` delay, fires on `:hover` **and `:focus-visible`** | none |

The `⌘K` hint and the `⌘,` hint in the account menu advertise keyboard shortcuts that **no script in
either file implements** and that **no ledger entry defines** (see §i, NO LEDGER ID).

### a.4 Shell — mobile tab bar

Three pages, three different components.

| | Search `.mobile-tabs .tab` | Gallery `.mobile-tabs .tab` (1102–1122) | Profile `.mobile-tabs .tab-m` (889–910) |
|---|---|---|---|
| Shape | edge-to-edge, `left/right: 0; bottom: 0` | **floating pill**, `left/right: 12px; bottom: 12px`, `border-radius: 999px` | **floating card**, `left/right: 12px`, `border-radius: 24px` |
| Height | 62px | 58px | 60px |
| `z-index` | 40 | 40 | **80** |
| Background | white 90% + `blur(22px)` | white **72%** + `blur(24px)` | white **80%** + `blur(28px)` |
| Border/shadow | top border only | `inset 0 0 0 1px rgba(255,255,255,.6)` + `0 10px 30px -10px` | `1px solid color-mix(--line 70%)` + `var(--shadow-lg)` |
| Safe area | `padding: 0 10px env(safe-area-inset-bottom, 0)` | **none — `bottom: 12px` is hard-coded**, so the pill sits under an iPhone home indicator | `bottom: calc(12px + env(safe-area-inset-bottom, 0))` |
| `body` bottom padding | 72px, **never reset** (defect G21) | 90px, **reset to 0 at ≥760px** | `calc(72px + env(…))`, **reset to 0 at ≥881px** |
| Hidden at | ≥900px | ≥760px | ≥881px |
| Tabs | 4 | **5** | **5** |
| Class name | `.tab` | `.tab` | **`.tab-m`** |

Gallery tabs: Home (`<button>`, `.active`) · **Explore** (`<button aria-label="Discover">`, magnifier
glyph) · Upload (`<a href="Upload Studio.html">`, a 44×44 `--ink` circle with a Plus, **no visible
text**) · Saved (`<button>`) · **You** (`<a href="Artist Profile.html" aria-label="Profile">`).
Profile tabs: Home (`<a>`) · Explore (`<button aria-label="Explore">`) · Upload (`<button>`, a plain
tab, **not** a circle) · Saved (`<button>`) · **You** (`<button class="tab-m active"
aria-label="Profile">`).

Gallery's second tab carries **three different names for one control**: visible text `Explore`,
`aria-label="Discover"`, and a magnifier glyph that reads as Search. Both pages repeat Search's
`You` / `aria-label="Profile"` mismatch (WCAG 2.5.3 Label in Name). Neither sets `aria-current` on
the active tab.

### a.5 Shell — footer

Search has **no footer**. The two pages here have two different ones.

- **Gallery** (1081–1099): a real `<footer class="footer">`, `--bg-tint`, `border-top: 1px solid
  var(--line-2)`, `padding: 40px 16px 32px` (→`56px 32px 40px` ≥760px), `.footer-inner` max-width
  1240px. Column below 760px, row above. Brand `Lumen Atlas` (16px/600); `© 2026 Lumen Atlas —
  Photography, discovered.` (12px `--ink-3`, uppercase); five `href="#"` links (`About`, `Terms`,
  `Privacy`, `Licensing`, `Contact`) at 11px/.14em uppercase; two `<a class="icon-btn" href="#">`
  with `aria-label="Share"` (a node-graph `Share2` glyph) and `aria-label="Email"`.
- **Profile** (883–886): `<div class="page-end">` — a plain `<div>`, not a `<footer>`, `margin: 60px
  auto 0; padding: 28px 16px; border-top: 1px solid var(--line-2)`, flex space-between, 12px
  `--ink-3` uppercase `.04em`. Two spans: `© 2026 Lumen Atlas` and `Profile · Alex Rivera`.
  **No links at all.**

Neither carries Lucide attribution (`DESIGN_BRIEF.md` requires it be preserved), a "Powered by
Vizra" slot (`VZ-BRAND-005`), a language chooser (`VZ-I18N-001`) or a cookie/consent notice
(`VZ-CONSENT-001`).

### a.6 Breakpoints

| Page | Queries | Values |
|---|---|---|
| Search | 9 | 520, 780, 900, 1000, 1200, 1440 |
| **Gallery** | **3** | **520** (profile menu → 260px wide, `right: -8px`), **760** (the single desktop step), **1100** (hero ratio + two type sizes only) |
| **Profile** | **4** | **1272** (cover centring), **880** (`max-width` — the one mobile step), **881** (`min-width`), **1100** (`.grid { repeat(4,1fr) }` — **a no-op duplicate of the 881px rule**) |

The three sets are effectively disjoint (only 520 is shared, and only by Search and Gallery). Shell
width is `1240px` on both pages here versus `1440px` on Search. The Profile is the only page using a
`max-width`/`min-width: n+1` seam pair rather than mobile-first `min-width` only. Nothing in either
file targets 390px specifically; nothing addresses 320px reflow or 200 % zoom.

**Gallery, full responsive behaviour:**

| Line | Query | Effect |
|---|---|---|
| 304–306 | `max-width: 520px` | `.profile-menu { width: 260px; right: -8px }` |
| 722–762 | `min-width: 760px` | `:root { --nav-h: 64px }`; `body { font-size: 16px; padding-bottom: 0 }`; `.shell { padding: 0 32px }`; `.nav { padding: 0 28px; gap: 20px }`; `.nav-search { max-width: 460px; margin: 0 auto; height: 38px }`; `.nav-links { display: flex; gap: 4px }`; `.nav-pill { display: inline-flex }`; `.hero { margin: 20px 32px 0; aspect-ratio: 16/9; border-radius: 32px }`; `.hero-card { left: 32px; bottom: 32px; right: auto; width: 440px; padding: 30px }`; `.hero-title { font-size: 48px }`; `.hero-desc { 16px }`; `.section { padding: 72px 0 }`; `.section-title { 36px }`; `.pill-row { padding: 8px 32px 14px }`; `.artists { padding: 72px 0 }`; `.artists-head { margin-bottom: 36px }`; `.artists-scroll { padding: 4px 32px 10px; gap: 18px }`; `.artist-card`/`.artist-avatar`/`.artist-thumb { width/height: 190px }`; `.collections-grid { 1fr 1fr; gap: 18px }`; `.collection { aspect-ratio: 3/2 }`; `.collection h3 { 26px }`; `.photo-grid { repeat(3, 1fr); gap: 14px }`; `.photo.wide { aspect-ratio: 4/3 }`; `.photo.hero-row { grid-column: span 3; aspect-ratio: 21/9 }` (**dead — no element has `.hero-row`**); `.editorial { 1fr 1fr; gap: 56px }`; `.editorial-title { 32px }`; `.footer-row { row }`; `.footer { padding: 56px 32px 40px }`; `.mobile-tabs { display: none }` |
| 764–768 | `min-width: 1100px` | `.hero { aspect-ratio: 16/8 }`; `.hero-title { 56px }`; `.section-title { 42px }` |

Base (<760px): `.photo-grid` is `repeat(2, 1fr); gap: 10px`; `.collections-grid` is one column;
`.editorial` is one column; `.hero` is `aspect-ratio: 4/5`. **The Discover grid never exceeds 3
columns**, so at 1440px it renders three ~380px columns inside a 1240px shell, while Search at the
same width renders 4 masonry columns inside 1440px.

**Profile, full responsive behaviour:**

| Line | Query | Effect |
|---|---|---|
| 134 | `min-width: 1272px` | `.cover { margin-left: auto; margin-right: auto }` — **below 1272px the 1240px-max cover is left-aligned with `margin: 12px 16px 0` while `.shell`/`.section` content is centred, so between ~1256px and 1272px the cover visibly misaligns with everything under it** |
| 568–591 | `max-width: 880px` | `.nav-search { display: none }`; `.cover { aspect-ratio: 16/8; margin-top: 8px }`; `.profile-head { grid-template-columns: 1fr; text-align: center; margin-top: 16px; gap: 14px }`; `.profile-avatar { 104px; justify-self: center; margin-top: -64px }`; `.profile-name { justify-content: center; 24px }`; `.profile-line { justify-content: center }`; `.profile-actions { justify-content: center; padding-bottom: 0 }`; `.profile-body { 1fr; gap: 20px; margin-top: 20px }`; `.series-row { 1fr 1fr }`; **`.series-card:nth-child(3) { display: none }`**; `.albums { 1fr }`; `.grid { repeat(2, 1fr); gap: 6px }` |
| 592–599 | `min-width: 881px` | `.mobile-tabs { display: none }`; `body { padding-bottom: 0 }`; `.grid { repeat(4, 1fr); gap: 14px }` |
| 600–602 | `min-width: 1100px` | `.grid { repeat(4, 1fr) }` — identical to the 881px rule; **dead** |

At 200 % zoom on a 1440px screen (effective 720px) the Profile takes the ≤880px branch: the nav
search disappears entirely, the stats card drops below the bio, and **the third Featured Series card
is hidden with no other route to it** — its "See all ›" link is `href="#"`.

### a.7 Motion and z-index

No `@keyframes`, no `animation`, and **no `prefers-reduced-motion` block** in either file (G8
unchanged). Gallery adds `.btn:active { transform: scale(0.98) }` — the only `:active` state in any
of the three public mockups.

Gallery transitions (14): `.nav-search` `border-color .15s, background .15s`; `.icon-btn`
`background .15s, color .15s`; `.has-tip::after` and `::before` `opacity .18s ease, transform .18s
ease` with `transition-delay: .35s` on show; `.avatar-btn` `transform .12s, box-shadow .15s`;
`.profile-menu` `opacity .18s ease, transform .22s cubic-bezier(.2,.9,.3,1.05)` (**overshoot**);
`.menu-item` `background .12s`; `.btn` `transform .08s ease, background .15s, color .15s,
border-color .15s`; `.pill` `all .15s`; `.collection` `transform .25s ease, box-shadow .25s ease`;
`.collection img` `transform .5s ease`; **`.photo img` `transform .6s ease`** (Ken-Burns on hover,
same as Search); `.photo-meta` `opacity .2s`; `.play-btn` `background .15s, color .15s`.

Profile transitions (9): `.icon-btn`; `.back-btn` `background .12s`; `.btn` `transform .12s,
background .15s, border-color .15s, color .15s`; `.tab` `color .15s`; `.series-card img` `transform
.5s`; `.photo img` `transform .4s`; `.photo .meta` `opacity .2s, transform .2s`; `.photo::after`
`opacity .2s`; `.album` `transform .15s, box-shadow .2s`.

Z-index:

| Page | Layers |
|---|---|
| Gallery | `.nav` **50**; `.hero-img` 0, `.hero::before` 1, `.hero-card` 2; `.collection img` 0, `::after` 1, `.collection-body` 2; `.mobile-tabs` **40**; `.has-tip` **200**; `.profile-menu` **250**; `.photo-meta::before` **−1** |
| Profile | `.nav` **100**; `.profile-head` 2; `.tabs-wrap` **40**; `.mobile-tabs` **80** |

Gallery repeats the Search defect class in reverse: the profile menu (250) correctly sits above the
nav (50), but the mobile tab bar (40) sits *below* the nav (50) — harmless only because they never
co-exist. On the Profile the nav is 100 and the sticky tabs are 40, which is correct; but the same
`.mobile-tabs` component is 40 on Gallery and 80 on Profile.

### a.8 Contrast — pairs new to these pages

Method and caveats as `INVENTORY-search.md` §f.4 and its Appendix; the token luminances there apply
unchanged. Computed additions:

| Value | sRGB | Relative luminance |
|---|---|---|
| `oklch(0.52 0.18 255)` (Gallery btn hover) | `#0066cd` | 0.1383 |
| `oklch(0.54 0.18 255)` (Profile btn hover) | `#006cd3` | 0.1543 |
| `oklch(0.52 0.18 25)` (danger) | `#ba2b2e` | 0.1236 |
| `oklch(0.48 0.20 25)` (danger hover) | `#b30018` | 0.0970 |
| `oklch(0.72 0.17 150)` (`.avail-dot`) | `#3fc168` | 0.4028 |

| Pair | Ratio | Verdict |
|---|---|---|
| `#0066cd` on white (Gallery `.btn-primary:hover` **background**, white text) | **5.58:1** | pass |
| `#006cd3` on white (Profile `.btn-primary:hover`) | **5.14:1** | pass |
| white on `--accent` (`.btn-primary` **resting**, Gallery 14px/600, Profile 13.5px/600) | **4.34:1** | **FAIL** — neither size qualifies as large text (needs 18.66px bold or 24px) |
| `oklch(0.52 0.18 25)` on white (`.menu-item.danger`, "Sign Out", 13.5px) | 6.05:1 | pass |
| `oklch(0.72 0.17 150)` on white (`.avail-dot`) | **2.32:1** | **FAIL 1.4.11** if the dot ever carries meaning alone; here it is paired with text, so it is decorative and `aria-hidden="true"` is set |
| `--accent` on white / on `--bg` | 4.34 / 4.16 | **FAIL** — hits `.link-inline` (13px/600, six instances), `.back-btn` (14px/500), `.play-row span` (14px/600), `.artist-card .link-inline` (**11px** uppercase), the website chip (13px), `.mobile-tabs .tab.active` (10px) |
| `--ink-3` on `--bg` | 4.46 | **FAIL** — `.section-sub` (14px, ×5), `.profile-handle` (14px), `.page-end` (12px), `.tab` (14px, on the 85 %-`--bg` glass) |
| `--ink-3` on `--bg-tint` | 4.14 | **FAIL** — `.artist-style` (13px), the entire Gallery footer (`.footer-copy`, `.footer-links`), both nav-search placeholders |
| `--ink-3` on white | 4.65 | passes by 0.15 — `.album-meta` (12.5px), `.stat .l` (11px), `.profile-stat .l` (10.5px), `.mi-aside` (11px) |
| `--line` on white / on `--bg-tint` | 1.35 / 1.20 | **FAIL 1.4.11** — every `.btn-secondary`, `.pill`, `.tool-group`, `.sort`, `.view-toggle`, `.stats-card` and `.album` boundary |

**Gallery-specific focus-ring measurement:** `.avatar-btn:focus-visible { box-shadow: 0 0 0 3px
color-mix(in oklab, var(--accent) 35%, transparent) }` over white ≈ `#a3c9ee`, about **1.85:1**
against white. Better than Search's 22 % mix (≈1.28:1) and still below the 3:1 that 1.4.11 requires
of a focus indicator.

**Unmeasurable by construction:** all text on photographs — `.hero-card` is glass over the hero
image; `.collection-body` (white `h3` + `opacity: .8` curator + a `rgba(255,255,255,.18)` chip);
`.photo-meta` / `.photo .meta` (white 12px over `rgba(0,0,0,.55)` and `rgba(10,12,18,.55)` scrims);
`.series-label` (white over `rgba(10,12,18,.72)` from 45 %); `.badge-new` (white on
`rgba(0,0,0,.45)`); `.heart` (white on `rgba(0,0,0,.3)` / `.35`). `VZ-A11Y-001` requires contrast
measured "over real backings", which means over real uploaded photographs, not these fixtures.

---

## b. `Lumen Atlas Gallery.html` — purpose and layout regions

### b.0 Purpose

The instance home page: a logged-in visitor's editorial front door. It presents one featured
editorial work, a category browser, a curated people carousel, four curated themed sets, a grid of
recent community uploads, one long-form editorial article with audio, and a site footer. It is
**not** a filtered explore surface — there is no facet UI, no result count, no sort, and no query
state. `<title>Lumen Atlas — Photography, discovered</title>`.

Outer containers: `.shell { max-width: 1240px; margin: 0 auto; padding: 0 16px }` (→`0 32px`
≥760px). The hero, the pill row, the artists strip and the footer all break out of `.shell` and use
their own horizontal padding. **There is no `<main>` landmark and no skip link.** Landmarks present:
`header`, `nav` ×2 (`aria-label="Primary"`, `aria-label="Mobile navigation"`), `section` ×5,
`footer`. The `role="menu"` panel is a third interactive region.

### G1. Top nav — `<header class="nav">` (774–876)

See §a.3 for the shell delta. Controls, in DOM order:

| # | Control | Element | Visible content | Evident intent |
|---|---|---|---|---|
| 1 | Brand | `<a class="brand" href="#">` (775) | 22×22 `.brand-mark` (`aria-hidden`, radius 7px, `radial-gradient(circle at 30% 30%, oklch(0.75 0.15 80), transparent 60%)` over `linear-gradient(135deg, oklch(0.58 0.18 255), oklch(0.45 0.14 285))`) + `<b>Lumen</b> <span>Atlas</span>` | Home. **`href="#"` — the logo on the home page links nowhere** |
| 2 | Search field | `<label class="nav-search" aria-label="Search">` wrapping a 16×16 Search SVG + `<input placeholder="Search photographers, places, moods…">` (780–784) | placeholder only | Issue a query. **No `type`, `name`, `id`, `aria-label`, no `<form>`, no submit control, no Enter handler.** The wrapping `<label>` has no text content, so the input's accessible name falls back to the placeholder |
| 3 | `⌘K` hint | inline-styled `<span>` (783) | `⌘K` | Advertises a command-palette shortcut. **Not implemented anywhere** |
| 4 | Discover | `<a class="nav-link" href="#">` (787) | `Discover` | Explore. Hidden <760px |
| 5 | Collections | `<a class="nav-link" href="#">` (788) | `Collections` | Collections index. Hidden <760px |
| 6 | Artists | `<a class="nav-link" href="#">` (789) | `Artists` | People directory. Hidden <760px |
| 7 | Surprise | `<a class="nav-pill" href="#">` (790–793) | gem/diamond glyph + `Surprise` | Random photo. 34px pill, `1px solid var(--line)`, 11px/600/.12em uppercase. Hidden <760px |
| 8 | Notifications | `<button class="icon-btn has-tip" aria-label="Notifications" data-tip="Notifications">` (797) | icon only (Bell) | Notification panel. **No badge, no unread count** |
| 9 | Upload | `<a class="icon-btn has-tip" href="Upload Studio.html" aria-label="Upload a photo" data-tip="Add a photo">` (800) | icon only (Upload) | Start an upload. **Accessible name "Upload a photo" ≠ tooltip "Add a photo"** |
| 10 | Account | `<button class="avatar-btn" id="avatarBtn" aria-label="Your profile" aria-haspopup="menu" aria-expanded="false">` + `<span class="avatar">MK</span>` (804–806) | initials `MK`, 30×30 gradient circle | Open the account menu |

### G2. Account menu — `<div class="profile-menu" id="profileMenu" role="menu" aria-labelledby="avatarBtn">` (808–873)

New to these pages; Search has no equivalent. `position: absolute; top: calc(100% + 10px); right: 0;
width: 280px`, background `color-mix(in oklab, white 92%, transparent)` + `saturate(180%)
blur(28px)`, `border-radius: 16px`, four-layer shadow, `z-index: 250`, `padding: 6px`,
`transform-origin: top right`. Closed state: `opacity: 0; transform: translateY(-6px) scale(.98);
pointer-events: none`.

**Data shown**

| Field | Value | Element |
|---|---|---|
| Avatar | `MK`, 44×44 | `.profile-head .avatar` |
| Display name | `Marie Kowalski` | `.profile-name` (14.5px/600) |
| Handle · role | `@marie.kowalski · Curator` | `.profile-handle` (12.5px, `--ink-3`) |
| Photos | `142` | `.profile-stat .n` |
| Series | `18` | `.profile-stat .n` |
| Followers | `2.4k` | `.profile-stat .n` |

`.profile-stats` is a 3-column grid, `gap: 2px`, `background: color-mix(in oklab, var(--bg-tint)
70%, transparent)`, radius 12px, labels 10.5px/.06em uppercase. **The "142 Photos" stat is
contradicted fourteen lines later by the menu item "My Photos · 312".** "18 Series" names an entity
Vizra does not have.

**Controls** — `.menu-item` = `all: unset`, flex, `gap: 11px`, `padding: 9px 10px`, radius 10px,
13.5px, 20px icon slot at `--ink-2`; hover/focus-visible = `color-mix(in oklab, var(--accent) 10%,
transparent)` background + `--accent-ink` text.

| # | Label | Element | Aside | Icon |
|---|---|---|---|---|
| 11 | `View Profile` | `<a href="Artist Profile.html" role="menuitem">` | — | User |
| 12 | `My Photos` | `<a href="My Photos.html" role="menuitem">` | `312` | LayoutGrid |
| 13 | `Albums` | `<a href="My Albums.html" role="menuitem">` | — | **Bookmark** |
| 14 | `Insights` | `<a href="Photo Insights.html" role="menuitem">` | — | LineChart |
| 15 | `Upload Studio` | `<a href="Upload Studio.html" role="menuitem">` | — | Image |
| 16 | `Edit Profile` | `<a href="Edit Profile.html" role="menuitem">` | — | Pencil |
| 17 | `Account Settings` | `<a href="Account Settings.html" role="menuitem">` | `⌘,` | Settings |
| 18 | `Notifications & Privacy` | `<a href="Notifications.html" role="menuitem">` | — | Bell |
| 19 | `Help & Feedback` | `<button class="menu-item" role="menuitem">` | — | CircleHelp |
| 20 | `Sign Out` | `<button class="menu-item danger" role="menuitem">` | — | LogOut, `oklch(0.52 0.18 25)` |

Three `.menu-sep` (1px, `color-mix(--line 70%)`, `margin: 2px 4px`) group them 5 / 4 / 1.

**Absent from this menu but required by `ui-controls.json` `shell.nav.account`** ("library, albums,
**favorites**, settings, sign out"): a Favorites entry (`VZ-FAVORITE-001`, `/u/{username}/favorites`).
Also absent: Blocks (`VZ-BLOCK-001`, `/settings/blocks`), API keys (`VZ-AUTH-008`), admin entry for
owner/admin roles (`VZ-ADMIN-001`), theme toggle, language.

The Bookmark glyph is used here for **Albums** and again 280 lines later for the mobile **Saved**
tab — one glyph, two unrelated meanings, in one shell.

### G3. Hero — `<section class="hero" aria-label="Featured work">` (879–893)

`margin: 12px 16px 0` (→`20px 32px 0`), `border-radius: var(--radius-xl)` 28px (→32px),
`overflow: hidden`, `background: #0e1820`, `isolation: isolate`.
**`aspect-ratio: 4/5` → `16/9` at ≥760px → `16/8` at ≥1100px** — three different crops of one
photograph, chosen by viewport, via `.hero-img { position: absolute; inset: 0; object-fit: cover }`.

`.hero::before` = `linear-gradient(180deg, transparent 35%, rgba(6,14,22,.55) 90%)`, z-index 1.

`.hero-card` (z-index 2): `left/right: 16px; bottom: 16px; padding: 22px` → `left: 32px; bottom:
32px; right: auto; width: 440px; padding: 30px` at ≥760px. Radius `var(--radius-lg)` 22px,
background `color-mix(in oklab, white 80%, transparent)` + `saturate(180%) blur(24px)`, `box-shadow:
var(--shadow-md), inset 0 0 0 1px rgba(255,255,255,.5)` — **glass over a photograph**.

**Data shown**

| Field | Value |
|---|---|
| Image | `https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1800&q=80` |
| Alt | `Misty mountain range at dawn` |
| Eyebrow | `Featured Series` (11px/600/.14em uppercase, `--accent-ink`) |
| Title | `The Silence of High Places` — `<h1 class="hero-title">`, 32px → 48px → 56px, 700, `-0.03em`, `text-wrap: balance` |
| Description | `An immersive study of stillness in the Northern Cascades — twelve frames captured during the blue hour of mid‑winter by Marie Okafor.` — 15px→16px, `--ink-2`, `max-width: 46ch`, `text-wrap: pretty` |
| Frame count | `twelve frames` (prose only) |
| Author | `Marie Okafor` (prose only — **not a link, not a field**) |

**The page's only `<h1>` is the title of one editorial item**, not the site or the page.

| # | Control | Element | Intent |
|---|---|---|---|
| 21 | `Read the Narrative` + ArrowRight | `<a class="btn btn-primary" href="#">` | Open a long-form written piece attached to the series |
| 22 | `View Collection` | `<a class="btn btn-secondary" href="#">` | Open the set of twelve frames |

`.btn`: 44px, radius 999px, 14px/600; `.btn-primary` `--accent`/white + `box-shadow: 0 6px 20px -8px
oklch(0.58 0.18 255 / .55)`; `.btn-secondary` white on `--line`. `.btn:active { transform:
scale(0.98) }`.

### G4. Category pill row — `<div class="pill-row" role="tablist" aria-label="Browse categories">` (896–907)

`display: flex; gap: 8px; overflow-x: auto; overflow-y: hidden; padding: 4px 16px 12px` (→`8px 32px
14px`), `scroll-snap-type: x proximity`, `scrollbar-width: none` + `::-webkit-scrollbar { display:
none }`, `-webkit-overflow-scrolling: touch`, inline `style="margin-top:22px;"`.

`.pill`: 36px, radius 999px, `background: var(--bg-elev)`, `1px solid var(--line)`, 13.5px/500,
`--ink-2`, `scroll-snap-align: start`, `flex-shrink: 0`, `transition: all .15s`; `.active` =
`--ink` background, white text, `--ink` border.

| # | Label | State |
|---|---|---|
| 23 | `For You` | `.active` |
| 24 | `Landscapes` | — |
| 25 | `Portraiture` | — |
| 26 | `Architecture` | — |
| 27 | `Street` | — |
| 28 | `Analog` | — |
| 29 | `Minimalism` | — |
| 30 | `Wildlife` | — |
| 31 | `Night Sky` | — |
| 32 | `Abstract` | — |

No counts (Search's scope chips had them). `.pill .dot` (a 5px `currentColor` circle at `opacity:
.4`) is styled at line 459 and **used by no element** — dead CSS.

`role="tablist"` on a container whose ten children are plain `<button>`s with **no `role="tab"`, no
`aria-selected`, no `aria-controls`, no roving `tabindex`, and no `role="tabpanel"` anywhere on the
page** — the same invalid-ARIA defect as Search's `.filter-row` and `.view-group`. A horizontal
scroll container with the scrollbar hidden and no keyboard scroll affordance and no `tabindex="0"`.

### G5. Artists strip — `<section class="artists">` (910–948)

`background: var(--bg-tint); padding: 48px 0` (→72px), `border-top`/`border-bottom` `1px solid
var(--line-2)`.

`.artists-head.shell` — `text-align: center; margin-bottom: 28px` (→36px):
`<span class="eyebrow">Visionaries</span>` · `<h2 class="section-title">Artist Showcases</h2>`
(26px→36px/700) · `<p class="section-sub">Photographers shaping the way we see this month.</p>`.

`.artists-scroll` — `display: flex; gap: 14px` (→18px), `padding: 0 16px 8px` (→`4px 32px 10px`),
`overflow-x: auto`, scrollbar hidden, no keyboard affordance.

**Seven `.artist-card` at `width: 160px` (→190px). Only three are people.**

| # | Card | Contents |
|---|---|---|
| 1 | Person | `.artist-avatar` 160/190px **circle**, `object-fit: cover`, `background: var(--line-2)`, `box-shadow: var(--shadow-sm), inset 0 0 0 1px rgba(255,255,255,.5)`; `<img alt="">` · `.artist-name` **Alex Rivera** (15px/600) · `.artist-style` **Urban Brutalism** (13px `--ink-3`, `margin-top: -6px`) · `<a href="#" class="link-inline">View Profile ›</a>` (**11px**/.12em uppercase, `--accent`) |
| 2 | Photo | `.artist-thumb` 160/190px square, `border-radius: 28px`, `background: var(--ink)`, `<img alt="Architectural study">`. **No name, no link, no control** |
| 3 | Photo | `.artist-thumb`, `alt="City light trails"` |
| 4 | Photo | `.artist-thumb`, `alt="Still life"` |
| 5 | Photo | `.artist-thumb`, `alt="Solitary tree"` |
| 6 | Person | avatar (`alt=""`) · **Elena Vogel** · **Organic Minimalism** · View Profile › |
| 7 | Person | avatar (`alt=""`) · **Hana Mori** · **Color Theory** · View Profile › |

| # | Control | Element |
|---|---|---|
| 33 | `View Profile ›` ×3 | `<a href="#" class="link-inline">` |

**Fields per person card:** avatar URL, display name, a one-line "style" string, a profile link.
**No handle, no photo count, no follower count, no Follow button** (Search's artist cards had a
Follow control; this one does not). The avatar and the name are inert — only the 11px link is
reachable. The four bare photo thumbnails are inert decoration sitting inside a list of people.

The literal `›` character is the disclosure glyph in all three links here and in `Browse all ›`
below — a text character, not an icon, exactly as Search's `.rc .arr`.

### G6. Collections — `<section class="section shell">` (951–1001)

`.section { padding: 48px 0 }` (→72px). `.section-head`: flex, `align-items: flex-end`,
`justify-content: space-between`, `gap: 24px`, `margin-bottom: 20px`.

- `<span class="eyebrow">Curated Series</span>` + `<h2 class="section-title"
  style="margin-top:6px;">Thematic Collections</h2>`
- | # | Control | Element |
  |---|---|---|
  | 36 | `Browse all ›` | `<a href="#" class="link-inline">` |

`.collections-grid`: `grid-template-columns: 1fr; gap: 14px` → `1fr 1fr; gap: 18px` at ≥760px.
**Never more than two columns**, so at 1440px each card is ~600px wide.

`.collection` = `<a href="#">`: `aspect-ratio: 4/3` → **`3/2`** at ≥760px, radius 22px, `background:
#111`, `isolation: isolate`, `--shadow-sm`; hover `translateY(-2px)` + `--shadow-md`.
`img { position: absolute; inset: 0; object-fit: cover; transition: transform .5s ease }`, hover
`scale(1.04)`. `::after` = `linear-gradient(180deg, transparent 40%, rgba(0,0,0,.7) 100%)`.
`.collection-body`: absolute `left/right: 20px; bottom: 18px`, white, flex, `align-items: flex-end`,
`justify-content: space-between`.

**Fields per collection card**

| # (control 37, ×4) | Title (`h3`, 22px→26px/700) | Curator (`.collection-curator`, 12px, `opacity: .8`) | Chip (`.chip`, 28px pill, `rgba(255,255,255,.18)` + `blur(12px)`, `1px solid rgba(255,255,255,.22)`, white 11px/600) | `img alt` |
|---|---|---|---|---|
| 1 | `Geometric Shadows` | `Curated by Marcus Thorne` | `24 images` | `Geometric shadows` |
| 2 | `Pulse of the Forest` | `Curated by Elena Vogel` | `18 images` | `Pulse of the forest` |
| 3 | `Quiet Thresholds` | `Curated by Jun Park` | `31 images` | `Quiet thresholds` |
| 4 | `After the Rain` | `Curated by Sara Linde` | `16 images` | **`Reflections`** — disagrees with its own title |

No privacy marker, no date, no link to the curator's profile. All four `href="#"`.

### G7. Discover grid — `<section class="section shell" style="padding-top: 0;">` (1004–1058)

`.discover-head`: flex, space-between, `align-items: center`, `margin-bottom: 18px`.
Left: `<h2 class="section-title">Discover Latest</h2>` + `<p class="section-sub">Fresh uploads from
the community, refreshed hourly.</p>`.
Right: an inline-styled `<div style="display:flex; gap:8px; align-items:center;">` holding:

| # | Control | Element | Intent |
|---|---|---|---|
| 38 | Layout: Grid | `<button class="tool-btn active" aria-label="Grid">` inside `<div class="tool-group" role="tablist" aria-label="Layout">` | density/layout switch |
| 39 | Layout: Mosaic | `<button class="tool-btn" aria-label="Mosaic">` | density/layout switch |
| 40 | Filter | `<button class="tool-btn" style="background:var(--bg-elev);border:1px solid var(--line);width:36px;height:36px;border-radius:50%;" aria-label="Filter">` (1019) | open a filter surface. **Inline-styled, outside the group, no panel, and not bound by the script** |

`.tool-group`: `inline-flex`, `--bg-elev`, `1px solid var(--line)`, radius 999px, `padding: 3px`,
`gap: 2px`; `.tool-btn` 34×34, `--ink-3`; `.active` = `--ink`/white.
`role="tablist"` with no `role="tab"` children — same defect as G4.

`.photo-grid`: `display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px` → `repeat(3, 1fr);
gap: 14px` at ≥760px. **No further step at 1100px or beyond.**

`.photo` = `<a href="#">`: `position: relative`, radius `var(--radius-md)` 16px, `overflow: hidden`,
`background: var(--line-2)` (the placeholder while the image loads), `aspect-ratio: 1`,
`--shadow-sm`. Modifiers: `.tall { aspect-ratio: 3/4 }`; `.wide { grid-column: span 2; aspect-ratio:
16/10 }` → `4/3` at ≥760px; `.hero-row { grid-column: span 3; aspect-ratio: 21/9 }` declared at
≥760px and **used by nothing** — dead CSS.

`.photo img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
transition: transform .6s ease }`, hover `scale(1.04)`. **No `loading="lazy"` on any of the nine
images** (Search's cards had it). Every photograph is hard-cropped into a layout-chosen box.

`.photo-meta`: absolute `left/bottom/right: 10px`, flex space-between, white, 12px,
**`opacity: 0`, revealed only by `.photo:hover`** — there is **no `:focus-within` fallback**, unlike
Search. Its `::before` paints `linear-gradient(180deg, transparent, rgba(0,0,0,.55))` inset
`-10px/-10px/-10px/-20px` at `z-index: -1`.

**Fields per photo card**

| Field | Element | Present on |
|---|---|---|
| Permalink | `<a class="photo" href="#">` | all 9 (all `#`) |
| Image URL | `<img src="https://images.unsplash.com/…?auto=format&fit=crop&w=900&q=80">` (1400 for `.wide`) | all 9 |
| Alt text | `alt="…"` | **all 9 have real alt text** |
| Intrinsic aspect | not transmitted; the class decides the box | — |
| Author handle | `<span class="author">` (12px/500, `text-shadow: 0 1px 2px rgba(0,0,0,.4)`) | all 9 — **a `<span>`, not a link** |
| Favourite count | `<span class="heart">` — `rgba(0,0,0,.3)` + `blur(8px)`, radius 999px, `padding: 4px 8px`, 11px/600, an 11×11 **filled** `<svg fill="currentColor">` Heart | all 9 — **a `<span>`, not a button. There is no favourite control anywhere on this page** |
| Title / caption | — | **none** |
| Date, badge, licence, privacy marker, safety marker | — | **none** |

| # | modifier | alt | author | hearts |
|---|---|---|---|---|
| 1 | — | `Sun rays over hills` | `@milo_fields` | `1.2k` |
| 2 | `tall` | `Night sky milky way` | `@astra.maps` | `3.4k` |
| 3 | — | `Abstract silk flow` | `@noir.studio` | `840` |
| 4 | — | `Mountain reflection` | `@marie_okafor` | `2.1k` |
| 5 | — | `Wheat field at golden hour` | `@june_harvest` | `976` |
| 6 | — | `Layered blue mountains` | `@highland.ink` | `1.9k` |
| 7 | `wide` | `Forest path` | `@elena.vogel` | `4.6k` |
| 8 | — | `Architectural geometry` | `@alex_rivera` | `1.4k` |
| 9 | — | `Lake at dusk` | `@dusk.files` | `2.7k` |

| # | Control | Element |
|---|---|---|
| 41 | Open photo ×9 | `<a class="photo" href="#">` |
| 44 | `Load more` | `<button class="btn btn-secondary">` inside an inline-styled centring `<div>` (1055–1057) |

No pager hint, no total, no `aria-live`, no infinite-scroll sentinel, no spinner.

### G8. Editorial — `<section class="section shell" style="padding-top:16px;">` (1061–1078)

`.editorial`: `grid-template-columns: 1fr; gap: 22px; align-items: center` → `1fr 1fr; gap: 56px`
at ≥760px.

- `.editorial-img`: `aspect-ratio: 1`, radius 22px, `background: #222`, `--shadow-md`; `img` 100 %
  `object-fit: cover`. `src=".../photo-1517245386807-bb43f82c33c4?…&w=1200"`, `alt="Desk with laptop
  and notebook"`.
- `<span class="eyebrow">Editorial Journal</span>`
- `<h2 class="editorial-title">The Art of Seeing: a conversation with Alex Rivera</h2>` (26px→32px/700)
- `<p class="editorial-desc">We sit down with the master of urban brutalism to discuss the
  intersection of concrete architecture and the human soul. Rivera shares his process for finding
  beauty in the overlooked corners of the metropolis.</p>`
- `.play-row` (`inline-flex`, `gap: 12px`, colour `--accent`):

| # | Control | Element | Intent |
|---|---|---|---|
| 45 | Play interview | `<button class="play-btn" aria-label="Play interview">` — 42px circle, `1.5px solid var(--accent)`, filled Play triangle 14px with `margin-left: 2px`; hover fills accent | Start a 28-minute **audio** interview |

`<span>Listen to the interview · 28 min</span>` (14px/600, inherits `--accent`).

**This region is an editorial article with an attached audio programme.** Vizra has no article
entity beyond owner-authored custom pages (`VZ-PAGE-001`) and **no audio media type at all** —
`VZ-MEDIA-002`'s matrix is JPEG/PNG/GIF/WebP/AVIF/BMP and `VZ-MEDIA-005` is MP4/MOV/WebM video.

### G9. Footer and G10. Mobile tab bar

See §a.5 and §a.4.

| # | Control | Element |
|---|---|---|
| 46–50 | `About` / `Terms` / `Privacy` / `Licensing` / `Contact` | `<a href="#">` ×5 |
| 51 | Footer Share | `<a class="icon-btn" href="#" aria-label="Share">` (Share2 node-graph glyph) |
| 52 | Footer Email | `<a class="icon-btn" href="#" aria-label="Email">` (Mail) |
| 53 | Mobile: Home | `<button class="tab active" aria-label="Home">` |
| 54 | Mobile: Explore | `<button class="tab" aria-label="Discover">` |
| 55 | Mobile: Upload | `<a class="tab upload" href="Upload Studio.html" aria-label="Upload photo">` |
| 56 | Mobile: Saved | `<button class="tab" aria-label="Saved">` |
| 57 | Mobile: You | `<a class="tab" href="Artist Profile.html" aria-label="Profile">` |

A "Share" affordance in a site footer with no target and no share sheet is meaningless as drawn.

### b.11 What the inline script does (1124–1162)

~38 lines, three units, **no data, no fetch, no state model, no templates**.

1. **Category pills** (1126–1129). `document.querySelectorAll('.pill')` → each click removes
   `.active` from all pills and adds it to the clicked one. **No grid on the page changes**; the nine
   Discover cards are identical whichever category is "selected".
2. **Layout toggle** (1131–1134). `.tool-group .tool-btn` → within `b.parentElement`, clear
   `.active`, set on clicked. Purely cosmetic; `.photo-grid` never changes. Scoped to `.tool-group`,
   so the standalone `aria-label="Filter"` button (1019) is deliberately **not** bound.
3. **Account menu** (1137–1161), an IIFE. `setOpen(open)` toggles `.open` on `#avatarBtn` and
   `#profileMenu` and mirrors it into `aria-expanded`. The button click `stopPropagation()`s and
   toggles. A document click outside both nodes closes. **A document `keydown` closes on `Escape` —
   the only Escape handler in any of the three public mockups.** Every `.menu-item` click closes it.
   - Missing: focus move into the menu on open, focus return to the trigger on close, roving
     `tabindex` / Home / End / arrow-key navigation required by `role="menu"`, and `inert`/`hidden`
     on the closed panel — so **all ten menu items stay in the tab order while the menu is shut**.

**Never wired:** the search input (no `keydown`, no submit), the `⌘K` hint, Notifications, all four
nav links including Surprise, the standalone Filter button, both hero buttons, all three
`View Profile ›` links, `Browse all ›`, all four collection cards, all nine photo cards, all nine
heart counts (they are spans), `Load more`, `Play interview`, all five footer links, both footer
social links, and three of the five mobile tabs.

**Mock-data shape: none.** There is no array, no object, no template and no fetch. The nine photos,
four collections, seven artist cards, three menu stats and every count are hand-written HTML
literals. The closest thing to a data contract is the per-card field set in G7 and G6, reconstructed
in §j.

### b.12 States

**Present**

| State | Where |
|---|---|
| Hover | `.icon-btn`, `.nav-link`, `.nav-pill`, `.pill`, `.collection` (+ its `img`), `.photo img`, `.photo-meta` reveal, `.btn-primary`, `.btn-secondary`, `.play-btn`, `.menu-item`, `.footer-links a`, `.has-tip` tooltip |
| **Active/pressed (visual)** | `.btn:active { transform: scale(0.98) }` — the only `:active` in any public mockup |
| **Focus-visible** | **three rules** — `.avatar-btn:focus-visible` (`0 0 0 3px` accent-35 %), `.menu-item:focus-visible` (accent-10 % background), `.has-tip:focus-visible` (tooltip shows). Search has **zero** |
| Selected | `.pill.active`, `.tool-btn.active`, `.mobile-tabs .tab.active` |
| Open | `.profile-menu.open`, `.avatar-btn.open` (accent-35 % ring) |
| Image placeholder | `.photo`/`.artist-avatar` `var(--line-2)`; `.hero` `#0e1820`; `.collection` `#111`; `.editorial-img` `#222` — flat blocks, not skeletons |

**Absent — and required by `DESIGN_BRIEF.md` ("loading/empty/error/success/disabled states,
light/dark modes, 200% zoom, reduced motion, keyboard navigation, and responsive behavior") and
`VZ-A11Y-001`**

| Missing state | Consequence for the implementer |
|---|---|
| **Empty / zero-content** | **The single most important missing state.** A freshly installed Vizra instance has 0 photos, 0 collections, 0 featured series and 0 "artists". This page is the first thing an operator sees after `vizra setup`, and the mockup presumes a mature populated instance. Nothing is drawn for a hero with nothing to feature, an empty Discover grid, an empty artists strip, or an instance with one user |
| **Anonymous / logged-out** | The nav always shows a signed-in avatar and a 10-item account menu. No sign-in / sign-up path exists anywhere on the page. `VZ-AUTH-005` registration policy (open / approval / invite / closed), `VZ-ADMIN-003` site-wide privacy mode and `VZ-EXPLORE-001`'s negative case ("Guest with explore disabled → 403 and nav hidden") all change this page and none is drawn |
| **Loading / skeleton** | No grid skeleton, no card placeholder ratio, no spinner on `Load more`, no pending state on anything |
| **Error** | No failed-fetch state for any of the five content regions |
| **Success / disabled / busy** | No `:disabled`, no `aria-busy`, no `aria-pressed`, no toast, no optimistic/settled distinction |
| **NSFW / safety blur** | `VZ-NSFW-001` requires viewer-side filtering and blur in listings. Nothing on any of the 9 photo cards, 4 collection cards or 7 artist cards |
| **Privacy / visibility marker** | `VZ-PRIVACY-001/002` — no unlisted/private/hidden-from-search indicator anywhere |
| **Dark mode** | Zero occurrences of `prefers-color-scheme`, `color-scheme`, `[data-theme]` or a second token block; 19 hard-coded `white` literals (G7 unchanged) |
| **Reduced motion** | No `prefers-reduced-motion`; the 0.6 s `.photo img` scale, the 0.5 s `.collection img` scale and the `cubic-bezier(.2,.9,.3,1.05)` menu overshoot all run regardless |
| **Focus for most controls** | `.pill`, `.tool-btn`, `.photo`, `.collection`, `.btn`, `.nav-link`, `.nav-pill`, `.link-inline`, `.play-btn`, footer links and all five mobile tabs rely on the UA default ring; `* { -webkit-tap-highlight-color: transparent }` removes the touch hint |

### b.13 Accessibility observations (Gallery)

**Non-button click targets and interactive nesting**

| Issue | Location |
|---|---|
| `<button class="clear">`-style nesting is gone, but the search `<input>` still sits inside `<label class="nav-search" aria-label="Search">` whose `aria-label` names the *label*, not the control | 780–784 |
| `.artist-card` name and avatar are inert `<div>`s | 917–947 — only the 11px "View Profile ›" is reachable |
| Four `.artist-thumb` cards are entirely inert | 923–934 |
| `.photo-meta .author` is a `<span>` | ×9 — the author is displayed but not navigable |
| `.heart` is a `<span>` | ×9 — reads as a favourite control, is a count |
| `<a href="#">` on 31 of 42 anchors | brand, 3 nav links, Surprise, both hero buttons, 3 View Profile, Browse all, 4 collections, 9 photos, 5 footer links, 2 footer social |

**Missing names, roles and states**

- The search input has **no `type`, `name`, `id` or `aria-label`**; its only accessible name is the
  placeholder, which disappears on input and sits at 4.14:1 on `--bg-tint`.
- `role="tablist"` on `.pill-row` (896) and `.tool-group` (1011) with **children that have no
  `role="tab"`**, no `aria-selected`, no `aria-controls`, no roving `tabindex`, and **no
  `role="tabpanel"` anywhere in the document**. Invalid ARIA that is worse than none.
- `role="menu"` on `.profile-menu` with `role="menuitem"` children but **no keyboard menu behaviour**
  and **no `tabindex="-1"` management**; the closed menu keeps 10 items in the tab order.
- **No `aria-pressed`** on `.pill`, `.tool-btn` or any mobile tab.
- **No `aria-current`** on `.mobile-tabs .tab.active`.
- `aria-label="Discover"` on a tab whose visible text is `Explore` and whose glyph is a magnifier;
  `aria-label="Profile"` on a tab whose visible text is `You` — two WCAG 2.5.3 Label in Name
  failures.
- `aria-label="Upload a photo"` with `data-tip="Add a photo"` — the tooltip and the accessible name
  say different things for one control.
- **No `aria-live`** for `Load more`, for the pill "filter" or for the layout toggle.
- **No `<main>`, no skip link.** Landmarks: `header`, `nav` ×2, `section` ×5, `footer`.
- **35 inline `<svg>` elements; exactly one `aria-hidden` in the whole file** (on `.brand-mark`, a
  `<span>`, not an SVG). `DESIGN_BRIEF.md`: "keep its redundant decorative SVG hidden from assistive
  technology."
- `.hero` carries `aria-label="Featured work"` on a `<section>`, which is correct; `.artists`,
  `.collections` and the Discover section carry none, so they are unlabelled regions.

**Hover-only meaning**

`.photo-meta` is `opacity: 0` and revealed **only** by `.photo:hover` — no `:focus-within`, unlike
Search. On touch there is no hover, so on every phone **the author handle and the favourite count of
all nine cards are invisible and unreachable**. The `.has-tip` tooltips are redundant with
`aria-label` (acceptable), except where the two disagree.

**Keyboard order and scroll containers**

`.pill-row` and `.artists-scroll` are horizontal scroll containers with `scrollbar-width: none`, no
`tabindex="0"` and no keyboard scroll affordance; when their content overflows, the tail is
unreachable by keyboard. The closed `.profile-menu` is `opacity: 0; pointer-events: none` but never
`hidden`/`inert`, so Tab passes through ten invisible menu items. `.photo-grid` is a CSS grid in DOM
order, so tab order and reading order agree — better than Search's multi-column masonry.

---

## c. `Artist Profile.html` — purpose and layout regions

### c.0 Purpose

A single member's public profile: identity, bio, statistics, a follow/message/share action bar, a
tabbed content switcher, three pinned "series", ten recent photographs and three albums. The
mockup draws **exactly one view**: a signed-in stranger looking at a populated, verified,
commissions-available photographer. `<title>Alex Rivera — Lumen Atlas</title>`.

Container: `.shell { max-width: 1240px; padding: 0 16px }` is declared (line 52) but **used by
nothing**; each region re-implements `max-width: 1240px; margin: 0 auto; padding: 0 16px`
independently (`.back-row`, `.cover`, `.profile-head`, `.profile-body`, `.tabs`, `.section`,
`.page-end`) — **seven copies of the same container recipe**. **There is no `<main>` and no skip
link.** Landmarks: `header`, `section` ×4, `aside` ×1, `nav` ×1. The cover is a bare `<div>`.

### P1. Top nav — `<header class="nav">` (608–628)

See §a.3.

| # | Control | Element | Intent |
|---|---|---|---|
| 1 | Brand | `<a class="brand" href="Lumen Atlas Gallery.html">` (609) | Home. **A real link**, unlike Gallery's `href="#"` |
| 2 | Search field | `<label class="nav-search" aria-label="Search">` + `<input placeholder="Search photographers, places, moods…">` (614–617) | Query. **No `type`/`name`/`id`/`aria-label`, no form, no submit, no `:focus-within` rule at all, and `display: none` below 881px** |
| 3 | Notifications | `<button class="icon-btn" aria-label="Notifications">` (620) | Panel. No badge |
| 4 | Upload | `<button class="icon-btn" aria-label="Upload">` (623) | Uploader. **A dead `<button>`; Gallery's is a real `<a>`** |
| 5 | Account | `<span class="avatar">MK</span>` (626) | Account menu. **An inert `<span>` with no `aria-label`, no role, no menu — not focusable, not activatable** |

The `.brand-mark` here is `border-radius: 6px` with `linear-gradient(135deg, oklch(0.78 0.09 50),
oklch(0.55 0.18 260))` and `box-shadow: inset 0 -1px 2px rgba(255,255,255,.5), 0 1px 2px
rgba(17,22,40,.1)` — **a different brand mark from Gallery's** (radius 7px, radial + linear,
different stops, different shadow). `.brand-name` is 15px/500 here, 16px/600 with `--font-display`
on Gallery.

### P2. Back row — `<div class="back-row">` (631–636)

`max-width: 1240px; margin: 14px auto 0; padding: 0 16px; display: flex; gap: 6px`.

| # | Control | Element | Intent |
|---|---|---|---|
| 6 | `‹ Artists` | `<a class="back-btn" href="Lumen Atlas Gallery.html">` — ChevronLeft 18px + text, `--accent`, 14px/500, `padding: 6px 8px; border-radius: 8px; margin-left: -8px`, hover accent-10 % | Return to a people index |

**It is labelled "Artists" and navigates to the home page**, which has no artists index. It is a
hard-coded parent, not history-aware back navigation, and it is the page's only breadcrumb.

### P3. Cover — `<div class="cover">` (639–641)

A bare `<div>` — no landmark, no `aria-label`, no owner control to change it.

`margin: 12px 16px 0`, `max-width: 1240px`, radius `var(--radius-xl)` 28px, `overflow: hidden`,
`background: #111`, **`aspect-ratio: 16/6` → `16/8` at ≤880px**. Centred (`margin-left/right: auto`)
only at ≥1272px, so between ~1256px and 1272px it is left-aligned while every region below it is
centred.

`img { width: 100%; height: 100%; object-fit: cover; filter: saturate(1.05) contrast(1.02) }` —
**a non-neutral colour transform applied to a photographer's own cover image.**
`alt="Concrete brutalist structure with dramatic shadows"`.
`::after` = `linear-gradient(180deg, transparent 60%, rgba(12,14,20,.35))`, `pointer-events: none`.

### P4. Profile header — `<section class="profile-head">` (644–684)

`max-width: 1240px; padding: 0 16px; display: grid; grid-template-columns: auto 1fr auto; gap: 20px;
align-items: end; margin-top: 20px; position: relative; z-index: 2`. At ≤880px: one column, centred,
`gap: 14px`, `margin-top: 16px`.

`.profile-avatar`: 128px circle (104px ≤880px), `overflow: hidden`, `background: var(--line-2)`,
`box-shadow: 0 12px 28px -12px rgba(17,22,40,.35), 0 2px 6px rgba(17,22,40,.1), 0 0 0 4px white`,
**`margin-top: -84px`** (−64px ≤880px) so it overlaps the cover. `img object-fit: cover` — a
circular crop of a person's photograph. `alt="Alex Rivera"`.

**Data shown**

| Field | Value | Element |
|---|---|---|
| Avatar | image URL | `.profile-avatar img` |
| Display name | `Alex Rivera` | `<h1 class="profile-name">` (28px/600/-0.02em; 24px ≤880px) |
| Verification | a 20px `--accent` circle with a white 11px Check | `<span class="verified" aria-label="Verified">` — **a `<span>` with `aria-label` and no `role`; the label is ignored by most assistive technology.** No tooltip, no explanation, no policy |
| Handle · style | `@alex.rivera · Urban Brutalism` | `.profile-handle` (14px `--ink-3`) — **two fields concatenated into one string** |
| Location | `Mexico City · Berlin` | `.profile-line .chip` + MapPin |
| Joined | `Member since 2019` | `.profile-line .chip` + Calendar |
| Website | `alexrivera.studio` | `<a class="chip" href="#" style="color:var(--accent);">` + Link glyph — **inline-styled colour; no `rel`, no `target`, no scheme shown, a user-supplied outbound URL with no hardening** |

`.profile-line`: `display: flex; flex-wrap: wrap; gap: 6px 14px; margin-top: 10px; font-size: 13px;
color: var(--ink-2)`; its SVGs are 14px `--ink-3`.

**Controls** — `.profile-actions` (flex, `gap: 8px`, `padding-bottom: 10px`; centred with
`padding-bottom: 0` at ≤880px). `.btn` here is **36px / 13.5px/600 / radius 999px**, smaller than
Gallery's 44px / 14px.

| # | Control | Element | Intent |
|---|---|---|---|
| 8 | `Follow` | `<button class="btn btn-primary" id="followBtn">` + Plus icon (672) | Follow. `.following` variant = `--bg-tint` bg, `--ink` text, `inset 0 0 0 1px var(--line)`, Check icon, text "Following" |
| 9 | `Message` | `<button class="btn btn-secondary">` (676) | Open a direct-message thread |
| 10 | Share | `<button class="btn btn-icon" aria-label="Share">` (677) — 36×36, the iOS-style upload-box glyph | Share this profile |
| 11 | More | `<button class="btn btn-icon" aria-label="More">` (680) — three filled dots | Open an overflow menu. **No `aria-haspopup`, no `aria-expanded`, no menu, nothing opens** |
| 7 | Website | `<a class="chip" href="#">` (665) | Open the member's own site |

The "More" button is where Block (`VZ-BLOCK-001`, whose `ui-controls.json` row names "profile menu")
and Report (`VZ-REPORT-001`, "report … users") belong. **The affordance is drawn and its contents
are not.** Nothing in the header distinguishes owner-viewing-own-profile (Edit profile, Edit cover)
from visitor, and nothing handles anonymous (Follow and Message are shown with no session and no
sign-in path).

### P5. Bio and stats — `<section class="profile-body">` (687–721)

`max-width: 1240px; padding: 0 16px; display: grid; grid-template-columns: minmax(0, 1fr) 340px;
gap: 40px; align-items: start; margin: 26px auto 0`. At ≤880px: one column, `gap: 20px` — the stats
card drops **below** the bio.

`.bio`: 16px, `--ink-2`, `line-height: 1.6`, `text-wrap: pretty`, `max-width: 60ch`. Two `<p>` with
`<i>` emphasis on publication names — so the bio field carries **multi-paragraph rich text**, which
is a contract decision the mockup makes silently.

`<aside class="stats-card">`: `--bg-elev`, `1px solid var(--line)`, radius 22px, `padding: 18px`,
`--shadow-sm`.

**Data shown**

| Block | Field | Value | Element |
|---|---|---|---|
| `.stats-grid` (3 cols, `gap: 2px`, `.stat + .stat { border-left: 1px solid var(--line-2) }`) | Photos | `312` | `.stat .n` 22px/600 + `.stat .l` 11px/.08em uppercase `--ink-3` |
| | Albums | `24` | same |
| | Followers | `48.2k` | same |
| `.stats-list` (13px rows, space-between) | `Most used camera` | `Leica Q3` | `.row b` 500 `--ink` |
| | `Favorite lens` | `28mm f/1.7` | same |
| | `Style` | `Brutalism`, `B&W` | two `.tag` pills (`--bg-tint`, 11px/500, radius 999px) |
| `.avail` | status | green `.avail-dot` 9px `oklch(0.72 0.17 150)` + `0 0 0 3px` halo, `aria-hidden="true"` | — |
| | title | `Available for commissions` | `.avail-title` 13px/600 |
| | sub | `Booking Q3 2026 · Architecture & editorial` | `.avail-sub` 11.5px `--ink-3` |

**All three stat tiles are inert `<div>`s.** Followers does not link to a followers list, Albums does
not link to the Albums tab, Photos does not link to anything. A **Following** count is absent
entirely, though `VZ-FOLLOW-001` requires both `/{username}/followers` and `/following`. A
**Favorites** count/link is absent, though `VZ-FAVORITE-001` requires `/u/{username}/favorites`.

| # | Control | Element |
|---|---|---|
| 12 | `Hire` | `<a class="btn btn-secondary btn-sm" href="#">` (718) — 30px, 12.5px |

`.stats-divider` is `height: 1px; background: var(--line-2); margin: 14px -18px` — full-bleed inside
the padded card.

### P6. Sticky tabs — `<div class="tabs-wrap">` (724–747)

`position: sticky; top: var(--nav-h)` (56px), `z-index: 40`, background `color-mix(in oklab,
var(--bg) 85%, transparent)` + `saturate(180%) blur(18px)`, `border-bottom: 1px solid color-mix(in
oklab, var(--line) 60%, transparent)`, `margin-top: 36px`. **A second sticky layer under the 56px
nav consumes ~104px of a 390×844 viewport before any content.**

`.tabs`: `max-width: 1240px; padding: 0 16px; display: flex; align-items: center; gap: 4px;
overflow-x: auto; scrollbar-width: none` + hidden WebKit scrollbar. **`role="tablist"`.**

`.tab`: `position: relative; padding: 14px 14px`, 14px/500 `--ink-3`, `white-space: nowrap`;
`.active` = `--ink`/600 plus a `::after` 2px `--ink` underline inset 14px, `bottom: -1px`.
`.tab .count`: 12px/500 `--ink-3`, `margin-left: 6px`.

| # | Control | Element | Count | State |
|---|---|---|---|---|
| 14 | `Photos` | `<button class="tab active" role="tab" aria-selected="true">` | `312` | active |
| 15 | `Albums` | `<button class="tab" role="tab">` | `24` | **no `aria-selected="false"`** |
| 16 | `Featured` | `<button class="tab" role="tab">` | `6` | **no `aria-selected`** |
| 17 | `About` | `<button class="tab" role="tab">` | — | **no `aria-selected`; no About panel exists** |

Then `<div class="tabs-spacer">` (`flex: 1`) and `<div class="tabs-tools">` — **both are DOM children
of the `role="tablist"`**, which may contain only tabs; and `.view-toggle` carries a **second nested
`role="tablist"`**.

| # | Control | Element | Intent |
|---|---|---|---|
| 18 | `Recent` sort | `<button class="sort">` (732) — 32px pill, white on `--line`, 12.5px/500, **a `ListFilter` glyph** + text + an 11px ChevronDown | Change listing order. **No `aria-haspopup`, no `aria-expanded`, no menu, no handler, and a filter glyph on a sort control** |
| 19 | View: Grid | `<button class="view-btn active" aria-label="Grid">` (738) — 30×26, 4 square-cornered rects | Density switch |
| 20 | View: Rows | `<button class="view-btn" aria-label="Rows">` (741) — **`M4 6h16M4 12h16M4 18h16`, a hamburger/`Menu` glyph, not a rows glyph** | Density switch |

`.view-toggle`: `--bg-tint` track, `1px solid var(--line)`, radius 999px, `padding: 3px`, `gap: 2px`;
`.view-btn.active` = `--ink`/white.

**Clicking a tab changes nothing.** The three content sections below (Featured Series, Recent Photos,
Albums) are all rendered simultaneously and unconditionally, so "Photos", "Albums" and "Featured"
are on screen at once while presenting as mutually exclusive tabs, and "About" has no panel at all
(the bio sits *above* the tab strip). The counts `312 / 24 / 6` also disagree with what is drawn:
3 series, 10 photos, 3 albums.

### P7. Featured Series — `<section class="section">` (750–788)

`.section { max-width: 1240px; margin: 0 auto; padding: 36px 16px 0 }`.
`.section-head`: flex, `align-items: flex-end`, space-between, `gap: 16px`, `margin-bottom: 16px`.

- `<span class="eyebrow">Pinned</span>` · `<h2 class="section-title">Featured Series</h2>`
  (22px/600) · `<p class="section-sub">Long-form bodies of work, curated by Alex.</p>`

| # | Control | Element |
|---|---|---|
| 21 | `See all ›` | `<a href="#" class="link-inline">` |
| 22 | Series card ×3 | `<a class="series-card" href="#">` |

`.series-row`: `grid-template-columns: repeat(3, 1fr); gap: 14px` → `1fr 1fr` at ≤880px **with
`.series-card:nth-child(3) { display: none }`** — the third series is removed on phones and its only
alternative route (`See all ›`) is dead.

`.series-card`: `aspect-ratio: 4/5`, radius 22px, `background: #222`, `--shadow-md`;
`img { width: 100%; height: 100%; object-fit: cover; transition: transform .5s }`, hover
`scale(1.03)`. `.grad` = `linear-gradient(180deg, transparent 45%, rgba(10,12,18,.72))`,
`pointer-events: none`.

`.series-label`: absolute `bottom: 14px; left/right: 16px`, white.
`.series-eyebrow` 10px/600/.14em uppercase `opacity: .85` with a `::before` 5px white dot;
`.series-title` 19px/600 `text-wrap: balance`; `.series-meta` 12px `opacity: .8`.

**Fields per series card**

| Frames | Title | Subtitle | `img alt` |
|---|---|---|---|
| `24 frames` | `Concrete Sundays` | `Civic theatres of the global south` | `""` |
| `18 frames` | `North Light` | `Studies in Nordic civic brutalism` | `""` |
| `12 frames` | `Mexico Modern` | `Luis Barragán's chromatic afterlife` | `""` |

**"Concrete Sundays · 24" and "North Light · 18" appear again 80 lines later as Albums with the same
names and the same counts.** Series and Album are the same objects under two names, with two
different visual treatments and two different sections.

### P8. Recent Photos — `<section class="section">` (791–834)

Head: `<h2 class="section-title">Recent Photos</h2>` · `<p class="section-sub">Fresh frames and
working edits.</p>`

| # | Control | Element | Note |
|---|---|---|---|
| 23 | `Open library ›` | `<a href="#" class="link-inline">` | **"Library" is the owner's private camera roll in Vizra (`VZ-LIBRARY-001`, `/library`). Linking to it from a stranger's public profile is a vocabulary and permission conflict** |
| 24 | Photo card ×10 | `<a class="photo" href="#">` | |

`.grid`: `repeat(2, 1fr); gap: 10px` base · `repeat(2, 1fr); gap: 6px` at ≤880px ·
`repeat(4, 1fr); gap: 14px` at ≥881px · `repeat(4, 1fr)` at ≥1100px (dead duplicate).

`.photo`: radius 16px, `background: var(--line-2)`, `aspect-ratio: 1`, `--shadow-sm`;
`img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s }`, hover
`scale(1.04)`. Modifiers: **`.tall { grid-row: span 2; aspect-ratio: 1/2 }`** and
**`.wide { grid-column: span 2; aspect-ratio: 2/1 }`** — three hard crops, chosen by the layout.
No `loading="lazy"` on any image.

`.photo::after` = `linear-gradient(180deg, transparent 55%, rgba(10,12,18,.55))`, `opacity: 0` → 1
on hover, `pointer-events: none`.
`.photo .meta`: absolute `left/right/bottom: 10px`, white 12px, `opacity: 0; transform:
translateY(6px)` → revealed **only** by `.photo:hover`. **No `:focus-within`.**
`.photo .heart`: `rgba(0,0,0,.35)` + `blur(10px)`, radius 999px, `padding: 4px 8px`, a 12px filled
Heart — **a `<span>`, not a control, ×10.**
`.badge-new`: absolute `top/left: 10px`, 10px/600/.08em uppercase, white on `rgba(0,0,0,.45)` +
`blur(10px)` — **always visible**, unlike the caption.

**Fields per photo card**

| # | class | `alt` | Caption (`.meta span`) | Hearts | Badge |
|---|---|---|---|---|---|
| 1 | `wide` | `""` | `Brutalist facade, Turin` | `1.2k` | `New` |
| 2 | — | `""` | `Mountain chapel` | `842` | — |
| 3 | `tall` | `""` | `Casa Gilardi` | `2.1k` | — |
| 4 | — | `""` | `Cold lobby` | `512` | — |
| 5 | — | `""` | `Civic stair` | `930` | — |
| 6 | — | `""` | `Shadow grid` | `1.4k` | — |
| 7 | — | `""` | `Cyanotype window` | `770` | — |
| 8 | `wide` | `""` | `Plinth at dusk · Marseille` | `3.3k` | — |
| 9 | — | `""` | `Light tunnel` | `604` | — |
| 10 | — | `""` | `Grey horizon` | `418` | — |

**All ten images carry `alt=""`** while the caption is `opacity: 0` until hover. There is no
favourite control, no date, no privacy marker, no safety marker, no comment or rating indicator, no
pagination, no total and no "load more" — the tab claims 312 photos and the only onward route is a
dead `Open library ›`.

Photo URLs are reused from the Gallery and Search mockups under different captions (e.g.
`photo-1470770841072-…` is "Lake at dusk" on Gallery and "Mountain chapel" here;
`photo-1500382017468-…` is "Wheat field at golden hour" on Gallery and "Light tunnel" here), so
captions cannot be treated as data about the images.

### P9. Albums — `<section class="section">` (837–881)

Head: `<h2 class="section-title">Albums</h2>` · `<p class="section-sub">Curated groupings and
in-progress edits.</p>`

| # | Control | Element |
|---|---|---|
| 26 | `All 24 ›` | `<a href="#" class="link-inline">` |
| 27 | Album card ×3 | `<a class="album" href="#">` |

`.albums`: `repeat(3, 1fr); gap: 16px` → `1fr` at ≤880px.
`.album`: radius 22px, `overflow: hidden`, `--bg-elev`, `1px solid var(--line-2)`, `--shadow-sm`;
hover `translateY(-2px)` + `--shadow-md`.
`.album-thumbs`: `display: grid; grid-template-columns: 2fr 1fr; grid-template-rows: 1fr 1fr;
gap: 2px; aspect-ratio: 4/3`; `img:first-child { grid-row: 1 / 3 }`; every `img` `object-fit: cover`
on `var(--line-2)`. **A three-image mosaic cover — three simultaneous crops per album.**
`.album-body`: `padding: 14px 16px 16px`; `.album-title` 15px/600; `.album-meta` 12.5px `--ink-3`.

| Title | Meta | Thumbnails |
|---|---|---|
| `Concrete Sundays` | `24 photos · Updated 3 days ago` | 3, all `alt=""` |
| `North Light` | `18 photos · Updated 2 weeks ago` | 3, all `alt=""` |
| `Working Edits` | `41 photos · Updated yesterday` | 3, all `alt=""` |

**No privacy marker on any album** — `VZ-ALBUM-002` defines public / private / link-only / password,
and "Working Edits" is precisely the album that would be private. No cover-choice affordance, no
sub-album indication, no album favourite or comment count (`VZ-ALBUM-004`), no sort control.
`VZ-ALBUM-001` specifies a **single chosen cover**; the mosaic treatment belongs to
`VZ-COLLECTION-001`.

### P10. Page end and P11. Mobile tabs

See §a.5 and §a.4.

| # | Control | Element |
|---|---|---|
| 28 | Mobile: Home | `<a class="tab-m" href="Lumen Atlas Gallery.html" aria-label="Home">` |
| 29 | Mobile: Explore | `<button class="tab-m" aria-label="Explore">` |
| 30 | Mobile: Upload | `<button class="tab-m" aria-label="Upload">` |
| 31 | Mobile: Saved | `<button class="tab-m" aria-label="Saved">` |
| 32 | Mobile: You | `<button class="tab-m active" aria-label="Profile">` |

### c.12 What the inline script does (912–934)

~22 lines, three units, **no data, no fetch, no state model**.

1. **Tabs** (914–917). `.tabs .tab` click → clear `.active` from all, set on clicked.
   **It never touches `aria-selected`.** After any click the DOM still asserts
   `aria-selected="true"` on "Photos" while the visual selection has moved — actively worse than
   omitting ARIA. No panel is shown or hidden.
2. **View toggle** (919–922). `.view-toggle .view-btn` → class toggle within `b.parentElement`.
   Cosmetic; `.grid` never changes.
3. **Follow** (924–933), an IIFE on `#followBtn`:
   ```js
   const on = b.classList.toggle('following');
   b.innerHTML = on ? '<svg …Check…/> Following' : '<svg …Plus…/> Follow';
   ```
   - **It replaces the entire inner HTML of the focused button**, destroying and recreating its
     accessible name in place; many screen readers will not announce the change.
   - **No `aria-pressed`**, no `aria-live`, no pending/`disabled` state, no failure path, no revert,
     no unfollow confirmation, and **no authentication check** — an anonymous visitor toggles
     "Following" with no request and no sign-in prompt. `DESIGN_BRIEF.md`: "A clicked animation or
     success toast is not proof."

**Never wired:** the search input, Notifications, Upload, the avatar, the back link (a real
navigation), Message, Share, More, the website chip, `Hire`, the sort button, `See all ›`,
`Open library ›`, `All 24 ›`, all 3 series cards, all 10 photo cards, all 10 heart counts, all 3
album cards, every stat tile, and 4 of the 5 mobile tabs.

**Mock-data shape: none.** Every value — three stats, three stat-list rows, three series, ten
photos, three albums, four tab counts — is a hand-written HTML literal.

### c.13 States

**Present:** hover (`.icon-btn`, `.back-btn`, `.btn-primary`, `.btn-secondary`, `.btn-icon`, `.tab`,
`.series-card img`, `.photo img`, `.photo::after`, `.photo .meta`, `.album`); selected
(`.tab.active` underline, `.view-btn.active`, `.tab-m.active`); **toggled** (`.btn-primary.following`
— the only two-state control in either page); image placeholders (`var(--line-2)` on `.photo`,
`.profile-avatar` and `.album-thumbs img`; `#111` cover; `#222` series); a status indicator
(`.avail-dot`).

**Absent:**

| Missing state | Consequence |
|---|---|
| **`:focus-visible` — there are zero rules in this file** | Every one of the 42 interactive elements relies on the UA default ring, over 999px pills bordered at 1.35:1, with `* { -webkit-tap-highlight-color: transparent }` also removing the touch hint. Gallery has three rules; this page has none |
| **Owner view** | No Edit profile, no Edit cover, no Edit avatar, no album/photo management, no "add to featured". The mockup draws only a stranger's view |
| **Anonymous view** | Follow and Message render with no session and no sign-in path |
| **Private profile** | `VZ-PROFILE-001`: "private profiles hide identity"; `VZ-ACCOUNT-001`: "private profile hides content from non-followers/anonymous". Undrawn |
| **Follow pending / request** | `VZ-FOLLOW-002` (`full`, M5) — the requester must see their own pending state. Undrawn |
| **Blocked / blocking** | `VZ-BLOCK-001` — no state for either direction |
| **Empty** | A member with no photos, no albums, no series, no bio, no website, no location. The default for every new account on a fresh instance |
| **Loading / error / disabled / busy** | None; no skeleton, no failed-fetch, no `aria-busy`, no `:disabled`, no pending Follow |
| **NSFW blur, visibility markers** | `VZ-NSFW-001`, `VZ-PRIVACY-001/002` — nothing on 10 photo cards, 3 album cards or 3 series cards |
| **Dark mode, reduced motion** | Absent (G7, G8 unchanged) |
| **Suspended / deleted member** | `VZ-ADMIN-USERS-001` — undrawn |

### c.14 Accessibility observations (Profile)

| Issue | Location |
|---|---|
| **Zero `:focus-visible` rules in the entire file** | — |
| `<span class="avatar">MK</span>` as the account control, with **no `aria-label` at all** | 626 — worse than Search's, which at least had one |
| `<span class="verified" aria-label="Verified">` — `aria-label` on a role-less `<span>` is ignored by most AT | 651 |
| `role="tablist"` containing `.tabs-spacer` and the whole `.tabs-tools` toolbar, plus a **nested** `role="tablist"` on `.view-toggle` | 725, 737 |
| `aria-selected="true"` on the first tab only; **the script never updates it**, so it is permanently wrong after any interaction | 726, 914–917 |
| No `role="tabpanel"`, no `aria-controls`, no roving `tabindex`, no panel switching | — |
| `<button class="sort">` with no `aria-haspopup`/`aria-expanded` and no menu | 732 |
| `<button aria-label="More">` with no `aria-haspopup`/`aria-expanded` and no menu | 680 |
| `aria-label="Rows"` on a hamburger glyph | 741 |
| `aria-label="Profile"` on a tab whose visible text is `You` — WCAG 2.5.3 | 906 |
| **All 10 photo images and all 9 album thumbnails and all 3 series images carry `alt=""`** — 22 of 24 images on the page | 761–879 |
| Captions are `opacity: 0` until hover, with no `:focus-within` — on touch the caption and the favourite count are unreachable | 462–469 |
| Ten `.heart` `<span>`s that read as favourite buttons and are not | — |
| Three inert `.stat` `<div>`s (Photos / Albums / Followers) that must be links | 694–696 |
| Three inert `.stats-list .row`s presenting derived public statistics | 700–707 |
| `<a class="chip" href="#" style="color:var(--accent);">` — user-supplied outbound website link with no `rel="nofollow ugc noopener"`, no `target`, no scheme | 665 |
| `.tabs` is a horizontal scroll container with `scrollbar-width: none`, no `tabindex="0"`, no keyboard scroll affordance | 331–334 |
| **No `<main>`, no skip link**; the cover is a bare `<div>`; no `aria-live` anywhere | — |
| **32 inline `<svg>` elements; two `aria-hidden` attributes in the file**, both on `<span>`s (`.brand-mark`, `.avail-dot`), **none on an SVG** | — |
| `.series-card:nth-child(3) { display: none }` at ≤880px removes content with no alternate route | 587 |
| Double sticky (nav 56px + tabs ~48px) = ~104px of a 390×844 viewport | 55–56, 318 |

---

## d. Icons — new to these pages, mapped to `lucide-react`

`INVENTORY-search.md` §g.1 already maps Search / X / Bell / Upload / ListFilter / sort /
ChevronDown / Check / LayoutGrid / masonry / rows / Star / Bookmark / Heart / Eye / Play /
ArrowRight / ArrowDown / House / User / ChevronRight / orientation glyphs. Those mappings apply
unchanged wherever the same path data appears here. Only **new** glyphs are listed below.

**Every name is marked TO VERIFY against the pinned `lucide-react` version.** Lucide renames exports
across releases (`Home`→`House`, `HelpCircle`→`CircleHelp`, `MoreHorizontal`→`Ellipsis`,
`LineChart`→`ChartLine`, `Rows`→`Rows2`), and `VZ-DESIGN-001` requires a test asserting every
registry name exists in the pinned package. Do not import any of these without that check.

| # | Mockup use | Path (abbreviated) | Proposed registry key | Closest `lucide-react` export | Note |
|---|---|---|---|---|---|
| 23 | Gallery nav pill "Surprise" (791) | `M8 3h5l8 8-8 8-8-8Z` + `circle 11,11 r1.5` | `random` | `Gem` | **TO VERIFY — and probably wrong.** Lucide's `Gem` is a faceted diamond (`M6 3h12l4 6-10 13L2 9Z` + facets); this is a rotated square with a dot. For "random" semantics `Shuffle` or `Dices` is the honest glyph. May need an original mark (separately reviewed per `DESIGN_BRIEF.md`) |
| 24 | Menu "Insights" (839) | `M3 3v18h18` + `m7 15 4-4 3 3 5-6` | `insights` | `ChartLine` | TO VERIFY — exported as `LineChart` in older versions; check which name the pinned package exports |
| 25 | Menu "Upload Studio" (843) | `rect 3,4 18×14 rx2` + `circle 9,11 r2` + `m21 15-5-4-9 7` | `media` / `photo` | `Image` | TO VERIFY — Lucide's `Image` is exactly this geometry |
| 26 | Menu "Edit Profile" (850) | `M12 20h9` + `M16.5 3.5a2.1 2.1 0 1 1 3 3L7 19l-4 1 1-4Z` | `edit` | `Pencil` | TO VERIFY — also consider `SquarePen` |
| 27 | Menu "Account Settings" (854) | gear, `circle 12,12 r3` + 12-lobe outline | `settings` | `Settings` | TO VERIFY |
| 28 | Menu "Help & Feedback" (863) | `circle 12,12 r9` + `M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3` + `M12 17h.01` | `help` | `CircleHelp` | TO VERIFY — renamed from `HelpCircle` |
| 29 | Menu "Sign Out" (870) | `M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4` + `m16 17 5-5-5-5` + `M21 12H9` | `sign-out` | `LogOut` | TO VERIFY — needs RTL mirroring |
| 30 | Discover "Mosaic" (1016) | `rect 3,3 18×8` + `rect 3,13 8×8` + `rect 13,13 8×8` | `view-mosaic` | `LayoutPanelTop` | TO VERIFY — no exact Lucide match; candidates `LayoutPanelTop`, `LayoutDashboard`, `PanelsTopLeft`. Likely an original mark |
| 31 | Mobile upload FAB (1112), Profile Follow (673), Profile mobile Upload (899) | `M12 5v14M5 12h14` | `add` | `Plus` | TO VERIFY |
| 32 | Gallery footer "Share" (1095) | `circle 18,5 r3` + `circle 6,12 r3` + `circle 18,19 r3` + connectors | `share-network` | `Share2` | TO VERIFY |
| 33 | Gallery footer "Email" (1096) | `rect 3,5 18×14 rx2` + `m3 7 9 6 9-6` | `email` | `Mail` | TO VERIFY |
| 34 | Profile back button (633) | `m15 18-6-6 6-6` | `back` / `disclosure-left` | `ChevronLeft` | TO VERIFY — **needs RTL mirroring** |
| 35 | Profile location chip (658) | `M20 10c0 7-8 12-8 12S4 17 4 10a8 8 0 0 1 16 0Z` + `circle 12,10 r3` | `location` | `MapPin` | TO VERIFY |
| 36 | Profile "Member since" chip (662) | `rect 3,5 18×16 rx2` + `M3 9h18M8 3v4M16 3v4` | `date` | `Calendar` | TO VERIFY |
| 37 | Profile website chip (666) | `M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1` + mirror | `link` | `Link` | TO VERIFY — also `Link2` |
| 38 | Profile header "Share" (678) | `M12 3v12` + `m8 7 4-4 4 4` + `M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4` | `share` | `Share` | TO VERIFY. **Note: the Gallery footer's "Share" uses `Share2` (node graph) and this uses `Share` (upload box) — two glyphs for one semantic key across two pages** |
| 39 | Profile "More" (681) | `circle 6,12 r1.6` + `circle 12,12` + `circle 18,12`, `fill="currentColor"` | `overflow-menu` | `Ellipsis` | TO VERIFY — renamed from `MoreHorizontal`; Lucide is stroke-only so the filled dots need a `fill` prop or CSS |
| 40 | Profile "Rows" view (742) | `M4 6h16M4 12h16M4 18h16` | `view-rows` | `Menu` / `AlignJustify` | **TO VERIFY — the glyph and the label disagree.** This is Lucide's hamburger, not `Rows2`/`Rows3`. Either the label or the glyph is wrong |
| 41 | Profile "verified" badge (652) and Follow "Following" state (930) | `m5 12 5 5 9-11` | `verified` **and** `following` | `Check` | TO VERIFY. **One glyph, two unrelated meanings** — identity verification and follow state. `DESIGN_BRIEF.md` requires semantically distinct actions to be distinguishable |
| 42 | Gallery "Albums" menu item (835) **and** both pages' mobile "Saved" tab (1115 / 903) | `M19 21 12 16l-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2Z` | `album` **and** `save` | `Bookmark` | TO VERIFY. **Same collision** — one glyph for Albums and for a bookmark list, in one shell |
| 43 | Literal `›` character | text, not SVG | `disclosure-right` | `ChevronRight` | 6 instances: `View Profile ›` ×3 and `Browse all ›` (Gallery), `See all ›`, `Open library ›`, `All 24 ›` (Profile). Currently not icons at all — same defect as Search's `.rc .arr` |

**Stroke widths in use:** Gallery `{1.7, 1.8, 1.9, 2}`; Profile `{1.7, 1.8, 1.9, 2, 2.2, 3}` —
against Search's `{1.4px CSS, 1.7, 1.8, 1.9, 2, 2.2, 2.4, 2.5, 3}`.
**Rendered sizes:** Gallery 11, 13, 15, 16, 17, 18, 19, 20 px (plus `width="16"` inline on the nav
search SVG); Profile 11, 12, 13, 14, 18, 19, 20 px. A registry must fix one stroke and a small size
set; `VZ-DESIGN-001` requires the typed registry and the export-existence test.

**Count:** 35 inline SVGs in Gallery, 32 in Profile, **67 total, none with `aria-hidden="true"`**.

---

## e. Conflicts with `docs/DESIGN_BRIEF.md` and `AGENTS.md`

### e.1 Inherited unchanged from `INVENTORY-search.md` §g

G1 (SF Pro named in the font stack — Gallery declares both `--font-sans` and `--font-display`;
Profile declares only `--font-sans`, so the display/text distinction is lost entirely on that page),
G2 (hand-inlined SVG instead of a typed Lucide registry — 67 here, plus 6 literal `›` characters),
G3 (hotlinked Unsplash — **22 URLs in Gallery, 24 in Profile**, all with `fit=crop`), G7 (no dark
mode), G8 (no reduced motion), G9 (dead controls and dead links — **31 of 42 anchors in Gallery and
21 of 24 in Profile are `href="#"`**), G13 ("Artists" vocabulary — here it is the nav link, the
section heading "Artist Showcases", the class `.artist-card`, and the back button's label), G14
(the "Lumen Atlas" brand and gradient mark — **here there are two different marks**), G15 (no
`<main>`, no skip link, and the Profile has no real footer), G16 (invalid ARIA), G17 (no token
discipline), G18 (backdrop blur over photography — nav 22px, hero card 24px, tooltip 20px, profile
menu 28px, Gallery mobile bar 24px, Profile mobile bar 28px, Profile tabs 18px, `.heart` 8–10px,
`.badge-new` 10px, `.chip` 12px), G22 (fixtures only, no API — recorded so it is not mistaken for
evidence).

### e.2 New or materially worse on these two pages

| # | Conflict | Evidence | Rule |
|---|---|---|---|
| C1 | **Every image on both pages is destructively cropped.** Search's masonry at least preserved `height: auto`. Here: Gallery hero `4/5`→`16/9`→`16/8`; `.photo` `1` / `3:4` / `16:10`→`4:3`; `.collection` `4/3`→`3/2`; `.editorial-img` `1`; `.artist-thumb` `1`; `.artist-avatar` circular. Profile: `.cover` `16/6`→`16/8`; `.series-card` `4/5`; `.photo` `1` / `1/2` / `2/1`; `.album-thumbs` `4/3` split three ways; `.profile-avatar` circular. **Zero images on either page are shown at their own aspect ratio**, and 46 of 46 image URLs carry `&fit=crop` | `DESIGN_BRIEF.md`: "Preserve the image's aspect ratio; do not default to destructive cropping." |
| C2 | **A colour transform on a photographer's cover image** — `filter: saturate(1.05) contrast(1.02)` | Profile 137 | `DESIGN_BRIEF.md` visual direction is "photography first". Silently altering an uploader's image is a product decision, not a style |
| C3 | **There is no favourite control on either page.** The heart is a `<span>` count **19 times** (9 Gallery + 10 Profile) | Gallery 1027–1051, Profile 804–831 | `VZ-FAVORITE-001`; `ui-controls.json` `photo.favorite`; `DESIGN_BRIEF.md` devotes a paragraph to proving the Favorite control ("a clicked animation or success toast is not proof") |
| C4 | **Hover-only card metadata with no `:focus-within` fallback** — worse than Search, which had one. On touch, the author handle, the caption and the favourite count of all 19 photo cards are invisible and unreachable | Gallery 605–608, Profile 466–469 | `DESIGN_BRIEF.md`: "Reject… missing mobile actions"; "Do not rely on hover-only tooltips"; `VZ-RESPONSIVE-001` |
| C5 | **Content deleted on mobile with no alternate route** — `.series-card:nth-child(3) { display: none }` at ≤880px, and its `See all ›` is `href="#"` | Profile 587 | `VZ-RESPONSIVE-001`; `DESIGN_BRIEF.md` |
| C6 | **Search removed entirely below 881px on the Profile**, with no replacement; and `VZ-PROFILE-001` separately requires **search within the profile**, which neither page draws | Profile 569 | `VZ-PROFILE-001`, `VZ-SEARCH-001`, `VZ-RESPONSIVE-001` |
| C7 | **Fabricated metrics, including metrics that contradict each other inside one component.** Gallery account menu: `142 Photos / 18 Series / 2.4k Followers` versus the `My Photos · 312` item **fourteen lines later**; 9 heart counts; 4 collection counts; "refreshed hourly"; "28 min". Profile: `312 / 24 / 48.2k`; tab counts `312 / 24 / 6` against 10 photos, 3 albums and 3 series actually drawn; `24 / 18 / 41` album counts; 10 heart counts; `Leica Q3`; `28mm f/1.7`; `Booking Q3 2026`; `Member since 2019` | Gallery 818–832, Profile 694–716, 726–729 | `DESIGN_BRIEF.md`: "Reject… fake metrics." `AGENTS.md`: "Do not fabricate outputs." Every count must be a permission-aware server value |
| C8 | **A verified badge with no verification feature.** Nothing in `docs/quality/features.json` defines identity verification; `VZ-AUTH-004` roles are not a verification mark | Profile 651–653 | Drawing an unbacked trust signal is a trust-and-safety hazard, not a styling choice |
| C9 | **A commissions / booking / hire surface** — "Available for commissions", "Booking Q3 2026", a `Hire` button | Profile 712–719 | Outside `docs/PRODUCT_CHARTER.md`; `README.md` standing note 3: "Vizra has no billing product" |
| C10 | **An audio programme** — "Listen to the interview · 28 min" with a Play button | Gallery 1070–1075 | `VZ-MEDIA-002` matrix is JPEG/PNG/GIF/WebP/AVIF/BMP; `VZ-MEDIA-005` is MP4/MOV/WebM. **Vizra has no audio media type** |
| C11 | **An editorial article with its own byline** — "Editorial Journal", "The Art of Seeing: a conversation with Alex Rivera", plus the hero's "Read the Narrative" | Gallery 883–891, 1067–1069 | No article entity exists. `VZ-PAGE-001` is owner-authored site pages, not per-photographer narratives |
| C12 | **"Series" as a first-class object on both pages** — hero eyebrow "Featured Series", menu stat "18 Series", Profile section "Featured Series", Profile tab "Featured 6", `.series-card` ×3, `.series-eyebrow` "24 frames" | Gallery 819, 882; Profile 726–729, 753–787 | The same NO-LEDGER-ID entity `INVENTORY-search.md` §h.7 #2 flagged as a filter chip. Here it is load-bearing structure, and its three instances are the **same objects** as the three Albums below |
| C13 | **"Curated by <person>" collections conflate two different ledger features.** `VZ-COLLECTION-001` is a member grouping **their own albums**; `VZ-GALLERY-001` is a member curating **other members' photos**. The mockup's "Thematic Collections" (named curator + image count) is the latter under the former's name | Gallery 951–1001 | Owner / contract decision; the two are different features, both `full`, both M5 |
| C14 | **One Bookmark glyph for "Albums" and for "Saved"**, 280 lines apart in one shell; and one Check glyph for "verified" and "following" | Gallery 835 / 1115; Profile 652 / 930 | `DESIGN_BRIEF.md`: "Favorites and ratings must not be visually or semantically indistinguishable" — the same hazard |
| C15 | **Two different brand marks and two different Share glyphs in one design system** | Gallery 82–88 / 1095; Profile 69–73 / 678 | `VZ-DESIGN-001`; `VZ-BRAND-001` |
| C16 | **Three mutually exclusive shells across three public pages** — nav (flex+tooltips+menu / grid, no links, inert avatar / flex with `order` reassignment), mobile bar (`999px` pill 58px z-40 no safe-area / `24px` card 60px z-80 with safe-area / edge-to-edge 62px z-40 with safe-area, and the class is `.tab` on two pages and `.tab-m` on the third), footer (full / two-span `div` / none) | §a.3–a.5 | `VZ-DESIGN-001` ("approved tokens, components"); a shell is one component |
| C17 | **Disjoint breakpoint sets and container widths** — `{520, 760, 1100}` / `{880, 881, 1100, 1272}` / `{520, 780, 900, 1000, 1200, 1440}`; shells `1240px` / `1240px` / `1440px`; the same Discover-style grid reaches 3 columns on Gallery and 4 on Search | §a.6 | `VZ-RESPONSIVE-001`, `VZ-LISTING-001` ("columns per device" is one owner setting, not three page opinions) |
| C18 | **`role="tablist"` misuse in three new forms** — (a) Gallery `.pill-row` and `.tool-group`: tablist with no `role="tab"` children and no tabpanel; (b) Profile `.tabs`: a tablist containing `.tabs-spacer`, a sort button and a **nested** tablist; (c) Profile's script never updates `aria-selected`, leaving it permanently false after any click | Gallery 896, 1011; Profile 725, 737, 914–917 | `VZ-A11Y-001`; invalid ARIA is worse than none |
| C19 | **The closed account menu keeps 10 items in the tab order** (`opacity: 0; pointer-events: none`, never `hidden`/`inert`) | Gallery 208–214 | `VZ-A11Y-001`; the same defect class as Search's closed sheet |
| C20 | **The Profile has zero `:focus-visible` rules**; Gallery has three but none for `.pill`, `.tool-btn`, `.photo`, `.collection`, `.btn`, nav links, `.link-inline` or the mobile tabs. Gallery's one designed ring measures ≈1.85:1 against white | Profile whole file; Gallery 189–190, 258–262, 167–174 | `VZ-A11Y-001` ("visible focus"); WCAG 1.4.11 needs 3:1 |
| C21 | **The Follow button rewrites its own `innerHTML`** — destroying the accessible name of the focused element — with no `aria-pressed`, no pending state, no failure path and **no authentication gate** | Profile 927–932 | `DESIGN_BRIEF.md`'s Favorite-proof paragraph applies verbatim to Follow; `VZ-FOLLOW-001`; `VZ-A11Y-001` |
| C22 | **A user-supplied outbound link with no hardening** — no `rel="nofollow ugc noopener"`, no `target`, no scheme shown, inline-styled colour | Profile 665–668 | `AGENTS.md`: "Never trust client MIME, filenames, EXIF, SQL fragments, **remote URLs**" |
| C23 | **Two keyboard shortcuts advertised and neither implemented** — `⌘K` in the search field, `⌘,` on Account Settings. No ledger entry defines a global command palette or a settings hotkey | Gallery 783, 856 | `DESIGN_BRIEF.md`: "Reject… dead links, no-op handlers" |
| C24 | **No empty / zero-content state anywhere.** The Gallery is the first page an operator sees after `vizra setup`, on an instance with 0 photos, 0 collections, 0 featured series and 1 user | both pages | `DESIGN_BRIEF.md`: "Document… loading/empty/error/success/disabled states" |
| C25 | **No anonymous variant.** Both pages render a signed-in avatar; the Profile renders Follow and Message with no session and no sign-in path. `VZ-EXPLORE-001`'s negative case, `VZ-AUTH-005` registration policy and `VZ-ADMIN-003` privacy mode all change these pages | both pages | `DESIGN_BRIEF.md`; `VZ-PRIVACY-001` |
| C26 | **No safety or visibility treatment** on any of the 19 photo cards, 4 collection cards, 3 album cards or 3 series cards | both pages | `VZ-NSFW-001` (blur in listings), `VZ-PRIVACY-001/002` |
| C27 | **The Gallery's own logo is `href="#"`** on the home page | Gallery 775 | `DESIGN_BRIEF.md`: "Reject dead links" |
| C28 | **Alt-text regression on the Profile** — `alt=""` on 22 of its 24 images (all 10 photos, all 3 series, all 9 album thumbnails), keeping alt only on the cover and the profile avatar. Gallery is materially better: real alt on the hero and all 9 Discover photos, `alt=""` only on 3 artist avatars | Profile 761–879; Gallery 918–1051 | `VZ-A11Y-001`; `VZ-LIBRARY-002` makes alt text an editable field |
| C29 | **Dead CSS and dead tokens** — `.pill .dot` (Gallery 459), `.photo.hero-row` (Gallery 756), `.shell` (Profile 52, declared and used by nothing), `--accent-soft` (Gallery, 0 uses), `--shadow-lg` (Gallery, 0 uses), `--radius-sm` (both, 0 uses), `@media (min-width: 1100px) { .grid … }` (Profile 600–602, a no-op duplicate) | — | `VZ-DESIGN-001` token discipline |
| C30 | **Layout misalignment between ~1256px and 1272px on the Profile** — the 1240px-max cover is left-aligned (`margin: 12px 16px 0`) while every region beneath it is centred, until `min-width: 1272px` adds `margin: auto` | Profile 125–134 | rendering defect |

---

## f. Control-to-action matrix

Action IDs follow the dotted convention already used in `docs/quality/ui-controls.json`
(`surface.component.verb`). **Proposed** means proposed by this inventory — none exists in
`ui-controls.json` yet except where the "Existing control ID" column names one. Milestones are from
`docs/MILESTONES.md`; where a control's ledger IDs span milestones, the **latest** governs when the
control can be fully honest.

`NO LEDGER ID` means: this control implies a capability that no entry in `docs/quality/features.json`
covers. Per the task brief, **none has been invented.**

Rows are numbered `GAL-nn` (Gallery) and `PRO-nn` (Profile), matching the `#` columns in §b and §c.

### f.1 Shared shell — both pages

| # | Control (visible label) | Element | Proposed action ID | Existing control ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|---|
| GAL-1 / PRO-1 | Brand → home | `<a class="brand">` | `shell.brand.home` | — | `VZ-BRAND-001` (logo), `VZ-BRAND-002` (homepage style), `VZ-EXPLORE-001` (if home routes to explore) | **M5** / **M5** / M3 |
| GAL-2 / PRO-2 | Search field | `<input placeholder="Search photographers, places, moods…">` | `search.query.submit` | `shell.nav.search` | `VZ-SEARCH-001` | **M3** |
| GAL-3 | `⌘K` shortcut hint | inline `<span>` | `search.query.hotkey` | — | **NO LEDGER ID** — no entry defines a global search hotkey or command palette. `VZ-ALBUM-003`, `VZ-LIBRARY-001` and `VZ-ADMIN-001` define shortcuts scoped to their own surfaces | n/a |
| — | (implied) typeahead suggestions | *absent from both mockups* | `search.query.suggest` | — | `VZ-SEARCH-003` | M3 |
| GAL-4 | `Discover` | `<a class="nav-link" href="#">` | `shell.nav.explore` | `shell.nav.explore` | `VZ-EXPLORE-001` | M3 |
| GAL-5 | `Collections` | `<a class="nav-link" href="#">` | `shell.nav.collections` | — | `VZ-COLLECTION-001` | **M5** |
| GAL-6 | `Artists` | `<a class="nav-link" href="#">` | `shell.nav.people` | — | `VZ-EXPLORE-001` (users listing) | M3 |
| GAL-7 | `Surprise` | `<a class="nav-pill" href="#">` | `shell.nav.random` | — | `VZ-EXPLORE-002` (`?random` shows a random public safe image when enabled) | M3 |
| GAL-8 / PRO-3 | Notifications | `<button class="icon-btn">` | `shell.nav.notifications` | `shell.nav.notifications` | `VZ-NOTIFY-001` | **M2** |
| — | (implied) unread badge | *absent from both* | `shell.nav.notifications.badge` | `shell.nav.notifications` (`states: badge-count`) | `VZ-NOTIFY-001` | **M2** |
| GAL-9 / PRO-4 | Upload | Gallery `<a href="Upload Studio.html">`; Profile dead `<button>` | `shell.nav.upload` | `shell.nav.upload` | `VZ-UPLOAD-001`, `VZ-UPLOAD-005` (guest uploads), `VZ-UPLOAD-009` (on-page vs `/upload` route) | M1 / M3 / M3 |
| GAL-10 / PRO-5 | Account avatar `MK` | Gallery `<button aria-haspopup="menu">`; Profile inert `<span>` | `shell.nav.account` | `shell.nav.account` | `VZ-AUTH-001`, `VZ-ACCOUNT-001` | M1 / M2 |

### f.2 Gallery — account menu

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| GAL-11 | `View Profile` | `<a href="Artist Profile.html" role="menuitem">` | `shell.account.profile` | `VZ-PROFILE-001` | **M2** |
| GAL-12 | `My Photos` (`312`) | `<a role="menuitem">` | `shell.account.library` | `VZ-LIBRARY-001` | M1 |
| GAL-13 | `Albums` | `<a role="menuitem">` | `shell.account.albums` | `VZ-ALBUM-001` | M1 |
| GAL-14 | `Insights` | `<a role="menuitem">` | `shell.account.stats` | `VZ-STATS-002` (member statistics, **`full` profile**). `VZ-STATS-001` is the *operator* dashboard at `/admin`, not a member surface | **M6** |
| GAL-15 | `Upload Studio` | `<a role="menuitem">` | `shell.nav.upload` | as GAL-9 | M1 / M3 |
| GAL-16 | `Edit Profile` | `<a role="menuitem">` | `shell.account.profile.edit` | `VZ-ACCOUNT-001` | **M2** |
| GAL-17 | `Account Settings` (`⌘,`) | `<a role="menuitem">` | `shell.account.settings` | `VZ-ACCOUNT-001`, `VZ-AUTH-003`, `VZ-ACCOUNT-004`. The `⌘,` hotkey → **NO LEDGER ID** | **M2** / n/a |
| GAL-18 | `Notifications & Privacy` | `<a role="menuitem">` | `shell.account.notify-prefs` | `VZ-ACCOUNT-004` (notification preferences), `VZ-PRIVACY-001` (defaults), `settings.privacy.defaults` | **M2** / M1 |
| GAL-19 | `Help & Feedback` | `<button role="menuitem">` | `shell.account.help` | `VZ-PAGE-001` **only if** the owner authored such a page. There is no built-in help, feedback or support system → otherwise **NO LEDGER ID** | **M5** / n/a |
| GAL-20 | `Sign Out` | `<button class="menu-item danger" role="menuitem">` | `auth.session.end` | `VZ-AUTH-001` ("sign-out, session revocation") | M1 |
| — | **Favorites** | *absent — required by `ui-controls.json` `shell.nav.account`* | `shell.account.favorites` | `VZ-FAVORITE-001` (`/u/{username}/favorites`) | **M2** |
| — | **Blocks** | *absent* | `shell.account.blocks` | `VZ-BLOCK-001` (`/settings/blocks`) | **M2** |
| — | **Admin console** (owner/admin roles) | *absent* | `shell.nav.admin` | `VZ-ADMIN-001`, `VZ-AUTH-004` | **M2** |

### f.3 Gallery — hero and categories

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| — | Hero slot (cover + eyebrow + title + paragraph + CTA) | `<section class="hero">` | `home.hero.render` | `VZ-BRAND-002` ("homepage styles… multiple cover images; title/paragraph; CTA") is exactly this slot, as an **owner** setting | **M5** |
| — | Hero subject "Featured Series" | text | `home.hero.subject` | **NO LEDGER ID** as a series. As a featured **album**: `VZ-ALBUM-001` (M1); as site-featured content: `VZ-EXPLORE-003` (**M6**, `full`) or operator curation under `VZ-ADMIN-002` (M2) | n/a |
| GAL-21 | `Read the Narrative` | `<a class="btn btn-primary" href="#">` | `home.hero.cta.primary` | **NO LEDGER ID** — a long-form narrative attached to a body of work. Nearest is `VZ-PAGE-001` (owner-authored site pages, **M5**), which is not per-photographer editorial. As a generic owner CTA: `VZ-BRAND-002` **M5** | n/a |
| GAL-22 | `View Collection` | `<a class="btn btn-secondary" href="#">` | `home.hero.cta.secondary` | `VZ-COLLECTION-001` (**M5**) if "collection"; `VZ-ALBUM-001` (M1) if it means album | **M5** |
| GAL-23 | Category: `For You` | `<button class="pill active">` | `explore.scope.foryou` | **NO LEDGER ID.** `VZ-EXPLORE-001` enumerates recent / trending / popular / **following**; a personalised recommendation feed is none of these. Nearest `VZ-FEED-001` (following feed, `full`, M5) — a follow graph is not a recommender | n/a |
| GAL-24…32 | `Landscapes` · `Portraiture` · `Architecture` · `Street` · `Analog` · `Minimalism` · `Wildlife` · `Night Sky` · `Abstract` | `<button class="pill">` ×9 | `explore.category.select` **or** `explore.tag.select` | `VZ-CATEGORY-001` (admin-defined categories, `/category/{key}`) **or** `VZ-TAG-001` (tag pages, `/tag/{name}`). **The mockup conflates the two; which one these are is an owner/contract decision.** `Analog` is additionally the unmodelled film facet `INVENTORY-search.md` §h.4 #50 already flagged — as a film/analogue classification: **NO LEDGER ID** | M3 / M3 / n/a |

### f.4 Gallery — artists strip

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| — | Section: "Artist Showcases… shaping the way we see this month" | `<section class="artists">` | `home.people.featured` | **NO LEDGER ID** as an editorially curated monthly people showcase. `VZ-EXPLORE-001` has a **users** listing (M3) but no curated showcase; `VZ-EXPLORE-003` (**M6**, `full`) features *content*, not people | n/a |
| GAL-33 | `View Profile ›` ×3 | `<a href="#" class="link-inline">` | `home.people.open` | `VZ-PROFILE-001` | **M2** |
| — | Artist avatar and name (inert; must be links) | `.artist-avatar`, `.artist-name` | `home.people.open` | `VZ-PROFILE-001` | **M2** |
| — | `.artist-style` one-liner (`Urban Brutalism` etc.) | `.artist-style` | `home.people.style.render` | **NO LEDGER ID** — `VZ-ACCOUNT-001`'s field list is username, display name, bio, website, avatar, background, language, timezone, privacy. There is no "style" or "specialty" field | n/a |
| — | Four bare `.artist-thumb` cards (inert) | `<div class="artist-thumb">` | — | **NO LEDGER ID** as drawn (decorative filler inside a people list). If they are photos: `VZ-VIEWER-001` M1 | n/a |
| — | **Follow** | *absent from this carousel* (Search's artist cards had one) | `home.people.follow` | `VZ-FOLLOW-001` | **M2** |
| — | Handle, photo count, follower count | *absent* | — | `VZ-PROFILE-001`, `VZ-FOLLOW-001` | **M2** |

### f.5 Gallery — collections

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| GAL-36 | `Browse all ›` | `<a href="#" class="link-inline">` | `collections.index.open` | `VZ-COLLECTION-001` (`/collections`) | **M5** |
| GAL-37 | Collection card ×4 | `<a class="collection" href="#">` | `collections.item.open` | **Ambiguous by design (C13).** As grouped own-albums: `VZ-COLLECTION-001` **M5**. As a curated set of other people's photos with a named curator: `VZ-GALLERY-001` **M5**. **Owner decision required** | **M5** |
| — | `Curated by <name>` | `.collection-curator` | `collections.item.curator.open` | `VZ-PROFILE-001` — **and it must be a link, which it is not** | **M2** |
| — | `24 images` chip | `.chip` | `collections.item.count.render` | `VZ-COLLECTION-001` / `VZ-GALLERY-001`; the count must be permission-aware ("sharing shows only albums the viewer may see") | **M5** |

### f.6 Gallery — discover grid

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| — | Section "Discover Latest" | `<section>` | `explore.recent.render` | `VZ-EXPLORE-001` (recent) | M3 |
| — | `refreshed hourly` | text | `explore.freshness.render` | **NO LEDGER ID** — the same public index-freshness claim `INVENTORY-search.md` §h.7 #8 flagged as "refreshed moments ago" | n/a |
| GAL-38 | View: `Grid` | `<button class="tool-btn active" aria-label="Grid">` | `explore.view.grid` | `VZ-LISTING-001` is an **owner** setting ("fixed/fluid grid, columns per device"), not a per-viewer toggle → **NO LEDGER ID** for a viewer-level density switch | M3 (owner) / n/a |
| GAL-39 | View: `Mosaic` | `<button class="tool-btn" aria-label="Mosaic">` | `explore.view.mosaic` | as GAL-38 | same |
| GAL-40 | `Filter` | inline-styled `<button aria-label="Filter">` | `explore.filters.open` | `VZ-SEARCH-002` is *search* filters (`full`, **M5**); `VZ-EXPLORE-001` enumerates no explore facets → **as an explore filter: NO LEDGER ID** | **M5** / n/a |
| GAL-41 | Open photo ×9 | `<a class="photo" href="#">` | `explore.result.open` | `VZ-VIEWER-001`; route shape `VZ-SHARE-003` | M1 / M3 |
| — | `.heart` count ×9 (display) | `<span class="heart">` | `explore.result.favorites.render` | `VZ-FAVORITE-001` ("public 'favorited by' count… where the item is public") | **M2** |
| — | **Favourite control** | *absent — the heart is a `<span>`* | `explore.result.favorite` | `VZ-FAVORITE-001`; `ui-controls.json` `photo.favorite` | **M2** |
| — | `.author` handle ×9 (display; must be a link) | `<span class="author">` | `explore.result.author.open` | `VZ-PROFILE-001` | **M2** |
| GAL-44 | `Load more` | `<button class="btn btn-secondary">` | `explore.page.more` | `VZ-EXPLORE-001`; `VZ-LISTING-001` ("classic/endless pagination" is an **owner** setting, and "endless scroll accessible (keyboard + announce)" is its success case) | M3 |
| — | **Card affordances the ledger expects and the mockup omits** | — | — | safety-level blur (`VZ-NSFW-001`, M2), visibility marker (`VZ-PRIVACY-001` M1 / `VZ-PRIVACY-002` M5), title (`VZ-UPLOAD-006` M3), rating (`VZ-RATING-001` M2), comment count (`VZ-COMMENT-001` M2), download (`VZ-DOWNLOAD-001` M3), share (`VZ-SHARE-001` M3), report (`VZ-REPORT-001` M2), add-to-album (`VZ-ALBUM-001` M1) | — |

### f.7 Gallery — editorial, footer, mobile tabs

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| — | Editorial article (title, byline, body) | `.editorial` | `editorial.article.render` | **NO LEDGER ID.** Nearest `VZ-PAGE-001` (owner-authored custom pages, **M5**) — not a per-photographer editorial journal with its own author | n/a |
| GAL-45 | `Play interview` (28 min audio) | `<button class="play-btn" aria-label="Play interview">` | `editorial.audio.play` | **NO LEDGER ID.** `VZ-MEDIA-002`'s format matrix is images; `VZ-MEDIA-005` is MP4/MOV/WebM video. **There is no audio media type in Vizra** | n/a |
| GAL-46 | `About` | `<a href="#">` | `site.page.open` | `VZ-PAGE-001` | **M5** |
| GAL-47 | `Terms` | `<a href="#">` | `site.page.terms` | `VZ-PAGE-001` ("ToS page type shown at consent"), `VZ-CONSENT-001` | **M5** |
| GAL-48 | `Privacy` | `<a href="#">` | `site.page.privacy` | `VZ-PAGE-001` | **M5** |
| GAL-49 | `Licensing` | `<a href="#">` | `site.page.licensing` | `VZ-PAGE-001`; the underlying per-item licences are `VZ-LICENSE-001` (`full`) | **M5** |
| GAL-50 | `Contact` | `<a href="#">` | `site.page.contact` | `VZ-PAGE-001`; `VZ-SERVICES-001` ("forced contact-page" CAPTCHA mode); `VZ-EMAIL-001` | **M5** / M2 |
| GAL-51 | Footer `Share` | `<a class="icon-btn" href="#" aria-label="Share">` | — | **NO LEDGER ID.** `VZ-SHARE-001/002` are per-**item** links and embeds; no site-level share affordance exists | n/a |
| GAL-52 | Footer `Email` | `<a class="icon-btn" href="#" aria-label="Email">` | `site.page.contact` | as GAL-50 if it is a contact route; as drawn (`href="#"`, no target) → **NO LEDGER ID** | **M5** / n/a |
| — | **`Powered by Vizra`** | *absent* | `site.footer.attribution` | `VZ-BRAND-005` | **M5** |
| — | **Language chooser** | *absent* | `site.footer.language` | `VZ-I18N-001` | **M5** |
| — | **Lucide attribution** | *absent* | — | `DESIGN_BRIEF.md` ("attribution preserved [LUCIDE-LICENSE]") | — |
| — | **Cookie / consent notice** | *absent* | `site.consent.render` | `VZ-CONSENT-001` | **M5** |
| GAL-53 | Mobile: `Home` | `<button class="tab active">` | `shell.tabbar.home` | `VZ-BRAND-002` / `VZ-EXPLORE-001` | **M5** / M3 |
| GAL-54 | Mobile: `Explore` (`aria-label="Discover"`, magnifier) | `<button class="tab">` | `shell.tabbar.explore` | `VZ-EXPLORE-001`; the glyph implies `VZ-SEARCH-001` | M3 |
| GAL-55 | Mobile: Upload FAB | `<a class="tab upload" href="Upload Studio.html">` | `shell.nav.upload` | as GAL-9 | M1 |
| GAL-56 | Mobile: `Saved` | `<button class="tab">` | `shell.tabbar.saved` | `VZ-FAVORITE-001` **if** "Saved" means the favourites listing; if it means a separate bookmark/read-later list → **NO LEDGER ID** (the same unresolved question as `INVENTORY-search.md` §h.7 #1) | **M2** / n/a |
| GAL-57 | Mobile: `You` | `<a class="tab" href="Artist Profile.html">` | `shell.tabbar.profile` | `VZ-PROFILE-001` | **M2** |

### f.8 Profile — header and identity

| # | Control / field | Element | Proposed action ID | Existing control ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|---|
| PRO-6 | `‹ Artists` back | `<a class="back-btn">` | `profile.back` | — | `VZ-EXPLORE-001` (users listing) | M3 |
| — | Cover image | `.cover img` | `profile.cover.render` | — | `VZ-ACCOUNT-001` / `VZ-PROFILE-001` ("avatar/**background**"); asset storage `VZ-STORAGE-015`. **Ledger says "background"; the mockup says "cover"** | **M2** / M4 |
| — | Avatar | `.profile-avatar img` | `profile.avatar.render` | — | `VZ-ACCOUNT-001` | **M2** |
| — | Display name | `<h1 class="profile-name">` | `profile.name.render` | — | `VZ-ACCOUNT-001`, `VZ-PROFILE-001` | **M2** |
| — | **Verified badge** | `<span class="verified" aria-label="Verified">` | `profile.verified.render` | — | **NO LEDGER ID.** No entry defines identity verification. `VZ-AUTH-004` roles (owner/admin/manager/member/guest) are not a verification mark; `VZ-ADMIN-USERS-001` is operator user management | n/a |
| — | Handle | `.profile-handle` | `profile.handle.render` | — | `VZ-ACCOUNT-001` (username) | **M2** |
| — | `· Urban Brutalism` (style) | `.profile-handle` | `profile.style.render` | — | **NO LEDGER ID** (as GAL artist-style) | n/a |
| — | **Location** `Mexico City · Berlin` | `.profile-line .chip` | `profile.location.render` | — | **NO LEDGER ID.** Not in `VZ-ACCOUNT-001`'s field list. `VZ-GEO-001` is per-**photo** geotags with geo-privacy (`full`, M5), not a profile location | n/a |
| — | `Member since 2019` | `.profile-line .chip` | `profile.joined.render` | — | **NO LEDGER ID** as a displayed public field. The datum exists; nothing defines exposing it, and `VZ-PROFILE-001` ("private profiles hide identity") makes it a policy question | n/a |
| PRO-7 | Website `alexrivera.studio` | `<a class="chip" href="#">` | `profile.website.open` | — | `VZ-ACCOUNT-001` (website field) | **M2** |
| PRO-8 | **`Follow`** | `<button id="followBtn">` | `profile.follow` | **`profile.follow`** | `VZ-FOLLOW-001` | **M2** |
| — | Follow **pending / request** state | *absent* | `profile.follow.pending` | — | `VZ-FOLLOW-002` (`full`) | **M5** |
| PRO-9 | **`Message`** | `<button class="btn btn-secondary">` | `profile.message` | — | `VZ-MESSAGE-001` (`full`) | **M5** |
| PRO-10 | **Share** (profile) | `<button aria-label="Share">` | `profile.share` | — | `VZ-SHARE-001/002` are per-**item** links and embeds. Nearest for a user URL is `VZ-SHARE-003` (SEO routes for users, M3). **As a profile share dialog: NO LEDGER ID** | M3 / n/a |
| PRO-11 | **More** (overflow) | `<button aria-label="More">` | `profile.overflow.open` | — | The menu that must hold **Block** (`VZ-BLOCK-001`, `ui-controls.json` `profile.block`, surface "profile menu") and **Report** (`VZ-REPORT-001`, "report… users"). The affordance is drawn; the contents are not | **M2** |
| — | **Block** | *absent (inside More)* | `profile.block` | **`profile.block`** | `VZ-BLOCK-001` | **M2** |
| — | **Report user** | *absent (inside More)* | `profile.report` | — | `VZ-REPORT-001` | **M2** |
| — | **Owner actions** (Edit profile / Edit cover / Edit avatar) | *absent* | `profile.edit` | — | `VZ-ACCOUNT-001` | **M2** |

### f.9 Profile — bio and stats card

| # | Control / field | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| — | Bio (2 paragraphs, `<i>` markup) | `.bio` | `profile.bio.render` | `VZ-ACCOUNT-001` (bio). **Whether it permits multi-paragraph rich text is a contract question the mockup silently answers "yes"** — sanitisation applies (`VZ-COMMENT-001`'s sanitisation discipline, `VZ-PAGE-001`'s "sanitized HTML") | **M2** |
| — | Stat `312 Photos` (inert; must be a link) | `.stat` | `profile.stats.photos` | `VZ-PROFILE-001` ("counters"; "counters exclude private items") | **M2** |
| — | Stat `24 Albums` (inert) | `.stat` | `profile.stats.albums` | `VZ-ALBUM-001`, `VZ-PROFILE-001` | M1 / **M2** |
| — | Stat `48.2k Followers` (inert) | `.stat` | `profile.stats.followers` | `VZ-FOLLOW-001` ("lists at `/{username}/followers` and `/following`; counts live"). **Must be a link; it is a `<div>`** | **M2** |
| — | **`Following` count** | *absent* | `profile.stats.following` | `VZ-FOLLOW-001` | **M2** |
| — | **`Favorites` count/link** | *absent* | `profile.stats.favorites` | `VZ-FAVORITE-001` (`/u/{username}/favorites`) | **M2** |
| — | `Most used camera · Leica Q3` | `.stats-list .row` | `profile.stats.camera` | **NO LEDGER ID.** EXIF is read at M1 (`VZ-MEDIA-004`) and camera/lens are *search facets* at M5 (`VZ-SEARCH-002`, "camera finder pages by brand/model from EXIF"), but **no entry defines a public per-profile camera aggregate**, and such an aggregate leaks over private items unless computed inside an authorized query | n/a |
| — | `Favorite lens · 28mm f/1.7` | `.stats-list .row` | `profile.stats.lens` | **NO LEDGER ID** (same) | n/a |
| — | `Style · Brutalism / B&W` | `.tag` ×2 | `profile.stats.style` | `VZ-TAG-001` **if** these are the member's top tags (M3); as a profile-level self-description field → **NO LEDGER ID** | M3 / n/a |
| — | `Available for commissions` + `Booking Q3 2026 · Architecture & editorial` | `.avail` | `profile.availability.render` | **NO LEDGER ID.** No availability, booking or commissions concept exists | n/a |
| PRO-12 | **`Hire`** | `<a class="btn btn-sm" href="#">` | `profile.hire` | **NO LEDGER ID.** Nearest contact primitive is `VZ-MESSAGE-001` (`full`, M5). `README.md` standing note 3: "Vizra has no billing product" | n/a |

### f.10 Profile — tabs and toolbar

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| PRO-14 | Tab `Photos` (`312`) | `<button role="tab" aria-selected="true">` | `profile.tab.photos` | `VZ-PROFILE-001` ("default view files or albums per site setting"); `GET /api/v1/users/{u}/photos` | **M2** |
| PRO-15 | Tab `Albums` (`24`) | `<button role="tab">` | `profile.tab.albums` | `VZ-ALBUM-001`, `VZ-PROFILE-001` | M1 / **M2** |
| PRO-16 | Tab `Featured` (`6`) | `<button role="tab">` | `profile.tab.featured` | **NO LEDGER ID.** Nothing lets a member pin or feature their own work on their own profile. `VZ-EXPLORE-003` is an **operator/site-level** featured Explore (`full`, **M6**); `VZ-ALBUM-001`'s cover is per-album, not a profile pin | n/a |
| PRO-17 | Tab `About` | `<button role="tab">` | `profile.tab.about` | `VZ-ACCOUNT-001` (bio/website). **No About panel exists; the bio sits above the tab strip** | **M2** |
| — | **Tab: Favorites** | *absent* | `profile.tab.favorites` | `VZ-FAVORITE-001` (`/u/{username}/favorites`) | **M2** |
| — | **Tab: Followers / Following** | *absent* | `profile.tab.followers` | `VZ-FOLLOW-001` | **M2** |
| — | **Search within the profile** | *absent* | `profile.search` | `VZ-PROFILE-001` explicitly requires "search within the profile" | **M2** |
| — | **Tab: Tags** | *absent* | `profile.tab.tags` | `VZ-TAG-001` (top tags) | M3 |
| — | **Tab: Collections** | *absent* | `profile.tab.collections` | `VZ-COLLECTION-001` | **M5** |
| — | **Tab: Galleries** | *absent* | `profile.tab.galleries` | `VZ-GALLERY-001` | **M5** |
| — | **Tab: Groups** | *absent* | `profile.tab.groups` | `VZ-GROUP-001` | **M5** |
| PRO-18 | Sort `Recent` | `<button class="sort">` | `profile.sort.open` | `VZ-ALBUM-003` / `VZ-PROFILE-001` listing sorts (recent / oldest / most viewed / most favorited / A-Z). The mockup shows one value and **no menu** | M3 / **M2** |
| PRO-19 | View `Grid` | `<button class="view-btn active" aria-label="Grid">` | `profile.view.grid` | `VZ-LISTING-001` is an **owner** setting → **NO LEDGER ID** as a viewer toggle | M3 (owner) / n/a |
| PRO-20 | View `Rows` | `<button class="view-btn" aria-label="Rows">` | `profile.view.rows` | as PRO-19 | same |

### f.11 Profile — content sections

| # | Control | Element | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| PRO-21 | `See all ›` (series) | `<a href="#" class="link-inline">` | `profile.featured.all` | as PRO-16 → **NO LEDGER ID** | n/a |
| PRO-22 | Series card ×3 | `<a class="series-card" href="#">` | `profile.featured.open` | **NO LEDGER ID** as "series". As albums (which they demonstrably are — same names, same counts as the Albums section): `VZ-ALBUM-001` M1 | n/a / M1 |
| — | `24 frames` eyebrow | `.series-eyebrow` | `profile.featured.count.render` | `VZ-ALBUM-003` ("album shows title, **count**, date") if albums | M3 |
| PRO-23 | `Open library ›` | `<a href="#" class="link-inline">` | `profile.photos.all` | **Conflict:** `VZ-LIBRARY-001` is the **owner's private** camera roll at `/library` (M1). From a visitor's view of someone else's profile this must be `VZ-PROFILE-001`'s public listing (**M2**), not `/library`. **Vocabulary and permission conflict** | **M2** |
| PRO-24 | Photo card ×10 | `<a class="photo" href="#">` | `profile.photo.open` | `VZ-VIEWER-001`; route `VZ-SHARE-003` | M1 / M3 |
| — | Photo caption | `.photo .meta span` | `profile.photo.title.render` | `VZ-UPLOAD-006` (title on upload), `VZ-LIBRARY-002` (edit title) | M3 |
| — | `New` badge | `.badge-new` | `profile.photo.recency.render` | **NO LEDGER ID** — nothing defines a recency badge or its window. `VZ-EXPLORE-001` has a "recent" **listing**, not a per-card badge | n/a |
| — | `.heart` count ×10 (display) | `<span class="heart">` | `profile.photo.favorites.render` | `VZ-FAVORITE-001` (public count) | **M2** |
| — | **Favourite control** | *absent* | `profile.photo.favorite` | `VZ-FAVORITE-001`; `photo.favorite` | **M2** |
| PRO-26 | `All 24 ›` | `<a href="#" class="link-inline">` | `profile.albums.all` | `VZ-ALBUM-001`, `VZ-PROFILE-001` | M1 / **M2** |
| PRO-27 | Album card ×3 | `<a class="album" href="#">` | `profile.album.open` | `VZ-ALBUM-001`; header/meta `VZ-ALBUM-003` | M1 / M3 |
| — | **3-image mosaic cover** | `.album-thumbs` | `profile.album.cover.render` | `VZ-ALBUM-001` specifies a **single chosen cover** ("public cover required when album is public"). A mosaic from child covers is `VZ-COLLECTION-001` (**M5**). **The mockup applies the collection treatment to albums** | M1 / **M5** |
| — | `24 photos · Updated 3 days ago` | `.album-meta` | `profile.album.meta.render` | `VZ-ALBUM-003` ("title, count, date") | M3 |
| — | **Album privacy marker** | *absent* | `profile.album.visibility.render` | `VZ-ALBUM-002` (public / private / link-only / password) | M1 |
| — | **Album favourite / comment count** | *absent* | — | `VZ-ALBUM-004` | M3 |
| — | `© 2026 Lumen Atlas` page-end | `.page-end` | `site.footer.attribution` | `VZ-BRAND-005` | **M5** |
| PRO-28…32 | Mobile tabs | `.tab-m` ×5 | as GAL-53…57 | as GAL-53…57 | as GAL-53…57 |

---

## g. Summary — controls with NO LEDGER ID

Numbered for citation. None of these was invented; each names the nearest ledger neighbour and why
it does not cover the control.

1. **`⌘K` global search shortcut** and **`⌘,` settings shortcut** — GAL-3, GAL-17. No command-palette
   or global-hotkey entry exists; the shortcut entries that do exist (`VZ-ALBUM-003`,
   `VZ-LIBRARY-001`, `VZ-ADMIN-001`) are scoped to their own surfaces.
2. **`For You` category pill** — GAL-23. `VZ-EXPLORE-001` enumerates recent / trending / popular /
   following; a personalised recommender is none of them.
3. **`Analog` category pill** — GAL-28. The same unmodelled film/analogue classification
   `INVENTORY-search.md` §h.4 #50 flagged.
4. **The artist-showcase section itself** ("shaping the way we see this month") and the four inert
   `.artist-thumb` cards inside it — a curated monthly people showcase; `VZ-EXPLORE-001` has a plain
   users listing, `VZ-EXPLORE-003` features content not people.
5. **`.artist-style` / `· Urban Brutalism`** — a "style"/specialty profile field that
   `VZ-ACCOUNT-001` does not have.
6. **`Read the Narrative`** and **the whole Editorial Journal region** — GAL-21, GAL-45's section.
   No article entity; `VZ-PAGE-001` is owner-authored site pages.
7. **`Play interview` — a 28-minute audio programme** — GAL-45. **Vizra has no audio media type**
   (`VZ-MEDIA-002` is images, `VZ-MEDIA-005` is video).
8. **`refreshed hourly`** public index-freshness label — the same class as Search's "refreshed
   moments ago".
9. **View-density switchers as viewer controls** — GAL-38, GAL-39, PRO-19, PRO-20.
   `VZ-LISTING-001` is an owner setting.
10. **The Discover `Filter` button** — GAL-40, as an *explore* facet surface. `VZ-SEARCH-002` is
    search filters (`full`, M5); `VZ-EXPLORE-001` enumerates no facets.
11. **Footer `Share`** — GAL-51. `VZ-SHARE-001/002` are per-item.
12. **Footer `Email`** as drawn (no target) — GAL-52.
13. **`Help & Feedback`** — GAL-19, unless the owner authored a `VZ-PAGE-001` page; there is no
    built-in help/feedback/support system.
14. **Mobile `Saved` tab** — GAL-56, PRO-31 — if it means a bookmark/read-later list rather than
    favourites. Vizra has favourites, albums, collections and galleries, but **no bookmark
    primitive**. (Unchanged from `INVENTORY-search.md` §h.7 #1; the Gallery makes it worse by using
    the same Bookmark glyph for the "Albums" menu item.)
15. **The "Series" entity, everywhere** — hero "Featured Series", account-menu stat "18 Series",
    Profile "Featured Series" section, Profile tab "Featured 6", `.series-card` ×3.
16. **Profile `Featured` tab and `See all ›`** — PRO-16, PRO-21. Members cannot pin or feature their
    own work; `VZ-EXPLORE-003` is operator/site-level and `full`/M6.
17. **The verified badge** — PRO. No identity-verification feature exists.
18. **Profile location** (`Mexico City · Berlin`) — not a `VZ-ACCOUNT-001` field; `VZ-GEO-001` is
    per-photo geotags.
19. **`Member since 2019`** as a displayed public field.
20. **`Most used camera`** and **`Favorite lens`** — public per-profile EXIF aggregates that nothing
    defines and that leak over private items unless computed inside an authorized query.
21. **`Style · Brutalism / B&W`** as a profile field (M3 `VZ-TAG-001` if they are top tags).
22. **`Available for commissions` / `Booking Q3 2026` / `Hire`** — PRO-12. No availability, booking
    or commissions concept; Vizra has no billing product.
23. **Profile `Share`** as a share dialog for a *user* — PRO-10. `VZ-SHARE-001/002` are per-item.
24. **`New` recency badge** on a photo card.
25. **Collections as drawn** — GAL-37 is not cleanly `VZ-COLLECTION-001` **or** `VZ-GALLERY-001`; as
    "a themed set with a named curator and an image count" it is `VZ-GALLERY-001` wearing
    `VZ-COLLECTION-001`'s name. **Owner decision required**, not a NO LEDGER ID in itself, but it
    cannot be implemented until decided.

## h. Summary — controls whose backend lands after M1, and after M3

Both pages are themselves **M3 surfaces at the earliest** — the Gallery is the explore/home surface
(`VZ-EXPLORE-001`, `VZ-EXPLORE-002`, M3) and the Profile is `VZ-PROFILE-001` (M2) with M3 listing
behaviour. Neither can be built at M1.

**After M1 (M2 and later)** — the controls that cannot be honest in the golden-path milestone:

- Notifications and the unread badge — GAL-8, PRO-3 — `VZ-NOTIFY-001`, **M2**.
- Every profile link on both pages — GAL-11, GAL-33, GAL-57, PRO-14, PRO-17, PRO-28…32, the nine
  inert `.author` handles, the four collection curators, the three inert artist names —
  `VZ-PROFILE-001`, **M2**.
- **Follow** — PRO-8 — `VZ-FOLLOW-001`, **M2**; and the missing Follow in the Gallery artists strip.
- Every favourite count (19 across the two pages) and the missing favourite control —
  `VZ-FAVORITE-001`, **M2**.
- Block and Report behind PRO-11 "More" — `VZ-BLOCK-001`, `VZ-REPORT-001`, **M2**.
- Bio, avatar, cover/background, website, Edit Profile, Account Settings, Notifications & Privacy —
  GAL-16…18, PRO fields — `VZ-ACCOUNT-001`, `VZ-ACCOUNT-004`, **M2**.
- NSFW blur and safety filtering on every listing card — `VZ-NSFW-001`, **M2**.
- Explore/Discover listings, category or tag pages, `Load more` pagination, sort orders, search,
  per-item view counts, share routes — GAL-4, GAL-6, GAL-7, GAL-24…32, GAL-41, GAL-44, PRO-6,
  PRO-18, PRO-23, PRO-24 — `VZ-EXPLORE-001/002`, `VZ-CATEGORY-001`, `VZ-TAG-001`, `VZ-SEARCH-001`,
  `VZ-LISTING-001`, `VZ-SHARE-003`, `VZ-ALBUM-003`, **M3**.

**After M3 (M4 and later)** — the controls that still cannot be honest when both pages' own
milestone closes:

| Control | Ledger ID | Milestone |
|---|---|---|
| `Collections` nav link, `Browse all ›`, 4 collection cards, hero `View Collection`, Profile Collections tab | `VZ-COLLECTION-001` (`full`) | **M5** |
| …or, if they are curated sets of others' photos | `VZ-GALLERY-001` (`full`) | **M5** |
| Profile **`Message`** | `VZ-MESSAGE-001` (`full`) | **M5** |
| Follow **pending / request** state | `VZ-FOLLOW-002` (`full`) | **M5** |
| Hero slot as an owner-configured homepage (cover, eyebrow, title, paragraph, CTA) | `VZ-BRAND-002` | **M5** |
| Brand mark / logo / palette | `VZ-BRAND-001` | **M5** |
| All five footer links, `Help & Feedback` as a page, the consent notice | `VZ-PAGE-001`, `VZ-CONSENT-001` | **M5** |
| `Powered by Vizra` footer toggle, the Profile's `© 2026` line | `VZ-BRAND-005` | **M5** |
| Language chooser | `VZ-I18N-001` | **M5** |
| `Licensing` footer link and any per-item licence display | `VZ-LICENSE-001` (`full`) | **M5** |
| Discover `Filter` if it maps to the search facet set | `VZ-SEARCH-002` (`full`) | **M5** |
| Album **mosaic cover** treatment (as opposed to a single cover) | `VZ-COLLECTION-001` | **M5** |
| `Hide from search/explore` markers the cards omit | `VZ-PRIVACY-002` (`full`) | **M5** |
| Account-menu **`Insights`** (member statistics) | `VZ-STATS-002` (`full`) | **M6** |
| Any "featured"/"interestingness" curation behind the hero or the Profile `Featured` tab | `VZ-EXPLORE-003` (`full`) | **M6** |
| Per-item view counts over time (if the heart counts are ever joined by view counts) | `VZ-STATS-002` | **M6** |

Neither page can be built as drawn before M5 without either removing the Collections region, the
Message button, the hero CTAs and the whole footer, or shipping them as visibly disabled/absent.

---

## i. Draft API response fields

**DRAFT FOR THE OpenAPI OWNER — not a contract.** Field *names* only, derived strictly from what the
pages render; no semantics, types, nullability, units, pagination style or authorization behaviour
are proposed here. `vizra-core` owns the canonical OpenAPI (`AGENTS.md`). Several entries correspond
to controls with no ledger ID (§g) and **must not be added on the strength of a mockup**. Fields
already drafted in `INVENTORY-search.md` §i are not repeated except where these pages add to them.

### i.1 Home / explore page envelope (Gallery)

```
hero                    ← VZ-BRAND-002 owner homepage slot (M5)
  cover_url, cover_alt, eyebrow, title, body, cta_primary{label,url}, cta_secondary{label,url}
  subject_type          (series? album? collection?) ← "series" has NO LEDGER ID (§g #15)
categories              [{ key, label }]  ← VZ-CATEGORY-001 or VZ-TAG-001; which is undecided
  personalised_scope    ← the "For You" pill, NO LEDGER ID (§g #2)
featured_people         [{ …user item… }] ← NO LEDGER ID as a curated showcase (§g #4)
collections             [{ …collection item… }]
recent                  [{ …photo card item… }]
recent_generated_at     ← the "refreshed hourly" label, NO LEDGER ID (§g #8)
next_cursor | page
editorial               ← NO LEDGER ID (§g #6, #7)
```

### i.2 Photo card item (both pages)

Adds to `INVENTORY-search.md` §i.2; fields unique to these pages are marked.

```
id
url
thumb_url
thumb_srcset
alt_text
title                          (Profile caption; absent on Gallery)
width, height, aspect_ratio    ← required if cropping is to stop (C1); neither page transmits it
placeholder_color              (the var(--line-2) slot)
owner { id, username, handle, display_name, avatar_url, url }
counts { favorites }           ← VZ-FAVORITE-001 public count
counts { views, comments, ratings }   ← absent from both mockups; VZ-STATS-001, VZ-COMMENT-001, VZ-RATING-001
viewer_state { favorited }     ← no control renders it on either page
safety_level                   ← required by VZ-NSFW-001; absent from both
visibility                     ← required by VZ-PRIVACY-001; absent from both
hidden_from_search             ← VZ-PRIVACY-002
is_new                         ← the Profile "New" badge, NO LEDGER ID (§g #24)
layout_hint                    ← the .tall / .wide / .hero-row classes. **A layout hint in the API
                                 would encode C1 into the contract; the correct field is the
                                 intrinsic aspect ratio, and the client chooses the layout**
```

### i.3 Collection / gallery item (Gallery)

```
id
title
url
cover_url, cover_alt
curator { id, username, display_name, url }   ← inert in the mockup; must be a link
item_count                                     ← must be permission-aware
visibility                                     ← absent from the mockup
```

**Note for the contract owner:** whether this object is `VZ-COLLECTION-001` (own albums, hierarchical,
mosaic cover) or `VZ-GALLERY-001` (others' public safe photos, creator opt-out) is undecided (C13).
They have different fields, different permission rules and different `full`-profile scopes.

### i.4 Profile page

```
user {
  id
  username
  handle
  display_name
  avatar_url
  cover_url | background_url        ← ledger says "background"; the mockup says "cover"
  cover_alt
  bio                               ← multi-paragraph; sanitisation policy required
  website_url                       ← must ship with rel/target hardening (C22)
  location                          ← NO LEDGER ID (§g #18)
  joined_at                         ← NO LEDGER ID as a public field (§g #19)
  style                             ← NO LEDGER ID (§g #5, #21)
  verified                          ← NO LEDGER ID (§g #17)
  counts { photos, albums, followers }
  counts { following, favorites }   ← required by VZ-FOLLOW-001 / VZ-FAVORITE-001; absent from the mockup
  derived { most_used_camera, favorite_lens }   ← NO LEDGER ID (§g #20)
  availability { status, note, contact_url }    ← NO LEDGER ID (§g #22)
  viewer_state { following, follow_requested, blocked, blocking }
                                    ← only `following` is drawn, and only as a CSS class
  is_private                        ← VZ-PROFILE-001 "private profiles hide identity"; undrawn
  is_self                           ← no owner view exists on the page
}
tabs      [{ key, label, count }]   ← "featured" has NO LEDGER ID (§g #16)
sort      (recent | oldest | most_viewed | most_favorited | alpha)
featured  [{ id, title, subtitle, item_count, cover_url, url }]   ← the "series" object (§g #15)
photos    [{ …photo card item… }]
albums    [{ id, title, photo_count, updated_at, cover_urls[], visibility, url }]
                                    ← `cover_urls[]` (plural) is the mosaic; VZ-ALBUM-001 specifies
                                       one cover. `visibility` is required by VZ-ALBUM-002 and absent
next_cursor | page                  ← neither the photos grid nor the albums grid has any pagination
```

---

## Appendix — verification notes

Contrast figures in §a.8 were computed from the OKLCH declarations by OKLab → linear sRGB → sRGB
gamma → WCAG relative luminance → `(L1+0.05)/(L2+0.05)`. They are **approximate**: the browser
resolves `oklch()` and `color-mix(in oklab, …)` itself, gamut-maps out-of-range values, and
composites translucent layers over whatever is behind them. Treat these as screening values that
identify which pairs need measurement in the running production build, per `AGENTS.md` ("Do not
fabricate outputs") and `VZ-A11Y-001` ("contrast … over real backings").

Counts in this document — 65 and 42 interactive elements; 31 of 42 and 21 of 24 dead anchors; 35 and
32 inline SVGs; 22 and 24 Unsplash URLs (46 total, all `fit=crop`); 1 and 2 `aria-hidden`
attributes; 3 and 0 `:focus-visible` rules; 21 and 19 declared custom properties; 19 and 15 literal
`white` values; 3 and 4 media queries; 18 and 14 font sizes; 9 and 10 photo cards — were taken by
direct enumeration of the files at the sha256 values recorded above and in
`docs/design/claude-design/README.md`. If either hash changes, re-derive them.

Ledger mappings were taken from `docs/quality/features.json` (schema_version 2, generated
2026-09-15, 191 features), `docs/quality/ui-controls.json` (schema_version 2, 59 controls) and
`docs/MILESTONES.md` (proposed 2026-09-15) as of 2026-09-20. Milestone assignments follow the
`Ledger IDs` column of `docs/MILESTONES.md`; where a ledger entry is `full`-profile only, the
milestone shown is the one that lists it, and the `full`/`core` distinction is noted inline.
