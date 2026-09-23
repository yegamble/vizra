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
- Commits on `chore/m1-anchor-allowlist-grammar`: `2dab194` (code, tests, fixtures, docs, demo harness; scripts/ tree `925bdc1c…`), `c6170f0` (transcripts). Makefile and `.github/` unchanged; no re-pin.
- Ported (source SHA vizra-search `4810048`): `LogicalLine`, `decode_makefile`, `makefile_lines` (lru_cache), `keeps_rule_open`, `recipe_lines`, `_strip_comment`, `_dollar_problems`, `_forbidden_char`, `DIRECTIVE_KEYWORDS`, `grammar_problems` → `scripts/makefile_pin.py`. Core is STRICTER in one place: a backslash-continued rule/`.PHONY` line is refused by the grammar (search refuses it by name, after). Real Makefile fits unchanged: 56 blank/comment, 11 assignment, 25 phony, 25 rule, 72 recipe.
- Anchor: grammar reported FIRST in `check_makefile_pin` (even alongside read-set problems), make not invoked; by-name checks still run as second diagnosis. Check 11 reports the same grammar via `verify_pin`.
- One reader: every makefile text reading in anchor/check 11/crg consumes `makefile_lines`; `scripts/testdata/one-reader-probe.py` (15 POISON probes, function + file-level AST SOURCE with 20 named non-makefile reads, IDENTITY) green.
- New tests `scripts/grammar_test.go`: `TestEveryOutOfGrammarLineIsRefusedBeforeMake` (80 refusal rows incl. every out-of-grammar form in search's table + 18 directive keywords, 4 controls; anchor + check 11), `TestTheRealMakefileFitsTheGrammar`, `TestTheGrammarRefusesEveryLineReadersCouldSplitDifferently`, `TestTheAnchorReadsTheRecipeMakeReads`, `TestEveryMakefileReaderConsumesTheOneLineReader`, `TestTheOneReaderSourceCheckRefusesAPlantedReader` (8 planted readers). Fixtures: 5 grammar-only makeguard, 2 makefilepin. `db-scan-probe.py` 26 rows (11 post-make rows moved in-process).
- T0 red on main: new tests + fixtures overlaid on `96d19b3` without the implementation → `go test ./scripts/` exit 1, 11 top-level tests FAIL (108 subtests) — `docs/evidence/hardening-b5/b5d/make-3.81-host/T0-red-on-main.txt`.
- Demo `docs/evidence/hardening-b5/b5d/demo.sh`, host GNU Make 3.81: D rows all held (D-rows 84/84); C33–C41 each red (CHECK EXIT 1) and green after byte-identical restore. 4.3 container (`ubuntu:24.04`, `b5d-make43-1790189293`, --rm; image pulled then `docker rmi`'d, no other container used it): D rows held, C33–C37, C41 red/green, both anchors 0, ci-required-guard 0, makeguard fixtures 66 exit 1 / 1 exit 0 (good).
- Measurement: with the grammar removed, 47 of 80 out-of-grammar rows are ACCEPTED outright by the anchor (make run, exit 0); 33 are still refused by another check.
- FINDING (pre-existing, not changed here): a multi-line environment variable whose lines look like `x:` makes the anchor's `-pn` database parse fail CLOSED ("target entr(ies) this guard cannot read as ONE name"). Reproducer: `VZ_B5D_INERT_MULTILINE=$'a\nfor x in y:\n' ./scripts/make-integrity-guard.sh --targets ci` → FAILED; without it → exit 0. False refusal, not a bypass. Hit by exported bash functions in the demo harness; worked around there.

## Blockers and handoff
