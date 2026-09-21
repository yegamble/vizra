# Independent verification — vizra META PR #3 (`validate` lane + `ci-required` fan-in)

**Verdict: PASS** (with 4 non-blocking findings, 2 of which are unstated gaps in
the lane's guarantees that should be closed in a follow-up).

| | |
|---|---|
| Repo | `yegamble/vizra` (meta) |
| PR | [#3](https://github.com/yegamble/vizra/pull/3) — `ci/meta-validate` → `chore/m0-meta-baseline` (stacked) |
| Head SHA verified | `e667b605b6c0f7930cea959d9585be17cd519662` |
| Head confirmed unmoved | `gh api repos/yegamble/vizra/git/ref/heads/ci%2Fmeta-validate` → `e667b605…` |
| Merge base | `3b63c0ef7eac2550f4d47dd5d854fec55a225df4` |
| Verifier | independent; did not write this code |
| Date | 2026-09-21 |

## Environment

Fresh clone from `https://github.com/yegamble/vizra.git` into a scratch
directory (never the builder's worktree at `.claude/worktrees/meta-validate`,
never a branch switch in the chair's main checkout), checked out detached at
`e667b60`, working tree clean.

| | Local (this verification) | CI (`e667b60`) |
|---|---|---|
| OS | macOS 26.5.1 (darwin) | Ubuntu 24.04.5 LTS, image `ubuntu-24.04` / `20260907.300.1` |
| Python | 3.9.6 (system); 3.13.13 (homebrew) for the cross-version attack | 3.12.14 (`actions/setup-python`, SHA-pinned) |
| PyYAML | 6.0.3 | 6.0.1 (runner image; the pinned install did **not** execute) |
| git | 2.50.1 | 2.55.0 |
| Docker | not used, not required | — |

## 1. The four lane scripts, from a clean clone at `e667b60`

All run from the repository root. Exit codes are the real exit codes, captured
separately from piped output.

| Command | Exit | Reported |
|---|---|---|
| `./scripts/check-generated-ledger.sh` | **0** | `OK 191 requirements; core=141` then `generated ledger reproduces byte-for-byte: docs/quality/features.json` |
| `./scripts/check-quality-json.py` | **0** | `json parsed: 4 file(s)`; `ledger: 191 requirement id(s)`; `requirement ids: 139 distinct VZ-… reference(s) across 14 document(s); every one resolves` |
| `./scripts/check-doc-links.py` | **0** | `relative links: none exist yet across 88 markdown file(s) (checked nothing); 6 external URL(s) recorded and not fetched` |
| `./scripts/ci-required-guard.sh` | **0** | floor ok; `6 fixtures exercised, floor 6`; `7 fixtures exercised, floor 7`; `workflows parsed: 2; 3 action reference(s), every one pinned` |

No tests are skipped — there is no test harness here; these are four assertions,
all four of which executed. Every numeric claim in the builder's PR body
reproduced exactly: 191 requirements / core=141, 4 JSON files, 139 ids across 14
docs, 0 relative links, 6 + 7 fixtures, `features.json` = **343,762 bytes**, 11
distinct non-ASCII characters (`§ ° × – — … ← → ↔ ≤ ≥`), 32 link-shaped strings
= 26 suppressed as code + 6 external, and the trailing-newline asymmetry
(`features.json`, `ui-controls.json`, `release-profiles/core.json` end `7d`;
`release-profiles/full.json` ends `0a`).

## 2. The six demonstrations — reproduced red, then green

Every mutation was proven to have landed by printing a SHA-256 digest of the
target file before and after. The builder's admission that its first pass
mutated nothing in one case is what this guards against; no such case occurred
here.

| # | Mutation | Digest moved | Red | Message | Green on restore |
|---|---|---|---|---|---|
| 1 | `implementation_status` hand-edited in `features.json`, **committed**, tree clean | `25231b84…` → `b53449d3…` | exit **1** | `GENERATED FILE IS NOT REPRODUCIBLE … - docs/quality/features.json` + the diff hunk | exit 0 |
| 2 | `VZ-FOUND-001` title changed in `docs/evidence/ledger-generator/s0_foundation.py`, **committed** without regenerating | src `1fd81a29…` → `ab3040b7…`, ledger untouched | exit **1** | names the file, shows `- "Component repositories exist…" / + "MUTATED TITLE…"` | exit 0 |
| 3 | `VZ-NOSUCH-999` + `VZ-ISSUE-404` appended to `docs/issues/VZ-ISSUE-001.md` | `2e5f3257…` → `9f3d2670…` | exit **1** | both listed with `referenced by docs/issues/VZ-ISSUE-001.md`; `VZ-ISSUE-404: no docs/issues/VZ-ISSUE-404.md exists` | exit 0 |
| 4 | one resolving + one broken relative link in `docs/MILESTONES.md` | `43be9f00…` → `9bb73540…` | exit **1** | `docs/MILESTONES.md:18: [./NO_SUCH_FILE.md] — 'docs/NO_SUCH_FILE.md' does not exist` | exit 0 |
| 4b | broken link removed, **resolving link kept** | — | exit **0** | `relative links: 1 checked across 88 markdown file(s), all resolve` | — |
| 5a | `validate` → `ci-required` in the manifest (other content intact) | `37b48472…` → `4c0c0be2…` | exit **1** | `FLOOR VIOLATION: 'validate' is a non-optional lane…` | exit 0 |
| 5b | manifest emptied of lane lines, comments kept (1374 bytes, 0 lanes) | `37b48472…` → `3ecd168c…` | exit **1** | `EMPTY MANIFEST: … lists no checks.` — **message present, not a silent `set -e` death** | exit 0 |
| 5c | manifest truncated to 0 bytes | — | exit **1** | `.github/required-checks.txt is missing or empty` | exit 0 |
| 6 | `continue-on-error: true` on the **real** `validate` job | `260bbf64…` → `009fcd15…` | exit **1** | `VIOLATION … at=job key=continue-on-error value=literal-true` | exit 0 |
| 6 | `"continue-on-error": true` (quoted key) | → `fcba655e…` | exit **1** | `key="continue-on-error"` | exit 0 |
| 6 | `Continue-On-Error: true` (capitalised) | → `414b7e9f…` | exit **1** | `key=Continue-On-Error` | exit 0 |

Demo 5b specifically confirms the builder's finding 5: the emptied manifest now
produces a named error rather than exit 1 with no output.

## 3. Attacks on the ledger check

**Locale.** With `PYTHONCOERCECLOCALE=0 PYTHONUTF8=0`, `LC_ALL=C LANG=POSIX` and
`LC_ALL=POSIX LANG=C` both yield `locale.getpreferredencoding(False) ==
US-ASCII` on this macOS box. Under all three of `C`/`POSIX`/`C.UTF-8` the fixed
generator exits 0 and produces a **byte-identical** `features.json`
(`25231b84…`), `git diff --quiet` clean.

**The pre-fix generator does fail, and I reproduced it on macOS.** Restoring
`origin/chore/m0-meta-baseline:docs/evidence/ledger-generator/build.py` (the
bare `open(sys.argv[1],"w")`) and running it under `LC_ALL=C LANG=POSIX
PYTHONCOERCECLOCALE=0 PYTHONUTF8=0`:

```
UnicodeEncodeError: 'ascii' codec can't encode character '—' in position 428: ordinal not in range(128)
```

exit 1, leaving a **truncated** `features.json` (`39a536f6…`). The builder's
finding 1 is real and the one-line fix is correct; only its claim that the
failure could not be reproduced on macOS is wrong (see FINDING 4).

**Different Python minor.** `python3.13.13` regenerates byte-identically to
`python3.9.6` and to CI's `3.12.14` (`25231b84…` in all three).

**Generator crash → fails closed.** With the pre-fix generator crashing, the
check prints `GENERATOR FAILED: … exited non-zero.` and exits **1**. Generator
deleted → `MISSING GENERATOR`, exit 1. Generated file deleted → `MISSING
GENERATED FILE`, exit 1.

**Generator writes nothing → passes green.** See FINDING 1.

**Honest regeneration is green.** Source edit + regenerate + commit both →
ledger digest legitimately moves `25231b84…` → `f6a379e6…`, and
`check-generated-ledger.sh` exits **0**, `check-quality-json.py` exits **0**.
The check does not forbid a legitimate ledger change.

**Generated siblings.** `build.py` writes exactly one file. No generator source
produces `ui-controls.json` or `release-profiles/*.json` (the only mentions are
prose inside requirement text in `core.py:51` and `s9_ui_design.py:16`), and
their `notice` fields read "seeded by Prompt 00" / "PROPOSED" — they are
hand-authored. A hand edit to `ui-controls.json` is therefore **not** red from
the regeneration check (exit 0) and only parse-checked by
`check-quality-json.py`. That is correct by design and the builder states it;
the `generated: 2026-09-15` key in those files is a date, not a provenance
claim.

## 4. The dangling-id check

- **Ids inside code spans and fenced blocks ARE checked** — confirmed by design
  (`check-quality-json.py` does no code stripping) and by demo 3, where the
  issue file writes ids in prose. This is the opposite of the link checker,
  deliberately, and the docstring says so.
- **Range and slash forms are NOT expanded** — see FINDING 2.
- **Scope** is `docs/MILESTONES.md` + `docs/issues/*.md`
  (`check-quality-json.py:46`). The war-room board (`docs/plans/WARROOM-BOARD.md`)
  and the 13 other plans under `docs/plans/` are **out of scope**. COMMANDS.md
  enumerates the scope but does not say the exclusion is deliberate. All ids
  currently in `docs/plans/` resolve, so adding the glob would be free today.

## 5. The guard and the fan-in

Every rule was attacked on the **real** workflows, not only on the fixtures:

| Attack on `.github/workflows/validate.yml` | Guard | Reason reported |
|---|---|---|
| `actions/checkout@3d3c42e5…` → `@v7` | exit **1** | `reason=not-a-40-hex-sha` |
| `pull_request: branches: [main]` (the stacked-PR trap) | exit **1** | `reason=base-branch-filter key=branches lanes=validate` |
| `pull_request: branches-ignore: [chore/**]` | exit **1** | `reason=base-branch-filter key=branches-ignore` |
| `pull_request` trigger removed entirely | exit **1** | `reason=not-triggered-on-pull-request lanes=validate` |

YAML is genuinely **parsed**, not grepped, for `continue-on-error` and for pins
and triggers (`check-workflows.py`, `check-action-pins.py`, both via
`yaml.safe_load`, both answering three ways: 0 clean / 1 VIOLATION / 2
UNEVALUABLE). Job *existence*, by contrast, is a grep
(`ci-required-guard.sh`: `grep -qE "^  ${check}:[[:space:]]*$" .github/workflows/*.yml`)
— see FINDING 3's second half.

`ci-required-select.sh`, driven directly with synthetic check-run TSV:

| Row | Exit | |
|---|---|---|
| `completed success` | 0 | pass |
| `completed failure` / `skipped` / `cancelled` / `timed_out` / `neutral` / `action_required` | **1** | all fail closed |
| `in_progress` / `queued` | 2 | pending → polled, then the 1800 s deadline exits 1 |
| lane absent from the run list, and empty run list | 2 | `validate: NEVER RAN` → deadline → exit 1 |
| duplicate name, old FAIL + new SUCCESS | **1** | `AMBIGUOUS — 2 check-runs share this name and their conclusions disagree` |
| duplicate name, old SUCCESS + new FAIL | **1** | `AMBIGUOUS` |
| duplicate name, both success | 0 | `(2 runs with this name, all agreeing)` |
| duplicate name, success + in_progress | 2 | takes the newest by `started_at` |

So on duplicate names it **fails on disagreement** rather than choosing a
winner. A stale success can no longer mask a current failure.

**Residuals confirmed as honestly STATED, not fixed:**

- The PR under test can edit `scripts/ci-required-guard.sh` itself. Stated, in
  those words, in the script's own FLOOR comment.
- `.github/CODEOWNERS` is enforced by nothing. Stated in the file's header, in
  the guard comment, in COMMANDS.md and in the PR body. **Independently
  confirmed:** `gh api repos/yegamble/vizra/rulesets` →
  `403 "Upgrade to GitHub Pro or make this repository public"`. The repository
  is private, owner type User. The claim is true.
- No `make` is involved, so a Makefile `SHELL` override is not applicable. The
  analogous constructs **are** `defaults.run.shell` and step-level `if:` — see
  FINDING 3. Neither appears anywhere in either shipped workflow
  (`grep -nE '^\s*(defaults|shell|if):' .github/workflows/*.yml` → no match), so
  nothing is neutered today.

## 6. Documentation honesty

`docs/quality/COMMANDS.md` lists only commands that exist in this repository and
that I re-ran successfully; each carries an exit code. The PyYAML correction is
accurate and is confirmed by the CI log: the runner shipped **PyYAML 6.0.1** and
the `pyyaml==6.0.3` fallback did not execute — exactly as COMMANDS.md now says.
The `bundle`/`boot` "not built" table matches the manifest and the workflow
comments. One stale count: FINDING 4.

`AGENTS.md`, `docs/META_REPO.md`, the ADRs and `docs/PRODUCT_*` are **not in the
diff**, so nothing there was rewritten to match the implementation. The PR body
overstates nothing I could find; where it is wrong it is wrong *against* itself
(FINDING 4).

## 7. Scope and secrets

`git diff --stat origin/chore/m0-meta-baseline...e667b60` — 34 files,
+2633 / −1, confined to:

```
.github/            CODEOWNERS, required-checks.txt, workflows/{validate,ci-required}.yml
scripts/            5 checkers + testdata/ (13 fixtures)
docs/quality/       COMMANDS.md   (new file only)
docs/evidence/      meta-validate/ (8 transcripts), ledger-generator/build.py (the 10-line encoding fix)
```

Nothing under `docs/adr/`, `.claude/`, `docs/plans/WARROOM-BOARD.md`,
`AGENTS.md`, `CLAUDE.md`, `docs/META_REPO.md`, `docs/PRODUCT_*` or
`docs/MILESTONES.md` was touched.

**Ledger content byte-identical between base and head:**

| File | base | head | |
|---|---|---|---|
| `docs/quality/features.json` | `25231b84…` | `25231b84…` | identical |
| `docs/quality/ui-controls.json` | `7bc463af…` | `7bc463af…` | identical |
| `docs/quality/release-profiles/core.json` | `a86d3b27…` | `a86d3b27…` | identical |
| `docs/quality/release-profiles/full.json` | `ecef0842…` | `ecef0842…` | identical |

**Secrets:** nothing credential-shaped added. The only token reference in the
diff is `GH_TOKEN: ${{ github.token }}` in `ci-required.yml`; every
credential-shaped string in the committed CI transcripts is already `***`-masked
by Actions. `permissions:` is least-privilege on both workflows
(`validate`: `contents: read`; `ci-required`: `contents/checks/actions: read`).
GitGuardian reported success on this SHA.

## 8. CI on `e667b60`

```
gh api repos/yegamble/vizra/commits/e667b60…/check-runs
  ci-required                   completed  success  00:20:21Z → 00:20:48Z
  validate                      completed  success  00:20:21Z → 00:20:31Z
  GitGuardian Security Checks   completed  success
gh run list --commit e667b60…
  35547383413  validate     pull_request  completed  success  ci/meta-validate
  35547383438  ci-required  pull_request  completed  success  ci/meta-validate
```

Exactly one check-run per required name — no duplicates, nothing skipped,
cancelled, timed out or missing. Both were triggered by `pull_request` on the
**stacked** branch `ci/meta-validate`, which is the case a `branches: [main]`
filter would have silently skipped.

**Required-checks manifest vs. what actually ran:** the manifest lists exactly
`validate`; `validate` ran and succeeded. No listed-but-unexecuted lane.

**The ledger check really ran the generator and diffed** — from
`gh run view 35547383413 --log`:

```
validate | record the environment          Python 3.12.14
validate | record the environment          preferred encoding: UTF-8
validate | record the environment          source SHA: e667b605b6c0f7930cea959d9585be17cd519662
validate | the generated ledger …          regenerating with: Python 3.12.14
validate | the generated ledger …          OK 191 requirements; core=141; areas={'foundation': 8, …}
validate | the generated ledger …          generated ledger reproduces byte-for-byte: docs/quality/features.json
validate | quality JSON parses …           json parsed: 4 file(s) under docs/quality/
validate | quality JSON parses …           requirement ids: 139 distinct VZ-… reference(s) across 14 document(s); every one resolves
validate | relative documentation links …  relative links: none exist yet across 88 markdown file(s) (checked nothing); 6 external URL(s) recorded and not fetched
```

The `OK 191 requirements; core=141; areas={…}` line is the real generator's own
stdout, so this was not a no-op.

From `gh run view 35547383438 --log` — `ci-required` genuinely **polled** rather
than asserting:

```
ci-required | ensure a YAML parser …   PyYAML 6.0.1
ci-required | guard the manifest …     the workflow checker rejects every continue-on-error spelling … (6 fixtures exercised, floor 6)
ci-required | guard the manifest …     the pin checker rejects every unpinned-action … (7 fixtures exercised, floor 7)
ci-required | every required check …   evaluating e667b605b6c0f7930cea959d9585be17cd519662
ci-required | every required check …     validate: in_progress
ci-required | every required check …     validate: success
ci-required | every required check …   ci-required: every required check succeeded on e667b605…
```

---

# Findings

```
FINDING 1: a ledger generator that exits 0 without writing anything passes as "reproduces byte-for-byte"
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-generated-ledger.sh:73-95 (regenerate, then `git diff --exit-code`)
             docs/evidence/ledger-generator/build.py
  requirements: VZ-CI-001 (fan-in/required checks); guards AGENTS.md § Engineering
                guardrails "never hand-edit generated files"

Observed:
  The check runs the generator and then asserts `git diff --exit-code` over the
  declared file list. It never asserts that the generator actually WROTE those
  files. Replacing build.py with a two-line no-op that prints the expected
  banner and exits 0:

      $ printf 'import sys\nprint("OK 191 requirements; core=141")\n' \
          > docs/evidence/ledger-generator/build.py
      $ ./scripts/check-generated-ledger.sh
      regenerating with: Python 3.9.6
      OK 191 requirements; core=141
      generated ledger reproduces byte-for-byte: docs/quality/features.json
      EXIT=0

  The "nothing else moved" assertion compares `git status --porcelain -- docs/quality`
  before and after, which is also unchanged when nothing is written, so it does
  not catch this either. The adjacent failure modes DO fail closed: generator
  missing → MISSING GENERATOR exit 1; generator crashes → GENERATOR FAILED exit 1;
  generated file deleted → MISSING GENERATED FILE exit 1.

Failure:
  The lane's primary check prints a confident reproduction claim while nothing
  was regenerated. A build.py gutted to an early return — deliberately, or by a
  refactor that drops the write path behind a condition — makes the ledger gate
  vacuous, and the success message actively asserts the opposite. This is the
  false-positive-CI class AGENTS.md § Code review rules tells reviewers to hunt,
  and it is the one hole in this slice the PR body does not state. Every other
  anti-false-green case here is handled explicitly (fixture floors, UNEVALUABLE
  vs VIOLATION, empty-glob refusal, "checked nothing" reporting).

Perspective:
  developer, operator

Recommendation:
  Delete the declared generated files before regenerating, so a generator that
  writes nothing leaves a deletion in the diff:

      rm -f "${generated[@]}"
      ( cd "$generator_dir" && python3 build.py ../../quality/features.json ) || { … }
      # existing `git diff --exit-code` now goes red on the missing file

  A content-hash-before/after comparison works equally well. Two lines either way.

Acceptance criteria:
  - `check-generated-ledger.sh` exits non-zero, naming the file, when the
    generator exits 0 without writing any declared file.
  - The existing six demonstrations stay red-for-their-reason and green on restore.
  - Honest regeneration (source edit + regenerate + commit both) stays exit 0.

Tests:
  No harness exists in this repo yet. The smallest addition is a seventh
  transcript under docs/evidence/meta-validate/ using the no-op build.py above,
  in the same red/restore/green shape as demos 1-6. Longer term this belongs in
  the same negative-fixture idiom as scripts/testdata/, driven from
  ci-required-guard.sh so the checker is proven on every run rather than once.

Cross-repo implications:
  core: none | user: none | search: none
  meta: the same pattern (regenerate + `git diff --exit-code`) is the intended
  shape for the future sqlc/OpenAPI regeneration lanes in vizra-core; fixing it
  here fixes the template before it is copied.

Challenge:
  Reaching this requires editing build.py, which is a CODEOWNERS path, is fully
  visible in the diff, and is the same trust class as the "this guard script is
  itself checked out from the PR under test" residual the builder DOES state.
  The CI log also prints the real generator's `areas={…}` stdout, which a gutted
  generator would have to forge. So the practical exposure is low — but the
  stated residual covers the guard, not the generator, and a reader of the PR
  body would believe this check is airtight.
```

```
FINDING 2: only the first id of a range or slash-list is resolved, and that is not stated
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-quality-json.py:48 (ID_PATTERN)
             docs/MILESTONES.md:7,10,11,12,13
             docs/issues/VZ-ISSUE-001.md:4
  requirements: VZ-CI-001; the ids it guards are the whole VZ-… ledger

Observed:
  ID_PATTERN = r"\bVZ-[A-Z0-9]+(?:-[A-Z]+)*-\d+\b" matches one id and stops.
  MILESTONES.md writes ranges and slash-lists in nine places:

      VZ-FOUND-001…008, VZ-CI-001/002/004, VZ-TOPOLOGY-001…003/006/007
      → the checker sees only ['VZ-FOUND-001', 'VZ-CI-001', 'VZ-TOPOLOGY-001']

  Mutating docs/MILESTONES.md (digest 43be9f00… → 6c973c26…):
      VZ-FOUND-001…008  →  VZ-FOUND-001…999   ./scripts/check-quality-json.py → EXIT 0
      VZ-CI-001/002/004 →  VZ-CI-001/888      ./scripts/check-quality-json.py → EXIT 0

  Neither the script docstring nor docs/quality/COMMANDS.md mentions range or
  slash-list expansion, so a reader takes "every VZ-… id referenced by
  docs/MILESTONES.md … names a requirement" at face value.

  Scope is a second, smaller version of the same gap: REFERENCING_GLOBS is
  ["docs/MILESTONES.md", "docs/issues/*.md"] (check-quality-json.py:46).
  docs/plans/ — 13 plans plus WARROOM-BOARD.md — is out of scope, and COMMANDS.md
  enumerates the scope without saying the exclusion is deliberate. Every VZ id
  currently in docs/plans/ resolves, so widening the glob costs nothing today.

Failure:
  The M0 row schedules VZ-FOUND-001…008 and only VZ-FOUND-001 is validated. If
  VZ-FOUND-005 were renamed or dropped — the exact owner-decision violation the
  check exists to catch — the milestone plan would keep pointing at nothing and
  the lane would stay green. docs/plans/ spells VZ-FOUND-002…008 out
  individually, but docs/plans/ is not checked, so nothing catches it there
  either.

Perspective:
  developer, business (milestone planning reads from these rows)

Recommendation:
  Either expand the forms, or say they are not expanded. Expanding is small:
  after matching a full id, consume a trailing `(?:[…/]\d+)+` run and resolve
  each numeric suffix against the same prefix. If expansion is deliberately out
  of scope for this slice, one sentence in the check-quality-json.py docstring
  and one row in COMMANDS.md turns an unknown gap into a recorded decision —
  which is the standard the rest of this PR holds itself to (cf. finding 2 on
  trailing newlines, which was recorded rather than fixed).

Acceptance criteria:
  - `VZ-FOUND-001…999` in docs/MILESTONES.md is red, naming VZ-FOUND-999.
  - `VZ-CI-001/888` is red, naming VZ-CI-888.
  - The nine existing range/slash rows stay green unchanged.
  - Or: COMMANDS.md and the docstring state that only the leading id of a range
    is resolved, and why.

Tests:
  A transcript under docs/evidence/meta-validate/ mutating a range endpoint,
  same red/restore/green shape as demo 3.

Cross-repo implications:
  core: none | user: none | search: none | meta: none

Challenge:
  A range is arguably prose shorthand, not a reference, and expanding it invents
  ids the document never literally wrote — a reader might reasonably say
  docs/plans/ is where individual ids belong and MILESTONES.md rows are summary.
  That is a defensible position; it is just not the position the check's own
  docstring takes, and it is not written down anywhere.
```

```
FINDING 3: continue-on-error is caught in five spellings, but two simpler ways to neuter a lane are unchecked and unstated
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-workflows.py (FORBIDDEN = "continue-on-error" only)
             scripts/ci-required-guard.sh:151 (job existence by grep, .yml only)
             .github/workflows/validate.yml
  requirements: VZ-CI-001

Observed:
  Inserting a workflow-level `defaults: run: shell:` that swallows non-zero
  exits, and separately a step-level `if: false` on the ledger check:

      defaults:
        run:
          shell: bash -c "eval "$@" || true" --
      → ./scripts/ci-required-guard.sh EXIT=0   (not caught)

      - name: the generated ledger matches its sources
        if: false
        run: ./scripts/check-generated-ledger.sh
      → ./scripts/ci-required-guard.sh EXIT=0   (not caught)

  Neither construct exists in either shipped workflow:
  `grep -nE '^\s*(defaults|shell|if):' .github/workflows/*.yml` → no match. A
  skipped JOB is still caught downstream (ci-required-select.sh refuses
  `skipped`), but a skipped STEP leaves the job green.

  Separately, the job-existence check is the one rule in the guard that is a
  grep rather than a parse:
      grep -qE "^  ${check}:[[:space:]]*$" .github/workflows/*.yml
  It is indentation-sensitive and matches only *.yml, while check-workflows.py
  and check-action-pins.py both glob *.yml and *.yaml. A required lane defined
  in a .yaml workflow would be reported as having no job.

Failure:
  Nothing is wrong today. But the guard's stated promise — "a lane that cannot
  fail is not a gate" — is enforced against one key in five spellings while two
  strictly simpler ways to disable the same check go unmentioned. The builder
  states the analogous residual for CODEOWNERS and for the guard being
  self-editable; this one is neither closed nor stated.

Perspective:
  developer

Recommendation:
  Cheapest honest fix is one sentence in ci-required-guard.sh's comment header
  naming `defaults.run.shell` and step-level `if:` as unchecked residuals of the
  same class as self-editing. Closing them is also small: add "defaults" and a
  step-level "if" to check-workflows.py's forbidden set for required lanes, and
  align the job-existence grep to *.yml + *.yaml (or parse it, as the other two
  checkers do).

Acceptance criteria:
  - Either ci-required-guard.sh exits 1 on a `defaults.run.shell` override and on
    a step-level `if:` in a required lane's workflow, or the header comment names
    both as known-unchecked with the reason.
  - The job-existence check finds a required lane defined in a .yaml workflow.

Tests:
  Two more fixtures in scripts/testdata/ in the existing wf-*.yml idiom, each
  declaring the rule it trips, so ci-required-guard.sh exercises them on every
  run and the fixture floor moves 5 → 7 deliberately.

Cross-repo implications:
  core: none | user: none | search: none
  meta: the component repos' own ci-required guards should carry the same rule set.

Challenge:
  Both vectors require editing the workflow in the PR under test, which is
  exactly the trust boundary the builder already declares open ("this script is
  also checked out from the PR under test"). So arguably these are already
  covered by the stated residual and adding more keys is whack-a-mole against an
  adversary who can edit the gate anyway. The asymmetry is still odd enough to
  be worth one sentence.
```

```
FINDING 4: two small documentation inaccuracies, both against the builder's own interest
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/quality/COMMANDS.md (§ "3. Relative documentation links resolve")
             PR #3 body, § Findings item 1
  requirements: none

Observed:
  (a) COMMANDS.md records the link check's last run as
      `relative links: none exist yet across 87 markdown file(s)`.
      At this SHA the command reports **88**, both locally and in the CI log
      (`gh run view 35547383413 --log`). The recorded run predates COMMANDS.md
      adding itself to the corpus.

  (b) The PR body says of the locale bug: "I could not reproduce the failure
      locally: macOS always reports UTF-8 regardless of LC_ALL." That is not so.
      With `LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0`,
      `locale.getpreferredencoding(False)` returns `US-ASCII` on macOS 26.5.1,
      and the pre-fix build.py from origin/chore/m0-meta-baseline raises
      `UnicodeEncodeError: 'ascii' codec can't encode character '—'` and
      leaves a truncated features.json. PYTHONCOERCECLOCALE (PEP 538) is what
      masks it by default.

Failure:
  (a) is a stale count in a file whose whole purpose is that recorded numbers
  can be trusted. (b) understates the builder's own finding: the bug was not
  fixed "by inspection", it is directly demonstrable, and the fix is verified
  correct (byte-identical output under C, POSIX, C.UTF-8, and under Python
  3.9/3.12/3.13).

Perspective:
  developer

Recommendation:
  Update the count to 88. Replace the "could not reproduce" sentence with the
  reproduction above, or simply drop the claim — the fix stands either way.

Acceptance criteria:
  - COMMANDS.md's recorded link-check output matches the command's output at the
    merged SHA.
  - No claim in the PR body that a reproducible failure could not be reproduced.

Tests:
  n/a — documentation.

Cross-repo implications:
  core: none | user: none | search: none | meta: none

Challenge:
  Both are cosmetic and neither affects whether the gate works. (a) will go
  stale again the next time a markdown file is added, which is an argument for
  not quoting a file count in prose at all.
```

## Process notes (not findings)

- The builder's execution plan `docs/plans/2026-09-21-meta-validate-lane.md`
  exists only as an **untracked** file in the chair's main checkout; it is not
  committed to PR #3 (`git cat-file -e e667b60:docs/plans/…` → absent; 14 plan
  files are tracked, this is not one). AGENTS.md § Required workflow point 5
  expects the execution plan updated alongside the slice. Worth the chair's
  attention when committing the board tick.
- `docs/quality/ui-controls.json` declares `control_count: 59` and carries
  exactly 59 controls today, but nothing asserts that invariant — the siblings
  are parse-checked only. A one-line assertion in `check-quality-json.py` would
  cover it.
- Running the generator leaves an untracked `docs/evidence/ledger-generator/__pycache__/`
  which `.gitignore` does not cover. Harmless on a fresh CI checkout; noise
  locally.
- `ci-required-select.sh` reports AMBIGUOUS (red) when a re-run produces a second
  check-run whose conclusion differs from the first. GitHub normally updates the
  existing check-run rather than adding one, so this should rarely bite, and it
  errs closed. Noted so it is not a surprise if a re-run ever stays red.

---

## Verdict

**PASS.**

- All three `validate` checks and the `ci-required` guard reproduce from a clean
  clone at `e667b60`, exit 0, with every count matching the PR body exactly.
- All six demonstrations reproduce red-for-the-stated-reason and green on
  restore, each with a digest proving the mutation landed — including both the
  non-empty and emptied manifest cases and all three `continue-on-error`
  spellings on the real `validate` job.
- The ledger check survives locale, Python-minor-version, crash, missing-file
  and missing-generator attacks, and correctly permits honest regeneration.
- `validate` and `ci-required` both executed and concluded `success` on this SHA
  on `ubuntu-24.04`, triggered by `pull_request` on the stacked branch; the
  manifest matches the jobs that ran; the logs show the generator really ran and
  the fan-in really polled.
- No ledger content, ADR, board or agent-config change; no secrets; scope as
  declared.
- The four findings are SHOULD × 2 and NIT × 2. None falsifies an acceptance
  bullet and none blocks the merge. FINDING 1 and FINDING 2 are real unstated
  gaps in what the lane guarantees and should be closed in a follow-up slice.

PASS is not a merge and does not make any ledger entry VERIFIED — the chair
records those.

Verified by an independent verifier that did not write this code.
