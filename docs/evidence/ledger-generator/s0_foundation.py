from core import *

# ---------------------------------------------------------------- F0 foundation / meta repo / CI
req("VZ-FOUND-001","Component repositories exist with binding contracts",
    "Owner/operator: vizra-core, vizra-user and vizra-search repositories exist, each with AGENTS.md, lockfiles, pinned toolchain, and a canonical contract source (OpenAPI in core; generated client in user).",
    "foundation", META, [{"source":"OWNER-2026-09-15","note":"meta repo mirrors Vidra"},{"source":"VIDRA-AGENTS","note":"repo-map shape"}],
    deps=(), success=["Each repo builds from a clean clone with documented commands","bootstrap.sh clones/pins all components; VIZRA_REF pins detached"],
    negative=["A missing lockfile or unpinned toolchain fails CI"], privacy=[], recovery=["bootstrap.sh is idempotent on rerun"],
    cli=["bootstrap.sh"], evidence=["clean-clone build transcript per repo with SHA"], unresolved=["Q-001","Q-002"])
req("VZ-FOUND-002","OpenAPI is the API source; TypeScript client is generated and drift-checked",
    "Developer: vizra-core/api/openapi.yaml defines every route; route↔spec drift fails CI in both directions; vizra-user's client is generated, never hand-edited.",
    "foundation", META, [{"source":"AGENTS","note":"regenerate clients from source contracts"},{"source":"VIDRA-AGENTS","note":"TestOpenAPIContract both directions"}],
    deps=["VZ-FOUND-001"], success=["Adding a route without spec fails; spec without route fails","Generated client diff is empty after regeneration"],
    negative=["Hand-edited generated file is rejected by a drift check"], evidence=["CI job output showing both-direction drift failure on a deliberate mutation, then green"])
req("VZ-FOUND-003","sqlc queries and append-only migrations are the database source",
    "Developer: migrations are append-only with matching down files where safe, compiled into the release binary; sqlc output is generated and drift-checked; migrate-lint rejects destructive statements inside the compatibility window.",
    "foundation", META, [{"source":"AGENTS","note":"append-only migrations, never hand-edit generated files"},{"source":"VIDRA-META-CI","note":"migrate-lint twin"}],
    deps=["VZ-FOUND-001"], success=["`migrate up` from the release image applies cleanly on empty DB","sqlc-verify passes"],
    negative=["A DROP COLUMN in *.up.sql fails migrate-lint","Editing sqlcgen output fails drift check"], recovery=["Dirty migration ledger is detected and reported, not auto-fixed"],
    evidence=["CI logs for sqlc-verify, migrate-lint, migrate up on empty DB"])
req("VZ-FOUND-004","Pinned, reviewed dependency versions and preserved licenses",
    "Owner: Go, Node, Next.js, Echo, sqlc, PostgreSQL, Redis, libvips binding, Lucide and Compose versions are pinned to reviewed releases with license notices preserved; the Echo major and Redis license question are decided explicitly.",
    "foundation", SAFE, [{"source":"RES-PROTOCOLS","note":"versions observed 2026-09-15: Go 1.27.1, Next.js 16.3.5, Echo v5 (requires Go 1.25+), sqlc 1.31.1, PostgreSQL 18, Redis 8.10.1 (RSALv2/SSPLv1/AGPLv3), libvips 8.18 LGPL-2.1+, govips 2.18.0 MIT, lucide-react 1.46.0 ISC"}],
    deps=["VZ-FOUND-001"], success=["Lockfiles committed; versions match ADR"], negative=["Dependabot/audit lane flags an unpinned or vulnerable dependency"],
    evidence=["ADR with versions and license table; govulncheck/npm audit lane output"], unresolved=["Q-003","Q-004"])
req("VZ-FOUND-005","Health, readiness, version and schema probes",
    "Operator: the API exposes /healthz, /readyz (fails when DB/Redis/storage unavailable), /version and a migration-state probe; readiness fails closed when the schema is behind.",
    "foundation", OPS, [{"source":"VIDRA-README","note":"/healthz /readyz /schemaz /version"}],
    deps=["VZ-FOUND-003"], success=["/readyz 200 only when DB, Redis and storage root are reachable and schema is current"],
    negative=["Stopping PostgreSQL turns /readyz non-200 within the declared interval"], recovery=["Probe recovers without restart when dependency returns"],
    api=["GET /healthz","GET /readyz","GET /version"], evidence=EV_OPS)
req("VZ-FOUND-006","Secure runtime configuration with fail-secure production validation",
    "Operator: every config key has one documented home (env template + compose consumer); production refuses dev defaults, blank secrets and insecure seams; secrets never logged.",
    "foundation", SAFE, [{"source":"VIDRA-META-CI","note":"config-key coverage assert; ${VAR:?} assertions"},{"source":"AGENTS","note":"never log credentials"}],
    deps=["VZ-FOUND-001"], success=["Every key read by config.Load reaches api and worker containers (asserted from rendered compose)","Every key `vizra setup` writes exists in the template"],
    negative=["Production boot with dev JWT/session secret fails","A key added to config without template/compose consumer fails CI"],
    privacy=["Log denylist test proves tokens/passwords/signed URLs never appear"], evidence=["CI assertion outputs; boot-refusal transcript"])
req("VZ-FOUND-007","Deterministic fixtures and representative media corpus",
    "Developer/QA: a versioned fixture set (portrait/landscape, EXIF-rotated, ICC wide-gamut, transparent PNG/WebP, animated GIF/WebP/AVIF, huge dimensions, truncated, corrupt, polyglot, GPS-tagged, MP4/MOV/WebM, equirectangular 360) with recorded hashes and provenance, usable in CI and release rehearsal.",
    "foundation", SAFE, [{"source":"PROMPT-05","note":"real media corpus"},{"source":"CHEV-COMPARE","note":"formats: AVIF JPEG GIF PNG WEBP BMP MOV MP4 WEBM; equirectangular 360"}],
    deps=[], success=["Fixture manifest lists sha256, dimensions, expected decode outcome and license per file"],
    negative=["A fixture without provenance is rejected by the manifest check"], evidence=["fixture manifest committed; hashes verified in CI"])
req("VZ-FOUND-008","Browser test environment against the production build",
    "QA: browser E2E runs against the production Next.js build and real API/PostgreSQL/Redis, with desktop (1440) and mobile (390) viewports, axe checks, screenshots and traces retained on failure.",
    "foundation", SAFE, [{"source":"DOD","note":"production-mode stack; traces retained"},{"source":"DESIGN-BRIEF","note":"390/1440 viewports, WCAG 2.2 AA"}],
    deps=["VZ-FOUND-005"], success=["E2E lane boots stack, runs, uploads artifacts"], negative=["Chromium-only coverage is labelled as such; Safari not claimed"],
    evidence=["CI artifact links; retained traces for a deliberately failing spec"])

# ---------------------------------------------------------------- CI required-check integrity
req("VZ-CI-001","One required check `ci-required` reads a checked-in manifest and fails when a lane never ran",
    "Owner: each repo has .github/required-checks.txt and a ci-required job that fails on failed/cancelled/timed-out/missing lanes; retiring a lane needs a tombstone comment; external actions pinned to commit SHAs.",
    "ci", META, [{"source":"VIDRA-CI-REQUIRED","note":"require-checks.sh; retired tombstone; SHA pins"},{"source":"DOD","note":"fail-closed gates"}],
    deps=["VZ-FOUND-001"], success=["Deleting a manifest line without tombstone fails validate","A renamed job makes ci-required fail, not pass"],
    negative=["A skipped required test fails the job","continue-on-error on a required lane is rejected by the guard"],
    recovery=["Manifest regression tests reject omitted tests, stale SHA, empty selection"], evidence=["CI run links showing deliberate breakage → red → restore → green"], unresolved=["Q-032"])
req("VZ-CI-002","Meta `validate` lane asserts the rendered topology",
    "Operator: CI renders every supported compose shape (default, external TLS, worker split, all optional profiles, external PostgreSQL, external Redis, external ClickHouse, external IPFS, combinations) and asserts ports closed, images pinned, one-shots unbuildable, restart/log policies, config-key coverage and wizard answer coverage.",
    "ci", META, [{"source":"VIDRA-META-CI","note":"validate job assertions"}],
    deps=["VZ-TOPOLOGY-001","VZ-INSTALL-002"], success=["All renders pass from a tree with no component checkouts (bundle)"],
    negative=["A new optional service publishing 0.0.0.0 fails the port-closure assert"], evidence=["validate lane logs"])
req("VZ-CI-003","Meta `boot` lane boots production mode and proves a real upload",
    "Operator: CI boots the stack in production mode from source with dummy secrets, asserts /readyz 200, runs both migration one-shots from service images, uploads a fixture JPEG through the API, and verifies a decoded thumbnail hash.",
    "ci", META, [{"source":"VIDRA-META-CI","note":"boot job; known gap F04 (no real media proof) closed here"}],
    deps=["VZ-CI-002","VZ-UPLOAD-001","VZ-MEDIA-001"], success=["Thumbnail bytes decode and match expected dimensions"],
    negative=["Migration one-shot that starts a server instead of exiting times out the job"], evidence=["boot lane logs and uploaded compose logs artifact"])
req("VZ-CI-004","Security scanning lanes",
    "Owner: govulncheck in Go repos, dependency audit in the frontend, image scan at publish, secret scanning; findings that reach code fail the lane.",
    "ci", SAFE, [{"source":"VIDRA-CORE-REQUIRED","note":"govulncheck lane"},{"source":"AGENTS","note":"security scanning"}],
    deps=["VZ-FOUND-001"], success=["Lanes present in required manifests"], negative=["A reachable advisory fails the lane"], evidence=["lane outputs with versions"])
req("VZ-CI-005","Schema compatibility and rollback-floor lanes",
    "Operator: the previous release's migrator and integration suite run against the new schema so a tag-flip rollback stays safe for one release.",
    "ci", META, [{"source":"VIDRA-CORE-REQUIRED","note":"?prev-migrator-against-new-schema, ?prev-release-against-new-schema"}],
    deps=["VZ-FOUND-003"], success=["Lane runs when migrations change"], negative=["A destructive migration fails migrate-lint before this lane"], evidence=["lane logs"])
