# Independent verification — yegamble/vizra-user PR #6 (contract re-vendor from core `main`)

**Verdict: PASS**

- PR: https://github.com/yegamble/vizra-user/pull/6
- Head SHA verified: `ca23fefcc8cd9bd026d66ff28647289faf07cdfd` (branch `chore/revendor-core-main`, base `main` `f49bca4615eb940feaccec284530c43eff426dbd`)
- Head re-checked at the end of the session: still `ca23fef…`, PR state OPEN. The branch did not move during verification.
- Verifier: independent agent; did not write any of this code.
- Slice: re-vendor `api/openapi.yaml` from vizra-core `main`, and close verifier Finding 3 of PR #1 (nothing read the manifest's provenance).
- Builder plan read: `/Users/yosefgamble/github/vizra/docs/plans/2026-09-21-vizra-user-revendor.md`.
  The transcripts under `docs/evidence/revendor/` in the PR were treated as claims, not evidence, and re-derived independently.

## Environment

| Item | Value |
|---|---|
| Machine | Darwin 25.5.0, arm64 (native, no emulation) |
| Fresh clone | `<scratch>/verify-pr6/user` — `git clone https://github.com/yegamble/vizra-user.git`, `git checkout ca23fef…`. Never the builder's checkout. |
| node / npm | v22.14.0 / 10.9.2 |
| `npm ci` | exit 0, 0 vulnerabilities |
| Playwright browsers | chromium-1243 / chromium_headless_shell-1243 (pre-installed cache, read-only) |
| Core reference (READ-ONLY) | `/Users/yosefgamble/github/vizra/vizra-core` — never written to |
| Core scratch clone | `<scratch>/verify-pr6/core-scratch`, cloned from the local core checkout; this is the only core tree that was dirtied |
| Disk before start | 11 GiB free (`df -h /`) |
| Docker | not used — this slice needs no image build (per brief) |

## 1. Repo lanes, from the clean clone

| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | clean install from lockfile |
| `npm run ci` (lint → typecheck → vitest → next build) | 0 | **Test Files 13 passed (13); Tests 315 passed (315)**; no `skipped`/`todo` line emitted; build "Compiled successfully" |
| `npm run check:contract` | 0 | manifest ✓ (sha256 `128d0509238a…`, 10695 bytes, blob `58030e7f0d90…`); client byte-for-byte from openapi-typescript 7.13.0 |
| `node scripts/check-spec-refs.mjs` | 0 | all 9 `$ref` values in-document |
| `node scripts/check-manifest.mjs` | 0 | provenance well-formed; prints its own "NOT checked here" caveat |
| `npx vitest run scripts/check-manifest.test.mjs` | 0 | **26 passed (26)** — the claimed 26 new unit tests exist and pass |
| `bash scripts/ci/require-checks_test.sh` | 0 | **102 cases, 109 assertions, 0 failed** |
| `bash scripts/ci/check-required-manifest.sh` | 0 | all 5 entries map to a defined job |
| `bash scripts/ci/check-required-floor.sh` | 0 | floor still `frontend contract e2e` |
| `bash scripts/ci/check-image-pins.sh` | 0 | 3 external FROM lines @sha256-pinned at node 22.14.0 |
| `node scripts/ci/check-e2e-lane.mjs` | 0 | e2e.yml still drives the built image, runs `npm run e2e` unconditionally, re-checks the floor, runs the canary, redacts before every upload |
| `npm run e2e` | 0 | **18 passed**; coverage floor **OK (desktop-chromium-1440=9/9 mobile-chromium-390=9/9)**; harness stamp **OK (18 verified)** |
| `node scripts/ci/harness-canary.mjs` | 0 | failed all 3 fault-injection fixtures with exactly the expected record kinds (`[console]` / `[response]`+http 404 / `[pageerror]`) |
| `bash scripts/demonstrate-contract.sh` | 0 | **12 expected outcomes, 0 unexpected**; code tree clean afterwards |

Every count the builder claimed reproduces exactly. No skipped, cancelled, timed-out or uncollected test in any lane I ran.

## 2. Provenance — independently derived

```
git hash-object contracts/vizra-core/api/openapi.yaml              -> 58030e7f0d90d9bf00f44782d705aad72a18407c
git -C <core> rev-parse 415a6d19cfc0…:api/openapi.yaml             -> 58030e7f0d90d9bf00f44782d705aad72a18407c   IDENTICAL
git -C <core> rev-parse origin/main                                -> 9e44d30415c9545aa12e4ce84e4afe6062725e55
git -C <core> rev-parse origin/main:api/openapi.yaml               -> 58030e7f0d90d9bf00f44782d705aad72a18407c   UNCHANGED at core's current main
git -C <core> merge-base --is-ancestor 415a6d19… origin/main       -> exit 0  (415a6d1 IS reachable from origin/main)
git -C <core> merge-base --is-ancestor b0dbeb6d… origin/main       -> exit 1  (b0dbeb6 is NOT)
git -C <core> branch -a --contains b0dbeb6d…                       -> feat/m0-foundation  (LOCAL branch only)
git -C <core> ls-remote --heads origin                             -> only refs/heads/main
shasum -a 256 contracts/vizra-core/api/openapi.yaml                -> 128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d
wc -c   contracts/vizra-core/api/openapi.yaml                      -> 10695
```

Manifest at head, field by field — every one true:

| Field | Value | Verified |
|---|---|---|
| `source_repo` | `yegamble/vizra-core` | ADR-002's repo |
| `source_ref` | `main` | yes |
| `source_commit` | `415a6d19cfc0acedd8ad84c1857c95db0ed63627` | 40-hex; reachable from core `origin/main` |
| `source_blob` | `58030e7f0d90d9bf00f44782d705aad72a18407c` | equals `git hash-object` of the file on disk and core's blob at that commit |
| `sha256` | `128d0509238a…` | matches `shasum -a 256` |
| `bytes` | `10695` | matches `wc -c` |
| `$schema_version` | `2` | matches the code's constant |

**Does vendoring `415a6d1` rather than `9e44d30` matter? No.** `api/openapi.yaml` is the same blob `58030e7f…` at both commits, and `415a6d1` is an ancestor of core's current `origin/main`. I proved the equivalence constructively: re-running the vendor script against a core clone whose `main` is `9e44d30` produced a diff of **exactly one line** — `source_commit` — with the spec and `lib/api/generated.ts` byte-identical. The recorded commit is one merge behind core's tip but is a real, reachable commit holding the exact bytes committed here. Re-pointing it at `9e44d30` would be cosmetic; it is not required for this PR and would need another re-vendor anyway when core lands the `VIZRA_SEARCH_HMAC_KEY` → `SEARCH_HMAC_KEY` rename.

**Scope of the change under `contracts/` and `lib/`:**

```
git diff --stat f49bca4 ca23fef -- contracts/ lib/
 contracts/manifest.json | 14 +++++++-------
 1 file changed, 7 insertions(+), 7 deletions(-)

git rev-parse f49bca4:lib/api/generated.ts   -> af5cf1f68d9ffddf3c9530954089fc3437501de1
git rev-parse ca23fef:lib/api/generated.ts   -> af5cf1f68d9ffddf3c9530954089fc3437501de1   BYTE-UNCHANGED
git rev-parse f49bca4:contracts/vizra-core/api/openapi.yaml -> 58030e7f…  (same as head)
```

The generated client is byte-unchanged and the vendored spec is byte-unchanged. The builder's "byte-identical across core's squash" claim is confirmed at the blob level.

## 3. The rewritten vendor script — demonstrations I ran myself

All run against `core-scratch` (my clone), with the vizra-user tree restored after each; final tree clean.

| # | Demonstration | Observed |
|---|---|---|
| A | `--ref main` (core-scratch main = `9e44d30`) | exit 0; manifest `source_commit` → `9e44d30…`; blob/sha256/bytes unchanged; only `contracts/manifest.json` modified |
| B | `--ref 415a6d19cfc0…` (explicit commit) | exit 0 with a warning that the ref is not `main`; manifest records `source_ref` = that commit; `check-manifest.mjs` then **exit 1**: `manifest source_ref is "415a6d19…", expected "main"` — so a non-`main` vendor cannot merge |
| C | **Never reads the working tree** — appended `# POISONED-BY-VERIFIER-WORKING-TREE` to `core-scratch/api/openapi.yaml` (tree dirty, file 10732 bytes), then `--ref main` | vendored file **10695 bytes**, blob `58030e7f…`, `grep -c POISONED` = **0**. The bytes came from the object database, not the dirty tree. |
| D | `--ref no-such-ref-xyz` | **exit 2**, message names the ref and the checkout; `git status --porcelain` empty — **nothing written** |
| E | Dirty *vizra-user* tree (`lib/api/generated.ts` hand-appended), then `--ref main` | exit 0 — **no dirty-tree refusal**. See NIT 1; the builder never claimed one. |
| F | Local `main` reset to `415a6d1` while `origin/main` = `9e44d30` | exit 0 **with warning**: "main in … is 415a6d19…, but origin/main is 9e44d30…". Warning only, never a failure — which is accurate to what AGENTS.md says ("warns — but does not fail"). |

**Injection probes (`--ref` and `--from` both reach `git`).** A canary path was chosen and watched; it was never created.

| Probe | Result |
|---|---|
| `--ref "main; touch <canary>"` | passed to `git` as one literal argv element; exit 2; no canary |
| `--ref "$(touch <canary>)"` | literal; exit 2; no canary |
| ``--ref "`touch <canary>`"`` | literal; exit 2; no canary |
| `--ref "--output=<canary>"` (option injection) | `git rev-parse --verify` rejected it; exit 2; nothing written; no canary |
| `--ref "--help"` | exit 2; nothing written |
| `--from "--upload-pack=touch <canary>"` | `resolve()`d to a path, then "is not a git checkout"; exit 2; no canary |
| `--from "<path with spaces>"` | works correctly (exit 0, correct blob) |

No shell is ever involved: the script uses `execFileSync("git", [...])` with an argument array. **No command injection and no option injection.**

## 4. `check-manifest.mjs` — red/green matrix, each named

Each mutation applied by me to the clean clone, `node scripts/check-manifest.mjs` run, then restored. Tree clean at the end.

| Mutation | Exit | First error |
|---|---|---|
| (baseline, unchanged) | **0** | ✅ green |
| `source_ref: feat/m0-foundation` + `source_commit: b0dbeb6…` — **PR #1's real state** | **1** | `manifest source_ref is "feat/m0-foundation", expected "main".` |
| `source_commit: "415a6d1"` (7 chars) | **1** | `expected a 40-character hex commit id.` |
| `bytes` + 1 | **1** | `…is 10695 bytes; the manifest says 10696.` |
| `source_blob` = 40 zeros | **1** | `…is not the blob the manifest names.` |
| `sha256` = 64 zeros | **1** | `…does not match its manifest.` |
| `source_ref: release/v1` | **1** | `expected "main".` |
| missing field (`delete spec.source_commit`) | **1** | `manifest source_commit is undefined, expected a 40-character hex commit id.` |
| **extra unknown fields** (`spec.totally_made_up`, top-level `attacker_note`) | **0** | **accepted** — see NIT 2 |
| `vendored_path` → `contracts/other.yaml` | **1** | `manifest vendored_path is "contracts/other.yaml", expected …` |
| manifest describes a **different file** (spec on disk altered, manifest untouched) | **1** | `…is not the blob the manifest names.` (+ sha256 and byte errors) |
| `$schema_version: 3` | **1** | `has $schema_version 3, expected 2.` |
| `spec` object deleted | **1** | `has no `spec` object.` |
| **residual:** well-formed manifest naming a commit that does not exist (`deadbeef`×5) | **0** | ✅ green — **undetectable here, as stated** |

**The residual is exactly as the builder describes it, and AGENTS.md says exactly that and no more.** The "Owed — STALENESS IS NOT DETECTED HERE" section states that the lane cannot prove the recorded commit exists, that the blob is the one that commit holds, or that core's `main` has not moved; that the blocker is a read token for the private `yegamble/vizra-core`; that providing it is an owner action outside any pull request; and names the concrete step to add once it exists. It claims nothing beyond that. `check-manifest.mjs`, `check-contract.mjs` and `contract-ci.yml` all print the same caveat at runtime, so a green lane cannot be misread as "current". I found no overclaim anywhere in the changed prose.

One honest limitation worth recording for the chair (not a defect): the specific PR #1 failure — a commit that has become unreachable — is caught only *indirectly*, by the `source_ref === "main"` rule acting as a proxy. A manifest that said `source_ref: main` while naming `b0dbeb6` would still pass. The builder's docs say so explicitly.

**The new tests are not tautological.** I mutated the implementation five ways and confirmed the suite catches each:

| Implementation mutation | Suite result (baseline 26 passed) |
|---|---|
| `source_ref` check disabled | **4 failed** |
| 40-hex `source_commit` check disabled | **6 failed** |
| sha256 comparison disabled | **2 failed** |
| byte-count comparison disabled | **2 failed** |
| blob-id comparison disabled | **1 failed** |

## 5. Regression and diff audit

| Check | Result |
|---|---|
| Hand-edited `lib/api/generated.ts` → `npm run check:contract` | **exit 1**, `lib/api/generated.ts is not what the contract generates`, first difference at line 6 |
| Vendored spec edited in place → `npm run check:contract` | **exit 1**, blob mismatch **and** sha256 mismatch, both with manifest-vs-disk values |
| Remote `$ref` (`https://evil.example/…`) → `check-spec-refs.mjs` | **exit 1**, names line 60 and the value |
| Same remote `$ref` → `node scripts/codegen.mjs` | **exit 1**, `codegen refused the contract` — the guard fires *before* the generator reads it |
| Relative file `$ref` (`./shared.yaml#/X`) | **exit 1**, names line 114 |
| Harness untouched | `git diff --stat f49bca4 ca23fef -- .github/required-checks.txt e2e/harness/required-projects.json playwright.config.ts e2e/harness/` → **empty**. `e2e/` is untouched entirely. |
| No test weakened or deleted | `git diff --numstat` over test paths: only `scripts/check-manifest.test.mjs` **227 added / 0 removed**. No test file anywhere has a nonzero removal count. |
| Removals audit (non-docs) | Only `contract-ci.yml` (6), `AGENTS.md` (12), `contracts/manifest.json` (7), `check-contract.mjs` (28), `vendor-contract.mjs` (47). I read every removed line in `check-contract.mjs`: the old inline sha256 and missing-file checks were **moved into** `checkManifestFiles`, which additionally checks bytes, blob id, ref, schema version and 40-hex ids. **Strictly stronger, nothing dropped.** |
| Generated files hand-edited | No. `lib/api/generated.ts` blob identical to base. |
| Invented package APIs | None — the new scripts use node builtins only (`node:crypto`, `node:fs`, `node:path`, `node:child_process`, `node:url`). |
| Unbounded resources | `execFileSync` bounded by `maxBuffer: 64 MiB`; no network, no subprocess shell, no recursion. |
| Secrets / private data in logs | None. Every "token"/"secret" hit in the diff is prose about the *absent* core read token. |
| Mock data on a product path / dead controls / fake success | Not applicable — no `app/`, `components/` or `lib/` source changed. |
| False-positive CI | See §6. |

## 6. GitHub CI on `ca23fef…`

`gh api repos/yegamble/vizra-user/commits/ca23fef…/check-runs` — 8 check runs, **all `completed` / `success`**:
`ci-required`, `contract`, `deps-scan`, `e2e`, `frontend`, `guard`, `image-scan`, `GitGuardian Security Checks`.
(The combined *status* API reads `pending` only because this repo publishes check-runs and no commit statuses; there are zero statuses. Not a gap.)

**`ci-required` (run 35547204935) actually ran on this SHA and read the manifest.** Its log:

```
ci-required: commit ca23fefcc8cd9bd026d66ff28647289faf07cdfd
ci-required: manifest .github/required-checks.txt
  - frontend
  - contract
  - ?guard
  - ?docker-build
  - e2e
waiting: frontend (in_progress) contract (in_progress) guard (in_progress) docker-build (…) e2e (in_progress)
waiting: docker-build (…) e2e (in_progress)
  (not triggered, optional-if-absent): docker-build
OK: every required check on ca23fefcc8cd9bd026d66ff28647289faf07cdfd concluded success.
```

It **waited for `e2e`** across three poll cycles until it concluded, and `CHECK_SHA` was the PR head, not the merge commit. The manifest's set matches the jobs that actually ran — no listed-but-never-executed lane.

**`docker-build` absence is legitimate, not a skipped required lane.** `.github/required-checks.txt` declares it `?docker-build` ("required only IF it ran (path-filtered lanes)"), with the reason written in the file. `docker-build.yml`'s `pull_request` path filter is `Dockerfile`, `.dockerignore`, `package.json`, `package-lock.json`, `.nvmrc`, `next.config.ts`, `.github/workflows/docker-build.yml`. I listed all 26 files this PR changes: **none** of them is in that set. The lane was never triggered, so there is no skipped check-run to launder. By contrast `e2e` is required unconditionally (`e2e`, not `?e2e`) and did run and pass.

Per-lane logs on this SHA:
- **contract-ci** — steps executed by name: "The vendored contract references nothing outside itself" (`OK: all 9 $ref values … are in-document pointers`), **"The manifest describes the vendored contract"** (✅ plus the "NOT checked here (needs a read token…)" caveat — the new named step exists and ran), "Generated client matches the contract" (✅), "The check changed nothing" (`git diff --exit-code`, clean).
- **frontend-ci** — `Test Files 13 passed (13)`, `Tests 315 passed (315)`; plus the server-only boundary negative case ("the build failed (exit 1) with 4 server-only diagnostics").
- **e2e** — `18 passed`, floor `desktop-chromium-1440=9/9 mobile-chromium-390=9/9`, `harness stamp: OK (18 verified)`, out-of-process floor re-check OK, canary step ran.
- **ci-guard** — shellcheck, immutable action pins, no unmarked `continue-on-error`, `npm ci` only.

## 7. PR-body and plan claims checked against what I observed

Every quantitative claim in the PR body and plan reproduced: byte-identity of the spec across core's squash (blob `58030e7f…`, sha256 `128d0509…`, 10695 bytes); `b0dbeb6` not an ancestor of core `main`; 315 tests / 13 files / 0 skipped; 18 e2e passed with 9/9 + 9/9 and 18 stamps; 102 cases / 109 assertions; 26 manifest unit tests; 12 demonstrations, 0 unexpected; `docker-build` path-filtered and optional-if-absent. I found **no fabricated, rounded or unsupported number**.

The committed transcripts under `docs/evidence/revendor/` were regenerated by me from the head: the only differences from the committed copies are the recorded source SHA (`549e589` → `ca23fef`), timestamps and temp-dir paths. Every recorded **outcome** is identical. The builder's statement that the transcripts were taken at code head `549e589` is accurate (`ca23fef` is a docs-only commit on top).

The PR body says READY_FOR_REVIEW and does not claim VERIFIED. Correct.

---

## Findings

No BLOCKER and no REQUIRED finding. Four NITs, none of which gates this merge.

```
FINDING 1: the vendor script silently overwrites a dirty vizra-user tree
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/vendor-contract.mjs:102-135 (main(); no working-tree check before writeFileSync)
  requirements: VZ-FOUND-002

Observed:
  With `lib/api/generated.ts` hand-modified and uncommitted, `node
  scripts/vendor-contract.mjs --from ../core-scratch --ref main` exits 0 and
  overwrites both contracts/ and lib/ without comment. The script checks that
  the CORE checkout is a git repo, but never inspects the vizra-user tree.
  AGENTS.md's "a dirty tree cannot be vendored" refers to core's tree, and
  that claim IS true (demonstration C above) — so this is not an overclaim.

Failure:
  A developer with uncommitted work under contracts/ or lib/ loses it with no
  prompt. Bounded: both paths are generated artifacts that should not carry
  hand edits, and the drift check would have rejected such edits anyway.

Perspective:
  developer

Recommendation:
  Optional. If wanted, one `git status --porcelain -- contracts lib` check with
  a `--force` escape hatch, before the first writeFileSync.

Acceptance criteria:
  Running the vendor script with a modified contracts/ or lib/ file exits
  non-zero naming the file, unless --force is passed; a clean tree is
  unaffected.

Tests:
  A case in scripts/check-manifest.test.mjs's idiom, or a new
  scripts/vendor-contract.test.mjs; the harness exists (vitest).

Cross-repo implications:
  core: none | user: the change above | search: none | meta: none

Challenge:
  Overwriting generated files is precisely what a re-vendor is for; a refusal
  here adds a flag and a failure mode to protect edits that CI rejects anyway.
```

```
FINDING 2: check-manifest accepts unknown extra manifest fields
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/check-manifest.mjs:78-173 (checkManifest — allow-list of checks, no deny-list of keys)
  requirements: VZ-FOUND-002

Observed:
  Adding `spec.totally_made_up: "hello"` and top-level `attacker_note: "x"` to
  contracts/manifest.json leaves `node scripts/check-manifest.mjs` at exit 0,
  green. Every field the checker knows about is still verified.

Failure:
  A hand-added field carrying misleading provenance prose (e.g. a "note" that
  contradicts source_ref) would sit in the manifest unchallenged. No checked
  property is weakened by it; the risk is a human reading the file.

Perspective:
  developer

Recommendation:
  Either reject unknown keys under `spec`, or say in the file's header comment
  that unknown keys are ignored. I lean to the second — the current behaviour
  is defensible, it is just undocumented.

Acceptance criteria:
  Either an unknown key in `spec` fails check-manifest by name, or
  scripts/check-manifest.mjs states that unknown keys are ignored and why.

Tests:
  One case in scripts/check-manifest.test.mjs asserting the chosen behaviour.

Cross-repo implications:
  core: none | user: the change above | search: none | meta: none

Challenge:
  Strict schemas break forward compatibility: the next schema bump would fail
  on an older checker for no real reason. Documenting is the cheaper fix.
```

```
FINDING 3: git's stderr leaks from a deliberately-swallowed lookup
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/vendor-contract.mjs:71-78 (gitOrNull), :131 (origin/<ref> lookup)
  requirements: VZ-FOUND-002

Observed:
  `node scripts/vendor-contract.mjs --from ../core-scratch --ref <a commit id>`
  prints a bare `fatal: Needed a single revision` before its own output. It
  comes from gitOrNull's `rev-parse --verify refs/remotes/origin/<ref>`, whose
  exception is caught and ignored, but whose stderr is inherited.

Failure:
  Cosmetic. A confusing `fatal:` appears above a run that succeeded, which
  reads to a human like a failure the script ignored.

Perspective:
  developer

Recommendation:
  `stdio: ["ignore", "pipe", "ignore"]` in gitOrNull's execFileSync options.

Acceptance criteria:
  Vendoring from an explicit commit prints no `fatal:` line; the
  local-vs-origin divergence warning still fires when it should
  (demonstration F above).

Tests:
  Manual, or a scripts/ unit test asserting stderr is free of "fatal:".

Cross-repo implications:
  core: none | user: the change above | search: none | meta: none

Challenge:
  Suppressing git's stderr in a helper could hide a genuinely interesting
  failure later; the message is only noise for this one optional lookup.
```

```
FINDING 4: ci-required's waiting message misattributes the workflow that might still create an absent check
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/require-checks.sh (UNCHANGED by this PR — pre-existing)
  requirements: VZ-FOUND-002

Observed:
  In ci-required run 35547204935 on ca23fef:
  "waiting: … docker-build (no check-run yet, but run 35547204871 of
  .github/workflows/supply-chain.yml is in_progress and may still create one)".
  Run 35547204871 is supply-chain, which never produces a `docker-build` check.
  The guard's conclusion was nonetheless correct: it waited out every
  in-progress run and then reported docker-build "(not triggered,
  optional-if-absent)".

Failure:
  A reviewer reading the log is pointed at the wrong workflow. The gate's
  decision is sound; only the explanation is wrong. Pre-existing, untouched by
  this PR — recorded so it is not re-discovered.

Perspective:
  developer

Recommendation:
  Name the in-progress run(s) generically ("1 workflow run still in progress"),
  or match the check name to its owning workflow before naming one.

Acceptance criteria:
  The waiting line either names no workflow, or names one that can actually
  produce the missing check run.

Tests:
  A case in scripts/ci/require-checks_test.sh (the harness exists; 102 cases).

Cross-repo implications:
  core: none | user: the change above | search: none | meta: none

Challenge:
  It is log prose in a passing gate; changing require-checks.sh means touching
  the fan-in and its suite for a cosmetic gain.
```

**Observation (no finding raised).** The committed transcripts under `docs/evidence/revendor/` contain the owner's absolute home paths (`/Users/yosefgamble/…`) and macOS temp paths. This is the repository's existing convention — 69 files under `docs/` at base `f49bca4` already do it — and `vizra-user` is a private repository, so this PR introduces no new exposure. Worth a separate decision some day, not this PR's business.

## Verdict

**PASS.**

- Every in-scope acceptance bullet of the builder's plan (1–6) reproduced by me from a clean clone at `ca23fef…`, including all six red/green demonstration families, re-derived independently rather than read from the builder's transcripts.
- `ci-required` ran on this exact SHA, is green, read `.github/required-checks.txt`, waited for `e2e`, and its required set matches the jobs that actually ran. `docker-build`'s absence is a legitimate path-filter miss declared `?docker-build`, not a skipped required lane.
- No blocking finding. Four NITs, one of them pre-existing and none of them affecting a gate.
- Residual, unchanged and correctly documented: staleness relative to core's live `main` is not detectable from this repository, and a well-formed manifest naming a nonexistent commit passes. Closing it needs a read-only token for private `yegamble/vizra-core` — an owner action outside any pull request.

PASS is not a merge and not VERIFIED in the ledger; the chair records those.

## Cleanup

Scratch tree `<scratch>/verify-pr6/` (the vizra-user clone, the `core-scratch` clone, the spaces-in-path copy, and all logs) removed by exact path. Disk after cleanup: 11 GiB free, unchanged from the start. No Docker image was built. No shared cache touched.

`/Users/yosefgamble/github/vizra/vizra-core` was treated as read-only throughout: the only commands issued against it were `rev-parse`, `merge-base --is-ancestor`, `cat-file -e`, `branch -a --contains`, `ls-remote`, and one `git clone` **out of** it into my scratch. Nothing was written to it. Note for the chair: between the start and the end of this session that checkout moved from branch `main` to `feat/m0-fixtures` (still at commit `9e44d30`) and grew an untracked `internal/fixtures/`. That is the concurrently-dispatched fixture-corpus slice, not me — `origin/main` and the `api/openapi.yaml` blob `58030e7f…` used for every provenance comparison above are unaffected by a branch checkout.
