# Prompt 01 — architecture and executable foundation
Use with Fable for the design pass; hand the approved plan to Opus or Codex for implementation.

Read AGENTS.md, the product/feature baseline, docs/ARCHITECTURE.md, and the repository state. Produce a short implementation plan and ADRs for the highest-impact decisions. Follow one monorepo/modular-monolith architecture with Go API, worker, and operator CLI, plus Next.js frontend. PostgreSQL is transactional truth; Redis is acceleration; ClickHouse is optional analytics. No Kubernetes, Kafka, custom database, or service split without a measured reason and approval.

Resolve: identity/session/CSRF model; media and derivative lifecycle; many-to-many album membership and privacy rules; durable outbox/jobs; quota/idempotency constraints; storage capabilities; tenant/site model for parity; federation mappings; codec boundary; release/configuration ownership. Define OpenAPI as the API source, sqlc queries/migrations as the database source, and generated TypeScript clients. Pin verified supported dependency versions and preserve licenses.

Choose and record the first acceptance platform early: proposed Ubuntu 24.04 on native AMD64, with separate ARM64 qualification before that support is advertised. Specify resource and fixture baselines; use no production host or paid cloud resources without authorization. Establish a repeatable clean-target rehearsal path now, not at release week.

After architecture approval, implement only the executable foundation: repository structure, real toolchain/version lockfiles, Go and web builds, health/readiness, secure runtime configuration, PostgreSQL migrations, Redis connection, production-mode Compose/images, deterministic fixtures, browser-test environment, and CI. Create docs/quality/COMMANDS.md from commands that actually execute. Include install/doctor scaffolding that performs real checks, not fake success.

Implement a reviewed required-check manifest and an aggregate check that cannot pass when required jobs did not run. Protect workflow/manifest/gate changes; account for PR and merge-queue events. Demonstrate a deliberately broken assertion makes its gate fail, then restore it. Do not use whole-suite skipping, continue-on-error, empty test selections, or missing tools as success. Do not fabricate branch-protection settings when permissions are unavailable: supply the exact required configuration and record that enforcement remains unverified.

Boot the real production-mode stack and test API↔database↔web connectivity from a clean workspace. Record actual commands, revisions, images, counts, and limitations. This foundation is not product or production completion. Close with the next slice plan, not a declaration that Vizra is ready.
