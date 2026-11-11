# Independent verification: yegamble/vizra PR 15 (audit of VZ-FOUND-002, -003, -006)

Verifier: vizra-verifier (did not write the PR). Date 2026-11-10.

- Subject SHA: `857b791c18bf6b967c832cb2d579b51258192957` (PR head at start: same; at end: `857b791c18bf6b967c832cb2d579b51258192957`; PR OPEN)
- Merge base with `origin/main`: `e5a571582ee2c773f1138be65c40e07c309403e9`. `origin/main` has since moved to `8680fb4846cbb974e8ad81adcfdc117d576d4b65`.
- Component SHAs used (the ones the audit names): vizra-core `27cee5417ac51dad041e6f311ba4ca238246563e`, vizra-user `783483f3c5f207d3370e6f1a79766f840e36472f`.
  vizra-core `main` is now `ce805b465080a890d102b24b1f5eefa549084f1a`: the audit's core SHA is no longer `main`. vizra-user `main` is unchanged.
- Environment: darwin/arm64, go1.27.1, fresh clones in a private `mktemp -d` scratch directory (deleted at the end). No Docker, no database, no npm install.

## Commands and exit codes

| # | Command (in scratch) | Exit | Result |
|---|---|---|---|
| 1 | meta: `git diff --name-only origin/main...HEAD` | 0 | exactly the 3 files (AUDIT, VZ-ISSUE-001, plan) |
| 2 | meta: `git diff origin/main...HEAD -- docs/quality docs/evidence/ledger-generator \| wc -l` | 0 | 0 lines |
| 3 | core baseline: `go test ./internal/httpapi/ -run TestEvery -count=1` | 0 | ok |
| 4 | core M1: add `e.GET("/files/*", ...)` in internal/httpapi/server.go, no spec entry; `go test ./internal/httpapi/ -run 'TestEveryRouteHasASpecOperation\|TestEverySpecOperationHasARoute' -v` | 0 | both PASS: wildcard route is invisible to the contract test |
| 5 | core M1 + full package `go test ./internal/httpapi/` | 1 | only `TestEveryRouteIsEitherUnclaimedAllowlistedOrGuarded` fails (claim classification, not the contract) |
| 6 | core M1c: M1 plus `claimGuardedRoutes = {"GET /files/*": true}`; `go test ./internal/httpapi/ -count=1` | 0 | whole package green with an undocumented wildcard route |
| 7 | core control: add `e.GET("/zzmut", ...)`, no spec | 1 | `TestEveryRouteHasASpecOperation`: "serves 1 route(s) that api/openapi.yaml does not describe: GET /zzmut" |
| 8 | core H1: add `/zzspeconly` get to api/openapi.yaml, no route | 1 | `TestEverySpecOperationHasARoute`: "describes 1 operation(s) cmd/api does not serve: GET /zzspeconly" |
| 9 | core baseline `./scripts/migrate-lint.sh` | 0 | passed |
| 10 | core M2 control: new 0006_zz_mut.up.sql `ALTER TABLE sites DROP COLUMN handle;` (+ down file, manifest regenerated) | 1 | "0006_zz_mut.up.sql:1 destructive statement in an up migration" |
| 11 | core M2a: same with `ALTER TABLE sites DROP handle;` | 0 | "migrate-lint: passed" |
| 12 | core M2b: same with `DROP` and `COLUMN handle;` on two lines | 0 | "migrate-lint: passed" |
| 13 | core: `grep -rn OWNER_CLAIM --include=*.go .` | 0 | internal/config/config.go:260-261 read VIZRA_OWNER_CLAIM_TTL and VIZRA_OWNER_CLAIM_ANNOUNCE; keys.go:71-72 declare them |
| 14 | meta at SHA: `grep -rn OWNER_CLAIM --exclude-dir=.git . \| grep -v '^./docs'` | 1 | no match: neither key is in any compose file or env template |
| 15 | operations in vizra-user contracts/vizra-core/api/openapi.yaml vs core api/openapi.yaml | 0 | vendored 4, core 6; missing: GET /api/v1/setup/claim-status, POST /api/v1/setup/claim-owner |
| 16 | core H2: append a comment to generated file `internal/store/sqlcgen/sites.sql.go`; `make sqlc-verify` | see result | base=0  } -// hand edit make: *** [sqlc-verify] Error 1 mut=2  |
| 17 | meta: `python3 scripts/check-doc-links.py` | 0 | |
| 18 | meta: `python3 scripts/check-quality-json.py` | 0 | |
| 19 | meta: `bash scripts/check-generated-ledger.sh` | 0 | |
| 20 | meta: `python3 scripts/warroom-check.py board` | 0 | |
| 21 | `gh pr checks 15 -R yegamble/vizra` | 0 | ci-required pass, validate pass, GitGuardian pass; run 42883100985 head_sha/conclusion: 857b791c18bf6b967c832cb2d579b51258192957 success |

After every mutation the file was restored from a saved copy and `git status --short` was empty.

## Result per claim

| Claim | Result |
|---|---|
| A scope | PASS. Three files against the merge base; features.json and status_records.json untouched. (A two-dot diff against today's `origin/main` lists 7 files only because main moved after the branch was cut.) |
| B acceptance target | PASS. Five lines changed, each differs from the old line only by an added `(VZ-FOUND-00N) ` prefix; no bullet added, removed or reworded. Tags checked against features.json: 001 repositories exist; 004 pinned versions and licences (ADR-001); 002 route/spec drift both directions; 003 sqlc output drift check (a listed negative case of 003); 006 production boot refuses dev secrets (a listed negative case of 006). All five match. |
| C audit file | PASS. No line starts with `FINAL VERDICT`; line 3 says "This is a builder's claim, not a verdict"; the SHA table records meta, core, user and search SHAs. |
| D reproduction | PASS. All four DOES NOT HOLD results reproduced (rows 4-6, 11-12, 13-14, 15). HOLDS reproduced: route without spec fails (row 7), spec without route fails (row 8), literal DROP COLUMN fails migrate-lint (row 10), hand-edited sqlc output (row 16). No audit claim was found to overstate what holds. |
| E meta checks | PASS, four of four exit 0. |
| F CI | PASS. ci-required success on the exact SHA. |
| G secrets | PASS. Pattern scan of added lines (tokens, private keys, JWTs, secret/password assignments) found nothing; the hex strings are commit SHAs and sha256 digests. GitGuardian passed. |

## Findings

| # | Class | Finding |
|---|---|---|
| 1 | FOLLOW-UP | The audit's vizra-core SHA (27cee54) is no longer `main` (now ce805b4). The audit is accurate for the SHA it names; whoever slices from it should re-check against current main. |
| 2 | FOLLOW-UP | Each tagged bullet in VZ-ISSUE-001 proves one case of its id, not the whole id (for example the 003 bullet covers sqlc drift, not migrate-lint or migrate up; the 006 bullet covers boot refusal, not key coverage or the log denylist). The tags are right, but the chair must not read a demonstrated bullet as the id being complete. |
| 3 | FOLLOW-UP | Audit detail for D1: an unclassified wildcard route is caught by a different test (claim classification, setup_test.go:47), so the gap needs the route to be classified as well. The audit's conclusion stands (row 6). |

No BLOCKING finding.

## Per-id answer for the chair

None of the three can honestly be recorded IMPLEMENTED or VERIFIED today.

- **VZ-FOUND-002: no.** (a) vizra-core internal/httpapi/openapi_contract_test.go:89 drops every route whose path contains `*`, so "route without spec fails" is false for wildcard routes (rows 4-6). (b) vizra-user's vendored contract is two operations behind core (row 15), so the generated client is drift-checked against a stale contract, not against core.
- **VZ-FOUND-003: no.** vizra-core scripts/migrate-lint.sh:92 matches `DROP\s+COLUMN` line by line: `ALTER TABLE x DROP handle;` and a DROP/COLUMN split over two lines both pass (rows 11-12). Not reproduced by me but claimed by the audit: no lane runs `migrate up` from the release image, no test for the dirty-ledger case, no compatibility window in the rule.
- **VZ-FOUND-006: no.** VIZRA_OWNER_CLAIM_ANNOUNCE and VIZRA_OWNER_CLAIM_TTL are read by config.Load (core internal/config/config.go:260-261) and appear nowhere in the meta repo's compose files or env templates (row 14), so "every key reaches api and worker" is false and the meta coverage check did not catch it (meta CI is green). Claimed by the audit, not reproduced: `vizra setup` does not exist.

### Defects as slices

| Repo | File | What is wrong | Reproducer |
|---|---|---|---|
| vizra-core | internal/httpapi/openapi_contract_test.go:89 | skips all paths containing `*` instead of only Echo's automatic not-found entry | add `e.GET("/files/*", s.handleSchemaz)` in server.go and `"GET /files/*": true` to claimGuardedRoutes in setup.go; `go test ./internal/httpapi/` exits 0 |
| vizra-core | scripts/migrate-lint.sh:92 | destructive regex needs the COLUMN keyword and works per line | new migrations/0006_x.up.sql with `ALTER TABLE sites DROP handle;` (or DROP and COLUMN on separate lines), a down file, regenerate manifest; `./scripts/migrate-lint.sh` exits 0 |
| vizra (meta) | compose files, env/*.env.example, scripts/check-config-coverage.py | two keys read by config.Load are not delivered to api/worker and the coverage check stays green | `grep -rn OWNER_CLAIM . --exclude-dir=.git --exclude-dir=docs` exits 1 while core internal/config/keys.go:71-72 declares both |
| vizra-user | contracts/vizra-core/api/openapi.yaml and generated client | vendored contract lacks GET /api/v1/setup/claim-status and POST /api/v1/setup/claim-owner | compare operations with vizra-core api/openapi.yaml at 27cee54: 4 against 6 |

## Not run

- vizra-user `npm run check:contract` and the hand-edited generated client mutation (no npm install in the time available).
- `migrate up` on an empty database, dirty-ledger behaviour, production boot refusal, log denylist tests, rendered-compose key count (22 of 24), vizra-search.
- Docker image build.

FINAL VERDICT: PASS — SHA 857b791c18bf6b967c832cb2d579b51258192957
