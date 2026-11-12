# Verify meta PR #32: VZ-FOUND-001 bootstrap.sh (meta part)

- PR: https://github.com/yegamble/vizra/pull/32, branch `feat/found-001-bootstrap`
- Head SHA verified: `4506e815b838edf3a725d2d368410e914ce666d9` (PR head was not moved, checked with `gh pr view 32 --json headRefOid`)
- Verifier: independent (did not write this code). Clean clone in `/tmp/vzv-meta-pr32-edufEW/r` via `git fetch origin pull/32/head`, deleted after the run.
- Env: darwin/arm64, POSIX sh, shellcheck, git, python3. Nothing was installed on the host.
- Verdict budget: this is verdict 1 of 4 for VZ-FOUND-001.

## Scope note
The brief asked for "bootstrap.sh checks/pins the toolchain … refuses a wrong-version tool". That is not what this script does, and the PR does not claim it. `bootstrap.sh` clones each component and pins it to a ref, which is ledger case S2. The toolchain is pinned in CI: `setup-go go-version-file` / `setup-node node-version-file` plus `GOTOOLCHAIN=local` (validate.yml S1 steps). The ledger negative case, "unpinned toolchain fails CI", is N1. N1 belongs to the component repos and stays open. I judged the PR against the ledger cases (features.json:149-160), not against the brief's wording.

## Local results (clean clone at the SHA)
| Command | Exit | Result |
|---|---|---|
| `shellcheck bootstrap.sh tests/bootstrap/*.sh docs/evidence/bootstrap/*.sh` | 0 | clean |
| `sh tests/bootstrap/bootstrap_test.sh` | 0 | 11 passed, 0 failed, 0 skipped |
| `sh docs/evidence/bootstrap/mutation-demo.sh` | 0 | 4 RED (dirty-check→dirty-refused; ref-validation→5 bad-ref; pin-checkout→S2-ref-detached; always-checkout→R1-rerun-default), unmutated GREEN 11/11 |
| `grep -nE "brew\|apt\|npm i\|install\|sudo\|curl" bootstrap.sh` | 1 | no match: no host package installs. The script only runs `git clone/fetch/checkout/merge --ff-only` |

Own mutation (not in the builder's demo): I replaced `merge -q --ff-only "$def"` with `reset -q --hard "$def"`. The suite stayed **green** (11/11). No test covers diverged-branch refusal. See F-2.

## CI on the SHA
- `validate` run 43247962101: success. `ci-required` run 43247962119: success. The manifest `.github/required-checks.txt` lists only `validate`, the ci-required log shows `validate: success`, and that is the job that ran. Manifest and jobs match.
- In-run steps all succeeded: bootstrap tests (11 passed), mutation demo, S1 clone. The S1 rerun printed identical SHAs: core 3f1def36…, user 9f7c639c…, search 8d0c293a…, all `main`. That is R1 against the real remotes. Core `make build` passed with go1.27.4. Search `make build` passed with **go1.26.0** (F-1). User `npm ci && npm run build` passed with node v22.14.0.
- The earlier fix is confirmed: `node-version-file: .s1/vizra-user/.nvmrc` is now a workspace-relative path, and setup-node resolved it to v22.14.0 and succeeded.

## Cases
Closed by this meta part (I reproduced each one):
- S1 "each repo builds from a clean clone with documented commands": CI log, all three builds green.
- S2 "bootstrap.sh clones/pins all components; VIZRA_REF pins detached": sha and tag tests, plus the pin-checkout mutation going red.
- R1 "bootstrap.sh is idempotent on rerun": state-hash tests, the mutation going red, and the CI rerun.

Still open:
- N1 "missing lockfile or unpinned toolchain fails CI": component repos (VZ-FOUND-004 / vizra-core, vizra-user, vizra-search). The plan's inventory table names the gaps.

## Findings
FINDING 1: S1 builds vizra-search with go1.26.0, not its pinned toolchain
Severity:    SHOULD
Confidence:  high
Affected:
  repo:      vizra
  files:     .github/workflows/validate.yml (S1 vizra-search setup-go step)
  requirements: VZ-FOUND-001
Observed:
  CI log: "go-version-file: .s1/vizra-search/go.mod … Setup go version spec 1.26.0", then "go version go1.26.0". The plan says vizra-search go.mod:5 has `toolchain go1.27.4`. setup-go took the `go` directive instead. Because GOTOOLCHAIN=local, the pinned toolchain was never used.
Failure:
  The plan's claim "toolchain from each repo's go.mod" is false for search. The build still passes, so S1 holds. This is not a blocking defect.
Perspective: developer
Recommendation:
  Read the `toolchain` line explicitly (or use a go-version step), and assert `go version` equals the pin.

FINDING 2: No test catches a destructive reset in the default-branch path
Severity:    SHOULD
Confidence:  high
Affected:
  repo:      vizra
  files:     tests/bootstrap/bootstrap_test.sh; bootstrap.sh (`merge -q --ff-only`)
  requirements: VZ-FOUND-001
Observed:
  Mutation `merge --ff-only` → `reset --hard` leaves the suite at 11/11 green.
Failure:
  Today's script is correct (it uses ff-only and dies on divergence). But a regression that discarded local commits would pass CI.
Perspective: developer
Recommendation:
  Add a "diverged local commit is refused and preserved" case, and add it to mutation-demo.sh.

No BLOCKING findings. Neither finding is an exploitable privacy, auth, data-loss or false-green defect in today's tree.

FINAL VERDICT: PASS — SHA 4506e815b838edf3a725d2d368410e914ce666d9
