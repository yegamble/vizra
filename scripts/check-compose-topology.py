#!/usr/bin/env python3
"""Assert the declared compose topology from RENDERED models.

Every rule here reads `docker compose config --format json` output parsed as
JSON. None of them greps YAML. That is not a style preference: a grep over the
source files answers a different question from the one an operator cares about.
What is reachable on a host is decided by the MERGED model — after the `-f`
chain, after profile selection, after `!override`/`!reset`, after interpolation
— and a source file can look closed while the merge opens it, or look open while
a later overlay closes it. Only the rendered model knows.

The one place YAML is parsed is `locate_in_sources()`, which runs AFTER a rule
has already failed, purely to tell the operator WHICH FILE to edit. It is a
diagnostic, never an assertion: if it finds nothing the violation still stands.

Usage:
    check-compose-topology.py <models-dir>

`<models-dir>` holds one `<shape-id>.json` per rendered shape, as written by
`scripts/compose-render.py`, plus the `shapes.json` manifest copied beside them
so this checker never has to re-read the repository to know what it is looking
at.

Exit codes are a three-way answer, matching the house convention in
`scripts/check-workflows.py`, because "I rejected this" and "I could not read
this" are different facts and `ci-required-guard.sh`-style fixture harnesses
must not confuse them:

    0  clean        every rule passed on every shape
    1  VIOLATION    at least one rule failed; one `VIOLATION …` line per hit
    2  UNEVALUABLE  a model was missing, unreadable or unparseable, or the
                    shape manifest disagreed with the models present — nothing
                    was checked

Each violation prints a machine-readable line to stderr:

    VIOLATION shape=<id> rule=<rule-id> service=<name> detail=<...> file=<...>

`rule=` is the stable identifier a negative fixture declares it must trip, so a
fixture that is rejected for the WRONG reason is caught (the same hole
`ci-required-guard.sh` closes for the workflow checkers).
"""

import json
import os
import sys

# PyYAML is used ONLY by locate_in_sources(), which names the file to edit
# after a rule has already failed. Every assertion below reads the rendered
# JSON model and needs no YAML parser at all, so a missing PyYAML degrades the
# error messages and must never decide whether the topology is asserted.
# It is announced loudly rather than swallowed.
try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None
    sys.stderr.write(
        "NOTE: PyYAML is not installed, so violations below will not name the "
        "source file to edit.\n      Every rule still runs: they read the "
        "rendered JSON model, not the YAML.\n      Install it with "
        "`python3 -m pip install --break-system-packages pyyaml==6.0.3`.\n"
    )


# --------------------------------------------------------------------------
# Declared facts about the topology. These are FLOORS: changing one is a
# decision that must be made in the diff, not a consequence of whatever the
# compose files happen to say today.
# --------------------------------------------------------------------------

# Services that run to completion and exit. They never restart, and in a
# production shape they never carry `build:` — `deploy.sh` runs them from the
# release image with `up -d --no-build` (ADR-002 § Release and deploy).
ONE_SHOT_SERVICES = frozenset({"migrate", "search-migrate"})

# Services that must NEVER publish a port in ANY shape — not in production, not
# in the developer override, not with every optional profile enabled. A
# datastore or an internal service reachable from off-host is the incident this
# whole file exists to prevent (docs/META_REPO.md §2 rule 3).
NEVER_PUBLISHED_SERVICES = frozenset({
    "postgres",
    "redis",
    "search",
    "search-migrate",
    "migrate",
    "worker",
    "clickhouse",
    "minio",
    "clamav",
    "otel-collector",
    "jaeger",
})

# Services that may publish, but only on loopback, and only where a shape's
# `published_allow` says so.
LOOPBACK_HOST_IPS = frozenset({"127.0.0.1", "::1"})

# `caddy` is the only service allowed to face the network, and only on the
# `edge` profile (VZ-TOPOLOGY-006).
EDGE_SERVICE = "caddy"
EDGE_PROFILE = "edge"

# The rule ids a negative fixture may declare. Listed so a typo in a fixture
# declaration is caught rather than silently matching nothing.
RULES = frozenset({
    "never-published",
    "public-bind",
    "port-not-allowed",
    "edge-profile",
    "missing-restart",
    "oneshot-restart",
    "missing-log-cap",
    "missing-healthcheck",
    "production-build",
    "unpinned-image",
    "docker-socket",
    "no-new-privileges",
    "privileged",
    "host-network",
    "missing-service",
    "unexpected-service",
    "missing-build",
    "dev-mode-in-production",
    "dev-hatch-in-production",
})

# vizra-core refuses every one of these by name when VIZRA_MODE=production, and
# VIZRA_DEV_AUTOLOGIN_USER is refused on PRESENCE with a non-empty value. They
# reach a container only through docker-compose.override.yml, which the
# production `-f` chain never loads — so finding one in a production model means
# the override leaked into the chain.
DEV_HATCH_PREFIX = "VIZRA_DEV_"

# The services that run the vizra-core binary and therefore read VIZRA_MODE.
CORE_SERVICES = frozenset({"api", "worker", "migrate"})


violations = []


def violation(shape, rule, service, detail, path=None):
    assert rule in RULES, f"undeclared rule id {rule!r}"
    line = (
        f"VIOLATION shape={shape} rule={rule} service={service} detail={detail}"
    )
    if path:
        line += f" file={path}"
    violations.append(line)


# --------------------------------------------------------------------------
# The diagnostic locator. Parses the SOURCE yaml to name the file an operator
# should edit. Never decides anything.
# --------------------------------------------------------------------------

def locate_in_sources(files, service, key, repo_root):
    """Return the first source file that sets `key` on `service`, or None."""
    if yaml is None:
        return None
    for rel in files:
        path = os.path.join(repo_root, rel)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                # The compose files carry `!override` / `!reset` tags, which
                # safe_load refuses. They are irrelevant to "which file mentions
                # this key", so unknown tags are ignored rather than fatal — a
                # locator that crashes would replace a precise violation message
                # with a stack trace.
                class Tolerant(yaml.SafeLoader):
                    pass

                Tolerant.add_multi_constructor(
                    "", lambda loader, suffix, node: None
                )
                doc = yaml.load(fh, Loader=Tolerant)
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(doc, dict):
            continue
        svc = (doc.get("services") or {}).get(service)
        if isinstance(svc, dict) and key in svc:
            return rel
    return None


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

def port_entries(svc):
    """Normalise the rendered `ports` list.

    A rendered entry looks like
        {"mode":"ingress","host_ip":"127.0.0.1","target":8080,
         "published":"8080","protocol":"tcp"}
    `host_ip` is ABSENT when the compose file did not name one, and an absent
    host_ip means every interface — which is exactly the dangerous case. It is
    therefore normalised to the string "0.0.0.0" rather than to None, so no rule
    can accidentally treat "unspecified" as "closed".
    """
    out = []
    for entry in svc.get("ports") or []:
        if isinstance(entry, dict):
            out.append((
                entry.get("host_ip") or "0.0.0.0",
                str(entry.get("published") or ""),
                entry.get("target"),
                entry.get("protocol") or "tcp",
            ))
        else:  # short syntax should never survive rendering, but fail loudly
            out.append(("0.0.0.0", str(entry), None, "tcp"))
    return out


def check_ports(shape, model, repo_root):
    sid = shape["id"]
    # allow[service] -> {published port: faces_network?}
    #
    # A port may be allowed AND still be required to be loopback. The two are
    # separate permissions on purpose: `"public": true` is the only way a port
    # faces the network, it has to be written per port per shape, and it carries
    # a `reason` in the manifest. Today exactly two services hold it — caddy
    # (80/443, the edge) and ipfs (4001, the swarm port a node must be dialled
    # on). Everything else that publishes at all publishes on 127.0.0.1.
    allow = {}
    for item in shape.get("published_allow") or []:
        allow[item["service"]] = {
            str(p): bool(item.get("public", False)) for p in item["ports"]
        }

    for name, svc in sorted((model.get("services") or {}).items()):
        entries = port_entries(svc)
        if not entries:
            continue
        where = locate_in_sources(shape["files"], name, "ports", repo_root)

        if name in NEVER_PUBLISHED_SERVICES:
            for host_ip, published, target, _ in entries:
                violation(
                    sid, "never-published", name,
                    f"publishes {host_ip}:{published}->{target}; this service "
                    f"must publish nothing in any shape",
                    where,
                )
            continue

        permitted = allow.get(name) or {}
        for host_ip, published, target, _ in entries:
            if published not in permitted:
                violation(
                    sid, "port-not-allowed", name,
                    f"publishes {host_ip}:{published}->{target}, which this "
                    f"shape does not allow",
                    where,
                )
                continue
            # Allowed to publish this port — but facing the network is a second,
            # separate permission that must be written out per port.
            if not permitted[published] and host_ip not in LOOPBACK_HOST_IPS:
                violation(
                    sid, "public-bind", name,
                    f"binds {host_ip}:{published}, but this shape allows that "
                    f"port only on loopback "
                    f"({'/'.join(sorted(LOOPBACK_HOST_IPS))}); a port faces the "
                    f"network only with an explicit \"public\": true and a "
                    f"reason in scripts/compose-shapes.json",
                    where,
                )


def check_edge(shape, model, repo_root):
    sid = shape["id"]
    svc = (model.get("services") or {}).get(EDGE_SERVICE)
    if svc is None:
        return
    profiles = svc.get("profiles") or []
    if EDGE_PROFILE not in profiles:
        violation(
            sid, "edge-profile", EDGE_SERVICE,
            f"declares profiles {profiles!r}; it must carry the "
            f"{EDGE_PROFILE!r} profile so a TLS-external operator never starts "
            f"a second web server (VZ-TOPOLOGY-006)",
            locate_in_sources(shape["files"], EDGE_SERVICE, "profiles", repo_root),
        )


def check_lifecycle(shape, model, repo_root):
    """restart policy, log cap, healthcheck — per docs/META_REPO.md §2 rule 4."""
    sid = shape["id"]
    for name, svc in sorted((model.get("services") or {}).items()):
        one_shot = name in ONE_SHOT_SERVICES
        restart = svc.get("restart")

        if one_shot:
            if restart not in (None, "no"):
                violation(
                    sid, "oneshot-restart", name,
                    f"restart={restart!r}; a one-shot that restarts re-runs "
                    f"migrations in a loop",
                    locate_in_sources(shape["files"], name, "restart", repo_root),
                )
        elif restart != "unless-stopped":
            violation(
                sid, "missing-restart", name,
                f"restart={restart!r}; every long-running service must declare "
                f"restart: unless-stopped so a host reboot brings the stack back",
                locate_in_sources(shape["files"], name, "restart", repo_root),
            )

        logging_cfg = svc.get("logging") or {}
        options = logging_cfg.get("options") or {}
        if (
            logging_cfg.get("driver") != "json-file"
            or not options.get("max-size")
            or not options.get("max-file")
        ):
            violation(
                sid, "missing-log-cap", name,
                f"logging={logging_cfg!r}; every service needs driver json-file "
                f"with max-size and max-file, or one busy day fills the disk",
                locate_in_sources(shape["files"], name, "logging", repo_root),
            )

        if not one_shot:
            hc = svc.get("healthcheck") or {}
            if not hc or hc.get("disable") is True or not hc.get("test"):
                violation(
                    sid, "missing-healthcheck", name,
                    f"healthcheck={hc!r}; a long-running service with no "
                    f"healthcheck cannot gate a depends_on and cannot be "
                    f"diagnosed by doctor",
                    locate_in_sources(shape["files"], name, "healthcheck", repo_root),
                )


def image_is_pinned(image):
    """A production image names an immutable artefact.

    Accepted: `repo@sha256:<64 hex>` (a digest), or `repo:<tag>` where the tag
    is neither empty nor `latest`. Refused: no image at all, a bare repository
    with no tag (which Docker resolves to `latest`), and `latest` spelled out.
    """
    if not image or not isinstance(image, str):
        return False, "no image"
    if "@sha256:" in image:
        digest = image.split("@sha256:", 1)[1]
        if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest):
            return True, ""
        return False, f"malformed digest {image!r}"
    # Split off the tag, being careful that a registry host may carry a :port.
    last = image.rsplit("/", 1)[-1]
    if ":" not in last:
        return False, f"{image!r} has no tag; Docker resolves that to :latest"
    tag = last.rsplit(":", 1)[1]
    if not tag:
        return False, f"{image!r} has an empty tag"
    if tag == "latest":
        return False, f"{image!r} is tagged latest, which is not an artefact"
    return True, ""


def check_production(shape, model, repo_root):
    """Rules that apply only where an operator's data lives."""
    if shape.get("kind") != "production":
        return
    sid = shape["id"]
    for name, svc in sorted((model.get("services") or {}).items()):
        if svc.get("build"):
            violation(
                sid, "production-build", name,
                f"carries build: in a production shape (one_shot="
                f"{str(name in ONE_SHOT_SERVICES).lower()}); production runs "
                f"`up -d --no-build` from published images and must never need "
                f"a compiler or a source checkout on the host",
                locate_in_sources(shape["files"], name, "build", repo_root),
            )

        ok, why = image_is_pinned(svc.get("image"))
        if not ok:
            violation(
                sid, "unpinned-image", name,
                f"{why}; production images come from the release record "
                f"(VIZRA_*_TAG) or a digest",
                locate_in_sources(shape["files"], name, "image", repo_root),
            )

        if "no-new-privileges:true" not in (svc.get("security_opt") or []):
            violation(
                sid, "no-new-privileges", name,
                "has no security_opt no-new-privileges:true (VZ-OPS-008)",
                locate_in_sources(shape["files"], name, "security_opt", repo_root),
            )

        env = svc.get("environment") or {}

        # VZ-TOPOLOGY-007. The developer override must never reach a production
        # chain, and these two rules are how that is observable rather than
        # merely asserted in a comment. Either one firing means
        # docker-compose.override.yml was loaded into a production shape.
        if name in CORE_SERVICES and env.get("VIZRA_MODE") != "production":
            violation(
                sid, "dev-mode-in-production", name,
                f"renders VIZRA_MODE={env.get('VIZRA_MODE')!r} in a production "
                f"shape; vizra-core's production refusals (dev secrets, short "
                f"secrets, wildcard CORS, plain-http origins, every named "
                f"escape hatch) are all keyed off this value",
                locate_in_sources(shape["files"], name, "environment", repo_root),
            )

        for key in sorted(env):
            if key.startswith(DEV_HATCH_PREFIX):
                violation(
                    sid, "dev-hatch-in-production", name,
                    f"carries the development escape hatch {key} in a production "
                    f"shape; VIZRA_DEV_AUTOLOGIN_USER is refused on PRESENCE, so "
                    f"these must not appear at all - not even set to empty",
                    locate_in_sources(shape["files"], name, "environment", repo_root),
                )


def check_security(shape, model, repo_root):
    """Applies to every shape, dev included: these are never acceptable."""
    sid = shape["id"]
    for name, svc in sorted((model.get("services") or {}).items()):
        for vol in svc.get("volumes") or []:
            source = vol.get("source") if isinstance(vol, dict) else str(vol)
            if source and "docker.sock" in source:
                violation(
                    sid, "docker-socket", name,
                    "bind-mounts the Docker socket; the web/API process never "
                    "gets unrestricted Docker-socket access (VZ-OPS-008)",
                    locate_in_sources(shape["files"], name, "volumes", repo_root),
                )
        if svc.get("privileged"):
            violation(sid, "privileged", name, "runs privileged")
        if svc.get("network_mode") == "host":
            violation(
                sid, "host-network", name,
                "uses network_mode: host, which bypasses every port rule above",
            )


def check_membership(shape, model):
    """A shape must render the services it declares, and none it forbids.

    Absence is as load-bearing as closure. "The external-PostgreSQL shape has no
    postgres service" is the whole point of that overlay, and "the default shape
    HAS caddy" is the whole point of the edge profile — neither is proven by any
    port rule.
    """
    sid = shape["id"]
    present = set((model.get("services") or {}).keys())
    for name in shape.get("requires_services") or []:
        if name not in present:
            violation(
                sid, "missing-service", name,
                f"is declared for this shape but did not render; present: "
                f"{sorted(present)}",
            )
    for name in shape.get("forbids_services") or []:
        if name in present:
            violation(
                sid, "unexpected-service", name,
                f"rendered in a shape that forbids it; present: {sorted(present)}",
            )
    # The inverse of `production-build`. A developer chain that has stopped
    # building from the checkouts is silently running published images — the
    # same class of "it renders, so nobody noticed" failure, pointing the other
    # way.
    for name in shape.get("requires_build") or []:
        svc = (model.get("services") or {}).get(name) or {}
        if not svc.get("build"):
            violation(
                sid, "missing-build", name,
                "is declared to build from its component checkout in this shape "
                "but carries no build:; the developer chain would run a "
                "published image instead of the tree being edited",
            )


# --------------------------------------------------------------------------

def main(argv):
    if len(argv) != 2:
        sys.stderr.write(__doc__.split("Usage:", 1)[1].split("\n\n", 1)[0])
        sys.stderr.write("\n")
        return 2
    models_dir = argv[1]
    repo_root = os.getcwd()

    manifest_path = os.path.join(models_dir, "shapes.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (OSError, ValueError) as err:
        sys.stderr.write(
            f"UNEVALUABLE: cannot read the shape manifest {manifest_path}: {err}\n"
            "  Nothing was checked. Run scripts/compose-render.py first.\n"
        )
        return 2

    shapes = manifest.get("shapes") or []
    if not shapes:
        sys.stderr.write(
            f"UNEVALUABLE: {manifest_path} declares no shapes. A checker with "
            f"nothing to check passes trivially; that is not a pass.\n"
        )
        return 2

    checked = 0
    for shape in shapes:
        sid = shape["id"]
        model_path = os.path.join(models_dir, f"{sid}.json")
        try:
            with open(model_path, "r", encoding="utf-8") as fh:
                model = json.load(fh)
        except (OSError, ValueError) as err:
            sys.stderr.write(
                f"UNEVALUABLE: shape {sid} declared but its rendered model "
                f"{model_path} is missing or unparseable: {err}\n"
                "  A declared shape that produced no model was NOT checked.\n"
            )
            return 2
        if not isinstance(model.get("services"), dict) or not model["services"]:
            sys.stderr.write(
                f"UNEVALUABLE: shape {sid} rendered no services at all. An "
                f"empty model satisfies every rule below and proves nothing.\n"
            )
            return 2

        check_ports(shape, model, repo_root)
        check_edge(shape, model, repo_root)
        check_lifecycle(shape, model, repo_root)
        check_production(shape, model, repo_root)
        check_security(shape, model, repo_root)
        check_membership(shape, model)
        checked += 1

    if violations:
        for line in violations:
            sys.stderr.write(line + "\n")
        sys.stderr.write(
            f"\n{len(violations)} violation(s) across {checked} shape(s).\n"
        )
        return 1

    print(
        f"compose topology: {checked} shape(s) asserted from their rendered "
        f"models; {len(RULES)} rules, 0 violations"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
