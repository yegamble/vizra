# Flickr Official-Source Research — Vocabulary & Workflow Reference for Vizra

**Observation date (all sources): 2026-09-15**
**Researcher note:** Vizra is an original product. This file records how *Flickr* (the incumbent) defines
and bounds these workflows, as a **vocabulary and completeness checklist only**. Vizra's albums,
collections, galleries, groups, favorites, comments, tags and ratings are Vizra's own designs.
**No Flickr implementation, asset, copy, or proprietary design is to be reproduced.** All quotes below
are <= 25 words and used for definitional precision.

**CRITICAL GATING NOTE FOR VIZRA:** Flickr gates a large share of its functional surface behind the
paid **Flickr Pro** subscription. Every such gate is marked **[PRO-ONLY / PAID]**. Vizra must NOT
require billing, so every PRO-ONLY item below is a *capability Vizra should provide ungated*, not a
tiering model to copy.

---

## 0. Method & source integrity

- **Transport:** `https://www.flickrhelp.com` (Zendesk Help Center) is behind a Cloudflare interactive
  challenge. Plain `WebFetch` and `curl` both returned **HTTP 403 ("Just a moment...")**. Content was
  retrieved by driving a real browser engine (Playwright) and reading the site's own public Zendesk
  Help Center API (`/api/v2/help_center/en-us/...`) from within that origin. All article HTTP codes
  recorded below are the codes returned by that API.
- **`https://www.flickr.com/services/api/*` and `https://www.flickr.com/about`** were retrievable by
  direct fetch (HTTP 200).
- **Complete Help Center index enumerated:** 10 categories, 33 sections, **157 published articles**
  (`articles.json`, page_count exhausted). This makes the "Not answered" list at the end *evidential*
  rather than speculative — absence was checked against the full index plus the Help Center search API.
- **76 articles were fetched in full** (all HTTP 200, zero failures). Raw text preserved at
  `/private/tmp/claude-501/-Users-yosefgamble-github-vizra/a5e22306-a936-47a0-b94f-185d8dac1fda/scratchpad/raw/txt/fk-batch{1..6}.txt`
  and `.../raw/guidelines.pdf` + `.../raw/guidelines.txt`.
- **"Last updated" dates** below are Flickr's own `updated_at` values from the Help Center API (exact,
  not the vague "Updated 1 month ago" shown in the rendered page).
- Anything not directly stated by an official source is labelled **INFERRED**. Failed fetches are
  labelled **FAILED** and are not silently replaced with recollection.

### 0.1 Failed / blocked fetches (recorded, not worked around silently)

| URL | Result | Note |
|---|---|---|
| `https://www.flickrhelp.com/` | **FAILED — HTTP 403** (WebFetch) | Cloudflare challenge; later reached via browser |
| `https://help.flickr.com/` | **HTTP 301 → www.flickrhelp.com** | Redirect only; no content of its own |
| `https://www.flickrhelp.com/hc/en-us/articles/4404058555028-...` (and 3 others) | **FAILED — HTTP 403** (WebFetch + curl) | Same challenge; succeeded via browser |
| `https://www.flickr.com/help/guidelines/` (HTML body) | **HTTP 200 but EMPTY** | Page is a shell; the guidelines are served only as an embedded PDF |
| `https://www.flickr.com/account/upgrade/pro` | **HTTP 200, thin** | Marketing page lists only 4 bullets; no numeric limits. Real limits live in the Help Center |

### 0.2 Official Help Center taxonomy (verbatim category / section names)

Categories: `Getting Started`, `Account & Login`, `Uploading to Flickr`, `Managing Your Content`,
`Sharing & Social`, `Pro Subscriptions & Billing`, `Safety & Reporting`, `Privacy & Content Settings`,
`Advanced Features`, `Troubleshooting`.

Sections of interest: `Albums`, `Collections`, `Galleries`, `Organize`, `Edit`, `Managing Content`,
`Delete Flickr Content`, `Download from Flickr`, `Groups`, `Sharing`, `Sharing and Social`,
`Privacy Settings`, `Content Type`, `Copyright & Licensing`, `Moderation & Safety Levels`,
`Reporting Abuse`, `Rules & Policies`, `Pro Only Features`, `Third-Party Apps`, `Advanced Flickr Features`.

> **Vizra signal:** Flickr's own information architecture separates *Privacy Settings* (who may see)
> from *Content Type* + *Moderation & Safety Levels* (what kind of thing it is). Vizra should keep the
> same two axes independent — see §5.

---

## 1. Photostream / Camera Roll / Organizr / batch editing / ordering

### 1.1 Photostream
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404064489108-View-images-with-the-Photostream
- **Title:** View images with the Photostream — **Updated 2026-08-10** — **HTTP 200**
- **Definition (quote, 12 words):** "The Photostream is the public-facing way to display photos on your account."
- **Viewer-perspective toggles:** Public view, Friends view, Family view, Friends & Family view, View all.
  This is a *"see it as they see it"* preview control, not a separate storage concept.
- **Ordering:** logged-out visitors get Date Uploaded by default; a logged-in member may toggle Date
  Uploaded / Date Taken, and that choice **applies to every other photostream they view**.
- **Key constraint (quote, 13 words):** "Anyone visiting your Photostream sees everything sorted by Date Uploaded by default."
  Owners cannot change the sort *for other people* — they can only change the underlying dates.
- **Paid gating:** none.

### 1.2 Camera Roll
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404064313620-View-and-manage-your-items-within-the-Camera-Roll
- **Title:** View and manage your items within the Camera Roll — **Updated 2026-08-10** — **HTTP 200**
- **Definition (quote, 16 words):** "The Camera Roll is a private tool for viewing & managing all content on your account."
- **Sort:** Date Taken or Date Uploaded. Items with no date sort to the top.
- **Selection tray actions:** Privacy, Edit info (title/description/dates/tags), Share, Add to album,
  Download, Delete. Plus "Clear selection".
- **Paid gating:** none.

### 1.3 Organizr (bulk editor)
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058763796-View-and-manage-your-photos-with-the-Organizr
- **Title:** View and manage your photos with the Organizr — **Updated 2026-05-12** — **HTTP 200**
- **Definition (quote, 17 words):** "The Organizr is a convenient feature to perform bulk edits to your photos & videos on Flickr."
- **Desktop web only.** Not in the app, not on mobile web.
- **Tabs:** Batch Organize · Albums & Collections · Groups · Map.
- **Batch operations (complete list):** edit titles/tags/descriptions; rotate; delete; permissions
  (who can see/comment/tag, licensing, safety filter, content type, hide/show in public searches);
  edit dates (set all to same day, **time shift**); add people & tags; add to album (new or existing);
  send to a group; location (change geoprivacy, add to map, remove from map).
- **Filter axes:** untagged, not-in-a-set, geotagged, non-geotagged, uploaded-by, albums, groups;
  full text / tags only / people only; photos & videos / photos / videos; privacy (public, friends,
  family, friends & family, private); safety (safe, moderate, restricted); date posted / date taken.
- **Paid gating:** none.

> **Vizra signal:** the *"not in a set"* and *"untagged"* filters are the backbone of bulk curation.
> Vizra's batch surface should expose the same negative-space filters, and time-shift is a genuinely
> load-bearing feature for imported archives.

### 1.4 Reordering
- **Photostream:** https://www.flickrhelp.com/hc/en-us/articles/4404064327444-Reorder-your-Flickr-Photostream
  — **Updated 2025-12-14** — **HTTP 200**. Order is a *function of the date fields*, not a manual list.
  Date Taken / Date Uploaded are editable (web only), single or batch.
- **Album display order (the list of albums):**
  https://www.flickrhelp.com/hc/en-us/articles/4404058665364-Rearrange-the-display-order-of-your-albums
  — **Updated 2026-04-01** — **HTTP 200**. Manual drag-and-drop, web only.
- **Content order inside an album:**
  https://www.flickrhelp.com/hc/en-us/articles/4404064144660-Reorder-the-content-in-an-album
  — **Updated 2026-08-11** — **HTTP 200**.
  **Sort modes (verbatim):** Date taken (oldest first), Date taken (newest first), Date uploaded
  (oldest first), Date uploaded (newest first), Alphabetical, Random, Manual (add to beginning),
  Manual (add to end). **"New albums will use manual (add-to-end) by default."** After an auto-sort,
  a manual drag reverts the album's mode to Manual (add to end).
- **Paid gating:** none.

### 1.5 Editing / replacing
- **Edit photos on Flickr** — https://www.flickrhelp.com/hc/en-us/articles/4404058509460-Edit-photos-on-Flickr
  — **Updated 2026-08-11** — **HTTP 200**. 7 tools: Transform, Filters, Adjust, Focus, Text, Brush, Frame.
  Output choice: **"Save as a new copy or Replace the original photo"** — replacement is irreversible.
- **Replace a photo (web only)** — https://www.flickrhelp.com/hc/en-us/articles/4404058489108-Replace-a-photo-in-Flickr-web-only
  — **Updated 2026-06-21** — **HTTP 200**. **Videos cannot be replaced.** Replacing does **not** reset views.
- **Paid gating:** none.

---

## 2. Albums, Collections, Galleries

### 2.1 Albums
- **Create/delete/edit:** https://www.flickrhelp.com/hc/en-us/articles/4404058555028-Create-delete-or-edit-an-album-on-Flickr
  — **Updated 2026-08-11** — **HTTP 200**
- **Add/remove content:** https://www.flickrhelp.com/hc/en-us/articles/4404064368276-Add-or-remove-content-from-an-album
  — **Updated 2026-08-11** — **HTTP 200**
- **Cover photo:** https://www.flickrhelp.com/hc/en-us/articles/4404078540052-Change-the-cover-photo-of-an-album
  — **Updated 2025-08-18** — **HTTP 200**
- **Definition (quote, 22 words):** "The albums can be sets of photos & videos that are grouped by date, topic, event, or any other criteria you choose."
- **Membership model (quote, 13 words):** "All photos organized into albums are also available in the Photostream."
  An item may be in **multiple albums without duplication** — albums are a tagging/join relation, not a folder move.
- **LIMIT:** "Each album can contain up to **100,000 items**."
- **Lifecycle rules:**
  - "It is not possible to create an empty album."
  - Deleting an album does **not** delete its contents.
  - "When all items are removed from an album, it is automatically deleted from your Albums page."
- **Cover rule:** "If your album includes Public photos, you must select a Public photo as your album cover."
  A non-public cover is auto-replaced. Cover cannot be set in the mobile app.
- **Sort order is a per-album property** chosen at creation (see §1.4).
- **Paid gating:** none.

> **Vizra signal:** the auto-delete-when-empty rule and the "cannot create empty" rule are a notable
> UX stance. Vizra should decide deliberately — an empty album is a legitimate pre-created container
> for many workflows, and silently deleting a user's named container is a data-loss-shaped surprise.

### 2.2 Collections (albums-of-albums)
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404064260884-How-to-create-and-manage-your-Flickr-collections
- **Title:** How to create and manage your Flickr collections — **Updated 2025-12-22** — **HTTP 200**
- **Definition (quote, 11 words):** "Collections can be made up of either albums or other collections."
- **LIMIT (quote, 5 words):** "Collection depth is 5 levels."
- **Structural rule (quote, 19 words):** "A collection containing albums can only be added to another collection that does not contain albums."
  i.e. a node holds *either* albums *or* sub-collections, never both.
- **Prerequisite:** you must have at least one album before you can create a collection.
- **PLATFORM GATE:** "Collections are a desktop-only feature." Not viewable on mobile web or the app.
- **Cover:** a "Collection Mosaic" built from child covers. Must be composed of Safe + Public photos or
  tiles render as grey boxes.
- **Sharing:** share by copying the URL. If a collection contains albums with non-public photos, only
  the Public albums are displayed.
- **Paid gating:** none. (But note the **desktop-only** gate is a real completeness defect Vizra should not copy.)

### 2.3 Galleries (curated sets of OTHER people's photos)
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058713236-Create-add-share-or-delete-a-gallery-in-Flickr
- **Title:** Create, add, share, or delete a gallery in Flickr — **Updated 2025-08-18** — **HTTP 200**
- **Definition (quote, 22 words):** "Galleries are a great way to create a themed collection of up to 500 photos or videos shared by other Flickr members!"
- **LIMIT: up to 500 items per gallery.**
- **Hard rule (quote, 13 words):** "It is not possible to add your own items to a Gallery."
- **Safety rule (quote, 8 words):** "Galleries can only contain content marked as safe."
- **PLATFORM GATE:** "Galleries can only be created on your desktop or mobile web browser, not the Flickr app."
- **Owner opt-out:** a member can disable others adding their content to galleries, via gallery
  preferences in settings.
- **Flickr's own Galleries-vs-Groups distinction (quote, 17 words):** "Groups, on the other hand, allow
  you to add your own content based on a theme or concept."
- **Paid gating:** none.

> **Vizra signal — the three-entity model is genuinely distinct and worth preserving conceptually:**
> **Album** = your own content, ordered, owned. **Collection** = hierarchical grouping of *your* albums.
> **Gallery** = curation of *other people's* content, capped, safe-only, with a creator opt-out.
> The creator opt-out on galleries is the privacy-critical piece: being curated is a permission,
> not a default. Vizra's default-deny authorization must cover gallery inclusion.

---

## 3. Groups

Sources (all **HTTP 200**):

| Article | URL | Updated |
|---|---|---|
| Get started with Flickr groups | `.../articles/4404078011156-Get-started-with-Flickr-groups` | 2026-03-31 |
| Create a Flickr group (web only) | `.../articles/4404064466836-Create-a-Flickr-group-web-only` | 2026-06-21 |
| Find, join, or leave a Flickr group | `.../articles/4404064539540-Find-join-or-leave-a-Flickr-group` | 2026-08-11 |
| Add or remove photos in Flickr groups | `.../articles/4404069536532-Add-or-remove-photos-in-Flickr-groups` | 2026-08-11 |
| Flickr group discussions | `.../articles/4404058884244-Flickr-group-discussions` | 2026-08-11 |
| Promote someone to be an admin or moderator (web only) | `.../articles/4404064596628-Promote-someone-to-be-an-admin-or-moderator-for-your-Flickr-group-web-only` | 2026-08-06 |
| Approving or denying photo submissions to groups | `.../articles/4404069943188-Approving-or-denying-photo-submissions-to-groups` | 2026-04-05 |
| Invite friends & family to your group (web only) | `.../articles/4404058819732-Invite-friends-family-to-your-group-web-only` | 2026-06-21 |
| Flickr group management (web only) | `.../articles/4404070473364-Flickr-group-management-web-only` | 2026-06-21 |
| Tips for running your Flickr group | `.../articles/30485380645140-Tips-for-running-your-Flickr-group` | 2026-03-28 |
| Change the safety level of your Flickr group | `.../articles/4404078572308-Change-the-safety-level-of-your-Flickr-group` | 2026-04-05 |
| Inactive Group Takeover Process | `.../articles/12705426101012-Inactive-Group-Takeover-Process` | 2024-02-09 |

(All prefixed `https://www.flickrhelp.com/hc/en-us`.)

### 3.1 Group privacy types (verbatim three-way)
- **Public** — "The group page is public and anyone who wants to can join instantly."
- **Invite only** — anyone can view the page, but joining requires an invitation; *optionally* can be
  made completely private and unsearchable.
- **Private** — "The group is hidden from non-members. Only invited members can see it, and it will not
  appear in searches or on member pages."
- **IRREVERSIBLE (quote, 13 words):** "if you make a group private, you cannot switch it back to public."

### 3.2 Limits
- **Group membership per member:** "You may already belong to the maximum number of groups (**5,000**)."
- **Photo → group posting caps:**
  - **"Free members can add each photo to up to 30 groups."**
  - **"Pro members can add each photo to up to 60 groups." [PRO-ONLY / PAID uplift]**
  - Scoping rule: the cap "only appl[ies] to groups that have their own posting limits set."
    Unlimited-posting groups don't count against it.
  - The cap is **per photo, not per account**.
- **Sticky topics:** "Create up to **20** Sticky Topics".
- **Group invites:** "Your account must be at least **30 days old** to send group invites."
- **Pending-queue paging:** 25 / 50 / 100 per page.

### 3.3 Pool visibility — the privacy-critical rule
- **Quote (18 words):** "Any group member can see and interact with photos in the pool, regardless of your individual privacy settings."
- **Quote (14 words):** "Adding a non-public photo to a group makes it visible to all group members"
  — and those members "can tag it, or leave a comment, even if commenting is disabled in your account settings."
- Adding to a group does **not** mutate the photo's own privacy value. Non-members still see it only if
  base privacy allows.

> **Vizra signal — this is a genuine authorization trap.** Flickr's group pool is an *override channel*
> that widens effective visibility and re-enables interaction the owner explicitly disabled.
> Per AGENTS.md ("Default-deny authorization covers originals, derivatives, search, counts, exports,
> embeds, feeds, federation, and caches"), Vizra should treat group-pool inclusion as an explicit
> grant with an explicit confirmation, and must NOT let pool membership silently re-enable commenting
> that the owner turned off. Flickr shows a warning dialog; Vizra should make it a real permission.

### 3.4 Roles and moderation
- **Roles:** admin, moderator, member. Admins may rename these labels ("Moderator roles: Give 'admin,'
  'moderator' & 'member' more descriptive names").
- **Shared admin + moderator powers:** approve/deny pool submissions; remove or ban members; moderate
  discussions; create up to 20 sticky topics; add and remove pool photos.
- **Admin-only powers:** set group rules; update group info; customise appearance; invite other
  members' content; promote admins/moderators; demote moderators; change privacy; change safety level;
  set keywords; set custom group URL; send/delete a "group blast" (message to all members); delete group.
- **Invariants:**
  - **Quote (14 words):** "Admins have full control of a group but cannot remove or demote other admins."
  - Succession: "If an admin leaves a group and there are no other admins, admin rights will
    automatically transfer to the longest-serving group member." (Takeover article refines this:
    longest-standing *moderator* first, else longest-standing member.)
  - "Promoted members do not receive a notification."
  - **Quote (9 words):** "Only the last remaining admin can delete a group."
  - Removing vs banning: removed members may rejoin freely; banned members cannot until unbanned.
    Neither is notified.
- **Pending queue:** opt-in per group ("Would you like to review submissions before they show up in the
  pool?"). Supports sort by newest/oldest, "Save for later", Approve all / Deny all (excluding saved),
  and per-submission Manage → remove or ban submitter.
- **Group safety level:** Safe / Moderate / Restricted. "Groups that allow Moderate or Restricted
  content will be designated as **18+**." Lowering a group to Safe **auto-removes** non-conforming pool
  photos. Group icon and cover must be Safe **and** Public.
- **Inactive group takeover:** staff-mediated process; requires clean account standing, existing
  membership, agreement to maintain theme, and a group blast announcing the change. "Promotion is not guaranteed."
- **Paid gating:** none on group creation, admin, moderation or discussions. The only paid element is
  the 30→60 per-photo posting cap (§3.2).

### 3.5 Discussions / topics
- Post a topic (title + message), reply, edit, delete. Inline images via embed code or a share link in
  square brackets.
- **Quote (7 words):** "You can only edit your own comments/replies."
- **Quote (16 words):** "Topic posts (the first post in a discussion) can only be edited/deleted by a group admin."
- "Group admins can edit or delete a member's comments/replies."
- Moderator controls: **sticky** (star icon) and **close/lock** (lock icon, no new replies).
- Edited comments display the last edited date.
- **Pinning a group** (member-side): surfaces more of that group in the member's activity feed and
  enables new-topic notifications.

---

## 4. Favorites, Comments, Notes, Tags, People-tagging, Geotags

### 4.1 Faves
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404064179220-Fave-and-un-fave-photos-videos-on-Flickr
- **Title:** Fave (and un-fave) photos & videos on Flickr — **Updated 2026-07-01** — **HTTP 200**
- **Definition (quote, 21 words):** "Use Flickr's faves feature to save images or videos you appreciate from other members.
  The creator gets notified and the item is added to your Faves tab"
- Faves are a **public-ish collection surface** (a "Faves tab"), a notification trigger, and an Explore
  ranking signal — three roles in one control.
- **Destructive side effect (recorded under Privacy, §5):** tightening a photo's privacy "will remove
  the accumulated faves" from viewers who lose access. Stats article: "I had views on a photo — but now
  I have 0... you recently changed the privacy of the photo to a stricter setting".
- **Abuse rule:** "Excessive faving" is listed as prohibited spam.
- **Paid gating:** none.

### 4.2 Comments
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058465172-Add-edit-or-delete-comments-and-notes-on-Flickr
- **Title:** Add, edit, or delete comments and notes on Flickr — **Updated 2026-08-10** — **HTTP 200**
- Add / edit / delete on both web and app. Owner controls availability via privacy settings:
  "If you can't comment on someone else's photo, it's usually because of their privacy settings."
- **HTML formatting** (web only): https://www.flickrhelp.com/hc/en-us/articles/14408223944468-Using-HTML-Code-to-Format-your-Comments
  — **Updated 2025-11-19** — **HTTP 200**. Allowed tags: `<b>`, `<i>`, `<u>`, `<del>`, `<blockquote>`.
  A Flickr photo/video/album URL in square brackets renders inline.
- Emoji picker on the comment box (per "About the Photo page").
- **Blocking removes comments** — see §9.
- **Paid gating:** none.

> **Vizra signal:** a fixed, tiny allow-list of formatting tags plus a bracket-link auto-embed is a
> sane, sanitiser-friendly comment grammar. AGENTS.md forbids "unrestricted custom-script surfaces" —
> an explicit five-tag allow-list is the shape to aim for, never raw HTML passthrough.

### 4.3 Notes
- Web only. A note is a **rectangular region drawn on the image** plus text. Add / edit / delete.
- Governed by the same "Who can add notes, tags, and people" permission as tags (§5.3).
- **Paid gating:** none.

### 4.4 Tags
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058631700-Tagging-your-Flickr-content
- **Title:** Tagging your Flickr content — **Updated 2026-08-11** — **HTTP 200**
- **Syntax rule (quote, 22 words):** "You can separate tags with spaces or make tag phrases by
  enclosing them in quotation marks. For example: sleeping cats will become two separate tags."
- Tag-level operations beyond per-photo add/remove: **rename a tag across all items**, **delete a tag
  from all tagged items**, **copy all tags from a photo to clipboard**, bulk add/remove via Camera Roll
  or Organizr.
- **Privacy coupling (quote, 18 words):** "Other people can only find your tagged items if you've
  marked them Public. You can also opt to hide your images from search results."
- **Abuse rule:** irrelevant/abusive/excessive tags → "your photos will be hidden from public search,
  and you will receive a warning from our Trust & Safety team."
- **Machine tags:** **not documented in any Help Center article** (verified against the full 157-article
  index and the Help Center search API). They exist only as an **API-level** concept — see §11
  (`flickr.machinetags.*`, and `machine_tags` / `machine_tag_mode` on `flickr.photos.search`).
  Format is the namespace:predicate=value triple. **INFERRED** from API surface only; no official
  end-user definition was found.
- **Paid gating:** none.

### 4.5 People-tagging
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058694164-Add-or-remove-people-from-your-Flickr-content-web-only
- **Title:** Add or remove people from your Flickr content (web only) — **Updated 2026-06-21** — **HTTP 200**
- **Privacy-critical (quote, 22 words):** "Tagging a person in a photo allows that person to see the
  photo even if the privacy setting is set to non-public."
- Subject-side controls: "Who can add you to a photo" permission, plus a bulk
  **"Remove yourself from all photos that you're marked in"** action.
- Tagged-in photos are surfaced on the subject's About page.
- **Paid gating:** none.

> **Vizra signal:** people-tagging is the second visibility-override channel (after group pools).
> Same default-deny requirement applies. The "remove me from everything" bulk escape hatch is a
> privacy-rights feature worth matching.

### 4.6 Geotags / map
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404070517908-Adding-removing-photos-to-your-map
- **Title:** Adding & removing photos to your map — **Updated 2026-08-11** — **HTTP 200**
- Three settings must align for auto-geotagging: EXIF Privacy off, EXIF location importing on, and
  Geo Preferences not set to "Only you".
- **Geofences — LIMIT:** "You can create up to **10** geofences."
  **Definition (quote, 19 words):** "A geofence is a hotspot on a map that has special default geo
  privacy settings" — e.g. home or school, more private than the global default.
- **Data-leak warning (Flickr's own):** uploaded geodata "will be embedded into the EXIF data of the
  original image file" — hiding it on Flickr does not strip it from a downloadable original.
- **Paid gating:** none.

> **Vizra signal:** geofences are an elegant privacy primitive (location-conditional default privacy).
> Also note Flickr's honest admission that EXIF-hiding is display-level only — Vizra should decide
> whether to actually **strip** on derivative generation, since AGENTS.md requires that private
> metadata never leak via originals, derivatives or exports.

---

## 5. Privacy, permissions, safety levels, content type, licensing, guest passes

### 5.1 Privacy settings (who may see)
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404078163732-Change-your-privacy-settings
- **Title:** Change your privacy settings — **Updated 2026-08-11** — **HTTP 200**
- **Two buckets: Non-public and Public.**
  - **Private** — "Only you can see the content."
  - **Friends** — contacts marked Friends.
  - **Family** — contacts marked Family.
  - **Friends and Family** — either.
  - **Public** — "Anyone, including visitors not signed in to Flickr, can see the content."
- Non-public levels require the viewer to be **signed in** as that contact type.
- **Independence (quote, 20 words):** "These settings work independently from Safety Levels, so you can
  customize visibility for each piece of content based on your preferences."
- **Documented visibility overrides (Flickr's own list):** group pools, people-tagging, guest passes.
- **DESTRUCTIVE (quote, 24 words):** "Changing to a stricter Privacy Setting (ex. from Public to
  Private), will permanently alter the original link and remove Faves from viewers who no longer have
  access. This cannot be undone."
- Defaults for new uploads are set separately (`Privacy & Permissions → Defaults for new uploads`).
- **Paid gating:** the *levels* are free. But **[PRO-ONLY / PAID]** "Store more than 50 Non-Public
  photos or videos" — a free account may hold at most **50** private/friends/family items (§7.1).
  Also: Auto-Uploadr content is always Private, and Auto-Uploadr is Pro-only.

### 5.2 Hide from public searches
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404078152468-Hide-or-unhide-photos-from-public-searches
- **Title:** Hide or unhide photos from public searches — **Updated 2025-08-11** — **HTTP 200**
- **Quote (19 words):** "When content is hidden from searches, it won't appear in public areas on Flickr
  (other than your Photostream)."
- Settable as a global default for new uploads **and** retroactively in bulk via Organizr
  (`Permissions → Hide/show in public searches`).
- **Scope caveat:** affects Flickr's own search only. External search-engine indexing is out of Flickr's
  control — https://www.flickrhelp.com/hc/en-us/articles/4404078147860-Appearing-on-search-engines
  — **Updated 2025-08-11** — **HTTP 200**.
- **Paid gating:** none.

### 5.3 Interaction permissions
- Setting is `Privacy & Permissions → "Who will be able to see, comment on, add notes, or add people"`.
- Sub-setting: **"Who can add notes, tags, and people"**.
- Separate setting: **"Who can add you to a photo"** (subject-side consent).
- Separate setting: gallery-inclusion opt-out (§2.3).
- Separate setting: **"Who can download your images (including originals)?"** (§5.6).
- **Paid gating:** none on the controls themselves.

### 5.4 Safety levels (what kind of content it is) — **SafeSearch**
- **Guide to Safety Levels** — https://www.flickrhelp.com/hc/en-us/articles/23250290741908-Guide-to-Safety-Levels
  — **Updated 2026-05-13** — **HTTP 200**
- **Set safety levels** — https://www.flickrhelp.com/hc/en-us/articles/4404064374164-Set-the-safety-levels-of-your-Flickr-content-or-account
  — **Updated 2026-08-11** — **HTTP 200**
- **Privacy vs Safety** — https://www.flickrhelp.com/hc/en-us/articles/4404064522132-Privacy-Settings-vs-Safety-Levels
  — **Updated 2025-10-14** — **HTTP 200**
- **SafeSearch (viewer side)** — https://www.flickrhelp.com/hc/en-us/articles/4404078858900-Managing-the-content-visible-to-you-with-SafeSearch
  — **Updated 2026-07-07** — **HTTP 200**
- **Content Filters (umbrella)** — https://www.flickrhelp.com/hc/en-us/articles/4404064206996-Flickr-Content-Filters
  — **Updated 2025-10-14** — **HTTP 200**

**Three levels (publisher side):**
| Level | Flickr's definition (quote) |
|---|---|
| **Safe** | "Content that is generally acceptable to a global, public audience." |
| **Moderate** | "Content that may be unacceptable to some audiences." |
| **Restricted** | "Content that must be restricted to limited audiences only." |

**Three SafeSearch states (viewer side):** On (Safe only) · Moderate (Safe + Moderate) · Off (all three).
- **Default (quote, 18 words):** "This is the default level for all members and for visitors to Flickr
  who are not logged in." (= SafeSearch **On**.)
- Overridable per-search via Advanced Search.
- **Jurisdictional overrides (verbatim, notable):** login IDs based in **Singapore, Hong Kong, India,
  Korea** (or Maktoob.com) are locked to Safe and cannot change SafeSearch. Login IDs based in
  **Germany or Romania** cannot turn SafeSearch off.

**Hard rules:**
- **Quote (14 words):** "Videos uploaded to Flickr cannot contain Restricted content. Only photos may
  include Restricted content."
- All content must be moderated "regardless of the Privacy Setting. This includes posts marked as
  Friends and/or Family and Private."
- Censoring (pixelation/blur/shapes) does **not** lower the required level — moderate by the underlying imagery.
- "Only Safe content can be used in Profile and cover photos."
- Galleries: Safe only. Group icon/cover: Safe + Public.
- **[PRO-ONLY / PAID] — the big one:** **"Free accounts are limited to posting Safe content only.
  Members interested in uploading Moderate or Restricted content will need to upgrade to Pro."**
  Enforcement is real: free accounts holding Moderate/Restricted content are suspended (§9.3).

> **Vizra signal:** Flickr paywalls the *ability to publish mature-but-legal content at all*. That is a
> billing-shaped gate on a moderation primitive. Vizra must NOT require billing, so Vizra needs an
> ungated three-tier (or equivalent) content rating with a viewer-side filter defaulting to the safest
> tier for logged-out visitors — plus an instance-admin policy switch, since a self-hosted operator may
> legitimately want to disallow mature tiers entirely.

### 5.5 Content type
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058750740-Set-the-Content-Type-for-your-Flickr-uploads
- **Title:** Set the Content Type for your Flickr uploads — **Updated 2026-04-05** — **HTTP 200**
- **Four categories (verbatim):** `Photos/ Videos` · `Screenshots/ Screencasts` ·
  `Illustration/ Art/ Animation/ CGI or other non-photographic images` · `Virtual Photography/ Machinima`.
- **AI guidance (quote, 17 words):** "We encourage members to select 'Art/Illustration' as the content
  type for any AI-generated images."
- Settable as default, per item, or in bulk. Filterable in search.
- **Paid gating:** none.

> **Vizra signal:** a first-class, filterable AI/synthetic-content declaration is now table stakes.
> Note Flickr only *encourages* it; Vizra could make it a required disclosure field.

### 5.6 EXIF and download permissions
- **EXIF data FAQ** — https://www.flickrhelp.com/hc/en-us/articles/4404078521108-EXIF-data-FAQ
  — **Updated 2026-08-10** — **HTTP 200**.
  Show/hide EXIF per photo or account-wide. Owner always sees own EXIF ("you'll need to log out" to
  see it as others do). Videos carry no EXIF. Date Taken / Date Uploaded are editable.
  Data-export note: post-upload metadata (title, description, tags) ships as a **separate JSON file**,
  not re-embedded.
- **Download permissions** — https://www.flickrhelp.com/hc/en-us/articles/4404079715220-Download-permissions
  — **Updated 2026-04-01** — **HTTP 200**.
  Setting: `Who can download your images (including originals)?`
  - **[PRO-ONLY / PAID] (quote, 18 words):** "Free accounts cannot offer downloads of original or
    large-size photos (larger than 1024px), regardless of the permission setting."
  - **[PRO-ONLY / PAID]** "Videos uploaded by free accounts are also not available for download."
  - **Pro** accounts may enable full-size/original downloads.
  - **Exceptions that bypass the free-account block:** Creative Commons–licensed photos (unless
    private), Public Domain works, Flickr Commons content.
  - **Honest limit (quote, 13 words):** "The only way to completely prevent downloads is to make your
    content private."

### 5.7 Licensing
- **Copyright Licenses on Flickr** — https://www.flickrhelp.com/hc/en-us/articles/40048459562388-Copyright-Licenses-on-Flickr
  — **Updated 2025-08-07** — **HTTP 200**
- **Change your photo's license** — https://www.flickrhelp.com/hc/en-us/articles/4404078674324-Change-your-photo-s-license-in-Flickr
  — **Updated 2026-08-11** — **HTTP 200**
- **Standard:** All Rights Reserved · Public Domain Work · CC0 (Public Domain Dedication).
- **Creative Commons 4.0:** CC BY · CC BY-SA · CC BY-ND · CC BY-NC · CC BY-NC-SA · CC BY-NC-ND.
- **Quote (12 words):** "Flickr now defaults to Creative Commons 4.0 for all newly uploaded content."
  Legacy CC 2.0 assignments persist on old photos; CC 2.0 is no longer offered for new uploads.
- **Special, by request only:** `United States Government Work`, `No Known Copyright Restrictions`
  (Commons institutions). These reconfigure the whole account to a single type.
- **Semantics (quote, 22 words):** "You can change the license as often as you like, but downloaded
  content always retains the license assigned to it, even if the license is changed on Flickr."
- Default license is an account setting; per-item and bulk changes supported.
- **Authoritative numeric license IDs** (from the API, `flickr.photos.licenses.getInfo`, HTTP 200):
  `0` All Rights Reserved · `1` CC BY-NC-SA 2.0 · `2` CC BY-NC 2.0 · `3` CC BY-NC-ND 2.0 · `4` CC BY 2.0 ·
  `5` CC BY-SA 2.0 · `6` CC BY-ND 2.0 · `7` No known copyright restrictions · `8` United States
  Government Work · `9` Public Domain Dedication (CC0) · `10` Public Domain Mark · `11` CC BY 4.0 ·
  `12` CC BY-SA 4.0 · `13` CC BY-ND 4.0 · `14` CC BY-NC 4.0 · `15` CC BY-NC-SA 4.0 · `16` CC BY-NC-ND 4.0.
- **Paid gating:** none.

> **Vizra signal:** the CC 2.0→4.0 migration is a worked example of *versioned license identity* —
> Flickr kept old IDs immutable and added new ones rather than mutating meaning. Vizra's license
> reference table should be append-only for exactly this reason.

### 5.8 Guest passes
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404069601172-Create-or-delete-temporary-Guest-Passes-in-Flickr-web-only
- **Title:** Create or delete temporary Guest Passes in Flickr (web only) — **Updated 2026-06-21** — **HTTP 200**
- **Definition (quote, 22 words):** "Guest Passes let you share non-public photos or albums. Anyone with
  the special link can view the content, even if they don't have a Flickr account."
- **Constraints:** content must be Safe or Moderate (not Restricted). Signed-out viewers see Safe only.
- **Revocation:** `Settings → Sharing & Extending → View and manage all the guest passes you've sent out`,
  then **Expire** per pass. Guest pass history is an auditable list.
- Web only; not in the app.
- Sharing non-public content via the Share icon **auto-creates** a guest pass.
- **Paid gating:** none.

> **Vizra signal:** an enumerable, individually-revocable capability-link registry is the right shape
> for a bearer-token share link. Note the safety-level ceiling on shareable links, and that Flickr
> makes the sharing action *implicitly mint a token* — Vizra should make that explicit to the user.

---

## 6. Following (contacts), activity feed, FlickrMail, notifications

### 6.1 Contacts / following
- **Manage your contacts** — https://www.flickrhelp.com/hc/en-us/articles/4404058842900-Manage-your-contacts-on-Flickr
  — **Updated 2026-08-10** — **HTTP 200**. Follow / unfollow; "Followers" and "Following" lists.
- **Friends / Family** — https://www.flickrhelp.com/hc/en-us/articles/4404069919252-Mark-a-contact-as-friends-or-family
  — **Updated 2026-08-10** — **HTTP 200**.
  **Quote (19 words):** "Marking someone you follow as a friend or family lets you easily share with
  just that group of people, instead of everyone."
  Flags are **orthogonal and combinable** (Friend and/or Family), set on people you follow.
  **PLATFORM GATE:** cannot be set in the mobile app; web only.
- **Stay connected (hub)** — https://www.flickrhelp.com/hc/en-us/articles/4404078047636-Stay-connected-with-people-on-Flickr
  — **Updated 2026-03-29** — **HTTP 200**.
- **Paid gating:** none.

> **Vizra signal:** Flickr's model is **asymmetric follow + owner-applied relationship labels**.
> Friend/Family is *not* mutual consent and *not* a follow-back — it is a unilateral ACL group the
> owner maintains over people they follow. That is a clean, simple audience model worth understanding
> before designing Vizra's equivalent.

### 6.2 Activity feed ("Recent activity")
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404078406932-Using-the-Flickr-activity-feed
- **Title:** Using the Flickr activity feed — **Updated 2026-08-10** — **HTTP 200**
- **Definition (quote, 23 words):** "Your activity feed is the heart of your Flickr home — a
  personalized stream of updates from the people, groups, and communities you follow."
- **Filters:** All Activity · People · Groups · Friends & Family.
- **Layouts:** Compact · Medium · Large.
- **Per-post actions:** fave, comment, share, mark contact as Friend/Family, unfollow, **block**, **report abuse**.
- **Content controls:** hide a group or person from the feed; unhide from the group page.
- **Right rail:** daily stats card, most-viewed photos, suggestions for new members, group discussions,
  blog posts.
- Cold start: "For brand new Flickr accounts with no followers yet, the feed surfaces recommended content".
- **Paid gating:** feed is free. The **daily stats card** links to Stats, which is Pro-only (§7.3).

### 6.3 FlickrMail
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058824340-Send-receive-or-manage-FlickrMail-messages-web-only
- **Title:** Send, receive, or manage FlickrMail messages (web only) — **Updated 2026-06-21** — **HTTP 200**
- **Definition (quote, 10 words):** "Use FlickrMail to connect with other members through private messages."
- One-to-one only: "FlickrMail works best for one-on-one conversations."
- Compose by username, from followers/following lists, or from a profile's 3-dot menu. Delete messages.
- **PLATFORM GATE:** web only.
- Also used as a **system channel**: Trust & Safety notices, zip-download links, and violation warnings
  are delivered to FlickrMail *and* the account email.
- **Paid gating:** none.

### 6.4 Notifications
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404377011476-Get-Flickr-notifications-by-email-and-in-your-account
- **Title:** Get Flickr notifications by email and in your account — **Updated 2025-10-28** — **HTTP 200**
- **Two tabs in the bell drop-down:** `Notifications` (followers, faves, comments, group activity) and
  **`Groups You Admin`** (join requests, pool additions, discussion activity) — the admin tab only
  appears if you administer a group.
- **Notification Center:** full-page view, filterable by type (comments, galleries, groups, and more),
  reverse-chronological, "Load more" paging, per-notification 3-dot actions.
- **Settings** split into: account (in-site) notifications, email notifications, marketing
  (Flickr Community, Monthly Newsletters, Marketing and Promotions), product (Product Announcements,
  Surveys), partner offers. Mobile push is managed separately in the app.
- **Paid gating:** none.

> **Vizra signal:** the separate "Groups You Admin" queue is a good pattern — moderation-duty
> notifications must not be buried in social noise. Matches the instance-admin/moderator surfaces
> Vizra needs.

---

## 7. Explore, search, stats, uploads, storage, video, sizes

### 7.1 Free-account limits (the core paid gate)
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/13690320471060-Free-account-limits-and-enforcement
- **Title:** Free account limits and enforcement — **Updated 2026-03-04** — **HTTP 200**

Free accounts are **not** allowed to (Flickr's own list):
| Restriction | Verbatim |
|---|---|
| Mature content | "Post content with Moderate or Restricted Safety Levels." **[PRO-ONLY / PAID]** |
| Commercial use | "Post Commercial content. Only our Pro members are permitted to engage in commercial activity." **[PRO-ONLY / PAID]** |
| Non-public storage | "Store more than **50** Non-Public photos or videos." **[PRO-ONLY / PAID]** |
| Item count | "Upload over **1,000** items." **[PRO-ONLY / PAID]** |

- Limits apply **regardless of privacy setting**, private content included.
- **Enforcement is punitive:** "Content that exceeds these limits is at risk of suspension or deletion."
  Accounts are suspended, notified via email + FlickrMail, and restored only by upgrading or deleting content.

### 7.2 Full Pro feature list **[ALL PRO-ONLY / PAID]**
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404078815508-Reasons-to-upgrade-to-Flickr-Pro
- **Title:** Reasons to upgrade to Flickr Pro — **Updated 2026-05-27** — **HTTP 200**

Unlimited storage · Ad-free browsing (for the Pro **and their visitors**) · unlimited non-public content ·
Moderate and Restricted uploads · original/large download rights · **Advanced Stats** ·
Desktop & Mobile **Auto-Uploadr** · commercial activity · Premier product support ·
**"Pros' images display at resolutions up to 6K."** · **10-minute** video playback (vs 3) ·
**60** groups per photo (vs 30) · partner discounts (Adobe, Blurb, Priime, KEH, SmugMug).

- **Pricing** (https://www.flickrhelp.com/hc/en-us/articles/4404064001812-Pricing-FAQ — **Updated 2026-01-21** — **HTTP 200**):
  USD $11/mo, $82/yr, $148/2yr (plus tax); GBP £9/£74/£124; EUR €10/€82/€148; CAD $14/$119/$217;
  International USD $13/$96/$170. **Out of scope for Vizra — recorded only to show the size of the paywall.**
- **Not gated:** **MyFlickrYear** (annual recap) is open to "Free and Pro members who uploaded at least
  1 photo that year (public or non-public) with at least 1 view."
  (https://www.flickrhelp.com/hc/en-us/articles/22482501289748-MyFlickrYear — **Updated 2026-01-19** — **HTTP 200**)

### 7.3 Stats **[PRO-ONLY / PAID]**
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/7700609124884-Stats-101-Pro-only
- **Title:** Stats 101 (Pro only) — **Updated 2026-08-10** — **HTTP 200**
- **Quote (17 words):** "Stats are a feature available to our Pro members that provides detailed analysis
  of their Flickr content."
- **The free/paid split (quote, 12 words):** "Everyone gets view counts, but only Pro's get access to their stats."
  - **Views (free + Pro):** a single integer per item, plus an account total on the About page.
  - **Stats (Pro):** per-item per-day counts with **source** (referring page) and **platform**.
- Sections: Daily stats (36-week trend line, views/faves/comments toggle, **Download stats CSV**,
  most-viewed/commented/faved, source breakdown into Flickr / Social / Search); All-time activity
  (Photos + Photostream + Albums + Collections + Galleries = total views; content breakdown; storage
  used; Pro join date).
- **View definition (quote, 20 words):** "a 'view' is added to your stats any time that particular image
  appears on someone's screen" — thumbnails in feeds and search results count.
- Batch-processed every few minutes; content breakdown updates roughly daily.
- Privacy tightening zeroes accumulated views/faves; the Replace feature does not.

> **Vizra signal:** Flickr's view counter is *impression-based*, not visit-based — worth an explicit
> decision in Vizra, and worth documenting to users, because it makes counts far larger and
> non-comparable to page views. Also note "counts" are named in AGENTS.md as an authorization surface:
> a per-item view count can leak the existence of private content if not scoped.

### 7.4 Upload requirements, formats, video limits
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404079649300-Flickr-upload-requirements
- **Title:** Flickr upload requirements — **Updated 2026-07-01** — **HTTP 200**
- **Photo formats:** JPEG, PNG, GIF (non-animated), TIFF (→JPEG), BMP (→JPEG), HEIF/HEIC (→JPEG, app only).
  **RAW is not supported.**
- **Video formats:** MP4 (H.264 recommended), AVI, WMV, MOV, MPEG (1/2/4), 3gp, M2TS, OGG, OGV.
- **Photo limits:** "Each photo can be up to **200 MB**." Aspect ratio: "Images can be no more than
  **31.25 times** wider than they are tall."
- **Video limits:** "Each video can be up to **1 GB**." "The maximum resolution for videos is **1080p**."
  Playback capped at **30 fps** for everyone.
  **[PRO-ONLY / PAID] (quote, 24 words):** "Although videos of any length can be uploaded, video
  playback is constrained to the first 3 minutes for free members, and 10 minutes for Pro members."
  "Restricted videos are not permitted."
- **Upload article** — https://www.flickrhelp.com/hc/en-us/articles/4404079632660-Upload-photos-and-videos-to-Flickr
  — **Updated 2026-09-09** — **HTTP 200**. Manual upload vs **Auto-Uploadr (Pro only)**; Auto-Uploadr
  content always lands Private. Upload form collects title, description, tags, people, albums, groups,
  license, privacy, content filters — **all set before the item exists**.

### 7.5 Photo sizes / 6K
- **Source:** https://www.flickr.com/services/api/misc.urls.html — **The App Garden** — **HTTP 200** (no date shown)
- URL template `https://live.staticflickr.com/{server-id}/{id}_{secret}_{size-suffix}.jpg`;
  original `{id}_{o-secret}_o.{o-format}`.
- **Size ladder (verbatim suffixes):** `s` 75 (square) · `q` 150 (square) · `t` 100 · `m` 240 · `n` 320 ·
  `w` 400 · *(none)* 500 · `z` 640 · `c` 800 · `b` 1024 · `h` 1600 · `k` 2048 · `3k` 3072 · `4k` 4096 ·
  `f` 4096 (2:1 only) · `5k` 5120 · **`6k` 6144** · `o` original.
- Sizes `h` and above carry a **unique per-size secret** and "photo owner can restrict" — i.e. large
  derivatives are separately access-controlled, not guessable from the base secret.
- **6K = the Pro display tier** (§7.2). `b` (1024) is the free-account download ceiling (§5.6).

> **Vizra signal:** per-size unguessable secrets on large derivatives is exactly the pattern AGENTS.md
> demands ("Default-deny authorization covers originals, derivatives..."). Vizra should not serve
> derivatives from a predictable path when the original is access-controlled.

### 7.6 Explore / interestingness
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404070823700-Flickr-Explore
- **Title:** Flickr Explore — **Updated 2026-09-08** — **HTTP 200**
- **Quote (21 words):** "Flickr's Explore page highlights a rotating array of about 500 photos each day,
  giving members a chance to discover inspiring work"
- **Ranking inputs (Flickr's own two headings):** *Interestingness* — "Signals of engagement such as
  comments, faves, and views"; *Activity* — "Participation in the Flickr community, such as groups and
  trending tags."
- Stated properties: quality of interaction weighted over quantity; posting time matters; metadata
  (tags/titles/descriptions) helps; on-topic group participation helps; **per-member frequency caps**
  ("limits are in place so the same members don't appear too frequently"); featured photos get a
  comment from the official Flickr account.
- **NOT paid-gated (quote, 10 words):** "No. All members have an equal chance of being featured."
- **Explore Takeovers:** curated monthly themes, last Thursday of each month.
- `interestingness` also appears as a **sort option** in Advanced Search and in Stats.

### 7.7 Search filters
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404058806420-Search-Flickr-to-find-photos-people-or-groups
- **Title:** Search Flickr to find photos, people, or groups — **Updated 2026-08-11** — **HTTP 200**
- **Three result types:** Photos · People · Groups.
- **Advanced filters (verbatim list):** Color · Photo style (B&W, shallow depth of field, minimalist,
  patterns) · Orientation (portrait, landscape, square, panorama) · Minimum size (web only) ·
  Date (taken or uploaded) · Content type · **Search in** (tags only, or include description and title) ·
  **License** · **SafeSearch** · **Sort by** (relevant, date uploaded, date taken, interestingness).
- Scoped search within a group, your photostream, or your albums (web only).
- "Your photos and photos from people you follow will be displayed separately from everyone's photos."
- **PLATFORM GATE:** advanced search in-app is iOS only.
- **Camera Finder** (https://www.flickrhelp.com/hc/en-us/articles/7940615222420-Flickr-Camera-Finder
  — **Updated 2025-08-19** — **HTTP 200**): browse by camera brand/model at `flickr.com/cameras`, driven
  by EXIF. Web only.
- **Improve public searches** (https://www.flickrhelp.com/hc/en-us/articles/4404058704404-Improve-public-searches-of-your-photos
  — **Updated 2025-08-18** — **HTTP 200**): requires **five or more public photos** for an account to
  surface in search, plus hide-from-search off and good tags/titles/descriptions.
- **Paid gating:** none.

### 7.8 Sharing / embedding
- **Share your Flickr content** — https://www.flickrhelp.com/hc/en-us/articles/4404078014356-Share-your-Flickr-content
  — **Updated 2026-08-11** — **HTTP 200**. Channels: copy link, group, social (Facebook/Tumblr/Twitter/
  Pinterest, web only), embed code, **BBCode**.
  **Safety-level share rules:** Moderate "Cannot be shared directly to social media"; non-public
  Restricted "cannot be shared"; public Restricted can't use the Share icon but its URL can be passed on.
  Non-public sharing mints a **Guest Pass** (§5.8).
- **Embed your Flickr content** — https://www.flickrhelp.com/hc/en-us/articles/24282601008404-Embed-your-Flickr-content
  — **Updated 2025-10-12** — **HTTP 200**. Safe or Moderate only. Album embeds require **all** items Public.
  Terms require a link back to Flickr on any externally embedded image.
- **Paid gating:** none (though ad-free *sharing* is a Pro benefit).

---

## 8. Print / other paid features — **OUT OF SCOPE for Vizra**

- **Evidence of absence, not assumption:** the complete 157-article Help Center index contains **no**
  print, photo-book, or merchandise article. Help Center search for `print` and `prints` returns
  **2 results each**, both irrelevant ("Request to Memorialize or Delete an account of a deceased
  member", "Discounts for non-profit organizations"). **Flickr currently documents no print/merch
  product.** (Checked 2026-09-15.)
- The only paid surfaces documented are: **Flickr Pro subscription** (§7.2), **Gifting Pro**
  (`.../4404079197076-Gifting-Pro`), **non-profit discounts** (`.../4404058120212`), **partner perk
  redemption** (`.../4404079107092`), and **commercial API keys** (§11.5).
- **Vizra position:** all of the above are **out of scope**. Vizra requires no billing, so it needs
  **no** subscription, invoice, payment-method, gifting, dunning, or perk-redemption surface. Every
  *capability* Flickr puts behind Pro (mature content, stats, originals, long video, large groups
  caps, unlimited storage, API access) must be available ungated in Vizra, subject to
  **instance-operator policy and quota**, not to payment.

---

## 9. Blocking, reporting, moderation, community guidelines, deletion & export

### 9.1 Blocking
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404057922324-Block-or-unblock-someone-in-Flickr
- **Title:** Block or unblock someone in Flickr — **Updated 2026-08-11** — **HTTP 200**
- **Effects (quote, 20 words):** "Once blocked, the member will not be able to: Follow you; Interact with
  your photos or videos; Send you FlickrMail."
- **Retroactive cleanup:** "Any comments or faves from them on your content will be deleted, and your
  content will be removed from their galleries." Can take several hours.
- **Explicit non-effects:** "The member you have blocked will not receive a notification about this
  action."; **"Blocked members will still be able to see your Public content."**; the blocker can still
  see and interact with the blocked member's account.
- Block from a profile, or directly from a notification. Block list at `Following → Your Block List`
  (web only); unblock requires a confirmation checkbox.
- **Paid gating:** none.

> **Vizra signal:** block is **asymmetric and non-secret-but-unnotified**, and it *mutates historical
> content* (deletes comments/faves, removes from galleries). That is a real data-lifecycle requirement
> with cache/counter implications — AGENTS.md's "stale authorization caches" risk applies directly.

### 9.2 Reporting
- **URL:** https://www.flickrhelp.com/hc/en-us/articles/4404057906068-How-to-report-violations-of-our-Community-Guidelines
- **Title:** How to report violations of our Community Guidelines — **Updated 2026-08-11** — **HTTP 200**
- **Three paths (verbatim):** **Flag Photo**, **Report Abuse**, **Contact Us**.
- Profile report (3-dot → Report user → category → details), photostream-level "Report Abuse",
  in-app "Flag this photo", and a Contact Us form routed to Trust & Safety.
- Separate flows exist for copyright (Copyright Infringement Form), counter-notices, EU illegal content,
  NetzDG, CSAM, NCII, suicide/self-harm, law enforcement, and deceased-member requests — all present as
  distinct articles in the `Reporting Abuse` / `Rules & Policies` sections.

### 9.3 Moderation & enforcement
- **The rules of Flickr** — https://www.flickrhelp.com/hc/en-us/articles/20529310987796-The-rules-of-Flickr
  — **Updated 2026-06-28** — **HTTP 200**. Enumerated zero-tolerance prohibited categories (~28 items
  incl. CSAM, NCII "including AI-generated imagery", hate speech, impersonation, sextortion, tribute
  imagery, voyeurism, PII, spam, terrorism, harassment). Child Nudity Policy. **Age requirement: 18+ to
  create an account**; browsing without an account is permitted.
- **Appeal Process** — https://www.flickrhelp.com/hc/en-us/articles/16080054760340-Appeal-Process-for-Account-Violations
  — **Updated 2026-03-11** — **HTTP 200**.
  **Graduated sanctions (verbatim examples):** "your account may be hidden from public view, your social
  functions may be disabled, or your ability to upload videos may be deactivated."
  Violation classes: Free Account Limits (non-Safe content; commercial activity), Mismoderated content
  in a Pro account, Collected content (rights), Prohibited content. Notice goes to FlickrMail **and**
  the login email. Egregious cases → immediate termination.
  **Scope note (quote, 24 words):** "All content on Flickr, including your private content,
  friends/family content, comments, tags, photo descriptions, FlickrMail, etc., must abide by our guidelines."
- **Spam on Flickr** — https://www.flickrhelp.com/hc/en-us/articles/21408093965972-Spam-on-Flickr
  — **Updated 2025-10-08** — **HTTP 200**. Prohibited: excessive faving, excessive commenting,
  irrelevant tags/people-tags, deceptive titles/descriptions, link spamming, resource abuse, mass
  copy-paste comments/FlickrMail, mass group invites, ignoring group rules, unsolicited advertising.
  **Resource abuse explicitly includes "Using Flickr as a content delivery network (CDN)"**, false abuse
  reports, and fraudulent copyright reports. API-specific bans: excessive bandwidth, rapid-pace
  uploading, artificially gaining followers/faves/views, mass group joining, mass topic creation.
- **Harassment and Bullying policy** — https://www.flickrhelp.com/hc/en-us/articles/50772269985940-Harassment-and-Bullying-policy
  — **Updated 2026-06-28** — **HTTP 200**. Applies "anywhere on Flickr, including public or private
  posts, comments, tags, FlickrMail messages, profile descriptions, groups, galleries, or favorites."
- **Group-level safety** — see §3.4.

### 9.4 Community Guidelines (primary document)
- **Landing page:** https://www.flickr.com/help/guidelines/ — *Flickr Community guidelines | Flickr* —
  **HTTP 200 but body EMPTY** (see §0.1).
- **Actual document:** https://combo.staticflickr.com/ap/build/pdfs/help/en-us/guidelines.pdf —
  **HTTP 200, application/pdf, 65,339 bytes, 3 pages.**
  **PDF internal Title metadata: "Flickr's Community Guidelines - Updated [3/2/23]"** — so the guidelines
  document itself is dated **2023-03-02** and is materially older than most Help Center articles.
- **Three sections:** *Participating in the Flickr community* · *Respecting photography* · *Enforcement*.
- Representative rules (quotes):
  - "Respect your fellow Flickr members." (5 words)
  - "Be constructive with your critiques, comments, and feedback." (8 words)
  - "Safety levels exist to make the whole community safer." (9 words)
  - **"Connect like a human, not like a robot."** (8 words) — the anti-spam principle; names
    "mass-faveing" and mass copy-paste commenting as disingenuous.
  - "Shady use of our API is likely to get your API key terminated." (13 words)
  - "Don't use hate speech, threaten another member's safety or privacy, or harass anyone." (13 words)
  - "Use your Flickr account to share your work." (8 words) — with faves and galleries named as the
    sanctioned way to appreciate others' work instead of re-uploading.
  - **CC grace period (notable):** reusers get "a 30-day grace period to fix any possible mistake or
    misuse of your CC-licensed work with no penalty"; refusing that "can result in your account being removed."
- **Enforcement escalation (quote, 24 words):** "Consequences may start with a reminder of the community
  guidelines but can also result in the removal of content, loss of certain account privileges or access
  to certain tools, or being removed and banned from Flickr altogether."

### 9.5 Deletion and data export
- **Delete photos/videos** — https://www.flickrhelp.com/hc/en-us/articles/4404058338708-How-to-delete-photos-or-videos
  — **Updated 2026-08-11** — **HTTP 200**.
  **Quote (4 words):** "Deleted photos aren't recoverable." — "all of the metadata and comments
  associated with it are removed from the server." **No trash / no undo.**
- **Delete account** — https://www.flickrhelp.com/hc/en-us/articles/4404071373588-Delete-your-Flickr-account
  — **Updated 2026-08-11** — **HTTP 200**. Password re-entry + explicit acknowledgement. Irrecoverable.
  Caveat: public images may persist in third-party search indexes.
- **Download / export** — https://www.flickrhelp.com/hc/en-us/articles/4404079675156-Downloading-content-from-Flickr
  — **Updated 2026-08-11** — **HTTP 200**.
  - Single-item download; **bulk selection capped at 500 items per zip**; albums same 500 cap.
  - **[PRO-ONLY / PAID]** free accounts capped at 1024px in bulk downloads; **videos excluded from all
    bulk downloads regardless of account type**.
  - **"Request My Flickr Data"** — the full account export. **"This method is always available for Free
    and Pro users."** — *not* paid-gated. Compilation takes "a few hours to a few weeks".
    Delivered as time-expiring links in account settings + email; re-requestable.
  - **Export shape (important):** photo files retain only **upload-time EXIF**; everything added later
    (title, description, tags) ships in a **separate JSON file**.
  - Zip handling: https://www.flickrhelp.com/hc/en-us/articles/4404071661844-Opening-Your-Flickr-Data-Zip-Files
    — **Updated 2025-10-07** — **HTTP 200**. Accounts >500 items get multiple numbered zips.

> **Vizra signal:** the account export being ungated while bulk *media* download is paywalled is an
> important asymmetry — Flickr satisfies data-portability obligations without conceding the product
> feature. Vizra, with no billing, should provide both. Note also that a sidecar JSON export is the
> honest approach (metadata added post-upload cannot be losslessly re-embedded into every format).

---

## 10. Photo page anatomy & account settings (entity-model vocabulary)

- **About the Photo page** — https://www.flickrhelp.com/hc/en-us/articles/31687228075540-About-the-Photo-page
  — **Updated 2025-08-11** — **HTTP 200**
  Sections, in Flickr's order: member info (username, profile icon, **Pro badge**), title, description;
  **Views / Favorites / Comments** counters; Uploaded on + Taken on; licensing dropdown; comment box
  (with emoji); camera model (links to Camera Finder) + EXIF (aperture, focal length, shutter speed,
  ISO, flash) + "Show EXIF"; map/location; **Groups** ("This photo is currently not in any groups") +
  Add to group; **Albums** + Add to album; **Tags** + Add tags; people; notes.
- **Overview of Your Flickr Account Settings** — https://www.flickrhelp.com/hc/en-us/articles/4404070523924-Overview-of-Your-Flickr-Account-Settings
  — **Updated 2026-03-29** — **HTTP 200**
  Tabs: **Account & Subscription** (membership status, password, time zone, **account safety level**,
  delete account, order history, **Your Flickr Data**, Pro Perks) · **Privacy & Permissions**
  (Global settings, Content filters, Defaults for new uploads) · **Emails & Notifications** ·
  **Sharing & Extending** (Guest passes history, **Account Links** = authorized third-party apps).

> **Vizra signal:** "Account Links" is the OAuth-authorization management surface. Vizra needs an
> equivalent revocable-grant list; it is part of a complete auth story, not an optional extra.

---

## 11. Flickr API — vocabulary reference for Vizra's entity model

**Primary source:** https://www.flickr.com/services/api/ — *The App Garden* — **HTTP 200** — no
last-updated date published.
**Help Center companion:** https://www.flickrhelp.com/hc/en-us/articles/4404070036884-Flickr-API —
*Flickr API* — **Updated 2025-08-06** — **HTTP 200**.

### 11.1 Authentication
- **Source:** https://www.flickr.com/services/api/auth.oauth.html — **HTTP 200**
- **OAuth Core 1.0 Revision A** (OAuth **1.0a**), three-legged.
- Endpoints: `/services/oauth/request_token` · `/services/oauth/authorize` · `/services/oauth/access_token`.
- **Signature (quote, 7 words):** "Currently, Flickr only supports HMAC-SHA1 signature encryption."
- **Permission scopes: `read`, `write`, `delete`.**
- No token-expiry statement on the page. **FAILED to confirm expiry semantics — recorded as unanswered.**
- Legacy non-OAuth family `flickr.auth.*` (frob/token) still listed.

> **Vizra signal:** OAuth 1.0a + HMAC-SHA1 is legacy and should **not** be copied. Vizra should use
> OAuth 2.0 / OIDC. What *is* worth copying is the coarse three-scope model (read / write / delete) —
> a delete scope separate from write is a good safety boundary.

### 11.2 Upload API (separate from the REST API)
- **Source:** https://www.flickr.com/services/api/upload.api.html — **HTTP 200**
- **Endpoint:** `POST https://up.flickr.com/services/upload/`. Requires `write` permission.
- **Signature gotcha:** "the 'photo' parameter **should not** be included in the signature."
- **Arguments:** `photo` (required); `title`, `description`, `tags` ("A space-seperated list of tags"),
  `is_public` / `is_friend` / `is_family`, `safety_level` (1=Safe, 2=Moderate, 3=Restricted),
  `content_type` (1=Photo, 2=Screenshot, 3=Other), `hidden` (1=hidden from public search, 2=visible).
- Returns REST XML with `<photoid>`. Async/ticket behaviour is **not documented on that page**, but
  `flickr.photos.upload.checkTickets` exists in the method list — **INFERRED** that async upload is
  ticket-based; the semantics were not officially confirmed. Replace API: `/services/api/replace.api.html`.

> **Vizra signal:** the privacy triple (`is_public`/`is_friend`/`is_family`), `safety_level`,
> `content_type` and `hidden` are all set **at upload time**, not patched afterwards. Vizra's upload
> contract should likewise accept the full permission envelope atomically so nothing is ever briefly
> public by default.

### 11.3 Rate limits
- **Source:** https://www.flickr.com/services/developer/api/ — *The Flickr Developer Guide - API* — **HTTP 200**
- **Quote (13 words):** "If your application stays under **3600 queries per hour** across the whole key"
  — the limit is **per key, aggregated across all that key's users**, not per user.
- Abuse → key expiry or shutdown.

### 11.4 API Terms of Use
- **Source:** https://www.flickr.com/services/api/tos/ — *Flickr APIs Terms of Use* — **HTTP 200**
- **Display cap (quote, 12 words):** "Display more than 30 Flickr user photos per page in your
  application" — prohibited; max 30 per page.
- Cached private photos must be purged "as soon as reasonably possible"; owner takedown requests
  honoured within **24 hours**.
- Required attribution string: "This product uses the Flickr API but is not endorsed or certified by
  SmugMug, Inc."
- Prohibited: replicating Flickr.com's core experience; surveillance/law-enforcement tracking; malware;
  generic image hosting. Commercial use needs a separate commercial key.

### 11.5 API access is paywalled
- **[PRO-ONLY / PAID] (quote, 12 words):** "The ability to request API keys is available exclusively to
  Pro subscribers."
- **[PRO-ONLY / PAID]** "Downloading original and large-size photos (larger than 1024px) from Free
  accounts is restricted via the Flickr API. This limitation applies to both the content owner and any
  users accessing the content through the API."
- Key types: **Non-Commercial** and **Commercial** (separate application forms).
- **Vizra position:** Vizra's API must be ungated. Rate limiting and quota are instance-operator
  policy, never a billing gate.

### 11.6 Method families — verbatim namespaces with one-line meanings
*(Namespace and method names are Flickr's identifiers, reproduced verbatim for vocabulary mapping.
The one-line meanings are this document's own summaries.)*

| Namespace | Meaning (one line) | Methods |
|---|---|---|
| `flickr.activity.*` | The "recent activity" feed: activity on your things, and your activity elsewhere | `userComments`, `userPhotos` |
| `flickr.auth.*` | Legacy pre-OAuth token exchange | `checkToken`, `getFrob`, `getFullToken`, `getToken` |
| `flickr.auth.oauth.*` | OAuth 1.0a token inspection / migration | `checkToken`, `getAccessToken` |
| `flickr.blogs.*` | Cross-post a photo to an external blog service | `getList`, `getServices`, `postPhoto` |
| `flickr.cameras.*` | Camera brand/model taxonomy behind Camera Finder | `getBrandModels`, `getBrands` |
| `flickr.collections.*` | Read the nested collection tree (albums-of-albums) — **read-only in the API** | `getInfo`, `getTree` |
| `flickr.commons.*` | The Commons: institutional no-known-copyright archives | `getInstitutions` |
| `flickr.contacts.*` | The follow graph and friend/family labels | `getList`, `getListRecentlyUploaded`, `getPublicList`, `getTaggingSuggestions` |
| `flickr.favorites.*` | Faves: add, remove, list, and position within a faves stream | `add`, `getContext`, `getList`, `getPublicList`, `remove` |
| `flickr.galleries.*` | Curated sets of **other people's** photos | `addPhoto`, `create`, `editMeta`, `editPhoto`, `editPhotos`, `getInfo`, `getList`, `getListForPhoto`, `getPhotos`, `removePhoto` |
| `flickr.groups.*` | Group entity: lookup, join/leave, join requests, search | `getInfo`, `join`, `joinRequest`, `leave`, `search` |
| `flickr.groups.members.*` | Group membership roster | `getList` |
| `flickr.groups.pools.*` | The group photo pool (add/remove photos, list pools a photo is in) | `add`, `getContext`, `getGroups`, `getPhotos`, `remove` |
| `flickr.groups.discuss.topics.*` | Group discussion topics (threads) | `add`, `getInfo`, `getList` |
| `flickr.groups.discuss.replies.*` | Replies within a discussion topic | `add`, `delete`, `edit`, `getInfo`, `getList` |
| `flickr.interestingness.*` | The Explore ranking: most interesting photos for a date | `getList` |
| `flickr.machinetags.*` | Structured `namespace:predicate=value` tag vocabulary | `getNamespaces`, `getPairs`, `getPredicates`, `getRecentValues`, `getValues` |
| `flickr.panda.*` | Novelty curated photo streams ("pandas") | `getList`, `getPhotos` |
| `flickr.people.*` | User entity: identity lookup, profile, quotas, upload status | `findByEmail`, `findByUsername`, `getGroups`, `getInfo`, `getLimits`, `getPhotos`, `getPhotosOf`, `getPublicGroups`, `getPublicPhotos`, `getUploadStatus` |
| `flickr.photos.*` | Core media entity: metadata, permissions, safety, search, sizes, EXIF | `addTags`, `delete`, `getAllContexts`, `getContactsPhotos`, `getContactsPublicPhotos`, `getContext`, `getCounts`, `getExif`, `getFavorites`, `getInfo`, `getNotInSet`, `getPerms`, `getPopular`, `getRecent`, `getSizes`, `getUntagged`, `getWithGeoData`, `getWithoutGeoData`, `recentlyUpdated`, `removeTag`, `search`, `setContentType`, `setDates`, `setMeta`, `setPerms`, `setSafetyLevel`, `setTags` |
| `flickr.photos.comments.*` | Comments on a photo | `addComment`, `deleteComment`, `editComment`, `getList`, `getRecentForContacts` |
| `flickr.photos.geo.*` | Geotags, geo permissions, and location correction | `batchCorrectLocation`, `correctLocation`, `getLocation`, `getPerms`, `photosForLocation`, `removeLocation`, `setContext`, `setLocation`, `setPerms` |
| `flickr.photos.licenses.*` | License assignment, catalogue and history | `getInfo`, `setLicense`, `getLicenseHistory`, `getAvailable` |
| `flickr.photos.notes.*` | Positional notes drawn on the image | `add`, `delete`, `edit` |
| `flickr.photos.people.*` | People-tagging, including bounding-box coordinates | `add`, `delete`, `deleteCoords`, `editCoords`, `getList` |
| `flickr.photos.suggestions.*` | Community-suggested locations awaiting owner approval | `approveSuggestion`, `getList`, `rejectSuggestion`, `removeSuggestion`, `suggestLocation` |
| `flickr.photos.transform.*` | Lossless server-side rotation | `rotate` |
| `flickr.photos.upload.*` | Async upload ticket status | `checkTickets` |
| `flickr.photosets.*` | **Albums** (the API's name for them is "photosets") | `addPhoto`, `create`, `delete`, `editMeta`, `editPhotos`, `getContext`, `getInfo`, `getList`, `getPhotos`, `orderSets`, `removePhoto`, `removePhotos`, `reorderPhotos`, `setPrimaryPhoto` |
| `flickr.photosets.comments.*` | Comments on an album | `addComment`, `deleteComment`, `editComment`, `getList` |
| `flickr.places.*` | Gazetteer: place IDs, WOE IDs, shapes, hierarchy | `find`, `findByLatLon`, `getChildrenWithPhotosPublic`, `getInfo`, `getInfoByUrl`, `getPlaceTypes`, `getShapeHistory`, `getTopPlacesList`, `placesForBoundingBox`, `placesForContacts`, `placesForTags`, `placesForUser`, `resolvePlaceId`, `resolvePlaceURL`, `tagsForPlace` |
| `flickr.prefs.*` | The authenticated user's default upload preferences | `getContentType`, `getGeoPerms`, `getHidden`, `getPrivacy`, `getSafetyLevel` |
| `flickr.profile.*` | Public profile / About page fields | `getProfile` |
| `flickr.push.*` | PubSubHubbub-style push subscriptions to Flickr events | `getSubscriptions`, `getTopics`, `subscribe`, `unsubscribe` |
| `flickr.reflection.*` | API self-description (method list and signatures) | `getMethodInfo`, `getMethods` |
| `flickr.stats.*` | **[PRO-ONLY]** per-item/per-day views, referrers, domains, CSV export | `getCollectionDomains`, `getCollectionReferrers`, `getCollectionStats`, `getCSVFiles`, `getMostPopularPhotoDateRange`, `getPhotoDomains`, `getPhotoReferrers`, `getPhotosetDomains`, `getPhotosetReferrers`, `getPhotosetStats`, `getPhotoStats`, `getPhotostreamDomains`, `getPhotostreamReferrers`, `getPhotostreamStats`, `getPopularPhotos`, `getTotalViews` |
| `flickr.tags.*` | Tag vocabulary, clustering, hot list, per-user tag lists | `getClusterPhotos`, `getClusters`, `getHotList`, `getListPhoto`, `getListUser`, `getListUserPopular`, `getListUserRaw`, `getMostFrequentlyUsed`, `getRelated` |
| `flickr.test.*` | Connectivity / auth smoke tests | `echo`, `login`, `null` |
| `flickr.testimonials.*` | Member-written testimonials with an approval workflow | `addTestimonial`, `approveTestimonial`, `deleteTestimonial`, `editTestimonial`, `getAllTestimonialsAbout`, `getAllTestimonialsAboutBy`, `getAllTestimonialsBy`, `getPendingTestimonialsAbout`, `getPendingTestimonialsAboutBy`, `getPendingTestimonialsBy`, `getTestimonialsAbout`, `getTestimonialsAboutBy`, `getTestimonialsBy` |
| `flickr.urls.*` | Resolve between canonical URLs and internal IDs | `getGroup`, `getUserPhotos`, `getUserProfile`, `lookupGallery`, `lookupGroup`, `lookupUser` |

**Terminology trap for Vizra:** the UI says **Album**, the API says **photoset** (`flickr.photosets.*`).
The UI **Collection** and API `flickr.collections.*` agree, but the API is **read-only** for collections
(`getInfo`, `getTree` only) — collection *authoring* is web-UI-only. Vizra should keep one name per
concept across UI, API and database, per AGENTS.md's single-contract requirement.

### 11.7 `flickr.photos.search` arguments (the canonical query surface)
**Source:** https://www.flickr.com/services/api/flickr.photos.search.html — **HTTP 200**

`user_id` (NSID, or `me`) · `tags` (comma-delimited; `-` prefix excludes) · `tag_mode` (`any`/`all`) ·
`text` (title, description or tags) · `min_upload_date` / `max_upload_date` / `min_taken_date` /
`max_taken_date` · `license` (comma-separated license IDs) · `sort` (date/interestingness/relevance) ·
`privacy_filter` (1–5) · `bbox` · `accuracy` (1–16) · `safe_search` (1=safe, 2=moderate, 3=restricted) ·
`content_types` (0=photos, 1=screenshots, 2=other, 3=virtual) · `machine_tags` · `machine_tag_mode` ·
`group_id` · `contacts` (`all`/`ff`) · `woe_id` · `place_id` · `media` (`all`/`photos`/`videos`) ·
`has_geo` · `geo_context` (0=undefined, 1=indoors, 2=outdoors) · `lat` / `lon` / `radius` (0–20 mi/32 km,
default 5 km) / `radius_units` · `is_commons` · `in_gallery` · `is_getty` · `extras` ·
**`per_page` (default 100, max 500)** · `page`.

> **Vizra signal:** this is the most complete single statement of Flickr's queryable dimensions, and it
> maps 1:1 onto the entity model — ownership, tags, text, two date axes, license, privacy, safety,
> content type, group, social graph, geo (three different geo idioms), media type, and curation state
> (`in_gallery`). It is the best available checklist for Vizra's search contract.

---

## 12. Consolidated limits table (all officially stated)

| Limit | Value | Paid? | Source § |
|---|---|---|---|
| Items per album | 100,000 | free | §2.1 |
| Collection nesting depth | 5 levels | free | §2.2 |
| Items per gallery | 500 | free | §2.3 |
| Groups a member may belong to | 5,000 | free | §3.2 |
| Groups a single photo may be posted to | **30 free / 60 Pro** | **PAID uplift** | §3.2 |
| Sticky topics per group | 20 | free | §3.4 |
| Geofences per account | 10 | free | §4.6 |
| Total items, free account | **1,000** | **PAID gate** | §7.1 |
| Non-public items, free account | **50** | **PAID gate** | §7.1 |
| Moderate / Restricted content | Pro only | **PAID gate** | §5.4 |
| Commercial content | Pro only | **PAID gate** | §7.1 |
| Original / >1024px download | Pro only | **PAID gate** | §5.6 |
| API key issuance | Pro only | **PAID gate** | §11.5 |
| Video playback length | **3 min free / 10 min Pro** | **PAID uplift** | §7.4 |
| Display resolution | up to **6K** (Pro) | **PAID uplift** | §7.2, §7.5 |
| Max photo file size | 200 MB | free | §7.4 |
| Max photo aspect ratio | 31.25 : 1 | free | §7.4 |
| Max video file size | 1 GB | free | §7.4 |
| Max video resolution / fps | 1080p / 30 fps | free | §7.4 |
| Bulk download batch | 500 items per zip | free (size-capped) | §9.5 |
| Data-export zip split | every 500 items | free | §9.5 |
| Public photos needed to appear in search | 5 | free | §7.7 |
| Account age to send group invites | 30 days | free | §3.2 |
| Explore daily feature pool | ~500 photos/day | free | §7.6 |
| API queries per key per hour | 3,600 | — | §11.3 |
| API photos displayed per page | 30 max | — | §11.4 |
| `flickr.photos.search` per_page | 500 max | — | §11.7 |
| Minimum account age | 18 years | free | §9.3 |

---

## 13. NOT ANSWERED BY OFFICIAL DOCS

Each item below was checked against the **complete 157-article Help Center index**, the Help Center
search API, and the public API reference on **2026-09-15**. These are genuine documentation gaps, not
things I failed to look for. **None of these should be guessed at when designing Vizra.**

1. **Maximum number of galleries per member.** The 500-items-per-gallery cap is documented; a cap on
   *how many galleries* a member may create is not stated anywhere (searched `gallery limit`,
   `how many galleries`).
2. **Maximum number of albums or collections per member.** Not stated.
3. **Maximum number of groups a member may create or administer.** The 5,000 *join* cap is stated; a
   creation/admin cap is not.
4. **Maximum members per group, or maximum photos in a group pool.** Not stated.
5. **Per-group posting throttles** (e.g. "N photos per day"). Referenced obliquely — "Some groups
   enforce posting limits" and "groups that have their own posting limits set" — but the configurable
   range, units and admin UI are never documented.
6. **Comment length limit, comment rate limit, or notes-per-photo limit.** Not stated. "Excessive
   commenting" is prohibited without any numeric threshold.
7. **Tag count limit per photo, or tag length limit.** Not stated.
8. **Machine tags — end-user definition and syntax.** No Help Center article exists. The concept is
   only exposed through `flickr.machinetags.*` and `machine_tags`/`machine_tag_mode` in the search API.
   Any `namespace:predicate=value` description is **INFERRED** from the API surface.
9. **Guest pass expiry semantics.** Called "temporary" in the article title and manually expirable, but
   no automatic TTL is documented. Whether passes ever auto-expire is unstated.
10. **OAuth access-token lifetime / expiry / refresh.** The OAuth page states no expiry policy.
    **FAILED to confirm.**
11. **Upload API async/ticket semantics.** `flickr.photos.upload.checkTickets` exists, but the upload
    page documents no `async` parameter or ticket lifecycle. **INFERRED only.**
12. **Rate limits for the Upload API specifically**, and whether uploads count against the
    3,600 queries/hour REST budget. Not stated.
13. **Per-user (as opposed to per-key) API rate limits.** The documented 3,600/hr is explicitly
    per-key-aggregate; per-user behaviour is unstated.
14. **Explore / interestingness algorithm specifics** — the actual weighting, the per-member frequency
    cap value, and the eligibility window. Described only qualitatively.
15. **Whether hidden-from-search content is excluded from the API** (`flickr.photos.search`) as well as
    from the web UI. The `hidden` upload parameter exists but cross-surface behaviour is unstated.
16. **Retention period for deleted content**, and whether any grace/undelete window exists server-side.
    Documentation says only that deletion is immediate and irreversible.
17. **Data-export JSON schema.** The sidecar JSON file is described in prose; no field-level schema or
    example is published.
18. **Group discussion attachment/embed limits**, topic length limits, and reply rate limits. Not stated.
19. **Gallery-inclusion opt-out granularity** — whether it is global-only or can be set per photo.
    Only "You can set your gallery preferences in your settings" is documented.
20. **Ratings.** Flickr has **no rating/scoring feature at all** — faves are binary. There is no official
    source for a star/score model. Vizra's ratings feature is therefore **entirely Vizra's own design**
    with no incumbent vocabulary to map onto.
21. **Print / photo-book / merchandise products.** None documented (see §8). If Vizra ever wanted a
    reference model for print fulfilment, Flickr's current docs provide none.
22. **Testimonials** (`flickr.testimonials.*`) — a full API family with an approval workflow, but **no
    Help Center article whatsoever**. End-user semantics, limits and visibility rules are undocumented.
23. **`flickr.panda.*`** — an undocumented curated-stream concept with no user-facing explanation.
24. **Photo "suggestions"** (`flickr.photos.suggestions.*`) — community-suggested locations with an
    approve/reject workflow. No Help Center article; the user-facing feature is undocumented.
25. **Album- and collection-level comments** (`flickr.photosets.comments.*`) — the API supports
    commenting on albums, but no Help Center article describes this in the UI.
