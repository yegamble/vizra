# Tool allocation and efficient sessions

## Recommended division of responsibility
Fable 5.1: product scope, architecture tradeoffs, source reconciliation, and difficult cross-cutting plans.
Opus 5: scoped vertical-slice implementation and design-system integration.
Codex Pro: implementation alternative, regression work, independent review of Claude changes, and release rehearsal.
Claude Design: explore and iterate visual direction.
Figma: approve, maintain, and hand off reusable design tokens/components and screen/state references.

This is a proposed workflow using the tools the user says are available, not a benchmark claim that one model is always better. Use actual model names offered in the current account; do not invent CLI aliases, configuration fields, or pricing. Verify current settings from official documentation before scripting them.

## Session settings
Use planning mode for material architectural/specification decisions, then execution mode for the accepted plan. Use normal/standard speed by default; choose reasoning effort appropriate to complexity rather than maximum for every task. For Codex, a practical starting point is medium for bounded work and high for difficult auth, migrations, distributed protocols, or release diagnosis; reserve extra-high for tasks that genuinely need it. Reassess using successful outcomes and reruns, not token count alone [CODEX-PRACTICES].

Keep default sandbox/approval protections initially. Allow routine repository-local build/test work as appropriate, but separately approve package installation, network/provider credentials, cloud spend, destructive operations, production deployment, DNS, and merges. Confirm each tool has real shell/Docker/browser access: a GitHub review-only surface may inspect a diff without executing the application. Use Claude Code CLI or a suitably provisioned Codex environment for actual verification.

## Avoid context and coordination waste
Keep root guidance concise; load relevant specifications on demand. Codex discovers AGENTS.md; CLAUDE.md imports it with @AGENTS.md [CODEX-AGENTS, CLAUDE-MEMORY]. Keep one session per coherent acceptance outcome, write a compact execution-plan handoff, and do not paste the complete project specification for every fix.

Start with one builder and one independent verifier, not a large permanent agent swarm. Add a parallel specialist only for a genuinely independent investigation or file domain. Use separate worktrees, branch names, and test resources. One owner controls shared migrations/OpenAPI contracts for a slice. A reviewer should not approve its own altered tests or loosened gates.

Use targeted checks while iterating, full affected gates for the PR, and broader release gates at appropriate boundaries. Cache dependencies/builds using lockfiles without reusing stale correctness evidence. Reuse the same install/recovery harness and representative media corpus. Run broad parity research once for the baseline, then investigate only relevant changes until the next planned baseline refresh.

When agents repeatedly make the same mistake, add a narrow regression test or CI assertion and only the necessary guidance. More emphatic prose is weaker than a failing test. Claude's official guidance similarly emphasizes executable verification and fresh review [CLAUDE-PRACTICES].
