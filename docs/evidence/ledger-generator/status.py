"""Ledger status: recorded only with evidence, never hand-asserted.

`build.py` calls this module. It is the OFFLINE half of the rule; the ONLINE half
(is the merge commit really on the component repo's `main`, did GitHub really
merge that PR from that head, is `ci-required` really green on that head) is
`scripts/check-ledger-status-remote.py`, which the `validate` lane runs with
`gh api`. Both read the same file, `status_records.json`, through `load_records`
below, so the two halves cannot disagree about what a record is.

Why the split. The generator must stay reproducible offline: the regeneration
check (`scripts/check-generated-ledger.sh`) re-runs it under two locales and
diffs the bytes, and a generator whose output depended on the network would make
that check flaky or, worse, would make the ledger's bytes depend on who ran it
and when. So the generator checks everything the TREE can prove — the record's
shape, the verdict line in a committed evidence file, the acceptance bullets it
cites — and the remote checker proves the facts only GitHub knows. The lane runs
both; neither alone admits a status.

THE RULES (default-deny: anything not explicitly admitted below is refused by
name):

1. A section source can never set a status. Every requirement must leave the
   DSL (`core.req`) as PLANNED / UNVERIFIED / NOT_STARTED / NOT_RELEASED with an
   empty `evidence` list. Anything else is a hand assertion and is refused.
2. A status comes from exactly one place: a record in `status_records.json`.
   A record may claim `IMPLEMENTED` or `VERIFIED`. Every other value — including
   the other members of the ledger's own vocabulary, such as `IN_PROGRESS` — is
   refused by name. There is no partial status.
3. `IMPLEMENTED`: at least one merge `{repo, pr, verified_head, merge_commit}`;
   SHAs are full 40-hex lowercase; no evidence file (a verdict is what makes a
   record VERIFIED, so an IMPLEMENTED record that carries one is contradictory).
4. `VERIFIED`: every merge carries `evidence_file`, a committed regular file
   under `docs/evidence/warroom/`, whose final non-empty line is
       FINAL VERDICT: PASS — SHA <40-hex>
   or  FINAL VERDICT: PASS (<qualifier>) — SHA <40-hex>
   and whose SHA equals THAT merge's `verified_head`. A qualifier such as
   "(local; CI BLOCKED)" is accepted here only because the remote half then
   requires `ci-required` green on the same SHA — a local PASS never proves CI.
5. Floors that stop a component half being recorded as the whole requirement:
   - a requirement with a `ui` surface needs a `vizra-user` merge;
   - a requirement with an `api` surface needs a `vizra-core` merge;
   - every `docs/issues/*.md` whose `**Ledger IDs:**` line names the requirement
     must be cited by at least one acceptance bullet from that issue's
     `## Acceptance` section, quoted exactly.
   These are FLOORS, not a proof of completeness: whether the merges deliver the
   whole ledger outcome is still a reviewed judgement, written in `rationale`.
6. Release state is never set here, by anything.
"""
import json
import os
import re

RECORDABLE = ("IMPLEMENTED", "VERIFIED")
REPOS = ("vizra", "vizra-core", "vizra-user", "vizra-search")
RECORD_KEYS = {"id", "status", "rationale", "acceptance", "merges"}
MERGE_KEYS_REQUIRED = {"repo", "pr", "verified_head", "merge_commit"}
MERGE_KEYS_OPTIONAL = {"evidence_file"}
ACCEPTANCE_KEYS = {"issue", "bullet"}
TOP_KEYS = {"schema", "github_owner", "records"}
SCHEMA = 1
EVIDENCE_DIR = "docs/evidence/warroom/"

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VERDICT_RE = re.compile(r"^FINAL VERDICT: PASS(?: \([^()\n]*\))? — SHA ([0-9a-f]{40})$")
OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")

# The DSL's defaults. Anything else leaving core.req is a hand assertion.
DSL_DEFAULTS = {
    "implementation_status": "PLANNED",
    "verification_status": "UNVERIFIED",
    "merge_status": "NOT_STARTED",
    "release_status": "NOT_RELEASED",
}

ID_RE = re.compile(r"\b(VZ-[A-Z]+(?:-[A-Z]+)*)-(\d{3})(?![\d])")
CONT_RE = re.compile(r"(…|\.\.\.|–|—|/)(\d{3})(?![\d-])")


def check_dsl_defaults(reqs):
    """Rule 1: no section source may set a status or evidence."""
    errors = []
    for r in reqs:
        for key, want in DSL_DEFAULTS.items():
            got = r.get(key)
            if got != want:
                errors.append(
                    f"{r['id']}: HAND-ASSERTED {key} {got!r} in a section source. "
                    f"A status comes only from a record in status_records.json; the DSL "
                    f"must leave every entry {want}.")
        if r.get("evidence") != []:
            errors.append(
                f"{r['id']}: HAND-ASSERTED evidence in a section source. Evidence is "
                f"written only from a checked record in status_records.json.")
    return errors


def load_records(path):
    """Parse and structurally validate the records file. Returns (doc, errors).

    Shared with scripts/check-ledger-status-remote.py, so the offline and online
    halves read one definition of a record.
    """
    errors = []
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        return None, [f"MISSING STATUS RECORDS: {path} does not exist. It must exist, even "
                      f"when empty, so that its absence cannot be mistaken for 'no claims'."]
    except ValueError as exc:
        return None, [f"STATUS RECORDS DO NOT PARSE: {path}: {exc}"]
    if not isinstance(doc, dict):
        return None, [f"STATUS RECORDS: {path}: the top level must be an object"]
    extra = sorted(set(doc) - TOP_KEYS)
    missing = sorted(TOP_KEYS - set(doc))
    if extra:
        errors.append(f"STATUS RECORDS: unknown top-level key(s) {extra}; refused")
    if missing:
        errors.append(f"STATUS RECORDS: missing top-level key(s) {missing}")
    if doc.get("schema") != SCHEMA:
        errors.append(f"STATUS RECORDS: schema must be {SCHEMA}, got {doc.get('schema')!r}")
    owner = doc.get("github_owner")
    if not isinstance(owner, str) or not OWNER_RE.match(owner):
        errors.append(f"STATUS RECORDS: github_owner {owner!r} is not a GitHub account name")
    records = doc.get("records")
    if not isinstance(records, list):
        errors.append("STATUS RECORDS: records must be a list")
        return doc, errors
    seen = set()
    for i, rec in enumerate(records):
        errors.extend(_check_record_shape(i, rec, seen))
    return doc, errors


def _label(i, rec):
    rid = rec.get("id") if isinstance(rec, dict) else None
    return f"status record #{i} ({rid})" if rid else f"status record #{i}"


def _check_record_shape(i, rec, seen):
    errors = []
    if not isinstance(rec, dict):
        return [f"status record #{i}: must be an object"]
    label = _label(i, rec)
    extra = sorted(set(rec) - RECORD_KEYS)
    missing = sorted(RECORD_KEYS - set(rec))
    if extra:
        errors.append(f"{label}: unknown key(s) {extra}; refused (default-deny)")
    if missing:
        errors.append(f"{label}: missing key(s) {missing}")
    rid = rec.get("id")
    if not isinstance(rid, str) or not rid:
        errors.append(f"{label}: id must be a non-empty string")
    elif rid in seen:
        errors.append(f"{label}: a second record for {rid}; one record per requirement")
    else:
        seen.add(rid)
    status = rec.get("status")
    if status not in RECORDABLE:
        errors.append(
            f"{label}: status {status!r} is REFUSED. A record may claim only "
            f"{' or '.join(RECORDABLE)}; anything else is refused by name.")
    rationale = rec.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append(f"{label}: rationale must say, in words, why the whole requirement is met")
    acc = rec.get("acceptance")
    if not isinstance(acc, list) or not acc:
        errors.append(f"{label}: acceptance must be a non-empty list of quoted issue bullets")
    else:
        for j, a in enumerate(acc):
            if not isinstance(a, dict) or set(a) != ACCEPTANCE_KEYS:
                errors.append(f"{label}: acceptance[{j}] must have exactly the keys {sorted(ACCEPTANCE_KEYS)}")
            elif not all(isinstance(a[k], str) and a[k] for k in ACCEPTANCE_KEYS):
                errors.append(f"{label}: acceptance[{j}] values must be non-empty strings")
    merges = rec.get("merges")
    if not isinstance(merges, list) or not merges:
        errors.append(f"{label}: merges must be a non-empty list; a status needs a merge")
        return errors
    pairs = set()
    for j, m in enumerate(merges):
        where = f"{label}: merges[{j}]"
        if not isinstance(m, dict):
            errors.append(f"{where}: must be an object")
            continue
        extra = sorted(set(m) - MERGE_KEYS_REQUIRED - MERGE_KEYS_OPTIONAL)
        missing = sorted(MERGE_KEYS_REQUIRED - set(m))
        if extra:
            errors.append(f"{where}: unknown key(s) {extra}; refused (default-deny)")
        if missing:
            errors.append(f"{where}: missing key(s) {missing}")
        if m.get("repo") not in REPOS:
            errors.append(f"{where}: repo {m.get('repo')!r} is not one of {list(REPOS)}")
        pr = m.get("pr")
        if not isinstance(pr, int) or isinstance(pr, bool) or pr <= 0:
            errors.append(f"{where}: pr must be a positive integer, got {pr!r}")
        for k in ("verified_head", "merge_commit"):
            v = m.get(k)
            if not isinstance(v, str) or not SHA_RE.match(v):
                errors.append(f"{where}: {k} {v!r} is not a full 40-character lowercase SHA")
        if m.get("verified_head") and m.get("verified_head") == m.get("merge_commit"):
            errors.append(f"{where}: verified_head equals merge_commit; the verified head is the "
                          f"PR head the verifier judged, the merge commit is what landed on main")
        key = (m.get("repo"), pr)
        if key in pairs:
            errors.append(f"{where}: {key[0]}#{key[1]} listed twice")
        pairs.add(key)
        has_file = "evidence_file" in m
        if status == "VERIFIED" and not has_file:
            errors.append(
                f"{where}: VERIFIED with NO EVIDENCE — every merge of a VERIFIED record needs an "
                f"evidence_file under {EVIDENCE_DIR} whose final line is the verifier's PASS on "
                f"that merge's verified_head.")
        if status == "IMPLEMENTED" and has_file:
            errors.append(
                f"{where}: IMPLEMENTED carries an evidence_file. A verifier's verdict is what makes a "
                f"record VERIFIED; claim VERIFIED (and meet its rules) or drop the file.")
    return errors


def final_line(path):
    with open(path, encoding="utf-8") as fh:
        lines = [ln.rstrip("\r\n") for ln in fh]
    for ln in reversed(lines):
        if ln.strip():
            return ln
    return ""


def check_evidence_file(where, rel, head, root):
    """Rule 4. Returns (errors, verdict_line)."""
    if not isinstance(rel, str) or not rel.startswith(EVIDENCE_DIR) or ".." in rel.split("/") \
            or rel.startswith("/") or "\\" in rel:
        return [f"{where}: evidence_file {rel!r} must be a relative path under {EVIDENCE_DIR}"], None
    path = os.path.join(root, rel)
    base = os.path.realpath(os.path.join(root, EVIDENCE_DIR))
    if os.path.islink(path) or not os.path.realpath(path).startswith(base + os.sep):
        return [f"{where}: evidence_file {rel} is a symlink or escapes {EVIDENCE_DIR}; refused"], None
    if not os.path.isfile(path):
        return [f"{where}: MISSING EVIDENCE FILE {rel}; a verdict that is not in the tree is not evidence"], None
    line = final_line(path)
    m = VERDICT_RE.match(line)
    if not m:
        return [f"{where}: {rel} does not END with a PASS verdict. Its final non-empty line is "
                f"{line[:160]!r}; required 'FINAL VERDICT: PASS[ (…)] — SHA <40-hex>'. "
                f"A verdict anywhere else in the file, a FAIL, or an abbreviated SHA does not count."], None
    if m.group(1) != head:
        return [f"{where}: VERDICT SHA MISMATCH — {rel} ends with a PASS on {m.group(1)}, but the "
                f"record's verified_head is {head}. The verdict must name the exact head that was merged."], None
    return [], line


def issue_ledger_ids(text):
    """Ids named on an issue's `**Ledger IDs:**` line, with …/– ranges and / lists expanded."""
    ids = set()
    for line in text.splitlines():
        if not line.startswith("**Ledger IDs:**"):
            continue
        for m in ID_RE.finditer(line):
            prefix, num = m.group(1), int(m.group(2))
            ids.add(f"{prefix}-{num:03d}")
            pos, prev = m.end(), num
            while True:
                c = CONT_RE.match(line, pos)
                if not c:
                    break
                val = int(c.group(2))
                if c.group(1) == "/":
                    ids.add(f"{prefix}-{val:03d}")
                else:
                    for n in range(prev + 1, val + 1):
                        ids.add(f"{prefix}-{n:03d}")
                prev, pos = val, c.end()
    return ids


def acceptance_bullets(text):
    bullets, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.startswith("## Acceptance")
            continue
        if inside and line.startswith("- "):
            bullets.append(line[2:].rstrip())
    return bullets


def load_issues(root):
    issues = {}
    d = os.path.join(root, "docs", "issues")
    for name in sorted(os.listdir(d)):
        if name.startswith("VZ-ISSUE-") and name.endswith(".md"):
            with open(os.path.join(d, name), encoding="utf-8") as fh:
                text = fh.read()
            issues[f"docs/issues/{name}"] = (issue_ledger_ids(text), acceptance_bullets(text))
    return issues


def apply_records(reqs, doc, root):
    """Rules 3–6 against the tree, then write the admitted statuses into `reqs`.

    Nothing is written unless EVERY record validates: a partly applied ledger
    would be a ledger whose statuses depend on the order of the records.
    """
    errors = []
    by_id = {r["id"]: r for r in reqs}
    issues = load_issues(root)
    admitted = []
    for i, rec in enumerate(doc["records"]):
        label = _label(i, rec)
        req = by_id.get(rec["id"])
        if req is None:
            errors.append(f"{label}: no requirement {rec['id']} in the ledger")
            continue
        repos = {m["repo"] for m in rec["merges"]}
        if req["surfaces"]["ui"] and "vizra-user" not in repos:
            errors.append(f"{label}: {rec['id']} has ui surface(s) {req['surfaces']['ui']} but the record "
                          f"names no vizra-user merge; a component half is not the requirement")
        if req["surfaces"]["api"] and "vizra-core" not in repos:
            errors.append(f"{label}: {rec['id']} has api surface(s) but the record names no vizra-core merge")
        cited = {}
        for a in rec["acceptance"]:
            entry = issues.get(a["issue"])
            if entry is None:
                errors.append(f"{label}: acceptance cites {a['issue']!r}, which is not an issue file")
                continue
            if a["bullet"] not in entry[1]:
                errors.append(f"{label}: acceptance bullet not found verbatim in the '## Acceptance' "
                              f"section of {a['issue']}: {a['bullet'][:120]!r}")
                continue
            cited[a["issue"]] = True
        for path, (ids, _b) in issues.items():
            if rec["id"] in ids and path not in cited:
                errors.append(f"{label}: {path} schedules {rec['id']} (its Ledger IDs line names it) and "
                              f"the record cites none of its acceptance bullets. A requirement split "
                              f"across issues is not complete after the first one.")
        evidence = [{"kind": "status_record", "status": rec["status"], "rationale": rec["rationale"],
                     "acceptance": rec["acceptance"]}]
        for j, m in enumerate(rec["merges"]):
            item = {"kind": "merge", "repo": m["repo"], "pr": m["pr"],
                    "verified_head": m["verified_head"], "merge_commit": m["merge_commit"]}
            if rec["status"] == "VERIFIED":
                errs, line = check_evidence_file(f"{label}: merges[{j}]", m["evidence_file"],
                                                 m["verified_head"], root)
                errors.extend(errs)
                item["evidence_file"] = m["evidence_file"]
                item["final_verdict"] = line
            evidence.append(item)
        admitted.append((req, rec["status"], evidence))
    if errors:
        return errors
    for req, status, evidence in admitted:
        req["implementation_status"] = status
        req["verification_status"] = "VERIFIED_AT_SHA" if status == "VERIFIED" else "UNVERIFIED"
        req["merge_status"] = "MERGED"
        req["evidence"] = evidence
        assert req["release_status"] == "NOT_RELEASED"
    return []
