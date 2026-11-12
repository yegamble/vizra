# Verify — meta PR #33 (VZ-INSTALL-002 setup answer coverage + template keys)

- PR: https://github.com/yegamble/vizra/pull/33, head `3b34e55dd11e420d846445b0f183f02221c5a41c` (confirmed via `gh pr view`; not moved)
- Verifier: independent (did not write the code). Clone: `/tmp/vzv-meta-pr33-hVexMz/r` (deleted after the run); vizra-core clone at main `46e9a33` (#22 merge).
- Env: darwin, python3, gh. Verdict budget: 3/4 used after this one.

## Commands and results
| Command | Exit | Result |
|---|---|---|
| `./scripts/compose-render.py --all --out build/compose-models` | 0 | 15 shapes |
| `python3 -I scripts/check-config-coverage.py` (unmodified head) | 0 | 0 violations, 64 template keys |
| M1: delete `VIZRA_TLS_MODE=` line from `env/production.env.example` | 1 | `setup-key-untemplated subject=tls/VIZRA_TLS_MODE` (red for the right reason) |
| M2: add `acme_email -> VIZRA_ACME_EMAIL` to `setup.json` questions | 1 | `setup-key-untemplated subject=acme_email/VIZRA_ACME_EMAIL` |
| restore both files | 0 | 0 violations; `git status` clean |
| `gh pr checks 33` | — | `ci-required` pass, `validate` pass, GitGuardian pass |
| `.github/required-checks.txt` | — | lists `validate` only; `validate` ran on this SHA, and its job runs `check-config-coverage.py` (validate.yml:308). Manifest matches. |

The rule logic works: M1/M2 reproduce as claimed.

## Snapshot against merged core
`setup.json` says `source_commit: 2c557ac62b04…`. In vizra-core, `git log 2c557ac` gives `fatal: Not a valid object name`. That was a #22 branch commit, and it was lost in the squash. Merged core `46e9a33` `internal/setup/questions.go` is a different interview:
- `storage`, `s3_*`, `smtp*`, `registration` and `import` questions **do not exist** on main.
- `postgres`, `redis`, `analytics` and `ipfs` use `Keys: topoKeys`, where `topoKeys = {"COMPOSE_FILE","COMPOSE_PROFILES"}` (questions.go:49). `engine.go:79-80` writes `env["COMPOSE_FILE"], env["COMPOSE_PROFILES"]` into the env file.
- `env/production.env.example` has no `COMPOSE_FILE` or `COMPOSE_PROFILES` line (`grep -c` = 0).

`python3 -I scripts/snapshot-setup-keys.py <core@46e9a33>` (the PR's refresh tool) **misparses** main. The regex skips non-literal `Keys: topoKeys` and takes the next literal list, so the mapping it produces is shifted: `postgres->DATABASE_URL`, `redis->VIZRA_CACHE_URL`, `analytics->CLICKHOUSE_PASSWORD`, `ipfs->VIZRA_SEARCH_MODE`. The keys that really get written never appear.

M3 reproducer: I hand-wrote the true questions map from core main (topology questions -> COMPOSE_FILE/COMPOSE_PROFILES, `unread_keys` emptied because main writes none of them) into `setup.json` and ran the check. Exit 1, 8 violations `setup-key-untemplated subject={postgres,redis,analytics,ipfs}/{COMPOSE_FILE,COMPOSE_PROFILES}`.

## Findings

```
FINDING 1: setup answer-coverage check is green while merged `vizra setup` writes untemplated keys
Severity:    BLOCKER
Confidence:  high
Affected:
  repo:      vizra
  files:     env/registry/setup.json (source_commit, questions, unread_keys), scripts/snapshot-setup-keys.py:20, env/production.env.example; core internal/setup/questions.go:49, engine.go:79-80 @46e9a33
  requirements: VZ-INSTALL-002, VZ-CI-002
Observed:
  The snapshot was taken from 2c557ac, which is not reachable in vizra-core. Merged #22 writes COMPOSE_FILE and COMPOSE_PROFILES. Neither is in the template, and the check passes (0 violations). The PR's refresh script cannot fix this: it misparses `Keys: topoKeys` and emits a shifted, wrong mapping.
Failure:
  The required `validate` gate claims "every answer vizra setup writes has a template key" and passes against the setup that actually shipped. That is a false green. The 14 `unread_keys` and the PR body's "16 pending keys" table describe questions that main does not have.
Perspective: operator, developer
Recommendation:
  Re-snapshot from core 46e9a33 with a parser that resolves named key slices (or have core emit the question->keys JSON). Then template or declare COMPOSE_FILE/COMPOSE_PROFILES, drop the stale unread_keys, and set source_commit to a reachable core commit (check it with `git cat-file -e`).
Acceptance criteria:
  snapshot-setup-keys.py output against core main equals setup.json questions. The check is green only with COMPOSE_* handled. source_commit resolves in vizra-core.
Tests:
  M3 above (true main map -> 8 violations before the fix, 0 after).
```

Follow-ups (non-blocking):
- F-1: The template comment still lists `STORAGE_BACKEND / SMTP_* / REGISTRATION_* / IMPORT_*` as "not yet carried". That is fine, but it should be re-worded once the snapshot is corrected.
- F-2: external-postgres shapes lack POSTGRES_PASSWORD (known from core #22; this PR does not claim it).

## VZ-INSTALL-002 cases still open
Storage/S3, SMTP, registration and import questions: none exist in merged core, so none has a reader. Optional-component selection is only through COMPOSE_* (untemplated). Also open: `--web` loopback wizard, `--non-interactive`, `--check`, `--rotate`, the KEK `--yes-i-know` path and re-run preservation. All of these are outside this meta PR.

FINAL VERDICT: FAIL — SHA 3b34e55dd11e420d846445b0f183f02221c5a41c
