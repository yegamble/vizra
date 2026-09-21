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
    "missing-mem-limit",
    "probe-gates-readiness",
    "stale-known-false-probe",
    "profile-not-enumerated",
    "known-false-undisclosed",
    "postgres-shm-floor",
    "gated-probe-unrecognised",
})

# Docker's default /dev/shm. PostgreSQL allocates dynamic shared memory there
# (dynamic_shared_memory_type=posix), so parallel plans fail against this
# default months after install while `shared_buffers` — anonymous mmap since
# 9.3 — keeps the cluster starting fine.
DOCKER_DEFAULT_SHM_BYTES = 64 * 1024 * 1024

# vizra-core refuses every one of these by name when VIZRA_MODE=production, and
# VIZRA_DEV_AUTOLOGIN_USER is refused on PRESENCE with a non-empty value. They
# reach a container only through docker-compose.override.yml, which the
# production `-f` chain never loads — so finding one in a production model means
# the override leaked into the chain.
DEV_HATCH_PREFIX = "VIZRA_DEV_"

# The services that run the vizra-core binary and therefore read VIZRA_MODE.
CORE_SERVICES = frozenset({"api", "worker", "migrate"})


# The FOUR states a healthcheck can be in. Written once, as a single function,
# because the previous shape — one conditional in check_lifecycle and another in
# check_probes — let a spelling fall between them. `test: ["NONE"]` is Docker's
# documented way to DISABLE a healthcheck (it is what `disable: true` compiles
# to), and it passed the "must have a healthcheck" rule because a one-element
# list is not falsy. The neighbouring spelling `disable: true` was caught, so the
# rule knew about the concept and missed one of its two spellings.
PROBE_ABSENT = "absent"          # no healthcheck at all
PROBE_DISABLED = "disabled"      # disable: true, or test NONE in any spelling
PROBE_KNOWN_FALSE = "known-false"  # declared in compose-shapes.json: cannot go red
PROBE_REAL = "real"              # actually probes the service


def probe_state(svc, name, known_false):
    hc = svc.get("healthcheck") or {}
    if not hc:
        return PROBE_ABSENT, hc
    if hc.get("disable") is True:
        return PROBE_DISABLED, hc
    test = hc.get("test")
    if isinstance(test, str):
        # Compose accepts the bare string form; normalise before comparing so
        # `test: NONE` and `test: ["NONE"]` cannot diverge.
        test = [test]
    if not test:
        return PROBE_ABSENT, hc
    if test[:1] == ["NONE"]:
        return PROBE_DISABLED, hc
    entry = known_false.get(name)
    if entry and list(test) == list(entry["test"]):
        return PROBE_KNOWN_FALSE, hc
    return PROBE_REAL, hc


violations = []

# Services whose healthcheck matched a known-false declaration in some rendered
# shape. Module level because two rules populate and read it, and because the
# "declared but matching nothing" check has to run once, after every shape.
KNOWN_FALSE_SEEN = set()


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


def profiles_declared_in_sources(files, repo_root):
    """Every `profiles:` name that appears in any compose file in the chain.

    Uses the same tolerant loader as the diagnostic locator. This is NOT an
    assertion on a rendered model, and it cannot be: the hole it closes is
    precisely that an unenumerated profile is NEVER rendered, so no amount of
    reading rendered models can see it.
    """
    if yaml is None:
        return None
    found = set()
    for rel in sorted(set(files)):
        path = os.path.join(repo_root, rel)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                class Tolerant(yaml.SafeLoader):
                    pass

                Tolerant.add_multi_constructor("", lambda l, sfx, n: None)
                doc = yaml.load(fh, Loader=Tolerant)
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(doc, dict):
            continue
        for svc in (doc.get("services") or {}).values():
            if not isinstance(svc, dict):
                continue
            profs = svc.get("profiles")
            # `profiles: !override [...]` loads as None under the tolerant
            # loader (the tag constructor discards the value), which is exactly
            # right here: an overlay that PARKS a service on a disabled profile
            # must not add that name to the set of profiles an operator can
            # select. Only plain lists count.
            if isinstance(profs, list):
                found.update(str(x) for x in profs)
    return found


def check_profile_coverage(all_files, enumerated, repo_root):
    """A service on a profile no shape enumerates is never rendered, so never
    asserted.

    Every rule in this file reads a rendered model, and a shape renders only the
    profiles it names. The union across every shape is therefore the exact
    boundary of this checker's coverage — complete inside it, EMPTY outside it.
    A later slice adding a `backup`, `debug` or `admin` profile with an open
    datastore port would leave the lane green at "0 violations" while an
    operator who enables that profile gets 0.0.0.0:5432.

    So the set is closed rather than enumerated: every profile name that appears
    in the compose files must be covered by at least one shape. Adding a profile
    AND a shape that enumerates it is green — the rule pushes authors toward
    declaring the shape, not away from adding profiles.
    """
    declared = profiles_declared_in_sources(all_files, repo_root)
    if declared is None:
        violation(
            "(manifest)", "profile-not-enumerated", "(all)",
            "PyYAML is unavailable, so the profiles declared in the compose "
            "files could not be read and this rule checked NOTHING. It fails "
            "closed: an unchecked closing rule is the one that lets an "
            "unrendered profile through",
        )
        return
    # `external-disabled` is the parking profile the external overlays use to
    # delete a bundled datastore. Nothing may ever select it — that is its
    # entire purpose — so a shape enumerating it would be a bug, not coverage.
    parking = {"external-disabled"}
    for name in sorted(declared - enumerated - parking):
        violation(
            "(manifest)", "profile-not-enumerated", "(profile)",
            f"profile {name!r} appears in a compose file but no shape in "
            f"scripts/compose-shapes.json enumerates it, so no shape renders it "
            f"and NO RULE HERE HAS EVER SEEN IT. Add a shape that selects "
            f"{name!r} (enumerated today: {sorted(enumerated)})",
        )


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
    # Keyed on "<published>/<protocol>", not on the port number alone. The
    # manifest reads as a protocol-aware allowlist and used to not be one: with
    # a number-only key, api publishing 8080/udp was allowed by an entry that
    # meant "this service may answer on TCP 8080". Bounded in impact — api and
    # frontend are loopback-only and any non-loopback bind is still caught by
    # public-bind — but an allowlist should mean what it reads as.
    #
    # A bare integer in the manifest still means tcp, so the common case stays
    # short; ipfs, the one service with a legitimate UDP port, names both.
    allow = {}
    for item in shape.get("published_allow") or []:
        entries = {}
        for p in item["ports"]:
            if isinstance(p, dict):
                entries[f"{p['port']}/{p.get('protocol', 'tcp')}"] = bool(
                    item.get("public", False)
                )
            else:
                entries[f"{p}/tcp"] = bool(item.get("public", False))
        allow[item["service"]] = entries

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
        for host_ip, published, target, proto in entries:
            key = f"{published}/{proto}"
            if key not in permitted:
                violation(
                    sid, "port-not-allowed", name,
                    f"publishes {host_ip}:{published}->{target}/{proto}, which "
                    f"this shape does not allow (allowed: "
                    f"{sorted(permitted) or 'nothing'})",
                    where,
                )
                continue
            # Allowed to publish this port — but facing the network is a second,
            # separate permission that must be written out per port.
            if not permitted[key] and host_ip not in LOOPBACK_HOST_IPS:
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


def check_lifecycle(shape, model, repo_root, known_false):
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
            state, hc = probe_state(svc, name, known_false)
            if state in (PROBE_ABSENT, PROBE_DISABLED):
                violation(
                    sid, "missing-healthcheck", name,
                    f"healthcheck is {state} ({hc!r}); a long-running service "
                    f"without one cannot gate a depends_on and cannot be "
                    f"diagnosed by doctor. NOTE: test ['NONE'] and the string "
                    f"'NONE' are Docker's spellings of disabled, not of a probe",
                    locate_in_sources(shape["files"], name, "healthcheck", repo_root),
                )
            elif state == PROBE_KNOWN_FALSE:
                # PRESENT, but a placeholder. This rule's whole reason for
                # existing is "cannot gate a depends_on" — so a probe that
                # cannot go red satisfies its letter and defeats its purpose.
                # It is allowed through ONLY because it is declared, and it is
                # NAMED on every run by the standing report in main().
                KNOWN_FALSE_SEEN.add(name)


def image_is_pinned(image, release_image):
    """A production image names an immutable artefact.

    TWO RULES, because there are two kinds of image and ADR-001 asks different
    things of them:

    * A **Vizra release image** (`release_image=True`) comes from the release
      record — `ghcr.io/…/vizra-core:${VIZRA_CORE_TAG}` — and a release tag is
      legitimately what `releases/<tag>.json` names. A non-empty, non-`latest`
      tag is enough. Recording the resolved digest at deploy time is
      VZ-UPGRADE-002's job, not this rule's.

    * **Anything else** is third-party, and ADR-001 says PostgreSQL 18 is
      "managed and digest-pinned" and Valkey 9.1.x "digest-pinned". So a digest
      is REQUIRED. The tree honoured that by hand; nothing enforced it, and
      `postgres:18` would have passed silently — a moving target that makes two
      operators on the same release record run different PostgreSQL builds and
      stops a rollback rolling the datastore back.

    The default for an unrecognised service is the strict branch, so a service
    added later must either be declared a release image or carry a digest.
    """
    if not image or not isinstance(image, str):
        return False, "no image"
    if "@sha256:" in image:
        digest = image.split("@sha256:", 1)[1]
        if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest):
            return True, ""
        return False, f"malformed digest {image!r}"
    if not release_image:
        return False, (
            f"{image!r} is a third-party image with no @sha256 digest. ADR-001 "
            f"pins these by digest; a bare tag is a moving target, so two "
            f"operators deploying the same release record get different builds "
            f"and a rollback does not roll the datastore image back"
        )
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


def check_production(shape, model, repo_root, release_services):
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

        ok, why = image_is_pinned(svc.get("image"), name in release_services)
        if not ok:
            violation(
                sid, "unpinned-image", name,
                f"{why}; production images come from the release record "
                f"(VIZRA_*_TAG) or a digest",
                locate_in_sources(shape["files"], name, "image", repo_root),
            )

        # F4. Same shape as missing-log-cap, and for a related reason: a
        # service with no cgroup limit cannot be contained, so the kernel picks
        # the victim by badness score - which on a Docker host is routinely
        # PostgreSQL, the largest resident process. A limit that OOM-kills the
        # worker is recoverable; one that OOM-kills PostgreSQL is crash
        # recovery. One-shots are exempt: they exit.
        if name not in ONE_SHOT_SERVICES and not svc.get("mem_limit"):
            violation(
                sid, "missing-mem-limit", name,
                "declares no mem_limit in a production shape; without one a "
                "burst has no containment and the OOM killer chooses by badness "
                "score, not by what is safe to lose",
                locate_in_sources(shape["files"], name, "mem_limit", repo_root),
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


def check_probes(shape, model, known_false, seen_known_false, repo_root,
                 gated_probes):
    """F3. A gate on a probe that cannot go red is worse than no gate.

    Two things happen here, and the second is the point:

    1. Any `depends_on: {condition: service_healthy}` edge pointing at a service
       whose probe is declared known-false FAILS. Docker would report that
       service healthy while it is wedged, the dependant would start anyway, and
       `vizra deploy`'s probe step and VZ-ISSUE-004's boot lane would both read
       the same green.

    SCOPE, stated because the rule is easy to over-read: it refuses a gate onto
    a probe someone has DECLARED false. It CANNOT tell a real probe from a fake
    one nobody declared — swapping postgres's `pg_isready` for `["CMD","true"]`
    would leave three `service_healthy` edges gating on nothing and this rule
    silent. `gated-probe-unrecognised`, below, is the converse that covers it.

    2. Every known-false probe present in the model is NAMED on every run, and
       `check_lifecycle`'s "must have a healthcheck" rule is deliberately NOT
       allowed to be quietly satisfied by one. That rule exists to make a
       `depends_on` gateable; a placeholder satisfies its letter and defeats its
       purpose, so the placeholder has to be announced every single time rather
       than declared once and forgotten.
    """
    sid = shape["id"]
    services = model.get("services") or {}

    for name, svc in sorted(services.items()):
        entry = known_false.get(name)
        if not entry:
            continue
        if list(svc.get("healthcheck", {}).get("test") or []) != list(entry["test"]):
            # The declaration no longer matches what the service actually runs.
            # Either the probe was fixed (delete the entry) or it changed and
            # nobody revisited the declaration. Both need a human.
            continue
        seen_known_false.add(name)

    for name, svc in sorted(services.items()):
        for dep, spec in sorted((svc.get("depends_on") or {}).items()):
            if not isinstance(spec, dict):
                continue
            if spec.get("condition") != "service_healthy":
                continue
            # THE CONVERSE. probe-gates-readiness below catches a gate onto a
            # probe someone DECLARED false. It cannot tell a real probe from a
            # fake one nobody declared — so a gated service must additionally
            # be listed in `gated_probes` and still invoke the command that
            # makes its probe mean something.
            if dep in services and dep not in known_false:
                rule = gated_probes.get(dep)
                dep_test = (services[dep].get("healthcheck") or {}).get("test") or []
                if isinstance(dep_test, str):
                    dep_test = [dep_test]
                joined = " ".join(str(x) for x in dep_test)
                if rule is None:
                    violation(
                        sid, "gated-probe-unrecognised", dep,
                        f"is gated on by {name} with condition service_healthy "
                        f"but is not listed in `gated_probes` in "
                        f"scripts/compose-shapes.json, so nothing asserts its "
                        f"probe means anything. Its rendered test is "
                        f"{dep_test!r}",
                        locate_in_sources(shape["files"], dep, "healthcheck", repo_root),
                    )
                elif rule["must_invoke"] not in joined:
                    violation(
                        sid, "gated-probe-unrecognised", dep,
                        f"is gated on by {name} with condition service_healthy, "
                        f"but its probe {dep_test!r} does not invoke "
                        f"{rule['must_invoke']!r} - {rule['why']}. A gate onto a "
                        f"probe that cannot fail is a gate onto nothing",
                        locate_in_sources(shape["files"], dep, "healthcheck", repo_root),
                    )
            if dep in known_false and dep in services:
                violation(
                    sid, "probe-gates-readiness", name,
                    f"gates on {dep} with condition service_healthy, but {dep}'s "
                    f"probe is declared known-false in "
                    f"scripts/compose-shapes.json ({known_false[dep]['why_false']}) "
                    f"- so this edge reports satisfied while {dep} is broken",
                    locate_in_sources(shape["files"], name, "depends_on", repo_root),
                )


def check_shm(shape, model, repo_root):
    """PostgreSQL needs more than Docker's 64 MiB /dev/shm.

    Cheap enough to be a rule rather than a comment: Compose renders `shm_size`
    as a byte count, so this is a comparison. The failure it guards against is
    the most Docker-specific PostgreSQL failure there is, and its signature is
    the worst possible one — plan-dependent, so it comes and goes with the
    statistics, and reports "No space left on device" on a host with gigabytes
    of disk free.
    """
    svc = (model.get("services") or {}).get("postgres")
    if svc is None:
        return
    raw = svc.get("shm_size")
    try:
        size = int(raw)
    except (TypeError, ValueError):
        size = None
    if size is None or size <= DOCKER_DEFAULT_SHM_BYTES:
        violation(
            shape["id"], "postgres-shm-floor", "postgres",
            f"shm_size={raw!r}, which is Docker's 64 MiB default or less. "
            f"PostgreSQL allocates dynamic shared memory in /dev/shm, so "
            f"parallel scans and hash joins fail with `could not resize shared "
            f"memory segment ... No space left on device` once a table grows "
            f"past the parallel threshold - long after install, on a host with "
            f"plenty of disk",
            locate_in_sources(shape["files"], "postgres", "shm_size", repo_root),
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

    known_false = {
        e["service"]: e for e in (manifest.get("known_false_probes") or [])
    }
    gated_probes = manifest.get("gated_probes") or {}
    release_services = set(manifest.get("release_image_services") or [])
    if not release_services:
        sys.stderr.write(
            "UNEVALUABLE: scripts/compose-shapes.json declares no "
            "`release_image_services`. Every image would then be required to "
            "carry a digest, including the Vizra images that legitimately come "
            "from a release tag - a rule nobody could satisfy is not a rule.\n"
        )
        return 2
    seen_known_false = KNOWN_FALSE_SEEN

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
        check_lifecycle(shape, model, repo_root, known_false)
        check_production(shape, model, repo_root, release_services)
        check_security(shape, model, repo_root)
        check_membership(shape, model)
        check_probes(shape, model, known_false, seen_known_false, repo_root,
                     gated_probes)
        check_shm(shape, model, repo_root)
        checked += 1

    # A declaration that matches nothing is a declaration nobody can act on, and
    # it is exactly how a list like this rots into permanent cover. If a probe
    # was fixed, the entry must go in the same commit.
    # F3's human half. The known-false list is printed on every run for CI; this
    # is the check that the OPERATOR-facing disclosure exists while it does.
    # It fails in both directions by construction: emptying the list without
    # deleting the paragraphs leaves a file claiming a limit that no longer
    # applies, and deleting a paragraph while the list stands leaves the person
    # running `docker compose ps` at 3am with no warning at all.
    disclosure = manifest.get("known_false_disclosure") or {}
    if known_false and disclosure:
        marker = disclosure.get("marker", "")
        for rel in disclosure.get("files", []):
            try:
                with open(os.path.join(repo_root, rel), "r", encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                text = ""
            if marker not in text:
                violation(
                    "(manifest)", "known-false-undisclosed", rel,
                    f"must carry the disclosure {marker!r} while "
                    f"known_false_probes is non-empty "
                    f"({sorted(known_false)}), and does not. `docker compose ps` "
                    f"reports those services healthy whatever their state, and "
                    f"the operator reading that column has no other warning",
                )

    # V3's closing rule: run once, over the union of every file any shape loads.
    all_files = sorted({f for sh in shapes for f in sh["files"]})
    enumerated = {p for sh in shapes for p in (sh.get("profiles") or [])}
    check_profile_coverage(all_files, enumerated, repo_root)

    for name in sorted(set(known_false) - seen_known_false):
        violation(
            "(manifest)", "stale-known-false-probe", name,
            f"is declared known-false in scripts/compose-shapes.json but no "
            f"rendered shape has a {name} service running that exact probe. "
            f"Either the probe was fixed - delete the entry - or it changed and "
            f"the declaration was not revisited",
        )

    # PRINTED ON EVERY RUN, pass or fail, before the verdict. A probe that
    # cannot go red is a standing admission, not a one-time note in a commit
    # message nobody re-reads. VZ-ISSUE-004's boot lane and `vizra deploy` are
    # both written against `--wait` / `ps --status healthy`; this list is what
    # stops them inheriting a false green silently, and it must be EMPTY before
    # that lane lands.
    if known_false:
        print(
            f"\nKNOWN-FALSE PROBES: {len(known_false)} service(s) carry a "
            f"healthcheck that CANNOT GO RED while the service is broken."
        )
        for name in sorted(known_false):
            e = known_false[name]
            state = "present in the rendered model" if name in seen_known_false \
                else "DECLARED BUT NOT MATCHED - see stale-known-false-probe"
            print(f"  - {name}: {' '.join(e['test'])}  [{state}]")
            print(f"      why it is false: {e['why_false']}")
            print(f"      emptied by:      {e['emptied_by']}")
        print(
            "  No depends_on service_healthy edge may point at one (rule "
            "probe-gates-readiness), and this list must be empty before "
            "VZ-ISSUE-004's boot lane lands."
        )
        disc = manifest.get("known_false_disclosure") or {}
        if disc:
            print(
                "  The operator-facing half of this admission — `docker compose "
                "ps` reports these\n  services healthy whatever their state — is "
                "carried by:"
            )
            for rel in disc.get("files", []):
                print(f"    {rel}")
            print(
                "  Those files and this list are deleted together (rule "
                "known-false-undisclosed)."
            )
        print(
            "  SCOPE: probe-gates-readiness only refuses a gate onto a probe\n"
            "  DECLARED false above. It cannot tell a real probe from a fake one\n"
            "  nobody declared; gated-probe-unrecognised is what covers that, by\n"
            "  requiring every service_healthy target to invoke a declared command.\n"
        )

    if violations:
        for line in violations:
            sys.stderr.write(line + "\n")
        sys.stderr.write(
            f"\n{len(violations)} violation(s) across {checked} shape(s).\n"
        )
        return 1

    print(
        f"compose topology: {checked} shape(s) asserted from their rendered "
        f"models; {len(RULES)} rules, 0 violations; "
        f"{len(known_false)} known-false probe(s) named above"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
