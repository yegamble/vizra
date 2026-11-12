# VERIFY vizra-user PR #18 — QUEUE-2f default-deny e2e artifact allowlist (VZ-FOUND-008)

- SHA: `edb70a1fcb2290c636337db46da8d6e119cfab90` (PR head at start and end; branch feat/e2e-artifact-allowlist)
- Clone: fresh `git clone` in `/tmp/vzv-user-pr18-kDpXAl` (deleted at end). Node v24.21.0, darwin arm64.
- Verifier: independent (did not write this code). Verdict 1 of 4 for VZ-FOUND-008.

## Commands and results (my clone, at the SHA)
| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | |
| `bash scripts/ci/require-checks_test.sh` | 0 | 235 cases, 242 assertions, 0 failed |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | OK |
| `npm run check:hygiene` | 0 | 357 sources clean, 17 digest lines match |
| `npm run lint` / `npm run typecheck` | 0 / 0 | |
| `npm run test` | 0 | 29 files, 917/917 passed, 0 skipped |
| `npx playwright test --list` | 0 | Total: 42 tests in 5 files = 21 per project = new floor (required-projects.json 9→21) |
| `npm run e2e:demos` | NOT RUN | time budget; optional per brief |

## CI on the SHA (`gh run view`)
ci-required 43274430718, e2e 43274430803, ci-guard 43274430611: headSha = edb70a1…, conclusion success. Also green: contract, frontend, deps-scan, image-scan. `.github/required-checks.txt` = frontend, contract, ?guard, ?docker-build, e2e; required lanes all ran and passed. `docker-build` is optional (`?`) and was not in this PR's check list. Accepted under the manifest's optional semantics.

## Demonstrations
1. **No-op guard (cases 179/180/182).** I changed the case-179 anchor to `ARTIFACT-NOMATCH/`, and the suite went red: `not ok 179 … the mutation is a no-op (its anchor no longer matches …e2e.yml)`, 1 failed, rc=1. Restored it and the suite went green. CONFIRMED.
2. **My own e2e.yml mutations through `check-e2e-lane.sh`. All rc=1, each with a named reason:**
   - m1: upload `test-results/` directly → upload step differs from the pin.
   - m2: add `playwright-report/` → "not on the allowlist" + pin mismatch.
   - m3: second `upload-artifact` step, `if: always()`, path test-results/, with no redact step → "not byte-equal to the pinned upload step".
   - m4: `if: always()` on the upload → pin mismatch.
   - m5: `continue-on-error` on the redact/gate step → "`continue-on-error` not in the pin".
   - m6: `continue-on-error` on the upload → pin mismatch.
   - m7: step `env: VZ_ARTIFACT_STAGE: test-results` (point staging at the raw tree) → "may set no environment" + pin mismatch.
   - m8: same variable at job env → "Env at this scope is DEFAULT-DENY".
   - m9: a `cp -r test-results artifact-upload/raw` step before redact → refused (mentions an artifact directory, not pinned).
3. **Fixture through the shipped path** (`bash scripts/ci/redact-artifacts.sh test-results playwright-report` from repo root). Fixture contents:
   - error-context.md holding a bearer token, a Set-Cookie and an X-Amz-Signature URL.
   - trace.zip holding Cookie/Set-Cookie headers, a signed URL and call params.
   - playwright-report/index.html holding a base64 template.
   - results.json whose error carries a bearer token, a signed URL and set-cookie.
   - png and webm files with the right magic bytes followed by planted text.

   Result: exit 0. REFUSED: error-context.md (not-staged), trace.zip (not-staged), index.html (not-staged), results.json (header-value, bearer-token). `artifact-upload/` = SUMMARY.txt, test-failed-1.png, video.webm. SUMMARY.txt: `got Bearer <redacted> at https://b.s3.amazonaws.com/k.jpg?<redacted> set-cookie (value redacted)`. **No token, cookie or trace reached artifact-upload/.** The exception is the crafted bytes after the magic in png/webm (`video.webm: …?X-Amz-Signature=WEBMSENTINEL`); see F-2.
4. **Typed-value probe.** results.json error `Received: "CorrectHorse!PWSENTINEL"`, exit 0. The value is uploaded verbatim in BOTH `artifact-upload/playwright-report/results.json` and `SUMMARY.txt`. See F-1.

## Diff audit
- No assertion removed or weakened. The only changes are lane-checker/test retargets from `test-results/` to `artifact-upload/`, plus the new no-op guard.
- demonstrate.sh derives counts from required-projects.json and `find e2e/specs`. No hard-coded 9/18/20 remain.
- No spec authenticates or fills credentials: `grep -rniE 'password|fill\(|storageState|authorization|cookie|X-Amz' e2e/specs` → no match.
- No generated files edited.

## Findings
FINDING F-1: assertion received values (typed passwords) pass the gate into results.json and SUMMARY.txt
Severity: REQUIRED (FOLLOW-UP: not exploitable today, because no spec types a credential)
Affected: vizra-user, scripts/ci/artifact-allowlist.mjs (TEXT_RULES, redactText, STAGED_FILES results.json); VZ-FOUND-008
Observed: demo 4 above. The text rules cover only header/bearer/JWT/schemeless-URL shapes. The e2e.yml comment itself names "a typed password and an assertion's received value" as a known channel.
Failure: the first spec that fills a credential and fails a `toHaveValue`/`toHaveText` assertion uploads it.
Recommendation: do not stage results.json. Have SUMMARY drop `Expected:`/`Received:` bodies, or keep only title + file:line.

FINDING F-2: screenshots and videos are admitted on magic bytes only and are never redacted
Severity: REQUIRED (FOLLOW-UP: no authenticated page exists today)
Affected: artifact-allowlist.mjs STAGED_FILES/ALLOWED_FILES png/jpeg/webm
Observed: demo 3. Any `.png`/`.webm` with valid magic is staged whatever its pixels or trailing bytes. Pixels of an authenticated page are not inspectable.
Failure: once a spec authenticates, the gate does not meet the brief's "screenshot of an authenticated page… unless allow-listed AND redacted".
Recommendation: for authenticated projects, set screenshot/video off or refuse media in staging, behind an explicit per-project allowlist.

FINDING F-3: the plan's own remaining items 2 (2ac, job-log `--log` not wired into e2e.yml) and 3 (V-D stamp key) are still open
Severity: SHOULD (FOLLOW-UP). The PR does not claim them.

**Chair note (not a merge block):** this PR closes the artifact path for traces, the HTML report, error-context.md, headers, cookies and signed URLs. It does NOT make authenticated specs safe: F-1 and F-2 stand, and so does plan item 4. The HARD GATE on authenticating specs must stay closed after this merge.

## Verdict
No BLOCKING finding. Every token, cookie, signed-URL and trace sensitive artifact in today's tree is refused, and every workflow bypass I tried is red. F-1 and F-2 are only reachable once a spec authenticates, which the hard gate forbids. Follow-ups: 3.

FINAL VERDICT: PASS — SHA edb70a1fcb2290c636337db46da8d6e119cfab90
