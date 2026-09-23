# Execution plan: vizra-core queue 2t, the M1-A owner-claim sentinel follow-ups (S-0002…S-0007, S-0009, S-0010)

## Context
- Repo: `vizra-core`. Worktree `/Users/yosefgamble/github/vizra/.claude/worktrees/core-2t`, branch `fix/m1a-sentinel-followups`, base `origin/main` = `a6bc77d` (B3 merged).
- Out of bounds: the `Makefile`, the pins (`.github/pinned-*.yml`), `internal/fixtures` (another builder, test stability), and meta S-0008.
- Sources:
  - `/Users/yosefgamble/github/vizra/docs/sentinel/FINDINGS.md`
  - the sweep `/Users/yosefgamble/github/vizra/docs/sentinel/sweeps/2026-09-23-bugs-core-m1a-owner-claim.md` (F1…F6, F8, F9 = S-0002…S-0007, S-0009, S-0010)
  - `docs/sentinel/RULES.md` R16 (upsert must not resurrect a terminal state), R17 (validator equals the constraint), R18 (`%w` where a caller branches)
- Requirement: VZ-INSTALL-003 (owner claim).

## Acceptance (each red on a6bc77d first)
1. **S-0002:** `MintOwnerClaimToken`'s `ON CONFLICT … DO UPDATE` gets `WHERE owner_claim_tokens.consumed_at IS NULL`.
   - A re-mint racing an in-flight claim returns `ErrHasUsers`, leaves no live token, and keeps the consumed generation's `consumed_at`.
   - Tested with the raw CTE held open, and through the real HTTP claim with a test-only slow audit trigger.
2. **S-0003:** the Go email validator uses the DDL's own literal (`^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$`).
   - It also refuses any Unicode space or control rune, so it is at least as strict as `[:space:]` under any libc locale, and refuses NUL, which `text` cannot hold.
   - `TestValidatorsMatchTheMigration` compares the email expression literally.
   - An integration corpus test runs Go and the migration's own CHECK expression over the same inputs and requires that Go never accepts what the database refuses.
   - SQLSTATE 22021 maps to 400.
3. **S-0004:** one `rate_limited` row per bucket per window, keyed per bucket and naming it truthfully: `ceiling.claim`, `ceiling.status`, `per_origin`, `global`. So a 429 on the operator's valid token is audited.
4. **S-0005:**
   - `ownerclaim.unavailable` wraps the cause with `%w`.
   - A request whose own context has ended answers 503 without logging "could not reach the database".
   - The check is on the REQUEST context, not on `errors.Is(err, DeadlineExceeded)`: a pgx connect timeout also wraps DeadlineExceeded, and that is a real outage.
5. **S-0006:** the claim-status 503, the unclaimed-guard 503 and the `poolFor` 503 go through `s.unavailable`, so the redacted cause is logged once.
6. **S-0007:**
   - The `succeeded` row's `after` carries `token_generation`.
   - Migration 0006 adds a CHECK (`NOT VALID`, so existing dev rows are not rewritten) that a `setup.owner_claim.succeeded` row names a numeric `token_generation`.
7. **S-0009:** the claim body's keys must match exactly (case-sensitive), and the body must end after one object: a trailing `}` or `]` is 400.
8. **S-0010:** `VIZRA_OWNER_CLAIM_TTL` below 1m is refused at config load.

## Verification
- Focused unit and integration tests.
- `make ci`.
- The unit report plus `--emit-floors`.
- Integration on Valkey 9.1.2 and Redis 7.2.16 (plain and shuffled), in own containers, with `TMPDIR` in scratch.

## Progress and evidence
State: IMPLEMENTED, READY_FOR_REVIEW. Head **`75e0a9510dcb92f3b7b9b880bbadb17960ffa18d`**. PR https://github.com/yegamble/vizra-core/pull/14

- Commit `6090b64` on `fix/m1a-sentinel-followups` (base a6bc77d).
- Transcripts: `/private/tmp/claude-501/-Users-yosefgamble-github-vizra/7321b930-95d2-4a95-ba2e-61ef2ce3c13c/scratchpad/q2t.G0PC/`.
- Containers: `vizra-q2t-{pg,valkey,redis72}-<n>` (the n is in `suffix`). `TMPDIR` points at scratch.
- Files:
  - `store/queries/owner_claim.sql` and the regenerated `internal/store/sqlcgen/{owner_claim.sql.go,querier.go}`
  - `internal/ownerclaim/ownerclaim.go`
  - `internal/httpapi/{setup.go,setup_limits.go,middleware.go}`
  - `internal/config/{config.go,keys.go}` and `.env.example`
  - `migrations/0006_audit_claim_succeeded_generation.{up,down}.sql` and `migrations/manifest.sha256`
  - `AGENTS.md`
  - tests: `internal/integration/owner_claim_followups_test.go` (new) and `owner_claim_test.go`
  - `internal/{httpapi/setup_test.go,httpapi/logsites_test.go,ownerclaim/ownerclaim_test.go,config/config_test.go}`
- Red on a6bc77d, with the new tests only:
  - unit (`red-unit.txt`): the TTL bound 4/4, `TestValidatorsMatchTheMigration`, the rune refusal, and the 22021 mapping;
  - integration (`red-integration.txt`): every new test except the "a second object" control, which was already refused by `dec.More()`.
- Green after the fix: `green-integration.txt`, 24 PASS lines.
- Mutations on the fixed tree (`mut-M*.txt`). Each is red on its intended test:

| Mutation | Red test |
|---|---|
| M1: consumed guard removed | both re-mint races |
| M2: rune refusal removed | the corpus and 400 tests |
| M3: 22021 branch removed | `TestClaimErrorMapping` |
| M4: ceiling.claim audit removed | the ceiling test and `TestARateLimitedClaimWritesNoAuditRow` |
| M5: shared marker | the per-origin/global test |
| M6: unclaimed-only gate removed | `TestACeilingOnAClaimedInstanceWritesNoRateLimitedRow`, added after the first M6 run was GREEN (the gate was untested) |
| M7: `s.unavailable` logs ended requests | the cancellation test |
| M8: the error handler logs ended requests | the cancellation test |
| M9, M10, M11: each 503 drops its cause | its own sub-test |
| M12: no generation in `after` | the succeeded-row test, and the migration's CHECK then fails every claim (the IPv6 loopback claim tests) |
| M13: case-folded keys | the strict-decode case tests |
| M14: `dec.More()` instead of the EOF check | the trailing-`}]` test |
| M15: no TTL bound | the TTL test |
| M16: `%v` instead of `%w` | `TestUnavailableKeepsItsCauseInspectable` |

- Changed existing test: `TestARateLimitedClaimWritesNoAuditRow`.
  - It asserted exactly 1 `rate_limited` row in total. The semantics are now one per bucket, so it asserts exactly `{per_origin:1, global:1}` after the transitions and `{per_origin:1, global:1, ceiling.claim:1}` after 600 more.
  - This is stricter than before, not looser.
- Log-site count in `internal/httpapi` went from 6 to 7: the new 22021 branch.

| Command | Rev | Exit | Result |
|---|---|---|---|
| `make ci` | 6090b64, 75e0a95 | 0, 0 | all lanes passed |
| unit `go test -race -count=1 -json ./...` + report | 6090b64 | 0/0 | 1575 executed, 0 skips |
| integration Valkey 9.1.2 plain / shuffled | 6090b64 | 0/0, 0/0 | 1769 / 1769 |
| integration Redis 7.2.16 plain / shuffled | 6090b64 | 0/0, 0/0 | 1769 / 1769 |
| `--emit-floors` (unit, and Valkey integration) | 6090b64 | — | applied in 75e0a95: config 94, httpapi 86, ownerclaim 18, integration 165, scripts 419 (core #13's growth), min_tests 1339 / 1504; all five streams re-judged: ok |

The host load average was 16–45 during the runs, and no timeouts this time.

## Blockers and handoff
- No blocker. The gate is the verifier plus `ci-required` on 75e0a95.
- A possible merge conflict in `scripts/test-floors.json` with the core test-stability builder: they may also be editing that file.
