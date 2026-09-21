# Vizra repo map — binding context for every council teammate

Read this once, at the start of your investigation, before you form any opinion.
It describes what EXISTS and what is only PLANNED. Never treat a planned path as
evidence that code exists.

## The repositories (decided 2026-09-15; mirrors the Vidra meta-repo shape)

You are launched from the **meta repo** (`vizra`). The component repos are
intended to be checked out NESTED inside it, as separate git repos, gitignored
here, and pinned DETACHED at release tags on operator hosts.

| Path | Repo | Owns | State on 2026-09-15 |
|---|---|---|---|
| `.` | `vizra` (meta) | AGENTS.md contract, `docs/` (product spec, feature ledger, UI-control inventory, release profiles, plans, evidence), and — once built — docker-compose files, Caddy, `deploy/`, `env/` templates, `install.sh`/`bootstrap.sh`, `tests/`, `releases/` | docs only; no compose, deploy, CI or code yet |
| `./vizra-core` | `vizra-core` | Go/Echo API, worker, and the `vizra` operator CLI (`setup`, `doctor`, `deploy`, `backup`, `restore`, …); **canonical `api/openapi.yaml` product contract**; sqlc queries; append-only migrations; media pipeline; storage adapters; federation; imports; instance settings | PLANNED — does not exist |
| `./vizra-user` | `vizra-user` | Next.js/TypeScript/Tailwind — the ENTIRE user-facing product: public exploration, personal library, viewer, albums, community, admin console, moderation | PLANNED — does not exist |
| `./vizra-search` | `vizra-search` | internal-only Go search service on PostgreSQL FTS/trigram + Redis; ranked IDs + scores only | PLANNED — created in M0 as a real minimal service; search logic ships in core SQL first, remote managed default from M3 (Q-001 decided 2026-09-15) |
| `./vizra-branding` | `vizra-branding` | original brand mark, design tokens, Figma references | not created (Q-002 decided 2026-09-15: tokens in `vizra-user/packages/ui`, assets in meta `brand/`) |

Binding documents in the meta repo, in priority order: `AGENTS.md` →
`docs/PRODUCT_SPEC.md` → `docs/quality/features.json` (the atomic requirement
ledger, IDs `VZ-<AREA>-<NNN>`) and `docs/quality/ui-controls.json` →
`docs/DEFINITION_OF_DONE.md`, `docs/RELEASE_ACCEPTANCE.md`, `docs/DESIGN_BRIEF.md`,
`docs/ARCHITECTURE.md`, `docs/META_REPO.md` → `docs/OPEN_QUESTIONS.md`.

## Non-negotiable architectural boundaries

```
Browser ──▶ vizra-user ──HTTP──▶ vizra-core ──HTTP (HMAC)──▶ vizra-search
                                 (transactional truth)
```

1. **PostgreSQL owns transactional truth; Go owns business rules and
   authorization.** No direct frontend database access and no second business
   backend in Node.
2. **core owns the contract.** `vizra-core/api/openapi.yaml` is the product
   contract; the frontend consumes a generated client and never hand-edits it or
   invents an endpoint or field.
3. **Default-deny authorization** covers originals, derivatives, metadata,
   search, counts, exports, embeds, feeds, federation, IPFS publication and
   caches. Private media must never reach public IPFS or public federation
   exports. Any read surface that bypasses this is a BLOCKER.
4. **search returns ranked IDs and scores only**; core hydrates and applies
   per-viewer visibility. Search is never a hard dependency: core falls back to
   its own SQL. A design that lets search take the site down or leak private
   media is a BLOCKER.
5. **Optional services follow OFF / EXTERNAL / MANAGED.** ClickHouse, IPFS,
   S3 emulators and scanners are off by default; an external endpoint
   suppresses the local container; invalid external config is an error, never a
   silent fallback to fresh local data.
6. **Favorites, numeric ratings and public likes are distinct concepts** unless
   the spec deliberately unifies two. Native comments and numeric ratings are
   explicit Vizra features regardless of what a reference product does.
7. **Paid-edition parity ≠ billing.** Vizra has no subscriptions, paywalls or
   payment processing. Anyone proposing them is off-charter.

## Verification gates (quote these; do not invent them)

Until `docs/quality/COMMANDS.md` exists (created by the foundation slice from
commands that actually execute), **there are no verified gates**. A finding
that cites a gate must say whether the gate exists. Planned gates, to be
created and proven in milestone M0:

| Repo | Planned gate |
|---|---|
| meta | `bash -n` + `shellcheck` on scripts; `docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file <filled> config -q`; rendered-topology assertions (ports closed, images pinned, OFF/EXTERNAL/MANAGED shapes) |
| core | `make ci` (fmt, vet, migrate-lint, openapi-verify, sqlc-verify, race unit tests) + `integration` lane on real PostgreSQL/Redis/media processors |
| user | `npx tsc --noEmit`, lint, icon lint, vitest; production-build browser E2E against a real backend in CI only |
| search | `make ci` (fmt, vet, migrate-lint, openapi-verify, sqlc-verify, race tests) |

## Status vocabulary (from AGENTS.md — use it exactly)

Implementation: PLANNED / IN_PROGRESS / IMPLEMENTED / VERIFIED. Evidence:
FAIL / BLOCKED / UNVERIFIED / NOT_APPLICABLE. Merge and release state are
separate. "Compiles", "has a handler", "renders a screen" or "returns 200" is
never VERIFIED. READY_FOR_REVIEW until independently verified and merged.

## Traps to avoid

- **Nothing is implemented yet.** The kit's prose and plans describe intent. A
  reviewer who cites `cmd/api/main.go` as evidence has cited a file that does
  not exist. Check with `ls` from the meta root before asserting anything.
- **Once component checkouts exist, a recursive grep from the meta root will
  silently skip them** (they are gitignored and search tooling honours ignore
  files). Always `cd <component> && grep -rn ...`.
- **Pinned checkouts freeze docs.** A file absent at a pinned tag may exist on
  `origin/main`. Confirm with `git show origin/main:<path>` before reporting a
  file missing.
- **A green `make ci` proves nothing about media** unless the media lane
  actually decoded real files. Ask which lane ran.
- **Implemented ≠ merged ≠ released ≠ deployed.** Say which.
- **"Implemented in Go" is not the same thing as "Vizra has this feature."**
