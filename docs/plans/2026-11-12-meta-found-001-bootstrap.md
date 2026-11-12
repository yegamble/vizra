# VZ-FOUND-001 (meta part) — bootstrap.sh and clean-clone builds

State: IN_PROGRESS → READY_FOR_REVIEW once CI on the final head is green. Base: origin/main cfce798. Branch `feat/found-001-bootstrap`. Builder does not verify its own work.

## Inventory (read-only, nested checkouts on main: core 3f1def3, user 9f7c639, search 8d0c293)

| Repo | AGENTS.md | Lockfile | Toolchain pin | Contract source | N1 CI (missing lockfile / unpinned toolchain fails) |
|---|---|---|---|---|---|
| vizra-core | `AGENTS.md` | `go.sum` | `go.mod:12` `toolchain go1.27.4` | `api/openapi.yaml` | toolchain: `.github/workflows/build-test.yml:178-184` asserts the runner matches go.mod `toolchain`; lockfile: `build-test.yml:212` "go.mod and go.sum are tidy" (a deleted go.sum makes tidy diverge). No explicit "toolchain directive present" check — an unpinned go.mod (no `toolchain` line) makes `want` empty; not verified that this fails. |
| vizra-user | `AGENTS.md` | `package-lock.json` | `.nvmrc` 22.14.0; `package.json:5-7` engines `>=22.13.0` | generated client from core OpenAPI, `contracts/manifest.json` + `contracts/vizra-core/` | `ci-guard.yml:125` refuses `npm install` in workflows; `npm ci` fails without a lockfile; `setup-node node-version-file: .nvmrc` (`ci-guard.yml:80`) fails without `.nvmrc`. No dedicated "lockfile/.nvmrc must exist" assertion found. |
| vizra-search | `AGENTS.md` | `go.sum` | `go.mod:5` `toolchain go1.27.4` | `api/` (internal search contract; core holds `api/search-internal.openapi.yaml`) | toolchain: `ci.yml:49` `GO_VERSION: "1.27.4"` hard-coded, NOT read from go.mod — go.mod's toolchain could be removed and CI stays green (gap). Lockfile: `Makefile:155` `tidy-check`. |

## Cases
- S1 — CI steps in `validate` (`.github/workflows/validate.yml`, "S1 …"): bootstrap.sh clones all three at main, then core `make build`, search `make build`, user `npm ci && npm run build`, toolchain from each repo's go.mod / .nvmrc, GOTOOLCHAIN=local; each step prints its SHA. Build-only targets, no services.
- S2 — `tests/bootstrap/bootstrap_test.sh` S2-clone, S2-ref-detached (sha), S2-tag.
- R1 — R1-rerun-default, R1-rerun-pinned (sha256 of HEAD/branch/status/files before and after); plus a second bootstrap run in CI against the real remotes.
- Dirty refused (preflight over every checkout before touching any) and bad refs (`;`, `$(…)`, leading `-`, `..`, space) refused before any clone.
- N1 — out of scope for meta; per-repo gaps above remain for the component repos.

## Demonstrations
`docs/evidence/bootstrap/mutation-demo.sh`: drop-dirty-check → dirty-refused red; drop-ref-validation → 5 bad-ref red; drop-pin-checkout → S2-ref-detached red; always-checkout-default (+drift commit) → R1-rerun-default red; unmutated 11/11 green.

The first test run itself found a real defect: the dirty check ran per component, so vizra-core was moved before vizra-user's dirty tree was refused. Fixed by a preflight pass.

## Local commands (darwin/arm64, via quiet.sh)
| Command | Exit |
|---|---|
| `sh tests/bootstrap/bootstrap_test.sh` | 0 (11 passed, 0 failed) |
| `sh docs/evidence/bootstrap/mutation-demo.sh` | 0 (4 RED, unmutated GREEN) |
| `shellcheck bootstrap.sh tests/bootstrap/*.sh docs/evidence/bootstrap/*.sh` | 0 |
| `python3 scripts/check-workflows.py` | 0 |
| `python3 scripts/check-action-pins.py --required .github/required-checks.txt` | 0 |
| `python3 scripts/check-lane-integrity.py --required .github/required-checks.txt` | 0 |
| `python3 scripts/check-doc-links.py` | see PR |

S1 not run locally (CI ubuntu-24.04 is the clean target).
