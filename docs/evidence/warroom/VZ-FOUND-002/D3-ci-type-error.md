# D3 — `npm run ci` fails on a type error

Acceptance: slice item "npm run ci = lint, typecheck, test, build", demonstrated red then green.

Repo: yegamble/vizra-user, branch `feat/m0-skeleton`. Host: darwin/arm64, node v22.14.0, npm 10.9.2, TypeScript 5.9.3.
`npm run ci` = `npm run lint && npm run typecheck && npm run test && npm run build`.
Recorded 2026-09-20T17:45:32Z.

## Controlled mutation — a value outside the declared union

```diff
--- /tmp/health.orig.ts	2026-09-20 13:45:24
+++ lib/health.ts	2026-09-20 13:45:24
@@ -18,5 +18,5 @@
 };
 
 export function healthPayload(): HealthPayload {
-  return { status: "ok", service: "vizra-user", scope: "liveness" };
+  return { status: "okay", service: "vizra-user", scope: "liveness" };
 }
```

## RED — `npm run ci` (exit 2)

```

> vizra-user@0.0.0 ci
> npm run lint && npm run typecheck && npm run test && npm run build


> vizra-user@0.0.0 lint
> eslint


> vizra-user@0.0.0 typecheck
> tsc --noEmit

lib/health.ts(21,12): error TS2322: Type '"okay"' is not assignable to type '"ok"'.
```

## GREEN — restored, `npm run ci` (exit 0)

```

> vizra-user@0.0.0 ci
> npm run lint && npm run typecheck && npm run test && npm run build


> vizra-user@0.0.0 lint
> eslint


> vizra-user@0.0.0 typecheck
> tsc --noEmit


> vizra-user@0.0.0 test
> vitest run


 RUN  v5.0.1 /Users/yosefgamble/github/vizra/vizra-user


 Test Files  5 passed (5)
      Tests  50 passed (50)
   Start at  13:45:29
   Duration  295ms (transform 35%, import 32%, tests 30%, worker 3%)


> vizra-user@0.0.0 build
> next build

▲ Next.js 16.3.5 (Turbopack)
✓ Running next.config.ts took 71ms

  Creating an optimized production build ...
✓ Compiled successfully in 557ms
  Running TypeScript ...
  Finished TypeScript in 691ms ...
  Collecting page data using 5 workers ...
  Generating static pages using 5 workers (0/3) ...
✓ Generating static pages using 5 workers (3/3) in 215ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
├ ○ /_not-found
└ ƒ /health


○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand

```
