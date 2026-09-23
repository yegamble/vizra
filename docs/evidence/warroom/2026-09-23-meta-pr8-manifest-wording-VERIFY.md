# Verify: yegamble/vizra (meta) PR #8, queue 2j, manifest comment wording

| | |
|---|---|
| PR | https://github.com/yegamble/vizra/pull/8, branch `docs/m1-manifest-wording` |
| Head verified | `357221840ee17cfd0af87f0dfbf439dfe705096a` (read with `gh api repos/yegamble/vizra/pulls/8` at start and end: unchanged) |
| Branch base | `e4f625e` (the merge base). The PR is not rebased. |
| Current main | `b5829d8a950d46a6ed439e770e5043ea739b6fc4` (meta #10, merged 2026-09-23T23:11:11Z) |
| Verifier | fresh independent verifier. I did not write this change. |
| Environment | macOS arm64 (Darwin 25.5.0). CPython 3.12.11 in a scratch venv with PyYAML 6.0.3. CI uses 3.12.14; no 3.12.14 build was available locally. Docker 29.8.0, Compose 5.5.1, gh 2.98.0, git 2.50.1 |
| Clone | a fresh `mktemp -d` clone under the session scratchpad, with three worktrees: **head** (`3572218`), **main** (`b5829d8`), and **merge** (`890495c`, a local `--no-ff` merge of the head into `b5829d8`, which is what a refreshed `refs/pull/8/merge` would contain). Deleted when I finished. |

## Verdict summary

The change itself is correct. It touches comments only, the parsed manifest is byte-identical to main's, every new sentence holds against GitHub and the tree, and the full validate lane is green on the head merged into the current main.

**The CI gate is not met.** There is no green `validate` or `ci-required` on this SHA. The reopen run did start after `b5829d8` merged, but it tested a stale merge commit that does not contain `b5829d8`. Details are in §4. So the verdict is **BLOCKED**, not PASS.

## 1. Comments only; parsed manifest identical to main's

```
git diff origin/main...HEAD --stat   ->  .github/required-checks.txt | 16 +++++++++-------  (1 file)
git diff origin/main...HEAD -U0 | grep '^[+-]' | grep -v '^+++\|^---' | grep -vE '^[+-]#'   ->  (no output)
```

Every added or removed line starts with `#`. No blank line was added or removed.

I parsed the manifest with the same expression `ci-required.yml` and `ci-required-guard.sh` use (`grep -vE '^\s*(#|$)' .github/required-checks.txt | tr -d '\r'`):

| tree | parsed bytes (`od -c`) | sha256 of parsed list | `./scripts/ci-required-guard.sh` |
|---|---|---|---|
| head `3572218` | `v a l i d a t e \n` | `f607475c…2eea65` | exit 0 |
| main `b5829d8` | `v a l i d a t e \n` | `f607475c…2eea65` | exit 0 |
| merge `890495c` | `v a l i d a t e \n` | `f607475c…2eea65` | exit 0 |

`cmp` shows all three are identical. Each guard run printed `required checks: - validate`. It also reported that the negative fixtures were all rejected: workflow checker 6/6 (floor 6), pin checker 7/7 (floor 7), lane checker 10/10 (floor 10).

Selector on the merge tree: `printf 'validate\tcompleted\tsuccess\t…' | ./scripts/ci-required-select.sh "$(parsed list)"` exits 0 (`validate: success`).

## 2. R1: is every new sentence true?

| New sentence | Check | Result |
|---|---|---|
| "CODEOWNERS names the owner for this file" | `.github/CODEOWNERS` has `* @yegamble` and `/.github/ @yegamble` | **true** |
| "but CODEOWNERS is advisory" | `gh api repos/yegamble/vizra/rulesets` gives `[]`. `gh api repos/yegamble/vizra/rules/branches/main` gives `[]`. `…/branches/main/protection` gives 404 "Branch not protected". `…/branches/main` gives `protected:false`, `required_status_checks.enforcement_level:"off"`. The owner is a User account, so there are no org rulesets. CODEOWNERS itself says "NOTHING ENFORCES THIS FILE TODAY." | **true** |
| "the war room's verifier-gated merge is the only review" | AGENTS.md § Merge authorization (2026-09-20). The wording matches `docs/quality/COMMANDS.md:116` and `validate.yml` on main. | **true** |
| "The compose topology landed in meta #4" | `gh api …/pulls/4`: "M0 compose topology…", merged 2026-09-23T17:50:51Z as `b2c5b96`. `docker-compose*.yml` files are in the tree. | **true** |
| "`validate` renders and asserts it" | `validate.yml` steps: `compose-render.py --all --out build/compose-models`, `check-compose-topology.py`, `check-config-coverage.py`, `check-template-claims.py`, `compose-topology/demo.sh`. Run locally in §3: 13 shapes rendered and asserted. | **true** |
| "there is still no installer, no bundle builder and no booted stack" | `git ls-files` finds no `install.sh` or other installer and no bundle script. The only matches are `prompts/11-installer-and-recovery.md` (a prompt) and `docs/evidence/ledger-generator/s1_install_ops.py` (a ledger source). The only workflows are `ci-required.yml` and `validate.yml` (`gh api …/actions/workflows` lists exactly these two, both active). No workflow or script runs `compose up/run/start`, `docker run`, `docker build` or `docker pull`. | **true** |
| "so `bundle` and `boot` have nothing to run against. They are NOT listed here" | parsed manifest = `validate` only | **true** |
| (reflowed, not new) "listing a lane that does not exist would make `ci-required` wait forever" | Mutation in my scratch clone: appending `bundle` makes the guard exit 1 immediately with `VIOLATION reason=no-such-job lane=bundle`. With the guard bypassed, the selector returns 2 (pending) until the 1800 s deadline in `ci-required.yml`, then fails. | overstated; see FINDING 3 (pre-existing, NIT) |

PR body claims: "comment lines only" (true), "`validate` unchanged" (true), and "the last live occurrence of the claim". On the merged tree, no "owner-reviewed" or "CODEOWNERS puts it under owner review" wording remains outside `docs/evidence/` and `docs/plans/`, because meta #7 swept the rest, so that claim is true. The body's local-lane table records "`--self-test` 10/10" at `3572218`. That is true of the merged tree. At the head alone it is **no longer** true since meta #7 merged: I got 9/10 (see §3). The body was presumably written before #7 landed; the difference is time, not a fabrication.

## 3. Full meta validate lane, locally

Commands (each one is a `validate.yml` step, run in order from the tree root, with `GH_TOKEN` taken from `gh auth token` and never printed):

```
./scripts/ci-required-guard.sh
./scripts/check-generated-ledger.sh
git fetch --no-tags --depth=1 origin +refs/heads/main:refs/remotes/origin/main && ./scripts/check-ledger-status-output.py
(cd docs/evidence/ledger-generator && python3 -m unittest -v test_status)
python3 scripts/test_ledger_status_remote.py -v
./scripts/check-ledger-status-remote.py --self-test
./scripts/check-ledger-status-remote.py
bash docs/evidence/ledger-status/demo.sh
./scripts/check-quality-json.py
./scripts/check-doc-links.py
./scripts/compose-render.py --list && ./scripts/compose-render.py --all --out build/compose-models
./scripts/check-compose-topology.py build/compose-models
./scripts/check-config-coverage.py build/compose-models
./scripts/check-template-claims.py
bash docs/evidence/compose-topology/demo.sh
rm -rf build; git status --porcelain   # must be empty
```

| step | merge `890495c` (head + main `b5829d8`) | head `3572218` alone |
|---|---|---|
| ci-required-guard | exit 0 | exit 0 |
| generated ledger | exit 0, reproduces byte-for-byte (UTF-8 and C/POSIX) | exit 0 |
| ledger-status output | exit 0, 192 entries, 0 statuses, 0 records | exit 0 |
| unit `test_status` | exit 0, Ran 38, OK, 0 skipped | exit 0, 38 OK |
| unit `test_ledger_status_remote.py` | exit 0, Ran 13, OK, 0 skipped | exit 0, 13 OK |
| remote `--self-test` | **exit 0, 10/10 cases behaved as expected** | **exit 1, 9/10**: `evidence-not-on-meta-main` expected "EVIDENCE NOT ON META MAIN" but got "…VERIFY.md is on meta main but missing from this tree" |
| remote records | exit 0, 0 status records | exit 0 |
| ledger-status demo | exit 0, 61 passed / 0 failed, tree restored | exit 0, 61/0 |
| quality JSON | exit 0, 204 distinct ids, every one resolves | exit 0 |
| doc links | exit 0 | exit 0 |
| compose render | exit 0, 13 shapes (Compose 5.5.1 meets floor 2.24.4) | exit 0 |
| compose topology | exit 0, 13 shapes, 27 rules, 0 violations | exit 0 |
| config coverage | exit 0, 0 violations | exit 0 |
| template claims | exit 0 | exit 0 |
| compose demo (run sequentially) | **exit 0, 95 passed / 0 failed across 50 cases** | exit 0, 95/0 |
| tree clean afterwards | clean | clean |

The head-alone self-test failure is expected. The head predates meta #7, which put `2026-09-21-vizra-core-pr8-m1a-owner-claim-VERIFY.md` on main, and meta #10 (`b5829d8`), which retargeted that case at a fixture that never lands on main. CI tests the merge ref, not the head, so the merge column is the one that counts, and it is fully green.

**A note on my own first run.** I first ran the compose demo on both trees **in parallel**. Both runs failed (head 94/1, merge 75/20), and the merge tree was left with `docker-compose.yml` modified. The cause is that `demo.sh` uses fixed paths under `/tmp` (`/tmp/vizra-redaction-demo`, `/tmp/vizra-redaction-demo2`, `/tmp/vizra-r1-reg.bak`, `/tmp/vizra-r1-dc.bak`), so the two concurrent runs overwrote each other's backups. Run one after the other, both trees give 95/0 with a clean tree. This is not caused by this PR; see FINDING 2. CI runs one job per runner, so CI is unaffected. After the runs, none of those `/tmp` paths existed.

## 4. CI on this SHA (read with my own `gh api`)

`gh api repos/yegamble/vizra/commits/357221840ee17cfd0af87f0dfbf439dfe705096a/check-runs`:

| check-run id | name | conclusion | started |
|---|---|---|---|
| 107404111040 | validate | **failure** | 2026-09-23T22:11:31Z (run 35926922450) |
| 107404110993 | ci-required | **failure** | 2026-09-23T22:11:31Z (run 35926922514) |
| 107421525298 | validate | **failure** | 2026-09-23T23:11:34Z (run 35932328753, after the reopen) |
| 107421525098 | ci-required | **failure** | 2026-09-23T23:11:34Z (run 35932328653) |
| 107421521489 | GitGuardian Security Checks | success | 2026-09-23T23:11:31Z |

The reopen run did start after `b5829d8` merged (23:11:11Z). **But it did not test a tree containing `b5829d8`.** Its "record the environment" step printed:

```
PR base SHA (the base this was merged into):        608ffbfc09b23d04e1797a64cd2f923b0d17877d
TREE UNDER TEST (the merge commit actually checked out):
  29e694bcff9daed000fb7b73e93d1f91c2437a3a
```

The first (22:11) run printed the **same** tree, `29e694b`. `gh api …/commits/29e694b` gives parents `[608ffbf, 3572218]`, committed 2026-09-23T22:11:25Z. That means GitHub reused the test-merge commit it made an hour earlier. The close/reopen came 18 s after #10 merged, before GitHub recomputed the merge ref. At the end of this session `gh api …/pulls/8` still reports `merge_commit_sha: 29e694b…`. The reopen run failed at "every recorded ledger status is proved against GitHub" with `self-test: 9/10`, the same `evidence-not-on-meta-main` case as the head alone. `ci-required` failed because `validate: failure`.

I polled until more than 20 minutes after the reopen (see §6 for the last poll). No run on a refreshed merge ref appeared.

Note for the chair: a re-run of run 35932328753 will not help. A `pull_request` re-run reuses the same `GITHUB_SHA` (`29e694b`). The run needs a fresh `pull_request` event after `pulls/8` reports a `merge_commit_sha` whose first parent is `b5829d8` (or a later main). For example: wait for the recompute and then close/reopen, or have the builder merge or rebase main into the branch. The last option moves the head and needs a new verification.

## 5. Diff audit (AGENTS.md review list)

The diff is 9 comment lines added and 7 removed in one file. It has no code, workflow, test, baseline, budget, generated-file, dependency, secret or private-data content. The single entry `validate` is unchanged, so the floor lane is intact. No assertion was weakened and no case was skipped. This PR does not touch the thing the manifest guards: `validate.yml`, `ci-required.yml` and `scripts/` are unchanged vs main in the PR's diff.

## Findings

```
FINDING 1: No green validate / ci-required on 3572218 from a tree that contains b5829d8
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra
  files:     GitHub check-runs 107421525298 (validate), 107421525098 (ci-required); runs 35932328753, 35932328653
  requirements: none (gate condition, AGENTS.md § Merge authorization)

Observed:
  Both check-runs on 3572218 after the reopen concluded failure. The run logged PR base 608ffbf and
  tree under test 29e694b, the same tree as the 22:11 run. `pulls/8` merge_commit_sha is still 29e694b
  (parents 608ffbf, 3572218). The failure is `check-ledger-status-remote.py --self-test` 9/10
  (evidence-not-on-meta-main), which meta #10 fixed on main.

Failure:
  The merge precondition "ci-required green on the verified SHA" does not hold. The PR content is not
  the cause: the local merge of 3572218 into b5829d8 is fully green (§3). GitHub's test-merge ref
  was stale when the reopen fired.

Perspective:
  developer (war-room chair)

Recommendation:
  Trigger a fresh pull_request run once GitHub's merge ref for #8 includes b5829d8. Confirm with
  `gh api repos/yegamble/vizra/pulls/8 --jq .merge_commit_sha` and then
  `gh api repos/yegamble/vizra/commits/<that>` (parents[0] == b5829d8 or later), then close/reopen.
  A re-run of 35932328753 reuses 29e694b and will fail the same way.

Acceptance criteria:
  A validate and ci-required check-run on 3572218 with conclusion success, whose log prints
  "PR base SHA" = b5829d8 (or a later main) and a TREE UNDER TEST other than 29e694b.

Tests:
  The existing validate lane. No harness change is needed.

Cross-repo implications:
  core: none | user: none | search: none | meta: this is a known GitHub behaviour and worth a board
  note for any chair "close/reopen to refresh" step: check merge_commit_sha before reopening.

Challenge:
  The run did start after b5829d8 merged, which is the letter of the brief. But it tested a pre-#10
  tree, so it proves nothing about the merged state, and it is red regardless.
```

```
FINDING 2: compose-topology/demo.sh uses fixed /tmp paths; two concurrent runs corrupt each other and can leave the tree modified
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/compose-topology/demo.sh:566-620 (/tmp/vizra-redaction-demo, /tmp/vizra-redaction-demo2), :758-787 (/tmp/vizra-r1-reg.bak, /tmp/vizra-r1-dc.bak)
  requirements: none

Observed:
  demo.sh already uses BACKUP_DIR="$(mktemp -d)" at :48 for most backups, but these four paths are
  fixed. I ran it at the same moment in two worktrees: the results were 94/1 and 75/20, and one tree
  was left with docker-compose.yml modified. Run one after the other, the results were 95/0 and 95/0
  with clean trees.

Failure:
  Pre-existing and not introduced by this PR. On a machine shared by several war-room agents, two
  verifiers running the meta demo at once get false reds and a dirty tree (R12, and the
  2026-09-21 shared-scratch incident). CI is unaffected: one job per runner.

Perspective:
  developer

Recommendation:
  Put those four paths under the existing "$BACKUP_DIR" (or another mktemp -d), in a separate slice.

Acceptance criteria:
  Two concurrent `bash docs/evidence/compose-topology/demo.sh` runs in separate clones both report
  95/0 and leave clean trees.

Tests:
  Run it twice concurrently, as above.

Cross-repo implications:
  core: none | user: none | search: none | meta: demo.sh only

Challenge:
  The demo is documented as a single-run CI step, and the header's `tee /tmp/demo.txt` shows /tmp
  was a conscious choice. Concurrency is a local-only hazard.
```

```
FINDING 3: After this PR, validate.yml's header says the manifest "still says 'there is no compose file'"; and the manifest's "wait forever" is overstated
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra
  files:     .github/workflows/validate.yml:47-50 (on main b5829d8; the sentence starts on line 47 and the quote is on line 48); .github/required-checks.txt:25-26 (at 3572218)
  requirements: none

Observed:
  validate.yml:47-50 on main: "Its comment block still says "there is no compose file", which this PR
  does not edit … That stale sentence is REPORTED, not silently fixed." This PR removes that
  sentence, so once it merges the validate.yml comment is false (R1).
  Separately, the reflowed (not new) manifest sentence says an undefined lane "would make
  `ci-required` wait forever". Measured: the guard refuses it at once (`VIOLATION reason=no-such-job
  lane=bundle`, exit 1), and without the guard the fan-in times out at 1800 s.

Failure:
  Comment-only inaccuracies. No gate behaviour is affected.

Perspective:
  developer

Recommendation:
  In a later PR that does not touch required-checks.txt, drop or past-tense the validate.yml
  sentence. That PR must be separate, because the manifest is never edited alongside the thing it
  guards. Optionally, change "wait forever" to "fail: the guard refuses a lane with no job, and the
  fan-in would otherwise time out".

Acceptance criteria:
  `grep -n 'still says' .github/workflows/validate.yml` returns nothing on main.

Tests:
  none (comments).

Cross-repo implications:
  core: none | user: none | search: none | meta: validate.yml comment only

Challenge:
  The PR could not fix validate.yml without breaking the one-thing-per-PR rule it exists to respect.
  The staleness is a necessary consequence of the sequencing, not a defect in this change.
```

## 6. What did not run

- CI on a refreshed merge ref. None exists (FINDING 1).
- Local runs used CPython 3.12.11, not the 3.12.14 CI pins. The generated-ledger check passed byte-for-byte on 3.12.11.
- The artifact upload step (`actions/upload-artifact`) is Actions-only and was not reproduced.
- UI and browser checks do not apply: the change is comments in a CI manifest.

Final head re-read: `gh api repos/yegamble/vizra/pulls/8` gives head `357221840ee17cfd0af87f0dfbf439dfe705096a`, unchanged. The last CI poll is recorded below.

Last CI poll: 2026-09-23T23:35:15Z, 23 min 46 s after the reopen at 23:11:29Z. `actions/runs?head_sha=3572218…` returns only runs 35932328753 and 35932328653 (validate and ci-required, both failure, tree `29e694b`) and 35926922450 and 35926922514 (the 22:11 runs, both failure). `pulls/8` `merge_commit_sha` is still `29e694bcff9daed000fb7b73e93d1f91c2437a3a` and `updated_at` is 23:11:29Z. `gh api rate_limit`: 4818 core requests remaining, so no rate-limit condition applied. No rate-limit notice appeared in any tool result.

Missing input: a `pull_request` CI run on `3572218` whose merge ref includes `b5829d8`. Once that run is green, this verification can be re-read against it without re-running §1–§3, provided the head has not moved.

FINAL VERDICT: BLOCKED — SHA 357221840ee17cfd0af87f0dfbf439dfe705096a
