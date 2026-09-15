# Prompt 14 — exact-release GO / NO-GO
Use with a fresh Codex or Claude session after the selected release manifest is feature-complete.

Perform an independent release rehearsal, not another static code audit. Read AGENTS.md, docs/RELEASE_ACCEPTANCE.md, the immutable release/profile manifest, feature and UI inventories, CI-required manifest, operator docs, and prior failures. Freeze source SHA, image digests, migrations, configuration, profile, fixture provenance, and target hardware/OS. Verify the package being installed is the candidate being assessed.

Use a clean disposable instance of the declared deployment target with no reused development state. Use only authorized infrastructure and test accounts; no production traffic/DNS changes or unapproved cloud spend. Follow the published installation instructions without undocumented manual patches. Test owner claim, sign-in, real upload/processing/view/download, albums/tags/privacy, comments/ratings/favorites, search, moderation, exports/imports, restart persistence, and every remaining mandatory workflow in that profile.

Test local and external-service topology, real AWS/Backblaze and other advertised provider qualification, ActivityPub/AT/IPFS interoperability, and optional ClickHouse behavior according to the frozen matrix. Use risk-based/pairwise combinations for breadth but require explicit high-risk combinations such as private media + CDN/storage and visibility change + queued federation. Do not claim combinations or providers absent from the matrix.

Perform backup/restore to a separate clean target, upgrade from the prior supported release with data, rollback only within the supported schema window, required fault injection, security checks, browser/design/accessibility review, and approved performance workloads. Verify recovery, not merely that scripts exit zero.

Validate required CI contexts actually ran on matching revisions and that required tests were collected with no unexplained skips. Store sanitized evidence durably with exact commands, counts, source/images, environment, timestamps, logs, screenshots/traces, restore checksums, and measured results. Artifact links that already expired cannot support a current claim.

A mandatory FAIL/BLOCKED/UNVERIFIED/missing criterion yields NO-GO. NOT_APPLICABLE requires an approved profile reason and cannot hide a required full-product feature. Deferred full-scope features prohibit calling a core release the completed requested application. Never rewrite the checklist to make the candidate pass.

Deliver: GO or NO-GO for the exact profile/artifacts; evidence matrix; unmet items and smallest corrective actions; supported/unsupported environments/providers; residual risks and limits. Do not claim zero bugs. Do not deploy, merge, or switch traffic. If target credentials/infrastructure are missing, provide the executable preflight/rehearsal command and exact missing input, not fabricated test results or repeated generic audits.
