# PR #11 fix round 1 — independent verification

- Subject: https://github.com/yegamble/vizra/pull/11 (repo yegamble/vizra)
- Verified SHA: a875a80beb7db90302f558f3d6d3ecc657742c68 — `gh pr view 11 --json headRefOid` returned this at the start and at the end; the head did not move.
- Baseline (first verdict): e796cca1e879ffa3f113292738ea2c8089e5333f
- Verifier: independent, wrote none of the code, edited/committed/pushed nothing. This file is the only file created outside the scratch directory and is not staged.
- Environment: macOS 26.5.1 (Darwin 25.5.0) arm64; GNU bash 3.2.57(1); Python 3.9.6; git 2.50.1 (Apple Git-155); shellcheck 0.11.0. Fresh `git clone` into `mktemp -d $TMPDIR/vzv-meta-pr11r1b-XXXXXX`, detached at the SHA; scratch dir deleted at the end.

## Step 1 — diff e796cca..a875a80

`git diff --stat e796cca..HEAD` exit 0: 7 files, +262 −32.

| File | Change | Allowed |
|---|---|---|
| scripts/warroom-check.py | 84 lines | yes |
| tests/warroom/test_warroom_check.py | 58 lines | yes |
| .claude/commands/warroom.md | 2 lines (one sentence each in §3 budget and §exit) | yes |
| docs/warroom/FOLLOWUPS.md | +20 | yes |
| docs/plans/WARROOM-BOARD.md | 1 row | yes |
| docs/evidence/warroom/2026-11-10-meta-warroom-rework-VERIFY.md | +119 (first verifier's evidence) | yes |
| docs/evidence/warroom/…checker-TRANSCRIPT.txt | 7 lines (regenerated) | yes |

Nothing outside the allowed list. AGENTS.md unchanged. I read the full diff of scripts, tests and .claude; the docs-only files I checked by stat only (contents not reviewed line by line).

## Step 2 — reruns (clone at a875a80, default ref origin/main)

| Command | Exit | Result | Claim |
|---|---|---|---|
| `shellcheck .claude/hooks/*.sh .claude/council/quiet.sh tests/warroom/*.sh` | 0 | 3 files, no findings | — |
| `bash tests/warroom/stop_hook_test.sh` | 0 | `stop hook: 18 passed, 0 failed` | 18/0 ✔ |
| `python3 -m unittest discover -s tests/warroom -p 'test_*.py'` | 0 | `Ran 29 tests … OK`, 0 skips | 29/0 skips ✔ |
| `python3 scripts/warroom-check.py stall --replay docs/warroom/TICK-LOG.md` | 1 | `STALL: 252 ticks logged (0-257), 0 ledger status change(s) on origin/main` | ✔ |
| `python3 scripts/warroom-check.py board` | 0 | `OK: docs/plans/WARROOM-BOARD.md is 81 lines, longest 282 characters` | ✔ |
| `python3 scripts/warroom-check.py exit` | 1 | OPEN: profile not frozen; 13 of 13 gates open; 141 of 141 ids not VERIFIED; NOT AN EXIT | ✔ |
| `python3 scripts/check-doc-links.py` | 0 | 29 relative links across 160 md files resolve; 8 external URLs recorded, not fetched | — |
| `python3 scripts/check-quality-json.py` | 0 | 4 JSON files parsed; 192 ids; every reference resolves | — |
| `bash scripts/check-generated-ledger.sh` | 0 | ledger reproduces byte-for-byte (UTF-8 and C/POSIX) | — |

## Step 3 — red before green

`git show e796cca:scripts/warroom-check.py > scripts/warroom-check.py`, then the unittest suite: `Ran 29 tests … FAILED (failures=4)`, 0 errors:

- FAIL test_owner_grant_must_cite_a_recorded_decision (Budget) — the grant test
- FAIL test_red_a_forged_working_tree_profile_is_not_read (Exit)
- FAIL test_red_an_evidence_file_that_is_not_committed (Exit)
- FAIL test_red_records_that_prove_nothing (Exit)

Matches the claim (4 red: one grant test, three exit tests). After `git checkout -- scripts/warroom-check.py`: `Ran 29 tests … OK` (exit 0), `git status --porcelain` empty, HEAD still a875a80.

Note: `test_an_uncommitted_decision_grants_nothing` passes against the old checker too (the old code rejects it for a different reason), so it is not one of the red tests; the committed-on-ref property is nevertheless shown red→green by my own control in step 4b/4a below.

## Steps 4 and 5 — exploits and residual limits

Driver: a Python script in the scratch dir that builds one throwaway git repo per case (docs/MILESTONES.md, docs/RELEASE_ACCEPTANCE.md with `## Gate matrix` listing gates `Clean install` and `Backup/restore`, docs/warroom/OWNER-DECISIONS.md with `## 2026-11-10` items 1 "Unrelated.", 2 "One more verdict for VZ-FOUND-001.", 3 "VZ-FOUND-001 stays BLOCKED; no further budget is granted.", status_records.json, ticks.jsonl) and runs `python3 <clone>/scripts/warroom-check.py --root <fixture> --ref main <cmd>`. `OLD(e796cca)` is the baseline checker extracted with `git show`, run on the same fixture as a control that the exploit is real. Driver exit 0, all assertions held. Full output:

```
== 4a G-1: ref 'a', verdicts 100, then 20 FAIL
[4a-control] python3 OLD(e796cca) --root fx --ref main budget -> exit 0
     | VZ-FOUND-001           verdicts 24/104  fix rounds 0/2  re-plans 0/1  ticks 0/12  ok
     | OK: every slice is within budget
[4a] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref 'a' is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-positive-control] python3 NEW --root fx --ref main budget -> exit 0
     | VZ-FOUND-001           verdicts 5/5  fix rounds 0/2  re-plans 0/1  ticks 0/12  ok
     | OK: every slice is within budget
[4a-variant ref='2026-11-10 #1'] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: decision 2026-11-10 #1 does not name VZ-FOUND-001
[4a-variant ref='2026-11-10 #9'] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref '2026-11-10 #9' is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-variant ref='2026-11-10'] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref '2026-11-10' is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-variant ref='#2'] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref '#2' is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-variant ref='2026-11-10 #2 x'] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref '2026-11-10 #2 x' is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-variant ref='2026-11-10 #02'] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref '2026-11-10 #02' is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-variant ref=['2026-11-10 #2']] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref ['2026-11-10 #2'] is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-variant ref=None] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 2: owner_grant ref None is not a numbered decision '<date> #<n>' in docs/warroom/OWNER-DECISIONS.md on main
[4a-variant two ids, one unnamed] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: tick 1: decision 2026-11-10 #2 does not name VZ-FOUND-002
== 4b G-9: committed profile one gate open; uncommitted forged profile all PASS, no ids
[4b-control] python3 OLD(e796cca) --root fx --ref main exit -> exit 0
     | GO-CANDIDATE: all 2 gates carry a PASS record for core at ce86309. Stop for the owner's release decision.
[4b] python3 NEW --root fx --ref main exit -> exit 1
     | OPEN: 1 of 2 gates have no PASS record for the frozen profile; first: Backup/restore
     | OPEN: 0 of 1 profile ids are not VERIFIED; first: -
     | NOT AN EXIT: derive the next slice from the first open item, or stop as OWNER-BLOCKED, STALLED or BUDGET
[4b-variant forged profile staged, not committed] python3 NEW --root fx --ref main exit -> exit 1
     | OPEN: 1 of 2 gates have no PASS record for the frozen profile; first: Backup/restore
     | OPEN: 0 of 1 profile ids are not VERIFIED; first: -
     | NOT AN EXIT: derive the next slice from the first open item, or stop as OWNER-BLOCKED, STALLED or BUDGET
[4b-variant forged profile committed on unmerged branch 'side'] python3 NEW --root fx --ref main exit -> exit 1
     | OPEN: 1 of 2 gates have no PASS record for the frozen profile; first: Backup/restore
     | OPEN: 0 of 1 profile ids are not VERIFIED; first: -
     | NOT AN EXIT: derive the next slice from the first open item, or stop as OWNER-BLOCKED, STALLED or BUDGET
[4b-variant committed profile, source_sha = commit NOT on main] python3 NEW --root fx --ref main exit -> exit 1
     | OPEN: the core profile on main is not frozen (source_sha is not a commit on that ref)
     | OPEN: 2 of 2 gates have no PASS record for the frozen profile; first: Clean install
     | OPEN: 0 of 1 profile ids are not VERIFIED; first: -
     | NOT AN EXIT: derive the next slice from the first open item, or stop as OWNER-BLOCKED, STALLED or BUDGET
[4b-positive-control (honest committed profile)] python3 NEW --root fx --ref main exit -> exit 0
     | GO-CANDIDATE: all 2 gates carry a PASS record for core at 4b65c39. Stop for the owner's release decision.
== 5 residual limits
[R1-1 decision #3 says 'stays BLOCKED', grant verdicts=100, 20 FAIL] python3 NEW --root fx --ref main budget -> exit 0
     | VZ-FOUND-001           verdicts 24/104  fix rounds 0/2  re-plans 0/1  ticks 0/12  ok
     | OK: every slice is within budget
[R1-4 evidence_file = committed dir + unrelated committed file] python3 NEW --root fx --ref main exit -> exit 0
     | GO-CANDIDATE: all 2 gates carry a PASS record for core at 4b65c39. Stop for the owner's release decision.
[R1-5a grant verdicts='lots'] python3 NEW --root fx --ref main budget -> exit 1
     | Traceback ...
     | ValueError: invalid literal for int() with base 10: 'lots'
[R1-5b evidence=5] python3 NEW --root fx --ref main exit -> exit 1
     | Traceback ...
     | TypeError: 'int' object is not iterable
[R1-5b evidence=True] python3 NEW --root fx --ref main exit -> exit 1
     | Traceback ...
     | TypeError: 'bool' object is not iterable
[R1-5b evidence='abc'] python3 NEW --root fx --ref main exit -> exit 1
     | OPEN: 2 of 2 gates have no PASS record for the frozen profile; first: Clean install
     | OPEN: 0 of 1 profile ids are not VERIFIED; first: -
     | NOT AN EXIT: derive the next slice from the first open item, or stop as OWNER-BLOCKED, STALLED or BUDGET
[R1-5b evidence={'gate': 'Clean install'}] python3 NEW --root fx --ref main exit -> exit 1
     | OPEN: 2 of 2 gates have no PASS record for the frozen profile; first: Clean install
     | OPEN: 0 of 1 profile ids are not VERIFIED; first: -
     | NOT AN EXIT: derive the next slice from the first open item, or stop as OWNER-BLOCKED, STALLED or BUDGET
[R1-5c profile is a JSON list] python3 NEW --root fx --ref main exit -> exit 1
     | Traceback ...
     | AttributeError: 'list' object has no attribute 'get'
[R1-5d verdict event without result] python3 NEW --root fx --ref main budget -> exit 2
     | UNUSABLE: docs/warroom/ticks.jsonl:1: a verdict needs result PASS, FAIL or BLOCKED
ALL ASSERTIONS HELD
```

Fixture detail: 4a ticks = tick 1 four FAIL verdicts + `blocked`; tick 2 `owner_grant` (ref as shown, verdicts 100) then 20 FAIL verdicts. 4b = ledger VZ-FOUND-001 VERIFIED; committed profile with a PASS record for `Clean install` only and source_sha = an ancestor commit; then the working-tree profile overwritten with PASS for both gates and `required_feature_ids: []`.

### Result

- **G-1 closed.** Old checker: exit 0 "within budget" (24/104). New checker: exit 2 `owner_grant ref 'a' is not a numbered decision`. Eight further malformed/unrelated refs and a two-id grant with one unnamed id all exit 2. A legitimate grant (`2026-11-10 #2`, verdicts 1) still exits 0.
- **G-9 closed.** Old checker: exit 0 GO-CANDIDATE. New checker: exit 1, `first: Backup/restore`, no GO-CANDIDATE — with the forged profile uncommitted, staged, and committed on an unmerged branch. A committed profile whose source_sha is a real commit not on the ref is "not frozen", exit 1. An honest committed profile still gives GO-CANDIDATE exit 0 (the fixture can go green, so the reds are meaningful).

### Residual limits observed (step 5)

- **R1-1 reproduced.** Decision #3 says the id "stays BLOCKED; no further budget is granted"; a grant citing it with verdicts 100 is accepted: exit 0, 24/104 "ok". The checker tests that the decision names the id, not what it decides or how much.
- **R1-4 reproduced.** A COMMITTED profile whose evidence_file values are the directory `docs/evidence/release` and the unrelated committed file `docs/evidence/ledger-generator/status_records.json` gives GO-CANDIDATE exit 0. `git cat-file -e ref:path` accepts trees and any blob.
- **R1-5 reproduced.** Tracebacks: grant `verdicts: "lots"` → ValueError, exit 1; `evidence: 5` / `true` → TypeError, exit 1; profile that is a JSON list → AttributeError, exit 1. `evidence: "abc"` or a dict does not crash: OPEN, exit 1. A verdict with no result is caught cleanly: exit 2. **No crash can exit 0**: an uncaught exception makes CPython exit 1, and `main()` only returns 0 from a completed command. The defect is the wrong code (1 "red" instead of 2 "unusable") and an unreadable message; it fails closed.

## Step 6 — CI

`gh pr checks 11 -R yegamble/vizra` exit 0:

| Check | State | Run | headSha of run |
|---|---|---|---|
| ci-required | pass (6m40s) | 42856201446 | a875a80beb7db90302f558f3d6d3ecc657742c68, completed/success |
| validate | pass (6m23s) | 42856201629 | a875a80beb7db90302f558f3d6d3ecc657742c68, completed/success |
| GitGuardian Security Checks | pass | external | not independently tied to the SHA |

## Findings

Bar: BLOCKING only if exploitable or wrong in today's tree for privacy, auth, data loss or a false-green product gate and reproduced on this head, or a fix-round claim I could not reproduce. All four fix-round claims reproduced. No BLOCKING findings.

| ID | Class | Where | Reproducer | Why not blocking | Smallest fix |
|---|---|---|---|---|---|
| R1-1 | FOLLOW-UP | scripts/warroom-check.py:293-297 | fixture `r11` above: grant ref `2026-11-10 #3`, verdicts 100 → exit 0 | Needs a numbered decision naming the id already merged on origin/main; the amount is still a tick-line claim, but no product gate, privacy or data path depends on it today and no owner_grant exists in today's tree | Require a machine-readable line in the decision (e.g. `grant: VZ-X verdicts=1`) and cap the event's amounts at it |
| R1-4 | FOLLOW-UP | scripts/warroom-check.py:403 | fixture `r14` above → GO-CANDIDATE exit 0 | Needs a forged profile merged to origin/main through review; today's tree is OPEN on 13/13 gates and 141/141 ids (step 2), and GO stays the owner's decision | `git cat-file -t ref:path` must be `blob`, and the file must be under a per-gate/per-SHA path or mention the gate and source_sha |
| R1-5 | FOLLOW-UP | scripts/warroom-check.py:297, :392, :398 | fixtures `r15a/b/c` above → traceback, exit 1 | Fails closed; never exit 0 | Validate types and raise `Unusable` (exit 2) |
| R1-6 | FOLLOW-UP (new, minor) | tests/warroom/test_warroom_check.py (`test_an_uncommitted_decision_grants_nothing`) | step 3: passes against the e796cca checker | Test does not discriminate old from new on its own; the property is covered by my 4a/4b controls | Make the uncommitted file contain an otherwise valid `<date> #<n>` item naming the id so only the ref read rejects it — it already does; add an assertion on the message, or accept as documentation |

The other 17 follow-ups from the first verdict are known and were not re-examined.

## Not run

- No Go, Next.js, Docker, database or browser lanes: this PR touches only the war-room checker, its tests and docs.
- CI was not re-run; I read its recorded result and confirmed each run's head SHA.
- The first verifier's full evidence at e796cca was not re-verified; only the delta e796cca..a875a80 and the reruns above.
- docs/warroom/FOLLOWUPS.md, WARROOM-BOARD.md and the transcript were checked for scope (diff stat), not for the accuracy of their prose.
- External URLs in docs were not fetched (the link checker records them only).
- `--ref` values other than `main` (fixtures) and the default `origin/main` (clone) were not exercised.

FINAL VERDICT: PASS — SHA a875a80beb7db90302f558f3d6d3ecc657742c68
