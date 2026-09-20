# Claude Design import — exploration mockups

Verbatim snapshot of the owner's Claude Design project, kept so implementers can open the
mockups locally, screenshot them, and compare. Nothing here is shipped code.

## Provenance

| Field | Value |
|---|---|
| Source | Claude Design project **"goimg"** (`PROJECT_TYPE_PROJECT`) |
| Project id | `74024d9f-fbd2-4152-9be0-d19ee68fec86` |
| URL | https://claude.ai/design/p/74024d9f-fbd2-4152-9be0-d19ee68fec86 |
| Owner | Yosef Gamble |
| Fetched | 2026-09-20, via the `DesignSync` tool (`get_file`, read-only) |
| Fidelity | Byte-exact: each file is the UTF-8 encoding of the `content` string the tool returned, with no reformatting and no added trailing newline. Every response reported `isBase64: false`, `truncated: false`. |

## Files (13 files, 265634 bytes)

| File | Bytes | sha256 | Truncated? |
|---|---:|---|---|
| `Lumen Atlas Search.html` | 65899 | `8c3d460c476e2f7a1cda34d18cb596b1c41ecc1f7e89a802eb92b98f327d9be5` | no |
| `Lumen Atlas Gallery.html` | 47712 | `73a22d5c85c290524fabb0f7403058c6bad939e547636f0a0e2647171fe7e9e5` | no |
| `Artist Profile.html` | 37507 | `1da8ec0c92bce6a3c867e0c29151eb947d37999783ba67a436ea72e74410f759` | no |
| `Account Settings.html` | 7990 | `edb42a597a78a2be92488846621ef70e6f65903a07e9667d610086d50071787c` | no |
| `Edit Photo.html` | 8113 | `8f19661c9de88cec81f52e9178fc45cb8bc5c3a24b2b9af535b08f9e0fe013a3` | no |
| `Edit Profile.html` | 8516 | `9ade2a21c2d61ca249b8d5793a8b1a5ebbe4414fe3e701f535389cb60427e853` | no |
| `My Albums.html` | 9858 | `26d1df93e4dec582906e4b3f7f59d74242b6b38f4ae67f9b567789517edb74c2` | no |
| `My Photos.html` | 10545 | `16a2759ddff22fb54395c7478da0f6096940b4eb9ca45f6a7359c0767f9e8a5c` | no |
| `Notifications.html` | 9094 | `2972260abe7891e4b70b009c9fe98dcd09d04beda29f1a8b125c09e251d45da8` | no |
| `Photo Insights.html` | 12020 | `7888b2acaaf391f11f1f66c3588b7db710bc5eca11336383af4e9ea9ebedff10` | no |
| `Upload Studio.html` | 23889 | `00cd5a72c3c7fd6a0965da424f5a00802c15f280f9205c16302ee676130266ae` | no |
| `account.css` | 16108 | `d7a5560196b8a1735c9a7de834c88acaf9db780251b29572a812c981b81a253f` | no |
| `account-shell.js` | 8383 | `a93dcb4a086348ea5e2a9b7d0979ce80a153084a78106c92833020f8f45685b7` | no |

Verify with `shasum -a 256 docs/design/claude-design/*` — a changed hash means the local copy
was edited or the project was re-imported; record a new fetch date rather than editing in place.

Page relationships: the three public pages (`Lumen Atlas Gallery.html`, `Lumen Atlas Search.html`,
`Artist Profile.html`) are self-contained (inline CSS/JS). The eight account pages share
`account.css` and `account-shell.js`; the script injects the top nav, sidebar, mobile section
select and mobile tab bar into `#nav-slot`, `#sidebar-slot`, `#mobile-header-slot` and
`#mobile-tabs-slot`, keyed by `window.__page.key`. All local `href`/`src` references between
these files resolve within this directory.

## Deliberately not imported

- `Lumen Atlas Gallery.standalone.html` — a bundled duplicate of the Gallery page with assets inlined.
- `uploads/*.png` (three `draw-*.png`, five `pasted-*.png`) — binary reference images pasted into the
  design project; provenance and licence unknown, so they stay out of the repository.
- `.thumbnail` — the design tool's own project thumbnail.

## Standing notes

1. **Exploration input, not the design source.** Per `docs/DESIGN_BRIEF.md`: "Claude Design is for
   exploration. Approved Figma components/tokens, mirrored in repository artifacts, become the design
   source." Implement from the approved Figma components/tokens and record node references and a
   design revision; use these mockups to understand intent, not as the acceptance target.
2. **Unsplash URLs are hotlinked placeholders.** Every photograph is an `https://images.unsplash.com/…`
   hotlink used for mock content. They are not assets to ship, bundle, cache or use as fixtures;
   shipping UI renders real uploaded media through the real API (`AGENTS.md`: no mock data in
   production paths).
3. **"Lumen Atlas" is a placeholder brand.** The public mockups say "Lumen Atlas" and the account
   mockups say "goimg" (including `goimg.com/` and "goimg Pro"); the product is **Vizra**. Do not carry
   either name, the gradient brand mark, or the mock plan/billing copy into the product — Vizra has no
   billing product, and its brand mark is an original, separately reviewed asset.

Also note when reading the mockups: the font stack names "SF Pro Text"/"SF Pro Display" (the brief
forbids distributing Apple fonts — a system stack is fine, bundling is not); icons are hand-inlined SVG
paths rather than the typed Lucide registry the brief requires; only a light theme is defined; and all
data, counts and interactions are static or cosmetic (class toggles), so no control here is evidence of
working behaviour.
