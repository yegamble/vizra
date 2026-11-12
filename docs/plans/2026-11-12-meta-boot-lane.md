# Execution plan: VZ-CI-003 boot lane (slice 1), VZ-ISSUE-004, VZ-FOUND-005 transcripts

## Context
Base origin/main d1988f9. Branch feat/ci-003-boot-lane, worktree .claude/worktrees/meta-boot-lane. Budget at start: VZ-CI-003 0/4 verdicts, ticks 0/12; VZ-FOUND-005 3/4 verdicts.

## Acceptance (this slice)
- boot lane: bootstrap.sh components (SHAs recorded in artifact component-shas.txt), build core+user images from source, render docker-compose.yml + docker-compose.prod.yml with dummy-secret env (openssl; `vizra setup` does not exist yet).
- migrate one-shot run from the service image exits 0 within timeout, twice (apply + idempotent rerun). ASSUMPTION: "both migration one-shots" = the core `migrate` service (the only one-shot in the compose model); recorded for the verifier.
- Negative: never-exiting migrate (tests/boot/migrate-never-exits.yml) is killed by the timeout → in-lane self-test, plus a temporary red commit demonstration.
- up --no-build --pull never --wait; /readyz 200; stop postgres → non-200 within declared interval (BOOT_READY_INTERVAL=30s, declared here; core declares none); start → 200, api StartedAt+RestartCount unchanged.
- compose logs artifact; dummy secret values asserted absent from it.
- NOT in this slice: fixture JPEG upload + thumbnail hash (needs M1 upload) — VZ-CI-003 stays open; VZ-TOPOLOGY-002/003 live runs; adding `boot` to required-checks.txt (owner-visible, separate).

## Checklist
- [x] scripts/boot-lane.sh (shellcheck clean), tests/boot/migrate-never-exits.yml, .github/workflows/boot.yml (pins/workflow/lane-integrity checks pass locally)
- [x] draft PR pushed
- [ ] boot lane green on GitHub (iterate via `gh run view --log`)
- [ ] red demo: temp commit setting BOOT_EXTRA_COMPOSE=tests/boot/migrate-never-exits.yml in boot.yml, then revert commit (no force-push)
- [ ] record run links here; evidence file
- [ ] later slice: upload/thumbnail; external PG/Redis shapes

## Progress and evidence
(append run URLs and outcomes)
