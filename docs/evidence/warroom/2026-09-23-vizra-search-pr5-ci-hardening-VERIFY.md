# Independent verification: vizra-search PR #5, CI hardening (queue 2g)

- **SHA verified:** `4476ad58aa3fbd7cd70604ad0b94ec10deea6b2d` (`git ls-remote` confirmed `refs/pull/5/head` at this SHA; one commit on `main@3ea4103`).
- **Clone:** fresh, under the verifier's own `mktemp -d …/scratchpad/vzv-search-pr5-XXXXXX`. Deleted at the end.
- **Host:** darwin/arm64, go1.27.1, GNU Make 3.81. No Make 4.3 container was started.

## What I reproduced

| check | command | result |
|---|---|---|
| head unmoved | `git ls-remote origin refs/pull/5/head` | `4476ad5…` |
| local CI entry point | `make ci` (clean clone, 3.81) | **exit 0**: 553 tests executed (floor 470), 553 passed, **0 skipped** (counted from the report's `-json` stream); contract-drift 365 tests across 4 packages, none deselected; vendor-contract-selftest 17/17 |
| vendored contract unchanged | `git diff --stat 3ea4103 4476ad5 -- api/` | empty, so it is byte-identical |
| "exhaustive" in docs | `grep -i exhaustive AGENTS.md README.md` | no match |
| deletions (`--numstat`) | see list | the largest deletions are AGENTS.md −43, config_test.go −46, ci-required-guard.sh −54 (logic moved into the .py) and contract-drift-guard.py −16. **Not audited line by line**: I did not confirm that each deleted assertion was replaced by an assertion at least as strong |

## CI: BLOCKED
All 12 jobs on this SHA (`fmt`, `vet`, `echo-containment`, `build`, `contract-drift`, `test`, `test-noskip`, `tidy-check`, `govulncheck`, `vendor-contract-selftest`, `docker-build`, `ci-required`) concluded `failure`. They were not started because of the account billing refusal. The following is BLOCKED:
- CI-printed counts and floors;
- GNU Make 4.3 on the runner;
- the `docker-build` lane;
- durations;
- the check that `ci-required`'s manifest matches the jobs that ran.

## Not performed by me: the adversarial reproduction (brief items 1–4)
I did not complete these with my own harness:
- the reproduction of core PR #9's evasion history (round-1 thirteen, N1–N4, the MAKELEVEL spellings, `?=` overrides, duplicate/merge keys, `if: always() && false`);
- the attack on the new parse-time pre-flight in `scripts/make-integrity-guard.py` (`check_parse_time_side_effects`);
- the Make 4.3 anchor rows;
- the `source_ref_tip` forging, two-segment URL, env.go seam and emptied-manifest demonstrations;
- the cross-repo reproduction against vizra-core's anchor.

These must be reproduced by a verifier before any PASS. The builder's own transcripts (`docs/evidence/ci-hardening/`) are the builder's claims, not independent evidence.

Design observation from reading the source, not measured: the pre-flight is a hand-written scanner plus regular expressions over the Makefile text. It is not a make parser. It runs before `make` is invoked and returns without invoking make on any refusal (`main()`, make-integrity-guard.py:986-989). Whether its coverage matches make's grammar is exactly what the unperformed attack rows would test.

## Findings
None raised in the first pass. See the continuation below.

---

# Continuation: the coordinator asked for the adversarial scope

The head was checked before and after with `git ls-remote`: `4476ad5…`, unmoved. I used a fresh clone in my own `mktemp -d …/vzv-search-pr5b-XXXXXX`, deleted afterwards. `git status` was clean after every restore.

## Declined by this verifier
I did not do these parts of the continuation request:
- coordinator item 1: building Makefile constructs to make the anchor's `make -pn` execute commands or write the runner's `$GITHUB_ENV`;
- coordinator item 2: re-creating core #9's workflow and environment evasion rows;
- coordinator item 4: the same against vizra-core's anchor.

A safety classifier stopped my first attempt at that payload work, and an agent message cannot lift that stop. **These remain unverified and need a different verifier.** Nothing in this file is evidence for or against the pre-flight's coverage.

## Item 3: reproduced by me

**Env seam (`TestNothingOutsideTheSeamReadsTheProcessEnvironment`).** I added a new non-test file, `internal/zz_vzv_probe.go`, then deleted it. The test is `ok` before and after.

| variant | result |
|---|---|
| aliased import `o "os"`, `o.Getenv("X")` | **RED**: `os.Getenv reads the process environment outside the Lookup seam` |
| `syscall.Getenv("X")` | **RED**: `syscall.Getenv …` |
| `var f = os.LookupEnv` (taken as a value) | **RED**: `os.LookupEnv …` |

**Manifest and selftest-lane agreement (`./scripts/ci-required-guard.sh`, PyYAML 6.0.3).** Each mutation was restored afterwards and the guard was green again.

| mutation | result |
|---|---|
| control | exit 0, `passed (11 required check(s), 11 checked lane(s))` |
| manifest with only comments and blank lines | **exit 1**, `REQUIRED-CHECKS MANIFEST EMPTY: … every line is a comment or blank.` |
| `vendor-contract-selftest` removed from the manifest | **exit 1**, `required lane 'vendor-contract-selftest' is MISSING from required-checks.txt` |
| `vendor-contract-selftest` removed from the Makefile's `ci:` | **exit 1**, `the Makefile's ci: and the required lanes disagree` |
| the `vendor-contract-selftest` job removed from ci.yml | **exit 1**, `matches no job` and `pinned-steps.yml requires invocations of job 'vendor-contract-selftest', which no workflow defines` |

**Two-segment URL (code read).** `scripts/vendor-contract.py:175-182`: `if len(parts) != 2: return host or None, None`. This replaces `parts[-2:]`. The selftest passed 17/17 under `make ci`. I did not write my own URL rows.

**`source_ref_tip` and "behind is a note" (code read, `vendor-contract.py:481-580`).**
- Without `--core`: the tip must be 40 lowercase hex characters and not the null id.
- With `--core`: the tip must be a commit, an ancestor of the recorded ref, and contain `source_commit`.
- A tip that differs from the current tip only prints a note.
- The laundering round 1 worried about is still refused by the separate check `commit != source_commit` ("re-vendor"). That check compares the pin against core's current last `api/` commit, so a stale pin is refused whatever tip is recorded.
- Residual: any on-ref commit between `source_commit` and the current tip is accepted as the tip. The check cannot prove the tip was the one current at vendoring time. AGENTS.md:99 states only what is checked ("a commit in core, **on** the recorded ref, and … **contain** `source_commit`"), which is accurate. The runtime note says "staleness, not forgery", which claims slightly more than the check shows (FINDING 1, NIT).
- `--check --core` does not run in CI (no core checkout), as the Makefile says.

**Deleted-assertion audit (`git diff 3ea4103 4476ad5`).**
- `config_test.go` (−46): every deleted `t.Fatal*` has an equivalent re-added at package scope. That covers lines 637, 656, 664, 671, 677, 881 and 885, and line 858 is a new check that config.go was read. The diff adds 20 `t.Fatal`/`t.Error` lines and deletes 8. The "exhaustive by construction" comment was removed, which is consistent with item 8.
- `vendor-contract-selftest.py`: the deleted line is a comment. The `--check` assertion stays, and a `--check --core` assertion was added. `EXPECTED_CASES` went from 11 to 17.
- `vendor-contract.py`: `parts[-2:]` was replaced by the exactly-two rule.
- `contract-drift-guard.py` (−16): only docstring prose describing the old, unclosed Makefile exposure was deleted.
- `ci-required-guard.sh` (−54): logic moved into the `.py`. The four refusals above show the manifest, `ci:` and job checks are live.
- No weakened assertion found.

## Findings

```
FINDING 1: the "behind" note says "not forgery", which the check cannot establish
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/vendor-contract.py:574-575
  requirements: none

Observed:
  The tip checks accept any commit that is on the ref and contains source_commit. The note printed for
  recorded_tip != tip reads "(staleness, not forgery — see the api/ commit check)".

Failure:
  A tip picked arbitrarily from between source_commit and the current tip is indistinguishable from an
  honest stale one. "not forgery" overstates the check. Nothing is laundered: the source_commit
  comparison still refuses a stale pin.

Perspective:
  developer

Recommendation:
  Reword to "(on the ref and contains source_commit; whether it was the tip at vendoring time cannot be
  checked)".

Acceptance criteria:
  The note states only what the three git checks establish.

Tests:
  review.

Cross-repo implications:
  none.

Challenge:
  "Everyone reads it as 'not a failure'." Probably. That is why this is a NIT.
```

## Cross-repo note for the chair
Not performed (declined, see above).

FINAL VERDICT (at 4476ad5): BLOCKED — CI blocked by account billing; brief items 1–2 and the core cross-check were declined by this verifier and need a different verifier; items 3–6 checked here hold, with one NIT. Superseded by the re-verification below at c3b2021.

---

# Re-verification at c3b2021

- **Head:** `git ls-remote origin refs/pull/5/head` = `c3b2021ee089a04dfbfce2a8cb0d3ee653e8b7fb`, before and after, unmoved. It is one commit on top of `4476ad5` (verified ancestor, no force-push). Fresh clone in my own `mktemp -d …/vzv-search-pr5c-XXXXXX`, deleted at the end.
- **Env:** darwin/arm64, GNU Make 3.81 (host); GNU Make 4.3 in a throwaway `ubuntu:24.04` container `vzvs5c-m43` (`--rm`), image pulled and removed by exact name.
- **The control changed.** The text-shape pre-flight is retired. `check_makefile_digests` (make-integrity-guard.py) now refuses to invoke make unless every file in `.github/pinned-makefiles.yml` matches its sha256 and no unpinned `GNUmakefile`/`makefile` sits beside it; after make runs, `MAKEFILE_LIST` must equal the pinned set.
- **Harness:** I wrapped `subprocess.run` so every `make` invocation the anchor makes is counted (`TRACE make invocations: N`), so "make was not invoked" is measured, not inferred.

## The digest gate under byte mutations (host 3.81, `--workflow` and local; Linux 4.3 for a subset)
Each row: mutate, run the traced anchor, restore, assert the tree is clean. `make invocations: 0` means make never ran.

| row | anchor | make invocations | correct? |
|---|---|---|---|
| control | exit 0 | 19 | yes |
| one byte changed in Makefile | exit 1 | 0 | yes — digest mismatch |
| trailing newline added / removed | exit 1 | 0 | yes |
| CRLF conversion | exit 1 | 0 | yes |
| `include` added, not re-pinned | exit 1 | 0 | yes — digest mismatch |
| `include` added, Makefile re-pinned, include not pinned | exit 1 | 1 | yes — `MAKEFILE_LIST` ≠ pinned set |
| `include` added, both pinned | exit 0 | 19 | yes (legitimate) |
| …then one byte of the included file changed | exit 1 | 0 | yes |
| `GNUmakefile` copy beside Makefile | exit 1 | 0 | yes — unpinned sibling |
| `gnumakefile` (lowercase) on case-insensitive host FS | exit 0 | 19 | benign on macOS (no second file exists); on Linux `makefile`/`GNUmakefile` are refused — rows L2/L3 |
| Makefile pin entry deleted | exit 1 | 0 | yes |
| pin malformed (63 hex) / upper-case hex | exit 1 | 0 | yes |
| extra pin for a non-existent file | exit 1 | 0 | yes |
| duplicate pin line | exit 1 | 0 | yes |
| pin file deleted | exit 1 | 0 | yes |
| pin file CRLF, Makefile unchanged | exit 0 | 19 | yes (Makefile bytes still match) |
| Makefile → symlink to identical bytes | exit 0 | 19 | yes (digest follows the link) |
| Makefile → symlink to changed bytes | exit 1 | 0 | yes |
| `MAKEFILES=<comment-only file>` in env | exit 1 | 1 | yes — `MAKEFILE_LIST` ≠ pinned set (and env refused) |

Linux/Make 4.3 container confirmed the control rows: control green (19), one byte red (0), `GNUmakefile` and `makefile` siblings red (0), unpinned include red, `MAKEFILES` red. `MAKEFILE` (uppercase, a name make does not read) is correctly green.

The `-f Makefile` path is refused statically: a `make -f Makefile test` step is not byte-equal to a pinned body (`ci-required-guard.sh` row S4, two named failures).

## FINDING 2 (below) — the digest gate is bypassed by a newer `Makefile.sh` sibling
The coordinator's added row. It **applies**. See the finding block.

## The `MAKEFILE_LIST` post-check
Meaningful, not redundant: it is the only thing that catches an `include` of a pinned-but-listed-elsewhere file and an env-injected `MAKEFILES` (both showed `make invocations: 1` then red). The pre-check catches on-disk byte changes; the post-check catches what make read that the directory listing did not show. Its `ok` line ("MAKEFILE_LIST is exactly the pinned set") claims exactly what it checks. But it does NOT catch a Makefile that make itself rewROTE during the anchor's own `make -pn` (FINDING 2): the rewritten file is still named `Makefile` and still the sole member of `MAKEFILE_LIST`.

## SIGPIPE fix (brief item 4)
`ci-required-guard.sh:244` now uses a here-string (`grep -qF "$want_line" <<< "$out"`) instead of `printf | grep -q`. Correct and race-free. Remaining `| grep -q` under `set -uo pipefail`: `scripts/revendor-demo.sh:163` (`printf '%s' "$LAST_OUT" | grep -qF`). revendor-demo.sh is not a CI lane, so this is a latent flake in a demo only (FINDING 3, NIT).

## Regression of the earlier baseline
- `make ci` exit 0: **554** tests executed (floor 470), **0 skipped** (counted from the report stream), contract-drift 365 across 4 packages, vendor-contract-selftest 17/17. (554 vs the earlier 553: one new test row.)
- `api/` byte-identical to `main@3ea4103` (`git diff --stat 3ea4103 HEAD -- api/` empty).
- Static guard fail-closed rows all red with named reasons (control green): Makefile byte change, pin entry deleted, pin file deleted, `make -f`, comment-only manifest, selftest dropped from `ci:`.
- Env-seam, manifest/lane agreement, and the two-segment URL rule are unchanged by this commit (verified present in the diff base and re-run at 4476ad5 in the section above).
- **Deleted assertions (4476ad5..c3b2021):** the removed `scripts_test.go` tests are `TestMakeIntegrityGuardRefusesEveryNeuteredMakefile` and `TestTheAnchorExecutesNothingWhileReadingTheMakefile` — both tested the retired text scanner, and both are REPLACED by `TestTheAnchorRunsMakeOnlyOnPinnedBytes`, `TestMakeIntegrityGuardStillRefusesKnownShapesInReviewedBytes` and the new digest-pin rows. No assertion covering a live control was weakened. The make-integrity-guard.py deletions are the retired `check_parse_time_side_effects`/`_expansions` and are replaced by `check_makefile_digests` + the `MAKEFILE_LIST` post-check.

## Truthfulness
- AGENTS.md:514-530 describes the digest gate accurately, including "make runs only on reviewed bytes" and the reviewer/pin-update residual. **But that central claim is falsified by FINDING 2**: the anchor's own `make -pn` can rewrite the Makefile to unreviewed bytes.
- No "exhaustive" in AGENTS.md or README.
- PR-body claims of 554 tests / 0 skips / selftest 17/17 and the SIGPIPE fix reproduce.

## Findings

```
FINDING 2: a newer unpinned `Makefile.sh` sibling makes the anchor's own `make -pn` rewrite the
           Makefile to unreviewed bytes, and the anchor passes
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/make-integrity-guard.py:978-1004 (main: digest gate, then `make -pn` with no remake check),
             resolve_database() `make -pn TARGET`
  requirements: the slice's central claim, "make runs only on reviewed bytes" (AGENTS.md:523-524)

Observed:
  Reproduced on GNU Make 3.81 (host), in the clean clone at c3b2021, with the make-invocation trace:
    1. Pin matches: `shasum -a256 Makefile` = 128b0f87a432…, the pinned value.
    2. Create `Makefile.sh` = a copy of Makefile + one comment line, with an mtime newer than Makefile.
       `Makefile.sh` is NOT in `.github/pinned-makefiles.yml` (the pin covers only `Makefile`).
    3. Run the anchor: `python3 make-integrity-guard.py --workflow`.
       Result: anchor exit 0, "make runs only on reviewed bytes … match", "MAKEFILE_LIST is exactly the
       pinned set: ['Makefile']", "passed (9 gate target(s))".
    4. After the anchor, `shasum -a256 Makefile` = b54f001b8ef9… — the Makefile on disk has been
       REWRITTEN, its tail now ends "# vzv sibling marker" (the Makefile.sh contents).
  GNU Make's built-in rule `% : %.sh` (`cat $< > $@; chmod a+x $@`) fires while make READS makefiles —
  makefile remaking happens even under `-pn` — so `make -pn ci` remade `Makefile` from the newer
  `Makefile.sh` before the anchor ever reached its checks on the running lane. The digest check ran
  first, on the still-original bytes, so it passed; the `MAKEFILE_LIST` post-check still sees only
  `Makefile`, so it passed too. This is exactly vizra-core's B5 class, reached with no Makefile line at
  all. (Siblings `Makefile.c/.o/.y/.l` and `SCCS/s.Makefile` made `make -pn` exit 2 and were refused by
  accident; `Makefile.sh` succeeds and rewrites. The one that matters is unrefused.)

Failure:
  The control's whole guarantee — "make runs only on reviewed bytes" — is false. An unpinned
  `Makefile.sh` (added in a PR without touching the pin, since the pin only covers `Makefile`) causes
  the anchor's own dry-run to overwrite `Makefile` with arbitrary attacker-chosen bytes, which the
  subsequent pinned `make` step in the same job then executes. The reviewed Makefile is not what runs.
  Exploitability in live CI depends on `Makefile.sh` being checked out with an mtime newer than
  `Makefile` (git does not preserve mtimes; ordering is filesystem/timing dependent), so it is not a
  guaranteed-every-run bypass — but the control is unsound, and the war-room bar is "gates cannot pass
  vacuously". UNVERIFIED: end-to-end in GitHub Actions (CI is billing-blocked); the mechanism is
  version-independent (core measured 3.81 and 4.3) and I reproduced it on 3.81.

Perspective:
  developer, operator (a merge gate that can be made to run unreviewed build/test bytes)

Recommendation:
  Adopt vizra-core's B5 fix: before `make -pn`, run `make -q` (or `make -pn --no-builtin-rules
  --assume-old=<each pinned makefile>`) against the pinned makefiles and REFUSE if make reports that any
  makefile would be remade; and/or disable built-in rules for the resolver (`-r`) and refuse any sibling
  that make's implicit rules could turn into a pinned makefile. Re-hash every pinned file AFTER `make -pn`
  and refuse if any changed.

Acceptance criteria:
  With a newer unpinned `Makefile.sh` (or `.c/.o/.y/.l`, `Makefile,v`, `RCS/`, `SCCS/`) beside the
  Makefile, the anchor exits non-zero, make is not left having rewritten any pinned file, and the
  on-disk Makefile digest after the anchor equals the pin. A row per sibling in
  TestTheAnchorRunsMakeOnlyOnPinnedBytes.

Tests:
  scripts/scripts_test.go: a new table in TestTheAnchorRunsMakeOnlyOnPinnedBytes that plants a newer
  Makefile.sh and asserts (a) the anchor is red, (b) the Makefile digest is unchanged afterward. The
  harness must set Makefile.sh's mtime ahead of Makefile's, as core's B5 test does.

Cross-repo implications:
  core: core's B5 fix is the reference; confirm search adopts it. user: none. search: this PR. meta: none.

Challenge:
  "git checkout won't reliably make Makefile.sh newer, so it may not fire in real CI." True, and that is
  why exploitability end-to-end is UNVERIFIED. But the anchor's job is to make the bypass IMPOSSIBLE, not
  improbable; on the host it fired every time I set the mtime, and the whole point of moving from grammar
  to digest was soundness. A control that a sibling file defeats is not sound.
```

```
FINDING 3: a demo script keeps `printf | grep -q` under pipefail
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/revendor-demo.sh:163
  requirements: none

Observed:
  ci-required-guard.sh:244 was fixed to a here-string. revendor-demo.sh:163 still has
  `printf '%s' "$LAST_OUT" | grep -qF -- "$n"` under `set -uo pipefail`.

Failure:
  The same SIGPIPE flake (grep -q exits on first match, printf dies of SIGPIPE, pipeline fails on a
  match). revendor-demo.sh is not a CI lane, so this is cosmetic.

Perspective:
  developer

Recommendation:
  `grep -qF -- "$n" <<< "$LAST_OUT"`.

Acceptance criteria:
  No `| grep -q` under pipefail remains in scripts/.

Tests:
  review / `grep -rn '| grep -q' scripts`.

Cross-repo implications:
  none.

Challenge:
  "It's a demo, not a gate." Correct — hence NIT.
```

FINDING 1 (the "behind is a note" NIT) from the 4476ad5 section still stands at c3b2021 (vendor-contract.py unchanged in this commit).

## Cleanup (round c3b2021)
Scratch clone deleted by exact path. Container `vzvs5c-m43` ran with `--rm`; `ubuntu:24.04` was pulled by me and removed by exact name (`docker rmi ubuntu:24.04`). A stray `row.out` my mis-pathed first harness wrote to the shared scratchpad root was removed by exact path; nothing else in the shared root was touched (`b5digest.*`, `closing-pr8-*`, `m1a5-*`, `m1close-*`, `vzv-core-pr8r3-*` and the loose `.m1a5`/`.vzv-r3-*`/`r3_race_test.go` files left in place).

FINAL VERDICT: FAIL — SHA c3b2021ee089a04dfbfce2a8cb0d3ee653e8b7fb (FINDING 2, BLOCKER: a newer unpinned `Makefile.sh` sibling makes the anchor's own `make -pn` rewrite the Makefile to unreviewed bytes while the anchor passes — the digest gate's central guarantee is unsound; core's B5 remake fix is not applied here. Plus two NITs. CI also BLOCKED by billing, but the FAIL does not depend on CI.)
