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
