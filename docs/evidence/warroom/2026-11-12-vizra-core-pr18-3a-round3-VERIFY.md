# vizra-core PR #18 (slice 3a) — round-3 VERIFY (third and last budgeted verdict)

- PR: https://github.com/yegamble/vizra-core/pull/18 — head `b1c1734f583a46f7abc295dcc55094f9d3f5717e` at start and at end (OPEN both times)
- IDs: VZ-FOUND-002 (core half), VZ-FOUND-003
- Verifier: independent, fresh (wrote neither the code nor verdicts 1 and 2). Date 2026-11-12.
- Environment: macOS Darwin 25.5.0 arm64, go1.27.4, fresh clone in a private `mktemp -d` scratch dir (`vzv-core-pr18c-XXXXXX`), origin/main = `5f615d74e840b23d2201b1d78dd89abfef07701b`.
- Verdict: **PASS with follow-ups.** R2-F1 and F1 are fixed; the "never accepts what main rejects" invariant holds structurally and over 52 trees of my own corpus (0 regressions).

## Commands

| Command | Exit | Result |
|---|---|---|
| `git diff 84f8ad1 b1c1734 --stat` | 0 | 53 files, +301/-40: `scripts/migrate-lint.sh`, `scripts/scripts_test.go`, `scripts/testdata/migratelint/**` only |
| `git diff a627e1f b1c1734 --stat -- internal/` | 0 | empty |
| `diff main-lint.sh scripts/testdata/migratelint/main-baseline/migrate-lint.sh` | 1 | exactly one added line (line 2, the FROZEN BASELINE header) |
| `diff main-lint.sh scripts/migrate-lint.sh` | 1 | 3 hunks, additions only (see B) |
| my differential, 52 trees, both scripts with `--dir` | — | 0 rows main≠0/head=0 (table in C) |
| `go test -count=1 ./scripts/ -run TestMigrateLint -v` | 0 | 4 top-level tests + 102 subtests PASS, 0 FAIL, 0 SKIP (50 subtests in NeverAcceptsWhatMainRejects) |
| same test against my mutant (D) | 1 | 9+ subtests red, "main's migrate-lint rejects this tree (exit 1) and the current one accepts it"; restored, `git status --short` empty |
| `go test -count=1 ./internal/httpapi/` | 0 | ok |
| `make migrate-lint` | 0 | |
| `./scripts/ci-required-guard.sh` | 0 | |
| `make ci` | 0 | "make ci: all lanes passed" |

## A. Scope of the fix round — OK
Only the lint script, its test and its testdata changed. `scripts_test.go` diff is purely additive (+58: `TestMigrateLintNeverAcceptsWhatMainRejects`); no existing assertion or table row was removed or loosened. No fixture directory was deleted. The two changed fixtures (`allow-destructive-split-alone/0001_x.up.sql`, `allow-destructive-split/0002_b.up.sql`) are must-PASS fixtures of the PR's own extension; the marker moved from "before the ALTER TABLE" to "directly before the DROP line". That is a tightening of the exemption (the old placement is now rejected: my n12b, head exit 1), not a weakening. No must-FAIL fixture was removed or changed.

## B. Invariant, structurally — holds
- Baseline copy is byte-identical to `origin/main:scripts/migrate-lint.sh` apart from the one header line.
- Full `diff main head` is three hunks, all pure additions (`>` lines only, no `<`): `14a15,17` header comment (INVARIANT note); `92a96` one blank line; `108a113,232` section 4b (comment block, `column_drops` awk function, one loop). Section 4's loop, the `destructive` pattern, `err`/`ok`, section 5 and the final `if [ $fail -ne 0 ]` are untouched.
- 4b cannot lower the failure state: it never assigns `fail` (only `err` does, to 1), has no `exit`, and runs after section 4's loop has finished, so its `continue`s cannot skip a section-4 line. Variables it reuses (`f base lineno line prevline`) are not read afterwards; section 5 reads only `CHECK_MANIFEST` and `fail`. awk runs in a process substitution, so even an awk error cannot abort the script with a success code.
- Confirmed empirically by C.

## C. Invariant, empirically — holds (my own corpus, 52 trees)
Layout: fixture-harness (`0001_a.up/down`, `0002_b.up/down`, `--dir <abs path>`), main's script in a second tree at `mainrepo/scripts/migrate-lint.sh`, same command for both. `c01` is the R2-F1 file (byte-identical to committed d16); `z_*` are the committed f1a-c (the three F1 files, content checked against verdict 1) and d06/d17/d18/d19. Content of each `n*` file is named by its row; exact bytes in the generator below the table.

| tree | main exit | head exit |
|---|---|---|
| c01_r2f1 | 1 | 1 |
| n01_marker_two_bare_two_stmts | 0 | 0 |
| n02_marker_bare_plus_truncate | 0 | 0 |
| n03_dollar_semicolon_then_bare | 0 | 1 |
| n03b_dollar_tag_multiline | 0 | 1 |
| n04_Estring_then_bare | 0 | 0 |
| n04b_Estring_then_dropcolumn | 1 | 1 |
| n05_nested_comment_then_bare | 0 | 1 |
| n05b_all_inside_nested_comment | 0 | 0 |
| n06_marker_in_block_comment_bare | 0 | 0 |
| n06b_marker_in_block_comment_dropcolumn | 0 | 0 |
| n07_crlf_bare | 0 | 1 |
| n07b_crlf_split | 0 | 1 |
| n07c_crlf_marker_bare | 0 | 0 |
| n08_tabs | 0 | 1 |
| n09_marker_empty_reason | 0 | 1 |
| n09b_marker_empty_reason_dropcolumn | 1 | 1 |
| n10_marker_two_above | 0 | 1 |
| n10b_marker_two_above_dropcolumn | 1 | 1 |
| n11_mixed_case | 0 | 1 |
| n11b_mixed_case_if_exists | 0 | 1 |
| n12_marker_before_stmt_dropcolumn_below | 1 | 1 |
| n12b_marker_before_stmt_bare_below | 0 | 1 |
| n13_marker_bare_plus_droptable_sameline | 0 | 0 |
| n14_marker_stmt_then_line_bare_droptable | 1 | 1 |
| n15_bare_with_trailing_comment_pattern | 1 | 1 |
| n16_dashdash_line_in_block_comment_then_bare | 0 | 0 |
| n16b_same_with_literal_dropcolumn | 0 | 0 |
| n16c_dashdash_line_in_string_then_bare | 0 | 0 |
| n17_multi_action | 0 | 1 |
| n18_comment_between_tokens | 0 | 1 |
| n18b_line_comment_between | 0 | 1 |
| n19_quoted_ident | 0 | 1 |
| n20_marker_on_drop_line_split | 0 | 0 |
| n21_marker_then_two_stmts_second_line_unmarked | 0 | 1 |
| n22_schema_qualified_if_exists | 0 | 1 |
| n23_drop_default_ok | 0 | 0 |
| n24_alter_then_comma_drop_default_named | 0 | 1 |
| n25_no_semicolon_eof | 0 | 1 |
| n26_marker_bare_plus_rename | 0 | 0 |
| n27_unterminated_string_before | 0 | 1 |
| n28_paren_then_drop | 0 | 1 |
| n29_marker_uppercase | 0 | 1 |
| n30_marker_trailing_not_leading | 0 | 1 |
| z_d06 | 1 | 1 |
| z_d16 | 1 | 1 |
| z_d17 | 1 | 1 |
| z_d18 | 1 | 1 |
| z_d19 | 1 | 1 |
| z_f1a | 1 | 1 |
| z_f1b | 1 | 1 |
| z_f1c | 1 | 1 |

Rows main≠0 and head=0: **none** (16 trees rejected by main, all 16 rejected by head; head additionally rejects 22 that main accepts).

Generator (file 0002_b.up.sql contents, `M` = `-- allow-destructive: r\n`):
```
C={
"c01_r2f1": M+"ALTER TABLE sites\n  DROP handle, ADD x text DEFAULT E'\\''; DROP TABLE users; --';\n",
"n01_marker_two_bare_two_stmts": M+"ALTER TABLE a DROP x; ALTER TABLE b DROP y;\n",
"n02_marker_bare_plus_truncate": M+"ALTER TABLE a DROP x; TRUNCATE users;\n",
"n03_dollar_semicolon_then_bare": "SELECT $$a;b$$; ALTER TABLE a DROP x;\n",
"n03b_dollar_tag_multiline": "SELECT $q$a;\n'b$$ $q$; ALTER TABLE a DROP x;\n",
"n04_Estring_then_bare": "SELECT E'a\\';'; ALTER TABLE a DROP x;\n",
"n04b_Estring_then_dropcolumn": "SELECT E'a\\';'; ALTER TABLE a DROP COLUMN x;\n",
"n05_nested_comment_then_bare": "/* a /* b */ c */ ALTER TABLE a DROP x;\n",
"n05b_all_inside_nested_comment": "/* a /* b */ ALTER TABLE a DROP x; */\nSELECT 1;\n",
"n06_marker_in_block_comment_bare": "/*\n-- allow-destructive: r\n*/ ALTER TABLE a DROP x;\n",
"n06b_marker_in_block_comment_dropcolumn": "/*\n-- allow-destructive: r\n*/ ALTER TABLE a DROP COLUMN x;\n",
"n07_crlf_bare": "ALTER TABLE a DROP x;\r\n",
"n07b_crlf_split": "ALTER TABLE a\r\n  DROP\r\n  COLUMN x;\r\n",
"n07c_crlf_marker_bare": "-- allow-destructive: r\r\nALTER TABLE a DROP x;\r\n",
"n08_tabs": "ALTER\tTABLE\ta\tDROP\tx;\n",
"n09_marker_empty_reason": "-- allow-destructive:\nALTER TABLE a DROP x;\n",
"n09b_marker_empty_reason_dropcolumn": "-- allow-destructive:   \nALTER TABLE a DROP COLUMN x;\n",
"n10_marker_two_above": M+"\nALTER TABLE a DROP x;\n",
"n10b_marker_two_above_dropcolumn": M+"SELECT 1;\nALTER TABLE a DROP COLUMN x;\n",
"n11_mixed_case": "alter Table a dRoP x;\n",
"n11b_mixed_case_if_exists": "Alter table only a drop if exists X cascade;\n",
"n12_marker_before_stmt_dropcolumn_below": M+"ALTER TABLE a\n  DROP COLUMN x;\n",
"n12b_marker_before_stmt_bare_below": M+"ALTER TABLE a\n  DROP x;\n",
"n13_marker_bare_plus_droptable_sameline": M+"ALTER TABLE a DROP x; DROP TABLE users;\n",
"n14_marker_stmt_then_line_bare_droptable": M+"ALTER TABLE a\n  DROP x; DROP TABLE users;\n",
"n15_bare_with_trailing_comment_pattern": "ALTER TABLE a DROP x; -- DROP COLUMN old\n",
"n16_dashdash_line_in_block_comment_then_bare": "/* note\n-- old: DROP COLUMN handle */ ALTER TABLE sites DROP handle;\n",
"n16b_same_with_literal_dropcolumn": "/* note\n-- old */ ALTER TABLE sites DROP COLUMN handle;\n",
"n16c_dashdash_line_in_string_then_bare": "SELECT '\n-- DROP TABLE x'; ALTER TABLE a DROP y;\n",
"n17_multi_action": "ALTER TABLE a ADD z int, DROP x, ADD w int;\n",
"n18_comment_between_tokens": "ALTER TABLE a DROP /* c */ x;\n",
"n18b_line_comment_between": "ALTER TABLE a -- hi\n DROP -- there\n x;\n",
"n19_quoted_ident": "ALTER TABLE \"a;b\" DROP \"x\";\n",
"n20_marker_on_drop_line_split": "ALTER TABLE a\n"+M+"  DROP\n  x;\n",
"n21_marker_then_two_stmts_second_line_unmarked": M+"ALTER TABLE a DROP x;\nALTER TABLE b DROP y;\n",
"n22_schema_qualified_if_exists": "ALTER TABLE IF EXISTS public.a DROP x RESTRICT;\n",
"n23_drop_default_ok": "ALTER TABLE a ALTER COLUMN x DROP DEFAULT;\n",
"n24_alter_then_comma_drop_default_named": "ALTER TABLE a ALTER x SET NOT NULL, DROP \"default\";\n",
"n25_no_semicolon_eof": "ALTER TABLE a DROP x",
"n26_marker_bare_plus_rename": M+"ALTER TABLE a DROP x; ALTER TABLE b RENAME TO c;\n",
"n27_unterminated_string_before": "SELECT 'it''s'; ALTER TABLE a DROP x;\n",
"n28_paren_then_drop": "ALTER TABLE a ADD CHECK (x > 0), DROP y;\n",
"n29_marker_uppercase": "-- ALLOW-DESTRUCTIVE: r\nALTER TABLE a DROP x;\n",
"n30_marker_trailing_not_leading": "SELECT 1; -- allow-destructive: r\nALTER TABLE a DROP x;\n",
}
```

### Both accept, file contains an unmarked plain-SQL column drop
| tree | why | class |
|---|---|---|
| n04 `SELECT E'a\';'; ALTER TABLE a DROP x;` | E'' backslash escape desynchronises the tokeniser; header states the limit ("E'...' strings with backslash-escaped quotes ... are not understood") | FOLLOW-UP (documented limit) |
| n16 block comment whose second line starts with `--` and contains `DROP COLUMN`, closed on that line, then `ALTER TABLE sites DROP handle;` | 4b's de-dup `continue` trusts that section 4 judged the line; section 4 (main's code) skipped it as "a comment" because it starts with `--` | FOLLOW-UP — see R3-F1 |
| n16c same with a multi-line string literal | same | FOLLOW-UP — R3-F1 |
| n16b (same shape with literal `DROP COLUMN`) | main's own pre-existing hole, shown for comparison: main 0, head 0 | pre-existing |

Every claimed spelling is caught when unmarked: bare DROP (n07, n08, n11, n25), IF EXISTS / ONLY / schema-qualified (n11b, n22), split lines (n07b, n12b, n18b), multi-action (n17, n24, n28), comment between tokens (n18, n18b), quoted identifiers (n19), after dollar-quoted `;` (n03, n03b), after nested comment (n05), CRLF and tabs. Marker rules: empty reason (n09), two lines above (n10), before the statement rather than the DROP line (n12b), uppercase marker (n29), trailing-comment marker (n30) are all rejected.

## D. Tests — OK
`TestMigrateLintNeverAcceptsWhatMainRejects` (read): execs the frozen baseline and the current script with `--dir` on every fixture tree and every `differential/*` tree, fatal if < 50 trees, fails a subtest when baseline≠0 and current=0, fatal if the baseline rejected < 20 trees. Mutation (scratch clone only): section 4's `prevline` widened to the two preceding lines (the round-1 style marker extension) → test exit 1, red on `allow-destructive-other-drop-column/-drop-table/-rename`, `differential/d06 d09 d16 d17 d18 d22 …` with the expected message. Restored from backup, tree clean, suite green again via `make ci`.

## E. CI on the exact SHA — OK
| Check | Conclusion | headSha | In manifest |
|---|---|---|---|
| ci-required (run 43208628133) | success | b1c1734f… | gate |
| append-only | success | b1c1734f… | yes |
| build-test | success | b1c1734f… | yes |
| cache-matrix + legs (valkey, redis) | success ×3 | b1c1734f… | yes |
| fixtures | success | b1c1734f… | yes |
| govulncheck | success | b1c1734f… | yes |
| docker-build | success | b1c1734f… | yes |
| image-scan | failure | b1c1734f… | no (deliberately absent, documented in `.github/required-checks.txt`); latest image-scan on main 5f615d7 is also `failure` |
| GitGuardian | success | | no |

## Findings
BLOCKING: none.

| # | Class | Finding | Reproducer |
|---|---|---|---|
| R3-F1 | FOLLOW-UP | A bare column drop is missed when its line starts with `--` inside a still-open block comment or string AND that line also matches the per-line pattern: 4b skips it as "already judged", section 4 skipped it as a comment. Not blocking: main accepts the file too (nothing main rejects is accepted), the root is main's untouched leading-`--` rule, which has the same hole for a literal `DROP COLUMN` today (n16b), and it needs a deliberately constructed line. Fix: in 4b skip the de-dup when the line starts with `--`. | `printf '/* note\n-- old: DROP COLUMN handle */ ALTER TABLE sites DROP handle;\n' > 0002_b.up.sql` → head exit 0 |
| R3-F2 | FOLLOW-UP | One marker exempts every ADDED hit on the next line, including two bare drops from two different statements (n01), and — as on main — any other destructive statement sharing that line (n02 TRUNCATE, n13 DROP TABLE, n26 RENAME; main exit 0 for all). Accepts nothing main rejected; the PR does not claim per-statement markers. | n01 |
| R3-F3 | FOLLOW-UP | A marker line inside a block comment is honoured (n06 by 4b, n06b by main's section 4 alike). Pre-existing rule, mirrored. | n06 |
| R3-F4 | FOLLOW-UP | E'' escape limit (n04): documented in the header; no fixture pins it. | n04 |
| (carried) | FOLLOW-UP | Verdict-1 F2–F5 and verdict-2 R2-F2..F4 where still applicable (R2-F4 is now addressed by the differential test). | — |

## Per-case table
| Case | State after this PR | Proof / what is missing |
|---|---|---|
| 002 S1 route without spec fails; spec without route fails | Proven | contract tests in `internal/httpapi` (lane build-test, green on this SHA); both-direction mutations reproduced by verifier 1 at a627e1f; `git diff a627e1f b1c1734 -- internal/` empty; `go test ./internal/httpapi/` exit 0 here |
| 002 S2 generated client diff empty after regeneration | Proven elsewhere | vizra-user #12 (merged 53a39a8), `2026-11-11-vizra-user-pr12-3b-VERIFY.md`; cited, not re-run |
| 002 N1 hand-edited generated file rejected by drift check | Proven elsewhere | same; cited, not re-run |
| 003 S1 `migrate up` from the release image on empty DB | **Missing** | no lane runs `vizra migrate up` from the built release image against an empty PostgreSQL (in-process migrator test only, per verdicts 1–2); untouched by this PR |
| 003 S2 sqlc-verify passes | Proven | `make ci` exit 0 here; lane build-test green |
| 003 N1 a DROP COLUMN in `*.up.sql` fails migrate-lint | Proven | `TestMigrateLintFixtures` + differential test (102 subtests, 0 skips), lane fixtures/build-test green; my corpus C; exemption no weaker than main (B, C, mutation D). Residual limits are follow-ups R3-F1..F4 |
| 003 N2 editing sqlcgen output fails drift check | Proven per verdict 1 / audit | not re-mutated here |
| 003 R1 dirty migration ledger detected and reported, not auto-fixed | **Missing** | no test puts a real ledger in the dirty state and asserts report-without-repair; untouched by this PR |

**VZ-FOUND-002:** with this PR merged every ledger case (S1, S2, N1) has a proof. What `evidence_required` ("CI job output showing both-direction drift failure on a deliberate mutation, then green") still lacks: the red half as *CI job output*. The both-direction failures exist only as verifier-local mutation transcripts (verdict 1; vizra-user #12 evidence); CI shows only the green half. Either a CI run on a deliberately mutated throwaway branch, or an owner/chair decision that the independent local transcript satisfies the wording, is needed before VERIFIED.

**VZ-FOUND-003:** not every case is proven: S1 (release image) and R1 (dirty ledger) are missing, so it cannot be VERIFIED from this PR; N1, N2, S2 are proven. I could not locate the ledger's `evidence_required` text for 003 in the time available, so I do not judge it beyond the two missing cases.

## Not run
- Contract/sqlcgen/append-only CI mutations: not repeated (unchanged since a627e1f; cited).
- Local PostgreSQL/Redis integration suite and executing any corpus SQL against PostgreSQL: not run; CI build-test only.
- `docs/warroom/FOLLOWUPS.md` not written (brief: this file is the only one I write) — chair to copy R3-F1..F4.
- 003 `evidence_required` wording not read from the ledger.

## End check
PR head at end: b1c1734f583a46f7abc295dcc55094f9d3f5717e OPEN. Scratch directory deleted by exact path.

FINAL VERDICT: PASS — SHA b1c1734f583a46f7abc295dcc55094f9d3f5717e
