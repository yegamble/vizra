# Ledger status: recorded only with evidence (war-room queue 2i)

`docs/quality/features.json` can now carry `IMPLEMENTED` or `VERIFIED`, but only when a record in
[`status_records.json`](../ledger-generator/status_records.json) admits it and the `validate` lane
proves that record. Release state is never set.

**How far this is enforced, as measured.** A status in the committed `features.json` that no
committed record admits turns the lane red, and this holds however the status was produced:
- a hand edit;
- a section source assignment;
- an extra key;
- a `str` subclass;
- a generator monkeypatched in-process;
- a replaced `json.dump` that writes a duplicate status key before the real one (round 2: duplicate
  keys are refused at every level, and the bytes must equal the output check's re-serialisation of
  its own parse with the generator's settings; bytes the generator itself would not write, such as
  `192.0` for `192`, pass that comparison and are refused by the regeneration check).

Free-text fields (`notes`, `title`, …) are not status fields. A status word written there is not
refused. `test_ids` is pinned to `[]`.

The out-of-process output check enforces that (fix round 1, meta PR #6 verify FINDING 1). **Not
defended:** a pull request that edits the checkers themselves (`status.py`, the three `scripts/`
checkers, `validate.yml`). That change is visible in the PR diff, and nothing else guards it today. CODEOWNERS
names the owner for these paths, but the file itself says it is advisory: `main` has no branch
protection (the API returns 404) and no ruleset (`[]`). The war room's verifier-gated merge is the
only review such a change gets.

## Why a committed record proved online

The generator has to stay reproducible offline. `scripts/check-generated-ledger.sh` regenerates it
under two locales and diffs the bytes, and the component repositories are not checked out in this
lane. So the rule is split in two, and both halves read the record through the same loader
(`status.load_records`):

| Half | Where | Proves |
|---|---|---|
| output (out of process) | [`scripts/check-ledger-status-output.py`](../../../scripts/check-ledger-status-output.py), step (a2), first | parses the COMMITTED `features.json` as plain JSON in a process that imports no section source; the tree matches HEAD for the ledger, records, issues and war-room evidence; every entry has exactly the keys `core.req` emits; the ids carrying any non-default status or evidence EQUAL the record ids; every entry, re-derived from defaults plus the committed records, equals the committed entry; the summary counts match |
| offline | [`status.py`](../ledger-generator/status.py), run by `build.py` inside step (a) | a first line against honest mistakes (a section source can defeat in-process checks; the output check is the guarantee): no section source sets a status, compared with `type(...) is str`; the record's shape; status is `IMPLEMENTED` or `VERIFIED` (anything else is refused by name); full 40-hex SHAs; for `VERIFIED`, each merge's evidence file under `docs/evidence/warroom/` **ends** with `FINAL VERDICT: PASS — SHA <40-hex>` or `FINAL VERDICT: PASS (local; CI BLOCKED) — SHA <40-hex>` (the qualifier is an allowlist; any other is refused by name) naming that merge's `verified_head`; the floors below |
| online | [`scripts/check-ledger-status-remote.py`](../../../scripts/check-ledger-status-remote.py), step (a2) | per merge: the PR is merged into `main`; GitHub's head for it is `verified_head`; GitHub's merge commit is `merge_commit`; `compare/<merge_commit>...main` is `ahead`/`identical` (on main now); for `VERIFIED`, the latest GitHub Actions `ci-required` check-run on `verified_head` is `completed/success` |

A hand-edited `features.json` is caught by the regeneration diff (demonstration D1c). The output
check catches it too.

A reviewer sees a committed record in the PR diff. The online half runs again on every meta pull
request and merge-queue entry, not on `main` after a merge. So a record that was true when written
and later stops being true (for example, a force-pushed component `main` that drops the merge
commit) turns the lane red at the next meta PR, not at once.

**VERIFIED requires the evidence to be on meta `main` first (fix round 2, R-3).** Each evidence
file a VERIFIED record cites must be on meta `main`, byte-identical. It is checked twice:
- offline, by the output check, against `origin/main` (CI fetches `main` before the step);
- online, by the remote check, through `contents/<path>?ref=main`, comparing git blob SHAs.

So a pull request cannot cite a verdict it introduces itself: the verdict has to be merged through
the chair's records path before any record can rest on it. This makes **war-room queue 2u a
prerequisite for any VERIFIED record**. Today the verifier files for core #8 and user #8 exist only
on `chore/warroom-records-2026-09-21`, not on `main`. The checks do not establish who wrote an
evidence file, only that it landed on `main` before the record.

**VERIFIED requires `ci-required` green on the verified head.** A verifier's
`PASS (local; CI BLOCKED)` passes the offline verdict check only because the online half then asks
GitHub for `ci-required` on the same SHA. A local PASS on its own never stands in for CI. That
matches the merge rule in `AGENTS.md`.

**Floors.** These stop a component half being recorded as the whole requirement. They set a
minimum and do not prove the requirement is complete:
- a requirement with a `ui` surface needs a `vizra-user` merge;
- a requirement with an `api` surface needs a `vizra-core` merge;
- every `docs/issues/*.md` whose `**Ledger IDs:**` line names the requirement must be cited, with at
  least one bullet quoted verbatim from its `## Acceptance` section. Where that section tags its
  bullets with ids (VZ-ISSUE-001 does), the cited bullet must name this requirement.

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
| D1c | `features.json` hand-edited to VERIFIED and committed (scratch copy) | output check `VZ-FOUND-008: STATUS WITHOUT A RECORD`; regeneration `GENERATED FILE IS NOT REPRODUCIBLE` | commit reverted |
| D2a | verdict line names another head of the same PR | `VERDICT SHA MISMATCH` | restored |
| D2b | a later `FINAL VERDICT: FAIL` becomes the final line | `does not END with a PASS verdict` | restored |
| D2c | evidence file path that does not exist | `MISSING EVIDENCE FILE` | restored |
| D3 | IMPLEMENTED, merge commit = an earlier head of user #8 (not on main) | `is NOT on yegamble/vizra-user main` | the true merge commit `7a3a572` proved |
| D4 | status `DONE`, `IN_PROGRESS`, `VERIFIED_AT_SHA` | `status '<x>' is REFUSED` | restored |
| D5a | VZ-INSTALL-003 with only a core merge | `names no vizra-user merge` | restored |
| D5b | VZ-FOUND-007 citing only VZ-ISSUE-001 | `docs/issues/VZ-ISSUE-006.md schedules VZ-FOUND-007` | restored |
| D6a | probe 2c: a section source adds `status`/`verified` keys; regenerated and committed (scratch copy). The generator and the regeneration check both stay green, which shows the escape is real | output check `KEY SET differs from what core.req emits; extra ['status', 'verified']` | reset to base: output check green |
| D6b-i | probe 2d: a `str` subclass whose `__ne__` returns False | the generator now refuses it in-process: `HAND-ASSERTED implementation_status 'VERIFIED'` | reset |
| D6b-ii | 2d plus a wrapper that hides it from the in-process check; generator and regeneration check green | output check `VZ-CONTROLS-001: STATUS WITHOUT A RECORD` | reset: green |
| D6c | probe 2e: a wrapper around `status.check_dsl_defaults`, then VERIFIED / VERIFIED_AT_SHA; generator and regeneration check green | output check `VZ-CONTROLS-001: STATUS WITHOUT A RECORD` | reset: green |
| D7 | `FINAL VERDICT: PASS (superseded — FAIL on re-run) — SHA …` | `is NOT ALLOWLISTED` | restored |
| D8 | VZ-FOUND-007 citing VZ-ISSUE-001's VZ-FOUND-008 bullet | `the cited bullet does not name VZ-FOUND-007` | restored |
| D9 | round-1 probe N3: a section source replaces `json.dump` to write `"implementation_status": "VERIFIED"` / `"verification_status": "VERIFIED_AT_SHA"` before VZ-CONTROLS-001's real keys. The generator and the regeneration check stay green | output check `DUPLICATE KEY 'implementation_status' in entry VZ-CONTROLS-001` | reset: green |
| D9b | the same route, writing `indent=1` instead of 2 (no duplicate, nothing a parser reads differently) | output check `NON-CANONICAL BYTES` (the byte guard is live on its own) | reset: green |
| D10a | a VERIFIED record plus the evidence file it cites, committed together; the copy's `origin/main` lacks the file | output check `EVIDENCE NOT ON META MAIN` | `origin/main` moved to include the file: green |
| D10b | the same record, online | `EVIDENCE NOT ON META MAIN` (contents API 404 on real `main`) | record removed: green |
| D11 | `summary.by_implementation_status` tampered and committed | `summary.by_implementation_status is {'PLANNED': 191, 'VERIFIED': 1} but the features count {'PLANNED': 192}` | reset: green |

The checkers are themselves mutation-tested:
- [`unit-mutations.txt`](unit-mutations.txt) (first round, at `94ac3bf`): five mutations of
  `status.py`, and each turns a named unit test red.
- [`remote-mutations.txt`](remote-mutations.txt) (first round): four mutations of the online checker,
  and each turns a named self-test case red.
- [`guard-mutations.txt`](guard-mutations.txt) (fix round 1): the guards the verifier found untested.
  - Deleting the `base == main` check turns `test_base_other_than_main_is_refused` red, and the
    self-test case for vizra#3 red.
  - Deleting the GitHub-Actions app filter turns `test_ci_required_from_a_non_actions_app_is_refused`
    red, with a second test.
  - Deleting the auth proof turns `test_anonymous_gh_is_refused` red.
  - Reverting the `type(...) is str` check, deleting the qualifier allowlist, or deleting the
    tagged-bullet check each turns its named unit test red.
- [`output-mutations.txt`](output-mutations.txt) (fix round 1): the output checker, run on the
  three committed escapes.
  - Deleting the key-set check lets 2c through, so that check is load-bearing.
  - Deleting only the set-equality check, or only the re-derivation, still refuses 2d and 2e, by
    the other one. Deleting both lets 2d and 2e through. The two checks are deliberately redundant.

- [`guard-mutations-round2.txt`](guard-mutations-round2.txt) (fix round 2): each of these turns
  its named test red:
  - deleting the `prove_auth()` call in `main()`;
  - deleting the one-page check-run cap;
  - deleting the online evidence-on-main call (the self-test goes 9/10 too);
  - reverting the evidence check to `ev != []`;
  - deleting the `test_ids` DSL check;
  - deleting the records file's duplicate-key hook.
- [`output-mutations-round2.txt`](output-mutations-round2.txt) (fix round 2): the output checker on
  committed routes e-dup (D9), e-canon (D9b), e-tid, e-sum (D11) and e-ev (D10a).
  - The `test_ids` pin, the summary check and the evidence-on-main check are each load-bearing
    for their route.
  - The duplicate-key hook and the canonical-bytes check back each other up on e-dup. Deleting
    both lets it through.
  - Deleting the canonical check lets e-canon through.

Unit tests: [`unit-tests.txt`](unit-tests.txt): 38 offline tests plus 13 online tests with an
injected `gh_api`. Self-test and output check: [`remote-self-test.txt`](remote-self-test.txt): 10/10.
