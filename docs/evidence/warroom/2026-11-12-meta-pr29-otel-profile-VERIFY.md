# VERIFY — yegamble/vizra PR #29 — VZ-OPS-005 (meta: otel OFF/MANAGED/EXTERNAL)

- SHA: fa06a7a6d6f35cec27d0ef9093dc4c5176d1dbbf (PR head at start and at end)
- Environment: macOS Darwin 25.5.0, Docker Compose locally, fresh clone in mktemp scratch dir (since deleted). Verifier did not write this code.

## Commands
| Command | Exit |
|---|---|
| `python3 scripts/compose-render.py --all --out build/compose-models` (15 shapes) | 0 |
| `scripts/check-compose-topology.py build/compose-models` | 0 |
| `scripts/check-config-coverage.py build/compose-models` | 0 |
| `scripts/check-workflows.py` | 0 |
| `scripts/check-doc-links.py` | 0 |
| `bash scripts/check-generated-ledger.sh` | 0 |
| `docker buildx imagetools inspect otel/opentelemetry-collector:0.139.0` | 0, Digest sha256:8ac5df2a931e9264667b236d65bf7591fa4ba633a7a634e6caa2f0a4fc549c07 (matches) |
| EXTERNAL `docker compose ... -f docker-compose.otel-external.yml config --quiet`, endpoint unset (other ci_overrides set) | 1, "required variable OTEL_EXPORTER_OTLP_ENDPOINT is missing a value" |
| same, with `OTEL_EXPORTER_OTLP_ENDPOINT=https://x.invalid:4318` | 0 |
| E: `docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.otel-managed.yml --env-file env/production.env.example config --quiet` (ci_overrides exported) | 0 |
| `gh run list --commit <sha>` | validate success, ci-required success, headSha = SHA |

## A. Scope
The diff touches exactly the 10 expected files. `.github/required-checks.txt` and the workflows are unchanged. Topology script: one new rule (`otel-mode`) was added; no rule was removed or loosened. The new `known_false_probes` entry exempts only the otel-collector probe `/otelcol --version`. The list was already non-empty, and the existing `known-false-undisclosed` / `stale` rules force operator disclosure. The probe really is false (the image is distroless and its health_check extension can't be reached), and the entry says so. This is honest disclosure, not a hidden gap, so it does not weaken any check.

## B. Rendered models
- OFF (12 shapes, every shape except managed/external; prod-frontend-only has no core services): no otel-collector; api/worker/migrate `OTEL_EXPORTER_OTLP_ENDPOINT=""`.
- prod-otel-managed: the collector is present with `ports: null` and network `default` only (the same network as every other service; there are no host or extra networks). Image is pinned by the confirmed digest. `restart: unless-stopped`, json-file logging 10m×5, no-new-privileges, mem 256m, config bind `read_only: true`. api/worker/migrate = `http://otel-collector:4318`. `user` is not set; the upstream image's default USER applies. The repo has no rule requiring non-root, and I did not inspect the image config.
- prod-otel-external: no collector. The endpoint equals the operator value. Rendering fails without it and succeeds with it (table above).
- collector.yaml: OTLP/HTTP receiver on 0.0.0.0:4318 inside the container, batch processor, `debug` exporter at `verbosity: basic`. There are no credentials and no external exporter. At `basic` the debug exporter logs one summary line per batch (span/resource counts), not span attributes. Request data reaches stdout only if an operator raises verbosity to `detailed`; even then, given the core filter, only the remaining span attributes (method, route, status, service.name) would print.

## C. Mutations (each one restored afterwards; `git status` clean)
1. Publishing the collector port 4318 makes topology fail (exit 1) on `never-published` and `otel-mode`.
2. Dropping the worker endpoint override in MANAGED makes topology fail (exit 1): `otel-mode` worker rendered ''.
3. Adding the collector to the base `core` profile makes topology fail (exit 1): `prod-default rule=otel-mode ... otel=off but a collector rendered` (plus restart/log/healthcheck rules).
4. Removing OTEL_SERVICE_NAME from the env makes config coverage fail (exit 1): `service-key-missing .../worker/OTEL_SERVICE_NAME`. Topology stays at 0, as expected.

## D/E/F
All exit 0 (see table). CI is green on this exact SHA.

## Findings
BLOCKING: none.
FOLLOW-UP:
- F1: the collector healthcheck is known-false; it needs a real health_check probe (already declared in the manifest).
- F2: the collector service sets no explicit `user:`; it relies on the image default.
- F3: no in-repo test shows that a running MANAGED stack actually delivers a span to the collector.

## Ledger answer (VZ-OPS-005)
- **IMPLEMENTED: yes.** Core #20 delivered JSON logs, the metrics endpoint, the OTel exporter and the denylist; this PR delivers the OFF/MANAGED/EXTERNAL deployment profiles, and every clause has an implementation.
- **VERIFIED: no.** The success case "traces exported when enabled" has no evidence of a span arriving at a collector: this PR is render-only, and core's evidence is in-process. evidence_required asks for a "scrape transcript", and an in-process test is not a transcript of scraping a running service. The denylist test is met by core #20 (I did not re-run it here).
- To reach VERIFIED: a stack run (rehearsal host or local compose) with a `curl /metrics` transcript and collector debug-log lines showing received spans in MANAGED mode.

## Not run
Core tests (verified in core #20). Running the stack. Container image USER inspection (image not pulled).

FINAL VERDICT: PASS — SHA fa06a7a6d6f35cec27d0ef9093dc4c5176d1dbbf
