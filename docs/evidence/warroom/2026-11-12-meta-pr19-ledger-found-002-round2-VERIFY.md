# meta PR #19 (ledger record VZ-FOUND-002 IMPLEMENTED) — second independent verification, round 2

- Subject: https://github.com/yegamble/vizra/pull/19, branch `ledger/vz-found-002-implemented`
- SHA verified: 5d8d281e8824820d457887b1b05147be046d032f (PR head at start: same; at end: same, OPEN)
- origin/main at verification: 449818fec2cd284b4031a67cb52160ed772ce55d (= merge-base with the head)
- Verifier: fresh; wrote neither the record nor the first verdict (`2026-11-12-meta-pr19-ledger-found-002-VERIFY.md`, FAIL at 4eb6249 for the stale demo case D11 only).
- Environment: macOS Darwin 25.5.0 arm64, Python 3.9.6, git, gh; fresh clone of yegamble/vizra in a `mktemp -d` scratch directory (two copies: one for demo.sh, one for the other checks), deleted by exact path at the end. Nothing edited, committed, pushed, merged or re-run.

## Commands

| # | Command | Exit | Result |
|---|---|---|---|
| A1 | `git diff 4eb6249447502d4aaee9aa2702df8ed7c4d1360c 5d8d281e… -- docs/evidence/ledger-generator/status_records.json docs/quality/features.json \| wc -c` | 0 | 0 bytes (empty) |
| A2 | `git diff --name-only origin/main...HEAD` | 0 | exactly `docs/evidence/ledger-generator/status_records.json`, `docs/quality/features.json` |
| A3 | `cat docs/evidence/ledger-generator/status_records.json` | 0 | one record: VZ-FOUND-002, IMPLEMENTED, merges core #18 (b1c1734… / 58d658f…) and user #12 (a3b8f94… / 53a39a8…), no `evidence_file` key, three acceptance bullets |
| B1 | `cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json` | 0 | `statuses={'IMPLEMENTED': 1, 'PLANNED': 191}`; `git status --porcelain` empty afterwards |
| B2 | `python3 scripts/check-ledger-status-output.py` | 0 | 192 entries, 1 carries a status, 1 record, sets equal |
| B3 | `python3 scripts/check-ledger-status-remote.py` | 0 | both merge commits on their repo's main (compare: identical); 1 record proved against GitHub |
| B4 | `bash scripts/check-generated-ledger.sh` | 0 | reproduces byte-for-byte, UTF-8 and C/POSIX |
| B5 | `python3 -m unittest discover -s docs/evidence/ledger-generator -p 'test_*.py'` | 0 | Ran 38 tests, OK |
| B6 | `python3 scripts/check-quality-json.py` | 0 | 4 files parsed, 192 ids, every reference resolves |
| B7 | `python3 scripts/check-doc-links.py` | 0 | 32 relative links resolve |
| B8 | `bash docs/evidence/ledger-status/demo.sh > $D/demo.log 2>&1` (background, separate clone copy) | 0 | last line `demo: 61 passed, 0 failed`; porcelain empty afterwards |
| C1 | `gh pr view 18 -R yegamble/vizra-core --json state,headRefOid,mergeCommit,baseRefName` | 0 | MERGED into main, head b1c1734f583a46f7abc295dcc55094f9d3f5717e, merge 58d658f128ed7dc4be7a218ae0cd5744b87d0601 |
| C2 | `gh pr view 12 -R yegamble/vizra-user --json …` | 0 | MERGED into main, head a3b8f942d566513b155971384bd2ee6b161d4520, merge 53a39a889ba0f456bbfdd4df7d5f241c12e7a1b5 |
| C3 | `gh api repos/yegamble/vizra-core/compare/58d658f…...main` | 0 | identical (ahead 0, behind 0) |
| C4 | `gh api repos/yegamble/vizra-user/compare/53a39a8…...main` | 0 | identical (ahead 0, behind 0) |
| C5 | `gh api repos/yegamble/vizra-core/commits/b1c1734…/check-runs` (ci-required) | 0 | success |
| C6 | `gh api repos/yegamble/vizra-user/commits/a3b8f94…/check-runs` (ci-required) | 0 | success |
| D1 | read features.json entry VZ-FOUND-002 (python json walk) | 0 | implementation_status IMPLEMENTED, verification_status UNVERIFIED, merge_status MERGED, release_status NOT_RELEASED; cases S1, S2, N1 |
| D2 | `grep -n` in docs/issues/VZ-ISSUE-001.md | 0 | the three bullets verbatim at lines 17-19, under `## Acceptance (observable)` (line 13; next heading line 33) |
| D3 | `grep -n` docs/warroom/FOLLOWUPS.md | 0 | line 49 (worker mux outside the contract walk), line 58 (no CI checks the vendored contract against core main) |
| D4 | read first verdict section D + D1-D8 rows; core #18 round 3 (lines 184, 193) and round 1 (lines 21, 32, 115); user #12 verdict (lines 5, 16-17, 34-35, 62, 70-75) | 0 | see "D" below |
| E1 | `gh run list -R yegamble/vizra --commit 5d8d281e…` | 0 | `ci-required` run 43212702693 success, `validate` run 43212702534 success, both headSha 5d8d281e8824820d457887b1b05147be046d032f, event pull_request |
| E2 | `gh run view 43212702534 -R yegamble/vizra --log \| grep -n 'demo:' \| tail -2` | 0 | step "every ledger-status guard still fails against a controlled mutation": `demo: 61 passed, 0 failed` (2026-11-12T11:52:03Z) |
| E3 | `gh pr view 19 -R yegamble/vizra --json state,headRefOid` (end) | 0 | OPEN, 5d8d281e8824820d457887b1b05147be046d032f |

## Results per claim

**A — PASS.** The record and the generated ledger are byte-identical to what the first verifier judged at 4eb6249; the PR differs from main in exactly the two files; the record's content is as stated.

**B — PASS.** All seven mechanical checks exit 0, tree clean after the build, demo 61 passed, 0 failed locally.

**C — PASS.** Both PRs merged with the recorded heads and merge commits; each merge commit is the tip of its repo's main; `ci-required` success on each verified head.

**D — PASS.** Rationale sentence by sentence:

1. "All three ledger cases are delivered on main and each was reproduced by an independent verifier." Supported: first verdict D2-D4 (S1), D6-D7 (S2), D8 (N1) on the component mains; core round 3 line 184/193; user verdict lines 70-71.
2. S1, "core #18 made the contract test walk wildcard routes and fail closed on shapes it cannot map; the verifier's own mutations on the real router went red in both directions." Supported: first verdict D2 (route without spec), D3 (wildcard `/files/*` named as `/files/{path}`), D4 (spec without route). "Fail closed on shapes it cannot map" is not shown in the round-3 file itself; it is shown in the round-1 verdict that round 3 cites (`2026-11-11-vizra-core-pr18-3a-VERIFY.md` on main, lines 21 and 32: 11 wildcard/unmappable subtests red when the skip is re-inserted), and round 3 records `git diff a627e1f b1c1734 -- internal/` empty.
3. S2/N1, "user #12 re-vendored the contract at core 5f615d7 and added an exact six-operation test; the verifier re-vendored from core main with no diff and saw the drift check reject a hand edit." Supported: user verdict lines 5, 16-17 (core main = 5f615d7 then; re-vendor + codegen, `git status --short` empty), line 34 (hand edit → exit 1), lines 35 and 70 (exact-set test, "expected six").
4. "IMPLEMENTED, not VERIFIED: … every red run so far is a verifier-local transcript." Supported: core round 3 line 193; user verdict lines 71, 73, 75; first verdict section D.
5. "Known limits, recorded in docs/warroom/FOLLOWUPS.md …" Supported: FOLLOWUPS.md lines 58 and 49.

No sentence is unsupported. Each ledger case has a named proof (S1: `TestEveryRouteHasASpecOperation`, `TestEverySpecOperationHasARoute`, `TestContractDriftOnSyntheticRouteTables`; S2: `contract` lane `check:contract` + `git diff --exit-code`; N1: `check:contract` exit 1 on a hand edit). The record does not claim VERIFIED; verification_status is UNVERIFIED and release_status NOT_RELEASED. The three bullets exist verbatim under `## Acceptance (observable)`.

**E — PASS.** `ci-required` and `validate` both success on headSha 5d8d281e8824820d457887b1b05147be046d032f; the CI log shows `demo: 61 passed, 0 failed`. The first verdict's only blocking finding (F1, stale D11) is closed.

## Findings

| ID | Severity | Finding |
|---|---|---|
| — | BLOCKING | none |
| R2-F1 | FOLLOW-UP | Rationale sentence 2's "fail closed on shapes it cannot map" rests on the core #18 round-1 verdict, not the round-3 file; a later VERIFIED record should cite both (and round 3 is still not on meta main — first verdict F2). |
| R2-F2 | FOLLOW-UP | First verdict F3-F5 stand unchanged (API metrics listener omitted from known limits; no rule orders a record after its dependency VZ-FOUND-001; manifest source_commit 5f615d7 vs core main 58d658f, no CI compares). |

## Not run

- The component-repo mutations (first verifier's D1-D8): by instruction, read only, not repeated.
- The vizra-user six-operation test source was not opened; its existence and behaviour are taken from the user #12 verdict (lines 35, 70).
- No CI re-run, no change to any GitHub setting. This is a verdict on the PR and on the honesty of an IMPLEMENTED record; it does not make VZ-FOUND-002 VERIFIED and is not release approval.

FINAL VERDICT: PASS — SHA 5d8d281e8824820d457887b1b05147be046d032f
