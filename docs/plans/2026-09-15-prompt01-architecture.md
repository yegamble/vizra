# Execution plan: Prompt 01 architecture pass — ADR-001…009 (design pass only; no acceptance ID closed)

## Context
- Repository: `vizra` meta repo, branch `main`. Base commit `bf25303` ("initial
  commit"), plus the uncommitted ratification changes from
  `docs/plans/2026-09-15-open-questions-ratification.md`, nothing committed. This
  pass edits tracked files on top of that working tree and commits nothing.
  Measured after the correction pass below: **36 modified tracked files** and five
  new paths (`git status --short` → 41 lines).
- Repositories `yegamble/vizra-core`, `yegamble/vizra-user` and
  `yegamble/vizra-search` were created 2026-09-15, private and README-only;
  content is still PLANNED. `docs/issues/VZ-ISSUE-001.md` was filed as
  <https://github.com/yegamble/vizra/issues/1> (#1).
- Owner instruction chain: (1) ratify `docs/OPEN_QUESTIONS.md` before starting
  Prompt 01 with VZ-ISSUE-001 — done 2026-09-15; (2) authorize GitHub writes for
  repository creation and issue filing — done 2026-09-15; (3) run the Prompt 01
  design pass, where the chair took the architecture decisions and this session is
  the single writer for the ADR set and this plan.
- Inputs of record: the chair's Prompt 01 architecture brief (session artifact),
  the Prompt 01 Vidra precedent survey (the only source for Vidra `file:line`
  citations; `~/github/vidra` was not opened in this pass), the
  `docs/OPEN_QUESTIONS.md` ratification record, and
  `docs/evidence/research-2026-09-15/ratification-facts.md` (the only source for
  version numbers and dates).
- Constraints honoured: no code, compose, CI or GitHub writes; no edits to
  `docs/OPEN_QUESTIONS.md`, `docs/quality/features.json`, anything under
  `docs/evidence/`, `prompts/`, `AGENTS.md`, `docs/PRODUCT_CHARTER.md` or
  `docs/DESIGN_BRIEF.md`; nothing committed.

## Acceptance
Prompt 01's "Resolve:" list and the paragraphs that follow it, each mapped to the
ADR section that resolves it:

| Prompt 01 requirement | Resolved by |
|---|---|
| Identity / session / CSRF model | ADR-003 Decision (sessions, API keys, CSRF table) |
| Media and derivative lifecycle | ADR-006 Decision (representation table, bounds) |
| Many-to-many album membership and privacy rules | ADR-007 Decision (`album_items`, precedence, the five rulings) |
| Durable outbox / jobs | ADR-004 Decision (one `jobs` table, DDL, state diagram) |
| Quota / idempotency constraints | ADR-005 Decision (reservation ledger, idempotent finalize) |
| Storage capabilities | ADR-005 Decision (`Backend` plus capability interfaces) |
| Tenant / site model for parity | ADR-007 Decision (site seam, no tenant column) |
| Federation mappings | ADR-008 Decision (mapping table, `remote_publications`) |
| Codec boundary | ADR-006 Decision (worker-only decode, libvips-only evidence) |
| Release / configuration ownership | ADR-002 Decision (config seam, settings, release record, deploy ordering) |
| OpenAPI as the API source; sqlc queries/migrations as the database source; generated TypeScript clients | ADR-002 Decision (contracts) |
| Pin verified supported dependency versions and preserve licences | ADR-001 Decision and licence table |
| First acceptance platform, ARM64 qualification before advertising | ADR-009 Decision (platform) |
| Resource and fixture baselines | ADR-009 Decision (minimum host, budget table, fixture manifest, load corpus) |
| No production host or paid cloud without authorization | ADR-009 Decision (rehearsal path) and Blockers below |
| Repeatable clean-target rehearsal path now | ADR-009 Decision (`boot` lane versus `install.sh` rehearsal) |
| Required-check manifest and an aggregate check that cannot pass when a lane did not run | ADR-002 Decision (CI fan-in) |
| Protect workflow/manifest/gate changes; PR and merge-queue events | ADR-002 Decision (ruleset list items 1–8) |
| Do not fabricate branch protection; supply exact configuration and record enforcement unverified | ADR-002 Decision (ruleset list items 9–10) and Q-032 |
| Demonstrate a deliberately broken assertion fails its gate, then restore it | Deferred to execution: the M0 foundation issue's demonstrations (Implementation step 1) — no CI exists to break in this pass |
| Executable foundation: repository structure, lockfiles, Go and web builds, health/readiness, secure runtime configuration, migrations, Redis connection, production-mode Compose/images, deterministic fixtures, browser-test environment, CI | Deferred to execution: VZ-ISSUE-001 (structure, lockfiles, builds, probes, config, migrations, images, fixtures, CI); VZ-ISSUE-002…004 own compose topology, installer/wizard and the boot lane |
| `docs/quality/COMMANDS.md` created from commands that actually execute | Deferred to execution: meta PR1 (Implementation step 6) — it may not be written before commands exist |
| Install/doctor scaffolding performing real checks | Deferred to execution: VZ-ISSUE-001 (`doctor` real checks) and VZ-ISSUE-002 (installer/wizard) |
| Boot the real production-mode stack and test API↔database↔web connectivity from a clean workspace | Deferred to execution: the meta `boot` lane, VZ-ISSUE-004 / VZ-CI-003 |
| Close with the next slice plan, not a readiness declaration | This plan's Blockers and handoff |

Non-goals of this slice: writing any code, compose file, workflow or CLI;
creating `docs/quality/COMMANDS.md`; changing any acceptance target, ledger entry
or open question; applying rulesets; committing, pushing or merging.

## Implementation
Documentation only.

- New `docs/adr/README.md` — naming convention `ADR-NNN-<slug>.md`, the
  Proposed → Accepted (owner) → Superseded status vocabulary, the
  immutable-once-Accepted rule with amendment by a new ADR, the nine required
  sections, the `C`/`U`/`M` precedent-path convention, the meaning of
  `[to confirm in M0]` and `[pin at PR time; verify]`, the statement that Vidra
  has no ADRs, and the index table (number, title, status, Q-ids, ledger IDs).
- New `docs/adr/ADR-001-stack-pins-and-licences.md` … `ADR-009-acceptance-platform-fixtures-budgets.md`
  — nine ADRs, one per brief section, all Status
  `Proposed — awaiting owner architecture approval (Prompt 01 gate)`, Date
  2026-09-15. ADR-001 carries the licence table; ADR-002 the ruleset list and the
  self-merge statement; ADR-003 the CSRF decision table and the `authz.Decide`
  signature; ADR-004 the `jobs` DDL sketch and the textual state diagram; ADR-005
  the upload state machine, the reserve → commit/release ledger flow and the key
  grammar; ADR-006 the representation and metadata-policy tables; ADR-007 the
  entity/key list and the precedence rules; ADR-008 the protocol mapping table and
  the SSRF rule list; ADR-009 the fixture manifest and the PROVISIONAL budget
  table.
- `docs/ARCHITECTURE.md` — the first paragraph's sentence "Freeze decisions as ADRs
  during Prompt 01." replaced by the pointer to `docs/adr/`; nothing else changed.
- `docs/issues/VZ-ISSUE-001.md` — one Verification bullet (read the ADRs and this
  plan before implementing) and one Dependencies line (owner architecture approval
  of ADR-001…009); then, in the correction pass, the "Ledger IDs" line widened to
  VZ-FOUND-001…008, the Outcome extended to name the fixture corpus and the
  browser-test environment, and two Acceptance bullets added for them (D11).
- `README.md` — one baseline bullet for `docs/adr/` and a rewritten "Next:" line.
- This plan.

### VZ-ISSUE-001 PR sequence (after architecture approval)
VZ-ISSUE-001 covers **VZ-FOUND-001…008** — `docs/MILESTONES.md` M0 lists all
eight. One PR per repository per session, in this order; each opened
READY_FOR_REVIEW with the evidence `AGENTS.md` demands.

1. **`vizra-core` PR1 "foundation"** (VZ-FOUND-001…006) — `go.mod` pins per
   ADR-001; `Makefile` `ci` = fmt-check, vet, migrate-lint, openapi-verify,
   sqlc-verify, test-race; `internal/config` with `LoadFrom` plus fail-secure
   production validation and tests (dev secret refused, short secret refused,
   escape hatches refused); `cmd/api` with Echo v5 + `otelhttp` + the route
   middleware (spike evidence) and `/healthz`, `/readyz`, `/version`, `/schemaz`;
   the **Valkey client wiring** — `go-redis` v9, a readiness probe of the cache,
   the two-image integration matrix lane skeleton (pinned Valkey + Redis 7.2.x)
   and the in-memory rate-limit fallback stub that marks readiness degraded
   (ADR-001 Q-004, ADR-003); `internal/search` with the `Searcher` interface
   (`Search`, `Suggest`, `Publish(event)`), the `remote` HMAC client that treats
   `not_indexed` as fallback and a `sql` implementation returning empty results
   (no product tables exist yet), the internal contract paths under
   `/internal/v1/` in `api/openapi.yaml` with its drift check, and readiness
   reporting `search: off|ok|degraded` (ADR-002, Q-001); `cmd/worker` with the
   jobs-loop skeleton (ADR-004 table, claim/lease/heartbeat/sweep, one `noop`
   kind, metrics); `cmd/vizra` with `version`, `doctor` (config check, compose
   version, ports, database reachability, cache flavour and version — real checks
   only) and `migrate`; migrations `0001_sites` (one default row), `0002_jobs`,
   `0003_audit_events` and `0004_storage_locations` (one `local` default row —
   ADR-005; `asset_files.storage_location_id` references it when the media tables
   arrive in M1); the `internal/authz` evaluator with the table-driven test whose
   fixture is ADR-007's frozen surface × visibility matrix; sqlc config, generated
   code and the `sqlc diff` guard; migrate-lint plus the append-only checksum
   manifest; `api/openapi.yaml` with the probe operations and both-direction
   contract tests; the Dockerfile (digest-pinned Debian 13 base, libvips from a
   checksummed tarball below the Go binary layer, loader list emitted at build);
   `.github/workflows` build-test, govulncheck, docker-build,
   `required-checks.txt` and `ci-required` on `pull_request` and `merge_group`.
   Demonstrations: route-without-spec fails; spec-without-route fails; hand-edited
   sqlc output fails; production boot refuses dev secrets; an edited merged
   migration fails the manifest check; the golden path passes after `FLUSHALL`.
2. **`vizra-core` PR2 "fixtures"** (VZ-FOUND-007) — the deterministic fixture
   generator script (pinned libvips + exiftool in the CI image), the committed
   sha256 manifest with the generator version, the twelve M0 fixtures of ADR-009,
   and the load-corpus generator kept separate from the correctness corpus.
   Demonstration: the manifest reproduces byte-identically, and a changed fixture
   fails the check.
3. **`vizra-user` PR1** (VZ-FOUND-002) — Next.js 16.3.x skeleton; `npm run ci` =
   lint, typecheck, test, build; codegen from `vizra-core/api/openapi.yaml` into
   one committed client file with drift CI; `publicFetch`/`viewerFetch` helpers
   with the lint rule that forbids identity headers in revalidated fetches; the
   production Dockerfile; a health page; `required-checks.txt`.
4. **`vizra-user` PR2 "browser environment"** (VZ-FOUND-008) — the Playwright
   harness driving the **production build**, desktop and mobile projects, console
   and network error capture, running in CI against the built image.
   Demonstration: a console or network error fails the lane.
5. **`vizra-search` PR1** — the minimal real service of ADR-002 and Q-001:
   `/healthz`, `/readyz`, `/version`, HMAC-verified
   `/internal/v1/search|suggestions|events` returning an explicit `not_indexed`
   status; a **drift check of the same contract** written in core's canonical
   OpenAPI, so both repositories fail on divergence; `make ci` with lanes that
   test exactly that and skip nothing; Dockerfile; workflows; no migrations yet,
   so it reports no `search_schema_version`.
6. **meta PR1** — `docs/adr` accepted; `docs/quality/COMMANDS.md` created from
   commands that ran; this plan checkpointed; ledger entries VZ-FOUND-001…008
   updated with evidence paths. VZ-ISSUE-002, VZ-ISSUE-003 and VZ-ISSUE-004 follow
   as their own issues.

Not in VZ-ISSUE-001: compose topology, installer and wizard, and the boot lane
(VZ-ISSUE-002…004).

## Verification
**No command ran, because nothing executable exists.** There is no Go module, no
`package.json`, no compose file and no workflow in any Vizra repository; the three
component repositories are README-only. This pass is therefore DOCUMENTED, not
IMPLEMENTED and certainly not VERIFIED, and no ledger entry changes status because
of it.

What can be verified for a docs-only pass is that each Prompt 01 requirement has a
written home:

| Prompt 01 requirement | ADR § | Status |
|---|---|---|
| Identity/session/CSRF | ADR-003 § Decision | DOCUMENTED |
| Authorization evaluator and default deny | ADR-003 § Decision | DOCUMENTED |
| Media/derivative lifecycle | ADR-006 § Decision | DOCUMENTED |
| Codec boundary | ADR-006 § Decision | DOCUMENTED |
| Metadata and GPS policy | ADR-006 § Decision | DOCUMENTED |
| Album membership and privacy rules | ADR-007 § Decision | DOCUMENTED |
| Privacy precedence and surface matrix | ADR-003 § Decision, ADR-007 § Decision | DOCUMENTED |
| Durable outbox/jobs | ADR-004 § Decision | DOCUMENTED |
| Quota and idempotency | ADR-005 § Decision | DOCUMENTED |
| Storage capabilities and key grammar | ADR-005 § Decision | DOCUMENTED |
| Tenant/site model | ADR-007 § Decision | DOCUMENTED |
| Federation mappings and SSRF guard | ADR-008 § Decision | DOCUMENTED |
| Release and configuration ownership | ADR-002 § Decision | DOCUMENTED |
| OpenAPI / sqlc / generated client sources | ADR-002 § Decision | DOCUMENTED |
| Pinned versions and preserved licences | ADR-001 § Decision, § Licence table | DOCUMENTED |
| Acceptance platform and ARM64 rule | ADR-009 § Decision | DOCUMENTED |
| Resource and fixture baselines | ADR-009 § Decision | DOCUMENTED |
| Clean-target rehearsal path | ADR-009 § Decision | DOCUMENTED |
| Required-check manifest and aggregate gate | ADR-002 § Decision | DOCUMENTED |
| Branch protection recorded, not fabricated | ADR-002 § Decision (items 1–10) | DOCUMENTED |
| Self-merge substitute stated plainly | ADR-002 § Decision | DOCUMENTED |

M0 demonstrations that will be the evidence later — none of them exists yet:

1. route-without-spec fails CI; 2. spec-without-route fails CI; 3. hand-edited
sqlc output fails the drift check; 4. production boot refuses a dev secret, a
short secret and each named escape hatch; 5. an edited merged migration fails the
append-only checksum manifest; 6. a deliberately broken assertion turns its gate
red, then is restored; 7. `ci-required` fails when a listed lane never ran;
8. `doctor` performs real checks and fails on a real defect; 9. the traced-route
spike shows a span carrying `http.route`; 10. the fixture manifest reproduces
byte-identically from the pinned generator.

## Progress and evidence
- 2026-09-15: read the chair's architecture brief and the precedent survey in
  full, then `docs/OPEN_QUESTIONS.md` (ratification record),
  `docs/evidence/research-2026-09-15/ratification-facts.md`,
  `docs/ARCHITECTURE.md`, `docs/META_REPO.md`, `docs/PRODUCT_SPEC.md` §§3–12 and
  §15, `AGENTS.md`, `docs/DEFINITION_OF_DONE.md`,
  `docs/RELEASE_ACCEPTANCE.md`, `prompts/01-architecture-and-foundations.md`,
  `docs/issues/VZ-ISSUE-001.md`, `docs/plans/TEMPLATE.md` and the prior
  ratification plan.
- 2026-09-15: every ledger ID quoted in an ADR checked to exist in
  `docs/quality/features.json` with `jq`; `docs/quality/features.json` was read
  only, never modified.
- 2026-09-15: wrote `docs/adr/README.md` and ADR-001…009; applied the four
  one-line edits to `docs/ARCHITECTURE.md`, `docs/issues/VZ-ISSUE-001.md` and
  `README.md`; wrote this plan.
- 2026-09-15: **Correction pass after independent verification: D1–D12, S1–S9
  applied.** An independent verifier found 21 defects in the ADR set and the chair
  ruled on each; every ruling was applied by a single writer, with no decision
  re-opened and no mechanism added beyond the rulings. Files changed in this pass:
  `docs/adr/ADR-001-stack-pins-and-licences.md` (D7 Q-004 in full, D8 Q-034
  completeness, S8 one licence-table row per runtime dependency with an SPDX
  re-verification column);
  `docs/adr/ADR-002-repository-process-release-configuration-ownership.md` (D1
  Q-001 verbatim plus the M0 search boundary, D6 Q-017 in full, D12/S4 merge-queue
  events and the two-file drift job, S6 the logging-redaction rule);
  `docs/adr/ADR-003-identity-sessions-csrf-authorization.md` (S7 argon2id
  parameters pinned and the marker removed, D2 pointer to the frozen matrix);
  `docs/adr/ADR-004-durable-work-transactional-outbox-and-jobs.md` (D3 the DSN
  source referenced); `docs/adr/ADR-005-ingestion-quota-storage.md` (D5 unlisted
  media serving, D10 `0004_storage_locations`, S2 expiring uploads);
  `docs/adr/ADR-006-derivatives-metadata-policy-codec-boundary.md` (S1 geo-privacy
  default "only me"); `docs/adr/ADR-007-domain-model-assets-albums-privacy-social-site.md`
  (D2 the frozen surface × visibility matrix with viewer classes, precedence and
  M0 obligation, D3 the DSN source, D4 the Q-008 checklist in full, S3 the tag,
  category, collection, gallery, group and audience reservations);
  `docs/adr/ADR-008-federation-and-protocol-boundaries.md` (D9 the mapping table
  rewritten against the VZ-AP-001…004 titles);
  `docs/adr/ADR-009-acceptance-platform-fixtures-budgets.md` (S5 Q-027 copied, D11
  the PR that owns each corpus); `docs/adr/README.md` (index Q-ids and ledger IDs
  re-synchronised); `docs/issues/VZ-ISSUE-001.md` (D11 ledger IDs, Outcome and two
  Acceptance bullets); and this plan (D1, D10, D11 PR sequence; S9 counts).
- 2026-09-15: `docs/issues/VZ-ISSUE-001.md` was pushed to the filed GitHub issue
  with `gh issue edit 1 --repo yegamble/vizra --body-file docs/issues/VZ-ISSUE-001.md`
  (the one GitHub write authorized for this pass); exit code recorded in the
  correction-pass report.
- State: DOCUMENTED. Nothing IMPLEMENTED, nothing VERIFIED, nothing committed,
  pushed or merged in this repository. The ADRs are Proposed and bind nothing until
  the owner accepts them.

## Blockers and handoff
Owner inputs this design pass surfaces:

1. **Architecture approval of ADR-001…009** (the Prompt 01 gate) — or amendments.
   Nothing in VZ-ISSUE-001 should start before this, because every PR1 item cites
   an ADR.
2. **A disposable Ubuntu 24.04 amd64 host**, or authorization to provision one,
   for the `install.sh` rehearsal. The meta `boot` lane on GitHub-hosted runners
   is the clean target in the meantime; the owner's arm64 laptop is not a
   substitute (ADR-009).
3. **Q-036 owner-controlled domain** for the AT Protocol Lexicon NSID (needed
   before M6, not M0).
4. **Ruleset application after PR1 lands**, because `ci-required` must exist
   before it can be a required check (ADR-002, Q-032).

Still BLOCKED on external input, unchanged: Q-016 (Backblaze live lane), Q-021
(CSAM provider credentials), Q-022 (ModerateContent credentials), Q-036 (owner
domain).

Next concrete action: **owner architecture approval of `docs/adr/`**, then
`vizra-core` PR1 for VZ-ISSUE-001 as sequenced above.

### Chair corrections after drafting (2026-09-15)
Three passages were corrected by the chair before independent verification:
1. ADR-003: the role enum is `owner > admin > manager > member > guest`, exactly VZ-AUTH-004 and PRODUCT_SPEC.md; the brief's "moderator" label was wrong and the `[to confirm in M0]` marker was removed.
2. ADR-004: `site_id` removed from the `jobs` table sketch. The Q-008 ruling (database-per-tenant, no tenant column in core; the devil's advocate's "tenant field on job rows" was explicitly not adopted) means a job lives in the database of its site and the worker fans out over the site registry's DSNs.
3. ADR-006: GPS reaches search facets in the full profile only where the owner's geo-privacy setting allows (VZ-SEARCH-002 privacy case), the same rule as display; excluded from search in core. Marker removed.
Remaining `[to confirm in M0]` markers, **measured after the correction pass** as
9 occurrences across the ADR set (`grep -c "to confirm in M0" docs/adr/*.md`:
ADR-002 1, ADR-004 2, ADR-005 2, ADR-006 2, ADR-007 1, ADR-008 1; `docs/adr/README.md`
carries one further occurrence, which is the convention's definition and not a
marker). They hide the nine values the brief did not fix: the migrator floor tag,
the retry ladder, the per-kind concurrency and timeout defaults, the quota
defaults, the presign TTL default, the display long-edge default, the thumbnail
sizes, the album depth limit and the ActivityPub actor key size. Each is set at PR
time and recorded in the ADR by amendment. The argon2id parameters are no longer
among them: S7 pinned them in ADR-003 and removed that marker.

### Re-verification (fresh Opus pass, 2026-09-15, after the correction pass)
All 21 items D1–D12 / S1–S9 confirmed resolved with quoted proof (Q-001 and Q-008 text byte-identical to the ratification record; 21-row visibility matrix present with DENY default; VZ-ISSUE-001 body on GitHub identical to the local file modulo one blank line; 89 ledger IDs resolve; all Vidra citations trace to the precedent survey; 9 `[to confirm in M0]` markers as listed). One minor defect found and fixed by the chair: ADR-001 attributed sqlc/Next.js/lucide-react/PostgreSQL/openapi-typescript versions and the SPDX ids to the facts file, which holds neither; the licence-table preamble, the Evidence section and the README marker convention now name `docs/SOURCE_REGISTER.md` §D for those versions and state that SPDX ids stay unverified until the pin lands.
State: ADR-001…009 and this plan are IMPLEMENTED as documents and independently verified for fidelity to the brief, the ratification record and the contract; nothing is product VERIFIED. Next action: owner architecture approval, then vizra-core PR1.
