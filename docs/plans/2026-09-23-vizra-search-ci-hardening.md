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
