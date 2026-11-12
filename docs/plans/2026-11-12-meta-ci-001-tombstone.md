# VZ-CI-001 part 2 (meta): lane tombstones

- S1: `scripts/check-required-tombstones.sh` + 16 cases in `tests/ci/test_required_tombstones.sh`, run in the `ci-required` job (step "a retired lane carries a tombstone"). No new check name.
- R1/N1/S2: `tests/ci/test_ci_required_select.sh` (11 cases: omitted lane, empty selection, renamed job, skipped/cancelled/timed_out/neutral, stale success masking a newer failure, pending, empty required list).
- Red first: tombstone tests 0/16 before the checker existed; select tests fail `skipped` under a mutation that lets `skipped` pass.
- Evidence: one breakage commit deleting a manifest line with no tombstone, then restore; URLs in the PR body.
- Open: unittest skips inside a lane still exit 0 (no skip decorators exist today); `tests/warroom` unittest is not run by any CI lane.
