# Execution plan: 2d-B5 — the vizra-core anchor never runs make on unreviewed Makefile bytes

Status: IN_PROGRESS (builder). Never VERIFIED by this author.

## Context
- Repo: `vizra-core`, checkout `/Users/yosefgamble/github/vizra/vizra-core`, branch `chore/m0-anchor-makefile-digest` from `origin/main@eeeea068a20118f7af721f024264603b436a1528`.
- Board queue: 2d-B5. Source: `docs/evidence/warroom/2026-09-23-anchor-preflight-DESK-REVIEW-security.md` FINDING 4 and the chair ruling (tick 132): the control is a committed digest of the Makefile bytes, not a text-shape scanner.
- Search's `RUNNER_COMMAND_FILES` scrub read (read-only) from `vizra-search@origin/chore/m0-ci-hardening` (4476ad5), `scripts/make-integrity-guard.py:183-196`. Its text scanner is NOT ported.
- Core PR #8 (separate worktree, not touched) edits the Makefile: whichever of #8 / this PR merges second must update the Makefile digest pin in the same merge.

## Acceptance
1. `.github/pinned-makefiles.yml` (path -> sha256) covers the Makefile and every file make may read. The anchor, in `--workflow` and lenient modes, computes the digests BEFORE invoking make; on any mismatch, and when the statically determined MAKEFILE_LIST would include an unpinned file, it refuses with make NOT invoked.
2. `ci-required-guard.py` asserts the pin exists, is non-empty, covers the Makefile (and, outside `--skip-makefile`, that it matches). A Makefile edit without a paired pin update fails by name.
3. `clean_env` for every subprocess the anchor runs drops GITHUB_ENV, GITHUB_PATH, GITHUB_OUTPUT, GITHUB_STATE, GITHUB_STEP_SUMMARY and any other runner command-file variable; demonstrated a subprocess cannot see them.
4. Demonstrations (byte mutations only): one Makefile byte; extra `include`; included file bytes; pin entry deleted -> red, make not invoked (proved by a spawn recorder); clean tree green on GNU Make 3.81 (host) and 4.3 (own ubuntu:24.04 container).
5. The ok message and docs state the guarantee exactly (reviewed bytes, including the reviewed `$(shell …)` calls at Makefile:22-23) and name the residual (a reviewer approving a malicious Makefile together with its pin; CODEOWNERS advisory).

Non-goals: no change under api/, internal/, cmd/, migrations/; Makefile content unchanged; required-checks.txt, FLOOR_LANES, pinned-steps.yml unchanged.

## Implementation
- `scripts/make-integrity-guard.py`: pin loader (strict line format, stdlib only), static MAKEFILE_LIST determination over pinned bytes, digest pre-flight gating every make invocation; all pre-flight failures stop before make; post-make corroboration (make's MAKEFILE_LIST == pinned set, pinned bytes unchanged); `clean_env` scrub.
- `scripts/ci-required-guard.py`: check 11 (pin exists / non-empty / covers Makefile / matches).
- Fixtures: pin files for every `scripts/testdata/makeguard/*`; new digest fixtures; `scripts/testdata/makefilepin/*` for check 11.
- `scripts/scripts_test.go`: mutation table over a temp copy of the REAL tree + recorder harness; clean_env subprocess visibility test.
- Docs: AGENTS.md, both guard docstrings, README.md, docs/quality/COMMANDS.md; evidence under `docs/evidence/hardening-b5/`.

## Verification
- `go test -race -count=1 ./scripts/` ; `make ci` ; `./scripts/ci-required-guard.sh` ; `./scripts/make-integrity-guard.sh` and `--workflow` ; direct unit steps with `scripts/go-test-report.py`.
- Container: GNU Make 4.3 in `ubuntu:24.04`, unique name, `--rm`.

## Progress and evidence
(appended below as it runs)

## Blockers and handoff
- GitHub Actions refuses to start jobs (billing) since ~06:21Z 2026-09-23: CI is BLOCKED; push once, do not re-run.

### 2026-09-23 — implementation (IMPLEMENTED, not verified)
- Branch `chore/m0-anchor-makefile-digest`; commits 17563bf (control), 57c1b7e (env-stop test), 4410fd1/e8e3ffc/3c56be5 (demo driver), 42c5609 (assert wording), 36c3f7c (evidence).
- Files: `.github/pinned-makefiles.yml` (Makefile e7cc357c…), `scripts/make-integrity-guard.py`, `scripts/ci-required-guard.py` (check 11), `scripts/scripts_test.go`, `scripts/makefiledigest_test.go`, `scripts/testdata/spawn-recorder.py`, `scripts/testdata/makeguard/*` (pins for the 18 existing + 13 new fixtures), `scripts/testdata/makefilepin/*` (7), AGENTS.md, README.md, docs/quality/COMMANDS.md, `docs/evidence/hardening-b5/`.
- FINDING (new, measured): GNU Make 3.81 AND 4.3 remake a Makefile from a newer sibling `Makefile.sh` via the builtin `%: %.sh` rule, EVEN UNDER `make -pn`, then read the rewritten bytes — no makefile line needed. The digest alone cannot see it (bytes still pinned when checked). Closed here with a `make -q <pinned makefiles>` probe (no recipe runs) before any other make, pinned makefiles named as goals on every later anchor make command, and a post-make re-hash. Transcripts: docs/evidence/hardening-b5/make-3.81-host/D5-remake-sibling.txt and make-4.3-ubuntu24.04/D5-remake-sibling.txt. Same class applies to vizra-search's anchor (not touched).
- Demonstrations (scratch clone at 3c56be5, via docs/evidence/hardening-b1/mutate.sh): D0 clean green both modes (3.81 and 4.3), D1 one Makefile byte, D2 extra include, D3 included a.mk byte, D4 pin entry deleted — each anchor exit 1 in both modes with 0 make processes recorded, ci-required-guard exit 1 by name; restore byte-identical; D5 remake sibling refused with only `make -q` started, Makefile byte-identical. C1–C6 code mutations each turn the named test red (go test exit 1) and green after restore.
- GNU Make 4.3: own `ubuntu:24.04` container `b5digest-make43-1790150290`, `--rm`; image was not present before, pulled, then removed with `docker rmi ubuntu:24.04`.

### 2026-09-23 — local lanes on code tree 36c3f7c (head 62d16aa adds only COMMANDS.md)
- `make ci` exit 0 (test-race 14 ok / 8 no-test-files / 0 FAIL); both anchors exit 0; `ci-required-guard.sh` exit 0; direct unit step + go-test-report exit 0 — 1149 executed, 0 failed, 0 skipped (floor 943), scripts 229 (floor 161); `go test -race -count=1 ./scripts/` exit 0, 229/0/0.
- Pushed once: PR https://github.com/yegamble/vizra-core/pull/10, head 62d16aa773a2db4414bc2f96b3381c732e2ebf88. State READY_FOR_REVIEW. CI BLOCKED (Actions billing), not re-run.
- Next action: independent verifier re-runs `bash docs/evidence/hardening-b5/demo.sh <out>` in a clean clone of the head and the lanes above; whichever of core #8 / #10 merges second re-pins the Makefile in the same merge.

### 2026-09-23 — fix round 1 (PR#10 VERIFY FAIL at 62d16aa) — READY_FOR_REVIEW
- One commit 08a59a91a6dcc91c2346bcb206d4c0ad8603e90e on 62d16aa (scripts/ tree 70d09e55…). Pushed once; CI refused (billing).
- F1 BLOCKER fixed: single `make -q <all pinned>` probe; test `TestAMakefileMakeWouldRemake…/an_included_makefile`; D6 HELD, C7 (per-file probe) BROKEN→HELD, 3.81 + 4.3.
- F2 wording fixed everywhere (-q runs no ORDINARY recipe; `+`/`$(MAKE)` lines still run; only from pinned bytes).
- F3: new `scripts/makefile_pin.py` shared by anchor and check 11; 5 new makefilepin fixtures; P1 shows exit 0 at 62d16aa vs 1 now; C8 red.
- F4: text checks run before make; 16 makeguard fixtures now assert make not started; `missing-prerequisite` keeps resolver path; C9 red.
- Lanes: make ci exit 2 ONLY from internal/fixtures 10m timeout (TestManifestDetectsEveryClassOfDrift, load ~360); `go test -race -timeout 20m ./internal/fixtures/` ok 409s; direct unit + report 1157/0/0; scripts 237/0/0; both anchors 0; ci-required-guard 0; 4.3 container anchors/guard 0.
- ubuntu:24.04 was already present this time (used by another container c831a8268ca2); not removed.
- Next: independent re-verify at 08a59a9; #8/#10 second-to-merge re-pins the Makefile.

### 2026-09-23 — fix round 2 (re-verification FAIL at 08a59a9, R1-F1) — READY_FOR_REVIEW
- One commit 398ac4fe2bd8a6096a24e402936ef3ab2c2238bc on 08a59a9 (scripts/ tree 7d236f17…). Pushed once; CI refused (billing).
- R1-F1: `.RECIPEPREFIX` / `.SECONDEXPANSION` refused wherever named, pre-make; computed names refused by resolver (measured -pn output 3.81/4.3). D7 HELD 3.81+4.3 (4.3 raw `make ci` exit 0 = the hole); C10/C10b BROKEN→HELD on both.
- Found + fixed (measured 3.81): pattern-specific `%: SHELL := …` bypass; expansion-produced `-` prefix bypass (`$(IGN)` with IGN := -); expansion-produced `|| true` suffix.
- R1-F2: 4 resolver-only fixtures; C11 red. NITs: unreadable pinned file named; make -q exit 2 named; directory pin named.
- Lanes: make ci 0; direct unit + report 1206/0/0 (scripts 286); scripts 286/0/0; anchors 0/0; guard 0; 4.3 all 46 fixtures as on 3.81.
- ubuntu:24.04 was present before and used by other agents' containers; not removed. Next: independent re-verify at 398ac4f.

### 2026-09-23 — slice B5b (LOCAL ONLY, not pushed; chair: push after #10 merges)
- Branch `chore/m0-anchor-special-targets` from 398ac4f; local commit 29387da9dcb4b6bd842396a5d01857f10de7a856 (scripts/ tree 6e3ed51e…). No upstream, no PR.
- R2-F1: `.IGNORE`, `.DEFAULT` (whole word; `.DEFAULT_GOAL` untouched), `.EXTRA_PREREQS` refused pre-make; resolver backstops for computed names. First measurement (3.81 + 4.3, measure.sh): `.IGNORE:`/`.IGNORE: ci`/computed → raw `make ci` exit 0 over a failing stub. Bare `.IGNORE:` also sets `i` in MAKEFLAGS (already caught at 398ac4f); `.IGNORE: ci` was the hole (C15b: anchor exit 0 on both versions).
- R2-F2: every gate-closure target must have one explicit rule and be .PHONY (text pre-make; make's own .PHONY list post-make); pattern rules refused; `$(MAKE)` in gate recipes refused. Measured: phony targets skip pattern/.DEFAULT rules on 3.81 and 4.3.
- R2-F3: AGENTS.md control-matrix row rewritten with the review residual.
- Lanes: make ci 0; unit+report 1230/0/0 (scripts 310); scripts 310/0/0; anchors 0/0; guard 0; 4.3: 57 fixtures 55 red / 2 green.
- Next: when chair says #10 merged → rebase onto main, re-pin Makefile if it changed, push, open PR.
- 2026-09-23: chair asked for early verification. Pushed `chore/m0-anchor-special-targets` at 29387da unchanged; draft PR https://github.com/yegamble/vizra-core/pull/11, stacked on #10 (base chore/m0-anchor-makefile-digest). CI not re-run (billing). After #10 merges: rebase onto main, re-pin if the Makefile changed, push, re-confirm.
- 2026-09-23 #11 fix round 1 (X-1 + B5c): one commit 5488eb0e23940a376ea333c483d9af3a71b5ba14 on 29387da (scripts/ tree 173c57f1…), pushed fast-forward. Inline `;` recipes, multi-target rule lines, `$`-named closure prerequisites and `.POSIX` refused pre-make; post-make scan of every closure recipe from make's -pn database. Lanes: make ci 0; unit 1247/0/0 (scripts 327); anchors 0/0; guard 0; demo 3.81 all D HELD, C15–C26 red→green; 4.3: 62 fixtures 60 red / 2 green, C22/C24/C25/C26 anchor passes when removed. ubuntu:24.04 was absent this time, pulled, then removed by exact name.
- 2026-09-23 #11 fix round 2 (R1-1, R1-2): one commit 0243f2ebf4b97d047acf8e3967924a8dd5c5d748 on 5488eb0 (scripts/ tree 4be7543e…), pushed fast-forward. Computed rule targets refused pre-make; parse_database (markers-only, duplicates, unreadable); check_db_recipes fail-closed + recipe equality; check_db_closure equality; db-scan-probe.py (15 rows). Lanes: make ci 0; unit 1252/0/0 (scripts 332); anchors 0/0; guard 0; 3.81 demo C15–C32 red→green; 4.3 D rows HELD, C22–C25/C27–C32 red→green, 62 fixtures 60/2. ubuntu:24.04 absent before, pulled, removed by exact name.
- 2026-09-23 #11 PASS at 0243f2e (local; CI BLOCKED). Carried SHOULD R2-1 prepared LOCALLY, NOT pushed: commit bc8df3aa75c6a1245a9268410c3d8a188f5c991a on 0243f2e (branch ahead 1) — doubled the backslash at make-integrity-guard.py:139 (only invalid escape in scripts/*.py and scripts/testdata/*.py), new TestEveryPythonScriptCompilesWithWarningsAsErrors (python3 -W error compile of all 7 files); red/green in docs/evidence/hardening-b5/b5b/R2-1-invalid-escape.txt. NIT R2-3 not done. Next (when chair says #10 merged): rebase onto main (R2-1 stays its own commit), re-pin Makefile if changed, run lanes, push, re-confirm.
- 2026-09-23 #10 re-pin after core #8 (billing fixed): on chore/m0-anchor-makefile-digest merged origin/main (f1972e8) with NO conflicts (AGENTS.md, README.md, Makefile, scripts/test-floors.json auto-merged) → merge 60c70c3; separate re-pin commit 33b951aed7db3137024f0247c6241425737846b2 (Makefile e7cc357c… → ad681247…, only that line). Pre-repin the anchor refused the merged tree by name with 0 make processes. Lanes on 33b951a: anchor wf/lenient 0/0 (18 make runs, pinned bytes); ci-required-guard 0; make ci 0 (test-race 17 ok, 8 no test files, 0 FAIL); unit+report 1281/0/0 (floor 1006, 17 pkgs; scripts 286, ownerclaim 19); go test -race ./scripts/ 286/0/0. Pushed fast-forward (no force); CI started (pending), not re-run by me. #11 untouched (local bc8df3a still unpushed).
- 2026-09-23 #10 MERGED as 36a72df. #11 brought onto main: base retargeted to main; merge f7b6956 (6 git conflicts from the squash's older merge base eeeea06, all resolved as 3-way merges on the true fork 398ac4f, no residual; 4 spurious, pinned-makefiles.yml + AGENTS.md real and combined; patch-id verified); R2-1 kept as own commit bc8df3a; evidence 238a9ca. No re-pin (Makefile = main's, pin ad681247…). Lanes: make ci 0 (first run 2 = no space left on device while linking, infra; re-run 0), unit 1328/0/0, scripts 333/0/0, anchors 0/0, guard 0, probe 15/15, demo 3.81 D 13 HELD, C 21 red→green. Pushed 238a9cafc6c8658e4022e4f5925d218e2ecfc471 (ff); PR ready for review; CI running, not re-run.
