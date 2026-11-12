# Execution plan: VZ-FOUND-002 (user half, queue 3b) — re-vendor the vizra-core contract and pin the expected operation set

## Context
Repo yegamble/vizra-user, worktree `.claude/worktrees/user-3b`, branch `fix/revendor-core-contract` from origin/main 33633d4. PR https://github.com/yegamble/vizra-user/pull/12. Head at the time of the transcripts: a3b8f942d566513b155971384bd2ee6b161d4520.
Reproduced hole: the vendored `contracts/vizra-core/api/openapi.yaml` (core 415a6d1) had 4 operations; core main 5f615d7 has 6.

## Acceptance
| Case | Statement | State after this PR |
|---|---|---|
| S1 (success) | Adding a route without spec fails; spec without route fails | **Stays open — not this PR.** It is a vizra-core check (queue 3a, in flight); nothing in vizra-user can observe core's routes. |
| S2 (success) | Generated client diff is empty after regeneration | **Hole closed by this PR.** It held before only against a vendored contract with 4 of core's 6 operations. Now vendored from core `main` `5f615d74e840b23d2201b1d78dd89abfef07701b` (6 operations), client regenerated, and `lib/api/contract-operations.test.ts` fails if the vendored spec or the generated client does not carry exactly the six expected operations. Residual gap: freshness against core `main` is still not checked by any CI (see below). |
| N1 (negative) | Hand-edited generated file is rejected by a drift check | **Held before, unchanged.** Re-demonstrated on this head: a one-line hand edit of `lib/api/generated.ts` makes `npm run check:contract` exit 1 (lane `contract`). |

Non-goals: no product code or UI calls the new operations; no request is sent to `claim-owner` (it carries a credential); no e2e; no dependency change; no new workflow.

## Implementation
- `contracts/vizra-core/api/openapi.yaml`, `contracts/manifest.json`, `lib/api/generated.ts`: written by `node scripts/vendor-contract.mjs --from <vizra-core checkout> --ref main` (core HEAD = main = origin/main = 5f615d74e840b23d2201b1d78dd89abfef07701b). Nothing hand-edited. Recorded SHA: `contracts/manifest.json` `spec.source_commit` (blob 8bab7e9d518511a1cae864459f1ff8e177ccb3b1, sha256 2ac32800…c1d6, 18521 bytes).
- `lib/api/contract-operations.test.ts` (new, runs in the `frontend` lane through vitest and tsc): explicit list of six operations; asserts the vendored spec's method+path+operationId set equals it, the generated `paths` bindings equal it, the generated `operations` ids equal it, and the same at type level.

Six operations: GET /healthz getHealthz; GET /readyz getReadyz; GET /version getVersion; GET /schemaz getSchemaz; GET /api/v1/setup/claim-status getSetupClaimStatus; POST /api/v1/setup/claim-owner claimOwner.

## Verification
Environment: macOS arm64, node v24.21.0 (`.nvmrc` says 22.14.0, which is not installed on this machine; CI uses the pinned version). All through `.claude/council/quiet.sh`.

| Command | Exit | Result |
|---|---|---|
| npm ci | 0 | |
| npm run lint | 0 | |
| npx tsc --noEmit | 0 | |
| npx vitest run | 0 | 23 files, 818 tests passed, 0 skipped |
| npm run check:contract | 0 | source 5f615d7 |
| npm run check:hygiene | 0 | 324 sources |
| npm run build | 0 | built locally |

## Progress and evidence
### (a) new test RED on the 4-operation contract (base tree + test only)
```
$ npx vitest run lib/api/contract-operations.test.ts
 RUN  v5.0.1 /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b
 ❯ lib/api/contract-operations.test.ts (4 tests | 3 failed) 17ms
   ❯ the vendored contract carries the operations the product expects (4)
     × vendored spec operation set equals the expected list 15ms
     × generated client exposes exactly the expected operations 1ms
     × generated client declares exactly the expected operation ids 1ms
     ✓ type-level checks are in force 0ms
⎯⎯⎯⎯⎯⎯⎯ Failed Tests 3 ⎯⎯⎯⎯⎯⎯⎯
 FAIL  lib/api/contract-operations.test.ts > the vendored contract carries the operations the product expects > vendored spec operation set equals the expected list
AssertionError: expected [ 'GET /healthz getHealthz', …(3) ] to deeply equal [ …(6) ]
- Expected
+ Received
  [
-   "GET /api/v1/setup/claim-status getSetupClaimStatus",
    "GET /healthz getHealthz",
    "GET /readyz getReadyz",
    "GET /schemaz getSchemaz",
    "GET /version getVersion",
-   "POST /api/v1/setup/claim-owner claimOwner",
  ]
 ❯ lib/api/contract-operations.test.ts:105:41
    103|
    104|   it("vendored spec operation set equals the expected list", () => {
    105|     expect(vendoredOperations().sort()).toEqual(expected);
       |                                         ^
    106|   });
    107|
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/3]⎯
 FAIL  lib/api/contract-operations.test.ts > the vendored contract carries the operations the product expects > generated client exposes exactly the expected operations
AssertionError: expected [ 'GET /healthz getHealthz', …(3) ] to deeply equal [ …(6) ]
- Expected
+ Received
  [
-   "GET /api/v1/setup/claim-status getSetupClaimStatus",
    "GET /healthz getHealthz",
    "GET /readyz getReadyz",
    "GET /schemaz getSchemaz",
    "GET /version getVersion",
-   "POST /api/v1/setup/claim-owner claimOwner",
  ]
 ❯ lib/api/contract-operations.test.ts:109:42
    107|
    108|   it("generated client exposes exactly the expected operations", () =>…
    109|     expect(generatedOperations().sort()).toEqual(expected);
       |                                          ^
    110|   });
    111|
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[2/3]⎯
 FAIL  lib/api/contract-operations.test.ts > the vendored contract carries the operations the product expects > generated client declares exactly the expected operation ids
AssertionError: expected [ 'getHealthz', 'getReadyz', …(2) ] to deeply equal [ 'claimOwner', 'getHealthz', …(4) ]
- Expected
+ Received
  [
-   "claimOwner",
    "getHealthz",
    "getReadyz",
    "getSchemaz",
-   "getSetupClaimStatus",
    "getVersion",
  ]
 ❯ lib/api/contract-operations.test.ts:116:22
    114|     const body = source.slice(source.indexOf("export interface operati…
    115|     const declared = [...body.matchAll(/^ {4}(\w+): \{$/gm)].map((matc…
    116|     expect(declared).toEqual(EXPECTED_OPERATIONS.map((o) => o.operatio…
       |                      ^
    117|   });
    118|
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[3/3]⎯
 Test Files  1 failed (1)
      Tests  3 failed | 1 passed (4)
   Start at  11:43:35
   Duration  128ms (tests 34%, import 32%, transform 30%, worker 4%)
exit 1
```
```
$ npx tsc --noEmit
lib/api/contract-operations.test.ts(47,7): error TS2322: Type 'true' is not assignable to type 'false'.
lib/api/contract-operations.test.ts(48,7): error TS2322: Type 'true' is not assignable to type 'false'.
lib/api/contract-operations.test.ts(60,3): error TS2322: Type 'true' is not assignable to type 'false'.
lib/api/contract-operations.test.ts(61,3): error TS2322: Type 'true' is not assignable to type 'false'.
exit 2
```
### vendor run
```
$ node scripts/vendor-contract.mjs --from /Users/yosefgamble/github/vizra/vizra-core --ref main
✨ openapi-typescript 7.13.0
🚀 /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b/contracts/vizra-core/api/openapi.yaml → /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b/lib/api/generated.ts [22.8ms]
vendor-contract: yegamble/vizra-core@main (5f615d74e840b23d2201b1d78dd89abfef07701b)
              :api/openapi.yaml -> /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b/contracts/vizra-core/api/openapi.yaml
            blob: 8bab7e9d518511a1cae864459f1ff8e177ccb3b1
          sha256: 2ac3280056871c48477b0238a398dc23afbd3afec5ff0ad170b27c5cc373c1d6
           bytes: 18521
       generated: /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b/lib/api/generated.ts
exit 0
```
### (a) GREEN after the re-vendor
```
$ npx vitest run lib/api/contract-operations.test.ts
 RUN  v5.0.1 /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b
 ✓ lib/api/contract-operations.test.ts (4 tests) 19ms
 Test Files  1 passed (1)
      Tests  4 passed (4)
   Start at  11:43:38
   Duration  129ms (import 40%, tests 31%, transform 25%, worker 3%)
exit 0
```
```
$ npx tsc --noEmit
exit 0
```
### (b) mutation: `/api/v1/setup/claim-owner` deleted from the vendored spec (lines 189-272), client not regenerated
```
$ npm run check:contract
> vizra-user@0.0.0 check:contract
> node scripts/check-contract.mjs
❌ contracts/vizra-core/api/openapi.yaml is not the blob the manifest names.
   manifest: 8bab7e9d518511a1cae864459f1ff8e177ccb3b1
   on disk:  a6c8339323f19e2f9d55f41029d9bbc7b7a938e4
   Compare with: git -C ../vizra-core rev-parse <source_commit>:api/openapi.yaml
❌ contracts/vizra-core/api/openapi.yaml does not match its manifest.
   manifest: 2ac3280056871c48477b0238a398dc23afbd3afec5ff0ad170b27c5cc373c1d6
   on disk:  fc8fadae51a5e4918d970e4356a3829776289f40263f04fae6976f2cb73e0dbe
   The contract is vizra-core's to change. Re-vendor it with scripts/vendor-contract.mjs;
   do not edit the vendored copy here.
❌ contracts/vizra-core/api/openapi.yaml is 15147 bytes; the manifest says 18521.
   Re-vendor rather than adjusting the number.
✨ openapi-typescript 7.13.0
🚀 /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b/contracts/vizra-core/api/openapi.yaml → /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/vizra-contract-AH4XgE/generated.ts [22.4ms]
❌ lib/api/generated.ts is not what the contract generates.
   first difference at line 134:
     committed: "    \"/api/v1/setup/claim-owner\": {"
     generated: "}"
   (594 committed lines vs 466 generated)
   
   lib/api/generated.ts is generated, never hand-edited (AGENTS.md).
   Run `npm run codegen` and commit the result — or, if the API changed,
   re-vendor the contract from vizra-core first.
exit 1
```
```
$ npx vitest run lib/api/contract-operations.test.ts
 RUN  v5.0.1 /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b
 ❯ lib/api/contract-operations.test.ts (4 tests | 1 failed) 17ms
   ❯ the vendored contract carries the operations the product expects (4)
     × vendored spec operation set equals the expected list 15ms
     ✓ generated client exposes exactly the expected operations 1ms
     ✓ generated client declares exactly the expected operation ids 0ms
     ✓ type-level checks are in force 0ms
⎯⎯⎯⎯⎯⎯⎯ Failed Tests 1 ⎯⎯⎯⎯⎯⎯⎯
 FAIL  lib/api/contract-operations.test.ts > the vendored contract carries the operations the product expects > vendored spec operation set equals the expected list
AssertionError: expected [ …(5) ] to deeply equal [ …(6) ]
- Expected
+ Received
@@ -2,7 +2,6 @@
    "GET /api/v1/setup/claim-status getSetupClaimStatus",
    "GET /healthz getHealthz",
    "GET /readyz getReadyz",
    "GET /schemaz getSchemaz",
    "GET /version getVersion",
-   "POST /api/v1/setup/claim-owner claimOwner",
  ]
 ❯ lib/api/contract-operations.test.ts:105:41
    103|
    104|   it("vendored spec operation set equals the expected list", () => {
    105|     expect(vendoredOperations().sort()).toEqual(expected);
       |                                         ^
    106|   });
    107|
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/1]⎯
 Test Files  1 failed (1)
      Tests  1 failed | 3 passed (4)
   Start at  11:43:55
   Duration  149ms (tests 34%, import 33%, transform 29%, worker 4%)
exit 1
```
Restored from a byte copy; `git status --short` empty.
### (c) mutation: one line of `lib/api/generated.ts` hand-edited (`post: operations["claimOwner"]; // hand edit`)
```
$ npm run check:contract
> vizra-user@0.0.0 check:contract
> node scripts/check-contract.mjs
✨ openapi-typescript 7.13.0
🚀 /Users/yosefgamble/github/vizra/.claude/worktrees/user-3b/contracts/vizra-core/api/openapi.yaml → /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/vizra-contract-PGPa3P/generated.ts [26.6ms]
❌ lib/api/generated.ts is not what the contract generates.
   first difference at line 165:
     committed: "        post: operations[\"claimOwner\"]; // hand edit"
     generated: "        post: operations[\"claimOwner\"];"
   (594 committed lines vs 594 generated)
   
   lib/api/generated.ts is generated, never hand-edited (AGENTS.md).
   Run `npm run codegen` and commit the result — or, if the API changed,
   re-vendor the contract from vizra-core first.
exit 1
```
Restored with `git checkout lib/api/generated.ts`; `git status --short` empty.

## Blockers and handoff
- Freshness against core `main` is not checked anywhere. vizra-user CI cannot read the private vizra-core (vizra-user AGENTS.md, "Owed — STALENESS IS NOT DETECTED HERE"; needs an owner-provided read-only token). The meta repo's workflows and `scripts/` were searched for a check comparing `contracts/manifest.json` `source_commit` with core's pin: none found. The new test pins the operation set the product expects, so it catches a vendor that lacks an expected operation, not a core that has moved on.
- The expected list must be updated in the same change as any later re-vendor that adds or removes an operation. vizra-user `AGENTS.md` does not say this yet (not edited here by instruction): follow-up.
- State: READY_FOR_REVIEW. Not verified, not merged.
