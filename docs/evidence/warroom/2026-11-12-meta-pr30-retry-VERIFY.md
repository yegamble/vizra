# Verify meta PR #30 — gh_api() transient retry

Verifier: independent (did not write code). SHA fc39d2dd7983cafad1395f179c215a8d6dd0d4ab (PR head at start and end). Clean clone in mktemp dir, deleted after. Env: darwin, python3, gh authed.

## Commands
| Command | Exit | Result |
|---|---|---|
| `python3 -m unittest discover -s docs/evidence/ledger-generator -p 'test_*.py'` | 0 | Ran 41, OK, 0 skips |
| `python3 scripts/check-ledger-status-remote.py --self-test` | 0 | 10/10 cases |
| `python3 scripts/check-ledger-status-remote.py` | 0 | 1 status record proved against GitHub |
| Mutation: retry tuple -> `(None,)` (no retry), rerun unittest | 1 | FAIL test_503_twice_then_success, test_503_always_fails_with_original_error; restored, `git status` clean |
| Fake gh: exit 1, stderr `HTTP 404`, body "Service Unavailable title" | - | 1 call, same failure (no retry) |
| Fake gh: exit 0, body "Service Unavailable fix" | - | 1 call, success (no retry) |
| Fake gh: exit 1, body-only "Service Unavailable", no HTTP code | - | 3 calls, same failure |
| check-runs on SHA | - | ci-required success, validate success, head_sha = SHA |

## Results
- A. Scope: PR files = script, new test file, plan. Script diff: only `import time`, constants, `_is_transient`, `_gh_api_once`, `gh_api` (JSON parse tail unchanged). Classification is on error TEXT, but only evaluated when gh exits non-zero; exit 0 is never retried or reclassified. 401/403/404/422 text forces non-transient. A retry only re-issues the same request; error returned after the last attempt is the original-format error; no path converts a failure into success other than GitHub actually returning success. 
- B. Worst case per call: 3x60 s + 2+5 s = 187 s. 6 gh_api call sites; per record a handful of calls, so bounded at ~187 s x calls; validate.yml has no `timeout-minutes` (GitHub default 360 min) — bounded and below it for current record count.
- C. CI green on exact SHA.

## Findings
- BLOCKING: none.
- FOLLOW-UP: text classification means a non-zero gh exit whose body merely contains e.g. "Service Unavailable" without a 4xx code (e.g. a 500/400 echoing user text) is retried up to 3 times — extra delay only, same final result. Prefer classifying on gh's `(HTTP NNN)` status. Also no explicit job `timeout-minutes` in validate.yml.

FINAL VERDICT: PASS — SHA fc39d2dd7983cafad1395f179c215a8d6dd0d4ab
