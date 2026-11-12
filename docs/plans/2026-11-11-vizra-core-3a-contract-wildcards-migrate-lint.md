# Execution plan: VZ-FOUND-002 (core half) and VZ-FOUND-003: contract gate walks wildcard routes; migrate-lint catches every DROP column spelling

## Context
Repo yegamble/vizra-core, base origin/main 5f615d7, branch `fix/contract-wildcards-migrate-lint`, worktree `.claude/worktrees/core-3a`, PR https://github.com/yegamble/vizra-core/pull/18. Source of the holes: `docs/evidence/warroom/2026-11-10-found-002-003-006-AUDIT.md`.

## Acceptance
| ID | Case | State after this PR |
|---|---|---|
| VZ-FOUND-002 | S1 "Adding a route without spec fails; spec without route fails" | **Closed by this PR** for the reproduced hole: wildcard (and parameter) routes are now compared, unmappable shapes fail. Plain routes held before. |
| VZ-FOUND-002 | S2 "Generated client diff is empty after regeneration" | Stays open: vizra-user, queue 3b. |
| VZ-FOUND-002 | N1 "Hand-edited generated file is rejected by a drift check" | Not this PR: held before, in vizra-user. |
| VZ-FOUND-003 | S1 "`migrate up` from the release image applies cleanly on empty DB" | Stays open: no lane runs it from the image; out of scope. |
| VZ-FOUND-003 | S2 "sqlc-verify passes" | Held before, still green (`make sqlc-verify` exit 0). |
| VZ-FOUND-003 | N1 "A DROP COLUMN in *.up.sql fails migrate-lint" | **Closed by this PR** for the reproduced hole: `DROP name` without COLUMN and DROP/COLUMN split across lines now fail. |
| VZ-FOUND-003 | N2 "Editing sqlcgen output fails drift check" | Held before; untouched. |
| VZ-FOUND-003 | R1 "Dirty migration ledger is detected and reported, not auto-fixed" | Stays open: behaviour exists, no test; out of scope. |
| VZ-FOUND-003 | outcome's "compatibility window" | Stays open: migrate-lint has no window, only the `-- allow-destructive:` line exemption. None invented here. |

Non-goals: the worker mux (F002-M4), a compatibility window, statement-level parsing of rules other than column drops.

## Implementation
### Wildcard mapping decision
The comparison is made on the OpenAPI spelling (`contractOperations` / `openAPIPath` in `internal/httpapi/openapi_contract_test.go`):

- `/photos/:id` <-> `/photos/{id}`: a whole-segment parameter keeps its name.
- `/files/*` <-> `/files/{path}`: a trailing wildcard is the parameter named `path`. The name is fixed so a route has exactly one spelling in the spec; `/files/{name}` does not satisfy `/files/*`.
- Fails closed, never skips: a wildcard that is not the whole last segment, a parameter that is only part of a segment, a `:path` parameter beside a wildcard, a literal brace, a path without a leading `/`, a method that is not one of the eight OpenAPI methods.
- Limit: OpenAPI 3.0 cannot say that `{path}` may contain `/`. The gate compares the route table, not that.

### migrate-lint: what changed and its limits
The per-line pattern list is unchanged. Column drops are additionally found per statement by an awk tokenizer (`column_drops`): `--` and nested `/* */` comments dropped; strings, quoted identifiers and `$tag$` bodies opaque; tokens joined up to `;` or end of file. In an `ALTER TABLE` statement, a `DROP` outside parentheses is reported unless it is `DROP CONSTRAINT` (left to the line rule, as before) or `DROP DEFAULT | NOT NULL | EXPRESSION | IDENTITY` inside an `ALTER [COLUMN] name` action. `ALTER TABLE t DROP identity` is a column drop and is reported.

`-- allow-destructive: <reason>` on the line before the match works as before. One addition: for a column drop found per statement, the comment may also sit on the line before the statement (fixture `allow-destructive-split`).

Limits:
- The inside of a dollar-quoted body or a string is not parsed: `DO $$ ... $$` and `EXECUTE 'ALTER TABLE ...'` are seen only by the old line pattern.
- `E'...'` strings with backslash-escaped quotes and psql meta-commands are not understood.
- Only `ALTER TABLE` is parsed per statement. `DROP CONSTRAINT`, `RENAME`, `ALTER COLUMN ... TYPE`, `ALTER FOREIGN TABLE` and `ALTER TYPE ... DROP ATTRIBUTE` stay per-line, so `DROP` and `CONSTRAINT` on separate lines still pass (not in this slice; follow-up).

### Fixtures and where they run
19 new directories under `scripts/testdata/migratelint/`: 12 must fail, 7 must pass. They run in `TestMigrateLintFixtures` (`scripts/scripts_test.go`), which `go test ./...` in `make ci` already runs, so no lane wiring was needed.

### F002-M4 (reported, not changed)
The worker mux (`cmd/worker/main.go:91-94`) serves more than its probes: `/` is the Prometheus handler for every path that is not `/readyz` or `/healthz`. The contract test does not walk that mux, and a route added there still leaves it green.

## Verification
See the command table under Progress. Docker/PostgreSQL lanes are not run locally; CI is their evidence.

## Progress and evidence
State: READY_FOR_REVIEW (not verified). Environment: darwin arm64, bash 3.2.57, local worktree.

### Commands (local, a627e1f, darwin arm64, each through `quiet.sh`)
| Command | Exit | Result |
|---|---|---|
| `go test -count=1 -v ./internal/httpapi/ -run 'TestContractDrift\|TestEvery'` | 0 | 33 PASS lines (20 synthetic cases + both directions on the real router) |
| `go test -count=1 -v ./scripts/ -run TestMigrateLint` | 0 | 36 PASS lines (34 fixtures, 19 new) |
| `gofmt -l .` | 0 | empty |
| `go vet ./...` | 0 | |
| `make migrate-lint` | 0 | real migrations pass, manifest matches |
| `make openapi-verify` | 0 | |
| `make sqlc-verify` | 0 | sqlcgen matches |
| `./scripts/ci-required-guard.sh` | 0 | 6 required checks |
| `make ci` | 0 | "all lanes passed", 20 packages ok |
| `shellcheck scripts/migrate-lint.sh` | 1 | one warning, SC2207 at line 59, identical on base 5f615d7 (also exit 1); nothing from the new code. Left alone as out of scope. |

Not run locally: Docker/PostgreSQL lanes (image build, image scan, DB-backed integration tests). CI is their evidence.

### (a) Red before the fix: commit a32d222 (tests and fixtures, old code)
```
$ go test ./internal/httpapi/ -run "TestContractDrift|TestEvery"   -> exit 1
  16 subtests of TestContractDriftOnSyntheticRouteTables FAIL, e.g.
  wildcard_route_without_spec: routes without a spec operation: got [], want [GET /files/{path}]
$ go test ./scripts/ -run TestMigrateLintFixtures   -> exit 1
  12 FAIL: drop-bare, drop-bare-if-exists, drop-bare-mixed-case, drop-bare-whitespace, drop-bare-quoted,
  drop-bare-named-identity, drop-bare-split-lines, drop-column-split-lines, drop-multi-action,
  drop-multi-action-split, drop-column-comments-between, drop-no-semicolon
```
After the fix (a627e1f): both exit 0.

### (b) Controlled mutations after the fix (run in a scratch copy of a627e1f made with git archive)
```
### M1 re-introduce the '*' skip in contractOperations (scratch copy of HEAD)
FAIL m1-skip exit 1 (2s) log: /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T//vizra-gate-logs/m1-skip-20261111-114530-82172.log
1:--- FAIL: TestContractDriftOnSyntheticRouteTables (0.00s)
2:    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route_without_spec (0.00s)
4:    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route_with_its_mapped_spec_path (0.00s)
6:    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route,_spec_has_another_method (0.00s)
8:    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route,_spec_names_the_parameter_differently (0.00s)
10:    --- FAIL: TestContractDriftOnSyntheticRouteTables/root_wildcard_without_spec (0.00s)
12:    --- FAIL: TestContractDriftOnSyntheticRouteTables/parameter_and_wildcard (0.00s)
14:    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_wildcard_in_the_middle (0.00s)
16:    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_wildcard_glued_to_a_segment (0.00s)
18:    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_two_wildcards (0.00s)
20:    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_parameter_already_named_path_next_to_a_wildcard (0.00s)
22:    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_not_an_HTTP_method (0.00s)
--- FAIL: TestContractDriftOnSyntheticRouteTables (0.00s)
    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route_without_spec (0.00s)
        openapi_contract_test.go:251: routes without a spec operation: got [], want [GET /files/{path}]
    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route_with_its_mapped_spec_path (0.00s)
        openapi_contract_test.go:254: spec operations without a route: got [GET /files/{path}], want []
    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route,_spec_has_another_method (0.00s)
        openapi_contract_test.go:251: routes without a spec operation: got [], want [GET /files/{path}]
    --- FAIL: TestContractDriftOnSyntheticRouteTables/wildcard_route,_spec_names_the_parameter_differently (0.00s)
        openapi_contract_test.go:251: routes without a spec operation: got [], want [GET /files/{path}]
    --- FAIL: TestContractDriftOnSyntheticRouteTables/root_wildcard_without_spec (0.00s)
        openapi_contract_test.go:251: routes without a spec operation: got [], want [GET /{path}]
    --- FAIL: TestContractDriftOnSyntheticRouteTables/parameter_and_wildcard (0.00s)
        openapi_contract_test.go:254: spec operations without a route: got [GET /u/{user}/files/{path}], want []
    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_wildcard_in_the_middle (0.00s)
        openapi_contract_test.go:257: unmappable routes: got 0 [], want 1
    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_wildcard_glued_to_a_segment (0.00s)
        openapi_contract_test.go:257: unmappable routes: got 0 [], want 1
    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_two_wildcards (0.00s)
        openapi_contract_test.go:257: unmappable routes: got 0 [], want 1
    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_parameter_already_named_path_next_to_a_wildcard (0.00s)
        openapi_contract_test.go:257: unmappable routes: got 0 [], want 1
    --- FAIL: TestContractDriftOnSyntheticRouteTables/unmappable:_not_an_HTTP_method (0.00s)
        openapi_contract_test.go:257: unmappable routes: got 0 [], want 1
exit 1

### M2 scripts/migrate-lint.sh reverted to 5f615d7 (scratch copy)
FAIL m2-lint exit 1 (2s) log: /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T//vizra-gate-logs/m2-lint-20261111-114532-82272.log
1:--- FAIL: TestMigrateLintFixtures (1.37s)
2:    --- FAIL: TestMigrateLintFixtures/drop-bare (0.04s)
7:    --- FAIL: TestMigrateLintFixtures/drop-bare-if-exists (0.03s)
12:    --- FAIL: TestMigrateLintFixtures/drop-bare-mixed-case (0.03s)
17:    --- FAIL: TestMigrateLintFixtures/drop-bare-whitespace (0.03s)
22:    --- FAIL: TestMigrateLintFixtures/drop-bare-quoted (0.03s)
27:    --- FAIL: TestMigrateLintFixtures/drop-bare-named-identity (0.04s)
32:    --- FAIL: TestMigrateLintFixtures/drop-bare-split-lines (0.04s)
37:    --- FAIL: TestMigrateLintFixtures/drop-column-split-lines (0.03s)
42:    --- FAIL: TestMigrateLintFixtures/drop-multi-action (0.03s)
47:    --- FAIL: TestMigrateLintFixtures/drop-multi-action-split (0.03s)
52:    --- FAIL: TestMigrateLintFixtures/drop-column-comments-between (0.03s)
57:    --- FAIL: TestMigrateLintFixtures/drop-no-semicolon (0.03s)
    --- FAIL: TestMigrateLintFixtures/drop-bare-named-identity (0.04s)
    --- FAIL: TestMigrateLintFixtures/drop-bare-split-lines (0.04s)
    --- FAIL: TestMigrateLintFixtures/drop-column-split-lines (0.03s)
    --- FAIL: TestMigrateLintFixtures/drop-multi-action (0.03s)
    --- FAIL: TestMigrateLintFixtures/drop-multi-action-split (0.03s)
    --- FAIL: TestMigrateLintFixtures/drop-column-comments-between (0.03s)
    --- FAIL: TestMigrateLintFixtures/drop-no-semicolon (0.03s)
exit 1

### M3 the audit's reproducer on the real router: e.GET("/files/*") + claimGuardedRoutes entry, no spec (scratch copy; exited 0 on 5f615d7)
FAIL m3-real exit 1 (1s) log: /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T//vizra-gate-logs/m3-real-20261111-114542-83471.log
1:--- FAIL: TestEveryRouteHasASpecOperation (0.00s)
--- FAIL: TestEveryRouteHasASpecOperation (0.00s)
          GET /files/{path}
exit 1
```
The scratch copy was discarded; the branch is unmutated and green.

## Blockers and handoff
None blocking. Follow-ups: split-line DROP CONSTRAINT and the other per-line rules; pre-existing shellcheck SC2207 at scripts/migrate-lint.sh:59; F002-M4.

## Fix round 1 (F1)

Finding: one `-- allow-destructive:` marker before a multi-line ALTER TABLE also exempted a different statement on the line of its DROP. Fix (commit 84f8ad1): the statement-level exemption applies only to a line holding tokens of no other statement; otherwise the line is judged by the line before it, as on main.

### Before — script at a627e1f (three must-fail fixtures accepted: RED)

```
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-other-drop-table
migrate-lint: scripts/testdata/migratelint/allow-destructive-other-drop-table
  ok    1 migrations form a gapless 1..1 sequence
  ok    0001_x.up.sql:3 destructive statement with a stated reason
migrate-lint: passed
exit=0
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-other-drop-column
migrate-lint: scripts/testdata/migratelint/allow-destructive-other-drop-column
  ok    1 migrations form a gapless 1..1 sequence
  ok    0001_x.up.sql:3 destructive statement with a stated reason
migrate-lint: passed
exit=0
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-other-rename
migrate-lint: scripts/testdata/migratelint/allow-destructive-other-rename
  ok    1 migrations form a gapless 1..1 sequence
  ok    0001_x.up.sql:3 destructive statement with a stated reason
migrate-lint: passed
exit=0
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-split-alone
migrate-lint: scripts/testdata/migratelint/allow-destructive-split-alone
  ok    1 migrations form a gapless 1..1 sequence
  ok    0001_x.up.sql:3 destructive statement with a stated reason
migrate-lint: passed
exit=0
```

### After — script at 84f8ad1 (three rejected, the must-pass still passes)

```
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-other-drop-table
migrate-lint: scripts/testdata/migratelint/allow-destructive-other-drop-table
  ok    1 migrations form a gapless 1..1 sequence
  FAIL  0001_x.up.sql:3 destructive statement in an up migration: DROP handle; DROP TABLE users;
        If this is deliberate, put '-- allow-destructive: <reason>' on the line before.
migrate-lint: FAILED
exit=1
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-other-drop-column
migrate-lint: scripts/testdata/migratelint/allow-destructive-other-drop-column
  ok    1 migrations form a gapless 1..1 sequence
  FAIL  0001_x.up.sql:3 destructive statement in an up migration: DROP handle; ALTER TABLE users DROP COLUMN email;
        If this is deliberate, put '-- allow-destructive: <reason>' on the line before.
migrate-lint: FAILED
exit=1
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-other-rename
migrate-lint: scripts/testdata/migratelint/allow-destructive-other-rename
  ok    1 migrations form a gapless 1..1 sequence
  FAIL  0001_x.up.sql:3 destructive statement in an up migration: DROP handle; ALTER TABLE users RENAME TO u2;
        If this is deliberate, put '-- allow-destructive: <reason>' on the line before.
migrate-lint: FAILED
exit=1
$ ./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/allow-destructive-split-alone
migrate-lint: scripts/testdata/migratelint/allow-destructive-split-alone
  ok    1 migrations form a gapless 1..1 sequence
  ok    0001_x.up.sql:3 destructive statement with a stated reason
migrate-lint: passed
exit=0
```

### Verifier reproducer in migrations/ at 84f8ad1 (tree restored afterwards)

```
  FAIL  0006_x.up.sql:3 destructive statement in an up migration: DROP handle; DROP TABLE users;
        If this is deliberate, put '-- allow-destructive: <reason>' on the line before.
  ok    append-only manifest matches (12 migrations)
migrate-lint: FAILED
repro exit=1
```

Lanes at 84f8ad1: `go test -count=1 ./scripts/ -run TestMigrateLint -v` exit 0 (52 subtests pass, 0 fail, 0 skip); `make migrate-lint` exit 0; `make ci` exit 0; `./scripts/ci-required-guard.sh` exit 0.

## Fix round 2 (R2-F1)

Design: section 4 of scripts/migrate-lint.sh is main's loop (5f615d7) again; section 4b (statement parser) only adds column-drop failures, exempt only by a marker on the line directly before the DROP token. The marker-before-the-statement extension is removed; fixtures allow-destructive-split and allow-destructive-split-alone now carry the marker directly above the DROP line.

RED at 84f8ad1 (new TestMigrateLintNeverAcceptsWhatMainRejects, script unchanged), `go test -count=1 ./scripts/ -run TestMigrateLintNeverAccepts`:

```
--- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects (4.36s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d06 (0.09s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d09 (0.10s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d16 (0.10s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d17 (0.10s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d18 (0.10s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d19 (0.11s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d22 (0.10s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d23 (0.09s)
    --- FAIL: TestMigrateLintNeverAcceptsWhatMainRejects/differential/d24 (0.10s)
FAIL
FAIL	github.com/yegamble/vizra-core/scripts	4.690s
FAIL
```

GREEN at b1c1734 (via quiet.sh):

```
PASS r2-test (6s) log: /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T//vizra-gate-logs/r2-test-20261112-062237-50835.log
--- PASS: TestMigrateLintPassesOnTheRealMigrations (0.14s)
PASS
ok  	github.com/yegamble/vizra-core/scripts	6.241s
exit 0
PASS r2-lint (0s) log: /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T//vizra-gate-logs/r2-lint-20261112-062244-56070.log
  ok    0005_users_credentials_owner_claim.up.sql:210 destructive statement with a stated reason
  ok    append-only manifest matches (10 migrations)
migrate-lint: passed
exit 0
PASS r2-ci (57s) log: /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T//vizra-gate-logs/r2-ci-20261112-062244-56225.log
ok  	github.com/yegamble/vizra-core/scripts	37.523s

make ci: all lanes passed
exit 0
PASS r2-guard (0s) log: /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T//vizra-gate-logs/r2-guard-20261112-062244-56207.log
  ok    every job runs on GitHub-hosted ubuntu-24.04
  ok    every third-party action is pinned to a commit SHA
ci-required-guard: passed (6 required check(s))
exit 0
```

TestMigrateLint: 4 tests, 102 subtests PASS, 0 skip. d16 reproducer (`./scripts/migrate-lint.sh --dir scripts/testdata/migratelint/differential/d16`): exit 1.
