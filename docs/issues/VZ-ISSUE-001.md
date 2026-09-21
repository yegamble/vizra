# VZ-ISSUE-001: M0 — create component repositories, pin the toolchain, record ADRs

**Status:** FILED 2026-09-15 as https://github.com/yegamble/vizra/issues/1 (#1)
**Ledger IDs:** VZ-FOUND-001, VZ-FOUND-002, VZ-FOUND-003, VZ-FOUND-004, VZ-FOUND-005, VZ-FOUND-006, VZ-FOUND-007, VZ-FOUND-008 (VZ-FOUND-001…008 — `docs/MILESTONES.md` M0 lists all eight)
**Implementation status:** PLANNED · **Verification status:** UNVERIFIED

## Outcome
Developer: `vizra-core`, `vizra-user` and `vizra-search` exist with AGENTS.md, lockfiles, pinned Go 1.27.x / Echo v5 ≥ 5.3.1 / sqlc 1.31.1 / PostgreSQL 18 / Valkey (managed) with go-redis v9 / Next.js 16.3.x / lucide-react 1.46.x, an OpenAPI source with both-direction drift check, sqlc verify, append-only migrations compiled into the binary with migrate-lint, health/readiness/version probes, and fail-secure production config validation. The foundation also produces the two things every later slice's evidence depends on: the **deterministic fixture corpus** — a pinned generator script, a committed sha256 manifest with the generator version, the twelve M0 fixtures and the load-corpus generator (VZ-FOUND-007) — and the **browser-test environment** — a Playwright harness driving the production build, desktop and mobile projects, capturing console and network errors, running in CI against the built image (VZ-FOUND-008).

## Scope
One focused PR per session; complete vertical slice (migration/query → API → real UI → tests → operations/docs) for the IDs above. Anything not listed stays in `docs/quality/features.json` and is not narrowed by this issue.

## Acceptance (observable)
- Repositories created: yegamble/vizra-core, yegamble/vizra-user, yegamble/vizra-search (private, README-only, created 2026-09-15; content still PLANNED)
- ADR-001 stack pins and licences (Echo v5 + otelhttp tracing path with spike transcript, Q-003; Valkey managed + go-redis with Valkey/Redis 7.2 matrix, Q-004; govips/libvips LGPL with digest-pinned build and loader list, Q-034)
- `make ci` in core/search and `npm run ci` in user execute real checks
- Route-without-spec and spec-without-route both fail CI (demonstrated)
- Hand-edited sqlc output fails drift check (demonstrated)
- Production boot refuses dev secrets (demonstrated)
- Fixture corpus (VZ-FOUND-007): the pinned generator reproduces the twelve M0 fixtures byte-identically against the committed sha256 manifest, and a changed fixture fails the manifest check (demonstrated)
- Browser-test environment (VZ-FOUND-008): the Playwright harness runs in CI against the production build image on desktop and mobile projects, and a console or network error fails the lane (demonstrated)

## Verification
- Read `AGENTS.md`, the ledger entries above (success / negative / privacy / recovery cases), `docs/PRODUCT_SPEC.md`, and `docs/quality/COMMANDS.md` once it exists.
- Tests must challenge the implementation: show the relevant test failing against a controlled mutation before claiming coverage.
- Run focused checks while iterating, then every required lane for the affected repos; a missing command or dependency is BLOCKED, never a pass.
- Record exact commands, exit codes, test counts, skips, source SHA, environment and artifact paths in the execution plan (`docs/plans/`).
- Read `docs/adr/ADR-001`…`ADR-009` (architecture pass 2026-09-15) and `docs/plans/2026-09-15-prompt01-architecture.md` before implementing.

## Evidence required
- Clean-clone build transcript per repo with SHA and exit codes
- CI run links showing deliberate breakage → red → restore → green

## Dependencies / blockers
Q-001…Q-004, Q-034 ratified 2026-09-15 (docs/OPEN_QUESTIONS.md ratification record). GitHub owner confirmed (yegamble) and repos created 2026-09-15; owner authorized gh writes this session.
Owner architecture approval of ADR-001…009 (Prompt 01 gate) — **given 2026-09-20** (docs/plans/WARROOM-BOARD.md, "Owner decisions"). Local preflight 2026-09-20: `exiftool` is not installed on the owner's machine, so the fixtures generator (VZ-FOUND-007) reproduces only in the CI image until it is.

## Definition of done
Ledger entries updated with evidence; UI-control inventory updated where controls changed; execution plan checkpointed; PR opened as READY_FOR_REVIEW. Never self-merge; never mark VERIFIED without independent verification.
