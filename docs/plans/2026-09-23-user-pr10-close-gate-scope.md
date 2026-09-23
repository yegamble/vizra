# Execution plan: VZ-FOUND-008 (security seat Q3/F14) — close vizra-user PR #10 FINDING 9

## Context
- Repo: `yegamble/vizra-user`, PR #10 "Lane A pixel channels off", branch `fix/lane-a-pixels-off`.
- Base head: `b68294b027965b6df57e3705d3b15631bafd4873` (fix round 2 of 2, by another builder). This builder is fresh and did not write it.
- Worktree: `/Users/yosefgamble/github/vizra/.claude/worktrees/user-pr10-close` (local branch `close/pr10-work` tracking `origin/fix/lane-a-pixels-off`).
- Finding: meta `docs/evidence/warroom/2026-09-23-vizra-user-pr10-pixels-off-VERIFY.md`, "Re-verification at b68294b", G3/G4/FINDING 9.
- Rules: sentinel R1, R5, R6, R14.

## Acceptance
One commit, fast-forward push, no force:
1. Gate (`scripts/ci/redact-artifacts.sh`) additions, fail closed, path named, content never echoed:
   - refuse any file or archive member containing `data:image/` or `data:video/` (case-insensitive, `\/`-escaped too);
   - refuse any symlink (and any other non-regular, non-directory entry) under the uploaded paths, and inside an opened archive (zip -r follows symlinks on repack);
   - refuse any archive the gate does not open: an archive inside an archive (any kind), and at top level any archive not named `*.zip` (by name or signature: zip, gzip, bzip2, xz, zstd, 7z, rar, ustar tar).
   Each has a unit case red on b68294b's gate, green now.
2. D25 end to end: a harness spec serves an inline data-URI image (tiny synthetic PNG) and fails; the gate refuses; 0 uploaded. Mutation "data-URI refusal off": it uploads. Restored: refused again.
3. AGENTS.md: three overstated sentences replaced with the verifier's G3 scope statement, adjusted; limits stated (BMP/TIFF/ICO/offset/hex; post-gate writes; diagnosability cost once the app fetches images).
4. Ledger: `mutation-digests.txt` redact-artifacts.sh lines recomputed by `demonstrate.sh`; every other line byte-identical.
Non-goals: detecting arbitrary image encodings; post-gate writes (the `run:` class).

## Verification
Node 22.14.0 (`.nvmrc`). `npm ci`; `npm run ci`; `bash scripts/ci/require-checks_test.sh`; `bash scripts/ci/check-e2e-lane.sh .github/workflows/e2e.yml`; Lane A (`E2E_LOCAL_PORT=… npm run e2e` per COMMANDS); `npm run e2e:demos`; `node scripts/ci/harness-canary.mjs`. Unit red run of the new cases against b68294b's gate (copied in), green on the new gate.

## Progress and evidence
(appended below as work proceeds)

## Blockers and handoff
None at start.

### 2026-09-23 progress (builder, worktree user-pr10-close, base b68294b, Node 22.14.0, macOS arm64)
- Preflight: node v22.14.0 (nvm, matches .nvmrc), npm ci exit 0, docker 29.8.0, Chromium 1243 installed, zip/unzip/perl/shellcheck/gh present. Disk ~13 GiB free. Local grep/find are BSD (CI GNU).
- Unit RED on b68294b gate (sha 97627fe1…): `npx vitest run e2e/harness/upload-gate-pixels.test.ts` exit 1, 9 failed / 7 passed (all new cases rc 0 = escaped).
- Unit GREEN on new gate: 16/16; with redaction-corpus 162/162.
- Measured: a real red Lane A run writes data:image/ only in playwright-report/index.html and playwright-report/trace/assets/codeMirrorModule-*.js (Playwright's own viewer, never uploaded) -> exact-path exemption, pinned by a unit case; mutation removing it -> real tree rc 4.
- D25 probe: gate rc 4 naming trace.zip::1-trace.trace and resources/<sha1>.html; error-context.md carries none.
- Mistake recorded: a `git checkout -- scripts/ci/redact-artifacts.sh` after the red run discarded the gate edits once; re-applied from the same patch, backed up in scratch.
- Not changed on purpose: e2e/harness/recorders.ts:44 comment still says "refuses any image or video" — the file is hashed in the ledger (D23b/D24d) and the brief requires those lines byte-identical.

### Verification (tree = commit 03baf75e8af0c204eb7a7c7a2243e2d5bdeebbf6, Node 22.14.0, Playwright 1.63.0, macOS arm64)
| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | 0 vulnerabilities |
| `npx vitest run e2e/harness/upload-gate-pixels.test.ts` with the b68294b gate | 1 | 9 failed / 7 passed (RED) |
| same + redaction-corpus, new gate | 0 | 162 passed (GREEN) |
| `npm run e2e:demos` (DEMO_PROD_PORT=3941, DEMO_IMAGE=pr10close-user:demonstrate) | 0 | 176 halves passed, 0 blocked, 0 failed; D25a/b/c ok |
| `npm run ci` | 0 | 21 files, 670 tests passed, 0 skipped; hygiene 332 sources, 25 digest lines (340 sources after adding the unit transcripts) |
| `bash scripts/ci/require-checks_test.sh` | 0 | 246 cases, 253 assertions, 0 failed |
| `bash scripts/ci/check-e2e-lane.sh .github/workflows/e2e.yml` | 0 | OK |
| `E2E_LOCAL_PORT=3943 npm run e2e` (Lane A) | 0 | 18 passed; floor 9/9 9/9; 18 stamps |
| `node scripts/ci/check-coverage-floor-ran.mjs` | 0 | OK, 18 verified |
| `E2E_LOCAL_PORT=3944 node scripts/ci/harness-canary.mjs` | 0 | all 4 fixtures failed with exact kind sets |
- Pushed as a fast-forward b68294b..03baf75 to fix/lane-a-pixels-off. CI: pending at the time of writing (see the final report).
- Ledger: the three D24e lines changed (bf820b0e… BEFORE/RESTORED, 528b9284… MUTATED); three D25b lines added (bf820b0e…, 83a85e46…, bf820b0e…); all other lines byte-identical.
- Transcript churn in the other D-rows is port (3391 -> 3941) and volatile run data only.
- Docker image pr10close-user:demonstrate removed.

### Chair ruling round (2026-09-23): recorders.ts:44 and any other absolute claim
- Commit 5c5c971ea8980c1ae44a3716f2d0b73ee54fe50b on 03baf75, fast-forward.
- Grep outside docs/evidence ("any image", "no image", "never uploaded", "whatever produced it", "refuses any", "holds regardless"): two gate claims found and scoped: e2e/harness/recorders.ts:43-45 and e2e/harness/test.ts:148-150. Remaining hits are the recorder-config policy ("Lane A records NO PIXELS"), negations ("not a proof that no pixels are present"), gate-OK-message assertions, the page-snapshot gate (ci-environment.ts:94), and unrelated text.
- test.ts is also hashed in the ledger (D13q/D15i/D15j), so its 6 lines changed too, as forced by the edit; flagged to the chair.
- Ledger diff vs 03baf75: 12 lines changed (6 recorders.ts, 6 test.ts); 17 lines byte-identical.
- npm ci 0; npm run e2e:demos 0 (176/0/0); npm run ci 0 (670 tests, 0 skipped, 25 digest lines); require-checks 0 (246/253/0); lane guard 0; Lane A 0 (18 passed, floor 9/9 9/9, 18 stamps); floor check 0; canary 0.
