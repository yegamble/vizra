# Independent verification — yegamble/vizra PR #22 (records)

- Subject: https://github.com/yegamble/vizra/pull/22, head `b7a2e961c8e75a646af6a64b116877cc9a3f1613` (checked at start and end; still OPEN)
- Verifier: independent sub-agent; I did not write this PR. No edits, pushes, merges or CI reruns.
- Environment: darwin, fresh clone in a mktemp scratch dir, checked out at the SHA. The scratch dir was deleted afterwards.

## Commands

| # | Command | Exit | Result |
|---|---------|------|--------|
| 1 | `gh pr view 22 --json headRefOid,state` | 0 | head b7a2e96…, OPEN |
| 2 | `git diff --name-only origin/main...HEAD` | 0 | exactly the 2 expected files |
| 3 | `git diff origin/main...HEAD -- docs/warroom/MERGED.md` | 0 | one `+` table row, no `-` lines |
| 4 | `gh pr view 21 --json state,headRefOid,mergeCommit` | 0 | MERGED, head 44d80e1fa129fad9dfa40658e2274a649da049b3, merge 4a53e88897a635ae854e3067dfcb29bda0274e5a |
| 5 | last non-empty line of pr21 evidence file | 0 | `FINAL VERDICT: PASS — SHA 44d80e1fa129fad9dfa40658e2274a649da049b3` |
| 6 | `gh run list --commit 44d80e1…` | 0 | ci-required success, validate success |
| 7 | `python3 scripts/check-doc-links.py` | 0 | 30 relative links resolve |
| 8 | `python3 scripts/warroom-check.py board` | 0 | OK, 92 lines |
| 9 | `bash scripts/check-generated-ledger.sh` | 0 | reproduces byte-for-byte (UTF-8 and C/POSIX) |
| 10 | credential-shape grep on added lines (ghp_/AKIA/BEGIN key/sk-/xox) | 1 | no matches |
| 11 | `gh run list --commit b7a2e96…` | 0 | ci-required completed/success, headSha b7a2e961c8e75a646af6a64b116877cc9a3f1613 |

## Claims
- A: PASS. Only the two expected files changed; MERGED.md has one added row.
- B: PASS. The row records `44d80e1` → `4a53e88`, which matches GitHub. The evidence verdict line is exact, and ci-required succeeded on 44d80e1.
- C: PASS. All three checks exited 0.
- D: PASS. No credential shapes found.
- E: PASS. ci-required succeeded on the exact head.

## Findings
None blocking. No findings.

FINAL VERDICT: PASS — SHA b7a2e961c8e75a646af6a64b116877cc9a3f1613
