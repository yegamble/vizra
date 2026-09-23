# vizra-user PR #9 — public artifact visibility (AGENTS.md) — INDEPENDENT VERIFICATION

- **Repo / PR:** `yegamble/vizra-user` #9, branch `docs/public-artifact-visibility`, base `main` @ `7a3a572`
- **SHA verified:** `f9f9478eed8f0536345f88f59882716fcdcc9698`
  (`gh pr view 9 -R yegamble/vizra-user --json headRefOid` → `f9f9478…` at start **and at end**; state OPEN)
- **Verifier:** fresh war-room independent verifier. I did not write this change. Read-only on every
  repository; the only file I write is this one.
- **Date:** 2026-09-23

## Environment

```
macOS Darwin 25.5.0 arm64
node v22.14.0 (the .nvmrc pin, via ~/.nvm/versions/node/v22.14.0), npm 10.9.2
fresh clone: git clone https://github.com/yegamble/vizra-user.git; git checkout f9f9478 (detached)
private dir: …/scratchpad/vzv-vizra-user-pr9-0diIu6/  (mktemp -d; deleted at the end)
```

(A first `npm ci` was started on the default node v24.4.1 by mistake; I stopped it and re-ran
everything on the pinned v22.14.0 from a fresh `npm ci`. Only the v22 results are recorded.)

## 1. Head and diff scope

| Check | Result |
|---|---|
| `git rev-parse HEAD` | `f9f9478eed8f0536345f88f59882716fcdcc9698` |
| `git merge-base HEAD origin/main` / `origin/main` | both `7a3a572b5a…` — one commit on top of main |
| `git diff --stat origin/main...HEAD` | `AGENTS.md | 58 +++++++---` — **AGENTS.md only**, +49/−9 |
| Is AGENTS.md digest-hashed? | No. `docs/evidence/VZ-FOUND-008/mutation-digests.txt` hashes `.github/workflows/e2e.yml`, `e2e/demos/console-error.demo.ts` and five `e2e/harness/*.ts` files; `grep -c AGENTS` → 0. No ledger lines needed. |

## 2. Lanes, run by me at f9f9478

| Command (in the clone) | Exit | Result |
|---|---|---|
| `npm ci` | 0 | `found 0 vulnerabilities` |
| `npm run ci` | 0 | eslint clean; `tsc --noEmit` 0; vitest **19 files / 627 tests passed, 0 skipped**; `next build` ✓ compiled; hygiene `OK: 308 text source(s) … 17 mutation-digest line(s) match this tree` |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | `OK: .github/workflows/e2e.yml still drives the built image … redacts artifacts before EVERY upload step publishes them.` |

This closes the builder's stated gap ("did not run `npm run build` locally"): the full `npm run ci`,
build included, is green on this SHA on my machine. `git status --porcelain` empty after the run.

## 3. GitHub CI on f9f9478

`gh api repos/yegamble/vizra-user/commits/f9f9478eed8f0536345f88f59882716fcdcc9698/check-runs` → 7 runs:

| check-run | status | conclusion | completed |
|---|---|---|---|
| frontend | completed | success | 17:35:44Z |
| contract | completed | success | 17:35:20Z |
| e2e | completed | success | 17:36:42Z |
| deps-scan | completed | success | 17:35:17Z |
| image-scan | completed | success | 17:36:15Z |
| GitGuardian Security Checks | completed | success | 17:34:56Z |
| **ci-required** | completed | **success** | 17:37:25Z |

`ci-required` job log (`gh api repos/yegamble/vizra-user/actions/jobs/107301910501/logs`):
`CHECK_SHA: f9f9478…`, manifest `.github/required-checks.txt` = `frontend, contract, ?guard,
?docker-build, e2e`; it waited for all three in-progress required lanes, recorded
`(not triggered, optional-if-absent): guard` and `… docker-build` (both path-filtered to
`.github/**`/`scripts/ci/**`/Docker inputs, which an AGENTS.md-only diff does not touch), and ended
`OK: every required check on f9f9478… concluded success.` Every non-optional manifest entry
(frontend, contract, e2e) has a real check-run on this SHA with conclusion success. No lane is
listed-but-unexecuted.

## 4. Factual claims, with my own calls

| Claim in the new paragraph | My call | Result |
|---|---|---|
| repo is PUBLIC; `vizra`, `vizra-core`, `vizra-search` too | `gh repo view yegamble/vizra-user --json visibility,isPrivate`; loop over the four | `{"isPrivate":false,"visibility":"PUBLIC"}`; all four `PUBLIC` — **true** |
| job logs 90 days, repo setting `{"days":90}` | `gh api repos/yegamble/vizra-user/actions/permissions/artifact-and-log-retention` | `{"days":90,"maximum_allowed_days":90}` — **true** |
| "uploaded artifacts: **3 days** (`retention-days: 3`, a ceiling `check-e2e-lane.mjs` enforces)" | `grep -rn retention-days .github/workflows/`; `gh api --paginate repos/yegamble/vizra-user/actions/artifacts` | e2e.yml:247 `retention-days: 3` and the ceiling at `check-e2e-lane.mjs:431-433` / `:1260-1269` — true **for the e2e upload step as it is now**. **Not true of the repository's public artifacts**: 59 unexpired artifacts = 29 `npm-audit-*` + 29 `trivy-image-*` at **30 days** (`supply-chain.yml:107,182`), and **one `playwright-artifacts-35536837315-1`, created 2026-09-20T20:53:24Z, expires 2026-10-04T20:53:23Z (14 days), `expired:false`** — see FINDING 1 |
| "Nothing in this repository shortens it [the log retention]" | grep of workflows for log deletion | none — true |
| "a line in a job log cannot be recalled or redacted after it is written" | reasoning (not executed) | overstated — a run's logs can be deleted (`DELETE /repos/{owner}/{repo}/actions/runs/{run_id}/logs`, or deleting the run); FINDING 4 |

## 5. Each "PR A still guarantees" sentence vs PR A's merged code and closing verification

Compared against the merged text of AGENTS.md §"Artifact privacy" (lines 507-825 at this SHA, unchanged
by this PR), the merged code, and `docs/evidence/warroom/2026-09-23-vizra-user-pr8-closing-VERIFY.md`
(rounds at f0f702e → f6d245f → cf053a3 → c2ff445, final `PASS (local; CI BLOCKED)`).

| New sentence | Source it restates | Verdict |
|---|---|---|
| upload only on a red lane, only after the pinned redaction step succeeded, only the three allowlisted paths | e2e.yml:239 `if: failure() && steps.redact.outcome == 'success'`, paths at :242-245; AGENTS.md:635-638, :985-996 (pinned upload, look-alikes refused); closing VERIFY V2/R3-FINDING H closed | matches; no over-claim **for uploads made under the current workflow** |
| `playwright-report/` not uploaded; nothing under `.vizra-e2e/` uploaded by any workflow | AGENTS.md:778-780; `check-e2e-lane.mjs:1250-1257` (`include-hidden-files`); supply-chain uploads only `npm-audit.json`, `trivy-image.json` | matches for current workflows. **A pre-PR-A artifact that DOES contain `playwright-report/` is still public** — FINDING 1 |
| query strings and fragments redacted in the four URL shapes, "and nothing else is"; every NOT-covered row published as recorded | AGENTS.md:509-569, :782-797, :1246 | no over-claim. It is a slight **under**-claim: the merged text says "query strings, fragments **and `Location`**" (:510, :1246), and redact.ts also sanitises CR/LF/`::`. FINDING 5 (NIT) |
| `# Page snapshot` suppressed in CI by `PLAYWRIGHT_NO_COPY_PROMPT` and refused at the upload gate | AGENTS.md:774 (the same words), layers 1-3 at :665-761, and "What still gets through" :750-761; closing VERIFY R6/RC accepted this wording | **same strength as the merged row :774**, not stronger. It does not repeat the residuals (pre-config preload routes, an earlier `run:` step rewriting `redact-artifacts.sh`), but the heading says "at their measured strength" and the residual paragraph sits 90 lines above. FINDING 5 (NIT) |
| traces carry no credential only because nothing authenticates; `no-credentials-in-specs.test.ts` is a tripwire, not a control | AGENTS.md:803-815; file exists `e2e/harness/no-credentials-in-specs.test.ts` | matches |
| job log: `list` reporter prints received value + source excerpt; `Container logs` prints last 200 lines as-is; only harness messages pass through redact.ts | `playwright.config.ts:90-91` `["list"]`; e2e.yml:160-162 `docker logs vizra-user-e2e 2>&1 \| tail -200 \|\| true`; `redact.ts:130-175` (`sanitiseExternalText`: `%25/%0A/%0D` escaping, CR/LF → ⏎, C0 → U+FFFD, leading-whitespace `::` broken, 200-char cap) | accurate; the sanitiser description is a subset (no over-claim) |
| hard rule unchanged; a spec that authenticated would publish the credential for up to 90 days (log) / 3 days (artifact) | AGENTS.md:803-815 | matches |

No sentence claims a control stronger than PR A measured. The only false statement is the
unqualified retention/exposure inventory (FINDING 1).

### Evidence for FINDING 1 — the surviving public pre-PR-A artifact

```
$ gh api --paginate 'repos/yegamble/vizra-user/actions/artifacts?per_page=100' \
    --jq '.artifacts[] | select(.name|startswith("playwright")) | {id,name,size_in_bytes,created_at,expires_at,expired,workflow_run}'
{"id":10612777314,"name":"playwright-artifacts-35536837315-1","size_in_bytes":1251268,
 "created_at":"2026-09-20T20:53:24Z","expires_at":"2026-10-04T20:53:23Z","expired":false,
 "workflow_run":{"head_branch":"chore/e2e-artifact-upload-proof","head_sha":"0401d5ea78cc…","id":35536837315}}
$ gh run view 35536837315 -R yegamble/vizra-user --json displayTitle,conclusion
"THROWAWAY — prove the e2e artifact path executes (do not merge)", failure
$ gh api repos/yegamble/vizra-user/actions/artifacts/10612777314/zip > a.zip; unzip -d x a.zip
x/playwright-report/index.html            <- carries <template id="playwrightReportBase64"> (grep -l hit)
x/playwright-report/data/*.zip|*.md|*.png|*.webm
x/test-results/…/error-context.md          <- 4 files carry "# Page snapshot"
```

I read the page snapshot: it is the foundation skeleton page ("Vizra … Foundation skeleton. No product
surface is implemented yet"). A grep of the unpacked trace archives for `?name=value` found no live
query string. So the **content is benign** — nothing authenticates, as the paragraph says — but the
artifact is public, holds exactly the three things the new paragraph says are not published
(the base64 report archive, `playwright-report/`, page snapshots), and outlives the stated 3 days
until 2026-10-04. It is also the artifact AGENTS.md:583 cites ("run 35536837315 … 239 `?<redacted>`").

## 6. Left-behind sentences that still say "private" / "collaborators"

`git grep -n -i -E "collaborator|private repo|is private|\*\*private\*\*|PRIVATE\b|not public"`:

| Location | What it says | Judgement |
|---|---|---|
| `.github/workflows/e2e.yml:231-237` (comment above the upload step) | "`yegamble/vizra-user` is a PRIVATE repository, so artifacts and job logs are readable by its collaborators … not by the public" | **False audience statement** — now contradicts AGENTS.md. Digest-hashed workflow; changing it needs a re-digest. Pre-existing on main, not introduced or worsened by this PR → REQUIRED follow-up, not a blocker of this docs PR (FINDING 2) |
| `scripts/ci/check-e2e-lane.mjs:1268` (retention refusal message) + its transcript `docs/evidence/VZ-FOUND-008/d7b-second-ungated-upload-RED.txt:5` | "readable by every collaborator on this private repository" | same — false audience in a guard message; code + committed transcript → REQUIRED follow-up (FINDING 2) |
| `e2e/harness/redact.ts:143` (doc comment) | "a durable log that every collaborator on this private repository can read" | same, rationale comment; the rationale is *stronger* now → follow-up (FINDING 2) |
| `AGENTS.md:142`, `scripts/check-manifest.mjs:14,31` | vizra-core "is **private** … no read token" | stale in the **pessimistic** direction (claims a blocker that no longer exists); not a false guarantee. Follow-up: the staleness check is now implementable without a token (FINDING 3) |
| **not named by the builder:** `.github/workflows/contract-ci.yml:23`, `scripts/vendor-contract.mjs:10`, `docs/evidence/revendor/README.md:62` | vizra-core "is private" | same class as the row above (FINDING 3) |
| `.github/workflows/ci-required.yml:35` | "the read fails on a private repository" | generic and still correct — no change needed |

None of the left-behind sentences is introduced by this PR, and fixing any of them here would move
hashed files or code into a docs-only PR. They do not block PR #9. The e2e.yml / check-e2e-lane.mjs
pair is the one that matters: it is the text a reader sees *at the upload step*.

## Findings

```
FINDING 1: "uploaded artifacts: 3 days" is false for the repository's public artifacts today
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     AGENTS.md:833-837 (at f9f9478); .github/workflows/supply-chain.yml:107,182;
             GitHub artifact 10612777314 (run 35536837315)
  requirements: VZ-FOUND-008

Observed:
  The paragraph says "Two retention periods apply … uploaded artifacts: 3 days". The artifacts API
  lists 59 unexpired public artifacts: 58 supply-chain scan reports at retention-days 30, and
  playwright-artifacts-35536837315-1 created 2026-09-20 with a 14-day expiry (2026-10-04,
  expired:false). That artifact predates PR A's allowlist and PLAYWRIGHT_NO_COPY_PROMPT: it
  contains playwright-report/index.html with the base64 report archive, playwright-report/data/,
  and four error-context.md files with a "# Page snapshot". Its content is benign (the skeleton
  page; no live query string found).

Failure:
  The one paragraph whose job is an exact exposure inventory after going public understates it:
  a reader concludes every public e2e artifact is ≤3 days old and was produced under PR A's
  controls. Neither is true until 2026-10-04. Harm today is nil (benign content), but the sentence
  is a false guarantee of the kind the war room does not merge.

Perspective:
  developer | operator

Recommendation:
  Scope the bullet: "the `e2e` lane's artifact: 3 days (…ceiling); the `supply-chain` scan reports
  (`npm-audit-*`, `trivy-image-*`): 30 days". Add one sentence naming the pre-PR-A artifact
  (`playwright-artifacts-35536837315-1`, 14 days, expires 2026-10-04, uploaded before the
  allowlist — it contains `playwright-report/` and page snapshots of the skeleton page) and that
  deleting it early is an owner decision. Docs-only; no hashed file moves.

Acceptance criteria:
  Every retention figure in the paragraph matches `gh api …/actions/artifacts` on the day it is
  written; the paragraph names each artifact family that is public and its retention; nothing in
  it implies all public e2e artifacts post-date PR A while one does not.

Tests:
  Docs-only: re-run the gh api listing above and compare. No harness change.

Cross-repo implications:
  core: check its own supply-chain/e2e retention before making the same statement | user: this |
  search: same | meta: same (all four are public)

Challenge:
  The paragraph sits inside the browser-lane section, so "uploaded artifacts" can be read as
  "this lane's uploads under the current workflow", which is true; and the stale artifact is
  benign and self-expires in 11 days. Counter: "Two retention periods apply" is phrased as the
  repository's complete answer, and the chair's rule is that a claim may not exceed what was
  measured — the listing I measured contradicts it.
```

```
FINDING 2: three code/workflow texts still say artifacts and logs are collaborator-only
Severity:    REQUIRED (follow-up; not a blocker of this docs-only PR)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     .github/workflows/e2e.yml:231-237; scripts/ci/check-e2e-lane.mjs:1268;
             docs/evidence/VZ-FOUND-008/d7b-second-ungated-upload-RED.txt:5; e2e/harness/redact.ts:143
  requirements: VZ-FOUND-008

Observed:
  e2e.yml:232-234 "PRIVATE repository, so artifacts and job logs are readable by its collaborators
  … not by the public"; check-e2e-lane.mjs:1268 "readable by every collaborator on this private
  repository"; redact.ts:143 "every collaborator on this private repository can read".

Failure:
  After this PR merges, AGENTS.md and the comment directly above the upload step contradict each
  other; the step-side text understates the audience. No control depends on it.

Perspective:
  developer

Recommendation:
  One follow-up PR: reword the three texts to "public", recompute the e2e.yml digest line with
  demonstrate.sh's own mutation, regenerate the d7b transcript. Until then, optionally add one
  clause to this paragraph: "the comment in e2e.yml and the guard's message still say private;
  this paragraph supersedes them".

Acceptance criteria:
  `git grep -n -i "collaborator"` finds no claim that artifacts or logs are collaborator-only;
  check:hygiene digest lines match.

Tests:
  npm run check:hygiene; scripts/ci/require-checks_test.sh (message text); check-e2e-lane.sh.

Cross-repo implications:
  core/search/meta: grep for the same wording | user: this

Challenge:
  They are comments and a refusal message; nobody's data depends on them. True — which is why
  this is a follow-up and not a blocker here.
```

```
FINDING 3: "vizra-core is private" appears in more places than the builder's follow-up list
Severity:    SHOULD
Confidence:  high
Affected:    vizra-user — AGENTS.md:142, scripts/check-manifest.mjs:14,31 (named by builder);
             .github/workflows/contract-ci.yml:23, scripts/vendor-contract.mjs:10,
             docs/evidence/revendor/README.md:62 (not named)
Observed:    each says the staleness check is blocked because vizra-core is private and no token exists.
Failure:     stale in the pessimistic direction; the owed staleness check is now implementable with
             no token. Not a false guarantee.
Recommendation: route the full list of six locations with the "Owed — staleness" item.
```

```
FINDING 4: "a line in a job log cannot be recalled or redacted after it is written" is overstated
Severity:    NIT
Confidence:  medium (reasoned from the documented REST endpoint; not executed)
Affected:    vizra-user — AGENTS.md:840-841 (at f9f9478)
Observed:    a run's logs can be deleted (DELETE /repos/{owner}/{repo}/actions/runs/{run_id}/logs,
             or deleting the run). A line cannot be edited, and deletion does not un-publish what was read.
Failure:     errs toward caution, but as incident guidance it omits the one remedy that exists
             (rotate, then delete the run's logs).
Recommendation: "cannot be edited; deleting the run's logs removes it from GitHub but not from anyone
             who already read it".
```

```
FINDING 5: minor under-statements versus the merged section
Severity:    NIT
Confidence:  high
Affected:    vizra-user — AGENTS.md:852-858 (at f9f9478)
Observed:    "redacted … and nothing else is" omits `Location` (merged :510, :1246 cover it); the
             page-snapshot bullet does not point at "What still gets through" (:750-761) although
             the heading says "at their measured strength".
Failure:     none is an over-claim; a reader could miss the residuals.
Recommendation: add "and `Location`", and "(subject to 'What still gets through' above)".
```

## Cleanup

`rm -rf …/scratchpad/vzv-vizra-user-pr9-0diIu6` (clone, node_modules, logs, the downloaded
artifact) — by exact path, after this file was written.

## Verdict

- Diff is AGENTS.md only; no hashed file touched; head unchanged start→end.
- `npm run ci` (build included) exit 0 locally on the pinned node; lane guard exit 0.
- CI: all 7 check-runs success on f9f9478; `ci-required` success with the manifest's three
  mandatory lanes present and green and the two optional lanes correctly absent.
- Visibility and 90-day log retention confirmed with my own calls. Every "PR A still guarantees"
  sentence is at or below the strength PR A measured.
- **But the retention/exposure inventory is false against the live artifact listing (FINDING 1,
  REQUIRED):** 30-day supply-chain artifacts and a 14-day pre-PR-A e2e artifact, containing the
  report archive and page snapshots, are public. The fix is a few docs lines in this PR.

FINAL VERDICT: FAIL — SHA f9f9478eed8f0536345f88f59882716fcdcc9698
