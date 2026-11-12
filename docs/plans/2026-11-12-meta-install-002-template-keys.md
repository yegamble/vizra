# VZ-INSTALL-002 (meta) — template keys for `vizra setup` + answer-coverage assert

Status: IN_PROGRESS → READY_FOR_REVIEW when CI on the final head is green.
Core source read: vizra-core PR #22, `internal/setup/questions.go` at 2c557ac62b04.

## Plan
1. Snapshot the interview (question id → keys) into `env/registry/setup.json`
   with `scripts/snapshot-setup-keys.py <core checkout>` (records source_commit).
2. `scripts/check-config-coverage.py` rules:
   - `setup-key-untemplated`: a written key with no production-template line and
     not a declared `unread_keys` finding (plus consistency of unread_keys/setup_reads).
   - `template-key-unasked`: a production-template key no question writes and
     `not_asked` gives no reason for.
   - `template-key-unused` also accepts `setup_reads` (keys `vizra setup` itself reads).
3. Red first: today's template with no unread/setup_reads lists → 16 violations.
4. Template: add only keys with a reader (VIZRA_DOMAIN, VIZRA_TLS_MODE — read by
   core `internal/setup/edge.go` RenderEdge). The other 14 are read by nothing at
   2c557ac: listed as `unread_keys` and reported as findings to the core PR.
5. Mutations: delete a template key → red; add an untemplated question key → red;
   drop a not_asked reason → red.

## Follow-up
- Core PR #22 must refresh `internal/setup/testdata/meta-production-env-keys.txt`
  after this merges and shrink `PendingTemplateKeys` to the 14 unread keys.
