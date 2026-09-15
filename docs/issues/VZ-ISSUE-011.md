# VZ-ISSUE-011: M2 — favorites, numeric ratings, native comments, notifications

**Status:** DRAFT (local only — not filed on GitHub; filing requires owner authorization)
**Ledger IDs:** VZ-FAVORITE-001, VZ-RATING-001, VZ-COMMENT-001, VZ-NOTIFY-001
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Member: favorite (idempotent, listing, count, notification), rate 1–5 (one current vote, change/remove, aggregate under concurrency), comment/reply/edit/delete/report with sanitization and owner permission, in-app notifications with preferences; favorites and ratings visually and semantically distinct.

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- 100 concurrent ratings → correct aggregate
- Retry of comment POST with same idempotency key → one comment; XSS vectors sanitized
- Favorite on inaccessible item denied without leaking details
- Notification never reveals a private item

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).

## Evidence required
- integration + browser tests; second-tab state test

## Dependencies / blockers
Q-018 ratified

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
