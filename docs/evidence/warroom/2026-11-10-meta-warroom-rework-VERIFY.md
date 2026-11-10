# Independent verification — meta PR #11 (war-room loop rework)

- PR: https://github.com/yegamble/vizra/pull/11, branch `chore/warroom-loop-rework`
- Head SHA verified: `e796cca1e879ffa3f113292738ea2c8089e5333f` (`gh pr view 11 --json headRefOid`, read at start and again after CI finished; unchanged)
- Date: 2026-11-10. Verifier: independent agent; wrote no code in this PR; edited nothing, pushed nothing.
- Method: fresh clone in `mktemp -d $TMPDIR/vzv-meta-pr11-XXXXXX`, detached at the SHA. Mutations were applied in that clone only and restored with `git checkout --`; `git status --short` was empty afterwards. The clone was deleted at the end.

## Environment

| Item | Value |
|---|---|
| OS | macOS 26.5.1 (25F80), Darwin 25.5.0, arm64 |
| bash | `/bin/bash` GNU bash 3.2.57(1)-release (the only bash on PATH) |
| Python | 3.9.6 |
| git | 2.50.1 (Apple Git-155) |
| shellcheck | 0.11.0 |

## Commands

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `shellcheck .claude/hooks/*.sh .claude/council/quiet.sh tests/warroom/*.sh` | 0 | no output (3 files) |
| 2 | `/bin/bash tests/warroom/stop_hook_test.sh` | 0 | `stop hook: 18 passed, 0 failed`; hook itself is run by `/bin/bash` 3.2.57 |
| 3 | `python3 -m unittest discover -s tests/warroom -p 'test_*.py' -v` | 0 | `Ran 26 tests`, `OK`, 0 skips (0 lines matching "skip") |
| 4 | `python3 scripts/warroom-check.py stall --replay docs/warroom/TICK-LOG.md` | 1 | `STALL: 252 ticks logged (0-257), 0 ledger status change(s) on origin/main` (exact match). `status_records.json` on `origin/main` is `"records": []` |
| 5 | `git show HEAD:docs/warroom/archive/WARROOM-BOARD-through-tick-257.md \| shasum -a 256` vs `git show origin/chore/warroom-records-2026-09-23b:docs/plans/WARROOM-BOARD.md \| shasum -a 256` | 0 | both `fce0ee1e88522455f2bf32fe916c2b949b3c080fee361916f08585543d873614`; git blob `1e93f95` both sides; old board 440 lines / 219537 bytes, new board 81 lines |
| 6a | `python3 scripts/check-doc-links.py` | 0 | 29 relative links across 159 files resolve |
| 6b | `python3 scripts/check-quality-json.py` | 0 | 4 JSON files, 192 requirement ids, all references resolve |
| 6c | `bash scripts/check-generated-ledger.sh` | 0 | ledger reproduces byte-for-byte in UTF-8 and C/POSIX |
| 6d | `check-workflows.py`, `check-action-pins.py`, `check-lane-integrity.py` | 0, 0, 0 | pass |
| 7a | `python3 scripts/warroom-check.py board` | 0 | `OK: docs/plans/WARROOM-BOARD.md is 81 lines, longest 282 characters` |
| 7b | `python3 scripts/warroom-check.py exit` | 1 | `OPEN: the core profile is not frozen`; 13 of 13 gates open; 141 of 141 ids not VERIFIED; `NOT AN EXIT` |
| 8 | `git diff origin/main...HEAD -- AGENTS.md` | 0 | numstat `9 0`: 9 added, 0 removed. Both owner sentences present exactly once, character for character (`grep -c` of the full quoted strings = 1 each) |
| 9a | tick lines: archive `## Tick log` section vs TICK-LOG.md `## Ticks 0–257` section, blank lines dropped, `cmp` | 0 | identical, 252 lines each, all `- Tick` lines |
| 9b | merged table: archive `## Merged` `\|` rows vs MERGED.md `\|` rows, `cmp` | 0 | identical, 34 rows each (header, separator, 32 data rows) |
| 10 | `gh pr checks 11 -R yegamble/vizra` | 0 | see CI state |
| – | `quiet.sh` smoke: passing command, failing command (exit 7), missing args | 0, 7, 2 | exit status is the command's; usage error is 2 |

No required check was skipped. Nothing timed out.

## Mutation demonstrations

| # | Mutation (in the clone) | Red | Green after restore |
|---|---|---|---|
| M1 | hook: final `exit 2` removed | `stop hook: 6 passed, 12 failed`, exit 1. All 12 red cases report `exit 0, wanted 2` | `18 passed, 0 failed`, exit 0 |
| M2 | hook: `MERGED)` arm replaced by `: ;;` | `14 passed, 4 failed`, exit 1. `red: merged branch not deleted` fails with `exit 0, wanted 2 … 'PR #9 is merged but branch 'feat/done' still exists'`; also the 9-Stops case, `merged worktree not removed`, `commits after a merged PR` | `18 passed, 0 failed`, exit 0 |
| M3 | `STALL_TICKS = 150` | `Ran 26 tests`, `FAILED (failures=5)`, exit 1. `test_red_fifteen_ticks_and_no_ledger_change`: `AssertionError: 0 != 1 : OK: 15 tick(s) recorded; the stall rule needs 150` | `Ran 26 tests`, `OK`, exit 0 |
| M4 | `MAX_FIX_ROUNDS = 20` | `FAILED (failures=2)`, exit 1. `test_red_a_replan_does_not_reset_the_counters`: `'VZ-FOUND-001: fix rounds 3 exceeds the budget of 2' not found`; also `test_green_within_budget` (prints `1/20`) | `Ran 26 tests`, `OK`, exit 0 |

All four went red for the stated reason and returned to green.

## CI state for e796cca1e879ffa3f113292738ea2c8089e5333f

- First read (about 16:14 UTC, two minutes after the PR was opened): `no checks reported`. Runs were created at 16:14:38Z.
- Final read (16:21:42 UTC, `gh pr checks 11 --watch`, exit 0): `ci-required` **pass** (run 42852551744), `validate` **pass** (run 42852551831), GitGuardian pass.
- `gh run list --commit <sha>` confirms both runs are `pull_request` events with `headSha` equal to the verified SHA, `conclusion: success`.
- `.github/required-checks.txt` lists one job, `validate`, and it ran on this SHA. The PR does not touch workflows or the manifest.
- The new tests (`tests/warroom/`) are not run by any CI lane. The PR body says so. CI green here does not cover them; rows 1–3 above are local results only.

## Findings

Bar used: BLOCKING only if exploitable or wrong in today's tree for privacy, auth, data loss or a false-green product gate and reproduced on the PR head, or a PR claim I could not reproduce. **No finding meets it.** Every PR claim I was asked to reproduce reproduced. All findings below are FOLLOW-UP.

Hook reproducers used a harness modelled on `tests/warroom/stop_hook_test.sh` (four fixture repos with bare remotes, stub `gh`, hook run by `/bin/bash`). Checker reproducers used a throwaway git repo and `scripts/warroom-check.py --root <fixture> --ref main`.

### Stop hook (`.claude/hooks/finished-means-merged.sh`)

Adversarial cases that the hook handled correctly (exit 2 where wanted): detached-HEAD worktree with an uncommitted tracked change; branch names `feat/a.b+c`, `feat/x$y(z)|w`, `feat/sp&ce;rm`, `feat/q'uote`, `feat/{a}` (blocked when unpushed, exit 0 when pushed with an open PR; git itself refuses names with spaces); `feat/a.b` does not match a PR for `feat/aXb`; `gh` printing `this is not json`, `null` or nothing gives "unreadable pull request list"; `gh` printing `{}` gives "no open or merged PR"; a branch whose only PR has `isCrossRepository: true` is blocked; empty stdin still audits (exit 0 clean, exit 2 dirty).

| ID | Class | Where | Reproducer → observed | Smallest fix |
|---|---|---|---|---|
| H-1 | FOLLOW-UP | hook :60-73, :131 | `git worktree add --detach wt main; echo c >> wt/README.md; git -C wt commit -qam x` then run hook → **exit 0**. Same with `git checkout --detach` and a commit in the main checkout. Commits on a detached HEAD are on no branch, so nothing checks them. The PR lists "unpushed commits" as blocked; for commits on a branch that is true | For each worktree line `detached`, block unless `git branch -r --contains HEAD` is non-empty |
| H-2 | FOLLOW-UP | hook :64-66 | `echo x > newfile.go` (never added) → exit 0; `git stash` holding the only copy of a change → exit 0. Untracked files are a stated limit ("tracked"); stashes are not mentioned | Block on `git stash list` non-empty; document untracked as a limit or check `git ls-files -o --exclude-standard` |
| H-3 | FOLLOW-UP | hook :108, :112 | local branch `1e2`, pushed, no PR; stub `gh` lists an OPEN PR for branch `100` → **exit 0**. awk `$1 == b` compares numerically when both look like numbers | Force string compare: `($1 "") == (b "")` |
| H-4 | FOLLOW-UP | hook :44-50 | two never-pushed branches with open PRs, each set as the other's upstream (`git branch -u feat/keep feat/x`) → exit 0. `@{u}` may be a local branch; "pushed" is not checked against `origin` | Require the upstream ref to start with `refs/remotes/origin/` |
| H-5 | FOLLOW-UP | hook :115-116 | open PR whose `headRefOid` differs from the pushed head → exit 0. The oid is compared only for MERGED | Low value; compare the oid to `origin/<branch>` if wanted |
| H-6 | FOLLOW-UP | hook :136-140 | `VIZRA_CORE_ROOT=/nonexistent` with a dirty `vizra-core` → exit 0. Needs a hostile environment | Block when the variable is set and the path has no `.git` |
| H-7 | FOLLOW-UP | hook :143-163, `.claude/settings.json` | By design the hook never lets a session stop while any of the four repos has a leftover, including leftovers the session does not own. The PR body says it will block on the real checkout today. Not run against the real checkout (it fetches and prunes there, outside my scratch directory) | Do the cleanup the PR describes before or with the merge; consider reporting pre-existing leftovers without blocking |

### Loop governors (`scripts/warroom-check.py`)

`ticks.jsonl` is written by the chair, so anything read only from it can be shaped by the chair. Ledger movement is read from git, which is the strong part. Limits found, each with exit 0 while the rule's intent is violated:

| ID | Class | Where | Reproducer → observed | Smallest fix |
|---|---|---|---|---|
| G-1 | FOLLOW-UP | :248-257 | `owner_grant` with `"ref": "a", "verdicts": 100, …` then 38 FAIL verdicts on one id → `verdicts 38/104 … ok`, `OK: every slice is within budget`, **exit 0**. `ref not in decisions` is a substring test, so any one letter that occurs in OWNER-DECISIONS.md passes as an owner decision | Require `ref` to match a whole decision id on its own line (for example `^G-\d+`), and bound the grant size |
| G-2 | FOLLOW-UP | :183-196 | Ledger moved once, long before the window. 15 ticks with honest `meta_main` → STALL exit 1. Same ticks with `meta_main` set to an older ancestor → `OK: ledger status moved`, exit 0. `meta_main` only has to be an ancestor of the ref and non-decreasing | Compare each tick's `meta_main` with the commit date or the first-parent position at the tick's `date`; or take the window start from the commit that added the tick line |
| G-3 | FOLLOW-UP | :180-182 | keep 14 lines in `ticks.jsonl` (truncate, or do not log wake-ups) → `OK: 14 tick(s) recorded`, exit 0 | Refuse a `ticks.jsonl` whose line count shrank against `origin/main`; tick numbers must be contiguous |
| G-4 | FOLLOW-UP | :192-196 | a new record with status PLANNED, or IMPLEMENTED → PLANNED, counts as movement → exit 0 | Count only forward moves (to IMPLEMENTED or VERIFIED) |
| G-5 | FOLLOW-UP | :230-246 | 20 FAIL verdicts, label renamed each tick (`QUEUE-fix-1` … `QUEUE-fix-20`) → all `ok`, exit 0. Control with one label: `verdicts 5/4 OVER`, exit 1. Ledger ids cannot be renamed this way; QUEUE labels can | Require QUEUE labels to be declared once in a tracked list; count by slot `slice`+`repo` as well |
| G-6 | FOLLOW-UP | :239-246, :289 | 40 ticks on `VZ-FOUND-001` with `slots: []`, 4 FAIL verdicts then `cleanup` events with no ids → `ticks 0/12 SPENT`, `OK`, exit 0. A spent slice is only reported if it is in the last tick's slots | Count a tick for every id named in a work event; report SPENT without requiring a slot |
| G-7 | FOLLOW-UP | :312 | three meta slots, each tagged with one later-milestone id (`["QUEUE-a","VZ-AUTH-001"]`) while M0 waits → `0 of 3 slot(s) on non-milestone work, 5 milestone id(s) waiting`, exit 0 | A slot counts as milestone work only if all its ids are ledger ids in the lowest open milestone |
| G-8 | FOLLOW-UP | :319, :305 | three meta slots with every open id listed in `blocked_ids` by the chair → exit 0; or three meta slots at tick 1 and a later tick with no slots → exit 0 (only the last tick is read) | Require each `blocked_ids` reason to cite an OWNER-INBOX item that exists; check every tick in the window |
| G-9 | FOLLOW-UP | :347-358 | fixture with an uncommitted `core.json`: `required_feature_ids: []`, `source_sha` forty zeros (not a commit), two PASS records whose `evidence_file` is `docs/evidence/ledger-generator/status_records.json` → `GO-CANDIDATE: all 2 gates carry a PASS record`, **exit 0**. The profile is read from the working tree, the SHA is not checked to be a commit, the evidence file's `FINAL VERDICT` line is not read, the profile's own `verdict: NO-GO` is ignored. Not BLOCKING: on today's tree `exit` is red (row 7b), it needs a forged profile, it is not a CI gate, and warroom.md §8 says the check is "necessary, not sufficient: GO is the owner's" | Read the profile at `--ref`; require `source_sha` to resolve to a commit; require the evidence file to end with `FINAL VERDICT: PASS — SHA <source_sha>`; refuse an empty id list |
| G-10 | FOLLOW-UP | `docs/quality/release-profiles/core.json` vs `docs/RELEASE_ACCEPTANCE.md` | the profile's `gates` list has 12 entries (snake_case names, no provider qualification); the gate matrix that `exit` reads has 13 title-case names. `exit` matches `evidence[].gate` against the matrix names. Pre-existing data, not changed here | State in warroom.md §8 which spelling an evidence record must use |
| G-11 | FOLLOW-UP | `.github/workflows/validate.yml` (unchanged) | `tests/warroom/` is run by no lane; the PR says so | Add both test commands and the shellcheck line to `validate` in a separate PR |

### Agent and command files against AGENTS.md

Read the full diff of `.claude/agents/**`, `.claude/commands/sentinel.md` and the whole of `.claude/commands/warroom.md`.

- No file tells an agent to merge its own work. warroom.md §3 restates the four merge conditions; §7 sends PRs that edit `AGENTS.md` or `.claude/` to the owner. The hook text says "never merge a PR to satisfy this hook".
- VERIFIED is not weakened: warroom.md §3 step 3 ("VERIFIED needs the independent evidence file too"), verifier.md ("PASS is not a merge and not VERIFIED"), and the AGENTS.md addition ("does not lower what VERIFIED or a release gate requires").
- The blocking bar is worded the same way in AGENTS.md, warroom.md, verifier.md, sentinel.md and vizra-sentinel-pr.md.
- Deploy: warroom.md §5 matches the AGENTS.md section (one rehearsal host, named in OWNER-DECISIONS.md first).
- No contradiction found. One note (FOLLOW-UP, D-1): verifier.md now lets the verifier write `docs/warroom/FOLLOWUPS.md` in the owner's main checkout, which the Stop hook will then report as an uncommitted tracked change until the chair commits it.

## What I could not or did not run

- The hook against the real checkout and the real `gh` (it would fetch and prune in the owner's four repos; outside my scratch directory). All hook results are from fixtures with a stub `gh`.
- The factual claims in `docs/warroom/RECONCILE-2026-11-10.md` and the PR body about the owner's local state ("about 25 merged branches", unpushed commits) and about `vizra-core` `govulncheck`. Not checked.
- Whether Claude Code loads `.claude/settings.json` and runs the hook on Stop in a live session. Only the JSON shape was read.
- Follow-ups were not written to `docs/warroom/FOLLOWUPS.md` (override from the dispatch); they are the tables above: H-1…H-7, G-1…G-11, D-1.

## Verdict

Every claim reproduced, all four demonstrations red then green, `ci-required` and `validate` green on the verified SHA, no BLOCKING finding, 19 follow-ups. PASS is not a merge and not VERIFIED; this PR edits `AGENTS.md` and `.claude/`, so the owner merges it.

FINAL VERDICT: PASS — SHA e796cca1e879ffa3f113292738ea2c8089e5333f
