#!/usr/bin/env python3
"""Every JSON under docs/quality/ parses, and every VZ-… id referenced by the
milestone plan and the issue files exists in the ledger.

Two separate failures, reported separately:

1. **Unparseable JSON.** `docs/quality/features.json` and its siblings are the
   machine-readable ledger. A file that does not parse is not a ledger, and a
   reviewer reading the rendered markdown would never notice.

2. **Dangling requirement ids.** `docs/MILESTONES.md` and `docs/issues/*.md`
   schedule work by `VZ-…` id. An id that names nothing in `features.json` is
   either a typo or a requirement that was renamed or dropped without the
   owner decision AGENTS.md requires. Either way the plan points at nothing.

Two `VZ-…` namespaces are deliberately NOT ledger requirement ids:

  VZ-ISSUE-NNN  the issue files themselves (docs/issues/VZ-ISSUE-NNN.md)
  VZ-SLICE-NN   the golden-path slice (docs/PRODUCT_SPEC.md §15)

They are allowlisted by name, not by a wildcard. `VZ-ISSUE-NNN` is additionally
resolved against an actual `docs/issues/VZ-ISSUE-NNN.md` file, so the allowlist
cannot be used to smuggle a made-up id through: a reference to a nonexistent
issue is still red.

Ids inside fenced code blocks and inline code spans are still checked — unlike a
markdown LINK, an id written in backticks is a real reference to a real
requirement, and that is in fact how the issue files write them.

Exit codes:
    0  clean
    1  at least one failure, each named
"""

import glob
import json
import os
import re
import sys

QUALITY_DIR = "docs/quality"
LEDGER = os.path.join(QUALITY_DIR, "features.json")

# Referencing documents. These are the two the acceptance names; a file that is
# listed but missing is a failure, not a silent skip.
REFERENCING_GLOBS = ["docs/MILESTONES.md", "docs/issues/*.md"]

ID_PATTERN = re.compile(r"\bVZ-[A-Z0-9]+(?:-[A-Z]+)*-\d+\b")

# Namespaces that are not requirement ids. Each carries how it is resolved.
ISSUE_PREFIX = "VZ-ISSUE-"
SLICE_PREFIX = "VZ-SLICE-"


def fail(messages, text):
    messages.append(text)


def check_json_parses(problems):
    """Every .json under docs/quality/ must parse."""
    paths = sorted(glob.glob(os.path.join(QUALITY_DIR, "**", "*.json"), recursive=True))
    if not paths:
        fail(problems, f"NO JSON FOUND under {QUALITY_DIR}/ — this check is not checking anything")
        return None

    ledger = None
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except OSError as err:
            fail(problems, f"UNREADABLE JSON: {path}: {err}")
            continue
        except json.JSONDecodeError as err:
            fail(
                problems,
                f"INVALID JSON: {path}: line {err.lineno} column {err.colno}: {err.msg}",
            )
            continue
        if path == LEDGER:
            ledger = data
    print(f"json parsed: {len(paths)} file(s) under {QUALITY_DIR}/")
    return ledger


def ledger_ids(ledger, problems):
    if ledger is None:
        fail(problems, f"MISSING LEDGER: {LEDGER} did not parse, so no id can be resolved")
        return set()
    features = ledger.get("features")
    if not isinstance(features, list) or not features:
        fail(problems, f"MISSING LEDGER: {LEDGER} declares no `features` array")
        return set()
    ids = set()
    for entry in features:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            ids.add(entry["id"])
    if not ids:
        fail(problems, f"MISSING LEDGER: {LEDGER} has a `features` array with no ids")
    return ids


def referencing_files(problems):
    paths = []
    for pattern in REFERENCING_GLOBS:
        matched = sorted(glob.glob(pattern))
        if not matched:
            fail(
                problems,
                f"NO FILES MATCHED '{pattern}' — the id check would silently verify nothing",
            )
        paths.extend(matched)
    return paths


def check_ids(ids, problems):
    paths = referencing_files(problems)
    known_issue_files = {
        os.path.splitext(os.path.basename(p))[0] for p in glob.glob("docs/issues/*.md")
    }

    references = {}
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as err:
            fail(problems, f"UNREADABLE: {path}: {err}")
            continue
        for match in ID_PATTERN.finditer(text):
            references.setdefault(match.group(0), set()).add(path)

    if not references:
        fail(problems, "NO VZ-… ids were found in any referencing document — nothing was checked")
        return

    dangling = []
    for ref in sorted(references):
        if ref in ids:
            continue
        if ref.startswith(SLICE_PREFIX):
            continue
        if ref.startswith(ISSUE_PREFIX):
            # Allowlisted namespace, still resolved: it must name a real issue file.
            if ref not in known_issue_files:
                dangling.append(
                    (ref, references[ref], f"no docs/issues/{ref}.md exists")
                )
            continue
        dangling.append((ref, references[ref], f"not in {LEDGER}"))

    if dangling:
        fail(problems, f"DANGLING REQUIREMENT ID(S): {len(dangling)} id(s) reference nothing:")
        for ref, where, why in dangling:
            problems.append(f"  {ref}: {why}")
            for path in sorted(where):
                problems.append(f"      referenced by {path}")
        return

    print(
        f"requirement ids: {len(references)} distinct VZ-… reference(s) across "
        f"{len(paths)} document(s); every one resolves"
    )


def main():
    problems = []
    ledger = check_json_parses(problems)
    ids = ledger_ids(ledger, problems)
    if ids:
        print(f"ledger: {len(ids)} requirement id(s) in {LEDGER}")
        check_ids(ids, problems)

    if problems:
        sys.stderr.write("\n".join(problems) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
