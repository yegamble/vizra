#!/usr/bin/env python3
"""A required lane must exist, and every step of it must actually run.

`scripts/check-workflows.py` refuses `continue-on-error` in five spellings, on
the principle that a lane which cannot fail is not a gate. But there are two
strictly simpler ways to neuter the same lane, and neither involves that key:

1. **`defaults.run.shell`**, at workflow or job level, replaces the shell every
   `run:` step is executed with. A shell that swallows non-zero exits —

       defaults:
         run:
           shell: bash -c "eval \"$@\" || true" --

   turns every check in the job into a no-op that reports success. This is the
   GitHub Actions analogue of a Makefile `SHELL := /usr/bin/true`, and it is one
   line.

2. **A step-level `if:`**. A skipped JOB is caught downstream — the fan-in
   refuses a `skipped` conclusion — but a skipped STEP leaves the job green. So
   `if: false` on the ledger check removes the lane's primary assertion while
   `validate` still reports success.

Both are refused here, on the workflows that define a required lane.

On `if:`, the rule is deliberately stricter than "constant false". A literal
`false` is refused by name, but so is any other step-level condition on a
required lane, because nothing here can evaluate
`${{ github.event.repository.owner.login == 'nobody' }}` — and a step that
*might* not run is not a gate either. A required lane's steps run
unconditionally or the lane is not required. (Job-level `if:` is left to the
fan-in, which already refuses a skipped job.)

Job EXISTENCE is also checked here, by parsing. It was previously a grep:

    grep -qE "^  ${check}:[[:space:]]*$" .github/workflows/*.yml

which is indentation-sensitive and matches only `.yml`, while every other
checker globs `.yml` and `.yaml`. A required lane defined in a `.yaml` workflow,
or indented differently, was reported as having no job at all.

Usage:
    check-lane-integrity.py [--required <manifest>] [workflow.yml ...]

Exit codes:
    0  clean
    1  VIOLATION
    2  UNEVALUABLE — a workflow could not be read or parsed; nothing was checked
"""

import argparse
import glob
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only on a runner without PyYAML
    sys.stderr.write(
        "PyYAML is required: this check parses the workflows rather than grepping them.\n"
    )
    sys.exit(2)

FALSE_LITERALS = {"false", "'false'", '"false"', "${{ false }}", "${{false}}"}


def load(path):
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


def normalise(key):
    if not isinstance(key, str):
        return ""
    return key.strip().strip("\"'").strip().lower()


def get(mapping, name):
    """Fetch a key the way a permissive reader would see it."""
    if not isinstance(mapping, dict):
        return None
    for key, value in mapping.items():
        if normalise(key) == name:
            return value
    return None


def shell_override(path, where, node):
    """Refuse defaults.run.shell at this level."""
    defaults = get(node, "defaults")
    if not isinstance(defaults, dict):
        return 0
    run = get(defaults, "run")
    if not isinstance(run, dict):
        return 0
    shell = get(run, "shell")
    if shell is None:
        return 0
    sys.stderr.write(
        f"VIOLATION {path} reason=defaults-shell-override where={where} shell={shell!r}\n"
        f"  `defaults.run.shell` replaces the shell every `run:` step executes in. A shell\n"
        f"  that swallows non-zero exits turns every check in this lane into a no-op that\n"
        f"  still reports success — the Actions analogue of `SHELL := /usr/bin/true`.\n"
    )
    return 1


def conditional_steps(path, job_name, job):
    violations = 0
    steps = get(job, "steps")
    if not isinstance(steps, list):
        return 0
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        condition = get(step, "if")
        if condition is None:
            continue
        name = get(step, "name") or get(step, "uses") or get(step, "run") or f"step {i}"
        rendered = str(condition).strip()
        constant_false = condition is False or rendered.lower() in FALSE_LITERALS
        reason = "constant-false-if" if constant_false else "conditional-step-on-required-lane"
        sys.stderr.write(
            f"VIOLATION {path} reason={reason} lane={job_name} "
            f"where=jobs.{job_name}.steps[{i}] if={rendered!r}\n"
            f"  Step {str(name)[:60]!r} carries an `if:` on a REQUIRED lane.\n"
        )
        if constant_false:
            sys.stderr.write(
                "  It is a constant false, so this step never runs at all while the lane\n"
                "  still reports success. A skipped JOB is refused by the fan-in; a skipped\n"
                "  STEP leaves the job green, which is why it is refused here.\n"
            )
        else:
            sys.stderr.write(
                "  Nothing here can evaluate that expression, and a step that MIGHT not run\n"
                "  is not a gate. A required lane's steps run unconditionally.\n"
            )
        violations += 1
    return violations


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

    lanes = read_manifest(args.required)

    violations = 0
    found = {}
    for path in paths:
        doc = load(path)
        jobs = get(doc, "jobs")
        if not isinstance(jobs, dict):
            continue
        defined_here = [lane for lane in lanes if lane in jobs]
        if not defined_here:
            continue
        # Workflow-level shell override affects every job in the file, including
        # the required one.
        violations += shell_override(path, "workflow", doc)
        for lane in defined_here:
            found.setdefault(lane, []).append(path)
            job = jobs[lane]
            violations += shell_override(path, f"jobs.{lane}", job)
            violations += conditional_steps(path, lane, job)

    missing = [lane for lane in lanes if lane not in found]
    for lane in missing:
        sys.stderr.write(
            f"VIOLATION reason=no-such-job lane={lane}\n"
            f"  Required check '{lane}' has no job of that name in any of "
            f"{len(paths)} workflow file(s). The fan-in would wait for a check nobody defined.\n"
        )
        violations += 1

    if violations:
        return 1
    print(
        f"lane integrity: {len(lanes)} required lane(s) defined by a real job across "
        f"{len(paths)} workflow file(s); no shell override, no conditional step"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
