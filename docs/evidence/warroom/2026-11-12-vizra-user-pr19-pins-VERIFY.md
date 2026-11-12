# Verify — vizra-user PR #19 (VZ-FOUND-001 negative, VZ-FOUND-004 user part)

- SHA: 87dc3a43e6e15f40e844fc46fe48d0939b16437a (PR head confirmed unchanged at start)
- Env: macOS darwin, Node v24.21.0, fresh clone /tmp/vzv-user-pr19-qBBwvS (deleted after)
- Verifier: independent (not builder)

## Commands and results
| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | installed |
| `npx vitest run scripts/ci/check-dependency-pins.test.mjs` | 0 | 14 passed / 14, 0 skipped |
| `node scripts/ci/check-dependency-pins.mjs` (baseline) | 0 | OK + 6 printed ADR-001 GAP lines |
| `bash scripts/ci/check-audit-gate.sh` | 0 | "npm audit --audit-level=high fails on the vulnerable fixture (lodash 4.17.20)" |

## Mutations (each red, restored with `git checkout`, then green exit 0)
| Mutation | Red exit | Reason reported |
|---|---|---|
| delete package-lock.json | 1 | `package-lock.json is missing` |
| .nvmrc → 22.15.0 | 1 | engines.node must equal .nvmrc; unrecorded node gap |
| .nvmrc → 22 | 1 | `.nvmrc must be an exact version, got '22'` |
| `next` → `^16.4.1` | 1 | not an exact version; lockfile out of sync; resolves 16.4.1 vs ^16.4.1 |
| frontend-ci.yml `npm ci` → `npm install` | 1 | `frontend-ci.yml:44 installs with 'npm install'` |
| frontend-ci.yml `node-version-file: .nvmrc` → `node-version: 22` | 1 | setup-node without node-version-file; sets node-version directly |
| remove Next.js line from adr_gaps | 1 | `ADR-001 mismatch not recorded ... next: ... 16.3.x, package.json pins 16.4.1` |
(Also tried appending steps to a new ci.yml: red; that untracked file was removed before the green re-run.)

## CI on SHA
`gh run list -c 87dc3a4…`: ci-required, frontend-ci, contract-ci, ci-guard, e2e, docker-build, supply-chain all success. frontend job "Canonical gate (npm run ci)" log shows `> vizra-user@0.0.0 check:pins` first and its OK line. `frontend` is a required entry in .github/required-checks.txt; deps-scan is deliberately not required (as stated).

## Audit
- Diff: 9 files; only removed lines are the old engines (package.json + lockfile root, exactly one lockfile line) and the old `ci` script line (extended, not weakened). No assertions removed, no skip/todo added. e2e.yml untouched.
- Gap-recording judgement: `adr_gaps` makes check:pins pass while Next.js 16.4.1 contradicts ADR-001 16.3.x. This is NOT a false green for this PR: the PR body states "**'Match ADR' is NOT met**: 6 ADR-001 gaps", the JSON note says a listed gap means the success case is not met, the check prints every gap, and stale/unlisted gaps fail. The VZ-FOUND-004 success case stays open → owner ADR amendment (follow-up).

## Findings
- FOLLOW-UP F1: ADR-001 needs amendment (Node row; Next.js 16.3.x vs 16.4.1; versions for React, Tailwind, TypeScript). Until then VZ-FOUND-004 "versions match ADR" must not be marked met.
- FOLLOW-UP F2: check:pins exits 0 with ADR gaps present; once the ADR is amended, consider making any non-empty adr_gaps fail so the success case cannot be claimed while gaps exist.

No BLOCKING findings.

FINAL VERDICT: PASS — SHA 87dc3a43e6e15f40e844fc46fe48d0939b16437a
