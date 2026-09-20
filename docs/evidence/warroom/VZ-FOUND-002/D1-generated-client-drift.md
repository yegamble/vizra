# D1 — a hand-edited generated client fails the drift check

Acceptance: VZ-FOUND-002 negative case — "Hand-edited generated file is rejected by a drift check".

Repo: yegamble/vizra-user, branch `feat/m0-skeleton`. Host: darwin/arm64, node v22.14.0, npm 10.9.2.
Vendored contract: yegamble/vizra-core@b0dbeb6dc27294fe793492ea60bc18b6aed4b042 `api/openapi.yaml` (sha256 128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d).
Recorded 2026-09-20T17:43:12Z. Each mutation was applied, the commands below were run, then the file was restored from a pre-mutation copy.

## Mutation A — one enum member added by hand to `lib/api/generated.ts`

```diff
--- /tmp/generated.orig.ts	2026-09-20 13:43:09
+++ lib/api/generated.ts	2026-09-20 13:43:09
@@ -114,7 +114,7 @@
              * @description `ok` while serving; `draining` after SIGTERM.
              * @enum {string}
              */
-            status: "ok" | "draining";
+            status: "ok" | "draining" | "fine";
         };
         /**
          * @description `off` means the component is deliberately not configured (for example
```

### RED — `npm run check:contract` (exit 1)

```

> vizra-user@0.0.0 check:contract
> node scripts/check-contract.mjs

✨ openapi-typescript 7.13.0
🚀 /Users/yosefgamble/github/vizra/vizra-user/contracts/vizra-core/api/openapi.yaml → /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/vizra-contract-oEsNhn/generated.ts [20.4ms]

❌ lib/api/generated.ts is not what the contract generates.
   first difference at line 117:
     committed: "            status: \"ok\" | \"draining\" | \"fine\";"
     generated: "            status: \"ok\" | \"draining\";"
   (356 committed lines vs 356 generated)
   
   lib/api/generated.ts is generated, never hand-edited (AGENTS.md).
   Run `npm run codegen` and commit the result — or, if the API changed,
   re-vendor the contract from vizra-core first.

```

### Why this check has to exist: no other lane catches it

With mutation A still in place:

- `npm run typecheck` → exit 0
- `npm run test` → exit 0 (Tests  44 passed (44))

A widened union is valid TypeScript and breaks no test, so only the byte-for-byte
drift check notices that the committed client no longer describes the contract
(ADR-002 § Contracts).

## Mutation B — editing the vendored contract here instead of in vizra-core

```diff
--- /tmp/spec.orig.yaml	2026-09-20 13:43:09
+++ contracts/vizra-core/api/openapi.yaml	2026-09-20 13:43:11
@@ -19,7 +19,7 @@
     Public HTTP API of `vizra-core`. In M0 this contract carries only the four
     operational probes; product surfaces arrive with their own slices and are
     added here before they are implemented.
-  version: 0.1.0
+  version: 0.9.9
   license:
     name: See LICENSE in the vizra-core repository
   contact:
```

### RED — `npm run check:contract` (exit 1)

```

> vizra-user@0.0.0 check:contract
> node scripts/check-contract.mjs


❌ contracts/vizra-core/api/openapi.yaml does not match its manifest.
   manifest: 128d0509238a8eb66e9847efd6bf90c4d52d2fb4c2d80b6fed88dbc3a0c8e04d
   on disk:  0d3d726b6068a9431f72b6aeb73d9b627726bfe14f210327b122822790c93ee4
   The contract is vizra-core's to change. Re-vendor it with scripts/vendor-contract.mjs;
   do not edit the vendored copy here.
✨ openapi-typescript 7.13.0
🚀 /Users/yosefgamble/github/vizra/vizra-user/contracts/vizra-core/api/openapi.yaml → /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/vizra-contract-LZO0dI/generated.ts [21ms]

```

## GREEN — both files restored, `npm run check:contract` (exit 0)

```

> vizra-user@0.0.0 check:contract
> node scripts/check-contract.mjs

✨ openapi-typescript 7.13.0
🚀 /Users/yosefgamble/github/vizra/vizra-user/contracts/vizra-core/api/openapi.yaml → /var/folders/f0/7491x4mn6r90h50q54n7bs440000gn/T/vizra-contract-O9IYCq/generated.ts [21.1ms]
✅ contract: contracts/vizra-core/api/openapi.yaml matches its manifest (sha256 128d0509238a…),
   and lib/api/generated.ts is exactly what openapi-typescript 7.13.0 generates from it.
   source: yegamble/vizra-core@b0dbeb6dc27294fe793492ea60bc18b6aed4b042 :api/openapi.yaml
```

Restoration of the client is equally reproducible with `npm run codegen`.
The `contract` CI lane runs the same command and then `git diff --exit-code`,
proving the check compares rather than repairs.
