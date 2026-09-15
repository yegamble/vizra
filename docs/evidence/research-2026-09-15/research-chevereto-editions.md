# Chevereto editions, features, releases, API and requirements — official-source evidence

- **Observation date (all fetches):** 2026-09-15
- **Researcher:** docs-researcher agent (Vizra)
- **Source restriction applied:** `chevereto.com`, `*.chevereto.com`, `github.com/chevereto` only. No third-party sources, no demo inspection, no private/paid source inspection.
- **Method caveat (read this before quoting):** every page was retrieved with the `WebFetch` tool, which converts the page to markdown and then runs an extraction model over it. Quoted strings below are as returned by that extraction. They are faithful to the page as returned, but this is *not* a byte-exact scrape; where a quote is load-bearing for a parity decision, re-verify against the live URL before relying on it. Nothing below is filled in from model memory — anything not returned by a fetch is recorded as a gap or FAILED.
- **Marking convention:** `INFERRED` = my conclusion, not something the page said. Everything else came back from a fetch.

---

## 0. Source ledger (every URL attempted)

| # | URL fetched | Page title returned | Version/date on page | HTTP result |
|---|---|---|---|---|
| 1 | `https://v4-docs.chevereto.com/introduction/editions/compare.html` | Compare editions \| Chevereto V4 Docs | "Last Updated: 9/14/2026, 3:32:06 PM" | ok |
| 2 | `https://v4-docs.chevereto.com/introduction/editions/` | — | — | **FAILED — HTTP 404.** Current official equivalent found via site nav on `https://v4-docs.chevereto.com/` = the four individual pages `/introduction/editions/compare.html`, `/chevereto-pro.html`, `/chevereto-lite.html`, `/chevereto-free.html`. There is no directory index page. |
| 3 | `https://v4-docs.chevereto.com/introduction/editions/chevereto-free.html` | Chevereto Free \| Chevereto V4 Docs | Last updated 9/14/2026 3:32:06 PM | ok |
| 4 | `https://v4-docs.chevereto.com/introduction/editions/chevereto-lite.html` | Chevereto Lite \| Chevereto V4 Docs | Last updated 9/14/2026 3:32:06 PM | ok |
| 5 | `https://v4-docs.chevereto.com/introduction/editions/chevereto-pro.html` | Chevereto Pro \| Chevereto V4 Docs | Last updated 9/14/2026 3:32:06 PM | ok |
| 6 | `https://chevereto.com/pricing` | Pricing - Chevereto self-hosted | "Latest release 4.5.7 (Elevado)" banner | ok |
| 7 | `https://chevereto.com/features` | Features - Chevereto self-hosted | "Latest release 4.5.7 'Elevado'" | ok |
| 8 | `https://v4-docs.chevereto.com/introduction/changelog.html` | — | — | **FAILED — HTTP 404.** Current official equivalent: per-minor pages under `/introduction/changelog/` (`4.5.html`, `4.4.html`, `4.3.html`, `4.2.html`, `4.1.html`, `4.0.html`, `welcome-back.html`), plus `https://chevereto.com/releases`. |
| 9 | `https://v4-docs.chevereto.com/introduction/changelog/4.5.html` | 🆕 4.5 Elevado \| Chevereto V4 Docs | Last updated 9/14/2026 | ok |
| 10 | `https://releases.chevereto.com/` | "Chevereto releases" | none shown | ok (content thin — navigation hub only, links to 4.X / 3.X / 2.X / 1.X branches; no dates or per-release notes rendered) |
| 11 | `https://chevereto.com/releases` | Chevereto releases - Chevereto self-hosted | Latest: 4.5.7, 2026-08-20 | ok |
| 12 | `https://github.com/chevereto/chevereto/releases` | Releases · chevereto/chevereto | Latest 4.5.7, Aug 20 2026 | ok |
| 13 | `https://v4-docs.chevereto.com/developer/api/api-v1.html` | — | — | **FAILED — HTTP 404.** (This URL is what web search surfaced; it is stale.) Current official equivalents, from the live docs sidebar: `/api/4/authorization.html`, `/api/4/tenants.html`, `/api/1/authorization.html`, `/api/1/file-upload.html`. |
| 14 | `https://v4-docs.chevereto.com/api/4/authorization.html` | Authorization (API V4) \| Chevereto V4 Docs | — | ok |
| 15 | `https://v4-docs.chevereto.com/api/4/tenants.html` | Tenants API \| Chevereto V4 Docs | — | ok |
| 16 | `https://v4-docs.chevereto.com/api/1/authorization.html` | Authorization (API V1) \| Chevereto V4 Docs | — | ok |
| 17 | `https://v4-docs.chevereto.com/api/1/file-upload.html` | File upload API \| Chevereto V4 Docs | — | ok |
| 18 | `https://v4-docs.chevereto.com/introduction/get-started/requirements.html` | — | — | **FAILED — HTTP 404.** Current official equivalent: the **Stack** section — `/application/stack/php.html`, `/application/stack/mysql-server.html`, `/application/stack/web-server.html`, `/application/stack/redis.html`, `/application/stack/utilities.html`, `/application/stack/cron.html`, `/application/stack/operating-system.html`. |
| 19 | `https://v4-docs.chevereto.com/application/stack/php.html` | PHP \| Chevereto V4 Docs | per-release PHP matrix incl. 4.5 | ok |
| 20 | `https://v4-docs.chevereto.com/application/stack/mysql-server.html` | MySQL Server \| Chevereto V4 Docs | per-release DB matrix incl. 4.5 | ok |
| 21 | `https://v4-docs.chevereto.com/application/installing/installation.html` | Installation \| Chevereto V4 Docs | — | ok |
| 22 | `https://v4-docs.chevereto.com/` | Home \| Chevereto V4 Docs | — | ok (used for authoritative sidebar/URL discovery) |
| 23 | `https://github.com/chevereto/v4-docs` | chevereto/v4-docs | Apache-2.0, 425 commits on main | ok |
| 24 | `https://v4-admin.chevereto.com/` | V4 Admin | — | ok (sidebar/URL discovery) |
| 25 | `https://v4-admin.chevereto.com/settings/external-services.html` | External services \| V4 Admin | — | ok |
| 26 | `https://v4-admin.chevereto.com/features/external-storage.html` | — | — | **FAILED — HTTP 404.** (Link published on `chevereto.com/features` is stale.) Current official equivalents: `https://v4-admin.chevereto.com/features/upload-storage.html` and `https://v4-admin.chevereto.com/settings/upload-storage.html`. |
| 27 | `https://v4-admin.chevereto.com/features/upload-storage.html` | Upload storage \| V4 Admin | — | ok |
| 28 | `https://v4-admin.chevereto.com/settings/upload-storage.html` | Upload storage \| V4 Admin (`/dashboard/settings/upload-storage`) | — | ok |
| 29 | `https://v4-admin.chevereto.com/features/login-providers.html` | Login providers \| V4 Admin | — | ok |
| 30 | `https://v4-admin.chevereto.com/settings/file-uploads.html` | File uploads \| V4 Admin (`/dashboard/settings/file-uploads`) | — | ok |
| 31 | `https://v4-admin.chevereto.com/settings/users.html` | Users \| V4 Admin (`/dashboard/settings/users`) | — | ok |
| 32 | `https://v4-admin.chevereto.com/dashboard/bulk-importer.html` | Bulk importer \| V4 Admin | — | ok |

**Failed fetches (5):** #2, #8, #13, #18, #26 — all 404, all with a current official equivalent identified and recorded above.

---

## 1. Edition comparison — `https://v4-docs.chevereto.com/introduction/editions/compare.html`

- **Page title:** "Compare editions | Chevereto V4 Docs"
- **Last Updated shown on page:** 9/14/2026, 3:32:06 PM
- **Observed:** 2026-09-15 — **HTTP ok**
- **Page's own framing (quote):** "This is a brief overview of the features available across Chevereto editions (Chevereto Free, Chevereto Lite, and Chevereto Pro)."

> **Structural note, important for parity work:** this page is *not* one uniform matrix. Each section has (a) a bullet list of capabilities with **no edition columns at all** — these are present in all editions unless a row later says otherwise — and (b) a Free/Lite/Pro table listing only the features that *differ* by edition. Both are reproduced below. Cell values use the page's own glyphs: `✅` = available, `–` = not available, or a literal string.

### 1.1 Files supported (no edition columns — applies to all editions)

Intro line (quote): "Upload and share the following media types from device file browser, drag and drop, on-the-fly device camera, clipboard, URL, ShareX and via API."

- `image/avif`
- `image/jpeg`
- `image/gif`
- `image/png`
- `image/webp`
- `image/bmp`
- `video/quicktime`
- `video/mp4`
- `video/webm`

### 1.2 Uploading features

Un-columned list (all editions):

- Image & Video uploads
- AVIF JPEG PNG BMP GIF WEBP MOV MP4 WEBM
- Chunked uploads
- Lossless media handling (JPEG auto-orientation & EXIF removal)
- User uploads, guest uploads
- API uploading (ShareX, etc)
- Equirectangular 360° images
- EXIF data (read, strip)
- Clipboard upload (copy/paste)
- Drag-and-drop upload (drop zone)
- File delete link
- Time-based auto-remove uploads
- Generate thumbs & medium sized images
- Generate video frame image
- Duplicate media detection
- Auto file-naming options
- Storage modes (date, direct)
- Upload user interface (container, page)
- Upload plugin (PUP.js, postMessage)
- Bulk importer (batch upload)

Edition table:

| Uploading features | Free | Lite | Pro |
|---|---|---|---|
| Upload moderation | – | ✅ | ✅ |
| Watermark image uploads | – | ✅ | ✅ |
| Asset storage API | Local, S3 | Local, S3 | All |
| External storage servers API | Local, S3 | Local, S3 | All |

### 1.3 Storage APIs

| Storage API | Free | Lite | Pro |
|---|---|---|---|
| Local | ✅ | ✅ | ✅ |
| Amazon S3 | ✅ | ✅ | ✅ |
| S3 compatible | ✅ | ✅ | ✅ |
| Google Cloud Storage | – | – | ✅ |
| Microsoft Azure | – | – | ✅ |
| Alibaba Cloud OSS | – | – | ✅ |
| SFTP | – | – | ✅ |
| FTP | – | – | ✅ |
| OpenStack Swift | – | – | ✅ |
| Backblaze B2 (legacy) | – | – | ✅ |

### 1.4 Content features (no edition columns)

- Listing viewer
- Dedicated Media, Album, Tags & Users listings
- Configure items per page
- Listing type (paginated/endless)
- Image listing size (fixed, fluid)
- Configure album listing requirement
- Configure listing columns per device (mobile, tablet, etc.)

### 1.5 Organization features (no edition columns)

- User defined Tags
- Albums & Sub-albums (nested)
- Categories
- Search
- Explore & Discovery

### 1.6 Tags features (no edition columns)

- On-the-fly tag creation
- Tag description
- Tag listings
- Tag filtering (users, albums)
- Tag autocomplete
- Top tags
- EXIF camera model auto-tagging

### 1.7 Album features (no edition columns)

- Nested albums (breadcrumbs)
- Album cover image
- Album privacy
- Album password
- Album description

### 1.8 Sharing features (no edition columns)

- Direct link sharing
- Sharing button
- Media oEmbed
- HTML, Markdown & BBCodes
- Embed codes on upload complete
- Embed codes on selected media
- Embed codes media page

### 1.9 User features (no edition columns)

- Multi-user support
- User profiles
- Private user profiles
- User-based API
- Roles available: admin, manager & user
- User management
- Guest API

### 1.10 Social features

Un-columned list:

- Call-to-action album buttons
- Random button
- Notifications
- List users

Edition table:

| Social features | Free | Lite | Pro |
|---|---|---|---|
| Followers | – | ✅ | ✅ |
| Likes | – | ✅ | ✅ |

### 1.11 Security features

Un-columned list:

- Two-Factor Authentication (2FA)
- Encrypt secrets
- Crypt-salted IDs

Edition table:

| Feature | Free | Lite | Pro |
|---|---|---|---|
| IP banning | – | – | ✅ |
| Stop words | – | – | ✅ |

### 1.12 Admin features

Un-columned list:

- Album creation on behalf of users
- Dashboard (admin UI)
- System stats & usage
- Website name
- Website document title
- Website description
- Website privacy mode (public, private)
- Default timezone
- Uploadable file extensions
- Guest uploads auto delete
- Upload threads
- Upload maximum image size
- Upload EXIF removal
- Upload max file size (users and guest)
- Upload path
- Upload file naming
- Upload thumb size
- Upload medium size and dimension
- Semantics
- Default palette
- Default font
- Image load max file size
- Image first tab
- Embed codes (content)
- Custom JS & CSS
- Universal CDN support
- Default language
- Logo & branding
- Logo type (vector, image, text)
- Logo height

Edition table (complete):

| Admin features | Free | Lite | Pro |
|---|---|---|---|
| Guest API key | ✅ | ✅ | ✅ |
| Homepage style | ✅ | ✅ | ✅ |
| Homepage cover images | – | ✅ | ✅ |
| Homepage title & paragraph | – | ✅ | ✅ |
| Homepage call to action | – | ✅ | ✅ |
| Pages | – | ✅ | ✅ |
| Lock NSFW editing | – | ✅ | ✅ |
| User min age required | – | ✅ | ✅ |
| User avatar max file size | – | ✅ | ✅ |
| User background max file size | – | ✅ | ✅ |
| Logo favicon image | – | ✅ | ✅ |
| OAuth2 login providers (Amazon, Google, Discord, etc) | – | ✅ | ✅ |
| Hide "Powered by Chevereto" footer | – | – | ✅ |
| Enabled languages | – | – | ✅ |
| Routing (user, image, album) | – | – | ✅ |
| Routing root | – | – | ✅ |
| External services | – | – | ✅ |
| Comments API (Disqus, JS) | – | – | ✅ |
| Analytics code | – | – | ✅ |
| Akismet spam protection | – | – | ✅ |
| StopForumSpam spam protection | – | – | ✅ |
| CAPTCHA (reCAPTCHA, hCaptcha) | – | – | ✅ |
| Configurable CAPTCHA threshold | – | – | ✅ |
| Shield by Project Arachnid | – | – | ✅ |
| Banners | – | – | ✅ |

### 1.13 Admin toggles

Un-columned list:

- Search (users and guest)
- Explore (users and guest)
- Random (users and guest)
- NSFW listings
- Blur NSFW content
- NSFW on random mode
- Banners on NSFW
- Upload toggle (users, guest)
- Upload (URL)
- Upload moderation
- Upload embed codes
- Upload redirection
- Upload duplication
- Upload expiration
- Upload NSFW checkbox
- Download button
- Right click
- Show Exif data
- Social share buttons
- Automatic updates check
- Dump update query
- Debug errors

Edition table (complete):

| Admin toggles | Free | Lite | Pro |
|---|---|---|---|
| User sign up | ✅ | ✅ | ✅ |
| User content delete | ✅ | ✅ | ✅ |
| Consent screen (age gate) | – | ✅ | ✅ |
| User notify sign up | – | ✅ | ✅ |
| User email confirmation | – | ✅ | ✅ |
| User email for social login | – | ✅ | ✅ |
| Watermarks | – | ✅ | ✅ |
| Auto language | – | – | ✅ |
| Language chooser | – | – | ✅ |
| SEO URLs (media and album) | – | – | ✅ |
| Cookie law compliance | – | – | ✅ |
| Flood protection | – | – | ✅ |

### 1.14 System features (no edition columns)

- Multitenancy support
- Image handling using GD or ImageMagick
- Theme palettes (10)
- One-click upgrade (web, CLI)
- Maintenance mode
- Email sending (SMTP, Postfix, AWS SES, Mailtrap, etc.)
- Cipher IDs
- Export user
- Docker support
- CLI console
- Built-in debugger (xrDebug)
- REPL (PsySH, Tinkerwel)
- Background file queue handling
- Configurable cache TTL
- Hreflang HTML tags
- Upload storage tools (regen stats, migrate records)
- Test-email tool

### 1.15 System tooling support (no edition columns)

- ExifTool
- ExifTran
- ffmpeg
- ImageMagick

### 1.16 Limits explicitly stated on the comparison page

- **The only numeric/enumerated limits on this page are the storage-API restrictions:** `Asset storage API` and `External storage servers API` = "Local, S3" for Free and Lite, "All" for Pro; plus the per-provider Storage APIs table (§1.3).
- **No user-count limit, no storage-size cap, no upload-count limit, and no site/domain limit appears anywhere on the comparison page.** (Gap recorded in §11.)

---

## 2. Edition pages

### 2.1 Chevereto Free — `https://v4-docs.chevereto.com/introduction/editions/chevereto-free.html` (ok)

- Title: "Chevereto Free"; Last Updated 9/14/2026 3:32:06 PM
- Quote: "A self-hosted media-sharing solution designed for personal use"
- Quote: provides "core functionality to create a personal media hosting website on your own server"
- Exclusions quote: the Free edition omits moderation tools and "other enhancements available in Chevereto Lite and Chevereto Pro."
- License: Open Source, source at the `chevereto/chevereto` GitHub repository. (License identifier AGPLv3 comes from the pricing page — see §3.)
- No numeric limits stated.

### 2.2 Chevereto Lite — `https://v4-docs.chevereto.com/introduction/editions/chevereto-lite.html` (ok)

- Title: "Chevereto Lite"; Last Updated 9/14/2026 3:32:06 PM
- Quote: "A lightweight, affordable media-sharing solution designed for communities of all types"
- Quote: offers "a simple and secure way to share and organize media within trusted groups."
- Listed: image and video hosting with upload/organization/management; multi-user account support; community sharing; affordable pricing; centralized shared spaces; private and secure content; upgrade path to Chevereto Pro.
- License: **not stated on this page.**
- No numeric limits stated.

### 2.3 Chevereto Pro — `https://v4-docs.chevereto.com/introduction/editions/chevereto-pro.html` (ok)

- Title: "Chevereto Pro"; Last Updated 9/14/2026 3:32:06 PM
- Quote: "Chevereto Pro edition is a robust self-hosted media-sharing platform tailored for professional and commercial use."
- Listed: image and video hosting with upload and management; multi-user support; advanced storage integrations (**"S3, Cloudflare R2, and others"**); full branding customization; scalable infrastructure.
- Use cases listed: independent media hosting services; digital asset organization/distribution; client-branded media-sharing platforms for agencies; private organizational content hosting.
- Purchase at `chevereto.com/pricing`. No numeric limits stated.

---

## 3. Pricing — `https://chevereto.com/pricing` (ok)

- Page title: "Pricing - Chevereto self-hosted"; page shows latest release **4.5.7 ("Elevado")**.

| Edition | Price | License | Feature framing | Support |
|---|---|---|---|---|
| Chevereto Free | **$0 Forever**, no subscription | **AGPLv3 license** | "Essential features" | "GitHub issues support" |
| Chevereto Lite | **$10 monthly** | Proprietary license | "More features" | Community support |
| Chevereto Pro | **$99 yearly** ("Best value", saves $21 annually) | Proprietary license | "All features" | Pro support, 30-day trial |

Shared across paid editions, as listed: perpetual usage rights; **unlimited websites deployment**; continuous software releases and bug fixes; community and support access.

**No user limits, storage caps, or domain restrictions are stated on the pricing page** (beyond "unlimited websites").

---

## 4. Features page — `https://chevereto.com/features` (ok)

- Page title: "Features - Chevereto self-hosted"; shows "Latest release 4.5.7 'Elevado'".
- The page is a very long marketing + capability enumeration. Edition attribution is **almost entirely absent** on this page — it does not tag claims Free/Lite/Pro. Where a claim conflicts with §1's edition table, **§1 governs**. Treat everything here as "exists somewhere in the product line", not "exists in Free".

### 4.1 Storage / infrastructure

- "Take total control of your visual content. Scalable multi-cloud storage"
- "Effortlessly offload high-volume images and videos across your choice of S3-compatible cloud providers"
- Storage names listed on the page: "Amazon S3", "S3 compatible", "Vultr Object Storage", "DigitalOcean Spaces", "Dreamhost Cloud Storage", "Minio", "Tencent Cloud Object Storage", "Wasabi", "Alibaba Cloud", "Microsoft Azure", "Backblaze B2", "Google Cloud", "OpenStack", "FTP/SFTP"
- "Deploy Chevereto on virtually any server in minutes"
- "Built-in one-click software updates"

### 4.2 Import / migration

- "Bring over your existing media archives in minutes"
- "Preserves users, albums, categories, tags, and file data"

### 4.3 Embedding into other software

- "Add instant media uploading to your existing website or forum"
- "XenForo, Discourse & MyBB plugins"
- "Upload plugin for third-party software"
- "bbPress, Discourse, Discuz!" plugins
- "Invision Power Board, phpBB" plugins

### 4.4 Authentication / identity

- "Remove registration friction and grow your user base faster"
- "Google & Facebook" social login
- "Twitter (X) & Discord" OAuth2 integration
- Additional providers named: "Amazon", "Discord", "GitHub, GitLab, Instagram", "Reddit, Twitch, WeChat", "Yandex"
- "With email address + password" registration; "With login providers" registration
- "Configurable signup enabled/validation"; "Minimum age required"
- "Two-factor authentication"
- "API key" management; "Connected login providers" display

### 4.5 Anti-abuse / moderation / safety

- "Akismet & Project Arachnid Shield for spam and CSAM"
- "Turnstile, reCAPTCHA & hCaptcha bot defense"
- "Cloudflare Turnstile" CAPTCHA; "reCAPTCHA v2, v3" options; "hCaptcha" bot protection
- "Akismet" spam service; "StopForumSpam" integration; "Project Arachnid" CSAM detection
- "ModerateContent integration"
- "Configurable uploads incoming approval"
- "Stop words filtering"
- "Prevent automated abuse from draining your bandwidth and storage"
- "Instantly detecting and blocking malicious bulk uploads"
- "Avoid malicious attempts to flood your website"; "Set limits by minute, hour, week and month"; "Get flood reports instantly to your email"; "Protects on image uploads, album creation"; "Protects on account creation, account login"
- "Ban any IP from using the entire system"; "Set expiration date"; "Set message, HTML display or URL redirection"
- "NSFW / SFW flagging"; "Configurable locking for NSFW editing"; "Blur for NSFW content"

> ⚠️ **Turnstile note.** "Turnstile, reCAPTCHA & hCaptcha bot defense" appears on `chevereto.com/features`, but the v4-admin External services page (§8) lists CAPTCHA providers as **reCAPTCHA v2, reCAPTCHA v3, hCaptcha only** — Turnstile is not listed there, and the compare page's CAPTCHA row reads "CAPTCHA (reCAPTCHA, hCaptcha)". Conflict recorded; do not treat Turnstile as confirmed-shipped without re-verifying.

### 4.6 Branding / customization

- "Set custom call-to-action buttons on any album"
- "Rename core system terms to fit your brand or industry"
- "Upload your custom logos and favicons, set default theme palettes"
- "Use your custom logo and favicon"; "Supports vector and raster logos"
- "Optional 'Powered by Chevereto' at homepage"
- "Custom CSS code" support; "Custom JS code" support
- "Theme hooks for adding custom code"; "Theme overrides (customize only what you need)"
- "System (follow system color)" palette; "Light, Dark" color palettes; "Flickr, Imgur, DeviantArt" color schemes; "Lush, Graffiti, Abstract" color palettes; "Cheers, CMYK" color schemes
- "One-click configure system wide font"; "Zero dependency web-safe fonts"

### 4.7 Search & discovery

- "Easily locate users, albums, and media files"
- "Full-text & exact phrase matching"
- "Basic and advanced search"; "Search images, albums and users"
- "Advanced search with excluded words"; "Full text search engine"
- "Search operators" including category, storage, IP
- "Explore recent, trending, popular, animated and social content"
- "Sort by date, views, likes, A-Z"
- "Automatically surface your most popular media"
- "Drive organic content discovery"

### 4.8 Albums / organization

- "Folder-style content containers" with "Nested sub-album support"
- "Public, private and guest albums"; "Sub-albums (nested albums)"
- "Configurable cover image"; "Editable description, name and privacy"
- "Privacy modes (public, private, link, password)"
- "Call-to-action buttons" for albums; "Drag to sort" album content
- "Well-organized category structure creates intuitive navigation"
- "Configure name, URL and description" for categories; "SEO-friendly categories"; "Category-based listings"
- "User-defined tags"; "Manage tags"; "Manage categories"

### 4.9 Social / community ("Flickr-like" items)

- "Boost user retention and return visits"; "Foster long-term brand loyalty"
- "Like system for images and albums"; "Configurable site-wide feature"; "Available in listings and content view"; "Liked content gets stored in user's listing"; "Likes provide instant feedback"
- "Follow system for users"; "Generates a curated list with followed content"; "User's following and followers lists"
- "Alerts for social triggered actions"; "Alert on content liked"; "Alert on new follower"
- "Disqus community comments"; "Disqus comments (SSO)"
- "Public and private profiles"; "User albums"; "Website" and "Bio" profile fields; "Avatar and profile background images"; "Search for user's content"; "Content counters"; "Social counters"

### 4.10 Media handling / formats / 360 / video

- "Image & Video uploading"
- "Supported image formats" including **AVIF, JPEG, PNG, BMP, GIF, WEBP, MP4, MOV, WEBM**
- "Configurable supported image formats"
- "Lossless JPEG handling"
- "Natively supporting interactive panoramas and virtual tours"
- "360-degree viewing allows your users to share captivating content"
- "Supports 360 images (equirectangular, gopro)"
- "Play animated GIF images"
- "Three (3) image Sizes: Thumbnail, medium and full"
- "Maximum image size (width/height) auto-resizing"
- "EXIF show/hide info"; "Keep image Exif data" user option; "Automatically extract camera metadata and organize massive media collections"

### 4.11 Upload sources & upload mechanics

- "Drag-and-drop upload"; "Clipboard upload"; "Multiple-image upload"
- "Upload from your computer, phone or image URL"
- "Chunked uploads"; "Simultaneous upload threads"
- "Public/private uploading"; "Configurable guest uploads"
- "Duplicate upload detector (Daily + IP + hash)"
- "Date-folders (Y/m/d)" storage mode; "Directory (/images)" storage mode
- File naming: "Original original file name", "Random filename", "Mixed (Original + Random)", "Match the image ID"
- "ShareX integration" / "ShareX support"
- "Public image upload API" / "Public API" for uploads; "User-based API"
- "Enable expirable uploads"; "Auto delete guest uploads"; "Auto-delete uploads" user option

### 4.12 Watermarks

- "Protect your copyright/brand"
- "Configure watermark image, opacity and position"
- "Adaptive watermarks (fits target image)"
- "Configurable per user group (guest, user, admin)" — "On guest uploads", "On user uploads", "On admin uploads"
- "Enable watermark on GIF image uploads"
- "Minimum image size" for watermark application
- "Watermark position", "Watermark percentage", "Watermark margin", "Watermark opacity"

### 4.13 Pages, SEO, routing

- "Build landing pages, terms, or promotional offers effortlessly"
- "Pages manager"; "PHP & HTML support"; "Raw HTML and rich text editing"
- "Configurable page settings" (title, URL, status, type); "Visibility"; "Link attributes (rel + target + icon)"; "Meta keywords and description (SEO)"; "Sort order"; "Source code" editing; "Internal page type"; "URL key"; "File path"
- "Custom URLs and navigation links"
- "Internal only redirection (zero link juice)"; "SEO optimized titles and descriptions"; "Friendly descriptive URLs"; "Foreign characters support for URLs"; "Uses hreflang"
- "Unique short and SEO URL"

### 4.14 Sharing / embeds

- "One-click social publishing, universal short links"
- "Embed & sharing codes"; "HTML, BBCode, Markdown" sharing formats
- "Supports oEmbed sharing"; "Get embed codes for selection"; "Copy sharing codes"
- "One-click sharing to Facebook, Twitter, Whatsapp"; "Sharing to Telegram, Weixin, Weibo"; "Sharing to QQ, Reddit, VK"; "Sharing to Blogger, Tumblr, Pinterest"
- "Support Twitter Cards"; "Support Facebook Open Graph"

### 4.15 Users, roles, quotas

- "Role-based user permissions"; "User, Admin, Manager" roles
- **"Individual storage and access limits"** ← the only per-user quota claim found anywhere in the docs set
- "Multi-user support"
- "Create users" from admin
- "Profile privacy" configuration; "Language" and "Timezone" user settings; "Newsletter" subscription option; "Show NSFW on listings" user option

### 4.16 Site modes (community vs personal/"single-user gallery")

- "Transform your platform into an exclusive, single-user gallery"
- "Personal mode streamlines the interface"
- "Community" mode (multiple users, social features); "Personal" mode (photo/store portfolio)
- "Mode" configuration; "Personal mode target user"; "Personal mode routing"
- "Website privacy mode"; "Content privacy mode"

### 4.17 Multitenancy / multi-site

- "Tenants API with key authorization"; "Request signing" for tenant API
- "Tenant lifecycle endpoints" (list, create, get, edit, delete)
- "Tenant install and user password reset endpoints"
- "Tenant plans API"; "Tenants CLI for provisioning"; "Tenants API key" management
- "Tenant plans, cache refresh and stats refresh commands"; "Tenants jobs worker"

### 4.18 Dashboard / statistics / admin tooling

- "Real-time metrics, manage users, and adjust settings"
- "Content stats (number of images, users, etc)"; "System runtime information"
- "Manage ALL content (images, albums, users)"; "System-wide content manager"; "Manage single/multiple content"
- "Drag-select for mass selection actions"; "Bulk actions"; "Create album"; "Move to album"; "NSFW flagging"; "Delete"; "Keyboard shortcuts"
- "One-click check for updates"; "One-click system upgrade"; "One-click license key handling"
- "Debug" support; "Custom error handlers with local and remote support"; "One-click enable debug reporting for admin"
- "Extremely configurable" system

### 4.19 Legal / consent / ads

- "Automated age-gate prompts"; "Consent screen (age verification)"; "Enable consent screen"; "Consent screen cover image"
- "Custom legal disclaimers"
- "EU Cookie law display"
- "Manage banners directly from the admin panel"; "Support any banner HTML/JS code and size"; **"16 predefined banner placements"**

### 4.20 Security posture claims

- "Non-enumerable IDs for the content"; "Uses alphanumeric IDs instead of actual integer"
- "Safely stores all sensitive application data"; "Service credentials" encryption; "Two-factor secrets" encryption; "Configurable"; "Re-encryption option available"
- **"Not encrypted source code"**
- "Based on own developed frameworks"
- "System-wide CSRF protection"; "Uses a cipher to store sensitive data"; "Uses hashing for passwords and API keys"

### 4.21 i18n / responsive

- "Automatic browser language detection"; "Manual and automatic language detection"; "Configurable allowed languages"; "Supports translation overrides"
- **"Over 30 built-in languages"**
- "Responsive layout (multi-device)"; "Optimized for any screen resolution"; "Works on phones, phablets, tablets and desktops"
- "Endless scrolling or classic pagination"; "Fixed-height or fluid" listing layout; "Listing columns per device" ("Phone, Phablet, Tablet, Laptop, Desktop")

### 4.22 Homepage / CDN / misc

- "Turn your front page into a high-converting growth engine"
- "Universal CDN support" / "CDN provider" integration
- "Website name, doctitle, description"; "HTTPS" configuration; "Default time zone"
- "Search, Explore, Random" site features; "Likes, Followers" feature toggles
- "Works with Emoji + FontAwesome"
- "Views counter"; "Configurable download button"; "Configurable right-click behavior"
- "About, Embed, Exif and info tabs"; "First tab (info, about, embeds)"

---

## 5. NOT SHIPPED — DO NOT COUNT AS PARITY

Items `chevereto.com/features` itself marks as upcoming / coming soon. These are **not** current Chevereto capability and must not be counted toward the Vizra functional-union target.

1. **Chevereto V5 — "coming soon".** Quote: "We are preparing Chevereto V5 with a full user-based API". Linked to `https://blog.chevereto.com/tag/upcoming/`.
2. **Tags support — marked "(upcoming)" on the features page.** Quotes: "Instantly autocomplete and on-the-fly tagging" and "Automatic EXIF camera metadata extraction". Linked to `https://blog.chevereto.com/upcoming/tags-support/`.

> ⚠️ **Conflict to resolve before planning.** Item 2 is flagged "upcoming" on the marketing features page, **but** the V4 docs compare page (§1.6 "Tags features") lists "On-the-fly tag creation", "Tag autocomplete" and "EXIF camera model auto-tagging" as shipped V4 capabilities with no edition restriction, and the v4-admin sidebar has a live `Tags` dashboard page (`/dashboard/tags.html`), and release 4.5.6 fixed "primary key indexes for tag-related tables". The most likely reading is that the marketing page's "upcoming" badge is stale copy left over from when tags shipped. **Marked INFERRED** — do not resolve this from inference alone; confirm against the 4.4/4.5 changelog before treating tags as parity-relevant shipped scope.

No page in the fetched set used the words "roadmap", "beta" or "planned" against a feature.

---

## 6. Releases — current version and recent history

Two official sources agree.

- **Source A:** `https://chevereto.com/releases` (title "Chevereto releases - Chevereto self-hosted") — ok
- **Source B:** `https://github.com/chevereto/chevereto/releases` — ok
- **Source C:** `https://releases.chevereto.com/` (title "Chevereto releases") — ok but **thin**: it is a navigation hub to 4.X / 3.X / 2.X / 1.X branches and rendered no dates or per-release notes.
- **Source D:** `https://v4-docs.chevereto.com/introduction/changelog/4.5.html` (title "🆕 4.5 Elevado") — ok

### 6.1 Current latest released version

> **Chevereto 4.5.7, released 2026-08-20.** Codename for the 4.5 line: **"Elevado"**. Confirmed identically by `chevereto.com/releases`, `github.com/chevereto/chevereto/releases`, and the version banner on both `chevereto.com/features` and `chevereto.com/pricing`.

### 6.2 Last five releases

| Version | Date | Headline items (as listed) |
|---|---|---|
| **4.5.7** | 2026-08-20 | "Improved mobile display for Upload storage settings page"; fixed error messaging for test-email and storage forms; fixed a JavaScript race condition in image loading; fixed tenant stats collection in database isolation mode |
| **4.5.6** | 2026-08-17 | "Added guide to disable automatic system notices display"; corrected primary key indexes for tag-related tables; updated vendor dependencies; fixed translation placeholder issues |
| **4.5.5** | 2026-07-10 | Introduced **tenant database isolation mode**; made user self-signup and guest uploads **disabled by default**; configurable system notices; email delivery warnings for signup and password features; fixed theme override support for dashboard/settings views |
| **4.5.4** | 2026-06-04 | "Redesigned default Contact page (HTML)"; **"[Security] Fix private account setting leaking username on /json endpoint"** |
| **4.5.3** | 2026-05-14 | CSRF protection for account and album endpoints; Variables support in encryption commands; fixed FTP storage folder-structure creation; **removed FTP/SFTP support in SaaS environments** |

### 6.3 Minor-line codenames (from docs sidebar)

`4.5 Elevado`, `4.4 Vivaracho`, `4.3 Entrador`, `4.2 Regio`, `4.1 Pulento`, `4.0 Macanudo`.

### 6.4 4.5 "Elevado" headline features (from `/introduction/changelog/4.5.html`)

1. Expanded email provider support — backing for **19 new email services** incl. Amazon SES, SendGrid, Mailgun.
2. Multi-tenant routing enhancements — new API endpoints for Traefik configuration and tenant-aware auth verification.
3. **Trial mode for SaaS** — quote: providers can "offer Chevereto with limited service caps before users commit to a full plan."
4. **PHP 8.2 minimum requirement.**
5. CLI improvements — added `version-installed`; `password-reset` gained a custom-password option.
6. Contact page redesign, "without traditional form elements".

The 4.5 changelog page did **not** render per-point-release dates (4.5.0 … 4.5.7); those came from §6.2.

---

## 7. API documentation

`https://v4-docs.chevereto.com/developer/api/api-v1.html` **FAILED (404)** — stale URL from search. The live docs sidebar shows the API section is split into **API V4** and **API V1**, four pages total. All four fetched ok.

### 7.1 Authorization — API V4 (`/api/4/authorization.html`, ok)

- Quote: "API V4 requires header authorization by passing the `X-API-Key` header with an API key."
- Header: `X-API-Key`. Token format shown as prefixed, e.g. `chv_key_here`.
- Key types documented:
  1. **Personal / user keys** — generated by individual users at `/settings/api`.
  2. **Admin keys** — set by admins for **guest uploads**, via the Dashboard Guest API panel.
  3. **Tenant keys** — generated by system administrators with the **CLI tool** for the Tenants HTTP API (`/application/reference/cli.html#create-tenants-api-key`).
- **Scopes: not specified.** **Rate limits: not specified.** **Edition availability: not specified.**

### 7.2 Authorization — API V1 (`/api/1/authorization.html`, ok)

- Header name: `X-API-Key`. Query/body parameter alternative: `key`.
- Users create API keys at `/settings/api`.
- Guest API key: administrators configure the public key for guest uploads in the Dashboard's Guest API settings.
- **No edition availability and no rate-limit information on this page.**

### 7.3 File upload — API V1 (`/api/1/file-upload.html`, ok)

- Title: "File upload API". Endpoint shown as `http://mysite.com/api/1/upload`. Method: **POST recommended**, GET also accepted.

| Parameter | Required? | Description / allowed values |
|---|---|---|
| `source` | **Required** | Binary file, base64 data, or image URL |
| `key` | Optional | API key (alternative to header auth) |
| `title` | Optional | File title; auto-detected from metadata if omitted |
| `description` | Optional | File description; auto-detected from metadata if omitted |
| `tags` | Optional | Comma-separated tag list |
| `album_id` | Optional | Album ID (must be owned by the API key's user) |
| `category_id` | Optional | Category ID |
| `width` | Optional | Target resize width (height auto-detected) |
| `expiration` | Optional | Auto-deletion interval, ISO-8601-style, e.g. `PT5M`, `P3D` |
| `nsfw` | Optional | `[0, 1]` |
| `format` | Optional | `[json, redirect, txt]` |
| `use_file_date` | Optional | `[0, 1]` — use EXIF date instead of upload date; **admin only** |

- Response formats: `json` (upload details, default), `txt` (direct URL, plain text), `redirect` (redirect to image viewer).
- Errors: responses carry `status_txt` and `status_code`; HTTP status indicates success (200) or failure.
- **Rate limits: not specified in documentation.**
- **Edition availability: no edition restrictions noted** — only the `use_file_date` admin restriction.

### 7.4 Tenants API — API V4 (`/api/4/tenants.html`, ok)

- Quote: "The Tenants API **requires** a key which can be generated using the Tenants CLI tool".
- Request signing: every request carries an `X-Signature` header = **HMAC SHA256** of the request body, hex, keyed with `CHEVERETO_TENANTS_API_REQUEST_SECRET`.

| Method | Path | Result / params |
|---|---|---|
| POST | `/_/api/4/auth/verify` | 200 — verify API key and signature |
| GET | `/_/api/4/config/traefik` | 200 — dynamic Traefik HTTP provider config; **localhost only, no signature required** |
| GET | `/_/api/4/tenants` | 200 — list tenants |
| POST | `/_/api/4/tenants` | 201 — required `id`, `hostname`, `is_enabled`; optional `plan_id`, `limits`, `env` |
| GET | `/_/api/4/tenants/{id}` | 200 |
| PATCH | `/_/api/4/tenants/{id}` | 204 — optional `is_enabled`, `hostname`, `plan_id`, `limits`, `env` |
| DELETE | `/_/api/4/tenants/{id}` | 204 — optional `drop_tables` |
| POST | `/_/api/4/tenants/{id}/install` | 201 / 404 / 409 |
| PATCH | `/_/api/4/tenants/{id}/user-password-reset` | 200 / 404 — required `username`, optional `password` |
| GET | `/_/api/4/tenants-plans` | 200 |
| POST | `/_/api/4/tenants-plans` | 201 — required `id`; optional `limits`, `env` |
| GET | `/_/api/4/tenants-plans/{id}` | 200 |
| PATCH | `/_/api/4/tenants-plans/{id}` | 204 — optional `limits`, `env` |
| DELETE | `/_/api/4/tenants-plans/{id}` | 204 |

- **Edition availability: not specified on the page.** Note the compare page (§1.14) lists "Multitenancy support" as a System feature with **no edition column**, i.e. not marked Pro-only there.
- A per-tenant `limits` object exists in the API but **its schema/fields were not rendered** — see §11.

### 7.5 API edition availability — what the docs actually establish

- The **compare page** puts `Guest API key` at ✅/✅/✅ (all three editions) and lists `User-based API` and `Guest API` in the un-columned User-features list (§1.9), i.e. **no edition gate on the API is documented**.
- None of the four API pages states an edition restriction or a rate limit.
- **INFERRED:** the upload API therefore appears available in Free as well as Lite/Pro. Not stated explicitly anywhere; do not treat as confirmed.

---

## 8. External services (integrations) — `https://v4-admin.chevereto.com/settings/external-services.html` (ok)

- Page title: "External services | V4 Admin". No edition notes on the page itself; **the compare page marks the whole "External services" row Pro-only** (§1.12).

| Service | Quote / detail |
|---|---|
| Comments API | "Use Disqus (opens new window) comment service" or "Use any HTML comment provider" |
| Disqus | shortname, secret key, public key configuration |
| Analytics | "Determines the analytics HTML code that will track stats for your website" — supports Google Analytics, Heap, Yandex.Metrica, Matomo, Mixpanel |
| Akismet | "Toggles usage of Akismet (opens new window) service" |
| StopForumSpam | "Toggles usage of Stop Forum Spam (opens new window) service" |
| CAPTCHA | "Toggles usage of CAPTCHA (opens new window)" — providers **reCAPTCHA v2, reCAPTCHA v3, hCaptcha**; configurable threshold; forced display on contact page |
| Project Arachnid Shield | "Toggles usage of Project Arachnid Shield (opens new window) service" — requires API username and password |
| **ModerateContent** | "Toggles usage of ModerateContent (opens new window) service" — options for **automatic approval, content blocking, and NSFW flagging** |

> No service named "Arcanine" exists in any fetched Chevereto page. The CSAM/abuse integration is **Project Arachnid Shield**; the general moderation integration is **ModerateContent**. Recorded so the Vizra ledger does not carry a misspelled vendor.

---

## 9. External storage — `https://v4-admin.chevereto.com/features/upload-storage.html` and `/settings/upload-storage.html` (both ok)

`https://v4-admin.chevereto.com/features/external-storage.html` **FAILED (404)** — this is the URL linked from `chevereto.com/features`; the live equivalent is `/features/upload-storage.html`.

### 9.1 Ten storage APIs, with the page's own wording

| Provider | Quote |
|---|---|
| Alibaba Cloud OSS | "uploads images to Alibaba Cloud (Aliyun) Object Storage System" |
| Amazon S3 | "uploads images to an Amazon S3 bucket" |
| Backblaze B2 | "uploads images to Backblaze's cloud storage" |
| FTP | "uploads images to any server implementing the File Transfer Protocol" |
| Google Cloud | "uploads images to a Google Cloud Storage bucket" |
| Local | "uploads images to any filesystem path on the server" |
| Microsoft Azure | "uploads images to Microsoft Azure Storage" |
| OpenStack | "uploads images to an OpenStack container" |
| S3 Compatible | "uploads images to any server implementing the Amazon S3 standard" |
| SFTP | "uploads images to any server implementing the SSH File Transfer Protocol" |

Matches the compare-page Storage APIs table (§1.3) exactly, where Backblaze B2 is labelled "(legacy)" and OpenStack is labelled "OpenStack Swift".

### 9.2 S3-compatible providers named

- **Hosted:** Backblaze B2, Cloudflare R2, DigitalOcean Spaces, DreamHost DreamObjects, Hetzner Object Storage, IBM COS S3, IDrive e2, Linode Object Storage, OVH Cloud Object Storage, PhoenixNAP Object Storage, Scaleway Object Storage, Storj, Tencent Cloud Object Storage, Vultr Object Storage, Wasabi.
- **Self-hosted:** MinIO, Ceph (RGW), SeaweedFS, Zenko, LeoFS, Garage.

### 9.3 Per-storage configuration fields (`/settings/upload-storage.html`)

- `Name` — "String max length 32"
- `Bucket` — "The bucket where the files will be stored"
- `Key` — "Public key"; `Secret` — "Secret key"
- **`Storage capacity`** — format example **"20 GB"** ← the only storage-quota mechanism found in the docs
- `URL` — "The URL that will be mapped to the storage"; warning quote: "For the example above, a file at `https://storage1.demo.chevereto.com/bucket/example.jpg` should be resolving."
- Type handles: `oss` (needs endpoint), `s3` (needs region), `b2` (legacy), `ftp` (server/path/user/password), `gcloud` (JSON private key), `local` (filesystem path), `azure` (account credentials + endpoint), `openstack` (service name, identity URL, credentials), `s3compatible` (region + endpoint), `sftp`.

**Note from release history:** 4.5.3 "removed FTP/SFTP support in SaaS environments" (§6.2) — FTP/SFTP remain for normal self-hosted installs but are disabled in SaaS/tenant mode.

---

## 10. OAuth / social login providers — `https://v4-admin.chevereto.com/features/login-providers.html` (ok)

30 providers listed with their internal handles. Compare page gates the whole "OAuth2 login providers" row at **Lite and Pro only** (§1.12).

Facebook (`facebook`), Twitter (`twitter`), Google (`google`), VK (`vkontakte`), Apple (`apple`), Amazon (`amazon`), BitBucket (`bitbucket`), Discord (`discord`), Dribbble (`dribbble`), Dropbox (`dropbox`), GitHub (`github`), GitLab (`gitlab`), Instagram (`instagram`), LinkedIn (`linkedin`), Mailru (`mailru`), Medium (`medium`), Odnoklassniki (`odnoklassniki`), ORCID (`orcid`), Reddit (`reddit`), Spotify (`spotify`), Steam (`steam`), Strava (`strava`), Telegram (`telegram`), Tumblr (`tumblr`), Twitch (`twitchtv`), WeChat (`wechat`), WordPress (`wordpress`), Yandex (`yandex`), Yahoo (`yahoo`), QQ (`qq`).

> No generic SAML/OIDC **SSO** option appears anywhere in the fetched pages. The only SSO mention found is "Disqus comments (SSO)" on `chevereto.com/features`, which is Disqus-specific, not site login. Recorded as a gap.

---

## 10b. File uploads admin settings — `https://v4-admin.chevereto.com/settings/file-uploads.html` (ok)

- Page: "File uploads" at `/dashboard/settings/file-uploads`.
- **Supported formats string, verbatim:** "AVIF JPG JPEG PNG BMP GIF WEBP MOV MP4 WEBM" — **no HEIC/HEIF, no TIFF, no SVG, no AV1/MKV.**
- `Enable uploads` (registered users) / `Enable uploads (URL)` (external URLs) / guest equivalent toggle / `Guest albums`.
- `Upload user interface`: "On-page container" (JS uploader stays in page) or "/upload route".
- **`Moderate uploads`: three modes — "Disabled", "Guest" (guest uploads only), "All".**
- File size: `Maximum upload file size [MB]` for users, `Maximum upload file size (guests)`; note: "capped by local `php.ini` configuration".
- `Storage mode`: "Datefolders" (YYYY/MM/DD) or "Direct" (no folder structure).
- `File naming method`: Original, Random, Mix original + random, ID-based.
- Image processing: maximum image size in pixels (larger auto-downscale), thumb size, medium image fixed dimension (Width or Height), medium image fixed size.
- Others: NSFW checkbox toggle, embed-codes toggle, upload threads, redirect on single upload, duplicate-upload acceptance toggle, expirable uploads toggle, auto-delete guest uploads, EXIF handling with user-level controls.

## 10c. Users admin settings — `https://v4-admin.chevereto.com/settings/users.html` (ok)

- `User profile view` — "Determine the default view for user profile" (Files or Albums)
- `Enable signups` — "Toggles the ability to signup to your website"
- `Enable user content delete` — "Toggles the ability of own content deletion for users"
- `Minimum age required` — "Determines the minimum age required to use your website" (recommended 13)
- `Notify on user signup` — "Toggles sending of an email notification when a new user sign up"
- `Require email confirmation` — "Toggles the requirement of confirming the email address on signup"
- `Require email for social signup` — "Toggles the requirement of an email address when user signup using a social network"
- `User avatar max. filesize (MB)` — recommended 1 MB
- `User background max. filesize (MB)` — recommended 2 MB
- **This page documents no roles, no per-user storage quota, and no personal-mode settings** — despite the features page claiming "Individual storage and access limits". Conflict recorded in §11.

## 10d. Bulk importer — `https://v4-admin.chevereto.com/dashboard/bulk-importer.html` (ok)

- Quote: it "import[s] a massive amount of content that otherwise will be troublesome to import by using the API or the web user interface."
- Parses filesystem directory contents. Three parse modes: **top-level folder as username** (creates users, nested folders become albums); **top-level folders as albums** (assigned to guest user); **no parse** (images imported public as guest).
- Charset: UTF-8 required for files and JSON metadata. Threading via `THREAD_ID` env var. Lock file at `./importing/.lock`. CRON scheduling supported.
- Metadata via JSON sidecars for images (title, description, NSFW, categories), albums (privacy, access) and users (profile info, avatar/background images, network links).
- No edition restriction stated; compare page lists "Bulk importer (batch upload)" un-columned (§1.2), i.e. all editions.

---

## 11. Requirements / installation / stack

`https://v4-docs.chevereto.com/introduction/get-started/requirements.html` **FAILED (404)**. Live equivalent is the docs "Stack" section.

### 11.1 PHP — `/application/stack/php.html` (ok)

| Chevereto version | Supported PHP |
|---|---|
| 4.5 | **8.2** |
| 4.4 | 8.1, 8.2 |
| 4.3 | 8.1, 8.2 |
| 4.2 | 8.1, 8.2 |
| 4.1 | 8.0, 8.1 |
| 4.0 | 8.0, 8.1 |

- Required extensions: `curl`, `exif`, `fileinfo`, `gd`, `hash`, `imagick`, `json`, `pdo`, `pdo-mysql` (`nd_pdo_mysql`), `session`, `xml`.
- Recommended php.ini: `upload_max_filesize = 64M`, `post_max_size = 64M`, `max_execution_time = 30`, `memory_limit = 512M`.
- Quote: "PHP versions explicitly listed in the table above are officially supported. Using any other PHP version may result in unexpected behavior or compatibility issues."
- Requires "unrestricted access to all PHP functions". ImageMagick preferred over GD; must support "PNG GIF JPG BMP WEBP".

### 11.2 Database — `/application/stack/mysql-server.html` (ok)

| Chevereto version | MySQL | MariaDB |
|---|---|---|
| 4.5 | 8.0.1 | 10.2.2 |
| 4.4 | 8.0.1 | 10.2.2 |
| 4.3 | 8.0.1 | 10.2.2 |
| 4.2 | 8.0.1 | 10.2.2 |
| 4.1 | 5.7; 8 | 10 |
| 4.0 | 5.7; 8 | 10 |

- Quote: "Chevereto support both MySQL/MariaDB database servers but we refer indistinctly as **MySQL**."
- "InnoDB table storage engine." MyISAM conversion required for older installs.
- "Database user must have `ALL PRIVILEGES` over the target database."
- **PostgreSQL is not supported** — it is not mentioned. (Relevant: Vizra is PostgreSQL-first, so no schema or query shape can be borrowed here anyway; stack facts only.)
- Charset/collation requirements not stated.

### 11.3 Other stack components (from docs sidebar, pages not individually fetched)

`/application/stack/operating-system.html`, `/web-server.html`, `/redis.html`, `/utilities.html`, `/cron.html`. Search result indicated the web-server page names **Apache HTTP Server and Nginx** as officially supported — **INFERRED from a search snippet, not from a direct fetch of that page; verify before citing.**

### 11.4 Installation — `/application/installing/installation.html` (ok)

- Five methods: **Docker** — "the recommended way to install Chevereto"; VPS; Synology NAS; release package (CLI or GUI); control-panel installers (EasyPanel, Installatron, SwiftWave).
- Setup via HTTP browser ("setup instructions") or CLI ("install command").
- CLI bootstrap shown: `bash <(curl -s https://raw.githubusercontent.com/chevereto/vps/4.3/common/get.sh)`
- References an "installation service" via Chevereto support; mentions both "Paid edition" and "Free edition" downloads.
- **Docker image names and tags were NOT rendered on this page.** Recorded as a gap.

### 11.5 Documentation repo — `https://github.com/chevereto/v4-docs` (ok)

- Top-level dirs: `.github/workflows`, `.vuepress`, `api`, `application`, `developer`, `guides`, `introduction`, `src`. Files incl. `README.md`, `LICENSE` (**Apache-2.0**), `naming.php`, `sorting.php`.
- README quote: Chevereto is "a robust, self-hosted media-sharing platform that prioritizes flexibility and control"; users can "build and manage a media-sharing website on your own server, granting you complete autonomy."
- Repo stats at observation: 3 stars, 42 forks, 425 commits on `main`.
- **Useful for future work:** the docs are VuePress markdown in this repo, so the exact byte-level table source for `introduction/editions/compare.md` can be read directly from the repo if a byte-exact comparison table is ever needed. Not done in this pass.

---

## 12. Cross-source conflicts to resolve before they enter the Vizra ledger

1. **Turnstile.** Claimed on `chevereto.com/features` ("Turnstile, reCAPTCHA & hCaptcha bot defense") but absent from the v4-admin External services CAPTCHA provider list and from the compare page's "CAPTCHA (reCAPTCHA, hCaptcha)" row. Unresolved.
2. **Tags "upcoming".** Features page badges tags as upcoming; V4 docs compare page, the admin Tags dashboard page, and the 4.5.6 changelog all treat tags as shipped. Likely stale marketing copy — **INFERRED**, unresolved.
3. **Per-user storage quota.** Features page claims "Individual storage and access limits"; the admin Users settings page documents no such quota, and the only capacity field found is per-storage `Storage capacity` ("20 GB") in Upload storage. Unresolved.
4. **Multitenancy edition gating.** Compare page lists "Multitenancy support" un-columned (implying all editions); the Tenants API page states no edition restriction; but tenancy is the SaaS/commercial surface and 4.5 added "Trial mode for SaaS". No official statement found either way.
5. **ModerateContent vs the compare page.** ModerateContent is documented in v4-admin External services, but does **not** appear as its own row in the compare page's Pro-only integration list (which names Akismet, StopForumSpam, CAPTCHA, Project Arachnid). It is presumably covered by the blanket Pro-only "External services" row — **INFERRED.**

---

## 13. Coverage gaps — what the official docs did NOT answer

1. **No user-count limit, storage cap, upload-count cap or site/domain cap** is published for any edition. Pricing only says "unlimited websites deployment" for paid editions. If Vizra's parity spec needs edition limits, they do not exist in public docs.
2. **No API rate limits** are published on any of the four API pages. None.
3. **No API scopes/permission model** documented for V4 keys beyond the three key *types* (user / admin-guest / tenant).
4. **No documented V4 REST surface beyond upload + tenants.** The docs sidebar exposes only `api/4/authorization`, `api/4/tenants`, `api/1/authorization`, `api/1/file-upload`. There is no published endpoint reference for albums, users, likes, follows, search, categories or moderation. The "full user-based API" is explicitly a **V5** item (§5). This is a significant gap for anyone specifying an API-parity target.
5. **Edition availability of the API is never stated.** §7.5 is inference only.
6. **Docker image names and tags** are not on the installation page. Not captured.
7. **Web server supported versions** not fetched directly (only a search snippet) — §11.3.
8. **Redis role/requirement** (optional vs required, versions) not fetched.
9. **Cron job list** (what must be scheduled, at what interval) not fetched.
10. **CLI command reference** not fetched (`/application/reference/cli.html`) — relevant for "admin tooling (CLI, cron)".
11. **Per-tenant `limits` object schema** — the Tenants API accepts `limits` on tenants and plans, but the field names and units were not rendered.
12. **HEIC/HEIF, TIFF, SVG, AV1/MKV are absent** from every format list found. Nothing says they are unsupported; they simply never appear. Do not record them as either supported or explicitly excluded.
13. **Generic SSO (SAML / OIDC)** — no evidence of any. Only the 30 named OAuth providers plus Disqus SSO for comments.
14. **Theme/palette count** — compare page says "Theme palettes (10)"; features page names System/Light/Dark/Flickr/Imgur/DeviantArt/Lush/Graffiti/Abstract/Cheers/CMYK (11 names). Not reconciled.
15. **Image expiration semantics** — `expiration` accepts `PT5M`/`P3D` style values in the upload API, but the allowed range, maximum, and deletion guarantees are not documented.
16. **Video handling depth** — MP4/MOV/WEBM are accepted and a "video frame image" is generated, but there is no documentation of transcoding, duration/size limits, streaming, or playback behaviour.
17. **The "editions" landing page, the consolidated changelog page, and the old developer/api path all 404** — anyone else researching this will hit the same three dead URLs; current equivalents are recorded in §0.
18. **Banner placements** — "16 predefined banner placements" is claimed, but the placement names/positions are not enumerated on any fetched page (`/settings/banners.html` not fetched).
19. **`releases.chevereto.com` is effectively contentless** as a machine-readable release feed; use `chevereto.com/releases` or the GitHub releases page instead.
20. **Nothing in this file came from the paid demo, the Chevereto Cloud product, or any private/paid source.** No proprietary source was inspected. All facts are from public official documentation and marketing pages only.
