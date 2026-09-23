# VERIFY — vizra-core PR #13 "allowlist the Makefile line grammar before make, one line reader (B5d)" (queue 2p)

- **Verifier:** independent war-room verifier (did not write this code).
- **PR:** https://github.com/yegamble/vizra-core/pull/13 — OPEN, not a draft, base `main`, MERGEABLE.
- **Head verified:** `54a137680cb8c7f9be28fd6c8befd1078d32145e`, confirmed with `gh pr view 13` at start and at end. It is 3 commits on main `96d19b3` (= merge base = `origin/main`): `2dab194` code, `c6170f0` transcripts, `54a1376` COMMANDS record.
- **Clone:** fresh, in `mktemp -d …/vzv-core-pr13-XXXXXX`, with a second local clone for T0.
- **Host:** darwin/arm64, GNU Make 3.81, Python 3.9.6, go1.27.1, 19 GiB free.
- **4.3:** my own `vzvpr13-make43-<pid>` container (`--rm`) running the builder's `inside-4.3.sh`. `ubuntu:24.04` was ABSENT before, so this run pulled it; it was removed afterwards, since no container used it.
- **Method:**
  - I ran committed fixtures and scripts only, reading each first (`demo.sh`, `inside-4.3.sh`, `rows.py`, `mutations.py`, `probe-verdict.py`, both probes).
  - For item 2, I made in-process calls of core's and search's committed readers on inert strings, with `subprocess` replaced by a raising stub.
  - Byte mutations went through `mutate.sh`.
  - I authored no hostile Makefile. No classifier stopped anything, so nothing is NOT RUN on that ground.

## 1. Scope

- `git diff --name-only 96d19b3..HEAD` touches only `scripts/`, `docs/`, AGENTS.md and README.md.
- The **Makefile, `.github/pinned-makefiles.yml`, all of `.github/`, `api/`, `internal/`, `cmd/` and `migrations/` are unchanged.** No file deleted.
- The real Makefile's digest still equals main's pin.

**Tests: not weakened.** Every expectation that changed became stricter:
- **Fixtures now refused before make:** 9 makeguard fixtures moved from post-make expectations to pre-make grammar refusals, each gaining `notInvoked: true`: `resolver-cannot-resolve`, `resolver-computed-{shell,makeflags,recipeprefix,extra-prereqs}`, `prefix-from-function`, `prefix-from-pattern-specific`, `make-q-parse-error`, and `include-pinned-good` (an include now refused).
- **Post-make branches:** they keep red cases as 11 new in-process rows in `db-scan-probe.py`:
  - the resolver: SHELL no-op, MAKEFLAGS `i`, `.RECIPEPREFIX`, `.EXTRA_PREREQS`;
  - expanded prefix: a function, a target-specific variable;
  - `make -pn` failing;
  - `make -q` exit 1 and exit 2;
  - one `make -q` naming every pinned makefile.
  - The probe goes from 15 to 26 rows.
- **Include-based cases** (the included-file byte mutation, the include sibling, the mode-000 `inc.mk`): replaced by Makefile-only equivalents, because an include can no longer reach them. Examples are the Makefile mode-000 test and the one-invocation probe row.
- **The removed "control: pattern-specific ordinary variable" row:** such a line is now refused by the grammar.
- **0 skips** by my own count.

## 2. T0 — the new tests against `96d19b3` without the implementation

Clone at `96d19b3`, with the PR's `scripts/*_test.go` and `scripts/testdata` checked out on top and main's Python kept:
- `go test -count=1 -json ./scripts/` → exit 1;
- **11 top-level tests FAIL, 108 subtests FAIL**:
  - TestAMakefileMakeWouldRemakeIsRefusedWithoutRunningARecipe;
  - TestCIRequiredGuardMakefilePin;
  - TestEveryMakefileReaderConsumesTheOneLineReader;
  - TestEveryOutOfGrammarLineIsRefusedBeforeMake;
  - TestEveryRefusedSpellingIsRefusedBeforeMake;
  - TestMakeIntegrityGuardFixtures;
  - TestMakefileDigestMutations;
  - TestTheAnchorReadsTheRecipeMakeReads;
  - TestTheGrammarRefusesEveryLineReadersCouldSplitDifferently;
  - TestTheOneReaderSourceCheckRefusesAPlantedReader;
  - TestTheRealMakefileFitsTheGrammar.

**Matches the builder's claim exactly.**

## 3. The builder's demonstrations

| Item | 3.81 host (`demo.sh`, full) | 4.3 container (`inside-4.3.sh`) |
|---|---|---|
| demo exit / tree after | 0 / clean | 0 / clean |
| D-fixtures (5 grammar-only fixtures, failing gate stub) | all HELD: exit 1, 0 make processes, grammar refusal | all HELD |
| D-pins (check 11 on 2 grammar pins) | HELD | HELD |
| D-rows (`rows.py`, every row of `TestEveryOutOfGrammarLineIsRefusedBeforeMake`) | **84 held, 0 broken** (80 refusals + 4 controls) | 84 / 0 |
| D-one-reader-probe | 15 probes, 20 named non-makefile reads, 0 problems | same |
| D-db-scan-probe | 26 rows as expected | 26 |
| D-real-tree | both anchors 0, ci-required-guard 0 | same (plus full transcripts, exit 0) |
| C33 (grammar removed at `verify_pin`) / C34 (check 11 stops reporting it) / C35 (anchor stops reporting it) | BROKEN, then restored, HELD | same |
| C36 (reader cache removed: IDENTITY) / C37 (second reader in ci-required-guard: POISON and SOURCE) | probe exit 1, then 0 | same |
| C38 / C39 / C40 (Go tables) | go test exit 1, then 0 | (Go rows host-only) |
| C41 (grammar removed, every row) | **4 held, 80 broken**, then 84 held | same |
| makeguard fixtures (all 67) | — | 63 refused before make (0 make), 3 refused after make (`prefix-from-variable`, `prefix-from-chained-variable`, `suffix-from-variable`: `$(NAME)` recipes the grammar allows, resolved from make's database), 1 green (`good`) |

**"With the grammar removed, 47 of the 80 lines are accepted outright":** `mutate.sh` truncates transcripts, so I re-ran `rows.py` under `mutations.py C41` with full output. **47** rows had the anchor exit 0. The other 33 were refused by the older by-name or post-make checks, or were refused by the anchor but passed by check 11. Byte-identical restore. **Reproduced.**

## 4. Lanes

| Command | Exit | Counts |
|---|---|---|
| `make ci` (3.81 host) | **0** | all lanes; test-race 19 ok, including `internal/fixtures` 316.7 s |
| `go test -race -count=1 -v ./scripts/` | 0 | 39 top-level tests, **493 PASS**, 0 FAIL, 0 SKIP |
| both anchors / `ci-required-guard.sh` (3.81 and 4.3) | 0 / 0 / 0 | grammar ok line: 56 blank/comment, 11 assignment, 25 phony, 25 rule, 72 recipe |
| direct unit step + `go-test-report.py` | **not run locally** | CI is authoritative (below). The builder's local run timed out in `internal/fixtures` under host load; my `make ci` ran the same package green in 316.7 s |

## 5. CI on 54a1376 (my own `gh api`)

11 check-runs, all completed:

| Check run | Conclusion |
|---|---|
| **ci-required** | **success** (run 35910352650, `pull_request`, headSha `54a1376…`) |
| build-test | success |
| cache-matrix | success |
| both cache-matrix legs | success |
| fixtures | success |
| govulncheck | success |
| docker-build | success |
| append-only | success |
| GitGuardian | success |
| image-scan | failure (pre-existing, not required; reported only) |

- **ci-required fan-in:** SUCCESS for all six manifest lanes.
- **build-test log** (ubuntu-24.04, GNU Make 4.3):
  - 8 anchor steps pass, each printing the grammar ok line with the same counts;
  - `make ci: all lanes passed`;
  - direct unit suite **1488 executed, 0 skipped**;
  - integration and shuffled integration **1657 executed, 0 skipped** each;
  - `scripts` 493.

## 6. The hunt: lines the grammar accepts but make reads differently (item 2)

**Parity with search's merged makegate** (`vizra-search` `origin/main` = `4810048`, read-only; `git show` into my scratch):
- `makefile_lines`, `_continued`, `keeps_rule_open`, `recipe_lines`, `decode_makefile`, `_forbidden_char`, `_strip_comment`, and every grammar constant are **identical**: `ASSIGNABLE_SPECIALS`, `_G_NAME`, `_G_ASSIGN_RE`, `_G_WORD`, `_G_PHONY_RE`, `_G_RULE_RE`, `_G_IDENT_RE`, `_G_LEAD_RE` and `DIRECTIVE_KEYWORDS`.
- `_dollar_problems` differs only in a type annotation.
- `grammar_problems` differs only in wording and in core's one extra refusal: a backslash-continued rule or `.PHONY` line. **The grammar is a verbatim port, stricter in one place, as claimed.**

**In-process hunt** (my harness `hunt.py`): each inert line appended to the `good` fixture text, run through core (`grammar_problems` + `prerequisite_closure` + `check_text`, i.e. every pre-make text refusal) and through search (`grammar_problems` + `reviewed_bytes_problems`).

| Probe line(s) | core | search |
|---|---|---|
| CR in an assignment / a recipe; NUL in a comment; NBSP before `:=`; U+200B in a name; BOM; a line of only spaces; a TAB-only line after a rule; a comment ending in `\`; `ifdef`; a directive keyword as a name or target; `undefine`; `.SUFFIXES`, `.NOTPARALLEL`, `.DELETE_ON_ERROR`, `.SILENT`; `other::`; `a b &:`; target- and pattern-specific ordinary vars; nested `$(shell $(shell …))`; `$(shell … $(notdir …))`; a function, `$X` or a substitution reference in a value; `#` inside `$(shell …)`; `+=`, `!=`, `::=`; `$(MAKE)`/`${MAKE}` in any recipe; a TAB line after an assignment; a leading-space rule; a continued rule or `.PHONY` line | **refused** (by the grammar, by line) | refused |
| benign assignment; a continued assignment; even trailing backslashes; `\#` in a value; `VPATH`/`GPATH`/`MAKE`/`MAKEFILES`/`MAKEFILE_LIST`/`SUFFIXES` assignment; `.SHELLFLAGS` (approved value) and `.DEFAULT_GOAL`; `a=b:` (read by both as the assignment `a = b:`); a `Makefile:` rule with and without a recipe; a recipe continued with a `#` line; a recipe after a column-0 comment | accepted | accepted |
| **a `+`-prefixed recipe on a non-closure rule** | **accepted** | **refused** |
| **a recipe on a non-closure rule that BEGINS with `$(NAME)`** | **accepted** | **refused** |
| a `-`-prefixed recipe on a non-closure rule | accepted | accepted |

For every accepted line, the reader and GNU Make agree on the reading: continuation joining, comment ending, `a=b:` as an assignment, the rule staying open across a column-0 comment. **I found no line the grammar accepts that make reads differently.**

The assignments of make's own variables (`VPATH`, `MAKE`, `MAKEFILES`, `MAKEFILE_LIST`, …) are accepted by both repositories' grammars. Their neutering members (SHELL, the MAKEFLAGS family, `.RECIPEPREFIX`, `.EXTRA_PREREQS`) are refused by name in both. The rest affect prerequisite search (VPATH/GPATH, irrelevant to explicit phony closure targets), recursive make (`MAKE`, refused in recipes), or nothing make reads from a makefile (`MAKEFILES`).

## 7. One reader, for real (item 4)

- `grep` for `read_text(`, `read_bytes(`, `open(`, `splitlines(`, `split("\n")`, `readlines`, `.read()` over `make-integrity-guard.py`, `makefile_pin.py` and `ci-required-guard.py`: every hit is one of the probe's 20 `NAMED_READS`.
  - Makefile text is read only in `makefile_lines` (split), `decode_makefile` and `read_makefile_text`.
  - `verify_pin`/`recheck_pinned_bytes` read bytes to digest.
  - `load_makefile_pin` reads the pin file.
  - The rest read make's own output, workflow YAML, `required-checks.txt` or a module docstring.
- `go-test-report.py` and `image-scan-verdict.py` read no makefile.
- **The probes are meaningful:**
  - SOURCE is an AST walk over all three files (comments and docstrings don't count; aliases and `re.M` do), plus a per-function regex over 13 named readers.
  - POISON rewrites the text inside `makefile_lines` and requires every named reader's verdict to change.
  - IDENTITY requires one sequence object per text.
  - C36 (cache removed) and C37 (a second reader planted in ci-required-guard) turn it red on 3.81 and 4.3.
  - `TestTheOneReaderSourceCheckRefusesAPlantedReader` has 8 planted cases; it is part of the 493.
- **By reading, a residual:** `verify_pin` digests and decodes the bytes it read, but the anchor's later readers re-read the file from disk through `read_makefile_lines`. A file swapped in between is the existing, stated review-only TOCTOU residual.

## 8. The builder's pre-existing finding (a multi-line environment variable)

**Executed.** `VZV_NOTE=$'first line\nci: not-a-rule'` in the anchor's environment on the real tree gives anchor `--workflow` exit 1, "make's database has MORE THAN ONE entry for gate closure target `ci`", plus a closure mismatch, after 18 make processes. The same text on one line gives exit 0.

**It is a false refusal and fails closed**, because environment-origin variables are printed in make's `-pn` database, and the parser reads the multi-line value as entries.

**By reading, not executed:** the same mechanism lets whoever controls the runner's environment shape the database parse, e.g. a value containing make's end-of-database marker line. That is the stated "an earlier step writing the machine" residual. It can only affect the post-make defence-in-depth checks: the grammar and the text checks run before make, on the pinned bytes. Worth tightening; not a bypass of the primary control.

## 9. Doc sentences under "no false-guarantee merges"

| Sentence | Verdict |
|---|---|
| "The allowlist grammar is the PRIMARY pre-make control … every logical line … must be one of five shapes … or refused by file and line number with make not started, in both modes and check 11" (AGENTS.md, COMMANDS.md, anchor docstring, `makefile_pin` module docstring) | true (§3 D rows, §6; C33–C35 show both callers depend on it) |
| The five shapes, as described (the recipe shape "using only `$$` and `$(NAME)`") | accurate; it does not claim prefixes are restricted, and they are not (§6) |
| "`include` is outside the grammar, so the pinned read set is the root `Makefile` alone" | true (the include fixtures are now refused) |
| "ONE line reader … proves it (POISON, SOURCE, IDENTITY)" | true (§7) |
| "The real Makefile fits it unchanged (56/11/25/25/72)" | true on 3.81, 4.3 and CI |
| "What the grammar does not see: make's BUILT-IN implicit rules … answered by the one `make -q` and the explicit-.PHONY closure rule" | true, and properly scoped |
| `makefile_pin.py` block comment: "a recipe body that BEGINS with `$(NAME)` … is allowed by the grammar in both repositories — search refuses it by name, core resolves it from make's own database after make" | **imprecise**: core resolves it only for **gate-closure** recipe lines (`GATE_RECIPE_LINES`). On other rules it is neither refused nor resolved (§6). See F-2 |
| "a `+` or `$(MAKE)` recipe line still runs under [-q]; such a line can come only from the pinned, reviewed bytes" (COMMANDS.md:55, anchor :88) | true. Slightly stale: `$(MAKE)` is now refused by the grammar, while a `+` line on a non-closure rule is still possible (F-1) |
| COMMANDS B5d table: "direct unit step … 1 — FAIL, not a pass … `internal/fixtures` timed out … re-run alone … exit 0 (1015.9 s)" | honest record; CI's unit lane is green (§5) |

No sentence claims more than the code does, except the F-2 wording, which is about coverage of non-gate recipes, not a gate guarantee.

## 10. Findings

```
FINDING F-1: core accepts a `+`-prefixed (and a `$(NAME)`-led) recipe line on a NON-closure rule before make; search's merged makegate refuses both anywhere
Severity:    SHOULD (parity; core looser than search in one place). Not a regression, and not a false guarantee (the residual is stated)
Confidence:  high (executed in-process on both committed readers)
Affected:    vizra-core scripts/make-integrity-guard.py check_recipe / check_text (the `+` refusal applies to gate-closure recipes only); vizra-search scripts/makegate.py reviewed_bytes_problems (refuses `+` and `$`-led recipe lines on every rule)
Observed:    the §6 rows "`+`-prefixed recipe on a non-closure rule" and "`$(NAME)`-led recipe on a non-closure rule": core ACCEPTED, search REFUSED. The grammar also accepts a rule whose target is `Makefile`.
Failure:     a non-closure rule's recipe runs only when make updates that target. During the anchor, that can happen only in the makefile-remake phase, i.e. a rule for a pinned makefile under the `make -q` probe, where a `+` line still runs (the stated residual). Reachable only through reviewed, pinned bytes.
Recommendation: port search's by-name refusal of `+`-prefixed and `$`-led recipe lines on every rule, or refuse any rule whose target is a pinned makefile name. Either closes the residual rather than stating it.
Acceptance:  in-process, the two §6 rows are refused by core before make; the real Makefile stays green.
Cross-repo:  search: already refuses.
Challenge:   pinned bytes are reviewed, and the docs state the `+` residual.
```

```
FINDING F-2 (NIT): makefile_pin.py's block comment says core resolves a `$(NAME)`-led recipe body "from make's own database after make"; that is true only for gate-closure recipes. Suggest "for gate-closure recipes (check_expanded_prefixes); other rules' recipes are not resolved".
FINDING F-3 (NIT): the multi-line environment value in §8 is a false refusal (confirmed). By reading, the database parser could skip environment-origin variable blocks (or read targets only from the `# Files` section) so the runner's environment cannot shape it at all. Defence in depth only.
FINDING F-4 (NIT): several post-make branches that used to be exercised by real make output through committed fixtures are now covered only by synthetic database strings in db-scan-probe.py, because the grammar refuses the fixtures first. This is expected with a stricter pre-make control; it is recorded so the chair knows the post-make layer's evidence is now in-process only.
```

No BLOCKER, no REQUIRED, no regression.

## 11. Cleanup and head

- Scratch `vzv-core-pr13-XXXXXX` (both clones, the container copy, the outputs) was deleted by exact path.
- The container ran with `--rm`, and the pulled `ubuntu:24.04` was removed.
- vizra-search was used read-only (`fetch`, `show`); the builder's checkout was not touched.
- Head re-checked at the end: `54a137680cb8c7f9be28fd6c8befd1078d32145e`.

## Verdict

Every claim reproduced:
- **T0:** 11 tests and 108 subtests red on `96d19b3`;
- **rows:** 84/84 on 3.81 and 4.3, with C33–C41 red then green; 47 of 80 accepted outright with the grammar removed;
- **probes:** 15 one-reader probes and 26 database rows;
- **real Makefile:** fits 56/11/25/25/72;
- **scope:** Makefile, pin and `.github/` unchanged; no test weakened; 0 skips;
- **lanes:** `make ci` 0; `scripts` 493 PASS;
- **CI:** `ci-required` and all required lanes green on this SHA (unit 1488, integration 1657; only the known, non-required `image-scan` red).

The grammar is a faithful port of search's verified grammar, stricter in one place. My hunt found no line it accepts that make reads differently. The one parity gap (F-1) is core looser than search for non-closure recipes, reachable only through reviewed bytes and stated as a residual: SHOULD, not blocking.

FINAL VERDICT: PASS — SHA 54a137680cb8c7f9be28fd6c8befd1078d32145e

---

# Re-confirmation at 66fcb2e

- **Head:** `gh pr view 13` → `66fcb2e6976b90102a61a01008c9d24335ba157f` (OPEN, MERGEABLE) at start and at end. One commit on `54a1376` ("docs(scripts): narrow the grammar comment to what core resolves after make"). Fresh clone in `mktemp -d …/vzv-core-pr13rc-XXXXXX`.

## RC-1. The diff is comment-only

- `git diff --stat 54a1376 66fcb2e`: `scripts/makefile_pin.py`, 8 insertions and 3 deletions.
- Filtering `git diff -U0` for changed lines that are not `#` comment lines gives **0 lines**.
- `git diff --quiet 54a1376 66fcb2e -- Makefile .github` is clean: **the Makefile, the pin and `.github/` are unchanged.**
- `makefile_pin.py` compiles with `python3 -W error`.

## RC-2. The new comment sentences

| Sentence | Verdict |
|---|---|
| "Core's differences from search's grammar, all NARROWER: one — a RULE or PHONY line continued with a backslash is refused here (search refuses it by name, after its grammar). Otherwise the same shapes." | **Correct and complete.** My §6 function-by-function comparison against search `4810048` found `grammar_problems` differing only in wording, type annotations and this one refusal; the reader, the byte checks and every grammar constant are identical. My hunt rows "rule line continued" and ".PHONY continued" show core refusing by grammar and search by name |
| "core resolves the leading reference from make's own database after make (check_expanded_prefixes) ONLY for recipe lines of the GATE CLOSURE's targets" | correct; F-2 closed |
| "NOT refused before make here (verifier F-1 on #13, queued to 2o …): a grammar-conforming recipe line on a rule OUTSIDE the gate closure — the by-name recipe checks read only closure recipes, and the grammar allows `$(NAME)` in any recipe line" | correct: it matches my §6 rows (non-closure `+`, `-` and `$(NAME)`-led recipe lines accepted). "The grammar allows `$(NAME)` in any recipe line" has one exception, `$(MAKE)`, which the grammar refuses; the whole-file token scan still applies to every line. NIT only |

## RC-3. Tests

`go test -count=1 -json ./scripts/` → **exit 0: 493 pass, 0 fail, 0 skip** (39 top-level tests). The tree was clean afterwards.

## RC-4. CI on 66fcb2e (my own `gh api`)

11 check-runs, all completed:

| Check run | Conclusion |
|---|---|
| **ci-required** | **success** (run 35914283059, `pull_request`, headSha `66fcb2e…`) |
| build-test | success |
| cache-matrix | success |
| both cache-matrix legs | success |
| fixtures | success |
| govulncheck | success |
| docker-build | success |
| append-only | success |
| GitGuardian | success |
| image-scan | failure (pre-existing, not required; reported only) |

ci-required's fan-in: SUCCESS for all six manifest lanes.

## Verdict

- The commit is comment-only.
- The new sentences are accurate. F-2 is closed, and F-1 is now stated in the code and queued to 2o.
- `go test ./scripts/` is green.
- `ci-required` is green on `66fcb2e`.

FINAL VERDICT: PASS — SHA 66fcb2e6976b90102a61a01008c9d24335ba157f
