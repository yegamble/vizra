# VERIFY vizra-user PR #20: QUEUE-2f F-1/F-2 artifact leaks (VZ-FOUND-008)

- SHA: `76401deb57aeafe86ddc4452cb210f4d8debc6bb`. It was the PR head at the start and at the end.
- Clone: fresh clone in `/tmp/vzv-user-pr20-8eGaV5` (deleted at the end). Node v24.21.0, darwin arm64.
- Verifier: independent; I did not write this code. This is verdict 2 of 4 for VZ-FOUND-008.

## Commands (my clone, at the SHA)
| Command | Exit | Result |
|---|---|---|
| `npm ci` | 0 | |
| `npx vitest run scripts/ci/artifact-allowlist.test.mjs` | 0 | 1 file, 24/24 passed, 0 skipped |
| `bash scripts/ci/require-checks_test.sh` | 0 | 237 cases, 244 assertions, 0 failed (PR #18 had 235/242, so +2 cases) |
| `bash scripts/ci/check-e2e-lane.sh` | 0 | OK |
| `npm run check:hygiene` | 0 | 361 sources clean, 17 digest lines match |

## CI on the SHA (`gh run list --commit`)
These are all `success` on 76401de: ci-required 43281799184, e2e 43281799154, ci-guard 43281799136, frontend-ci 43281798573, contract-ci 43281799328 and supply-chain 43281799038. `required-checks.txt` lists frontend, contract, ?guard, ?docker-build and e2e. Every required lane ran. `docker-build` is optional and did not run, which matches PR #18.

## Reproducer (F-1/F-2 fixture, run through the shipped path)
- Generator: a Python script outside the repo, run with `python3 -I mk.py <clone>`. I ran the shipped path from the repo root: `bash scripts/ci/redact-artifacts.sh test-results playwright-report`, which calls `artifact-allowlist.mjs --stage artifact-upload` at line 243.
- `playwright-report/results.json` holds three specs: (a) `unlisted.spec.ts`, (b) `listed.spec.ts`, and (c) `authlisted.spec.ts` tagged `@authenticated`.
- Each spec has an error message containing all of these:
  - a matcher header and a `Locator:` line;
  - `Received: "CorrectHorse!PWSENTINEL"`;
  - a `Call log` with `Authorization: Bearer …`, `set-cookie: sid=…` and an `X-Amz-Signature=` URL;
  - `stack` and `value` fields holding the sentinel.
- Each spec has these attachments: png, webm, an uppercase `SHOT.PNG` and `trace.zip`.
- Bypass files I planted:
  - `note.txt`;
  - `fake.txt` (png magic bytes plus a bearer token);
  - `results-copy.json` (a renamed results file);
  - `error-context.md` holding the password;
  - a symlink `link.png` pointing to a png outside the tree;
  - a directory named `Bearer abcdefghijklPWSENTINEL/x.png` (a secret in the filename, owner unknown);
  - a temporary scratch edit of `artifact-media-allowlist.json` that lists (b) and (c) with reasons. I restored it afterwards.
- Result: rc=0. `artifact-upload/` contains `SUMMARY.txt` plus only `test-results/b-listed/{test-failed-1.png,video.webm,SHOT.PNG}`.
- Every other file was REFUSED with a named reason:
  - (a) media: media-not-opted-in;
  - (c) media: media-authenticated-spec, even though (c) is on the allowlist;
  - the symlink: refused as a symlink;
  - the secret filename: media-not-opted-in;
  - txt/md/renamed json/trace.zip/results.json: not-staged.
- Media therefore reached the upload only in case (b). CONFIRMED.
- SUMMARY.txt: Received/Expected values, the Call log (bearer, cookie, signed URL), the stack and the value are all absent. Uppercase extensions go through the media verdict (`/i`). A png payload in a `.txt` file is not staged.
- **One leak:** the message line `Timed out waiting for token abcPWSENTINEL` was copied verbatim into SUMMARY.txt for all three specs. See F-A.

## Retargeted tests (`git show 23ae754`)
- "uploads … png, webm, results.json" became `expect(got).toEqual(["SUMMARY.txt"])` plus three exact `REFUSED … media-not-opted-in|not-staged` stderr matches.
- "admits a clean results.json" became `not.toContain("playwright-report/results.json")`.
- Both changes are strictly tighter: an exact set where there was a superset, and named refusals.
- In check-e2e-lane.mjs, `test-results/` and `playwright-report/results.json` are removed from the upload allowlist. `e2e.yml:243-245` uploads only `artifact-upload/` and `playwright-browsers.txt`.

## Findings
FINDING F-A: free text that starts with `Timeout`/`Timed out` passes the F-1 line allowlist verbatim
Severity: SHOULD (FOLLOW-UP). The PR's "free text withheld" claim is false for this one line shape. It is not exploitable today, because no spec types a credential and real Playwright `Timed out Nms waiting for expect(...)` lines carry no value. A secret reaches this line only through author-written error text.
Affected: vizra-user `scripts/ci/artifact-allowlist.mjs`, `MESSAGE_LINE_ALLOW` regex `/^(Error: )?Timed? ?out\b[^"'`]*$/i`.
Observed: the reproducer above. `Timed out waiting for token abcPWSENTINEL` appears in SUMMARY.txt. Bearer and URL-query shapes are still caught by redactText; a bare password is not.
Recommendation: anchor the regex to Playwright's exact shapes, `^Timed out \d+ms waiting for expect\(…\)\.\w+\(…\)$` and `^Timeout: \d+ms$`. Add a negative test with the sentinel.

FINDING F-B: `Locator:` lines pass verbatim, so a selector built from a value (`getByText(secret)`, `[value="…"]`) would upload it
Severity: SHOULD (FOLLOW-UP). No such spec exists today.

FINDING F-C (carried, = PR #18 F-3): the job-log gate (`artifact-allowlist.mjs --log`) is still not wired into e2e.yml (grep found nothing), and the V-D stamp key is still open. REFUSED lines echo artifact paths into the public job log.
Severity: SHOULD (FOLLOW-UP). Not claimed by this PR.

## Gate judgement (hard gate on signing-in specs)
Do NOT lift it yet for M1. The artifact upload path is now default-deny and survived every bypass I tried. Lift the gate only after all three of these:
1. F-A: tighten the Timeout regex.
2. F-C: wire the job-log gate. Playwright's list reporter and `docker logs | tail -200` print failure messages, including Received values, to the public job log. That job log is outside this artifact gate.
3. F-C: settle the stamp key.

## Verdict
No BLOCKING finding by the AGENTS.md bar: F-A needs author-written secret text, and no spec authenticates in today's tree. Every bypass on the brief's list was refused. CI is green on the SHA. Follow-ups: 3.

FINAL VERDICT: PASS — SHA 76401deb57aeafe86ddc4452cb210f4d8debc6bb
