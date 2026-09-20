# War-room board

State for `/warroom`. Tool results outrank this file: every tick reconciles it against `git` and `gh` before acting. Statuses use the AGENTS.md vocabulary; nothing here is VERIFIED without an evidence file under `docs/evidence/warroom/`.

Last tick: 2026-09-20 (tick 0 — war room created; wave 1 dispatched. A first dispatch was stopped by the owner for a session restart so the `vizra-builder`/`vizra-verifier` agent types would register; it left no branches, commits or PRs. Wave 1 was re-dispatched with the registered types).

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
| user PR1 skeleton | vizra-user | `feat/m0-skeleton` | VZ-FOUND-002 | DISPATCHED 2026-09-20 | — | — | — |
| search PR1 minimal service | vizra-search | `feat/m0-minimal-service` | VZ-FOUND-003 (search half), Q-001 | DISPATCHED 2026-09-20 | — | — | — |

Contract rule for this wave: the core builder owns `api/` and commits it first; user and search consume it from `/Users/yosefgamble/github/vizra/vizra-core/api/` at a recorded SHA and do their contract-dependent step last.

## Queue (dependency order)

| # | Slice | Repo | Depends on | Notes |
|---|---|---|---|---|
| 1 | meta PR-A: Prompt 00/01 baseline docs, owner decisions, war room, design import — **OPEN as yegamble/vizra#2** (`chore/m0-meta-baseline`, head `b76dd6b` at open), READY_FOR_REVIEW; not mergeable by the war room until `ci-required` exists | vizra | — | Next meta slice (dispatch when a builder slot frees): minimal `validate` lane + `required-checks.txt` + `ci-required` — the ledger generator reproduces `docs/quality/*` with no diff — in a worktree on a branch stacked on `chore/m0-meta-baseline`. The main meta checkout stays on `chore/m0-meta-baseline` so the docs stay on disk for builders. |
| 2 | core PR2: public search contract (`GET /api/v1/search`, suggestions) with `SEARCH_MODE=off` semantics | vizra-core | core PR1 merged | Unblocks the Search page against a real contract. Promoted ahead of fixtures because the owner asked for the Search page. |
| 3 | user PR2: Playwright harness on the production build (VZ-FOUND-008) | vizra-user | user PR1 merged | Desktop + mobile projects; console/network error fails the lane (demonstrated). |
| 4 | core PR3: fixture corpus (VZ-FOUND-007) | vizra-core | core PR1 merged | exiftool only in the CI image. |
| 5 | user PR3: tokens, typed Lucide icon registry, app shell (VZ-DESIGN-001) | vizra-user | user PR2 merged; design accepted | Tokens from `docs/design/claude-design/` reconciled with DESIGN_BRIEF: add dark mode, drop "SF Pro" names from the stack, brand = Vizra. `~/github/goimg/goimg-user` holds the owner's earlier MIT token port — consult it; copy nothing from its `catalyst-ui-kit/` (paid, non-redistributable). |
| 6 | **user PR4: Search page** (`Lumen Atlas Search.html`) | vizra-user | queue 2, 3, 5 | Real contract, no mock data in production paths: with search off the page renders the real unavailable/empty state; the populated layout is proven in Playwright with route fixtures. VZ-SEARCH-001/003 stay short of VERIFIED until the M3 backend exists. Inventory: `docs/design/claude-design/INVENTORY-search.md`. |
| 7 | meta PR-B: VZ-ISSUE-001 closure (COMMANDS.md from commands that ran, ledger evidence) | vizra | queue 1–4 | Then VZ-ISSUE-002…004 (compose, installer, boot lane). |

After M0: M1 golden path (`VZ-SLICE-01`), which needs the first-slice design accepted (design track below).

## Design track

Source rule (DESIGN_BRIEF): Claude Design mockups are exploration input; approved Figma components and tokens mirrored in the repo are the design source.

| Step | State |
|---|---|
| Import Claude Design project "goimg" (13 files, sha256 table) → `docs/design/claude-design/` | DONE 2026-09-20 — committed `b76dd6b` on yegamble/vizra#2 |
| Search page inventory + control-to-action matrix → `INVENTORY-search.md` | IN_PROGRESS |
| Inventory of the other 10 pages; gap list against `docs/quality/ui-controls.json` and the first-slice workflow | PLANNED |
| Figma: Vizra token/component library from the mockups (light + dark) | PLANNED |
| Figma: missing first-slice pages — owner setup/sign-in, photo viewer, album page and dialog, share/privacy dialog | PLANNED |
| Owner design acceptance (Prompt 02 gate, blocks M1 and queue 5) | OWNER |

Known gaps in the mockups: no photo viewer/detail page, no album detail, no auth or owner-claim pages, no admin/moderation, no error pages, light theme only, two placeholder brands ("Lumen Atlas", "goimg").

## Blocked

| Item | Missing input |
|---|---|
| VZ-FOUND-007 local reproduction | `exiftool` on the owner's machine (package install is owner-only) |
| Q-016, Q-021, Q-022, Q-036 | provider credentials / owner domain (unchanged from 2026-09-15) |

## Owner inbox

1. Install `exiftool` (`brew install exiftool`) or accept CI-only reproduction for the fixture corpus.
2. Free disk space — 19 GiB free limits Docker and Playwright work.
3. Mockup controls with **no ledger ID** need a scope decision (add to the ledger, mark unavailable, or drop): passkeys, SMS 2FA, Instagram/Adobe connections, scheduled publish, "AI training" toggle, "Hire", RAW/TIFF upload chips, and the "goimg Pro" billing card (Vizra has no billing product).
4. Design acceptance once the Figma first-slice pages exist.
5. Still open from 2026-09-15: Q-008 tenancy, Q-041 notes/people, Q-042 messages; a disposable Ubuntu 24.04 amd64 host for the install rehearsal; Q-036 domain before M6.

## Merged

None yet.
