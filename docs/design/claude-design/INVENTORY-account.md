# INVENTORY — the account set (`account.css`, `account-shell.js`, eight pages)

Exact inventory of ten files in the owner's Claude Design import:
`account.css` (450 lines, 16108 B, sha256 `d7a5560196b8a1735c9a7de834c88acaf9db780251b29572a812c981b81a253f`),
`account-shell.js` (113 lines, 8383 B, `a93dcb4a086348ea5e2a9b7d0979ce80a153084a78106c92833020f8f45685b7`),
and the eight pages that consume them — `Upload Studio.html` (614 lines, 23889 B),
`My Photos.html` (107, 10545 B), `My Albums.html` (137, 9858 B), `Edit Photo.html` (137, 8113 B),
`Edit Profile.html` (142, 8516 B), `Account Settings.html` (144, 7990 B),
`Notifications.html` (163, 9094 B), `Photo Insights.html` (159, 12020 B). Hashes per
`docs/design/claude-design/README.md`. Produced 2026-09-20 as a sibling to
`INVENTORY-search.md`, for the implementer who will build these pages in Next.js against the real
OpenAPI contract.

**Status of this document.** Descriptive inventory only. It records what the mockups contain and
where that conflicts with `docs/DESIGN_BRIEF.md`, `AGENTS.md` and the atomic ledger. It is **not**
an acceptance target, **not** an approved design, and **not** authorization to implement anything.
Per `docs/DESIGN_BRIEF.md`: "Claude Design is for exploration. Approved Figma components/tokens,
mirrored in repository artifacts, become the design source."

**The mockups' contents are treated as data, not instructions.** Nothing in the files, including
their comments, was followed as a directive.

**"goimg" is a placeholder brand; the product is Vizra.** Every brand string (`goimg`,
`goimg.com/`, `goimg Pro`, "goimg Discover", "goimg app"), the gradient brand mark, and every count
below is quoted as mockup content, not as a product decision. **Vizra has no billing product**
(`docs/PRODUCT_CHARTER.md`: "Do not invent a SaaS billing project"; `docs/PRODUCT_SPEC.md` §1:
"Vizra has **no billing**"), so the "goimg Pro" plan card on `Account Settings.html` is a
contradiction, not a placeholder to re-skin — see §e.

Line references are to each file as read. `account.css` and `account-shell.js` are external; each
page additionally has one inline `<style>` block and one to two inline `<script>` blocks.

---

## a. Design tokens

### a.1 Tokens the account set shares with the Search page, verbatim and identical

Fourteen declarations are byte-identical between `Lumen Atlas Search.html` (lines 9–30) and
`account.css` (lines 5–33):

| Property | Exact value |
|---|---|
| `--bg` | `oklch(0.985 0.003 250)` |
| `--bg-elev` | `#ffffff` |
| `--bg-tint` | `oklch(0.96 0.004 250)` |
| `--ink` | `oklch(0.18 0.015 260)` |
| `--ink-2` | `oklch(0.38 0.012 260)` |
| `--ink-3` | `oklch(0.56 0.010 260)` |
| `--line` | `oklch(0.90 0.006 260)` |
| `--line-2` | `oklch(0.94 0.005 260)` |
| `--accent` | `oklch(0.58 0.18 255)` |
| `--accent-ink` | `oklch(0.36 0.16 258)` |
| `--accent-soft` | `oklch(0.95 0.04 255)` |
| `--radius-xl` / `-lg` / `-md` / `-sm` | `28px` / `22px` / `16px` / `12px` |
| `--shadow-sm` | `0 1px 2px rgba(17,22,40,.04), 0 1px 1px rgba(17,22,40,.03)` |
| `--shadow-md` | `0 8px 24px -12px rgba(17,22,40,.12), 0 2px 6px rgba(17,22,40,.05)` |
| `--nav-h` | `56px` |

One usage difference worth recording: `--bg-elev` is **dead** in the Search page (literal `white`
is used in 14 places instead) but **live** here — it is the background of `.sidebar` (120),
`.card` (168), `.input/.textarea/.select` (224), `.input-with-prefix` (240),
`.mobile-header-menu select` (395), `.queue` and `.step-rail` and `.preview` (Upload Studio),
`.alb` (My Albums), `.kpi` and `.chart-wrap` (Photo Insights). The account set nevertheless still
hard-codes literal `white` **19 times** (`.btn-secondary` 282, `.btn-icon` 297, `.toggle .thumb`
314, `.segmented button.active` 339, `.tag.success`/`.tag.warn` mixes 352–353, `.btn-primary`
colour 276, `.nav` `color-mix(in oklab, white 76%…)` 64, `.mobile-tabs` `white 80%` 423, plus per-page
`.drop` gradients, `.drop-icon`, `.format-chip`, `.license.selected`, `.publish-bar`, `.alb-new`).

### a.2 Tokens the account set **adds** (not present on the Search page)

| Property | Exact value | Computed sRGB | Used by |
|---|---|---|---|
| `--bg-tint-2` | `oklch(0.94 0.004 250)` | `#e9ebee` | `.queue-item .status.uploading` conic track (Upload Studio 165); `.bar-track` (Photo Insights 35) |
| `--danger` | `oklch(0.58 0.20 25)` | `#d73337` | `.btn-danger` text (289) and border mix (290); `.dot.danger` (360); `.tag.danger` text (354); inline `style="color:var(--danger)"` on both "Danger zone" `<h2>`s (Edit Photo 118, Account Settings 122) |
| `--danger-soft` | `oklch(0.96 0.04 25)` | `#ffe8e4` | `.btn-danger:hover` background (292); `.tag.danger` background (354) |
| `--success` | `oklch(0.66 0.16 150)` | `#33ac5a` | `.toggle input:checked + .track` (319); `.dot.success` (358); `.tag.success` background mix (352); `.step.done .node` and its connector (Upload Studio 51, 67); `.queue-item .status.ready` (162); `.kpi .delta.up` (Photo Insights 14); `.top-stat .d` (32) |
| `--warn` | `oklch(0.76 0.14 80)` | `#dfa635` | `.dot.warn` (359); `.tag.warn` background mix (353); `.queue-item .status.draft` (163) |
| `--radius-xs` | `8px` | — | **declared, never referenced** |
| `--shadow-lg` | `0 30px 60px -25px rgba(17,22,40,.25), 0 10px 24px -15px rgba(17,22,40,.10)` | — | `.mobile-tabs` (428); `.bulk-bar` (My Photos 35) |
| `--sidebar-w` | `248px` | — | `.app` grid column (114); **overridden to `232px` by `Upload Studio.html` line 9** |

### a.3 Token the Search page has that the account set **drops**

`--font-display` (`-apple-system, BlinkMacSystemFont, "SF Pro Display", …`) does not exist here.
`account.css` declares only `--font-sans` (line 30), with the identical SF-Pro-naming problem
recorded as conflict G1 in `INVENTORY-search.md`. All display-weight type (`.page-title` 28px/600,
`.kpi .val` 28px/600, `.drop-title` 18px/600) uses the same stack. **Consequence:** the two mockup
families disagree about whether a display face exists at all.

### a.4 Typography actually used

Base (`account.css` 44–45): `font-size: 15px; line-height: 1.5; letter-spacing: -0.005em;` plus
`-webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility`.

| Role | Selector | Size | Weight | Tracking |
|---|---|---|---|---|
| Page title | `.page-title` (162) | 28px (→ **24px** ≤900px, 412) | 600 | `-0.02em` |
| KPI value | `.kpi .val` (Photo Insights 12) | 28px | 600 | `-0.02em` |
| Drop-zone title | `.drop-title` (Upload Studio 94) | 18px | 600 | `-0.01em` |
| Card title | `.card-title` (178) | 16px | 600 | `-0.01em` |
| Body / brand / mobile select | `body` (44), `.brand-name` (75), `.mobile-header-menu select` (396) | 15px | 400 / 500 / 500 | `-0.005em` / `-0.01em` |
| Album title | `.alb-title` (My Albums 17) | 15px | 600 | `-0.01em` |
| Row title | `.row-title` (199) | **14.5px** | 500 | `-0.005em` |
| Nav search, side link, page-sub, back-btn, matrix label | `.nav-search` (86), `.side-link` (138), `.page-sub` (163), `.back-btn` (377), `.matrix .mlabel` (Notifications 13) | 14px | 400 / 400 / 400 / 500 / 400 | — |
| Top-list stat | `.top-stat` (Photo Insights 31) | 14px | 600 | — |
| Button, row value, callout, license name, top-list title | `.btn` (269), `.row-value` (201), `.callout` (368), `.license-name` (Upload 274), `.top-title` (Photo Insights 29) | **13.5px** | 600 / 400 / 400 / 500 / 500 | `-0.005em` |
| Card sub, prefix, add-link, toolbar search, queue name, tag-input, step name is 14 | `.card-sub` (179), `.prefix` (252), `.add-link` (Edit Profile 22), `.toolbar .search` (My Photos 10), `.queue-item .nm` (Upload 154) | 13px | 400 / 400 / 500 / 400 / 400 | — |
| Segmented button, queue head, step-rail `h3` | `.segmented button` (335), `.queue-head .t` (Upload 131), `.step-rail h3` (Upload 29) | 13px | 500 / 600 / 600 | — |
| Field label, row sub, alb-sub, btn-sm, preview bar, bar-row, map-chip, license desc is 12 | `.field label` (212), `.row-sub` (200), `.alb-sub` (My Albums 18), `.btn-sm` (293), `.preview-bar` (Upload 203), `.bar-row` (Photo Insights 34), `.map-chip` (38) | **12.5px** | 500 / 400 / 400 / 500 / 400 / 400 / 400 | `-0.005em` on the label |
| Help text, aside count, step-sub, license desc, alb-new sub, top-sub, chart legend, kpi delta | `.field .help` (219), `.side-link .aside` (148), `.step-sub` (Upload 58), `.license-desc` (Upload 275), `.top-sub` (Photo Insights 30), `.chart-legend` (19) | 12px | 400 | — |
| Tag / badge | `.tag` (348) | **11.5px** | 500 | — |
| KPI label, queue count | `.kpi .lbl` (Photo Insights 11), `.queue-head .c` (Upload 132) | **11.5px** | 600 / 400 | `.08em` uppercase on the KPI label |
| Eyebrow, avatar initials, char count, format chip, matrix head, step node, queue size | `.eyebrow` (52), `.avatar` (103), `.char-count` (262), `.format-chip` (Upload 101), `.matrix .mhead` (Notifications 10), `.step .node` (Upload 46), `.queue-item .sz` (157) | 11px | 600 / 600 / 400 / 500 / 600 / 600 / 400 | `.14em` / `.06em` uppercase variants |
| Sidebar group title | `.side-section-title` (130) | **10.5px** | 600 | `.12em` uppercase |
| Mobile tab label, photo-card badge/meta | `.mobile-tabs .tab-m` (436), `.pbadge` (My Photos 32) | 10px | 500 / 600 | `.06em` uppercase on `.pbadge` |

Discrete sizes in use: **10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 16, 18, 28 px —
14 values, four of them fractional, on no modular ratio.** Weights 400/500/600/700
(700 only on `.conn-logo`, Account Settings 11). Tracking: `-0.02em`, `-0.01em`, `-0.005em`, `0`,
`.02em`, `.04em`, `.06em`, `.08em`, `.12em`, `.14em`.

### a.5 Spacing, and control heights

Distinct px values used as padding / margin / gap / fixed dimension across `account.css` and the
eight inline stylesheets:

`1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38,
40, 44, 48, 52, 56, 60, 72, 74, 110, 112, 120, 160, 180, 200, 220, 232, 248, 260, 280, 360, 420,
1240`

There is **no 4px or 8px grid**: 5, 7, 9, 11, 14, 18, 22, 26, 34, 38, 52, 74 all appear. Named
rhythm: `.app { padding: 24px 16px 40px; gap: 28px }` → `14px 12px 28px; gap: 14px` ≤900px;
`.page-head { margin-bottom: 22px }`; `.card + .card { margin-top: 18px }`;
`.card-head { padding: 18px 20px 4px }`; `.card-body { padding: 14px 20px 20px }`;
`.row { padding: 14px 20px; min-height: 58px }`; `.form-grid { gap: 18px }`.

Control heights: 26 (`.toggle`), 30 (`.avatar`, `.btn-sm`), 32 (`.alb-more`), 34 (`.conn-logo`,
`.toolbar .search`, and both sort `<select>`s via inline `style="height:34px"`),
36 (`.btn`, `.icon-btn`, `.nav-search`, `.btn-icon`), 40 (`.tag-input` min, `.plan-mark`),
42 (`.btn-lg`), 44 (`.queue-item .thumb`), 48 (`.top-thumb`), 56 (`--nav-h`), 60 (`.mobile-tabs`),
112 (`.avatar-big`).

**`.btn-sm` is 30px tall and `.toggle` is 26px** — both below the 44×44 CSS-px target
`VZ-RESPONSIVE-001` asks for ("touch targets"); `.btn-sm` is the element used for every action in
every `.row` on `Account Settings.html` (13 of them), `Notifications.html` (2) and
`Edit Photo.html` (1).

### a.6 Radii

Tokens: `28px` (**unused**), `22px` (`.sidebar`, `.card`, `.step-rail`, `.queue`, `.preview`,
`.alb`, `.alb-new`, `.kpi`, `.chart-wrap`, `.drop`, `.photo-pane`, `.cover-edit`), `16px`
(**unused as a token**; `.publish-bar` and `.bulk-bar` use a literal `16px`), `12px` (**unused as a
token**; `.license`, `.plan-mark`, `.callout`, `.alb-new .ico`, `.drop-icon` is 18px), `8px`
(`--radius-xs`, **unused**).

Literal radii used instead: `999px` (pills: `.nav-search`, `.icon-btn`, `.btn`, `.tag`,
`.kpi .delta`, `.bar-track`, `.bar-fill`, `.map-chip`, `.pbadge`, `.pill-stat`, `.toggle .track`,
`.mobile-tabs .tab-m`, `.cover-tool`, `.tag-input .t`, `.format-chip`, `.bulk-bar button`),
`50%` (circles), `2px` (`.sw` on the Search page only), `3px` (`.kpi`… none here), `6px`
(`.brand-mark`, `.cb`), `7px` (`.segmented button`), `8px` (`.side-link .ico` none; `.back-btn`,
`.add-link`, `.queue-item .thumb`), `10px` (`.side-link`, `.input`, `.textarea`, `.select`,
`.input-with-prefix`, `.segmented`, `.step`, `.queue-item`, `.queue-add`, `.mobile-header-menu
select`, `.conn-logo`, `.top-thumb`, `.alb-thumbs`), `11px` (none), `12px` (`.license`,
`.callout`, `.plan-mark`), `14px` (`.plan-card`, `.pcard`), `16px` (`.bulk-bar`, `.publish-bar`),
`18px` (`.drop-icon`), `24px` (`.mobile-tabs`).

**Twelve distinct radii against a five-value token set, three of the five tokens unused.**

### a.7 Shadows

Three tokens; **eleven further ad-hoc recipes** inline in rules:

| Selector | Value |
|---|---|
| `.brand-mark` (73) | `inset 0 -1px 2px rgba(255,255,255,.5), 0 1px 2px rgba(17,22,40,.1)` |
| `.avatar` (105) | `inset 0 0 0 1px rgba(255,255,255,.3)` |
| `.input:focus` etc. (234), `.input-with-prefix:focus-within` (245) | `0 0 0 3px color-mix(in oklab, var(--accent) 25%, transparent)` |
| `.btn-primary` (277) | `0 6px 16px -8px oklch(0.58 0.18 255 / .55)` |
| `.toggle .thumb` (316) | `0 2px 6px rgba(17,22,40,.2), 0 0 0 0.5px rgba(17,22,40,.04)` |
| `.toggle input:focus-visible + .track` (321) | `0 0 0 3px color-mix(in oklab, var(--accent) 30%, transparent)` |
| `.segmented button.active` (340) | `0 1px 2px rgba(17,22,40,.06), 0 0 0 0.5px rgba(17,22,40,.04)` |
| `.dot.success` / `.warn` / `.danger` (358–360) | `0 0 0 3px color-mix(in oklab, <token> 18–22%, transparent)` |
| `.drop-icon` (Upload 91) | `0 10px 24px -10px oklch(0.58 0.18 255 / .4), inset 0 0 0 1px color-mix(in oklab, var(--accent) 20%, transparent)` |
| `.license.selected` (Upload 259) | `0 0 0 3px color-mix(in oklab, var(--accent) 15%, transparent)` |
| `.avatar-big` (Edit Profile 15) | `0 0 0 4px white, 0 10px 24px -10px rgba(17,22,40,.35)` |
| `.alb-new .ico` (My Albums 22) | `0 4px 12px -4px oklch(0.58 0.18 255 / .3)` |
| `.queue-item .status.*` | `0 0 0 3px color-mix(…)` halos |

### a.8 Breakpoints — every media query, and what changes

| File:line | Query | Effect |
|---|---|---|
| `account.css` 208 | `max-width: 640px` | `.form-grid.two` collapses to one column |
| `account.css` 405–415 | `max-width: 900px` | `.app` → single column, `gap: 14px`, `padding: 14px 12px 28px`; `.sidebar { display: none }`; `.mobile-header-menu { display: block }`; **`.nav-search { display: none }`**; `.page-head` stacks; `.page-actions` right-aligns; `.page-title` 28→24px; `.card-head`/`.card-body`/`.row` side padding 20→16px |
| `account.css` 442–445 | `min-width: 901px` | `.mobile-tabs { display: none }`; `body { padding-bottom: 0 }` |
| `Edit Photo.html` 17 | `max-width: 900px` | `.edit-grid` → one column; `.photo-pane` loses `sticky` and becomes 16/9 |
| `Photo Insights.html` 23 | `max-width: 900px` | `.grid-two` → one column |
| `Upload Studio.html` 294–306 | `max-width: 960px` | `.studio` → one column; `.step-rail` becomes a horizontal scroller, `.step-sub` hidden, connectors hidden; `.editor` → one column; `.queue` un-sticks; `.license-grid` → one column; `.publish-bar` stacks with `padding-bottom: calc(14px + 74px)` |
| `My Photos.html` 14–16 | `min-width: 600 / 900 / 1100` | `.photos-grid` 2 → 3 → 4 (gap 8→12px) → 5 columns |
| `My Albums.html` 9 | — | `.albums` uses `repeat(auto-fill, minmax(260px, 1fr))`, no media query |
| `Photo Insights.html` 9 | — | `.kpis` uses `repeat(auto-fit, minmax(180px, 1fr))`, no media query |

Breakpoint set: **600, 640, 900, 901, 960, 1100 — six values across three conventions** (the shell
switches at 900/901, Upload Studio at 960, the photo grid at 600/900/1100). The `DESIGN_BRIEF.md`
review viewports are 390px and 1440px; nothing targets 390px, nothing addresses 320px reflow, and
`.app { max-width: 1240px }` means the 1440px viewport is 200px of gutter.

Three fixed widths will overflow a narrow viewport or a 200 % zoom: `.link-row .select { width:
160px }` beside a flexed `.input` and a 36px `.btn-icon` (Edit Profile 20) → the three link rows
need ≈260px minimum and never wrap; `.matrix { grid-template-columns: 1fr 44px 44px 44px }`
(Notifications 9) → the event label column is whatever is left of 390px − 132px − gutters;
`.bar-row { grid-template-columns: 120px 1fr 52px }` (Photo Insights 34).

### a.9 Dark mode

**Absent.** Zero occurrences of `prefers-color-scheme`, `color-scheme`, `[data-theme]` or `.dark`
across `account.css`, `account-shell.js` and all eight pages. Nineteen rules hard-code `white`
(§a.1), four hard-code `color-mix(in oklab, white …%, transparent)` (`.nav` 76 %, `.mobile-tabs`
80 %, `.publish-bar` 90 %, `.tag.success`/`.tag.warn` mixes), `.btn-primary` and
`.segmented button.active` and `.bulk-bar` hard-code `color: white`, and two surfaces hard-code a
near-black (`#0a0c12` on `.preview-body` and `.photo-pane`; `#111` on `.cover-edit`). Two further
rules invert on `--ink`: `.bulk-bar { background: var(--ink); color: white }`. A dark theme
requires re-authoring every one of these, not only the `:root` block.
`DESIGN_BRIEF.md` requires "excellent light/dark modes"; `VZ-DESIGN-001` requires "light/dark".

### a.10 Transitions, animation, reduced motion

No `@keyframes` and no `animation` property anywhere in the set. **No `prefers-reduced-motion`
block anywhere.**

| Selector | Transition |
|---|---|
| `.icon-btn` (96) | `background .15s, color .15s` |
| `.side-link` (139) | `background .12s, color .12s` |
| `.input/.textarea/.select` (229) | `border-color .15s, box-shadow .15s, background .15s` |
| `.input-with-prefix` (241) | `border-color .15s, box-shadow .15s` |
| `.btn` (271) | `transform .12s, background .15s, border-color .15s, color .15s, box-shadow .15s` |
| `.toggle .track` (309) | `background .18s` |
| `.toggle .thumb` (317) | `transform .2s cubic-bezier(.3,.7,.3,1)` |
| `.back-btn` (379) | `background .12s` |
| `.alb` (My Albums 10) | `transform .15s, box-shadow .2s` + `:hover { translateY(-2px) }` |
| `.pcard img` (My Photos 18) | `transform .3s` + `.pcard:hover img { scale(1.04) }` — **zoom on every library thumbnail** |
| `.pcard::after`, `.pcard .check`, `.pmeta` (My Photos 20, 22, 27) | `opacity .15–.2s` |
| `.cb` (Notifications 16) | `background .12s, border-color .12s` |
| `.drop` (Upload 78) | `background .15s, border-color .15s, transform .15s` + `.drag-over { scale(1.005) }` |
| `.queue-item` (Upload 138) | `background .12s` |
| `.license` (Upload 253) | `border-color .12s, background .12s` |

`.btn` declares a `transform` transition but **no rule ever changes its transform** — a dead
declaration. The `.pcard img` scale and the `.drop` scale are the two motions
`VZ-A11Y-001` ("reduced motion") obliges to be gated; neither is.

### a.11 Focus appearance

| Mechanism | Where | Verdict |
|---|---|---|
| `.input:focus`, `.textarea:focus`, `.select:focus` (231–235) | `outline: none` **replaced** by `border-color: var(--accent)` + `box-shadow: 0 0 0 3px color-mix(in oklab, var(--accent) 25%, transparent)` | The ring computes to ≈`#c5def8`, about **1.3:1 against white** — not a perceivable indicator; the accent border is the only real signal, and `--accent` on white is 4.34:1 (§a.12) |
| `.input-with-prefix:focus-within` (243–246) | same | same |
| `.toggle input:focus-visible + .track` (321) | `0 0 0 3px color-mix(in oklab, var(--accent) 30%, transparent)` | The **only** `:focus-visible` rule in the entire account set; ring ≈1.4:1 |
| `button { … }` reset (50) | does **not** touch `outline` | Buttons keep the UA default ring — by omission, not by design |
| `.nav-search input { all: unset }` (88) | removes `outline` | **The shell search field has no focus indicator at all**, and `.nav-search` has no `:focus-within` rule (the Search page's `.nav-search` did) |
| `.input-with-prefix input { all: unset }` (256) | removes `outline` | Rescued by the parent's `:focus-within` |
| `.tag-input input { all: unset }` (Upload 235, Edit Photo 16) | removes `outline` | **No `:focus-within` on `.tag-input`** — the tag entry field has no focus indicator |
| `.toolbar .search input { all: unset }` (My Photos 11) | removes `outline` | **No `:focus-within` on `.toolbar .search`** — the library search field has no focus indicator |
| `.cb` (Notifications 16) | `appearance: none` with no replacement focus style | **21 matrix checkboxes have no visible focus** |
| `* { -webkit-tap-highlight-color: transparent }` (35) | — | Removes the touch activation hint everywhere |

`VZ-A11Y-001` requires "visible focus". Four input surfaces have none, 21 checkboxes have none, and
the three rings that exist are below any usable contrast.

### a.12 Contrast — computed for the tokens this set adds

sRGB and WCAG 2.x ratios computed from the OKLCH declarations (OKLab → linear sRGB → gamma →
relative luminance). The shared tokens are already tabulated in `INVENTORY-search.md` §f.4; the
findings there (`--ink-3` on `--bg` 4.46:1 FAIL, `--accent` text 4.34:1 FAIL, `--line` 1.35:1 FAIL)
apply unchanged here.

| Token | sRGB | Y |
|---|---|---|
| `--bg-tint-2` | `#e9ebee` | 0.8309 |
| `--danger` | `#d73337` | 0.1717 |
| `--danger-soft` | `#ffe8e4` | 0.8468 |
| `--success` | `#33ac5a` | 0.3108 |
| `--warn` | `#dfa635` | 0.4320 |
| `oklch(0.54 0.18 255)` (`.btn-primary:hover`) | `#006cd3` | 0.1543 |
| `oklch(0.44 0.15 150)` (`.tag.success` text) | `#00671d` | 0.0987 |
| `oklch(0.42 0.13 80)` (`.tag.warn` text) | `#714100` | 0.0729 |
| `oklch(0.72 0.12 220)` (chart series 2) | `#2fb5d8` | 0.3883 |

| Pair | Ratio | Verdict |
|---|---|---|
| **white on `--accent`** (`.btn-primary` label, 13.5px/600) | **4.34:1** | **FAIL** 1.4.3 (needs 4.5:1). Passes only on hover (`oklch(0.54…)`, 5.14:1) — the primary button of the whole design system fails at rest and passes under the pointer |
| `--danger` on `--bg-elev` (`.btn-danger` label) | 4.74:1 | pass |
| **`--danger` on `--danger-soft`** (`.btn-danger:hover`) | **4.05:1** | **FAIL** — the destructive button fails *on hover*, the inverse of the primary button |
| `--danger` on `--bg-tint` (`.card-foot` "Sign out of all") | 4.22:1 | **FAIL** |
| **white on `--success`** (`.toggle` on-state track) | **2.91:1** | **FAIL** 1.4.11 (3:1 non-text) |
| `--success` on `--bg-elev` (`.dot.success`, `.kpi .delta.up` text at 12px) | 2.91:1 | **FAIL** for both text and non-text |
| **`--warn` on `--bg-elev`** (`.dot.warn`, `.queue-item .status.draft`) | **2.18:1** | **FAIL** 1.4.11 |
| white on `rgba(211,151,53,.9)` (`.pbadge.draft`, 10px/600 uppercase) | **2.55:1** | **FAIL** |
| `.toggle` off-track `#c6c8ca` vs white | **1.68:1** | **FAIL** 1.4.11 — and the on/off distinction is **colour plus a 18px thumb translation only**, with no text, icon or `aria-*` state |
| `--bg-tint-2` on `--bg-elev` (`.bar-track` unfilled portion) | 1.19:1 | **FAIL** — the empty part of every traffic-source bar is invisible |
| `oklch(0.72 0.12 220)` on white (chart series 2 line + legend swatch) | **2.40:1** | **FAIL** 1.4.11 — the Favorites series and its legend key |
| `--ink-3` on `--bg-tint-2` | 3.90:1 | **FAIL** |
| `--ink-3` on `--bg-elev` (`.row-sub`, `.card-sub`, `.field .help`, `.alb-sub`, `.top-sub`) | 4.65:1 | pass by 0.15 |
| `.tag.success` text on its mixed background `#e0f3e6` | 6.08:1 | pass |
| `.tag.danger` (`--danger` on `--danger-soft`) | 4.05:1 | **FAIL** |
| white on `#0a0c12` (`.preview-body`, `.photo-pane`) | 19.55:1 | pass |
| white on `rgba(31,34,48,.8)` (`.pbadge.private`) | 15.79:1 | pass |
| white on `--ink` (`.bulk-bar`) | 18.81:1 | pass |

Also unmeasurable by construction: `.pmeta` (12px white on a photo behind a
`rgba(0,0,0,.18)→transparent→transparent→rgba(0,0,0,.6)` scrim) and `.cover-tool` (12.5px white on
`rgba(0,0,0,.5)` over a photograph). `VZ-A11Y-001` requires contrast "over real backings".

### a.13 Z-index layers

| Layer | `z-index` | Selector |
|---|---|---|
| Top nav | `100` | `.nav` (57) — the Search page uses 50 |
| Mobile tab bar | `80` | `.mobile-tabs` (430) — the Search page uses 40 |
| Library bulk bar | `20` | `.bulk-bar` (My Photos 35) |
| Upload publish bar | `10` | `.publish-bar` (Upload 289) |
| Photo-card check / meta / badge | `2` | `.pcard .check`, `.pmeta`, `.pbadge` (My Photos 22, 27, 32) |
| Avatar row over cover | `2` | `.avatar-row` (Edit Profile 14) |
| Step node over connector | `1` | `.step .node` (Upload 49) |

**Defect.** `.mobile-tabs` is `position: fixed; bottom: 12px; height: 60px; z-index: 80`, and
`.bulk-bar` is `position: sticky; bottom: 12px; z-index: 20`. Below 901px the two occupy the same
12px offset, so **the entire library bulk-action bar (Move to album / Set visibility / Download /
Delete) renders behind the floating tab bar on every phone viewport.** Upload Studio compensates
for exactly this with `.publish-bar { padding-bottom: calc(14px + 74px) }` ≤960px; My Photos has no
such rule. `VZ-RESPONSIVE-001` requires "mobile viewer actions" to be reachable.

**Improvement over the Search page, recorded for completeness:** `body` here uses
`padding-bottom: calc(72px + env(safe-area-inset-bottom, 0))` and resets it to `0` at ≥901px
(444), fixing the 72px of dead desktop space recorded as defect G21 in `INVENTORY-search.md`.

---

## b. The account shell

Every page except `Upload Studio.html` contains four empty slot divs — `#nav-slot`,
`#sidebar-slot`, `#mobile-header-slot`, `#mobile-tabs-slot` — which `account-shell.js` replaces via
`outerHTML`. `Upload Studio.html` omits `#sidebar-slot` (it has its own step rail).

### b.1 Top nav — injected `<header class="nav">` (`account-shell.js` 28–47)

`position: sticky; top: 0; height: 56px; z-index: 100; display: grid;
grid-template-columns: auto 1fr auto; gap: 14px; padding: 0 16px`, background
`color-mix(in oklab, white 76%, transparent)` + `backdrop-filter: saturate(180%) blur(22px)`,
bottom border `1px solid color-mix(in oklab, var(--line) 70%, transparent)`.

| # | Control | Element | Visible content | Evident intent |
|---|---|---|---|---|
| 1 | Brand | `<a class="brand" href="Lumen Atlas Gallery.html">` (30) | `<span class="brand-mark" aria-hidden="true">` (22×22, radius 6px, `linear-gradient(135deg, oklch(0.78 0.09 50), oklch(0.55 0.18 260))`) + `<b>go</b><span>img</span>` | Return to the public gallery |
| 2 | Search field | `<label class="nav-search" aria-label="Search">` (34) wrapping a Search SVG + `<input placeholder="Search your library…">` | placeholder only | Search **the member's own library**. **No `type`, no `name`, no `id`, no `<form>`, no submit control, no handler, no clear button, no `:focus-within` style.** Hidden entirely below 900px |
| 3 | Notifications | `<button class="icon-btn" aria-label="Notifications">` (39) | Bell icon only | Open a notifications panel. **No badge, no unread count, no handler** |
| 4 | Upload | `<a class="icon-btn" href="Upload Studio.html" aria-label="Upload">` (42) | Upload icon only | Go to the uploader. **An `<a>` here; the Search page's identical control is a `<button>`** — the two mockup families disagree on the element for the same action |
| 5 | Account | `<span class="avatar">MK</span>` (45) | Initials `MK`, 30×30 gradient circle | Account menu. **A `<span>` with no `aria-label`, no `role`, no `tabindex` — not focusable, not activatable, and worse than the Search page's version, which at least carried `aria-label="Your profile"`** |

Not present: sign-in/sign-out, theme toggle, language chooser, admin entry, skip link, breadcrumb.

### b.2 Sidebar — injected `<aside class="sidebar" aria-label="Account sections">` (62–74)

`position: sticky; top: calc(56px + 16px)` = 72px; `background: var(--bg-elev)`;
`border: 1px solid var(--line)`; `border-radius: 22px`; `padding: 8px`; `box-shadow: var(--shadow-sm)`;
`max-height: calc(100vh - 88px)`; `overflow: auto`. `display: none` below 900px.

Structure is a flat sequence of `<div class="side-section"><div class="side-section-title">` group
labels interleaved with sibling `<a class="side-link">` elements — **no list, no `<nav>`, no
`<fieldset>`/`role="group"`, no `aria-labelledby`, and the group title is a `<div>`, not a heading.**

| # | Group | Label | `href` | Trailing count | Active rule |
|---|---|---|---|---|---|
| 6 | Library | `My Photos` | `My Photos.html` | `312` | `.active` when `__page.key === 'photos'` |
| 7 | Library | `Albums` | `My Albums.html` | `24` | `'albums'` |
| 8 | Library | `Upload` | `Upload Studio.html` | — | `'upload'` |
| 9 | Library | `Insights` | `Photo Insights.html` | — | `'insights'` |
| 10 | Account | `Edit Profile` | `Edit Profile.html` | — | `'edit-profile'` |
| 11 | Account | `Account` | `Account Settings.html` | — | `'account'` |
| 12 | Account | `Notifications & Privacy` | `Notifications.html` | — | `'notifications'` |
| 13 | Help | `Help & Support` | `#` | — | never active — **dead link** |
| 14 | Help | `Back to gallery` | `Lumen Atlas Gallery.html` | — | never active |

`.side-link.active` = `background: color-mix(in oklab, var(--accent) 12%, transparent);
color: var(--accent-ink); font-weight: 600`, and `.ico` turns `--accent`. **No `aria-current="page"`.**
The `312` and `24` counts are hard-coded string literals in the script (lines 9, 11).

`Edit Photo.html` sets `window.__page = { key: 'photos' }`, so the sidebar highlights "My Photos"
while the user is on the edit screen — deliberate, but there is no breadcrumb other than the
`.back-btn`.

### b.3 Mobile section select — injected (78–83)

```
<div class="mobile-header-menu">
  <select onchange="if(this.value) location.href=this.value"> … 7 <option> … </select>
</div>
```

`display: none` above 900px. One `<option>` per sidebar item in `Library` + `Account` order
(Help entries are excluded), with `selected` on the current page. Styled with
`appearance: none` and an inline `data:image/svg+xml` chevron background.

Defects: **no `<label>`, no `aria-label`, no accessible name at all**; an inline `onchange`
attribute; and navigation occurs on **change**, which is a WCAG 2.2 3.2.2 (On Input) hazard —
a keyboard user arrowing through the list navigates away on the first key press.

### b.4 Mobile tab bar — injected `<nav class="mobile-tabs" aria-label="Mobile navigation">` (85–102)

`position: fixed; left: 12px; right: 12px; bottom: calc(12px + env(safe-area-inset-bottom, 0));
height: 60px; border-radius: 24px; z-index: 80`, background `color-mix(in oklab, white 80%,
transparent)` + `saturate(180%) blur(28px)`, `box-shadow: var(--shadow-lg)`. Hidden ≥901px.
A floating pill — structurally different from the Search page's edge-to-edge bar.

| # | Tab | Element | Visible label | `aria-label` | Active when |
|---|---|---|---|---|---|
| 15 | Home | `<a href="Lumen Atlas Gallery.html">` | `Home` | `Home` | never |
| 16 | Library | `<a href="My Photos.html">` | `Library` | `Library` | `key === 'photos'` |
| 17 | Upload | `<a href="Upload Studio.html">` | `Upload` | `Upload` | `key === 'upload'` |
| 18 | Insights | `<a href="Photo Insights.html">` | `Insights` | `Insights` | `key === 'insights'` |
| 19 | You | `<a href="Edit Profile.html">` | `You` | **`Profile`** | `key ∈ {edit-profile, account, notifications}` |

All five are real links (an improvement over the Search page's dead `<button>` tabs). But: the
active state is `color: var(--accent)` **only** — no `aria-current`, no weight or shape change,
and `--accent` on the blurred white pill is ~4.3:1; and tab 19's visible text "You" disagrees with
its accessible name "Profile" — the same WCAG 2.5.3 *Label in Name* failure recorded on the Search
page. The sidebar's **Albums** and **Account Settings** sections have no tab; on a phone they are
reachable only through the `<select>` in `#mobile-header-slot`.

**Desktop navigation hole.** `Upload Studio.html` has no `#sidebar-slot`, and
`.mobile-header-menu` is `display: none` above 900px. The injected nav has no links. Therefore
**on a desktop viewport, Upload Studio offers no way to reach any other account page** except the
brand link to the public gallery and the nav's Upload icon (which points at itself). The step
rail's only escape is `<a href="#">Save draft & exit`, a dead link.

### b.5 What `account-shell.js` does — and its defects

113 lines, one IIFE, no data, no fetch, no state. It reads `window.__page` (set by an inline
`<script>` immediately before it on every page), builds four HTML strings, and replaces each slot
with `outerHTML` if the element exists (105–112). Nothing else happens: no handler is bound, no
count is computed, no current-page ARIA is applied.

- Every icon is a hand-inlined `<svg>` string in JS (17 of them) — three of the shell's icons
  (`My Photos`/`Library` camera, `Upload` arrow, `Insights` chart) are duplicated between the
  sidebar array and the tab bar with **different `stroke-width` values** (1.7 vs 1.9/2).
- `outerHTML` assignment re-parses the whole document fragment; because the script tag sits at the
  end of `<body>`, this is safe here, but it means the shell cannot be progressively enhanced and
  is invisible to any SSR/SEO path.
- The sidebar counts (`312`, `24`) and the avatar initials (`MK`) are literals.
- The mobile `<select>` carries an inline event-handler attribute, which a Content-Security-Policy
  without `unsafe-inline` would block.

### b.6 Shared components defined in `account.css`

`.card` / `.card-head` / `.card-title` / `.card-sub` / `.card-body` / `.card-foot`;
`.row-list` / `.row` / `.row-main` / `.row-title` / `.row-sub` / `.row-value` / `.row-chev`;
`.form-grid` (+`.two`) / `.field` / `.input` / `.textarea` / `.select` / `.input-with-prefix`
(+`.prefix`) / `.char-count`; `.btn` with variants `-primary` `-secondary` `-ghost` `-danger`
`-sm` `-lg` `-icon`; `.toggle`; `.segmented`; `.tag` with `.accent` `.success` `.warn` `.danger`;
`.dot` with `.success` `.warn` `.danger`; `.callout`; `.back-btn`; `.eyebrow`; `.muted`;
`.stack-sm` `.stack-md` `.hr-soft`.

**Declared and never used by any of the eight pages:** `.eyebrow`, `.muted`, `.callout`,
`.row-chev`, `.stack-sm`, `.stack-md`, `--radius-xs`. `.hr-soft` is used once (Upload Studio 339).

**Used by a page and never defined anywhere:** `.view-toggle` and `.view-btn`
(`My Photos.html` 64–66) — the grid/rows switcher has **no CSS rule in `account.css` or in the
page's own `<style>`**, so it renders as two unstyled `<button>`s with bare 24px SVGs and no
grouping, border, active fill or hit area; and `.link-inline` (`Photo Insights.html` 125), which
renders as plain inherited text with no link affordance at all. `.chip` on `My Photos.html` 89 is
only meaningful because the element also carries `.tag`.

### b.7 Footer

**There is no footer on any of the eight pages.** No legal links, no instance branding, no Lucide
attribution — which `DESIGN_BRIEF.md` requires be preserved.

---

## c. The pages

### C1. `Upload Studio.html` — the uploader

**Purpose.** Three-step upload flow: select files → add per-photo details → review and publish.
Maps to `/upload`.

**Layout regions.** `<main class="studio">` — a 232px `.step-rail` + `minmax(0,1fr)` `.studio-main`
grid, `max-width: 1240px`, collapsing to one column ≤960px. Inside `.studio-main`:
`#mobile-header-slot` → `.drop` zone → `.editor` (280px `.queue` + `.editor-main`) →
inside `.editor-main`: `.preview`, three `.card`s (Photo details, License, Audience & comments),
and a sticky `.publish-bar`. **No `<h1>` anywhere on this page** — the highest heading is
`<h3>Upload</h3>` in the step rail (317), followed by three `<h2>` card titles.

**Controls.**

| # | Visible label | Element | Evident intent |
|---|---|---|---|
| 21 | `Select files` / `Add details` / `Review & publish` + subs `3 photos added` / `Title, tags, license` / `Choose audience` | three `<div class="step">` (318–338), classes `done` / `active` / — | Progress indicator. **Inert divs — not links, not buttons, no `aria-current`, no `role="list"`** |
| 22 | `Save draft & exit` | `<a class="side-link" href="#">` (340) with inline colour/size overrides | Leave the flow keeping a draft. **Dead link** |
| 23 | (drop target) | `<div class="drop" id="drop">` (351) | Drop files. Handlers on `dragenter/dragover/dragleave/drop` call `preventDefault()` and toggle `.drag-over` **and nothing else** — no `DataTransfer` read, no file list, no upload |
| 24 | `choose from your library` | `<b>` inside `.drop-sub` (356), styled `color: var(--accent); cursor: pointer` | Open a file picker. **A `<b>` element: not a button, not focusable, no handler, and there is no `<input type="file">` anywhere in the file** |
| 25 | `JPG` `PNG` `HEIC` `RAW` `TIFF` `WebP` | six `<span class="format-chip">` (358–363) | Advertise accepted formats. Inert |
| 26 | `up to 50 files, 100 MB each` | text in `.drop-sub` | Advertise limits |
| 27 | queue rows ×3 | `<div class="queue-item">` (374, 382, 390) | Select the photo being edited. `div` with a click handler that toggles `.active` |
| 28 | `12.4 MB · Editing` / `11.1 MB · Ready` / `4.9 MB · Uploading 65%` + status dot | `.sz` text + `<span class="status draft|ready|uploading" title="…">` | Per-file state. The `uploading` dot is a `conic-gradient(var(--accent) 65%, var(--bg-tint-2) 0)` — a **hard-coded** 65 % arc. `title` is the only accessible text and there is no `role="progressbar"`, `aria-valuenow` or `aria-live` |
| 29 | `Add more` | `<button class="queue-add">` (398) | Add files to the queue. No handler, no file input |
| 30 | `Fujifilm X-T5 · 23mm f/2.8` / `ISO 400 · 1/250s` / `6240 × 4160` / `DSCF8821.RAF` | `.preview-bar .exif` (411–416) | Display EXIF. Read-only text |
| 31 | `Title` | `<input class="input" id="title">` with `<label for="title">` (429–430) | Photo title. **One of only two correctly associated labels in the entire account set** |
| 32 | `45 / 80` | `.char-count` (431) | Character counter. **Static and wrong** — the value is 35 characters |
| 33 | `Description` | `<textarea class="textarea" id="desc">` with `<label for="desc">` | Photo description |
| 34 | `160 / 500` | `.char-count` (436) | **Static and wrong** — the value is 152 characters |
| 35 | `Album` | `<select class="select">` (442) — `Concrete Sundays`, `Working Edits`, `North Light`, `— New album…` | Choose or create an album. The label has no `for`; "— New album…" is an option that implies a dialog that is not drawn |
| 36 | `Location` | `.input-with-prefix` + map-pin prefix + `<input value="Mexico City, Mexico">` (451–456) | Free-text place name |
| 37 | tag remove ×4 | `<button aria-label="Remove tag">` inside `.tag-input .t` (464, 467, 470, 473) | Remove `brutalism` / `architecture` / `concrete` / `mexico` |
| 38 | `Add a tag…` | `<input placeholder="Add a tag…">` inside `.tag-input` (475) | Add a tag. No handler; no autocomplete; help text says "Try 5–10 specific words" |
| 39 | `All rights reserved` / `CC BY 4.0` / `CC BY-NC` / `Public domain (CC0)` | four `<label class="license">` (491–518), each containing `<span class="radio">` and two `<div>`s | Choose a licence. **There is no `<input type="radio">` — these are `<label>` elements with no form control: not focusable, not keyboard-operable, no radiogroup, no name, no value.** Selection is a JS class toggle |
| 40 | `Public` / `Followers` / `Private` | `<div class="segmented" role="tablist">` with three `<button>` (534–538) | Set visibility. `role="tablist"` with **no `role="tab"` children, no `aria-selected`, no tabpanel** |
| 41 | `Allow comments` (`Everyone can reply; spam filter is on by default.`) | `.toggle` (545) | Comment permission |
| 42 | `Show EXIF` (`Camera, lens, ISO, shutter, location.`) | `.toggle` (552) | EXIF visibility |
| 43 | `Safe for all audiences` (`Uncheck if the photo contains nudity, violence, or graphic content.`) | `.toggle` (559) | Content safety — **binary** |
| 44 | `2 of 3 ready · 1 still uploading` + green dot | `.publish-status` (566) | Batch state. Static |
| 45 | `Save as draft` | `<button class="btn btn-ghost">` (571) | Keep unpublished |
| 46 | `Schedule` | `<button class="btn btn-secondary">` (572) | Publish later |
| 47 | `Publish all` + arrow | `<button class="btn btn-primary btn-lg">` (573) | Finalize the batch |

**Form fields.** Title (text, no `maxlength` despite "/ 80"), Description (textarea, no
`maxlength` despite "/ 500"), Album (`<select>`, 4 options), Location (text, no geocoder, no
`type`), Tags (text, free entry), Licence (4 fake radios), Visibility (3 segmented buttons), three
checkboxes. **No field has `required`, `pattern`, `aria-describedby`, `aria-invalid` or any
validation hint; there is no `<form>`; there is no error slot.**

**States present.** Step `done` / `active` / pending; queue `active`; per-file `ready` / `draft` /
`uploading` (a static 65 % arc); drop-zone `drag-over`; licence `selected`; segmented `active`;
toggle checked; `.btn-primary[disabled] { opacity: .55; cursor: not-allowed }` is **defined but
never applied**.

**States the brief requires and the mockup lacks.** Real upload progress with a live percentage
and `aria-live`; per-file **cancel** and **retry**; upload **error** (network drop, rejected
format, oversized file, decoder failure, quota exceeded) — `prompt 03` explicitly requires
"Surface processing failure instead of leaving an endless spinner"; post-finalize **processing /
queued** state; **duplicate-detected** state; empty queue; disabled Publish while files are
in flight; success/result panel with links and delete link; unauthorized/session-expired;
moderation-pending; loading skeleton; destructive confirmation on removing a queued file
(no remove control exists at all).

**Responsive.** ≤960px the rail becomes a horizontal scroll strip (`overflow-x: auto`, no keyboard
scroll affordance, `.step-sub` hidden), the editor stacks, the licence grid becomes one column, and
`.publish-bar` stacks with 74px of bottom padding to clear the tab bar. At 390px the licence cards,
the preview 16/9 box and the `.preview-bar` EXIF flex row (three spans, `gap: 14px`, no wrap) are
the tightest points; the EXIF row will overflow.

**Inline script (588–612).** Four handlers, ~24 lines: licence click → clear `.selected` on all,
set it on the clicked label; `.segmented button` click → clear `.active`, set it; `.queue-item`
click → clear `.active`, set it; drop-zone drag events → toggle `.drag-over`. Nothing else is
wired: `.queue-add`, all four tag removes, the tag input, every text field, `Save as draft`,
`Schedule`, `Publish all`, `Save draft & exit`, and the `choose from your library` text.

**Mock data shape.** None — no object, no array, no template. Three queue entries
(`DSCF8821.RAF` 12.4 MB, `DSCF8834.RAF` 11.1 MB, `DSCF8902.RAF` 4.9 MB; header `3 files · 28.4 MB`,
which does not sum: 12.4+11.1+4.9 = 28.4 ✓) and one hydrated form are hand-written HTML. Four
hotlinked `images.unsplash.com` URLs (three queue thumbnails, one preview).

**Accessibility.** No `<h1>`; heading order is `h3` then `h2`. Ten inline `<svg>`, **none with
`aria-hidden`**. Six `aria-` attributes total, all on the two `<aside>`s and the four tag-remove
buttons. Four fake radios with no form control. A drag-and-drop zone with **no keyboard and no
file-picker path** — `prompt 03` states in terms: "A drag-and-drop upload is not sufficient without
a usable keyboard/file-picker alternative". `div`-as-button on three queue rows. `role="tablist"`
with no tabs. `title` as the only accessible text on three status dots. The progress arc is
colour-and-shape only. `alt=""` on three of four images.

---

### C2. `My Photos.html` — the personal library

**Purpose.** The member's own photos, all visibilities, with selection and bulk actions.
Maps to `/library`.

**Layout regions.** `.app` grid (sidebar + main) → `.page-head` (title, sub, two actions) →
`.toolbar` (search, segmented filter, spacer, sort `<select>`, view toggle) → `.photos-grid`
(2 → 3 → 4 → 5 columns) → sticky `.bulk-bar`.

**Controls.**

| # | Visible label | Element | Evident intent |
|---|---|---|---|
| 48 | `Insights` | `<a class="btn btn-secondary" href="Photo Insights.html">` (54) | Open member stats |
| 49 | `Upload` | `<a class="btn btn-primary" href="Upload Studio.html">` (55) | Open the uploader |
| 50 | `Search your photos…` | `<input>` in `.toolbar .search` (60) | Filter the library. No `type`, no `name`, no label, no `:focus-within` style, no handler |
| 51 | `All 312` / `Published 280` / `Drafts 22` / `Private 10` | `.segmented` ×4 `<button>` (61) | Filter by publication state. No `role`, no `aria-pressed` |
| 52 | `Newest` / `Oldest` / `Most favorited` / `Most viewed` | `<select class="select" style="width:150px;height:34px">` (63) | Sort. **No label, no accessible name** |
| 53 | Grid | `<button class="view-btn active" aria-label="Grid">` (65) | Dense grid. **Unstyled — no CSS rule exists** |
| 54 | Rows | `<button class="view-btn" aria-label="Rows">` (66) | List view. **Unstyled** |
| 55 | photo card ×15 | `<a class="pcard" href="Edit Photo.html">` (71–85) | Open the photo. **Every card links to the edit screen, not to a viewer** |
| 56 | selection check ×15 | `<span class="check">` inside each card (22–25) | Select for bulk action. **A `<span>` with a click handler, nested inside an `<a>`**: not focusable, not keyboard-operable, no `role`, no `aria-checked`, no label. Visible only on `:hover` unless `.selected` |
| 57 | `2.1k` + heart `820` | `.pmeta` on card 1 only (71) | Views and favourites. **`opacity: 0` until `:hover` — invisible and unreachable on touch** |
| 58 | `Draft` (cards 3, 13) / `Private` (card 7) | `.pbadge` | State marker. Always visible |
| 59 | `3 selected` | `<span class="chip tag">` (89) | Selection count. Updated by script |
| 60 | `Move to album…` | `<button>` (91) | Bulk add to album |
| 61 | `Set visibility` | `<button>` (92) | Bulk privacy change |
| 62 | `Download` | `<button>` (93) | Bulk download |
| 63 | `Delete` | `<button class="btn-danger">` (94) | Bulk delete. **No confirmation drawn** |

**Data per card.** Image URL (hotlinked Unsplash, `&fit=crop&w=600`), `alt=""` on all 15, an
optional badge (`Draft` / `Private`), and on card 1 only a view count and a favourite count. No
title, no date, no album, no visibility marker on the 12 unbadged cards, no safety-level state, no
processing state.

**Page-level data.** `312 photos · 8.2 GB · last uploaded 3 days ago` (51). The `8.2 GB` is a quota
consumption figure with no ceiling, no percentage and no warning state.

**States present.** `.pcard:hover` (image scale 1.04, scrim, check and meta fade in);
`.pcard.selected` (3px inset accent outline, check filled, scrim on); `.segmented button.active`;
`.view-btn.active` (class only — no style exists); bulk bar shown/hidden by script.

**States the brief requires and the mockup lacks.** Loading skeleton for the grid; **empty library**
(the zero-photo first-run state a new owner sees immediately after the golden-path install);
zero-results for the search/filter; error (listing failed); per-card processing/failed-derivative
state; destructive **confirmation** for bulk Delete; disabled bulk actions when nothing is selected
(the bar is rendered visible in the markup with three cards pre-selected); pagination/infinite
scroll (none: exactly 15 cards, no pager, no "load more", against a claimed 312); optimistic
selection failure; unauthorized.

**Responsive.** Grid 2/3/4/5 columns at 0/600/900/1100px. Below 900px the sidebar disappears,
the nav search disappears, and the `.toolbar` wraps. Two problems: the bulk bar is occluded by the
floating tab bar (§a.13); and the card hover layer — which carries the only per-photo metadata —
has no touch equivalent, so on a phone every card is an untitled square.

**Inline script (101–105).** Three one-liners: segmented `.active` toggle (with
`ev.preventDefault()`); view-btn `.active` toggle; `.check` click → `preventDefault` +
`stopPropagation`, toggle `.selected` on the parent, recount `.pcard.selected`, write
`n + ' selected'` into `.bulk-bar .chip`, and set `#bulkBar.style.display = n ? 'flex' : 'none'`.
Nothing else is wired: the search input, the sort select, all 15 card links (they navigate), the
four bulk buttons, and both page actions.

**Mock data shape.** None. Fifteen hand-written `<a class="pcard">` with hotlinked URLs.

**Accessibility.** Zero `<h2>`; one `<h1>`. Five inline `<svg>`, none `aria-hidden`. Two `aria-`
attributes in total, both `aria-label` on the unstyled view buttons. `<span>`-as-checkbox nested
inside a link on all 15 cards. Unlabelled search input and sort select. Hover-only metadata.
`alt=""` on all 15 photographs, so a screen reader hears fifteen identical "link" entries whose
only accessible content is the occasional badge text.

---

### C3. `My Albums.html` — the album index

**Purpose.** Grid of the member's albums with a create affordance. Maps to `/albums`.

**Layout regions.** `.app` grid → `.page-head` (title, sub, `New album`) → an inline flex filter row
(segmented + spacer + sort `<select>`) → `.albums` grid (`auto-fill, minmax(260px, 1fr)`) whose
first cell is the create tile.

**Controls.**

| # | Visible label | Element | Evident intent |
|---|---|---|---|
| 64 | `New album` | `<button class="btn btn-primary">` (41) | Create an album |
| 65 | `New album` + `Group photos by series, location, or theme.` | `<button class="alb-new">` (52) | Create an album — **a second, differently-styled path to the same action** |
| 66 | `All 24` / `Public` / `Unlisted` / `Private` | `.segmented` ×4 `<button>` (46) | Filter by album privacy |
| 67 | `Recently updated` / `A — Z` / `Most photos` | `<select style="width:160px;height:34px">` (48) | Sort. **No label** |
| 68 | album cover mosaic ×5 | `<a class="alb-thumbs" href="#">` (58, 72, 86, 100, 114) | Open the album. **All five are dead `href="#"`** |
| 69 | `Concrete Sundays` / `North Light` / `Working Edits` / `Mexico Modern` / `Portraits, 2025` + `N photos · Updated … · <visibility>` | `<div class="alb-title">` and `<div class="alb-sub">` | Identify the album. **The title is not a link** — only the image mosaic is clickable |
| 70 | `Public` (×3) / `Private` / `Unlisted` + globe / lock / eye icon | `<span class="alb-visibility">` | Show album privacy. Inert |
| 71 | ⋯ ×5 | `<button class="alb-more">` (68, 82, 96, 110, 124) | Album menu. **No `aria-label`, no `aria-haspopup`, no handler, and no menu is drawn anywhere** |

**Data per album card.** Three cover thumbnails in a `2fr 1fr / 1fr 1fr` mosaic (first image spans
both rows), all `object-fit: cover` (destructive crop) with `alt=""`; title; photo count; relative
update time; privacy label. No cover-selection control, no description, no owner, no sub-album
indicator, no share state.

**States present.** `.alb:hover` (translateY −2px + `--shadow-md`); `.segmented button.active`.

**States the brief requires and the mockup lacks.** **Empty state** — zero albums (the create tile
is always present, so the page can never be truly empty, but there is no first-run explanation);
loading skeleton; error; album with fewer than three photos (the mosaic assumes exactly three —
`.alb-thumbs img:first-child { grid-row: 1/3 }` plus two more; an album with one photo or none
leaves broken cells); the `password` privacy mode (present in `VZ-ALBUM-002`, absent here);
sub-album nesting (`VZ-ALBUM-001` requires nested sub-albums — this is a flat grid with no depth
affordance); destructive confirmation for album deletion; rename/inline edit; drag reorder;
disabled create when a quota is exhausted.

**Responsive.** `auto-fill, minmax(260px, 1fr)` means one column below ~292px of content width and
the cards never go narrower than 260px — at 390px with 12px `.app` padding this just fits. The
filter row is a raw inline `style="display:flex;…flex-wrap:wrap"`, not a shared component.

**Inline script (133–135).** One line: segmented `.active` toggle. Nothing else is wired — neither
create path, neither album link, the sort select, nor any of the five ⋯ buttons.

**Mock data shape.** None. Five hand-written `<article class="alb">` with 15 hotlinked URLs.

**Accessibility.** Zero `<h2>` (the album titles are `<div>`s, so the page has one `<h1>` and no
structure below it). Twelve inline `<svg>`, none `aria-hidden`. **Zero `aria-` attributes on the
page.** Five unlabelled icon-only `<button>`s. Five dead `href="#"`. Titles that look like links
and are not. `alt=""` on all 15 covers.

---

### C4. `Edit Photo.html` — single-photo metadata editor

**Purpose.** Edit one photo's details, audience and metadata; delete it. Maps to
`/photos/{id}/edit`.

**Layout regions.** `.app` grid → `.back-btn` → `.page-head` (title, sub, Cancel + Save) →
`.edit-grid` (`1.1fr` sticky dark `.photo-pane` + `1fr` column of four `.card`s: Details, Audience,
EXIF, Danger zone).

**Controls.**

| # | Visible label | Element | Evident intent |
|---|---|---|---|
| 72 | `My Photos` + chevron | `<a class="back-btn" href="My Photos.html">` (26) | Return to the library |
| 73 | `Cancel` | `<button class="btn btn-ghost">` (33) | Discard changes |
| 74 | `Save changes` | `<button class="btn btn-primary">` (34) | Persist changes |
| 75 | `Title` | `<input class="input" value="Brutalist facade, Turin">` (48) | Title. Label has no `for` |
| 76 | `Description` | `<textarea class="textarea">` (52) | Description. No char count here (unlike Upload Studio) |
| 77 | `Album` | `<select>` — `North Light`, `Concrete Sundays`, `Working Edits` (57) | Album membership — **single-select** |
| 78 | `License` | `<select>` — `All rights reserved`, `CC BY 4.0`, `CC BY-NC`, `CC0 Public Domain` (61) | Licence. A `<select>` here; four card-radios in Upload Studio — **two different controls for the same field, with differently worded options** |
| 79 | `Location` | `.input-with-prefix` + `<input value="Turin, Italy">` (66–69) | Place name |
| 80 | tag remove ×3 | `<button>` inside `.tag-input .t` (74–76) | Remove `brutalism` / `italy` / `architecture`. **No `aria-label` here** (Upload Studio's equivalents have one) |
| 81 | `Add a tag…` | `<input>` (77) | Add a tag |
| 82 | `Public` / `Followers` / `Private` | `.segmented` (89) | Visibility. **No `role` here** (Upload Studio's has `role="tablist"`) |
| 83 | `Allow comments` | `.toggle` (93) | Comment permission |
| 84 | `Show EXIF data` | `.toggle` (97) | EXIF visibility |
| 85 | `Allow downloads` | `.toggle`, unchecked (101) | Download permission — **binary** |
| 86 | `Camera` `Leica Q3` / `Lens` `28mm f/1.7` / `Exposure` `1/500s · f/5.6 · ISO 200` / `Captured` `Mar 2, 2026 · 16:42` / `Dimensions` `6000 × 4000` | five `.row` with `.row-value` (109–113) | Read-only EXIF |
| 87 | `Delete` (`Permanently removes this photo and all stats.`) | `<button class="btn btn-danger btn-sm">` (122) | Delete the photo. **No confirmation dialog drawn** |

**Internal contradiction.** The page subtitle reads "Update details and metadata. **Changes apply
instantly.**" while the header carries explicit `Cancel` and `Save changes` buttons. The two models
are mutually exclusive; the implementer must pick one and the design does not say which.

**States present.** `.segmented button.active`; toggle checked/unchecked; `.btn-danger:hover`.

**States the brief requires and the mockup lacks.** Dirty/unsaved indicator; saving (in-flight),
saved (success), save-failed with recoverable retry; per-field validation error; disabled Save when
unchanged; **destructive confirmation** for Delete (`DESIGN_BRIEF.md` and `prompt 02` both name
"destructive-confirmation" explicitly); loading state for the photo itself; a broken/failed
derivative state; unauthorized (someone else's photo); not-found; concurrent-edit conflict; the
`unlisted` visibility option.

**Responsive.** ≤900px the two columns stack and `.photo-pane` un-sticks and becomes 16/9
(from 4/3). The EXIF `.row-value` right-aligned column and `.row-title` can collide at 390px —
`Exposure` + `1/500s · f/5.6 · ISO 200` is 29 characters of value against a `flex: 1` label with
`gap: 14px` and 16px side padding.

**Inline script (133–135).** One line: segmented `.active` toggle. Cancel, Save, Delete, both
selects, all text fields, all three tag removes, the tag input and all three toggles are unwired.

**Mock data shape.** None. One hotlinked image (`alt=""`).

**Accessibility.** One `<h1>`, four `<h2>`. Five inline `<svg>`, none `aria-hidden`. **Zero
`aria-` attributes on the page** — including the three unlabelled tag-remove buttons. Nine
`<label>` elements, **none with `for`**, none wrapping their control except the three empty
`.toggle` wrappers. The three toggles therefore have **no accessible name at all**; a screen reader
announces "checkbox, checked" three times with the row titles unassociated.

---

### C5. `Edit Profile.html` — public profile editor

**Purpose.** Edit the member's public-facing identity. Maps to `/settings/profile`.

**Layout regions.** `.app` grid → `.page-head` (title, sub, `View profile` + `Save changes`) →
four `.card`s: Cover & avatar, About you, Links, Availability.

**Controls.**

| # | Visible label | Element | Evident intent |
|---|---|---|---|
| 88 | `View profile` | `<a class="btn btn-ghost" href="Artist Profile.html">` (38) | Preview the public profile |
| 89 | `Save changes` | `<button class="btn btn-primary">` (39) | Persist |
| 90 | `Replace` + image icon | `<button class="cover-tool">` (49) | Replace the cover image. **No file input** |
| 91 | `Remove` + trash icon | `<button class="cover-tool">` (50) | Remove the cover. **No confirmation** |
| 92 | `Upload new` | `<button class="btn btn-secondary btn-sm">` (56) | Replace the avatar. **No file input** |
| 93 | `Remove` | `<button class="btn btn-ghost btn-sm">` (57) | Remove the avatar |
| 94 | `Display name` | `<input value="Alex Rivera">` (68) | Display name |
| 95 | `Username` | `.input-with-prefix` with prefix `goimg.com/` + `<input value="alex.rivera">` (69) | Username. **The prefix hard-codes a domain** — on a self-hosted instance this must be the operator's configured site URL |
| 96 | `Tagline` (`Shown under your name on your profile.`) | `<input value="Urban Brutalism · Editorial architecture">` (73) | One-line descriptor |
| 97 | `Bio` + `242 / 500` | `<textarea>` + `.char-count` (78–79) | Biography. **The counter is static and wrong** — the value is 206 characters |
| 98 | `Location` | `.input-with-prefix` + `<input value="Mexico City · Berlin">` (84) | Where the member is based |
| 99 | `Pronouns` | `<select>` — `he / him`, `she / her`, `they / them`, `Custom…`, `Prefer not to say` (88) | Pronouns. `Custom…` implies a field that is not drawn |
| 100 | link type ×3 | `<select class="select">` (100, 105, 110) — option sets differ per row: row 1 `Website / Instagram / Are.na / Twitter-X / Mastodon / Other`, row 2 `Instagram / Website / Are.na`, row 3 `Are.na` only | Categorise the link. **Three inconsistent option lists** |
| 101 | link URL ×3 | `<input value="alexrivera.studio" / "@alex.rivera.studio" / "are.na/alex-rivera">` | The link target. No `type="url"`, no scheme, no validation |
| 102 | remove link ×3 | `<button class="btn btn-icon" aria-label="Remove">` (102, 107, 112) | Remove the row |
| 103 | `Add another link` | `<button class="add-link">` (114) | Add a row, up to the stated 5 |
| 104 | `Available for commissions` (`A green dot will show on your profile.`) | `.toggle` (124) | Availability flag |
| 105 | `Booking note` → `Booking Q3 2026` | `.row-value` (128) | **Read-only display of an editable-looking value with no control** |
| 106 | `Open to` → `Architecture · Editorial` | `.row-value` (132) | Same — no control |

**Form fields.** Display name, Username, Tagline, Bio, Location (all bare `<input>`/`<textarea>`
with no `type`, `maxlength`, `pattern`, `required` or `aria-describedby`), Pronouns and three link
types (`<select>`), three link URLs. No `<form>`, no validation, no error slot. Username has no
availability check, no allowed-character hint and no reserved-name handling.

**States present.** `.cover-tool` and `.btn` hovers; toggle checked.

**States the brief requires and the mockup lacks.** Image upload in progress / crop / failed /
too-large (both cover and avatar); **no avatar or no cover** (the empty state a brand-new account
starts in — both are shown populated); username taken / invalid; saving / saved / failed;
disabled Save; the 6th link attempt against the stated 5-link cap; removal confirmation for cover
and avatar; loading; unauthorized.

**Responsive.** `.form-grid.two` collapses at 640px. `.avatar-row` uses `margin-top: -56px;
margin-left: 20px` to overlap the cover, and `.avatar-actions { padding-top: 48px }` to bottom-align
the two buttons beside a 112px avatar — at 390px the avatar (112px) + gap (16px) + two buttons
(`Upload new` ≈104px + `Remove` ≈78px + 8px gap) ≈ 318px plus 24px of page padding, so it just fits
and has no wrap rule. `.link-row` is the real hazard: `160px` select + flexed input + `36px` button
+ two 8px gaps never wraps (§a.8).

**Inline script.** **None.** This is the only page with no page-level `<script>` beyond
`window.__page` and `account-shell.js`. Every one of its 19 controls is inert.

**Mock data shape.** None. Two hotlinked images, both `alt=""` — including the avatar, which is the
one image on the page that genuinely needs alternative text.

**Accessibility.** One `<h1>`, four `<h2>`. Seven inline `<svg>`, none `aria-hidden`. Three
`aria-` attributes, all `aria-label="Remove"` on the link-delete buttons — **three buttons with
the identical accessible name "Remove"**, with nothing to distinguish which link each removes;
the two cover buttons also read "Replace"/"Remove" with no object. Seven `<label>`, none with
`for`. The single toggle has no accessible name.

---

### C6. `Account Settings.html` — sign-in, security, sessions

**Purpose.** Account basics: plan, sign-in credentials, 2FA, connected services, sessions,
destructive account actions. Spans `/settings/account`, `/settings/security`, `/settings/sessions`
and `/settings/connections`.

**Layout regions.** `.app` grid → `.page-head` (title + sub, no actions) → six `.card`s: Plan,
Sign-in, Two-factor authentication, Connected accounts, Sessions (with `.card-foot`), Danger zone.

**Controls.**

| # | Visible label | Element | Evident intent |
|---|---|---|---|
| 107 | `goimg Pro` + `Active` tag + `Unlimited uploads · 4K exports · Renews May 12, 2026` + `Manage` | `.plan-card` (34–41) with `<button class="btn btn-secondary btn-sm">` | Manage a paid subscription. **Vizra has no billing product** — see §e |
| 108 | `Email` `alex@alexrivera.studio · verified` + `Change` | `.row` + `btn-sm` (48–51) | Change the sign-in email |
| 109 | `Password` `Last changed 4 months ago` + `Change` | `.row` + `btn-sm` (52–55) | Change the password |
| 110 | `Passkeys` `2 devices · iPhone, MacBook Pro` + `Manage` | `.row` + `btn-sm` (56–59) | Manage WebAuthn credentials |
| 111 | `Authenticator app` `1Password · Enabled` + `On` tag + toggle | `.row` (66–69) | Enable/disable TOTP. **A toggle cannot express enrolment** (QR, secret, verification code, recovery-code display) |
| 112 | `SMS backup` `+1 ••• ••• 0142` + toggle | `.row` (70–73) | SMS second factor |
| 113 | `Recovery codes` `8 of 10 remaining` + `View` | `.row` + `btn-sm` (74–77) | Reveal recovery codes |
| 114 | `Apple` `Connected as alex@icloud.com` + `Disconnect` | `.row` (84–87) | Unlink an identity provider |
| 115 | `Instagram` `@alex.rivera.studio` + `Disconnect` | `.row` (88–91) | Unlink Instagram |
| 116 | `Google` `Not connected` + `Connect` | `.row` (92–95) | Link Google |
| 117 | `Adobe Creative Cloud` `Import edits from Lightroom` + `Connect` | `.row` (96–99) | Link Adobe |
| 118 | `MacBook Pro · Safari` + `This device` tag / `iPhone 15 Pro · goimg app` / `iPad Air · Safari`, each with `Berlin, Germany`/`Mexico City` + relative time | three `.row` (106–116) | List active sessions |
| 119 | `Sign out` ×2 | `<button class="btn btn-ghost btn-sm">` (111, 115) | Revoke one session. **Two buttons with the identical accessible name** |
| 120 | `Don't recognize a session?` + `Sign out of all` | `.card-foot` + `<button class="btn btn-danger btn-sm">` (118) | Revoke every session |
| 121 | `Export your data` (`Download a ZIP of your photos, albums, and metadata.`) + `Request export` | `.row` (124–127) | Request an export archive |
| 122 | `Deactivate account` (`Temporarily hide your profile. Reactivate any time.`) + `Deactivate` | `.row` (128–131) | Self-deactivation |
| 123 | `Delete account` (`Permanently remove your account and all content.`) + `Delete` | `.row` (132–135) | Delete the account. **No re-auth step, no confirmation, no typed-name gate** |

**Data fields displayed.** Plan name, status, entitlements, renewal date; email + verification
state; password age; passkey count and device names; 2FA provider name and state; recovery-code
remaining count; four provider names with account handles; three session rows (device, browser/app,
city+country, relative last-seen). Every value is a hard-coded literal.

**States present.** `.tag.accent` ("Active", "This device"); `.tag.success` with a `.dot.success`
("On"); toggle checked/unchecked; button hovers.

**States the brief requires and the mockup lacks.** Every one of these flows is a multi-step
dialog that the mockup renders as a single row + button and never draws: change-email
(new address → password confirm → verification email sent → pending state), change-password
(current → new → strength → confirm), 2FA enrolment (secret/QR → verify code → recovery codes
shown once → download/print), recovery-code regeneration, provider connect (OAuth redirect →
return → error), session revoke confirmation, export requested → queued → ready → expired
(an export is a durable job, not a button), **destructive confirmation with re-authentication** for
Deactivate and Delete. Plus: loading, error, disabled, unauthorized/expired-session, and the
zero-state of each card (no passkeys, no connected providers, one session).

**Responsive.** ≤900px the cards go full width and `.row` padding drops to 16px. `.row` is
`display: flex` with no `flex-wrap`, so at 390px each of the 13 rows is `row-main` (flex 1,
wrapping text) + a `btn-sm` with `white-space: nowrap`. The tightest is row 111, whose right side
is a `<div style="display:flex;gap:10px">` holding both the "On" tag and a 44px toggle.

**Inline script.** **None.** All 15 buttons and both toggles are inert.

**Mock data shape.** None. **Zero images and zero inline SVGs** — the only page in the set with
neither. Provider marks are letters in `.conn-logo` divs (`A`, `IG`, `G`, `A`) with inline
brand-colour styles, two of which are the same letter.

**Accessibility.** One `<h1>`, six `<h2>`. **Zero `aria-` attributes on the page.** Two toggles
with no accessible name. Two `Sign out` buttons and two `Disconnect` buttons with duplicate
accessible names. Two `Connect` buttons likewise. The `.tag.success` "On" indicator duplicates the
toggle's state in colour and text but is not programmatically associated with it. `.conn-logo` uses
brand colour as the only identifier for Instagram (a gradient) and Adobe (orange) — colour alone.

---

### C7. `Notifications.html` — "Notifications & Privacy"

**Purpose.** Per-event notification channel preferences, quiet hours, profile privacy defaults,
blocks and comment filtering. Spans `/settings/notifications`, `/settings/privacy`,
`/settings/blocks` and `/settings/content`.

**Layout regions.** `.app` grid → `.page-head` → four `.card`s: How you get notified (a
`1fr 44px 44px 44px` CSS-grid matrix), Quiet hours, Privacy, Blocked & muted.

**Controls.**

| # | Row / control | Element | Channels / options |
|---|---|---|---|
| 124 | `New follower` (`Someone starts following you.`) | three `<input type="checkbox" class="cb">` (45–47) | Push ✓ · Email ✗ · In-app ✓ |
| 125 | `Favorites on your photos` (`Batched daily.`) | three `.cb` (51–53) | ✗ · ✓ · ✓ |
| 126 | `Comments and replies` | three `.cb` (57–59) | ✓ · ✓ · ✓ |
| 127 | `Mentions` (`When someone @mentions you.`) | three `.cb` (63–65) | ✓ · ✓ · ✓ |
| 128 | `Featured in a collection` (`A curator adds you to a collection.`) | three `.cb` (69–71) | ✓ · ✓ · ✓ |
| 129 | `Weekly digest` (`Your top photos & discoveries.`) | three `.cb` (75–77) | ✗ · ✓ · ✗ |
| 130 | `Product announcements` | three `.cb` (81–83) | ✗ · ✓ · ✗ |
| 131 | `Pause push notifications` (`Apply Do Not Disturb during a daily window.`) | `.toggle`, checked (94) | — |
| 132 | `From` | `<select style="width:120px">` — `22:00`, `21:00`, `23:00` (98) | Three options only |
| 133 | `Until` | `<select style="width:120px">` — `07:30`, `08:00`, `07:00` (102) | Three options only |
| 134 | `Profile visibility` (`Who can find your profile.`) | `.segmented` — `Public` / `Signed-in` / `Private` (112) | — |
| 135 | `Who can message you` | `<select style="width:180px">` — `Anyone` / `People you follow` / `Mutual follows only` / `No one` (116) | — |
| 136 | `Show me in search engines` (`Let Google and others index your profile.`) | `.toggle`, checked (120) | — |
| 137 | `Hide EXIF from viewers by default` | `.toggle`, unchecked (124) | — |
| 138 | `Hide precise location` (`Round GPS to the nearest city.`) | `.toggle`, checked (128) | — |
| 139 | `Allow AI training on public photos` (`Opt out of third-party dataset inclusion.`) | `.toggle`, unchecked (132) | — |
| 140 | `Blocked accounts` (`4 accounts can't see or contact you.`) + `Manage` | `btn-sm` (142) | — |
| 141 | `Muted tags` (`Hide photos with these tags from Discover.`) + `Manage` | `btn-sm` (146) | — |
| 142 | `Comment filter` | `.segmented` — `Off` / `Standard` / `Strict` (150) | Three undefined levels |

**Inverted copy — a defect.** Row 139's title is "**Allow** AI training on public photos" and its
help text is "**Opt out** of third-party dataset inclusion." Checking the toggle means the
opposite of the two lines. The control cannot be implemented as drawn.

**Data fields.** Seven event names with descriptions; three channel column headers; two time
values; one blocked-account count (`4`); no muted-tag count.

**States present.** `.cb:checked` (accent fill + CSS-drawn tick); toggle on/off;
`.segmented button.active`.

**States the brief requires and the mockup lacks.** Saving / saved / failed (there is no Save
button at all, so the page implies auto-save with no feedback); disabled channel column when that
channel is unavailable (an operator with no SMTP configured cannot deliver email —
`VZ-EMAIL-001`); "email not verified, so email delivery is off"; quiet-hours rows disabled while
the pause toggle is off (rows 132–133 are live regardless); loading; error; the blocked/muted
management screens themselves (both `Manage` buttons lead nowhere and no list is drawn); empty
states for both lists; destructive confirmation for unblocking.

**Responsive.** The matrix is `grid-template-columns: 1fr 44px 44px 44px` with no media query. At
390px with 12px page padding and 16px card padding, the event-label column gets
390 − 24 − 32 − 132 = **202px** for strings such as "Featured in a collection" plus its sub-line.
The three 20px checkboxes sit in 44px cells, below the 44px touch target only in height
(`.mcell { padding: 12px 0 }` gives 44px total, so this is borderline acceptable). The three
fixed-width `<select>`s (120/120/180px) inside flex rows are the other narrow-viewport risk.

**Inline script (159–161).** One line: segmented `.active` toggle. All 21 checkboxes, all five
toggles, all three selects and both `Manage` buttons are unwired.

**Mock data shape.** None. **Zero images and zero inline SVGs.**

**Accessibility — the worst page in the set.** One `<h1>`, four `<h2>`. **Zero `aria-`
attributes.** The 21 matrix checkboxes have **no `<label>`, no `aria-label`, no
`aria-labelledby` and no `<table>` semantics** — the column headers are `<div class="mhead">` and
the row labels are `<div class="mlabel">`, associated only by CSS grid position. A screen-reader
user hears "checkbox, checked" twenty-one times with no way to know the event or the channel; a
keyboard user tabs through 21 anonymous, focus-invisible (`appearance: none`, no focus style)
controls. The five `.toggle`s likewise have no accessible name. The three `<select>`s have no
label. `.matrix .mrow { display: contents }` removes the row grouping from the box tree, so even
a `<table>` retrofit is not a CSS-only change.

---

### C8. `Photo Insights.html` — member statistics

**Purpose.** Views, favourites, followers and traffic for the member's own work. Maps to `/stats`.

**Layout regions.** `.app` grid → `.page-head` (title, sub, range segmented + Export CSV) →
`.kpis` (`auto-fit, minmax(180px,1fr)`) → `.chart-wrap` (hand-authored SVG) → `.grid-two`
(`1.3fr` Top photos card + `1fr` card carrying both Traffic sources and Audience locations).

**Controls.**

| # | Visible label | Element | Evident intent |
|---|---|---|---|
| 143 | `7d` / `30d` / `90d` / `1y` | `.segmented` ×4 `<button>` (54) | Change the reporting window |
| 144 | `Export CSV` | `<button class="btn btn-secondary btn-sm">` (55) | Download the data |
| 145 | `VIEWS` `184.2k` `↑ +24% vs last 30d` | `.kpi` (60) | Headline metric |
| 146 | `FAVORITES` `12.8k` `↑ +18%` | `.kpi` (61) | — |
| 147 | `NEW FOLLOWERS` `+642` `↑ +9%` | `.kpi` (62) | — |
| 148 | `ENGAGEMENT RATE` `6.9%` `↓ −0.3 pp` | `.kpi` (63) | — |
| 149 | `Views over time` / `Daily views across all published photos` + legend `Views` (accent) and `Favorites` (`oklch(0.72 0.12 220)` dashed) | `<svg viewBox="0 0 800 220" preserveAspectRatio="none">` (77–87) with three gridlines, one filled area path, two stroke paths | Trend chart |
| — | `Feb 20` `Feb 28` `Mar 8` `Mar 15` `Mar 22` `Today` | a flex row of `<span>` (88–90) | X axis. **Six evenly spaced labels over unevenly spaced dates** (8, 8, 7, 7, and an open-ended "Today"); **no Y axis, no values, no units, no tooltip, no data table** |
| 150 | five rows: thumb + title + `N views · N favorites` + rank `1`–`5` | `.top-row` (98–122) | Ranked top photos. **Not links** — inert `<div>`s |
| 151 | `View all photos` | `<a class="link-inline" href="My Photos.html">` (125) | Go to the library. **`.link-inline` is undefined CSS** — renders as unstyled inherited text with no underline or colour |
| 152 | `goimg Discover` 72% / `Direct & shares` 14% / `Search engines` 8% / `Referrals` 4% / `Other` 2% | five `.bar-row` (132–136) | Traffic mix |
| 153 | `United States · 31%` / `Germany · 14%` / `Mexico · 11%` / `Japan · 8%` / `UK · 7%` / `France · 5%` | six `.map-chip` with coloured `.flag` rectangles (141–146) | Audience geography |

**Falsified chart — a defect, not merely mock data.** In control 152 the bar `width` percentages do
not match the printed values: `14%` is drawn at `width:38%`, `8%` at `22%`, `4%` at `12%`, `2%` at
`6%`. Only the 72 % bar is drawn at its stated value. `DESIGN_BRIEF.md` rejects "fake metrics";
`AGENTS.md` says "Do not fabricate outputs". A reviewer reading the picture gets a different answer
from a reviewer reading the numbers.

Two further numeric problems: the six audience-location percentages total 76 %, with no "Other"
row; and the KPI deltas ("+24% vs last 30d") are pinned to the 30d range but do not change with
control 143 because nothing is wired.

**States present.** `.segmented button.active`; `.kpi .delta.up` / `.down`.

**States the brief requires and the mockup lacks.** **Loading** (every panel — this is the one page
that is entirely asynchronous data); **empty** — a new account with zero views, zero favourites and
zero followers, which is what every instance looks like on day one; **error / analytics unavailable**
— `VZ-STATS-002` depends on ClickHouse or on PostgreSQL rollups, and an operator with analytics OFF
must see an honest degraded state rather than zeros; partial data (range longer than the account's
age); CSV export queued/ready/failed; disabled range buttons; no-data-for-this-range; unauthorized.

**Responsive.** `.grid-two` collapses at 900px; `.kpis` auto-fits at 180px. Two hazards: the SVG
uses `preserveAspectRatio="none"` with `height: 220px`, so at 390px the whole curve is horizontally
crushed to 40 % of its authored width and the stroke widths distort; and `.bar-row` is a fixed
`120px 1fr 52px` grid, leaving ~190px of track at 390px. `.page-actions` at ≤900px is
`justify-content: flex-end` on a row holding a 4-button segmented control plus `Export CSV`, which
does not wrap.

**Inline script (155–157).** One line: segmented `.active` toggle. `Export CSV`, the chart, all
five top-photo rows and `View all photos` are unwired.

**Mock data shape.** None. Five hotlinked thumbnails (`alt=""`). The chart is two hand-drawn
cubic-Bézier `d` attributes; there is no series array, no scale and no axis generator.

**Accessibility.** One `<h1>`, three `<h2>` (the "Audience locations" heading is a second
`.card-head` injected inside the same card with an inline border style, so it reads as an `<h2>`
sibling of "Traffic sources"). Five inline `<svg>` plus the chart, none `aria-hidden`. **Zero
`aria-` attributes.** The chart has **no `role="img"`, no title, no description, no accessible
table alternative** — it is unreadable without sight. The two chart series are distinguished by
colour plus a dash pattern; the legend swatch for series 2 is 2.40:1 against white. The
`.kpi .delta` direction is conveyed by a chevron glyph plus green/red — the `+`/`−` prefix in the
text is the only non-colour cue, and it is inside the same 12px string. The `.flag` rectangles are
pure colour with no meaning. Five inert `.top-row` entries that look like list items and carry no
list semantics.

---

## d. Cross-page states and accessibility

### d.1 States present anywhere in the set

hover (buttons, rows, cards, side links, album cards, photo cards, queue items, licences);
`.active` selection on `.segmented`, `.side-link`, `.view-btn`, `.queue-item`, `.step`,
`.mobile-tabs .tab-m`; checked on `.toggle` and `.cb`; `.selected` on `.pcard` and `.license`;
`.drag-over` on `.drop`; `.tag` semantic badges (accent/success/warn/danger); `.dot` status halos;
`.step.done`; three `.queue-item .status` variants; `.btn-primary[disabled]` (defined, never used).

### d.2 States absent everywhere in the set

| Missing state | Where it is required |
|---|---|
| **Loading / skeleton** | every page; `DESIGN_BRIEF.md` "loading/empty/error/success/disabled states" |
| **Empty** | empty library, empty album list, empty album, no avatar/cover, no passkeys, no connected providers, no sessions but this one, no blocked accounts, no muted tags, no stats — i.e. **the state every freshly installed instance is in** |
| **Error / retry** | upload failure, save failure, listing failure, export failure, analytics unavailable; `VZ-SEARCH-004`-style honest degradation has no analogue here |
| **Progress** | the only progress indicator in the set is a static 65 % conic gradient with no `role="progressbar"` and no `aria-live` |
| **Disabled** | no control anywhere carries `disabled`; the one disabled style is never applied |
| **Destructive confirmation** | four destructive actions (`Delete` photo, bulk `Delete`, `Deactivate`, `Delete account`) plus cover/avatar `Remove` and `Sign out of all` — **no dialog, sheet or confirmation pattern exists anywhere in the account set** |
| **Success / saved** | no toast, no inline confirmation, no dirty-state indicator; two pages have Save buttons, three have none and imply auto-save |
| **Unauthorized / not-found / session-expired** | `prompt 02` names "unauthorized"; `prompt 03` requires an "expired session" test |
| **Dark mode** | §a.9 |
| **Reduced motion** | §a.10 |
| **Focus-visible** | §a.11 — one rule, on one component |
| **`aria-live`** | nothing announces selection count, save result, upload progress or filter changes |

### d.3 Accessibility findings that recur across the set

1. **61 inline `<svg>` elements across the eight pages plus the shell; exactly zero carry
   `aria-hidden="true"`.** (`account-shell.js`'s single `aria-hidden` is on the `<span
   class="brand-mark">`, not an SVG.) `DESIGN_BRIEF.md`: "keep its redundant decorative SVG hidden
   from assistive technology."
2. **Four of the eight pages have zero `aria-` attributes** (`Account Settings`, `My Albums`,
   `Edit Photo`, `Notifications`, `Photo Insights` — five, in fact). Total across the set: 22.
3. **14 `.toggle` components, none with an accessible name.** The pattern is
   `<label class="toggle"><input type="checkbox"><span class="track"><span class="thumb"></label>`
   — the label wraps the input but has no text, so the computed name is empty. The visible
   `.row-title` beside it is never associated.
4. **35 form controls in total, 2 correctly labelled.** Only `Upload Studio.html`'s `for="title"`
   and `for="desc"` associate a label with a control. Every other `<label>` lacks `for`; the 21
   notification checkboxes and all eight `<select>` elements have no label of any kind.
5. **No `<form>` element anywhere in the set**, so no control can be submitted by keyboard and no
   native validation exists.
6. **Zero `<input type="file">` in the set**, while three surfaces (drop zone, cover Replace,
   avatar Upload new) exist to receive files.
7. **`div`/`span`-as-button:** 15 `.pcard .check` selection targets (nested inside `<a>`), three
   `.queue-item` rows, four `.license` pseudo-radios, three `.step` nodes, five `.top-row` entries.
8. **Duplicate accessible names:** `Remove` ×3 (Edit Profile links) + ×1 (avatar) + ×1 (cover);
   `Sign out` ×2; `Disconnect` ×2; `Connect` ×2; `Manage` ×3; `Change` ×2; `New album` ×2.
9. **Unlabelled icon-only buttons:** five `.alb-more` (⋯), three `.tag-input .t button` on
   Edit Photo.
10. **`alt=""` on 41 of 42 images**, including the profile avatar and every album cover.
11. **No `aria-current`** on the active side link or the active mobile tab; **no `aria-pressed`**
    on any of the 24 `.segmented` buttons or the two `.view-btn`s.
12. **`role="tablist"` once (Upload Studio 534) with no `role="tab"` children** and no tabpanel;
    the six other `.segmented` instances have no role at all — the same component is announced
    three different ways.
13. **Navigation on `<select>` change** with no accessible name (`#mobile-header-slot`), a WCAG
    3.2.2 hazard.
14. **Hover-only information**: `.pmeta` (per-photo view and favourite counts) and `.pcard .check`
    (the entire selection affordance) are `opacity: 0` until `:hover`. On touch they do not exist.
15. **Colour-only state**: the toggle (track colour + 18px thumb translation), `.kpi .delta`
    up/down, `.dot` status, the three `.queue-item .status` variants, `.flag` country swatches,
    `.conn-logo` brand fills, the two chart series.

---

## e. Conflicts with `docs/DESIGN_BRIEF.md`, `AGENTS.md` and the ledger

| # | Conflict | Evidence | Rule |
|---|---|---|---|
| A1 | **A paid plan card in a product with no billing** | `Account Settings.html` 31–43: `goimg Pro`, `Active`, `Unlimited uploads · 4K exports · Renews May 12, 2026`, `Manage` | `docs/PRODUCT_CHARTER.md`: "Do not invent a SaaS billing project." `docs/PRODUCT_SPEC.md` §1: "Vizra has **no billing**. Every capability a reference product paywalls … is provided ungated under instance-operator policy and quotas (Q-019)." `VZ-NSFW-001`: "ungated by billing." `VZ-EXPLORE-003`: "no billing bias." **This card has no ledger ID and must be removed, not re-skinned.** The legitimate surface in its place is storage quota and usage (`VZ-QUOTA-001`, `/settings/storage`), which the set does not have |
| A2 | **`RAW` and `TIFF` advertised as accepted upload formats** | `Upload Studio.html` 361–362 `.format-chip`; and all three queue files are `.RAF` (Fujifilm RAW), as is the preview filename | `VZ-MEDIA-002`: "JPEG, PNG, GIF (animated), WebP (animated), AVIF, BMP; … **RAW declined**"; its provenance note reads "AVIF JPG JPEG PNG BMP GIF WEBP MOV MP4 WEBM — **no HEIC/TIFF/SVG**". The mockup advertises two declined formats and makes RAW the entire worked example |
| A3 | **`HEIC` advertised unconditionally** | `Upload Studio.html` 360 | `VZ-MEDIA-010`: HEIC/HEIF decode is **full profile, config-gated, OFF by default**, licence-reviewed build. A format chip that is always shown states a capability most instances will not have |
| A4 | **GIF, AVIF and BMP missing from the advertised formats** | same chip row | `VZ-MEDIA-002` requires all three, including animated GIF/WebP |
| A5 | **Binary "Safe for all audiences" instead of three safety levels** | `Upload Studio.html` 556–559 | `VZ-NSFW-001`: "safety levels (**safe / moderate / restricted**)… viewer-side filter, blur, lock editing". A binary flag is the Chevereto behaviour the ledger explicitly improves on ("Chevereto: binary NSFW flag… Vizra outcome: three levels"). `Edit Photo.html` drops the control entirely |
| A6 | **The `unlisted` visibility option does not exist anywhere** | Visibility segmented on `Upload Studio.html` 534 and `Edit Photo.html` 89 offer `Public / Followers / Private`; `My Photos.html` 61 filters `All / Published / Drafts / Private` | `VZ-PRIVACY-001` (M1): "public, **unlisted (link)**, private". Unlisted is a core-profile, first-slice obligation and it is absent from every control that sets or filters visibility. Meanwhile `Followers` is `VZ-PRIVACY-004`, **full profile, M5** |
| A7 | **Binary "Allow downloads"** | `Edit Photo.html` 100–101 | `VZ-DOWNLOAD-001`: owner setting is **nobody / followers / members / anyone**, plus a size picker |
| A8 | **Single-select album membership** | `Edit Photo.html` 57; `Upload Studio.html` 442 | `VZ-ALBUM-001`: "**many-to-many membership**; a photo can be in several albums". A `<select>` cannot express it |
| A9 | **No sub-albums** | `My Albums.html` renders a flat grid with no nesting affordance | `VZ-ALBUM-001`: "nested sub-albums (cycle-safe)" |
| A10 | **No `password` album privacy** | `My Albums.html` 46 filters `Public / Unlisted / Private` | `VZ-ALBUM-002`: "public, private, **link-only, password**; share grants per album" |
| A11 | **Alt text is absent from both editors** | `Upload Studio.html` and `Edit Photo.html` Details cards | `VZ-LIBRARY-002`: "**alt text is a first-class field** feeding embeds, federation and OG". `VZ-A11Y-001` depends on it. Forty-one of forty-two images in the mockups themselves carry `alt=""` |
| A12 | **Drag-and-drop upload with no keyboard or file-picker path** | `Upload Studio.html` 351–365; no `<input type="file">` in the set | `prompt 03`: "A drag-and-drop upload is not sufficient without a usable keyboard/file-picker alternative." `VZ-UPLOAD-003` requires "file picker, drag-and-drop, clipboard paste, device camera" — only one of four is present, and only as a class toggle |
| A13 | **Falsified chart** | `Photo Insights.html` 132–136: 14 % drawn at 38 %, 8 % at 22 %, 4 % at 12 %, 2 % at 6 % | `DESIGN_BRIEF.md` "Reject… fake metrics"; `AGENTS.md` "Do not fabricate outputs" |
| A14 | **Three static character counters, all wrong** | `45 / 80` for a 35-char value (Upload 431); `160 / 500` for 152 (436); `242 / 500` for 206 (Edit Profile 79) | Same rule; also `DESIGN_BRIEF.md` "no-op handlers" |
| A15 | **Hard-coded brand domain in a self-hosted product** | `Edit Profile.html` 69 prefix `goimg.com/`; `Upload Studio.html` 532 "on goimg"; `Photo Insights.html` 51, 132 "goimg" | The instance URL is operator configuration (`VZ-ADMIN-003` website settings, `VZ-BRAND-001` logo/name). Also README standing note 3 |
| A16 | **Inverted privacy copy that cannot be implemented** | `Notifications.html` 131: title "**Allow** AI training on public photos", help "**Opt out** of third-party dataset inclusion" | `DESIGN_BRIEF.md` "Provide visible labels when meaning is uncertain"; the two lines contradict |
| A17 | **"Changes apply instantly" beside explicit Cancel/Save** | `Edit Photo.html` 30 vs 33–34 | Two mutually exclusive persistence models in one header |
| A18 | **No destructive-confirmation pattern anywhere** | six destructive controls, no dialog | `DESIGN_BRIEF.md` states list; `prompt 02` "destructive-confirmation states"; `ui-controls.json` `library.bulk.delete` says "bulk delete **with confirmation**", `photo.delete` "delete **with confirmation**", `settings.account.delete` "authenticated (**re-auth**)" |
| A19 | **61 hand-inlined SVG icons instead of the typed Lucide registry**, with `stroke-width` 1.7 / 1.8 / 1.9 / 2 / 2.2 / 2.5 / 3 and sizes 10–26px, and three icons duplicated at different stroke weights between the sidebar and the tab bar | `account-shell.js` and every page | `DESIGN_BRIEF.md`: "one consistent licensed icon family… named, statically imported SVG components behind a typed semantic registry. Verify actual exports in the pinned package." `VZ-DESIGN-001` requires a registry test |
| A20 | **42 hotlinked Unsplash images** | 15 (My Photos) + 15 (My Albums) + 5 (Insights) + 4 (Upload) + 2 (Edit Profile) + 1 (Edit Photo) | `AGENTS.md` "no mock data in production paths"; README standing note 2; a third-party hotlink is also a visitor-IP leak and a CSP problem |
| A21 | **Destructive cropping by default** | every URL carries `&fit=crop`; `.pcard img`, `.alb-thumbs img`, `.top-thumb img`, `.queue-item .thumb img`, `.avatar-big img`, `.cover-edit img` all `object-fit: cover`; `.pcard` forces `aspect-ratio: 1` | `DESIGN_BRIEF.md`: "Preserve the image's aspect ratio; do not default to destructive cropping." Only `.preview-body img` and `.photo-pane img` use `object-fit: contain` |
| A22 | **No dark mode** | §a.9 | `DESIGN_BRIEF.md` "excellent light/dark modes"; `VZ-DESIGN-001` "light/dark" |
| A23 | **No reduced-motion handling** | §a.10 | `DESIGN_BRIEF.md`; `VZ-A11Y-001` |
| A24 | **Contrast failures on the primary and destructive buttons and on every status colour** | §a.12 | `VZ-A11Y-001` "contrast ≥ 4.5:1 text / 3:1 UI over real backings" |
| A25 | **Focus indication missing on four input surfaces and 21 checkboxes; one `:focus-visible` rule in 450 lines** | §a.11 | `VZ-A11Y-001` "visible focus" |
| A26 | **The library bulk-action bar is occluded by the mobile tab bar** | §a.13 | `DESIGN_BRIEF.md` "Reject… missing mobile actions"; `VZ-RESPONSIVE-001` |
| A27 | **Per-photo metadata and the entire selection affordance are hover-only** | `My Photos.html` 22–28 | Same rules |
| A28 | **Upload Studio has no account navigation on desktop** | §b.4 | `VZ-CONTROLS-001` (every route reachable); `DESIGN_BRIEF.md` "Reject dead links" — the only escape is `href="#"` |
| A29 | **Two classes used and never defined** (`.view-btn`/`.view-toggle`, `.link-inline`) and **seven declared and never used** (`.eyebrow`, `.muted`, `.callout`, `.row-chev`, `.stack-sm`, `.stack-md`, `--radius-xs`) | §b.6 | `VZ-DESIGN-001` "approved tokens and components"; a control with no style is a dead control |
| A30 | **Token indiscipline** | 14 font sizes incl. four fractional; 12 radii against five tokens with three unused; 14 shadow recipes against three tokens; spacing on no grid; `--font-display` present in one mockup family and absent in the other | `VZ-DESIGN-001` |
| A31 | **"goimg" brand, gradient mark, and the "artists"/"curator" vocabulary** | throughout; `Notifications.html` 68 "A curator adds you to a collection" | README standing note 3; Vizra's ledger vocabulary is members/photographers/users. A vocabulary decision is an owner call |
| A32 | **Prototype presented with fixtures only** | no fetch, no state, no API shape on any page; every "handler" is a class toggle | `DESIGN_BRIEF.md`: "Prototypes may use fixtures; **shipping UI must use real APIs**." Recorded so it is not mistaken for evidence |

---

## f. Control-to-action matrix

Action IDs follow the dotted convention already used in `docs/quality/ui-controls.json`
(`surface.component.verb`). **Proposed** means proposed by this inventory; the "Existing" column
names the row in `ui-controls.json` when one already covers the control. Milestones are from
`docs/MILESTONES.md`; where a control's ledger IDs span milestones, the **latest** governs when the
control can be honest. **`NO LEDGER ID`** means the control implies a capability that no entry in
`docs/quality/features.json` covers — per the brief, none has been invented.

### f.1 Shell (controls 1–20)

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 1 | Brand → gallery | `shell.brand.home` | — | `VZ-EXPLORE-001`, `VZ-BRAND-001/002` (site name, logo, homepage) | M3 / M5 |
| 2 | Nav search (`Search your library…`) | `library.search.submit` | — | `VZ-LIBRARY-001` ("filters"), `VZ-PROFILE-001` ("search within user"). As a **global** search field: `shell.nav.search` / `VZ-SEARCH-001` — the placeholder scopes it to the library, which `VZ-SEARCH-001` does not cover | M1 (library) / M3 (global) |
| 3 | Notifications bell | `shell.nav.notifications` | `shell.nav.notifications` | `VZ-NOTIFY-001` | M2 |
| 4 | Upload icon | `shell.nav.upload` | `shell.nav.upload` | `VZ-UPLOAD-001`, `VZ-UPLOAD-005` | M1 / M3 |
| 5 | Account avatar `MK` | `shell.nav.account` | `shell.nav.account` | `VZ-AUTH-001` (sign out), `VZ-ACCOUNT-001` | M1 / M2 |
| 6 | Sidebar: My Photos `312` | `shell.side.library` | — | `VZ-LIBRARY-001`; the count is `VZ-LIBRARY-001` / `VZ-STATS-001` | M1 / M3 |
| 7 | Sidebar: Albums `24` | `shell.side.albums` | — | `VZ-ALBUM-001` | M1 |
| 8 | Sidebar: Upload | `shell.side.upload` | — | `VZ-UPLOAD-001` | M1 |
| 9 | Sidebar: Insights | `shell.side.stats` | — | `VZ-STATS-002` | **M6** |
| 10 | Sidebar: Edit Profile | `shell.side.profile` | — | `VZ-ACCOUNT-001` | M2 |
| 11 | Sidebar: Account | `shell.side.account` | — | `VZ-AUTH-001`, `VZ-ACCOUNT-002` | M1 / M3 |
| 12 | Sidebar: Notifications & Privacy | `shell.side.notifications` | — | `VZ-ACCOUNT-004`, `VZ-NOTIFY-001`, `VZ-PRIVACY-001` | M1 / M2 |
| 13 | Sidebar: Help & Support (`#`) | `shell.side.help` | — | `VZ-PAGE-001` (custom pages) | **M5** |
| 14 | Sidebar: Back to gallery | `shell.side.exit` | — | `VZ-EXPLORE-001` | M3 |
| 15 | Mobile tab: Home | `shell.tabbar.home` | — | `VZ-EXPLORE-001`, `VZ-BRAND-002` | M3 / M5 |
| 16 | Mobile tab: Library | `shell.tabbar.library` | — | `VZ-LIBRARY-001` | M1 |
| 17 | Mobile tab: Upload | `shell.tabbar.upload` | — | `VZ-UPLOAD-001` | M1 |
| 18 | Mobile tab: Insights | `shell.tabbar.stats` | — | `VZ-STATS-002` | **M6** |
| 19 | Mobile tab: You | `shell.tabbar.profile` | — | `VZ-ACCOUNT-001`, `VZ-PROFILE-001` | M2 |
| 20 | Mobile section `<select>` | `shell.side.navigate` | — | `VZ-RESPONSIVE-001` (mobile equivalent of the sidebar) | M1 |

### f.2 `Upload Studio.html` (21–47)

**`VZ-UPLOAD-006` — the entire "upload page options" set (title, description, tags, album,
category, privacy, NSFW, expiration) — is M3.** M1 requires only `VZ-UPLOAD-001` (authenticated
JPEG/PNG upload with real-byte validation) and `VZ-UPLOAD-003` (sources). Most of this page
therefore cannot be honest at M1.

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 21 | Step rail (3 inert steps) | `upload.progress.render` | — | `VZ-UPLOAD-002` (progress) | **M3** |
| 22 | `Save draft & exit` | `upload.draft.save` | — | **NO LEDGER ID** — no draft/unpublished asset state exists. Nearest: `VZ-UPLOAD-012` moderation queue (operator-owned, not the uploader's), `VZ-UPLOAD-008` expiration | n/a |
| 23 | Drop zone | `upload.dropzone` | `upload.dropzone` | `VZ-UPLOAD-003` | **M1** |
| 24 | `choose from your library` | `upload.picker` | `upload.picker` | `VZ-UPLOAD-003` | **M1** |
| 25 | Format chips `JPG PNG HEIC RAW TIFF WebP` | `upload.formats.render` | — | `VZ-MEDIA-002` — **CONFLICT: RAW declined, TIFF excluded**; `VZ-MEDIA-010` for HEIC (full, OFF by default); GIF/AVIF/BMP missing | M3 |
| 26 | `up to 50 files, 100 MB each` | `upload.limits.render` | — | `VZ-UPLOAD-013` (per-role size, pixel, thread, format limits), `VZ-QUOTA-001` | M3 / M1 |
| 27 | Queue row ×3 | `upload.queue.select` | — | `VZ-UPLOAD-002` ("per-file progress") | **M3** |
| 28 | Per-file status `ready` / `draft` / `uploading 65%` | `upload.file.status` | — | `VZ-UPLOAD-002` for `uploading`; **`draft` → NO LEDGER ID** (as #22) | M3 / n/a |
| 29 | `Add more` | `upload.picker` | `upload.picker` | `VZ-UPLOAD-003` | M1 |
| 30 | Preview EXIF bar | `upload.exif.render` | — | `VZ-MEDIA-004` | **M1** |
| 31 | `Title` | `upload.options.title` | — | `VZ-UPLOAD-006`, `VZ-LIBRARY-002` | **M3** |
| 32 | Title char count | — | — | `VZ-UPLOAD-006`; a field-length limit is undefined in the ledger → **NO LEDGER ID for `80`** | M3 / n/a |
| 33 | `Description` | `upload.options.description` | — | `VZ-UPLOAD-006`, `VZ-LIBRARY-002` | **M3** |
| 34 | Description char count | — | — | as #32 (`500`) | n/a |
| 35 | `Album` select incl. `— New album…` | `upload.options.album` | `upload.options.album` | `VZ-UPLOAD-006`, `VZ-ALBUM-001` — **CONFLICT: single-select vs many-to-many** | M3 / M1 |
| 36 | `Location` | `upload.options.location` | — | `VZ-GEO-001` ("location per photo… from EXIF when allowed or manual") | **M5** |
| 37 | Tag remove ×4 | `upload.options.tags` | `upload.options.tags` | `VZ-UPLOAD-006`, `VZ-TAG-001` | M3 |
| 38 | Tag input (`Add a tag…`) | `upload.options.tags` | `upload.options.tags` | same; autocomplete is `VZ-TAG-001` | M3 |
| 39 | Licence ×4 | `upload.options.license` | — | `VZ-LICENSE-001` — ledger set is "All Rights Reserved, Public Domain, CC0, **CC 4.0 family**"; the mockup offers only BY and BY-NC (missing BY-SA, BY-ND, BY-NC-SA, BY-NC-ND) and merges Public Domain with CC0 | **M5** |
| 40 | Visibility `Public / Followers / Private` | `upload.options.privacy` | `upload.options.privacy` | `VZ-PRIVACY-001` (public/**unlisted**/private) + `VZ-PRIVACY-004` (`Followers`, full) — **CONFLICT: `unlisted` missing, `Followers` is M5** | M1 / **M5** |
| 41 | `Allow comments` | `upload.options.comments` | — | `VZ-COMMENT-001` ("owner controls") | **M2** |
| 42 | `Show EXIF` | `upload.options.exif` | — | `VZ-MEDIA-004` | **M1** |
| 43 | `Safe for all audiences` | `upload.options.safety` | — | `VZ-NSFW-001` — **CONFLICT: binary vs three levels** | **M2** |
| 44 | `2 of 3 ready · 1 still uploading` | `upload.batch.status` | — | `VZ-UPLOAD-002` | M3 |
| 45 | `Save as draft` | — | — | **NO LEDGER ID** (as #22) | n/a |
| 46 | `Schedule` | `upload.schedule` | — | **NO LEDGER ID** — there is no scheduled-publication capability anywhere in the ledger. Nearest and opposite: `VZ-UPLOAD-008` (time-based **expiry**) | n/a |
| 47 | `Publish all` | `upload.start` | `upload.start` | `VZ-UPLOAD-001`, `VZ-UPLOAD-002`, `VZ-QUOTA-001`, `VZ-JOBS-001` | **M1** |
| — | **Ledger controls this page omits** | — | — | `upload.cancel` and `upload.retry` (`VZ-UPLOAD-002`); `upload.url` (`VZ-UPLOAD-004`); paste and camera sources (`VZ-UPLOAD-003`); category (`VZ-UPLOAD-006`, `VZ-CATEGORY-001`); expiration and delete link (`VZ-UPLOAD-008`); duplicate detection (`VZ-UPLOAD-007`); `upload.result.embed` (`VZ-UPLOAD-009`, `VZ-SHARE-002`); alt text (`VZ-LIBRARY-002`); content type (`VZ-PRIVACY-003`); quota usage (`VZ-QUOTA-001`); guest-upload variant (`VZ-UPLOAD-005`); moderation-pending (`VZ-UPLOAD-012`) | — |

### f.3 `My Photos.html` (48–63)

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 48 | `Insights` | `shell.side.stats` | — | `VZ-STATS-002` | **M6** |
| 49 | `Upload` | `shell.nav.upload` | `shell.nav.upload` | `VZ-UPLOAD-001` | M1 |
| 50 | `Search your photos…` | `library.search` | — | `VZ-LIBRARY-001` | M1 |
| 51 | `All 312` | `library.filter.all` | — | `VZ-LIBRARY-001` | M1 |
| 51a | `Published 280` | `library.filter.public` | — | `VZ-PRIVACY-001` — "published" is not a ledger state; the ledger's axis is public/unlisted/private → **NO LEDGER ID for a published/unpublished axis** | n/a |
| 51b | `Drafts 22` | `library.filter.draft` | — | **NO LEDGER ID** (as #22) | n/a |
| 51c | `Private 10` | `library.filter.private` | — | `VZ-LIBRARY-001` ("filters… private"), `VZ-PRIVACY-001` | M1 |
| — | missing filter: `Unlisted` | — | — | `VZ-PRIVACY-001` | M1 |
| 52 | Sort `Newest / Oldest / Most favorited / Most viewed` | `library.sort` | — | `VZ-LIBRARY-001` sorts are "date taken / uploaded / views / name" — `Newest`/`Oldest`/`Most viewed` map; **`Most favorited` → NO LEDGER ID as a library sort key** (`VZ-FAVORITE-001` supplies the count, not the ordering); **`name` sort is missing** | M1 / n/a |
| 53–54 | View `Grid` / `Rows` | `library.view.density` | — | `VZ-LISTING-001` is an **owner** setting ("fixed/fluid grid, columns per device"), not a per-viewer toggle → **NO LEDGER ID for a viewer-level density switch** (identical finding to `INVENTORY-search.md` §h.3 #31–33) | M3 (owner) / n/a |
| 55 | Photo card ×15 | `library.grid.item` | `library.grid.item` | `VZ-LIBRARY-001`, `VZ-VIEWER-001` — **CONFLICT: the existing control's action is "open in viewer"; every card here links to the edit screen** | M1 |
| 56 | Selection check ×15 | `library.select.item` | `library.select.all` (partial) | `VZ-LIBRARY-001` ("selects by click/checkbox/drag/keyboard"). The existing `library.select.all` control (select-all `.` / clear `Z`) **has no counterpart in the mockup** | M1 |
| 57 | `2.1k` / heart `820` | `library.item.stats` | — | `VZ-STATS-001` (per-item views), `VZ-FAVORITE-001` (public count) | M3 / M2 |
| 58 | `Draft` badge | — | — | **NO LEDGER ID** (as #22) | n/a |
| 58a | `Private` badge | `library.item.visibility` | — | `VZ-PRIVACY-001` | M1 |
| 59 | `3 selected` | `library.select.count` | — | `VZ-LIBRARY-001` | M1 |
| 60 | `Move to album…` | `library.bulk.album` | `library.bulk.album` | `VZ-LIBRARY-001`, `VZ-ALBUM-001`. Note the label says **Move**, the ledger means **add** (many-to-many) | M1 |
| 61 | `Set visibility` | `library.bulk.privacy` | `library.bulk.privacy` | `VZ-LIBRARY-001`, `VZ-PRIVACY-001` | M1 |
| 62 | `Download` | `library.bulk.download` | — | `VZ-DOWNLOAD-001` ("bulk zip of selected… bounded (e.g. 500 items) as a job") | **M3** |
| 63 | `Delete` | `library.bulk.delete` | `library.bulk.delete` | `VZ-LIBRARY-001`, `VZ-ACCOUNT-003` ("user content deletion toggle" — the operator can disable this) | M1 / **M2** |
| — | **Ledger controls this page omits** | — | — | filters: untagged, not-in-album, NSFW, media type, date range (`VZ-LIBRARY-001`); bulk edit info / tags / category / date time-shift (`VZ-LIBRARY-002`); select-all and clear shortcuts (`library.select.all`); pagination (`VZ-LISTING-001`) | — |

### f.4 `My Albums.html` (64–71)

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 64, 65 | `New album` ×2 | `album.create` | `album.create` | `VZ-ALBUM-001` | **M1** |
| 66 | `All 24 / Public / Unlisted / Private` | `albums.filter.privacy` | — | `VZ-ALBUM-002` — **`password` mode missing** | M1 |
| 67 | Sort `Recently updated / A — Z / Most photos` | `albums.sort` | — | `VZ-ALBUM-003` ("listing sorts") | **M3** |
| 68 | Album cover link ×5 | `album.open` | — | `VZ-ALBUM-001`, `VZ-SHARE-003` (route shape `/a/{id}`) | M1 / M3 |
| 69 | Title + `N photos · Updated … ` | `album.summary.render` | — | `VZ-ALBUM-001` | M1 |
| 70 | Visibility pill `Public / Private / Unlisted` | `album.privacy.render` | `album.privacy` | `VZ-ALBUM-002` | M1 |
| 71 | ⋯ menu ×5 | `album.menu.open` | — | The menu is not drawn, so its contents are unknown. The plausible items map to `VZ-ALBUM-001` (rename, cover, delete, reorder, sub-album) and `VZ-ALBUM-002` (privacy, share grants) — **as drawn, an unlabelled button with no defined action: NO LEDGER ID until the menu exists** | M1 / n/a |
| — | **Ledger controls this page omits** | — | — | `album.cover` (H), `album.reorder`, `album.sub.create` (J), `album.delete` (`VZ-ALBUM-001`); `album.share-grant` and `/settings/shares` (`VZ-ALBUM-002`); album description; album comments and favourites (`VZ-ALBUM-004`, M3); CTA buttons (`VZ-BRAND-004`, M5) | — |

### f.5 `Edit Photo.html` (72–87)

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 72 | `← My Photos` | `photo.edit.back` | — | `VZ-LIBRARY-001` | M1 |
| 73 | `Cancel` | `photo.edit.cancel` | — | `VZ-LIBRARY-002` | M3 |
| 74 | `Save changes` | `photo.edit.save` | `photo.edit` | `VZ-LIBRARY-002` | **M3** |
| 75 | `Title` | `photo.edit.title` | `photo.edit` | `VZ-LIBRARY-002` | M3 |
| 76 | `Description` | `photo.edit.description` | `photo.edit` | `VZ-LIBRARY-002` | M3 |
| 77 | `Album` | `photo.add-to-album` | `photo.add-to-album` | `VZ-ALBUM-001` — **CONFLICT: single-select** | M1 |
| 78 | `License` | `photo.edit.license` | — | `VZ-LICENSE-001` | **M5** |
| 79 | `Location` | `photo.edit.location` | — | `VZ-GEO-001` | **M5** |
| 80, 81 | Tags (remove ×3, add) | `photo.edit.tags` | `photo.edit` | `VZ-LIBRARY-002`, `VZ-TAG-001` | M3 |
| 82 | Visibility segmented | `photo.privacy` | `photo.privacy` | `VZ-PRIVACY-001` (+ `VZ-PRIVACY-004` for `Followers`) — **CONFLICT: `unlisted` missing** | M1 / **M5** |
| 83 | `Allow comments` | `photo.edit.comments` | — | `VZ-COMMENT-001` | **M2** |
| 84 | `Show EXIF data` | `photo.edit.exif` | `photo.exif.tab` (viewer side) | `VZ-MEDIA-004` | **M1** |
| 85 | `Allow downloads` | `photo.edit.download` | — | `VZ-DOWNLOAD-001` — **CONFLICT: binary vs four-way** | **M3** |
| 86 | EXIF rows ×5 (read-only) | `photo.exif.render` | `photo.exif.tab` | `VZ-MEDIA-004`. **No GPS row is shown despite a Location field** — `VZ-MEDIA-004`/`VZ-GEO-001` require GPS to be visible and controllable to the owner | M1 |
| 87 | `Delete` | `photo.delete` | `photo.delete` | `VZ-LIBRARY-001`, `VZ-ACCOUNT-003` — the existing control specifies "delete **with confirmation**"; none is drawn | M1 / M2 |
| — | **Ledger controls this page omits** | — | — | alt text (`VZ-LIBRARY-002`); category (`VZ-CATEGORY-001`); date taken / uploaded editing (`VZ-LIBRARY-002`); safety level (`VZ-NSFW-001`); content type (`VZ-PRIVACY-003`); hide-from-search (`VZ-PRIVACY-002`); replace original and lossless rotate (`VZ-LIBRARY-003`, M5); share and embed (`VZ-SHARE-001/002`); add-to-gallery, add-to-group (M5) | — |

### f.6 `Edit Profile.html` (88–106)

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 88 | `View profile` | `profile.preview` | — | `VZ-PROFILE-001` | **M2** |
| 89 | `Save changes` | `settings.profile.save` | — | `VZ-ACCOUNT-001` | **M2** |
| 90, 91 | Cover `Replace` / `Remove` | `settings.profile.background` | — | `VZ-ACCOUNT-001` ("background"; "avatar/background size limits set by admin" — no limit is surfaced), `VZ-STORAGE-015` (site/user assets) | M2 / **M4** |
| 92, 93 | Avatar `Upload new` / `Remove` | `settings.profile.avatar` | — | `VZ-ACCOUNT-001` | M2 |
| 94 | `Display name` | `settings.profile.display_name` | — | `VZ-ACCOUNT-001` | M2 |
| 95 | `Username` (`goimg.com/` prefix) | `settings.profile.username` | — | `VZ-ACCOUNT-001`; the prefix is `VZ-ADMIN-003` (site URL) — **hard-coding a domain conflicts with self-hosting** | M2 |
| 96 | `Tagline` | `settings.profile.tagline` | — | **NO LEDGER ID** — `VZ-ACCOUNT-001` enumerates username, display name, bio, website, avatar, background, language, timezone, privacy. There is no tagline field | n/a |
| 97 | `Bio` + counter | `settings.profile.bio` | — | `VZ-ACCOUNT-001`; the `500` limit → **NO LEDGER ID** | M2 / n/a |
| 98 | `Location` (profile) | `settings.profile.location` | — | **NO LEDGER ID** as a profile field. `VZ-GEO-001` is per-photo geotagging, not a profile attribute | n/a |
| 99 | `Pronouns` | `settings.profile.pronouns` | — | **NO LEDGER ID** — zero occurrences in the ledger | n/a |
| 100–102 | Link rows ×3 (type, URL, remove) | `settings.profile.links` | — | `VZ-ACCOUNT-001` provides **one** "website" field. A typed, repeatable link list (Instagram / Are.na / Twitter-X / Mastodon / Other) → **NO LEDGER ID**. `VZ-AP-001` and `VZ-AT-001` are protocol identities, not profile links | n/a |
| 103 | `Add another link` | same | — | **NO LEDGER ID**; the "up to 5" cap likewise | n/a |
| 104 | `Available for commissions` | `settings.profile.availability` | — | **NO LEDGER ID** — zero occurrences of "commission" in the ledger. Also a commerce-adjacent surface in a product with no billing (see A1) | n/a |
| 105 | `Booking note` → `Booking Q3 2026` | same | — | **NO LEDGER ID**; and it is rendered as a read-only value with no control | n/a |
| 106 | `Open to` → `Architecture · Editorial` | same | — | **NO LEDGER ID** | n/a |
| — | **Ledger fields this page omits** | — | — | language, timezone, profile privacy (`VZ-ACCOUNT-001` — privacy lives on `Notifications.html` instead); website as a distinct field; the member-visible quota/usage (`VZ-QUOTA-001`) | — |

### f.7 `Account Settings.html` (107–123)

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| 107 | Plan card + `Manage` | — | — | **NO LEDGER ID — and a direct contradiction** of `docs/PRODUCT_SPEC.md` §1 and `docs/PRODUCT_CHARTER.md`: Vizra has no billing. The legitimate replacement surface is `VZ-QUOTA-001` (`/settings/storage`, "usage shown to member") | n/a |
| 108 | Email `Change` | `settings.account.email` | — | `VZ-ACCOUNT-001`, `VZ-AUTH-002` (verification) | **M2** |
| 109 | Password `Change` | `settings.account.password` | — | `VZ-AUTH-002` (recovery), `VZ-SECURITY-003` (hashing) | **M2** |
| 110 | Passkeys `Manage` | `settings.security.passkeys` | — | **NO LEDGER ID** — zero occurrences of "passkey" or "WebAuthn". `VZ-AUTH-003` is TOTP only | n/a |
| 111 | `Authenticator app` toggle + `On` | `settings.2fa.enroll` | `settings.2fa.enroll` | `VZ-AUTH-003` — the existing control's action is "enroll/disable TOTP; view recovery codes", which a toggle cannot express | **M2** |
| 112 | `SMS backup` toggle | `settings.2fa.sms` | — | **NO LEDGER ID** — `VZ-AUTH-003` is TOTP + recovery codes; there is no SMS channel and `VZ-EMAIL-001` is the only delivery integration | n/a |
| 113 | Recovery codes `View` | `settings.2fa.recovery` | `settings.2fa.enroll` | `VZ-AUTH-003` | M2 |
| 114 | Apple `Disconnect` | `settings.connections.revoke` | — | `VZ-AUTH-006` (OAuth2 providers, `/settings/connections`) — but the provider list must come from what the **operator configured** ("owner enables providers from the admin UI"), never hard-coded | **M5** |
| 115 | Instagram `Disconnect` | same | — | `VZ-AUTH-006` only if the operator configures Instagram as an OAuth2 login provider. The card's subtitle "**and share to them**" implies cross-posting; the ledger's only cross-post target is Bluesky (`VZ-AT-001`) → **NO LEDGER ID for sharing to Instagram** | M5 / n/a |
| 116 | Google `Connect` | same | — | `VZ-AUTH-006` | **M5** |
| 117 | Adobe Creative Cloud `Connect` (`Import edits from Lightroom`) | — | — | **NO LEDGER ID** — this is neither a login provider nor a listed import. `VZ-IMPORT-001/002/003` are filesystem, Chevereto and Flickr only | n/a |
| — | missing provider | `settings.connections.atproto` | — | `VZ-AUTH-007` (sign in with an AT Protocol identity) is in the ledger and absent from the mockup | **M6** |
| 118 | Session rows ×3 | `settings.sessions.list` | — | `VZ-AUTH-001` ("sessions are server-side revocable"). The displayed city/country is IP geolocation; `VZ-OPS-005` forbids logging full IPs and requires "privacy-safe fields" — the precision of this display needs an owner decision | **M1** |
| 119 | `Sign out` ×2 | `settings.sessions.revoke` | — | `VZ-AUTH-001` | **M1** |
| 120 | `Sign out of all` | `settings.sessions.revoke_all` | — | `VZ-AUTH-001` ("signs out everywhere") | **M1** |
| 121 | `Request export` | `settings.account.export` | — | `VZ-ACCOUNT-002` | **M3** |
| 122 | `Deactivate` | `settings.account.deactivate` | — | **NO LEDGER ID** — `VZ-ACCOUNT-002` covers export and **deletion**; `VZ-ADMIN-USERS-001` has operator-initiated suspend/restore. Self-deactivation ("temporarily hide your profile") exists nowhere | n/a |
| 123 | `Delete` | `settings.account.delete` | `settings.account.delete` | `VZ-ACCOUNT-002` — the existing control requires re-authentication; none is drawn | **M3** |
| — | **Ledger surfaces this page omits** | — | — | API keys and ShareX snippet (`VZ-AUTH-008`, `/settings/api`); storage quota (`VZ-QUOTA-001`, `/settings/storage`); share grants (`VZ-ALBUM-002`, `/settings/shares`); federation opt-out (`VZ-AP-001`, `/settings/federation`); language and timezone (`VZ-ACCOUNT-001`) | — |

### f.8 `Notifications.html` (124–142)

| # | Control | Proposed action ID | Existing | Ledger ID(s) | Milestone |
|---|---|---|---|---|---|
| — | **`Push` channel column (7 checkboxes)** | `settings.notifications.push` | — | **NO LEDGER ID** — `VZ-NOTIFY-001` defines **in-app** (badge, panel, history) and **email per type**; `VZ-ACCOUNT-004` repeats "in-app/email". There is no web-push or mobile-push obligation anywhere in the ledger, and no mobile app | n/a |
| 124 | `New follower` (3 channels) | `settings.notifications.follow` | — | `VZ-NOTIFY-001`, `VZ-FOLLOW-001`, `VZ-ACCOUNT-004` | **M2** |
| 125 | `Favorites on your photos` | `settings.notifications.favorite` | — | `VZ-NOTIFY-001`, `VZ-FAVORITE-001` ("creator notification") | **M2** |
| 126 | `Comments and replies` | `settings.notifications.comment` | — | `VZ-NOTIFY-001`, `VZ-COMMENT-001` | **M2** |
| 127 | `Mentions` | `settings.notifications.mention` | — | `VZ-NOTIFY-001` ("mention") | **M2** |
| 128 | `Featured in a collection` (`A curator adds you to a collection.`) | `settings.notifications.gallery` | — | The described behaviour — a *curator* adding *your* photo to *their* set — is `VZ-GALLERY-001` (curated sets of **other members'** public safe photos with creator opt-out), **not** `VZ-COLLECTION-001` (a member's tree of **their own** albums). The label is wrong for both | **M5** |
| 129 | `Weekly digest` | `settings.notifications.digest` | — | **NO LEDGER ID** — no digest/batched-summary notification exists (`VZ-NOTIFY-001` is per-event). Row 125's own sub-line "Batched daily" is the same gap | n/a |
| 130 | `Product announcements` | `settings.notifications.newsletter` | — | `VZ-ACCOUNT-004` ("newsletter opt-in field exists for owner exports") | **M2** |
| 131 | `Pause push notifications` | `settings.notifications.quiet_hours` | — | **NO LEDGER ID** — zero occurrences of quiet hours / do-not-disturb; and it governs a channel that itself has no ledger ID | n/a |
| 132, 133 | `From` / `Until` | same | — | **NO LEDGER ID** | n/a |
| 134 | `Profile visibility` `Public / Signed-in / Private` | `settings.privacy.profile` | — | `VZ-ACCOUNT-001` ("private profile hides content from non-followers/anonymous") covers Public/Private. **`Signed-in` is site privacy mode**, which `VZ-PRIVACY-001` and `VZ-ADMIN-003` make an **owner** setting, not a member one → **CONFLICT of ownership** | M2 / M5 |
| 135 | `Who can message you` | `settings.privacy.messages` | — | `VZ-MESSAGE-001` (private one-to-one messages) | **M5** |
| 136 | `Show me in search engines` | `settings.privacy.indexing` | — | `VZ-SEO-001` (sitemaps/robots for public pages) and `VZ-PRIVACY-002` (hide from public search/explore). `VZ-PRIVACY-002` is per-item or a default, not a profile-level switch | **M5** |
| 137 | `Hide EXIF from viewers by default` | `settings.privacy.defaults` | `settings.privacy.defaults` | `VZ-MEDIA-004` | **M1** |
| 138 | `Hide precise location` | `settings.privacy.geo` | — | `VZ-GEO-001` ("geo-privacy… separate from photo privacy", geofences) | **M5** |
| 139 | `Allow AI training on public photos` | — | — | **NO LEDGER ID** — zero occurrences. Also internally contradictory (A16) | n/a |
| 140 | `Blocked accounts` `Manage` | `settings.blocks.manage` | `profile.block` (the act, not the list) | `VZ-BLOCK-001` (`/settings/blocks`) | **M2** |
| 141 | `Muted tags` `Manage` | `settings.mutes.manage` | — | **NO LEDGER ID** — zero occurrences of mute. Nearest: `VZ-NSFW-001` (viewer-side safety filter) and `VZ-SECURITY-001` (stop words, admin-owned). A member-level tag mute is a new capability | n/a |
| 142 | `Comment filter` `Off / Standard / Strict` | `settings.content.comment_filter` | — | `VZ-COMMENT-001` (owner controls), `VZ-SPAM-001` (anti-abuse thresholds), `VZ-SERVICES-002` (Akismet/StopForumSpam — operator-configured). The three levels are undefined and the ledger places this filtering with the operator, not the member → **partial: NO LEDGER ID for a per-member three-level filter** | M2 / M5 / n/a |
| — | **Ledger preferences this page omits** | — | — | moderation-outcome and group-activity notifications, and the separated moderation-duty queue for admins (`VZ-NOTIFY-001`); rating notifications (`VZ-RATING-001`); default visibility for new uploads, default download permission, default comment permission (`settings.privacy.defaults`, `VZ-PRIVACY-001`, `VZ-DOWNLOAD-001`); viewer safety-level display preference (`VZ-NSFW-001`, `/settings/content`); follow-request handling (`VZ-FOLLOW-002`); named audiences (`VZ-PRIVACY-004`); **and the notification centre itself** — `VZ-NOTIFY-001` requires a bell panel and a `/notifications` history, neither of which has a mockup | — |

### f.9 `Photo Insights.html` (143–153)

**The whole page is `VZ-STATS-002` — full profile, M6**, and it depends on `VZ-ANALYTICS-001`
(ClickHouse) or on bounded PostgreSQL rollups when analytics is off.

| # | Control | Proposed action ID | Ledger ID(s) | Milestone |
|---|---|---|---|---|
| 143 | `7d / 30d / 90d / 1y` | `stats.range.set` | `VZ-STATS-002` | **M6** |
| 144 | `Export CSV` | `stats.export.csv` | `VZ-STATS-002` ("downloadable CSV") | **M6** |
| 145 | KPI `Views` | `stats.kpi.views` | `VZ-STATS-002`; the bare count is `VZ-STATS-001`; "impression vs view" is Q-020, decided 2026-09-15 | M3 / **M6** |
| 146 | KPI `Favorites` | `stats.kpi.favorites` | `VZ-FAVORITE-001`, `VZ-STATS-002` | M2 / **M6** |
| 147 | KPI `New followers` | `stats.kpi.followers` | `VZ-FOLLOW-001`, `VZ-STATS-002` | M2 / **M6** |
| 148 | KPI `Engagement rate` `6.9%` / `−0.3 pp` | — | **NO LEDGER ID** — `VZ-STATS-002` enumerates "daily views/favorites/comments, top items, referrer classes". No engagement-rate metric is defined; `VZ-EXPLORE-003` uses "engagement quality" as a **ranking input**, not a member-facing figure | n/a |
| 149 | Views-over-time chart | `stats.chart.timeseries` | `VZ-STATS-002` ("views/favorites/comments over time") — **comments series missing** | **M6** |
| 150 | Top photos ×5 | `stats.top_items` | `VZ-STATS-002` ("top items") | **M6** |
| 151 | `View all photos` | `shell.side.library` | `VZ-LIBRARY-001` | M1 |
| 152 | Traffic sources ×5 | `stats.sources` | `VZ-STATS-002` ("sources… referrer classes"). **The bars are drawn at widths that contradict their labels (A13)** | **M6** |
| 153 | Audience locations ×6 | `stats.geo` | **NO LEDGER ID** — no geographic audience breakdown exists in `VZ-STATS-002`. It is also a privacy decision: `VZ-OPS-005` requires privacy-safe fields and `VZ-ANALYTICS-001` requires "privacy minimization"; deriving per-country viewer counts on a self-hosted instance needs an owner decision, not a mockup | n/a |
| — | **Ledger content this page omits** | — | per-**item** statistics (`VZ-STATS-002` is "per-item **and** per-account"); comments over time; the honest degraded state when analytics is OFF | — |

---

## g. Summaries

### g.1 Controls with **NO LEDGER ID**

1. **Plan / subscription card and `Manage`** — #107. Contradicts the product charter (see g.2).
2. **Drafts as an asset state** — #22, #28 (`draft` status), #45 (`Save as draft`), #51b
   (`Drafts 22` filter), #58 (`Draft` badge). Five controls across two pages resting on one
   non-existent concept.
3. **Scheduled publishing** — #46.
4. **Passkeys / WebAuthn** — #110.
5. **SMS second factor** — #112.
6. **Self-deactivation** — #122.
7. **Adobe Creative Cloud / Lightroom import** — #117; and **sharing to Instagram** — #115.
8. **Push as a notification channel** — the entire `Push` column (7 checkboxes) — plus
   **quiet hours** built on it — #131–133.
9. **Weekly digest / batched notifications** — #129 (and row 125's "Batched daily").
10. **Muted tags** — #141; and a **per-member three-level comment filter** — #142.
11. **AI-training opt-out** — #139.
12. **Profile tagline** — #96, **profile location** — #98, **pronouns** — #99,
    **typed multi-link list** — #100–103.
13. **Commission availability, booking note, "open to"** — #104–106.
14. **Engagement rate** — #148, and **audience geography** — #153.
15. **View-density switcher as a viewer control** — #53–54 (identical finding to the Search page).
16. **`Most favorited` as a library sort key** — #52; **`Published/Drafts` as a filter axis** — #51a.
17. **Field length limits** (80 / 500 / 500 characters, "up to 5 links", "up to 50 files,
    100 MB each") — no ledger entry fixes any of these numbers.
18. **Album ⋯ menu contents** — #71, undrawn.

### g.2 Controls that **contradict** a ledger entry

| Control | Contradiction |
|---|---|
| Plan card `goimg Pro` (#107) | `docs/PRODUCT_SPEC.md` §1 and `docs/PRODUCT_CHARTER.md`: **Vizra has no billing**; `VZ-NSFW-001` "ungated by billing"; `VZ-EXPLORE-003` "no billing bias" |
| `RAW` format chip + three `.RAF` queue files + `DSCF8821.RAF` preview (#25) | `VZ-MEDIA-002`: "**RAW is declined** unless the owner adds it" |
| `TIFF` format chip (#25) | `VZ-MEDIA-002` provenance: "no HEIC/**TIFF**/SVG" |
| `HEIC` format chip (#25) | `VZ-MEDIA-010`: full profile, config-gated, **OFF by default** |
| `Safe for all audiences` binary toggle (#43) | `VZ-NSFW-001`: three levels (safe/moderate/restricted), explicitly an improvement on Chevereto's binary flag |
| `Allow downloads` binary toggle (#85) | `VZ-DOWNLOAD-001`: nobody / followers / members / anyone + size picker |
| Visibility `Public / Followers / Private` (#40, #82) and library filter `All / Published / Drafts / Private` (#51) | `VZ-PRIVACY-001`: public / **unlisted** / private — the core M1 triad. `Followers` is `VZ-PRIVACY-004`, full profile, M5 |
| Album `<select>` (#35, #77) | `VZ-ALBUM-001`: many-to-many membership |
| Flat album grid (`My Albums.html`) | `VZ-ALBUM-001`: nested sub-albums |
| Album privacy filter without `password` (#66) | `VZ-ALBUM-002`: public / private / link-only / **password** |
| Photo card → `Edit Photo.html` (#55) | `ui-controls.json` `library.grid.item`: "open **in viewer**" |
| `Profile visibility: Signed-in` (#134) | `VZ-PRIVACY-001` / `VZ-ADMIN-003`: site privacy mode is an **owner** setting |
| `Featured in a collection` (#128) | Describes `VZ-GALLERY-001` behaviour under the `VZ-COLLECTION-001` name |
| Hard-coded `goimg.com/` username prefix (#95) | Self-hosted instance URL is `VZ-ADMIN-003` configuration |
| Traffic-source bar widths (#152) | `AGENTS.md` "Do not fabricate outputs"; `DESIGN_BRIEF.md` "Reject fake metrics" |
| `Allow AI training` title vs its own help text (#139) | Internally contradictory; unimplementable as drawn |
| `Changes apply instantly` beside Cancel/Save (`Edit Photo.html`) | Two persistence models |

### g.3 Controls whose backend lands after the page's own milestone

- **`Upload Studio.html`** is drawn as a complete M3 surface (`VZ-UPLOAD-006` option set,
  `VZ-TAG-001`, `VZ-UPLOAD-002` progress) with M5 additions (`VZ-LICENSE-001`, `VZ-GEO-001`,
  `VZ-PRIVACY-004`), while the golden path needs only `VZ-UPLOAD-001` + `VZ-UPLOAD-003` at M1.
  The M1 subset of this page is: drop zone, file picker, queue, real progress with cancel/retry,
  visibility (public/unlisted/private), Show EXIF, Publish.
- **`Edit Photo.html`** is `VZ-LIBRARY-002` = **M3**, with `VZ-LICENSE-001` and `VZ-GEO-001` at M5
  and `VZ-DOWNLOAD-001` at M3. Its only M1 elements are visibility and the EXIF display.
- **`Edit Profile.html`** is `VZ-ACCOUNT-001` = **M2** minus five fields that have no ledger ID.
- **`Account Settings.html`** spans M1 (sessions), M2 (email, password, 2FA), M3 (export, delete)
  and M5 (OAuth providers) in one undifferentiated page; two of its cards and three of its rows
  have no ledger ID at all.
- **`Notifications.html`** spans M1 (`VZ-MEDIA-004` default), M2 (notification preferences, blocks)
  and M5 (`VZ-MESSAGE-001`, `VZ-GEO-001`, `VZ-PRIVACY-002`), with one whole column (`Push`) and
  four rows that have no ledger ID.
- **`Photo Insights.html`** is entirely **M6** (`VZ-STATS-002`, full profile, ClickHouse-dependent),
  yet it is a first-class sidebar and mobile-tab destination on every page of the set.
- **`My Photos.html`** and **`My Albums.html`** are the two pages that sit closest to M1, and they
  are the two that most need the states the mockups omit: empty, loading, error, confirmation.

### g.4 Ledger surfaces this eight-page set does not cover at all

Recorded here as a pointer; enumerated with milestones and closest visual relatives in
`docs/design/claude-design/GAPS.md`.

Owner claim and first-run setup; sign-in, sign-up, email verification, password reset; **the photo
page and lightbox viewer** (`VZ-VIEWER-001`, the centre of the golden path); the album detail page;
the add-to-album dialog; the per-asset privacy dialog; the album privacy and share-grant dialog;
every destructive-confirmation dialog; the upload result/embed panel; the share dialog; the
download menu; the notification centre; the moderation queue and the entire admin console; API
keys; storage quota; tags and categories; and the unauthorized/not-found/session-expired states.

---

## Appendix — verification notes

- All line numbers are as-read on 2026-09-20 against the sha256 values in
  `docs/design/claude-design/README.md`. Re-verify with
  `shasum -a 256 docs/design/claude-design/*` before relying on a line reference.
- sRGB values and contrast ratios in §a.12 were computed from the OKLCH declarations
  (OKLab → linear sRGB → gamma encode → WCAG relative luminance), not sampled from a render. They
  should be re-confirmed against a real browser render before being cited as evidence, because
  `color-mix(in oklab, …)` and `backdrop-filter` compositing are browser-dependent.
- Control counts, `aria-` counts, `<svg>` counts, `alt=""` counts and the Unsplash hotlink count
  were taken by direct enumeration of the files; the three character-counter discrepancies in A14
  were computed from the literal string values in the markup.
- No control in these mockups is evidence of working behaviour. Every "handler" in the set is a CSS
  class toggle; there is no fetch, no state model and no data structure anywhere.
