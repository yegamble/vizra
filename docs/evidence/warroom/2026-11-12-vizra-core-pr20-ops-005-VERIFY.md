# VERIFY — vizra-core PR #20, VZ-OPS-005 (observability)

- Subject: https://github.com/yegamble/vizra-core/pull/20, head 030a13fc4c52e9dca89ca761603b8a8924a1985c (checked at start via `gh pr view` + fresh clone)
- Verifier: independent vizra-verifier (did not write the code). Env: darwin arm64, go1.27.4, fresh clone in mktemp scratch.

## A. Scope and deps
- 17 files, +634/-35; AGENTS.md untouched (0 matches in name-only diff).
- NOTICE adds otel/sdk, otlptracehttp v1.46.0 (Apache-2.0), proto/otlp v1.11.0 (Apache-2.0), backoff/v5 v5.0.3 (MIT), grpc-gateway/v2 v2.30.0 (BSD-3). LICENSE heads read from module cache for sdk, proto/otlp, backoff: they match.
- `go list -m -versions go.opentelemetry.io/otel/sdk` includes v1.46.0.
- jsonpointer: kin-openapi v0.149.0 needs v0.22.5; grpc-gateway v2.30.0 needs v1.0.0. MVS selects v1.0.0. The module path is the same (a v0 to v1 move needs no /vN suffix). The contract test result is in the lanes table.

## B. Denylist probes on obs.NewLogger(os.Stdout, production=true), the constructor cmd/api/main.go:73 and cmd/worker/main.go:43 use
| Probe | Result |
|---|---|
| 16 keys (password, token, secret, authorization, cookie, set-cookie, session, claim_token, signed_url, presigned_url, access_token, refresh_token, x-amz-signature, x-goog-signature, Authorization, X-Amz-Signature) x 4 modes (flat, slog.Group, With, WithGroup): 64 cases | all redacted |
| `dsn_plain`=postgres://u:pw@h/db (string value) | redacted |
| error value containing the DSN | redacted |
| message containing the DSN | redacted |
| `url`=...?X-Amz-Signature=..., `location`=...?X-Goog-Signature=... | redacted |
| Mutation: remove `claim_token` from secretKeys | `go test ./internal/obs -run Denylist` FAIL (exit 1); restored |

## C. Metrics (scratch probe on the real Server handler + obs.MetricsHandler)
Requests: `/healthz?token=TOKX`, `/no/such/1234`, `/no/such/5678?x=1`. Scrape:
```
vizra_http_requests_total{code="200",method="GET",route="/healthz"} 1
vizra_http_requests_total{code="404",method="GET",route="unmatched"} 2
```
No query, id or raw path appears in any label. Labels are method x route template x code, so cardinality is bounded. I found no parameterised route in internal/httpapi, so I could not run an id-in-route probe. The metrics listener is separate from the API: VIZRA_METRICS_ADDR defaults to 127.0.0.1:9090 (internal/config/keys.go:45), and cmd/api runs a separate http.Server. Tests: TestMetricsScrapeByRouteTemplate PASS, TestWorkerMetricsScrape PASS.

## D. Traces
- TestTracesExportedWhenEnabled PASS, TestTracesNotExportedWhenDisabled PASS.
- My variant: `GET /healthz?secret=abc` with Authorization: Bearer xyz, Cookie: s=1, User-Agent: secret-ua, RemoteAddr 198.51.100.9. Exported span is "GET /healthz" with attributes http.request.method, url.scheme, server.port, network.protocol.version, http.route, http.response.status_code. None contains abc, xyz, s=1, secret-ua or the client address.
- Disabled path: with an empty endpoint, SetupTracing (internal/obs/tracing.go) returns a no-op before any exporter or provider is built, so there is no goroutine and no network traffic.
- Mutation: make DeniedAttribute return false. TestTracesExportedWhenEnabled FAILs with 9 leak errors; restored, and `git status` is clean.
- Endpoint logging: OTLPEndpoint is used only in SetupTracing calls (cmd/api/main.go:85, cmd/worker/main.go:52) and is never logged directly. Residual: a SetupTracing error is returned wrapped, and an otlptracehttp URL-parse error could echo the endpoint. That path goes through main's error output, not NewLogger.

## E. Lanes (fresh clone at the SHA)
Raw: `ci=0 cfg=0 tidy=0 vuln=0 all modules verified ver=0 guard=0 ok  	github.com/yegamble/vizra-core/internal/httpapi	3.703s `
- `make ci`: "all lanes passed". config-template-check, tidy-check, govulncheck (no called vulnerabilities), `go mod verify`, ci-required-guard and `go test ./internal/httpapi -run Contract` (kin-openapi with jsonpointer v1.0.0): exit codes above.
- GitHub on 030a13fc: ci-required success (headSha 030a13fc); build-test, append-only, cache-matrix(+2 legs), docker-build, fixtures, govulncheck all success. image-scan failure: it is red on main and not in the manifest.
- Head re-checked at the end: 030a13fc4c52e9dca89ca761603b8a8924a1985c (unchanged).

## Findings
BLOCKING: none.
FOLLOW-UP (vizra-core batch):
1. cmd/api/main.go:36 (worker likewise) prints the error from run() to stderr through fmt, not Redact. If otlptracehttp.New rejects a malformed OTEL_EXPORTER_OTLP_ENDPOINT, the error can echo the endpoint, userinfo included. This class is unclaimed.
2. The metrics middleware is registered after siteMiddleware, so requests refused earlier (wrong host) are not counted. Not a leak.
3. No parameterised route exists yet, so no probe could test a route template with an id in it.

## Per-case
| Case | Result |
|---|---|
| JSON logs (production NewLogger is a JSON handler) | PASS |
| Denylist test (+ mutation goes red) | PASS |
| Prometheus metrics scrapeable + scrape transcript (section C) | PASS |
| Traces exported when enabled / none when disabled (+ mutation goes red) | PASS |
| otel profile OFF/MANAGED/EXTERNAL (meta compose profile) | NOT_APPLICABLE to this PR; undelivered |

VZ-OPS-005 cannot be recorded IMPLEMENTED after merge: the meta-repo otel compose profile (OFF/MANAGED/EXTERNAL, collector service, env wiring) and its rehearsal evidence are missing. This PR delivers the core-side slice only.

## Not run
Running-binary scrape over the real 127.0.0.1:9090 listener (an in-process handler was used instead); a real OTel collector.

FINAL VERDICT: PASS — SHA 030a13fc4c52e9dca89ca761603b8a8924a1985c
