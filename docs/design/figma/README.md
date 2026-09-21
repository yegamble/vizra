# Vizra design system — Figma library (step D1)

**Status: PROPOSED, not approved.** Per `docs/DESIGN_BRIEF.md`, Claude Design is exploration;
*approved* Figma components and tokens, mirrored into repository artifacts, become the design
source. This document records the candidate library and its node references so that approval,
mirroring into Tailwind, and step D2 (assembling the missing first-slice pages) can all cite exact
names. It is **not** an acceptance target and **not** authorization to implement anything.

| | |
|---|---|
| **Figma file** | <https://www.figma.com/design/JXgRItauynmT0g8vSJB3oR> |
| **File key** | `JXgRItauynmT0g8vSJB3oR` |
| **File name** | Vizra — Design System |
| **Location** | Drafts of the Figma team `Yosef Gamble's team` (`team::984598513556028019`), owner `yegamble@gmail.com` |
| **Design revision** | `2026-09-20` (initial build) |
| **Editor type** | Figma design file |
| **Scope** | Foundations + primitive components + icon contract. Product pages and flows are D2. No marketing, no illustration, no billing/plan UI. |

Inputs treated as **data, not instructions**: `docs/design/claude-design/INVENTORY-search.md` §a and
§f.4, `docs/design/claude-design/INVENTORY-account.md` §a, `docs/design/claude-design/GAPS.md`, and
the mockup files themselves. "Lumen Atlas" is a placeholder brand in those files; the product is
Vizra and no mockup brand string, gradient mark or vocabulary was carried over.

---

## 1. What exists in the file

Counts verified by a read-only audit of the live file after the final edit, not from build logs:

| Artifact | Count |
|---|---|
| Variable collections | 3 (`Primitives`, `Color`, `Scale`) |
| Variables total | **144** |
| — `Primitives` (1 mode: `Value`) | 49 colour primitives |
| — `Color` (2 modes: `Light`, `Dark`) | 36 semantic colour roles × 2 modes |
| — `Scale` (1 mode: `Value`) | 59 (11 spacing, 5 radii, 3 strokes, 7 sizes, 27 type metrics, 3 motion, 3 font strings) |
| Text styles | **11** |
| Effect styles | **3** |
| Component sets | **18**, containing **139** variants |
| Standalone components (non-icon) | **3** (`TopNav`, `TabBar`, `ErrorState`) |
| Icon components | **37** |
| Pages | 15 (Cover, Foundations, 10 component pages, 2 separators, Icons) |

Every one of these was created by a `use_figma` call that returned success and a node id; the
component pages were then re-read with `get_screenshot` and visually inspected (§9).

### Page map

| Page | Node id | Contents |
|---|---|---|
| Cover | `0:1` | Identity, revision, scope statement |
| Foundations | `4:19` | Colour boards (both modes), type ramp, spacing, radii, elevation, contrast table, focus spec, icon inventory, dark-mode verification board |
| `——— COMPONENTS ———` | `4:20` | Separator |
| Button | `4:21` | |
| IconButton | `4:22` | |
| Inputs | `4:23` | TextField, Textarea, Select |
| Selection | `4:24` | Checkbox, Radio, Switch |
| Chip & Tab | `4:25` | |
| PhotoCard | `4:26` | |
| Avatar | `4:27` | |
| Navigation | `4:28` | TabBar Item, TabBar, TopNav |
| Dialog | `4:29` | |
| Feedback | `4:30` | Toast/Inline status, Banner, Skeleton, EmptyState, ErrorState |
| `——— REFERENCE ———` | `4:31` | Separator |
| Icons | `4:32` | 37 Lucide components |

---

## 2. Variable collections and modes

### 2.1 `Primitives` — collection `VariableCollectionId:2:2`, mode `Value` (`2:0`)

Raw ramp values only. `scopes = []` so they never appear in a property picker; components must
never bind to them directly. Every value is **chroma-clamped into sRGB**, so the recorded OKLCH
specification and the shipped hex agree exactly (no silent gamut clipping).

| Primitive | OKLCH | sRGB |
|---|---|---|
| `amber/300` | `oklch(0.8 0.14 80)` | `#edb345` |
| `amber/50` | `oklch(0.96 0.0367 80)` | `#fff0d7` |
| `amber/500` | `oklch(0.54 0.11 80)` | `#906606` |
| `amber/600` | `oklch(0.48 0.0994 80)` | `#7b5600` |
| `amber/700` | `oklch(0.42 0.087 80)` | `#664700` |
| `amber/d-soft` | `oklch(0.3 0.055 80)` | `#3c2a07` |
| `blue/50` | `oklch(0.95 0.0243 255)` | `#e4f0ff` |
| `blue/100` | `oklch(0.9 0.0494 255)` | `#c9e0ff` |
| `blue/200` | `oklch(0.78 0.112 255)` | `#86bafe` |
| `blue/300` | `oklch(0.72 0.14 255)` | `#65a7fa` |
| `blue/400` | `oklch(0.68 0.15 255)` | `#539af2` |
| `blue/500` | `oklch(0.55 0.18 255)` | `#026fd7` |
| `blue/600` | `oklch(0.48 0.1581 255)` | `#005bb4` |
| `blue/700` | `oklch(0.42 0.1384 255)` | `#004b96` |
| `blue/800` | `oklch(0.36 0.1334 258)` | `#003981` |
| `blue/900` | `oklch(0.3 0.1112 258)` | `#002a64` |
| `blue/d-soft` | `oklch(0.3 0.07 255)` | `#132e50` |
| `green/50` | `oklch(0.95 0.045 150)` | `#daf8df` |
| `green/300` | `oklch(0.74 0.15 150)` | `#5ac576` |
| `green/500` | `oklch(0.52 0.14 150)` | `#0a7e3a` |
| `green/600` | `oklch(0.46 0.1267 150)` | `#006b2e` |
| `green/700` | `oklch(0.4 0.11 150)` | `#005725` |
| `green/d-soft` | `oklch(0.3 0.06 150)` | `#14361d` |
| `neutral/0` | `oklch(1.0 0.0 260)` | `#ffffff` |
| `neutral/25` | `oklch(0.985 0.003 250)` | `#f9fafc` |
| `neutral/50` | `oklch(0.96 0.004 250)` | `#f0f2f4` |
| `neutral/100` | `oklch(0.9 0.006 260)` | `#dcdee2` |
| `neutral/200` | `oklch(0.82 0.008 260)` | `#c1c4c9` |
| `neutral/300` | `oklch(0.7 0.01 260)` | `#9b9fa5` |
| `neutral/400` | `oklch(0.62 0.01 260)` | `#83868c` |
| `neutral/500` | `oklch(0.52 0.01 260)` | `#66696f` |
| `neutral/600` | `oklch(0.38 0.012 260)` | `#3f4349` |
| `neutral/700` | `oklch(0.27 0.013 265)` | `#23262d` |
| `neutral/750` | `oklch(0.22 0.013 265)` | `#181b21` |
| `neutral/800` | `oklch(0.18 0.015 260)` | `#0e1218` |
| `neutral/850` | `oklch(0.17 0.012 265)` | `#0d0f15` |
| `neutral/900` | `oklch(0.13 0.012 265)` | `#05070c` |
| `neutral/d-ink` | `oklch(0.97 0.004 265)` | `#f4f5f8` |
| `neutral/d-ink-2` | `oklch(0.84 0.008 265)` | `#c8cad0` |
| `neutral/d-ink-3` | `oklch(0.68 0.012 265)` | `#9598a0` |
| `neutral/d-line` | `oklch(0.56 0.012 265)` | `#71747c` |
| `neutral/d-line-2` | `oklch(0.33 0.012 265)` | `#32353c` |
| `red/50` | `oklch(0.95 0.025 25)` | `#ffe8e6` |
| `red/200` | `oklch(0.78 0.128 25)` | `#ff958e` |
| `red/300` | `oklch(0.7 0.17 25)` | `#f66d67` |
| `red/500` | `oklch(0.55 0.21 25)` | `#d01c29` |
| `red/600` | `oklch(0.48 0.19 25)` | `#b00a1d` |
| `red/700` | `oklch(0.4 0.16 25)` | `#8a0314` |
| `red/d-soft` | `oklch(0.3 0.07 25)` | `#4b1d1b` |

### 2.2 `Color` — collection `VariableCollectionId:2:51`, modes `Light` (`2:1`) and `Dark` (`2:2`)

Semantic roles. Every entry except the four alpha-carrying tokens is an **alias** to a primitive —
no raw value is duplicated in the semantic layer. Web code syntax is set on every variable as
`var(--vz-<name>)`, so `color/ink-2` mirrors to `--vz-ink-2` in Tailwind.

`Light` is mode index 0 and is therefore the default a node resolves with no explicit mode.

| Token | Light → | Light hex | Light OKLCH | Dark → | Dark hex | Dark OKLCH |
|---|---|---|---|---|---|---|
| `color/bg` | `neutral/25` | `#f9fafc` | `oklch(0.985 0.003 250)` | `neutral/850` | `#0d0f15` | `oklch(0.17 0.012 265)` |
| `color/bg-elevated` | `neutral/0` | `#ffffff` | `oklch(1.0 0.0 260)` | `neutral/750` | `#181b21` | `oklch(0.22 0.013 265)` |
| `color/bg-tint` | `neutral/50` | `#f0f2f4` | `oklch(0.96 0.004 250)` | `neutral/700` | `#23262d` | `oklch(0.27 0.013 265)` |
| `color/ink` | `neutral/800` | `#0e1218` | `oklch(0.18 0.015 260)` | `neutral/d-ink` | `#f4f5f8` | `oklch(0.97 0.004 265)` |
| `color/ink-2` | `neutral/600` | `#3f4349` | `oklch(0.38 0.012 260)` | `neutral/d-ink-2` | `#c8cad0` | `oklch(0.84 0.008 265)` |
| `color/ink-3` | `neutral/500` | `#66696f` | `oklch(0.52 0.01 260)` | `neutral/d-ink-3` | `#9598a0` | `oklch(0.68 0.012 265)` |
| `color/line` | `neutral/400` | `#83868c` | `oklch(0.62 0.01 260)` | `neutral/d-line` | `#71747c` | `oklch(0.56 0.012 265)` |
| `color/line-2` | `neutral/100` | `#dcdee2` | `oklch(0.9 0.006 260)` | `neutral/d-line-2` | `#32353c` | `oklch(0.33 0.012 265)` |
| `color/accent` | `blue/500` | `#026fd7` | `oklch(0.55 0.18 255)` | `blue/300` | `#65a7fa` | `oklch(0.72 0.14 255)` |
| `color/accent-hover` | `blue/600` | `#005bb4` | `oklch(0.48 0.1581 255)` | `blue/200` | `#86bafe` | `oklch(0.78 0.112 255)` |
| `color/accent-pressed` | `blue/700` | `#004b96` | `oklch(0.42 0.1384 255)` | `blue/400` | `#539af2` | `oklch(0.68 0.15 255)` |
| `color/accent-soft` | `blue/50` | `#e4f0ff` | `oklch(0.95 0.0243 255)` | `blue/d-soft` | `#132e50` | `oklch(0.3 0.07 255)` |
| `color/accent-ink` | `blue/800` | `#003981` | `oklch(0.36 0.1334 258)` | `blue/300` | `#65a7fa` | `oklch(0.72 0.14 255)` |
| `color/on-accent` | `neutral/0` | `#ffffff` | `oklch(1.0 0.0 260)` | `neutral/900` | `#05070c` | `oklch(0.13 0.012 265)` |
| `color/danger` | `red/500` | `#d01c29` | `oklch(0.55 0.21 25)` | `red/300` | `#f66d67` | `oklch(0.7 0.17 25)` |
| `color/danger-hover` | `red/600` | `#b00a1d` | `oklch(0.48 0.19 25)` | `red/200` | `#ff958e` | `oklch(0.78 0.128 25)` |
| `color/danger-pressed` | `red/700` | `#8a0314` | `oklch(0.4 0.16 25)` | `red/300` | `#f66d67` | `oklch(0.7 0.17 25)` |
| `color/danger-soft` | `red/50` | `#ffe8e6` | `oklch(0.95 0.025 25)` | `red/d-soft` | `#4b1d1b` | `oklch(0.3 0.07 25)` |
| `color/danger-ink` | `red/700` | `#8a0314` | `oklch(0.4 0.16 25)` | `red/300` | `#f66d67` | `oklch(0.7 0.17 25)` |
| `color/on-danger` | `neutral/0` | `#ffffff` | `oklch(1.0 0.0 260)` | `neutral/900` | `#05070c` | `oklch(0.13 0.012 265)` |
| `color/success` | `green/500` | `#0a7e3a` | `oklch(0.52 0.14 150)` | `green/300` | `#5ac576` | `oklch(0.74 0.15 150)` |
| `color/success-soft` | `green/50` | `#daf8df` | `oklch(0.95 0.045 150)` | `green/d-soft` | `#14361d` | `oklch(0.3 0.06 150)` |
| `color/success-ink` | `green/700` | `#005725` | `oklch(0.4 0.11 150)` | `green/300` | `#5ac576` | `oklch(0.74 0.15 150)` |
| `color/on-success` | `neutral/0` | `#ffffff` | `oklch(1.0 0.0 260)` | `neutral/900` | `#05070c` | `oklch(0.13 0.012 265)` |
| `color/warn` | `amber/500` | `#906606` | `oklch(0.54 0.11 80)` | `amber/300` | `#edb345` | `oklch(0.8 0.14 80)` |
| `color/warn-soft` | `amber/50` | `#fff0d7` | `oklch(0.96 0.0367 80)` | `amber/d-soft` | `#3c2a07` | `oklch(0.3 0.055 80)` |
| `color/warn-ink` | `amber/700` | `#664700` | `oklch(0.42 0.087 80)` | `amber/300` | `#edb345` | `oklch(0.8 0.14 80)` |
| `color/on-warn` | `neutral/0` | `#ffffff` | `oklch(1.0 0.0 260)` | `neutral/900` | `#05070c` | `oklch(0.13 0.012 265)` |
| `color/focus-ring` | `blue/600` | `#005bb4` | `oklch(0.48 0.1581 255)` | `blue/300` | `#65a7fa` | `oklch(0.72 0.14 255)` |

Four tokens carry alpha and are therefore **raw per mode**, not aliases:

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `color/scrim` | `neutral/800` @ 55% | `neutral/900` @ 72% | Modal/dialog backdrop |
| `color/bg-frost` | `#ffffff` @ 92% | `#181b21` @ 92% | Sticky top bar and tab bar, with `backdrop-filter: blur(20px)` |
| `color/on-media-scrim` | `neutral/900` @ 88% | `neutral/900` @ 88% | Chip behind controls that sit on a photograph. **Theme-invariant** |
| `color/on-media` | `#ffffff` | `#ffffff` | Ink for controls on a photograph. **Theme-invariant** |

Plus three mode-aware shadow colours used only by effect styles:
`color/shadow-1` (light `neutral/800` @ 6%, dark `#000` @ 40%), `color/shadow-2` (14% / 52%),
`color/shadow-3` (22% / 64%). Dark-mode shadow is authored heavier because a soft shadow is
invisible on a dark surface.

### 2.3 `Scale` — collection `VariableCollectionId:3:2`, mode `Value` (`3:0`)

| Group | Tokens |
|---|---|
| Spacing (4px grid) | `space/0` 0, `space/1` 4, `space/2` 8, `space/3` 12, `space/4` 16, `space/5` 20, `space/6` 24, `space/8` 32, `space/10` 40, `space/12` 48, `space/16` 64 |
| Radii (5) | `radius/sm` 8, `radius/md` 12, `radius/lg` 16, `radius/xl` 24, `radius/full` 999 |
| Strokes | `stroke/hairline` 1, `stroke/regular` 1.5, `stroke/focus` 2 |
| Sizes | `size/control-sm` 32, `size/control` 40, `size/control-lg` 48, `size/touch-min` 44, `size/icon-sm` 16, `size/icon` 20, `size/icon-lg` 24 |
| Type metrics | `type/<step>/size`, `type/<step>/line-height`, `type/<step>/tracking` for the 9 steps below |
| Motion | `motion/fast` 120, `motion/base` 180, `motion/slow` 240 (ms) |
| Font stacks (STRING) | `font/sans`, `font/mono`, `font/figma-proxy` |

`font/sans` = `system-ui, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", Arial, sans-serif`
`font/mono` = `ui-monospace, "Cascadia Mono", "Segoe UI Mono", "Roboto Mono", "DejaVu Sans Mono", monospace`
`font/figma-proxy` = `Inter`

No Apple font is named in either stack. These three are `scopes = []` and must **not** be bound to
a Figma `fontFamily` — a CSS stack is not a loadable Figma family. See §10 for the consequence.

---

## 3. Scale tables

### 3.1 Type ramp — 9 steps (+ mono + wordmark)

| Text style | Size / line-height | Tracking | Weight | Use |
|---|---|---|---|---|
| `text/Display` | 32 / 38 | −2% | Semi Bold | Page title, one per page |
| `text/Title 1` | 24 / 30 | −1.5% | Semi Bold | Section title, dialog title |
| `text/Title 2` | 20 / 26 | −1% | Semi Bold | Card title, sheet title |
| `text/Title 3` | 17 / 24 | −1% | Semi Bold | Sub-section, list group heading |
| `text/Body` | 15 / 22 | −0.3% | Regular | Default running text |
| `text/Body Strong` | 15 / 22 | −0.3% | Semi Bold | Emphasis; list-row accessible name |
| `text/Label` | 13 / 18 | 0 | Medium | Buttons, chips, tabs, form labels |
| `text/Caption` | 12 / 16 | 0 | Regular | Metadata, counts, helper and error text |
| `text/Overline` | 11 / 14 | +8% | Semi Bold | Section eyebrow — **author sets caps; no CSS transform in Figma** |
| `text/Mono` | 13 / 18 | 0 | Roboto Mono Regular | EXIF, IDs, claim tokens, API keys |
| `brand/Wordmark (placeholder)` | 20 / 24 | −2% | Semi Bold | The string "Vizra" only — **not a logo** |

Every one of the 9 ramp styles has `fontSize`, `lineHeight` and `letterSpacing` bound to the
matching `type/*` variable, so a ramp change is a variable edit, not a style edit.

### 3.2 Spacing, radii, elevation

Spacing and radii are listed in §2.3. Elevation:

| Effect style | Recipe | Use |
|---|---|---|
| `elevation/1` | `0 1px 2px` + `0 1px 3px −1px` of `color/shadow-1` | Raised card, photo card, sticky bar. The only shadow allowed over a photograph |
| `elevation/2` | `0 2px 6px` + `0 8px 24px −12px` of `color/shadow-2` | Popover, menu, toast |
| `elevation/3` | `0 8px 16px −10px` + `0 24px 48px −16px` of `color/shadow-3` | Dialog, bottom sheet, lightbox chrome |

---

## 4. Contrast — measured, before and after

"Before" is the mockup set as measured in `INVENTORY-search.md` §f.4 and `INVENTORY-account.md` §a.2
(OKLab → linear sRGB → relative luminance; my recomputation reproduced their published figures
exactly, e.g. `--accent` `oklch(0.58 0.18 255)` → `#1779e1`, luminance 0.1917). The mockups have **no
dark mode at all**, so every dark figure is new work rather than a correction.

**37 audited pairs, 0 failures, in both modes.**

| Pair | Min | Before (mockup) | After — Light | After — Dark | Result |
|---|---|---|---|---|---|
| `ink` on `bg` | 4.5 | 18.02 | 18.02 | 17.53 | kept |
| `ink` on `bg-elevated` | 4.5 | 18.81 | 18.81 | 15.88 | kept |
| `ink` on `bg-tint` | 4.5 | 16.75 | 16.75 | 13.82 | kept |
| `ink` on `accent-soft` | 4.5 | 16.16 | 16.27 | 12.53 | kept |
| `ink-2` on `bg` | 4.5 | 9.59 | 9.59 | 11.71 | kept |
| `ink-2` on `bg-elevated` | 4.5 | 10.01 | 10.01 | 10.60 | kept |
| `ink-2` on `bg-tint` | 4.5 | 8.91 | 8.91 | 9.23 | kept |
| **`ink-3` on `bg`** | 4.5 | **4.46 FAIL** | **5.28** | 6.64 | fixed |
| **`ink-3` on `bg-tint`** | 4.5 | **4.14 FAIL** | **4.90** | 5.23 | fixed |
| `ink-3` on `bg-elevated` | 4.5 | 4.65 | 5.51 | 6.01 | raised |
| **`ink-3` on `accent-soft`** | 4.5 | **4.00 FAIL** | **4.76** | 4.74 | fixed |
| **`accent` as link text on `bg`** | 4.5 | **4.16 FAIL** | **4.72** | 7.70 | fixed |
| **`accent` as link text on `bg-elevated`** | 4.5 | **4.34 FAIL** | **4.93** | 6.97 | fixed |
| **`on-accent` on `accent` (rest)** | 4.5 | **4.34 FAIL** | **4.93** | 8.10 | fixed |
| `on-accent` on `accent-hover` | 4.5 | not designed | 6.63 | 10.07 | new |
| `on-accent` on `accent-pressed` | 4.5 | not designed | 8.57 | 6.96 | new |
| `accent-ink` on `accent-soft` | 4.5 | 9.50 | 9.58 | 5.50 | kept |
| **`line` on `bg` (input, unchecked box)** | 3.0 | **1.29 FAIL** | **3.49** | 4.11 | fixed |
| **`line` on `bg-elevated`** | 3.0 | **1.35 FAIL** | **3.64** | 3.72 | fixed |
| **`line` on `bg-tint`** | 3.0 | **1.20 FAIL** | **3.24** | 3.24 | fixed |
| **focus ring vs page** | 3.0 | **1.28 FAIL** | **6.36** | 7.70 | fixed |
| `danger` as text on `bg` | 4.5 | 4.68 | 5.18 | 6.64 | raised |
| `danger` as text on `bg-elevated` | 4.5 | 4.88 | 5.41 | 6.01 | raised |
| `on-danger` on `danger` | 4.5 | 4.88 | 5.41 | 6.98 | raised |
| `on-danger` on `danger-hover` | 4.5 | not designed | 7.23 | 9.55 | new |
| `danger-ink` on `danger-soft` | 4.5 | not designed | 8.57 | 4.87 | new |
| **`success` as text on `bg`** | 4.5 | **2.79 FAIL** | **4.95** | 8.80 | fixed |
| **`success` as text on `bg-elevated`** | 4.5 | **2.91 FAIL** | **5.17** | 7.96 | fixed |
| **`on-success` on `success`** | 4.5 | **2.91 FAIL** | **5.17** | 9.25 | fixed |
| `success-ink` on `success-soft` | 4.5 | not designed | 7.69 | 6.13 | new |
| **`warn` as text on `bg`** | 4.5 | **2.09 FAIL** | **4.92** | 10.10 | fixed |
| **`warn` as text on `bg-elevated`** | 4.5 | **2.18 FAIL** | **5.13** | 9.14 | fixed |
| **`on-warn` on `warn`** | 4.5 | **2.18 FAIL** | **5.13** | 10.62 | fixed |
| `warn-ink` on `warn-soft` | 4.5 | not designed | 7.61 | 7.24 | new |
| `success` / `danger` / `warn` as graphic on `bg` | 3.0 | 2.09–4.68 | 4.92–5.18 | 6.64–10.10 | fixed |
| **`on-media` over ANY photograph (worst case)** | 4.5 | **unmeasurable** | **15.3** | 15.3 | fixed |
| **`ink-3` through the frosted bar (worst case)** | 4.5 | **unmeasurable** | **4.60** | 4.80 | fixed |
| `line-2` (decorative dividers only) | n/a | 1.19 | 1.35 | 1.40 | no requirement |

Notes on the two "unmeasurable" rows, which are the ones that matter most for a photo product:

- **On-media.** The mockups put white 11–14px text and `rgba(255,255,255,.22)` + blur control chips
  directly over photographs. Contrast was image-dependent and could not be certified.
  `color/on-media-scrim` is `neutral/900` at **88%**, so the worst possible backing (a pure-white
  photograph) composites to `#22252a` and white text on it is **15.3:1**; over a black photograph it
  is 20.2:1. Lowering the alpha weakens this guarantee — 86% still gives 14.4:1, below that it was
  not evaluated.
- **Frosted bar.** `color/bg-frost` is 92%, and 92% is a **measured floor, not a taste**: at 90% the
  worst case (`ink-3` with a black photograph scrolling beneath, light mode) is **4.39:1 and fails**;
  at 92% it is 4.60:1 light and 4.80:1 dark. Do not lower it.

A status colour satisfies both the 3:1 graphic floor and the 4.5:1 text floor with **one** token
rather than a graphic/text pair, because every one is ≥ 4.5:1 on `color/bg` in both modes.

### Focus-visible

One rule for every interactive component:

```css
outline: 2px solid var(--vz-focus-ring);
outline-offset: 2px;
```

The offset is load-bearing. The ring is measured against the **page** (6.36:1 light, 7.70:1 dark),
not against the control it surrounds — a ring drawn directly on an accent-filled button would be
1.35:1. On a photograph it becomes a dual ring instead:

```css
box-shadow: 0 0 0 2px var(--vz-on-media-scrim), 0 0 0 4px var(--vz-on-media);
```

In Figma this is modelled as a 2px `color/focus-ring` stroke with `strokeAlign: OUTSIDE` on a
component root that carries 2px of transparent padding.

---

## 5. Components — node ids and variant properties

| Component | Node id | Page | Variant properties | Variants | Other component properties |
|---|---|---|---|---|---|
| `Button` | `7:146` | `4:21` | `Kind` = Primary \| Secondary \| Quiet \| Danger; `State` = Default \| Hover \| Pressed \| Focus \| Disabled \| Loading | 24 | `Label` (TEXT, default "Button"), `Leading icon` (BOOLEAN, default false), `Icon` (INSTANCE_SWAP, default `icon/Check`) |
| `IconButton` | `8:104` | `4:22` | `Kind` = Secondary \| Quiet \| Danger \| On media; `State` = Default \| Hover \| Pressed \| Focus \| Disabled | 20 | `Icon` (INSTANCE_SWAP, default `icon/Heart`) |
| `TextField` | `9:42` | `4:23` | `State` = Default \| Hover \| Focus \| Error \| Disabled | 5 | — |
| `Textarea` | `9:83` | `4:23` | same | 5 | — |
| `Select` | `9:139` | `4:23` | same | 5 | — |
| `Checkbox` | `10:66` | `4:24` | `Checked` = Off \| On \| Mixed; `State` = Default \| Hover \| Focus \| Disabled | 12 | — |
| `Radio` | `10:103` | `4:24` | `Checked` = Off \| On; `State` = Default \| Hover \| Focus \| Disabled | 8 | — |
| `Switch` | `10:144` | `4:24` | `Checked` = Off \| On; `State` = Default \| Hover \| Focus \| Disabled | 8 | — |
| `Chip` | `11:54` | `4:25` | `Selected` = No \| Yes; `State` = Default \| Hover \| Focus \| Disabled | 8 | — |
| `Tab` | `11:79` | `4:25` | `Selected` = No \| Yes; `State` = Default \| Hover \| Focus | 6 | — |
| `PhotoCard` | `12:263` | `4:26` | `Aspect` = Landscape 3:2 \| Square 1:1 \| Portrait 4:5; `State` = Default \| Sensitive \| Loading | 9 | — |
| `Avatar` | `14:56` | `4:27` | `Size` = XS \| SM \| MD \| LG (24/32/40/64); `Type` = Image \| Initials \| Fallback | 12 | — |
| `TabBar Item` | `15:31` | `4:28` | `Selected` = No \| Yes; `State` = Default \| Focus | 4 | `Icon` (INSTANCE_SWAP, default `icon/House`), `Label` (TEXT, default "Home") |
| `TabBar` | `15:32` | `4:28` | — (single component, 390×72) | 1 | — |
| `TopNav` | `15:74` | `4:28` | — (single component, 1440×64) | 1 | — |
| `Dialog` | `16:43` | `4:29` | `Kind` = Standard \| Destructive | 2 | — |
| `Toast / Inline status` | `17:40` | `4:30` | `Tone` = Success \| Error \| Info | 3 | — |
| `Banner` | `17:68` | `4:30` | `Tone` = Info \| Warn \| Danger | 3 | — |
| `Skeleton` | `17:72` | `4:30` | `Shape` = Line \| Block \| Circle | 3 | — |
| `EmptyState` | `17:95` | `4:30` | `Kind` = Empty \| No results | 2 | — |
| `ErrorState` | `17:96` | `4:30` | — (single component) | 1 | — |

Every component carries a written `description` in Figma covering its accessibility contract
(accessible naming, roles, keyboard behaviour, live regions, target size). Those descriptions are
part of the deliverable and should be read in Dev Mode alongside this file.

Key ones, condensed:

- **Button** — focus-visible is a designed state, not a browser default. Disabled uses
  `bg-tint` + `ink-3` (4.90:1 light, 5.23:1 dark) so disabled text stays readable. Loading must set
  `aria-busy`, keep the accessible name stable, announce completion in a live region and swap the
  spinner for a static indicator under `prefers-reduced-motion`. Native `<button>` for actions,
  `<a>` for navigation.
- **IconButton** — the accessible name goes on the **button** (`aria-label` or a visually-hidden
  span), never on the SVG; the SVG is `aria-hidden="true" focusable="false"`. Never a hover-only
  tooltip as the only label. Toggles keep a stable label and expose `aria-pressed`. Hit box is
  **44×44** (root including its 2px padding) though the visible pill is 40×40 — WCAG 2.2 2.5.8.
- **TextField / Textarea / Select** — persistent visible `<label>`, never placeholder-as-label.
  Helper and error linked with `aria-describedby`; error carries `icon/CircleAlert` **plus** text
  plus `aria-invalid`, never colour alone. Correct `autocomplete` tokens (`username`,
  `current-password`, `new-password`, `one-time-code`) for WCAG 3.3.8.
- **Checkbox / Radio** — the unchecked boundary is the only signal of the off state, so it is
  `color/line` at `stroke/regular`: **3.49:1 light / 4.11:1 dark**, against the mockup's 1.35:1.
  Radios need a real `<fieldset>`/`<legend>`; the mockups used a bare `<p>` with no programmatic
  association.
- **Switch** — thumb **position** is the visual cue and `role="switch"` + `aria-checked` the
  programmatic one; state is never colour alone. The off track carries a `color/line` boundary.
- **Chip / Tab** — selection adds `icon/Check` (chip) or a 2px indicator plus a weight change (tab),
  never colour alone. A removable applied filter must name its **facet** ("Orientation: Landscape"),
  and its remove control is a separate labelled button.
- **PhotoCard** — see §6, departures 1–3.
- **Dialog** — `role="dialog" aria-modal="true"`, labelled by its title, focus moved in and
  **returned** on close, Escape closes, background inert, focus trapped. Initial focus lands on
  **Cancel**, never on the destructive action. The destructive variant states what will be deleted
  **and what will not**.
- **Toast / Inline status** — for **real outcomes only**. A failure toast does not auto-dismiss and
  carries the recovery action. Prefer inline status next to the control that failed.
- **Banner** — the honest surface for "this feature is unavailable here": names why and who can
  change it, instead of hiding the control or leaving a dead button.
- **ErrorState** — always carries retry; says what did not happen and what was not changed; never
  exposes a stack trace, internal id or signed URL in visible copy.

---

## 6. Change record — deliberate departures from the mockups

Each row is a decision, not an accident, with the reason and the authority.

| # | Departure | Why |
|---|---|---|
| 1 | **PhotoCard actions moved out of the `:hover` overlay into a persistent bar below the image.** | The mockup revealed Save/Love only on `:hover`/`:focus-within`. On touch a hover overlay does not exist, and white text over an arbitrary photograph has unmeasurable contrast. `DESIGN_BRIEF.md` rejects "missing mobile actions"; `GAPS.md` names this explicitly for the viewer. |
| 2 | **Image aspect ratio is preserved; `object-fit: cover`/`fill` is forbidden and three aspect variants ship.** | `DESIGN_BRIEF.md`: "Preserve the image's aspect ratio; do not default to destructive cropping." Mockup card 1 combined `aspect-ratio: 4/5` with default `object-fit: fill`, distorting the photograph. |
| 3 | **Favorite (`icon/Heart`, binary, `aria-pressed`) and Rating (`icon/Star`, 1–5, radiogroup) are separated in glyph and semantics.** | `DESIGN_BRIEF.md` names their conflation as a hazard. The mockup had only a Heart and a Bookmark and no rating at all. |
| 4 | **`--line` was split into `color/line` (meaningful, ≥3:1) and `color/line-2` (decorative).** The mockup's single `--line` at `oklch(0.90 …)` became `color/line-2`; the new `color/line` is `oklch(0.62 0.01 260)`. | One token cannot be both a 1.19:1 hairline divider and the sole indicator of an unchecked checkbox. WCAG 1.4.11 applies to the second use only. |
| 5 | **`--ink-3` darkened from `oklch(0.56 …)` to `oklch(0.52 …)`.** | 4.46:1 on `--bg` and 4.14:1 on `--bg-tint` both failed 4.5:1, and `--ink-3` is the colour of result counts, facet counts, section labels, handles, pager hints and placeholders. |
| 6 | **`--accent` darkened from `oklch(0.58 0.18 255)` to `oklch(0.55 0.18 255)`.** | One value now satisfies both duties: white-on-accent 4.93:1 **and** accent-as-link-text 4.72:1 on `color/bg`. At 0.58 both were 4.34/4.16 and failed. |
| 7 | **`--success` and `--warn` darkened substantially** (`oklch(0.66 0.16 150)` → `0.52 0.14`; `oklch(0.76 0.14 80)` → `0.54 0.11`). | The account-set values were 2.79:1 and 2.09:1 as text — they failed the graphic floor too. Amber is the hardest hue: reaching 4.5:1 forces it to read as a deep ochre. This is a deliberate legibility-over-vibrancy trade. |
| 8 | **The frosted top bar survives but at a fixed 92% opacity.** | The mockup's `color-mix(in oklab, white 82%, transparent)` put secondary text below 4.5:1 whenever a light photograph scrolled beneath. 92% is the measured minimum that keeps `ink-3` above 4.5:1 in both modes. |
| 9 | **On-image controls use an 88% opaque `color/on-media-scrim` chip instead of `rgba(255,255,255,.22)` + blur.** | Turns an unmeasurable value into a guaranteed 15.3:1 worst case. These two tokens are theme-invariant because their backing is a photograph, not a themed surface. |
| 10 | **Dark mode is authored, not inverted.** Dark neutrals sit on hue 265 with their own lightness ladder; dark accent/status colours move **up** the ramp (`blue/500`→`blue/300`) and `on-*` flips to `neutral/900`. | The mockups have no dark mode at all — 19 hard-coded `white` values in `account.css` alone. Inversion would have produced a 0.18-lightness "white" and a garish accent. |
| 11 | **Focus-visible designed on every interactive component, with a 2px offset.** | The mockups had **no** `:focus-visible` rule and actively removed focus in four places (`all: unset` on menu items, `outline: none` on the range input, `appearance: none` on 17 checkboxes/radios with no replacement, `-webkit-tap-highlight-color: transparent`). |
| 12 | **Scales collapsed:** 15 radii → 5; 9+11 ad-hoc shadow recipes + 5 tokens → 3 elevations; 15+14 type sizes (with fractional 11.5/12.5/13.5/14.5px) → 9 steps; ~35 off-grid spacing values → an 11-step 4px grid. | The mockups declared token sets and then bypassed them with literals. A design system that is not used is not a design system. |
| 13 | **Font stack renamed to a neutral system stack** (`system-ui, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", Arial, sans-serif`); `--font-display` dropped entirely. | `DESIGN_BRIEF.md` forbids assuming Apple fonts; the mockups named `-apple-system`, `BlinkMacSystemFont`, `"SF Pro Text"` and `"SF Pro Display"`. The two mockup families also disagreed about whether a display face existed — one ramp settles it. |
| 14 | **The gradient brand mark is gone; only a placeholder text style remains.** | `DESIGN_BRIEF.md`: custom Vizra brand marks are original vector assets, separately reviewed. D1 must not pre-empt that. |
| 15 | **New components the mockups had no pattern for:** Dialog (incl. destructive), Toast/inline status, Banner, Skeleton, EmptyState (two kinds), ErrorState, Switch, safety-blur state, visibility marker. | `GAPS.md` §"Two cross-cutting gaps": "No dialog, sheet, menu, toast, skeleton, focus-visible system or `aria-live` region exists anywhere in the account set", and six of the fourteen M1 surfaces are dialogs. |
| 16 | **EmptyState is two variants, not one** (genuinely empty vs filtered-to-zero). | `GAPS.md`: "specify them for both the genuinely-empty case and the filtered-to-zero case, which are different." |
| 17 | **TopNav gains a real skip link and a `<button>` account control.** | No mockup had a skip link; the account control was an inert `<span>`. |
| 18 | **`color/danger-hover` / `-pressed` added** (and the accent equivalents). | The requirement that on-accent text hold ≥4.5:1 "at rest **and on hover**" cannot be met if no hover fill is defined. |

---

## 7. Icon inventory

One family: **Lucide** (ISC licence; attribution must be preserved per `DESIGN_BRIEF.md`). Named
static imports behind a typed semantic registry — never an arbitrary runtime string, never the whole
library loaded for a handful of controls.

**Every export name below is PROPOSED and must be verified against the pinned `lucide-react`
version before use.** Names marked **(!)** were renamed in recent Lucide releases; the older spelling
may exist only as a deprecated alias, or not at all. Do not assume either spelling.

| Purpose | Proposed `lucide-react` export | Confidence | Figma node |
|---|---|---|---|
| upload | `Upload` | high | `5:20` |
| favorite (binary toggle) | `Heart` | high | `5:12` |
| rating (1–5 value) | `Star` | high | `5:15` |
| comment | `MessageCircle` | high | `5:64` |
| add to album | `FolderPlus` | high | `5:69` |
| share | `Share2` | high | `5:76` |
| download | `Download` | high | `5:25` |
| report | `Flag` | high | `5:61` |
| delete | `Trash2` | high | `5:32` |
| search | `Search` | high | `5:5` |
| filter | `SlidersHorizontal` | high | `5:87` |
| visibility: public | `Globe` | high | `5:41` |
| visibility: unlisted | `Link` | high | `5:45` |
| visibility: private | `Lock` | high | `5:36` |
| visibility: password | `KeyRound` | **medium (!)** (was `Key`) | `5:49` |
| settings | `Settings` | high | `5:53` |
| notifications | `Bell` | high | `5:57` |
| close / dismiss | `X` | high | `5:9` |
| back | `ArrowLeft` | high | `5:91` |
| previous | `ChevronLeft` | high | `5:94` |
| next | `ChevronRight` | high | `5:97` |
| disclosure / expand | `ChevronDown` | high | `5:100` |
| zoom in | `ZoomIn` | high | `5:106` |
| zoom out | `ZoomOut` | high | `5:111` |
| selected / confirm | `Check` | high | `5:114` |
| in flight (spinner) | `LoaderCircle` | **medium (!)** (was `Loader2`) | `5:117` |
| info | `Info` | high | `5:122` |
| warning | `TriangleAlert` | **medium (!)** (was `AlertTriangle`) | `5:127` |
| success status | `CircleCheck` | **medium (!)** (was `CheckCircle2`) | `5:131` |
| error status | `CircleAlert` | **medium (!)** (was `AlertCircle`) | `5:136` |
| photo / media placeholder | `Image` | high | `5:141` |
| hidden / safety blur | `EyeOff` | high | `5:147` |
| retry | `RotateCw` | high | `5:151` |
| overflow menu | `Ellipsis` | **medium (!)** (was `MoreHorizontal`) | `5:156` |
| person / avatar fallback | `User` | high | `5:160` |
| home | `House` | **medium (!)** (was `Home`) | `5:164` |
| edit | `Pencil` | high | `5:168` |

**Favorite and Rating are deliberately distinct** in glyph *and* semantics: `Heart` is a binary
toggle exposing `aria-pressed`; `Star` is a 1–5 value in a radiogroup. `DESIGN_BRIEF.md` names their
conflation as a hazard.

**Glyph geometry caveat.** The 37 Figma components are drawn on Lucide's 24px grid with a 2px
round-cap stroke and match Lucide's construction, but they are **hand-drawn stand-ins, not traced
from the package**. The library's contract is the *name*, the *size*, the *stroke* and the
*semantic role*; the shipping SVG must come from the pinned `lucide-react` package. Do not export
these Figma vectors into the codebase.

Sizes: `size/icon-sm` 16 (inline), `size/icon` 20 (default, used in all controls here),
`size/icon-lg` 24 (prominent). Stroke is fixed at 2px at 24px and scales with the icon.

---

## 8. Mirroring into Tailwind

Every semantic colour and every `Scale` variable already carries a Figma **web code syntax** of the
form `var(--vz-<token>)`, with the `color/` prefix stripped:

| Figma variable | CSS custom property |
|---|---|
| `color/ink-2` | `--vz-ink-2` |
| `color/on-media-scrim` | `--vz-on-media-scrim` |
| `space/4` | `--vz-space-4` |
| `radius/lg` | `--vz-radius-lg` |
| `type/body/size` | `--vz-type-body-size` |

Recommended shape: define the light palette on `:root`, redefine only the 36 `Color` tokens under
`:root[data-theme="dark"]` **and** under `@media (prefers-color-scheme: dark)` guarded as
`:root:not([data-theme="light"])`, then map the custom properties into the Tailwind theme. Primitives
should **not** be emitted as CSS variables — they are an implementation layer and are `scopes = []`
in Figma for the same reason.

### 8.1 DO NOT MIRROR INTO CODE — `Meter fit (fill width)`

One variable collection in this file is **not a design token set** and must never be mirrored into
Tailwind, CSS custom properties, or any generated token artifact:

| Collection | `Meter fit (fill width)` — `VariableCollectionId:67:1772` |
|---|---|
| Modes | `Natural 320`, `Column 670`, `Column 308` |
| Variables | `meter/fill-62`, `meter/fill-91`, `meter/fill-100` (FLOAT, `scopes = ["WIDTH_HEIGHT"]`) |

It exists only because a Figma instance cannot override nested geometry, so the `Meter` fill could
not otherwise draw the percentage its label states once the instance was stretched to a column
width. It encodes three hard-coded percentages against three hard-coded column widths — a layout
workaround, not a semantic role.

**In production the storage meter computes its own width** (`width: used / allowed`) and needs none
of these values. They are marked `hiddenFromPublishing`, carry a `DO NOT MIRROR INTO CODE`
description on the collection and on every variable, and deliberately have **no** `var(--vz-…)` web
code syntax — unlike every real token in §8. A mirroring script should key on the presence of the
`var(--vz-…)` code syntax, not on "every local variable", so that this collection and any future
Figma-only workaround are excluded by construction.

---

## 9. Verification performed

Screenshots were taken with `get_screenshot` and visually inspected. Where inspection found a
defect it was fixed and re-inspected; three defects were found this way.

| Surface | Node | Verdict |
|---|---|---|
| Icons (all 37) | `4:32` | PASS — all glyphs legible; Heart and Star visibly distinct |
| Button (24 variants) | `7:146` | PASS |
| IconButton (20 variants) | `8:104` | PASS after fix (see below) |
| Inputs — TextField, Textarea, Select | `4:23` | PASS after fix |
| Selection — Checkbox, Radio, Switch | `4:24` | PASS — unchecked boundaries clearly visible |
| Chip & Tab | `4:25` | PASS |
| PhotoCard (9 variants) | `12:263` | PASS after fix |
| Dialog | `16:43` | PASS — focus ring on Cancel renders correctly |
| Feedback — Toast, Banner, Skeleton, EmptyState, ErrorState | `4:30` | PASS after fix |
| Navigation — TopNav, TabBar | `4:28` | PASS after fix |
| Foundations — colour boards, both modes | `18:49`, `18:213` | PASS |
| Foundations — type ramp | `19:2` | PASS |
| Foundations — contrast table | `20:2` | PASS |
| **Dark mode verification board** (live instances, `Color` forced to `Dark`) | `21:326` | PASS — every component resolves the Dark column correctly |

Defects found by looking at the screenshots and then fixed:

1. **PhotoCard and all three Inputs collapsed to 10px tall.** `resize()` had silently reset the
   auto-layout `primaryAxisSizingMode` from `AUTO` to `FIXED`. Repaired by restoring
   `layoutSizingVertical = 'HUG'` on 24 variant roots; heights are now 288–481 (PhotoCard) and
   90/146/90 (TextField/Textarea/Select).
2. **ErrorState rendered with a black background.** The fill was correctly bound to
   `color/bg-elevated` but Figma was painting the unresolved black fallback. Repaired by writing the
   resolved Light-mode value into every bound paint on that page; a sweep found exactly one affected
   node.
3. **TabBar's selected tab icon did not resolve `color/accent`,** and **IconButton `On media` Hover
   was visually identical to Pressed.** Both repaired; Pressed now inverts to a solid `on-media`
   chip with an `ink` glyph, Hover keeps the scrim chip with an `on-media` ring.

A structural audit of the finished file also confirmed **no hardcoded solid paint remains inside any
component** other than six deliberate ones (§10).

---

## 10. What is not finished, and what I could not verify

Recorded honestly. None of these is blocking for D2, but all are open.

1. **Lucide export names are unverified.** No package is pinned in this repo yet, and I had no
   network access to check. Seven names are flagged **(!)** as renamed in recent Lucide releases.
   `vizra-user` must resolve all 37 against the pinned `lucide-react` version and correct this
   document. **Do not ship the typed registry until this is done.**
2. **Icon glyphs are stand-ins, not Lucide's own paths.** See §7. The names, sizes and stroke are the
   contract; the vectors are not for export.
3. **Six intentionally unbound paints remain** — the `blur` and `safety-cover` layers of the three
   PhotoCard `Sensitive` variants. They represent image content and a photographic darkening layer,
   not themeable surfaces. Everything else in every component is variable-bound.
4. **Not built in D1** (out of scope, needed by D2 or later): Menu/Popover, Tooltip, Breadcrumb,
   Pagination/Load-more, Progress bar (`role="progressbar"` for upload), file-drop zone, segmented
   control, range slider, tag input, table/list row, bottom-sheet presentation as its own component,
   lightbox chrome, and the album/photo grid containers.
5. **No responsive proof.** Components were designed with 390px and 1440px in mind and `TopNav`
   (1440) and `TabBar` (390) are drawn at those widths, but **no page has been laid out and checked
   at 390px, at 320px reflow, or at 200% zoom** — there are no pages yet. That verification belongs
   to D2 and must not be assumed from this file.
6. **No real photographs.** PhotoCard and Avatar use gradient placeholders. The on-media contrast
   figures are worst-case *computed* bounds (white and black extremes), which is the strongest claim
   available without images — but they have not been confirmed against actual photographs.
7. **Motion is tokenised but not specified.** `motion/fast|base|slow` exist; no easing curves,
   no per-component transition map, and no `prefers-reduced-motion` variant has been drawn. The
   mockups' two overshoot curves and the 0.6s Ken-Burns image zoom were simply dropped, not
   redesigned.
8. **Not published as a Figma library.** The file is a draft; components are local, not published
   for subscription. D2 will need it published (or will work in the same file) before
   `search_design_system` can find these components from another file.
9. **Not reviewed by anyone.** This is a single-pass build. `AGENTS.md` requires independent review;
   `vizra-design` in council mode has not seen it, and the owner has not approved it. Status remains
   **PROPOSED**. Nothing here is VERIFIED.
10. **Dark mode was verified by forcing the `Color` collection mode on a verification board**, which
    is how Figma models theming — but that is a design-time check. It is not evidence that the
    shipped Tailwind implementation will resolve identically.
11. **Screenshots are not archived in the repository.** They were inspected in-session via
    short-lived `get_screenshot` URLs. If the war room needs durable visual evidence under
    `docs/evidence/`, it must be re-captured and committed.
