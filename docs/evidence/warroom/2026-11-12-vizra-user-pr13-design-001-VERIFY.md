# VERIFY: vizra-user#13, VZ-DESIGN-001 (remainder)

- Verifier: independent vizra-verifier (did not write this code). Date 2026-11-12.
- SHA: fa99ca384af1fe7dfc3d2affdefc7d25ead4d0ef. `gh pr view` showed this head at the start and again at the end; PR OPEN.
- Environment: macOS (darwin), Node v24.21.0 from nvm. `.nvmrc` asks for 22.14.0, which is NOT installed here. Fresh clone in a mktemp dir, `npm ci` from the lockfile (exit 0). Playwright Chromium was in the cache (chromium-1243). The scratch dir was deleted at the end.

## Commands
| Command | Exit | Result |
|---|---|---|
| npm ci | 0 | — |
| npm run lint | 0 | — |
| tsc --noEmit | 0 | — |
| vitest run | 0 | 26 files, 869 passed, 0 skipped |
| npm run check:hygiene | 0 | — |
| npm run build | 0 | — |
| playwright security-headers.spec.ts (E2E_LOCAL_PORT) baseline | 1* | 10 passed, 0 failed |
| same with `'unsafe-inline'` added to script-src (rebuilt) | 1 | **4 failed / 6 passed**: red as required; file restored |
| vitest components/ui with M1 (aria-invalid removed) | 1 | 1 failed / 50 |
| M2 (Toast `message = "Saved"` default) | 0 | 51 passed: **stays green** |
| M3 (aria-labelledby removed from Dialog) | 1 | 1 failed / 50 |

\* Exit 1 at baseline comes only from the harness floor guard. A one-spec run collects 5 tests per project and the floor is 9. The run itself had 0 failures, and the harness stamp said OK with 10 results. The mutated run is red on real test failures. The builder recorded 8 failed. My run had 4 failed. Either way the run goes red.

## Results
- **A PASS.** The diff has 24 files: 17 components in components/ui, 3 test files, design/HANDOFF.md, design/CATALOG.md, and one comment line each in design/tokens.css and components/icons/registry.ts. It does not touch package.json, the lockfile, .github, e2e or the generated client. Nothing is deleted except those two comment lines, and there is no skip.
- **B PASS.** File key `JXgRItauynmT0g8vSJB3oR` and revision `2026-09-20` match figma/README.md lines 11–15. I checked every node id in HANDOFF.md mechanically. All of them appear in README.md or FIRST-SLICE-*.md. That covers collections 2:2/2:51/3:2 and modes, 22 component rows, and 40 icon rows, with each icon's export appearing on the same line as its node. I spot-checked these for meaning: 7:146, 9:42, 10:66, 10:144, 11:79, 16:43, 17:40, 12:263, 15:31, 30:770, 5:147, 28:585. The variant properties match §5 verbatim. The rows that say "no node id" (text styles §3.1, elevation §3.2) are truly absent: README lines 210 and 231 list those styles without ids. No node id was invented.
- **C PASS.** All variants are present and none is invented for Dialog (Standard and Destructive), Toast (Success, Error, Info), Switch, Tabs, Checkbox (Off, On, Mixed) and TextField (the 5 states). Accessibility in the real markup:
  - All actions are native buttons or inputs.
  - TextField sets aria-invalid and aria-describedby pointing at the error id, and shows an icon plus text.
  - Toast has no default message (it is required by the type), and its Error tone uses role=alert.
  - Dialog is a native `<dialog>` opened with showModal, labelled with aria-labelledby, autofocuses Cancel, and returns focus to the opener in cleanup.
  - Tabs use roving tabindex with Left/Right/Home/End.
  - Switch is `input type=checkbox role=switch`.
  - Nothing in app/, components/shell or lib/ imports components/ui, so no production route renders these components and there can be no mock data or dead control on a route.
- **D PASS.** The counts are above. M2 stays green, which is a follow-up and not a block: the negative case is not a ledger case, and the required `message` type still stops a call that omits the message.
- **E PASS.** I reproduced the CSP mutation locally: red with the mutation, green when restored.
- **F PASS.** CI e2e run 43230757364 "Browser lane": 42 passed. shell.spec ran in desktop-chromium-1440 and mobile-chromium-390, with both the light-palette and dark-palette token tests in each. The log shows no failed, flaky or skipped tests outside the canary job, where failures are the expected result. No ledger case requires components in a browser.
- **G PASS.** On fa99ca3: ci-required, frontend-ci, contract-ci and e2e succeeded. supply-chain (deps-scan and image-scan) failed, but required-checks.txt leaves it out on purpose, and this PR changes no dependency.

## Findings
- BLOCKING: none.
- FOLLOW-UP (one batched vizra-user item): (1) no test fails when a default success message is added to Toast (M2); (2) Dialog focus return and showModal are not exercised in a browser until a route renders the Dialog.

## Ledger answer
With #11 and #13 on main, these parts of the outcome are delivered: tokens (semantic colour light and dark, scale, type, elevation), 17 of the design's 21 §5 components with their variants and states, the typed Lucide registry with a pinned-export test, and the Figma mirror with file key, revision and node references.

These parts are not delivered:
- PhotoCard, TabBar Item and TabBar are PLANNED.
- TopNav was superseded by TopNav/M1, which is only PARTIAL.
- There is no brand mark. Owner inbox 20 has to decide it.

`evidence_required` is met: HANDOFF.md is a design handoff record with node references, and every id checks out. VZ-DESIGN-001 should not be recorded IMPLEMENTED as a whole yet. Record it IN_PROGRESS (with this PR's slice IMPLEMENTED and verified) until inbox 20 settles the brand mark and PhotoCard and TabBar land.

## Not run
- The full local e2e suite (only security-headers was run; the browser lane comes from the CI log).
- Node 22.14.0 (not installed).
- Docker image build.

FINAL VERDICT: PASS — SHA fa99ca384af1fe7dfc3d2affdefc7d25ead4d0ef
