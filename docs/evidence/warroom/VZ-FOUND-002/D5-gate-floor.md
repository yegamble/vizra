# D5 — the merge gate can no longer be redefined by the pull request it gates

Fix round 1. Security Finding 2: `scripts/ci/require-checks.sh` reads the manifest
from the checkout under test, and nothing asserted that the lanes that matter were
still IN it. Deleting one line merged green with lint, typecheck, vitest and the
production build never having had to pass.

Repo: yegamble/vizra-user, branch `feat/m0-skeleton`. Recorded 2026-09-20T18:22:16Z.

## Mutation 1 — delete the `frontend` line

```diff
@@ -19,7 +19,6 @@
 
 # frontend-ci.yml — the canonical `npm run ci` gate: lint (including the
 # ADR-003 identity/caching rules), typecheck, vitest, production build.
-frontend
 
 # contract-ci.yml — the vendored vizra-core contract matches its manifest, and
 # lib/api/generated.ts is byte-for-byte what the pinned generator produces from
```

### RED — `bash scripts/ci/check-required-floor.sh` exit 1

```
::error::required-checks.txt no longer requires the floor this repository merges on:
  frontend: missing. It is not listed, so `ci-required` would not wait for it.
  The floor is defined in scripts/ci/check-required-floor.sh and is owner-reviewed (.github/CODEOWNERS).
  If a floor lane is genuinely being retired, change the floor and the manifest in the same, reviewed diff.
```

### The contrast that makes this finding real — the guard that already existed, on the same mutation

`bash scripts/ci/check-required-manifest.sh` exit 0:

```
OK: all 3 entries in .github/required-checks.txt map to a defined job.
```

It was asked whether the names present are real jobs, never whether the names that
matter are present. It said OK to a manifest with no `frontend` lane in it.

## Mutation 2 — demote it to `?frontend` (optional-if-absent)

```diff
@@ -19,7 +19,7 @@
 
 # frontend-ci.yml — the canonical `npm run ci` gate: lint (including the
 # ADR-003 identity/caching rules), typecheck, vitest, production build.
-frontend
+?frontend
 
 # contract-ci.yml — the vendored vizra-core contract matches its manifest, and
 # lib/api/generated.ts is byte-for-byte what the pinned generator produces from
```

### RED — floor guard exit 1

```
::error::required-checks.txt no longer requires the floor this repository merges on:
  frontend: marked optional (`?frontend`). An optional lane passes when it never runs, so this is a removal with extra steps.
  The floor is defined in scripts/ci/check-required-floor.sh and is owner-reviewed (.github/CODEOWNERS).
  If a floor lane is genuinely being retired, change the floor and the manifest in the same, reviewed diff.
```

Pre-existing manifest guard on this mutation: exit 0 (`OK: all 4 entries in .github/required-checks.txt map to a defined job.`). An optional lane passes
when it never runs, so demotion is deletion with extra steps — which is why the floor
guard reports it separately rather than treating presence as enough.

## GREEN — manifest restored

```
OK: .github/required-checks.txt still requires the floor: frontend contract.
```

exit 0.

## Regression cases, so this cannot silently rot

`bash scripts/ci/require-checks_test.sh` exit 0 — **require-checks_test: 55 cases, 62 assertions, 0 failed**.
Ten of those cases are new and drive the floor guard directly: the valid manifest, the
two mutations above for each floor lane, a commented-out lane, a floor name that
appears only inside another line’s comment, a near-miss name (`frontend-ci`), an empty
manifest, and the repository’s own committed manifest.

One of those new cases found a bug in the harness itself while being written:
`if ! cmd; then rc=$?` reads `$?` as the status of the NEGATION, so every failing case
was recording exit 0 — a suite that would have passed while testing nothing. It is
`|| rc=$?` now, with a comment saying why.

## The other half, which is not in this PR

`.github/CODEOWNERS` is committed (covering `/.github/`, `/scripts/ci/`,
`/eslint-rules/`, `/contracts/`). GitHub enforces it only once a ruleset on `main`
requires Code Owner review, and applying that ruleset is an owner action (ADR-002
items 9–10). The floor guard deliberately needs no repository setting at all.
