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

---
---

# RE-VERIFICATION AT 9767015

**Everything above this line describes SHA `5672bfd` and does not carry over.**
This section is a complete, independent re-verification of the new head after
the chair's round-1 fix round.

**Verdict: PASS.** Finding 1 **CLOSED**. Finding 2 **CLOSED**. Finding 4
**CLOSED**. Findings 3 and 5 remain **OPEN** and unchanged (both were SHOULD,
both are acknowledged in the PR; neither was in the fix round's scope). One new
narrower finding, **FINDING 6**, and one NIT, **FINDING 7**.

| | |
|---|---|
| Head SHA verified | `9767015444fa8bdbf1a1326f1cc58b41d068ba14` |
| Previous SHA | `5672bfdb5718cf9916174ddb6c25cd5ac39e5f88` (my PASS-with-findings) |
| Delta | one commit, `fix(m0): fail the identity lint control closed; pin the gate's floor`, 16 files, +948 −189 |
| Head moved during re-verification? | No — re-read at start and end, unchanged |
| Clone | fresh, second clone; the round-1 clone was already deleted |
| Environment | identical to round 1 (macOS arm64, Node v22.14.0, npm 10.9.2, Docker linux/arm64, shellcheck 0.11.0) |

## R1. CI entry point and the guards, from the clean clone

| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | clean install, tree clean afterwards |
| `npm run ci` | 0 | lint clean; typecheck clean; **5 files, 116 tests passed, 0 skipped, 0 todo**; production build |
| `npm run check:contract` | 0 | unchanged from round 1; same spec sha256 `128d0509238a…`, same source commit |
| `bash scripts/ci/require-checks_test.sh` | 0 | **55 cases, 62 assertions, 0 failed** |
| `bash scripts/ci/check-required-manifest.sh` | 0 | 4 entries, all defined |
| `bash scripts/ci/check-required-floor.sh` | 0 | `still requires the floor: frontend contract` |
| `bash -n` + `shellcheck -x` over `scripts/ci/*.sh` | 0 | clean, all **four** scripts |
| `docker build` + container run | 0 | see R6 |

Builder's claimed 116 tests / 0 skipped and 55 cases / 62 assertions both
reproduce exactly. `grep -rnE '\.skip\(|\.todo\(|xit\(|xdescribe'` over `lib`,
`eslint-rules`, `app` → no test skips.

## R2. All nine round-1 bypasses, re-run — plus twelve new ones

Probe files created, linted, deleted; tree clean. A case is REPORTED if either
rule fires anywhere the construct appears (an alias is reported at its
declaration, which is what makes the construct unwritable).

| # | Shape | round 1 | now | Reported by |
|---|---|---|---|---|
| B1 | `headers: { ...identityHeaders() }` | GREEN | **REPORTED** | identity `unreadable` + `rawFetch` |
| B2 | `new Headers()` + `.set()` | GREEN | **REPORTED** | identity `unreadable` + `rawFetch` |
| B3 | wrapper fn holding the cache posture | GREEN | **REPORTED** | `aliasedFetch` |
| B4 | `const alias = fetch` | GREEN | **REPORTED** | `aliasedFetch` at the declaration (line 23) |
| B4b | `const { fetch: d } = globalThis` | GREEN | **REPORTED** | `aliasedFetch` at the declaration (line 27) |
| B5 | init hoisted into a variable | GREEN | **REPORTED** | identity `unreadable` + `rawFetch` |
| B6 | init assembled by spread | GREEN | **REPORTED** | identity `unreadable` + `rawFetch` |
| B7 | second alias of the headers variable | GREEN | **REPORTED** | identity `unreadable` + `rawFetch` |
| B8 | computed header key | GREEN | **REPORTED** | identity `unreadable` + `rawFetch` |
| B9 | `Object.assign(headers, …)` | GREEN | **REPORTED** | identity `unreadable` + `rawFetch` |

**All nine closed.** New shapes I tried against the fail-closed rules:

| # | Shape | Result |
|---|---|---|
| N1 | `Reflect.apply(fetch, null, [...])` | REPORTED `aliasedFetch` |
| N2 | `fetch.call(null, url, init)` | REPORTED `aliasedFetch` |
| N3 | `fetch.bind(null)` then call | REPORTED `aliasedFetch` |
| N4 | `new Request(url, {cookie})` + `fetch(req, {revalidate})` | REPORTED `unreadable` + `rawFetch` |
| N4b | `fetch(new Request(url, {cookie}))`, single-arg | REPORTED `rawFetch` |
| N6 | `(0, fetch)(url, init)` | REPORTED `aliasedFetch` |
| N7 | `[fetch][0](url, init)` | REPORTED `aliasedFetch` |
| N8 | `fetch?.(url, init)` optional call | REPORTED `unreadable` + `rawFetch` |
| N9 | `const o = { fetch }; o.fetch(url, init)` | REPORTED `aliasedFetch` |
| N11 | `fetch(url, opts)` — unreadable init | REPORTED `unreadable` + `rawFetch` |
| N12 | `{ headers: {cookie}, ...posture }` | REPORTED `unreadable` + `rawFetch` |
| N13 | `new Headers(raw)` non-literal | REPORTED `unreadable` + `rawFetch` |

**Two stayed silent:**

- **N5 — `globalThis["fetch"](…)`**, the computed-member spelling. Four
  variants (`globalThis["fetch"]`, `window["fetch"]`, aliased-then-called, and
  a template-literal key `` globalThis[`fetch`] ``) in a real page file
  produced **zero lint messages of any kind**. This is a genuine remaining
  bypass of both rules, and the runtime test does **not** catch it: the
  `lib/api/fetch.test.ts` table asserts the two helpers' behaviour, and a page
  that reaches the global this way is not exercised by any test. See FINDING 6.
- **N10 — a different HTTP client** (`await import("undici")` → `request(…)`).
  Silent, but out of scope by construction: `undici` is not a dependency, no
  rule named `no-raw-fetch` can be expected to ban every client, and
  `node:http` would be the same category. Recorded as a known residual, not a
  finding — the control against it is review plus the helpers-only
  architecture, which AGENTS.md already states.

## R3. TEST-WEAKENING CHECK — the chair's specific concern

I extracted every `code:` string from the `valid` and `invalid` arrays of both
rule test files at each SHA and set-differenced them, rather than reading the
diff:

| File | valid | invalid | cases removed |
|---|---|---|---|
| `no-identity-headers-in-cached-fetch.test.mjs` | 10 → 10 | 14 → **30** | **1** |
| `no-raw-fetch.test.mjs` | 4 → **8** | 3 → **10** | **0** |

**Zero valid cases were removed from either file, so nothing moved
invalid→valid.** That is the shape a weakening would take, and it did not
happen. The −52 lines in the diff are almost entirely *reformatting*:
nine cases that were written as multi-line `{ code: … }` objects were collapsed
to one line, so the diff shows them as removed and re-added. Ruling case by
case on everything the diff marks removed:

| Removed by the diff | Ruling |
|---|---|
| `fetch(url,{headers:{cookie:session},cache:"no-store"})` (valid) | **Reformatted, still present.** Legitimate. |
| `fetch(url,{headers:{Authorization:token},cache:"no-store"})` (valid) | **Reformatted, still present.** Legitimate. |
| `fetch(url,{headers:{Cookie:c},next:{revalidate:0}})` (valid) | **Reformatted, still present.** Legitimate. |
| `headers["cookie"]=jar` + revalidate (invalid) | **Reformatted, still present**, same `messageId` and `data`. Legitimate. |
| `headers.authorization=bearer` + unmarked (invalid) | **Still present**, same assertion. Legitimate. |
| `const headers={cookie:jar}` + `force-cache` (invalid) | **Still present.** Legitimate. |
| `const h={cookie:jar}` + `revalidate:5` (invalid) | **Still present.** Legitimate. |
| `globalThis.fetch(…)` + revalidate (invalid) | **Still present**, collapsed to one line. Legitimate. |
| `fetch(url,{headers:{authorization:bearer},next:{revalidate:30}})` (invalid) | **GENUINELY DELETED — the only one.** See below. |
| 3 comment lines in `no-raw-fetch.test.mjs` | Comment rewording only. Legitimate. |
| 4 lines of the `cookies` mock in `fetch.test.ts` | **Strengthened, not removed**: the mock gained a `cookiesCalls` counter; the `get` logic is byte-identical. Legitimate. |

**Ruling on the one genuine deletion.** It asserted lowercase `authorization` +
`next: { revalidate: 30 }` → `revalidated`. Every dimension it covered survives
in at least two other cases: `AUTHORIZATION` + `force-cache` (authorization as
identity, uppercase), `Authorization` + `no-store` (valid, so identity is still
recognised), `headers.authorization = bearer` (unmarked), `cookie` +
`revalidate: 60` and `"Cookie"` + `revalidate: 3600` (the revalidated posture and
casing). To be sure rather than to argue, I ran the deleted snippet against the
**current** rule as a standalone RuleTester case:

```
Tests  1 passed (1)   // deleted-case-still-caught
```

The behaviour it asserted is still enforced. **Verdict: a redundant duplicate
removed, coverage-neutral — not a weakening.** My only comment is that it cost
one line and should have been kept; I am not raising a finding for it.

Also worth recording as the opposite of weakening: `eslint.config.mjs` **removed**
the `"vizra/no-raw-fetch": "off"` exemption that `scripts/**` and
`eslint-rules/**` previously enjoyed. The rule now applies there too.

## R4. The shell suite's exit-code pattern

**No instance of `if ! cmd; then rc=$?` remains anywhere in `scripts/ci`.** The
only two places an exit status is captured both use the correct form:
`require-checks_test.sh:177` (`wait "$pid" || rc=$?`) and `:432`
(`… || rc=$?`). The two surviving `if !` constructs are a `grep` in an `elif`
and a `grep` condition in `require-checks.sh:121` — neither captures `$?`.

**Were the pre-existing 45 Vidra-adapted cases silently passing for the same
reason? No.** I read the `expect()` helper as it stood at `5672bfd`: it already
used `wait "$pid" || rc=$?`. The bug was confined to the newly written
`floor_expect`, and the builder found and fixed it before this SHA.

I did not take that on reading alone. Two mutations to guards the **pre-existing**
cases cover:

| Mutation | Suite result |
|---|---|
| baseline | 55 cases, 62 assertions, **0 failed** |
| M1 — delete the abbreviated-SHA guard in `require-checks.sh` | 55 cases, **1 failed** |
| M2 — make a non-success conclusion pass (`if (0) bad = bad …`) | 55 cases, **14 failed** |
| restored | 55 cases, **0 failed** |

The suite is genuinely armed, not vacuously green.

## R5. D5 reproduced — the floor guard

Mutating `.github/required-checks.txt` myself, running the guard directly:

| Mutation | Exit | Message |
|---|---|---|
| delete the `frontend` line | **1** | `frontend: missing. It is not listed, so \`ci-required\` would not wait for it.` |
| `frontend` → `?frontend` | **1** | `frontend: marked optional (\`?frontend\`). An optional lane passes when it never runs, so this is a removal with extra steps.` |
| `contract` → `?contract` | **1** | `contract: marked optional (\`?contract\`) …` |
| restored | **0** | `OK: .github/required-checks.txt still requires the floor: frontend contract.` |

Tree clean afterwards. **D5 reproduced, red by name each time.**

**Is the floor list in a CODEOWNERS-covered path?** Yes. The floor is the default
in `scripts/ci/check-required-floor.sh:37` (`FLOOR=${FLOOR:-"frontend contract"}`),
and `.github/CODEOWNERS` covers `/scripts/ci/` and `/.github/` (and
`/eslint-rules/` and `/contracts/`) with `@yegamble`, plus a `*` default so no
path is silently unowned. `ci-guard.yml` invokes the guard with **no `FLOOR`
override**, so the reviewed default applies. The path filter on `ci-guard`
already includes `.github/required-checks.txt`, so a PR that edits the manifest
triggers the lane that checks it.

The builder's CODEOWNERS header states plainly that the file does nothing until
the owner applies a ruleset requiring Code Owner review — which matches ADR-002
items 9–10 and is honest rather than an implied protection claim.

## R6. Timeout

Read and then mutation-tested, not taken on assertion:

- **Default applies when the caller passes none** — `boundedSignal` uses
  `apiTimeoutMs()` (default 10 000 ms) when `timeoutMs === undefined`.
- **A caller cannot extend past the ceiling** —
  `Math.max(1, Math.min(timeoutMs, ceiling))`, so a longer request is clamped.
- **`apiTimeoutMs()` cannot be disabled by typo** — unset, empty, non-numeric,
  zero and negative all fall back to the default rather than removing the bound.
- **The caller's own signal is composed**, not replaced (`AbortSignal.any`), and
  an external abort is reported as `network`, not `timeout`.

Mutations:

| Mutation | `lib/api/fetch.test.ts` |
|---|---|
| T1 — remove the default (unbounded when the caller passes none) | **2 failed** / 51, run took 10 098 ms |
| T2 — remove the ceiling clamp (`Math.max(1, timeoutMs)`) | **1 failed** / 51 |
| restored | 51 passed |

**Does the timeout test really exercise an aborted request, or assert a
constant?** A real abort. The `neverAnswers()` stub returns a promise that only
settles by rejecting on the abort signal (including one already aborted at call
time), and T1's run spent 10.1 s on real timers before failing — a constant
assertion would have failed instantly. **FINDING 2 CLOSED.**

## R7. False positives, and the "two spellings" question

**No false positives reachable by a normal author.** I wrote a realistic page
using both helpers in six shapes — revalidated read, no-store read with an
interpolated query, viewer read, POST with a JSON body, upload with
`uploadIntent` and a shorter `timeoutMs`, and options passed as a variable —
and linted it: **zero messages**. The fail-closed rule only inspects `fetch`
calls, and `no-raw-fetch` already bans those outside `lib/api/fetch.ts`, so the
entire pressure of failing closed lands on **one file** — the file whose author
is, by definition, changing the privacy control. That is the right blast radius.

**Is `publicFetch`'s "two spellings" sound or a contortion?** Sound, and I would
have accepted it without the comment. The previous code chose its cache posture
with a spread (`...(freshness === "no-store" ? … : …)`), which the fail-closed
rule now correctly reports as an init it cannot read. The rewrite is a ternary
over two fully literal inits, duplicating `method`, `headers` and `signal` across
roughly six lines. It is mild duplication in the single most safety-critical
function in the repository, it is visible rather than hidden, the comment states
the trade, and the alternatives — exempting the file, or an inline
`eslint-disable` — are both strictly worse. Not a contortion that would push a
future author to disable the rule; the rule is unreachable from the code future
authors actually write.

## R8. CI on 9767015

All four manifest lanes executed and concluded `success`; none skipped,
cancelled or timed out:

| Check | Conclusion | Window |
|---|---|---|
| `guard` | success | 18:23:54 → 18:24:06 |
| `contract` | success | 18:23:54 → 18:24:27 |
| `frontend` | success | 18:23:55 → 18:24:48 |
| `docker-build` | success | 18:23:55 → 18:24:54 |
| `ci-required` | success | 18:24:30 → 18:25:21 |
| `GitGuardian Security Checks` | success | third-party app, not in the manifest |

The fan-in log confirms it gated **this** SHA and waited:

```
CHECK_SHA: 9767015444fa8bdbf1a1326f1cc58b41d068ba14
ci-required: manifest .github/required-checks.txt
waiting: frontend (in_progress) docker-build (in_progress)
OK: every required check on 9767015444fa8bdbf1a1326f1cc58b41d068ba14 concluded success.
```

The `guard` log confirms the **new** floor step and the enlarged suite both ran
in CI on this SHA:

```
OK: all 4 entries in .github/required-checks.txt map to a defined job.
OK: .github/required-checks.txt still requires the floor: frontend contract.
require-checks_test: 55 cases, 62 assertions, 0 failed
```

`frontend` reports `Test Files 5 passed (5) / Tests 116 passed (116)`.

## R9. D2 re-run at this SHA — both layers

Weakening `viewerFetch` from `cache: "no-store"` to `next: { revalidate: 60 }`
(`lib/api/fetch.ts:240`) now fails **twice**:

| Layer | Result |
|---|---|
| `npm run lint` | **exit 1** — `vizra/no-identity-headers-in-cached-fetch` at 240:15 |
| `lib/api/fetch.test.ts` | **31 of 51 failed** — the method × json × uploadIntent table |
| restored | lint exit 0, 51 passed, tree clean |

That is the defence in depth the fix round was asked for: a syntactic
rearrangement that kept lint green would still be caught by the runtime table,
which asserts `init.cache === "no-store"` and `init.next === undefined` across
all 30 combinations, plus `cookies()` being consulted on every `viewerFetch`
path (1 call per invocation, 0 for `publicFetch`).

## R10. Finding 4 (round 1) — closed

`Dockerfile` now uses `addgroup -S -g 1001 nodejs && adduser -S -u 1001 -G nodejs nextjs`.
In the container I built and ran from this SHA:

```
$ docker exec vizra-user-verify2 id
uid=1001(nextjs) gid=1001(nodejs) groups=1001(nodejs)
$ ls -ln /app/server.js
-rw-r--r-- 1 1001 1001 7198 … /app/server.js
```

Still non-root, and the `--chown=nextjs:nodejs` group half is now real.
`GET /health` → 200; the leak scan (env var names, the configured upstream,
`API_TIMEOUT_MS`, the session cookie name) returns nothing. **FINDING 4 CLOSED.**

## R11. Findings at 9767015

```
FINDING 6: globalThis["fetch"] — the computed-member spelling still escapes both rules
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-user
  files:     eslint-rules/no-raw-fetch.mjs:110-113 (`MemberExpression(node) { if (node.computed) return; … }`)
  requirements: VZ-FOUND-002; ADR-003 § SSR identity

Observed:
  The alias ban closed `const alias = fetch` and
  `const { fetch: d } = globalThis`, and every indirection I could think of —
  Reflect.apply, .call, .bind, (0, fetch), [fetch][0], { fetch } — is now
  reported. The bracket spelling is not. In a page file, all four of these
  produced ZERO lint messages of any rule:

      const a = await globalThis["fetch"](url, { headers: { cookie }, next: { revalidate: 60 } });
      const b = await window["fetch"](url,     { headers: { cookie }, next: { revalidate: 60 } });
      const g = globalThis["fetch"]; const c = await g(url, { headers: { cookie }, next: { revalidate: 60 } });
      const d = await globalThis[`fetch`](url, { headers: { cookie }, next: { revalidate: 60 } });

  `no-raw-fetch.mjs`'s MemberExpression visitor returns immediately on
  `node.computed`, and the identity rule does not recognise the call as a fetch,
  so neither looks. The runtime test does NOT cover this: `lib/api/fetch.test.ts`
  asserts the two helpers' behaviour, and a page reaching the global this way is
  exercised by no test at all.

Failure:
  A page can send `__Host-vizra_session` on a `next: { revalidate: 60 }` request
  with a completely clean lint run — the same shared-cache leak, by the same
  mechanism, as the alias hole just closed. Nothing leaks on this SHA: no
  product code calls the API yet.

Perspective:
  visitor, member, developer

Recommendation:
  In the MemberExpression visitor, instead of returning on any computed access,
  read a computed property that is a string Literal (or a TemplateLiteral with
  no expressions) and treat the value "fetch" exactly as the non-computed
  spelling is treated. Roughly four lines, symmetrical with the fix already made.

Acceptance criteria:
  - `globalThis["fetch"](url, {})` and `window["fetch"](url, {})` are errors
    outside the allow-list, and `globalThis["fetch"]` as a VALUE is
    `aliasedFetch` in every file including lib/api/fetch.ts.
  - The template-literal spelling behaves the same.
  - A genuinely dynamic computed access (`globalThis[name]`) is still allowed,
    or is reported — either is defensible, but say which.
  - `client["fetch"](…)` on some other object stays clean.

Tests:
  `eslint-rules/no-raw-fetch.test.mjs` — four invalid cases and one valid case
  as above. The harness exists and runs under `npm run test`.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  Nobody writes `globalThis["fetch"]` by accident, so this is only reachable by
  someone deliberately evading a control they could equally evade with
  `eslint-disable-next-line`, and no syntactic rule ever terminates. That is the
  strongest argument, and it is why I rated this SHOULD rather than REQUIRED —
  unlike `const alias = fetch`, which arises from ordinary refactoring (extracting
  a helper, injecting fetch for testability), the bracket form does not. My
  answer is only that it is the same hole shape the fix round just closed, the
  fix is symmetrical and four lines, and leaving one spelling open invites the
  question of why the others were worth closing.
```

```
FINDING 7: a whitespace-only FLOOR override passes vacuously
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-required-floor.sh:37,43
  requirements: VZ-FOUND-002; ADR-002 § CI fan-in

Observed:
  `FLOOR=${FLOOR:-"frontend contract"}` then `for want in $FLOOR`. An EMPTY
  FLOOR correctly falls back to the default (`:-` treats empty as unset) — I
  checked, and `FLOOR="" bash check-required-floor.sh` still enforces
  `frontend contract`. But a whitespace-only value is non-empty, so the default
  does not apply and the loop iterates zero times:

      $ FLOOR=" " bash scripts/ci/check-required-floor.sh .github/required-checks.txt
      OK: .github/required-checks.txt still requires the floor:  .
      EXIT=0

Failure:
  Nothing today: `ci-guard.yml` invokes the script with no FLOOR override, and
  both the script and the workflow are CODEOWNERS-covered. It is a latent
  vacuous-pass in a gate-integrity script whose entire purpose is to refuse to
  pass vacuously — the same class of defect as the empty-manifest case the
  suite already covers ("an empty manifest fails rather than vacuously passing").

Perspective:
  developer

Recommendation:
  After resolving FLOOR, fail when it contains no non-whitespace token — one
  line, mirroring the existing empty-manifest guard.

Acceptance criteria:
  `FLOOR=" "` and `FLOOR=""` both either enforce the default or exit non-zero;
  neither prints OK with an empty floor list.

Tests:
  `scripts/ci/require-checks_test.sh` — one `floor_expect 1` case with a
  whitespace-only FLOOR. The harness exists.

Cross-repo implications:
  core: none | user: as above | search: same script when it lands | meta: same.

Challenge:
  FLOOR is only ever set by the test suite, so this is unreachable in practice.
  Agreed — hence NIT.
```

**Carried over, unchanged and still OPEN:** FINDING 3 (the manifest's
`source_commit` is provenance no check verifies — still gated on the read-only
`vizra-core` token, still recorded as Owed in the repo's AGENTS.md) and
FINDING 5 (ADR-001's licence table still carries `[pin at PR time; verify]` for
React, Tailwind and TypeScript — a meta-repo follow-up this PR cannot make).
Neither was in the fix round's scope and neither regressed.

## R12. Verdict at 9767015

**PASS.**

- **FINDING 1 — CLOSED.** All nine bypasses I found in round 1 are now reported;
  twelve further indirection shapes I invented are reported; the false backstop
  sentence is gone from the docblock and the replacement text states the rule's
  reach accurately; and a runtime layer now asserts the property directly, which
  I confirmed by mutation (lint red *and* 31 runtime tests red).
- **FINDING 2 — CLOSED.** Default and ceiling both present, both mutation-tested,
  timeout path exercises a real abort.
- **FINDING 4 — CLOSED.** `gid=1001(nodejs)` in the running container.
- **No test was weakened.** Zero valid cases removed from either rule test file;
  the single deleted invalid case is coverage-neutral and I proved the behaviour
  it asserted is still enforced. The test surface grew 50 → 116 tests and
  14 → 30 invalid rule cases, and an eslint exemption was removed rather than added.
- **The shell suites are armed**, including the 45 pre-existing Vidra cases,
  which were never affected by the `if ! cmd` bug — proven by mutation, not by
  reading.
- **CI green on this SHA**, all four manifest lanes executed, fan-in gated the
  real head, and the new floor step and enlarged suite both ran in CI.
- FINDING 6 (SHOULD) and FINDING 7 (NIT) are new and neither blocks: no product
  code calls the API on this SHA, and FINDING 6 needs conscious evasion rather
  than ordinary refactoring.

Unchanged from round 1 and still true: this PASS covers **vizra-user's half of
VZ-FOUND-002 only**. Core's route↔spec both-direction test has not landed, so
the ledger entry must not reach VERIFIED on this evidence alone; and the `main`
ruleset (required `ci-required` context, Code Owner review, force-push and
deletion blocks, linear history) remains an owner action that CODEOWNERS being
committed does not substitute for.

## R13. Cleanup (re-verification)

Second clone at `…/scratchpad/verify2/vizra-user` deleted. Probe files
(`lib/api/probe.ts`, `app/probe/page.tsx`, `app/fp/page.tsx`,
`eslint-rules/deleted-case.test.mjs`) and every mutation were reverted and the
tree confirmed clean before deletion. Docker image `vizra-user:verify2` and
container `vizra-user-verify2` removed; the build cache I created pruned. The
containers `vizra-verify-run`, `vizra-pr1-redis`, `vizra-pr1-cache`,
`vizra-pr1-pg` and the `vidra-ipfs-071-*` set are not mine and were left alone.
