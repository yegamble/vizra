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


---

# Fix round 1 of 2 — the verifier returned FAIL at `e710c3c`

`docs/evidence/warroom/2026-09-21-vizra-core-pr9-hardening-b1-VERIFY.md`.
Most of round 1 reproduced; it failed on ONE class: both residual lists were
declared **EXHAUSTIVE** and **thirteen** evasions left both guards green and
were on neither list.

## The chair's ruling, and what it changed

The defect is a CLASS — a blacklist tokeniser over arbitrary shell cannot be
exhaustive — so the control was **INVERTED to default-deny on the SHAPE** of the
steps that carry the gate. The tokeniser is kept only to produce a friendlier
message; it decides nothing.

| # | Ruling | Implementation |
|---|---|---|
| 1 | a make step's `run:` must be byte-equal to a committed literal | `.github/pinned-steps.yml` `make_steps` (8 bodies); check 8b |
| 2 | such a step may carry only `name`/`run`/`id`; job/workflow `env` family, `defaults.run`, `container:` refused | check 8b keys; `check_job_surroundings`. `timeout-minutes` **refused** — it can only make a step fail sooner, but nothing uses one and an unused key is surface for no benefit |
| 3 | the anchor ADJACENT to every make step, and asserting its own process | 4 new anchor steps; `check_environment` is now default-deny (unset, not "free of flags I recognise"), plus MAKEFILES/BASH_ENV/ENV, SHELL sanity, and `make` resolving to a real program in a system directory |
| 4 | pin the DIRECT test steps; `go test`'s own exit must fail the step without the report line | `direct_test_steps` (3 bodies) ending `|| exit 1` and `exit "$rc"`; check 9 pins them |
| 5 | per-package floors for EVERY package in both suites | `scripts/test-floors.json`, generated by `go-test-report.py --emit-floors`; a package that RUNS with no floor is refused |
| 6 | D6 truthfulness | new stub `broken-probes-1-3`; D6 rewritten |
| 7 | `_why` numbers from the tool | done |
| 8 | delete EXHAUSTIVE and "the whole remaining residual" | done; both replaced by what the guard IS and CANNOT do |

**Beyond the ruling — check 8c, the positive half.** Pinning a shape does not
stop a step being DELETED or replaced by an indirection no classifier can see
(`M=make; $M -i ci`, `${MAKE:-make}`). `pinned-steps.yml` now also records, per
job, the invocations that MUST be present byte-equal. That closes the
indirection class without parsing shell, because it does not care what replaced
them.

## The verifier's entire evasion table, re-run

`vizra-core/docs/evidence/hardening-b1/R1-evasion-table.txt`, produced by
`evasion-table.py` (committed). Each row is substituted into a COPY of the real
`.github/` tree; the harness aborts unless the digest moved; the repository is
never modified.

**45 attack rows — every one RED, each by a named rule.** That includes all
thirteen that were GREEN-and-UNLISTED, and `A7`/`A11`, which do not actually
neuter make but are refused anyway because the shape is pinned.

Three honest counter-rows are GREEN and named in the residuals:

| row | what | status |
|---|---|---|
| R1 | a wrapper script ADDED early in the job (not replacing a pinned step) | GREEN — REVIEW-ONLY, named |
| R2 | an arbitrary EARLY step rewrites a test file on disk | GREEN — REVIEW-ONLY, named |
| R3 | an arbitrary EARLY step writes `MAKEFLAGS` to `$GITHUB_ENV` | GREEN at the guard, **RED at the anchor at runtime** (adjacency) |

## Other round-2 transcripts

- `R2-anchor-environment.txt` — the anchor's own assertions. `MAKEFLAGS=-i`,
  `MAKEFLAGS=--no-such-flag` (which a blacklist would pass), GNUMAKEFLAGS,
  MFLAGS, MAKEFILES, BASH_ENV, ENV, a neutered SHELL, a `$GITHUB_PATH` stub
  `make`, and an exported `make` function — **all exit 1**.
- `R3-direct-step-exit.txt` — FINDING 6. Planted `t.Fatal`: step as pinned
  **exit 1**; report line deleted **exit 1** (was 0 at `e710c3c`); main's shape
  exit 1. Both mutations also red statically.
- `D6-docker-run-failure.txt` — rewritten. Main's step against `broken`
  **exits 125** (the verifier is right, my first transcript was wrong); against
  `broken-probes-1-3` it prints all three reassuring lines and **exits 0**.

## Session restart (2026-09-22) — re-oriented from disk

Machine restarted mid-round. `git status` on `chore/m0-hardening-b1` @ `e710c3c`:
58 modified, 2 deleted (`guard/step-env-makeflags/`, superseded by
`guard/make-step-env/`), 33 untracked — the whole round-2 redesign was on disk,
uncommitted. Two stray artefacts at the repo root (`unit-events.json`,
`unit-exit.txt`, left by an earlier verbatim run of the pinned step) were
deleted, not committed. `/tmp` was cleared by the reboot, so both suites were
re-measured for the final floors rather than reusing pre-restart numbers.
Containers restarted by name: `vzb2-pg`, `vzb2-cache` (this round's prefix;
no `vzb1-*` containers remained). `vizra-m1a-*` and `vidra-*` untouched.

Correction to an earlier number: a pre-restart measurement set the `scripts`
package floor at 171 from a run in which the migrate-lint test table had been
clobbered by the guard table (65 subtests instead of 15). After restoring it,
`scripts` runs 151 and the per-package floor went RED while the whole-suite
floor (1071 ≥ 953) stayed green — FINDING 7's property, observed live on my own
mistake. Floors are regenerated from the post-restart measurement.

## Round 2 committed and pushed (2026-09-22)

| | |
|---|---|
| commits | `8fa04b1` (redesign: guard, anchor, report, pins, 65/12/6 fixtures, workflows, docs) · `6b65eff` (evidence) — on top of `e710c3c`, no amend, no force-push |
| head | `6b65eff6ee29e99e1b93b01242b4c97d90a57267` |
| PR | https://github.com/yegamble/vizra-core/pull/9 — body replaced with the round-2 account |
| attribution | commits carry `Co-Authored-By: Claude Opus 5.5 (1M context)` per the harness attribution in force after the restart (round 1 carried Fable 5.1 per the brief) |

Local at `8fa04b1`: `make tidy-check` 0 · `make ci` 0 · `make build` 0 · both guards 0 ·
unit report 0 (1071, 0 skips, floor 910) · integration report 0 (1116, 0 skips, floor 949;
internal/integration 45 ≥ 40) · `go test -race -count=3 ./scripts/` 0.

Runtime: fixture subtests now run in parallel — `scripts` under -race went 53s → 13s locally,
because it runs twice in build-test (make ci's test-race and the direct unit step).

Cleanup: `vzb2-pg`, `vzb2-cache` removed by name; scratch copy for R4 removed.

## CI on `6b65eff` — every required lane green

ci-required success 11m22s · build-test success **11m17s** (was 11m03s; timeout 20, unchanged) ·
cache-matrix 5s (legs 4m51s/5m01s) · docker-build 2m48s · fixtures 2m01s · govulncheck 36s ·
append-only 7s · GitGuardian 20s · image-scan failure (not required; exit 1 findings, 48 HIGH).
Fan-in `all 6 required check(s) succeeded` on head 6b65eff. CI counts: unit 1071/0 skips,
integration 1116/0 skips (×2 incl. shuffled), internal/integration 45. New controls' ok
lines present in the CI log for every make-running lane. State: READY_FOR_REVIEW; next action
is the independent verifier at 6b65eff.

# Fix round 2 of 2 (the last) — the verifier's re-verification FAIL at `6b65eff`

`docs/evidence/warroom/2026-09-21-vizra-core-pr9-hardening-b1-VERIFY.md`, section
"Re-verification at 6b65eff". The anchor was weak two ways: recognised by substring
(R-1, N1–N4) and lenient whenever MAKELEVEL was present (R-2).

| # | Fix | Where |
|---|---|---|
| R-1 | anchor pinned: `anchor_step: ./scripts/make-integrity-guard.sh --workflow`; the step before each make step must BE it; a look-alike is refused anywhere | `pinned-steps.yml`, `step_is_the_anchor`, `check_job_surroundings`; 8 workflow anchors updated |
| R-2 | mode chosen by `--workflow`, never by env; strict = MAKEFLAGS family unset, make recipe vars absent; lenient = measured allowlist (Make 4.3 in `ubuntu:24.04`, 3.81 host); MAKELEVEL & co. refused as job/workflow env | `check_environment`, `DANGEROUS_ENV_NAMES` |
| (mine) | `?=` variables (`GO`, `SQLC`, `GOFLAGS`, `RELEASE`, `COMMIT`, `BUILT_AT`) refused in strict mode and as job/workflow env — `GO=true make test-race` exits 0 over a failing test | `check_environment_overrides`, `MAKEFILE_ENV_NAMES`; `R5-makefile-env-override.txt` |
| R-4 | duplicate YAML keys refused | `_NoDuplicateKeysLoader` |
| R-5 | real file must be named make; ok line states only what is checked | `check_make_resolves_to_a_real_program` |
| R-3 | AGENTS.md, both docstrings, pinned-steps.yml, README, COMMANDS, PR body restated | |

Commits `fc4885b` (code), `d435cd8` (evidence) on top of `6b65eff`; head `d435cd8`.
Fixtures 75 (+10). Evasion table at `fc4885b`: static 57 rows / 54 red / 3 named
counter-rows; runtime 13 rows / 11 red / green = control + GOTOOLCHAIN (stated boundary).
Local at the working tree: tidy/ci/build 0, both guards 0, `make ci-guard` (plain, -j2, -s) 0,
`go test -race ./scripts/` 0. Host load average ~250 (other agents) — local timings unreliable.
Cross-PR: PR #8's `internal/audit`, `internal/credential`, `internal/ownerclaim` need floors in
BOTH suites from whichever PR merges second; stated in the PR body. Not added here.

CI on `d435cd8`: every required lane green (build-test 10m32s, ci-required 10m03s), but it
measured unit **1109** / integration **1154** (scripts 189), disproving my PR-body sentence
"counts unchanged from round 2 (1071/1116)" and staling test-floors.json `_why` (the FINDING 8
class). Corrected in `e2a3e01`: `_why` and COMMANDS take CI's numbers; floors raised with the
same generator formula (never lowered): suite 910→943 / 949→981, `scripts` 128→161. PR body
carries an explicit correction paragraph. Head `e2a3e01`; waiting on CI.

## CI on `e2a3e01` — every required lane green (final head of fix round 2)

ci-required 11m23s · build-test **11m13s** · cache-matrix 4s (legs 4m33s/5m05s) · docker-build 3m09s ·
fixtures 1m49s · govulncheck 30s · append-only 7s · GitGuardian 1s · image-scan failure (not required;
exit 1 findings, 48 HIGH / 179). Fan-in `all 6 required check(s) succeeded` on `e2a3e01`. CI counts:
unit 1109 (floor 943), integration 1154 ×2 (floor 981), internal/integration 45, scripts 189 (floor
161), 0 skips. 7 strict `--workflow` anchor passes plus 1 ci-guard (allowlist) pass. State:
READY_FOR_REVIEW; next action is the same verifier at `e2a3e01`.
Cleanup: `ubuntu:24.04` image I pulled removed by name; no containers of mine remain; scratch removed.
