# Live-state reconcile, 2026-11-10

Read with `gh` (account `yegamble`) and `git` on the owner's machine, after `git fetch --prune` in all four repos. Nothing was changed in any repo to produce this. It is a snapshot; the next tick re-reads everything.

## Can CI run today? Yes

| Repo | Visibility | Actions | Evidence |
|---|---|---|---|
| yegamble/vizra | PUBLIC | enabled | last runs 2026-09-23 on PR #9: `validate` and `ci-required` success. Both lanes trigger on pull requests only, so there is no run on `main` |
| yegamble/vizra-core | PUBLIC | enabled | scheduled runs started and ran to completion on 2026-11-09 and 2026-11-10 (ids 42574177050, 42770496103) |
| yegamble/vizra-user | PUBLIC | enabled | `main` `783483f`, 2026-09-23: `ci-required`, `e2e`, `frontend-ci`, `contract-ci`, `supply-chain` success |
| yegamble/vizra-search | PUBLIC | enabled | `main` `4810048`, 2026-09-23: `ci` success |

No job was refused for billing. Old inbox item 0 is closed on this evidence. No pull-request run has happened since 2026-09-23, so "required lanes are green today" is unproven in every repo until a PR runs.

## Red on `main` today: vizra-core

- **`govulncheck` fails on `main` (`27cee54`) on every weekly run since 2026-10-12** (green on 2026-10-05). The 2026-11-09 run names 16 advisories: GO-2026-6603, 6605, 6607, 6608, 6610, 6611, 6612, 6613, 6617, 6809, 6873, 6876, 6877, 6879, 6881, 6883. The reported call paths go through `net/http`, HTTP/2, `crypto/x509` and Echo. `govulncheck` is in core's `.github/required-checks.txt`, so **every new vizra-core PR will fail `ci-required` until the toolchain and dependencies are bumped.** This is the first core slice.
- **`image-scan` fails on `main` on every scheduled run since 2026-09-22.** 2026-11-10: 69 findings at or above HIGH, 1 CRITICAL, 273 in total. Not a required lane (inbox 9).

## Rulesets and branch protection: none

`gh api repos/yegamble/<repo>/rulesets` returns `[]` and `branches/main/protection` returns 404 "Branch not protected" for all four. `ci-required` is advisory and CODEOWNERS is not enforced. The owner approved rulesets on 2026-11-10 (decision 3). Because core's `govulncheck` is red, applying "require `ci-required`" to vizra-core before the CI repair merges would block that repo; apply it there after the repair slice is green.

## Open pull requests

| Repo | PR | Branch | Head | State |
|---|---|---|---|---|
| vizra | #9 (draft) | `chore/warroom-records-2026-09-23b` | `ce2a352` | mergeable; `validate` and `ci-required` pass; GitGuardian fails (non-required). 18 files of records, ticks 239 to 257 |
| vizra-core | #14 | `fix/m1a-sentinel-followups` | `1d57ad8` | **conflicts with `main`**; checks on the head passed on 2026-09-23 except `image-scan`. The local worktree is 3 commits ahead of the PR and unpushed |
| vizra-user | #10 | `fix/lane-a-pixels-off` | `5c5c971` | mergeable; all checks pass. The local branch is 2 commits behind the PR head |
| vizra-search | none | | | |

vizra-core #15 merged on 2026-09-23 as `27cee54`; the board at tick 257 already says so.

## Work that exists only on this machine

Unpushed work does not exist for anyone else. None of it was touched.

1. **Records checkout** (`/Users/yosefgamble/github/vizra`, branch `chore/warroom-records-2026-09-21`). 5 modified and 9 untracked record files were compared with `chore/warroom-records-2026-09-23b`: 12 are byte-identical to that branch. Two hold content found nowhere else:
   - `docs/plans/2026-09-23-user-pr10-close-gate-scope.md` has 46 extra lines at the end, starting "### Chair's provisional rulings on § F (2026-09-23; the security seat may overrule)";
   - `docs/plans/2026-09-23-vizra-search-2o5-vendor-tool.md` (49 lines) is not on any branch.
2. **vizra-core `fix/m1a-sentinel-followups`** (worktree `.claude/worktrees/core-2t`): 3 unpushed commits; one is new work (`e8a8b66` "fix(ownerclaim): hold both halves of isOwnCancellation…"), then a merge of `main`.
3. **vizra-user worktree `.claude/worktrees/user-pr10-allowlist`** (branch `allowlist/pr10-work`, no upstream, tip equal to the PR #10 head): 13 modified or untracked files, uncommitted.
4. **vizra-search `feat/vendor-tool-second-manifest`** (worktree `.claude/worktrees/search-2o5-vendor`): 2 commits, never pushed, no PR.
5. **meta local `main`** is `bf25303`, 2 commits "ahead" of and 3 behind `origin/main` with no common ancestor. Both commits are contained in `origin/chore/warroom-records-2026-09-21`, so nothing is lost; the local ref is simply stale and should be reset only on the owner's word.

## Local branches and their pull requests

"[gone]" means the remote branch was deleted. A merged PR whose local tip differs from the PR head needs a look before the branch is deleted: `feat/m0-compose-topology` and search `chore/m0-ci-hardening` were checked and their local tips are ancestors of the merged head (nothing local-only); `docs/m1-manifest-wording` could not be checked (the merged head `31bebdb` is not in the local object store) and stays until it is.

### vizra

| Local branch | Tip | PR on GitHub | Against upstream |
|---|---|---|---|
| `chore/warroom-loop-rework` | `a1ffa28` | no PR | in sync / no upstream info |
| `chore/warroom-records-2026-09-21` | `935f25e` | no PR | in sync / no upstream info |
| `chore/warroom-records-2026-09-23b` | `ce2a352` | OPEN #9 | in sync / no upstream info |
| `docs/m1-manifest-wording` | `3572218` | MERGED #8 (tip differs from PR head 31bebdb) | [gone] |
| `docs/m1-warroom-records` | `939b32d` | MERGED #7 | [gone] |
| `docs/m1a-ledger-obligations` | `c3bb02e` | MERGED #5 | [gone] |
| `feat/m0-compose-topology` | `ddec39c` | MERGED #4 (tip differs from PR head 8e2a867) | [gone] |
| `feat/m0-ledger-status` | `e4c7be8` | MERGED #6 | [gone] |
| `fix/m1-selftest-fixture` | `33d435c` | MERGED #10 | [gone] |
| `main` | `bf25303` | no PR | [ahead 2, behind 3] |

### vizra-core

| Local branch | Tip | PR on GitHub | Against upstream |
|---|---|---|---|
| `chore/m0-anchor-makefile-digest` | `33b951a` | MERGED #10 | [gone] |
| `chore/m0-anchor-special-targets` | `238a9ca` | MERGED #11 | [gone] |
| `chore/m0-hardening-a` | `1c12fd9` | MERGED #6 | [gone] |
| `chore/m0-hardening-b1` | `0c1851f` | MERGED #9 | [gone] |
| `chore/m1-anchor-allowlist-grammar` | `66fcb2e` | MERGED #13 | [gone] |
| `chore/m1-httpapi-redaction` | `25f62ac` | MERGED #12 | [gone] |
| `chore/m1-test-stability` | `e161af7` | MERGED #15 | [gone] |
| `feat/m0-fixtures` | `56920fe` | MERGED #5 | [gone] |
| `feat/m0-foundation` | `b5f8f6a` | MERGED #1 | [gone] |
| `feat/m0-healthcheck-runtime-image` | `6829285` | MERGED #7 | [gone] |
| `feat/m1-owner-claim` | `0cc906e` | MERGED #8 | [gone] |
| `fix/m0-stabilise` | `bfd2d5f` | MERGED #4 | [gone] |
| `fix/m1a-sentinel-followups` | `e43d501` | OPEN #14 (tip differs from PR head 1d57ad8) | [ahead 3] |
| `main` | `eeeea06` | no PR | [behind 6] |

### vizra-user

| Local branch | Tip | PR on GitHub | Against upstream |
|---|---|---|---|
| `allowlist/pr10-work` | `5c5c971` | no PR | in sync / no upstream info |
| `chore/m0-hardening` | `6b0ba87` | MERGED #2 | [gone] |
| `chore/revendor-core-main` | `ca23fef` | MERGED #6 | [gone] |
| `docs/public-artifact-visibility` | `760cc8f` | MERGED #9 | [gone] |
| `feat/m0-browser-env` | `3b566c3` | MERGED #3 | [gone] |
| `feat/m0-skeleton` | `9767015` | MERGED #1 | [gone] |
| `fix/lane-a-pixels-off` | `b68294b` | OPEN #10 (tip differs from PR head 5c5c971) | [behind 2] |
| `fix/m0-artifact-privacy-a` | `c2ff445` | MERGED #8 | [gone] |
| `fix/m0-harness-hardening` | `f0ee8f1` | MERGED #7 | [gone] |
| `main` | `6bf0a0e` | no PR | [behind 2] |

### vizra-search

| Local branch | Tip | PR on GitHub | Against upstream |
|---|---|---|---|
| `chore/m0-ci-hardening` | `e068e07` | MERGED #5 (tip differs from PR head 1d28281) | [gone] |
| `chore/m0-vizra-mode-rename` | `cb02cdf` | MERGED #4 | [gone] |
| `chore/revendor-core-4a80a1e` | `2997e64` | MERGED #3 | [gone] |
| `chore/revendor-core-main` | `744c607` | MERGED #2 | [gone] |
| `feat/m0-minimal-service` | `ab41219` | MERGED #1 | [gone] |
| `feat/vendor-tool-second-manifest` | `ed9f9cc` | no PR | in sync / no upstream info |
| `main` | `3ea4103` | no PR | [behind 1] |

## Worktrees

| Repo | Path | Branch | Note |
|---|---|---|---|
| vizra | `.claude/worktrees/meta-compose` | `feat/m0-compose-topology` | PR #4 merged; clean |
| vizra | `.claude/worktrees/meta-ledger-m1a` | `docs/m1a-ledger-obligations` | PR #5 merged; clean |
| vizra | `/private/tmp/claude-501/…/scratchpad/meta-rec` | `chore/warroom-records-2026-09-23b` | directory gone; prunable |
| vizra-core | `.claude/worktrees/core-2t` | `fix/m1a-sentinel-followups` | PR #14 open; unpushed commits |
| vizra-core | `.claude/worktrees/core-m1-owner-claim` | `feat/m1-owner-claim` | PR #8 merged; clean |
| vizra-user | `.claude/worktrees/user-pixels-off` | `fix/lane-a-pixels-off` | PR #10 open; clean, behind |
| vizra-user | `.claude/worktrees/user-pr10-allowlist` | `allowlist/pr10-work` | uncommitted work |
| vizra-user | `.claude/worktrees/user-visibility` | `docs/public-artifact-visibility` | PR #9 merged; clean |
| vizra-search | `.claude/worktrees/search-2o5-vendor` | `feat/vendor-tool-second-manifest` | unpushed, no PR |
| vizra-search | two under `/private/tmp/claude-501/…/scratchpad/b2o5-TexgaJ/` | detached | directories gone; prunable |

Free disk: 56 GiB (87 % used).

## Ledger

`docs/evidence/ledger-generator/status_records.json` on `origin/main` (`a1ffa28`) has `"records": []`. The ledger has 192 entries (191 plus `VZ-AUDIT-001` from meta #5), all PLANNED / UNVERIFIED. `python3 scripts/warroom-check.py stall --replay docs/warroom/TICK-LOG.md` reports 252 logged ticks and 0 ledger status changes.

## Not checked

- Whether the required lanes pass on today's `main` in vizra, vizra-user and vizra-search: nothing has run there since 2026-09-23.
- Actions usage and spending limits: the token has no billing scope. Jobs start, which is the fact that matters.
- The contents of the 13 uncommitted files in the vizra-user allowlist worktree.
