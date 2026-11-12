# Independent verification — meta PR #19, first ledger status record (VZ-FOUND-002 IMPLEMENTED)

- Subject: https://github.com/yegamble/vizra/pull/19
- SHA verified: `4eb6249447502d4aaee9aa2702df8ed7c4d1360c` (PR head at start: same, OPEN; at end: `4eb6249447502d4aaee9aa2702df8ed7c4d1360c`)
- Date: 2026-11-12. Environment: macOS (darwin 25.5.0), Python 3.9.6, go1.26.2, node v19.9.0, gh with the owner's token. Fresh clones in a mktemp scratch dir (meta at the SHA; vizra-core main 58d658f; vizra-user main 53a39a8), deleted by exact path at the end.
- The verifier wrote no code under review and changed nothing but this file.

## Commands

| # | Command | Exit | Result |
|---|---|---|---|
| A1 | `git diff --name-only origin/main...HEAD` | 0 | exactly status_records.json and docs/quality/features.json |
| A2 | `git diff origin/main...HEAD -- docs/quality/features.json` | 0 | 2 hunks: summary counts (PLANNED 192 -> IMPLEMENTED 1 / PLANNED 191) and the VZ-FOUND-002 entry (implementation_status IMPLEMENTED, merge_status MERGED, evidence[]); verification_status UNVERIFIED and release_status NOT_RELEASED unchanged |
| B1 | `python3 build.py ../../quality/features.json` | 0 | statuses={'IMPLEMENTED': 1, 'PLANNED': 191}; `git status --porcelain` empty |
| B2 | `python3 scripts/check-ledger-status-output.py` | 0 | 192 entries, 1 record, sets equal |
| B3 | `python3 scripts/check-ledger-status-remote.py` | 0 | 1 status record proved against GitHub |
| B4 | `bash scripts/check-generated-ledger.sh` | 0 | byte-for-byte, both locales |
| B5 | `python3 -m unittest discover -s docs/evidence/ledger-generator -p 'test_*.py'` | 0 | OK |
| B6 | `python3 scripts/check-quality-json.py` | 0 | |
| B7 | `python3 scripts/check-doc-links.py` | 0 | porcelain still empty |
| C1 | `gh pr view 18 -R yegamble/vizra-core` | 0 | MERGED, head b1c1734f583a46f7abc295dcc55094f9d3f5717e, merge 58d658f128ed7dc4be7a218ae0cd5744b87d0601; compare merge...main = identical |
| C2 | `gh pr view 12 -R yegamble/vizra-user` | 0 | MERGED, head a3b8f942d566513b155971384bd2ee6b161d4520, merge 53a39a889ba0f456bbfdd4df7d5f241c12e7a1b5; compare = identical |
| C3 | `gh api .../commits/<head>/check-runs` | 0 | ci-required success on b1c1734 (build-test success; image-scan failure, not required) and on a3b8f94 (contract, frontend, e2e success; deps-scan and image-scan failure, not required) |
| C4 | final lines of the verifier evidence | 0 | user #12: `FINAL VERDICT: PASS — SHA a3b8f942…` (on origin/main). core #18 round 3: `FINAL VERDICT: PASS — SHA b1c1734f…` (read in the meta-records-1110 worktree; NOT on meta main) |
| D1 | core: `go test -count=1 ./internal/httpapi/` | 0 | ok |
| D2 | core mutation: `e.GET("/plainz", s.handleSchemaz)` | 1 | TestEveryRouteHasASpecOperation names GET /plainz (and the claim-classification test) |
| D3 | core mutation: `e.GET("/files/*", …)` + `claimGuardedRoutes = {"GET /files/*": true}` | 1 | TestEveryRouteHasASpecOperation names GET /files/{path} |
| D4 | core mutation: spec path /mutantz (copy of /version) with no route | 1 | TestEverySpecOperationHasARoute names GET /mutantz |
| D5 | core restored, `go test` | 0 | porcelain empty |
| D6 | user: sha256 of contracts/vizra-core/api/openapi.yaml vs core main api/openapi.yaml | 0 | both 2ac3280056871c48477b0238a398dc23afbd3afec5ff0ad170b27c5cc373c1d6 |
| D7 | user: `npm ci`; `npm run check:contract` | 0 / 0 | clean, no diff |
| D8 | user mutation: lib/api/generated.ts line 173 string -> number; `npm run check:contract` | 1 | "first difference at line 173 … generated, never hand-edited"; restored -> 0 |
| E1 | `grep -n VZ-FOUND-002 docs/issues/*.md` | 0 | only VZ-ISSUE-001.md; lines 17-19 are the three cited bullets verbatim |
| G1 | `gh api repos/yegamble/vizra/commits/4eb6249…/check-runs` | 0 | **ci-required: failure; validate: failure** (head_sha = the PR head); GitGuardian success |
| G2 | `gh run view 43210473134 --log-failed` | 0 | step "every ledger-status guard still fails against a controlled mutation": `demo: 60 passed, 1 failed` |

## Results per claim

- A scope: HOLDS.
- B mechanical: HOLDS locally (all seven exit 0, no diff).
- C GitHub facts: HOLD. Note the core #18 round-3 evidence is not yet on meta main.
- D judgement: IMPLEMENTED is honest (below).
- E acceptance floor: HOLDS.
- G CI on the exact SHA: **DOES NOT HOLD** — completed, red.

## Route / spec set comparison (vizra-core main 58d658f)

Routes from `testServer(t).Routes()` (throwaway test, removed) and path+method pairs parsed from api/openapi.yaml are the same six:

| Operation | Router | Spec |
|---|---|---|
| GET /healthz | yes | yes |
| GET /readyz | yes | yes |
| GET /version | yes | yes |
| GET /schemaz | yes | yes |
| GET /api/v1/setup/claim-status | yes | yes |
| POST /api/v1/setup/claim-owner | yes | yes |

Other HTTP surfaces: grep of non-test Go for route registration, ServeMux, pprof, promhttp, Static/File finds routes only in internal/httpapi/server.go:171-180. cmd/api/main.go:146 serves promhttp on its own listener (cfg.MetricsAddr), not the API listener; cmd/worker/main.go:91 is the worker's metrics mux. No pprof, no static, no second router on the API listener. I agree the metrics listeners are outside "defines every route" (not public API routes). The record names only the worker's mux; the API process's own metrics listener is equally unwalked and is not mentioned (FOLLOW-UP wording).

Required lanes: core .github/required-checks.txt lists build-test, which runs `make ci` (includes openapi-verify) and `go test ./...`. vizra-user required-checks.txt lists contract; contract-ci.yml triggers on every pull_request with no path filter.

## D — is IMPLEMENTED honest?

Yes. S1, S2 and N1 were each reproduced by my own run on the component mains today; nothing in the outcome or the three cases is undelivered. Rationale sentence by sentence: cases delivered and reproduced — true; core #18 wildcard walk and both-direction red — reproduced (D2-D4); user #12 vendored at core 5f615d7 — matches contracts/manifest.json source_commit; hand edit rejected — reproduced (D8); "not VERIFIED because evidence_required wants CI job output and every red run is verifier-local" — true, mine are local too; known limits — truthful, slightly incomplete (API metrics listener). The "exact six-operation test" in vizra-user was not separately inspected (NOT RUN).

Dependency VZ-FOUND-001 still PLANNED: status.py has no rule on dependency order (grep 'depend' in status.py: see below) and AGENTS.md's "dependency-ready" governs the work unit, not the record. Not forbidden: FOLLOW-UP.

## Findings

| ID | Severity | Finding | Reproducer |
|---|---|---|---|
| F1 | **BLOCKING** (G; required gate red on the exact SHA) | `validate` fails, so `ci-required` fails. docs/evidence/ledger-status/demo.sh case D11 expects the output check to say "…but the features count {'PLANNED': 192}", a string that is only true while status_records.json is empty. With the first real record the guard still goes red (exit 1) but says "{'IMPLEMENTED': 1, 'PLANNED': 191}", so the demo counts it as a failure: 60 passed, 1 failed. The record itself is not wrong; the demo's expectation is stale. | `gh run view 43210473134 -R yegamble/vizra --log-failed`, or `bash docs/evidence/ledger-status/demo.sh` at 4eb6249 (local run NOT RUN by me; the CI log is the evidence). Fix needs a change to demo.sh (a checker: its own PR and independent review), which is outside this PR's two-file scope. |
| F2 | FOLLOW-UP | core #18 round-3 evidence is not on meta main; an IMPLEMENTED record does not cite evidence files, but a later VERIFIED will need it merged first. | `git show origin/main:docs/evidence/warroom/2026-11-12-vizra-core-pr18-3a-round3-VERIFY.md` fails |
| F3 | FOLLOW-UP | Rationale's known limits omit the API process's own metrics listener (cmd/api/main.go:146). | grep above |
| F4 | FOLLOW-UP | No rule orders a record after its dependency (VZ-FOUND-001 PLANNED). | grep status.py |
| F5 | FOLLOW-UP | manifest source_commit is 5f615d7 while core main is 58d658f; bytes are identical today, no CI compares them (already recorded). | D6 |

## Not run

- demo.sh locally; the vizra-user six-operation test read; FOLLOWUPS.md wording check beyond a grep; no CI re-run (forbidden).

FINAL VERDICT: FAIL — SHA 4eb6249447502d4aaee9aa2702df8ed7c4d1360c
