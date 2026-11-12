# VERIFY — yegamble/vizra PR #24 — VZ-INSTALL-001 installer

- SHA: a31837f9806d83e12aa2a59e35a8a5e849e9ce4a (PR head checked at start and end; `git diff abd9df2 a31837f --stat` = plan file only, +27)
- Env: macOS darwin, local /bin/sh and /bin/dash, Docker not running; clone in mktemp scratch (now deleted)

## Commands
| command | exit | result |
|---|---|---|
| git diff --name-only origin/main...HEAD | 0 | validate.yml, mutation-demo.sh, plan, install.sh, tests/install/{clean_target,install_test}.sh: in scope |
| python3 scripts/check-action-pins.py | 0 | 4 refs SHA-pinned |
| python3 scripts/check-workflows.py | 0 | no continue-on-error |
| sh tests/install/install_test.sh | 0 | 15 passed, 0 failed |
| dash tests/install/install_test.sh | 0 | 15 passed, 0 failed |
| sh docs/evidence/install/mutation-demo.sh | n/a | NOT RUN to completion (hit the 85 s tool limit) |
| own mutations (verify_sha256 → true; write env) | n/a | NOT RUN (out of time) |
| operator-data probe, --dir '/tmp/.../a b' with env/production.env + notes.txt, 2 runs | 0,0 | both files byte-identical (shasum -c OK) |
| --ref 'main;touch /tmp/pwn' | 2 | refused, no /tmp/pwn |
| bad --cli-sha256 | 4 | aborted, --dir never created |
| forged state probe (below) | 0 | **ran the unverified binary** |
| gh run list --commit a31837f | 0 | validate success, ci-required success, headSha a31837f |

## Findings
BLOCKING B1: a stale or forged `.vizra-install.state` makes the installer hand over to a CLI that was never verified. install.sh:202-215: when the state file lists `cli`, the copy and verify step is skipped and `$DIR/bin/vizra setup` is exec'd with no checksum check. This happens even when the operator passes `--cli good --cli-sha256 <good>` on this run.
Reproducer: mkdir -p F/bin; printf 'docker\ntree-meta\ntree-core\ntree-user\ntree-search\ncli\n' >F/.vizra-install.state; printf '#!/bin/sh\necho EVIL-UNVERIFIED "$@"\n' >F/bin/vizra; chmod +x F/bin/vizra; VIZRA_INSTALL_TESTING=1 VIZRA_INSTALL_SKIP_DOCKER=1 VIZRA_INSTALL_REPO_BASE=file://repos sh install.sh --yes --git --dir F --cli good --cli-sha256 <sha of good>  → prints "EVIL-UNVERIFIED setup", exit 0.
Real-world case: a re-run or upgrade with a new verified CLI silently runs the old binary instead, as root. Fix: on every run, re-check bin/vizra against --cli-sha256 before exec (or refuse to hand over).
The test hooks used in the reproducer only stand in for the network and Docker. They do not touch the defect.

FOLLOW-UP: the meta clone runs `git init` inside an existing operator --dir, so operator files sit alongside an untracked tree (they survived here). The `tree-*` state steps trust the file without checking HEAD == ref.

## D. CI
The ci-required job is green on a31837f. In run 43230841779 my log grep turned up only the ledger-guard RED lines. I did NOT confirm the installer test, installer mutation or clean-target step lines myself: UNVERIFIED.

## Per-case
| case | status |
|---|---|
| S1 fresh Ubuntu → /opt/vizra + CLI + interview | OPEN: no published CLI or bundle; `vizra setup` is VZ-INSTALL-002 |
| S2 --help with no network/root/PATH | the install_test case passed locally; the CI clean-target step is UNVERIFIED by me |
| N1 checksum mismatch aborts before writing | PASS (my probe + tests) |
| N2 non-tty without --yes refuses | install_test passed (install.sh:97-98) |
| P1 existing env/production.env never regenerated | PASS (my probe, byte-identical over 2 runs) |
| R1 resume from completed step | the tests passed; **unsafe because of B1** (the cli step is trusted from the state file) |
| second run changes nothing | PASS for the tree and env; the CLI is not re-verified (B1) |
| installs Docker+Compose if missing | code review only (pinned fingerprint, apt, no convenience script); not run, Docker not tested |
| checksum-verified bundle | OPEN: the bundle path refuses (VZ-INSTALL-004) |
| checksum-verified CLI | FAIL on re-run (B1) |
| never writes secrets / compose up | the code has no such writes or calls (grep and read); confirmed by my probe |

VZ-INSTALL-001 can NOT be recorded IMPLEMENTED: S1 needs a published CLI, a published bundle and VZ-INSTALL-002, and B1 must be fixed.

## Not run
mutation-demo.sh to completion, my own two mutations, a Docker install on a real host, and reading the CI installer-step log lines.

FINAL VERDICT: FAIL — SHA a31837f9806d83e12aa2a59e35a8a5e849e9ce4a
