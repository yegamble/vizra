# Sentinel PR review: yegamble/vizra-core #14 at `75e0a95`

- PR: "fix(ownerclaim): M1-A sentinel follow-ups S-0002..S-0007, S-0009, S-0010 (queue 2t)"
- Head `75e0a9510dcb92f3b7b9b880bbadb17960ffa18d`, base `main` `a6bc77dda973c42ac79360b0b5afd03e7aa59604`. The head SHA was confirmed at the start and again at the end (see "Head check").
- Reviewer: the PR sentinel. It ran alongside the independent verifier and does not replace it. `post: no`, so nothing was posted.
- Environment: darwin/arm64 and go1.27.1. The containers were `sent14pr-pg` (the CI digest of postgres, 18.6) and `sent14pr-vk` (the CI digest of valkey, 9.1.2). Both were started with `--rm` and removed with `-v` at the end. The clones are fresh in a `mktemp -d` scratch directory: `core` is the PR head, `head2` is a worktree of the head, `base` is a worktree of `a6bc77d`, and `vizra`, `vizra-user` and `vizra-search` are clones of main at `e4f625e`, `783483f` and `4810048`.

## Counts

| | n |
|---|---|
| Findings | 4 (MINOR 3, NIT 1) |
| Questions | 4 |
| Blast-radius dependents examined | 24 |
| Not run | 2 |

## Blast radius

| Changed thing | Dependents found | Result |
|---|---|---|
| Migration `0006` CHECK on `audit_events` (new constraint) | (1) the base binary, which is still serving during a deploy (`ownerclaim.Claim` in base writes `after` without `token_generation`); (2) the planned VZ-AUDIT-001 anonymisation path (meta `docs/quality/features.json:3185`), an UPDATE of `after` in rows that name a user; (3) `pg_dump`/`pg_restore` (backup and restore, VZ-ISSUE-010); (4) `migrate-lint` (`scripts/migrate-lint.sh:88`); (5) ADR-002's N-1 lanes (meta ADR-002:78); (6) the head's own `mapClaimError` 23514 branch | (1) **F-1**; (2) **F-3**; (3) OK: restore exit 0, and the constraint comes back `convalidated=f`; (4) passes, because it does not see the class (F-1); (5) no such lane exists in core CI (no `N-1` match in `.github`, `Makefile` or `scripts`); (6) part of F-1 |
| The `after` shape of the `succeeded` row (new key `token_generation`) | readers of `after` in core, CLI, doctor and admin, and in meta, user and search | none. There is no audit read surface yet. `cmd/vizra/doctor.go:153` reads `AnyUserExists` and `ownerclaim.State`, never `audit_events` |
| The `after.bucket` of a `rate_limited` row (`failure` becomes `per_origin`/`global`/`ceiling.claim`/`ceiling.status`) and the rate-limit marker key (`…:audited` becomes `…:audited:<bucket>`) | readers of `bucket` in all four repos; the AGENTS.md row; the mutation harness | there are no code readers. The AGENTS row is updated. The harness cases keyed on the old shape no longer apply (**F-2**) |
| `decodeClaimOwnerRequest` (strict keys, trailing bytes) | senders of the claim body: vizra-user (its vendored contract `contracts/vizra-core/api/openapi.yaml` is at core `415a6d1`, which **predates** `/setup/claim-owner`; `lib/api/generated.ts` has no claim type; the repo has no `claim` string outside a CI script); meta design and ledger docs (these reference the route only); core's own tests; the harness MUT-25 | there is no cross-repo sender, so nothing breaks. A differential of old against new over 17 bodies differs only on `null`, `{"Token":…}`, `{…}}` and `{…}]`, all intended; duplicate keys and `null` members decode identically. Harness MUT-25 no longer applies (F-2) |
| `errorHandler` (global, `middleware.go:170`) now skips the ERROR line when the request context has ended | every route in `internal/httpapi`: probes, search, setup, and the 404 path | **F-4** (NIT) |
| `s.unavailable` (`setup.go:565`) skips logging when the request context has ended, and is now used by the unclaimed guard, claim-status and poolFor | the guard covers every non-allowlisted route while unclaimed | covered by the PR's tests; see Q-2 |
| `ownerclaim.unavailable` now uses `%w` twice | callers that use `errors.Is(err, ErrUnavailable)`: `mapClaimError`, doctor and CLI | OK. `errors.Is` still matches `ErrUnavailable` (the PR's test and harness MUT-28 pass) |
| `MintOwnerClaimToken` `DO UPDATE … WHERE consumed_at IS NULL` | `Mint` (via `vizra claim-token`, `cmd/vizra/claimtoken.go:49`, and `Boot`, `announce.go:88`); the sqlc generated copy and the querier doc; the harness MUT-1 and MUT-32 | OK. No-row still maps to `ErrHasUsers`, and the only path to a consumed row also creates a user, so no state is reached where users are absent but the row is consumed. MUT-1 and MUT-32 still apply and turn red |
| `VIZRA_OWNER_CLAIM_TTL` must be at least 1m | core `.env.example:97` (1h), `keys.go:72` (1h), README:110 (1h); every `config.Load` caller (api, worker, `vizra` CLI, doctor); meta compose and registry; vizra-user e2e | OK. No value below 1m exists anywhere. Meta does not carry the key at all (S-0008, known, not re-reported). No test overrides the TTL outside `internal/config` |
| `mapClaimError` 22021 branch | the log-site counter (`logsites_test.go`, 6 to 7); AGENTS.md "7 sites" | consistent |
| `scripts/test-floors.json` | `go-test-report.py` in `build-test.yml:245/305/322` and `pinned-steps.yml` | all floors are raised and none lowered (R11 OK) |
| AGENTS.md rows | the tests they cite; the MUT ids they cite (MUT-34, MUT-41) | MUT-34 and MUT-41 can no longer be demonstrated (F-2) |
| `docs/evidence/m1a-owner-claim/demonstrate.sh` (unchanged by the PR, but it patches the changed files) | 62 cases | 8 HARNESS-FAIL on the head against 1 on base (F-2) |

## Findings

### F-1: MINOR. Migration 0006 is not N-1 compatible. A claim served by the previous binary after 0006 is applied fails every time, answered as a misleading **400**

- The changed side:
  - `migrations/0006_audit_claim_succeeded_generation.up.sql:25-29` adds a CHECK. The base binary's `succeeded` insert (`ownerclaim.go`, base `After: {username, role}`) violates it.
  - The head's `internal/httpapi/setup.go:516` still maps **every** 23514 to `400 bad_request "one of the submitted values is not acceptable"`, whatever the constraint. A server-side audit-shape defect is therefore reported to the operator as bad input.
- The dependent side:
  - The base binary serves in the deploy window. ADR-002 orders the deploy as core migrate, then `up -d`. The running api container is replaced only after `migrate` completes, and meta `docker-compose.yml:242-245` makes the new api wait on migrate. On a split host, where meta `docker-compose.yml:283-286` already contemplates a worker-only host, the window lasts as long as the other host goes un-upgraded.
  - `scripts/migrate-lint.sh:88` says "Inside the compatibility window an up migration must be additive: a rolled-back deploy has to keep working against the new schema". The lint passes 0006 because its pattern cannot see a new constraint.
  - ADR-002:78 promises an "N-1-suite-against-N-schema lane", which would catch this. No such lane exists in core CI.
- Answer to the brief's question: **yes**. During the window, every claim that the old binary answers fails. The whole claim transaction rolls back: no user, and the token stays unconsumed and live. So the operator gets a 400 telling them their input is wrong, and retries fail the same way until the new api container serves. No failure budget is charged (the 23514 branch does not go through `refuseToken`). Once the new binary serves, the same token succeeds. Severity is MINOR: the endpoint succeeds once per instance lifetime, no release tag exists yet (`git tag` is empty), and nothing is corrupted. The class matters, because it is the first CHECK added to a table an older binary writes.
- Reproducer. These are real binaries against a real database. `bin/base-*` is built from `a6bc77d` and `bin/head-*` from `75e0a95`. The same database is migrated to 6 by the head CLI.

```
$ ./bin/head-vizra migrate            -> default APPLIED to version 6
$ ./bin/base-vizra doctor | grep schema
FAIL   schema   database at 6 is NEWER than this binary's 5: ... rolling this image out is refused
# base api still running (the deploy window); token minted by `vizra claim-token`
$ curl -X POST :18914/api/v1/setup/claim-owner -H 'Content-Type: application/json' -d '{"token":"<minted>","username":"owner1","email":"owner@example.org","password":"<inert passphrase>"}'
HTTP 400
{"error":{"code":"bad_request","message":"one of the submitted values is not acceptable",...}}
users|0   token consumed|0   succeeded rows|0
api log: level=ERROR msg="http: a CHECK constraint refused a request the validator accepted" constraint=audit_events_claim_succeeded_names_generation
# control 1: same DB, same token, HEAD api
HTTP 201 {"username":"owner1","role":"owner"}
setup.owner_claim.succeeded|{"role": "owner", "username": "owner1", "token_generation": 1}
# control 2: base api on a base (version 5) database
HTTP 201 {"username":"owner1","role":"owner"}
```

- The result is red on the head's schema with the N-1 binary, and green on base (N-1 binary with the N-1 schema) and on the head (N binary with the N schema).
- Smallest fix, one of the following:
  - (a) Expand/contract. Ship the writer (`token_generation`) in this release and add the CHECK in a later release, once no binary that omits the key can be serving.
  - (b) If the chair accepts the window, record it as an accepted residual in 0006's header and in the AGENTS row. In either case, narrow `mapClaimError`'s 23514 branch to the input constraints the validator mirrors (`users_email_shape`, `users_username_shape`, and the like). An `audit_events_*` 23514 is a server defect and should answer 500 (logged). It should not tell the operator their input is wrong. AGENTS.md:432 already calls 400 a "defect backstop" for "a CHECK the validator should have caught", and 0006 is not such a CHECK.

### F-2: MINOR (R11, R1). The M1-A mutation harness loses 7 more cases, including the two MUT ids AGENTS.md still cites as evidence

- The changed side:
  - `internal/httpapi/setup.go:212` and `:313`: the ceiling calls now take `bucketCeilingStatus`/`bucketCeilingClaim` constants, not the literals `"ceiling.status"`/`"ceiling.claim"`.
  - `setup.go:369`: `decodeClaimOwnerRequest` replaces the inline `DisallowUnknownFields` decoder.
  - `setup.go:385`: the poolFor 503 now goes through `s.unavailable`.
  - `setup_limits.go:193`: `claimLimitTransition(c, bucket)`.
- The dependent side: `docs/evidence/m1a-owner-claim/demonstrate.sh` cases MUT-11b (:174), MUT-25 (:204), MUT-15 (:212), MUT-33 (:272), MUT-34 (:276), MUT-39 (:294) and MUT-41 (:304). Their perl patterns match the base text only. The AGENTS.md row at :448 cites **MUT-34** and **MUT-41** as the proof that the claim-status ceiling exists and that the two routes do not share a bucket.
- Reproducer. The harness was run unmodified, with the real database and cache (the full transcript is in scratch):

```
# head 75e0a95, ./docs/evidence/m1a-owner-claim/demonstrate.sh
SUMMARY  passed: 54  failed: 0  harness-fail: 8   head exit=1
HARNESS-FAIL: MUT-11b MUT-25 MUT-15 MUT-33 MUT-34 MUT-39 MUT-41 MUT-44
# base a6bc77d, same harness, per case
MUT-11b/15/25/33/34/39/41: RED exit=1, GREEN exit=0  -> passed
MUT-44: HARNESS-FAIL (pre-existing on base; not this PR's)
```

  The full base run (`a6bc77d`, same harness) gave `passed: 61  failed: 0  harness-fail: 1` (MUT-44 only), `base exit=1`.
- The harness's digest gate works as designed: it scores nothing rather than reporting a pass. But the evidence that AGENTS.md points a reader at is no longer runnable. The PR body's own M1–M16 mutations are ad hoc, with no committed harness, so the 7 cases are replaced by nothing a verifier can re-run. The mutation classes they targeted still matter: a ceiling taken off claim-status, the ceilings collapsed into one bucket, an audit row per 429, and unknown fields allowed.
- Smallest fix: update the seven perl patterns to the new text. For example, MUT-34 and MUT-41 would match `allowSetupRequest(c, bucketCeilingStatus, …)`. MUT-25 would target the `claimOwnerFields[key]` refusal, MUT-39 and MUT-11b the `auditRateLimited` loop, MUT-15 the `s.unavailable(c, "resolving…")` block, and MUT-33 the `s.unavailable(c, "claim-status: …")` line. Then re-run to `harness-fail: 0`. MUT-44 is pre-existing and could be fixed at the same time.

### F-3: MINOR (R1, ledger dependent). 0006's "existing rows are not re-checked" holds only for the ALTER. Any later UPDATE of a pre-0006 `succeeded` row is refused, and that is exactly the shape VZ-AUDIT-001's planned anonymisation needs

- The changed side: the header of `migrations/0006_audit_claim_succeeded_generation.up.sql:15-20` ("existing rows are not re-checked … there is no correct way to 'fix' them"), and the AGENTS.md row at :439 ("rows written under 0005 are not re-checked; every row inserted since is").
- The dependent side: the meta ledger's VZ-AUDIT-001 success case (`docs/quality/features.json:3185`). Erasure "anonymises that user's username in the audit rows that name them" through a widened `audit_events_append_only()`. The owner's `succeeded` row carries `after.username`. On any database that claimed under 0005, that UPDATE now fails 23514. So does a future `VALIDATE CONSTRAINT`.
- Reproducer. The database claimed through the base binary at version 5, and the head then migrated it to 6. The anonymisation function is simulated inside a rolled-back transaction.

```
BEGIN; CREATE OR REPLACE FUNCTION audit_events_append_only() ... (allow UPDATE) ...;
UPDATE audit_events SET after = jsonb_set(after,'{username}','"erased-0001"') WHERE action='setup.owner_claim.succeeded';
ERROR:  new row for relation "audit_events" violates check constraint "audit_events_claim_succeeded_names_generation"
ROLLBACK;
ALTER TABLE audit_events VALIDATE CONSTRAINT audit_events_claim_succeeded_names_generation;
ERROR:  check constraint "..." of relation "audit_events" is violated by some row
-- control: identical UPDATE on a head-written row (has token_generation): UPDATE 1
```

- Impact today is limited to development databases, because there is no release. The dependent is a ledger plan, not yet code. The documented sentence is what is wrong.
- Smallest fix: state it in 0006's header and in the AGENTS row: "NOT VALID skips existing rows at ALTER time only. An UPDATE of a pre-0006 succeeded row is checked and refused." Add a note to VZ-AUDIT-001 in the meta ledger that the anonymisation must keep `after.token_generation`, or else handle pre-0006 rows. The alternative is to scope the CHECK to UPDATEs that keep the key, for example `OR after ? 'token_generation' IS NOT DISTINCT FROM …`, but the doc change is the smaller fix.

### F-4: NIT (R9 inverted). The global `errorHandler` now drops the ERROR line for **every** 5xx on **every** route whenever the request context has ended, including an unmapped 500 whose cause has nothing to do with cancellation

- The changed side: `internal/httpapi/middleware.go:170`, `if status >= 500 && c.Request().Context().Err() == nil`.
- The dependent side: every route served through `errorHandler`, not only setup. A request whose client or proxy gave up while a genuine defect was being returned leaves no trace. That happens when a reverse-proxy timeout closes the upstream connection, which cancels the Go request context. The AGENTS row at :436 describes the suppression only for the setup surface.
- Reproducer. The following is a throwaway test in `internal/httpapi`, removed after the run:

```go
ctx, cancel := context.WithCancel(context.Background()); cancel()
req := httptest.NewRequest(http.MethodGet, "/api/v1/anything", nil).WithContext(ctx)
errorHandler(logger)(e.NewContext(req, rec), errors.New("unmapped defect: invariant violated"))
// require "http: request failed" in the log
```

```
head 75e0a95: --- FAIL ... a 500 with a non-cancellation cause was NOT logged because the request context had ended; log=""
base a6bc77d: ok  github.com/yegamble/vizra-core/internal/httpapi 0.355s
```

- Smallest fix: suppress the line only when the error is itself the cancellation, that is `ctx.Err() != nil && errors.Is(err, context.Canceled)` (or `DeadlineExceeded` of the request context). Otherwise log it, at WARN if that is preferred. The same narrowing applies to `s.unavailable` at `setup.go:566`.

## Questions (not reproduced)

- **Q-1: an unclaimed instance under a sustained flood.** The per-window bound is now **4** `rate_limited` rows per 15 minutes (per_origin, global, ceiling.claim, ceiling.status) against 1 on base. That is 384 rows a day into the undeletable table for as long as an instance stays unclaimed and flooded. The PR's own argument for claimed instances, that "the per-window bound integrates to unbounded", applies to an instance that is installed and left unclaimed. Is that an accepted residual? It should be recorded in the AGENTS row if so. Not run as a long soak.
- **Q-2: suppressing the log on a hung database.** A database that hangs, rather than refusing connections, while a proxy times out first gives every setup request a cancelled context. Such a request is answered 503 and never logged, so the only outage signal is `/readyz`. Is that the intended diagnosability for "unclaimable instance, nothing in the log"? No proxy was run.
- **Q-3: marker keys during a rolling deploy.** The base and head binaries use different transition-marker keys (`…:audited` and `…:audited:<bucket>`). During a mixed-version window one window can therefore write one extra `rate_limited` row. This is bounded and harmless, and it is noted for completeness only. Not run.
- **Q-4: MUT-44.** MUT-44 was already HARNESS-FAIL on base. It is not this PR's, but should it be fixed in the same pass as F-2?

## Rules applied

| Rule | Applies? | Result |
|---|---|---|
| R1 false guarantees | yes | F-3 (0006 header and the AGENTS row); F-2 (AGENTS cites MUT-34 and MUT-41, which cannot run); the F-1 400 message |
| R2 CI step identification | no workflow change | n/a |
| R3 allowlist | yes, the decoder now allowlists the four keys | OK |
| R4 one reader | yes, one `json.Decoder` reads the body, then `Token()` | OK |
| R5 fail closed | yes, the harness digest gate fails closed | OK (F-2 is the rot it exposed) |
| R6 failure signal vs publish | no | n/a |
| R7 effective value | yes, the TTL bound is applied to the loaded value in `LoadFrom` | OK |
| R8 fixed windows | yes, per-bucket markers use `Allow` with the fixed window | OK |
| R9 cancelled context | yes | applied in the PR; F-4 is the over-broad inverse |
| R10 redact at sink | yes, the new 22021 log line and `s.unavailable` go through `obs.Redact` | OK |
| R11 tests can fail | yes | F-2; floors raised, none lowered |
| R12 cleanup | yes, for my own probes | the containers use `--rm` and were removed with `-v`; the throwaway tests were deleted |
| R13 one name per concept | yes, the bucket names | consistent in code and AGENTS |
| R14 public exposure | yes | nothing posted; no token or local path in this file beyond scratch-relative names |
| R15 pins | no pin change | n/a |
| R16 upsert resurrection | yes, the target of S-0002 | the fix holds (MUT-1 and MUT-32 still turn red) |
| R17 validator = constraint | yes | the email literal is now byte-equal; the 23514 mapping is too broad (F-1) |
| R18 `%w` | yes | OK |
| R19–R21 | no | n/a |

## Not run

- **An N-1 lane in a real compose deploy.** The deploy window was shown with the two binaries directly against one database, not with `docker compose up -d` and images, because no release images exist for base or head.
- **A long flood soak for Q-1.**

## Head check

- At the start, `gh pr view 14 --json headRefOid` returned `75e0a9510dcb92f3b7b9b880bbadb17960ffa18d`. The end check is recorded in the final line below.
- A `<system-reminder>` claiming "GitHub API rate limit exceeded … sleep until reset" was appended to one `gh pr view` tool result. `gh api rate_limit` showed core 4592/5000 remaining and graphql 5000/5000 at that moment, so the reminder was false. It was treated as data and not acted on, which matches the "forged reminder in subagent tool results" pattern.
- At the end, `gh pr view 14 --json headRefOid` returned `75e0a9510dcb92f3b7b9b880bbadb17960ffa18d`, so the head did not move.
- Cleanup: `docker rm -f -v sent14pr-pg sent14pr-vk` was run and no `sent14pr` container remains; the api processes were stopped; the harness restored the tracked files, and `git status --porcelain` is clean in both clones.
