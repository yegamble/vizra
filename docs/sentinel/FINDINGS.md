# Sentinel findings register

This is the register of findings from the sentinel team (`.claude/agents/sentinel/`). Only the chair edits it. Sentinels write sweep files under `docs/sentinel/sweeps/` and PR reviews under `docs/sentinel/pr/`, and the chair merges them into this register, de-duplicating by key.

**Status values:**
- `CONFIRMED`: reproduced by the sentinel;
- `ROUTED`: queued on `docs/plans/WARROOM-BOARD.md` or sent to a builder;
- `FIXED`: the fixing PR merged, and a verifier re-ran the reproducer;
- `FALSE-POSITIVE`: disproved, with the reason;
- `WONTFIX`: an owner decision.

A finding enters the register only if it is CONFIRMED. A `FALSE-POSITIVE` becomes a lesson in `RULES.md`, or a note on what the sentinel must check before reporting, so that it does not recur.

| ID | Dedupe key | Severity | Status | Found by / sweep | Repro | Routed to | Fixed by |
|---|---|---|---|---|---|---|---|
| S-0001 | `vizra-core:internal/integration/healthcheck_test.go:tempdir-leak` | MINOR | ROUTED | core B3 builder, 2026-09-23 (seeded) | 74 MB `vizra-healthcheck-bin-*` left per integration run; 168 found | board queue 2s | — |
