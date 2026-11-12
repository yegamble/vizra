# VERIFY — vizra (meta) PR #39, VZ-FOUND-005 meta part (rendered compose model assertion)

- PR: https://github.com/yegamble/vizra/pull/39 (branch feat/found-005-compose-healthcheck, OPEN)
- SHA verified: 1ee80cf38ec792e5967c01ee9b3fad26d3dd7e4d (head re-checked with `gh pr view 39` at start: unmoved)
- Verifier: independent (did not write the code). Verdict 3 of 4 for VZ-FOUND-005.
- Environment: darwin (macOS 25.5), python3, docker compose CLI used by compose-render.py; fresh clone at /tmp/vzv-vizra-pr39-Ddgr8J (deleted at end).
- vizra-core read at main 0c79669 (contains merged #24 = 84a3da7).

## Core support (read, not run)
- `cmd/vizra/main.go:49` dispatches `healthcheck`; `cmd/vizra/healthcheck.go` returns `healthcheck.Run` exit code directly.
- `internal/healthcheck/healthcheck.go:103-116` targets `api` (VIZRA_LISTEN_ADDR, /readyz) and `worker` (VIZRA_METRICS_ADDR, /readyz); `:68-72` exit 0 ready / 1 not ready / 64 usage; `:79` DefaultTimeout = 2s, applied as one context deadline (`:248`), under compose `timeout: 3s`; non-2xx → 1 (`:255`).
- docker-compose.yml:75/78 set VIZRA_LISTEN_ADDR ":8080" and VIZRA_METRICS_ADDR "127.0.0.1:9090" — both dialable on loopback by the probe.

## Lanes (fresh clone, at SHA)
| command | exit | result |
|---|---|---|
| `python3 scripts/compose-render.py --all` | 0 | 15 shapes rendered |
| `python3 scripts/check-compose-topology.py build/compose-models` | 0 | 15 shapes, 30 rules, 0 violations, 1 known-false probe (otel-collector) |
| `bash tests/bundle/bundle_test.sh` | 0 | PASS: 10 cases |
| `python3 scripts/check-config-coverage.py` | 0 | 0 violations |
| `python3 scripts/check-doc-links.py` | 0 | 29 relative links resolve |

The full demo.sh was not run (time limit; it has no case selection). Cases 15/15b/15c/15d were reproduced by hand as M1–M6 below. Chair's full run on this SHA: `RESULT: 99 assertion(s) passed, 0 failed, across 52 case(s)` (PR comment, not re-run by me).

## Mutations (each: mutate → render → check; restore → render → check)
Script: /tmp/.../mut.sh (python replace asserting one match; restore = stash+drop in the scratch clone).
- M1 api probe → `vizra version`: RED exit 1, `required-probe` service=api in every shape with api, and `gated-probe-unrecognised` (frontend gate). Restored: GREEN exit 0.
- M2 worker probe → `vizra version`: RED exit 1, `required-probe` service=worker (dev-default, bundle-no-checkouts, dev-build-from-checkouts, …). Restored: GREEN exit 0.
- M3 `required_probes` key renamed out of compose-shapes.json: exit 2 `UNEVALUABLE: the shape manifest declares no required_probes` — fails closed. Restored: GREEN.
- M4 compose-render.py stops forwarding `required_probes`: exit 2 same UNEVALUABLE — the earlier inertness cannot recur silently. Restored: GREEN.
- M5 frontend `depends_on.api.condition` → `service_started`: STAYS GREEN (exit 0, 0 violations; restored also green). No rule asserts that the frontend → api edge is `service_healthy`. See finding F1.
- M6 api probe → `vizra healthcheck worker` (right binary, wrong target): RED exit 1, `required-probe` + `gated-probe-unrecognised` on api. Restored: GREEN.
- Builder's red/green file docs/evidence/VZ-FOUND-005/red-green.txt matches what M1/M2 show.

## Does the assertion prove the api probe tests readiness?
Within what a static model can prove, yes: it asserts on the RENDERED model (post-overlay, post-interpolation) that argv[0] basename is `vizra` and argv[1:] starts with `healthcheck api` (resp. `worker`) in every shape containing the service — so `vizra version`, `vizra healthcheck worker` on api, and CMD-SHELL wrapper forms are refused (probe_invokes shell-control guard pre-exists). That the binary inside the image really implements /readyz semantics is proven by vizra-core's own tests (#24, verified) — not by this lane — and that the container goes unhealthy with PostgreSQL stopped needs a running stack: that is the boot lane (VZ-CI-003), honestly scoped in the checker's own SCOPE output.

## CI on this SHA
`gh api repos/yegamble/vizra/commits/1ee80cf…/check-runs`: ci-required success, validate success, GitGuardian success. `.github/required-checks.txt` lists exactly `validate`, which ran. No skipped/missing required lane.

## Cases for VZ-FOUND-005
- CLOSES (meta part): evidence_required "rendered compose model assertion" — api/worker probes are `vizra healthcheck api|worker` and asserted per shape, fail-closed; frontend gated `service_healthy` on api.
- STAYS OPEN: evidence_required "command transcript with exit code on the declared clean target"; negative "Stopping PostgreSQL turns /readyz non-200 within the declared interval" and recovery "Probe recovers without restart" observed through compose health — boot lane VZ-CI-003. Ledger `outcome` text still says /readyz fails when Redis unavailable; owner decision 2026-11-12 #8 changes it to `degraded` — that edit goes through the ledger generator and is not in this PR (not a defect of this PR).

## Findings
FINDING F1: frontend → api `service_healthy` gate is not asserted by any rule
Severity:    SHOULD (FOLLOW-UP — not blocking)
Confidence:  high
Affected:
  repo: vizra; files: docker-compose.yml (frontend depends_on api), scripts/check-compose-topology.py; requirements: VZ-FOUND-005
Observed:
  M5 (condition → service_started) renders and checks GREEN, exit 0, 0 violations. PR body line 24 lists "frontend gates on api service_healthy" under the rendered compose model assertion; body line 6 claims only that any service_healthy gate lands on a real probe, which M1/M6 confirm.
Failure:
  The gate can be quietly removed again. That does not make a check false-green for what VZ-FOUND-005 requires (api/worker probes are real and asserted; `--wait` still reads them). frontend would only start before the api is ready. Not a privacy, auth, data-loss or false-gate defect in today's tree, where the edge is `service_healthy`.
Perspective: operator
Recommendation:
  Add a `required_gates` entry (frontend→api: service_healthy) checked in every shape that has both services, plus a demo case; or remove line 24's wording.

FINDING F2: README / env still say "Real probes land with `vizra healthcheck` (vizra-core, queue 2h)"
Severity:    NIT (FOLLOW-UP)
Confidence:  high
Affected: repo: vizra; files: README.md:114, env/production.env.example:195, docs/META_REPO.md:156-160 ("both probes are declared known-false … why frontend → api is service_started")
Observed: these lines describe the pre-PR state, while the paragraphs above them were updated.
Failure: they confuse an operator about which probes are real. The disclosures the checker enforces for otel-collector are present and correct.
Recommendation: reword so they refer to otel-collector only.

No BLOCKING findings.

## Verdict
Every claim except the frontend-gate wording (F1) reproduced, and F1 does not change what VZ-FOUND-005 proves. CI is green on this SHA. PASS with 2 follow-ups.

FINAL VERDICT: PASS — SHA 1ee80cf38ec792e5967c01ee9b3fad26d3dd7e4d
