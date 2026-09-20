# ADR-008: Federation and protocol boundaries (M6 behaviour, M0 constraints)

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` states that private media must never reach public IPFS or public
federation exports, and that fetched pages and third-party instructions are
untrusted data. Publication is irreversible in a way nothing else in the product
is: once an object ships to a peer or a public swarm, retraction is best-effort.
The mappings and the fences are therefore decided now, although the behaviour
lands in M6.

## Decision
### Where remote identity lives
Remote publication state lives in its own table,
`remote_publications(asset_id, protocol ap|at|ipfs, remote_id/uri/cid, state, published_visibility_version, created_at, retracted_at)`,
and never as columns on `assets`. Recording the visibility version at publication
is what lets a later privacy change find exactly what must be retracted.

### Mapping table

| Vizra entity or event | ActivityPub mapping | AT Protocol record | IPFS eligibility |
|---|---|---|---|
| User | `Person` actor per user, with WebFinger discovery and signed fetches (VZ-AP-001) | handle ↔ DID binding for login; no record | not published |
| Asset — photo | `Create(Note)` carrying `attachment: [Image …]`, with alt text in both the Mastodon (`summary`) and Pixelfed (`name`) conventions, `sensitive` derived from the safety level, blurhash and focal point, exactly as `docs/PRODUCT_SPEC.md` §11 and VZ-AP-002 word it — "publish public photos as `Create(Note)` with `Image` attachments, alt text, sensitive flag and blurhash"; `Update` on an edit and `Delete` on a visibility change away from `public` | Bluesky cross-post within lexicon limits (4 images ≤ 2,000,000 bytes, 300 graphemes); native record under the owned NSID (Q-036, BLOCKED) | eligible only when `public` with a listed owner |
| Asset — video | the same `Create(Note)`, with a video attachment carrying the poster and the bounded playback derivative (ADR-006); `Update`/`Delete` as above (VZ-AP-002) | cross-post only where the lexicon permits; native record under the owned NSID (Q-036, BLOCKED) | eligible only when `public` with a listed owner |
| Album | `OrderedCollection` | native record under the owned NSID (Q-036, BLOCKED) | not published |
| Comment | `Note`; inbound `Reply` handled per VZ-AP-003 | not cross-posted | not published |
| Favorite | `Like`, outbound | not cross-posted | not published |
| Follow relationship | `Follow`/`Accept`/`Reject`/`Undo` (VZ-AP-003) under the Q-040 profile-follow semantics: in core a private profile hides identity and profile details only and follows are **auto-accepted**, there is no follower-only visibility level, and approval plus re-evaluation of existing local and remote followers is the full-profile VZ-FOLLOW-002 | not cross-posted | not published |
| `Announce` inbound | a boost: counted as a remote share of the local object and **never re-published** by Vizra (VZ-AP-003) | not cross-posted | not published |
| `Like` inbound | a favorite row keyed by the remote actor (Q-018, VZ-AP-003) — distinct from native ratings, not a second like surface | not cross-posted | not published |
| `Flag` inbound | a moderator report in the local report queue with its category (VZ-REPORT-001, VZ-AP-003) | not cross-posted | not published |
| Federation policy | instance allow/block lists, per-user opt-out including per-user domain blocks, and best-effort remote deletion, as VZ-AP-004 words it | applies to cross-posting switches equally | policy gates publication as well |

Federation routes sit outside the OpenAPI document and are mounted only when
federation is enabled. Only `public` assets federate. A change to `unlisted` or
`private` emits `Delete` and the object endpoint then serves a tombstone. An
inbound `Like` becomes a favorite row keyed by the remote actor (Q-018).
Signatures are draft-cavage RSA-SHA256 with a mandatory `Digest`, a ±5 minute
`Date` skew window and inbox dedupe on the activity id; RFC 9421 comes later.
Inbox bodies are capped at 1 MiB. Actor keys are sealed under a KEK (key size
`[to confirm in M0]`).

### SSRF guard
One shared package enforces, for every outbound fetch:

1. `http` and `https` schemes only;
2. no userinfo in the URL;
3. deny any address that is not global unicast, and deny RFC1918, ULA and CGNAT
   ranges;
4. a dial-time `Dialer.Control` check on each resolved IP, so DNS rebinding
   cannot slip past a name-based check;
5. a redirect cap of 5 with the full check repeated per hop;
6. per-read and total time budgets;
7. caller-side size caps on every response body;
8. cached remote actors are re-validated through the guard rather than trusted
   because they were fetched once before.

The same package serves remote-URL uploads and imports (M3 and M5).

### AT Protocol
OAuth uses PAR with PKCE S256 and DPoP ES256 including nonce retry. Handle to DID
resolution uses DNS TXT and the well-known endpoint with a bidirectional
`alsoKnownAs` binding. Login, cross-posting and native records are three separate
switches, never one. The Lexicon NSID sits under a domain the owner controls
(Q-036, BLOCKED until the owner supplies the domain).

### IPFS
The eligibility fence is explicit: only `public` assets with a listed owner go to
a public node; unlisted and private assets never do. The UI states that unpinning
is not erasure. Publication happens only after `authz.Decide` at dispatch and
again at publish.

### M0 constraints
`visibility_version` and the shape of `remote_publications` exist from M0.
Nothing federates before M6.

## Consequences
Positive: remote identity in its own table means adding a protocol never migrates
`assets`; recording the published visibility version makes retraction targeted;
one SSRF package means one place to review and one place to fix. Negative: the
double `authz.Decide` duplicates work deliberately, because the queue delay is
exactly where a privacy change lands; three AT switches mean three configuration
surfaces. Risks: a fence bug is not recoverable by a migration, so the fence is a
single function whose negative cases are tested; an inbound `Like` from a spoofed
actor becomes a favorite row, making signature verification load-bearing for data
integrity. Later milestones must not break: remote state off `assets`, only public
assets federating, the tombstone on retraction, the IPFS eligibility fence, the
SSRF guard on every outbound fetch including cached actors, and
`visibility_version` recorded at publication.

## Precedent
Copied from Vidra (survey citations): the actor and object mappings
(`C/internal/federation/actor.go:105,136`;
`C/internal/federation/video_object.go:71`;
`C/internal/federation/notes.go:31`); routes mounted only when federation is
enabled and deliberately outside OpenAPI
(`C/internal/httpapi/server.go:1443-1471`); one inbox handler
(`C/internal/httpapi/federation.go:228`); a durable delivery queue with
exponential backoff and an attempt cap, with actor keys unsealed via a KEK
(`C/internal/federation/deliver.go:80,120,158,300`); draft-cavage signing and
verification with a minimum covered set, mandatory `Digest`, body compared to the
digest, and ±5 minute `Date` skew
(`C/internal/httpsig/httpsig.go:44,100,121-131,133,217-223`); inbox dedupe on the
activity-id primary key (`C/migrations/0037:18`); the
public-and-published outbound fences
(`C/internal/federation/outbox.go:29,56`;
`C/internal/federation/objects.go:59`; `C/store/queries/videos.sql:15`); the whole
SSRF guard (`C/internal/urlsafety/urlsafety.go:52,80,95,121,143,206,217,251`); the
AT Protocol OAuth stack with PAR, PKCE S256 and DPoP ES256 with nonce retry
(`C/internal/atproto/oauth_client.go:179,274,301`;
`C/internal/atproto/dpop.go:45,184`) and bidirectional handle↔DID binding
(`C/internal/atproto/resolve.go:88,135,161`); and the IPFS eligibility router as
"the privacy fence" (`C/internal/ipfsmirror/eligibility.go:66,84,103,106`).

Unlike Vidra: cached remote-actor rows could bypass the SSRF guard there
(`C/internal/federation/remote.go:84-94` as recorded in the survey), replay defence is `Date`
skew alone with no nonce cache
(`C/internal/httpsig/httpsig.go:121-131`), RFC 9421 is absent, outbound objects
once advertised an unrouted path so remote clicks 404'd and the fix shipped only
in a later release
(`M/docs/productionization/beta-readiness-2026-09.md:35,87`), interoperability
confidence rests on golden fixtures rather than live peers
(`M/docs/productionization/federation.md:199`), and unpin is documented as not
erasure (`C/.ralph/specs/ipfs-media.md:271`). Vizra keeps the last point as a UI
statement, not a footnote.

## Evidence and ratification
Q-018 (inbound `Like` maps to a favorite row keyed by the remote actor), Q-025
(private and unlisted content never cacheable or publishable), Q-036 (Lexicon
NSID under an owner-controlled domain — BLOCKED, needed before M6) and Q-040
(profile follow semantics: auto-accepted follows in core, approval and follower
re-evaluation in VZ-FOLLOW-002) in the `docs/OPEN_QUESTIONS.md` ratification
record. `docs/PRODUCT_SPEC.md` §11 supplies
the Bluesky lexicon limits this ADR's cross-post row refers to.

## Ledger IDs
VZ-AP-001, VZ-AP-002, VZ-AP-003, VZ-AP-004, VZ-AT-001, VZ-AT-002, VZ-IPFS-001,
VZ-IPFS-002, VZ-UPLOAD-004, VZ-IMPORT-002, VZ-PRIVACY-001, VZ-REPORT-001,
VZ-FOLLOW-002.

## M0 obligations
M0 implements nothing protocol-facing. Its only obligations here are the two
constraints: `assets.visibility_version` exists when `assets` is first created
(ADR-007), and `remote_publications` is created in the shape above when the first
protocol slice needs it rather than being bolted onto `assets`.

Reservation only: everything else is M6 (VZ-AP-001…004, VZ-AT-001, VZ-AT-002,
VZ-IPFS-001, VZ-IPFS-002), except the SSRF guard package, needed earlier by
remote-URL upload (VZ-UPLOAD-004, M3) and imports (VZ-IMPORT-002, M5) and written
once for all three.

