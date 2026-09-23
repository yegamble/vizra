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

---

## RE-PLAN (2026-09-23, fresh builder): flip the upload gate to an ALLOWLIST (chair ruling, defect class R3)

**State: PLANNED. Awaiting the chair's go, after the security seat reviews this section. No code has been written.**

- Repo `yegamble/vizra-user`, PR #10, branch `fix/lane-a-pixels-off`, base head `5c5c971ea8980c1ae44a3716f2d0b73ee54fe50b`. The builder is fresh and wrote none of the earlier rounds.
- Read-only worktree for measurement: `.claude/worktrees/user-pr10-allowlist` (detached at 5c5c971). Step B will commit there as fast-forward commits on `fix/lane-a-pixels-off`, and never force-push.
- Inputs:
  - the verifier's § "Re-verification at 5c5c971": FINDINGS 10–15, plus FINDING 9 and the G3 table;
  - sentinel `docs/sentinel/pr/vizra-user-pr10-5c5c971.md`: F-1…F-6 and Q-1…Q-4;
  - `docs/sentinel/RULES.md`: R1, R3, R5, R6, R7, R11, R14 and R23.
- Acceptance: VZ-FOUND-008 (security seat Q3/F14). The ledger's acceptance text is NOT changed here; see "Flags for the chair".

### A. Threat model, stated so the claims can be scoped (R1)

The public Lane A artifact must never publish something the lane captured by ACCIDENT: pixels a page showed, fetched or inlined; trace/HAR bodies; signed URLs.

A spec author who DELIBERATELY encodes data into the spec's own stdout or error message is not stopped by any artifact gate. That author can also send the data over the network from the runner. This is the `run:` class, and review is its control. Every claim below is scoped to this model.

### B. Design

**B1. The upload publishes exactly one directory, the staging directory `e2e-artifacts/`, which the gate creates.**
- The gate stages exactly two TEXT shapes, and nothing else:
  - `playwright-report/results.json` (required: exit 3 if it is absent, as today for a missing tree);
  - `test-results/<dir>/error-context.md`, at depth exactly 1, where `<dir>` does not start with `.`.
  Both are staged at their same relative paths under `e2e-artifacts/`.
- These are not uploaded: `trace.zip`, the HTML report, `*.har`, any archive, `.last-run.json`, `browser-signals.json`, screenshots, video, `playwright-browsers.txt`, and anything a spec writes. They need no detection, because they are not staged.
- Traces, the HTML report and pixels are Lane B's (PR B, planned separately).
- **Proposed and NOT added silently:** no third file. The harness's `browser-signals.json` is not needed in the artifact. Every failing test's message already carries its records, as measured below ("2 DURING THE TEST: [response] http 404 … <redacted: 2 parameter(s)>"). For a passing test the records are "none".

**B2. Stage by content. The gate copies BYTES into a fresh directory and edits nothing in place.**
- If `e2e-artifacts/` already exists in any form, the gate refuses (exit 6), because anything already in it would be published.
- The gate `mkdir`s the directory and checks that call's status.
- Traversal is TOCTOU-safe:
  - `lstat` each directory, which must be a real directory and not a link;
  - `chdir` into it, and compare `stat(".")` dev/ino with the `lstat`;
  - open each candidate with `O_NOFOLLOW`, `fstat` it (it must be a regular file), and read at most cap+1 bytes;
  - write the staged copy with explicit `open … or die` / `print … or die` / `close … or die`.
- The source tree is never written. FINDING 14's `perl -pi` "Can't do inplace edit" exit 0 cannot recur, because there is no in-place edit.
- Anything written after the gate into `test-results/` or `playwright-report/` cannot be published: the upload reads only `e2e-artifacts/`.

**B3. Every staged file must pass all of the rules below, or the WHOLE upload is refused.** The checks run on the FINAL bytes, after URL redaction. The gate names the path and the rule, and never echoes content.

| Rule | Value | Measured basis |
|---|---|---|
| Regular file | `lstat`, then `O_NOFOLLOW` + `fstat`. A link or other non-regular file named `error-context.md` / `results.json` refuses the upload (exit 5). A symlinked `<dir>` or root is not traversed, so nothing under it is staged. | FINDING 9/12, G3 symlink rows |
| Size cap | `results.json` ≤ 8 MiB; each `error-context.md` ≤ 256 KiB; at most 500 `error-context.md` files | real maxima 143,806 B and 2,554 B; 36 results per full CI red run today (18 tests × retry 1) |
| Valid UTF-8 | strict decode (`Encode` `UTF-8`, FB_CROAK) | all 21 real files valid |
| No control bytes beyond TAB and LF | refuse C0 except 0x09/0x0A, DEL 0x7F, and C1 U+0080–U+009F (CR and ESC included) | 0 control bytes in all 21 real files |
| **No long encoded run** | no maximal run longer than **N = 89** characters of ANY one of: base64 `[A-Za-z0-9+/]`, base64url `[A-Za-z0-9_-]`, hex `[0-9A-Fa-f]` | see B4 |
| `results.json` is JSON | strict parse (JSON::PP); an unparseable file refuses the upload | R5 |
| URL redaction still applied | the four shared programs of `redaction-patterns.json` plus the HAR `queryString` program, on the staged copies | corpus unchanged |
| Page snapshot | a `# Page snapshot` heading line in a staged file refuses the upload (exit 1), as before | D16a/D17 |
| Fail closed (R5) | any error from `opendir`/`lstat`/`open`/`read`/`write`/`close`/`mkdir` or a perl `die` makes the gate exit 2. A missing `test-results/` means 0 contexts, not an error. A missing `results.json` exits 3. | FINDING 14 (mode-000 dir; read-only dir) |

**B4. The measured N.** Longest maximal run per alphabet, in real red-run files:

| Source | Files | With JSON-reporter attachment bodies | Without bodies |
|---|---|---|---|
| Real CI artifact `playwright-artifacts-35536837315-1` (id 10612777314, GitHub `ubuntu-24.04`, 2026-09-20, commit e67c35f; downloaded with `gh api`) | `results.json` 61,518 B; 4 × `error-context.md` 1,422 B | std **695**, url **695**, hex 40 (all from a `browser-signals.json` body, base64) | std 52 (`user/commit/<sha>`), url **89** (output dir `…-desktop-chromium-1440-retry1`), hex 40 (commit sha) |
| Local red run at 5c5c971 (Node 22.14.0, PW 1.63.0, `CI=1 PLAYWRIGHT_NO_COPY_PROMPT=1`, full lane plus a temporary 4-test failing spec that was never committed and has been deleted: text assertion, 404 through the guard, locator timeout, thrown error; 18 passed, 16 failed results) | `results.json` 143,806 B (34 bodies, all `browser-signals.json`); 16 × `error-context.md` 1,120–2,554 B | std 878, url 415, hex 64 | std **64**, url **89**, hex **64** (the harness stamp, an HMAC-SHA256 in hex) |
| `error-context.md` alone, both sources | 20 files | — | std ≤ 18, url ≤ 21, hex ≤ 6 |

- **Consequence 1, a harness change.** The JSON reporter inlines every `testInfo.attach(…, { body })` as base64 (`playwright/lib/runner/index.js:4212`). The harness's own `browser-signals.json` body would therefore refuse EVERY red run. So `e2e/harness/test.ts` attaches `browser-signals.json` by `path` (a file in the test's output directory), not by `body`, and `results.json` then carries only its path.
- **Consequence 2, N = 89 is derived, not guessed.**
  - The one legitimate run near the bound is Playwright's output directory name inside `attachments[].path`: `trimLongString(…, 60)` (`workerProcessEntry.js:904`, `windowsFilesystemFriendlyLength = 60`) + `-` + the longest project id `desktop-chromium-1440` (21) + `-retry1` (CI `retries: 1`) = **89** exactly, measured 89 in both sources.
  - The next legitimate maxima are 64 (the stamp) and 52.
  - A longer project id, retries ≥ 10 or `--repeat-each` would exceed 89 and refuse the upload, which fails CLOSED. A future long hyphenated slug in an error message could as well. This is a stated cost.
- **What N = 89 catches:**
  - unseparated base64 or base64url of ≥ 67 bytes (67 bytes is the smallest valid PNG, which encodes to 90 characters);
  - unseparated hex of ≥ 45 bytes;
  - the synthetic 70-byte 1×1 PNG used in the tests (94 characters in base64 and in base64url, 140 in hex).
  This covers the encoded shapes Playwright and Chromium write unprompted into these two files: a `data:` URI of ANY media type in an error's received value or in stdout, a JSON attachment `body`, a stdout `buffer`, and a HAR-style `"encoding":"base64","text"`.
- **What N = 89 does NOT catch (stated, R1):**
  - encodings a spec writes WITH separators: MIME base64 wrapped at 76, Node's `<Buffer 89 50 4e …>` in `console.log`, decimal byte arrays, base85/Z85 (whose punctuation breaks the runs);
  - binaries below the sizes above (a 1×1 GIF, 35–43 B, in base64 is not detected);
  - text the page renders as TEXT, such as a received `toHaveText` value or page words. This is error-message content, which is uploaded as before.
- A per-alphabet tightening (std 64, hex 64, url 89) is possible. It is not proposed, because the chair asked for one stated N.

**B5. The lane guard and the workflow (`check-e2e-lane.mjs`, `e2e.yml`, `e2e-pinned-steps.yml`).**
- The redact pin becomes exactly `bash scripts/ci/redact-artifacts.sh`. The sources and the staging name are fixed in the script, and it refuses any argument.
- The record-browsers pin drops `| tee playwright-browsers.txt`: the revision still prints to the job log.
- The upload pin's `path:` must be exactly one entry, `e2e-artifacts/`. `ALLOWED_UPLOAD_PATHS = { "e2e-artifacts/" }`.
- The `playwright-browsers.txt` token stays in MENTIONS, so any step that names it is refused. A new `e2e-artifacts` token is claimed only by `upload`, so a `run:` step that writes into the staging directory is refused by name. That comes on top of "upload IMMEDIATELY follows the redaction".
- **Q-1 is closed for uploader and `path:` actions across the repository.** The guard sweeps EVERY workflow file (as it already does for `.vizra-e2e`). Any step with a `with.path`, or whose `uses:` looks like an uploader (UPLOADER_MENTION), must be one of three allowlisted (file, path) pairs:
  - (`e2e.yml`, `e2e-artifacts/`);
  - (`supply-chain.yml`, `npm-audit.json`);
  - (`supply-chain.yml`, `trivy-image.json`).
  Anything else is refused by name. That covers `actions/cache` and a new workflow uploading `test-results/`.
- Stated as NOT closed: a new workflow whose `run:` publishes (`gh`, `curl`), or a third-party action whose input is not `path`. Both are the `run:` class.

**B6. R7: `recorderProblems` screens the resolved `_combinedContextOptions`.**
- `_combinedContextOptions` is Playwright's effective, test-scoped merge `{ ...contextOptions, ...options }` (`playwright/lib/index.js:264-345`). It is copied into EVERY `browser.newContext` of the test (`runBeforeCreateBrowserContext`, :122-126).
- A value passes only if all of these hold:
  - it is a plain object (prototype `Object.prototype`, not a Proxy);
  - it has no OWN property `recordHar` or `recordVideo`, of any descriptor kind;
  - `Object.prototype` has no `recordHar` or `recordVideo` at check time (an inherited key would reach Playwright's `options.recordHar` read).
- It is named `contextOptions` in the message and never echoes a value.
- Only `vizraHarnessGuard` can take it, because the fixture is test-scoped. `vizraWorkerGuard` keeps its three options.
- Measured order: the default context already exists when `vizraHarnessGuard` runs, since it depends on `context`. No page exists yet. D27 measures what, if anything, is written.
- A `test.use({ contextOptions })` and a `test.extend({ _combinedContextOptions })` override are both screened, because the harness fixture receives the resolved value.
- If a probe shows that a user fixture cannot depend on the boxed `_combinedContextOptions`, I fall back to the public `contextOptions`, state the private-override residual, and report it.
- **F-5:** a unit case `{ mode: "retain-on-failure", sources: false, screenshotz: undefined }` must give `["trace"]`, which kills the `|| !known` mutant.
- The gate stays the control, and this stays the early one.

**B7. Stated residuals, the new wording.**
- **A process a spec leaves running can write INTO `e2e-artifacts/` between the gate and the upload.** Every process on a hosted runner shares the runner user and passwordless sudo, so no in-job permission trick stops a deliberate writer. The mitigations are adjacency (the upload immediately follows the gate), the pinned steps, and review; this is the `run:` class. **The chair's phrase "anything written after the gate … cannot be published" is therefore scoped to writes into `test-results/`/`playwright-report/`**, and I ask the chair to accept that scoping.
- What the staged files still carry: error messages (received values, page text), stdout/stderr, test titles, redacted URLs, and runner paths. The hard rule "no spec may authenticate" stays, unchanged.

### C. R1: claims rewritten (each to "Lane A publishes only the two allowlisted text shapes, each checked by B3, and states B4's limits")
- `AGENTS.md` § Artifact privacy, rewritten from "WHAT A RED LANE A ACTUALLY PUBLISHES" through "What PR A's controls still guarantee":
  - the published table becomes two rows;
  - "What the gate refuses, exactly" becomes B3 + B4;
  - the NOT-covered table is re-scoped: trace channels are no longer published by Lane A;
  - :182 (the COMMANDS row, "anywhere in what would be uploaded"), :214 ("holds regardless", FINDING 13), :774, :777, :826, :830-831 ("covers everything … an image a page inlines", FINDINGS 10/11, F-2), :843, :846 ("any spelling"), :947-948, :963-969 and :1062-1064 are all rewritten or removed;
  - § Pins: "prints … into its artifacts" becomes "into its job log".
- The gate's own header and comments (the old :199-465 detectors go).
- `e2e.yml` comments:
  - :164-172 (redaction);
  - :193-195 "Traces, screenshots and videos";
  - :200-206 "retained traces";
  - :224-229 `test-failed-1.png`/`video.webm`;
  - :231-237 "PRIVATE repository" (F-3), which becomes PUBLIC.
- `e2e-pinned-steps.yml`:110-111 (F-1 premise) and :119-138.
- `eslint.config.mjs`:147 "traces and screenshots".
- The comments in `recorders.ts`:29-48 and `test.ts`:141-150.
- The `check-e2e-lane.mjs` comments that describe the old upload (:142-158, :1075, :1119-1175).
- `docs/evidence/VZ-FOUND-008/README.md` index.
- PR body: a current summary covering 03baf75, 5c5c971 and this round. The unscoped § 1 heading and the § 3 bullet are removed.
- Grep list for acceptance, run outside `docs/evidence`, each hit judged: "any image", "holds regardless", "of any kind", "anywhere in what would be uploaded", "any archive", "whatever it is called", "whatever its name or kind", "no unopened archive", "everything Playwright", "image a page inlines", "never uploaded", "PRIVATE repository", "screenshots and videos".

### D. Tests that must be able to fail (R11)

**D1. Unit regression file `e2e/harness/upload-gate-allowlist.test.ts`.** It replaces `upload-gate-pixels.test.ts`, whose cases assert the removed detectors.
- It uses ONE oracle for every case: `published(tree)`.
  - For the new gate: every file under `e2e-artifacts/` if the exit code is 0, else ∅.
  - Under `VZ_GATE_LEGACY=<gate file>`: the 5c5c971 semantics. That means `redact-artifacts.sh test-results playwright-report`, then, if the exit code is 0, `test-results/` + `playwright-report/results.json` + `playwright-browsers.txt`, with links followed as the pinned upload action does.
- Each case asserts two things:
  - every published path matches the allowlist grammar, and every published file passes B3;
  - no published byte carries the planted marker or the fixture in any encoding (raw signature; std/url base64 at the 3 alignments; hex lower/upper).
- RED = the committed file run with `VZ_GATE_LEGACY` pointing at the 5c5c971 gate: assertion failures, not errors. GREEN = the new gate. Both transcripts are kept.
- The cases:
  - **G3:** PNG/JPEG with 1 leading byte; zip-in-zip; a zip named `a.dat` and `trace.zip.bak`; `a.png.gz`, `a.dat.gz`, `a.tar`; a data-URI PNG in `error-context.md` (refused by N); base64 PNG in `results.json` stdout (refused); a `results.json` attachment typed octet-stream with a base64 body (refused); SVG with an embedded raster; a trace member with 1 leading byte; BMP/TIFF/ICO; a symlink to a file and to a directory; a hex dump in `a.txt` (not staged) and in `error-context.md` (refused by N); a PNG written into `test-results/` AFTER the gate (not published).
  - **FINDING 10:** lz4, brotli, `.Z`, lzma, cpio, ar, zlib and raw deflate as `x.dat`, under their own names, and as trace members; a zip with a leading byte, both at top level and as a member. These use synthetic signature + PNG bytes, or `node:zlib` for zlib/deflate/brotli.
  - **FINDING 11:** `data:application/octet-stream;base64` and `data:;base64` in trace members (not staged), and in `error-context.md`/`results.json` (refused).
  - **FINDING 12 / F-1:** `playwright-browsers.txt` as PNG bytes and as a link (not published).
  - **F-2:** `test-results/zz/net.har` with an embedded PNG (not staged); HAR-style base64 text in `results.json` (refused).
  - **FINDING 14:** a mode-000 directory holding `error-context.md` (exit 2, with an assertion that the chmod took effect); a mode-000 `error-context.md` (exit 2); a mode-555 directory holding `error-context.md` with `?X-Amz-Signature=VZSECRET…` (published copy redacted; legacy: the value is published); the root made read-only so `mkdir` fails (exit 2); `ulimit -f` so the staged write fails (non-zero).
  - **New shapes:** a pre-existing `e2e-artifacts/` (exit 6); `test-results/a/b/error-context.md` and `test-results/t/notes.md` (not staged); `test-results/.h/error-context.md` (not staged); a symlink named `error-context.md` to an outside TEXT file with a marker (exit 5); invalid UTF-8 (Latin-1 0xE9); ESC and NUL; a 9 MiB `results.json`; 501 contexts; unparseable `results.json`; a run of exactly 89 (passes) and of 90 (refused), for each alphabet.
- **Inverse controls:**
  - a tree built from the measured real shapes passes with exit 0, and stages exactly `results.json` + N contexts, with the URL redacted;
  - a `results.json` carrying a 64-hex stamp and an 89-character output-directory path passes;
  - a missing `test-results/` stages only `results.json`.

**D2. One mutation per new rule, run by `demonstrate.sh` (new D28).** Each is a `perl` edit of the gate or the guard. The `cmp` check proves the file changed. The named case must go red on an assertion (the transcript is checked for the case name and for no `SyntaxError`/`command failed`), and the digests are recorded:
- regular-file check off;
- size cap off;
- UTF-8 off;
- control bytes off;
- long run off, one mutation each for std, url and hex;
- allowlist widened (any depth / any `*.md`);
- freshness off (`mkdir -p`);
- fail-closed off (`lstat` error ignored);
- URL redaction skipped;
- page-snapshot refusal off;
- JSON parse off.
- Guard (D29, `require-checks_test.sh` red): the pinned upload path check off; the repo-wide (file, path) sweep off (Q-1).
- Recorders: the `contextOptions` screen off; `|| !known` removed (unit, F-5).

**D3. `demonstrate.sh` D-rows retargeted (R23).** Every old pattern is re-pointed or replaced, and each mutation is proven live by `cmp`:
- D9: run the gate, then sweep `e2e-artifacts/`. The run gets `--reporter=list,json` with `PLAYWRIGHT_JSON_OUTPUT_FILE` (to be verified), because the demos configuration has no JSON reporter.
- D16a: new command.
- D16d: the upload set becomes the staging directory.
- D17b/c/d: the "upload set" counts become staging after the gate. D17c's `|| true` pattern is moved to the new pin text.
- D24: `gate_then_upload` means staging. D24e's dead `refuse_pixels() {` mutation becomes "stage every file, check nothing" (pixels published, RED), then restored (0).
- D25: the spec fails with a received value carrying the typed data URI, so the gate refuses by N and nothing is published. D25b: the long-run rule is off, and the base64 image IS published (RED). D25c: restored.
- **New D26, end to end.** A real failing spec whose page shows a typed data URI, an untyped (`application/octet-stream`) data URI and a fetched PNG, and which records a HAR (`content: "embed"`) through a context it creates itself.
  - The fixture is a synthetic 1×1 PNG written by the script to a temp file and read by the spec at runtime, so no literal reaches the code frame.
  - Positive control: `naturalWidth === 1` for each image, and the raw `test-results/` holds the image in the trace, the HAR and `resources/`.
  - GREEN: the gate exits 0, and `e2e-artifacts/` holds only `results.json` + `error-context.md`, with `# Error details` present and no fixture encoding.
  - D26b, the mutation "stage everything, check nothing": the images are published (RED). Restored: GREEN.
- **New D27, R7.** `test.use({ contextOptions: { recordHar: { … content: "embed" } } })` and `{ recordVideo }` are refused by name. With the screen mutated off, the HAR is written with the image (RED). Restored: refused.
- The ledger `mutation-digests.txt` is regenerated ONLY by `npm run e2e:demos`, and every line not touched by a mutated file stays byte-identical.
- **R14:** `normalise-transcript.mjs` gains the core #15 rule, `(/private)?/var/folders/…/T/` and `/tmp/…/` → `$TMPDIR/`, so the regenerated `d16d-*` files carry no local path.
  - **Proposal, not default:** a mechanical path-only scrub of the pre-existing historical transcripts that carry `/Users/…` or `/var/folders/…` (`round6-*`, `round7-*`, `gate-local-npm-run-ci.txt`, `demonstrate-summary.txt`, `browser-revision.txt`, `d12-requestfailed-listener-neutered-GREEN.txt`). The chair decides.

**D4. Normal red run and `ci-required`.**
- D26 GREEN proves a useful upload locally.
- **Proposal:** with chair approval, push one fast-forward commit adding a temporary failing spec, let CI go red, and read the real artifact with `gh api`: it must be `e2e-artifacts/` holding only the two shapes. `ci-required` must be red. Then push a fast-forward revert and wait for green.
  - This adds 2 commits to the PR, and publishes a synthetic-failure artifact for 3 days.
  - Without approval, `ci-required` red-on-failure rests on the unchanged `required-checks.txt` semantics. It is not demonstrated.

### E. Verification (Step B)
The lanes, in order:
1. `npm ci`
2. `npm run ci`
3. `bash scripts/ci/require-checks_test.sh`
4. `bash scripts/ci/check-e2e-lane.sh .github/workflows/e2e.yml`
5. Lane A: `E2E_LOCAL_PORT=… npm run e2e`
6. `node scripts/ci/check-coverage-floor-ran.mjs`
7. `npm run e2e:demos`, with its own ports and image tag
8. `node scripts/ci/harness-canary.mjs`
9. the unit RED run (`VZ_GATE_LEGACY` at the 5c5c971 gate) and the GREEN run

Then push fast-forward, and wait for `ci-required` green, read with my own `gh api`. The environment is Node 22.14.0, Playwright 1.63.0 and Chromium 1243 (cached), on macOS arm64 (BSD userland; CI is GNU).

### F. Flags for the chair
1. **VZ-FOUND-008 acceptance text** ("screenshots and traces retained on failure"): after this round Lane A retains NEITHER in its artifact. Traces stay on the runner only. That widens sentinel F-4 from screenshots to traces. The owner record is inbox 12, and it is not changed here.
2. **B7 scoping** of "anything written after the gate cannot be published".
3. **The harness change in B4.** It is required: without it N would refuse every red run. The cost is that a spec's own `testInfo.attach(…, { body })` over ~66 bytes refuses the upload, fail-closed.
4. **The Q-1 sweep reads `supply-chain.yml`'s two upload paths.** Editing them will then also need this guard's allowlist edited.
5. **The Meta `docs/quality/COMMANDS.md` and other meta docs, if they describe the upload set.** They are not touched here, because they are meta-owned. They are reported for the chair.
6. **The pre-existing historical transcript paths (R14).** Scrub, or leave; the chair decides.
