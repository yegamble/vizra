# vizra-user PR #10 re-plan (allowlist upload gate): security seat plan review

- **Plan reviewed:** `docs/plans/2026-09-23-user-pr10-close-gate-scope.md`, § "RE-PLAN (2026-09-23, fresh builder): flip the upload gate to an ALLOWLIST".
- **Checked against:**
  - vizra-user `5c5c971ea8980c1ae44a3716f2d0b73ee54fe50b`, read in the read-only worktree `.claude/worktrees/user-pr10-allowlist`. The worktree was left clean (`git status` empty) and the PR head was re-checked at the end: unchanged, open, not a draft.
  - The installed Playwright 1.63.0.
  - The findings the re-plan must close: VERIFY FINDINGS 9–15 and G3; sentinel F-1…F-6 and Q-1…Q-4.
  - Sentinel RULES R1, R3, R5, R6, R7, R14.
- **`gh api rate_limit`:** 4832, then 4786, of 5000. No forged rate-limit notice was seen.
- **Method:** read-only. Inert experiments ran only in the session scratchpad, with synthetic bytes and markers:
  - node scripts that required the worktree's `node_modules` by absolute path;
  - one scratch Playwright project whose `node_modules` was a symlink to the worktree's;
  - a download of the public CI artifact 10612777314 into scratch.

  Nothing was written to the worktree. Every scratch file was deleted afterwards. No safety classifier stopped anything, so there are no NOT RUN rows for that reason. For what was not run, see "Not run".

## Verdict in one paragraph

The flip to an allowlist is the right design. It closes the R3 class for binary files: traces, HARs, archives, screenshots, symlinks and `playwright-browsers.txt` are not detected, they are simply not staged. The source-side traversal is sound. Three things in the plan are wrong, and all three are cheap to fix:
1. **The second allowlisted shape, `error-context.md`, publishes a whole-page aria snapshot**, typed input values included (a password field's value, measured). The snapshot bypasses both `PLAYWRIGHT_NO_COPY_PROMPT` and the `# Page snapshot` refusal. It is the only content of that file that is not already in `results.json` or the job log (S-1).
2. **N = 89 was measured on shapes that lack a field CI now fills.** Playwright's git-info plugin writes the PR's diff into `results.json` on `pull_request` runs, and 7.2% of this repository's lockfile integrity values exceed N (S-2).
3. **Two claims are false.** B4's "covers the encoded shapes Playwright and Chromium write unprompted" is false: Playwright's own `toEqual` diff prints every byte of a buffer in decimal. The plan's "nothing is published" statements ignore the job log, which prints the same error text and stdout verbatim (S-3).

---

## Threat model, and who the attacker actually is

The plan's § A is correct, and it should say one more thing (residual R-C below). On a `pull_request` run the workflow file comes **from the pull request**, fork pull requests included. `gh api …/actions/permissions/fork-pr-contributor-approval` returns `first_time_contributors`. So any outside contributor who has contributed once can edit `e2e.yml` and upload anything, and no in-repo gate or guard can prevent it. The job holds nothing worth stealing: `permissions: contents: read`, no `secrets.` reference, `persist-credentials: false`, no authentication in Lane A.

So the gate protects against two things only: **accident**, meaning honest specs on pages that will soon render real-looking content, and **unreviewed drift**. That calibrates everything below:
- a channel an honest spec or Playwright opens unprompted is a finding;
- a channel only deliberate spec code opens is a residual, to be stated precisely and not chased with detectors.

---

## Ranked concerns

### S-1 — BLOCKER (for this plan). `error-context.md` carries a whole-page aria snapshot, with typed input values, that neither page-snapshot control sees

- **Confidence:** high. Measured end to end with Playwright 1.63.0.
- **Code path:**
  - `playwright-core/lib/coreBundle.js:24357-24365`: when a locator assertion fails because the element resolves to 0 elements (the commonest red), the server captures `injected.ariaSnapshotForExpectFailure(document.body, { mode: "default" })`.
  - `playwright/lib/worker/workerProcessEntry.js:829-834` copies it into `error.errorContext`.
  - `playwright/lib/errorContext.js:56-73` writes it into `error-context.md` under `# Error details` as a ` ```yaml ` block, not under `# Page snapshot`.
  - `playwright/lib/index.js:657-658`: `PLAYWRIGHT_NO_COPY_PROMPT` gates only the separate `_takePageSnapshot`, and `:662` even skips that when a matcher snapshot exists.
  - `scripts/ci/redact-artifacts.sh:187` refuses on the heading `# Page snapshot` only.
- **Reproducer (scratch; synthetic page via `setContent`; no network):**
  - The spec types a runtime-built marker into a text input with `pressSequentially` (`.fill(` is banned in specs, and `pressSequentially` is a documented tripwire evasion).
  - It then asserts `expect(page.getByRole('heading', { name: 'Not there' })).toBeVisible()`.
  - It runs with `PLAYWRIGHT_NO_COPY_PROMPT=1` and a JSON reporter.

  ```
  error-context.md: headings  # Instructions / # Test info / # Error details / ```yaml / # Test source
  '# Page snapshot' heading lines: 0          <- what the gate refuses on
  ```yaml
  - heading "Synthetic page" [level=1]
  - paragraph: Visible text VZTEXT-7f3a
  - text: Password
  - textbox "Password": VZTYPED-secret-9d44   <- a type=password field's typed value
  ```
  runtime-built marker: error-context.md 1 hit | results.json 0 | list-reporter terminal output 0
  ```

  A standalone probe also showed link targets in the snapshot (`/url: /photos/…?sig=…`). The gate's URL redaction would rewrite that query; the text and the values it does not touch.
- **Failure:**
  - The re-plan keeps "Page snapshot … refuses the upload (exit 1), as before" as a B3 rule, and AGENTS.md says the page snapshot is "suppressed in CI … and refused at the upload gate". Both are true of the `# Page snapshot` section and false of the content: the same class of data (page text and typed values) arrives in the commonest failure under another heading.
  - This snapshot is the **only** part of `error-context.md` that is not already public: the error text is in `results.json` and the job log, and the code frame is the public spec. So the second allowlisted shape exists, in effect, to publish exactly the channel the repository decided not to publish.
  - This is pre-existing on `main` (the file ships inside `test-results/` today), and Lane A data is synthetic by rule. That is why this blocks the plan, not the programme.
- **Smallest change:** **drop `error-context.md` from the allowlist.** Stage exactly one shape, `playwright-report/results.json`.
  - That loses nothing that is not public or in the log.
  - It also deletes the depth-1 traversal, the per-directory TOCTOU surface, the dir-name questions (S-6) and the 500-file cap.
  - If the chair wants the file anyway, the alternative is two layers:
    - `vizraHarnessGuard`'s teardown deletes `errorContext` from `testInfo.errors`. It runs before `didFinishTest` writes the file; measure that.
    - The gate refuses a ` ```yaml ` fence inside `# Error details` (pinned against `errorContext.js` by a unit test, as the heading is), and any `errorContext` key in `results.json`.
- **Acceptance:**
  - A red run whose failure is a missing element publishes no page text and no typed value in any staged file.
  - D26 (or a new D-row) plants a runtime marker in a text input and fails on a missing element. RED: with the shape re-added (or the strip mutated off), the marker is in the staged set. GREEN: it is absent.
  - AGENTS.md states which snapshot is controlled where.
- **Tests:** `upload-gate-allowlist.test.ts`: a tree whose `test-results/x/error-context.md` carries the yaml block → not staged (option A) or exit ≠ 0 (option B). A `results.json` with an `errorContext` key → exit ≠ 0 (a cheap backstop in either option).

### S-2 — REQUIRED. `results.json` carries `metadata.gitDiff` (the PR's diff) and `gitCommit` in CI; N was not measured on it, and common diffs exceed it

- **Confidence:** high on the code path; medium on whether the diff is captured on a hosted runner today (UNVERIFIED, see below).
- **Code path:**
  - `playwright/lib/runner/index.js:669-682`: with `captureGitInfo` unset, `commit` and `diff` are captured whenever `ciInfo()` is truthy, which it is under `GITHUB_ACTIONS` (`:686-701`).
  - `:766-780`: on a pull request the plugin runs `git fetch origin <base> --depth=1` and `git diff base HEAD`, truncated to 100,000 characters.
  - `:4069-4071`: the JSON reporter serialises `config` including `metadata`.
  - `playwright.config.ts` sets no `captureGitInfo`.
- **Observed:**
  - The one real CI `results.json` the plan measured (artifact 10612777314, run 35536837315, event `pull_request`) has `metadata` keys `ci`, `gitCommit`, `actualWorkers` and **no `gitDiff`**. On 2026-09-20 the repository was private and the checkout does not persist credentials, so the plugin's anonymous fetch presumably failed. The repository has been public since 2026-09-23, so it can now succeed. (UNVERIFIED: the plugin has a 3 s git timeout, and a depth-1 fetch may not finish in time. S-9's D4 run settles it.)
  - Local runs (no `GITHUB_ACTIONS`) capture neither field, so B4's local measurement cannot see them.
  - The lockfile, measured: 512 `integrity` values, **37 (7.2%) with a base64url run of 93** (`sha512-` + 86 characters that happen to hold no `+` or `/`). A PR diff touching `package-lock.json` (every Dependabot PR), a digest ledger, or a base64 fixture therefore makes every red run of that PR refuse its upload. That includes the D4 proof PR if its base is `main`, because PR #10's own diff would ride along.
  - `gitCommit` adds the author and committer name and email, which are already public on the commit.
- **Failure:** N's "measured basis" omits an input CI fills. The result is fail-closed, but an unexplained loss of diagnostics on a whole class of PRs, and a D4 run whose outcome depends on the diff.
- **Smallest change:**
  - Add `captureGitInfo: { commit: false, diff: false }` as a literal in `playwright.config.ts`. The demos configuration inherits it. `check-e2e-lane.mjs` reads it as an early-warning literal, like the recorder literals.
  - `metadata.ci`, which carries `prTitle`, `prHref`, `commitHref` and `buildHref` and is not gated by `captureGitInfo`, stays. State that it is PR-author text.
- **Acceptance:**
  - D1's inverse-control tree includes a `metadata.ci` object of the real CI shape and passes.
  - The D4 readback lists `config.metadata` keys, which must not include `gitDiff` or `gitCommit`.
- **Tests:** a unit case with a `metadata.gitDiff` holding one 93-character base64url run → exit ≠ 0 (this documents why the config is off), plus the lane-guard literal case.

### S-3 — REQUIRED. B4's scope claim is false for Playwright's own output, and "nothing is published" ignores the job log

- **Confidence:** high, measured.
- **Observed:**
  - (a) Playwright's bundled `expect`, in scratch, with random synthetic bytes:
    ```
    toEqual two different 2000-B Buffers   | message 40,069 B | 1,779 "+ <byte>," lines | longest std run 8
    toEqual Buffer vs empty Buffer         | message 21,300 B | 2,000 "+ <byte>," lines | longest std run 8
    toEqual {body: Buffer} objects         | message 47,661 B | 1,779 "+ <byte>," lines | longest std run 8
    toEqual near-equal Buffers             | 211 B (context lines only)
    toBe on two base64 strings             | longest std run 2,667 (N catches this one)
    ```
    So an honest "download returns the uploaded bytes" spec that fails prints the received image in decimal, one byte per line. That fits in a 256 KiB file up to about 24 KB of image, and in 8 MiB up to about 780 KB. N does not see it, and B4 attributes decimal arrays to "a spec [that] writes" them.
  - (b) The `list` reporter:
    - `runner/index.js:4699-4706` and `:4777-4782` write every test stdout and stderr chunk **raw** to the job log (`stream.write(chunk)`, Buffers included);
    - `formatFailure` prints the full error message and code frame.

    The same text N refuses in `results.json` is therefore already in a log that is public for 90 days and that no gate reads. Also ungated: `Container logs` (`docker logs … | tail -200`, `if: always()`), the canary's captured Playwright output and the floor check's messages.
- **Failure:** R1 and R6. D25/D26 "nothing is published" is true of the artifact only. For error-text and stdout channels the N rule withholds the 3-day copy while the 90-day copy is printed. N keeps real value for what the log does NOT print: attachment bodies, annotations and `metadata`.
- **Smallest change:** plan text only.
  - Replace B4's "This covers the encoded shapes Playwright and Chromium write unprompted …" with residual **R-A** below.
  - Scope D25/D26/§ C to "nothing is uploaded as an artifact".
  - Add the log channel to AGENTS.md's "What still gets through".
  - Queue a separate slice (SHOULD, not this PR): a CI-mode reporter that routes failure text and stdout through `redact.ts` plus the long-run rule before the log. Without it, the log is the channel that matters for both diagnosis and exposure.
- **Tests:** a named residual unit case: an `error-context.md`/`results.json` whose message is a decimal-per-line dump → staged, asserting rc 0 and naming it a residual (or refused, if the chair ever adds a rule). A grep in the acceptance list for "write unprompted".

### S-4 — SHOULD. Make N's derivation a test, and make a refusal diagnosable without content

- **N is stable** for today's inputs, because the output directory is the only legitimate producer near it:
  - `trimLongString(…, 60)`, then `-` + `desktop-chromium-1440` (21, `required-projects.ts:28`), then `-retry1` (`retries: process.env.CI ? 1 : 0`, `playwright.config.ts:94`) = 89;
  - `sanitizeForFilePath` maps everything outside `[A-Za-z0-9-]` (and non-ASCII) to `-`, so titles cannot lengthen it;
  - raw titles in `results.json` keep their spaces.

  It moves only with a longer project name, `retries ≥ 10`, `--repeat-each` (refused by the floor reporter), or S-2's diff. Fail-closed is acceptable, because the job log keeps the failure text.
- **Change:**
  - A unit test that computes `60 + 1 + max(project name length) + len("-retry" + CI retries)` from `required-projects.ts` and the config literal, and asserts it is ≤ N. A rename then goes red in `npm run ci`, not in a real red run.
  - The refusal line names the file, the rule, the alphabet, the run length and the byte offset. It never names the content.

### S-5 — SHOULD. Close the destination side of the gate's own TOCTOU

- The source side is sound: lstat, chdir with a dev/ino comparison, `O_NOFOLLOW`, fstat.
- The destination side is not specified. A writer racing the gate can plant `e2e-artifacts/test-results` or `…/playwright-report` as a **symlink** between `mkdir e2e-artifacts` and the gate's sub-`mkdir`. The pinned `upload-artifact` follows symlinks (VERIFY G3, `dist/upload/index.js:9721`), so the upload would publish the target.
- **Change:**
  - `mkdir` each staging directory singly (no `-p`) and `lstat`-verify it.
  - Write with `O_CREAT|O_EXCL|O_NOFOLLOW`.
  - As the gate's last act, re-walk `e2e-artifacts/` with `lstat` and require exactly the set it wrote: every entry a regular file with `nlink == 1`, and its size and sha256 equal to the buffer it checked.
  - Open sources with `O_NONBLOCK` as well, so a FIFO swapped in after the `lstat` cannot hang the step until the 30-minute job timeout.
  - With S-1's option A, the source side shrinks to one file.
- **Test:** a unit case where a pre-planted symlink appears under `e2e-artifacts/` after `mkdir` (simulated by a hook between steps, or by pre-creating it in a subdirectory the gate would create) → exit ≠ 0.

### S-6 — SHOULD, only if `error-context.md` stays. Directory grammar and log-safe path printing

- `<dir>` is spec-writable: a spec can `mkdir` any name under `test-results/`, including newlines, `::` and invalid UTF-8.
- Upload-artifact v4 fails the whole upload on `\r \n " : < > | * ?` in a path. That fails closed, but at the wrong layer and without a named reason.
- **Change:**
  - `<dir>` must be valid UTF-8, with no C0, C1 or DEL, not start with `.`, and be ≤ 255 bytes. Anything else refuses, with a named reason.
  - A symlinked `test-results` root refuses; it is not silently skipped.
  - Paths printed by the gate go through the same sanitiser `redact.ts` uses (non-printables as `\xNN`, a leading `::` neutralised).

### S-7 — SHOULD (owner action, outside the PR). Fork-PR approval policy

`first_time_contributors` means a returning outside contributor's PR runs its own `e2e.yml` without approval. On a public repository that is the route by which arbitrary content can be published under this repository's name, with any retention the PR's workflow sets. It is independent of this gate. **Proposal for the owner inbox:** `all_external_contributors`.

### S-8 — NIT. R7 wording

With the allowlist, R7 is an early control only. State that `contextOptions.recordHar`/`recordVideo` are screened. The following still WRITE on the runner and are unpublished only because nothing but the allowlisted file is staged:
- `page.screenshot`;
- `browser.startTracing({ screenshots: true })`;
- `context.tracing.start/stop({ path })`;
- `routeFromHAR(…, { update: true })`;
- `browser.newContext({ recordHar })` in a spec.

### S-9 — NIT. Small fail-closed gaps

- The harness's write of `browser-signals.json` must be awaited and must fail the test if it throws (R5).
- Add `/e2e-artifacts` to `.gitignore`.
- The lane guard should refuse a tracked `e2e-artifacts/`. A committed one makes every red run exit 6: closed, but silent.

---

## Answers to the chair's list

**Encodings under N that carry an image.** "Unprompted" means written by Playwright, Chromium or Node from an honest spec.

| Shape | Unprompted producer | N catches | Also in the job log |
|---|---|---|---|
| unbroken base64 / base64url / hex, ≥ 67 B | yes: a received value, a `data:` URI, an attach body, a stdout Buffer entry | yes | yes (error text, raw stdout) |
| **decimal, one per line** (the jest diff of bytes) | **yes: a failing `toEqual` on a Buffer, Uint8Array or number array** | **no** | yes |
| inline `[137, 80, …]` | yes, on a type mismatch, but pretty-format stops at 10 elements (measured) | no | bounded |
| `<Buffer 89 50 …>` from `console.log` | yes, but `util.inspect` stops at 50 bytes by default | no | bounded |
| wrapped or chunked base64, ascii85/Z85, percent, quoted-printable, octal/`\xNN`, JSON number arrays, many short runs across fields | spec-authored only | no | yes |
| base32 / base36 / base58 | spec-authored | yes (subsets of the base64 alphabet) | yes |
| latin-1-as-string binary | spec-authored | no, but bytes 0x80–0x9F become C1 in `results.json` (refused), and C0 is raw in `.md` (refused) | yes |
| anything under 67 B (a 1×1 GIF) | — | no | — |

**Spec-controlled free text in `results.json`:**
- titles, tags, annotations;
- stdout/stderr (text, or a base64 `buffer`);
- error messages, received values, `snippet`, `stack`, `location`;
- attachment names, content types, paths and bodies;
- `test.step` titles;
- `metadata.ci.prTitle` (PR author);
- and, until S-2, `gitCommit` and `gitDiff`.

All of it is arbitrary text. Under the threat model that is acceptable, and it is the log's text too (S-3).

**N stability:** see S-4. Fail-closed is acceptable for diagnosability, because the log keeps the failure text.

**TOCTOU, depth 1, path tricks:**
- The source side is sound.
- The destination side needs S-5.
- Directory names need S-6, which is moot under S-1's option A.
- Unicode in names is harmless to confidentiality. Newlines break the uploader (closed, but unnamed).

**R7:** complete enough as an early control (S-8). The allowlist is the control.

**R6, what still publishes on failure outside the staging directory:**
- the job log: the `list` reporter's failure text and raw stdout/stderr; `Container logs`, tail 200, `if: always()`; the canary's captured output; the floor check; the gate's own messages;
- nothing else, once the Q-1 sweep lands, except the `run:` class.

**R14, page text from snapshots:** acceptable for synthetic data only, and only once S-1 removes the matcher snapshot (typed values do not belong in a public artifact even when synthetic, because the day one is not synthetic the channel is already open). The conditions are in residual R-D.

---

## Rulings on the builder's decisions

1. **Attach `browser-signals.json` by path: CONFIRMED.**
   - `e2e/harness/test.ts:327` is the only attacher, and nothing in `scripts/` decodes the body out of `results.json` (grep).
   - A path attachment is copied to `attachments/<name>-<sha1>.json` (`workerProcessEntry.js:100`), which is not staged.
   - Condition: S-9's first bullet.
2. **Post-gate writer: CONFIRMED as a residual. The residual is acceptable on a public repository, with S-5's end-of-gate re-walk as the cheap mitigation.**
   - The re-walk closes writes during the gate, planted symlinks included, and leaves only the gate-exit → upload-start window.
   - Declined:
     - running the lane in its own process group or session and killing it (a child can `setsid` or double-fork out, and a cgroup scope can be left with passwordless sudo);
     - a manifest re-checked by a pinned step before the upload (it only moves the window, and it needs a step between the gate and the upload, which the guard forbids).
   - Why acceptable: the only writer is code the PR supplies. That code can equally edit `e2e.yml` (residual R-C), and the job holds no secret. No accidental writer targets `e2e-artifacts/`: honest leftovers write into `test-results/`, which is no longer uploaded.
   - Exact sentence: R-B.
3. **VZ-FOUND-008 retention to Lane B: CONFIRMED as owner inbox 12, not decided here.**
   - Until the owner rules, no doc may say Lane A retains screenshots or traces, and VZ-FOUND-008 cannot go VERIFIED on its current text (sentinel F-4).
   - Tell the owner that with S-1's option A, Lane A's artifact is `results.json` alone.
4. **Real-CI proof: CONFIRMED, on a throwaway draft PR from a separate branch, closed afterwards, not on #10. Publishing a synthetic-failure artifact is acceptable:** the same class as any red run, 3 days. Conditions:
   - Branch from #10's head. Either set the PR's base to `fix/lane-a-pixels-off`, or land S-2 first, so the diff is not an unknown input.
   - The title and body are inert: `prTitle` lands in `results.json`.
   - **Run (a):** a missing-element assertion on the real page, which also exercises S-1. The artifact read back with `gh api` must hold exactly the allowlisted shape(s), `config.metadata` keys without `gitDiff`/`gitCommit`, no attachment body, and no `playwright-browsers.txt`, trace, `.last-run.json` or `browser-signals.json` file.
   - **Run (b):** a failure whose message carries an inert 90-character run of a marker (not an image). The redact step must be red, the upload skipped, and `gh api …/runs/<id>/artifacts` must give `total_count` 0.
   - `ci-required` must be red on both, read with the chair's own `gh api`.
   - Do not delete the artifact (deleting is owner-only); let it expire.
   - The branch follows the precedent of `chore/e2e-artifact-upload-proof`.
5. **Scrub older transcripts: CONFIRMED NO, queued separately.** This round's regenerated transcripts must carry no local path (plan D3's normaliser rule), checked by grep in acceptance.

---

## Residual sentences, exact (for AGENTS.md and the PR body)

- **R-A (text channels).** "Lane A publishes one text file, `playwright-report/results.json`, checked by the rules in 'What the gate refuses, exactly'. Text cannot be made image-proof. The long-run rule refuses data written as one unbroken run of more than 89 base64, base64url or hex characters. It does not refuse data written with separators, or payloads under 67 bytes. That includes a form Playwright writes for an honest assertion: a failing `toEqual` on a byte buffer or byte array prints every differing byte as a decimal, one per line. The same error text, and every line a test writes to stdout or stderr, is printed verbatim to the public job log by the `list` reporter, and no gate reads that log. For those channels the rule withholds the artifact copy only."
- **R-B (post-gate writer).** "A process started by code under test can outlive the lane step and write into `e2e-artifacts/` after the gate's final check and before the upload step reads it, and the upload would publish what it wrote. No in-job control prevents this, because every step runs as the same user with passwordless sudo. It is the `run:` class, and it is dominated by R-C."
- **R-C (who can publish).** "On a `pull_request` run the workflow file comes from the pull request, fork pull requests included. A pull request can therefore publish anything by editing `e2e.yml`, whatever this gate does. The gate and the lane guard protect against accident and unreviewed drift, not against the author of a malicious pull request. Against that author, the controls are review and GitHub's fork-PR approval setting (currently `first_time_contributors`)."
- **R-D (page text).** "The artifact and the job log carry page text from failing tests: error messages and received values. That is acceptable only while Lane A's pages are synthetic by rule: no spec authenticates, CI drives no backend holding real data, and fixture media carry no real EXIF, GPS or maker data (a photo page renders those as text). It lapses the day any of those stops being true."

## NOT WORTH DOING

- **More detectors** (per-alphabet tightening, aggregate multi-run thresholds, decoders for wrapped base64, decimal or quoted-printable). Text cannot be made image-proof, the log prints the same bytes, and each detector restarts the R3 cycle this re-plan exists to end. The harness's 64-hex stamp alone would defeat simple aggregate thresholds (36 per red run).
- **Per-file withholding instead of whole-upload refusal.** `results.json` carries the same message as any `error-context.md`, so it would rarely save anything.
- **Process-group or cgroup kill, and a manifest re-check step** (decision 2).

## Not run

- A real hosted runner, so these were not observed:
  - orphan-process survival across steps (sentinel Q-2);
  - whether the plugin's anonymous `git fetch` completes within its 3 s limit (S-2);
  - upload-artifact's path-character validation (S-6).

  D4 run (a) covers S-2's question.
- The builder's and verifier's lanes (`npm run ci`, Lane A, demos, canary, `require-checks_test.sh`): the plan has no code yet.
- Nothing was posted, pushed, commented or merged.

**Must change before Step B:** S-1, S-2 and S-3 go into the plan. S-4 to S-7 are SHOULD, with S-7 for the owner inbox. S-8 and S-9 are NITs.

PLAN VERDICT: APPROVE WITH CHANGES
