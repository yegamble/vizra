# ADR-004: Durable work: transactional outbox and jobs

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`AGENTS.md` requires durable idempotent jobs, explicit retry and recovery,
bounded queue and subprocess resources, and database constraints for concurrency
invariants; `docs/ARCHITECTURE.md` requires the job record written in the same
transaction as the business mutation. Vidra's history makes the cost concrete: a
committed mutation whose enqueue failed was silently lost until a reconcile sweep,
and two api replicas once corrupted jobs three ways.

## Decision
Unlike Vidra's roughly twelve per-feature queue tables, best-effort side-writes
and a `WithTx` helper with a single caller, Vizra has **one `jobs` table** written
in the same transaction as the business mutation. A test enforces the rule: every
`Enqueue` takes a `pgx.Tx`, and because the API accepts only a transaction type,
an enqueue outside a transaction does not compile.

### Table sketch

```sql
CREATE TABLE jobs (
  id              uuid PRIMARY KEY,          -- uuidv7
  kind            text NOT NULL,
  payload         jsonb NOT NULL,
  idempotency_key text NULL,
  state           text NOT NULL,             -- queued|leased|succeeded|failed|dead
  priority        smallint NOT NULL,
  attempts        int NOT NULL,
  max_attempts    int NOT NULL,
  run_after       timestamptz NOT NULL,
  leased_until    timestamptz NULL,
  leased_by       text NULL,
  last_error      text NULL,
  correlation_id  text NOT NULL,
  created_at      timestamptz NOT NULL,
  updated_at      timestamptz NOT NULL,
  finished_at     timestamptz NULL
);
CREATE UNIQUE INDEX jobs_idem ON jobs (kind, idempotency_key)
  WHERE state IN ('queued','leased');
CREATE INDEX jobs_claim ON jobs (state, run_after, priority);
```

There is no site or tenant column on `jobs`: a job lives in the database of the
site it belongs to, and the worker fans out over the site registry's DSNs
(ADR-007, Q-008 checklist item 5). Q-008 forbids a tenant column in core and
isolates tenants by DSN, so a discriminator here would be dead weight. The DSN
source is ADR-007 § "Site and tenant seam": **in core there is no DSN column** —
the registry is the single `sites` row of the connected database plus the one
`DATABASE_URL` from configuration, and what the worker iterates is
`site.Resolver.Sites()`, which returns exactly one entry in core and the control
database's hostname → DSN mapping under tenancy (M5).

### State diagram (text)

- `queued` → `leased`: a worker claims the row with `FOR UPDATE SKIP LOCKED` when
  `run_after <= now()`, ordered by priority, and sets `leased_until`/`leased_by`.
- `leased` → `leased`: a heartbeat renews `leased_until` every lease/3.
- `leased` → `succeeded`: the handler returned no error; `finished_at` is set.
- `leased` → `queued`: a retryable error with `attempts < max_attempts`;
  `attempts` increments and `run_after` moves out along the retry ladder with
  jitter (ladder values `[to confirm in M0]`).
- `leased` → `dead`: a retryable error with `attempts = max_attempts`.
- `leased` → `failed`: a terminal error, which bypasses the retry ladder entirely.
- `leased` → `queued`: the lease elapsed; a leader-gated sweep every 2 minutes
  reclaims it.
- Retention: `succeeded` pruned after 30 days, `failed` and `dead` kept 90 days,
  `queued` never pruned. `job_runs` audit rows (attempt, error, duration) are kept
  90 days.

### Execution rules
Per-kind concurrency limits and a per-job wall-clock timeout apply; the timeout is
a context deadline, and any subprocess runs in its own process group and is killed
on timeout. Per-kind concurrency and timeout defaults are `[to confirm in M0]`.
`max_attempts` exhaustion yields `dead`, and the dead-letter queue is inspectable
in `/admin/jobs` (M2) and through `vizra jobs list|retry|drop`.

Recovery has no boot blanket requeue; instead a leader-gated lease-elapsed sweep
runs every 2 minutes, with leader election by a session-scoped advisory lock in
its two-integer form so it cannot collide with golang-migrate.

Every external effect — search events, federation delivery, CDN purge, IPFS pin,
webhooks, email — is a `kind` in this table, so there is one mechanism and not
five; the search reconcile sweep survives as belt-and-braces, not as the primary
path. Every handler is idempotent by design, with keys derived from the mutation,
and each is tested by delivering its job twice. The worker fans out over the site
registry (Q-008 checklist item 5).

Metrics: `vizra_jobs_depth{kind,state}`,
`vizra_jobs_oldest_queued_age_seconds{kind}` — which feeds the doctor and
readiness thresholds of Q-028 — and `vizra_jobs_stale_leases`.

## Consequences
Positive: a committed mutation can never lose its side effect; one table means
one depth gauge, one retention policy and one dead-letter view; the compile-time
transaction requirement makes the invariant unbreakable rather than merely
documented. Negative: one hot table for every kind of work, so the claim index and
retention matter from day one, and a noisy kind can crowd others until per-kind
concurrency is tuned. Risks: a handler that is not genuinely idempotent turns a
lease reclaim into a double effect — the twice-delivered test is the guard; the
sweep must reclaim only rows whose `leased_until` has elapsed. Later milestones
must not break: the single table, the transaction-only enqueue, `SKIP LOCKED`
claiming, the leader-gated sweep, the absence of a boot blanket requeue, and the
queue-age metric readiness and doctor depend on.

## Precedent
Copied from Vidra (survey citations): `FOR UPDATE SKIP LOCKED` claiming with a
lease renewed on a timer (`C/internal/lease/lease.go:32,45-74`;
`C/store/queries/upload_finalize_jobs.sql:73,132`); the shared retry ladder
(`C/internal/retry/retry.go:26`) and terminal-error bypass
(`C/internal/uploadfinalize/service.go:60-68,453`); idempotency by a partial
unique index over live states returning the in-flight job
(`C/migrations/0120_upload_finalize_jobs.up.sql:78`;
`C/store/queries/upload_finalize_jobs.sql:20`); the event-id unique key and
`pending|delivered|dead` states of the outbox
(`C/migrations/0092_search_outbox.up.sql:13,15,18`); the job loop with interval,
jitter, leader gating and a capped failure ladder
(`C/internal/jobloop/jobloop.go:81-101,146-160`) and bounded concurrency
(`C/internal/workerpool/pool.go:37`); leader election by a session-scoped advisory
lock in two-int form (`C/internal/leaderlock/leaderlock.go:44-60`) with sweeps
leader-gated (`C/cmd/api/main.go:2169`); the deliberate removal of boot
blanket-requeue and the lease-elapsed sweep that replaced it
(`C/internal/jobrecovery/jobrecovery.go:17-43,81-113`); retention split between
live and terminal rows (`C/internal/searchevents/retention.go:16-63`;
`C/internal/jobstatus/jobstatus.go:547`); and the queue metric names
(`C/internal/observability/metrics.go:139-163`).

Unlike Vidra: there is no generic job table and no transactional outbox there —
`search_outbox` is a best-effort side-write that logs and swallows a failed insert
(`C/internal/searchevents/enqueuer.go:60-92`), repaired later by a re-emit sweep
(`C/internal/searchevents/reconcile.go:30`), and `WithTx` exists with one caller
(`C/internal/store/sqlcgen/db.go:28`; `C/internal/peertubeimport/importer.go:621`).
The depth gauge omits two queues (`C/internal/jobstatus/jobstatus.go:187`), the
projection's lease columns are never populated
(`M/docs/productionization/interfaces.md:108`), the outbox has no correlation or
trace column (`M/docs/productionization/release-readiness.md:8591`), leader
failover was measured at 10.4 s (`:18428`), there is no per-job wall-clock
timeout, and two api replicas once corrupted jobs three ways — double claims,
double delivery of signed federation activities, and boot requeue of the other
node's work (`M/docs/productionization/risks.md:29`).

## Evidence and ratification
Q-008 (the worker loops a registry and leases from each database; no tenant
column) and Q-028 (oldest-pending-job age exposed as a metric that fails doctor
and readiness above 15 minutes) in the `docs/OPEN_QUESTIONS.md` ratification
record. No version claim is made here.

## Ledger IDs
VZ-JOBS-001, VZ-FOUND-003, VZ-OPS-002, VZ-OPS-005, VZ-OPS-006, VZ-OPS-007,
VZ-SEARCH-004.

## M0 obligations
The M0 foundation issue implements migration `0002_jobs` with the table, both
indexes and the state constraint; the `cmd/worker` loop with claim, lease,
heartbeat and the leader-gated sweep; one `noop` kind; the three metrics; and the
compile-time proof that `Enqueue` requires a transaction.

Reservation only: `job_runs`, retention jobs, the dead-letter admin surface
(VZ-OPS-006, M2) and the real kinds (processing, search events, federation
delivery, IPFS pin, purge, email) arrive with their own slices; the table shape
above is the reservation they must fit.
