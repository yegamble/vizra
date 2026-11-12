# Execution plan: VZ-CI-004 — vizra-user deps-scan green

## Context
yegamble/vizra-user, base origin/main 0bb8dc6, branch fix/deps-scan-green (head 312d895), PR #16. deps-scan red on main (run 43232455771).

## Acceptance
`npm audit --audit-level=high` (deps-scan verdict step) exits 0 on the head; red on main. No overrides, ignore lists or threshold changes; deps-scan stays out of required-checks.txt.

## Implementation
next + eslint-config-next 16.3.5 -> 16.4.1 (no 16.3.x fix for GHSA-2464-fhr4-w9xw, GHSA-673q-mjm6-r5xr, GHSA-p3m5-59mp-jv5r; range <=16.4.0). vitest 5.0.1 -> 5.0.3. Lockfile: sharp 0.35.5, vite 8.3.8, zod 4.6.7, source-map-js 1.2.2.

## Verification
Main: audit exit 1 (crit next; high next/sharp/vite/zod/source-map-js). Head: exit 0, 10 moderate left (minimatch GHSA-g3hv-75wg-m249 via eslint; @typescript-eslint <=8.72.2, no fix published).
Local (node 24.21.0, npm 11.19.0) via quiet.sh: lint 0, tsc 0, vitest 0 (26 files / 869 tests), hygiene 0, contract and build: see PR.

## Progress and evidence
IMPLEMENTED, READY_FOR_REVIEW once CI is green. Not verified (builder).

## Blockers and handoff
Moderate eslint-chain advisories go to FOLLOWUPS. image-scan: Debian base CVEs (owner inbox 9).
