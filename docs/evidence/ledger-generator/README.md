# Ledger generator (evidence of how docs/quality/features.json was produced)

`docs/quality/features.json` is generated from these Python sources (`core.py` DSL + `s0…s9` sections) by `build.py`, which also validates: unique IDs, required fields, resolvable dependencies, no dependency cycles, every entry in `full`, and **core closure** (a core requirement never depends on a full-only requirement). Run from this directory:

```
python3 build.py ../../quality/features.json
```

Last run 2026-09-23 (after VZ-AUDIT-001 was added): `OK 192 requirements; core=142` (exit 0). Earlier: 2026-09-15, after the open-questions ratification, `OK 190 requirements; core=141`. This is documentation tooling, not application code. Edit the sources, regenerate, and commit both; do not hand-edit the JSON. A CI check that reruns the validator belongs to milestone M0 (VZ-CI-001).

## Status: only with evidence (queue 2i, 2026-09-23)

A section source can never set a status: `build.py` refuses any entry that leaves the DSL as anything but PLANNED / UNVERIFIED / NOT_STARTED / NOT_RELEASED, or with evidence. The only source of a status is a record in [`status_records.json`](status_records.json), checked by [`status.py`](status.py) (offline, inside the generator) and by [`scripts/check-ledger-status-remote.py`](../../../scripts/check-ledger-status-remote.py) (online, with `gh api`, in the `validate` lane). A record may claim `IMPLEMENTED` or `VERIFIED`; everything else is refused by name. The rules, the demonstrations and today's decisions are in [`docs/evidence/ledger-status/`](../ledger-status/README.md). Unit tests: `python3 -m unittest -v test_status` from this directory.

Last run 2026-09-23 (queue 2i): `OK 192 requirements; core=142; … statuses={'PLANNED': 192}` (exit 0) — zero records admitted; see the ledger-status README for why each candidate was not recorded.

