# Execution plan: meta queue 2i — the ledger can record status, but only with evidence

## Context
- Repo: `yegamble/vizra` (meta). Branch `feat/m0-ledger-status`, worktree
  `.claude/worktrees/meta-ledger-status`, based on `origin/main` at
  `b2c5b96c8dc19d7f6b4f55b5dd649a75461dbf71` (includes meta #4 compose and #5 VZ-AUDIT-001).
- Brief: war-room queue 2i. Candidates named by the chair: VZ-FOUND-007 (core #5),
  VZ-FOUND-008 (user #3 / user #8), VZ-INSTALL-003 (core #8). NITs R-N1 / R-N2 from
  `docs/evidence/warroom/2026-09-23-meta-pr5-ledger-m1a-VERIFY.md` (chair records branch).
- Contract: `AGENTS.md` § Completion and evidence (IMPLEMENTED / VERIFIED are different states;
  "No feature is VERIFIED merely because…"; release state is separate and never touched here).
- Before this slice `build.py` refused every status other than PLANNED/UNVERIFIED. There was no
  way to record a status at all, honestly or otherwise.

## Acceptance
1. A status reaches `docs/quality/features.json` only from a committed status record, checked
   mechanically by the `validate` lane. It can never be hand-asserted:
   - a status written into a section source (the DSL) is refused by name;
   - a hand-edited `features.json` is refused by the existing regeneration check;
   - a record may claim only `IMPLEMENTED` or `VERIFIED`; every other value is refused by name.
2. `IMPLEMENTED` requires, per merge in the record, a PR that GitHub reports merged into `main`
   whose head is the recorded verified head and whose merge commit is the recorded merge commit,
   and that merge commit must be on the component repo's `main` (checked online in CI with
   `gh api`).
3. `VERIFIED` additionally requires, per merge, an evidence file under `docs/evidence/warroom/`
   whose final non-empty line is `FINAL VERDICT: PASS … — SHA <40-hex>` with that SHA equal to
   the recorded verified head, **and** the most recent `ci-required` check-run on that head
   `completed/success` (a "PASS (local; CI BLOCKED)" verdict alone never proves CI).
4. Default-deny: unknown status, unknown key, missing or mismatched file, malformed SHA, API
   error, missing `gh` → the lane is red.
5. Only the statuses today's evidence supports are recorded; release state untouched.
6. VZ-AUDIT-001 carries R-N1 and R-N2.

Non-goals: no partial ("half") status; no change to the required-check manifest; no edit of any
evidence file written by another agent.

## Implementation
- `docs/evidence/ledger-generator/status.py` — offline rules (DSL defaults, record schema,
  verdict line, surface and issue floors), applied by `build.py`.
- `docs/evidence/ledger-generator/status_records.json` — the only source of a status.
- `scripts/check-ledger-status-remote.py` — online facts via `gh api`; `--self-test` runs
  committed fixtures (`scripts/testdata/ledger-status/`) whose outcomes are asserted.
- `docs/evidence/ledger-status/demo.sh` — red/green demonstrations, also run in CI.
- `.github/workflows/validate.yml` — three steps added to the existing `validate` job.
- `s2_identity.py` — R-N1 / R-N2 wording.

## Verification
See "Progress and evidence".

## Progress and evidence
(appended below as work proceeds)

## Blockers and handoff
(appended below)
