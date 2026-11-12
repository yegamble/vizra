# VZ-OPS-005 vizra-core observability — plan & evidence (IN_PROGRESS)
Repo yegamble/vizra-core, branch feat/ops-005-observability, PR #20 (draft), head 5ce752f.
## Inventory (base 58d658f)
- internal/obs/log.go: NewLogger JSON (prod)/text, redactingHandler with secretKeys + valuePatterns (Redact). Lacked claim_token, x-amz-signature, signed_url keys.
- cmd/api/main.go:146 metrics listener (promhttp, own addr); only job gauges (internal/jobs/metrics.go). NO HTTP request metrics.
- cmd/worker/main.go:92 promhttp on "/" + /readyz,/healthz.
- internal/httpapi/server.go:212 otelhttp.NewHandler; middleware.go:73 routeAttributeMiddleware sets http.route/span name. No SDK/exporter: global no-op tracer.
## Done
1+2. internal/obs/denylist_test.go: real NewLogger, every key class top/group/WithGroup/With, error strings with DSN & signed URL, each line parsed as one JSON object with time/level/msg. RED /tmp/ops005/red-denylist.txt (3 keys leaked) -> fix log.go -> green; mutation (drop claim_token) mutation-denylist.txt RED.
3. internal/httpapi/metrics.go: vizra_http_requests_total{method,route,code}, vizra_http_request_duration_seconds{method,route}, unmatched -> "unmatched". obs.MetricsHandler shared by both binaries. metrics_test.go scrapes over HTTP, expfmt parses (prometheus/common v0.70.1, now direct). Mutation (raw URL as route) RED, 4 violations.
## Remaining
- Worker scrape test (job families) and curl transcript from a running binary (needs PostgreSQL).
- OTLP: add go.opentelemetry.io/otel/sdk + otlptracehttp (v1.46.0 line, confirm via go list -m -versions, LICENSE Apache-2.0, NOTICE), OTEL_EXPORTER_OTLP_ENDPOINT in config.Registry + .env.example, TracerProvider in api+worker, flush on SIGTERM bounded; httptest /v1/traces receiver test; check otelhttp server span attributes for url.query/url.path (initial span name uses raw path, server.go:216) and filter through denylist.
- Meta compose otel profile OFF/MANAGED/EXTERNAL passing OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME, OTEL_TRACES_SAMPLER(_ARG).
- Lanes not run: make ci, config-template-check, tidy-check, govulncheck, ci-required-guard.

## Session 2 (2026-11-12)
- Lanes on 5ce752f+scrape test: make ci PASS (50s), config-template-check PASS, tidy-check PASS, ci-required-guard PASS (6 required checks).
- Step 2 DONE: internal/jobs/metrics_scrape_test.go TestWorkerMetricsScrape PASS (real obs.MetricsHandler, expfmt parse, 3 job families, labels limited to kind/state). Pushed.
- Step 3 NOT STARTED (session time): pin probe only, reverted. `go get otel/sdk@v1.46.0 otlptracehttp@v1.46.0` adds otlptracehttp v1.46.0, sdk v1.46.0, proto/otlp v1.11.0, backoff/v5 v5.0.3, and MOVES existing pins: otlptrace v1.29.0->v1.46.0, grpc v1.82.0->v1.83.1, protobuf v1.36.11->v1.36.12, genproto api/rpc 20260630->20260819, grpc-gateway v2.27.1->v2.30.0, go-openapi/jsonpointer v0.22.5->v1.0.0 (unexpected; needs review), adds golang.org/x/net v0.58.0. No otel/otel core bump.
- Remaining: OTLP wiring + privacy filter + red/green test, step 4 rerun incl. govulncheck, PR body, ready.

## Session 3 (2026-11-12)
- Red first: d014905 adds internal/httpapi/tracing_test.go (TestTracesExportedWhenEnabled, TestTracesNotExportedWhenDisabled); failed to build: `undefined: obs.SetupTracing`, `cfg.OTLPEndpoint undefined`.
- Implemented (next commit): internal/obs/tracing.go SetupTracing (OTLP/HTTP + batcher only when OTEL_EXPORTER_OTLP_ENDPOINT set; base URL + /v1/traces), filteringExporter with an attribute ALLOWLIST (method, status, http.route, protocol version, url.scheme, server.port, error.type) + DeniedAttribute (secretKeys + Redact); config keys OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME (Registry + .env.example); span name `HTTP <METHOD>` / `<METHOD> <r.Pattern>` (otelhttp re-runs the formatter after serving when Echo sets r.Pattern — the raw-path formatter would have overwritten the route-template name); SetupTracing before srv.Handler() in api, bounded flush on shutdown in api (grace ctx) and worker (5s).
- Mutation: `WithBatcher(exp)` (filter removed) -> FAIL: user_agent.original="secret-agent/1.0" leaks "secret", client.address / network.peer.address = 203.0.113.7 (/tmp/ops005-red.txt). Restored -> `ok internal/httpapi` (/tmp/ops005-green.txt).
- Pins: jsonpointer v0.22.5->v1.0.0 is required by grpc-gateway/v2 v2.30.0, which proto/otlp v1.11.0 (needed by otlptracehttp v1.46.0) requires; MVS selects it; kin-openapi still builds and tests pass. x/net v0.58.0 had GO-2026-6611/6612/6617 reachable -> bumped to v0.60.0; govulncheck exit 0.
- Lanes: config-template-check PASS, tidy-check PASS, ci-required-guard PASS (6), govulncheck exit 0 on 030a13f; make ci: see PR.
