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

  A'. SCRIPTS get the same two passes, against `env/registry/meta.json`:
     a script that exists in the tree may be named freely; one declared in
     `future_scripts` needs its marker within `MARKER_WINDOW`; anything else is
     refused outright.

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

RULES = frozenset({"unknown-command", "unmarked-future-command",
                   "unknown-script", "unmarked-future-script"})

# `vizra setup --rotate` → ("vizra", "setup"). A trailing flag is ignored: the
# claim being made is about the subcommand.
BACKTICKED = re.compile(r"`(vizra|vizra-search)\s+([a-z][a-z0-9-]*)")

# ANY `*.sh` token, with or without a path prefix, with or without backticks.
#
# The checker used to match only `vizra <sub>`, so every claim about a SHELL
# SCRIPT was outside its scope — and `backup.sh refuses to back the cache up,
# and says so` survived round 1 in two operator-facing files for a script that
# does not exist. An operator cannot tell a Go subcommand from a shell script
# and does not care: the failure this checker prevents is about belief, not
# provenance.
#
# The FIRST fix was narrower than its own comment, which read "backticked or
# bare". It listed six names and excluded `.`, `/` and `-` in a lookbehind, so
# the two spellings an operator-facing document actually uses for a runnable
# script — `./backup.sh` and `scripts/backup.sh` — both passed unmarked, and a
# backticked `` `./backup.sh` `` with them. Worse, because the six matchable
# names were exactly the six declared future, the `unknown-script` branch was
# UNREACHABLE from any documentation edit: a rule id that cannot fire is a
# control that does not exist, which AGENTS.md forbids listing as one
# (verifier S-3).
#
# So the matcher is now general and the REGISTRIES decide, which is the right
# division: an invented `rotate-secrets.sh` reaches `unknown-script`, a declared
# future one needs its marker, and a script that exists in the tree may be named
# freely. The lookbehind keeps `.`/`/` out only so a match cannot start in the
# middle of a longer word; a path prefix is consumed rather than excluded.
SCRIPTNAME = re.compile(
    r"(?<![\w.-])(?:\.{0,2}/)?(?:[A-Za-z0-9_.-]+/)*"
    r"([A-Za-z0-9_][A-Za-z0-9_.-]*\.sh)\b"
)

# Directories a bare script name is looked for in, in order, when deciding
# whether it EXISTS. A script that exists may be named freely, and it is checked
# on disk rather than trusted from the registry so that a script landing makes
# its references legal in the same commit.
SCRIPT_DIRS = ("", "scripts", "deploy")

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


def script_on_disk(ref, name):
    """Does the script this reference names exist in THIS repository?

    `ref` is the whole matched token as written (`./backup.sh`,
    `scripts/backup.sh`, `backup.sh`); `name` is its basename. A path form is
    resolved literally, and every form is additionally looked for in
    SCRIPT_DIRS, because a document that writes the bare name means the script
    wherever it lives.

    A reference that resolves OUTSIDE the repository (`../../thing.sh`) is
    reported as not existing rather than followed. Fail closed: the caller then
    refuses it as `unknown-script`, which is the correct answer for a path an
    operator cannot run from a deployment bundle either.
    """
    candidates = [ref.lstrip("./")] if "/" in ref else []
    candidates += [
        os.path.join(d, name) if d else name for d in SCRIPT_DIRS
    ]
    for rel in candidates:
        path = os.path.normpath(os.path.join(REPO_ROOT, rel))
        if not path.startswith(REPO_ROOT + os.sep):
            continue
        if os.path.exists(path):
            return True
    return False


def main(argv):
    registries = {}
    for comp in COMPONENTS:
        path = os.path.join(REGISTRY_DIR, f"{comp}.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                registries[comp] = json.load(fh)
        except (OSError, ValueError) as err:
            unevaluable(f"cannot read {path}: {err}")

    meta_path = os.path.join(REGISTRY_DIR, "meta.json")
    try:
        with open(meta_path, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
    except (OSError, ValueError) as err:
        unevaluable(f"cannot read {meta_path}: {err}")
    if "future_scripts" not in meta:
        unevaluable(
            f"{meta_path} declares no `future_scripts`, so every script "
            f"reference would be refused or - worse, if the default were "
            f"permissive - none would."
        )
    # A script that actually exists may be named freely; the declaration is only
    # about the ones that do not. Checked on disk rather than trusted from the
    # registry, so a script landing makes its references legal automatically.
    declared_present = {
        n for n in meta.get("scripts", [])
        if os.path.exists(os.path.join(REPO_ROOT, n))
    }
    future_scripts = {
        k: v for k, v in meta["future_scripts"].items()
        if k not in declared_present and not script_on_disk(k, k)
    }

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
    resolved_on_disk = set()
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

            # --- pass A': a script must exist, or be declared and marked
            for m in SCRIPTNAME.finditer(line):
                ref, name = m.group(0), m.group(1)
                refs += 1
                if name in declared_present or script_on_disk(ref, name):
                    resolved_on_disk.add(name)
                    continue
                if name not in future_scripts:
                    violation(
                        "unknown-script", rel, i + 1,
                        f"names the script {ref!r}, which does not exist in "
                        f"this repository (looked for it as written and in "
                        f"{'/, '.join(d or '.' for d in SCRIPT_DIRS)}/) and is "
                        f"not declared in env/registry/meta.json "
                        f"`future_scripts`. An operator-facing file may not "
                        f"name a script that does not exist",
                    )
                    continue
                if future_scripts[name] not in ctx:
                    violation(
                        "unmarked-future-script", rel, i + 1,
                        f"names {ref!r} with no {future_scripts[name]!r} within "
                        f"{MARKER_WINDOW} line(s). No such script exists, so the "
                        f"sentence reads as a description of current behaviour - "
                        f"and an operator who believes a backup tool exists "
                        f"defers setting up provider snapshots until they have "
                        f"checked what it does",
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
        f"and script reference(s); {len(shipped)} shipped command(s), "
        f"{len(future)} declared future command(s), "
        f"{len(resolved_on_disk)} script reference(s) resolved to a file in the "
        f"tree and {len(future_scripts)} script(s) declared future; 0 violations"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
