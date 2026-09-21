#!/usr/bin/env python3
"""A template may not tell an operator to run a command that does not exist.

The failure this exists to prevent is not a typo. It is this line, which shipped
in `env/production.env.example` and was caught in review:

    # ROTATING THIS RE-SEALS STORED MFA SECRETS. `vizra setup --rotate` requires
    # --yes-i-know for exactly this key.
    VIZRA_MFA_KEY_KEK=

`vizra setup` does not exist. `vizra` has three subcommands. An operator who
believed that sentence, edited the key and restarted would not have re-sealed
anything: every TOTP secret in the database stays sealed under the old key and
becomes permanently undecryptable, and every MFA-enrolled member is locked out.
The sentence that caused it is the one they trusted — in a file whose entire job
is to be edited by hand.

So the rule is not "documentation should be accurate". It is: **an operator-
facing file may only name a command that exists, or one explicitly marked as not
yet existing.** Two passes, because the two failures are different:

  A. UNKNOWN COMMAND — a backtick-quoted `vizra <sub>` / `vizra-search <sub>`
     that is in neither the shipped set nor the declared future set. Backticks
     are how this repository writes commands; prose mentions ("vizra has three
     subcommands") are deliberately not scanned, because a regex over prose
     produces false positives that train people to silence the checker.

  B. UNMARKED FUTURE COMMAND — a declared future command named ANYWHERE, with
     or without backticks, without that command's declared marker within
     `MARKER_WINDOW` lines. This pass is the strict one on purpose: pass A
     can be evaded by dropping backticks, and the dangerous direction is
     promising a capability that does not exist. Every future command is named
     in `env/registry/*.json` `future_commands` together with the marker that
     must accompany it, so "marked as future" is mechanical rather than a
     judgement about tone. The marker must sit within `MARKER_WINDOW` lines of
     the promise — see the note on that constant for why the whole comment
     block was too wide a window to be worth anything.

Sources scanned: `env/*.env.example` and `docker-compose*.yml` comments — the
two operator-facing surfaces of this repository. Shipped and future commands
come from `env/registry/*.json`, which is read from the component checkouts at
a recorded commit.

Usage:
    check-template-claims.py [file ...]      (default: the two globs above)

Exit codes, matching the house convention:
    0  clean
    1  VIOLATION   one `VIOLATION …` line per hit
    2  UNEVALUABLE  an input was missing or unusable; nothing was checked
"""

import glob
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_DIR = os.path.join(REPO_ROOT, "env", "registry")
COMPONENTS = ("core", "user", "search")

RULES = frozenset({"unknown-command", "unmarked-future-command"})

# `vizra setup --rotate` → ("vizra", "setup"). A trailing flag is ignored: the
# claim being made is about the subcommand.
BACKTICKED = re.compile(r"`(vizra|vizra-search)\s+([a-z][a-z0-9-]*)")

violations = []


def violation(rule, path, lineno, detail):
    assert rule in RULES, f"undeclared rule id {rule!r}"
    violations.append(f"VIOLATION rule={rule} at={path}:{lineno} detail={detail}")


def unevaluable(msg):
    sys.stderr.write("UNEVALUABLE: " + msg.rstrip() + "\n  Nothing was checked.\n")
    sys.exit(2)


# How far from a future-command reference its marker may sit, in lines.
#
# This was the whole comment BLOCK, and that was wrong in a way the red
# demonstration caught: the sentence this checker exists to refuse —
#
#     # ROTATING THIS RE-SEALS STORED MFA SECRETS. `vizra setup --rotate` requires
#     # --yes-i-know for exactly this key.
#
# sits in the same block as a later, correct sentence that does name
# VZ-ISSUE-004. With the block as the window, the correct sentence LAUNDERED the
# false one and the checker passed. A marker five lines away does not qualify a
# present-tense claim; it just happens to share a comment.
#
# +/- 2 lines is the width of a wrapped sentence, which is the unit a reader
# actually takes the claim from. It is deliberately narrow enough that a promise
# must carry its own qualifier rather than borrow a neighbour's.
MARKER_WINDOW = 2


def marker_context(lines, i):
    """The reference line plus MARKER_WINDOW lines either side."""
    lo = max(0, i - MARKER_WINDOW)
    hi = min(len(lines), i + MARKER_WINDOW + 1)
    return "\n".join(lines[lo:hi])


def main(argv):
    registries = {}
    for comp in COMPONENTS:
        path = os.path.join(REGISTRY_DIR, f"{comp}.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                registries[comp] = json.load(fh)
        except (OSError, ValueError) as err:
            unevaluable(f"cannot read {path}: {err}")

    shipped = set()
    future = {}
    for comp, reg in registries.items():
        if "commands" not in reg:
            unevaluable(
                f"env/registry/{comp}.json declares no `commands` list. Without "
                f"one every command reference would be reported unknown, or - "
                f"worse, if the default were permissive - none would."
            )
        shipped.update(reg["commands"])
        future.update(reg.get("future_commands") or {})

    if not shipped:
        unevaluable(
            "no component declares a single shipped command, so this checker "
            "would refuse every reference or allow every one."
        )

    targets = [a for a in argv[1:] if not a.startswith("--")]
    if not targets:
        targets = sorted(
            glob.glob(os.path.join(REPO_ROOT, "env", "*.env.example"))
            + glob.glob(os.path.join(REPO_ROOT, "docker-compose*.yml"))
        )
    if not targets:
        unevaluable(
            "no operator-facing file matched. An empty scan passes trivially."
        )

    scanned = 0
    refs = 0
    for path in targets:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as err:
            unevaluable(f"cannot read {path}: {err}")
        rel = os.path.relpath(path, REPO_ROOT)
        scanned += 1

        for i, line in enumerate(lines):
            ctx = marker_context(lines, i)

            # --- pass A: a backticked command that is neither shipped nor declared
            for m in BACKTICKED.finditer(line):
                cmd = f"{m.group(1)} {m.group(2)}"
                refs += 1
                if cmd in shipped or cmd in future:
                    continue
                violation(
                    "unknown-command", rel, i + 1,
                    f"names `{cmd}`, which no component declares as shipped "
                    f"(shipped: {sorted(shipped)}) and which is not in any "
                    f"future_commands table. An operator-facing file may not "
                    f"name a command that does not exist",
                )

            # --- pass B: a declared future command must carry its marker
            for cmd, marker in sorted(future.items()):
                if cmd not in line:
                    continue
                if marker in ctx:
                    continue
                violation(
                    "unmarked-future-command", rel, i + 1,
                    f"names the UNIMPLEMENTED command {cmd!r} with no "
                    f"{marker!r} within {MARKER_WINDOW} line(s), so it reads as "
                    f"something an operator can run today. A qualifier further "
                    f"down the same comment block does not count - it launders "
                    f"the claim instead of qualifying it. Either name the slice "
                    f"beside the promise, or do not make it",
                )

    if violations:
        for line in violations:
            sys.stderr.write(line + "\n")
        sys.stderr.write(f"\n{len(violations)} violation(s).\n")
        return 1

    print(
        f"template claims: {scanned} operator-facing file(s), {refs} command "
        f"reference(s); {len(shipped)} shipped command(s), {len(future)} "
        f"declared future command(s); 0 violations"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
