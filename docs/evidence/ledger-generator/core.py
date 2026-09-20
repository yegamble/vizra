"""Ledger DSL. Each requirement is one dict; sections append to REQS."""
REQS = []
SEEN = set()

def req(id, title, outcome, area, kind, provenance, profiles=("core","full"), deps=(),
        success=(), negative=(), privacy=(), recovery=(), api=(), ui=(), cli=(),
        evidence=(), edition=None, mechanism=None, unresolved=(), decided=(), notes=None):
    assert id not in SEEN, f"duplicate id {id}"
    SEEN.add(id)
    REQS.append({
        "id": id,
        "title": title,
        "area": area,
        "outcome": outcome,
        "source_kind": kind,
        "provenance": list(provenance),
        "reference_edition": edition,
        "profiles": list(profiles),
        "dependencies": list(deps),
        "cases": {
            "success": list(success),
            "negative": list(negative),
            "privacy": list(privacy),
            "recovery": list(recovery),
        },
        "surfaces": {"api": list(api), "ui": list(ui), "cli": list(cli)},
        "evidence_required": list(evidence),
        "competitor_mechanism_vs_equivalent": mechanism,
        "unresolved": list(unresolved),
        "decided": list(decided),
        "notes": notes,
        "implementation_status": "PLANNED",
        "verification_status": "UNVERIFIED",
        "merge_status": "NOT_STARTED",
        "release_status": "NOT_RELEASED",
        "test_ids": [],
        "evidence": [],
    })

# source_kind vocabulary
EXPLICIT = "explicit_user_requirement"
CHEV = "chevereto_parity"
FLICKR = "flickr_workflow"
INTEG = "requested_integration"
SAFE = "recommended_safeguard"
OPS = "operator_requirement"
META = "meta_repo_parity_with_vidra"

# common evidence bundles
EV_API = ["integration test on real PostgreSQL/Redis with exit code and counts", "OpenAPI operation present and drift-checked"]
EV_UI = ["production-build browser test with desktop+mobile screenshots and console/network error capture", "control row in docs/quality/ui-controls.json"]
EV_NEG = ["negative/permission test that fails against a controlled mutation"]
EV_OPS = ["command transcript with exit code on the declared clean target", "rendered compose model assertion"]
