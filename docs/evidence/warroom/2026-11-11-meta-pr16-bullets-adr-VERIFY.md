# Independent verification: vizra (meta) PR 16, acceptance bullets and ADR-001 versions

- Subject: https://github.com/yegamble/vizra/pull/16
- Head SHA verified: 791235375cd3d5b224e417d43cd78204f8480633 (PR head at start and at end, state OPEN)
- Base: origin/main 60a447fb4f6120b9f7e015ec6ea30b7eeb64ea8f (equal to the merge base)
- Date: 2026-11-11, about 16:40 to 16:50 UTC
- Verifier: independent sub-agent, did not write the PR; read-only, no edits, commits, pushes or GitHub setting changes
- Environment: macOS 26.5.1 (darwin), Python 3.9.6, git 2.50.1, gh 2.98.0; fresh clone of
  https://github.com/yegamble/vizra.git checked out at the SHA in a mktemp scratch directory, deleted at the end

## Owner ruling under test (2026-11-11)
"Inbox 16: add the missing acceptance bullets to docs/issues/VZ-ISSUE-001.md for the VZ-FOUND-002/003/006
ledger cases listed in the audit. This aligns the issue to the ledger, it does not change the ledger. Also
approved: the editorial ADR-001 update to the Go and Echo versions actually pinned."

## Commands

| # | Command (in the clone unless noted) | Exit | Result |
|---|---|---|---|
| 1 | `gh pr view 16 -R yegamble/vizra --json headRefOid,state,baseRefName,title,files` | 0 | head 7912353…, OPEN, base main, 2 files (issue +10/-0, ADR +5/-3) |
| 2 | `git clone` + `git fetch origin <SHA>` + `git checkout <SHA>`; `git rev-parse HEAD` | 0 | HEAD = 7912353… |
| 3 | `git diff --name-only origin/main...HEAD` | 0 | exactly the ADR and the issue file |
| 4 | `git diff --quiet origin/main HEAD -- docs/quality/features.json docs/evidence/ledger-generator` | 0 | no difference |
| 5 | `git diff origin/main...HEAD -- docs/issues/VZ-ISSUE-001.md` and `--numstat` | 0 | 10 added, 0 removed |
| 6 | scratch script `b.py` (run with `python3 -I`): parses features.json, matches each added line against the id's `cases` strings, checks section and that new-minus-added equals old | 0 | 10 of 10 OK, `B_SCRIPT_OK True` |
| 7 | `git diff origin/main...HEAD -- docs/adr/ADR-001-stack-pins-and-licences.md` | 0 | 3 lines changed, 2 appended |
| 8 | `gh api 'repos/yegamble/vizra-core/contents/go.mod?ref=main' -q .content \| base64 -d \| grep -n 'toolchain\|labstack/echo'` | 0 | line 12 `toolchain go1.27.4`; line 19 `github.com/labstack/echo/v5 v5.4.4` |
| 9 | `python3 scripts/check-doc-links.py` | 0 | pass |
| 10 | `python3 scripts/check-quality-json.py` | 0 | pass |
| 11 | `bash scripts/check-generated-ledger.sh` | 0 | "generated ledger reproduces byte-for-byte" (UTF-8 and C/POSIX); 192 requirements |
| 12 | `gh pr checks 16 -R yegamble/vizra` (first, 16:4x UTC) | 8 | ci-required and validate pending |
| 13 | `gh run list -R yegamble/vizra --commit <SHA> --json name,headSha,status,conclusion,databaseId`, polled every 30 s | 0 | run 43060597838 `ci-required` completed/success, headSha 7912353…; run 43060597796 `validate` completed/success, same headSha |
| 14 | `gh pr checks 16 -R yegamble/vizra` (final) | see end of file | see claim E |
| 15 | `gh pr view 16 -R yegamble/vizra-core --json title,state` | 0 | "fix(deps): go1.27.4 and echo v5.4.4 …" MERGED (the ADR's editorial line cites it correctly) |

One polling invocation (a single long shell loop) was killed by the tool host before printing; it was
repeated in shorter loops, whose results are rows 13 and 14. Nothing was lost.

## Result per claim

- **A — PASS.** Changed files are exactly `docs/adr/ADR-001-stack-pins-and-licences.md` and
  `docs/issues/VZ-ISSUE-001.md`. `docs/quality/features.json` and `docs/evidence/ledger-generator/*`
  are identical to origin/main (row 4).
- **B — PASS.** Ten added lines, none removed. All ten are in `## Acceptance (observable)`. Each is
  `- (VZ-FOUND-00N) <text>` with `<text>` byte-equal to a `cases` string of that id (script, row 6).
  Removing the ten added lines from the new file gives the old file exactly, so no existing bullet was
  changed, removed or reordered. Every ledger case of the three ids has a bullet (table below).
- **C — PASS.** The ADR diff is: Echo `≥ v5.3.1` → `≥ v5.4.4` in the Decision paragraph; Go `(1.27.1)` →
  `(1.27.4)` and Echo `≥ v5.3.1` → `≥ v5.4.4` in the licence table; an appended `## Editorial updates`
  section with the single line "2026-11-11: editorial, Go 1.27.4 and Echo v5.4.4 as pinned by vizra-core
  #16 (owner decision 2026-11-11 #1)". No other pin, decision, licence text or section is touched.
  vizra-core main pins go1.27.4 and echo v5.4.4 (row 8).
- **D — PASS.** All three scripts exit 0 in the clone (rows 9 to 11).
- **E — PASS.** `ci-required` run 43060597838 concluded success with headSha equal to the PR head (row 13).

## Case-to-bullet table

New = bullet added by this PR, verbatim from the ledger. Old = bullet already on main, worded differently.

### VZ-FOUND-002
| Kind | Ledger case | Covered by | Strength |
|---|---|---|---|
| success | Adding a route without spec fails; spec without route fails | Old: "Route-without-spec and spec-without-route both fail CI (demonstrated)" | equivalent (both directions fail) |
| success | Generated client diff is empty after regeneration | New, verbatim | identical |
| negative | Hand-edited generated file is rejected by a drift check | New, verbatim | identical |
| privacy / recovery | (no case strings in the ledger) | n/a | n/a |

### VZ-FOUND-003
| Kind | Ledger case | Covered by | Strength |
|---|---|---|---|
| success | `migrate up` from the release image applies cleanly on empty DB | New, verbatim | identical |
| success | sqlc-verify passes | New, verbatim | identical |
| negative | A DROP COLUMN in *.up.sql fails migrate-lint | New, verbatim | identical |
| negative | Editing sqlcgen output fails drift check | Old: "Hand-edited sqlc output fails drift check (demonstrated)" | equivalent |
| recovery | Dirty migration ledger is detected and reported, not auto-fixed | New, verbatim | identical |
| privacy | (no case strings in the ledger) | n/a | n/a |

### VZ-FOUND-006
| Kind | Ledger case | Covered by | Strength |
|---|---|---|---|
| success | Every key read by config.Load reaches api and worker containers (asserted from rendered compose) | New, verbatim | identical |
| success | Every key `vizra setup` writes exists in the template | New, verbatim | identical |
| negative | Production boot with dev JWT/session secret fails | Old: "Production boot refuses dev secrets (demonstrated)" | equivalent in substance; the old bullet says "dev secrets" without naming JWT/session (unchanged by this PR, see follow-up 3) |
| negative | A key added to config without template/compose consumer fails CI | New, verbatim | identical |
| privacy | Log denylist test proves tokens/passwords/signed URLs never appear | New, verbatim | identical |
| recovery | (no case strings in the ledger) | n/a | n/a |

No ledger case is left without a bullet. No new bullet is weaker or stronger than its case, since all ten
are byte-equal to it.

## Findings

Blocking: none.

Follow-up (not blocking under AGENTS.md "Blocking findings"; none is a privacy, auth, data-loss or
false-green defect):
1. ADR-001 writes Echo as `≥ v5.4.4`, a floor, while vizra-core go.mod pins exactly v5.4.4, and the
   editorial line says "as pinned". The floor form was already the ADR's convention (`≥ v5.3.1`) and is
   true of the pin, so this reads correctly as a minimum; an exact pin wording would be tighter.
2. `docs/issues/VZ-ISSUE-001.md` line 8 (Outcome paragraph) still says "Echo v5 ≥ 5.3.1". Not wrong as a
   floor, but now out of step with ADR-001. The owner ruling did not ask for it to change.
3. The pre-existing 006 bullet "Production boot refuses dev secrets" is less specific than the ledger's
   "dev JWT/session secret". Unchanged by this PR; a verbatim alignment could go in the batched follow-up.
4. vizra-core go.mod has `go 1.26.0` as the language line and `toolchain go1.27.4`; consistent with the
   ADR's "supported lines 1.26 and 1.27". Informational only.

## Not run
- No product test lanes (Go, web, search): docs-only PR, not in scope of the requested checks.
- The `validate` workflow's steps were not re-run locally beyond the three scripts in claim D; its CI
  result (success) is taken from GitHub.
- The audit document that lists the missing cases was not re-derived; coverage was checked directly
  against every case string in the ledger for the three ids instead.

## Final state
- Final `gh pr checks 16`:
    GitGuardian Security Checks	pass	1s	https://dashboard.gitguardian.com	
    ci-required	pass	7m18s	https://github.com/yegamble/vizra/actions/runs/43060597838/job/130661990209	
    validate	pass	7m25s	https://github.com/yegamble/vizra/actions/runs/43060597796/job/130661800959	
- PR head at end: 791235375cd3d5b224e417d43cd78204f8480633
- Scratch clone deleted.

FINAL VERDICT: PASS — SHA 791235375cd3d5b224e417d43cd78204f8480633
