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
Preflight (2026-09-23, macOS arm64): python3 3.9.6 (also 3.10.20, 3.13.13), gh 2.98.0 authenticated,
git 2.50.1, docker compose 5.5.1, PyYAML 6.0.3. Nothing BLOCKED. CI target: ubuntu-24.04, Python 3.12.14.

Baseline at `b2c5b96` before any edit: check-generated-ledger 0, check-quality-json 0,
check-doc-links 0, ci-required-guard 0.

Code commit `94ac3bf`. Full local lane at `94ac3bf` (transcripts in scratch; the ledger-status ones
are copied to `docs/evidence/ledger-status/`):

| Step | Command | Exit | Result |
|---|---|---|---|
| a | `./scripts/check-generated-ledger.sh` | 0 | reproduces byte-for-byte (UTF-8 and C/POSIX) |
| a2 | `(cd docs/evidence/ledger-generator && python3 -m unittest -v test_status)` | 0 | 30 tests, 0 skipped |
| a2 | `./scripts/check-ledger-status-remote.py --self-test` | 0 | 8/8 cases as expected |
| a2 | `./scripts/check-ledger-status-remote.py` | 0 | 0 records |
| a2 | `bash docs/evidence/ledger-status/demo.sh` | 0 | 26 passed, 0 failed; tree restored |
| b | `./scripts/check-quality-json.py` | 0 | 204 distinct ids resolve |
| c | `./scripts/check-doc-links.py` | 1 → 0 | red only because the README linked transcripts not yet written; 0 once they existed |
| d | compose render / topology / config coverage / template claims | 0 / 0 / 0 / 0 | unchanged by this slice |
| d | `bash docs/evidence/compose-topology/demo.sh` | 1 | same cause as (c): its baseline runs doc-links, and it found the untracked transcripts being written during the run. Re-run on the final head below |
| ci-required | `./scripts/ci-required-guard.sh` | 0 | validate.yml edit accepted (pins, lane integrity, no continue-on-error) |

**Re-run of the full lane on `81da01e`** (the head with transcripts, local, load average ~100):
every step exits 0.
- ledger: reproduces byte-for-byte.
- unit: 30 tests, 0 skipped.
- self-test: 8/8.
- remote: 0 records.
- ledger demo: 26 passed / 0 failed.
- quality-json: 204 ids.
- doc-links: 0.
- render, topology (27 rules, 0 violations), config coverage, template claims: 0.
- compose demo: 95 assertions passed, 0 failed, tree clean.
- ci-required-guard: 0.

Generator output is byte-identical under Python 3.9.6, 3.10.20 and 3.13.13.

Demonstrations (red, then green on restore): `docs/evidence/ledger-status/demo-transcript.txt`.
- D1: VERIFIED with no evidence file; a status set in a section source; a hand-edited and committed
  `features.json`.
- D2: verdict SHA mismatch, FAIL as the final line, missing file.
- D3: IMPLEMENTED on a merge commit not on main (online).
- D4: `DONE` / `IN_PROGRESS` / `VERIFIED_AT_SHA`.
- D5: the floors.

Checker mutation tests: `unit-mutations.txt` (5/5 caught) and `remote-mutations.txt` (4/4 caught).

Candidates: `candidates.txt`, with the decision table in `docs/evidence/ledger-status/README.md`.
**Zero records committed.**
- VZ-FOUND-007: VZ-ISSUE-006 floor; the evidence has no final verdict line; the ledger outcome is
  wider than the M0 twelve.
- VZ-FOUND-008 via user #8: passes every mechanical rule, but is withheld because the outcome needs a
  real API/PostgreSQL/Redis and axe checks, and neither exists.
- VZ-INSTALL-003: ui floor (no `/setup/claim` in vizra-user).

## Blockers and handoff
- No external blocker.
- CI decides whether the default `GITHUB_TOKEN` can read the component repositories. They are
  public, so it should. If it cannot, step (a2) goes red naming the `gh api` error; that is a finding
  for the chair, and the token scope must not be weakened.
- Decisions for the chair:
  1. Whether a partial status is wanted. This slice refuses one.
  2. The VZ-FOUND-008 issue bullet is narrower than its ledger outcome.
  3. Two evidence files need a `FINAL VERDICT` line (board follow-up F3), written by their verifiers:
     core #5 and user #3.
- The candidate attempts (`candidates.txt`) read three evidence files from the chair's records
  branch `chore/warroom-records-2026-09-21` at `b331f63` with `git show`, into a scratch copy only.
  This PR adds and edits no evidence file written by another agent. A future VERIFIED record needs
  its evidence file on `main` first, which means the records branch must land.

## Fix round 1 (verifier FAIL at 36913d2, `docs/evidence/warroom/2026-09-23-meta-pr6-ledger-status-VERIFY.md` on the chair's records branch)

The verifier upheld all three candidate refusals and reproduced every lane and D1–D5. Its findings and what closed each:

- **REQUIRED 1** (probes 2c extra key, 2d `str` subclass, 2e wrapper: each a status with zero
  records and the lane green). This slice guarded the INPUT path in-process. The fix guards the
  OUTPUT, out of process: `scripts/check-ledger-status-output.py`, its own `validate` step. It
  - parses the committed `features.json` as plain JSON and imports no section source;
  - requires the tree to match HEAD for the ledger, records, issues and war-room evidence;
  - requires the exact `core.req` key set, pinned to `core.req` by a unit test;
  - requires the ids with a non-default status or evidence to equal the record ids;
  - re-derives every entry from defaults plus the committed records and compares the whole entry;
  - requires the summary counts to match.

  The DSL check now requires `type(got) is str`. Demonstrations D6a / D6b-i / D6b-ii / D6c: for each
  escape, the generator and the regeneration check are green (the escape is real), and the output
  check is red naming it. After a reset it is green (`demo-transcript.txt`). `output-mutations.txt`:
  the key-set check is load-bearing for 2c; set-equality and re-derivation are redundant for 2d/2e.
- **REQUIRED 2**:
  - self-test case `merged-into-a-non-main-branch` (vizra#3: head `f9b85537`, merge `4920786`);
  - `scripts/test_ledger_status_remote.py` (9 tests, injected `gh_api`), covering the non-Actions
    `ci-required`, the base branch, the latest run deciding, in-progress, and anonymous auth.

  `guard-mutations.txt`: deleting the base guard turns the unit test and the self-test case red;
  deleting the app filter turns 2 unit tests red.
- **REQUIRED 3**: narrowed the README, the `status.py` header and rule 1, the `features.json`
  notice (regenerated) and `validate.yml` clause (e) to what is measured. Each now says a PR that
  edits the checkers is not defended, and that the lane runs on PRs and merge-queue entries only.
- **SHOULD 4**: the verdict qualifier is an allowlist (`(local; CI BLOCKED)` only). D7 shows
  `PASS (superseded — FAIL on re-run)` red.
- **NIT 1**: README wording fixed. **NIT 2**: where an issue tags its bullets with ids, the cited
  bullet must name the record's requirement (D8). **NIT 3**: the remote checker proves `gh` is
  authenticated (`rate_limit` core limit above 60) even with zero records; it exits 2 otherwise.

Round-1 local evidence at `19ba567` (tests, demo, mutations): unit 35 + 9, self-test 9/9, output
check 0, demo 47 passed / 0 failed. The full-lane table for the pushed head follows.

**Full local lane at `f32f9a8`** (macOS arm64, Python 3.9.6, gh 2.98.0), every step exit 0:
- `check-generated-ledger.sh`: byte-for-byte;
- `check-ledger-status-output.py`: 192 entries, 0 statuses, 0 records;
- unit: 35 offline plus 9 online, 0 skipped;
- remote: self-test 9/9, 0 records;
- ledger demo: 47 / 0;
- quality-json: 204 ids;
- doc-links;
- compose render / topology (27 rules, 0 violations) / config coverage / template claims;
- compose demo: tree clean;
- `ci-required-guard.sh`.
