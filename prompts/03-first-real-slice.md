# Prompt 03 — first complete golden path
Use with Opus or Codex after foundation and first-slice design acceptance.

Read AGENTS.md, the approved first-slice plan, relevant ADRs/design references, and actual verification commands. Implement and verify this exact outcome before adding another subsystem:

A new operator boots Vizra using its published instructions, securely claims the owner account, signs in, uploads a real JPEG/PNG, sees an actual processed thumbnail, opens the image, creates an album, adds the image, changes its privacy, restarts the stack, and sees the persisted state. A second account and an anonymous visitor cannot read the private original, derivative, metadata, album contents, or cached response. Authorized viewing still works.

Build the real migration/sqlc/API/generated client/UI/worker/storage path. Use local storage initially, while preserving the approved storage interface. Validate real bytes, bound decoder and upload resources, reserve/release quota safely, and make finalization idempotent. The original file and database record must survive restart; don't use an in-memory repository or production mock.

Use the approved Figma components/tokens and typed icon registry. Every visible first-slice control must perform its real behavior and show recoverable loading/error states. A drag-and-drop upload is not sufficient without a usable keyboard/file-picker alternative. Surface processing failure instead of leaving an endless spinner.

Test success, malformed/oversized input, denied access, interrupted upload, duplicate finalization, worker failure/retry, expired session, stale UI state, and restart persistence. Run browser tests against the production build and real services; inspect desktop/mobile screenshots and browser console/network errors. Prove the image itself decodes, not just that its URL returns 200. Record test fixtures and hashes where useful.

Exercise the clean-target installation path already established. Add a backup/restore smoke rehearsal for this minimal dataset so recovery is tested before the library grows. Unavailable target infrastructure is a named BLOCKED gate, not silently replaced by a laptop test.

Keep this one focused, reviewable delivery; split into dependent PRs only if necessary without calling the user outcome complete early. Report exact evidence and gaps. Do not proceed to advanced analytics/federation until this golden path is verified.
