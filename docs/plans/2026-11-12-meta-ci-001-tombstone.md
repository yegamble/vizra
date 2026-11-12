# VZ-CI-001 part 2 (meta): lane tombstones

- S1: `scripts/check-required-tombstones.sh` + 16 cases in `tests/ci/test_required_tombstones.sh`, run in the `ci-required` job (step "a retired lane carries a tombstone"). No new check name.
- R1/N1/S2: `tests/ci/test_ci_required_select.sh` (11 cases: omitted lane, empty selection, renamed job, skipped/cancelled/timed_out/neutral, stale success masking a newer failure, pending, empty required list).
- Red first: tombstone tests 0/16 before the checker existed; select tests fail `skipped` under a mutation that lets `skipped` pass.
- Evidence: one breakage commit deleting a manifest line with no tombstone, then restore; URLs in the PR body.
- N1 (session 2): `scripts/run-unittest-noskip.py` replaces `python3 -m unittest` in validate step "the ledger-status rules hold (unit tests)" (test_status: 38 run; test_ledger_status_remote: 13 run; 0 skipped). It fails on any skip, expected failure, unexpected success, or zero tests run. 8 cases in `tests/ci/test_run_unittest_noskip.sh` (red first: 2/8 failed before the runner existed), run in the same step. Both `demo.sh` drivers now fail when zero demonstrations pass. The `tests/ci` drivers already had a case floor.
- Remaining: `tests/warroom` is not run by any CI lane. Wiring it in is reserved for owner review. The pre-existing shellcheck findings in both demo.sh files are not touched here.
