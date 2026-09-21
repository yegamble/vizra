# Execution plan: vizra-core hardening sweep B1 — the CI gates cannot be silenced from a workflow line, and cannot pass vacuously

## Context

| | |
|---|---|
| Repo | `vizra-core` (`yegamble/vizra-core`), main checkout |
| Base | `main` @ `5eb2829eb4f830206029f8e2a836f93a44a93a02` |
| Branch | `chore/m0-hardening-b1` |
| Concurrent writer | `core-m1-owner-claim` worktree owns `migrations/`, `internal/`, `api/`, `cmd/vizra`. **This slice adds no migration and touches nothing under `api/`, `internal/` or `cmd/`.** |
| Host | darwin/arm64, GNU Make 3.81, go1.27.1, python3 3.9.6 + PyYAML 6.0.3, Docker 29.8.0, sqlc v1.31.1 |
| Acceptance platform | CI `ubuntu-24.04` (GNU Make 4.3) |

Findings being closed, each with a measured reproduction at the base before any change:

* PR#6 VERIFY — FINDINGS 1, 2, 3, 4 and (re-confirmation section) FINDING 6.
* PR#7 VERIFY — FINDINGS 1 and 2, and "CI cannot corroborate the zero-skip count
  because no lane runs `-v`".

## Acceptance

1. A floor lane's make step cannot be no-opped from the workflow line — flags,
   variable overrides, and a MAKEFLAGS-family `env:` at step/job/workflow level.
2. Checks 3, 4 and 8 run over `set(FLOOR_LANES) | set(required)`.
3. The direct `go test` lane FAILS on zero tests, and CI corroborates test and
   skip counts from machine-readable output, with an executed-test floor and a
   named skip allowlist. Same for the integration suite.
4. A REQUIRED lane invokes the integration suite directly, without make.
5. `append-only` gains a provenance step, with a control.
6. docker-build's image assertions cannot pass on a `docker run` FAILURE.
7. `image-scan-verdict.py` refuses an empty or unknown `--fail-on`.
8. Docs at exactly the strength of the controls; the EXHAUSTIVE residual lists
   stay true.

**Non-goals** (queued elsewhere): healthcheck follow-ups (probe body check,
`--timeout` clamp, monotonic-clock pin, saturated-worker signal),
`internal/obs` redaction review, `vizra setup`, compose, the base-image CVE
decision.

## Implementation

No migration, no `api/` change, no `internal/` change, no `cmd/` change.

| File | Change |
|---|---|
| `scripts/ci-required-guard.py` | checks 3/4/8 over floor ∪ required; new check 8b (make argv + `env:`); new check 10 (provenance step on any checked lane that checks out) |
| `scripts/go-test-report.py` | NEW — judges `go test -json`: floor on executed tests, skip allowlist, counts printed |
| `scripts/test-floors.json` | NEW — the committed floors and the (empty) skip allowlist |
| `scripts/assert-runtime-image.sh` | NEW — docker-build's three image assertions, with `docker run` failures fatal; `$DOCKER` injectable so it is testable with no daemon |
| `scripts/image-scan-verdict.py` | refuse an empty `--fail-on` |
| `.github/workflows/build-test.yml` | provenance on `append-only`; unit + integration suites run directly with `-json` and the report script; make runs the rest |
| `.github/workflows/docker-build.yml` | call `assert-runtime-image.sh` |
| `scripts/scripts_test.go`, `scripts/imagescan_test.go` | fixtures wired into the required `scripts` package |
| `scripts/testdata/guard/*`, `scripts/testdata/gotest/*`, `scripts/testdata/fakedocker/*` | NEW fixtures |
| `AGENTS.md`, `README.md`, `docs/quality/COMMANDS.md`, both guard docstrings | docs at control strength |

## Verification

Focused: `go test -race -count=1 ./scripts/`.
Full: `make ci`, `make tidy-check`, both guards, both integration lanes, and CI.

Every *demonstrated* bullet uses `docs/evidence/hardening-b1/mutate.sh`, which
aborts unless the mutation's digest moved and the restore is byte-identical.

## Progress and evidence

### Baselines measured at `5eb2829` BEFORE any change

`docs/evidence/hardening-b1/B0-baseline-four-spellings.txt`,
`B0-baseline-items-2-3-5-7.txt`.

| Defect | Measured at base |
|---|---|
| `run: make -i ci` | both guards EXIT 0 |
| `run: make SHELL=/usr/bin/true ci` | both guards EXIT 0 |
| `run: make MAKEFLAGS=-i ci` | both guards EXIT 0 |
| step-level `env: MAKEFLAGS: -i` | both guards EXIT 0 |
| required-but-not-floor `extra-lane` (`continue-on-error: true` + `run: make -i ci`, no anchor, no `pull_request`) | guard EXIT 0; only line: `ok required check 'extra-lane' resolves to a job` |
| 23 `*_test.go` moved aside, `go test -race -count=1 ./...` | **EXIT 0**, 22 packages `[no test files]` |
| `image-scan-verdict.py --fail-on ''` over the `findings` fixture (1 CRITICAL) | **EXIT 0**, "found nothing at or above []" |
| `--fail-on ','` | EXIT 0 |
| `append-only` job | `checkout=True provenance=False` |

### Implemented at `6b25fc5` (branch `chore/m0-hardening-b1`)

All eight items implemented. No migration, no `api/` change, no `internal/`,
`cmd/` or `migrations/` change — verified by `git diff --stat`.
`.github/required-checks.txt` and `FLOOR_LANES` are byte-identical to `5eb2829`
(D8): **no required lane was added or renamed.**

### Demonstrations — every one red against a controlled mutation, green restored

The harness `vizra-core/docs/evidence/hardening-b1/mutate.sh` records the target
file's sha256 before and after, **aborts if the mutation did not apply**, runs
the check, restores **from a byte copy** (not `git checkout --`, which restores
from the index and destroyed this branch's own uncommitted workflow edits on the
harness's first run — recorded in the script's own header), and **aborts if the
restore is not byte-identical**.

| Transcript | Item | Result |
|---|---|---|
| `D1-workflow-line.txt` | 1 | 16 mutations, **all exit 1**; the verifier's four spellings, plus `make ci SHELL=…` (after the target), `--ign` and `--dry` (long-option abbreviations), `-srik` (a cluster), `-f`, `-C`, `bash -c "make -i ci"`, `env MAKEFLAGS=-i make ci`, `… && make --keep-going ci`, step/job/workflow `env:`, and an untokenisable `run:`. Control 0 before and after. |
| `D2-required-not-floor.txt` | 2 | the verifier's `extra-lane`: **five separate FAILs** where the baseline printed one `ok … resolves to a job` |
| `D3-zero-tests-and-skips.txt` | 3 | 23 `*_test.go` moved aside → `go test` **exit 0**, report **exit 1** ("only 0 test(s) executed; floor 900"). A planted `t.Skip` → `go test` **exit 0**, report **exit 1** naming the test. |
| `D4-integration-without-make.txt` | 4 | direct integration lane green (1092 executed, 0 skipped); deleting it → guard red; emptying `internal/integration` → **suite floor still clear (1047 ≥ 940) but the per-package floor red** |
| `D5-provenance.txt` | 5 | every checked lane that checks out has an unconditional provenance step; mismatched head **exit 1**, pinned-to-head (no `HEAD^2`) **exit 1**, correct **exit 0**; deleting the step → guard red |
| `D6-docker-run-failure.txt` | 6 | the old inline shape, run verbatim against a stub daemon that exits 125: **exit 0, "no build tooling on PATH"**. The new script: **exit 1**, "the container did not run". |
| `D7-fail-on.txt` | 7 | `--fail-on ''`, `','`, `' , '`, `',,'` all **exit 3** (was 0 over a CRITICAL); `HIGH,SEVERE` exit 3; `HIGH,CRITICAL` exit 1 |
| `D8-manifest-floor-agreement.txt` | hard rule | manifest ≡ FLOOR_LANES, unchanged from main; three disagreement mutations all red; an orphaned guard fixture is red |

### Local lanes at `6b25fc5`

darwin/arm64, GNU Make 3.81, go1.27.1, python3 3.9.6 + PyYAML 6.0.3, sqlc
v1.31.1, Docker 29.8.0. Services: my own `vzb1-pg` (55611) / `vzb1-cache`
(63911), removed by name at the end. **Not the ADR-009 acceptance platform.**

| Command | Exit | Detail |
|---|---|---|
| `make ci` | 0 | 10 lanes; 14 ok, 8 `[no test files]`, 0 FAIL |
| `make tidy-check` | 0 | |
| `make build` | 0 | |
| `./scripts/make-integrity-guard.sh` | 0 | `passed (8 gate target(s))` |
| `./scripts/ci-required-guard.sh` | 0 | `passed (6 required check(s))` |
| unit suite + report | 0 | **1047 executed, 0 skipped**, floor 900 |
| integration suite + report | 0 | **1092 executed, 0 skipped**, floor 940; `internal/integration` 45, floor 40 |
| `make test-integration` | 0 | 15 ok, 0 FAIL — the recipe `cache-matrix` still uses |
| `make test-integration-shuffle` | 0 | **exit code only.** I deleted its log during container cleanup before the counts were read, so the per-package tally is UNVERIFIABLE locally. Both `cache-matrix` legs exercise both recipes on this head in CI; that is the authoritative evidence for them. |

### Pushed

| | |
|---|---|
| Branch | `chore/m0-hardening-b1` |
| Head | `e710c3cff18bd63c87a692937b608fa762627d99` |
| Commits | `6b25fc5` (the slice), `e710c3c` (evidence, COMMANDS, the denylist-red reason) |
| PR | https://github.com/yegamble/vizra-core/pull/9 |
| State | **READY_FOR_REVIEW** — not verified, not merged |

All five `uses:` pins re-confirmed against the live repositories with
`gh api repos/<owner>/<repo>/commits/<sha>`; `if-no-files-found: warn` read from
`actions/upload-artifact`'s own `action.yml` at the pinned SHA
`043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`.

### CI on `e710c3c` — every required lane green, on this SHA

| lane | conclusion | duration |
|---|---|---|
| `ci-required` | **success** | 11m26s |
| `build-test` | success | **11m03s** |
| `cache-matrix` (+ both legs) | success | 3s (legs 5m06s / 5m03s) |
| `docker-build` | success | 3m36s |
| `fixtures` | success | 2m14s |
| `append-only` | success | 5s |
| `govulncheck` | success | 39s |
| GitGuardian Security Checks | success | 1s |
| `image-scan` | **failure — by design, NOT required** | 3m31s |

Fan-in: `ci-required-guard: passed (6 required check(s))` then `SUCCESS` observed
for each of the six, `all 6 required check(s) succeeded`.

**CI now corroborates the counts** (the PR#7 note closed):

```
unit          1047 executed, 194 top-level, 1047 passed, 0 failed, 0 SKIPPED   floor 900
integration   1092 executed, 225 top-level, 1092 passed, 0 failed, 0 SKIPPED   floor 940
              internal/integration: 45 test(s), floor 40
integration (shuffled)  identical: 1092 / 0 skipped / 45
```

Identical to the local numbers. The `build-test-events-<sha>` artifact carries
the raw `go test -json` streams so a verifier can re-derive them.

**Timing, before → after.** `build-test` **11m03s** against the verifiers'
baseline of 10m59s (PR#6) and 11m08s (PR#7), of an **unchanged 20-minute
timeout**. The restructure is runtime-neutral as intended: the direct integration
steps (117s + 115s) replaced the recipe invocations that stood there, and the
unit step (112s) replaced the bare `go test` step. No timeout was raised.

**`image-scan` red is the pre-existing upstream CVE red, not this slice.** It
exited **1 (findings)**, not 3 (no valid scan), with `--fail-on HIGH,CRITICAL`
and **48 HIGH / 175 TOTAL** — the same numbers PR#7's verifier confirmed. The
verdict's own gate chain ran (`ok the scanner exited 0`), so the new `--fail-on`
refusal did not break the valid path. The lane is deliberately not required.

### What did NOT run

- **`docker-build` / `image-scan` were not run locally** — arm64 host, CI builds
  linux/amd64. `assert-runtime-image.sh` was exercised against stub daemons,
  never a real image.
- **GNU Make 4.3 was not exercised locally** (3.81 here). The CI log is the 4.3
  evidence; all MAKEFLAGS reasoning is letter-order-insensitive.

## Blockers and handoff

No blockers. The remaining gate is an independent verifier plus `ci-required`
green on `e710c3c`.

**Residual, as it now stands** (both guards' EXHAUSTIVE lists say exactly this):

1. A **wrapper script**, a **`uses:` composite action**, or a **reusable
   workflow** that calls make carries no `make` token on the workflow line, so
   neither guard reads its argv and neither demands the anchor. REVIEW-ONLY.
   This is the whole remainder of the one-word evasion.
2. `make ci`'s own `test-race` and both `cache-matrix` legs still run a
   non-verbose `go test`, so **their** skip counts are not readable from their
   logs. The two direct steps cover the same package set, so nothing is
   unmeasured — but the corroboration comes from those steps, not from every
   lane.
3. The floors and the skip allowlist are committed files: lowering a floor is
   made **visible**, not prevented.
4. Everything here is editable in the pull request under test, and CODEOWNERS
   remains **advisory** until the owner's ruleset exists (403 on their plan).

**Cleanup done:** containers `vzb1-pg` and `vzb1-cache` removed by name; the
`mktemp -d` scratch directory removed. Nothing named `vidra-*`, `vizra-m1a-*`
or `vzv8-*` (other agents') was touched; no global prune.
