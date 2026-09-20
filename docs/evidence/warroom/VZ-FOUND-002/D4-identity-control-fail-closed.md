# D4 — the identity/caching lint control, after being made fail-closed

Fix round 1. Security Finding 1 and verifier Finding 1: two reviewers independently
defeated the first version of this control. The fix is structural — the rule reports
what it cannot read, aliasing `fetch` is banned in every file including the
allow-listed one, and the runtime property is asserted by test rather than inferred
from syntax.

Repo: yegamble/vizra-user, branch `feat/m0-skeleton`. Host: darwin/arm64, node v22.14.0, eslint 10.11.0.
Recorded 2026-09-20T18:21:44Z. Every mutation was applied, the commands run, then the file restored from a pre-mutation copy.

## A — weaken `viewerFetch`, INLINE spelling (the mutation the old rule already caught)

```diff
@@ -237,7 +237,7 @@
       // NON-NEGOTIABLE: this request carries identity, so it must never be
       // cached or revalidated. The lint rule enforces the same thing for any
       // future call site.
-      cache: "no-store",
+      next: { revalidate: 60 },
       signal: boundedSignal(options.timeoutMs, options.signal),
     });
     return await decode<T>(res);
```

### RED — `npm run ci` exit 1

```
  240:15  error  This fetch sends "cookie" and is cached or revalidated. A shared cache entry built from one viewer's credentials is served to other viewers (ADR-003). Use viewerFetch, or set cache: "no-store"  vizra/no-identity-headers-in-cached-fetch
✖ 1 problem (1 error, 0 warnings)
```

## B — the SAME weakening, with the init hoisted into a variable

This spelling produced **zero lint errors** before this round: one line of refactoring,
in the one file where `no-raw-fetch` is allow-listed off, and the only lint control
protecting `viewerFetch` went silent.

```diff
@@ -230,16 +230,14 @@
   if (options.uploadIntent) headers["x-vizra-upload"] = "1";
 
   try {
-    const res = await fetch(target, {
+    const init: RequestInit & { next?: { revalidate: number } } = {
       method,
       headers,
       body: options.json === undefined ? undefined : JSON.stringify(options.json),
-      // NON-NEGOTIABLE: this request carries identity, so it must never be
-      // cached or revalidated. The lint rule enforces the same thing for any
-      // future call site.
-      cache: "no-store",
+      next: { revalidate: 60 },
       signal: boundedSignal(options.timeoutMs, options.signal),
-    });
+    };
+    const res = await fetch(target, init);
     return await decode<T>(res);
   } catch (error) {
     return failed<T>(error);
```

### RED — `npm run ci` exit 1

```
  240:37  error  This rule cannot read this fetch, so it cannot prove the request carries no identity on a cached read — and it fails closed (ADR-003). Write the init and its headers as object literals at the call site, or call publicFetch / viewerFetch from lib/api/fetch.ts  vizra/no-identity-headers-in-cached-fetch
✖ 1 problem (1 error, 0 warnings)
```

### RED — and the runtime test catches it independently of lint: `npm run test` exit 1

```
⎯⎯⎯⎯⎯⎯ Failed Tests 31 ⎯⎯⎯⎯⎯⎯⎯
AssertionError: expected undefined to be 'no-store' // Object.is equality
AssertionError: expected undefined to be 'no-store' // Object.is equality
      Tests  31 failed | 85 passed (116)
```

Thirty-one failures, from the table-driven assertion over method x json x uploadIntent
plus the `cookies()` cases. That layer does not care how the init is spelled — which is
the point of adding it, because the syntactic rule was defeated twice.

## C — `const alias = fetch; alias(url, …)` in a page

A reviewer showed this escaping BOTH rules: not a call whose callee is `fetch`, so
`no-raw-fetch` stayed silent, and not a recognised fetch, so the identity rule never
looked. A session cookie could ride a revalidated request with a clean lint run.

```diff
@@ -5,7 +5,14 @@
  * The first real page (Search) lands in a later PR and replaces this. It shows
  * nothing that could be mistaken for a working feature, and it invents no data.
  */
-export default function Home() {
+export default async function Home() {
+  const alias = fetch;
+  const res = await alias("http://api:8080/api/v1/me", {
+    headers: { cookie: "__Host-vizra_session=abc" },
+    next: { revalidate: 60 },
+  });
+  void res;
+
   return (
     <main>
       <h1>Vizra</h1>
```

### RED — `npm run lint` exit 1

```
  9:17  error  Do not bind global fetch to another name. An aliased fetch is invisible to the identity/caching lint rule, so a session cookie could ride a revalidated request with a clean lint run (ADR-003). Call it directly inside lib/api/fetch.ts, or use publicFetch / viewerFetch  vizra/no-raw-fetch
✖ 1 problem (1 error, 0 warnings)
```

## D — `fetch(url, opts)` where `opts` is not a literal

```diff
@@ -5,7 +5,11 @@
  * The first real page (Search) lands in a later PR and replaces this. It shows
  * nothing that could be mistaken for a working feature, and it invents no data.
  */
-export default function Home() {
+export default async function Home() {
+  const opts = { headers: { cookie: "x" }, next: { revalidate: 60 } };
+  const res = await fetch("http://api:8080/api/v1/me", opts);
+  void res;
+
   return (
     <main>
       <h1>Vizra</h1>
```

### RED — `npm run lint` exit 1 (both rules fire)

```
  10:21  error  Call publicFetch or viewerFetch from lib/api/fetch.ts instead of global fetch: they carry the identity, cache and CSRF rules of ADR-003, and keep pages from inventing their own data source                                                                        vizra/no-raw-fetch
  10:56  error  This rule cannot read this fetch, so it cannot prove the request carries no identity on a cached read — and it fails closed (ADR-003). Write the init and its headers as object literals at the call site, or call publicFetch / viewerFetch from lib/api/fetch.ts  vizra/no-identity-headers-in-cached-fetch
✖ 2 problems (2 errors, 0 warnings)
```

## E — bare `fetch(url)` in the allowed file is still accepted

A temporary `export async function probeBareFetch(target: string) { return fetch(target); }`
in `lib/api/fetch.ts`: `npm run lint` exit **0**, no output. Failing closed is about an
init the rule cannot read, never an absent one — so the rule adds no false positive here.

## GREEN — everything restored

`npm run ci` exit 0 — Tests  116 passed (116).

Rule unit coverage: `eslint-rules/*.test.mjs`, 59 RuleTester cases, including every
bypass both reviewers reported (headers from a call, `new Headers().set()`, a wrapper
parameter, an aliased fetch, a hoisted init, spread options, a second headers alias,
a computed key, `Object.assign`) — each as an `unreadable` or `aliasedFetch` error.
