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

**Ranges and slash-lists are expanded, and every member is resolved.**
The milestone rows do not spell ids out one per line; they write

    VZ-FOUND-001…008          a range:      001 002 003 004 005 006 007 008
    VZ-CI-001/002/004         a list:       001 002 004
    VZ-MEDIA-002/005…010      both:         002 005 006 007 008 009 010
    VZ-STORAGE-002…006/014/015              002 003 004 005 006 014 015

Resolving only the leading id — which is what a single-id regex does — means
`VZ-FOUND-001…008` is validated by checking `VZ-FOUND-001` alone. The M0 row
schedules eight requirements and seven of them would go unchecked, so renaming
or dropping `VZ-FOUND-005` (exactly the owner-decision violation this check
exists to catch) would leave the plan pointing at nothing and the lane green.

A range separator is `…`, `...`, `–` or `—`; a list separator is `/`. A
continuation is read only when ALL THREE of these hold, and the run ends
quietly at the first one that does not:

  1. digits follow the separator — so the `.` ending a sentence
     (`… see VZ-CI-001.`) and the `/` ending a path
     (`docs/evidence/VZ-FOUND-008/`) end the run;
  2. those digits are followed by neither a digit nor a hyphen — so
     `docs/evidence/VZ-FOUND-008/2026-09-21.md`, an ordinary evidence path in
     this repository, is NOT read as a list. Without this the checker invented
     `VZ-FOUND-0008` and `VZ-FOUND-2026` and turned the lane red on a correct
     document;
  3. the digits are written at the same width as the id they continue, and that
     width is one the ledger actually uses — derived from features.json, not
     hard-coded. A four-digit number after a slash is a date or a version, not a
     sibling requirement.

Ending the run is deliberately NOT an error: `VZ-FOUND-008` in a path is a
correct reference to one requirement, and the checker resolves it as such.
Only a reference that was read AS a range and cannot be made sense of — end
before start, or an implausible span — is a NAMED FAILURE, never a silent skip.

Two `VZ-…` namespaces are deliberately NOT ledger requirement ids:

  VZ-ISSUE-NNN  the issue files themselves (docs/issues/VZ-ISSUE-NNN.md)
  VZ-SLICE-NN   the golden-path slice (docs/PRODUCT_SPEC.md §15)

They are allowlisted by name, not by a wildcard. `VZ-ISSUE-NNN` is additionally
resolved against an actual `docs/issues/VZ-ISSUE-NNN.md` file, so the allowlist
cannot be used to smuggle a made-up id through: a reference to a nonexistent
issue is still red. Ranges expand in this namespace too (`VZ-ISSUE-001…012`).

**Scope: exactly `docs/MILESTONES.md` and `docs/issues/*.md`.** These are the
two documents that SCHEDULE work: a `VZ-…` id in them is a commitment to build
a requirement, so an id naming nothing is a planning error. Two directories are
deliberately excluded, and each exclusion was measured rather than assumed:

  docs/evidence/  Evidence transcripts quote deliberately-nonexistent ids —
                  `VZ-NOSUCH-999`, `VZ-ISSUE-404`, `VZ-FOUND-001…999` — because
                  recording a red/green demonstration REQUIRES writing down the
                  id that was made to dangle. Checking this directory would turn
                  every demonstration transcript into a lane failure.

  docs/plans/     Plans are working documents, and one of the things they
                  legitimately do is PROPOSE ids that do not exist yet.
                  Measured at the time of writing: the 13 slice plans are
                  clean, but `docs/plans/WARROOM-BOARD.md` row 2b names four
                  proposed requirement ids — `VZ-SEC-SSR-001`, `VZ-SEC-HDR-001`,
                  `VZ-SEC-SSR-002`, `VZ-SEC-SUPPLY-001` — whose whole purpose is
                  to be evaluated and possibly added to the ledger. They dangle
                  by design. Including this directory would make the lane red
                  for proposing a requirement, which is backwards, and would put
                  a gate in the way of the war room's own working notes.

If a plan or the board should be gated later, the honest way in is a marker
that distinguishes "proposed" from "referenced", not a wildcard exemption.

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

# Referencing documents. A glob that is listed but matches nothing is a
# failure, not a silent skip. docs/evidence/ and docs/plans/ are excluded on
# purpose, each for a measured reason — see the module docstring.
REFERENCING_GLOBS = ["docs/MILESTONES.md", "docs/issues/*.md"]

# A bare id, and then the run of range/list continuations that may follow it.
ID_PATTERN = re.compile(r"\bVZ-[A-Z0-9]+(?:-[A-Z]+)*-\d+\b")
# A separator only counts when digits follow, so a sentence-ending "." and a
# path "/" terminate the run rather than extending it. Applied with .match(s, pos),
# which anchors at pos (Python's re has no \G).
#
# `(?![\d-])` is the boundary that stops a DATE from being read as a list of
# requirement ids. This repository names evidence directories after requirement
# ids, so `docs/evidence/VZ-FOUND-008/2026-09-21.md` is an ordinary path — and
# without the boundary it parsed as "VZ-FOUND-008, then list member 2026",
# inventing `VZ-FOUND-0008` and `VZ-FOUND-2026` and turning the lane red on a
# correct document. A member must be followed by something that is neither a
# digit nor a hyphen, so `/2026-09-21` does not match at all and the run ends.
CONTINUATION = re.compile(r"(?:(…|\.\.\.|–|—)|(/))(\d+)(?![\d-])")

# An upper bound on how many ids one range may name. A range is shorthand for a
# handful of consecutive requirements; anything larger is a typo (VZ-FOUND-001…999
# is 999 ids) and must be reported rather than silently expanded into a thousand
# lookups that all happen to fail.
MAX_RANGE_SPAN = 200

# Namespaces that are not requirement ids. Each carries how it is resolved.
ISSUE_PREFIX = "VZ-ISSUE-"
SLICE_PREFIX = "VZ-SLICE-"


def fail(messages, text):
    messages.append(text)


def expand_reference(text, match, problems, path, widths):
    """Expand one id and any range/list run that follows it.

    `widths` is the set of numeric-suffix widths actually used by the ledger
    (derived from features.json, not hard-coded). A continuation member must be
    written at the SAME width as the id it continues, and that width must be one
    the ledger uses. Anything else ends the run instead of extending it, because
    a number of a different width is not a sibling requirement — it is a date, a
    version, or some other digits that happen to follow a slash.

    Returns the list of fully-qualified ids the reference names. Appends to
    `problems` (and returns what it could read) when a range is unreadable —
    an unreadable reference must be reported, never silently dropped.
    """
    base = match.group(0)
    prefix, _, first_digits = base.rpartition("-")
    width = len(first_digits)
    numbers = [int(first_digits)]
    shorthand = base

    # An id whose own suffix is not a ledger width is left exactly as written.
    # It is still resolved as a plain id (and will be reported if it names
    # nothing); it simply does not get to start a range.
    if width not in widths:
        return [base]

    pos = match.end()
    previous = int(first_digits)
    while True:
        cont = CONTINUATION.match(text, pos)
        if not cont:
            break
        range_sep, _list_sep, digits = cont.group(1), cont.group(2), cont.group(3)
        if len(digits) != width:
            # Not a sibling id: a date, a version, a line number. End the run
            # rather than inventing an id at a width the ledger never uses.
            break
        shorthand += cont.group(0)
        value = int(digits)
        if range_sep:
            if value < previous:
                fail(
                    problems,
                    f"UNREADABLE RANGE: {path}: '{shorthand}' ends at {value:0{width}d} "
                    f"but starts at {previous:0{width}d}. A range must ascend; this cannot "
                    f"be read as a reference, so it is reported rather than skipped.",
                )
                return [f"{prefix}-{n:0{width}d}" for n in numbers]
            span = value - previous + 1
            if span > MAX_RANGE_SPAN:
                fail(
                    problems,
                    f"IMPLAUSIBLE RANGE: {path}: '{shorthand}' names {span} ids, ending at "
                    f"{prefix}-{value:0{width}d}; the cap is {MAX_RANGE_SPAN}. A range is "
                    f"shorthand for a handful of consecutive requirements, so a span this "
                    f"large is a typo, not a range.",
                )
                return [f"{prefix}-{n:0{width}d}" for n in numbers]
            numbers.extend(range(previous + 1, value + 1))
        else:
            numbers.append(value)
        previous = value
        pos = cont.end()

    return [f"{prefix}-{n:0{width}d}" for n in numbers]


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


def ledger_widths(ids):
    """The numeric-suffix widths the ledger actually uses.

    Derived, never hard-coded: if the ledger ever adopts a second width this
    follows it, and if the ledger is empty the caller has already failed.
    """
    return {len(one.rsplit("-", 1)[1]) for one in ids if one.rsplit("-", 1)[1].isdigit()}


def check_ids(ids, problems):
    problems_before = len(problems)
    widths = ledger_widths(ids)
    if not widths:
        fail(problems, "LEDGER HAS NO NUMERIC IDS: cannot determine the id width")
        return
    paths = referencing_files(problems)
    known_issue_files = {
        os.path.splitext(os.path.basename(p))[0] for p in glob.glob("docs/issues/*.md")
    }

    references = {}
    expanded_total = 0
    written_total = 0
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as err:
            fail(problems, f"UNREADABLE: {path}: {err}")
            continue
        pos = 0
        while True:
            match = ID_PATTERN.search(text, pos)
            if not match:
                break
            written_total += 1
            ids_here = expand_reference(text, match, problems, path, widths)
            expanded_total += len(ids_here)
            for one in ids_here:
                references.setdefault(one, set()).add(path)
            # Continue past the whole expanded run, so the trailing numbers of a
            # range are not re-matched as bare ids.
            pos = match.end()
            while True:
                cont = CONTINUATION.match(text, pos)
                if not cont or len(cont.group(3)) != len(match.group(0).rsplit("-", 1)[1]):
                    break
                pos = cont.end()

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

    # Only claim "every one resolves" when nothing went wrong on the way here.
    # A reference this run could not READ — a descending or implausible range —
    # was reported above but never resolved, so printing the success summary
    # alongside it would be a false statement in the same output.
    if len(problems) > problems_before:
        print(
            f"requirement ids: {written_total} written reference(s), "
            f"{expanded_total} id(s) expanded and resolved, but at least one reference "
            f"could not be read — see the failure(s) above"
        )
        return

    print(
        f"requirement ids: {written_total} written reference(s) expanded to "
        f"{expanded_total} id(s), {len(references)} distinct, across {len(paths)} "
        f"document(s); every one resolves"
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
