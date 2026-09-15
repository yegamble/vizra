# Release acceptance — proposed gates, not executed results

## Declare the claim before testing
Freeze a profile, source SHA, image digests, migration version, supported OS/architecture, required services/providers/integrations, fixture provenance, and measurable performance/recovery objectives. A core-only release cannot be called the finished full product. A missing requirement, undefined threshold, or unverified mandatory environment blocks the relevant claim.

## Gate matrix
| Gate | Required proof |
|---|---|
| Baseline completeness | Every explicit requirement and audited reference obligation reconciled; no silent deferrals or scope deletion. |
| Build and provenance | All artifacts come from the frozen source; migrations and frontend/API contracts match; no untracked developer-state dependency. |
| Clean install | A fresh declared target, actual release images, secure owner claim, no undocumented manual repair. |
| Main user flows | Real upload/decode/view/download, organization, social actions, search, sharing, moderation, import/export, persistence after restart. |
| Privacy and abuse | Allowed and denied users/tenants across originals, derivatives, metadata, counts, caches, embeds, feeds, federation; realistic malicious-input limits. |
| Provider qualification | Actual tests for advertised external providers; distinguish emulator, fixture, native peer, and live-service evidence. |
| Optional topology | Disabled services absent; external endpoints suppress local containers; managed enablement works; invalid config does not silently fork data. |
| Fault recovery | Worker, Redis, database, storage, analytics, and peer failures exercise the documented behavior without privacy fail-open or lost/duplicated actions. |
| Backup/restore | Restore on a separate clean target; verify original checksums, application state, keys, and post-restore functionality. |
| Upgrade/recovery | Prior supported release plus data; failed migration; compatible rollback or proven forward/backup recovery. |
| UI and accessibility | Approved design, actual control effects, icon states, responsive/keyboard checks, browser errors, automated accessibility plus recorded manual review. |
| Performance | Declared dataset/hardware/load and explicit budgets; real media workload separated from metadata-only tests; error/latency/resource evidence. |
| CI integrity | Required jobs really ran on the right revision; required tests collected; no unexplained skips, stale reports, or removed checks. |

## Efficient test scheduling
For each PR, run static/build/generated-contract checks, focused unit/integration tests, and affected production-mode browser cases. Run the broader integration/browser/fault suite on the main branch at an appropriate cadence. Run provider qualification after relevant adapter/config changes and for release; real-provider work needs scoped credentials and spend limits. Rehearse clean install and minimal recovery as soon as the first slice runs, then grow the same harness with each milestone.

Use explicit high-risk combinations plus pairwise coverage for the remaining configuration breadth. Do not claim every possible combination is certified. At minimum, cover private media with storage/CDN/cache; queued publication with privacy change; external PostgreSQL/Redis; managed/external analytics; migration with live data; restore with original-object and key recovery. Test native architectures before advertising them; emulation is not native performance evidence.

## Performance and recovery objectives
During foundation work, record named reference hardware and dataset sizes, request/media mix, concurrency, network assumptions, duration, warm/cold behavior, p95/p99 latency budgets, error rate, queue drain/resource ceilings, and RPO/RTO. Propose and approve numerical budgets before acceptance; do not change them to excuse a failed run. A 100% code-coverage target is not a substitute for functional coverage, realistic load, or privacy evidence.

## Evidence record
Each criterion needs requirement IDs, PASS/FAIL/BLOCKED/UNVERIFIED/NOT_APPLICABLE, exact commands, test totals/skips, source/images/profile/environment, timestamps, fixture identity, and retained artifact references. Manual observations identify the reviewer and tested setup. Provider evidence identifies provider/region/endpoint style or peer/version without leaking credentials. Sensitive URLs and private content must be sanitized.

Use trusted CI-generated reports, provenance, and independent inspection. An agent-authored JSON object saying PASS is not proof. The manifest/gate itself needs regression tests that reject omitted tests, skipped jobs, stale SHAs, empty selections, and erased requirements.

## Verdict
GO requires every mandatory criterion to pass for the frozen profile and the approved scope to be complete. A required FAIL, BLOCKED, UNVERIFIED, missing artifact, or unexecuted environment yields NO-GO with a precise remediation list. Approval to deploy is a separate human decision. A passing rehearsal establishes bounded evidence, not a guarantee of zero bugs or unknown vulnerabilities.
