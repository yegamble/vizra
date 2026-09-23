# Workflow catalogue for the workflow sentinel

This is every workflow a person or CI is told to run, as documented on `main`. `vizra-sentinel-workflows` sweeps it in rotation. A sweep takes the entries with the oldest **Last swept** date, and the chair updates that column when merging a sweep. Add an entry whenever a PR documents a new workflow.

| ID | Workflow | Where it is documented | Repos | Last swept |
|---|---|---|---|---|
| W-OP-1 | Operator install and first boot with the compose shapes: render, `docker compose up`, all services healthy | meta README / `docs/quality/COMMANDS.md` §4–6, `deploy/` | meta, core, user, search | never |
| W-OP-2 | First-run owner claim: `vizra` issues the claim token, claim-status is unclaimed, the claim succeeds once, a second claim gets 409, rate limits apply | core README / AGENTS.md (M1-A) | core | 2026-09-23 (S-0011…S-0020) |
| W-OP-3 | Health and diagnosis: `vizra healthcheck api|worker`, `vizra doctor` (cache floor, unclaimed warning), readiness with the cache down | core README | core, meta compose | 2026-09-23 (S-0011…S-0020) |
| W-OP-4 | Configuration: every template key documented, `config-template-check`, a boot refused on a bad value with a named error | core `.env.example`, meta `check-config-coverage.py` | core, meta | never |
| W-DEV-1 | Core developer loop: `make ci`, `make test-integration` (Valkey and Redis 7.2), `sqlc-verify`, `openapi-verify`, `migrate-lint`, `fixtures-verify` | core AGENTS.md / README / COMMANDS | core | 2026-09-23 (S-0011…S-0020) |
| W-DEV-2 | User developer loop: `npm ci`, `npm run ci`, `npm run e2e` (Lane A), `e2e:demos`, `codegen` then `check:contract` | user AGENTS.md / README | user, core (spec) | never |
| W-DEV-3 | Search developer loop: `make ci`, `contract-drift`, `vendor-contract-check`, `boot-matrix`, `run` | search AGENTS.md / README | search, core | never |
| W-DEV-4 | Meta validate lane: the ledger generator reproduces, quality JSON, doc links, compose checks, `ci-required-guard`, `demo.sh` | meta `docs/quality/COMMANDS.md` | meta | never |
| W-XR-1 | Contract vendoring: core spec change → user `codegen` + `check:contract`; search `vendor-contract` from core, then its check | user and search READMEs | core, user, search | never |
| W-XR-2 | Release pinning: the meta repo pins component tags and image digests, and the compose shapes pull exactly those | `docs/META_REPO.md` | all | never |
| W-CI-1 | Each repo's CI on a fresh PR: every `required-checks.txt` lane runs, selects non-zero tests, and `ci-required` fans in correctly | each `.github/` | all | never |
| W-CI-2 | Scheduled or supply-chain workflows (`supply-chain.yml`, `image-scan`, `govulncheck`) run, produce valid reports, and fail on what they claim to | each `.github/` | core, user | never |

Coverage gaps the sentinel should also report: a workflow the product promises (see `docs/PRODUCT_CHARTER.md` and the ledger) that has NO documented way to run yet is logged as a MINOR "undocumented workflow". It is not a failure.
