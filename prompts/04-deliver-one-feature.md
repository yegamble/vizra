# Prompt 04 — daily implementation prompt
Reuse this prompt; change only the acceptance ID or issue.

Implement the next dependency-ready acceptance item in docs/quality/features.json, or the specific issue I supplied. Read AGENTS.md, relevant directory instructions, the item, its execution plan, approved design, and docs/quality/COMMANDS.md. If several items are ready, choose the highest-priority one that closes the current milestone; record the chosen ID. Do not reinterpret the whole project or start a broad audit.

Preflight the tools, services, fixtures, design access, and credentials needed to verify it. Write or update a short plan, then implement the complete vertical slice through real data, Go API/business rules, frontend controls, background work, and operational documentation as applicable. Use existing abstractions and generated contracts. No mock shipping path, unfinished subtask, fake success, or unconnected UI.

Create tests for the user's actual outcome, persistence, permissions, invalid input, loading/error states, retry/concurrency, and recovery when relevant. For a bug, first reproduce it with a failing test. For new critical behavior, show the tests reject a controlled violation where practical. Test the production-mode browser journey rather than only the handler or component in isolation.

Run focused checks while developing and all required affected lanes before handoff. Fix root causes without weakening assertions, skipping required tests, silently changing baselines, or hiding unsupported features. Review migrations, generated-code drift, secrets, logging, and privacy/caching effects. Update the feature ledger, control inventory, and plan with actual evidence.

Use a short-lived branch and one coherent PR. A second writer must use a separate worktree and non-overlapping files. Do not merge or deploy. End with acceptance IDs, exact commands/results and test counts, UI/provider evidence, any blocked or unexecuted checks, branch/PR, and remaining gate. A session ending is not permission to call unfinished work done. Preserve a precise checkpoint rather than asking the user to re-explain the requirement.
