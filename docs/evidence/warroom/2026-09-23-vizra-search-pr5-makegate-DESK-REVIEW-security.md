<!-- Recorded by the war-room chair, 2026-09-23 (tick 162), verbatim from the vizra-security seat's hand-back
     (agent a63560b55dd6042a4). The seat is read-only and does not write files; the text below is the seat's,
     unchanged except for this header comment. -->

# vizra-search PR #5: makegate security desk review

**Date:** 2026-09-23
**Seat:** vizra-security (application security), read-only desk review
**Subject:** vizra-search PR #5, head `e068e07fed999141a601374bb2b3b6251ede04d6` (a single commit on top of c3b2021)
**Compared against:** vizra-core `29387da` (B5b) and `398ac4f` (#10 round 2), both read with `git show`
**Method:** I ran only `git fetch`, `git show` and `git diff`. I built no Makefiles and ran no mutations or make. I have not checked anything by running it; where a claim depends on how GNU Make behaves, it rests on the manual or on the builder's recorded measurements, and I say so where it matters. No tool output contained instructions.

**Threat model.** A pull request author who can edit any file, including the Makefile and its pin. An earlier workflow step that has already changed the machine is outside the anchor's stated scope. Findings are split by whether they need unreviewed bytes (none found) or need a reviewer to approve a hostile Makefile together with its pin (these are "reviewed-bytes" gaps).

## Q1: are FINDING 2, R-1 and R-2 closed?

All three are closed, and R-3 is closed too.

**FINDING 2 (a sibling file remakes the Makefile while the anchor's make runs): closed.**
- The gate runs its checks in this order, collecting every failure and starting make only if there are none (makegate.py:436-462):
  1. pin and bytes (`check_pinned_bytes`, :299-339);
  2. environment (:369-373);
  3. which `make` binary (:345-366).
- Next, one `make -q` names every pinned makefile as a goal (`remake_probe`, :382-396). Any non-zero exit refuses. A re-hash follows (:459-461).
- This matches manual §3.5 ("How Makefiles Are Remade"). Under `-q`/`-n`/`-t`, make does not remake a makefile that is named as a goal, and `-q` exits non-zero if that goal is out of date.
- Every later anchor make names the pinned files as goals (make-integrity-guard.py:224-225, `name_goals=True`) and re-hashes afterwards (makegate.py:420-426, and :939-940 in the anchor).
- The contract-drift shape check (contract-drift-guard.py:168-169) and the lane test (lane_selection_test.go:54) go through `open_gate`, so the same probe runs before their `--dry-run`.
- The design is sound for a specific reason: the probe asks make its own remake question. That covers every built-in and user rule without modelling any of them.

**R-1 (make started outside the gate): closed**, within the stated limit of the inventory test.
- The two sites that were outside the gate now use it: contract-drift-guard.py:142-178 and lane_selection_test.go:52-61.
- `TestEveryPlaceThatStartsMakeIsGated` (scripts/scripts_test.go:1264-1304) fails on any literal make call in a `.go`, `.py` or `.sh` file other than makegate.py. It skips `docs/`, `testdata/` and `bin/`. The evidence scripts under `docs/` call make but are not run in CI.
- AGENTS.md states the limit honestly: literal calls only; a make started through a variable or a wrapper is left to review.

**R-2 (make still starting after a failed pre-make check; MAKEFILES not scrubbed): closed.**
- The anchor collects the pin, environment, make-binary and environment-override results, then returns before any make process if any of them failed (make-integrity-guard.py:845-872).
- `MAKEFILES` is refused (makegate.py:369-373) and always dropped from the child environment (:86, :115).
- make is started by the real path that was checked (:376-379), not looked up on PATH again.

**R-3 (symlinks and case-insensitive filesystems): closed.**
- A pinned file must be a regular file according to `lstat` (makegate.py:308-315).
- The check for a `GNUmakefile` or `makefile` sibling is case-folded (:191-195).

## Q2: parity with core B5b's closure rule

The answer is yes. A recipe that the gate closure reaches can carry an unscanned literal `-` prefix past makegate and the anchor. This needs reviewed (pinned) bytes. Some search doc sentences read as covering it. See M-1.

## Findings

### FINDING M-1: the gate closure reaches recipes that the text reading never scans

- **Severity:** REQUIRED. Under the chair's "no false-guarantee merges" rule this blocks merging until either the code or the sentences change.
- **Confidence:** high for the code path. That the recipe actually runs relies on manual §10 ("Using Implicit Rules") and §4.6 (phony targets).
- **Affected:**
  - repo: vizra-search
  - files:
    - scripts/make-integrity-guard.py:386-425 (`prerequisite_closure` skips `%` targets at :410-411 and drops `$`-named prerequisites at :413)
    - :620-643 (a closure prerequisite with no explicit rule is only printed as a "note")
    - :646ff (`check_recipe` scans explicit gate-target rules only)
    - makegate.py:256-292 (no pattern-rule, suffix-rule or `.PHONY` check)
  - requirements: VZ-CI-ANCHOR-DIGEST (proposed)
- **Observed:** A lane target can depend on a target that is not phony. That target can be built by a user pattern rule, an old-style suffix rule or a built-in implicit rule. It can also be named through a variable, in which case it drops out of the closure entirely. The recipe that runs is then outside every text reading:
  - A literal `-` prefix on it is invisible to the dry-run, which prints commands without the prefix. The code comment at :649-666 says this itself.
  - makegate refuses `+`, `$(MAKE)` and a leading `$(`/`${` on every tab line. It does not refuse `-`.
  - The only later backstop is `check_expanded_commands` (:352-377), which catches a trailing swallowing suffix and nothing else.
- **Core's closure rule:** B5b requires every gate-closure target to have one explicit rule and to be `.PHONY`. It checks this in the text before make runs, and again against make's own `.PHONY` list after. It also refuses pattern rules. Make does not search implicit rules for a phony target (manual §4.6), so in core every reached recipe is explicit and gets scanned. Search has none of this.
- **Failure:** A reviewed Makefile can move a lane's real work into a rule the closure does not scan. The lane's failure is then ignored and it exits 0, and every anchor reading stays green. This is the same class that core measured live in B5b: `.IGNORE: ci` made `make ci` exit 0.
- **Doc sentences that claim closure coverage:**
  - AGENTS.md:568-570: "the text of every gate recipe may carry no `-` prefix and no `|| true`-family suffix".
  - The `prerequisite_closure` docstring at make-integrity-guard.py:387-394: "the closure is COMPUTED from the rules ... a lane added to `ci` is covered".
  - AGENTS.md:531: "aligned with vizra-core PR #10 and its re-verification". Core has since moved on to B5b.
- **Perspective:** developer, operator.
- **Recommendation:** Port core B5b's closure rule. Every closure target needs one explicit rule, must be `.PHONY` in the text and in make's `.PHONY` list, and pattern rules are refused. In addition (see Cross-repo), refuse a `$`-named prerequisite on any gate-closure rule, and refuse old-style suffix rules. If the code does not change in this PR, then at minimum narrow AGENTS.md:568-570 and the docstring at :387-394 to "explicit rules of the named closure only".
- **Acceptance criteria:** Each of the following, pinned, makes the anchor red with 0 make processes started:
  - a closure prerequisite that is not phony;
  - a pattern rule;
  - a suffix rule;
  - a `$`-named prerequisite on a gate rule.

  The clean Makefile stays green.
- **Tests:** Add rows to scripts/scripts_test.go in its existing mutation idiom (digest before and after, re-pin, expect red, restore byte-identically, expect green). No new harness is needed.
- **Cross-repo:**
  - core: the `$`-named-prerequisite hole appears to be shared. Core's closure has the same drop at make-integrity-guard.py:812 (29387da), and I found no refusal of `$`-named prerequisites elsewhere. UNVERIFIED that no other core check catches it, because I read only core's closure and refusal code.
  - user: none. meta: none.
- **Challenge:** "It needs a reviewer to approve a hostile Makefile, and that is the stated residual." The residual paragraph does say that unlisted constructs run. But the sentence at AGENTS.md:569 lists `-` prefixes in gate recipes as refused. A reviewer who trusts that sentence stops looking, and that is what makes it a false guarantee.

### FINDING M-2: named constructs are refused only in their literal spelling

- **Severity:** REQUIRED. Under the chair's rule it blocks merging until the code or the sentences change.
- **Confidence:** high for the code path. That computed names work as bypasses rests on core's B5b measurement ("a computed `$(I)ORE:` made `make ci` exit 0").
- **Affected:**
  - repo: vizra-search
  - files:
    - makegate.py:238-243 (`_ASSIGN_CONTROLLED_RE` and `_SPECIAL_TARGET_RE` match only a literal name at the start of a line)
    - make-integrity-guard.py:262-320 (`check_resolved` looks at SHELL, `.SHELLFLAGS`, `.ONESHELL` and MAKEFLAGS in make's database, not at `.IGNORE`, `.DEFAULT`, `.EXTRA_PREREQS`, `.RECIPEPREFIX` or `.SECONDEXPANSION`)
- **Observed:** Core refuses these tokens anywhere in a line, in any spelling. It also backs the text check with a check on make's `-pn` database for names that make computes. It refuses a target- or pattern-specific assignment whose variable name contains `$`. Search has none of these, so the following pass makegate:
  - a special target whose name is computed by expansion;
  - a controlled variable (SHELL, MAKEFLAGS, ...) assigned target- or pattern-specifically under a computed name. The global database cannot see such an assignment. Core's docstring measured this for `%: SHELL`.
  - UNVERIFIED: a special target that is not the first word of a multi-target rule.
- **Failure:** A failure-ignoring special target, or a recipe prefix that is not a tab (a computed `.RECIPEPREFIX`, which makes every tab-keyed check blind, makegate's `+` check included), can be approved under a spelling the named-construct list does not match.
- **Doc sentences:**
  - AGENTS.md:530-540: "each refused BY NAME … in every form (target- or pattern-specific, `define`, `private`, `override`)".
  - The same claim in the makegate.py docstring at :27-30 and the anchor docstring at :80-84.
- **Recommendation:** Port core's refusal of these tokens anywhere in a line, its database backstop in the resolver (a `.IGNORE:` target, a `.DEFAULT` entry that has a recipe, a non-empty `.EXTRA_PREREQS`, and `.RECIPEPREFIX`/`.SECONDEXPANSION` in the database), and its refusal of target-specific assignments whose variable name contains `$`. Alternatively, qualify "every form" as "every literal spelling".
- **Acceptance criteria:** A pinned computed-name form of each named construct is red, either before make starts or from the resolver.
- **Tests:** Add mutation rows in scripts_test.go, one per construct.
- **Cross-repo:** core already has this. user: none. meta: none.
- **Challenge:** A computed special-target name is conspicuous in review. That is true, and so is a literal one, yet both repos refuse the literal one by name.

### FINDING M-3: "a recipe line that BEGINS with an expansion" misses single-character references

- **Severity:** REQUIRED. The code fix is one line.
- **Confidence:** high.
- **Affected:** makegate.py:272, which tests only for a leading `$(` or `${`.
- **Observed:** Make also expands `$` followed by a single character, including automatic variables such as `$@`, and it applies the `-`/`+`/`@` prefixes after expansion (manual §5.2 recipe syntax; core measured this in #10 round 2). A tab line that starts with a single-character reference is not refused. The text reading and the dry-run then both miss a `-` produced that way. Core's `_LEAD_REF_RE` (29387da:1101) handles `$X` and refuses automatic variables in that position.
- **Doc sentences:** AGENTS.md:540-542, makegate.py:31-32 and the anchor docstring at :83 all say this form is refused.
- **Recommendation:** Refuse any recipe body that starts with `$` and is not `$$`.
- **Tests:** A pinned mutation row that expects red with 0 make processes.
- **Cross-repo:** core already handles this.
- **Challenge:** This is still a reviewed-bytes construct. But the sentence claims this exact shape is refused.

### FINDING M-4: environment-taken variables are refused only on the anchor path

- **Severity:** SHOULD.
- **Confidence:** medium.
- **Affected:**
  - makegate.py:369-373 (`check_environment` checks MAKEFILES only)
  - contract-drift-guard.py:168 and lane_selection_test.go:54 (callers that open the gate without the anchor's `check_environment_overrides`)
- **Observed:** Make imports environment variables as recursively expanded variables (manual §6.10). `VERSION ?=` and the related variables are then expanded while the Makefile is read. In the contract-drift job, the drift-guard step runs `make -q` and `make --dry-run` before the anchor has refused a planted `VERSION`, `COMMIT` or similar.
- **Failure:** Make evaluates environment-supplied text as make syntax. Only an earlier step can plant it, and in that job the earlier steps are the pinned checkout and setup-go actions, so this falls inside the declared "earlier step" residual. It still contradicts "make runs only on reviewed bytes".
- **Recommendation:** Move the anchor's environment-taken-variable refusal into `open_gate`, or drop those variables in `clean_env` for every caller.
- **Tests:** A row that sets an environment-taken variable and runs the drift guard, expecting "make was NOT invoked".

### FINDING M-5: parity in the other direction (core is missing things search has)

- **Severity:** SHOULD, for core.
- `.POSIX` is refused by search (makegate.py:243, :250). I found no refusal of it in core's anchor at 29387da.
- Search also refuses every leading `$(`/`${` outright, which is stricter than core's resolution approach.
- The `$`-named-prerequisite gap from M-1 appears to be shared by both repos. UNVERIFIED for core; see M-1.

### NITs

- **N-1.** AGENTS.md:558-559 says `ci-required-guard.py` makes "the same byte, symlink, include and sibling checks without running make". It cannot run the remake probe. So the siblings it checks are `GNUmakefile`/`makefile` only; remake sources such as `Makefile.sh` are caught by the anchor alone. The sentence should say which siblings.
- **N-2.** evidence README:10, "every script or test that starts make goes through it", does not mention the literal-call limit of the inventory test that AGENTS.md states.
- **N-3.** The anchor runs the remake probe once, at the start. The real make step relies on nothing touching file modification times between the probe and itself. Only the anchor's own later make runs sit in that window, and they run reviewed bytes. A final `make -q` at the end of the anchor would remove the dependence cheaply.

## Q4: doc sentences checked against the "no false-guarantee merges" rule

| Sentence | Verdict |
|---|---|
| AGENTS.md:517-525 ("Every place … goes through one helper") | Accurate. The stated limit is at "Likewise TestEveryPlaceThatStartsMakeIsGated…". |
| AGENTS.md:530-542 ("each refused BY NAME … in every form … BEGINS with an expansion") | Overclaims (M-2, M-3). |
| AGENTS.md:531 ("aligned with vizra-core PR #10 and its re-verification") | Stale compared with B5b (M-1, M-2). |
| AGENTS.md:546-557 (remake probe and re-hash) | Accurate. |
| AGENTS.md:558-559 ("ci-required … sibling checks") | Ambiguous (N-1). |
| AGENTS.md:563-575 ("What it guarantees, exactly … every gate recipe may carry no `-`") | The first half is accurate. "every gate recipe" overclaims closure coverage (M-1). |
| The residual paragraph on a reviewer approving a malicious Makefile | Accurate, and it correctly says unlisted constructs run. It does not rescue the listed claims above. |
| makegate.py docstring :18-44 | Steps 1, 3, 4, 5 and 6 are accurate. Step 2's "every form" and "BEGINS with an expansion" overclaim (M-2, M-3). |
| makegate.py docstring :46-52 (limits) | Accurate. |
| anchor docstring :26-35, :80-88 | Same verdicts as the matching AGENTS.md sentences. |
| `prerequisite_closure` docstring :387-394 | Overclaims coverage (M-1). |
| evidence README round 2 (:9-22) | The measurements are recorded as measurements, and the lost `%` row and the hung container attempt are disclosed. N-2 only. |

No unreviewed-bytes bypass was found. Every open item needs a Makefile approved together with its pin. M-1, M-2 and M-3 are documented guarantees that the code does not keep; under the chair's rule they gate the merge until either the code reaches B5b parity or the sentences are narrowed.

SEAT VERDICT: NO BLOCKER — SHA e068e07fed999141a601374bb2b3b6251ede04d6
