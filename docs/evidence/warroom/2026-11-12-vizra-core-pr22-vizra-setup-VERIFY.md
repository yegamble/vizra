# VERIFY: vizra-core PR #22 (`vizra setup`), VZ-INSTALL-002

- Subject: https://github.com/yegamble/vizra-core/pull/22. Head at the start and at the end: ab6e74d821266bbe546e83f648412ade07e4f1fd
- Verifier: independent vizra-verifier (did not write the code). Ran on darwin/arm64 with local Go, in a fresh clone in a mktemp scratch dir, using the binary from `go build ./cmd/vizra`.

## Commands
| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `go test -count=1 -race ./internal/setup/ ./cmd/vizra/` | 0 | 41 run, 41 pass, 0 skip |
| 2 | `git diff origin/main...HEAD --stat` | 0 | 27 files, +2130/-4; AGENTS.md not touched; test-floors raised (cmd/vizra 10->12; internal/setup 14 is new), nothing lowered |
| 3 | `setup --non-interactive --answers a.txt` | 0 | file mode 600, 15 keys; 4 secrets each 43 chars base64 (32 bytes); 0 occurrences in stdout/stderr |
| 4 | Re-run with the same answers | 0 | sha256 identical, "unchanged" |
| 5 | Re-run with instance_name changed, no --yes | 0 | file unchanged (existing value kept, see F-1) |
| 6 | `VIZRA_SETUP_SESSION_SECRET`, `mfa_kek=@kek`, `search_hmac=-` (stdin) | 0 | all 3 values land in the file; none echoed |
| 7 | Existing env file with mode 0644 | 1 | refused with a chmod hint; file not modified |
| 8 | `--check` on a tampered file (blank session secret, bad domain) | 1 | both keys named; sha256 unchanged |
| 9 | `--rotate session_secret` / `search_hmac` | 1 without --yes / 0 with --yes | rotated |
| 10 | `--rotate mfa_kek` / `postgres_password` / `clickhouse_password` with `--yes --yes-i-know` | 1 | refused, each with a data-loss reason; file unchanged |
| 11 | `--web` then curl | - | listens only on 127.0.0.1 (lsof); `--web-addr 0.0.0.0:0` refused; no token, wrong token, Host `evil.example`: 403/403/403; CSP `default-src 'none'; form-action 'self'; frame-ancestors 'none'`, no-store, XFO DENY, Referrer-Policy no-referrer; existing secrets in the HTML: 0/4; POST with `@/etc/passwd` or `-`: 400, file unchanged; cross-origin POST without the token: 403; valid POST: 200, file 600, server exited; replayed token: connection refused (server gone) |
| 12 | `gh pr view` checks | 0 | ci-required, build-test, govulncheck, append-only, docker-build, fixtures, cache-matrix: SUCCESS; image-scan FAILURE (known red on main, not in the manifest) |

## Not run (time cut-off)
- `make ci` and `./scripts/ci-required-guard.sh`. A local `make govulncheck` was not run; the CI govulncheck lane is green.
- D, topology: COMPOSE_FILE/PROFILES per shape against compose-shapes.json; `docker compose config` honouring COMPOSE_FILE.
- E: Caddyfile and nginx goldens, `caddy adapt`, refusal to overwrite an operator-edited edge file. Observed: re-runs print "Caddyfile.local: written" every time, so whether an operator edit is preserved is UNVERIFIED.
- Headers of the individual CI lanes against manifest names were not cross-checked one by one.

## Findings
- No BLOCKING finding reproduced. No secret leak, no non-loopback bind, no rebinding, no CSRF, no local-file read and no data-losing rotation found.
- F-1 FOLLOW-UP: a changed answer on re-run without --yes exits 0 and silently keeps the old value. It is not refused as R1 words it. This is not data loss.
- F-2 FOLLOW-UP: `--yes-i-know` is accepted but has no effect (documented in --help).
- F-3 FOLLOW-UP / UNVERIFIED: the edge file is reported "written" on every re-run (see E).

## Per-case table
| Case / clause | State |
|---|---|
| Interview: domain, TLS, instance name, release, external PG/Redis, analytics, IPFS, optional components (search) | PASS (questions.go:116-164; exercised) |
| Interview: storage/S3, SMTP, registration, import questions | NOT DELIVERED. Removed deliberately because nothing reads those keys yet. The outcome is undelivered for these clauses, and VZ-INSTALL-002 cannot be recorded until the readers exist or the outcome changes. |
| `--web` on loopback with a one-time link | PASS |
| `--non-interactive` with flags/answers | PASS |
| `--check` | PASS |
| Secrets minted, never blank | PASS |
| Re-run preserves values | PASS |
| `--rotate` explicit; KEK needs --yes-i-know | PASS, stricter: the KEK is always refused |
| S1, CI answer-coverage assert | NOT VERIFIED. It lives in meta PR #33, which is not merged. Unit tests pass. |
| S2, Caddyfile/nginx goldens | NOT RUN |
| N1, external datastore with no DSN refused | NOT RUN by the verifier (unit tests only) |
| N2, s3 default | NOT APPLICABLE (the storage question was removed) |
| P1, no echo; @file, stdin, VIZRA_SETUP_*; 0600 | PASS. Prompt echo in a TTY was not tested. |
| R1, keeps values; refuses rewrite without --yes | PARTIAL (F-1) |

FINAL VERDICT: BLOCKED — SHA ab6e74d821266bbe546e83f648412ade07e4f1fd
