# Verification commands — vizra META repo

The actual commands for this repository's required checks, and what each one
proves. AGENTS.md § Required workflow point 3 points here: *"Use actual commands
documented in docs/quality/COMMANDS.md once created. A missing command or
dependency is BLOCKED, never a pass."*

**This file lists only commands that exist in this repository and that were run
to produce the evidence cited below.** It does not list commands for
`vizra-core`, `vizra-user` or `vizra-search`: those are separate repositories
with their own contracts, they are gitignored checkouts here (docs/META_REPO.md
§1), and nothing in this file was run against them. Look in each component
repository's own `AGENTS.md` for its lanes.

## Prerequisites

| Requirement | Used for | Checked with |
|---|---|---|
| `python3` ≥ 3.9 | every check; the ledger generator | `python3 --version` |
| PyYAML | the workflow checkers parse YAML rather than grepping it | `python3 -c 'import yaml; print(yaml.__version__)'` |
| `git` | the generated-ledger diff | `git --version` |
| `bash` | the two shell guards | — |

No Docker, no database, no browser and no network access is required. The link
checker deliberately performs **no** network I/O.

CI pins the interpreter to **Python 3.12.14** (`actions/setup-python`, pinned by
commit SHA). PyYAML is **not** pinned in practice: the `ubuntu-24.04` runner
image ships it, and the `pyyaml==6.0.3` line in `ci-required.yml` is only a
fallback for an image that does not. The first CI run used the runner's
preinstalled **PyYAML 6.0.1**; the pinned install did not execute. Recorded
here because "pinned" and "what actually ran" are different facts.

The local transcripts below were produced on macOS with the system
**Python 3.9.6** and PyYAML 6.0.3. The CI transcripts in
`docs/evidence/meta-validate/ci-run-*.txt` are the Linux runs.

## The `validate` lane

`.github/workflows/validate.yml` runs these three, in this order. Run them from
the repository root.

### 1. The generated ledger matches its sources

```
./scripts/check-generated-ledger.sh
```

Re-runs the ledger generator and asserts `git diff --exit-code` over every file
it writes (today: `docs/quality/features.json`). Catches **both** a hand-edited
generated file and a generator source changed without regenerating — they are
indistinguishable in review and identical from this check's point of view.
Refuses to run against a dirty working tree, so a difference is never
misattributed.

It **deletes the declared files before regenerating**. A diff alone cannot tell
"rewrote it identically" from "wrote nothing", so a generator gutted to
`print("OK 191 requirements; core=141")` used to exit 0 here while the check
printed a reproduction claim that was false. With the files removed first, a
generator that writes nothing leaves a deletion, and each declared file must
then **exist, be non-empty and parse as JSON** before the diff runs. Together
with the existing undeclared-file check, the declared list and the generator's
real output set are asserted equal in **both** directions.

It then re-runs the generator once under
`LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0` and requires
byte-identical output. That is the environment in which the pre-fix generator
raises `UnicodeEncodeError: 'ascii' codec can't encode character '—'` and
leaves a truncated `features.json`; PEP 538's C-locale coercion is what
normally masks it, which is why both variables are needed to see it.

Last run: **exit 0**, `generated ledger reproduces byte-for-byte:
docs/quality/features.json (UTF-8 and C/POSIX locales)` (191 requirements,
core=141).

To regenerate after editing a generator source — and you must commit both:

```
(cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json)
```

Last run: **exit 0**, `OK 191 requirements; core=141`.

### 2. Quality JSON parses and every requirement id resolves

```
./scripts/check-quality-json.py
```

Every `*.json` under `docs/quality/` parses, and every `VZ-…` id referenced by
`docs/MILESTONES.md` and `docs/issues/*.md` names a requirement in
`features.json`. `VZ-ISSUE-NNN` and `VZ-SLICE-NN` are separate namespaces,
allowlisted by name — and `VZ-ISSUE-NNN` is still resolved against a real
`docs/issues/VZ-ISSUE-NNN.md`, so the allowlist is not an escape hatch.

**Ranges and slash-lists are expanded and every member resolved.** The
milestone rows write `VZ-FOUND-001…008`, `VZ-CI-001/002/004` and
`VZ-MEDIA-002/005…010`; resolving only the leading id would validate one
requirement out of eight. A separator (`…`, `...`, `–`, `—`, `/`) only counts
when digits follow it, so a sentence-ending `.` and a path `/` end the run. A
descending or implausibly long range is a **named failure**, not a silent skip.

Last run: **exit 0** — 4 JSON files parsed, 191 requirement ids in the ledger,
191 written references expanded to 287 ids (204 distinct) across 14 documents,
every one resolving.

### Scope of the id check, and what is deliberately excluded

| Path | Checked | Why |
|---|---|---|
| `docs/MILESTONES.md` | yes | schedules work; an id here is a commitment |
| `docs/issues/*.md` | yes | the slice definitions |
| `docs/plans/*.md` | **no** | plans legitimately PROPOSE ids that do not exist yet. Measured: the 13 slice plans are clean, but `docs/plans/WARROOM-BOARD.md` row 2b names four proposed ids (`VZ-SEC-SSR-001`, `VZ-SEC-HDR-001`, `VZ-SEC-SSR-002`, `VZ-SEC-SUPPLY-001`) whose purpose is to be evaluated and possibly added to the ledger. Gating this directory would make the lane red for proposing a requirement. |
| `docs/evidence/**` | **no** | a red/green transcript must write down the id it deliberately made dangle (`VZ-NOSUCH-999`, `VZ-ISSUE-404`, `VZ-FOUND-001…999`). Gating it would make every demonstration a lane failure. |

Both exclusions were measured, not assumed. If a plan or the board should be
gated later, the honest way in is a marker distinguishing "proposed" from
"referenced", not a wildcard exemption.

### 3. Relative documentation links resolve

```
./scripts/check-doc-links.py
```

Relative markdown links in `docs/**/*.md` and the root `*.md` resolve to a file
that exists. External URLs are recorded and **never fetched**. Fenced blocks and
inline code spans are stripped first.

Last run: **exit 0** — `relative links: none exist yet … (checked nothing);
6 external URL(s) recorded and not fetched`.

The markdown-file count the command prints is **deliberately not quoted here**.
It changes every time a document is added — this file's own first version
recorded 87 and was stale within the same commit that added it, because
COMMANDS.md joined the corpus it was counting. A number that goes stale on its
own is worse than no number in a file whose purpose is that recorded figures can
be trusted. Run the command for the current value.

That "checked nothing" is accurate and is printed on purpose: this repository
currently contains **zero** relative markdown links. Every link-shaped string in
`docs/` is either inside code (26 of them) or an external URL (6). The check is
proven by the controlled mutation in
`docs/evidence/meta-validate/demo-4-broken-relative-link.txt`, not by existing
content. The checker fails if it matches *no* link of any kind, so a regex that
silently stopped matching is red rather than green.

## The `ci-required` fan-in

```
./scripts/ci-required-guard.sh
```

Everything that can be checked about the gate from the checkout itself:
the floor (`validate` present and non-optional), bare job names, every required
check defined by a real job, `continue-on-error` refused wherever it appears
(parsed, not grepped), every action pinned to a 40-hex commit SHA, every
required lane triggered on `pull_request` with no base-branch filter, no
`defaults.run.shell` override, no step-level `if:` on a required lane, and all
three checkers exercised against their negative fixtures.

Last run: **exit 0** — 6 continue-on-error fixtures (floor 6), 7 pin/trigger
fixtures (floor 7), 7 lane-integrity fixtures (floor 7).

The three checkers it calls can also be run alone:

```
./scripts/check-workflows.py                                            # exit 0
./scripts/check-action-pins.py --required .github/required-checks.txt   # exit 0
./scripts/check-lane-integrity.py --required .github/required-checks.txt # exit 0
```

All three answer three ways, so "rejected" and "could not be evaluated" are
never confused: `0` clean, `1` VIOLATION, `2` UNEVALUABLE.

`check-lane-integrity.py` covers the two ways to neuter a lane that
`continue-on-error` does not: a `defaults.run.shell` override — the Actions
analogue of a Makefile `SHELL := /usr/bin/true`, which makes every `run:` step
in the job a no-op that still reports success — and a step-level `if:`, since a
skipped JOB is refused by the fan-in but a skipped STEP leaves the job green. A
constant false is refused by name; any other condition is refused too, because
nothing here can evaluate it and a step that might not run is not a gate. It
also owns job existence, which was previously a grep over `*.yml` only and
would have reported a lane defined in a `.yaml` workflow as missing.

The aggregate's row-selection rules run outside Actions too, which is how they
can be demonstrated at all:

```
./scripts/ci-required-select.sh "$(grep -vE '^\s*(#|$)' .github/required-checks.txt)" < runs.tsv
```

Exit `0` every required check succeeded · `1` at least one did not · `2` at
least one is still pending or never ran. `runs.tsv` is name/status/conclusion/
started_at, as `.github/workflows/ci-required.yml` produces it from the
check-runs API.

## Red/green demonstrations

Transcripts are under `docs/evidence/meta-validate/`. Each applies a controlled
mutation, shows the check red, restores, and shows it green.

| File | Mutation |
|---|---|
| `demo-1-hand-edited-features-json.txt` | a status hand-edited in the generated JSON and **committed** |
| `demo-2-stale-generated-file.txt` | a requirement title changed in the generator source without regenerating |
| `demo-3-dangling-requirement-id.txt` | `VZ-NOSUCH-999` and `VZ-ISSUE-404` referenced from an issue file |
| `demo-4-broken-relative-link.txt` | one resolving and one broken relative link added to `docs/MILESTONES.md` |
| `demo-5-floor-lane-deleted.txt` | `validate` removed from the manifest, both non-empty and empty |
| `demo-6-continue-on-error-three-spellings.txt` | `continue-on-error`, `"continue-on-error"`, `Continue-On-Error` inserted into the real `validate` job |
| `demo-7-generator-wrote-nothing.txt` | a generator that writes nothing, an empty file, only some declared files, and the pre-fix generator under the C/POSIX locale |
| `demo-8-range-and-slash-list-expansion.txt` | a range whose end does not exist, a slash-list with one bad member, a descending range |
| `demo-9-shell-override-and-conditional-step.txt` | `defaults.run.shell` at workflow and job level, `if: false`, a non-constant `if:`, and the required job renamed — all on the real `validate` workflow |

Demos 1 and 2 commit the mutation, because that is how one reaches CI: with the
mutation uncommitted, the dirty-tree precheck fires instead of the regeneration
check, which proves something weaker than intended.

## What is NOT covered

`docs/META_REPO.md` §7 names three target lanes for this repository. Only
`validate` exists.

| Lane | State |
|---|---|
| `validate` | **implemented here** |
| `bundle` | **not built.** There is no deployment bundle, no installer and no release record to build one from. |
| `boot` | **not built.** There is no compose file, no image and no service to boot. |

`bundle` and `boot` are deliberately absent from `.github/required-checks.txt`
rather than listed and empty: `ci-required` fails on a required check that never
ran, so listing a lane nobody defined would block every merge rather than gate
anything. They are added by the slices that create the things they test.

Also not covered by any lane here: shellcheck on the guard scripts (no
shellcheck dependency is introduced by this slice), and `.github/CODEOWNERS`
itself, which **nothing enforces** — see that file.
