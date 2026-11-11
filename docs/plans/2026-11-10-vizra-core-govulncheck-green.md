# Execution plan: VZ-CI-004 (part) — the govulncheck lane is green again on vizra-core

## Context
Repo `yegamble/vizra-core`, worktree `.claude/worktrees/core-ci-repair`, branch
`fix/govulncheck-green` from origin/main `27cee54`. `govulncheck` is a required
lane (`.github/required-checks.txt`) and has failed on main since 2026-10-12
(run 42574177050). References: ADR-001 § Bump policy; ledger case "A reachable
advisory fails the lane". Budget on entry: verdicts 0/4, fix rounds 0/2,
re-plans 0/1, ticks 0/12.

## Acceptance
`make govulncheck` exits 0 on the branch because the advisories are FIXED, and
`ci-required` is green on the PR. Non-goals: the red `image-scan` lane, any
refactor, any ignore list / `|| true` / narrowed package set / change to the
required set. The lane itself (Makefile recipe, workflow, manifest) is untouched.

## Implementation
Pins changed (each confirmed against the live registry on 2026-11-10):

| Pin | From | To | Where changed | Confirmed at |
|---|---|---|---|---|
| Go toolchain | go1.27.1 | go1.27.4 | `go.mod` `toolchain` | `https://go.dev/dl/?mode=json&include=all` lists go1.27.4 stable (newest 1.27 patch); `go` downloaded and ran it |
| golang build image | golang:1.27.1-trixie `sha256:433790e5…` | golang:1.27.4-trixie index `sha256:b54b2639de8c1bfe538ec5ffc45f29b1932235ac5f6d63c059853646677112d9` | `Dockerfile` | `docker buildx imagetools inspect golang:1.27.4-trixie` (index has linux/amd64 and linux/arm64) |
| `github.com/labstack/echo/v5` | v5.3.1 | v5.4.4 | `go.mod`, `go.sum`, `NOTICE` | `go list -m -versions github.com/labstack/echo/v5` (… v5.4.0 v5.4.1 v5.4.2 v5.4.3 v5.4.4); LICENSE re-read from the module cache: MIT |
| fixtures manifest toolchain | go1.27.1 | go1.27.4 | `fixtures/manifest.json` via `make fixtures-manifest` | only the `toolchain.go` field moved; every fixture hash is unchanged |

Workflows read the Go version from `go.mod` (`go-version-file`), so they need
no edit. `AGENTS.md` (vizra-core) pin table updated. Advisory → fix mapping:
GO-2026-6873/6876/6877/6879/6881/6883 fixed in echo v5.4.0; GO-2026-6603,
6605, 6607, 6608, 6610, 6611, 6612, 6613, 6617 fixed in go1.27.2; GO-2026-6809
fixed in go1.27.3.

## Verification
`make govulncheck` (red on origin/main, green on head), `make tidy-check`,
`make ci`, `make build`, the two guards, `go test ./internal/fixtures/`.
Integration / cache-matrix / docker-build need Docker, PostgreSQL and a RESP
server: none is running on this host (Docker daemon down, `pg_isready` no
response), so they are NOT RUN locally and CI on the PR is their evidence.

## Progress and evidence
Host darwin/arm64, GNU Make 3.81. Gate logs: `/tmp/vz-govuln/logs/`.

| Command | Exit | Note |
|---|---|---|
| `make govulncheck` on 27cee54 (go1.27.1) | 2 | RED, 16 advisories, transcript below |
| `make govulncheck` on head (go1.27.4) | 0 | GREEN, transcript below |
| `make fixtures-verify` before re-pin | 2 | red by name: `toolchain-pin` (expected) |
| `make fixtures-manifest` | 0 | 1-line diff, hashes unchanged |
| `make tidy-check` | 0 | |
| `make ci` | 0 | "make ci: all lanes passed" (136s; unit test-race, no DB) |
| `make build` + `./bin/vizra version` | 0 | |
| `./scripts/make-integrity-guard.sh --workflow` | 0 | |
| `./scripts/ci-required-guard.sh` | 0 | 6 required checks |
| `go test -race -count=1 ./internal/fixtures/` | 0 | |

### RED transcript — `make govulncheck` on origin/main 27cee54
```
==> govulncheck
go: downloading golang.org/x/vuln v1.8.0
go: downloading golang.org/x/telemetry v0.0.0-20260908163034-4bcc4b2ee518
go: downloading golang.org/x/tools v0.50.0
=== Symbol Results ===

Vulnerability #1: GO-2026-6883
    Echo has Open Redirect via Control-Character Prefix Defeating sanitizeURI in
    github.com/labstack/echo
  More info: https://pkg.go.dev/vuln/GO-2026-6883
  Module: github.com/labstack/echo/v5
    Found in: github.com/labstack/echo/v5@v5.3.1
    Fixed in: github.com/labstack/echo/v5@v5.4.0
    Example traces found:
      #1: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls echo.Echo.ServeHTTP

Vulnerability #2: GO-2026-6881
    Echo static file middleware route protection bypass via encoded dot-dot
    traversal in github.com/labstack/echo
  More info: https://pkg.go.dev/vuln/GO-2026-6881
  Module: github.com/labstack/echo/v5
    Found in: github.com/labstack/echo/v5@v5.3.1
    Fixed in: github.com/labstack/echo/v5@v5.4.0
    Example traces found:
      #1: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls echo.Echo.ServeHTTP

Vulnerability #3: GO-2026-6879
    Echo: HTTPS Redirect and HSTS Bypass via Unconditional Trust of Forwarded
    Scheme Headers in github.com/labstack/echo
  More info: https://pkg.go.dev/vuln/GO-2026-6879
  Module: github.com/labstack/echo/v5
    Found in: github.com/labstack/echo/v5@v5.3.1
    Fixed in: github.com/labstack/echo/v5@v5.4.0
    Example traces found:
      #1: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls echo.Echo.ServeHTTP

Vulnerability #4: GO-2026-6877
    Echo has CSRF Protection Bypass via MethodOverride Rewriting POST to Safe
    Method in github.com/labstack/echo
  More info: https://pkg.go.dev/vuln/GO-2026-6877
  Module: github.com/labstack/echo/v5
    Found in: github.com/labstack/echo/v5@v5.3.1
    Fixed in: github.com/labstack/echo/v5@v5.4.0
    Example traces found:
      #1: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls echo.Echo.ServeHTTP

Vulnerability #5: GO-2026-6876
    Cross-Site Scripting (XSS) via unsanitized JSONP callback in
    github.com/labstack/echo
  More info: https://pkg.go.dev/vuln/GO-2026-6876
  Module: github.com/labstack/echo/v5
    Found in: github.com/labstack/echo/v5@v5.3.1
    Fixed in: github.com/labstack/echo/v5@v5.4.0
    Example traces found:
      #1: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls echo.Echo.ServeHTTP

Vulnerability #6: GO-2026-6873
    URL-encoded path bypasses route/group middleware guarding a
    statically-served path in github.com/labstack/echo
  More info: https://pkg.go.dev/vuln/GO-2026-6873
  Module: github.com/labstack/echo/v5
    Found in: github.com/labstack/echo/v5@v5.3.1
    Fixed in: github.com/labstack/echo/v5@v5.4.0
    Example traces found:
      #1: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls echo.Echo.ServeHTTP

Vulnerability #7: GO-2026-6809
    Distrust compromised intermediate certificates in crypto/x509
  More info: https://pkg.go.dev/vuln/GO-2026-6809
  Standard library
    Found in: crypto/x509@go1.27.1
    Fixed in: crypto/x509@go1.27.3
    Example traces found:
      #1: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls x509.Certificate.Verify

Vulnerability #8: GO-2026-6617
    HTTP/2 server crash due to HPACK encoder race in net/http
  More info: https://pkg.go.dev/vuln/GO-2026-6617
  Standard library
    Found in: net/http/internal/http2@go1.27.1
    Fixed in: net/http/internal/http2@go1.27.2
    Example traces found:
      #1: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.Close
      #2: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.Close
      #3: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.RoundTrip
      #4: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.RoundTrip
      #5: cmd/api/main.go:181:25: api.run calls http.Server.Shutdown, which calls http2.Server.GracefulShutdown
      #6: cmd/api/main.go:181:25: api.run calls http.Server.Shutdown, which calls http2.Server.GracefulShutdown
      #7: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #8: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #9: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #10: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #11: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #12: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #13: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip
      #14: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip
      #15: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.bufferedWriterTimeoutWriter.Write
      #16: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.bufferedWriterTimeoutWriter.Write
      #17: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.chunkWriter.Write
      #18: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.chunkWriter.Write
      #19: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.gzipReader.Close
      #20: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.gzipReader.Close
      #21: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.gzipReader.Read
      #22: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.gzipReader.Read
      #23: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #24: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #25: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http2.responseWriter.Write
      #26: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http2.responseWriter.Write
      #27: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http2.responseWriter.WriteHeader
      #28: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http2.responseWriter.WriteHeader
      #29: internal/fixtures/png.go:127:22: fixtures.buildAlphaPNG calls png.Encoder.Encode, which eventually calls http2.responseWriter.WriteString
      #30: internal/fixtures/png.go:127:22: fixtures.buildAlphaPNG calls png.Encoder.Encode, which eventually calls http2.responseWriter.WriteString
      #31: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.stickyErrWriter.Write
      #32: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.stickyErrWriter.Write
      #33: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close
      #34: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close
      #35: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.transportResponseBody.Read
      #36: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.transportResponseBody.Read

Vulnerability #9: GO-2026-6613
    HTTP/1 server connection desynchronization after 2xx CONNECT response in
    net/http
  More info: https://pkg.go.dev/vuln/GO-2026-6613
  Standard library
    Found in: net/http@go1.27.1
    Fixed in: net/http@go1.27.2
    Example traces found:
      #1: internal/testtmp/testtmp.go:71:15: testtmp.Run calls testing.M.Run, which eventually calls http.CanonicalHeaderKey
      #2: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do
      #3: internal/jobs/metrics.go:8:2: jobs.init calls prometheus.init, which eventually calls http.HandleFunc
      #4: internal/search/hmac.go:243:18: search.Verify calls http.Header.Get
      #5: internal/search/hmac.go:221:16: search.SignRequest calls http.Header.Set
      #6: internal/search/hmac.go:251:22: search.Verify calls http.Header.Values
      #7: internal/healthcheck/healthcheck.go:284:40: healthcheck.probe calls http.NewRequestWithContext
      #8: cmd/worker/main.go:92:12: worker.run calls http.ServeMux.Handle
      #9: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe
      #10: cmd/api/main.go:181:25: api.run calls http.Server.Shutdown
      #11: internal/search/remote.go:169:2: search.RemoteClient.call calls http.body.Close
      #12: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.body.Read
      #13: internal/search/remote.go:169:2: search.RemoteClient.call calls http.bodyEOFSignal.Close
      #14: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.bodyEOFSignal.Read
      #15: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.bodyLocked.Read
      #16: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.bufioFlushWriter.Write
      #17: internal/search/remote.go:169:2: search.RemoteClient.call calls http.cancelTimerBody.Close
      #18: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.cancelTimerBody.Read
      #19: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http.checkConnErrorWriter.Write
      #20: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http.chunkWriter.Write
      #21: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.connReader.Read
      #22: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close, which eventually calls http.expectContinueReader.Close
      #23: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.expectContinueReader.Read
      #24: internal/search/remote.go:169:2: search.RemoteClient.call calls http.gzipReader.Close
      #25: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.gzipReader.Read
      #26: internal/search/hmac.go:202:24: search.NewNonce calls rand.Read, which eventually calls http.loggingConn.Read
      #27: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which calls http.loggingConn.Write
      #28: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.maxBytesReader.Read
      #29: internal/db/db.go:71:13: db.Pools.Close calls pgxpool.Pool.Close, which eventually calls http.onceCloseListener.Close
      #30: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.persistConn.Read
      #31: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.persistConnWriter.ReadFrom
      #32: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http.persistConnWriter.Write
      #33: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close, which eventually calls http.readTrackingBody.Close
      #34: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.readTrackingBody.Read
      #35: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.readWriteCloserBody.Read
      #36: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http.response.ReadFrom
      #37: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http.response.Write
      #38: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http.response.WriteHeader
      #39: internal/fixtures/png.go:127:22: fixtures.buildAlphaPNG calls png.Encoder.Encode, which eventually calls http.response.WriteString
      #40: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http.timeoutWriter.Write
      #41: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http.timeoutWriter.WriteHeader
      #42: internal/migrate/migrate.go:212:32: migrate.Probe calls http.transportReadFromServerError.Error

Vulnerability #10: GO-2026-6612
    Double flow control refund on HTTP/2 server streams in net/http
  More info: https://pkg.go.dev/vuln/GO-2026-6612
  Standard library
    Found in: net/http/internal/http2@go1.27.1
    Fixed in: net/http/internal/http2@go1.27.2
    Example traces found:
      #1: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #2: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #3: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #4: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #5: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.requestBody.Read
      #6: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.requestBody.Read

Vulnerability #11: GO-2026-6611
    Excessive CPU consumption from repeated initial window changes in net/http
  More info: https://pkg.go.dev/vuln/GO-2026-6611
  Standard library
    Found in: net/http/internal/http2@go1.27.1
    Fixed in: net/http/internal/http2@go1.27.2
    Example traces found:
      #1: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.Close
      #2: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.Close
      #3: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.RoundTrip
      #4: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.RoundTrip
      #5: cmd/api/main.go:181:25: api.run calls http.Server.Shutdown, which calls http2.Server.GracefulShutdown
      #6: cmd/api/main.go:181:25: api.run calls http.Server.Shutdown, which calls http2.Server.GracefulShutdown
      #7: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #8: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #9: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #10: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #11: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #12: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #13: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip
      #14: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip
      #15: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.bufferedWriterTimeoutWriter.Write
      #16: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.bufferedWriterTimeoutWriter.Write
      #17: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.chunkWriter.Write
      #18: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.chunkWriter.Write
      #19: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.gzipReader.Close
      #20: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.gzipReader.Close
      #21: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.gzipReader.Read
      #22: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.gzipReader.Read
      #23: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #24: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #25: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http2.responseWriter.Write
      #26: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http2.responseWriter.Write
      #27: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http2.responseWriter.WriteHeader
      #28: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http2.responseWriter.WriteHeader
      #29: internal/fixtures/png.go:127:22: fixtures.buildAlphaPNG calls png.Encoder.Encode, which eventually calls http2.responseWriter.WriteString
      #30: internal/fixtures/png.go:127:22: fixtures.buildAlphaPNG calls png.Encoder.Encode, which eventually calls http2.responseWriter.WriteString
      #31: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.stickyErrWriter.Write
      #32: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.stickyErrWriter.Write
      #33: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close
      #34: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close
      #35: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.transportResponseBody.Read
      #36: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.transportResponseBody.Read

Vulnerability #12: GO-2026-6610
    HTTP/2 transport accepts malformed framing-related headers in net/http
  More info: https://pkg.go.dev/vuln/GO-2026-6610
  Standard library
    Found in: net/http/internal/http2@go1.27.1
    Fixed in: net/http/internal/http2@go1.27.2
    Example traces found:
      #1: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #2: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #3: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #4: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #5: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip
      #6: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip

Vulnerability #13: GO-2026-6608
    Memory limit bypass when parsing MIME headers in net/textproto,
    mime/multipart
  More info: https://pkg.go.dev/vuln/GO-2026-6608
  Standard library
    Found in: net/textproto@go1.27.1
    Fixed in: net/textproto@go1.27.2
    Example traces found:
      #1: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls textproto.Reader.ReadMIMEHeader

Vulnerability #14: GO-2026-6607
    Reject malformed ECH outer extension references in crypto/tls
  More info: https://pkg.go.dev/vuln/GO-2026-6607
  Standard library
    Found in: crypto/tls@go1.27.1
    Fixed in: crypto/tls@go1.27.2
    Example traces found:
      #1: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls tls.Conn.HandshakeContext
      #2: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls tls.Conn.Read
      #3: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which calls tls.Conn.Write
      #4: internal/cache/cache.go:69:37: cache.Open calls redis.NewClient, which eventually calls tls.DialWithDialer
      #5: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls tls.Dialer.DialContext

Vulnerability #15: GO-2026-6605
    HTTP/1 client connection desynchronization after CONNECT rejection in
    net/http
  More info: https://pkg.go.dev/vuln/GO-2026-6605
  Standard library
    Found in: net/http@go1.27.1
    Fixed in: net/http@go1.27.2
    Example traces found:
      #1: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do

Vulnerability #16: GO-2026-6603
    HTTP/2 server memory exhaustion due to Trailer headers in net/http
  More info: https://pkg.go.dev/vuln/GO-2026-6603
  Standard library
    Found in: net/http/internal/http2@go1.27.1
    Fixed in: net/http/internal/http2@go1.27.2
    Example traces found:
      #1: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.Close
      #2: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.Close
      #3: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.RoundTrip
      #4: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.NetHTTPClientConn.RoundTrip
      #5: cmd/api/main.go:181:25: api.run calls http.Server.Shutdown, which calls http2.Server.GracefulShutdown
      #6: cmd/api/main.go:181:25: api.run calls http.Server.Shutdown, which calls http2.Server.GracefulShutdown
      #7: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #8: cmd/api/main.go:152:38: api.run calls http.Server.ListenAndServe, which eventually calls http2.Server.ServeConn
      #9: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #10: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.AddConn
      #11: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #12: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.NewClientConn
      #13: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip
      #14: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.Transport.RoundTrip
      #15: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.bufferedWriterTimeoutWriter.Write
      #16: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.bufferedWriterTimeoutWriter.Write
      #17: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.chunkWriter.Write
      #18: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.chunkWriter.Write
      #19: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.gzipReader.Close
      #20: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.gzipReader.Close
      #21: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.gzipReader.Read
      #22: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.gzipReader.Read
      #23: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #24: internal/healthcheck/healthcheck.go:300:24: healthcheck.probe calls http.Client.Do, which eventually calls http2.requestBody.Close
      #25: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http2.responseWriter.Write
      #26: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which calls http2.responseWriter.Write
      #27: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http2.responseWriter.WriteHeader
      #28: internal/doctor/doctor.go:305:14: doctor.Report calls fmt.Fprintln, which eventually calls http2.responseWriter.WriteHeader
      #29: internal/fixtures/png.go:127:22: fixtures.buildAlphaPNG calls png.Encoder.Encode, which eventually calls http2.responseWriter.WriteString
      #30: internal/fixtures/png.go:127:22: fixtures.buildAlphaPNG calls png.Encoder.Encode, which eventually calls http2.responseWriter.WriteString
      #31: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.stickyErrWriter.Write
      #32: internal/fixtures/manifest.go:547:13: fixtures.Manifest.Summary calls fmt.Fprintf, which eventually calls http2.stickyErrWriter.Write
      #33: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close
      #34: internal/search/remote.go:169:2: search.RemoteClient.call calls http2.transportResponseBody.Close
      #35: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.transportResponseBody.Read
      #36: internal/search/remote.go:130:16: search.RemoteClient.ping calls io.Copy, which eventually calls http2.transportResponseBody.Read

Your code is affected by 16 vulnerabilities from 1 module and the Go standard library.
This scan also found 7 vulnerabilities in packages you import and 3
vulnerabilities in modules you require, but your code doesn't appear to call
these vulnerabilities.
Use '-show verbose' for more details.
exit status 3
make: *** [govulncheck] Error 1
exit=2
```

### GREEN transcript — `make govulncheck` on the branch head
```
==> govulncheck
=== Symbol Results ===

No vulnerabilities found.

Your code is affected by 0 vulnerabilities.
This scan also found 0 vulnerabilities in packages you import and 1
vulnerability in modules you require, but your code doesn't appear to call these
vulnerabilities.
Use '-show verbose' for more details.
exit=0
```

## Blockers and handoff
- Not called, not failing the lane, left alone: GO-2026-5932 (`golang.org/x/crypto/openpgp`,
  module-level only; vizra-core does not import the package; the only fix is an
  untagged pseudo-version).
- The meta repo's ADR-001 licence table still reads "Go toolchain 1.27.x (1.27.1)"
  and "echo/v5 ≥ v5.3.1". Both ranges still hold, but the parenthetical should be
  moved to 1.27.4 by the meta owner (a builder does not run git in the meta checkout).
- `api/openapi.yaml` keeps `example: go1.27.1`; it is an illustrative example, not a pin.
- PR and CI results: appended by the chair/verifier from the PR.
