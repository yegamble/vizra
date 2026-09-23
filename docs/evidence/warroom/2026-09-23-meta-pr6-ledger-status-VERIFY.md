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
