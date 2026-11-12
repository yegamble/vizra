# VERIFY — yegamble/vizra-user PR #16 (VZ-CI-004 part: frontend dependency audit)

- Head SHA: 312d895771adb9304dee99e3a403cd695b181fde (checked at start and end: unchanged)
- Merge base: 0bb8dc6814e40b46d2db17bab39f4b0857dd1eac
- Environment: macOS Darwin 25.5.0, Node v24.21.0 (nvm), fresh clones in a mktemp dir (deleted afterwards), `npm ci` from the lockfile
- Verifier: independent vizra-verifier (did not write this code)

## Commands
| Command | Where | Exit | Result |
|---|---|---|---|
| `npm audit --audit-level=high` (the job's gate, supply-chain.yml:95) | merge base | 1 | 17 vulns (12 moderate, 4 high, 1 critical; next 16.0.0–16.4.0) |
| `npm audit --audit-level=high` | head | 0 | 10 moderate |
| `npm audit --omit=dev --audit-level=low` | head | 0 | no production findings |
| `npm ls minimatch --omit=dev` | head | 0 | (empty): dev-only |
| `npm ci` | head | 0 | |
| `npm run lint` | head | 0 | |
| `./node_modules/.bin/tsc --noEmit` | head | 0 | |
| `./node_modules/.bin/vitest run` | head | 0 | 26 files, 869 tests passed, 0 skipped |
| `npm run check:hygiene` | head | 0 | |
| `npm run check:contract` | head | 0 | |
| `npm run build` | head | 0 | |

## Results
- A. Scope: PASS. The diff touches only package.json and package-lock.json. package.json changes three pins, all exact: next 16.3.5→16.4.1, eslint-config-next 16.3.5→16.4.1, vitest 5.0.1→5.0.3. There are no `overrides` and no .npmrc changes. supply-chain.yml and required-checks.txt are untouched, so the audit level is still high.
- B. Red/green: PASS. The gate fails on the base and passes on the head. All 10 remaining findings are moderate, in one chain: minimatch GHSA-g3hv-75wg-m249 → @eslint/config-array → eslint 10, and @typescript-eslint/* → typescript-eslint. They are dev-only: there are no production findings with `--omit=dev`. npm's only offered fix is a breaking downgrade to eslint 9.39.5. No fixed version exists inside the eslint 10 line.
- C. next 16.4.0 and 16.4.1 release notes. Relevant items:
  - "detect proxy.ts correctly with compound pageExtensions" (#93246). This is a detection fix; it does not weaken anything.
  - Changes to `use cache` revalidation and reuse.
  - The listed fix for the GHSA-673q `use cache` RCE.
  - Nothing that changes CSP nonce handling or caching of authenticated responses.
  - Local e2e was not run (time budget). I rely on the CI e2e lane, which passed on the exact SHA and includes the security-headers spec.
- D. All local checks exit 0 (table above).
- E. CI on headSha 312d895 (headSha confirmed via run view): ci-required, frontend, contract, e2e, deps-scan, guard, docker-build and GitGuardian are green. image-scan is also green.

## Findings
- BLOCKING: none.
- FOLLOW-UP: the 10 moderate dev-only minimatch/eslint-chain advisories. Re-check when eslint 10 or typescript-eslint ships a fixed minimatch.

## VZ-CI-004
Not recordable as VERIFIED yet. deps-scan and image-scan are not required lanes, there is no secret-scan lane, and there is no publish-time image scan.

## Not run
- Local Playwright e2e and the security-headers spec (I rely on CI e2e).

FINAL VERDICT: PASS — SHA 312d895771adb9304dee99e3a403cd695b181fde
