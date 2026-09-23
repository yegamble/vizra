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
