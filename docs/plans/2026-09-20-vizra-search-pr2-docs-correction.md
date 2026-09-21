# vizra-search PR #2 — docs-only correction (chair re-plan)

Slice: correct the overstated guarantee blocking the merge of
https://github.com/yegamble/vizra-search/pull/2 (verifier PASS at `7babbd3`,
merge condition OPEN — FINDING 8).

- Repo: `yegamble/vizra-search`, branch `chore/revendor-core-main`
- Base for this round: `7babbd396a1fcf1a2940c45a8eeeb9d9d2854331` (clean tree confirmed)
- Acceptance: FINDING 8 acceptance criteria in
  `/Users/yosefgamble/github/vizra/docs/evidence/warroom/2026-09-20-vizra-search-pr2-revendor-VERIFY.md`
- Constraint: **docs only.** No recipe line, no Python statement, no Go code, no workflow key.

## What is false today

1. Claim A — "What one edit to `/Makefile` can no longer do: leave the
   `contract-drift` CI job green with a vendored file edited in place."
   Falsified by `SHELL := /usr/bin/true` and by `MAKEFLAGS += -i`, each one line.
2. Claim B — the residual's backstop, "`test` and `test-noskip` run `go test`
   directly". False for CI: the workflows run `make test` / `make test-noskip`,
   which are make recipes and are no-opped by the same edit. Only a direct
   `go test ./internal/httpapi/` goes red, and no CI lane runs that.
3. `MAKEFLAGS += -i` is named nowhere except `cmd_workflow`'s docstring.

## Files to correct

- `scripts/contract-drift-guard.py` — module docstring (Claim A + residual list)
- `AGENTS.md` — the same two paragraphs
- `Makefile` — the `contract-drift` comment block that points at AGENTS.md
- `docs/evidence/pr2/README.md` — the `F5-F6-round3…` row, plus a correction note
  for the `>>> RESIDUAL` annotation inside that transcript (the transcript itself
  is recorded evidence and is not rewritten)

## Steps

1. Re-measure `SHELL :=` / `MAKEFLAGS += -i` / `.SHELLFLAGS` in a scratch clone.
2. Rewrite the passages so each sentence is exactly true; name the queued
   cross-repo hardening item.
3. `git diff --stat` must show only those four files; `git diff` must contain no
   executable line.
4. `make ci`, `./scripts/contract-drift-guard.py recipe|workflow`,
   `./scripts/ci-required-guard.sh` — counts must still be 347 pass / 0 skips and
   `324 tests ran … none deselected`.
5. Commit, push (no force), wait for CI on the new head.

## Evidence

Appended below as it is produced.

### Re-measurement (scratch clone at `7babbd3`, darwin/arm64, GNU Make 3.81, go1.27.1)

Each mutation one line in `/Makefile`, each with a vendored file edited in place
(sha256 printed before/after, so a mutation that failed to apply could not pass
as green):

| `/Makefile` edit | `make contract-drift` | guard `recipe` | `make test` | `make test-noskip` | `go test ./internal/httpapi/` |
|---|---|---|---|---|---|
| none (control, drift only) | 2 | 0 | 2 | 2 | 1 |
| `SHELL := /usr/bin/true` | **0** | 0 | **0** | **0** | 1 |
| `MAKEFLAGS += -i` | **0** | 0 | **0** | **0** | 1 |
| `.SHELLFLAGS := -c true` | 2 | 0 | 2 | 2 | 1 |

`.SHELLFLAGS` is inert on GNU Make 3.81 (the variable landed in 3.82), so this
host cannot judge it on CI's make 4.x — it is therefore named only in the queued
hardening item and no claim is made about its current effect.

Harness + raw output:
`/private/tmp/claude-501/-Users-yosefgamble-github-vizra/7321b930-95d2-4a95-ba2e-61ef2ce3c13c/scratchpad/docfix/{measure.sh,measure-out.txt}`

### Verification after the edit (working checkout)

| command | exit | result |
|---|---|---|
| `python3 -c ast.parse(contract-drift-guard.py)` | 0 | parses |
| `./scripts/contract-drift-guard.py recipe` | 0 | `4 package(s) selected with no test-selecting flag` |
| `./scripts/contract-drift-guard.py workflow` | 0 | anchor at step 2, before `make contract-drift` at step 3 |
| `make ci` | 0 | all lanes green |
| `make contract-drift` (inside `ci`) | 0 | `324 tests ran across 4 package(s), 0 failures, none deselected` |
| `make test-noskip` (inside `ci`) | 0 | `347 pass events, 0 skips` |
| `./scripts/ci-required-guard.sh` | 0 | `6 fixtures exercised, floor 6` |

`git diff --stat`: `AGENTS.md 48+/-`, `Makefile 14`, `docs/evidence/pr2/README.md 33`,
`scripts/contract-drift-guard.py 47` — 4 files, 114 insertions, 28 deletions.
Every changed `Makefile` line begins with `#`; every changed `.py` line is inside
the module docstring (old 54-69). No recipe line, no Python statement, no Go
file, no workflow file touched.

### Commits and CI

| SHA | what | CI |
|---|---|---|
| `4cd380b10860e3f0cf295b25d47bc35229ff63ef` | `docs: state what the lane guard does and does not stop` | **12/12 pass** — build, ci-required, contract-drift, docker-build, echo-containment, fmt, GitGuardian, govulncheck, test, test-noskip, tidy-check, vet |
| `744c60719dd1feaa5786498cbc4b9c243c60843b` | `docs: narrow the coverage bullet to what check_coverage actually enforces` | **12/12 pass**, `ci-required` completed success |

The second commit is a self-caught precision defect: the first draft's bullet
said "a listed package dropped from the lane", but `check_coverage` refuses only
a package that **holds a vendored-file guard**, and `cmd_ran` refuses a listed
package that produced no result or ran zero tests. Corrected to say exactly that.

Cumulative `7babbd3..744c607`: 4 files, 116 insertions, 28 deletions — AGENTS.md,
Makefile (comment block only), docs/evidence/pr2/README.md, scripts/contract-drift-guard.py
(module docstring only).

### Out of scope, reported to the chair rather than edited

`/Users/yosefgamble/github/vizra/docs/plans/2026-09-20-vizra-search-pr2-revendor.md`
lines 319-328 (the **previous builder's** plan file, in the meta repo) repeats
the same false backstop: "The drift is still caught: `T` = 1, because the
required `test` and `test-noskip` lanes run `go test` directly." Outside this
slice's boundary; left for the chair. The meta `AGENTS.md` itself does not carry
the claim.
