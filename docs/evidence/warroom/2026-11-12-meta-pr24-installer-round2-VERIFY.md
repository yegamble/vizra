# VZ-INSTALL-001 — PR #24 installer, round-2 independent verification

- Repo yegamble/vizra, PR #24, SHA f52faf1f64f63b47bf28e33bb93991d14d7a2c06 (PR head at the start and the end: f52faf1f64f63b47bf28e33bb93991d14d7a2c06)
- Previous verdict: FAIL at a31837f (forged state made the installer run an unverified bin/vizra)
- Verifier: an independent vizra-verifier that wrote neither the code nor the first verdict. Environment: macOS Darwin 25.5.0, /bin/sh plus /bin/dash, fresh clone in a mktemp scratch dir (deleted afterwards)

## Commands
| command | exit | result |
|---|---|---|
| git diff a31837f..f52faf1 --stat | 0 | 4 files: install.sh, tests/install/install_test.sh, docs/evidence/install/mutation-demo.sh, the plan |
| sh tests/install/install_test.sh | 0 | 19 passed, 0 failed |
| dash tests/install/install_test.sh | 0 | 19 passed, 0 failed |
| sh docs/evidence/install/mutation-demo.sh (local) | n/a | the harness stopped the background job after its first line (RED skip-checksum). Local run NOT COMPLETED; CI evidence is below |
| own mutation: remove the final `verify_sha256 "$BIN" "$CLI_SHA"` | 0 | **19 passed, 0 failed: no test went red** (see FOLLOW-UP) |
| attack scripts B0, A1-A4 (below) | see table | |
| gh run list --commit f52faf1 | 0 | ci-required 43236100004 success, validate 43236101658 success; headSha matches |
| gh run view 43236101658 --log | 0 | L569 "19 passed, 0 failed"; L589 "mutations: 8 red of 8"; L636 "clean target: all checks passed" |

## A. Diff scope
Only the four expected files changed. The diff removes no test and no mutation. It adds tests V1, V2 (two cases) and V3, and the mutation state-skips-verification. The counter now reports n/red.

## B. Blocking finding and attacks
Hooks used, as in the tests: VIZRA_INSTALL_TESTING=1, VIZRA_INSTALL_SKIP_DOCKER=1, VIZRA_INSTALL_REPO_BASE=file://<local bare repos>, absolute --dir, stdin /dev/null.
| id | attack | result |
|---|---|---|
| B0 | the first reproducer: state lists all six steps plus a fake bin/vizra, run with a valid --cli/--cli-sha256 | rc=4 "does not match the checksum recorded"; EVIL marker absent. FIXED |
| A1 | state `cli <sha of fake>` and the fake binary, run with a different valid --cli/--cli-sha256 | rc=0; the binary was replaced by the verified one; output "GOOD-CLI setup", no EVIL; the state now holds `cli <good sha>` |
| A2 | no --cli/--cli-sha256, state and binary match each other | rc=3 "no checksum-verified vizra CLI"; nothing executed |
| A2b | --cli-sha256 set to the fake's sha with no --cli | rc=2 "--cli and --cli-sha256 go together"; nothing executed |
| A3 TOCTOU | verify, then exec by path | default /opt/vizra and bin/ are created by root with mkdir -p (umask, so 0755 and safe). An operator-supplied --dir that is already world-writable is not checked: here F6 was 0777 before and after, so another local user could rename bin/ between verify and exec. That needs an operator to have picked an unsafe dir: FOLLOW-UP |
| A4 | upgrade with a file whose checksum does not match (wrong sha; also another file against the good sha) | rc=4 "checksum mismatch … nothing written"; old binary and state byte-identical; no leftover .vizra.* temp file. The temp file is mktemp in bin/ and is verified before mv -f |
| idem | re-run with the same verified CLI | rc=0, state byte-identical |
Logic (install.sh ~L202-221): exec happens only when CLI_SHA is non-empty, and the binary then is either a fresh copy verified against CLI_SHA, or an existing one whose sha equals rec_sha == CLI_SHA. A final verify follows. No path executes a binary unverified against this run's operator checksum.

## C/E. Tests and CI
Local sh and dash: 19/0. CI validate on the exact SHA: 19 passed, 8 red of 8, clean target passed. ci-required success.

## D. Cases
| case | status |
|---|---|
| S1 fresh Ubuntu → /opt/vizra + CLI + interview | OPEN: no published CLI or bundle; `vizra setup` is VZ-INSTALL-002 |
| S2 --help with no network/root/PATH | PASS (local test, plus the CI clean target) |
| N1 checksum mismatch aborts before writing | PASS (test + A4) |
| N2 non-tty without --yes refuses | PASS (test) |
| P1 / R1 resume after each step | PASS (tests, sh + dash) |
| idempotence | PASS (test + idem) |
| V1-V3 forged / tampered / upgrade | PASS (tests + B0/A1/A2/A4) |

## Findings
BLOCKING: none.
FOLLOW-UP (docs/warroom/FOLLOWUPS.md, meta):
1. The final `verify_sha256 "$BIN"` before hand-off has no test that goes red when it is removed. Today it is redundant with the rec_sha checks, so this is defense-in-depth only, but it should get a test.
2. An already world- or group-writable operator --dir/bin is not refused, which leaves a verify→exec TOCTOU window for another local user.
3. Carried from round 1: git init inside an existing operator --dir; tree-* state entries trusted without checking HEAD == ref.
4. Not new: a tampered binary gives exit 4 and the operator has to remove it by hand.

## Not run
The local mutation demo did not complete (the harness stopped it); I rely on the CI log line 589. I did not run on a real root or Ubuntu host myself beyond the CI clean target.

## Ledger
VZ-INSTALL-001 cannot be recorded IMPLEMENTED after merge. S1 is open: there is no published checksum-verified CLI or release bundle (VZ-INSTALL-004) and no `vizra setup` interview (VZ-INSTALL-002).

FINAL VERDICT: PASS — SHA f52faf1f64f63b47bf28e33bb93991d14d7a2c06
