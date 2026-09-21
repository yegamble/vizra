#!/usr/bin/env python3
"""Two properties of the workflow definitions, checked by PARSING them.

1. **Every `uses:` is pinned to a 40-character commit SHA.**
   A tag is a mutable pointer. `actions/checkout@v7` runs whatever the tag
   points at today, so a compromised or simply retagged action changes what CI
   executes without any diff in this repository. AGENTS.md § Engineering
   guardrails ("use reviewed dependency versions") and docs/META_REPO.md §7
   ("External actions are pinned to 40-character commit SHAs") both require the
   pin. A local action (`./path`) is exempt: it is in this repository and shows
   up in the diff. `docker://` is refused outright — it has no commit to pin to.

2. **Every required lane is actually triggered on `pull_request`, for any base
   branch.**
   A lane that is not triggered never runs, and a check that never ran must not
   be mistaken for a passing one. `scripts/ci-required-select.sh` already treats
   NEVER RAN as a failure at aggregate time, but that produces a 30-minute
   timeout rather than an immediate, legible error — and only for a PR that
   someone opened. This catches the same mistake statically.

   The base-branch filter matters here specifically. This repository's own
   workflow lands on a STACKED pull request (base `chore/m0-meta-baseline`, not
   `main`). A `pull_request: branches: [main]` filter would silently skip the
   lane on exactly that PR, leaving `ci-required` waiting for a check nobody
   scheduled. So a `branches:` or `branches-ignore:` filter on the
   `pull_request` trigger of a required lane's workflow is refused.

Usage:
    check-action-pins.py [--required <manifest>] [workflow.yml ...]

Exit codes:
    0  clean
    1  VIOLATION — at least one unpinned action or untriggered/filtered lane
    2  UNEVALUABLE — a workflow could not be read or parsed; nothing was checked
"""

import argparse
import glob
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only on a runner without PyYAML
    sys.stderr.write(
        "PyYAML is required: this check parses the workflows rather than grepping them.\n"
    )
    sys.exit(2)

SHA40 = re.compile(r"^[0-9a-f]{40}$")


def load(path):
    """Return the parsed workflow, or raise SystemExit(2) — never a silent skip."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as err:
        sys.stderr.write(f"UNEVALUABLE {path}: cannot read: {err}\n")
        raise SystemExit(2)
    if not text.strip():
        sys.stderr.write(f"UNEVALUABLE {path}: file is empty\n")
        raise SystemExit(2)
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as err:
        sys.stderr.write(f"UNEVALUABLE {path}: cannot parse: {err}\n")
        raise SystemExit(2)
    if not isinstance(doc, dict):
        sys.stderr.write(f"UNEVALUABLE {path}: not a workflow mapping\n")
        raise SystemExit(2)
    return doc


def walk_uses(node, path):
    """Yield (location, value) for every `uses:` anywhere under node."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}"
            if isinstance(key, str) and key.strip().strip("\"'").lower() == "uses":
                yield here, value
            else:
                yield from walk_uses(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from walk_uses(item, f"{path}[{i}]")


def check_pins(path, doc):
    """Every remote action reference must carry a 40-hex commit SHA."""
    violations = 0
    for where, value in walk_uses(doc.get("jobs", {}), f"{path}:jobs"):
        if not isinstance(value, str):
            sys.stderr.write(f"VIOLATION {path} uses={value!r} where={where} reason=not-a-string\n")
            violations += 1
            continue
        ref = value.strip()
        if ref.startswith("./") or ref.startswith(".\\"):
            continue  # local action: it is in this repository and shows in the diff
        if ref.startswith("docker://"):
            sys.stderr.write(
                f"VIOLATION {path} uses={ref} where={where} reason=docker-image\n"
                f"  A `docker://` action has no commit to pin to. Use a repository action\n"
                f"  pinned by SHA, or a `run:` step.\n"
            )
            violations += 1
            continue
        if "@" not in ref:
            sys.stderr.write(
                f"VIOLATION {path} uses={ref} where={where} reason=no-ref\n"
                f"  An action reference with no `@<sha>` is unpinned.\n"
            )
            violations += 1
            continue
        _, _, pin = ref.rpartition("@")
        if not SHA40.match(pin):
            sys.stderr.write(
                f"VIOLATION {path} uses={ref} where={where} reason=not-a-40-hex-sha\n"
                f"  '{pin}' is a tag or branch, which is mutable. Pin the action to the\n"
                f"  40-character commit SHA that tag points at today, and keep the tag in\n"
                f"  a trailing comment so a human can read it.\n"
            )
            violations += 1
    return violations


def normalise_triggers(doc):
    """Return the `on:` mapping. YAML 1.1 parses a bare `on` as the boolean True."""
    for key in ("on", True, "On", "ON"):
        if key in doc:
            return doc[key]
    return None


def check_pull_request_trigger(path, doc, lanes):
    """Every required lane defined here must run on pull_request, unfiltered."""
    jobs = doc.get("jobs")
    if not isinstance(jobs, dict):
        return 0
    defined = [lane for lane in lanes if lane in jobs]
    if not defined:
        return 0

    triggers = normalise_triggers(doc)
    if isinstance(triggers, str):
        triggers = {triggers: None}
    elif isinstance(triggers, list):
        triggers = {t: None for t in triggers}
    if not isinstance(triggers, dict):
        sys.stderr.write(
            f"VIOLATION {path} reason=no-triggers lanes={','.join(defined)}\n"
            f"  This workflow defines required lane(s) but declares no usable `on:` block,\n"
            f"  so they would never run and `ci-required` would wait for a check nobody scheduled.\n"
        )
        return 1

    if "pull_request" not in triggers:
        sys.stderr.write(
            f"VIOLATION {path} reason=not-triggered-on-pull-request lanes={','.join(defined)}\n"
            f"  A required lane that does not run on `pull_request` never produces a check run.\n"
            f"  `ci-required` treats NEVER RAN as a failure, so this is a 30-minute timeout,\n"
            f"  not a pass — but it should be caught here, statically.\n"
        )
        return 1

    config = triggers.get("pull_request")
    if isinstance(config, dict):
        for filter_key in ("branches", "branches-ignore"):
            if filter_key in config:
                sys.stderr.write(
                    f"VIOLATION {path} reason=base-branch-filter key={filter_key} "
                    f"lanes={','.join(defined)}\n"
                    f"  `pull_request.{filter_key}` filters by BASE branch. A stacked pull\n"
                    f"  request — one whose base is a feature branch rather than `main` —\n"
                    f"  would skip this lane entirely, and `ci-required` would then wait\n"
                    f"  forever for a check that was never scheduled. Required lanes run for\n"
                    f"  ANY base branch.\n"
                )
                return 1
    return 0


def read_manifest(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as err:
        sys.stderr.write(f"UNEVALUABLE {path}: cannot read required-check manifest: {err}\n")
        raise SystemExit(2)
    lanes = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    if not lanes:
        sys.stderr.write(f"UNEVALUABLE {path}: manifest lists no checks\n")
        raise SystemExit(2)
    return lanes


def main(argv):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--required", default=".github/required-checks.txt")
    parser.add_argument("workflows", nargs="*")
    args = parser.parse_args(argv[1:])

    paths = args.workflows or sorted(
        glob.glob(".github/workflows/*.yml") + glob.glob(".github/workflows/*.yaml")
    )
    if not paths:
        sys.stderr.write("no workflow files found; this check is not checking anything\n")
        return 2

    lanes = read_manifest(args.required) if args.required else []

    violations = 0
    pinned = 0
    for path in paths:
        doc = load(path)
        before = violations
        violations += check_pins(path, doc)
        if lanes:
            violations += check_pull_request_trigger(path, doc, lanes)
        if violations == before:
            pinned += sum(1 for _ in walk_uses(doc.get("jobs", {}), path))

    if violations:
        return 1
    print(
        f"workflows parsed: {len(paths)}; {pinned} action reference(s), every one pinned "
        f"to a 40-hex commit SHA; every required lane runs on pull_request for any base branch"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
