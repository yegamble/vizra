# Ledger generator (evidence of how docs/quality/features.json was produced)

`docs/quality/features.json` is generated from these Python sources (`core.py` DSL + `s0…s9` sections) by `build.py`, which also validates: unique IDs, required fields, resolvable dependencies, no dependency cycles, every entry in `full`, and **core closure** (a core requirement never depends on a full-only requirement). Run from this directory:

```
python3 build.py ../../quality/features.json
```

Last run 2026-09-15: `OK 188 requirements; core=141` (exit 0). This is documentation tooling, not application code. Edit the sources, regenerate, and commit both; do not hand-edit the JSON. A CI check that reruns the validator belongs to milestone M0 (VZ-CI-001).
