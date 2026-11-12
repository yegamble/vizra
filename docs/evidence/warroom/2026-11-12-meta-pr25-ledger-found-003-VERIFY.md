# Independent verification — meta PR #25 (ledger record VZ-FOUND-003 VERIFIED)

- Subject: https://github.com/yegamble/vizra/pull/25, head `bd93f368b327dd61d59f511d87ca831627d137e5` (checked at start and at end; it did not move)
- vizra-core main checked: `a6d4792914337c4835a0587f6c43138c5502efcc`
- Environment: macOS (darwin) local clones in a mktemp scratch dir (deleted at the end); gh CLI; no Docker/PostgreSQL locally (so S1 and R1 rest on CI logs)
- Verifier: independent; did not write PR #25, vizra-core #18 or #19

## Commands
| # | Command (cwd) | Exit | Result |
|---|---|---|---|
| A1 | `git diff --name-only origin/main...HEAD` (meta) | 0 | only status_records.json and features.json |
| A2 | `git diff origin/main...HEAD -- docs/quality/features.json` | 0 | 2 hunks: summary counts (IMPLEMENTED 1, PLANNED 190, VERIFIED 1; UNVERIFIED 191, VERIFIED_AT_SHA 1) and the VZ-FOUND-003 entry; release_status NOT_RELEASED |
| B1 | `cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json`; `git diff --quiet` | 0 / 0 | regenerates with no diff |
| B2 | `python3 scripts/check-ledger-status-output.py` | 0 | |
| B3 | `python3 scripts/check-ledger-status-remote.py` | 0 | `OK: 2 status record(s) proved against GitHub` |
| B4 | `bash scripts/check-generated-ledger.sh` | 0 | (my first run gave 1 because the demo was editing the same clone at the same time; a clean re-run on its own gave 0) |
| B5 | `python3 -m unittest discover -s docs/evidence/ledger-generator -p 'test_*.py'` | 0 | Ran 38, OK |
| B6 | `bash docs/evidence/ledger-status/demo.sh` | 0 | `demo: 61 passed, 0 failed` on the third run. Run 1 had 1 FAIL ("tree not restored"), caused by my B4 running at the same time. Run 2 had 1 FAIL in D3 because the GitHub API returned `Service Unavailable` (infra). Run 3 ran on its own and passed. |
| B7 | `git show origin/main:<evidence>` for both cited files | 0 | both on meta main; last lines are `FINAL VERDICT: PASS — SHA b1c1734f…` and `… 37a6d55b…` |
| C1 | `gh pr view 18/19 -R yegamble/vizra-core` | 0 | both MERGED into main; heads b1c1734f… and 37a6d55b…; merge commits 58d658f1… and a6d47929… |
| C2 | `gh api compare/<merge>...main` | 0 | ahead / identical: both commits are on main |
| C3 | ci-required check-runs on both verified heads | 0 | completed/success on both |
| D1 | `make ci` (vizra-core main) | 0 | `make ci: all lanes passed` |
| D2 | N1: `migrations/0006_x.up.sql` = `ALTER TABLE sites DROP COLUMN handle;` + down file, `./scripts/migration-manifest.sh generate`, `make migrate-lint` | 2 | `FAIL 0006_x.up.sql:1 destructive statement` |
| D3 | N1 with `-- allow-destructive: x` on the line before, regenerate the manifest, `make migrate-lint` | **0** | `migrate-lint: passed`: one comment with a one-character reason is enough to land a DROP COLUMN |
| D4 | N2: append `// x` to internal/store/sqlcgen/audit.sql.go, `make sqlc-verify` | 2 | drift detected; restored, then `make migrate-lint sqlc-verify` exit 0, tree clean |
| D5 | `gh run view --job 131223440387 --log` | 0 | docker-build success on 37a6d55b; runs `vizra-core:ci /usr/local/bin/vizra migrate`; prints `ledger: 5 false` twice |
| D6 | `gh run view --job 131221389383 --log` | 0 | docker-build failure: `CREATE TABLEE broken_on_purpose` fails migrate from the image |
| D7 | `gh run view --job 131217791460 --log` | 0 | build-test failure: `--- FAIL: TestDirtyLedgerIsReportedNotRepaired` |
| D8 | `gh run download 43230273284`; parsed the int / int-shuffle events with `python3 -I` | 0 | TestDirtyLedgerIsReportedNotRepaired `pass` in both runs; 0 skips; exit files 0 |
| D9 | `gh run view 43230273284 --log` | 0 | headSha 37a6d55b, success; `==> migrate-lint` then `migrate-lint: passed`; `==> sqlc-verify` then `internal/store/sqlcgen matches store/queries + migrations`; `make ci: all lanes passed` |
| E1 | check-runs on bd93f368 | 0 | ci-required, validate and GitGuardian all completed/success with head_sha bd93f368… |
| E2 | validate job 131248142512 log | 0 | contains `demo: 61 passed, 0 failed` |

## Results
- A: PASS. B: PASS (mechanical). C: PASS. E: PASS (CI green on the exact SHA).
- D cases: S1 PASS (CI), S2 PASS, N1 PASS for an unmarked drop, N2 PASS, R1 PASS (CI). evidence_required PASS (logs D5 and D9).

## Outcome clauses
| Clause | Verdict | Basis |
|---|---|---|
| migrations append-only | delivered | migrate-lint rule 5, the checksum manifest (`append-only manifest matches`) |
| matching down files where safe | delivered | rule 3: a down file, or `-- no-down: <reason>` |
| compiled into the release binary | delivered | migrations/embed.go; D5 runs `vizra migrate` from the image, `embedded schema version` |
| sqlc generated and drift-checked | delivered | D4, D9 |
| migrate-lint rejects destructive statements inside the compatibility window | **NOT delivered** | D3 |

## Compatibility-window decision
NOT satisfied. A compatibility window exists so that the previous release keeps working against the migrated schema during an upgrade or rollback. migrate-lint.sh:91-92 states exactly that purpose. The outcome promises that destructive statements are *rejected* inside that window. On main there is no window at all. There is a per-statement escape: any `-- allow-destructive:` comment with any non-empty reason (`x` works, D3) passes a `DROP COLUMN` that would break the previous release. No rule ties the marker to a release boundary, and no rule requires a review. So "superset" is wrong: the outcome rejects every destructive statement inside the window with no exceptions, and the implementation accepts any statement that carries a marker. The implementation enforces something weaker, not stronger.

## Rationale, sentence by sentence
- The S1, R1, N2/S2 and build-test sentences match what I saw (D5-D9).
- "Every ledger case … was reproduced by an independent verifier": the cases, yes. It is phrased so that it also implies the outcome was reproduced, and the outcome was not.
- "a reviewed `-- allow-destructive:` marker": UNSUPPORTED. Nothing checks the reason text or requires review. The meta notice itself says CODEOWNERS is advisory, with no branch protection.
- "which the verifier judged a superset of rejecting inside a window": wrong on the facts (above).
- The N1 differential-test claim for #18 was not re-run by me. I accepted it from the #18 evidence file on main.

## Findings
- **BLOCKING (false-green product gate):** VZ-FOUND-003 is recorded VERIFIED, but one clause of its outcome (rejecting destructive statements inside the compatibility window) is not delivered. Reproduced on vizra-core main a6d4792 (D3). The rationale also contains an unsupported claim ("reviewed") and a wrong one ("superset").
- What would be honest: IMPLEMENTED, with a rationale that states the window is not implemented and that markers are unrestricted. VERIFIED needs either a real window rule (refuse `allow-destructive` for changes inside the window) or an owner decision in docs/OPEN_QUESTIONS.md that rewords the outcome.
- FOLLOW-UP: demo.sh and check-generated-ledger.sh both write to the shared tree, so running them at the same time gives false failures (non-blocking).

## Not run
S1 and R1 locally (no Docker/PostgreSQL); I relied on the CI logs and artifacts. I did not re-run #18's differential test.

FINAL VERDICT: FAIL — SHA bd93f368b327dd61d59f511d87ca831627d137e5
