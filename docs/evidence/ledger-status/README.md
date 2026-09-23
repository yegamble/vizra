# Ledger status: recorded only with evidence (war-room queue 2i)

`docs/quality/features.json` can now carry `IMPLEMENTED` or `VERIFIED`, but only when a record in
[`status_records.json`](../ledger-generator/status_records.json) admits it and the `validate` lane
proves that record. Nobody can write a status by hand. Release state is never set.

## Why a committed record proved online

The generator has to stay reproducible offline. `scripts/check-generated-ledger.sh` regenerates it
under two locales and diffs the bytes, and the component repositories are not checked out in this
lane. So the rule is split in two, and both halves read the record through the same loader
(`status.load_records`):

| Half | Where | Proves |
|---|---|---|
| offline | [`status.py`](../ledger-generator/status.py), run by `build.py` inside step (a) | no section source sets a status; the record's shape; status is `IMPLEMENTED` or `VERIFIED` (anything else is refused by name); full 40-hex SHAs; for `VERIFIED`, each merge's evidence file under `docs/evidence/warroom/` **ends** with `FINAL VERDICT: PASS[ (…)] — SHA <40-hex>` naming that merge's `verified_head`; the floors below |
| online | [`scripts/check-ledger-status-remote.py`](../../../scripts/check-ledger-status-remote.py), step (a2) | per merge: the PR is merged into `main`; GitHub's head for it is `verified_head`; GitHub's merge commit is `merge_commit`; `compare/<merge_commit>...main` is `ahead`/`identical` (on main now); for `VERIFIED`, the latest GitHub Actions `ci-required` check-run on `verified_head` is `completed/success` |

A hand-edited `features.json` is still caught by the regeneration diff (demonstration D1c).

Because the record is committed, a reviewer sees it in the PR diff. Because the online half runs
again on every PR, a record that was true when it was written and stops being true later (a
force-pushed main, a PR re-opened) turns the lane red instead of staying green.

**VERIFIED requires `ci-required` green on the verified head.** A verifier's
`PASS (local; CI BLOCKED)` passes the offline verdict check only because the online half then asks
GitHub for `ci-required` on the same SHA. A local PASS on its own never stands in for CI. That
matches the merge rule in `AGENTS.md`.

**Floors.** These stop a component half being recorded as the whole requirement. They set a
minimum and do not prove the requirement is complete:
- a requirement with a `ui` surface needs a `vizra-user` merge;
- a requirement with an `api` surface needs a `vizra-core` merge;
- every `docs/issues/*.md` whose `**Ledger IDs:**` line names the requirement must be cited, with at
  least one bullet quoted verbatim from its `## Acceptance` section.

Whether the merges deliver the **whole ledger outcome** is still a judgement, written in the
record's `rationale` and reviewed by a person.

## Decision on the chair's three candidates (2026-09-23): none recorded

Every fact below comes from `gh api` in this session. The attempts ran in a scratch copy and are in
[`candidates.txt`](candidates.txt).

| Candidate | Merge facts (online half) | Offline half | Recorded? |
|---|---|---|---|
| VZ-FOUND-007, core #5 `56920fe` → `c043df7` | merged, on main; `ci-required` success (check-run 106186425769) | **red**: `VZ-ISSUE-006` also schedules VZ-FOUND-007, and the record can cite only VZ-ISSUE-001. `VERIFIED` is also red: `2026-09-21-vizra-core-pr5-fixtures-VERIFY.md` has no `FINAL VERDICT` line (board follow-up F3) | **No.** The ledger outcome includes ICC wide-gamut, MP4/MOV/WebM and equirectangular 360. The core #5 verifier measured zero ICC profiles in the twelve M0 fixtures. The M1 part is VZ-ISSUE-006. |
| VZ-FOUND-008, user #3 `3b566c3` → `f49bca4` | merged, on main; `ci-required` success (106171959382) | **red for VERIFIED**: `2026-09-20-vizra-user-pr3-browser-env-VERIFY.md` has no `FINAL VERDICT` line | **No** (see next row) |
| VZ-FOUND-008, user #8 `c2ff445` → `7a3a572` | merged, on main; `ci-required` success (107288308319) | **green**: the final line is `FINAL VERDICT: PASS (local; CI BLOCKED) — SHA c2ff4454…` | **No — withheld by judgement.** The mechanical rules would admit it. But the ledger outcome says the E2E runs "against the production Next.js build **and real API/PostgreSQL/Redis** … **axe checks**". `vizra-user` main has neither: `package.json` has no axe dependency, and the harness drives the Next build alone. User #8's verifier judged the artifact-privacy follow-up, and its V-D finding is still open. The VZ-ISSUE-001 bullet was met, but that bullet is narrower than the ledger entry. |
| VZ-INSTALL-003, core #8 `0cc906e` → `f1972e8` | merged, on main; `ci-required` success (107288249394); the evidence ends `PASS (local; CI BLOCKED) — SHA 0cc906ed…` | **red**: the `ui` surface `/setup/claim` needs a `vizra-user` merge, and there is none. `vizra-user` main has no claim page. | **No.** The core half (API + `vizra claim-token`) is done and verified. The claim page is not built. The recovery case "Restart re-mints" is also still pending owner inbox 8a. |

So `status_records.json` holds zero records and all 192 entries stay PLANNED/UNVERIFIED. **No
partial status exists.** Recording "the core half" or "the M0 part" would need a chair ruling on
a new vocabulary value (for example a derived `IN_PROGRESS` that makes no completeness claim). This
slice deliberately refuses that.

## Demonstrations

`bash docs/evidence/ledger-status/demo.sh` also runs in CI (step "every ledger-status guard still
fails against a controlled mutation"). Each case prints the file's sha256 before and after the
mutation and refuses to score a mutation that did not apply. The tree must be restored at the
end. Transcript: [`demo-transcript.txt`](demo-transcript.txt).

| Case | Mutation | Red names | Green |
|---|---|---|---|
| D1a | VERIFIED record, evidence file removed | `VERIFIED with NO EVIDENCE` | restored fixture record admitted |
| D1b | a section source sets `implementation_status = "VERIFIED"` | `HAND-ASSERTED implementation_status 'VERIFIED' in a section source` | source restored |
| D1c | `features.json` hand-edited to VERIFIED and committed (scratch copy) | `GENERATED FILE IS NOT REPRODUCIBLE` | commit reverted |
| D2a | verdict line names another head of the same PR | `VERDICT SHA MISMATCH` | restored |
| D2b | a later `FINAL VERDICT: FAIL` becomes the final line | `does not END with a PASS verdict` | restored |
| D2c | evidence file path that does not exist | `MISSING EVIDENCE FILE` | restored |
| D3 | IMPLEMENTED, merge commit = an earlier head of user #8 (not on main) | `is NOT on yegamble/vizra-user main` | the true merge commit `7a3a572` proved |
| D4 | status `DONE`, `IN_PROGRESS`, `VERIFIED_AT_SHA` | `status '<x>' is REFUSED` | restored |
| D5a | VZ-INSTALL-003 with only a core merge | `names no vizra-user merge` | restored |
| D5b | VZ-FOUND-007 citing only VZ-ISSUE-001 | `docs/issues/VZ-ISSUE-006.md schedules VZ-FOUND-007` | restored |

The checkers are themselves mutation-tested:
- [`unit-mutations.txt`](unit-mutations.txt): five mutations of `status.py`, and each turns a named unit test red.
- [`remote-mutations.txt`](remote-mutations.txt): four mutations of the online checker, and each turns a named self-test case red.

Unit tests: [`unit-tests.txt`](unit-tests.txt). Self-test: [`remote-self-test.txt`](remote-self-test.txt).
