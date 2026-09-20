from core import *

# ---------------------------------------------------------------- F7 explore, search, analytics
req("VZ-EXPLORE-001","Explore: recent, trending, popular, following, animated, videos, albums, users, tags listings with guest/member toggles",
    "Visitor: explores public content by recent/trending/popular; tabs for images/videos/animated/tags/albums/users; owner toggles search/explore/random for guests and members; album listing requires N items.",
    "search", CHEV, [{"source":"CHEV-USER-DISCOVERY","note":"Recent, Trending (views), Popular (likes), Following; tabs"},{"source":"CHEV-WEBSITE","note":"Explore/Search/Random toggles for users and guests"},{"source":"CHEV-LISTINGS","note":"album listing requirement"}], edition="all",
    deps=["VZ-VIEWER-001","VZ-PRIVACY-001"], success=["Listings contain only public safe-filtered items; toggles enforced"], negative=["Guest with explore disabled → 403 and nav hidden"], privacy=["Counts and pagination never include private items"], api=["GET /api/v1/explore/*"], ui=["/explore/*"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-EXPLORE-002","Random mode",
    "Visitor: ?random shows a random public safe image when enabled.", "search", CHEV, [{"source":"CHEV-USER-RANDOM"}], edition="all",
    deps=["VZ-EXPLORE-001"], success=["Random respects NSFW random setting"], api=["GET /api/v1/explore/random"], ui=["/explore/random"], evidence=EV_API+EV_UI)
req("VZ-EXPLORE-003","Interestingness-style featured Explore with engagement-quality ranking and per-member frequency caps",
    "Visitor: a daily featured set ranked by engagement quality (comments, favorites, ratings, views with decay) with per-member caps; operator can curate/takeover themes; no billing bias.",
    "search", FLICKR, [{"source":"FLICKR-EXPLORE","note":"interestingness + activity; frequency caps"}],
    deps=["VZ-EXPLORE-001","VZ-ANALYTICS-002"], success=["Ranking documented; evaluation metric recorded"], negative=["Private/hidden/unsafe items never featured"], api=["GET /api/v1/explore/featured"], ui=["/explore"], evidence=EV_API+["evaluation report"], profiles=("full",))
req("VZ-SEARCH-001","Permission-aware search of photos, albums, users and tags with full-text and phrase matching, exclusions, operators",
    "Visitor/member: basic keyword search; advanced dialog with all-words/exact-phrase/none-of-these; category and (admin-only) IP operators; PostgreSQL FTS + trigram; authorization inside the query for results, counts, facets and suggestions; bounded pagination; p95 budget on a declared fixture.",
    "search", EXPLICIT, [{"source":"CHEV-USER-SEARCH","note":"basic + advanced fields"},{"source":"CHEV-FEATURES","note":"operators incl. category, storage, IP"},{"source":"PG-FTS"},{"source":"PG-TRGM"}],
    deps=["VZ-PRIVACY-001","VZ-TAG-001"], success=["Fixture catalog: expected results and counts per viewer role"], negative=["Admin-only operator rejected for members"], privacy=["Visibility change reflected immediately in results and caches (test)"], api=["GET /api/v1/search"], ui=["search bar","advanced search dialog"], evidence=EV_API+EV_UI+EV_NEG+["query plans + p95 report"])
req("VZ-SEARCH-002","Search filters: date taken/uploaded, license, safety level, content type, media type, orientation, min size, color, camera/lens/EXIF, tags-only, in-gallery, group, geo",
    "Visitor: filters mirroring the Flickr search contract, all permission-aware; camera finder pages by brand/model from EXIF.",
    "search", FLICKR, [{"source":"FLICKR-SEARCH","note":"advanced filters"},{"source":"FLICKR-API","note":"photos.search arguments"}],
    deps=["VZ-SEARCH-001","VZ-LICENSE-001","VZ-MEDIA-004"], success=["Each filter tested with fixture expectations"], privacy=["GPS facets off unless geo-privacy allows"], api=["GET /api/v1/search?filters"], ui=["advanced search","/cameras"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-SEARCH-003","Suggestions/autocomplete for tags, users, albums with privacy-safe cache",
    "Visitor: typeahead suggestions limited to visible entities; cached per audience class; invalidated on visibility change.",
    "search", SAFE, [{"source":"CHEV-COMPARE","note":"Tag autocomplete"},{"source":"PROMPT-07","note":"suggestions authorized"}],
    deps=["VZ-SEARCH-001"], success=["Suggestions exclude private tags/users"], api=["GET /api/v1/suggest"], ui=["search bar"], evidence=EV_API+EV_NEG)
req("VZ-SEARCH-004","vizra-search internal service contract and SQL fallback",
    "Operator: search runs as an internal HMAC-authenticated service returning ranked IDs; core hydrates and authorizes; when unavailable core falls back to its own SQL; admin status shows index freshness and reconcile.",
    "search", META, [{"source":"VIDRA-REPO-MAP","note":"ranked IDs only; never hard dependency"},{"source":"OWNER-2026-09-15","note":"vizra-search repo"}],
    deps=["VZ-SEARCH-001","VZ-JOBS-001"], success=["Kill search → results still served; reconcile catches up"], negative=["Port published off-host fails CI"], privacy=["Search never returns titles or viewer state"], api=["/internal/v1/search|suggestions|events"], ui=["/admin/search"], evidence=EV_OPS+["fault-injection transcript"], decided=["Q-001"],
    notes="Q-001 decided 2026-09-15: repo created in M0 as a real minimal service returning not_indexed; SEARCH_MODE=off default before M3, managed default from M3; misconfiguration is a doctor FAIL with degraded readiness, served from SQL.")
req("VZ-STATS-001","Basic operator statistics dashboard from authoritative PostgreSQL counts",
    "Owner: dashboard charts (files, disk, users, albums, tags) over 1W/1M/3M/6M/1Y with totals; per-item views count (definition documented); works with analytics OFF.",
    "search", CHEV, [{"source":"CHEV-DASHBOARD-HOME","note":"chart metrics and ranges"},{"source":"PROMPT-07","note":"basic stats useful when analytics off"}], edition="all",
    deps=["VZ-ADMIN-001"], success=["Numbers match SQL ground truth on fixture"], privacy=["View counts on private items visible to owner/admin only"], api=["GET /api/v1/admin/stats"], ui=["/admin"], evidence=EV_API+EV_UI)
req("VZ-STATS-002","Member statistics: per-item and per-account views, favorites, comments over time, sources, CSV export (ungated)",
    "Photographer: stats page with daily views/favorites/comments, top items, referrer classes; downloadable CSV; requires analytics events (ClickHouse) or bounded PostgreSQL rollups when analytics is off.",
    "search", FLICKR, [{"source":"FLICKR-STATS","note":"Pro-only in Flickr; ungated in Vizra"}],
    deps=["VZ-ANALYTICS-001"], success=["Stats match event fixture; lag displayed"], privacy=["Referrers minimized; no full IPs"], api=["GET /api/v1/me/stats"], ui=["/stats"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-ANALYTICS-001","Optional ClickHouse analytics pipeline: versioned events, outbox delivery, dedup keys, retention, privacy minimization, lag/replay/dead-letter",
    "Operator: when enabled, events (view, favorite, comment, search term class) flow via durable outbox with idempotency keys to ClickHouse; documented metric semantics; ReplacingMergeTree not treated as dedup guarantee (FINAL or reconciliation); ClickHouse outage never affects uploads/comments; replay reconciles without double counting.",
    "search", EXPLICIT, [{"source":"CHARTER","note":"optional ClickHouse"},{"source":"CH-REPLACING","note":"does not guarantee absence of duplicates"},{"source":"PROMPT-07"}],
    deps=["VZ-TOPOLOGY-004","VZ-JOBS-001"], success=["Kill ClickHouse during uploads/comments → core writes succeed; resume → counts reconcile"], negative=["Duplicate event replay counted once"], privacy=["No raw private search terms, signed URLs, full IPs, private metadata"], recovery=["Backup or replay source declared and rehearsed"], api=["admin status"], ui=["/admin/analytics"], evidence=["fault-injection + reconciliation report"], profiles=("full",))
req("VZ-ANALYTICS-002","Trending with time decay and popularity signals",
    "Visitor: trending uses decayed engagement rather than raw view count; documented; works from PostgreSQL rollups when analytics is off.",
    "search", SAFE, [{"source":"CHEV-USER-DISCOVERY","note":"Trending = raw views (improved)"},{"source":"VIDRA-SEARCH","note":"decayed-counter trending"}],
    deps=["VZ-EXPLORE-001"], success=["Decay documented and tested"], evidence=EV_API, profiles=("full",))
req("VZ-SEO-001","Sitemaps, robots, hreflang, canonical URLs, OG/Twitter cards for public pages only",
    "Operator: sitemap of public items/albums/users/tags; hreflang; canonical; private/unlisted excluded; hide-from-search honored.",
    "search", CHEV, [{"source":"CHEV-COMPARE","note":"Hreflang HTML tags; SEO URLs"}], edition="all",
    deps=["VZ-PRIVACY-001"], success=["Sitemap contains only public items"], privacy=["Unlisted never in sitemap/feeds"], api=["GET /sitemap.xml"], evidence=EV_API+EV_NEG)
