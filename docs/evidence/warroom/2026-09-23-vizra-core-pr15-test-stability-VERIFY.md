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

---

## Re-verification at 434abe5

- Target: head **`434abe5dd4332e7291820f0f8555b9d33e4d2bbc`** (fix round 1), one fast-forward commit on `96b8999` (`git merge-base --is-ancestor` ok).
- Head confirmed by `gh api repos/yegamble/vizra-core/pulls/15` at the start and at the end (2026-09-23T23:13:45Z): unchanged, PR open.
- Environment and isolation as before. I used a fresh clone in a new `mktemp -d $SCRATCH/vzv-core-pr15r1-XXXXXX`, with worktrees for `96b8999` (comparison) and for the mutations, and my own `--rm` containers at the CI digests. Everything is removed (`docker rm -f -v`, scratch deleted).
- The host was heavily shared: load average 35–164 during these runs.
- Inputs read: the fix-round diff `96b8999..434abe5` (21 files) and the sentinel report `docs/sentinel/pr/vizra-core-pr15-96b8999.md` (F-1…F-5, Q-1…Q-3).

### (a) T1–T4 re-run on 434abe5

I applied each mutation with the PR's own `mutations.py`, ran `go vet` on the mutant, ran the named test, restored with `git checkout`, and re-ran.

| Id | Mutant compiles | Red (mine) | `[build failed]` lines | Restored |
|---|---|---|---|---|
| T1 | yes | `tmpleak_test.go:35 a normal run of the fixtures tests left [vizra-fixtures-shared-…]`, exit 1 | 0 | sha back to `864996c8…`, 0 porcelain, green exit 0 |
| T2 | yes | `tmpleak_test.go:33 a normal run of the integration tests left [vizra-healthcheck-bin-2439684021]`, exit 1 | 0 | `0f3d0926…`, green exit 0 |
| T3 | yes | `testtmp_test.go:50 Sweep removed []; want exactly …`, exit 1 | 0 | `e899c169…`, green exit 0 |
| T4 | yes | **`testtmp_test.go:74 pid 1 (owned by root: EPERM, not ESRCH) is reported dead`**, exit 1 | 0 | `e899c169…`, green exit 0 |

- None of the four reds is a build failure.
- The committed `host-darwin-arm64/T1–T4.txt` contain 0 `build failed` lines, and T4.txt shows the `:74` failure.
- **FINDING 1 is closed.**

### (b) Timeout coverage

- `fixtures.yml:136` now reads `go test -race -count=1 -timeout 8m -v ./internal/fixtures/`.
  - The CI log of job 107412121052 on 434abe5 shows `Run go test -race -count=1 -timeout 8m -v ./internal/fixtures/`, `--- PASS: TestTheFixturesTestsLeaveNoTemporaryEntry (2.87s)` and `ok …/internal/fixtures 26.704s`.
- README.md:65 and `lanes.sh` are fixed. `lanes.sh` now reads the three bodies out of `pinned-steps.yml` itself.
- **Is that step really unpinned?**

  | Probe (mutation worktree, restored after each) | Result |
  |---|---|
  | P1: drop `-timeout 8m` from `fixtures.yml:136` | `ci-required-guard` rc 0: unpinned, as documented |
  | P2: drop it from build-test's unit direct step | guard FAIL (`… is not byte-equal to any entry in .github/pinned-steps.yml`): pinned, as documented |
  | P3: drop it from all four Makefile recipes and re-pin the digest | both anchors rc 0, guard rc 0: "a re-pinned Makefile without it passes every anchor" holds exactly |

  "Check 9" is the guard's real name for the direct-step check (`ci-required-guard.py:974`).
- **Testing the COMMANDS.md sentence against every `go test` invocation.** I grepped the Makefile, every workflow and `pinned-steps.yml`. Every invocation carries `-timeout 8m` except two, both inside `make ci`'s closure: `Makefile:81` (`config-template-check`) and `Makefile:86` (`openapi-verify`). See FINDING 5.

### (c) Non-unix build

Checked with `GOOS=<os> go vet` on each head:

| Head | GOOS | `./internal/fixtures/` | `-tags=integration ./internal/integration/` |
|---|---|---|---|
| 96b8999 | windows | rc 1 (`build constraints exclude all Go files in …/internal/testtmp`) | rc 1 |
| 434abe5 | windows | rc 0 | rc 0 |
| 434abe5 | linux | rc 0 | rc 0 |

- `testtmp_other.go` (`//go:build !unix`) is a pass-through `Run`.
- **No required linux test was dropped.** I compared the build-test event artifacts of 96b8999 (run 35924115437, merge tree `be6be9e`) and 434abe5 (run 35929397673, merge ref `fd53b93`, tree `8ede49d` = 434abe5's tree), per package and per test name:
  - unit 1566 → 1566;
  - integration 1737 → 1737;
  - shuffled 1737 → 1737;
  - 0 packages differ, and no test name was removed or added;
  - fixtures 43, integration 171, testtmp 2 in both;
  - 0 skips and 0 failures in all six streams.
- `TestTheEntryPointsBuild` moved to `entrypoints_test.go` (`integration`), and the leak test is `integration && unix`. Both still run on linux.

### (d) Floors

- The diff lowers nothing. The only three removed floor lines are `fixtures 36`, `fixtures 36` and `integration 144`, replaced by 37, 37 and 145.
- `go-test-report.py --emit-floors` on MY 434abe5 events gives:
  - fixtures 37 (measured 43);
  - integration 145 (measured 171);
  - testtmp 1 (measured 2);
  - scripts 419 (measured 493);
  - min_tests 1331 (unit) and 1476 (integration).
- That matches the `_why` text exactly. The scripts and min_tests rises are left undone, which the floors note states and the brief allows.
- Residual, known: at 15% slack no single test is pinned, so deleting one leak test (43 → 42 ≥ 37) stays green.

### (e) Doc sentences (R1)

I recomputed every CI number from the cited runs' job metadata and `ok` log lines (build-test plus both cache-matrix legs, all 12 runs `35857960260 … 35921428335`, 12 green build-test runs):

| Claim | Measured | Verdict |
|---|---|---|
| 12 runs: fixtures widest 146.1 s | 146.135 s (35921428335) | exact |
| 4 runs: fixtures 77.4–143.5 s, integration 54.9–99.5 s | 77.361–143.497, 54.900–99.478 | exact |
| 4 runs: build-test 7.8–10.8 min | 7.80–10.88 (35914283132) | truncated, not rounded; 10.9 when rounded (FINDING 6) |
| 4 runs: cache-matrix-leg 4.5–5.8 min | 4.58–5.83 | truncated (4.6–5.8 when rounded) |
| 12 runs: cache-matrix-leg widest 6.3 min | 6.38 (35921428335) | truncated (6.4 when rounded) |
| Makefile comment: 146 s and 201 s give 3.3x and 2.4x | 480/146.1 = 3.29, 480/201.2 = 2.39 | ok |
| Last step starts at about 8.7 (build-test) and about 3.7 (leg) | max 8.70 and 3.65 | ok |

The truncation is consistent, understates only the "before" figures, and changes no conclusion.

**"Limits" list** (COMMANDS.md) and the `testtmp` package doc:

| Claim | Check | Verdict |
|---|---|---|
| Enforced only on the pinned steps; review-only elsewhere | P1–P3 above | exactly true |
| An orphaned `go build` can outlive a real `-timeout` kill and race the next sweep | go's `-timeout` panics only the test binary. The builder measured this at `e80fb96` (18M entries, timings.txt). | accurate |
| PID namespace: one run can sweep the other's LIVE root | follows from `syscall.Kill(pid, 0)` being namespace-local | stated as a capability ("can"), not as a measurement, and declared unsupported; accurate |
| "A reused PID only ever keeps a root; it never removes one" | reused means alive, so it is skipped (`testtmp.go:92`) | true |
| Root caveat in the test comment | as root, `kill(1, 0)` returns nil, so T4 would survive | accurate |

- No claim goes beyond what was measured or follows from the code.
- The contention residual stands and I measured it again. At load ~138, `internal/integration` took **310.2 s** in my Valkey integration lane: 8m is 1.5× that, and still green. COMMANDS.md's "a host whose load average is several times its core count can still exceed it" is the right strength.

### (f) R14 (absolute paths)

- `git diff origin/main...HEAD | grep '^+'` over `/Users/`, `/var/folders/`, `/private/tmp`, `/home/<name>` and the user name matches only the `demo.sh` sed expression itself.
- `docs/evidence/test-stability/` contains no absolute path (F-5 is closed), and F3-before.txt uses `<clone>`.
- **Is `demo.sh`'s scrub sound?** The default macOS TMPDIR and `/private/tmp/...` paths are fully replaced by `$TMPDIR/`. A TMPDIR under a home directory would leak (see FINDING 7).

### (g) Pin and anchors

- `shasum -a 256 Makefile` gives `6b3d93c779420ed656e1070ff0ce832af130ab4e3a19b4b230cab615270f4eba`, which equals the pin.
- `make-integrity-guard.sh --workflow` rc 0; lenient rc 0; grammar 64/11/25/25/72.
- `ci-required-guard.sh` rc 0, with 0 FAIL lines.

### (h) Lanes on 434abe5

Every lane ran the exact pinned bodies, with its own TMPDIR and my own containers:

| Lane | Exit | Wall | Tests pass/fail/skip | Report | `vizra-*` left |
|---|---|---|---|---|---|
| `make ci` | 0 | 274 s (load 69→137) | – | – | 0 |
| unit (body 0) | 0 | 175 s | 1566/0/0 | ok, floor 1070 met | 0 |
| integration Valkey 9.1.2 (body 1) | 0 | 323 s | 1737/0/0 | ok, floor 1214 met | 0 |
| integration Redis 7.2 (body 1) | 0 | 264 s | 1737/0/0 | ok | 0 |
| shuffled Valkey (body 2) | 0 | 204 s | 1737/0/0 | ok | 0 |
| shuffled Redis 7.2 (body 2) | 0 | 170 s | 1737/0/0 | ok | 0 |

**CI on 434abe5** (`gh api …/commits/434abe5…/check-runs`): all success on head_sha 434abe5.

| Check | Job id |
|---|---|
| ci-required | 107412120893 |
| build-test | 107412121828 (6.4 min) |
| cache-matrix | – |
| cache-matrix-leg valkey | 107412122103 |
| cache-matrix-leg redis | 107412122307 |
| fixtures | 107412121052 |
| append-only | – |
| govulncheck | – |
| docker-build | – |
| GitGuardian | – |

- `image-scan` failed and is not required.
- The ci-required log ends `all 6 required check(s) succeeded`: append-only, build-test, cache-matrix, fixtures, govulncheck, docker-build, which equals `required-checks.txt`. Each one ran on this SHA.

### Earlier findings

| Finding | Status |
|---|---|
| 1 (T4 build failure) | **closed** |
| 2 (`fixtures.yml:136`) | **closed** |
| 3 (limits undocumented) | **closed**: all three are in COMMANDS.md and the package doc |
| 4 (numbers) | **closed** (fixture count, 143.5/146.1 s, `lanes.sh` bodies). The rounding residue is FINDING 6. |
| Sentinel F-1…F-5, Q-1, Q-3 | addressed as above; Q-2 is the contention residual, documented and re-measured |

### New findings (none blocking)

```
FINDING 5: COMMANDS.md's "Every `go test` lane … passes -timeout 8m" still has two exceptions inside `make ci`
Severity:    NIT
Confidence:  high
Affected:
  repo:      vizra-core
  files:     Makefile:81 (config-template-check), Makefile:86 (openapi-verify), docs/quality/COMMANDS.md:378-381
Observed:
  `grep -nE 'go test|GO\) test' Makefile .github/workflows/*.yml .github/pinned-steps.yml | grep -v -- -timeout`
  (comment and echo lines excluded) leaves exactly
  Makefile:81 `@$(GO) test -count=1 -run 'TestEveryKeyHasATemplateEntry|…' ./internal/config/` and
  Makefile:86 `@$(GO) test -count=1 -run 'TestEveryRouteHasASpecOperation|…' ./internal/httpapi/`.
  Both run in build-test's required `make ci` step. The sentence's dash-list does not name them, but its "Every" does.
Failure:
  Doc accuracy only. They keep go's 10m default, `make ci` starts ≤ 1.7 min into a 20-min job, and these run only
  a handful of fast tests, so a hang still dumps at about 12 min. Nothing is at risk.
Recommendation:
  Either add `-timeout 8m` to Makefile:81 and :86 (then re-pin `.github/pinned-makefiles.yml` and re-run both anchors),
  or reword COMMANDS.md:378 to "Every full-suite `go test` lane …" and name the two targeted contract checks as keeping go's default.
Acceptance criteria:
  The grep above returns nothing, or COMMANDS.md names both exceptions.
Cross-repo implications: none
Challenge: the sentence enumerates its lanes explicitly. "Every" still overclaims, and R1 asks for measured strength.
```

```
FINDING 6: Min-range figures are truncated, not rounded
Severity:    NIT
Confidence:  high
Affected:    docs/quality/COMMANDS.md test-stability table, docs/evidence/test-stability/timings.txt, Makefile comment
Observed:    build-test before 7.8–10.8 min (true max 10.88, run 35914283132); cache-matrix-leg 4.5–5.8 (true 4.58–5.83);
             "widest 6.3m" (true 6.38, run 35921428335).
Failure:     These understate the "before" figures by < 0.1 min. No conclusion changes.
Recommendation: write 10.9, 4.6 and 6.4, or say "truncated to 0.1 min".
```

```
FINDING 7: demo.sh's path scrub leaves an absolute path when TMPDIR lives under a home directory; the transcripts cite a tree that is not on the remote
Severity:    NIT
Confidence:  high
Affected:    docs/evidence/test-stability/demo.sh:28-29, docs/evidence/test-stability/host-darwin-arm64/T1–T4.txt, timings.txt (FIX ROUND 1 header)
Observed:
  - Feeding "/Users/alice/tmp/TestSweep/vizra" through the sed gives "/Users/alice$TMPDIR/vizra": the `/tmp/` rule matches mid-path and
    leaves the home prefix. The default macOS and /private/tmp TMPDIRs scrub correctly, and the committed files are clean.
  - T1–T4.txt record `tree: 8f96cd6ca968…`, which the builder says was squashed locally.
    `git fetch origin 8f96cd6…` → "not our ref", so the claimed provenance cannot be checked.
    I re-ran T1–T4 on 434abe5 myself (table (a)), so no claim rests on it.
Recommendation:
  Anchor the scrub to any absolute prefix ending in the TMPDIR value (e.g. sed on "$TMPDIR" itself), and record
  T1–T4 on a pushed commit, or note in the files that 8f96cd6 is unpublished.
```

### Verdict at 434abe5

- Every in-scope acceptance bullet reproduced:
  - valid T1–T4 reds, none a build failure;
  - R0 unchanged (the `testtmp` code diff is comment-only);
  - lanes green on both cache images, plain and shuffled, with 0 skips, floors met and 0 leaked entries;
  - guards, pin and anchors pass;
  - the non-unix build is fixed with no linux test dropped.
- CI is green on this SHA, and `ci-required`'s manifest matches the jobs that ran.
- All earlier findings are closed. FINDINGS 5–7 are NITs and non-blocking.

FINAL VERDICT: PASS — SHA 434abe5dd4332e7291820f0f8555b9d33e4d2bbc
