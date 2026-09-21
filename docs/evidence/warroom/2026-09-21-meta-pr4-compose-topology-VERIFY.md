# Independent verification — meta PR #4, VZ-ISSUE-002 (compose topology)

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
