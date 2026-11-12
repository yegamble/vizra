# vizra-user QUEUE-2f: e2e artifact allowlist gate (VZ-FOUND-008)

State: IN_PROGRESS, DRAFT PR yegamble/vizra-user#18 (branch feat/e2e-artifact-allowlist).

Done in slice 1: scripts/ci/artifact-allowlist.mjs is a default-deny gate over file types, trace zip members and content shapes, called from redact-artifacts.sh. Tests are in scripts/ci/artifact-allowlist.test.mjs, with red/green evidence in docs/evidence/QUEUE-2f/.

Remaining, in order:
1. Calibrate the gate against real traces and the HTML report from `npm run e2e:demos` (needs Docker), and allowlist only shapes that have been shown to be safe.
2. 2ac: quiet the `list` reporter, or pipe the job log through `--log`. This changes e2e.yml, so the D17c digest must be refreshed in the same commit.
3. V-D: keep the stamp key out of the main process's process.env while specs are collected.
4. HARD GATE: no authenticated spec until steps 1–3 are VERIFIED.
