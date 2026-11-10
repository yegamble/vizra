> **Chair's note (2026-09-23, tick 255).** The vizra-architect seat is read-only and has no Write tool. The chair recorded this file from the seat's hand-back. The text between the markers is copied verbatim, as the security desk review for search #5 was. The chair's rulings on the open questions come after the seat's text.

----- BEGIN FILE -----
# Queue 2o — should vizra-search adopt vizra-core's Makefile anchor? Architect review

- **Seat:** vizra-architect (the technical chair). Read-only desk review plus in-process evaluation. No make process was started: `subprocess.run` and `subprocess.Popen` were stubbed to raise.
- **Code read:** vizra-core `main` = `27cee5417ac51dad041e6f311ba4ca238246563e` and vizra-search `main` = `4810048a5c7c65c6b5134d0ec2fd0dacd5f884c6`, in fresh `gh repo clone`s under the scratchpad, deleted afterwards.
- **Documents read:** AGENTS.md, docs/META_REPO.md, docs/sentinel/RULES.md, WARROOM-BOARD rows 2o/#10/#11/#13/search #5, core pr10/pr11/pr13 VERIFY, search pr5 closing VERIFY, and search pr5 makegate DESK-REVIEW.

## 0. Recommendation

1. **One implementation, owned by vizra-core, vendored into vizra-search** with the existing vendoring tool, a recorded source SHA and per-file digests. This is the same model and direction as the OpenAPI contract.
2. **Do not vendor core's anchor as it stands.**
   - The two anchors share the same grammar and line reader. Beyond that, each is stronger on different axes (§1).
   - Taking core's anchor as-is would remove five search controls that core lacks: every-rule `+`/`$`-led refusal, the environment-word drop, starting make by its checked real path, a re-hash after every make run, and a case-folded sibling check. It would also remove the gate API through which search's other make callers go.
3. **Core hardens first and becomes a strict superset:** F-1, F-3, and a port of search's gate half.
4. **Core then extracts the engine into a self-contained directory** with a small data-only per-repo config, with no behaviour change.
5. **Search then adopts it** through a generalised vendoring tool.
6. **Search #5's eight rounds of escape rows become one regression corpus that ships with the engine.** Both repos run it.
7. **B5c is already closed in core** (§4) and should be struck from 2o.

## 1. How the two anchors actually differ

**Measured, in-process.** Each repo's pre-make checks were run against the other repo's real Makefile, with no process started:
- **search's Makefile under core's checks** (`verify_pin` + `prerequisite_closure` + `check_text`):
  - 0 pin problems and 0 grammar problems;
  - closure of 10 targets;
  - 3 FAIL lines:
    - `Makefile:25 sets SHELL to something other than the approved value` (`/bin/bash`);
    - `Makefile:133 … contract-drift has a recipe line ending || true`;
    - the resulting "root Makefile does not carry BOTH approved assignments".
  - **No closure-rule failure:** every one of search's 10 closure targets already has one explicit rule and is `.PHONY`.
- **core's Makefile under search's makegate:**
  - grammar 0;
  - `reviewed_bytes_problems` 19: `Makefile:11` SHELL (`/usr/bin/env bash`) plus 18 recipe lines that begin with `$(GO)`/`$(SQLC)` (Makefile:61…175).
- **core's Makefile under core's checks:** 0 FAIL, closure of 17 targets.

| Axis | core @27cee54 | search @4810048 | Stronger |
|---|---|---|---|
| Pin file reader | `makefile_pin.py:57-158` | `makegate.py:107-109,169` | Identical shape |
| Line reader | `makefile_pin.py:188-277` | `makegate.py:238-318` | **Identical.** pr13 VERIFY §6: `makefile_lines`, `_continued`, `keeps_rule_open`, `recipe_lines`, `decode_makefile`, `_forbidden_char`, `_strip_comment` all equal |
| Grammar | `makefile_pin.py:280-486` | `makegate.py:406-600` | **Identical.** Core refuses a continued rule/`.PHONY` line in the grammar; search refuses it by name. Same outcome |
| `+` / `$`-led recipe lines | Refused only on gate-closure recipes (`make-integrity-guard.py:1468-1516`); leading `$(NAME)` is resolved after make (`check_expanded_prefixes`, :1413) | Refused on **every** rule, before make (`makegate.py:776-780`) | **search** (core #13 F-1) |
| Rule whose target is a pinned makefile | Accepted by the grammar (pr13 VERIFY F-1) | Accepted by the grammar | Neither refuses it |
| Starting make | `run_make` runs `["make", …]` by a PATH lookup (`make-integrity-guard.py:485-494`) after checking what make is | Starts the checked real path (`makegate.py:854-876, 961-969`) | **search** |
| Re-hash of pinned bytes | Once, at the end (`recheck_pinned_bytes`, :643) | After every make run (`Gate.run`, `makegate.py:1011-1017`) | **search** |
| Environment for make | Fixed scrub list (`clean_env`, :457); environment-taken variables refused only in `--workflow` mode | Scrub list, plus `environment_words ∪ environment_taken` dropped for every make any caller starts (`makegate.py:903-969`) | **search** |
| GNUmakefile/makefile sibling | Exact-name match (`makefile_pin.py:514-518`) | Case-folded (`makegate.py:330`) | **search**, conservative. UNVERIFIED whether macOS make would read a differently-cased sibling |
| Make callers | The anchor only | One gate (`open_gate`, `makegate.py:1026`) for the anchor, `contract-drift-guard.py:145-173` and `internal/httpapi/lane_selection_test.go`; launch inventory `TestEveryPlaceThatStartsMakeIsGated` (`scripts_test.go:1531`) | **search** (structure) |
| Database scan | `parse_database` (:660-761): between markers, fails closed on no database, duplicate or unreadable entries; `.IGNORE`/`.DEFAULT`/`.PHONY`/`.SECONDEXPANSION` backstops | Variables only (`resolve_database`, `make-integrity-guard.py:255-283`) | **core** |
| Closure rules | One explicit rule and `.PHONY` in the text and in make's database; closure equality (`check_db_closure`, :1386); recipe equality (`check_db_recipes`, :1321) | Closure prerequisite with no rule is only printed as a `note` (:652); stated residual (search AGENTS.md:766-773) | **core** |
| Computed names after make | Resolver backstops | Refused by the grammar only | **core** (defence in depth) |
| F-3: environment-origin blocks in the database | Parsed as entries: a false refusal (pr13 VERIFY §8) | Also parsed (the variables loop) | Neither |

**Do the Makefiles need different grammars? No.** The only real differences are these:

- **(a) SHELL literal:** `/usr/bin/env bash` (core Makefile:11) versus `/bin/bash` (search Makefile:25).
- **(b) One swallow exemption in search:**
  - `SWALLOW_EXEMPT` at `make-integrity-guard.py:184-186` and `_EXPANDED_EXEMPT_RE` at :373 cover `contract-drift`'s `go test … || true`.
  - The following `contract-drift-guard.py ran` line gives the verdict.
- **(c) Recipe style:** core's 18 `@$(GO)`/`@$(SQLC)` lines. They cost nothing to rewrite so the body starts with a literal (e.g. `@"$(GO)" vet …`). No bash-4 construct appears in core's Makefile (grep: 0 hits).
- **(d) The gate-target set.**

(a)–(c) are one-line Makefile choices, not language differences. (d) is data.

## 2. Where the implementation lives and how it is consumed

**Recommended: core owns it; search vendors it.**
- **Engine location:** `vizra-core/scripts/makeanchor/`. It holds the pin reader, line reader, grammar, gate (search's structure), the anchor checks (core's text, closure and database layers), the make-launch inventory matcher, and `corpus/`.
- **Search's copy:** vendored byte-identical at the same path. The tool requires `source_path == vendored_path`: `vendor-contract.py:349`.
- **Provenance manifest:** `scripts/ANCHOR-SOURCE.json`, outside the vendored directory, so the directory's git tree SHA is identical in both repos.
- **Why this fits the meta-repo model:**
  - Components stay independent at runtime. No CI step fetches another repo, and search's CI runs offline on in-tree bytes.
  - The engine version is visible in search's diff.
  - The direction matches the existing contract (ADR-002: core owns; search vendors).
- **Bootstrapping:**
  - The engine is invoked by the pinned workflow step `./scripts/make-integrity-guard.sh --workflow`. The literal is identical in both repos (core `.github/pinned-steps.yml:71-72`, search `:48-49`), so the step, the wrapper path and `pinned-steps.yml` do not change.
  - The engine guards the Makefile; the Makefile never invokes the engine as its only home.
  - The engine's own integrity in search is a digest check that the engine does not perform on itself: a Go test in the `test`/`test-noskip` floor lane that compares the vendored bytes to `ANCHOR-SOURCE.json`. This mirrors how `contract-drift` catches in-place contract edits (search AGENTS.md:124-129).
- **R15:** the recorded 40-character source commit plus a per-file sha256, and a check that the pin matches, which R15 requires. `--check --core` (provenance against core `main`) stays a local and verifier step, as it is for the contract.
- **How a fix flows:**
  1. Fix and corpus row in core's engine.
  2. Core PR verified and merged at SHA X.
  3. A search re-vendor PR, produced by the tool: bytes and manifest only, verified mechanically (`--check --core` equals core@X; search lanes green).
- **The window cannot be zero with separate repos.** The invariant we can enforce is narrower:
  - (i) search always runs bytes that exist on core `main` at a recorded SHA, never a fork;
  - (ii) during the window, search is behind by exactly the recorded fix, and has no different implementation;
  - (iii) no release pairs different engine trees (PR 7).
- **Process rule (open question Q6):** the chair dispatches the search re-vendor PR in the same tick as the core merge, and the board tracks the pair as one item.

## 3. Parametrisation

**Per-repo, as data only.** An engine-owned strict reader parses a shape like the pin file's, with unknown keys refused.
- `.github/pinned-makefiles.yml`: unchanged.
- `.github/make-anchor.yml`:
  - `gate_targets` (search adds `ci` for local parity);
  - `swallow_exempt` as exact `(target, written bytes, expanded bytes)` triples, with no regex or wildcard. Search's `_EXPANDED_EXEMPT_RE` becomes exact bytes; `DRIFT_PKGS` is a literal assignment, so the expansion is deterministic.
- **Gate targets must not be a second hand-kept list.** `ci-required-guard.py`, which already reads `pinned-steps.yml`, gains a check: every `make_steps` target is in `gate_targets`, and it fails closed. Keeping that reader in one place follows R4. By reading and grep only (UNVERIFIED by mutation), no test today ties `GATE_TARGETS` (core `make-integrity-guard.py:296-305`, search `:142-152`) to `make_steps`. A new make step whose target is outside `GATE_TARGETS` and outside `ci`'s closure would go unscanned in either repo.

**Never configurable**, i.e. engine code, changed only in core:
- fail-closed on unreadable, empty or zero-match input (R5);
- strict mode chosen only by the `--workflow` argument, never by the environment (R2);
- digest before make; one `make -q` remake probe; re-hash after every run;
- the grammar's five shapes, the forbidden characters, the directive keywords and the refused tokens;
- the one line reader (R4);
- the every-rule `+`/`$`-led refusal and the closure rule (explicit rule, `.PHONY`, database equality);
- the environment scrub and drop lists, `APPROVED_MAKE_DIRS`, and starting make by its real path;
- `SHELL`/`.SHELLFLAGS` values (unified; Q1);
- no skip or allow flags and no environment toggles.

The engine offers no step-identification helper. Byte-equality of steps stays in `ci-required-guard`, and substring identification is banned by R2.

## 4. Where F-1, F-3 and B5c land

- **B5c: already closed in core. Strike it from 2o.**
  - `.POSIX` is in `REFUSED_TOKENS` (`make-integrity-guard.py:371`).
  - `$`-named closure prerequisites are refused at :1193-1205.
  - core #11 verified both at `5488eb0` and `0243f2e` (pr11 VERIFY:297, :353: "`$`-prerequisites and `.POSIX` are refused before make with 0 make processes").
  - B5d then refused both again in the grammar: targets starting with `.` are refused, and prerequisites must be literal words (`makefile_pin.py:326-327`).
  - The board text "M-1 UNVERIFIED in core" is stale.
- **F-1 lands in core PR 1.**
  - Port search's every-rule refusal (`makegate.py:776-780`).
  - Also refuse any rule whose target is a pinned makefile path. That is the only way a non-closure recipe runs under the anchor's `-q`/`-n` (remake phase). Neither Makefile has such a rule today.
- **F-3 lands in core PR 2.**

## 5. PR sequence

**PR 1: vizra-core, "B5e: every-rule recipe refusal (F-1) + text-half corpus"**
- **Scope:**
  - refuse `+`-prefixed and `$`-led (not `$$`) recipe lines on every rule before make;
  - refuse a rule targeting a pinned makefile;
  - rewrite core's 18 `$(NAME)`-led lines so the body begins with a literal;
  - apply the SHELL decision (Q1);
  - re-pin;
  - port search #5's pre-make text rows as table rows in core's suite: grammar rows, named constructs, FINDING 5/9/10/11/14/15 examples, the M-1/M-2/M-3 spellings;
  - correct the comment at `makefile_pin.py:314-321` (R1).
- **Acceptance:**
  - T0: the new rows are red at `27cee54` and green after, with exact counts, including the two pr13 §6 rows and a `Makefile:` rule;
  - differential, in evidence: every search #5 row gets a core verdict at least as strict as search's at `4810048`, with any row where core is weaker listed as a FAIL;
  - real tree green on Make 3.81 and 4.3;
  - `make ci` 0, with unit and integration counts not lower;
  - `db-scan-probe.py` still exercises `check_expanded_prefixes`;
  - R23 retargeting of `mutate.sh`/`rows.py` patterns that named `@$(GO)`;
  - `ci-required` green.
- **Depends on:** nothing. Coordinate with any open core PR that touches the Makefile (re-pin order).

**PR 2: vizra-core, "F-3: database parser ignores environment-origin blocks"**
- **Scope:** read targets only inside `# Files`, and variables only with a makefile, default or automatic origin. Optionally, also run engine-internal make with a `KEEP_ENV` allow-list environment.
- **Acceptance:**
  - the pr13 §8 reproducer (`VZV_NOTE=$'first line\nci: not-a-rule'`) gives exit 1 on `main` and exit 0 after;
  - new `db-scan-probe.py` rows: an environment value carrying `# Finished Make data base`, a `SHELL = …` line and a target-shaped line are not read, on 3.81 and 4.3 output shapes;
  - every existing fail-closed row is still red (no database section, duplicate, unreadable).
- **Depends on:** nothing. Can run in parallel with PR 1 in a separate worktree, since the files overlap only in the anchor.

**PR 3: vizra-core, "gate parity: port search's gate half"**
- **Scope:**
  - one gate API (`open_gate`/`Gate.run`) as the only way the engine starts make;
  - start make by its checked real path;
  - re-hash after every run;
  - `environment_words ∪ environment_taken` dropped for every engine make;
  - case-folded siblings;
  - port `TestEveryPlaceThatStartsMakeIsGated` and `TestTheMakeLaunchInventorySeesEveryListedForm`.
- **Acceptance:**
  - the spawn recorder shows `argv[0]` is the resolved real path;
  - a planted PATH stub is refused;
  - a re-hash failure between two engine make runs is caught;
  - search's M-4 rows (environment-taken variables never reach make) are red on `main` and green after;
  - planted inventory forms are red.
- **Depends on:** PR 1 and PR 2 merged, because they overlap `make-integrity-guard.py`.

**PR 4: vizra-core, "extract engine to `scripts/makeanchor/` + `.github/make-anchor.yml`"**
- **Scope:**
  - move the engine behind the unchanged wrapper `scripts/make-integrity-guard.sh`;
  - data config;
  - `ci-required-guard` imports the engine's pin and config readers (check 11 unchanged in meaning) and adds a check that `make_steps` targets are a subset of `gate_targets`;
  - `corpus/` holds every row as data (Makefile snippet → refused-before-make, refused-after-make, or accepted, with a make-process count), run by core's Go test;
  - CODEOWNERS covers the new directory.
- **Acceptance:** no behaviour change:
  - on the real tree and on every `makeguard` fixture, the anchor's ok and FAIL lines are identical before and after, modulo paths;
  - test counts are equal;
  - the one-reader probe's SOURCE/POISON/IDENTITY lists are retargeted, and a disappearing named read fails (R23);
  - a planted `make_step` target outside `gate_targets` is red;
  - `pinned-steps.yml` and `required-checks.txt` are byte-unchanged.
- **Depends on:** PR 3.

**PR 5: vizra-search, "vendoring tool: a second manifest"**
- **Scope:** generalise `vendor-contract.py`:
  - manifest path per invocation (today hard-coded at :105);
  - commit pathspec per manifest (today `-- api/` at :308);
  - minimum file count per manifest (`MIN_VENDORED_FILES = 2`, :111);
  - keep every refusal;
  - add selftest fixtures for the engine manifest and raise `EXPECTED_CASES`.
- **Acceptance:**
  - the existing 17 fixtures still fire by name;
  - `revendor-demo.sh` gives identical contract-manifest output;
  - each new engine-manifest refusal fires;
  - the lane name `vendor-contract-selftest` (a FLOOR lane) is unchanged.
- **Depends on:** none. Can run in parallel with PRs 1–4.

**PR 6: vizra-search, "adopt core's engine (queue 2o proper)"**
- **Scope:**
  - vendor `scripts/makeanchor/` at PR 4's merge SHA with the tool;
  - point `make-integrity-guard.py`, `ci-required-guard.py`, `contract-drift-guard.py` and `lane_selection_test.go` at the engine's gate;
  - delete `makegate.py`;
  - add `.github/make-anchor.yml` (targets including `ci`; the contract-drift exemption as exact bytes);
  - add the engine-digest Go test in the `test` lane;
  - narrow AGENTS.md:766-773, whose residual is now closed.
- **Acceptance:**
  - `--check --core` shows the vendored bytes equal core@SHA;
  - **differential against `4810048`:**
    - every existing search anchor test row (scripts_test.go mutation rows);
    - `ci-hardening-demo.py` C1–C22, R01–R16 and G1–G6;
    - the grammar and one-reader rows;
    - each gives a verdict the same as or stricter than before, with a table in the evidence and any weaker row counted as a FAIL. Rows assert the outcome (exit code, stage, make count), not the message text;
  - **core-only controls now fire in search:** a non-`.PHONY` closure target, a closure prerequisite with no rule, a closure mismatch, a computed `.IGNORE`;
  - the real tree is green on 3.81 and 4.3, with a closure of 10 targets;
  - a planted edit to a vendored engine byte is red in the `test` lane;
  - **the old engine is run on the PR tree in evidence**, because the PR's own CI runs only the new one;
  - `pinned-steps.yml`, `required-checks.txt` and `FLOOR_LANES` are byte-unchanged;
  - `ci-required` green.
- **Depends on:** PR 4 and PR 5.

**PR 7: vizra (meta), optional**
- **Scope:** a release check. `releases/<tag>.json` records `git rev-parse <tag>:scripts/makeanchor` for core and search and refuses a pair that differs. Add a board or process rule: an engine change is done only when search's re-vendor merges.
- **Acceptance:** a fixture pair with differing tree SHAs is refused.
- **Depends on:** PR 6, and on `releases/` existing (Q5).

## 6. Risks

- **An engine change gates its own PR.**
  - PR 1 changes the Makefile, the pin and the refusal in one commit, or core's own CI goes red.
  - PR 6 swaps the gate that judges it, so its evidence must include a run of the old engine on the PR tree.
- **Required-check names:**
  - Core's six (append-only, build-test, cache-matrix, fixtures, govulncheck, docker-build) and search's eleven, including the FLOOR lane `vendor-contract-selftest`, must not be renamed or removed.
  - New checks go inside existing lanes.
  - The anchor step literal stays the same.
- **Vendoring-tool limits** (§5, PR 5):
  - offline `--check` proves only bytes against the manifest;
  - provenance needs a core checkout, and the tool refuses shallow clones, so it cannot run in CI;
  - `internal/httpapi`'s manifest test covers the contract manifest only.
- **R23 churn:**
  - core's `docs/evidence/hardening-b5` harnesses and `one-reader-probe.py`, and search's AST SOURCE list (28 named reads), all name file paths;
  - PR 4 and PR 6 must report harness-fail counts.
- **CI availability:** earlier rounds were BLOCKED by billing, and local evidence is not CI evidence.
- **Python floor:** the verifier host runs 3.9.6, so the engine must stay 3.9-compatible.

## 7. Rejected alternatives

1. **Keep two implementations plus a cross-repo parity test.**
   - Two readers of one language at repo scale, which is R4 writ large.
   - Drift is found after the fact; that is exactly what produced M-1 and M-2.
   - The test would need the other repo in CI.
2. **Search owns it (its structure is better).**
   - Search is core's contract consumer.
   - Core has more lanes and the post-make layer.
   - Reversing the vendoring direction would make core depend on search.
   - Instead, port search's structure into core (PR 3).
3. **Meta-owned tool.**
   - It creates a cycle: meta pins component tags, and components would pin meta.
   - Component CI must run standalone.
   - Meta has no Python or Go test lanes for it.
   - META_REPO.md §7 gives each repo its own `ci-required`.
4. **A new shared repo, package, submodule or CI-time fetch.**
   - Another repo to release, pin, CODEOWNER and CI.
   - A network dependency in the gate.
   - The engine bytes would sit outside the PR diff.
   - A submodule changes pinned checkout steps.
   - A new repo needs a measured need (AGENTS.md); vendoring gives the same single implementation in-tree.
5. **Vendor core's anchor now, as queue 2o literally says.** It weakens search on five controls and on the gate API (§1).
6. **Per-repo strictness knobs** (allow a leading reference, free-text SHELL, regex exemptions). This is the R2 class; fix the Makefile line instead.
7. **A required lane in search comparing against core `main` live.**
   - It goes red for reasons outside the repo: core's own reasoning for keeping `image-scan` out of `required-checks.txt` (core `.github/required-checks.txt:24-38`).
   - A core push would change search's verdict with no search diff.

Not worth doing in 2o: converging the two `ci-required-guard.py` files (1335 and 810 lines). Their shared part is only check 11 and the pin reader, which PR 4 already shares.

## 8. Open questions for the chair and owner

- **Q1.** Unify both Makefiles on `SHELL := /bin/bash`: one line in core plus a re-pin; it removes a PATH lookup and a config value. Or accept an engine-owned closed set of the two values?
- **Q2.** Accept rewriting core's 18 `$(GO)`/`$(SQLC)`-led recipe lines (e.g. `@"$(GO)" …`) so the every-rule refusal holds with no knob? The alternative is a static pre-make resolver, which is more code and more attack surface.
- **Q3.** Search's `contract-drift` `|| true`: keep it as an exact-bytes exemption in config, or restructure the lane later so the engine carries no exemption mechanism?
- **Q4.** Is an offline digest check plus a non-required `--check --core` enough for the engine, as for the contract? Or does the owner want a required provenance lane that fetches core at the recorded SHA?
- **Q5.** PR 7 now, with a ledger ID proposal `VZ-CI-ANCHOR-PARITY`, or when `releases/` exists?
- **Q6.** Board rule: a core engine PR and its search re-vendor PR are tracked as one item, and the re-vendor is dispatched in the same tick as the core merge?
- **Q7.** Strike B5c from 2o and correct "M-1 UNVERIFIED in core" (§4).
----- END FILE -----

## Chair's rulings (tick 255)

These are engineering rulings within the war room's remit. None changes the acceptance target, release scope or spend.

- **Recommendation accepted.** One engine, owned by core in `scripts/makeanchor/` and vendored into search, with core first becoming a strict superset. Queue 2o is split into **2o-1 … 2o-7**, following §5.
- **Q1:** unify on `SHELL := /bin/bash`, one line in core, in PR 1 with the re-pin. This removes a PATH lookup and a config value.
- **Q2:** yes. Rewrite core's 18 `$(NAME)`-led recipe lines so each body starts with a literal. No pre-make resolver, and no knob.
- **Q3:** keep the one exact-bytes exemption in config for PR 6. Restructuring the `contract-drift` lane so the engine carries no exemption mechanism is queued as a later follow-up; it is not a blocker.
- **Q4:** an offline digest check plus a non-required `--check --core`, the same as the contract, which is the model the owner already accepted. If the owner wants a required provenance lane that fetches core, that goes in the owner inbox; it is not assumed.
- **Q5:** PR 7 waits until `releases/` exists. No new ledger ID is proposed now; that would be a scope decision, which is the owner's.
- **Q6:** yes. A core engine PR and its search re-vendor PR are tracked as one board item, and the re-vendor is dispatched in the same tick as the core merge.
- **Q7:** yes. B5c is struck from 2o, and the board text "M-1 UNVERIFIED in core" is corrected: core #11 verified it at `5488eb0`/`0243f2e`.
- **Order under "one writer per repo":**
  - search PR 5 can start now;
  - core PRs 1 and 2 start after core #14 merges. They are separate worktrees, and PR 2 can run in parallel with PR 1 only if a second core writer is acceptable; the default is one at a time;
  - core PR 3, PR 4 and search PR 6 follow in sequence.
