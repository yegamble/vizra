# Execution plan: VZ-ISSUE-002 closing round — make every compose-topology claim true

## Context

- Repo: vizra (meta). Worktree `/Users/yosefgamble/github/vizra/.claude/worktrees/meta-compose`.
- Branch `feat/m0-compose-topology`, base head `9c4b5d3285e1368634bc2042a83a91bfcb7e564b`
  (confirmed clean, `git status --porcelain` empty, HEAD == `origin/feat/m0-compose-topology`).
- PR https://github.com/yegamble/vizra/pull/4.
- Ledger IDs: VZ-TOPOLOGY-001, -002, -003, -006, -007, VZ-CI-002, VZ-OPS-008.
- Inputs read: `AGENTS.md`;
  `docs/evidence/warroom/2026-09-21-meta-pr4-compose-topology-VERIFY.md`
  § "Re-verification at 9c4b5d3" (S-1…S-7);
  `docs/evidence/warroom/2026-09-21-meta-pr4-compose-topology-INFRASTRUCTURE.md`
  § "Chair note on the final re-review" and below (NEW-2, NEW-3).

**The defect class this round closes.** The topology itself is sound — an
independent verifier reproduced all three VZ-ISSUE-002 acceptance bullets from
its own renderer, three rounds running, and the infrastructure seat has no
blocking finding open. What fails is a different thing: several of this PR's
checkers are **text matches that its own documents describe with guarantee
words** ("invokes", "both directions", "refuses", "enforced") the code does not
deliver. Every item below either makes the sentence true or removes it. Nothing
else is added.

## Acceptance

I am a fresh builder; the previous builder spent its two fix rounds. The chair's
list is the acceptance target and it is closed — no new rule, shape, key or
behaviour beyond items 1–7.

| # | Finding | Observable success |
|---|---|---|
| 1 | S-1 / NEW-2 | new rule id `known-false-stale-disclosure` fails when either disclosure marker survives while `known_false_probes` is empty; the existing direction still fails; **both** demonstrated red by rule id |
| 2 | S-2 | `gated-probe-unrecognised` decides "invoke" structurally from the rendered `healthcheck.test`, not by substring; the verifier's four bypass spellings plus `["CMD","true"]` and `["NONE"]` all red; the real probe green in all 13 shapes; the residual stated wherever the rule is described |
| 3 | S-3 | the script matcher reaches `./x.sh`, `scripts/x.sh` and a backticked path form; `unknown-script` is reachable; a path form **with** its marker in the window stays green |
| 4 | S-4 | no `… \| grep -q` under `set -o pipefail` anywhere in `demo.sh`; 25 consecutive full runs green with identical counts; sibling scripts/workflows swept |
| 5 | S-5 | `--drift` compares the `secret` flag against the component source; removing `"secret": true` from `VIZRA_SESSION_SECRET` in `env/registry/core.json` fails drift; honest snapshots still pass; BLOCKED path still exit 2 |
| 6 | S-6 (NIT) | residual stated precisely in `compose-render.py`'s docstring and COMMANDS.md §4. **No widening of the suffix heuristic.** |
| 7 | NEW-3 | three one-line operator-surface edits (ports named beside variables; documented `/readyz` command cannot read OK on `degraded`; the 4092/4096 sentence attributes intent to the oversubscription, not the coincidence) |
| 8 | THE CLASS | `docs/evidence/compose-topology/CLAIMS.md` — every guarantee-word sentence on the operator/CI surfaces, its file:line, the demo case id that turns red when it is false, and what it does **not** guarantee. Written last, so it describes the final code. |
| 9 | S-7 | PR body rewritten from tool output (case count from the harness, not by hand), every claim at the strength CLAIMS.md supports |
| 10 | — | transcripts regenerated in a final evidence-only commit stamped with the last code commit's SHA (branch V9 convention) |

Non-goals, explicitly: no change to `docker-compose*.yml` **semantics** (NEW-3
touches comments and docs only); no edit to `.github/required-checks.txt` or the
ledger generator's gate (`build.py:20`); `docs/quality/features.json` stays
byte-identical; no component repository is touched (read only via
`git -C <path> show origin/main:<file>`); no container is started.

## Implementation

No migration, no OpenAPI operation, no UI. Deployment configuration and its
checkers only.

| Item | Files |
|---|---|
| 1 | `scripts/check-compose-topology.py` (RULES + the disclosure block + its comment), `docs/META_REPO.md` §2a, `docs/quality/COMMANDS.md` §5, PR body |
| 2 | `scripts/check-compose-topology.py` (`probe_state` stays the single four-state decision; a new structural `probe_invokes()` beside it), `docs/META_REPO.md` §2a, `docs/quality/COMMANDS.md` §5 |
| 3 | `scripts/check-template-claims.py` (`SCRIPTNAME`, its comment, the resolution order), `docs/quality/COMMANDS.md` §7 |
| 4 | `docs/evidence/compose-topology/demo.sh` (every `\| grep -q` and every `\| head -N` reporting pipeline), sweep of `scripts/*` and `.github/workflows/*` |
| 5 | `scripts/check-config-coverage.py` (`check_drift`, a declared `SECRET_SOURCE` table in the checker rather than a new registry field), `docs/quality/COMMANDS.md` §6, `env/registry/README.md` if it describes drift |
| 6 | `scripts/compose-render.py` docstring, `docs/quality/COMMANDS.md` §4 |
| 7 | `README.md`, `env/production.env.example`, `docs/quality/COMMANDS.md` §5a |
| 8 | `docs/evidence/compose-topology/CLAIMS.md` (new) |

Shared interfaces: none. `api/openapi.yaml` and migrations are `vizra-core`'s;
this slice consumes neither.

### Design notes decided before writing code

- **Item 2's structural rule.** From the RENDERED model, so `${POSTGRES_USER}`
  is already substituted. `["CMD", argv…]` → `basename(argv[0])` must equal the
  declared command. `["CMD-SHELL", s]` → `s` must contain none of
  `; | & # backtick $( < > newline` (which subsumes `||` and `&&`) and its first
  whitespace-separated word must be the declared command. Any other form —
  a bare string that survived rendering, `["NONE"]`, absent — is a violation.
  The four-state `probe_state()` from V2 stays the single place absent /
  disabled / known-false / real is decided; the structural parse runs only on
  the REAL branch.
  Rendered probes this must keep green, confirmed before writing the rule:
  `postgres ["CMD-SHELL", "pg_isready -U \"vizra\" -d \"vizra\""]`,
  `redis ["CMD", "valkey-cli", "ping"]`. Gated targets are exactly those two
  (`api→postgres`, `api→redis`, `migrate→postgres`, `worker→postgres`,
  `worker→redis`).
  **Residual to state, not to hide:** it still cannot show that the command can
  exit non-zero (`pg_isready --version` passes) or that a binary named like the
  declared command is the real one.
- **Item 5's source parse.** `vizra-core/internal/config/keys.go` writes
  `{Name: "X", Secret: true, …}` — one struct literal per key, both fields in
  the same braces, `Secret` always before `Doc`. `vizra-search` and `vizra-user`
  carry **no** machine-readable secret marker (checked: `lib/config.ts` has no
  `secret` token at all; `internal/config/config.go` redacts but never declares
  a flag). So the table is per-component and `None` means UNCHECKED — reported
  on every drift run rather than passing silently, which is the S-5 defect one
  level down.
- **Item 4's replacement form.** Here-strings (`grep -q … <<< "$out"`): bash 3.2
  on this host supports them, and a here-string is a file descriptor, not a
  pipeline, so there is no SIGPIPE producer for `pipefail` to propagate. The
  reporting pipelines lose `| head -N` too (`grep -mN`, or `sed -n '1,Np'`),
  because `head` closing the pipe is the same mechanism.

## Verification

Preflight, run before any edit: Python 3.9.6 (`/usr/bin/python3`), PyYAML 6.0.3,
Docker Engine 29.8.0 + Compose v5.5.1, `gh` 2.98.0, bash 3.2.57, jq 1.7.1.
All present. **No container is started** — this is a render-only slice.

Required local lane (the 8 commands in `docs/quality/COMMANDS.md`):

```
./scripts/check-generated-ledger.sh
./scripts/check-quality-json.py
./scripts/check-doc-links.py
./scripts/compose-render.py --all --out build/compose-models
./scripts/check-compose-topology.py build/compose-models
./scripts/check-config-coverage.py build/compose-models
./scripts/check-template-claims.py
bash docs/evidence/compose-topology/demo.sh
```

plus `./scripts/ci-required-guard.sh` and `./scripts/check-config-coverage.py --drift`
(the latter is BLOCKED, exit 2, with the checkouts absent — recorded as BLOCKED,
never as a pass).

Every rule change is *demonstrated*: red for the DECLARED rule id, sha256 of the
mutated file before and after (the harness refuses to score a mutation that did
not apply), green after restore, and the tree byte-identical at the end.

- 25 consecutive full `demo.sh` runs, all green, identical counts — item 4's
  acceptance. Run from a self-contained copy under my own `mktemp -d` so it
  cannot race an edit in the worktree.
- Drift red/green recorded in `docs/evidence/compose-topology/drift-transcript.txt`.
  It cannot run in CI and is not added to `demo.sh`.

Baseline before any edit, from tool output: `demo.sh` → **73 assertions passed,
0 failed, exit 0, 39 `CASE` headers**, 3 min 51 s wall.

## Progress and evidence

Appended as it happens. Nothing here is a narrative; each line names a command,
an exit code and a file.

- 2026-09-21 — preflight done; worktree clean at `9c4b5d3`; baseline demo run
  73/73 exit 0, 39 cases, 3 min 51 s.
- 2026-09-21 — items 1–7 implemented. Code commit
  **`e82e659e251356a55c94fc36a0f6dc0730239808`**; evidence commit
  **`cf9e4c86b077335fcad8cf8050c8fe57a50431c2`**. Plain push onto
  `feat/m0-compose-topology`, no amend, no rebase, no force.

| Command | Exit | From tool output |
|---|---|---|
| `./scripts/check-generated-ledger.sh` | 0 | 191 requirements, reproduces byte-for-byte in both locales |
| `./scripts/check-quality-json.py` | 0 | 191 ids, 287 references, all resolve |
| `./scripts/check-doc-links.py` | 0 | 95 markdown files; 6 compose paths resolve |
| `./scripts/ci-required-guard.sh` | 0 | fixtures 6 / 7 / 10, floors met |
| `./scripts/compose-render.py --all` | 0 | 13 shapes |
| `./scripts/check-compose-topology.py` | 0 | `13 shape(s) … 27 rules, 0 violations; 2 known-false` |
| `./scripts/check-config-coverage.py` | 0 | `34 component keys, 58 template keys, 58 interpolated, 13 shapes; 1 alias; 1 retired refused` |
| `./scripts/check-template-claims.py` | 0 | `10 files, 16 references; 5 shipped, 11 future; 0 resolved on disk, 6 future scripts` |
| `python3 docs/evidence/compose-topology/claims.py --check` | 0 | `CLAIMS.md is current (47 audited claims)` |
| `./scripts/check-config-coverage.py --drift` (checkouts absent) | **2** | **BLOCKED**, recorded as BLOCKED |
| `bash docs/evidence/compose-topology/demo.sh` | 0 | `RESULT: 95 assertion(s) passed, 0 failed, across 50 case(s)`; tree byte-identical; **0** `broken pipe` |

Demonstrations added this round, each red for the DECLARED rule id with a
digest pair either side and green after restore:

| Case | Rule id | Mutation |
|---|---|---|
| 26a–26e | `gated-probe-unrecognised` | `pg_isready \|\| true`; `true # pg_isready`; `sh -c 'exit 0; pg_isready'`; `echo pg_isready`; `["NONE"]` |
| 27 | `known-false-stale-disclosure` | `known_false_probes: []` with both paragraphs present |
| 28a–28d | `unmarked-future-script` ×3, `unknown-script` ×1 | `./backup.sh`; `scripts/backup.sh`; `` `./backup.sh` ``; `rotate-secrets.sh` |
| 28e | — (green) | `./backup.sh` **with** its marker in the window stays exit 0 |
| drift transcript | `registry-drift` | `"secret": true` deleted from `VIZRA_SESSION_SECRET` |

Residuals measured rather than asserted, recorded in `local-run.txt`:
`["CMD-SHELL","pg_isready --version"]` is **green** (the S-2 limit), and an
absent rule id is still reported absent after the here-string change (the S-4
acceptance criterion that the fix must not make a condition unconditionally
true).

Scope checks: `docs/quality/features.json` byte-identical to `main`;
`.github/required-checks.txt`, `scripts/ci-required-guard.sh` and
`docs/evidence/ledger-generator/` untouched; no path under `vizra-{core,user,search}/`
in the diff; no container started; added lines carry no credential-shaped
literal and no `scheme://user:pass@host`.

## Blockers and handoff

None at plan time. `--drift` needs the component checkouts, which is a recorded
BLOCKED for CI and not a blocker locally (they exist in the main checkout and
are read with `git -C … show origin/main:<file>`).

If the verifier fails this round, the chair's standing instruction applies:
prefer **removing** a claim to defending a weak one, and the PR is cut down to
the topology plus the rules whose claims hold.
