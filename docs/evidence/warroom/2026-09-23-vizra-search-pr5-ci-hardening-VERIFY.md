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

FINAL VERDICT: BLOCKED — SHA 4476ad58aa3fbd7cd70604ad0b94ec10deea6b2d (CI blocked by account billing; brief items 1–2, and the core cross-check, were declined by this verifier and need a different verifier; items 3–6 checked here hold, with one NIT)
