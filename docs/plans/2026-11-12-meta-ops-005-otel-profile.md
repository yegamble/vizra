# Execution plan: VZ-OPS-005 (meta half): otel profile OFF / MANAGED / EXTERNAL

## Context
Base origin/main 206d739, branch `feat/ops-005-otel-profile`. The core half (JSON logs, sensitive-key denylist, metrics on a separate listener, OTLP/HTTP traces only when `OTEL_EXPORTER_OTLP_ENDPOINT` is set) is vizra-core #20, merged 7f64b6d and verified PASS separately. This PR covers the compose tree only.

## Acceptance
- OFF, the default in every existing shape: api, worker and migrate get `OTEL_EXPORTER_OTLP_ENDPOINT=""`, and no collector service exists.
- MANAGED (`-f docker-compose.otel-managed.yml`): an `otel-collector` service, digest-pinned, Apache-2.0, with no published port. api, worker and migrate get `http://otel-collector:4318`. The config in `deploy/otel/collector.yaml` exports only to the `debug` exporter and holds no credentials.
- EXTERNAL (`-f docker-compose.otel-external.yml`): no collector. The endpoint must be set (`${OTEL_EXPORTER_OTLP_ENDPOINT:?}`).
- The `env/registry/core.json` snapshot is refreshed at core 7f64b6d, and coverage sees both OTEL keys.
- Non-goal: a running-stack scrape or trace transcript. That needs the boot lane.

## Implementation
- Base `x-core-env` sets the endpoint to `""` (a literal) and `OTEL_SERVICE_NAME=${OTEL_SERVICE_NAME:-vizra-core}`.
- Two overlays. MANAGED has to change api/worker environment, and a profile cannot do that, so it is an overlay rather than a base profile like ClickHouse/IPFS. This is a deliberate difference from that pattern, and it keeps `prod-all-optional` from ending up with a collector and an empty endpoint.
- New shapes `prod-otel-managed` and `prod-otel-external`, with per-shape `otel` / `otel_endpoint`.
- New rule `otel-mode` in `scripts/check-compose-topology.py`.
- The collector probe (`/otelcol --version`) is declared in `known_false_probes`, because the image is distroless and nothing can reach the health_check extension.

## Verification
Docker Compose 5.6.1 with the daemon running locally, so real `docker compose config` renders ran:
`./scripts/compose-render.py --all --out /tmp/o5/g1`, then `check-compose-topology.py` and `check-config-coverage.py` on that directory.

## Progress and evidence
RED: the snapshot was refreshed before the compose change (`check-config-coverage.py`, exit 1):
```
VIOLATION rule=service-key-missing subject=bundle-no-checkouts/api/OTEL_EXPORTER_OTLP_ENDPOINT detail=vizra-core reads OTEL_EXPORTER_OTLP_ENDPOINT (env/registry/core.json at 7f64b6de5dbc) but the rendered environment map does not deliver it ...
(same for OTEL_SERVICE_NAME, and for worker/migrate, in every shape)
```
Rule `otel-mode`, using controlled mutations in a throwaway worktree (each render exit 0, topology exit 1):
```
## M1 collector port published (ports: ["0.0.0.0:4318:4318"] in the managed overlay)
VIOLATION shape=prod-otel-managed rule=otel-mode service=otel-collector detail=the collector must be on the internal network only; ports=[{'host_ip': '0.0.0.0', ... 'published': '4318', 'target': 4318}] ...
## M2 endpoint missing in EXTERNAL (api's overlay env removed)
VIOLATION shape=prod-otel-external rule=otel-mode service=api detail=otel=external needs OTEL_EXPORTER_OTLP_ENDPOINT='https://otel.ci.invalid:4318', rendered ''
## M3 collector in an OFF shape (managed overlay added to prod-default)
VIOLATION shape=prod-default rule=otel-mode service=otel-collector detail=otel=off but a collector rendered
VIOLATION shape=prod-default rule=otel-mode service=api detail=otel=off needs OTEL_EXPORTER_OTLP_ENDPOINT='', rendered 'http://otel-collector:4318'
```
GREEN on the PR head: render 15 shapes (exit 0), topology (exit 0), coverage "39 component keys ... 15 shapes ... 0 violations" (exit 0). check-workflows, check-action-pins --required, check-doc-links, check-quality-json, check-template-claims and check-generated-ledger all exit 0.

Image: `otel/opentelemetry-collector:0.139.0@sha256:8ac5df2a931e9264667b236d65bf7591fa4ba633a7a634e6caa2f0a4fc549c07`, the multi-arch index. Confirmed locally on 2026-11-12 with `docker buildx imagetools inspect`.

## Blockers and handoff
- Did not run: booting the stack, scraping metrics against a running stack, and trace export through the collector. Both need the VZ-ISSUE-004 boot lane.
- The "scrape transcript" evidence is core's in-process scrape test only (core #20).
- Follow-up: replace the known-false collector probe.
