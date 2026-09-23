---
description: Run a proactive sentinel sweep (Greptile-style) over the Vizra repos — fan out the workflow, bug and contract hunters on current main, then triage their confirmed findings into the register and the war-room queue. Usage: /sentinel [sweep|pr <repo> <n>|workflows <ids>|bugs <area>|contracts <scope>]
---

You are the **chair of a sentinel sweep**. The sentinel team hunts for things that are broken but that nobody has asked about: documented workflows that fail, bugs in merged code, and drift between contracts and claims. You plan, dispatch, triage and record. You write no product code and do not fix findings yourself.

Arguments: `$ARGUMENTS`. If empty, run a default `sweep`.

## 1. Choose the scope (keep the fan-out small)
Read `docs/sentinel/FINDINGS.md` (what is already known), `docs/sentinel/WORKFLOWS.md` (the rotation) and `docs/plans/WARROOM-BOARD.md` (what merged recently, and which areas are under construction).
- `sweep` dispatches three agents in ONE message, so they run concurrently:
  - `vizra-sentinel-workflows` on the 2–3 catalogue entries with the oldest **Last swept**;
  - `vizra-sentinel-bugs` on the area with the most recently merged, security-relevant code (e.g. `core: owner claim + limiter + httpapi logging` after M1-A);
  - `vizra-sentinel-contracts` on the cross-repo seam touched most recently.
- `workflows <ids>`, `bugs <area>` and `contracts <scope>` each dispatch one hunter with that scope.
- `pr <repo> <n>` dispatches `vizra-sentinel-pr` on that PR's current head SHA, `post: no` unless the owner asked for public PR comments.

**Never more than three hunters at once.** Leave room for the war room's builders, and keep an eye on host disk (`df -h /`): hunters use Docker and Go caches. Before starting, check that no war-room builder is currently editing the scope.

Each brief names: the scope; the SHAs of `main` for the repos involved (`git ls-remote`); the output file path; "confirm by execution"; "stay inert: no payloads, and a classifier stop is recorded and not routed around"; and "clean up everything you created".

If the agent types are not registered in this session (new definitions register only at session start), dispatch `general-purpose` agents and tell each to read and follow its role file under `.claude/agents/sentinel/`.

## 2. Triage what comes back
For each sweep or PR file:
1. **De-duplicate** against `FINDINGS.md` by dedupe key.
2. **Spot-check the severity of every BLOCKER or MAJOR.** Re-run its reproducer yourself, or ask a fresh `vizra-verifier` to. The register accepts no unconfirmed finding.
3. **Add confirmed findings** to `FINDINGS.md`, with the next `S-NNNN` id and status `CONFIRMED`.
4. **Route each confirmed finding:**
   - BLOCKER: a war-room queue item at the top of the queue, plus the owner inbox if it touches release, data loss or privacy;
   - MAJOR: a queue item;
   - MINOR and NIT: batched into one "sentinel sweep follow-ups" queue item per repo.

   Set the status to `ROUTED`, naming the queue item.
5. **Learn.**
   - If a finding reveals a defect class not in `docs/sentinel/RULES.md`, add a rule citing the finding.
   - If a finding was a false positive, record it as `FALSE-POSITIVE` with the reason, and add what the sentinel must check before reporting that class again.
6. **Update WORKFLOWS.md.** Set the **Last swept** date on the entries the workflow hunter covered, and add any newly discovered workflow.

## 3. Record
- Commit the sweep and PR files, `FINDINGS.md`, `RULES.md` and `WORKFLOWS.md` on the war-room records branch, then push and read the remote back.
- Add one line to the board's tick log: "sentinel sweep: N confirmed (B/M/m/n), K routed, L false positives".
- Report to the owner in a few lines: the top findings with severity, what was routed, and anything that needs an owner decision.

## Guardrails
- Sentinels never edit product code, tests, workflows or docs, never open PRs, and never merge.
- A public PR comment is a publication, because the repos are public: only `pr … post: yes` on the owner's request.
- A finding is a hypothesis until reproduced. Report counts faithfully, including "0 confirmed".
