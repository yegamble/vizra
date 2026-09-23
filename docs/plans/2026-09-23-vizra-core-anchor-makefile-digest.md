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
