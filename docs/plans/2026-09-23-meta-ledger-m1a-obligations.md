# Execution plan: ledger entries the chair owes the M1-A owner claim (VZ-AUDIT-001 new; VZ-INSTALL-003 and VZ-ADMIN-USERS-001 additive)

## Context
- Repo: `yegamble/vizra` (meta). Base `origin/main` at `6b8158c`. Branch `docs/m1a-ledger-obligations`, worktree `.claude/worktrees/meta-ledger-m1a`.
- Brief: war-room tick 136 slice "meta: ledger entries the chair owes M1-A".
- Source of the obligations: the chair's M1-A plan rulings, `docs/evidence/warroom/2026-09-21-vizra-core-m1a-owner-claim-PLAN-RULINGS.md` (rows 1, 2, 4; OQ-3, OQ-7, OQ-9, OQ-11; "Queued by the chair"). That file lives on the chair's records branch and is not on `origin/main` at `6b8158c`, so it is cited by path, not linked.
- Consumer: vizra-core PR #8, migration `migrations/0005_users_credentials_owner_claim.up.sql` (read at core worktree head `56504c1`, read-only), whose header says the audited retention / anonymisation path "carries its own ledger ID". This slice makes that sentence true.

## Acceptance
1. A new requirement for audit retention and actor anonymisation exists, PLANNED/UNVERIFIED, with success/negative/privacy/recovery cases covering: additive widening of `audit_events_append_only()` via `CREATE OR REPLACE FUNCTION`; erasure as scrub-and-tombstone of `users`, never DELETE; audit rows never carrying PII beyond the username; a dependency on `VZ-ACCOUNT-002`.
2. `VZ-INSTALL-003.surfaces.api` gains `GET /api/v1/setup/claim-status` (OQ-3); `.surfaces.cli` gains `vizra claim-token` (OQ-9).
3. `VZ-ADMIN-USERS-001` gains an owner-transfer and tombstoned-owner recovery obligation, and states that "cannot demote the last owner" is enforced application-side (`users_one_owner` permits at most one LIVE owner; it refuses a second, not zero).
4. `VZ-INSTALL-003`'s recovery sentence is NOT changed; a `notes` line points at owner inbox 8a and the chair's interim ruling (the schema has a `notes` field: `core.py` `req(..., notes=None)`).
5. Additions only: no existing string removed or narrowed; the generator's PLANNED/UNVERIFIED gate (`build.py`) kept.
6. Requirement count goes from 191 to exactly 192.

Non-goals: the recovery-sentence rewrite (owner inbox 8a), PRODUCT_SPEC §15 step 4 and copy key `claim.help.body` (a separate meta docs slice), any vizra-core change.

## ID choice
`VZ-AUDIT-001`. The ledger's scheme is `VZ-<CAPABILITY>-<NNN>` where the prefix names the capability, independent of the `area` field (e.g. `VZ-ADMIN-USERS-001` sits in area `identity`). No existing prefix owns audit-trail lifecycle: `VZ-PRIVACY-*` are asset-visibility controls, `VZ-SECURITY-*` are Chevereto-parity abuse/secret rows, `VZ-ADMIN-001`/`VZ-MOD-001` own the audit LOG surfaces, not its retention. `AUDIT` is the name both council seats already used (security review of core PR1: "propose VZ-AUDIT-00x"; M1-A security plan review: "VZ-AUDIT/0003 deferred obligation"). `001` because the prefix is new. Area `identity`, beside `VZ-ACCOUNT-002` and `VZ-ADMIN-USERS-001`, because the entry is driven by user erasure. Profiles core+full: `audit_events` exists from M0 and its dependency `VZ-ACCOUNT-002` is core, so core closure holds.

## Implementation
Generator sources only (`docs/evidence/ledger-generator/`):
- `s2_identity.py`: extend `VZ-ADMIN-USERS-001` (outcome sentence appended; cases added; notes added); add `VZ-AUDIT-001` after it.
- `s1_install_ops.py`: `VZ-INSTALL-003` api/cli surfaces appended; notes added.
- Regenerate `docs/quality/features.json` with `(cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json)`.
- Recorded counts that go stale: `docs/quality/COMMANDS.md` "Last run" lines and the generator `README.md` "Last run" line are updated to the numbers this slice actually observes.

## Verification
Preflight (2026-09-23, macOS arm64): `python3 --version` → Python 3.9.6; PyYAML 6.0.3; git 2.50.1. No Docker/database/browser needed (COMMANDS.md). CI: BLOCKED by account billing per the brief; local evidence only.

Commands (from repo root of the worktree):
1. `(cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json)`
2. `./scripts/check-generated-ledger.sh`
3. `./scripts/check-quality-json.py`
4. `./scripts/check-doc-links.py`
5. `./scripts/ci-required-guard.sh` and its three checkers (the rest of the documented local lane set)
6. ID-count diff: base 191 vs head, and the set difference of ids.
7. Additions-only check: every string in every base entry's cases/surfaces is still present at head, and base outcomes are prefixes of head outcomes.
8. Demonstration: a reference to `VZ-AUDIT-001` in an issue file is RED against the base ledger and GREEN against the head ledger (scratch, not committed).

## Progress and evidence
(appended below as commands run)

## Blockers and handoff
- CI: BLOCKED (billing) — no Actions run is expected for this PR.
