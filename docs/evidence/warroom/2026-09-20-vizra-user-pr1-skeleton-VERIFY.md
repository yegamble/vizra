# Independent verification — vizra-user PR #1 "skeleton" (VZ-FOUND-002)

**Verdict: PASS**, with one REQUIRED finding (F1) that does not block this merge
and does block PR2. PASS is not a merge and not VERIFIED; the chair records those.

| | |
|---|---|
| PR | https://github.com/yegamble/vizra-user/pull/1 |
| Head SHA verified | `5672bfdb5718cf9916174ddb6c25cd5ac39e5f88` (branch `feat/m0-skeleton`) |
| Head moved during verification? | No — re-read at start and end, unchanged |
| Ledger | VZ-FOUND-002 (`docs/quality/features.json`), currently PLANNED / UNVERIFIED / NOT_STARTED |
| Verifier | independent; did not write this code |
| Builder's own transcripts | `docs/evidence/warroom/VZ-FOUND-002/` — read as claims, re-run from scratch here |

## Environment

Fresh `git clone` of `yegamble/vizra-user`, detached at the head SHA, under the
session scratch directory — never the builder's checkout. Deleted after the run.

- macOS 25.5.0, darwin/arm64
- Node v22.14.0, npm 10.9.2 (matches `.nvmrc` 22.14.0)
- Docker server linux/arm64 (native build only; no emulation, no cross-build)
- shellcheck 0.11.0 present locally
- `gh` authenticated as the repository owner

Working tree was confirmed clean (`git status --porcelain` empty) before and after
every mutation in every demonstration.

---

## 1. Documented CI entry point, run from the clean clone

| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | 410 packages installed from the committed lockfile; tree clean afterwards; peer warnings only (`eslint-plugin-react` declares `^9` against eslint 10) |
| `npm run ci` | 0 | lint clean; `tsc --noEmit` clean; **5 test files, 50 tests passed, 0 skipped, 0 todo**; production build of 3 routes (`/`, `/_not-found`, `ƒ /health`) |
| `npm run check:contract` | 0 | spec ↔ manifest ↔ generated client all agree |
| `bash scripts/ci/require-checks_test.sh` | 0 | **45 cases, 52 assertions, 0 failed** |
| `bash scripts/ci/check-required-manifest.sh` | 0 | 4 manifest entries, all map to a defined job |
| `bash -n` + `shellcheck -x` over `scripts/ci/*.sh` | 0 | clean, all three scripts |
| `docker build --tag vizra-user:verify .` | 0 | native linux/arm64 |
| container smoke (port 3319) | — | `GET /health` → 200, `status ok / service vizra-user / scope liveness` |

Test-count and skip audit: `grep -rnE '\.skip|\.todo|xit\(|xdescribe'` over `lib`,
`eslint-rules`, `app`, `scripts` returns no test skips (only `process.exit(2)` in
codegen scripts). `vitest.config.mts` sets `passWithNoTests: false`, so an empty
collection cannot pass. Every builder-claimed number above reproduced exactly.

---

## 2. Demonstrations — reproduced by me, from the clean clone

### D1 — a hand-edited generated client fails the drift check while typecheck and tests stay green

Mutation applied by me to `lib/api/generated.ts:126` (widening a union — valid
TypeScript that breaks no test):

```
-        ComponentStatus: "ok" | "degraded" | "unavailable" | "off";
+        ComponentStatus: "ok" | "degraded" | "unavailable" | "off" | "probably-fine";
```

| Lane | Exit |
|---|---|
| `npm run check:contract` | **1** — `❌ lib/api/generated.ts is not what the contract generates. first difference at line 126` |
| `npm run typecheck` | 0 |
| `npm run test` | 0 (5 files, 50 tests passed) |
| `npm run lint` | 0 |

The contrast is the argument for the check, and it holds: nothing else notices.

**D1b — the other direction.** Appending `# verifier mutation` to
`contracts/vizra-core/api/openapi.yaml` fails on content hash, not on the client:

```
❌ contracts/vizra-core/api/openapi.yaml does not match its manifest.
   manifest: 128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d
   on disk:  28ba9994906bf9e653f4a03f79184fd41a541be51947a1aa81e251bc9f79637a
```

Restored → `npm run check:contract` exit 0, `git status --porcelain` empty.
**D1 reproduced, both directions.**

### D2 — identity headers on a revalidated fetch fail lint

Mutation applied by me to `lib/api/fetch.ts` (`viewerFetch`, line 200), the exact
weakening the builder says the first version of the rule missed:

```
-      cache: "no-store",
+      next: { revalidate: 60 },
```

`npm run lint` → **exit 1**:

```
lib/api/fetch.ts
  200:15  error  This fetch sends "cookie" and is cached or revalidated. A shared
                 cache entry built from one viewer's credentials is served to other
                 viewers (ADR-003). Use viewerFetch, or set cache: "no-store"
                 vizra/no-identity-headers-in-cached-fetch
```

Restored → exit 0, tree clean. **D2 reproduced.** The builder's recorded
self-correction (the rule originally read only object literals and went green on
this mutation) is consistent with what I see: the shipped rule resolves the headers
identifier through scope and tracks `headers["cookie"] = …` writes.

### D2-BREAK — my attempt to defeat the rule beyond the builder's cases

Twelve leak shapes, each one a `fetch` that sends viewer identity on a cached or
revalidated request. Probe files were created, linted, then deleted; tree clean.

Positive controls (all correctly RED): inline literal + `next.revalidate`;
inline literal + `cache: "force-cache"`; headers-in-variable + revalidate;
unmarked cache posture; `credentials: "include"`; `revalidate` in a `const`;
`cache` value in a `const`; `new Headers({cookie})`.

**Nine bypasses found — each one lints GREEN:**

| # | Shape | Result |
|---|---|---|
| B1 | `headers: { ...identityHeaders() }` | GREEN |
| B2 | `const h = new Headers(); h.set("cookie", s)` | GREEN |
| B3 | wrapper fn: `cachedGet(url, { cookie })` where the wrapper holds `next.revalidate` | GREEN |
| B4 | `const alias = fetch;` then `alias(url, {headers:{cookie}, next:{revalidate:60}})` | GREEN |
| B5 | options object in a variable: `fetch(url, opts)` | GREEN |
| B6 | options by spread: `fetch(url, { ...base, next:{revalidate:60} })` | GREEN |
| B7 | second alias of the headers variable | GREEN |
| B8 | computed key: `headers[COOKIE_KEY] = s` | GREEN |
| B9 | `Object.assign(headers, { cookie: s })` | GREEN |

B1, B2 and B7 are explicitly named as limits in the rule's own docblock
(`eslint-rules/no-identity-headers-in-cached-fetch.mjs:34-41`). B3, B4, B5, B6,
B8 and B9 are not.

**The load-bearing part.** That docblock justifies the limits with a backstop
claim: *"That is why `no-raw-fetch.mjs` keeps every module except
`lib/api/fetch.ts` out of global `fetch` in the first place."* I tested that
claim in a real page (`app/probe/page.tsx`, since deleted) and it is false for an
alias. Of three leaking call sites, only the plain one was reported:

```tsx
const alias = fetch;
const { fetch: destructured } = globalThis;

export default async function Probe() {
  const cookie = "__Host-vizra_session=abc";
  const a = await alias("http://core/a",        { headers: { cookie }, next: { revalidate: 60 } });  // NO error
  const b = await destructured("http://core/b", { headers: { cookie }, next: { revalidate: 60 } });  // NO error
  const c = await fetch("http://core/c",        { headers: { cookie }, next: { revalidate: 60 } });  // vizra/no-raw-fetch
  ...
}
```

eslint output: `line 22 vizra/no-raw-fetch`, `line 24 vizra/no-identity-headers-in-cached-fetch`
— both against P3 only. P1 and P2 pass both rules silently. See FINDING 1.

### D3 — a type error fails `npm run ci`

Mutation applied by me to `lib/health.ts:21` (`"ok"` → `"OK"`):

`npm run ci` → **exit 2**, `lib/health.ts(21,12): error TS2322: Type '"OK"' is not
assignable to type '"ok"'.` Restored → clean. **D3 reproduced.**

---

## 3. GitHub CI on this SHA

`gh api repos/yegamble/vizra-user/commits/5672bfdb…/check-runs` — six check-runs,
all `completed` / `success`, none skipped, cancelled or timed out:

| Check | Conclusion | Window |
|---|---|---|
| `frontend` | success | 17:48:35 → 17:49:13 |
| `contract` | success | 17:48:34 → 17:49:03 |
| `guard` | success | 17:48:35 → 17:48:48 |
| `docker-build` | success | 17:48:34 → 17:49:31 |
| `ci-required` | success | 17:48:34 → 17:50:13 |
| `GitGuardian Security Checks` | success | (third-party app, not in the manifest) |

**The fan-in is not a rubber stamp.** Its job log shows it read the real head SHA,
not the merge commit, loaded the manifest, and waited:

```
CHECK_SHA: 5672bfdb5718cf9916174ddb6c25cd5ac39e5f88
ci-required: manifest .github/required-checks.txt
  - frontend
  - contract
  - ?guard
  - ?docker-build
waiting: frontend (in_progress) contract (in_progress) guard (in_progress) docker-build (in_progress)
waiting: docker-build (in_progress)
OK: every required check on 5672bfdb5718cf9916174ddb6c25cd5ac39e5f88 concluded success.
```

The manifest matches the jobs that actually ran, one for one. The `guard` job log
confirms the fan-in's own regression suite really executed in CI on this SHA
(`require-checks_test: 45 cases, 52 assertions, 0 failed`), alongside
`OK: all 4 entries in .github/required-checks.txt map to a defined job` and the
SHA-pin, `continue-on-error`, `npm ci` and `passWithNoTests` assertions.

---

## 4. The chair's six questions, answered with evidence

### Q1 — Where is the required-checks manifest, does it match, and is a listed-but-never-run lane caught?

The manifest is **`.github/required-checks.txt`**, not the repo root. That is where
`scripts/ci/require-checks.sh:57` looks (`manifest=${MANIFEST:-.github/required-checks.txt}`)
and where `check-required-manifest.sh` and the `ci-guard` path filters point. The
brief's "`required-checks.txt`" is satisfied; only the location differs, and
nothing reads a root copy.

It lists exactly four entries — `frontend`, `contract`, `?guard`, `?docker-build` —
and exactly those four jobs ran on this SHA.

I tested the fail-closed behaviour rather than reading it. Driving the real script
against the real SHA with a doctored manifest:

```
MANIFEST=<frontend, contract, never-ran-lane>   →  EXIT 1
  ::error::ci-required: gave up after 1 minutes.
    never started (a required lane is not triggering for this commit):
      never-ran-lane

MANIFEST=<frontend, contract, ?never-ran-lane>  →  EXIT 0
  (not triggered, optional-if-absent): never-ran-lane

MANIFEST=.github/required-checks.txt            →  EXIT 0
```

**A listed-but-never-run REQUIRED lane is caught**: it stays in `missing`, the
script blocks to its deadline and then fails by name. A `?`-marked lane that never
ran is accepted — by design, and both `?` lanes are path-filtered to the files
that can break them. The script is additionally fail-closed on a failed API read,
on a rate limit, on an abbreviated SHA, and on a workflow file GitHub rejects
(a run that concludes failure with zero jobs).

### Q2 — Are the two extra lanes and the Vidra adaptation honest, and does the suite run in CI?

**Honest.** I diffed all three adapted scripts against the owner's Vidra originals
at `/Users/yosefgamble/github/vidra/vidra-user/scripts/ci/`:

- `require-checks.sh` — 340 → 348 lines. The **only** changes are the requirement
  id (`A39 / QLT-01, SC3` → `ADR-002 … VZ-CI-001`), a new PROVENANCE header naming
  the Vidra source, `TWIN:` → `TWIN (intended):` because no sibling Vizra repo
  carries the file yet, and **every recorded incident relabelled as Vidra's**
  (`vidra-search 1f8b8542` → `Vidra's vidra-search 1f8b8542`; `vidra-core 13e5d04`;
  `vidra-search#44`; `rollback-floor.yml`). The control-flow logic is unchanged.
- `require-checks_test.sh` — 11 diff lines, all header provenance.
- `check-required-manifest.sh` — 3 diff lines, all header provenance.

No Vidra incident is re-told as Vizra history, no invented dates, and nothing was
carried over that does not apply. This is the opposite of a blind `vidra`→`vizra`
rename, and the builder flagged that risk itself in the PR body.

**The suite runs in CI on this SHA**: the `guard` job's step
`The ci-required fan-in stays fail-closed` executed `bash scripts/ci/require-checks_test.sh`
and printed `require-checks_test: 45 cases, 52 assertions, 0 failed`. I reproduced
the same result locally. `guard` and `docker-build` are beyond the brief's list but
are declared as such in the PR body and are additive, not substitutive.

### Q3 — Do all pins exist, match ADR-001, and is the lockfile consistent?

Every pin resolves on the npm registry (`npm view <pkg>@<version> version`):

| Pin | Registry | ADR-001 |
|---|---|---|
| `next` 16.3.5 | 16.3.5 | "Next.js 16.3.x" ✅ |
| `react` / `react-dom` 19.3.0 | 19.3.0 | "matching React" ✅ |
| `typescript` 5.9.3 | 5.9.3 | `[pin at PR time; verify]` ✅ |
| `tailwindcss` / `@tailwindcss/postcss` 4.3.3 | 4.3.3 | `[pin at PR time; verify]` ✅ |
| `openapi-typescript` 7.13.0 | 7.13.0 | "openapi-typescript 7.13.x" ✅ |
| `eslint` 10.11.0 | 10.11.0 | not pinned by ADR-001 |
| `eslint-config-next` 16.3.5 | 16.3.5 | tracks `next` |
| `vitest` 5.0.1 | 5.0.1 | not pinned by ADR-001 |
| `@types/node` 22.20.4, `@types/react(-dom)` 19.3.0 | all resolve | — |
| `lucide-react` | **absent** | ADR-001 pins 1.46.x; deliberately out of scope until the icon registry (PR2) ✅ |

`npm ci` succeeded from the committed lockfile and left the tree clean — the
lockfile is consistent with `package.json`. No pin contradicts ADR-001. See
FINDING 5 for the ADR-001 licence-table bookkeeping this leaves open in the meta repo.

### Q4 — The vendored contract, the source SHA, and squash-merge

The vendored copy is genuine, not a fabrication. Core's real file at that commit
hashes to exactly what the manifest records:

```
gh api repos/yegamble/vizra-core/contents/api/openapi.yaml?ref=b0dbeb6…  |  base64 -d  |  shasum -a 256
  128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d
contracts/vizra-core/api/openapi.yaml
  128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d
manifest.spec.sha256
  128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d
```

`b0dbeb6dc27294fe793492ea60bc18b6aed4b042` is reachable and is the head of
`feat/m0-foundation` in `yegamble/vizra-core` (there is no open PR on core yet).

**What the drift lane actually enforces**: `scripts/check-contract.mjs` checks
(1) the vendored file's sha256 against `manifest.spec.sha256`, (2) byte-for-byte
equality between `lib/api/generated.ts` and a fresh generation into a temp
directory, and (3) that the installed generator version equals
`manifest.generated_client.generator_version`. It **never reads
`manifest.spec.source_commit`** and never contacts vizra-core. Confirmed by
reading the script and by D1/D1b, which fail on content, not on provenance.

**So if `b0dbeb6…` becomes unreachable after a squash-merge, no CI lane breaks.**
The `contract` job stays green: it compares bytes it already has. What breaks is
human re-vendoring and audit — `scripts/vendor-contract.mjs --from ../vizra-core`
needs a checkout containing that commit, and a reviewer can no longer resolve the
`source_commit` to confirm where the spec came from. In practice a squash-merge
via a PR leaves the commit alive on `refs/pull/N/head`; a direct branch delete
with no PR is the case that loses it. See FINDING 3 — the provenance the manifest
records is honest but unverified by any check, and the PR body says so.

### Q5 — Mock data, dead controls, fake success, hand-written API types

None found.

- `lib/api/types.ts` re-exports `components`/`operations`/`paths` from
  `./generated` and derives `ApiPath`, `Schemas`, `Ok<Id>` from them. **No
  hand-written interface for any endpoint the contract describes.**
- `app/page.tsx` is an honest placeholder — a heading, one sentence saying no
  product surface is implemented, and a link to `/health`. It invents no data and
  shows no control.
- `app/health/page.tsx` renders only `healthPayload()`, which is three literal
  fields with no I/O, and the page text states in prose that it is liveness only
  and says nothing about core, PostgreSQL, cache or storage.
- No component fetches anything; there are no controls at all yet, so no dead
  ones and no fake success states.
- `eslint.config.mjs` sets `no-console: "error"` outside scripts, and
  `vizra/no-raw-fetch` allow-lists exactly `lib/api/fetch.ts`.
- `lib/api/fetch.ts` returns a discriminated `ApiResult<T>` and carries no upstream
  error body into the page — an error cannot be mistaken for empty data.
- The helper tests are behavioural, not shape assertions: 13 named cases including
  "is anonymous even when a session cookie exists", "forwards only the session
  cookie, never the whole cookie jar", "refuses a path that is not rooted, so a
  base URL cannot be swapped", "still asks core when there is no session, instead
  of guessing 401". The two RuleTester suites carry 10 valid + 14 invalid cases.

### Q6 — Non-root image, and does `/health` leak configuration?

**Non-root: yes.** In the running container built from this SHA:

```
$ docker exec vizra-user-verify id
uid=1001(nextjs) gid=65533(nogroup) groups=65533(nogroup)
```

`USER nextjs` is set before `CMD ["node", "server.js"]`. See FINDING 4 for a NIT
about the `nodejs` group.

**No leak.** `GET /health` → 200. Scanning the rendered HTML for
`INTERNAL_API_BASE_URL`, `PUBLIC_ORIGIN`, the configured upstream `127.0.0.1:9`,
`process.env`, `__Host-vizra_session`, node version or build id returns **nothing**.
The page reports only `status ok / service vizra-user / scope liveness` — no
version, no commit, no build metadata, consistent with the comment in
`lib/health.ts`. Response carries `Cache-Control: private, no-cache, no-store,
max-age=0, must-revalidate` and no `X-Powered-By` (`poweredByHeader: false`).
`lib/config.ts` reads nothing as `NEXT_PUBLIC_*`, so no configuration reaches the
browser bundle, and a missing value throws rather than defaulting.

---

## 5. Findings

```
FINDING 1: The identity-header lint rule has nine bypasses, and its own documented
           backstop (no-raw-fetch) does not hold for an aliased fetch
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-user
  files:     eslint-rules/no-identity-headers-in-cached-fetch.mjs:34-41,226-236
             eslint-rules/no-raw-fetch.mjs:59-69
  requirements: VZ-FOUND-002 (slice scope: "the lint rule forbidding identity
             headers in revalidated/cached fetches"); ADR-003 § SSR identity

Observed:
  Twelve identity-leaking fetch shapes linted from a clean clone. Eight were
  correctly reported. Nine were not: headers spread from a function call (B1),
  `new Headers()` + `.set()` (B2), a wrapper function that separates identity
  from cache posture (B3), an aliased `fetch` (B4), the options object held in a
  variable (B5), options assembled by spread (B6), a second alias of the headers
  variable (B7), a computed header key (B8), and `Object.assign` (B9).
  B1/B2/B7 are named as limits in the rule's docblock; B3/B4/B5/B6/B8/B9 are not.
  The docblock justifies the limits with: "That is why `no-raw-fetch.mjs` keeps
  every module except `lib/api/fetch.ts` out of global `fetch` in the first
  place." In a page I wrote at app/probe/page.tsx (deleted after the run), that
  claim failed:

      const alias = fetch;
      const { fetch: destructured } = globalThis;
      await alias(url,        { headers: { cookie }, next: { revalidate: 60 } });  // no error
      await destructured(url, { headers: { cookie }, next: { revalidate: 60 } });  // no error
      await fetch(url,        { headers: { cookie }, next: { revalidate: 60 } });  // reported

  `no-raw-fetch.mjs:59-69` only matches a CallExpression whose callee is the
  Identifier `fetch` or `globalThis.fetch` / `window.fetch`. Binding `fetch` to
  another name is neither a call nor a matching callee, so both rules stay silent.

Failure:
  Two distinct exposures. (a) Anywhere in the app, a module can bind global
  `fetch` to another name and then send `__Host-vizra_session` on a
  `next: { revalidate: n }` request with zero lint errors — the exact shared-cache
  leak the rule exists to stop, and the one that produces no error, no log line
  and no failing test. (b) Inside `lib/api/fetch.ts`, where `no-raw-fetch` is
  allow-listed off, B1 and B9 are plausible ordinary refactors of the helper
  (`...identityHeaders()`, `Object.assign(headers, …)`) that would silently
  disarm the one control protecting viewerFetch — which is precisely the class of
  regression D2 was written to catch.
  Nothing leaks on this SHA: no product code calls the API yet. The exposure
  begins with the first page that does.

Perspective:
  visitor, member (one viewer's private response served to another), developer

Recommendation:
  Smallest change, two parts:
  1. In `no-raw-fetch.mjs`, also report any reference to the global `fetch`
     binding that is not a call — an alias assignment, a destructure from
     `globalThis`/`window`, passing `fetch` as an argument. That closes B4 and
     leaves B1/B2/B3/B5/B6/B8/B9 covered outside `lib/api/fetch.ts`, where
     `no-raw-fetch` already fires on the literal `fetch(` call.
  2. Correct the docblock in `no-identity-headers-in-cached-fetch.mjs`: list the
     six undocumented shapes, and drop or qualify the backstop sentence, which is
     false as written. A privacy control must not claim reach it does not have.

Acceptance criteria:
  - `const f = fetch; f(url, {...})` and `const { fetch: f } = globalThis;`
    each produce a lint error in a file outside the allow-list.
  - B1, B2, B3, B5, B6, B8 and B9 each produce at least one lint error when
    written in a file under `app/` or `lib/` other than `lib/api/fetch.ts`.
  - The rule's "LIMITS, STATED PLAINLY" section enumerates every shape that is
    still unreported, and makes no claim about no-raw-fetch that a test does not
    back.
  - Negative case: `publicFetch`-shaped code (cached, no identity) stays green.

Tests:
  `eslint-rules/no-raw-fetch.test.mjs` — add invalid cases for the alias and the
  destructure. `eslint-rules/no-identity-headers-in-cached-fetch.test.mjs` — add
  the six undocumented shapes as invalid cases if the rule is strengthened, or as
  commented, explicitly-out-of-reach valid cases if the fix lands in no-raw-fetch
  instead. The harness exists and runs under `npm run test`; no new harness needed.

Cross-repo implications:
  core: none | user: as above | search: none
  meta: none, unless the chair wants ADR-003's "a lint rule forbids identity
  headers in revalidated fetches" annotated with the rule's real reach.

Challenge:
  The strongest counterargument: this is a defence-in-depth control with no call
  sites to defend on this SHA, the rule catches every shape that exists in the
  repository today, it caught the one mutation that mattered (D2), and the
  docblock already says the rule is syntax and not type inference. Demanding
  data-flow analysis from an ESLint rule is a treadmill. My answer: I am not
  asking for data-flow analysis — I am asking that a stated backstop be true, and
  the alias fix is roughly six lines. It is much cheaper now than after PR2 adds
  the first twenty call sites.
```

```
FINDING 2: publicFetch and viewerFetch have no default request deadline
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     lib/api/fetch.ts:103-110 (timeoutSignal), :137-152 (publicFetch),
             :180-205 (viewerFetch)
  requirements: VZ-FOUND-002 (slice scope: the fetch helpers); meta AGENTS.md
             "Propagate cancellation/deadlines; bound request, file, decoder,
             subprocess, and queue resources"

Observed:
  `timeoutMs?: number` is optional in both PublicFetchOptions and
  ViewerFetchOptions, and `timeoutSignal` returns the caller's signal unchanged
  when it is absent:

      function timeoutSignal(timeoutMs, caller) {
        if (timeoutMs === undefined) return caller;
        ...
      }

  Every call therefore defaults to no deadline. `grep -c timeout
  lib/api/fetch.test.ts` → 0: none of the 13 helper cases exercises a timeout,
  and `ApiResult`'s `reason: "timeout"` branch is unexercised.

Failure:
  A vizra-core that accepts a connection and never answers holds the SSR render
  open indefinitely. The operator sees requests pile up on the Node process with
  no bound and no signal in the helpers that anything is wrong; the visitor sees
  a page that never arrives rather than the real failure state the helpers were
  designed to render. This is the "bound request resources" rule in AGENTS.md.

Perspective:
  visitor, operator

Recommendation:
  Give both helpers a default `timeoutMs` (a named constant, overridable per
  call), so that omitting the option yields a bounded request rather than an
  unbounded one.

Acceptance criteria:
  - `publicFetch(path, { freshness: "no-store" })` with no timeoutMs aborts at
    the default and returns `{ ok: false, status: 0, reason: "timeout" }`.
  - The same for `viewerFetch(path)`.
  - An explicit `timeoutMs` still wins, and a caller-supplied `signal` still
    composes with the deadline (AbortSignal.any).

Tests:
  `lib/api/fetch.test.ts` — two cases against a stubbed fetch that never settles,
  asserting `reason === "timeout"` for each helper with no options. The harness
  exists (vitest, stubbed global fetch); no new harness needed.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  A default deadline can turn a slow-but-working large response into a failure,
  and Next/undici may impose its own bound. My answer: whatever undici's default
  is, it is not this repository's reviewed decision, and `reason: "timeout"`
  exists in the result union precisely because the helpers mean to own it.
```

```
FINDING 3: contracts/manifest.json records provenance that no check verifies
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     contracts/manifest.json, scripts/check-contract.mjs:52-118,
             .github/workflows/contract-ci.yml
  requirements: VZ-FOUND-002

Observed:
  The manifest records source_repo, source_commit, source_head, source_branch and
  vendored_at. `check-contract.mjs` reads only `spec.sha256` and
  `generated_client.generator_version`; `source_commit` is printed in the success
  message and otherwise unused. The `contract` workflow makes no network call.
  I confirmed independently (Q4) that the recorded commit is real, reachable, and
  hashes to the recorded sha256 — so the record is currently honest. Nothing in
  CI would notice if it were not.
  The builder states this limitation plainly in the PR body, in
  contract-ci.yml's header, and in the repo's AGENTS.md "Owed" section. This
  finding records the residual risk, not a concealment.

Failure:
  A future re-vendor could copy a spec from an uncommitted working tree, or record
  a source_commit that does not correspond to the bytes, and every lane stays
  green. Separately, `source_commit` points at a feature branch; if core deletes
  that branch without a PR, a reviewer can no longer resolve the provenance —
  though, as established in Q4, no lane breaks.

Perspective:
  developer

Recommendation:
  When the read-only vizra-core token exists (already tracked as Owed), the same
  step that checks staleness should also assert that the vendored bytes equal
  `source_path` at `source_commit`. Until then, the cheapest improvement is for
  `vendor-contract.mjs` to refuse to record a commit that is not an ancestor of
  core's default branch, or to mark the manifest `provenance_verified: false`
  when it is not.

Acceptance criteria:
  - A manifest whose source_commit does not produce the recorded sha256 fails a
    lane, with the two hashes printed.
  - A vendored spec taken from a dirty working tree is recorded as such and is
    rejected on `main`.

Tests:
  A new case in the contract lane, once a token exists. Harness does not exist
  yet: it needs the read-only token already recorded as Owed in the repo's
  AGENTS.md. No smaller harness closes it honestly.

Cross-repo implications:
  core: must land its own route↔spec both-direction test before VZ-FOUND-002 can
  be VERIFIED end to end — this repository proves only its own half.
  user: as above | search: none | meta: track the token as an owner input.

Challenge:
  The PR already declares this as Owed, so recording it again is bookkeeping. My
  answer: it is the one gap between "the client matches some spec" and "the client
  matches core's spec", and the ledger's outcome sentence claims the latter.
```

```
FINDING 4: the image's nodejs group is created but the runtime user is not in it
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     Dockerfile:44-52
  requirements: VZ-FOUND-002 (production Dockerfile)

Observed:
  `addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs` —
  BusyBox `adduser` without `-G` places the user in `nogroup`. In the running
  container: `uid=1001(nextjs) gid=65533(nogroup) groups=65533(nogroup)`.
  The `--chown=nextjs:nodejs` on the two COPY lines therefore sets a group the
  runtime user does not belong to.

Failure:
  No functional impact — user ownership alone is sufficient for the server to
  read its own bundle, and the container is correctly non-root. But the group
  half of the chown is inert, so a future change that relies on group permissions
  (a writable cache directory, say) would fail in a confusing way.

Perspective:
  operator, developer

Recommendation:
  Add `-G nodejs` to the adduser call, or drop the group and the `:nodejs` half
  of the chown so nothing implies a membership that does not exist.

Acceptance criteria:
  `docker run … id` reports `gid=1001(nodejs)`, or the Dockerfile no longer
  creates a group it does not use.

Tests:
  Extend the existing `docker-build` lane's smoke step with
  `docker exec … id -gn` asserting the expected group.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  It is cosmetic and the image is already non-root. Agreed — hence NIT.
```

```
FINDING 5: ADR-001's licence table is not updated for the pins this PR establishes
Severity:    SHOULD
Confidence:  medium

Affected:
  repo:      vizra (meta)
  files:     docs/adr/ADR-001-stack-pins-and-licences.md (licence table rows for
             React, Tailwind CSS, TypeScript, Next.js)
  requirements: VZ-FOUND-002; ADR-001 "Bump policy"

Observed:
  ADR-001's table still carries `[pin at PR time; verify]` in the Version cell for
  React, Tailwind CSS and TypeScript, and every SPDX cell says "SPDX to be
  re-verified from the upstream LICENSE file at pin time (PR1)". This PR is
  vizra-user's PR1 and establishes react 19.3.0, tailwindcss 4.3.3 and typescript
  5.9.3 — each of which I confirmed exists on the registry and is consistent with
  ADR-001 — but no SPDX re-verification evidence accompanies it, and the table is
  in a different repository that this PR cannot touch.
  The builder's plan does record each pin with its observed licence
  (docs/plans/2026-09-20-vizra-user-pr1-skeleton.md:126-138), which is most of the
  work.

Failure:
  ADR-001 requires a pin to be reviewable against the table in the same diff. A
  cross-repo split means the table drifts behind the lockfiles, and the
  "Nothing AGPL or GPL is shipped" claim rests on unverified SPDX ids for three
  components that now ship in the image.

Perspective:
  operator, business

Recommendation:
  A small meta-repo follow-up filling the three Version cells from this
  lockfile and replacing the SPDX placeholder with the id read from each
  package's own LICENSE file. Not a change to this PR.

Acceptance criteria:
  - No `[pin at PR time; verify]` remains for a component vizra-user actually
    installs.
  - Each such SPDX cell names the file and version the id was read from.

Tests:
  None automatable yet. A future meta CI lane could diff the table's version
  cells against the component lockfiles.

Cross-repo implications:
  core: the same obligation applies at its PR1 | user: none in this PR |
  search: same | meta: the table update.

Challenge:
  ADR-001's bump policy may only govern *changes* to an existing pin, not the
  first pin, making this premature. My answer: the SPDX column names PR1
  explicitly as the moment of verification, so the obligation is at least
  arguable — hence Confidence: medium, and a follow-up rather than a block.
```

---

## 6. Verdict

**PASS.**

- Every in-scope acceptance bullet reproduced by me from a clean clone: the
  negative case ("hand-edited generated file is rejected by a drift check") and
  its mirror (edited spec rejected on sha256), and "generated client diff is empty
  after regeneration".
- All three demonstrations reproduced independently: D1 red-then-green with
  typecheck/test/lint staying green, D2 red-then-green, D3 exit 2 then green.
- CI green on this exact SHA. All four manifest lanes ran; the fan-in verified
  them against the real head SHA, and I confirmed by direct experiment that it
  fails closed on a listed-but-never-run required lane.
- No fabricated evidence. Every number in the PR body and the execution plan that
  I could re-derive, I re-derived, and all of them matched: 410 packages, 50 tests
  in 5 files with 0 skips, 45 cases / 52 assertions, 4 manifest entries, three
  routes, non-root container, `/health` 200. The vendored spec really is core's
  bytes at the commit named. The Vidra adaptation is honest.

**FINDING 1 is REQUIRED and I am explicitly not treating it as merge-blocking for
this SHA**, because no production code in this repository calls the API, so there
is no live leak — the control is protecting an empty room. It **does** block the
first PR that adds a call site (PR2 / VZ-FOUND-008); the fix is roughly six lines
plus two test cases and is far cheaper before those call sites exist than after.
If the chair's bar is "no open REQUIRED finding at merge", this becomes a FAIL and
the reproduction above is enough for the builder to close it in one commit.

Also recorded, and not verified by me because it is out of this repository's reach:
VZ-FOUND-002's full outcome ("route↔spec drift fails CI in both directions")
depends on vizra-core's own contract test, which has not landed. **PASS here covers
vizra-user's half only.** The ledger entry must not reach VERIFIED on this evidence
alone, and — per the builder's own PR body — the `main` ruleset requiring the
`ci-required` context, force-push/deletion blocks, linear history and CODEOWNERS
over `.github/**` and `scripts/ci/**` are still owner actions that no CI result
can substitute for.

## 7. Cleanup

Clone at `…/scratchpad/verify/vizra-user` deleted. Probe files
(`lib/api/probe.ts`, `app/probe/page.tsx`) were removed before deletion and the
tree was confirmed clean. Docker image `vizra-user:verify` and container
`vizra-user-verify` removed and the build cache I created pruned. The container
`refpin-spike-kubo` was not touched.
