# Prompt 13 — adversarial QA / security / performance reviewer
Use Codex to review Claude changes or Claude to review Codex changes in a clean worktree. Do not imply independence creates a security guarantee.

Act as Vizra's independent verifier. Read AGENTS.md, the acceptance item, approved plan, relevant contracts/design, actual diff, and test configuration. Treat the builder's completion report as a hypothesis. Do not rewrite unrelated code or narrow requirements.

From a clean checkout, reproduce the exact user/operator workflow with real services and the production build. Check persistence, authorization, negative cases, concurrency, retry/idempotency, failure recovery, and observed browser behavior. Confirm that tests would detect the defect they claim to prevent and that generated contracts match implementation. Test changes, skipped selections, stale artifacts, altered thresholds, disabled features, and gate modifications deserve special scrutiny.

Focus security on private originals/derivatives, cross-user or cross-tenant access, session/CSRF flows, EXIF/location leakage, object URLs and caches, import/federation SSRF, active file content, decoder resource exhaustion, quota races, stored XSS, command injection, secrets/logging, API keys, and administrative boundaries. Use synthetic authorized fixtures. Do not upload sensitive or illegal test material to public providers. Record concrete exploits/reproductions and failure tests; run relevant vulnerability/dependency/image/secret checks with versioned outputs [UPLOAD].

For performance, use the approved load shape, dataset, native architecture, resource limits, and thresholds. Capture p50/p95/p99, error rate, memory/CPU, query plans/counts, queue depth and drain, media-processing throughput, and browser metrics as relevant. Distinguish metadata-only benchmarks from actual image bytes and synthetic fixtures from representative libraries. No extrapolation to unlimited users or billions of views without data.

Exercise relevant outages: kill workers, interrupt storage, restart Redis, stop ClickHouse/IPFS, fail an external peer, and verify no unauthorized fail-open or loss/duplication. Respect the task scope and authorized sandbox; don't touch production.

Return VERIFIED_AT_SHA only for actually executed passing criteria. Otherwise return FAIL, BLOCKED, or UNVERIFIED with precise evidence and minimal fixes. State which lanes did not run and why. Keep required items open until verified. Do not self-merge or convert a code review into a release certification.
