# VERIFY — vizra-core PR #10 "hardening B5: the anchor never runs make on unreviewed Makefile bytes"

- **Verifier:** independent war-room verifier (did not write this code). Written incrementally.
- **PR:** https://github.com/yegamble/vizra-core/pull/10 — branch `chore/m0-anchor-makefile-digest`
- **Head verified:** `62d16aa773a2db4414bc2f96b3381c732e2ebf88` (confirmed `gh pr view` headRefOid at start). Merge base `eeeea068a20118f7af721f024264603b436a1528` = `origin/main`.
- **Clone:** fresh `git clone` + `git fetch origin pull/10/head` + detached checkout, under my own `mktemp -d` (`…/scratchpad/vzv-core-pr10-7gRiCT/repo`). The builder's checkout and the core #8 worktree were not touched.
- **Host:** Darwin arm64, GNU Make 3.81 (`/usr/bin/make`), Python 3.9.6 + PyYAML 6.0.3, go1.26.2 (see lanes for toolchain), Docker 29.8.0. Disk 18 GiB free.
- **CI:** BLOCKED by billing (chair). Verdict can at best be `PASS (local; CI BLOCKED)`.
- **Method constraint:** byte mutations and ordinary file-system changes only; no exploit payload built.

## 0. Frozen paths

`git diff --name-only origin/main...HEAD | grep -E '^(Makefile|api/|internal/|cmd/|migrations/|\.github/required-checks.txt|\.github/pinned-steps.yml|scripts/test-floors.json|\.github/workflows)'` → no output, exit 1. The PR does not touch the Makefile, `api/`, `internal/`, `cmd/`, `migrations/`, `.github/required-checks.txt`, `.github/pinned-steps.yml`, `scripts/test-floors.json`, or any workflow. FLOOR_LANES lives in `.github/required-checks.txt` and the workflows, which are unchanged.

Pin: `.github/pinned-makefiles.yml` → `Makefile: e7cc357cd09a6fc78e006d4f55a396e425dd574ea5cc7888b740513b18778fb2`; `shasum -a 256 Makefile` at the head → the same digest. The pin matches.

## 1. The builder's driver, re-run by me (GNU Make 3.81, host)

`cd <clone> && bash docs/evidence/hardening-b5/demo.sh ../demo-out` → exit 0; `tree after all demonstrations: 0 uncommitted path(s)`. (The driver's own `go version` inside the repo reports go1.27.1 via the go.mod toolchain.)

| ID | Reproduced by me | Observation |
|---|---|---|
| D0 | yes | anchor `--workflow` and lenient exit 0, 19 processes, 18 make, first argv `['make','-q','Makefile']`; ci-required-guard exit 0, check 11 ok |
| D1 | yes | sha `e7cc357c…`→`78e6e7d2…`; anchor exit 1 both modes, **0 make processes**; ci-required-guard exit 1 "Makefile changed without the paired update"; restore byte-identical; green after |
| D2 | yes | sha →`fcc7ad63…`; same as D1 |
| D3 | yes | fixture `include-pinned-good`, a.mk sha `8f77c0a5…`→`11b88465…`; exit 1 both modes, 0 make; restore identical; control 6 make processes |
| D4 | yes | pin entry deleted → "pins no file", 0 make, ci-required-guard exit 1 |
| D5 | yes | raw `make -pn ci` rewrote a 3-line Makefile (`Makefile unchanged: NO`); `make -q Makefile` exit 1, unchanged; anchor exit 1 both modes, 1 make process (`make -q Makefile`), Makefile byte-identical |
| C1 | yes | `TestMakefileDigestMutations` (3 subtests) + `TestMakeIntegrityGuardFixtures/digest-mismatch` red, go test exit 1; green after restore |
| C2 | yes | `TestAFailedEnvironmentCheckStopsTheAnchorBeforeMake` 6 subtests red (BASH_ENV, MAKEFLAGS=-i/-ki, MAKEFILES×2, GO=true); green after |
| C3 / C3b | yes | `TestTheAnchorsSubprocessesCannotSeeTheRunnerCommandFiles` red, exit 1; green after C3 restore |
| C4 | yes | `TestAMakefileMakeWouldRemakeIsRefusedWithoutRunningARecipe` red, exit 1; green after |
| C5 | yes | `TestCIRequiredGuardMakefilePin/stale` red; green after |
| C6 | yes | `include-unpinned` + 2 `TestMakefileDigestMutations` subtests red; green after |

Every builder demonstration reproduces. They do not cover the case in §2.

## 2. NEW: the `make -q` probe itself remakes and parses an unpinned included makefile (3.81)

The anchor probes **one pinned file per make process** (`make -q Makefile`, then `make -q a.mk`, then `make -q b.mk`; `check_no_pinned_makefile_would_be_remade`, scripts/make-integrity-guard.py:647-648). GNU Make honours `-q`/`-n`/`-t` in the makefile-remake phase **only for makefiles that are also command-line goals**. For every other makefile it clears those flags and really runs the remake recipe. The builder's own comment at :624-631 says so. So in `make -q Makefile`, the pinned include `a.mk` is not a goal and gets remade for real.

Reproduction: byte and file changes only. The sibling is a copy of a.mk with one value changed.
```
cp -R scripts/testdata/makeguard/include-pinned-good X1 && cd X1
{ cat a.mk; echo '# sibling copy, one comment longer'; } > a.mk.sh
touch -t 202001010000 a.mk
PATH=<observer-bin>:$PATH python3 <clone>/scripts/testdata/spawn-recorder.py rec.json --root $PWD --targets ci --workflow
```
- anchor exit **1**, but only from the post-make re-hash: `FAIL a.mk CHANGED while this guard ran make (sha256 8f77c0a5… -> b7792d4b…)`.
- Before that it printed **`ok `make -q` (no recipe run) reports none of Makefile, a.mk, b.mk would be remade`** and `ok make's own MAKEFILE_LIST … is exactly the pinned set`. Both are false.
- Recorder argv: `make -q Makefile`, `make -q a.mk`, `make -q b.mk`, `make -pn Makefile a.mk b.mk ci` ×2, `make --dry-run … ci`. That is **6 make processes; from the first one onward, make read the unpinned a.mk bytes.**
- Independent observer (PATH-first `cat`/`chmod` wrappers that log, then exec the real tool; the anchor keeps PATH): `argv=a.mk.sh` and `chmod argv=a+x a.mk`. make's builtin `%: %.sh` recipe ran.
- Isolating the first probe (fresh copy; sibling `A_VALUE := from-unpinned-sibling`): `make -q Makefile` → prints `cat a.mk.sh >a.mk` and `chmod a+x a.mk`, **exit 0**. `make -p -q Makefile | grep A_VALUE` → `A_VALUE := from-unpinned-sibling`. So the probe process, run with exactly the anchor's argv, ran a recipe, re-executed, **evaluated unpinned bytes**, and reported "up to date".
- Control for the fix: `make -q Makefile a.mk b.mk`, one process naming every pinned file as a goal, gives exit 1 and a.mk unchanged.

Consequence: in any tree whose pin lists more than `Makefile` (a supported shape, exercised by D3 and fixture `include-pinned-good`), a newer sibling of an included makefile makes the anchor evaluate unreviewed bytes **during the anchor step**. That is the class B5 exists to close. The anchor fails in the end, but only after make ran six times on those bytes. Any parse-time construct in them runs, and the PR itself says the scrub "hides variable names but not the directory". Today's core pin lists only `Makefile`, so the current tree is not affected. The PR's claims "make's first invocation … `make -q`, which runs no recipe" and "the anchor never runs make on unreviewed Makefile bytes" are false as written for the include shape the PR documents and tests.

### 2a. Same result on GNU Make 4.3 (my own `ubuntu:24.04` container)

Container `vzvpr10b5-make43-<pid>`, `--rm`. The tree was mounted read-only and copied inside. `ubuntu:24.04` was ABSENT before I pulled it and was removed afterwards with `docker rmi ubuntu:24.04`; no container was using it. make 4.3, python 3.12.3. **Independent observer:** `/usr/bin/make` was replaced by a logging wrapper that execs `/usr/bin/make.real`. The anchor accepts it because it checks location and name, not content, as its own ok line says. The PATH-first tool wrappers were present too.

X1 on 4.3: anchor exit 1 via `a.mk CHANGED` only. The wrapper log shows 6 make starts: `-q Makefile`, `-q a.mk`, `-q b.mk`, `-pn Makefile a.mk b.mk ci` ×2, `--dry-run … ci`. The observer shows `argv=a.mk.sh` and `chmod a+x a.mk`. The anchor printed the false `ok make -q (no recipe run) reports none … would be remade`. First probe alone: `make -q Makefile` exit 0, and its db holds `A_VALUE := from-unpinned-sibling`. `make -q Makefile a.mk b.mk` exits 1 with a.mk unchanged. **The same on 3.81 and 4.3.**

## 3. My own byte and file mutations on the real tree

Each row was run with the recorder (in-process, subprocess.Popen) **and** an independent observer: on 3.81 the PATH-first wrappers for `cat chmod cc gcc co get yacc lex bison flex`; on 4.3 those plus the `/usr/bin/make` logging wrapper. Makefile mtime was set older for the sibling rows. The tree was reset between rows (`git checkout -- . && git clean -fdx && touch Makefile`, then asserted clean with the pinned digest).

| Row | 3.81 anchor (wf / lenient) | 4.3 anchor (wf / lenient) | make processes (recorder; 4.3 wrapper) | tools run (observer) | Makefile after |
|---|---|---|---|---|---|
| clean | 0 / 0 | 0 / 0 | 18; 18 | none | unchanged |
| trailing `\n` appended | 1 / 1 `sha256 ad40b602… does not match` | 1 / 1 | **0; 0** | none | (mutated) |
| CRLF | 1 / 1 `sha256 86211e22…` | 1 / 1 | **0; 0** | none | (mutated) |
| touch Makefile, future mtime | 0 / 0 | — | 18 | none | unchanged |
| Makefile mtime old, no sibling | 0 / 0 | — | 18 | none | unchanged |
| newer `Makefile.sh` | 1 / 1 `make would REMAKE Makefile` | 1 / 1 | 1 (`make -q Makefile`); 1 | none | unchanged |
| newer `Makefile.o` | 1 / 1 | 1 / 1 | 1; 1 | none | unchanged |
| newer `Makefile.c` | 1 / 1 | 1 / 1 | 1; 1 | none | unchanged |
| newer `Makefile,v` | 0 / 0 | 0 / 0 | 18; 18 | none | unchanged |
| newer `RCS/Makefile,v` | 0 / 0 | 0 / 0 | 18; 18 | none | unchanged |
| newer `SCCS/s.Makefile` | 1 / 1 | 1 / 1 | 1; 1 | none | unchanged |
| newer `Makefile.y` | 1 / 1 | 1 / 1 | 1; 1 | none | unchanged |
| newer `Makefile.l` | 1 / 1 | 1 / 1 | 1; 1 | none | unchanged |

Raw GNU Make 3.81 in a 3-line scratch Makefile, for comparison (observer on): `make -pn ci` really ran `cat` (`.sh`, Makefile rewritten), `cc Makefile.o -o Makefile` (**Makefile destroyed**), `cc Makefile.c`, `get SCCS/s.Makefile`, `get s.Makefile`, `yacc`, `lex`, `cc Makefile.s/.S`. `make -q Makefile` ran none of them (exit 1). `Makefile,v`, `RCS/Makefile,v` and `Makefile.texinfo` gave `-q` exit 0, raw nothing run, Makefile unchanged: the builtin `CHECKOUT,v` is `+$(if $(wildcard $@),,…)` and the Makefile exists. So the anchor passing those two rows is correct.

**Conclusion for the root Makefile:** the probe `make -q Makefile` is sound on both versions for every sibling I tried. It refuses before any other make runs, runs no tool, and leaves the Makefile byte-identical. The hole is only for pinned makefiles that are not a goal of the probe (§2).

## 4. Does `make -q` itself run a recipe?

Scratch Makefiles; `Makefile` older than `dep.txt`. These bytes would have to be pinned, meaning reviewed.

| Case | 3.81 `make -q Makefile` | 4.3 `make -q Makefile` |
|---|---|---|
| P1 `Makefile: dep.txt` / `\t+touch plus-line-ran` | **ran it** (file created), exit 1 | **ran it**, **exit 0** |
| P2 `Makefile: dep.txt` / `\techo $(MAKE) >/dev/null; touch make-line-ran` | **ran it**, exit 1 | **ran it**, **exit 0** |
| P3 `.PHONY: Makefile` + `Makefile:` recipe | not run, exit 1 (anchor would refuse) | not run, exit 1 |

So `-q` does run `+` and `$(MAKE)` lines, as GNU Make documents. On 4.3 it then reports "up to date", so the anchor proceeds. On 3.81 it reports exit 1, so the anchor refuses, but only after the line ran. The anchor's text checks, which refuse `+` and `$(MAKE)`, run only after `make -pn`, so the probe runs before them. Reachable only through pinned (reviewed) bytes, so this is a truthfulness defect, not a bypass. It contradicts "`make -q`, which runs no recipe" (PR body, AGENTS.md, the docstring at scripts/make-integrity-guard.py:636, and the ok line "(no recipe run)").

The probe covers the later invocations only because they name the pinned files as goals: `make -pn Makefile ci`, `make --dry-run Makefile ci`. For those, a non-goal makefile cannot exist, since every pinned file is a goal. The `-q` probe is the one invocation that does not name them all (§2).

## 5. The pre-make stop (environment failures)

4.3 container, wrapper-counted, clean tree: `BASH_ENV=/dev/null`, `MAKEFILES=extra.mk` and `ENV=/dev/null`, each in `--workflow` and lenient mode, exit 1 with **0 wrapper-observed make starts** and "make was NOT invoked (0 make process(es) started)". C2 (§1) shows that narrowing the gate turns `TestAFailedEnvironmentCheckStopsTheAnchorBeforeMake` red. The claim is reproduced.

## 6. Pin shape, GNUmakefile/makefile, symlink, TOCTOU (3.81 host, recorder + observer)

| Row | anchor (wf / lenient) | make processes | ci-required-guard (check 11) |
|---|---|---|---|
| pin duplicate key (`Makefile:` twice) | 1 / 1 `'Makefile' is pinned twice` | 0 | exit 1 `not valid YAML: duplicate key` |
| pin upper-case hex | 1 / 1 `not a … 64 lowercase hex sha256 entry` | 0 | exit 1 `not in its one accepted shape` |
| `GNUmakefile` beside (copy of Makefile) | 1 / 1 `GNUmakefile exists beside the Makefile` | 0 | **exit 0**, check 11 ok |
| Makefile → symlink to identical bytes | 1 / 1 `not a regular file` | 0 | **exit 0**, check 11 ok |
| lower-case `makefile` beside | not testable on this case-insensitive APFS (`cp` reports "identical"). Code path: the same exact-name `os.listdir` loop as GNUmakefile (scripts/make-integrity-guard.py:493-496) | — | — |
| reviewed shape: `include a.mk`, Makefile and a.mk re-pinned | 0 / 0 | 19 | exit 0, "pins 2 makefile(s)" |
| same + newer `a.mk.sh` (§2 on the REAL tree) | **1 (only from `a.mk CHANGED`) after 19 make processes** / 1 (digest) | 19 | — |

**Check 11 parity (chair's question): NOT matched.** `ci-required-guard.py` `check_makefile_pin` does not refuse a `GNUmakefile`/`makefile` beside the Makefile, and it accepts a symlinked Makefile (`path.is_file()` follows links). It also does not check stale entries or include coverage. In both rows above, ci-required-guard exits 0 while the anchor refuses. Its docstring scopes check 11 to "exists, shape, non-empty, pins Makefile, matches", so it is not untruthful. But the runtime anchor is the only thing that catches these, and every make lane fails through it.

**TOCTOU:** the window is real. `check_makefile_pin` does `os.lstat`, then `read_bytes()` (which follows links), and hashes. make opens the path by name up to 18 times later. `recheck_pinned_bytes` re-reads by name without re-`lstat`. Deterministic simulation (my own harness `toctou.py`, which wraps `run_make` in-process, swaps the fixture Makefile to pinned bytes plus 2 lines around each make call, and restores it): anchor **exit 0**, `passed … only on the pinned bytes of Makefile`, with the swapped bytes present during 4 of 4 make calls. This needs a concurrent process on the runner. It is **stated as a review-only residual** in AGENTS.md:207-210 ("the digest is taken at one moment … the re-check after make narrows, not closes, that window") and in the guard docstring :147-150.

## 7. Inventory of every place core starts make (coordinator addition)

`grep` over `*.go *.py *.sh *.yml Makefile Dockerfile`, excluding docs/ and testdata:

| Site | Starts make? | Behind the digest gate + `clean_env`? | Before an anchor? |
|---|---|---|---|
| `.github/workflows/build-test.yml` `make tidy-check`, `make ci`, `make build`, `make test-integration`, `make test-integration-shuffle` | yes | each step is immediately preceded by `./scripts/make-integrity-guard.sh --workflow` (:206/209, :215/217, :255/258, :448/451, :461/463), which is enforced by ci-required-guard checks 8b/8c | no |
| `fixtures.yml` `make fixtures`, `make fixtures-verify` | yes | anchor at :119, :131 | no |
| `govulncheck.yml` `make govulncheck` | yes | anchor at :50 | no |
| `ci-required.yml`, `docker-build.yml`, `image-scan.yml`, `Dockerfile` | **no make** | n/a | n/a |
| `scripts/make-integrity-guard.py` `run_make` | yes | yes, only after the gate at :1332; `clean_env` | it is the anchor |
| `scripts/make-integrity-guard.py` `check_make_resolves_to_a_real_program` | bash only (`type -t make; command -v make`), not make | `clean_env`; runs **before** the digest gate | — |
| `scripts/ci-required-guard.py`, `go-test-report.py`, other `scripts/*.py` | **no subprocess at all** (only make-integrity-guard.py imports subprocess) | n/a | n/a |
| `scripts/*.sh` | no make invocation | n/a | n/a |
| Go tests: `scripts/scripts_test.go:17,46,445`, `makefiledigest_test.go:91,548` | indirectly: they run the guard (python), which runs make only through `run_make` behind its gate. No Go file calls `exec.Command("make", …)` | yes | in the direct unit-suite step, where there is no workflow anchor, the guard is its own gate. Fixture makefiles are gated by their own committed fixture pins, which a PR can update along with them. That is the same "review is the control" posture as test code, which runs arbitrary code in that step anyway |
| Makefile `$(MAKE)`, `+` recipe lines | none in the Makefile | — | — |

Result: no make read outside the anchor's gate in a required lane. No doc sentence claims "the anchor refuses to invoke make at all" as a repository-wide property. AGENTS.md, the README and COMMANDS scope it to the anchor.

## 8. Truthfulness: AGENTS.md, docstrings, README, COMMANDS, PR body

| Claim (where) | Observed | Verdict |
|---|---|---|
| "make's first invocation is `make -q <each pinned makefile>`, which runs no recipe" (AGENTS.md B5 bullet 3; guard docstring :75-77; `check_no_pinned_makefile_would_be_remade` docstring :636; ok line "(no recipe run)"; README; PR body §2) | §2: the per-file probe really runs the builtin remake recipe for any pinned makefile it does not name. §4: `-q` runs `+`/`$(MAKE)` lines | **false** |
| "never lets make read or remake a file that is not pinned" (COMMANDS.md guarantee row) | §2/§6: make read the remade a.mk 6 times (fixture) or 19 times (real tree with a pinned include) | **false** for any pin with more than one file |
| "the anchor never runs make on unreviewed Makefile bytes" (PR title) | true for today's one-file pin (§3, both versions); false for the pinned-include shape the PR supports and tests | **false as a general statement** |
| "What make will read is determined without running any makefile" (AGENTS.md, docstring :65-66) | true of the static listing, which is computed from the pinned text before make. It does not model make's builtin remake rules; the PR hands that job to the `-q` probe and says so | true, narrowly |
| "Any failed pre-flight now stops the anchor before make" | §5 and C2: 0 make starts under BASH_ENV/ENV/MAKEFILES on 4.3 (wrapper) and 3.81 (recorder) | true |
| `clean_env` for every subprocess | code :307-326; `run_make` and the `bash -c type` call both pass `env=clean_env()`; C3/C3b red/green | true |
| residual "digest taken at one moment" / TOCTOU is review-only | AGENTS.md:207-210, docstring :147-150; §6 simulation | true, and stated |
| residual "reviewer approves a malicious Makefile together with its pin; CODEOWNERS advisory" | stated in AGENTS.md, README, COMMANDS, pin-file header, both docstrings | stated |
| "a Makefile … that overrides SHELL … fails the lane BY NAME before make is ever invoked" (guard docstring :89-91, **pre-existing** on main:65) | fixture `shell-override` (pinned): 4 make processes before the refusal | false, pre-existing (NIT) |
| Cross-PR: "Whichever of #8 and this PR merges second must update `.github/pinned-makefiles.yml`" (PR body § Cross-PR) | present, with `shasum -a 256 Makefile` | confirmed |
| Unit 1149 / 0 skipped, scripts 229, both guards 0, `make ci` 0 | see §10 | see §10 |
| "The same class probably applies to vizra-search's anchor" (PR body) | §9: it does, and there the anchor passes | confirmed, and worse there |

## 9. Cross-repo (report only): vizra-search PR #5 at `c3b2021`

Read-only: `git -C …/vizra-search fetch -q`, then `git show c3b2021:scripts/make-integrity-guard.py`. `git archive c3b2021` was extracted into my own scratch directory; search's working tree was not touched.
- **Sibling-remake class: present, and the anchor passes.** Search's first make call is `make -pn <target>` (:339), with the Makefile not a goal. There is no `-q` probe and no re-hash after make. In my copy, with a newer `Makefile.sh` (a copy of the Makefile plus one comment) and the Makefile mtime set older: `./scripts/make-integrity-guard.sh --workflow` → **exit 0, `passed (9 gate target(s))`**, having printed `ok make runs only on reviewed bytes`. The Makefile was **rewritten** (sha `128b0f87…` → `64c36a81…`), and my PATH-first observer logged `cat Makefile.sh` and `chmod a+x Makefile`. The next `make` step would then read the rewritten, unpinned bytes.
- **Environment failure does not stop make:** in search's `main()` (:955-980), `check_environment` runs, but only a digest failure returns early. With `BASH_ENV=/dev/null`, my in-process recorder counted exit 1 with **19 make processes**. That is the pre-B5 core behaviour.
- Search's digest check (:282-316) refuses unpinned `GNUmakefile`/`makefile` by exact name. `read_bytes()` follows a symlinked Makefile, and I saw no refusal for one (read only, not run).

## 11. Findings

```
FINDING 1: the `make -q` remake probe runs one make per pinned file, so it really remakes, and make then evaluates, any OTHER pinned makefile from an unpinned sibling
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/make-integrity-guard.py:635-661 (check_no_pinned_makefile_would_be_remade: `for rel in files: run_make(root, ["-q", rel])`), :1341, :1390; AGENTS.md (B5 bullet 3); docs/quality/COMMANDS.md (guarantee row); README.md
  requirements: none yet — 2d-B5 / desk-review FINDING 4 (chair ruling tick 132: "MAKEFILE_LIST exactly the pinned set", checked BEFORE make)

Observed:
  GNU Make applies -q/-n/-t in the makefile-remake phase only to makefiles that are command-line goals; for every other makefile it clears them and runs the remake recipe for real. The comment at :624-631 states this rule. The probe names ONE pinned file per process. Fixture include-pinned-good plus a newer sibling `a.mk.sh` (a copy of a.mk with one extra comment line) and a.mk's mtime set older:
    - `make -q Makefile` (the anchor's exact first argv) ran `cat a.mk.sh >a.mk` and `chmod a+x a.mk`, re-executed, EXIT 0; `make -p -q Makefile` shows `A_VALUE := from-unpinned-sibling` in make's db. Same on GNU Make 3.81 (host) and 4.3 (ubuntu:24.04 container).
    - Anchor --workflow: printed `ok make -q (no recipe run) reports none of Makefile, a.mk, b.mk would be remade` and `ok make's own MAKEFILE_LIST … is exactly the pinned set`, then ran 6 make processes on the rewritten a.mk (recorder AND a /usr/bin/make logging wrapper on 4.3; a PATH-first `cat` observer). It exited 1 only from the post-make re-hash `a.mk CHANGED`.
    - The same on the REAL tree with a reviewed `include a.mk`, both files re-pinned: 19 make processes on the rewritten bytes before exit 1.
    - One invocation naming every pinned file (`make -q Makefile a.mk b.mk`) exits 1 and leaves a.mk unchanged, on 3.81 and 4.3.

Failure:
  For any pin with more than one file (the shape the PR documents, tests with D3 and ships as fixture include-pinned-good), adding an unreviewed sibling of an included makefile (no makefile line, no pin change) makes the anchor evaluate unreviewed bytes DURING the anchor step, 6-19 times, before it fails. Any parse-time construct in those bytes runs then, and the scrub hides only the command-file variable names, not the directory (PR's own residual). This is exactly the class B5 was opened to close. The anchor's ok line and four docs say the opposite. Today's core pin lists only `Makefile`, so main-after-merge is not exposed until the first include lands.

Perspective:
  operator, developer

Recommendation:
  Probe once, naming every pinned makefile as a goal: `run_make(root, ["-q", *files])`. On non-zero, refuse without further make. Keep the post-make re-hash. Correct the ok line and docs accordingly.

Acceptance criteria:
  With fixture include-pinned-good plus a newer `a.mk.sh`: the anchor exits 1 in both modes, the recorder shows exactly one make process (`make -q Makefile a.mk b.mk`), the observer shows no `cat`, a.mk is byte-identical afterwards, and no ok line claims the probe passed. Same on 3.81 and 4.3. The clean tree and include-pinned-good stay green.

Tests:
  scripts/makefiledigest_test.go: extend TestAMakefileMakeWouldRemakeIsRefusedWithoutRunningARecipe with an "included makefile's sibling" case (copy of include-pinned-good, newer a.mk.sh), asserting exit 1, one make argv containing every pinned file, and a.mk unchanged. Code mutation: restoring the per-file loop must turn it red.

Cross-repo implications:
  core: this PR | user: none | search: same class, worse (FINDING 5) | meta: none

Challenge:
  Today's only pinned file is the Makefile, which IS the probe's goal, so nothing on this tree is exploitable, and the post-make re-hash does fail the lane. Counter: the control's whole purpose is that unreviewed bytes are never evaluated, not that the lane fails afterwards. The PR explicitly supports and tests pinned includes, and the fix is one line.
```

```
FINDING 2: "`make -q` … runs no recipe" is false — `+` and `$(MAKE)` lines run under -q, and on 4.3 make then reports up-to-date
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/make-integrity-guard.py:75-76, :636, :656, :660 (ok line "(no recipe run)"); AGENTS.md B5 bullet 3; README.md; PR body §2
  requirements: none yet

Observed:
  Scratch Makefile with `Makefile: dep.txt` and recipe `+touch plus-line-ran` (P1), or `echo $(MAKE) …; touch make-line-ran` (P2): `make -q Makefile` created the file on BOTH 3.81 (exit 1) and 4.3 (exit 0). A .PHONY Makefile (P3) ran nothing, exit 1. The anchor's text checks that refuse `+`/`$(MAKE)` run only after `make -pn`, i.e. after the probe.

Failure:
  The statement overclaims. It is reachable only through pinned (reviewed) bytes, so this is not a bypass of the digest. But on 4.3 such a rule passes the probe as "up to date" after running.

Perspective:
  developer

Recommendation:
  Reword to "-q runs no ordinary recipe; `+`/`$(MAKE)` lines in the pinned bytes still run". Optionally refuse, before the probe, a pinned-file rule whose target is a pinned makefile.

Acceptance criteria:
  No doc or ok line says -q runs no recipe without that qualification.

Tests:
  none needed for wording. An optional fixture: a pinned Makefile with a `+` rule for itself, refused with 0 make processes.

Cross-repo implications:
  core: this PR | user: none | search: n/a (no probe) | meta: none

Challenge:
  Pinned bytes are reviewed, and a reviewer would see a `Makefile:` rule. Hence SHOULD.
```

```
FINDING 3: ci-required-guard check 11 does not match the anchor: it accepts a GNUmakefile/makefile beside the Makefile and a symlinked Makefile
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py check_makefile_pin (`path.is_file()` follows links; no default-name or stale-entry check)
  requirements: none yet

Observed:
  `cp Makefile GNUmakefile` → anchor exit 1 (0 make), ci-required-guard exit 0 "check 11 ok". Makefile replaced by a symlink to identical bytes → anchor exit 1, ci-required-guard exit 0.

Failure:
  The static required check reports green on a tree every anchor refuses. The lanes still fail through the anchor, so this is fail-closed. But ci-guard/ci-required does not name the cause, and the chair asked for parity (search's check 11 had the same gap).

Perspective:
  developer

Recommendation:
  Reuse the anchor's rules in check 11: exact-name refusal of GNUmakefile/makefile, `os.lstat` + S_ISREG, and stale entries.

Acceptance criteria:
  makefilepin fixtures `gnumakefile-present` and `makefile-symlink` → ci-required-guard exit 1 by name.

Tests:
  TestCIRequiredGuardMakefilePin: two new rows. The orphan test forces them to be named.

Cross-repo implications:
  core: this PR | search: same gap reported earlier | user/meta: none

Challenge:
  The anchor is the runtime control and already refuses, so check 11 is a duplicate early warning by design.
```

```
FINDING 4 (pre-existing, NIT): the guard docstring says a SHELL/.SHELLFLAGS/MAKEFLAGS override "fails the lane BY NAME before make is ever invoked"
Severity:    NIT
Confidence:  high
Affected:    vizra-core scripts/make-integrity-guard.py:89-91 (same text at origin/main:65)
Observed:    fixture shell-override (pinned): recorder shows 4 make processes (`-q Makefile`, `-pn Makefile ci` ×2, `--dry-run … ci`) before the three FAIL lines. check_text runs after resolve_database.
Failure:     overclaim next to the B5 text that was rewritten "to state the guarantee exactly". Pinned bytes only.
Recommendation: "fails the lane by name (make runs only on the pinned bytes first)".
Acceptance criteria / Tests: wording only.
Cross-repo implications: none.
Challenge:   not introduced by this PR.
```

```
FINDING 5 (cross-repo, for the chair; report only): vizra-search PR #5 at c3b2021 passes its anchor while make rewrites the Makefile from a sibling, and an environment failure does not stop make
Severity:    BLOCKER (search)
Confidence:  high
Affected:    vizra-search scripts/make-integrity-guard.py@c3b2021 :339 (first make is `make -pn <target>`, Makefile not a goal), :955-1039 (no -q probe, no post-make re-hash; only a digest failure returns before make)
Observed:    in my own `git archive` copy: newer `Makefile.sh` plus an older Makefile mtime → `--workflow` exit 0 `passed (9 gate target(s))`, Makefile sha 128b0f87… → 64c36a81…, observer logged `cat Makefile.sh` and `chmod a+x Makefile`. `BASH_ENV=/dev/null` → exit 1 but 19 make processes (in-process recorder).
Failure:     the anchor passes and the next make step reads unreviewed bytes; the pre-make stop is missing.
Recommendation: port core's pre-make gate on any failure, a single `make -q <all pinned>` probe (FINDING 1's corrected form), and the post-make re-hash.
Cross-repo implications: search only.
Challenge:   none from reading; demonstrated.
```

## 10. Local lanes at 62d16aa (host darwin/arm64, GNU Make 3.81, go1.27.1 via go.mod toolchain, heavily loaded by other agents' concurrent integration/fixtures runs)

| Command (clean clone) | Exit | Counts / notes |
|---|---|---|
| direct unit step: `go test -race -count=1 -json ./... > unit-events.json; python3 scripts/go-test-report.py --events … --suite unit --floors scripts/test-floors.json --go-exit-file …` | 0 / report 0 | **1149 executed, 1149 pass, 0 fail, 0 skipped** (my own count from the JSON: `{'pass': 1149}`, no skip events), floor 943, 14 packages ok, 8 `[no test files]`; `scripts` 229 (floor 161). `internal/fixtures` took **484 s** of go test's default 600 s |
| `make ci` | **2** | every lane before `test-race` passed (fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify). `test-race`: `internal/fixtures` **`panic: test timed out after 10m0s`** in `TestManifestDetectsEveryClassOfDrift`; every other package ok |
| `make test-race` (re-run once) | **2** | same timeout, same test (6m28s in it), others ok |
| `./scripts/make-integrity-guard.sh --workflow` | 0 | `passed (8 gate target(s); make ran 18 time(s), only on the pinned bytes of Makefile)` |
| `./scripts/make-integrity-guard.sh` (lenient) | 0 | same |
| `./scripts/ci-required-guard.sh` | 0 | `passed (6 required check(s))`; check 11 ok |
| `go test -race -count=1 ./scripts/` | 0 | ok |
| fixture-orphan: `mkdir scripts/testdata/makeguard/zz-orphan` then `go test -run TestEveryMakeGuardAndPinFixtureIsExercised ./scripts/` | 1, then 0 after removal | red: "zz-orphan is a fixture TestMakeIntegrityGuardFixtures does not name" |

The `make ci` timeout is in `internal/fixtures`, which this PR does not touch (§0). In the direct run the same package passed at 484 s against a 600 s limit, while other agents' `fixtures.test` and `integration.test` processes were running on the host (seen in `ps`). I judge it environmental, not caused by this diff. It is still recorded as **`make ci` NOT green locally for me**, and that lane is UNVERIFIED on this host. The builder's `make ci` exit 0 could not be reproduced here.

No test weakened: the `scripts/scripts_test.go` diff only adds cases, a field and assertions. `scripts/testdata` has only added files (`git diff --diff-filter=DM` empty). 0 skips.

### Evidence that would normally come from CI (all ABSENT on this SHA)
`gh api …/commits/62d16aa…/check-runs`: 11 runs, and every Actions job concluded `failure` in 3 s with the annotation "The job was not started because recent account payments have failed or your spending limit needs to be increased". Only GitGuardian passed. Combined status is `pending`, 0 statuses. So none of these exist: `ci-required` green on this SHA; required-checks manifest vs the jobs that actually ran; `build-test` (the anchor on ubuntu-24.04 with GNU Make 4.3 in an `actions/checkout` tree, `make ci`, the direct unit/integration suites with counts, `make build`); the integration suites (`-tags=integration`, PostgreSQL/RESP, never run locally for this slice); `cache-matrix` legs; `fixtures` (amd64 acceptance platform); `govulncheck`; `docker-build`; `image-scan`; `append-only`. Also not measured anywhere: whether `actions/checkout` ordering ever makes a committed sibling newer than the Makefile.

## 12. Cleanup

The scratch dir `vzv-core-pr10-7gRiCT` was deleted by exact path. The `ubuntu:24.04` image I pulled was removed; the container ran with `--rm`. The builder's checkout, the core #8 worktree, vizra-search's working tree (fetch only) and other agents' containers (`vzv11-*`) were not touched. At the end, `ubuntu:24.04` was present again. It was pulled by someone else after my `rmi`, and I left it alone. vizra-search's working tree shows 14 porcelain entries; I did not write any of them, since I only ran `fetch`, `show` and `archive` there. The PR head was re-checked at the end: still `62d16aa773a2db4414bc2f96b3381c732e2ebf88`.

## Verdict

**FAIL.** Every builder demonstration (D0–D5, C1–C6) reproduced. The root-Makefile controls hold on 3.81 and 4.3 under every byte and sibling mutation I tried, and the pre-make stop is real. But FINDING 1 (BLOCKER) shows that the B5 remake probe itself makes make remake and evaluate an unpinned included makefile, 6 times on the fixture and 19 on the real tree with a pinned include, while printing an ok line saying it did not. That contradicts the slice's headline guarantee for a shape the PR supports and tests. Also: `make ci` was not green locally (environmental timeout in untouched `internal/fixtures`), and CI is BLOCKED. The builder can reproduce with §2 (fixture `include-pinned-good` + `{ cat a.mk; echo '# x'; } > a.mk.sh; touch -t 202001010000 a.mk`) and fix with a single `make -q <all pinned files>` probe.

FINAL VERDICT: FAIL — SHA 62d16aa773a2db4414bc2f96b3381c732e2ebf88

---

# Re-verification at 08a59a9 (round 1 of 2)

- **Head:** `gh pr view 10` at start → `08a59a91a6dcc91c2346bcb206d4c0ad8603e90e`. It is one commit on `62d16aa`: "fix(ci): B5 fix round 1 — one make -q naming every pinned makefile; check 11 shares the anchor's reader; text checks before make".
- **Clone:** new `mktemp -d …/vzv-core-pr10r1-XXXXXX`, fresh `git clone` + `fetch pull/10/head`, detached at the SHA, with a second local clone for my mutations. `HEAD:scripts` tree = `70d09e55…`, the same scripts tree object the builder's transcripts name (their `# tree: a656144` header is a pre-squash commit with identical `scripts/` bytes).
- **Host:** darwin/arm64, GNU Make 3.81, Python 3.9.6, go1.27.1 (go.mod toolchain), heavily loaded by other agents. **4.3:** my own `ubuntu:24.04` containers `vzvpr10r1-make43-<pid>` and `vzvpr10r1-rp43-<pid>`, `--rm`, with a logging `/usr/bin/make` wrapper. The image was already present and in use by another agent's container (`searchci-r2-40c87c`), so I did **not** remove it.

## R1-0. Scope of the diff

- `git diff --name-only origin/main...HEAD` outside `scripts/`, `docs/` and `.github/pinned-makefiles.yml`: only `AGENTS.md` and `README.md`, both documentation, as in the original PR.
- Frozen-path grep (Makefile, api/, internal/, cmd/, migrations/, required-checks.txt, pinned-steps.yml, test-floors.json, workflows): no output, exit 1.
- `.github/pinned-makefiles.yml` changed in its comment header only; the digest is still `e7cc357c…` and equals `shasum -a 256 Makefile`.
- No file deleted in the round (`--diff-filter=D` empty).

## R1-1. The builder's driver

`bash docs/evidence/hardening-b5/demo.sh ../demo-out` → **exit 0**, 0 uncommitted paths afterwards. Every row reproduced:
- D0: 18 make processes, first argv `make -q Makefile`.
- D1, D2, D4: anchor exit 1 in both modes, **0 make**; ci-required-guard exit 1 by name; restore byte-identical.
- D3: a.mk byte change → 0 make; the control's first argv is `make -q Makefile a.mk b.mk`.
- D5: one `make -q Makefile`, Makefile byte-identical.
- **D6** (include sibling): exactly one make, `make -q Makefile a.mk b.mk`, a.mk unchanged.
- C1–C6, **C7** (per-file probe restored): the anchor goes back to 6 make processes and `a.mk CHANGED`; restored, it is one process. **C8** (check-11 parity dropped) and **C9** (text checks moved after make): each named test red with go test exit 1, green after restore.
- **P1:** the 5 new makefilepin fixtures are exit 0 under the 62d16aa check 11 and exit 1 now.

## R1-2. F1 — my own reproducers (fixture `include-pinned-good`; recorder + PATH-first `cat/chmod/cc/get/…` observer; on 4.3 also the make wrapper)

| Case | 3.81 (wf / lenient) | 4.3 (wf / lenient) | make processes | observer | makefiles after |
|---|---|---|---|---|---|
| control | 0 / 0 | 0 / 0 | 4: `-q Makefile a.mk b.mk`, `-pn … ci` ×2, `--dry-run … ci` | none | unchanged |
| newer `a.mk.sh` | 1 / 1 | 1 / 1 | **1**: `make -q Makefile a.mk b.mk` | none | unchanged |
| newer `b.mk.sh` (the `sinclude`) | 1 / 1 | 1 / 1 (the probe exits 2 on 4.3; still refused) | 1 | none | unchanged |
| newer **`Makefile.sh` while includes are pinned** | 1 / 1 | 1 / 1 | 1 | none | unchanged |
| newer `a.mk.sh` **and** `b.mk.sh` together | 1 / 1 | 1 / 1 | 1 | none | unchanged |
| newer `a.mk.c` | 1 / 1 | 1 / 1 | 1 | none | unchanged |
| newer `SCCS/s.b.mk` | 1 / 1 | — | 1 | none | unchanged |
| real tree, clean | 0 / 0 | 0 / 0 | 18 (host); 4 on 4.3 with `--targets ci` | none | unchanged |
| real tree, newer `Makefile.sh` | 1 / 1 | 1 / 1 | 1 | none | unchanged |

**F1 is closed** on both versions: make starts once, as the single probe, runs no tool, and nothing is rewritten. My original round-0 reproducer (§2) now gives exit 1 with one make process.

## R1-3. F4 — the text checks before make, and whether the fixtures got stricter

Recorder over all 32 `scripts/testdata/makeguard/*` fixtures at `--workflow`:
- Every failing fixture has **0 make processes** except `missing-prerequisite`, which has 2: `make -q`, then `make -pn ci` fails. That is by design.
- `good` and `include-pinned-good` have 4 make processes, exit 0.

`scripts/scripts_test.go` diff: the 16 text-check fixtures keep their `wantText` and **add** `notInvoked: true`, which asserts "make was NOT invoked (0 make process(es) started)". That is strictly stronger.

`missing-target` changed text from `could not be established` (resolver) to `is not defined in any makefile make will read` and gained `notInvoked`. Coverage the resolver path had is kept by the new `missing-prerequisite` fixture: its target is defined but make cannot resolve it, and it asserts `could not be established`.
- Loss check: the resolver's own failure path (`make -pn` non-zero) is still exercised.
- `check_resolved`/`check_warnings` still run on every passing tree after make.
- No fixture isolates `check_resolved`'s SHELL/.SHELLFLAGS/MAKEFLAGS failure branch. None did at 62d16aa either: the old `shell-override` text "shell" matched the text check first. So this is not a regression, but that defence-in-depth layer is untested (see R1-F2).

`makefiledigest_test.go`:
- The forbidden-spawn list now covers `makefile_pin.py` too, plus a regex that forbids it importing `subprocess`.
- The remake test is table-driven: the Makefile case plus an included-makefile case. Each asserts exactly one make argv equal to `make -q <every pinned file>` and every pinned file byte-identical. Stronger than before.
- The 5 new check-11 rows are `wantFail`.

**No assertion was weakened.**

## R1-4. `makefile_pin.verify_pin` through BOTH callers (anchor via recorder; `ci-required-guard.py --makefile-pins <copy>`)

The base is fixture include-pinned-good. Every row fails closed, with the anchor starting 0 make processes:

| Pin / tree mutation | anchor | check 11 |
|---|---|---|
| missing pin | 1 `does not exist` | 1 `is missing` |
| header-only / zero-byte | 1 `pins no file` | 1 `pins no file` |
| no header; flow mapping; CRLF; `---` second document; indented `  # note`; quoted key; tab indent; `./a.mk` key; `../x.mk` key | 1 (shape/header) | 1 `not in its one accepted shape` |
| duplicate key | 1 `'b.mk' is pinned twice` | 1 |
| pin is a directory | 1 `cannot be read: Is a directory` | 1 (labelled "not in its one accepted shape", a misleading label, NIT) |
| pin not UTF-8 | 1 | 1 |
| no `Makefile` entry | 1 | 1 |
| extra pinned file, present but not included (stale) | 1 | 1 |
| extra pinned file, absent | 1 `does not exist` | 1 `changed without the paired update` |
| pinned file is a directory; `GNUmakefile` beside; symlinked Makefile | 1 | 1 |
| pinned include unreadable (`chmod 000`) | **exit 1 via an uncaught `PermissionError` traceback**, 0 make | **exit 1 via a traceback** |
| extra **unpinned** file beside, not included | 0 | 0 (correct: make does not read it) |

Code read: `verify_pin` returns `ok` only when `problems` is empty. Every early exit (pin error, no Makefile) appends a problem. An unreadable pinned file raises rather than being skipped. `stale` is added only when there is no other problem, which cannot turn a failure into ok. **No path returns ok on a pin it could not fully read.** The only rough edge is the traceback: fail-closed, but not a by-name message (R1-F3, NIT).

## R1-5. Lanes at 08a59a9 (clean clone; host load average fell from about 180 to about 17 during the run)

| Command | Exit | Counts |
|---|---|---|
| direct unit step: `go test -race -count=1 -json ./...` + `go-test-report.py --suite unit --floors scripts/test-floors.json` | 0 / 0 | **1157 executed, 1157 pass, 0 fail, 0 skipped** (my own JSON count `{'pass': 1157}`), floor 943, 14 packages ok, 8 no-test-files; `scripts` **237** (floor 161), `internal/fixtures` 42 |
| `./scripts/make-integrity-guard.sh --workflow` / lenient | 0 / 0 | `passed (8 gate target(s); make ran 18 time(s), only on the pinned bytes of Makefile)` |
| `./scripts/ci-required-guard.sh` | 0 | `passed (6 required check(s))`, check 11 ok |
| **`make ci`** | **0** | all 10 lanes; `test-race` 14 ok (internal/fixtures 221.9 s, scripts 31.6 s), 0 FAIL. The round-0 timeout did not recur at lower load |
| tree after all runs | clean | 0 porcelain entries |

On the 4.3 container I did not install PyYAML, so `ci-required-guard` exited 2 inside it. That is my own environment's missing input, not the product's; check 11 is make-version independent and passed on the host. The anchor (stdlib only) ran fully on 4.3.

**CI evidence (all ABSENT):** `gh api …/commits/08a59a9…/check-runs` gives 11 runs: 10 failed ("The job was not started because recent account payments have failed…") and GitGuardian passed. No `ci-required`, build-test, integration, cache-matrix, fixtures (amd64), govulncheck, docker-build, image-scan or append-only result exists for this SHA, and the manifest-vs-jobs comparison is impossible. Integration suites were not run locally.

## R1-6. Doc sentences, under "no false-guarantee merges"

| Sentence | Verdict |
|---|---|
| "ONE `make -q` naming every pinned makefile … -q applies in make's remake phase only to goals" (AGENTS.md, README, COMMANDS, docstring, pin header) | true (R1-2) |
| "-q runs no ORDINARY recipe; a `+`/`$(MAKE)` line still runs … can come only from the pinned, reviewed bytes (builtin RCS/SCCS checkout is a `+` line that expands to nothing for an existing file)" | true. Re-measured on 4.3 with the one-invocation form: a pinned `a.mk: dep.txt` + `+touch` rule runs under `make -q Makefile a.mk` and exits 0. The docs say exactly this |
| "check 11 … calls the anchor's own `verify_pin`, so it refuses whatever the anchor refuses before make" | true for everything `verify_pin` decides (R1-4, P1). It does not run the anchor's pre-make TEXT checks or environment checks; the sentences name the list (GNUmakefile, symlink, stale/missing entry, computed include) and do not claim those. Acceptable |
| COMMANDS guarantee row: "make reads only the pinned files and remakes none of them except through a `+`/`$(MAKE)` line in the pinned bytes"; swap window stated as the review-only residual | true as measured |
| Docstring :94-100 "text checks … before make is ever invoked … a value only make can resolve … is refused by the RESOLVER, which necessarily runs make first" | true. The old NIT (FINDING 4) is closed |
| **Docstring :101-102 (edited in this round) "a gate target whose recipe carries a `-` / `@-` prefix … fails the lane by name, before make is invoked"; COMMANDS.md:68-70 (line 68 authored in this PR) "On pinned bytes it then refuses … a `-`/`@-` prefix …"; AGENTS.md:57 (from main)** | **false**. See R1-F1 |

## R1-7. Findings (round 1)

```
FINDING R1-F1: `.RECIPEPREFIX` in pinned bytes hides a `-` prefixed gate recipe; the anchor passes and `make ci` exits 0 with the gate failing, while the docs say the lane fails by name before make
Severity:    REQUIRED (blocks under the chair's "no false-guarantee merges" rule; the control gap itself is pre-existing on main)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/make-integrity-guard.py:101-102 (bullet edited at 08a59a9), check_text / logical_recipe_lines (tab-keyed; `.RECIPEPREFIX` appears only in the builtin-variable list at :685); docs/quality/COMMANDS.md:68-70 (line 68 authored at 17563bf in this PR); AGENTS.md:57 (from eeeea06)
  requirements: none yet — the desk review's FINDING 2 (search) marked "core: same gap"

Observed:
  Fixture `good`, copied, with two byte changes: `.RECIPEPREFIX := >` added under `.SHELLFLAGS`, and the ci recipe rewritten with `>` prefixes, the second as `> -./run-the-real-tests.sh`. Makefile re-pinned (a reviewed-bytes shape; no payload).
    GNU Make 4.3 (my container): `make-integrity-guard.py --root <copy> --targets ci --workflow` → exit 0, "passed (1 gate target(s); make ran 4 time(s), only on the pinned bytes of Makefile)". With `run-the-real-tests.sh` = `exit 1`, `make ci` exits 0.
    GNU Make 3.81 does not support `.RECIPEPREFIX`: the probe fails with exit 2 ("missing separator"), and the anchor reports it as "make would REMAKE one of Makefile" (mislabelled, but fail-closed).
  The pre-make text checks emitted no FAIL on either version.

Failure:
  The `-`-prefix and `|| true` checks are text controls on REVIEWED bytes. The PR's own tests call them the only reading that can see a `-` prefix ("A `-` prefix is INVISIBLE to `make --dry-run`… Only the text reading can see this one"). One directive blinds them on the acceptance platform's make (4.3), and a failing gate goes green. Three documents, two of whose lines this PR authored, state the refusal unconditionally.

Perspective:
  operator, developer

Recommendation:
  Smallest: refuse any assignment to `.RECIPEPREFIX` in the pinned read set pre-make (default-deny, like `.ONESHELL`), with a fixture `recipeprefix` (notInvoked). Or, at minimum, qualify the three sentences. The first is one line and matches the desk review's ask.

Acceptance criteria:
  The copy above → anchor exit 1 in both modes, 0 make processes, the message naming `.RECIPEPREFIX`; the clean tree and all 32 fixtures unchanged.

Tests:
  scripts/scripts_test.go TestMakeIntegrityGuardFixtures: add `{dir: "recipeprefix", wantFail: true, notInvoked: true, wantText: ".RECIPEPREFIX"}` plus its pinned fixture; the orphan test forces the row.

Cross-repo implications:
  core: this | search: the desk review's FINDING 2, same class | user/meta: none

Challenge:
  Pre-existing on main, and it needs a reviewer to approve both lines plus the pin. But this PR edited the very bullet and wrote the COMMANDS sentence, and the chair's rule is about what merges.
```

```
FINDING R1-F2: no fixture isolates the resolver's SHELL/.SHELLFLAGS/MAKEFLAGS/.ONESHELL failure branch
Severity: SHOULD   Confidence: high
Affected: vizra-core scripts/make-integrity-guard.py check_resolved/check_warnings; scripts/scripts_test.go
Observed: after fix round 1 every such fixture is refused by the text check before make, so check_resolved never fails in any test. At 62d16aa none isolated it either (text matched first), so this is not a regression.
Recommendation: a code-mutation demo, or a fixture reaching the resolver only (e.g. via a construct the text reading does not attribute), proving the post-make layer still fails by name.
Cross-repo: none.  Challenge: defence in depth, not the control.
```

```
FINDING R1-F3: rough edges that still fail closed
Severity: NIT   Confidence: high
- A pinned file that is unreadable (`chmod 000`) raises an uncaught PermissionError in verify_pin: anchor and check 11 both exit 1 with a traceback, 0 make. Better to report it by name.
- A pin that is a directory is labelled "not in its one accepted shape" by check 11.
- `make -q` exit 2 (a parse error, e.g. `.RECIPEPREFIX` on 3.81) is reported as "make would REMAKE one of …".
```

## R1-8. Cleanup and head

- Scratch `vzv-core-pr10r1-MGp6LT` was deleted by exact path.
- Containers ran with `--rm`. `ubuntu:24.04` was not removed: it was present before and used by `searchci-r2-40c87c`.
- The builder's checkout, the core #8 worktree and vizra-search were not touched.
- Head re-checked at end: `08a59a91a6dcc91c2346bcb206d4c0ad8603e90e`.

## Round-1 verdict

F1, F2, F3 and F4 are **fixed and reproduced**:
- the single probe works on 3.81 and 4.3, including a sibling of the main Makefile with includes pinned, and siblings of two includes at once;
- the wording is corrected;
- check-11 parity holds through the shared reader, with every malformed, duplicate, empty, missing or extra pin failing closed in both callers;
- the text checks run before make, with strictly stronger fixtures.

`make ci`, the unit report (1157/0 skipped), `scripts` 237 and both guards are green locally.

One REQUIRED finding remains, R1-F1. Under the chair's "no false-guarantee merges" rule it blocks: sentences this PR authored or edited state that a `-` prefixed gate recipe is refused by name before make, and on GNU Make 4.3 a pinned `.RECIPEPREFIX` makes the anchor pass with a failing gate. The fix is a one-line pre-make refusal plus one fixture, or a qualified sentence. If the chair rules pre-existing control gaps out of this slice's scope, everything else here would support `PASS (local; CI BLOCKED)`.

FINAL VERDICT: FAIL — SHA 08a59a91a6dcc91c2346bcb206d4c0ad8603e90e

---

# Re-verification at 398ac4f (round 2 of 2, the last)

- **Head:** `gh pr view 10` at start → `398ac4fe2bd8a6096a24e402936ef3ab2c2238bc`. It is one commit on `08a59a9`: "fix(ci): B5 fix round 2 — refuse .RECIPEPREFIX and .SECONDEXPANSION before make; target/pattern-specific and define assignments; expansion-produced prefixes and suffixes; resolver fixtures".
- **Clone:** new `mktemp -d …/vzv-core-pr10r2-XXXXXX`, fresh clone + `fetch pull/10/head`, detached at the SHA, with a second local clone for my sweeps.
- **Host:** darwin/arm64, GNU Make 3.81, go1.27.1.
- **4.3:** my own container `vzvpr10r2-make43-<pid>`, `--rm`, with **PyYAML 6.0.1 installed this time** and a logging `/usr/bin/make` wrapper. `ubuntu:24.04` was already present and in use by `searchci-r2-66aa22`, so it was not removed.

## R2-0. Scope

- Outside `scripts/`, `docs/`, `.github/pinned-makefiles.yml`, `AGENTS.md` and `README.md`: nothing.
- Frozen-path grep: no output.
- No file deleted in the round.
- Pin still `e7cc357c…` and still matches the Makefile.
- `git diff 08a59a9..HEAD -- scripts/scripts_test.go scripts/makefiledigest_test.go`: **zero removed lines**. The round only adds tests.

## R2-1. The builder's driver and demonstrations

- **3.81 host:** `demo.sh` exit 0, 0 uncommitted paths. Every row reproduced:
  - D0–D6 as in round 1.
  - **D7** (`.RECIPEPREFIX`): anchor exit 1 in both modes, 0 make processes, `Makefile:3 names .RECIPEPREFIX`.
  - **C10** and **C10b**: on 3.81 they are refused only as a `make -q` exit-2 parse error, because 3.81 lacks the feature.
  - C7 as before; C1–C9 red/green; **C11** (resolver removed), **C12**, C13 and C14 each turn their named test red (go test exit 1) and green after restore.
- **4.3 container** (`DEMO_ONLY=D`, exit 0):
  - D0–D6 match 3.81, with `ci-required-guard` **exit 0 on D0 and exit 1 by name on D1, D2 and D4** now that PyYAML is installed.
  - **D7:** raw `make ci` exits 0 on those bytes, while the anchor exits 1 with 0 make processes.
  - **C10** (pre-make refusal removed): the anchor still exits 1 after 4 make processes, from the resolver backstop `make resolves .RECIPEPREFIX to '>'`.
  - **C10b** (both removed, the 08a59a9 state): the anchor **exits 0**, reproducing R1-F1. Restored: exit 1, 0 make processes.
  - C7 BROKEN, then HELD after restore.
  - The in-container copy reported 1 uncommitted path afterwards. That is the container's scratch copy only; the host tree is clean.

## R2-2. All 46 makeguard fixtures, on 3.81 and 4.3

Swept with the recorder at `--workflow`; on 4.3 also counted with the make wrapper. **Exit codes and make-process counts are identical on 3.81 and 4.3 for all 46, and the recorder and wrapper counts agree on every fixture.**
- 0 make processes: every text-refused fixture, including the new `recipeprefix`, `secondexpansion`, `define-shell` and `pattern-specific-shell`.
- 1: `make-q-parse-error` (the probe's exit 2 is now labelled "make reported an ERROR", closing the round-1 NIT).
- 2: `missing-prerequisite`.
- 4 then refused by the resolver by name: `resolver-computed-{shell,makeflags,recipeprefix,secondexpansion}`, `prefix-from-{variable,chained-variable,function,pattern-specific}`, `suffix-from-variable`.
- 0 failures: `good` and `include-pinned-good`.

## R2-3. The chair's spellings (item 2)

I read these from code and confirmed them against the builder's fixtures and table. I built no new Makefile.

| Spelling | Where it is refused | Evidence |
|---|---|---|
| `.RECIPEPREFIX` in any line: comment, recipe, CRLF, tab-indented, any operator | before make (substring scan of every raw line of every file in the pinned read set, :876-880) | fixture `recipeprefix`; `TestEveryRefusedSpellingIsRefusedBeforeMake` (32 rows) is present and passed in the unit run |
| via `-include`/`include` of a pinned file | before make (the included file is in the read set and scanned the same way) | code :866-880 |
| via `$(eval …)` | before make (makefile_pin refuses any `$(eval`) | fixture `eval-in-pinned-bytes` |
| name held in a variable (`$(X)PREFIX`) | after make, resolver `.RECIPEPREFIX` from the `-pn` db | fixture `resolver-computed-recipeprefix`; C10 on 4.3 |
| backslash-newline split | not a substring. make joins a continuation with a space, so this is not a `.RECIPEPREFIX` name; the resolver backstop reads the db either way | reasoned, not run |
| prefix via a chained or recursive variable | after make: leading references are resolved iteratively from the db, up to 25 levels, then refused | fixture `prefix-from-chained-variable` |
| prefix via `+=` | after make (the db holds the final value) | reasoned from code, not run |
| via a leading function, automatic variable, substitution reference, or a target/pattern-specific variable | after make, refused as undeterminable | fixtures `prefix-from-function`, `prefix-from-pattern-specific` |

## R2-4. Remaining GNU Make 4.3 evaluation features (item 3)

**Method:** static reading of `make-integrity-guard.py`, `makefile_pin.py` and the docs (`grep` for each name), plus the GNU Make manual's documented semantics. **I did not build a Makefile for any of these.** A dynamic check of each would require constructing a neutering Makefile, which is outside my byte-and-file-mutation remit. Where a row needs a live check, I say so.

| Feature | Status at 398ac4f | Note |
|---|---|---|
| **`.IGNORE`** | **not named by any check** (0 hits in the guard, makefile_pin or docs). Before make: not refused. After make: the resolver's MAKEFLAGS check might catch a prerequisite-less `.IGNORE:` if make reflects it as `i` in the `-pn` MAKEFLAGS. **UNVERIFIED.** `.IGNORE: <gate target>` (per-target, per the manual) is by reading not visible to any check. | Same effect as a `-` prefix, per the manual. Covered only by the catch-all residual ("everything else a reviewed Makefile says is review's to catch", AGENTS.md:235-238) and the "not exhaustive" clause (AGENTS.md:215-217). For test lanes it is mitigated by the direct suite steps with floors, which run without make; `fixtures-verify`, `openapi-verify` and the other make-only lanes have no such second layer. **NEW-CLASS, see R2-F1** |
| `.SILENT` | not named | Suppresses echo only; no exit-status effect per the manual. Not a neutering feature |
| `.ONESHELL` | refused before make (line start) **and** after make (db) | fixture `oneshell`; C11 |
| `.POSIX` | not named | In 4.3 it adds `-e` to the shell flags only when .SHELLFLAGS is the default; here .SHELLFLAGS is pinned and checked. By reading, it does not weaken exit status. Residual |
| `.DEFAULT` | not named | Supplies a recipe for a prerequisite with no rule. Its recipe is outside the scanned gate closure (check_text notes rule-less prerequisites as "file dependencies, not lanes"). Catch-all residual. **Same class as R2-F2** |
| `.EXTRA_PREREQS` (4.3) | not named | Adds prerequisites the text closure (which parses explicit rule lines) does not see, so their recipes are not scanned. Catch-all residual. **R2-F2 class** |
| `.NOTPARALLEL` | not named | Ordering only; no exit-status effect |
| `$(eval)` / `$(call)` building rules | `$(eval`/`$(guile` refused before make wherever named (makefile_pin). `$(call)` cannot build a rule without eval. `$(call)` leading a gate recipe line → refused after make as undeterminable | fixtures `eval-in-pinned-bytes`, `prefix-from-function` |
| `vpath` / `VPATH` | not named | Changes prerequisite search, not recipe exit status. Catch-all residual |
| `.DEFAULT_GOAL` | not relevant | CI names explicit targets (pinned step bodies) |
| `export SHELL` | `export SHELL := x` refused before make (assignment regex allows `export`/`override`/`private`); bare `export SHELL` only exports the approved value | code :857-861; fixtures shell-* |
| `MAKESHELL` | not relevant | MS-DOS/Windows only, per the manual |
| gate target declared twice with `::` | by reading, refused before make as "defined 2 times" (the definition regex `^ci\s*:` matches `ci::`). A single `ci::` has its recipe scanned like any other | reasoned from code, not run |
| pattern-rule / implicit-rule recipes reached through a gate's prerequisites | not scanned for literal `-`/`+`/`|| true` (check_text scans only explicit `target:` rules for names in the closure) | **R2-F2** |

## R2-5. Lanes at 398ac4f (clean clone)

| Command | Exit | Counts |
|---|---|---|
| direct unit step + `go-test-report.py` | 0 / 0 | **1206 executed, 1206 pass, 0 skip** (my own JSON count `{'pass': 1206}`); `scripts` **286**; floor 943; `TestEveryRefusedSpellingIsRefusedBeforeMake` present and passed |
| `make ci` | **0** | all 10 lanes; `internal/fixtures` 253 s, `scripts` 42.8 s |
| both anchors (host) | 0 / 0 | 18 make processes on the pinned Makefile |
| `ci-required-guard.sh` (host and 4.3) | 0 / 0 | check 11 ok |
| tree after all runs | clean | 0 porcelain entries |

**CI: BLOCKED** (billing). There is no `ci-required` or any other Actions result for this SHA, and the integration suites were not run locally. Everything in §10 of the round-0 section remains absent.

## R2-6. Docs under "no false-guarantee merges"

- **Every sentence round 2 added is scoped to a named list of constructs,** with timing (before or after make), and ends in the explicit residual "the value of any other variable in the pinned bytes is not checked … everything else a reviewed Makefile says is review's to catch". COMMANDS.md and AGENTS.md match the code (R2-2, R2-3).
- **"-q runs no ordinary recipe"** and the single-probe sentences remain true (R1-2 and D6 on both versions).
- **One broad sentence is not from this PR:** the AGENTS.md control-matrix row "A one-line edit to the Makefile or its includes … cannot turn a required lane into a no-op" (blame: `eeeea06`, main) is contradicted, if R2-F1 is confirmed, by the unnamed `.IGNORE`. The same file says the list "is not called exhaustive". I record it as a pre-existing over-claim for the chair (R2-F3), not a round-2 authored one.

## R2-7. Findings (round 2)

No REGRESSION: every round-0 and round-1 row still holds on both make versions.

```
FINDING R2-F1: `.IGNORE` is not named by any anchor check. It has the same effect as a `-` prefix (the manual: errors are ignored for the listed targets, or for all when it has no prerequisites)
Severity:    SHOULD (follow-up slice). NEW-CLASS
Confidence:  medium (static reading plus manual semantics; dynamic behaviour UNVERIFIED)
Affected:    vizra-core scripts/make-integrity-guard.py (REFUSED_TOKENS :308-314 lists only .RECIPEPREFIX/.SECONDEXPANSION; no `.IGNORE` anywhere); AGENTS.md:235-238 residual
Observed:    `grep -c '\.IGNORE'` = 0 in the guard, makefile_pin.py, AGENTS.md and COMMANDS.md. Whether the resolver's MAKEFLAGS check sees a prerequisite-less `.IGNORE:` is UNVERIFIED. The per-target form has, by reading, no check that could see it.
Failure:     If confirmed, reviewed bytes naming `.IGNORE` for a make-only lane (fixtures-verify, openapi-verify, sqlc-verify, …) would let that lane pass on a failing command, with the anchor green. Test lanes keep the direct-suite second layer.
Recommendation: add `.IGNORE` to REFUSED_TOKENS (refused wherever named, before make), plus a fixture `ignore-special-target` (notInvoked). The same one-line treatment is worth considering for `.DEFAULT` and `.EXTRA_PREREQS` (R2-F2).
Acceptance criteria: a pinned Makefile naming `.IGNORE` → anchor exit 1 in both modes, 0 make processes, on 3.81 and 4.3.
Tests:       TestMakeIntegrityGuardFixtures row plus TestEveryRefusedSpellingIsRefusedBeforeMake rows.
Cross-repo:  search: same class (not checked).
Challenge:   The PR's docs never claim it is refused, they state a catch-all review residual, and the neutering-construct checks are B1 scope that predates this slice. That is why this is SHOULD, not BLOCKER. I withheld the dynamic confirmation (it would mean constructing a neutering Makefile); the builder's next slice can confirm it with its fixture.
```

```
FINDING R2-F2: recipes the gate closure reaches through rules other than explicit `target:` lines are not scanned for literal `-`/`+`/`|| true`
Severity:    SHOULD. NEW-CLASS
Confidence:  medium (code reading)
Affected:    scripts/make-integrity-guard.py check_text :938-956 (only lines matching `^<target>\s*:` for closure names are scanned); :988-990 ("prerequisite(s) have no rule and are treated as file dependencies")
Observed:    pattern/implicit rules, `.DEFAULT` and 4.3's `.EXTRA_PREREQS` can supply recipes that run as part of a gate, and none of them is a closure name with an explicit rule. The expanded-suffix dry-run check (check_warnings) does see their `|| true`; the literal `-` prefix, invisible to `--dry-run`, is not checked there.
Failure:     the "over the prerequisite closure" sentence (COMMANDS.md) is true only for explicit rules.
Recommendation: refuse `.DEFAULT`/`.EXTRA_PREREQS` by name, and either refuse pattern rules that match a closure prerequisite or scan their recipes; or narrow the sentence to "explicit rules".
Cross-repo:  search: same.
Challenge:   reviewed bytes; covered by the catch-all residual.
```

```
FINDING R2-F3 (pre-existing, for the chair): AGENTS.md control-matrix row "A one-line edit to the Makefile or its includes … cannot turn a required lane into a no-op" (from main, eeeea06) is broader than the controls, given R2-F1/R2-F2
Severity:    NIT for this PR (not authored here); SHOULD for the follow-up.
Recommendation: qualify it with "for the constructs named in sweep B5; review for the rest".
```

## R2-8. Cleanup and head

- Scratch `vzv-core-pr10r2-Vp6LXO` was deleted by exact path.
- The container ran with `--rm`. `ubuntu:24.04` was left in place (in use by `searchci-r2-66aa22`).
- The builder's checkout, the core #8 worktree and vizra-search were not touched.
- Head re-checked at end (see below).

## Round-2 verdict

- **Every round-2 claim reproduced on 3.81 and 4.3:** D7; C10 and C10b; the 46 fixtures, identical across versions and counted by two independent observers; C11–C14; the NIT fixes; no weakened test; 0 skips; 1206 executed; `scripts` 286; `make ci` 0.
- **Round-0 and round-1 findings are closed, with no regression.**
- **What remains is NEW-CLASS coverage**, all reachable only through reviewed, pinned bytes, all outside the slice's acceptance ("make runs only on reviewed bytes", FINDING 4), and none contradicting a sentence this PR authored:
  - R2-F1 `.IGNORE` (dynamic behaviour UNVERIFIED);
  - R2-F2 pattern/`.DEFAULT`/`.EXTRA_PREREQS` recipes;
  - R2-F3, a pre-existing broad sentence on main.
- **My recommendation to the chair:** open these as a follow-up hardening slice rather than re-plan B5. If the chair instead reads the main-branch sentence in R2-F3 as a false guarantee this merge would carry, the verdict would be FAIL on that basis alone.

FINAL VERDICT: PASS (local; CI BLOCKED) — SHA 398ac4fe2bd8a6096a24e402936ef3ab2c2238bc
