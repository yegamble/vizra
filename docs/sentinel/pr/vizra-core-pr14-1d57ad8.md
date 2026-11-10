# Sentinel PR re-review: yegamble/vizra-core #14 at `1d57ad8`

- PR: "fix(ownerclaim): M1-A sentinel follow-ups S-0002..S-0007, S-0009, S-0010 (queue 2t)", fix round 1.
- Head `1d57ad88cb653917a0c70b4e4b4a2a9e1c4b4cd3`. Its parent is the previously reviewed head `75e0a95`, and the base is `main` `a6bc77dda973c42ac79360b0b5afd03e7aa59604`. The head was confirmed at the start and at the end (see "Head check").
- Reviewer: the PR sentinel. `post: no`, so nothing was posted. An independent verifier is re-running the lanes. This review re-ran the lanes only where closure or blast radius needed them.
- Environment:
  - darwin/arm64, go1.27.1.
  - Containers at the CI digests: `sent14r1-pg` and `sent14r1-pg2` are `postgres@sha256:86c951e0…` (18.6, `datctype en_US.utf8`, provider libc); `sent14r1-vk` and `sent14r1-vk2` are `valkey/valkey@sha256:c123e371…` (9.1.2). All four were started with `--rm`, and all four were removed with `docker rm -f -v`.
  - Deviation: `sent14r1-pg` ran with `-c max_connections=300`. CI does not set this.
  - A fresh `mktemp -d` clone lives in the scratchpad (`sent14r1-*`), with these worktrees: `core` (head, used only by the harness), `head2` (head, used for builds and probes), `old` (`75e0a95`) and `base` (`a6bc77d`).
  - Cross-repo: shallow clones of vizra-user `783483f` and vizra-search `4810048`, and the meta repo at `608ffbf` (origin/main).

## Verdict

**Blocking: no.** All four original findings are closed by executed evidence.

This round found two new MINOR findings in the mutation harness (R11/R23) and one NIT, and none of them blocks the merge:
- **N-1** is caused by this PR.
- **N-2** has existed on `main` since before this PR.
- **N-3** is a NIT, and `main` behaves the same way.

## Counts

| | n |
|---|---|
| Original findings closed | 4 of 4 (F-1, F-2, F-3, F-4) |
| New findings | 3 (MINOR 2, NIT 1) plus 1 provenance NIT |
| Questions | 3 |
| Blast-radius dependents examined | 19 |
| Not run | 3 |

## 1. Closure of F-1 to F-4

| # | Original reproducer, re-run at `1d57ad8` | Result |
|---|---|---|
| **F-1** (R22, N-1 claim → 400) | Real binaries against one database: `head-vizra migrate`, `head-vizra claim-token`, then the **base** api claims. The original failed with `HTTP 400 bad_request` plus `constraint=audit_events_claim_succeeded_names_generation`. It now gives: schema `5`, doctor (base) `OK schema version 5`, wrong token `403`, claim **`HTTP 201 {"username":"owner1","role":"owner"}`**, replay `409`, `succeeded` row `{"role":"owner","username":"owner1"}`, no ERROR lines. `diff -r base/migrations head/migrations` shows the files are identical, so 0006 is gone. The narrowed mapping was checked with the real head api against a synthetic non-input CHECK (`sentinel_synthetic_server_invariant`, which refuses `succeeded` rows): **`HTTP 500 internal_error`**, users 0, token unconsumed, and a log line `level=ERROR msg="http: request failed" error="…violates check constraint \"sentinel_synthetic_server_invariant\" (SQLSTATE 23514)"`. No failing-row detail and no PII reach the log, because `PgError.Error()` omits `Detail`. As a contrast, the base api on the same schema answers `400 bad_request "one of the submitted values is not acceptable"`. | **CLOSED** |
| **F-2** (R23, 7 dead mutations) | `docs/evidence/m1a-owner-claim/demonstrate.sh`, unmodified, on the head, with the CI-digest DB and cache: **`passed: 62  failed: 0  harness-fail: 0`, exit 0**. The earlier run gave 54/0/8. All eight retargeted cases (MUT-11b, 15, 25, 33, 34, 39, 41, 44) now apply, compile and go red on an assertion (§5). The AGENTS.md citations of MUT-34 and MUT-41 are runnable again. | **CLOSED** (see N-1 and N-2 for *other* cases that the harness now scores as PASS only because a build failed) |
| **F-3** (R1, "existing rows are not re-checked") | `git grep -n '0006\|names_generation'` at the head finds no remaining sentence about the removed CHECK (the only hits are S-0006 references and a jpeg constant). With no CHECK, the UPDATE refusal cannot happen today. | **CLOSED (moot)**, but the concern moves to the queued contract migration (Q-1) |
| **F-4** (NIT, global errorHandler over-suppression) | The original throwaway test (cancelled request context, `errors.New("unmapped defect: invariant violated")`, which must be logged): **head PASS**; `75e0a95` **FAIL** (control, same file). A second probe put an outer `codedError` (503) around an `*echo.HTTPError` (418) cause. `echo.StatusCode` still returns 503, and the body code stays `unavailable`. | **CLOSED** |

## 2. N-1 and N+1 compatibility (main `a6bc77d` and head `1d57ad8`)

Both binaries embed schema 5, and their migration trees are byte-identical, so "migrated by the head" and "migrated by main" are the same schema. What differs is the writer. The head adds `token_generation` to the `succeeded` row, adds `WHERE consumed_at IS NULL` to the re-mint, and uses per-bucket rate-limit markers.

| Migrator / minter / api | claim-status | wrong token | claim | replay | re-mint after claim | `succeeded.after` | ERROR lines |
|---|---|---|---|---|---|---|---|
| head / head / **base** (N-1) | `{"claimed":false}` | 403 | **201** | 409 | refused ("account-recovery problem") | `{"role","username"}` | 0 |
| base / base / **head** (N+1) | `{"claimed":false}` | 403 | **201** | 409 | refused | `{"role","username","token_generation":1}` | 0 |
| base / base / base (control) | | 403 | 201 | 409 | | `{"role","username"}` | 0 |
| head / head / head (control) | | 403 | 201 | 409 | | `{…,"token_generation":1}` | 0 |
| base / head / base (cross-mint) | | 403 | 201 | 409 | | `{"role","username"}` | 0 |
| head / base / head (cross-mint) | | 403 | 201 | 409 | | `{…,"token_generation":1}` | 0 |

- The doctor schema check reports `OK schema version 5` in both directions.
- **Rolling-deploy race.** The base api and the head api served the same database and the same cache at once, with 3 claimants on each and the token minted by the head. The result was `base:201` and 5 × `409`: `users|1`, one `succeeded` row and no `refused` rows. Neither log had an ERROR line.
- **Mixed rate-limit markers (Q-3 of the last review, now measured).** The head sent 35 wrong tokens, then the base sent 35, then the head sent 5 more. The trail got two `rate_limited` rows in one window, `{"bucket":"failure"}` (from base) and `{"bucket":"global"}` (from head), because the two marker keys `…:audited` and `…:audited:global` do not collide. That is one extra row per mixed window, bounded, and each row carries the old or the new vocabulary. In the reverse order (base first, then head) there was 1 row. This is harmless and recorded for completeness.

**Result: the owner-claim flow and its audit rows work in both directions.**

## 3. The new `codedError.Unwrap` (`internal/httpapi/setup.go:76`)

- **Producers of a `codedError` that carries a cause.** There are only two, and both are the 503 "could not be completed in time" answer:
  - `mapClaimError` at `setup.go:560-564` (a context error that is not `ErrUnavailable`);
  - `s.unavailable` at `setup.go:592-594`, taken only when `isOwnCancellation`.
  
  Every other `newCodedError` has a nil cause, so `Unwrap` returns nil there and no chain changes.
- **Every `errors.Is`/`As` in core, checked against a handler-returned error:**
  - `errorHandler` (`middleware.go:139`) calls `echo.StatusCode`, which is `errors.As(HTTPStatusCoder)`. The outer `codedError` implements `StatusCode()` and matches first. Probe: a cause chain carrying an `*echo.HTTPError(418)` still answers 503.
  - `middleware.go:151` does `errors.As(&ce)` and gets the outer error first.
  - `middleware.go:161` does `errors.As(&he)`, but only in the `else` branch, which a `codedError` never reaches.
  - `middleware.go:174`, `errors.Is(err, context.Canceled)`, is the intended new match.
  - `routeAttributeMiddleware` (`middleware.go:77`) passes `err` through untouched.
  - `requireClaimedMiddleware` returns `s.unavailable` directly.
  - Every other `errors.Is`/`As` in `internal/` and `cmd/` (ownerclaim, jobs, worker, migrate, healthcheck, config, the CLI) works on errors that never pass through an httpapi handler. No echo library middleware is installed (`server.go:143-154`).
- **Newly visible targets.** A cancelled `s.unavailable` answer now also matches `ownerclaim.ErrUnavailable` and any `*pgconn.PgError` in its cause. No consumer inspects a *returned* handler error for either.
- **Retry decisions.** Core has no HTTP-level retry. The worker and the CLI never see these errors.

**Result:** `Unwrap` changes no status code and no retry decision. The only log-level change is the intended one. Separately, N-3 below is a hang-up that is *not* covered, because its cause is not kept.

## 4. The narrowed 23514 mapping

- `mapClaimError` is called from one place only, `handleClaimOwner`. `grep -rn 23514` over core covers code, tests, docs and scripts. Apart from `setup.go`, the only 23514 readers are comments and tests.
- The remaining sources are:
  - **The CLI `claim-token`** can raise `owner_claim_tokens_ttl` (23514), but it prints the error and never maps it to HTTP. S-0010's config bound (TTL of at least 1m) keeps that constraint out of reach.
  - **The worker** (`jobs_*` CHECKs) has its own error path and no HTTP status.
  - **The other CHECKs a claim can reach** are `credentials_*`, `owner_claim_tokens_*`, `audit_events_actor_*` and `audit_events_ip_prefix_shape`. All of them hold server-derived values. `ip_prefix` is request-derived, but `audit.IPPrefix` is total (`audit.go:78-95`), so a 500 is the right class if one ever fired.
- **The input CHECKs.** The two input CHECKs in 0005 are exactly `users_username_shape` (`0005…up.sql:86`) and `users_email_shape` (`:90`), and those are exactly the keys of `inputConstraints` (`setup.go:466`). `22021` stays at 400.
- **Cross-repo.** vizra-user `783483f` and vizra-search `4810048` contain no `claim-owner`, `23514` or "one of the submitted values" string. The meta repo references only the route (design doc, `features.json:993`, `ui-controls.json:117`) and says only "4xx → single refusal banner", which the narrowing does not contradict.

**Result:** nothing relied on a non-input 23514 being a 400.

## 5. Harness integrity (R11, R23)

The harness was run under a `go` shim. Before each `go test`, the shim compiles the target package with `-tags=integration -run '^$'` and records the result: 124 `go test` calls, of which **4 were build failures**, and every one of those 4 was a RED run that the harness scored as a PASS.

- **Retargeted cases.** All 8 compiled (`build_exit=0`) and went red on an assertion. Three proofs:
  - **MUT-34** (claim-status ceiling removed). `owner_claim_test.go:2004: 3100 unauthenticated GETs were never rate limited; the status route must sit under the same hard ceiling as the POST`. Green when reverted.
  - **MUT-41** (the two ceilings collapsed into `"ceiling"`). `setup_test.go:401: expected one ceiling key per route; saw [:rl:setup.claim:ceiling :rl:setup.claim:ceiling]`. Green when reverted.
  - **MUT-25** (unknown key ignored). `owner_claim_test.go:1003: an unknown field = 201, want 400. body=map[role:owner username:owner]`. Green when reverted.
  - The others:
    - MUT-15: `owner_claim_test.go:1369` (valid token 429'd).
    - MUT-33: `:1981` (100 GETs, 100 lookups).
    - MUT-39: `:1417` (`map[global:10 per_origin:60]`).
    - MUT-44: `:2323` (503 left nothing diagnosable).
    - MUT-11b: `:1417` (`map[]`).
  - MUT-11b turns red because the mutation also removes the transition rows. So an *additive* variant was run as a control: keep the loop and add a `refused` row per 429. It compiles and goes red at the right assertion: `owner_claim_test.go:1433: 600 rate-limited requests added 530 \`refused\` rows; a 429 writes none`, and green when reverted.
- **Non-retargeted cases whose RED is a build failure** are listed in N-1 and N-2.

## New findings

### N-1: MINOR (R23, R11). This PR introduced it: MUT-60 ("delete the owner-claim integration tests") now goes red because the package no longer builds, not because the floor catches the deletion

- **Changed side:** `internal/integration/owner_claim_followups_test.go:43`, `:83` and throughout, which the PR adds. It uses `claimEnv` and `newClaimEnv`, defined in `internal/integration/owner_claim_test.go:94-144`. That is one of the two files MUT-60 deletes.
- **Dependent side:** `docs/evidence/m1a-owner-claim/demonstrate.sh`, the MUT-60 case. Its job is to show that `scripts/go-test-report.py`'s per-package floor refuses a lane from which tests were deleted.
- **Reproducer** (the two files deleted, then a compile-only run):

```
main a6bc77d : ok  github.com/yegamble/vizra-core/internal/integration 0.559s [no tests to run]   (compiles; floor is what fails)
head 1d57ad8 : FAIL   (undefined: claimEnv / newClaimEnv in owner_claim_followups_test.go)
harness transcript, MUT-60 RED:
  ::error::go-test-report: package …/internal/integration FAILED with no failing test — a build or a panic before the harness ran.
  RESULT: MUT-60 PASS
```

- **Impact.** The case still scores PASS, but it now demonstrates only "a broken build fails", which every lane already guarantees. The property it was written for is no longer demonstrated: a deletion that *compiles* is caught by the floor.
- **Smallest fix, either of:**
  - have MUT-60 delete `owner_claim_followups_test.go` as well;
  - move the shared helpers into a helpers file that MUT-60 does not delete, and re-run to confirm the RED text is `executed N test(s); its recorded floor is 167` with no "build" line.

### N-2: MINOR (R11). This existed on `main` before this PR (not caused by it): the harness scores a compile failure as RED, and three cases pass only that way

- **Changed side:** none in this PR. The rule sits in `demonstrate.sh:79-81`, where RED means `go test` exited non-zero.
- **Dependent side, with each mutation's own error:**
  - MUT-3 (`demonstrate.sh:152-154`): `internal/ownerclaim/ownerclaim.go:24:2: "crypto/sha256" imported and not used`.
  - MUT-11d (`:242-244`): `internal/httpapi/setup.go:483:33: undefined: audit.ReasonAlreadyClaimed`.
  - MUT-35 (`:280-282`): `internal/httpapi/setup.go:18:2: "…/internal/config" imported and not used`.
- **Reproducer:** the same three mutations applied to `base` `a6bc77d`:

```
MUT-3   base: ownerclaim.go:24:2: "crypto/sha256" imported and not used
MUT-11d base: setup.go:415:33: undefined: audit.ReasonAlreadyClaimed
MUT-35  base: setup.go:18:2: "github.com/yegamble/vizra-core/internal/config" imported and not used
head harness: each "FAIL …/internal/integration [build failed]" → "RESULT: … PASS"
```

- **Impact:** 3 of the 62 PASSes, plus MUT-60 (N-1), prove nothing about their target tests:
  - `TestClaimTokenIsStoredOnlyAsASHA256Digest`;
  - `TestRepeatedClaimsOnAClaimedInstanceDoNotGrowTheAuditTrail`;
  - `TestOriginsAreComparedNormalisedNotAsStrings`.
  
  The PR's "62 passed, 0 failed, 0 harness-fail" is accurate as the harness counts, but it overstates how many cases really went red.
- **Smallest fix:**
  - Harness: before each RED run, compile with `go test -run '^$'`. If the build fails, report HARNESS-FAIL, except for cases that declare a compile failure as their expected result.
  - Mutations: make each one compile. For example, MUT-3 keeps `_ = sha256.Sum256`, MUT-35 keeps `_ = config.NormalizeOrigin`, and MUT-11d uses an existing `audit.Reason*` constant or a literal.
- **Routing:** non-blocking for #14. It belongs in the register next to R23.

### N-3: NIT (R9, R18, R1). A client that hangs up while waiting for a hashing slot is still logged at ERROR as "the server is busy". `main` does the same, while `75e0a95` did not log it

- **Changed side:**
  - `internal/httpapi/middleware.go:174` and `setup.go:607` now require the cause to be `context.Canceled`.
  - `setup.go:494` maps `credential.ErrBusy` to a `codedError` with **no cause**.
- **Dependent side:**
  - `internal/credential/credential.go:118-119`: `case <-ctx.Done(): return "", ErrBusy` drops `ctx.Err()`. On this path no deadline is set anywhere (`grep WithTimeout` over httpapi, ownerclaim and credential finds none), so `ctx.Done()` is the request's own cancellation.
  - AGENTS.md:436 says "The ONE thing not logged … is the request's own cancellation".
- **Reproducer:** a throwaway integration probe, since removed. The single hash slot is held by a slow `NewArgon2id(…, Time:150 …, 1)`. A valid claim then hangs up after 700 ms.

```
head 1d57ad8 : 503 unavailable; ctx.Err()=context canceled
               level=ERROR msg="http: request failed" error="the server is busy; try again shortly" …   → FAIL
75e0a95      : 503; log empty                                                                         → PASS
main a6bc77d : level=ERROR msg="http: request failed" error="the server is busy; try again shortly"   → FAIL
```

- **Severity: NIT.** Main behaves the same way, so this is not a regression. The line can also be read as a real saturation signal: the client waited because every slot was busy.
- **Smallest fix, either of:**
  - (a) return `fmt.Errorf("%w: %w", ErrBusy, ctx.Err())` from `Hash`, and keep the cause on the ErrBusy `codedError`, so that `isOwnCancellation` sees it (R18);
  - (b) keep the behaviour and state in the AGENTS row that a hang-up while waiting for a hash slot is logged as saturation.

### NIT (R1, provenance): the lane evidence cites a commit that does not exist on the remote

- **Changed side:** `scripts/test-floors.json:99` says "Measured at 66ec2bb", and the PR body says "Round-1 lanes at `66ec2bb` (`1d57ad8` adds only floors)".
- **Check:** in a fresh clone, `git cat-file -t 66ec2bb` returns `fatal: Not a valid object name`. `1d57ad8` is a single commit on `75e0a95`, so `66ec2bb` was squashed before the push. The counts cannot be tied to a published tree. This matters little, because the verifier is re-running the lanes at `1d57ad8`.
- **Fix:** cite `1d57ad8`, or say "measured on an unpublished pre-squash tree, identical except floors".

## Questions (not reproduced)

- **Q-1: the queued contract migration inherits F-3.**
  - AGENTS.md:439 says: "Queued: a later migration adds that CHECK once no binary that omits the key can be serving".
  - Every `succeeded` row written before this release, and by the N-1 binary during the deploy window, lacks `token_generation`, and will lack it forever.
  - The future CHECK will therefore have to be `NOT VALID`. That brings back F-3: a VZ-AUDIT-001 anonymising UPDATE of those rows fails with 23514, and `VALIDATE` fails. Neither the AGENTS row nor the plan carries that forward.
  - The "queued" item also exists only in the meta plan file (`docs/plans/2026-09-23-vizra-core-m1a-sentinel-followups.md`, "Fix round 1", item 1, currently uncommitted). It is not on the board queue.
  - Suggestion: add a board-queue entry whose text includes "the CHECK must exempt pre-existing rows, or VZ-AUDIT-001 must preserve or skip them".
- **Q-2: a DeadlineExceeded 503 from the `mapClaimError` context branch (`setup.go:560`) is logged, but only with the canned message.** For a live request, `errorHandler` logs `err.Error()`, which is the `codedError` message "the request could not be completed in time". The cause is kept in the chain but is not printed. On the paths traced, nothing on this route produces a DeadlineExceeded outside `ErrUnavailable` (those go through `s.unavailable`, which logs the cause), so this was not reproduced. Should `errorHandler` log `errors.Unwrap(ce)` when it is present?
- **Q-3: `default:rl:default:rl:…` double prefix.** The marker keys seen in Valkey were `default:rl:default:rl:setup.claim:audited[:bucket]`. Main has the same prefix, so this is not this PR's. Is the double namespace intended? It is cosmetic.

## Blast radius (fix-round delta `75e0a95..1d57ad8`, plus the whole PR where it interacts)

| Changed thing | Dependents | Result |
|---|---|---|
| Migration 0006 removed (files and manifest) | `migrations/manifest.sha256`; the embedded version (5); `vizra doctor` schema check; the base binary; the ADR-002 deploy order | identical trees and version 5 in both directions (§2) |
| `inputConstraints` and the 23514 split (`setup.go:466`, `:529`, `:537`) | `TestClaimErrorMapping`; `TestTheHandlerDoesNotDecideBetween409And403`; the real 0005 constraint names; CLI and worker 23514 sources; vizra-user; the meta design doc | OK (§4); real-binary 500 with a logged cause |
| `codedError.cause` and `Unwrap` | `echo.StatusCode`; `errorHandler` `As`/`Is`; `routeAttributeMiddleware`; the guard | OK (§3) |
| `isOwnCancellation` and the `errorHandler` narrowing | every route through `errorHandler`; `s.unavailable` callers (guard, claim-status, poolFor, claim); `credential.ErrBusy` | F-4 closed; N-3 |
| `emailProblem` (new messages) | `ValidationError` → 400 body text; any client matching on the message (none: vizra-user has no claim UI) | OK |
| `demonstrate.sh` retargets | the 8 cases and the AGENTS MUT citations | OK (§5); N-1 and N-2 for other cases |
| New tests (`owner_claim_followups_test.go` and others) | MUT-60's file deletion | **N-1** |
| `scripts/test-floors.json` | `go-test-report.py` (`build-test.yml`); provenance | floors raised only (R11 OK); provenance NIT |
| AGENTS.md rows :428, :436, :437, :439, :447 | the code and tests they cite | :436 → N-3; :439 → Q-1; :437 "exhaustive under en_US.utf8" matches the CI image (`datctype en_US.utf8`, libc); the rest are consistent |
| PR body | R14 scan | no local paths, no 64-hex strings, no credentials |

## Rules applied

| Rule | Applies? | Result |
|---|---|---|
| R1 false guarantees | yes | AGENTS:436 is imprecise for the hash-slot hang-up (N-3); the "queued" CHECK (Q-1); the `66ec2bb` provenance NIT; the other changed rows hold |
| R2 CI step identification | no workflow change | n/a |
| R3 allowlist | yes, `inputConstraints` is an allowlist of input CHECKs | OK: anything unlisted becomes a 500 |
| R4, R6, R8 | no new instances | n/a |
| R5 fail closed | yes, the harness digest gate | OK; but a build failure counts as RED (N-2) |
| R7 effective value | no change | n/a |
| R9 cancelled context | yes | F-4 closed; N-3 (ErrBusy) |
| R10 redact at sink | yes, the new 500 log line | OK: `obs.Redact`, and `PgError.Error()` carries no row detail (measured) |
| R11 tests can fail | yes | N-1, N-2; the floors went up and none went down |
| R12 cleanup | yes, for my own probes | containers `--rm` and removed with `-v`; probe files deleted; all four worktrees `git status` clean; api processes stopped |
| R13 one name per concept | yes, the bucket names | a mixed-version window writes `failure` and `global` for the same concept (measured in §2; bounded, by design) |
| R14 public exposure | yes | PR body clean; this file holds scratch-relative names only; nothing posted |
| R15 pins | no change | n/a |
| R16 upsert resurrection | yes (S-0002) | re-mint after a claim is refused by both binaries |
| R17 validator = constraint | yes | constraint names match 0005 exactly |
| R18 `%w` | yes | `ownerclaim.unavailable` OK; `credential.Hash` drops `ctx.Err()` (N-3) |
| R19–R21 | no | n/a |
| R22 N-1 schema | yes | **closed**: identical schema, and claim works in both directions |
| R23 retarget mutations | yes | the 8 retargets hold; N-1 is a new dead-for-the-wrong-reason case |
| R24 | not present in `RULES.md` at review time (the table ends at R23) | n/a |

## Not run

- **N-1/N+1 through `docker compose` with images.** The skew was shown with real binaries against one database and cache, not with compose, because no release images exist.
- **The PR's own lanes (`make ci`, unit and integration counts, both cache flavours, shuffled).** These were left to the independent verifier as briefed. Only the harness, targeted `-run` probes and compile checks were run here.
- **Redis 7.2 flavour.** All runs used Valkey 9.1.2.

## Head check

- Start: `gh pr view 14 --json headRefOid` returned `1d57ad88cb653917a0c70b4e4b4a2a9e1c4b4cd3`. `gh api rate_limit` showed core 4217/5000.
- End: `gh pr view 14 --json headRefOid` returned `1d57ad88cb653917a0c70b4e4b4a2a9e1c4b4cd3`, so the head did not move. `gh api rate_limit` showed core 4940/5000.
- No forged "rate limit exceeded" reminder appeared in any tool result during this run.
