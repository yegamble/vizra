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
| S-0002 | `vizra-core:store/queries/owner_claim.sql:remint-racing-claim-mints-on-claimed-instance` | MINOR | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | remint racing a claim: live gen-2 token on a claimed instance; gen-1 consumption record lost; 3/3 | board queue 2t | — |
| S-0003 | `vizra-core:internal/ownerclaim:email-validator-diverges-from-ddl` | MINOR | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | NUL → 500 (22021 unmapped); VT/U+2003 hit the 23514 fallback; validator test skips the email expression | board queue 2t | — |
| S-0004 | `vizra-core:internal/httpapi/setup_limits.go:rate-limited-audit-not-per-bucket` | MINOR | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | shared marker key; hard ceilings write no row — the operator's valid token 429ed leaves no audit | board queue 2t | — |
| S-0005 | `vizra-core:internal/ownerclaim:cancellation-logged-as-db-unreachable` | MINOR | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | `unavailable` wraps with %v, so a client disconnect logs ERROR "could not reach the database" | board queue 2t | — |
| S-0006 | `vizra-core:internal/httpapi:claim-status-503-without-cause-log` | MINOR | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | claim-status and the unclaimed guard return 503 without logging the cause | board queue 2t | — |
| S-0007 | `vizra-core:audit:succeeded-row-lacks-token-generation` | MINOR | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | 0005 says traceable by generation; the succeeded row omits it | board queue 2t | — |
| S-0008 | `vizra\|vizra-core:compose-env:owner-claim-keys-not-plumbed` | MINOR | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | `VIZRA_OWNER_CLAIM_ANNOUNCE`/`_TTL` not passed by compose/registry; `claim-token` missing from the command list; meta `check-config-coverage.py --drift` flags them locally | board queue 2t (meta part) | — |
| S-0009 | `vizra-core:internal/httpapi:strict-decode-accepts-case-and-trailing` | NIT | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | upper-case keys and a trailing `}]` accepted | board queue 2t | — |
| S-0010 | `vizra-core:internal/config:owner-claim-ttl-unbounded-low` | NIT | ROUTED | sentinel-bugs, sweep `2026-09-23-bugs-core-m1a-owner-claim` | TTL `500ns` accepted; every mint then fails the DB TTL check | board queue 2t | — |
