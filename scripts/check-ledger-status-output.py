#!/usr/bin/env python3
"""The ledger's statuses, checked on the OUTPUT, out of process.

The generator's own status checks (docs/evidence/ledger-generator/status.py) run
INSIDE the process that has just imported every section source, and a section
source can defeat them. The meta PR #6 verifier did it three ways, each with the
whole lane green and zero records:

  2c  an extra key:        REQS[-1]["status"] = "VERIFIED"
  2d  a str subclass:      class _S(str): __ne__ -> False; implementation_status=_S("VERIFIED")
  2e  a wrapper:           status.check_dsl_defaults monkeypatched to drop one id's errors

This script is the guard against that class. It never imports `core` or any
section source. It reads the COMMITTED `docs/quality/features.json` as plain
JSON, which a Python object cannot survive: a `str` subclass is a str again, and
an extra key is visible. It then asserts:

  1. the working tree matches HEAD for the ledger, the records, the issues and
     the war-room evidence, with nothing untracked there, so what is checked is
     what was committed and nothing a build step rewrote on disk;
  2. the top-level keys are exactly the ones build.py writes, every feature has
     EXACTLY the keys `core.req` emits (and exactly the nested `cases` /
     `surfaces` keys);
  3. the set of ids whose implementation/verification/merge/release status is
     not PLANNED/UNVERIFIED/NOT_STARTED/NOT_RELEASED, or whose `evidence` is
     non-empty, EQUALS the set of ids in the committed status_records.json;
  4. re-deriving every entry from scratch — each status reset to its default,
     then the committed records applied by `status.apply_records` in THIS fresh
     process — reproduces the committed JSON exactly, so each recorded value is
     what its record admits, and nothing else;
  5. the summary's status counts equal the counts in the features;
  6. (fix round 2) neither JSON file has a DUPLICATE KEY at any level, and the
     bytes of features.json equal the generator's own serialisation of what was
     parsed (`json.dump(..., indent=2, ensure_ascii=False)`, no trailing
     newline). A text that carries more than the parse keeps (a duplicate key
     before the real one, which Python, jq and node all resolve to the LAST
     value) is refused, not silently resolved;
  7. `test_ids` is [] everywhere (core.req always emits []);
  8. every evidence file a VERIFIED record cites is on meta `main`
     (refs/remotes/origin/main) with identical bytes, so a pull request cannot
     cite a verdict it introduces itself. CI fetches `main` before this step.

It deliberately does import `status.py` from the generator directory, for step
4. That module in a fresh process is not influenced by any section source (none
is imported). A PR that edits status.py or this script is visible in its diff,
and that is all: CODEOWNERS is advisory (no branch protection or ruleset
requires owner review), so the war room's verifier-gated merge is the only
review. This check does not and cannot defend against that.

Exit 0 when all hold; 1 with every violation named otherwise; 2 when it cannot
run (no git, not a checkout).
"""
import copy
import json
import os
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
GEN = os.path.join(ROOT, "docs", "evidence", "ledger-generator")
FEATURES = "docs/quality/features.json"
RECORDS = "docs/evidence/ledger-generator/status_records.json"
PINNED_PATHS = [FEATURES, RECORDS, "docs/issues", "docs/evidence/warroom"]

# Exactly what core.req emits, in order. test_status.py asserts this list equals
# the keys of a dict core.req really produces, so the two cannot drift silently.
FEATURE_KEYS = ("id", "title", "area", "outcome", "source_kind", "provenance", "reference_edition",
                "profiles", "dependencies", "cases", "surfaces", "evidence_required",
                "competitor_mechanism_vs_equivalent", "unresolved", "decided", "notes",
                "implementation_status", "verification_status", "merge_status", "release_status",
                "test_ids", "evidence")
CASES_KEYS = ("success", "negative", "privacy", "recovery")
SURFACES_KEYS = ("api", "ui", "cli")
TOP_KEYS = ("schema_version", "generated", "notice", "parity_baseline_status", "status_vocabulary",
            "source_kinds", "summary", "features")
DEFAULTS = {"implementation_status": "PLANNED", "verification_status": "UNVERIFIED",
            "merge_status": "NOT_STARTED", "release_status": "NOT_RELEASED"}


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True)


def check_tree_matches_head(errors):
    p = git("rev-parse", "--is-inside-work-tree")
    if p.returncode != 0:
        print("CANNOT RUN: not a git checkout; the committed ledger cannot be identified.")
        sys.exit(2)
    d = git("diff", "--name-only", "HEAD", "--", *PINNED_PATHS)
    u = git("ls-files", "--others", "--exclude-standard", "--", *PINNED_PATHS)
    if d.returncode != 0 or u.returncode != 0:
        errors.append(f"git could not compare the tree with HEAD: {d.stderr.strip()} {u.stderr.strip()}")
        return
    for f in d.stdout.split():
        errors.append(f"TREE DIFFERS FROM HEAD: {f} — this check reads the COMMITTED ledger; commit or revert it")
    for f in u.stdout.split():
        errors.append(f"UNTRACKED FILE: {f} — nothing uncommitted may feed the ledger check")


class DuplicateKey(ValueError):
    pass


def refuse_duplicates(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            owner = next((v for kk, v in pairs if kk == "id"), None)
            raise DuplicateKey(f"DUPLICATE KEY {k!r}" + (f" in entry {owner}" if owner else "")
                               + " — a parser keeps one value and a reader of the text may see the other")
        seen.add(k)
    return dict(pairs)


def strict_load(rel, errors):
    with open(os.path.join(ROOT, rel), "rb") as fh:
        raw = fh.read()
    try:
        return raw, json.loads(raw.decode("utf-8"), object_pairs_hook=refuse_duplicates)
    except DuplicateKey as exc:
        errors.append(f"{rel}: {exc}")
    except (UnicodeDecodeError, ValueError) as exc:
        errors.append(f"{rel}: does not parse as strict UTF-8 JSON: {exc}")
    return raw, None


def check_evidence_on_main(records_raw, errors):
    files = []
    for r in records_raw.get("records", []):
        if isinstance(r, dict) and r.get("status") == "VERIFIED":
            for m in r.get("merges", []):
                if isinstance(m, dict) and isinstance(m.get("evidence_file"), str):
                    files.append((r.get("id"), m["evidence_file"]))
    if not files:
        return
    if git("rev-parse", "--verify", "-q", "refs/remotes/origin/main").returncode != 0:
        errors.append("refs/remotes/origin/main is not available, so no VERIFIED record's evidence can be "
                      "placed on meta main; fetch it (CI: git fetch --depth=1 origin main) — refused, not skipped")
        return
    for rid, rel in files:
        on_main = subprocess.run(["git", "-C", ROOT, "show", f"refs/remotes/origin/main:{rel}"], capture_output=True)
        if on_main.returncode != 0:
            errors.append(f"{rid}: EVIDENCE NOT ON META MAIN — {rel} does not exist on origin/main. Evidence must be "
                          f"merged before a status can cite it; a PR cannot cite a verdict it introduces itself")
            continue
        try:
            with open(os.path.join(ROOT, rel), "rb") as fh:
                local = fh.read()
        except OSError:
            local = None
        if local != on_main.stdout:
            errors.append(f"{rid}: EVIDENCE DIFFERS FROM META MAIN — {rel} in this tree is not byte-identical to "
                          f"origin/main:{rel}")


def main():
    errors = []
    check_tree_matches_head(errors)
    raw, doc = strict_load(FEATURES, errors)
    _, records_raw = strict_load(RECORDS, errors)
    if doc is None or records_raw is None:
        print("\n".join(errors))
        print(f"LEDGER STATUS OUTPUT CHECK FAILED: {len(errors)} problem(s)")
        return 1
    canonical = json.dumps(doc, indent=2, ensure_ascii=False).encode("utf-8")
    if raw != canonical:
        n = next((i for i, (a, b) in enumerate(zip(raw, canonical)) if a != b), min(len(raw), len(canonical)))
        line = raw[:n].count(b"\n") + 1
        errors.append(f"{FEATURES}: NON-CANONICAL BYTES — the file differs from the generator's serialisation of "
                      f"its own parse, first at byte {n} (line {line}); the text carries something the parse "
                      f"does not")
    check_evidence_on_main(records_raw, errors)

    if tuple(doc) != TOP_KEYS:
        errors.append(f"features.json top-level keys are {list(doc)}, expected exactly {list(TOP_KEYS)}")
    feats = doc.get("features", [])
    for f in feats:
        fid = f.get("id", "<no id>")
        if tuple(f) != FEATURE_KEYS:
            extra = sorted(set(f) - set(FEATURE_KEYS))
            missing = sorted(set(FEATURE_KEYS) - set(f))
            errors.append(f"{fid}: KEY SET differs from what core.req emits"
                          + (f"; extra {extra}" if extra else "") + (f"; missing {missing}" if missing else "")
                          + ("; order differs" if not extra and not missing else ""))
        if f.get("test_ids") != []:
            errors.append(f"{fid}: test_ids is {f.get('test_ids')!r}; core.req always emits []")
        if tuple(f.get("cases", {})) != CASES_KEYS:
            errors.append(f"{fid}: cases keys {list(f.get('cases', {}))}, expected {list(CASES_KEYS)}")
        if tuple(f.get("surfaces", {})) != SURFACES_KEYS:
            errors.append(f"{fid}: surfaces keys {list(f.get('surfaces', {}))}, expected {list(SURFACES_KEYS)}")

    record_ids = {r.get("id") for r in records_raw.get("records", []) if isinstance(r, dict)}
    claimed = set()
    for f in feats:
        if any(f.get(k) != v for k, v in DEFAULTS.items()) or f.get("evidence") != []:
            claimed.add(f.get("id"))
    for fid in sorted(claimed - record_ids, key=str):
        f = next(x for x in feats if x.get("id") == fid)
        vals = {k: f.get(k) for k in DEFAULTS}
        errors.append(f"{fid}: STATUS WITHOUT A RECORD — features.json carries {vals}"
                      f"{' and evidence' if f.get('evidence') else ''}, and status_records.json has no record for it")
    for rid in sorted(record_ids - claimed, key=str):
        errors.append(f"{rid}: a record exists but features.json shows no status for it; regenerate")

    # Re-derive every entry in this fresh process and compare the whole entry.
    sys.path.insert(0, GEN)
    import status  # noqa: E402  (no section source is imported in this process)
    rdoc, rerr = status.load_records(os.path.join(ROOT, RECORDS))
    errors += [f"records: {e}" for e in rerr]
    if not rerr:
        pristine = copy.deepcopy(feats)
        for f in pristine:
            f.update(DEFAULTS)
            f["evidence"] = []
        aerr = status.apply_records(pristine, rdoc, ROOT)
        errors += [f"records: {e}" for e in aerr]
        if not aerr:
            for got, want in zip(feats, pristine):
                if json.dumps(got, sort_keys=True) != json.dumps(want, sort_keys=True):
                    fields = sorted(k for k in set(got) | set(want) if got.get(k) != want.get(k))
                    errors.append(f"{got.get('id')}: RE-DERIVATION MISMATCH in {fields} — the committed entry is "
                                  f"not what the committed records admit")

    summ = doc.get("summary", {})
    for key, field in (("by_implementation_status", "implementation_status"),
                       ("by_verification_status", "verification_status")):
        counts = {}
        for f in feats:
            counts[f.get(field)] = counts.get(f.get(field), 0) + 1
        if summ.get(key) != dict(sorted(counts.items())):
            errors.append(f"summary.{key} is {summ.get(key)} but the features count {dict(sorted(counts.items()))}")

    if errors:
        print("\n".join(errors))
        print(f"LEDGER STATUS OUTPUT CHECK FAILED: {len(errors)} problem(s)")
        return 1
    print(f"ledger status output: {len(feats)} entries, exact key set; "
          f"{len(claimed)} carry a status, {len(record_ids)} record(s), sets equal; "
          f"every entry re-derived from the committed records in a fresh process")
    return 0


if __name__ == "__main__":
    sys.exit(main())
