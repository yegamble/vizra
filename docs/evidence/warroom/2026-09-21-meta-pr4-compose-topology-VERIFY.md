# Independent verification — meta PR #4, VZ-ISSUE-002 (compose topology)

> **Round 1 verdict below is SUPERSEDED.** The builder's fix round 1 moved the
> head to `3261ad3e`. See **“Re-verification at 3261ad3 (2026-09-21)”** at the
> end of this file for the current verdict.

## Round 1 — verification at 69e197e (2026-09-21)

**Verdict: FAIL** — every VZ-ISSUE-002 acceptance bullet reproduced MET by my own
evidence, `validate` and `ci-required` green on the verified SHA, but one
**BLOCKER** finding outside the acceptance bullets: the renderer's secret
redaction is a dead control and the models it writes — including the ones
uploaded as a CI artifact — are stamped `"secret_values_redacted": true` while
carrying the unredacted values.

| | |
|---|---|
| Repository | `yegamble/vizra` (META) |
| PR | https://github.com/yegamble/vizra/pull/4 |
| Head SHA verified | `69e197e1583d9adb90b0130b4a7c28d78b0878a3` |
| Branch / base | `feat/m0-compose-topology` → `main` (`6b8158c3`) |
| Head moved during verification? | No. `gh pr view 4` at start and the checks below both read `69e197e1`. |
| Verifier | independent; did not write any of this code |
| Date | 2026-09-21 |

## Environment

Fresh clone, **not** the builder's worktree:
`/private/tmp/claude-501/-Users-yosefgamble-github-vizra/7321b930-95d2-4a95-ba2e-61ef2ce3c13c/scratchpad/verify/meta`
(`git clone --no-checkout` + `git fetch origin 69e197e…` + `git checkout 69e197e…`;
`git rev-parse HEAD` = `69e197e1583d9adb90b0130b4a7c28d78b0878a3`).

| | |
|---|---|
| Platform | macOS (darwin 25.5.0), arm64 |
| Python | 3.9.6 (system), PyYAML 6.0.3 |
| Docker Engine | 29.8.0 |
| Docker Compose | **v5.5.1** (CI ran v2.38.2 / Engine 28.0.4 — both above the 2.24.4 floor) |
| Containers started | **zero**. Only `docker compose config` was invoked. |

**No registry contact.** `scripts/compose-render.py` builds its command at
`scripts/compose-render.py:315-321` as
`docker compose -f … --env-file … [--profile …] config --format json` and, for
the variables, `config --variables --format json`. There is no `pull`, no
`build`, and no `--resolve-image-digests` anywhere in the file (grepped). All
twelve shapes rendered in **1.85 s wall clock**, which is not a registry round
trip. Images are read as strings.

## 1. The documented CI entry point, run from the clean clone

Commands exactly as `docs/quality/COMMANDS.md` and `.github/workflows/validate.yml`
give them. Run from the repository root.

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `./scripts/check-generated-ledger.sh` | 0 | `generated ledger reproduces byte-for-byte: docs/quality/features.json (UTF-8 and C/POSIX locales)`; 191 requirements, core=141 |
| 2 | `./scripts/check-quality-json.py` | 0 | 4 JSON files parsed; 191 ledger ids; 287 ids (204 distinct) across 14 documents, all resolve |
| 3 | `./scripts/check-doc-links.py` | 0 | `relative links: none exist yet across 94 markdown file(s) (checked nothing); 7 external URL(s) recorded and not fetched` |
| 4 | `./scripts/ci-required-guard.sh` | 0 | floor `validate` present; 6 / 7 / 10 negative fixtures exercised (floors 6 / 7 / 10) |
| 5 | `./scripts/compose-render.py --list` | 0 | 12 shapes listed |
| 6 | `./scripts/compose-render.py --all --out build/compose-models` | 0 | **12 shapes rendered**; `docker compose 5.5.1 (parsed 5.5.1) meets the floor 2.24.4 (Q-017)` |
| 7 | `./scripts/check-compose-topology.py build/compose-models` | 0 | `12 shape(s) asserted from their rendered models; 19 rules, 0 violations` |
| 8 | `./scripts/check-config-coverage.py build/compose-models` | 0 | `34 component keys across 3 components, 47 template keys, 47 interpolated variables, 12 shapes; 2 declared alias(es); 0 violations` |
| 9 | `./scripts/check-config-coverage.py --drift` (no checkouts) | **2** | `BLOCKED: the drift check needs the component checkouts…` — BLOCKED, not a pass, as documented |
| 10 | `bash docs/evidence/compose-topology/demo.sh` | 0 | `RESULT: 32 assertion(s) passed, 0 failed`; `tree is clean - every mutation was reverted` (confirmed independently with `git status --porcelain`) |

Test counts match the builder's claims exactly: **12 shapes, 19 rules, 0
violations; 34 / 47 / 47 / 2 in the coverage line; 32 demo assertions**. No
skipped, cancelled or uncollected check.

## 2. Every shape judged from the rendered model, by me

I did **not** trust the builder's renderer. I wrote my own render script
(replicating only the `-f` chain, `--env-file`, `--profile` list and the CI
placeholder environment from `scripts/compose-shapes.json`) and invoked plain
`docker compose config --format json`, then audited the JSON myself. The service
sets, ports, restart policies, log caps, healthchecks, build keys and images
below are read from **my** models, and they agree with the builder's.

### Port closure — the finding that matters most

| Service | Published in **any** of the 12 shapes | Verified |
|---|---|---|
| `postgres` | **nothing** | ✅ |
| `redis` (Valkey — the cache) | **nothing** | ✅ |
| `search` | **nothing** | ✅ |
| `clickhouse` | **nothing** | ✅ |
| `migrate`, `worker` | **nothing** | ✅ |
| `api` | `127.0.0.1:8080→8080/tcp` only | ✅ loopback |
| `frontend` | `127.0.0.1:3000→3000/tcp` only | ✅ loopback |
| `caddy` | `80→80`, `443→443` (all interfaces) — **only** under profile `edge` | ✅ declared `"public": true` with a reason |
| `ipfs` | `4001/tcp` + `4001/udp` (all interfaces) — only in `prod-all-optional` and `bundle-no-checkouts` | ✅ declared public with a reason; Kubo API 5001 and gateway never published |

No service in any shape declares `network_mode: host`, `privileged: true`, or a
`docker.sock` bind mount. `caddy` is the only service outside `edge` → nothing:
`check_edge` rejects `caddy` without the `edge` profile (proved by mutation
below), and `caddy` does not render in `prod-external-tls`, which is the whole
point of `VIZRA_TLS_MODE=external`.

### Lifecycle, build and pinning, all twelve shapes

- Every long-running service: `restart: unless-stopped`, `logging.driver:
  json-file` with **both** `max-size: 10m` and `max-file: "5"`, and a
  `healthcheck.test`. Verified per service per shape from my own models.
- `migrate` (the only one-shot rendered): `restart: "no"`, no healthcheck — correct.
- **No `build:` in any of the ten production shapes.** `build:` appears only in
  `dev-build-from-checkouts`, on `migrate`, `api`, `worker`, `frontend`,
  `search` — which is the shape's declared `requires_build` set.
- No image is `latest` or untagged in any production shape. Third-party images
  are digest-pinned (`postgres:18@sha256:86c951e0…`, `valkey/valkey:9.1.2@sha256:c123e371…`,
  `caddy:2.11.4-alpine@sha256:de23def3…`, `clickhouse/clickhouse-server:25.8@sha256:0152dd51…`,
  `ipfs/kubo:v0.39.0@sha256:41ad6d8c…`); Vizra images come from `VIZRA_*_TAG`
  (`ghcr.io/yegamble/vizra-core:v0.0.0-ci` in the render). See **FINDING 4** on
  what the checker does and does not enforce about that.

### Shape membership — absence proved, not assumed

| Shape | Services rendered | The load-bearing fact |
|---|---|---|
| `dev-default` | api, frontend, migrate, postgres, redis, search, worker | no caddy |
| `dev-build-from-checkouts` | same + `build:` on the five component services | really builds |
| `prod-default` | api, caddy, frontend, migrate, postgres, redis, worker | caddy present |
| `prod-external-tls` | api, frontend, migrate, postgres, redis, worker | **caddy absent** |
| `prod-worker-split` | **worker only** | api, frontend, migrate, the datastores all absent — the split is real |
| `prod-all-optional` | all ten | the port-closure authority |
| `prod-external-postgres` | api, caddy, frontend, migrate, **redis**, worker | **postgres container dropped**, not left running unused |
| `prod-external-redis` | api, caddy, frontend, migrate, **postgres**, worker | **redis container dropped** |
| `prod-external-both` | api, caddy, frontend, migrate, worker | **no datastore at all on this host** |
| `prod-external-clickhouse` | …, no `clickhouse` | analytics profile ON, **still no container** |
| `prod-external-ipfs` | …, no `ipfs` | ipfs profile ON, **no container and therefore no swarm port** |
| `bundle-no-checkouts` | all ten, no `build:` | rendered from a tree with `vizra-core`/`vizra-user`/`vizra-search` **absent** |

`bundle-no-checkouts` renders from a temporary tree that also **excludes**
`docker-compose.override.yml` and `docker-compose.dev.yml`
(`scripts/compose-render.py:252-262`), so the developer shapes are not merely
absent from the chain by luck — they are excluded by construction, which is
also why no dev shape needs to fail there. The component directories were
absent in my clone in any case (they are gitignored), and I confirmed the
bundle tree is built by copying **in** rather than by trusting that.

### Compose floor asserted from the engine, not a comment

`scripts/compose-render.py:85-97,464` runs `docker compose version --short`,
parses it numerically (tuple, so `2.9 > 2.24` cannot happen), refuses below
`(2, 24, 4)` and **fails closed with exit 2** on a version string it cannot
parse. My run printed `docker compose 5.5.1 (parsed 5.5.1) meets the floor
2.24.4 (Q-017)`; CI printed the same for v2.38.2.

## 3. Demonstrations reproduced, and the checker attacked

### 3a. The builder's demonstrations

`bash docs/evidence/compose-topology/demo.sh` from the clean clone: **exit 0, 32
assertions passed, 0 failed**, 18 labelled cases (0, 1, 2, 3, 4, 5, 6a, 6b, 6c,
7, 8a, 8b, 9a, 9b, 10a, 10b, 11, 12). Each case prints a sha256 before and after
its mutation and refuses to score a case whose mutation did not apply; the run
ends with `tree is clean - every mutation was reverted`, which I confirmed
independently with `git status --porcelain` (empty). Each red carries the
declared rule id (`rule=never-published`, `rule=public-bind`, `rule=edge-profile`,
`rule=missing-restart`, `rule=missing-log-cap`, `rule=missing-healthcheck`,
`rule=production-build`, `rule=unpinned-image`, `rule=service-key-missing`,
`rule=template-key-unused`, the DSN messages, and the shape-floor refusal).

### 3b. My own attack matrix

Applied by me to the clean tree, one at a time, each restored with
`git checkout -- .` and the tree re-confirmed clean.

| Attack | Caught? | Rule / note |
|---|---|---|
| `ports:` in **long syntax** on postgres (`target`/`published`/`host_ip`/`mode: host`) | ✅ | `never-published`, 9 shapes |
| **empty `host_ip`** (`":5432:5432"`) — Docker treats empty as all interfaces | ✅ | normalised to `0.0.0.0` at `check-compose-topology.py:190-212`; `never-published` in all 12 shapes |
| **`0.0.0.0`** on api | ✅ | `public-bind` |
| **`[::]`** on api | ✅ | `public-bind` (`LOOPBACK_HOST_IPS` is `{127.0.0.1, ::1}`, so `::` is public) |
| **port range** `127.0.0.1:5432-5434:5432-5434` | ✅ | expands to three entries, three `never-published` hits each shape |
| **env-interpolated port** that is empty by default (`${PG_PORT:-}5432:5432`) | ✅ | `never-published` |
| **`network_mode: host`** | ✅ | `host-network` |
| port published via an **`include:`d file** | ✅ | `never-published` — the rendered model resolves `include:` |
| port published via **`extends:`** from another file | ✅ | `never-published` |
| **profile-gated duplicate service** on a profile a shape enables (`analytics`) | ✅ | `port-not-allowed` + `missing-log-cap` + `missing-healthcheck` + `no-new-privileges` |
| **caddy smuggled in via `profiles: []`** | ✅ | `edge-profile` **and** `unexpected-service` |
| **per-service log driver** changed to `local` | ✅ | `missing-log-cap` |
| **`restart: "no"`** on a long-running service | ✅ | `missing-restart` |
| **`healthcheck: disable: true`** | ✅ | `missing-healthcheck` |
| `expose:` instead of `ports:` on postgres | n/a — **correctly not a violation**: `expose` publishes nothing to the host |
| **`healthcheck: test: ["NONE"]`** | ❌ **MISSED** | see **FINDING 2** |
| **a service on a profile no shape enumerates** | ❌ **MISSED** | see **FINDING 3** |
| a production image pinned by **tag only** (`postgres:18`) | ❌ not refused | by design (`image_is_pinned` accepts any non-`latest` tag) — see **FINDING 4** |
| an allowed port number republished over **UDP** | ❌ not refused | loopback-only today, so harmless — see **FINDING 8** |
| an **override file the lane does not render** | n/a | a production chain uses explicit `-f`, so `docker-compose.override.yml` is never auto-loaded into it; the dev shapes do render it and are asserted |

## 4. Configuration-key coverage

### Snapshots vs the components' `main` branches, today

The component checkouts under `/Users/yosefgamble/github/vizra/` were treated as
**read-only**: I materialised each registry's `source_files` from
`git -C <component> show origin/main:<path>` into a temporary directory inside
my clone, ran `--drift`, then deleted them (`git status --porcelain` clean
afterwards).

```
./scripts/check-config-coverage.py --drift
config registry drift: every snapshot matches its component source     exit=0
```

Materialised from `origin/main` of each component:
`vizra-core/internal/config/keys.go`, `internal/config/config.go`, `.env.example`;
`vizra-user/lib/config.ts`, `Dockerfile`;
`vizra-search/internal/config/config.go`, `Dockerfile`, `AGENTS.md`.

| Component | Snapshot `source_commit` | `origin/main` today | Verdict |
|---|---|---|---|
| vizra-core | `c043df72f06cc7b5…` | `c043df72f06cc7b5…` | ✅ identical |
| vizra-search | `808a5499dae1d589…` | `808a5499dae1d589…` | ✅ identical |
| vizra-user | `77305009a7ae5b20…` | `90896beb9669a3b3…` | ⚠️ different commit — see **FINDING 7**. `git diff origin/main 7730500 -- lib/config.ts Dockerfile` is **empty**, so the snapshot content is true to `main` today. |

And the BLOCKED path is real: with the checkouts absent, `--drift` exits **2**
with `BLOCKED: … This is BLOCKED, not a pass and not a skip.` It is never
reached in CI (`validate.yml` runs `check-config-coverage.py` without `--drift`),
which is stated in `env/registry/README.md` and `COMMANDS.md` §6 rather than
papered over.

### Both directions are red

Reproduced by running the builder's demo cases 9a and 9b and reading the
violation lines:

- a key added to a component snapshot with **no template entry** →
  `VIOLATION rule=service-key-missing` (exit 1);
- a template key **nothing consumes** →
  `VIOLATION rule=template-key-unused subject=env/production.env.example/VIZRA_KEY_NOBODY_READS detail=no compose file in any rendered shape interpolates it, so setting it does nothing at all` (exit 1).

Both restored to exit 0. The "consumed" side is Compose's own
`config --variables` output recorded in `shapes.json`, not a grep for `${`.

### The two aliases

`env/registry/aliases.json` declares `floor: 2` and exactly two entries, and
`check-config-coverage.py:243-274` enforces `floor == len(aliases)` (rule
`alias-floor`) plus that each operator key has a template entry and each service
key exists in that component's snapshot (rule `alias-unwired`). So a **third**
alias cannot be added without moving the floor in the same diff.

1. `SEARCH_HMAC_KEY` → `vizra-core: VIZRA_SEARCH_HMAC_KEY` + `vizra-search: SEARCH_HMAC_KEY`.
   Marked `authorised_by: "war-room chair ruling, VZ-ISSUE-002 brief"`. **Matches
   the authorisation the chair states.**
2. `VIZRA_PUBLIC_ORIGIN` → `vizra-core: VIZRA_PUBLIC_ORIGIN` + `vizra-user: PUBLIC_ORIGIN`.
   Marked `authorised_by: "NOT YET RULED ON. Found while implementing
   VZ-ISSUE-002 and REPORTED…"`.

**Answer to the chair's question: the code tolerates the second alias silently.**
The checker has no notion of "authorised" at all — it counts entries against
`floor` and checks wiring. The `NOT YET RULED ON` string is prose inside a JSON
file that no check reads, and the lane prints only `2 declared alias(es)`. The
declaration is honest and it is also in `docs/META_REPO.md` §2a, so this was
reported rather than hidden; but nothing makes it visible in a green run.
See **FINDING 6**.

### No secret has a default value in a production template

Read from `env/production.env.example`, cross-referenced against the
`secret: true` keys in the three registries:

```
VIZRA_SESSION_SECRET=    VIZRA_MFA_KEY_KEK=    SEARCH_HMAC_KEY=
POSTGRES_PASSWORD=       DATABASE_URL=         VIZRA_CACHE_URL=
CLICKHOUSE_PASSWORD=
```

All seven are **blank**. `env/development.env.example` carries obvious
`local-development-*` placeholders, which is the correct behaviour for a
developer template that never reaches a production chain — and
`check-config-coverage.py:232-241` (`hatch-in-production-template`) plus
`check-compose-topology.py:400-418` (`dev-mode-in-production`,
`dev-hatch-in-production`) prove the developer override cannot leak into one.

### The `VIZRA_SEARCH_MODE` clash

Confirmed against the components' `main`:

- `vizra-core` `internal/config/keys.go:53` — `VIZRA_SEARCH_MODE`, `Default: "off"`,
  `"off | managed | external"`, validated at `internal/config/config.go:227`.
- `vizra-search` `internal/config/config.go:121` — `EnvMode = "VIZRA_SEARCH_MODE"`,
  meaning `production | development`.

The compose files keep them apart by having **no `env_file:` on any service** —
I confirmed this from the rendered model, not the YAML: every service's
`env_file` key is absent in all twelve models. `docker-compose.yml:87` feeds core
`${VIZRA_SEARCH_MODE:-off}`; `docker-compose.yml:329` sets the search service's
value **literally** to `production`. Rendered in `prod-all-optional`:

```
api    VIZRA_SEARCH_MODE = 'off'
worker VIZRA_SEARCH_MODE = 'off'
search VIZRA_SEARCH_MODE = 'production'
```

The builder's report of this is accurate.

## 5. Invalid / missing external DSN

`env DATABASE_URL=<value> ./scripts/compose-render.py --shape prod-external-postgres --out …`

| Case | Exit | Message names the variable? | Value echoed? |
|---|---|---|---|
| empty / missing | 1 | yes — `DATABASE_URL is empty, but docker-compose.external-postgres.yml is in the chain and requires it.` plus the expected form and why no fallback is started | **no** |
| malformed scheme (`mysql://…`) | 1 | yes — `DATABASE_URL is not a valid DSN: it does not start with postgres:// or postgresql://.` | **no** |
| no host (`postgres://`) | 1 | yes — `DATABASE_URL names no host.` | **no** |
| valid, password containing `@` **and** `#` | 0 | renders | **the value reached the written model — see FINDING 1** |

The three failure messages each end with `(The value is not echoed here; it
carries a password.)` and I grepped stdout+stderr for the password substring:
**0 hits** in every failing case. The failure path is clean.

The **success** path is not: with a valid DSN the rendered model written to disk
contains the full DSN including the password, under a file stamped
`"secret_values_redacted": true`. That is FINDING 1, below.

## 6. History rewrite — ruling

Facts, from `gh api`:

- PR #4 head is `69e197e1`; its two commits are `b3ee44db` (the squash) and
  `69e197e1`.
- The four superseded commits `aa9af5dd`, `67526fd9`, `864f77f5`, `b206d51e`
  still exist on the server and each compares `ahead` of `main` — i.e. **`main`
  is their ancestor and never contained them.**
- `main` is `6b8158c3`, unchanged. The only other branch on the server is
  `chore/warroom-records-2026-09-21` (`440b0948`), which is not based on any
  superseded commit. PRs #2 and #3 are merged and predate this branch. **Nothing
  was based on the rewritten commits.**
- The placeholder is **gone from the head tree**: `grep -rn 'postgres://user:password'`
  over the checkout returns nothing, and a `git grep` for
  `user:password@ / password@host` across all 81 commits reachable from HEAD
  returns only *prose* mentions (`scripts/compose-shapes.json:32` explaining why
  the placeholder was dropped, and a sentence in an earlier verification report).
  No credential-shaped DSN survives in reachable history.
- **But** the string is still served by the GitHub API at the dangling SHA:
  `gh api repos/yegamble/vizra/commits/864f77f5` returns a patch containing
  `user:password@host`. A force-push removes a commit from a ref, not from
  GitHub's object store.

**Ruling: acceptable, with a caveat.** The builder's role contract
(`.claude/agents/warroom/vizra-builder.md:15`) says *"never force-push a **shared**
branch"*. `feat/m0-compose-topology` was the builder's own PR branch, unreviewed,
with nothing downstream and `main` untouched — that is not a shared branch under
any reading, and the rewrite is within the rule. Two caveats for the record, both
non-blocking: (a) the remediation is **incomplete** — the flagged string remains
retrievable by SHA, so if it had been a real credential it would still need
rotating; it is a self-evident placeholder, so nothing needs rotating; (b) the
rewrite orphaned the CI results of four SHAs, and the shipped transcripts still
name one of them (FINDING 9).

## 7. Truthfulness of the documentation

Checked line by line against what I observed.

| Claim | Where | Verdict |
|---|---|---|
| "Nothing in this repository starts a container… 'The port is closed' means the model publishes nothing, not that a running host was scanned." | `docs/META_REPO.md` §2a | ✅ **true** — I started no container and the lane starts none |
| "`api` and `worker` declare a healthcheck that runs `vizra version` … It proves the binary runs; it does **not** prove `/readyz` answers … `vizra-core` has no `healthcheck` subcommand (`vizra-search` has exactly that)." | §2a | ✅ **true** — rendered test is `["CMD","/usr/local/bin/vizra","version"]`; `vizra-search` `cmd/vizra-search/main.go:79` has `case "healthcheck":`; no such case in `vizra-core/cmd` on `origin/main` |
| "none of the three component repositories ships a compose file" | §2a table | ✅ **true** — `git ls-tree -r origin/main` in all three returns no compose file |
| "a green `validate` does **not** prove the snapshots are current… `--drift` cannot run in CI at all and reports BLOCKED, exit 2" | `env/registry/README.md`, `COMMANDS.md` §6 | ✅ **true** — reproduced, exit 2 |
| "**What this does NOT prove.** It proves what the *model* declares. It has never started a container…" | `COMMANDS.md` §5 | ✅ **true** |
| "`bundle` and `boot` are **not built**" | `COMMANDS.md` | ✅ **true** — neither exists, and neither is in `.github/required-checks.txt` |
| "Declared secret values are redacted from every model before it is written, and the renderer re-scans the redacted model … and refuses to write a file that still contains one." | `COMMANDS.md` §4; `scripts/compose-render.py` docstring lines 22-28 | ❌ **FALSE** — **FINDING 1** |
| `"secret_values_redacted": true` in every written model | `scripts/compose-render.py:397` | ❌ **FALSE** — **FINDING 1** |
| `README.md` | — | unchanged by this PR; makes no claim about compose or ports. ✅ nothing to correct |

### `.github/required-checks.txt` — confirmed and ruled

**Confirmed.** The file is **not** in this PR's diff (`git diff --name-only
origin/main...HEAD` has no match), and it still says:

> "Only `validate` exists today: **there is no compose file**, no installer, no
> bundle and no image to boot…"

At this head there *is* a compose file, so that clause is now false. **Ruling:
the builder was right not to edit it here.** `AGENTS.md` ("Tests, workflows,
manifests … require independent review") and the file's own header ("This file is
owner-reviewed (CODEOWNERS): it must not be edited in the same PR as the thing it
guards") both forbid it. `validate.yml` states the deviation in its own header
comment and calls the sentence "REPORTED, not silently fixed", which is the
correct disposition. Recorded as **FINDING 5** for a separate owner-reviewed
follow-up. It changes no behaviour: the manifest's one live line, `validate`, is
correct.

## 8. Scope

| Check | Result |
|---|---|
| Any component repository modified? | **No.** `git diff --name-only origin/main...HEAD` matches nothing under `vizra-core`/`vizra-user`/`vizra-search`. 27 files changed, all meta-repo files. |
| `docs/quality/features.json` byte-identical? | **Yes.** `git diff --stat origin/main...HEAD -- docs/quality/features.json` is empty. |
| Ledger-DSL experiment fully reverted? | **Yes.** `git diff --stat origin/main...HEAD -- docs/evidence/ledger-generator/` is empty; `build.py:20` still carries the gate verbatim — `if r["implementation_status"]!="PLANNED" or r["verification_status"]!="UNVERIFIED": errors.append(…)`. Nothing of the attempt remains. |
| Secrets in the diff? | **No real secret.** The only credential-shaped strings are the deliberately fake `ci-render-only-*-not-a-real-value` placeholders in `scripts/compose-shapes.json` and the `.invalid` DSNs (RFC 2606). Production template secret fields are all blank. |
| `.github/required-checks.txt` / `scripts/ci-required-guard.sh` edited? | **No.** |

## 9. CI on the verified SHA

`69e197e1583d9adb90b0130b4a7c28d78b0878a3`:

| Check run | Status | Conclusion |
|---|---|---|
| `validate` | completed | **success** |
| `ci-required` | completed | **success** |
| `GitGuardian Security Checks` | completed | success |

(The combined *status* API reads `pending` only because this repository uses
check-runs and posts no commit statuses; `.statuses[]` is empty. Not a gap.)

**The manifest matches what actually ran.** `.github/required-checks.txt`
contains exactly one live entry, `validate`. The `ci-required` log for this SHA
shows the guard printing `required checks: - validate`, then the aggregate
evaluating `69e197e1…`. `validate` ran on this SHA and concluded `success`. No
listed lane went unexecuted; no executed-but-unlisted lane is claimed as a gate.

**Every `validate` step ran and succeeded** (run `35566151734`, 17 steps, none
skipped):
`record the environment and the tree under test` → `the generated ledger matches
its sources` → `quality JSON parses…` → `relative documentation links resolve` →
`ensure a YAML parser is available` → `record the container toolchain…` →
**`render every declared compose shape`** → **`upload the rendered compose
models`** → **`the rendered topology is closed, capped and pinned`** →
**`configuration-key coverage in both directions`** → **`every compose guard
still fails against a controlled mutation`**.

From the CI log:

```
Docker version 28.0.4, build b8034c0
Docker Compose version v2.38.2
… 66 "rendered …" lines (12 shapes × --list and --all across the steps)
compose topology: 12 shape(s) asserted from their rendered models; 19 rules, 0 violations
config coverage: 34 component keys across 3 components, 47 template keys, 47 interpolated variables, 12 shapes; 2 declared alias(es); 0 violations
RESULT: 32 assertion(s) passed, 0 failed
```

Artifact `meta-validate-compose-models`, 33 929 bytes, not expired. I downloaded
it. It contains the twelve models plus `shapes.json` — **and the unredacted
values** (FINDING 1).

Also recorded, because the lane itself says so and it is easy to misread: on a
`pull_request` event `actions/checkout` tests `refs/pull/4/merge`, i.e. the head
merged into `main` **as it stood at 05:52 UTC**. The base moves (the chair commits
the board to `main` every tick). A green `ci-required` on `69e197e1` means that
merge was green then. `main` is `6b8158c3` right now; if it moves before the
merge, the lane should be re-run.

---

# Findings

```
FINDING 1: compose-render.py writes UNREDACTED models and stamps them "secret_values_redacted": true
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/compose-render.py:371-403 (the defect), :406-421 (redact),
             :424-440 (find_leaks, now dead), :397 (the false stamp);
             .github/workflows/validate.yml (the "render every declared compose shape"
             and "upload the rendered compose models" steps);
             docs/quality/COMMANDS.md §4; scripts/compose-render.py docstring lines 22-28
  requirements: VZ-OPS-008, VZ-CI-002

Observed:
  The renderer computes a redacted copy, validates THAT copy, and then writes the
  ORIGINAL:

      redacted = redact(model, set(man.get("redact_keys", [])), secrets)   # :376
      leaked   = find_leaks(redacted, secrets)                             # :377
      … fail() if leaked …
      model["x-vizra-shape"] = { …, "secret_values_redacted": True }       # :388-398
      json.dump(model, fh, indent=2, sort_keys=True)                       # :401  <-- model, not redacted

  `redacted` is never used again. Reproduced on the verified SHA from a clean
  clone:

      $ ./scripts/compose-render.py --all --out build/compose-models
      $ python3 -c "import json; m=json.load(open('build/compose-models/prod-default.json')); \
          print(m['services']['postgres']['environment']['POSTGRES_PASSWORD']); \
          print(m['x-vizra-shape']['secret_values_redacted'])"
      ci-render-only-postgres-password-not-a-real-value
      True

  And with a real-shaped value, which is what the documented local command does:

      $ env DATABASE_URL='postgres://vizra:sup3rs3cr3t@#x@db.ci.invalid:5432/vizra?sslmode=require' \
          ./scripts/compose-render.py --shape prod-external-postgres --out /tmp/m
      $ python3 -c "import json; print(json.load(open('/tmp/m/prod-external-postgres.json'))\
          ['services']['api']['environment']['DATABASE_URL'])"
      postgres://vizra:sup3rs3cr3t@#x@db.ci.invalid:5432/vizra?sslmode=require

  The CI artifact has the same content. I downloaded
  `meta-validate-compose-models` from run 35566151734 (the run for this SHA) and
  ten of its twelve models contain `ci-render-only-…`, each stamped
  `"secret_values_redacted": true`.

  `find_leaks` — the guard whose stated job is "refuses to write a file that still
  contains one" — runs only against the discarded copy. It can never fire on what
  is actually written. It has no demonstration case in demo.sh (cases 0-12 cover
  ports, lifecycle, build, pinning, coverage, DSN, bundle and the shape floor;
  none covers redaction), so nothing would have caught this.

Failure:
  Three separate failures, in increasing order of seriousness:

  1. A dead control. The redaction and its leak-detector do nothing. AGENTS.md:
     "No fake success toasts, dead controls… or mock data in production paths."
  2. A false claim in a published artifact. Every uploaded model asserts
     `secret_values_redacted: true`. Anyone who reads that field — a reviewer, a
     future lane, the operator CLI — is told a thing that is not true about the
     file they are holding. AGENTS.md: "Do not fabricate outputs"; "unsupported
     readiness claims".
  3. A credential-exposure path. COMMANDS.md §4 documents
     `./scripts/compose-render.py --all --out build/compose-models` as the command
     to run, and a developer or operator running it has real values in the shell or
     in `env/production.env` — POSTGRES_PASSWORD, DATABASE_URL, VIZRA_SESSION_SECRET,
     VIZRA_MFA_KEY_KEK, SEARCH_HMAC_KEY. The result is a plaintext file on disk
     labelled "redacted", which is exactly the label that makes someone attach it
     to an issue. AGENTS.md: "Never log credentials, private signed URLs, or raw
     private metadata."

  Nothing real has leaked yet: the only values CI renders are the obviously fake
  `ci-render-only-*-not-a-real-value` placeholders. That is why this is a defect to
  fix before merge rather than an incident.

Perspective:
  operator, developer

Recommendation:
  Two lines. Set the provenance stamp on the redacted copy and write that copy:

      redacted["x-vizra-shape"] = { …, "secret_values_redacted": True }
      json.dump(redacted, fh, indent=2, sort_keys=True)

  Then add the demonstration that was missing, as a new case in
  docs/evidence/compose-topology/demo.sh: render a shape with a recognisable
  secret value in the environment and assert the written model does NOT contain
  it — which is red against the current code and green after the fix. That case
  is what keeps `find_leaks` from going dead again.

Acceptance criteria:
  - Rendering any shape with `POSTGRES_PASSWORD`, `DATABASE_URL`,
    `VIZRA_CACHE_URL`, `VIZRA_SESSION_SECRET`, `VIZRA_MFA_KEY_KEK`,
    `SEARCH_HMAC_KEY` or `CLICKHOUSE_PASSWORD` set to a recognisable value
    produces a model file that does not contain that value anywhere —
    including inside composite strings such as the `DATABASE_URL` built from
    `POSTGRES_PASSWORD` in docker-compose.yml:80.
  - The `secret_values_redacted` field is true only of a file that is redacted.
  - A deliberately un-redacted value (a key removed from `redact_keys`) makes
    the renderer FAIL rather than write the file — i.e. find_leaks fires on the
    bytes that get written.
  - The uploaded `meta-validate-compose-models` artifact contains no value that
    was supplied through a `redact_keys` variable.
  - The negative case is in demo.sh and counted in its assertion total.

Tests:
  docs/evidence/compose-topology/demo.sh, a new "CASE 13 — a declared secret
  value must not survive into a written model", in the existing idiom: digest
  before/after, the mutation being an environment variable rather than a file
  edit (like cases 10a/10b, which already do exactly that), asserting exit and
  a grep over the written file. The harness exists; no new dependency.

Cross-repo implications:
  core: none | user: none | search: none | meta: the fix is entirely in
  scripts/compose-render.py and demo.sh; no compose file, manifest or workflow
  changes.

Challenge:
  "The values are fake, the artifact retention is 14 days, and the repository is
  private — so nothing is actually exposed." True today, and that is why I have
  not called this an incident. It is still blocking, because the defect is in the
  control rather than in the data: the control is inert, the file asserts the
  opposite, and the only thing standing between this and a real credential on
  disk is that nobody has yet run the documented command with a real env file.
  The fix is two lines and one test case.
```

```
FINDING 2: a healthcheck of ["NONE"] defeats the missing-healthcheck rule
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-compose-topology.py:324-333
  requirements: VZ-TOPOLOGY-002, VZ-OPS-008

Observed:
  The rule is

      hc = svc.get("healthcheck") or {}
      if not hc or hc.get("disable") is True or not hc.get("test"):
          violation(… "missing-healthcheck" …)

  `test: ["NONE"]` is a non-empty list, so `not hc.get("test")` is False and the
  rule passes. In Docker, `["NONE"]` is the documented way to DISABLE a
  healthcheck — it is what `disable: true` compiles to.

  Reproduced on the verified SHA. Adding to docker-compose.prod.yml:

      postgres:
        healthcheck:
          test: ["NONE"]
        restart: unless-stopped

  renders (`docker compose … config --format json`):

      {"test": ["NONE"], "timeout": "5s", "interval": "10s", "retries": 10, "start_period": "30s"}

  and the checker says:

      compose topology: 12 shape(s) asserted from their rendered models; 19 rules, 0 violations
      exit=0

  The neighbouring spelling IS caught: `disable: true` produces
  `VIOLATION rule=missing-healthcheck`. So the rule knows about the concept and
  misses one of its two spellings.

Failure:
  A service can be shipped with its healthcheck switched off while the lane
  certifies "19 rules, 0 violations". `depends_on: condition: service_healthy`
  then never becomes satisfiable for that service, so a deploy that relies on
  ordering hangs or proceeds against a datastore that is not ready — and the
  future `doctor` command, which META_REPO §2a says is what healthchecks exist
  for, reports nothing for it. The operator sees a green CI badge for a stack
  whose ordering guarantee is gone.

Perspective:
  operator

Recommendation:
  Treat `["NONE"]` as disabled, next to the `disable` test:

      test = hc.get("test")
      if not hc or hc.get("disable") is True or not test or test == ["NONE"] \
         or (isinstance(test, list) and test[:1] == ["NONE"]):

  (Compose also accepts the string form `test: NONE`, so normalise a str to a
  one-element list first.)

Acceptance criteria:
  - `healthcheck: {test: ["NONE"]}` on any long-running service in any shape
    produces `VIOLATION … rule=missing-healthcheck`, exit 1.
  - `healthcheck: {test: "NONE"}` (string form) does the same.
  - `healthcheck: {disable: true}` still does (no regression).
  - The unmutated tree is still exit 0.

Tests:
  docs/evidence/compose-topology/demo.sh — extend CASE 6c, which today mutates
  only one spelling, into 6c/6d/6e covering "no healthcheck", "disable: true"
  and "test: [NONE]", each declaring rule=missing-healthcheck. The harness
  already scores mutations by declared rule id, so this is three more entries
  in the existing table.

Cross-repo implications:
  core: none | user: none | search: none | meta: checker only.

Challenge:
  "Nothing in the tree writes ["NONE"] today, and a reviewer would notice it."
  A reviewer would notice it in docker-compose.yml. They would not notice it in
  an overlay three files away, which is the exact failure mode this whole
  checker exists to make impossible — and the file's own docstring says so:
  "a source file can look closed while the merge opens it". A rule that catches
  one spelling of a disabled healthcheck and not the other is a rule an author
  can pass by accident.
```

```
FINDING 3: a service on a profile no shape enumerates is never rendered and never asserted
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/compose-shapes.json (the `profiles` list of each shape);
             scripts/compose-render.py:315-321; scripts/check-compose-topology.py:443-478
  requirements: VZ-TOPOLOGY-001, VZ-TOPOLOGY-003, VZ-CI-002

Observed:
  Every shape names its profiles explicitly, and the union across all twelve is
  exactly {core, frontend, edge, worker, search, analytics, ipfs}. A service
  carrying any other profile name renders in NO shape, so no rule ever sees it.

  Reproduced on the verified SHA. Appending to docker-compose.prod.yml:

      pgadmin-tunnel:
        image: alpine:3.22
        profiles: ["backup"]
        restart: unless-stopped
        ports:
          - "0.0.0.0:5432:5432"

  The lane is green:

      $ ./scripts/compose-render.py --all --out build/compose-models && \
        ./scripts/check-compose-topology.py build/compose-models
      compose topology: 12 shape(s) asserted from their rendered models; 19 rules, 0 violations
      exit=0

  The port is nevertheless real:

      $ docker compose -f docker-compose.yml -f docker-compose.prod.yml \
          --env-file env/production.env.example --profile core --profile backup \
          config --format json
      services: ['api','migrate','pgadmin-tunnel','postgres','redis','worker']
      pgadmin-tunnel ports -> [{"mode":"ingress","host_ip":"0.0.0.0","target":5432,
                                "published":"5432","protocol":"tcp"}]

  Note the contrast with the same service on an ENUMERATED profile: putting it on
  `analytics` is caught immediately, with four violations
  (port-not-allowed, missing-log-cap, missing-healthcheck, no-new-privileges).
  The coverage is complete inside the enumerated set and empty outside it, and
  nothing detects the difference.

Failure:
  The guarantee the slice sells — "postgres, the cache and search publish
  nothing, in any shape" — is true of the twelve shapes and does not generalise
  to the compose files. Any later slice (backup/restore, the boot lane, an
  admin tunnel, a debug profile) can add a service on a new profile with an open
  port, and `validate` stays green while the operator who enables that profile
  gets a datastore port on 0.0.0.0. That is precisely the incident this topology
  exists to prevent, arriving through the one door the checker does not watch.

  This is a coverage hole, not a present defect: no such service exists at this
  head, and I verified the union above by reading every shape.

Perspective:
  operator, instance-admin

Recommendation:
  Close the set rather than enumerate it. Add a rule that collects every
  `profiles:` value appearing in the compose files and fails if any name is not
  covered by at least one shape — "an unrendered profile is an unasserted
  profile", the same argument scripts/compose-shapes.json already makes for the
  shape `floor` ("a shape in the floor may not be removed … an unrendered one is
  an unsupported one"). The `!override`/`!reset` tolerant loader already in
  locate_in_sources() can read the profile names; the rule itself is a set
  difference and needs no render.

Acceptance criteria:
  - Adding a service with `profiles: ["anything-not-in-a-shape"]` to any compose
    file in the chain fails the lane with a named rule, exit 1, whatever that
    service declares.
  - Adding a service to an existing profile still behaves as today (caught by
    the port and lifecycle rules).
  - Adding a genuinely new profile AND a shape that enumerates it is green —
    the rule must push authors toward declaring the shape, not away from adding
    profiles.

Tests:
  docs/evidence/compose-topology/demo.sh, a new case in the existing idiom:
  insert the pgadmin-tunnel block above, assert exit 1 with the new rule id,
  restore, assert exit 0.

Cross-repo implications:
  core: none | user: none | search: none | meta: one rule in
  check-compose-topology.py plus one demo case.

Challenge:
  "Every profile that exists today is enumerated, so this rule would find
  nothing." Correct — and that is the right moment to add it, because it costs
  nothing now and it is the only thing that makes 'in any shape' mean 'in any
  configuration' for the slices that come next. The counter-counterargument is
  that the same hole could be closed by convention (a reviewer checks the shape
  list whenever a profile is added); I do not think a convention is adequate for
  a property whose violation is a published database port.
```

```
FINDING 4: unpinned-image accepts a tag-only reference, so a third-party image can lose its digest pin silently
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-compose-topology.py:336-359 (image_is_pinned), :378-385
             docker-compose.yml:122 (postgres), :149ff (valkey), caddy/clickhouse/kubo
             docs/adr/ADR-001-stack-pins-and-licences.md:28,33,103,104
  requirements: VZ-TOPOLOGY-001, VZ-OPS-008

Observed:
  ADR-001 says PostgreSQL 18 is "managed and digest-pinned" (:28, :103) and
  Valkey 9.1.x "digest-pinned" (:104). The tree honours that today — all five
  third-party images carry `@sha256:<64 hex>`.

  The rule does not require it. `image_is_pinned` accepts `repo:<tag>` for any
  tag that is neither empty nor `latest`. Reproduced: replacing
  `postgres:18@sha256:86c951e0…` with plain `postgres:18` in docker-compose.yml
  leaves the lane green —

      compose topology: 12 shape(s) asserted from their rendered models; 19 rules, 0 violations
      exit=0

  The loosening is deliberate and documented — COMMANDS.md §5 says the rule
  refuses "no image, no tag, or :latest", and the Vizra images legitimately come
  from a mutable release tag (`VIZRA_*_TAG`, rendered `:v0.0.0-ci`). So this is a
  gap between the ADR and the enforcement, not a false claim.

Failure:
  A later edit can drop a digest pin from a third-party image and no check
  notices. `postgres:18` is a moving target: two operators deploying the same
  release record get different PostgreSQL builds, and a rollback to a release
  tag does not roll the datastore image back. ADR-001's reproducibility argument
  quietly stops holding.

Perspective:
  operator, developer

Recommendation:
  Split the rule by image origin: require `@sha256:` for any image whose
  reference does NOT interpolate a `VIZRA_*_TAG` (i.e. the third-party set), and
  keep the current tag rule for the Vizra release images. The manifest already
  distinguishes shapes; this distinction is a substring test on the rendered
  image string.

Acceptance criteria:
  - Replacing any `@sha256:…` on postgres, redis, caddy, clickhouse or ipfs with
    a bare tag fails the lane, exit 1, naming the service.
  - `ghcr.io/yegamble/vizra-core:${VIZRA_CORE_TAG}` still passes.
  - `:latest` and untagged still fail (no regression).

Tests:
  demo.sh cases 8a/8b already cover `:latest` and untagged; add 8c — a
  third-party image demoted from digest to tag — declaring rule=unpinned-image.

Cross-repo implications:
  core: none | user: none | search: none | meta: checker + one demo case.

Challenge:
  "A digest pin has a real cost: security updates require an explicit bump, and
  a stale digest is its own risk." True, and that is exactly why it should be a
  DECISION recorded in ADR-001 rather than a property the checker happens not to
  enforce. If the owner would rather allow tag pins for datastores, the right
  outcome is amending ADR-001, not leaving the two documents disagreeing.
```

```
FINDING 5: .github/required-checks.txt carries a now-false comment ("there is no compose file")
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     .github/required-checks.txt (the comment block, ~line 20)
  requirements: VZ-CI-002

Observed:
  The file says: "Only `validate` exists today: there is no compose file, no
  installer, no bundle and no image to boot, so `bundle` and `boot` have nothing
  to run against."

  At this head there are eight compose files. The file is NOT in this PR's diff:
  `git diff --name-only origin/main...HEAD | grep -c required-checks` → 0.
  The builder's report of this is accurate, and .github/workflows/validate.yml
  states the deviation in its own header ("That stale sentence is REPORTED, not
  silently fixed").

Failure:
  Documentary only. The manifest's one live line, `validate`, is correct and is
  what `ci-required` enforces; I confirmed from the CI log that the guard read
  `required checks: - validate` and that `validate` ran and succeeded on this
  SHA. A reader of the manifest alone would draw a false conclusion about the
  repository's contents, and would not learn that `bundle`/`boot` are still
  absent for a different reason than the one stated.

Perspective:
  developer

Recommendation:
  A separate, owner-reviewed one-line PR updating the comment: `bundle` and
  `boot` remain absent because there is no installer, no bundle builder and no
  published image — the compose files now exist and are gated by `validate`.

Acceptance criteria:
  - The comment states the current reason for each absent lane.
  - The live entry list is unchanged (`validate` only).
  - The PR touches no other file, per the file's own "must not be edited in the
    same PR as the thing it guards" rule.

Tests:
  ./scripts/ci-required-guard.sh (exit 0) — it parses the manifest and ignores
  comments, so the edit is provably behaviour-free.

Cross-repo implications:
  core: none | user: none | search: none | meta: comment only.

Challenge:
  "It is a comment; leave it." The comment is load-bearing in the sense that it
  is the only place the repository explains WHY two named required lanes are
  missing, and a wrong explanation there is how a future author concludes the
  lanes were forgotten rather than deferred.
```

```
FINDING 6: the un-ruled PUBLIC_ORIGIN alias is tolerated silently by the code
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     env/registry/aliases.json (the second entry, `authorised_by: "NOT YET RULED ON…"`);
             scripts/check-config-coverage.py:243-274
  requirements: VZ-TOPOLOGY-007, VZ-OPS-008

Observed:
  Two aliases are declared. The first, `SEARCH_HMAC_KEY` ↔
  `VIZRA_SEARCH_HMAC_KEY`, carries `authorised_by: "war-room chair ruling,
  VZ-ISSUE-002 brief"` — which matches the authorisation the chair states. The
  second, `VIZRA_PUBLIC_ORIGIN` ↔ `vizra-user`'s `PUBLIC_ORIGIN`, carries
  `authorised_by: "NOT YET RULED ON. Found while implementing VZ-ISSUE-002 and
  REPORTED…"`.

  Answering the chair's question directly: **the code tolerates it silently.**
  check-config-coverage.py has no concept of authorisation. It enforces
  `floor == len(aliases)` (rule `alias-floor`) and that each alias is really
  wired (rule `alias-unwired`), and the lane prints only:

      … 12 shapes; 2 declared alias(es); 0 violations

  The "NOT YET RULED ON" text is prose inside a JSON file that no check reads.
  There are exactly two aliases and no more — I read the file and the floor
  enforcement, and a third could not be added without moving `floor` in the same
  diff.

Failure:
  An unauthorised design decision — one operator key feeding two differently
  spelled service keys across two repositories — is now load-bearing in the
  topology and is indistinguishable, in every green run, from the one the chair
  approved. If the chair rules the other way (two keys, or a rename in
  vizra-user), the change is a breaking config change for anyone who deployed
  meanwhile. Nothing in CI surfaces that a ruling is outstanding.

Perspective:
  operator, instance-admin, developer

Recommendation:
  Make "pending a ruling" machine-visible. Give each alias an explicit
  `authorised: true|false`, have check-config-coverage.py PRINT a line naming
  every alias with `authorised: false` (not a violation — the builder was right
  to implement it rather than ship two hand-synchronised keys), and add
  `VIZRA_PUBLIC_ORIGIN` to the chair's open-decisions list alongside the
  ADR-009 tooling deviation.

Acceptance criteria:
  - A green run names every un-ruled alias on stdout.
  - Adding an alias without an `authorised` field is a violation.
  - The floor rule still fires when the count and `floor` disagree.
  - The chair's ruling is recorded in the file's `authorised_by`, and the
    `removed_when` condition is testable.

Tests:
  demo.sh — extend the coverage cases with an alias added without moving the
  floor (rule=alias-floor) and an alias whose service key is absent from the
  snapshot (rule=alias-unwired). Both rules exist and neither has a
  demonstration case today.

Cross-repo implications:
  core: VIZRA_PUBLIC_ORIGIN is core's spelling | user: PUBLIC_ORIGIN is user's
  spelling; one of the two repositories renames once the chair rules |
  search: none | meta: the alias table and the printed line.

Challenge:
  "The alias IS the smaller evil, and the file says so loudly." Agreed — I am
  not asking for it to be removed. I am asking that 'loudly' mean something a
  green CI run shows, because the current arrangement is exactly the failure
  mode aliases.json's own note warns about: "every alias is a place where an
  operator can believe they configured something they did not."
```

```
FINDING 7: the vizra-user registry snapshot names a commit that is not on main
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     env/registry/user.json (`source_commit`);
             docs/evidence/compose-topology/drift-transcript.txt;
             docs/META_REPO.md §2a (the "checked at … vizra-user 7730500" row)
  requirements: VZ-TOPOLOGY-007

Observed:
  `env/registry/user.json` records `source_commit:
  77305009a7ae5b20411134ce5497f88d824e68ce`. That commit is the tip of
  `fix/m0-harness-hardening` — an unmerged branch (PR #7, which the war room
  records as verifier-FAILed) — not of `main`, which is
  `90896beb9669a3b305269a298d507fd7a9e27aa4`. It is the HEAD of the meta
  checkout's nested `vizra-user` working copy, which is what the builder read.

  Content is NOT affected:
      git -C vizra-user diff origin/main 7730500 -- lib/config.ts Dockerfile
  is empty, and my `--drift` run against files materialised from `origin/main`
  reports `config registry drift: every snapshot matches its component source`,
  exit 0. The core and search snapshots DO name their components' `origin/main`
  tips exactly (c043df7, 808a549).

Failure:
  The snapshot's provenance is unreproducible for anyone who does not have that
  branch checked out: `git show 7730500:lib/config.ts` fails against a clone of
  `main`. env/registry/README.md says "`source_commit` is the component commit
  the keys were read from… Update the snapshot and the commit in the same edit,
  or the drift check will say so" — but the drift check compares FILES, not
  commits, so it will never say so. If PR #7 is abandoned or rebased, the
  recorded commit becomes unresolvable.

Perspective:
  developer

Recommendation:
  Re-stamp `source_commit` to `90896beb9669a3b305269a298d507fd7a9e27aa4` (the
  content is identical, so no key edit is needed) and update the §2a row and
  drift-transcript.txt to match. Optionally have `--drift` warn when
  `source_commit` is not an ancestor of the component's `origin/main`.

Acceptance criteria:
  - Every `source_commit` in env/registry/*.json resolves on the component's
    `main`.
  - `--drift` still reports clean.

Tests:
  ./scripts/check-config-coverage.py --drift with the checkouts present, exit 0.

Cross-repo implications:
  core: none | user: none | search: none | meta: one field and two documents.

Challenge:
  "It is a label; the content is right and I proved it." Yes — which is why this
  is a NIT and not a finding about drift. It matters only because this slice's
  whole argument for snapshots is that provenance is recorded precisely.
```

```
FINDING 8: the port allowance is protocol-blind
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-compose-topology.py:215-268 (allow map keyed on
             published port only; `protocol` is parsed at :204-209 and then discarded)
  requirements: VZ-TOPOLOGY-003

Observed:
  `allow[service] = {str(p): public}` is keyed on the published port NUMBER.
  `port_entries` extracts `protocol` and no rule reads it. Reproduced: changing
  api's map to `"127.0.0.1:${VIZRA_HTTP_PORT:-8080}:8080/udp"` leaves the lane
  green (12 shapes, 19 rules, 0 violations) even though nothing in Vizra speaks
  UDP on 8080.

  The impact is bounded: api and frontend are loopback-only, so a stray UDP
  binding there is not reachable off-host, and any non-loopback binding — UDP
  included — is still caught by `public-bind`. The only service with a legitimate
  public UDP port is ipfs/4001, which is declared.

Failure:
  A port allowance reads as "this service may answer on 8080" when it actually
  means "this service may publish the number 8080 on any protocol". No present
  exposure.

Perspective:
  operator

Recommendation:
  Key the allow map on `"<published>/<protocol>"` and write the manifest entries
  as `[{"port": 4001, "protocol": "tcp"}, {"port": 4001, "protocol": "udp"}]`
  for ipfs, `tcp` elsewhere.

Acceptance criteria:
  - api publishing 8080/udp is `port-not-allowed`.
  - ipfs publishing 4001/tcp and 4001/udp remains allowed.

Tests:
  demo.sh, appended to the existing port cases.

Cross-repo implications:
  core: none | user: none | search: none | meta: checker + manifest shape.

Challenge:
  "Loopback makes this unreachable, and public UDP is already caught." Correct —
  hence NIT. I record it because the manifest reads as a protocol-aware
  allowlist and is not one.
```

```
FINDING 9: the shipped local transcripts are stamped at a superseded SHA
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/evidence/compose-topology/local-run.txt (`head: 864f77f5c949c528…`)
  requirements: VZ-CI-002

Observed:
  local-run.txt records `head: 864f77f5c949c52855c430b59338a9b5eb0706b4`. That
  commit was superseded by the squash-and-force-push; it is not reachable from
  the PR head and exists only as a dangling object on GitHub. The verified head
  is 69e197e1.

  The transcript's CONTENT is accurate: I reproduced every line of it from
  69e197e1 (same 191/141 ledger figures, same 94-file link count, same 6/7/10
  fixture floors, same "12 shapes, 19 rules, 0 violations", same
  "34/47/47/12, 2 aliases"). So nothing in it is false except the provenance
  line.

Failure:
  A reader cannot check out the SHA the evidence names. AGENTS.md requires
  evidence to record "source SHA" precisely because a transcript is only as good
  as the tree it names.

Perspective:
  developer

Recommendation:
  Re-run the transcript at the final head and commit it, or add one line saying
  the content was re-verified at 69e197e1 and by whom.

Acceptance criteria:
  - Every SHA named in docs/evidence/compose-topology/*.txt is reachable from
    the PR head.

Tests:
  `git cat-file -e <sha>` in a fresh clone of the branch.

Cross-repo implications:
  core: none | user: none | search: none | meta: one evidence file.

Challenge:
  "I reproduced the content, so the transcript is sound." Yes — that is exactly
  why it is a NIT rather than a finding about the evidence being wrong.
```

---

# Acceptance bullets — VZ-ISSUE-002, verbatim

> **`validate` lane renders default, external-TLS, worker, all-optional, external PG, external Redis, both, bundle-without-checkouts**

**MET.** All eight named shapes render, plus four more (`dev-default`,
`dev-build-from-checkouts`, `prod-external-clickhouse`, `prod-external-ipfs`) —
twelve in total. Reproduced by me two ways: via
`./scripts/compose-render.py --all` (exit 0) **and** independently with plain
`docker compose config --format json` per shape, replicating only the `-f` chain,
`--env-file` and `--profile` list. The CI log for `69e197e1` shows the same
twelve rendered and the models uploaded as `meta-validate-compose-models`.

> **Port-closure, restart-policy, log-cap, one-shot no-build and config-key coverage assertions pass**

**MET.** `check-compose-topology.py` exit 0, `12 shape(s) … 19 rules, 0
violations`; `check-config-coverage.py` exit 0, `34 component keys …, 47 template
keys, 47 interpolated variables, 12 shapes; 2 declared alias(es); 0 violations`.
Each individual property was re-derived by me from my own rendered models
(§2 above), not read off the checker: postgres / cache / search / clickhouse /
migrate / worker publish nothing in any of the twelve; api and frontend are
`127.0.0.1` only; caddy is `edge`-profile-only and the only thing on 80/443;
every long-running service has `restart: unless-stopped` and a json-file cap with
both `max-size` and `max-file`; `migrate` is `restart: "no"`; no `build:` in any
production shape; no `latest`/untagged image in any production shape. Fourteen of
my sixteen adversarial mutations were caught with the correct rule id.
**Caveats, recorded as findings, not as failures of this bullet:** FINDING 2
(one disabled-healthcheck spelling is missed — healthchecks are not named in this
bullet) and FINDING 3 (the port-closure guarantee holds for the twelve enumerated
shapes and does not extend to a service on an unenumerated profile).

> **Invalid external DSN fails render/boot with an actionable message**

**MET** for render, which is the whole of this slice (boot is VZ-ISSUE-004 and
does not exist). Missing, malformed-scheme and host-less DSNs each exit 1 with a
message naming the variable, the expected form and the overlay that requires it,
and none echoes the value — grepped, 0 hits. The "no silent fallback to the
bundled datastore" reasoning is in the message, which is the actionable part an
operator needs.

---

# Verdict

**FAIL.**

Every VZ-ISSUE-002 acceptance bullet is **MET** by my own evidence, `validate`
and `ci-required` are **green on `69e197e1583d9adb90b0130b4a7c28d78b0878a3`**
with a manifest that matches the jobs that actually ran, the scope is clean (no
component repo touched, ledger byte-identical, the ledger-DSL experiment fully
reverted, no real secret in the diff), the history rewrite was within the
builder's contract, and the documentation is unusually honest about what a green
run does and does not prove.

It fails on one blocking defect outside the acceptance bullets:
**FINDING 1** — `scripts/compose-render.py` computes a redacted model, validates
that copy, and then writes the **unredacted** one, stamped
`"secret_values_redacted": true`, into the files that `validate` uploads as a CI
artifact. The redaction and its leak-detector are inert, the stamp is false, and
the command COMMANDS.md tells operators to run writes real credentials to disk
under that label. The fix is two lines plus the demonstration case that was
missing; re-verification should be quick.

Also to fix before merge: **FINDING 2** and **FINDING 3**, both REQUIRED, both
holes I opened in the checker with a mutation the lane called clean.

PASS is not a merge and FAIL is not a rejection of the slice — the chair records
the disposition. No ledger entry reaches VERIFIED on this evidence.

## Reproductions the builder can run

```bash
# FINDING 1
./scripts/compose-render.py --all --out build/compose-models
python3 -c "import json; m=json.load(open('build/compose-models/prod-default.json')); \
  print(m['services']['postgres']['environment']['POSTGRES_PASSWORD']); \
  print(m['x-vizra-shape']['secret_values_redacted'])"
# -> ci-render-only-postgres-password-not-a-real-value
# -> True

# FINDING 2  (restore with: git checkout -- docker-compose.prod.yml)
#   add to docker-compose.prod.yml under `postgres:`  ->  healthcheck: {test: ["NONE"]}
./scripts/compose-render.py --all --out build/compose-models && \
  ./scripts/check-compose-topology.py build/compose-models   # exit 0, 0 violations

# FINDING 3  (restore with: git checkout -- docker-compose.prod.yml)
#   append the pgadmin-tunnel block from the finding to docker-compose.prod.yml
./scripts/compose-render.py --all --out build/compose-models && \
  ./scripts/check-compose-topology.py build/compose-models   # exit 0, 0 violations
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  --env-file env/production.env.example --profile core --profile backup \
  config --format json | python3 -c "import json,sys; \
  print(json.load(sys.stdin)['services']['pgadmin-tunnel']['ports'])"
# -> [{'mode':'ingress','host_ip':'0.0.0.0','target':5432,'published':'5432','protocol':'tcp'}]
```

## Cleanup

The verification clone and all scratch output were created under my scratchpad
directory and are removed by exact path. The three component checkouts under
`/Users/yosefgamble/github/vizra/` were read with `git show origin/main:<path>`
only; nothing was checked out, fetched into a working tree, or modified in them,
and no branch was switched in the chair's checkout. No container was started and
no image was pulled or built.

---

# Re-verification at 3261ad3 (2026-09-21)

Same verifier, same method, **new clean clone** in a private `mktemp -d`
directory — not the builder's worktree, not the shared scratchpad, not the
chair's checkout. Started no container. The only file I write anywhere is this
one.

| | |
|---|---|
| Head SHA verified | `3261ad3edd63684855ff9d2346895a70522b5a8b` |
| Head moved during verification? | No. `gh pr view 4` read `3261ad3e` at the start, and the CI/artifact queries below all name it. |
| Round-1 head | `69e197e1…` (superseded; five commits on top, **plain push**, no rewrite) |
| Base | `main` |
| Environment | macOS arm64, Python 3.9.6, PyYAML 6.0.3, Docker Engine 29.8.0, **Compose v5.5.1** (CI: Engine 28.0.4, Compose v2.38.2 — both above the 2.24.4 floor) |

Commits added since my FAIL, all reachable, none rewritten:

```
a96f188 fix(compose): review round 1 — infrastructure seat + verifier findings
df55226 fix(compose): deliver SEARCH_HMAC_KEY only, against core main 4a80a1e
9eaf8c9 docs(evidence): transcripts for df55226…
bb8163f fix(evidence): assemble the redaction demo's marker at runtime
3261ad3 docs(evidence): transcripts for bb8163f…
```

The transcript commits are separate and each names the code commit it
transcribes — V9 as claimed.

## 1. Lanes, from the clean clone

| Command | Exit | Result |
|---|---|---|
| `./scripts/check-generated-ledger.sh` | 0 | reproduces byte-for-byte (UTF-8 and C/POSIX), 191 requirements, core=141 |
| `./scripts/check-quality-json.py` | 0 | 4 JSON files, 191 ids, 287 references (204 distinct) across 14 documents |
| `./scripts/check-doc-links.py` | 0 | 94 markdown files; **and new**: `compose comments: 6 env//deploy/ path(s) across 8 file(s), all resolve (2 allow-listed as generated-and-absent)` — the F9 fix |
| `./scripts/ci-required-guard.sh` | 0 | floor `validate`; 6 / 7 / 10 fixtures (floors 6 / 7 / 10) |
| `./scripts/check-template-claims.py` | 0 | `10 operator-facing file(s), 9 command reference(s); 5 shipped, 11 declared future; 0 violations` |
| `./scripts/compose-render.py --list` | 0 | **13 shapes** |
| `./scripts/compose-render.py --all --out build/compose-models` | 0 | 13 rendered |
| `./scripts/check-compose-topology.py build/compose-models` | 0 | **`13 shape(s) … 23 rules, 0 violations; 2 known-false probe(s) named above`** |
| `./scripts/check-config-coverage.py build/compose-models` | 0 | **`34 component keys …, 57 template keys, 57 interpolated variables, 13 shapes; 1 declared alias(es); 1 retired key(s) refused; 0 violations`** |
| `./scripts/check-config-coverage.py --drift` (no checkouts) | **2** | BLOCKED, as documented |
| `bash docs/evidence/compose-topology/demo.sh` | 0 | **`RESULT: 61 assertion(s) passed, 0 failed`**, `tree is clean` |

Every claimed count reproduces: **13 shapes, 23 topology rules, 10 coverage
rules, 61 assertions, 1 alias, 1 retired key, 4 lane checkers.**

**Demonstration count.** The script makes **33** `case_header` calls and **33**
cases ran — none skipped. (`grep -c '^case_header'` returns 34 because it also
matches the function *definition*; that is where the “34 cases” figure comes
from. See finding R-4.) Each case prints a sha256 either side of its mutation,
refuses to score a mutation that did not apply, and the run ends on a
whole-tree cleanliness assertion.

**Demonstrations ran on CI** for this SHA — `validate` run `35572579144`, step
`every compose guard still fails against a controlled mutation` = success,
`RESULT: 61 assertion(s) passed, 0 failed` in the log.

## 2. Acceptance bullets, re-derived from my own renderer at this SHA

I re-rendered all 13 shapes with plain `docker compose config --format json`
(my own script, replicating only the `-f` chain, `--env-file` and `--profile`
list) and re-ran my own audit — not the builder's checker. **0 violations
found by me**, now including the new `mem_limit` requirement:

| Shape | Services | Published |
|---|---|---|
| dev-default | api,frontend,migrate,postgres,redis,search,worker | api 127.0.0.1:8080; frontend 127.0.0.1:3000 |
| dev-build-from-checkouts | same (+`build:` on the five component services) | same |
| prod-default | api,caddy,frontend,migrate,postgres,redis,worker | + caddy 0.0.0.0:80/443 |
| prod-external-tls | (no caddy) | api/frontend loopback only |
| prod-worker-split | **worker only** | **NOTHING** |
| **prod-frontend-only** (new) | **frontend only** | frontend 127.0.0.1:3000 |
| prod-all-optional | all ten | + ipfs 0.0.0.0:4001 tcp **and** udp |
| prod-external-postgres | **no postgres** | — |
| prod-external-redis | **no redis** | — |
| prod-external-both | **neither** | — |
| prod-external-clickhouse | **no clickhouse** | — |
| prod-external-ipfs | **no ipfs, no swarm port** | — |
| bundle-no-checkouts | all ten, no `build:` | rendered with the component dirs absent |

- postgres / redis / search / clickhouse / migrate / worker publish **nothing**
  in any of the 13.
- api and frontend bind **127.0.0.1** only; caddy is the only thing on 80/443
  and only under `edge`; ipfs 4001 is the only other public port, declared.
- Every long-running service: `restart: unless-stopped`, json-file with
  `max-size` **and** `max-file`, a real `healthcheck.test`, and in every
  production shape a `mem_limit`. `migrate` is `restart: "no"`, exempt from
  healthcheck and mem_limit as a one-shot.
- No `build:` in any production shape; no `latest`/untagged image.
- `frontend → api` is now `service_started` / `required: false` (F3).

**All three VZ-ISSUE-002 acceptance bullets remain MET**, now across 13 shapes.
Invalid/missing/host-less external DSNs still exit 1 naming the variable and
never echoing the value.

## 3. V1 — the BLOCKER. Fixed, and verified on the bytes.

The fix is structural and correct: `redacted` is the object that is stamped,
leak-checked and serialised (`scripts/compose-render.py:437-455`). My evidence:

- **All 8 declared secret values, all 13 locally written models: 0
  occurrences.** The composite `DATABASE_URL` — assembled from
  `POSTGRES_PASSWORD` in `docker-compose.yml:80` — renders `'<redacted>'`. The
  only injected values that survive are `VIZRA_*_TAG` and `VIZRA_PUBLIC_ORIGIN`,
  which belong in a model.
- **Real-shaped values**, supplied through the two caller-controlled doors
  (`DATABASE_URL`, `VIZRA_CACHE_URL`), including a password containing `@` and
  `#`: 0 occurrences in the written file.
- **The CI artifact for THIS SHA**, downloaded from run `35572579144`
  (`meta-validate-compose-models`, 36 170 B): **14 files, 0 secret-value hits**;
  `prod-default` `api.DATABASE_URL` = `'<redacted>'`, stamp `true` and now true.
- **Case 18b reproduced by me**: deleting `POSTGRES_PASSWORD` from `redact_keys`
  (leaving it in `secret_keys`) makes the renderer exit 1 and write **0 files** —
  `a value this renderer injected survived into the model at
  $.services.postgres.environment.POSTGRES_PASSWORD. Nothing is written.` The
  stamp can no longer be true of an unredacted file, because an unredacted file
  is not written.
- A secret shorter than `MIN_SECRET_LEN` is still redacted **by key**, so the
  length floor only limits substring substitution, not the primary path.

**A correction to my own round-1 finding, which I got partly wrong.**
`compose-render.py:312` is `env.update(man.get("ci_overrides", {}))` — an
unconditional overwrite. A caller therefore **cannot** inject a real value for
`POSTGRES_PASSWORD`, `VIZRA_SESSION_SECRET`, `VIZRA_MFA_KEY_KEK`,
`SEARCH_HMAC_KEY` or `CLICKHOUSE_PASSWORD`; only `DATABASE_URL` and
`VIZRA_CACHE_URL` are caller-controlled (`if var not in os.environ`, line 326),
and the render reads `env/production.env.example`, never an operator's real
`env/production.env`. So my round-1 sentence "a developer or operator running it
has real values in the shell … the result is a plaintext file on disk" was true
for two of the eight keys, not eight. The defect I named — a guard inspecting
something other than the bytes it guards, under a false stamp — was real, and
the fix is right. The blast radius I attached to it was overstated, and I should
have checked line 312 before writing it.

### R-1 — the residual gap (new)

Nothing forces a **new** secret key to be classified. See finding R-1 below: I
added `VIZRA_SMTP_PASSWORD` the fully correct way — `"secret": true` in
`env/registry/core.json`, an entry in `env/production.env.example`, delivered by
the compose files — and it was written raw into all 13 models (47 occurrences)
under `secret_values_redacted: true`, with **render, topology, coverage and
template-claims all exit 0**.

## 4. V2 / V3 / V4 / V6 / V7 / V8 — my own attacks

| Attack | Result |
|---|---|
| `healthcheck: {test: ["NONE"]}` (V2) | ✅ `missing-healthcheck` |
| `healthcheck: {disable: true}` | ✅ `missing-healthcheck` |
| `healthcheck: {test: NONE}` (string form) | Compose renders this as `["CMD-SHELL","NONE"]` — a probe that always goes **red**, i.e. fail-safe, not a disabled probe. The checker's string branch is defensive and unreachable through Compose. Not a hole. |
| service on profile `backup` publishing `0.0.0.0:5432` (V3) | ✅ `profile-not-enumerated`, naming the enumerated set — **my exact round-1 pgadmin-tunnel block** |
| `postgres:18@sha256:…` → `postgres:18` (V4) | ✅ `unpinned-image`, third-party branch |
| api 8080 published over **UDP** (V8) | ✅ `port-not-allowed … (allowed: ['8080/tcp'])` |
| alias flipped to `authorised: false` (V6) | ✅ `alias-floor … is declared with authorised=false, so it is not authorised and must not be wired` |
| second alias added without moving the floor (V6) | ✅ `alias-floor … declares floor=1 but lists 2 alias(es)` |
| `env/registry/user.json` `source_commit` (V7) | ✅ `90896beb…` = `vizra-user` `origin/main` exactly |
| `--drift` against all three components' `origin/main` (materialised read-only with `git show`, then deleted) | ✅ `every snapshot matches its component source`, exit 0; exit **2 BLOCKED** with the checkouts absent |

Carried over from round 1 and re-confirmed green at this SHA: long-syntax ports,
empty `host_ip`, `[::]`, port ranges, env-interpolated ports, `network_mode:
host`, `include:`, `extends:`, caddy via `profiles: []`, per-service log driver,
`restart: "no"`.

## 5. F1 — the retired key. Verified against core `main` myself.

- `env/registry/core.json` `source_commit` = `4a80a1e3f36b8001c2954d0568bea29268e739fe`,
  which **is** `vizra-core` `origin/main` today.
- I parsed `internal/config/keys.go` at that commit and compared **every** key:
  22 registry keys, 22 found, **0 field mismatches** on name, `default` or
  `secret`. The only names in `keys.go` and not in `keys` are the seven
  `VIZRA_DEV_*` hatches, which the registry carries under `escape_hatches`. The
  three defaults the builder says it corrected are correct at this SHA.
- `VIZRA_SEARCH_HMAC_KEY` is in core's `RetiredKeys` at `keys.go:91-99`
  (*"every name production refuses because it was renamed"*), and
  `config.go:214` reads `get("SEARCH_HMAC_KEY")`. So the rename is real and
  delivering the old name would make every core container refuse to boot.
- My own render confirms compose delivers **`SEARCH_HMAC_KEY` only** —
  `VIZRA_SEARCH_HMAC_KEY` absent from api, worker, migrate and search in all 13
  shapes.
- I re-added `VIZRA_SEARCH_HMAC_KEY` to the shared core anchor: **exit 1, 34 ×
  `rule=retired-key-delivered`**, message naming the snapshot commit and the
  boot consequence. The dedicated rule fires, not merely the generic
  `service-key-unknown`.

## 6. F2 — the template-claims checker and its 2-line window

| Attack | Result |
|---|---|
| `vizra setup` **3 lines** from its `VZ-ISSUE-004` marker | ✅ `unmarked-future-command`, with the “a qualifier further down the same comment block launders the claim” reasoning |
| `vizra setup` **1 line** from its marker | allowed — by design; that is the window |
| `vizra setup` inside a compose **`:?` interpolation message**, no marker nearby | ✅ caught at `docker-compose.yml:80`. (My first attempt at this landed two lines from an existing `VZ-ISSUE-004` and correctly passed — operator error on my part, re-run properly.) |
| `vizra setup --rotate` in an env template comment, no marker | ✅ caught |
| an invented `vizra rekey --all` | ✅ `unknown-command`, listing the shipped set |
| the same claim in `docs/OPERATOR-NOTES.md` | **not caught** — see R-4; the scanned set is `env/*.env.example` + `docker-compose*.yml`, which the docstring states |

The checker scans **every line**, not only comments, which is stricter than its
own docstring says (“`docker-compose*.yml` comments”). Erring strict.

## 7. F3 — known-false probes. Works as specified; the specification has a floor.

- `service_healthy` edge onto `api` (declared known-false), injected through the
  **overlay**: ✅ `probe-gates-readiness`, in every shape where both render.
- Changing the api probe to `vizra --help` so the declaration no longer matches:
  ✅ `stale-known-false-probe` for **both** api and worker.
- Both probes are printed **by name, with the reason and the thing that empties
  them**, on every run — pass or fail. I confirmed the same block in the CI log
  for this SHA.
- `frontend → api` is `service_started` / `required: false` in my own render.

**But "real" means "not on the list."** Replacing postgres's real `pg_isready`
probe with `["CMD","true"]` — a probe that can never go red — leaves the three
existing `service_healthy` edges (`api→postgres`, `worker→postgres`,
`migrate→postgres`) pointing at it, and the lane is **green: 23 rules, 0
violations**. `probe_state()` classifies anything that is not absent, not
disabled and not an exact match for a declared entry as `PROBE_REAL`.

Said plainly, because the coordinator asked for it: **the rule guarantees that
no readiness gate points at a probe someone has *admitted* is false. It cannot
tell a real probe from a fake one nobody declared, and it never claims to.**
`docs/META_REPO.md:152-161` and `COMMANDS.md:347` are both accurate on this —
they say "declared known-false" throughout — but neither states the converse.
See R-3.

## 8. F4 — memory caps

| Attack | Result |
|---|---|
| `mem_limit: 0` | ✅ `missing-mem-limit` (Compose renders 0 falsy) |
| `mem_limit: ${PG_MEM:-}` (empty default) | ✅ the **render refuses** — Compose rejects the empty value before any checker runs |
| `mem_limit` deleted, `deploy.resources.limits.memory: 2g` instead | ✅ `missing-mem-limit` — `deploy.resources` is swarm-only and does not satisfy the rule on a non-swarm engine |

Per the coordinator, I did not re-argue the capacity numbers; the seat owns
those.

## 9. The demonstration harness under interruption

`demo.sh` sets `trap cleanup EXIT` (line 45) and restores from a `mktemp -d`
backup, so an ordinary interrupt restores. A `SIGKILL` bypasses the trap, which
is what left the builder's detached run mutated. **The committed tree at this
SHA is clean** (`git status --porcelain` empty in a fresh clone), so nothing
from that incident was committed.

It does **not refuse** a dirty start: it prints `dirty: N file(s)` in its header
and continues. I measured what happens rather than inferring it — starting the
run with one stray comment appended to `docker-compose.prod.yml` gave:

```
dirty: 1 file(s)
...
RESULT: 57 assertion(s) passed, 5 failed
  tree is clean - every mutation was reverted
exit=1
```

So a dirty start is **fail-closed and loud**: five case assertions went red and
the run exited 1. (My first reading of the code predicted it would fail only on
the closing whole-tree assertion; that prediction was wrong — the perturbation
shows up in the per-case digests first, and the closing check actually passed
because the backup/restore machinery put the stray line back. Recording the
measurement, not the prediction.)

Adequate as it stands. A refusal at the top would be clearer than five confusing
red cases, and would let the run distinguish "a guard stopped working" from "the
tree was dirty when you started" — which the script's own closing message says
it cannot do. R-4 material at most.

## 10. GitGuardian and the history question

- **The head tree contains no credential-shaped literal.** I swept for
  `(password|secret|token|hmac|api_key)\s*=\s*['"]…['"]` across `*.sh`, `*.py`,
  `*.yml`, `*.json`, `*.example`: **no hits**. I swept for
  `scheme://user:pass@host`: the only hits are in
  `docs/evidence/warroom/2026-09-20-vizra-core-pr1-foundation-SECURITY.md`,
  which is **pre-existing on `main`, not in this PR's diff**, and which labels
  each one SYNTHETIC.
- **Nothing real was ever committed on this branch.** I read the incident commit
  `a96f188` myself. The literals were `zzMARKERzzPOSTGRESzz`,
  `zzMARKERzzSESSIONzz`, `zzMARKERzzKEKzz`, `zzMARKERzzHMACzz`,
  `zzMARKERzzCLICKHOUSEzz` and a `db.ci.invalid` DSN carrying
  `zzMARKERzzDSNzz`. Every one is a synthetic marker; `.invalid` is RFC 2606.
  Nothing needs rotating. `bb8163f` assembles the marker at runtime
  (`MARKER="zz$(printf 'MARK')ERzz"`) so no committed line is a
  credential-shaped assignment, with a comment telling the next author not to
  "simplify" it back.
- **I agree with leaving history alone.** A second rewrite would buy nothing:
  the strings are provably fake, a force-push does not remove a blob from
  GitHub's object store anyway (I demonstrated that in round 1 — `864f77f5` is
  still served by the API), and a squash-merge keeps `a96f188` off `main`. The
  cost of a rewrite — orphaning the CI results and the transcript commits that
  name them — is real and the benefit is zero. Dismissing the incident is the
  owner's call, not mine or the chair's.

## 11. CI on `3261ad3e`

| Check run | Status | Conclusion | In the manifest? |
|---|---|---|---|
| `validate` | completed | **success** | **yes** — the manifest's only entry |
| `ci-required` | completed | **success** | (the aggregate itself) |
| `GitGuardian Security Checks` | completed | failure | **no** |

`.github/required-checks.txt` at this SHA contains exactly one live line,
`validate`, and **is not touched by this PR** (`git diff --name-only
origin/main...HEAD | grep -c required-checks` → 0). GitGuardian is not a required
check and does not gate the merge — confirmed by reading the manifest at this
SHA, not by taking the claim.

All **18** `validate` steps succeeded, none skipped, including the new
`no template claims a command that does not exist` step. From the log:

```
Docker version 28.0.4 / Docker Compose version v2.38.2
KNOWN-FALSE PROBES: 2 service(s) …
compose topology: 13 shape(s) … 23 rules, 0 violations; 2 known-false probe(s) named above
ALIASES: 1 operator key(s) feeding two service spellings
config coverage: 34 component keys …, 57 template keys, 57 interpolated variables, 13 shapes; 1 declared alias(es); 1 retired key(s) refused; 0 violations
template claims: 10 operator-facing file(s), 9 command reference(s); … 0 violations
RESULT: 61 assertion(s) passed, 0 failed
```

The `pull_request` caveat from round 1 still applies: the lane tests
`refs/pull/4/merge`, so a green on this head means the merge into `main` **as it
stood at 07:21 UTC**. Re-run if `main` moves before the merge.

## 12. Scope

| Check | Result |
|---|---|
| Component repositories modified? | **No** — 0 paths under `vizra-core/`, `vizra-user/`, `vizra-search/` in the whole PR diff |
| `docs/quality/features.json` | **byte-identical to `main`** (empty diff) |
| `docs/evidence/ledger-generator/` | **untouched**; `build.py:20` gate intact verbatim |
| `.github/required-checks.txt` | **untouched** |
| Secrets in the diff | none real; markers are runtime-assembled |

## 13. Truthfulness — sentences that promise more than their control

Accurate, and I checked each: `META_REPO.md` §2a on known-false probes and on
"the port is closed means the model publishes nothing"; `COMMANDS.md` §4 on the
two redaction lists (it correctly says `secret_keys` is *"a separate list,
identical in content today"* and openly records the defect it replaced);
`COMMANDS.md` §5 "What this does NOT prove"; `env/registry/README.md` on
snapshots; the corrected MFA/KEK template sentences (no command is promised —
`docker-compose.yml:91` now says *"do NOT change it after first boot … nothing
re-seals them"*, which is true).

Not accurate — see R-2 and R-4:

- `scripts/compose-render.py` docstring, bullet 3: *"Every value this renderer
  INJECTED — `redact_keys`, `ci_overrides` and `external_dsn_overrides`
  together — drives the LEAK CHECK … **The wider set is the point**"*. The code
  reads `secret_keys`, which is **identical** to `redact_keys`; the inline
  comment twelve lines below even says *"Deliberately NOT everything this
  renderer injects"*. The file contradicts itself and the docstring is the
  wrong half.
- `docs/quality/COMMANDS.md:282` "the **twelve** shapes" → 13.
- `docs/quality/COMMANDS.md:327` "**Nineteen** rules" → 23.
- `docs/quality/COMMANDS.md:492` "61 assertions across **34** cases" → 33.
- `docs/quality/COMMANDS.md:342` the `unpinned-image` table row still reads "no
  image, no tag, or `:latest`", omitting the digest requirement that the
  paragraph two below it correctly describes.
- `docs/META_REPO.md:84` "**Twelve** shapes are rendered on every run" → 13.
- **The PR body is stale** — see R-5.

---

# Findings — round 2

```
FINDING R-1: nothing forces a new secret key into redact_keys/secret_keys
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/compose-render.py:412-433 (secret_keys read from the manifest only);
             scripts/compose-shapes.json (`redact_keys`, `secret_keys`);
             env/registry/core.json (already carries a per-key `"secret": true` flag)
  requirements: VZ-OPS-008, VZ-CI-002

Observed:
  The leak check looks only for values of keys listed in the manifest's
  `secret_keys`. A key that is not in that list is neither redacted nor checked.

  Reproduced at this SHA by adding a new secret key the FULLY CORRECT way —
  declared to the component, documented for the operator, delivered by compose:

    1. docker-compose.yml, on the shared core anchor:
         VIZRA_SMTP_PASSWORD: ${VIZRA_SMTP_PASSWORD:-}
    2. env/registry/core.json  keys += {"name":"VIZRA_SMTP_PASSWORD","secret":true,…}
    3. env/production.env.example += VIZRA_SMTP_PASSWORD=

    $ env VIZRA_SMTP_PASSWORD='zzREALSMTPSECRETzz9f2a7c4e' \
        ./scripts/compose-render.py --all --out build/compose-models   # exit 0
    $ ./scripts/check-compose-topology.py  build/compose-models        # exit 0
    $ ./scripts/check-config-coverage.py   build/compose-models        # exit 0
    $ ./scripts/check-template-claims.py                               # exit 0
    $ grep -rc 'zzREALSMTPSECRETzz9f2a7c4e' build/compose-models/*.json | ...
      47
    api.VIZRA_SMTP_PASSWORD -> 'zzREALSMTPSECRETzz9f2a7c4e'
    stamp secret_values_redacted -> True

  Every one of the four lane checkers is green and the value is in every model
  under a stamp saying it is not.

  Note what does NOT save it: the coverage checker refuses an UNREGISTERED key
  (I confirmed: `service-key-unknown` + `variable-untemplated`, 35 violations),
  so an author cannot land a new key carelessly. They can land one carefully and
  still miss the classification, because no check connects the registry's own
  `"secret": true` flag to `redact_keys`.

Failure:
  The V1 control is now correct for every secret it knows about and has no way
  to learn about a new one. The next slice that adds an SMTP password, an S3
  secret key, an OAuth client secret or a captcha secret — all of them are on
  the M1-M3 ledger — reintroduces exactly the condition I raised in round 1: a
  model file stamped `secret_values_redacted: true` that is not redacted. In CI
  the value would be the template's blank, so the artifact stays clean; the
  exposure is a developer or operator running the documented command with the
  value exported, and the file's own stamp is what makes it look safe to attach
  to an issue.

Perspective:
  operator, developer

Recommendation:
  Derive the set instead of hand-maintaining it. `env/registry/*.json` already
  marks each key `"secret": true`; have the renderer union those names into
  `secret_keys`, and have `check-config-coverage.py` fail when a registry key
  marked secret, or a template key whose name ends in `_PASSWORD`/`_SECRET`/
  `_KEY`/`_TOKEN`/`_DSN`/`_URL`-with-credentials, is absent from `redact_keys`.
  A new rule id (`unclassified-secret-key`) keeps the failure legible.

Acceptance criteria:
  - Adding a key marked `"secret": true` to any component registry without
    adding it to `redact_keys` fails a lane, exit 1, naming the key.
  - Rendering with that key set to a recognisable value writes no model
    containing it (or refuses to write at all).
  - The existing eight keys still pass unchanged.
  - Removing a key from `redact_keys` still makes the renderer write nothing
    (case 18b must not regress).

Tests:
  docs/evidence/compose-topology/demo.sh, a new case beside 18a/18b: register a
  secret key without classifying it, assert the lane goes red with the new rule
  id, restore, assert green. Same idiom, no new dependency.

Cross-repo implications:
  core: none — the `secret` flag it already publishes becomes load-bearing here |
  user: none | search: none | meta: renderer + coverage checker + one demo case.

Challenge:
  "The eight secrets that exist are all classified, and I proved zero leaks."
  True — this is a durability finding, not a present defect, and it is the same
  shape as the profile hole the builder just closed. The counterargument I take
  seriously is that a name-pattern heuristic will misfire on something like
  `VIZRA_SESSION_SECRET_ROTATION_DAYS`; that is why the registry's explicit
  `"secret": true` should be the primary signal and the pattern only a
  secondary net.
```

```
FINDING R-2: the renderer's docstring describes a wider leak-check set than the code uses
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/compose-render.py:36-41 (docstring) vs :412-424 (code and its
             own inline comment)
  requirements: VZ-CI-002

Observed:
  Docstring:

    * Every value this renderer INJECTED — `redact_keys`, `ci_overrides` and
      `external_dsn_overrides` together — drives the LEAK CHECK … The wider set
      is the point

  Code:

      secret_keys = set(man.get("secret_keys") or [])

  and its own inline comment: "A SEPARATE list from `redact_keys`, and identical
  to it today … Deliberately NOT everything this renderer injects:
  `VIZRA_CORE_TAG` and `VIZRA_PUBLIC_ORIGIN` are injected too and belong in a
  rendered model."

  Measured: `secret_keys == redact_keys` is True; the injected keys NOT in
  `secret_keys` are `VIZRA_CORE_TAG`, `VIZRA_USER_TAG`, `VIZRA_SEARCH_TAG`,
  `VIZRA_PUBLIC_ORIGIN`. There is no wider set.

  `docs/quality/COMMANDS.md` §4 gets this right, so the error is isolated to the
  module docstring — the first thing a maintainer reads.

Failure:
  The mechanism the docstring credits for catching a de-classified key is not
  the mechanism that catches it. What actually works is that the two lists are
  read independently, which I verified (case 18b, reproduced). A maintainer who
  believed the docstring would think every injected value is watched — the exact
  belief that produces R-1.

Perspective:
  developer

Recommendation:
  Replace that sub-bullet with what COMMANDS.md §4 already says: a separate
  list, identical in content today, and the INDEPENDENCE is the mechanism, not
  the width.

Acceptance criteria:
  - No sentence in the file claims a set the code does not build.
  - The docstring and COMMANDS.md §4 say the same thing.

Tests:
  None mechanical. Adjacent to R-1's checker, which would make the claim true if
  the set is genuinely widened instead.

Cross-repo implications:
  core: none | user: none | search: none | meta: one docstring bullet.

Challenge:
  "It is a comment." It is a comment in the file whose last defect was a control
  that did not do what its comment said — and this PR's own COMMANDS.md says
  recorded figures in this repository are meant to be trustable.
```

```
FINDING R-3: probe-gates-readiness cannot see a false probe nobody declared
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-compose-topology.py probe_state() and check_probes();
             docs/META_REPO.md:152-161; docs/quality/COMMANDS.md:347
  requirements: VZ-TOPOLOGY-002, VZ-OPS-008

Observed:
  `probe_state()` returns PROBE_REAL for any healthcheck that is present, not
  disabled, and not an exact match for a `known_false_probes` entry. The gate
  rule fires only when `dep in known_false`.

  Reproduced: replace postgres's real probe in the production overlay with one
  that can never go red —

      postgres:
        healthcheck: !override
          test: ["CMD", "true"]
          interval: 10s

  The three real readiness edges onto postgres (`api`, `worker` and `migrate`
  all gate on it with `condition: service_healthy`) now gate on nothing, and:

      compose topology: 13 shape(s) … 23 rules, 0 violations; 2 known-false probe(s)

  For contrast, both declared cases ARE caught: a `service_healthy` edge onto
  `api` injected through an overlay gives `probe-gates-readiness` in every shape,
  and changing the api probe to `vizra --help` gives `stale-known-false-probe`
  for api and worker.

Failure:
  The rule's guarantee is narrower than a reader is likely to take from
  "a gate that cannot go red is worse than no gate". It guarantees no gate
  points at an ADMITTED placeholder. A placeholder nobody admitted — including
  the two most natural ones, `["CMD","true"]` and `["CMD-SHELL","exit 0"]` —
  reads as real. Since META_REPO.md says the known-false list "must be empty
  before VZ-ISSUE-004's boot lane lands", the pressure at that moment is to
  empty the list, and emptying it by weakening a probe rather than by shipping
  `vizra healthcheck` would be invisible here.

Perspective:
  operator

Recommendation:
  Two small things, in order of value:
  1. Say it plainly in META_REPO.md §2a and the COMMANDS.md rule row: *a probe
     not on the known-false list is treated as real; this rule cannot detect an
     undeclared placeholder.*
  2. Refuse the handful of probes that are placeholders by construction —
     `["CMD","true"]`, `["CMD-SHELL","exit 0"]`, `["CMD-SHELL",":"]`, and a
     `test` whose only argument is `--help`/`version` on a binary that is a
     `depends_on: service_healthy` target. A denylist is not a classifier, and
     should be described as what it is.

Acceptance criteria:
  - The documentation states the converse explicitly.
  - `test: ["CMD","true"]` on any service that is the target of a
    `service_healthy` edge fails the lane with a named rule.
  - The two declared known-false probes still produce their standing named
    output, and `vizra version` on api/worker is not newly refused (it is
    already declared).

Tests:
  demo.sh beside case 15: an undeclared always-green probe on a
  `service_healthy` target, red for the new rule id, restored, green.

Cross-repo implications:
  core: `vizra healthcheck` (already queued, 2h) is what removes the need |
  user: none | search: none | meta: checker + two doc sentences.

Challenge:
  "You cannot decide from a rendered model whether a probe is honest, so the
  declared list is the only sound mechanism." I agree — that is exactly why
  recommendation 1 matters more than recommendation 2, and why I filed this as
  SHOULD rather than REQUIRED. What I am refusing is the silence, not the
  design.
```

```
FINDING R-4: stale figures in the two documents whose purpose is trustable figures
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/quality/COMMANDS.md:282, :327, :342, :492; docs/META_REPO.md:84
  requirements: VZ-CI-002

Observed:
  Measured against the tree at this SHA (13 shapes from `--list`, 23 ids in
  check-compose-topology.py's RULES, 10 in check-config-coverage.py's, 33
  `case_header` CALLS of which 33 ran):

  | Says | Is |
  |---|---|
  | COMMANDS.md:282 "the twelve shapes" | 13 |
  | COMMANDS.md:327 "Nineteen rules" | 23 |
  | COMMANDS.md:492 "61 assertions across 34 cases" | 61 across **33** |
  | META_REPO.md:84 "Twelve shapes are rendered on every run" | 13 |
  | COMMANDS.md:342 `unpinned-image` row: "no image, no tag, or `:latest`" | also refuses a third-party image with no digest |

  The "34" is almost certainly `grep -c '^case_header'`, which counts the
  function DEFINITION as well as its 33 calls — I made the same mistake before
  checking. COMMANDS.md:314's "ten of twelve models" is a correct HISTORICAL
  statement about the 69e197e artifact and matches what I measured; leave it.

  Also: `demo.sh` uses the fixed shared paths /tmp/vizra-redaction-demo and
  /tmp/vizra-redaction-demo2. Exact paths, never a glob, so the `rm -rf` is
  safe — but two concurrent runs (two worktrees on one machine) would collide.

Failure:
  Documentary. COMMANDS.md argues in its own voice that "a number that goes
  stale on its own is worse than no number in a file whose purpose is that
  recorded figures can be trusted" — and then carries four.

Perspective:
  developer

Recommendation:
  Correct the five; reuse the existing convention of not quoting a number that
  will drift where the exact value is not load-bearing. For demo.sh, use
  `mktemp -d` as the script already does for its backup directory.

Acceptance criteria:
  - Every count in COMMANDS.md and META_REPO.md §2a matches the tree.
  - The `unpinned-image` row mentions both branches.
  - demo.sh uses no fixed shared /tmp path.

Tests:
  None mechanical. A `check-recorded-counts.py` would be over-engineering for
  five numbers; the honest alternative is not writing counts that drift.

Cross-repo implications:
  core: none | user: none | search: none | meta: docs + one demo line.

Challenge:
  "Five numbers, after a round that fixed thirteen real findings." Agreed —
  NIT, and I have capped myself. I record them because they are the kind of
  drift this repository has already decided it cares about.
```

```
FINDING R-5: the PR body still describes the round-0 tree
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     yegamble/vizra#4 pull-request body
  requirements: VZ-CI-002

Observed:
  Read from `gh pr view 4 --json body` at this SHA. It still says:

  - "**Twelve shapes rendered on every run**" (13)
  - "`./scripts/check-compose-topology.py` | 0 | 12 shapes, 19 rules" (13, 23)
  - "34 component keys, 47 template keys, 47 interpolated variables, **2
    aliases**" (57, 57, **1**)
  - "### Red/green — **32 assertions**" (61)
  - "Head **`69e197e1…`** — `validate` ✅, `ci-required` ✅, **GitGuardian ✅**"
    (head is `3261ad3e`; GitGuardian is **red** on this PR)
  - Open item 3: "`VIZRA_PUBLIC_ORIGIN` / `PUBLIC_ORIGIN` … **has not been ruled
    on** … with a floor of **2**" — the chair ruled on it on 2026-09-21 and the
    floor is now 1, which is exactly what `env/registry/aliases.json` records.

Failure:
  The PR body is the first artifact a reviewer, the chair, or the owner reads,
  and it is the one place in this PR that still asserts a green GitGuardian and
  an unresolved alias question. A merge decision made from it would be made on
  superseded facts — including the one fact (GitGuardian) the owner has to act
  on personally.

Perspective:
  developer, instance-admin

Recommendation:
  Update the body in the same round as the next push: the counts, the head SHA,
  the GitGuardian status with the reason it is red and that it is not in the
  required-check manifest, and the alias item to record the ruling.

Acceptance criteria:
  - Every figure in the body matches the head it names.
  - The body names the current head SHA.
  - The GitGuardian line says red, why, and that it does not gate.
  - The alias item records the chair's ruling rather than asking for one.

Tests:
  None mechanical.

Cross-repo implications:
  core: none | user: none | search: none | meta: PR body only.

Challenge:
  "The evidence files are the record; the PR body is a narrative." AGENTS.md
  makes the opposite call — "report what passed, what did not run, and the
  remaining gate" — and a stale "GitGuardian ✅" is the single sentence most
  likely to stop someone looking at a red check.
```

---

# Round-1 findings — disposition

| Round-1 finding | Severity | Status at `3261ad3e` | How I verified |
|---|---|---|---|
| **1** renderer writes unredacted models under a true stamp | BLOCKER | **CLOSED** | redacted copy is stamped and serialised; 0 secret values in 13 local models **and** in the CI artifact for this SHA; case 18b reproduced (writes 0 files). Residual gap filed as **R-1**; my round-1 blast-radius claim corrected above. |
| **2** `test: ["NONE"]` defeats `missing-healthcheck` | REQUIRED | **CLOSED** | four explicit probe states; my own mutation now red. String form is unreachable via Compose and fail-safe. |
| **3** service on an unenumerated profile never asserted | REQUIRED | **CLOSED** | `profile-not-enumerated` catches my exact pgadmin-tunnel block and names the enumerated set. |
| **4** tag-only pin accepted for third-party images | SHOULD | **CLOSED** | origin split; `postgres:18` now red. |
| **5** `.github/required-checks.txt` stale comment | SHOULD | **OPEN, correctly** | still not edited — the manifest rule forbids it in this PR. Owner-reviewed follow-up. |
| **6** un-ruled alias tolerated silently | SHOULD | **CLOSED** | `authorised`/`authorised_by`/`removed_when`, printed every run; `authorised: false` and a floor mismatch are both violations; the chair ruled and floor is 1. |
| **7** `user.json` stamped off `main` | NIT | **CLOSED** | `90896beb…` = vizra-user `origin/main`. |
| **8** protocol-blind port allowance | NIT | **CLOSED** | keyed `<published>/<protocol>`; UDP on an allowed TCP port red. |
| **9** transcripts stamped at a superseded SHA | NIT | **CLOSED** | transcripts are separate evidence-only commits naming the code commit they transcribe. |

All four `vizra-infrastructure` chair blockers (F1 retired key, F2 template
claim, F3 probe gate, F4 memory caps) reproduce as fixed by my own mutations,
with the limit on F3 recorded as R-3.

## Cleanup

Clone and all scratch output were created under a private `mktemp -d`
directory and are deleted by exact path. The three component checkouts were read
with `git -C … show origin/main:<path>` only — nothing checked out, fetched into
a working tree, or modified; no branch switched in the chair's checkout. No
container started, no image pulled or built. The only file written outside my
scratch directory is this one.

FINAL VERDICT: PASS — SHA 3261ad3edd63684855ff9d2346895a70522b5a8b

---

# Re-verification at 9c4b5d3 (2026-09-21)

Same verifier. Two fresh clones under my own `mktemp -d` inside the shared
scratch root — one for the demonstration run, one for mutations, because in this
round I first made the mistake of mutating the tree a background demo run was
using and had to discard that result. Started no container. Wrote only this file.

| | |
|---|---|
| Head SHA verified | `9c4b5d3285e1368634bc2042a83a91bfcb7e564b` |
| Head moved? | No — `gh pr view 4` read `9c4b5d3e` at the start and the CI/artifact queries all name it. |
| Previous head | `3261ad3e` (my PASS). Two commits on top, **plain push**, nothing rewritten. |
| Environment | macOS arm64, Python 3.9.6, PyYAML 6.0.3, Docker Engine 29.8.0, Compose **v5.5.1** (CI: Engine 28.0.4, Compose v2.38.2) |

```
7e95989 fix(compose): review round 2 — untrue statements, /dev/shm, and a derived secret set
9c4b5d3 docs(evidence): transcripts for 7e959893…
```

## Verdict summary

Every acceptance bullet is still MET from my own renderer, CI is green, the
scope is clean, and the artifact carries no secret. **R-1 is genuinely fixed in
substance.** The verdict is FAIL on two findings of one kind: a guarantee
asserted in the PR body and in three documents that the control does not
deliver. That is the exact condition the chair has held this PR for twice, and
the coordinator asked me to list any sentence that still is stronger than its
control. Neither touches the topology; both are a few words and, for one, a
three-line code change.

## 1. Lanes

| Command | Exit | Result |
|---|---|---|
| `check-generated-ledger.sh` | 0 | reproduces byte-for-byte, 191 requirements |
| `check-quality-json.py` | 0 | 191 ids, 287 references, all resolve |
| `check-doc-links.py` | 0 | + new: `compose comments: 6 env//deploy/ path(s) across 8 file(s), all resolve` |
| `ci-required-guard.sh` | 0 | floor `validate`; 6 / 7 / 10 fixtures |
| `check-template-claims.py` | 0 | `10 files, 16 command references; 5 shipped, 11 future, 0 scripts present and 6 declared future; 0 violations` |
| `compose-render.py --all` | 0 | **13 shapes** |
| `check-compose-topology.py` | 0 | **`13 shape(s) … 26 rules, 0 violations; 2 known-false probe(s)`** |
| `check-config-coverage.py` | 0 | **`34 component keys …, 58 template keys, 58 interpolated variables, 13 shapes; 1 alias; 1 retired key refused; 0 violations`** |
| `check-config-coverage.py --drift` (absent) | 2 | BLOCKED, as documented |
| `demo.sh` (clean clone, nothing else touching it) | **1** | **72 of 73 assertions passed, 1 failed** — see **S-4**; CI reported 73/73 |

Counted from source: **26** topology rule ids, **11** coverage rule ids, **4**
template-claims rule ids — all three claims reproduce. `case_header` is called
**39** times and 39 cases printed; the "40 cases" figure counts the function
definition (see S-7).

## 2. Acceptance bullets — re-derived from my own renderer

I re-rendered all 13 shapes with plain `docker compose config --format json` and
ran my own audit. **0 violations found by me**, covering ports, restart, log cap,
healthcheck state (including the `["NONE"]` spelling), production build, image
pinning and `mem_limit`:

```
bundle-no-checkouts        10 svc | api 127.0.0.1:8080; caddy 0.0.0.0:80,443; frontend 127.0.0.1:3000; ipfs 0.0.0.0:4001 tcp+udp
dev-build-from-checkouts    7 svc | api 127.0.0.1:8080; frontend 127.0.0.1:3000
dev-default                 7 svc | api 127.0.0.1:8080; frontend 127.0.0.1:3000
prod-all-optional          10 svc | + ipfs 0.0.0.0:4001 tcp+udp
prod-default                7 svc | api/frontend loopback; caddy 80/443
prod-external-both          5 svc | no postgres, no redis
prod-external-clickhouse    7 svc | no clickhouse
prod-external-ipfs          7 svc | no ipfs, no swarm port
prod-external-postgres      6 svc | no postgres
prod-external-redis         6 svc | no redis
prod-external-tls           6 svc | no caddy
prod-frontend-only          1 svc | frontend 127.0.0.1:3000
prod-worker-split           1 svc | PUBLISHES NOTHING
shapes audited: 13 | MY OWN violations: 0
```

postgres, the cache, search, clickhouse, migrate and worker publish **nothing**
in any of the 13. The external overlays really delete the container. The
worker-split shape really renders worker alone and publishes nothing. **All
three VZ-ISSUE-002 acceptance bullets remain MET.**

## 3. R-1 — fixed in substance

The derivation is real: `registry_secret_names()` unions every
`"secret": true` key from all three component registries into **both** the
redaction set and the leak-check set, on top of the two manifest lists.

| Attack | Result |
|---|---|
| **my exact round-2 mutation** (`"secret": true` in core.json + template entry + compose delivery) | **47 occurrences → 0**; `api.VIZRA_SMTP_PASSWORD` = `'<redacted>'`; the key appears in the model's `redacted_keys` and `leak_checked_keys` |
| the same secret ALSO delivered under a second, non-secret key (`VIZRA_MAILER_AUTH: ${VIZRA_SMTP_PASSWORD}`) | **0 occurrences** — the substring pass covers the alias |
| the secret in `labels:` / `command:` rather than `environment:` | **0 occurrences** |
| **case 18b must not regress**: delete `POSTGRES_PASSWORD` from `redact_keys` | render **exit 1**, `a value this renderer injected survived into the model at $.services.postgres.environment.POSTGRES_PASSWORD`, **0 files written** |
| a suffix-matching name with **no** registry flag (`VIZRA_SMTP_PASSWORD`) | value written, but **the lane goes red**: `unclassified-secret-key … is named like a secret (_PASSWORD) but is neither flagged secret in a registry nor listed in redact_keys` |
| a credential whose name matches **none** of `_PASSWORD/_SECRET/_TOKEN/_KEY` and which no registry flags (`VIZRA_S3_ACCESS_ID`) | **47 occurrences, every lane exit 0** — see **S-6** |

**The CI artifact for this SHA is clean.** Downloaded from run `35576458546`
(`meta-validate-compose-models`, 37 204 B): **14 files, 0 hits** for any of the
eight secret values; `prod-default` `api.DATABASE_URL` = `'<redacted>'`; the
stamp is `true` and each model now records `redacted_keys: 8` and
`leak_checked_keys: 8`, so a reader can see what was protected instead of
trusting the boolean.

`ci_overrides` is still applied with `env.update()` after the process
environment, and the docstring now states that property and says "Keep it" —
which matches the code and matches my round-2 correction.

## 4. R-3 — implemented, and weaker than its own description

`gated-probe-unrecognised` exists and the declared case works. Its
implementation is `rule["must_invoke"] not in joined`, where `joined` is the
rendered `healthcheck.test` list joined with spaces — a **substring test over
the command line**, not a check that the command runs or that its status gates.

| Probe substituted on `postgres` (three `service_healthy` edges point at it) | Lane |
|---|---|
| `["CMD", "true"]` | **red** — `gated-probe-unrecognised`, the declared case |
| `["NONE"]` | **red** — twice (`missing-healthcheck` + `gated-probe-unrecognised`) |
| `["CMD-SHELL", "pg_isready -U vizra \|\| true"]` | **green** |
| `["CMD-SHELL", "true # pg_isready"]` | **green** |
| `["CMD", "sh", "-c", "exit 0; pg_isready"]` | **green** |
| `["CMD", "echo", "pg_isready"]` | **green** |

All four green rows are probes that **always exit 0**, so all three readiness
gates onto PostgreSQL become gates onto nothing, with `26 rules, 0 violations`.

**What the rule now guarantees, plainly:** every `service_healthy` target must
be listed in `gated_probes`, and its rendered probe command line must *contain
the declared command's name somewhere*. **What it does not guarantee:** that the
command is executed, that its exit status decides the probe, or that the probe
can go red. It raises the cost of killing a gate from deleting a word to writing
a line that still mentions `pg_isready` — real, and one line.

**The docs do not say that.** `docs/META_REPO.md:162` — "must be listed in
`gated_probes` and still **invoke** the command"; `docs/quality/COMMANDS.md:348`
— "whose probe no longer **invokes** the declared command". "Invoke" is a claim
about execution; the control tests for a mention. See **S-2**.

## 5. Infrastructure F2 / F3 / F4 / NEW-1

### F4 and NEW-1 — solid

`VIZRA_WORKER_CONCURRENCY=2` with a corrected comment block (1 / 2 / 4 by host
size); `VIZRA_CADDY_MEM_LIMIT=160m`; COMMANDS.md §5a states the 4092 MiB sum on
a 4096 MiB host and the three added caveats. `mem_limit` is on every
long-running production service in all 13 shapes (my own audit).

`postgres-shm-floor` survives every defeat I tried:

| Mutation | Result |
|---|---|
| `shm_size: 0` | red (`shm_size=None`) |
| `shm_size: 64m` (exactly Docker's default) | red |
| `shm_size: 65m` | green — the boundary is where it says it is |
| `shm_size: ${PG_SHM:-}` (empty default) | **render refuses** |
| `shm_size: 256` (bytes, not `m`) | red |

Compose normalises the value to a byte count (`'268435456'` rendered from
`256m`), so the units-versus-bytes question the coordinator raised is settled by
Compose before the rule sees it.

### F3 — the disclosure is one-directional

| Mutation | Result |
|---|---|
| delete the `IGNORE THE \`healthy\` COLUMN` marker from `env/production.env.example` | **red** — `known-false-undisclosed` |
| delete it from `README.md` | **red** |
| **empty `known_false_probes` while both paragraphs remain** | **green, exit 0** |
| marker present, the `curl` commands stripped out | green (the rule matches the marker string only) |

`scripts/check-compose-topology.py:876` is `if known_false and disclosure:` —
the whole block is skipped when the list is empty. See **S-1**.

### F2 — the script pass, and where it does not reach

`env/registry/meta.json` is well built: six future scripts, each mapped to
`VZ-ISSUE-004`, with an explicit empty `scripts` list. The three `backup.sh`
sentences are genuinely future tense with the marker adjacent — I read all three
(`env/production.env.example:144,158`, `docker-compose.external-postgres.yml:51`):
"backup.sh, which **will** refuse such a database out loud, **arrives with**
VZ-ISSUE-004". That is the fix, done properly.

| Spelling in an operator-facing file, no marker | Caught? |
|---|---|
| `backup.sh` (bare) | ✅ `unmarked-future-script` |
| `bash backup.sh` | ✅ |
| `bootstrap.sh` inside a compose `:?` message | ✅ |
| **`./backup.sh`** | ❌ |
| **`scripts/backup.sh`** | ❌ |
| **`` `./backup.sh` `` (backticked)** | ❌ |
| an invented `rotate-secrets.sh` | ❌ |

The regex is `(?<![\w./-])((?:backup|restore|install|bootstrap|deploy|rollback)\.sh)`.
The negative lookbehind excludes `.`, `/` and `-`, which is exactly the two
spellings an operator-facing document uses for a runnable script. And because
`SCRIPTNAME` matches only those six names and all six are in `future_scripts`,
**`unknown-script` cannot be tripped by any documentation edit at all** — I
computed the set difference: empty. See **S-3**.

## 6. Truthfulness — sentences still stronger than their control

Accurate, checked against what I measured: META_REPO §2a on known-false scope
("it only refuses a gate onto a probe someone has **declared** false, and cannot
tell a real probe from a fake one nobody declared" — correct and well put);
COMMANDS.md §4 on the derivation and the two manifest lists; the renderer
docstring, which now matches the code including the `ci_overrides` property;
COMMANDS.md §5 "What this does NOT prove"; the PR body's GitGuardian section;
the capacity note. The stale counts I raised as R-4 are gone from COMMANDS.md
and META_REPO.md — the only remaining figure there is the correct historical
"ten of the twelve models in the CI artifact for 69e197e".

Still stronger than the control:

| Sentence | Where | Measured |
|---|---|---|
| "it fails in **both directions**, so the list and the paragraphs are deleted together" | `COMMANDS.md:352`, `META_REPO.md:175`, `check-compose-topology.py:871`, **PR body** | one-directional; emptying the list with the paragraphs present is exit 0 |
| "must be listed in `gated_probes` and still **invoke** the command" | `META_REPO.md:162` | substring test; `echo pg_isready` passes |
| "whose probe no longer **invokes** the declared command" | `COMMANDS.md:348` | same |
| "Shell scripts, **backticked or bare**" | `check-template-claims.py:74` | a backticked `` `./backup.sh` `` is not matched |
| "73 assertions across **40** cases" | **PR body** | 39 `case_header` calls, 39 cases printed |

## 7. CI on `9c4b5d3e`

| Check run | Status | Conclusion | In the manifest? |
|---|---|---|---|
| `validate` | completed | **success** | **yes** — the only entry |
| `ci-required` | completed | **success** | the aggregate |
| `GitGuardian Security Checks` | completed | failure | **no** |

`.github/required-checks.txt` at this SHA has one live line, `validate`, and is
not in this PR's diff. All **18** `validate` steps succeeded, none skipped. From
the log: `13 shape(s) … 26 rules, 0 violations`, the coverage line, the
template-claims line, and `RESULT: 73 assertion(s) passed, 0 failed`.

**GitGuardian names no newer commit.** Its output reads "1 secret were uncovered
from the scan of **9 commits** in your pull request" — one incident, the PR's
whole commit range. I swept both new commits' added lines myself for
credential-shaped assignments and `scheme://user:pass@host`: **no hits in either
`7e95989` or `9c4b5d3`**. The red is attributable to `a96f188` alone, as stated.

## 8. Scope

| Check | Result |
|---|---|
| Component repositories modified | **No** — 0 paths under `vizra-{core,user,search}/` |
| `docs/quality/features.json` | **byte-identical to `main`** |
| `docs/evidence/ledger-generator/` | **untouched**; `build.py:20` PLANNED/UNVERIFIED gate present |
| `.github/required-checks.txt` | **untouched** |
| New credential-shaped literal in either new commit | **none** |

---

# Findings — round 3

```
FINDING S-1: known-false-undisclosed is one-directional, and four places say it is not
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-compose-topology.py:875-876 (the guard) and :871 (the comment);
             docs/quality/COMMANDS.md:352; docs/META_REPO.md:175; the PR #4 body
  requirements: VZ-TOPOLOGY-002, VZ-OPS-008

Observed:
  The rule body is entered only when the list is non-empty:

      disclosure = manifest.get("known_false_disclosure") or {}
      if known_false and disclosure:          # :876
          marker = disclosure.get("marker", "")
          for rel in disclosure.get("files", []):
              ...

  Measured, from a clean clone at this SHA:

    - marker deleted from env/production.env.example, list populated -> exit 1,
      `rule=known-false-undisclosed service=env/production.env.example`
    - marker deleted from README.md, list populated                  -> exit 1
    - `known_false_probes` emptied, BOTH paragraphs left in place     -> exit 0
      (compose topology: 13 shape(s) … 26 rules, 0 violations)

  The documentation says the opposite in four places, including the line
  immediately above the guard:

    check-compose-topology.py:871  "It fails in both directions by construction:
                                    emptying the list without …"
    COMMANDS.md:352                "it fails in both directions, so the list and
                                    the paragraphs are deleted together"
    META_REPO.md:175               "and it fails in both directions, so **the
                                    list and the paragraphs are deleted together**"
    PR #4 body                     "that paragraph and the list are deleted
                                    together, enforced in both directions"

Failure:
  The direction that is unenforced is the one that matters later. The disclosure
  paragraph tells an operator to IGNORE the `healthy` column in
  `docker compose ps`. `vizra healthcheck` is queued in vizra-core (queue 2h);
  when it lands and the known-false list is emptied, nothing makes the author
  delete the paragraphs — and META_REPO.md tells them a rule already handles it.
  The instance is then shipping a README and a production template instructing
  operators to distrust a health column that has become trustworthy, which is
  how a real outage gets diagnosed slowly. The claimed control is precisely what
  would have prevented it.

Perspective:
  operator, instance-admin, developer

Recommendation:
  Three lines. Run the block unconditionally and branch on the list:

      if disclosure:
          marker = disclosure.get("marker", "")
          for rel in disclosure.get("files", []):
              text = read(rel)
              if known_false and marker not in text:
                  violation(... "must carry the disclosure while known_false_probes is non-empty" ...)
              if not known_false and marker in text:
                  violation(... "still carries the disclosure, but known_false_probes is empty:"
                                " the probes were fixed and the paragraph now tells operators"
                                " to distrust a column that works" ...)

Acceptance criteria:
  - Emptying `known_false_probes` while either declared file still contains the
    marker fails the lane, exit 1, naming the file.
  - Deleting the marker while the list is non-empty still fails (no regression).
  - Emptying the list AND removing both paragraphs in the same change is green.
  - The four sentences above become true, or are rewritten to match.

Tests:
  docs/evidence/compose-topology/demo.sh, beside the existing disclosure case:
  empty `known_false_probes` in scripts/compose-shapes.json with the paragraphs
  in place, assert exit 1 with rule=known-false-undisclosed, restore, assert
  exit 0. The harness already mutates that file in case 12.

Cross-repo implications:
  core: `vizra healthcheck` (queue 2h) is the change that will empty the list and
  trip this | user: none | search: none | meta: three lines plus a demo case.

Challenge:
  "The list is non-empty today, so the unenforced direction cannot fire." True —
  and it becomes live on the exact change the documentation is written to
  survive. A guarantee that is false only in the future is still false now, and
  this one is asserted in the PR body a merge decision is read from.
```

```
FINDING S-2: gated-probe-unrecognised tests for a mention, and two documents say "invoke"
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-compose-topology.py, check_probes() — `rule["must_invoke"] not in joined`;
             docs/META_REPO.md:162; docs/quality/COMMANDS.md:348
  requirements: VZ-TOPOLOGY-002, VZ-OPS-008

Observed:
  `joined = " ".join(str(x) for x in dep_test)` and the test is
  `rule["must_invoke"] not in joined` — a substring match over the rendered
  healthcheck command line.

  Measured on `postgres`, which three services gate on with
  `condition: service_healthy` (api, worker, migrate). Each probe below always
  exits 0, so all three gates gate on nothing:

    ["CMD-SHELL", "pg_isready -U vizra || true"]   -> 26 rules, 0 violations
    ["CMD-SHELL", "true # pg_isready"]             -> 26 rules, 0 violations
    ["CMD", "sh", "-c", "exit 0; pg_isready"]      -> 26 rules, 0 violations
    ["CMD", "echo", "pg_isready"]                  -> 26 rules, 0 violations

  The declared case is caught, and so is the disabled case:

    ["CMD", "true"]  -> rule=gated-probe-unrecognised (api, worker, migrate)
    ["NONE"]         -> rule=missing-healthcheck AND rule=gated-probe-unrecognised

  The documentation claims execution, not mention:

    META_REPO.md:162   "must be listed in `gated_probes` and still INVOKE the
                        command that makes its probe mean something"
    COMMANDS.md:348    "or whose probe no longer INVOKES the declared command"

Failure:
  A maintainer under pressure to empty the known-false list — which META_REPO.md
  says "must be empty before VZ-ISSUE-004's boot lane lands" — can satisfy every
  rule here with `pg_isready || true` and believe the checker vetted it, because
  the checker's own documentation says it checks invocation. The deploy then
  proceeds past a PostgreSQL that is not accepting connections, which is the
  failure the whole F3 round exists to prevent.

  This is not a demand that the rule become a classifier. It cannot be one: you
  cannot decide from a rendered model whether a shell string exits non-zero when
  the server is down. The finding is that the description promises what the
  implementation cannot do.

Perspective:
  operator, developer

Recommendation:
  Two parts, both small.
  1. Say what it does: "…and its probe must still NAME the declared command.
     This is a mention, not an execution check: `pg_isready || true` and
     `echo pg_isready` both pass. It raises the cost of killing a gate; it
     cannot prove a probe can go red."
  2. Refuse the cheap defeats that ARE decidable from the string, as a declared
     denylist rather than a classifier: a `CMD-SHELL` test containing `|| true`,
     `; true`, `# ` before the declared command, or whose first token is `echo`
     or `true`. Name it in the message as a denylist so nobody mistakes it for
     coverage.

Acceptance criteria:
  - `["CMD-SHELL","pg_isready || true"]` on a gated service fails the lane.
  - `["CMD","echo","pg_isready"]` fails the lane.
  - The real probe `["CMD-SHELL","pg_isready -U \"$POSTGRES_USER\" -d …"]` still
    passes (the token match must survive interpolation, which is why it exists).
  - Both documents describe a mention plus a denylist, not an invocation check.

Tests:
  demo.sh beside case 26: `pg_isready || true` red for
  rule=gated-probe-unrecognised, restored, green.

Cross-repo implications:
  core: none | user: none | search: none | meta: the rule and two sentences.

Challenge:
  "Any denylist is bypassable too, so only the wording needs fixing." A fair
  reading, and I would accept wording alone. What I will not accept is the
  current pair: a rule that catches `["CMD","true"]` and nothing else, described
  as checking invocation, in the document a reviewer uses to decide what is
  proven.
```

```
FINDING S-3: the script pass misses ./backup.sh and scripts/backup.sh, and unknown-script cannot fire
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-template-claims.py:74-83 (SCRIPTNAME and its comment);
             env/registry/meta.json (`future_scripts`)
  requirements: VZ-CI-002, VZ-OPS-008

Observed:
  SCRIPTNAME = re.compile(
      r"(?<![\w./-])((?:backup|restore|install|bootstrap|deploy|rollback)\.sh)"
  )

  The negative lookbehind excludes `.`, `/` and `-`. Measured, each inserted
  into env/production.env.example with no marker within 2 lines:

      backup.sh                 -> exit 1  rule=unmarked-future-script
      bash backup.sh            -> exit 1
      bootstrap.sh in a `:?`    -> exit 1
      ./backup.sh               -> exit 0
      `./backup.sh` (backticked)-> exit 0
      scripts/backup.sh         -> exit 0
      rotate-secrets.sh         -> exit 0

  And `unknown-script` is unreachable from any documentation edit. SCRIPTNAME
  matches exactly six names; env/registry/meta.json lists all six in
  `future_scripts` and none in `scripts`. The set difference
  {matchable} − {future} − {existing} is EMPTY, so no string in any scanned file
  can reach the `unknown-script` branch. It fires only if someone edits
  meta.json itself.

  The code comment above the regex says "Shell scripts, backticked or bare" — a
  backticked path form is neither.

Failure:
  The two spellings the checker misses are the two an operator-facing document
  actually uses: you write `./backup.sh` or `scripts/backup.sh` when you mean
  "run this", and the bare word when you mean "the backup tool". The round-2
  finding this rule exists to close was a present-tense claim about a script
  that does not exist; the same claim written `Run ./backup.sh nightly` passes
  today. `unknown-script` gives the appearance of covering invented scripts and
  covers none.

Perspective:
  operator, developer

Recommendation:
  Allow an optional leading `./` or `scripts/` or `deploy/` instead of excluding
  it — the lookbehind is there to avoid matching inside a longer word, which
  `(?<![\w-])` alone achieves once the path prefix is consumed:

      SCRIPTNAME = re.compile(
          r"(?<![\w-])(?:\./|scripts/|deploy/)?"
          r"((?:backup|restore|install|bootstrap|deploy|rollback)\.sh)"
      )

  For `unknown-script`: either match any `[a-z][a-z0-9-]*\.sh` and let the
  future/existing lists decide — which is what makes the rule reachable — or
  delete the rule id and stop listing a rule that cannot fire.

Acceptance criteria:
  - `./backup.sh`, `scripts/backup.sh` and `` `./backup.sh` `` without a marker
    each fail the lane.
  - A path-form reference WITH its marker within the window passes.
  - Either an invented `rotate-secrets.sh` fails with `unknown-script`, or that
    rule id is removed from RULES.
  - The code comment describes the forms actually matched.

Tests:
  demo.sh, beside the existing script case: the `./` form red, restored, green.

Cross-repo implications:
  core: none | user: none | search: none | meta: one regex, one comment, one
  demo case.

Challenge:
  "No document in the tree writes `./backup.sh` today." Correct — I checked, all
  three live references are bare and correctly marked. The rule's purpose is the
  next document, and the next document is where a path form is most likely.
```

```
FINDING S-4: the demonstration harness can report a correct guard as FAILED
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/evidence/compose-topology/demo.sh:23 (`set -uo pipefail`) and
             :375 (and every `printf … | grep -q` in the file)
  requirements: VZ-CI-002

Observed:
  In my clean run at this SHA, in a clone nothing else was touching:

      RESULT: 72 assertion(s) passed, 1 failed
      DEMO2 exit=1

  The failing case, verbatim:

      CASE 10a — an INVALID external DSN
      docs/evidence/compose-topology/demo.sh: line 375: printf: write error: Broken pipe
          FAIL: expected exit 1 with an actionable message, got 1
            | shape prod-external-postgres: DATABASE_URL is not a valid DSN: it does not start with postgres:// …
            |   (The value is not echoed here; it carries a password.)

  The guard behaved correctly — exit 1, the actionable message, the value not
  echoed. The harness reported FAIL, and its own message is self-contradictory
  ("expected exit 1 … got 1"). The mechanism is line 375:

      if [ "$rc" = "1" ] && printf '%s\n' "$out" | grep -q 'DATABASE_URL is not a valid DSN'; then

  `grep -q` exits at the first match and closes the pipe; `printf` then takes
  EPIPE; `set -o pipefail` (line 23) propagates that non-zero through the
  pipeline even though grep matched. The `if` takes the else branch.

  It is intermittent: the same pipeline in isolation returned true 20/20 times
  for me, and CI reported 73/73 on this SHA. It fires under load, which is what
  a full demo run with concurrent `docker compose` provides.

Failure:
  `validate` is a required lane and this step is one of its gates, so the lane
  can go red with no product cause — and the message it prints sends whoever
  reads it hunting a regression that does not exist. It is fail-closed (the `ok`
  branch requires the pipeline to succeed, so a genuinely broken guard cannot be
  reported as passing this way), which is why this is SHOULD and not higher. But
  "all 40 cases red for their declared reason" is not reproducible on my
  environment, and CI's green is partly timing.

Perspective:
  developer

Recommendation:
  Take the pipe out of the condition. Either capture first:

      printf '%s\n' "$out" > "$tmp"; grep -q '…' "$tmp"

  or use a here-string, which has no pipeline and no SIGPIPE:

      grep -q '…' <<< "$out"

  The same construct appears throughout the file; fix it in the `expect` helper
  and at every open-coded site (10a, 10b and the redaction cases).

Acceptance criteria:
  - Ten consecutive local runs of demo.sh report the same assertion count and
    exit 0.
  - No `printf: write error: Broken pipe` in any transcript.
  - A deliberately broken guard is still reported FAIL (the fix must not make
    the condition unconditionally true).

Tests:
  Run demo.sh ten times in a loop and diff the RESULT lines. Worth doing once
  before merge, since the lane is required.

Cross-repo implications:
  core: none | user: none | search: none | meta: demo.sh only.

Challenge:
  "CI is green and you cannot reproduce it in isolation." Both true, and that is
  the shape of the problem: a required lane whose result depends on scheduling
  is one I cannot certify as reproducible, and the next person to see it red
  will be told the DSN guard broke when it did not.
```

```
FINDING S-5: --drift compares key names only, never the "secret" flag the redaction now depends on
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-config-coverage.py check_drift() (quoted-literal scan
             over source_files, compared against key NAMES);
             scripts/compose-render.py registry_secret_names()
  requirements: VZ-TOPOLOGY-007, VZ-OPS-008

Observed:
  The R-1 fix makes the redaction set derive from `"secret": true` in the
  component registries. `--drift` is the only check that compares a registry to
  its component, and it compares presence of NAMES:

      found = {quoted literals and ENV assignments in source_files}
      new  = found - known - ignore
      gone = known - found

  Nothing compares the `secret` flag, or `default`. Measured: I materialised all
  three components' `source_files` from their `origin/main` with `git show`,
  confirmed `config registry drift: every snapshot matches its component source`
  (exit 0), then deleted `"secret": true` from `VIZRA_SESSION_SECRET` in
  env/registry/core.json. `--drift` still reported

      config registry drift: every snapshot matches its component source   exit 0

  and the coverage lane stayed green.

  No value leaks today, because all five registry-flagged secrets are ALSO in
  the manifest's `redact_keys`/`secret_keys` — I computed the difference:
  registry-only = []. The derivation carries nothing alone yet.

Failure:
  The durable half of the R-1 fix rests on a field that no check validates
  against its source. A snapshot re-taken carelessly, or hand-edited, can drop a
  `secret` flag and narrow the redaction set silently while the drift check says
  the snapshot matches. For the next component secret — one not in the manifest
  lists — that is the R-1 defect again, arriving through the door R-1's fix
  walked in.

Perspective:
  developer, operator

Recommendation:
  Compare the flag where the component declares it. `vizra-core`'s
  `internal/config/keys.go` writes `Secret: true` in the same struct literal as
  `Name:`, so the existing scan can read both; `vizra-search` and `vizra-user`
  need the same treatment or an explicit "this component declares no secrets"
  note. Failing that, at minimum fail when a key in `redact_keys` is NOT flagged
  in its registry — the union hides that today.

Acceptance criteria:
  - Removing `"secret": true` from any registry key that the component's source
    marks secret fails `--drift`, exit 1.
  - The honest snapshots still pass (exit 0).
  - The BLOCKED path with the checkouts absent still exits 2.

Tests:
  A drift case in demo.sh cannot run in CI (no checkouts). Record it in
  docs/evidence/compose-topology/drift-transcript.txt the way the current drift
  evidence is recorded, red and green.

Cross-repo implications:
  core: `keys.go` already carries the flag in a parseable form | user: none |
  search: none | meta: the drift scan.

Challenge:
  "Drift is a coarse quoted-literal net by design, and flags are not literals."
  Agreed for names. But the flag is now load-bearing for a security control, and
  a security control resting on an unvalidated field is the thing I raised in
  R-1 one level down.
```

```
FINDING S-6: a credential the registry does not flag and whose name matches no suffix is still written raw
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     scripts/check-config-coverage.py:76 (SECRET_NAME_SUFFIXES);
             scripts/compose-render.py registry_secret_names()
  requirements: VZ-OPS-008

Observed:
  SECRET_NAME_SUFFIXES = ("_PASSWORD", "_SECRET", "_TOKEN", "_KEY").

  Measured: `VIZRA_S3_ACCESS_ID` added the fully correct way but WITHOUT
  `"secret": true` — registered in env/registry/core.json, declared in
  env/production.env.example, delivered by compose — renders with the value
  present 47 times across the 13 models, stamp `secret_values_redacted: true`,
  and render / topology / coverage / template-claims all exit 0.

  The same key named `VIZRA_SMTP_PASSWORD` IS caught, by the suffix net:
  `unclassified-secret-key … is named like a secret (_PASSWORD) but is neither
  flagged secret in a registry nor listed in redact_keys`.

  An AWS access key id is a credential; `_ID` matches nothing. M2's storage
  slice adds exactly this shape of key.

Failure:
  Bounded and one step removed from R-1: it needs a component to declare a
  credential without flagging it secret, which is a component-side bug. But the
  meta repo is where the value gets written to an uploaded artifact, so it is
  also where the backstop belongs.

Perspective:
  developer, operator

Recommendation:
  Add `_ID` only where it is preceded by a credential word, or better, add the
  handful of known credential-name shapes (`*_ACCESS_ID`, `*_ACCESS_KEY_ID`,
  `*_CLIENT_ID` is NOT one) as a declared list with the existing
  `not_secret_despite_name` escape hatch the checker already offers. One
  declared exception beats a wider matcher — which is the rule's own stated
  philosophy.

Acceptance criteria:
  - `VIZRA_S3_ACCESS_ID` unflagged fails `unclassified-secret-key`.
  - `VIZRA_SEARCH_URL` and other plain addresses still pass.
  - `not_secret_despite_name` still silences a declared false positive.

Tests:
  demo.sh beside the existing unclassified-secret-key case.

Cross-repo implications:
  core: should flag it at source when M2 adds it | user: none | search: none |
  meta: one tuple and a demo case.

Challenge:
  "The primary signal is the component's own flag, and a name matcher will never
  be complete." Right — which is why this is a NIT and why I am asking for a
  named list rather than a cleverer regex.
```

```
FINDING S-7: the PR body's case count, and its repetition of the "both directions" claim
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     the PR #4 body
  requirements: VZ-CI-002

Observed:
  The body is otherwise accurate and much improved — head SHA, 26/11/4 rule
  counts, the GitGuardian incident stated with its id and the commit it belongs
  to, the alias ruling, and a "What a green result does NOT prove" section that
  correctly narrows `probe-gates-readiness`. Two items do not hold:

  - "**73 assertions across 40 cases**". `grep -c '^case_header "'` is 39 and 39
    cases printed in my run. The extra one is the function definition — the same
    off-by-one I reported as R-4 last round and made myself before checking.
  - "that paragraph and the list are deleted together, **enforced in both
    directions**" — disproved in S-1.

Failure:
  Documentary, and the second one repeats a claim the merge decision is read
  from.

Perspective:
  developer

Recommendation:
  Fix both when S-1 is fixed; if S-1 is fixed as recommended the second sentence
  becomes true as written.

Acceptance criteria:
  - The case count matches `case_header` CALLS.
  - No claim in the body outlives the control it describes.

Tests:
  None mechanical.

Cross-repo implications:
  core: none | user: none | search: none | meta: PR body.

Challenge:
  "One number." It is the third round in which a recorded count in this PR is
  off by the same mistake, in a repository whose COMMANDS.md argues recorded
  figures must be trustable.
```

---

# Round-2 findings — disposition

| Round-2 finding | Severity | Status at `9c4b5d3e` | Verified by |
|---|---|---|---|
| **R-1** nothing forces a new secret into the redaction set | REQUIRED | **CLOSED in substance** | derivation from `"secret": true`; my exact mutation 47 → 0; alias-name and labels/command paths also 0; case 18b does not regress; CI artifact clean. Residuals filed as **S-5** and **S-6** |
| **R-2** docstring described a wider leak-check set than the code used | SHOULD | **CLOSED** | docstring now describes the derivation and the two manifest lists, and states the `ci_overrides` property correctly |
| **R-3** probe rule could not see an undeclared fake probe | SHOULD | **PARTLY CLOSED** | `gated-probe-unrecognised` exists and catches `["CMD","true"]` and `["NONE"]`; four one-line bypasses remain and the docs say "invoke" — **S-2** |
| **R-4** stale counts in COMMANDS.md / META_REPO.md | NIT | **CLOSED** | no stale shape/rule/case figure remains in either file |
| **R-5** stale PR body | SHOULD | **CLOSED but for two items** | rewritten and accurate on head, counts, GitGuardian, alias, limits — except **S-7** |

Infrastructure PARTIALs: **F4 and NEW-1 closed** (verified by four mutations
each); **F2 closed in substance**, with the reach gap at **S-3**; **F3 closed
one-directionally**, at **S-1**.

## Cleanup

Both clones and all scratch output live under one `mktemp -d` directory inside
the shared scratch root and are deleted by exact path. Component checkouts were
read with `git -C … show origin/main:<path>` only — nothing checked out, fetched
into a working tree or modified; no branch switched in the chair's checkout. No
container started, no image pulled or built. The only file written outside my
scratch directory is this one.

FINAL VERDICT: FAIL — SHA 9c4b5d3285e1368634bc2042a83a91bfcb7e564b

---

# Re-verification at cf9e4c8 (2026-09-21)

Same verifier. Three clones under one private `mktemp -d`: `loop/` runs the
demo stability loop and is never edited, `atk/` takes every mutation, `prev/`
holds `9c4b5d3` for the model comparison. No container started. Only this file
written outside my scratch.

| | |
|---|---|
| Head SHA verified | `cf9e4c86b077335fcad8cf8050c8fe57a50431c2` |
| Head moved? | No — read `cf9e4c86` at the start; every CI/artifact query below names it. |
| Previous head | `9c4b5d3e` (my FAIL). Two commits on top, plain push. |
| Environment | macOS arm64, Python 3.9.6, PyYAML 6.0.3, Docker Engine 29.8.0, Compose v5.5.1 (CI: v2.38.2) |

## 0. Scope first — the topology did not move

`git diff --name-only 9c4b5d3 HEAD` touches **no** `docker-compose*.yml`, no
`.github/`, no `features.json`, no `build.py`, no component directory. I checked
the stronger thing the chair asked for: I rendered all 13 shapes at **both**
SHAs and compared the models.

```
SERVICE-MODEL DIFFERENCES (clone paths normalised): 1
  bundle-no-checkouts.json -> caddy.volumes[0].source
     .../vizra-bundle-0t7__4oc/deploy/Caddyfile.local   (prev)
     .../vizra-bundle-3p7mlxme/deploy/Caddyfile.local   (new)
provenance differences: none
```

The single difference is the random `mktemp -d` name of the bundle tree. **The
rendered compose semantics are identical.** Everything below is about the
checkers and the prose, which is what this slice was scoped to.

| Check | Result |
|---|---|
| `docs/quality/features.json` | byte-identical |
| `build.py:20` PLANNED/UNVERIFIED gate | present |
| `.github/required-checks.txt` | untouched (one live entry, `validate`) |
| Component repositories | untouched |

## 1. Lanes and counts

| Command | Exit | Result |
|---|---|---|
| `check-generated-ledger.sh` / `check-quality-json.py` / `check-doc-links.py` / `ci-required-guard.sh` | 0 | as before |
| `claims.py --check` | 0 | `CLAIMS.md is current (47 audited claims)` |
| `compose-render.py --all` | 0 | 13 shapes |
| `check-compose-topology.py` | 0 | `13 shape(s) … **27 rules**, 0 violations; 2 known-false probe(s)` |
| `check-config-coverage.py` | 0 | `34 component keys, 58 template keys, 58 interpolated variables, 13 shapes; 1 alias; 1 retired key refused; 0 violations` |
| `check-template-claims.py` | 0 | `16 command and script reference(s); 5 shipped, 11 future commands, 0 script references resolved to a file, 6 scripts declared future` |
| `demo.sh` (run 1 of 10, isolated clone) | 0 | **`RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`**, 0 broken pipes, tree clean |

Counted from source: **27** topology rule ids, **11** coverage, **4** template —
every claimed count reproduces, and the demo line is byte-identical to CI's.

## 2. Acceptance bullets — my own renderer, 13 shapes, 0 violations

Re-rendered with plain `docker compose config --format json` and audited myself
(ports, restart, log cap, healthcheck state, production build, image pinning,
`mem_limit`, privileged/host-network): **0 violations found by me.**
postgres/redis/search/clickhouse/migrate/worker publish **nothing** in any of the
13; api and frontend loopback only; caddy `edge`-only on 80/443; ipfs 4001 the
only other public port; external overlays delete their container;
`prod-worker-split` renders worker alone and publishes nothing;
`prod-frontend-only` renders frontend alone. **All three VZ-ISSUE-002 acceptance
bullets remain MET.**

## 3. CLAIMS.md, line by line

I parsed all **47** rows and resolved every `file:line` myself: every anchor
lands on a line that really contains the quoted claim. (My first automated
relevance heuristic flagged 14 rows; reading each one, all 14 are exact — the
heuristic had filtered out the distinctive words. Recording that so the number
is not mistaken for a finding.)

Kinds: 37 `demonstrated`, 6 `no mechanism`, 2 `code-only`, 2 `not ours`.

### 3a. The adversarial mutation sample — 20 rows, run by me

Every row below uses a guarantee word. I made its sentence false in the tree and
recorded what fired.

| CLAIMS row | Mutation | Result |
|---|---|---|
| 19, 18 | `ports:` on postgres in the BASE file | `rule=never-published` |
| 18 | `ports:` on the cache **via the prod overlay** (invisible to a grep of the base) | `rule=never-published` |
| 35 | ipfs publishes the Kubo API 5001 | `rule=port-not-allowed` |
| 12 | `postgres:18@sha256:…` → `postgres:18` | `rule=unpinned-image` |
| 13 | `healthcheck: disable: true` | `rule=missing-healthcheck` |
| 13 | `healthcheck: test: ["NONE"]` | `rule=missing-healthcheck` |
| 11 | service on profile `backup`, publishing 5432 | `rule=profile-not-enumerated` |
| 4 | compose delivers the **retired** `VIZRA_SEARCH_HMAC_KEY` | `rule=retired-key-delivered` ×34 |
| 22 | a template key with no consumer | `rule=template-key-unused` |
| 47 | a shape deleted from the manifest | `SHAPE FLOOR VIOLATION`, render exit 1 |
| 14, 45 | `POSTGRES_PASSWORD` removed from `redact_keys` | render exit 1, **0 files written** |
| 10, 29, 33 | marker deleted from `env/production.env.example` | `rule=known-false-undisclosed` |
| 10, 29, 33 | marker deleted from `README.md` | `rule=known-false-undisclosed` |
| 10, 29, 33 | `known_false_probes` **emptied**, both paragraphs left | **`rule=known-false-stale-disclosure`** |
| 5 | `service_healthy` edge onto `api` (declared known-false) | `rule=probe-gates-readiness` |
| 9 | api probe changed so the declaration is stale | `rule=stale-known-false-probe` |
| 7 | the five probe spellings (below) | `rule=gated-probe-unrecognised` |
| 25 | six script spellings (below) | `unmarked-future-script` / `unknown-script` |
| 17, 44 | a registry-flagged new secret | **47 → 0** occurrences |
| 23, 41 | `--drift` with the `secret` flag stripped / with no checkouts | exit 1 / exit **2 BLOCKED** |

Every one turned red for the reason its row cites. The one row whose *negative*
is the evidence — row 17/44's `VIZRA_S3_ACCESS_ID` — reproduces exactly as
stated: **47 occurrences, every lane exit 0**. The row says so in its own "does
NOT guarantee" column.

### 3b. Can `claims.py --check` be satisfied while a claim is false?

The generator's **positive** claims hold. I broke an anchor two ways:

```
anchor reworded away  -> exit 2  "the anchor '…' no longer appears in docs/META_REPO.md"
anchor duplicated     -> exit 2  "appears 2 times … an audit row must name one sentence"
```

But the **claim text** and the **Red-when** cells are hand-written in
`claims.py` and tied to nothing:

- I prefixed `Only ONE shape ` to the sentence row 1 audits, inverting it
  (row 1 claims *“Every declared shape is rendered on every run”*). The anchor
  substring still resolved uniquely → **`claims.py --check` exit 0**.
- I rewired row 7's Red-when from `26, 26a…26e` to `1, 2, 3` — the *port* cases,
  which test something else entirely. **Regeneration exit 0, `--check` exit 0.**

So `--check` proves (i) every anchor resolves uniquely and (ii) CLAIMS.md is
byte-identical to what the generator emits. It does **not** prove the claim text
still describes the anchored sentence, nor that the cited cases exercise the
claim. See **T-2**.

### 3c. The "16 of 42" admission

Accurate as a count, and computed rather than hand-listed. The gap is where it
is published: `COMMANDS.md` §8 and CLAIMS.md say it in prose, while the **rule
tables at `COMMANDS.md:363-375` describe all ten undemonstrated topology rules
in exactly the same voice as the demonstrated ones.** Named, with the line that
still reads as a demonstrated guarantee:

| Line | Rule ids with no demonstration, described as controls |
|---|---|
| `:368` | `docker-socket`, `privileged`, `host-network`, `no-new-privileges` |
| `:369` | `missing-service`, `unexpected-service` |
| `:370` | `dev-mode-in-production`, `dev-hatch-in-production` |
| `:363` | `oneshot-restart` |
| `:366` | `missing-build` |

None is false — I have personally seen `host-network` fire (round 1) — but a
reader of the table alone is not told. See **T-3**.

### 3d. The converse — guarantee sentences with no row

CLAIMS.md declares its scope (`META_REPO.md` §2a; `COMMANDS.md` §4–§8; four
docstrings/banners; README's operator section; the production template's
comments about tooling). Swept **inside that scope** for
every/never/cannot/refuses/enforced/both directions/invokes/proves/guarantee,
excluding lines within ±3 of an audited anchor, I found at least four
unaudited guarantee sentences:

| Sentence | Verified by me |
|---|---|
| `COMMANDS.md:437` "Every long-running service in a production shape declares [a `mem_limit`]" | true — case 16 and my own 13-shape audit |
| `COMMANDS.md:528-531` the retired key is "a guaranteed boot refusal" | true — 34 × `retired-key-delivered`, and core's `RetiredKeys` at `keys.go:91` |
| `COMMANDS.md:534-536` "Every alias carries an explicit `authorised` decision … printed on every green run" | true — verified at 9c4b5d3 (`alias-floor` fires both ways) and printed in this run |
| `COMMANDS.md:647` "No condition in the harness reads its captured output through a pipe. Every one uses a here-string" | true — `grep -c '| grep -q' demo.sh` = **0** |

All four are **true but unaudited** — a completeness gap in the table, not a
false claim. See **T-5**.

## 4. S-2 — the probe tokeniser. This is the strong part of the round.

`probe_invokes()` is structural: `["CMD", argv…]` → `basename(argv[0])` must
**equal** the declared command; `["CMD-SHELL", s]` → `s` must contain none of
`SHELL_CONTROL = (";","|","&","#","`","$(","<",">","\n")` and its first word's
basename must equal the declared command; anything else fails closed.

| Rendered probe on `postgres` (gated by api, worker, migrate) | Result |
|---|---|
| `["CMD","true"]` | **red** |
| `["CMD-SHELL","pg_isready -U vizra \|\| true"]` | **red** |
| `["CMD-SHELL","true # pg_isready"]` | **red** |
| `["CMD","sh","-c","exit 0; pg_isready"]` | **red** |
| `["CMD","echo","pg_isready"]` | **red** |
| `["NONE"]` | **red** (`missing-healthcheck`) |
| `["CMD","/tmp/pg_isready/true"]` — a *directory* named pg_isready | **red** |
| `["CMD","env","pg_isready"]` | **red** |
| `["CMD","sh","-c","pg_isready"]` | **red** |
| `["CMD-SHELL","PGHOST=x pg_isready"]` — leading assignment | **red** |
| `["CMD-SHELL","exec pg_isready"]` | **red** |
| `["CMD-SHELL","pg_isready； true"]` — full-width semicolon | **red** |
| `["CMD-SHELL","pg_isready \|\| true"]` — NBSP separator | **red** |
| `["CMD-SHELL","pg_isready && true"]` | **red** |
| **real newline** `["CMD-SHELL","pg_isready\nexit 0"]` (YAML block list) | **red** |
| `["CMD","/usr/bin/pg_isready","-U","vizra"]` | green — **correct**, basename matches a real probe |
| `["CMD-SHELL","pg_isready -U $POSTGRES_USER"]` | green — **correct**, `$VAR` is not substitution syntax and cannot change the exit status |
| `["CMD-SHELL","  pg_isready\t-U vizra"]` | green — **correct**, whitespace only |
| `["CMD-SHELL","pg_isready --version"]` | green — **the stated, measured residual** (CLAIMS row 7, `local-run.txt`) |
| baseline: the real probes (`pg_isready -U "vizra" -d "vizra"`, `valkey-cli ping`) across all 13 shapes | green |

**A correction to my own testing.** My first newline attempt reported green; the
`\n` had not survived my one-line YAML edit as a real newline. Re-done with a
YAML block list so a real newline lands in the rendered model, the rule fires.
I nearly filed that as a REQUIRED finding — it would have been wrong.

**What the rule guarantees now, plainly:** every `service_healthy` target must be
listed in `gated_probes`, and its rendered probe must be a single command whose
basename is the declared one, with no shell control or substitution syntax.
**What it does not:** that the command can exit non-zero (`pg_isready --version`
passes and always succeeds), and that a binary with the right name is the real
one. Both need a running container. `META_REPO.md:169`, `COMMANDS.md:419` and
the function's own docstring state exactly those two limits, and CLAIMS row 7
and row 20 carry them. **My round-3 S-2 is closed and the documentation now
matches the control.**

## 5. S-1, S-3, S-5, S-6, NEW-3

**S-1 — closed, by distinct rule ids.** Both directions fire, and a reviewer can
tell which: `known-false-undisclosed` (list stands, paragraph gone — either
file) and `known-false-stale-disclosure` (list emptied, paragraphs stand). The
marker-string limit is still real — stripping the `curl` commands while leaving
the heading is green — and it is conceded in CLAIMS rows 10/29/33 *and* in the
"Known weak spots" section. Stated, so not a finding.

**S-3 — closed.**

| Spelling, no marker | Result |
|---|---|
| `backup.sh`, `./backup.sh`, `scripts/backup.sh`, `` `./backup.sh` ``, `deploy/rollback.sh` | all **red**, `unmarked-future-script` |
| `rotate-secrets.sh` | **red**, `unknown-script` — the rule is reachable now |
| `./backup.sh` **with** its `VZ-ISSUE-004` marker | green — no false positive |
| `scripts/ci-required-guard.sh` (a script that **exists**) | green — correctly not flagged |
| `bootstrap.sh` in a compose `:?` message; `./backup.sh` in a YAML comment | both **red** |
| `BACKUP.SH` (uppercase) | green — a gap nobody writes; noted, not filed |

**S-5 — closed and honestly bounded.** `--drift` now compares the `secret` flag:
stripping `"secret": true` from `VIZRA_SESSION_SECRET` gives
`rule=registry-drift … the snapshot's secret FLAG disagrees with the component`,
exit 1. On the same tree the CI lane is exit 0 — which is the stated limit,
because drift needs the checkouts. It also prints, every run, that
`vizra-search` and `vizra-user` flags are **UNCHECKED** with the reason and the
count. Absent checkouts: exit **2 BLOCKED**.

**S-6 — stated, not fixed, as agreed.** `VIZRA_S3_ACCESS_ID` unflagged: 47
occurrences, every lane exit 0. CLAIMS rows 17 and 44 and `COMMANDS.md:332-339`
say so in those words.

**NEW-3 — verified against the rendered model.** `README.md:100-110` names
`VIZRA_HTTP_PORT` and `VIZRA_FRONTEND_PORT` beside `:8080` and `:3000`, which
match the loopback publishes I re-derived; `/readyz` is now
`curl -sS … ; echo   # NO -f: /readyz answers 200 "degraded"` in **both**
`README.md:105` and `env/production.env.example:182-183`.

## 6. S-4 — the pipe race

`demo.sh` contains **zero** `| grep -q` sites and one `set -uo pipefail`. The
only remaining sites in the repository are in files this PR does not touch:

```
scripts/ci-required-guard.sh:80,249,348,423,440   (5 sites)  — in diff? no
scripts/ci-required-select.sh                      (0 sites) — in diff? no
```

The builder's follow-up list names `ci-required-guard.sh` lines 80, 249, 348,
423 and 440 — **exactly the five I find**. It also names
`ci-required-select.sh:56`; that line is
`status="$(printf '%s' "$line" | cut -f2)"` — a `| cut` inside a command
substitution, not a `grep -q` early-exit, and `cut` consumes its whole input, so
it is not the same race. One entry of the follow-up list is misdescribed (**T-4**).

The stability loop is reported in §9.

## 7. Regression

| | |
|---|---|
| R-1 redaction, my registry-flagged-secret mutation | **47 → 0**, and `rule=unclassified-secret-key` fires |
| Case 18b (key removed from `redact_keys`) | render exit 1, 0 files written |
| **CI artifact for THIS SHA** (run `35582443280`, 37 204 B) | **14 files, 0 secret-value hits**; `api.DATABASE_URL` = `'<redacted>'`; stamp true, `redacted_keys: 8`, `leak_checked_keys: 8` |
| V1–V9, F1–F4, `postgres-shm-floor` | all re-exercised above or unchanged by a diff that touches no compose file |
| Acceptance bullets | MET, from my own renderer, 0 violations |

## 8. CI on `cf9e4c8`, and GitGuardian

| Check run | Status | Conclusion | In the manifest? |
|---|---|---|---|
| `validate` | completed | **success** | **yes** — the only entry |
| `ci-required` | completed | **success** | the aggregate |
| `GitGuardian Security Checks` | completed | failure | **no** |

All **18** `validate` steps succeeded, none skipped. The job log carries
`13 shape(s) … 27 rules, 0 violations`, the coverage and template-claims lines,
and **`RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`** — identical
to my local run.

GitGuardian reports **1 secret across 11 commits** — the same single incident,
count risen only with the commit range. I swept both new commits' added lines
for credential-shaped assignments and `scheme://user:pass@host`: **no hits in
`e82e659` or `cf9e4c8`**. It still names only `a96f188`.

**One thing the lane does not run: `claims.py --check`.** It is not a workflow
step, it is not invoked from `demo.sh`, and `CLAIMS.md is current` appears **0
times** in the CI log for this SHA. I checked whether any artifact claims
otherwise — `COMMANDS.md:643` says "regenerate it … when a rule or a document
moves", the PR body lists `claims.py --check` as the *source of the 47 figure*,
and nothing anywhere says it runs in the lane. So the builder has not
over-claimed; but the brief I was given asserts it does, and it does not. See
**T-1**.

## 8a. Two things the audit invites a reader to check, checked

- **CLAIMS row 2** ("Nothing in this repository starts a container… A reader
  should verify that rather than take this sentence."). I did: every
  `docker compose` invocation in `scripts/`, `.github/workflows/` and
  `docs/evidence/compose-topology/` is `config` (8), `version` (5), or the
  strings `up`/`ps` appearing inside comments, violation-message text, echoed
  prose and transcripts. **No lane script or workflow step starts, runs, pulls
  or creates a container.** Row 2 holds.
- **`claims.py --check` catches a hand edit.** Changing `47 rows` to `48 rows`
  in CLAIMS.md gives exit 1, `CLAIMS.md is stale: re-run …`. So the
  "do not edit this file by hand" instruction is enforced locally.

---

# Findings — round 4

All five are **class (a)**: a claim about, or the gating of, a checker — each
could be corrected, or the rule removed with its claim, without touching the
topology. **None is class (b): nothing here is a defect in anything the three
VZ-ISSUE-002 acceptance bullets depend on**, which I re-derived independently at
this SHA with 0 violations.

```
FINDING T-1: claims.py --check does not run in the validate lane
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     .github/workflows/validate.yml (no step); docs/evidence/compose-topology/demo.sh (no call);
             docs/evidence/compose-topology/claims.py
  requirements: VZ-CI-002

Observed:
  `claims.py --check` is the only thing that keeps CLAIMS.md honest about its
  anchors and its own byte-identity. It is not a workflow step (the workflow is
  untouched by this PR), it is not invoked from `demo.sh` — the lane's last
  step — and `CLAIMS.md is current` appears **0 times** in the `validate` job
  log for this SHA (run 35582443280).

  No artifact over-claims: `COMMANDS.md:643` says "regenerate it … when a rule
  or a document moves", and the PR body lists `claims.py --check` as the source
  of the 47 figure, not as a gate. The brief I was given says it "runs in the
  lane"; it does not, and the chair should not rely on that sentence.

Failure:
  The remedy for the class that has held this PR three times is itself ungated.
  A later PR that reworks a checker and reworks a document can leave CLAIMS.md
  behind — stale anchors, a row whose rule no longer exists — and the lane stays
  green. Every other control added in this slice runs on every push; this one
  runs only when someone remembers.

Perspective:
  developer

Recommendation:
  One line, in the PR that is allowed to touch the workflow (this one was not):
  a `no claim is stale` step running
  `python3 docs/evidence/compose-topology/claims.py --check`. It needs no new
  dependency — it is the same interpreter the lane already pins — and it is a
  gate, not a report, so it belongs beside the other four checker steps rather
  than inside `demo.sh`.

Acceptance criteria:
  - `validate` fails when an anchor no longer resolves, when an anchor is
    ambiguous, or when CLAIMS.md is not byte-identical to the generator's
    output. All three already work locally; only the wiring is missing.
  - The step is added in a PR that does not also change what it audits, per the
    manifest rule this slice has respected throughout.

Tests:
  Already demonstrated locally: reworded anchor -> exit 2; duplicated anchor ->
  exit 2; hand-edited CLAIMS.md -> exit 1. The step would carry those into CI.

Cross-repo implications:
  core: none | user: none | search: none | meta: one workflow step.

Challenge:
  "The chair told this builder to add no new behaviour, and the workflow is
  owner-reviewed — so leaving it out was correct." Agreed, and that is why this
  is SHOULD and not higher, and why I am naming it as a follow-up rather than a
  defect in the slice. But a reader of the PR body's table sees
  `claims.py --check` in the right-hand column beside figures every other row
  gets from a lane step, and will reasonably assume it runs.
```

```
FINDING T-2: --check validates anchors and byte-identity, not the claim text or the cited cases
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/evidence/compose-topology/claims.py resolve() and the CLAIMS table literals;
             docs/evidence/compose-topology/CLAIMS.md:3-7 (the header)
  requirements: VZ-CI-002

Observed:
  The positive mechanism works — I broke it two ways and it refused:

      anchor reworded away  -> exit 2 "the anchor '…' no longer appears in docs/META_REPO.md"
      anchor duplicated     -> exit 2 "appears 2 times … an audit row must name one sentence"
      CLAIMS.md hand-edited -> exit 1 "CLAIMS.md is stale"

  Two things are not tied to anything:

  1. THE CLAIM TEXT. I prefixed `Only ONE shape ` to the sentence row 1 audits,
     inverting it — row 1 claims *"Every declared shape is rendered on every
     run"* — and the anchor substring still resolved uniquely:

         ./docs/evidence/compose-topology/claims.py --check   ->  exit 0

  2. THE "RED WHEN" CELL. I rewired row 7's cases from `26, 26a…26e` to
     `1, 2, 3` — the port cases, which test something unrelated. Regeneration
     exit 0, `--check` exit 0. The generator does compute a rule->case map from
     `demo.sh`, but it feeds the "16 of 42" table, not the per-row cells.

  The header reads: "Every line number below is resolved against the live file
  at generation time, and the generator REFUSES to write anything if an anchor
  no longer resolves uniquely — so **a stale row is a failed run**, not a
  quietly wrong number." The tail scopes it to numbers; the clause a reader
  takes away is about rows, and a row can be stale in the two ways above.

Failure:
  The artifact built to stop sentences outrunning their controls describes its
  own control slightly more strongly than it is. Concretely: an author who
  softens a sentence in META_REPO.md while leaving the anchor phrase intact
  leaves CLAIMS.md asserting the old, stronger claim, and every check passes.
  That is the same shape as S-1 and S-2 one level up.

Perspective:
  developer

Recommendation:
  Cheapest honest fix is wording: "the generator refuses to write if an anchor
  is missing or ambiguous, so a LINE NUMBER is never quietly wrong. The claim
  text and the cited cases are written by hand and are not machine-checked —
  read the anchored sentence."
  If it should be mechanical instead: store a hash of the anchored LINE beside
  each row and fail when it changes, and validate each Red-when cell's case ids
  against the ids `demonstrated_rules()` already parses out of `demo.sh`.

Acceptance criteria:
  - Editing an audited sentence without removing its anchor either fails
    `--check` or is explicitly out of scope in the header.
  - A Red-when cell naming a case id that does not exist in `demo.sh` fails.
  - The three refusals I measured still work.

Tests:
  Both mutations above, in the transcript the way `local-run.txt` records the
  other measurements.

Cross-repo implications:
  core: none | user: none | search: none | meta: claims.py and one paragraph.

Challenge:
  "The header says 'line number' twice; you are reading it uncharitably." Fair,
  and it is why this is SHOULD. But this PR's whole thesis is that a reader
  takes the strong clause, and "a stale row is a failed run" is the strong
  clause in a file whose subject is exactly that failure.
```

```
FINDING T-3: the rule tables describe the 16 undemonstrated rule ids in the same voice as the demonstrated ones
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/quality/COMMANDS.md:363, :366, :368, :369, :370 (the rule tables);
             the admission itself is at COMMANDS.md:636-644 and CLAIMS.md row 28
  requirements: VZ-CI-002

Observed:
  The admission is accurate and computed, not hand-counted. But it lives in §8
  prose and in CLAIMS.md, while the tables a reader actually consults mark
  nothing. The ten topology rule ids with no demonstration, and the line that
  still reads as a control:

    :368  docker-socket, privileged, host-network, no-new-privileges
    :369  missing-service, unexpected-service
    :370  dev-mode-in-production, dev-hatch-in-production
    :363  oneshot-restart
    :366  missing-build

  None is false — I have seen `host-network` fire myself, with my own mutation,
  in round 1. The issue is that the table does not distinguish "refuses X,
  demonstrated" from "refuses X, code review only".

Failure:
  A reader deciding what a green lane proves reads the table, not §8.

Perspective:
  developer

Recommendation:
  A dagger and one legend line: mark the 16 ids in the tables and footnote
  "† no red demonstration; asserted by code review — see CLAIMS.md". The
  generator already computes the set, so the marks can be generated rather than
  maintained.

Acceptance criteria:
  - Every rule id in COMMANDS.md's tables carries its demonstrated/undemonstrated
    status.
  - The marks come from `demonstrated_rules()`, not a hand list.

Tests:
  `claims.py` already computes the set; the check is that the two agree.

Cross-repo implications:
  core: none | user: none | search: none | meta: docs.

Challenge:
  "§8 says it plainly and CLAIMS.md lists them." True — this is a NIT about
  where the fact is published, not whether it is.
```

```
FINDING T-4: one entry of the deferred pipe-race list is misdescribed
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/evidence/compose-topology/CLAIMS.md ("Known weak spots"), and the
             same list in the PR body; the real file is scripts/ci-required-select.sh:56
  requirements: VZ-CI-002

Observed:
  The follow-up list names `scripts/ci-required-guard.sh` lines 80, 249, 348,
  423, 440 — **exactly the five `printf … | grep -q` sites I find** — and
  `scripts/ci-required-select.sh:56`. That line is

      status="$(printf '%s' "$line" | cut -f2)"

  `grep -c '| grep -q' scripts/ci-required-select.sh` is **0**. A `| cut` inside
  a command substitution is not the `grep -q` early-exit race: `cut` consumes
  its whole input, so `printf` never takes EPIPE.

Failure:
  Trivial, but the list is the handover to whoever fixes the siblings, and one
  of its six entries points at a construct that is not the bug.

Perspective:
  developer

Recommendation:
  Drop the `ci-required-select.sh:56` entry, or re-describe it if a different
  concern was meant.

Acceptance criteria:
  - Every line the list names contains a `printf … | grep -q` under pipefail.

Tests:
  `grep -n '| *grep -q' scripts/*.sh`.

Cross-repo implications:
  core: none | user: none | search: none | meta: one list entry.

Challenge:
  "It is a follow-up list, not a control." Agreed — NIT.
```

```
FINDING T-5: four guarantee sentences inside CLAIMS.md's own declared scope have no row
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra (meta)
  files:     docs/quality/COMMANDS.md:437, :528-531, :534-536, :647;
             docs/evidence/compose-topology/claims.py (the CLAIMS table)
  requirements: VZ-CI-002

Observed:
  CLAIMS.md declares its surfaces, and `COMMANDS.md` §4–§8 is one of them.
  Sweeping that scope for guarantee words, excluding lines within +/-3 of an
  audited anchor, at least four sentences have no row:

    :437      "Every long-running service in a production shape declares [a mem_limit]"
    :528-531  a compose map that still sends a retired key "is a guaranteed boot refusal"
    :534-536  "Every alias carries an explicit `authorised` decision … printed on every green run"
    :647      "No condition in the harness reads its captured output through a pipe. Every one uses a here-string"

  I verified all four are TRUE: case 16 and my own 13-shape audit; 34 x
  `retired-key-delivered` plus core's `RetiredKeys` at `keys.go:91`; the
  `alias-floor` rule firing in both directions (measured at 9c4b5d3) and the
  ALIASES banner in this run; and `grep -c '| grep -q' demo.sh` = 0.

Failure:
  A completeness gap, not a false claim. But the table's value is that a
  reviewer can read it INSTEAD of re-deriving every guarantee, and four
  omissions inside its own declared scope means the table cannot yet be read
  that way. The sweep is mechanical and could be a check.

Perspective:
  developer

Recommendation:
  Add the four rows. Better: have `claims.py` run the sweep itself — the
  guarantee-word regex over the declared surfaces, minus the audited anchors —
  and fail when an unaudited sentence appears. That turns "we audited the
  claims" from a one-time effort into a property, which is what this slice is
  trying to establish.

Acceptance criteria:
  - The four sentences have rows, or are covered by an explicit exclusion the
    file names.
  - A new guarantee sentence added to an audited surface fails a check until it
    is audited or excluded.

Tests:
  The sweep itself; its red case is adding a guarantee sentence to
  `COMMANDS.md` §5 and seeing the generator refuse.

Cross-repo implications:
  core: none | user: none | search: none | meta: claims.py plus four rows.

Challenge:
  "All four are true, so nothing is wrong." Correct today. The finding is that
  nothing keeps it so, and the previous three rounds are the argument that
  'nothing keeps it so' is how this PR kept failing.
```

---

# Round-3 findings — disposition

| Round-3 finding | Severity | Status at `cf9e4c8` | Verified by |
|---|---|---|---|
| **S-1** `known-false-undisclosed` one-directional, four places said both | REQUIRED | **CLOSED** | both directions fire with **distinct rule ids** — `known-false-undisclosed` (either file) and `known-false-stale-disclosure` (list emptied). Marker-only limit conceded in three rows and the weak-spots section |
| **S-2** the gate rule tested for a mention; docs said "invoke" | REQUIRED | **CLOSED** | structural tokeniser; 15 of my attacks red, including a real mid-string newline, a directory named `pg_isready`, `env`/`sh -c`, a leading assignment, `exec`, full-width `;` and NBSP. The 4 greens are correct behaviour or the stated residual, and the docs state exactly the two limits |
| **S-3** path spellings missed; `unknown-script` unreachable | SHOULD | **CLOSED** | `./`, `scripts/`, `deploy/`, backticked path all red; `rotate-secrets.sh` red as `unknown-script`; marked path form and an existing script stay green |
| **S-4** pipe race in a required lane | SHOULD | **CLOSED pending the loop** | 0 `\| grep -q` in `demo.sh`; siblings correctly outside the diff (one entry misdescribed, T-4). Stability loop in §9 |
| **S-5** drift compared names only | SHOULD | **CLOSED** | secret-flag comparison fires (exit 1); per-component UNCHECKED reported; BLOCKED exit 2 unchanged |
| **S-6** unflagged credential written raw | NIT | **STATED, not fixed** — as agreed | reproduced: 47 occurrences, every lane exit 0; said in CLAIMS rows 17/44 and COMMANDS.md:332-339 |
| **S-7** stale PR-body counts and a repeated false claim | NIT | **CLOSED** | every figure matches my measurements (13 / 27 / 11 / 4 / 95 / 50 / 1 / 1 / 47); the case count now comes from the harness (41 `case_header` + 9 parameterised call sites = 50), and the body records the three-times-wrong history |

Infrastructure NEW-2 (the stale-disclosure direction) and NEW-3 (README ports,
`/readyz` without `-f` in both files, the 4092/4096 sentence) both verified.


## 9. S-4 — demo.sh stability loop, back to back on a quiescent tree

Method: an isolated clone at `cf9e4c8` that nothing else touches while it runs;
`bash docs/evidence/compose-topology/demo.sh` back to back; after each run the
RESULT line, the exit code, the count of `Broken pipe` in that run's output, and
`git status --porcelain` (excluding `build/`) are recorded. Each line below was
appended as its run landed, so a restart cannot lose completed runs.

Runs 1–3 are from the pre-restart clone (`…/scratchpad/vzver4-qi87vDoa/loop`,
since removed with the session). Their RESULT lines are reproduced from my tool
output in that session; the per-run output files did not survive the restart.
Runs 4–10 are from a fresh clone made after the restart.

| Run | Clone | Exit | RESULT | Broken pipe | Tree dirty |
|---:|---|---:|---|---:|---:|
| 1 | pre-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 2 | pre-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 3 | pre-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 4 | post-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 5 | post-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 6 | post-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 7 | post-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 8 | post-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 9 | post-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |
| 10 | post-restart | 0 | `95 assertion(s) passed, 0 failed, across 50 case(s)` | 0 | 0 |

**10 of 10 runs clean.** Every run: exit 0, `95 assertion(s) passed, 0 failed,
across 50 case(s)`, zero `Broken pipe`, the tree byte-identical afterwards. For
runs 4–10, where the per-run files exist, I also checked each one: 0 `FAIL`
lines, 50 `CASE` headers printed. That is the same RESULT line CI printed for
this SHA (run `35582443280`). With `grep -c '| grep -q' demo.sh` = 0, the race is
gone by construction, and the loop shows it is gone in practice. **S-4 is CLOSED.**

At 9c4b5d3 the same harness gave me 72/73 once, with a
`printf: write error: Broken pipe` and the contradictory
`FAIL: expected exit 1 …, got 1`. Nothing like that appeared in any of these ten
runs.

## Verdict

Head still `cf9e4c86b077335fcad8cf8050c8fe57a50431c2` when the loop finished;
`validate` and `ci-required` success on it; GitGuardian red for `a96f188` alone
and not in the manifest.

**Every blocking finding from 9c4b5d3 is closed, and my own mutations confirm
it:** S-1 (both directions, distinct rule ids), S-2 (a structural tokeniser
that survived 15 attacks; the greens are correct behaviour or the documented
`pg_isready --version` residual), S-3, S-4 (10/10), S-5, S-7. S-6 is stated
rather than fixed, as agreed. **All three VZ-ISSUE-002 acceptance bullets are
MET** from my own renderer over 13 shapes. The rendered compose models are
identical to `9c4b5d3` apart from the random bundle-tree name. Scope is clean.
The CI artifact for this SHA holds no secret value.

**On T-1…T-5 and the standing "no false guarantee merges" ruling:** all five are
class (a). None is a defect in anything the acceptance bullets depend on, and
**I consider none of them blocking.**

- **T-2 is the only one that touches the ruling.** CLAIMS.md's header says "a
  stale row is a failed run". The generator does refuse a missing anchor, an
  ambiguous anchor and a hand edit; I measured all three. It does not tie the
  claim text or the Red-when cell to the source. I rule it non-blocking because
  the sentence is about the audit file, not about a control an operator or the
  topology relies on. Its own tail also scopes it to line numbers ("not a
  quietly wrong number"). If the chair reads it as a false guarantee under the
  ruling, the remedy is one sentence of wording: *"a line number is never
  quietly wrong; the claim text and the cited cases are hand-written — read the
  anchored sentence."* No code change is needed to make it true.
- **T-1 is not a false claim by the builder.** No artifact says
  `claims.py --check` runs in the lane; only the brief I was given did. It
  should become a lane step in a PR allowed to touch the workflow.
- **T-3, T-4 and T-5 are completeness or publication gaps.** Every sentence
  involved is true, and I verified each one.

FINAL VERDICT: PASS — SHA cf9e4c86b077335fcad8cf8050c8fe57a50431c2

---

# Re-confirmation of docs delta at ddec39c

Verifier: a fresh independent verifier (did not write the code and did not produce the
`cf9e4c8` verdict above). Date: 2026-09-23. Scope: the delta `cf9e4c8..ddec39c` only,
plus the local lane and CI on `ddec39c`.

## Head and ancestry

| When | `gh pr view 4 --json headRefOid` | `git ls-remote … refs/heads/feat/m0-compose-topology` |
|---|---|---|
| start | `ddec39c34fe92857b03c40a21b9645dec96c50c5` | `ddec39c34fe92857b03c40a21b9645dec96c50c5` |
| end (2026-09-23T17:09:59Z) | `ddec39c34fe92857b03c40a21b9645dec96c50c5` (OPEN, not merged) | `ddec39c34fe92857b03c40a21b9645dec96c50c5` |

- `git merge-base --is-ancestor cf9e4c8 ddec39c` → true; `git rev-list --parents -n1 ddec39c` →
  single parent `cf9e4c86b077335fcad8cf8050c8fe57a50431c2`. A one-commit fast-forward.
- `git diff --stat cf9e4c8 ddec39c`:
  `docs/evidence/compose-topology/CLAIMS.md | 10 +++++-----`,
  `docs/evidence/compose-topology/claims.py | 10 +++++-----`; 2 files, 10 insertions, 10 deletions.
  Nothing else changed.
- AST comparison (Python 3.9.6 `ast`, every `str` constant replaced by one placeholder,
  `include_attributes=False`): **identical** (37641-char dump on both sides). Without blanking the
  raw ASTs differ, as they should. The five `w("…")` header lines became four text lines plus one
  extra `w("")`, so the call count is unchanged; code is unchanged apart from string literals.

## Environment

Own clone: `mktemp -d …/scratchpad/vzv-vizra-pr4-XXXXXX` → `vzv-vizra-pr4-CAUCD1/repo`, checked
out detached at `ddec39c`. macOS arm64, Python 3.9.6, PyYAML 6.0.3, Docker 29.8.0, Compose 5.5.1,
git 2.50.1. The builder's worktree was not used.

## Local lane (docs/quality/COMMANDS.md §1–§8), run from the clone root

| Command | Exit | Result line |
|---|---:|---|
| `python3 docs/evidence/compose-topology/claims.py --check` | 0 | `CLAIMS.md is current (47 audited claims)` |
| `python3 docs/evidence/compose-topology/claims.py` (write) then `git diff --exit-code` | 0 / 0 | CLAIMS.md sha256 `a08e8384…a344d` before and after: **byte-identical regeneration** |
| `./scripts/check-generated-ledger.sh` | 0 | `OK 191 requirements; core=141`; byte-for-byte in UTF-8 and C/POSIX locales |
| `./scripts/check-quality-json.py` | 0 | 4 JSON files; 191 ids; 287 references, 204 distinct, 14 documents, all resolve |
| `./scripts/check-doc-links.py` | 0 | 95 markdown files; compose comments 6 paths / 8 files resolve (2 allow-listed) |
| `./scripts/ci-required-guard.sh` | 0 | 1 required lane; fixtures 6/6, 7/7, 10/10 at floor |
| `./scripts/compose-render.py --all --out build/compose-models` | 0 | 13 shapes rendered |
| `./scripts/check-compose-topology.py build/compose-models` | 0 | `13 shape(s) … 27 rules, 0 violations; 2 known-false probe(s)` |
| `./scripts/check-config-coverage.py build/compose-models` | 0 | `34 component keys … 58 template keys, 58 interpolated variables, 13 shapes; 1 alias; 1 retired key refused; 0 violations` |
| `./scripts/check-template-claims.py` | 0 | `10 operator-facing file(s), 16 … reference(s) … 0 violations` |
| `bash docs/evidence/compose-topology/demo.sh` | 0 | `RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`; 0 `FAIL` lines; 0 `Broken pipe`; `tree is clean`; 355 s |

No skips. `git status --porcelain` (excluding `build/`) empty after every step.

## Mutations on the changed sentences (each restored; `--check` exit 0 and a clean tree after)

| # | Mutation | Observed | Sentence it tests |
|---|---|---|---|
| M1 | append one line to CLAIMS.md | `--check` exit **1**, `CLAIMS.md is stale` | "`claims.py --check` fails on a hand edit" — **true** |
| M2 | insert one line at the top of `docs/quality/COMMANDS.md` (14 rows cite it) | `--check` exit **1** | line numbers in the `Where` column are resolved — **true when the generator runs** |
| M3 | replace CLAIMS row 1's anchor (`is rendered on every run and asserted`, `docs/META_REPO.md`) | write exit **2**, `UNEVALUABLE … no longer appears`; CLAIMS.md sha256 unchanged | "REFUSES to write anything if an anchor is missing" — **true** |
| M4 | append a second copy of the same anchor | write exit **2**, `appears 2 times … (lines [85, 353])` | "… or appears more than once" — **true** |
| M5 | insert one comment line after the shebang of `scripts/ci-required-guard.sh` and `scripts/ci-required-select.sh` | `--check` exit **0**, `CLAIMS.md is current`; CLAIMS.md:157–158 still say "lines 80, 249, 348, 423, 440" and "line 56"; guard line 80 is now `[ -z "$lane" ] && continue`, select line 56 is now blank | "every line number is resolved … a line number is **never quietly wrong**" — **false** for these six numbers (F-1) |

At `ddec39c` without mutation the six hand-written numbers are correct today: guard lines
80, 249, 348, 423, 440 are the `printf '%s\n' … | grep -q…` lines, and select line 56 is
`printf '%s\n' "$rows" | head -n 1`.

Other changed sentences, checked against code and workflow:

- "the claim text, the kind and the cited cases in each row are hand-written" — true: they are
  literals in `CLAIMS` (`claims.py`), emitted unchanged by `build()`.
- "The rule-id table further down is the exception: it is computed from `demo.sh` and each
  checker's `RULES`" — true: `undemo`/`total` come from `demonstrated_rules()` (demo.sh scan) and
  `declared_rules()` (the `RULES = frozenset({…})` of the three checkers).
- "It is **not** a step of the `validate` CI lane, so CI does not notice a stale CLAIMS.md" — true:
  `git grep claims.py ddec39c` finds no reference in `.github/workflows/` (validate.yml line 226 is
  `check-template-claims.py`, a different script), none in `demo.sh`, none in `scripts/`.
- "`claims.py --check` is run by hand as part of the local lane (recorded in `local-run.txt`)" —
  recorded: yes (`local-run.txt:107`, exit 0, 47 claims, at code commit `e82e659e`). "Part of the
  local lane" is looser: the transcript header says it was "generated by the 8 required local lane
  commands in docs/quality/COMMANDS.md", and `claims.py --check` is not one of the eight — COMMANDS.md
  §8 mentions only the write form. (F-2, NIT.)

## CI on ddec39c (`gh api repos/yegamble/vizra/commits/ddec39c/check-runs`)

| Check run | Status | Conclusion | Job / run |
|---|---|---|---|
| `validate` | completed | **success** | job 107288215713, run 35826344782 (attempt 3), 16:59:14–17:05:39Z |
| `ci-required` | completed | **success** | job 107288209911, run 35826344784 (attempt 2), 16:59:49–17:05:42Z |
| `GitGuardian Security Checks` | completed | failure | 107068799057, 06:21Z |

- `ci-required` log: manifest `.github/required-checks.txt` at `ddec39c` lists exactly `validate`;
  the guard printed `required checks: - validate`, polled `validate: in_progress` until
  `validate: success`, then `ci-required: every required check succeeded on ddec39c34fe9…`. The one
  listed lane actually ran and succeeded on this SHA — no listed-but-unexecuted lane.
- `validate` log: PR head `ddec39c…`, base `6b8158c3280ecd17a32efbb009ab06d04da42260` (= `origin/main`
  when I cloned); topology `13 shape(s) … 27 rules, 0 violations`; coverage `… 0 violations`;
  template claims `0 violations`; `RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`.
  Same figures as my local run.
- GitGuardian: `1 secret uncovered` — incident 37486665, "Generic Password", commit
  `a96f18895f38594164bc216b2f9727d63a10ecf9`, `docs/evidence/compose-topology/demo.sh` line 546. That is
  the historical fake-marker commit; `demo.sh` is not in this delta and the check is not in the
  required manifest. Reported, not counted as a finding against this delta.

## Findings

```
FINDING F-1: "every line number is resolved … never quietly wrong" is false for six line numbers in the same file
Severity:    REQUIRED (merge-blocking only under the chair's "no false guarantee merges" ruling; not a product defect)
Confidence:  high

Affected:
  repo:      vizra
  files:     docs/evidence/compose-topology/claims.py:558, CLAIMS.md:4, CLAIMS.md:157-158,
             claims.py (the "Known weak spots" w() lines), PR #4 body ("The generator guarantees that a
             line number is never quietly wrong.")
  requirements: VZ-CI-002 (evidence discipline for this slice)

Observed:
  The new header (the whole point of ddec39c, "states only what claims.py enforces") says:
  "every line number is resolved against the live file at generation time … so **a line number is
  never quietly wrong**". CLAIMS.md:157-158 contain six line numbers that are hard-coded string
  literals in claims.py and are never resolved: `scripts/ci-required-guard.sh` (lines 80, 249, 348,
  423, 440) and `scripts/ci-required-select.sh` (line 56). The PR body goes further: "The generator
  guarantees that a line number is never quietly wrong."

Failure:
  Reproduction (in a clean clone at ddec39c):
    sed -i '' '1a\
    # x
    ' scripts/ci-required-guard.sh scripts/ci-required-select.sh
    python3 docs/evidence/compose-topology/claims.py --check   # exit 0, "CLAIMS.md is current"
    sed -n 157,158p docs/evidence/compose-topology/CLAIMS.md    # still "lines 80, 249, …" / "line 56"
    sed -n 80p scripts/ci-required-guard.sh                      # now `[ -z "$lane" ] && continue`
  Those scripts are exactly the ones the follow-up will edit, so the numbers will go quietly wrong
  with the generator and --check both green. It is the same class as the vizra-core #6 hold: a
  sentence that reads as exhaustive ("every", "never", "guarantees") while omitting a case.

Perspective:
  developer (the reviewer who follows a cited line number)

Recommendation:
  One of, in claims.py (then regenerate) and the PR body:
  (a) scope the sentence: "every line number in the Where column is resolved …; line numbers quoted
      in prose (Known weak spots) are hand-written and not checked"; or
  (b) drop the six numbers from the prose and cite the pattern instead; or
  (c) resolve them through anchors like the Where column.
  Change the PR body's "guarantees" sentence to match.

Acceptance criteria:
  After M5 above, either --check exits non-zero, or no sentence in CLAIMS.md / claims.py / the PR body
  says every line number in the file is resolved or can never be quietly wrong. claims.py AST unchanged
  modulo strings if (a) or (b).

Tests:
  M5 above, plus claims.py --check and a byte-identical regeneration.

Cross-repo implications:
  core: none | user: none | search: none | meta: CLAIMS.md header and PR body only

Challenge:
  The header also says CLAIMS.md is not checked in CI and that hand-written parts should be read at
  source, and the six numbers are correct today. The previous verifier ruled the predecessor sentence
  non-blocking because it concerns an audit file, not an operator control. If the chair applies that
  reading, F-1 is a NIT; I rate it REQUIRED only because this commit exists to make exactly this
  sentence exact, and the PR body now uses the word "guarantees".
```

```
FINDING F-2: two small non-exhaustive statements in the new header
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra
  files:     claims.py:559-560 → CLAIMS.md:5-6; docs/evidence/compose-topology/local-run.txt:1,107;
             docs/quality/COMMANDS.md §8
  requirements: VZ-CI-002

Observed:
  (1) "What it does NOT enforce: the claim text, the kind and the cited cases …" leaves out the
  "What it does NOT guarantee" column, which is also a hand-written literal (CLAIMS tuple field
  `limit`). (2) "run by hand as part of the local lane": it is recorded in local-run.txt:107, but that
  transcript describes itself as "the 8 required local lane commands in docs/quality/COMMANDS.md", and
  --check is not one of the eight; COMMANDS.md §8 documents only the write form.

Failure:
  A reader could take the limit column as checked, or look for --check in COMMANDS.md and not find it.

Recommendation:
  Add "and the 'does NOT guarantee' cell" to the list; add `claims.py --check` to COMMANDS.md §8 (or say
  "run by hand alongside the local lane").

Acceptance criteria / Tests:  text change; --check exit 0 after regeneration.

Cross-repo implications:  none

Challenge:
  "The rule-id table is the exception" already implies everything else is hand-written.
```

## Verdict

Everything the delta was supposed to be, it is: a one-commit fast-forward, two files, claims.py
unchanged apart from string literals (AST-identical), CLAIMS.md regenerated byte-for-byte, the whole
local lane green (`demo.sh` 95/0 across 50 cases, clean tree), and `validate` + `ci-required` green on
`ddec39c` with the manifest's only lane actually executed. Four of the five checkable claims in the
new header are true, and M1, M3 and M4 confirm the refusals.

The headline sentence is not. "Every line number is resolved … never quietly wrong", and the PR
body's "The generator guarantees that a line number is never quietly wrong", are false for six
hand-written line numbers in the same file, and M5 shows `--check` staying green while they point at
the wrong lines. Under the standing "no false guarantee merges" ruling I return FAIL. The fix is one
sentence of wording in claims.py plus regeneration, and one PR-body sentence. No code change is
needed and nothing else is outstanding from this delta. If the chair reads F-1 as a NIT, as the prior
verifier did for T-2, then everything else here would support PASS.

FINAL VERDICT: FAIL — SHA ddec39c34fe92857b03c40a21b9645dec96c50c5
