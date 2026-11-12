# Execution plan: VZ-CI-004 (govulncheck lane) — vizra-search green

## Context
yegamble/vizra-search, base origin/main 4810048, branch `fix/govulncheck-green`, worktree .claude/worktrees/search-govuln. Pattern: vizra-core #16 (ce805b4).

## Acceptance
`govulncheck ./...` (govulncheck@v1.8.0) reports no vulnerabilities on the PR head; ci-required green. Non-goals: no lane removal, ignore list, `|| true` or package narrowing.

## Implementation
go.mod toolchain go1.27.1 -> go1.27.4 (go.dev/dl JSON); echo/v5 v5.3.1 -> v5.4.4 (GO-2026-6873/6876/6877/6879/6881/6883 called, fixed v5.4.0; `go list -m -versions`); Dockerfile golang:1.27.4-bookworm index sha256:4fa7c968…f36570ea (imagetools inspect); ci.yml GO_VERSION; scripts_test.go fixture string; AGENTS.md pin rows.

## Verification
govulncheck, make ci, scripts/ci-required-guard.sh, go mod verify (via quiet.sh, GOTOOLCHAIN=go1.27.4); PR CI.

## Progress and evidence
Red on 4810048 (go1.27.1): 10 vulns, exit 3 (6 echo + GO-2026-6859, 6809, 6617, 6613). Green locally: "No vulnerabilities found", exit 0. Remaining results in the PR body. State: READY_FOR_REVIEW, UNVERIFIED.

## Blockers and handoff
None known. Independent verifier next.
