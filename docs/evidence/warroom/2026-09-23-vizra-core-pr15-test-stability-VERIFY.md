# VERIFY — vizra-core PR #15 `chore/m1-test-stability` (queue 2m + 2s, sentinel S-0016 / S-0001)

- Verifier: independent war-room verifier (fresh; did not write this code)
- Target: https://github.com/yegamble/vizra-core/pull/15, head **`96b8999e99d801aa38da84aef4792952f14ff9f0`**
- Head confirmed at start and at end (2026-09-23T22:17:20Z) via `gh pr view` and `git ls-remote`: unchanged, PR OPEN.
- Base: `a6bc77d` (main), merged in as `888a003`; `git diff 3994893 a6bc77d -- internal/fixtures internal/integration` is empty, so main's shape of those packages is the same at both.
- Plan: `docs/plans/2026-09-23-vizra-core-test-stability.md`
- Environment: darwin/arm64, 8 cores, go1.27.1 (go.mod `go 1.26.0`, `toolchain go1.27.1`), GNU Make 3.81, Docker 29.8.0, sqlc v1.31.1. The host was SHARED: load average 14–164 during the runs, recorded per lane.
- Isolation: fresh `git clone` in `mktemp -d $SCRATCH/vzv-core-pr15-XXXXXX`. Separate worktrees for base `a6bc77d` (R0) and for the mutations. `TMPDIR` pointed inside that directory for every run. I owned the containers (`--rm`, digests as CI pins them):
  - `postgres@sha256:86c951e0…` (18.6)
  - `valkey/valkey@sha256:c123e371…` (9.1.2)
  - `redis@sha256:06379549…` (7.2.16)

## 1. Lanes on 96b8999 (exact pinned bodies extracted from `.github/pinned-steps.yml`)

| Lane | Command | Exit | Wall | Tests (pass/fail/skip) | Slowest package | TMPDIR entries left |
|---|---|---|---|---|---|---|
| make ci | `make ci` | 0 | 122 s (load 70→40) | – | – | 0 |
| unit (pinned body 0) | `go test -race -count=1 -timeout 8m -json ./...` + report | 0 | 78 s | 1566/0/0, report ok, floor 1070 | fixtures 73.3 s | 0 |
| integration Valkey (body 1) | `… -timeout 8m -tags=integration …` + report | 0 | 176 s | 1737/0/0, floor 1214 | integration 167.7 s | 0 |
| integration Redis 7.2 (body 1) | same | 0 | 126 s | 1737/0/0 | integration 120.4 s | 0 |
| integration shuffled, Valkey (body 2) | `… -timeout 8m -shuffle=on -tags=integration …` | 0 | 140 s | 1737/0/0 | integration 135.3 s | 0 |
| recipe, Redis 7.2 | `make test-integration-shuffle` | 0 | 153 s | no FAIL lines | – | 0 |
| fixtures stress | `go test -race -count=3 -shuffle=on -timeout 30m -v ./internal/fixtures/` (seed 1790200558622680000) | 0 | 329 s | 129 PASS, 0 FAIL, 0 DATA RACE, 0 SKIP | – | 0 |

- `internal/testtmp` ran in both suites and passed (floor 1).
- `go vet -tags=integration` passed on fixtures, integration and testtmp.
- `go list -deps ./cmd/...` shows no production binary imports `internal/testtmp`.
- No `t.Skip` or `testing.Short` appears in any new test.

## 2. No test weakened (brief item 1)

- The only `.go` lines removed are:
  - the three `Generate(...)` calls inside drift-case mutations, each replaced by `copySharedCorpus`, which fatals on any error;
  - the old TestMain's `RemoveAll(sharedDir)`, now done by `testtmp.Run`'s root removal.
- No assertion, `wantKind` or case was changed or dropped. All 9 drift cases are still present.
- **The copy is equivalent to generating.** `Generate` (fixtures.go:287) writes exactly the `Corpus()` entries with mode 0644 under a 0755 directory, and returns them all in its map. `copySharedCorpus` writes those same names with the same modes.
- **The dotfile case is still a strong check.** It expects zero problems, so any hash or name difference in the copy would turn it red.
- **No mutation can leak between cases.**
  - Every `mutate` writes only under its own `copyRepoSlice(t)` root.
  - `copySharedCorpus` only reads `sharedDir`.
  - `VerifyAgainstManifest` regenerates only into its `scratch` argument (manifest.go:422).
  - count=3 with shuffle re-verifies the shared corpus (`TestEveryFixtureIsWhatItClaimsToBe`) after the drift cases of earlier iterations, and stayed green, race-clean.
- **Generation count 9 → 6** matches the code:
  - shared 1, determinism 1, committed-manifest 1;
  - the drift test's unmutated pre-check 1, plus the dotfile and edited-hash cases 2.

## 3. The 8m timeout (brief item 2)

**CI per-package worst**, from `ok` lines in the build-test and both cache-matrix-leg job logs:

| Run (head) | internal/fixtures | internal/integration |
|---|---|---|
| 35914283132 (66fcb2e, pre) | 109.8–**143.5 s** | 61.7–99.5 s |
| 35914133999 (25f62ac, pre) | 84.8–125.3 s | 54.9–87.5 s |
| 35910352499 (54a1376, pre) | 77.4–139.5 s | 61.2–93.6 s |
| 35899392555 (96d19b3, pre) | 103.7–133.8 s | 56.7–90.0 s |
| 35922912235 (888a003) | 56.5–98.2 s | 71.2–112.5 s |
| **35924115437 (96b8999)** | 45.7–94.5 s | 75.0–**107.4 s** |

- The worst package measured anywhere in CI is 143.5 s. That leaves 8m with a 3.3× margin; the worst on this head is 107.4 s (4.5×).
- In the build-test artifact for 96b8999 (merge ref e86988b, whose tree `be6be9e…` is identical to 96b8999's):
  - unit 1566/0/0;
  - integration 1737/0/0;
  - shuffled 1737/0/0;
  - all three exit files 0.

**Step offsets from job start, and the goroutine dump.** Steps 12, 18 and 19 carry no `if:`, so after a failed step the later ones are skipped: at most one hang runs per job.

| Job | Last test step starts at (11 runs) | Step duration | Limit | Hang in last step dumps at about |
|---|---|---|---|---|
| build-test | 5.9–**8.7** min | ≤ 2.1 min | 20 min | 8.7 + ~1 (compile) + 8 ≈ 17.7 min |
| cache-matrix-leg | 2.8–**3.6** min | – | 15 min | ≈ 12.6 min |

- Both hang cases print the dump before the job limit, with margin.
- The required `fixtures` job's own go test (`fixtures.yml:136`) keeps go's 10m default. Its step starts at +0.2 min in a 15-min job, so its dump still prints at about 10.5 min. See FINDING 2.
- **Probe.** A deliberately hanging test under `-race -timeout 5s -json` printed `panic: test timed out after 5s` with the goroutine dump naming the test. `go-test-report.py` then reported FAILED.
- **Is 8m tighter than a measured worst case in any required lane?** No. It is tighter only on an overloaded local host:
  - pre-change, S-0016 recorded >600 s under contention;
  - post-change, the builder measured 201 s at load ~44, and I measured 167.7 s at load ~25–47.
- **Wall-time claim:** build-test on 96b8999 took 7.2 min, and 7.4 min on 888a003.

## 4. Pin and guards (brief item 3)

- **Makefile digest.** `shasum -a 256 Makefile` gives `7c2a2ea72fa5867d442d5e1b8bdf8763a567d113fd5766e13d5b74884782ba78`, which equals `.github/pinned-makefiles.yml`.
- **Guard and anchors.**
  - `./scripts/ci-required-guard.sh` exit 0.
  - `make-integrity-guard.sh --workflow` exit 0.
  - `make-integrity-guard.sh` (lenient) exit 0.
  - Grammar: 64 blank/comment, 11 assignment, 25 phony, 25 rule, 72 recipe, which matches COMMANDS.md.
  - CI's anchor steps (GNU Make on ubuntu) were green on 96b8999.
- **Fixture edits.** A script applied the three exact old→new pinned-body substring replacements to every base fixture and compared the result with HEAD (`../fixcheck.py`):
  - 151 guard files, **75 changed** (not 74);
  - every change is exactly that replacement: 73 files with 2 occurrences and 2 with 1;
  - **0 mismatches**, and 0 un-replaced old bodies left anywhere.
- **Verdicts unchanged.** I ran the guard over all 75 fixture dirs at base `a6bc77d` and at HEAD:
  - exit codes are identical for every fixture (74 fail, 1 pass);
  - the first three FAIL lines are identical, except that the echoed `got:` text now contains `-timeout 8m` in `direct-lane-without-exit-rc` and `direct-lane-without-report`.

## 5. internal/testtmp (brief item 4)

### Reproduced demonstrations

| Id | What | Result (mine) |
|---|---|---|
| R0 | leak tests overlaid on main `a6bc77d` (identical to 3994893 for these packages) | **red**: fixtures `tmpleak_test.go:51 the next run of this package did not remove what a killed run left: [vizra-fixtures-shared-2926196678]`; integration `tmpleak_test.go:51 a normal run … left [vizra-healthcheck-bin-1761864157]` |
| T1 | fixtures TestMain without testtmp | red (`tmpleak_test.go:35 … left [vizra-fixtures-shared-…]`, exit 1) → restored byte-identical → green (exit 0) |
| T2 | integration TestMain without testtmp | red (`tmpleak_test.go:51 … left [vizra-healthcheck-bin-1465891413]`, exit 1) → green (exit 0) |
| T3 | Sweep never removes | red (`testtmp_test.go:50 Sweep removed []`, exit 1) → green |
| **T4 as committed** | `alive()` treats EPERM as dead | **red for the WRONG reason**: `FAIL internal/testtmp [build failed]` — `vet: internal/testtmp/testtmp.go:30:2: "errors" imported and not used`. The builder's own `host-darwin-arm64/T4.txt` shows the same `[build failed]`. See FINDING 1. |
| T4′ (mine, compiling) | `_ = errors.Is; return err == nil` | red for the stated reason: `testtmp_test.go:70 pid 1 (owned by root: EPERM, not ESRCH) is reported dead` → restored → green |
| M5 (mine) | T3's mutation against the fixtures kill+sweep test | red: `tmpleak_test.go:51 the next run of this package did not remove what a killed run left: [vizra-test-fixtures-16001-…]` → green |

### Can Sweep delete something it must not?

A scratch probe test (since removed) checked these cases. Sweep removed only the dead real root, and the `+pid` spelling:

| Probe | Result |
|---|---|
| Symlink named `vizra-test-fixtures-<deadpid>-sym` pointing at a real directory | kept (`DirEntry.IsDir()` is false for a symlink) |
| Regular file with that name | kept |
| Dead root containing a symlink to an outside directory | root removed, outside target kept (RemoveAll does not follow) |
| PID 1 (live, EPERM) | kept |
| No suffix after the PID | kept |
| PID 0 | kept |
| 20-digit PID | kept |
| Sibling name `fixtures-extra-<pid>` | kept |
| `+<deadpid>` | removed. `strconv.Atoi` accepts a leading `+`, but only a `vizra-test-fixtures-` directory of a dead PID can match; harmless |

Other cases, by analysis:
- **PID reuse:** the root is kept, a conservative leak and never a deletion.
- **Other user:** EPERM counts as alive and the directory is skipped. A dead-PID root of another user is 0700 under sticky `/tmp`, so RemoveAll fails.
- **Residual:** liveness is local to the PID namespace. If two runs in different PID namespaces share one TMPDIR (a container bind-mounting the host tmp), one can sweep the other's live root. See FINDING 3.

## 6. Docs and residuals (brief item 5)

- **Documented in COMMANDS.md:** the measured table, and "a host whose load average is several times its core count can still exceed it".
- **Documented only in the PR body, not in any repo doc:**
  - the `-timeout` in the Makefile recipes is review-only;
  - an orphaned `go build` after a real `-timeout` kill can race the next sweep. `child.go:79-84` covers only the test helper's process-group kill.
  - See FINDING 3.
- **Overstated:** COMMANDS.md says "Every `go test` lane … passes `-timeout 8m`". See FINDING 2.

## 7. CI on 96b8999 (brief item 6, own `gh api`)

| Check | Result | Job id |
|---|---|---|
| ci-required | success | 107394946466 |
| build-test | success (7.2 min) | 107394947156 |
| cache-matrix | success | – |
| cache-matrix-leg valkey | success | 107394947301 |
| cache-matrix-leg redis | success | 107394947266 |
| fixtures | success | 107394946939 |
| append-only | success | – |
| govulncheck | success | – |
| docker-build | success | – |
| GitGuardian | success | – |
| image-scan | failure | – |

- image-scan is not in `.github/required-checks.txt`. The builder states it fails as it does on main; I did not re-check that.
- **Manifest against executed jobs.** The ci-required log ends `all 6 required check(s) succeeded`. It lists append-only, build-test, cache-matrix, fixtures, govulncheck and docker-build, exactly the six in `required-checks.txt`. Each of those ran on this SHA with real step timings and non-empty test logs, so no lane is listed without running.

## Findings

```
FINDING 1: The committed T4 demonstration is red by compile error, not by the test
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     docs/evidence/test-stability/mutations.py (T4), docs/evidence/test-stability/host-darwin-arm64/T4.txt,
             docs/quality/COMMANDS.md:421, internal/testtmp/testtmp.go:30,105-107
  requirements: queue 2m/2s (S-0016/S-0001) — the "EPERM counts as alive" guarantee

Observed:
  mutations.py T4 replaces `return err == nil || !errors.Is(err, syscall.ESRCH)` with `return err == nil`.
  `errors` is then unused, so the package does not compile. Reproduced: `go vet ./internal/testtmp/` →
  `testtmp.go:30:2: "errors" imported and not used`; `go test` → `FAIL internal/testtmp [build failed]`.
  The builder's own T4.txt records exactly `FAIL ... [build failed]` as the demonstration's red.

Failure:
  The committed evidence, the PR body ("T1–T4 … Each is red") and COMMANDS.md present a build failure as proof
  that TestAliveTellsALiveProcessFromADeadOne catches EPERM-treated-as-dead. Any mutation that breaks the build
  would be "red", so the transcript proves nothing about the test. (The test IS sound: my compiling variant
  T4′ `_ = errors.Is` + `return err == nil` goes red at testtmp_test.go:70 for the stated reason.)

Perspective:
  developer

Recommendation:
  Change T4's replacement to "\t_ = errors.Is\n\treturn err == nil\n" (or any compiling variant), re-run
  demo.sh for T4 and commit the new T4.txt, which must show the testtmp_test.go:70 failure line.

Acceptance criteria:
  host-darwin-arm64/T4.txt shows the mutated run failing at testtmp_test.go:70 "pid 1 … is reported dead",
  no "[build failed]" anywhere in T1–T4, then green after a byte-identical restore.

Tests:
  cd <clone>; python3 docs/evidence/test-stability/mutations.py T4; go vet ./internal/testtmp/   # red: unused import
  git checkout -- internal/testtmp/testtmp.go

Cross-repo implications:
  core: evidence only | user: none | search: none | meta: none

Challenge:
  The underlying test is correct and I reproduced its red with a one-token fix, so the code is fine. But the
  red/green demonstration is the evidence this slice commits, and a compile-error red is the textbook false
  positive the verifier exists to reject.
```

```
FINDING 2: A required go test lane on internal/fixtures has no -timeout, while COMMANDS.md says every lane does
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .github/workflows/fixtures.yml:136, docs/quality/COMMANDS.md (Test stability section, "Every `go test` lane — …")
  requirements: queue 2m (S-0016)

Observed:
  fixtures.yml:136 `run: go test -race -count=1 -v ./internal/fixtures/` has no `-timeout`, in the REQUIRED
  `fixtures` job (15-min limit). This is the very package S-0016 is about. COMMANDS.md opens its test-stability section with
  "Every `go test` lane — the Makefile's … and the three pinned direct steps — passes -timeout 8m".

Failure:
  The claim is broader than the change. That lane still runs under go's 10m default. At a step offset of
  +0.2 min in a 15-min job, the goroutine dump still prints (~10.5 min), so this is not a hang-safety hole.
  It is an inconsistency, and a reader of the doc would believe it is bounded at 8m.

Perspective:
  developer

Recommendation:
  Either add `-timeout 8m` to fixtures.yml:136 (not a pinned direct step, so no fixture lockstep), or change the
  COMMANDS.md sentence to name this lane as keeping the 10m default.

Acceptance criteria:
  Either `grep -n 'go test' .github/workflows/*.yml Makefile` shows -timeout on every invocation, or the doc
  names the exception.

Tests:
  grep -n "go test" .github/workflows/fixtures.yml

Cross-repo implications:
  none

Challenge:
  "Every go test lane" is qualified by the dash list, which does not include fixtures.yml. But the sentence
  still reads as universal.
```

```
FINDING 3: Two residuals live only in the PR body; a third is undocumented
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     docs/quality/COMMANDS.md (Test stability section), internal/testtmp/testtmp.go:25-26,103-107, internal/testtmp/child.go:79-84

Observed:
  The PR body's "Not run / residual" section names two limits that no repo doc records:
    (a) no guard requires `-timeout` in the Makefile recipes; they are review-only;
    (b) a real go `-timeout` kill while binaries() runs `go build` leaves that build orphaned, and it can
        rewrite a root the next run has just swept.
  child.go's comment covers only the test helper's process-group kill. Also undocumented:
    (c) testtmp's liveness check `syscall.Kill(pid, 0)` is local to the PID namespace. Two runs that share a
        TMPDIR across namespaces (a container bind-mounting the host tmp) can sweep each other's LIVE root.

Failure:
  After merge, the PR body is not where the next developer looks. The docs present the leak fix as complete.

Perspective:
  developer

Recommendation:
  Add three sentences to the COMMANDS.md test-stability section (or the testtmp package doc) stating (a), (b) and (c).

Acceptance criteria:
  COMMANDS.md or testtmp.go's package doc names all three limits.

Tests:
  none (documentation)

Cross-repo implications:
  none

Challenge:
  (c) needs an unusual setup. It is still a way the sweep can delete a live run's files, which is the one thing
  the package promises never to do.
```

```
FINDING 4: Evidence numbers slightly off
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     docs/evidence/test-stability/timings.txt, docs/evidence/test-stability/lanes.sh, PR body, plan

Observed:
  - The fixture count is 75, not 74 (`git diff --name-only origin/main...HEAD | grep -c testdata/guard` → 75).
  - The CI pre-change worst is internal/fixtures 143.5 s (run 35914283132), not 139.5 s.
  - "build-test before 8.3–10.9 min": run 35910352499, one of the four runs timings.txt itself cites, took 7.8 min.
    The cache-matrix-leg range "4.6–5.6" misses a 5.8 min leg in run 35914283132.
  - lanes.sh's unit_body and int_body omit `-timeout 8m`, so the "final head d817f33 (with -timeout 8m)" and
    888a003 local lane rows did not run the pinned bodies. This does not change the wall times.

Failure:
  Small misstatements in the committed evidence. None changes the sizing conclusion (8m is 3.3× the true CI worst).

Recommendation:
  Correct the numbers when re-recording T4.
```

## Verdict

- CI is green on 96b8999, and `ci-required`'s manifest matches the jobs that actually ran.
- All lanes reproduced: 1566/0/0 unit and 1737/0/0 integration, on both cache flavours and shuffled, leaving 0 `vizra-*` entries.
- The guards, pin and 75 fixture edits are exact, and every verdict is unchanged.
- R0, T1, T2 and T3 reproduced. The drift cases and their assertions are unchanged, and the shuffled race stress run is clean.
- **But the committed T4 demonstration is red only because the mutant does not compile (FINDING 1, REQUIRED).** A demonstration that goes red for a reason other than the one stated fails its bullet.
- The fix is a one-line change to `mutations.py` plus a re-recorded T4.txt. FINDINGS 2–4 are non-blocking but cheap to fold into that round.

FINAL VERDICT: FAIL — SHA 96b8999e99d801aa38da84aef4792952f14ff9f0
