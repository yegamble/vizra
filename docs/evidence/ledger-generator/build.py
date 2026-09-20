import json, sys, importlib, collections
import core
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
    if r["implementation_status"]!="PLANNED" or r["verification_status"]!="UNVERIFIED": errors.append(f"{r['id']}: status must be PLANNED/UNVERIFIED")
    if not r["cases"]["success"]: errors.append(f"{r['id']}: no success case")
    if not r["evidence_required"]: errors.append(f"{r['id']}: no evidence_required")
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
  "schema_version": 3,
  "generated": "2026-09-15",
  "notice": "Atomic requirement ledger produced by Prompt 00 on 2026-09-15. Every entry is PLANNED/UNVERIFIED. No entry may be marked IMPLEMENTED or VERIFIED without recorded evidence (commands, exit codes, counts, SHA, artifacts). Removing or narrowing an entry requires an owner decision recorded in docs/OPEN_QUESTIONS.md. Open questions ratified 2026-09-15; DECIDED ids are listed under `decided`, remaining open ids under `unresolved` — see docs/OPEN_QUESTIONS.md ratification record.",
  "parity_baseline_status": "UNVERIFIED",
  "status_vocabulary": {"implementation_status":["PLANNED","IN_PROGRESS","IMPLEMENTED","VERIFIED"],"verification_status":["UNVERIFIED","FAIL","BLOCKED","NOT_APPLICABLE","VERIFIED_AT_SHA"],"merge_status":["NOT_STARTED","READY_FOR_REVIEW","MERGED"],"release_status":["NOT_RELEASED","RELEASED"]},
  "source_kinds": {"explicit_user_requirement":"stated by the owner in the charter/prompt","chevereto_parity":"audited Chevereto Free/Lite/Pro capability (reference_edition = lowest edition that has it)","flickr_workflow":"Flickr-like community workflow clarified from official Flickr docs; Vizra's own design","requested_integration":"S3/AWS/Backblaze, ActivityPub, AT Protocol, IPFS","recommended_safeguard":"engineering/privacy/quality safeguard from AGENTS.md, DoD, release acceptance","operator_requirement":"install/operate/recover obligations","meta_repo_parity_with_vidra":"mechanism mirrored from the Vidra meta repo by owner direction"},
  "summary": {"total": len(reqs), "core_profile": core_n, "full_profile": len(reqs), "by_area": dict(sorted(by_area.items())), "by_source_kind": dict(sorted(by_kind.items())), "open_questions_referenced": unresolved, "decided_questions_referenced": decided},
  "features": reqs,
}
json.dump(out, open(sys.argv[1],"w"), indent=2, ensure_ascii=False)
print(f"OK {len(reqs)} requirements; core={core_n}; areas={dict(by_area)}; questions={unresolved}; decided={decided}")
