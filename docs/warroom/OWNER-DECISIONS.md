# Owner decisions

Verbatim record. Add new decisions at the end with their date; never reword an old one.

## 2026-09-20

Recorded verbatim from the session of 2026-09-20. The owner answered two questions put by the chair.

1. **ADR gate.** Question: "ADR-001…009 are still 'Proposed — awaiting owner architecture approval', and VZ-ISSUE-001 lists that approval as a blocker for any component-repo code. Do you approve them so M0 implementation can start?" Answer: **"Approve ADR-001…009 (Recommended)"** — described to the owner as: "ADRs flip to Accepted dated 2026-09-20 on your instruction. The nine '[to confirm in M0]' values … still get set at PR time as planned. Builders start on vizra-core / vizra-user / vizra-search."
2. **Merge policy.** Question: "AGENTS.md says 'do not self-merge without explicit authorization', but a build loop stalls at the first PR … In every option agents commit on branches, push and open PRs — including a PR for the Prompt 00/01 docs that are still uncommitted on main. Who merges?" Answer: **"Verifier-gated auto-merge (Recommended)"** — described as: "A PR merges only when a separate verifier agent that did not write the code passes it with recorded evidence AND ci-required is green. The builder never merges its own work. Release, deploy, DNS, cloud spend and resource deletion stay owner-only." Now in AGENTS.md, "Merge authorization".
3. **Owner request (same session):** implement the Claude Design mockup `Lumen Atlas Search.html`; use Figma to improve the design where photo pages and other pages are missing.

## 2026-11-10

Answers the owner gave while approving the war-room rework plan. Each answer is quoted exactly as the owner chose it; the topic line is the chair's label, not the owner's words.

1. **Design acceptance (inbox 4).** "Accept the first-slice design with the chair's five answers". Consequence recorded with the answer: the CLI password reset pulled into M1 gets a ledger ID through the generator, citing this decision.
2. **Amending ADRs (inbox 4a, 4b, 8a, 8b, 8d).** "Do not approve - I want to rule on each one separately". The five stay five separate inbox items. VZ-MEDIA-001 and M1-B stay blocked until the owner rules on 4a and 8b.
3. **Rulesets (inbox 5).** "Rulesets: apply to all four repos - require ci-required, block force-push and deletion, linear history; no required CODEOWNERS review"
4. **GitGuardian (inbox 4c).** "GitGuardian: I will dismiss the synthetic hits in the dashboard; the check stays non-required"
5. **exiftool (inbox 1).** "exiftool: accept CI-only reproduction for the fixture corpus; no install on my machine"
6. **Disk (inbox 2).** "Disk: the chair may remove worktrees and local branches whose PR is merged, and prune caches it created, when free disk is under 15 GiB"
7. **Stamp key (inbox 10).** "Stamp key: accept "main-process code during collection is trusted-by-review" as a documented residual and open Lane B"
8. **Deploy.** "Autonomous deploy to one disposable rehearsal host that I provide; production deploy, DNS, cloud spend and deleting resources stay owner-only"
9. **Old hardening PRs.** "Triage by the new bar: one final bounded round only for parts that fix an exploitable auth, privacy, data-loss or false-green defect; close the rest into one batched follow-up per repo"
10. **Blocking bar and loop rules.** The owner approved the rework plan, which states the bar as: only findings that are exploitable or wrong in today's tree for privacy, auth, data loss or a false-green product gate block a merge; everything else goes to one batched follow-up item. This line is the approved plan's wording, not a quoted answer.
11. **Who merges a PR that edits a component repo's `AGENTS.md` pin table (asked at tick 259 for vizra-core #16).** "Chair merges #16 now; version-pin table edits in a component AGENTS.md are fine for the chair from now on". Scope as asked: version-pin table rows only; every other edit to `AGENTS.md` or `.claude/` is still merged by the owner.

## 2026-11-11

Rulings the owner gave after tick 260, quoted exactly; the topic line is the chair's label.

1. **Inbox 16: acceptance bullets for VZ-FOUND-002, VZ-FOUND-003, VZ-FOUND-006 and ADR-001.** "Inbox 16: add the missing acceptance bullets to docs/issues/VZ-ISSUE-001.md for the VZ-FOUND-002/003/006 ledger cases listed in the audit. This aligns the issue to the ledger, it does not change the ledger. Also approved: the editorial ADR-001 update to the Go and Echo versions actually pinned."
2. **Inbox 15: Redis in readiness, VZ-FOUND-005.** "Inbox 15: first confirm from ADR-002 and the core code whether Redis carries anything beyond cache (sessions, job dispatch, rate limits). If cache only, /readyz stays 200 degraded and the VZ-FOUND-005 ledger text is amended to say so. If it carries more, stop and tell me what, do not amend anything." Outcome of the check (chair, vizra-core `5f615d7`): Redis carries more than cache, so nothing was amended and inbox 15 stays open with the finding.
3. **How queue 3a, 3b, 3c are briefed, and what a tick must report.** "Write each brief from the full ledger entry, not just the reproduced defect: list every ledger case for the slice's ID and say which the PR closes and which stay open. Each fix needs its test shown failing before the fix or against a controlled mutation (wildcard routes in the contract test, DROP without COLUMN and split lines in migrate-lint, the two missing vendored operations, the three compose/env keys)." "Normal gates apply: independent verifier PASS, green ci-required on the verified SHA, nobody merges their own work, and the pending records PR goes through the same gate. A tick ends with a ledger ID recorded on main, or with the exact cases still missing per ID. Report which."
4. **Queue 14, VZ-DESIGN-001.** "Add to queue 14 that VZ-DESIGN-001 still owes a production-mode browser pass at desktop and mobile plus the CSP mutation, since the user #11 verifier ran neither locally."

## 2026-11-12

1. **Budget grant, VZ-FOUND-002 and VZ-FOUND-003 (inbox 17).** Asked on 2026-11-11: "VZ-FOUND-002 has used 3 of its 4 verifier verdicts, and two open PRs each still need one. Grant extra verdicts?" The owner chose: "Grant 2 more verdicts for VZ-FOUND-002 and 1 more for VZ-FOUND-003, for these two PRs only". The two PRs are vizra-core #18 and vizra-user #12. The answer arrived after #12 had merged on the fourth verdict, so the grant is used by vizra-core #18 only: VZ-FOUND-002 may reach 6 verdicts and VZ-FOUND-003 5. No other number changes.
