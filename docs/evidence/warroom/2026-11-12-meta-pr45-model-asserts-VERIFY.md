# Verify — vizra (meta) PR #45 — VZ-CI-002 / VZ-OPS-008 model assertions

- SHA: 6ebb99c03ba8df0ced4c81ca41c3cad97433f9d6 (I compared it with `gh pr view 45 --json headRefOid`. They match.)
- Verifier: independent (I am not the builder). Environment: darwin, a fresh clone in `/tmp/vzv-vizra-pr45-4J0mKc` (deleted afterwards).
- Budgets on entry: VZ-CI-002 0/4, VZ-OPS-008 0/4. This verdict spends 1 of each.

## Commands (clean clone, all at the SHA)
| Command | rc | Result |
|---|---|---|
| `bash tests/ci/test_compose_model_asserts.sh` | 0 | passed=9 failed=0 (65 s). Every mutation printed a before→after sha256 prefix, and every red named its rule |
| `./scripts/check-secrets-untracked.sh` | 0 | `secrets-untracked: OK` |
| `./scripts/compose-render.py --all --out build/compose-models` | 0 | 15 shapes, including bundle-no-checkouts |
| `./scripts/check-compose-topology.py build/compose-models` | 0 | 15 shapes, 30 rules, 0 violations, 1 known-false probe disclosed |
| `python3 scripts/check-config-coverage.py` | 0 | 0 violations |
| `python3 scripts/check-action-pins.py` | 0 | 7 action refs, all pinned to 40-hex SHAs |
| `python3 scripts/check-workflows.py` | 0 | no continue-on-error |
| `python3 scripts/check-lane-integrity.py` | 0 | 1 required lane, no conditional step |
| `bash tests/bundle/bundle_test.sh` | 0 | PASS: 10 cases |
| `shellcheck` on both new scripts | 0 | clean |

## Demonstrations
- I reproduced all six harness mutations: docker.sock on api → `rule=docker-socket service=api`; no-new-privileges dropped → `rule=no-new-privileges`; max-file dropped → `rule=missing-log-cap`; new optional `newopt` on 0.0.0.0 → `rule=port-not-allowed service=newopt`; clickhouse on 0.0.0.0 → `rule=never-published service=clickhouse`; force-added env/production.env → `rule=tracked-secret-file`.
- **Test of the harness:** I copied it to `tests/ci/broken.sh` with the max-file mutation's match string changed to `"NOPE"`. The python `assert n != s` raised AssertionError, then `FAIL  mutation did not apply to docker-compose.yml`, `passed=8 failed=1`, rc=1. So a mutation that does not apply turns the harness red. It cannot pass falsely. Afterwards I deleted the copy.

## CI on the SHA
- Run 43288009156 `ci-required` success; run 43288009183 `validate` success. The validate log records the head SHA 6ebb99c… In job `validate`, the steps "model-assert negatives go red …" (log shows all 9 `ok` lines, `passed=9 failed=0`) and "no environment file holding secrets is tracked" (`secrets-untracked: OK`) both ran and succeeded. They sit at validate.yml:373 and :376 inside the required `validate` job, and neither has continue-on-error.

## Clause audit (against check-compose-topology.py RULES, lines 106-135, and scripts/compose-shapes.json)
VZ-CI-002:
- Shapes: compose-shapes.json lists 15 shapes: default, external-tls, worker-split, all-optional, external postgres/redis/clickhouse/ipfs, external-both, the otel combos and bundle. Covered.
- Ports closed: `never-published`, `public-bind`, `port-not-allowed`, `edge-profile` and `host-network` are in RULES. Covered.
- Images pinned: `unpinned-image`. One-shots unbuildable: `production-build` and `oneshot-restart`. Restart/log: `missing-restart` and `missing-log-cap`. Config keys: check-config-coverage.py. All covered.
- Wizard answer coverage: asserted by check-config-coverage.py §3c (line 422, "`vizra setup` answer coverage (VZ-INSTALL-002 S1, VZ-CI-002)"). **The map leaves this clause out.** The clause is asserted, so this is not a false claim. It is follow-up F-1.
- Success bullet (bundle with no checkouts): the bundle-no-checkouts shape and bundle_test.sh pass. Negative bullet: reproduced (`newopt`).
VZ-OPS-008:
- no-new-privileges: rule at check-compose-topology.py:688. Capped logs: `missing-log-cap`. Tag pinning: `unpinned-image`. Secrets untracked: new script. No Docker socket: rule at :728. All covered, and the negative bullet (docker.sock) is reproduced.
- Digest records: the map assigns these to VZ-UPGRADE-002, an out-of-scope claim. Nothing in this PR asserts them.
- **Non-root containers: not asserted by any rule** (RULES has no `user` rule). The map discloses this honestly as a GAP and does not claim it is covered.
- Every clause the map says is asserted is asserted by a real rule. I found no false coverage claim.

## Findings
FINDING 1: The clause map leaves out VZ-CI-002 "wizard answer coverage". Severity SHOULD. The clause is asserted by check-config-coverage.py:422. Add a row to the map. FOLLOW-UP.
FINDING 2: Non-root containers are unasserted. Severity REQUIRED for VZ-OPS-008 closure, but it is disclosed and not claimed, so it does not block. FOLLOW-UP / OPEN.
FINDING 3: Both harness baselines run the same `--all` render on the full tree, so the "bundle-no-checkouts" baseline label proves no more than the first. The real bundle proof is bundle_test.sh. Severity NIT. FOLLOW-UP.
FINDING 4: check-secrets-untracked.sh only covers `.env` patterns. Tracked key or credential files (`*.pem`, `*.key`, `*secret*`) are not caught. Severity SHOULD. FOLLOW-UP.
FINDING 5: Digest records are not asserted here (deferred to VZ-UPGRADE-002). They are part of the VZ-OPS-008 outcome text. FOLLOW-UP / OPEN.

BLOCKING findings: none.

## Per-ID judgement
- **VZ-CI-002: CLOSED by this evidence.** Every clause is asserted, the success and negative bullets are reproduced, and CI is green.
- **VZ-OPS-008: OPEN.** The outcome text requires "non-root containers" and "(digest records)". Neither is asserted, so VZ-OPS-008 cannot be recorded as complete or VERIFIED from this PR. The negative bullet (docker.sock) and the other clauses are reproduced. The PR's own claims are true, so the PR itself passes.

FINAL VERDICT: PASS — SHA 6ebb99c03ba8df0ced4c81ca41c3cad97433f9d6
