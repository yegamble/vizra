# Second verdict: meta PR #25 (VZ-FOUND-003 IMPLEMENTED), round 2

- Subject: https://github.com/yegamble/vizra/pull/25
- Head SHA: a02ef82942b20ca495d08e378f066f1ef8d9437d (checked at the start and the end with `gh pr view 25 --json headRefOid`; the same both times)
- Verifier: independent. I wrote neither the record nor the round-1 verdict.
- Environment: darwin, a fresh clone in a mktemp scratch directory (now deleted), gh CLI. Date: 2026-11-12.
- First verdict read: 2026-11-12-meta-pr25-ledger-found-003-VERIFY.md (FAIL at bd93f36).

## Commands

| # | Command | Exit | Result |
|---|---|---|---|
| A1 | `git diff --name-only origin/main...HEAD` | 0 | exactly `docs/evidence/ledger-generator/status_records.json` and `docs/quality/features.json` |
| A2 | features.json counts (python) | 0 | implementation: IMPLEMENTED 2, PLANNED 190; verification: UNVERIFIED 192, no VERIFIED. VZ-FOUND-003 is IMPLEMENTED / UNVERIFIED / NOT_RELEASED, merge_status MERGED |
| A3 | `cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json` and then `git status --porcelain` | 0 | no diff |
| A4 | `python3 scripts/check-ledger-status-output.py` | 0 | |
| A5 | `python3 scripts/check-ledger-status-remote.py` (1st run) | 1 | `gh api repos/yegamble/vizra-core/pulls/19: Service Unavailable` (GitHub infra) |
| A5' | `python3 scripts/check-ledger-status-remote.py` (re-run) | 0 | `OK: 2 status record(s) proved against GitHub`; 58d658f and a6d4792 are on vizra-core main |
| A6 | `bash scripts/check-generated-ledger.sh` | 0 | |
| A7 | `python3 -m unittest discover -s docs/evidence/ledger-generator -p 'test_*.py'` | 0 | Ran 38 tests, OK, 0 skipped |
| C1 | `git show origin/chore/warroom-records-2026-11-12d:docs/warroom/OWNER-INBOX.md` | 0 | item `### 21` exists |
| D1 | `gh pr checks 25` | — | `ci-required` fail, `validate` fail |
| D2 | `gh run view 43239191026 --json headSha` / `--log-failed` | 0 | headSha a02ef82…; step "every ledger-status guard still fails against a controlled mutation": `demo: 59 passed, 2 failed` (D3 restored, D10b restored); both failed on `could not read … gh api …`; the failed log contains 5 `Service Unavailable` lines |

## A: PASS
The mechanics are all correct. The record follows rule 3: it has merges, full SHAs and no evidence_file.

## B: the judgement. IMPLEMENTED overclaims (BLOCKING)
1. The record's own first sentence says "one outcome clause is not delivered". The outcome is the definition of what gets implemented. An implementation that is missing one of its outcome clauses is a partial implementation. status.py rule 2 says "There is no partial status", and it refuses IN_PROGRESS for exactly this reason. Labelling a known-incomplete implementation IMPLEMENTED is IN_PROGRESS under another name.
2. AGENTS.md separates implementation state from verification state. In this ledger, IMPLEMENTED means "the implementation is complete and only VERIFIED's evidence is missing". VZ-FOUND-002 uses it that way: "All three ledger cases are delivered". Here the gap is in the implementation, not in the evidence. No verifier could ever issue a PASS on this code as it stands. So IMPLEMENTED would tell a ledger reader (who sees only the status column in summaries) that the work is complete when it is not.
3. Round 1 suggested IMPLEMENTED could be honest if the gap were stated. I disagree. The plain wording makes the record transparent, but it does not make the status true. A disclosed overclaim is still an overclaim, and rule 2 leaves no room for a qualified status.
4. Sentence by sentence: the rationale is now accurate. "reviewed" is gone, "superset" is gone, the description of the marker (any reason, no review, no release tie) matches round 1's D3, and the S1/R1/N1/S2/N2 claims match round 1's reproductions. I found no unsupported factual sentence. The only overstatement is the status itself.
5. Honest status: none, so leave VZ-FOUND-003 PLANNED (no record). IMPLEMENTED becomes honest only after one of two things: the window is built (inbox 21 option A), or the owner rewords the outcome (option B). Option B changes the acceptance target, so it is owner-only.

## C: FOLLOW-UP (not blocking)
Inbox 21 exists on records PR #28's branch and describes the gap accurately (no window, marker unrestricted, options A/B). It is not on main yet, so the citation is a follow-up only. It does not misstate the item.

## D: FAIL, caused by CI infra
Both checks ran on head a02ef82…. `validate` failed with `demo: 59 passed, 2 failed`, not 61/0. Both failures are gh API reads that returned `Service Unavailable` (5 occurrences), in the demo mutation step rather than the remote-proof step. Locally the remote proof passed when re-run. So the CI red is infra (BLOCKED on its own), but it is not the deciding issue.

## Findings
- **BLOCKING (false-green product gate):** VZ-FOUND-003 is recorded IMPLEMENTED while its own rationale says an outcome clause is not implemented. That is a partial status, which rule 2 forbids. Fix: drop the record (leave PLANNED) until inbox 21 is resolved, or deliver the window.
- FOLLOW-UP: the rationale cites inbox 21, which is not yet on main (PR #28).
- INFRA: CI red because of GitHub `Service Unavailable`. Needs a re-run by the chair (I did not re-run it).

## Not run
I did not re-run demo.sh locally (CI ran it), and I did not re-run CI (forbidden). I did not re-reproduce the vizra-core cases: I relied on round 1 for D3/S1/R1/N1/S2/N2.

FINAL VERDICT: FAIL — SHA a02ef82942b20ca495d08e378f066f1ef8d9437d
