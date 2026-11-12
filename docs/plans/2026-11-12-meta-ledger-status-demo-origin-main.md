# Execution plan: ledger-status demo — scratch copy carries origin/main

## Context
Base origin/main e91e28e, branch `fix/ledger-status-demo-origin-main`. Defect: with draft PR #25 (first VERIFIED record VZ-FOUND-003, head 8cf0640), `docs/evidence/ledger-status/demo.sh` gives `53 passed, 8 failed`: the restored cases D1c, D6a, D6b-i, D6b-ii, D6c, D9, D9b, D11 fail because the scratch copy has no `refs/remotes/origin/main`, and `scripts/check-ledger-status-output.py` refuses it, as it should. Same class as meta #20 (D11).

## Acceptance
With a real VERIFIED record, the demo passes all 61 cases. Without one, it still passes 61. D10a's red case still bites when the evidence-on-main check is broken. No checker, assertion, needle or case changed.

## Implementation
demo.sh only: (1) when the copy's base commit is made, also set `refs/remotes/origin/main` to it, the way a real checkout has it (the copy's tree holds the real evidence files); (2) D10a's cleanup now restores the ref to `base-commit` instead of deleting it. D10a's red half is unchanged: it still points origin/main at base-commit, and the fixture evidence exists only in the later commit. Audited the other ref changes: `git reset --hard HEAD~1` (D1c), `git reset --hard base-commit` (escape, D10, D11) and `git tag -f base-commit` move HEAD or the tag and never touch origin/main. The tag points at the same commit as the ref.

## Verification / Progress and evidence
Scratch clone `mktemp -d` → `$S/c`, base e91e28e plus PR #25's two files (checked out from FETCH_HEAD 8cf0640) and committed locally there only.

(a) RED before, old demo.sh: exit 1
```
  FAIL  D1c output check restored — expected exit 0, got 1:
  FAIL  D6a (2c) extra keys restored — expected exit 0, got 1:
  FAIL  D6b-i (2d) str subclass alone restored — expected exit 0, got 1:
  FAIL  D6b-ii (2d) str subclass with the in-process check wrapped away restored — expected exit 0, got 1:
  FAIL  D6c (2e) wrapper around check_dsl_defaults restored — expected exit 0, got 1:
  FAIL  D9 duplicate status keys restored — expected exit 0, got 1:
  FAIL  D9b non-canonical serialisation restored — expected exit 0, got 1:
  FAIL  D11 restored — expected exit 0, got 1:
demo: 53 passed, 8 failed
```
(b) GREEN after, same state, new demo.sh: exit 0
```
demo: 61 passed, 0 failed
```
(c) GREEN on this branch as is (one IMPLEMENTED record): exit 0
```
demo: 61 passed, 0 failed
```
(d) state (b), checker mutated (`if on_main.returncode != 0:` → `if False:`, so any evidence path is accepted), then restored: exit 1
```
  FAIL  D10a offline: evidence not on (the copy's) origin/main — expected a non-zero exit naming [EVIDENCE NOT ON META MAIN], got exit 1:
demo: 60 passed, 1 failed
        | VZ-FOUND-008: EVIDENCE DIFFERS FROM META MAIN — docs/evidence/warroom/DEMO-FIXTURE-ledger-status-VERIFY.md in this tree is not byte-identi
```
Also: `shellcheck docs/evidence/ledger-status/demo.sh` exit 1, the same two SC2001 style findings (lines 79, 93) as origin/main, so nothing new. `python3 scripts/check-doc-links.py` exit 0; `bash scripts/check-generated-ledger.sh` exit 0 (reproduces byte-for-byte).

## Blockers and handoff
None. READY_FOR_REVIEW; the verifier and merge are separate.
