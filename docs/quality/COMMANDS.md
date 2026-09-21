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
misattributed. Also fails if the generator writes a file that is not in its
declared list.

Last run: **exit 0**, `generated ledger reproduces byte-for-byte:
docs/quality/features.json` (191 requirements, core=141).

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

Last run: **exit 0** — 4 JSON files parsed, 191 requirement ids, 139 distinct
`VZ-…` references across 14 documents, every one resolving.

### 3. Relative documentation links resolve

```
./scripts/check-doc-links.py
```

Relative markdown links in `docs/**/*.md` and the root `*.md` resolve to a file
that exists. External URLs are recorded and **never fetched**. Fenced blocks and
inline code spans are stripped first.

Last run: **exit 0** — `relative links: none exist yet across 87 markdown
file(s) (checked nothing); 6 external URL(s) recorded and not fetched`.

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
required lane triggered on `pull_request` with no base-branch filter, and both
checkers exercised against their negative fixtures.

Last run: **exit 0** — 6 continue-on-error fixtures exercised (floor 6) and
7 pin/trigger fixtures exercised (floor 7).

The two checkers it calls can also be run alone:

```
./scripts/check-workflows.py                                  # exit 0
./scripts/check-action-pins.py --required .github/required-checks.txt   # exit 0
```

Both answer three ways, so "rejected" and "could not be evaluated" are never
confused: `0` clean, `1` VIOLATION, `2` UNEVALUABLE.

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
