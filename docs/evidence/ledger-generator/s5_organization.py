from core import *

# ---------------------------------------------------------------- F3 library / viewer / organization
req("VZ-LIBRARY-001","Personal library (camera roll) with sort, filters and multi-select bulk actions",
    "Photographer: sees every own asset regardless of privacy; sorts by date taken/uploaded/views/name; filters untagged, not-in-album, private, NSFW, media type, date range; selects by click/checkbox/drag/keyboard; bulk privacy, edit info, add to album, tags, category, download, delete.",
    "organization", FLICKR, [{"source":"FLICKR-CAMERA-ROLL","note":"private tool for managing all content"},{"source":"FLICKR-ORGANIZR","note":"untagged / not-in-a-set filters, time shift"},{"source":"CHEV-USER-EDITING","note":"select all ., clear Z, drag select, Actions"}],
    deps=["VZ-UPLOAD-001","VZ-ALBUM-001","VZ-TAG-001"], success=["Bulk privacy change on 50 assets persists and every read surface updates"], negative=["Bulk action on an asset the user does not own is rejected"], privacy=["Library visible only to owner (and admins with audit)"], api=["GET /api/v1/me/photos?filters","POST /api/v1/photos:batch"], ui=["/library"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-LIBRARY-002","Edit title, description, alt text, tags, category, dates (taken/uploaded), NSFW flag; date time-shift in bulk",
    "Photographer: edits metadata per asset or in bulk; alt text is a first-class field feeding embeds, federation and OG; date taken editable; bulk time shift.",
    "organization", FLICKR, [{"source":"FLICKR-ORGANIZR","note":"edit dates, time shift"},{"source":"CHEV-USER-MEDIA","note":"edit form: title, tags, album, category, NSFW, description"},{"source":"WCAG","note":"1.1.1 text alternatives"}],
    deps=["VZ-LIBRARY-001"], success=["Alt text saved and rendered in img alt, oEmbed and OG"], negative=["Stop-word filter applied to titles/descriptions when configured"], api=["PATCH /api/v1/photos/{id}"], ui=["/photos/{id}/edit","library bulk edit"], evidence=EV_API+EV_UI)
req("VZ-LIBRARY-003","Replace original (photos only) and lossless rotate",
    "Photographer: replaces the file behind an asset keeping ID, URL, comments, ratings and views; rotates losslessly; videos cannot be replaced.",
    "organization", FLICKR, [{"source":"FLICKR-REPLACE","note":"replace does not reset views; videos cannot be replaced"},{"source":"FLICKR-API","note":"photos.transform.rotate"}],
    deps=["VZ-UPLOAD-001","VZ-MEDIA-001"], success=["Replace keeps ID and interactions; derivatives regenerated"], negative=["Replace with different visibility never widens access"], recovery=["Failed replace leaves the prior original intact"], api=["POST /api/v1/photos/{id}/replace","POST /api/v1/photos/{id}/rotate"], ui=["viewer owner menu"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-VIEWER-001","Photo page and lightbox viewer with zoom/pan, keyboard navigation, captions, metadata, actions",
    "Visitor: opens a photo from any listing in a lightbox without leaving the page; next/prev arrows, Esc closes and returns focus; zoom/pan; title link to the full page; About/Exif/Embed tabs; download when allowed; favorite/rating/comment/share/report actions; album strip.",
    "organization", CHEV, [{"source":"CHEV-USER-VIEWER","note":"fullscreen viewer; → ← Esc; L S E Del shortcuts"},{"source":"CHEV-USER-MEDIA","note":"About/Embed/Info tabs; album thumbnails"},{"source":"DESIGN-BRIEF","note":"viewer zoom/pan, keyboard, captions on small screens"}], edition="all",
    deps=["VZ-MEDIA-001"], success=["Keyboard-only journey through 5 photos; screenshots 390/1440 light/dark"], negative=["Private photo page 404 for anonymous; unlisted reachable by link only"], privacy=["No private data in SSR payload"], api=["GET /api/v1/photos/{id}"], ui=["/p/{id}","lightbox"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-VIEWER-002","Image load threshold and click-to-load full resolution; right-click and download toggles",
    "Owner: images above a size threshold show a reduced version with click-to-load; right-click and download button toggles per site policy.",
    "organization", CHEV, [{"source":"CHEV-THEME","note":"Image load max filesize; Enable download button; Enable right click"}], edition="all",
    deps=["VZ-VIEWER-001"], success=["Settings honored in browser"], negative=["Download disabled does not pretend to secure the bytes (documented)"], ui=["/admin/settings/theme"], evidence=EV_UI)
req("VZ-DOWNLOAD-001","Original and derivative downloads with per-owner and per-site permission, plus bulk zip",
    "Visitor/member: downloads original when the owner allows (owner setting: nobody/followers/members/anyone); size picker; bulk zip of selected/album items bounded (e.g. 500 items) as a job; owner always may download own originals.",
    "organization", FLICKR, [{"source":"FLICKR-DOWNLOAD-PERMS","note":"who can download originals"},{"source":"FLICKR-DOWNLOAD","note":"500 items per zip"},{"source":"CHEV-USER-MEDIA","note":"Download the original file"}],
    deps=["VZ-VIEWER-001","VZ-JOBS-001"], success=["Permission matrix tested; zip job produces archive with manifest"], negative=["Denied download 403 on the object path too, not only the button"], privacy=["Derivative URLs above the public size tier are unguessable when originals are restricted"], api=["GET /api/v1/photos/{id}/download","POST /api/v1/downloads (zip)"], ui=["viewer download menu","library bulk download"], evidence=EV_API+EV_NEG)
req("VZ-ALBUM-001","Albums with nested sub-albums, many-to-many membership, cover, description, ordering, and explicit privacy",
    "Photographer: creates albums and sub-albums (cycle-safe); a photo can be in several albums; cover chosen (public cover required when album is public); sort modes (date taken/uploaded asc/desc, alphabetical, random, manual add-to-start/end) with drag reorder; empty albums allowed; deleting an album never deletes photos.",
    "organization", EXPLICIT, [{"source":"CHEV-COMPARE","note":"Albums & Sub-albums (nested); cover; description; privacy; password"},{"source":"FLICKR-ALBUMS","note":"100,000 items; multiple albums without duplication; sort modes"},{"source":"ARCH","note":"many-to-many; cycle prevention"}], edition="all",
    deps=["VZ-UPLOAD-001"], success=["Photo in two albums; sub-album breadcrumbs; manual reorder persists"], negative=["Making an album its own descendant rejected","Deleting album keeps photos"], privacy=["Album privacy never widens an asset's own visibility"], api=["/api/v1/albums*","POST /api/v1/albums/{id}/items"], ui=["/albums","/a/{id}","add-to-album dialog"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-ALBUM-002","Album privacy: public, private, link-only, password; share grants per album",
    "Photographer: sets album visibility; link-only albums reachable by unguessable URL; password albums require entry; share grants (guest passes) let named or anonymous recipients view non-public albums; grants listed and revocable.",
    "organization", CHEV, [{"source":"CHEV-USER-ALBUM","note":"Public / Private (just me) / Private (anyone with the link) / Private (password protected)"},{"source":"FLICKR-GUEST-PASS","note":"revocable guest passes listed in settings"}], edition="all",
    deps=["VZ-ALBUM-001","VZ-PRIVACY-001"], success=["Each mode tested on album page, thumbnails, counts, search, embeds, export, API, direct object links"], negative=["Password brute force rate-limited; revoked grant 404s immediately incl. cached responses"], privacy=["Link-only albums excluded from listings, sitemap, feeds, federation, search"], api=["PATCH /api/v1/albums/{id} privacy","/api/v1/albums/{id}/grants"], ui=["album privacy dialog","/settings/shares"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-ALBUM-003","Album header, listing sorts, album actions and keyboard shortcuts",
    "Visitor: album shows title, count, date, views, description; sorts recent/oldest/most viewed/most favorited/A-Z; owner actions create/edit/move/delete/cover/share with keyboard shortcuts.",
    "organization", CHEV, [{"source":"CHEV-USER-ALBUM","note":"header metadata; sorting; A J E M K S L H shortcuts"}], edition="all",
    deps=["VZ-ALBUM-001"], success=["Shortcuts documented and tested"], ui=["/a/{id}"], evidence=EV_UI)
req("VZ-ALBUM-004","Album comments and album favorites",
    "Member: comments on and favorites an album as a whole (distinct from item interactions).",
    "organization", CHEV, [{"source":"CHEV-FEATURES","note":"Like system for images and albums"},{"source":"FLICKR-API","note":"photosets.comments"}], edition="Lite",
    deps=["VZ-ALBUM-001","VZ-COMMENT-001","VZ-FAVORITE-001"], success=["Album favorite counted separately"], api=["/api/v1/albums/{id}/comments|favorite"], ui=["/a/{id}"], evidence=EV_API+EV_UI)
req("VZ-COLLECTION-001","Collections: hierarchical grouping of own albums (up to 5 levels), mosaic cover, share by URL",
    "Photographer: groups albums into collections and collections into collections (a node holds albums or sub-collections, not both); cover mosaic from child covers; sharing shows only albums the viewer may see; works on mobile and desktop.",
    "organization", FLICKR, [{"source":"FLICKR-COLLECTIONS","note":"albums or other collections; depth 5; desktop-only (not copied)"}],
    deps=["VZ-ALBUM-001"], success=["5-level tree renders; deeper rejected"], privacy=["Non-visible albums omitted from shared view and counts"], api=["/api/v1/collections*"], ui=["/collections"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-GALLERY-001","Galleries: curated sets of other members' public safe photos with creator opt-out",
    "Member: curates up to N (proposed 500) other people's public, safe-rated photos into a titled gallery with description; owners can opt out of gallery inclusion globally; blocking removes content from the blocker's galleries.",
    "organization", FLICKR, [{"source":"FLICKR-GALLERIES","note":"500 items; other members only; safe only; opt-out"}],
    deps=["VZ-ALBUM-001","VZ-NSFW-001","VZ-BLOCK-001"], success=["Add/remove; opt-out removes and prevents"], negative=["Own item or non-safe/non-public item rejected"], privacy=["Inclusion is a grant checked at add time and at render time"], api=["/api/v1/galleries*"], ui=["/galleries","photo → add to gallery"], evidence=EV_API+EV_UI+EV_NEG, profiles=("full",), decided=["Q-037"])
req("VZ-TAG-001","User-defined tags with on-the-fly creation, autocomplete, tag pages, top tags, rename/delete across items, phrase tags",
    "Photographer: adds comma/space-separated tags with quoted phrases; autocomplete; tag pages /tag/{name} with sorts; top tags; rename or delete a tag across all own items; admin edits/deletes tags globally; optional camera-model auto-tag.",
    "organization", CHEV, [{"source":"CHEV-COMPARE","note":"Tags features list"},{"source":"FLICKR-TAGS","note":"rename across items; quoted phrases"},{"source":"CHEV-FEATURES-NOTSHIPPED","note":"tags marked upcoming on marketing page; shipped per docs"}], edition="all",
    deps=["VZ-UPLOAD-001"], success=["Tag page lists only visible items; counts match"], negative=["Tag spam limits (count/length) enforced"], privacy=["Private items never surface on tag pages or counts"], api=["/api/v1/tags*"], ui=["/explore/tags","/tag/{name}"], evidence=EV_API+EV_UI+EV_NEG, decided=["Q-006"])
req("VZ-TAG-002","Machine tags (namespace:predicate=value) stored and searchable",
    "Photographer/API: structured tags recognized and queryable; not shown as plain tags unless configured.",
    "organization", FLICKR, [{"source":"FLICKR-API","note":"machinetags.* — API-only, no user docs"}],
    deps=["VZ-TAG-001","VZ-SEARCH-001"], success=["Search by machine tag"], api=["search machine_tags"], evidence=EV_API, profiles=("full",))
req("VZ-CATEGORY-001","Admin-defined categories with name, URL key, description; category listings; assignment by users",
    "Owner: creates categories (name ≤32, URL key, SEO description); members assign; category pages with sorts and bulk actions.",
    "organization", CHEV, [{"source":"CHEV-CATEGORIES","note":"fields"},{"source":"CHEV-USER-CATEGORIES","note":"/category/{url-key}"}], edition="all",
    deps=["VZ-ADMIN-002"], success=["Category page with sorts"], negative=["Duplicate URL key rejected"], api=["/api/v1/admin/categories","GET /api/v1/categories/{key}/photos"], ui=["/admin/settings/categories","/category/{key}"], evidence=EV_API+EV_UI)
req("VZ-SHARE-001","Direct links, viewer links, thumbnail/medium links and social share buttons",
    "Visitor: copies viewer/direct/frame/thumbnail/medium links; social share buttons toggleable; OG/Twitter card tags on public pages only.",
    "organization", CHEV, [{"source":"CHEV-USER-ALBUM","note":"Link formats table"},{"source":"OGP","note":"og:image:alt"},{"source":"CHEV-COMPARE","note":"Social share buttons toggle"}], edition="all",
    deps=["VZ-VIEWER-001"], success=["Link formats resolve"], privacy=["No og:image for non-public pages"], ui=["share dialog"], evidence=EV_UI+EV_NEG)
req("VZ-SHARE-002","Embed codes: HTML, Markdown, BBCode (full/linked/medium/thumbnail), on upload complete and in viewer; oEmbed photo type",
    "Visitor/photographer: copies embed codes in the documented format matrix; oEmbed discovery on public photo pages returns type photo; embed of non-public content refused; album embeds require all items public.",
    "organization", CHEV, [{"source":"CHEV-USER-ALBUM","note":"HTML/Markdown/BBCode matrix"},{"source":"OEMBED","note":"photo type"},{"source":"FLICKR-EMBED","note":"album embed requires all items public"}], edition="all",
    deps=["VZ-SHARE-001"], success=["oEmbed endpoint returns photo type with width/height and alt"], privacy=["oEmbed for private/unlisted 404"], api=["GET /api/v1/oembed"], ui=["embed tab"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-SHARE-003","Short URLs and SEO-friendly routes for media, albums, users with configurable route roots",
    "Owner: chooses route words (user/u, image/i, video/v, album/a), root routing, SEO URLs including titles; non-enumerable IDs.",
    "organization", CHEV, [{"source":"CHEV-ROUTING","note":"routing settings; SEO image/album URLs"},{"source":"CHEV-COMPARE","note":"Routing Pro; Crypt-salted IDs"}], edition="Pro",
    deps=["VZ-VIEWER-001"], success=["Route change keeps old links working via redirect"], negative=["IDs non-sequential"], ui=["/admin/settings/routing"], evidence=EV_UI+EV_API)
req("VZ-LICENSE-001","Per-item license (All Rights Reserved, Public Domain, CC0, CC 4.0 family) with account default, bulk change, append-only license table, license filter in search",
    "Photographer: sets license per item or default; displayed on photo page; downloads note license; search filter; license IDs never mutate.",
    "organization", FLICKR, [{"source":"FLICKR-LICENSES","note":"CC 4.0 default; append-only IDs 0-16"}],
    deps=["VZ-LIBRARY-002","VZ-SEARCH-001"], success=["License shown and filterable"], api=["PATCH /api/v1/photos/{id} license"], ui=["edit form","viewer"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-GEO-001","Geotags with geo-privacy, map view, geofences, and EXIF location import policy",
    "Photographer: location per photo (from EXIF when allowed or manual); geo-privacy (who sees location) separate from photo privacy; geofences apply stricter defaults; map view of own/public geotagged photos; location never in public derivatives/exports unless allowed.",
    "organization", FLICKR, [{"source":"FLICKR-GEO","note":"geofences (10); EXIF embedded warning"}],
    deps=["VZ-MEDIA-004"], success=["Map shows only permitted locations"], privacy=["Geo-privacy tested on API, page, search, federation, IPFS"], api=["/api/v1/photos/{id}/location"], ui=["viewer map","/map"], evidence=EV_API+EV_UI+EV_NEG, profiles=("full",), decided=["Q-038"])
req("VZ-PRIVACY-001","Asset-level visibility: public, unlisted (link), private; plus site-wide privacy mode",
    "Photographer: sets visibility per asset (not only per album, unlike Chevereto); owner can force site-private mode (login required) with content privacy defaults; every read surface enforces one authorization decision. Named audiences and follower-only visibility are VZ-PRIVACY-004 (full).",
    "organization", EXPLICIT, [{"source":"CATALOG-F1","note":"decide private/unlisted/public semantics before social features spread"},{"source":"FLICKR-PRIVACY","note":"private/friends/family/public; overrides via groups, people tags, guest passes"},{"source":"CHEV-WEBSITE","note":"Website privacy mode; Content privacy mode"}],
    deps=["VZ-AUTH-001","VZ-UPLOAD-001"], success=["Matrix: 3 visibilities × anonymous/member/grantee/owner/admin × every read surface"], negative=["Tightening privacy invalidates caches, embeds, feeds, federation copies (Delete sent), IPFS (unpin)"], privacy=["Counts (favorites/views) of private items not leaked"], api=["PATCH /api/v1/photos/{id} visibility"], ui=["privacy dialog","/settings/privacy"], evidence=EV_API+EV_UI+EV_NEG, decided=["Q-039"],
    mechanism="Chevereto: privacy only at album level ('Media on its own cannot be private'). Flickr: per-item privacy with friends/family. Vizra outcome: per-item visibility plus album privacy plus explicit grants; album never widens.")
req("VZ-PRIVACY-002","Hide from public search/explore while remaining visible on the profile",
    "Photographer: per-item or default flag to exclude from search, explore, tag pages, feeds and sitemap while the item stays public by link.",
    "organization", FLICKR, [{"source":"FLICKR-HIDE-SEARCH","note":"hidden from public areas other than photostream"}],
    deps=["VZ-PRIVACY-001","VZ-SEARCH-001"], success=["Hidden item absent from search/explore/tags; present on profile"], api=["PATCH /api/v1/photos/{id} hidden"], ui=["privacy dialog"], evidence=EV_API+EV_NEG, profiles=("full",))
req("VZ-PRIVACY-003","Content type (photo / screenshot / art-illustration / virtual / AI-generated) declaration and filter",
    "Photographer: declares content type (with an explicit AI-generated option); filterable in search and explore; owner may require it.",
    "organization", FLICKR, [{"source":"FLICKR-CONTENT-TYPE","note":"four categories; AI guidance"}],
    deps=["VZ-LIBRARY-002"], success=["Filter works"], api=["field content_type"], ui=["edit form"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-PRIVACY-004","Named audiences and follower-only visibility",
    "Photographer: maintains named audiences (friends/family-style lists) and targets an item at an audience or at approved followers; the single core authorization evaluator applies the precedence site mode → asset visibility → album privacy / share grant → audience on every read surface.",
    "organization", EXPLICIT, [{"source":"FLICKR-PRIVACY","note":"friends/family audiences; per-item overrides"},{"source":"CATALOG-F1","note":"decide private/unlisted/public semantics before social features spread"}],
    deps=["VZ-PRIVACY-001","VZ-FOLLOW-002"],
    success=["Audience-targeted item visible to listed members and followers only; matrix covers anonymous/member/follower/non-approved follower/owner/admin across every read surface"],
    negative=["A non-approved follower is denied follower-only items"],
    privacy=["Audience membership never revealed to non-owners; counts exclude items the viewer cannot see"],
    recovery=["Removing a member from an audience invalidates caches, embeds and feeds"],
    api=["GET/POST/PATCH/DELETE /api/v1/me/audiences","PATCH /api/v1/photos/{id} audience targets"],
    ui=["privacy dialog audience picker","/settings/privacy/audiences"],
    evidence=EV_API+EV_UI+EV_NEG, profiles=("full",), decided=["Q-039"])
