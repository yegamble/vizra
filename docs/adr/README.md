# Architecture decision records

This directory is Vizra's decision record. Together with the ratification record
in `docs/OPEN_QUESTIONS.md` it is the only place where an architecture decision is
binding: `docs/ARCHITECTURE.md` is a narrative overview and defers to these files
where they differ, and `docs/META_REPO.md` describes the target topology that
ADR-002 governs.

**Vidra has no ADRs.** The precedent survey for Prompt 01 records that plainly
(no ADR directory; the substitutes are `M/docs/productionization/*-decision.md`
and the risk register `M/docs/productionization/risks.md:161`), and Vidra's
decisions therefore had to be reconstructed from code and from a risk register
that went stale (nine of seventeen rows — `risks.md:161-175`). Vizra writes the
decision down first, cites the Vidra mechanism it copies or refuses, and names
the ledger entries the decision binds.

## File naming

`ADR-NNN-<slug>.md`, `NNN` zero-padded and never reused; `<slug>` lower-case
words joined by hyphens. Numbers are allocated in the order decisions are drafted,
not by topic.

## Statuses

**Proposed** → **Accepted (owner)** → **Superseded**.

- **Proposed** — drafted by a design pass; not yet binding. ADR-001…009 were Proposed
  on 2026-09-15 and **Accepted by the owner on 2026-09-20** (the Prompt 01 gate). The
  session recorded the owner's act; the question put to the owner and the answer
  given are quoted in `docs/plans/WARROOM-BOARD.md`, "Owner decisions".
- **Accepted (owner)** — the owner approved it. Only the owner moves an ADR to
  Accepted; an agent session never does. Per `AGENTS.md` and
  `docs/DEFINITION_OF_DONE.md`, material architecture changes require human approval.
- **Superseded by ADR-NNN** — replaced. The superseded file stays in place.

**An Accepted ADR is immutable.** Amend it only by a new ADR that states what it
changes and sets the old one to Superseded (wholly) or records an amendment
(partly). Editorial corrections that do not change a decision are allowed and must
say so in the file. A Proposed ADR may still be edited freely until the owner
accepts it.

## Required sections

Every ADR carries exactly these, in this order:

1. **Status** · 2. **Date** · 3. **Context** (why the decision is needed and which
charter/`AGENTS.md` constraint it serves) · 4. **Decision** (the operative rules,
in complete sentences) · 5. **Consequences** (positive, negative, risks, and what
later milestones must not break) · 6. **Precedent** (Vidra mechanisms copied, with
`file:line`; and "Unlike Vidra" gaps, with `file:line`) · 7. **Evidence and
ratification** (the `Q-` ids from the `docs/OPEN_QUESTIONS.md` ratification record
and the facts file behind any version claim) · 8. **Ledger IDs** (entries in
`docs/quality/features.json` this decision binds) · 9. **M0 obligations** (what the
M0 foundation issue must implement, and what is only a schema or constraint
reservation for a later milestone).

Conventions used inside the files:

- Precedent paths use the prefixes of the Prompt 01 precedent survey: **C** =
  `vidra-core`, **U** = `vidra-user`, **M** = the Vidra meta repo. Every line number
  is quoted from that survey; no Vidra file was opened while drafting these ADRs.
- **The M0 foundation issue** means the filed M0 issue
  (<https://github.com/yegamble/vizra/issues/1>, drafted under `docs/issues/`).
- `[to confirm in M0]` marks a value the brief did not fix and that the M0
  implementation PR must supply; it never marks a decision that was taken.
- `[pin at PR time; verify]` in ADR-001 marks a version that neither the 2026-09-15
  facts file nor `docs/SOURCE_REGISTER.md` §D observed; SPDX identifiers are never
  asserted as verified in ADR-001 until the pin lands (see its verification column).

## Index

| # | Title | Status | Q-ids | Ledger IDs |
|---|---|---|---|---|
| ADR-001 | Stack pins and licences | Accepted (owner) 2026-09-20 | Q-003, Q-004, Q-009, Q-010, Q-017, Q-027, Q-034 | VZ-FOUND-001, VZ-FOUND-004, VZ-MEDIA-002, VZ-MEDIA-005, VZ-MEDIA-010, VZ-TOPOLOGY-001, VZ-OPS-005 |
| ADR-002 | Repository, process, release and configuration ownership | Accepted (owner) 2026-09-20 | Q-001, Q-002, Q-008, Q-017, Q-028, Q-032 | VZ-FOUND-001, VZ-FOUND-002, VZ-FOUND-003, VZ-FOUND-005, VZ-FOUND-006, VZ-CI-001, VZ-CI-002, VZ-CI-005, VZ-TOPOLOGY-001, VZ-OPS-001, VZ-OPS-002, VZ-OPS-005, VZ-UPGRADE-001, VZ-UPGRADE-002, VZ-SEARCH-004, VZ-ADMIN-002 |
| ADR-003 | Identity, sessions, CSRF, authorization | Accepted (owner) 2026-09-20 | Q-032, Q-033, Q-039, Q-040 | VZ-AUTH-001, VZ-AUTH-003, VZ-AUTH-004, VZ-AUTH-008, VZ-AUTH-009, VZ-INSTALL-003, VZ-PRIVACY-001, VZ-SECURITY-003, VZ-UPLOAD-010, VZ-ADMIN-USERS-001 |
| ADR-004 | Durable work: transactional outbox and jobs | Accepted (owner) 2026-09-20 | Q-008, Q-028 | VZ-JOBS-001, VZ-FOUND-003, VZ-OPS-002, VZ-OPS-005, VZ-OPS-006, VZ-OPS-007, VZ-SEARCH-004 |
| ADR-005 | Ingestion, quota, storage | Accepted (owner) 2026-09-20 | Q-007, Q-015, Q-016, Q-025, Q-034 | VZ-UPLOAD-001, VZ-UPLOAD-002, VZ-UPLOAD-008, VZ-UPLOAD-013, VZ-QUOTA-001, VZ-QUOTA-002, VZ-STORAGE-001, VZ-STORAGE-002, VZ-STORAGE-004, VZ-STORAGE-014, VZ-BACKUP-001, VZ-BACKUP-004, VZ-MEDIA-008 |
| ADR-006 | Derivatives, metadata policy, codec boundary | Accepted (owner) 2026-09-20 | Q-009, Q-010, Q-034, Q-038 | VZ-MEDIA-001, VZ-MEDIA-002, VZ-MEDIA-003, VZ-MEDIA-004, VZ-MEDIA-005, VZ-MEDIA-009, VZ-MEDIA-010, VZ-UPLOAD-013, VZ-GEO-001 |
| ADR-007 | Domain model: assets, albums, privacy, social, site | Accepted (owner) 2026-09-20 | Q-007, Q-008, Q-018, Q-037, Q-039, Q-040 | VZ-PRIVACY-001, VZ-PRIVACY-002, VZ-PRIVACY-004, VZ-ALBUM-001, VZ-ALBUM-002, VZ-SHARE-001, VZ-FAVORITE-001, VZ-RATING-001, VZ-COMMENT-001, VZ-TAG-001, VZ-CATEGORY-001, VZ-COLLECTION-001, VZ-GALLERY-001, VZ-GROUP-001, VZ-AUTH-004, VZ-TENANT-001, VZ-ADMIN-002, VZ-FOUND-003 |
| ADR-008 | Federation and protocol boundaries (M6 behaviour, M0 constraints) | Accepted (owner) 2026-09-20 | Q-018, Q-025, Q-036, Q-040 | VZ-AP-001, VZ-AP-002, VZ-AP-003, VZ-AP-004, VZ-AT-001, VZ-AT-002, VZ-IPFS-001, VZ-IPFS-002, VZ-UPLOAD-004, VZ-IMPORT-002, VZ-PRIVACY-001, VZ-REPORT-001, VZ-FOLLOW-002 |
| ADR-009 | Acceptance platform, fixtures, budgets, rehearsal path | Accepted (owner) 2026-09-20 | Q-027, Q-028 | VZ-FOUND-007, VZ-FOUND-008, VZ-OPS-007, VZ-CI-003, VZ-INSTALL-001, VZ-BACKUP-002, VZ-TOPOLOGY-007 |

ADR-001…009 were corrected on 2026-09-15 after an independent verification pass
found 21 defects; the chair's rulings (D1–D12, S1–S9) were applied while every ADR
was still **Proposed**, so no accepted decision was amended. The changes are
itemised in the execution plan.

Execution plan for this pass: `docs/plans/2026-09-15-prompt01-architecture.md`.
