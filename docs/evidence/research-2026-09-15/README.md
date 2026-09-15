# Research evidence — 2026-09-15

Four official-source research passes produced these files. Each records exact URLs, page titles, on-page versions/dates, observation date, HTTP result (including FAILED fetches), verbatim short quotes, and explicit INFERRED/UNVERIFIED markers. `docs/SOURCE_REGISTER.md` summarizes them; when the register and an evidence file disagree, re-verify against the live URL.

| File | Scope | Fetch outcome |
|---|---|---|
| research-chevereto-editions.md | Chevereto compare page, edition pages, pricing, features page, releases/changelog, API v1/v4/tenants, stack/installation | 32 URLs, 27 ok, 5 × 404 (equivalents recorded) |
| research-chevereto-manuals.md | Chevereto V4 admin manual (39/39) and user manual (34/35) | 1 broken internal link 404 |
| research-flickr.md | Flickr Help Center (157-article index, 76 fetched), Community Guidelines PDF, API reference | direct fetches 403 (Cloudflare); read via the site's public Help Center API in a browser |
| research-protocols-providers.md | ActivityPub/Mastodon/Pixelfed, AT Protocol/Bluesky, IPFS, Backblaze/AWS, ClickHouse, Next.js/Echo/sqlc/PostgreSQL/Redis/Go/libvips, OWASP, Lucide, WCAG, Compose, oEmbed/OG | 45 URLs, 6 FAILED, 2 partial |

Method caveat: pages fetched through the WebFetch tool pass through an extraction model; quotes are faithful as returned but not byte-exact. The Chevereto manuals were crawled with curl (exact HTML). No paid demo, proprietary source or third-party mirror was inspected.
