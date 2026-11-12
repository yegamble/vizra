# VERIFY — meta PR #31 VZ-INSTALL-004 first slice (deterministic bundle + content/render check)

- PR: https://github.com/yegamble/vizra/pull/31 (OPEN), head `b7761b3a7d3ac1dfaaadc9b7c0230bb06fc0d845` (matches brief)
- Verifier: independent (did not write the code). Verdict budget: 1/4 used by this verdict.
- Environment: macOS arm64 (Darwin 25.5), python3 system, fresh clone in `/tmp/vzv-meta-pr31-*` (deleted after).

## Lane run
`bash tests/bundle/bundle_test.sh` → exit 0, `PASS: 10 cases`, 0 skips; case 3: 13/13 production shapes rendered from the unpacked bundle.

## CI on the SHA (`gh api .../commits/b7761b3.../check-runs`)
validate success, ci-required success, GitGuardian success — all head_sha b7761b3. `.github/required-checks.txt` lists only `validate` (unchanged by this PR); `validate` ran and its log (run 43248197726) contains `ok 1 - two builds are byte-identical`, `ok 3 ... 13/13`, `PASS: 10 cases` → bundle step really executed in the required lane. Manifest matches jobs run.

## Earlier-round fix (otel)
`scripts/bundle-contents.json` include carries `docker-compose.otel-managed.yml`, `docker-compose.otel-external.yml`, `deploy/otel/collector.yaml`; `bundle.py check` now requires every file of every production shape in shipped `compose-shapes.json` (case 9, and my DEMO2b). Confirmed.

## Demonstrations reproduced by me (script own, outside repo; `COPYFILE_DISABLE=1`)
| Demo | Result |
|---|---|
| D1 two builds (2 s apart) `cmp` | identical, sha256 aa699685d640b489… (green) |
| baseline check | exit 0 |
| D2 remove `docker-compose.prod.yml` from bundle | exit 1: `manifest lists docker-compose.prod.yml, absent`, `missing: compose files`, `missing: production shape prod-default needs …` |
| D2b remove it from bundle AND manifest | exit 1: `missing: compose files (docker-compose.prod.yml)` + shape errors |
| D3 add `extra.txt` | exit 1: `unlisted file in bundle: extra.txt` |
| D4 syntactically broken compose built consistently | exit 1 (yaml ParserError traceback from bind-source scan — red, but via traceback) |
| D4b valid YAML, bad `depends_on` in docker-compose.yml | exit 1: `render of production shape prod-default from the unpacked bundle failed` |
Restore = unmutated build → green (baseline). (First D2/D3 attempt failed only on macOS `._` AppleDouble entries from my repack — my artifact, not a defect.)

## Findings
No BLOCKING findings.

FOLLOW-UP:
- F-1 (low): a tamperer who adds a file AND its sha256 to MANIFEST.json passes `check` (exit 0, reproduced): the manifest is not compared to the shipped `include` list. Not a claimed property (no signing); harden by checking manifest keys == include ∪ {contract}.
- F-2 (low): broken compose YAML is reported via an uncaught Python traceback from `bind_sources`, not a `bundle: FAIL:` line. Still exit 1.
- F-3 (info): `schema_version = migrations on disk` is proven only against test fixtures, not a pinned vizra-core tag.

## Ledger cases still open for VZ-INSTALL-004
Deploy scripts, Caddyfile template, systemd units, release record (`releases/<tag>.json`, `vizra release`) — declared `not_yet_shipped`; schema from a real pinned core tag; separate required `bundle` lane in required-checks.txt; release upload. Success case (cmp + schema vs fixtures) and negative case (missing bind-mount source, case 5) reproduced for this slice.

FINAL VERDICT: PASS — SHA b7761b3a7d3ac1dfaaadc9b7c0230bb06fc0d845
