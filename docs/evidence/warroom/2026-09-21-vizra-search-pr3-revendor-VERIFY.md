# Independent verification — vizra-search PR #3 (re-vendor core contract @ core main 4a80a1e)

**Verifier:** war-room independent verifier (did not write this code).
**Subject:** https://github.com/yegamble/vizra-search/pull/3 — `chore/revendor-core-4a80a1e`
**SHA verified:** `aa1c3fb73b1771b91704587bb1d2a25b7cf39396` (parent `581bffc4c116af7eee4f41e7f1157e1a1bd8109a`, committed 2026-09-21T03:22:26-04:00).
**Branch head at verification time:** `aa1c3fb73b1771b91704587bb1d2a25b7cf39396` — unmoved.
**Base:** `main` @ `808a5499dae1d58971d740f34749c2f35149fa4d`.
**Plan under review:** `/Users/yosefgamble/github/vizra/docs/plans/2026-09-21-vizra-search-revendor-4a80a1e.md`

## 0. Environment

Fresh clones made for this verification only, in a private `mktemp -d` under the shared scratchpad
root (`…/scratchpad/vzv-search-pr3-KI6LB6/`), deleted at the end. The shared working checkouts
`/Users/yosefgamble/github/vizra/vizra-core` and `…/vizra-search` were **never touched**.

| | |
|---|---|
| host | `Darwin 25.5.0 arm64` (macOS) |
| go | `go1.27.1 darwin/arm64` |
| make | GNU Make 3.81 |
| python3 | 3.9.6 |
| jq | jq-1.7.1-apple |
| govulncheck | v1.8.0 (the version `.github/workflows/ci.yml` pins) |
| search clone | `gh repo clone yegamble/vizra-search` → `git checkout aa1c3fb7…`, clean tree |
| core clone | `gh repo clone yegamble/vizra-core`, `origin = https://github.com/yegamble/vizra-core.git` |

`docker-build` was **not** run locally: arm64 host, amd64 image target (ADR-009 / Q-027). Judged
from CI on this SHA — see §6. Everything else was run here.

---

## 1. Provenance — verified independently (acceptance 1)

Run in my own clone of `yegamble/vizra-core`:

```
$ git merge-base --is-ancestor 4a80a1e3f36b8001c2954d0568bea29268e739fe origin/main ; echo $?
0
$ git branch -r --contains 4a80a1e3f36b8001c2954d0568bea29268e739fe
  origin/HEAD -> origin/main
  origin/main
$ git log -1 --format=%H origin/main -- api/
4a80a1e3f36b8001c2954d0568bea29268e739fe
$ git log -1 --format='%H %s' origin/main
4a80a1e3f36b8001c2954d0568bea29268e739fe chore(ci,config): hardening sweep A — … (#6)
```

The pinned commit **is** core `main`'s tip and **is** the last commit on `main` touching `api/`.

Bytes, by two independent methods (sha256 of the git object stream, and git's own blob id):

| file | core `4a80a1e` sha256 | bytes | vendored at `aa1c3fb` sha256 | bytes | core blob | vendored blob |
|---|---|---|---|---|---|---|
| `api/search-internal.openapi.yaml` | `a78d8aa7320dbd49530b10bf1c9dcb22ff5f586f06bd7c821aa7cb8b4a735448` | 25297 | **identical** | 25297 | `848503cca45dc427fede810d3ab30e73e07bd392` | **identical** |
| `api/search-hmac-testvectors.json` | `f95623b0ad6783818bc73c5b4d516d84ce7b2b6afde01397a6c8b15a422c2862` | 22321 | **identical** | 22321 | `1509da859954f65fd5542053332b8417fe4eb8da` | **identical** |

Both equal what `api/CONTRACT-SOURCE.json` records (`make vendor-contract-check` exit 0, §5).
**Acceptance 1 (provenance + digests) reproduced.**

### Only the prose field moved — measured, not asserted

Old vendored vectors (`origin/main:api/search-hmac-testvectors.json`) vs new, key by key
(`jq -cS '.<key>' | shasum -a 256`):

```
SAME  _comment            SAME  key_utf8              SAME  max_clock_skew_seconds
SAME  negative_vectors    SAME  scheme                SAME  vectors
SAME  verifier_now_unix   SAME  window
DIFF  key_utf8_warning    d06ecc83a953 -> a6f2c225eb1c
```

No key added or removed. `vectors` 5 → 5 and `negative_vectors` 24 → 24, each half hashing
identically (`9d7bfdc4943ae075…`, `a835c72fe92e6288…`). The textual diff on the whole file is
**one line**: `VIZRA_SEARCH_HMAC_KEY` → `SEARCH_HMAC_KEY` inside `key_utf8_warning`.
**All 29 vectors are byte-identical.** Confirmed as the chair asked.

---

## 2. Scope (acceptance 4)

`git diff --name-status origin/main...aa1c3fb` — 13 files, +4216 −11:

```
M AGENTS.md                             (+28, pure addition: documents the new command)
M Makefile                              (+21, pure addition — see §4c)
M api/CONTRACT-SOURCE.json              (source_commit, vendored_at, one sha256/bytes, $provenance_note)
M api/search-hmac-testvectors.json      (one line, the prose field)
A scripts/vendor-contract.py            (349)
A scripts/revendor-demo.sh              (293)
A docs/evidence/pr3/{README.md, provenance.txt, revendor-run.txt,
                     D-A-…txt, D-C-…txt (2846), D-V-…txt, lanes-local.txt}   (3513 lines)
```

3513 of the 4216 added lines (83%) are evidence transcripts; 642 are the two new scripts; 49 are
`AGENTS.md` + `Makefile`. **Confirmed as claimed.**

Negative checks, all run by me on the diff:

- `git diff --stat origin/main...HEAD -- .github/` → **empty**. No workflow, no
  `.github/required-checks.txt`, no CODEOWNERS change.
- `scripts/ci-required-guard.sh`, `scripts/contract-drift-guard.py`, `scripts/check-workflows.py`:
  not in the diff.
- No `*.go` file in the diff at all — no production code, no test file, so no test could have been
  weakened, deleted, renamed or skipped.
- `VIZRA_SEARCH_MODE` / `VIZRA_MODE`: not in the diff. No rename.

**Acceptance 4 holds.**
