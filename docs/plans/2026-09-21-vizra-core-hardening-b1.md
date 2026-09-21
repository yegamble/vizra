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

(Appended below as the work lands.)

## Blockers and handoff

None at plan time. Local `make` is 3.81 and CI is 4.3; all MAKEFLAGS reasoning
stays letter-order-insensitive.
