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

---

# Re-verification at `5dfa75c`

**Verdict: PASS.** Findings 1–4 **all CLOSED**. Four new findings (1 SHOULD,
3 NIT), none blocking.

| | |
|---|---|
| Head SHA verified | `5dfa75ca1453f390cea1da1a7bd9accbfd641cb3` |
| Head confirmed unmoved | `gh api repos/yegamble/vizra/git/ref/heads/ci%2Fmeta-validate` → `5dfa75ca…` |
| Previous verdict SHA | `e667b605…` — **confirmed an ancestor** (`git merge-base --is-ancestor` → true): history extended, not rewritten |
| New commits | `4b22690` close the ledger false green, expand id ranges, harden the lane guard · `cd1188d` do not claim "every one resolves" when a reference could not be read · `dd31782` nine transcripts · `5dfa75c` Linux CI transcripts |
| Clone | fresh from GitHub into scratch; builder's worktree untouched; no branch switch in the main checkout |
| Date | 2026-09-21 |

**Ledger invariant holds.** All four quality JSON files byte-identical to
`origin/chore/m0-meta-baseline`: `features.json` `25231b84…`, `ui-controls.json`
`7bc463af…`, `release-profiles/core.json` `a86d3b27…`,
`release-profiles/full.json` `ecef0842…`. The delta since `e667b60` touches only
`scripts/`, `scripts/testdata/`, `docs/quality/COMMANDS.md` and
`docs/evidence/meta-validate/`. `.github/`, `docs/evidence/ledger-generator/build.py`,
`ci-required-select.sh`, `check-workflows.py`, `check-action-pins.py` and
`check-doc-links.py` are **unchanged since `e667b60`** — so everything I verified
about them still stands. Zero credential-shaped lines added.

**Nothing weakened.** Failure-exit counts rose (`check-generated-ledger.sh` 6→13,
`ci-required-guard.sh` 22→32); `check-quality-json.py` keeps all 8 `fail()`
calls; fixture floors are declared 5 / 6 / 5 with 20 fixtures on disk (6 `wf-*`,
7 `pin-*`, 7 `lane-*`). No floor lowered, no assertion deleted, no baseline moved.

## Lane at `5dfa75c` (clean clone, Python 3.9.6, PyYAML 6.0.3, no Docker)

| Command | Exit | Reported |
|---|---|---|
| `./scripts/check-generated-ledger.sh` | **0** | `locale regression: re-running under LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0` → `generated ledger reproduces byte-for-byte: docs/quality/features.json (UTF-8 and C/POSIX locales)` |
| `./scripts/check-quality-json.py` | **0** | `requirement ids: 191 written reference(s) expanded to 287 id(s), 204 distinct, across 14 document(s); every one resolves` |
| `./scripts/check-doc-links.py` | **0** | `relative links: none exist yet across 88 markdown file(s) (checked nothing); 6 external URL(s)` |
| `./scripts/ci-required-guard.sh` | **0** | + `lane integrity: 1 required lane(s) defined by a real job across 2 workflow file(s); no shell override, no conditional step` and `the lane checker rejects … (7 fixtures exercised, floor 7)` |

## FINDING 1 — CLOSED

`check-generated-ledger.sh` now `rm -f`s the declared files before regenerating,
then requires each to exist, be non-empty and parse before the diff.

| Attack | Exit | Message |
|---|---|---|
| **my exact no-op generator** from the `e667b60` report | **1** | `GENERATOR WROTE NOTHING: 'docs/quality/features.json' … It was removed before regeneration, so the generator did not write it.` |
| writes a zero-byte file | **1** | `GENERATOR WROTE AN EMPTY FILE` |
| writes truncated/invalid JSON | **1** | `GENERATOR WROTE INVALID JSON` |
| writes only *some* declared files (2nd file declared, generator writes 1) | **1** | `GENERATOR WROTE NOTHING: 'docs/quality/ui-controls.json'` |
| writes an **extra undeclared** file (first run) | **1** | `UNDECLARED GENERATED FILE: … 'docs/quality/EXTRA-generated.json'` |
| **honest regeneration** (source edit + regenerate + commit both) | **0** | still green — a legitimate ledger change is not forbidden |

**`rm -f` cannot destroy a hand-maintained file.** The declared list is exactly
`docs/quality/features.json`. `build.py` has a single `open(…, "w")` — `sys.argv[1]`
(line 64) — and no generator source opens `ui-controls.json` or
`release-profiles/*.json` for writing. Those three siblings are never deleted.
A residual ergonomic hazard: when the generator fails, the script exits 1 with
`features.json` **deleted**; it prints `Restore the removed file(s) with:
git checkout -- docs/quality/features.json` at every such exit. Harmless in CI
(ephemeral checkout), a footgun locally, and documented.

Residual on the "both directions" claim → FINDING 6.

## FINDING 2 — CLOSED

Ranges (`…`, `...`, `–`, `—`) and slash-lists now expand, and every member
resolves. `139 distinct` → `191 written references expanded to 287 ids, 204
distinct`.

Expansion is **exact** (probed against the real `expand_reference`):

```
VZ-TOPOLOGY-001…003/006/007  -> 001 002 003 006 007          (exactly, as required)
VZ-FOUND-001…008             -> 001 002 003 004 005 006 007 008
VZ-CI-001/002/004            -> 001 002 004
VZ-MEDIA-002/005…010         -> 002 005 006 007 008 009 010
VZ-STORAGE-002…006/014/015   -> 002 003 004 005 006 014 015
VZ-AP-001...004 / 001–004 / 001—004  -> 001 002 003 004      (all three separators)
```

**Not over-eager** on the two cases asked for:

```
"see VZ-FOUND-001. Next sentence"  -> [VZ-FOUND-001]   (sentence period does not start a range)
"see VZ-FOUND-001.  5 items"       -> [VZ-FOUND-001]
"docs/VZ-FOUND-001/notes"          -> [VZ-FOUND-001]   (path slash does not start a range)
```

In real documents:

| Mutation (digest before → after) | Exit | Message |
|---|---|---|
| `VZ-FOUND-001…008` → `…999` (`43be9f00…`→`6c973c26…`) | **1** | `IMPLAUSIBLE RANGE: … names 999 ids … the cap is 200` |
| `VZ-FOUND-008…001` (descending) | **1** | `UNREADABLE RANGE: … ends at 001 but starts at 008` |
| `VZ-CI-001/002/004` → `VZ-CI-001/888` | **1** | `VZ-CI-888: not in docs/quality/features.json` |
| **`VZ-FOUND-005` deleted from the ledger** (the failure invisible at `e667b60`) | **1** | `VZ-FOUND-005: not in … referenced by docs/MILESTONES.md / docs/issues/VZ-ISSUE-001.md` |

**Hand spot-check, five ids that exist only as expanded members** — none is
written literally anywhere in `docs/MILESTONES.md`, and all five are real ledger
entries, so the expansion is doing genuine new work: `VZ-FOUND-005`,
`VZ-TOPOLOGY-002`, `VZ-STORAGE-004`, `VZ-AP-003`, `VZ-SERVICES-004`.

A narrow over-expansion remains → FINDING 8.

### The builder's refusal to widen the scope to `docs/plans/` — facts confirmed, call endorsed

Every fact the builder gives checks out:

- `docs/plans/WARROOM-BOARD.md:48` reads: *"2b | meta: evaluate the security
  reviewer's four proposed requirement IDs (VZ-SEC-SSR-001, VZ-SEC-HDR-001,
  VZ-SEC-SSR-002, VZ-SEC-SUPPLY-001) against existing VZ-SECURITY-* / VZ-CI-*
  entries…"*. All four are in the board and **none** is in `features.json`. They
  dangle because the row's purpose is to decide whether to create them.
- The **13 slice plans are clean** — I resolved every `VZ-…` id in
  `docs/plans/*.md` against the ledger, the issue files and the `VZ-SLICE-`
  allowlist; the only unresolved ids in the whole directory are those four, all
  in `WARROOM-BOARD.md`.
- `docs/evidence/` does quote deliberately-bad ids: `VZ-NOSUCH-999` (×2),
  `VZ-CI-001/888` (×2), `VZ-FOUND-001…999` (×3). Gating it would make every
  red/green transcript a lane failure.

**Verdict on the call: the refusal is correct and well-reasoned.** Excluding
`docs/evidence/` is plainly right — a demonstration must be able to write down
the id it made dangle. Excluding `docs/plans/` is right *as stated*, because a
plan proposing a requirement must not turn the gate red. A narrower rule is
genuinely available — the 13 slice plans are clean today, so gating
`docs/plans/*.md` while exempting `WARROOM-BOARD.md`, or requiring proposed ids
to carry a marker, would catch a typo in a slice plan at no cost. But that is a
**scope addition, not a defect**: the builder measured both exclusions, wrote
them into the script docstring and into a COMMANDS.md table, and named the
honest way in ("a marker distinguishing 'proposed' from 'referenced', not a
wildcard exemption"). That meets the AGENTS.md standard for a recorded decision.
I would not hold the merge for it; it is a good candidate for the follow-up.

**COMMANDS.md now states exactly which paths are checked and why the rest are
not** — a four-row table at § "Scope of the id check, and what is deliberately
excluded", naming both excluded directories, the four proposed ids by name, and
the sentence "Both exclusions were measured, not assumed."

## FINDING 3 — CLOSED

New `scripts/check-lane-integrity.py`. Run individually, each fixture trips its
own declared reason:

| Fixture | Exit | Reason |
|---|---|---|
| `lane-clean.yml` | 0 | accept |
| `lane-yaml-extension.yaml` | 0 | accept — **the `.yaml` extension is the point** |
| `lane-workflow-shell.yml` | 1 | `defaults-shell-override` |
| `lane-job-shell.yml` | 1 | `defaults-shell-override` |
| `lane-if-false.yml` | 1 | `constant-false-if` |
| `lane-if-expression.yml` | 1 | `conditional-step-on-required-lane` |
| `lane-missing-job.yml` | 1 | `no-such-job` |

Floor declared `expected_lane_fixtures=5` + 2 accept = the `7 fixtures
exercised, floor 7` the guard prints. Job existence is now parsed from YAML over
`*.yml` **and** `*.yaml`, replacing the indentation-sensitive grep.

The four probes requested, on the real `validate` lane:

| Probe | Caught | Stated as out of scope |
|---|---|---|
| **job-level `if:`** on the required lane | no | **yes** — docstring: *"(Job-level `if:` is left to the fan-in, which already refuses a skipped job.)"* The delegation is sound: I confirmed at `e667b60` that `ci-required-select.sh` exits 1 on a `skipped` conclusion. |
| **step-level `shell:`** on the ledger-check step | **no** | **no** → FINDING 7 |
| required lane moved into a **reusable workflow** (`jobs.validate.uses:`) | **no** | no → FINDING 7 |
| **`runs-on: [self-hosted, attacker-box]`** | **no** | no → FINDING 7 |

## FINDING 4 — CLOSED

The PR body no longer claims the locale failure is unreproducible; it now says
*"**That was incorrect.**"* and gives the reproduction, crediting PEP 538's
C-locale coercion as the mask. The hard-coded markdown count is gone from
COMMANDS.md, which explains *why* no number replaced it: *"A number that goes
stale on its own is worse than no number in a file whose purpose is that
recorded figures can be trusted. Run the command for the current value."*

**The locale invocation runs in the lane** — precisely, it is a block inside
`scripts/check-generated-ledger.sh:167-199`, which the lane's *"the generated
ledger matches its sources"* step runs. It is not a separate workflow step
(`.github/` is unchanged since `e667b60`); the PR body's "that exact invocation
is now a step of the lane" is loose wording for a true fact. Confirmed executing
in CI at this SHA:

```
validate | the generated ledger matches its sources   locale regression: re-running under LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0
validate | the generated ledger matches its sources   generated ledger reproduces byte-for-byte: docs/quality/features.json (UTF-8 and C/POSIX locales)
```

**With the encoding fix reverted, that step goes RED.** Restoring
`origin/chore/m0-meta-baseline:build.py` (the bare `open(sys.argv[1],"w")`) and
running the check on this host: exit **1**, `UnicodeEncodeError: 'ascii' codec
can't encode character '—' in position 428`, caught as `GENERATOR FAILED`.
**On Linux, by reading the workflow:** the runner reports `preferred encoding:
UTF-8` (recorded in the CI log), so the *first* regeneration would succeed — but
the locale block then re-runs the generator under `LC_ALL=C LANG=POSIX
PYTHONCOERCECLOCALE=0 PYTHONUTF8=0`, which forces `getpreferredencoding` to
ASCII on CPython regardless of platform, so the pre-fix `open()` raises there and
the block's `LOCALE REGRESSION: the generator failed under a C/POSIX locale`
branch fires. The check is therefore host-independent, which is the point of it.

## Success lines on failing runs

The Finding-5 self-report is closed: a reference that could not be read now
prints *"191 written reference(s), 280 id(s) expanded and resolved, but at least
one reference could not be read — see the failure(s) above"* and **never**
`every one resolves`. The two statements cannot co-occur — confirmed on both the
descending-range and implausible-range mutations.

Audited all five scripts under forced failure for a leaked overall-success line.
Clean, with one thing worth naming precisely: `ci-required-guard.sh` prints its
earlier **per-assertion** lines (`no continue-on-error on any job or step`,
`every one pinned`, `floor: every non-optional lane is present`) before a later
sub-check fails. Those are true statements about assertions that genuinely
passed, each naming its own scope, and the script still exits 1 with no line
claiming the run succeeded. That is not the Finding-5 defect, which was one
check contradicting itself about the same object.

## The nine demonstrations, re-run with digests

| # | Mutation | Digest before → after | Exit |
|---|---|---|---|
| 1 | hand-edited `features.json`, committed | `25231b8411f7` → `b53449d33c6e` | **1** |
| 2 | generator source changed, not regenerated, committed | `b7a4927f0551` → `83067fdad4a6` | **1** |
| 3 | `VZ-NOSUCH-999` + `VZ-ISSUE-404` in an issue file | `2e5f32570e45` → `0ecabc6f80be` | **1** |
| 4 | broken relative link beside a resolving one | `43be9f00a91e` → `a555814b22ef` | **1** |
| 5 | floor lane removed / manifest emptied | `37b484721324` → `4c0c0be25382` / `3ecd168c47f2` | **1** / **1** |
| 6 | `continue-on-error` ×3 spellings | `009fcd15f48b` / `fcba655e5900` / `414b7e9f72e5` | **1** ×3 |
| 7 | generator wrote nothing / empty / partial / invalid JSON | — | **1** ×4 |
| 8 | range + slash-list expansion (4 mutations) | `6c973c269b92` etc. | **1** ×4 |
| 9 | shell override ×2, `if: false`, non-constant `if:`, missing job | — | **1** ×5 |

All four lane scripts green again after every restore; tree clean.

## CI on `5dfa75c`

```
ci-required   completed  success  00:44:57Z → 00:45:24Z
validate      completed  success  00:44:57Z → 00:45:03Z
GitGuardian   completed  success
35548669403  validate     pull_request  success  ci/meta-validate
35548669385  ci-required  pull_request  success  ci/meta-validate
```

One check-run per required name; manifest lists exactly `validate`; nothing
skipped, cancelled, timed out or missing. Logs confirm the generator ran
(`OK 191 requirements; core=141`), the locale block ran (quoted above), the id
expansion ran (`191 written reference(s) expanded to 287 id(s), 204 distinct …
every one resolves`), the lane-integrity check ran (`lane integrity: 1 required
lane(s) … no shell override, no conditional step`), and the fan-in genuinely
polled (`validate: in_progress` → `validate: success` → `ci-required: every
required check succeeded on 5dfa75ca…`).

---

# New findings at `5dfa75c`

```
FINDING 5: CI validates the PR MERGE commit, not the head SHA, and the provenance step records the wrong one
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     .github/workflows/validate.yml:45-68 (checkout with no `ref:`; "record the environment")
             .github/workflows/ci-required.yml:136-141 (HEAD_SHA = pull_request.head.sha)
             docs/quality/COMMANDS.md; PR #3 body
  requirements: VZ-CI-001

Observed:
  The link check reports 88 markdown files and 6 external URLs in a clean clone
  at 5dfa75c, but 92 and 7 in the CI log for the same SHA. Not an interpreter
  difference — Python 3.9.6 and 3.13.13 both count 88 on this tree. The CI log
  settles it:

      [command]/usr/bin/git checkout --progress --force refs/remotes/pull/3/merge
      HEAD is now at e85e875 Merge 5dfa75ca1453f390cea1da1a7bd9accbfd641cb3 into 5f0cd6631fc5e19d17ab0d25f806df0a68582841

  `actions/checkout` with no `ref:` on a `pull_request` event checks out
  refs/pull/N/merge. The base branch has advanced four commits since the
  merge-base (war-room ticks 60-63), adding four markdown files — including this
  very evidence file — so the merge tree carries 92. Meanwhile:

      validate | record the environment   source SHA: 5dfa75ca1453f390cea1da1a7bd9accbfd641cb3

  printed while standing in tree e85e875. The step designed to record provenance
  records a SHA that is not the tree it is describing.

  ci-required is unaffected in its polling: HEAD_SHA is
  `github.event.pull_request.head.sha` = 5dfa75c, which is where the check-runs
  are attributed, so the fan-in reads the right rows.

Failure:
  Two concrete consequences.

  (1) The owner's merge rule (AGENTS.md § Merge authorization) reads "ci-required
  is green on the verified SHA" and "the head has not moved since the verdict".
  Both are satisfied here — but what `validate` actually executed against is a
  tree the verifier never verified, and it changes whenever the BASE branch
  moves, with no change to the PR and no signal to anyone. A war room that ticks
  the board on every cycle moves that base constantly. Green can become red (or
  red green) between the verdict and the merge without the head moving at all.

  (2) It already produced a wrong number in the PR body: "At this SHA the command
  reports 92." At this SHA the command reports 88. 92 is the merge tree's count.
  This is the third iteration of the same class of error the same round closed as
  FINDING 4 — a figure read off a corpus that is not the one named.

Perspective:
  developer, operator, business (the merge rule is what this slice exists to serve)

Recommendation:
  One line in the "record the environment" step, so the transcript names the tree
  it tested:

      echo "checked-out tree: $(git rev-parse HEAD)"
      echo "PR head SHA:      ${{ github.event.pull_request.head.sha || github.sha }}"

  Then one paragraph in COMMANDS.md (and ideally in AGENTS.md § Merge
  authorization, which is an owner edit and out of scope here) stating that on
  `pull_request` the lane validates the merge result, so a green ci-required
  attests to head-merged-into-base-as-of-that-run, not to the head tree alone.
  Do NOT "fix" this by pinning checkout to the head SHA: testing the merge result
  is the more useful behaviour. The defect is that it is unrecorded, not that it
  happens.

Acceptance criteria:
  - The validate log names both the checked-out tree SHA and the PR head SHA,
    and they are visibly different on a stacked PR whose base has moved.
  - COMMANDS.md states which tree the lane validates on `pull_request` and on
    `merge_group`.
  - No document quotes a count taken from the merge tree as if it were the head's.

Tests:
  No harness exists. The smallest check is a transcript recording both SHAs from
  one real run where they differ — which is every run of this PR right now.

Cross-repo implications:
  core: none | user: none | search: none
  meta: every component repo's ci-required inherits this; the chair's merge
  procedure should record the tree SHA alongside the head SHA in the board tick.

Challenge:
  This is stock GitHub behaviour that this PR did not introduce, and testing the
  merge result is what a merge gate SHOULD do — arguably the head-only tree is
  the less interesting one. Fair. But the lane ships a step whose entire job is
  to record what was tested, and it records something else; and the discrepancy
  has already put a wrong number in the PR body, which is how I found it.
```

```
FINDING 6: the undeclared-output check is a change detector, so "equal in both directions" is overstated
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-generated-ledger.sh:137-158 (before/after `git status --porcelain -- docs/quality`)
             PR #3 body, FINDING 1 paragraph
  requirements: VZ-CI-001

Observed:
  The PR body says: "With the existing undeclared-file check, the declared list
  and the generator's real output set are asserted equal in **both** directions."
  The first direction is genuinely asserted — every declared file must exist,
  be non-empty and parse after regeneration. The second is not: it compares
  `git status --porcelain -- docs/quality` before and after the run, which sees
  only files whose status CHANGES during the run.

      A4a  extra undeclared file, first run (file appears)   -> EXIT 1, UNDECLARED GENERATED FILE
      A4b  same file left over from the previous run         -> EXIT 0, "reproduces byte-for-byte"
      A4c  same file COMMITTED, tree clean (the CI state)    -> EXIT 0, "reproduces byte-for-byte"

  In A4c the generator writes docs/quality/EXTRA-generated.json on every run, the
  committed bytes already match, `before == after`, and the file is never named,
  never diffed and not in the declared list — so it is neither covered by the
  reproduction assertion nor by the locale re-check. (A subsequent hand-edit of it
  IS caught, incidentally: the generator then rewrites it, the status changes, and
  the before/after comparison fires.)

Failure:
  A second generated file can enter docs/quality/ and sit there permanently
  outside the gate. Narrow — but the claim in the PR body is what a reviewer
  would rely on to decide the ledger gate needs no further thought, and it is not
  true in the steady state that CI actually runs in.

Perspective:
  developer

Recommendation:
  Compare content, not status. Before deleting, record a hash for every file
  under docs/quality/; after regenerating, require that the set of files whose
  hash or mtime changed is a subset of the declared list. That catches a
  steady-state rewrite, which the status diff cannot see by construction.
  Alternatively, soften the PR body sentence to match what the code does.

Acceptance criteria:
  - An undeclared file that the generator rewrites identically on every run is
    reported by name, on a clean tree, with the file already committed.
  - The existing six ledger attacks stay red and honest regeneration stays green.

Tests:
  A tenth transcript under docs/evidence/meta-validate/ using the A4c state:
  generator extended to write a second file, that file committed, tree clean,
  check run.

Cross-repo implications:
  core: none | user: none | search: none
  meta: same pattern is intended for the future sqlc/OpenAPI regeneration lanes.

Challenge:
  Adding a second generated file requires editing build.py — a CODEOWNERS path,
  visible in the diff — and the first run after adding it IS caught, so the
  window is "someone adds it, sees it caught, commits it anyway, and nobody reads
  the diff". Low exposure. The finding is really about the sentence in the PR
  body, not the code.
```

```
FINDING 7: three more ways to neuter a required lane are unchecked, and unlike job-level `if:` they are not stated
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-lane-integrity.py (shell_override covers defaults.run.shell only)
             scripts/check-action-pins.py:walk_uses (local `./` refs exempt from pinning)
  requirements: VZ-CI-001

Observed:
  Probed on the real validate lane; each mutation left ci-required-guard.sh at
  EXIT 0:

  (a) STEP-level `shell:` —
          - name: the generated ledger matches its sources
            shell: bash -c "eval \"$@\" || true" --
            run: ./scripts/check-generated-ledger.sh
      This is the same neutering the checker exists to refuse, one line, on the
      exact step, and `defaults.run.shell` is refused at workflow AND job level
      while the per-step spelling is not mentioned anywhere.

  (b) The required lane moved into a reusable workflow:
          jobs:
            validate:
              uses: ./.github/workflows/reusable.yml
      The job exists, has no `steps`, so conditional_steps and shell_override
      both return 0 and the lane passes with nothing about its contents checked.
      A `./`-prefixed ref is additionally exempt from the pin rule by design.

  (c) `runs-on: [self-hosted, attacker-box]` — nothing inspects `runs-on`.

  Contrast job-level `if:`, which is ALSO uncaught but is explicitly stated:
  "(Job-level `if:` is left to the fan-in, which already refuses a skipped job.)"
  I verified that delegation is sound — ci-required-select.sh exits 1 on a
  `skipped` conclusion. That is the standard the other three do not meet.

Failure:
  Nothing is wrong at this SHA: no `shell:`, no `uses:` job, no self-hosted
  label anywhere in either workflow. But the slice's own claim is that
  FINDING 3 was "closed, not merely stated", and the closure covers one spelling
  of shell override out of two.

Perspective:
  developer

Recommendation:
  Smallest real fix: in check-lane-integrity.py, refuse a step-level `shell:` on
  a required lane exactly as `defaults.run.shell` is refused (the same
  `shell_override` message applies), and refuse a required lane whose job has a
  `uses:` instead of `steps:` unless the called workflow is itself checked.
  `runs-on` is a policy question — one sentence naming it as unchecked is enough.

Acceptance criteria:
  - A step-level `shell:` on a required lane exits 1 with a named reason.
  - A required lane defined by `uses:` is either followed into the called
    workflow or refused by name.
  - check-lane-integrity.py's docstring names `runs-on` as deliberately unchecked.
  - Two new lane-* fixtures, with expected_lane_fixtures moved 5 → 7 in the same
    commit so the floor is a decision.

Tests:
  scripts/testdata/lane-step-shell.yml and lane-reusable.yml, each declaring the
  rule it trips, exercised by ci-required-guard.sh on every run.

Cross-repo implications:
  core: none | user: none | search: none
  meta: the component repos' guards should inherit the same rule set.

Challenge:
  All three require editing the workflow in the PR under test, which is the trust
  boundary the builder already declares open. An adversary who can edit
  validate.yml can also edit check-lane-integrity.py. The argument for fixing (a)
  anyway is that it is the *same rule* the file already enforces, differing only
  in where the key sits — not a new class of defence.
```

```
FINDING 8: range expansion is over-eager on a numeric path segment, and the header's claim about path slashes is too broad
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-quality-json.py:95-99 (CONTINUATION), 117-163 (expand_reference)
             scripts/check-quality-json.py docstring; docs/quality/COMMANDS.md § ranges
  requirements: VZ-CI-001

Observed:
  The docstring says a separator "only counts when digits follow it, so the `.`
  ending a sentence … and the `/` in a path (`docs/evidence/VZ-FOUND-008/`) end
  the run instead of extending it." True for the example given. Not true when the
  next path segment starts with digits:

      "docs/evidence/VZ-FOUND-008/2026-09-21.md"
        -> ['VZ-FOUND-0008', 'VZ-FOUND-2026']

  Two effects. The `/2026` is read as a list continuation, inventing
  VZ-FOUND-2026; and `width = max(width, len(digits))` then promotes the width to
  4, so the REAL id VZ-FOUND-008 is re-rendered as VZ-FOUND-0008 and also fails to
  resolve. Confirmed end-to-end by appending that path to docs/issues/VZ-ISSUE-001.md
  (digest 2e5f32570e45 → 37d49d726796): exit 1, both invented ids reported as
  dangling.

Failure:
  A date-shaped path written in an issue file — "transcript at
  docs/evidence/VZ-FOUND-008/2026-09-21.md" is an entirely natural sentence in
  this repository's idiom — turns the lane red with two ids nobody wrote. It
  fails CLOSED, so it cannot hide a real problem; it blocks a legitimate document
  and sends the author hunting for ids that do not exist. No such path exists in
  the checked corpus today, which is why the lane is green.

Perspective:
  developer

Recommendation:
  Two small changes. Require a list continuation's digit run to be the same width
  as the base id (or at most the base width), which rejects `/2026` after a
  3-digit id; and stop promoting `width` from continuations, so a malformed
  continuation can never corrupt the rendering of the ids that were read
  correctly. Then narrow the docstring sentence to what the code does.

Acceptance criteria:
  - "docs/evidence/VZ-FOUND-008/2026-09-21.md" in a checked document expands to
    exactly [VZ-FOUND-008] and the lane stays green.
  - The nine existing range/slash rows in docs/MILESTONES.md expand unchanged
    (VZ-TOPOLOGY-001…003/006/007 -> 001,002,003,006,007).
  - VZ-CI-001/888 stays red.

Tests:
  Extend demo-8-range-and-slash-list-expansion.txt with the path case, showing it
  green rather than red.

Cross-repo implications:
  core: none | user: none | search: none | meta: none

Challenge:
  A width rule would reject a legitimate cross-width list such as
  `VZ-X-008/0012` — but no such id exists, the ledger uses uniform 3-digit
  suffixes throughout all 191 entries, and "a continuation must match the base
  width" is a rule the corpus already obeys. The alternative reading is that
  writing a bare path next to an id is simply bad practice in a checked document
  and should be wrapped in backticks — except backticked ids ARE checked here, by
  deliberate design, so that escape does not exist.
```

---

## Re-verification verdict

**PASS at `5dfa75c`.**

| Original finding | Status |
|---|---|
| FINDING 1 — ledger false green | **CLOSED** — no-op, empty, partial and invalid-JSON generators all red by name; honest regeneration still green; `rm -f` provably cannot touch the hand-maintained siblings |
| FINDING 2 — range expansion | **CLOSED** — 287 ids from 191 written references; mid-range members now caught; descending and implausible ranges are named failures; no over-eagerness on sentence periods or ordinary path slashes; exclusions measured and documented |
| FINDING 3 — lane neutering | **CLOSED** — `defaults.run.shell` (workflow + job), any step-level `if:`, and parsed job existence over `.yml` and `.yaml`; 7 fixtures, floor 7 |
| FINDING 4 — doc accuracy | **CLOSED** — PR body corrects itself explicitly; stale count removed and deliberately not replaced; the locale invocation runs in the lane and goes red with the fix reverted |
| Self-reported: "every one resolves" beside an unreadable range | **CLOSED** — the two statements cannot co-occur |

New: FINDING 5 (SHOULD), FINDINGS 6–8 (NIT). None blocks. FINDING 5 is the one
the chair should act on before relying on the merge rule, because it changes what
"ci-required green on the verified SHA" attests to: on a `pull_request` the lane
validates head-merged-into-base, and this PR's base has moved four commits since
the verdict. `ci-required` itself polls the correct SHA, both lanes are green, and
the head has not moved — so the rule's conditions are met as written.

Ledger content byte-identical to base; `e667b60` an ancestor; nothing weakened;
no secrets; scope confined to `scripts/`, `docs/quality/COMMANDS.md` and
`docs/evidence/meta-validate/`.

PASS is not a merge and does not make any ledger entry VERIFIED — the chair
records those.
