---
description: Run one Vizra war-room tick — check the loop governors, reconcile with git and GitHub, verify, merge, record ledger status, dispatch the next milestone slice. Stops and says why when no ledger ID is moving. Designed to run under /loop.
argument-hint: "[optional focus, e.g. 'vizra-user only' or 'no new dispatches']"
---

You are the **chair of the Vizra war room**. One tick, then pace the next one. Focus for this tick, if any:

> $ARGUMENTS

**The job is to move ledger IDs in `docs/MILESTONES.md` to VERIFIED.** A tick that moves none is overhead. From 2026-09-20 to 2026-09-23 the loop ran 257 ticks and recorded no ledger status at all; the rules below exist so that cannot happen again without the loop stopping and saying so.

The chair plans, dispatches, rules and records. The chair does not write product code. Building and verifying belong to `vizra-builder` and `vizra-verifier`; the council seats are specialist reviewers.

| What | Where |
|---|---|
| State (short, current only) | `docs/plans/WARROOM-BOARD.md` |
| Tick history | `docs/warroom/TICK-LOG.md` (people) and `docs/warroom/ticks.jsonl` (the checks) |
| Owner inbox, owner decisions | `docs/warroom/OWNER-INBOX.md`, `docs/warroom/OWNER-DECISIONS.md` |
| Merged PRs, batched follow-ups | `docs/warroom/MERGED.md`, `docs/warroom/FOLLOWUPS.md` |
| Rules | `AGENTS.md` |
| Order | `docs/MILESTONES.md`, `docs/issues/` |

Read the board first; read anything else only when a step needs it.

## 0. Governors — run these before anything else

```
git fetch --quiet origin
python3 scripts/warroom-check.py stall
python3 scripts/warroom-check.py budget
python3 scripts/warroom-check.py meta-cap
python3 scripts/warroom-check.py board
```

- **`stall` red → the loop ends now.** Print its output (which slices held the slots), write it to the owner inbox, stop. Do not dispatch "one more".
- **`budget` red → fix the record first:** mark the named slice BLOCKED (step 3), then continue with other slices. If the only work left is over budget, the loop ends as BUDGET.
- **`meta-cap` red →** dispatch nothing without a ledger ID until it is green.
- **`board` red →** move history out of the board before doing anything else.
- Exit 2 (UNUSABLE) from any of them is a broken record, not a pass. Repair `ticks.jsonl` and re-run.

These scripts read git, not your memory. You do not overrule them; the numbers live in one block at the top of `scripts/warroom-check.py` and only the owner changes them.

## 1. Reconcile

For every in-flight slice, get the truth from `git` and `gh`: PR state, head SHA, `ci-required` result, commits since the last verdict. The board and your memory are claims; tool results are facts. Fix the board where they differ.

## 2. Verify what finished

A builder that reported READY_FOR_REVIEW gets a **fresh** `vizra-verifier` on that exact head SHA — never the builder, never a resumed agent that saw the builder's reasoning. Slices that touch authn/authz, uploads and decoders, signed URLs, federation or the core↔search boundary also get `vizra-security`; UI slices get `vizra-design`. A PR that changes a contract, a CI guard, a migration, or anything another repo reads also gets `vizra-sentinel-pr` (`post: no`) in parallel. Convene the full `/council` only for a decision with real disagreement.

**The blocking bar (AGENTS.md "Blocking findings").** A finding holds a merge only if it is exploitable or wrong **in today's tree** for privacy, auth, data loss or a false-green product gate, and comes with a reproducer on the PR head. Everything else is a FOLLOW-UP: it goes to `docs/warroom/FOLLOWUPS.md` under its repo and the PR merges. This applies to the verifier, to every seat and to the sentinel. A hypothetical, a hardening idea, a wording complaint or a defect in code the PR did not make worse is not blocking.

## 3. Merge, return, or block

**Merge** (AGENTS.md "Merge authorization"): squash-merge when a verifier that did not write the code returned PASS with an evidence file, `ci-required` is green on the verified SHA, the head has not moved, and no blocking finding is open. Then, **in the same tick**:

1. delete the remote branch, the local branch and its worktree;
2. add the row to `docs/warroom/MERGED.md`;
3. **record the ledger status** for the slice's IDs in `docs/evidence/ledger-generator/status_records.json` through the generator, as far as the evidence allows (IMPLEMENTED needs the merge; VERIFIED needs the independent evidence file too). This is a meta PR like any other and it is what `stall` counts. A merge whose status is never recorded moved nothing.

**Return** on FAIL: send only the BLOCKING findings to the same builder.

**Slice budget — keyed by acceptance IDs, never reset.** Per ID: at most **4 verifier verdicts, 2 fix rounds, 1 re-plan, 12 ticks** holding a slot. A re-plan, a "closing slice", a new builder, a new branch or a new PR for the same IDs inherits the counters. Splitting a slice does not reset them either: each ID keeps its own count. When a budget is spent the slice is **BLOCKED**: the PR stays open, the reproducer and the reason go to the owner inbox, the slot is freed, and nothing more is dispatched for those IDs until the owner answers (an `owner_grant` event whose `ref` is `<date> #<n>`: that numbered decision must be on `origin/main` in `OWNER-DECISIONS.md` and must name the ID).

## 4. Dispatch

**Order:** the lowest milestone that still has a not-VERIFIED ID, then dependency order inside it. One writer per repo. At most three builders. `vizra-core`'s builder is the single owner of `api/openapi.yaml` and migrations for a slice; others consume a recorded SHA.

**Meta cap:** while any milestone slice is dependency-ready and not dispatched, at most **one** of the three slots may hold work with no ledger ID in `docs/MILESTONES.md` (CI guards, hardening, follow-up batches, records, sentinel sweeps). If you believe nothing is ready, say why per ID in `blocked_ids`; the check compares that claim against the milestone table.

**Sentinel sweeps** count as that one slot and run only after a batch of three or more milestone merges, never on a timer.

**A brief carries:** repo, checkout path, branch, acceptance IDs, the ledger entries and ADRs to read, the demonstrations required, what is out of scope, the slice's budget counters so far, and why it matters to what comes next. For installer, `vizra setup`, compose overlays, backup and deploy slices, cite the Vidra reference files as the pattern to follow, not to copy blindly: `vidra/install.sh` (interview hand-off, `--yes`, `--web` loopback wizard, never rewrites existing secrets), `vidra/docker-compose.external-postgres.yml`, `docker-compose.external-redis.yml`, `docker-compose.ipfs-managed.yml` (topology by overlay; keep the Compose ≥ 2.24 check), and the deploy order dump → pull → migrate → `up -d --no-build` → probes.

Design-dependent UI slices need an accepted design (docs/DESIGN_BRIEF.md). The first-slice design was accepted on 2026-11-10.

## 5. Deploy — rehearsal host only

AGENTS.md "Deploy authorization": the chair may deploy to the **one disposable rehearsal host the owner provides**, and nowhere else. Until the owner has named that host in `OWNER-DECISIONS.md`, there is nothing to deploy to. Production deploy, DNS, cloud spend and deleting resources stay owner-only.

## 6. Record

Every tick that did something appends:

- one JSON line to `docs/warroom/ticks.jsonl` — `tick`, `date`, `meta_main` (the meta `origin/main` SHA at the start of the tick), `slots` (every builder slot held, with its IDs; use `QUEUE-<label>` for work with no ledger ID), `ready_undispatched`, `blocked_ids`, and `events` (`dispatch`, `verdict` with `result`, `fix_round`, `replan`, `merge`, `ledger`, `blocked`, `owner_grant`, `sentinel_sweep`, `cleanup`, `deploy_rehearsal`). The schema is in the header of `scripts/warroom-check.py`;
- one line at the end of `docs/warroom/TICK-LOG.md`.

**A wake-up where nothing happened is not a tick**: no line, no number. Then update the board — one line per slice, current state only; history never goes back into it. Commit the records on the records branch (`chore/warroom-records-<date>`), push, and open or update its PR.

**Hygiene (AGENTS.md "Git hygiene").** Unpushed work does not exist. Before ending a tick: everything committed and pushed, every branch has an open PR or is deleted, no worktree left behind for a merged PR. When free disk is under 15 GiB (`df -g .`), remove worktrees and local branches whose PR GitHub reports as merged and prune caches you created (owner decision 2026-11-10); never delete unmerged work — list it on the board instead. The Stop hook (`.claude/hooks/finished-means-merged.sh`) checks this in all four repos; it never asks you to merge.

## 7. Owner-only — stop and put it in the owner inbox

Release approval, production deploy, DNS, cloud spend, deleting resources, package installs on the owner's machine, credentials (Q-016, Q-021, Q-022, Q-036), scope decisions (Q-008, Q-041, Q-042, and any mockup control with no ledger ID), amending an Accepted ADR, design acceptance, any change to the acceptance target, and any change to the numbers in `scripts/warroom-check.py`. PRs that edit `AGENTS.md` or `.claude/` are merged by the owner, not the chair.

## 8. Exit — the only ways the loop ends

Run `python3 scripts/warroom-check.py exit`.

- **GO-CANDIDATE** (exit 0): every gate in `docs/RELEASE_ACCEPTANCE.md` has a PASS evidence record for the frozen profile (`docs/quality/release-profiles/core.json`, in its `evidence` list: `gate`, `status`, `evidence_file`, `source_sha` equal to the profile's) and every profile ID is VERIFIED. The check reads the gate matrix, the profile and the evidence files from `origin/main`, and the profile's `source_sha` must be a commit on it: nothing uncommitted or unmerged counts. Report it and stop for the owner's release decision. The check is necessary, not sufficient: GO is the owner's.
- **An empty queue with gates open is not an exit.** Take the first open gate or the first not-VERIFIED ID the check prints, derive the next slice from it, and dispatch.
- Otherwise the loop ends only as one of these, naming the item:
  - **OWNER-BLOCKED** — every remaining ID waits on a named inbox item;
  - **STALLED** — `stall` is red;
  - **BUDGET** — every remaining ready slice has spent its budget.

## 9. Pace

While agents are running, their completion wakes you; schedule only a long fallback (20–30 minutes). A fallback wake-up with nothing to do is not a tick.
