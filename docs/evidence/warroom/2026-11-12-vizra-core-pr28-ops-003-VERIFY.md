# Verify — vizra-core PR #28 (VZ-OPS-003) — 1st verdict of 4

- SHA: d83f1434a9b75efc656229d0a9311bb52ec8351f (PR head confirmed via `gh pr view 28`, unmoved)
- Env: darwin, Go (homebrew), Docker Compose 5.6.1; fresh clone /tmp/vzv-core-pr28-WuJoVl (deleted after run); meta compose files at meta HEAD e66b85de read-only.
- Verifier: independent, wrote none of this code.

## Commands and results
- `go test ./internal/ops ./cmd/vizra` → exit 0 (both `ok`).
- `go build -o vz ./cmd/vizra`; `vz setup --non-interactive --set domain=photos.example.org --set release=v0.1.0 --env $E/p.env --deploy-dir $E/d` → exit 0, 15 keys, `COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml`, `COMPOSE_PROFILES=core,frontend,edge`.
- Dry runs (`--project-dir` = meta checkout):
  - `restart --dry-run api` → exit 0: `docker compose --env-file $E/p.env -f docker-compose.yml -f docker-compose.prod.yml --profile core --profile frontend --profile edge restart -- api`
  - `logs api --dry-run --tail 1 --since 168h` → exit 0, same chain + `logs --no-color --tail 1 --since 168h -- api`
  - `--tail 0` → exit 2; `--tail 10001` → exit 2; `--since 169h` → exit 2
  - `restart migrate` → exit 2 (one-shot, restart "no"); `restart nope` → exit 2 (unknown, lists rendered services)
  - env without COMPOSE_FILE (chmod 600) → exit 1 "has no COMPOSE_FILE … refusing to guess"; at 0644 it first refuses on file mode (exit 1).
  - `status` (no stack running) → every service FAIL "no container", `BLOCKED jobs queue depth not measured: … DATABASE_URL: must be set`, exit 1 (FAIL dominates; exit 3 only when services are OK — code read cmd/vizra/ops.go:163-170, test TestStatusQueueDepthBlockedNeverZero).
  - `update` → release check BLOCKED, Compose ≥ 2.24.4 floor explained, detected 5.6.1, exit 3.
  - `vizra --help` contains: 'Running bare "docker compose" on a production host is WRONG: it drops the prod and external overlays, every profile and the env file.'
- Secret scan: every SECRET/PASSWORD/KEY/TOKEN value in p.env grep'd against all captured CLI output → 0 hits.
- Live stack: NOT RUN (needs pulling ghcr core/user images plus postgres/valkey/caddy; not cheap). Non-dry-run exec, real `ps` parsing against containers and measured queue depth are UNVERIFIED live; covered by unit tests only.

## "Wraps compose.sh" judgement
No `compose.sh` exists in the meta repo (`find` over the meta checkout: none; the ledger-candidates record says "no install.sh or compose.sh"). The fair reference is the topology the env-derived chain names. Comparison: `docker compose --env-file p.env config --services` in the meta dir (Compose reading COMPOSE_FILE/COMPOSE_PROFILES from the env file itself) → `api caddy frontend migrate postgres redis worker`, the same set the CLI renders with explicit `-f`/`--profile`. Bare `docker compose config` with no env file fails to interpolate, so it is a different invocation, as documented. No divergence → not blocking. The ledger wording "compose.sh" points at a script that does not exist → follow-up F-2.

## Mutations (mine), each red then restored green
| Mutation | Red | Restored |
|---|---|---|
| drop `-f` append in Chain.Argv | TestArgvIsExactEnvDerivedChain, TestLogsArgs…, TestRestartRefuses…, cmd TestRestartExecsChain… FAIL | ok/ok |
| OneShot() always false | TestRestartRefusesUnknownAndOneShot, TestParsePS…, cmd TestRestartExecs…, TestStatusQueueDepthBlockedNeverZero FAIL | ok/ok |
| allow `--tail 0` (`tail < 0`) | TestLogsArgsBoundedAndValidated FAIL | ok/ok |
| status prints "queue empty (measured)" on depth error | TestStatusQueueDepthBlockedNeverZero FAIL | ok/ok |
`git status` clean afterwards.

## CI on this SHA
ci-required SUCCESS; build-test, append-only, docker-build, fixtures, govulncheck, cache-matrix (redis, valkey), GitGuardian SUCCESS. image-scan FAILURE (not required; red on main too).

## Ledger cases
- success "Commands wrap compose.sh with the env-derived chain": CLOSED for the env-derived chain (argv reproduced); the compose.sh naming is a ledger wording gap (F-2).
- negative "Bare docker compose usage documented as wrong": CLOSED (help text, package doc, update text).
- outcome: logs/restart CLOSED (dry-run); update PARTIAL (release check honestly BLOCKED, no feed; floor explained but not compared, F-5); status PARTIAL — health from rendered model + ps, versions from image refs not OCI labels (F-4), queue depth BLOCKED on a setup-written env (F-3).
- evidence "unit tests + transcript": CLOSED (reproduced; live-stack run not done).

## Findings
FINDING 1: 37 MB compiled `vizra` binary committed at repo root
Severity: SHOULD · Confidence: high · repo vizra-core · files: `vizra` (diff stat: Bin 0 -> 37689874 bytes)
Observed: build artefact in the PR diff. Not privacy/auth/data loss → FOLLOW-UP.

FINDING 2: ledger names a `compose.sh` that does not exist; CLI builds the chain itself
Severity: NIT · Confidence: high · repo vizra (ledger) / vizra-core · requirements VZ-OPS-003
Observed: argv equivalent to Compose's own env-derived resolution (same services). FOLLOW-UP.

FINDING 3: status queue depth is always BLOCKED on a `vizra setup` env
Severity: SHOULD · Confidence: high · files cmd/vizra/ops.go:60-85
Observed: setup writes no DATABASE_URL (compose composes it), and bundled postgres is not host-reachable, so the host CLI can never measure depth. Honest BLOCKED, not a false 0 → FOLLOW-UP; outcome partial.

FINDING 4: versions come from image refs, not OCI labels/running digests
Severity: SHOULD · Confidence: high · files internal/ops/ops.go ServiceHealth. FOLLOW-UP.

FINDING 5: `vizra update` prints the detected Compose version but does not compare it with the 2.24.4 floor
Severity: SHOULD · Confidence: high · files cmd/vizra/ops.go runUpdate, internal/ops/ops.go UpdateReport. FOLLOW-UP.

No BLOCKING findings.

FINAL VERDICT: PASS — SHA d83f1434a9b75efc656229d0a9311bb52ec8351f
