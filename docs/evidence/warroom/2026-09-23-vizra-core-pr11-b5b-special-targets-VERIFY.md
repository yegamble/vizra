# VERIFY — vizra-core PR #11 "B5b: anchor refuses .IGNORE/.DEFAULT/.EXTRA_PREREQS and non-explicit closure recipes"

- **Verifier:** independent war-room verifier (did not write this code).
- **PR:** https://github.com/yegamble/vizra-core/pull/11, a **draft stacked on PR #10**. Base is branch `chore/m0-anchor-makefile-digest`.
- **Head verified:** `29387da9dcb4b6bd842396a5d01857f10de7a856`, one commit on `398ac4fe2bd8a6096a24e402936ef3ab2c2238bc` (PR #10's verified head). Head confirmed with `gh pr view 11` at start (end: see the last section).
- **Source:** my PR #10 round-2 findings R2-F1 (`.IGNORE`), R2-F2 (recipes outside explicit rules), R2-F3 (an over-broad AGENTS.md row), in `2026-09-23-vizra-core-pr10-makefile-digest-VERIFY.md`.
- **Clone:** new `mktemp -d …/vzv-core-pr11-XXXXXX`, fresh `git clone` + `fetch pull/11/head pull/10/head`, detached at the SHA. A second local clone sat at `398ac4f` for the C15b comparison.
- **Host:** darwin/arm64, GNU Make 3.81, Python 3.9.6, go1.27.1.
- **4.3:** my own container `vzvpr11-make43-<pid>`, `--rm`, `ubuntu:24.04`, make 4.3, PyYAML 6.0.1, with a logging `/usr/bin/make` wrapper. The image was **absent** and was pulled by this run. No container was using it afterwards, so I removed it with `docker rmi ubuntu:24.04`.
- **Method:** I ran only the builder's committed fixtures and scripts (`measure.sh`, `demo.sh`, `mutations.py`, all read before running). I authored no Makefile that disables a gate. Nothing was stopped by a classifier in this run.
- **Rebase:** **after PR #10 merges, this PR is rebased onto main, and the rebased SHA must be re-confirmed** (at least `ci-required` plus the D rows and the fixture sweep) before any merge. This verdict covers `29387da` only.

## 1. Scope

- `git diff --name-only 398ac4f..HEAD` touches only `scripts/` (guard, tests, 11 new makeguard fixtures), `docs/` (COMMANDS.md and `docs/evidence/hardening-b5/b5b/`) and `AGENTS.md`.
- No Makefile, `.github/` (pin, workflows, required-checks, pinned-steps), `api/`, `internal/`, `cmd/` or `migrations/` change. No file deleted.
- **Tests:** the only removed test lines are a two-line comment, moved and extended (it now also names `.DEFAULT_GOAL` as a control). Every existing table row is kept.
- **`missing-prerequisite`** changed from `wantText: "could not be established"` (resolver) to `notInvoked: true, wantText: "has no explicit rule in the pinned bytes"`. That is **stricter**: it is now refused before make, with 0 make starts. The resolver's failure path moved to the new `resolver-cannot-resolve` fixture, which still asserts `could not be established` after 2 make starts. Nothing lost.

## 2. `measure.sh` — the first live measurement (committed inert Makefiles, failing gate stub)

| Case | 3.81 raw `make ci` | 4.3 raw `make ci` | `-pn` db shows |
|---|---|---|---|
| clean | 2 (the gate fails) | 2 | — |
| `.IGNORE:` | **0** | **0** | `.IGNORE:` |
| `.IGNORE: ci` | **0** | **0** | `.IGNORE: ci` |
| computed `$(I)ORE:` | **0** | **0** | `.IGNORE:` |
| `.DEFAULT:` recipe; computed `.DEFAULT` | 2 | 2 | `.DEFAULT has a recipe` |
| `.EXTRA_PREREQS := Makefile` | 2 | 2 | `.EXTRA_PREREQS := Makefile` |
| phony `ci` with `%:` and `.DEFAULT` recipes | "Nothing to be done for ci" (no pattern or `.DEFAULT` recipe ran) | same | — |
| non-phony `ci`, same rules | `PATTERN-RECIPE-RAN-for-ci` | same | — |
| phony `ci: helper`, `helper` rule-less | `DEFAULT-RECIPE-RAN-for-helper` | same | — |

This confirms my R2-F1 by measurement: `.IGNORE` in every form turns a failing gate into exit 0 on both versions.

It also settles the builder's claim that make runs no pattern or `.DEFAULT` recipe for a phony target: **correct on both 3.81 and 4.3**. The last row shows why the second half of the rule is needed too: a rule-less *prerequisite* of a phony target does get the `.DEFAULT` recipe. The PR's requirement covers it, because every closure target needs an explicit rule (`missing-prerequisite`), and `.DEFAULT` is refused outright.

## 3. `demo.sh` (full on 3.81; `DEMO_ONLY=D` on 4.3)

3.81: `demo.sh` exit 0, tree clean afterwards. 4.3: `DEMO_ONLY=D` exit 0; the in-container scratch copy shows 1 path, and the host tree is clean.

| Row | 3.81 | 4.3 |
|---|---|---|
| D- fixtures `ignore-bare`, `ignore-per-target`, `default-recipe`, `extra-prereqs`, `pattern-rule`, `closure-not-phony`, `missing-prerequisite`, `submake` | each **HELD**: exit 1 in both modes, **0 make processes**, refusal names the construct; raw `make ci` exit 0 for both `.IGNORE` fixtures | identical |
| C15 (`.IGNORE` pre-make refusal removed) | both fixtures still refused after make: `.IGNORE:` is in effect (plus MAKEFLAGS `pni` for bare); 4 make processes | identical |
| **C15b** (refusal and `.IGNORE` backstop removed, i.e. the 398ac4f state) | `ignore-per-target`: **anchor exit 0, `passed`**; `ignore-bare`: still refused by MAKEFLAGS `pni` | identical (4.3 MAKEFLAGS shows `inp`) |
| C16–C21 (`.DEFAULT`, `.EXTRA_PREREQS`, pattern rule, `.PHONY` requirement, no-explicit-rule, sub-make refusals removed) | each named test red (go test exit 1), byte-identical restore, then green | (Go rows host-only) |

## 4. C15b confirmed with each PR's own anchor

Committed fixture `ignore-per-target`, copied with a failing gate stub; each tree's own `spawn-recorder.py` and anchor:

| Anchor | 3.81 | 4.3 |
|---|---|---|
| raw `make ci` | 0 | 0 |
| PR #10 @ `398ac4f`, `--workflow` / lenient | **exit 0 / 0, `passed`, 4 make processes** | **exit 0 / 0, 4 make processes** |
| PR #11 @ `29387da`, `--workflow` / lenient | **exit 1 / 1, 0 make processes**, `Makefile:8 names .IGNORE: .IGNORE: ci` | identical |

**R2-F1 is confirmed as a real hole in #10, and it is closed by #11.** The PR #10 verdict (PASS local) stands on its stated scope, but the chair should know #10 alone lets `.IGNORE: <gate>` through, so #11 should follow it closely.

## 5. All 57 makeguard fixtures, 3.81 vs 4.3

Recorder at `--workflow` on both versions, and the make wrapper on 4.3. **Exit codes and make counts are identical across versions, and recorder and wrapper agree on every fixture.**
- **55 red, 2 green** (`good`, `include-pinned-good`).
- Every text-refused fixture starts 0 make processes, including the 11 new ones except the resolver rows.
- `resolver-computed-{default,extra-prereqs,ignore}` and the older resolver rows: 4 make processes, then refused by name.
- `resolver-cannot-resolve`: 2 make processes. `make-q-parse-error`: 1.

## 6. The `.PHONY`/explicit-rule requirement against the real Makefile

- The real tree passes on both versions:
  - anchor `--workflow` and lenient exit 0 (18 make processes);
  - `ok every one of the 17 gate closure target(s) has one explicit rule and is declared .PHONY`;
  - `ok make's own .PHONY list covers all 17 gate closure target(s)`.
- The Makefile declares `.PHONY` for all 25 of its targets (lines 28-210), so nothing it needs today is rejected.
- **Design constraint (NIT, not a defect):** a future gate lane cannot depend on a real *file* target (a stamp file or a built binary). Such a target would have to be refactored as phony, or the requirement relaxed in a reviewed change. The docs imply this by stating the rule; they could say it outright.
- `ci-required-guard.sh` exits 0 on both 3.81 and 4.3; PyYAML was installed this time.

## 7. Lanes at 29387da

| Command (clean clone, 3.81 host) | Exit | Counts |
|---|---|---|
| direct unit step: `go test -race -count=1 -json ./...` + `go-test-report.py --suite unit --floors scripts/test-floors.json` | 0 / 0 | **1230 executed, 1230 pass, 0 skip** (my own JSON count `{'pass': 1230}`); `scripts` **310**; floor 943 |
| `make ci` | **0** | all 10 lanes; `internal/fixtures` 325 s, `scripts` 45 s |
| `./scripts/make-integrity-guard.sh --workflow` / lenient | 0 / 0 | |
| `./scripts/ci-required-guard.sh` | 0 | (also 0 on 4.3) |
| tree after all runs | clean | 0 porcelain entries |

**CI: BLOCKED** (billing). `gh api …/commits/29387da…/check-runs` returns 11 runs: 10 failed without starting, and GitGuardian passed. There is no `ci-required`, build-test, integration, cache-matrix, fixtures, govulncheck, docker-build, image-scan or append-only result for this SHA. Integration suites were not run locally.

EOF
## 8. Doc sentences under "no false-guarantee merges"

| Sentence | Verdict |
|---|---|
| AGENTS.md control matrix (R2-F3): "cannot turn a required lane into a no-op **through the constructs the anchor names**", followed by the full list before and after make | scoped and true. Every named construct is refused as stated (§3–§5). The row no longer claims more than the controls do. **R2-F3 closed** |
| AGENTS.md / COMMANDS.md: `.IGNORE`, `.DEFAULT` (whole word; `.DEFAULT_GOAL` harmless), `.EXTRA_PREREQS` refused before make; computed forms after make | true (§3–§5; `TestEveryRefusedSpellingIsRefusedBeforeMake` carries `.IGNORE::`, `.PHONY .IGNORE: ci`, `.DEFAULT: ; @true`, target-specific and `override +=` `.EXTRA_PREREQS`, and a `.DEFAULT_GOAL` control) |
| "GNU make skips implicit-rule search for phony targets, so every recipe the gate closure reaches is one the text reading scans" / "make reaches no implicit, pattern or `.DEFAULT` recipe through it" | true as measured on 3.81 and 4.3 (§2). It holds because it is combined with "every closure target has one explicit rule" and the `.DEFAULT` refusal, and the text says so |
| "a measured `.IGNORE:`, `.IGNORE: ci` and computed `$(I)ORE:` each made `make ci` exit 0" | reproduced (§2) |
| "The value of any other variable in the pinned bytes is not checked … review's to catch"; "not called exhaustive" | stated residuals, unchanged |
| COMMANDS.md B5b table (`make ci` 0; 1230/0; `scripts` 310; 57 fixtures, 55 red / 2 green on 4.3) | reproduced (§5, §7) |

No over-claim found.

## 9. Findings

No BLOCKER, REQUIRED or REGRESSION. R2-F1, R2-F2 and R2-F3 from the PR #10 verification are **closed**.

```
FINDING B5b-N1: the closure rule forbids file targets in any gate lane
Severity:    NIT   Confidence: high
Affected:    vizra-core scripts/make-integrity-guard.py (the closure `.PHONY`/explicit-rule requirement); docs/quality/COMMANDS.md
Observed:    every gate closure target must be `.PHONY` with one explicit rule. The real Makefile complies (all 25 targets phony).
Failure:     none today. A future lane that depends on a real file target (a stamp file, a built binary) is refused, and a maintainer may not expect that.
Recommendation: one sentence in COMMANDS.md: "gate lanes may not depend on file targets; make them phony."
Cross-repo:  search: consider the same rule when its anchor is brought level.
Challenge:   it is the intended default-deny.
```

```
FINDING B5b-N2 (for the chair): PR #10 alone passes `.IGNORE: <gate target>`
Severity:    NIT for #11 (informational); relevant to merge sequencing
Observed:    §4. #10's anchor at 398ac4f passes the committed `ignore-per-target` fixture on 3.81 and 4.3 (exit 0, `passed`), while raw `make ci` exits 0 over a failing gate.
Recommendation: merge #11 promptly after #10. Re-verify the rebased #11 SHA (ci-required once Actions runs, the D rows, the 57-fixture sweep).
```

## 10. Cleanup and head

- Scratch `vzv-core-pr11-XXXXXX` was deleted by exact path.
- The container ran with `--rm`. `ubuntu:24.04`, which this run pulled, was removed with `docker rmi ubuntu:24.04` after I confirmed no container used it.
- The builder's checkout, the core #8 worktree and vizra-search were not touched.

## Verdict

Every claim in the PR reproduced on GNU Make 3.81 and 4.3:
- the `.IGNORE`/`.DEFAULT`/`.EXTRA_PREREQS` refusals, before and after make;
- the explicit-and-phony closure rule, with make's no-implicit-search behaviour for phony targets measured on both versions;
- C15/C15b and C16–C21 red then green;
- 57 fixtures, 55 red and 2 green, identical across versions and across two observers;
- `make ci` 0, unit 1230 with 0 skips, `scripts` 310;
- the real tree green;
- stricter test expectations and scoped docs.

CI is blocked by billing. This PR is a draft stacked on #10: **after #10 merges it is rebased, and the rebased SHA needs re-confirmation before merge.**

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA 29387da9dcb4b6bd842396a5d01857f10de7a856

---

## Cross-check: inline and multi-target rules (chair's cross-repo question from search PR #5)

- **Head:** `gh pr view 11` → `29387da9dcb4b6bd842396a5d01857f10de7a856`. New scratch clone `vzv-core-pr11x-XXXXXX`, detached at the SHA.
- **Method:** in-process calls to core's committed functions on **in-memory strings**:
  - `RULE_RE`, `logical_recipe_lines`, `check_recipe`;
  - `prerequisite_closure` and `check_text`, handed a stand-in root whose `/ rel` returns an object with `read_text()`.
  - I wrote no Makefile to disk and ran no make. `subprocess.Popen`/`run` were replaced by functions that raise, and none raised.
- **Scope of what I ran:** only the two spellings the chair named, and neighbours of the same shape. Two further spellings I identified **by reading the code** were **not executed** (marked below). I kept to reading because constructing new evasion spellings is what a classifier stopped in my PR #10 round-2 work.

### Gap 1 — inline `;` recipe (`t: ; -true`, `t: ; $@x`)

The recipe-line reader is tab-keyed (`logical_recipe_lines`, scripts/make-integrity-guard.py; it collects only `\t` lines after the rule line). The definition match `^ci\s*:(?!=)` hits `ci: ; -true`, but the reader returns `[]`: **the inline recipe is not scanned**. It is also never added to `GATE_RECIPE_LINES`, so the post-make expanded-prefix check does not see it either.

What `check_text` did, pre-make, on each string (the full pre-make text reading plus the closure):

| String (after the two approved SHELL lines) | Result |
|---|---|
| control `ci:` / `\t-./run…` | refused: "recipe line prefixed `-`" |
| `ci: ; -true` | **refused**, but only because `RULE_RE` makes `;` and `-true` "prerequisites": "`;` … has no explicit rule" |
| `ci:;-true` | refused (`;-true` treated as a prerequisite) |
| `ci: ; $@x` | refused (`;` treated as a prerequisite; `$@x` is dropped as a `$`-token) |
| `ci: ; ./run… \|\| true` | refused (`;`, `./run…` and `true` treated as prerequisites) |
| a closure prerequisite `lane: ; -./run…` | refused the same way |

**Core does not have the search spellings as a hole.** Every inline form the chair named is refused before make. But the refusal is **incidental**: it comes from B5b's "every closure prerequisite needs an explicit rule" rule applied to junk tokens, with a misleading message. It is not a scan of the inline recipe.

**By reading, not executed:** `prerequisite_closure` drops every whitespace-separated token that starts with `$` (`if not d.startswith("$")`). An inline recipe whose `;` is glued to a `$`-token would therefore produce no junk prerequisite, and nothing above would fire. The unscanned inline recipe would then pass the pre-make checks. After make, the dry-run suffix check would still catch a `|| true`, but a leading `-` is invisible to `--dry-run`. **UNVERIFIED by execution** — I did not construct that spelling.

### Gap 2 — the closure target is not the first name (`bar ci-lane:`)

The definition match is anchored at the line start and needs `:` directly after the name (optional whitespace), so **any** multi-target line fails it: `bar ci:` and also `ci bar:`. `RULE_RE` in `prerequisite_closure` does split multi-target names, so the target is in the closure but has no "definition".

| String | Result |
|---|---|
| `bar ci:` + `\t-./run…` (ci a seed) | **refused**: "gate target `ci` is not defined in any makefile make will read" |
| `ci bar:` + `\t-./run…` | refused, same message (even as the FIRST name) |
| `ci: lane`, then `bar lane:` + `\t-./run…` | refused: "`lane` … has no explicit rule in the pinned bytes" |

**B5b does NOT treat `bar ci-lane:` as the explicit rule**, and its recipe is not scanned. The lane is refused outright (fail-closed), with a message that is inaccurate: the rule exists, but in multi-target form.

**By reading, not executed:** if the same closure target also has a **recipe-less** single-target line (e.g. `lane:` alone, which satisfies "one explicit rule" with an empty recipe), and the recipe sits on a multi-target line naming it:
- the recipe is not scanned before make;
- make reports no duplicate, because only one rule has a recipe;
- after make, only a `|| true` suffix would be caught (dry run); a `-` prefix would not.
**UNVERIFIED by execution** — not constructed.

### Doc sentences

- `scripts/make-integrity-guard.py:118-122`: "every target in the gate closure must have ONE explicit rule … so every recipe the closure reaches is an explicit one the text reading scans".
- AGENTS.md:165-166: "so every recipe the gate closure reaches is one the text reading scans".
- COMMANDS.md:75: "The recipe scan covers the EXPLICIT rules of the prerequisite closure".

For the spellings the chair named, the outcome is refusal, so these sentences are not falsified **by those spellings**. The code does not do what the sentences say, though: inline `;` recipes and recipes on multi-target lines are explicit rules the text reading does **not** scan. Whether the two by-reading spellings above slip through is UNVERIFIED by execution. If either does, those three sentences overclaim.

The AGENTS.md matrix row ("a literal `-`/`+` prefix … on a gate recipe line") has the same dependency.

```
FINDING X-1: core's recipe scan ignores inline `;` recipes and recipes on multi-target rule lines; the named spellings are refused only incidentally
Severity:    REQUIRED if the by-reading spellings are confirmed (the doc sentences above would then be false guarantees); SHOULD otherwise. NEW-CLASS relative to B5b
Confidence:  high for the mechanism (executed on inert strings); medium for the two by-reading spellings (not executed)
Affected:    vizra-core scripts/make-integrity-guard.py logical_recipe_lines (tab-only), check_text definition match `^%s\s*:(?!=)` (single-target only), prerequisite_closure (`$`-token filter); AGENTS.md:165-166; COMMANDS.md:75; guard docstring :118-122
Recommendation (smallest, default-deny): before make, refuse any rule line in the pinned read set that carries an inline `;` recipe, and any multi-target rule line naming a gate-closure target. Or scan both forms and give the exact message. Add one inert fixture per form (notInvoked) plus rows in TestEveryRefusedSpellingIsRefusedBeforeMake.
Acceptance:  each form refused by name, 0 make processes, on 3.81 and 4.3; the real tree unaffected. The Makefile uses neither form: every gate rule there is a single-target line with tab recipes.
Cross-repo:  search: the same two gaps as reported by its verifier.
Challenge:   today every spelling I executed is refused. The residual needs a reviewed Makefile that uses an unusual form. That is why it is not a BLOCKER.
```

- **Cleanup:** scratch clone deleted by exact path; no container used.
- **Head re-check** at the end: see the next line.

CROSS-CHECK: GAP — SHA 29387da9dcb4b6bd842396a5d01857f10de7a856 (the named spellings are refused, incidentally; the recipe scan does not cover inline or multi-target rules, and two bypass spellings found by reading are UNVERIFIED by execution)

---

# Re-verification at 5488eb0 (#11 fix round 1 of 2: X-1 plus B5c)

- **Head:** `gh pr view 11` → `5488eb0e23940a376ea333c483d9af3a71b5ba14` (draft). One commit on `29387da`.
- **Clone:** new `mktemp -d …/vzv-core-pr11r1-XXXXXX`.
- **Hosts:** 3.81 on the host. 4.3 in my own `vzvpr11r1-make43-<pid>` container (`--rm`, PyYAML, logging `/usr/bin/make` wrapper).
- **Image:** `ubuntu:24.04` was **absent** before, so this run pulled it. It was removed afterwards; no container was using it.
- **Method:** I ran only committed scripts and fixtures, which I read first. For item 2 I made in-process calls on the **committed** spelling strings from `TestEveryRefusedSpellingIsRefusedBeforeMake`. I authored nothing new. No classifier stopped anything.

## R1-a. Scope

- The Makefile and the pin are unchanged; `.github/` is untouched.
- Only `scripts/`, `docs/` and `AGENTS.md` changed. No file was deleted.
- **Tests:** the diff "removes" 45 rows of the refused-spelling table, but a row-by-row comparison of 29387da and 5488eb0 shows all 45 are present with **identical inputs and expected text**. Each only gained a `mustNot` field (nil), which the loop uses to fail a refusal given for the wrong reason. That is stricter. 12 rows were added. `scripts_test.go` only adds rows.
- **Skips:** 0, by my own count (below).

## R1-b. Builder's scripts and the 62 fixtures

- **`measure.sh`**, 3.81 and 4.3: identical to the previous round (`.IGNORE` forms exit 0 raw; the phony rows behave as documented).
- **`demo.sh`**, full on 3.81: exit 0, tree clean afterwards.
  - All 13 D rows **HELD**, including `inline-recipe`, `multi-target-rule`, `computed-prerequisite`, `posix` (0 make processes) and `computed-target-recipe`. On that last fixture raw `make ci` exits 0 on 3.81 **and 4.3**, and the anchor refuses after make: "make's own database gives gate closure target `ci` the recipe line `-./run-the-real-tests.sh`".
  - C15/C15b and C16–C26 each go BROKEN or red, restore byte-identical, then HELD or green.
- **`DEMO_ONLY=D` on 4.3:** exit 0; the same D rows and C15, C15b and C22–C26 outcomes.
- **62 makeguard fixtures:** 60 red, 2 green. Exit codes and make counts are **identical on 3.81 and 4.3**, and the recorder and wrapper agree on every one.
  - 0 make processes for every text-refused fixture.
  - 4 for `computed-target-recipe` and the resolver rows.
  - 2 for `resolver-cannot-resolve`; 1 for `make-q-parse-error`.

## R1-c. X-1: the two by-reading spellings, in-process on committed strings

Method as in the cross-check: `prerequisite_closure` and `check_text` over an in-memory `good` Makefile plus the committed row text, with `subprocess.Popen`/`run` made to raise (none did).

| Committed row | Pre-make result (0 make processes) |
|---|---|
| `inline recipe glued to a computed token`: `EMPTY :=` / `ci: $(EMPTY); -./run-the-real-tests.sh` | **refused by name**: "is a rule with an INLINE `;` recipe", plus "prerequisite make COMPUTES: $(EMPTY)" |
| `multi-target recipe beside a recipe-less rule`: `lane:` + `other lane:` / `\t-./run…` | **refused by name**: "is a MULTI-TARGET rule (other, lane)" |
| `inline recipe on the gate target`, `multi-target rule naming a closure target`, `grouped targets` (`a b &:`), `static pattern, two targets` | each refused by name |
| control (nothing added) | not refused |

(The in-process base, like the Go test's, already defines `ci`, so "defined 2 times" also fires on rows that add a `ci:` line. The committed test's `wantText` pins the specific message, so that collateral refusal cannot mask a regression.)

**Both by-reading spellings are now refused by name before make.** The X-1 items from the cross-check are closed.

## R1-d. C23: is the multi-target refusal adequately tested?

- The demo's C23 row uses fixture `multi-target-rule` (`ci other:`). With the refusal removed it is still refused before make, as "not defined", because that fixture has no other `ci` rule.
- **A spelling where "not defined" would not fire exists:** `lane:` (recipe-less, which satisfies "one explicit rule") plus `other lane:` carrying the recipe. The committed row `multi-target recipe beside a recipe-less rule` covers exactly that.
- With `mutations.py C23` applied (through `mutate.sh`; byte-identical restore) and the Go tests run, these go **red**:
  - `TestEveryRefusedSpellingIsRefusedBeforeMake/{multi-target rule naming a closure target, multi-target rule, gate target first, multi-target recipe beside a recipe-less rule, grouped targets, static pattern, two targets}`;
  - `TestMakeIntegrityGuardFixtures/multi-target-rule`.
  - `grouped targets` and `static pattern` even report "exit 0, want 1" under C23.
- **Adequately tested.** Without C23's refusal, the recipe-less-beside spelling would be caught only after make, by the database scan.

## R1-e. The post-make database recipe scan (`check_db_recipes`)

- **It scans the TEXT closure, not make's closure.** `check_db_recipes(g, closure)` iterates the closure computed by `prerequisite_closure` from literal prerequisites. It reads no prerequisites from make's database.
- **It is not fail-closed.** Called in-process:
  - `DB_RECIPES={}` with `closure=['ci']` → **failed=False**, "the 0 recipe line(s) of the 1 gate closure target(s) carry no …";
  - `{'ci': []}` → failed=False.
  - `_db_recipe_lines` uses `DB_RECIPES.get(t, [])`, so a closure target the parser did not capture is silently treated as recipe-less.
  - The parser (in `resolve_database`) keeps only the **first** occurrence of a name (`… if name not in recipes else None`) and skips names containing a space. A later occurrence's recipe is dropped without a failure.
- **By reading, not executed:**
  - A rule whose target NAME make computes is still accepted before make. Only its *recipe* for a closure target is caught after make.
  - Such a rule can instead add a *prerequisite* to a closure target (a recipe-less `$(NAME): extra`, per GNU Make's multiple-rules semantics). make's closure would then include `extra`, but the text closure, the database scan and the `.PHONY` checks would all cover only the text closure, so `extra`'s recipe would go unscanned.
  - I did not construct or run this spelling.
- On the real Makefile the parser works: it attributes 62 recipe lines to all 17 closure targets on 3.81 and 4.3.

## R1-f. Real Makefile

The anchor passes on 3.81 and 4.3, in both modes, with `ci-required-guard` exit 0:
- "every one of the 17 gate closure target(s) has one explicit rule and is declared .PHONY";
- "make's own database: the 62 recipe line(s) of the 17 gate closure target(s) carry no `-`/`+` prefix …";
- "make's own .PHONY list covers all 17".

Nothing the Makefile uses is refused: every rule there is a single-target line with TAB recipes, with no inline `;`, no multi-target line, no `$`-prerequisite and no `.POSIX`. COMMANDS.md now states "No gate lane may depend on a real file target", which closes my earlier NIT B5b-N1.

## R1-g. Lanes at 5488eb0 (3.81 host, clean clone)

| Command | Exit | Counts |
|---|---|---|
| direct unit step + `go-test-report.py` | 0 / 0 | **1247 executed, 1247 pass, 0 skip** (my own JSON count `{'pass': 1247}`); `scripts` **327** |
| `make ci` | 0 | all 10 lanes |
| both anchors / `ci-required-guard.sh` | 0 / 0 / 0 | |
| tree afterwards | clean | 0 porcelain entries |

**CI: BLOCKED** (billing); nothing is recorded for this SHA, and the integration suites were not run.

## R1-h. Doc sentences under "no false-guarantee merges"

- **Guard docstring :118-129:** "every recipe the closure reaches … is then scanned twice: before make … and after make … the recipe of every closure target AS MAKE'S `-pn` DATABASE HOLDS IT, which catches a recipe make attached some other way (a rule whose target name make computes)".
- **COMMANDS.md:** "So every recipe the closure reaches is scanned … After make, every closure target's recipe as make's `-pn` database holds it is held to the same literal checks, which catches a recipe make attaches some other way (a rule whose target name make computes)".
- **AGENTS.md:165-172:** same wording.

**Verdict on the sentences:**
- The *before-make* half is true as measured (R1-b, R1-c).
- The *after-make* half overclaims in two ways:
  1. "the recipe of every closure target as make's database holds it": a closure target the database parser does not capture passes with 0 lines (R1-e, executed). The scan is not fail-closed.
  2. "catches a recipe make attaches some other way (a rule whose target name make computes)": it catches such a recipe only when attached to a text-closure target. A computed-name rule that adds a prerequisite widens make's closure beyond the text closure, and nothing scans the added target's recipe (R1-e, by reading; not executed).

## R1-i. Findings

```
FINDING R1-1: the post-make database recipe scan is not fail-closed and covers only the text closure, while three authored sentences say it scans "every closure target's recipe as make's database holds it"
Severity:    REQUIRED (a false-guarantee sentence authored in this round). NEW-CLASS relative to X-1 (the backstop introduced this round)
Confidence:  high for fail-open on a missing or shadowed entry (executed in-process); medium for the computed-prerequisite widening (by reading plus GNU Make's documented multiple-rules semantics; not executed)
Affected:    vizra-core scripts/make-integrity-guard.py check_db_recipes / _db_recipe_lines (`DB_RECIPES.get(t, [])`), the recipe parser in resolve_database (first occurrence only; names with spaces skipped), main() (`check_db_recipes(g, closure)` with the text closure); check_text (no pre-make refusal of a rule line whose target name contains `$`); guard docstring :118-129, COMMANDS.md, AGENTS.md:165-172
Recommendation (smallest, default-deny):
  (a) before make, refuse any rule line whose TARGET contains `$`, as B5c already does for prerequisites. That removes the computed-name route at the source, and `computed-target-recipe` becomes a pre-make refusal;
  (b) in check_db_recipes, FAIL for any closure target with no database entry, and fail on a duplicate entry rather than keeping the first;
  (c) optionally, compute the closure from the database's own prerequisite lists and require it to equal the text closure;
  (d) or narrow the three sentences to what the scan does.
Acceptance:  in-process `DB_RECIPES={}` with closure ['ci'] → failed=True; a committed inert fixture with a computed target name refused before make with 0 make processes on 3.81 and 4.3; the real tree green.
Tests:       one TestEveryRefusedSpellingIsRefusedBeforeMake row for a `$`-named rule target; a unit test of check_db_recipes on an empty and a duplicated database.
Cross-repo:  search: if it adopts the database scan, the same requirements.
Challenge:   reaching this needs reviewed bytes with a computed target name. (a) is a one-line default-deny consistent with every other B5 refusal, and the sentences can be made true cheaply.
```

```
FINDING R1-2 (NIT): 3.81 reports 66 distinct expanded-prefix lines on the real tree, 4.3 reports 62; both pass. Informational only (the text and database line sets are deduplicated differently).
```

## R1-j. Cleanup and head

- Scratch `vzv-core-pr11r1-XXXXXX` deleted by exact path.
- The container ran with `--rm`, and the pulled `ubuntu:24.04` was removed.
- The builder's checkout, the core #8 worktree and vizra-search were not touched.

## Verdict (round 1 of 2)

X-1 is closed and reproduced on 3.81 and 4.3:
- inline and multi-target rules, `$`-prerequisites and `.POSIX` are refused before make with 0 make processes, including both of my by-reading spellings;
- C22–C26 go red, then green;
- 62 fixtures identical across versions;
- no weakened test; 0 skips; `make ci` 0; unit 1247; `scripts` 327.

One REQUIRED finding blocks under "no false-guarantee merges": R1-1. The new post-make backstop, which this round's docs describe as scanning every closure recipe as make holds it, passes a closure target it did not parse, and covers only the text closure. A one-line pre-make refusal of `$`-named rule targets, plus a fail-closed database lookup, would make the sentences true.

FINAL VERDICT: FAIL — SHA 5488eb0e23940a376ea333c483d9af3a71b5ba14

---

# Re-verification at 0243f2e (#11 fix round 2 of 2, the last: R1-1)

- **Head:** `gh pr view 11` → `0243f2ebf4b97d047acf8e3967924a8dd5c5d748` (draft). One commit on `5488eb0`.
- **Clone:** new `mktemp -d …/vzv-core-pr11r2-XXXXXX`.
- **Hosts:** 3.81 on the host. 4.3 in my own `vzvpr11r2-make43-<pid>` container (`--rm`, PyYAML, logging `/usr/bin/make` wrapper).
- **Image:** `ubuntu:24.04` was **absent** before, so this run pulled it. It was removed afterwards; no container was using it.
- **Method:** committed scripts and fixtures only, all read first, plus in-process calls on inert strings with process creation made to raise. I authored no Makefile. The only make runs on non-fixture bytes were the anchor's own runs on the real pinned Makefile, and one `make -pn Makefile ci` on it to read the database headers. No classifier stopped anything.

## R2-a. Scope

- Makefile and pin unchanged (`e7cc357c…`); nothing under `.github/`.
- Only `scripts/`, `docs/` and `AGENTS.md` changed.
- One file was deleted: `docs/evidence/hardening-b5/b5b/make-4.3-ubuntu24.04/C26.txt`. The C26 row is now a Go-test row, so it is not produced by the 4.3 `DEMO_ONLY=D` run; the 3.81 transcript is updated. Consistent, not a loss.
- **Fixture moves:** `computed-target-recipe` and `resolver-computed-{ignore,default,secondexpansion}` now carry `notInvoked: true` with the text "is a rule whose TARGET make computes". **Stricter** (0 make processes). The post-make branches they used to exercise keep red cases as in-process rows in `db-scan-probe.py`: `.IGNORE` in effect, `.DEFAULT` has a recipe, `.SECONDEXPANSION` in effect, and the database recipe/closure rows. `TestTheDatabaseChecksFailClosed` runs them, and C26/C28–C32 go red without them.
- **Real-tree assertions:** "carry no …" is replaced by "each of the 17 … has ONE readable entry whose 62 recipe line(s) equal the pinned rule's", and "the gate closure make reports … equals the text closure (17 target(s))" is added. Stricter.
- 4 new refused-spelling rows for computed rule targets: recipe, prerequisite-only, `${G}::`, target-specific.
- **No test line weakened; 0 skips** (below).

## R2-b. Builder's scripts, probe and fixtures

| Item | 3.81 | 4.3 |
|---|---|---|
| `measure.sh` | exit 0, as before | as before |
| `db-scan-probe.py` | **PROBE: all 15 rows as expected** | same |
| `demo.sh` (full) / `DEMO_ONLY=D` | exit 0, tree clean; 13 D rows HELD + probe; C15–C32 red or BROKEN, byte-identical restore, then green or HELD (C28–C32 show 1–2 `ROW BAD` each under mutation, then "all 15") | exit 0; D rows, C15/C15b, C22–C25, C27–C32 identical |
| 62 makeguard fixtures | 60 red / 2 green | **identical to 3.81**, recorder = wrapper on every one |

- `computed-target-recipe` and the three moved `resolver-computed-*` fixtures: 0 make processes, "is a rule whose TARGET make computes".
- `resolver-computed-{shell,makeflags,recipeprefix,extra-prereqs}`: 4 make processes, refused by the resolver.

## R2-c. My round-1 fail-open calls, re-run in-process (item 2)

| Call | Result |
|---|---|
| empty database (no entry for `ci`) | **refused**: "make's database has NO entry for gate closure target `ci`" |
| empty `ci` entry, while the text shows a recipe | **refused**: "make holds a DIFFERENT recipe for gate closure target `ci` … 0 line(s)" |
| empty `ci` entry, and no recipe in the text either | not refused. Correct: a recipe-less aggregate like the real `ci` |
| duplicate `ci` entry | **refused**: "MORE THAN ONE entry" |
| a spaced (unreadable) header recorded | **refused**: "cannot read as ONE name" |

The probe also refuses "no `# Make data base` section". Its control shows `-n` command output before the database (3.81) is not read as a target.

## R2-d. Closure equality (item 3)

- **Real databases:** on 3.81 and 4.3 the real `-pn` database prints `ci: fmt-check vet lint-imports … test-race` between the `# Make data base` and `# Finished Make data base` markers. `parse_database` reads it into `DB_PREREQS`, and the anchor reports "the gate closure make reports from its database equals the text closure (17 target(s))" on both versions.
- **Order-only:** the reader replaces `|` with a space, so order-only prerequisites are included. By code: the real Makefile has none, and no committed fixture feeds real make output with one (NIT R2-3).
- **Double-colon:** each `name::` rule prints as its own entry, so a closure target with two is refused as "MORE THAN ONE entry". Only the first entry's prerequisites feed the closure walk, but the target is refused anyway.
- **`.PHONY`:** read as a separate `.PHONY:` entry and into `__PHONY__`; never reached from the seeds.
- **Could equality pass while make's real closure differs?** The ways make reaches a target without listing it as a prerequisite are each refused or inapplicable:
  - `.EXTRA_PREREQS`, refused before and after make;
  - `.DEFAULT` and implicit or pattern rules: `.DEFAULT` refused, pattern rules refused, and phony targets skip implicit search (measured);
  - `.SECONDEXPANSION` and `$(MAKE)`, refused;
  - computed rule targets and `$`-prerequisites, refused before make.
- I found no path; none was constructed.

## R2-e. Recipe equality with whitespace collapsed (item 4)

`_norm(line) = " ".join(line.split())`. In-process, against a text line `./run-the-real-tests.sh`:

| Database line | Result |
|---|---|
| `-./run…` | refused (DIFFERENT, and the `-` prefix check) |
| `+./run…` | refused (DIFFERENT, and the `+` prefix check) |
| `@./run…` | refused (DIFFERENT) |
| `./run… \|\| true` | refused (DIFFERENT, and the suffix check) |
| `  ./run…  ` | equal (whitespace only) |

Prefix characters are never collapsed away. Collapsing could only equate lines that differ in runs of whitespace, e.g. inside a quoted string. That cannot change a `-`/`+` prefix, a suffix or `$(MAKE)`, and each of those is checked on make's line independently. Not a material equivalence.

## R2-f. Real Makefile and lanes (3.81 host, clean clone; 4.3 in the container)

| Command | Exit | Counts |
|---|---|---|
| direct unit step + `go-test-report.py` | 0 / 0 | **1252 executed, 1252 pass, 0 skip** (my own JSON count); `scripts` **332**; `TestTheDatabaseChecksFailClosed` present and passed |
| `make ci` | 0 | all 10 lanes |
| anchors `--workflow` / lenient; `ci-required-guard` | 0 / 0 / 0 on 3.81 and on 4.3 | "each of the 17 gate closure target(s) has ONE readable entry whose 62 recipe line(s) equal the pinned rule's"; closure equality ok; **62 distinct expanded-prefix lines on 3.81** (R1-2 closed) |
| tree afterwards | clean | 0 porcelain entries |

Nothing the real Makefile needs is refused.

**CI: BLOCKED** (billing); no result for this SHA, and the integration suites were not run.

## R2-g. Doc sentences under "no false-guarantee merges"

- **The new claim**, in AGENTS.md, COMMANDS.md and the guard docstring :118-141: "With (i)–(iii) [closure equality, one readable entry, recipe equal to the pinned TAB lines and the same literal checks], every recipe of every target in make's own closure is one the text reading scanned."
  - (i)–(iii) are implemented as described and fail closed (R2-b to R2-e).
  - The only qualifier is "whitespace collapsed", which COMMANDS.md states.
  - The residual mechanisms by which make could run a recipe outside its listed prerequisites are each refused (R2-d).
  - **I find the claim true** for what it states. It is scoped by the anchor's named constructs and the stated review residuals ("the value of any other variable … review's to catch"; TOCTOU; the pin is only as good as review).
- The before-make sentences, including "a rule whose TARGET make computes is refused before make too": true (the 4 spelling rows and the 4 moved fixtures).
- The "66 on 3.81, 62 on 4.3; both now read 62" note: reproduced (62 on both).

## R2-h. Findings

```
FINDING R2-1: the guard's docstring now contains an invalid escape sequence — a SyntaxWarning on every anchor run under Python 3.12 (the CI runner's python3), and a SyntaxError under -W error
Severity:    SHOULD (introduced in this round; one-character fix). Not a guarantee issue.
Confidence:  high (executed)
Affected:    vizra-core scripts/make-integrity-guard.py:139 (blame 0243f2e): "four `\`-continued recipe lines" inside the non-raw module docstring
Observed:    4.3 container (python 3.12.3): `make-integrity-guard.py:2: SyntaxWarning: invalid escape sequence '\`'` printed by db-scan-probe and the anchor. `python3 -W error::DeprecationWarning -W error::SyntaxWarning` compile of 0243f2e → "SyntaxError: invalid escape sequence \`"; 5488eb0 compiles clean.
Failure:     stderr noise on every anchor run in CI. CPython has announced invalid escapes will eventually become SyntaxErrors, and then the anchor would not start (fail-closed, every make lane red).
Recommendation: write `\\`` (as line 1292 already does) or make the docstring raw.
Acceptance:  `python3 -W error::SyntaxWarning -c 'compile(open("scripts/make-integrity-guard.py").read(),"g","exec")'` exits 0.
Cross-repo:  none.  Challenge: harmless today.
```

```
FINDING R2-2 (NIT): an unreadable pinned file or a database-less make run is reported by name, but a closure target that is legitimately recipe-less in BOTH the text and the database passes. That is correct (aggregates such as `ci`); recorded so the chair knows it was checked.
FINDING R2-3 (NIT): no committed fixture feeds real make output with an order-only prerequisite or a double-colon closure target through parse_database. Both paths are right by code (R2-d), but only the synthetic probe covers the database reader. A fixture per form, run through the anchor, would pin it on 3.81 and 4.3.
```

No BLOCKER, no REQUIRED, no REGRESSION of any earlier row. R1-1 and R1-2 are **closed**.

## R2-i. Cleanup and head

- Scratch `vzv-core-pr11r2-XXXXXX` was deleted by exact path.
- The container ran with `--rm`, and the pulled `ubuntu:24.04` was removed after I confirmed no container used it.
- The builder's checkout, the core #8 worktree and vizra-search were not touched.
- Head re-checked at the end: see below.

## Verdict (#11 round 2 of 2)

R1-1 is fixed and reproduced on GNU Make 3.81 and 4.3:
- computed rule targets are refused before make;
- the database scan fails closed on missing, duplicate, unreadable and differing entries;
- make's closure must equal the text closure;
- C26–C32 go red, then green;
- the probe gives 15 of 15;
- 62 fixtures, identical across versions and two observers;
- fixture moves are stricter; no weakened test; 0 skips;
- `make ci` 0; unit 1252; `scripts` 332; the real tree green on both versions.

The new "every recipe of every target in make's own closure" claim holds for everything I could test and read. One SHOULD finding remains (R2-1, a one-character docstring escape).

**This PR is a draft stacked on #10. After #10 merges and #11 is rebased, the rebased SHA must be re-confirmed** (at least the fixture sweep, the probe and `ci-required` once Actions runs) before merge.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA 0243f2ebf4b97d047acf8e3967924a8dd5c5d748
