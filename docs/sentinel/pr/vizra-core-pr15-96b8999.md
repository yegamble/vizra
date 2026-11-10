# Sentinel PR review: yegamble/vizra-core #15 at `96b8999`

- PR: "test: bounded, measured test timeouts and no temp leaks (S-0016, S-0001)"
- Head `96b8999e99d801aa38da84aef4792952f14ff9f0`, base `main` `a6bc77dda973c42ac79360b0b5afd03e7aa59604`. I confirmed the head SHA at the start and again at the end, and it had not moved.
- Reviewer: the PR sentinel. It ran alongside the independent verifier and does not replace it. The brief said `post: no`, so nothing was posted.
- Environment: darwin/arm64, go1.27.1 and GNU Make 3.81. The host's load average was 6 to 91 during the runs, because other agents were working on it.
  - Containers: `sent15pr-pg` (postgres at the CI digest `86c951e0…`) and `sent15pr-vk` (valkey at the CI digest `c123e371…`). Both were started with `--rm` and removed with `-v` at the end.
  - Clones: fresh, in a `mktemp -d` scratch directory. `core` is the PR head, `base` is a worktree of `a6bc77d` and `mut` is a mutation worktree of the head. `vizra`, `vizra-user` and `vizra-search` are clones of main at `e4f625e`, `783483f` and `4810048`.
  - Every run had its own empty `TMPDIR`, and all four were still empty afterwards.

## Counts

| | n |
|---|---|
| Findings | 5 (all NIT) |
| Blocking findings | 0 |
| Questions | 3 |
| Blast-radius dependents examined | 22 |
| Not run | 3 |

**Verdict: nothing here blocks the merge.** No dependent of the change breaks, the lanes pass on the head, and runs leave nothing behind.
- Unit suite: 1566 executed, 0 fail, 0 skip, floor met.
- Integration suite (Valkey): 1737 executed, 0 fail, 0 skip, floor met.
- `make fixtures-verify` reproduces the manifest.
- `ci-guard` passes.

The findings are documentation drift, a non-unix build break, and the known limits of floors and evidence paths.

## Blast radius

| Changed thing | Dependents found | Result |
|---|---|---|
| Makefile `test`, `test-race`, `test-integration` and `test-integration-shuffle` gain `-timeout 8m` (`Makefile:162,167,175,190`) | `make ci` (via `test-race`); the cache-matrix legs (`build-test.yml:451,463`); README `make test-integration` (`README.md:54`); AGENTS "The gate"; `pinned-makefiles.yml` digest | Consistent. The digest was re-pinned, the anchor's grammar line prints `64 blank/comment …`, and COMMANDS.md:91-93 matches it. No other repo holds the old digest `ad681247…`: I searched all four. |
| The three pinned direct steps (`pinned-steps.yml:116,130,140`) and their copies in `build-test.yml:240,300,317` | `ci-required-guard.py` byte-equality; the guard fixtures under `scripts/testdata/guard/*/workflows/floor.yml` (all 74 updated); COMMANDS.md:199,207; **README.md:65**; `go-test-report.py:39` docstring | The guard and `go test ./scripts/` pass (493 tests). README.md:65 still shows the old body (**F-2**). The docstring is generic usage and is fine. |
| Timeout policy in the COMMANDS.md prose ("Every `go test` lane") | `.github/workflows/fixtures.yml:136`, which runs `go test -race -count=1 -v ./internal/fixtures/`. It is a required check. | It has no `-timeout` (**F-1**). |
| The CI timing claim (a hang still prints its goroutine dump before the job is killed) | build-test (`timeout-minutes: 20`) and cache-matrix-leg (15), measured on this PR's CI run | Holds. In build-test the last test step starts at 6.0 min, so 6 + 8 is 14, under 20. In cache-matrix-leg the second step starts at 3.0 min, so 3 + 8 is 11, under 15. |
| `internal/testtmp` (new, `//go:build unix`) | importers: `internal/fixtures/fixtures_test.go:15` (untagged) and `internal/integration/main_test.go:9` (`//go:build integration` only) | On a non-unix GOOS the test packages no longer compile (**F-3**). `lint-imports` passes. |
| `TMPDIR` redirected per test binary (`testtmp.go:53`) | subprocesses started under it: `go build` of the entry points (`healthcheck_test.go:72`); `go test -c` (`child.go:36`); the `vizra`, `vizra-api` and `vizra-worker` binaries (`healthcheck_test.go:195,263,519`, `claimtoken_cli_test.go:38,197`) | OK. No production code calls `TempDir`, `CreateTemp` or `MkdirTemp` (searched `cmd/` and `internal/`), so the spawned binaries write nothing there. Go's `WORK` directory lands inside the root and is removed with it. `GOCACHE` is not under `TMPDIR`. **No test shells out to docker or exiftool**: the only `docker` exec is `cmd/vizra/doctor.go:279`, and the tests stub it with a fake `DOCKER=`. No Unix sockets are created, so the longer macOS path is harmless. |
| Other `TestMain`s, and tests that assume the default `TMPDIR` | `func TestMain` appears only in `fixtures` and `integration`. There are no hard-coded `/tmp` or `/var/folders` paths in Go, shell or Python outside the evidence. `cmd/fixturegen/main.go:76` has its own `MkdirTemp` with a deferred `RemoveAll`. | No dependent. A full unit and integration run left 0 entries in its `TMPDIR`. |
| `internal/fixtures` output shared between tests (the `sharedCorpus` copy and the parallel tests) | `mutation_test.go:189` (reads the shared dir; mutates in memory only); the drift cases (they write only into their own `copyRepoSlice` and `t.TempDir`); `VerifyAgainstManifest` (writes only to scratch) | No writer to the shared corpus. The drift cases still fail when mutated: `replaceOnce` needs the file to exist. |
| `fixtures-verify` / manifest reproduction | `make fixtures-verify`; the fixtures lane; `TestGeneratorSourceListCoversThePackage` | `fixtures-verify: ok — 12 fixtures, 1791508 bytes, generator 1 (4ff582ba6959), toolchain go1.27.1`. The new files are all `_test.go` or live outside the generator's source list. |
| `scripts/test-floors.json` (testtmp 1, and the notes) | `go-test-report.py`; the new leak tests | Nothing was lowered. The new tests are not protected by any floor (**F-4**). |
| Evidence files under `docs/evidence/test-stability/` | R14 (public repo) | One absolute local path (**F-5**). |
| Mutation harnesses that patch the changed files (R23) | `docs/evidence/{fixtures,hardening-b1,hardening-b5,m1a-owner-claim}/*` | None of them uses a needle in text this PR changed. The Makefile recipes and the fixtures TestMain/`Generate` lines appear in no harness. No dead mutation. |
| Search, user and meta copies of core's commands | vizra-search keeps its own `pinned-steps.yml` and Makefile (`go test -race -count=1 $(PKG)`); vizra-user pins e2e steps only; meta has only historical evidence and plans quoting old commands | None of them copies core's bodies. Nothing breaks. |

## Findings

### F-1: NIT (R1). COMMANDS.md says every `go test` lane passes `-timeout 8m`, but the required `fixtures` lane does not

- Changed side: `docs/quality/COMMANDS.md:378-380`: "Every `go test` lane — the Makefile's `test`, `test-race`, `test-integration`, `test-integration-shuffle` and the three pinned direct steps — passes `-timeout 8m`." Also `Makefile:152`: "-timeout 8m on every go test here and in the pinned direct steps".
- Dependent side: `.github/workflows/fixtures.yml:136`, `run: go test -race -count=1 -v ./internal/fixtures/`. `fixtures` is a required check (`required-checks.txt`), it runs `go test`, and it keeps go's 10-minute default inside a 15-minute job.
  - It runs exactly the package S-0016 is about.
  - This PR adds `TestTheFixturesTestsLeaveNoTemporaryEntry` to it.
- Reproducer:

```
$ grep -rn 'go test' .github/workflows/*.yml | grep -v -- '-timeout'
.github/workflows/fixtures.yml:136:        run: go test -race -count=1 -v ./internal/fixtures/
```

  On base the same line exists, so the drift is only in the new sentence. CI timing is harmless today: the step took 49 s on this PR's run.
- Smallest fix: either say "every go test lane in build-test" in COMMANDS.md:378, or add `-timeout 8m` to `fixtures.yml:136`. That step is not a pinned step, so no fixture churn follows.

### F-2: NIT (R1). The README's "Reproducing what CI asserts" command no longer matches the pinned step

- Changed side: `.github/pinned-steps.yml:116`, `go test -race -count=1 -timeout 8m -json ./...`.
- Dependent side: `README.md:59-65`, "To reproduce that locally:" followed by `go test -race -count=1 -json ./... > unit-events.json; echo $? > unit-exit.txt`.
- Reproducer:

```
$ diff <(sed -n 65p README.md) <(sed -n 199p docs/quality/COMMANDS.md)
< go test -race -count=1 -json ./... > unit-events.json; echo $? > unit-exit.txt
> rc=0; go test -race -count=1 -timeout 8m -json ./... > unit-events.json || rc=$?
```

  A package taking 8 to 10 minutes fails in CI and passes with the README's command.
- Smallest fix: add `-timeout 8m` to README.md:65 (COMMANDS.md already has it).

### F-3: NIT. The fixtures and integration test packages no longer compile on a non-unix GOOS

- Changed side: `internal/testtmp/testtmp.go:1` and `child.go:1`, both `//go:build unix`, with no fallback file.
- Dependent side:
  - `internal/fixtures/fixtures_test.go:15,50` imports and calls `testtmp.Run` with no build tag.
  - `internal/integration/main_test.go:1,9` is tagged `integration` only.
- The PR does tag `tmpleak_test.go` `unix` on purpose, so the intent was to exclude non-unix systems gracefully. Instead, the whole package fails to build there.
- Reproducer:

```
head$ GOOS=windows go vet ./internal/fixtures/
package github.com/yegamble/vizra-core/internal/fixtures (test)
	imports github.com/yegamble/vizra-core/internal/testtmp: build constraints exclude all Go files in …/internal/testtmp
vet-rc=1
head$ GOOS=windows go vet -tags=integration ./internal/integration/   -> rc=1
head$ GOOS=windows go test -count=1 -run XXX ./internal/fixtures/     -> FAIL … [setup failed]
base$ GOOS=windows go vet ./internal/fixtures/                         -> rc=0
base$ GOOS=windows go vet -tags=integration ./internal/integration/    -> rc=0
```

- Severity is NIT because no document names Windows as a supported development platform and no CI lane cross-vets.
- Smallest fix: add `internal/testtmp/testtmp_other.go` with `//go:build !unix` and `func Run(m *testing.M, _ string) int { return m.Run() }`.

### F-4: NIT (R11). The S-0001 and S-0016 regression tests can be deleted with every floor still green

- Changed side:
  - `scripts/test-floors.json:88-91,113,138`: testtmp gets floor 1 for 2 tests, and the notes say "their floors are unchanged" for `fixtures` (36) and `integration` (144).
  - The formula (`go-test-report.py:211`) run on the head's events now gives **37** and **145**. The committed floors are one under the generator's output. The same file's earlier note says "Every other per-package floor already equals the generator's output", and that is no longer true.
- Dependent side: `internal/fixtures/tmpleak_test.go`, `internal/integration/tmpleak_test.go` and `internal/testtmp/testtmp_test.go`. These are the only tests that pin the leak fixes.
- Reproducer: my head runs, with the events of `TestTheFixturesTestsLeaveNoTemporaryEntry`, `TestTheIntegrationTestsLeaveNoTemporaryEntry`, `TestTheEntryPointsBuild` and `TestAliveTellsALiveProcessFromADeadOne` removed. That is exactly what deleting them would emit.

```
integration: fixtures 42 (floor 36), integration 169 (floor 144), testtmp 1 (floor 1)
go-test-report: ok — 1733 test(s) executed across 19 package(s), 0 unexpected skips, floor 1214 met   rc=0
unit:        fixtures 42 (floor 36), testtmp 1 (floor 1)
go-test-report: ok — 1564 test(s) executed across 18 package(s), 0 unexpected skips, floor 1070 met
--emit-floors on the full head events: fixtures 37 (measured 43), integration 145 (measured 171), testtmp 1 (measured 2)
```

- This is the known limit of slack floors: at 15% slack, no single test is protected. It is recorded because R11 names it.
- Smallest fix: raise the two floors to the formula's 37 and 145. The durable fix is a named `required_tests` list in the floors file for the tests that pin sentinel findings, which is a chair or owner decision.

### F-5: NIT (R14). The new evidence commits an absolute local temp path

- Changed side: `docs/evidence/test-stability/host-darwin-arm64/T3.txt:15`, `…want exactly /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/TestSweepRemoves…`.
- Dependent side: the repository is public (R14).
- Reproducer: `grep -rnE '/var/folders/|/Users/' docs/evidence/test-stability/` finds 1 hit.
- The class already exists on main: 8 files carry the same per-user `/var/folders` hash. So this adds one more instance and opens nothing new.
- Smallest fix: replace the prefix with `$TMPDIR/` in T3.txt, and fold the 8 existing files into the same scrub later.

## Questions (not reproduced)

- **Q-1: can the PID-only liveness check misfire?** `testtmp.go:92,105-108` decides liveness from the PID alone.
  - PID reuse means a killed run's root is never swept when its PID now belongs to a live process. That is a leak, not data loss, and no worse than base.
  - Across PID namespaces the opposite could happen. If `TMPDIR` is bind-mounted into a container that also runs the suite, the host's `Sweep` sees the container's PID as ESRCH and could remove a live run's root.
  - Neither case was reproduced, and no documented workflow shares `TMPDIR` with a container.
- **Q-2: does 8m remain enough under the load that produced S-0016?** The S-0016 sweep measured `internal/integration` at 489 s and 422 s at load 91 to 161, and 489 s is over the new 480 s budget.
  - My head runs at load 60 to 91 were well under it: integration 231.8 s, fixtures 175.5 s (integration suite) and fixtures 136.2 s (unit suite).
  - COMMANDS.md documents a contention escape hatch, so this is recorded only as the direction of the strictness change (10m to 8m). It is not a break.
- **Q-3: does `TestAliveTellsALiveProcessFromADeadOne` still catch mutation T4 when the tests run as root?** Its `alive(1)` row relies on EPERM. As root, `kill(1, 0)` succeeds, so T4 ("EPERM means dead") would survive, for example in a container job.
  - Not run, because the GitHub runners are not root.
  - A pid owned by another non-root user would be a sturdier probe.

## Execution transcript (head `96b8999`)

```
anchor (make-integrity-guard.sh --workflow)                         rc=0  grammar: 64 blank/comment, 11 assignment, 25 phony, 25 rule, 72 recipe
make ci-guard                                                       rc=0
make fixtures-verify                                                rc=0  12 fixtures, 1791508 bytes, generator 1 (4ff582ba6959), toolchain go1.27.1
go test -race -count=1 -timeout 8m ./internal/testtmp ./internal/fixtures   ok 1.3s / ok 101.1s; TMPDIR left empty
go test -race -count=1 -timeout 8m -json ./...  (unit)              rc=0; report: 1566 executed, 0 unexpected skips, floor 1070 met; slowest fixtures 136.2s; TMPDIR left empty
go test -race -count=1 -timeout 8m -tags=integration -json ./...  (PG 18.6 + Valkey 9.1.2)
                                                                    rc=0 (4:04 wall); report: 1737 executed, 0 unexpected skips, floor 1214 met;
                                                                    slowest integration 231.8s, fixtures 175.5s; TMPDIR left empty
extra mutation (not in the builder's T1–T4): testtmp.Run does not set TMPDIR
  go test -count=1 -run '^TestTheFixturesTestsLeaveNoTemporaryEntry$' ./internal/fixtures/
  --- FAIL: tmpleak_test.go:35: a normal run of the fixtures tests left [vizra-fixtures-shared-3361598053] in its TMPDIR   rc=1  (restored; worktree clean)
PR CI at 96b8999: every required check green; build-test 7m14s; image-scan fails, as on main a6bc77d/3994893/96d19b3 (not a required check)
```

## Rules applied

| Rule | Applies | Result |
|---|---|---|
| R1 no false guarantees | yes | F-1, F-2. The CI timing claim was measured and holds. |
| R2 do not identify a CI step by substring | yes | The pinned direct steps are still byte-equal, the guard passes, and all 74 guard fixtures moved in step. |
| R3 allowlist an attacker-editable language | yes | The Makefile still fits the grammar, and the pin was updated. |
| R5 fail closed on the unreadable | yes | `KillChildWhen` fails when the marker never appears. The leak tests fail when the child run fails. OK. |
| R11 tests must be able to fail | yes | The leak tests go red under an independent mutation. The floors do not protect them (F-4). No `-run` selects zero tests: the children's `-test.run` patterns are anchored and checked for `PASS`. |
| R12 tests clean up after themselves | yes (the subject of the PR) | Normal runs leave 0 entries across the whole unit and integration suites. A killed root is swept by the next run of the same package. See Q-1. |
| R14 public-repo exposure | yes | F-5 |
| R15 supply chain and pins | yes | Only the Makefile digest changed, and it was re-pinned. No actions or images changed. |
| R23 retarget mutations after rewrites | yes | No harness needle touches the changed text. The builder's T1 to T4 needles match the head. |
| R4, R6-R10, R13, R16-R22 | no | There is no parser, uploader, config, cache, TTL, health, SQL, validator, error-wrap, probe, template or migration change. |

## Not run

- Q-3's root-user case: I did not run the suite as root in a container.
- The Redis 7.2 cache-matrix leg: I did not run it locally. The PR's CI legs for both flavours are green.
- The builder's T1 to T4 and the base-side red (`R0-red-on-main.txt`): I did not re-run them. That is the verifier's reproduction, and I ran one independent mutation instead.
