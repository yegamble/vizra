# Verification commands — vizra META repo

The actual commands for this repository's required checks, and what each one
proves. AGENTS.md § Required workflow point 3 points here: *"Use actual commands
documented in docs/quality/COMMANDS.md once created. A missing command or
dependency is BLOCKED, never a pass."*

**This file lists only commands that exist in this repository and that were run
to produce the evidence cited below.** It does not list commands for
`vizra-core`, `vizra-user` or `vizra-search`: those are separate repositories
with their own contracts, they are gitignored checkouts here (docs/META_REPO.md
§1), and nothing in this file was run against them. Look in each component
repository's own `AGENTS.md` for its lanes.

## Prerequisites

| Requirement | Used for | Checked with |
|---|---|---|
| `python3` ≥ 3.9 | every check; the ledger generator | `python3 --version` |
| PyYAML | the workflow checkers parse YAML rather than grepping it | `python3 -c 'import yaml; print(yaml.__version__)'` |
| `git` | the generated-ledger diff | `git --version` |
| `bash` | the two shell guards, and the compose demonstration script | — |
| Docker Engine + Compose **>= 2.24.4** | rendering the compose shapes | `docker compose version --short` |

No database and no browser is required. The link checker deliberately performs
**no** network I/O, and **no compose command here pulls or builds an image**:
`docker compose config` resolves the model from the files and the environment
and never contacts a registry. The base images are pinned by digest in
`docker-compose.yml`, which a render reads as a string.

A missing or too-old Compose is **BLOCKED**, never a pass:
`scripts/compose-render.py` exits 2 on a version string it cannot parse and 1
below the floor, and it renders nothing in either case.

## What a green check covers, and which tree it covers

On `pull_request`, `actions/checkout` checks out `refs/pull/N/merge` — the PR
head **already merged into the current base** — so the lane validates the merge
result, not the head commit on its own. `ci-required`, however, is reported
against the **head** SHA, because that is what a status check attaches to.

The practical consequence: a green `ci-required` on a head SHA means "the merge
of that head into the base *as it stood when the lane ran*" was green. The base
branch moves — the war-room chair commits the board to it every tick — so the
tested tree can change while the head SHA does not, and a check that was green
can stop reflecting the current merge without the head moving. The `validate`
lane therefore prints the PR head SHA, the base SHA and `git rev-parse HEAD`
(the merge commit actually tested), each labelled, so no transcript can be read
as a claim about a tree it did not test. Re-run the lane if the base has moved
since and you need the guarantee to be current.

This is also how the first version of this file came to record a markdown-file
count that the head itself does not have: the count came from the merge tree.

CI pins the interpreter to **Python 3.12.14** (`actions/setup-python`, pinned by
commit SHA). PyYAML's availability depends on **which** interpreter runs:

- In `ci-required.yml` the first CI run used the runner's preinstalled
  **PyYAML 6.0.1** and the pinned `pyyaml==6.0.3` install did not execute.
- In `validate.yml` it did **not** resolve. The first run of the compose steps
  failed with `ModuleNotFoundError: No module named 'yaml'`, because
  `actions/setup-python` puts a *different* interpreter first on `PATH` and
  PyYAML is preinstalled on the system Python only. `validate.yml` now carries
  the same install-if-absent step, with the same pin.

Recorded because "pinned", "preinstalled" and "what actually ran" are three
different facts, and the first version of this paragraph got the third wrong.

`scripts/check-compose-topology.py` additionally treats PyYAML as optional and
says so on stderr: it uses YAML only to name the source file in a failure
message, and every rule it enforces reads the rendered JSON model. A missing
parser degrades an error message; it never decides whether the topology is
asserted.

The local transcripts below were produced on macOS with the system
**Python 3.9.6** and PyYAML 6.0.3. The CI transcripts in
`docs/evidence/meta-validate/ci-run-*.txt` are the Linux runs.

## The `validate` lane

`.github/workflows/validate.yml` runs these, in this order. Run them from the
repository root. Checks 1-3 are documentary; 4-8 are the compose topology added
by VZ-ISSUE-002.

### 1. The generated ledger matches its sources

```
./scripts/check-generated-ledger.sh
```

Re-runs the ledger generator and asserts `git diff --exit-code` over every file
it writes (today: `docs/quality/features.json`). Catches **both** a hand-edited
generated file and a generator source changed without regenerating — they are
indistinguishable in review and identical from this check's point of view.
Refuses to run against a dirty working tree, so a difference is never
misattributed.

It **deletes the declared files before regenerating**. A diff alone cannot tell
"rewrote it identically" from "wrote nothing", so a generator gutted to
`print("OK 191 requirements; core=141")` used to exit 0 here while the check
printed a reproduction claim that was false. With the files removed first, a
generator that writes nothing leaves a deletion, and each declared file must
then **exist, be non-empty and parse as JSON** before the diff runs.

A second check compares `git status --porcelain -- docs/quality` before and
after the run. Precisely what the pair detects:

- a **declared** file that this run did not write, and
- an **undeclared** file under `docs/quality/` that this run **created or
  changed**.

It is a change detector, not a set comparison: an undeclared generated file that
is already committed and that the run rewrites byte-identically moves nothing in
`git status` and is not reported. Nothing like that exists today — `build.py`
writes exactly one file — and adding a second output means editing `build.py`,
which is a CODEOWNERS path.

It then re-runs the generator once under
`LC_ALL=C LANG=POSIX PYTHONCOERCECLOCALE=0 PYTHONUTF8=0` and requires
byte-identical output. That is the environment in which the pre-fix generator
raises `UnicodeEncodeError: 'ascii' codec can't encode character '—'` and
leaves a truncated `features.json`; PEP 538's C-locale coercion is what
normally masks it, which is why both variables are needed to see it.

Last run: **exit 0**, `generated ledger reproduces byte-for-byte:
docs/quality/features.json (UTF-8 and C/POSIX locales)` (192 requirements,
core=142; 2026-09-23, after VZ-AUDIT-001 was added).

To regenerate after editing a generator source — and you must commit both:

```
(cd docs/evidence/ledger-generator && python3 build.py ../../quality/features.json)
```

Last run: **exit 0**, `OK 192 requirements; core=142` (2026-09-23).

### 2. Quality JSON parses and every requirement id resolves

```
./scripts/check-quality-json.py
```

Every `*.json` under `docs/quality/` parses, and every `VZ-…` id referenced by
`docs/MILESTONES.md` and `docs/issues/*.md` names a requirement in
`features.json`. `VZ-ISSUE-NNN` and `VZ-SLICE-NN` are separate namespaces,
allowlisted by name — and `VZ-ISSUE-NNN` is still resolved against a real
`docs/issues/VZ-ISSUE-NNN.md`, so the allowlist is not an escape hatch.

**Ranges and slash-lists are expanded and every member resolved.** The
milestone rows write `VZ-FOUND-001…008`, `VZ-CI-001/002/004` and
`VZ-MEDIA-002/005…010`; resolving only the leading id would validate one
requirement out of eight.

A continuation is read only when all three hold, and the run ends quietly at the
first that does not:

1. digits follow the separator (`…`, `...`, `–`, `—`, `/`) — so a
   sentence-ending `.` and a trailing path `/` end the run;
2. those digits are followed by neither a digit nor a hyphen — so
   `docs/evidence/VZ-FOUND-008/2026-09-21.md`, an ordinary evidence path here,
   is **not** read as a list. Without this rule the checker invented
   `VZ-FOUND-0008` and `VZ-FOUND-2026` and went red on a correct document;
3. the digits are the same width as the id they continue, and that width is one
   the ledger uses — **derived from `features.json`, not hard-coded**.

Ending the run is not an error: `VZ-FOUND-008` in a path is a correct reference
to one requirement and resolves as such. Only a reference read **as** a range
that cannot be made sense of — descending, or implausibly long — is a **named
failure**, never a silent skip.

Last run: **exit 0** — 4 JSON files parsed, 192 requirement ids in the ledger,
191 written references expanded to 287 ids (204 distinct) across 14 documents,
every one resolving.

### Scope of the id check, and what is deliberately excluded

| Path | Checked | Why |
|---|---|---|
| `docs/MILESTONES.md` | yes | schedules work; an id here is a commitment |
| `docs/issues/*.md` | yes | the slice definitions |
| `docs/plans/*.md` | **no** | plans legitimately PROPOSE ids that do not exist yet. Measured: the 13 slice plans are clean, but `docs/plans/WARROOM-BOARD.md` row 2b names four proposed ids (`VZ-SEC-SSR-001`, `VZ-SEC-HDR-001`, `VZ-SEC-SSR-002`, `VZ-SEC-SUPPLY-001`) whose purpose is to be evaluated and possibly added to the ledger. Gating this directory would make the lane red for proposing a requirement. |
| `docs/evidence/**` | **no** | a red/green transcript must write down the id it deliberately made dangle (`VZ-NOSUCH-999`, `VZ-ISSUE-404`, `VZ-FOUND-001…999`). Gating it would make every demonstration a lane failure. |

Both exclusions were measured, not assumed. If a plan or the board should be
gated later, the honest way in is a marker distinguishing "proposed" from
"referenced", not a wildcard exemption.

### 3. Relative documentation links resolve

```
./scripts/check-doc-links.py
```

Relative markdown links in `docs/**/*.md` and the root `*.md` resolve to a file
that exists. External URLs are recorded and **never fetched**. Fenced blocks and
inline code spans are stripped first.

Last run: **exit 0** — `relative links: none exist yet … (checked nothing);
6 external URL(s) recorded and not fetched`.

The markdown-file count the command prints is **deliberately not quoted here**.
It changes every time a document is added — this file's own first version
recorded 87 and was stale within the same commit that added it, because
COMMANDS.md joined the corpus it was counting. A number that goes stale on its
own is worse than no number in a file whose purpose is that recorded figures can
be trusted. Run the command for the current value.

That "checked nothing" is accurate and is printed on purpose: this repository
currently contains **zero** relative markdown links. Every link-shaped string in
`docs/` is either inside code (26 of them) or an external URL (6). The check is
proven by the controlled mutation in
`docs/evidence/meta-validate/demo-4-broken-relative-link.txt`, not by existing
content. The checker fails if it matches *no* link of any kind, so a regex that
silently stopped matching is red rather than green.

## The `ci-required` fan-in

```
./scripts/ci-required-guard.sh
```

Everything that can be checked about the gate from the checkout itself:
the floor (`validate` present and non-optional), bare job names, every required
check defined by a real job, `continue-on-error` refused wherever it appears
(parsed, not grepped), every action pinned to a 40-hex commit SHA, every
required lane triggered on `pull_request` with no base-branch filter, no shell
override at workflow, job or step level, no step-level `if:`, no self-hosted
runner, no reusable-workflow call, and all three checkers exercised against
their negative fixtures.

Last run: **exit 0** — 6 continue-on-error fixtures (floor 6), 7 pin/trigger
fixtures (floor 7), 10 lane-integrity fixtures (floor 10).

The three checkers it calls can also be run alone:

```
./scripts/check-workflows.py                                            # exit 0
./scripts/check-action-pins.py --required .github/required-checks.txt   # exit 0
./scripts/check-lane-integrity.py --required .github/required-checks.txt # exit 0
```

All three answer three ways, so "rejected" and "could not be evaluated" are
never confused: `0` clean, `1` VIOLATION, `2` UNEVALUABLE.

`check-lane-integrity.py` covers five ways to neuter a lane that
`continue-on-error` does not:

| Refused on a required lane | Why |
|---|---|
| `defaults.run.shell` (workflow or job) | the Actions analogue of `SHELL := /usr/bin/true` — every `run:` step becomes a no-op that reports success |
| a step-level `shell:` | the same rule with the key in a different place |
| a step-level `if:` | a skipped JOB is refused by the fan-in, but a skipped STEP leaves the job green. A constant false is refused by name; any other condition too, because nothing here can evaluate it and a step that might not run is not a gate |
| `runs-on` naming `self-hosted` | ADR-009 / Q-027 makes GitHub-hosted `ubuntu-24.04` the qualified target; a self-hosted runner is a machine this repository does not describe or control |
| a job-level `uses:` (reusable workflow) | the real steps would live where this checker cannot see them, and every rule above would be enforced against an empty job |

A **job-level `if:`** is deliberately not checked: the fan-in already refuses a
`skipped` conclusion, so a skipped job is visible as a skipped check-run. That
asymmetry is the whole reason the step case needs its own rule.

It also owns job existence, which was previously a grep over `*.yml` only and
would have reported a lane defined in a `.yaml` workflow as missing.

The aggregate's row-selection rules run outside Actions too, which is how they
can be demonstrated at all:

```
./scripts/ci-required-select.sh "$(grep -vE '^\s*(#|$)' .github/required-checks.txt)" < runs.tsv
```

Exit `0` every required check succeeded · `1` at least one did not · `2` at
least one is still pending or never ran. `runs.tsv` is name/status/conclusion/
started_at, as `.github/workflows/ci-required.yml` produces it from the
check-runs API.

### 4. Every declared compose shape renders

```
./scripts/compose-render.py --list
./scripts/compose-render.py --all --out build/compose-models
```

Renders every shape in `scripts/compose-shapes.json` — the topologies
`docs/META_REPO.md` §2 says Vizra supports; `--list` prints them — to one JSON model each, plus
`shapes.json` carrying the manifest and the interpolation variables Compose
reported. Before rendering anything it refuses a Compose below **2.24.4**
(Q-017), failing closed on an unparseable version — that path is `require_floor`
and is **not exercised by any demonstration**, because the harness runs on
whatever Compose the host has; read it as code that has been reviewed, not as a
control that has been seen to fire. It also validates any external DSN the chain
requires with a message that names the variable and **never echoes the value**,
which cases 10a and 10b do demonstrate, value check included.

`bundle-no-checkouts` is rendered from a temporary tree built by copying in only
what a deployment bundle ships — no `vizra-core`, `vizra-user` or `vizra-search`
directory, and no `docker-compose.override.yml` or `docker-compose.dev.yml`. It
is built by copying in rather than by trusting that the component directories
happen to be absent today.

**Redaction, and the two lists that make it provable.** Declared secret values
are redacted from every model *before it is written*, and the leak check runs on
the object being serialised — not on a copy.

- `redact_keys` drives the redaction: those values are replaced by key, and
  their exact strings are substituted wherever they appear inside another value.
  The substring pass is not belt-and-braces: `DATABASE_URL` is assembled from
  `POSTGRES_PASSWORD` in `docker-compose.yml`, so a by-key replacement alone
  would leave the password inside the DSN.
- `secret_keys` drives the leak check. It is a separate list, identical in
  content today, and the independence is the mechanism: deleting a key from
  `redact_keys` stops redacting its value and does **not** stop looking for it,
  so the renderer **fails and writes nothing** rather than producing a file that
  is less redacted than its own `secret_values_redacted: true` stamp claims.

This corrects an earlier version of this paragraph that described a control
which did not work. The renderer computed a redacted copy, validated that copy,
and then serialised the original — so `find_leaks` could never fire on the bytes
that were written, and ten of the twelve models in the CI artifact for
`69e197e` carried their placeholder values under a stamp saying otherwise. The
values were the obviously fake `ci-render-only-*`, so nothing real leaked; the
defect was in the control. Demonstrations 18a and 18b are what keep it working.

**What redaction covers, and what it does not.** Exactly two things are
redacted: a key some `env/registry/*.json` flags `"secret": true`, and a key
named in the manifest's explicit `redact_keys` / `secret_keys` (the composite
and non-component values — `DATABASE_URL`, `POSTGRES_PASSWORD`,
`CLICKHOUSE_PASSWORD`). **A key that is neither is written raw into the uploaded
artifact, and no lane goes red for it.**

That is measured, not theoretical. The verifier added `VIZRA_S3_ACCESS_ID` the
fully correct way — registered in `env/registry/core.json`, declared in the
template, delivered by compose — but without `"secret": true`, and its value
appeared 47 times across the 13 models with every lane exit 0. An AWS access key
id is a credential and `_ID` matches nothing, so `unclassified-secret-key`'s
suffix net (`_PASSWORD`, `_SECRET`, `_TOKEN`, `_KEY`) does not catch it either.
That net is deliberately **not** widened: one declared exception beats a matcher
nobody trusts, and the primary signal is meant to be the component's own flag.

So: **the component's `secret` flag is the control.** A component that declares
a credential without flagging it is a component-side bug this repository cannot
see, and the flag itself is compared against the component's source only by
`check-config-coverage.py --drift`, which needs the component checkouts and
**cannot run in CI**.

The models are uploaded as the `meta-validate-compose-models` artifact.

### 5. The rendered topology is closed, capped and pinned

```
./scripts/check-compose-topology.py build/compose-models
```

Every rule below is read from `docker compose config --format json` parsed
as JSON — never from the YAML sources, because what is reachable on a host is
decided by the merged model and a source file can look closed while an overlay
opens it. The only YAML parsing is the diagnostic that names *which file* to
edit after a rule has already failed.

| Rule | What it refuses |
|---|---|
| `never-published` | postgres, the cache, search, the one-shots, worker and every optional datastore publishing anything, in any shape |
| `port-not-allowed` / `public-bind` | a port the shape does not allow, or one facing the network without an explicit `"public": true` and a reason in the manifest |
| `edge-profile` | caddy outside the `edge` profile |
| `missing-restart` / `oneshot-restart` | a long-running service that would not survive a reboot; a one-shot that would loop |
| `missing-log-cap` | a service inheriting the daemon's unbounded json-file default |
| `missing-healthcheck` | a long-running service that cannot gate a `depends_on` |
| `production-build` / `missing-build` | a `build:` in a production shape; a developer shape that stopped building from the checkouts |
| `unpinned-image` | in a production shape: no image, no tag, or `:latest`; and no `@sha256:` on a third-party image |
| `docker-socket` / `privileged` / `host-network` / `no-new-privileges` | VZ-OPS-008 |
| `missing-service` / `unexpected-service` | a shape that lost a service it needs, or rendered one it forbids |
| `dev-mode-in-production` / `dev-hatch-in-production` | the developer override leaking into a production chain |
| `missing-mem-limit` | a long-running production service with no cgroup cap, so a burst is contained by the OOM killer's badness score instead — which picks PostgreSQL |
| `probe-gates-readiness` | a `depends_on: service_healthy` edge onto a probe **declared** known-false: a gate that cannot go red is worse than no gate. **Scope:** it cannot tell a real probe from a fake one nobody declared |
| `gated-probe-unrecognised` | the converse — a `service_healthy` target that is not in `gated_probes`, or whose **rendered** probe does not run the declared command *as its own command*. See the paragraph below for exactly what that means and what it still cannot show |
| `unclassified-secret-key` | a registry key flagged `"secret": true` that is not in `redact_keys`, or a template key *named* like a secret that is neither. The renderer derives its redaction set from the same flag, so the value is never written — this makes the author classify it where a reader will look |
| `stale-known-false-probe` | a known-false declaration matching no rendered service, so the list cannot rot into permanent cover |
| `postgres-shm-floor` | postgres left on Docker's 64 MiB `/dev/shm`, which starts a cluster fine and fails parallel plans months later |
| `known-false-undisclosed` | a known-false probe declared while the operator-facing disclosure is missing from a file that must carry it |
| `known-false-stale-disclosure` | the other direction: `known_false_probes` emptied while a file still carries the disclosure, which would leave the template telling an operator to ignore a `healthy` column that has become trustworthy. The two rules together are why the list and the paragraphs are deleted in the same change — before the closing round only the first existed, and three documents said otherwise |
| `profile-not-enumerated` | a `profiles:` name no shape renders. Everything else here reads a rendered model, so an unrendered profile is an **unasserted** one — this is the rule that makes "in any shape" mean "in any configuration" |

`missing-healthcheck` treats four states explicitly — absent, disabled,
known-false, real — in one function rather than two overlapping conditionals.
`test: ["NONE"]` and `test: NONE` are Docker's spellings of *disabled*; the
neighbouring `disable: true` was already caught, and a rule that catches one
spelling and not the other is one an author can pass by accident.

`unpinned-image` splits by origin: a **release image** (`migrate`, `api`,
`worker`, `frontend`, `search`) may carry a non-empty, non-`latest` tag, because
that is what `releases/<tag>.json` names. Everything else is third-party and
must carry an `@sha256:` digest — ADR-001 pins PostgreSQL 18 and Valkey 9.1.x by
digest, and a bare `postgres:18` is a moving target that makes two operators on
the same release record run different builds. A service absent from
`release_image_services` gets the strict branch, so the safe default is a digest.

The port allowlist is keyed on `<published>/<protocol>`. A bare integer in the
manifest means `tcp`; `ipfs` names 4001 on both. Before that it was keyed on the
number alone, so an entry reading "may answer on 8080" also permitted 8080/udp.

**`gated-probe-unrecognised`: what "run the declared command" means, and what it
does not.** The check is structural and reads the **rendered** probe, which is
why the real one survives — `pg_isready -U "${POSTGRES_USER:-vizra}" …` has
already become `pg_isready -U "vizra" …` by the time the rule sees it.

- `["CMD", argv…]` — `basename(argv[0])` must *be* the declared command.
  `["CMD","echo","pg_isready"]` runs `echo`; naming the command in an argument
  is not invoking it.
- `["CMD-SHELL", s]` — `s` must contain none of `;` `|` `&` `#` `` ` `` `$(`
  `<` `>` or a newline, and its first word must be the declared command. That is
  a refusal list, not a shell parser: a gated probe has no business carrying a
  pipeline, a comment, a redirection, a substitution or a second statement, and
  refusing all of them is decidable from the string.
- anything else — a bare string that survived rendering, `["NONE"]`, no
  healthcheck at all — is refused rather than assumed to probe something.

Red, each demonstrated by rule id: `["CMD","true"]`, `["NONE"]`,
`pg_isready -U vizra || true`, `true # pg_isready`,
`sh -c 'exit 0; pg_isready'`, `echo pg_isready`.

**What it still cannot show.** That the command can exit **non-zero** —
`["CMD-SHELL","pg_isready --version"]` passes this check and succeeds whatever
PostgreSQL is doing — or that a binary with the right name is the real one
rather than a wrapper earlier on `PATH`. Neither is decidable from a rendered
model; both need a running container, which is VZ-ISSUE-004's boot lane. What
the rule buys is a price change: killing a readiness gate now costs a change to
the image, not one line of YAML that still mentions the right word. An earlier
version of this rule was a **substring test** over the joined command line and
two documents called it an invocation check; all four bypasses above passed it.

**What this does NOT prove.** It proves what the *model* declares. It has never
started a container, so it does not prove a service is healthy, that a probe
answers, that a port is genuinely closed on a running host, or that the IPFS
swarm port is firewalled. Those belong to the `boot` lane (VZ-ISSUE-004), which
does not exist.

### 5a. Capacity note — what the memory caps are, and what they are not

Every long-running service in a production shape declares
`mem_limit: ${VIZRA_*_MEM_LIMIT:-default}`, asserted by `missing-mem-limit`.

| Service | Default cap | Why |
|---|---:|---|
| `postgres` | 768m | the service we most want the OOM killer *not* to choose. PostgreSQL 18's `shared_buffers` defaults to 128 MB and no tuning knobs are set (VZ-OPS-007 adds them when it has measured a budget); the cap sits well above realistic use so it contains a pathology without clipping normal work |
| `redis` | 384m | `VALKEY_MAXMEMORY` defaults to 256mb; the rest is fragmentation and copy-on-write headroom. Raise both together or the cap fights the eviction policy |
| `api` | 768m | no pixel decode ever happens in the API process (ADR-002, Q-034), so this is request handling, pools and Go runtime overhead |
| `worker` | 1500m | the largest cap and the one doing the real containment: the only process that runs libvips, peaking on a 12 MP JPEG derivative set. Sized for the shipped `VIZRA_WORKER_CONCURRENCY=2` |
| `frontend` | 512m | Next.js standalone server |
| `caddy` | 160m | the one container whose death is **total site downtime**, and it was the tightest cap in the stack at 96m. Caddy idles at 25-40 MiB but reaches 80-150 MiB with HTTP/2, TLS session state and a few hundred concurrent connections; saving 64 MiB on a 4 GB host is not worth an OOM of the edge |
| `migrate` | 256m | a one-shot; exempt from the rule, capped anyway |
| `search` | 256m | a static Go binary on `scratch` owning no index at M0; rises with VZ-SEARCH-001 |
| `clickhouse` | 1g | **not sized for the floor host** — enabling `analytics` on 4 GB is not a supported shape |
| `ipfs` | 768m | likewise optional |

**The default-shape caps sum to 4092 MiB on a 4096 MiB host. The
*oversubscription* is deliberate; landing 4 MiB under physical RAM is a
coincidence and not the number that matters** — realistic concurrent peak on the
default shape is roughly **2.3 GB** (postgres ~250, the cache ~320 at its 256m
`maxmemory` plus fragmentation, api 100–200, frontend 150–250, caddy 30–60,
worker 800–1200 at concurrency 2 during an AVIF encode), against ~3500 MiB usable
after Ubuntu 24.04 and dockerd. Sizing a larger host means scaling the *peak*,
not the sum. (Plus `migrate` 256m transiently during a deploy.)
They are caps on *peak*, not reservations: nothing is set aside,
and these services do not peak together. The job they do is containment. Without
a cgroup limit anywhere, a burst of concurrent libvips decodes exhausts RAM and
the kernel OOM killer chooses by badness score — which on a Docker host is
routinely PostgreSQL, the largest resident process. The operator's symptom is
then not "uploads are slow" but PostgreSQL killed mid-write and crash recovery on
restart, for reasons unrelated to the upload, with `restart: unless-stopped`
cycling it. **A limit that OOM-kills the worker is recoverable; one that
OOM-kills PostgreSQL is not.**

These numbers are sized for the **shipped** `VIZRA_WORKER_CONCURRENCY=2`. On the
2 vCPU / 4 GB floor host run 1 — the caps still hold, with more headroom — and
use 4 from 8 GB up, raising `VIZRA_WORKER_MEM_LIMIT` with it. No two files may
state a different sizing assumption for the same default; an earlier version of
this note and the template disagreed, which is the very defect the caps were
added for.

**What happens when a cap IS reached**, which matters more than why it was
chosen:

- **worker** — the intended victim. Killed inside its own cgroup; the job lease
  is swept and the job retried (ADR-004). Recoverable by design.
- **postgres** — the cgroup OOM killer kills a backend, and the postmaster
  treats that as a crash: it terminates every backend and runs **crash
  recovery**. That is the outcome the caps exist to avoid, now merely much less
  likely rather than impossible. So **raise this cap alongside any tuning
  change** — `max_connections`, `work_mem`, `shared_buffers`. An operator who
  raises those without raising the cap walks straight into it.
- **caddy** — total downtime, which is why it is no longer the tightest cap.

**The caps assume a host with no swap.** `mem_limit` without `memswap_limit`
leaves swap unbounded, so on a host that HAS swap the worker thrashes before it
is killed and a 2 vCPU box becomes unresponsive — worse than the clean kill.
Most VPS images ship swapless, which is why this is a sentence rather than a
mechanism; if you add swap, add `memswap_limit` with it.

**`/dev/shm` is charged to the postgres cap** under cgroup v2, so
`VIZRA_POSTGRES_SHM_SIZE` (256m) shares the 768m limit. That is fine — dynamic
shared memory is transient and bounded by the parallel-worker settings — but it
is the kind of thing that should be stated rather than discovered. The setting
exists because Docker's 64 MiB default is enough to start a cluster and not
enough to run a parallel query, so it fails months after install with
`could not resize shared memory segment … No space left on device` on a host
with gigabytes free. `postgres-shm-floor` asserts it from the rendered model.

Precedent: Vidra's `docker-compose.prod.yml` sets `cpus`/`mem_limit` on api,
worker and ipfs. It was read for **shape** — the `${…:-default}` indirection so
a larger host raises a cap without editing a tracked file — and not for values,
which are sized there for a much larger machine. These numbers are VZ-OPS-007's
starting budget, not a measurement; nothing here has been benchmarked, and the
first boot-lane run on the reference host is what calibrates them.

### 6. Configuration-key coverage, in both directions

```
./scripts/check-config-coverage.py build/compose-models
./scripts/check-config-coverage.py --drift        # needs the component checkouts
```

Compares `env/registry/<component>.json` — a snapshot of each component's
declared keys at a named component commit — against the rendered `environment:`
map of every service, and `env/*.env.example` against the variables Compose says
it interpolates. Fails on a key a component reads that nothing delivers, on a
template key nothing consumes, on api and worker carrying different key sets
(they run the same binary), on a development escape hatch in the production
template, and on an undeclared alias.

It also refuses a **retired** key (`retired-key-delivered`). That is a different
failure from an unknown one: an unknown key is merely useless, while `vizra-core`
refuses a retired name in production *on presence*, so a compose map that still
sends it is a guaranteed boot refusal — naming a variable that appears nowhere in
the operator's env file, because compose injects it.

Every **alias** carries an explicit `authorised` decision with its authority and
its removal condition; an alias without one is a violation, and each is printed
on every green run. One alias remains (`VIZRA_PUBLIC_ORIGIN`, which `vizra-user`
reads as `PUBLIC_ORIGIN`); the `SEARCH_HMAC_KEY` alias was **deleted** when
`vizra-core` 4a80a1e adopted the contract's spelling, and the floor moved 2 → 1
in the same edit — a resolved alias left in the table is a compromise that reads
as current. An alias is a standing compromise — a place an operator can
believe they configured something they did not — so it has to be looked at
rather than filed once.

**What `--drift` compares.** Exactly the two fields of a `keys[]` entry that any
checker consumes, because a field nothing reads is a field nothing can be wrong
about:

- **`name`**, by a coarse quoted-literal scan over the component's declared
  `source_files`. It over-reports rather than under-reports.
- **`secret`**, against the component's own source where the component states it
  in a machine-readable form. `vizra-core`'s `internal/config/keys.go` writes
  `{Name: "…", Secret: true, …}`, so all 22 of its snapshot keys are compared.
  `vizra-search` and `vizra-user` carry **no** such marker, so their flags are
  reported **UNCHECKED on every run** — named, with the count of keys they flag
  — rather than rounded up into "matches".

The flag is on that list because it is load-bearing: `scripts/compose-render.py`
derives its redaction set from it, so a snapshot that quietly drops a
`"secret": true` narrows what is kept out of the uploaded artifact. Until the
closing round nothing compared it, and deleting the flag from
`VIZRA_SESSION_SECRET` still reported *every snapshot matches its component
source*.

`required`, `default`, `delivered_by` and `reason` are documentation for a human
reader. Nothing reads them, so nothing validates them and this check does not
pretend to.

**What a green result does NOT prove.** It proves the topology is consistent
with the snapshots. It does **not** prove the snapshots are current: this
repository's CI has no token to check out a private sibling repository, so
`--drift` — **including the secret-flag comparison above** — **cannot run in CI
at all** and reports BLOCKED, exit 2, when a checkout is absent. Drift is a
local control; the only secret-classification rule CI enforces on every run is
`unclassified-secret-key`. See `env/registry/README.md`.

### 7. No operator-facing file names a command that does not exist

```
./scripts/check-template-claims.py
```

Run it to see the current counts of shipped commands, declared future commands
and scripts. Scans `env/*.env.example` and `docker-compose*.yml` comments. A backticked
`vizra <sub>` must be a shipped command or a declared future one; a declared
future command named anywhere must carry its declared marker **within 2 lines**,
so a promise carries its own qualifier rather than borrowing a neighbour's.

**Any `*.sh` token** is a script reference, with or without backticks and with
or without a path prefix — `backup.sh`, `./backup.sh`, `scripts/backup.sh`,
`` `./backup.sh` ``. It must exist in the tree (looked for as written and under
`./`, `scripts/` and `deploy/`), or be declared in `env/registry/meta.json`
`future_scripts` **with its marker in the window**; anything else is
`unknown-script`. The first version of this pass listed six names and excluded
`.` and `/` in a lookbehind, so the two spellings an operator-facing document
actually uses for a runnable script both passed unmarked — and because the six
matchable names were exactly the six declared future, `unknown-script` could not
be tripped by any documentation edit at all. A rule id that cannot fire is a
control that does not exist. It fires now: an invented `rotate-secrets.sh`
is red.

The sentence this exists to refuse shipped in the production template:

> `# ROTATING THIS RE-SEALS STORED MFA SECRETS. `vizra setup --rotate` requires`
> `# --yes-i-know for exactly this key.`

`vizra setup` does not exist. An operator who believed it, edited
`VIZRA_MFA_KEY_KEK` and restarted would not have re-sealed anything: every TOTP
secret stays sealed under the old key, becomes permanently undecryptable, and
every MFA-enrolled member is locked out. The marker window is 2 lines because
the block was tried first and failed its own red demonstration — a correct
sentence further down the same comment *laundered* the false one.

`scripts/check-doc-links.py` additionally scans compose comments for `env/…` and
`deploy/…` paths, after a header pointed at a file that had never existed.
`env/production.env`, `env/development.env` and `deploy/Caddyfile.local` are
allow-listed **by name, with reasons** — they are generated or operator-owned and
gitignored by design — rather than by relaxing the matcher.

### 8. Every compose guard still fails against a controlled mutation

```
bash docs/evidence/compose-topology/demo.sh
```

Runs the red/green demonstrations on every CI run, not only once. Each case
prints a sha256 either side of its mutation and **refuses to score a case whose
mutation did not apply** — otherwise a mutation that silently failed would run
the checker against the unmodified tree, pass, and be recorded as a guard that
caught something. It restores every file it touches and fails if the tree is not
byte-identical afterwards; the run prints its own totals — assertions **and
case count**, both counted by the harness — and the committed transcript under
`docs/evidence/compose-topology/` records them for the code commit it names.
Read the counts off the `RESULT:` line rather than counting `case_header`, which
was off by one in three successive PR bodies because it counts the function
definition too.

**Not every rule id has a red demonstration, and the tables above do not say so
on their own.** Sixteen of the 42 declared rule ids across the three checkers
have never been seen to fire; they are asserted by code review only, and a
reader deciding what this lane proves needs that distinction. The full list,
with the claim each one backs, is
`docs/evidence/compose-topology/CLAIMS.md` — regenerate it with
`python3 docs/evidence/compose-topology/claims.py` when a rule or a document
moves, and it recomputes the mapping from `demo.sh` rather than trusting a hand
count.

No condition in the harness reads its captured output through a pipe. Every one
uses a here-string, and no reporting pipeline ends in `head`: under
`set -o pipefail`, `printf … | grep -q` is a race — `grep -q` exits on its first
match, `printf` takes EPIPE, and pipefail propagates that through a pipeline
whose grep matched, so a correct guard is reported `FAIL: expected exit 1 …,
got 1`. It is fail-closed (the `ok` branch requires the pipeline to succeed), but
a required lane that can go red with no product cause is a defect in the lane.
`scripts/ci-required-guard.sh` (lines 80, 249, 348, 423, 440) and
`scripts/ci-required-select.sh` (line 56) still carry that shape; they are
outside this slice's diff and are recorded here as a follow-up rather than
edited alongside the thing they guard.

## Red/green demonstrations

Transcripts are under `docs/evidence/meta-validate/`. Each applies a controlled
mutation, shows the check red, restores, and shows it green.

| File | Mutation |
|---|---|
| `demo-1-hand-edited-features-json.txt` | a status hand-edited in the generated JSON and **committed** |
| `demo-2-stale-generated-file.txt` | a requirement title changed in the generator source without regenerating |
| `demo-3-dangling-requirement-id.txt` | `VZ-NOSUCH-999` and `VZ-ISSUE-404` referenced from an issue file |
| `demo-4-broken-relative-link.txt` | one resolving and one broken relative link added to `docs/MILESTONES.md` |
| `demo-5-floor-lane-deleted.txt` | `validate` removed from the manifest, both non-empty and empty |
| `demo-6-continue-on-error-three-spellings.txt` | `continue-on-error`, `"continue-on-error"`, `Continue-On-Error` inserted into the real `validate` job |
| `demo-7-generator-wrote-nothing.txt` | a generator that writes nothing, an empty file, only some declared files, and the pre-fix generator under the C/POSIX locale |
| `demo-8-range-and-slash-list-expansion.txt` | a range whose end does not exist, a slash-list with one bad member, a descending range |
| `demo-9-shell-override-and-conditional-step.txt` | `defaults.run.shell` at workflow and job level, `if: false`, a non-constant `if:`, and the required job renamed — all on the real `validate` workflow |

Demos 1 and 2 commit the mutation, because that is how one reaches CI: with the
mutation uncommitted, the dirty-tree precheck fires instead of the regeneration
check, which proves something weaker than intended.

## What is NOT covered

`docs/META_REPO.md` §7 names three target lanes for this repository. Only
`validate` exists.

| Lane | State |
|---|---|
| `validate` | **implemented here**, including the compose-topology checks added by VZ-ISSUE-002 |
| `bundle` | **not built.** There is no deployment bundle builder, no installer and no release record to build one from. `validate` renders the bundle *shape* (`bundle-no-checkouts`) from a tree with no component checkouts, which is a necessary condition for a bundle and not a bundle. |
| `boot` | **not built.** No lane in this repository starts a container. Everything the compose checks assert is read from a rendered model. |

`bundle` and `boot` are deliberately absent from `.github/required-checks.txt`
rather than listed and empty: `ci-required` fails on a required check that never
ran, so listing a lane nobody defined would block every merge rather than gate
anything. They are added by the slices that create the things they test.

Also not covered by any lane here: shellcheck on the guard scripts (no
shellcheck dependency is introduced by this slice), and `.github/CODEOWNERS`
itself, which **nothing enforces** — see that file.
