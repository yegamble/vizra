# VERIFY — meta PR #37: VZ-DESIGN-001 IMPLEMENTED status record

- PR: https://github.com/yegamble/vizra/pull/37 — head `b7a373454753ad02434937c8d53097d96b220690` (matches `gh pr view 37 --json headRefOid` at both the start and the end)
- Verifier: independent (did not write the record). Budget QUEUE-ledger-VZ-DESIGN-001, verdict 1.
- Environment: macOS darwin, Python 3.9.6, Node v24.21.0, Playwright chromium from vizra-user devDependencies (@playwright/test 1.63.0). Clones: /tmp/vzv-vizra-pr37-dh3ra4/{meta,user}, deleted after.
- vizra-user main at `9f7c639cf2702ce6a95395a7876f5d51679acff1`.

## Part 1: the record

(a) **Diff scope: PASS.** `git diff --stat origin/main...HEAD` touches only `docs/evidence/ledger-generator/status_records.json` (+39), `docs/issues/VZ-ISSUE-008.md` (+4), `docs/quality/features.json` (+51/-5, generated).
| command | exit | result |
|---|---|---|
| `bash scripts/check-generated-ledger.sh` | 0 | reproduces byte-for-byte in UTF-8 and C/POSIX locales; statuses IMPLEMENTED 2, PLANNED 190 |
| `python3 scripts/check-ledger-status-output.py` | 0 | 192 entries, 2 records, sets equal |
| `python3 scripts/check-ledger-status-remote.py` | 0 | 33633d4, 0bb8dc6, 77c4738 are all on vizra-user main |
| `python3 -m pytest -q docs/evidence/ledger-generator/test_status.py` | 0 | 38 passed, 0 skipped |
| `python3 -m pytest -q docs/evidence/ledger-generator/test_ledger_status_remote.py` | 0 | 3 passed |

(b) **Bullets: PASS.** The 3 bullets are `(VZ-DESIGN-001) ` + outcome, + success[0], + negative[0], each identical character for character to the features.json entry. The evidence_required line is also verbatim.
Scope judgement on owner decision 2026-11-12 #5: #5 grants adding "a ledger ID and its ledger cases (copied word for word)… when no issue lists that ID". VZ-ISSUE-008 already listed the ID; the record adds only the verbatim cases. That is less than #5 grants. It is not a change of the acceptance target, because the issue already bound to "the ledger entries above (success / negative…)". Within #5 (a fortiori). The literal wording gap is filed as a follow-up.

(c) **Rationale claims: PASS.** All checked on vizra-user main:
- `design/tokens.css` and `design/tokens.test.ts` are present.
- `components/icons/registry.ts` and `registry.test.ts` are present. `npx vitest run components design` gives 6 files, 231 tests passed, 0 skipped.
- Closed union: `components/icons/icon.typecheck.tsx` carries `@ts-expect-error` cases. Base `npx tsc --noEmit` exits 0. My mutation (`<Icon name="notARealIcon"/>` in a temporary file) gives TS2322 "not assignable to type '"search" | …'". Removed afterwards; clean tree.
- Section-5 components: every node id in meta `docs/design/figma/README.md` §5 (7:146 … 17:96, 15 component sets plus the page ids) appears in `design/HANDOFF.md` §2, each with a repo file under `components/ui/` or `components/shell/`. TopNav/AppBar M1 are PARTIAL, mapped to TopBar/SkipLink. The rationale says only "has a file", which is true.
- Wordmark: `components/shell/TopBar.tsx:23-32` renders the text "Vizra" (seen in the browser below). This is consistent with owner decision 2026-11-12 #6 (quoted on main).
- HANDOFF.md carries the Figma file key `JXgRItauynmT0g8vSJB3oR`, design revision `2026-09-20`, and node ids for tokens, components and icons.
- The prior PASS evidence files are cited and exist on meta main, as the brief states.

(d) **Merges: PASS.** From `gh pr view`:
- vizra-user #11: MERGED, head 505fb28…6c6, merge 33633d4…505
- vizra-user #13: MERGED, head fa99ca3…ef, merge 0bb8dc6…eac
- vizra-user #15: MERGED, head 4f99186…f6, merge 77c4738…7e6

All six full SHAs equal the record's.

## Part 2: queue 14 (vizra-user main, production server)
Commands: `npm ci`, `npm run build` (ok), `npx next start -p 3917` (PIDs 90766 and child 90810, both killed by exact PID; port free afterwards). Driver: Playwright chromium script at 1440x900 and at 390x844 (isMobile/hasTouch). Nothing was signed in; no credentials or signed URLs were used.
- **CSP:** the response carries an enforcing `content-security-policy` with `script-src 'self' 'nonce-…' 'strict-dynamic'`, a nonce style-src and `frame-ancestors 'none'`. The nonce differs per request. nosniff, Referrer-Policy and Permissions-Policy are present.
- **Console/network:** 0 console errors or warnings, 0 pageerrors, 0 failed or ≥400 requests at both viewports.
- **Wordmark:** "Vizra" is visible in the header at both widths (shell-*.png).
- **Keyboard:** Tab order is the same at both widths.
  1. Skip to content: focus outline solid 2px rgb(0,91,180). Enter moves focus to `MAIN#content`.
  2. Vizra → `/`: focus outline solid 2px. Enter goes to `/`.
  3. `/health` link: focus outline solid 2px. Enter goes to `/health`.
  4. The next Tab leaves the document.

  The shell has only links, no buttons, so Space does not apply.
- **CSP mutation** (`lib/security/headers.ts`, `'unsafe-inline'` appended to script-src):
  - Base `npx vitest run lib/security/headers.test.ts`: 19/19 passed.
  - Mutated: 4 failed, exit 1 (e.g. "has no unsafe-inline, unsafe-eval or wildcard source in ANY directive in production").
  - Restored: `git diff` is clean, 19/19 passed.
  - The e2e security-headers spec was not mutated: the unit test was enough for the demonstration.
- Screenshots and driver log are in `docs/evidence/warroom/2026-11-12-meta-pr37-design-001-shots/`: shell-desktop.png, shell-mobile.png, focus-{desktop,mobile}-{0,1,2}.png, drive.log.

**queue 14: PASS** (Chromium only).

## CI
`gh pr checks 37` was polled from about 17:2x to the 15-minute limit. Throughout, `ci-required` was **pending** (run 43267968651) and `validate` was **pending/in_progress** (run 43267968116, headSha b7a3734…). GitGuardian passed. A required check that has not completed is not a pass.

## Findings
- BLOCKING: none.
- FOLLOW-UP (1): owner decision 2026-11-12 #5 literally covers only "IDs no issue lists". Have the owner confirm it also covers adding the verbatim cases for an ID an issue already lists (as VZ-ISSUE-008 / VZ-DESIGN-001 did here).

FINAL VERDICT: BLOCKED — SHA b7a373454753ad02434937c8d53097d96b220690 — missing input: ci-required (run 43267968651) still pending after the 15-minute poll window; every other check PASS. Re-poll and convert to PASS once ci-required is green on this SHA.
