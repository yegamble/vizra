# War-room board

State only: what is true now and what happens next. One line per slice. `scripts/warroom-check.py board` fails this file above 120 lines or 300 characters a line. Tool results outrank it; every tick reconciles it against `git` and `gh`.

Everything else lives in `docs/warroom/`:

[tick log](../warroom/TICK-LOG.md) · [owner inbox](../warroom/OWNER-INBOX.md) · [owner decisions](../warroom/OWNER-DECISIONS.md) · [merged](../warroom/MERGED.md) · [follow-ups](../warroom/FOLLOWUPS.md) · [board through tick 257](../warroom/archive/WARROOM-BOARD-through-tick-257.md)

**Loop: STOPPED.** Last tick 257 (2026-09-23). Next tick is 258. Restart waits for the rework PR to merge and for the after-merge steps below.

**Ledger on `main`: 192 entries, 0 IMPLEMENTED, 0 VERIFIED.** 257 ticks moved no ledger status. Live state: [reconcile of 2026-11-10](../warroom/RECONCILE-2026-11-10.md).

## In flight

Budget is verdicts/fix rounds/re-plans/ticks against 4/2/1/12, counted per ID from tick 258 (`scripts/warroom-check.py budget`).

| Slice | Repo | IDs | PR | Head | State | Budget |
|---|---|---|---|---|---|---|
| war-room rework | vizra | QUEUE-warroom-rework | #11 | verified `a875a80` | PASS at `e796cca`, then PASS at `a875a80` after fix round 1 (G-1, G-9); 0 blocking, 21 follow-ups open; `ci-required` green. Owner merges | 2/1/0/0 |
| records, ticks 239–257 | vizra | QUEUE-records | #9 draft | `ce2a352` | open; lands after the rework PR | n/a |
| M1-A sentinel follow-ups | vizra-core | QUEUE-2t | #14 | `1d57ad8` | FAIL at round 2; conflicts with main; 3 unpushed local commits. Triage by the new bar | old rules: spent |
| Lane A records no pixels | vizra-user | VZ-FOUND-008 | #10 | `5c5c971` | re-planned as an allowlist gate; uncommitted local work. Triage by the new bar | old rules: 1 re-plan |
| vendor tool, second manifest | vizra-search | QUEUE-2o-5 | none | `ed9f9cc` | 2 commits, unpushed, no PR. Triage by the new bar | old rules: n/a |

## After the rework PR merges (chair, in this order)

1. Land the records: PR #9 plus the two working-tree-only items named in the reconcile.
2. Apply the approved rulesets; vizra-core after its CI repair is green.
3. Triage core #14, user #10, the search vendor branch and queue 2o: one final bounded round only for parts that meet the bar; the rest to follow-ups.
4. Remove worktrees and local branches whose PR is confirmed merged; list anything unmerged.
5. Record ledger status for merged work where the evidence satisfies the status checker (its own verified PR).
6. Seed the queue below with slice briefs, then restart the loop.

## Queue (milestone order; lowest milestone with a not-VERIFIED ID first)

| # | Slice | Repo | IDs | Depends on |
|---|---|---|---|---|
| 1 | CI repair: `govulncheck` is a required lane and is red on main since 2026-10-12 (16 advisories) | vizra-core | VZ-CI-004 | nothing; every core PR is red until it lands |
| 2 | Record status for merged work, only where the evidence satisfies `status.py` | vizra | candidates: VZ-FOUND-001…008, VZ-INSTALL-003, VZ-TOPOLOGY-001…003 | nothing |
| 3 | Installer, one command, idempotent (reference: `vidra/install.sh`) | vizra | VZ-INSTALL-001 | compose on main |
| 4 | `vizra setup`: interview, `--web` loopback wizard, `--yes`, `--check` | vizra-core + vizra | VZ-INSTALL-002 | 3 |
| 5 | Deterministic bundle and the `bundle` lane | vizra | VZ-INSTALL-004 | 3 |
| 6 | `boot` lane: production-mode stack boots in CI | vizra | VZ-CI-003 (M1), closes M0 "boot lane green" | 3, 5 |
| 7 | `vizra doctor`, status, logs, restart, update | vizra-core | VZ-OPS-002, VZ-OPS-003 | 4 |
| 8 | Logs, metrics, tracing with privacy-safe fields | vizra-core | VZ-OPS-005 | none |
| 9 | Tokens, typed icon registry, app shell, security headers (design accepted 2026-11-10) | vizra-user | VZ-DESIGN-001 | none |
| 10 | Host and image security posture | vizra + vizra-core | VZ-OPS-008 | inbox 9 for the image CVEs |
| 11 | M1, not blocked by 4a or 8b: registration and sessions, roles | vizra-core + vizra-user | VZ-AUTH-001, VZ-AUTH-004 | M0 boot; M1-A merged |
| 12 | M1: durable jobs, local storage, quota, JPEG/PNG upload | vizra-core | VZ-JOBS-001, VZ-STORAGE-001, VZ-QUOTA-001, VZ-UPLOAD-001 | 11 |
| 13 | M1: backup and restore on a clean target (reference: vidra deploy order) | vizra-core + vizra | VZ-BACKUP-001, VZ-BACKUP-002, VZ-OPS-001 | 12; rehearsal host |

Rows 3 to 13 are a starting order, not briefs. The chair writes each brief from the ledger entry and `docs/issues/` when the slice is dispatched.

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
| 5 | Fork-PR workflow approval setting (`all_external_contributors`?). Rulesets part decided |
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
