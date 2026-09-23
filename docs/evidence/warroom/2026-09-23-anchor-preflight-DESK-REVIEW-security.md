# vizra-search PR #5 anchor pre-flight — read-only DESK REVIEW by the `vizra-security` seat

- **Subject:** `scripts/make-integrity-guard.py` at vizra-search `4476ad5` (PR #5), and vizra-core `origin/main@eeeea06`
- **Reviewer:** `vizra-security` seat (agent `a63560b55dd6042a4`), static read only — no Makefile executed, no payload constructed (the verifier had declined payload construction after a safety classifier stopped it; the chair did not re-route it)
- **Date:** 2026-09-23

## Chair ruling (tick 132)

Adopted: the control for "reading the Makefile executes nothing" becomes a **committed digest of the Makefile's bytes** (and of every file make may read — `MAKEFILE_LIST` exactly the pinned set), checked by the anchor BEFORE make is invoked, with a Makefile change mergeable only together with a reviewed pin update — the same discipline as `.github/pinned-steps.yml`. The text-shape scanner is retired or kept only as an early-warning message, never as the control. Search PR #5 gets this as fix round 1 (FINDINGS 1–3 + the "executes nothing" wording); vizra-core gets it as a new slice 2d-B5 (FINDING 4, incl. scrubbing the runner command-file variables in `clean_env`). Dynamic confirmation of FINDINGS 1–2 is UNVERIFIED by design; the digest control makes them moot.

The review follows verbatim.

---

DESK REVIEW — vizra-search PR #5 parse-time pre-flight (`check_parse_time_side_effects`)
Subject: /Users/yosefgamble/github/vizra/vizra-search/scripts/make-integrity-guard.py at 4476ad58aa3fbd7cd70604ad0b94ec10deea6b2d
Also reviewed: /Users/yosefgamble/github/vizra/vizra-core/scripts/make-integrity-guard.py at origin/main (eeeea068)
Method: static read only. No Makefile was executed, no `make -pn` was run, no payload was constructed. Dynamic confirmation is marked UNVERIFIED and reasoned from the GNU Make manual (§3.7 "How make Reads a Makefile", §3.8 secondary expansion / "Secondary Expansion", §5.1.1 recipe echoing under `-n`, §5.7.1 the `+` prefix, §6.3.4 `.RECIPEPREFIX`, §8.1 `$(shell)`).

===============================================================================
Q1 — WHAT THE SCANNER ACCEPTS AND REJECTS (scripts/make-integrity-guard.py)
===============================================================================
`_expansions` (lines 231-263) tokenises the WHOLE Makefile text as one blob:
- `$(`/`${` push an open with the matching closer `)`/`}` (lines 249-252); nested `$( … $(X) )` yields the inner `X` and, separately, the outer body (lines 253-259). Computed names `$($(X))` therefore reach the accept test as body `$(X)`, which is not a plain var → REJECTED. Good.
- `$$` is treated as make's literal-`$` escape and BOTH dollars are skipped (lines 245-247). This is the load-bearing blind spot — see BLOCKER 1.
- Comments and recipe lines are NOT stripped before tokenising, so `$(shell …)` in a comment or recipe is flagged (false-positive-safe; a recipe `$(shell)` genuinely runs under `-n`, so flagging it is correct).
- Accept test (lines 278-295): a `$(…)`/`${…}` body is admitted only if it exactly equals one of 4 pinned `$(shell …)` strings (APPROVED_SHELL_CALLS, 220-225) or matches `_PLAIN_VAR` `^[A-Za-z_][A-Za-z0-9_]*$` (226), with `MAKE`/`MAKEFILES` specially rejected (283-286). Everything else (eval/call/foreach/value/origin/wildcard/file/guile/patsubst/if/…) → REJECTED by default-deny.
- Line loop (296-321) on `text.split("\n")`: tab-prefixed lines are treated as recipes, prefix chars stripped from `@-+ `, `+` rejected (300-306); non-recipe lines checked for include/load directives (308-311), `!=` shell-assignment (312-314), and rule targets whose name is `%`-bearing / a makefile name / `*.mk` / `*/Makefile` (315-321).
- `define`/`endef` bodies: not specially handled, but any literal `$(shell …)` inside is still tokenised → rejected. A `define` body used only via `$(eval …)`/`$(call …)` is dead because eval/call are rejected.
- CRLF: `body = inner.strip()` (279) and `body.rstrip()` neutralise trailing `\r`; tends toward false-positive, not bypass. UNVERIFIED at the margins but low-risk.
Net: for constructs that surface as a literal `$(`/`${` expansion, a `!=`, an include, a `+`-tab-recipe, or a makefile-remake/pattern rule, the allowlist is sound and default-deny.

===============================================================================
Q2 — CONSTRUCT-BY-CONSTRUCT (does the scanner REFUSE / ADMIT / N-A under -pn)
===============================================================================
- `$(shell/eval/call/foreach/value/origin/wildcard/file/guile …)` written literally: REFUSE (accept test, 278-295).
- `!=` shell assignment: REFUSE (312-314).
- `+` recipe prefix, `$(MAKE)`/`${MAKE}`: REFUSE (300-306 for `+`; 283-286 for MAKE).
- `include`/`-include`/`sinclude`/`load`/`-load` and makefile-remake / pattern rules: REFUSE (308-311, 315-321).
- `export VAR := $(shell …)`, `override … := $(shell …)`: the `$(shell …)` is tokenised → REFUSE.
- `vpath`, `.DEFAULT`, double-colon `::` rules, order-only `|` prereqs (alone): make performs no parse-time evaluation for these under `-pn`, so N/A — EXCEPT when combined with secondary expansion (below).
- Computed variable names `$($(X))`: REFUSE (nested yield, 253-259).
- **`.SECONDEXPANSION` + `$$(…)` in a prerequisite: ADMIT.** `.SECONDEXPANSION` appears nowhere in the guard; prerequisites are collected for the closure (prerequisite_closure, 465-504) but their VALUES are never inspected; and `$$(…)` is skipped whole by the tokeniser (245-247). See BLOCKER 1.
- **`.RECIPEPREFIX := <char>`: ADMIT.** Only listed as a builtin var (line 531); never refused. Recipes then no longer start with a tab, so the tab-keyed `+` scan (296-306) and the whole text recipe scan (`logical_recipe_lines`/`check_recipe`) go blind. See BLOCKER 2.

===============================================================================
BLOCKING-BEFORE-MERGE
===============================================================================
FINDING 1: security — needs owner attention: vizra-search anchor, parse-time-execution bypass via secondary expansion, BLOCKER
Severity: BLOCKER   Confidence: high (mechanism); dynamic exec UNVERIFIED (read-only, no crafted Makefile run)
Affected:
  repo: vizra-search
  files: scripts/make-integrity-guard.py:245 (the `$$` skip in `_expansions`), :315-321 (rule check inspects target names only, never prerequisite values), and the absence of any `.SECONDEXPANSION` refusal anywhere in the file
  requirements: none yet — propose VZ-CI-ANCHOR-PARSE
Observed: `_expansions` treats `$$` as a literal-`$` escape and skips both characters (245-247), so a `$$`-escaped expansion inside a prerequisite is invisible to the accept test. `.SECONDEXPANSION` is never named. The rule check (315-321) validates only `m.group(1)` target names; prerequisite text is passed to `prerequisite_closure` for graph-walking but never shape-checked.
Failure: GNU Make expands prerequisites during the target-consideration phase, and that phase runs under `--dry-run`/`-pn` (manual §3.8 "Secondary Expansion"). A `$$`-escaped make function in a prerequisite of a target inside the `ci` goal graph would be evaluated by the anchor's own `make -pn` AFTER `check_parse_time_side_effects` has returned True — which is precisely the "the anchor's own dry-run writes $GITHUB_ENV for the next step" class this pre-flight was added to close. The pre-flight closes the literal-`$(shell)` route the builder found but leaves the secondary-expansion route open. DETAIL WITHHELD per disclosure discipline (no copy-paste Makefile given); the fixer has the construct, the phase, and the admitting lines.
Perspective: operator, developer (a merge gate that can be neutered from inside the file it guards)
Recommendation: smallest fix — refuse `.SECONDEXPANSION` outright in the parse-time scanner (it has no place in a gate Makefile), AND stop skipping `$$` when the following char opens a `$$(`/`$${` inside a non-recipe (prerequisite/assignment) context, or simply refuse any `$$(`/`$${` outside a tab recipe line. Prefer the stronger control in the closing recommendation.
Acceptance criteria: a Makefile containing `.SECONDEXPANSION` is refused with make never invoked; a `$$(…)`-bearing prerequisite on a gate target is refused; the existing 4-pinned-shell-call accept set still passes.
Tests: add cases to the guard's Go/py meta-test harness (scripts/scripts_test.go equivalent) asserting exit 1 and "make was NOT invoked" for (a) a `.SECONDEXPANSION` directive and (b) a `$$`-escaped-function prerequisite; assert the current clean Makefile still passes. Harness exists (scripts test lane); this is a new-case addition, not a new harness.
Cross-repo implications: core: same class, and core has NO pre-flight at all — FINDING 4. user: none. search: none. meta: none.
Challenge: reachability of the second-expansion phase under `-pn` for a prereq that is not on the actual build path is the weak point; if make only second-expands prereqs of goals it would (dry-)build, an attacker still controls the graph by hanging the prereq on `ci`/a lane, so it remains reachable — but the exact `-pn` behaviour on 3.81 vs 4.3 is UNVERIFIED here and should be confirmed dynamically by the verifier in a sandbox before ruling.

FINDING 2: security — needs owner attention: vizra-search anchor, recipe-scan evasion via `.RECIPEPREFIX`, BLOCKER
Severity: BLOCKER   Confidence: high
Affected:
  repo: vizra-search
  files: scripts/make-integrity-guard.py:296-306 (tab-keyed `+` scan), :507-524 (`logical_recipe_lines`, tab-keyed), :717-755 (`check_recipe`: `-` prefix and swallow-suffix), :531 (`.RECIPEPREFIX` listed only as a builtin, never refused)
  requirements: propose VZ-CI-ANCHOR-PARSE
Observed: every recipe-line check keys on `raw.startswith("\t")`. `.RECIPEPREFIX` is only in `_MAKE_BUILTIN_VARS` (531); no code refuses an assignment to it. Note the post-make `check_text` assignment scan (607-611) only watches SHELL/.SHELLFLAGS/MAKEFLAGS/GNUMAKEFLAGS/MFLAGS — not `.RECIPEPREFIX`.
Failure: GNU Make lets a makefile set `.RECIPEPREFIX` to a non-tab character (manual §6.3.4); recipes then begin with that character, not a tab. Every tab-keyed scan here — the parse-time `+` detection AND the `-`-prefix and swallowing-suffix checks in `check_recipe` — sees no recipe lines at all. A `-`-prefixed recipe line (whose failure make ignores, and which `make --dry-run` prints WITHOUT the `-`, so the resolver cannot see it either) then passes every check. That is the exact "swallowed failure invisible to dry-run" hole the guard's own comments (720-738) say text-scanning exists to catch.
Perspective: operator, developer
Recommendation: refuse any assignment to `.RECIPEPREFIX` in the parse-time scanner (a gate Makefile has no need to change the recipe prefix). Prefer the stronger control below.
Acceptance criteria: a Makefile assigning `.RECIPEPREFIX` is refused, make not invoked; clean Makefile still passes.
Tests: guard meta-test: `.RECIPEPREFIX := >` → exit 1, "make was NOT invoked".
Cross-repo implications: core: same gap (no `.RECIPEPREFIX` refusal, and no pre-flight). others: none.
Challenge: `.RECIPEPREFIX` also changes what the resolver/text passes expect, so some checks might incidentally fail first; but nothing GUARANTEES a failure, and default-deny means "might fail elsewhere" is not a control.

===============================================================================
REQUIRED
===============================================================================
FINDING 3: design — the control should be a committed-digest pin, not a grammar model, REQUIRED
Severity: REQUIRED   Confidence: high
Affected:
  repo: vizra-search (and vizra-core)
  files: scripts/make-integrity-guard.py (whole parse-time scanner, 199-327); .github/pinned-steps.yml (pins workflow STEP bodies but NOT the Makefile bytes — confirmed: no makefile/digest/sha256 key present)
  requirements: propose VZ-CI-ANCHOR-DIGEST
Observed: the pre-flight is an allowlist-of-shapes over Makefile TEXT that must perfectly re-implement GNU Make's parser to be sound. BLOCKERS 1 and 2 are two independent points where the text model diverges from make's actual evaluation; the `$(shell)` accept-set and the tab assumption show the surface area. pinned-steps.yml already establishes the pattern of pinning bytes byte-for-byte for workflow steps, but the Makefile itself is not pinned.
Failure: an allowlist-of-shapes will keep growing a tail of "constructs we forgot make evaluates" (secondary expansion, `.RECIPEPREFIX`, and whatever 3.82/4.4 add). Each miss is a silently-neutered merge gate. Modelling a Turing-capable macro language from the outside is the wrong shape of control.
Recommendation (SMALLEST STRONGER CONTROL): gate `make` on the Makefile's BYTES, not its shape. Record a sha256 of the Makefile (and of any file make is allowed to read — here MAKEFILE_LIST must be exactly `[Makefile]`) in a committed pin alongside pinned-steps.yml; the anchor refuses to invoke make unless the on-disk bytes match the pin. Any Makefile change is then only mergeable paired with a reviewed pin update — exactly the discipline already applied to workflow steps. This collapses the entire parser-modelling class (including BLOCKERS 1 and 2) to a constant-time compare and makes `make -pn` no longer security-load-bearing. Keep the environment/`make`-is-a-real-file/resolver checks; retire the text-shape scanner behind the digest.
Acceptance criteria: anchor exits non-zero, make never invoked, when the Makefile bytes differ from the committed digest or when MAKEFILE_LIST is not exactly the pinned single file; a Makefile edit with no paired pin update fails CI; ci-required-guard asserts the digest pin exists and is non-empty.
Tests: meta-test that mutating one byte of the Makefile fails the anchor; that adding an `include` (extra MAKEFILE_LIST entry) fails; that a matching Makefile passes.
Cross-repo implications: core: adopt identically. user/search: search adopts here; meta: fan-in gate references the pin.
Challenge: a digest pin adds friction to every legitimate Makefile edit; rebuttal — that friction is the point (a Makefile change to a merge gate SHOULD require a reviewed pin bump), and it is strictly less friction than chasing every new make evaluation construct forever.

===============================================================================
FINDING 4 (core equivalent, Q4)
===============================================================================
FINDING 4: security — needs owner attention: vizra-core anchor, `make -pn` parse-time execution wholly unmitigated, BLOCKER
Severity: BLOCKER   Confidence: high
Affected:
  repo: vizra-core
  files: scripts/make-integrity-guard.py@origin/main — `main()` calls `resolve_database` (which runs `make -pn`) with NO `check_parse_time_side_effects` step at all; `run_make`/`clean_env` (core 223-240) do not even drop the GITHUB_* command-file vars that the search port added (search 183-196); Makefile@origin/main:22-23 already contains `$(shell git rev-parse …)` and `$(shell date …)`.
Observed: reading only — core main has none of the parse-time pre-flight, the APPROVED_SHELL_CALLS allowlist, or the RUNNER_COMMAND_FILES scrubbing that the search PR introduces. Its anchor invokes `make -pn` directly.
Failure: exactly the exposure the search PR was written to close, unfixed in core: any parse-time-executing construct added to core's Makefile ($(shell …)/$(file >…)/`!=`/`+`/$(MAKE)/remake, plus the two bypasses above) runs during core's OWN anchor `make -pn`, and because core's `clean_env` does not strip GITHUB_ENV/GITHUB_PATH, such a line can write the next (pinned `make`) step's environment after the anchor has passed. Core PR #9 is cited as the origin of this whole design; the merged core main does not yet carry this half of it.
Perspective: operator, developer
Recommendation: port the search PR's mitigation to core — but per FINDING 3, port the digest-pin control rather than the text scanner. At minimum, immediately: add the RUNNER_COMMAND_FILES scrub to core's `clean_env`.
Acceptance criteria: core anchor refuses to invoke make on a Makefile that would execute anything while read; core `clean_env` drops the GITHUB_* command-file vars; core meta-tests cover it.
Tests: mirror the search guard meta-tests in core.
Cross-repo implications: core owns this; search already ahead. meta: fan-in should not treat core `ci-required` as equivalent to search's until core is brought up.
Challenge: none — the absence is direct from the code.

===============================================================================
FOLLOW-UPS (SHOULD / NITs)
===============================================================================
- SHOULD: the 4 pinned APPROVED_SHELL_CALLS (220-225) DO execute real shell (`go env`, `git describe`, `git rev-parse`, `date`) at parse time by design. Benign today and pinned, but this means "reading this Makefile executes nothing else" (the `ok` message, 323-325) is literally false — it executes those four. The message should say "executes only the four pinned shell calls." NIT-adjacent but the guard's honesty about its own boundary is part of why it is trustworthy.
- SHOULD: `_expansions` scans comments too, so a `$(eval …)` in a comment is a hard failure (false positive). Safe, but will surprise a maintainer; consider stripping `#` comments on non-recipe lines before tokenising, only if it does not reintroduce a bypass (be careful: `#` inside a `$(shell …)` argument is not a comment).
- NIT: CRLF handling around the expansion-body match (279) is UNVERIFIED at the margin; add one CRLF fixture to the meta-tests.

===============================================================================
ONE-LINE RECOMMENDATION TO THE CHAIR
===============================================================================
For BOTH repos, replace the grammar-modelling parse-time scanner with a committed-Makefile-digest gate (FINDING 3): pin the Makefile bytes and refuse to run make unless they match a reviewed pin — this closes BLOCKERS 1 and 2 and the whole "constructs make evaluates that we forgot" class at once; do not merge search PR #5 as the sound control on the strength of the text scanner alone, and open a core BLOCKER because core main has no parse-time mitigation at all.

