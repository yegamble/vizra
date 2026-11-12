# Execution plan: VZ-INSTALL-001 — installer (`install.sh`)

## Context
Base origin/main 4a53e88, branch `feat/installer`, worktree `.claude/worktrees/meta-install-001`. Issue `docs/issues/VZ-ISSUE-004.md`; repo shape `docs/META_REPO.md` §1. Reference pattern: vidra `install.sh` (behaviour/order only).

## Acceptance
Ledger entry VZ-INSTALL-001 unchanged. Cases S1, S2, N1, N2, P1, R1. Non-goals here: the release bundle (VZ-INSTALL-004), a published CLI + checksums and `vizra setup` (VZ-INSTALL-002).

## Implementation
- `install.sh` (POSIX sh): `--yes --ref --dir --owner --git --cli --cli-sha256 --help`. Steps `docker, tree-meta, tree-core, tree-user, tree-search, cli` recorded in `DIR/.vizra-install.state`; resume skips recorded steps. Docker + Compose >= 2.24 detected; on Ubuntu/Debian installed from Docker's apt repo with key fingerprint `9DC858229FC7DD38854AE2D88D81803C0EBFCD88` pinned; never the convenience script. `verify_sha256` is used for the `--cli` override (checked before anything is written, then again on the copy); `manifest_sha256` reads the documented sha256sum-format manifest (`<64 hex>  <name>`) for the future bundle path. Bundle path refuses: `no release bundle is published for <ref>; use --git` (exit 3). No CLI -> exit 3 before hand-off. Hand-off: exec `vizra setup` if `vizra setup --help` succeeds, else print `next: cd DIR && DIR/bin/vizra setup` and exit 0. Never writes env/production.env, never runs compose up.
- Test-only hooks (refused, exit 2, unless `VIZRA_INSTALL_TESTING=1`): `VIZRA_INSTALL_TEST_STOP_AFTER`, `VIZRA_INSTALL_SKIP_DOCKER`, `VIZRA_INSTALL_REPO_BASE`.
- `tests/install/install_test.sh` (15 checks, local bare repos, no network); `docs/evidence/install/mutation-demo.sh` (7 controlled mutations, each must go red). Both wired as steps in the required `validate` job.

## Verification
`sh tests/install/install_test.sh`; `sh docs/evidence/install/mutation-demo.sh`; `shellcheck -s sh install.sh tests/install/install_test.sh docs/evidence/install/mutation-demo.sh`; meta check scripts.

## Progress and evidence
2026-11-12, macOS arm64 (/bin/sh = bash in sh mode), via quiet.sh:
| command | exit | result |
|---|---|---|
| sh tests/install/install_test.sh | 0 | 15 passed, 0 failed (first run: 6 passed 9 failed — a test-driver arg bug and `cat` in `--help` under empty PATH; both fixed) |
| sh docs/evidence/install/mutation-demo.sh | 0 | 7/7 RED as expected: skip-checksum->N1, no-tty-check->N2, rewrite-production-env->P1, no-resume->R1-resume-after-tree-core, help-needs-path->S2, rerun-touches-state->idempotent, bundle-pretends->bundle-refuses |
| shellcheck -s sh (3 files) | 0 | clean |
| check-workflows / check-action-pins / check-lane-integrity / check-doc-links / check-quality-json | 0 | pass |
| check-generated-ledger.sh | 0 | 192 requirements |

Red transcripts: the mutation demo output above (re-run in CI on every PR). Green: the install_test run above.

| case | state | why |
|---|---|---|
| S1 | OPEN | tree + CLI land, but the interview cannot start: `vizra setup` does not exist (VZ-INSTALL-002); no clean Ubuntu 24.04 transcript yet |
| S2 | closed (test) | `env -i PATH=/nonexistent /bin/sh install.sh --help`, empty cwd stays empty; dash/busybox not run locally — CI ubuntu /bin/sh is dash |
| N1 | closed (test) | wrong sha256 -> exit 4, --dir byte-identical |
| N2 | closed (test) | stdin /dev/null, no --yes -> exit 2, --dir not created |
| P1 | closed (test) | existing production.env byte-identical across two runs; never created |
| R1 | closed (test) | stop after each of 5 steps, rerun -> exit 0, tree + state equal an uninterrupted run |

## Blockers and handoff
Not run: clean-target `ubuntu:24.04` container run (Docker not running locally; not added to CI in this PR); real Docker apt install path (needs root on a clean host); busybox sh. Remaining: S1 needs VZ-INSTALL-002 (`vizra setup`) and a published CLI + checksum manifest (VZ-INSTALL-004 / vizra-core release); bundle path needs VZ-INSTALL-004 and should then use `manifest_sha256` + `verify_sha256`; add a digest-pinned ubuntu:24.04 container step with `--yes --git` to CI.

## Session 2 (2026-11-12)
- CI on 92825bf (validate attempt 2): failed again in "every recorded ledger status is proved against GitHub" (`gh api ... pulls/18: Service Unavailable`, plus fixture lines); installer steps were skipped there. Left to the chair; step untouched.
- Added `--skip-docker` (documented in `--help`: "for environments that provide Docker otherwise"). The only existing skip was the test-only `VIZRA_INSTALL_SKIP_DOCKER`, refused outside `VIZRA_INSTALL_TESTING=1`.
- Added `tests/install/clean_target.sh` + validate step "installer on a clean digest-pinned ubuntu:24.04". Image `ubuntu:24.04@sha256:2198e4c65076e9cb0b3d695219df667c0e3b0072da64ca3c2648aca17dcecaf5` (index; amd64 manifest `sha256:77eb101c…57ec`), confirmed with `docker buildx imagetools inspect ubuntu:24.04` on 2026-11-12.
- Deviation: `--ref main`, not the PR head SHA — `--ref` applies to all four repos and a meta SHA does not exist in vizra-core/user/search.
- The full run uses a PLACEHOLDER local CLI (a script that implements no command) because no vizra CLI is published; it proves only the hand-off message. S1 stays open.
- Local (arm64, same index digest): `sh tests/install/clean_target.sh` exit 0 — /bin/sh is /usr/bin/dash; `--help` with --network none exit 0 and nothing written (root and ubuntu); no-CLI run exit 3 with the tree in place; placeholder-CLI run exit 0 naming `vizra setup`; third run gives the same tree-listing + state sha256 (root and ubuntu).
- Local gates: install_test 15 passed 0 failed; mutation-demo PASS; shellcheck, check-workflows, check-action-pins, check-lane-integrity, check-doc-links all exit 0.
