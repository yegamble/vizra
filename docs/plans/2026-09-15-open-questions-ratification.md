# Execution plan: ratify docs/OPEN_QUESTIONS.md before Prompt 01 (all 43 questions; no acceptance ID — documentation-only edit pass)

## Context
- Repository: `vizra` meta repo, branch `main`. Base commit for this pass: `bf25303` ("initial commit", HEAD at the start of the pass); `b6d3bc4` is the empty root commit. The Prompt 00 baseline plan was written while the docs were still untracked; `bf25303` committed them, so this pass edits tracked files. No code, compose, CI or workflow files exist or were created.
- Trigger: the owner's instruction to review `docs/OPEN_QUESTIONS.md` and ratify the decisions before starting Prompt 01 with `docs/issues/VZ-ISSUE-001.md`.
- Chair: the Fable session. Seats: `vizra-architect`, `vizra-infrastructure`, `vizra-devils-advocate` — Round A blind review of Q-001, Q-002, Q-003, Q-004, Q-017, Q-027, Q-028, Q-032, Q-034, Q-008, Q-018, Q-039, Q-040, plus a bounded Round B between architect and devil's advocate on Q-001 and Q-008.
- One Opus research pass supplied live facts (all fetches 2026-09-15) for Q-003, Q-004, Q-010, Q-017 and Q-034; it wrote nothing to the repository.
- Inputs of record: the chair's ruling (applied here), `docs/evidence/council/2026-09-15-open-questions-ratification.md`, `docs/evidence/research-2026-09-15/ratification-facts.md`.
- This pass is an edit pass only: nothing was committed, pushed, filed on GitHub, deployed or merged. `docs/quality/features.json` was regenerated from its sources, never hand-edited.

## Acceptance
1. Every one of the 43 questions carries a status: `DECIDED 2026-09-15`, `DECIDED 2026-09-15 (modified)`, `DECIDED 2026-09-15 (method); numbers PROVISIONAL until M0 measurement` (Q-028), `OWNER ACTION (mechanism decided 2026-09-15)` (Q-032), or the unchanged `BLOCKED (…)` (Q-016, Q-021, Q-022, Q-036). Q-008, Q-041 and Q-042 additionally carry "; owner may still DECLINE (scope)".
2. Every modified row's decision cell is a ≤ 70-word, pipe-free summary keeping every operative clause name and ending "— full text in the ratification record"; rows ratified as proposed keep their text.
3. The approved-difference register is signed for 2026-09-15 with no "pending" cell left, and carries the two new rows (Q-026 dev tooling, Q-030 legacy native B2).
4. Every document line that cites a Q-id reflects the ruling: `docs/PRODUCT_SPEC.md`, `docs/MILESTONES.md`, `docs/ARCHITECTURE.md`, `docs/META_REPO.md`, `docs/SOURCE_REGISTER.md`, `README.md`, `docs/issues/*`, `docs/quality/release-profiles/{core,full}.json`, `.claude/council/repo-map.md`, `.claude/agents/technical/*`.
5. The ledger regenerates from its sources with `OK 191 requirements; core=141` at exit 0 (190 before the independent-verification fixes below); `schema_version` 3; `unresolved` keeps only Q-016, Q-021, Q-022, Q-028, Q-032, Q-036; `decided` records the ratified ids; the two new full-profile entries (VZ-PRIVACY-004, VZ-FOLLOW-002) exist and core closure still holds (core stays 141).
6. Both evidence files are present under `docs/evidence/`; the four pre-existing research files are untouched.
7. No scope reduction: no requirement removed or narrowed, every "owner may DECLINE" option still open, and both new requirements are additions to the full profile.

Non-goals for this slice: filing issues, creating repositories, writing code/compose/CI, changing acceptance targets, re-litigating any decision, and editing `~/github/vidra`.

## Implementation
Documentation and generator sources only.

- `docs/OPEN_QUESTIONS.md` — ratification line under the title; column header "Conservative proposed decision" → "Decision (proposed → ratified)"; all 43 status cells; 13 rewritten decision cells (Q-001, Q-002, Q-003, Q-004, Q-008, Q-010, Q-017, Q-027, Q-028, Q-032, Q-034, Q-039, Q-040); register sign-off plus two new rows; new "## Ratification record — 2026-09-15" section (Authority, per-question rulings with dissent, Tier C list, BLOCKED list, owner inputs, process note, evidence pointers).
- Ledger generator (`docs/evidence/ledger-generator/`): `core.py` gains the `decided=()` parameter and emits `"decided"` after `"unresolved"`; `build.py` at `schema_version` 3 computes `decided`, adds `summary.decided_questions_referenced`, extends the notice and the final print line; `s0_foundation.py`, `s1_install_ops.py`, `s2_identity.py`, `s3_media.py`, `s4_storage_integrations.py`, `s5_organization.py`, `s6_community.py`, `s7_search_analytics.py`, `s8_admin_brand.py` move 46 question references from `unresolved` to `decided`; `README.md` last-run line.
  - New entries: `VZ-PRIVACY-004` "Named audiences and follower-only visibility" (full; deps VZ-PRIVACY-001, VZ-FOLLOW-002) in `s5_organization.py`; `VZ-FOLLOW-002` "Follow requests with approval and re-evaluation on profile privacy change" (full; deps VZ-FOLLOW-001, VZ-ACCOUNT-001) in `s6_community.py`.
  - Edited entries: VZ-PRIVACY-001 (title/outcome/cases trimmed to core scope), VZ-FOLLOW-001 (privacy case and approval wording), VZ-OPS-007 (declared load corpus, provisional-then-frozen budgets, oldest-pending-job-age case), VZ-SEARCH-004 / VZ-TENANT-001 / VZ-FOUND-004 / VZ-MEDIA-001 (ruling notes), VZ-TOPOLOGY-001 (Compose floor 2.24.4).
- `docs/quality/features.json` — regenerated, not hand-edited.
- `docs/quality/release-profiles/full.json` — VZ-PRIVACY-004 and VZ-FOLLOW-002 added to `required_feature_ids`, count 188 → 190, arm64 line, Q-030/Q-031 evidence_kind strings.
- `docs/quality/release-profiles/core.json` — search topology line, arm64 line, `performance_budgets` and `recovery_objectives` replaced with `PROVISIONAL_UNTIL_M0_MEASUREMENT` objects carrying the Q-028 reference host, measurement points, provisional targets and RPO/RTO wording.
- `docs/PRODUCT_SPEC.md` — counts 188 → 190 (three places), ARM64 note, Q-018 domain line, seven reconciliation rows, §14 ambiguous-behavior row, §15 items 1 and 5.
- `docs/MILESTONES.md` — M0 "Depends on" and ADR phrase, M3 exit criterion, M5 ledger IDs.
- `docs/ARCHITECTURE.md` — repository-tree bracket, search paragraph, favorites/likes sentence, tenancy sentence.
- `docs/META_REPO.md` — search and branding repo rows, redis and search compose rows, port-closure sentence beside the merge-tag rule, Compose floor (two places), installer platform step.
- `docs/SOURCE_REGISTER.md` — new `[RATIFICATION-FACTS]` bullet; `[COMPOSE-MERGE]` minimum-version clause.
- `README.md` — OPEN_QUESTIONS baseline bullet, "Next:" line, full-profile count.
- `docs/issues/VZ-ISSUE-001.md`, `-002`, `-003`, `-006`, `-007`, `-009`, `-010`, `-011` — outcome/acceptance/blocker lines.
- `.claude/council/repo-map.md`, `.claude/agents/technical/vizra-search.md`, `.claude/agents/technical/vizra-infrastructure.md`.
- New evidence: `docs/evidence/research-2026-09-15/ratification-facts.md`, `docs/evidence/council/2026-09-15-open-questions-ratification.md` (byte-identical copies of the session artifacts; md5 `e8610495a866908f8eca6c0196581536` and `e1f9d74755c1806c11732bc7159fe100`).
- This plan, plus one appended line in `docs/plans/2026-09-15-prompt00-baseline.md`.

## Verification
No application code exists, so no application tests can run; nothing here is VERIFIED as product behaviour. What ran:

1. `cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json`
   → `OK 190 requirements; core=141; areas={'foundation': 8, 'ci': 5, 'install': 4, 'topology': 8, 'operations': 8, 'backup': 4, 'upgrade': 2, 'identity': 14, 'upload': 13, 'media': 12, 'storage': 15, 'import': 4, 'activitypub': 4, 'atproto': 2, 'ipfs': 2, 'organization': 24, 'community': 19, 'search': 12, 'admin': 26, 'design': 4}; questions=['Q-016', 'Q-021', 'Q-022', 'Q-028', 'Q-032', 'Q-036']; decided=['Q-001', 'Q-002', 'Q-003', 'Q-004', 'Q-005', 'Q-006', 'Q-007', 'Q-008', 'Q-009', 'Q-010', 'Q-011', 'Q-012', 'Q-013', 'Q-014', 'Q-015', 'Q-017', 'Q-018', 'Q-023', 'Q-024', 'Q-027', 'Q-028', 'Q-029', 'Q-030', 'Q-031', 'Q-033', 'Q-034', 'Q-035', 'Q-037', 'Q-038', 'Q-039', 'Q-040', 'Q-041', 'Q-042', 'Q-043']` — exit 0. One run; no failures.
2. `jq -r '.schema_version, .summary.total, .summary.core_profile, (.summary.open_questions_referenced|join(",")), (.summary.decided_questions_referenced|length)' docs/quality/features.json`
   → `3` / `190` / `141` / `Q-016,Q-021,Q-022,Q-028,Q-032,Q-036` / `34` — exit 0.
3. `jq . docs/quality/release-profiles/core.json >/dev/null; echo core=$?` → `core=0`; `jq . docs/quality/release-profiles/full.json >/dev/null; echo full=$?` → `full=0`.
4. `grep -rn "M2 search" docs` → exit 0 with two hits, neither a live statement: `docs/evidence/council/2026-09-15-open-questions-ratification.md:7` (a verbatim seat report quoting the pre-ruling text, which must not be edited) and this plan's own transcript line, which quotes the command. With `--exclude-dir=council` and this plan excluded, the grep returns nothing (exit 1); the ratified Q-001 row and every doc statement now say M3.
5. `grep -rnE "(≥|>=) ?2\.24([^.]|$)" docs .claude README.md` → one hit only, the same council record at line 42 (a seat's verbatim argument); exit 0. With `--exclude-dir=council`: nothing, exit 1. Live statements read 2.24.4 — CORRECTED after independent verification: this grep cannot match `< 2.24`, and VZ-TOPOLOGY-001's negative case still said `< 2.24`; fixed in the verification round below (`docs/META_REPO.md` ×2, `docs/PRODUCT_SPEC.md` §15, `docs/SOURCE_REGISTER.md`, `docs/issues/VZ-ISSUE-002.md`, `.claude/agents/technical/vizra-infrastructure.md`, and VZ-TOPOLOGY-001 in the generator + regenerated JSON).
6. `grep -c "DECIDED 2026-09-15" docs/OPEN_QUESTIONS.md` → `57`. `grep -cE "^\| Q-0[0-9]{2} \|" docs/OPEN_QUESTIONS.md` → `43`.
7. `grep -rn "PROPOSED" docs/OPEN_QUESTIONS.md` → three lines: the status-vocabulary line (5), the ratification line under the title (3) and the same strike-back sentence inside the verbatim Authority paragraph (69). No row status is PROPOSED.
8. `grep -rn "Echo v4\|Echo (v4)\|echo/v4" .claude docs prompts README.md AGENTS.md` → three hits, none in a council/agent file: `docs/OPEN_QUESTIONS.md:9` (the question text "Echo v4 or v5?"), `docs/SOURCE_REGISTER.md:116` (the recorded kit-vs-docs conflict) and `docs/evidence/research-2026-09-15/research-protocols-providers.md:527` (pre-existing research evidence, not modified). No council/agent file names a version other than v5, so no "Echo (v5)" substitution was required.
9. Evidence copies confirmed byte-identical by md5 against the session artifacts; the four pre-existing research files kept their original mtimes.

Not run / not applicable: no compose render, boot lane, browser journey, provider lane or performance measurement exists yet. Q-028's numbers stay PROVISIONAL until the first M0 measurement run; `docs/quality/COMMANDS.md` does not exist yet, so the commands above are recorded verbatim in this plan.

## Progress and evidence
- 2026-09-15: ruling, research facts and council record read in full; `docs/OPEN_QUESTIONS.md`, the ledger generator sources, the release profiles, the issue drafts and the council files read before editing.
- 2026-09-15: all edits applied in one pass as listed under Implementation; the ledger regenerated once from sources (single run, exit 0, `OK 190 requirements; core=141`).
- 2026-09-15: verification commands 1–9 executed with the outputs recorded above.
- State: IMPLEMENTED as documents; UNVERIFIED as product behaviour; nothing committed, pushed, filed or merged. The ratification is an owner-authorized decision record, not an engineering verification.

## Blockers and handoff
Owner inputs still required before VZ-ISSUE-001 can execute (from the ruling):
1. GitHub organisation/owner and the three repository names (`vizra-core`, `vizra-user`, `vizra-search` assumed).
2. Authorization to create the repositories, to file VZ-ISSUE-001…004, and to apply the rulesets (Q-032).
3. Q-036 owner-controlled domain for the AT Lexicon NSID (needed before M6, not M0).
4. Optional declines still open, none taken here: Q-008 tenancy, Q-041 notes/people tagging, Q-042 messages; RAW (Q-010) stays declined unless the owner adds it.
Still BLOCKED on external input: Q-016 (Backblaze live lane), Q-021 (CSAM provider credentials), Q-022 (ModerateContent credentials), Q-036 (owner domain).

Next concrete action: the Prompt 01 architecture/design pass (ADR-001 stack pins with the Echo v5 + `otelhttp` spike transcript, the Valkey/Redis 7.2 matrix, the pinned libvips build and loader list; the authorization-precedence ADR; the tenancy plumbing checklist), then `docs/issues/VZ-ISSUE-001.md` once the owner confirms the org/repo names and authorizes GitHub writes.

## Independent verification round (fresh Opus pass, 2026-09-15, after the edit pass)
Five defects found and fixed by the chair; nothing else changed:
1. `docs/OPEN_QUESTIONS.md` Q-014 cell said "pending owner sign-off" and Q-026 cell said "Owner to confirm" while both register rows were signed → both cells now read "Approved difference; register row signed 2026-09-15".
2. VZ-TOPOLOGY-001 negative case tested `< 2.24` while the ruling floor is 2.24.4 → `"Compose < 2.24.4 (including 2.24.0–2.24.3) refused by install.sh, deploy, rollback, restore and doctor"` (`s1_install_ops.py`), regenerated.
3. This plan claimed the 2.24 grep proved all live statements; the grep cannot match `< 2.24` → claim corrected above.
4. Q-010's decided HEIC/HEIF decode option existed in no ledger entry and VZ-MEDIA-002 still said "only if approved" → VZ-MEDIA-002 reworded; new full-only entry **VZ-MEDIA-010** (HEIC/HEIF decode-to-JPEG/AVIF, config-gated, OFF by default, no x265; RAW declined) added in `s3_media.py`; added to `full.json` required IDs and to milestone M3; counts 190 → 191 in README.md, PRODUCT_SPEC.md, full.json.
5. Disclosed vocabulary deviation kept: Q-008/Q-041/Q-042 statuses carry "; owner may still DECLINE (scope)".
Re-run evidence is appended below by the chair.

### Re-run evidence after the verification-round fixes (chair, 2026-09-15)
- `cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json` → `OK 191 requirements; core=141; areas={… 'media': 13 …}; questions=['Q-016', 'Q-021', 'Q-022', 'Q-028', 'Q-032', 'Q-036']; decided=[34 ids]` — exit 0.
- `jq` on features.json → `schema=3 total=191 core=141 open=Q-016,Q-021,Q-022,Q-028,Q-032,Q-036 decided_n=34`; VZ-MEDIA-010 `profiles=["full"] deps=["VZ-MEDIA-002","VZ-FOUND-004"] decided=["Q-010"]`.
- `jq . docs/quality/release-profiles/full.json` → exit 0; `required_feature_count=191`, ids=191, VZ-MEDIA-010 present; core.json ids=141, VZ-MEDIA-010 absent.
- `grep -rn "only if approved\|pending owner sign-off\|Owner to confirm" docs/OPEN_QUESTIONS.md docs/quality/features.json docs/evidence/ledger-generator/*.py` → no output.
- `grep -rn '< 2\.24[^.]' docs .claude README.md --exclude-dir=council` → only this plan's own defect narrative (lines quoting the corrected text); no live statement.
- `grep -rnE "(≥|>=) ?2\.24([^.]|$)" docs .claude README.md --exclude-dir=council` → no output.
- Milestone/ledger closure: every ID cited in docs/MILESTONES.md exists in the ledger; every ledger ID appears in a milestone row (VZ-A11Y-001 and VZ-I18N-001 are present; a first regex pass mis-tokenised their digit-bearing names).
- `git status --short | wc -l` → 37 (34 modified tracked files + 3 new paths); `git diff --stat | tail -1` → `34 files changed, 774 insertions(+), 231 deletions(-)`. Nothing committed; commit/push remain the owner's call.

State: documents IMPLEMENTED and independently re-verified as consistent with the ruling; nothing here is product VERIFIED (no code exists). Next concrete action: owner supplies GitHub org/owner + repo names and authorizes GitHub writes; then Prompt 01 design pass (ADR-001 stack pins with the Echo v5 tracing spike, ADR tenant/privacy/search boundaries) and VZ-ISSUE-001.

### GitHub actions after owner authorization (2026-09-15)
- Owner confirmed gh permissions ("you should have gh cli permissions for repo creation/ownership"). `gh auth status` → account yegamble, scopes gist/read:org/repo/workflow. Meta repo remote: https://github.com/yegamble/vizra (PRIVATE); Vidra components live under the same account.
- Created private, README-only repositories: https://github.com/yegamble/vizra-core, https://github.com/yegamble/vizra-user, https://github.com/yegamble/vizra-search (visibility matches the meta repo; content PLANNED).
- Filed VZ-ISSUE-001 as https://github.com/yegamble/vizra/issues/1 (#1) from docs/issues/VZ-ISSUE-001.md. VZ-ISSUE-002…012 stay local per docs/issues/README.md.
- Not done: rulesets/branch protection (Q-032) — the required configuration is a Prompt 01 output; applying a required check before `ci-required` exists would block every merge. Owner inputs 1 and 2 from the ruling are resolved; Q-036 domain and the optional declines remain.
