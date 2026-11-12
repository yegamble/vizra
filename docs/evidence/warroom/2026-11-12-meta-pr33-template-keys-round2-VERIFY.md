# Verify (round 2): meta PR #33 (VZ-INSTALL-002 setup answer coverage + template keys)

- PR: https://github.com/yegamble/vizra/pull/33, head `e5316a9f08f9718d2c3f33dcbbfd8e3d8e19cbc8` (checked with `gh pr view`; it has not moved)
- Verifier: independent; I did not write this code. Verdict 4 of 4 for VZ-INSTALL-002.
- Clone: `/tmp/vzv-vizra-pr33b-ihVMm0/{r,core}`, deleted after the run. vizra-core freshly cloned, origin/main = `46e9a33` (#22).
- Environment: darwin, python3, Docker Compose v5.6.1, gh.

## Prior BLOCKING finding (round 1 FINDING 1): fixed
- `snapshot-setup-keys.py <core>` output equals setup.json: questions equal, compose_keys equal, and source_commit equals origin/main `46e9a33`. It resolves `Keys: topoKeys`, so postgres/redis/analytics/ipfs now map to COMPOSE_FILE and COMPOSE_PROFILES. The shifted mapping is gone.
- `unread_keys` is `[]`.
- `--check core` printed PASS (16 questions), exit 0.

## Commands and demonstrations
| # | Command / mutation | Exit | Result |
|---|---|---|---|
| 1 | `compose-render.py --all --out build/compose-models` | 0 | |
| 2 | `check-config-coverage.py build/compose-models` (head) | 0 | 0 violations, 64 template keys |
| a | real map with `compose_keys={}` (COMPOSE_* handling dropped) | 1 | 8 × `setup-key-untemplated` ({postgres,redis,analytics,ipfs}/COMPOSE_{FILE,PROFILES}) |
| b1 | `--check` with source_commit = 40 zeros | 1 | "does not exist in vizra-core" |
| b2 | `--check` with source_commit `5582ba21…` (a core PR-head commit, not on main) | 1 | "is not an ancestor of vizra-core origin/main" |
| b3 | `--check` with source_commit `origin/main~1` | 1 | questions.go absent at that commit, so it fails |
| c1 | add question `smtp -> SMTP_HOST` | 1 | `setup-key-untemplated subject=smtp/SMTP_HOST` |
| c2 | delete `VIZRA_SITE_HANDLE=` from the production template | 1 | `setup-key-untemplated subject=instance_name/VIZRA_SITE_HANDLE` |
| d1 | `compose_keys += COMPOSE_X` (no question writes it) | 1 | "listed as compose_keys but no question writes it" |
| d2 | append `COMPOSE_PROFILES=` to the template | 1 | "listed as compose_keys … but env/production.env.example also carries it" (plus template-key-unused) |
| e | `--check /nonexistent` (simulates a failed clone) | 1 | FAIL, not a skip |
| 3 | restore all files | 0 | 0 violations; `git status` clean |
| 4 | `check-template-claims.py` | 0 | 0 violations |
| 5 | `check-doc-links.py` | 0 | |
| 6 | shellcheck on changed `.sh` files | n/a | the PR changes no `.sh` file |

## Are COMPOSE_* as compose_keys a hidden gap?
Docker Compose reads COMPOSE_FILE and COMPOSE_PROFILES from `--env-file`. Reproduced: an env file with `COMPOSE_FILE=x.yml:y.yml` and `COMPOSE_PROFILES=p`, run as `docker compose --env-file my.env config --services`, printed `a` and `b`, so both values were honoured. No container and no compose interpolation reads them. In the meta tree, only a research note mentions them; no script does. Core writes them (engine.go:79-80) and `vizra setup --check` validates them against the topology answers (engine.go:136). A template line would add nothing an operator needs. Not a false green.

## Workflow review (validate.yml step)
- `run:` uses the default bash `-e`, so a failed `git clone` fails the step.
- No `continue-on-error` anywhere in validate.yml.
- The step adds no `uses:`, and every existing `uses:` is pinned to a 40-hex SHA.
- A `--filter=blob:none --no-checkout` clone still allows `git show` of the file (lazy fetch).
- The step runs inside the `validate` job, which `required-checks.txt` lists.

## Findings
No BLOCKING findings.

Follow-ups:
- R2-F1: `--check` compares at source_commit only. If core main later adds a question, the check stays green until someone re-snapshots. Consider also failing when the parse at origin/main differs from the snapshot.

## CI
`gh pr checks 33` on e5316a9: `ci-required` pass (13m11s), `validate` pass (13m1s), GitGuardian pass. The validate log contains the snapshot step's PASS line. The manifest lists `validate`, and that job ran on this SHA.

FINAL VERDICT: PASS — SHA e5316a9f08f9718d2c3f33dcbbfd8e3d8e19cbc8
