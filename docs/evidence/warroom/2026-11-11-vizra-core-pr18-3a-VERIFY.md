# vizra-core PR #18 (3a: contract wildcards + migrate-lint) — independent verification

- Subject: https://github.com/yegamble/vizra-core/pull/18
- SHA verified: `a627e1f64afc8888350e9ba55420c9d355c73559` (PR head at start and at end: same, state OPEN)
- IDs: VZ-FOUND-002 (core half), VZ-FOUND-003
- Environment: Darwin 25.5.0 arm64, go1.27.4, fresh clone under `mktemp -d $TMPDIR/vzv-core-pr18-XXXXXX` (deleted at end). Date 2026-11-11.
- Verdict: **FAIL** — one BLOCKING finding (F1, weakened exemption). Everything else reproduced.

## Commands

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `make ci` | 0 | 20 packages `ok`, 0 FAIL, 0 skip lines, 8 packages with no test files |
| 2 | `make migrate-lint` | 0 | `migrate-lint: passed`, manifest matches (10 migrations) |
| 3 | `make openapi-verify` | 0 | `internal/httpapi` ok |
| 4 | `make sqlc-verify` | 0 | sqlcgen matches |
| 5 | `./scripts/ci-required-guard.sh` | 0 | passed (6 required checks) |
| 6 | `go test ./scripts/ ./internal/httpapi/ -v` | 0 | 0 `--- SKIP`; 54 subtests PASS in TestMigrateLintFixtures + TestContractDriftOnSyntheticRouteTables |
| 7 | B1 mutation (below) `go test ./internal/httpapi/` | 1 | `TestEveryRouteHasASpecOperation` names `GET /files/{path}` |
| 8 | B2 mutation | 1 | `TestEverySpecOperationHasARoute` names `GET /mutantz` (+ public-contract test) |
| 9 | B3 mutation | 1 | 11 wildcard/unmappable subtests of `TestContractDriftOnSyntheticRouteTables` red |
| 10 | restored tree `go test ./internal/httpapi/` | 0 | `git status --short` empty |
| 11 | B4/C: `migrations/0006_x.{up,down}.sql` + `./scripts/migration-manifest.sh generate` + `./scripts/migrate-lint.sh` (and main's script, `git show origin/main:scripts/migrate-lint.sh`, on the same tree) | per table | see B4, C |

## A. Diff scope — PASS
`git diff origin/main...HEAD --stat`: 79 files, +413/-12. Modified: `internal/httpapi/openapi_contract_test.go`, `scripts/migrate-lint.sh`, `scripts/scripts_test.go`; everything else is added fixtures under `scripts/testdata/migratelint/`. No deletions (`--diff-filter=D` empty). AGENTS.md, workflows, manifest untouched. No `t.Skip` in either test file. The removed lines in the contract test are the old `serverOperations` body including the `*` skip; no existing fixture case removed from `TestMigrateLintFixtures` (existing 15 cases still listed, 19 added).

## B. Mutations on the real tree

1. `e.GET("/files/*", s.handleSchemaz)` in `server.go` + `claimGuardedRoutes = {"GET /files/*": true}` in `setup.go` → `go test ./internal/httpapi/` exit 1, `TestEveryRouteHasASpecOperation` lists `GET /files/{path}`. Restored. **Reproduced.**
2. Copied the `/schemaz` path item to `/mutantz` in `api/openapi.yaml` (new operationId) → exit 1, `TestEverySpecOperationHasARoute` lists `GET /mutantz`. Restored. **Reproduced.**
3. Re-inserted `if strings.Contains(r.Path, "*") { continue }` in `contractOperations` → exit 1, 11 subtests red (wildcard route without spec, mapped path, other method, different parameter name, root wildcard, parameter and wildcard, 5 unmappable shapes). Restored. **Reproduced.**
4. migrate-lint on the real tree, `0006_x.up.sql` + down + regenerated manifest. "main" = main's script on the same file.

| Case | SQL | PR exit | main exit | Result |
|---|---|---|---|---|
| B4a | `ALTER TABLE sites DROP handle;` | 1 | 0 | caught |
| B4b | `alter table sites\n  drop\n  column handle;` | 1 | 0 | caught |
| B4c | `ALTER TABLE sites ADD x int, DROP handle;` | 1 | 0 | caught |
| B4d | `ALTER TABLE sites DROP /* c */ COLUMN IF EXISTS handle;` | 1 | 0 | caught |
| B4e | `ALTER TABLE ONLY public.sites DROP "handle" CASCADE;` | 1 | 0 | caught |
| P1 | `ALTER TABLE sites ALTER COLUMN handle DROP DEFAULT;` | 0 | 0 | passes (correct) |
| P2 | `... DROP NOT NULL;` | 0 | 0 | passes (correct) |
| P3 | `-- allow-destructive: reason` then `ALTER TABLE sites DROP handle;` | 0 | 0 | exempt (correct), also multi-line form |
| E1 | `DO $$ BEGIN\n ALTER TABLE sites\n DROP handle;\nEND $$;` | 0 | 0 | **missed** — documented limit (dollar-quoted body), FOLLOW-UP |
| E1b | `DO $$ BEGIN ALTER TABLE sites DROP COLUMN handle; END $$;` | 1 | 1 | caught (line rule) |
| E2 | `ALTER TABLE sites DROP "column";` | 1 | 0 | caught |
| E3 | CRLF, split over three lines | 1 | 0 | caught |
| E4 | no trailing semicolon at EOF | 1 | 0 | caught |
| E5 | `ALTER TABLE IF EXISTS sites DROP IF EXISTS handle RESTRICT;` | 1 | 0 | caught |
| E6 | `ALTER TABLE sites ALTER COLUMN a DROP DEFAULT, DROP handle;` | 1 | 0 | caught |
| E7 | `ALTER TABLE sites DROP identity;` | 1 | 0 | caught |
| E8 | preceding string literal containing `;`, `--`, `/*` | 1 | 0 | caught |
| E9 | nested block comment between TABLE and DROP, split line | 1 | 0 | caught |
| E10 | `ADD CONSTRAINT c CHECK (a > 0), DROP handle` | 1 | 0 | caught |
| E11 | preceding `E'it\'s'` string, then bare drop | 0 | 0 | **missed** — documented limit (E'' backslash quotes), FOLLOW-UP |
| E12 | `BEGIN; ALTER TABLE sites DROP handle; COMMIT;` | 1 | 0 | caught |
| E13 | `DROP U&"handle"` | 1 | 0 | caught |
| E14 | `SELECT $q$ x $q$; ALTER TABLE sites DROP handle;` | 1 | 0 | caught |

No plain-SQL column drop the PR claims to catch was missed.

## C. Exemption — FAIL (F1)

| Case | File (`\n` = newline) | PR exit | main exit | Result |
|---|---|---|---|---|
| C1 | marker, `ALTER TABLE sites ADD x int;`, `ALTER TABLE sites DROP handle;` | 1 | 0 | correct: later drop not exempt |
| C2 | marker, two bare drops on two lines | 1 | 0 | correct: second fails |
| C4 | marker, split drop, then `TRUNCATE users;` on its own line | 1 | 1 | correct |
| C7 | marker, one ALTER with `DROP a,\n DROP b` | 0 | 0 | one statement, both actions exempt (as designed) |
| C8 | marker, blank line, split drop | 1 | 0 | correct |
| C9 | marker with no reason | 1 | 0 | correct |
| **C3** | `-- allow-destructive: r\nALTER TABLE sites\n  DROP handle; DROP TABLE users;\n` | **0** | **1** | **REGRESSION**: `DROP TABLE users` exempted |
| **C3b** | `-- allow-destructive: r\nALTER TABLE sites\n  DROP handle; ALTER TABLE users DROP COLUMN email;\n` | **0** | **1** | **REGRESSION**: second statement's DROP COLUMN exempted |
| **C10** | `-- allow-destructive: r\nALTER TABLE sites\n  DROP handle; ALTER TABLE users RENAME TO u2;\n` | **0** | **1** | **REGRESSION**: RENAME exempted |
| C5 | marker, two `DROP COLUMN` statements on ONE line | 0 | 0 | both exempt; same on main (pre-existing) |
| C6 | marker, `SELECT 1; ALTER TABLE sites\n  DROP handle;` | 0 | 0 | exempt; main missed the drop entirely |
| C11 | marker inside a `/* */` block comment on the line before | 0 | 0 | exempt; main missed the drop entirely |
| C12 | marker in the middle of the statement, before `DROP handle, DROP b` | 0 | 0 | exempt (line-before rule) |

PR output for C3: `ok    0006_x.up.sql:3 destructive statement with a stated reason` / `migrate-lint: passed`.

Cause (`scripts/migrate-lint.sh`, section 4 loop): the exemption is decided per LINE. `exempt=1` is set when any statement-level column drop on line N belongs to a statement whose first line is preceded by a marker, and then the whole of line N is skipped, including line-pattern hits on N that belong to a different, later statement. On main line 3 was judged only by the line before it (`ALTER TABLE sites`, not a marker) and failed.

## D. Lanes — PASS
Commands 1-6 above: all exit 0, 0 skips.

## E. CI on a627e1f — PASS
| Check | Status | In manifest |
|---|---|---|
| ci-required | success | (fan-in) |
| append-only | success | yes |
| build-test | success | yes |
| cache-matrix (+ redis and valkey legs) | success | yes |
| fixtures | success | yes |
| govulncheck | success | yes |
| docker-build | success | yes |
| GitGuardian Security Checks | success | no |
| image-scan | failure | no (red on main too, per brief; not re-checked on main here) |

## Findings

| # | Class | Finding | Reproducer |
|---|---|---|---|
| F1 | **BLOCKING** (weakened gate / false-green; reproduced on head; main is red on the same file) | One `-- allow-destructive:` marker before a multi-line ALTER TABLE also exempts any other destructive statement that shares a line with one of that statement's column drops (DROP TABLE, DROP COLUMN of another table, RENAME). | `printf -- '-- allow-destructive: r\nALTER TABLE sites\n  DROP handle; DROP TABLE users;\n' > migrations/0006_x.up.sql; echo 'SELECT 1;' > migrations/0006_x.down.sql; ./scripts/migration-manifest.sh generate; ./scripts/migrate-lint.sh` → exit 0 on a627e1f, exit 1 with main's script. Needs a fix plus a fixture (expected: fail). |
| F2 | FOLLOW-UP | Marker exempts every statement on the following line (C5); pre-existing on main. Exemption should be per statement. | C5 |
| F3 | FOLLOW-UP | Marker is honoured inside a block comment (C11) and mid-statement (C12), and for a statement that starts after a harmless one on the same line (C6). | C6, C11, C12 |
| F4 | FOLLOW-UP | Documented limits confirmed as misses: split bare drop inside `DO $$`, statements after an `E'..\'..'` string. Stated in the script header. | E1, E11 |
| F5 | FOLLOW-UP | No fixture for an exemption that must NOT apply (marker then later drop, marker + blank line); behaviour is correct (C1, C2, C8) but untested. | — |

## Per-case table

| Case | State on main + this PR | Proof / what is missing |
|---|---|---|
| FOUND-002 S1 route without spec fails; spec without route fails | **Proven** by this PR | `TestEveryRouteHasASpecOperation`, `TestEverySpecOperationHasARoute`, `TestContractDriftOnSyntheticRouteTables` (`make openapi-verify`, lane `build-test`); B1-B3 reproduced incl. wildcard |
| FOUND-002 S2 generated client diff empty after regeneration | Not in this PR | vizra-user; not examined here |
| FOUND-002 N1 hand-edited generated file rejected | Not in this PR | vizra-user; not examined here |
| FOUND-003 S1 `migrate up` from the release image on empty DB | **Missing as worded** | `TestMigrateUpOnEmptyDatabase` proves the in-process migrator (per 2026-11-10 audit; not re-run here); no lane runs `vizra migrate` from the built image |
| FOUND-003 S2 sqlc-verify passes | Proven | `make sqlc-verify` exit 0, lane `build-test` |
| FOUND-003 N1 DROP COLUMN in `*.up.sql` fails migrate-lint | Detection **proven** by this PR (B4a-e, 19 fixtures in `TestMigrateLintFixtures`); **exemption path regressed (F1)** | fix F1; documented dynamic-SQL limits remain |
| FOUND-003 N2 editing sqlcgen output fails drift check | Proven per audit `F003-M6` | not re-mutated here (only the green run) |
| FOUND-003 R1 dirty ledger detected, reported, not auto-fixed | **Missing** | no test sets a real ledger dirty; `internal/migrate` has no test files (audit); untouched by this PR |

Recording after a merge of a fixed PR: VZ-FOUND-002 core half S1 could be IMPLEMENTED; the id cannot be VERIFIED from this PR (S2, N1 are vizra-user). VZ-FOUND-003 cannot be VERIFIED: S1 (release-image migrate lane) and R1 (real dirty-ledger test) are missing; at most IMPLEMENTED with those two named.

## Not run
- Integration suite against PostgreSQL / Redis locally (CI `build-test` green on the SHA is the only evidence).
- sqlcgen edit mutation (N2) and append-only CI mutation: not repeated.
- image-scan status on main: not re-checked.
- `docs/warroom/FOLLOWUPS.md` not written (brief restricts writes to this file); follow-ups are F2-F5 above.

FINAL VERDICT: FAIL — SHA a627e1f64afc8888350e9ba55420c9d355c73559
