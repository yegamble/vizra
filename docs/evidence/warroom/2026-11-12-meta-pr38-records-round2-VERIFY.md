# VERIFY round 2 — yegamble/vizra PR #38 — VZ-CI-001 IMPLEMENTED, VZ-OPS-005 IMPLEMENTED

- SHA: `6ea3bf5fe8af2fdad03727a43be951411ac9f89c` (`gh pr view 38`: headRefOid matches, OPEN, MERGEABLE). It has not moved since the round-1 FAIL. Meta main: `bc2aa061687724eeea803300d3f26b8010ddb117`.
- Verifier: a fresh independent verifier. Clone at `/tmp/vzv-vizra-pr38b-kXytAw`, deleted afterwards. darwin.
- Budgets: QUEUE-ledger-VZ-CI-001 2nd verdict; QUEUE-ledger-VZ-OPS-005 2nd verdict.

## B-1 re-check — RESOLVED
- `git ls-tree -r origin/main docs/evidence/warroom | grep pr17-ci-001` → `blob d38a7c49… docs/evidence/warroom/2026-11-12-vizra-user-pr17-ci-001-n1-VERIFY.md`. It arrived through bc2aa06 "chore(warroom): records, ticks 282+ (#36)", which is an ancestor of origin/main.
- The file ends with `FINAL VERDICT: PASS — SHA e6748c22015368bcaf77e579440febb91af4f0d1`.
- It supports the vizra-user N1 claim:
  - mutations it.skip, skipIf, describe.skip and a Playwright fixture skip → check:skips exit 1 (:17-24);
  - an extra required workflow step (:27);
  - RED run 43245135598 (:32);
  - GREEN at e6748c2 with 898 vitest and 42 playwright tests, none skipped (:33).
- `gh pr view 17 -R yegamble/vizra-user` → e6748c22 / 72340983, MERGED. This matches the record.

## Checks re-run on 6ea3bf5
| Command | Result |
|---|---|
| `git diff --stat origin/main...HEAD` | only status_records.json (+84) and features.json (+105/-8) |
| `bash scripts/check-generated-ledger.sh` | exit 0 |
| `python3 scripts/check-ledger-status-output.py` | exit 0 (192 entries, 4 records) |
| `python3 scripts/check-ledger-status-remote.py` | exit 0 ("4 status record(s) proved against GitHub") |
| `python3 -m unittest test_status` | Ran 38 tests, OK |

## Merge entries vs `gh pr view` (all MERGED; head/merge match the record)
| PR | verified_head | merge_commit | PASS line on main |
|---|---|---|---|
| core #21 | 71a1ff31 | 3f1def36 | ci-001-core-search-VERIFY.md |
| search #6 | 0e93164b | 8d0c293a | ci-001-core-search-VERIFY.md |
| meta #27 | cb500ae5 | 791a0207 | ci-001-user-meta-VERIFY.md |
| user #14 | 50b1cd14 | 9f7c639c | ci-001-user-meta-VERIFY.md |
| user #17 | e6748c22 | 72340983 | vizra-user-pr17-ci-001-n1-VERIFY.md |
| core #20 | 030a13fc | 7f64b6de | vizra-core-pr20-ops-005-VERIFY.md |
| meta #29 | fa06a7a6 | cfce798d | meta-pr29-otel-profile-VERIFY.md |

The PASS lines were found with `git grep "PASS — SHA <head>" origin/main -- docs/evidence/warroom`.

## Bullets, rationale and status
- The SHA is unchanged, so the round-1 results for the verbatim bullets still hold: VZ-ISSUE-003.md:14-16 and VZ-ISSUE-004.md:18-20.
- The round-1 rationale spot-check also still holds. The only unsupported claim was the user N1 claim, and it is now supported.
- IMPLEMENTED (not VERIFIED) is honest for both records:
  - CI-001 has no red-then-green CI link for every case in every repo.
  - OPS-005 has no span that has reached a collector.

## Merge onto current main
`git merge origin/main` succeeded with no conflict (exit 0). After the merge, check-generated-ledger.sh exited 0 and check-ledger-status-output.py exited 0 (192 entries, 4 records).

## CI on 6ea3bf5 (`gh pr checks 38`)
- ci-required: pass (run 43271421040)
- validate: pass (run 43271421114)
- GitGuardian: pass

## Findings
No BLOCKING findings. No new follow-ups: the round-1 follow-up is already recorded and is not raised again.

## Verdict per record
- VZ-CI-001: PASS
- VZ-OPS-005: PASS

FINAL VERDICT: PASS — SHA 6ea3bf5fe8af2fdad03727a43be951411ac9f89c
