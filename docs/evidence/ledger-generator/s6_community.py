from core import *

# ---------------------------------------------------------------- F4 community
req("VZ-COMMENT-001","Native threaded comments with edit, delete, report, sanitization, pagination and owner controls",
    "Member: comments on photos (and albums) with one-level replies; edits/deletes own; owner deletes on own content; report to moderators; formatting limited to a small allow-list; owner setting who may comment (nobody/followers/members/anyone); notifications.",
    "community", EXPLICIT, [{"source":"CHARTER","note":"native comments explicit even though Chevereto uses Disqus/JS"},{"source":"FLICKR-COMMENTS","note":"allowed tags b i u del blockquote; owner privacy controls"},{"source":"CHEV-EXTERNAL-SERVICES","note":"Comments API: Disqus or JavaScript/HTML — no native engine"}],
    deps=["VZ-AUTH-001","VZ-VIEWER-001","VZ-NOTIFY-001"], success=["Comment persists; reply thread; edit shows edited timestamp; pagination"], negative=["Retry of POST with same idempotency key creates one comment","XSS payload sanitized (test vectors)","Commenting disabled → 403 and control hidden"], privacy=["Comments on private items visible only to those who may see the item"], recovery=["Deleted item deletes/hides comments consistently"], api=["/api/v1/photos/{id}/comments*"], ui=["viewer comments"], evidence=EV_API+EV_UI+EV_NEG,
    mechanism="Chevereto offers Disqus or arbitrary comment HTML. Vizra ships a native engine; an optional external-provider embed is a separate, sandboxed question (Q-011).")
req("VZ-RATING-001","Numeric ratings (1–5) with one current vote per user, change/removal, accurate aggregate and concurrency safety",
    "Member: rates a photo 1–5; can change or remove; aggregate (average, count, distribution) correct under concurrent updates; owner may disable ratings site-wide or per item; ratings visually distinct from favorites.",
    "community", EXPLICIT, [{"source":"CHARTER","note":"numeric ratings explicit"},{"source":"FLICKR-NOTANSWERED","note":"Flickr has no ratings; Vizra's own design"},{"source":"DESIGN-BRIEF","note":"favorites and ratings distinguishable"}],
    deps=["VZ-AUTH-001","VZ-VIEWER-001"], success=["Aggregate matches after 100 concurrent votes; refresh shows own vote"], negative=["Out-of-range rejected; self-rating policy enforced; anonymous 401"], privacy=["Rating a private item requires view access; aggregates of private items hidden"], api=["PUT/DELETE /api/v1/photos/{id}/rating","GET aggregate"], ui=["viewer rating control"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-FAVORITE-001","Favorites: one durable favorite per user per item/album, personal favorites listing, public count, creator notification",
    "Member: favorites a photo or album (heart, keyboard L); repeated/retried requests keep one row; own favorites listing at /{username}/favorites; public 'favorited by' count/list where the item is public; owner notified; Explore signal.",
    "community", EXPLICIT, [{"source":"CHARTER","note":"favorites"},{"source":"CHEV-USER-LIKED","note":"liked listing; L shortcut"},{"source":"FLICKR-FAVES","note":"Faves tab; creator notified"}],
    deps=["VZ-AUTH-001","VZ-VIEWER-001"], success=["Add/remove idempotent; second tab reflects state; listing correct"], negative=["Favoriting an inaccessible item denied without revealing details"], privacy=["Tightening privacy removes it from others' favorites views and counts"], api=["PUT/DELETE /api/v1/photos/{id}/favorite","GET /api/v1/users/{u}/favorites"], ui=["favorite control","/u/{username}/favorites"], evidence=EV_API+EV_UI+EV_NEG, decided=["Q-018"],
    mechanism="Chevereto 'likes' and Flickr 'faves' are both binary. Proposed decision: Vizra unifies likes and favorites into one action named Favorite (no separate public like).")
req("VZ-FOLLOW-001","Follow/unfollow, followers and following lists, following feed",
    "Member: follows users; lists at /{username}/followers and /following; a following feed sorted by recency; counts live; approval is VZ-FOLLOW-002 (full).",
    "community", CHEV, [{"source":"CHEV-COMPARE","note":"Followers (Lite/Pro)"},{"source":"CHEV-USER-FOLLOWING","note":"following feed sorted by most recent"},{"source":"FLICKR-CONTACTS","note":"asymmetric follow + friend/family labels"}], edition="Lite",
    deps=["VZ-AUTH-001","VZ-ACCOUNT-001"], success=["Follow idempotent; feed shows only visible items"], negative=["Blocked user cannot follow"], privacy=["Feed respects per-item visibility"], api=["PUT/DELETE /api/v1/users/{u}/follow"], ui=["profile follow button","/feed"], evidence=EV_API+EV_UI+EV_NEG, decided=["Q-040"])
req("VZ-FOLLOW-002","Follow requests with approval and re-evaluation on profile privacy change",
    "Member: on a private profile a follow becomes a request; the owner approves or denies it from a pending list; approved followers may see follower-only items; the requester sees their own pending state and nobody else's; flipping a profile to private re-evaluates existing local and remote followers.",
    "community", SAFE, [{"source":"CHEV-USERS-SETTINGS","note":"private profile setting"},{"source":"FLICKR-CONTACTS","note":"asymmetric follow; Flickr has no approval step"},{"source":"FLICKR-PRIVACY","note":"follower/friend audiences presuppose an approved relationship"}],
    deps=["VZ-FOLLOW-001","VZ-ACCOUNT-001"],
    success=["Private profile → follow becomes a request; approve/deny UI; pending state visible to requester only"],
    negative=["Stranger self-follows a private profile → still denied follower-only items"],
    privacy=["Flipping a profile to private re-evaluates existing local and remote (ActivityPub Follow/Accept/Reject/Undo) followers"],
    recovery=["Re-evaluation job is idempotent"],
    api=["PUT/DELETE /api/v1/users/{u}/follow","GET /api/v1/me/follow-requests","POST /api/v1/me/follow-requests/{id}/approve|deny"],
    ui=["profile follow button pending state","/settings/follow-requests"],
    evidence=EV_API+EV_UI+EV_NEG, profiles=("full",), decided=["Q-040"])
req("VZ-FEED-001","Activity feed of people and groups you follow with filters and hide controls",
    "Member: home feed of uploads, comments, favorites from followed people and groups; filters (all/people/groups/audiences); hide a person/group from feed; cold start shows recommended public content.",
    "community", FLICKR, [{"source":"FLICKR-ACTIVITY-FEED","note":"filters; layouts; hide"}],
    deps=["VZ-FOLLOW-001"], success=["Feed items link to sources; hidden sources excluded"], privacy=["No private items from unfollowed audiences"], api=["GET /api/v1/me/feed"], ui=["/home"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-NOTIFY-001","In-app notifications with badge, panel, mark-as-read, history and per-type/email preferences",
    "Member: notified on favorite, follow, comment/reply, mention, moderation outcome, group activity; unread badge; panel marks read; full notification center with paging; email per type; moderation-duty notifications separated for admins/group admins.",
    "community", CHEV, [{"source":"CHEV-USER-NOTIFICATIONS","note":"likes, follows, comments; badge"},{"source":"FLICKR-NOTIFICATIONS","note":"Groups You Admin tab; notification center"}], edition="all",
    deps=["VZ-AUTH-001","VZ-JOBS-001","VZ-EMAIL-001"], success=["Each event type produces one notification; preferences honored"], negative=["Notification never reveals a private item to a user who cannot view it"], recovery=["Email failure never fails the action"], api=["GET/PATCH /api/v1/me/notifications"], ui=["bell panel","/notifications","/settings/notifications"], evidence=EV_API+EV_UI)
req("VZ-BLOCK-001","Block/unblock members with retroactive cleanup",
    "Member: blocks another member; blocked member cannot follow, comment, rate, favorite, message, or add to groups/galleries; existing comments/favorites removed and galleries cleaned; block list in settings; no notification to the blocked user; public content still visible to them.",
    "community", FLICKR, [{"source":"FLICKR-BLOCK","note":"effects and non-effects"},{"source":"CATALOG-F4","note":"anti-spam/blocking"}],
    deps=["VZ-FOLLOW-001","VZ-COMMENT-001","VZ-FAVORITE-001"], success=["Block then attempt each interaction → denied; cleanup job completes"], privacy=["Caches/counters updated after cleanup"], api=["PUT/DELETE /api/v1/users/{u}/block"], ui=["profile menu","/settings/blocks"], evidence=EV_API+EV_NEG)
req("VZ-REPORT-001","Report content, comments and users to moderators with categories",
    "Member/visitor: reports a photo, album, comment or user with a category and details; reporter sees outcome; moderators triage in a queue.",
    "community", FLICKR, [{"source":"FLICKR-REPORTING","note":"Flag Photo / Report Abuse"},{"source":"CHEV-MANUALS-ABSENT","note":"Chevereto has no user-facing report feature"}],
    deps=["VZ-MOD-001"], success=["Report creates queue item; resolution notifies reporter"], negative=["Report spam rate-limited"], api=["POST /api/v1/reports"], ui=["report dialog"], evidence=EV_API+EV_UI)
req("VZ-MOD-001","Moderation queue: reports, pending uploads, NSFW flags, with actions, reasons and audit trail",
    "Moderator (manager/admin): queue of reports and pending uploads; approve/reject/delete/flag safe-unsafe/suspend user; every action audited with actor, time, reason; badge refreshes; bulk actions with keyboard shortcuts.",
    "community", CHEV, [{"source":"CHEV-DASHBOARD-FILES","note":"Flag safe V, unsafe F, Approve, Delete Del; approval shown only when moderation enabled"},{"source":"DOD","note":"audit"}], edition="Lite",
    deps=["VZ-AUTH-004","VZ-ADMIN-001"], success=["Queue count accurate; action effect visible to users; audit row"], negative=["Approve twice safe; manager cannot change settings"], api=["/api/v1/admin/moderation*","/api/v1/admin/audit"], ui=["/admin/moderation","/admin/audit"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-NSFW-001","Content safety levels (safe / moderate / restricted) with viewer-side filter, blur, lock editing, and site policy",
    "Photographer: rates own content; visitors' default filter shows safe only (logged-out) with member-adjustable level; owner can blur NSFW in listings, hide from random/explore, disallow moderate/restricted site-wide, lock NSFW editing to moderators; galleries/covers safe-only; ungated by billing.",
    "community", FLICKR, [{"source":"FLICKR-SAFETY","note":"three levels; SafeSearch default on; Pro-gated (not copied)"},{"source":"CHEV-CONTENT","note":"show/blur NSFW, lock NSFW editing, random mode"}],
    deps=["VZ-LIBRARY-002","VZ-ADMIN-002"], success=["Level × viewer filter matrix on listings, search, explore, embeds"], negative=["Restricted video refused if policy says so"], privacy=["Level is orthogonal to visibility"], api=["field safety_level; settings"], ui=["edit form","/settings/content","/admin/settings/content"], evidence=EV_API+EV_UI+EV_NEG,
    mechanism="Chevereto: binary NSFW flag. Flickr: three levels paywalled. Vizra outcome: three levels, operator policy, no billing.")
req("VZ-PROFILE-001","Public profile page with content/albums view, counters, search within user, avatar/background",
    "Visitor: sees a member's public content (default view files or albums per site setting), counters, bio/website; search within the profile; private profiles hide identity.",
    "community", CHEV, [{"source":"CHEV-USER-PROFILE","note":"profile background; user search; follow"},{"source":"CHEV-USERS-SETTINGS","note":"User profile view default Files"}], edition="all",
    deps=["VZ-ACCOUNT-001"], success=["Profile renders per privacy; counters exclude private items"], privacy=["Private profile: no username leak on any JSON endpoint"], api=["GET /api/v1/users/{u}/photos"], ui=["/u/{username}"], evidence=EV_API+EV_UI+EV_NEG)
req("VZ-GROUP-001","Groups: create, privacy (public / invite-only / private), join/leave/invite, roles (admin/moderator/member) and management",
    "Member: creates groups; admins set rules, info, appearance, keywords, custom URL, privacy (private irreversible), safety level; admins/moderators remove/ban members; succession when last admin leaves; only last admin deletes.",
    "community", FLICKR, [{"source":"FLICKR-GROUPS","note":"privacy types; roles; invariants"}],
    deps=["VZ-AUTH-001","VZ-NOTIFY-001"], success=["Role matrix tested; private group invisible to non-members in search/profile"], negative=["Admin cannot demote another admin; last admin only can delete"], privacy=["Private group content never in public search/feeds/federation"], api=["/api/v1/groups*"], ui=["/groups","/g/{slug}","/g/{slug}/admin"], evidence=EV_API+EV_UI+EV_NEG, profiles=("full",))
req("VZ-GROUP-002","Group pools with submission limits, pending-approval queue, and explicit visibility grant",
    "Member: adds own photos to a group pool (per-photo group cap configurable); group may require approval; adding a non-public photo to a pool is an explicit grant confirmed by the owner and never re-enables disabled commenting; lowering group safety removes non-conforming items.",
    "community", FLICKR, [{"source":"FLICKR-GROUP-POOLS","note":"pool visibility override — treated as explicit grant"}],
    deps=["VZ-GROUP-001","VZ-PRIVACY-001"], success=["Pool listing; approve/deny; per-photo cap"], negative=["Non-member cannot see pool of private group"], privacy=["Non-public photo in pool visible to members only via grant; owner's comment setting honored"], api=["/api/v1/groups/{id}/pool*"], ui=["/g/{slug}","photo → add to group"], evidence=EV_API+EV_UI+EV_NEG, profiles=("full",))
req("VZ-GROUP-003","Group discussions: topics, replies, edit/delete rules, sticky and locked topics, inline photo embeds",
    "Member: posts topics and replies; edits own; admins edit/delete any; moderators pin (cap) and lock; embedded group/site photos by link; notifications for pinned groups.",
    "community", FLICKR, [{"source":"FLICKR-GROUP-DISCUSSIONS","note":"sticky (20), lock, edit rules"}],
    deps=["VZ-GROUP-001","VZ-COMMENT-001"], success=["Thread lifecycle tested"], negative=["Locked topic rejects replies"], api=["/api/v1/groups/{id}/topics*"], ui=["/g/{slug}/discuss"], evidence=EV_API+EV_UI, profiles=("full",))
req("VZ-NOTES-001","Positional notes on photos (rectangle + text) governed by owner permission",
    "Member: adds/edits/deletes rectangular notes when the owner allows; notes shown on hover/focus with accessible alternative.",
    "community", FLICKR, [{"source":"FLICKR-NOTES","note":"web-only in Flickr; permission shared with tags/people"}],
    deps=["VZ-VIEWER-001","VZ-PRIVACY-001"], success=["Note persists with coordinates"], negative=["Permission 'nobody' hides control and rejects API"], api=["/api/v1/photos/{id}/notes*"], ui=["viewer notes layer"], evidence=EV_API+EV_UI, profiles=("full",), decided=["Q-041"])
req("VZ-PEOPLE-001","People tagging with subject consent and 'remove me from all' escape hatch",
    "Member: tags people in photos when permitted; a tagged person gains view access only through an explicit grant they can revoke; 'who can tag me' setting; bulk self-removal.",
    "community", FLICKR, [{"source":"FLICKR-PEOPLE","note":"tagging grants access to non-public — treated as explicit grant"}],
    deps=["VZ-PRIVACY-001","VZ-NOTIFY-001"], success=["Tag, consent, revoke flows"], privacy=["No access before grant; removal revokes"], api=["/api/v1/photos/{id}/people*"], ui=["viewer people","/settings/privacy"], evidence=EV_API+EV_NEG, profiles=("full",), decided=["Q-041"])
req("VZ-MESSAGE-001","Private one-to-one messages between members",
    "Member: sends/reads/deletes direct messages; blocked users cannot message; used for system notices too.",
    "community", FLICKR, [{"source":"FLICKR-MAIL","note":"one-on-one; system channel"}],
    deps=["VZ-BLOCK-001","VZ-NOTIFY-001"], success=["Send/receive; block enforced"], privacy=["Message bodies never logged"], api=["/api/v1/me/messages*"], ui=["/messages"], evidence=EV_API+EV_UI, profiles=("full",), decided=["Q-042"])
req("VZ-SPAM-001","Anti-abuse limits on faving, commenting, tagging, following, group invites; account-age gates",
    "Operator: configurable thresholds and account-age requirements for invites/publishing; violations rate-limited and surfaced to moderators.",
    "community", FLICKR, [{"source":"FLICKR-SPAM","note":"excessive faving/commenting; 30-day invite age"}],
    deps=["VZ-AUTH-009"], success=["Thresholds enforced with tests"], api=["settings"], ui=["/admin/settings/limits"], evidence=EV_API+EV_NEG, profiles=("full",))
