# Execution plan: queue 2o-5 (vizra-search) — vendoring tool: a second manifest

## Context
- Repo `yegamble/vizra-search`, base `main` = `4810048a5c7c65c6b5134d0ec2fd0dacd5f884c6`.
- Branch `feat/vendor-tool-second-manifest`, worktree `vizra/.claude/worktrees/search-2o5-vendor`.
- Ruling: `docs/evidence/warroom/2026-09-23-queue-2o-anchor-ARCHITECT.md` §2, §5 PR 5, §6 and the chair's rulings (tick 255).
- Rules: `docs/sentinel/RULES.md` R1, R2, R4, R5, R14, R15, R23.

## Acceptance
- `scripts/vendor-contract.py` takes the manifest per invocation from a CLOSED set of known manifests
  (`--manifest api/CONTRACT-SOURCE.json` default, or `--manifest scripts/ANCHOR-SOURCE.json`). No
  environment switch (R2). Each known manifest carries, in code: its commit pathspec (`api/` vs
  `scripts/makeanchor/`), its minimum file count (2 vs 3), and whether it mirrors a whole directory.
- Every vendored path must lie inside its manifest's pathspec (otherwise the chosen commit does not track
  it). A whole-directory manifest must also pin every file of the directory: in core at the commit
  (vendor, `--check --core`) and on disk (`--check`).
- The 17 existing selftest fixtures still fire by name. New engine-manifest fixtures, each firing by
  name: wrong pathspec, file outside the directory, digest mismatch, below the minimum, source path !=
  vendored path, shallow clone; plus an engine happy path, an unpinned file in core's directory, an
  unpinned file on disk, and an unknown manifest refused. `EXPECTED_CASES` raised to match.
- Unchanged bytes: lane name `vendor-contract-selftest`, `.github/required-checks.txt`,
  `.github/pinned-steps.yml`, `Makefile` (pinned by digest), `api/CONTRACT-SOURCE.json`.
- Non-goals: vendoring the engine (2o-6), any core change, renaming the tool.

## Implementation
- `scripts/vendor-contract.py`: `KNOWN_MANIFESTS` table; `load_manifest`, `choose_commit`, `vendor`,
  `check` take the selected manifest; `ls-tree` completeness for whole-directory manifests; parent
  directories created on vendor. Contract output byte-identical.
- `scripts/vendor-contract-selftest.py`: engine fixtures (synthetic bytes only), `EXPECTED_CASES`.
- `scripts/revendor-demo.sh`: stale "all 11 fixtures" assertion in `guard` mode (pre-existing) updated.
- AGENTS.md / README / docstrings: describe exactly what is enforced (R1).
- R23: `scripts/ci-hardening-demo.py` rows that patch `vendor-contract.py` (1v, 4d, 5a-5c, C5-C7) must
  still apply exactly once; rerun them.

## Verification
- `./scripts/vendor-contract-selftest.py` before (17) / after (17+k); each new fixture red under a
  mutation of the new code, green restored.
- Contract flow unchanged: re-vendor the real contract from a full core clone with the old and new tool
  into throwaway copies and diff stdout + manifest; `revendor-demo.sh after` before/after diff;
  `--check`; `--check --core` (see progress for the pre-existing api/ drift).
- `make ci`, `make contract-drift`, `make vendor-contract-check`, `make vendor-contract-selftest`,
  `./scripts/boot-matrix.sh`, `./scripts/make-integrity-guard.sh --workflow`,
  `bash scripts/ci-required-guard.sh`; `ci-required` on the pushed head.

## Progress and evidence
(appended below as it runs)

## Blockers and handoff
None at start.
