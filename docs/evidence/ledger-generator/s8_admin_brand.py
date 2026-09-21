from core import *

# ---------------------------------------------------------------- F5 admin, branding, services, tenancy
req("VZ-ADMIN-001","Admin console: dashboard, files, albums, tags, users with sorts, bulk actions, keyboard shortcuts and audit log",
    "Owner/manager: full-screen listings of all files/albums/tags/users with sorts (recent/oldest/most viewed/most favorited/A-Z), select-all/clear/drag-select, bulk delete/assign category/flag/approve; every consequential action audited and searchable.",
    "admin", CHEV, [{"source":"CHEV-DASHBOARD-FILES","note":"controls and keys"},{"source":"CHEV-DASHBOARD-ALBUMS"},{"source":"CHEV-DASHBOARD-USERS"}], edition="all",
    deps=["VZ-AUTH-004"], success=["Bulk action on 100 items with audit rows"], negative=["Manager denied settings routes"], api=["/api/v1/admin/*"], ui=["/admin/*"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-ADMIN-002","Runtime settings registry with validation, effective-value display, no-restart application, and audit",
    "Owner: every operator-facing setting (website, content, uploads, users, listings, theme, routing, semantics, email, services, limits, federation, IPFS policy) lives in a DB-backed registry editable from the UI, validated, applied without restart, shown with its effective value, audited; env vars only for boot-time infrastructure.",
    "admin", OPS, [{"source":"CHEV-SETTINGS-ALL","note":"29 settings pages"},{"source":"VIDRA-INSTANCE-ADMIN","note":"instance settings registry"}],
    deps=["VZ-FOUND-003"], success=["Settings count test; change reflected immediately"], negative=["Invalid value rejected with message"], recovery=["Settings included in backup/restore"], api=["GET/PATCH /api/v1/admin/settings"], ui=["/admin/settings/*"], evidence=EV_API+EV_UI)
req("VZ-ADMIN-003","Website settings: name, doctitle, description, timezone, privacy mode (public/private), content privacy defaults, single-profile mode",
    "Owner: sets site identity; private site requires login for all content; content privacy defaults (free / force private / force link-only); single-profile (personal) mode targets one user with custom root routing.",
    "admin", CHEV, [{"source":"CHEV-WEBSITE","note":"Website mode Multi-user / Single profile; privacy modes"}], edition="all",
    deps=["VZ-ADMIN-002","VZ-PRIVACY-001"], success=["Private site: anonymous → login on every route incl. object URLs, feeds, oEmbed, sitemap"], privacy=["Private site emits no public sitemap/OG"], ui=["/admin/settings/website"], evidence=EV_UI+EV_NEG, decided=["Q-023"])
req("VZ-BRAND-001","Logo (vector/image/text), favicon, palettes (light/dark/system + themed), default font, custom CSS with a safe boundary",
    "Owner: uploads vector or raster logo and favicon; selects default palette and font; members choose palette; custom CSS allowed within a sanitized, CSP-compatible boundary; no arbitrary JS injection.",
    "admin", CHEV, [{"source":"CHEV-LOGO"},{"source":"CHEV-THEME","note":"palette, font, custom CSS/JS"},{"source":"AGENTS","note":"no unrestricted custom-script surfaces"}], edition="all",
    deps=["VZ-ADMIN-002"], success=["Logo/palette/font applied; screenshots light/dark"], negative=["CSS containing url()/@import to remote hosts blocked or documented; JS injection unavailable"], ui=["/admin/settings/theme","/admin/settings/logo"], evidence=EV_UI+EV_NEG, decided=["Q-014"],
    mechanism="Chevereto allows raw Custom JS and PHP pages. Vizra provides theme tokens, sanitized CSS and typed extension points instead; owner decision Q-014.")
req("VZ-BRAND-002","Homepage styles: landing, split landing + images, route explore, route upload; covers, title, paragraph, call-to-action",
    "Owner: chooses homepage style; multiple cover images; title/paragraph; CTA (trigger uploader or URL) with color/outline; user IDs for split listing.",
    "admin", CHEV, [{"source":"CHEV-HOMEPAGE","note":"styles and CTA"},{"source":"CHEV-COMPARE","note":"Homepage cover/title/CTA Lite/Pro"}], edition="Lite",
    deps=["VZ-ADMIN-002"], success=["Each style renders"], ui=["/","/admin/settings/homepage"], evidence=EV_UI)
req("VZ-PAGE-001","Custom pages (terms, extra pages, links) with rich text/sanitized HTML, visibility, sort, link attributes, meta",
    "Owner: creates internal pages (rich text or sanitized HTML, no server code) and link pages; visibility, status, sort order, meta description; ToS page type shown at consent.",
    "admin", CHEV, [{"source":"CHEV-PAGES","note":"fields; .php internal pages (not copied)"}], edition="Lite",
    deps=["VZ-ADMIN-002"], success=["Page renders; nav link"], negative=["Script tags stripped"], api=["/api/v1/admin/pages"], ui=["/admin/settings/pages","/page/{key}"], evidence=EV_API+EV_UI+EV_NEG, decided=["Q-014"])
req("VZ-BRAND-003","Semantics: rename core nouns (album, image, video, file, tag, user, category, explore, discovery) and navigation labels",
    "Owner: overrides 16 nouns and navigation labels; applied across UI and emails.",
    "admin", CHEV, [{"source":"CHEV-SEMANTICS","note":"16 nouns"}], edition="all",
    deps=["VZ-ADMIN-002","VZ-I18N-001"], success=["Override visible in UI and emails"], ui=["/admin/settings/semantics"], evidence=EV_UI)
req("VZ-BRAND-004","Album call-to-action buttons",
    "Owner/photographer: configurable CTA buttons on albums (label, URL, style).", "admin", CHEV, [{"source":"CHEV-COMPARE","note":"Call-to-action album buttons"}], edition="all",
    deps=["VZ-ALBUM-001"], success=["CTA rendered and clickable; URL validated"], ui=["album edit"], evidence=EV_UI)
req("VZ-BRAND-005","'Powered by Vizra' footer toggle",
    "Owner: toggles attribution footer.", "admin", CHEV, [{"source":"CHEV-WEBSITE","note":"Powered by toggle"},{"source":"CHEV-COMPARE","note":"Hide Powered by (Pro)"}], edition="Pro",
    deps=["VZ-ADMIN-002"], success=["Toggle works"], ui=["/admin/settings/website"], evidence=EV_UI)
req("VZ-I18N-001","Internationalization: default language, auto-detect, language chooser, enabled-language list, translation overrides, RTL",
    "Owner: sets default language; auto language from browser; chooser for guests and members; enabled subset; translation overrides; RTL layouts.",
    "admin", CHEV, [{"source":"CHEV-LANGUAGES","note":"34 locales; auto; chooser"},{"source":"CHEV-COMPARE","note":"Auto language, Language chooser, Enabled languages (Pro)"}], edition="Pro",
    deps=["VZ-ADMIN-002"], success=["Two locales + RTL screenshot"], ui=["language chooser","/admin/settings/languages"], evidence=EV_UI, decided=["Q-043"])
req("VZ-LISTING-001","Listing settings: items per page, classic/endless pagination, fixed/fluid grid, columns per device, listing viewer toggle",
    "Owner: configures listings; members see consistent grids on phone/phablet/tablet/laptop/desktop.",
    "admin", CHEV, [{"source":"CHEV-LISTINGS"}], edition="all",
    deps=["VZ-ADMIN-002","VZ-VIEWER-001"], success=["Settings applied; endless scroll accessible (keyboard + announce)"], ui=["/admin/settings/listings"], evidence=EV_UI)
req("VZ-CONSENT-001","Consent/age-gate screen with cover image and cookie-law notice",
    "Owner: enables consent screen (terms) with cover; cookie compliance banner toggle.",
    "admin", CHEV, [{"source":"CHEV-CONSENT-SCREEN"},{"source":"CHEV-COOKIE"}], edition="Lite",
    deps=["VZ-ADMIN-002"], success=["Consent required before browsing; cookie banner dismissible and accessible"], ui=["consent screen","cookie banner"], evidence=EV_UI)
req("VZ-BANNER-001","Banner/ad slots: 16 predefined placements × SFW/NSFW with sanitized HTML and 'show banners on NSFW' toggle",
    "Owner: fills placements (homepage, listings, content, image page, album page, profile, explore) with sanitized markup; NSFW variant; no arbitrary script unless owner accepts a documented CSP-scoped provider boundary.",
    "admin", CHEV, [{"source":"CHEV-BANNERS","note":"16 placements"},{"source":"AGENTS","note":"unrestricted script surfaces prohibited"}], edition="Pro",
    deps=["VZ-ADMIN-002"], success=["Placement renders where configured"], negative=["Script stripped/blocked by policy"], ui=["/admin/settings/banners"], evidence=EV_UI+EV_NEG, decided=["Q-013"])
req("VZ-EMAIL-001","Email delivery: SMTP with TLS/SSL, from/incoming addresses, provider presets, test-email tool, delivery warnings",
    "Owner: configures SMTP (or provider presets); test email; warnings when signup/password features need mail and it is off.",
    "admin", CHEV, [{"source":"CHEV-EMAIL"},{"source":"CHEV-CHANGELOG-4.5","note":"19 email providers"}], edition="all",
    deps=["VZ-ADMIN-002","VZ-JOBS-001"], success=["Test email received (mail capture in QA)"], negative=["Bad credentials surface in admin, not to users"], cli=["vizra setup SMTP answers"], ui=["/admin/settings/email"], evidence=EV_UI+["mail capture transcript"])
req("VZ-SERVICES-001","CAPTCHA providers (reCAPTCHA v2/v3, hCaptcha, Turnstile) with threshold and forced contact-page mode",
    "Owner: enables a CAPTCHA provider with site/secret keys; threshold after N failed attempts; forced on contact form; server-side verification.",
    "admin", CHEV, [{"source":"CHEV-EXTERNAL-SERVICES","note":"reCAPTCHA v2/v3, hCaptcha, threshold"},{"source":"CHEV-FEATURES","note":"Turnstile claimed (conflict)"}], edition="Pro",
    deps=["VZ-AUTH-001"], success=["Each provider live-tested with test keys"], negative=["Missing token rejected server-side"], ui=["/admin/settings/services"], evidence=EV_API+EV_NEG, decided=["Q-005"])
req("VZ-SERVICES-002","Akismet and StopForumSpam integration on signup/comments/contact",
    "Owner: enables Akismet (key) and StopForumSpam checks; flagged content held for moderation.",
    "admin", CHEV, [{"source":"CHEV-EXTERNAL-SERVICES"},{"source":"CHEV-COMPARE","note":"Akismet, StopForumSpam (Pro)"}], edition="Pro",
    deps=["VZ-COMMENT-001","VZ-MOD-001"], success=["Fixture spam flagged (provider test mode)"], privacy=["Only required fields sent; documented"], ui=["/admin/settings/services"], evidence=["provider transcript"], profiles=("full",))
req("VZ-SERVICES-003","External image-moderation API (ModerateContent-class) with auto-approve, block and NSFW-flag policies",
    "Owner: connects a moderation API; policies: auto-approve approved, block adult / teen+adult, flag NSFW; results audited; provider adapter interface allows alternatives.",
    "admin", CHEV, [{"source":"CHEV-EXTERNAL-SERVICES","note":"ModerateContent options"}], edition="Pro",
    deps=["VZ-UPLOAD-012"], success=["Fixture classified in sandbox; policy applied"], negative=["Provider outage → hold for manual review, not auto-publish"], ui=["/admin/settings/services"], evidence=["provider transcript"], profiles=("full",), unresolved=["Q-022"])
req("VZ-SERVICES-004","CSAM detection integration (Project Arachnid Shield-class) with credentialed adapter",
    "Owner: enables a CSAM-detection service with credentials; matches block publication and alert admins; requires provider access for live evidence.",
    "admin", CHEV, [{"source":"CHEV-EXTERNAL-SERVICES","note":"Arachnid API username/password"}], edition="Pro",
    deps=["VZ-UPLOAD-012"], success=["Adapter contract test with provider sandbox or documented BLOCKED"], privacy=["Only hashes/required data sent"], ui=["/admin/settings/services"], evidence=["provider transcript or BLOCKED record"], profiles=("full",), unresolved=["Q-021"])
req("VZ-SERVICES-005","Analytics snippet slot (privacy-respecting) and external comment provider embed (optional)",
    "Owner: adds a site analytics snippet within a CSP-scoped allowlist of providers; optional external comment provider embed as an alternative to native comments.",
    "admin", CHEV, [{"source":"CHEV-EXTERNAL-SERVICES","note":"Analytics code; Comments API"},{"source":"AGENTS","note":"restrict privileged customization"}], edition="Pro",
    deps=["VZ-ADMIN-002"], success=["Allowed provider renders; disallowed blocked"], ui=["/admin/settings/services"], evidence=EV_UI+EV_NEG, profiles=("full",), decided=["Q-011","Q-014"])
req("VZ-SECURITY-001","IP bans (v4/v6, ranges, expiration, description) and stop words",
    "Owner: bans IPs/ranges with expiry and reason; stop words (regex) block content; both audited.",
    "admin", CHEV, [{"source":"CHEV-IP-BANS"},{"source":"CHEV-CONTENT","note":"stop words regex"}], edition="Pro",
    deps=["VZ-ADMIN-002"], success=["Banned IP receives configured response; stop word rejects"], negative=["Regex DoS bounded"], api=["/api/v1/admin/ip-bans"], ui=["/admin/settings/ip-bans","/admin/settings/content"], evidence=EV_API+EV_NEG)
req("VZ-SECURITY-002","Flood protection: per-period upload/creation/login limits with email notification",
    "Owner: minute/hour/day/week/month caps on uploads, album creation, account creation and login with notification; distinct from API rate limits.",
    "admin", CHEV, [{"source":"CHEV-FLOOD","note":"recommended values 50/500/1000/5000/10000"}], edition="Pro",
    deps=["VZ-AUTH-009"], success=["Caps enforced; report email sent"], ui=["/admin/settings/flood-protection"], evidence=EV_API+EV_NEG)
req("VZ-SECURITY-003","Secrets encryption at rest with KEK, rotation, non-enumerable IDs, CSRF, password/API-key hashing",
    "Operator: provider credentials and 2FA secrets sealed by a KEK with documented rotation; public IDs non-sequential; CSRF on every mutating cookie route; hashing for passwords and API keys.",
    "admin", CHEV, [{"source":"CHEV-COMPARE","note":"Encrypt secrets; Crypt-salted IDs; CSRF"},{"source":"VIDRA-SETUP","note":"KEK rotation --yes-i-know"}], edition="all",
    deps=["VZ-FOUND-006"], success=["Rotation rehearsal; CSRF negative tests"], evidence=EV_NEG+["rotation transcript"])
req("VZ-TOOLS-001","Admin tools: decode/encode ID, send test email, export user profile JSON, regenerate storage stats, migrate records",
    "Owner: utility tools from the admin UI and CLI.", "admin", CHEV, [{"source":"CHEV-TOOLS"}], edition="all",
    deps=["VZ-ADMIN-001"], success=["Each tool tested"], cli=["vizra tools *"], ui=["/admin/tools"], evidence=EV_UI)
req("VZ-UPDATE-001","One-click update check and guided upgrade from the admin UI (delegating to the CLI)",
    "Owner: sees available releases and changelog; upgrade is executed by the operator CLI (never by the web process) with the documented gates.",
    "admin", CHEV, [{"source":"CHEV-COMPARE","note":"One-click upgrade (web, CLI); Automatic updates check"},{"source":"ARCH","note":"web/API must not orchestrate Docker"}], edition="all",
    deps=["VZ-OPS-001","VZ-OPS-003"], success=["Update available banner; CLI performs upgrade"], negative=["Web process cannot trigger docker actions"], ui=["/admin/system"], cli=["vizra update"], evidence=EV_UI+["transcript"],
    mechanism="Chevereto upgrades from the web UI. Vizra shows availability in the UI and performs upgrades via the CLI for privilege separation.")
req("VZ-TENANT-001","Multi-tenancy: tenants with hostname, plans/limits, lifecycle API with HMAC-signed requests, install and password-reset endpoints, per-tenant isolation",
    "Operator: creates tenants (id, hostname, enabled, plan, limits, env) via signed API/CLI; tenant install; per-tenant data isolation (schema or database mode); jobs worker per tenant; stats per tenant; FTP/SFTP disabled in tenant mode.",
    "admin", CHEV, [{"source":"CHEV-TENANTS-API","note":"13 endpoints; X-Signature HMAC"},{"source":"CHEV-COMPARE","note":"Multitenancy support (un-columned)"},{"source":"CHEV-RELEASES","note":"4.5.5 tenant database isolation mode"}], edition="all",
    deps=["VZ-FOUND-003","VZ-STORAGE-004"], success=["Two tenants on separate hostnames; cross-tenant read denied on every surface"], negative=["Unsigned tenant request rejected"], privacy=["Tenant isolation tested for search, counts, caches, federation actors"], recovery=["Backup/restore per tenant"], api=["/_/api/v4-compatible tenants + plans"], cli=["vizra tenants"], ui=["/admin/tenants"], evidence=EV_API+EV_NEG, profiles=("full",), decided=["Q-008"],
    notes="Q-008 decided 2026-09-15: database-per-tenant (tenant registry → DSN); no tenant column or per-tenant schema in core; M5 must design N search DSNs or one search instance per tenant.")
req("VZ-TENANT-002","Reverse-proxy dynamic config export for tenant routing",
    "Operator: endpoint/CLI emits routing configuration for the edge proxy (Caddy) from the tenant list; localhost-only.",
    "admin", CHEV, [{"source":"CHEV-TENANTS-API","note":"GET /config/traefik localhost only"}], edition="all",
    deps=["VZ-TENANT-001"], success=["Config renders; proxy validates"], api=["GET /_/config/caddy (loopback)"], evidence=EV_OPS, profiles=("full",), decided=["Q-008"])
