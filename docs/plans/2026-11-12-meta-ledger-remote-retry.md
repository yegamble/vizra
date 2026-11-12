# Execution plan: QUEUE-ci-flake — retry transient GitHub API failures in check-ledger-status-remote.py

## Context
Base origin/main 206d739, branch `fix/ledger-remote-retry`, worktree `.claude/worktrees/meta-retry`. No ledger ID.
On 2026-11-12 GitHub's API answered `gh api` with `Service Unavailable` (HTTP 503) intermittently, turning the
required `validate` lane red at least five times (PR #24 twice, #25, #29, others) in the step "every recorded
ledger status is proved against GitHub" and in `docs/evidence/ledger-status/demo.sh` cases D3/D10b (which call
the same script). Each needed a manual re-run.

## Acceptance
- `gh_api()` retries only transient failures: HTTP 502/503/504, `Bad Gateway`/`Service Unavailable`/`Gateway
  Timeout` text, connection resets/timeouts, and the subprocess timeout. At most 3 attempts, waits 2 s then 5 s
  (≤ 7 s added sleep), one stderr line per retry.
- 4xx (401/403/404/422) and every other failure: no retry, same message as before.
- After the last attempt: the same error message and the same non-zero outcome as before. Fail-closed unchanged.
- Non-goals: any other behaviour or message of the checker.

## Implementation
`scripts/check-ledger-status-remote.py`: `RETRY_DELAYS`, `TRANSIENT`, `_is_transient()`, `_gh_api_once()`;
`gh_api()` loops. Tests: `docs/evidence/ledger-generator/test_ledger_status_remote.py` (new; no prior tests
for this script existed) with a fake `gh` on PATH replaying scripted replies; delays patched to 0.

## Verification
- `python3 -m unittest discover -s docs/evidence/ledger-generator -p 'test_*.py'`
- `python3 scripts/check-ledger-status-remote.py --self-test` and without arguments
- `bash docs/evidence/ledger-status/demo.sh` (expect 61 passed, 0 failed)
- `python3 scripts/check-doc-links.py`
All through `.claude/council/quiet.sh`.

## Progress and evidence
- RED (tests written first, before retry code): `python3 -m unittest docs/evidence/ledger-generator/test_ledger_status_remote.py`
  → `Ran 3 tests … FAILED (failures=2)` (503×2-then-ok and 503×4 fail; 404-no-retry passes, as today).
- GREEN after the fix: same command → `Ran 3 tests … OK`.
- Gates on the fix revision, darwin arm64, gh authenticated: unit discover 41 tests OK (exit 0); --self-test 10/10
  (exit 0); remote `OK: 1 status record(s) proved` (exit 0); demo and doc-links: see PR body.

## Blockers and handoff
None. State: READY_FOR_REVIEW once CI on the final head is green.
