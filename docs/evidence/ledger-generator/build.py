import json, os, sys, importlib, collections
import core
import status
for m in ["s0_foundation","s1_install_ops","s2_identity","s3_media","s4_storage_integrations","s5_organization","s6_community","s7_search_analytics","s8_admin_brand","s9_ui_design"]:
    importlib.import_module(m)
reqs = core.REQS
ids = {r["id"] for r in reqs}
errors = []
required = ["id","title","area","outcome","source_kind","provenance","profiles","dependencies","cases","surfaces","evidence_required","implementation_status","verification_status"]
for r in reqs:
    for k in required:
        if k not in r or r[k] in (None, [], ""):
            if k in ("dependencies",):  # allowed empty
                continue
            errors.append(f"{r['id']}: missing {k}")
    for d in r["dependencies"]:
        if d not in ids: errors.append(f"{r['id']}: unknown dependency {d}")
    for p in r["profiles"]:
        if p not in ("core","full"): errors.append(f"{r['id']}: bad profile {p}")
    if "full" not in r["profiles"]: errors.append(f"{r['id']}: every requirement must be in full")
    if not r["cases"]["success"]: errors.append(f"{r['id']}: no success case")
    if not r["evidence_required"]: errors.append(f"{r['id']}: no evidence_required")
# Status: a section source may not set one (status.check_dsl_defaults); the only
# source of a status is a checked record in status_records.json. See status.py
# for the rules and scripts/check-ledger-status-remote.py for the online half.
errors += status.check_dsl_defaults(reqs)
here = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.normpath(os.path.join(here, "..", "..", ".."))
records_doc, record_errors = status.load_records(os.path.join(here, "status_records.json"))
errors += record_errors
if not errors:
    errors += status.apply_records(reqs, records_doc, repo_root)
# core profile closure: a core requirement may not depend on a full-only requirement
for r in reqs:
    if "core" in r["profiles"]:
        for d in r["dependencies"]:
            dep = next(x for x in reqs if x["id"]==d)
            if "core" not in dep["profiles"]:
                errors.append(f"{r['id']} (core) depends on full-only {d}")
# cycle check
graph = {r["id"]: r["dependencies"] for r in reqs}
state = {}
def visit(n, stack):
    if state.get(n)==1: errors.append("cycle: "+" -> ".join(stack+[n])); return
    if state.get(n)==2: return
    state[n]=1
    for d in graph.get(n,[]): visit(d, stack+[n])
    state[n]=2
for n in graph: visit(n, [])
if errors:
    print("\n".join(errors)); sys.exit(1)
by_area = collections.Counter(r["area"] for r in reqs)
by_kind = collections.Counter(r["source_kind"] for r in reqs)
core_n = sum(1 for r in reqs if "core" in r["profiles"])
unresolved = sorted({q for r in reqs for q in r["unresolved"]})
decided = sorted({q for r in reqs for q in r.get("decided", [])})
out = {
  "schema_version": 4,
  "generated": "2026-09-15",
  "notice": "Atomic requirement ledger produced by Prompt 00 on 2026-09-15. An entry is PLANNED/UNVERIFIED/NOT_STARTED/NOT_RELEASED unless a record in docs/evidence/ledger-generator/status_records.json admits IMPLEMENTED or VERIFIED. What enforces that, and how far: scripts/check-ledger-status-output.py parses THIS file as plain JSON in a separate process that imports no section source, refuses a duplicate key at any level and any byte that differs from re-serialising its own parse with the generator's settings (bytes the generator itself would not write, such as 192.0 for 192, are refused by the regeneration check in the same lane), requires exactly the keys core.req emits (test_ids always []), and re-derives every entry's status from the committed records, so a status with no record, however it was produced, turns the validate lane red (probed: a hand edit, a section source, an extra key, a str subclass, an in-process wrapper, a replaced json.dump); free-text fields such as notes and title are not status fields and are not checked for status words; the generator (status.py) refuses a claimed status other than IMPLEMENTED/VERIFIED by name and, for VERIFIED, requires the evidence file under docs/evidence/warroom/ to END with a PASS (no qualifier, or exactly '(local; CI BLOCKED)') on the merged head, and the output check and the remote check both require that file to be on meta main with identical bytes, so a PR cannot cite evidence it introduces itself; scripts/check-ledger-status-remote.py proves with the GitHub API that each PR merged into main from that head as that merge commit, that the commit is on the component repo's main, and for VERIFIED that ci-required succeeded on the verified head. These run on meta pull requests and merge-queue entries, not on main after a merge. Not defended: a pull request that edits the checkers themselves. No mechanism enforces review of such a change today (CODEOWNERS is advisory: no branch protection or ruleset requires it); the war room's verifier-gated merge is the only review. Also not established: who wrote an evidence file, beyond that it is on meta main with identical bytes before a record cites it. A recorded entry lists its merges under `evidence`. The generator never sets release_status. Removing or narrowing an entry requires an owner decision recorded in docs/OPEN_QUESTIONS.md. Open questions ratified 2026-09-15; DECIDED ids are listed under `decided`, remaining open ids under `unresolved` — see docs/OPEN_QUESTIONS.md ratification record.",
  "parity_baseline_status": "UNVERIFIED",
  "status_vocabulary": {"implementation_status":["PLANNED","IN_PROGRESS","IMPLEMENTED","VERIFIED"],"verification_status":["UNVERIFIED","FAIL","BLOCKED","NOT_APPLICABLE","VERIFIED_AT_SHA"],"merge_status":["NOT_STARTED","READY_FOR_REVIEW","MERGED"],"release_status":["NOT_RELEASED","RELEASED"]},
  "source_kinds": {"explicit_user_requirement":"stated by the owner in the charter/prompt","chevereto_parity":"audited Chevereto Free/Lite/Pro capability (reference_edition = lowest edition that has it)","flickr_workflow":"Flickr-like community workflow clarified from official Flickr docs; Vizra's own design","requested_integration":"S3/AWS/Backblaze, ActivityPub, AT Protocol, IPFS","recommended_safeguard":"engineering/privacy/quality safeguard from AGENTS.md, DoD, release acceptance","operator_requirement":"install/operate/recover obligations","meta_repo_parity_with_vidra":"mechanism mirrored from the Vidra meta repo by owner direction"},
  "summary": {"total": len(reqs), "core_profile": core_n, "full_profile": len(reqs), "by_area": dict(sorted(by_area.items())), "by_source_kind": dict(sorted(by_kind.items())), "open_questions_referenced": unresolved, "decided_questions_referenced": decided, "by_implementation_status": dict(sorted(collections.Counter(r["implementation_status"] for r in reqs).items())), "by_verification_status": dict(sorted(collections.Counter(r["verification_status"] for r in reqs).items()))},
  "features": reqs,
}
# encoding is explicit on purpose. With ensure_ascii=False the output carries
# non-ASCII characters (§ ° × – — … ← → ↔ ≤ ≥), and a bare open(..., "w") encodes
# them with locale.getpreferredencoding(False). That is UTF-8 on macOS and on a
# C.UTF-8 runner, but ASCII under a POSIX/C locale, where this line would raise
# UnicodeEncodeError instead of writing the ledger. A generated file must not
# depend on the ambient locale of whoever regenerates it. Output bytes are
# unchanged; only the guarantee is new.
with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
print(f"OK {len(reqs)} requirements; core={core_n}; areas={dict(by_area)}; questions={unresolved}; decided={decided}; statuses={out['summary']['by_implementation_status']}")
