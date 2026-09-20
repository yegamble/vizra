# Backend / data-model review — vizra-core PR #1 (foundation) at e45e78454f101ebbf814dbdcaeef0117ec9a30e0

Reviewer: `vizra-core` council seat (read-only), dispatched by the war-room chair 2026-09-20 because migrations are append-only once merged. SQL claims were reproduced by the reviewer against a disposable PostgreSQL 16 container. Verbatim, extracted from its transcript by script.

**Chair ruling 2026-09-20:** Findings 1–6 must be fixed before this PR merges (1 and 2 are blockers; 3–6 are schema shape that becomes permanent). Findings 7, 8 and 9 ride along in the same round: 7 and 8 are how Finding 1's fix gets proven and the builder is already in `worker.go`; 9 is a documented constant. Finding 10 and the ADR-004 table-sketch index order are ADR wording — they go into the amending ADR the owner approves (board, owner inbox 4a/4b), not into this PR. The findings are held until the independent verifier and the security seat report, so the builder receives one consolidated round.

---

Verified HEAD = `e45e784`, branch `feat/m0-foundation`, working tree clean, nothing edited. All SQL claims below were reproduced against a disposable PostgreSQL 16 container (now removed), not reasoned from reading.

**Verdict: two BLOCKING items, four REQUIRED-before-merge, three follow-ups.**

The schema is unusually careful — partial idempotency index over live states only, `jobs_lease_complete`, `jobs_terminal_finished`, `storage_locations_one_default`, no tenant column anywhere, DSN kept out of the table, seeded UUIDs fixed so a fresh database is byte-identical. The sqlc output is genuinely generated (`emit_pointers_for_null_types` gives `*string`/`*uuid.UUID`, no `interface{}`), no query builds SQL from strings, and `internal/migrate` correctly reports a dirty ledger instead of force-repairing, refuses a binary older than the database via `StateAhead`, and exposes no `down` path in the CLI. Context propagation is right in `db.Open`, `cache.Open` and the API's drain.

The two blockers are both about permanence.

The first is a real, reproduced durable-work defect where three individually-correct decisions combine: `attempts` is incremented at *claim* time, the sweep requeues an elapsed lease without touching `attempts`, and `jobs_attempts_bounded` makes exceeding `max_attempts` a hard error. After `max_attempts` worker crashes the row can no longer be claimed, and because the claim subselect orders by `priority, run_after` the poisoned row is re-selected on every poll — I watched a healthy job sitting behind it stay at `attempts=0` forever while the claim raised a constraint violation each cycle. The whole site's queue stalls and needs manual SQL. The fix needs no migration, which is why it should land now.

The second is that the append-only guarantee this PR rests on is not actually enforced. `scripts/migration-manifest.sh:12-14` states CI asserts the manifest diff against the base branch contains only added lines; no such job exists in either workflow, and there is no `git diff`/`merge-base` logic anywhere in `.github/` or `scripts/`. `make migrations-manifest` regenerates every hash silently, and the failure message hands a future agent the exact command. As shipped, the manifest catches the honest mistake and not the deadline-pressure edit.

Beyond those: the claim index does not match the claim's `ORDER BY` and indexes terminal rows too, so at 50k queued rows every claim sorts all 50k and spills 2.3 MB to disk (14.5 ms, 815 buffers) where the matching partial index gives 0.03 ms and 4 buffers; `payload` accepted 7.8 MB and `correlation_id` 100 KB with no bound, on the hottest table in the system; `sites` has no singleton constraint although `privacy_mode` is precedence step 1 of the frozen matrix; and `audit_events` is append-only purely by convention — `UPDATE` and `DELETE` both succeeded, and `ip_prefix` accepted `203.0.113.47` whole despite the migration comment promising truncation.

---

## BLOCKING-BEFORE-MERGE

```
FINDING 1: A crash-looping job wedges the entire queue: attempts-at-claim + sweep + CHECK
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0002_jobs.up.sql:34 (jobs_attempts_bounded)
             store/queries/jobs.sql:33-48 (ClaimJob: attempts = attempts + 1)
             store/queries/jobs.sql:105-111 (SweepExpiredLeases: no attempts accounting)
             internal/jobs/worker.go:175-181 (claim error → log, sleep, retry forever)
  requirements: VZ-JOBS-001, VZ-OPS-002, VZ-OPS-005 (ADR-004 § State diagram, § Recovery)

Observed:
  ClaimJob increments `attempts` when a job is CLAIMED, not when it FAILS.
  SweepExpiredLeases returns an elapsed lease to 'queued' without incrementing,
  decrementing or checking attempts. jobs_attempts_bounded makes
  `attempts > max_attempts` a hard constraint violation.
  Reproduced on PostgreSQL 16 against migrations/0002_jobs.up.sql verbatim:
  a row with max_attempts=2, crash-claimed twice and swept twice, reached
  attempts=2, state='queued'. The next ClaimJob returned
    ERROR: new row for relation "jobs" violates check constraint "jobs_attempts_bounded"
    DETAIL: Failing row contains (..., leased, 100, 3, 2, ...)
  and a second healthy job enqueued behind it still showed attempts=0 after
  every cycle — it was never claimed.

Failure:
  A worker that dies mid-job (OOM kill, SIGKILL, node eviction, libvips crash —
  ADR-004 explicitly expects this and has no boot blanket requeue) burns one
  `attempts` per death. After max_attempts deaths the row is unclaimable but
  still `queued` with an old `run_after`, so the claim subselect
  (ORDER BY priority, run_after) selects it first on every poll. worker.go:176
  treats the error as a transient claim failure, logs it, sleeps PollInterval
  and loops. Every subsequent job for that site is never claimed. Derivative
  processing, email, federation delivery and CDN purge all stop; recovery
  requires an operator with psql. Q-028's oldest-queued-age metric will turn
  readiness red, so it is loud — but it is not self-healing, and it is exactly
  the "two api replicas corrupted jobs three ways" class of failure ADR-004
  cites as its reason for existing.

Perspective:
  operator, photographer (uploads never publish), instance-admin

Recommendation:
  No migration and no constraint change. Two query edits:
  1. store/queries/jobs.sql ClaimJob subselect — add `AND attempts < max_attempts`
     so an exhausted row is never selected.
  2. SweepExpiredLeases — split it: rows with `attempts >= max_attempts` go to
     'dead' with last_error 'lease elapsed with attempts exhausted' and
     finished_at = now(); the rest return to 'queued'. That is what ADR-004's
     "max_attempts exhaustion yields dead" means for the crash path, and it
     keeps jobs_attempts_bounded intact as a genuine invariant.
  Then decide and DOCUMENT what `attempts` counts. Claim-count (current) makes a
  crash consume a retry budget; failure-count would need the increment moved to
  RetryJob/DeadLetterJob. Claim-count is defensible and is the crash-loop brake —
  but only once the sweep dead-letters instead of requeueing.

Acceptance criteria:
  * A job whose worker dies max_attempts times ends in state='dead' with a
    last_error naming lease exhaustion, not in 'queued'.
  * After that job is dead, an unrelated job enqueued before it is claimed and
    succeeds.
  * ClaimJob never raises jobs_attempts_bounded under any sequence of
    claim/sweep/claim.
  * vizra_jobs_depth does not grow monotonically after a crash loop.

Tests:
  internal/integration/golden_test.go, new case
  `TestACrashLoopingJobDeadLettersAndDoesNotBlockTheQueue`: enqueue poison
  (MaxAttempts 2) then healthy; loop {ClaimJob; UPDATE leased_until = now() -
  interval '1 minute'; SweepExpiredLeases} three times; assert poison is 'dead'
  and healthy reaches 'succeeded'. It fails against today's code with the
  constraint violation quoted above, which is the controlled-mutation proof
  AGENTS.md asks for. The harness exists; no new infrastructure needed.

Cross-repo implications:
  core: query + worker only. user: none. search: search-event delivery is an
  ADR-004 kind from M3, so this stall would silently stop indexing. meta: none.

Challenge:
  "at-least-once already means handlers are idempotent, so requeueing forever is
  safe." It is not the double delivery that is the bug — it is that the row
  becomes unclaimable AND stays at the head of the claim order, converting one
  poisoned job into a total queue outage. A queue that merely redelivers is
  degraded; this one stops.
```

```
FINDING 2: The append-only manifest can be regenerated silently — the CI half it claims does not exist
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/migration-manifest.sh:12-14, :30-33, :54
             scripts/migrate-lint.sh:95-98
             .github/workflows/ci-required.yml (no such job)
             .github/workflows/build-test.yml (no such job)
  requirements: VZ-FOUND-003 (ADR-002 § Migration discipline); AGENTS.md
                "Append-only migrations"

Observed:
  scripts/migration-manifest.sh:12-14 states:
    "CI adds the other half: it asserts that the diff of manifest.sha256 against
     the base branch contains only ADDED lines, so regenerating the manifest
     cannot launder an edit to a merged migration."
  `grep -rn "base_ref\|merge-base\|origin/main\|fetch-depth" .github/ scripts/`
  returns nothing. `grep -rn "manifest.sha256" .github/` returns nothing. The
  only manifest logic in CI is `make ci` → migrate-lint → `migration-manifest.sh
  check`, which compares the manifest to the files ON DISK in the same commit.
  `scripts/ci-required-guard.sh` guards .github/required-checks.txt, a different
  manifest, and does not touch migrations.

Failure:
  The check is self-consistent, not append-only. Anyone who edits
  0002_jobs.up.sql after merge and runs `make migrations-manifest` gets a green
  migrate-lint and a green ci-required. The script's own failure text at line 54
  tells them the command: "Only when you have ADDED a migration: make
  migrations-manifest". A production database that already applied 0002 never
  re-applies it, so the repo and the live schema diverge permanently while every
  gate is green — precisely the outcome the file says it prevents. This PR's
  entire premise is that these four migrations become frozen on merge; that
  freezing is not implemented.

Perspective:
  operator, developer

Recommendation:
  Add one step to build-test.yml before `make ci` (checkout with
  fetch-depth: 0):
    base=$(git merge-base origin/${{ github.base_ref }} HEAD)
    if git diff "$base" -- migrations/manifest.sha256 | grep -q '^-[0-9a-f]'; then
      echo "a manifest line was REMOVED or CHANGED: a merged migration was edited"; exit 1
    fi
  plus the same assertion for a deleted/renamed migrations/*.sql. Guard it for
  merge_group (compare against the queue base). If that cannot be made reliable
  for merge_group, fall back to CODEOWNERS on migrations/** so a changed hash
  needs owner review, and correct the comment either way — a comment describing
  a control that does not exist is worse than no comment.

Acceptance criteria:
  * A PR that edits any merged migration's bytes and regenerates the manifest
    fails ci-required with a message naming the file.
  * A PR that only ADDS a migration and regenerates the manifest passes.
  * A PR that deletes a migration file fails.
  * migration-manifest.sh's header describes only controls that exist.

Tests:
  A repo-level test cannot prove a CI control. Prove it with two throwaway
  branches and their run URLs recorded in docs/evidence/warroom/ — the negative
  branch (edit 0002, regenerate, push) must go red. Until that evidence exists
  this lane is UNVERIFIED, not passing.

Cross-repo implications:
  core: primary. search: vizra-search ships the same migrate-lint pattern and
  almost certainly has the same hole — worth checking in its PR1.
  meta: the release profile assumes frozen migrations. user: none.

Challenge:
  "CI is another reviewer's lane." The lane boundary is which checks run; this
  is whether the migration-immutability MECHANISM works, which is item 6 of my
  brief and the stated reason this review exists before merge. I would rather
  double-report it than assume the security reviewer reads shell comments for
  claims about controls.
```

```
FINDING 3: jobs_claim does not match the claim's ORDER BY and indexes every terminal row
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0002_jobs.up.sql:53
             store/queries/jobs.sql:44 (ORDER BY priority, run_after)
             docs/adr/ADR-004-...md:47 (the ADR sketch has the same wrong order)
  requirements: VZ-JOBS-001, VZ-OPS-007

Observed:
  Index is `(state, run_after, priority)`; the claim orders by `priority,
  run_after`. Measured on PostgreSQL 16 with 200k terminal + 50k queued rows
  (a realistic steady state inside the ADR's 30/90-day retention window):

    Limit -> LockRows -> Sort (Sort Key: priority, run_after;
             Sort Method: external merge  Disk: 2352kB)
             -> Bitmap Heap Scan on jobs (rows=50000)
    Buffers: shared hit=815, temp read=261 written=295
    Execution Time: 14.523 ms

  With `CREATE INDEX jobs_claim_v2 ON jobs (priority, run_after) WHERE
  state='queued'`:

    Limit -> LockRows -> Index Scan using jobs_claim_v2
    Buffers: shared hit=1 read=2
    Execution Time: 0.031 ms

  Index sizes: jobs_claim 1648 kB (covers all 250k rows), jobs_claim_v2 360 kB
  (covers the 50k live rows only).

Failure:
  Every claim reads and sorts the whole eligible backlog and writes a temp file.
  At Concurrency 4 with a 50k backlog — an import, a re-derive, a purge fan-out —
  the workers spend their time sorting and spilling to disk instead of working,
  and the sort cost grows with backlog depth exactly when the queue is deepest.
  ADR-004 names this itself: "one hot table for every kind of work, so the claim
  index and retention matter from day one."

Perspective:
  operator, photographer (uploads publish slowly under load)

Recommendation:
  In migration 0002, replace line 53 with
    CREATE INDEX jobs_claim ON jobs (priority, run_after) WHERE state = 'queued';
  This is not strictly permanent — a later migration can add the right index
  CONCURRENTLY — but it costs one line today, the wrong index stays in the schema
  forever as dead weight otherwise, and the ADR sketch should be corrected in the
  same breath so the next reader does not re-copy it.

Acceptance criteria:
  * EXPLAIN of the ClaimJob subselect with >=10k queued rows shows an Index Scan,
    no Sort node and no temp file.
  * The index does not cover succeeded/failed/dead rows.

Tests:
  internal/integration/golden_test.go: insert 10k queued rows, run
  `EXPLAIN (FORMAT JSON)` on the claim subselect, assert no "Sort" node appears
  anywhere in the plan. That asserts the property rather than a timing, so it is
  not flaky in CI.

Cross-repo implications:
  meta: docs/adr/ADR-004 § Table sketch line 47 carries the same index and should
  be corrected. core: none beyond the migration. user/search: none.

Challenge:
  "An index is not permanent, so this is a follow-up." True, and I have said so.
  It is in the blocking group only because the cost is one line now versus a
  migration plus a CONCURRENTLY rollout later, and because the ADR will keep
  propagating the wrong shape until someone corrects it.
```

```
FINDING 4: No size bound on payload, kind or correlation_id on the hottest table
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0002_jobs.up.sql:17-18, :28 (no length CHECK)
             internal/jobs/jobs.go:90-97 (json.Marshal with no size check)
             store/queries/jobs.sql:48 (ClaimJob RETURNs payload on every claim)
  requirements: VZ-JOBS-001; AGENTS.md "bound request, file, decoder, subprocess
                and queue resources"

Observed:
  Reproduced: an INSERT with a 8 MB JSON string was accepted —
    kind | payload_size
    noop | 7813 kB
  and `kind` of 5000 characters plus `correlation_id` of 100000 characters were
  both accepted. Enqueue marshals `Payload any` with no bound. `last_error` is
  the only bounded field, and only in Go (worker.go:395, 2000 chars) — not in
  the database.

Failure:
  ClaimJob RETURNs `payload`, so every claim of a fat row pulls it over the wire
  and through TOAST. An import manifest, a batch id list or an accidentally
  embedded blob turns the queue table into a blob store, inflates every backup,
  and — combined with Finding 3's full-backlog scan — makes claiming
  progressively slower. AGENTS.md requires queue resources bounded; they are not.
  There is no product caller of Enqueue yet (only tests), so the bound is free to
  add today and awkward later: adding it in M2 means ADD CONSTRAINT ... NOT VALID
  plus a VALIDATE pass plus deciding what to do with rows that already violate it.

Perspective:
  operator, developer

Recommendation:
  In migration 0002 add:
    CONSTRAINT jobs_payload_bounded CHECK (octet_length(payload::text) <= 65536),
    CONSTRAINT jobs_kind_bounded CHECK (char_length(kind) BETWEEN 1 AND 64),
    CONSTRAINT jobs_correlation_bounded CHECK (char_length(correlation_id) BETWEEN 1 AND 128),
    CONSTRAINT jobs_last_error_bounded CHECK (last_error IS NULL OR char_length(last_error) <= 4096)
  and refuse an oversized payload in Enqueue with a named error, so the caller
  sees a Go error rather than a constraint violation. 64 KiB is generous for
  "ids and a version"; a job needing more should reference a row, not carry it.

Acceptance criteria:
  * Enqueue with a >64 KiB payload returns a named error and writes no row.
  * A direct INSERT of an oversized payload is rejected by the database.
  * jobs_kind_bounded keeps (kind, idempotency_key) inside the btree index limit.

Tests:
  internal/integration/golden_test.go `TestEnqueueRefusesAnUnboundedPayload`:
  assert the Go error, then assert the raw INSERT is rejected — the second half
  is what proves the bound is in the database and not only in the caller.

Cross-repo implications:
  core only. Note for M1: the upload-finalize and derivative kinds must carry
  ids, not extracted metadata blobs.

Challenge:
  "64 KiB is arbitrary and a future kind will need more." Then that kind raises
  it in an additive migration with a stated reason — which is the reviewed
  decision this constraint exists to force.
```

```
FINDING 5: `sites` singleton is documented but not enforced, and GetDefaultSite picks alphabetically
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0001_sites.up.sql:12-27 (no singleton constraint)
             store/queries/sites.sql:6-12 (ORDER BY handle LIMIT 1)
             docs/adr/ADR-007-...md:28, :132 ("exactly one row in core")
  requirements: VZ-PRIVACY-001, VZ-TENANT-001, VZ-FOUND-003

Observed:
  0001_sites.up.sql:3-6 says "Exactly one row in core", and the integration test
  at golden_test.go:131-136 asserts CountSites() == 1 on a fresh database. Nothing
  in the schema prevents a second row. sites.sql:6-8 openly plans for one:
  "Ordering by handle makes the result deterministic even if a future migration
  ever adds one."

Failure:
  `privacy_mode` is step (1) of the frozen precedence matrix — on a private site
  an anonymous viewer is denied every read surface. If a second row is ever
  inserted (a bad import, an admin surface in M2, a restore that merges two
  dumps), GetDefaultSite silently returns whichever handle sorts first
  alphabetically. A site set to `private` whose handle is 'z-main' loses to an
  accidental 'a-test' row with the default 'public', and the whole instance opens
  to anonymous readers with no error anywhere. "Deterministic" is not the property
  that matters here; "correct" is.

Perspective:
  instance-admin, photographer, operator

Recommendation:
  Add to migration 0001:
    CREATE UNIQUE INDEX sites_singleton ON sites ((true));
  Database-per-tenant means one row per database for the life of the product
  (ADR-007 § Site and tenant seam explicitly rejects schema-per-tenant), so this
  is permanently safe and cannot obstruct M5. Then change GetDefaultSite's comment
  and, better, its query to `SELECT ... FROM sites` with no LIMIT so a second row
  becomes a loud :one error rather than a silent wrong answer.

Acceptance criteria:
  * A second INSERT into sites is rejected by the database.
  * GetDefaultSite cannot return a row other than the one site.
  * The M5 tenancy notes record that the singleton is per tenant database.

Tests:
  Add to golden_test.go TestSchemaConstraintsAreEnforced a subtest
  "only one site row": INSERT a second site and assert the error. It fails today.

Cross-repo implications:
  core: authz.Decide step (1) reads this row. user: none. meta: worth one line in
  the M5 tenancy plan.

Challenge:
  "A second site row is a bug that would be caught elsewhere." It would be caught
  by CountSites() on a fresh database only. AGENTS.md says concurrency and
  uniqueness invariants belong in the database, and this one gates every privacy
  decision on the instance.
```

```
FINDING 6: audit_events is append-only and IP-truncating by comment only; the database enforces neither
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0003_audit_events.up.sql:7-11 (the claim), :28 (ip_prefix)
             store/queries/audit.sql:1-8 (insert only; nothing calls it)
  requirements: VZ-ADMIN-002, VZ-FOUND-003 (ADR-007 § audit; ADR-002 § Logging
                and redaction)

Observed:
  The migration header states: "Privacy rules baked into the shape, not left to
  callers: no raw IP column — ip_prefix holds a truncated prefix only". Reproduced
  against the migration verbatim:
    INSERT ... ip_prefix='203.0.113.47'        -> INSERT 0 1   (full IPv4 accepted)
    UPDATE audit_events SET action='nothing-happened', after='{"clean":true}'
                                               -> UPDATE 1
    DELETE FROM audit_events                   -> DELETE 1, rows_left = 0
  `grep -rn "InsertAuditEvent" --include="*.go"` returns only generated sqlcgen
  code — no production caller, and therefore no truncation helper anywhere.

Failure:
  Two separate problems with one root: the shape does not carry the rules the
  comment promises. (a) The audit trail exists specifically so settings, role,
  moderation and privacy changes cannot be rewritten; today the application role
  can UPDATE or DELETE any row, so the trail is evidence only against someone who
  is not trying. ADR-007's stated reason for shipping it in M0 — "an audit trail
  added after the fact has a hole exactly where the interesting period was" —
  applies equally to a trail that can be edited. (b) `ip_prefix` is a plain
  nullable text column with no CHECK and no writer, so the first M1 caller that
  passes `c.RealIP()` stores a full address and the comment turns into a false
  privacy claim in a queryable table.

Perspective:
  instance-admin, visitor (whose IP it is), operator

Recommendation:
  Two additions to migration 0003, both cheap now:
    CONSTRAINT audit_events_ip_prefix_shape CHECK (
      ip_prefix IS NULL OR ip_prefix ~ '^([0-9]{1,3}\.){3}0(/24)?$'
                        OR ip_prefix ~ '^[0-9a-f:]+::(/48)?$' )
  (tune the exact grammar, but make the column refuse a full address), plus a
  BEFORE UPDATE OR DELETE trigger raising an exception, with a named exemption
  path for the retention job when it arrives. A trigger is an additive migration,
  so if the council prefers to defer the trigger, the CHECK alone should still
  land now — it is the half that cannot be added painlessly once rows exist.
  Separately, ship the truncation helper with the first writer in M1, not later.

Acceptance criteria:
  * INSERT with a full IPv4 or IPv6 address in ip_prefix is rejected.
  * UPDATE and DELETE on audit_events raise an error for the application role.
  * The M1 audit writer has a single truncation function with a test covering
    IPv4 /24, IPv6 /48 and the "no IP available" case.

Tests:
  golden_test.go TestSchemaConstraintsAreEnforced subtests "a raw IP cannot be
  stored in ip_prefix" and "an audit event cannot be rewritten or deleted". Both
  fail today with the outputs quoted above.

Cross-repo implications:
  core: primary. user: the M2 admin console reads this table and must not offer a
  delete control. meta: retention policy for audit rows is still unstated —
  ADR-004 sets job retention but nothing sets audit retention.

Challenge:
  "Nothing writes audit_events yet, so this is M1's problem." The column shape and
  the CHECK are exactly what append-only migrations make expensive later — that is
  the reason ADR-005 gives for creating storage_locations in M0 at all. The trigger
  can wait; the CHECK should not.
```

---

## FOLLOW-UPS (not blocking — no migration required)

```
FINDING 7: Every graceful shutdown redelivers all in-flight jobs; the drain comment claims the opposite
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/jobs/worker.go:192 (w.run(ctx, ...) — the loop ctx)
             internal/jobs/worker.go:225 (handler correctly gets WithoutCancel)
             internal/jobs/worker.go:248, :261, :270, :282 (Complete/DeadLetter/
               Retry/Fail all use the CANCELLED ctx)
             internal/jobs/worker.go:195-197 (the comment)
  requirements: VZ-JOBS-001, VZ-OPS-005

Observed:
  worker.go:225 deliberately detaches the handler:
    jobCtx, cancel := context.WithTimeout(context.WithoutCancel(ctx), w.opts.Timeout)
  but every outcome-recording call in the same function takes `ctx`, the
  claimLoop context that signal.NotifyContext cancels on SIGTERM
  (cmd/worker/main.go:50). The comment at :195-197 reads: "a job already leased by
  this process must be allowed to finish and record its outcome, or the sweep
  reclaims work that actually succeeded."

Failure:
  On SIGTERM, in-flight handlers run to completion (correct) and then every
  CompleteJob/RetryJob/DeadLetterJob/FailJob fails instantly with context
  canceled. The code logs "jobs: recording success failed" and returns; the row
  stays `leased`; two minutes later the leader sweep requeues it and it runs
  AGAIN. So every rolling deploy re-delivers every in-flight job — up to
  Concurrency per site, every restart, forever. ADR-004's idempotency rule makes
  this survivable rather than corrupting, but it converts a routine restart into
  guaranteed duplicate external effects (email, federation delivery, IPFS pin),
  which is the failure mode the ADR's Vidra precedent section calls out. The drain
  at :197 does the expensive half and throws away the result.

Perspective:
  operator, member (duplicate email/notification), developer

Recommendation:
  Give the outcome writes their own short-lived context, e.g. in w.run:
    recCtx, recCancel := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
    defer recCancel()
  and pass recCtx to Complete/Retry/DeadLetter/Fail and to finishFailed. Also bound
  the drain in cmd/worker/main.go so a stuck handler cannot hold shutdown for the
  full JobTimeout (5m default) past the container's kill deadline.

Acceptance criteria:
  * A job running when SIGTERM arrives reaches 'succeeded' in the database, not
    'leased'.
  * The sweep after a graceful restart reclaims zero rows.
  * Shutdown completes within a bounded grace period.

Tests:
  golden_test.go `TestGracefulShutdownRecordsTheOutcomeOfAnInFlightJob`: register a
  handler that blocks on a channel; enqueue; wait for state='leased'; cancel the
  worker ctx; release the handler; assert state becomes 'succeeded' and
  SweepExpiredLeases returns nothing. Fails today.

Cross-repo implications:
  core only.

Challenge:
  "Handlers are idempotent by contract, so redelivery is harmless." Then delete the
  drain and the comment. Keeping a drain that cannot record its result is worse
  than not draining: it pays the shutdown latency and still redelivers.
```

```
FINDING 8: No crash-recovery test, and the retry-ladder test never walks the ladder
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/integration/golden_test.go:391-429 (sweep: SQL only)
             internal/integration/golden_test.go:493-534 (MaxAttempts: 1)
             internal/jobs/jobs_test.go (no worker-level recovery case)
  requirements: VZ-JOBS-001, VZ-OPS-005

Observed:
  TestSweepReclaimsOnlyElapsedLeases exercises the sweep STATEMENT — it never
  involves a Worker, so it does not prove that a job whose worker died is
  subsequently claimed and completed. TestRetryLadderAndTerminalFailure is
  commented "walks the ladder and then dead-letters" but enqueues with
  `MaxAttempts: 1`, so RetryJob's `attempts < max_attempts` is false on the first
  failure and the job goes straight to 'dead'. RetryJob's backoff path and the
  Backoff() integration are never executed against a database. The double-delivery
  case at :433-489 enqueues two DIFFERENT jobs with the same payload, which tests
  that the handler tolerates two calls — not that ONE job redelivered after a lost
  lease is handled idempotently, which is what ADR-004 means by "each is tested by
  delivering its job twice".

Failure:
  Findings 1 and 7 both survived this suite. The two invariants with no coverage
  are exactly the two that are broken.

Perspective:
  developer, operator

Recommendation:
  Three cases, all on the existing harness: (a) worker-level crash recovery — run
  a worker, let a handler hang past its lease, sweep, assert the job is re-claimed
  and reaches a terminal state; (b) a real ladder walk with MaxAttempts 3,
  asserting run_after moves out and attempts increments per failure; (c) the
  Finding 1 case. Fix the misleading comment at :491-492 either way.

Acceptance criteria:
  * A test fails if RetryJob's attempts guard or backoff is removed.
  * A test fails if SweepExpiredLeases stops requeueing.

Tests:
  As above, in internal/integration/golden_test.go behind the existing
  `integration` build tag.

Cross-repo implications:
  core only.

Challenge:
  "M0 ships one noop kind; deep queue tests are premature." The opposite: every
  real kind from M1 inherits this machinery unchanged, and these are the cheapest
  tests this repo will ever write.
```

```
FINDING 9: Priority 0 is silently rewritten to 100, so the highest priority is unreachable
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/jobs/jobs.go:101-103
             migrations/0002_jobs.up.sql:21 (priority smallint DEFAULT 100)
  requirements: VZ-JOBS-001

Observed:
  `if j.Priority == 0 { j.Priority = DefaultPriority }` with
  DefaultPriority = 100, and jobs.go:38 documents "lower runs first". Zero is the
  most urgent value and is the Go zero value, so a caller who writes
  `Priority: 0` meaning "most urgent" gets the default instead, silently.

Failure:
  A latent trap for M1's upload-finalize path, which is the one kind that will
  want to jump the queue. No current caller.

Perspective:
  developer

Recommendation:
  Make Priority a *int16, or invert so higher runs first and zero means default,
  or add `PriorityUrgent int16 = 1` and document that 0 is reserved. Cheapest:
  document 0 as "unset" in the NewJob comment and add PriorityUrgent = 1.

Acceptance criteria:
  A caller can enqueue a job that is claimed ahead of a default-priority job.

Tests:
  A unit test asserting the resolved priority for each input; no database needed.

Cross-repo implications:
  core only.

Challenge:
  "Nobody will pass 0." M1 will, because 0 looks like the most urgent value in a
  lower-runs-first scheme.
```

```
FINDING 10: ADR-002's "the settings registry and its version counter row are M0 schema" has no migration
Severity:    SHOULD
Confidence:  medium

Affected:
  repo:      vizra (meta) / vizra-core
  files:     docs/adr/ADR-002-...md:222-224
             vizra-core/migrations/ (only 0001–0004; no instance_settings)
  requirements: VZ-ADMIN-002, VZ-FOUND-003

Observed:
  ADR-002's "Reservation only" paragraph reads: "the settings registry and its
  version counter row are M0 schema driven from the admin UI in M2
  (VZ-ADMIN-002)". Read one way that means the SCHEMA is M0 and only the UI is M2;
  read the other way the whole thing is deferred. This PR ships neither table.
  The M0-obligations paragraph above it (lines 205-211) lists internal/config, the
  probes, make ci, openapi and sqlc — not instance_settings — which favours the
  second reading.

Failure:
  Low risk either way: instance_settings arriving as migration 0009 in M2 is purely
  additive and forces no amendment to 0001–0004. But an ambiguous ADR sentence about
  what M0 owes is the kind of thing that produces a "we thought you did it" gap at
  the M2 boundary, and this is the last moment it is free to settle.

Perspective:
  developer, instance-admin

Recommendation:
  Do NOT add the table to this PR. Reword ADR-002:222-224 to say explicitly
  "instance_settings and its version counter row ship with VZ-ADMIN-002 in M2;
  M0 owes only the env-var config registry in internal/config/keys.go", and note
  in the ledger which env keys are restart-only versus future settings-registry
  keys — ADR-002's own restart-only-vs-live distinction is not recorded anywhere
  in internal/config/keys.go today.

Acceptance criteria:
  * ADR-002 names one milestone for instance_settings.
  * Each key in config.Registry is marked restart-only or live-reloadable.

Tests:
  Documentation; no test. The keys.go annotation could be asserted by the existing
  config-template-check.

Cross-repo implications:
  meta: ADR-002 edit. core: a comment-level annotation in keys.go. user: the M2
  admin console needs to know which keys it may not offer to edit.

Challenge:
  "This is a docs nit." It is, until M2 opens and two agents each believe the other
  created the table.
```

---

## NOT WORTH DOING

- **A `site_id` or `tenant_id` column on `jobs` or `audit_events`.** Q-008 forbids it and database-per-tenant makes it dead weight a later reader would start trusting. The migrations are correct here and the comments explaining why are worth keeping.
- **Adding `storage_location_id`, `visibility_version` or any media column now.** ADR-005 is explicit that `asset_files` arrives in M1 with the reference; pre-creating columns for tables that do not exist would be worse than an additive migration.
- **Splitting `jobs` per kind, or adding `job_runs` now.** ADR-004 chose one table deliberately and reserved `job_runs`; re-litigating that here would reverse an accepted decision on no new evidence. Findings 1, 3 and 4 fix the single table rather than replace it.
- **Rewriting the ClaimJob CTE to batch-claim N rows.** Real win at high throughput, but it changes the lease and heartbeat semantics that Findings 1 and 7 touch; sequence it after those land.
