# Prompt 15 — resume and choose the next bounded task
Use at the beginning of a new coding session; no whole-project reprompt needed.

Read AGENTS.md, the active milestone, docs/quality/features.json, the latest relevant execution plan, current branch/PR status, and recent CI evidence. Discover actual repository instructions. Do not re-audit the entire repository or trust an old narrative summary over the current tree.

Identify the smallest dependency-ready unverified acceptance item that advances the current milestone. Prefer completing or repairing an in-progress slice over starting unrelated features. If an item is blocked on a previously documented external input, do not repeat unsuccessful setup attempts without new information. Preserve the blocker and select independent in-scope work when possible.

State the selected ID, the expected user-visible outcome, and the evidence needed. Then follow Prompt 04 and the relevant specialist addendum. Read only relevant files, use available generated contracts/design context, and implement/test one coherent delivery. Avoid parallel agents editing shared schema/contracts or the same working tree.

Keep scope and release requirements unchanged. Record exact test outcomes, current artifacts, unresolved defects, and the next action in the execution plan before closing. Report READY_FOR_REVIEW or a precise blocked/unverified state. Do not claim the project is complete because the current session's changes compile.
