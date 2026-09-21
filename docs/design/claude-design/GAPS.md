# Design gaps — surfaces the product needs that have no mockup

Companion to `INVENTORY-search.md` and `INVENTORY-account.md`. Those two documents record what the
owner's Claude Design import **contains**; this one records what it **does not**.

**Scope.** Eleven mockups exist in `docs/design/claude-design/`:

| Mockup | Surface it stands for |
|---|---|
| `Lumen Atlas Gallery.html` | public exploration / home |
| `Lumen Atlas Search.html` | search results (`VZ-SEARCH-001`) |
| `Artist Profile.html` | public member profile (`/u/{username}`, `VZ-PROFILE-001`) |
| `Upload Studio.html` | `/upload` |
| `My Photos.html` | `/library` |
| `My Albums.html` | `/albums` |
| `Edit Photo.html` | `/photos/{id}/edit` |
| `Edit Profile.html` | `/settings/profile` |
| `Account Settings.html` | `/settings/account` + `/security` + `/sessions` + `/connections` |
| `Notifications.html` | `/settings/notifications` + `/privacy` + `/blocks` |
| `Photo Insights.html` | `/stats` |

**Method.** The needed-surface list is derived from the 59 rows of `docs/quality/ui-controls.json`
(their `route` values), the domain and workflow sections of `docs/PRODUCT_SPEC.md` (§4–§9, §15), the
first-slice workflow named in `prompts/02-design-system.md` ("setup/sign-in → upload → personal
library → photo viewer → add to album → share/privacy controls") and the golden path in
`prompts/03-first-real-slice.md`. Milestones are from `docs/MILESTONES.md`. Ledger IDs are from
`docs/quality/features.json`; none has been invented.

**Status.** Descriptive gap list only. Not an acceptance target, not a design brief, not
authorization to build anything. Per `docs/DESIGN_BRIEF.md`, the design source is approved Figma
components and tokens mirrored into the repository — and per the same document, "Start with the
first working slice, not fifty speculative screens", so the M1 block below is the only part that is
urgent.

**The headline.** `docs/PRODUCT_SPEC.md` §15 defines `VZ-SLICE-01` as *install → owner claim →
sign in → upload → decoded thumbnail → **viewer** → album → privacy → restart → denied access →
backup → restore*. Of the nine user-facing steps in that sentence, the mockups cover **two**
(upload, library). **The photo viewer — the single screen the whole product exists to
serve — has no mockup at all**, and neither does anything before sign-in.

---

## The table

| Milestone | Surface | What it is | Ledger ID(s) | Closest existing mockup |
|---|---|---|---|---|
| M0 | **Setup wizard (loopback web)** | The `vizra setup` browser wizard: interview questions, validation, written env file, `--check` result | `VZ-INSTALL-002`, `VZ-TOPOLOGY-006/007` | `Account Settings.html` (card + `.row` list) |
| **M1** | **Owner claim** (`/setup/claim`) | One-time token entry, owner credential creation, "already claimed" refusal | `VZ-INSTALL-003`, `VZ-AUTH-004` | `Edit Profile.html` (single form card) |
| **M1** | **Sign-in** (`/login`) | Email + password, errors, rate-limit lockout; later the 2FA challenge and provider buttons | `VZ-AUTH-001`; later `VZ-AUTH-003` (M2), `VZ-AUTH-006/007` (M5/M6) | `Edit Profile.html` |
| **M1** | **Sign-up** (`/signup`) | Registration when policy allows; closed / invite / approval refusals; consent and age gate | `VZ-AUTH-001`; later `VZ-AUTH-005` (M2), `VZ-CONSENT-001` (M5) | `Edit Profile.html` |
| **M1** | **Photo page + lightbox viewer** (`/p/{id}`) | The product's centre: image at true aspect ratio, zoom/pan, next/previous, close, caption, metadata, EXIF tab, owner actions, and later favourite / rating / comments / share / download / report | `VZ-VIEWER-001`, `VZ-MEDIA-001/003/004`, `VZ-PRIVACY-001`, `VZ-LIBRARY-001`; later `VZ-FAVORITE-001`, `VZ-RATING-001`, `VZ-COMMENT-001` (M2), `VZ-DOWNLOAD-001`, `VZ-SHARE-001/002` (M3) | `Edit Photo.html`'s `.photo-pane` (a `#0a0c12` box with `object-fit: contain`) — the only dark image surface in the set |
| **M1** | **Album detail** (`/a/{id}`) | Album header, cover, description, its photos, sorts, add/remove, reorder, sub-albums, owner actions | `VZ-ALBUM-001`; later `VZ-ALBUM-003/004` (M3) | `My Photos.html` grid + `My Albums.html` card head |
| **M1** | **Add-to-album dialog** | Pick one or more existing albums, or create one inline, from the viewer or from a library selection | `VZ-ALBUM-001` (its `ui` field names this dialog explicitly) | none — **no dialog, modal or sheet exists anywhere in the account set**; nearest is the `<select>` in `Upload Studio.html` |
| **M1** | **Asset privacy dialog** | Set public / unlisted / private on one asset or a selection, with the consequence stated | `VZ-PRIVACY-001` (its `ui` field names this dialog); later `VZ-PRIVACY-002/003/004` (M5) | `Edit Photo.html` "Audience" card |
| **M1** | **Album privacy + share-grant dialog** | public / private / link-only / **password**; create, list and revoke share grants | `VZ-ALBUM-002` (`album privacy dialog`, `/settings/shares`) | none |
| **M1** | **Destructive-confirmation dialog** | The single reusable pattern behind delete photo, bulk delete, delete album, remove avatar/cover, sign out of all, delete account | `VZ-LIBRARY-001`, `VZ-ALBUM-001`, `VZ-ACCOUNT-002/003`, `VZ-AUTH-001`; `DESIGN_BRIEF.md` "destructive-confirmation" | none — six destructive controls, zero confirmations |
| **M1** | **Upload progress / failure / retry panel** | Real per-file progress, cancel, retry, rejected-format and oversized refusals, quota exceeded, worker failure, processing-failed | `VZ-UPLOAD-001/002`, `VZ-QUOTA-001`, `VZ-JOBS-001`; `prompt 03`: "Surface processing failure instead of leaving an endless spinner" | `Upload Studio.html` `.queue` (a static 65 % arc) |
| **M1** | **Keyboard / file-picker upload path** | The `<input type="file">` route, its focus and labelling, and paste + camera sources | `VZ-UPLOAD-003`; `prompt 03`: drag-and-drop alone "is not sufficient" | `Upload Studio.html` `.drop` (drag handlers only; **zero file inputs exist in the whole import**) |
| **M1** | **Empty states for library and albums** | Zero photos, zero albums — what a freshly installed instance shows its owner the minute after claim | `VZ-LIBRARY-001`, `VZ-ALBUM-001`; `DESIGN_BRIEF.md` states list | `My Albums.html`'s `.alb-new` create tile |
| **M1** | **Unauthorized / not-found / private-content page** | What a second account or an anonymous visitor sees on a private photo, derivative, album or metadata URL — the negative half of the golden path | `VZ-PRIVACY-001`, `VZ-AUTH-004`; `prompt 03` denied-access tests | none |
| **M1** | **Session-expired / re-authenticate dialog** | Mid-action session loss, and re-auth before destructive account actions | `VZ-AUTH-001`; `ui-controls.json` `settings.account.delete` ("re-auth"); `prompt 03` "expired session" | `Account Settings.html` Sessions card |
| **M1** | **Storage quota / usage** (`/settings/storage`) | Used vs allowed, near-limit warning, over-limit refusal — the honest replacement for the mockup's billing card | `VZ-QUOTA-001` | `Account Settings.html` `.plan-card` (which must be deleted, not re-skinned) |
| M2 | **Notification centre** (`/notifications`) + bell panel | Unread badge, panel, mark-as-read, paged history — the ledger surface the "Notifications & Privacy" page is named after but does not contain | `VZ-NOTIFY-001` | `Notifications.html` (preferences only); `Account Settings.html` row list |
| M2 | **Report dialog** | Report a photo, comment or member with categories and outcome feedback | `VZ-REPORT-001` | none |
| M2 | **Blocked-accounts list** (`/settings/blocks`) | The list behind `Notifications.html`'s dead `Manage` button | `VZ-BLOCK-001` | `Account Settings.html` Connected-accounts rows |
| M2 | **2FA enrolment flow** (`/settings/security`) | Secret/QR → verify code → recovery codes shown once → regenerate | `VZ-AUTH-003` | `Account Settings.html` 2FA card (a toggle) |
| M2 | **Email verification + password reset** (`/verify`, `/reset`) | Sent / expired / invalid / success | `VZ-AUTH-002` | `Edit Profile.html` |
| M2 | **Content-safety preferences** (`/settings/content`) | The member's viewing level across safe / moderate / restricted | `VZ-NSFW-001` | `Notifications.html` Privacy card |
| M2 | **Favourites listing** (`/u/{username}/favorites`) | A member's favourited photos and albums | `VZ-FAVORITE-001` | `My Photos.html` grid |
| M2 | **Following feed** | Photos from followed members | `VZ-FOLLOW-001`; later `VZ-FEED-001` (M5) | `Lumen Atlas Gallery.html` |
| M2 | **Admin dashboard** (`/admin`) | Operator overview and entry point to every admin surface | `VZ-ADMIN-001`; counts are `VZ-STATS-001` (M3) | `Photo Insights.html` KPI row |
| M2 | **Admin settings registry** (`/admin/settings/*`) | ~20 settings sections with validation, effective values, audit | `VZ-ADMIN-002/003` | `Notifications.html` row lists |
| M2 | **Admin users** (`/admin/users`, `/admin/users/{id}`) | List, search, role change, suspend, reset password, quota override | `VZ-ADMIN-USERS-001`, `VZ-AUTH-004`, `VZ-QUOTA-001` | `Account Settings.html` |
| M2 | **Moderation queue + audit log** (`/admin/moderation`, `/admin/audit`) | Reports, pending uploads, safety flags, actions with reasons | `VZ-MOD-001`, `VZ-UPLOAD-012`, `VZ-NSFW-001` | `My Photos.html` (grid + bulk bar) |
| M2 | **Registration policy screens** (`/admin/settings/registration`, `/admin/registrations`) | Open / approval / invite / closed; pending approvals | `VZ-AUTH-005` | `Account Settings.html` |
| M2 | **Job administration** (`/admin/jobs`) | Queue depth, failures, retry, dead letters | `VZ-OPS-006`, `VZ-JOBS-001` | `Photo Insights.html` |
| M3 | **Share dialog** | Direct / viewer / thumbnail links, HTML / Markdown / BBCode embeds, social buttons, oEmbed | `VZ-SHARE-001/002` | none |
| M3 | **Download menu + bulk zip** | Size picker, permission refusal, bounded zip as a job | `VZ-DOWNLOAD-001` | `My Photos.html` bulk `Download` button |
| M3 | **Upload result panel** | Links, embed codes, delete link, expiry | `VZ-UPLOAD-008/009`, `VZ-SHARE-002` | `Upload Studio.html` publish bar |
| M3 | **URL upload and guest upload** | Remote-URL tab with SSRF refusal; the anonymous uploader variant | `VZ-UPLOAD-004/005` | `Upload Studio.html` |
| M3 | **API keys + ShareX** (`/settings/api`) | Create / regenerate / revoke, scopes, snippet | `VZ-AUTH-008`, `VZ-UPLOAD-010` | `Account Settings.html` |
| M3 | **Library bulk-edit panel** | Bulk title/description/alt/tags/category/NSFW/date time-shift | `VZ-LIBRARY-002` | `My Photos.html` bulk bar |
| M3 | **Tag pages** (`/tag/{name}`, `/explore/tags`) | Tag listing, top tags, rename/delete across items | `VZ-TAG-001` | `Lumen Atlas Search.html` |
| M3 | **Category listings** (`/category/{key}`, `/admin/settings/categories`) | Admin-defined categories and their pages | `VZ-CATEGORY-001` | `Lumen Atlas Gallery.html` |
| M3 | **Explore tabs + random** (`/explore/*`) | Recent / trending / popular / following / albums / users / tags; random | `VZ-EXPLORE-001/002` | `Lumen Atlas Gallery.html` |
| M3 | **Advanced search dialog** | All-words / exact-phrase / none-of-these, operators, category scope | `VZ-SEARCH-001` | `Lumen Atlas Search.html` sidebar |
| M3 | **Account export / delete flow** | Re-auth → confirm → queued → ready → expired | `VZ-ACCOUNT-002` | `Account Settings.html` Danger zone |
| M3 | **Search admin** (`/admin/search`) | Index state, fallback status, reindex | `VZ-SEARCH-004` | `Photo Insights.html` |
| M4 | **Storage locations** (`/admin/storage`) | Add location, capacity, CDN mapping, migration with reconciliation | `VZ-STORAGE-004/005/014`, `VZ-QUOTA-002` | `Account Settings.html` |
| M4 | **Filesystem importer** (`/admin/import`) | Dry run, mapping, checkpoints, resume, report | `VZ-IMPORT-001` | `Upload Studio.html` step rail |
| M4 | **Maintenance mode + system** (`/admin/settings`, `/admin/system`) | Maintenance banner, update check, guided upgrade | `VZ-OPS-004`, `VZ-UPDATE-001` | `Notifications.html` |
| M5 | **Collections** (`/collections`) | Tree of own albums, depth 5, mosaic cover, share by URL | `VZ-COLLECTION-001` | `My Albums.html` |
| M5 | **Galleries** (`/galleries`) | Curated sets of other members' public safe photos, creator opt-out | `VZ-GALLERY-001` | `My Albums.html` |
| M5 | **Groups** (`/groups`, `/g/{slug}`, pool, discussions) | Create, privacy, join/invite, roles, pool approval, topics | `VZ-GROUP-001/002/003` | `Artist Profile.html` |
| M5 | **Messages** (`/messages`) | One-to-one conversations — the target of `Notifications.html`'s "Who can message you" | `VZ-MESSAGE-001` | none |
| M5 | **Map / geo** (`/map`, viewer map) | Geotagged photos, geo-privacy, geofences | `VZ-GEO-001` | `Photo Insights.html` audience chips |
| M5 | **Named audiences** (`/settings/privacy/audiences`) | Friends/family-style lists usable as visibility targets — the real backing for the "Followers" segment the mockups already draw | `VZ-PRIVACY-004` | `Edit Profile.html` Links card |
| M5 | **Follow requests** (`/settings/follow-requests`) | Approve/decline, re-evaluation on privacy change | `VZ-FOLLOW-002` | `Account Settings.html` |
| M5 | **Notes and people tags** (viewer layers) | Positional notes; people tagging with consent and "remove me from all" | `VZ-NOTES-001`, `VZ-PEOPLE-001` | none |
| M5 | **Branding, homepage, pages, semantics, languages** (`/admin/settings/*`, `/page/{key}`) | Logo, palettes, custom CSS boundary, homepage styles, custom pages, noun renaming, language chooser | `VZ-BRAND-001…005`, `VZ-PAGE-001`, `VZ-I18N-001`, `VZ-LISTING-001` | `Notifications.html`, `Lumen Atlas Gallery.html` |
| M5 | **Consent / age gate and cookie notice** | Pre-entry gate with cover image | `VZ-CONSENT-001` | `Lumen Atlas Gallery.html` |
| M5 | **External services, IP bans, flood protection, banners** (`/admin/settings/*`) | CAPTCHA, Akismet/SFS, moderation API, CSAM adapter, bans, limits, ad slots | `VZ-SERVICES-001…005`, `VZ-SECURITY-001/002`, `VZ-BANNER-001` | `Account Settings.html` Connected-accounts card |
| M5 | **Chevereto / Flickr import and site export** | Mapping, dry run, report | `VZ-IMPORT-002/003`, `VZ-EXPORT-001` | `Upload Studio.html` |
| M6 | **Federation settings** (`/settings/federation`, `/admin/federation`) | Actor, per-user opt-out, instance allow/block lists | `VZ-AP-001/004` | `Account Settings.html` |
| M6 | **AT Protocol / Bluesky** (`/settings/connections`) | DID login, cross-post opt-in with lexicon limits | `VZ-AUTH-007`, `VZ-AT-001/002` | `Account Settings.html` Connected-accounts card |
| M6 | **IPFS publication dialog** (viewer share → IPFS) | Per-publication consent with a persistence warning; pin inventory | `VZ-IPFS-001/002` | none |
| M6 | **Analytics admin** (`/admin/analytics`) | Pipeline lag, replay, dead letters, retention | `VZ-ANALYTICS-001` | `Photo Insights.html` |

---

## What each **M1** surface must specify

`DESIGN_BRIEF.md` requires every one of these to document loading / empty / error / success /
disabled states, light and dark modes, 200 % zoom, reduced motion, keyboard navigation and
responsive behaviour at 390px and 1440px. The notes below name what is *additionally* specific to
each surface, and are written against `VZ-A11Y-001`, `VZ-RESPONSIVE-001` and `VZ-CONTROLS-001`.

**Setup wizard (M0) and Owner claim.** States: token valid / already used / expired / instance
already claimed; password strength; submission in flight; failure with the token preserved.
Keyboard: a real `<form>` with a submit button, focus on the first invalid field, errors linked by
`aria-describedby` and announced in an `aria-live` region — none of the eleven mockups contains a
`<form>` element at all. Mobile: single column at 390px; the token is long, so it needs a
wrapping monospace field, not a fixed-width input. This surface is seen exactly once per instance
and cannot be recovered from a design error, so its refusal copy matters more than its layout.

**Sign-in and sign-up.** States: invalid credentials (without revealing which field), unverified
email, rate-limited/locked with a wait time, registration closed / invite-only / awaiting approval,
2FA challenge and recovery-code entry (M2), provider buttons rendered only for providers the
operator configured (M5). Keyboard: autocomplete tokens (`username`, `current-password`,
`new-password`, `one-time-code`), Enter submits, error summary receives focus. Mobile: the shell's
sidebar and nav search are both hidden below 900px, so these pages need their own centred layout
rather than the `.app` grid.

**Photo page + lightbox viewer.** The largest gap and the highest risk. Must specify: true aspect
ratio with no crop (`DESIGN_BRIEF.md`) and a defined behaviour for very tall and very wide images;
zoom and pan with a **keyboard alternative** (`ui-controls.json` `photo.viewer.zoom` says so in
terms); next/previous on arrow keys and close on Escape **with focus returned to the invoking
thumbnail** (`photo.viewer.close`); a focus trap while the lightbox is open and `inert` content
behind it; caption, title, author, date, EXIF tab, license and visibility marker; the owner's
actions (privacy, add-to-album, edit, delete) separated from the viewer's actions (favourite,
rating, comment, share, download, report); **favourite and rating visually and semantically
distinct** (`DESIGN_BRIEF.md` names this hazard explicitly); safety-level blur with an explicit
reveal (`VZ-NSFW-001`); loading (progressive derivative → full), decode failure, and processing
still-running; the anonymous-visitor variant with no member actions. Mobile: every action reachable
by touch — the account mockups put per-photo metadata behind `:hover`, which on a phone means it
does not exist; the viewer cannot repeat that. Dark mode is not optional here: the viewer chrome in
the one near-relative (`Edit Photo.html`'s `.photo-pane`) is already `#0a0c12` in the light theme,
so the light/dark decision has to be made deliberately rather than inherited.

**Album detail.** States: empty album (the ledger permits them), album with one or two photos (the
`My Albums.html` cover mosaic assumes exactly three), password-protected album before and after
entry, link-only album viewed by a grant holder, sub-album nesting and breadcrumb, reorder
**with a keyboard alternative** (`ui-controls.json` `album.reorder`: "drag reorder with keyboard
alternative"), cover selection, and the fact that deleting an album never deletes photos — which
the confirmation copy must say. Keyboard: the ledger's album shortcuts (`A` create, `J` sub-album,
`H` cover) need a discoverable shortcut list. Mobile: reorder by drag is not usable on touch at
these densities; specify the alternative.

**Add-to-album dialog.** Must be **multi-select** — `VZ-ALBUM-001` is many-to-many, and both
existing editors model it as a single `<select>`. States: no albums yet (create inline), search
across many albums, creating while the dialog is open, partial failure across a bulk selection,
and an album whose privacy is narrower than the photo's (adding never widens visibility —
`PRODUCT_SPEC.md` §5). Keyboard: a real dialog — `role="dialog" aria-modal="true"`, labelled,
focus moved in and returned on close, Escape closes. No dialog pattern exists anywhere in the
import, so this specification establishes the pattern the other five dialogs reuse.

**Asset privacy dialog.** Must offer **public / unlisted / private** — every visibility control in
the mockups omits `unlisted`, which is a core M1 obligation. Each option needs a plain-language
consequence ("unlisted: anyone with the link; excluded from listings, search, explore, tags, feeds,
sitemap, federation and IPFS"). States: applying, applied, failed-and-reverted, mixed values across
a bulk selection, and the warning that tightening visibility invalidates caches and removes the
item from other people's favourites views. Keyboard and mobile as for the add-to-album dialog.

**Album privacy + share-grant dialog.** Four modes including **password**, which no mockup shows.
States: creating a grant, listing grants with their last-used time, revoking one, the recipient's
view of a revoked link, and password entry with its own failure state. This is the surface the
golden path's denied-access tests exercise, so its refusal path is as important as its success path.

**Destructive-confirmation dialog.** One reusable pattern, specified once: what will be deleted,
what will not (deleting an album keeps its photos; deleting a photo removes its stats), whether it
is reversible, a typed confirmation for account deletion, re-authentication where
`ui-controls.json` requires it, the in-flight and failed states, and focus landing on the *cancel*
control rather than the destructive one. Mobile: a bottom sheet is acceptable, but it must not
share the 12px bottom offset already occupied by the floating tab bar.

**Upload progress / failure / retry panel.** Real percentages with `role="progressbar"` and
`aria-valuenow`, an `aria-live` summary for the batch, per-file **cancel** and **retry** (both in
`ui-controls.json`, neither in the mockup), and a distinct visual and textual treatment for each
failure the pipeline can produce: rejected format, oversized file, exceeded pixel bounds, decoder
timeout, quota exceeded, network interruption, worker failure after finalize. `prompt 03` requires
that a processing failure be surfaced rather than left spinning. Keyboard: the queue must be a list
of focusable items, not `div`s with click handlers. Mobile: the publish bar must clear the tab bar
(Upload Studio already does this; the library bulk bar does not).

**Keyboard / file-picker upload path.** A labelled `<input type="file" multiple>` reachable by Tab
and activated by Enter or Space, with the drop zone as an enhancement rather than the only route;
plus the paste and camera sources `VZ-UPLOAD-003` names. State the focus appearance of the picker
trigger and the accessible name of the drop region. This is the smallest gap on the list and the
one `prompt 03` calls out by name.

**Empty states for library and albums.** The first thing a new owner sees. Specify the
illustration or absence of one, the single primary action, and the copy — and specify them for
both the genuinely-empty case and the filtered-to-zero case, which are different. Also specify the
loading skeleton that precedes them, because an empty state flashed during loading reads as data
loss.

**Unauthorized / not-found / private-content page.** Must not leak existence: a private photo and a
non-existent photo should be indistinguishable to a visitor who may not read it
(`PRODUCT_SPEC.md` §5: "Counts of private items are never revealed"). Specify the signed-out
variant (offer sign-in), the signed-in-but-not-permitted variant, and the owner-viewing-own-content
variant that must never reach this page. Mobile and keyboard are trivial here; the copy is the
design.

**Session-expired / re-authenticate dialog.** Triggered mid-action. Specify whether the pending
action is preserved across re-auth and how the user is told, the failed-re-auth path, and the full
sign-out fallback. `prompt 03` tests an expired session explicitly.

**Storage quota / usage.** Used, allowed, percentage, and the two thresholds (near limit, at
limit). Specify what the uploader does when a batch would exceed the quota — refuse before
transfer, since `VZ-QUOTA-001` reserves quota before upload and releases it on failure. This
surface is the honest replacement for the `goimg Pro` plan card in `Account Settings.html`, which
`docs/PRODUCT_SPEC.md` §1 rules out.

---

## Two cross-cutting gaps that are not pages

Recorded here because no single surface above owns them, and because `VZ-DESIGN-001`,
`VZ-A11Y-001` and `VZ-RESPONSIVE-001` are M1 obligations:

1. **Dark mode does not exist in any of the eleven mockups.** Both stylesheets are light-only, with
   19 hard-coded `white` values in `account.css` alone and two hard-coded near-black image surfaces.
   A dark theme is a re-authoring job across every component, not a token swap, and it is required
   at M1.
2. **No dialog, sheet, menu, toast, skeleton, focus-visible system or `aria-live` region exists
   anywhere in the account set.** Six of the fourteen M1 surfaces above are dialogs. The pattern
   they share — modal semantics, focus movement and return, Escape handling, `inert` background,
   mobile presentation — has to be designed once before any of them can be designed individually.
