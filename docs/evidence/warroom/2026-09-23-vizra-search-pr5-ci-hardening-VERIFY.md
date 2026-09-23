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

---

# Re-verification at e068e07 (round 2 of 2, the last)

- **Head at start:** `git ls-remote origin refs/pull/5/head` = `e068e07fed999141a601374bb2b3b6251ede04d6`. One commit on `c3b2021` (verified ancestor, no force-push). Fresh clone in my own `mktemp -d …/vzv-search-pr5d-XXXXXX`.
- **Method:** byte and file mutations and inert fixtures only (comment-only files, copies of the Makefile, `/dev/null`). No payloads. Anything a classifier stops is recorded as NOT RUN.

## E1. Makefile diff and re-pin
- `git diff c3b2021 HEAD -- Makefile`: every changed line starts with `#`, so the diff is **comments only**.
- `shasum -a 256 Makefile` = `e9d7c58e…f5d02c`, which equals the pin in `.github/pinned-makefiles.yml`. The pin moved to core's shape (`makefiles:` mapping).
- `git diff --stat 3ea4103 HEAD -- api/` is empty, so `api/` is byte-identical.

## E2. Lanes (host, GNU Make 3.81)
`make ci` exit 0: **613** tests executed (floor 470), **0 skipped** (counted from the report stream), contract-drift 365 across 4 packages, vendor-contract-selftest 17/17. These match the builder's 613/0. The tree was clean afterwards.

## E3. Read, not tested
`scripts/makegate.py` was read in full. By its own description it adds the following, all before the requested command runs:
- `lstat` regular-file digests;
- a static read set;
- case-folded sibling refusal;
- a refusal of `MAKEFILES`;
- `clean_env` dropping `BASH_ENV`/`ENV`;
- make started by its realpath;
- one `make -q <every pinned file>` remake probe;
- a re-hash after the probe and after the command.

Its docstring states the residuals (reviewed bytes run their reviewed `$(shell …)` calls; a pin update approved with a malicious Makefile; machine changes by earlier steps; no `-r`, with the reason). **Reading is not verification.** None of these was exercised by me.

## E4. NOT RUN
A safety classifier stopped my response while I was preparing this round's mutation testing. Per the chair's instruction I record the following as **NOT RUN** and did not route around the stop:
- brief item 1: the builder's demo, and the Make 4.3 container run;
- brief item 2: my own F2 row (a newer `Makefile.sh`), the contract-drift-guard path, and `BASH_ENV=/dev/null`, with make-process counting;
- brief item 3: parity with core #10/B5b (closure targets reached through pattern rules, implicit rules or `.DEFAULT`);
- brief item 5: the full audit of doc sentences and residuals;
- brief item 6: the planted-ungated-make inventory test, and the deleted-assertion audit for c3b2021..e068e07.

**Whether FINDING 2 is closed at e068e07 is therefore UNVERIFIED by me.** The builder's claim (a `make -q` probe naming every pinned file) addresses its mechanism on paper.

## Cleanup (round e068e07)
Scratch clone deleted by exact path. No container was started and no image was pulled this round.

FINAL VERDICT: BLOCKED — SHA e068e07fed999141a601374bb2b3b6251ede04d6 (CI blocked by billing; the mutation and parity checks of brief items 1–3, 5 and 6 were NOT RUN because a safety classifier stopped this verifier, so FINDING 2's closure and core-B5b parity are unverified. What did run holds: `make ci` 613 tests / 0 skips, Makefile diff comments only, pin matches, `api/` unchanged. A different verifier must run the tamper rows before any PASS.)

---

# Re-verification at e068e07, part 2 (committed suite and reading)

- **Head at start:** `git ls-remote origin refs/pull/5/head` = `e068e07fed999141a601374bb2b3b6251ede04d6`. Fresh clone in my own `mktemp -d …/vzv-search-pr5e-XXXXXX`.
- **Method, as the chair narrowed it:** I ran the repository's own committed suite, and read tests, code and docs. I authored no mutation of the repository. The one thing I evaluated beyond reading: the inventory test's committed regexes, run against sample strings in a throwaway Python process (P3). No classifier stop occurred in this part.
- **Host:** darwin/arm64, go1.27.1, GNU Make 3.81. No container. **Nothing here was run on GNU Make 4.3**; the 4.3 rows rest on the builder's `docs/evidence/ci-hardening/make43-round2.txt` alone.

## P1. The committed suite
`go test -count=1 -v ./scripts/ ./internal/httpapi/`: **exit 0**. `ok scripts 116.2s`, `ok internal/httpapi 26.2s`. 372 `--- PASS` lines, **0 SKIP, 0 FAIL**.

| old finding | committed test (exact name) | ran / passed / skipped | what it asserts (read) | strong enough? |
|---|---|---|---|---|
| **FINDING 2**, newer sibling, through the anchor | `TestTheAnchorRefusesAPinnedMakefileMakeWouldRemake`, 10 subtests (`Makefile.sh`, `.c`, `.o`, `.y`, `.l`, `SCCS/s.Makefile`, `s.Makefile`, `Makefile,v`, `RCS/Makefile,v`, `RCS/Makefile`) | ran, 10/10 PASS, 0 skipped | The sibling is dated +24h, taken from the Makefile's own mtime. The test asserts: **the Makefile is byte-identical afterwards** (sha256 before and after, for every sibling); for the 7 `mustRed` siblings, a non-zero exit **and** the refusal by name ("would REMAKE a pinned makefile"); on any green, that the remake-probe-passed line was printed; and green again after the sibling is removed. | **Yes.** Byte-identity is the property FINDING 2 broke, and it is asserted directly. The 3 RCS rows are allowed to be green only with bytes unchanged and the probe line present. Make processes are not counted here; byte-identity is the stronger check for this finding. |
| **FINDING 2** through contract-drift-guard (R-1 path) | `TestEveryOtherMakeCallIsGated/contract-drift-guard.py_recipe/newer_Makefile.sh`, and the same for `makegate.py_--_--dry-run` | ran, PASS (8/8 subtests in the test), 0 skipped | non-zero exit; the gate's own text ("make was NOT invoked" or "only `make -q` ran"); Makefile byte-identical | **Yes.** |
| **FINDING 2** for a pinned include | `TestTheRemakeProbeCoversEveryPinnedInclude` | ran, PASS, 0 skipped | a reviewed, pinned include passes as the control; a newer `inc.mk.sh` then leaves `inc.mk` byte-identical, and the refusal names the one-invocation probe `make -q Makefile inc.mk` | **Yes.** |
| **R-1**: every make launch is gated | `TestEveryPlaceThatStartsMakeIsGated` (inventory) and `TestEveryOtherMakeCallIsGated` (the two known callers) | ran, PASS, 0 skipped. The inventory's log: "every place that starts make: [scripts/makegate.py:379]" | see P3 | **Partly.** The two known callers are gated (strong). The inventory has a reach gap: FINDING 4. |
| **R-2**: a failed pre-make check means 0 make processes | `TestTheAnchorStartsNoMakeAfterAFailedPreMakeCheck`, 10 subtests: `MAKEFILES` (workflow, local), a non-system make on PATH (workflow, local), `MAKEFLAGS=-i`, `BASH_ENV=/dev/null` (workflow, local), `ENV=/dev/null`, `GNUMAKEFLAGS=-i`, `VERSION=x` | ran, 10/10 PASS, 0 skipped | non-zero exit **and** the text "make was NOT invoked (0 make process(es) started)" | **Yes, with one note.** The "0" is interpolated from `makegate.MAKE_INVOCATIONS` (make-integrity-guard.py:870), not hard-coded. It is incremented in `makegate.run_make` (makegate.py:377-378), the only function that starts make. A read-only grep finds no `subprocess`/`os.system`/`os.exec`/`Popen` call in make-integrity-guard.py, contract-drift-guard.py or ci-required-guard.py, so every launch those scripts make goes through that counter. It is the guard's own counter, not an external recorder; an external PATH shim is impossible because the gate refuses a non-system make. `ENV` and `MAKEFLAGS` have a `--workflow` row only; local mode legitimately admits make-exported flag words. |
| **the 25 named constructs** | `TestNamedMakefileConstructsAreRefusedBeforeMake`, **25 subtests** (`.RECIPEPREFIX` ×3 spellings, `.SECONDEXPANSION`, `.ONESHELL`, `.IGNORE` ×2, `.DEFAULT`, `.POSIX`, `.EXTRA_PREREQS` ×2, `SHELL`, `.SHELLFLAGS`, `MAKEFLAGS`, `GNUMAKEFLAGS`, `MFLAGS`, target-specific `MAKEFLAGS`, pattern-specific `SHELL`, target-specific private `SHELL`, override `.SHELLFLAGS`, `define MAKEFLAGS`, `$(eval …)`, `+` recipe, `$(MAKE)` recipe, a recipe beginning with an expansion) | ran, 25/25 PASS, 0 skipped | Each fixture is inert and **re-pinned** (`repin`), so the digest passes and the named refusal itself is under test. Asserts non-zero, the refusal **by name**, "0 make process(es) started", and ci-required-guard red with the same name (parity) | **Yes.** Re-pinning is what makes each row test the named refusal and not the digest. |
| (R-3, parity) symlink and siblings | `TestPinnedFilesMustBeRegularAndAloneInBothReaders`, 5 subtests (a symlink to identical bytes, `GNUmakefile`, a case-variant `GNUMakefile`, a missing pinned file, a stale pin entry) | ran, 5/5 PASS, 0 skipped | refused by name before make in the anchor, and by ci-required-guard | **Yes.** |

## P2. `make ci` (from part 1, same SHA)
Exit 0: 613 tests, 0 skips, contract-drift 365, selftest 17/17.

## P3. The inventory test, by reading and by evaluating its committed regexes
`TestEveryPlaceThatStartsMakeIsGated` (scripts_test.go:1264-1322) walks `.go`/`.py`/`.sh` files. It skips `.git`, `bin`, `docs`, `testdata` and `node_modules`, and skips lines that start with `#` or `//`. It applies one regex per language, and it fails on a zero-hit scan (a good non-vacuity check). I evaluated the three committed regexes against sample strings in a throwaway process; the repository was not touched:

| language | sample | result |
|---|---|---|
| go | `exec.Command("make", "ci")` | HIT |
| go | `exec.Command("/usr/bin/make", "ci")` | HIT |
| go | **`exec.CommandContext(ctx, "make", "ci")`** | **MISS**. The regex names `Context`, but `[^,)]*?` cannot cross the comma after `ctx`. |
| py | `subprocess.run(["make", "ci"])` | HIT |
| py | **`subprocess.run("make ci", shell=True)`** | **MISS** |
| py | **`os.system("make ci")`** | **MISS** |
| py | **`subprocess.run(["env", "make", "ci"])`** | **MISS** |
| sh | `make ci`, `FOO=1 make ci` | HIT |
| sh | **`cd x && make ci`**, **`if make -q ci; then …`**, **`/usr/local/bin/make ci`** | **MISS** (the pattern is anchored at line start, and only `/usr/bin/` is allowed as a path) |

Every MISS is a literal call, not a variable or a wrapper. **Today's tree has none of them.** A broader read-only grep for `CommandContext(…"make"`, `os.system(…make`, `shell=True`, `make` after `&&`/`;`/`|`/`(`/`then`/`do`/`if`, and `/usr/local/bin/make`, over `.go`/`.py`/`.sh` outside `docs/`, found only messages, comments, test-fixture strings and a stub body inside a Go string. `scripts/*.sh` start no make. So the claim "every place a script or test starts make goes through makegate" is **true of this tree today**. The inventory test would not catch a future literal call in the missed forms. See FINDING 4.

## P4. Doc sentences under "no false-guarantee merges"

| sentence | verdict |
|---|---|
| AGENTS.md:518-522 "Every place a script or test … starts make goes through one helper … `TestEveryPlaceThatStartsMakeIsGated` fails on any other make call it can see" | **TRUE today**, by my grep; "it can see" is hedged |
| **AGENTS.md:609-611** "`TestEveryPlaceThatStartsMakeIsGated` sees literal make calls in `.go`, `.py` and `.sh` files; a make started through a variable or a wrapper it cannot read is review-only" | **OVERSTATED**: the literal forms in P3 are not seen (FINDING 4) |
| **makegate.py:9** "scripts/scripts_test.go inventories every place the repository starts make and fails on any other" | **OVERSTATED**, unhedged (FINDING 4) |
| **scripts_test.go:1259-1262** (the test's own comment) "Anything else — a Go exec.Command, a Python subprocess list, a shell line — is red here, so a new, ungated make call cannot arrive unnoticed" | **OVERSTATED** (FINDING 4) |
| AGENTS.md:540-551, makegate docstring: the `make -q <every pinned makefile>` probe; the sibling list; RCS forms green with bytes unchanged | **consistent with the committed tests on 3.81** (P1). The 4.3 half rests on the builder's transcript; I did not run 4.3. |
| AGENTS.md:552-556 "After every make run the pinned files are re-hashed"; "`ci-required-guard.py` makes the same byte, symlink, include and sibling checks without running make" | **consistent with the code** (`Gate.run` → `recheck`) and with the parity asserts in P1 |
| AGENTS.md:557-560, makegate docstring: "`-r` deliberately NOT used", with its reason | stated, and consistent with the code |
| AGENTS.md "What it guarantees, exactly: make runs only on reviewed bytes — and those reviewed bytes run their own reviewed `$(shell …)` calls …" | **consistent with the committed tests** for every path those tests cover (P1). I did not assess core B5b parity (closure targets reached through pattern rules, implicit rules or `.DEFAULT`); the chair assigned it to the security seat. Whether this sentence survives that review is theirs to say. |
| residuals: a reviewer approving a malicious Makefile with its pin; another step's effects on the machine; env vars outside the named set; reusable workflows and wrappers | stated. Accurate, except the inventory clause above |
| evidence README:10 "every script or test that starts make goes through it" | **TRUE today** (P3 grep) |
| evidence README: a first 4.3 container attempt hung, partial output not used, cause "not verified" | honest disclosure |

## P5. Deleted-assertion audit, `c3b2021..e068e07` (reading `git diff`)
Deletions: scripts_test.go −27, make-integrity-guard.py −234, ci-required-guard.py −28, lane_selection_test.go −6, contract-drift-guard.py −9, ci-hardening-demo.py −9, vendor-contract.py −5, revendor-demo.sh −1.
- Each deleted mutation row in scripts_test.go reappears at HEAD under the same name, with its `want` updated to the new wording. Examples: "does not match its pinned digest" became "does not match its pin"; the pin-shape rows now name the `makefiles:` shape. `.SHELLFLAGS without -e` became `.SHELLFLAGS := -c` in `TestNamedMakefileConstructsAreRefusedBeforeMake`, which is stronger: it also asserts 0 make processes and guard parity.
- lane_selection_test.go: the deleted `t.Fatalf("make --dry-run contract-drift failed…")` is replaced at line 61 by the same assertion over `makegate.py -- --dry-run contract-drift`.
- make-integrity-guard.py −234: the digest logic moved into makegate.py.
- **No weakened assertion found.**
- `revendor-demo.sh`: the leftover `printf | grep -q` (my FINDING 3, NIT) is the one-line change, so FINDING 3 is presumably closed. Not re-run.

## Findings (part 2)

```
FINDING 4: the make-launch inventory misses literal make calls, and three sentences say it does not
Severity:    REQUIRED
Confidence:  high
Class:       NEW-CLASS (the inventory test is new in this round; not a regression of FINDING 2)

Affected:
  repo:      vizra-search
  files:     scripts/scripts_test.go:1257-1268 (TestEveryPlaceThatStartsMakeIsGated and its regexes),
             AGENTS.md:609-611, scripts/makegate.py:9
  requirements: none (R-1 of the security desk review)

Observed:
  Evaluated against the committed regexes: exec.CommandContext(ctx, "make", …), subprocess.run("make …",
  shell=True), os.system("make …"), subprocess.run(["env", "make", …]), and shell lines `cd x && make …`,
  `if make …`, `/usr/local/bin/make …` do not match. All are literal calls. AGENTS.md:609-611 says the test
  "sees literal make calls" and puts only variables and wrappers out of reach. makegate.py:9 says the test
  "inventories every place the repository starts make and fails on any other". The test's own comment says
  an ungated call "cannot arrive unnoticed". Today's tree has no such call (P3 grep), so there is no live
  ungated launch.

Failure:
  A future PR could add, for example, a Go test that runs exec.CommandContext(ctx, "make", …) in the
  test-noskip lane, where no anchor runs. That is exactly R-1's exposure. The inventory, which is the
  control for R-1, stays green, and three sentences tell the reviewer it would not. This is a
  false-guarantee sentence on a security control.

Perspective:
  developer, operator

Recommendation:
  The smallest fix is to state what the scan matches: "literal exec.Command("…make", …), a Python list
  starting with "…make", and a shell line whose first word is make", and to name the missed forms as
  review-only. Better is to widen the scan: a Go AST walk over every exec.Command* call with a "make"
  string argument; for .py, any "make" token inside a string passed to subprocess/os.system/os.exec*;
  for .sh, make in any command position (after ;, &&, ||, |, `(`, then, do, if).

Acceptance criteria:
  Either every form in the P3 table is refused by TestEveryPlaceThatStartsMakeIsGated, with a table case
  for each, or AGENTS.md, makegate.py:9 and the test comment name exactly the forms matched and list the
  rest as review-only.

Tests:
  scripts/scripts_test.go: give TestEveryPlaceThatStartsMakeIsGated a table of source lines, fed to its
  matcher, one per P3 row, each expected to hit (or, after a narrowing, to be named in the doc as a miss).

Cross-repo implications:
  core: if core adopts an inventory test, the same regex shapes need the same review. user/meta: none.

Challenge:
  "Today's tree is clean and a reviewer would see such a line." True. So this is not a BLOCKER. But the
  inventory exists precisely so that nobody has to notice, and three sentences promise more than it does.
```

Earlier findings at e068e07: **FINDING 2 (BLOCKER at c3b2021)** is covered by committed, passing, byte-identity-asserting tests on 3.81 (P1). I judge it **closed on 3.81**; on 4.3 it rests on the builder's transcript. FINDING 3 (NIT) is presumably closed (P5). FINDING 1 (NIT, "not forgery" wording): not re-checked.

## Which rows rest on what
- **Committed tests, run by me (3.81):** FINDING 2 through the anchor, through contract-drift-guard, and for a pinned include; R-2 (10 rows); the 25 named constructs; symlink and sibling parity; the two known make callers gated; `make ci` 613/0.
- **Reading only:** the assertion strength of each test; the counter's provenance; doc truthfulness; the deleted-assertion audit; my judgement that `ci-required-guard.py` shares makegate's checks.
- **Regex evaluation against sample strings (no repository change):** FINDING 4.
- **Not run by me:** anything on GNU Make 4.3; core B5b parity (the security seat's); the builder's demo harness.

## Cleanup (part 2)
Scratch clone deleted by exact path. No container, no image.

## Verdict at e068e07 (supersedes part 1's BLOCKED)
Everything the committed suite covers holds on 3.81:
- FINDING 2's sibling remake, through both callers and for a pinned include;
- R-2's zero-make rows;
- the 25 named constructs;
- the byte, symlink and sibling parity;
- `make ci` 613/0, with no weakened assertion and `api/` unchanged.

One NEW-CLASS REQUIRED finding remains. The R-1 inventory misses literal make launches, and AGENTS.md:609-611, makegate.py:9 and the test's own comment say it does not. Under "no false-guarantee merges" that sentence is blocking. It is a narrow fix: reword three sentences, or widen the scan. It does not show a live ungated launch in today's tree. CI remains BLOCKED by billing. The 4.3 half rests on the builder's transcript, and core-B5b parity is with the security seat.

FINAL VERDICT: FAIL — SHA e068e07fed999141a601374bb2b3b6251ede04d6 (FINDING 4, REQUIRED, NEW-CLASS: the make-launch inventory's stated reach exceeds its regexes. Everything else the committed suite covers passes, and FINDING 2 is closed on 3.81.)
