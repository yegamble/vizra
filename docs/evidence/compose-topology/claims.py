#!/usr/bin/env python3
"""Regenerate docs/evidence/compose-topology/CLAIMS.md.

WHY THIS IS A GENERATOR AND NOT A HAND-WRITTEN TABLE. The audit it produces has
two halves that rot in different ways. The file:line of every audited sentence
moves whenever a document is edited, and a stale line number in an evidence file
is worse than none — a reviewer follows it, lands somewhere else, and stops
trusting the rest. And the rule-id -> demonstration mapping is exactly the hand
count that has been wrong in three successive PR bodies. So both are computed:
the anchors are resolved against the live files (and the script REFUSES to write
anything if one is missing or ambiguous), and the mapping is read out of
`demo.sh` and the checkers' own `RULES` sets.

Run from the repository root:

    python3 docs/evidence/compose-topology/claims.py          # write CLAIMS.md
    python3 docs/evidence/compose-topology/claims.py --check  # verify, write nothing

Exit codes: 0 written/verified, 1 CLAIMS.md is stale (--check), 2 an anchor no
longer resolves — the audit is UNEVALUABLE and nothing is written.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "docs", "evidence", "compose-topology", "CLAIMS.md")
DEMO = os.path.join("docs", "evidence", "compose-topology", "demo.sh")

CHECKERS = (
    ("scripts/check-compose-topology.py", "topology"),
    ("scripts/check-config-coverage.py", "config coverage"),
    ("scripts/check-template-claims.py", "template claims"),
)

# --------------------------------------------------------------------------
# The audit. One row per sentence on an operator-facing or CI-facing surface
# that uses a guarantee word: enforce, refuse, fail, cannot, never, always,
# every, both directions, invoke, guarantee, prove, by construction.
#
# `anchor` must appear EXACTLY ONCE in the file; the generator refuses to run
# otherwise, so a reworded sentence cannot silently keep an old line number.
#
# WHAT IS DELIBERATELY NOT AUDITED HERE, so the exclusion is a decision rather
# than an omission:
#
#   * The text of a violation MESSAGE. It is printed only after its rule has
#     already fired, so it describes a failure that happened rather than
#     guaranteeing one that will.
#   * Narrative about a defect that was fixed ("the renderer used to serialise
#     the original"). That is history, and its evidence is the case that keeps
#     it fixed, which is audited on its own row.
#   * A claim about another repository's behaviour — what vizra-core refuses,
#     what Docker does on `unhealthy`, what PostgreSQL does with /dev/shm.
#     Those are audited as NOT OURS with the artefact they rest on, because
#     nothing in this repository can demonstrate them and pretending otherwise
#     is the exact failure this file exists to catch.
# --------------------------------------------------------------------------

D = "demonstrated"      # a demo.sh case turns this red
C = "code-only"         # asserted by a rule, but no case has seen it fire
N = "not ours"          # a claim about another component or another tool
X = "no mechanism"      # true of the artefact as written; nothing enforces it

CLAIMS = [
    # ---------------- docs/META_REPO.md §2a ----------------
    ("docs/META_REPO.md",
     "is rendered on every run and asserted",
     "Every declared shape is rendered on every run and asserted from the "
     "rendered JSON, never from the YAML sources.",
     D, "0 (baseline) and every case below",
     "That the 13 declared shapes are the only reachable configurations. The "
     "closure on that is `profile-not-enumerated` (case 19), and its own limit "
     "is the next row."),

    ("docs/META_REPO.md",
     "**Nothing in this repository starts a container.**",
     "Nothing in this repository starts a container; every assertion is about "
     "a rendered model.",
     X, "n/a - a negative",
     "Not demonstrable by a case. It is checkable by inspection: no "
     "`docker compose up`, `run`, `start` or `pull` appears in any lane script "
     "or workflow step. A reader should verify that rather than take this "
     "sentence."),

    ("docs/META_REPO.md",
     "so whichever slice adds them cannot add them open",
     "`minio`, `clamav`, `otel-collector` and `jaeger` are in the "
     "never-published list, so a later slice cannot add them with a port.",
     D, "1, 2, 3 (the rule, on services that do render)",
     "Only in a shape that RENDERS the service. A service added on a profile "
     "no shape enumerates is caught by `profile-not-enumerated`, and a compose "
     "file no shape lists at all is scanned by neither."),

    ("docs/META_REPO.md",
     "**never both** — the retired name is refused on presence",
     "Compose never delivers both the retired and the current spelling of a "
     "renamed key.",
     D, "13",
     "That vizra-core actually refuses the retired name. This repository "
     "asserts only what the model delivers; the refusal is core's, recorded in "
     "`env/registry/core.json` `retired_keys` at a named component commit."),

    ("docs/META_REPO.md",
     "- **refuses** any `depends_on: {condition: service_healthy}` edge",
     "Any `service_healthy` edge onto a probe declared known-false fails.",
     D, "15",
     "Nothing about a probe nobody declared false - that is the next row."),

    ("docs/META_REPO.md",
     "and cannot tell a real probe from a fake one nobody declared. The converse is",
     "`probe-gates-readiness` only refuses a gate onto a DECLARED false probe "
     "and cannot recognise an undeclared fake.",
     D, "26 (the converse rule is what catches it)",
     "Nothing - this row is a statement of a LIMIT, and case 26 is what shows "
     "the limit is covered by a second rule rather than left open."),

    ("docs/META_REPO.md",
     "its **rendered** probe must run the declared command *as",
     "Every `service_healthy` target's rendered probe must run the declared "
     "command as its own command; `[\"CMD\",\"true\"]`, `pg_isready || true`, "
     "`true # pg_isready`, `sh -c 'exit 0; pg_isready'` and `echo pg_isready` "
     "are all red.",
     D, "26, 26a, 26b, 26c, 26d, 26e",
     "That the command can exit NON-ZERO: "
     "`[\"CMD-SHELL\",\"pg_isready --version\"]` passes and always succeeds "
     "(measured, recorded in local-run.txt). And that a binary with the right "
     "name is the real one rather than a wrapper on PATH. Both need a running "
     "container."),

    ("docs/META_REPO.md",
     "- **names every entry on every run**, pass or fail",
     "Every known-false probe is named on every run, pass or fail.",
     D, "0 (the banner is in every transcript)",
     "It is a printout, not a gate. Nothing fails because the list is "
     "non-empty; that is the point of `probe-gates-readiness` instead."),

    ("docs/META_REPO.md",
     "- **refuses a declaration that matches nothing** (rule",
     "A known-false declaration matching no rendered service fails, so the "
     "list cannot rot into permanent cover.",
     D, "15b", "Nothing further."),

    ("docs/META_REPO.md",
     "deleted in the same PR**: `known-false-undisclosed` fails when the list is",
     "The known-false list and the operator-facing paragraphs are deleted in "
     "the same PR, enforced in BOTH directions.",
     D, "23 (list stands, paragraph gone) and 27 (list empty, paragraph stands)",
     "It matches a MARKER STRING, not the content around it. Stripping the "
     "`curl` commands while leaving the heading passes - measured by the "
     "verifier at 9c4b5d3 and still true."),

    ("docs/META_REPO.md",
     "`profile-not-enumerated` closes the set: every `profiles:` name in the compose",
     "Every `profiles:` name in the compose files is covered by at least one "
     "shape, so no service escapes assertion on an unrendered profile.",
     D, "19",
     "Only across the compose files some shape's `files` list names. A new "
     "`docker-compose.*.yml` that no shape loads is not read by this rule at "
     "all. It also needs PyYAML, and fails closed when it is absent."),

    ("docs/META_REPO.md",
     "`postgres:18` cannot quietly replace a digest",
     "A third-party image must carry an `@sha256:` digest, so a bare tag "
     "cannot replace one.",
     D, "8a, 8b, 8c",
     "That the digest names the image anyone actually runs - `unpinned-image` "
     "reads the model, and nothing here pulls or resolves a manifest."),

    ("docs/META_REPO.md",
     "- **A disabled healthcheck is disabled in every spelling.**",
     "`disable: true`, `test: [\"NONE\"]` and `test: NONE` are one state.",
     D, "6c (absent), 6d (`disable: true`), 6e (`[\"NONE\"]`)",
     "The bare STRING spelling `test: NONE` is handled in `probe_state()` but "
     "has no case of its own; Compose normalises it before the checker sees "
     "it, which is why. Asserted by code, not by demonstration."),

    ("docs/META_REPO.md",
     "key from the first makes the renderer fail rather than write a file that is",
     "Deleting a key from `redact_keys` makes the renderer fail rather than "
     "write a model less redacted than its own stamp claims.",
     D, "18b (exit 1, zero files written)",
     "Only for a key in `secret_keys` or flagged by a registry. A credential "
     "in neither is written raw - see the S-6 row below."),

    # ---------------- docs/quality/COMMANDS.md §4 ----------------
    ("docs/quality/COMMANDS.md",
     "and is **not exercised by any demonstration**",
     "The Compose floor (>= 2.24.4) is refused, failing closed on an "
     "unparseable version.",
     C, "none - softened this round to say so",
     "No case has seen it fire; the harness runs on whichever Compose the host "
     "has. The sentence was rewritten to state that rather than read as a "
     "demonstrated control."),

    ("docs/quality/COMMANDS.md",
     "which cases 10a and 10b do demonstrate, value check included",
     "An invalid or missing external DSN fails with a message that names the "
     "variable and never echoes the value.",
     D, "10a (invalid, and asserts the value is ABSENT from the message), 10b (empty)",
     "Scheme and host shape only. A syntactically valid DSN pointing at the "
     "wrong database renders and passes."),

    ("docs/quality/COMMANDS.md",
     "**A key that is neither is written raw into the uploaded",
     "Redaction covers a registry-flagged `\"secret\": true` key plus the "
     "manifest's explicit composite list - and nothing else.",
     D, "18a, 25, 25b (the positive); the NEGATIVE is the verifier's "
        "VIZRA_S3_ACCESS_ID measurement, 47 occurrences with every lane green",
     "An unflagged credential whose name matches none of `_PASSWORD`, "
     "`_SECRET`, `_TOKEN`, `_KEY` is NOT protected and no lane goes red. The "
     "suffix net was deliberately not widened. The flag itself is compared "
     "against the component only by `--drift`, which cannot run in CI."),

    # ---------------- docs/quality/COMMANDS.md §5 ----------------
    ("docs/quality/COMMANDS.md",
     "as JSON — never from the YAML sources, because what is reachable",
     "Every topology rule reads the rendered model, never the YAML.",
     D, "2 (a port added in an OVERLAY, invisible to a grep of the base file)",
     "One exception, stated in the checker: `profiles_declared_in_sources()` "
     "parses YAML, because an unenumerated profile is never rendered and no "
     "rendered model can see it."),

    ("docs/quality/COMMANDS.md",
     "| `never-published` | postgres, the cache, search,",
     "postgres, the cache, search, the one-shots, worker and every optional "
     "datastore publish nothing in any shape.",
     D, "1, 2, 3",
     "\"Any shape\" means any of the 13 declared shapes. See the "
     "`profile-not-enumerated` row for what closes that set and what it misses."),

    ("docs/quality/COMMANDS.md",
     "**What it still cannot show.** That the command can exit **non-zero**",
     "`gated-probe-unrecognised` cannot show that a probe can go red, or that "
     "a correctly named binary is the real one.",
     X, "n/a - a statement of limits",
     "Nothing. This row exists so the limit is on the record beside the rule "
     "that has it."),

    ("docs/quality/COMMANDS.md",
     "**What this does NOT prove.** It proves what the *model* declares.",
     "The topology check proves what the model declares and nothing about a "
     "running host.",
     X, "n/a - a statement of limits", "Nothing."),

    # ---------------- docs/quality/COMMANDS.md §6 ----------------
    ("docs/quality/COMMANDS.md",
     "on api and worker carrying different key sets",
     "Coverage fails on a key a component reads that nothing delivers, a "
     "template key nothing consumes, and api/worker key-set asymmetry.",
     D, "9a and 9b (the first two). `api-worker-asymmetry`, "
        "`service-key-unknown`, `variable-untemplated` and "
        "`hatch-in-production-template` have NO case",
     "Four of the eleven coverage rule ids have never been seen to fire. See "
     "the undemonstrated-rules table below."),

    ("docs/quality/COMMANDS.md",
     "`vizra-search` and `vizra-user` carry **no** such marker, so their flags are",
     "`--drift` compares the `secret` flag against the component source for "
     "vizra-core's 22 keys, and reports vizra-search and vizra-user UNCHECKED "
     "on every run.",
     D, "drift-transcript.txt, red and green "
        "(`\"secret\": true` deleted from VIZRA_SESSION_SECRET)",
     "It cannot run in CI - there is no token for a private sibling - so this "
     "is a LOCAL control. And it compares only keys the parsed source file "
     "declares; a key declared elsewhere in the component is counted and "
     "printed as NOT compared rather than assumed to match."),

    ("docs/quality/COMMANDS.md",
     "`--drift` — **including the secret-flag comparison above** — **cannot run in CI",
     "A green `validate` proves the topology is consistent with the snapshots, "
     "not that the snapshots are current.",
     D, "the BLOCKED path, exit 2, in drift-transcript.txt",
     "Nothing. BLOCKED is recorded as BLOCKED and never as a pass."),

    # ---------------- docs/quality/COMMANDS.md §7 ----------------
    ("docs/quality/COMMANDS.md",
     "`unknown-script`. The first version of this pass listed six names",
     "Any `*.sh` token, path-prefixed or not, backticked or not, must exist in "
     "the tree or be declared future with its marker in the window.",
     D, "22 (bare), 28a (`./`), 28b (`scripts/`), 28c (backticked path), "
        "28d (`unknown-script`, now reachable), 28e (path form WITH marker "
        "stays green)",
     "Two operator-facing surfaces only: `env/*.env.example` and "
     "`docker-compose*.yml` comments. A claim in `README.md`, "
     "`docs/META_REPO.md` or an issue file is NOT scanned. `unknown-command` "
     "has no demonstration."),

    ("docs/quality/COMMANDS.md",
     "so a promise carries its own qualifier rather than borrowing a neighbour's",
     "A declared future command named anywhere must carry its marker within 2 "
     "lines.",
     D, "14 (the `vizra setup --rotate` line that actually shipped)",
     "Prose mentions without backticks are not scanned for pass A; pass B "
     "scans them, which is why the two passes exist."),

    # ---------------- docs/quality/COMMANDS.md §8 ----------------
    ("docs/quality/COMMANDS.md",
     "**refuses to score a case whose",
     "The harness refuses to score a case whose mutation did not apply, and "
     "fails if the tree is not byte-identical afterwards.",
     D, "every case prints a sha256 pair; the tree check is the last line of "
        "every transcript",
     "It compares `git status --porcelain`, so a change to a GITIGNORED path "
     "would not be seen. The component checkouts are gitignored and are "
     "removed before an evidence run for exactly that reason."),

    ("docs/quality/COMMANDS.md",
     "Sixteen of the 42 declared rule ids across the three checkers",
     "Sixteen of the 42 declared rule ids have no red demonstration.",
     D, "computed by this generator from `demo.sh` and each checker's `RULES`",
     "Nothing - this row is the admission itself. The table below names them."),

    # ---------------- README.md, operator section ----------------
    ("README.md",
     "and with `known-false-stale-disclosure` when the list is empty",
     "The disclosure section and the known-false list are deleted together, "
     "enforced in both directions.",
     D, "23 and 27", "Marker matching only - see the META_REPO row."),

    ("README.md",
     "NO -f: /readyz answers 200 \"degraded\"",
     "The documented readiness command does not read as OK on a degraded "
     "instance.",
     X, "n/a - documentation; testable once VZ-ISSUE-004's boot lane exists",
     "Nothing mechanises this. It became true this round by dropping `-f` "
     "from the `/readyz` line, on the infrastructure seat's NEW-3(b)."),

    # ---------------- env/production.env.example ----------------
    ("env/production.env.example",
     "#   `./scripts/check-config-coverage.py` fails on exactly that",
     "Coverage fails in both directions: a key nothing delivers, and a "
     "template key nothing consumes.",
     D, "9a and 9b", "See the §6 row for the four coverage rules with no case."),

    ("env/production.env.example",
     "# `${KEY:?message}`, which refuses to render on an unset OR EMPTY value",
     "A half-filled template fails loudly at render time instead of booting "
     "with a published placeholder.",
     N, "10b demonstrates the renderer's own DSN refusal, not Compose's `:?`",
     "This is Docker Compose's behaviour, not a control in this repository. "
     "No case exercises a blank `${KEY:?}` interpolation."),

    ("env/production.env.example",
     "# known-false-undisclosed fails if the list stands without this paragraph",
     "Both halves of the known-false admission are enforced.",
     D, "23 and 27", "Marker matching only."),

    ("env/production.env.example",
     "# cluster and not enough to run a parallel query — so this fails MONTHS after",
     "Docker's 64 MiB `/dev/shm` starts a PostgreSQL cluster and fails "
     "parallel plans months later.",
     N, "24 demonstrates the RULE, not the PostgreSQL behaviour",
     "The PostgreSQL failure mode is upstream behaviour, not something this "
     "repository measured. What case 24 shows is that the floor is asserted "
     "from the rendered model, including the exact 64 MiB boundary."),

    ("env/production.env.example",
     "# firewall. The Kubo HTTP API is never published",
     "The Kubo HTTP API (5001) is never published.",
     D, "21 (the same rule, `port-not-allowed`, on a different service)",
     "The IPFS SWARM port 4001 IS public by an explicit per-port "
     "`\"public\": true` with a reason, and nothing here proves it is "
     "firewalled - that is the boot lane's."),

    ("env/production.env.example",
     "# preflight yet: install.sh (VZ-ISSUE-004) will refuse a non-amd64 server host",
     "`install.sh` will refuse a non-amd64 server host - future tense, "
     "declared.",
     D, "22, 28a-28d keep every such sentence future-marked",
     "`install.sh` does not exist. The control is that the sentence cannot be "
     "written in the present tense, not that the script behaves."),

    # ---------------- checker docstrings and banners ----------------
    ("scripts/check-compose-topology.py",
     "diagnostic, never an assertion: if it finds nothing the violation still stands",
     "The YAML locator is a diagnostic and never decides a violation.",
     X, "n/a - code shape",
     "Verifiable by reading `locate_in_sources()`: its return value is only "
     "ever the `file=` field of an already-created violation."),

    ("scripts/check-compose-topology.py",
     "# This is a REFUSAL LIST, not a parser.",
     "The CMD-SHELL check is a refusal list, not a shell parser.",
     D, "26a (`||`), 26b (`#`), 26c (`;` via CMD sh -c)",
     "A shell construct not on the list would pass. The list is `;` `|` `&` "
     "`#` backtick `$(` `<` `>` newline; anything else in a one-word-command "
     "probe is accepted."),

    ("scripts/check-compose-topology.py",
     "    WHAT THIS STILL CANNOT SHOW, stated here because the documents",
     "`probe_invokes()` states its own limits in the code that implements it.",
     X, "n/a - a statement of limits",
     "Nothing. Recorded so the limit travels with the function rather than "
     "only with the prose."),

    ("scripts/check-compose-topology.py",
     "    #                                  Every probe is real now, and the file still",
     "The two disclosure rule ids are distinguishable, so a reviewer can tell "
     "which direction fired.",
     D, "23 and 27 assert different rule ids",
     "Nothing."),

    ("scripts/check-config-coverage.py",
     "A missing dependency is BLOCKED, never a pass.",
     "`--drift` reports BLOCKED and exits 2 when a checkout is absent - never "
     "a pass, never a skip.",
     D, "drift-transcript.txt, the BLOCKED section, exit 2",
     "Nothing."),

    ("scripts/check-config-coverage.py",
     "# Exactly TWO fields of a `keys[]` entry are consumed by any checker",
     "Exactly two fields of a registry key entry are consumed by any checker, "
     "and both are drift-checked.",
     D, "drift-transcript.txt (the `secret` flag); 9a (the name)",
     "`required`, `default`, `delivered_by` and `reason` are documentation "
     "and nothing validates them. The claim that only two are consumed is "
     "checkable by grep over `scripts/*.py` and is recorded in local-run.txt."),

    ("scripts/check-template-claims.py",
     "# UNREACHABLE from any documentation edit: a rule id that cannot fire is a",
     "`unknown-script` is reachable now; it was not before this round.",
     D, "28d (`rotate-secrets.sh`)", "Nothing."),

    ("scripts/compose-render.py",
     "   **WHAT IS NOT PROTECTED, precisely.**",
     "Redaction covers registry-flagged secrets plus the explicit composite "
     "list; an unflagged key is not protected.",
     D, "25, 25b (protected); the verifier's `VIZRA_S3_ACCESS_ID` measurement "
        "(not protected, every lane green)",
     "Stated rather than fixed, on purpose: widening the suffix heuristic "
     "would train people to add exceptions. The component's flag is the "
     "control, and only `--drift` validates it."),

    ("scripts/compose-render.py",
     "   THE LEAK CHECK RUNS ON THE OBJECT THAT IS ABOUT TO BE SERIALISED"
     if False else
     "    # THE LEAK CHECK RUNS ON THE OBJECT THAT IS ABOUT TO BE SERIALISED",
     "The leak check runs on the object being serialised, not on a discarded "
     "copy.",
     D, "18a (0 occurrences across 13 models), 18b (removal of a redact key "
        "fails the render and writes nothing)",
     "It looks for the exact injected VALUES, so it can only find what this "
     "renderer put there. A secret arriving from the operator's real "
     "environment is redacted by key, but only if the key is known."),

    ("scripts/compose-render.py",
     "That is a deliberate property: rendering cannot be",
     "`ci_overrides` is applied after the process environment, so rendering "
     "cannot be made to embed an operator's real session secret.",
     C, "none - `env.update()` ordering, asserted by reading `render()`",
     "`DATABASE_URL` and `VIZRA_CACHE_URL` are NOT in `ci_overrides` and do "
     "take a caller's value; they are redacted rather than overridden. No "
     "case demonstrates the ordering."),

    ("scripts/compose-render.py",
     "4. **Enforces the shape floor.**",
     "The declared floor and the shapes array must name the same ids, so "
     "deleting a shape is a visible edit.",
     D, "12", "Nothing."),
]


def fail(msg):
    sys.stderr.write("UNEVALUABLE: " + msg.rstrip() + "\n  Nothing was written.\n")
    sys.exit(2)


def resolve(path, anchor):
    """(line number, ) for a unique anchor. Refuses anything else."""
    try:
        with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as err:
        fail(f"cannot read {path}: {err}")
    hits = [i + 1 for i, ln in enumerate(lines) if anchor in ln]
    if not hits:
        fail(
            f"the anchor {anchor!r} no longer appears in {path}. The sentence "
            f"it audits was reworded or removed; update CLAIMS in this file "
            f"rather than letting a line number go stale."
        )
    if len(hits) > 1:
        fail(
            f"the anchor {anchor!r} appears {len(hits)} times in {path} "
            f"(lines {hits}); an audit row must name one sentence."
        )
    return hits[0]


def demonstrated_rules():
    """{rule id: sorted case ids} read out of demo.sh, plus the declared sets."""
    text = open(os.path.join(ROOT, DEMO), "r", encoding="utf-8").read()
    cur, hits = None, {}
    for ln in text.splitlines():
        m = re.match(r'\s*case_header "([^"]+)"', ln)
        if m:
            cur = m.group(1).split(" ")[0]
        for r in re.findall(r"rule=([a-z][a-z-]+)", ln):
            hits.setdefault(r, set()).add(cur)
    # The parameterised helpers pass their case id in as $1, so the static scan
    # sees "$id". Recover the real ids from the call sites, which is still
    # reading the harness rather than trusting a hand list.
    for helper in ("probe_case", "script_case"):
        ids = re.findall(r'^%s "([0-9a-z]+)"' % helper, text, re.M)
        body = text.split("%s() {" % helper, 1)[1].split("\n}\n", 1)[0]
        for r in re.findall(r"rule=([a-z][a-z-]+)", body):
            hits.setdefault(r, set()).update(ids)
        for want in re.findall(r'\\\n  "(rule=[a-z-]+)"', text):
            pass
    # script_case takes its expected rule as $4, so read the call sites too.
    for cid, rule in re.findall(
            r'^script_case "([0-9a-z]+)"[^\n]*\n[^\n]*\n[^\n]*\n\s*"rule=([a-z-]+)"',
            text, re.M):
        hits.setdefault(rule, set()).add(cid)
    out = {}
    for r, cs in hits.items():
        out[r] = sorted(c for c in cs if c and c != "$id")
    return out


def declared_rules(path):
    txt = open(os.path.join(ROOT, path), "r", encoding="utf-8").read()
    m = re.search(r"RULES = frozenset\(\{(.*?)\}\)", txt, re.S)
    if not m:
        fail(f"{path} declares no RULES frozenset")
    return sorted(set(re.findall(r'"([a-z][a-z-]+)"', m.group(1))))


LEGEND = {
    "demonstrated": "**demonstrated** — a `demo.sh` case turns it red",
    "code-only": "**code-only** — a real rule, but no case has seen it fire",
    "not ours": "**not ours** — a claim about another component or tool",
    "no mechanism": "**no mechanism** — true of the artefact; nothing enforces it",
}


def build():
    demo = demonstrated_rules()
    rows = []
    for path, anchor, claim, kind, cases, limit in CLAIMS:
        rows.append((path, resolve(path, anchor), claim, kind, cases, limit))

    undemo = []
    for path, label in CHECKERS:
        for r in declared_rules(path):
            if r not in demo:
                undemo.append((label, r))
    total = sum(len(declared_rules(p)) for p, _ in CHECKERS)

    o = []
    w = o.append
    w("# Claims audit — VZ-ISSUE-002 compose topology")
    w("")
    w("GENERATED. Edit `docs/evidence/compose-topology/claims.py` and re-run it;")
    w("do not edit this file by hand. Every line number below is resolved against")
    w("the live file at generation time, and the generator REFUSES to write")
    w("anything if an anchor no longer resolves uniquely — so a stale row is a")
    w("failed run, not a quietly wrong number.")
    w("")
    w("## Why this file exists")
    w("")
    w("Three review rounds on this PR found the same defect in different clothes:")
    w("a checker that matches TEXT, described in this repository's own documents")
    w("with a guarantee word — *enforce*, *refuse*, *cannot*, *never*, *every*,")
    w("*both directions*, *invoke*, *prove*, *by construction*. The topology was")
    w("sound each time; the sentences around it were stronger than the code.")
    w("")
    w("So every such sentence on an operator-facing or CI-facing surface is")
    w("audited here: where it lives, what turns it red, and — the column that")
    w("matters — **what it does not guarantee**. A sentence with no demonstration")
    w("is either softened to what is true or removed; the ones that were are")
    w("listed at the end.")
    w("")
    w("Surfaces audited: `docs/META_REPO.md` §2a; `docs/quality/COMMANDS.md`")
    w("§4–§8; the docstrings and printed banners of `check-compose-topology.py`,")
    w("`check-config-coverage.py`, `check-template-claims.py` and")
    w("`compose-render.py`; `README.md`'s operator section; and")
    w("`env/production.env.example`'s comments about what tooling does.")
    w("")
    w("What is deliberately **not** audited, as a decision rather than an")
    w("omission: the text of a violation message (printed only after its rule has")
    w("already fired); narrative about a defect that was fixed (its evidence is")
    w("the case that keeps it fixed, audited on its own row); and a claim about")
    w("another repository's behaviour, which is marked *not ours* with the")
    w("artefact it rests on rather than dressed up as something this lane proves.")
    w("")
    w("## Legend")
    w("")
    for k in ("demonstrated", "code-only", "not ours", "no mechanism"):
        w(f"- {LEGEND[k]}")
    w("")
    w(f"## The claims ({len(rows)} rows)")
    w("")
    w("| # | Where | Claim | Kind | Red when | What it does NOT guarantee |")
    w("|---:|---|---|---|---|---|")
    for i, (path, line, claim, kind, cases, limit) in enumerate(rows, 1):
        w(f"| {i} | `{path}:{line}` | {claim} | {kind} | {cases} | {limit} |")
    w("")
    w("## Rule ids with no red demonstration")
    w("")
    w(f"**{len(undemo)} of {total}** declared rule ids across the three checkers")
    w("have never been seen to fire. They are asserted by code review only. This")
    w("is not an argument that they are wrong — it is the distinction a reader")
    w("needs in order to say what a green lane proves, and the tables in")
    w("`docs/quality/COMMANDS.md` do not draw it on their own.")
    w("")
    w("| Checker | Rule id |")
    w("|---|---|")
    for label, r in undemo:
        w(f"| {label} | `{r}` |")
    w("")
    w("`registry-drift` is among them for `demo.sh` specifically: it is")
    w("demonstrated red and green in")
    w("`docs/evidence/compose-topology/drift-transcript.txt`, which cannot run in")
    w("CI because there is no token for the private component repositories.")
    w("")
    w("## Softened or removed this round")
    w("")
    w("| Sentence, as it stood at `9c4b5d3` | Disposition |")
    w("|---|---|")
    w("| \"it fails in **both directions**, so the list and the paragraphs are "
      "deleted together\" — `META_REPO.md`, `COMMANDS.md`, the code comment and "
      "the PR body | **Made true.** `known-false-stale-disclosure` added; both "
      "directions demonstrated by rule id (cases 23 and 27). |")
    w("| \"must be listed in `gated_probes` and still **invoke** the command\" — "
      "`META_REPO.md`; \"whose probe no longer **invokes** the declared "
      "command\" — `COMMANDS.md` | **Made true, and bounded.** The rule is now "
      "structural (cases 26, 26a–26e), and both documents now state the two "
      "things it still cannot show. |")
    w("| \"Shell scripts, **backticked or bare**\" — `check-template-claims.py` | "
      "**Made true.** The matcher takes any `*.sh` token with an optional path "
      "prefix (cases 28a–28e), and `unknown-script` is reachable (28d). |")
    w("| \"Before rendering anything it refuses a Compose below 2.24.4\" — "
      "`COMMANDS.md` §4 | **Softened.** The sentence now says the path is not "
      "exercised by any demonstration and should be read as reviewed code. |")
    w("| \"The default-shape caps sum to 4092 MiB on a 4096 MiB host, and that is "
      "deliberate\" — `COMMANDS.md` §5a | **Corrected.** The *oversubscription* "
      "is deliberate; landing under physical RAM is a coincidence, and the "
      "number that matters is a ~2.3 GB realistic concurrent peak. |")
    w("| `curl -fsS …/readyz` in `README.md` and `env/production.env.example` | "
      "**Corrected.** `-f` exits 0 on a 200 `degraded`, so the documented "
      "command read as OK on a degraded instance. `-f` dropped and the "
      "semantics stated on the same line. |")
    w("| README's diagnostic ports | **Corrected.** `:8080` and `:3000` now name "
      "`VIZRA_HTTP_PORT` and `VIZRA_FRONTEND_PORT` beside them. |")
    w("| Nothing said which rule ids had never fired | **Added.** The table "
      "above, computed from `demo.sh`, plus a pointer to it in `COMMANDS.md` §8. |")
    w("")
    w("## Known weak spots this file does not fix")
    w("")
    w("Recorded because a claims audit that only lists what was fixed is the")
    w("same failure one level up.")
    w("")
    w("- **The disclosure rules match a marker string.** Stripping the `curl`")
    w("  commands while leaving the heading passes. The verifier measured this")
    w("  at `9c4b5d3` and it is still true.")
    w("- **`profile-not-enumerated` reads only compose files some shape lists.**")
    w("  A new `docker-compose.*.yml` that no shape loads is read by neither it")
    w("  nor any rendered model.")
    w("- **An unflagged credential is written raw** into the uploaded artifact")
    w("  (S-6). Stated, not fixed: widening the suffix heuristic would train")
    w("  people to add exceptions, and the component's own flag is meant to be")
    w("  the control.")
    w("- **The `secret` flag is validated only locally.** `--drift` needs the")
    w("  component checkouts and cannot run in this repository's CI.")
    w("- **`scripts/ci-required-guard.sh` (lines 80, 249, 348, 423, 440) and")
    w("  `scripts/ci-required-select.sh` (line 56)** still read captured output")
    w("  through `printf … | grep -q` under `set -o pipefail` — the same race")
    w("  removed from `demo.sh` this round. They are outside this slice's diff")
    w("  and are recorded here as a follow-up rather than edited alongside the")
    w("  thing they guard.")
    w("")
    return "\n".join(o) + "\n"


def main(argv):
    text = build()
    if "--check" in argv:
        try:
            with open(OUT, "r", encoding="utf-8") as fh:
                have = fh.read()
        except OSError:
            have = None
        if have != text:
            sys.stderr.write(
                "CLAIMS.md is stale: re-run "
                "`python3 docs/evidence/compose-topology/claims.py`.\n"
            )
            return 1
        print(f"CLAIMS.md is current ({len(CLAIMS)} audited claims)")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(CLAIMS)} audited claims")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
