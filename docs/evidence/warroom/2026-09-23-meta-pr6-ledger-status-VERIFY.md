# Independent verification: meta PR #6, queue 2i "the ledger can record status, but only with evidence"

- Repo / PR: `yegamble/vizra` #6, branch `feat/m0-ledger-status`
- Head verified: `36913d2926ac2e5af4ab878f158764f089f24b83`, confirmed with `gh pr view` at the start and at the end. Base `b2c5b96c8dc19d7f6b4f55b5dd649a75461dbf71`.
- Verifier: war-room independent verifier. I did not write this code. Date: 2026-09-23.
- Environment: macOS arm64 (Darwin 25.5.0), `/usr/bin/python3` 3.9.6 (plus 3.10.20 and 3.13.13), gh 2.98.0 (authenticated), Docker Compose v5.5.1. The machine was heavily loaded (load average about 260).
- Clone: a fresh `git clone` at the head in `mktemp -d …/scratchpad/vzv-meta-pr6-XXXXXX`. Mutations ran in a second copy (`mut/`) in the same directory. The directory was deleted at the end. Nothing was edited, pushed, merged or approved.

## 1. Lanes (my runs, clean clone at the head)

| Step | Command | Exit | Result |
|---|---|---|---|
| a | `./scripts/check-generated-ledger.sh` | 0 | reproduces |
| a2 | `(cd docs/evidence/ledger-generator && python3 -m unittest -v test_status)` | 0 | 30 tests, 30 ok, 0 skipped |
| a2 | `./scripts/check-ledger-status-remote.py --self-test` | 0 | 8/8 cases as expected |
| a2 | `./scripts/check-ledger-status-remote.py` | 0 | "0 status records" |
| a2 | `bash docs/evidence/ledger-status/demo.sh` | 0 | `demo: 26 passed, 0 failed`; tree restored |
| b | `./scripts/check-quality-json.py` | 0 | 204 distinct ids resolve |
| c | `./scripts/check-doc-links.py` | 0 | |
| guard | `./scripts/ci-required-guard.sh` | 0 | pins, lane integrity and continue-on-error fixtures all rejected as required |
| compose | `bash docs/evidence/compose-topology/demo.sh` | not completed locally | I stopped it at case 14 of 50 after about 22 minutes: the load average was about 230 and every assertion up to that point had passed. This slice does not change it. CI ran it on this SHA: 95 passed, 0 failed (below). |
| generator | `build.py` under 3.9.6, 3.10.20, 3.13.13 and `LC_ALL=C` | 0 | byte-identical to the committed `features.json` (3.12 in CI, via step a) |

**GitHub CI on the head:**
- `validate`: check-run 107331511385, `completed/success`, github-actions.
- `ci-required`: check-run 107331512934, `completed/success`, github-actions.
- Workflow runs: 35905343018 (validate) and 35905343199 (ci-required), both `pull_request` on `36913d2`.

I read the CI logs with `gh run view --log`:
- the unit step printed `Ran 30 tests … OK`;
- the remote step printed `gh version 2.100.0`, `self-test: 8/8` and "0 status records";
- the demo printed `demo: 26 passed, 0 failed`;
- the compose demo printed `RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`;
- `ci-required` polled until `validate: success` and printed `ci-required: every required check succeeded on 36913d2…`.

The manifest (`.github/required-checks.txt`) lists `validate`, and that job ran. No listed lane was left unexecuted.

## 2. Demonstrations reproduced

**D1–D5.** All 26 red and green cases reproduced through `demo.sh`: D1a, D1b, D1c, D2a, D2b, D2c, D3 (online), D4 × 3, D5a and D5b. Each red case named the stated reason, and every restore went back to green.

**Offline checker, `status.py`.** I applied 11 mutations, one at a time, then ran `python3 -m unittest test_status`. The builder's five are the first five below; I added six. Every one went red, and the restored file went back to OK:

| Mutation | Test that goes red |
|---|---|
| no head comparison | `test_verdict_sha_mismatch_is_refused` |
| any status recordable | `test_unknown_status_is_refused_by_name` |
| no ui floor | `test_ui_surface_needs_a_user_merge` |
| verdict anywhere, not final | `test_fail_as_final_line_is_refused` and `test_pass_not_on_the_final_line_is_refused` |
| no DSL default check | two DslDefaults tests |
| no api floor | `test_api_surface_needs_a_core_merge` |
| no issue floor | `test_every_scheduling_issue_must_be_cited` |
| no evidence-in-DSL check | `test_hand_asserted_evidence_is_refused` |
| VERIFIED needs no file | `test_verified_with_no_evidence_is_refused` (ERROR) |
| bullet not verbatim | `test_bullet_must_be_verbatim_and_in_acceptance` |
| no symlink check | `test_symlinked_evidence_is_refused` |

**Online checker.** I applied 7 mutations and ran `--self-test` after each. The builder's four reproduced exactly:
- on-main check removed: 7/8;
- ci-required conclusion ignored: 7/8;
- head comparison removed: 6/8;
- merged flag ignored: 7/8.

**Two more mutations stay GREEN (8/8), so no test covers them:**
- `if base != "main":` → `if False:`
- the `github-actions` app-slug filter → `if True`

See FINDING 2.

## 3. Attempts to get a status past the gate

| # | Attempt (scratch only) | Outcome |
|---|---|---|
| 1 | hand-edit `features.json` and commit | **caught**: D1c, `GENERATED FILE IS NOT REPRODUCIBLE` |
| 2a | section source: `REQS[-1]["implementation_status"]="VERIFIED"` | **caught**: D1b, HAND-ASSERTED |
| 2b | section source: `"PLANNED "` (trailing space) or `"verified_at_sha"` (lowercase) | **caught**: HAND-ASSERTED |
| 2c | section source: extra keys `REQS[-1]["status"]="VERIFIED"; REQS[-1]["verified"]=True` | **ESCAPED**: `features.json` carries `"status": "VERIFIED", "verified": true` on VZ-CONTROLS-001; the whole lane is green (see below) |
| 2d | section source: `class _S(str): __ne__ → False`; `implementation_status=_S("VERIFIED")` | **ESCAPED**: VZ-CONTROLS-001 `implementation_status: VERIFIED`, `by_implementation_status {'PLANNED':191,'VERIFIED':1}`, zero records; lane green, including demo 26/0 |
| 2e | section source (s0): wraps `status.check_dsl_defaults` to drop its own id's errors, then sets VERIFIED / VERIFIED_AT_SHA | **ESCAPED**: VZ-CI-005 `VERIFIED / VERIFIED_AT_SHA`, zero records; lane green, including demo 26/0 |
| 2e′ | same, but replacing the function globally | caught, but only indirectly: demo D1b turns red (25/1) |
| 3 | evidence: PASS earlier, FAIL as the last line | **caught**: `does not END with a PASS verdict` |
| 4a | verdict line with a trailing space or tab | **caught** (refused, fails closed) |
| 4b | en dash, hyphen, `--`, U+2212, NBSP inside, uppercase SHA, leading space, `**bold**`, lowercase, fenced | **caught** (each refused) |
| 4c | CRLF line endings; an NBSP-only last line | admitted, which is correct: the verdict is still the last content |
| 4d | `FINAL VERDICT: PASS (superseded — FAIL on re-run) — SHA <head>` | **ESCAPED**: the qualifier is free text (FINDING 4) |
| 5a | user #8 record with user #3's head `3b566c3…` | **caught**: `head is c2ff445…, but the record's verified_head is 3b566c3…` |
| 5b | user #8 record with user #3's head AND merge `f49bca4…` | **caught**: head and merge_commit_sha mismatches |
| 6 | meta #3 (merged into `chore/m0-meta-baseline`; merge `4920786…` is on main now, compare `ahead`, behind 0) | **caught**: `targets 'chore/m0-meta-baseline', not main`. **With that guard deleted, the record is admitted and the self-test is still 8/8** (FINDING 2) |
| 7a | `ci-required` from a non-Actions app only (stub `gh`) | **caught**: `no ci-required check-run from GitHub Actions` |
| 7b | Actions `failure`, then a later non-Actions `success` (stub) | **caught**: latest Actions run `completed/failure` |
| 7c | Actions `success`, then a later Actions `failure`; Actions `skipped` (stub) | **caught** |
| 7d | 7a against the app-filter-deleted mutant | **admitted** (`OK: 1 status record(s)`), and no test notices (FINDING 2) |

**Whole lane with 2c, 2d or 2e committed in a scratch copy.** Each result was the same:
- `check-generated-ledger` = 0
- unit = 0
- remote = 0 ("0 status records")
- quality-json = 0
- doc-links = 0
- `demo.sh` = 0 (26/0) for 2c, 2d and 2e

## 4. Offline versus online split

**Fail-closed.**
- No `gh` on PATH: exit 2 (`BLOCKED`) in both modes.
- Bogus `GH_TOKEN`: `--self-test` exits 1 ("Bad credentials", 1/8).
- No auth at all: `--self-test` exits 1 (gh exit 4, 1/8).
- In CI, `--self-test` runs first under `set -euo pipefail`, so the step fails closed.
- Records mode with 0 records exits 0 even with no auth. It is protected only because the self-test comes first (NIT 3).

**Could the online check pass with zero records while a record exists that it did not read?** Through the records file, no:
- both halves call `status.load_records` on the same path;
- with duplicate `records` keys, the last one wins in both halves.

However, a status can reach `features.json` with **zero records** (2d, 2e). The online half never reads `features.json`, so it reports "0 status records" and passes (FINDING 1).

## 5. Workflow change

- Three steps were added to the existing `validate` job. No job was added, so the manifest is unchanged and still correct.
- Job-level `permissions`: `contents: read`, `checks: read`, `pull-requests: read`. The top level stays `contents: read`. Everything is read-only. The two extra scopes matter only if a record names the meta repo itself; that is justified in a comment and acceptable.
- `GH_TOKEN` is passed to the remote step and to `demo.sh`, which needs it for D3.
- Every `uses:` in both workflows is pinned by full SHA (checkout, setup-python, upload-artifact). The PR adds no action.
- `ci-required-guard.sh` exits 0 locally and in CI.

## 6. Builder's refusals

**VZ-FOUND-008 via user #8, withheld as "narrower".** This is the right reading.
- The ledger outcome requires E2E "against the production Next.js build and real API/PostgreSQL/Redis … axe checks", and the success case is "E2E lane boots stack".
- `vizra-user` main `783483f` has none of it: no axe dependency in `package.json`, no compose, postgres or redis path in its 341-file tree, and the app has only `health`, `layout` and `page`.
- The VZ-ISSUE-001 bullet is narrower than the ledger entry, so recording VERIFIED would overstate it.
- UNVERIFIED by me: whether user #8's V-D finding is still open.

**VZ-INSTALL-003, the ui floor.** This is the right reading, not too strict.
- The outcome itself says "the claim page creates the owner", and `ui: ["/setup/claim"]`.
- `vizra-user` main has no setup or claim route.

**VZ-FOUND-007.** This is also right.
- VZ-ISSUE-006 schedules it too.
- The outcome includes ICC, video and 360 fixtures.
- `2026-09-21-vizra-core-pr5-fixtures-VERIFY.md` at `b331f63` has no `FINAL VERDICT` line; its last line is a cleanup note.

**Cited facts.** Every `ci-required` check-run id in `README.md` matches what `gh api` returns:
- core `56920fe` → 106186425769
- user `3b566c3` → 106171959382
- user `c2ff445` → 107288308319
- core `0cc906e` → 107288249394

All four are success from github-actions. `2026-09-20-vizra-user-pr3-browser-env-VERIFY.md` has no `FINAL VERDICT` line. user #8's closing evidence ends with `PASS (local; CI BLOCKED) — SHA c2ff4454…`.

## 7. Doc sentences checked under "no false-guarantee merges"

| Sentence | Where | Verdict |
|---|---|---|
| "Nobody can write a status by hand." | `docs/evidence/ledger-status/README.md` | **false** (2d, 2e) |
| "A section source can never set a status." | `status.py` rule 1 | **false** (2d, 2e) |
| "The generator refuses a status written anywhere else" | `features.json` notice, generated from `build.py` | **false** (2d, 2e) |
| "THE RULES (default-deny: anything not explicitly admitted below is refused by name)" | `status.py` | **false** for requirement-entry keys (2c) |
| "(e) … written into a section source … by hand … Steps (a) and (a2)" | `validate.yml` header | **false** (2c, 2d, 2e) |
| "a record … stops being true later (a force-pushed main, a PR re-opened) turns the lane red" | README | overstated: the lane runs only on `pull_request` and `merge_group`, and a merged PR cannot be reopened (NIT 1) |

Accurate:
- COMMANDS.md ("Without gh … exits 2 (BLOCKED, never a pass)"; the counts 30, 8/8, 0, 26/0).
- The README table of online rules. Each rule is enforced; two are untested (FINDING 2).
- The README floors ("They set a minimum and do not prove the requirement is complete").
- The candidate table.
- R-N1 and R-N2 in VZ-AUDIT-001: the text is carried in `s2_identity.py` and regenerated.

## Findings

```
FINDING 1: A status reaches features.json from a section source, with zero records, and the whole validate lane stays green
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-generator/status.py:79-94 (check_dsl_defaults), build.py:1-5,21-24, scripts/check-ledger-status-remote.py:150-159
  requirements: queue 2i acceptance 1 (a status "can never be hand-asserted: a status written into a section source is refused by name")

Observed:
  check_dsl_defaults compares values with `!=` inside the same Python process that has just imported every section source, and it never checks which keys a requirement carries. I committed each of these in a scratch copy, regenerated features.json, and ran the lane:
  (2c) REQS[-1]["status"]="VERIFIED"; REQS[-1]["verified"]=True → features.json carries both keys; build exit 0.
  (2d) class _S(str): def __ne__(self,o): return False ; REQS[-1]["implementation_status"]=_S("VERIFIED") → VZ-CONTROLS-001 VERIFIED, summary {'PLANNED':191,'VERIFIED':1}, status_records.json empty.
  (2e) in s0_foundation.py: import status as _st; _orig,_mine=_st.check_dsl_defaults,REQS[-1]["id"]; _st.check_dsl_defaults=lambda reqs:[e for e in _orig(reqs) if not e.startswith(_mine+":")]; then set VERIFIED / VERIFIED_AT_SHA → VZ-CI-005 VERIFIED / VERIFIED_AT_SHA with zero records.
  For 2c, 2d and 2e alike: check-generated-ledger 0, unit 0, remote 0 ("0 status records"), quality-json 0, doc-links 0, demo.sh 0 (26/0).

Failure:
  The ledger can show VERIFIED for an entry that no record, no verdict and no merge supports, and every gate in the lane reports green. The online half cannot notice, because it reads only status_records.json and never features.json.

Perspective:
  developer, instance-admin (anyone who trusts the ledger's statuses)

Recommendation:
  Add an out-of-process cross-check that parses the committed docs/quality/features.json as plain JSON, without importing any section source, and asserts:
  (a) every feature has exactly the key set core.req emits;
  (b) the ids whose four status fields differ from PLANNED/UNVERIFIED/NOT_STARTED/NOT_RELEASED, or whose `evidence` is non-empty, are exactly the ids in status_records.json;
  (c) for each such id, the values are what the record admits.
  Put it in check-quality-json.py or check-ledger-status-remote.py. Also make check_dsl_defaults use `type(got) is str and got == want`.

Acceptance criteria:
  Probes 2c, 2d and 2e, each committed in a scratch copy with features.json regenerated, turn the validate lane red with a named reason. Zero records with a VERIFIED entry is refused.

Tests:
  Three demo.sh cases (the extra key, the str subclass, and the targeted wrapper of check_dsl_defaults), each committed in the D1c-style scratch copy and each red naming the cross-check. Plus a unit test for the key allowlist.

Cross-repo implications:
  core: none | user: none | search: none | meta: validate lane

Challenge:
  2d and 2e are deliberately adversarial Python in a reviewed diff; editing status.py itself is just as visible. But 2c is plain data. And the slice's whole claim is that the gate is mechanical rather than review-dependent: it says "never", "by anything" and "default-deny". A cross-check in a separate process is cheap and closes all three.
```

```
FINDING 2: Two online guards (PR base is main; ci-required must come from GitHub Actions) have no test, so deleting either stays green
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra
  files:     scripts/check-ledger-status-remote.py:89-91, :117; scripts/testdata/ledger-status/remote-cases.json
  requirements: queue 2i acceptance 2 ("merged into main") and 3 (ci-required)

Observed:
  Mutant `if base != "main":` → `if False:` gives --self-test 8/8 (exit 0) and demo 26/0. A real record then passes the whole check: yegamble/vizra #3 (base chore/m0-meta-baseline, head f9b85537…, merge 4920786…, which is now on main: compare ahead, behind 0) gives "OK: 1 status record(s) proved against GitHub".
  Mutant: the app-slug filter set to always true gives self-test 8/8. With a stub gh returning only a non-Actions "ci-required" success, the result is "OK".
  At the verified head both guards are correct: probes 6 and 7a–7c were refused.

Failure:
  Two of the online rules this PR claims are not demonstrated. A later edit can remove either rule and the lane stays green. AGENTS.md says "Tests must challenge the implementation", and the README says the checkers are "mutation-tested" without noting these two gaps.

Perspective:
  developer

Recommendation:
  Add a self-test case for yegamble/vizra #3 (IMPLEMENTED, true head and merge commit, expected red naming "targets 'chore/m0-meta-baseline', not main"). For the app filter, add a unit test that injects gh_api (it is a module-level function) returning a non-Actions ci-required success, and expects "no ci-required check-run from GitHub Actions".

Acceptance criteria:
  Each of the two mutants turns a named test or self-test case red. Restored, everything is green.

Tests:
  scripts/testdata/ledger-status/remote-cases.json: a new case. A new unit test for check_merge with an injected gh_api.

Cross-repo implications:
  none

Challenge:
  The code is correct today. But this slice exists to make the gate mechanical and the tests self-challenging, and the base-main rule already has a real counterexample on GitHub.
```

```
FINDING 3: Docs and the generated notice promise that a status cannot be written by hand, which FINDING 1 disproves
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-status/README.md ("Nobody can write a status by hand."), status.py:19-24 (default-deny; rule 1), build.py notice → docs/quality/features.json "notice" ("The generator refuses a status written anywhere else"), .github/workflows/validate.yml header (e)
  requirements: queue 2i

Observed:
  See section 7 of this record and FINDING 1 (probes 2c, 2d, 2e).

Failure:
  A false guarantee sits in the generated ledger itself and in the lane's header.

Perspective:
  developer

Recommendation:
  Resolved by FINDING 1's cross-check. Otherwise, reword each sentence to say what is actually enforced.

Acceptance criteria:
  Every sentence in section 7 is true against the probes in section 3.

Tests:
  The probes of FINDING 1.

Cross-repo implications:
  none

Challenge:
  The sentences describe intent. But under the war room's no-false-guarantee rule (core #12 FAIL for a redaction overclaim), intent written as a guarantee is a finding.
```

```
FINDING 4: The verdict qualifier is free text, so "PASS (superseded — FAIL on re-run)" is admitted
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-generator/status.py:64 (VERDICT_RE `(?: \([^()\n]*\))?`)
  requirements: queue 2i acceptance 3

Observed:
  Final lines "FINAL VERDICT: PASS (superseded — FAIL on re-run) — SHA <head>" and "FINAL VERDICT: PASS (NOT; retracted) — SHA <head>" both give build exit 0, and VERIFIED is admitted.

Failure:
  A verdict that negates itself is counted as PASS.

Perspective:
  developer

Recommendation:
  Allowlist the qualifiers actually in use, for example none or exactly "(local; CI BLOCKED)", and refuse every other qualifier by name.

Acceptance criteria:
  Both lines above are refused. The existing "(local; CI BLOCKED)" form is still admitted.

Tests:
  test_status Evidence: a qualifier-not-allowlisted case.

Cross-repo implications:
  none

Challenge:
  Verifiers are agents under our control, and the online ci-required rule still applies.
```

**NITs (not blocking):**
1. README: "a PR re-opened" cannot happen to a merged PR. Also, `validate` triggers only on `pull_request` and `merge_group`, so a record that becomes false stays green on `main` until the next meta PR.
2. The issue floor accepts any verbatim bullet from the scheduling issue, even one about a different requirement. For example, the FOUND-008 bullet would satisfy VZ-ISSUE-001's floor for FOUND-007. VZ-ISSUE-001's bullets are id-tagged ("(VZ-FOUND-00n)"), so where an issue tags its bullets, the floor could require the cited bullet to name the record's id.
3. With 0 records, `check-ledger-status-remote.py` exits 0 without proving `gh` auth. That is safe only because `--self-test` precedes it in the same step.

## Summary

Every lane the builder claimed reproduces, CI is green on this SHA, and I reproduced D1–D5 and the builder's 9 checker mutations. All three refusals of candidates are correct readings of the ledger. However:
- the central guarantee, that a status comes only from a checked record, is escaped by a few lines in a section source, and the entire lane stays green (FINDING 1, with the docs that promise otherwise in FINDING 3);
- two online guards have no test (FINDING 2).

No status is recorded by this PR, so nothing false is in the ledger today. But the gate as merged would not stop one.

FINAL VERDICT: FAIL — SHA 36913d2926ac2e5af4ab878f158764f089f24b83

---

# Re-verification at b694813 (fix round 1 of 2)

- Head verified: `b694813fd63ce12cf2be403ad80ef448cbe41ca6`, confirmed with `gh pr view` at the start and at the end. Base `b2c5b96`.
- Commits since `36913d2`: `1996d1c`, `19ba567`, `f32f9a8`, `b694813`.
- Clone: fresh, in `mktemp -d …/scratchpad/vzv-meta-pr6r1-XXXXXX`, deleted at the end.
- Environment: as in round 0 (macOS arm64, Python 3.9.6, gh 2.98.0).

## R1. Lanes (my runs)

| Step | Command | Exit | Result |
|---|---|---|---|
| a | `./scripts/check-generated-ledger.sh` | 0 | reproduces |
| a2 | `./scripts/check-ledger-status-output.py` | 0 | 192 entries, exact key set, 0 statuses, 0 records |
| a2 | `(cd docs/evidence/ledger-generator && python3 -m unittest -v test_status)` | 0 | 35 tests, 0 skipped |
| a2 | `python3 scripts/test_ledger_status_remote.py -v` | 0 | 9 tests, all ok |
| a2 | `./scripts/check-ledger-status-remote.py --self-test` | 0 | 9/9 |
| a2 | `./scripts/check-ledger-status-remote.py` | 0 | 0 records |
| a2 | `bash docs/evidence/ledger-status/demo.sh` | 0 | `demo: 47 passed, 0 failed`; tree restored |
| b, c, guard | `check-quality-json.py`, `check-doc-links.py`, `ci-required-guard.sh` | 0 / 0 / 0 | |

**CI, read with my own `gh api`:**
- `validate`: check-run 107361901343, success, github-actions.
- `ci-required`: check-run 107361899706, success, github-actions.
- Workflow runs: 35914343009 and 35914342918, both `pull_request`.

The `validate` log shows the checkout of `refs/remotes/pull/6/merge`, "HEAD is now at 0fa3d82 Merge b694813… into b2c5b96…", and then:
- output check: 192 entries, 0 statuses;
- unit tests: `Ran 35` and `Ran 9`;
- self-test: 9/9;
- remote check: 0 records;
- demo: 47/0;
- compose demo: 95/0.

`ci-required` logged: every required check succeeded on `b694813…`.

## R2. Demonstrations reproduced

- **Through `demo.sh`:** D1c now names both the output check and the regeneration check. D6a, D6b-i, D6b-ii and D6c are each red by name and then green. D7 (`is NOT ALLOWLISTED`) and D8 (`the cited bullet does not name VZ-FOUND-007`) are red, then green.
- **Output checker.** I built my own escape branches in a scratch git copy: 2c, 2d with a wrapper, 2e, and a tampered summary. Then I ran a mutated copy of the checker on each. Results:
  - key-set check deleted: 2c passes (load-bearing);
  - set-equality deleted: 2d and 2e still refused, by RE-DERIVATION MISMATCH;
  - re-derivation deleted: 2d and 2e still refused, by STATUS WITHOUT A RECORD;
  - both deleted: 2d and 2e pass;
  - summary check deleted: the tampered summary passes (not demonstrated in the demo, but it is not claimed there).

  The builder's `output-mutations.txt` claims match what I saw.
- **Online checker.** I made 11 mutations and ran the unit tests and the self-test after each:
  - base guard deleted: unit test red, self-test 8/9;
  - app filter deleted: 2 unit tests red;
  - anonymous-limit test deleted: unit test red;
  - on-main check deleted: unit test red, self-test 8/9;
  - conclusion check deleted: 3 unit tests red;
  - `max` → `min`: unit test red;
  - merged flag, head comparison and merge-SHA deleted: self-test red.

  Not caught:
  - removing the `prove_auth()` call site in `main()` (unit tests test the function, not the call);
  - removing the one-page cap on check-runs.

  Both are NITs.
- **`status.py`.** Reverting the type check to `!=`, deleting the qualifier allowlist, and deleting the tagged-bullet check each turn a named test red. The head comparison, ui floor and final-line checks are still covered. Reverting the evidence check to `ev != []` is not caught by a unit test. The output check covers that case.

## R3. Escape attempts

| # | Route (scratch copy, regenerated and committed) | Outcome |
|---|---|---|
| 2c | extra `status`/`verified` keys | **caught** by the output check: `KEY SET differs … extra ['status', 'verified']` |
| 2d | `str` subclass, with a wrapper that hides it from the in-process check | **caught**: `STATUS WITHOUT A RECORD` |
| 2e | targeted wrapper around `check_dsl_defaults` (VZ-CI-005) | **caught**: `STATUS WITHOUT A RECORD` |
| Q | `PASS (superseded — FAIL on re-run)` | **caught**: `is NOT ALLOWLISTED` |
| N1 | a status in allowed free-text fields: `notes="STATUS: VERIFIED at SHA c2ff445… (ci-required green)"`, `title+=" [VERIFIED]"`, `test_ids=["VERIFIED"]` | **passes**, lane green. These are prose fields, not status fields, so the stated guarantee does not cover them (NIT). `test_ids` is always `[]` from `core.req`, yet it is not pinned. |
| N2a | a unicode-lookalike extra key `implementation_ѕtatus` (Cyrillic ѕ) | **caught**: KEY SET (extra) |
| N2b | the real key replaced by a lookalike | **caught**: the generator refuses it (`implementation_status None`); the output check fails closed |
| N3 | **duplicate JSON keys.** A section source replaces `json.dump`, so the generator writes `"implementation_status": "VERIFIED", "verification_status": "VERIFIED_AT_SHA",` immediately before VZ-CONTROLS-001's real `"implementation_status": "PLANNED"` | **ESCAPED**: `check-generated-ledger` 0 (reproducible from the tampered source), output check 0, quality-json 0. The committed `features.json` contains, at line 11251, `"implementation_status": "VERIFIED"` and `"verification_status": "VERIFIED_AT_SHA"` for VZ-CONTROLS-001, with zero records. Python `json`, `jq` and `node` all keep the last value (PLANNED), so no parser in use is fooled. But the file as read by a person, `grep` or the GitHub file view carries a status no record admits. See FINDING R-2. |
| N4 | BOM prepended by a patched `json.dump` | **caught**: fails closed (the regeneration check and the output check both exit non-zero with a JSON decode error) |
| N5 | a record whose values are all admissible, with its evidence file written by the same PR (not on meta main: `contents/…?ref=main` returns 404) | **admitted by every check**: generator (`statuses={'PLANNED': 191, 'VERIFIED': 1}`), regeneration, output check (1 status, 1 record, sets equal), remote check (`ci-required` 107288308319 success; `OK: 1 status record(s)`), quality-json, doc-links. Nothing checks that the evidence file was written by a verifier or landed before the record. The builder's own judgement is the only thing that kept VZ-FOUND-008 out. See FINDING R-3. |
| N6 | the PR also edits `check-ledger-status-output.py` | defeats it, trivially. The docs now declare this "not defended", which is honest, but they give CODEOWNERS review as the mitigation, and that is false (FINDING R-1) |

## R4. Is "tree matches HEAD" sound in CI's merge-ref checkout?

Yes.
- `actions/checkout` checks out `refs/remotes/pull/6/merge`. HEAD is that merge commit (`0fa3d82`) and the tree equals it, so the output check reads exactly the merged ledger that would land.
- The only earlier step that writes to a pinned path is the regeneration check. It regenerates `features.json` in place and fails the job if the bytes differ, so a passing run leaves no diff.
- None of the pinned paths is gitignored.
- Locally, a modified `docs/issues/VZ-ISSUE-001.md` is refused (`TREE DIFFERS FROM HEAD`), and so is an untracked `docs/evidence/warroom/untracked.md` (`UNTRACKED FILE`).

## R5. The narrowed sentences

| Sentence (new in this round) | Where | Verdict |
|---|---|---|
| "a status with no record (however it was produced) turns the validate lane red" | the notice in `build.py` and `features.json` | false for the duplicate-key route (N3), taking "status in this file" to include its raw text |
| "this holds however the status was produced: … a generator monkeypatched in-process" | README:8–13 | same (N3) |
| "Not defended: a pull request that edits the checkers themselves, which is a CODEOWNERS-reviewed path." | notice | **false** |
| "That change is visible in the diff and owner-reviewed under CODEOWNERS." | README:17 | **false** |
| "visible in the diff and owner-reviewed under CODEOWNERS" | `validate.yml:36` | **false** |
| "A PR that edits status.py or this script is itself a visible, CODEOWNERS-reviewed change" | `check-ledger-status-output.py:35-36` | **false** |

Why the CODEOWNERS sentences are false:
- `.github/CODEOWNERS` itself says "NOTHING ENFORCES THIS FILE TODAY. CODEOWNERS is advisory until a ruleset requires owner review".
- `gh api repos/yegamble/vizra/branches/main/protection` → 404 "Branch not protected".
- `gh api repos/yegamble/vizra/rulesets` → `[]`.
- Under AGENTS.md's verifier-gated merge authorization, the chair merges on a verifier PASS without owner review.

Accurate, as far as I can see:
- the rest of the notice and README (the output check's steps; "runs on meta pull requests and merge-queue entries, not on main after a merge");
- `status.py`'s new "WHAT THIS MODULE CAN AND CANNOT ENFORCE";
- COMMANDS.md (exits and counts; anonymous `gh` → exit 2);
- the `validate.yml` step comments.

The same unenforced-CODEOWNERS wording already existed before this PR, in `scripts/ci-required-guard.sh:6`, `check-generated-ledger.sh:17` and `ci-required-select.sh:12`. It is out of scope here, but it is the same defect.

## Round-0 findings: status

- **FINDING 1:** resolved. The output check refuses 2c, 2d and 2e by name, and my mutations show it is load-bearing.
- **FINDING 2:** resolved (base guard, app filter).
- **FINDING 3:** partly resolved. The overclaims are narrowed, but the new CODEOWNERS mitigation sentence is false (R-1).
- **FINDING 4:** resolved.
- **NIT 1:** resolved.
- **NIT 2:** resolved (tagged bullets).
- **NIT 3:** resolved (`rate_limit` auth proof), though the call site is untested.

## Findings (round 1)

```
FINDING R-1: The "not defended" caveat names CODEOWNERS review as the mitigation, and nothing enforces CODEOWNERS
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-generator/build.py:60 → docs/quality/features.json "notice"; docs/evidence/ledger-status/README.md:17; .github/workflows/validate.yml:36; scripts/check-ledger-status-output.py:35-36
  requirements: queue 2i

Observed:
  .github/CODEOWNERS says "NOTHING ENFORCES THIS FILE TODAY." `gh api repos/yegamble/vizra/branches/main/protection` gives 404 Branch not protected. `gh api repos/yegamble/vizra/rulesets` gives []. War-room merges are verifier-gated, not owner-reviewed.

Failure:
  The generated ledger's own notice tells a reader that edits to the checkers are owner-reviewed. They are not. A PR that edits the checker and records a status merges on a verifier PASS alone.

Perspective:
  developer, business (the owner relying on the ledger)

Recommendation:
  Replace "CODEOWNERS-reviewed" / "owner-reviewed under CODEOWNERS" with what is true: "visible in the PR diff and judged by the war-room verifier; CODEOWNERS names the owner for these paths but is advisory until a ruleset enforces it". Regenerate features.json.

Acceptance criteria:
  No sentence added by this PR states or implies enforced owner review.

Tests:
  None (a docs change). `git grep -n "CODEOWNERS"` over the four files shows only the corrected wording.

Cross-repo implications:
  none (the same wording in scripts/ci-required-guard.sh, check-generated-ledger.sh and ci-required-select.sh predates this PR; the chair may route it separately)

Challenge:
  The owner intends to apply a ruleset. But intent written as a present-tense guarantee, inside the generated ledger itself, is the defect this slice exists to prevent.
```

```
FINDING R-2: The output check parses duplicate JSON keys leniently, so a status can sit in features.json's text while the lane is green
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra
  files:     scripts/check-ledger-status-output.py:91-94 (json.load with no object_pairs_hook)
  requirements: queue 2i acceptance 1

Observed:
  Probe N3. A section source replaces json.dump so that "implementation_status": "VERIFIED" and "verification_status": "VERIFIED_AT_SHA" are written just before VZ-CONTROLS-001's real keys. Regenerated and committed, with zero records: check-generated-ledger 0, check-ledger-status-output 0, check-quality-json 0. json.load, jq and node all read PLANNED, and the raw file carries VERIFIED at line 11251.

Failure:
  It contradicts the README's "however the status was produced: … a generator monkeypatched in-process". RFC 8259 leaves duplicate-name behaviour to the parser, and a reader of the file sees a status that no record admits.

Perspective:
  developer

Recommendation:
  In the output check, load both JSON files with `object_pairs_hook` that raises on a repeated key (at every nesting level). Add a demo case that commits N3 and expects a named refusal.

Acceptance criteria:
  N3, regenerated and committed, turns the output check red, naming the duplicated key and the entry.

Tests:
  demo.sh: a D6d case (json.dump replaced to emit a duplicate key) that is red by name, then green on reset.

Cross-repo implications:
  none

Challenge:
  Every parser in use reads PLANNED, so no tool is misled today. The fix is three lines, though, and the sentence it falsifies was written to close my round-0 finding.
```

```
FINDING R-3: A VERIFIED record's evidence file can be written by the same PR that records the status
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/ledger-generator/status.py (check_evidence_file), scripts/check-ledger-status-remote.py
  requirements: queue 2i acceptance 3

Observed:
  Probe N5 added, in one commit, a status record for VZ-FOUND-008 (vizra-user #8, true head and merge) and a new docs/evidence/warroom/2026-09-23-self-minted-VERIFY.md ending "FINAL VERDICT: PASS — SHA c2ff4454…". Every check passed. The file is not on meta main (contents API returns 404). The notice calls it "the verifier's evidence file", but nothing checks authorship or that the file landed first.

Failure:
  VERIFIED can rest on a verdict that the recording PR wrote itself. Only review of the record stops it, which is the builder's judgement today.

Perspective:
  developer, business

Recommendation:
  Online half: require each evidence_file to exist on the meta repo's main with identical bytes, via `gh api repos/{owner}/vizra/contents/<path>?ref=main`, so that the verdict landed through the chair's records path before the record. Or state the limit in the notice ("the checks do not establish who wrote the evidence file").

Acceptance criteria:
  N5 is red naming the evidence file not being on main, or the notice states the limit.

Tests:
  A self-test case (a real warroom file that is on main, admitted) and an injected unit test (a 404 on contents is refused).

Cross-repo implications:
  none

Challenge:
  The record PR itself goes through an independent verifier. But that is judgement, not mechanism, and "the verifier's evidence file" implies mechanism.
```

**NITs:**
1. `test_ids` (always `[]` from `core.req`) and prose fields can carry "VERIFIED" (N1). Pinning `test_ids == []` in the output check is cheap.
2. Removing the `prove_auth()` call site in `main()`, or the one-page check-run cap, is caught by no test.
3. Removing the summary check is caught by no demo. It is load-bearing against a tampered summary.

## Verdict

**Fixed:** the round-0 escapes are fixed and demonstrated, the two untested guards are now tested, and CI is green on this SHA.

**Still failing:**
- one new sentence written as the mitigation for what is not defended claims CODEOWNERS enforcement that does not exist (R-1);
- a duplicate-key route still leaves a hand-made status in the committed ledger with the lane green (R-2).

Both are small fixes.

FINAL VERDICT: FAIL — SHA b694813fd63ce12cf2be403ad80ef448cbe41ca6

---

# Re-verification at e4c7be8 (fix round 2 of 2, the last)

- Head verified: `e4c7be855d6dac447b7fa42a4791c41d8d1cd227`, confirmed with `gh pr view` at the start and at the end. Base `b2c5b96`.
- The only commit since `b694813` is `e4c7be8`.
- Clone: fresh, in `mktemp -d …/scratchpad/vzv-meta-pr6r2-XXXXXX`, deleted at the end.
- Environment: macOS arm64, Python 3.9.6, gh 2.98.0.

## Lanes (my runs)

| Step | Command | Exit | Result |
|---|---|---|---|
| a | `./scripts/check-generated-ledger.sh` | 0 | reproduces |
| a2 | `./scripts/check-ledger-status-output.py` | 0 | 192 entries, exact key set, 0 statuses, 0 records |
| a2 | `(cd docs/evidence/ledger-generator && python3 -m unittest -v test_status)` | 0 | 38 tests, 0 skipped |
| a2 | `python3 scripts/test_ledger_status_remote.py -v` | 0 | 13 tests, 0 skipped |
| a2 | `./scripts/check-ledger-status-remote.py --self-test` | 0 | 10/10, including `evidence-not-on-meta-main` |
| a2 | `./scripts/check-ledger-status-remote.py` | 0 | 0 records |
| a2 | `bash docs/evidence/ledger-status/demo.sh` | 0 | `demo: 61 passed, 0 failed`; tree restored |
| b, c, guard | quality-json, doc-links, `ci-required-guard.sh` | 0 / 0 / 0 | |

**CI, read with my own `gh api`:**
- `validate`: check-run 107376010435, success, github-actions.
- `ci-required`: check-run 107376010342, success, github-actions.
- Workflow runs: 35918466595 and 35918466616.

The `validate` log shows, in order:
- the checkout of the merge ref, "HEAD is now at 6f6fd96 Merge e4c7be8… into b2c5b96…";
- the new fetch, `* [new branch] main -> origin/main`;
- the output check: 192 entries, 0 statuses;
- the unit tests: `Ran 38`, `Ran 13`;
- the self-test: 10/10;
- the remote check: 0 records;
- the demo: 61/0, with D10b red as required, online against real `main`;
- the compose demo: 95/0.

`ci-required` logged: every required check succeeded on `e4c7be8…`. Its manifest lists `validate`, which ran.

## Demonstrations and mutations reproduced

**Demo cases.** D9 (`DUPLICATE KEY 'implementation_status' in entry VZ-CONTROLS-001`), D9b (`NON-CANONICAL BYTES`), D10a, D10b and D11 are each red by name, then green.

**Online checker.** Five mutations, each red:

| Mutation | Result |
|---|---|
| evidence-on-main call removed | unit test red, self-test 9/10 |
| blob-SHA comparison removed | `test_evidence_must_be_on_meta_main_byte_identical` red |
| API-error branch disabled | 2 unit tests red, self-test 9/10 |
| `prove_auth` call site removed | `test_main_proves_auth_even_with_zero_records` red |
| one-page cap removed | `test_more_than_one_page_of_check_runs_is_refused` red |

**`status.py`.** Deleting the `test_ids` DSL check, deleting the records duplicate-key hook, or reverting the evidence check to `ev != []` each turns its named test red.

**Output checker.** I built my own committed escape branches in a scratch copy, then ran a mutated copy of the checker on each:
- N3 (duplicate key);
- a non-canonical `json.dump`;
- `test_ids` = `["VERIFIED"]` behind a wrapper;
- a tampered summary;
- a VERIFIED record whose evidence is on a scratch `origin/main` (control);
- the same record with its evidence bytes changed in the PR;
- the same record citing a case-variant path.

| Mutation | Effect |
|---|---|
| duplicate-key hook removed | N3 still red, by NON-CANONICAL BYTES |
| canonical-bytes check removed | N3 still red, by DUPLICATE KEY; the non-canonical route passes |
| both removed | N3 passes |
| `test_ids` pin removed | the `test_ids` route passes |
| evidence-on-main call removed | bytes-differ and case-variant both pass |
| evidence byte comparison removed | bytes-differ passes |
| summary check removed | the summary route passes |

Every guard is load-bearing for its route. The one guard no test covers is noted in NIT 3.

## Escape attempts

| Route | Outcome |
|---|---|
| my round-1 N3 (a replaced `json.dump` writes duplicate status keys) | **caught**: `DUPLICATE KEY 'implementation_status' in entry VZ-CONTROLS-001` (the generator and the regeneration check stay green, as the demo shows) |
| a duplicate `records` key in `status_records.json` | **caught** by the generator (`STATUS RECORDS DO NOT PARSE`), the output check (`DUPLICATE KEY 'records'`) and the remote check (`REFUSED`) |
| feature key order swapped | **caught**: `KEY SET … order differs` |
| summary key order reversed | the output check passes, the regeneration check refuses it; not a status field |
| trailing newline; trailing space; CRLF | **caught**: NON-CANONICAL BYTES |
| `"PLANNED"` and `"VERIFIED"` as escapes; the whole file `ensure_ascii=True` | **caught**: NON-CANONICAL BYTES |
| `1.92e2` for `total` | **caught**: NON-CANONICAL BYTES |
| `192.0` for `total`; `Infinity` in `notes` | pass the output check (they round-trip through Python's `json`), and the regeneration check refuses both. Neither is a status field (NIT 1) |
| `NaN` as a status value | refused (exit 1), but by a `TypeError` crash in the summary sort, so the named errors are lost (NIT 2) |
| a VERIFIED record whose evidence is on (scratch) `origin/main`, byte-identical | admitted, the control case |
| a record citing a file on main whose last line is a PASS for a different SHA (`3b566c3…` versus a verified head of `c2ff445…`) | **caught**: `VERDICT SHA MISMATCH` |
| an evidence path that is a symlink (on main and in the tree) | **caught** by the generator (`symlink or escapes`) and the output check (`EVIDENCE DIFFERS FROM META MAIN`) |
| the path through a directory symlink (`warroom/sub -> .`) | the generator admits it; **caught** by the output check (`EVIDENCE NOT ON META MAIN`), because git does not traverse tree symlinks |
| a case variant (`PROBE-OK-VERIFY.md`; macOS resolves it locally) | the generator admits it; **caught** by the output check (`EVIDENCE NOT ON META MAIN`) |
| the evidence file edited in the PR (bytes differ from main) | **caught**: `EVIDENCE DIFFERS FROM META MAIN` (online: blob-SHA compare, unit-tested) |
| a stale `origin/main` that lacks the file | **caught**, fails closed: `EVIDENCE NOT ON META MAIN` |
| `origin/main` absent | **caught**, fails closed: "refused, not skipped" |

**Is the `origin/main` fetch in CI shallow or stale?**
- It is shallow (depth 1) and taken at the moment the step runs, so it is the tip of `main` then.
- Only that tip's tree is needed for `git show origin/main:<path>`, so depth 1 is enough.
- A merge ref that predates a later change to the file on main is red, not green: the bytes differ.
- In the merge queue, the ref already contains main.
- A record whose evidence later disappears from main is caught only at the next meta PR. The notice states this ("not on main after a merge").

## Sentences under the "no false-guarantee merges" rule

**R-1 is resolved.** Every CODEOWNERS sentence this PR added now says what is true:
- the generated notice: "No mechanism enforces review of such a change today (CODEOWNERS is advisory: no branch protection or ruleset requires it); the war room's verifier-gated merge is the only review";
- `README.md:21-25`;
- `validate.yml:35-38`;
- `check-ledger-status-output.py:45-48`.

**R-3 wording.** "so a PR cannot cite evidence it introduces itself" is demonstrated true (D10a, D10b and my probes). "Also not established: who wrote an evidence file, beyond that it is on meta main with identical bytes" is honest.

**Other checked sentences.** "free-text fields such as notes and title are not status fields and are not checked for status words" is honest. So is "(probed: a hand edit, a section source, an extra key, a str subclass, an in-process wrapper, a replaced json.dump)". The README statement that queue 2u is a prerequisite is also true: no file under `docs/evidence/warroom/` on `origin/main` ends with a `FINAL VERDICT` line, and the core #8 and user #8 verifier files are on `chore/warroom-records-2026-09-21` only.

**Imprecise, not a status guarantee (NIT 1).** "refuses … any byte that differs from the generator's own serialisation" is broader than the output check alone. It compares the bytes with the serialisation of its own parse, so `192.0` passes it. The same lane's regeneration check refuses those bytes, and no status can travel that way.

**Older wording, out of scope, predating this PR.** "owner-reviewed under CODEOWNERS" or "CODEOWNERS puts it under owner review" appears in:
- `.github/workflows/validate.yml:219` (line 143 at base `b2c5b96`);
- `docs/quality/COMMANDS.md:116`;
- `scripts/check-generated-ledger.sh:17,157`;
- `scripts/ci-required-guard.sh:6`;
- `scripts/ci-required-select.sh:12`.

This is the same unenforced-CODEOWNERS claim. The chair should route it as a separate slice; it is not this PR's change.

## Round-1 findings: status

- **R-1 (REQUIRED):** resolved (above).
- **R-2 (REQUIRED):** resolved. Duplicate keys are refused at every level in both files, the canonical-bytes rule backs that up, and both are load-bearing.
- **R-3 (SHOULD):** resolved. Evidence must be on meta main and byte-identical, checked offline and online; demonstrated.
- **Round-1 NITs:** all resolved:
  - `test_ids` is pinned;
  - the auth call site and the page cap are tested;
  - the summary has D11.

## Remaining (all NIT, none blocking)

1. **Wording.** The notice and README say the output check refuses "any byte that differs from the generator's own serialisation". The output check itself admits round-tripping re-typings such as `192.0` or `Infinity` in `notes`. The regeneration check in the same lane refuses them, and no status route exists. Suggested wording: "…from the serialisation of its own parse; the regeneration check covers the rest".
2. **Crash on a non-string status.** A non-string status value such as `NaN` makes the output check exit 1 through a `TypeError` in the summary sort. It fails closed, but the named `STATUS WITHOUT A RECORD` error is lost.
3. **Untested offline byte comparison.** The offline "EVIDENCE DIFFERS FROM META MAIN" comparison has no demo or unit test; deleting it is caught by nothing offline. The online blob-SHA comparison covers the same fact, is unit-tested, and runs in the same lane.

## Verdict

Every acceptance bullet in scope reproduced for me on this SHA:
- a status only from a committed record;
- `IMPLEMENTED` and `VERIFIED` proved against GitHub;
- VERIFIED needs a PASS on the verified head, with its evidence already on meta main;
- default-deny;
- no status recorded;
- R-N1 and R-N2 carried into VZ-AUDIT-001.

CI is green on this SHA. Every escape I tried in three rounds is now refused by name. The limits the docs declare (a PR that edits the checkers; who wrote an evidence file; the lane runs only on PRs) are stated truthfully. No blocking finding is open.

This PASS is not a merge and not VERIFIED in the ledger; the chair records those.

FINAL VERDICT: PASS — SHA e4c7be855d6dac447b7fa42a4791c41d8d1cd227
