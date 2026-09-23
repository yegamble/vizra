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
