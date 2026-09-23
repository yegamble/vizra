# vizra-search PR #5 — closing slice: independent verification

- **Verifier:** fresh war-room verifier (did not write this code; saw no builder reasoning).
- **PR:** yegamble/vizra-search #5, branch `chore/m0-ci-hardening`.
- **SHA under test:** `617c6d92b34c1acb68556f5f02a5b12793344cf5` (one commit on `e068e07fed999141a601374bb2b3b6251ede04d6`).
- **Head at start:** `gh pr view 5 --json headRefOid` = `617c6d92b34c1acb68556f5f02a5b12793344cf5`; `git ls-remote … refs/heads/chore/m0-ci-hardening` = the same. State OPEN, 4 commits on `main`.
- **Clone:** fresh `git clone` into my own `mktemp -d …/scratchpad/vzv-search-pr5-closing-XXXXXX`, detached at the SHA.
- **Host:** darwin/arm64, go1.27.1, GNU Make 3.81, Python 3.9.6 (PyYAML 6.0.3), Docker 29.8.0 available (not used). **Nothing here ran on GNU Make 4.3.**
- **Inputs read:** vizra/AGENTS.md; the security desk review at e068e07 (M-1…M-5, N-1…N-3); VERIFY "Re-verification at e068e07, part 2" (FINDING 4); the plan's "Closing slice" section; the full diff `e068e07..617c6d9`.
- **Scope check (preflight):** `git diff --stat e068e07 617c6d9 -- Makefile api/` is empty. `shasum -a 256 Makefile` = `e9d7c58edc93ed4e95daa9ebb3553736864b5346cd10ca4004ad7f79c9f5d02c`, equal to the pin in `.github/pinned-makefiles.yml`. The pins-file change is a comment only.

(Sections below are appended as the run proceeds.)

## 1. Lanes (all run by me in the clean clone at 617c6d9, darwin/arm64, GNU Make 3.81)

| command | exit | counts / result |
|---|---|---|
| `make ci` (MAKEFLAGS, VERSION unset) | **0** | fmt-check clean; vet; echo-containment; build; contract-drift **365** tests / 4 pkgs / 0 failures / none deselected; `test` (-race) 7 pkgs ok; test-noskip: **664 tests / 7 packages / 0 skipped / 0 failed** (suite floor 470; scripts 277, httpapi 146, hmacauth 109, config 84, contract 26, cmd 16, buildinfo 6, each at or above floor); tidy-check tidy; vendor-contract-selftest **17/17** |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | **0** | **423 `--- PASS`, 0 `--- FAIL`, 0 `--- SKIP`**; `ok scripts 23.2s`, `ok internal/httpapi 7.0s` |
| — of which the new/changed tests | | `TestTheMakeLaunchInventorySeesEveryListedForm`: 31 matched + 10 not matched + 2 fails-closed subtests PASS; `TestNamedMakefileConstructsAreRefusedBeforeMake`: 28 subtests PASS (25 + `$@`, `$<`, `$X`); `TestARecipeBeginningWithAnEscapedDollarIsNotRefused` PASS; `TestEnvironmentTakenVariablesNeverReachMake`: 2/2 PASS, each logging 2 make processes (`-q Makefile`, `--dry-run …`) with `planted: none`; `TestEveryPlaceThatStartsMakeIsGated` PASS, sites = `[scripts/makegate.py:448]` |
| `python3 scripts/ci-hardening-demo.py` | **0** | **54/54 rows behaved as declared** (tree = HEAD 617c6d9, no working-tree changes) |
| `env -i PATH HOME GOPATH GOCACHE bash scripts/ci-required-guard.sh` | **0** | `passed (11 required check(s), 11 checked lane(s))` |
| `env -i … ./scripts/make-integrity-guard.sh --workflow` | **0** | `passed (9 gate target(s); make ran 21 time(s), by /usr/bin/make, only on the pinned bytes of Makefile, which are unchanged)`; last check line: "`make -q Makefile` again at the end: still nothing would be remade" (N-3) |
| `env -i … python3 scripts/vendor-contract.py --check` | **0** | `vendor-contract: OK — every vendored file matches the manifest.` |

All of the builder's local numbers are reproduced exactly: 664/0 skips, 423 PASS, 54/54, guards 0, 21 make runs.

**GitHub CI on 617c6d9** (read with `gh api …/commits/617c6d9…/check-runs`; not re-run): 13 check runs. All 12 workflow jobs, `ci-required` included, `completed/failure`, and the `ci-required` annotation reads "The job was not started because recent account payments have failed or your spending limit needs to be increased." GitGuardian `success`. **CI: BLOCKED (billing).** No job executed, so the required-checks manifest cannot be compared with jobs that ran.

## 2. Red/green

### 2a. The committed new tests against e068e07's gate files (the repo's own history)
A second worktree at 617c6d9 with `git checkout e068e07 -- scripts/makegate.py scripts/make-integrity-guard.py` (sha256 of both equal to `git show e068e07:<file>`: `c98b2fb7…`, `0fefd96f…`). Command: `go test -count=1 -v -run 'TestNamedMakefileConstructsAreRefusedBeforeMake|TestEnvironmentTakenVariablesNeverReachMake|TestARecipeBeginningWithAnEscapedDollarIsNotRefused' ./scripts/`.

| state | exit | result |
|---|---|---|
| e068e07 gate + 617c6d9 tests | **1** | **M-3 red for the stated reason:** `recipe_that_begins_with_$@`, `$<`, `$X (a one-letter variable)` FAIL: `exit 0; want "begins with an expansion" refused with 0 make processes started`. Every other named-construct row PASS. **M-4 red for the stated reason:** both subtests FAIL: `a make process received a variable the Makefile takes from the environment: MAKE-ENV -q Makefile \| planted: VERSION,COMMIT,CORE,GOFLAGS` and the same for `MAKE-ENV --dry-run --no-print-directory`, for `contract-drift-guard.py recipe` and for `makegate.py -- --dry-run contract-drift`. The `$$` control PASSES (it was never refused, as expected). |
| restored (`git checkout 617c6d9 -- …`, `git status` clean) | **0** | 33 PASS, 0 FAIL, 0 SKIP |

### 2b. FINDING 4 against e068e07's inventory
A worktree at e068e07 with only `scripts/ci-hardening-demo.py` copied from 617c6d9; `python3 scripts/ci-hardening-demo.py --only <row>` for C4…C10, one row each. **Every row: `MUTATED : exit 0 -> *** NOT RED AS DECLARED`, `RESTORED: exit 0 -> GREEN`, harness exit 1.** The e068e07 inventory misses all seven planted literal forms. FINDING 4 reproduced; matches the builder's `closing/finding4-planted-forms-at-e068e07-BEFORE.txt`.

### 2c. Builder's rows C1–C10 at 617c6d9 (from the full demo run in section 1)
C1 (makegate back to `$(`/`${` only), C2 (refuse every leading `$`, so `$$` too), C3 (`env=clean_env()` in run_make), C4–C10 (planted Go/Python/shell forms): each `MUTATED : exit 1 -> RED as declared` (the harness requires the row's declared text in the output), restored byte-identical (sha256 printed), `RESTORED: exit 0 -> GREEN`. **10/10 reproduced.**

## 3. Test strength (reading, plus evaluation of committed matchers on sample strings)

Method note: where I say "evaluated", I imported the committed function or pattern (for example `makegate.reviewed_bytes_problems`, `make-integrity-guard.logical_recipe_lines`, `makegate._REF_RE`, the Go `makeShellPattern` const, the `pyMakeCalls` program extracted verbatim from scripts_test.go) into a throwaway Python process and fed it an inert string. Nothing was written as a Makefile, nothing was run by make, and the repository was not touched. One sample `.py` file was written under my scratch dir, read by the extracted matcher, and deleted. No safety classifier stopped anything.

- **`TestEnvironmentTakenVariablesNeverReachMake` observes the real child environment, not the guard's belief.** It runs the caller under `runpy` with `subprocess.run` wrapped. For every call whose argv[0] basename is `make`/`gmake`, it records which of the four hard-coded planted names are in the `env` mapping handed to `subprocess.run`. That mapping is exactly what `execve` gives make. It is independent of `environment_taken()`'s output. It asserts per process, requires at least 2 make processes (so a recorder that sees nothing is red), and covers both non-anchor callers. It went red at e068e07 (2a) and under C3. Limits: it observes the spawn boundary, not make's own view (`$(origin VERSION)`); it plants 4 of the 7 names (not BUILD_TIME, IMAGE, CORE_REMOTE); and it would not see a make started through another API, which the inventory covers. Its success `t.Logf` ("none received …") also prints on failure (seen in 2a); cosmetic. **Adequate.**
- **The inventory's negative controls show it does not match everything, but they do not prove it never over-matches.** The 10 controls cover a commented call, make in a non-exec call, a non-make program through exec, make in a message, a subprocess call without make, a commented Python call, a shell comment, `echo make ci`, a `make-`prefixed script path, and `command -v make`. The strongest evidence of no practical over-match is the real tree: exactly one site, `scripts/makegate.py:448`. Evaluated over-match: the shell line `echo "done; make sure"` is a HIT. That fails safe (red), so it is not a guarantee problem.
- **The 2 parse-failure cases fail closed.** A `.go` or `.py` file that does not parse becomes a `problems` entry ("does not parse, so it is not cleared"). `TestEveryPlaceThatStartsMakeIsGated` calls `t.Errorf` on every problem, and the subtest asserts exactly one problem. A `.py` file with a `UnicodeDecodeError` or `ValueError` is also a problem. If the Python half cannot run at all, the result is `t.Fatalf("BLOCKED …")`. If python3 or PyYAML is missing, `requirePython` fails the test; it does not skip. **Yes, fail-closed.**
- **Evaluated reach of the widened shell pattern** (the committed const, which the test says Python's `re` and RE2 agree on):
  - HIT: `time make`, `{ make ci; }`, `` `make ci` ``, `nohup make`, `sudo make`, `else make`, `while make -q`, `x=1; exec make`, `echo x | make`, `command make`, and a tab or space before make.
  - MISS: **`env -u X make ci`** and **`sudo -u bob make ci`**, meaning env or sudo with a flag that takes a separate argument (FINDING 6). `xargs make`, `timeout 60 make`, `nice make` and `builtin make` also miss; AGENTS.md names these as review-only or they are "not listed".

## 4. Sentences against "no false-guarantee merges"

| sentence (at 617c6d9) | verdict |
|---|---|
| M-2 narrowing: AGENTS.md:545-562, makegate.py docstring step 2 (:32-41), the block comment (:250-257), the anchor docstring (:82-99): named constructs "in its LITERAL spelling at the start of a line"; computed names "NOT refused" | **Accurate.** It matches `_SPECIAL_TARGET_RE`, `_ASSIGN_CONTROLLED_RE` and `_DEFINE_CONTROLLED_RE`, which are all `^\s*`-anchored. |
| M-1 narrowing: the pattern, suffix, implicit, `.DEFAULT` and `$`-named-prerequisite recipes are "NOT scanned" (AGENTS.md:598-605, :655-666; anchor docstring :43-46, :93-95; `prerequisite_closure` docstring :399-416; GATE_TARGETS comment) | **The named exclusions are accurate. The positive half still overclaims:** "the text of the EXPLICIT rules of the named gate targets and of their prerequisite closure … may carry no `-` prefix and no `\|\| true`-family suffix". Two explicit-rule forms are not scanned: (a) a recipe written on the rule line after `;` (evaluated: `logical_recipe_lines(["test: ; -true"], 1)` → `[]`, while the tab form gives `[(2, '-true')]`); (b) a closure target that is not the FIRST name of a multi-target rule (`bar foo:`). The definitions match is `^foo\s*:`, so `foo` gets no definition and is only printed as a "note", and its tab recipe is never scanned (read at make-integrity-guard.py:592-610, :621-644). **FINDING 5.** |
| M-3: "A recipe line whose body (after any `@`/`-`/`+`) begins with `$` other than `$$` … is refused" (AGENTS.md:560-563, makegate.py:39-41, anchor docstring :90-91); "`+` recipe lines … refused" (AGENTS.md:551, makegate.py:38, anchor :90) | **Accurate for TAB-started recipe lines; overclaims for the `;` inline recipe.** Evaluated: `reviewed_bytes_problems("Makefile", "t:\n\t$@x\n")` gives 1 problem, but `"t: ; $@x\n"` gives 0; `"t:\n\t+true\n"` gives 1, but `"t: ; +true\n"` gives 0. The check runs only under `if raw.startswith("\t")` (makegate.py:284). **FINDING 5.** |
| M-4: "every make process, whichever caller opened the gate, also runs without the variables the pinned makefiles take from the environment (`?=` names, names referenced and never assigned, and GOFLAGS; today VERSION … GOFLAGS)" (AGENTS.md:566-570; makegate docstring step 3; `environment_taken` docstring) | **The mechanism is accurate** (`run_make` computes `environment_taken` from the pin on every call; 2a and C3 demonstrate it), **and the today-list is exact** (evaluated: `['BUILD_TIME','COMMIT','CORE','CORE_REMOTE','GOFLAGS','IMAGE','VERSION']`). "Referenced" is narrower than make's meaning: `_REF_RE` sees only `$(NAME)`/`${NAME}`. Evaluated misses: `$(V:a=b)`, `$V`, `ifdef V`, `$(origin V)`, `$(value V)`. A name read before its `:=` assignment is also not taken. None occurs in today's Makefile. **FINDING 7 (SHOULD).** |
| FINDING 4 narrowing: AGENTS.md:521-537 (what is matched) and :642-648 (review-only); makegate.py:9-14; test comment scripts_test.go:1261-1286; pins-file header | **Mostly accurate, and the seven P3 forms are now matched (2b/2c).** Two overclaims remain. (1) "`env`/`nohup`/`sudo` (with flags and `VAR=value` words)" at AGENTS.md:537 and scripts_test.go:1285: `env -u X make` and `sudo -u bob make` are not matched. (2) The Go half "(under any import name)" at scripts_test.go:1267-1268: a dot-import of os/exec (`Command("make")`, an `*ast.Ident`, not a selector) is not matched. The AGENTS.md Go sentence does not say "any import name". **FINDING 6.** |
| N-1: `ci-required-guard.py` "of the siblings it checks only `GNUmakefile`/`makefile`; a remake source … is caught only by the `make -q` probe" (AGENTS.md:584-588) | **Accurate. N-1 closed.** |
| N-2: evidence README:33-36, "as far as `TestEveryPlaceThatStartsMakeIsGated` can tell … make started through a variable, a wrapper or a form it does not match is review-only" | **Accurate. N-2 closed.** NIT: it says "see the closing slice below", but the closing slice section is ABOVE it (README:3). |
| N-3: "it ends with the same `make -q` probe again" | **Accurate.** The code is at make-integrity-guard.py:943-952, and the anchor log's last check line shows it ran. |
| AGENTS.md:531 (the old "aligned with vizra-core PR #10"), now "derived from … PR #10; core has since moved on to B5b … whose computed-name refusals this list does NOT have" | **Accurate. The stale claim is removed.** |
| Deviation: "a `$`-named prerequisite is dropped from core's closure too (read at 29387da, its make-integrity-guard.py:812), so that one is refused in neither repo yet" | **Line 812 confirmed:** I fetched core's file at 29387da with `gh api …/contents?ref=29387da`, and line 812 is `prereqs[n].extend(d for d in deps if not d.startswith("$"))`. "Refused in neither repo" is the builder's reading; I did not audit all of core for another refusal. This is an attributed cross-repo statement, not a search control. |
| Unchanged: "What it guarantees, exactly: make runs only on reviewed bytes …"; the remake-probe paragraph; "The same names are refused statically as job- or workflow-level `env:`"; "The direct lane … only through `scripts/makegate.py`" | Consistent with the code and with the committed tests I ran (unchanged from e068e07, where part 2 judged them consistent). |
| evidence README "Host for all of these: … go1.27.1" | NIT: the two BEFORE transcripts record `go version go1.26.2`. |
| evidence README "three controls are widened … FINDING 4 (the make-launch inventory reads Go with `go/ast`, Python with `ast` …)" | Mostly true, but the Python half is narrower than e068e07's in one form. **FINDING 8 (SHOULD).** |

## 5. Scope and deleted-line audit (`e068e07..617c6d9`)
- The Makefile and `api/` are unchanged (empty diff), and the Makefile's sha256 equals its pin. `.github/pinned-makefiles.yml` has a comment-only change.
- Deleted lines by file: scripts_test.go −40, make-integrity-guard.py −49, makegate.py −23, AGENTS.md −15, README −1, pins −1.
  - scripts_test.go −40 is the old regex inventory. Its only assertion, `t.Errorf("… starts make outside scripts/makegate.py")`, reappears in the new `TestEveryPlaceThatStartsMakeIsGated` together with the non-vacuity `t.Fatal`. Parse failures are now also errors.
  - make-integrity-guard.py −49: the environment-taken code moved to makegate and is re-exported. `check_environment_overrides` keeps its `--workflow` refusal, which the R-2 `VERSION=x` row still covers.
  - No `g.fail` was removed. No assertion was weakened. No `t.Skip` was added (grep of added lines). 0 skips in every run.
- One narrowing of detection that the brief does not ask about (see FINDING 8): the e068e07 Python regex matched any list literal starting with `"make"` on any line. The new ast half matches only inside a subprocess/os call's arguments. Evaluated on a sample, `ARGV = ["make", "ci"]` followed by `subprocess.run(ARGV)`: the old regex hits line 2 and the new matcher returns `[]`. AGENTS.md does list "make named through a variable" as review-only, so this is disclosed as a class but not as a regression.

## Findings

```
FINDING 5: the `;` inline recipe and the non-first name of a multi-target rule are outside the scans the narrowed sentences describe
Severity:    REQUIRED  (blocking under the chair's "no false-guarantee merges" rule; reviewed-bytes only)
Confidence:  high for the code paths (evaluated/read); make's handling of an inline recipe's prefix is per the GNU Make
             manual §5.1 ("the first recipe line may be attached to the target-and-prerequisites line with a semicolon")
             and §5.5; NOT measured here (the brief forbids building new hostile Makefiles)
Affected:
  repo:      vizra-search
  files:     scripts/makegate.py:284-295 (`if raw.startswith("\t")`: the `+` and leading-`$` checks see TAB lines only);
             scripts/make-integrity-guard.py:450-466 (logical_recipe_lines: TAB lines after the rule line only),
             :592-610 (definitions keyed on `^target\s*:`, so only the FIRST name of a rule line), :621-644
             (a closure target with no first-name definition is only a "note");
             sentences: AGENTS.md:551, :560-563, :598-605, :655-666; makegate.py:38-41; make-integrity-guard.py:43-46,
             :90-95, :399-416
  requirements: VZ-CI-ANCHOR-DIGEST (proposed)
Observed:
  Evaluated with the committed functions on inert strings:
    reviewed_bytes_problems("Makefile", "t:\n\t+true\n")  -> 1 problem;  "t: ; +true\n" -> 0
    reviewed_bytes_problems("Makefile", "t:\n\t$@x\n")    -> 1 problem;  "t: ; $@x\n"   -> 0
    logical_recipe_lines(["test:", "\t-true"], 1) -> [(2, '-true')];  logical_recipe_lines(["test: ; -true"], 1) -> []
  Read: for a closure prerequisite `foo` defined only as `bar foo:` (foo not first), `re.match(r"^foo\s*:", …)` never
  matches, so definitions["foo"] stays empty and foo is listed under "note … treated as file dependencies"; its
  explicit recipe is not passed to check_recipe.
Failure:
  The closing slice rewrote these sentences to say exactly what is refused and scanned. They still say that the text of
  "the EXPLICIT rules of the named gate targets and of their prerequisite closure" carries no `-` prefix, that `+`
  recipe lines are refused, and that a recipe line whose body begins with `$` is refused. A reviewer who trusts them
  would not look for `test: ; -go test …`, `test: ; +cmd` (runs under the anchor's own -n/-pn) or `lint foo:` with a
  `-` recipe. The dry-run cannot show the `-`. This is the same class as M-1/M-3.
Perspective: developer, operator
Recommendation:
  Smallest: add both forms to the not-scanned / not-refused lists in every sentence named above (for example, "TAB-started
  recipe lines only; a recipe written after `;` on the rule line, and a target that is not the first name of its rule
  line, are not read"). Better, and still small: in reviewed_bytes_problems, refuse a `;` on a non-TAB rule line
  outside a variable assignment; in the anchor, fail a closure target whose rule names it anywhere other than first.
Acceptance criteria:
  Either every listed sentence names both forms as not scanned, or pinned inert fixtures `t: ; +true`, `t: ; $@x` and
  a closure target defined as `x t:` with a `-` recipe are red before make with 0 make processes (the repo's
  TestNamedMakefileConstructsAreRefusedBeforeMake idiom), and the clean Makefile stays green.
Tests: rows in scripts/scripts_test.go TestNamedMakefileConstructsAreRefusedBeforeMake (re-pinned, refusal by name,
  0 make, ci-required-guard parity); no new harness needed.
Cross-repo implications:
  core: appears shared. At 29387da core uses the same RULE_RE (:782) and logical_recipe_lines (:827) shape. UNVERIFIED
  whether a core check catches the inline form. | user: none | search: this PR | meta: none
Challenge:
  "Reviewed bytes only, and an inline `-` recipe is conspicuous." True, and the same was said of M-3's `$@`. The chair's
  rule is about what the sentence promises, and the sentence promises this shape is refused or scanned.
```

```
FINDING 6: the inventory sentence says `env`/`sudo` "with flags" are matched, but a flag that takes an argument is not
Severity:    REQUIRED  (FINDING 4's class under the chair's rule; a narrow wording or one-regex fix)
Confidence:  high (evaluated the committed makeShellPattern)
Affected:
  repo:      vizra-search
  files:     AGENTS.md:535-537; scripts/scripts_test.go:1282-1289 (makeShellPattern and its comment), :1267-1268
             (Go "(under any import name)")
  requirements: none (R-1 of the security desk review)
Observed:
  makeShellPattern is `(?:env|nohup|sudo)\s+(?:-\S+\s+)*(?:VAR=\S*\s+)*`, so a flag's separate argument
  breaks the match. Evaluated: `env -u X make ci` MISS, `sudo -u bob make ci` MISS; `env -i PATH=/usr/bin make ci` HIT
  (the committed test row). The Go half checks `call.Fun.(*ast.SelectorExpr)`, so a dot-import of os/exec
  (`Command("make")`) is not matched, although the test comment says Go calls are matched "under any import name".
Failure:
  The re-verification asked that the sentences "name exactly the forms matched and list the rest as review-only". These
  two forms are literal make launches that the sentences place inside the matched set.
Perspective: developer
Recommendation: say "flags without a separate argument" (or widen `-\S+(?:\s+[^-\s]\S*)?`, at the cost of over-match),
  and drop "under any import name" for Go or name the dot-import as review-only. Add the misses to the review-only list.
Acceptance criteria: AGENTS.md and the test comment match the evaluated behaviour, or the forms are added to
  TestTheMakeLaunchInventorySeesEveryListedForm as matched rows.
Tests: rows in TestTheMakeLaunchInventorySeesEveryListedForm (`sh behind env -u NAME`, `sh behind sudo -u user`, `go a dot-import`).
Cross-repo implications: none
Challenge: these are unusual in this repo's scripts. They are also exactly what "(with flags …)" tells a reader is covered.
```

```
FINDING 7: environment_taken's "referenced" is `$(NAME)`/`${NAME}` only
Severity:    SHOULD
Confidence:  high (evaluated makegate._REF_RE)
Affected:    vizra-search scripts/makegate.py:410-439; AGENTS.md:566-570; makegate docstring step 3
Observed:    `$(V:a=b)`, `$V`, `ifdef V`, `$(origin V)` and `$(value V)` yield no reference, and a name read before its `:=`
             assignment is counted as assigned. None occurs in today's Makefile, so the today-list is exact.
Failure:     A future pinned Makefile could read an environment value that run_make does not drop, while the sentence says every
             make runs without "the variables the pinned makefiles take from the environment". An earlier step must plant
             the variable, which is the declared residual.
Recommendation: word the sentence as the regex ("names referenced as `$(NAME)`/`${NAME}` and never assigned"), or widen the
             reading to substitution references, `ifdef`/`ifndef`, `$(origin …)` and `$(value …)`.
Tests:       a table test of environment_taken over inert text rows.
Cross-repo:  core: its equivalent reading is unexamined. Others: none.
Challenge:   M-4 was a SHOULD, and nothing in today's bytes is affected.
```

```
FINDING 8: the "widened" Python inventory no longer matches a make argv list held in a variable, which e068e07 matched
Severity:    SHOULD
Confidence:  high (the old regex and the new pyMakeCalls, both evaluated on one inert sample)
Affected:    vizra-search scripts/scripts_test.go (pyMakeCalls vs the deleted pyList regex); evidence README "three controls are widened"
Observed:    `ARGV = ["make", "ci"]` / `subprocess.run(ARGV)`: the e068e07 regex hits line 2; the new matcher returns [].
Failure:     A detection that existed is silently dropped in a change described as widening. AGENTS.md does list "make named
             through a variable" as review-only, so there is no false guarantee, but there is an undisclosed regression.
Recommendation: also report any list or tuple literal whose first element matches PROG, anywhere in a .py file (the old rule),
             or record the narrowing in the README.
Tests:       a matched row "py an argv list held in a variable" in TestTheMakeLaunchInventorySeesEveryListedForm.
Cross-repo:  none
Challenge:   variable-held argv is review-only by the stated contract. It was nonetheless caught before this commit.
```

NITs (3):
- The evidence README:35 says "see the closing slice below", but that section is above (README:3).
- The evidence README says the host was go1.27.1 for all transcripts, but the two BEFORE transcripts record go1.26.2.
- `TestEnvironmentTakenVariablesNeverReachMake` logs "none received …" (scripts_test.go:1784) even on a failing subtest. The FAIL status is still correct, but the log line reads as success.

### Closed at 617c6d9 (reproduced or read)
- **M-3 (code):** closed for TAB recipe lines. It goes red at e068e07 and green now, C1 and C2 reproduce, and `$$` stays green. The inline-recipe gap is in FINDING 5.
- **M-4 (code):** closed. It goes red at e068e07 and green now, C3 reproduces, and the test observes the spawn environment.
- **FINDING 4:** the seven P3 forms are now matched. C4–C10 are red now and all 7 were missed at e068e07. The residual wording is in FINDING 6.
- **M-1 and M-2:** the named exclusions (computed names; pattern, suffix and implicit rules, `.DEFAULT`, `$`-named prerequisites) are stated accurately. The positive claim about explicit rules still overreaches (FINDING 5).
- **N-1, N-2 and N-3:** closed.

## What did not run
- **GitHub CI:** BLOCKED by billing. No job started on 617c6d9, and I did not re-run it.
- **GNU Make 4.3:** nothing ran on it (host 3.81 only).
- **Live make behaviour of the FINDING 5 forms:** not measured, because the brief forbids new hostile Makefiles. The code paths were evaluated; the make semantics come from the manual.
- **Core:** I read one line of core (29387da:812) and no more.

## Instruction-shaped text in tool output
None observed. The demo, test, guard, gh and git outputs contained no instruction-shaped text.

## Cleanup
- Removed my two worktrees (`wt-mix`, `wt-e068`) and my `mktemp -d` scratch directory by exact path. The demo harness removed its own `tempfile.mkdtemp` copy (its `finally`). No container or image was created.

## Head at end
`gh pr view 5 --json headRefOid` = `617c6d92b34c1acb68556f5f02a5b12793344cf5`; `git ls-remote` `refs/heads/chore/m0-ci-hardening` and `refs/pull/5/head` = `617c6d92b34c1acb68556f5f02a5b12793344cf5`. The head did not move.

## Verdict
Every lane is green locally, and every number the builder reported reproduces: `make ci` 664/0 skips, 423 PASS, demo 54/54, guards 0, vendor check 0. The M-3, M-4 and FINDING 4 tests go red on e068e07's code and green on 617c6d9. C1–C10 reproduce. The Makefile, its pin and `api/` are unchanged, and no assertion was weakened.

The slice's own goal was "every gate sentence claims no more than its control", and two REQUIRED false-guarantee findings remain:
- FINDING 5: the narrowed "EXPLICIT rules" and "recipe line whose body begins with `$`" / "`+` recipe lines" sentences do not hold for a `;` inline recipe or for a closure target that is not the first name of its rule line.
- FINDING 6: "`env`/`sudo` with flags" and Go "under any import name" name forms the inventory does not match.

Both can be fixed by rewording alone. CI remains BLOCKED by billing.

FINAL VERDICT: FAIL — SHA 617c6d92b34c1acb68556f5f02a5b12793344cf5

---

# Re-verification at 888a51b (closing slice, fix round 1 of 2)

- **SHA under test:** `888a51b872f15fa5fa0ca9d323f4d06a9b12d166` (one commit on `617c6d9`).
- **Head at start:** `gh pr view 5 --json headRefOid` = `888a51b872f15fa5fa0ca9d323f4d06a9b12d166`; `git ls-remote` `refs/heads/chore/m0-ci-hardening` and `refs/pull/5/head` = the same. State OPEN.
- **Clone:** fresh clone in my own `mktemp -d …/scratchpad/vzv-search-pr5-888a-XXXXXX`, detached at the SHA.
- **Host:** the same as above (darwin/arm64, go1.27.1, GNU Make 3.81, Python 3.9.6). **Nothing ran on GNU Make 4.3.**
- **Scope:** `git diff --stat 617c6d9 888a51b -- Makefile api/ .github/` is empty. The Makefile's sha256 is `e9d7c58e…`, equal to its pin. The changed files are AGENTS.md, the evidence README, `closing/round1/` (7 transcripts), `ci-hardening-demo.py`, `ci-required-guard.py` (docstring only), `make-integrity-guard.py`, `makegate.py` and `scripts_test.go`.

## R1. Lanes (run by me at 888a51b)

| command | exit | counts / result |
|---|---|---|
| `make ci` (MAKEFLAGS, VERSION unset) | **0** | contract-drift 365 / 0 failures / none deselected; test-noskip **689 tests / 7 packages / 0 skipped / 0 failed**, every package at or above its floor; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | **0** | **448 PASS / 0 FAIL / 0 SKIP**. The inventory test has 38 matched, 13 not-matched and 2 fails-closed subtests. The named-construct test has 41 subtests. `TestMakeIntegrityGuardStillRefusesKnownShapesInReviewedBytes` has 10. The M-4 test is 2/2, and each run logs 2 make processes, neither of which received any of the 12 planted names. The inventory's sites are `scripts/makegate.py:545` (a `("make", "gmake")` membership tuple, which the argv-literal rule matches) and `:636` (run_make). |
| `env -i … bash scripts/ci-required-guard.sh` | **0** | 11 required checks |
| `env -i … ./scripts/make-integrity-guard.sh --workflow` | **0** | make ran 21 times, and the final `make -q` ran |
| `env -i … python3 scripts/vendor-contract.py --check` | **0** | OK |

The builder's local numbers reproduce: 689/0 skips, 448 PASS, guards 0. The demo result is in R3.

## R2. The new tests against 617c6d9's gate files, then restored

This is a worktree at 888a51b with `git checkout 617c6d9 -- scripts/makegate.py scripts/make-integrity-guard.py scripts/ci-required-guard.py`. The command is `go test -count=1 -v -run 'TestNamedMakefileConstructsAreRefusedBeforeMake|TestMakeIntegrityGuardStillRefusesKnownShapesInReviewedBytes|TestEnvironmentTakenVariablesNeverReachMake' ./scripts/`.

| state | exit | result |
|---|---|---|
| 617c6d9 gate files + 888a51b tests | **1** | **20 FAIL / 36 PASS / 0 SKIP.** 13 new pre-make rows fail with `want "<refusal>" refused with 0 make processes started`: inline `;` ×3, two targets, `&:`, a non-first special target, `$(I)ORE:`, whitespace, backslash, computed name global/target-specific, `define`, `$(call eval,…)`. Both new anchor rows fail with `exit 0, want a refusal naming …`: the conditional within the test recipe, and the ci line whose comment holds `=`. Both M-4 callers fail: the make processes received `VZ_M4_SUBST,Q,VZ_M4_ORIGIN,VZ_M4_VALUE,VZ_M4_EARLY,VZ_M4_IFDEF`. Each row is red for its stated reason. |
| restored (`git checkout 888a51b -- scripts/`, status clean) | **0** | 56 PASS / 0 FAIL / 0 SKIP |

**Inventory BEFORE:** in a worktree at 617c6d9 with only the new demo copied in, I ran `ci-hardening-demo.py --only R11` … `R16`. Every row gave `MUTATED : exit 0 -> *** NOT RED AS DECLARED` and `RESTORED: exit 0 -> GREEN`, and the harness exited 1. This matches `closing/round1/inventory-planted-forms-at-617c6d9-BEFORE.txt`.

## R3. Demo, rows R01–R16
`python3 scripts/ci-hardening-demo.py` at 888a51b exited **0** with **70/70 rows behaved as declared**. In R01–R16 every row gave `MUTATED : exit 1 -> RED as declared`, was restored byte-identical (16/16), and gave `RESTORED: exit 0 -> GREEN`. The output has no `NOT RED`, `NOT IDENTICAL` or `STILL RED` anywhere. **16/16 reproduced.**

**GitHub CI on 888a51b** (`gh api …/check-runs`, not re-run): 12 jobs failed and GitGuardian succeeded. The `ci-required` annotation reads "The job was not started because recent account payments have failed …". **CI: BLOCKED (billing).**

## R4. The committed functions on inert strings (no Makefile written, none run)
`makegate.reviewed_bytes_problems("Makefile", s)`, number of problems:

| refused (≥1) | NOT refused (0) |
|---|---|
| `t: ; +true`, `t: ; $@x`, `test: ; -true`, `t:;-true`, `t : ; -true`, `t:: ; -true`, `lint foo:⏎⇥-true`, `a b: ; x` (2), `a &: b`, `x .IGNORE:`, `$(T): ; -true` (2), ` t: ; -true` (2), `t: \⏎ ; -true` (2), `$(M)AKEFLAGS += -i`, `test: $(S)HELL = x`, `define $(X)`, `ifeq (a,b)⏎foo: ; -true⏎endif` | **`test: ; -go test -run=Foo ./...`**, **`test: dep ; -false X=1`**, **`test: ; @echo a=b`**, **`private foo: ; -true`**, **`override foo: ; -true`**, **`private foo:⏎⇥-true`**, **`override a b:`**, **`private a b &: ; -true`**, **`undefine foo: ; -true`**, **`load foo: ; -true`**; and, correctly not refused: `test: X = 1`, `test: X = a;b`, `test: X=1 ; -true` (a target-specific value), `export foo: ; -true`, `unexport foo: ; -true`, `vpath foo: ; -true` |

`makegate._MANUFACTURES_DIRECTIVES_RE`:
- It matches `$(call eval,…)`, `$(call guile,…)`, `$(call $(F),…)`, `${call eval,…}`, `$(call  eval,…)`, `$(call $F,…)` and `$(foreach f,eval,$(call $f,x))`.
- It does not match `$(call ev$(A)al,x)`.
- It correctly does not match `X := $(call foo,eval)`.

`make-integrity-guard.logical_recipe_lines(lines, 1)`:
- A plain conditional inside a recipe (`test:`, `⇥go test`, `ifeq (a,b)`, `⇥-false`, `else`, `⇥true`, `endif`, `⇥-x`) returns all four TAB lines, which is correct.
- **`test:`, `⇥go test`, `ifeq (a,b)`, `X := 1`, `endif`, `⇥-false` returns `[(2, 'go test')]`.** The same happens with `foo:` in place of `X := 1`. The reader stops at the first non-TAB line inside the branch, so `-false` after `endif` is not read.

## R5. By reading
- **Is KEEP_ENV safe? Acceptable, and disclosed.**
  - Of the kept names, `SHELL` is the only one the Makefile mentions. Make never takes SHELL from the environment (GNU Make manual §5.3.2), and the Makefile assigns it at :25.
  - KEEP_ENV subtracts only from `environment_words`, not from `environment_taken`. A kept name referenced as `$(NAME)` and never assigned (a future `$(HOME)`) is therefore still dropped from gate make processes, and the `--workflow` anchor would refuse it. That fails closed.
  - The remaining reach is a future reviewed Makefile that reads a kept name another way (`$(HOME:a=b)`, `ifdef TERM`, `$(origin TZ)`), combined with an earlier step setting it. That is the declared "earlier step" and "variables outside the named set" residual. The sentence names the keep-list.
- **Does conditional stepping match make? No, in one case (FINDING 10).**
  - make ignores every line of a false branch, including assignments and rule lines. In read.c the `ignoring` check comes before an assignment ends the rule context. So a recipe continues after `endif`.
  - The reader continues only over TAB lines and conditional keywords. The branch-stepping itself is right: R08 reproduces, and both branches are read.
- **Is the anchor's narrower refusal stated accurately? Yes, with one misleading word (FINDING 13).**
  - AGENTS.md:500-508 says `$(NAME)`/`${NAME}` only. The anchor docstring (:61-64), the `check_environment_overrides` message and ci-required-guard's docstring all say the same.
  - The word "instead" at AGENTS.md:506 is the problem: "every make process the gate starts runs without it instead". The lane's own pinned `make` step is not a gate process.

## R6. Changed sentences under "no false-guarantee merges"

| sentence | verdict |
|---|---|
| FINDING 6: AGENTS.md:524-549 and scripts_test.go:1276-1311. They cover a flag with one argument, a Go dot-import, Python star-imports, and argv literals anywhere. The review-only list adds `nice`, `env -S`, `getattr`, `importlib` and concatenation. | **Accurate**, backed by R11–R16 and the matched and not-matched rows. The argv-literal rule over-matches in the safe direction: the `("make", "gmake")` membership tuple at makegate.py:545 is a site. |
| FINDING 7: AGENTS.md:589-596 and makegate docstring step 3. Every word except the keep-list is dropped; a name assembled from parts is not. | **Accurate** (R10, and R2 for the M-4 rows). |
| FINDING 8: README "restores the form e068e07 matched" | **Accurate** (R16). |
| Anchor env refusal: AGENTS.md:500-508, anchor docstring :61-64, ci-required-guard docstring | Accurate except "instead" (FINDING 13, SHOULD). |
| M-2: "a variable name that is an expansion in any assignment … or `define` … refused outright"; "a rule target that is an expansion" | **Accurate** for the evaluated forms. |
| `$(eval …)` "refused directly and through `$(call eval,…)`, `$(call guile,…)` or `$(call $(F),…)`" (AGENTS.md:569-571, makegate:33-34) | Accurate as a list of spellings. The README's reason, "because `call` runs the built-in of that name", also applies to `$(call ev$(A)al,…)`, which is not matched (FINDING 12, SHOULD). |
| **FINDING 5 fix:** "any rule line naming more than one target", "a rule with an inline `;` recipe (`t: ; -true`) … refused", "every recipe line is a TAB line" (AGENTS.md:575-580); makegate docstring :42-47 and :400-404; anchor docstring :44-47, :93-97 and :411-414 ("makegate has already refused, before make, every rule line the reading could misattribute"); README:9-10 | **OVERCLAIMS.** Two cases are missed: an inline recipe whose text contains `=` (FINDING 9), and a rule line whose first word is `private`/`override` (and `undefine`/`load` on 3.81) (FINDING 11). |
| "recipe lines read through conditional directives" (AGENTS.md:627); "the TAB lines of EVERY branch are read" (anchor :469-471); "steps over conditional directives, as make does" (README:21) | **OVERCLAIMS**: a non-TAB line inside a branch ends the reading (FINDING 10). |
| Closure "read with comments stripped" | **Accurate** (R09). |
| NITs from 617c6d9 | Closed: README "above"; the go1.26.2 header explained; the M-4 `t.Logf` now guarded by `!t.Failed()`. |

## R7. Scope and deleted-line audit (`617c6d9..888a51b`)
- The Makefile, its pin, `.github/` and `api/` are unchanged.
- **Assertions:**
  - The only deleted assertion is the M-4 `t.Errorf`, re-added with "can read" wording.
  - The anchor's `RULE_RE` was replaced by makegate's `_rule_parts`. No `g.fail` was removed.
  - The M-4 test now runs on a re-pinned copy: the real Makefile plus an inert block. It still plants VERSION, COMMIT, CORE and GOFLAGS, adds 8 names, and still asserts each make process.
- No `t.Skip` was added. 0 skips in every run. **No weakened assertion found.**

## Findings (fix round 1)

```
FINDING 9: an inline `;` recipe whose command text contains `=` is not refused
Severity:    REQUIRED  (the FINDING 5 fix is incomplete, and its sentences say this shape is refused)
Confidence:  high for the code path (evaluated). make's parse, read by me from GNU make's read.c and not measured: the
             rule line is cut at the first unquoted `;` BEFORE make tests for a target-specific assignment, and only
             the text before the `;` can make it one.
Affected:
  repo:      vizra-search
  files:     scripts/makegate.py:417 (`if "=" not in bare_rest and ";" in bare_rest:`), where `=` ANYWHERE in the rest
             suppresses the refusal; scripts/make-integrity-guard.py:444-446 (the closure skips such a rest as an
             assignment); sentences AGENTS.md:578-580, makegate.py:45-46 and :402, make-integrity-guard.py:45-47, :96,
             :413, README:9
  requirements: VZ-CI-ANCHOR-DIGEST (proposed)
Observed:    reviewed_bytes_problems gives 0 problems for `test: ; -go test -run=Foo ./...`, for `test: dep ; -false X=1`
             and for `test: ; @echo a=b`, and 1 problem for `test: ; -true`.
Failure:     A pinned `test: ; -go test -race -count=1 $(PKG) -run=.` (any flag written `-x=y`) passes makegate. The anchor
             reads only the TAB lines after `test:`, so it sees no recipe, and the dry-run prints the command without
             the `-`. The lane's failure is ignored. This needs reviewed bytes.
Recommendation: follow make: cut `rest` at its first `;` outside expansions, and treat the rule as a target-specific
             assignment only if the text BEFORE the `;` has a bare `=`; otherwise refuse the inline recipe. Apply the same
             cut in prerequisite_closure.
Acceptance criteria: the three spellings above are red before make with 0 make processes; `test: X = a;b` and
             `test: X=1 ; y` (target-specific values) stay green.
Tests:       rows in TestNamedMakefileConstructsAreRefusedBeforeMake, plus a control row for `test: X = a;b`.
Cross-repo:  core: unexamined. user/meta: none.
Challenge:   the builder may say `=` after `;` is ambiguous. It is not: make decides from the text before the `;`.
```

```
FINDING 10: the recipe reader stops at a non-TAB line inside a conditional branch make ignores
Severity:    REQUIRED  (the sentences say every branch is read)
Confidence:  high for the code path (evaluated). make semantics per GNU Make manual §7.2 (the false branch's text is
             ignored) and read.c (in an ignored branch an assignment or rule line does not end the rule context). Not
             measured.
Affected:    scripts/make-integrity-guard.py:480-484 (conditional keywords are stepped over; any other non-TAB line
             `break`s); sentences AGENTS.md:627, make-integrity-guard.py:44-45 and :469-471, README:21
Observed:    logical_recipe_lines(["test:","\tgo test","ifeq (a,b)","X := 1","endif","\t-false"], 1) gives
             [(2, 'go test')]. The same happens with `foo:` in place of `X := 1`.
Failure:     In a pinned Makefile, `test:` followed by `⇥go test …`, `ifeq (a,b)`, any non-TAB line, `endif` and
             `⇥-false`: make runs `-false` as part of test's recipe, and the anchor never reads it.
Recommendation: while inside a conditional opened within the recipe (depth > 0), skip non-TAB lines instead of
             stopping. Stop only at depth 0. Reading TAB lines that make would give a different rule is over-scanning,
             which fails safe.
Acceptance criteria: the fixture above is red ("prefixed `-`"), and the clean Makefile stays green.
Tests:       a row next to "- prefix inside a conditional within the test recipe" in reviewedBytesEvasions.
Cross-repo:  core: unexamined.
Challenge:   a non-TAB line inside a recipe's conditional is unusual. So is everything this list refuses; the sentence
             says "EVERY branch".
```

```
FINDING 11: rule lines whose first word is `private` or `override` (and, on GNU Make 3.81, `undefine` or `load`) are exempt
Severity:    REQUIRED  (the sentences say every multi-target and inline-`;` rule line is refused)
Confidence:  medium. The code path is certain (evaluated). How make parses these lines comes from its source as I read it,
             and I did not measure it:
               - 3.81 has no `private`, `undefine` or `load` keyword (they arrived in 3.82 and 4.0), so
                 `private foo: ; -true` is a two-target rule there;
               - in 4.x, parse_var_assignment returns a non-assignment line unchanged, and no directive handles a
                 leading `private` or `override`, so the line is parsed as a rule.
Affected:    scripts/makegate.py:293-294 (`_DIRECTIVES` includes private, override, undefine, load) and :406-408
             (such a first word returns []); the same sentences as FINDING 9
Observed:    0 problems for `private foo: ; -true`, `override foo: ; -true`, `private foo:⏎⇥-true`,
             `override a b:`, `private a b &: ; -true`, `undefine foo: ; -true` and `load foo: ; -true`.
             `export` and `unexport` lines are correctly exempt, because make handles them as export directives.
Failure:     For a closure prerequisite `foo` written as `private foo:`, the anchor's `^foo\s*:` finds no definition, so
             foo is only a "note" and its recipe (TAB or inline) is not read. A gate SEED written that way is red ("not
             defined"), so the exposure is non-seed closure targets.
Recommendation: exempt only lines that are assignments, which `_rule_parts` already detects. For `private`, `override`,
             `undefine` and `load` lines that are not assignments, apply the rule checks, or refuse such a line outright.
Acceptance criteria: the evaluated spellings are red before make; `override X := 1` and `private X = 1` stay green.
Tests:       rows in TestNamedMakefileConstructsAreRefusedBeforeMake.
Cross-repo:  none known.
Challenge:   make 4.x might reject `override foo:` differently from how I read it. If so, the row is red either way and costs
             nothing.
```

```
FINDING 12: `$(call ev$(A)al,…)` is not matched
Severity: SHOULD   Confidence: high (evaluated)
Affected: makegate.py:108 (_MANUFACTURES_DIRECTIVES_RE); README:14 ("because `call` runs the built-in of that name")
The listed spellings are accurate. A partly computed function name in `call` is not listed and not matched. Either refuse
`$(call` whose first argument contains `$` anywhere before the comma, or list it as not refused.
```

```
FINDING 13: "every make process the gate starts runs without it instead" can read as covering the lane's own make step
Severity: SHOULD   Confidence: high (reading)
Affected: AGENTS.md:505-507
The pinned workflow `make` step is not a gate process. A name the Makefile reads as `$V`, `ifdef V` and so on, if planted
by an earlier step, reaches that make: the anchor does not refuse it, and nothing drops it. Today's Makefile has no such
read. Add "the pinned workflow make step still receives it".
```

## What did not run (fix round 1)
- **GitHub CI:** BLOCKED (billing).
- **GNU Make 4.3:** nothing ran on it.
- **Live make behaviour of FINDINGS 9–11:** not measured, because the brief forbids authoring or running Makefiles. The code paths were evaluated; the make semantics come from the manual and my reading of make's source.
- **Safety classifier:** no stop occurred.

## Instruction-shaped text
None observed in any tool output.

## Cleanup (fix round 1)
My worktrees (`wt-mix`, `wt-617`) and my `mktemp -d` directory are removed by exact path (see below). The demo removed its own temp copy.

## Verdict at 888a51b
**What holds:**
- Every lane is green locally, and the builder's numbers reproduce: 689/0 skips, 448 PASS, demo 70/70, guards and vendor check 0.
- Every new test goes red on 617c6d9's gate files for its stated reason (20 FAIL), and green when restored.
- R01–R16 reproduce, and R11–R16 are missed by 617c6d9's inventory.
- FINDINGS 6, 7 and 8 and the 3 NITs are closed.
- The Makefile, its pin, `.github/` and `api/` are unchanged, and no assertion was weakened.

**What fails:** the FINDING 5 fix is incomplete in three places. Its sentences say these shapes are refused or read, and they are not:
- FINDING 9: an inline `;` recipe containing `=`.
- FINDING 10: a non-TAB line inside a recipe's conditional ends the reading.
- FINDING 11: `private`/`override` rule lines are exempt.

These three are REQUIRED under the "no false-guarantee merges" rule; FINDINGS 12 and 13 are SHOULD. CI remains BLOCKED by billing.


**Head at end (888a51b):** `gh pr view 5 --json headRefOid` = `888a51b872f15fa5fa0ca9d323f4d06a9b12d166`; `git ls-remote` `refs/heads/chore/m0-ci-hardening` and `refs/pull/5/head` = the same. The head did not move. The scratch clone `vzv-search-pr5-888a-QqaK84` and its two worktrees were removed by exact path.

FINAL VERDICT: FAIL — SHA 888a51b872f15fa5fa0ca9d323f4d06a9b12d166

---

# Re-verification at e711d33 (closing slice, fix round 2 of 2, the last)

- **SHA under test:** `e711d336e147583a084252387f4a19697e5f8788` (one commit on `888a51b`).
- **Head at start:** `gh pr view 5 --json headRefOid` = `e711d336e147583a084252387f4a19697e5f8788`; `git ls-remote` `refs/heads/chore/m0-ci-hardening` and `refs/pull/5/head` = the same. State OPEN.
- **Clone:** fresh clone in my own `mktemp -d …/scratchpad/vzv-search-pr5-e711-XXXXXX`.
- **Host:** darwin/arm64, go1.27.1, GNU Make 3.81, Python 3.9.6. **Nothing ran on GNU Make 4.3.**
- **Method:** the repo's committed tests; the repo's own history; and in-process calls of the committed functions on inert strings. I wrote no Makefile and ran make on none. No safety classifier stopped anything.
- **Scope:** `git diff --stat 888a51b e711d33 -- Makefile api/ .github/` is empty. The Makefile's sha256 is `e9d7c58e…`, equal to its pin.

## E1. Lanes and demo (run by me at e711d33)

| command | exit | counts / result |
|---|---|---|
| `make ci` | **0** | contract-drift 365; test-noskip **720 tests / 7 packages / 0 skipped / 0 failed**; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | **0** | **479 PASS / 0 FAIL / 0 SKIP** |
| of which | | `TestNamedMakefileConstructsAreRefusedBeforeMake` 72 subtests; `TestTheRealMakefileFitsTheGrammar` PASS, logging `assignment:15 blank/comment:133 phony:17 recipe:24 rule:17`, `RECIPE_FUNCTIONS = []`; `TestTheRemakeProbeCoversEveryPinnedInclude` PASS; `TestTheAnchorRefusesAPinnedMakefileMakeWouldRemake` 10/10, where e.g. "newer Makefile.sh \| anchor exit 1: make would REMAKE a pinned makefile"; `TestEveryOtherMakeCallIsGated` 8/8; `TestTheLaneGuardRefusesEveryKnownBypass/-run_hidden_behind_a_make_variable` PASS; `TestTheLaneGuardRefusesAFlagFromAnIncludedMakefile` PASS; M-4 2/2 |
| `python3 scripts/ci-hardening-demo.py` | **0** | **75/75 rows behaved as declared.** The output has no NOT RED, NOT IDENTICAL or STILL RED. G1–G6 and the redefined R01 and R04 each go red as declared and green after a byte-identical restore. |
| `env -i … bash scripts/ci-required-guard.sh` | **0** | 11 required checks. It reaches the grammar through `mg.check_pinned_bytes`, which calls `static_read_set` and then `grammar_problems` (read). |
| `env -i … ./scripts/make-integrity-guard.sh --workflow` | **0** | make ran 21 times |
| `env -i … python3 scripts/vendor-contract.py --check` | **0** | OK |

**GitHub CI on e711d33:** 12 jobs failed and GitGuardian succeeded. The `ci-required` annotation reads "The job was not started because recent account payments have failed …". **CI: BLOCKED (billing)**, not re-run.

## E2. The new tests against 888a51b's gate files, then restored
This is a worktree at e711d33 with `git checkout 888a51b -- scripts/makegate.py scripts/make-integrity-guard.py`.
- **Result:** `go test -count=1 -v -run 'TestNamedMakefileConstructsAreRefusedBeforeMake|TestTheRealMakefileFitsTheGrammar|TestTheRemakeProbeCoversEveryPinnedInclude|TestEnvironmentTakenVariablesNeverReachMake' ./scripts/` exits 1. The same run of `TestTheLaneGuardRefusesAFlagFromAnIncludedMakefile` in `./internal/httpapi/` exits 1. Together: **35 FAIL / 44 PASS / 0 SKIP.**
  - **All 31 grammar rows are red.** 24 fail with `exit 0; want "outside the makefile grammar" refused with 0 make processes`, meaning 888a51b accepted them outright. The other 7 are exit 1, refused by an older check with a different message.
  - `TestTheRealMakefileFitsTheGrammar` is red (no grammar function).
  - `TestTheRemakeProbeCoversEveryPinnedInclude` is red: "want it refused by the grammar before make".
  - The lane test is red: "expected the include refused by the Makefile grammar before make".
  - These numbers match the builder's "24 accepted outright, 7 caught only by other checks".
- **Restored** with `git checkout e711d33 -- scripts/` (status clean): both packages `ok`.

## E3. Hunting for a line the grammar accepts that it shouldn't (`makegate.grammar_problems` on inert strings)

**Refused (G ≥ 1):**
- **Directive lines:** every directive as a directive: `ifeq`, `ifdef`, `include`, `-include`, `sinclude`, `load`, `define`, `undefine`, `export X`, `export X = 1`, `unexport`, `override X = 1`, `private X = 1`, `vpath …`.
- **Rule forms:** `.IGNORE:`, `a:: b`, `a b &: c`, `a &: b`, `a: b | c`, `%: %.c`, `.c.o:`, `a: X = 1`, `a: ; true`, `a: b\ c`, `a:b`, `x: .WAIT`, `a: -lfoo`, `a: ~/x`.
- **Assignment values:** `$(shell $(shell id))`, `$(Y:a=b)`, `$Y`, `${shell id}`, `$(eval Y)`, `$(shell echo #)`.
- **Recipe lines:** `$(MAKE)`, `${MAKE}`, `$(value MAKE)`, `$@`.
- **Layout:** a TAB line outside a rule, leading spaces, a rule line ending CR, a fullwidth `：`, a Cyrillic target.

**Accepted (G = 0) and consistent with make:**
- `.PHONY: a b`, `Makefile: x`, `a.o: a.c`.
- `X := $(shell echo $(Y))`, `$(shell echo $$(date))`, `$(shell⇥id)`, `X := a # c`, `X := a\#b`, `X := 1 ; y`, `X = a:b`.
- Recipe lines with `-`, `$$x`, `$(X)` or a raw `#`.
- A backslash-continued rule line, and an assignment continued onto a TAB line.
- Special variable names: `VPATH`, `MAKEFILE_LIST`, `CC`, `MAKE`, `MAKEFILES`, `SUFFIXES`.
- `+true` passes the grammar but is refused by name (R=1).

**Accepted (G = 0) where make's meaning, or the anchor's reading, differs:**
1. **A comment line ending in an unescaped backslash.** GNU Make manual §3.1: "a trailing backslash not escaped by another backslash will continue the comment across multiple lines." Two strings show it:
   - `test:⏎⇥go test⏎# note \⏎inert:⏎⇥-false⏎`;
   - `test: # c \⏎inert:⏎⇥-false⏎`, a rule line with a trailing continued comment.

   The grammar and make agree here: the comment swallows `inert:`, the rule stays open, and `-false` is **test's** recipe. The anchor's text reading (`make-integrity-guard.py` reads `path.read_text().split("\n")`, and `logical_recipe_lines` works on physical lines) does not. It skips the `#` line, stops at `inert:`, and returns `[(2, 'go test')]` and `[]` respectively. **The `-` prefix on a recipe line of a gate target is unread → FINDING 14.**
2. **A lone CR inside a comment**, i.e. the physical line `# note\rX := 1` between recipe lines: grammar G=0. makegate decodes bytes and keeps the `\r`, and so does make. The anchor's `read_text()` uses universal newlines and turns `\r` into a line break, so it stops at `X := 1` and misses a later `⇥-false`. Same finding.
3. **CRLF and NUL** (the grammar differs from make; confidence medium, from my reading of GNU make's `readline()` source, not measured):
   - make strips a CR before LF, so `# c \` followed by CRLF continues the comment, while the grammar sees the line end in `\r` and does not join.
   - a NUL mid-line makes make drop the rest of that physical line and join the next line to it ("Athena lossage" path).

   Both are accepted in comment lines (G=0). Either way the grammar's view of the following lines is not make's. This belongs in FINDING 14's recommendation: refuse `\r`, NUL and other control characters except TAB.
4. **Directive keywords as assigned NAMEs**: `ifdef := 1`, `endif := 1`, `else := x`, `define = x`, `export := 1`, `include := x`, `override ?= 1`, `private := 1`, `vpath := x`, `load := x` are all G=0.
   - In GNU Make 4.x, `parse_var_assignment` runs first, so these are assignments.
   - In 3.81 I am NOT sure. I recall a check that skips conditional parsing only when the second token is exactly `:`, `+` or `=`, so `ifdef := 1` … `endif := 1` may be parsed as a conditional pair that hides the lines between them.
   - UNVERIFIED, confidence low. **FINDING 15 (SHOULD):** refusing these ~15 keywords as NAMEs costs nothing.
5. **A Unicode-whitespace-only line** (U+00A0 NBSP): G=0, because `str.strip()` treats it as blank. make sees `\xc2\xa0` and stops with "missing separator", so it fails loudly and nothing is bypassed. NIT.

## E4. The two changed assertions (plus the moved rows)
- **`TestTheLaneGuardRefusesAFlagFromAnIncludedMakefile`** (httpapi). Its premise, `include drift.mk`, is now refused by the grammar, so asserting "the include is refused, make was NOT invoked" is right. The coverage it used to give is still exercised: `TestTheLaneGuardRefusesEveryKnownBypass/-run_hidden_behind_a_make_variable` (lane_selection_test.go:379-382, `TESTFLAGS ?= -run=…` then `$(TESTFLAGS)` in the recipe) passes with want "carries -run". That form is grammatical, so it reaches make through the gate. **Justified; coverage preserved.**
- **`TestTheRemakeProbeCoversEveryPinnedInclude`.** The pinned include can no longer reach make. A second pinned file that make would not read is refused as a stale pin (makegate.py:686-690, the "pins … which make would NOT read" refusal at :689). So the multi-file form of the one-invocation probe (`make -q Makefile inc.mk`) is **no longer reachable, and not exercised**. The single-file probe is still exercised where it can reach make: `TestTheAnchorRefusesAPinnedMakefileMakeWouldRemake` 10/10 with a byte-identity assert, the `TestEveryOtherMakeCallIsGated` newer-`Makefile.sh` rows 8/8, and the anchor's final `make -q`. The include-following code in `static_read_set` is now unreachable for an accepted pin. **Justified.** The docstring states this accurately.
- **Moved or reduced rows:**
  - The anchor row "- prefix inside a conditional within the test recipe" is now a before-make grammar row, and the conditional stepping in the reader was removed. That is justified, because conditionals cannot be written.
  - The M-4 test's planted forms dropped `$V`, `$(V:a=b)`, `$(origin)`, `$(value)` and `ifdef`. Each is now a grammar row, and the 7 remaining names still assert per make process. Justified.

## E5. The built-in implicit-rule residual
- **Stated accurately:** at AGENTS.md "What they cannot do" and at the anchor docstring (:44-50, :414-420; the note at :47-50 and :415-418). A recipe make supplies from its built-in implicit rules is not scanned, "for a closure prerequisite with no explicit rule (printed as a note; there are none today), or for a target whose explicit rule has no recipe and is not `.PHONY`".
- **Reachable within the grammar: yes.** A literal prerequisite word such as `test: foo`, with no rule and a `foo.c` or `foo.sh` beside it, gets a built-in recipe. So does a non-`.PHONY` rule with no TAB lines. The built-in recipes expand variables the grammar lets a reviewer assign (`CC`, `LINK.c` …, for example `CC := -false`). make applies a `-` prefix after expansion, and that expansion happens in a recipe the text reading never sees.
- It remains a residual that needs reviewed bytes, as stated. Core B5b's `.PHONY`-closure rule is the named follow-up.

## E6. Changed sentences

| sentence | verdict |
|---|---|
| The grammar's five shapes (AGENTS.md "every line of the reviewed bytes fits the Makefile grammar"; makegate docstring step 2 and the block comment at :265-293; README round 2) | **Accurate as a description of `grammar_problems`**: each shape matches the code, and E3's refused list holds. The one gap against make is E3 items 3-4, which are FINDING 14's CRLF and NUL part and FINDING 15. |
| "Any other line is refused with its line number. So a conditional, `include`, … cannot appear, in any spelling." | Accurate for the listed constructs (E3). |
| **"Because of the grammar, a rule's recipe is exactly the TAB lines after it"** (AGENTS.md, the "What it guarantees" paragraph); **"every TAB recipe line of the EXPLICIT rules … may carry no `-` prefix"**; anchor docstring :44-47 "so a rule's recipe is exactly the TAB lines after it"; `logical_recipe_lines` docstring "a rule's recipe is exactly the TAB lines after it, up to the next line of another shape" | **OVERCLAIMS (FINDING 14).** It is true of the grammar's logical lines, but the anchor reads physical lines, and a continued comment moves the next line into the comment. |
| "A `-`/`+` prefix cannot be produced that way, because a recipe body may not begin with an expansion" (residuals) | Accurate for explicit recipes: the by-name check refuses a leading `$` after `@-+` and whitespace, and a value cannot hold a newline without `define`. Built-in recipes are covered by the separate implicit-rule residual (E5). |
| FINDING 13: "One read the anchor does NOT refuse remains possible: an immediate `:=` value referencing a name assigned only LATER … the lane's own pinned `make` step … would still receive it" | **Accurate. F13 closed.** In the grammar, `$(NAME)` is the only make read, and `environment_taken` misses only the read-before-assignment case. (A shell's own `$$NAME` read belongs to the existing "variables outside the named set" residual.) |
| makegate "WHAT IT DOES NOT DO" and the anchor residual, now describing the grammar | Accurate. |
| The by-name functions' docstrings now call themselves diagnoses with known misses | Accurate. |
| ci-required-guard gets the grammar through `check_pinned_bytes` | Accurate (E1). |

## E7. Scope and deleted-line audit (`888a51b..e711d33`)
- The Makefile, its pin, `.github/` and `api/` are unchanged.
- **Removed assertions:**
  - the two changed tests' old asserts (E4);
  - the conditional reading row (moved, E4);
  - the M-4 planted forms (moved, E4).

  Every removed assertion is either replaced or moved to a before-make row that runs and passes.
- No `t.Skip` was added. 0 skips in every run.
- Code: the anchor's conditional stepping was removed (conditionals are refused), and `RULE_RE` was already gone in round 1. No `g.fail` was removed.

## Findings (fix round 2)

```
FINDING 14: a backslash-continued comment line moves the next line into the comment, and the anchor's `-` scan stops there
Severity:    REQUIRED  (the grammar accepts it; make and the grammar agree the TAB line after it belongs to the open rule;
             the anchor's reading, which the sentences say reads "every TAB recipe line", does not)
Confidence:  high for the code path (evaluated). make: GNU Make manual §3.1, "a trailing backslash not escaped by
             another backslash will continue the comment across multiple lines" (not measured, per the brief).
Affected:
  repo:      vizra-search
  files:     scripts/make-integrity-guard.py:461-484 (logical_recipe_lines: physical lines; a `#` line is skipped
             without following its continuation) and :552-566 (read_text().split("\n")); scripts/makegate.py:378-436
             (grammar_problems accepts the continued comment as one blank/comment line and keeps the rule open);
             sentences AGENTS.md ("Because of the grammar, a rule's recipe is exactly the TAB lines after it"),
             make-integrity-guard.py:44-47 and the logical_recipe_lines docstring
  requirements: VZ-CI-ANCHOR-DIGEST (proposed)
Observed:
  grammar_problems("Makefile", "test:\n\tgo test\n# note \\\ninert:\n\t-false\n") gives [] and
  logical_recipe_lines(<its lines>, 1) gives [(2, 'go test')].
  grammar_problems("Makefile", "test: # c \\\ninert:\n\t-false\n") gives [] and the anchor's recipe for test is [].
  makegate._logical_lines of the second string gives ['test: ', '\t-false', ''], which is make's view and the grammar's.
  Also: a lone `\r` inside a comment (`# note\rX := 1`) is one line to makegate (bytes) and to make, but two lines to
  the anchor (read_text, universal newlines), which then stops at `X := 1`.
Failure:     In a pinned Makefile, a `-` prefix on a gate target's recipe line placed after a backslash-ended comment
             passes the grammar and every anchor reading. The dry-run prints it without the `-`, and the lane's
             failure is ignored. This needs reviewed bytes, and it is the M-1 class this slice exists to close.
Recommendation (smallest): in grammar_problems refuse a comment whose logical line was joined from more than one
             physical line (a comment ending in an odd number of backslashes), and refuse `\r`, NUL and any other
             control character except TAB anywhere. Or have logical_recipe_lines and the anchor's definitions loop
             read makegate._grammar_lines over the same decoded bytes. Doing both is cheap.
Acceptance criteria: the two strings above, and `# c\rX := 1` between recipe lines, are red before make with 0 make
             processes; the real Makefile still fits.
Tests:       rows in TestNamedMakefileConstructsAreRefusedBeforeMake ("grammar: a comment continued with a backslash",
             "grammar: a CR", "grammar: a NUL").
Cross-repo:  core: unexamined.
Challenge:   "Nobody ends a comment with a backslash." The chair's allowlist exists so that "nobody writes that" is
             no longer the argument.
```

```
FINDING 15: directive keywords are accepted as assigned variable names
Severity:    SHOULD   Confidence: low (make 3.81 behaviour UNVERIFIED; on 4.x they are plain assignments)
Affected:    scripts/makegate.py `_G_NAME` / `_G_ASSIGN_RE` (any identifier)
Observed:    `ifdef := 1`, `endif := 1`, `else := x`, `define = x`, `export := 1`, `include := x`, `override ?= 1`,
             `private := 1`, `vpath := x`, `load := x`, `undefine = 1` all give G=0.
Failure:     If 3.81 (the local host's make) parses `ifdef := 1` as a conditional, a pinned pair could hide lines from
             make that the grammar and anchor read, for example a gate recipe, turning the lane into a no-op locally.
Recommendation: exclude the directive keywords from NAME in the grammar.
```

NIT: a line that is only Unicode whitespace (NBSP) counts as blank to the grammar (`str.strip()`). make stops with "missing separator", so it fails loudly. Checking blank lines as `[ \t]*` would match make.

## What did not run (round 2)
- **GitHub CI:** BLOCKED (billing).
- **GNU Make 4.3:** nothing ran on it.
- **Live make behaviour of FINDING 14 (comment continuation, CRLF, NUL) and FINDING 15:** not measured, because the brief forbids authoring or running Makefiles. FINDING 14's comment-continuation part rests on the manual's text. The CRLF, NUL and FINDING 15 parts rest on my reading of make's source.

## Instruction-shaped text
None observed.

## Cleanup and head at end (e711d33)
- The worktree `wt-mix` and the scratch clone `vzv-search-pr5-e711-lA2HRK` are removed by exact path. The demo removed its own temp copy. No container or image was created.
- **Head at end:** `gh pr view 5 --json headRefOid` = `e711d336e147583a084252387f4a19697e5f8788`; `git ls-remote` `refs/heads/chore/m0-ci-hardening` and `refs/pull/5/head` = the same. The head did not move.

## Verdict at e711d33
**What holds:**
- Every lane is green locally, and the builder's numbers reproduce: `make ci` 720/0 skips, 479 PASS, demo 75/75, guards and vendor check 0, and the real Makefile at 133/15/17/17/24.
- All 31 grammar rows are red on 888a51b's gate files (24 accepted outright, 7 caught by other checks), and green when restored.
- G1–G6 reproduce.
- FINDINGS 9–13 are closed by the grammar. Both changed assertions are justified, and the coverage they gave is kept where it can still reach make.
- The Makefile, its pin, `.github/` and `api/` are unchanged, with 0 skips and no weakened assertion.

**What fails:**
- **FINDING 14 (REQUIRED).** The grammar accepts a comment line continued with a backslash (and a CR or NUL in a comment). There, the anchor's physical-line recipe reader stops early, so a `-` prefix on a gate target's recipe line goes unread. The sentence "a rule's recipe is exactly the TAB lines after it" is then false for the reading that enforces it. The fix is small (refuse continued comments and control characters in the grammar, or have the anchor read the grammar's logical lines).
- **FINDING 15** is a low-confidence SHOULD.

CI remains BLOCKED by billing.

FINAL VERDICT: FAIL — SHA e711d336e147583a084252387f4a19697e5f8788

---

# Verification of re-plan at 854a337 (one line reader; FINDINGS 14 and 15)

- **SHA under test:** `854a3376f005dc7cca3358d9b815205616f7b2fb` (one commit on `e711d33`, fresh builder).
- **Head at start:** `gh pr view 5 --json headRefOid` = `854a3376f005dc7cca3358d9b815205616f7b2fb`; `git ls-remote` `refs/heads/chore/m0-ci-hardening` and `refs/pull/5/head` = the same. State OPEN.
- **Clone:** fresh clone in my own `mktemp -d …/scratchpad/vzv-search-pr5-854a-XXXXXX`.
- **Host:** darwin/arm64, go1.27.1, GNU Make 3.81, Python 3.9.6. **Nothing ran on GNU Make 4.3.**
- **Method:** committed tests; the repo's own history; in-process calls of the committed functions on inert strings. I wrote no Makefile and ran make on none. No safety classifier stopped anything.
- **Scope:** `git diff --stat e711d33 854a337 -- Makefile api/ .github/` is empty. The Makefile's sha256 is `e9d7c58e…`, equal to its pin.

## V1. Lanes and demo (run by me at 854a337)

| command | exit | counts / result |
|---|---|---|
| `make ci` | **0** | contract-drift 365; test-noskip **801 tests / 7 packages / 0 skipped / 0 failed**; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | **0** | **560 PASS / 0 FAIL / 0 SKIP**. `TestTheGrammarRefusesEveryLineReadersCouldSplitDifferently` 37 subtests (31 refused + 6 controls). `TestEveryMakefileReaderConsumesTheOneLineReader` 17 subtests; its log reads "15 reader probes changed verdict under a poisoned makefile_lines; no second splitter; one sequence per text per program (3)". `TestTheAnchorReadsTheRecipeMakeReads` PASS. `TestNamedMakefileConstructsAreRefusedBeforeMake` 96. `TestTheRealMakefileFitsTheGrammar` PASS at `assignment:15 blank/comment:133 phony:17 recipe:24 rule:17`. |
| `python3 scripts/ci-hardening-demo.py` | **0** | **85/85 rows behaved as declared.** No NOT RED, NOT IDENTICAL or STILL RED. R09 (re-pinned) and C11–C20 each go red as declared and green after a byte-identical restore. |
| `env -i … bash scripts/ci-required-guard.sh` | **0** | 11 required checks |
| `env -i … ./scripts/make-integrity-guard.sh --workflow` | **0** | make ran 21 times |
| `env -i … python3 scripts/vendor-contract.py --check` | **0** | OK |

**GitHub CI on 854a337:** 12 jobs failed and GitGuardian succeeded. The `ci-required` annotation reads "The job was not started because recent account payments have failed …". **CI: BLOCKED (billing)**, not re-run.

**The real Makefile: every reader's output is byte-identical to e711d33's.** I ran one script against a worktree at e711d33 and against my clone at 854a337 and compared the JSON: grammar, by-name refusals, static read set, parse-time sites, environment_taken, environment_words, closure over GATE_TARGETS, and `check_text`'s failures and log. **All 9 are IDENTICAL.**

## V2. New tests against e711d33's gate code, then restored
This is a worktree at 854a337 with `git checkout e711d33 -- scripts/makegate.py scripts/make-integrity-guard.py scripts/ci-required-guard.py scripts/contract-drift-guard.py`.
- **Result:** `go test -count=1 -v -run 'TestTheGrammarRefusesEveryLineReadersCouldSplitDifferently|TestEveryMakefileReaderConsumesTheOneLineReader|TestTheAnchorReadsTheRecipeMakeReads|TestNamedMakefileConstructsAreRefusedBeforeMake|TestTheRealMakefileFitsTheGrammar' ./scripts/` exits **1**, with **59 FAIL / 79 PASS / 0 SKIP**:
  - 31 inert-string subtests fail, e.g. `"test:\n\tgo test\n# note \\\ninert:\n\t-false\n": grammar_problems gave []; want a refusal naming "a comment continued onto the next line"`;
  - 24 re-pinned rows fail: 5 with `exit 0; want … refused with 0 make processes` (accepted outright) and 19 with exit 1 but not the named refusal;
  - the probe test fails because `ci_required_guard` has no `mg`;
  - `TestTheAnchorReadsTheRecipeMakeReads` fails because `makegate` has no `makefile_lines`.

  That is 55 red subtests, matching the builder's claim, plus 4 red parents.
- **Restored** with `git checkout 854a337 -- scripts/` (status clean): **155 PASS / 0 FAIL / 0 SKIP.**

## V3. My FINDING 14 and 15 examples, through BOTH the grammar and the anchor's recipe reader (inert strings)

| input | grammar problems | anchor recipe for `test` (over `makefile_lines`) |
|---|---|---|
| F14a `test:⏎⇥go test⏎# note \⏎inert:⏎⇥-false` | 2 (refused) | `[(2,'go test'),(5,'-false')]`, which is make's reading |
| F14b `test: # c \⏎inert:⏎⇥-false` | 2 (refused) | `[(3,'-false')]`, make's reading |
| F14c lone CR in a comment | 2 (refused) | `[(2,'go test'),(4,'-false')]`: no universal-newline split |
| F14d `# c \` + CRLF | 1 (refused) | n/a |
| F14e NUL in a comment | 1 (refused) | n/a |
| NBSP-only / spaces-only / TAB-only / VT / FF / ZWSP / BOM / DEL | refused | n/a |
| control: even backslashes `⇥go test \\⏎⇥-false` | 0 | `[(2,'go test \\\\'),(3,'-false')]` |
| control: recipe continued onto `# not a comment` / onto `inert:` | 0 | the joined line, then `-false`, which is make's reading (the recipe continuation belongs to the recipe) |
| control: `# c \\` (escaped pair) then `inert:` | 0 | `[(2,'go test')]` (not continued, in both) |
| F15: `ifdef := 1`, `endif := 1`, `endif:=1`, `ifeq= 1`, `else`, `define`, `endef`, `export`, `unexport`, `include`, `sinclude`, `override ?=`, `private`, `vpath`, `load`, `undefine` as NAME; `ifdef: x`, `export:` as target | 1 each (refused) | n/a |
| control: `IFDEF := 1`, `ifdefx := 1` | 0 | n/a |

**The grammar and the anchor now read the same lines, or the line is refused. FINDINGS 14 and 15, and the NBSP NIT, are closed.**

## V4. One reader, for real?
- **grep of `scripts/`** (`read_text`, `read_bytes`, `open(`, `split("\n")`, `splitlines`, `decode(`):
  - Makefile bytes are read only in `makegate.read_makefile_text` and `check_pinned_bytes`, both through `decode_makefile`, and split only in `makefile_lines`. `load_pin` splits the pin YAML, which is not makefile text.
  - The remaining `.splitlines()` calls parse make's stdout and stderr, docstrings, or the manifest.
  - ci-required-guard's `read_text` calls read workflow YAML and the manifest. contract-drift-guard's `open` calls read the manifest, Go test sources and report files.
  - **No reader of makefile text outside `makefile_lines` in `scripts/*.py`.**
- **Go tests that read the Makefile:**
  - `TestTheRealMakefileFitsTheGrammar` uses `open(...).read()` (universal newlines). It is a test-side reader only. Had the real Makefile a CR, this test would see LF-converted text and pass, while the gate itself (bytes, `decode_makefile`) would refuse, so `make ci` and the anchor go red. The failure is loud, not hidden. **NIT:** use `mg.read_makefile_text`.
  - `scripts_test.go` also reads the Makefile with `os.ReadFile` only for digests and byte-identity.
  - `cmd/vizra-search/main_test.go:514` reads the Makefile for the `make run` loopback check. That is product behaviour, not a gate reader.
- **Are the POISON, SOURCE and IDENTITY probes meaningful? Yes, for the 15 named readers.**
  - **POISON:** each module's `makefile_lines` attribute is wrapped to rewrite the text. Callers look it up as a module global, so `read_makefile_lines` inside makegate is covered too. A reader that bypasses it keeps its clean verdict and fails the probe. C15 and C16 re-introduce a `read_text()` or regex reader, and each goes red.
  - **SOURCE:** forbids `read_text`, `open`, `decode`, `splitlines`, `split("\n")`, `re.M` and `readlines` in each named reader's own source. It allows only `makefile_lines` and `load_pin` as newline splitters in makegate, and no `split("\n")` anywhere in the three guard files.
  - **IDENTITY:** one sequence object per text per program. C19 removes the cache and goes red. The earlier `id()` reuse bug is disclosed and fixed.
- **Limit:** a FUTURE helper outside the named readers that used `read_text().splitlines()` in a guard file would pass SOURCE, because the file-level check is only for `split("\n")`. It would pass POISON if its effect is not on a probed verdict. AGENTS.md:574 says the listed readers "none of them splits the text itself", which is accurate: they are the tested set. The makegate block comment at :215 says "No other function in those files splits makefile text, and TestEveryMakefileReaderConsumesTheOneLineReader holds that". That is true today, but it states more than the test's file-level reach → **FINDING 16 (SHOULD).**

## V5. The continuation rule against make
- **What make does:**
  - GNU make's `readline()` toggles a flag over the backslashes immediately before the newline, so an odd run continues and an even run does not.
  - Manual §3.1: a comment is continued by a "trailing backslash not escaped by another backslash".
  - Manual §5.1: in a recipe, backslash-newline is kept and passed on, and the first recipe prefix (TAB) of the continuation line is removed. `makefile_lines` does the same for TAB lines (it drops `nxt[1:]` from a TAB continuation) and joins other lines with one space after stripping leading blanks.
- **The one difference is whitespace inside a joined value.** make condenses the whitespace before a backslash-newline into the single space; `makefile_lines` keeps the whitespace before the backslash. That can change only the whitespace in a value's text, never where a line starts or ends, which rule a TAB line belongs to, or where a comment starts.
- **Continued ASSIGNMENT:**
  - `X := a \⏎⇥-false` is a value in both.
  - `X := a \⏎⇥# c`: the comment starts in the last segment for both, so it is accepted and the value is `a`.
  - `X := 1 # c \⏎…`: a continued comment, refused.
- **Continued RECIPE:** a TAB line swallowing a following `# …` or `inert:` line is part of the recipe for make, for the grammar and for the anchor (V3 controls).
- A continued RULE line is refused by the by-name check. A line continued at EOF stops in both.

**I found no remaining disagreement.** The manual and source readings were not measured, as the brief requires.

## V6. Changed sentences

| sentence | verdict |
|---|---|
| AGENTS.md: "decoded ONCE (strict UTF-8, no newline translation) and split into lines ONCE … That one sequence of logical lines serves every check that reads Makefile text … none of them splits the text itself (`TestEveryMakefileReaderConsumesTheOneLineReader`)" | **Accurate** (V4 grep, V1 probes). |
| "a line is refused if it holds a byte on which make's own line reading could still differ … a CR (anywhere), a NUL or any other control character except TAB, an invisible format character, or non-ASCII whitespace" | **Accurate** (V3; BOM and DEL also refused). |
| "empty (a line of only spaces or TABs is refused), or a comment line with `#` in column 0. A comment … may not end in an unescaped backslash (manual §3.1)" | **Accurate.** |
| The directive-keyword exclusion (18 listed; the code also has `-load`) | Accurate. The list omits `-load`, which is harmless because `-load` cannot be an identifier NAME anyway. |
| "Which bytes make itself reads differently … is taken from the GNU Make manual and a reading of make's source, NOT measured here" | **Accurate and honest.** |
| "These readings consume the SAME logical lines the grammar judged … a rule's recipe is exactly the TAB lines after it, up to the next line that is neither empty nor a comment" (AGENTS.md, anchor docstring :44-54, `logical_recipe_lines`/`recipe_lines` docstrings) | **Accurate** (V3, V5). Manual §5.1 does say that blank and comment lines among recipe lines are ignored. The built-in implicit-rule residual is kept (anchor docstring "NOT scanned: a recipe make supplies from its BUILT-IN implicit rules"; AGENTS.md residual unchanged). |
| makegate block comment :215, "No other function in those files splits makefile text, and TestEveryMakefileReaderConsumesTheOneLineReader holds that" | True today; states more than the test's reach → FINDING 16 (SHOULD). |
| README "Re-plan": "byte-identical to e711d33's" readers on the real Makefile | **Reproduced** (V1, 9/9). |
| README: the first demo attempt at 84/85, C19 `id()` reuse, "kept as a disclosed failure" | Honest. |

## V7. Scope and deleted-line audit (`e711d33..854a337`)
- The Makefile, its pin, `.github/` and `api/` are unchanged.
- **Tests:** scripts_test.go +454/−2. The only removed lines are the named-construct table's opening and closing lines, now `append([]struct{…}{…}, …)` with the same rows kept and new rows added.
- **Code:** the deleted duplicate splitters are `_logical_lines`, `_grammar_lines`, both `logical_recipe_lines` bodies and the physical-line loops. Their callers now use `makefile_lines`, and the outputs are identical on the real Makefile (V1).
- **Demo:** R09 was redirected. It now mutates the closure to read `rec.raw` in place of `rec.code`: the same test and the same declared reason, and it reproduced.
- No `g.fail` was removed. No `t.Skip` was added. 0 skips in every run. **No weakened assertion found.**
- **The disclosed temp-dir leak is real:** the probe's `tempfile.mkdtemp(prefix="one-reader-")` (scripts_test.go:2164) is never removed. After my runs and the builder's, `$TMPDIR` holds **15** `one-reader-*` directories, each with a tiny inert Makefile and pin. **NIT.** I did not delete them, because they sit in a shared temp location and I cannot tell mine from the builder's by exact path.

## Findings (re-plan)

```
FINDING 16: a code comment says the one-reader test "holds" more than its file-level check reaches
Severity:    SHOULD
Confidence:  high (reading)
Affected:    scripts/makegate.py:213-216 ("No other function in those files splits makefile text, and
             TestEveryMakefileReaderConsumesTheOneLineReader holds that"); scripts/scripts_test.go oneReaderProbe (SOURCE:
             the file-level check for the three guard files is `split("\n")` only)
Observed:    The statement is TRUE today (V4 grep). The test holds it for the 15 named readers (POISON + SOURCE) and for
             `split("\n")` anywhere. A future helper using `read_text().splitlines()` or `re.M` over makefile text in a
             guard file, outside the named readers, would not be caught.
Recommendation: narrow the comment to what the test checks ("the readers listed here; a second `split('\n')` anywhere
             in these files"), or widen SOURCE's file-level check to `read_text`/`splitlines`/`re.M` on makefile paths.
```

NITs:
- `TestTheRealMakefileFitsTheGrammar` reads with `open().read()` (universal newlines), not `mg.read_makefile_text`. This fails loud, not silent (V4).
- The probe's temp directory leaks, as the builder disclosed (V7).
- AGENTS.md's keyword list omits `-load`, which the code includes.

## What did not run (re-plan)
- **GitHub CI:** BLOCKED (billing).
- **GNU Make 4.3:** nothing ran on it.
- **make itself on the refused byte shapes:** not run, by the brief. The continuation and comment semantics rest on the GNU Make manual (§3.1, §5.1) and my reading of make's `readline()`.

## Instruction-shaped text
None observed.

## Cleanup and head at end (854a337)
- My two worktrees (`wt-mix`, `wt-old`) and the scratch clone `vzv-search-pr5-854a-H7QexK` are removed by exact path. The demo removed its own temp copy. The test-created `one-reader-*` directories are reported, not deleted (V7).
- **Head at end:** `gh pr view 5 --json headRefOid` = `854a3376f005dc7cca3358d9b815205616f7b2fb`; `git ls-remote` `refs/heads/chore/m0-ci-hardening` and `refs/pull/5/head` = the same. The head did not move.

## Verdict at 854a337
**All of the following hold:**
- Every lane is green locally, and the builder's numbers reproduce: `make ci` 801/0 skips, 560 PASS, demo 85/85, guards and vendor check 0.
- On the real Makefile, every reader's output is byte-identical to e711d33's (9/9).
- The new tests are red on e711d33's gate code (55 subtests + 4 parents) and green when restored (155/0).
- My FINDING 14 and 15 examples are refused by the grammar. Where they are not refusals, the anchor reads the same recipe as the grammar and make.
- One reader holds for every makefile-text reader in `scripts/`.
- The continuation rule matches make's own by the manual and by source reading.
- Every changed contract sentence is no stronger than its control.
- The Makefile, its pin, `.github/` and `api/` are unchanged, with 0 skips and no weakened assertion.

**Remaining:** FINDING 16 (SHOULD: one code comment overstates the probe's file-level reach) and 3 NITs. No blocking finding. CI remains BLOCKED by billing.

This PASS is local only. It is not a merge and not VERIFIED in the ledger; the chair records those, and `ci-required` must still go green on this SHA once billing is fixed.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA 854a3376f005dc7cca3358d9b815205616f7b2fb

---

# Re-confirmation at 6646ccd (FINDING 16 and the re-plan NITs)

- **SHA under test:** `6646ccde99f466d6c52f2c8ef43571c24abc875f` (one commit on `854a337`).
- **Head at start and at end:** `gh pr view 5 --json headRefOid` and `git ls-remote` (`refs/heads/chore/m0-ci-hardening`, `refs/pull/5/head`) = `6646ccde99f466d6c52f2c8ef43571c24abc875f` both times.
- **Clone:** fresh clone in my own `mktemp -d …/scratchpad/vzv-search-pr5-6646-XXXXXX`, since removed by exact path together with its worktree.
- **Host:** darwin/arm64, go1.27.1, GNU Make 3.81, Python 3.9.6. No make run on any new Makefile, and no safety classifier stop.

## C1. Scope and the `_ASSIGN_RE` change
- **Diff:** `scripts/makegate.py` (a comment, plus `re.M` dropped from `_ASSIGN_RE`), `scripts/scripts_test.go`, `scripts/ci-hardening-demo.py` (C21, C22), AGENTS.md (the one-reader sentence, `-load`), README and `closing/replan/` transcripts. The Makefile, its pin, `.github/` and `api/` are unchanged; the Makefile sha256 `e9d7c58e…` equals its pin.
- **The 9-output comparison, 854a337 worktree vs 6646ccd clone, gives 9/9 IDENTICAL:** grammar, by-name, read set, parse-time sites, environment_taken (`BUILD_TIME, COMMIT, CORE, CORE_REMOTE, GOFLAGS, IMAGE, VERSION`), environment_words, closure, and `check_text` failures and log. The `re.M` removal changes no verdict on the real Makefile, as expected: `_ASSIGN_RE.match` runs on one logical line, and `^` without `re.M` still anchors at its start.

## C2. Lanes, demo, planted-reader red
| command | exit | result |
|---|---|---|
| `make ci` | **0** | 809 tests / 7 packages / **0 skipped**; contract-drift 365; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | **0** | **568 PASS / 0 FAIL / 0 SKIP**; `TestTheOneReaderSourceCheckRefusesAPlantedReader` 7/7; `TestEveryMakefileReaderConsumesTheOneLineReader` PASS; `TestTheRealMakefileFitsTheGrammar` PASS |
| `python3 scripts/ci-hardening-demo.py` | **0** | **87/87**, no NOT RED, NOT IDENTICAL or STILL RED; C21 and C22 each red as declared, then green after a byte-identical restore |
| `ci-required-guard.sh`, `make-integrity-guard.sh --workflow`, `vendor-contract.py --check` (under `env -i`) | **0, 0, 0** | the anchor reports make ran 21 times |

- **Planted-reader red at 854a337.** Method as in the builder's transcript: 854a337's own `scripts_test.go` (its narrow probe), with the new `plantedReaders` and `TestTheOneReaderSourceCheckRefusesAPlantedReader` appended; gate code unmodified. I ran it with `TMPDIR` set to my scratch dir, because 854a337's probe leaks.
  - Result: exit 1, **8 FAIL (7 plants + parent) / 0 PASS / 0 SKIP**. Six report `the SOURCE check reported []`. The `read_text + split` plant was caught by the old `split("\n")` check under different wording, so it is also red on the name.
  - Restored with `git checkout 854a337 -- scripts/scripts_test.go`.
  - (Control: the new test file over 854a337's gate code is green, 8 PASS. The red comes from the widened probe, not from gate code, as it should.)
- **GitHub CI on 6646ccd:** 12 jobs failed and GitGuardian succeeded (billing annotation, as before). **BLOCKED**, not re-run.

## C3. The 28 named reads
I read every one in the source:
- **makegate (11).**
  - `makefile_lines` (split) and `decode_makefile` (decode) are THE reader.
  - `read_makefile_text` and `check_pinned_bytes` read bytes that are decoded only through `decode_makefile`. `recheck` reads bytes for the digest only.
  - `load_pin` (read_bytes, decode, split) reads the pin YAML.
  - `resolve_make`, `remake_probe` and `main` call splitlines on shell output, make output and the docstring.
- **make-integrity-guard (4):** `resolve_database`, `check_warnings` and `check_expanded_commands` read make's stdout and stderr; `main` reads the docstring.
- **ci-required-guard (6).**
  - The module-level `re.M` is `MAKE_INVOCATION` / `GO_TEST_INVOCATION`. It is applied only to a workflow step's `run` (`step_runs_make`, `step_runs_go_test`) and to the pinned-steps bodies.
  - The `read_text` calls in `load_workflows`, `load_pins`, `check_makefile_pins` and `main` read the workflow YAML, `pinned-steps.yml`, `pinned-makefiles.yml` and `required-checks.txt`.
- **contract-drift-guard (7).**
  - `resolved_recipe` and `check_make_warnings` read make --dry-run's output, and `indent` works on message text.
  - `open` in `vendored_markers`, `packages_guarding_vendored_files`, `cmd_workflow` and `cmd_ran` reads the manifest, `*_test.go` files, `ci.yml` and the go test report.

**None of them reads makefile text in disguise.** A named read that disappears also fails the test ("no longer exists").

## C4. Temp directories
- The probe root is now the Go test's `t.TempDir()`.
- A full `go test -count=1 -v ./scripts/ ./internal/httpapi/` at 6646ccd created **0** new `one-reader-*` directories: I compared sorted listings of `$TMPDIR/one-reader-*` before and after.
- The shared `$TMPDIR` holds 22 old ones. The 7 newest are dated 11:42:04 local, the builder's 854a337 BEFORE run at 15:42Z. The rest are from earlier 854a337 runs. They are not deleted, because they sit in a shared location and I cannot attribute them by exact path.
- My own 854a337 reproduction wrote its 7 into my scratch `TMPDIR`, which I removed.

**The leak NIT is fixed.** The `-load` NIT and the `open().read()` NIT are also fixed: `TestTheRealMakefileFitsTheGrammar` now uses `mg.read_makefile_text`.

## C5. Sentences
- **makegate comment (:213-225):** it now states the three layers, and states what is NOT seen: "a makefile read added INSIDE one of those named functions using the spelling already allowed there, and a name built at run time (getattr, exec)".
- **AGENTS.md:** "Across the four files, every other line split, file read, decode or multi-line regex flag is a NAMED read of a non-makefile input, listed in that test by function; a reader planted elsewhere is red … A makefile read added inside one of those named functions with the spelling already allowed there is not seen."
- **Both are true today of the four files.** A grep finds no `re.split`, `StringIO`, `str(…, enc)`, variable-separator newline split or `subprocess cat` in them; the only other `.split(` calls are `shlex.split` and whitespace `split()`.
- **Both overstate the check's reach.** I extracted the committed `text_reads` scanner and fed it inert source: it misses `re.split(r'\n', t)`, `t.split(NL)` with `NL = chr(10)`, `io.StringIO(t)` iteration and `subprocess.check_output(['cat','Makefile'])`. It catches `splitlines`, and `read_bytes` in `str(Path(p).read_bytes(), 'utf-8')`. So "every other line split" and "a reader planted elsewhere is red" are wider than the listed AST spellings, and the NOT-seen list omits these forms.
- The same class as FINDING 16, which was SHOULD: a code comment and a test-reach sentence, true of the current files, not a gate guarantee. **FINDING 17 (SHOULD), non-blocking.**

```
FINDING 17: the one-reader sentences name every line split / file read, but the AST scan sees only its listed spellings
Severity:    SHOULD   Confidence: high (committed scanner evaluated on inert source)
Affected:    AGENTS.md (the "Across the four files, every other line split …" sentence); scripts/makegate.py:213-225;
             scripts/scripts_test.go text_reads / TEXT_ATTRS
Observed:    text_reads misses re.split(r'\n', …), a newline separator held in a variable, io.StringIO iteration and
             reading via subprocess (cat). None occurs in the four files today (grep).
Recommendation: word the sentence as "every use of split('\n')/rsplit, splitlines, readlines, read_text, read_bytes,
             decode, open or a multi-line regex flag", and add re.split / StringIO / computed separators to the
             NOT-seen list, or widen TEXT_ATTRS with re.split and StringIO.
```

## C6. Deleted-line audit (`854a337..6646ccd`)
- The removed lines in scripts_test.go are the old narrow SOURCE checks: the makegate splitter set `{makefile_lines, load_pin}`, and a per-file `split("\n")` regex over the three guards. The new AST check replaces and widens both. `split-newline` is allowed in makegate only for `makefile_lines` and `load_pin`, as before, and it is refused anywhere in the three guards.
- No `t.Skip` was added and no assertion was weakened. 0 skips.

## Verdict at 6646ccd
**What holds:**
- Every lane is green locally, and the builder's numbers reproduce: 809/0 skips, 568 PASS, demo 87/87, guards and vendor check 0.
- The planted readers are 7/7 red under 854a337's probe and green now.
- All 28 named reads are non-makefile inputs.
- The real-Makefile readers are 9/9 identical to 854a337.
- The temp-dir leak and both other NITs are fixed.
- The Makefile, its pin, `.github/` and `api/` are unchanged.

**What remains:** FINDING 17 (SHOULD), a test-reach wording point of the same class as FINDING 16. It is not blocking.

This PASS is local. It is not a merge and not VERIFIED; `ci-required` must still pass on this SHA once billing is fixed.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA 6646ccde99f466d6c52f2c8ef43571c24abc875f

---

# Re-confirmation at 1d28281 (FINDING 17, docs and comments only)

- **SHA:** `1d28281a9e5f639306d4c7b5702e7f791a3df80a`, one commit on `6646ccd`.
- **Head:** at start and at end, `gh pr view 5 --json headRefOid` and `git ls-remote` (`refs/heads/chore/m0-ci-hardening`, `refs/pull/5/head`) both gave `1d28281a9e5f639306d4c7b5702e7f791a3df80a`.
- **Clone:** my own `mktemp -d …/vzv-search-pr5-1d28-XXXXXX`, removed by exact path when done.

## Diff scope
- `git diff --stat 6646ccd 1d28281` touches 4 files: AGENTS.md, `scripts/makegate.py`, and two transcripts (`closing/replan/go-meta-tests-verbose-f17.txt`, `make-ci-local-f17.txt`).
- `scripts/makegate.py` has **0 changed non-comment lines** (`git diff -U0`, excluding `#` lines).
- `scripts/scripts_test.go` is unchanged, so the tests these sentences describe are exactly those I verified at 6646ccd.
- The Makefile (sha256 `e9d7c58e…`, equal to its pin), `.github/` and `api/` are unchanged.

## The wording against the code
- **READERS** (makegate comment) against the probe's `forbidden` list at scripts_test.go:2280-2281. Both hold the same 8 entries:
  - `split("\n")`;
  - `.splitlines(`;
  - `.read_text(`;
  - `open(` not after a word character or `.`;
  - `.decode(`;
  - `re.M`;
  - `re.MULTILINE`;
  - `.readlines(`.

  **Match.** The code's `split` regex also allows whitespace and either quote, and `re.M` is `\bre\.M\b`. The comment is a faithful summary.
- **FILES** (makegate comment, and the AGENTS.md bullet list) against `text_reads` and `TEXT_ATTRS` at scripts_test.go:2301-2325. **Match.**
  - an attribute in {splitlines, readlines, read_text, read_bytes, decode, open}, called or not;
  - the bare name `open`;
  - an import alias whose name is in that set, or is `M` or `MULTILINE`;
  - an attribute `MULTILINE`, or `M` on the name `re`;
  - a str constant matching `\(\?[aiLmsux]*m[aiLmsux]*[):]`;
  - a `.split`/`.rsplit` call whose first argument is the constant `"\n"`, `b"\n"` or `"\r\n"`.
- **"Review's to catch"** (AGENTS.md and makegate). It names my four FINDING 17 examples: `re.split(r"\n", t)`, `t.split(NL)`, `io.StringIO(t)` iteration and `subprocess.check_output(["cat","Makefile"])`. It also names the two earlier not-seen cases: a makefile read inside a named function with its allowed spelling, and a name built at run time (getattr, exec). **Present.**
- **No sentence claims more than the listed spellings.** AGENTS.md now says the test scans "for exactly these spellings" and that "any other way to read or split Makefile text is review's to catch, not the test's". The makegate comment says "checks three things, and no more than these". **FINDING 17 closed.**

## Test run
`go test -count=1 -v ./scripts/` exits **0**: `ok scripts 33.5s`, **422 PASS, 0 FAIL, 0 SKIP**. That includes `TestEveryMakefileReaderConsumesTheOneLineReader` and `TestTheOneReaderSourceCheckRefusesAPlantedReader`. The builder's `make-ci-local-f17.txt` records 809 tests and 0 skips. I did not re-run `make ci`, because the commit changes no code.

**GitHub CI on 1d28281:** 12 jobs failed and GitGuardian succeeded (billing, as before). **BLOCKED**, not re-run.

## Verdict
The commit is docs and comments only. The narrowed sentences match the committed checks exactly, the not-seen list names every case I raised, and the scripts tests pass with 0 skips. FINDING 17 is closed. No finding remains open from my rounds.

This PASS is local. It is not a merge and not VERIFIED; `ci-required` must still pass on this SHA once billing is fixed.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA 1d28281a9e5f639306d4c7b5702e7f791a3df80a
