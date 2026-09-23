# Execution plan: vizra-search queue 2g — CI gates cannot be silenced or pass vacuously

## Context
- Repo: `/Users/yosefgamble/github/vizra/vizra-search`, base `origin/main@3ea4103`, branch `chore/m0-ci-hardening`.
- Builder: war-room builder (this session). Never verifies or merges its own work.
- Design source: vizra-core PR #9, merged as `eeeea068a20118f7af721f024264603b436a1528`
  (`.github/pinned-steps.yml`, `scripts/ci-required-guard.py`, `scripts/make-integrity-guard.py`,
  `scripts/go-test-report.py`, `scripts/test-floors.json`), and its verification history
  `docs/evidence/warroom/2026-09-21-vizra-core-pr9-hardening-b1-VERIFY.md` (round 1 A1–A34, round 2 N1–N6/P1–P16/J1–J5,
  round 3 AP1–AP10, DK1–DK4, R2-1).
- Search findings closed here: PR#3 VERIFY FINDING 4 (`source_ref_tip` unvalidated), FINDING 6 (`parse_remote_url`
  `parts[-2:]`); PR#4 VERIFY V3 note (no guard on a stray `os.Getenv`), FINDING 6 (prose counts), FINDING 7
  (no-echo guard reach); PR#2 VERIFY FINDING 8 (one Makefile line no-ops every lane, no CI lane catches it).

## Acceptance (brief items)
1. Make and direct-test steps pinned (`.github/pinned-steps.yml`), keys name/run/id only; pinned anchor immediately
   before each make step; strict mode chosen by `--workflow`; runtime refusal of MAKEFLAGS family, MAKELEVEL,
   MAKE_RESTARTS, MAKEOVERRIDES, MAKECMDGOALS, MAKEFILES, BASH_ENV, ENV, non-system make, every `?=`/referenced-unassigned
   Makefile variable; static refusal of those as job/workflow env, `defaults.run`, `container:`, undigested service
   images, duplicate keys, merge keys; each lane runs its recorded invocations.
2. `go test -json` → `scripts/go-test-report.py`: any skip fails, per-package floor for every package, unfloored package
   refused, counts printed; the direct step never swallows go test's exit.
3. `ci-required-guard.sh` fails loudly, by name, on a comment-only manifest.
4. `vendor-contract-selftest` is a required lane: `ci:`, manifest, floor, workflow — disagreement is red.
5. `vendor-contract.py --check` validates `source_ref_tip`; `parse_remote_url` requires exactly two segments.
6. AST test: no `os.Getenv`/`os.LookupEnv`/`os.Environ` (and relatives) outside `internal/config/env.go` in non-test code.
7. No-echo guard: WIDENED to the whole package (decision below); `config_test.go:616` and AGENTS.md say exactly that;
   the two prose counts fixed.
8. AGENTS.md states what the guards are and cannot do; never "exhaustive".

Non-goals: no service behaviour change; nothing under `api/` changes; vendored contract byte-identical.

## Implementation
- `.github/pinned-steps.yml` (new): anchor, make bodies, the direct unit body, required invocations per job.
- `scripts/ci-required-guard.py` (new, ported from core@eeeea06, adapted): floor, resolvable, triggered, continue-on-error,
  anchor, pinned make/direct steps, required invocations, surroundings, env, runner, action pins, duplicate + merge keys.
- `scripts/ci-required-guard.sh`: loud manifest read; floor/job-existence moved into the .py; still runs
  check-workflows.py + fixture floor, contract-drift anchor, bare names, Dockerfile digests, then the .py.
- `scripts/make-integrity-guard.{py,sh}` (new, ported): search's approved SHELL `/bin/bash`, gate targets from ci.yml,
  one byte-equal swallow exemption (contract-drift's `|| true`, judged by `ran`).
- `scripts/go-test-report.py` (new, ported, no skip allowlist, refuses `[no test files]`), `scripts/test-floors.json`.
- `scripts/doc.go` + `scripts/scripts_test.go` (Go meta-tests). Deviation from core: instead of committed fixture
  directories, each case is a controlled mutation of the REAL ci.yml / manifest / pins / Makefile in a temp copy
  (digest before/after, refused unless applied exactly once, restored byte-identical, green again), and the report
  cases are synthetic `go test -json` streams built in the test.
- `.github/workflows/ci.yml`: anchor before every make step; `test-noskip` becomes the direct pinned step; new
  `vendor-contract-selftest` job. `ci-required.yml`: loud manifest read.
- `Makefile`: `ci:` gains `vendor-contract-selftest`; `test-noskip` uses the report; `fmt-check` covers `scripts`.
- `scripts/vendor-contract.py` + selftest cases; `internal/config` AST tests; AGENTS.md; demo harness + transcripts.

## Verification
Focused: `go test ./scripts/ ./internal/config/`, `scripts/vendor-contract-selftest.py`, `scripts/ci-required-guard.sh`,
`scripts/make-integrity-guard.sh --workflow`. Lanes: `make ci`, `make vendor-contract-check`. Make 4.3: anchor rows in a
`ubuntu:24.04` container. Demonstrations: `scripts/ci-hardening-demo.py` → `docs/evidence/ci-hardening/`.

## Progress and evidence
Environment: darwin/arm64 host, load 150–450 (shared with other agents); go1.26.2 (host, GOTOOLCHAIN local), GNU Make
3.81, Python 3.9.6 + PyYAML 6.0.3. Make 4.3: `ubuntu:24.04` container `searchci-m43-*` (`--rm`), Python 3.12.3, go1.22.2
(only for `go env GOROOT`).

Preflight (2026-09-23): go, python3+yaml, make, docker, gh present; actionlint absent (not needed). Action pins confirmed
via `gh api repos/actions/{checkout,setup-go}/git/ref/tags/...` → 3d3c42e… (v7.0.1), b7ad1da… (v7.0.0), unchanged.
Coordinator heads-up 06:21Z: GitHub Actions refuses to start jobs on this account (billing). CI evidence may be BLOCKED.

Implemented (IMPLEMENTED, not VERIFIED):
- `.github/pinned-steps.yml`; `scripts/ci-required-guard.py` (ported from core@eeeea06 + PARITY check, merge-key refusal,
  job `if:`/reusable-workflow refusal, default-deny on `go test` steps, env refusal on direct lanes, strict pins file).
- `scripts/make-integrity-guard.{py,sh}` ported; search SHELL `/bin/bash`; one byte-equal swallow exemption.
- NEW FINDING while porting (not in core's history): the anchor's own `make -pn` EXECUTES `$(shell …)`, `$(file …)`,
  `+`/`$(MAKE)` lines and makefile-remaking rules, so a Makefile line can write MAKEFLAGS=-i to `$GITHUB_ENV` during
  the anchor step. Measured: 3.81 host (`make381-anchor-parse-side-effects-before.txt`) and Make 4.3 container rows
  p10/p11 (anchor exit 0, env file written) and g10 (a glob defeats variable stripping). Fixed with a parse-time
  pre-flight that refuses before make is invoked (rows m10–m13, h10 red, env file empty). Applies to vizra-core too.
- `scripts/go-test-report.py` (no allowlist, `[no test files]` refused, vacuous floors refused), `scripts/test-floors.json`
  (measured 553 executed / 0 skips; floors via --emit-floors).
- `ci-required-guard.sh` loud manifest read; `ci-required.yml` same fix.
- `vendor-contract-selftest` required lane (ci:, manifest, FLOOR_LANES, ci.yml job).
- `vendor-contract.py`: two-segment URL; `source_ref_tip` shape (no core) + existence/on-ref/contains-commit (with core);
  selftest 11 → 17 cases.
- `internal/config/envseam_test.go`; no-echo guard widened to the whole package + bypass test; prose counts fixed.
- AGENTS.md, Makefile, README, contract-drift-guard.py docstring; `scripts/ci-hardening-demo.py`.

Verification run by the builder (local, head 4476ad58aa3fbd7cd70604ad0b94ec10deea6b2d, before push):
- `make ci` exit 0 — 553 tests executed across 7 packages, 0 skips, every package at or above its floor; contract-drift 365
  tests; vendor-contract-selftest 17/17. (`vizra-search/docs/evidence/ci-hardening/make-ci-local.txt`)
- `go test -count=1 -v ./scripts/ ./internal/config/` exit 0 — 128 mutation rows RED as declared, then GREEN after a
  byte-identical restore. (`go-meta-tests-verbose.txt`)
- `scripts/ci-hardening-demo.py`, 36 rows, exit 1: 35/36. Row 5c was red for the right reason, but its declared want text
  was mis-quoted. After correcting only that text, `--only 5` exit 0: 3/3.
- GNU Make 4.3 container: every env and Makefile row red as declared; the hole reproduced (p10/p11/g10) and closed
  (m10–m13, h10). (`make43-anchor-rows.txt`)
- `vendor-contract.py --check` exit 0; `--check --core ../vizra-core` exit 0; `git diff origin/main -- api/` is empty.

PR: https://github.com/yegamble/vizra-search/pull/5 (READY_FOR_REVIEW).
CI on 4476ad5: all 12 jobs failed in ~3 s with 0 steps. Annotation: "The job was not started because recent account
payments have failed…". BLOCKED by billing; not re-run.
Cleanup: `ubuntu:24.04` (pulled by me) removed by name; `searchci-m43-*` containers ran with `--rm`; scratch dir deleted.

## Blockers and handoff
- BLOCKED: CI (account billing). Needs the owner to fix billing, then a re-run of the ci and ci-required workflows on 4476ad5.
- Cross-repo, reported to the chair and not changed here: vizra-core's anchor has the same parse-time side-effect
  hole. Its `make -pn` would execute `$(shell)`, `$(file)`, `+`, `$(MAKE)` and remake rules in the Makefile.
- Next action: independent verification of PR #5, then CI once Actions runs.

## Fix round 1 (2026-09-23) — the control moves from grammar to digest
Input: the chair's ruling on docs/evidence/warroom/2026-09-23-anchor-preflight-DESK-REVIEW-security.md (FINDINGS 1–3).
The verifier reproduced the baseline and declined to build payloads; the security seat's desk review found the text
scanner admits `.SECONDEXPANSION` + `$$`-escaped prerequisites and `.RECIPEPREFIX`.
Changes (commits on top of 4476ad5, no amend or force-push):
- `.github/pinned-makefiles.yml` (`path: sha256`, a format shared with core slice 2d-B5). The anchor refuses to invoke make
  unless the bytes match, and refuses an unpinned GNUmakefile/makefile (exact-name listing, so it is case-insensitive-FS safe). After
  make runs, MAKEFILE_LIST must equal the pinned set. This applies in both modes; there is no `make ci-guard` in search.
- The text-shape scanner (`check_parse_time_side_effects`, APPROVED_SHELL_CALLS) is RETIRED. Kept: the environment
  checks, the make-is-a-real-file check, the resolver, the text readings of reviewed bytes (plus `.SECONDEXPANSION` and
  `.RECIPEPREFIX` refusals there, no claim of control), and the runner command-file scrub.
- `ci-required-guard.py`: DIGEST check (exists, non-empty, 64-hex, covers Makefile, tree matches).
- The `ok` wording now states what the digest guarantees; AGENTS.md, ci.yml, Makefile header, and the pin comments are updated.
  The residual is named: a reviewer approving a malicious Makefile together with its pin update.
- Tests: TestTheAnchorRunsMakeOnlyOnPinnedBytes, TestMakeIntegrityGuardStillRefusesKnownShapesInReviewedBytes, and
  digest rows in TestCIRequiredGuardRefusesEveryEvasion. The demo harness has rows 1k–1m4 and 1q.
- Make 4.3 container: `make43-digest-gate-round1.txt`. Every row is as expected; the env file is empty in all rows.
- Review follow-ups (comment false positives, CRLF in the scanner) did not survive the redesign: the scanner is gone.

Round 1 pushed: head c3b2021ee089a04dfbfce2a8cb0d3ee653e8b7fb. CI on c3b2021: all 12 jobs failed with 0 steps (billing annotation); not re-run.
Local: make ci exit 0 (554/0 skips); go meta-tests exit 0 (129 red→green rows); demo 39/39; Make 4.3 digest rows as expected.
Next: independent verification of round 1; CI once billing is fixed; core slice 2d-B5 adopts the same pin format.

## Fix round 2 (LAST) — re-verification FAIL at c3b2021
Inputs:
- VERIFY "Re-verification at c3b2021": FINDING 2 BLOCKER (a newer unpinned Makefile.sh rewrites the Makefile during the
  anchor's own `make -pn`); FINDING 3 NIT (revendor-demo.sh `printf | grep -q`); FINDING 1 NIT (the "behind" note).
- Security re-review at c3b2021: R-1 (every make call through one digest-gated helper, plus a meta-test inventory, plus
  ci-required parity), R-2 (a failed pre-make check stops before make; MAKEFILES scrubbed; make started by its checked
  realpath), R-3 (lstat regular non-symlink files; case-folded sibling names).
- Chair correction: ONE `make -q` naming EVERY pinned file; do not say "-q runs no recipe"; zero make processes on a
  failed pre-make check (BASH_ENV was measured at 19); guard parity for siblings, symlinks and stale or missing pins.
Design (aligned with core PR #10 @62d16aa; the pin shape is `makefiles:` then `  path: sha256`):
- NEW `scripts/makegate.py` is the one helper. It covers pin parse, lstat regular files, the static read set (includes
  pinned, eval/guile/computed names refused), case-folded siblings, MAKEFILES refused, clean_env (flag vars, MAKEFILES,
  BASH_ENV, ENV, GITHUB_* and anything in the runner command-file dir), the checked make realpath, ONE
  `make -q <all pinned>` remake probe, and a re-hash after every run. It has a CLI for the Go tests.
- The anchor, contract-drift-guard.py (runs before the anchor) and lane_selection_test.go (inside test-noskip) all use
  it. ci-required-guard.py runs its checks without starting make.
- `-r`/`--no-builtin-rules` is NOT used. In the probe it would hide the very built-in remake the pinned `make` step
  would perform, and on the resolver it would change MAKEFLAGS and the database the checks read.
- Tests: TestTheAnchorRefusesAPinnedMakefileMakeWouldRemake (10 siblings), TestTheRemakeProbeCoversEveryPinnedInclude,
  TestEveryOtherMakeCallIsGated, TestTheAnchorStartsNoMakeAfterAFailedPreMakeCheck (asserts "0 make process(es)"),
  TestPinnedFilesMustBeRegularAndAloneInBothReaders, TestEveryPlaceThatStartsMakeIsGated.
- Docs: "without make" is now "without a make step" (Makefile, AGENTS.md, ci.yml, ci-required-guard). The anchor's
  "refuses to invoke make" claim is scoped to makegate. The pin header says "same shape core PR #10 uses". The -q
  wording is corrected. NITs fixed.
Measured (GNU Make 3.81 host): newer Makefile.sh/.c/.o/.y/.l, SCCS/s.Makefile and s.Makefile are refused by the probe,
with the Makefile byte-identical afterwards. The RCS `,v` and RCS/ forms leave `make -q Makefile` at 0 (make would not
remake an existing Makefile from them), so the anchor is correctly green and the bytes are unchanged.
Chair corrections during round 2 (design alignment, not new rounds):
- ONE `make -q` naming every pinned file (already the case). TestTheRemakeProbeCoversEveryPinnedInclude shows a pinned
  include plus a newer inc.mk.sh is refused by `make -q Makefile inc.mk`.
- The -q wording is corrected everywhere. `+` and `$(MAKE)` lines are now also refused before make, so the probe runs no
  recipe from reviewed bytes either.
- 0 make processes on any failed pre-make check. Tested for MAKEFILES, BASH_ENV, ENV, MAKEFLAGS, GNUMAKEFLAGS, VERSION
  and a stub make.
- Guard parity: symlink, sibling, missing pin, stale pin. Tested in both readers.
- Named constructs refused before make (makegate.reviewed_bytes_problems): .RECIPEPREFIX, .SECONDEXPANSION, .ONESHELL,
  .IGNORE, .DEFAULT, .POSIX, .EXTRA_PREREQS; SHELL/.SHELLFLAGS other than the approved line; MAKEFLAGS, GNUMAKEFLAGS and
  MFLAGS in any form (target- and pattern-specific, define, private, override); $(eval); `+` and $(MAKE); recipe lines
  that begin with an expansion. After make: expansion-produced swallowed exits, read from make's --dry-run.
  TestNamedMakefileConstructsAreRefusedBeforeMake runs 25 inert, re-pinned cases, each asserting 0 make processes.
- 4.3 container: the first round-2 container hung on a measured row, a per-file `make -q` with a +1-day sibling. The
  inferred cause is make re-exec looping. It was killed and the row is now bounded by `timeout 60`.

Round 2 pushed: head e068e07fed999141a601374bb2b3b6251ede04d6. CI on e068e07: all 12 jobs failed with 0 steps (billing annotation); not re-run.
Local: make ci exit 0 (613 tests / 0 skips); go -v meta tests exit 0 (456 PASS / 0 FAIL); demo 44/44; Make 4.3 rows as declared (one row lost to a harness printf bug, re-run separately: red, 0 make).
Next: independent re-verification at e068e07; CI once billing is fixed.

## Closing slice (fresh builder, 2026-09-23) — no false-guarantee sentences
Inputs: security desk review at e068e07 (`docs/evidence/warroom/2026-09-23-vizra-search-pr5-makegate-DESK-REVIEW-security.md`,
M-1…M-5, N-1…N-3) and VERIFY "Re-verification at e068e07, part 2" FINDING 4. Base: `origin/chore/m0-ci-hardening` =
e068e07fed999141a601374bb2b3b6251ede04d6. ONE commit on top, fast-forward push, no force/rebase. Worktree:
`/Users/yosefgamble/github/vizra/.claude/worktrees/search-pr5-close` (local branch `close/search-pr5`, tracks the PR branch).
Out of scope (chair): porting core's B5b closure / computed-name machinery; `api/`; the Makefile (untouched, pin unchanged).

Plan:
1. M-1/M-2 — narrow AGENTS.md (named constructs; "What it guarantees"; stale "aligned with core PR #10"), makegate.py
   docstring + block comment, anchor docstring, `prerequisite_closure` docstring and the GATE_TARGETS comment to exactly what
   the code enforces: LITERAL spelling at the start of a line; recipe scan = EXPLICIT rules of the named closure only.
   Both added to the residuals with "core refuses these (vizra-core #11); search adopts core's anchor in a follow-up".
2. M-3 — makegate: refuse a recipe body starting with `$` that is not `$$`. Rows `$@`, `$<`, `$X` in
   TestNamedMakefileConstructsAreRefusedBeforeMake (re-pinned, 0 make, refusal by name) + a `$$` control that stays green.
3. FINDING 4 — widen the inventory: Go via go/ast (os/exec Command/CommandContext, a make/gmake string literal in ANY
   argument, or a shell string with make in command position); Python via the `ast` module (every string passed to a
   subprocess.* / os.system|popen|exec*|spawn* call, list or shell=True, `env make` included); shell lines with make in
   command position after `;` `&&` `||` `|` `(` `` ` `` `{` `!` then/do/if/elif/else/while/until/time, any path prefix.
   A planted-call table test for every form (+ negative controls). Sentences narrowed to name exactly this.
4. M-4 — move the anchor's environment-taken computation into makegate (`environment_taken`) and drop those names in
   `run_make` for EVERY make process (anchor, contract-drift-guard, lane test). Test: record the env of every make process
   the contract-drift-guard path starts, with VERSION/COMMIT/CORE/GOFLAGS planted.
5. N-1, N-2 wording; N-3 a final `make -q` at the end of the anchor.
Verification: `make ci`; `go test -count=1 -v ./scripts/ ./internal/httpapi/`; `scripts/ci-hardening-demo.py`;
`ci-required-guard.sh`; `make-integrity-guard.sh --workflow`; red/green under `docs/evidence/ci-hardening/closing/`.

### Closing slice: evidence (READY_FOR_REVIEW, not VERIFIED)
Pushed once as a fast-forward `e068e07..617c6d9` to `chore/m0-ci-hardening`. Head **617c6d92b34c1acb68556f5f02a5b12793344cf5**.
PR #5 body now starts with "READY_FOR_REVIEW. CI: BLOCKED" and has a "Closing slice" section. The four round-2 bullets
that overclaimed are annotated inline.
- Files: AGENTS.md, scripts/makegate.py, scripts/make-integrity-guard.py, scripts/scripts_test.go,
  scripts/ci-hardening-demo.py (rows C1 to C10), .github/pinned-makefiles.yml (a comment only),
  docs/evidence/ci-hardening/README.md, docs/evidence/ci-hardening/closing/ (6 transcripts).
- Unchanged: the Makefile (sha256 e9d7c58…, which equals its pin) and `api/` (`git diff e068e07 -- api/` is empty).
- The transcripts ran on the working tree. The sha256 of every changed code or doc file was recorded before the runs and
  re-checked just before the commit: all OK.
- Host: darwin/arm64, go1.27.1, GNU Make 3.81, Python 3.9.6. Nothing in this slice ran on GNU Make 4.3.

| command | exit | counts |
|---|---|---|
| `make ci` | 0 | 664 tests / 7 pkgs / 0 skips; contract-drift 365; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | 0 | 423 PASS / 0 FAIL / 0 SKIP |
| `scripts/ci-hardening-demo.py` | 0 | 54/54 (C1 to C10 are the closing rows) |
| `scripts/ci-required-guard.sh` | 0 | passed, 11 required checks |
| `scripts/make-integrity-guard.sh --workflow` | 0 | passed; 21 make runs, the last being the final `make -q` (N-3) |
| `scripts/vendor-contract.py --check` | 0 | — |
| new tests against e068e07's unmodified gate (BEFORE) | 1 | M-3 `$@`/`$<`/`$X` FAIL; both M-4 callers FAIL (planted names reached make) |
| C4 to C10 planted forms against e068e07's inventory (BEFORE) | 0 each | 7/7 missed (FINDING 4 reproduced) |

- CI on 617c6d9: all 12 jobs failed with 0 steps and the billing annotation. BLOCKED; not re-run.
- Deviation from the brief's wording, disclosed: the brief asked for "core refuses these (vizra-core #11)". Reading core at
  29387da (`git show`, not run), its `prerequisite_closure` also drops a `$`-named prerequisite (its line 812), and grep
  found no refusal of one. The residual therefore says that core #11 refuses computed names and non-explicit closure
  recipes (per the security seat), and that the `$`-named prerequisite is refused in neither repo yet. This confirms, by
  reading only, the security seat's UNVERIFIED cross-repo note on M-1.
- Next action: independent verification of 617c6d9, then CI once billing is fixed. A follow-up slice adopts core's anchor
  in search.

### Closing slice, fix round 1 of 2 (READY_FOR_REVIEW, not VERIFIED)
Input: `docs/evidence/warroom/2026-09-23-vizra-search-pr5-closing-VERIFY.md` (FAIL at 617c6d9: FINDING 5 and 6 REQUIRED,
FINDING 7 and 8 SHOULD, 3 NITs). Chair ruling: refuse where cheap, narrow only where refusing is not practical. Fresh
worktree `.claude/worktrees/search-pr5-close2` (local branch `close2/search-pr5`), since removed. Pushed once as a
fast-forward `617c6d9..888a51b`. Head **888a51b872f15fa5fa0ca9d323f4d06a9b12d166**. The Makefile (e9d7c58…, equal to
its pin), `.github/` and `api/` are unchanged.

What changed, in code:
- makegate.rule_line_problems refuses: an inline `;` recipe; several targets on one rule line (grouped `&:` too); an
  expansion as a rule target; a rule line starting with whitespace; a rule line continued with `\`.
- makegate.computed_name_problems refuses a variable name that is an expansion in any assignment or `define`.
- `_MANUFACTURES_DIRECTIVES_RE` also refuses `$(call eval|guile|$(F),…)`.
- run_make drops environment_words: every word of the pinned text, minus KEEP_ENV.
- The anchor: logical_recipe_lines steps over conditional directives; prerequisite_closure reads makegate's logical
  lines, so comments are stripped; the unused RULE_RE is removed.
- The inventory: an env/nohup/sudo flag may take one argument; a Go dot-import is matched; Python star-imports are
  matched; a Python list or tuple literal starting with make is matched anywhere.

Found beyond the verifier's list, same class, all fixed: the indented, continued and computed-target rule lines; a
conditional inside a recipe; a `=` in a rule line's comment dropping prerequisites from the closure; `$(call eval,…)`;
Python star-imports. Today's Makefile uses none of them.

Tested-file sha256s were recorded after the last edit and re-checked before the commit: all OK. After the demo's C3
declared text was corrected, make ci, go test -v and the guards were re-run so that every transcript matches the final
bytes.

| command | exit | counts |
|---|---|---|
| `make ci` | 0 | 689 tests / 7 pkgs / 0 skips; contract-drift 365; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | 0 | 448 PASS / 0 FAIL / 0 SKIP |
| `scripts/ci-hardening-demo.py` | 0 | 70/70. The first run was 69/70: C3 red for the right reason, stale declared text. Both transcripts kept. |
| `ci-required-guard.sh` / `make-integrity-guard.sh --workflow` / `vendor-contract.py --check` | 0 / 0 / 0 | anchor: 21 make runs |
| this round's tests against 617c6d9's gate files (BEFORE) | 1 | 13 new pre-make rows + 2 reading rows + both M-4 callers FAIL |
| R11–R16 against 617c6d9's inventory (BEFORE) | 0 each | 6/6 missed |

- CI on 888a51b: all 12 jobs failed with 0 steps and the billing annotation; not re-run.
- Evidence is in `vizra-search/docs/evidence/ci-hardening/closing/round1/`.
- Next action: independent re-verification of 888a51b. This was fix round 1 of 2.

### Closing slice, fix round 2 of 2 (the last; READY_FOR_REVIEW, not VERIFIED)
Input: VERIFY "Re-verification at 888a51b" (FAIL: F9, F10, F11 REQUIRED; F12, F13 SHOULD). Chair ruling: ALLOWLIST the
Makefile grammar, default-deny per line. Fresh worktree `.claude/worktrees/search-pr5-close3`, since removed. Pushed once
as a fast-forward `888a51b..e711d33`. Head **e711d336e147583a084252387f4a19697e5f8788**. The Makefile (e9d7c58…, equal to
its pin), `.github/` and `api/` are unchanged.

The grammar:
- `makegate.grammar_problems` runs before make, for every caller and in ci-required-guard.
- The allowed shapes: blank or comment; `NAME := | ?= | = value`, with the value using only `$$`, `$(NAME)`, `${NAME}`
  and `$(shell …)`; `.PHONY: names`; a single-target rule with literal prerequisites; a TAB recipe line of a rule, using
  `$$`, `$(NAME)` and `${NAME}` only, and not `$(MAKE)`. `RECIPE_FUNCTIONS = ()`.
- The real Makefile passes unchanged: 133 blank or comment, 15 assignment, 17 phony, 17 rule, 24 recipe lines.
- The by-name checks are kept as a second diagnosis, and their misses are stated.
- The anchor's conditional stepping from round 1 is removed.

Test changes, all disclosed in the PR and the README:
- the include-probe test now asserts that the include is refused before make;
- the M-4 test plants only the forms the grammar allows;
- the lane test with `include drift.mk` now asserts the grammar refusal;
- one reviewed-bytes row moved to the before-make rows;
- demo row R08 is removed, and R01/R04 remove both layers.

| command | exit | counts |
|---|---|---|
| `make ci` | 0 | 720 tests / 7 pkgs / 0 skips; contract-drift 365; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | 0 | 479 PASS / 0 FAIL / 0 SKIP |
| `scripts/ci-hardening-demo.py` | 0 | 75/75. The first run was 73/75, with R01/R04 masked by the grammar; kept. |
| guards / `vendor-contract.py --check` | 0 / 0 / 0 | — |
| this round's tests on 888a51b's gate files (BEFORE) | 1 | 31 grammar rows FAIL: 24 accepted outright, 7 red by another check. The include test and the grammar test FAIL. |

- A claim removed rather than asserted: "GNU Make 3.81 and 4.3 disagree on `#` inside `$(…)`". That was unverified, from
  memory, and nothing here ran on 4.3.
- CI on e711d33: 12 jobs failed with the billing annotation; not re-run.
- Evidence is in `vizra-search/docs/evidence/ci-hardening/closing/round2/`.
- Next action: independent re-verification of e711d33. If it fails, the slice goes BLOCKED and moves to queue 2o.

## Re-plan: one line reader (fresh builder, 2026-09-23; IN_PROGRESS)
Input: VERIFY "Re-verification at e711d33" (FAIL: FINDING 14 REQUIRED, FINDING 15 SHOULD, NBSP NIT). Chair brief: one
commit on `chore/m0-ci-hardening` from head `e711d336e147583a084252387f4a19697e5f8788`, fast-forward push, no force.
Worktree `/Users/yosefgamble/github/vizra/.claude/worktrees/search-pr5-close4` (local branch `pr5-close4` tracking
`origin/chore/m0-ci-hardening`). Preflight: go1.27.1 darwin/arm64, GNU Make 3.81, Python 3.9.6 + PyYAML, gh logged in;
GNU Make 4.3 not available locally (not run). GitHub CI: BLOCKED (billing), not re-run.

Defect class: two readers of the same bytes disagree on where lines are (grammar joins; the anchor's recipe reader,
check_text, prerequisite_closure's caller, ci-required-guard and contract-drift-guard split physical lines, some via
`read_text()` universal newlines).

Plan:
1. makegate gets ONE decoder (`read_makefile_text`: bytes -> strict UTF-8, no newline translation) and ONE line reader
   (`makefile_lines(text)` -> LogicalLine records: first line number, physical segments, tab flag, joined raw text,
   comment-stripped code). `_logical_lines` and `_grammar_lines` are deleted. Every text reading of a pinned makefile
   consumes it: grammar_problems, reviewed_bytes_problems, static_read_set, the parse-time sites, environment_taken,
   environment_words; the anchor's prerequisite_closure, check_text (definitions, assignments, conditional depth) and
   logical_recipe_lines; ci-required-guard's makefile_env_names, check_makefile_selection, check_local_parity;
   contract-drift-guard's check_makefile_text (a reader of the same pinned bytes, included for the same reason).
2. Grammar tightened before make: a comment continued by an unescaped trailing backslash is refused; every control
   character other than TAB and LF (CR anywhere, NUL, C1) and every non-ASCII whitespace character (NBSP, U+2028 …)
   is refused; "blank" means an EMPTY line (a line of only spaces/TABs is refused); a comment line starts with `#` in
   column 0; the directive keywords are excluded from an assignment NAME (FINDING 15).
3. Tests: in-process inert-string test (committed functions, each FINDING 14 example, lone CR, CRLF, NUL, NBSP, each
   directive keyword) + a reader-identity test (spy/poisoned `makefile_lines` changes every reader's answer);
   re-pinned inert rows in TestNamedMakefileConstructsAreRefusedBeforeMake (0 make processes, refusal by name).
   Red on e711d33's gate files, green on mine; demo C-rows (remove each check: red; restore byte-identically: green).
4. Docs: AGENTS.md, anchor docstring, makegate docstring/block comment, logical_recipe_lines docstring: the grammar and
   "a rule's recipe is exactly the TAB lines after it" made true, and "one reader serves every check".
Evidence dir: `vizra-search/docs/evidence/ci-hardening/closing/replan/`.

### Re-plan evidence (IMPLEMENTED locally; READY_FOR_REVIEW once pushed; not VERIFIED)
Modified in vizra-search: `scripts/makegate.py`, `scripts/make-integrity-guard.py`, `scripts/ci-required-guard.py`,
`scripts/contract-drift-guard.py`, `scripts/scripts_test.go`, `scripts/ci-hardening-demo.py`, `AGENTS.md`,
`docs/evidence/ci-hardening/README.md`, new `docs/evidence/ci-hardening/closing/replan/*.txt`. Makefile, pin,
`.github/`, `api/` unchanged.

| command | exit | counts |
|---|---|---|
| new tests on e711d33's gate code (detached worktree, only scripts_test.go replaced) | 1 | 55 subtests FAIL (31 inert-string, 24 re-pinned rows: 5 accepted outright, 6 other pre-make check, 11 red after `make -q` started, 2 duplicate-target); reader + recipe tests FAIL |
| `make ci` | 0 | contract-drift 365; test-noskip 801 / 7 pkgs / 0 skips; selftest 17/17 |
| `go test -count=1 -v ./scripts/ ./internal/httpapi/` | 0 | 560 PASS / 0 FAIL / 0 SKIP |
| guards under `env -i` (ci-required-guard.sh, make-integrity-guard.sh --workflow, vendor-contract.py --check) | 0/0/0 | 11 checks; make ran 21 times; OK |
| `scripts/ci-hardening-demo.py` | 0 | 85/85. The first run was 84/85: C19 was not red because the identity probe held only `id()`s, which can be reused. The probe now keeps the objects. Both transcripts are kept. |
Real-Makefile reader outputs identical to e711d33 (taken, 559 words, 4 sites, grammar [], closure 10).
Pushed once, fast-forward `e711d33..854a337`. Head **854a3376f005dc7cca3358d9b815205616f7b2fb**. The PR #5 body now opens with a
"Re-plan: one line reader" section, and its first line says CI: BLOCKED. State: READY_FOR_REVIEW, not VERIFIED. The worktree
`search-pr5-close4` and its scratch dir are removed. Evidence: `vizra-search/docs/evidence/ci-hardening/closing/replan/`.
Next action: independent re-verification of 854a337.

### Re-plan follow-up: FINDING 16 plus three nits (chair hold on the PASS at 854a337)
- **Worktree:** `.claude/worktrees/search-pr5-close5`, branch `pr5-close5` tracking `origin/chore/m0-ci-hardening`.
- **FINDING 16:**
  - The probe's file-level SOURCE check is now an AST scan of the four files for every text-read spelling, against 28 NAMED non-makefile reads.
  - `_ASSIGN_RE` loses its no-op `re.M`.
  - The makegate comment is narrowed to what the test holds.
  - New `TestTheOneReaderSourceCheckRefusesAPlantedReader`: 7 plants.
- **NITs:** the probe fixture moved to the Go test's `t.TempDir()`; `-load` added to AGENTS.md; `TestTheRealMakefileFitsTheGrammar` now reads through `read_makefile_text`.
- **Red at 854a337:** 7/7 plants FAIL; six were reported by nothing.
- **Green:**
  - `make ci` 809 / 0 skips;
  - `go test -v` 568/0/0;
  - demo 87/87 (C21 and C22 red then green);
  - guards and vendor check: all exit 0.
- **First attempt:** `make ci` exit 2, `go test` 4 FAIL, demo 82/87. The cause was the vendored manifest's file name in the test's reason text. It is fixed, and the failed transcripts are kept.
Pushed `854a337..6646ccd`. Head **6646ccde99f466d6c52f2c8ef43571c24abc875f**. Worktree removed. Next action: the verifier's re-confirmation.
- FINDING 17 (docs and comments only): pushed `6646ccd..1d28281`. Head **1d28281a9e5f639306d4c7b5702e7f791a3df80a**. `make ci`: 809 tests, 0 skips. `go test -v`: 568/0/0. Worktree removed.
