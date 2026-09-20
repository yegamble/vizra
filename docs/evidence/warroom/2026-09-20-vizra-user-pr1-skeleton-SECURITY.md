# Security review — vizra-user PR #1 (skeleton) at 5672bfdb5718cf9916174ddb6c25cd5ac39e5f88

Reviewer: `vizra-security` council seat (read-only), dispatched by the war-room chair 2026-09-20. Text below is the reviewer's report verbatim, extracted from its transcript by script.

**Chair ruling 2026-09-20:** Findings 1 and 2 are BLOCKING for this PR and go to the builder together with the verifier's findings (one consolidated round). Finding 3 lands with vizra-user PR3 (tokens + app shell, the first real page). Findings 4–6 form a follow-up hardening slice queued directly after PR1 merges. The four requirement IDs the reviewer proposes (VZ-SEC-SSR-001, VZ-SEC-HDR-001, VZ-SEC-SSR-002, VZ-SEC-SUPPLY-001) are proposals, not ledger entries; a meta slice checks them against existing VZ-SECURITY-* / VZ-CI-* entries and adds what is not covered through the ledger generator.

---

HEAD confirmed `5672bfdb5718cf9916174ddb6c25cd5ac39e5f88`. Gate is green today (`npm run lint` exit 0; `vitest run` 5 files / 50 tests / 0 skipped).

**What is genuinely well built, so the findings read in proportion:** `viewerFetch` forces `cache: "no-store"` at runtime (`lib/api/fetch.ts:200`), not by lint alone; `publicFetch`'s options type has no header slot, so anonymity is a type property; `url()` rejects any path without a leading `/` and I verified by URL parsing that no `path` value can swap the host (`//evil.example/x`, `/\evil`, `/@evil` all keep host `api:8080`) — no SSRF reachable from request input. No `NEXT_PUBLIC_*` exists and `process.env[name]` is computed access, so the internal base URL cannot be inlined into the client bundle. `/health` discloses only three constants, is `force-dynamic` and `noindex` — nothing to file. Workflows are clean on the classic vectors: no `pull_request_target`, no secrets, workflow-level `permissions: contents: read`, `persist-credentials: false`, actions pinned to 40-char SHAs with a guard that enforces it.

**On disclosure:** Finding 1 is written in full deliberately. It is a gap in a *lint* control; no running instance is attackable through it and no viewer data is rendered anywhere in this PR. Withholding its shape would make it unfixable. Chair may overrule.

**Blocking before merge:** Findings 1 and 2.
**Follow-ups:** Findings 3–6. Finding 3 must land with the Search slice (the first page that renders anything); 4–6 any time in M0.

**NOT WORTH DOING:** chasing the remaining syntactic bypasses I found (`Headers.set()`, `Object.assign(headers, …)`, computed key `{[k]: v}`, second-alias, spread-from-call) with more AST analysis. Each is cheap to add and none raises the floor — a committer who wants to defeat a syntax rule always can. The structural fix in Finding 1 is what actually changes the risk; more rule cases are a treadmill.

---

```
FINDING 1: the identity/caching lint rule is defeated by hoisting the fetch init object into a variable — in the one file where it is the only control
Severity:    REQUIRED  (blocking for this PR)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     eslint-rules/no-identity-headers-in-cached-fetch.mjs:234-236,
             eslint-rules/no-raw-fetch.mjs:50-56, eslint.config.mjs:23,
             lib/api/fetch.ts:193-202, eslint-rules/no-identity-headers-in-cached-fetch.test.mjs
  requirements: none yet — propose VZ-SEC-SSR-001 (ADR-003 "SSR identity")

Observed:
  The rule bails before judging anything unless the second argument is a literal:
      const options = node.arguments[1];
      if (!options || options.type !== "ObjectExpression") return;
  I drove the two rules with the repo's own ESLint 10 and @typescript-eslint/parser
  over a faithful copy of viewerFetch's body. The builder's reported mutation is
  genuinely caught — good:
      headers["cookie"] = `${SESSION_COOKIE}=${session.value}`;
      await fetch(target, { method, headers, next: { revalidate: 60 } });
      => v/raw:rawFetch, v/id:revalidated     CAUGHT
  The same mutation with the init object hoisted one line, filename
  lib/api/fetch.ts and no-raw-fetch configured exactly as eslint.config.mjs:23
  configures it (allow: ["lib/api/fetch.ts"]):
      const init: RequestInit = { method, headers, next: { revalidate: 60 } };
      const res = await fetch(target, init);
      => messages: []                          ZERO ERRORS, both rules silent
  Also MISSED by the identity rule (probed the same way): options object mutated
  after construction (`opts.next = {revalidate:60}`), `{ ...base }` spread into
  the call, headers spread from another literal, `Object.assign(headers, {cookie})`,
  a `let headers` reassigned wholesale, computed key `{[k]: session}`, and
  `const f = fetch; f(url, …)` — the last escapes BOTH rules in any file.
  Correctly CAUGHT: cache mode / revalidate window / next-object held in variables.

Failure:
  The header comment claims defence in depth: "no-raw-fetch keeps every module
  except lib/api/fetch.ts out of global fetch in the first place". In
  lib/api/fetch.ts that second layer is switched off by configuration, so the
  identity rule is the sole lint control exactly where viewerFetch lives — and a
  refactor any reviewer would wave through as cosmetic removes it. The lint half
  of the three-part control is weaker than its own documentation, and the
  documented LIMITS section does not mention init-in-a-variable at all. Today
  nothing leaks: the only fetch call sites are correct and Next 16.3.5 throws
  E831/E846 when cookies() is reached inside "use cache"/unstable_cache
  (node_modules/next/dist/esm/server/request/cookies.js:39-54), which is a real
  backstop because viewerFetch calls cookies() unconditionally. The exposure is
  to the NEXT change, on the file every private photo page will route through.

Perspective:
  member, photographer (a cached viewer response served to a stranger), developer

Recommendation:
  Two small changes, not a bigger rule:
  (a) Make the rule fail closed on what it cannot read. When a fetch's second
      argument is present but is not an ObjectExpression, report it (new
      messageId: "unreadable") rather than returning. Add the same for a `headers`
      value it cannot resolve. Keep the existing allowance for `fetch(url)` with
      no init.
  (b) Pin the runtime property with a test rather than syntax: assert in
      lib/api/fetch.test.ts that viewerFetch's init has cache === "no-store" AND
      next === undefined for every method and option combination, and that it
      calls cookies() on every path — the second is what keeps Next's cache-scope
      backstop armed if someone later "optimises" the cookie read away.
  Update the rule's LIMITS comment to name init-in-a-variable, Object.assign and
  aliased fetch, so the doc stops over-claiming.

Acceptance criteria:
  - `const init = { headers, next: { revalidate: 60 } }; fetch(t, init);` in
    lib/api/fetch.ts produces a lint error.
  - `fetch(url, opts)` where opts is any non-literal produces a lint error.
  - `fetch(url)` with no second argument still produces none.
  - Mutating viewerFetch's `cache: "no-store"` to `next: {revalidate: n}` fails
    `npm run ci` in BOTH the inline and hoisted spellings; evidence records both.
  - The rule's header comment lists init-in-a-variable among its limits.

Tests:
  Harness exists. Add to eslint-rules/no-identity-headers-in-cached-fetch.test.mjs:
  invalid cases for the hoisted init, the post-hoc `opts.next = …` mutation and
  the `{ ...base }` spread; a valid case for bare `fetch(url)`. Add to
  lib/api/fetch.test.ts a case asserting cookies() is consulted even with no
  session present (it already is — lock it), and a table-driven assertion over
  method x json x uploadIntent that init.cache === "no-store" and init.next is
  undefined in every row.

Cross-repo implications:
  core: none. user: the fix. search: none.
  meta: the mutation evidence filed under docs/evidence/warroom/ should record
  both spellings, not just the caught one.

Challenge:
  "No exploit exists — there is one fetch call site and it is correct, and Next
  throws if you wrap it in a cache. This is hypothetical." True today. The answer
  is that this PR's entire stated purpose is to be the control every later page
  relies on, the builder offered the mutation test as proof the control holds,
  and a one-line refactor falsifies that proof. Fixing it costs one `if`.
```

```
FINDING 2: .github/required-checks.txt defines the gate and is editable by the PR it gates; the CODEOWNERS it names does not exist
Severity:    REQUIRED  (blocking for this PR)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     .github/required-checks.txt:19-21, scripts/ci/require-checks.sh:57,
             scripts/ci/check-required-manifest.sh:22-43, .github/ (no CODEOWNERS)
  requirements: VZ-CI-001 (ADR-002 "CI fan-in and merge queue")

Observed:
  require-checks.sh:57 reads the manifest from the checkout under test:
      manifest=${MANIFEST:-.github/required-checks.txt}
  check-required-manifest.sh only asserts that every name PRESENT in the file
  maps to a defined job; it never asserts a name is present. So deleting the
  `frontend` line satisfies ci-guard and leaves `ci-required` demanding only
  `contract` plus two optional lanes — green without lint, typecheck, vitest or
  the production build ever having to succeed.
  The file itself acknowledges the intended mitigation at line 19:
      "This file is owner-reviewed (CODEOWNERS, once the ruleset is applied)"
  `ls -la .github/` shows only required-checks.txt and workflows/. No CODEOWNERS
  is committed at this SHA.

Failure:
  AGENTS.md's merge authorization (owner decision 2026-09-20) lets the chair
  squash-merge when "`ci-required` is green on the verified SHA". This PR is the
  commit that establishes what `ci-required` means, and at present a single-line
  deletion in the same PR redefines it. The same self-modification applies to
  ci-guard's own pin and continue-on-error checks. That is the false-positive CI
  that AGENTS.md's code-review rules call out by name.

Perspective:
  operator, developer, business (a merge gate that can be turned off in the
  change it is gating)

Recommendation:
  Commit `.github/CODEOWNERS` assigning `/.github/`, `/scripts/ci/` and
  `/eslint-rules/` to the owner, and add one step to ci-guard asserting the
  manifest still contains a fixed floor of non-optional lanes (at minimum
  `frontend` and `contract`) — so removing one is a red lane, not a silent one.
  The floor list is the thing CODEOWNERS then protects.

Acceptance criteria:
  - .github/CODEOWNERS exists and covers .github/, scripts/ci/, eslint-rules/.
  - Deleting the `frontend` line from required-checks.txt fails ci-guard with a
    named error, demonstrated against a controlled mutation.
  - Marking `frontend` optional (`?frontend`) fails the same step.
  - Owner action, recorded separately: enable the ruleset requiring CODEOWNERS
    review. The repo's half is the file; the setting is not in this PR.

Tests:
  scripts/ci/require-checks_test.sh exists and is run by ci-guard. Add a case
  asserting the floor check rejects a manifest missing `frontend` and one
  asserting it accepts the current file unchanged.

Cross-repo implications:
  core: same script is the intended twin — same gap, same fix.
  search: same. user: the fix. meta: the war-room merge rule leans on this.

Challenge:
  "Branch protection plus human review already covers it; CODEOWNERS without the
  ruleset is decoration." Partly fair — the ruleset is owner-only. But the
  ci-guard floor check works with no repo settings at all, and it is the half
  that belongs in this PR.
```

```
FINDING 3: no security response headers — no CSP, frame-ancestors, Referrer-Policy, nosniff or Permissions-Policy
Severity:    SHOULD  (follow-up — must land with the Search slice, the first real page)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     next.config.ts:1-17 (no `headers()`), no middleware.ts in the tree
  requirements: none yet — propose VZ-SEC-HDR-001

Observed:
  next.config.ts sets output, poweredByHeader:false and typescript.ignoreBuildErrors
  only. There is no `async headers()`, and `find app -name "route.*"` returns
  nothing, so no handler sets them either. Next sends none of these by default.

Failure:
  Today's blast radius is two static pages, which is why this is not blocking.
  But the next PR renders captions, descriptions and remote profile fields —
  the XSS sinks on my beat — and the slice after that adds cookie-authenticated
  mutations. Landing CSP after those pages exist means retrofitting a policy
  around inline styles and scripts already shipped, which is when teams reach
  for 'unsafe-inline' and never remove it. Missing frame-ancestors also leaves
  every future mutating control clickjackable, which matters more than usual
  here: ADR-003 puts CSRF defence on an Origin check, and framing is the
  classic way to drive a same-origin action the viewer did not intend.

Perspective:
  visitor, member, photographer, instance-admin

Recommendation:
  Add `async headers()` in next.config.ts now, while there is nothing to break:
  Content-Security-Policy with a nonce-based script-src and
  `frame-ancestors 'none'`, plus Referrer-Policy: strict-origin-when-cross-origin,
  X-Content-Type-Options: nosniff, and a Permissions-Policy denying camera,
  microphone and geolocation. Start in report-only if the Search slice needs a
  settling period, but commit the enforcing policy in the same PR as the first
  page — not later.

Acceptance criteria:
  - A response from / and from /health carries all five headers.
  - The CSP contains no 'unsafe-inline' and no 'unsafe-eval' in script-src.
  - frame-ancestors is 'none' (or an explicit allowlist with a recorded reason).
  - A negative test asserts a page with an inline <script> without the nonce is
    blocked, so the policy is proven to be enforcing rather than present.

Tests:
  No harness for response headers yet. Smallest change: extend the existing
  docker-build.yml "image serves /health" step to `curl -sI` and grep for each
  header — it already runs the production image, which is the only place
  next.config's headers() actually applies.

Cross-repo implications:
  core: sets its own headers on API responses; independent. user: this.
  search: never public. meta: deployment tree may terminate TLS in front — the
  policy must be set here, not delegated to a proxy an operator may replace.

Challenge:
  "A skeleton with no user content has nothing to protect; this is ceremony."
  Correct for this SHA. The argument is sequencing, not present risk: CSP is
  cheap before the first page and expensive after.
```

```
FINDING 4: server-only boundary is a runtime throw, not a build error
Severity:    SHOULD  (follow-up, any time in M0)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     lib/api/fetch.ts:83-89 (assertServer), lib/config.ts (no guard at all),
             package.json (no `server-only` dependency; node_modules/server-only absent)
  requirements: none yet — propose VZ-SEC-SSR-002

Observed:
  fetch.ts guards with `if (typeof window !== "undefined") throw`. lib/config.ts
  has no guard — its protection is the comment at line 6 plus the fact that
  `process.env[name]` is computed access Next will not inline. The `server-only`
  package is not a dependency.

Failure:
  A Client Component importing internalApiBaseUrl compiles, builds and ships;
  it fails at runtime in the browser with "INTERNAL_API_BASE_URL is not set",
  which fails closed but only after the module has been bundled and served.
  A Client Component importing viewerFetch likewise builds green and throws in
  the browser. Both should be `next build` failures. This is also the only thing
  standing between a future refactor and the internal API base URL appearing in
  a client chunk.

Perspective:
  developer, operator

Recommendation:
  Add the `server-only` dependency and `import "server-only";` at the top of
  lib/api/fetch.ts and lib/config.ts. Keep assertServer — it is defence in depth
  and costs nothing.

Acceptance criteria:
  - A Client Component ("use client") importing viewerFetch or
    internalApiBaseUrl fails `npm run build` with the server-only error.
  - assertServer's existing behaviour is unchanged and still covered.
  - No chunk under .next/static contains the string INTERNAL_API_BASE_URL.

Tests:
  vitest cannot express a bundler error. Smallest harness: a build-time fixture
  under a __fixtures__ route plus a scripted `npm run build` expected to fail —
  or, cheaper and adequate, a grep step over .next/static in frontend-ci
  asserting the env var name and PUBLIC_ORIGIN value never appear.

Cross-repo implications:
  core: none. user: this. search: none. meta: none.

Challenge:
  "Computed process.env access already prevents inlining, and it fails closed."
  Both true. The gap is that failing closed happens in the visitor's browser
  instead of in CI.
```

```
FINDING 5: Docker base image pinned by mutable tag, and no dependency or image scanning lane
Severity:    SHOULD  (follow-up, any time in M0)
Confidence:  high

Affected:
  repo:      vizra-user
  files:     Dockerfile:19,25,33 (`FROM node:22.14.0-alpine`),
             .github/workflows/docker-build.yml (build only), .github/required-checks.txt
  requirements: none yet — propose VZ-SEC-SUPPLY-001

Observed:
  All three stages use `node:22.14.0-alpine` — an exact patch tag, but a tag,
  which Docker Hub can repoint. `@sha256:` digests are absent. The repo already
  insists on immutable pins everywhere else: ci-guard rejects any GitHub Action
  not pinned to a 40-character commit SHA, and check-contract.mjs pins the
  codegen generator by version and verifies the spec by sha256. The base image
  is the one input that escapes that standard. Separately, no workflow runs
  `npm audit` / osv-scanner, and docker-build.yml builds the image without
  scanning it; .github/required-checks.txt lists no such lane.

Failure:
  Two distinct gaps, deliberately filed as one finding because they share a
  single cause — nothing checks what the runtime image is made of. A repointed
  tag changes what ships with no diff; and a known-vulnerable transitive npm
  package or an Alpine CVE in the shipped layer reaches production with no
  signal. `apk upgrade --no-cache` in the runner stage (Dockerfile:44) helps with
  the OS half and is a good call, but it is a mitigation, not a detection.

Perspective:
  operator, instance-admin

Recommendation:
  Pin `FROM node:22.14.0-alpine@sha256:<digest>` in all three stages, with the
  digest recorded next to the .nvmrc note so the three stay in step. Add one
  non-blocking-at-first scan job (osv-scanner or `npm audit --audit-level=high`
  over the lockfile, plus a Trivy/Grype scan of the built image in
  docker-build.yml). Promote it to required in .github/required-checks.txt once
  its baseline is clean.

Acceptance criteria:
  - Every FROM in the Dockerfile carries an @sha256 digest.
  - A scan lane runs on pull_request and merge_group and reports high/critical
    findings; its results are an artifact, not just log text.
  - Bumping .nvmrc without updating the digest fails a check (the two are
    already documented as needing to stay in step — make that enforced).

Tests:
  ci-guard is the right home for the digest assertion: one grep step over the
  Dockerfile in the same idiom as its existing action-pin check.

Cross-repo implications:
  core: same pattern for its Go image. search: same. user: this.
  meta: release records should carry the resolved digests, which the Dockerfile
  comment at :41-43 already anticipates.

Challenge:
  "Digest pinning makes routine base-image updates a two-line chore and people
  skip them, ending up MORE stale." Real cost. The counter is that the repo has
  already accepted exactly this trade for GitHub Actions and enforces it in CI;
  the base image is a larger attack surface than any action.
```

```
FINDING 6: codegen resolves whatever the vendored spec references — a poisoned $ref reaches the network in CI
Severity:    SHOULD  (follow-up, low urgency)
Confidence:  medium

Affected:
  repo:      vizra-user
  files:     scripts/codegen.mjs:34-41, scripts/check-contract.mjs:101-105,
             .github/workflows/contract-ci.yml, contracts/vizra-core/api/openapi.yaml
  requirements: VZ-FOUND-002

Observed:
  generate() runs the pinned local binary via execFileSync with an argument
  array — no shell, no npx. That is the right shape and closes the obvious
  injection. What remains: openapi-typescript 7.13.0 depends on
  @redocly/openapi-core (confirmed in its package.json dependencies), which
  resolves external $ref targets, including http(s) ones. check-contract.mjs
  invokes the same generate() inside the `contract` lane on every PR. The
  current spec is clean — all 9 $refs are local `#/components/schemas/...` and
  the file is 307 lines. UNVERIFIED: I did not execute the generator against a
  spec containing a remote $ref to confirm Redocly fetches it in this exact
  version and invocation, so this is reachability by dependency behaviour rather
  than by demonstration.

Failure:
  A PR that edits the vendored spec (updating the manifest sha256 to match,
  which a contributor can do) makes CI issue an outbound request to a host of
  the author's choosing during codegen. Impact is bounded and that is why this
  is a follow-up: contract-ci has permissions contents:read, persist-credentials
  false, no secrets in scope, and is a plain `pull_request` — a fork gets a
  read-only token and nothing to exfiltrate. The realistic harm is a build-time
  network dependency and an unreviewed schema being pulled into a committed
  artifact, not credential theft.

Perspective:
  developer, operator

Recommendation:
  Add one step to contract-ci before codegen: reject any `$ref` in the vendored
  spec whose target is not local (`#/...`) — a grep in the same idiom as
  ci-guard's action-pin check. Optionally document that `contracts/**` is
  owner-reviewed (covered by Finding 2's CODEOWNERS).

Acceptance criteria:
  - A vendored spec containing `$ref: "https://…"` or a relative file ref fails
    the contract lane with a named error, before the generator runs.
  - The current spec passes unchanged.
  - The check runs on pull_request and merge_group, like the rest of the lane.

Tests:
  No harness for this yet; it is a workflow step. Smallest addition: a fixture
  spec under scripts/ci fixtures plus a shell assertion, or — cheaper — assert
  the grep step's exit code against a here-doc in require-checks_test.sh's idiom.

Cross-repo implications:
  core: owns the spec; the same guard belongs on its side at authoring time.
  user: this. search: none. meta: none.

Challenge:
  "contracts/ is vendored by a script from a trusted private repo, the sha256
  pins it, and a hostile spec means the reviewer already lost." Largely right —
  which is why it is a follow-up and not a blocker. The grep is three lines and
  turns a review-dependent property into a checked one.
```
