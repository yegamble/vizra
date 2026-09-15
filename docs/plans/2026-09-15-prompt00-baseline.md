# Execution plan: Prompt 00 — product baseline, atomic ledger, meta-repo design, council

## Context
Base commit: b6d3bc4 (Initial commit) on `main`; working tree carried the untracked build kit (AGENTS.md, CLAUDE.md, docs/, prompts/) and a modified README.md. No application code, CI, compose or component repos exist.
Owner instructions this session: execute prompts/00-scope-and-parity.md; additionally (mid-session) treat `vizra` as a Vidra-style meta repo for `vizra-core`/`vizra-user`/`vizra-search`, mirror Vidra's CI/CD + wizard/CLI install + compose-with-external-services topology, and create a council of `.claude/agents` for business/engineering/user/QA perspectives.
Environment: macOS, Claude Code (Fable 5.1), read access to ~/github/vidra as reference.

## Acceptance (this run)
- Source register updated with URL, version/date, observation date, capability, limitation per source; official sources only; roadmap items excluded; no paid/demo inspection claimed.
- docs/PRODUCT_SPEC.md: two claims (core, full), scope, model, semantics, topology, baseline-completeness gate, first runnable slice + exact test inputs.
- docs/quality/features.json: atomic ledger with the required fields per entry; all PLANNED/UNVERIFIED.
- docs/quality/ui-controls.json: control inventory for the first slice + known controls, UNVERIFIED.
- docs/quality/release-profiles/{core,full}.json manifests.
- docs/OPEN_QUESTIONS.md with conservative proposed decisions.
- docs/MILESTONES.md dependency-ordered + docs/issues/ 8–12 drafted issue bodies (local only; no GitHub writes).
- docs/META_REPO.md; AGENTS.md/ARCHITECTURE.md reconciled to the meta-repo decision.
- .claude/agents council + .claude/council contracts + /council command.
- Non-goals: application code, CI workflows, compose files, GitHub issues/PRs, any VERIFIED status.

## Implementation (artifacts written this run)
- .claude/council/{repo-map,finding-format,protocol}.md; .claude/agents/**/vizra-*.md (15 seats); .claude/agents/README.md; .claude/commands/council.md
- docs/META_REPO.md; AGENTS.md (repository-shape paragraph); docs/ARCHITECTURE.md (repository section)
- docs/SOURCE_REGISTER.md (rewritten); docs/evidence/research-2026-09-15/*.md (4 evidence files); docs/PRODUCT_SPEC.md; docs/quality/features.json (188 entries, generated); docs/quality/ui-controls.json (59 controls); docs/quality/release-profiles/{core,full}.json; docs/OPEN_QUESTIONS.md (Q-001…Q-043); docs/MILESTONES.md; docs/issues/VZ-ISSUE-001…012.md + README; docs/evidence/ledger-generator/ (sources + validator); README.md baseline note; docs/quality/*.example.json removed (superseded)

## Verification
- Research: four parallel official-source research passes (Chevereto editions/features/releases/API; Chevereto admin+user manuals; Flickr help/API; protocol/provider/toolchain docs). Results land in the session scratchpad and are reconciled into docs/SOURCE_REGISTER.md. Fetch failures are recorded as FAILED, not filled from memory.
- Ledger validation: a scratchpad Python generator emits features.json and a check asserts unique IDs, required fields present, every dependency resolves, every profile in {core, full}, statuses PLANNED/UNVERIFIED. Command and result recorded below.
- No application tests exist; nothing here is VERIFIED.

## Progress and evidence
- 2026-09-15: repository state discovered (git status, tree); Vidra reference mechanisms read (install.sh, setup.go interview, compose overlays, meta-ci.yml, ci-required.yml, required-checks.txt, releases/README.md, deploy/README.md, council agents/protocol).
- 2026-09-15: council files, META_REPO.md, AGENTS.md/ARCHITECTURE.md edits written (IMPLEMENTED as documents; UNVERIFIED as process until first council run).
- 2026-09-15: research passes completed — Chevereto editions (32 URLs, 5×404 recorded), Chevereto manuals (73/74 pages, 1×404), Flickr (157-article index, 76 fetched, direct fetch 403 → browser API), protocols/providers (45 URLs, 6 FAILED, 2 partial). No paid/demo/private source inspected.
- 2026-09-15: ledger validation — `cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json` → `OK 188 requirements; core=141` exit 0 (first run exit 1 exposed 5 dependency cycles and 2 core→full violations; fixed in sources and re-run).
- 2026-09-15: profile manifests generated from the ledger (core 141 IDs, full 188 IDs); ui-controls references checked against ledger IDs (0 missing).
- State: all artifacts IMPLEMENTED as documents; every requirement PLANNED/UNVERIFIED; nothing merged; no application code, CI or compose written.

## Blockers and handoff
- Component repositories do not exist; creating them and any GitHub writes need owner authorization.
- Open decisions are in docs/OPEN_QUESTIONS.md; the conservative proposals are applied provisionally and marked.
- Next concrete action after this run: owner reviews OPEN_QUESTIONS.md and the core/full manifests, then Prompt 01 (architecture + executable foundation) starting with VZ-ISSUE-001.
