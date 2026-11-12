# Execution plan: ledger-status demo D11 derives its count dicts from the ledger

Status: READY_FOR_REVIEW (not verified, not merged).

## Context
Base `origin/main` 792cfad, branch `fix/ledger-status-demo-counts`, worktree `.claude/worktrees/meta-demo-fix`.
`docs/evidence/ledger-status/demo.sh` case D11 hard-coded the refusal message for the zero-record ledger
(`{'PLANNED': 191, 'VERIFIED': 1}` / `{'PLANNED': 192}`). The first real status record (meta PR #19,
VZ-FOUND-002 IMPLEMENTED, head 4eb6249) changes the true counts, the guard still goes red, but the demo scored
D11 as FAIL (`demo: 60 passed, 1 failed`), turning `validate` / `ci-required` red there (run 43210473134).

## Acceptance
- D11 still asserts the FULL exact message `summary.by_implementation_status is <tampered> but the features count <true>`, both dicts.
- Both dicts are computed from the scratch copy's `docs/quality/features.json`; the tampered summary is the true
  counts with one requirement moved PLANNED -> VERIFIED (keys sorted), so it differs in every ledger state.
- No PLANNED entry to move => the case is counted as a FAIL, never skipped.
- Same number of cases (61). No case weakened, deleted, or re-typed. No checker, workflow or ledger file changed.
- Non-goals: any change to `scripts/`, the records, or `features.json`.

## Implementation
`docs/evidence/ledger-status/demo.sh`, D11 block only.

### Other cases audited and left unchanged (none breaks with one real IMPLEMENTED record; shown by run (b))
- D1c `s.index('"id": "VZ-FOUND-008"')` then the next `"implementation_status": "PLANNED"`: holds while VZ-FOUND-008
  itself is PLANNED in the committed ledger. It would stop applying (the mutation would error, counted FAIL, loud)
  only when a real record is written for VZ-FOUND-008 itself. Left; follow-up candidate.
- G1 and every `build` case: `write_fixture_state` REPLACES the records file with the one fixture record, so they do
  not depend on the committed records being empty. Same latent dependency on VZ-FOUND-008 having no real record.
- D9 `text.rindex('"implementation_status": "PLANNED"')` and the D6/D9 needles naming VZ-CONTROLS-001: assume the
  LAST requirement (VZ-CONTROLS-001) is PLANNED. Unaffected by a record on any other requirement. Left.
- D10a copies the fixture record over the copy's records and rebuilds: independent of the real records.
- D10b `green "D10b restored (no record)"` and `records.orig`: the command restores whatever is committed and runs
  the remote check on it; with the PR #19 record it is GREEN (real merge commit on main). Only the label text
  "(no record)" is inaccurate in that state; behaviour is right. Left (label only).
- No other hard-coded count: `grep -n '19[012]' docs/evidence/ledger-status/demo.sh` matches nothing after the fix (only the D11 lines before it).

## Verification
Environment: macOS arm64 (Darwin 25.5.0), `gh` installed and authenticated (D3, D10b ran online).
Scratch clones under one `mktemp -d` directory, each at base 792cfad plus PR #19's two files
(`git fetch origin ledger/vz-found-002-implemented && git checkout FETCH_HEAD -- docs/evidence/ledger-generator/status_records.json docs/quality/features.json`, committed locally in the scratch clone only). Command in every run: `bash docs/evidence/ledger-status/demo.sh`.

## Progress and evidence

### (a) RED before the fix, one record (base demo.sh) — exit 1
```
== D11 the summary counts disagree with the features (verify round 1, NIT 3)
  mutation on /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/tmp.ubzoiSuMAw/copy/docs/quality/features.json: sha256 64ae15292deab1b1dadb315803e263ed83832c832a033ee3f563214107ed8c5a -> 54514aaf1814fd64659f807372895c7bc08ba4c60642c0dc2d3d505e4fdab258
  FAIL  D11 — expected a non-zero exit naming [summary.by_implementation_status is {'PLANNED': 191, 'VERIFIED': 1} but the features count {'PLANNED': 192}], got exit 1:
        | summary.by_implementation_status is {'PLANNED': 191, 'VERIFIED': 1} but the features count {'IMPLEMENTED': 1, 'PLANNED': 191}
        | LEDGER STATUS OUTPUT CHECK FAILED: 1 problem(s)
  GREEN (as required) D11 restored — exit 0: ledger status output: 192 entries, exact key set; 1 carry a status, 1 record(s), sets equal; every entry re-derived from the committed records in a fr
== cleanup
  tree restored: git status identical to the start
demo: 60 passed, 1 failed
exit 1
```

### (b) GREEN after the fix, same one-record state — exit 0, 61 cases
```
== D11 the summary counts disagree with the features (verify round 1, NIT 3)
  D11 tampered summary: {"IMPLEMENTED": 1, "PLANNED": 190, "VERIFIED": 1}
  mutation on /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/tmp.Kzz1oLGA7c/copy/docs/quality/features.json: sha256 64ae15292deab1b1dadb315803e263ed83832c832a033ee3f563214107ed8c5a -> 8d7897a4d9d77da88c2dd93968ca012b3a30725a100c719d45b1f6d6b55e1de5
  RED   (as required) D11 — exit 1, named: summary.by_implementation_status is {'IMPLEMENTED': 1, 'PLANNED': 190, 'VERIFIED': 1} but the features count {'IMPLEMENTED': 1, 'PLANNED': 191}
        | summary.by_implementation_status is {'IMPLEMENTED': 1, 'PLANNED': 190, 'VERIFIED': 1} but the features count {'IMPLEMENTED': 1, 'PLANNED': 191}
  GREEN (as required) D11 restored — exit 0: ledger status output: 192 entries, exact key set; 1 carry a status, 1 record(s), sets equal; every entry re-derived from the committed records in a fr
== cleanup
  tree restored: git status identical to the start
demo: 61 passed, 0 failed
exit 0
```

### (c) GREEN on this branch as it is (no record) — exit 0, 61 cases
```
== D11 the summary counts disagree with the features (verify round 1, NIT 3)
  D11 tampered summary: {"PLANNED": 191, "VERIFIED": 1}
  mutation on /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/tmp.UnyjvDQwb5/copy/docs/quality/features.json: sha256 173016b14a351f799447290699ab52ff3258b4ccd30a291a1904fddf0a0dc0b3 -> 091b001b15aa33214dce72a151b73560794fb9a020cfcada80f10c377a317734
  RED   (as required) D11 — exit 1, named: summary.by_implementation_status is {'PLANNED': 191, 'VERIFIED': 1} but the features count {'PLANNED': 192}
        | summary.by_implementation_status is {'PLANNED': 191, 'VERIFIED': 1} but the features count {'PLANNED': 192}
  GREEN (as required) D11 restored — exit 0: ledger status output: 192 entries, exact key set; 0 carry a status, 0 record(s), sets equal; every entry re-derived from the committed records in a fr
== cleanup
  tree restored: git status identical to the start
demo: 61 passed, 0 failed
exit 0
```

### (d) the case still bites — exit 1
One-record scratch state with the fixed demo.sh, and `scripts/check-ledger-status-output.py` mutated IN THE SCRATCH
CLONE ONLY: `if summ.get(key) != ...` -> `if False and summ.get(key) != ...` (exactly one match asserted). The
checker then exits 0 on the tampered summary and D11 is scored FAIL. The mutation lived only in the scratch clone,
which was deleted; the checker in this branch is untouched (`git diff origin/main -- scripts/` is empty).
```
== D11 the summary counts disagree with the features (verify round 1, NIT 3)
  D11 tampered summary: {"IMPLEMENTED": 1, "PLANNED": 190, "VERIFIED": 1}
  mutation on /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/tmp.5niarh1AiS/copy/docs/quality/features.json: sha256 64ae15292deab1b1dadb315803e263ed83832c832a033ee3f563214107ed8c5a -> 8d7897a4d9d77da88c2dd93968ca012b3a30725a100c719d45b1f6d6b55e1de5
  FAIL  D11 — expected a non-zero exit naming [summary.by_implementation_status is {'IMPLEMENTED': 1, 'PLANNED': 190, 'VERIFIED': 1} but the features count {'IMPLEMENTED': 1, 'PLANNED': 191}], got exit 0:
        | ledger status output: 192 entries, exact key set; 1 carry a status, 1 record(s), sets equal; every entry re-derived from the committed records in a fresh process
  GREEN (as required) D11 restored — exit 0: ledger status output: 192 entries, exact key set; 1 carry a status, 1 record(s), sets equal; every entry re-derived from the committed records in a fr
== cleanup
  tree restored: git status identical to the start
demo: 60 passed, 1 failed
exit 1
```

### Other checks (this branch)
| command | exit | note |
|---|---|---|
| `shellcheck docs/evidence/ledger-status/demo.sh` | 1 | 2 findings, same 2 as on origin/main 792cfad (no new finding) |
| `python3 scripts/check-doc-links.py` | 0 | |
| `python3 scripts/check-quality-json.py` | 0 | |
| `bash scripts/check-generated-ledger.sh` | 0 | byte-for-byte |

## Blockers and handoff
None. Independent verification and merge are for the verifier and chair. Follow-up candidates (not blocking):
the D1c/G1 dependence on VZ-FOUND-008 having no real record, and the "(no record)" label in D10b.
