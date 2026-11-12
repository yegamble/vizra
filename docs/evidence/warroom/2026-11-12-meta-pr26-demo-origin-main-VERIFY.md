# Independent verification — yegamble/vizra PR #26 (demo.sh origin/main)

Subject SHA: dcd07826d914a4382cb8ae09b79c0672b6750a32 (PR head at start and end). Verifier did not write the change. Environment: darwin, scratch clones under $TMPDIR/vzv-meta-pr26-*, deleted after the run. PR #25 head 8cf0640.

## Commands
| # | Command / state | Exit | Result |
|---|---|---|---|
| A | `git diff --name-only origin/main...HEAD` | 0 | demo.sh + docs/plans/2026-11-12-meta-ledger-status-demo-origin-main.md only |
| A | red/green invocation counts (origin/main vs HEAD) | 0 | 41 / 41 (red 4, green 12 line-start; no change) |
| C1 | head as is, `bash docs/evidence/ledger-status/demo.sh` | 0 | demo: 61 passed, 0 failed |
| C2 | head + PR #25 status_records.json, features.json | 0 | demo: 61 passed, 0 failed |
| C3 | C2 + `return` inserted before the origin/main check in check-ledger-status-output.py | 1 | 60 passed, 1 failed: the only FAIL is "D10a offline: evidence not on (the copy's) origin/main ... got exit 0" |
| C4 | C2 with origin/main's demo.sh | 1 | 53 passed, 8 failed (D1c, D6a, D6b-i, D6b-ii, D6c, D9, D9b, D11 restored; 8× "not available") |
| D | shellcheck on both versions | — | 2 findings blocks each (same count); no new findings |
| E | `gh run list --commit <sha>` | — | ci-required, validate both still in_progress at cut-off |

## Findings
- A: The diff touches only the setup of the scratch copy (`git update-ref refs/remotes/origin/main HEAD`), one comment, and D10a's cleanup (`update-ref ... base-commit` replaces `update-ref -d`). No needle, red/green call or case was removed.
- B: D10a still sets origin/main to base-commit before its red half. The fixture evidence is only in the later commit, and C3 shows the red half fails when the check is disabled, so the protection is still live. No demo needle mentions 'not available' (grep finds nothing), so no red case relied on origin/main being absent.
- No blocking findings.

## Not run
- CI is not confirmed: neither run had finished when I was cut off, so I could not check validate's `demo:` log line.

SUPERSEDED (see completion section below): FINAL VERDICT: BLOCKED — SHA dcd07826d914a4382cb8ae09b79c0672b6750a32

## Completion of E by a second independent verifier (2026-11-12)
- `gh pr view 26 -R yegamble/vizra --json headRefOid,state` → `{"headRefOid":"dcd07826d914a4382cb8ae09b79c0672b6750a32","state":"OPEN"}` (head unchanged, open).
- `gh run list -R yegamble/vizra --commit dcd07826d914a4382cb8ae09b79c0672b6750a32 --json databaseId,workflowName,status,conclusion,headSha` → validate 43235631796 completed/success; ci-required 43235631578 completed/success; both headSha dcd07826d914a4382cb8ae09b79c0672b6750a32.
- `gh run view 43235631796 -R yegamble/vizra --log | grep -n 'demo:' | tail -3` → line 511, step "every ledger-status guard still fails against a controlled mutation": `demo: 61 passed, 0 failed`.
- E: PASS. A-D taken from the first verifier's reproduction above; earlier BLOCKED verdict is superseded.

FINAL VERDICT: PASS — SHA dcd07826d914a4382cb8ae09b79c0672b6750a32
