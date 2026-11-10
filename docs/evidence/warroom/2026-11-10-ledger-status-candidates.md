# Ledger status candidates, 2026-11-10: none recordable

Chair's record of plan step 18. A helper tried each candidate record in a scratch clone of meta `main` `27be92a` (component mains: core `27cee54`, user `783483f`, search `4810048`), with `python3 build.py` (offline half) and `python3 scripts/check-ledger-status-remote.py --records <file>` (online half), and read each component's `main` from a shallow clone. Nothing was built or run beyond those two checkers. No checker, issue file or evidence file was changed. This record was not independently verified.

**Result: `status_records.json` stays `"records": []`. All 192 entries stay PLANNED / UNVERIFIED.** Seven candidates pass both mechanical halves; each was withheld because the merged work is narrower than the ledger outcome, the same judgement as [2026-09-23](../ledger-status/README.md).

| ID | Offline / online | Why not recorded | What would make it recordable |
|---|---|---|---|
| VZ-FOUND-001 | exit 1 / 0 | no VZ-ISSUE-001 bullet names it; no `bootstrap.sh` in any repo | the script; a bullet naming the id; an evidence file ending in a verdict line |
| VZ-FOUND-002 | exit 1 / 0 | no bullet names it; "every route" not audited | bullet; audit; verdict-line evidence |
| VZ-FOUND-003 | exit 1 / 0 | no bullet names it; compatibility-window rule not audited | the same |
| VZ-FOUND-004 | exit 1 / 0 | no libvips binding in core `go.mod`; no Lucide in user `package.json` | both pins |
| VZ-FOUND-005 | exit 1 / 0 | `internal/httpapi/probes.go` has no storage check in readiness | storage check in `/readyz` with a failing-storage test |
| VZ-FOUND-006 | exit 1 / 0 | no bullet names it; coverage not audited | bullet; audit; verdict-line evidence |
| VZ-FOUND-007 | exit 1 / 0 | VZ-ISSUE-006 also schedules it and is unbuilt; only the twelve M0 fixtures exist | ICC wide-gamut, video and 360 fixtures (M1) |
| VZ-FOUND-008 | exit 0 / 0 | no axe dependency; the harness has no real API, PostgreSQL or Redis (`playwright.config.ts:153`) | harness boots the stack; axe runs |
| VZ-INSTALL-003 | exit 1 / 0 | no `/setup/claim` page in vizra-user | the claim page (M1) |
| VZ-TOPOLOGY-001 | exit 0 / 0 | no `install.sh` or `compose.sh`; the lane has never started a container | installer and boot lane |
| VZ-TOPOLOGY-002 | exit 0 / 0 | no live external-PostgreSQL run, no unreachable-DSN `/readyz` test, no backup runbook | boot lane with the external shape |
| VZ-TOPOLOGY-003 | exit 0 / 0 | `SEARCH_REDIS_URL` deferred past M0; no Redis fault-injection run | the same, with fault injection |
| VZ-CI-001 | exit 0 / 0 (IMPLEMENTED) | no tombstone rule in any guard; vizra-user marks two lanes "required only if it ran"; VERIFIED closed (no verdict line) | tombstone rule in four guards; fix the optional lanes; fresh evidence |
| VZ-CI-002 | exit 0 / 0 | no wizard-answer coverage; `bundle` not built | VZ-INSTALL-002 and the bundle lane |
| VZ-CI-004 | exit 0 / 0 (IMPLEMENTED) | image and dependency scans are deliberately outside the required manifests; no publish-time scan; no secret-scan lane; core `image-scan` red | scans required and green (needs inbox 9) |
| VZ-AUDIT-001 | exit 1 / 0 | no issue schedules it; nothing built | M2 work |

Merges tried (verified head → merge commit): core #1 `b5f8f6aa` → `415a6d19`; user #1 `97670154` → `752253cb`; search #1 `ab41219b` → `581d79dc`; core #5 `56920fec` → `c043df72`; user #3 `3b566c3b` → `f49bca46`; user #8 `c2ff4454` → `7a3a572b`; core #8 `0cc906ed` → `f1972e82`; meta #4 `8e2a8674` → `b2c5b96c`; meta #2 `736488ec` → `6b8158c3`; user #2 `6b0ba871` → `1a952b50`.

Two mechanical blockers repeat and are cheap to remove: VZ-ISSUE-001 tags only its -007 and -008 bullets with an id, so no record for -001 to -006 can cite a bullet; and the September evidence files for core #1, user #1, search #1, core #5, user #3 and meta #2 do not end in a `FINAL VERDICT` line.

Not checked: FOUND-002, -003 and -006 beyond the presence of their make targets and files; the with-record lane run (there was no record to put in place); the helper wrote this table before the rulesets on vizra, vizra-user and vizra-search were read back, so its note that `ci-required` is "not actually required" is out of date for those three.
