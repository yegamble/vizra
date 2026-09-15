# Chevereto V4 — Official Admin & User Manual evidence file

**Purpose:** source-of-truth capture of the two official Chevereto V4 manuals, for Vizra functional-union planning.
**Observation date (all pages):** 2026-09-15
**Sources (official Chevereto domains only):**

- Admin manual — `https://v4-admin.chevereto.com/`
- User manual — `https://v4-user.chevereto.com/`

## Method & provenance

- Retrieved over HTTPS with `curl -L`, full rendered HTML captured to disk, then converted to text. Exact wording preserved; all quotes below are verbatim from the pages.
- Both sites are VuePress 1.9.10 static sites served from GitHub Pages. The sidebar is server-rendered, so the complete section list is extractable from the HTML.
- Enumeration was a breadth-first crawl of every internal link, not just the index sidebar. No page in either sidebar was skipped.
- **Nothing in this file comes from memory, from the Chevereto paid demo, or from private/proprietary source code.** The paid demo and the Chevereto source were NOT inspected. Failed fetches are recorded as FAILED and left empty.

### Build/version stamps

Neither manual prints a product version, a "Last updated" footer, or an "applies to" banner on any page. The only date evidence available is the HTTP `Last-Modified` header, which is uniform per site (i.e. it is the static-site deploy timestamp, not a per-page edit date):

| Manual | `Last-Modified` (uniform across all pages) | Pages sharing it |
|---|---|---|
| Admin | `Tue, 14 Jul 2026 13:01:05 GMT` | 39 / 39 |
| User | `Sun, 16 Aug 2026 14:55:41 GMT` | 34 / 34 |

The manuals self-describe only as "Chevereto V4":

- Admin home — "Documentation for administrators of Chevereto V4 based systems"
- User home — "Documentation for users of Chevereto V4 based systems"

### Edition (Free / Lite / Pro) — NOT PRESENT

**Critical for the functional-union goal:** a full-text search of both manuals for `Free`, `Lite`, `Pro`, `edition`, `license`, `premium`, `paid`, `subscription` returns **no edition gating whatsoever**. No page states that any setting or capability is restricted to a particular Chevereto edition. Every capability below is documented unconditionally.

The single scope restriction stated anywhere in either manual is a role restriction, not an edition restriction (Upload URL, see below).

## Fetch inventory

### Admin manual — 39 requested, 39 × HTTP 200, 0 FAILED

| HTTP | URL | `<title>` |
|---|---|---|
| 200 | https://v4-admin.chevereto.com/ | V4 Admin |
| 200 | https://v4-admin.chevereto.com/account/ | Account \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/dashboard/home.html | Home \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/dashboard/files.html | Files \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/dashboard/tags.html | Tags \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/dashboard/albums.html | Albums \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/dashboard/users.html | Users \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/dashboard/bulk-importer.html | Bulk importer \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/api.html | API \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/banners.html | Banners \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/categories.html | Categories \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/consent-screen.html | Consent screen \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/content.html | Content settings \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/cookie-compliance.html | Cookie compliance \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/email.html | Email \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/external-services.html | External services \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/file-uploads.html | File uploads \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/flood-protection.html | Flood protection \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/guest-api.html | Guest API \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/homepage.html | Homepage \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/ip-bans.html | IP bans \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/languages.html | Languages \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/listings.html | Listing settings \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/login-providers.html | Login providers \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/logo.html | Logo \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/pages.html | Pages \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/routing.html | Routing \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/semantics.html | Semantics \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/site-storage.html | Site storage \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/system.html | System \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/theme.html | Theme \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/tools.html | Tools \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/upload-plugin.html | Upload plugin \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/upload-storage.html | Upload storage \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/users.html | Users \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/watermarks.html | Watermarks \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/settings/website.html | Website settings \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/features/upload-storage.html | Upload storage \| V4 Admin |
| 200 | https://v4-admin.chevereto.com/features/login-providers.html | Login providers \| V4 Admin |

### User manual — 35 requested, 34 × HTTP 200, 1 FAILED

| HTTP | URL | `<title>` |
|---|---|---|
| 200 | https://v4-user.chevereto.com/ | V4 User |
| 200 | https://v4-user.chevereto.com/user/account/signup.html | Create Account \| V4 User |
| 200 | https://v4-user.chevereto.com/user/account/login.html | Login \| V4 User |
| 200 | https://v4-user.chevereto.com/user/account/password-forgot.html | Recover Password \| V4 User |
| 200 | https://v4-user.chevereto.com/user/profile/user-profile.html | User Profile \| V4 User |
| 200 | https://v4-user.chevereto.com/user/profile/notifications.html | Notifications \| V4 User |
| 200 | https://v4-user.chevereto.com/user/profile/color-palette.html | Color Palette \| V4 User |
| 200 | https://v4-user.chevereto.com/user/profile/albums.html | Albums \| V4 User |
| 200 | https://v4-user.chevereto.com/user/profile/liked.html | Liked \| V4 User |
| 200 | https://v4-user.chevereto.com/user/profile/following.html | Following \| V4 User |
| 200 | https://v4-user.chevereto.com/user/profile/followers.html | Followers \| V4 User |
| 200 | https://v4-user.chevereto.com/user/settings/account.html | Account \| V4 User |
| 200 | https://v4-user.chevereto.com/user/settings/profile.html | Profile \| V4 User |
| 200 | https://v4-user.chevereto.com/user/settings/password.html | Password \| V4 User |
| 200 | https://v4-user.chevereto.com/user/settings/security.html | Security \| V4 User |
| 200 | https://v4-user.chevereto.com/user/settings/api.html | API \| V4 User |
| 200 | https://v4-user.chevereto.com/features/upload/local.html | Upload local \| V4 User |
| 200 | https://v4-user.chevereto.com/features/upload/url.html | Upload URL \| V4 User |
| 200 | https://v4-user.chevereto.com/features/upload/formats.html | Formats \| V4 User |
| 200 | https://v4-user.chevereto.com/features/explore/menu.html | Explore Menu \| V4 User |
| 200 | https://v4-user.chevereto.com/features/explore/discovery.html | Discovery \| V4 User |
| 200 | https://v4-user.chevereto.com/features/explore/categories.html | Categories \| V4 User |
| 200 | https://v4-user.chevereto.com/features/explore/tags.html | Tags \| V4 User |
| 200 | https://v4-user.chevereto.com/features/explore/random.html | Random Mode \| V4 User |
| 200 | https://v4-user.chevereto.com/features/search/basic.html | Basic search \| V4 User |
| 200 | https://v4-user.chevereto.com/features/search/advanced.html | Advanced search \| V4 User |
| 200 | https://v4-user.chevereto.com/features/listings/content.html | Content Listings \| V4 User |
| 200 | https://v4-user.chevereto.com/features/listings/viewer.html | Viewer \| V4 User |
| 200 | https://v4-user.chevereto.com/features/listings/editing.html | Editing \| V4 User |
| 200 | https://v4-user.chevereto.com/features/listings/actions.html | Actions \| V4 User |
| 200 | https://v4-user.chevereto.com/features/content/album.html | Album \| V4 User |
| 200 | https://v4-user.chevereto.com/features/content/media.html | Media \| V4 User |
| 200 | https://v4-user.chevereto.com/integrations/sharex.html | ShareX \| V4 User |
| 200 | https://v4-user.chevereto.com/integrations/pup.html | Popup Upload Plugin \| V4 User |
| **404 FAILED** | https://v4-user.chevereto.com/features/explorer/explore.html | — (broken internal link discovered during crawl; NOT filled from memory) |

---

# ADMIN MANUAL — `https://v4-admin.chevereto.com/`

Headings below mirror the admin sidebar exactly and in sidebar order, so this can be reconciled section-by-section.

## Home (index)

- URL `https://v4-admin.chevereto.com/` · HTTP 200 · title `V4 Admin` · observed 2026-09-15
- Quote: "Welcome to the Chevereto V4 Admin Manual. This documentation covers everything you need to know about administrating a Chevereto-based system."
- Sidebar group "Home" contains one entry, "Links", pointing to Website / Docs / Releases (`chevereto.com`, `v4-docs.chevereto.com`, `releases.chevereto.com`). No settings content.

## Account

- URL `https://v4-admin.chevereto.com/account/` · HTTP 200 · title `Account | V4 Admin` · observed 2026-09-15
- Quote: "The account created on install is the **admin account**, which can can be modified. Additional administrators can be also added." *(sic — "can can")*
- **Roles named (as written):** `Administrator`, `manager role`. Quote: "Users with role **Administrator** can grant admin access to other users."
- Quote: "Grant admin access only to system administrators. If you need to grant moderation permissions use the **manager role**."
- Procedure controls as written: **User profile** → **Edit** → user role → **Save changes**.
- Edition restriction: none stated.

## Dashboard

### Dashboard › Home

- URL `https://v4-admin.chevereto.com/dashboard/home.html` · HTTP 200 · title `Home | V4 Admin` · observed 2026-09-15 · admin route `/dashboard`
- Quote: "The **Dashboard Homepage** provides a real-time overview of all activity and resource usage across your instance."
- **Chart metrics (as written):** Files, Disk, Users, Albums, Tags.
- **Time range buttons (as written):** `1W` Last 7 days · `1M` Last 30 days · `3M` Last 3 months · `6M` Last 6 months · `1Y` Last 12 months.
- Quote: "The chart toolbar also provides zoom-in, zoom-out, pan, and reset controls for closer inspection of any time range."
- **Totals (as written):** Files, Albums, Users, Tags, Disk used.
- Edition restriction: none stated. Defaults: none stated.

### Dashboard › Files

- URL `https://v4-admin.chevereto.com/dashboard/files.html` · HTTP 200 · title `Files | V4 Admin` · observed 2026-09-15 · admin route `/dashboard/files`
- Quote: "At **Dashboard Files** you can administer all the files uploaded to the system."
- **Sorting options (as written):** Most recent (stated default), Oldest, Most viewed, Most liked.
- **Per-file controls (as written):** Delete, Flag, Select. Quote (Flag): "Marks the file as safe or unsafe for content moderation".
- **Bulk actions + keys (as written):** Delete `Del` · Assign category `C` · Flag as safe `V` · Flag as unsafe `F` · Approve (no key, "—").
- **Selection keys (as written):** Select all `.` · Clear selection `Z`.
- Quote: "Approval actions are only shown when the system is configured to require upload moderation."
- **Moderation actions table (as written):** Flag as safe — "Clears any NSFW flag; content appears normally in listings"; Flag as unsafe — "Marks content as NSFW; visibility follows content settings"; Approve — "Publishes content held in the moderation queue"; Delete — "Permanently removes content from the system".
- Quote: "NSFW visibility in listings is controlled by Content settings ."
- Edition restriction: none stated.

### Dashboard › Tags

- URL `https://v4-admin.chevereto.com/dashboard/tags.html` · HTTP 200 · title `Tags | V4 Admin` · observed 2026-09-15 · admin route `/dashboard/tags`
- Quote: "Tags are created automatically when users apply them to files; they cannot be created from this page."
- Quote: "Each tag is a link to its public tag page at `/tag/{name}`, showing all files tagged with that label."
- **Sorting options (as written):** Most recent (stated default), Oldest, Most viewed, A-Z. *(Note: no "Most liked" here, unlike Files/Albums.)*
- Quote: "To edit or delete a tag, open it by clicking on it to go to the tag page, where those actions are available."
- Edition restriction: none stated.

### Dashboard › Albums

- URL `https://v4-admin.chevereto.com/dashboard/albums.html` · HTTP 200 · title `Albums | V4 Admin` · observed 2026-09-15 · admin route `/dashboard/albums`
- Quote: "It provides a full-screen grid listing of every album across all users, with tools to sort, browse, and bulk-manage content."
- Quote: "Each card shows the album cover image (or a placeholder when the album has no files), the album name, and the file count."
- **Sorting options (as written):** Most recent (stated default), Oldest, Most viewed, Most liked, A-Z.
- **Per-album controls (as written):** Delete ("confirmation required"), Select.
- **Bulk actions (as written):** Delete `Del`. **Selection keys:** Select all `.` · Clear selection `Z`. Quote: "Press `Z` to deselect everything."
- Quote: "Deleting an album removes the album record and all files it contains. This action cannot be undone."
- Quote (album view): "top-level buttons to edit album details, create a sub-album, delete the album, and share it."
- Edition restriction: none stated.

### Dashboard › Users

- URL `https://v4-admin.chevereto.com/dashboard/users.html` · HTTP 200 · title `Users | V4 Admin` · observed 2026-09-15 · admin route `/dashboard/users`
- **Listing sort options (as written):** "Top, Most recent, Oldest, Most viewed, Most liked, and AZ" via the **Top** dropdown.
- **Create user form fields (as written):** Role, Username, Email, Password. Quote (Role): "The user's permission level: User, Manager, or Administrator."
- **User edit route (as written):** `/dashboard/user/{id}`, reached via profile → **Settings**.
- **Account tab — read-only info (as written):** Username (with **Delete user** button), User ID ("Internal numeric ID and its short encoded form"), Images, Albums, Register date ("shown in local time and UTC"), IP Address with **Search** and **Ban** actions.
- **Account tab — editable settings (as written), with option values:**
  - **Status** — "Account state: Valid, Banned, Awaiting email, or Awaiting confirmation."
  - **Role** — "User, Manager, or Administrator."
  - **Username** — "(URL preview shown below the field)".
  - **Email address**
  - **Auto delete uploads** — "Automatically delete uploaded files after a set period, from 5 minutes up to 1 year." Quote: "Applies as the default for all uploads; can be overridden per upload."
  - **Keep EXIF data** — "Preserve EXIF metadata on upload."
  - **Automatic metadata tags** — "Assign the camera model as a tag on upload."
  - **Newsletter** — "Opt in or out of Chevereto news emails."
  - **Show not safe content** — "Whether the user sees not-safe content in listings from others."
  - **Language** — "Interface language for the account (supports 40+ locales)."
  - **Timezone** — "User timezone by region and city."
- **Profile tab** `/dashboard/user/{id}/profile` — Avatar, Privacy ("Toggle to make the profile and identity fully private"), Name, Website, Bio.
- **Password tab** `/dashboard/user/{id}/password` — Quote: "If the user has no password (e.g. registered via a login provider), a notice is shown."
- **Security tab** `/dashboard/user/{id}/security` — Quote: "A QR code is provided to scan with any TOTP authenticator app." Fields: **OTP**, **Submit**. *(Admin-side 2FA enable; no admin-side disable documented — see Gaps.)*
- **API tab** `/dashboard/user/{id}/api` — **API key** (masked, copy button), **Regen key**. Quote: "The key is only displayed in full once at generation time." Quote: "The tab also shows an example `curl` command for uploading files via the API."
- Edition restriction: none stated.

### Dashboard › Bulk importer

- URL `https://v4-admin.chevereto.com/dashboard/bulk-importer.html` · HTTP 200 · title `Bulk importer | V4 Admin` · observed 2026-09-15 · admin route `/dashboard/bulk-importer`
- Quote: "you can mass import images, albums, and users by parsing the contents of a filesystem location."
- Quote: "The system doesn't mirror a directory, it imports it and remove the file from the import path."
- Quote: "Failed files will be stored at `./importing/failed/`."
- **Parsing folders (as written):** `parse-users/` — "Top-level folder as username"; `parse-albums/` — "Top-level folders as albums"; `no-parse/` — "No folder parsing". Scans the `importing/` path.
- **Charset:** "Files and `.json` metadata must be in UTF-8."
- **Threads:** "You can speed up the process by running the importing in multiple threads by passing different `env` for `THREAD_ID`."
- **File locking:** "The importing process can be locked by placing an empty lock file at `./importing/.lock`."
- **Statuses (as written):** Queued ("default status"), Working, Paused, Canceled, Completed. Quote: "Importing may show "completed" when there's nothing else to parse, but internally it will get re-queued automatically."
- **Metadata:** "The bulk importer supports metadata using the JSON format, same as Google Photos ." One metadata file per content; `metadata.json` for user/album, `<name>.json` for image.
- **Image metadata keys (as written):** `imageData` → `title`, `description`, `nsfw`, `category` → `name`, `urlKey`, `description`. Quote: "Image categories will be created if needed long as you provide both `name` and `urlKey`."
- **Album metadata keys (as written):** `albumData` → `title`, `description`, `access`, `privacy` → `type`, `password`.
- **Album privacy types (as written, with stated default):** `public` — "Public album (default)"; `private` — "Private album for owner"; `private_but_link` — "Same as `private` + those with the album link"; `password` — "Will set the password for accessing the album".
- **User metadata keys (as written):** `userData` → `role`, `name`, `username`, `email`, `website`, `bio`, `profileImages` (`avatar`, `background`), `networks` (`facebook`, `twitter`), `timezone`, `language`, `private`.
- Quote: "Profile images have to be located in the `.assets/` folder inside the user folder."
- Quote (parser idempotency): "The parser creates users and albums only if those doesn't exists."
- **Cron entry:** "The importing command can be automatically scheduled by using CRON" — links out to `https://v4-docs.chevereto.com/application/stack/cron.html`.
- ⚠ **GAP — "Command" section is EMPTY.** The page renders a `### Command` heading with no body at all (verified in raw HTML: `<h3 id="command">…</h3> <!----> <h3 id="cron-entry">`). **The actual bulk-importer CLI command is therefore NOT published in the admin manual.** Not filled from memory.
- Sample repo referenced: `https://github.com/chevereto/demo-importing`.
- Edition restriction: none stated.

## Settings

### Settings › API

- URL `https://v4-admin.chevereto.com/settings/api.html` · HTTP 200 · title `API | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/api`
- **Enable API user** — "Toggles the access to the API for authenticated users."
- **Enable API guest** — "Toggles the access to the API for guest users (not authenticated). We recommend to keep this disabled unless you need it."
- **Public API key** — "The public API key is intended to be used by guest users to access public resources through the API."
- Defaults: none stated. Edition restriction: none stated.
- ⚠ The admin manual documents **no admin API and no API v2**. The only API documentation referenced is external: `https://v4-docs.chevereto.com/developer/api/api-v1.html` (API V1). Not fetched — out of the two-manual scope.

### Settings › Banners

- URL `https://v4-admin.chevereto.com/settings/banners.html` · HTTP 200 · title `Banners | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/banners`
- Quote: "There are 16 predefined ad spaces (32 if you consider SFW and NSFW usage)."
- **Ad spaces by location (as written):**
  - Homepage — Before main title (homepage), After call to action (homepage), After cover (homepage), After listing (homepage)
  - Listings — Before pagination, After pagination
  - Content (image and album) — Tab about column, Before comments
  - Image page — Inside viewer top (image page), Inside viewer foot (image page), After image viewer (image page), Before header (image page), After header (image page), Footer (image page)
  - Album page — Before header (album page), After header (album page)
  - User profile page — After top (user profile), Before listing (user profile)
  - Explore page — After top (explore page)
- Edition restriction: none stated.

### Settings › Categories

- URL `https://v4-admin.chevereto.com/settings/categories.html` · HTTP 200 · title `Categories | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/categories`
- Quote: "Categories classify the uploaded files and generate listings based in each category."
- Created via **Create**. **Fields (as written):** **Name** ("String | maxlength 32"), **URL key** ("Only letters, numbers, and hyphens"), **Description** ("String | Any").
- Quote (URL key): "For better SEO, try to use hyphens (-) instead of underscores (_) in the URL key."
- Quote (Description): "It will be used in the `<meta name="description">` tag for the category page."
- Edition restriction: none stated.

### Settings › Consent screen

- URL `https://v4-admin.chevereto.com/settings/consent-screen.html` · HTTP 200 · title `Consent screen | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/consent-screen`
- **Enable consent screen** — Values `Enabled` / `Disabled`. Quote: "When enabled users must agree to the terms of service before they can continue."
- **Consent screen cover image** — "Applies only if `Enable consent screen` is set to `Enabled`." Type Image, Recommended "<`400KB`".
- Defaults: none stated. Edition restriction: none stated.

### Settings › Content

- URL `https://v4-admin.chevereto.com/settings/content.html` · HTTP 200 · title `Content settings | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/content`
- **Show not safe content in listings** — `Enabled` "Show NSFW content in listings" / `Disabled` "Hide NSFW content from appearing in listings".
- **Blur NSFW content in listings** — `Enabled` "A blur filter is implemented on the image, requires mouse over to see the image without filtering".
- **Show not safe content in random mode** — "Toggles the display of NSFW content in randomized image fetching (`?random`)."
- **Show banners in not safe content** — `Enabled` / `Disabled`.
- **Lock NSFW editing** — `Enabled` "Prevent users from changing the NSFW flag" / `Disabled` "Allow users to freely change the NSFW flag".
- **Stop words** — "Define words that won't be allowed for content. One sentence per line, it supports regex."
- Defaults: none stated. Edition restriction: none stated.

### Settings › Cookie compliance

- URL `https://v4-admin.chevereto.com/settings/cookie-compliance.html` · HTTP 200 · title `Cookie compliance | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/cookie-compliance`
- **Cookie law compliance** — "Toggles the display of the cookie law acceptance message." Values `Enabled` / `Disabled`.
- This is the entire page — a single setting. Defaults: none stated. Edition restriction: none stated.

### Settings › Email

- URL `https://v4-admin.chevereto.com/settings/email.html` · HTTP 200 · title `Email | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/email`
- **From name** — Type String, **Default `Chevereto`**.
- **From email address** — Example `no-reply@chevereto.com`. Quote: "It is recommended to use a "no-reply" address."
- **Incoming email address** — Example `inbox@chevereto.com`. Quote: "Contact form and system notifications will send emails to this address."
- **Email mode** — Values `SMTP` / `PHP mail() func.`. Quote: "The setting `PHP mail() func.` should only be used at development environment and for reliability you should always use SMTP."
- **SMTP server and port** — "Ports: 25, 80, 465, 587".
- **SMTP username**, **SMTP password**.
- **SMTP security** — Values `TLS`, `SSL`, `Unsecured` ("Don't secure emails").
- Quote: "Test email delivery results at tools ."
- Edition restriction: none stated.

### Settings › External services

- URL `https://v4-admin.chevereto.com/settings/external-services.html` · HTTP 200 · title `External services | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/external-services`
- **Comments API** — Values `Disqus`, `JavaScript/HTML` ("Use any HTML comment provider"). **There is no first-party/native comment engine documented anywhere in either manual.**
- **Disqus shortname** / **Disqus secret key** / **Disqus public key** — each "Applies only if `Comments API` is set to `Disqus`."
- **Comment code** — "Applies only when `Comments API` is set to `JavaScript/HTML`". "Determines the HTML comment code, which will get added to image view."
- **Analytics code** — Quote: "This is where you can place the tracking code provided by Google Analytics, Heap, Yandex.Metrica, Matomo , Mixpanel, etc." Quote: "Code you enter in this section will be printed in all views." *(A generic HTML field — there is no dedicated Google/Bing Analytics integration.)*
- **Akismet spam protection** — `Enabled` / `Disabled`; **Akismet API key** ("Applies only if `Akismet spam protection` is `Enabled`").
- **StopForumSpam spam protection** — `Enabled` / `Disabled`. No key field documented.
- **CAPTCHA** — `Enabled` / `Disabled`.
- **CAPTCHA API** — Values `reCAPTCHA v2`, `reCAPTCHA v3`, `hCaptcha`. ⚠ **Cloudflare Turnstile is NOT listed.**
- **CAPTCHA site key**, **CAPTCHA secret key** — both "Applies only if `CAPTCHA` is set to `Enabled`."
- **CAPTCHA threshold** — "This is how many failed attempts are accepted before asking for CAPTCHA." Values: `0` "Always display CAPTCHA"; `n` "Display CAPTCHA after (n) failed attempts".
- **Force CAPTCHA on contact page** — `Enabled` / `Disabled`.
- **Project Arachnid Shield** — `Enabled` / `Disabled`; **Arachnid API username**, **Arachnid API password**. *(CSAM-detection service; present in V4.)*
- **ModerateContent** — `Enabled` / `Disabled`; **ModerateContent API Key**.
- **Automatic approve** — "Toggles automatic approve for content approved by ModerateContent." (Applies only if ModerateContent Enabled.)
- **Block content** — Values `Disabled` "Don't block any content", `Adult` "Block adult content", `Teen and adult` "Block adult and teen content".
- **Flag NSFW** — Values `Disabled`, `Adult` "Flag adult as NSFW", `Teen and adult` "Flag adult and teen as NSFW".
- Defaults: none stated for any of the above. Edition restriction: none stated.
- ⚠ **IP bans and CDN are NOT on this page** — IP bans has its own page; CDN lives in Settings › System.

### Settings › File uploads

- URL `https://v4-admin.chevereto.com/settings/file-uploads.html` · HTTP 200 · title `File uploads | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/file-uploads`
- **Enabled file extensions** — "Determines which file formats can be uploaded." Quote of the supported-format block: "AVIF JPG JPEG PNG BMP GIF WEBP MOV MP4 WEBM".
- **Enable uploads** — "Toggles the file upload functionality."
- **Enable uploads (URL)** — "Toggles the file upload functionality from URL."
- **Upload user interface** — Values `On-page container` "Uses a JS uploader that stays in page"; `/upload route` "Drives users towards the upload page".
- **Guest uploads** — "Same as enable uploads , but for guest users."
- **Guest albums** — `Enabled` "Enable album creation for guests" / `Disabled`.
- **Moderate uploads** — Values `Disabled` "No moderation required", `Guest` "Moderate guest uploads", `All` "Moderate all uploads".
- **Not safe content checkbox in uploader** — `Enabled` / `Disabled`.
- **Enable embed codes (uploader)** — "Toggles the display of embed codes after upload process."
- **Upload threads** — "Determines the number of parallel threads used by the uploader."
- **Redirect on single upload** — Quote: "This setting should be disabled if moderate upload is enabled. This is because the viewer URL will return `HTTP 403` until the image **gets approved**."
- **Enable duplicate uploads** — "Toggles the acceptance of duplicate uploads."
- **Enable expirable uploads** — "Toggles the availability of expirable uploads, which will get automatically removed after a certain date."
- **Auto delete guest uploads** — "Determines the automatic deletion of guest uploads."
- **Maximum image size** — "Determines the maximum size (in pixels) allowed for image uploads. Larger images will get automatically downscale."
- **Image Exif data** — "Toggles the handling of image Exif data."
- **Image Exif data (user setting)** — "Toggles if users can determine how to handle Exif data."
- **Maximum upload file size [MB]** — Quote: "This setting is capped by local `php.ini` configuration ."
- **Maximum upload file size (guests)** — "Same as above, but for guests."
- **File path** — "The file system path for storing uploads."
- **Storage mode** — Values `Datefolders` "Uses a nested folder structure `YYYY/MM/DD`"; `Direct` "No folder structure". Quote: "Altering this setting only affects future uploads. Previous uploads won't be affected."
- **File naming method** — Values with stated examples (source `./DSC-1313.jpg`): `Original` → `DSC-1313.jpg` ("will randomize on collisions"); `Random` → `bJdrpmdfi.jpg`; `Mix original + random` → `DSC-13pLfm.jpg`; `ID` → `kIf.jpg` ("Name the uploads as their public (encoded) ID").
- **Thumb size** — "The width and height for the image thumbs."
- **Medium image fixed dimension** — Values `Width`, `Height`.
- **Medium image fixed size** — "The medium image size."
- Defaults: none stated numerically. Edition restriction: none stated.
- ⚠ **No per-user/per-group storage quota setting appears on this page.** Storage capacity is a *per-storage* field (see Upload storage), not a per-user quota.

### Settings › Flood protection

- URL `https://v4-admin.chevereto.com/settings/flood-protection.html` · HTTP 200 · title `Flood protection | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/flood-protection`
- Quote: "Flood protection is highly encouraged to enable on your website."
- **Flood protection toggle** — `Enabled` / `Disabled`, "Toggles flood protection globally."
- **Notify to email** — `Enabled` "Email notify on flood" / `Disabled`.
- **Recommended values as written (labelled "Recommended", not "Default"):** Minute limit `50` · Hourly limit `500` · Daily limit `1000` · Weekly limit `5000` · Monthly limit `10000`. All described as "maximum image uploads per <period>".
- Edition restriction: none stated.

### Settings › Guest api — ⚠ DEPRECATED PAGE

- URL `https://v4-admin.chevereto.com/settings/guest-api.html` · HTTP 200 · title `Guest API | V4 Admin` · observed 2026-09-15
- The page body is a single warning block. Quote: "This page is deprecated. The `/dashboard/settings/guest-api` route no longer exists."
- Quote: "Guest API settings (including the Public API key) have been merged into API settings at `/dashboard/settings/api`."
- Still listed in the live sidebar as "Guest api". See also the NOT SHIPPED section below.

### Settings › Homepage

- URL `https://v4-admin.chevereto.com/settings/homepage.html` · HTTP 200 · title `Homepage | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/homepage`
- **Style** — Values `Landing page`, `Split landing + images`, `Route explore` ("Set homepage as `/explore`"), `Route upload` ("Set homepage as `/upload`").
- **Cover image (`n`)** — "Determines the cover image used in homepage (multiple instances)." Recommended "`<400KB`".
- **Add new cover image** — Recommended "`<400KB`".
- **Title** — **Default (stated):** "Upload and share your images."
- **Paragraph** — **Default (stated):** "Drag and drop anywhere you want and start uploading your images now. 2 MB limit. Direct image links, BBCode and HTML thumbnails."
- **Call to action button color** — Options "Accent, Blue, Green, Orange, Red, Grey, Black, White, Default".
- **Call to action outline style button** — `Enabled` / `Disabled`.
- **Call to action functionality** — Values `Trigger uploader` "Prompt image upload file picker"; `Open URL` "Link to the target URL".
- **Call to action URL** — "Applies only when `Call to action functionality` is set to `Open URL`." Example `/page/tos`.
- **Call to action HTML** — **Default (stated):** "Start uploading".
- **User IDs** — "This setting applies only when `Style` is set to `Split landing + images`." Quote: "Leave it blank to display "trending" images, which will work as `/explore/trending`." Example "1,2,3,5,70".
- Edition restriction: none stated.

### Settings › IP Bans

- URL `https://v4-admin.chevereto.com/settings/ip-bans.html` · HTTP 200 · title `IP bans | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/ip-bans`
- Quote: "IP bans allows to ban IP addresses and IP ranges from using the system."
- Added via **Add**. **Fields (as written):** **Ip address** ("IPV4 and IPV6 addresses"), **Expiration date** (Datetime, Optional "Y"), **Description** ("A brief description about the IP ban (e.g. the reason for the ban)").
- Edition restriction: none stated.

### Settings › Languages

- URL `https://v4-admin.chevereto.com/settings/languages.html` · HTTP 200 · title `Languages | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/languages`
- **Default language** — **Default (stated):** `English`.
- **Auto language** — `Enabled` / `Disabled`. Quote: "the system language will be set based on user's browser default language setting."
- **Language chooser** — `Enabled` / `Disabled`. Quote: "Guests will be able to pick the language from the top bar, registered users will be able to pick the language at `/settings`."
- **Enabled languages** — checkbox list, **34 locales as written**: "Bahasa Indonesia, Čeština, Dansk, Deutsch, Eesti (Eesti), English, Español, Français, Italiano, Lietuvių (Lietuva), Magyar, Nederlands, ‪Norsk Bokmål‬, Polski, Português, Português (Brasil), Slovenčina, Suomi, Svenska, Tiếng Việt, Türkçe, Ελληνικά, Български, Русский, Српски, Українська, עברית, العربية, فارسی, ไทย, 한국어, 日本語, 简体中文, 繁體中文".
- Customization/adding languages is deferred to an external doc: `https://v4-docs.chevereto.com/developer/customization/language.html` (not fetched — outside the two manuals).
- Edition restriction: none stated.

### Settings › Listings

- URL `https://v4-admin.chevereto.com/settings/listings.html` · HTTP 200 · title `Listing settings | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/listings`
- **List items per page** — Recommended `24`. Quote: "The more you display, the slower it gets. Choose wisely."
- **List pagination mode** — Values `Classic pagination` "Use conventional pages to browse listings"; `Endless scrolling` "Use XHR to append content to the listing page".
- **Listing viewer** — `Enabled` "Enables a a full-screen image browsing experience, like a lightbox" *(sic)* / `Disabled` "No viewer".
- **Image listing size** — Values `Fixed` "Tiled listing display, fixed width and height"; `Fluid` "Masonry listing display, automatic height".
- **Album listing requirement (explore)** — "Determine the album image count required to show the album in listings." Recommended `5`.
- **Listing columns number** — Quote: "You can control this for a wide selection of devices: phone, phablet, tablet, laptop and desktop." Recommended "`1` or `2` columns for small devices".
- Edition restriction: none stated.

### Settings › Login Providers

- URL `https://v4-admin.chevereto.com/settings/login-providers.html` · HTTP 200 · title `Login providers | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/login-providers`
- Quote: "For each provider you can enable/disable and configure the application id and secret."
- **Configurable providers listed on this page (29):** Amazon, BitBucket, Discord, Dribbble, Dropbox, Facebook, GitHub, GitLab, Google, Instagram, LinkedIn, Mailru, Medium, Odnoklassniki, ORCID, QQ, Reddit, Spotify, Steam, Strava, Telegram, Tumblr, Twitch, Twitter, VK, WeChat, WordPress, Yahoo, Yandex.
- ⚠ **Discrepancy inside the admin manual:** Features › Login providers lists **30** providers; this Settings page lists **29**. The difference is **Apple**, which appears in the Features handle table (`apple`) but not in this Settings list. Both lists are reproduced verbatim.
- Edition restriction: none stated.

### Settings › Logo

- URL `https://v4-admin.chevereto.com/settings/logo.html` · HTTP 200 · title `Logo | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/logo`
- **Logo select** — Values `Vector` "Use vector image", `Image` "Use a raster image", `Text` "Use website name".
- **Logo vector** — Type SVG, **Default (stated)** `500x76`.
- **Logo image** — Type PNG, **Default (stated)** `314x48`.
- **Logo height** — Recommended `20`. "Determines the logo height (fixed) as width will be adjusted."
- **Favicon image** — Type PNG, **Default (stated)** `300x300`.
- Edition restriction: none stated.

### Settings › Pages

- URL `https://v4-admin.chevereto.com/settings/pages.html` · HTTP 200 · title `Pages | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/pages`
- **Fields (as written):** Title, Page status, Type, Internal page type, Page visibility, URL key, File path, Meta keywords, Meta description, Source code, Link URL [page type link], Link target attribute, Link rel attribute, Link icon, Sort order display.
- Quote (Type): "Internal page is a `.php` file in which you can do anything."
- Quote (Type): "Link page is just a link to a target URL."
- Quote (Internal page type): "which can be of type terms of service or extra page."
- Quote (Source code): "The code for the internal `.php` page."
- ⚠ **Security-relevant for Vizra:** this is an unrestricted server-side script surface — admins author raw `.php` executed by the app. AGENTS.md forbids "unrestricted custom-script surfaces", so this is a deliberate non-parity item. Marked here as a finding, not a requirement.
- Defaults: none stated. Edition restriction: none stated.

### Settings › Routing

- URL `https://v4-admin.chevereto.com/settings/routing.html` · HTTP 200 · title `Routing | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/routing`
- **User routing** — Examples "`user`, `u`". **Image routing** — "`image`, `i`". **Video routing** — "`video`, `v`". **Album routing** — "`album`, `a`".
- **Root routing** — "Determine which content to resolve on root route." Values `User` → `/user`, `Album` → `/album`, `Image` → `/image`, `Video` → `/video`.
- **SEO image URLs** — `Enabled` / `Disabled`. Quote: "the image URL will contain its title, like `/image/image-title.<id>`."
- **SEO album URLs** — `Enabled` / `Disabled`. Quote: "the album URL will contain its title, like `/album/album-name.<id>`."
- Defaults: none stated. Edition restriction: none stated.

### Settings › Semantics

- URL `https://v4-admin.chevereto.com/settings/semantics.html` · HTTP 200 · title `Semantics | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/semantics`
- Quote: "Semantics allows you to define the nouns used for content to customize your content driven experience."
- **Overridable nouns (16, as written):** Album, Albums, Image, Images, Video, Videos, File, Files, Tag, Tags, User, Users, Category, Categories, Explore, Discovery.
- Defaults: none stated. Edition restriction: none stated.

### Settings › Site storage

- URL `https://v4-admin.chevereto.com/settings/site-storage.html` · HTTP 200 · title `Site storage | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/site-storage`
- This is the "assets storage" surface. Quote from Features › Upload storage: "Check the Site storage documentation to control where website assets (backgrounds, avatars, etc.) are stored."
- **Common fields (as written):** Bucket, Key ("Public key"), Secret ("Secret key"), Storage capacity (Example "20 GB"), URL (Example `https://storage1.demo.chevereto.com/bucket/`).
- Quote: "For the example above, a file at `https://storage1.demo.chevereto.com/bucket/example.jpg` should be resolving."
- **Provider list and storage-type identifiers — identical to Upload storage (see next-but-one section for the full per-provider field table):** `oss`, `s3`, `b2`, `ftp`, `gcloud`, `local`, `azure`, `openstack`, `s3compatible`, `sftp`.
- ⚠ Site storage has **no `Name` field** (Upload storage does). Otherwise the two pages' provider sections are byte-identical in content.
- Edition restriction: none stated.

### Settings › System

- URL `https://v4-admin.chevereto.com/settings/system.html` · HTTP 200 · title `System | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/system`
- **Cache time seconds** — "Determines the cache TTL (time to live) in seconds. Use zero (`0`) to disable caching." **Default (stated): `0`.**
- **Automatic updates check** — `Enabled` / `Disabled`. "your installation will automatically check for new updates."
- **Display available updates notification** — `Enabled` / `Disabled`.
- **Dump update query** — `Enabled` "Dump the update query (queries should be manually executed)" / `Disabled` "Run the update query (queries will be executed directly)". Quote: "This is automatically enabled if the installation holds more than 1,000,000 (1M) images."
- **CDN** — `Enabled` / `Disabled`. **CDN URL** — "Applies only if `CDN` is set to `Enabled`." Quote: "The CDN URL will be used for all local static resources."
- **Maintenance** — `Enabled` / `Disabled`. Quote: "the website will show a maintenance message and no actions will be allowed."
- **Crypt salt** — "The crypt salt used to encode DB integer IDs to alphanumeric representations." Quote: "This value is shown only for reference. It shouldn't be edited." Example `bnnnfer98`.
- **Debug errors** — `Enabled` / `Disabled`.
- **Debug level** — Values `None`, `Error log`, `Print errors without error log`, `Print and log errors`.
- **Enable xrDebug** — "Toggles integration with xrDebug for sending debug messages to an xrDebug server."
- ⚠ This page is the closest thing to "system/upgrade" in the sidebar. **There is no separate upgrade/installer page, no Docker page, no environment-variable page, and no licensing page in the admin manual.** See "Requested topics absent".
- Edition restriction: none stated.

### Settings › Theme

- URL `https://v4-admin.chevereto.com/settings/theme.html` · HTTP 200 · title `Theme | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/theme`
- **Theme select** — "Determines the theme to use." (No theme names listed.)
- **Default palette** — "Determines the default palette to use." (No palette names listed on this page; see PUP for a palette-name list.)
- **Default font** — "Font used by default."
- **Image load max. filesize (MB)** — Recommended `3`. Quote: "Images bigger than this value will require "click to load" full resolution image."
- **Enable download button** — `Enabled` / `Disabled`.
- **Enable right click on image** — `Enabled` "Enable to right click on images (save-as)" / `Disabled`. Quote: "This controls the display of the context menu for the `<image>` tag."
- **Enable show Exif data** — `Enabled` / `Disabled`.
- **Image first tab** — Values `Embeds` "Embed codes"; `About` "About (description, Exif)"; `Info` "Admin only (extensive details)".
- **Enable social share** — `Enabled` / `Disabled`.
- **Enable embed codes (content)** — `Enabled` / `Disabled`.
- **Custom CSS code** — "Custom `CSS` code that will get added to the HTML."
- **Custom JS code** — "Custom `JS` code that will get added to the HTML." ⚠ Another unrestricted script-injection surface (same Vizra caveat as Pages).
- Defaults: none stated. Edition restriction: none stated.

### Settings › Tools

- URL `https://v4-admin.chevereto.com/settings/tools.html` · HTTP 200 · title `Tools | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/tools`
- **Decode ID** — "Converts an encoded id into its integer decoded value." Example `v5ZO` → `1234`.
- **Encode ID** — "Converts an integer id into its encoded value." Example `1234` → `v5ZO`.
- **Send test email** — "Sends a test mail to the target email address. Use this to test email delivery rate."
- **Export a user** — "Exports user profile information in `json` format." Sample keys as written: `name`, `username`, `email`, `facebook_username`, `twitter_username`, `website`, `bio`, `timezone`, `language`, `is_private`, `newsletter_subscribe`.
- **Regenerate external storage stats** — "Re-calculate external storage stats for the target storage id."
- **Migrate image records** — "Re-assign image database tables from one storage to another." Inputs: **Source storage id**, **Target storage id**.
- ⚠ **"Export a user" exports profile fields only** — it is not a GDPR content/media export. No account-deletion or data-portability tool is documented.
- Edition restriction: none stated.

### Settings › Upload plugin

- URL `https://v4-admin.chevereto.com/settings/upload-plugin.html` · HTTP 200 · title `Upload plugin | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/upload-plugin`
- **Plugin route** — "Toggles the availability of the `/plugin` route." `Enabled` / `Disabled`.
- **PUP SDK URL** — "Determines the URL for PUP SDK." Type String / URL.
- Defaults: none stated. Edition restriction: none stated.

### Settings › Upload storage

- URL `https://v4-admin.chevereto.com/settings/upload-storage.html` · HTTP 200 · title `Upload storage | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/upload-storage`
- Added via **Add storage**. Multiple storages are supported (the Tools page migrates records between storage ids).
- **Common fields (as written):** **Name** ("String | max length 32"), **Bucket**, **Key** ("Public key"), **Secret** ("Secret key"), **Storage capacity** (Example "20 GB"), **URL** (Example `https://storage1.demo.chevereto.com/bucket/`).
- **Per-provider storage types and extra fields — verbatim:**

| Provider heading (as written) | Storage type | Additional fields as written |
|---|---|---|
| Alibaba Cloud OSS | `oss` | Endpoint — "Alibaba Cloud OSS endpoint" |
| Amazon S3 | `s3` | Region — "Amazon S3 region". Quote: "If your S3 provider isn't AWS you have to use S3 Compatible ." |
| Backblaze B2 (legacy) | `b2` | Key = "Account ID"; Secret = "Master Application Key" |
| FTP | `ftp` | Server (`127.0.0.1`, `ftp.chevereto.com`), Path (`/path/in/server/`), User, Password |
| Google Cloud | `gcloud` | Private key — "Google Cloud JSON key" |
| Local | `local` | "Local requires to provide the local path." |
| Microsoft Azure | `azure` | Account = "Microsoft Azure AccountName"; Key = "Microsoft Azure Accountkey"; Endpoint |
| OpenStack | `openstack` | Service name ("For example, `swift`"), Identity URL, Username, Password, Region, Container, Tenant id, Tenant name |
| S3 compatible | `s3compatible` | Region, Endpoint |
| SFTP | `sftp` | "Same as FTP , but using the SSH File Transfer Protocol protocol." |

- **All ten providers requested are present and documented.** Edition restriction: none stated on any provider.

### Settings › Users

- URL `https://v4-admin.chevereto.com/settings/users.html` · HTTP 200 · title `Users | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/users`
- **User profile view** — Values `Files` "Show files (default)"; `Albums` "Show albums". **Stated default: Files.**
- **Enable signups** — `Enabled` / `Disabled`.
- **Enable user content delete** — `Enabled` "Enable users to delete their own content" / `Disabled`.
- **Minimum age required** — Recommended `13`.
- **Notify on user signup** — `Enabled` / `Disabled`.
- **Require email confirmation** — `Enabled` "Require to confirm singup email address" *(sic)* / `Disabled`.
- **Require email for social signup** — `Enabled` / `Disabled`.
- **User avatar max. filesize (MB)** — Recommended `1`.
- **User background max. filesize (MB)** — Recommended `2`.
- ⚠ **There is no user-groups/roles-management page.** Roles are a fixed three-value enum (User / Manager / Administrator) set per user; no group CRUD, no per-group quota or permission editing is documented anywhere in either manual.
- Edition restriction: none stated.

### Settings › Watermarks

- URL `https://v4-admin.chevereto.com/settings/watermarks.html` · HTTP 200 · title `Watermarks | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/watermarks`
- **Watermarks toggle** — "Toggles image watermarking, which are images that are merged in front of the images."
- **Watermark user toggles** — "Select which user uploads will be watermarked." (Options not enumerated on the page.)
- **Watermark file toggles** — "Which image formats will be watermarked." (Options not enumerated.)
- **Minimum image size needed to apply watermark**
- **Watermark image** — Recommended "PNG with alpha transparency".
- **Watermark position** — 3×3 grid as written: "Left top, Center top, Right top, Left center, Center center, Right center, Left bottom, Center bottom, Right bottom".
- **Watermark percentage** — "The watermark size expressed in percentage of the target area."
- **Watermark margin**, **Watermark opacity**.
- Defaults: none stated. Edition restriction: none stated.

### Settings › Website

- URL `https://v4-admin.chevereto.com/settings/website.html` · HTTP 200 · title `Website settings | V4 Admin` · observed 2026-09-15 · route `/dashboard/settings/website`
- **Website name** — "it will be used in all document titles (trailing)."
- **Website `doctitle`** — "mainly used in homepage."
- **Website description**, **Default time zone** ("This will be the default timezone for new user sign-up").
- **Search** / **Search (guests)** — `Enabled` / `Disabled`. Quote: "Search allows users to locate content based on a search query."
- **Explore** / **Explore (guests)** — `Enabled` / `Disabled`. Quote: "Explore browses the public available images."
- **Random** / **Random (guests)** — `Enabled` / `Disabled`. Quote: "It enables `?random` to fetch a random public image."
- **Powered by Chevereto** — `Enabled` / `Disabled`. Quote: "Showing "Powered by Chevereto" allows others to know the software and it helps us to get known." *(Documented as a plain toggle — no edition/licence condition is stated.)*
- **Likes** — `Enabled` / `Disabled`. Quote: "Likes allow users to like content. It also generates "liked" listings."
- **Followers** — `Enabled` / `Disabled`. Quote: "Followers allow users to follow each other. It also enables the "following" listing for each user."
- **Website mode** — Values `Multi-user` "A community-like website with users interacting"; `Single profile` "A single-user experience".
- **Single profile target user** — "Applies only if `Website mode` is set to `Single profile`." Integer, Example `1`.
- **Single profile routing** — "Determines a custom route to map `/username` to another path. Use `/` to map directly to the homepage."
- **Website privacy mode** — Values `Public` "All content is intended to be public"; `Private` "All content is intended to be private (login required)". Quote: "Private mode will always require login. Implement it only for private audiences."
- **Content privacy mode** — "Applies only if `Website privacy mode` is set to `Private`." Quote: "Privacy is provisioned per album basis. Images inherits privacy from the album." Values: `Default` "Users can freely choose the privacy for their own content"; `Force private (self)`; `Force private (anyone with the link)` "User content is forced to be private but accesible for anyone with the link" *(sic)*.
- ⚠ **No "multi-server"/"multi-site" setting exists.** The nearest concepts are multiple *upload storages* and `Website mode: Single profile`.
- Defaults: none stated except as noted. Edition restriction: none stated.

## Features

### Features › Upload storage

- URL `https://v4-admin.chevereto.com/features/upload-storage.html` · HTTP 200 · title `Upload storage | V4 Admin` · observed 2026-09-15
- Quote: "Upload storage lets you offload user-uploaded files to one or more external servers."
- Quote: "That server exposes the files over HTTP, so users and visitors can access uploaded images directly without hitting your origin."
- **Storage URL mapping example (Amazon S3, direct):** Bucket `my-bucket` · Storage URL `https://s3.amazonaws.com/my-bucket/` · Stored image `my-bucket/image.jpg` · Mapped URL `https://s3.amazonaws.com/my-bucket/image.jpg`.
- **Folder-based + CNAME example:** Storage URL `https://img.domain.com/my-bucket/` · Stored image `/my-bucket/2020/10/06/image.jpg`.
- Quote: "It is recommended to use a URL that matches your own domain."
- **CDN:** "To use a CDN, create a pull zone at your CDN provider pointing to the origin Storage URL."
- ⚠ **Lifecycle warning (operationally important):** "Always disable lifecycle policies on your storage bucket. If prompted, select **keep only the last version of the file**."
- **Amazon S3 setup as written:** IAM **Create users**; "attach **AmazonS3FullAccess**"; "Click **Create access key** and select **Third-party service**"; bucket Object Ownership "**ACLs enabled** and **Bucket owner preferred**"; "leave **Block all public access** unchecked so objects are publicly accessible"; "Under Bucket Versioning, select **Disable**".
- **Backblaze B2 — S3-compatible mapping table as written:** Region `us-west-002` ("from your Endpoint URL") · keyID → Storage key · applicationKey → Storage secret · Endpoint `https://s3.us-west-002.backblazeb2.com` · URL `https://f002.backblazeb2.com/file/your_bucket/`. Legacy: keyID → "Storage key (Account ID)"; applicationKey → "Storage secret (Master Application Key)". Quote: "Set **Files in Bucket** to **Public**"; "Type of Access: **Read and Write**".
- **Google Cloud setup as written:** "confirm that **Google Cloud Storage JSON API** is enabled"; "Uncheck **Enforce public access prevention on this bucket**"; "Set Access control to **Fine-grained**"; service account "Grant role: **Owner**", "Key type: **JSON**"; "paste its entire contents into Chevereto's **Secret Key** field".
- **OpenStack field table as written:** Identity URL ("Your provider's Keystone identity endpoint URL"), Username, Password, Region, Container, Tenant ID ("Leave blank if not required by your provider"), Tenant name ("Your project ID (found in OpenStack Horizon under CURRENT PROJECT)"), URL.
- **S3 Compatible** — Quote: "Configuration is identical to Amazon S3, with the addition of a custom provider endpoint."
  - **Hosted providers listed:** Backblaze B2 (via S3-compatible API), Cloudflare R2, DigitalOcean Spaces, DreamHost DreamObjects, Hetzner Object Storage, IBM COS S3, IDrive e2, Linode Object Storage (now Akamai), OVH Cloud Object Storage, PhoenixNAP Object Storage, Scaleway Object Storage, Storj, Tencent Cloud Object Storage (COS), Vultr Object Storage ("use region `us-east-1`"), Wasabi.
  - **Self-hosted listed:** MinIO, Ceph (RGW), SeaweedFS (S3 Gateway), Zenko (by Scality), LeoFS (S3 support in gateway mode), Garage (Deuxfleurs).
- **Alibaba Cloud OSS / FTP / Local / Microsoft Azure / SFTP** — each present with a one-line description only.
- Edition restriction: none stated.

### Features › Login providers

- URL `https://v4-admin.chevereto.com/features/login-providers.html` · HTTP 200 · title `Login providers | V4 Admin` · observed 2026-09-15
- Quote: "Login providers let your users sign in or register using an existing account from a third-party service such as Google, GitHub, or Apple."
- **Provider → handle table, verbatim (30 rows):** Facebook `facebook` · Twitter `twitter` · Google `google` · VK `vkontakte` · Apple `apple` · Amazon `amazon` · BitBucket `bitbucket` · Discord `discord` · Dribbble `dribbble` · Dropbox `dropbox` · GitHub `github` · GitLab `gitlab` · Instagram `instagram` · LinkedIn `linkedin` · Mailru `mailru` · Medium `medium` · Odnoklassniki `odnoklassniki` · ORCID `orcid` · Reddit `reddit` · Spotify `spotify` · Steam `steam` · Strava `strava` · Telegram `telegram` · Tumblr `tumblr` · Twitch `twitchtv` · WeChat `wechat` · WordPress `wordpress` · Yandex `yandex` · Yahoo `yahoo` · QQ `qq`.
- **Callback URL format as written:** `https://yourwebsite.com/connect/HANDLE/` — "Replace `HANDLE` with the provider's handle from the supported providers table."
- Quote: "Each provider requires you to register an application in their developer portal before Chevereto can use it."
- ⚠ **No SSO/SAML/OIDC-generic provider is documented.** OAuth is per-named-provider only.
- Edition restriction: none stated.

---

# USER MANUAL — `https://v4-user.chevereto.com/`

Headings mirror the user sidebar exactly and in sidebar order.

## Home (index)

- URL `https://v4-user.chevereto.com/` · HTTP 200 · title `V4 User` · observed 2026-09-15
- Quote: "Welcome to the Chevereto V4 User Manual. This documentation contains all what's need to know about using a Chevereto-based system." *(sic)*
- Hero CTA reads "Create account →". Sidebar group "Home" contains one entry, "Links".

## User

### User › Account › Signup

- URL `https://v4-user.chevereto.com/user/account/signup.html` · HTTP 200 · title `Create Account | V4 User` · observed 2026-09-15
- Quote: "Creating an account will allow you to associate content with a user and access other Chevereto features."
- **Flow as written:** top bar **Login** → **Sign Up** → "Complete the **registration form**" → "Select the checkbox for **terms** and **privacy policies**" → **Create account**.
- Registration form fields are NOT enumerated on this page. Not inferred.

### User › Account › Login

- URL `https://v4-user.chevereto.com/user/account/login.html` · HTTP 200 · title `Login | V4 User` · observed 2026-09-15
- Quote: "When you log in, the activity and content will be associated with your user account."
- **Flow as written:** top bar **Login** → "Complete the **login form**" → "**Submit the form** to perform the login".
- ⚠ The Login page does **not** mention social/OAuth sign-in buttons, 2FA prompt, or "remember me". 2FA-at-login is mentioned only on the Security page.

### User › Account › Password forgot

- URL `https://v4-user.chevereto.com/user/account/password-forgot.html` · HTTP 200 · title `Recover Password | V4 User` · observed 2026-09-15
- Quote: "If you don't remember or have lost your password and don't have backup codes, the user must follow the password recovery procedure."
- **Flow as written:** **Login** → **Recover password** → submit form → "Instructions will be sent to your email to proceed with password reset".
- ⚠ **"backup codes" are referenced here but are documented nowhere else** in either manual — the Security page describes only TOTP enrol/disable. Flagged as an internal documentation gap; NOT inferred into a feature.

### User › Profile › User Profile

- URL `https://v4-user.chevereto.com/user/profile/user-profile.html` · HTTP 200 · title `User Profile | V4 User` · observed 2026-09-15
- Quote: "The user profile displays the content and (public) information of a user. The user profile is completely customizable and configurable."
- **Profile background:** "Click on the **Upload profile background** button (requires Login )"; "click on the **Change background** button".
- **User search:** "Use the user profile search to find content provided by the particular user."
- **Follow user:** "Click on the **Follow** button (requires Login )".

### User › Profile › Notifications

- URL `https://v4-user.chevereto.com/user/profile/notifications.html` · HTTP 200 · title `Notifications | V4 User` · observed 2026-09-15
- Quote: "Notifications are located in the top bar, next to the user icon. The icon displays a badge with the count of unread notifications."
- **Notification types, verbatim list:** "Someone **likes** your media or album"; "Someone **follows** you"; "Someone **comments** on your content (when comments are enabled)".
- **Marking as read:** "Notifications are marked as read automatically when you open the notifications panel."
- ⚠ **No email-notification preferences, no per-type notification settings, and no notification history/pagination are documented.** The only email opt-in documented anywhere is the Chevereto **Newsletter**.

### User › Profile › Color Palette

- URL `https://v4-user.chevereto.com/user/profile/color-palette.html` · HTTP 200 · title `Color Palette | V4 User` · observed 2026-09-15
- Quote: "The system color palette is configurable and can be changed from anywhere."
- **Flow as written:** top bar **User icon** → "**Palettes** section" → "Click to **confirm the change** to the desired palette".
- Palette names are not listed on this page. (A palette-name list does appear in the PUP integration page — see Integrations › PUP.)

### User › Profile › Albums

- URL `https://v4-user.chevereto.com/user/profile/albums.html` · HTTP 200 · title `Albums | V4 User` · observed 2026-09-15
- Quote: "Albums are content containers that work like folders, grouping media files with support for nested sub-albums and privacy controls."
- **Access:** top bar **User Icon** → **Albums**.
- **Create:** "Click on **Create new album**" → submit → "you will be **redirected** to the newly created album".
- **Post-upload create:** "click the **Create new album** link that appears in the post-upload area"; "All the files just uploaded will be moved into the new album automatically".

### User › Profile › Liked

- URL `https://v4-user.chevereto.com/user/profile/liked.html` · HTTP 200 · title `Liked | V4 User` · observed 2026-09-15
- Quote: "This section displays all media and albums that you have marked as liked. It acts as a personal collection of favourited content across the site."
- **Direct route as written:** `/{username}/liked`.
- **Liking:** "Click the **heart icon** on any media or album thumbnail"; "or use the `L` keyboard shortcut".
- **Unliking:** "click the **heart icon** again on any content you have previously liked."
- ⚠ **"Likes" and "favorites" are the same feature in Chevereto** — the manual uses "liked"/"favourited" interchangeably on this page. There is no separate favorites/collections feature.

### User › Profile › Following

- URL `https://v4-user.chevereto.com/user/profile/following.html` · HTTP 200 · title `Following | V4 User` · observed 2026-09-15
- Quote: "This section displays content uploaded by the users that you follow, giving you a personalised feed of media from your network."
- **Direct route as written:** `/{username}/following`.
- Quote: "The Following feed shows the latest media from all users you follow, sorted by most recent." (No other sort documented for this feed.)
- **Unfollow:** "Visit the profile of the user you want to unfollow" → "Click the **Unfollow** button".

### User › Profile › Followers

- URL `https://v4-user.chevereto.com/user/profile/followers.html` · HTTP 200 · title `Followers | V4 User` · observed 2026-09-15
- Quote: "Each entry shows the follower's avatar, username, and a link to their profile."
- **Direct route as written:** `/{username}/followers`.
- Quote: "This count updates in real time as users follow or unfollow the account."
- ⚠ No block/mute is documented anywhere in either manual — following is one-directional with no user-level blocking.

### User › Settings › Account

- URL `https://v4-user.chevereto.com/user/settings/account.html` · HTTP 200 · title `Account | V4 User` · observed 2026-09-15 · route `/settings`
- **Username** — "The username is the alphanumeric identifier of the account. This identifier is unique per user."
- **Email** — "This email address will be used for all types of communications with the user."
- **Auto delete uploads** — "The range goes from 5 minutes to 1 year."
- **Keep EXIF data** — "When disabled, Chevereto will remove that information from the image file." Sub-option as written: **Keep EXIF data on upload**.
- **Automatic metadata tags** — "Chevereto will **assign camera model tag on upload** automatically based on the image EXIF data."
- **Newsletter** — checkbox label as written: "Send me emails with news about Chevereto".
- **Content settings › Show not safe content in listings** — "When unchecked, unsafe content is hidden."
- **Language** — "Chevereto automatically detects the language. Additionally, you can force the use of a language of your choice."
- **Timezone** — "The timezone allows you to determine the user's local time."
- ⚠ **No "delete my account" control is documented on this page or anywhere in the user manual.** Account deletion appears only as an admin action (**Delete user**, Dashboard › Users). Recorded as a gap, not inferred.

### User › Settings › Profile

- URL `https://v4-user.chevereto.com/user/settings/profile.html` · HTTP 200 · title `Profile | V4 User` · observed 2026-09-15 · route `/settings/profile`
- **Avatar** — "The avatar corresponds to the user image and will be used extensively to indicate the user and/or their content."
- **Privacy** — "The user profile can be public or private. When the profile is private, the user's identity is hidden from others in their interactions with the system."
- **Name** — "this is ideally the user's real name."
- **Website** — "this is the personal website or any other URL."
- **Bio** — "this is what you tell others about yourself."
- ⚠ The profile-background upload is documented on the User Profile page, not here. Social-network handles (`facebook_username`, `twitter_username` seen in the admin Tools export) are **not** documented as editable fields in the user manual.

### User › Settings › Password

- URL `https://v4-user.chevereto.com/user/settings/password.html` · HTTP 200 · title `Password | V4 User` · observed 2026-09-15 · route `/settings/password`
- Full body quote: "In this section you can configure your account password. If you don't remember your password, you should Recover password ."
- No field names, strength rules, or re-authentication requirement are documented.

### User › Settings › Security

- URL `https://v4-user.chevereto.com/user/settings/security.html` · HTTP 200 · title `Security | V4 User` · observed 2026-09-15 · route `/settings/security`
- Quote: "Two-factor authentication allows you to configure a TOTP device for an additional layer of account security."
- Quote: "When enabled, the system will require the code provided by the synchronized application at the moment of Login ."
- **Enable flow as written:** "Open your **authenticator app** (Google Authenticator, Authy, etc.)" → "Scan the **QR code** shown on this page" → "Enter the **OTP code** from your app into the **OTP** field" → **Submit**.
- **Disable flow as written:** "Click on the **Disable** button".
- ⚠ Only TOTP. **No backup/recovery codes, no WebAuthn/passkeys, no session management or device list, no login-history** documented — despite the Password-forgot page referencing "backup codes".

### User › Settings › API

- URL `https://v4-user.chevereto.com/user/settings/api.html` · HTTP 200 · title `API | V4 User` · observed 2026-09-15 · route `/settings/api`
- Quote: "In this section you can configure the user API key, which allows you to use the Chevereto API ."
- **API Key** — "The API key is auto-generated."
- **Sample request, verbatim:** `curl --fail-with-body -X POST -H "X-API-Key: YOUR_API_KEY" -H "Content-Type: multipart/form-data" -F "source=@image.jpeg" http://yoursite/api/1/upload`
- **Auth header as written:** `X-API-Key`. **Endpoint as written:** `/api/1/upload`.
- **Viewing your key** — "The API key is displayed **only once** — store it in a secure location as it will be shown just once."
- **Regen key** — "Click the **Regen key** button to invalidate the current key and generate a new one."
- API reference is external: `https://v4-docs.chevereto.com/developer/api/api-v1.html` (not fetched — outside the two manuals).

## Features

### Features › Upload › Upload local

- URL `https://v4-user.chevereto.com/features/upload/local.html` · HTTP 200 · title `Upload local | V4 User` · observed 2026-09-15
- **Upload-page prompt, verbatim:** "Drag and drop or paste files here to upload". Also "browse from your computer".
- Quote: "Supported formats: **AVIF JPG PNG BMP GIF WEBP MOV MP4 WEBM** (max 8 GB per file)". *(8 GB is this instance's configured value, not a product default — see Formats.)*
- **Upload-page options (pre-upload), as written:** Album ("requires Login"), Category, Expiration time, NSFW flag (unsafe content).
- **Advanced (per-file) options, as written:** Title, Tags, Album, Category, Resize, Auto delete, NSFW flag (unsafe content), Description. Quote: "After selecting the media to upload you can edit any of them by clicking on the preview."
- **Post-upload:** "Once the upload is complete you can create a new album and access the embed codes."
- **Post-upload embed formats listed here:** BBCode, HTML, Markdown.
- ⚠ Confirms drag-and-drop, paste, and file-picker. **Device/camera capture is not documented.**

### Features › Upload › Upload URL

- URL `https://v4-user.chevereto.com/features/upload/url.html` · HTTP 200 · title `Upload URL | V4 User` · observed 2026-09-15
- **The only explicit access restriction in the entire user manual**, verbatim: "This functionality is exclusive to system administrators."
- **Flow as written:** top bar **Upload** → **Add URL** → "Complete and **submit the form**".
- Note: the admin manual exposes **Enable uploads (URL)** as a global toggle (Settings › File uploads) without stating the admin-only restriction. The two manuals are not fully reconciled on this point. Recorded as observed; not resolved.

### Features › Upload › Formats

- URL `https://v4-user.chevereto.com/features/upload/formats.html` · HTTP 200 · title `Formats | V4 User` · observed 2026-09-15
- **Image, verbatim:** "Chevereto supports the image formats **AVIF, JPG, PNG, BMP, GIF, WEBP**."
- Quote: "Note: BMP is automatically converted to PNG."
- **Video, verbatim:** "Chevereto supports the video formats **MOV, MP4, WEBM**."
- **Upload limits:** "The maximum file size for uploads is displayed on the upload page (e.g. **MAX 8 GB** depending on server configuration)."
- ⚠ Discrepancy with the admin manual: admin Settings › File uploads lists "AVIF JPG **JPEG** PNG BMP GIF WEBP MOV MP4 WEBM" (includes `JPEG` separately); the user manual omits `JPEG`. Both recorded verbatim. **No HEIC/HEIF, TIFF, SVG, or animated-AVIF support is claimed.**

### Features › Explore › Explore Menu

- URL `https://v4-user.chevereto.com/features/explore/menu.html` · HTTP 200 · title `Explore Menu | V4 User` · observed 2026-09-15
- Quote: "The Explore functionality may require Login or may be completely disabled by the system administrator."
- **Access:** "In the top bar click the **Explore** button".
- Three sub-areas named: **Discovery**, **Categories**, **Tags**.

### Features › Explore › Discovery

- URL `https://v4-user.chevereto.com/features/explore/discovery.html` · HTTP 200 · title `Discovery | V4 User` · observed 2026-09-15
- **Discovery listings, verbatim definitions:** **Recent** "Sorts content by upload date, most recent first."; **Trending** "Sorts content by views, most viewed first."; **Popular** "Sorts content by likes, most liked first."; **Following** "Displays content uploaded by users followed by the logged-in user." (Requires Login.)
- **Content tabs, verbatim:** Images "Image files only" · Videos "Video files only" · Animated "Animated GIF files only" · Tags "Content grouped by tags" · Albums "All public albums" · Users "All registered users".
- ⚠ **Trending is view-count ordering and Popular is like-count ordering — no time decay, no personalisation, no recommender is documented.** Relevant to Vizra's Flickr-like discovery ambitions.

### Features › Explore › Categories

- URL `https://v4-user.chevereto.com/features/explore/categories.html` · HTTP 200 · title `Categories | V4 User` · observed 2026-09-15
- Quote: "Categories are labels used to organize content across the site. Any media can be assigned to a category".
- **Route as written:** `/category/{url-key}` — "a category with URL key `art` is browsable at `/category/art`".
- Category page shows name, optional description, a listing sortable by "**Most recent**, **Oldest**, **Most viewed**, **Most liked**, **AZ**", and "The standard **All / Actions** bulk action menu".
- ⚠ Categories are **admin-defined only** (created in admin Settings › Categories); users assign but cannot create them.

### Features › Explore › Tags

- URL `https://v4-user.chevereto.com/features/explore/tags.html` · HTTP 200 · title `Tags | V4 User` · observed 2026-09-15
- Quote: "Tags are user-defined keywords that can be assigned to any media to describe its content."
- **Routes as written:** listing `/explore/tags`; per-tag `/tag/{tag-name}` ("a tag named `sunset` is browsable at `/tag/sunset`").
- **Tag listing sorts:** "**Most recent**", "**Oldest**", "**Most viewed**", "**AZ**". Sidebar shows **Top Tags** — "a quick-access list of the most popular tags on the site".
- **Assigning tags:** at upload time via the per-file **Tags** field ("comma-separated list of tags"), or via the media **Edit** form.
- ⚠ No tag synonyms, tag moderation, machine tags, or per-tag privacy documented. Admins can edit/delete a tag only from the tag page (admin Dashboard › Tags).

### Features › Explore › Random Mode

- URL `https://v4-user.chevereto.com/features/explore/random.html` · HTTP 200 · title `Random Mode | V4 User` · observed 2026-09-15
- Full body quote: "To explore the site randomly, click the **Random** button". This is the entire page.

### Features › Search › Basic search

- URL `https://v4-user.chevereto.com/features/search/basic.html` · HTTP 200 · title `Basic search | V4 User` · observed 2026-09-15
- Quote: "In Chevereto you can search users, albums, and media."
- **Flow as written:** top bar **Search icon** → "Enter the **keyword**" → "**Submit** the form".

### Features › Search › Advanced search

- URL `https://v4-user.chevereto.com/features/search/advanced.html` · HTTP 200 · title `Advanced search | V4 User` · observed 2026-09-15
- Quote: "You can also search by category and system administrators can search by IP address."
- **Access:** "Click the **filter (sliders) icon** next to the search bar to open the **Advanced search** dialog".
- **Fields, verbatim:** **All these words** "Results must contain all entered words" · **This exact word or phrase** "Results must contain the exact phrase" · **None of these words** "Results must not contain these words" · **IP address** "Search uploads by IP address (administrators only)".
- ⚠ The intro sentence claims category search, but **no category field appears in the documented field table**. Internal inconsistency recorded as observed. **No date-range, size, licence, colour, camera/EXIF, or geo search is documented** — a notable gap versus Flickr-like expectations.

### Features › Listings › Content Listings

- URL `https://v4-user.chevereto.com/features/listings/content.html` · HTTP 200 · title `Content Listings | V4 User` · observed 2026-09-15
- Quote: "Content listings refer to those that list content from a user, an album, or a category."
- **Sorts, verbatim:** Newest, Oldest, Most viewed, Most liked, A-Z. *(Note: "Newest" here vs "Most recent" elsewhere — inconsistent labelling across pages.)*

### Features › Listings › Viewer

- URL `https://v4-user.chevereto.com/features/listings/viewer.html` · HTTP 200 · title `Viewer | V4 User` · observed 2026-09-15
- Quote: "The media viewer opens media in fullscreen directly within a listing, without navigating away from the page."
- **Navigation keys, verbatim:** Next media `→` (Right arrow) · Previous media `←` (Left arrow) · Close viewer `Esc`.
- Quote: "the same Actions shortcuts are available (`L` to like, `S` to share, `E` to edit, `Del` to delete, etc.)."
- Quote: "To open the full media page, click the title link displayed at the top of the viewer."

### Features › Listings › Editing

- URL `https://v4-user.chevereto.com/features/listings/editing.html` · HTTP 200 · title `Editing | V4 User` · observed 2026-09-15 · Requires Login
- **Multiple selection methods, verbatim:** "click **All** or the `.` key"; "Click the **checkbox** to select items"; "**Right-click** (long press) to select items"; "**Drag** selection with the cursor to select items"; "Click **Actions**".
- **Individual editing — Media:** Delete, Create album, Move, Edit, NSFW flag (unsafe content), Like, Share.
- **Individual editing — Albums:** Delete, Move, Edit, Like, Share.

### Features › Listings › Actions

- URL `https://v4-user.chevereto.com/features/listings/actions.html` · HTTP 200 · title `Actions | V4 User` · observed 2026-09-15 · Requires Login
- Quote: "The actions menu is contextual, appearing depending on the listing content and who is requesting that listing."
- **Common actions:** Select all `.` · Clear selection `Z` · Delete `Del`. Quote: "Administrators can delete content in listings."
- **General listings (Explore + search results) — Media:** Get embed codes `K` · Flag as safe `V` · Flag as unsafe `F` · Assign category `C`.
- **User listings — common:** Edit `E` · Share `S` · Move to album `M` · Delete `Del` · Select all `.` · Clear selection `Z`.
- **User listings — media:** Get embed codes `K` · Flag as safe `V` · Flag as unsafe `F` · Assign category `C` · Like `L` · Share `S`.
- **User listings — album:** Create album `A` · Upload to album `P` · Create sub-album `J`.
- **Album cover:** `H` — "You will find the cover option next to the download icon."
- **Album privacy options, verbatim:** "Public", "Private (just me)", "Private (anyone with the link)", "Private (password protected)".
- Quote: "Media will be private if it is within a private album or sub-album. Media on its own cannot be private."
- ⚠ **Internal inconsistency in this page:** under "Select all (.)" it says "To clear the selection, click **Clear** (on the right) or use the `Z` key. Or simply use the `J` shortcut" — but `J` is documented everywhere else as "Create sub-album". Recorded verbatim; not resolved.
- ⚠ **Flag as safe/unsafe (`V`/`F`) is listed for general listings**, which would let ordinary users re-flag others' content; the admin manual's **Lock NSFW editing** setting is the stated control. No user-facing "report/flag for moderator review" feature exists.

### Features › Content › Album

- URL `https://v4-user.chevereto.com/features/content/album.html` · HTTP 200 · title `Album | V4 User` · observed 2026-09-15
- Quote: "An album is a user-level content container that works like a folder."
- **Header metadata, verbatim:** Title, File count, Date ("shown as relative time"), Views, Description.
- **Privacy table, verbatim:** Public "Visible to anyone" · Private (just me) "Visible only to the album owner" · Private (anyone with the link) "Visible to anyone who has the direct URL" · Private (password protected) "Requires a password to view".
- Quote: "Individual media files cannot be made private on their own — privacy is controlled at the album level."
- **Sub-albums:** "A sub-album is an album contained within another album." Quote: "Sub-albums have their own name, description, and privacy settings independent of the parent album." Shown in the **Sub albums** tab; created with **Create sub album** / `J`.
- **Sorting:** Most recent, Oldest, Most viewed, Most liked, A-Z.
- **Sharing:** **Share** / `S` — "The share dialog provides a direct link to the album and options to share to social networks."
- **Likes:** "The like button is shown as a heart icon on each media item in the listing."
- **Embed-code formats, verbatim table (this is the authoritative list):**

| Format | Options |
|---|---|
| Link | Viewer link, Direct link, Frame link, Thumbnail link, Medium link |
| HTML | Embed, Full linked, Medium linked, Thumbnail linked |
| Markdown | Full, Full linked, Medium linked, Thumbnail linked |
| BBCode | Full, Full linked, Medium linked, Thumbnail linked |

- **Create album:** Name (required), optional Description, Privacy.
- **Edit album:** "changing the **Name**, **Description**, and **Privacy** setting (including adding or removing a password)".
- **Delete album**, **Album cover** (`H`), **Move to album** (`M`).
- **Actions reference keys, verbatim:** Create album `A` · Create sub-album `J` · Edit `E` · Move to album `M` · Get embed codes `K` · Share `S` · Like `L` · Flag as safe `V` · Flag as unsafe `F` · Delete `Del` · Select all `.` · Clear selection `Z`.
- ⚠ **No album-level collaboration, no licence/rights field, no EXIF-based geo/map, no ordering/manual sort, no album download-as-zip** documented.

### Features › Content › Media

- URL `https://v4-user.chevereto.com/features/content/media.html` · HTTP 200 · title `Media | V4 User` · observed 2026-09-15
- **Metadata shown, verbatim:** Title · "Dimensions, format and file size — e.g. `1429 × 636 — JPG 154.6 KB`" · "Uploaded to — the category it belongs to, how long ago it was uploaded, and the view count" · "Tags — clickable pill chips linking to each tag page, shown only when tags have been assigned".
- **Action buttons, verbatim:** Edit (requires Login) · Delete (requires Login) · Download ("Download the original file") · Share · Like.
- **Tabs:** **About** — "If no description was provided at upload time, it reads "No description provided.""; **Embed codes** — same four formats as Album; **Info** — "Shows technical metadata about the file."
- **Edit form fields, verbatim:** Title ("optional display name") · Tags ("optional comma-separated tags") · Album ("assign to one of your albums") · Category ("assign to a site category") · Flag not safe ("mark the media as NSFW") · Description.
- **Album thumbnails:** "thumbnails of the other items in that album are displayed at the bottom of the page."
- ⚠ **No comments UI is documented on the media page** even though admin External services configures a Comments API and Notifications mentions comment notifications. **No licence field, no EXIF map, no download-size picker, no versioning/replace-file.**

## Integrations

### Integrations › ShareX

- URL `https://v4-user.chevereto.com/integrations/sharex.html` · HTTP 200 · title `ShareX | V4 User` · observed 2026-09-15
- Quote: "You can easily use ShareX with your Chevereto website to upload media directly from your computer thanks to the Chevereto API V1 ."
- Quote: "Since ShareX version 9.4.0 you only need to: Go to image **destination settings**, Select **Chevereto**, Fill your website details".
- **Legacy custom-uploader JSON, verbatim keys:** `Name`, `RequestType` `"POST"`, `RequestURL` `"http://mysite.com/api/1/upload"`, `FileFormName` `"source"`, `Arguments` (`key`, `format` `"redirect"`, `source` `"%input"`), `ResponseType` `"RedirectionURL"`, `RegexList`, `URL`, `ThumbnailURL`, `DeletionURL`.
- Quote: "Since Chevereto V4.0, users can create their own API key which is compatible with ShareX." *(Only in-manual occurrence of a version string, "V4.0".)*
- ⚠ Note the legacy API form uses a `key` argument while the user API page uses an `X-API-Key` header. Both recorded verbatim.

### Integrations › PUP (Popup Upload Plugin)

- URL `https://v4-user.chevereto.com/integrations/pup.html` · HTTP 200 · title `Popup Upload Plugin | V4 User` · observed 2026-09-15
- Quote: "The Popup Upload Plugin (PUP) is a lightweight JavaScript file that adds Chevereto image uploads to external websites."
- Quote: "When PUP is enabled, open `/plugin` on your Chevereto site to get integration instructions."
- **Install snippet, verbatim:** `<script async src="//demo.chevereto.com/sdk/pup.js" data-url="https://demo.chevereto.com/upload"></script>`
- Quote: "PUP works in modern HTML5 browsers on desktop and mobile." "Tested platforms include Windows, macOS, Linux, and Android (Chrome)."
- **Options (all configured as `data-<key>`), with stated defaults:**

| Option | Type | Default (as stated) | Values / notes (verbatim) |
|---|---|---|---|
| `url` | String | — | "Target Chevereto website URL." |
| `palette` | String | `default` | `default, clear, turquoise, green, blue, purple, darkblue, yellow, orange, red, grey, black` |
| `auto-insert` | String | `bbcode-embed-medium` | `viewer-links, direct-links, frame-links, thumb-links, medium-links, delete-links, html-embed, full-html-embed, medium-html-embed, thumb-html-embed, markdown-embed, full-markdown-embed, medium-markdown-embed, thumb-markdown-embed, bbcode-embed, full-bbcode-embed, medium-bbcode-embed, thumb-bbcode-embed`. "Use `0` to disable auto-insert." |
| `auto-close` | Integer | `1` | `0`, `1` |
| `sibling` | String | — | "CSS selector used as the reference node for button insertion." |
| `sibling-pos` | String | `after` | `before`, `after` |
| `vendor` | String | `auto` | `bbpress, discourse, discuz, ipb, mybb, nodebb, phpbb, smf, vanilla, vbulletin, woltlab, xenforo` |
| `mode` | String | `auto` | `auto`, `manual` |
| `target` | String | `auto` | "CSS selector for target editable content." |
| `lang` | String | `auto` | `ar, cs, de, es, fi, fr, id, it, ja, nl, pt_BR, ru, zh_CN, zh_TW` |
| `container-class` | String | `chevereto-pup-container` | "Mapped to `%cClass` in templates." |
| `button-class` | String | `chevereto-pup-button` | "Mapped to `%bClass` in templates." |
| `html` | String | — | "Custom HTML and CSS ." |
| `css` | String | — | "Custom HTML and CSS ." |
| `fit-editor` | Integer | — | `0`, `1` |
| `observe` | String | — | "CSS selector for elements that trigger sibling observation on click" |
| `observe-cache` | Integer | `1` | `0`, `1` |

- **Template placeholders, verbatim:** `%x` "PUP button observer (must be used to trigger button action)" · `%cClass` · `%bClass` · `%iClass` · `%iconSvg` "Vector icon in the form of a ready-to-use SVG HTML tag" · `%text` "Translated button text". Palette colour placeholders `%1 … %n`.
- **Manual binding, verbatim:** `data-chevereto-pup-trigger` and `data-target` on your own button.
- **Security-relevant quotes:** "PUP uses the postMessage API to communicate with the Chevereto website." "It restricts accepted origins and validates message payloads. PUP only listens to messages from the configured Chevereto origin."
- Quote: "The script is about 18KB (around 6KB gzipped)."
- ⚠ Note `delete-links` is an `auto-insert` value — implying delete-URL tokens exist — but **no delete-link/delete-token feature is documented on any other page of either manual.**

---

# NOT SHIPPED — roadmap / upcoming / beta

A full-text search of both manuals for `roadmap`, `upcoming`, `coming soon`, `beta`, `planned`, `preview`, `experimental` returns **zero matches**. **Neither manual contains a roadmap, upcoming-feature, or beta section.** Every documented capability is presented as shipped.

The only lifecycle marker found anywhere in either manual is a **deprecation**, recorded here for completeness:

| Item | URL | HTTP | Status as written |
|---|---|---|---|
| Settings › Guest api | https://v4-admin.chevereto.com/settings/guest-api.html | 200 | "This page is deprecated. The `/dashboard/settings/guest-api` route no longer exists." Settings merged into `/dashboard/settings/api`. Page still listed in the live sidebar. |

Additionally, one section is **published but empty**, which is a documentation gap rather than a roadmap item:

| Item | URL | Nature |
|---|---|---|
| Dashboard › Bulk importer › **Command** | https://v4-admin.chevereto.com/dashboard/bulk-importer.html | Heading renders with no body (verified in raw HTML: `<h3 id="command">…</h3> <!----> <h3 id="cron-entry">`). The bulk-importer CLI invocation is therefore **not published**. Not reconstructed from memory. |

---

# Requested topics ABSENT from both manuals

These were on the research brief but are **not documented anywhere in the admin or user manual**. Recorded as absent — NOT filled in from memory or from any other source.

| Requested topic | Status in the two manuals | Nearest documented thing |
|---|---|---|
| CLI commands (`app/bin/legacy` etc.) | **ABSENT.** No page documents any CLI binary or command. The one CLI section that exists (Bulk importer › Command) renders empty. | Bulk importer › Threads mentions an env var `THREAD_ID`; Cron entry links out to `v4-docs.chevereto.com/application/stack/cron.html` (not fetched). |
| Docker / container deployment | **ABSENT.** The string "docker" does not appear in either manual. | — |
| Environment variables | **ABSENT** as a documented surface. | Only `THREAD_ID` (Bulk importer › Threads). |
| Licensing / editions / activation | **ABSENT.** No licence page, no edition matrix, no activation flow, no Free/Lite/Pro gating on any setting. | Settings › Website › "Powered by Chevereto" is a plain toggle with no licence condition stated. |
| Admin API / API v2 | **ABSENT.** | Settings › API exposes only Enable API user / Enable API guest / Public API key. API reference is external (`v4-docs` API V1, not fetched). |
| SSO (SAML / OIDC / generic OAuth) | **ABSENT.** | Only the 30 named per-provider OAuth login providers. |
| Cloudflare Turnstile | **ABSENT.** | CAPTCHA API values are `reCAPTCHA v2`, `reCAPTCHA v3`, `hCaptcha` only. |
| User groups / role management | **ABSENT.** No group CRUD, no per-group permissions or quotas. | Fixed three-value role enum per user: User / Manager / Administrator. |
| Per-user storage quotas | **ABSENT.** | Only per-storage **Storage capacity** (e.g. "20 GB") on Upload storage / Site storage. |
| Multi-server / multi-site | **ABSENT.** | Multiple upload storages; `Website mode: Single profile`. |
| Admin notification settings | **ABSENT** as a settings page. | Scattered toggles: Flood protection › Notify to email; Settings › Users › Notify on user signup; Settings › System › Display available updates notification. |
| User-facing report / flag-for-review | **ABSENT.** There is no "report this content" feature. | Only the NSFW **Flag as safe/unsafe** (`V`/`F`) actions, plus admin **Approve** in the moderation queue. |
| Self-service account deletion | **ABSENT** from the user manual. | Admin-only **Delete user** button (Dashboard › Users › Account tab). |
| Comments UI | **ABSENT** from the user manual. | Admin Settings › External services configures Disqus or arbitrary JavaScript/HTML; there is no first-party comment engine. |
| 2FA backup / recovery codes | **ABSENT** as documentation, though **referenced**: Password forgot says "if you don't remember or have lost your password and don't have backup codes". Security page documents only TOTP enrol/disable. | — |
| Delete links / delete tokens | **ABSENT** as a documented feature, though `delete-links` is a valid PUP `auto-insert` value. | — |
| Dedicated "statistics" page | **ABSENT** as a separate page. | Dashboard › Home chart (Files, Disk, Users, Albums, Tags; 1W/1M/3M/6M/1Y) and Totals. |
| Dedicated "images"/"users"/"pages"/"dashboard" settings pages as named in the brief | Partially differently named. | Images ≈ Settings › File uploads + Settings › Content; Users ≈ Settings › Users; Pages ≈ Settings › Pages (exists); "Dashboard settings" ≈ no such page. |
| "Assets storage" | Present under a different name. | Settings › **Site storage** — "control where website assets (backgrounds, avatars, etc.) are stored". |
| Upgrade / installer | **ABSENT** as a page. | Settings › System › Automatic updates check, Display available updates notification, Dump update query. |
| Flickr-like: licensing/rights, EXIF geo map, date/camera/colour search, groups/pools, galleries, photostream, download-size picker, album zip download, collaboration, block/mute | **ABSENT** — none documented. | Nearest: albums + sub-albums, tags, categories, likes, following, Discovery (Recent/Trending/Popular/Following). |

**Out-of-scope pointers observed (NOT fetched, recorded only as links the manuals themselves make):** `https://v4-docs.chevereto.com/developer/api/api-v1.html`, `https://v4-docs.chevereto.com/application/stack/cron.html`, `https://v4-docs.chevereto.com/application/stack/php.html#php-configuration`, `https://v4-docs.chevereto.com/developer/customization/language.html`, `https://releases.chevereto.com/`. These are official Chevereto domains but are **not** part of the admin or user manual and were deliberately left unfetched for this brief.

---

# Sidebar sections not fetched

**None.** Every entry in both sidebars was fetched successfully.

- Admin sidebar documents enumerated: 38 (Account 1; Dashboard 6; Settings 29; Features 2) plus the index page = **39 fetched, 0 failed**. "Home › Links" is an in-page anchor, not a document.
- User sidebar documents enumerated: 33 (User 15 = Account 3 + Profile 7 + Settings 5; Features 16 = Upload 3 + Explore 5 + Search 2 + Listings 4 + Content 2; Integrations 2) plus the index page = **34 fetched, 0 failed**. "Home › Links" is an in-page anchor, not a document.
- The sidebar "Home › Links" entry on both sites is an in-page anchor (`/#links`), not a separate document; its content is captured under "Home (index)" above.

**One non-sidebar URL failed** (discovered by crawling, not listed in any sidebar):

| URL | HTTP | Note |
|---|---|---|
| https://v4-user.chevereto.com/features/explorer/explore.html | **404 FAILED** | Broken internal link present in the user manual's rendered pages (note `explorer/`, not `explore/`). Recorded as FAILED; content NOT supplied from memory. |

---

# INFERRED items

Everything above is quoted or transcribed from the pages. The following are the only inferences in this file, and each is marked as such:

1. **INFERRED** — The uniform `Last-Modified` value per site is a static-site *deploy* timestamp rather than a per-page edit date. Basis: the value is byte-identical across all 39 admin pages and all 34 user pages, and the sites are GitHub Pages builds. The manuals themselves print no dates.
2. **INFERRED** — "Likes" and "favorites" are the same feature. Basis: the Liked page describes itself as "a personal collection of favourited content" while the mechanism is the like/heart action. No separate favorites feature is documented.
3. **INFERRED** — Settings › **Site storage** is what the brief calls "assets storage". Basis: the Features › Upload storage page cross-references it as controlling "where website assets (backgrounds, avatars, etc.) are stored".
4. **INFERRED** — The absence of any Free/Lite/Pro marker means these manuals document a single undifferentiated V4 feature set. This is an inference about *documentation scope only*; it is **not** evidence about what any particular Chevereto edition ships. The manuals cannot settle the Free/Lite/Pro functional-union question, and no other source was consulted.
5. **INFERRED** — The `JPEG` discrepancy (admin lists it, user manual does not) is a documentation inconsistency rather than two different format sets. Not verified against any running instance.

---

# Reconciliation notes for Vizra

Observed contradictions *within* the official manuals, recorded so they are not silently resolved during planning:

1. **Login providers count** — Features page lists 30 providers (includes Apple); Settings page lists 29 (omits Apple).
2. **Upload from URL** — user manual says "exclusive to system administrators"; admin manual presents **Enable uploads (URL)** as an unqualified global toggle.
3. **Supported formats** — admin lists `JPEG` separately, user manual does not.
4. **Advanced search** — prose claims category search; the documented field table has no category field.
5. **Keyboard shortcut `J`** — documented as "Create sub-album" everywhere, but the Actions page's "Select all" section also tells the reader to "use the `J` shortcut" to clear a selection.
6. **Sort labels** — "Newest" (Content Listings) vs "Most recent" (everywhere else).
7. **API auth** — user Settings › API uses the `X-API-Key` header; the ShareX legacy uploader passes `key` as a POST argument.
8. **Comments** — admin configures a Comments API and notifications fire on comments, but no comment UI is documented on the media page, and there is no first-party comment engine.

Security/compliance items that are Chevereto behaviour but conflict with Vizra's AGENTS.md guardrails (flagged, not proposed as parity targets):

- **Settings › Pages** lets an admin author raw `.php` executed by the app ("Internal page is a `.php` file in which you can do anything").
- **Settings › Theme** provides unrestricted **Custom JS code** / **Custom CSS code** injection into all views.
- **Settings › External services › Analytics code** and **Comment code** are unrestricted HTML/JS injected into all views.

*End of evidence file. Captured 2026-09-15 from official Chevereto domains only. No paid demo, private source, or third-party mirror was inspected.*
