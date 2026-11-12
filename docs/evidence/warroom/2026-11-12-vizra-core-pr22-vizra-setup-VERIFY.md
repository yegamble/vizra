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

(SUPERSEDED by the completion section below) verdict line of the first verifier: BLOCKED (time cut-off), SHA ab6e74d821266bbe546e83f648412ade07e4f1fd

---

# Completion by a second independent verifier (2026-11-12)
This verifier did not write the code. I used a fresh clone of vizra-core at ab6e74d821266bbe546e83f648412ade07e4f1fd; `gh pr view 22` headRefOid matched at the start. The binary was built with `go build -o $D/vizra ./cmd/vizra`. The meta tree is a `git archive origin/main` copy under $D/meta, and compose was never run in the meta checkout. Base flags were `--non-interactive --set domain=photos.example.com --set instance_name=vz --set release=v1.0.0`.

## D: topology
internal/setup/topology.go:28-37 lists 8 shapes. Each one equals the matching prod shape in compose-shapes.json on origin/main, by file chain and by profiles. All 4 named overlays exist in the meta tree.

| Answers | rc | COMPOSE_FILE (after base `docker-compose.yml:docker-compose.prod.yml`) / COMPOSE_PROFILES | Shape | `docker compose --env-file … config --services` |
|---|---|---|---|---|
| defaults | 0 | base / core,frontend,edge | prod-default ✓ | api caddy frontend migrate postgres redis worker |
| tls=external | 0 | base / core,frontend | prod-external-tls ✓ | – |
| search,analytics,ipfs=managed | 0 | base / core,frontend,edge,worker,search,analytics,ipfs | prod-all-optional ✓ | adds clickhouse ipfs search |
| postgres=external + dsn | 0 | +external-postgres / core,frontend,edge | prod-external-postgres ✓ | **fails: POSTGRES_PASSWORD missing** (F-4). With a fake shell POSTGRES_PASSWORD: no postgres service |
| redis=external + url | 0 | +external-redis / core,frontend,edge | prod-external-redis ✓ | (with fake PG pw) no redis service |
| both external | 0 | +ext-postgres:+ext-redis / core,frontend,edge | prod-external-both ✓ | (with fake PG pw) neither service |
| analytics=external | 0 | +external-clickhouse / core,frontend,edge,analytics | prod-external-clickhouse ✓ | no clickhouse container |
| ipfs=external | 0 | +external-ipfs / core,frontend,edge,ipfs | prod-external-ipfs ✓ | no ipfs container |
| search=managed only | **1** | refused: "not a supported compose shape", nothing written | – | – |
| analytics=managed + ipfs=external | **1** | refused, nothing written | – | – |

COMPOSE_FILE is honoured, because the overlays add and remove services. D: PASS, with F-4.

## E: S2 edge file
- `go test -count=1 -run Edge -v ./internal/setup/`: TestRenderEdgeGolden passed for acme, internal, plain-http and external. TestWriteEdgeOverwriteRules: PASS, ok.
- Binary run: wrote Caddyfile.local. I then prepended a hand-edited line (sha 96cffb50…). A re-run without --yes exited **1** with "Caddyfile.local was edited by hand; re-run with --yes to replace it". The sha was unchanged (96cffb50…, byte-identical), so the edit is preserved and there is **no data loss**. With --yes it exited 0 and the file was regenerated (sha 19ad4fd2…, GENERATED header).
- F-3 is resolved. "written" appears only when the file is unedited or --yes is given. E: PASS.

## N1
`--set postgres=external --set postgres_dsn=` in non-interactive mode: rc 1 ("postgres_dsn: must be a postgres/postgresql URL"). No env file and no deploy dir were written. PASS.

## R1 / F-1
A re-run with `--set instance_name=changed` and no --yes: rc 0. It printed "p.env: unchanged" and VIZRA_SITE_HANDLE stayed `vz`. The output is truthful: it makes no claim that the change was applied, and nothing is lost. This is still a deviation from "refuses rewrite without --yes", because the changed answer is silently ignored instead of refused. Classification: FOLLOW-UP (not blocking).

## Guard / make ci
- `./scripts/ci-required-guard.sh`: exit 0, "passed (6 required check(s))".
- `make ci` (fresh clone, local darwin): EXIT=0, "make ci: all lanes passed".

## Findings (completion)
- No BLOCKING finding reproduced.
- F-1 FOLLOW-UP (confirmed as above).
- F-2 FOLLOW-UP (unchanged).
- F-3 CLOSED: an edited edge file is refused without --yes and preserved byte-identical.
- F-4 FOLLOW-UP (new): for postgres=external, setup writes no POSTGRES_PASSWORD. The meta repo's base docker-compose.yml:80,149 still requires it, and docker-compose.external-postgres.yml:37 documents that. So `docker compose config` on the env file setup wrote fails for prod-external-postgres and prod-external-both. It fails loudly, with no data loss, auth or privacy impact and no false gate, but the generated env does not deploy those shapes as-is.

## Per-case table (final)
| Case / clause | State |
|---|---|
| Interview questions present (domain, tls, instance, release, PG/Redis, analytics, IPFS, search) | PASS |
| Storage/S3, SMTP, registration, import questions | NOT DELIVERED. VZ-INSTALL-002 cannot be recorded yet; this does not block merging this PR. |
| --web one-time loopback | PASS (first verifier) |
| --non-interactive | PASS |
| --check | PASS (first verifier) |
| Secrets minted / never blank | PASS (first verifier) |
| --rotate rules | PASS (first verifier) |
| Topology → COMPOSE_FILE/PROFILES (D) | PASS (F-4 follow-up) |
| Unsupported topology refused | PASS |
| S1, CI answer-coverage | NOT VERIFIED here (meta PR #33) |
| S2, edge goldens + operator-edit protection | PASS |
| N1, external PG with empty DSN | PASS |
| N2, s3 default | NOT APPLICABLE |
| P1, no echo, @file, stdin, env, 0600 | PASS (TTY echo untested) |
| R1, keep values; refuse rewrite without --yes | PARTIAL (F-1 follow-up) |

Head at the end: ab6e74d821266bbe546e83f648412ade07e4f1fd.

FINAL VERDICT: PASS — SHA ab6e74d821266bbe546e83f648412ade07e4f1fd
