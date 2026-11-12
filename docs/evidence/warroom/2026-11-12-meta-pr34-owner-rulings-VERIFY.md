# Verify meta PR #34 — owner rulings 2026-11-12 #5 and #8

- PR: https://github.com/yegamble/vizra/pull/34 (docs/owner-rulings-2026-11-12)
- SHA: e29477f919f08cd21b9dede890d23674ac9a6106 (confirmed via `gh pr view --json headRefOid`, before and after)
- Clone: fresh `git clone` into `/tmp/vzv-vizra-pr34-pe0fbw` (deleted after); macOS, python3, bash
- Rulings text: `origin/chore/warroom-records-2026-11-12d:docs/warroom/OWNER-DECISIONS.md` lines 44 (#5), 47 (#8)
- Budget: QUEUE-owner-rulings, verdict 1
- Diff: 3 files — `s0_foundation.py`, `docs/issues/VZ-ISSUE-004.md`, `docs/quality/features.json` (+9/-5)

## #5 — VZ-OPS-005 in VZ-ISSUE-004
- `**Ledger IDs:**` line now ends `VZ-OPS-003, VZ-OPS-005, VZ-CI-003`.
- Bullets compared with the features.json entry: outcome "Operator: JSON logs, Prometheus metrics, optional OpenTelemetry traces (otel profile OFF/MANAGED/EXTERNAL); sensitive-key denylist enforced." ; success "Metrics endpoint scrapeable; traces exported when enabled" ; privacy "Denylist test" ; evidence_required "scrape transcript; denylist test" — each identical after the `(VZ-OPS-005) ` prefix. negative/recovery are empty in the ledger, so nothing is missing.
- VZ-OPS-005 ledger entry unchanged (per-id diff below).

## #8 — VZ-FOUND-005 via generator
- Generator diff changes only the outcome string and `success` list; schema-behind clause, negative, recovery, api and evidence (EV_OPS) untouched.
- `python3 docs/evidence/ledger-generator/build.py <tmp>` → `cmp` with committed features.json: identical (REGEN_IDENTICAL).
- Per-id comparison against origin/main features.json: 192 vs 192 ids, same set; only changed entry `VZ-FOUND-005`, fields `outcome` and `cases.success`.

## Checks (all exit 0 at the SHA)
| command | result |
|---|---|
| ./scripts/check-generated-ledger.sh | 0; byte-for-byte, UTF-8 and C/POSIX |
| ./scripts/check-ledger-status-output.py | 0; 192 entries |
| test_status via run-unittest-noskip | 0; 38 run, 0 skip |
| test_ledger_status_remote via run-unittest-noskip | 0; 13 run, 0 skip (gh anonymous) |
| ./scripts/check-quality-json.py | 0; all ids resolve |
| ./scripts/check-doc-links.py | 0 |
| ./scripts/check-template-claims.py | 0; 0 violations |

## Mutation (bullet binding)
Changed `- (VZ-OPS-005) Denylist test` → `Denylist tests`.
- Uncommitted: only check-ledger-status-output.py red, with "TREE DIFFERS FROM HEAD" — a dirty-tree guard, not binding.
- Committed (local only): check-ledger-status-output, check-quality-json, check-doc-links, check-template-claims, check-generated-ledger **all exit 0**. Reset to the SHA after.
- Result: **no check binds issue bullets to ledger cases** → F-1 (follow-up: the content of this PR is correct, so nothing is false-green today; the check does not claim to bind bullets).

## CI
`gh pr checks 34`: validate pass (run 43265848177), ci-required pass (run 43265848152), GitGuardian pass; both runs' headSha = e29477f919f08cd21b9dede890d23674ac9a6106, conclusion success. Head unchanged at end.

## Findings
- F-1 FOLLOW-UP: no automated issue-bullet ↔ ledger binding; drift from the ledger in a later edit would go unnoticed. Repro: mutation above.
- F-2 FOLLOW-UP: PR body claims "compose demo + shellcheck reported in comments"; the only PR comment is a Blocks bot advert. Not an acceptance claim.
- No BLOCKING findings.

FINAL VERDICT: PASS — SHA e29477f919f08cd21b9dede890d23674ac9a6106
