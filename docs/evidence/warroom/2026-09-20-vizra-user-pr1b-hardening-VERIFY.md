# Independent verification — vizra-user PR #2 (PR1b "hardening") at 6b0ba871d3ccdda9f3d054398335138b08e84fd8

Verifier: `vizra-verifier` seat, dispatched by the war-room chair 2026-09-20. This
agent did not write the code under review. Read-only on the repository under test;
the only file written is this one.

**VERDICT: PASS.** All five findings CLOSED. `ci-required` green on this SHA with
every manifest lane actually executed. No blocking finding. Three NITs and two
recording observations are filed below; none blocks the merge.

PASS is not a merge and does not make any ledger entry VERIFIED. The chair records
those.

---

## R1. Scope and inputs

| Item | Value |
|---|---|
| PR | https://github.com/yegamble/vizra-user/pull/2 |
| Head SHA verified | `6b0ba871d3ccdda9f3d054398335138b08e84fd8` |
| Head confirmed unmoved | yes — `gh api .../pulls/2` returned `head_sha 6b0ba871…`, `headRefName chore/m0-hardening`, `state OPEN`, `mergeable true` |
| Base | `main` @ `752253cb13409de251c7ec7ea896af2eba579095` |
| Diff | 36 files, +1789 −30 |
| Findings under review | SECURITY.md F4 (`server-only`), F5 (digest pin + scan lanes), F6 (non-local `$ref`), closure-section FLOOR note; VERIFY.md F6 (computed-member fetch), F7 (blank FLOOR) |
| Builder's plan | `/Users/yosefgamble/github/vizra/docs/plans/2026-09-20-vizra-user-pr1b-hardening.md` |

The builder's in-repo transcripts under `docs/evidence/pr1b/` were read as **claims**.
Every number below is from my own run in my own clone.

## R2. Environment

macOS 26.5.1 (Darwin 25.5.0), arm64. node v22.14.0, npm 10.9.2, Docker 29.8.0
(daemon `linux/aarch64`). Clean clone at
`…/scratchpad/vfy-pr1b-78006/vizra-user`, checked out at the head SHA,
`git status` clean. `npm ci` exit 0, 411 packages, `found 0 vulnerabilities`.

Disk at the image step: 17 GiB free (threshold was 8 GiB), so **the local image
build WAS run**, natively on arm64. linux/amd64 is covered by CI's `docker-build`
and `image-scan` on this SHA (ADR-009's acceptance platform); no emulated amd64
build was attempted.

**Incident, recorded because it affected method:** my first clone at
`…/scratchpad/verify/vizra-user` was deleted out from under me by a concurrent
agent between two commands. I re-cloned into a uniquely named directory. No
result below comes from the deleted tree.

## R3. Gate, reproduced from the clean clone

| Command | Exit | Counts |
|---|---|---|
| `npm ci` | 0 | 411 packages, 0 vulnerabilities |
| `npm run ci` (lint → typecheck → vitest → build) | 0 | **6 files, 147 passed, 0 skipped** |
| `npm run check:contract` | 0 | spec sha256 `128d0509238a…`, client byte-for-byte |
| `node scripts/check-spec-refs.mjs` | 0 | 9 `$ref`s, all in-document |
| `bash scripts/ci/require-checks_test.sh` | 0 | **70 cases, 77 assertions, 0 failed** |
| `bash scripts/ci/check-required-floor.sh` | 0 | floor `frontend contract` |
| `bash scripts/ci/check-image-pins.sh` | 0 | 3 FROM lines pinned at node 22.14.0 |
| `bash scripts/ci/check-client-bundle.sh` | 0 | 10 chunks, no leak |
| `bash scripts/ci/check-server-only-boundary.sh` | 0 | build failed with 4 server-only diagnostics, both modules named |

**The builder's claimed counts are exact.** 147 tests / 0 skipped and
70 cases / 77 assertions reproduce identically. `passWithNoTests: false` is set
(`vitest.config.mts:37`); no `.skip`, `.todo`, `.only` or `xit` exists anywhere
in the tree.

---

## R4. A1 — security FINDING 4 (`server-only`)

### A1.1 Deletion demonstrations — the guard fails BY NAME per module

`scripts/ci/check-server-only-boundary.sh` writes two probe routes, one per
module, and requires Next's server-only diagnostic to be attributed to each.

| Mutation | Guard exit | Named error |
|---|---|---|
| baseline, both imports present | 0 | `OK: the build failed (exit 1) with 4 server-only diagnostics, attributed to both modules` |
| delete `import "server-only"` from `lib/api/fetch.ts` only | **1** | `lib/api/fetch.ts: no server-only diagnostic attributed to it` |
| delete from `lib/config.ts` only | **1** | `lib/config.ts: no server-only diagnostic attributed to it` |
| delete **both** | **1** | both modules named, one line each |

This is the criterion the builder's own first attempt failed. The per-module
probe is what makes it real: `lib/api/fetch.ts` also imports `next/headers`,
which Next refuses independently, so a single-probe guard would have "passed"
on the wrong diagnostic.

### A1.2 I tried to fool the rewritten guard the way the first one was fooled

Both attempts were made with **both imports deleted**.

| Attack | Guard exit | Result |
|---|---|---|
| literal `server-only` planted in a comment, a `const` string, and a thrown `Error` message in both modules (4 and 7 occurrences of the phrase respectively) | **1** | both modules named as missing — not fooled |
| the **exact diagnostic sentence** `// Error: 'server-only' cannot be imported from a Client Component module` planted as source text in both modules | **1** | both modules named as missing — not fooled |

The guard strips ANSI, then requires the diagnostic sentence to appear within
one line **after** the offending module's own `./<path>:` header. Planting the
sentence in source does not satisfy that, because Next's code frame quotes it
under a different path context. The rewrite genuinely closes the flaw the
builder disclosed.

### A1.3 The client-bundle check really finds a leak

I planted a real leak using the actual inlining vector — a `"use client"` page
reading `process.env.INTERNAL_API_BASE_URL` and `process.env.PUBLIC_ORIGIN`
directly — and built with sentinel values.

- Build exit 0 (the leak ships silently, which is the point).
- `check-client-bundle.sh` exit **1**: `server-side identifier 'INTERNAL_API_BASE_URL' appears in: .next/static/chunks/0d7l7iuvbbwsd.js`, and the same for `PUBLIC_ORIGIN`.
- Fixture removed, rebuilt: exit **0**, `OK: 10 chunks under .next/static, none carrying server-side configuration`.
- Vacuity: pointed at an empty directory → exit **1**, `no chunks found … refusing to pass vacuously`.

`frontend-ci.yml` passes real sentinels (`SENTINELS: "http://api.sentinel.invalid:8080 https://origin.sentinel.invalid 4242"`), so CI tests an outcome rather than trusting that a real value would have been noticed. Verified in the workflow diff.

**A1 CLOSED.**

---

## R5. A2 — security FINDING 5 (digest pin + scan lanes)

### A2.1 The digests genuinely belong to node 22.14.0-alpine, amd64 AND arm64

Pinned digest in all three stages: `sha256:9bef0ef1e268f60627da9ba7d7605e8831d5b56ad07487d24d1aa386336d1944`.

Verified two independent ways:

1. `docker buildx imagetools inspect node:22.14.0-alpine` → top-level
   `Digest: sha256:9bef0ef1…`, `MediaType: application/vnd.oci.image.index.v1+json`.
2. Raw registry API (no Docker): `GET registry-1.docker.io/v2/library/node/manifests/22.14.0-alpine`
   returned header `docker-content-digest: sha256:9bef0ef1e268f60627da9ba7d7605e8831d5b56ad07487d24d1aa386336d1944`.

Platforms inside that index: **`linux/amd64`** (`sha256:01393fe5…`) and
**`linux/arm64/v8`** (`sha256:4a78eedb…`), plus arm/v6, arm/v7, s390x. It is the
multi-arch **index** digest, not a per-platform manifest — which is what the
Dockerfile comment claims and what makes one pin serve both the amd64
acceptance platform and an arm64 dev machine.

### A2.2 Guard mutations

| Mutation | Exit | Named error |
|---|---|---|
| baseline | 0 | `OK: all 3 external FROM lines … @sha256-pinned at node 22.14.0` |
| strip `@sha256` from the runner stage | **1** | `node:22.14.0-alpine: not pinned to an immutable @sha256 digest` |
| truncate a digest to 63 chars | **1** | `@sha256 digest is 63 characters, want 64` |
| bump `.nvmrc` to 22.15.0, Dockerfile untouched | **1** | `tag '22.14.0-alpine' does not match .nvmrc ('22.15.0')` (×3) |

`.nvmrc`, the tag and the digest are tied together: the third case is the
acceptance criterion "bumping `.nvmrc` without updating the digest fails a
check", and it does, by name. See FINDING V3 for the one mismatch that slips
through.

### A2.3 Scan lanes fail on scanner ERROR

Both lanes have the same two-step shape: a **recording** run that writes an
artifact, and a **verdict** run that re-invokes the scanner. The verdict does
not read the artifact — that is what makes a crashed scanner red.

- `deps-scan`: recording is `npm audit --json > npm-audit.json || true`. The
  `|| true` is scoped to recording. The summarise step runs `jq` under
  `set -euo pipefail` (I confirmed locally: malformed JSON → exit 5; `{}` →
  exit 5, `null has no keys`). The verdict step `npm audit --audit-level=high`
  is unmasked, so a broken npm exits non-zero → job red.
- `image-scan`: both trivy invocations are pinned at `version: v0.70.0` with the
  action pinned by commit SHA. The verdict uses `exit-code: "1"`,
  `ignore-unfixed: false`, `severity: HIGH,CRITICAL`. A crashed trivy fails the
  action step → job red.
- **No `continue-on-error` anywhere.** `ci-guard` asserts this at runtime
  (`OK: no unmarked continue-on-error.`) and a full step-level enumeration of
  every job on this SHA found zero steps with conclusion other than `success`.
- `if: always()` on the upload steps affects step execution only, not job
  conclusion, and both uploads use `if-no-files-found: error`.

### A2.4 They ran on this SHA and published artifacts

Both `deps-scan` and `image-scan` ran (run `35531071982`, event `pull_request`),
both `success`.

- `deps-scan`: `info 0, low 0, moderate 0, high 0, critical 0, total 0`; verdict
  step `found 0 vulnerabilities`, exit 0.
- `image-scan`: trivy enumerated `alpine 3.21.3` with `pkg_num=17` plus every
  node-pkg target; `TOTAL: 0`; verdict `success`. `INPUT_TRIVYIGNORES:` empty, so
  nothing was suppressed.
- Artifacts: `trivy-image-f0665032…` (7624 B) and `npm-audit-f0665032…` (317 B),
  neither expired. See observation V4 on their naming.

### A2.5 Is the builder's condition for promoting them to required reasonable?

**Yes, and I would not promote them today.** The manifest and the workflow both
state the reason in writing: `ci-guard` forbids `continue-on-error` (correctly),
so a required scan lane has no honest way to absorb a CVE published against an
unfixed upstream package with no change to this repo — and a required lane that
goes red on its own is how a team learns to merge past red. The stated remaining
condition is *an agreed route for an unfixed upstream CVE — a reviewed, expiring
`.trivyignore.yaml` entry* — not the baseline, which is already zero. That is the
right gating condition, it is written where the next reader will find it
(`.github/required-checks.txt`, the `DELIBERATELY ABSENT` block), and promotion
is correctly scoped as an owner-reviewed change to both the manifest and the
floor. I endorse it.

**A2 CLOSED.**

---

## R6. A3 — security FINDING 6 (non-local `$ref`)

The guard is wired **inside `generate()`, before `execFileSync`**
(`scripts/codegen.mjs:51-59`), so both `npm run codegen` and the `contract` lane
are covered, and `contract-ci.yml` also runs it as a visible step of its own.

I applied the realistic attack — poison the spec **and resync
`contracts/manifest.json`'s sha256 to match**, which any contributor can do:

| Poisoned `$ref` | `npm run check:contract` | Named error | Generator banner / network |
|---|---|---|---|
| `https://attacker.invalid/evil.yaml#/Health` | **1** | `codegen refused the contract: … contains 2 non-local $refs: line 60 … line 66` | **0 lines** |
| `./sidecar.yaml#/Health` | **1** | same, both lines named | **0 lines** |
| `../../../etc/passwd` | **1** | same | **0 lines** |
| `//attacker.invalid/x.yaml#/H` | **1** | same | **0 lines** |
| restored | **0** | `✅ contract: … matches its manifest (sha256 128d0509238a…)` | generator ran normally |

The zero banner count is the load-bearing evidence: `✨ openapi-typescript`,
`🚀`, `fetch failed` and `Can't resolve` are all absent, proving the refusal
happens **before** the generator reads the spec, so no outbound request is
issued. The current spec passes unchanged and `lib/api/generated.ts` is
untouched.

**A3 CLOSED.**

---

## R7. A4 — verifier FINDING 6 (computed-member access to global fetch)

Driven through the repo's own ESLint 10 on a page file outside the allow-list.

### Acceptance cases

| Spelling | Result |
|---|---|
| `globalThis["fetch"](url, init)` | `rawFetch` |
| `window["fetch"](url, init)` | `rawFetch` |
| `` globalThis[`fetch`](url, init) `` | `rawFetch` |
| `const g = globalThis["fetch"]` (as a value) | `aliasedFetch` |
| `globalThis[name]` (dynamic key) | `dynamicGlobalMember` |
| `` globalThis[`fet${x}`] `` | `dynamicGlobalMember` |
| `const { ["fetch"]: df } = globalThis` | `aliasedFetch` |
| `const { [key]: dk } = globalThis` | `dynamicGlobalMember` |
| `client["fetch"](url)` | **silent** ✓ |
| `registry[name]` | **silent** ✓ |
| `rows[0]` | **silent** ✓ |
| `client[name]` | **silent** ✓ |

Every acceptance bullet met, including the "unrelated objects stay clean" half.

### Spellings I invented — reported vs silent

| Spelling | Result |
|---|---|
| `globalThis?.["fetch"](url, init)` (optional chaining, computed) | **`rawFetch`** |
| `window?.fetch(url, init)` (optional chaining, dotted) | **`rawFetch` + `unreadable`** |
| `globalThis["fe" + "tch"](url, init)` (concatenated key) | **`dynamicGlobalMember`** (fails closed) |
| `(globalThis)["fetch"](url, init)` (parenthesised) | **`rawFetch`** |
| `(0, globalThis["fetch"])(url, init)` (sequence) | **`aliasedFetch`** |
| `self["fetch"](url, init)` | **SILENT** — see FINDING V1 |
| `self.fetch` | **SILENT** — see FINDING V1 |
| `Reflect.get(globalThis, "fetch")` | **SILENT** (documented limit) |
| `const gt = globalThis; gt["fetch"]` | **SILENT** (documented limit, named in the docblock) |
| `(globalThis as any)["fetch"](url, init)` | no fetch rule fires, but `unexpectedAny` errors → lint still red |

### Arming

I reverted the rule's computed-key handling to the base behaviour. Four of the
new test cases went red (`const f = globalThis[name]`, `window[name](url, {})`,
`` globalThis[`fet${suffix}`](url) ``), `Tests 4 failed | 143 passed`. Restored →
147 passed. The new cases are armed, not decorative.

### Ruling on builder decision 1 — `dynamicGlobalMember` is sound, not a false-positive generator

**Sound. Keep it.** I linted a realistic page carrying the patterns that would
plausibly trip a fail-closed rule: the Next.js "cache a client on the global"
singleton (`globalThis as unknown as {...}`), the `Symbol.for` singleton,
`"IntersectionObserver" in window` feature detection,
`window["IntersectionObserver"]`, an analytics shim reading
`(window as Record<string, unknown>)[key]`, `window.location.href`, and
`window["localStorage"]`. **Every line was silent.**

The reason it does not over-fire is structural: the rule requires
`node.object.type === "Identifier"` and the name to be exactly `globalThis` or
`window`. The idiomatic singleton and shim patterns go through a TypeScript cast
(`TSAsExpression`), which the rule skips entirely; readable literal keys that
are not `fetch` are skipped; and unrelated objects are never examined. The
repository's own `npm run lint` is exit 0. This will not push authors toward
`eslint-disable`.

**A4 CLOSED.**

---

## R8. A5 — verifier FINDING 7 (blank FLOOR)

| `FLOOR` value | Exit | Behaviour |
|---|---|---|
| unset | 0 | enforces default `frontend contract` |
| `" "` (single space) | **1** | `FLOOR resolved to no lanes (value: ' ')` |
| `""` (empty) | 0 | `:-` substitutes → enforces the **default**, not an empty floor |
| `$'\t'` (tab) | **1** | `FLOOR resolved to no lanes` |
| `"   "` (three spaces) | **1** | `FLOOR resolved to no lanes` |
| `$' \t \n '` (mixed whitespace) | **1** | `FLOOR resolved to no lanes` |
| `"frontend contract"` | 0 | enforces both |
| `"nosuchlane"` | **1** | `no longer requires the floor this repository merges on` |

**No value passes vacuously.** The acceptance criterion ("`FLOOR=" "` and
`FLOOR=""` both either enforce the default or exit non-zero") is met. Arming
confirmed: neutering the guard's zero-lane test turned suite cases 62 and 63
red (`70 cases, 77 assertions, 2 failed`); restored → 0 failed.

### Ruling on builder decision 2 — keeping the env override is ACCEPTABLE

**No workflow or PR-controlled input can set `FLOOR` in CI.** I grepped the
entire tree (excluding `node_modules`, `.git`, `docs/evidence`). `FLOOR` appears
in exactly two files: `scripts/ci/check-required-floor.sh` (the guard itself)
and `scripts/ci/require-checks_test.sh` (its regression suite, which needs the
override to drive the guard). No `.github/workflows/*.yml` sets it; no
`env:` block references `github.event.*` or `inputs.*` for it. `ci-guard.yml`
invokes the script with no override. Reaching the override requires a
CODEOWNERS-covered `.github/` or `scripts/ci/` edit. **Acceptable — no finding.**

**A5 CLOSED.**

---

## R9. Rulings on the remaining builder decisions

### Decision 3 — the vitest `server-only` alias does NOT leak into the production build or weaken the boundary

**Confirmed clean.** Three independent checks:

1. **It cannot reach the build.** `vitest.config.mts` is not a Next build input;
   `next.config.ts`, `tsconfig.json` and the `build` script reference nothing
   from it. The alias exists only in the vitest resolver.
2. **It points at the package's own file, not a stub.**
   `node_modules/server-only/package.json` declares
   `exports: {".": {"react-server": "./empty.js", "default": "./index.js"}}`.
   `empty.js` is 0 bytes — exactly the file the `react-server` condition selects,
   which is what Next resolves for a Server Component. `index.js` (the throwing
   default entry) is untouched, and that is the file a Client Component hits.
3. **`server-only` is not even in the shipped image.** Inside the running
   production container, `/app/node_modules` contains `client-only` but no
   `server-only` — it is tree-shaken out of the standalone bundle. There is
   nothing for the alias to leak into.

The boundary is a bundler property that vitest cannot observe at all, and it is
asserted by `check-server-only-boundary.sh`, which I independently drove red and
green in R4. `server-only@0.0.1` is a real registry dependency with a lockfile
integrity hash, correctly placed in `dependencies` (the build needs it).

**What was removed from `vitest.config.mts` (−3/+23):** exactly the three lines
of the old object-form alias —
`alias: { "@": fileURLToPath(new URL(".", import.meta.url)) },` — replaced by the
array form `{ find: /^@\//, replacement: … }` plus the `server-only` entry and
its 13-line explanatory comment. The `@` alias is preserved with equivalent
semantics; **no test setting was weakened, no `exclude` added, no threshold
changed.** `passWithNoTests: false` is retained.

### Decision 4 — removing npm/npx/yarn/corepack: JUSTIFIED, and it works

I built the image natively on arm64 (`BUILD_EXIT=0`) and ran it.

| Assertion | Result |
|---|---|
| base digest actually resolved | `node:22.14.0-alpine@sha256:9bef0ef1…` — the pinned one |
| `/health` numeric HTTP status | **200**, body `data-testid="health-status">ok</dd>` |
| runtime identity | `uid=1001(nextjs) gid=1001(nodejs) groups=1001(nodejs)` |
| `npm` / `npx` / `yarn` / `yarnpkg` / `corepack` at runtime | **all absent** |
| `node` at runtime | `v22.14.0` |
| process tree | `PID 1 nextjs next-server` — nothing needs a package manager |
| HEALTHCHECK after start-period | `healthy`, `running=true`, `restarts=0` |

I recorded the **numeric 200** that CI never logs (CI relies on `curl --fail`
semantics plus a body assertion — see observation V5).

**The removal is asserted in the same `RUN`.** `Dockerfile:86-96`: the `rm -rf`
is chained with `&&` into a loop
`for gone in npm npx yarn yarnpkg corepack; do if command -v "$gone" …; then echo "runner stage: $gone survived removal at …"; exit 1; fi; done`,
then `node --version`. A future base image that moved a path fails the build
rather than silently re-shipping it. I confirmed in the local build log that
layer `#10` completed with `v22.14.0` and no `survived removal` line.

**The removal targets are real, not vacuous.** Against the pinned base image, all
five binaries exist and every single `rm -rf` path resolves —
`/opt/yarn-v1.22.22` (the glob), `/usr/local/lib/node_modules/npm`,
`/usr/local/lib/node_modules/corepack`, and the five `/usr/local/bin` entries.
The npm vendored tree contains `minimatch`, `glob`, `@sigstore`, `@tufjs`,
`@npmcli` and `pacote` — exactly the packages the builder names as the 53-finding
surface, corroborating the rationale structurally.

**Ruling: going beyond FINDING 5's literal text is justified here.** F5's stated
end state is a scan lane whose baseline is clean enough to promote. Leaving 3
CRITICAL and 35 HIGH findings in a tree the runtime never uses would have meant
either a permanently red lane or an ignore-file suppressing real CVEs — both
worse than deletion. The removal is narrow (one stage, the one that ships),
asserted, documented in place with the measurement that motivated it, and
verified by me not to break the app. It also removes install capability from a
runtime shell, which is a defensible hardening in its own right. I would have
raised a finding had it been unasserted or had it touched the builder stage; it
is neither.

---

## R10. GitHub CI on this SHA

All 8 check runs on `6b0ba871…` are `completed` / **`success`**. Nothing skipped,
cancelled, timed out, neutral or missing.

| Check | Conclusion | Event |
|---|---|---|
| `ci-required` | success | pull_request |
| `frontend` | success | pull_request |
| `contract` | success | pull_request |
| `guard` | success | pull_request |
| `docker-build` | success | pull_request |
| `deps-scan` | success | pull_request |
| `image-scan` | success | pull_request |
| `GitGuardian Security Checks` | success | (app) |

**`ci-required` waited for the floor lanes and gated the real head.** Runtime
output, verbatim:

```
ci-required: commit 6b0ba871d3ccdda9f3d054398335138b08e84fd8
ci-required: manifest .github/required-checks.txt
  - frontend
  - contract
  - ?guard
  - ?docker-build
waiting: frontend (in_progress) contract (in_progress) guard (in_progress) docker-build (queued)
waiting: frontend (in_progress) docker-build (in_progress)
OK: every required check on 6b0ba871d3ccdda9f3d054398335138b08e84fd8 concluded success.
```

`CHECK_SHA` was the **head** SHA, not the merge commit — correct.

**The manifest matches the jobs that actually ran.** All four entries executed as
real check runs on this SHA; both `?`-optional lanes ran rather than being
path-filtered away. No lane is listed-but-absent — no false positive.
`ci-guard` independently asserted manifest integrity at runtime:
`OK: all 4 entries in .github/required-checks.txt map to a defined job.` and
`OK: .github/required-checks.txt still requires the floor: frontend contract.`

`frontend` in CI reported `Test Files 6 passed (6)`, `Tests 147 passed (147)` —
matching my local run exactly — and `ci-guard` asserted
`OK: a vitest run that collects nothing fails.`

`docker-build` (amd64) corroborates my arm64 run: same base digest resolved, the
removal layer executed with no `survived removal` line, and a runtime assertion
`runtime identity: uid=1001(nextjs) gid=1001(nodejs)` gated by a `case` that
exits 1 on anything else.

## R11. No test was weakened or deleted

Proven by `git diff --numstat`, not by reading:

- `eslint-rules/no-raw-fetch.test.mjs` — **+99 / −0**
- `scripts/ci/require-checks_test.sh` — **+135 / −0**
- `lib/api/fetch.test.ts` — **unchanged**
- `eslint-rules/no-identity-headers-in-cached-fetch.test.mjs` — **unchanged**

Across the whole PR, the only files with deleted lines are `ci-guard.yml`
(−2, comment renumbering), `AGENTS.md` (−5, documentation updated), `Dockerfile`
(−3), `no-raw-fetch.mjs` (−12, the rewritten visitor), `lib/api/fetch.ts` (−3),
`package.json`/`package-lock.json` (−1 each, the added dependency), and
`vitest.config.mts` (−3, the alias reshape covered above). **The only deletion in
product source is three lines of docblock prose in `lib/api/fetch.ts`**, replaced
by a longer and more accurate one. No assertion loosened, no case removed, no
lane demoted, no baseline or budget changed, no generated file hand-edited
(`check:contract` passes byte-for-byte), no eslint-disable added.

## R12. Diff audit against the AGENTS.md review rules

- **Privacy leaks:** none. The PR *adds* two controls against the only leak path
  in the tree and I proved both red/green. No logging of credentials, signed URLs
  or private metadata is introduced.
- **Negative tests:** present and armed — `unreadable`/`dynamicGlobalMember`
  invalid cases, the zero-lane FLOOR cases, the vacuity guards.
- **Skips / weakened assertions / hand-edited generated files:** none (R11).
- **Invented package APIs:** none. `server-only@0.0.1` verified against its own
  `package.json` `exports` and the lockfile integrity hash.
- **Unbounded resources:** no new ones; `timeout-minutes` set on both new jobs
  (15 and 30).
- **Mock data / dead controls / fake success states:** **NOT APPLICABLE** — this
  PR touches no file under `app/` and adds no UI. The UI lane (AGENTS.md step 4)
  is therefore not applicable, though I did exercise the real production image
  and confirmed `/health` renders `ok` at HTTP 200 as a non-root user.
- **False-positive CI:** specifically hunted. The fan-in polled four lanes, all
  four executed, `ci-guard` re-asserted the manifest and the floor, and every
  step of every job concluded `success`. No `continue-on-error`.
- **Secrets:** workflows carry `permissions: contents: read`,
  `persist-credentials: false`, all actions pinned to 40-char commit SHAs.

---

## R13. Findings

All five findings under review are CLOSED. The items below are new, all
non-blocking, and none affects the verdict.

```
FINDING V1: `self["fetch"]` and `self.fetch` remain silent — the sibling spelling of the hole just closed
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     eslint-rules/no-raw-fetch.mjs:165-166
             (`if (node.object.name !== "globalThis" && node.object.name !== "window") return;`)
  requirements: VZ-FOUND-002; ADR-003 § SSR identity

Observed:
  With the PR's rule, `globalThis["fetch"](url, init)` is `rawFetch` — the fix
  works. But driven through the same ESLint run in the same file:
      await self["fetch"](url, { headers: { cookie }, next: { revalidate: 60 } });  -> SILENT
      void self.fetch;                                                              -> SILENT
  I confirmed this is PRE-EXISTING, not a regression introduced here. Against the
  BASE commit's rule (752253c), all three of `globalThis["fetch"]`, `self["fetch"]`
  and `self.fetch` were silent; at HEAD the first is reported and the other two
  are not. The object-name test is unchanged context in this PR's diff.

Failure:
  `self` is the global object in the browser and in Web Workers, and in the Edge
  runtime. A page reaching `self["fetch"]` with a session cookie on a
  `next: { revalidate: 60 }` request would lint clean by the same mechanism the
  PR just closed for `globalThis`. Nothing leaks on this SHA: no product code
  calls the API, and in the Node server runtime `self` is undefined, so the SSR
  shared-cache path this control exists for would ReferenceError rather than
  leak. That is what keeps it a NIT rather than a SHOULD.

Perspective:
  developer

Recommendation:
  Add `"self"` to the two-name object test, in both the MemberExpression visitor
  and the VariableDeclarator visitor. One token in each place, symmetrical with
  the fix already made.

Acceptance criteria:
  - `self["fetch"](url, {})` and `self.fetch(url, {})` are errors outside the allow-list.
  - `self["fetch"]` as a value is `aliasedFetch` in every file.
  - A local binding named `self` is still left alone (isLocalBinding already covers this).

Tests:
  eslint-rules/no-raw-fetch.test.mjs — two invalid cases and one valid case
  (a local `const self = {...}`). The harness exists and runs under `npm run test`.

Cross-repo implications:
  core: none | user: as above | search: none | meta: none

Challenge:
  The same argument the original FINDING 6 conceded: nobody writes `self["fetch"]`
  by accident, no syntactic rule terminates, and `self` is undefined in the Node
  server runtime where the cache-leak actually bites. All true — which is why this
  is a NIT and not a blocker. The only reason to file it is that the PR's own
  rationale for closing `globalThis["fetch"]` was "leaving one spelling open
  invites the question of why the others were worth closing", and that argument
  applies verbatim to `self`.
```

```
FINDING V2: image-scan has no "refuse to pass vacuously" assertion, unlike every other guard this PR adds
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     .github/workflows/supply-chain.yml — image-scan "Summarise by severity"
  requirements: none yet — the VZ-SEC-SUPPLY-001 proposal from security FINDING 5

Observed:
  Every other guard this PR adds explicitly refuses to pass on nothing:
    check-client-bundle.sh   -> "no chunks found under $dir — refusing to pass vacuously"
    check-image-pins.sh      -> "declares no external FROM — refusing to pass vacuously"
    check-required-floor.sh  -> "FLOOR resolved to no lanes"
  image-scan's summarise step does not. I drove its exact jq locally:
    input {"Results":[]}                 -> exit 0, "TOTAL: 0"
    input {}                             -> exit 0, "TOTAL: 0"
    input {"Results":[{"Target":"x"}]}   -> exit 0, "TOTAL: 0"
    input <0-byte file>                  -> exit 0, "TOTAL: " (empty)
  Malformed JSON does fail (exit 5), and a crashed trivy fails the action step and
  the independent verdict step, so a CRASHED scanner is correctly red — I verified
  that separately. The gap is narrower: a structurally valid report that enumerated
  NOTHING is indistinguishable from a clean scan.

Failure:
  The baseline is now genuinely 0 findings, so "TOTAL: 0" is the expected green
  state — which means the lane can no longer tell "clean" from "scanned nothing".
  There is no assertion that trivy enumerated any packages. Today the CI log does
  prove real work happened (`pkg_num=17`, per-target rows), but nothing CHECKS it,
  so the proof depends on a human reading the log. Bounded: the lane is not in the
  required set, so this cannot green a merge on its own.

Perspective:
  operator, developer

Recommendation:
  One line in the summarise step, in the idiom the other three guards already use:
  assert the report enumerated at least one target/package, e.g.
      targets=$(jq '[.Results[]?] | length' trivy-image.json)
      [ "$targets" -gt 0 ] || { echo "::error::trivy enumerated no targets — refusing to pass vacuously"; exit 1; }

Acceptance criteria:
  - A trivy report with no Results fails the lane with a named error.
  - The current report (17 alpine packages plus node-pkg targets) passes unchanged.
  - A 0-byte report fails rather than printing an empty TOTAL.

Tests:
  No harness for workflow steps yet. Cheapest adequate addition: the assertion
  above is self-testing in CI; a fuller version belongs with require-checks_test.sh
  if the jq moves into a scripts/ci/ file, which would also let shellcheck see it.

Cross-repo implications:
  core: same pattern when its image scan lands | user: as above | search: same | meta: none

Challenge:
  Trivy exits non-zero on an image it cannot resolve, so reaching a valid-but-empty
  report needs an odd failure mode, and the lane is not gating. Fair — hence NIT.
  The reason to file it is consistency: this PR's own standard is that a check
  which scanned nothing is not a check, and this is the one new check that does
  not meet it.
```

```
FINDING V3: check-image-pins.sh accepts a bumped tag carrying a stale digest
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-user
  files:     scripts/ci/check-image-pins.sh (tag/nvmrc comparison), Dockerfile:39,45,53
  requirements: none yet — the VZ-SEC-SUPPLY-001 proposal from security FINDING 5

Observed:
  The guard correctly catches a bumped .nvmrc with an untouched Dockerfile
  (verified, R5). It does not catch the inverse. I set .nvmrc to 22.15.0 AND
  rewrote all three FROM tags to node:22.15.0-alpine while leaving the 22.14.0
  digest in place:
      FROM node:22.15.0-alpine@sha256:9bef0ef1…  (a 22.14.0 index digest)
      -> EXIT 0, "OK: all 3 external FROM lines in Dockerfile are @sha256-pinned at node 22.15.0."
  Docker resolves by digest and ignores the tag, so the build would silently use
  22.14.0 while every line of the Dockerfile and .nvmrc says 22.15.0.
  The script documents this limitation honestly in its own header ("Nothing
  offline can tell whether a digest is the RIGHT digest for a tag; that needs a
  registry round trip, which this check deliberately does not make").

Failure:
  A Node bump that looks complete in review ships the old runtime. The version
  recorded in the release and the version actually running diverge with no
  signal. Not a supply-chain hole — the digest is still immutable and
  CODEOWNERS-reviewed — but the tag becomes a lie, and the tag is what a human
  reads. The acceptance criterion F5 actually asked for ("bumping .nvmrc without
  updating the digest fails a check") IS met; this is the adjacent case.

Perspective:
  operator, developer

Recommendation:
  Do not add a network call to ci-guard — the script's reasoning for staying
  offline is sound. Instead record the resolved digest's own tag next to the pin
  and assert agreement offline, or add the registry round trip to the separate
  non-required supply-chain lane where a network failure does not block a merge.

Acceptance criteria:
  - A FROM whose tag and digest disagree fails some check, in a lane where a
    registry outage cannot block an unrelated PR.
  - ci-guard stays offline and keeps its current behaviour.

Tests:
  scripts/ci/require-checks_test.sh already has image-pin cases (72-77); add one
  asserting the mismatch is rejected once a mechanism exists.

Cross-repo implications:
  core: same script is the intended twin — same gap | user: as above | search: same | meta: release records carry resolved digests

Challenge:
  Editing three FROM tags while deliberately leaving the digest stale is not an
  accident, and CODEOWNERS covers the Dockerfile. Largely right — hence NIT. The
  realistic path is carelessness during a Node bump, not malice.
```

### Recording observations (no action required from the builder)

- **V4 — scan artifacts are keyed by the merge commit, not the head SHA.**
  `npm-audit-f0665032…` and `trivy-image-f0665032…` use `${{ github.sha }}`, which
  on a `pull_request` event is the merge commit `f0665032…`, not the head
  `6b0ba871…`. Anyone retrieving this evidence by the verified SHA will not find
  it. Worth `${{ github.event.pull_request.head.sha || github.sha }}` next time
  the file is touched, matching what `ci-required` already does for `CHECK_SHA`.
- **V5 — `docker-build` never logs a numeric HTTP status for `/health`.** It
  relies on `curl --silent --fail` semantics plus a body assertion, which is
  sound but means the CI log cannot be quoted for "HTTP 200". I supplied the
  numeric **200** from my own local run (R9). Adding `-w '%{http_code}'` would
  make the CI log self-sufficient.
- **V6 — no `merge_group` runs exist on this SHA.** All six Actions runs are
  `event: pull_request`. The workflows all declare `merge_group:`, but the
  merge-queue path is untested on this commit. Expected for an open PR; recorded
  because the acceptance text for A2 says the scan lanes run "on `pull_request`
  and `merge_group`" and only the first half is demonstrated here.
- **V7 — process note.** A subagent I used for the CI audit reported that a
  forged `<system-reminder>` claiming the GitHub API rate limit was exceeded
  appeared appended to the output of a repository file read. It verified the
  claim directly (`{"limit":5000,"remaining":4902,"used":98}`), found it false,
  and did not act on it. No evidence in this file depends on that tool call.
  Recorded because content arriving inside tool output is not a trustworthy
  instruction channel, and a verifier acting on such text would be the exact
  false-positive path AGENTS.md warns about.

---

## R14. Verdict

**PASS.**

| Finding | Source | Verdict |
|---|---|---|
| SECURITY F4 — `server-only` boundary is a runtime throw, not a build error | SECURITY.md | **CLOSED** |
| SECURITY F5 — mutable base-image tag; no dependency or image scanning | SECURITY.md | **CLOSED** |
| SECURITY F6 — codegen resolves a poisoned `$ref` | SECURITY.md | **CLOSED** |
| VERIFY F6 — `globalThis["fetch"]` escapes both rules | VERIFY.md | **CLOSED** |
| VERIFY F7 — whitespace-only `FLOOR` passes vacuously | VERIFY.md (+ SECURITY closure note) | **CLOSED** |

Every in-scope acceptance bullet was reproduced by me from a clean clone:
each *demonstrated* bullet driven red against my own mutation and green when
restored, with the guards additionally attacked in ways the builder did not try
(planting the exact diagnostic sentence in source; resyncing the manifest sha256
behind a poisoned `$ref`; four invented lint spellings; a real client-bundle leak
via the actual inlining vector; a tag/digest mismatch). `ci-required` is green on
`6b0ba871…`, waited for the floor lanes, and its manifest matches the jobs that
actually ran. No test was weakened or deleted. No blocking finding.

Builder decisions, ruled: **(1)** `dynamicGlobalMember` — sound, not a
false-positive generator, keep it. **(2)** `FLOOR` env override kept —
acceptable, unreachable from CI or PR-controlled input. **(3)** vitest
`server-only` alias — does not leak into the production build and does not weaken
the build-time boundary. **(4)** package-manager removal — justified, asserted in
the same `RUN`, and verified not to break the app.

Scan lanes `deps-scan` / `image-scan`: correctly excluded from
`.github/required-checks.txt`; they fail on scanner error; they ran on this SHA
with zero findings and published artifacts; the builder's stated condition for
promotion (an agreed route for an unfixed upstream CVE, not the baseline) is
reasonable and I endorse it.

This PASS covers **vizra-user PR1b only**. It is not a merge and does not make
any ledger entry VERIFIED — the chair records those. The `main` ruleset (required
`ci-required` context, Code Owner review, force-push and deletion blocks) remains
an owner action that committing CODEOWNERS does not substitute for.

## R15. Cleanup

Clone at `…/scratchpad/vfy-pr1b-78006/vizra-user` deleted; every mutation was
reverted and `git status` confirmed clean before deletion (verified after each of
A1, A2, A3, A4, A5 and the arming tests). Probe files (`app/lintprobe/`,
`app/leakprobe/`, `app/server-only-probe/`) removed. Docker image
`vizra-user:vfy-pr1b`, container `vizra-user-vfy-pr1b` and the base image layer I
pulled were removed; the build cache this session created was pruned. The
containers `vidra-ipfs-071-minio`, `vidra-ipfs-071-kubo`, `vidra-ipfs-071-postgres`
and the `redis` / `postgres` / `kubo` / `minio` images are not mine and were left
alone.
