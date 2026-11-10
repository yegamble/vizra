# Independent verification — vizra (meta) PR #12, chair records

- Subject: https://github.com/yegamble/vizra/pull/12
- Verified SHA: `ed8cd9caa71e771ab4b60ee4dadcc30ec153373c` (PR head at start and at end; PR OPEN)
- Base: `origin/main` = merge-base = `27be92a2a3706108d6f3b2d6058d3fbec00634a1`
- Date: 2026-11-10. Verifier: independent read-only agent; did not write the PR; no edit, commit, push or GitHub setting change.
- Environment: macOS (Darwin 25.5.0), `gh` authenticated, python3, bash; fresh clone in a `mktemp -d` scratch directory (`vzv-meta-pr12-O3vYXW`), deleted at the end.
- Component repos read at: vizra-core main `27cee5417ac51dad041e6f311ba4ca238246563e`, vizra-user main `783483f3c5f207d3370e6f1a79766f840e36472f` (shallow clones in the scratch directory).

## Commands

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `gh pr view 12 -R yegamble/vizra --json headRefOid` (start, end) | 0, 0 | `ed8cd9c…` both times |
| 2 | `git clone`, `git fetch origin pull/12/head`, `git checkout --detach ed8cd9c…` | 0 | HEAD = verified SHA |
| 3 | `git diff --name-only origin/main HEAD`, `--name-status` | 0 | 7 files, all under `docs/` (3 A, 4 M) |
| 4 | `gh api repos/yegamble/<repo>/rulesets` x4 | 0 | vizra 26967150, vizra-user 26967155, vizra-search 26967161, vizra-core: empty list |
| 5 | `gh api repos/yegamble/<repo>/rulesets/<id>` x3 | 0 | see B |
| 6 | `gh pr view` (vizra 11, 9; vizra-core 14; vizra-user 10); `gh api …/branches/<branch> -q .commit.sha` x2 | 0 | see C |
| 7 | `grep` MERGED.md; last non-empty line of the #9 evidence file | 0 | see D |
| 8 | Read `store/queries/owner_claim.sql`, `internal/ownerclaim/ownerclaim.go`, `.github/workflows/e2e.yml`, `internal/httpapi/probes.go` on component mains | 0 | see E |
| 9 | `python3 scripts/warroom-check.py board` | 0 | `OK: docs/plans/WARROOM-BOARD.md is 89 lines, longest 291 characters` |
| 10 | `python3 scripts/check-doc-links.py` | 0 | 32 relative links resolve |
| 11 | `python3 scripts/check-quality-json.py` | 0 | 192 ids in ledger; 191 written references, every one resolves |
| 12 | `bash scripts/check-generated-ledger.sh` | 0 | 192 requirements, statuses `{'PLANNED': 192}`, reproduces byte-for-byte in both locales |
| 13 | Queue-table ids vs `docs/quality/features.json` (regex `VZ-[A-Z0-9]+-[0-9]+`) | 0 | 32 distinct ids; 31 in the ledger; `VZ-ISSUE-001` is an issue id, see F |
| 14 | `git diff origin/main HEAD` added lines, credential patterns | 0 | see G |
| 15 | `gh pr checks 12 --watch --interval 20` | KILLED | the tool killed the watch; replaced by 16 |
| 16 | poll `gh run view 42874153812 --json status,conclusion,headSha` every 20 s; then `gh pr checks 12` | 0 | see H |

## Result per claim

**A — scope: REPRODUCED.** Exactly 7 paths: `docs/evidence/warroom/2026-11-10-after-merge-TRIAGE.md` (A), `…-ledger-status-candidates.md` (A), `…-meta-pr9-records-VERIFY.md` (A), `docs/plans/WARROOM-BOARD.md` (M), `docs/warroom/FOLLOWUPS.md` (M), `MERGED.md` (M), `OWNER-INBOX.md` (M). 281 insertions, 31 deletions. No code, workflow, script, test, AGENTS.md or `.claude/` path; `docs/evidence/ledger-generator/status_records.json` and `docs/quality/features.json` are not in the diff.

**B — rulesets: REPRODUCED.** For 26967150 (vizra), 26967155 (vizra-user), 26967161 (vizra-search), each read back: `enforcement: active`, `target: branch`, `conditions.ref_name.include: ["~DEFAULT_BRANCH"]`, exclude empty, rules `deletion`, `non_fast_forward`, `required_linear_history`, `required_status_checks` with one check `{context: ci-required, integration_id: 15368}` and `strict_required_status_checks_policy: false`, `bypass_actors: []`. No pull-request (review) rule. vizra-core: `rulesets` returns an empty list. Matches the triage record lines 9-16.

**C — PR and branch states: REPRODUCED.**
- vizra #11: MERGED, merge commit `82e952942a64ccb44522b575c88a4ae8c6fd2478`.
- vizra #9: MERGED, merge commit `27be92a2a3706108d6f3b2d6058d3fbec00634a1`, head `57f8f2b330c53ff3ca85b48ab7afa5e1b750deac`.
- vizra-core #14: CLOSED, `mergedAt` null, head `e43d5011584c33785c471d9aa27c000ad927f4dc`.
- vizra-user #10: CLOSED, `mergedAt` null, head `5c5c971ea8980c1ae44a3716f2d0b73ee54fe50b`.
- vizra-user branch `allowlist/pr10-work`: `7fb1365b96f89dcf422bb58cbcf34b418c79b3ad`.
- vizra-search branch `feat/vendor-tool-second-manifest`: `ed9f9cc3a8c4f9ce689d9c4f4d475cd1e04a118f`.

**D — MERGED.md row and #9 evidence: REPRODUCED.** `docs/warroom/MERGED.md:7` reads `57f8f2b` → `27be92a`, squash, PASS at `57f8f2b`, pointing at the evidence file. The last non-empty line of `docs/evidence/warroom/2026-11-10-meta-pr9-records-VERIFY.md` is `FINAL VERDICT: PASS — SHA 57f8f2b330c53ff3ca85b48ab7afa5e1b750deac`.

**E — spot checks: all three HOLD (read only, nothing executed).**
1. vizra-core `store/queries/owner_claim.sql` (the file is at `store/queries/`, as the record cites, not `internal/store/queries/`). The re-mint upsert, lines 45-51, sets `consumed_at = NULL` with no `WHERE owner_claim_tokens.consumed_at IS NULL` on the `DO UPDATE`: the defect the record describes is real. The redeem statement `ClaimOwner` requires `AND NOT EXISTS (SELECT 1 FROM users)` at line 97, and `ownerclaim.go:403-409` and `:473-479` return `ErrAlreadyClaimed` when `AnyUserExists` is true, the second inside the writing transaction. The mint itself selects `WHERE NOT EXISTS (SELECT 1 FROM users)` (line 44), so it can only reach the conflict update from a snapshot taken before the claim committed. Once the racing claim has committed its owner row, the re-opened token fails line 97 on every later statement. As far as I can read it, "the re-opened token cannot be redeemed" holds. Residual condition, not reproduced as reachable: it would become redeemable if the `users` table became empty again; a grep of non-test `.go` and `.sql` for `DELETE FROM users` found nothing. No database was run and the race was not executed.
2. vizra-user `.github/workflows/e2e.yml`: workflow-level `permissions: contents: read` (lines 29-30), no job-level override; `grep 'secrets\.'` has no match; the redact step is `if: failure()` (188-191) and the only upload step is `if: failure() && steps.redact.outcome == 'success'` with paths `test-results/`, `playwright-report/results.json`, `playwright-browsers.txt`, `retention-days: 3` (238-248). Lines 231-233 do still call the repo private, as the record says.
3. vizra-core `internal/httpapi/probes.go`: `computeReadiness` (from line 141) appends components `database`, `owner_claim`, `cache`, `search`, `worker` only; a case-insensitive grep for `storage`, `s3`, `blob` in the file has no match. The VZ-FOUND-005 statement holds.

**F — ledger untouched and consistent: REPRODUCED.** Commands 9-12 exit 0; the working tree was clean afterwards. Queue table: 31 of 32 matched ids are ledger ids present in `features.json`. The 32nd, `VZ-ISSUE-001` (board line 42, task text of row 3, not the ledger-id column), is an issue id: `docs/issues/VZ-ISSUE-001.md` exists and `check-quality-json.py` resolves that namespace against the issue file. It is not a missing ledger id.

**G — secrets: REPRODUCED, no live credential.** Hits in added lines, all inside the quoted #9 verifier evidence and labelled there: AWS's published documentation example access key id (the `…IOSFODNN7EXAMPLE` one, not reproduced here), a GitHub-token-shaped placeholder whose body is the word SECRETTOKEN, the literal text of a PEM header prefix twice inside a list of search patterns, `VIZRA_SMTP_PASSWORD=…` (elided marker) and `VZTYPED-secret-9d44` (labelled test marker). No OAuth token, fine-grained PAT, JWT, Slack token, `sk-` key or userinfo URL.

**H — CI: REPRODUCED.** `ci-required` run 42874153812: `completed`, `success`, headSha `ed8cd9caa71e771ab4b60ee4dadcc30ec153373c`, event `pull_request`, 7m38s. `validate` run 42874153861: `completed`, `success`, same headSha. GitGuardian: pass. `gh pr checks 12` exit 0.

## Findings

| # | Class | Finding |
|---|---|---|
| 1 | FOLLOW-UP | vizra-core `owner_claim.sql:45-51`: re-mint clears `consumed_at` without a guard. Real, already recorded as S-0002 follow-up; not redeemable today (line 97, `ownerclaim.go:403-409`, `:473-479`), so it does not meet the blocking bar. |
| 2 | FOLLOW-UP | vizra-user `e2e.yml:231-233` comment says the repo is private; it is public. Already recorded (queue 2q). |
| 3 | FOLLOW-UP | vizra-core has no ruleset; the record says so and does not claim otherwise. |

No BLOCKING finding.

## Not run

- No database, no Go or Playwright test, no execution of the owner-claim race: E is a code read.
- `gh api repos/<repo>/rules/branches/main` (the record's second read-back) was not run; the ruleset objects were read directly.
- The triage record's other rows (S-0009 and the rest, "no spec types into a field", the vendor-tool selftest, the local-cleanup branch list) and the `2026-11-10-ledger-status-candidates.md` rows other than VZ-FOUND-005 were not checked.
- No red-run artifact was downloaded.
- External URLs in the docs were not fetched.
- Process deviations: this file was created first with a BLOCKED line and rewritten once at the end, not after each step; the first `gh pr checks --watch` was killed by the tool and replaced by a 20-second poll of the run.

FINAL VERDICT: PASS — SHA ed8cd9caa71e771ab4b60ee4dadcc30ec153373c
