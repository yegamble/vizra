# Owner inbox

Things only the owner can decide or supply. Item numbers are the old board's and never change; new items get the next number. The board carries a one-line index of the open items; the full text lives here. September text is verbatim from the old board ([archive](archive/WARROOM-BOARD-through-tick-257.md)).

## Open

### 3

Mockup controls with **no ledger ID** need a scope decision (add to the ledger, mark unavailable, or drop). Search page: Save/bookmark on cards and the "Saved" tab (is Save the same thing as Favorite, which the ledger has?), the "Series" scope and "Editorial series" facet, the view-density switcher, "Interesting" / "Most loved" / "Most viewed" as sort orders, the "Analog / Film" facet, the per-card `4K` badge, the public "refreshed moments ago" label, related-query chips; and the `RAW` badge contradicts VZ-MEDIA-002, which declines RAW. Public pages (25 items, `INVENTORY-public.md` §g): the whole "Series" entity, verified badge, commissions / "Hire", audio playback and the Editorial Journal, "For You", ⌘K palette, artist showcase + style tags, profile Featured tab, "Member since" / location / most-used camera, footer Share/Email, Help & Feedback, "New" badge, "refreshed hourly". Account pages (full list of 18 groups in `INVENTORY-account.md`): plan/subscription card (Vizra has no billing product), drafts as a state, the whole Push notification channel + quiet hours, weekly digest, muted tags, per-member comment filter, self-deactivation, tagline/pronouns/multi-link profile fields, commissions + booking, engagement rate, audience geography, passkeys, SMS 2FA, Instagram/Adobe connections, scheduled publish, "AI training" toggle, "Hire", RAW/TIFF upload chips, and the "goimg Pro" billing card (Vizra has no billing product).

### 4a

> Owner decision 2026-11-10 #2: ruled on separately. **VZ-MEDIA-001 stays blocked until this is ruled.**

**Architecture ruling needed before M1 (VZ-MEDIA-001) — ADR-001's AVIF/HEIC split is not implementable as written.** The core builder found that libvips decodes AVIF *through libheif* (dav1d/aom are libheif's backends, not a separate path), so the current image — which excludes libheif and asserts `no heif` — also has no AVIF. Chair's recommendation: build libheif with AV1 backends only (dav1d decode, aom or svt encode) and WITHOUT libde265/x265, so AVIF works and HEIC/HEVC stays out by default (VZ-MEDIA-010 keeps HEIC as the opt-in); change the image assertion from "no heif loader" to "heif loader present, no HEVC codec". ADR-001 is Accepted and immutable, so this lands as a new amending ADR — owner approves.

### 4b

> Owner decision 2026-11-10 #2: ruled on separately.

**ADR-009 tooling for the same amending ADR:** the fixture generator is Go-standard-library-only (byte-identical across amd64 and arm64) rather than the libvips + exiftool script ADR-009 names; the manifest-of-record, sha256-per-file and generator-version decisions are implemented as written. **ADR-004 / ADR-002 wording for the same amending ADR:** ADR-004's table sketch carries the claim index in the wrong column order (`state, run_after, priority` vs the claim's `ORDER BY priority, run_after`; should be a partial index on queued rows); ADR-002 lines 222–224 are ambiguous about whether `instance_settings` is M0 or M2 schema (the backend seat reads it as M2 — say so). **ADR-002 amendment (small):** the core↔search contract lives in a separate file `api/search-internal.openapi.yaml`, kept out of core's own route↔spec check; record it in the same amending ADR.

### 5

> Rulesets part DECIDED 2026-11-10 #3 and APPLIED 2026-11-10 on vizra, vizra-user and vizra-search (ids 26967150, 26967155, 26967161; no bypass actors, so the owner is bound too). vizra-core waits for its CI repair. The fork-PR approval setting in the first sentence is still open.

**(tick 256 addition: the security seat recommends the fork-PR workflow approval setting `all_external_contributors` instead of the current `first_time_contributors` — on a `pull_request` run the workflow file comes from the PR, so a returning outside contributor can upload anything; S-7 in `docs/evidence/warroom/2026-09-23-vizra-user-pr10-allowlist-PLAN-REVIEW-security.md`. Your call; the chair will apply it with `gh api` on your word.)** **UPDATE tick 198: the repos are now PUBLIC, so rulesets work on the Free plan — say the word and the chair applies them with `gh api` (require `ci-required`, block force-push/deletion, linear history; CODEOWNERS review would then gate the chair's own merges, so decide whether to require it).** **Rulesets cannot be applied on the current GitHub plan.** The core verifier called the rulesets API and got `403 Upgrade to GitHub Pro`: on a Free personal plan GitHub does not enforce rulesets or branch protection on PRIVATE repositories. So CODEOWNERS is unenforceable, `ci-required` is advisory, and any PR can edit the gate that judges it — the war room's verifier-gated process is currently the only control, and per Q-032 no ledger entry can reach VERIFIED on CI evidence alone. Options for the owner: (a) GitHub Pro (paid — owner-only spend decision), (b) make the repositories public, which enables rulesets for free (a disclosure decision; the security seats assumed the repos "may be public" when withholding exploit detail), (c) move the repos to an organization on a plan that supports rulesets, or (d) accept the residual for now and record it as a release-gate item in `docs/RELEASE_ACCEPTANCE.md`. Chair's recommendation: decide before M1 lands auth code; (d) is tolerable for M0 only. Original item — **Rulesets (Q-032, owner action):** once the first PRs merge, each repo's `main` needs a ruleset requiring the `ci-required` context, blocking force-push and deletion, linear history, and CODEOWNERS over `.github/**` and `scripts/ci/**` (ADR-002 items 9–10). Until then a green check is advisory, and the builders say so in each repo's AGENTS.md. Note: GitHub does not enforce rulesets on private repos on a Free personal plan — check the plan, or say the word and the chair applies them with `gh api`.

### 6

**Cross-repo contract freshness:** vizra-user and vizra-search vendor core's contract and verify its sha256, but cannot detect that the vendored copy is *stale* without read access to private vizra-core from CI — a fine-grained read-only token as an Actions secret, or making the check a meta fan-in lane. Owner supplies the credential or picks the fan-in.

### 7

> Owner decision 2026-11-10 #8 authorizes deploys to one disposable rehearsal host the owner provides. The host has not been provided yet.

Still open from 2026-09-15: Q-008 tenancy, Q-041 notes/people, Q-042 messages; a disposable Ubuntu 24.04 amd64 host for the install rehearsal; Q-036 domain before M6.

### 8a

> Owner decision 2026-11-10 #2: ruled on separately.

**Ledger wording to ratify (VZ-INSTALL-003 recovery case).** The ledger says "Restart re-mints; old token invalid". The security seat showed that an unconditional re-mint at boot lets any restart (OOM, env edit, updater, crash loop) silently invalidate the token the operator is holding — a denial-of-claim — and, combined with printing the token at boot, writes a fresh live owner credential into the logs on every restart. Chair ruling (reversible in code, no schema impact): the token is delivered by `docker compose exec api vizra claim-token`, which ALWAYS supersedes the previous token and mints a new one; boot prints the command, not a credential; printing to stderr is an explicit opt-in. Proposed ledger sentence: "A lost token is recoverable: `vizra claim-token` mints a new one and invalidates the previous; an expired token is never accepted." Also touches PRODUCT_SPEC §15 step 4 and copy key `claim.help.body`.

### 8b

> Owner decision 2026-11-10 #2: ruled on separately. **M1-B stays blocked until this is ruled.**

**ADR-003 interpretation to ratify + one-line amending ADR before M1-B merges.** (i) The CSRF table's "Setup wizard \| loopback bind and one-time X-Setup-Token and Host allowlist" row is read as the INSTALLER wizard (VZ-ISSUE-004), not `POST /api/v1/setup/claim-owner` — both seats concur, and the other reading makes the approved claim page unbuildable. Requested amendment: rename the row "Installer setup wizard" and add a row "Unauthenticated pre-claim JSON POST \| credential in body \| exact JSON content type; Origin / Sec-Fetch-Site must not be cross-site when present \| allow". (ii) "Vizra version tag… without a second column" is read as a plain standard PHC string whose embedded `m,t,p` are the version.

### 8c

**User erasure vs the audit trail (decision needed before M2).** `audit_events` rows name their actor with `ON DELETE RESTRICT` (the frozen 0003 CHECK makes SET NULL impossible) and become append-only in M1-A, so a user row that has ever acted can never be deleted: erasure becomes scrub-and-tombstone, and audit rows must never carry PII beyond the username. The audited retention / anonymisation path 0003 promised is still owed; the chair will add a ledger ID for it. Say if Vizra must support hard deletion of users.

### 8d

> Owner decision 2026-11-10 #2: ruled on separately.

**ADR-003 "owner is single and cannot be demoted" vs owner transfer.** The ledger (`VZ-ADMIN-USERS-001`, meta PR #5) now records owner-transfer and tombstoned-owner recovery cases, which move the owner role to another user and leave the previous owner in a lower role — contrary to the Accepted ADR-003's literal text (also PRODUCT_SPEC:24). Only you can amend an Accepted ADR. Options: an amending ADR permitting transfer (recommended — an owner who cannot hand over the instance or recover from a deleted owner account strands the instance), or drop transfer from the ledger. Also: the ID migration 0005 means by "carries its own ledger ID" is `VZ-AUDIT-001` (inbox 8c).

### 8e

**Owner-claim lockout residual (security seat, core PR #8, tick 156).** Until M1-B's concurrency bound, anyone who can reach an unclaimed instance can keep the first-run owner claim closed by sending 600 claim requests per 15-minute window (~0.67/s sustained); `claim-status` reveals which instances are unclaimed, so this is scanner-scale; claim-status has the same shape at 3000/15 min; a restart does not help; recovery today is to firewall the port during setup or delete the cache key. Options: accept it as a documented residual until M1-B with a README/doctor recovery line (queue 2n; recommended — the M1-B bound is the real fix), or pull a per-origin claim ceiling forward into M1-A. Merge of core #8 does not wait on this; release does.

### 9

> Update 2026-11-10: `image-scan` on core `main` (`27cee54`) now reports 69 findings at or above HIGH, 1 of them CRITICAL (run 42770496103). It has been red on every scheduled run since 2026-09-22.

**Base-image CVEs with no fix (decision: accept, or an expiring ignore file).** vizra-core's new `image-scan` lane ran for the first time on PR #7 and is red: 0 CRITICAL, 48 HIGH, none with a fixed version — 13 distinct CVEs in Debian 13 base packages (`ncurses`, `libsystemd0`, `libtiff6`, `libexpat1`, `util-linux`, `perl-base`), the same packages `main`'s image already carries. The lane is NOT a required check, so merges are not blocked. The chair will not weaken the threshold or add an ignore file on its own. Options: leave it red as a standing true signal; or an owner-reviewed, EXPIRING `.trivyignore.yaml` listing exactly those CVEs so that a NEW finding turns the lane red again. The builder recommends against raising the failure threshold to CRITICAL (it would hide the decoder libraries in an image whose job is decoding untrusted images).

### 11

> Update 2026-11-10: the artifact's stated expiry (2026-10-04) has passed; only the path-scrub question remains.

**(tick 202) Also: a pre-PR-A public artifact `playwright-artifacts-35536837315-1` (id 10612777314) holds a Playwright HTML report with page snapshots of the skeleton page (harmless content per the verifier) and expires 2026-10-04 — delete it early? (`gh api -X DELETE repos/yegamble/vizra-user/actions/artifacts/10612777314`, your call).** **Public-repo consequences (tick 194, your instruction).** Actions artifacts and job logs are now world-readable for their retention period; committed evidence transcripts contain local paths such as `/Users/yosefgamble/…` (already noted by an earlier verifier as the repos' convention). A docs PR corrects vizra-user's "collaborators only" sentence. No action needed unless you want the paths scrubbed.

### 12

**(tick 246) VZ-FOUND-008's acceptance text vs Lane A with pixels off (user #10 sentinel F-4, Q-4).** The ledger (`docs/quality/features.json`, generated from `ledger-generator/s0_foundation.py:45`) requires "screenshots and traces retained on failure" and that CI "uploads artifacts"; `PRODUCT_SPEC.md:127` and `DEFINITION_OF_DONE.md:10` expect 390/1440 screenshots. On the now-PUBLIC repos, Lane A publishes no pixels (user #10) — and after the tick-247 re-plan (allowlist gate) it publishes **no traces either**: only `results.json` + `error-context.md` text. Chair's proposal, NOT applied: those bullets are met by user PR B's authenticated Lane B (pixel artifacts not public), so VZ-FOUND-008 stays short of VERIFIED on them until PR B merges; the acceptance text is unchanged. Alternative: you reword the bullet. The chair will not change the target.

### 13

**Coverage gaps found on 2026-11-10 (reported, no scope added). Decide which get their own queue row, ledger ID or milestone.**

| Capability | Ledger ID | Milestone | Queue | Gap |
|---|---|---|---|---|
| CLI install | VZ-INSTALL-001/002/004 | M0 | lumped into queue 7 | no own queue row; no code exists |
| Wizard install | VZ-INSTALL-002 (`vizra setup`, `--web`) | M0 | lumped into queue 7 | no own queue row; RELEASE_ACCEPTANCE does not name it |
| IPFS off / external / managed | VZ-TOPOLOGY-005; VZ-IPFS-001/002 | M4; M6 | none | no queue item; external overlay is a placeholder; no managed overlay |
| Local / external Postgres, Redis | VZ-TOPOLOGY-001…003 | M0 | merged as meta #4 | status never recorded; evidence is render-only, no boot |
| QA | VZ-FOUND-008, VZ-CI-003, VZ-A11Y-001, VZ-RESPONSIVE-001, VZ-CONTROLS-001 | M0, M1 | harness merged | no queue rows for a11y, responsive, controls |
| Security testing | VZ-CI-004, VZ-OPS-008, VZ-PRIVACY-001, VZ-SECURITY-003 | M0, M1, M2 | 2b, 2c, 2w | no ID for abuse / pen-test style testing; four proposed VZ-SEC IDs unratified |
| Deployment rehearsal | VZ-BACKUP-001/002, VZ-UPGRADE-001/002, M7 | M1, M4, M7 | none | no queue rows; rehearsal host not yet provided |
| CI repair | VZ-CI-001/002/004 | M0 | several hardening items | no ID or item for "required lanes green on main in all four repos today" |
| Audit trail | VZ-AUDIT-001 | none | none | in the ledger (192 entries, core profile) since meta #5, but in no row of `docs/MILESTONES.md` and not in `docs/quality/release-profiles/core.json` (141 ids against the ledger's 142) |

### 15

> RULED 2026-11-11 #2, conditionally; the condition for amending was NOT met, so this stays open. The chair checked vizra-core `5f615d7`: Redis carries **rate-limit counters**, not only cache. ADR-003 "Rate limits": "Counters live in Valkey; if Valkey is unreachable the api falls back to a per-process in-memory limiter and marks readiness degraded". In code: `internal/cache/ratelimit.go` (`FallbackLimiter`), wired at `cmd/api/main.go:96`, used by the owner-claim failure budget and the setup route ceilings (`internal/httpapi/setup_limits.go:81-111,154-158`), an auth surface. With Redis down the limits become per process, so N replicas allow N times the limit; `/readyz` says `degraded` (`probes.go:192-203`). Sessions are in PostgreSQL (ADR-003: "never in the cache") and job dispatch is PostgreSQL (ADR-004); the worker does not open the cache. Today nothing else is stored in Redis. Nothing was amended.

**VZ-FOUND-005: Redis in readiness (new 2026-11-10, tick 260).** The ledger outcome says `/readyz` "fails when DB/Redis/storage unavailable". vizra-core returns 200 with `degraded` when the cache is down and tests that on purpose (`TestReadyzCacheDownIs200Degraded`), following ADR-002. One of the two has to change before the ID can be recorded; changing the ledger text or the ADR is yours. Evidence: `docs/evidence/warroom/2026-11-10-vizra-core-pr17-readyz-storage-VERIFY.md`.

## Closed

### 0

> CLOSED 2026-11-10 by observation: the repos are public and Actions starts jobs (vizra-core run 42770496103 ran to completion on 2026-11-10). See RECONCILE-2026-11-10.md.

**URGENT — GitHub Actions billing (2026-09-23 ~06:21Z).** Every new Actions job on the account is refused before it starts: "The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings." All four Vizra repos are private, so they share one Actions allowance; the last green runs were vizra-core 04:51Z and vizra-user 05:29Z. Until it is fixed, no `ci-required` can go green, so NO merge can happen (merge condition 2). The chair cannot read usage (`gh auth refresh -s user` would be needed, and billing is owner-only spend). After the fix: `gh run rerun 35826344782 -R yegamble/vizra` re-runs meta PR #4's CI. Options for you: fix the payment/spending limit; or make the repos public (Actions minutes are free for public repos — but that is a visibility decision with privacy implications); or run a self-hosted runner.

### 1

> CLOSED by owner decision 2026-11-10 #5: CI-only reproduction accepted; no install.

Install `exiftool` (`brew install exiftool`) or accept CI-only reproduction for the fixture corpus.

### 2

> CLOSED by owner decision 2026-11-10 #6. 56 GiB were free on 2026-11-10.

Free disk space — 19 GiB free limits Docker and Playwright work.

### 4

> CLOSED by owner decision 2026-11-10 #1: design accepted with the chair's five answers. Chair still owes a ledger ID for the CLI password reset, through the generator.

**DESIGN ACCEPTANCE — the first-slice design is ready for your review** (independent reviewer's final verdict: SHOW; known soft spot: the phone lightbox `V5` makes the photo smaller than its action sheet): https://www.figma.com/design/JXgRItauynmT0g8vSJB3oR — pages "M1 · Auth & system" and "M1 · Library, viewer, albums", plus the library. Independent review and re-check: `docs/design/figma/REVIEW-first-slice.md`. Your acceptance (Prompt 02 gate) unblocks the app-shell PR, the Search page and all of M1. **Top five questions, one line each:** (1) `Download original` in the M1 viewer — keep as an owner-only action, or remove until M3? (2) Include a signed-out public photo page in the first slice? (3) Duplicate e-mail at sign-up — allow, accept the enumeration leak, or pull VZ-AUTH-002 forward? (4) Accept no password recovery at M1, or pull a host-side CLI reset into M1 (chair recommends the CLI reset)? (5) One visibility vocabulary — "Unlisted" or "Link only"? Earlier note — Design acceptance once the Figma first-slice pages exist. **Product questions raised by the auth designs (10 in `FIRST-SLICE-auth-system.md` §7), the sharp ones:** (a) **there is no password recovery at all at M1** — reset-by-email and admin reset are both M2; chair recommends pulling a host-side CLI reset (`vizra` command, no email dependency) into M1 so a freshly claimed owner cannot lock themselves out; (b) a duplicate e-mail at sign-up cannot be made enumeration-safe at M1 without VZ-AUTH-002 — accept the leak for M1 or pull verification forward; (c) is the pending action resubmitted after session-expired re-auth; (d) status code for "already claimed" (409 drawn); (e) near-limit quota threshold (90 % drawn). **From the library/viewer designs (15 in `FIRST-SLICE-library-viewer-albums.md` §7):** (f) "Download original" is drawn in the viewer because the chair briefed it, but VZ-DOWNLOAD-001 is **M3** — chair recommends keeping an owner-only download of one's own original in M1 (the golden path proves the original survives and authorized access works) and leaving the visitor-facing four-way download setting in M3; owner decides; (g) deleting an album that has sub-albums — the copy says they are re-parented, which ADR-007 does not rule on; (h) sign-off on a theme-invariant near-black photo stage; (i) `Needs attention` filter, `Show more`, `F` full-screen and `I` details have NO LEDGER ID; (j) quota, derivative-size and album-depth defaults are still `[to confirm in M0]` placeholders on the frames.

### 4c

> CLOSED by owner decision 2026-11-10 #4: the owner dismisses the synthetic hits in the dashboard; the check stays non-required. Still red on meta PR #9 on 2026-11-10.

**GitGuardian: the in-repo ignore file does nothing for the red check.** The core PR2 builder measured it: the failing check is the GitGuardian GitHub *App*, scanning server-side, while `.gitguardian.yaml` configures the *ggshield CLI* — and no workflow runs ggshield. The App reported the same hit before and after an exclusion naming the flagged file was added, so none of the file's entries has ever applied. Every hit triaged so far is a synthetic test value; nothing needs rotating. To stop the check being red forever: (a) resolve/ignore the findings in the GitGuardian dashboard (owner-only), or (b) approve a ggshield CI lane that honours the file (a new required-checks/floor entry — owner-reviewed). Until then agents keep triaging each hit in the PR body. Earlier note — **GitGuardian dashboard:** once the security seat confirms the 7 hits are synthetic test values, resolve them in the dashboard (owner-only); no scanner exclusion file was added, deliberately. **Also to dismiss (2026-09-21): incident 37486665 on yegamble/vizra PR #4, "Generic Password" in `docs/evidence/compose-topology/demo.sh` at intermediate commit `a96f188` — the flagged values are fake test markers (`zzMARKERzzPOSTGRESzz` etc., read by the chair); fixed at `bb8163f`; the commit never reaches `main` (squash-merge).**

### 10

> CLOSED by owner decision 2026-11-10 #7: residual accepted and documented; Lane B is open.

**Stamp-key (V-D) design authorship (user PR B item 1).** Two agent sessions were stopped by a safety classifier while designing how to keep the per-run stamp key out of the Playwright main process during spec collection (measured: the key is defined at spec module scope in the main process, undefined in workers). The chair does not route a classifier-stopped task to another agent. Options: you (or a human reviewer) author the item-1 design in `docs/plans/2026-09-23-vizra-user-artifact-privacy-b.md`; or accept "main-process code during collection is trusted-by-review" as a documented residual. Until then Lane B (authenticated specs) stays closed, which blocks M1 auth UI e2e tests.

### 14

> CLOSED 2026-11-10 by the owner's answer "Chair does it: stash the 14 files, reset local main to origin/main, switch to main": the 14 record files are in `stash@{0}` of the main checkout (kept), local `main` is `e5a5715` = `origin/main`, the checkout is on `main`. The owner also answered "Remove the local worktrees and branches; keep them on GitHub only" for the four parked branches; done after checking each local head is on its origin branch.

**The main checkout is not on `main` (new 2026-11-10).** `/Users/yosefgamble/github/vizra` is on `chore/warroom-records-2026-09-21` with 5 modified and 9 untracked record files. All of that content is on `main` since meta #9 (12 files byte-identical, 2 landed from the working tree; verifier claim B in `docs/evidence/warroom/2026-11-10-meta-pr9-records-VERIFY.md`). Local `main` is `bf25303`, stale and unrelated to `origin/main`. Until the checkout is on current `main`, `/warroom` there is the September command file and no Stop hook runs. The chair has not touched the checkout or the local `main`. Either do it yourself (`git stash -u`, `git branch -f main origin/main`, `git switch main`) or tell the chair to.

### 16

> CLOSED 2026-11-11 by owner decision 2026-11-11 #1: meta #16 (`f990008`) added the ten bullets verbatim from the ledger and updated ADR-001 to Go 1.27.4 and Echo v5.4.4; verifier PASS at `7912353`.

**Acceptance bullets and ADR-001 (new 2026-11-10, tick 260).** (a) These ledger cases have no acceptance bullet in `docs/issues/VZ-ISSUE-001.md`, and adding one changes the acceptance target: VZ-FOUND-002 both generated-client cases; VZ-FOUND-003 migrate up from the image, sqlc-verify, DROP COLUMN, dirty ledger; VZ-FOUND-006 key delivery, `vizra setup` keys, key without consumer, log denylist (`docs/evidence/warroom/2026-11-10-found-002-003-006-AUDIT.md`). (b) ADR-001 lines 18, 93, 94 still say Go 1.27.1 and Echo ≥ v5.3.1 after core #16 raised both; its bump policy wants them in step, and editing an Accepted ADR is yours.

### 17

> CLOSED 2026-11-12 by owner decision 2026-11-12 #1: 2 more verdicts for VZ-FOUND-002 and 1 more for VZ-FOUND-003, for vizra-core #18 and vizra-user #12 only.

**Budget grant for VZ-FOUND-002 (new 2026-11-11, tick 261).** VZ-FOUND-002 has used its 4 verifier verdicts: the audit PASS (meta #15), a FAIL on vizra-core #18 at `a627e1f` (one `-- allow-destructive:` marker exempted a later statement on the same line; main's script rejected the file, the PR accepted it), a BLOCKED on vizra-user #12 caused only by an apt failure in the e2e runner, and the PASS that completed #12. vizra-core #18 now has its fix (`84f8ad1`, fix round 1, `ci-required` green) and is not re-verified: that would be a fifth verdict for VZ-FOUND-002 (VZ-FOUND-003 is at 2 of 4). The PR stays open and nothing more is dispatched for it. Reproducer and finding: `docs/evidence/warroom/2026-11-11-vizra-core-pr18-3a-VERIFY.md`. To continue, a numbered decision naming VZ-FOUND-002 and the number of extra verdicts.

### 18

> CLOSED 2026-11-12 by owner decision 2026-11-12 #3: the chair merges status record PRs after an independent PASS. Meta #19 merged as `0a204e8`.

**Who merges a ledger status record the chair wrote (new 2026-11-12, tick 264).** Meta #19 records VZ-FOUND-002 IMPLEMENTED from vizra-core #18 and vizra-user #12. An independent verifier returned PASS at `5d8d281` and `ci-required` is green on it (`docs/evidence/warroom/2026-11-12-meta-pr19-ledger-found-002-round2-VERIFY.md`). The loop rules have the chair write status records, and the owner said on 2026-11-11 "nobody merges their own work", so the chair has not merged it. Either merge #19, or say the chair may merge status record PRs after an independent PASS, or have a builder write them.
