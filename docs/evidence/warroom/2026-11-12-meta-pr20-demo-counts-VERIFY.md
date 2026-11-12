# Independent verification — meta PR #20 (ledger-status demo D11 derives its counts)

- Subject: https://github.com/yegamble/vizra/pull/20, branch `fix/ledger-status-demo-counts`
- Verified head: `ccacb50d69c8a38f1c6ef9f5d6f30dc273bdbe72` (checked at start and end via `gh pr view 20 --json headRefOid`; unchanged)
- Date: 2026-11-12. Verifier: independent sub-agent; wrote none of the code; edited, committed, pushed and re-ran nothing in the repo.
- Environment: macOS (Darwin 25.5.0), bash, python3, shellcheck, `gh` authenticated; four fresh clones of
  https://github.com/yegamble/vizra.git in a `mktemp -d` scratch directory (deleted at the end).
- PR #19 head used for the record state: `4eb6249447502d4aaee9aa2702df8ed7c4d1360c` (`ledger/vz-found-002-implemented`).

## Commands and results

| # | Command (in its own clone) | Exit | Result |
|---|---|---|---|
| A | `git diff --name-only origin/main...HEAD` | 0 | exactly `docs/evidence/ledger-status/demo.sh`, `docs/plans/2026-11-12-meta-ledger-status-demo-counts.md` |
| B1 | count of `red "` / `green "` invocations, origin/main vs head | 0 | 18 / 23 on both |
| B2 | head's derivation run against the head's `docs/quality/features.json` and compared with the old literal | 0 | identical, character for character: `summary.by_implementation_status is {'PLANNED': 191, 'VERIFIED': 1} but the features count {'PLANNED': 192}` |
| B3 | D11 block extracted verbatim from the head, run against a ledger with no PLANNED entry (mutate/red stubbed) | 0 | derivation exits non-zero; `FAIL  D11 could not derive…`; `FAILED=1 PASSED=0`; neither mutate nor red ran |
| C1 | state 1, PR head as is: `bash docs/evidence/ledger-status/demo.sh` | 0 | `demo: 61 passed, 0 failed` |
| C2 | state 2, head + PR #19's `status_records.json` and `features.json` committed locally | 0 | `demo: 61 passed, 0 failed`; D11 RED on `…is {'IMPLEMENTED': 1, 'PLANNED': 190, 'VERIFIED': 1} but the features count {'IMPLEMENTED': 1, 'PLANNED': 191}` |
| C3 | state 3, state 2 + checker comparison made unreachable (`if False and summ.get(key) != …`, committed locally) | 1 | `demo: 60 passed, 1 failed`; the one FAIL is `D11 — expected a non-zero exit naming […], got exit 0` |
| C4 | state 4, state 2 with origin/main's demo.sh | 1 | `demo: 60 passed, 1 failed`; the FAIL is D11 with the stale hard-coded needle (reproduces PR #19's run 43210473134) |
| D | `shellcheck` on origin/main's demo.sh and on the head's | 1 / 1 | 3 findings each, all SC2001 at lines 73/79/93 (pre-existing `red`/`green` helpers); no new finding |
| E | `gh run list --commit ccacb50…`, `gh run view 43211366492` | 0 | see "CI" below |

## Result per claim

- A. HOLDS. Two files only; no checker, workflow, record or ledger file.
- B. HOLDS. Read line by line: the only hunk replaces the three-line D11 body. D11 still tampers
  `summary.by_implementation_status` (through the unchanged `mutate`, which refuses a no-op mutation), commits
  it in the scratch copy, and calls the unchanged `red`, which needs a non-zero exit AND `grep -qF` of the
  needle. The needle is the full message with both dicts, built with the same `dict(sorted(...))` f-string as
  scripts/check-ledger-status-output.py:227-233. The tampered summary always differs from the true counts (one
  entry moved from PLANNED to VERIFIED). A ledger without PLANNED adds to FAILED; it is not skipped. Case count
  unchanged (18 red, 23 green; total 61 in both states). No other case is touched; `red`, `green`, `mutate`
  are byte-identical.
- C. HOLDS. States 1 and 2 are 61/0; state 3 shows D11 is reachable and scored FAIL when the guard is
  removed, with a non-zero exit of demo.sh; state 4 reproduces the 60/1 the change is meant to fix.
- D. HOLDS.
- E. HOLDS. `ci-required` run 43211366458: completed/success, headSha ccacb50d69c8a38f1c6ef9f5d6f30dc273bdbe72. `validate` run 43211366492: completed/success, same headSha; its log, step 'every ledger-status guard still fails against a controlled mutation', line 509: `demo: 61 passed, 0 failed` (`gh run view 43211366492 -R yegamble/vizra --log | grep -n 'demo:' | tail -3`).

## Findings

Blocking: none in the change itself.

Non-blocking (follow-up, does not affect scoring):
1. In the missing-PLANNED branch the reason is written by `sys.exit(...)` to stderr while `$D11_PLAN` captures
   stdout only, so the FAIL line ends with an empty reason (`…counted as a FAIL: `); the reason still appears on
   the line above in the transcript. Cosmetic.
2. The tamper always moves one entry PLANNED→VERIFIED; a ledger with zero PLANNED entries makes D11 a
   permanent FAIL (loud, not a false green). Far off; note for the future.

## Not run

- No CI re-run, no `gh pr checks --watch`. Case D10b and the other online cases ran with the local `gh`.
- Only the `by_implementation_status` comparison is demonstrated by D11 (as before the change); the
  `by_verification_status` half has no demo case on either side. Not a regression of this PR.

FINAL VERDICT: PASS — SHA ccacb50d69c8a38f1c6ef9f5d6f30dc273bdbe72
