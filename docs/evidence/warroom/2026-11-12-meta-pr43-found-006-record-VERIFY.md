# Verify meta PR #43 — VZ-FOUND-006 VERIFIED status record

- PR: https://github.com/yegamble/vizra/pull/43 (`ledger/vz-found-006-verified`), head 457df28ff61391599b2df1c5a2f2f722d219101c (unmoved at start and end; `gh pr view` headRefOid)
- Verifier: independent (did not write the record). Budget QUEUE-ledger-VZ-FOUND-006, verdict 1.
- Environment: darwin, fresh clone `/tmp/vzv-vizra-pr43-opYudq` (deleted after the run); origin/main e66b85de24cd39e3513b001d845c4e8b3716457c.

## 1. Diff scope
`git diff --stat origin/main...HEAD`: only `docs/evidence/ledger-generator/status_records.json` (+57, pure append of record #4) and `docs/quality/features.json` (VZ-FOUND-006 entry + summary counts PLANNED 188→187, VERIFIED 1→2). No existing record line changed or removed.

## 2. Checks (at PR head)
| Command | Exit | Result |
|---|---|---|
| `bash scripts/check-generated-ledger.sh` | 0 | reproduces byte-for-byte (UTF-8 and C/POSIX) |
| `python3 scripts/check-ledger-status-output.py` | 0 | 192 entries, 5 records, sets equal |
| `python3 scripts/check-ledger-status-remote.py` | 0 | 5 records proved; 99e74317 on core main; ci-required success on 52b4326b |
| `python3 -m unittest test_status` (docs/evidence/ledger-generator) | 0 | Ran 38 tests, OK, 0 skips |
| `git merge origin/main` (local branch) then generated-ledger + status-output | 0 / 0 | clean merge; still reproduces |

## 3. Bullets ↔ cases
docs/issues/VZ-ISSUE-001.md:25-29 hold all five bullets verbatim. features.json VZ-FOUND-006 cases: S1 "Every key read by config.Load reaches api and worker containers (asserted from rendered compose)", S2 "Every key `vizra setup` writes exists in the template", N1 "Production boot with dev JWT/session secret fails" (bullet: "Production boot refuses dev secrets (demonstrated)"), N2 "A key added to config without template/compose consumer fails CI", P1 "Log denylist test proves tokens/passwords/signed URLs never appear". evidence_required: "CI assertion outputs; boot-refusal transcript".

## 4. Merges (`gh pr view`)
| PR | state | head | merge commit | evidence last line (origin/main) |
|---|---|---|---|---|
| meta #17 | MERGED | ad86e243… = record | 6dfcb221… = record | PASS — SHA ad86e2436a94fd137cd9b30e51bc6f4a7cc8d92c |
| meta #33 | MERGED | e5316a9f… = record | 5124be5f… = record | PASS — SHA e5316a9f08f9718d2c3f33dcbbfd8e3d8e19cbc8 |
| core #20 | MERGED | 030a13fc… = record | 7f64b6de… = record | PASS — SHA 030a13fc4c52e9dca89ca761603b8a8924a1985c |
| core #25 | MERGED | 52b4326b… = record | 99e74317… = record | PASS — SHA 52b4326b7d1ed4d20919ceca3a64501d024b6516 |

## 5. Rationale vs evidence files
- S1: meta #17 VERIFY §B table from rendered models + M1 red, row "S1 … Proven statically" — supported.
- N2: meta #17 M5 (`VIZRA_FAKE_VERIFIER_KEY` no consumer → exit 1), M2/M6 template red, in `validate`; snapshot limit F2 — supported, limit recorded in FOLLOWUPS.md:36.
- S2: meta #33 round 2: snapshot equals core origin/main parse at source_commit, mutation (a) red with 8 `setup-key-untemplated`, step in `validate` — supported (R2-F1 limit in FOLLOWUPS.md:54).
- N1 + boot-refusal transcript: core #25 §1 real vizra-api/vizra-worker, 4 refusals each exit 1 with named errors, `grep -c changeme-changeme` = 0; §2 integration test red with `if false && production` — supported.
- P1: core #20 denylist (16 keys × 4 modes incl. token/password, mutation red); core #25 §3 SigV4/GCS V4/CloudFront, red when signature patterns removed — supported.
- CI assertion outputs: meta #17/#33 validate logs + core #25 §5 — supported.
Judged against docs/DEFINITION_OF_DONE.md and docs/evidence/ledger-status/README.md: every case and evidence item is independently proven by a non-author verifier at the merged head.

## 6. CI on 457df28
`gh pr checks 43`: ci-required pass (run 43286397528), validate pass (run 43286397427), GitGuardian pass.

## Findings
- BLOCKING: none.
- FOLLOW-UP F1: rationale sentence "Core has no separate JWT secret" is not stated in any of the four cited evidence files (core #25 VERIFY only says the JWT/session case is closed). Wording only; N1 is proven regardless.

FINAL VERDICT: PASS — SHA 457df28ff61391599b2df1c5a2f2f722d219101c
