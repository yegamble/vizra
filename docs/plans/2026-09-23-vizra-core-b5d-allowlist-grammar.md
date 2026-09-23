# Execution plan: queue 2p "core B5d" — allowlist the Makefile line grammar (default-deny per line)

Status: IN_PROGRESS (builder). Never VERIFIED by this author.

## Context
- Repo `vizra-core`, branch `chore/m1-anchor-allowlist-grammar` from `origin/main@96d19b3` (#11 merged).
- Source of the ported code: vizra-search `4810048` (search #5, VERIFIED), `scripts/makegate.py`: `decode_makefile`, `makefile_lines`, `keeps_rule_open`/`recipe_lines`, `_strip_comment`, `_dollar_problems`, `_forbidden_char`, `DIRECTIVE_KEYWORDS`, `grammar_problems`; its one-reader probe (POISON / SOURCE / IDENTITY) in `scripts/scripts_test.go`.
- Verifier evidence for search: meta `docs/evidence/warroom/2026-09-23-vizra-search-pr5-closing-VERIFY.md`.

## Acceptance (chair brief)
1. Allowlist grammar is the PRIMARY pre-make control in the anchor and `ci-required-guard` (through the shared `scripts/makefile_pin.py`): every logical line of every pinned makefile is empty / column-0 comment (no continued comment) / column-0 literal assignment (NAME not a directive keyword; values only `$$`, `$(NAME)`/`${NAME}`, reviewed `$(shell …)`) / `.PHONY:` / single-literal-target rule with literal prerequisites / TAB recipe line using only `$$`/`$(NAME)`; plus byte refusals (CR, NUL, control chars, Cf, non-ASCII whitespace). Anything else refused by name with its line number.
2. ONE line reader (`makefile_lines`) for every text reading of the Makefile in the anchor and the guard; POISON, SOURCE, IDENTITY tests ported.
3. Post-make database scan, closure equality and the pin are kept (defence in depth); the named denylist refusals become the second diagnosis.
4. Core's real Makefile fits unchanged (no re-pin). If a real line does not fit: report, do not widen.
5. Docs (AGENTS.md, COMMANDS.md, docstrings) at measured strength; built-in implicit rules a stated residual.

Non-goals: queue 2o (search adopting core's anchor). No change outside `scripts/`, docs and evidence. Makefile unchanged.

## Verification
Test-first; red rows for every out-of-grammar form search covered; C-rows (grammar removed) red and green on 3.81 and 4.3 (own container); `make ci`, both anchors, `ci-required-guard`, `go test -race ./scripts/`, the unit report, `db-scan-probe.py`.

## Progress and evidence
(appended as it runs)

## Blockers and handoff
