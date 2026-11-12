# War-room board

State only: what is true now and what happens next. One line per slice. `scripts/warroom-check.py board` fails this file above 120 lines or 300 characters a line. Tool results outrank it; every tick reconciles it against `git` and `gh`.

Everything else lives in `docs/warroom/`:

[tick log](../warroom/TICK-LOG.md) · [owner inbox](../warroom/OWNER-INBOX.md) · [owner decisions](../warroom/OWNER-DECISIONS.md) · [merged](../warroom/MERGED.md) · [follow-ups](../warroom/FOLLOWUPS.md) · [board through tick 257](../warroom/archive/WARROOM-BOARD-through-tick-257.md)

**Loop: RUNNING since tick 258 (2026-11-10), restarted on the owner's word.** Previous tick 257 (2026-09-23). The rework (#11, `82e9529`) and the records (#9, `27be92a`) are on `main`; the after-merge steps are done ([record](../evidence/warroom/2026-11-10-after-merge-TRIAGE.md)).

The main checkout is on `main` since 2026-11-10 (inbox 14, closed), so `/warroom` there is the reworked command and the Stop hook runs.

**Ledger on `main`: 192 entries, 0 IMPLEMENTED, 0 VERIFIED.** 16 candidates were tried on 2026-11-10 and none is honestly recordable ([why, per ID](../evidence/warroom/2026-11-10-ledger-status-candidates.md)). Live state in September terms: [reconcile](../warroom/RECONCILE-2026-11-10.md).

Ticks 258–261 merged seven milestone PRs and recorded no status. What each ID still lacks, case by case, is in the queue rows 2, 3 (002, 003, 006), 11 and 14.

Rulesets (`ci-required` required, linear history, no force-push, no deletion) are active on all four repos (vizra-core `26972947` since tick 259).

## In flight

Budget is verdicts/fix rounds/re-plans/ticks against 4/2/1/12, counted per ID from tick 258 (`scripts/warroom-check.py budget`).

| Slice | Repo | IDs | PR | Head | State | Budget |
|---|---|---|---|---|---|---|
| Queue 3a: contract test walks wildcard routes; migrate-lint column drops | vizra-core | VZ-FOUND-002, VZ-FOUND-003 | #18 | `84f8ad1` | FAIL at `a627e1f`, fix round 1 pushed, `ci-required` green; re-verification allowed by owner grant 2026-11-12 #1 once it is on `main` | 002: 4/1/0/3 of 6/2/1/12; 003: 2/1/0/3 of 5/2/1/12 |

## Parked (closed by the triage of 2026-11-10; on GitHub only since the owner's answer of 2026-11-10, not merged, not in flight)

| Branch | Repo | State |
|---|---|---|
| `fix/m1a-sentinel-followups` `e43d501` | vizra-core | #14 closed unmerged; parts are in the core follow-up batch |
| `fix/lane-a-pixels-off` `5c5c971` | vizra-user | #10 closed unmerged; superseded by the allowlist branch |
| `allowlist/pr10-work` `7fb1365` | vizra-user | one WIP commit, UNVERIFIED, no PR; the base for queue 2f |
| `feat/vendor-tool-second-manifest` `ed9f9cc` | vizra-search | UNVERIFIED, no PR; waits for the 2o engine in core |

## Queue (milestone order; within M0, the IDs closest to recordable first)

Every row names what is missing for the ID to be recorded, from the candidates record. A slice is done when its ID's record is on `main`, not when its PR merges.

| # | Slice | Repo | IDs | Depends on |
|---|---|---|---|---|
| 2 | `/readyz`: storage merged (core #17). Left: schema-behind is not a `/readyz` component; no DB-recovery test; transcript on a compose stack and rendered-model assertion; Redis-down is 200 `degraded` against the ledger text (inbox 15) | vizra-core | VZ-FOUND-005 | inbox 15 for the Redis part |
| 3 (002) | VZ-FOUND-002 lacks: S1 until core #18 is re-verified and merged; `evidence_required` (the drift mutation red then green as CI job output, not local). S2 and N1 proven (user #12) | vizra-core | VZ-FOUND-002 | core #18 |
| 3 (003) | VZ-FOUND-003 lacks: N1 until core #18 merges; S1 (no lane runs `migrate up` from the release image); R1 (no test sets a ledger dirty); the outcome's "compatibility window" does not exist. S2, N2 proven | vizra-core | VZ-FOUND-003 | core #18 for N1 |
| 3 (006) | VZ-FOUND-006 lacks: S2 (`vizra setup` does not exist, queue 7); N1 boot-refusal transcript; P1 (two integration tests not run); N2 limit: meta CI checks a snapshot of core's keys. S1 and N2 proven on the meta side (meta #17) | vizra + vizra-core | VZ-FOUND-006 | queue 7 for S2 |
| 4 | Tombstone rule in all four `ci-required` guards; vizra-user's two "required only if it ran" lanes | all four | VZ-CI-001 | 1 for core |
| 5 | `bootstrap.sh`; pin the libvips binding and Lucide | vizra + vizra-core + vizra-user | VZ-FOUND-001, VZ-FOUND-004 | 1 |
| 6 | Installer, one command, idempotent (reference: `vidra/install.sh`) | vizra | VZ-INSTALL-001 | compose on main |
| 7 | `vizra setup`: interview, `--web` loopback wizard, `--yes`, `--check` | vizra-core + vizra | VZ-INSTALL-002, closes VZ-CI-002 with 8 | 6 |
| 8 | Deterministic bundle and the `bundle` lane | vizra | VZ-INSTALL-004 | 6 |
| 9 | `boot` lane: production-mode stack boots in CI, including the external PostgreSQL and Redis shapes with fault injection | vizra | VZ-CI-003 (M1), VZ-TOPOLOGY-001…003 | 6, 8 |
| 10 | Harness boots the real API, PostgreSQL and Redis; axe runs | vizra-user | VZ-FOUND-008 | 9; the artifact gate (2f) before any spec signs in |
| 11 | Scan lanes required and green; secret-scan lane | vizra-core + vizra-user | VZ-CI-004 | 1; inbox 9 for the image CVEs |
| 12 | `vizra doctor`, status, logs, restart, update | vizra-core | VZ-OPS-002, VZ-OPS-003 | 7 |
| 13 | Logs, metrics, tracing with privacy-safe fields | vizra-core | VZ-OPS-005 | none |
| 14 | Tokens, icon registry, shell and CSP merged (user #11). Left: components with variants and states, brand mark, `design/HANDOFF.md`, first-slice screens; owed: production-mode browser pass at desktop and mobile, and the CSP mutation (owner 2026-11-11 #4) | vizra-user | VZ-DESIGN-001 | none |
| 15 | Host and image security posture | vizra + vizra-core | VZ-OPS-008 | inbox 9 |
| 16 | M1, not blocked by 4a or 8b: registration and sessions, roles, the claim page | vizra-core + vizra-user | VZ-AUTH-001, VZ-AUTH-004, VZ-INSTALL-003 | M0 boot |
| 17 | M1: durable jobs, local storage, quota, JPEG/PNG upload, the rest of the fixture corpus | vizra-core | VZ-JOBS-001, VZ-STORAGE-001, VZ-QUOTA-001, VZ-UPLOAD-001, VZ-FOUND-007 | 16 |
| 18 | M1: backup and restore on a clean target (reference: vidra deploy order) | vizra-core + vizra | VZ-BACKUP-001, VZ-BACKUP-002, VZ-OPS-001 | 17; rehearsal host |

Rows are a starting order, not briefs. The chair writes each brief from the ledger entry and `docs/issues/` when the slice is dispatched.

## Blocked

| Item | Waiting on |
|---|---|
| VZ-MEDIA-001 (derivatives) and what depends on it: VZ-MEDIA-003/004, VZ-VIEWER-001 | owner ruling on inbox 4a |
| M1-B (rest of the owner-claim issue) | owner ruling on inbox 8b |
| Deploy rehearsal, VZ-BACKUP-002 on a separate host | the disposable rehearsal host (inbox 7) |
| Q-016, Q-021, Q-022, Q-036 | provider credentials and the owner's domain |

## Owner inbox (index; full text in [OWNER-INBOX.md](../warroom/OWNER-INBOX.md))

| # | One line |
|---|---|
| 3 | Mockup controls with no ledger ID: add, mark unavailable, or drop |
| 4a | ADR-001 AVIF/HEIC split is not implementable as written. Blocks VZ-MEDIA-001 |
| 4b | ADR-009 fixture tooling and ADR-004 / ADR-002 wording, for the same amending ADR |
| 5 | Fork-PR workflow approval setting (`all_external_contributors`?). Rulesets applied on three repos |
| 6 | Cross-repo contract freshness: token or meta fan-in lane |
| 7 | Q-008, Q-041, Q-042; the rehearsal host; Q-036 domain before M6 |
| 8a | Ledger wording for the VZ-INSTALL-003 recovery case |
| 8b | ADR-003 CSRF-table reading and one-line amending ADR. Blocks M1-B |
| 8c | User erasure against the audit trail (before M2) |
| 8d | ADR-003 "owner is single" against owner transfer |
| 8e | Owner-claim lockout residual until M1-B |
| 9 | Base-image CVEs: accept, or an expiring ignore file. Now 69 at or above HIGH, 1 CRITICAL |
| 11 | Scrub local paths from committed evidence on the public repos? |
| 12 | VZ-FOUND-008 acceptance text against Lane A with pixels off |
| 13 | Coverage gaps: installer, wizard, IPFS topology, QA, security testing, rehearsal, CI repair, VZ-AUDIT-001 |
| 15 | VZ-FOUND-005: Redis carries rate-limit counters, not only cache, so the ledger text was not amended; `/readyz` 503 or 200 `degraded` when it is down? |
