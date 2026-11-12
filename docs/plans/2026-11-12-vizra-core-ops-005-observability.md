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
