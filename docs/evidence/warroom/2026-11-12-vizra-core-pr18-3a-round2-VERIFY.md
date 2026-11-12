# vizra-core PR #18 (3a) — round 2 independent verification

- Subject: https://github.com/yegamble/vizra-core/pull/18
- SHA verified: `84f8ad1a678a2c7dd432884131a2fc01398acbd4` (PR head at start: same, OPEN; end check: see last section)
- IDs: VZ-FOUND-002 (core half), VZ-FOUND-003
- First verdict: `2026-11-11-vizra-core-pr18-3a-VERIFY.md` (FAIL at a627e1f, F1). This verifier wrote neither the code nor that verdict.
- Environment: Darwin 25.5.0 arm64, go1.27.4, fresh clone under `mktemp -d $TMPDIR/vzv-core-pr18b-XXXXXX`; `mainc/` = second copy of the tree with `git show origin/main:scripts/migrate-lint.sh` (origin/main 5f615d7) copied over `scripts/migrate-lint.sh`. Date 2026-11-12.
- Verdict: **FAIL** — F1 as reported is fixed, but the differential found one file main rejects and the head accepts in which a second, unmarked `DROP TABLE` really is a separate statement (R2-F1).

## Commands

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `git diff a627e1f..84f8ad1 --stat` | 0 | 10 files, +64/-8: migrate-lint.sh, scripts_test.go, 4 new fixture dirs |
| 2 | `go test -count=1 ./internal/httpapi/` | 0 | ok |
| 3 | `go test -count=1 ./scripts/ -run TestMigrateLint -v` | 0 | 3 top-level PASS, 52 subtests PASS, 0 SKIP, 0 FAIL |
| 4 | `make migrate-lint` | 0 | passed |
| 5 | `make ci` | 0 | 20 packages ok, 0 FAIL, 8 without test files, 0 skip lines |
| 6 | `./scripts/ci-required-guard.sh` | 0 | passed (6 required checks) |
| 7 | per case: `cp case migrations/0006_x.up.sql; echo 'SELECT 1;' > migrations/0006_x.down.sql; ./scripts/migration-manifest.sh generate; ./scripts/migrate-lint.sh` in `head/` and in `mainc/` | table | sections B, C |

## A. Fix-round diff — PASS
Only `scripts/migrate-lint.sh`, `scripts/scripts_test.go` and new fixtures under `scripts/testdata/migratelint/` (allow-destructive-other-drop-table, -other-drop-column, -other-rename, allow-destructive-split-alone). `--diff-filter=D` empty; the test diff is additions only (4 table rows + `TestMigrateLintRejectsEverythingMainRejected`); nothing under `internal/` changed, so the first verifier's B1-B3 stand. `go test -count=1 ./internal/httpapi/` exit 0.

## B. F1 and the differential

F1 reproducers (first verdict C3, C3b, C10) now exit 1 on the head: fixed.

`M` = `-- allow-destructive: r` line; `\n` = newline. Exit codes of the whole lint, real tree plus the one file.

| File | Content | main | head | Note |
|---|---|---|---|---|
| F1a | `M\nALTER TABLE sites\n  DROP handle; DROP TABLE users;` | 1 | 1 | fixed |
| F1b | `... DROP handle; ALTER TABLE users DROP COLUMN email;` | 1 | 1 | fixed |
| F1c | `... DROP handle; ALTER TABLE users RENAME TO u2;` | 1 | 1 | fixed |
| d01 | `M\nALTER TABLE sites\n  ADD x int; DROP TABLE users; ALTER TABLE sites DROP handle;` | 1 | 1 | |
| d02 | `M\nALTER TABLE sites ADD x int;\nDROP TABLE users; ALTER TABLE sites\n DROP handle;` | 1 | 1 | |
| d03 | `M\nALTER TABLE sites\n  DROP handle;\nDROP TABLE users;` | 1 | 1 | |
| d04 | `M\nALTER TABLE sites\n  DROP handle,\n  ADD y int; ALTER TABLE users DROP email;` | 0 | 1 | strengthening |
| d05 | `M\n\nALTER TABLE sites\n  DROP COLUMN handle;` | 1 | 1 | |
| d06 | `/*\nM\n*/ ALTER TABLE sites\n  DROP COLUMN handle;` | 1 | **0** | marker inside block comment honoured; only the one statement (FOLLOW-UP) |
| d07 | `ALTER TABLE sites\nM\n  DROP COLUMN handle; TRUNCATE users;` | 0 | 0 | pre-existing on main (marker exempts the whole next line) |
| d08 | `ALTER TABLE users\n  ADD z int; M\nALTER TABLE sites ADD q int; ALTER TABLE users\n  DROP email; ALTER TABLE sites DROP COLUMN handle;` | 1 | 1 | |
| d09 | `M\nALTER TABLE sites\n  DROP handle; -- DROP TABLE users` | 1 | **0** | builder-disclosed; comment text only (FOLLOW-UP) |
| d10 | F1a with CRLF | 1 | 1 | |
| d11 | `... DROP handle; TRUNCATE users;` | 1 | 1 | |
| d12 | `... DROP handle; ALTER TABLE users ALTER COLUMN email TYPE text;` | 1 | 1 | |
| d13 | `M\nALTER TABLE sites\n  ADD x int,\n  DROP handle; DROP INDEX users_email_idx;` | 1 | 1 | |
| d14 | `... DROP handle; DO $$ BEGIN DROP TABLE users; END $$;` | 1 | 1 | |
| d15 | `... DROP handle /* x */; /* y */ DROP SCHEMA public;` | 1 | 1 | |
| **d16** | `M\nALTER TABLE sites\n  DROP handle, ADD x text DEFAULT E'\''; DROP TABLE users; --';` | 1 | **0** | **BLOCKING R2-F1**: a real second statement is exempted |
| d17 | `M\nALTER TABLE sites\n  DROP handle, DROP CONSTRAINT sites_pkey;` | 1 | **0** | same marked statement (FOLLOW-UP / design) |
| d18 | `M\nALTER TABLE sites\n  DROP COLUMN handle;` | 1 | **0** | same marked statement: the PR's intended "marker before a multi-line ALTER" |
| d19 | `M\nALTER TABLE sites\n  DROP COLUMN handle,\n  DROP COLUMN name;` | 1 | **0** | same marked statement, two actions |
| d20 | `M\nSELECT 1;\nALTER TABLE users DROP COLUMN email; ALTER TABLE sites\n DROP handle;` | 1 | 1 | |
| d21 | `M\nALTER TABLE sites\n  DROP handle;\nALTER TABLE users\n  DROP email;` | 0 | 1 | strengthening |
| d22 | `... DROP handle; /* DROP TABLE users; */` | 1 | **0** | block-comment text only (FOLLOW-UP) |
| d23 | `... DROP handle, ADD n text DEFAULT 'DROP TABLE users';` | 1 | **0** | string literal text only (FOLLOW-UP) |
| d24 | `... DROP handle, ADD "a""; DROP TABLE users; --" int;` | 1 | **0** | quoted-identifier text only (FOLLOW-UP) |
| d25 | `M\nALTER TABLE sites\n  DROP COLUMN handle; DROP VIEW v;` | 1 | 1 | |

34 rows with section C (28 here). main-rejects / head-accepts: 9 (d06, d09, d16, d17, d18, d19, d22, d23, d24). Classified:

- **d16 — BLOCKING.** PostgreSQL reads `E'\''` as a complete string (backslash-escaped quote), so `; DROP TABLE users;` is a second, unmarked statement that runs. The head's tokeniser treats `''` as an escaped quote, keeps the string open to the final `'`, sees ONE statement on line 3 and applies the marker of the ALTER to the whole line. main fails the file (`DROP TABLE` on a line not preceded by a marker). Head transcript: `ok    0006_x.up.sql:3 destructive statement with a stated reason` / `migrate-lint: passed`, exit 0. The script header lists E'' strings as a DETECTION limit; here the same limit widens the EXEMPTION, which is exactly the property under test (head must not accept what main rejects).
- d17, d18, d19 — every destructive action belongs to the one statement that carries the marker. This is the behaviour the PR introduced on purpose in round 1 (fixtures allow-destructive-split / -split-alone are the bare-DROP form of it) and the first verdict accepted (its C7). Reported so the owner sees that "never accepts what main rejects" is NOT literally true for a marked multi-line statement; not counted as blocking because no unmarked statement is let through. If the owner wants the literal property, these three are the reproducers.
- d06 — marker text inside a block comment counts as a marker (first verdict F3); only the statement after it is exempt. FOLLOW-UP.
- d09, d22, d23, d24 — the text main matched is inside a `--` comment, a block comment, a string literal or a quoted identifier on the marked statement's line; no second statement exists, nothing else runs. Harmless as a gate; the cost is a reviewer-facing oddity (main was stricter by accident). d09 is the builder's disclosed case. FOLLOW-UP.

Rows main 0 / head 1 (intended strengthening): d04, d21, and C-section c1, c2, c3.

## C. Round-1 detection on the head — PASS

| Case | main | head |
|---|---|---|
| c1 `ALTER TABLE sites DROP handle;` | 0 | 1 |
| c2 `ALTER TABLE sites\n  DROP\n  handle;` | 0 | 1 |
| c3 `ALTER TABLE sites ADD x int, DROP handle;` | 0 | 1 |
| c4 `ALTER TABLE sites ALTER COLUMN handle DROP DEFAULT;` | 0 | 0 |
| c5 `... DROP NOT NULL;` | 0 | 0 |
| c6 `M\nALTER TABLE sites DROP handle;` | 0 | 0 |

## D. Tests and lanes — PASS (with the gap that R2-F1 has no fixture)
`go test -count=1 ./scripts/ -run TestMigrateLint -v`: exit 0; TestMigrateLintFixtures, TestMigrateLintRejectsEverythingMainRejected, TestMigrateLintPassesOnTheRealMigrations PASS; 52 subtests PASS, 0 SKIP. allow-destructive-other-drop-table / -other-drop-column / -other-rename run as must-fail in both tests; allow-destructive-split-alone runs as must-pass. Static list of TestMigrateLintRejectsEverythingMainRejected: I ran main's script on each of the 15 fixtures on origin/main; it rejects 11 (alter-type, bad-filename, drop-column, drop-constraint, drop-index, drop-table, empty-down, missing-down, rename, sequence-gap, truncate) and accepts 4 (allow-destructive, commented-out, good, no-down-declared). All 11 are in the list: complete. The list is static (it does not run main's script), so it cannot find new counter-examples such as d16. `make migrate-lint`, `make ci`, `./scripts/ci-required-guard.sh` exit 0. Tree clean after the runs.

## E. CI on 84f8ad1 — PASS
`gh api repos/yegamble/vizra-core/commits/84f8ad1.../check-runs`: every run has head_sha 84f8ad1a678a2c7dd432884131a2fc01398acbd4.

| Check | Conclusion | In manifest |
|---|---|---|
| ci-required | success | fan-in |
| append-only | success | yes |
| build-test | success | yes |
| cache-matrix (+ redis leg, valkey leg) | success, success, success | yes |
| fixtures | success | yes |
| govulncheck | success | yes |
| docker-build | success | yes |
| GitGuardian Security Checks | success | no |
| image-scan | failure | no (red on main per brief; not re-checked) |

Manifest (`.github/required-checks.txt`): append-only build-test cache-matrix fixtures govulncheck docker-build — all six ran and passed.

## Findings

| # | Class | Finding | Reproducer |
|---|---|---|---|
| R2-F1 | **BLOCKING** (weakened gate / false green; reproduced on head; main is red on the same file) | A marker before a multi-line ALTER TABLE exempts a separate unmarked statement on the DROP's line when it follows an `E'..\'..'` string: the tokeniser miscounts statements on the line. | `printf -- "-- allow-destructive: r\nALTER TABLE sites\n  DROP handle, ADD x text DEFAULT E'\\\\''; DROP TABLE users; --';\n" > migrations/0006_x.up.sql; echo 'SELECT 1;' > migrations/0006_x.down.sql; ./scripts/migration-manifest.sh generate; ./scripts/migrate-lint.sh; echo $?` → head 0, main 1. File line 3 must read `  DROP handle, ADD x text DEFAULT E'\''; DROP TABLE users; --';`. Suggested direction (not prescriptive): keep main's rule as a floor — a line that matches the per-line pattern for anything other than the marked statement's own column drop is judged by the line before it alone; or refuse the statement-level exemption when the line contains a backslash/`E'`. |
| R2-F2 | FOLLOW-UP | Text matching the line pattern inside a comment, string or quoted identifier on the marked statement's line is no longer rejected (d09, d22, d23, d24). Harmless: no statement. | d09 |
| R2-F3 | FOLLOW-UP | Marker inside a block comment is honoured (d06); marker before a multi-line statement covers every action of that statement including DROP CONSTRAINT (d17-d19) where main required the marker on the line directly before. Decide and document, add fixtures. | d06, d17 |
| R2-F4 | FOLLOW-UP | TestMigrateLintRejectsEverythingMainRejected is a static list, not a differential against main's script. | — |
| (carried) | FOLLOW-UP | First verdict F2-F5 unchanged (d07 = F2). | — |

## Per-case table

| Case | State after this PR | Proof / what is missing |
|---|---|---|
| FOUND-002 S1 route without spec fails; spec without route fails | Proven | `TestEveryRouteHasASpecOperation`, `TestEverySpecOperationHasARoute`, `TestContractDriftOnSyntheticRouteTables` (lane build-test); mutations B1-B3 reproduced by the first verifier at a627e1f, contract test unchanged since; `go test ./internal/httpapi/` exit 0 here |
| FOUND-002 S2 generated client diff empty after regeneration | Proven elsewhere | vizra-user #12 (merged 53a39a8), `2026-11-11-vizra-user-pr12-3b-VERIFY.md`; not re-run |
| FOUND-002 N1 hand-edited generated file rejected by drift check | Proven elsewhere | same vizra-user #12 evidence; not re-run |
| FOUND-003 S1 `migrate up` from the release image on empty DB | **Missing as worded** | in-process migrator test only (per first verdict/audit); no lane runs `vizra migrate` from the built image; untouched by this PR |
| FOUND-003 S2 sqlc-verify passes | Proven | `make ci` exit 0 here (first verifier ran `make sqlc-verify` exit 0); lane build-test green |
| FOUND-003 N1 DROP COLUMN in `*.up.sql` fails migrate-lint | Detection proven (section C, 52 fixture subtests); **exemption path still has a hole (R2-F1)** | fix R2-F1 and add its fixture; documented dynamic-SQL limits remain |
| FOUND-003 N2 editing sqlcgen output fails drift check | Proven per audit F003-M6 | not re-mutated here |
| FOUND-003 R1 dirty ledger detected, reported, not auto-fixed | **Missing** | no test sets a real ledger dirty; untouched by this PR |

Recording: 002 core half S1 may be IMPLEMENTED after a merge; 003 cannot be VERIFIED from this PR (S1 and R1 missing).

## Not run
- B1-B3 contract mutations, sqlcgen mutation, append-only CI mutation: not repeated (unchanged since a627e1f).
- Local PostgreSQL/Redis integration suite: CI build-test only.
- image-scan on main not re-checked.
- `docs/warroom/FOLLOWUPS.md` not written (brief: this file only).
- Execution of d16 against a live PostgreSQL to watch `users` disappear: attempted with a throwaway local cluster, the server did not start in the time available. The claim that `E'\''` closes the string rests on PostgreSQL's documented escape-string syntax (backslash-escaped quote), the same limit the script header itself names. The lint result (head 0, main 1) was reproduced.

## End check
PR head at end: 84f8ad1a678a2c7dd432884131a2fc01398acbd4 OPEN. Scratch directory deleted by exact path.

FINAL VERDICT: FAIL — SHA 84f8ad1a678a2c7dd432884131a2fc01398acbd4
