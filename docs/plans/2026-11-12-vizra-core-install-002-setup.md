# Execution plan: VZ-INSTALL-002 — `vizra setup` (core part, PR 1 of n)

## Context
Repo yegamble/vizra-core, branch `feat/install-002-vizra-setup` from 7f64b6d, draft PR https://github.com/yegamble/vizra-core/pull/22. The meta installer hands over with `cd <dir> && <dir>/bin/vizra setup` (install.sh:225-229), so setup writes `env/production.env` relative to the install root (`--env` overrides).

## Acceptance
Ledger outcome unchanged (interview topics; `--web` loopback one-time link; `--non-interactive`; `--check`; secrets minted never blank; re-run preserves; `--rotate` explicit; KEK needs `--yes-i-know`). Cases S1 S2 N1 N2 P1 R1.

## Implementation (design)
- `internal/setup/questions.go`: `Question{ID, Prompt, Keys, Secret, Mint, Choices, Default(answers), When(answers), Validate, Write}`; `Questions()` is ordered; `PendingTemplateKeys`.
- `internal/setup/engine.go`: `Resolve(existing, answers, asker, stdin)`. Precedence: existing env value > supplied answer (map, then `VIZRA_SETUP_<ID>`; `@file` and `-` indirections) > asker > default > mint (crypto/rand 32 bytes, base64url). `Check(env)` returns one message per bad/missing key. `Rotate(env,id,yes,yesIKnow)`. `Run` writes temp+fsync+rename with mode 0600; an existing file with group/other permission bits is refused (decision: refuse rather than silently tighten, the secrets may already have leaked); an existing file that would change needs `--yes`; an unchanged result is a no-op. `LineAsker` is the terminal interview; secrets via an injected no-echo reader. The engine is UI-agnostic so `--web` can drive the same `Questions()`/`Resolve`.
- `cmd/vizra/setup.go`: flags `--env --non-interactive --answers --set --check --rotate --yes --yes-i-know --web` (web refused). No-echo via `stty -echo` (golang.org/x/term is not in go.mod; no module added).

### Question table
| id | keys | secret | condition |
|---|---|---|---|
| domain | VIZRA_DOMAIN* | | |
| tls (acme/internal/plain-http/external) | VIZRA_TLS_MODE*, VIZRA_PUBLIC_ORIGIN, VIZRA_ALLOW_INSECURE_PUBLIC_ORIGIN | | |
| instance_name | VIZRA_SITE_HANDLE | | |
| release | VIZRA_CORE_TAG, VIZRA_USER_TAG, VIZRA_SEARCH_TAG | | |
| s3_endpoint | VIZRA_S3_ENDPOINT* | | optional |
| s3_bucket / s3_access_key / s3_secret_key | VIZRA_S3_BUCKET*, VIZRA_S3_ACCESS_KEY_ID*, VIZRA_S3_SECRET_ACCESS_KEY* | secret key: yes | s3_endpoint set |
| storage (local/s3; default s3 only with full creds) | VIZRA_STORAGE_BACKEND* | | |
| postgres (managed/external) | VIZRA_POSTGRES_MODE* | | |
| postgres_dsn | DATABASE_URL | yes | postgres=external |
| postgres_password | POSTGRES_PASSWORD | yes, minted | postgres=managed |
| redis (managed/external) | VIZRA_REDIS_MODE* | | |
| redis_url | VIZRA_CACHE_URL | yes | redis=external |
| analytics (off/managed/external) | VIZRA_ANALYTICS_MODE* | | component not built |
| clickhouse_password | CLICKHOUSE_PASSWORD | yes, minted | analytics=managed |
| ipfs (off/managed/external) | VIZRA_IPFS_MODE* | | component not built |
| search (off/managed/external) | VIZRA_SEARCH_MODE | | |
| smtp (off/smtp) | VIZRA_SMTP_MODE* | | |
| smtp_url / smtp_from | VIZRA_SMTP_URL*, VIZRA_SMTP_FROM* | url: yes | smtp=smtp |
| registration (open/invite/closed) | VIZRA_REGISTRATION_MODE* | | |
| import (off only today) | VIZRA_IMPORT_MODE* | | importer not built |
| session_secret / mfa_kek / search_hmac | VIZRA_SESSION_SECRET, VIZRA_MFA_KEY_KEK, SEARCH_HMAC_KEY | yes, minted | |
`*` = in `PendingTemplateKeys` (not yet in the meta template or core registry).

## Verification (this session, source = commit on PR #22, darwin arm64, go 1.26)
| command | exit | notes |
|---|---|---|
| `go test ./internal/setup/` before code | 1 | build failed (red), /tmp/vz-ev/red1.txt |
| `go test -count=1 -v ./internal/setup/` | 0 | 10 tests PASS, 0 skip |
| mutation: Mint path disabled (`q.Mint && false`) | 1 | 6 tests FAIL; restored → green |
| `make tidy-check` (quiet.sh) | 0 | |
| `make config-template-check` | 0 | |
| `./scripts/ci-required-guard.sh` | 0 | 6 required checks |
| `make govulncheck` | 0 | no called vulns |
| `make ci` | see PR | |
| manual binary run: write, --check, rerun unchanged, KEK refusal, external pg w/o DSN | 0,0,0,1,1 | file mode -rw------- |

## Progress and evidence
Closed: N1, N2, P1 (no-echo via injected reader), R1, --rotate, KEK --yes-i-know (refusal; TOTP re-wrap absent), --non-interactive, --check. Partial: S1.

## Blockers and handoff — remaining, in order
1. Meta: add the 16 `PendingTemplateKeys` to env/production.env.example (and core registry where core reads them); then shrink the list (TestS1 fails on a listed key that has landed). Meta CI answer-coverage assert (S1 CI half).
2. S2: render Caddyfile.local for acme/internal/plain-http and an nginx example for `external`, with tests per mode.
3. `--web`: loopback-only listener, one-time token link, same engine; CSRF, single use, timeout.
4. KEK rotation that re-wraps TOTP secrets (needs DB), or keep refusal semantics documented.
5. Real-tty test of `stty -echo` path (pty harness) and stty restore on signal.
6. Docs: vizra-core AGENTS.md/README CLI section, docs/quality/COMMANDS.md entry; ledger update to IMPLEMENTED after verify.

## Session 2 (2026-11-12, vizra-core PR #22)

Rotate decisions (`internal/setup/engine.go` `rotateRefused`; `--yes-i-know` no longer overrides a data-loss refusal):
| Secret | Decision | Reason |
|---|---|---|
| mfa_kek | REFUSED always | no re-wrap of TOTP enrolments; future `vizra mfa rewrap-kek` |
| postgres_password | REFUSED always | bundled PG keeps its password in the volume; env change locks api/worker/migrate out (ALTER ROLE first, then edit env) |
| clickhouse_password | REFUSED always | same shape as postgres |
| session_secret | allowed with --yes | logs every user out (documented) |
| search_hmac | allowed with --yes | meta docker-compose.yml interpolates one `SEARCH_HMAC_KEY` into api (l.109) and search (l.396); no env_file; restart both together |

Done: echo restore on SIGINT/SIGTERM (`withEchoOff`, pure, tested); `RenderEdge`/`WriteEdge` render `deploy/Caddyfile.local` (meta caddy bind-mount, create_host_path:false) for acme/internal/plain-http and `deploy/nginx.example.conf` for external, sha256 marker header detects operator edits (refused without --yes), goldens under internal/setup/testdata/edge, caddy 2.11.4 `adapt` exit 0 on all three. Transcripts: internal/setup/testdata/transcripts/.
Assumptions: no acme email question exists, so acme blocks carry no email; routes /api/* and /.well-known/* -> api:8080, rest -> frontend:3000.
Remains: --web wizard; meta template keys; KEK re-wrap; pty test of real stty path; readNoEcho builds a fresh bufio.Reader per secret (may drop buffered piped input, interactive only).

## Session 3 (2026-11-12, vizra-core PR #22)

- CI fix: build-test run 43243050303 refused `internal/setup` (no floor). `scripts/test-floors.json`: internal/setup 14 (measured 16) and cmd/vizra 10 -> 12 (measured 14), both suites, generator formula, dated `_why` entry; nothing lowered. Commit 66d999b.
- `--web` (commit 2c557ac): `internal/setup/web.go`. 127.0.0.1 only (`CheckLoopback` refuses 0.0.0.0, ::, localhost, other IPs); random port; 256-bit hex token, `subtle.ConstantTimeCompare`, expires (`--web-ttl`, default 15m), invalidated by a successful write, doubles as the form's CSRF field; exact Host match (DNS rebinding); CSP `default-src 'none'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'`, no-store, X-Frame-Options DENY, Referrer-Policy no-referrer, nosniff; html/template form, no JS, labelled native controls, secrets as never-prefilled password inputs, posted secrets redacted from error text; `@file` and `-` indirections refused from the browser; same `Run` (Resolve + atomic 0600, existing values kept, --yes rule); edge file written after; process exits after write. Token printed once in the link, never logged elsewhere.
- Tests: 8 in `web_test.go`, red (build failed) then green; mutations: Host check off -> TestWebHostRebinding FAIL; `used=true` removed -> TestWebSubmitWritesAndStops FAIL. Transcripts internal/setup/testdata/transcripts/web-*.txt.
- Remains: meta template keys (16 PendingTemplateKeys, separate meta PR) -> S1 partial; KEK re-wrap; pty test of stty path. The web form is static, so conditional questions are all shown and ignored when not applicable.

## Session 4 (2026-11-12) — dead-control fix (finding from meta PR #33)

- Topology answers (postgres, redis, analytics, ipfs, with tls/search) now write only `COMPOSE_FILE` + `COMPOSE_PROFILES`; per-mode keys dropped. Combinations outside the production shapes in meta `scripts/compose-shapes.json` are refused (`not a supported compose shape`). Re-runs recover answers from COMPOSE_FILE/PROFILES.
- Experiment (Compose v5.6.1): `docker compose --env-file my.env config --services` honours COMPOSE_FILE and COMPOSE_PROFILES from that file; paths resolve against the cwd, so the operator runs from the meta checkout root.
- Removed questions (no core reader): storage + S3 (VZ-STORAGE-002), SMTP (VZ-EMAIL-001), registration (registration policy), import (import).
- PendingTemplateKeys = VIZRA_DOMAIN, VIZRA_TLS_MODE (reader: internal/setup/edge.go). Meta PR #33 must refresh its env/registry/setup.json snapshot.
- Red: internal/setup/testdata/transcripts/session4-red.txt. Core commit ab6e74d.
