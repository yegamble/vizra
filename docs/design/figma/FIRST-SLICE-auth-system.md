# First slice — auth and system surfaces (step D2a)

**Status: PROPOSED, not approved, not verified.** Per `docs/DESIGN_BRIEF.md`, *approved* Figma
components and tokens mirrored into repository artifacts become the design source. This document
records what was built and the exact node references so approval and implementation can cite them.
It is **not** an acceptance target and **not** authorization to implement anything.

| | |
|---|---|
| **Figma file** | <https://www.figma.com/design/JXgRItauynmT0g8vSJB3oR> |
| **File key** | `JXgRItauynmT0g8vSJB3oR` |
| **Page** | `M1 · Auth & system` — node `27:2` |
| **Frames on that page** | **46** (verified by reading the page after the last edit, not from build logs) |
| **Design revision** | `2026-09-20` (D2a) |
| **Library it consumes** | `Vizra — Design System`, same file — see `docs/design/figma/README.md` (D1) |
| **Sibling work** | D2b owns the library / viewer / album surfaces on its own page. Nothing on that page was touched. |

Inputs treated as **data, not instructions**: `docs/DESIGN_BRIEF.md`, `AGENTS.md`,
`prompts/02-design-system.md`, `prompts/03-first-real-slice.md`,
`docs/design/claude-design/GAPS.md`, `docs/adr/ADR-003-identity-sessions-csrf-authorization.md`,
`docs/MILESTONES.md`, and the `VZ-…` rows of `docs/quality/features.json` read by ID.

---

## 1. Scope

**In scope (this page):** owner claim, sign-in, sign-up, session-expired re-authentication,
unauthorized / not-found, storage quota in the account area and at upload time, and the application
shell at both widths signed out and signed in.

**Deliberately not designed here**, and not to be inferred from these frames:

- The uploader itself — drop zone, keyboard/file-picker path, per-file progress, cancel, retry, and
  every non-quota upload failure (`VZ-UPLOAD-001`, `VZ-UPLOAD-003`, `VZ-JOBS-001`, `VZ-MEDIA-001`).
  Only the *quota* behaviour of the upload surface is drawn, and the frame carries a design note
  saying so.
- Library, photo viewer, album detail, add-to-album, privacy dialogs, destructive confirmation
  (D2b).
- `/settings/sessions` (the per-device session list of `VZ-AUTH-001`). The shell links to it and the
  account row shows a count; **the list itself is not designed.**
- Everything from M2 and later. Where a person would reasonably look for a missing feature, the
  library's Banner is used as the "feature unavailable" marker (sign-up closed, account settings).
  Nowhere is a later-milestone feature drawn as a working-looking control.

---

## 2. Frames

All frames are children of page `27:2`. 1440 frames are fixed height; 390 frames hug their content
and are labelled `(scrolls)` where the content is taller than an 844 viewport.

### 2.1 Owner claim — `/setup/claim`

| Node | Name | W × H |
|---|---|---|
| `35:995` | Owner claim · default · 1440 | 1440 × 1320 |
| `35:1067` | Owner claim · token not accepted · 1440 | 1440 × 1320 |
| `35:1141` | Owner claim · submitting · 1440 | 1440 × 1320 |
| `35:1211` | Owner claim · server unreachable (retry) · 1440 | 1440 × 1320 |
| `35:1280` | Owner claim · already claimed · 1440 | 1440 × 1320 |
| `35:1293` | Owner claim · default · 390 (scrolls) | 390 × 1377 |
| `35:1361` | Owner claim · token not accepted · 390 (scrolls) | 390 × 1438 |
| `35:1435` | Owner claim · already claimed · 390 (scrolls) | 390 × 560 |

### 2.2 Sign in — `/login`

| Node | Name | W × H |
|---|---|---|
| `37:301` | Sign in · default · 1440 | 1440 × 1120 |
| `37:350` | Sign in · field error (empty identifier) · 1440 | 1440 × 1120 |
| `37:410` | Sign in · wrong credentials (enumeration-safe) · 1440 | 1440 × 1120 |
| `37:465` | Sign in · rate limited · 1440 | 1440 × 1120 |
| `37:528` | Sign in · submitting · 1440 | 1440 × 1120 |
| `37:574` | Sign in · offline, retry · 1440 | 1440 × 1120 |
| `37:632` | Sign in · default · 1440 · **DARK** | 1440 × 1120 |
| `37:677` | Sign in · default · 390 (scrolls) | 390 × 723 |
| `37:722` | Sign in · wrong credentials · 390 (scrolls) | 390 × 880 |
| `37:777` | Sign in · default · 390 · **DARK** (scrolls) | 390 × 723 |

### 2.3 Sign up — `/signup`

| Node | Name | W × H |
|---|---|---|
| `38:546` | Sign up · registration open · 1440 | 1440 × 1120 |
| `38:600` | Sign up · field errors · 1440 | 1440 × 1120 |
| `38:670` | Sign up · registration closed · 1440 | 1440 × 1120 |
| `38:691` | Sign up · registration open · 390 (scrolls) | 390 × 821 |
| `38:741` | Sign up · registration closed · 390 (scrolls) | 390 × 649 |

### 2.4 Session-expired re-authentication

| Node | Name | W × H |
|---|---|---|
| `39:1707` | Session expired · re-authenticate in place · 1440 | 1440 × 1000 |
| `39:1789` | Session expired · re-auth failed · 1440 | 1440 × 1000 |
| `39:1876` | Session expired · bottom sheet · 390 | 390 × 844 |

### 2.5 Unauthorized and not found

| Node | Name | W × H |
|---|---|---|
| `40:986` | Not found (404) · signed out · 1440 — the page a visitor gets for a private photo | 1440 × 900 |
| `40:1029` | Not found (404) · signed in · 1440 | 1440 × 900 |
| `40:1065` | Forbidden (403) · signed in · 1440 | 1440 × 900 |
| `40:1101` | Not found (404) · signed out · 390 | 390 × 844 |
| `40:1132` | Forbidden (403) · signed in · 390 | 390 × 844 |

### 2.6 Storage quota

| Node | Name | W × H |
|---|---|---|
| `42:1012` | Storage quota · account area · normal · 1440 | 1440 × 1100 |
| `42:1078` | Storage quota · account area · near limit · 1440 | 1440 × 1100 |
| `42:1159` | Storage quota · account area · full · 1440 | 1440 × 1100 |
| `42:1238` | Storage quota · refused at upload time · 1440 | 1440 × 1120 |
| `42:1325` | Storage quota · account area · near limit · 390 (scrolls) | 390 × 1106 |
| `42:1450` | Storage quota · refused at upload time · 390 (scrolls) | 390 × 1287 |

### 2.7 Application shell

| Node | Name | W × H |
|---|---|---|
| `43:2982` | Shell · signed out · 1440 | 1440 × 900 |
| `43:3000` | Shell · signed in · account · 1440 | 1440 × 900 |
| `43:3061` | Shell · signed in · account menu open · 1440 | 1440 × 900 |
| `43:3169` | Shell · signed in · account · 1440 · **DARK** | 1440 × 900 |
| `43:3230` | Shell · signed in · offline with retry · 1440 | 1440 × 900 |
| `43:3307` | Shell · signed out · 390 (no tab bar at M1) | 390 × 844 |
| `43:3320` | Shell · signed in · account · 390 | 390 × 844 |
| `43:3404` | Shell · signed in · account · 390 · **DARK** | 390 × 844 |
| `43:3488` | Shell · signed in · keyboard focus (skip link + row) · 390 | 390 × 844 |

---

## 3. Control matrix

One row per interactive control. **Action IDs are proposals** for `docs/quality/ui-controls.json`
(`VZ-CONTROLS-001`); none of them exists in that file yet. **"NO LEDGER ID"** means exactly that —
no ledger entry was invented. API paths are quoted from the `surfaces.api` field of the named ledger
entry; where no path is quoted, none is defined yet.

### 3.1 Owner claim

| Control | Action ID (proposed) | Ledger ID | Role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Claim token field | `setup.claim.token` | VZ-INSTALL-003 | Anonymous, instance unclaimed only | Value accepted for submit | One refusal message covering mistyped / used / superseded; value preserved | None until submit |
| Username field | `setup.claim.username` | VZ-INSTALL-003, VZ-AUTH-001 | same | — | Inline error, value preserved | `users` row on submit |
| Email field | `setup.claim.email` | VZ-INSTALL-003, VZ-AUTH-001 | same | — | Inline error, value preserved | `users` row on submit; **no mail is sent at M1** (VZ-EMAIL-001 is M2) |
| Password field | `setup.claim.password` | VZ-INSTALL-003 | same | — | Inline error; field cleared on server refusal | argon2id hash per ADR-003 |
| Show password | `setup.claim.password.reveal` | **NO LEDGER ID** | same | Characters shown, button label becomes "Hide password" | — | Client only, never persisted |
| Confirm password | `setup.claim.password_confirm` | VZ-INSTALL-003 | same | — | Inline error "Both passwords must match" | Not stored |
| **Create owner account** | `setup.claim.submit` | VZ-INSTALL-003 | Anonymous, unclaimed | `POST /api/v1/setup/claim-owner` → owner row + session cookie → redirect to library | 4xx → single refusal banner, token + username + email preserved, passwords cleared | Owner `users` row, redeemed token hash. **Atomic exactly-once**: two concurrent claimers yield one owner; the loser gets "already claimed" |
| Try again (offline) | `setup.claim.retry` | **NO LEDGER ID** (recovery path of VZ-INSTALL-003) | same | Resubmits the same form | Banner stays, everything preserved | Nothing written on a failed attempt |
| Go to sign in (already claimed) | `setup.claim.goto_signin` | **NO LEDGER ID** (navigation) | Anonymous, instance claimed | `/login` | — | None |

### 3.2 Sign in

| Control | Action ID (proposed) | Ledger ID | Role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Email or username | `auth.signin.identifier` | VZ-AUTH-001 | Anonymous | — | Inline error only for an empty/malformed field, never for "no such account" | None |
| Password | `auth.signin.password` | VZ-AUTH-001 | Anonymous | — | Never carries a field-level error on a credential mismatch | None |
| Show password | `auth.signin.password.reveal` | **NO LEDGER ID** | Anonymous | Characters shown | — | Client only |
| **Sign in** | `auth.signin.submit` | VZ-AUTH-001 | Anonymous | `POST /api/v1/auth/login` → `__Host-vizra_session` cookie (ADR-003) → returns to the page that sent them | 401 → one enumeration-safe summary; 429 → rate-limit banner + disabled form + countdown; network → offline banner | Server-side `sessions` row (SHA-256 of the id); 30-day rolling, 180-day absolute cap |
| Error summary | `auth.signin.error_summary` | VZ-A11Y-001 | Anonymous | Receives focus on submit; each line links to its field | — | None |
| Try again (offline) | `auth.signin.retry` | **NO LEDGER ID** | Anonymous | Resubmits | Banner stays | None |
| Create an account | `auth.signin.goto_signup` | VZ-AUTH-001 | Anonymous; **rendered only when registration is open** | `/signup` | — | None |

### 3.3 Sign up

| Control | Action ID (proposed) | Ledger ID | Role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Username | `auth.signup.username` | VZ-AUTH-001 | Anonymous, registration open | — | "That username is already taken" (usernames are public identifiers, so this is not an enumeration leak) | `users` row on submit |
| Email | `auth.signup.email` | VZ-AUTH-001 | same | — | See open question Q-D2a-3 — the duplicate-email message is **not settled** | `users` row on submit |
| Password | `auth.signup.password` | VZ-AUTH-001 | same | — | "Use at least 12 characters" | argon2id hash |
| Show password | `auth.signup.password.reveal` | **NO LEDGER ID** | same | Characters shown | — | Client only |
| **Create account** | `auth.signup.submit` | VZ-AUTH-001 | Anonymous, registration open | `POST /api/v1/auth/register` → account + session → library | 422 → error summary + field errors; 403 while the instance is unclaimed (VZ-INSTALL-003) | `users` row + `sessions` row |
| Sign in | `auth.signup.goto_signin` | **NO LEDGER ID** (navigation) | Anonymous | `/login` | — | None |
| Go to sign in (closed) | `auth.signup.closed.goto_signin` | **NO LEDGER ID** | Anonymous, registration closed | `/login` | — | None. **The closed state has no form at all** — there is nothing to submit and nothing to discard |

### 3.4 Session-expired re-authentication

| Control | Action ID (proposed) | Ledger ID | Role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Close (X) / Escape | `auth.reauth.dismiss` | **NO LEDGER ID** | Signed-out session on an already-rendered page | Dialog closes, focus returns to the control that was in use, a persistent "You are signed out" banner replaces it | — | Nothing; the pending action stays queued and unsent |
| Not you? | `auth.reauth.switch_account` | **NO LEDGER ID** | same | Full sign-out then `/login` | — | Destroys the stale session row |
| Password | `auth.reauth.password` | VZ-AUTH-001 | same | — | Field error + banner, attempts counted | None |
| Show password | `auth.reauth.password.reveal` | **NO LEDGER ID** | same | Characters shown | — | Client only |
| **Sign in and continue** | `auth.reauth.submit` | VZ-AUTH-001 | same | `POST /api/v1/auth/login` → new session → **the pending action is resubmitted automatically** | Wrong password → banner + field error + remaining-attempt count; after 3 more → full sign-out | New `sessions` row. The pending action persists only once it is resubmitted and succeeds |
| Sign out | `auth.reauth.signout` | VZ-AUTH-001 | same | `POST /api/v1/auth/logout` → `/login` | — | Session row removed; the pending action is discarded |

### 3.5 Unauthorized / not found

| Control | Action ID (proposed) | Ledger ID | Role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Sign in (on 404, signed out) | `error.404.goto_signin` | **NO LEDGER ID** | Anonymous | `/login` with a return address | — | None. Shown on **every** 404 for a signed-out visitor, so its presence is not a hint that anything exists |
| Go to your library (404/403, signed in) | `error.404.goto_library`, `error.403.goto_library` | VZ-LIBRARY-001 (destination) | Any signed-in role | `/library` | — | None |

### 3.6 Storage quota

| Control | Action ID (proposed) | Ledger ID | Role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Storage meter | `settings.storage.meter` | VZ-QUOTA-001 | Signed in, own quota only | `GET /api/v1/me/quota` → used / allowed / free | Error state with retry; never a silent zero | Read-only |
| Manage your photos | `settings.storage.goto_library` | VZ-LIBRARY-001 (destination) | Signed in | `/library` | — | None |
| Go to upload | `settings.storage.goto_upload` | VZ-UPLOAD-001 (destination) | Signed in, quota not full | `/upload` | — | None |
| Free up space (upload) | `upload.quota.goto_storage` | VZ-QUOTA-001 | Signed in | `/settings/storage` | — | None |
| Choose different photos | `upload.quota.reselect` | VZ-UPLOAD-003 | Signed in | Re-opens the file picker with the selection cleared | — | None |
| Add photos (disabled at limit) | `upload.picker.open` | VZ-UPLOAD-003 | Signed in; **disabled** while the quota is full | Opens the file picker | — | None. Disabled with the reason stated in visible text beside it — never a silently dead control |

**Quota mechanism the design commits to** (from `VZ-QUOTA-001`): space is **reserved before any byte
is transferred**, so an over-quota batch is refused up front and a long upload never dies half way;
the reservation is released on failure or cancel; a retried upload is not charged twice.

### 3.7 Application shell

| Control | Action ID (proposed) | Ledger ID | Role / state | Success | Failure | Persistence |
|---|---|---|---|---|---|---|
| Skip to content | `shell.skip_link` | VZ-A11Y-001 | Everyone | First Tab stop; moves focus to `main#content` | — | None |
| Wordmark | `shell.home` | VZ-LIBRARY-001 signed in / **NO LEDGER ID** signed out | Everyone | `/library` signed in; `/login` signed out | — | None |
| Library | `shell.nav.library` | VZ-LIBRARY-001 | Signed in | `/library`, `aria-current="page"` when active | — | None |
| Albums | `shell.nav.albums` | VZ-ALBUM-001 | Signed in | `/albums` | — | None |
| Upload (icon-only, accessible name "Upload photos") | `shell.nav.upload` | VZ-UPLOAD-001 | Signed in | `/upload` | — | None |
| Account button (44 × 44) | `shell.account.menu` | **NO LEDGER ID** | Signed in | Opens the account menu, `aria-expanded` toggles | — | None |
| Menu · Account | `shell.menu.account` | **NO LEDGER ID** | Signed in | `/settings` | — | None |
| Menu · Storage | `shell.menu.storage` | VZ-QUOTA-001 | Signed in | `/settings/storage` | — | None |
| Menu · Sessions and devices | `shell.menu.sessions` | VZ-AUTH-001 | Signed in | `/settings/sessions` — **the list itself is not designed here** | — | None |
| Menu · Sign out | `shell.menu.signout`, `auth.signout` | VZ-AUTH-001 | Signed in | `POST /api/v1/auth/logout` → `/login` | Error toast, still signed in | Session row removed server-side; the cookie alone is never trusted |
| Sign in (signed out) | `shell.signin` | VZ-AUTH-001 | Anonymous | `/login` | — | None |
| Create account (signed out) | `shell.signup` | VZ-AUTH-001 | Anonymous; **absent when registration is closed** | `/signup` | — | None |
| Tab · Library / Albums / Upload / Account | `shell.tab.library`, `.albums`, `.upload`, `.account` | VZ-LIBRARY-001, VZ-ALBUM-001, VZ-UPLOAD-001, **NO LEDGER ID** | Signed in only | Navigates; selection shown by an indicator bar **plus** a weight and colour change | — | None |
| Account row · Storage | `settings.storage` | VZ-QUOTA-001 | Signed in | `/settings/storage` | — | None |
| Account row · Sessions and devices | `settings.sessions` | VZ-AUTH-001 | Signed in | `/settings/sessions` | — | None |
| Try again (offline) | `shell.offline.retry` | **NO LEDGER ID** | Everyone | Re-fetches | Banner stays | None |

**Destinations deliberately absent from the shell at M1**, because they do not exist yet and a dead
link is worse than an omission: search (`VZ-SEARCH-001`, M3), notifications (`VZ-NOTIFY-001`, M2),
explore (`VZ-EXPLORE-001`, M3), public profile (`VZ-PROFILE-001`, M2), admin console
(`VZ-ADMIN-001`, M2).

---

## 4. Interaction notes

### 4.1 Focus order

- Every auth page: skip link (where a shell is present) → wordmark → error summary, *when one is
  present* → fields in visual order → primary submit → secondary links. There is one `<h1>` per
  page.
- The error summary is a real focus target (`tabindex="-1"`), receives focus on a failed submit, and
  is drawn with the library's focus ring in frames `35:1067`, `37:350`, `37:410`, `37:465`,
  `37:574`, `38:600`. Each bullet is a link to the field it names.
- Focus ring is the library rule without exception: `outline: 2px solid var(--vz-focus-ring);
  outline-offset: 2px` (6.36:1 light / 7.70:1 dark against the page — D1 §4). Modelled in Figma as a
  2px `color/focus-ring` stroke with `strokeAlign: OUTSIDE` on a wrapper carrying 2px of transparent
  padding.
- The skip link is first in DOM order on both widths. At 1440 it is drawn visible (matching the
  library's own TopNav documentation); at 390 it is hidden until focused — frame `43:3488` shows the
  focused state. It must not be obscured by the sticky bar (WCAG 2.4.11).

### 4.2 Error announcement

- Field errors: `aria-invalid` on the control, message linked by `aria-describedby`, an
  `icon/CircleAlert` **plus** text — never colour alone.
- Submit-time errors: the summary is rendered into an **assertive** live region and takes focus.
- In-flight status ("Signing in", "Creating the owner account") is a **polite** live region. The
  button sets `aria-busy` and keeps its accessible name stable.
- A quota threshold crossed during a session is announced politely; it is never signalled by colour
  alone — the Meter always carries an icon and a sentence.

### 4.3 Autocomplete (WCAG 3.3.8)

`username` on the sign-in identifier and the claim/sign-up username; `email` on email fields;
`current-password` on sign-in and re-authentication; `new-password` on claim and sign-up and on the
confirm field. No CAPTCHA, no puzzle, no cognitive-function test anywhere in this set.

### 4.4 Dialogs

- Re-authentication uses `role="dialog" aria-modal="true"`, labelled by its title, background
  `inert`, focus trapped, Escape closes, focus **returned** to the invoking control on close.
- Initial focus lands on the **password field**, not on a button. The library's Dialog contract
  ("initial focus on Cancel") exists to keep focus off a destructive action; there is no destructive
  action here and the field is the thing to do.
- At 390 the dialog is a bottom sheet that covers the tab bar completely (frame `39:1876`). It does
  **not** share the tab bar's bottom offset, which `GAPS.md` calls out.

### 4.5 Reduced motion

`motion/fast|base|slow` exist as tokens; no easing curves were authored in D1 and none are proposed
here. Under `prefers-reduced-motion`: the button spinner becomes a static indicator with an
unchanged accessible name; the Meter fill does not animate; the bottom sheet appears without a slide.

### 4.6 200% zoom and 320px reflow

- 1440 frames put all content in a column of 480–720px, so at 200% zoom the column reflows into the
  390-style single column already drawn.
- 390 frames hug their content and have been audited for horizontal overflow (§9). **320px reflow
  and 200% browser zoom have not themselves been rendered or measured** — see §10.

### 4.7 Touch targets

Buttons are 40px tall inside a 44px focus/hit wrapper (library Button). The account button is 44 × 44.
Tab bar items are 80 × 56. Settings rows are ≥ 44 tall. All clear WCAG 2.5.8.

---

## 5. Copy deck

Every string drawn on the page. Strings are written to be honest about what this release can do.

### 5.1 Owner claim

| Key | Copy |
|---|---|
| `claim.eyebrow` | FIRST RUN |
| `claim.h1` | Claim this Vizra instance |
| `claim.lede` | This server has no owner yet. Paste the one-time claim token, then create the owner account. Until that is done every sign-up and sign-in path is refused. |
| `claim.help.title` | Where to find the token |
| `claim.help.body` | Run your log command against the api service and look for the line printed at start-up. The token is 64 hexadecimal characters and works exactly once. |
| `claim.token.label` | Claim token |
| `claim.token.help` | Printed once in the API log when the server starts, on a line beginning "owner claim token". It is never shown in a web page and never emailed. |
| `claim.section.owner` | Owner account |
| `claim.username.label` / `.help` | Username / 3 to 30 characters: letters, numbers, hyphen, underscore. You sign in with this. |
| `claim.email.label` / `.help` | Email address / Stored for later account recovery. This release does not send email yet, so nothing will be sent here. |
| `claim.password.label` / `.help` | Password / At least 12 characters. There is no password-reset path in this release — keep it in a password manager. |
| `claim.confirm.label` / `.help` | Confirm password / Type it again. |
| `claim.submit` | Create owner account |
| `claim.footnote` | Restarting the API before you finish mints a new token and invalidates this one. |
| `claim.error.title` | That claim token was not accepted |
| `claim.error.body` | It may have been mistyped, already used, or replaced when the API last restarted — the server cannot tell these apart. Read the newest claim-token line from the log and paste it again. Nothing has been created. |
| `claim.error.field` | This token is not valid. Paste the newest one from the server log. |
| `claim.submitting` | Creating owner account… |
| `claim.submitting.live` | Creating the owner account. |
| `claim.offline.title` / `.body` | We could not reach the server / The claim was not sent. Nothing has been created and everything you typed is still here. Check that the server is running, then try again. |
| `claim.offline.retry` | Try again |
| `claimed.h1` | This instance already has an owner |
| `claimed.body.1` | Vizra can be claimed only once, and it has been claimed on this server already. Nothing on this page will create a second owner. |
| `claimed.body.2` | If you are the owner, sign in. If you are not, ask the owner to create an account for you. |
| `claimed.cta` | Go to sign in |
| `claimed.footnote` | Check that you are pointing at the right server if this is unexpected. Vizra never mints a new claim token for an instance that already has users. |

**One refusal message, deliberately.** The server stores only the hash of the *current* token, so a
mistyped token, an already-redeemed token and a token superseded by a restart are indistinguishable
to it. Three different messages would be a lie and an oracle. One message covers all three.

### 5.2 Sign in

| Key | Copy |
|---|---|
| `signin.h1` / `.lede` | Sign in / Sign in to continue on this Vizra instance. |
| `signin.identifier.label` | Email or username |
| `signin.password.label` | Password |
| `signin.reveal` | Show password |
| `signin.session.note` | You stay signed in on this device for 30 days unless you sign out. You can revoke any device later from Account → Sessions. |
| `signin.submit` | Sign in |
| `signin.signup.prompt` / `.cta` | New to this instance? / Create an account |
| `signin.noreset` | No password reset in this release. If you are locked out, ask the person who runs this instance. |
| `signin.fielderror.title` / `.body` | There is a problem / • Enter your email address or username. |
| `signin.wrong.title` | We could not sign you in |
| `signin.wrong.body` | That email or username and password do not match. Check both and try again. We do not say which one was wrong, and we never say whether an account exists on this instance. |
| `signin.ratelimit.title` | Too many sign-in attempts |
| `signin.ratelimit.body` | Sign-in from this device is paused for 4 minutes 30 seconds. This happens whether or not the details were correct, so it reveals nothing about any account. The countdown continues if you leave this page. |
| `signin.ratelimit.button` | Try again in 4:30 |
| `signin.loading` / `.live` | Signing in… / Signing in. |
| `signin.offline.title` / `.body` | You appear to be offline / We could not reach this Vizra server, so you were not signed in and your password was not sent anywhere. Check your connection, then try again. |

### 5.3 Sign up

| Key | Copy |
|---|---|
| `signup.h1` / `.lede` | Create your account / Registration is open on this instance. |
| `signup.username.label` / `.help` | Username / 3 to 30 characters: letters, numbers, hyphen, underscore. It appears on the photos you publish. |
| `signup.email.label` / `.help` | Email address / Stored for account recovery. This release does not send email, so there is no verification step and no reset link yet. |
| `signup.password.label` / `.help` | Password / At least 12 characters. A passphrase of ordinary words is stronger than a short complicated one. |
| `signup.submit` | Create account |
| `signup.signin.prompt` / `.cta` | Already have an account? / Sign in |
| `signup.errors.title` / `.body` | There are 2 problems / • That username is already taken.  • Use a password of at least 12 characters. |
| `signup.username.taken` | That username is already taken. Try another. |
| `signup.password.short` | Use at least 12 characters. |
| `signupclosed.h1` | Registration is closed |
| `signupclosed.body` | The owner of this instance has turned off new accounts, so there is nothing to fill in here. If you were told you would be given an account, ask them to create one for you. |
| `signupclosed.banner.title` | Invitations and approval queues are not in this release |
| `signupclosed.banner.body` | An instance can only be open or closed at the moment. Invite-only sign-up and an approval queue are planned for a later release, so no request form is offered here — an offer we could not honour would be worse than none. |
| `signupclosed.cta` | Go to sign in |
| `signupclosed.footnote` | Already have an account? The sign-in page works whether or not registration is open. |

### 5.4 Session-expired re-authentication

| Key | Copy |
|---|---|
| `reauth.title` | Your session expired |
| `reauth.body` | You were signed out because this session reached its 30-day limit. Nothing was lost: the change you were making has not been saved, and Vizra will submit it again as soon as you are signed in. |
| `reauth.identity.role` | Owner · mo@example.org |
| `reauth.switch` | Not you? |
| `reauth.password.help` | Initial focus lands here, not on a button. Enter submits. |
| `reauth.signout` / `.submit` | Sign out / Sign in and continue |
| `reauth.escape` | Escape closes this dialog and returns focus to the control you were using; a persistent "You are signed out" banner then replaces it at the top of the page. Background content is inert while the dialog is open. |
| `reauth.failed.title` / `.body` | That password did not match / Try again. After 3 more attempts you will be signed out completely and returned to the sign-in page. |
| `reauth.failed.field` | That password did not match. Check it and try again. |

### 5.5 Not found and forbidden

| Key | Copy |
|---|---|
| `notfound.title` | We can't find that page |
| `notfound.body.anon` | The address may be wrong, the photo may have been removed, or it may not be shared with you. If you have an account on this instance, signing in may show more. |
| `notfound.body.auth` | The address may be wrong, the photo may have been removed, or it may not be shared with your account. Nothing has been changed. |
| `notfound.cta.anon` / `.auth` | Sign in / Go to your library |
| `forbidden.title` | You don't have permission to do that |
| `forbidden.body` | You are signed in, but this needs a different role on this instance. Nothing was changed. If you think that is wrong, ask the person who runs it. |
| `forbidden.cta` | Go to your library |

**Which one a visitor sees for a private photo: 404, always.** ADR-003 — "Private resources return
404 to non-viewers, hiding existence." The 404 page is byte-for-byte identical, with the same status
code and the same timing budget, for a private photo, a private album, a private derivative and a
photo that never existed. The offer to sign in appears on *every* 404 for a signed-out visitor, so it
is not a signal that something is there. Never add a count, an owner name, a thumbnail, a "this is
private" wording, or a "request access" control — each of them confirms existence.

**403 is reserved for cases where existence is not a secret:** (a) an action needing a higher role
than the account has, (b) a state-changing request refused by the same-origin / `Content-Type` check
in ADR-003, and (c) every sign-up and claim path while the instance is unclaimed (VZ-INSTALL-003).
The owner viewing their own content must never reach either page.

### 5.6 Storage quota

| Key | Copy |
|---|---|
| `quota.h1` / `.eyebrow` | Storage / ACCOUNT |
| `quota.meter.label` | Storage used |
| `quota.meter.value` | 12.4 GB of 20 GB |
| `quota.status.normal` | 62% used — 7.6 GB free. |
| `quota.status.near` | Nearly full — 1.8 GB free. A batch larger than 1.8 GB will be refused before any file is sent. |
| `quota.status.full` | Storage is full. Delete photos, or ask the instance owner to raise your quota. |
| `quota.rows` | Quota / Used / Free / Set by · Role default (member) |
| `quota.release` | Space is released when a photo is permanently deleted. |
| `quota.reserve.title` | Uploads are checked before any file is sent |
| `quota.reserve.body` | Vizra reserves the space a batch needs before it starts sending, so a long upload never fails half way through. If an upload fails or is cancelled the reservation is released, and a retry of the same upload is not charged twice. |
| `quota.near.title` / `.body` | You are close to your storage limit / 1.8 GB free of 20 GB. Delete photos you no longer need, or ask the person who runs this instance to raise your quota. Nothing has been hidden or deleted. |
| `quota.full.title` / `.body` | Your storage is full / New uploads are refused until you free space or the owner raises your quota. Everything you have already uploaded is untouched and still visible to the people you shared it with. |
| `quota.cta.library` / `.upload` | Manage your photos / Go to upload |
| `upload.refused.title` | This batch was not uploaded |
| `upload.refused.body` | You chose 18 photos (2.4 GB). No space is free in your 20 GB quota, so nothing was sent, nothing was processed, and nothing was counted against your quota. Your selection is still here. |
| `upload.file.status` | Not sent — no storage free |
| `upload.cta` | Free up space / Choose different photos / Add photos |
| `upload.disabled.why` | "Add photos" is switched off because your storage is full, not because it is broken. Free space or have your quota raised and it works again. |

### 5.7 Shell

| Key | Copy |
|---|---|
| `shell.skip` | Skip to content |
| `shell.wordmark` | Vizra |
| `shell.nav` | Library / Albums |
| `shell.signedout.cta` | Create account / Sign in |
| `shell.tabs` | Library / Albums / Upload / Account |
| `account.h1` / `.eyebrow` | Account / ACCOUNT |
| `account.rows` | Storage · 12.4 GB of 20 GB / Sessions and devices · 3 signed in / Sign out |
| `account.unavailable.title` | Most account settings are not in this release |
| `account.unavailable.body` | Profile, password change, two-factor sign-in, notification and privacy settings, blocked accounts and account deletion all arrive after this release. They are left out rather than shown as controls that would not work. |
| `shell.menu.identity` | mo · Owner · mo@example.org |
| `shell.offline.title` / `.body` | You are offline / Vizra cannot reach this server. What you can see was loaded earlier and may be out of date. Nothing you change now will be saved, so wait until the connection is back. |
| `shell.offline.retry` | Try again |

---

## 6. Library additions

All additive. **No existing component was renamed, restructured or removed.** Every addition carries
a written Figma `description` with its accessibility and usage contract, in the library's own style.

| Addition | Node | Type | Variants | Library page | Why |
|---|---|---|---|---|---|
| `TopNav / M1` | `30:770` | COMPONENT_SET | `State` = Signed out \| Signed in | Navigation (`4:28`) | The library's `TopNav` (`15:74`) hard-codes a search field and a notifications bell. Search is `VZ-SEARCH-001` (M3) and notifications are `VZ-NOTIFY-001` (M2); neither exists at M1, and an instance cannot remove a child from a component. Built by **cloning** `TopNav`, so every variable binding is inherited exactly. |
| `AppBar / M1` | `30:814` | COMPONENT_SET | `State` = Signed out \| Signed in | Navigation (`4:28`) | The library had no 390 top bar at all. Same omissions; skip link present in DOM order and hidden until focused. |
| `TabBar / M1` | `30:935` | COMPONENT_SET | `Selected` = Library \| Albums \| Upload \| Account | Navigation (`4:28`) | The library's `TabBar` (`15:32`) carries Home / Search / Upload / You. At M1 the signed-in home **is** the library, there is no search, and there is no public profile. Built by cloning `TabBar` and re-pointing its four `TabBar Item` instances. |
| `Meter` | `31:86` | COMPONENT_SET | `Level` = Normal \| Near limit \| At limit | Feedback (`4:30`) | `VZ-QUOTA-001` needs a determinate usage indicator; D1 §10.4 records that no progress/meter primitive was built. Implement as `role="meter"` with `aria-valuenow/min/max/valuetext`; `role="progressbar"` is for an operation in flight, not a standing quantity. The track keeps a 1px `color/line` boundary so the empty portion stays ≥ 3:1. |
| `icon/Images` | `28:585` | COMPONENT | — | Icons (`4:32`) | Albums. Distinct from `icon/Image` (one photo) and from `icon/FolderPlus` (the add-to-album *action*). |
| `icon/HardDrive` | `28:595` | COMPONENT | — | Icons (`4:32`) | Storage and quota. |
| `icon/LogOut` | `28:605` | COMPONENT | — | Icons (`4:32`) | Sign out. |

The three icons follow D1 §7 exactly: drawn on Lucide's 24px grid with a 2px round-cap stroke bound
to `color/ink`, and they are **hand-drawn stand-ins, not traced from the package**. Proposed
`lucide-react` export names — `Images`, `HardDrive`, `LogOut` — are **unverified**, like the other
37, and must be checked against the pinned package before the typed registry ships.

### 6.1 A library gap this work hit and did *not* close

The library's `Dialog` (`16:43`) has a fixed body that can hold a description and nothing else, and a
Figma instance cannot take new children. The re-authentication dialog therefore had to be
**composed** from a container frame following the Dialog recipe (`color/bg-elevated`, `radius/lg`,
`elevation/3`, header / body / footer) with library instances inside it. It is bound to variables
throughout and contains no hard-coded colour, but it is not an instance of `Dialog`. A
`Dialog / Form` variant with a body slot should be added when the library is approved — D2b's
add-to-album, privacy and share dialogs will hit the same wall.

`Menu` / `Popover` remains unbuilt (D1 §10.4). The account menu in frame `43:3061` is composed
ad hoc from a variable-bound popover frame and row frames.

---

## 7. Design decisions taken here that need owner ratification

These were decided in order to draw the screens. None is settled by an existing ADR or ledger entry.

1. **Q-D2a-1 — One refusal message for a bad claim token.** Mistyped, already used and superseded by
   a restart are indistinguishable to the server and are shown as one message. Confirm that no more
   specific diagnostic is wanted (it would be an oracle).
2. **Q-D2a-2 — "Already claimed" status code.** The frame is drawn for a refusal; the design assumes
   **409 Conflict** for a claim attempt against a claimed instance, while `VZ-INSTALL-003` only fixes
   403 for *sign-up paths while unclaimed*. ADR-003 does not settle it.
3. **Q-D2a-3 — Duplicate email on sign-up.** With no email verification at M1 (`VZ-AUTH-002` is M2),
   sign-up cannot be made enumeration-safe without either allowing duplicate emails or adding a
   verification step. The frames therefore show a **username**-taken error and leave the duplicate-
   email message open. Owner decision needed: allow duplicate emails at M1, accept the enumeration
   surface, or pull `VZ-AUTH-002` forward.
4. **Q-D2a-4 — No password recovery at M1.** `VZ-AUTH-002` (reset) and `VZ-ADMIN-USERS-001` (admin
   reset) are both M2, so a member who forgets their password at M1 is locked out with no path back.
   The copy says so plainly rather than offering a link that does not exist. Confirm this is
   acceptable for the golden path, or pull one of them forward.
5. **Q-D2a-5 — Pending action preserved across re-authentication.** The design promises that the
   action interrupted by session expiry is resubmitted automatically after re-auth. That is an
   implementation commitment with real cost. Confirm, or the copy must change.
6. **Q-D2a-6 — Near-limit quota threshold.** Drawn at 90%. No document fixes a number. Confirm 90%,
   or set it (and say whether it is an instance setting).
7. **Q-D2a-7 — Signed-out shell has no tab bar at 390.** At M1 the only surface a signed-out visitor
   can reach is a public or unlisted photo page; four tabs they cannot use would be worse than none.
   Confirm.
8. **Q-D2a-8 — "Account" rather than "You" / profile.** The fourth tab goes to `/settings`, not to a
   public profile (`VZ-PROFILE-001` is M2). Confirm the label.
9. **Q-D2a-9 — Session note wording "30 days".** Taken from ADR-003 (30-day rolling, 180-day absolute
   cap). Confirm this is the right thing to tell a member, and whether the 180-day cap should be
   mentioned too.
10. **Q-D2a-10 — No live password-strength meter.** A client-side estimator (e.g. zxcvbn) is a
    dependency with no ledger entry, so the design uses a stated minimum instead. Confirm.

---

## 8. What each M1 requirement this page touches still needs elsewhere

`VZ-A11Y-001`, `VZ-RESPONSIVE-001` and `VZ-CONTROLS-001` are **not** satisfied by this document.
They require axe results on running routes, a screenshot matrix from a production build inspected by
a human, a recorded manual keyboard/screen-reader review, and `docs/quality/ui-controls.json` rows
audited against the running application. A Figma page is an input to those, never evidence for them.

---

## 9. Verification performed

Every frame and component named above was created by a `use_figma` call that returned success and a
node id, and the inventory in §2 and §6 was produced by **re-reading the live file after the last
edit**, not from build logs.

Screenshots were taken with `get_screenshot` and inspected. Defects found by looking and then fixed:

1. **Helper text clipped on every text field.** The library `TextField` hugs its `helper` frame, so
   long helper copy ran past the card edge. Repaired on **30** instances by setting `helper` and
   `helper-text` to `FILL`.
2. **Owner-claim 1440 frames too short**, clipping the footnote. Resized 1100 → 1320.
3. **Primary submit buttons rendered at natural width** inside a full-width instance root, so the
   visible pill did not match the hit area. Repaired by filling the Button's inner `surface` frame
   and centring its label.
4. **Disabled field values were drawn in `color/ink`,** making a disabled field look enabled.
   Repaired on **9** instances to `color/ink-3`.
5. **Skip link did not become visible** in the 390 keyboard-focus frame: `findOne` had skipped
   invisible instance children. Repaired, and the focus ring applied.
6. **Horizontal overflow at 390** on the upload action row (three buttons, ~465px of content in a
   358px column). Repaired by allowing action rows to wrap; **22** rows were made wrappable.

Automated audits run over the whole page after the fixes:

| Audit | Result |
|---|---|
| Horizontal overflow — every non-absolute descendant against its frame's box | **0 offenders** across all 46 frames |
| Vertical clipping — top-level children past a fixed frame's bottom | **0 offenders** |
| Collapsed auto-layout — any auto-layout frame under 4px in either axis | **0** |
| Unbound solid fills on authored (non-instance) nodes | **0** — every colour resolves through a `Color` or `Primitives` variable |

Dark mode is applied by setting the `Color` collection to its `Dark` mode on the frame
(`setExplicitVariableModeForCollection`), which is how Figma models theming; frames `37:632`,
`37:777`, `43:3169`, `43:3404` were rendered and inspected in that mode.

---

## 10. What is unfinished or unverified

Recorded honestly. None of this is hidden behind a success summary.

1. **Nothing here is approved or reviewed.** Single-pass build by one agent. `AGENTS.md` requires
   independent review; the `vizra-design` seat has not seen it and the owner has not approved it.
   Status is **PROPOSED**.
2. **200% zoom and 320px reflow were not rendered or measured.** §4.6 states an expectation only.
   `VZ-RESPONSIVE-001` and `VZ-A11Y-001` need real captures from a running build.
3. **Contrast was not re-measured for this page.** Every colour resolves through a D1 token whose
   pairs were measured in D1 §4, and no new colour pair was introduced — but the specific
   combinations used here (for example `color/danger-ink` on `color/bg` inside a file row, and
   `color/ink-3` on `color/bg-tint` in the identity row) were **not** individually recomputed.
4. **The three new icon names are unverified**, like the 37 from D1, and the glyphs are stand-ins.
5. **`/settings/sessions` is not designed**, although the shell links to it and the account row shows
   "3 signed in". `VZ-AUTH-001` requires that list. It belongs to this area and is a gap.
6. **The full uploader is not designed** — see §1. Frame `42:1238`/`42:1450` covers quota only and
   says so on the canvas.
7. **The "dismissed re-auth" state is described in §4.4 but not drawn** — the persistent
   "You are signed out" banner that replaces the dialog after Escape has no frame.
8. **No motion specification.** Tokens exist; curves, durations per component and reduced-motion
   variants were not authored in D1 and were not added here.
9. **Placeholder content only.** No photographs anywhere on this page; the content area of the shell
   frames is a dashed marker, not a design. Names, sizes and counts in the frames are fabricated
   sample data.
10. **Screenshots are not archived in the repository.** They were inspected in-session through
    short-lived `get_screenshot` URLs. If the war room needs durable visual evidence under
    `docs/evidence/`, it must be re-captured and committed.
11. **The library is still a draft, not published.** These frames use local components in the same
    file. If D2b or implementation work moves to another file, the library must be published first.
12. **Action IDs in §3 do not exist yet** in `docs/quality/ui-controls.json`. They are proposals for
    `VZ-CONTROLS-001`, and adding them is a separate change to that file.
