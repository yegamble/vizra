# VERIFY — vizra-core PR #19, VZ-FOUND-003 (final budgeted verdict)

- Subject: https://github.com/yegamble/vizra-core/pull/19, head 37a6d55b6e3447902444ee7e5caeb1dd4d8078c9. Checked at start and end: unchanged, OPEN.
- Verifier: independent vizra-verifier; did not write this code. No source edits, pushes, merges or CI re-runs.
- Environment: darwin, a fresh clone in mktemp scratch (deleted afterwards). No local Docker or PostgreSQL, so the image and integration behaviour come only from CI logs I read myself.

## Commands
| Command | Exit | Result |
|---|---|---|
| `git diff origin/main...HEAD --stat` | 0 | 2 files: docker-build.yml +54, migrate_dirty_test.go +56 |
| `git diff origin/main...HEAD -- migrations internal/migrate AGENTS.md .github/required-checks.txt \| wc -l` | 0 | 0 |
| `git merge-base --is-ancestor 32999a0 HEAD` / `bd26b16 HEAD` | 0 / 0 | both are ancestors |
| `make ci` | 0 | "make ci: all lanes passed" (sqlc-verify and migrate-lint included) |
| N2: append `// x` to the first internal/store/sqlcgen/*.go, then `make sqlc-verify` | 2 | red as required; restored |
| N1: 0006_x.up.sql `ALTER TABLE sites DROP COLUMN handle;` + down file, `make migrations-manifest`, `make migrate-lint` | 2 | "migrate-lint: FAILED"; restored, `git status` clean |
| `./scripts/ci-required-guard.sh` | 0 | — |
| `gh api commits/37a6d55/check-runs` | 0 | ci-required, append-only, build-test, cache-matrix + 2 legs, fixtures, govulncheck, docker-build: all success; image-scan failure |
| `gh run list -b main -w image-scan` | 0 | failure on main 58d658f, so it is a pre-existing red and image-scan is not in the manifest |
| `gh run download 43230273284` (head 37a6d55, success) | 0 | int-events: 1854 pass, 0 fail, 0 skip; int-shuffle: 1854 pass, 0 fail, 0 skip; TestDirtyLedgerIsReportedNotRepaired=pass in both |

## Results
- **A. Scope: PASS.** Only the two files changed. The net diff under migrations/ and internal/migrate is zero. AGENTS.md and required-checks.txt are untouched and no lane was renamed. Every `uses:` is pinned to a 40-hex SHA, and the postgres image is pinned to digest sha256:86c951e0… (the same one build-test uses).
- **B. S1: PASS.**
  - Which image: the step runs `/usr/local/bin/vizra migrate` from `vizra-core:ci`. build-push-action is called with no `target`, so it builds the last stage (`runtime`), which is the image that would ship. The repo has no release workflow, so reading this as "the release image" is reasonable.
  - Empty database: asserted (public table count = 0).
  - Fails closed: `set -euo pipefail` with `migrate | tee` means a non-zero exit fails the step even if the expected text was printed. A missing binary fails the same way.
  - Version prefix: `grep -q "APPLIED to version $head"` would also match 50 when $head is 5. That does not cause a false green, because the ledger check that follows is an exact `= "$head false"`, and it runs on both runs.
  - Run 2 asserts "current at version" plus the exact ledger value.
  - CI: red job 131221389383 is on 32999a0, an ancestor of the head; the conclusion is failure and the log contains `TABLEE`. Green job 131223440387 is on 37a6d55: "head version 5", "ledger: 5 false" twice, then "applied to 5, clean, idempotent".
- **C. R1: PASS.**
  - The test makes the real schema_migrations row dirty, then asserts that Apply returns an error containing "dirty at version N", applied=false, version unchanged, Probe reports StateDirty, and the raw row is still dirty.
  - Build tag is `integration`. The build-test lane runs `go test -tags=integration -json ./...` in both ordered and shuffled order, and `go-test-report.py` fails on any skip that is not allowlisted. Silent skipping is therefore impossible, and the artifact shows 0 skips.
  - Red: job 131217791460 on mutation bd26b16 (an ancestor) shows `migrate_dirty_test.go:30 … it must refuse`. Green: run 43230273284 on 37a6d55.
- **D. S2, N1, N2: PASS** (see the command table).
- **E. CI: PASS.** ci-required succeeded with headSha = 37a6d55.
- **F. Compatibility window: judgement for the ledger, not a blocker.** No window mechanism exists. migrate-lint rejects destructive statements in every up file, which is a superset of rejecting them inside a window. The one gap is the `-- allow-destructive:` marker, which can let a destructive statement in regardless of any window. The outcome is satisfied as written only if the ledger records that the marker is a reviewed exemption. Recommendation: record IMPLEMENTED with that caveat, and add a FOLLOW-UP for window-aware exemption checking.

## Findings
- BLOCKING: none.
- FOLLOW-UP (vizra-core):
  1. The S1 grep could be anchored, e.g. `version $head\b`. Cosmetic only, because the exact ledger check already covers it.
  2. The `allow-destructive` marker is not checked against any compatibility window.
  3. image-scan is red on main. It was red before this PR and is outside the manifest.

## Per-case
| Case / clause | Proven by |
|---|---|
| S1 migrate up from the release image on an empty DB | docker-build job 131223440387 (green, 37a6d55); red control 131221389383 |
| S2 sqlc-verify passes | `make ci` locally; build-test on 37a6d55 (run 43230273284) |
| N1 DROP COLUMN fails migrate-lint | local mutation, exit 2 |
| N2 sqlcgen edit fails the drift check | local mutation, exit 2 |
| R1 dirty ledger reported, not repaired | TestDirtyLedgerIsReportedNotRepaired, pass ordered and shuffled in run 43230273284; red control job 131217791460 |
| append-only | append-only lane success; manifest check inside migrate-lint |
| down files where safe | migrate-lint checks for down files (make ci) |
| compiled into the release binary | S1 runs the embedded migrations from the runtime image; `migrate.EmbeddedVersion` |
| sqlc drift-checked | S2 and N2 |
| compatibility window | see F: superset delivered, with the marker caveat |

**IMPLEMENTED:** yes, after merge.

**VERIFIED:** supportable. The CI logs that evidence_required asks for:
- sqlc-verify and migrate-lint: build-test in run 43230273284 on 37a6d55. These checks run under make ci, so I proved them locally rather than by reading that job's step log.
- migrate up on an empty DB: job 131223440387.

## Not run
- Local Docker and PostgreSQL (not available).
- `shellcheck` (no shell files changed).

FINAL VERDICT: PASS — SHA 37a6d55b6e3447902444ee7e5caeb1dd4d8078c9
