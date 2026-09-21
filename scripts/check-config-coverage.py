#!/usr/bin/env python3
"""Configuration-key coverage, in both directions, from the rendered models.

Two failures this catches, and they are opposites:

  * a key a component READS that no compose file delivers — the service boots
    with a default nobody chose, or refuses to boot, and the env template the
    operator filled in had no line for it;
  * a key a template DECLARES that nothing consumes — the operator sets it,
    believes it took effect, and it reaches no process. This is the worse of the
    two, because it fails silently and looks configured.

Both are answered from artefacts, never from prose:

  what a component reads    env/registry/<component>.json, a snapshot at a named
                            component commit (see env/registry/README.md for why
                            a snapshot and what that does NOT prove)
  what compose delivers     the rendered `environment:` map of each service, in
                            build/compose-models/*.json
  what compose consumes     `docker compose config --variables`, i.e. Compose's
                            own answer, recorded in shapes.json by
                            scripts/compose-render.py — not a grep for `${`
  what an operator can set   env/*.env.example

Usage:
    check-config-coverage.py [models-dir]      (default build/compose-models)
    check-config-coverage.py --drift           (additionally: snapshot vs. the
                                                live component checkouts)

Exit codes, matching the house convention:
    0  clean
    1  VIOLATION   one `VIOLATION …` line per hit
    2  UNEVALUABLE  an input was missing or unusable; nothing was checked

`--drift` reports BLOCKED and exits 2 when a component checkout is absent. That
is deliberate and it is why drift is a separate flag: this repository's CI has
no token to check out a private sibling repository, so a green `validate` proves
the topology is consistent with the snapshots, NOT that the snapshots are
current. A missing dependency is BLOCKED, never a pass.
"""

import glob
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_DIR = os.path.join(REPO_ROOT, "env", "registry")
COMPONENTS = ("core", "user", "search")
TEMPLATES = {
    "production": os.path.join(REPO_ROOT, "env", "production.env.example"),
    "development": os.path.join(REPO_ROOT, "env", "development.env.example"),
}
DEV_HATCH_PREFIX = "VIZRA_DEV_"

RULES = frozenset({
    "service-key-missing",
    "service-key-unknown",
    "template-key-unused",
    "variable-untemplated",
    "hatch-in-production-template",
    "api-worker-asymmetry",
    "alias-floor",
    "alias-unwired",
    "registry-drift",
    "retired-key-delivered",
    "unclassified-secret-key",
})

# Secondary net only. The registry's explicit `"secret": true` is the primary
# signal; these suffixes catch a key whose author forgot the flag. Deliberately
# NOT `_URL`: DATABASE_URL and VIZRA_CACHE_URL are registry-flagged already,
# while VIZRA_SEARCH_URL is a plain address and matching it would train people
# to add exceptions.
SECRET_NAME_SUFFIXES = ("_PASSWORD", "_SECRET", "_TOKEN", "_KEY")

violations = []


def violation(rule, subject, detail):
    assert rule in RULES, f"undeclared rule id {rule!r}"
    violations.append(f"VIOLATION rule={rule} subject={subject} detail={detail}")


def unevaluable(msg):
    sys.stderr.write("UNEVALUABLE: " + msg.rstrip() + "\n  Nothing was checked.\n")
    sys.exit(2)


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as err:
        unevaluable(f"cannot read {path}: {err}")


def read_template(path):
    """Return the ordered list of KEY names a template declares.

    Commented-out keys do not count: a key an operator must uncomment is a key
    the template does not declare, and treating it as declared would let a
    consumer-less key hide behind a `#`.
    """
    keys = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"^([A-Z][A-Z0-9_]*)=", line)
                if m:
                    keys.append(m.group(1))
    except OSError as err:
        unevaluable(f"cannot read {path}: {err}")
    if not keys:
        unevaluable(
            f"{path} declares no keys at all. An empty template satisfies "
            f"'every template key has a consumer' trivially."
        )
    return keys


def main(argv):
    drift_only = "--drift" in argv
    positional = [a for a in argv[1:] if not a.startswith("--")]
    models_dir = os.path.join(
        REPO_ROOT, positional[0] if positional else "build/compose-models"
    )

    registries = {c: read_json(os.path.join(REGISTRY_DIR, f"{c}.json"))
                  for c in COMPONENTS}
    aliases = read_json(os.path.join(REGISTRY_DIR, "aliases.json"))

    if drift_only:
        return check_drift(registries)

    manifest_path = os.path.join(models_dir, "shapes.json")
    if not os.path.exists(manifest_path):
        unevaluable(
            f"{manifest_path} is missing. Run ./scripts/compose-render.py --all "
            f"--out {os.path.relpath(models_dir, REPO_ROOT)} first."
        )
    manifest = read_json(manifest_path)
    shapes = {s["id"]: s for s in manifest.get("shapes") or []}
    if not shapes:
        unevaluable(f"{manifest_path} declares no shapes.")

    models = {}
    for path in sorted(glob.glob(os.path.join(models_dir, "*.json"))):
        if os.path.basename(path) == "shapes.json":
            continue
        models[os.path.basename(path)[:-5]] = read_json(path)
    missing_models = sorted(set(shapes) - set(models))
    if missing_models:
        unevaluable(
            f"shapes {missing_models} are declared but have no rendered model in "
            f"{models_dir}. A shape that produced no model was not checked."
        )

    templates = {name: read_template(p) for name, p in TEMPLATES.items()}
    all_template_keys = set(templates["production"]) | set(templates["development"])

    # --- 1. Every key a component reads is delivered to every service of that
    #        component, in every shape where the service renders. ------------
    for comp, reg in registries.items():
        declared = {k["name"] for k in reg["keys"]}
        extra_ok = set(reg.get("non_registry_env") or [])
        for sid, model in models.items():
            kind = shapes[sid]["kind"]
            for svc_name in reg["services"]:
                svc = (model.get("services") or {}).get(svc_name)
                if svc is None:
                    continue  # not selected in this shape; membership is
                              # check-compose-topology.py's job, not this one
                env = set((svc.get("environment") or {}).keys())
                for key in sorted(declared - env):
                    violation(
                        "service-key-missing",
                        f"{sid}/{svc_name}/{key}",
                        f"vizra-{comp} reads {key} (env/registry/{comp}.json at "
                        f"{reg['source_commit'][:12]}) but the rendered "
                        f"environment map does not deliver it, so the service "
                        f"gets its built-in default and the operator has no way "
                        f"to change it",
                    )
                allowed = declared | extra_ok
                if kind == "development":
                    allowed |= {
                        k for k in env if k.startswith(DEV_HATCH_PREFIX)
                    } & set(reg.get("escape_hatches") or [])
                for key in sorted(env - allowed):
                    violation(
                        "service-key-unknown",
                        f"{sid}/{svc_name}/{key}",
                        f"is delivered to {svc_name} but vizra-{comp} declares "
                        f"no such key; it reaches the container and nothing "
                        f"reads it",
                    )

    # --- 1b. A RETIRED key must never be delivered. --------------------------
    #
    # This is not the same rule as service-key-unknown, and the difference is
    # the whole point. An unknown key is merely useless: it reaches the
    # container and nothing reads it. A RETIRED key is actively fatal —
    # vizra-core refuses a retired name in production ON PRESENCE with any
    # non-empty value, so a "belt and braces" map that sets both the old and the
    # new spelling is a guaranteed boot refusal.
    #
    # The 3am scenario this exists to prevent: core's rename merges, the
    # operator pulls the new image, and `vizra migrate`, `vizra-api` and
    # `vizra-worker` all refuse to start naming a variable that appears NOWHERE
    # in their env file, because compose injects it. They grep production.env,
    # find the key the template told them to set, and have no path forward
    # without reading docker-compose.yml.
    for comp, reg in registries.items():
        retired = set(reg.get("retired_keys") or [])
        if not retired:
            continue
        for sid, model in sorted(models.items()):
            for svc_name in reg["services"]:
                svc = (model.get("services") or {}).get(svc_name)
                if svc is None:
                    continue
                for key in sorted(retired & set((svc.get("environment") or {}).keys())):
                    violation(
                        "retired-key-delivered",
                        f"{sid}/{svc_name}/{key}",
                        f"vizra-{comp} has RETIRED {key} (env/registry/{comp}.json "
                        f"at {reg['source_commit'][:12]}) and refuses it in "
                        f"production on presence, but the rendered model still "
                        f"delivers it - every container running that image would "
                        f"refuse to boot, naming a variable the operator's env "
                        f"file does not contain",
                    )

    # --- 1c. A secret must be CLASSIFIED, not merely flagged. ---------------
    #
    # scripts/compose-render.py derives its redaction set from these same flags,
    # so a newly flagged key is protected on the bytes immediately. This rule is
    # the other half: it makes the author say so in the manifest, because the
    # manifest is what a reader consults to learn what the artifact protects,
    # and a set that is only ever implicit cannot be reviewed.
    #
    # The failure it prevents was reproduced by the verifier: a key added the
    # FULLY correct way — `"secret": true` in the registry, an entry in the
    # template, delivered by compose — was written raw into all thirteen models,
    # 47 occurrences, stamped `secret_values_redacted: true`, with all four lane
    # checkers green. Nothing connected the registry's own flag to the
    # redaction set.
    try:
        with open(os.path.join(REPO_ROOT, "scripts", "compose-shapes.json"),
                  "r", encoding="utf-8") as fh:
            shapes_manifest = json.load(fh)
    except (OSError, ValueError) as err:
        unevaluable(f"cannot read scripts/compose-shapes.json: {err}")
    declared_redact = set(shapes_manifest.get("redact_keys") or [])
    allowed_lookalikes = set(shapes_manifest.get("not_secret_despite_name") or [])

    flagged = set()
    for comp, reg in registries.items():
        for k in reg["keys"]:
            if k.get("secret"):
                flagged.add(k["name"])
    for key in sorted(flagged - declared_redact):
        violation(
            "unclassified-secret-key", key,
            f"is marked \"secret\": true in a component registry but is not in "
            f"`redact_keys` in scripts/compose-shapes.json. The renderer derives "
            f"its redaction set from the same flag so the value is not written, "
            f"but the manifest is what a reader consults to learn what the "
            f"artifact protects - classify it there too",
        )
    for key in sorted(set(templates["production"]) | set(templates["development"])):
        if key in declared_redact or key in flagged or key in allowed_lookalikes:
            continue
        if key.endswith(SECRET_NAME_SUFFIXES):
            violation(
                "unclassified-secret-key", key,
                f"is named like a secret ({[x for x in SECRET_NAME_SUFFIXES if key.endswith(x)][0]}) "
                f"but is neither flagged secret in a registry nor listed in "
                f"`redact_keys`. If it really is not a secret, add it to "
                f"`not_secret_despite_name` in scripts/compose-shapes.json with "
                f"the reason - one declared exception beats a matcher nobody trusts",
            )

    # --- 2. api and worker run the SAME binary: identical key sets or one half
    #        is configured differently than its operator believes. -----------
    for sid, model in models.items():
        svcs = model.get("services") or {}
        if "api" not in svcs or "worker" not in svcs:
            continue
        a = set((svcs["api"].get("environment") or {}).keys())
        w = set((svcs["worker"].get("environment") or {}).keys())
        if a != w:
            violation(
                "api-worker-asymmetry",
                sid,
                f"api-only={sorted(a - w)} worker-only={sorted(w - a)}; they run "
                f"the same vizra-core binary and must read the same keys",
            )

    # --- 3. Template keys have a consumer, and consumed variables have a
    #        template entry. Compose is the authority on both sides. --------
    consumed = set(manifest.get("interpolation_variables") or [])
    if not consumed:
        unevaluable(
            f"{manifest_path} records no interpolation variables, so every "
            f"template key would be reported unused."
        )
    for name, keys in templates.items():
        for key in keys:
            if key not in consumed:
                violation(
                    "template-key-unused",
                    f"env/{name}.env.example/{key}",
                    "no compose file in any rendered shape interpolates it, so "
                    "setting it does nothing at all",
                )
    for key in sorted(consumed - all_template_keys):
        violation(
            "variable-untemplated",
            key,
            "a compose file interpolates it but no env template declares it, so "
            "an operator has no documented place to set it",
        )

    # --- 4. No development escape hatch in the production template. ---------
    for key in templates["production"]:
        if key.startswith(DEV_HATCH_PREFIX):
            violation(
                "hatch-in-production-template",
                key,
                "vizra-core refuses every VIZRA_DEV_* key by name in production "
                "and refuses VIZRA_DEV_AUTOLOGIN_USER on presence; the "
                "production template must not invite an operator to set one",
            )

    # --- 5. The alias table is a floor and every entry is really wired. -----
    declared_aliases = aliases.get("aliases") or []
    floor = aliases.get("floor")
    if floor != len(declared_aliases):
        violation(
            "alias-floor",
            "env/registry/aliases.json",
            f"declares floor={floor} but lists {len(declared_aliases)} alias(es). "
            f"Every alias is a place an operator can believe they configured "
            f"something they did not, so adding or removing one must be a "
            f"visible edit that moves the floor in the same diff",
        )
    for al in declared_aliases:
        op_key = al["operator_key"]
        # An alias must be a DECISION. Without this, the table records that
        # somebody wrote a paragraph about a naming conflict, which is not the
        # same as somebody having ruled on it - and the second alias sat in
        # exactly that state ("NOT YET RULED ON") while reading as declared.
        if "authorised" not in al:
            violation(
                "alias-floor", op_key,
                "is declared as an alias with no `authorised` field. Every "
                "alias is a place an operator can believe they configured "
                "something they did not, so it needs an explicit decision and "
                "the authority for it, not a description",
            )
        elif not al["authorised"]:
            violation(
                "alias-floor", op_key,
                f"is declared with authorised=false, so it is not authorised "
                f"and must not be wired: {al.get('authorised_by', '(no reason given)')}",
            )
        if op_key not in all_template_keys:
            violation(
                "alias-unwired",
                op_key,
                "is declared as the operator-facing key of an alias but no "
                "template declares it",
            )
        for sk in al["service_keys"]:
            comp = sk["component"].replace("vizra-", "")
            reg = registries.get(comp)
            if reg is None or sk["key"] not in {k["name"] for k in reg["keys"]}:
                violation(
                    "alias-unwired",
                    f"{sk['component']}/{sk['key']}",
                    f"is declared as an alias target but {sk['component']}'s "
                    f"registry snapshot does not list it; the alias may already "
                    f"have been resolved upstream",
                )

    if violations:
        for line in violations:
            sys.stderr.write(line + "\n")
        sys.stderr.write(f"\n{len(violations)} violation(s).\n")
        return 1

    # Printed on every GREEN run, like the known-false probe list: an alias is a
    # standing compromise and should have to be looked at, not filed once.
    if declared_aliases:
        print(f"ALIASES: {len(declared_aliases)} operator key(s) feeding two service spellings")
        for al in declared_aliases:
            spellings = ", ".join(
                f"{sk['component']}:{sk['key']}" for sk in al["service_keys"]
            )
            print(f"  - {al['operator_key']} -> {spellings}")
            print(f"      authorised: {al.get('authorised')}  by {al.get('authorised_by')}")
            print(f"      removed when: {al.get('removed_when')}")

    total_keys = sum(len(r["keys"]) for r in registries.values())
    print(
        f"config coverage: {total_keys} component keys across "
        f"{len(registries)} components, {len(all_template_keys)} template keys, "
        f"{len(consumed)} interpolated variables, {len(models)} shapes; "
        f"{len(declared_aliases)} declared alias(es); "
        f"{sum(len(r.get('retired_keys') or []) for r in registries.values())} "
        f"retired key(s) refused; 0 violations"
    )
    return 0


# --------------------------------------------------------------------------

def check_drift(registries):
    """Snapshot vs. the live component source. BLOCKED when absent."""
    blocked = []
    for comp, reg in registries.items():
        root = os.path.join(REPO_ROOT, f"vizra-{comp}")
        if not os.path.isdir(root):
            blocked.append(f"vizra-{comp}")
            continue
        found = set()
        for rel in reg["source_files"]:
            path = os.path.join(root, rel)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                blocked.append(f"vizra-{comp}/{rel}")
                continue
            # Every env key this component could read appears as a quoted
            # literal in its own registry source. This is a coarse net on
            # purpose: it over-reports rather than under-reports, and an
            # over-report is a snapshot that needs a human look.
            for m in re.finditer(r'["\'`]([A-Z][A-Z0-9_]{2,})["\'`]', text):
                found.add(m.group(1))
            # A Dockerfile writes `ENV PORT=3000` unquoted, so the quoted-literal
            # scan alone reported PORT and HOSTNAME as removed keys.
            for m in re.finditer(r'(?m)^\s*ENV\s+([A-Z][A-Z0-9_]{2,})=', text):
                found.add(m.group(1))
        # A RETIRED name legitimately still appears in the component's source —
        # that is where the refusal is implemented — and the snapshot accounts
        # for it under `retired_keys`. Without this it is reported as an
        # undeclared key, which would push an author toward deleting the
        # retired-key declaration to silence the drift check: the one edit that
        # would let the old spelling come back unnoticed.
        known = (
            {k["name"] for k in reg["keys"]}
            | set(reg.get("escape_hatches") or [])
            | set(reg.get("retired_keys") or [])
        )
        ignore = set(reg.get("drift_ignore") or [])
        new = sorted(found - known - ignore)
        gone = sorted(k for k in known if k not in found)
        for key in new:
            violation(
                "registry-drift", f"vizra-{comp}/{key}",
                f"appears in {reg['source_files']} but not in "
                f"env/registry/{comp}.json (snapshot at "
                f"{reg['source_commit'][:12]}). Either it is a new config key "
                f"and the snapshot is stale, or it is not a config key and "
                f"belongs in that file's `drift_ignore`",
            )
        for key in gone:
            violation(
                "registry-drift", f"vizra-{comp}/{key}",
                f"is in env/registry/{comp}.json but no longer appears in "
                f"{reg['source_files']}; the component may have removed it",
            )

    if blocked:
        sys.stderr.write(
            "BLOCKED: the drift check needs the component checkouts and these "
            "are absent:\n"
        )
        for b in blocked:
            sys.stderr.write(f"  - {b}\n")
        sys.stderr.write(
            "  This is BLOCKED, not a pass and not a skip. Run bootstrap.sh (or\n"
            "  clone the components) and run this again. It cannot run in this\n"
            "  repository's CI at all: there is no token for a private sibling\n"
            "  repository, which is why env/registry/*.json are snapshots.\n"
        )
        return 2

    if violations:
        for line in violations:
            sys.stderr.write(line + "\n")
        sys.stderr.write(f"\n{len(violations)} drift violation(s).\n")
        return 1
    print("config registry drift: every snapshot matches its component source")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
