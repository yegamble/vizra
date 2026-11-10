# After-merge steps, 2026-11-10: rulesets, triage of old work, local cleanup

Chair's record. Source: `gh` and `git` on 2026-11-10, after meta #11 merged as `82e9529` and meta #9 as `27be92a`. The three triage reads were done by read-only helpers; nothing below was independently verified. No product code changed.

## Rulesets (owner decision 2026-11-10 #3)

Created with `gh api -X POST repos/yegamble/<repo>/rulesets` and read back with `gh api repos/yegamble/<repo>/rulesets/<id>` and `gh api repos/yegamble/<repo>/rules/branches/main`.

| Repo | Ruleset id | Rules read back on `main` |
|---|---|---|
| vizra | 26967150 | deletion, non_fast_forward, required_linear_history, required_status_checks (`ci-required`, GitHub Actions app 15368) |
| vizra-user | 26967155 | the same |
| vizra-search | 26967161 | the same |
| vizra-core | none | NOT applied: `govulncheck` is a required lane and is red on `main`. Apply after the CI repair (queue 1) is green |

Enforcement active, target the default branch, no bypass actors (the owner is bound too), "branch must be up to date" off, no required reviews. `ci-required` was confirmed to run on pull requests in all four repos before applying.

## Triage of old work (owner decision 2026-11-10 #9)

Bar: a part gets one final round only if it fixes a defect that is exploitable or wrong on today's `main` for auth, privacy, data loss or a false-green product gate, with a trigger against `main`. Result: **nothing qualified; no final round was opened.**

### vizra-core #14 (`fix/m1a-sentinel-followups`), closed unmerged

Read against `origin/main` `27cee54`. Three commits that existed only locally were pushed first; the branch head is now `e43d501`.

| Part | Verdict | Reason |
|---|---|---|
| S-0002 re-mint can clear `consumed_at` of a token a racing claim just consumed (`store/queries/owner_claim.sql:45-50`) | FOLLOW-UP, closest call | The defect is real, but the re-opened token cannot be redeemed: the claim refuses once any user row exists (`owner_claim.sql:97`, `ownerclaim.go:403-409`, `:473-479`). Trigger needs the operator to run `vizra claim-token` in the same instant as the claim. Fix is about 45 lines and stands alone |
| S-0003 email validator against the DDL | FOLLOW-UP | wrong status code and a noisy log; nothing bad is stored |
| S-0004 `rate_limited` audit row per bucket | FOLLOW-UP | audit completeness |
| S-0005, S-0006 log wording and 503 causes | FOLLOW-UP | diagnosability |
| S-0007 `token_generation` on the audit row | FOLLOW-UP | audit enrichment |
| S-0009 strict body decode | FOLLOW-UP | the caller still needs the valid token; no bypass |
| S-0010 TTL lower bound | FOLLOW-UP | a bad TTL already fails closed at mint |
| `e8a8b66` (was unpushed): two `isOwnCancellation` tests, `ErrBusy` cause wrap, test-harness move | FOLLOW-UP | tests and logging |
| Verifier round-2 findings R1-F1, R1-F2, R1-F3, NIT-4, NIT-5 | below the bar | R1-F2 (`demonstrate.sh` scores a build failure as PASS) is a false green in an evidence script no workflow runs; it is queue 2ab |

The owner-claim routes are wired on `main` (`internal/httpapi/server.go:166-167`); no release exists.

### vizra-user #10 (`fix/lane-a-pixels-off`), closed unmerged

Read against `origin/main` `783483f`. 120 of its 132 files are regenerated demo transcripts; the change is 12 files.

| Part | Verdict | Reason |
|---|---|---|
| A recorders off in `playwright.config.ts` | FOLLOW-UP | main records pixels on failure, but Lane A drives only the placeholder home, `/health` and build markers |
| B static lane guard, C runtime recorder check, D upload gate | FOLLOW-UP | guards against a future spec; none exists on main |
| E demos and transcripts, F docs | FOLLOW-UP | tests and docs |

What main uploads today: on a red run only, `test-results/`, `playwright-report/results.json` and `playwright-browsers.txt`, kept 3 days (`e2e.yml:188-191`, `:239-247`). The job has `contents: read`, no `secrets.` reference, and no spec types into a field. No red-run artifact was downloaded to confirm. `e2e.yml:231-233` still says the repo is private; it is public (queue 2q).

The uncommitted allowlist re-plan (13 files in worktree `user-pr10-allowlist`) was committed as found, as one WIP commit `7fb1365`, and pushed as branch `allowlist/pr10-work`. It is UNVERIFIED and was not run. **The hard gate stands: no spec may authenticate, fill a credential or touch a signed URL before the artifact work lands (queue 2f).**

### vizra-search `feat/vendor-tool-second-manifest` and queue 2o

The branch (2 commits, tip `ed9f9cc`, 5 files, +791/-54) was never pushed; it is pushed now, with no PR. The helper ran its selftest (33 fixtures, exit 0) and `vendor-contract.py --check` (pass); `make ci` and CI did not run. It is tooling for a manifest that does not exist on main: FOLLOW-UP.

Queue 2o (one Makefile-anchor engine owned by core, vendored into search): none of 2o-1 to 2o-7 is done and none meets the bar. 2o-1 guards a Makefile rule neither repo has; 2o-2 is a false refusal, not a false green; 2o-3, 2o-4, 2o-6 are hardening and refactor; 2o-7 waits for `releases/`. The contract-drift lane never compares against core (by design, `Makefile:175-177`), so it would stay green if core's contract moved; today both vendored digests equal core `main`, so this is not a defect today.

## Local cleanup (plan step 17)

Free disk was 53 GiB, above the 15 GiB line of decision #6, so no caches were pruned. Worktrees and branches were removed under the approved plan and the "Git hygiene" rule, only where GitHub reports the PR merged and the local tip equals the merged PR head or is an ancestor of it. Every worktree was clean and was removed without force. A deleted branch can be restored from `refs/pull/<n>/head` on GitHub.

Removed worktrees (6): `meta-warroom-rework`, `meta-records`, `meta-ledger-m1a`, `meta-compose`, `core-m1-owner-claim`, `user-visibility`. Stale scratch entries under `/private/tmp` were pruned (metadata only; the directories were already gone). The three component checkouts were switched from merged branches to `main` and fast-forwarded: core `27cee54`, user `783483f`, search `4810048`.

Deleted local branches (31), with the tip each had:

- vizra `chore/warroom-loop-rework` `83384de6f107`
- vizra `chore/warroom-records-2026-09-23b` `57f8f2b330c5`
- vizra `docs/m1-warroom-records` `939b32d5f8b6`
- vizra `docs/m1a-ledger-obligations` `c3bb02edb2bb`
- vizra `feat/m0-compose-topology` `ddec39c34fe9`
- vizra `feat/m0-ledger-status` `e4c7be855d6d`
- vizra `fix/m1-selftest-fixture` `33d435cf8c8b`
- vizra-core `chore/m0-anchor-makefile-digest` `33b951aed7db`
- vizra-core `chore/m0-anchor-special-targets` `238a9cafc6c8`
- vizra-core `chore/m0-hardening-a` `1c12fd9e6eb4`
- vizra-core `chore/m0-hardening-b1` `0c1851ffa678`
- vizra-core `chore/m1-anchor-allowlist-grammar` `66fcb2e6976b`
- vizra-core `chore/m1-httpapi-redaction` `25f62ac6ff2b`
- vizra-core `chore/m1-test-stability` `e161af7bcecc`
- vizra-core `feat/m0-fixtures` `56920fec76c5`
- vizra-core `feat/m0-foundation` `b5f8f6aa0584`
- vizra-core `feat/m0-healthcheck-runtime-image` `68292851e768`
- vizra-core `feat/m1-owner-claim` `0cc906ed35b8`
- vizra-core `fix/m0-stabilise` `bfd2d5f3f550`
- vizra-user `chore/m0-hardening` `6b0ba871d3cc`
- vizra-user `chore/revendor-core-main` `ca23fefcc8cd`
- vizra-user `docs/public-artifact-visibility` `760cc8fa6bb8`
- vizra-user `feat/m0-browser-env` `3b566c3b057a`
- vizra-user `feat/m0-skeleton` `9767015444fa`
- vizra-user `fix/m0-artifact-privacy-a` `c2ff4454b28d`
- vizra-user `fix/m0-harness-hardening` `f0ee8f15a002`
- vizra-search `chore/m0-ci-hardening` `e068e07fed99`
- vizra-search `chore/m0-vizra-mode-rename` `cb02cdf19ddf`
- vizra-search `chore/revendor-core-4a80a1e` `2997e6427abd`
- vizra-search `chore/revendor-core-main` `744c60719dd1`
- vizra-search `feat/m0-minimal-service` `ab41219bb99c`

Kept, not deleted:

| Repo | Branch | Why |
|---|---|---|
| vizra | `chore/warroom-records-2026-09-21` | the main checkout is on it with 14 modified or untracked record files; all of that content is now on `main`, but the checkout is the owner's to switch |
| vizra | local `main` (`bf25303`) | stale and unrelated to `origin/main`; reset only on the owner's word |
| vizra | `docs/m1-manifest-wording` | PR #8 merged; the local tip `3572218` is an ancestor of the merged head `31bebdb`, but that head is on no local ref, so the tool guard refused the delete. Nothing local-only |
| vizra-core | `fix/m1a-sentinel-followups` (worktree `core-2t`) | PR #14 closed unmerged; pushed, `e43d501` |
| vizra-user | `fix/lane-a-pixels-off` (worktree `user-pixels-off`) | PR #10 closed unmerged; pushed |
| vizra-user | `allowlist/pr10-work` (worktree `user-pr10-allowlist`) | no PR; pushed, `7fb1365` |
| vizra-search | `feat/vendor-tool-second-manifest` (worktree `search-2o5-vendor`) | no PR; pushed, `ed9f9cc` |

The Stop hook will name the four unmerged branches and `docs/m1-manifest-wording` on every stop until they are resolved; that is its design (follow-up H-7).
