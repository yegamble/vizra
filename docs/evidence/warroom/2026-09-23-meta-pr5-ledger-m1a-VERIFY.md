# Independent verification — vizra (meta) PR #5, M1-A ledger obligations

- PR: https://github.com/yegamble/vizra/pull/5 — "docs(ledger): VZ-AUDIT-001 and the M1-A owner-claim ledger obligations"
- Head SHA verified: `cd4c0f2dddbe1616fa525fc5a4be9633ca4dfd86` (branch `docs/m1a-ledger-obligations`), confirmed with `gh pr view 5 --json headRefOid` at the start of the run
- Base: `main` @ `6b8158c3280ecd17a32efbb009ab06d04da42260` (merge-base = origin/main; two commits `dd7955e`, `cd4c0f2`)
- Verifier: independent war-room verifier (did not write this code)
- Date: 2026-09-23
- Clone: fresh `git clone` of github.com/yegamble/vizra into a `mktemp -d` scratch dir under the session scratchpad, `git fetch origin pull/5/head`, detached checkout of the SHA; base checked out as a separate worktree of that clone. Nothing run in the builder's checkout.
- Environment: macOS (Darwin 25.5.0, arm64); `/usr/bin/python3` 3.9.6 and uv-managed CPython 3.12.11 (CI pins 3.12.14); git 2.50.1 (Apple Git-155); `PYTHONDONTWRITEBYTECODE=1` on every Python run. No containers started.

## 1. Validate lane and guards, local (head cd4c0f2)

| Command | Python | Exit | Output (key line) |
|---|---|---|---|
| `./scripts/check-generated-ledger.sh` | 3.9.6 | 0 | `OK 192 requirements; core=142` … `generated ledger reproduces byte-for-byte: docs/quality/features.json (UTF-8 and C/POSIX locales)` |
| `./scripts/check-generated-ledger.sh` | 3.12.11 | 0 | same, byte-for-byte under both locales |
| `./scripts/check-quality-json.py` | 3.9.6 and 3.12.11 | 0 | `4 file(s)`; `192 requirement id(s)`; `191 written reference(s) expanded to 287 id(s), 204 distinct, across 14 document(s); every one resolves` |
| `./scripts/check-doc-links.py` | 3.9.6 | 0 | `relative links: none exist yet across 95 markdown file(s) (checked nothing); 7 external URL(s)` |
| `./scripts/ci-required-guard.sh` | 3.9.6 | 0 | workflows 2, no continue-on-error; 3 pinned actions; floor present; manifest bare; lane integrity 1; fixture floors 6/7/10 exercised |
| `./scripts/check-workflows.py`, `check-action-pins.py`, `check-lane-integrity.py` | 3.9.6 | 0 each | as above |

`git status --short` after all runs: clean. No skips (these scripts have no skip mechanism; each prints what it checked).

Base (6b8158c) for comparison: 191 requirement ids; the same 191 written references / 287 / 204; generator reproduces; doc-links reports 7 external URLs across 94 files.

## CI on this SHA

Read with `gh api repos/yegamble/vizra/commits/cd4c0f2dddbe1616fa525fc5a4be9633ca4dfd86/check-runs` and `gh api repos/yegamble/vizra/actions/runs/35836746761/jobs`:

| Check run | Status | Conclusion | Steps |
|---|---|---|---|
| `validate` (run 35836746761) | completed | **failure** | **0** — annotation: "The job was not started because recent account payments have failed or your spending limit needs to be increased." |
| `ci-required` (run 35836746627) | completed | **failure** | not started (same billing refusal) |
| GitGuardian Security Checks (third-party app, not in `required-checks.txt`) | completed | success | "2 commits were scanned without uncovering any secrets" |

`ci-required` is **not green** on this SHA and `validate` never executed. Per AGENTS.md a check that did not run is not a pass: **CI is BLOCKED (missing input: GitHub Actions billing on the account)**. Every result in this file is local. The manifest `.github/required-checks.txt` lists exactly `validate`, which is the only job `validate.yml` defines; the manifest is consistent with the workflows (`ci-required-guard.sh` exit 0), but nothing ran.

## 2. features.json, base 6b8158c → head cd4c0f2, field by field

Method: `json.load` both files; compare every top-level key, every requirement by id, and every field of every changed requirement (lists: removed items / added items / base-is-ordered-prefix; dicts: per sub-key; strings: equality and startswith).

- Top-level keys other than `summary` and `features`: identical (`schema_version`, `generated`, `notice`, `parity_baseline_status`, `status_vocabulary`, `source_kinds`).
- `summary`: `total` 191→192, `core_profile` 141→142, `full_profile` 191→192, `by_area.identity` 14→15, `by_source_kind.recommended_safeguard` 19→20. Nothing else moved; open/decided question lists identical.
- Ids: removed `{}`; added `{VZ-AUDIT-001}` (index 53, directly after `VZ-ADMIN-USERS-001`); base id order is preserved as a subsequence of head.
- Changed existing entries: exactly two.
  - **VZ-INSTALL-003**: `surfaces.api` `[POST …/claim-owner]` → `[POST …/claim-owner, GET /api/v1/setup/claim-status]`; `surfaces.cli` `[]` → `[vizra claim-token]`; `notes` null → a note citing the rulings (OQ-3, OQ-9, S-12, row 2/OQ-11, row 3/OQ-2) and owner inbox 8a. `cases.recovery` is `["Restart re-mints; old token invalid"]` at both base and head (**byte-identical**, compared as parsed strings and absent from `git diff` of the generator source); `outcome` identical ("…mints a one-time token at boot, prints it to its log…"). No other field changed.
  - **VZ-ADMIN-USERS-001**: `outcome` = base outcome verbatim + one appended sentence ("Owner: transfers the single owner role to another live user; an instance whose only owner account is tombstoned is recoverable and never left ownerless.") — `head.startswith(base)` True; `cases.success` base item kept + 2 added; `cases.negative` base item "Cannot demote the last owner" kept + 2 added; `cases.privacy` [] → 1; `cases.recovery` [] → 1; `notes` null → note. No other field changed.
- No requirement removed, narrowed or re-scoped; no list item removed anywhere.
- Statuses: all 192 entries are (`PLANNED`, `UNVERIFIED`, `NOT_STARTED`, `NOT_RELEASED`) — the same tuple as base for every pre-existing entry.
- Generator-source diff (`s1_install_ops.py` +2/−1, `s2_identity.py` +31/−3) corresponds one-to-one with the JSON diff; the JSON is reproduced from those sources byte-for-byte (§1), so nothing in the JSON is hand-edited.
- `VZ-AUDIT-001`: area `identity`, source_kind `recommended_safeguard`, profiles core+full, deps `[VZ-ACCOUNT-002]` (exists, core+full, "Account export (all data) and deletion", owns `DELETE /api/v1/me`), cases success 3 / negative 3 / privacy 2 / recovery 3, surfaces api `DELETE /api/v1/me`, `GET /api/v1/admin/audit` (both already owned by VZ-ACCOUNT-002 / VZ-MOD-001 — consistent), ui `/admin/audit`, PLANNED/UNVERIFIED, `test_ids` and `evidence` empty.

## 3. Is VZ-AUDIT-001 true of the actual core design?

Read-only: `git -C /Users/yosefgamble/github/vizra/.claude/worktrees/core-m1-owner-claim show 56504c1:migrations/0005_users_credentials_owner_claim.up.sql`, `… show 56504c1:migrations/0003_audit_events.up.sql`, `… show 56504c1:scripts/migrate-lint.sh`. Core PR #8 head is still `56504c14683224cfd1fce0ecd7b826dcbf6de88d` (checked with `gh pr view 8 -R yegamble/vizra-core`), so 0005 is the bytes that will freeze.

**Does 0005 name an ID?** No. The ERASURE AND RETENTION paragraph says only: "The audited retention / anonymisation path is still owed and carries its own ledger ID." No `VZ-…` string appears in that paragraph, so there is no exact string the entry has to match; the chair's rulings ("a new ID for audit retention + user erasure") also name none. `VZ-AUDIT-001` was proposed by the backend seat (NEW-A: "Propose VZ-AUDIT-001") and does not collide with any existing prefix. The link is one-directional: the entry's `notes` point at 0005; 0005 will never point back (see F4). NEW-A's acceptance criterion — "at the merge SHA, features.json has an entry for audit retention/anonymisation" — is met by this PR.

Claim-by-claim against the DDL:

| VZ-AUDIT-001 statement | 0005 / 0003 at 56504c1 | Holds? |
|---|---|---|
| Widening via `CREATE OR REPLACE FUNCTION audit_events_append_only()` is additive and not matched by migrate-lint | Function exists (`CREATE FUNCTION audit_events_append_only() … RAISE … 42501`). migrate-lint pattern: `DROP\s+(TABLE\|COLUMN\|CONSTRAINT\|INDEX\|TYPE\|SCHEMA\|VIEW\|SEQUENCE)\|ALTER\s+TABLE…RENAME\|ALTER\s+TABLE…ALTER\s+COLUMN…TYPE\|TRUNCATE` (`grep -nEi`, every line). `CREATE OR REPLACE FUNCTION` does not match. | Yes — with the caveat in F3 (the bare word `TRUNCATE` anywhere in the new migration matches) |
| Row trigger and statement-level TRUNCATE trigger stay in place | `audit_events_no_update_or_delete` (BEFORE UPDATE OR DELETE, FOR EACH ROW) and `audit_events_refuse_truncation` (BEFORE TRUNCATE, FOR EACH STATEMENT) both call the same function; replacing the function body leaves both triggers | Yes |
| UPDATE, DELETE and TRUNCATE refused today | the function raises unconditionally | Yes |
| `DELETE FROM users` for a user named by an audit row fails, 23503 | `audit_events_actor_user_fk … REFERENCES users (id) ON DELETE RESTRICT` | Yes (RESTRICT raises foreign_key_violation 23503) |
| Erasure is scrub-and-tombstone, never DELETE | 0005 header: "Erasure is therefore scrub-and-tombstone of `users`, never DELETE"; `users.tombstoned_at` exists | Yes |
| `actor_user_id` still references the tombstoned row | FK + 0003 CHECK `(actor_kind='user') = (actor_user_id IS NOT NULL)` | Yes |
| No PII beyond the username in `before`/`after`/`actor_label` | 0005 header, verbatim rule; 0003 columns `before`, `after`, `actor_label` exist | Yes |
| Anonymisation also clears `ip_prefix` | 0003 `ip_prefix text NULL` (NULL allowed by `audit_events_ip_prefix_shape`) | Yes (feasible) |
| Erasure: "email NULLed" | 0005: `email text NOT NULL` | **Not as the schema stands** — needs an additive `ALTER COLUMN email DROP NOT NULL` first (F2) |
| Tombstoning the owner leaves the instance recoverable; claim endpoint stays closed | `users_one_owner … WHERE role='owner' AND tombstoned_at IS NULL`; 0005: "Tombstoning does NOT reopen the claim endpoint, because that gate is EXISTS(users)" | Yes |

Does the entry promise a mechanism 0005 forbids? It never proposes DELETE on `users`, `ON DELETE SET NULL`, an edit of 0003/0005, dropping a trigger, or an API route that mutates audit rows; it requires the triggers stay and TRUNCATE stay refused. The only statement not satisfiable against the frozen schema without a further (additive, un-annotated) migration is "email NULLed" (F2). Nothing it promises is forbidden.

## 4. VZ-ADMIN-USERS-001 against ADR-003

`docs/adr/ADR-003-identity-sessions-csrf-authorization.md` (Accepted by the owner 2026-09-20; identical at head and in the main checkout), lines 84–87: "Roles are an ordered enum on `users.role`: owner > admin > manager > member > guest … owner is single and cannot be demoted". `docs/PRODUCT_SPEC.md:24` repeats "Owner (single; cannot be demoted)".

- Tombstoned-owner recovery: consistent. No owner row is demoted (the tombstoned row keeps `role='owner'`); a live user is promoted; at most one LIVE owner (the index). "Single" holds for live owners, which is exactly the chair's row-1 ruling that 0005 implements.
- "Cannot demote the last owner" enforced application-side: consistent and TRUE of 0005 — a partial unique index can refuse a second live owner but cannot refuse zero, so demoting the only owner is not a database error.
- Negative cases (transfer by non-owner refused; to tombstoned/disabled/unknown refused; concurrent transfers leave one live owner, 23505→409): consistent with the index.
- **Owner transfer** (success case 2 and the appended outcome sentence): after it, "the previous owner holds the role the transfer names" — i.e. the previous owner is demoted, by their own act. That contradicts the literal Accepted text "cannot be demoted". The entry does not hide this: its `notes` records the reading "no other actor demotes the owner; the owner's own transfer is the only way the role moves", and the builder's plan hands it to the chair. But the note says "the implementing slice's plan review confirms that reading". In this repo, readings of Accepted ADR-003 have gone to the OWNER (rulings OQ-6 and OQ-10; board owner inbox 8b), and the rulings file states "Nothing here amends an Accepted ADR". A plan review cannot ratify an ADR interpretation. → F1.
- The chair's own ruling row 1 ("Owner transfer stays a later slice") and "Queued by the chair" ("owner-transfer obligation under VZ-ADMIN-USERS-001") are what put the obligation here; the builder executed the queued item faithfully.

## 5. Demonstrations, reproduced by the verifier at cd4c0f2 (base worktree at 6b8158c), `PYTHONDONTWRITEBYTECODE=1`

| Demo | Mutation | Red | Green (restored) |
|---|---|---|---|
| A | append `Demo A reference: VZ-AUDIT-001` to `docs/issues/README.md` | base 6b8158c: `check-quality-json.py` **exit 1** — `DANGLING REQUIREMENT ID(S): 1 id(s) reference nothing: VZ-AUDIT-001: not in docs/quality/features.json, referenced by docs/issues/README.md` | head cd4c0f2, same line: **exit 0** — `192 written reference(s) expanded to 288 id(s), 205 distinct … every one resolves`. File restored with `git checkout`; both trees clean. |
| B | `s2_identity.py`: `deps=["VZ-ACCOUNT-002"]` → `["VZ-ACCOUNT-999"]` (1 occurrence) | `build.py` **exit 1**, `StopIteration` traceback at `build.py:27` (`dep = next(x for x in reqs if x["id"]==d)`); through the lane, `check-generated-ledger.sh` **exit 1** `GENERATOR FAILED: … exited non-zero` | restored: `build.py` exit 0, `OK 192 requirements; core=142`, output `cmp`-identical to committed `features.json`; `check-generated-ledger.sh` exit 0 |
| C | `features.json`: VZ-AUDIT-001 `implementation_status` PLANNED → IMPLEMENTED | uncommitted: **exit 1** `DIRTY WORKING TREE`; committed locally (scratch clone only, never pushed): **exit 1** `GENERATED FILE IS NOT REPRODUCIBLE … docs/quality/features.json` with the diff shown | `git reset --hard cd4c0f2…` → HEAD verified, tree clean, **exit 0** byte-for-byte |

All three reproduce for the stated reason. (The builder's transcript ran them at `dd7955e`; `cd4c0f2` changes only docs, and I ran them at `cd4c0f2`.)

## 6. Scope

`git diff --name-only 6b8158c cd4c0f2`: `docs/evidence/ledger-generator/{README.md,s1_install_ops.py,s2_identity.py}`, `docs/evidence/warroom/meta-m1a-ledger-builder-transcripts/2026-09-23-red-green-demos.txt`, `docs/plans/2026-09-23-meta-ledger-m1a-obligations.md`, `docs/quality/COMMANDS.md`, `docs/quality/features.json`. No `.github/` file and no `required-checks.txt` touched. Count edits in COMMANDS.md and the generator README match what I observed (192 / core=142; check 2's "191 written reference(s) … 287 … 204" is the value actually printed at head, not a stale number).

## 7. PR-body and plan claims

| Claim | Observed |
|---|---|
| 191 → 192, core 141 → 142, only VZ-AUDIT-001 added | Yes |
| Generator sources only; nothing hand-edited; all PLANNED/UNVERIFIED | Yes (byte-for-byte regeneration under 3.9.6 and 3.12.11, both locales) |
| INSTALL-003 recovery sentence and boot-mint outcome unchanged | Yes, byte-identical |
| ADMIN-USERS-001 outcome verbatim + one sentence; base negative kept | Yes |
| Lane exit 0 at HEAD; 4 JSON / 192 ids / 191→287 (204) / 14 docs; 95 md files, 7 URLs; fixtures 6/7/10 | Yes, all reproduced |
| Demos A/B/C | Reproduced (§5) |
| "Core PR #8's migration 0005 … cites item 1" | Overstated: 0005 names no ID (F4) |
| "`ci-required` has no result for this head" | Inaccurate: it has a **failure** result with 0 steps (billing) — still not a pass (F4) |
| Builder finding 1 (StopIteration) | Reproduced (§5 Demo B). Pre-existing; exit code still non-zero, lane script names `GENERATOR FAILED` |
| Builder finding 2 (Apple bytecode cache) | `/usr/bin/python3 -c 'import sys; print(sys.pycache_prefix)'` → `/Users/yosefgamble/Library/Caches/com.apple.python` (mechanism exists). The one-second stale-bytecode race itself not reproduced by me; all my runs used `PYTHONDONTWRITEBYTECODE=1` in a fresh clone |
| Builder finding 3 (COMMANDS.md URL count) | Confirmed: COMMANDS.md:177 and :188 say 6 external URLs; the checker prints 7 at base and at head. Pre-existing |

No instruction-shaped text appeared in any tool output during this run.

## 8. Findings

None of these blocks this PR. F1 needs a chair action before any slice that implements owner transfer is dispatched; it does not need a change to this PR's head.

```
FINDING 1: the owner-transfer obligation contradicts ADR-003's literal "cannot be demoted", and the entry names a plan review as the ratifier instead of the owner
Severity:    REQUIRED (before the implementing slice is dispatched; NOT a merge blocker for this PR)
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-generator/s2_identity.py (VZ-ADMIN-USERS-001 outcome, success[1], notes);
             docs/quality/features.json VZ-ADMIN-USERS-001;
             docs/adr/ADR-003-identity-sessions-csrf-authorization.md:86-87; docs/PRODUCT_SPEC.md:24
  requirements: VZ-ADMIN-USERS-001, VZ-AUTH-004

Observed:
  ADR-003 (Accepted by the owner): "owner is single and cannot be demoted". PRODUCT_SPEC:24:
  "Owner (single; cannot be demoted)". New success case: "Owner transfer: … afterwards exactly one
  live owner exists, the previous owner holds the role the transfer names". New note: "this entry
  reads that as 'no other actor demotes the owner' … the implementing slice's plan review confirms
  that reading." The rulings file: "Nothing here amends an Accepted ADR"; OQ-6 and OQ-10, the
  previous ADR-003 readings, were sent to the OWNER (board owner inbox 8b). No inbox item covers this one.

Failure:
  After merge, the acceptance ledger requires a behaviour (the owner demoting themselves via transfer)
  that the Accepted ADR and product spec literally forbid, and it names a non-owner review as the
  ratifier. A builder could implement and ship transfer on a plan-review sign-off. The tension is
  disclosed in the note, not hidden, and the entry is PLANNED.

Perspective: instance-admin, developer

Recommendation:
  The chair adds an owner-inbox item (like 8b): "ADR-003 'owner … cannot be demoted': read it as
  'no other actor demotes the owner; the owner's own transfer is the only way the role moves'?". In a
  later generator edit, change the note's last clause to "pending owner ratification (owner inbox
  <n>)". Until the owner answers, the transfer success case is conditional.

Acceptance criteria:
  - WARROOM-BOARD owner inbox has the item.
  - VZ-ADMIN-USERS-001 notes cite the owner inbox, not a plan review.
  - No slice implementing owner transfer is dispatched before the owner answers.

Tests: none (ledger/governance state). The implementing slice's tests are already listed in the entry.
Cross-repo implications: core: the owner-transfer slice waits on the ruling | user: /admin/users transfer control likewise | search: none | meta: board + one generator edit
Challenge:
  The chair's own ruling row 1 queued owner transfer, so the chair has already accepted that it
  exists. A voluntary hand-over is arguably not a "demotion". And the tombstoned-owner recovery path
  covers the brick case without any transfer. That is exactly why the owner should say which reading holds.
```

```
FINDING 2: VZ-AUDIT-001's erasure case says "email NULLed", but 0005 makes users.email NOT NULL
Severity:    SHOULD
Confidence:  high (from reading the DDL; not executed — I started no PostgreSQL container per the brief)

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-generator/s2_identity.py (VZ-AUDIT-001 success[2], privacy[1]);
             vizra-core@56504c1 migrations/0005_users_credentials_owner_claim.up.sql (users table)
  requirements: VZ-AUDIT-001, VZ-ACCOUNT-002

Observed:
  0005: `email text NOT NULL`; `username text NOT NULL` with users_username_shape CHECK and the
  users_username_fold_key unique index. VZ-AUDIT-001 success[2]: "scrubs and tombstones the users row —
  email NULLed, credentials removed, tombstoned_at set — and anonymises that user's username in the
  audit rows". privacy[1]: "after erasure the user's username … not reachable from the audit read surface".

Failure:
  Against the frozen schema, `UPDATE users SET email = NULL` raises 23502. An implementer following the
  ledger literally hits a NOT NULL violation. The path is not forbidden: 0005 names
  `ALTER COLUMN email DROP NOT NULL` as additive, users_email_fold_key is already partial, the email
  shape CHECK passes on NULL, and migrate-lint's pattern does not match DROP NOT NULL (checked). But
  the entry does not name that prerequisite. Separately: actor_user_id still joins to users.username,
  so the privacy case also needs the users row's username replaced (a placeholder satisfying the shape
  CHECK). The success case lists only email, credentials and tombstoned_at.

Perspective: developer, member (erasure subject)

Recommendation:
  Next generator edit: "email NULLed (after an additive `ALTER COLUMN email DROP NOT NULL`) or
  replaced with a non-identifying placeholder; username replaced with a non-identifying handle that
  satisfies users_username_shape".

Acceptance criteria:
  The VZ-AUDIT-001 text names either the schema prerequisite for NULL email or a placeholder, and
  scrubs users.username as well as the audit rows.

Tests: the entry's own migration test on real PostgreSQL, plus an erasure test asserting that users.email,
  users.username and credentials hold no original value after scrub.
Cross-repo implications: core: one additive migration in the erasure slice | user: none | search: none | meta: generator edit
Challenge:
  The ledger states intent, not DDL, and the slice would discover the constraint at once. True. It is
  still a statement about a frozen schema that is false as written.
```

```
FINDING 3: "needs no -- allow-destructive: annotation" holds only if the new migration never contains the bare word TRUNCATE
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra
  files:     VZ-AUDIT-001 success[0]; vizra-core@56504c1 scripts/migrate-lint.sh:92,106
  requirements: VZ-AUDIT-001

Observed:
  destructive='…|TRUNCATE', applied with `grep -nEi` to every line of an up migration, including comments
  and function bodies. The natural widened body `IF TG_OP = 'TRUNCATE' THEN RAISE …` matches.

Failure:
  The success case can be false for a correct implementation. The entry's own evidence_required ("migrate-lint
  transcript showing the widening is not classed destructive") would flag it, so no harm lands.

Perspective: developer
Recommendation: Optional wording: "…is not matched, provided the new body refuses by default rather than naming TRUNCATE (or carries an allow-destructive line)".
Acceptance criteria: wording adjusted or left as is by chair decision.
Tests: none.
Cross-repo implications: none
Challenge: 0005 itself makes the same claim in the same words; the ledger faithfully mirrors it.
```

```
FINDING 4: the PR body overstates two facts
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra
  files:     PR #5 body ("Core PR #8's migration 0005 … cites item 1"; "ci-required has no result for this head")
  requirements: VZ-AUDIT-001

Observed:
  0005 names no ledger ID ("carries its own ledger ID"). `ci-required` has a completed FAILURE check run
  on cd4c0f2 (run 35836746627, not started for billing), not "no result".

Failure:
  The ID mapping is one-directional: a reader of 0005 cannot find VZ-AUDIT-001 without searching the
  ledger. Both statements are narrative, not evidence, and neither changes a result.

Perspective: developer
Recommendation:
  The chair records "0005 'its own ledger ID' = VZ-AUDIT-001" on board owner inbox 8c when merging. Any
  later core docs change that touches the audit path cites VZ-AUDIT-001. 0005 itself must not be edited.
Acceptance criteria: board 8c names VZ-AUDIT-001.
Tests: none.
Cross-repo implications: core: none (0005 frozen) | meta: board line
Challenge: The ledger note already makes the mapping, and ledger search is how IDs are found.
```

```
FINDING 5: builder-reported pre-existing issues, confirmed
Severity:    NIT (all pre-existing at base 6b8158c, out of this slice's scope)
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-generator/build.py:27; scripts/check-generated-ledger.sh; docs/quality/COMMANDS.md:177,188

Observed:
  (a) An unknown dependency on a core-profile entry raises StopIteration at build.py:27 before the collected
      "unknown dependency" error prints. Exit 1 and the lane's GENERATOR FAILED message still hold (Demo B).
  (b) Apple /usr/bin/python3 sys.pycache_prefix = ~/Library/Caches/com.apple.python (the stale-bytecode race
      itself not reproduced by me).
  (c) COMMANDS.md records 6 external URLs; check-doc-links.py prints 7 at base and at head.
Recommendation: `next(…, None)` guard in build.py; `export PYTHONDONTWRITEBYTECODE=1` in
  check-generated-ledger.sh; correct the URL count. A separate slice for each (the check script is owner-reviewed).
Acceptance criteria: (a) the unknown-dependency message prints with no traceback; (b) the script exports the variable; (c) the count matches the checker.
Tests: the fixture-driven demos in COMMANDS.md.
Cross-repo implications: none
Challenge: CI runs on a fresh runner with no bytecode cache, and the gate never fails open, so (a) and (b) are ergonomics only.
```

Also noted, not a finding: the `notes` of all three entries cite `docs/evidence/warroom/2026-09-21-vizra-core-m1a-owner-claim-PLAN-RULINGS.md`, which is on the chair's records branch and not on `main`. It is text in JSON, so no link check covers it. It resolves once the records branch lands.

## Verdict

- Every in-scope acceptance item reproduced locally at `cd4c0f2`: generator, byte-for-byte reproduction (Python 3.9.6 and 3.12.11, UTF-8 and C/POSIX), all validate-lane and guard scripts exit 0, and demonstrations A, B and C red for the stated reason and green once restored.
- The features.json diff is additions only, plus the two stated appends. No requirement is narrowed, removed or re-scoped. Statuses are unchanged. The INSTALL-003 recovery sentence is byte-identical.
- VZ-AUDIT-001 is true of 0005/0003 at 56504c1 except "email NULLed" (F2). It promises nothing 0005 forbids, and it satisfies NEW-A's acceptance criterion. 0005 names no ID string.
- Scope is clean: no workflow or manifest edit.
- CI: `validate` and `ci-required` are FAILURE with 0 steps because of billing. CI is BLOCKED, and that is not a pass. The merge rule in AGENTS.md requires `ci-required` green on the verified SHA, so this verdict does not by itself meet the merge authorization.
- Open for the chair: F1 (owner-inbox item before the owner-transfer slice), F2 (next generator edit), F3–F5 (nits).

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA cd4c0f2dddbe1616fa525fc5a4be9633ca4dfd86
