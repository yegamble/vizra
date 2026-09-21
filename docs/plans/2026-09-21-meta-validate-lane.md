# Execution plan: meta repo `validate` lane and `ci-required` fan-in (VZ-CI-001, meta side)

## Context

- Repo: `yegamble/vizra` (meta). Worktree: `/Users/yosefgamble/github/vizra/.claude/worktrees/meta-validate`,
  branch `ci/meta-validate`, based on `origin/chore/m0-meta-baseline` at `3b63c0e`.
- The main checkout stays on `chore/m0-meta-baseline` and is written to by the
  war-room chair. Nothing outside the worktree is edited except this plan file.
- Why: the owner's merge rule (AGENTS.md § Merge authorization, 2026-09-20)
  requires `ci-required` green on the verified SHA. The meta repo has **no CI at
  all**, so PR #2 (`yegamble/vizra#2`) has been unmergeable since it opened.
- References: `AGENTS.md`; `docs/META_REPO.md` § 7 (CI/CD — meta's required lanes);
  `docs/adr/ADR-002` § "CI fan-in and merge queue" and § "Branch protection and
  rulesets (Q-032)"; `docs/evidence/ledger-generator/README.md` + `build.py`;
  reference implementation read read-only from `vizra-search/.github/` and
  `vizra-search/scripts/`.

## Acceptance

`validate` job (ubuntu-24.04, GitHub-hosted, `permissions: contents: read`,
triggers `pull_request` for **any** base branch + `merge_group`):

- (a) **generated ledger**: re-run `docs/evidence/ledger-generator/build.py` with a
  pinned Python and assert `git diff --exit-code` over every file it writes.
  A hand-edited or stale generated file is red **and names the file**.
- (b) **quality JSON + referential integrity**: every `*.json` under `docs/quality/`
  parses; every `VZ-…` id referenced by `docs/MILESTONES.md` and `docs/issues/*.md`
  exists in `features.json`. Dangling ids are red and listed.
- (c) **relative links**: relative markdown links in `docs/**` and root `*.md`
  resolve to files that exist. External URLs are never fetched.

`ci-required` fan-in: reads `.github/required-checks.txt`, polls the check-runs
API for the PR head SHA, fails closed on missing / skipped / cancelled /
timed-out / failed. Guard enforces: floor (`validate` present, non-optional),
`continue-on-error` refused **wherever it appears** (YAML parsed, not grepped),
every `uses:` pinned to a 40-hex SHA, and every required lane actually triggered
on `pull_request` with no base-branch filter.

Non-goals: product code; compose/installer/bundle/boot lanes (META_REPO § 7
target set — only `validate` is built here); changing ledger content or statuses;
the war-room board; merging.

## Implementation

New files, all inside the worktree:

| Path | Role |
|---|---|
| `.github/workflows/validate.yml` | the `validate` job (a)(b)(c) |
| `.github/workflows/ci-required.yml` | the fan-in aggregate |
| `.github/required-checks.txt` | the checked-in definition of "required" |
| `.github/CODEOWNERS` | owner review on gate paths (advisory until a ruleset exists) |
| `scripts/check-generated-ledger.sh` | (a) |
| `scripts/check-quality-json.py` | (b) |
| `scripts/check-doc-links.py` | (c) |
| `scripts/check-workflows.py` | `continue-on-error` by parse (adapted from vizra-search) |
| `scripts/check-action-pins.py` | every `uses:` pinned by 40-hex SHA; required lanes triggered on `pull_request` |
| `scripts/ci-required-guard.sh` | floor + bare names + job existence + pins + triggers + fixtures |
| `scripts/ci-required-select.sh` | check-run row selection (adapted) |
| `scripts/testdata/wf-*.yml` | negative fixtures |
| `docs/quality/COMMANDS.md` | only commands that exist and were run |

Generator determinism (finding, see below) is fixed in
`docs/evidence/ledger-generator/build.py` **without changing output bytes**.

## Verification

Focused, then the full lane. Exact commands and exit codes recorded in
`docs/quality/COMMANDS.md` and in the transcripts under
`docs/evidence/meta-validate/`.

Required demonstrations (red against a controlled mutation, green when restored):

1. hand-edit `docs/quality/features.json` → red naming the file
2. generator source change without regenerating → red
3. dangling `VZ-…` id in an issue file → red
4. broken relative link → red
5. `validate` deleted from `.github/required-checks.txt` → red
6. `continue-on-error` in three spellings → red

Linux evidence: the `validate` job on ubuntu-24.04 against the PR head SHA is
the only proof that the generator reproduces `features.json` byte-for-byte on
Linux. That cannot be produced on this macOS host.

## Progress and evidence

### Preflight (2026-09-20)

| Tool | Result |
|---|---|
| `python3 --version` | `Python 3.9.6` (`/usr/bin/python3`), macOS system |
| `python3 -c 'import yaml'` | PyYAML 6.0.3 present |
| `gh --version` / `gh auth status` | 2.98.0, logged in as `yegamble`, scopes include `repo`, `workflow` |
| `git --version` | 2.50.1 |
| `jq --version` | jq-1.7.1-apple |
| `yq` | **absent** — not used; workflows are parsed with PyYAML |
| Docker | not needed for this slice |

### Finding 1 — generator determinism (reported before any workflow was written)

`python3 build.py <out>` in `docs/evidence/ledger-generator/` exits 0 and the
output is **byte-identical** to the committed `docs/quality/features.json`
(343762 bytes) on this host:

```
cmp <regen> docs/quality/features.json  → IDENTICAL
```

Two portability defects were found in `build.py` anyway, only one of which is
observable on macOS:

1. **Locale-dependent encoding (real, unobservable here).**
   `json.dump(out, open(sys.argv[1],"w"), ensure_ascii=False)` opens the file
   with **no `encoding=`**, so the output encoding is
   `locale.getpreferredencoding(False)`. `features.json` contains 11 distinct
   non-ASCII characters (`§ ° × – — … ← → ↔ ≤ ≥`). On Linux under a `POSIX`/`C`
   locale that is ASCII and the write raises `UnicodeEncodeError`; on a
   `C.UTF-8` runner it happens to work. macOS always reports UTF-8
   (`LC_ALL=POSIX python3 -c 'locale.getpreferredencoding(False)'` → `UTF-8`),
   so **the failure cannot be reproduced on this host** — it is fixed by
   inspection, not by a red transcript.
   Fix: `open(sys.argv[1], "w", encoding="utf-8")`. Output bytes unchanged.
2. **No trailing newline.** `features.json`, `ui-controls.json` and
   `release-profiles/core.json` end without `\n`; `release-profiles/full.json`
   ends with one. Deliberately **not changed**: adding one would rewrite the
   committed ledger bytes, which this slice is scoped out of. Recorded here so
   it is a decision, not an oversight.

`build.py` writes exactly one file — `sys.argv[1]`. `ui-controls.json` and
`release-profiles/*.json` are **not** generated (no generator source references
them); they are hand-authored siblings. So check (a) diffs `docs/quality/features.json`
only, and check (b) parse-checks every JSON under `docs/quality/`.

### Finding 2 — the link checker must not read code samples

A naive `\[[^\]]*\]\(([^)]+)\)` scan reports 26 broken links, **all 26 false
positives** from inline code spans such as
`` `globalThis["fetch"](url, init)` `` in
`docs/evidence/warroom/2026-09-20-vizra-user-pr1b-hardening-VERIFY.md` and
`docs/plans/2026-09-20-vizra-user-pr1b-hardening.md`. The checker therefore
strips fenced blocks and inline code spans before matching.

### Finding 3 — two `VZ-…` namespaces are not ledger ids

Of 138 distinct `VZ-…` ids referenced by `docs/MILESTONES.md` and
`docs/issues/*.md`, 13 are not in `features.json`: `VZ-ISSUE-001…012` (the issue
files themselves) and `VZ-SLICE-01` (the golden path, `docs/PRODUCT_SPEC.md` §15).
These are separate namespaces, allowlisted **by name** — and `VZ-ISSUE-NNN` is
still resolved against an actual `docs/issues/VZ-ISSUE-NNN.md` file, so the
allowlist is not an escape hatch.

### Finding 4 — an emptied manifest killed the guard silently

Found while running demonstration 5, not by inspection.
`required="$(grep -vE '^\s*(#|$)' "$manifest" | tr -d '\r')"` exits 1 when the
manifest has no lane lines, and under `set -e` that kills the script **on the
assignment**, before the `test -n` written to explain it. A manifest emptied
down to its comments therefore exited 1 with **no output at all** — the worst
possible error for the one gate that decides whether a PR may merge. The first
red transcript for demo 5 was an empty block and an exit code, which is what
exposed it. Fixed in its own commit (`9da584e`) with `|| true` plus an explicit
`EMPTY MANIFEST` message. Note this defect is inherited from the `vizra-search`
guard, which still has it.

### Process error in the first evidence pass (recorded, not smoothed over)

The first run of the demonstration script used `git checkout --` to restore, but
`.github/` and `scripts/` were still **untracked**, so nothing was restored:
demo 6 accumulated all three `continue-on-error` spellings in the live workflow
and demo 5 left `validate` missing from the manifest. Demo 1 also tripped the
dirty-tree precheck instead of the regeneration check (the mutation was left
uncommitted, whereas a hand-edit reaches CI as a commit), and demo 2's mutation
regex did not match the generator's source format, so it mutated nothing and
"passed" — a non-demonstration. The lane files were committed first, demos 1, 2
and 5 were rewritten to commit their mutation and to use `git reset --hard`, and
all six were re-run. The transcripts in `docs/evidence/meta-validate/` are from
the corrected pass.

### Local results (macOS, Python 3.9.6, PyYAML 6.0.3)

| Command | Exit | Result |
|---|---|---|
| `./scripts/check-generated-ledger.sh` | 0 | reproduces byte-for-byte; 191 requirements, core=141 |
| `./scripts/check-quality-json.py` | 0 | 4 JSON parsed; 191 ids; 139 refs across 14 docs, all resolve |
| `./scripts/check-doc-links.py` | 0 | 0 relative links exist; 6 external recorded, not fetched |
| `./scripts/ci-required-guard.sh` | 0 | floor ok; 6 CoE fixtures (floor 6); 7 pin fixtures (floor 7) |

Encoding fix verified byte-neutral, and now works under a forced ASCII IO
encoding: `LC_ALL=POSIX PYTHONIOENCODING=ascii python3 build.py <out>` → exit 0,
`cmp` IDENTICAL.

### CI results (ubuntu-24.04) — head SHA `78f0b7169b1bea08cb7b989dd33d1b9081765856`

PR: https://github.com/yegamble/vizra/pull/3 (base `chore/m0-meta-baseline`)

| Check | Conclusion | Duration |
|---|---|---|
| `validate` | **success** | 44s |
| `ci-required` | **success** | 48s |
| GitGuardian Security Checks | pass | 1s |

Both lanes triggered on a **stacked** PR, which is the property the unfiltered
`pull_request` trigger exists to guarantee.

**Finding 1 resolved.** On Linux with Python 3.12.14 the generator reproduces
`docs/quality/features.json` byte-for-byte (`generated ledger reproduces
byte-for-byte`). The committed ledger was never stale; the encoding defect was
latent, not active — the runner's locale is UTF-8 (`preferred encoding: UTF-8`
recorded in the transcript).

**Accuracy correction.** The runner used its preinstalled **PyYAML 6.0.1**; the
`pyyaml==6.0.3` line is only a fallback for an image without PyYAML and did not
execute. `docs/quality/COMMANDS.md` says so rather than claiming a pin that did
not apply.

Artifacts: `docs/evidence/meta-validate/ci-run-validate.txt`,
`docs/evidence/meta-validate/ci-run-ci-required.txt`.

### Fix round 1 — verifier PASS at `e667b60`, four findings closed

Head after the round: **`5dfa75ca1453f390cea1da1a7bd9accbfd641cb3`**.
`validate` success (6s), `ci-required` success (27s) on ubuntu-24.04.
Ledger content byte-identical to base on all four quality JSON files
(`features.json` `25231b8411f7`, `ui-controls.json` `7bc463afc1a2`,
`release-profiles/core.json` `a86d3b2704d2`, `full.json` `ecef08429693`).

**Finding 1 — the lane's primary check was a false green.** A generator that
exits 0 without writing anything passed as "reproduces byte-for-byte", because
`git diff --exit-code` cannot tell "rewrote identically" from "wrote nothing".
Fixed by deleting the declared files before regenerating, then requiring each to
exist, be non-empty and parse before the diff. Set equality now holds in both
directions. Plus a C/POSIX locale regression pass on every run.

**Finding 2 — ranges and slash-lists were not expanded.** Coverage went from 139
distinct ids to 287 expanded from 191 written references.

*The verifier's scope premise was wrong and I did not adopt it.* It suggested
widening to `docs/plans/` because "all ids there resolve today". Measured: the
13 slice plans are clean, but `docs/plans/WARROOM-BOARD.md` row 2b names four
**proposed** ids (`VZ-SEC-SSR-001`, `VZ-SEC-HDR-001`, `VZ-SEC-SSR-002`,
`VZ-SEC-SUPPLY-001`) that dangle by design. Gating that directory would make the
lane red for proposing a requirement. Took the chair's stated alternative:
scope unchanged, both exclusions documented with their measured reasons.

**Finding 3 — two simpler ways to neuter a lane.** New
`scripts/check-lane-integrity.py`: refuses `defaults.run.shell` at workflow or
job level and any step-level `if:` on a required lane; job existence moved from
a `.yml`-only grep to a YAML parse. Seven fixtures, one `.yaml` by design.

**Finding 4 — I was wrong about the locale bug.** My previous PR body claimed the
failure could not be reproduced on macOS. It can: with
`LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0` (PEP 538 coercion was
masking it) the pre-fix generator raises
`UnicodeEncodeError: 'ascii' codec can't encode character '—' in position 428`
and truncates the ledger. Reproduced in demo 7d; the invocation is now a lane
step. PR body corrected. The stale `87` file count was removed rather than
updated — it is 92 at this SHA, which is the argument against quoting it.

**Self-found during the round:** the id checker printed "every one resolves"
alongside a reported unreadable range — two statements about one run, one false.
Fixed.

Nine demonstrations now, each printing a sha256 before and after so a mutation
that did not land cannot be mistaken for a demonstration. Transcripts:
`docs/evidence/meta-validate/demo-1…9`, `ci-run-validate.txt`,
`ci-run-ci-required.txt`.

## Blockers and handoff

No blockers. State is **READY_FOR_REVIEW**, not VERIFIED: an independent
verifier that did not write this must reproduce the demonstrations from a clean
clone of the head, and `ci-required` must be green on the SHA it verifies.

Two things a reviewer should weigh rather than take on trust:

1. **The link check verifies nothing today** (0 relative links in the
   repository). It is proven only by demo 4's mutation. It is written to fail if
   it matches no link of any kind, so it cannot rot into a silent pass.
2. **Nothing enforces the gate.** CODEOWNERS is advisory, the floor lives in a
   script the PR under test can edit, and GitHub rulesets return 403 on this
   plan. Closing that is an owner action (ADR-002 item 9) and is not part of
   this slice.

The worktree at `/Users/yosefgamble/github/vizra/.claude/worktrees/meta-validate`
is left in place for the verifier; the chair removes it after the merge.
