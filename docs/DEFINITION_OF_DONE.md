# Definition of done

## Task-level evidence
Each acceptance item has a stable ID, explicit behavior and failure cases, dependencies, affected interfaces, authorization requirements, and tests that examine actual outcomes. Implemented code is not yet verified behavior.

A completed slice includes its schema/queries and generated contracts, Go business/API implementation, real frontend interaction, negative/permission/concurrency tests where applicable, operational behavior, and docs. There must be no TODO, stub, mock transport, placeholder image/icon, unsupported control, fake success, or manual database patch on the shipping path.

Test the production-mode stack with real PostgreSQL/Redis and actual media processors for relevant integration/E2E cases. Unit doubles are useful but cannot substitute for integration proof. Provider emulators and protocol fixtures are not the same as external interoperability tests. Browser engine automation is not the same as testing every physical device.

Evidence records source commit and image digests, configuration profile, timestamp, environment/hardware, fixture provenance, commands, exit codes, passed/failed/skipped/collected counts, and artifact references. Link requirements to test IDs; retain failure traces, not only successful screenshots. An unrelated old green CI run cannot certify new code.

## Fail-closed gates
The required-check manifest is reviewed independently from implementation. CI must detect missing or unexpectedly skipped jobs/tests, workflow parse problems, and a manifest that has silently lost requirements. A required skipped/cancelled/timed-out/missing lane blocks its release. Legitimate NOT_APPLICABLE decisions require explicit profile/reason and must not be used to hide an advertised capability.

The aggregate merge check must run on every applicable PR and relevant merge queue event. Required contexts must be configured in repository rules; an untriggered workflow must leave merge blocked, not invisible. Protect workflows, gate scripts, release manifests, migrations, and privacy/auth modules with owner review. GitHub-hosted code review is not itself proof that commands ran.

Use lint, formatting, typecheck, generated-code drift detection, Go unit/race/integration suites, frontend/component tests, production build, browser E2E, accessibility, visual review, security checks, and deployment/recovery lanes according to the affected scope. The full release lane is not replaced by changed-files-only testing.

## Review and authority
A separate reviewer reproduces critical paths from a clean checkout and treats the implementation summary as untrusted. Review changes to tests and gates with the same skepticism as production code. Human approval is required for material architecture/scope changes, security exceptions, release, production deployment, DNS changes, paid provisioning, and destructive operations.

A clean report may say READY_FOR_REVIEW, VERIFIED_AT_SHA, or MERGED. Only a completed release rehearsal can recommend GO for its exact declared profile. A text file, coverage percentage, agent self-rating, or polished screenshot cannot certify production readiness.

## Session closeout
Report: acceptance IDs; changes; exact executed checks/results; checks not run and why; real UI/provider evidence; remaining defects; branch/PR; next action. Checkpoint unfinished work rather than concealing it. Preserve full required scope even when only one slice is complete.
