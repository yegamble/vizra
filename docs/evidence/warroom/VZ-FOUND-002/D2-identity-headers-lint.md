# D2 — a fetch that sends identity headers on a revalidated request fails lint

Acceptance: ADR-003 § SSR identity — "A lint rule forbids identity headers in revalidated fetches."

Repo: yegamble/vizra-user, branch `feat/m0-skeleton`. Host: darwin/arm64, node v22.14.0, eslint 10.11.0.
Rule: `vizra/no-identity-headers-in-cached-fetch` (eslint-rules/), configured as `error`.
Recorded 2026-09-20T17:45:13Z. Each mutation was applied, the commands run, then the file restored from a pre-mutation copy.

## Mutation A — weaken `viewerFetch` itself: keep forwarding the session cookie, but revalidate

```diff
--- /tmp/fetch.orig.ts	2026-09-20 13:44:53
+++ lib/api/fetch.ts	2026-09-20 13:44:53
@@ -197,7 +197,7 @@
       // NON-NEGOTIABLE: this request carries identity, so it must never be
       // cached or revalidated. The lint rule enforces the same thing for any
       // future call site.
-      cache: "no-store",
+      next: { revalidate: 60 },
       signal: timeoutSignal(options.timeoutMs, options.signal),
     });
     return await decode<T>(res);
```

### RED — `npm run lint` (exit )

```

> vizra-user@0.0.0 lint
> eslint


/Users/yosefgamble/github/vizra/vizra-user/lib/api/fetch.ts
  200:15  error  This fetch sends "cookie" and is cached or revalidated. A shared cache entry built from one viewer's credentials is served to other viewers (ADR-003). Use viewerFetch, or set cache: "no-store"  vizra/no-identity-headers-in-cached-fetch

✖ 1 problem (1 error, 0 warnings)

```

### RED — `npm run test` (exit ), defence in depth

```
⎯⎯⎯⎯⎯⎯⎯ Failed Tests 1 ⎯⎯⎯⎯⎯⎯⎯
 FAIL  lib/api/fetch.test.ts > viewerFetch > never caches, with no option to make it cache
AssertionError: expected undefined to be 'no-store' // Object.is equality
      Tests  1 failed | 49 passed (50)
```

### What this mutation first exposed (kept, because it is the point)

The first version of the rule read only object literals at the call site, so this
mutation produced **no** lint error: `viewerFetch` passes its headers by name.
The rule now resolves a headers identifier through scope and inspects both its
initializer and every `headers["cookie"] = …` write. Four RuleTester cases cover
it (`eslint-rules/no-identity-headers-in-cached-fetch.test.mjs`), and the run
above is against the strengthened rule.

## Mutation B — a page fetching vizra-core on its own, with a cookie, revalidated

```diff
--- /tmp/page.orig.tsx	2026-09-20 13:44:53
+++ app/page.tsx	2026-09-20 13:44:55
@@ -5,7 +5,13 @@
  * The first real page (Search) lands in a later PR and replaces this. It shows
  * nothing that could be mistaken for a working feature, and it invents no data.
  */
-export default function Home() {
+export default async function Home() {
+  const res = await fetch("http://api:8080/api/v1/me", {
+    headers: { cookie: "__Host-vizra_session=abc" },
+    next: { revalidate: 60 },
+  });
+  void res;
+
   return (
     <main>
       <h1>Vizra</h1>
```

### RED — `npm run lint` (exit )

```

> vizra-user@0.0.0 lint
> eslint


/Users/yosefgamble/github/vizra/vizra-user/app/page.tsx
   9:21  error  Call publicFetch or viewerFetch from lib/api/fetch.ts instead of global fetch: they carry the identity, cache and CSRF rules of ADR-003, and keep pages from inventing their own data source      vizra/no-raw-fetch
  11:13  error  This fetch sends "cookie" and is cached or revalidated. A shared cache entry built from one viewer's credentials is served to other viewers (ADR-003). Use viewerFetch, or set cache: "no-store"  vizra/no-identity-headers-in-cached-fetch

✖ 2 problems (2 errors, 0 warnings)

```

Two rules fire: `vizra/no-raw-fetch` (a page may not call global fetch at all)
and `vizra/no-identity-headers-in-cached-fetch` (the cookie on a revalidated read).

## GREEN — both files restored

- `npm run lint` → exit  (no output)
- `npm run test` → exit  (Tests  50 passed (50))

Unit coverage of the rules themselves: `eslint-rules/*.test.mjs`, run by vitest as part of `npm run ci`.
