# The Vizra Product & Engineering Council

Fifteen project subagents, checked into this meta repo, that review Vizra from
genuinely different seats. Launch from the meta repo root — this is where
`vizra-core`, `vizra-user` and `vizra-search` will be tied together. Adapted
from the Vidra council (`~/github/vidra/.claude/agents`) on 2026-09-15 for a
photo product and for Vizra's `AGENTS.md` contract.

## Launch

```
/council <scope>
```

e.g. `/council albums: do album privacy, sub-albums, multi-album membership,
share grants and every read surface (thumbnails, counts, search, embeds,
export) add up to a complete, private-by-default product, or only a schema?`

The chair picks **3–5** teammates — never all fifteen. Beyond five,
coordination overhead eats the benefit.

## Roster

| Agent | Seat | Primary question |
|---|---|---|
| `vizra-architect` | principal architect | Does this make sense across core/user/search/meta, and is each responsibility in the right place? |
| `vizra-core` | backend/API engineer | Is the domain model, API and data behaviour correct — after a partial failure too? |
| `vizra-user` | frontend engineer | Can people operate what core implements, from every control in the inventory? |
| `vizra-search` | search/discovery engineer | Is discovery useful, private (facets, counts, suggestions, caches), resilient, measurable? |
| `vizra-media-storage` | media pipeline / storage engineer | Are the bytes safe, correct, private and recoverable across local/S3/AWS/Backblaze/IPFS? |
| `vizra-infrastructure` | self-hosting SRE / platform | Can an operator install, upgrade, diagnose and recover this safely? |
| `vizra-security` | application security | What can an attacker, a hostile instance or a low-privileged user reach? |
| `vizra-qa-release` | QA / release lead | Does it work end to end, including failure paths — and is the evidence real? |
| `vizra-product-completeness` | principal PM | Is this a complete vertical slice of a ledger obligation, or just code that exists? |
| `vizra-visitor` | visitor/member advocate | Would a normal person understand, find, enjoy and use this? |
| `vizra-photographer` | uploader/creator advocate | Can a photographer actually finish the job — upload, organize, share, leave? |
| `vizra-instance-admin` | owner/moderator advocate | Can the owner configure, moderate, diagnose and reverse this from the UI? |
| `vizra-design` | UI/UX design authority | Is this designed and measurably accessible, or just styled? |
| `vizra-business` | product strategy | Does this earn its complexity in adoption and value, without inventing billing? |
| `vizra-devils-advocate` | adversarial reviewer | What are we fooling ourselves about — including claims of VERIFIED? |

## Shared contracts (every teammate reads these first)

- `.claude/council/repo-map.md` — the repositories (what exists and what is
  only planned), the boundaries, the planned verification gates, the status
  vocabulary and the traps.
- `.claude/council/finding-format.md` — the one finding schema everybody uses,
  including ledger requirement IDs.
- `.claude/council/protocol.md` — Round 0 (shared evidence) → A (blind) →
  B (cross-examination) → C (rebuttal) → D (chair's ruling), plus the effort
  budget for each round.

`AGENTS.md` is binding on every seat. Each component's `AGENTS.md` becomes
binding the moment that repo exists.

## Design decisions worth knowing

- **All fifteen are read-only during council rounds.** The council reviews; it
  does not edit. Implementation is assigned afterwards, one repo to one
  implementer, and follows `AGENTS.md`: one acceptance item, one focused PR,
  tests that challenge the implementation, exact evidence, READY_FOR_REVIEW.
  - `vizra-design` is the one seat that also carries `Edit`/`Write`, for
    *direct* invocation outside a council run, and defaults to read-only when
    ambiguous.
- **No "finished means merged" Stop hook here, deliberately.** Vidra's meta
  repo enforces self-merge on green CI. Vizra's `AGENTS.md` forbids self-merge
  and requires independent verification before anything is VERIFIED; the
  session close-out rule is "checkpoint unfinished work in `docs/plans/`
  rather than conceal it". A hook that pushes agents to merge would contradict
  the contract.
- **`vizra-media-storage` is a seat Vidra does not have.** In a photo product
  the originals, derivatives, EXIF/GPS policy and provider matrix are the
  centre of gravity, and they deserve a reviewer whose whole job it is.
  `vizra-core` still owns the transactional model around them.
- **All fifteen run on Opus with `effort: high` pinned in frontmatter**, for
  the same reason as Vidra: the teammates perform the cross-examination, and a
  weaker challenger weakens the mechanism. Cost is controlled by the Round 0
  evidence pass and by not running every round at maximum.
- **The chair is an Opus session running `/advisor fable`**, not a Fable
  session. Never introduce "show/explain your reasoning" wording into the
  protocol or a teammate prompt.
- **Infrastructure, security and instance-admin are three separate seats.**
  "Can the machine run and recover?", "what can an attacker reach?" and "can I
  run my community?" are different questions with different evidence.
- **Visitor and photographer are deliberately separate.** They want opposite
  things (simplicity vs control) and that tension should surface.
- The most valuable seat is usually `vizra-product-completeness`, whose
  mantra is: *"Implemented in Go" is not the same thing as "Vizra has this
  feature"* — and whose second job is catching scope that quietly vanished
  from the ledger.
