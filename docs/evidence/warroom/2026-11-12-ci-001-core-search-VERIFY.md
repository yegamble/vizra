# VZ-CI-001 — vizra-search#6 + vizra-core#21 independent verify (2026-11-12)

Heads checked at start and end (gh pr view): search 0e93164b562a05ad0e591d5d81de2dc7a761d888, core 71a1ff3103e709b91ed93d4fe22e2b722d2d6862 — unchanged.
Env: macOS darwin, fresh full clones under mktemp scratch; base = `git merge-base HEAD origin/main` exported as CI_REQUIRED_BASE_SHA; guard run as `./scripts/ci-required-guard.sh` (the ci-required.yml step).

## A. Diff scope
Both: manifest header doc, ci-required.yml env CI_REQUIRED_BASE_SHA, guard .sh/.py tombstone check, scripts_test.go. Core also build-test.yml job env and 3 test call sites gaining `sameBaseManifest` (makefile-pins tests, not tombstone tests). No lane removed/renamed/made optional seen. Core .sh: any --manifest/--base-manifest arg skips git lookup; CI invokes with no args (ci-required.yml:53, Makefile:105), so the real path resolves the true base.

## B. Mutations (guard exit code)
| # | case | search | core |
|---|---|---|---|
|0|clean|0|0|
|1|delete lane, no tombstone|1 names 'fmt'|1 names 'fixtures'|
|2a|valid tombstone non-floor|tombstone ok ('retired: [tidy-check]') but guard 1 from pinned-steps coupling|N/A: every core lane is a floor lane → 1|
|2b|tombstone floor lane|1|1|
|3|tombstone no reason|1 malformed|1 malformed|
|4|comment out|1|1|
|5|delete base tombstone|1 'tombstone ... deleted'|1|
|6|shallow depth=1, no origin/main|1 BASE MANIFEST UNAVAILABLE|not run|
|7|rename required job|**0** (static guard does not catch)|**0**|
|8|continue-on-error on required job|1|1|

## C/D/E
NOT RUN within time budget: t.Skip mutation on noskip lanes, `go test ./scripts/` counts, reading the four breakage run logs. CI on heads: all manifest lanes + ci-required success on exact heads (core image-scan failure, not in manifest).

## Findings
- UNVERIFIED (S2): rename passes the static guard in both repos; S2 relies on the fan-in step failing on a missing lane result — not demonstrated by me. Needs verification before PASS.
- FOLLOW-UP: search 2a green path is blocked by pinned-steps coupling for fmt/tidy-check; core has no retirable lane.

[SUPERSEDED by completion below] PR VERDICT vizra-search#6: BLOCKED — SHA 0e93164b562a05ad0e591d5d81de2dc7a761d888
[SUPERSEDED by completion below] PR VERDICT vizra-core#21: BLOCKED — SHA 71a1ff3103e709b91ed93d4fe22e2b722d2d6862

[SUPERSEDED by completion below] FINAL VERDICT: BLOCKED — SHA 0e93164b562a05ad0e591d5d81de2dc7a761d888 71a1ff3103e709b91ed93d4fe22e2b722d2d6862

---
## Completion by second independent verifier (2026-11-12)
Heads re-checked via `gh pr view`: search 0e93164b…, core 71a1ff31… unchanged. Fresh full clones in mktemp scratch (deleted afterwards).

**S2, renamed job (resolves the UNVERIFIED item above).** Static guard: rename gives exit 0 (as found). The fan-in catches it. Search `ci-required.yml:77-104` calls `scripts/ci-required-select.sh`. When a required name is missing, the script prints `fmt: NEVER RAN` and exits 2 (pending). The loop polls until the 1800 s deadline, then `exit 1` ("a check that never ran is not a pass"). Local fixture: TSV of every required lane as success except `fmt` → `fmt: NEVER RAN`, select exit 2 → workflow exit 1. Core `ci-required.yml:59-118`: the inline step was extracted and run with a stub `gh` that omits `append-only`, deadline set to 0, under bash 5. Output: `PENDING append-only (no check run reported yet)`, `::error::timed out…`, exit 1. A renamed job cannot turn ci-required green. Cost: about 25–30 min of latency, not a false green.

**Mutation 6, core shallow clone.** `--depth=1` at 71a1ff3, CI_REQUIRED_BASE_SHA unset → `BASE MANIFEST UNAVAILABLE…`, exit 1.

**D.** `go test -count=1 -json ./scripts/`: search exit 0, 29 top-level pass / 0 fail / 0 skip. Core exit 0, 44 pass / 0 fail / 0 skip.

**R1, named regression tests (they ran in D and passed).** Search: `TestRemovingAManifestLaneNeedsATombstone` (scripts_test.go:2587), `TestTheShellGuardFailsClosedWithoutABaseManifest` (:2650), `TestTheRepositoryFloorsCoverEveryPackage` (:892). Core: `TestRemovingAManifestLaneNeedsATombstone` (:1077), `TestTheGuardFailsClosedWithoutABaseManifest` (:1124), `TestTheGuardRejectsAnEmptyManifest` (:1137), `TestGoTestReportRefusesASuiteWithNoFloor` (:877). The empty selection case is also refused inline in search's ci-required.yml:66-70.

**N1.** I added `t.Skip("x")` to `TestRemovingAManifestLaneNeedsATombstone` in both repos and fed the result through `go-test-report.py --floors scripts/test-floors.json` (the lane's command). It hit my 88 s tool limit before reporting. Both files were restored from backup and `git status` was clean. **NOT RUN to completion. UNVERIFIED.**

**E, breakage evidence.** All run heads are ancestors of the PR heads (`merge-base --is-ancestor` = 0). Search red job 131231204263 (1eb8eaf): `FAIL required lane 'docker-build' was removed from the manifest without a tombstone`. Search "green" job 131232969753 (63cb2a8): the guard step is ok (11 lanes compared, 6 floor lanes present). The ci-required job conclusion is still `failure`, from a later step on that intermediate SHA, so this is guard-green, not job-green. Core red run 43237242458 (3d7ad9c): same FAIL naming `docker-build`. Core green run 43239712800 = head 71a1ff3, success. ci-required on the exact heads: search success @0e93164b…, core success @71a1ff31….

| case | search#6 | core#21 |
|---|---|---|
|S1 removed lane fails|PASS (mut 1)|PASS (mut 1)|
|S2 rename fails ci-required|PASS (fan-in NEVER RAN→exit 1)|PASS (PENDING→exit 1)|
|N1 skip fails noskip lane|UNVERIFIED|UNVERIFIED|
|N2 continue-on-error/comment-out|PASS (mut 4, 8)|PASS (mut 4, 8)|
|R1 regression tests|PASS|PASS|
|only-success fan-in|PASS (select.sh: only `success`)|PASS (case: only success)|
|SHA pins / base resolution|PASS (mut 6)|PASS (mut 6 shallow)|
|breakage evidence|PASS (green = guard step only)|PASS|

Findings: no blocking defect. FOLLOW-UP (from verifier 1): search `fmt`/`tidy-check` tombstones are blocked by the coupling in pinned-steps.yml; core has no lane it can retire. FOLLOW-UP: in both repos a renamed lane fails only at the fan-in deadline, 25–30 min later.

[SUPERSEDED by third verifier below] PR VERDICT vizra-search#6: BLOCKED — SHA 0e93164b562a05ad0e591d5d81de2dc7a761d888
[SUPERSEDED by third verifier below] PR VERDICT vizra-core#21: BLOCKED — SHA 71a1ff3103e709b91ed93d4fe22e2b722d2d6862

[SUPERSEDED by third verifier below] FINAL VERDICT: BLOCKED — SHA 0e93164b562a05ad0e591d5d81de2dc7a761d888 71a1ff3103e709b91ed93d4fe22e2b722d2d6862

---
## Completion by third independent verifier (2026-11-12): N1
I checked the heads with `gh pr view` at the start and at the end. They had not moved: search 0e93164b562a05ad0e591d5d81de2dc7a761d888, core 71a1ff3103e709b91ed93d4fe22e2b722d2d6862. I worked in fresh clones in mktemp scratch `$D` (vzv-ci001d-3MuGcI), which I deleted afterwards. `git status` was clean after each restore.

**Lane read.** Search `.github/workflows/ci.yml:181-195` (test-noskip) runs `go test -count=1 -json ./... > unit-events.json`, then `python3 scripts/go-test-report.py --events unit-events.json --suite unit --floors scripts/test-floors.json --go-exit-file unit-exit.txt || exit 1`. Core `.github/workflows/build-test.yml:244-250` runs the same with `-race -count=1 -timeout 8m`. The lane takes no package argument, so I gave the report script a `go test -json` of one package, using the lane's flags and arguments. `allowed_skips` is `{}` in both real `test-floors.json`.

**Mutation.** I added `t.Skip("x")` as the first line of search `internal/buildinfo.TestSearchSchemaVersionIsAbsent` and of core `internal/config.TestValidProductionEnvironmentLoads`.

**Run 1, real floors file (`--floors scripts/test-floors.json`):**
- Search, mutated: go test exit 0. Report EXIT=1 with `SKIPPED: github.com/yegamble/vizra-search/internal/buildinfo.TestSearchSchemaVersionIsAbsent` (8 problems).
- Search, restored: EXIT=1 with 7 problems. These are only the suite and package floors, because only one package ran.
- Core, mutated: EXIT=1 with `SKIPPED: github.com/yegamble/vizra-core/internal/config.TestValidProductionEnvironmentLoads` (19 problems).
- Core, restored: EXIT=1 with 18 problems (floors only).
- In both repos the skip is exactly the one extra problem.

**Run 2, exit-0 control.** This used a scratch floors file outside the repo: the real file cut down to the one package, with suite min_tests=1.
- Search, mutated: go test 0, report `SKIPPED: …buildinfo.TestSearchSchemaVersionIsAbsent`, `FAILED (1 problem(s))`, EXIT=1.
- Search, restored: `ok — 6 test(s) executed across 1 package(s), 0 skips`, EXIT=0.
- Core, mutated: go test 0, report `SKIPPED: …config.TestValidProductionEnvironmentLoads`, `FAILED (1 problem(s))`, EXIT=1.
- Core, restored: `ok — 101 test(s) executed across 1 package(s), 0 unexpected skips`, EXIT=0.

**N1 result.** A skipped test fails the no-skip lane in both repos, even though `go test` exits 0. N1 PASS.

| case | search#6 | core#21 |
|---|---|---|
|S1 removed lane fails|PASS (v1 mut 1)|PASS (v1 mut 1)|
|S2 rename fails ci-required|PASS (v2 fan-in)|PASS (v2 fan-in)|
|N1 skip fails noskip lane|PASS (v3)|PASS (v3)|
|N2 continue-on-error/comment-out|PASS (v1 mut 4, 8)|PASS (v1 mut 4, 8)|
|R1 regression tests|PASS (v2)|PASS (v2)|
|only-success fan-in|PASS (v2)|PASS (v2)|
|SHA pins / base resolution|PASS (v1/v2 mut 6)|PASS (v2 mut 6)|
|breakage evidence|PASS (v2; green = guard step only)|PASS (v2)|

No blocking finding. Earlier follow-ups stand (pinned-steps coupling for search tombstones; fan-in deadline latency on a renamed lane). They are non-blocking.

PR VERDICT vizra-search#6: PASS — SHA 0e93164b562a05ad0e591d5d81de2dc7a761d888
PR VERDICT vizra-core#21: PASS — SHA 71a1ff3103e709b91ed93d4fe22e2b722d2d6862

FINAL VERDICT: PASS — SHA 0e93164b562a05ad0e591d5d81de2dc7a761d888 71a1ff3103e709b91ed93d4fe22e2b722d2d6862
