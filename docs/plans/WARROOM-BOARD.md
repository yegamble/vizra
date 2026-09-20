# War-room board

State for `/warroom`. Tool results outrank this file: every tick reconciles it against `git` and `gh` before acting. Statuses use the AGENTS.md vocabulary; nothing here is VERIFIED without an evidence file under `docs/evidence/warroom/`.

Last tick: 2026-09-20, tick 2 (user PR1 READY_FOR_REVIEW → verifier + security dispatched; Search inventory done; remaining inventories + GAPS.md in progress). Tick 0 — war room created; wave 1 dispatched. A first dispatch was stopped by the owner for a session restart so the `vizra-builder`/`vizra-verifier` agent types would register; it left no branches, commits or PRs. Wave 1 was re-dispatched with the registered types.

## Owner decisions

Recorded verbatim from the session of 2026-09-20. The owner answered two questions put by the chair.

1. **ADR gate.** Question: "ADR-001…009 are still 'Proposed — awaiting owner architecture approval', and VZ-ISSUE-001 lists that approval as a blocker for any component-repo code. Do you approve them so M0 implementation can start?" Answer: **"Approve ADR-001…009 (Recommended)"** — described to the owner as: "ADRs flip to Accepted dated 2026-09-20 on your instruction. The nine '[to confirm in M0]' values … still get set at PR time as planned. Builders start on vizra-core / vizra-user / vizra-search."
2. **Merge policy.** Question: "AGENTS.md says 'do not self-merge without explicit authorization', but a build loop stalls at the first PR … In every option agents commit on branches, push and open PRs — including a PR for the Prompt 00/01 docs that are still uncommitted on main. Who merges?" Answer: **"Verifier-gated auto-merge (Recommended)"** — described as: "A PR merges only when a separate verifier agent that did not write the code passes it with recorded evidence AND ci-required is green. The builder never merges its own work. Release, deploy, DNS, cloud spend and resource deletion stay owner-only." Now in AGENTS.md, "Merge authorization".
3. **Owner request (same session):** implement the Claude Design mockup `Lumen Atlas Search.html`; use Figma to improve the design where photo pages and other pages are missing.

## Preflight — owner's machine, 2026-09-20

| Check | Result |
|---|---|
| go | 1.26.2 darwin/arm64 (pin 1.27.x — relies on the `toolchain` directive) |
| node / npm | 22.14.0 / 10.9.2 |
| docker / compose | 29.8.0 linux/arm64 / 5.5.1 — images are amd64-only (ruling), so CI ubuntu-24.04 is the clean target |
| sqlc | 1.31.1 (matches pin) |
| vips | 8.18.2 |
| exiftool | **missing** — BLOCKS local reproduction of VZ-FOUND-007 |
| playwright | not installed (arrives as a devDependency; browsers need download) |
| gh | yegamble; scopes gist, read:org, repo, workflow |
| disk | **19 GiB free (96 % used)** — caps parallel builders at 3; no emulated amd64 builds locally |

## In flight

| Slice | Repo | Branch | Acceptance IDs | Builder state | PR | Verified SHA | Verdict |
|---|---|---|---|---|---|---|---|
| core PR1 foundation | vizra-core | `feat/m0-foundation` | VZ-FOUND-001, -003…-006 (per plan §PR1) | DISPATCHED 2026-09-20 | — | — | — |
| user PR1 skeleton | vizra-user | `feat/m0-skeleton` | VZ-FOUND-002 | READY_FOR_REVIEW (builder) — head `5672bfd`; gh confirms OPEN, non-draft, MERGEABLE; `ci-required` + frontend/contract/guard/docker-build green on that SHA (50 tests, 0 skipped per builder) | yegamble/vizra-user#1 | verifying `5672bfd` | `vizra-verifier` + focused `vizra-security` review dispatched 2026-09-20; pending |
| search PR1 minimal service | vizra-search | `feat/m0-minimal-service` | VZ-FOUND-003 (search half), Q-001 | DISPATCHED 2026-09-20 | — | — | — |

Open points on user PR1 for the verdict: `required-checks.txt` is not at the repo root on the branch (where is the manifest, does it match the jobs that ran?); the vendored contract records core SHA `b0dbeb6`, which is on core's feature branch — after core PR1 squash-merges, user re-vendors from core `main` as the first step of user PR2 so provenance never dangles; the builder wrote its red/green transcripts under `docs/evidence/warroom/VZ-FOUND-002/` (builder claims — the verifier's file is separate).

Contract rule for this wave: the core builder owns `api/` and commits it first; user and search consume it from `/Users/yosefgamble/github/vizra/vizra-core/api/` at a recorded SHA and do their contract-dependent step last.

## Queue (dependency order)

| # | Slice | Repo | Depends on | Notes |
|---|---|---|---|---|
| 1 | meta PR-A: Prompt 00/01 baseline docs, owner decisions, war room, design import — **OPEN as yegamble/vizra#2** (`chore/m0-meta-baseline`, head `b76dd6b` at open), READY_FOR_REVIEW; not mergeable by the war room until `ci-required` exists | vizra | — | Next meta slice (dispatch when a builder slot frees): minimal `validate` lane + `required-checks.txt` + `ci-required` — the ledger generator reproduces `docs/quality/*` with no diff — in a worktree on a branch stacked on `chore/m0-meta-baseline`. The main meta checkout stays on `chore/m0-meta-baseline` so the docs stay on disk for builders. |
| 2 | core PR2: public search contract (`GET /api/v1/search`, suggestions) with `SEARCH_MODE=off` semantics | vizra-core | core PR1 merged | Unblocks the Search page against a real contract. Promoted ahead of fixtures because the owner asked for the Search page. |
| 3 | user PR2: Playwright harness on the production build (VZ-FOUND-008) | vizra-user | user PR1 merged | Desktop + mobile projects; console/network error fails the lane (demonstrated). |
| 4 | core PR3: fixture corpus (VZ-FOUND-007) | vizra-core | core PR1 merged | exiftool only in the CI image. |
| 5 | user PR3: tokens, typed Lucide icon registry, app shell (VZ-DESIGN-001) | vizra-user | user PR2 merged; design accepted | Tokens from `docs/design/claude-design/` reconciled with DESIGN_BRIEF: add dark mode, drop "SF Pro" names from the stack, brand = Vizra. The inventory measured the mockup's tokens failing WCAG AA — `--ink-3` on `--bg` 4.46:1 and on `--bg-tint` 4.14:1, `--accent` text 4.34:1, `--line` borders 1.29–1.35:1 (the only unchecked-checkbox indicator) — and found 15 radii / 9 shadows / 15 type sizes against 4 / 2 declared; the Figma library fixes the values and collapses the scale before this PR mirrors it. Add `:focus-visible` and `prefers-reduced-motion`, both absent. `~/github/goimg/goimg-user` holds the owner's earlier MIT token port — consult it; copy nothing from its `catalyst-ui-kit/` (paid, non-redistributable). |
| 6 | **user PR4: Search page** (`Lumen Atlas Search.html`) | vizra-user | queue 2, 3, 5 | Real contract, no mock data in production paths: with search off the page renders the real unavailable/empty state; the populated layout is proven in Playwright with route fixtures. VZ-SEARCH-001/003 stay short of VERIFIED until the M3 backend exists. Inventory: `docs/design/claude-design/INVENTORY-search.md`. **Chair ruling 2026-09-20 (scope of this slice):** build what M3 search backs — query field, result header with server counts, the scope tabs that have ledger IDs, Relevant/Recent sort, aspect-ratio-preserving masonry (no `fit=crop`), card → photo link, load-more, suggestions, and real loading / empty / no-results / error / search-unavailable states. **Not rendered in this slice:** the facet sidebar, mobile filter sheet and applied-filter chips (all `VZ-SEARCH-002`, M5 full profile), Collections scope (`VZ-COLLECTION-001`, M5), licence badge (M5), Featured badge and per-item views (M6). The layout keeps the 248 px column as a documented slot so M5 adds facets without a redesign. No dead or decorative controls; nothing fabricated — every count comes from the server and is permission-aware. Mockup defects the implementation must not inherit: card actions hidden in an `opacity:0` hover overlay (unreachable on touch and keyboard), `<button>` nested in `<a>`, removed focus rings, duplicate IDs from the cloned sheet. |
| 7 | meta PR-B: VZ-ISSUE-001 closure (COMMANDS.md from commands that ran, ledger evidence) | vizra | queue 1–4 | Then VZ-ISSUE-002…004 (compose, installer, boot lane). |

After M0: M1 golden path (`VZ-SLICE-01`), which needs the first-slice design accepted (design track below).

## Design track

Source rule (DESIGN_BRIEF): Claude Design mockups are exploration input; approved Figma components and tokens mirrored in the repo are the design source.

| Step | State |
|---|---|
| Import Claude Design project "goimg" (13 files, sha256 table) → `docs/design/claude-design/` | DONE 2026-09-20 — committed `b76dd6b` on yegamble/vizra#2 |
| Search page inventory + control-to-action matrix → `INVENTORY-search.md` (1,126 lines) | DONE 2026-09-20 |
| Account pages inventory → `INVENTORY-account.md` (153 controls audited) and missing-surface list → `GAPS.md` | DONE 2026-09-20 |
| Gallery + Artist Profile inventory → `INVENTORY-public.md` | IN_PROGRESS |
| Figma D1: Vizra library — corrected AA tokens, light + dark, collapsed radius/shadow/type scales, focus-visible, core components incl. the patterns the mockups lack (dialog, toast, skeleton, empty/error state, live region) → handoff in `docs/design/figma/README.md` | IN_PROGRESS — dispatched 2026-09-20 |
| Figma D2: the 16 M1 surfaces with no mockup (GAPS.md) at 390 and 1440 — owner claim, sign-in, sign-up, photo page + lightbox viewer, album detail, add-to-album dialog, asset privacy dialog, album privacy/share-grant dialog, destructive confirmation, upload progress/failure/retry + file-picker path, library and album empty states, unauthorized/not-found, session-expired re-auth, storage quota | PLANNED — after D1 |
| Owner design acceptance (Prompt 02 gate, blocks M1 and queue 5) | OWNER |

Findings that shape the design track (INVENTORY-account.md, GAPS.md): of the nine golden-path steps the mockups cover two, and the viewer — the centre of `VZ-SLICE-01` — has none. Dark mode is a re-authoring job (19 hard-coded `white`s), due at M1. `white` on `--accent` is 4.34:1, so the primary button fails AA at rest; `--danger` fails on hover; `--success`/`--warn` fail 3:1. Upload Studio and Edit Photo are drawn as M3–M5 surfaces; M1 builds a much smaller subset. **Mockup details that contradict the ledger and are corrected in Figma, not carried into code:** `unlisted` is missing from every visibility control (an M1 obligation) while `Followers` (M5) is present; binary NSFW vs three safety levels (VZ-NSFW-001); binary downloads vs the four-way setting (VZ-DOWNLOAD-001); single-select album vs many-to-many; flat albums vs sub-albums; no `password` album mode; library card opens the editor instead of the viewer; RAW/TIFF chips vs VZ-MEDIA-002; unconditional HEIC vs VZ-MEDIA-010; Photo Insights bars drawn at widths that contradict their labels; hard-coded `goimg.com/`.

## Blocked

| Item | Missing input |
|---|---|
| VZ-FOUND-007 local reproduction | `exiftool` on the owner's machine (package install is owner-only) |
| Q-016, Q-021, Q-022, Q-036 | provider credentials / owner domain (unchanged from 2026-09-15) |

## Owner inbox

1. Install `exiftool` (`brew install exiftool`) or accept CI-only reproduction for the fixture corpus.
2. Free disk space — 19 GiB free limits Docker and Playwright work.
3. Mockup controls with **no ledger ID** need a scope decision (add to the ledger, mark unavailable, or drop). Search page: Save/bookmark on cards and the "Saved" tab (is Save the same thing as Favorite, which the ledger has?), the "Series" scope and "Editorial series" facet, the view-density switcher, "Interesting" / "Most loved" / "Most viewed" as sort orders, the "Analog / Film" facet, the per-card `4K` badge, the public "refreshed moments ago" label, related-query chips; and the `RAW` badge contradicts VZ-MEDIA-002, which declines RAW. Account pages (full list of 18 groups in `INVENTORY-account.md`): plan/subscription card (Vizra has no billing product), drafts as a state, the whole Push notification channel + quiet hours, weekly digest, muted tags, per-member comment filter, self-deactivation, tagline/pronouns/multi-link profile fields, commissions + booking, engagement rate, audience geography, passkeys, SMS 2FA, Instagram/Adobe connections, scheduled publish, "AI training" toggle, "Hire", RAW/TIFF upload chips, and the "goimg Pro" billing card (Vizra has no billing product).
4. Design acceptance once the Figma first-slice pages exist.
5. **Rulesets (Q-032, owner action):** once the first PRs merge, each repo's `main` needs a ruleset requiring the `ci-required` context, blocking force-push and deletion, linear history, and CODEOWNERS over `.github/**` and `scripts/ci/**` (ADR-002 items 9–10). Until then a green check is advisory, and the builders say so in each repo's AGENTS.md. Note: GitHub does not enforce rulesets on private repos on a Free personal plan — check the plan, or say the word and the chair applies them with `gh api`.
6. **Cross-repo contract freshness:** vizra-user and vizra-search vendor core's contract and verify its sha256, but cannot detect that the vendored copy is *stale* without read access to private vizra-core from CI — a fine-grained read-only token as an Actions secret, or making the check a meta fan-in lane. Owner supplies the credential or picks the fan-in.
7. Still open from 2026-09-15: Q-008 tenancy, Q-041 notes/people, Q-042 messages; a disposable Ubuntu 24.04 amd64 host for the install rehearsal; Q-036 domain before M6.

## Merged

None yet.
