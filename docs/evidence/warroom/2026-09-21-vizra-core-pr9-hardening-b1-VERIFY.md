# Independent verification — vizra-core PR #9, hardening sweep B1

- **Repo / PR:** `yegamble/vizra-core` — https://github.com/yegamble/vizra-core/pull/9
- **Title:** chore(ci): hardening sweep B1 — the CI gates cannot be silenced from a workflow line, and cannot pass vacuously
- **Head SHA verified:** `e710c3cff18bd63c87a692937b608fa762627d99`
- **Base:** `main@5eb2829`; commits `6b25fc5`, `e710c3c`; 119 files, +4473 −217
- **Verifier:** independent — did not write this code, did not touch the builder's checkout
  (`/Users/yosefgamble/github/vizra/vizra-core`) or the `core-m1-owner-claim` worktree.
- **Date:** 2026-09-21

Branch head re-read at the start of the run:

```
$ git ls-remote origin refs/heads/chore/m0-hardening-b1
e710c3cff18bd63c87a692937b608fa762627d99	refs/heads/chore/m0-hardening-b1
```

The branch has not moved. This report verifies exactly that SHA.

## Environment

| | |
|---|---|
| host | darwin/arm64 (Darwin 25.5.0), Apple silicon |
| clone | fresh `git clone` into a private `mktemp -d` under the session scratchpad; deleted at the end |
| go | go1.27.1 darwin/arm64 |
| python3 | 3.9.6, PyYAML 6.0.3 |
| make (host) | **GNU Make 3.81** |
| make (CI reference) | **GNU Make 4.3**, exercised in a throwaway `ubuntu:24.04` container named `vzv9pr9-make43` (removed) |
| docker | 29.8.0 |
| containers | `docker ps` inspected first: `vizra-m1a-*` and `vzv8-*` belong to other agents; none touched. My own services use the unique prefix `vzv9pr9-` and ports 55913/63913. |

**This host is not the ADR-009 acceptance platform.** Where a result depends on the
runner, the CI log for this SHA is the authority and is read below.

---

## 1. Frozen paths (brief item g)

```
$ git diff --stat 5eb2829..e710c3c -- migrations/ api/ internal/ cmd/ sqlcgen/
(empty)
$ git diff 5eb2829..e710c3c -- .github/required-checks.txt
(empty)
```

`FLOOR_LANES` in `scripts/ci-required-guard.py` is byte-identical to main
(`["append-only","build-test","cache-matrix","fixtures","govulncheck","docker-build"]`).
`Makefile` is not in the diff at all. **The builder's "claimed unchanged" set is true.**

Non-testdata diff: 24 files — the two workflows, both guards, `go-test-report.py` (new),
`assert-runtime-image.sh` (new), `image-scan-verdict.py`, `test-floors.json` (new),
two Go test files, AGENTS.md, README, `docs/quality/COMMANDS.md`, and
`docs/evidence/hardening-b1/`. 95 files are `scripts/testdata/` fixtures.

## 2. Baseline at the head SHA

| Command | Exit | Result |
|---|---|---|
| `./scripts/make-integrity-guard.sh` | 0 | `passed (8 gate target(s))` |
| `./scripts/ci-required-guard.sh` | 0 | `passed (6 required check(s))`, 44 ok lines |
| `go test -race -count=1 ./scripts/` | 0 | `ok github.com/yegamble/vizra-core/scripts 13.535s`, 20 top-level tests, 127 PASS lines, **0 skips** |

Fixture directory counts (brief item a): `scripts/testdata/guard` **44** (builder claimed 44 ✔),
`gotest` 12 entries — 10 fixture dirs + 2 `floors*.json` files (builder said "11"; the
difference is bookkeeping, not a missing case), `fakedocker` 6 entries — 5 stub dirs +
`README.md` (builder said 5 ✔), `imagescan` **16** ✔.

---

## 3. The evasion matrix — attacking check 8b (brief item b)

Both guards' "what this does NOT give you" lists are declared **EXHAUSTIVE**. The test
below is therefore: for each evasion, is the guard RED, or GREEN-and-listed, or
**GREEN-and-UNLISTED** (a defect in a list that claims to be exhaustive)?

Harness: the real `.github/workflows/` tree copied to a temp dir, the `make ci` step in
`build-test.yml` replaced, digest asserted to have moved, then
`python3 scripts/ci-required-guard.py --workflows … --manifest … --makefile …`.
Control (comment-only edit): **GREEN, exit 0** — the harness does not fail open.

"Neuters?" is measured, not assumed: a two-line `Makefile` whose `ci` recipe does
`@echo RECIPE RAN; exit 7`, run under **GNU Make 4.3 on ubuntu:24.04** (the CI runner's
version) and cross-checked on the host's 3.81.

### 3a. The builder's own ten spellings — all reproduce RED

| # | Mutation | Guard |
|---|---|---|
| B1 | `make -i ci` | RED exit 1 |
| B2 | `make SHELL=/usr/bin/true ci` | RED exit 1 |
| B3 | `make ci SHELL=/usr/bin/true` (override **after** the target) | RED exit 1 |
| B4 | `make --ign ci` (long-option abbreviation) | RED exit 1 |
| B5 | `make -srik ci` (short cluster) | RED exit 1 |
| B6 | `bash -c "make -i ci"` | RED exit 1 |
| B7 | `env MAKEFLAGS=-i make ci` | RED exit 1 |
| B8 | step `env: MAKEFLAGS: -i` | RED exit 1 |
| B9 | `make -C build ci` | RED exit 1 |
| B10 | `go build ./... && make --keep-going ci` | RED exit 1 |

Each red names the flag *and what it does* ("`-i/--ignore-errors`: every recipe's failure
is ignored and make exits 0"). **Item 1's claimed demonstrations reproduce.**

### 3b. My own evasions

| # | Evasion (in `build-test`'s `make ci` step) | Guard | Neuters `make`? (measured, Make 4.3) | Verdict |
|---|---|---|---|---|
| A3 | `eval "make -i ci"` | RED | — | red |
| A4 | `echo ci \| xargs make -i` | RED | — | red |
| A5 | `nice make -i ci` | RED | — | red |
| A6 | `time make -i ci` | RED | — | red |
| A8 | `exec make -i ci` | RED | — | red |
| A9 | here-doc feeding `sh` (`sh <<'EOS' / make -i ci / EOS`) | RED | — | red |
| A10 | line continuation splitting `-i` onto the next line | RED | — | red |
| A12 | `make ci -i` (flag after target) | RED | — | red |
| A13 | `make --ignore-errors=yes ci` | RED | — | red |
| A14 | `make -ki ci` | RED | — | red |
| A15 | `make -j4 -i ci` | RED | — | red |
| A28 | `make -e ci` | RED | — | red |
| A29 | `make -f Makefile -i ci` | RED | — | red |
| A30 | YAML anchor/alias duplicating the step with `-i` | RED | — | red |
| A31 | untokenisable `run:` (unbalanced quote) | RED | — | red (FAILURE, not skip — as documented) |
| A32 | `make -E bogus -i ci` | RED | — | red |
| A34 | `echo $(make -i ci)` | RED | — | red |
| A23 | `continue-on-error: ${{ true }}` | RED | — | red |
| A7 | `sudo -E make ci` | GREEN | **no** — `-E` is sudo's, `make ci` still fails | correct |
| A11 | `make -- -i ci` | GREEN | **no** — after `--`, `-i` is a *target*; make exits 2 | correct |
| A26 | wrapper script `./scripts/wrap.sh` running `make -i ci` | GREEN | yes | **green — LISTED** (residual bullet 1) |
| **A16** | **`make -j -i ci`** | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| **A17** | **`make -l -i ci`** | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| **A18** | **`export MAKEFLAGS=-i` on a line above `make ci`, same `run:`** | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| **A18b** | **`export GNUMAKEFLAGS=-i` likewise** | **GREEN** | **YES — exit 0 on Make 4.3** (3.81 ignores it) | **green — UNLISTED** |
| **A19** | **`echo 'MAKEFLAGS=-i' >> "$GITHUB_ENV"` in an earlier step** (after the anchor) | **GREEN** | **YES** (GHA documented behaviour) | **green — UNLISTED** |
| **A20** | **step-level `shell: bash -c '{0} \|\| true'`** | **GREEN** | swallows the exit code entirely | **green — MIS-listed** (see FINDING 4) |
| **A21** | **`working-directory: build/other`** (a different Makefile) | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| **A22** | **`if: always() && false` on the `make ci` step** | **GREEN** | step never runs at all | **green — UNLISTED** |
| **A24** | **`make() { :; }` then `make ci` in the same `run:`** | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| **A25** | **PATH shadow: write a stub `make`, then `PATH=/tmp/sh:$PATH make ci`** | **GREEN** | **YES** | **green — UNLISTED** |
| **A1** | **`M=make` then `$M -i ci`** | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| **A2** | **`${MAKE:-make} -i ci`** | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| **A33** | **`echo \`make -i ci\`** (command substitution in backticks) | **GREEN** | **YES — exit 0** | **green — UNLISTED** |
| A27 | `shopt -s expand_aliases; alias make='make -i'; make ci` | GREEN | not reproduced (exit 2 on both makes) | not demonstrated |

Measured neutering, verbatim, GNU Make 4.3 / `ubuntu:24.04`:

```
GNU Make 4.3
baseline                       exit=2
make -j -i ci                  exit=0
make -l -i ci                  exit=0
export MAKEFLAGS=-i            exit=0
export GNUMAKEFLAGS=-i         exit=0
M=make; $M -i ci               exit=0
func shadow                    exit=0
alias expand                   exit=2
```

**Thirteen distinct evasions leave both guards green and are on neither exhaustive list.**
They fall into four mechanisms, written up as FINDINGS 1–4 below.

---

## 4. Items 2–7, reproduced

### Item 2 — the checked set (PR#6 FINDING 6): **reproduces**

The PR#6 verifier's `extra-lane` fixture, run at both trees:

```
main@5eb2829 guard:  ok    required check 'extra-lane' resolves to a job        EXIT=0
this head:           ok    checked set is floor ∪ required (7 lanes); beyond the floor: ['extra-lane']
                     FAIL  … is not triggered on pull_request.
                     FAIL  … invokes `make` (step 'step 0') with NO make-integrity-guard step before it.
                     FAIL  … step 'step 0' no-ops `make` from the WORKFLOW LINE:
                     FAIL  … carries continue-on-error:                          EXIT=1
```

The committed fixture yields **4** FAILs (it has no checkout step, so check 10 is
correctly satisfied). The builder's D2 ran an ad-hoc variant that *did* check out,
giving the 5th (`no scripts/provenance.sh step`). Both are internally consistent;
the "five FAILs" figure is D2's construction, not the committed fixture's. Not a defect.

### Item 3 — counts, floors and skips: **reproduces, with one gap (FINDING 7)**

My own runs, on my own services (`vzv9pr9-pg` PostgreSQL 18 on :55913, `vzv9pr9-cache`
Valkey 9.1.2 on :63913), running the workflow's steps verbatim:

```
go test (unit) exited 0
  tests executed:           1047  (floor: 900)     skipped: 0     report exit 0
go test (integration) exited 0
  tests executed:           1092  (floor: 940)     skipped: 0
  github.com/yegamble/vizra-core/internal/integration: 45 test(s) (floor: 40)   report exit 0
```

**All three claimed numbers reproduce exactly**, and the zero-skip figure is *measured*
(the `-json` stream carries an explicit `skip` action per test), not assumed.

Vacuity attacks on `go-test-report.py`:

| Attack | Result |
|---|---|
| `go test -run '^$'` (select nothing) | report **exit 1** — `only 0 test(s) executed; floor 900` |
| `go test -count=0` | report **exit 1**, same |
| truncated stream, clean line boundary (40%) | **exit 1** — 420 < floor |
| truncated stream, cut mid-line | **exit 1** — *and* `1 line(s) … are not JSON events; the stream is truncated or corrupt` |
| empty events file | **exit 1** — `contains no go test -json events; nothing ran` |
| a package that fails to **build** | `go test` exit 1; report **exit 1** — `package … FAILED with no failing test — a build or a panic before the harness ran` |
| `t.Skip` top-level | skip event seen, **exit 1** naming the test |
| `t.Skip` inside a **subtest** | skip event `TestVZVSubtestSkip/sub` seen, **exit 1** |
| `t.SkipNow()` after `t.Parallel()` | skip event seen, **exit 1** |
| `-short` flipping a `testing.Short()` guard | skip event seen, **exit 1** |
| a **stale/foreign** events file that clears the floor | **exit 0** — the tool does not bind the stream to this invocation. Not reachable from the committed step (`go test … > unit-events.json` truncates first); recorded as an observation, not a finding. |
| **emptying a package other than `internal/integration`** | **exit 0** — see FINDING 7 |

`--go-exit-file` absent → exit 1; floors file missing/`min_tests` absent → exit 1
(`TestGoTestReportRefusesASuiteWithNoFloor`). The report is a genuine control.

### Item 4 — the integration suite off the make path: **reproduces**

`git diff` shows the direct steps **replaced** the recipe invocations — the
`make test-integration` / `make test-integration-shuffle` steps are deleted, not
supplemented. Flags compared line by line against `Makefile:162` and `Makefile:170`:
both use `-race -count=1 -tags=integration ./...` (plus `-shuffle=on`), the same
three env vars, the same Valkey container. The recipe's "services absent ⇒ BLOCKED,
not passed" refusal is reproduced inline. **Both `cache-matrix` legs still run
`make test-integration` and `make test-integration-shuffle`** (workflow lines 440, 451),
so the recipes keep required coverage. `make test-integration` here: **exit 0, 15 ok**.

Guard check 9 is red when both direct integration steps are deleted
(`no required lane runs the INTEGRATION suite directly`) and green when only one is —
correct, since the shuffled step is itself a direct integration invocation.

`timeout-minutes` unchanged by this PR (no line in the diff). `build-test` on this SHA:
**09:01:09 → 09:12:12 = 11m03s** of a **20-minute** timeout — in line with the
10m59s/11m08s baselines. Runtime-neutral, as claimed.

### Item 5 — `append-only` provenance is a control: **reproduces**

Driven against purpose-built merge refs:

```
honest merge ref, PR_HEAD_SHA == HEAD^2   exit 0   "checked: HEAD^2 == the PR head SHA"
PR_HEAD_SHA != HEAD^2                     exit 1   ::error::HEAD^2 (…) is not the PR head SHA (…)
checkout pinned to the head (no HEAD^2)   exit 1   ::error::HEAD has no second parent …
depth-1 shallow clone                     exit 0   parent method: cat-file (parent objects are not present)
```

Guard check 10 is red when the step is deleted from `append-only`, and red when it is
made conditional (`makes the provenance step CONDITIONAL (if: …)`).

**On CI for this SHA** the step names the tree it actually stood in:

```
TESTED TREE (git rev-parse HEAD):  60793e1ee2eba77a93ece395934b22405f0278b4
base actually merged in (HEAD^1):  5eb2829eb4f830206029f8e2a836f93a44a93a02
head actually merged in (HEAD^2):  e710c3cff18bd63c87a692937b608fa762627d99
checked: HEAD^2 == the PR head SHA, so this really is the merge ref.
```

### Item 6 — the image assertions: **control verified; the demonstration is not (FINDING 5)**

`assert-runtime-image.sh` against five stub `docker` binaries of my own:

| stub | behaviour | script |
|---|---|---|
| exits 125 on everything | daemon gone | **exit 1** — "the container did not run while checking the build toolchain (docker exited 125)" |
| exits 0, prints nothing | runs but says nothing | **exit 1** — `test -e /src` returning 0 is read as `/src` present |
| prints a usage banner, exit 1 | wrong invocation | **exit 1** |
| prints a usage banner, exit 0 | garbage on stdout | **exit 1** — "carries build tooling" |
| reports a toolchain | real positive | **exit 1** |
| hangs (`sleep 600`) | — | **no timeout in the script**; killed externally at 25s. In CI the job's 45-minute `timeout-minutes` bounds it and a timed-out lane is not a pass, so this fails closed. Observation, not a finding. |

Empty / comments-only / absent denylist → exit 1 each.

**On CI for this SHA**, against the real `linux/amd64` image:

```
checking for: gcc cc g++ cpp ld as ar make cmake meson ninja pkg-config pkgconf curl wget xz go git
  ok   no build tooling on PATH (18 names checked)
  ok   no -dev packages installed
  ok   no /src
assert-runtime-image: ok — vizra-core:ci carries no toolchain, no -dev packages and no source tree
```

The assertions ran and passed **for the right reason** — 18 names checked, three
distinct ok lines, the final banner.

### Item 7 — `--fail-on`: **reproduces**

```
--fail-on ''           exit 3   ::error::image-scan: --fail-on is empty ('');  …cannot fail
--fail-on ,            exit 3   ::error::image-scan: --fail-on is empty (',')
--fail-on HIGH,BOGUS   exit 3   ::error::image-scan: --fail-on names severities Trivy does not use: ['BOGUS']
--fail-on high         exit 0   (case-normalised to HIGH — correct)
--fail-on UNKNOWN      exit 0   (a real Trivy severity)
--fail-on LOW          exit 1   (the findings path, on the `good` fixture)
--fail-on repeated     exit 1   (argparse last-wins; harmless)
```

**On CI for this SHA**, `image-scan` failed on the *valid* path:

```
trivy exit code: 0
##[error]image-scan: 48 finding(s) at or above ['CRITICAL', 'HIGH']
##[error]Process completed with exit code 1.
```

Exit **1 (findings)**, not 3 (verdict error) — the `--fail-on` change did not break the
valid path. Every finding is an unfixed Debian 13.7 base CVE (`libtiff6`, `util-linux`,
`libexpat1`, `ncurses`, `libsystemd0` …). `image-scan` is deliberately **not** in
`.github/required-checks.txt`; that exclusion is unchanged by this PR.

---

## 5. Guard self-consistency and diff audit (brief items f, g)

| Mutation | Guard |
|---|---|
| `required-checks.txt` comments out `fixtures` | **RED** — `required lane 'fixtures' is COMMENTED OUT` |
| manifest names a job that does not exist | **RED** — `matches no job` |
| the make-integrity anchor step deleted | **RED** — `invokes make … with NO make-integrity-guard step before it` |
| the direct **unit** step deleted | **RED** — `no required lane runs the UNIT suite directly` |
| both direct **integration** steps deleted | **RED** — `no required lane runs the INTEGRATION suite directly` |
| provenance step deleted / made conditional | **RED** (both) |
| `continue-on-error: 'True'` (quoted, capitalised) | **RED** |
| `continue-on-error: ${{ true }}` (expression) | **RED** |
| workflow-level `defaults.run.shell: /usr/bin/true {0}` | **RED** |
| **the `go-test-report.py` call deleted from the direct step** | **GREEN** — see FINDING 6 |

Diff audit: **no new `continue-on-error`**, **no new `|| true`** outside comments and
two legitimately scoped uses (`grep` no-match inside the container; denylist extraction,
both explained in-line), **no new `if:`** on any workflow step except the pre-existing
`if: always()` on the artifact upload. `.github/required-checks.txt`, `FLOOR_LANES`,
`Makefile`, `scripts/provenance.sh` all unchanged.

Every new test runs in a required lane: the eight new `Test…` functions live in
`scripts/scripts_test.go` and `scripts/imagescan_test.go`, package
`github.com/yegamble/vizra-core/scripts`, which the direct unit step covers via `./...`.
The CI log for this SHA shows the package executed — `scripts` is one of the 14
`packages ok`, and `make ci`'s log carries `ok github.com/yegamble/vizra-core/scripts 24.454s`.
`TestEveryGuardFixtureIsExercised` and `TestEveryImageScanFixtureIsExercised` both pass,
so a check cannot be dropped by orphaning its fixture.

## 6. CI on `e710c3cf` (brief item h)

| check | conclusion | note |
|---|---|---|
| `ci-required` | **success** | reads the manifest with `mapfile`, collects each name's `check_runs` conclusion, prints `SUCCESS <name>`; the guard's 44 ok lines are in this job's log |
| `append-only` | success | floor lane |
| `build-test` | success | floor lane — 11m03s / 20m |
| `cache-matrix` | success | floor lane (+ both legs, `redis` and `valkey`, green) |
| `fixtures` | success | floor lane |
| `govulncheck` | success | floor lane |
| `docker-build` | success | floor lane |
| `image-scan` | **failure** | **not required** — 48 unfixed Debian base CVEs, exit 1 (findings) |
| GitGuardian | success | not in the manifest |

All six `FLOOR_LANES` ran and are green on this SHA; the manifest and the jobs that
actually ran agree; no required lane was skipped, cancelled or missing. Runner
`ubuntu-24.04` (image 20260907.300.1) with **GNU Make 4.3**. The job log prints the
executed and skip counts three times (unit, integration, integration-shuffled) —
this closes PR#7's "CI cannot corroborate skip counts".

## 7. Truthfulness of the PR body, evidence and docs (brief item i)

| Claim | Verdict |
|---|---|
| "No change under `api/`, `internal/`, `cmd/` or `migrations/`" | **TRUE** — diff empty |
| "`.github/required-checks.txt` and `FLOOR_LANES` byte-identical to main" | **TRUE** |
| "unit 1047 executed, 0 skipped, floor 900" | **TRUE** — reproduced locally and in the CI log |
| "integration 1092, 0 skipped, floor 940; `internal/integration` 45, floor 40" | **TRUE** — both |
| "`make ci` exit 0; 14 ok, 8 `[no test files]`" | **TRUE** |
| "`make test-integration` exit 0, 15 ok" | **TRUE** |
| "44 guard fixtures + 11 gotest + 5 fakedocker + 16 imagescan" | **TRUE** for 44, 5, 16; `testdata/gotest` holds 10 fixture dirs + 2 floors files. Bookkeeping, not a missing case. |
| "D1: 16 mutations, all exit 1" | **TRUE** — I reproduced ten of them by name plus seven more of my own |
| "D2: five FAILs where main printed one `ok`" | **TRUE of D2's construction**; the committed fixture gives 4 (no checkout ⇒ no check-10 FAIL) |
| "the direct steps REPLACED the recipe invocations; no added runtime" | **TRUE** — measured 11m03s vs 10m59s/11m08s; no `timeout-minutes` changed |
| "build-test ~11m against a 20-minute timeout" | **TRUE** — 11m03s |
| PR does **not** cite the deleted `make test-integration-shuffle` log's counts | **TRUE** — no such number appears in the PR body or in `docs/evidence/hardening-b1/` |
| "`D6` runs **main's inline shape verbatim** … EXIT=0" | **FALSE as written** — see FINDING 5 |
| AGENTS.md: the wrapper-script bullet "is **the whole remaining residual** of the one-word evasion" | **FALSE** — see FINDINGS 1–3 |
| both guards' residual lists are "meant to be EXHAUSTIVE" | **FALSE** — thirteen unlisted evasions |
| `scripts/test-floors.json` `_why`: "Measured on 5eb2829 + this branch … unit 1001 … integration 1046" | **STALE** — this branch measures 1047 / 1092. See FINDING 8. |

`README.md` and `docs/quality/COMMANDS.md` additions are accurate: the commands they
give reproduce what CI asserts, and I ran them as written.

---

## Findings

```
FINDING 1: check 8b lets `-j`/`-l` swallow the next flag, and does not read an
           `export MAKEFLAGS` inside the same `run:`
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py:323 (SHORT_TAKES_ARG), :390-432 (_scan_make_argv),
             :433-463 (make_command_line_problems), :120-152 (the EXHAUSTIVE residual list)
             AGENTS.md:45-108 (the assurance table and its residual list)
  requirements: none yet — propose VZ-OPS-CI-00x (a floor lane's make step cannot be no-opped)

Observed:
  `SHORT_TAKES_ARG = set("CfIjloWE")` treats `j` and `l` as argument-taking, and
  _scan_make_argv does:
      if pos == len(tok) - 1 and i < len(argv):
          i += 1
  so in `make -j -i ci` the token after `-j` is consumed as -j's argument and never
  scanned. But GNU make declares `-j`/`--jobs` and `-l`/`--load-average` with
  optional_argument, which getopt_long only accepts ATTACHED (`-j4`). A separate
  `-i` is therefore a flag to make and an argument to this guard.

  Measured, GNU Make 4.3 on ubuntu:24.04 (the CI runner's version), against a
  Makefile whose `ci` recipe is `@echo RECIPE RAN; exit 7`:
      baseline            exit=2
      make -j -i ci       exit=0      <- neutered
      make -l -i ci       exit=0      <- neutered
      export MAKEFLAGS=-i ; make ci   exit=0
      export GNUMAKEFLAGS=-i ; make ci exit=0
  Guard verdict on each, with the step substituted into the real build-test.yml:
  GREEN, exit 0, printing `ok  checked lane 'build-test': 3 make step(s) carry no
  no-op flag, no variable override and no MAKEFLAGS-family env`.

  For the export case, `_commands()` splits the `run:` on `;` and newlines, so
  `export MAKEFLAGS=-i` is a command of its own and `make ci` has an empty
  argv[:make_at] — the MAKE_ENV_NAMES test only inspects tokens BEFORE `make` in
  the SAME command. The anchor (check 8) cannot cover it: it runs in its own
  step, hence its own process, with a clean environment.

Failure:
  A one-token edit on a workflow line — `make -j -i ci`, or one `export` line
  above `make ci` — makes every make-driven gate exit 0 without running, with
  both guards green and an `ok` line asserting the opposite. That is the exact
  defect PR#6 FINDING 1 recorded and this PR claims to close. Blast radius:
  fmt-check, vet, lint-imports, migrate-lint, config-template-check,
  openapi-verify, sqlc-verify, ci-guard, fixtures-verify, tidy-check, build, and
  both cache-matrix legs. (The unit and integration SUITES survive, because
  control 3 now invokes them directly — that part of B1 does hold.)

Perspective:
  developer, operator

Recommendation:
  Two lines. (a) Remove `j` and `l` from SHORT_TAKES_ARG — GNU make requires
  their argument to be attached, so nothing legitimate breaks and `-j4` still
  parses (it already breaks out of the cluster loop without consuming).
  (b) In make_command_line_problems, scan EVERY command in the `run:` for a
  `export NAME=…` / `NAME=…` assignment in MAKE_ENV_NAMES, not only the tokens
  before `make` in the same command — the whole `run:` is one shell process.

Acceptance criteria:
  With `run: make -j -i ci`, `run: make -l -i ci`, and a `run:` block whose first
  line is `export MAKEFLAGS=-i` (and one with GNUMAKEFLAGS), ci-required-guard.py
  exits 1 naming the flag or the variable. A fixture under scripts/testdata/guard/
  for each, and the control case `make -j4 ci` still exits 0.

Tests:
  scripts/scripts_test.go TestCIRequiredGuardFixtures, with new fixture dirs
  make-flag-optarg-swallow/, make-flag-load-swallow/, make-export-makeflags/,
  make-export-gnumakeflags/ and the green control make-jobs-attached/.
  TestEveryGuardFixtureIsExercised already forces each to be named.

Cross-repo implications:
  core: this guard. user: none. search: vizra-search carries the same guard
  lineage (its PR#2 verifier found FINDING 8) — the same two fixes apply there.
  meta: the assurance table in this repo's AGENTS.md is quoted by the war-room
  board; it must be corrected with the fix.

Challenge:
  `-j -i` and a stray `export` are visible in a diff, and CODEOWNERS is the
  backstop. True — but that argument applies equally to `make -i ci`, which this
  PR spent 534 lines refusing, and CODEOWNERS is documented here as advisory
  only. A control that refuses nine spellings and accepts the tenth is worse
  than one that admits it reads nothing, because the `ok` line is read as proof.
```

```
FINDING 2: a checked lane's make step can be skipped entirely (`if:`) or pointed
           at a different Makefile (`working-directory:`), unread by either guard
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py:475-543 (check_make_command_lines),
             :587-649 (check_anchor), :683-732 (check_direct_test_lane)
  requirements: none yet — propose VZ-OPS-CI-00x

Observed:
  Substituted into the real build-test.yml and run through the guard:
      - name: make ci
        if: always() && false          -> guard GREEN, exit 0
        run: make ci
      - name: make ci
        working-directory: build/other -> guard GREEN, exit 0
        run: make ci
  check_anchor asserts the ANCHOR step is unconditional and not continue-on-error,
  and check_direct_test_lane explicitly refuses a conditional direct step
  (`if "if" in step: continue  # a conditional lane is not a floor`). Neither
  check applies that reasoning to the make step itself.

  `working-directory:` is the same effect as `-C`, which check 8b refuses by name
  with the reason "make changes directory first, so it reads a different
  makefile". Measured: `cd other && make ci` against a different Makefile exits 0
  where the real one exits 2.

  Neither appears on either EXHAUSTIVE residual list.

Failure:
  `if: ${{ false }}` on `run: make ci` means `make ci` never executes and
  build-test is green with the guard printing `ok  … 3 make step(s) carry no
  no-op flag`. `working-directory:` runs a Makefile the integrity guard never
  read — the precise condition check 8 exists to prevent.

Perspective:
  developer, operator

Recommendation:
  In check_make_command_lines, FAIL when a make step in a checked lane carries
  `if:` at all (the anchor is already held to that standard), and FAIL when it
  carries `working-directory:` pointing anywhere but the repository root — or
  simply refuse `working-directory:` on a make step, since no lane here uses one.

Acceptance criteria:
  A make step with any `if:`, and a make step with any `working-directory:`, each
  turn ci-required-guard.py red with a named reason. The real workflows still
  pass (no make step in them carries either).

Tests:
  scripts/scripts_test.go TestCIRequiredGuardFixtures, fixtures
  make-step-conditional/ and make-step-working-directory/.

Cross-repo implications:
  core: this guard. user: none. search: same guard lineage. meta: none.

Challenge:
  A job-level `if:` that skips the whole lane makes the CHECK skipped, and
  ci-required already refuses a skipped required check — so job-level is covered.
  Correct, and that is why this finding is about the STEP-level `if:`, which
  leaves the job green and the check SUCCESS.
```

```
FINDING 3: `make` reached indirectly — a variable, a shell function, a PATH edit,
           a backtick — is unlisted, and the "wrapper script" bullet does not cover it
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py:286 (MAKE_INVOCATION), :352 (MAKE_COMMAND),
             :120-152 (residual list); AGENTS.md:83-92 (residual list)
  requirements: none yet — propose VZ-OPS-CI-00x

Observed:
  Each substituted into the real build-test.yml; guard verdict, then the measured
  effect on GNU Make 4.3:
      run: |
        M=make
        $M -i ci                      GREEN   make exits 0 (neutered)
      run: ${MAKE:-make} -i ci        GREEN   make exits 0
      run: |
        make() { :; }
        make ci                       GREEN   exits 0 — the guard PRINTS `ok … carry no no-op flag`
      run: |
        mkdir -p /tmp/sh && printf '#!/bin/sh\nexit 0\n' > /tmp/sh/make && chmod +x /tmp/sh/make
        PATH=/tmp/sh:$PATH make ci    GREEN   PATH is not in MAKE_ENV_NAMES
      run: echo `make -i ci`          GREEN   backticks: no token matches ^g?make$, and the
                                              docstring's "reported rather than passed silently"
                                              is an informational line, not a FAIL
  For `$M` and `${MAKE:-make}` the step is not even classified as a make step
  (MAKE_INVOCATION's leading character class excludes `=` and `-`), so no anchor
  is demanded either.

  The only listed bullet is "a wrapper script, a `uses:` composite action or a
  reusable workflow … carries no `make` token". Three of the five above DO carry
  the token and the guard actively prints an `ok` about them; none needs a new
  file, so the mitigation the bullet leans on ("louder in a diff … it needs a new
  script or action as well as the workflow edit") does not apply.

Failure:
  Same blast radius as FINDING 1, reachable without adding a file to the
  repository — and in three of the five cases the guard emits a positive `ok`
  line about the very step that is neutered.

Perspective:
  developer, operator

Recommendation:
  This one cannot be closed by parsing — it is shell. The honest fix is to say
  so: replace the single wrapper-script bullet with "**`make` reached by any
  indirection is not read**: a shell variable, a function definition, an alias, a
  PATH edit, command substitution, a wrapper script, a `uses:` composite action
  or a reusable workflow. REVIEW-ONLY." Optionally add the cheap mechanical
  narrowing: FAIL a checked lane's make-step `run:` that defines a function named
  `make`, assigns PATH, or contains a `$`-expansion in command position.

Acceptance criteria:
  Both residual lists (guard docstring and AGENTS.md) name indirection as a class
  with these five spellings, and neither claims the wrapper-script bullet is "the
  whole remaining residual". If the mechanical narrowing is taken, fixtures prove
  the three refusable spellings red.

Tests:
  scripts/scripts_test.go TestCIRequiredGuardFixtures for whichever spellings are
  made mechanical; the rest are documentation, checked by review.

Cross-repo implications:
  core: this guard and AGENTS.md. user: none. search: same lineage. meta: the
  war-room board quotes "the whole remaining residual".

Challenge:
  Any list of shell tricks is unbounded, so refusing to enumerate is defensible.
  Agreed — which is exactly why the list must not be labelled EXHAUSTIVE and must
  not name one bullet as "the whole remaining residual".
```

```
FINDING 4: the step-level `shell:` bullet claims it "fails closed toward refusing";
           a custom shell that swallows the exit code passes
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py:143-146
  requirements: none yet

Observed:
  The docstring says: "`defaults.run.shell` is refused, but `shell:` on an
  individual step is not — a step-level `shell: python` on a make step would make
  the `run:` text not a shell script at all. It is still tokenised and still
  anchored, so this fails closed toward refusing, not toward passing."
  Substituted into the real build-test.yml:
      - name: make ci
        shell: bash -c '{0} || true'
        run: make ci
  Guard: GREEN, exit 0. GitHub Actions' documented custom-shell form is
  `<command> [options] {0}`, so this runs the step script and discards its
  status — the step passes whatever `make ci` did. Workflow-level
  `defaults.run.shell: /usr/bin/true {0}` IS refused (I confirmed it goes red),
  which makes the step-level gap an inconsistency rather than a stated position.
  UNVERIFIED: I did not execute this on a live GitHub runner; the claim rests on
  the documented custom-shell contract, not on an observed run.

Failure:
  A reader of the docstring concludes step-level `shell:` cannot make a lane
  pass. It can, by the same mechanism the guard refuses one scope higher.

Perspective:
  developer

Recommendation:
  Refuse `shell:` on a make step in a checked lane unless it is one of the
  allowed values (`bash`, `sh`, `bash -e {0}`), the same way
  `defaults.run.shell` is refused — and correct the docstring sentence.

Acceptance criteria:
  A make step with `shell: bash -c '{0} || true'` turns the guard red; the real
  workflows (which set no step-level `shell:`) still pass.

Tests:
  scripts/scripts_test.go TestCIRequiredGuardFixtures, fixture
  make-step-custom-shell/.

Cross-repo implications:
  core: this guard. user/search/meta: none.

Challenge:
  `shell:` on a step is rare and conspicuous. True — but the docstring's claim is
  affirmative, and this PR is being judged on whether its text matches its control.
```

```
FINDING 5: D6's headline "OLD SHAPE EXIT=0" is not what main's committed step does
           with the stub the evidence names
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     docs/evidence/hardening-b1/D6-docker-run-failure.txt:1-30,
             the PR body § "6 — the `docker run` failure",
             scripts/testdata/fakedocker/broken
  requirements: AGENTS.md § Completion and evidence ("Do not fabricate outputs")

Observed:
  D6 quotes main's three-assertion step in full under the heading "reproduced
  verbatim", then prints:
      docker: Error response from daemon: no such image
      no build tooling on PATH
      docker: Error response from daemon: no such image
      no /src
      OLD SHAPE EXIT=0   <-- 0. Both assertions PASSED against a daemon that ran nothing.
  I extracted that step's `run:` from `git show 5eb2829:.github/workflows/
  docker-build.yml` with a YAML parser and ran it with the named fixture
  `scripts/testdata/fakedocker/broken` on PATH as `docker`:
      checking for: gcc cc g++ cpp ld as ar make cmake meson ninja …
      docker: Error response from daemon: no such image
      no build tooling on PATH
      docker: Error response from daemon: no such image
      OLD SHAPE EXIT=125
  The middle assertion `devpkgs=$(docker run …)` has no `|| true` on the OUTER
  command substitution, so under the step's own `set -euo pipefail` a 125 kills
  the step. `broken` returns 125 for the dpkg probe too. D6's transcript shows
  neither that error nor the `no -dev packages installed` line that a success
  would print — the middle assertion did not run in whatever was measured.

  The underlying defect IS real, and I reproduced it: with a stub that fails only
  probes 1 and 3, main's step prints "no build tooling on PATH", "no -dev
  packages installed", "no /src" and exits 0. And the PR#7 verifier's original
  FINDING 1 (Severity SHOULD) claimed only that the step "prints 'no build
  tooling on PATH' and PASSES" for that assertion — not that the step exits 0.

Failure:
  The PR body states, as a measured result, that main's inline shape "run verbatim
  against a stub daemon that exits 125" exits 0. Against a stub that exits 125 it
  exits 125. The demonstration is stronger than the thing demonstrated, in a PR
  whose subject is controls that must not claim more than they check.

Perspective:
  developer

Recommendation:
  Re-run the old shape with a stub whose failure mode actually produces EXIT=0
  (fails probes 1 and 3, succeeds on the dpkg probe), commit that stub alongside
  `broken`, and restate D6 and the PR body as: "assertion 1 and assertion 3 each
  pass on a docker failure; with a daemon that fails only those two, the whole
  step exits 0." No code change — the script itself is correct and I verified it
  against five independent stubs.

Acceptance criteria:
  D6 and the PR body describe a run that can be reproduced from the fixtures in
  the tree, with the fixture named and the exit code matching.

Tests:
  scripts/scripts_test.go, a fifth fakedocker mode (e.g. `broken-probes-1-3`)
  driven by TestAssertRuntimeImageFixtures, asserting the NEW script exits 1
  where the old shape exited 0.

Cross-repo implications:
  core only.

Challenge:
  The fix is right and the number is incidental. That is the argument this war
  room has rejected nine times; the chair's standing rule is that a demonstration
  which cannot be reproduced fails the bullet it demonstrates.
```

```
FINDING 6: check 9 prints `ok` for a direct step whose `go test` exit code is
           discarded — one deleted line makes a failing test green
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .github/workflows/build-test.yml:224-233, :273-300, :302-320;
             scripts/ci-required-guard.py:683-732 (check_direct_test_lane)
  requirements: none yet — propose VZ-OPS-CI-00x

Observed:
  At main the direct step was `run: go test -race -count=1 ./...` — a failing test
  failed the step directly. This PR replaces it with:
      set -uo pipefail
      rc=0
      go test -race -count=1 -json ./... > unit-events.json || rc=$?
      echo "$rc" > unit-exit.txt
      echo "go test (unit) exited $rc"
      python3 scripts/go-test-report.py --events … --go-exit-file unit-exit.txt
  The `go test` status is deliberately captured, so the ONLY thing that fails the
  step is the last command — the report call. Measured with a planted
  `t.Fatal` test:
      step as committed            -> exit 1  (::error::go-test-report: FAILED: …)
      report call deleted, nothing else changed -> exit 0   <-- a FAILING test, step GREEN
      main's shape, same test      -> exit 1
  And with the report call deleted, ci-required-guard.py is GREEN and prints
      ok  the unit suite runs directly, without make, in required lane 'build-test'
  check_direct_test_lane matches on `"go test" in run`, `"./..." in run`, no make
  token and no `if:`. It never asks whether the exit code is judged.

  The guard's own docstring for check 9 states its purpose as "whatever make did,
  a real failing test must still fail a required lane" — which is now false of
  any step it will accept.

Failure:
  The second layer — the control that exists because make can be neutered — is
  now one line away from being a no-op, and the guard whose job is to assert it
  is "present and armed" cannot tell. That is the false-positive `ok` line the
  guard's own preamble is written against.

Perspective:
  developer, operator

Recommendation:
  In check_direct_test_lane, require that a direct-suite step also invokes
  `scripts/go-test-report.py` with `--go-exit-file`, or that the `go test`
  invocation is the step's last command. The first is a two-line substring test
  and matches what the workflow already does three times.

Acceptance criteria:
  Deleting the `go-test-report.py` call from either direct step turns
  ci-required-guard.py red with a named reason; the committed workflows still pass.

Tests:
  scripts/scripts_test.go TestCIRequiredGuardFixtures, fixture
  direct-lane-without-report/.

Cross-repo implications:
  core only, today. If vizra-user or vizra-search adopt the -json + report shape,
  the same assertion belongs there.

Challenge:
  The report call is present, so nothing is broken today. Correct — this is about
  the guard's `ok` line asserting a property it does not check, which is the
  defect class this whole PR exists to remove, and it is a REGRESSION against
  main, where the bare `go test` could not be weakened this way.
```

```
FINDING 7: only one package has a floor; 12 of 14 unit packages can be emptied
           inside the 147-test headroom
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/test-floors.json:29-40, :2-26 (the `_why` block)
  requirements: none yet

Observed:
  The unit suite has `min_tests: 900` and NO `min_package_tests`. Measured
  executed counts on this head, from the `-json` stream:
      502 internal/authz   129 internal/search   127 scripts   96 internal/config
       42 internal/fixtures  39 internal/doctor   30 internal/httpapi
       30 internal/jobs      17 internal/obs      12 internal/healthcheck
       10 cmd/vizra           6 internal/cache     6 internal/site   1 cmd/api
  Total 1047; headroom above the floor is 147.

  I reproduced the builder's D4 — moving `internal/integration/*_test.go` aside
  leaves 1047 of a 940 suite floor and is caught ONLY by the per-package floor
  (`internal/integration executed 0 test(s); its recorded floor is 40`). Correct
  as claimed.

  Then I emptied a different package. `internal/search` (129 tests, the whole
  search layer):
      go test exit 0
      tests executed:  918  (floor: 900)
      go-test-report: ok — 918 test(s) executed across 13 package(s), floor 900 met
  Exit 0. The same holds individually for internal/httpapi (30), internal/jobs
  (30), internal/obs (17 — the redaction tests), internal/healthcheck (12,
  PR#7's own slice), internal/config (96), internal/fixtures (42),
  internal/doctor (39), cmd/vizra (10), internal/cache, internal/site, cmd/api.

  The file's `_why` says the floors "exist to catch a suite being emptied **or a
  package disappearing**". The second half is true only for internal/integration.

Failure:
  A package's tests can be deleted or build-tagged away and the required lane
  stays green with its count printed and unremarked. `internal/obs` is the
  redaction suite; `internal/authz` is 48% of the count and would be caught, but
  everything else is inside the headroom.

Perspective:
  developer, operator

Recommendation:
  Add `min_package_tests` for the unit suite covering the packages whose absence
  matters — at minimum internal/authz, internal/obs, internal/httpapi,
  internal/healthcheck, internal/config, internal/search — set well below today's
  counts so ordinary churn does not trip them. Or state the limit plainly in the
  `_why` block: "a whole-suite floor does not detect one package disappearing;
  only the packages named in min_package_tests are protected."

Acceptance criteria:
  Moving `internal/obs/*_test.go` aside turns the unit report red naming the
  package. The real tree still passes.

Tests:
  scripts/scripts_test.go TestTheRepositoryFloorsAreUsable extended to assert a
  per-package floor exists for each named package; a gotest fixture
  unit-package-emptied/ in the idiom of integration-package-emptied/.

Cross-repo implications:
  core only.

Challenge:
  Per-package floors are churn-prone and invite ratchet edits. True — which is
  why the alternative (say the limit honestly in `_why`) is offered; what is not
  acceptable is the current text claiming the floors catch "a package
  disappearing" when they catch exactly one.
```

```
FINDING 8: scripts/test-floors.json records measured counts that this branch does
           not produce
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/test-floors.json:8-11

Observed:
  "Measured on 5eb2829 + this branch, go1.27.1, darwin/arm64, `go test -count=1 -json`:
     unit (./...) 1001 tests executed, 0 skips
     integration (-tags=integration ./...) 1046 tests executed, 0 skips"
  This branch measures 1047 and 1092 — locally and in the CI log — because the
  branch adds 46 tests to package `scripts`. The numbers are the pre-branch ones
  under a label that says "+ this branch".

Failure:
  A reviewer setting a future floor reads a number 46 lower than reality.

Perspective:
  developer

Recommendation:
  Update the two numbers, or relabel them "measured at 5eb2829".

Acceptance criteria:
  The `_why` counts match what `go-test-report.py` prints on the same tree.

Tests:
  none needed.

Cross-repo implications:
  none.

Challenge:
  It is a comment. Yes — and it is the comment that explains where the floors
  came from.
```

---

## Cross-PR note for the chair (reported, not acted on)

Core **PR #8** (M1-A owner claim) is open and adds ~60 tests plus one Makefile
`-run` regex edit. Interaction with #9, whichever merges second:

1. **Floors are not at risk from #8.** `scripts/test-floors.json` sets floors of
   900 / 940 against measured 1047 / 1092. #8 ADDS tests, so both floors stay
   met; a floor bump is optional, never required. The per-package floor
   (`internal/integration` ≥ 40, measured 45) only rises if #8 adds integration
   tests — it cannot fall.
2. **The `-run` regex edit is the live conflict.** #9's guard check 5
   (`check_makefile_selection`) asserts "all 2 -run selections are non-empty" by
   reading the Makefile. If #8's edit produces a `-run` pattern the guard reads
   as empty, or adds a third one, the guard's count changes and the lane can go
   red on a Makefile edit that looks innocuous in #8's own diff. Whoever merges
   second must re-run `./scripts/ci-required-guard.sh` on the merge result, not
   just on their own head.
3. **The direct steps and `openapi-verify`.** #9 deletes the `make
   test-integration` / `make test-integration-shuffle` STEPS from `build-test`
   (the recipes survive, used by both cache-matrix legs). If #8 touches those
   workflow steps or the `openapi-verify` recipe, it is a textual conflict in
   `.github/workflows/build-test.yml` around lines 241-320 and in the Makefile's
   gate-target block — `make-integrity-guard` asserts each gate target is defined
   exactly once, so a botched merge that duplicates one goes red by name, which
   is the desired behaviour.
4. **#8 adding a test that SKIPS would now be red.** `allowed_skips` is empty in
   both suites. If any of #8's ~60 tests skips (a `testing.Short()` guard, an
   absent-service skip), `go-test-report.py` fails the lane by name and #8 would
   need a reviewed `allowed_skips` entry with a reason. Worth telling that
   builder before it merges second.

---

## Cleanup

Containers `vzv9pr9-pg` and `vzv9pr9-cache` stopped and removed by exact name;
`ubuntu:24.04` (pulled for the Make 4.3 check) removed by exact name. No other
container, image or cache touched — `vizra-m1a-*`, `vzv8-*` and every `vidra-*`
were left alone. The scratch clone and all mutation temp dirs were deleted.
No file in `yegamble/vizra-core` was modified: every mutation was applied to a
copy or reverted with a verified-clean `git diff`, checked after each one.

---

FINAL VERDICT: FAIL — SHA e710c3cff18bd63c87a692937b608fa762627d99

---
---

# Re-verification at 6b65eff — 2026-09-22

- **Head verified:** `6b65eff6ee29e99e1b93b01242b4c97d90a57267` (fix round 1 of 2). Commits on top of
  my FAIL at `e710c3c`: `8fa04b1` (redesign — pin, don't parse), `6b65eff` (evidence). No force-push:
  `e710c3c` is an ancestor. `git ls-remote` at start: `6b65eff…`, unmoved.
- **Clone:** fresh `mktemp -d …/scratchpad/vzv-core-pr9r1-XXXXXX` (the machine was restarted since round
  one; none of my `vzv9pr9-*` containers survived, so there was nothing of mine to remove).
  Containers of others present at start and left alone: `vzv10-*`, `vizra-m1a-*`, `vidra-ipfs-071-*`.
  My own services this round: prefix `vzv9r1-`, ports 55919/63919.
- **Environment:** as round one — darwin/arm64, go1.27.1, python3 3.9.6 + PyYAML 6.0.3, host GNU Make
  3.81; GNU Make 4.3 exercised in a throwaway `ubuntu:24.04` container named `vzv9r1-make43`.
- **Harness:** my OWN (`h.py`, written fresh in scratch — it copies `.github/` to a temp dir, applies a
  text mutation to `build-test.yml`, asserts the digest moved, and runs
  `ci-required-guard.py --workflows … --manifest … --pins …`). The builder's `evasion-table.py` was read,
  not relied on. Control (comment-only edit): **GREEN** — the harness does not fail open.

## R1. Frozen paths and baseline

```
git diff --stat 5eb2829..6b65eff -- migrations/ api/ internal/ cmd/ sqlcgen/ Makefile .github/required-checks.txt
(empty)
FLOOR_LANES: unchanged
./scripts/make-integrity-guard.sh        exit 0   passed (8 gate target(s)); both new runtime ok lines
./scripts/ci-required-guard.sh           exit 0   passed (6 required check(s)), 49 ok lines
go test -race -count=1 ./scripts/        exit 0   ok … 29.349s
scripts/testdata/guard                   65 fixture dirs (claimed 65 ✔)
```

## R2. My 45 round-one rows, re-run with my own harness

Every row substituted into the real `build-test.yml`'s `make ci` step, the anchor kept in place:

| rows | result |
|---|---|
| B1–B10, A1–A18b, A20–A34 (44 rows) | **all RED** — flag/override/indirection rows by check 8b ("mentions `make` but its `run:` is not byte-equal to any entry in `.github/pinned-steps.yml`"), key rows (`env:`, `shell:`, `working-directory:`, `if:`, `continue-on-error:`) by the name/run/id rule, and the no-`make`-token rows (`M=make; $M -i ci`, `${MAKE:-make}`, the wrapper script replacing `make ci`) by **check 8c** ("does not run required invocation(s) ['make ci']") |
| A19 `$GITHUB_ENV` write in an earlier step | **GREEN at the static guard** — as the builder states; defended only at runtime by the anchor. See R4. |

**The builder's claim "your 45 rows all red by named rule, R3 `$GITHUB_ENV` green at the static
guard" reproduces with my harness.** The round-one FINDINGS 1–4 (tokeniser holes) are closed *as
spellings*.

## R3. Attacking the NEW control — static guard (my harness)

| # | Mutation of `build-test.yml` | Guard | Runtime effect | Verdict |
|---|---|---|---|---|
| **N1** | the anchor step immediately before `make ci` becomes `run: ./scripts/make-integrity-guard.sh && echo "MAKEFLAGS=-i" >> "$GITHUB_ENV"` | **GREEN** | anchor passes, THEN poisons the next step; `make ci` runs with `MAKEFLAGS=-i` (simulated, R4) | **green — UNLISTED** |
| **N2** | real anchor kept, then a second step `run: \| : make-integrity-guard / echo "MAKEFLAGS=-i" >> "$GITHUB_ENV"`, then `make ci` | **GREEN** | same | **green — UNLISTED** |
| **N3** | earlier step writes `MAKEFLAGS=-i` to `$GITHUB_ENV`; the adjacent "anchor" is `run: ': make-integrity-guard'` | **GREEN** | the real anchor never runs before `make ci` | **green — UNLISTED** |
| **N4** | compound anchor writes a stub dir to `$GITHUB_PATH` | **GREEN** | a stub `make` resolves first for `make ci` | **green — UNLISTED** |
| N5 | compound anchor writes `MAKELEVEL=1` + `MAKEFLAGS=n` | GREEN | as N1 | (same class as N1) |
| N6 | an `id:`-only step between anchor and `make ci` | RED | — | red (adjacency) |
| P1 | `run: 'make ci '` (trailing space) | RED | — | red |
| P2/P3/P5 | `\|-`, `\|`, folded `>` around `make ci` | GREEN | the parsed string is exactly `make ci` (+1 newline) — identical command | correct |
| P4 | `\|+` with two trailing newlines | RED | — | red (only one newline trimmed) |
| P6 | `run: "make ci\n"` | GREEN | identical string | correct |
| P7 | whole file CRLF | GREEN | YAML normalises line breaks; identical string | correct |
| P8 | `run: "make ci\r"` | RED | — | red |
| **P9** | duplicate key: `run: make -i ci` then `run: make ci` | **GREEN** | PyYAML keeps the LAST value; if GitHub's parser kept the first, `make -i ci` would run. UNVERIFIED on a live runner — I believe GitHub rejects duplicate keys (the workflow would then not run and the fan-in would be red), but the guard does not assert that. | see FINDING R-4 |
| P10 | duplicate key, `make ci` first, `make -i ci` last | RED | — | red |
| P11 | Cyrillic `mаke -i ci` as an extra step | GREEN | `mаke: command not found`, the step fails — fails closed at runtime | correct |
| P12/P13 | zero-width joiner / NBSP inside `make ci` | RED | — | red |
| P14 | merge key `<<: {if: …}` on the pinned step | RED | — | red (the merged key is seen) |
| P15 | a second YAML document in the workflow file | RED | — | red |
| P16 | `run: !!str make ci` | GREEN | identical string | correct |
| U1 | local composite `uses: ./.github/actions/x` before the anchor | GREEN | whatever the action does to the machine | green — LISTED ("any OTHER step … `uses:` actions") |
| U2 | composite action replacing the anchor | RED | — | red (adjacency) |
| U3 | SHA-pinned `actions/github-script` exporting MAKEFLAGS before the anchor | GREEN | the anchor refuses MAKEFLAGS at runtime — *unless* MAKELEVEL is also exported (R4) | listed class; defeated by R4 |
| J1 | job-level `if: ${{ false }}` on `build-test` | GREEN | job skipped → `ci-required` treats `skipped` as FAILED (`ci-required.yml:86-92`) | correct (fails closed at fan-in) |
| J2 | job-level `if: ${{ false }}` on `cache-matrix-leg` | GREEN | leg skipped → aggregator's `result != success` exits 1 | correct |
| J3 | the `cache-matrix` aggregator's body replaced by `'true'` | GREEN | legs become non-blocking | outside the stated scope ("make steps and direct test steps … That is the whole claim"); covered by "everything here can be edited". Observation. |
| J4 | job-level `env: MAKELEVEL: '1'` | GREEN | arms R4's fallback | see FINDING R-2 |
| J5 | job-level `continue-on-error: true` on `cache-matrix-leg` | GREEN | check 4 is applied to `cache-matrix`, not to the jobs it `needs` | observation — pre-existing, and the aggregator reads `needs.*.result`; UNVERIFIED what GitHub reports there for a continue-on-error job |

**Why N1–N4 pass:** `step_is_the_anchor()` (`scripts/ci-required-guard.py:284`) is
`MAKE_INTEGRITY_GUARD in run and not MAKE_INVOCATION.search(run)` — a SUBSTRING test. The anchor's
body is **not pinned** (it is not in `.github/pinned-steps.yml`), so any step whose text contains
`make-integrity-guard` and no bare `make` token satisfies "IMMEDIATELY preceded by the anchor",
including one that runs the real guard and then writes `$GITHUB_ENV`, or one that is `: make-integrity-guard`.

## R4. The anchor's runtime checks (the chair's priority question)

`check_environment()` (`scripts/make-integrity-guard.py`, new in `8fa04b1`):

```python
inside_make = os.environ.get("MAKELEVEL") is not None
...
if not inside_make:
    g.fail(... "Out of make these must be unset" ...)      # default-deny
    continue
words = value.split()
cluster = words[0] if words and not words[0].startswith("-") and "=" not in words[0] else ""
hits = sorted(set(cluster) & set("iktq"))
hits += [w for w in words if w in DANGEROUS_FLAG_WORDS or w in ("-i", "-k", "-t", "-q")]
```

**Answer: yes, `MAKELEVEL` set by an earlier `$GITHUB_ENV` write (or a job-level `env:`, which the
static guard allows — J4) switches the workflow anchor to the weaker blacklist, and that blacklist
passes values that neuter make.** Nothing checks that the process really is a child of make: the
variable's mere presence decides, and an EMPTY `MAKELEVEL=` counts.

The real anchor, measured on **GNU Make 4.3 / ubuntu:24.04** (repo mounted read-only) and on the host's 3.81:

```
control                                        anchor exit=0
MAKEFLAGS=-ki (no MAKELEVEL)                   anchor exit=1   FAIL the environment sets MAKEFLAGS='-ki' …
MAKELEVEL=1 MAKEFLAGS=-ki                      anchor exit=0   <- a dash-cluster: only the bare words -i/-k/-t/-q are matched
MAKELEVEL=1 MAKEFLAGS=n                        anchor exit=0   <- 'n' is not in "iktq", and the per-target check
                                                                  treats 'p' and 'n' as the guard's own (-pn)
MAKELEVEL= MAKEFLAGS=--ign                     anchor exit=0   <- EMPTY MAKELEVEL counts; long abbreviation not matched
MAKELEVEL=1 GNUMAKEFLAGS=-ki                   anchor exit=0
MAKELEVEL=1 MAKEFLAGS=e                        anchor exit=0
```

and what GNU Make 4.3 does with each, against a Makefile whose `ci` recipe is `@echo RECIPE RAN; exit 7`:

```
MAKELEVEL=1 MAKEFLAGS=-ki make ci       exit=0
MAKELEVEL=1 MAKEFLAGS=n make ci         exit=0
MAKELEVEL= MAKEFLAGS=--ign make ci      exit=0
MAKELEVEL=1 GNUMAKEFLAGS=-ki make ci    exit=0
```

So A19 — the one row the builder states is green at the static guard and "red at the anchor at
runtime" — is green at BOTH when the `$GITHUB_ENV` write carries two lines instead of one:

```
- run: printf 'MAKELEVEL=1\nMAKEFLAGS=-ki\n' >> "$GITHUB_ENV"     # any earlier step; static guard GREEN
- name: Refuse a neutered Makefile
  run: ./scripts/make-integrity-guard.sh                            # anchor exit 0 (measured above)
- name: make ci
  run: make ci                                                      # pinned, byte-equal; neutered
```

The builder's R2 transcript (`docs/evidence/hardening-b1/R2-anchor-environment.txt`) never tests an
injected MAKELEVEL; its only MAKELEVEL rows are `make ci-guard`, where make sets it legitimately.

### N1 end-to-end, with GitHub's `$GITHUB_ENV` semantics simulated (ubuntu:24.04, Make 4.3)

```
### N1: the anchor step, compound, VERBATIM as a run: body (GHA runs bash -e {0})
  anchor step exit=0  (make-integrity-guard: passed (8 gate target(s)))
  GITHUB_ENV now: MAKEFLAGS=-i
### next step (pinned: make ci) runs with GITHUB_ENV applied, as GitHub does for LATER steps
RECIPE RAN
make: [Makefile:2: ci] Error 7 (ignored)
  make ci step exit=0
```

UNVERIFIED on a live runner: the carry-over of `$GITHUB_ENV` to later steps is GitHub's documented
behaviour and the premise of the builder's own adjacency design; I simulated it, I did not push a workflow.

### `make` identity

- `/usr/local/bin/make -> /bin/true` (a symlink ahead of `/usr/bin`): anchor **RED** — but by accident:
  `make -pn` through `true` yields an empty `MAKEFILE_LIST`. The identity check itself would have passed
  (`realpath` is `/usr/bin/true`, an approved directory).
- A forwarding stub — a real FILE `/usr/local/bin/make` that `exec`s `/usr/bin/make` for `-pn` and
  `exit 0`s otherwise: anchor **exit 0**, printing
  `ok  'make' is a real program at /usr/local/bin/make (type -t: file), not a function, alias or PATH stub`;
  `make ci` exit 0. This requires an earlier step to write to the machine, which AGENTS.md lists
  ("anything at all before the anchor runs"), so it is a listed residual — but the `ok` line's words
  "not … a PATH stub" claim more than the check establishes. See FINDING R-5 (NIT).
- `hash -p` / functions / aliases cannot cross a step boundary; `BASH_ENV`/`ENV` are refused in both modes
  (they are NOT behind the MAKELEVEL switch). Correct.

### The anchor-accepted environment on the REAL repository (host, GNU Make 3.81)

A planted gofmt violation (`internal/site/zz_vzv_fmt.go`), then reverted (`git diff --quiet` clean):

```
control (clean env)             make fmt-check exit=2
MAKELEVEL=1 MAKEFLAGS=-ki       make fmt-check exit=0
MAKELEVEL= MAKEFLAGS=--ign      make fmt-check exit=0
MAKELEVEL=1 MAKEFLAGS=e         make fmt-check exit=2    (not neutering here — harmless for this target)
MAKELEVEL=1 MAKEFLAGS=n         make ci        exit=0    (the WHOLE gate, dry-run)
```

(A full `make ci` with a planted failing test under each env was started first; on a host loaded by other
agents' test runs it had not finished after ~10 minutes, so I stopped my own processes by exact PID —
verified by `lsof` cwd inside my scratch clone — and used the faster gate above. Not a pass for anything.)

## R5. Round-one findings 5–8

| round-one finding | status at 6b65eff | evidence (mine) |
|---|---|---|
| **5 — D6 not reproducible** | **CLOSED.** D6 now says main's step exits **125** against `broken` and adds `fakedocker/broken-probes-1-3` | extracted main's step from `5eb2829` with a YAML parser: `broken` → **125**, `broken-probes-1-3` → **0**; new script **1** on both |
| **6 — report line deletable (regression)** | **CLOSED.** Direct bodies are pinned; each ends `\|\| exit 1` on the report and `exit "$rc"` last | my harness: report call deleted → RED; `exit "$rc"` deleted → RED; `\|\| exit 1` removed → RED; `if: always()` added → RED |
| **7 — only one package floored** | **CLOSED.** 14 unit + 15 integration package floors; an unfloored package that ran tests is refused | real `go test -json` runs: emptying `internal/obs` → **1054 ≥ 910 but RED** (`internal/obs executed 0 test(s); its recorded floor is 14`); deleting `internal/healthcheck` → RED (build failure in `cmd/vizra` + floor); a NEW package with one test → RED (`no recorded floor`); a rename (stream-level) → RED on both counts; a NEW package with **zero** tests → green (nothing to lose; consistent with the doc's wording "a package that **runs** with no recorded floor is refused") |
| **8 — stale `_why` counts** | **CLOSED** — `_why` reads 1071 / 1116 / 45 | matches my runs and CI |

Incidentally measured: when something outside my run SIGTERM'd a background `go test`, the report
failed it correctly — "`go test` exited 143 but no test or package event reports a failure … It is not a
pass." Fail-closed on a signal.

## R6. Lanes from the clean clone, and CI on 6b65eff

Local, verbatim bodies extracted from `.github/pinned-steps.yml`, on my own `vzv9r1-pg` (PostgreSQL 18,
:55919) and `vzv9r1-cache` (Valkey 9.1.2, :63919):

```
direct step 0 (unit)                 EXIT=0   1071 executed (floor 910), skipped 0, 14 packages
direct step 1 (integration)          EXIT=0   1116 executed (floor 949), skipped 0; internal/integration 45 (floor 40)
direct step 2 (integration shuffled) EXIT=0   1116 executed (floor 949), skipped 0; internal/integration 45 (floor 40)
```

Zero skips is **measured** from the `-json` stream in all three.

CI on `6b65eff` (runs 35805827409 build-test, 35805827266 ci-required, 35805827280 image-scan):

| check | conclusion | note |
|---|---|---|
| `ci-required` | **success** | `ci-required-guard: passed (6 required check(s))`; fan-in prints `SUCCESS` for all six manifest names |
| `append-only`, `build-test`, `cache-matrix` (+ both legs), `fixtures`, `govulncheck`, `docker-build` | **success** | all six FLOOR_LANES ran on this SHA; manifest and jobs agree; nothing skipped/cancelled |
| `image-scan` | failure | **not required**; `48 finding(s) at or above ['CRITICAL','HIGH']`, **exit 1** (findings), not 3 |

build-test log: unit **1071**/910, integration **1116**/949 twice, `internal/integration` **45**/40,
`skipped: 0` in each; every anchor prints both new runtime `ok` lines; provenance names the tested merge
tree `fa15bca…` with `HEAD^2 == 6b65eff…`. Duration **01:19:42 → 01:30:59 = 11m17s** of a 20-minute
timeout (claimed 11m17s ✔; +14s over round one).

## R7. Truthfulness at 6b65eff

| claim | verdict |
|---|---|
| "EXHAUSTIVE" / "the whole remaining residual" deleted everywhere | **TRUE** — the only remaining uses say a blacklist *cannot* be exhaustive, or that the list is *not* called exhaustive |
| no change under api/, internal/, cmd/, migrations/, Makefile; manifest and FLOOR_LANES identical | **TRUE** |
| 65 guard fixtures; counts 1071 / 1116 / 45; 0 skips; build-test 11m17s | **TRUE** — all reproduced |
| "45 attack rows, all RED, each by a named rule" | **TRUE of those 45 rows** (R2), except that A19/A19b are only red when the writing step is a *separate* step — see next row |
| PR body: "A19 / A19b `$GITHUB_ENV` / `$GITHUB_PATH` write by the preceding step → RED — 8b adjacency (and the anchor at runtime)" | **FALSE when the preceding step is the anchor or looks like it** — FINDING R-1 |
| PR body/R2: "R3 … an arbitrary early step writing MAKEFLAGS to `$GITHUB_ENV` … RED at the anchor at runtime" | **FALSE when that step also writes MAKELEVEL** — FINDING R-2 |
| AGENTS.md:59 "MAKEFLAGS/GNUMAKEFLAGS/MFLAGS are unset (not merely free of flags it recognises)" | **FALSE under an injected MAKELEVEL**, which AGENTS.md never mentions — FINDING R-3 |
| AGENTS.md:70 / guard docstring:96 "Every one of the thirteen fails this by construction" (the thirteen include the `$GITHUB_ENV`/`$GITHUB_PATH` write) | **FALSE** — the builder's own counter-row R3 is green at 8b — FINDING R-3 |
| `check_environment` docstring: "the flag test still refuses -i/-k/-t/-q, and the workflow anchor … never runs under make" | **FALSE** — `-ki` passes; "under make" is an env var — FINDING R-2 |
| D6 corrected | **TRUE** |
| review-only residuals (another step's effect on the machine; wrapper/composite; reusable workflow; committed pins/floors editable; CODEOWNERS advisory) | **TRUE and honestly stated** — U1, U3 (absent MAKELEVEL), J3, the forwarding `make` stub all fall inside them |

## Findings at 6b65eff

```
FINDING R-1: the "anchor immediately before make" is recognised by SUBSTRING and its
             body is not pinned — the anchor step itself can poison the pinned make step
Severity:    REQUIRED
Confidence:  high (static guard: measured; GitHub $GITHUB_ENV carry-over: simulated, not run live)

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py:284 (step_is_the_anchor),
             :575-603 (the adjacency test in check_pinned_make_steps),
             .github/pinned-steps.yml (no entry for the anchor body),
             AGENTS.md:55-64, PR body § anchor and the A19/A19b row
  requirements: none yet — propose VZ-OPS-CI-00x (a floor lane's make step cannot be no-opped)

Observed:
      def step_is_the_anchor(step):
          run = step.get("run")
          return isinstance(run, str) and MAKE_INTEGRITY_GUARD in run and not MAKE_INVOCATION.search(run)
  "The anchor" is any step whose text CONTAINS `make-integrity-guard` and no bare
  `make` token. Its body is never compared to anything. Each of these, substituted
  into the real build-test.yml, leaves ci-required-guard.py GREEN, exit 0:
    N1  - name: Refuse a neutered Makefile
          run: ./scripts/make-integrity-guard.sh && echo "MAKEFLAGS=-i" >> "$GITHUB_ENV"
        - name: make ci
          run: make ci
    N2  real anchor, then a second step `: make-integrity-guard` + the same write, then make ci
    N3  an earlier step writes MAKEFLAGS=-i; the adjacent "anchor" is `run: ': make-integrity-guard'`
    N4  the compound anchor writes a stub directory to $GITHUB_PATH
  N1 end-to-end on ubuntu:24.04 / GNU Make 4.3, the anchor body run as `bash -e`,
  then the next step run with the $GITHUB_ENV file applied (GitHub's documented
  semantics for LATER steps):
      anchor step exit=0  (make-integrity-guard: passed (8 gate target(s)))
      GITHUB_ENV now: MAKEFLAGS=-i
      RECIPE RAN
      make: [Makefile:2: ci] Error 7 (ignored)
      make ci step exit=0

Failure:
  The redesign's stated premise — "Adjacency is what gives this teeth: a write to
  $GITHUB_ENV or $GITHUB_PATH only applies to later steps, so it reaches the anchor's
  process exactly as it would reach make's" — holds only if the adjacent step IS the
  anchor. A write made BY that step, after the guard exits, reaches make and not the
  guard. One edited line on the anchor, or a fake anchor, silences every pinned make
  step with both guards green. The AGENTS.md residual ("what any OTHER step does …
  before the anchor runs") does not cover the anchor step itself or a step that only
  looks like one.

Perspective:
  developer, operator

Recommendation:
  Pin the anchor exactly like the make steps: add `./scripts/make-integrity-guard.sh`
  as an `anchor_step` literal in .github/pinned-steps.yml and make step_is_the_anchor
  mean "byte-equal to that literal, keys ⊆ {name, run, id}". A step that merely
  contains the string is then neither an anchor nor exempt from 8b.

Acceptance criteria:
  N1, N2, N3 and N4 each turn ci-required-guard.py red with a named reason; the
  committed workflows (whose anchors are all exactly `./scripts/make-integrity-guard.sh`)
  still pass.

Tests:
  scripts/scripts_test.go TestCIRequiredGuardFixtures — fixtures anchor-compound-github-env/,
  anchor-fake-noop/, anchor-then-lookalike/, anchor-compound-github-path/, each one
  change from `good`.

Cross-repo implications:
  core: this guard. user/search: if the pinned-step design is ported, pin the anchor
  there from the start. meta: none.

Challenge:
  `&& echo … >> $GITHUB_ENV` on the anchor is conspicuous in a diff. So was
  `make -i ci`; the whole slice exists because conspicuous is not a control.
```

```
FINDING R-2: MAKELEVEL in the environment switches the workflow anchor to a flag
             blacklist, and that blacklist passes `-ki`, `n` and `--ign`
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/make-integrity-guard.py:574-650 check_environment() (`inside_make = …` at :593
             and the fallback `hits` at :611); :284-306 (per-target MAKEFLAGS check treats p/n as its own);
             scripts/ci-required-guard.py DANGEROUS_ENV_NAMES (MAKELEVEL absent)
  requirements: none yet

Observed:
  The mode is chosen by the PRESENCE of MAKELEVEL, which any earlier step can set
  through $GITHUB_ENV and a job-level `env:` can set outright (the static guard
  passes `env: MAKELEVEL: '1'` — row J4). An EMPTY MAKELEVEL counts. In that mode the
  test is: a leading dash-less word's letters ∩ {i,k,t,q}, or a whole word equal to
  -i/-k/-t/-q or one of nine long spellings. So a dash CLUSTER (`-ki`), `n`, and a long
  ABBREVIATION (`--ign`) pass; `n` is also invisible to the per-target check, which
  treats `p` and `n` as the guard's own `-pn`.
  The real anchor, GNU Make 4.3 on ubuntu:24.04 (repo mounted read-only):
      MAKEFLAGS=-ki (no MAKELEVEL)       anchor exit=1
      MAKELEVEL=1 MAKEFLAGS=-ki          anchor exit=0
      MAKELEVEL=1 MAKEFLAGS=n            anchor exit=0
      MAKELEVEL= MAKEFLAGS=--ign         anchor exit=0
      MAKELEVEL=1 GNUMAKEFLAGS=-ki       anchor exit=0
  and what make does under each, with a failing `ci` recipe: exit 0, 0, 0, 0.
  On the real repository (host, planted gofmt violation):
      control                            make fmt-check exit=2
      MAKELEVEL=1 MAKEFLAGS=-ki          make fmt-check exit=0
      MAKELEVEL= MAKEFLAGS=--ign         make fmt-check exit=0
      MAKELEVEL=1 MAKEFLAGS=n            make ci        exit=0   (the whole gate)
  The builder's R2 transcript never injects MAKELEVEL; its only MAKELEVEL rows are
  `make ci-guard`, where make sets it legitimately.

Failure:
  Row R3/A19 — "an arbitrary early step writing MAKEFLAGS to $GITHUB_ENV: green at the
  guard; RED at the anchor at runtime" — is green at both when that step writes two
  lines, `MAKELEVEL=1` and `MAKEFLAGS=-ki`. The pinned, byte-equal `make ci` then runs
  with -k -i and exits 0. The function's own docstring says "That path is not a hole:
  the flag test still refuses -i/-k/-t/-q, and the workflow anchor … never runs under
  make" — `-ki` is refused by neither half, and "never runs under make" is decided by
  an environment variable the attacker controls.

Perspective:
  developer, operator

Recommendation:
  Choose strict mode from something the workflow controls and the environment cannot:
  the workflow anchor is already about to be pinned byte-equal (FINDING R-1), so pin it
  as `./scripts/make-integrity-guard.sh --workflow` and in that mode refuse any
  non-empty MAKEFLAGS/GNUMAKEFLAGS/MFLAGS AND any MAKELEVEL, unconditionally. Keep the
  lenient path only for the `make ci-guard` recipe (which is not a control anyway).
  Belt and braces: add MAKELEVEL to DANGEROUS_ENV_NAMES, and make the lenient path an
  ALLOWLIST (empty, `-j…`, `--jobserver-…`, `--no-print-directory`, `w`, `s`) rather
  than a letter blacklist.

Acceptance criteria:
  The anchor, invoked as the workflow invokes it, exits 1 for every row above including
  MAKELEVEL=1 MAKEFLAGS=-ki, MAKELEVEL=1 MAKEFLAGS=n and an empty MAKELEVEL; `make
  ci-guard` locally still passes; `env: MAKELEVEL:` at job or workflow level is red.

Tests:
  scripts/scripts_test.go — a TestMakeIntegrityGuardEnvironment table driving the
  script with each env row (no workflow needed), plus a guard fixture job-env-makelevel/.

Cross-repo implications:
  core only today; vizra-search carries the anchor's lineage.

Challenge:
  Someone who can write $GITHUB_ENV in a floor lane can do anything (the stated
  "machine" residual). True for effects the anchor does not claim to see — but MAKEFLAGS
  in the anchor's own environment is precisely what it claims to see, "unset, not merely
  free of flags it recognises", and it is the sole runtime defence the PR body cites for
  the R3 row.
```

```
FINDING R-3: the docs and PR body state the anchor and adjacency controls at a strength
             they do not have
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md:55-72 (controls 1 and 2; :59 and :70 quoted), scripts/ci-required-guard.py:96 docstring
             ("8b … Every one of the thirteen fails this by construction"),
             scripts/make-integrity-guard.py check_environment docstring,
             PR body (anchor row; the A19/A19b row; the R3 row)

Observed:
  - AGENTS.md control 1: "MAKEFLAGS/GNUMAKEFLAGS/MFLAGS are unset (not merely free of
    flags it recognises)". The MAKELEVEL fallback is not mentioned anywhere in AGENTS.md;
    under it they are merely free of flags it recognises, and it does not recognise -ki.
  - AGENTS.md and the ci-required-guard docstring both list "a `$GITHUB_ENV` or
    `$GITHUB_PATH` write by an earlier step" among the thirteen, then say "Every one of
    the thirteen fails this by construction, because every one changes the bytes or adds
    a key." That write changes neither; the builder's own table lists it as GREEN at the
    static guard (counter-row R3).
  - PR body: "A19 / A19b | `$GITHUB_ENV` / `$GITHUB_PATH` write by the preceding step |
    RED — 8b adjacency (and the anchor at runtime)" — green when the preceding step is
    the anchor itself or a look-alike (R-1); "R3 … RED at the anchor at runtime" — green
    with MAKELEVEL (R-2).
  - check_environment docstring: "the flag test still refuses -i/-k/-t/-q, and the
    workflow anchor … never runs under make" — both measured false.

Failure:
  The chair's standing rule: text stronger than its control holds the PR. These are the
  sentences a reviewer reads to decide that the $GITHUB_ENV class is closed.

Perspective:
  developer

Recommendation:
  Fix R-1 and R-2, after which most sentences become true. Independently: drop "every
  one of the thirteen" (say which ones 8b catches and which the anchor catches at
  runtime), and state the MAKELEVEL behaviour — whatever it becomes — in AGENTS.md.

Acceptance criteria:
  Each sentence above names the control that makes it true, and a fixture or transcript
  exists for it.

Tests:
  review; the fixtures of R-1 and R-2.

Cross-repo implications:
  meta: the war-room board quotes AGENTS.md.

Challenge:
  "Adjacency" is true of every real anchor in the committed workflows. Yes; the claim is
  about what the guard enforces, and it enforces a substring.
```

```
FINDING R-4: duplicate YAML keys are resolved last-wins by the guard, silently
Severity:    SHOULD
Confidence:  medium (the guard's behaviour is measured; GitHub's is UNVERIFIED)

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.py load_workflows() (yaml.safe_load)

Observed:
  A make step with `run: make -i ci` followed by `run: make ci` (same mapping) is GREEN:
  PyYAML keeps the last value. The reverse order is RED. I did not push a workflow to
  learn which value GitHub's parser uses; I believe it rejects the file ("'run' is
  already defined"), in which case no job runs and the fan-in is red — but the guard
  neither knows nor asserts that.

Failure:
  If GitHub's parser keeps the FIRST value, `make -i ci` runs under a green guard.
  Either way the guard's verdict rests on a parser disagreement nobody has measured.

Perspective:
  developer

Recommendation:
  Load workflows and pinned-steps.yml with a SafeLoader subclass whose construct_mapping
  raises on a duplicate key; report it as a FAILURE. Ten lines.

Acceptance criteria:
  A fixture with a duplicate `run:` (either order) is red, naming the key.

Tests:
  scripts/scripts_test.go, fixture duplicate-run-key/.

Cross-repo implications:
  none.

Challenge:
  GitHub almost certainly rejects duplicates, so this can never fire. Then the loader
  change costs nothing and removes the "almost".
```

```
FINDING R-5: the anchor's `make` identity `ok` line says "not … a PATH stub" but checks
             only the directory
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/make-integrity-guard.py:656 check_make_resolves_to_a_real_program()

Observed:
  A real file at /usr/local/bin/make that execs /usr/bin/make for `-pn` and `exit 0`s
  otherwise: anchor exit 0, printing "`make` is a real program at /usr/local/bin/make
  (type -t: file), not a function, alias or PATH stub"; `make ci` then exits 0. (A
  symlink to /bin/true IS red — but only because `make -pn` returns an empty
  MAKEFILE_LIST, not because of this check; realpath /usr/bin/true is in an approved dir.)
  Planting it needs an earlier step writing to the machine, which AGENTS.md lists as
  review-only — so this is a wording defect, not an unlisted hole.

Recommendation:
  Say what is checked: "`make` resolves to a file in a system directory". Optionally
  compare `make --version`'s first line to `GNU Make` and require realpath basename
  `make`/`gmake`.

Acceptance criteria / Tests:
  The ok line states only what the check establishes.

Cross-repo implications:  none.
Challenge:  cosmetic. It is the line a reader takes as proof.
```

## Cross-PR note for the chair (reported, not acted on) — core PR #8 at `59a19c5`, whichever merges second

1. **#8 adds three new tested packages** — `internal/audit`, `internal/credential`, `internal/ownerclaim`
   (none exists on main or on #9). #9's report now REFUSES any package that runs tests with no recorded
   floor (measured: FL3). So **the first `build-test` run after both land goes red** on all three direct
   steps — `N package(s) executed tests with no recorded floor` — until floors for those three are added
   to BOTH suites in `scripts/test-floors.json` (the `--emit-floors` generator prints them). Intended
   behaviour, but it must be done in the second PR, not discovered on main.
2. **#8's Makefile edit** renames one `-run` alternative in `openapi-verify`
   (`TestM0ContractIsTheFourProbes` → `TestPublicContractIsTheProbesPlusTheSetupOperations`). It does not
   touch any step pinned in `.github/pinned-steps.yml` (those are `make <target>` bodies; the recipe body is
   free), and check 5's "every -run selection is non-empty" still holds. No pin or floor conflict from it.
   `make-integrity-guard` would only object if the merge duplicated a gate target.
3. **#8 raises counts** (new tests in `internal/httpapi`, `internal/config`, `cmd/vizra`,
   `internal/integration`), so no existing floor can trip; per-package floors do not need raising, only
   ADDING for the three new packages.
4. **Skips:** `allowed_skips` is empty in both suites; any `t.Skip` among #8's tests fails the lane by name.
5. **If #8 changes any workflow step** (e.g. new `env:` on a test step), the job-level-env and pinned-body
   rules apply: a step-level `env:` on a pinned step is now refused (name/run/id only).

## Cleanup (round two)

`vzv9r1-pg`, `vzv9r1-cache` removed by exact name; `ubuntu:24.04` (pulled by me this round — absent at
start) removed by exact name; `vzv9r1-make43` ran with `--rm`. My four stopped processes were mine by
`lsof` cwd. Scratch clone deleted. Nothing belonging to `vzv10-*`, `vizra-m1a-*` or `vidra-*` touched;
the builder's checkout and the core-#8 worktree were never opened for writing.

## Verdict at 6b65eff

The redesign is real progress and most of it holds: all 45 round-one rows are red with my harness,
round-one findings 5–8 are closed and reproduced, the lanes and counts reproduce locally and in CI, and
the "exhaustive" language is gone. It fails on the control the redesign itself depends on: the
**anchor** that must sit "immediately before" each pinned make step is recognised by substring and its
body is unpinned (R-1), and its runtime default-deny collapses to a leaky blacklist whenever `MAKELEVEL`
is present in the environment, which an earlier step or a job-level `env:` can arrange (R-2). Either
alone lets a byte-pinned `make ci` run neutered with both guards green; the docs and PR body claim both
paths are closed (R-3). Fixes are small (pin the anchor body; choose strict mode by argv, not env; refuse
MAKELEVEL at job/workflow level) — this is round 1 of 2.

FINAL VERDICT: FAIL — SHA 6b65eff6ee29e99e1b93b01242b4c97d90a57267

---
---

# Re-verification at e2a3e01 — 2026-09-23

- **Head verified:** `e2a3e0177bdcda4ddb16b4b53cadafa69bb21ef4` (fix round 2 of 2, the last). On top of `6b65eff`:
  `fc4885b` (code), `d435cd8` (evidence), `e2a3e01` (counts/floors from CI). `6b65eff` is an ancestor, so
  there was no force-push. `git ls-remote` showed `e2a3e01…` at the start.
- **Clone:** fresh `mktemp -d …/scratchpad/vzv-core-pr9r2-XXXXXX`. None of my earlier containers existed.
  Others present and left alone: `m1close-*` (the core-#8 closing builder), `vidra-ipfs-071-*`. My services:
  `vzv9r2-pg` (PostgreSQL 18, :55929) and `vzv9r2-cache` (Valkey 9.1.2, :63929). GNU Make 4.3 ran in a throwaway
  `ubuntu:24.04` container, `vzv9r2-make43`, started with `--rm`.
- **Host condition:** the shared host was saturated by other agents' runs, with **load average 279–442**
  (`uptime`). One heavy test process belonged to the `m1close` builder (cwd in the core-#8 worktree);
  I did not touch it. This affected only my local `-race` timing; see R2-4.
- **Harness:** my own `h.py`, rewritten fresh, with the round-one/round-two rows. The builder's `evasion-table.py`
  was not used. Control (a comment-only edit) is **GREEN**.

## R2-1. Frozen paths and baseline

```
git diff --stat 5eb2829..e2a3e01 -- migrations/ api/ internal/ cmd/ sqlcgen/ Makefile .github/required-checks.txt   (empty)
./scripts/make-integrity-guard.sh --workflow   exit 0   passed (8 gate target(s))
./scripts/ci-required-guard.sh                 exit 0   passed (6 required check(s))
go test -race -count=1 ./scripts/              exit 0   ok … 47.648s
scripts/testdata/guard                         75 fixture dirs (claimed 75 ✔)
anchors in workflows, byte-equal to the pin    8 (build-test.yml 5, fixtures.yml 2, govulncheck.yml 1)
```

## R2-2. My earlier rows, re-run with my own harness

| rows | result |
|---|---|
| 44 round-one rows (B1–B10, A1–A34, the key rows, the merge-key row) | **44/44 RED** |
| A19: a separate *earlier* step writes MAKEFLAGS to `$GITHUB_ENV` | GREEN at the static guard, as stated; **RED at the runtime anchor** (R2-3) |
| **N1** compound anchor `… --workflow && echo "MAKEFLAGS=-i" >> "$GITHUB_ENV"` | **RED**: `make step 'make ci' is not IMMEDIATELY preceded by the make-integrity-guard …` |
| **N2** real anchor, then a look-alike step that writes | **RED** (same rule) |
| **N3** earlier write, then a fake `': make-integrity-guard'` | **RED** (same rule) |
| **N4** compound anchor writing `$GITHUB_PATH` | **RED** (same rule) |
| J4 job-level `env: MAKELEVEL: '1'` | **RED**: `job-level env sets MAKELEVEL: '1', and this job invokes make` |
| R-4 duplicate `run:` key (`make -i ci` then `make ci`) | **RED**: the loader refuses the file |

**Round-two FINDINGS R-1 and R-4 are closed statically.**

## R2-3. The runtime anchor (round-two FINDING R-2)

`./scripts/make-integrity-guard.py --workflow` measured on **GNU Make 4.3 / ubuntu:24.04** (repo mounted
read-only) and on the host's **3.81**. Both produced identical verdicts:

```
control (clean)                     exit=0
MAKELEVEL=1 MAKEFLAGS=-ki           exit=1   FAIL  the environment has MAKELEVEL='1', and this is the WORKFLOW anchor.
MAKELEVEL=1 MAKEFLAGS=n             exit=1   (same)
MAKELEVEL= MAKEFLAGS=--ign          exit=1   FAIL  the environment has MAKELEVEL='', …
MAKELEVEL=1 GNUMAKEFLAGS=-ki        exit=1
MAKEFLAGS= (empty but set)          exit=1   FAIL  the environment sets MAKEFLAGS='', …
MAKELEVEL=1 alone                   exit=1
GO=true                             exit=1   FAIL  the environment sets GO='true', …
GOFLAGS=-run=^$                     exit=1
MAKEFILES=/tmp/x.mk                 exit=1
```

**All four of my MAKELEVEL spellings are now red, and so is the builder's own `?=` finding (`GO=true`).
FINDING R-2 is closed.** The strict mode is selected by the pinned argv `--workflow`. The environment has
no influence on it.

## R2-4. Attacking the new surface

**The anchor pin** (each substituted for the anchor immediately before `make ci`):

| # | variant | guard |
|---|---|---|
| AP1 | `run: ./scripts/make-integrity-guard.sh --workflow # ok` | GREEN — correct: YAML treats ` #` in a plain scalar as a comment, so the parsed string (and what GitHub runs) is byte-equal to the pin |
| AP2 | `--workflow --workflow` | RED |
| AP3 | `--workflow=` | RED |
| AP4 | extra argument `--root .` | RED |
| AP5 | reordered `--targets ci --workflow` | RED |
| AP6 | env prefix `FOO=1 ./scripts/…` | RED |
| AP7 | no `--workflow` | RED |
| AP8 | `python3 scripts/make-integrity-guard.py --workflow` | RED |
| AP9 | `\|` block scalar | GREEN — correct: identical string |
| AP10 | anchor with an `env:` key | RED (`carries ['env']`) |

**Mode selection:** argv is the pinned text. Aliases and functions cannot cross a step boundary.
`BASH_ENV`/`ENV` are refused in both modes, and the step's keys are limited to name/run/id, so no `shell:` or `env:` is possible.
**The argument-less allowlist mode is not reachable from a floor lane.** `make ci-guard` is not a
pinned body (the pins are tidy-check, ci, build, test-integration, test-integration-shuffle, fixtures,
fixtures-verify, govulncheck), and an anchored `make ci-guard` step is RED (CG1). A non-anchor step that
merely mentions `make-integrity-guard` is RED anywhere in the lane (CG2).

**Duplicate-key loader vs anchors, aliases and merge keys:**

- DK1, reusing an identical anchor step through `*alias`: GREEN. Correct; it is legitimate content.
- DK2, a merge key overridden with the same `run:` value: RED. This fails closed on a construct nobody uses.
- DK3, a merge key overridden with `make -i ci`: RED.
- DK4, a duplicate `name:`: RED.

**`?=` / environment-read discovery.** The strict anchor lists what it refuses in its own log:
`['BUILT_AT', 'COMMIT', 'GO', 'GOFLAGS', 'RELEASE', 'SQLC']`. `:=`, `=` and `override` assignments are not
overridable by the environment without `make -e`, which the make-step pin already excludes. `export` does
not let the environment win. Variables that the **go command** (not make) reads were measured, and the
anchor passes them all:

```
GOTOOLCHAIN=local  GOENV=<file>  GOROOT  GOPATH  CGO_ENABLED=0  GOCACHE  GOPROXY=off  GODEBUG  GOEXPERIMENT   -> anchor exit=0
```

AGENTS.md:144-148 states this: "**The anchor checks a named set of variables, not the whole
environment.** A `$GITHUB_ENV` write by an earlier step of any variable NOT in the list above
(`GOTOOLCHAIN`, `GODEBUG`, `CGO_ENABLED`, …) is not refused. The per-package floors in the direct test
steps still turn a suite that was made to run nothing red; anything subtler is review-only." A
`go env -w` / `GOENV` **file** is a change to the machine, which falls under the first bullet. I measured the
stated backstop directly: with `GOFLAGS=-run=^$` supplied through a `GOENV` file, not the environment, the
anchor exits 0 (as stated), `go test ./...` exits 0 having run nothing, and the report goes **RED**:
`tests executed: 0 (floor: 943)`, `FAILED (15 problem(s))`. **The residual is accurately stated and its
backstop works.**

**Floor arithmetic.** The formula is in code (`go-test-report.py:205-211`: 15% headroom, at least 2 tests
of slack, never below 1) and in `test-floors.json`'s `_why`. The new floors (unit 943, integration 981;
per package, for example authz 427 of 502, scripts 161, obs 14, fixtures 36, internal/integration 40)
still leave each per-package floor meaningful. Emptying `internal/obs` in my own unit event stream
leaves 1092 executed (above the suite floor of 943) and is **RED** by its package floor of 14.

## R2-5. Regression, and counts from my own runs

| check | result |
|---|---|
| FINDING 6 (direct-step exit) | report call deleted → RED; `\|\| exit 1` removed → RED; `exit "$rc"` deleted → RED |
| D6 | main's step: `broken` → 125, `broken-probes-1-3` → 0; the new script exits 1 on both |
| FINDING 7 (per-package floors) | `internal/obs` emptied → RED (above) |
| round-one rows | 44/44 RED (R2-2) |

**Counts, on my own services:**

- Unit (`go test -count=1 -json ./...` + report): **1109 executed, 0 skipped, 14 packages, report exit 0**. This matches CI.
- Integration (`go test -count=1 -tags=integration -json ./...` + report): **1154 executed, 0 skipped, 15
  packages; `internal/integration` 45 (floor 40); report exit 0**. This matches CI.

Zero skips was **measured** from the `-json` stream both times.

**Local `-race` limit:** my verbatim run of the pinned unit body (`-race`) failed. The only problem was
`internal/fixtures`, which hit Go's default 10-minute test timeout (`FAIL … internal/fixtures 604.929s`,
12 of its tests run). Re-running that package alone under `-race` hit the same 604 s timeout. The host load
average was 279–442 at the time, driven by other agents' runs. The same package passes under `-race` in CI on
this SHA inside build-test's 11m13s, and it passes locally without `-race` at the full count. I record the
local `-race` runs as **UNVERIFIED on this host (resource-starved), corroborated by CI**. They are not a pass
of mine. The report handled the timeout correctly: it named the package as `FAILED with no failing test`
and flagged it as below its floor.

## R2-6. CI on e2a3e01

| check | conclusion |
|---|---|
| `ci-required` | **success**: `ci-required-guard: passed (6 required check(s))`; the fan-in prints `SUCCESS` for all six manifest names |
| `append-only`, `build-test`, `cache-matrix` (+ both legs), `fixtures`, `govulncheck`, `docker-build` | **success**. All six FLOOR_LANES ran on this SHA and the manifest matches the jobs; none was skipped or cancelled |
| `image-scan` | failure, **not required**: `48 finding(s) at or above ['CRITICAL','HIGH']`, **exit 1** (findings), not 3 |

The build-test log (run 35815363655) shows:

- unit **1109**/943, integration **1154**/981 (plain and shuffled), `internal/integration` **45**/40, and `skipped: 0` in each;
- all 7 anchor runs print `[--workflow (strict)]` and `none of the 6 variable(s) the makefiles take from the environment is set`;
- provenance names the tested merge tree `f70b5b4…` with `HEAD^2 == e2a3e01…`;
- a duration of **03:42:07 → 03:53:20 = 11m13s** of the 20-minute timeout (claimed 11m13s ✔).

## R2-7. Truthfulness at e2a3e01

| claim | verdict |
|---|---|
| anchor pinned byte-equal; look-alikes refused anywhere in a floor lane | **TRUE** (N1–N4, AP2–AP10, CG2) |
| strict mode chosen by `--workflow`, never by the environment; MAKEFLAGS family unset, MAKELEVEL/MAKE_RESTARTS/MAKEOVERRIDES/MAKECMDGOALS absent | **TRUE**, measured on Make 4.3 and 3.81 |
| `?=` / referenced-but-unassigned variables refused in strict mode (GO, SQLC, GOFLAGS, RELEASE, COMMIT, BUILT_AT) and as job/workflow env | **TRUE** (`GO=true` and `GOFLAGS` red at runtime; the anchor's log lists all six) |
| duplicate keys refused | **TRUE** |
| make must be a file named make in a system directory; the log line does not claim to inspect content | **TRUE** — the ok line now reads "This does not inspect the program's CONTENT" |
| "Eleven of the thirteen … refused statically; `$GITHUB_ENV`/`$GITHUB_PATH` refused statically when the writer sits between the anchor and make or IS the anchor" | **TRUE** (N1–N4, A19) |
| AGENTS.md:98-101: an EARLIER step's write is refused at runtime if it "puts a directory other than a system one first on PATH" | **OVERSTATED**: an empty non-system directory prepended to PATH gives anchor **exit 0**. The anchor refuses a `make` that *resolves* outside a system directory; it does not check PATH order. See FINDING R2-1 |
| residual list: "a named set of variables, not the whole environment (GOTOOLCHAIN, GODEBUG, CGO_ENABLED, …)", "what make IS, not what it DOES", other steps' effects on the machine are review-only | **ACCURATE**. Every green I found falls inside one of these bullets |
| no "exhaustive" claim; "by construction" replaced by the 11 + 2 split | **TRUE**: the remaining uses say a blacklist *cannot* be exhaustive, or that the list is *not* called exhaustive |
| counts 1109 / 1154 / 45, 0 skips; floors 943 / 981; 75 fixtures; 11m13s | **TRUE**, reproduced |
| PR body correction paragraph ("unchanged 1071/1116 … was false") | **TRUE and accurate** |
| no change under api/, internal/, cmd/, migrations/, Makefile, required-checks.txt; FLOOR_LANES unchanged | **TRUE** |

## Finding at e2a3e01

```
FINDING R2-1: one AGENTS.md clause says the anchor refuses a non-system PATH directory; it refuses only a
              non-system `make`
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md:98-101
  requirements: none

Observed:
  AGENTS.md:98-101: "When the writer is an EARLIER step they are refused at RUNTIME, by the anchor —
  provided the write is to a variable the anchor checks (the list above), or puts a directory other than
  a system one first on PATH."
  Measured: `env PATH="<empty scratch dir>:$PATH" python3 scripts/make-integrity-guard.py --workflow`
  -> exit 0. check_make_resolves_to_a_real_program() refuses only when `make` itself resolves outside
  the approved directories. It does not look at PATH order. The clause does not appear in the PR body,
  the guard docstrings or pinned-steps.yml.

Failure:
  A reader concludes that any $GITHUB_PATH write is refused at runtime. It is refused only when the
  prepended directory provides `make`. A directory providing a different `go` or `python3` passes.
  That is the "another step changes the machine" boundary, which the same section's first bullet states
  correctly, so this is a wording defect, not an unlisted hole.

Perspective:
  developer

Recommendation:
  Reword to "…or makes `make` resolve to a file outside the approved system directories", or add a PATH-
  order check to the strict anchor.

Acceptance criteria:
  The clause states what the anchor checks. Or, if a PATH-order check is added, the empty-directory row
  goes red with a named reason and has a table case in TestMakeIntegrityGuardEnvironment.

Tests:
  review, or one TestMakeIntegrityGuardEnvironment row if the check is added.

Cross-repo implications:
  none.

Challenge:
  "It's one clause and the bullet below states the boundary." True. That is why this is SHOULD and not
  REQUIRED. It is still text stronger than its control.
```

No other finding. Round-two FINDINGS R-1, R-2, R-3, R-4 and R-5 are closed and reproduced by me.

## Cross-PR note for the chair (reported, not acted on). Core PR #8 at `655f46a` (the head is moving)

1. **Floors for three new packages.** #8 adds tested packages `internal/audit`, `internal/credential`
   and `internal/ownerclaim`. #9 refuses any package that runs tests without a recorded floor, in either suite.
   Whichever PR merges second must add floors for all three, in **both** suites of `scripts/test-floors.json`
   (`--emit-floors`), or all three direct steps go red.
2. **Anchor text: no conflict today.** #8 does not touch `.github/` (its file list has no workflow),
   so the 8 pinned `--workflow` anchors are unaffected. If #8 later adds or edits a make step, it must copy the
   pinned anchor exactly and use only pinned bodies. Any other form is refused.
3. **Makefile.** #8 changes only the `openapi-verify` `-run` alternation
   (`TestM0ContractIsTheFourProbes` → `TestPublicContractIsTheProbesPlusTheSetupOperations`). It adds no
   `?=` or unassigned variable, so the strict anchor's from-environment list stays at six. No pinned body
   changes, and check 5 ("non-empty -run") still holds.
4. **Counts only rise**, so the existing floors cannot trip. **Any `t.Skip`** in #8 fails the lane by name,
   because `allowed_skips` is empty.

## Cleanup (round three)

`vzv9r2-pg` and `vzv9r2-cache` were removed by exact name. `vzv9r2-make43` ran with `--rm`. `ubuntu:24.04` was
pulled by me this round and removed by exact name. The scratch clone was deleted. Nothing belonging to
`m1close-*` or `vidra-*` was touched, and neither was the builder's checkout nor the core-#8 worktree. `git ls-remote`
at the end: `e2a3e01…`, unmoved.

## Verdict at e2a3e01

Every in-scope acceptance bullet reproduced by me:

- the round-one and round-two attack rows are red with my own harness;
- the anchor pin holds against every altered form;
- strict mode can no longer be selected, or softened, from the environment;
- the builder's own `?=` finding is closed and demonstrated;
- the duplicate-key loader holds;
- the per-package floors are meaningful;
- FINDING 6 and D6 hold;
- the counts reproduce (1109 / 1154 / 45, 0 skips);
- CI is green on this SHA, with the manifest matching and the provenance naming the tested merge tree.

The residual list is now accurate. One SHOULD-level wording overstatement remains (R2-1). It is not
blocking, but the chair may want it fixed in the merge commit or a follow-up. Local `-race` runs were
starved by host load and are corroborated by CI only.

FINAL VERDICT: PASS — SHA e2a3e0177bdcda4ddb16b4b53cadafa69bb21ef4

---
---

# Re-confirmation at 0c1851f — 2026-09-23

- **Head:** `0c1851ffa678fa6e100a0dea26ebb5815aea87ff`, one commit on `e2a3e01` (an ancestor, no force-push):
  "docs: the anchor checks where `make` RESOLVES, not PATH order (R2-1)". Fresh clone in a private
  `mktemp -d`. No containers were needed this round.
- **Scope (narrow, as briefed):** the docs-only property, the R2-1 correction, the lanes that matter for a
  docs change, and CI on this SHA.

## RC-1. Docs-only, by my own method

`git diff --numstat e2a3e01..0c1851f`: `.github/pinned-steps.yml` 3/1, `AGENTS.md` 3/1,
`scripts/ci-required-guard.py` 3/1, and the new `docs/evidence/hardening-b1/R6-path-order.txt` 20/0. The diff
is empty for api/, internal/, cmd/, migrations/, Makefile, `.github/workflows`, `required-checks.txt`, every
other script, the Go tests, testdata and `test-floors.json`.

My method is different from the chair's AST comparison. I **tokenised** both versions of
`ci-required-guard.py` with Python's `tokenize`, dropped COMMENT/NL tokens and the module-docstring STRING,
and compared the streams:

```
guard: token streams equal (comments + module docstring removed): True | tokens: 5883 5883
pinned-steps.yml: parsed documents equal: True
pinned-steps.yml: non-comment lines byte-equal: True
__doc__ used in guard: 0
```

**The code path is byte-for-byte unchanged, and so is every value the guard reads from the pins file.**

## RC-2. The corrected sentence, against my R2-1 measurement

The strict anchor on the host, `python3 scripts/make-integrity-guard.py --workflow`:

```
control                                 exit=0
PATH=<empty non-system dir>:$PATH       exit=0
PATH=<dir holding a stub make>:$PATH    exit=1   FAIL  `make` resolves to '<scratch>/stubdir-…/make' …
```

The new AGENTS.md:100-103 reads: "…or makes `make` resolve outside the approved system directories. The anchor
checks where `make` RESOLVES, not the order of PATH: prepending a directory that holds no `make` is not
refused, and has no effect on which `make` runs." **This matches the measurement.** The two other copies
now say the same thing: the `pinned-steps.yml` comment at :34-36 and the guard docstring at :105-107, "…or
makes `make` resolve outside the approved system directories. The anchor checks where `make` RESOLVES, not
the order of PATH." **Both are true.**

Grep across every `.md/.py/.yml/.txt/.sh` outside testdata for PATH-order wording ("first on PATH", "earlier
on PATH", "prepend", "PATH order", "order of PATH"). Every remaining hit is one of these:

- the corrected sentences;
- R6's labelled quotation of the retracted sentence;
- a description of a stub **`make`** earlier on PATH. That case is refused, and the exit=1 row above measures it.
  The hits are `ci-required-guard.py:539`, `make-integrity-guard.py:799, :836`, `pinned-steps.yml:16`,
  evasion row A25, and `evasion-table.py:194`, which describes GitHub's `$GITHUB_PATH` mechanism.

In the PR body, line 42 states the corrected split. Line 97 quotes the retracted sentence under "**That was
false.**", which is a labelled quotation. **No PATH-order claim stronger than the control remains.**
**FINDING R2-1 is closed.**

## RC-3. Lanes

```
./scripts/make-integrity-guard.sh --workflow   exit 0   passed (8 gate target(s))
./scripts/ci-required-guard.sh                 exit 0   passed (6 required check(s))
go test -race -count=1 -v ./scripts/           exit 0   ok … 70.678s — 189 PASS, 0 FAIL, 0 SKIP
```

## RC-4. CI on 0c1851f

| check | conclusion |
|---|---|
| `ci-required` (run 35818887320) | **success**: `ci-required-guard: passed (6 required check(s))`; the fan-in prints `SUCCESS` for append-only, build-test, cache-matrix, fixtures, govulncheck and docker-build |
| `append-only`, `build-test`, `cache-matrix` (+ both legs), `fixtures`, `govulncheck`, `docker-build` | **success**. All six FLOOR_LANES completed on this SHA; the manifest matches the jobs that ran |
| `image-scan` (not required) | failure: `48 finding(s) at or above ['CRITICAL','HIGH']`, exit **1** (findings) |

The build-test log (run 35818887259) prints unit **1109**/943 and integration **1154**/981 (plain and
shuffled), with `internal/integration` **45**/40 and `skipped: 0` in all three. Provenance: tested merge tree
`4d44026…`, `HEAD^2 == 0c1851f…`, "checked: HEAD^2 == the PR head SHA". Duration 04:34:35 → 04:44:46 =
10m11s of 20 minutes.

## Verdict at 0c1851f

The only change since my PASS at `e2a3e01` is documentation. It is proven docs-only by token comparison, and
it corrects the one overstatement I raised (R2-1) to match my measurement exactly. The lanes and CI are green
on this SHA with the expected counts and 0 skips. No open finding.

Cleanup: the scratch clone and the two temporary PATH directories were deleted. No containers or images
were created.

FINAL VERDICT: PASS — SHA 0c1851ffa678fa6e100a0dea26ebb5815aea87ff
