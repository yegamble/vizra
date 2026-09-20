# Execution plan: vizra-search PR1 — the minimal real service (Q-001 / VZ-SEARCH-004 boundary, search half of VZ-FOUND-003)

## Context
- Repository `yegamble/vizra-search` (private), checkout
  `/Users/yosefgamble/github/vizra/vizra-search`, base commit `1b0a979`
  ("Initial commit", README only) on `main`. Branch for this slice:
  `feat/m0-minimal-service`.
- Slice: item **5** of the numbered PR sequence in
  `docs/plans/2026-09-15-prompt01-architecture.md` § "VZ-ISSUE-001 PR sequence".
- Governing decisions, all **Accepted (owner) 2026-09-20**:
  - `docs/adr/ADR-002-repository-process-release-configuration-ownership.md`
    — § "Search service and boundary (Q-001)" (copied ruling), § "Configuration
    ownership" (the `Load`/`LoadFrom`/`CheckEnv` seam and the fail-secure
    production block), § "Probes", § "Contracts", § "CI fan-in and merge queue",
    § "Logging and redaction", § "M0 obligations".
  - `docs/adr/ADR-001-stack-pins-and-licences.md` — Go toolchain line 1.27,
    Echo v5 ≥ v5.3.1, Echo types confined to one package.
  - `docs/OPEN_QUESTIONS.md` § "Q-001 — DECIDED 2026-09-15 (modified)" (the
    ruling text ADR-002 copies).
- Ledger entries this slice serves: `VZ-SEARCH-004` (internal service contract
  and SQL fallback — this PR delivers the *service side* of the boundary only,
  not indexing, ranking or the admin surface) and the search half of
  `VZ-FOUND-003`. Neither reaches IMPLEMENTED for its full outcome here.
- Issue: <https://github.com/yegamble/vizra/issues/1> (VZ-ISSUE-001).

## Acceptance
Exactly item 5 of the PR sequence, no more:

| # | Requirement | Source |
|---|---|---|
| A1 | `/healthz` (liveness), `/readyz` (readiness, drain-aware), `/version` | Q-001, ADR-002 § Probes |
| A2 | `/internal/v1/search`, `/internal/v1/suggestions`, `/internal/v1/events` verified by HMAC and returning an explicit `not_indexed` status | Q-001 |
| A3 | No `search_schema_version` is reported (no migrations yet) | Q-001 |
| A4 | A drift check of those handlers against the canonical contract owned by `vizra-core` | Q-001, ADR-002 § Contracts |
| A5 | `make ci` whose lanes test exactly that and **skip nothing** | Q-001 ("nothing skipped or fake") |
| A6 | Dockerfile | item 5 |
| A7 | `.github/required-checks.txt` and a `ci-required` workflow on `pull_request` **and** `merge_group`, GitHub-hosted `ubuntu-24.04`, third-party actions pinned by commit SHA | ADR-002 § CI fan-in |
| A8 | The repository's own `AGENTS.md`, and `CLAUDE.md` importing it | meta `AGENTS.md`, `CLAUDE.md` precedent |
| A9 | HMAC: constant-time comparison, a timestamp/replay rule, key from the environment, fail-secure production boot that refuses a dev or empty key | brief; ADR-002 § Configuration ownership |
| A10 | Negative tests: missing signature, wrong signature, stale timestamp, tampered body | brief |
| A11 | Bounded request size; deadlines propagated | meta `AGENTS.md` § Engineering guardrails |

Demonstrations required (red against a controlled mutation, green when restored):

- **D1** a handler that drifts from the contract fails CI;
- **D2** an unsigned or wrongly signed request is rejected;
- **D3** production boot refuses the dev HMAC key.

**Non-goals** (explicitly out of this slice): indexing, PostgreSQL, any
migration, ranking, event storage, compose wiring, the `/admin/search` UI,
`SEARCH_MODE` selection (that is core's config), and the ruleset application
(ADR-002 item 9 — an owner action *after* PR1 lands, so
`.github/expected-ruleset.json` and the ruleset drift job are **not** in this PR).

## Implementation

### Decisions — SUPERSEDED by the canonical contract, which exists

The provisional HMAC scheme and vendoring location planned above were replaced
by the canonical contract as soon as it was published. **`vizra-core` had
already written `api/search-internal.openapi.yaml` on `feat/m0-foundation`**, so
nothing here is provisional and nothing is invented. The contract-dependent work
was therefore not deferred.

Consumed: `yegamble/vizra-core` `api/search-internal.openapi.yaml` at commit
**`b0dbeb6dc27294fe793492ea60bc18b6aed4b042`** (also the branch head at the time
of reading), sha256
`5bf9dd22a2209dbfacb99f4c2d2d620ff15e0465f9b98228ec120983a3bf448a`, 21 551
bytes. Recorded in `api/CONTRACT-SOURCE.json` and verified by the drift check.
**No file in `vizra-core` was read through anything but the GitHub API, and none
was modified.**

Where the contract overrode the plan:

| Planned | Canonical contract | Action |
|---|---|---|
| two headers | **three**: adds `X-Vizra-Nonce`, ≥ 16 bytes lowercase hex | implemented the contract |
| five-field canonical string | **six fields**, nonce between timestamp and body hash | implemented the contract |
| vendor under `contracts/` | the contract itself states search vendors at `api/search-internal.openapi.yaml` | used the contract's path |
| key `VIZRA_SEARCH_HMAC_KEY` | **`SEARCH_HMAC_KEY`** | renamed |
| body bound `VIZRA_SEARCH_MAX_BODY_BYTES`, 64 KiB | **`MAX_INTERNAL_BODY_BYTES`**, 1 MiB | renamed and re-defaulted |
| events answers `202` | **`200`** for all three internal operations | changed |
| 401 body names the rejection reason | "MUST NOT say which of the three headers was wrong" | the reason now goes only to the log |
| probes out of the shared contract | the contract declares `/healthz`, `/readyz`, `/version` | the drift check covers all six operations |
| bespoke response fields (`reason`, `stored`, …) | fixed schemas, every one `additionalProperties: false` | responses rewritten to the schemas |

Two things the contract fixes that the plan had to guess and got right: the
**300 s** window, and the statement that the timestamp window is the only replay
bound until search owns storage ("recorded as a known limitation rather than
implied to be covered").

One judgement the contract left open. It declares `500` and `503` on every
internal operation. At M0 this service has no dependency that can fault, so
`internal/httpapi.Route` splits every status into **`Emitted`** — each provoked
by a real request in `TestEveryEmittedStatusIsReachable` — and
**`DeclaredNotEmitted`**, each carrying a written reason. Their union must equal
the contract's set exactly. `503` is genuinely emitted (a draining process is a
fault, not an empty index); only `500` is declared-not-emitted.

### Files
- `go.mod` / `go.sum` — module `github.com/yegamble/vizra-search`; `go 1.26.0`
  with `toolchain go1.27.1` (ADR-001 line 1.27; local Go is 1.26.2, so the
  toolchain directive fetches 1.27.1).
- `cmd/vizra-search/main.go` — boot, signal handling, graceful drain.
- `internal/config` — `Load()`, `LoadFrom(lookup)`, `CheckEnv(map)` (the ADR-002
  seam), a collecting `validate()`, and the production refusals.
- `internal/hmacauth` — signing string, `Sign`, `Verify`, typed rejection
  reasons.
- `internal/buildinfo` — version/commit/build time via `-ldflags`, plus
  `SchemaVersion` which is deliberately absent (A3).
- `internal/httpapi` — the only package importing Echo (ADR-001); router,
  probe handlers, the three internal handlers, body-size bound, request
  deadline, redacting logger.
- `internal/contract` — OpenAPI reader and the both-direction comparison, with
  its own testdata fixtures so the *mechanism* is tested independently of the
  vendored file.
- `contracts/search-internal.openapi.yaml` + `contracts/MANIFEST.json`.
- `Makefile` (`ci` = fmt-check, vet, echo-containment, lint-free build, contract
  drift, test-race, no-skip guard), `Dockerfile`, `.dockerignore`, `.gitignore`.
- `.github/workflows/ci.yml`, `.github/workflows/ci-required.yml`,
  `.github/required-checks.txt`.
- `AGENTS.md`, `CLAUDE.md`.

### Interfaces shared with another workstream
`vizra-core` (branch `feat/m0-foundation`) owns
`api/search-internal.openapi.yaml`. This repo consumes it read-only at a
recorded SHA. **Any needed change to that contract is reported to the chair, not
edited here.**

## Verification
Lanes, all in `make ci`, all run on `ubuntu-24.04` in CI:

| Lane | Command | Proves |
|---|---|---|
| fmt | `make fmt-check` | gofmt clean |
| vet | `make vet` | `go vet ./...` |
| boundary | `make echo-containment` | `echo.` imported only by `internal/httpapi` (ADR-001) |
| build | `make build` | binary links |
| contract | `make contract-drift` | A4/D1 |
| test | `make test` | `go test -race -count=1 ./...` |
| no-skip | `make test-noskip` | the run reports 0 skipped tests (A5) |
| docker | CI job `docker-build` | A6 |

Demonstrations are recorded as transcripts in `docs/evidence/` of this repo
under `docs/evidence/m0-demonstrations/`.

## Progress and evidence

### Preflight (2026-09-20, before any code)
| Item | Result |
|---|---|
| Local Go | `go1.26.2 darwin/arm64`; `toolchain go1.27.1` in `go.mod` resolves `go1.27.1` (`go env GOVERSION` → `go1.27.1`) |
| Go 1.27 exists | `go.dev/dl?mode=json&include=all` lists `go1.27.1`, `go1.27.0` |
| Echo v5 | proxy.golang.org `@latest` → `v5.3.1` (2026-07-21), satisfies ADR-001 "≥ v5.3.1" |
| yaml | proxy.golang.org `gopkg.in/yaml.v3@latest` → `v3.0.1` |
| Docker | `linux/arm64`, ~17 GiB free. Native builds only; no emulated amd64 |
| gh | authenticated as `yegamble` |
| `vizra-core` contract | present on `feat/m0-foundation` at the time of the contract step |

No BLOCKED preflight item. Nothing was blocked at any point in this slice.

### Commits on `feat/m0-minimal-service`
| SHA | What |
|---|---|
| `2983b1c` | the slice |
| `7abf369` | test gap found by mutation D2b: MAC comparison pinned to the whole value |
| `ee4bdb7` | test gap found by mutation D3b: key-length refusal pinned to its own rule |
| `271ac34` | chair finding: manifest floor, CODEOWNERS, non-local `$ref` rejection, Dockerfile digest guard |

### Verification — every command run, with exit codes
Host: `Darwin arm64`, `go1.27.1`, source at `271ac34`.

| Command | Exit | Result |
|---|---|---|
| `make fmt-check` | 0 | clean |
| `make vet` | 0 | — |
| `make echo-containment` | 0 | Echo confined to `internal/httpapi` (ADR-001) |
| `make build` | 0 | binary links, `version` prints identity |
| `make contract-drift` | 0 | handlers, operation ids, status sets and response bodies all match the canonical contract |
| `make test` | 0 | `go test -race -count=1 ./...`, 6 packages |
| `make test-noskip` | 0 | **187 pass events, 0 skips**; 181 test functions and subtests pass, 0 fail, 0 skip |
| `make ci` (all of the above) | 0 | — |
| `./scripts/ci-required-guard.sh` | 0 | floor, bare-name, continue-on-error and digest checks all pass |
| `docker build -t vizra-search:local .` | 0 | 10.4 MB scratch image, native arm64 |

`test-noskip` initially failed on **1 skip** — `internal/buildinfo` had no test
file. That was closed by writing real tests for it, not by loosening the guard.

### Demonstrations — 16, each red under a controlled mutation and green when restored
All transcripts in `vizra-search/docs/evidence/m0-demonstrations/`. Each file
records the baseline commit, date, toolchain, host, the mutation diff, the RED
command and exit code, the restore, and the GREEN command and exit code.

| ID | Mutation | RED | GREEN |
|---|---|---|---|
| D1a | route renamed away from the contract | 2 | 0 |
| D1b | response field `results` → `hits` | 2 | 0 |
| D1c | a status the contract never declares | 2 | 0 |
| D1d | the vendored contract edited in place | 2 | 0 |
| D2a | unsigned requests accepted | 1 | 0 |
| D2b | MAC compared one byte only | 1 | 0 |
| D2c | stale timestamps accepted | 1 | 0 |
| D2d | body not bound into the MAC | 1 | 0 |
| D3a | every dev-placeholder refusal removed | 1 | 0 |
| D3b | key-length floor removed | 1 | 0 |
| D3c | mode defaults to development | 1 | 0 |
| D4a | a required lane deleted from the manifest | 1 | 0 |
| D4b | a required lane marked optional | 1 | 0 |
| D4c | `continue-on-error` on a required lane | 1 | 0 |
| D4d | Dockerfile base image unpinned | 1 | 0 |
| D4e | non-local `$ref` in the contract | 2 | 0 |

`E1-image-end-to-end.txt` additionally records the built image refusing the dev
key, reporting `healthy` through its own `HEALTHCHECK`, serving all three probes
with `search_schema_version: null`, rejecting an unsigned call with 401
`signature_rejected`, answering a signed call `200 not_indexed`, rejecting the
same signature replayed against another endpoint, and a container log carrying
zero occurrences of the key, nonce or signature.

### Two mutations that SURVIVED, and what was done about them
Both were real gaps in the tests, not in the product, and both were closed
rather than explained away:

1. **D2b** — comparing only the first byte of the MAC passed the whole suite,
   because two unrelated MACs almost always differ in the first byte, so every
   wrong-key test was satisfied. Closed in `7abf369` with a forgery that differs
   only in the **last** byte, its mirror for the first byte, and a source-level
   guard that the comparison goes through `hmac.Equal` — the one part of
   "constant time" a functional test can assert.
2. **D3b** — removing the 32-byte floor passed, because the short fixture was
   also caught by the distinct-byte rule and the assertion matched only the
   substring `"at least"`. Closed in `ee4bdb7` by naming the rule in the
   assertion and adding a 31-byte fixture with enough variety that only the
   length floor can refuse it.

A third mutation (**D3a**, removing only the exact-match dev-key check) also
stayed green, and that one is **correct**: the documented key is independently
caught by the `dev-` prefix rule and the `insecure` and `do-not-use` markers.
The transcript records the layered defence and the mutation was widened to the
whole placeholder family, which does turn it red.

### Chair finding (mid-slice), addressed in `271ac34`
The security review of `vizra-user` PR1 found a manifest that gates a PR while
being editable by it. This repository had the same shape. Fixed:

- `scripts/ci-required-guard.sh` (extracted from the workflow so it is runnable
  and demonstrable) enforces a **floor** of lanes — `build`, `test`,
  `test-noskip`, `contract-drift`, `govulncheck` — that no PR may remove from
  the manifest, and requires every entry to be a bare job name so a lane cannot
  be neutered in place (D4a, D4b).
- `.github/CODEOWNERS` assigns `/.github/`, `/scripts/`, `/Makefile`, `/api/`,
  `internal/hmacauth`, `internal/config`, `AGENTS.md` and `CLAUDE.md` to
  `@yegamble`. **The ruleset that enforces CODEOWNERS is an owner action and is
  not part of this PR** (ADR-002 item 9).
- Every pullable Dockerfile base is digest-pinned and the guard enforces it
  (D4d). `FROM scratch` is exempt and the Dockerfile says why: it is Docker's
  reserved empty base, not a pullable image, and has no digest.
- `internal/contract` refuses any `$ref` that is not local (`#/...`) at parse
  time, before anything resolves one, across the whole document including
  branches the parser never walks (D4e).

### CI on GitHub

**PR: <https://github.com/yegamble/vizra-search/pull/1>** (open, not a draft).

**First run, head `e1e76c2`: 10 pass, 2 fail.**

| Lane | Result |
|---|---|
| fmt, vet, echo-containment, build, contract-drift, test, test-noskip, tidy-check, docker-build | SUCCESS |
| GitGuardian Security Checks | SUCCESS |
| **govulncheck** | **FAILURE** (exit 2) |
| **ci-required** | **FAILURE** |

The `ci-required` failure was the gate **working**: a required lane did not
succeed, so the aggregate did not either. No gate was weakened to clear it.

The `govulncheck` failure was a **scanner crash, not a finding**. It aborted
with `panic: unexpected expr: *ast.KeyValueExpr` on the linux/amd64 runner and
produced no verdict. The pin `@v1.1.4` was stale — its `go.mod` declares
`go 1.22.0`, predating Go 1.27 entirely. Fixed in `a57aa7a` by pinning
`@v1.8.0` (2026-09-08, `go 1.26.0`), verified locally on Go 1.27.1:
`No vulnerabilities found`, exit 0, scanner and DB date printed. The lane now
runs `govulncheck -version` before the scan so a green tick names the scanner
and the database date instead of being an unexplained pass.

Attempted and recorded: v1.1.4 does **not** crash on darwin/arm64, so the
diagnosis stops at "scanner too old for this toolchain on that platform" rather
than claiming which file triggered it. Evidence:
`docs/evidence/m0-demonstrations/E2-govulncheck-pin-correction.txt`.

**Second run, head `a57aa7a`: all 12 checks PASS, `ci-required` green.**

| Check | Result |
|---|---|
| fmt, vet, echo-containment, build, contract-drift, test, test-noskip, tidy-check, govulncheck, docker-build | pass |
| GitGuardian Security Checks | pass |
| **ci-required** | **pass** — "every required check succeeded on `a57aa7a02b05b09238e027fbecfe1d75b373b9c5`" |

Runs: [ci 35528384451](https://github.com/yegamble/vizra-search/actions/runs/35528384451),
[ci-required 35528384428](https://github.com/yegamble/vizra-search/actions/runs/35528384428).
Transcript: `docs/evidence/m0-demonstrations/E3-ci-green-on-amd64.txt`.

This run supplies the **linux/amd64 evidence** this arm64 machine could not
produce (ADR-009 / Q-027). On the `ubuntu-24.04` runner the built image refused
the dev key, answered `/healthz` `{"status":"ok"}`, `/readyz`
`{"status":"ok","components":[],"search_schema_version":null,…}`, reported
`search_schema_version: null` on `/version`, rejected an unsigned internal call
with 401, answered a signed one `not_indexed`, and logged `hmac_key:
"[redacted]"` with no key, nonce or signature anywhere. `govulncheck` recorded
`Scanner: govulncheck@v1.8.0`, `DB updated: 2026-09-16`, `No vulnerabilities
found`. `test-noskip` reported **187 pass events, 0 skips**. The `ci-required`
log shows the guard output (floor, bare names, job existence, digest pinning)
and every lane polled to a conclusion before the aggregate passed.

## Blockers and handoff

**No blockers.** Nothing in this slice was blocked, and no external input is
missing.

### Contract changes needed from another owner
**None.** The canonical contract was implementable as written. Two observations
for the chair, neither requiring a change:

1. The contract declares `500` on the internal operations; `vizra-search` has no
   dependency that can fault at M0 and therefore cannot emit one. This is
   recorded in the route table with a reason rather than faked.
2. `SearchResponse` declares an optional `search_schema_version` but
   `SuggestResponse` and `EventAck` do not. This service follows the contract
   exactly (the field appears only on `SearchResponse`), which is asymmetric but
   not wrong. Worth a look when core next touches the file.

### For the verifier
- Reproduce with `make ci` from a clean clone of the PR head; expect exit 0,
  187 pass events, 0 skips.
- Re-run any demonstration by applying the mutation diff at the top of its
  transcript and running the command the transcript names.
- `./scripts/ci-required-guard.sh` runs outside GitHub Actions.
- Note that `docs/evidence/m0-demonstrations/` is inside the `vizra-search`
  repository, not the meta repo, because it is this PR's own evidence.

### Remaining gate
Independent verification, then `ci-required` green on the verified SHA, then the
chair merges. The ruleset application (ADR-002 items 9 and 10) stays an owner
action after this PR lands, and **no ledger entry reaches VERIFIED on CI
evidence alone until branch protection is confirmed applied** (Q-032).

### Next concrete action
Independent verification of the PR, then the meta PR1 ledger update recording
`VZ-SEARCH-004` as partially IMPLEMENTED — the service side of the boundary
only; indexing, ranking, the `sql` fallback in core and the `/admin/search`
surface all remain PLANNED.
