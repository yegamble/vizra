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

---

## 3. Demonstrations — reproduced by me, from my own clone (acceptance 2)

I did **not** run the builder's `scripts/revendor-demo.sh` to produce these. I applied the
mutations myself, with **different anchors** from the ones the harness hard-codes, so the
demonstration is not anchor-specific.

### D-A — before the re-vendor, core main's vectors file turns the manifest test red by name

Run in a second worktree at base `808a5499…` (the pre-re-vendor tree):

| state | `api/search-hmac-testvectors.json` sha256 | `go test -run '^TestEveryVendoredFileMatchesItsManifest$' ./internal/httpapi/` |
|---|---|---|
| as vendored on `main` (stale pin) | `ff21e6b8cdd7d3bc…` | **exit 0 — GREEN** |
| `git show 4a80a1e:…` dropped in, manifest untouched | `f95623b0ad678381…` | **exit 1 — RED** |
| restored | `ff21e6b8cdd7d3bc…` | **exit 0 — GREEN** |

The RED names the test and the reason, verbatim:

```
contract_drift_test.go:106: the vendored api/search-hmac-testvectors.json does not match its manifest.
      manifest sha256: ff21e6b8cdd7d3bc32caa455cf605e1069ea4534db2b9b0a9e2d90c78a3d35c3
      file sha256:     f95623b0ad6783818bc73c5b4d516d84ce7b2b6afde01397a6c8b15a422c2862
    This repository does not own it. Re-vendor from yegamble/vizra-core@415a6d19… instead of editing it.
contract_drift_test.go:111: the vendored api/search-hmac-testvectors.json is 22321 bytes, the manifest says 22327
--- FAIL: TestEveryVendoredFileMatchesItsManifest (0.00s)
```

**Reproduced.** This is what makes the re-vendor required rather than cosmetic.

### D-C — after the re-vendor, one byte in either vendored file is caught by both lanes

My anchors: YAML `this file is the canonical copy` → `canonicat` (inside the header comment);
JSON `Generate a real key with` → `real kez with` (inside the non-normative
`key_utf8_warning` prose). Both files still parse afterwards (checked: `yaml.safe_load` and
`json.load` both succeed), so a parse error cannot masquerade as a digest failure.

| state | sha256 | `make contract-drift` | `make ci` | `vendor-contract --check` |
|---|---|---|---|---|
| baseline | `a78d8aa7…` / `f95623b0…` | **0 GREEN** | **0 GREEN** | **0 GREEN** |
| YAML one byte | `73c08102372c6f2f…` | **2 RED** | **2 RED** | **1 RED** |
| YAML restored | `a78d8aa7…` | **0 GREEN** | — | — |
| JSON one byte | `7cc4537cbb1aa357…` | **2 RED** | **2 RED** | **1 RED** |
| JSON restored | `f95623b0…` | **0 GREEN** | **0 GREEN** (`324 tests… 0 failures, none deselected`; `347 pass events, 0 skips`) | **0 GREEN** |

Every RED names the mechanism, not just an exit code — e.g. for the YAML mutation:

```
contract_drift_test.go:106: the vendored api/search-internal.openapi.yaml does not match its manifest.
      manifest sha256: a78d8aa7320dbd49530b10bf1c9dcb22ff5f586f06bd7c821aa7cb8b4a735448
      file sha256:     73c08102372c6f2fd1a2822eb7631b245bb82a504a557ff954a4a14f3949350e
CONTRACT-DRIFT LANE REFUSED: 1 test(s) failed:
  github.com/yegamble/vizra-search/internal/httpapi.TestEveryVendoredFileMatchesItsManifest
```

`git status --porcelain` empty after every restore. **Acceptance 2 reproduced on both files
against both lanes.**

---

## 4. Vectors (acceptance 3)

Counted by me from `go test -count=1 -json ./...`, parsing `Action:"pass"` subtest events — not
by reading the builder's transcript:

- `TestVerifierReproducesTheSharedVectors` — **5/5 ACCEPT** subtests pass:
  `events-batch, search-empty-body, search-simple, suggestions, unicode-body`.
- `TestVerifierRefusesEveryNegativeVector` — **24/24 REJECT** subtests pass:
  `method-lowercase, method-mixed-case, nonce-empty, nonce-not-hex, nonce-too-short,
  nonce-uppercase-hex, timestamp-duplicated-header, timestamp-duration-overflow-ahead,
  timestamp-duration-overflow-far, timestamp-empty, timestamp-future-past-window, timestamp-hex,
  timestamp-leading-plus, timestamp-leading-space, timestamp-leading-zero, timestamp-leading-zeros,
  timestamp-max-int64, timestamp-max-int64-overflow, timestamp-one, timestamp-stale-past-window,
  timestamp-trailing-space, timestamp-underscores, timestamp-year-10000, timestamp-zero`.
- The vendored file itself carries `vectors: 5`, `negative_vectors: 24` — so **every** vector in
  the file is consumed; none is loaded-and-ignored.

Whole-suite counts, my own run: **347 pass, 0 skip, 0 fail**. `grep -rn 't\.Skip' --include='*_test.go'`
→ **no match**; no `//go:build`-excluded test file exists, so nothing is skipped by exclusion
either. **Acceptance 3 reproduced, counts identical to the builder's claim.**

---

## 5. Lanes I ran, from the clean clone at `aa1c3fb7`

| lane | command | exit | evidence |
|---|---|---|---|
| **documented CI entry point** | `make ci` | **0** | full transcript below |
| fmt-check | (in `make ci`) | 0 | `fmt-check: clean` |
| vet | (in `make ci`) | 0 | — |
| echo-containment | (in `make ci`) | 0 | `Echo is confined to internal/httpapi` |
| build | (in `make ci`) | 0 | binary linked at `aa1c3fb7…` |
| contract-drift | (in `make ci`) | 0 | `4 package(s) selected with no test-selecting flag`; `324 tests ran across 4 package(s), 0 failures, none deselected` |
| test (race) | (in `make ci`) | 0 | 6 packages `ok` |
| test-noskip | (in `make ci`) | 0 | `347 pass events, 0 skips` |
| tidy-check | (in `make ci`) | 0 | `tidy-check: tidy` |
| vendor-contract-check | `make vendor-contract-check` | **0** | both files `OK` against the manifest |
| ci-required-guard | `./scripts/ci-required-guard.sh` | **0** | floor intact, 6 fixtures exercised |
| check-workflows | `./scripts/check-workflows.py` | **0** | 2 workflows, no `continue-on-error` |
| govulncheck v1.8.0 | `go run golang.org/x/vuln/cmd/govulncheck@v1.8.0 ./...` | **0** | `No vulnerabilities found.` |
| `bash -n scripts/revendor-demo.sh` | — | 0 | |
| `python3 -m py_compile scripts/vendor-contract.py` | — | 0 | |
| **docker-build** | — | **NOT RUN LOCALLY** | arm64 host, amd64 image target (ADR-009 / Q-027). Judged from CI — §6, where it ran on `ubuntu-24.04` and passed. |

`make ci` wall time 37.7 s. Every number the builder reported reproduced **exactly** (324 / 347 / 0).

### The PR-#2-era false-positive holes, re-probed

| hole | probe | result |
|---|---|---|
| is the manifest test still *selected* by the lane? | both one-byte mutations turned `make contract-drift` red through the lane (not through a hand-run `go test`) | **closed — proven by mutation**, plus the out-of-make anchor prints `4 package(s) selected with no test-selecting flag` and `none deselected` |
| does the fixture glob fail when its directory is missing? | `mv scripts/testdata …; ./scripts/ci-required-guard.sh` | **exit 1** — `With the directory gone there is nothing to prove it with, and this guard must not pass by default` |
| …and when the directory exists but is empty? | `mkdir scripts/testdata` (empty); same guard | **exit 1** — `MISSING FIXTURE: 'scripts/testdata/wf-false.yml' is a non-optional fixture and is absent` |
| does `test-noskip` really count zero skips? | my own `grep -c '"Action":"skip"'` over `go test -json ./...` | **0 skips, 347 passes, 0 fails** — matches the lane's own arithmetic |

All three PR-#2-era holes are closed at this SHA. Tree restored and `git status --porcelain` empty
after each probe.

---

## 6. GitHub CI on this SHA (acceptance: `ci-required` green on `aa1c3fb7…`)

My own `gh` calls, not the PR body's table:

```
$ gh api repos/yegamble/vizra-search/commits/aa1c3fb73b1771b91704587bb1d2a25b7cf39396/check-runs
total_count = 12 ; unique conclusions = ["success"]
```

| check run | status | conclusion | app |
|---|---|---|---|
| fmt, vet, echo-containment, build, contract-drift, test, test-noskip, tidy-check, govulncheck, docker-build | completed | **success** | github-actions |
| **ci-required** | completed | **success** | github-actions |
| GitGuardian Security Checks | completed | **success** | gitguardian |

**The required-checks manifest matches the jobs that actually ran.** `.github/required-checks.txt`
lists exactly 10 names — `fmt, vet, echo-containment, build, contract-drift, test, test-noskip,
tidy-check, govulncheck, docker-build` — and all 10 exist as *completed, successful* check runs on
this SHA. No listed lane is missing, skipped, cancelled or never-executed. `ci-required`'s own log
polls each one by name and ends:

```
ci-required: every required check succeeded on aa1c3fb73b1771b91704587bb1d2a25b7cf39396
```

All 7 of its steps concluded `success` (no step skipped). The `ci` workflow run
(35572658912) shows all 10 jobs `success`, including **`docker-build`** — the lane I could not run
on this arm64 host.

**Which tree CI tested.** The workflow triggers on `pull_request` and `actions/checkout` is used
with no `ref:` override, so CI built the **merge commit** `7c9029747b4af58e3f5bdedb1bce3bc61975e32f`
(parents `808a5499…` = current `main`, and `aa1c3fb7…`). I checked that this does not matter here:

```
tree(aa1c3fb7)               = 88ff4b7a5179ff23d4b27551b23186723748ab9a
tree(refs/pull/3/merge)      = 88ff4b7a5179ff23d4b27551b23186723748ab9a
git diff aa1c3fb7 refs/pull/3/merge  ->  empty
```

**The tree CI tested is byte-identical to the head tree I verified.** `main` has not moved since
the merge base, so no untested divergence exists.

---

## 7. Diff audit against the AGENTS.md review rules

| hunted for | result |
|---|---|
| privacy leak / private data in logs | none. The only new output is digests, commit SHAs and file paths. |
| secrets or credentials in output or committed transcripts | **none.** Scanned `docs/evidence/pr3/` and both new scripts for `gh[pousr]_…`, `github_pat_`, `Bearer …`, `AKIA…`, PEM private keys, `Authorization:`, `x-access-token`, `password=`, `SEARCH_HMAC_KEY=…` → no match. The one key in the diff is `key_utf8`, the deliberately-published test vector that both repos refuse by exact match. |
| missing negative tests | none introduced: the 24 REJECT vectors all still run and pass. |
| weakened or deleted assertions, skips | **no `*.go` file is in the diff at all.** 0 skips measured independently. |
| hand-edited generated files | the two vendored files are written by the script and byte-equal core's; I verified against core's git objects, not against the manifest. |
| invented package APIs | none — the new script uses only stdlib (`argparse, datetime, hashlib, json, os, subprocess, sys`). |
| unbounded resources | none. No new runtime path; both scripts are developer tools. |
| shell injection in the new tooling | **none found.** No `shell=True`, `os.system` or `os.popen` anywhere in `scripts/*.py`; every `git` call is an argv list. |
| mock data in production paths / dead controls / fake success | n/a — no product surface changed. |
| Makefile integrity (the core-PR-#6 class) | **clean.** `git diff --unified=0 … -- Makefile` contains **no `-` lines**: the change is a pure 21-line append. The `ci:` target at line 33 is byte-unchanged and still reads `ci: fmt-check vet echo-containment build contract-drift test test-noskip tidy-check`. No lane reordered, renamed or removed; no `SHELL`/`.SHELLFLAGS`/`MAKEFLAGS` introduced; `./scripts/ci-required-guard.sh` (which parses the recipes) exits 0. |
| CI provenance overclaim | `vendor-contract-check` is **not** in `make ci` and **not** in `.github/required-checks.txt` — verified in both files. The PR body and AGENTS.md both state this explicitly and correctly ("deliberately not a CI lane … `contract-drift` already fails on any drift"). **No sentence claims CI enforces provenance.** The overclaims I did find are about the *script's* refusals — see FINDING 1 and 2. |
| unverified head | branch head is still `aa1c3fb7…`; PR `OPEN`, `MERGEABLE`. |

---

## 8. Attacking the new tooling's refusals (the chair's item (a))

New tooling in a contract-provenance path, so I attacked each documented refusal from an
adversarial `vizra-core` checkout I built in my own scratch dir (a copy — the shared
`/Users/yosefgamble/github/vizra/vizra-core` was never touched).

| attack | expected | **observed** |
|---|---|---|
| `--ref feature/x` (name not ending `main`) | refuse | **refused**, exit 1 |
| `--ref main-tag` (tag, name not `main`) | refuse | **refused**, exit 1 |
| `--core /tmp` (not a git checkout) | refuse | **refused**, exit 1 (`/tmp is not a git checkout`) |
| dirty / mid-edit core working tree | ignore the worktree | **correct** — reads only `git show <commit>:<path>`, committed objects only |
| unquoted shell input | none | **correct** — argv lists throughout, no `shell=True` |
| credential in output | none | **correct** |
| a file list that silently omits a file | refuse | **refused** — `MIN_VENDORED_FILES = 2` rejects a manifest pinning fewer than two files |
| bytes written without verification | never | **correct** — writes, re-opens, compares to what it fetched, then digests **the bytes read back off disk** (`vendor-contract.py:209-214`); a mid-loop failure leaves the manifest un-rewritten, so the tree goes red rather than silently green |
| **a git *tag* literally named `main`** | refuse | **ACCEPTED — exit 0** |
| **a branch named `<anything>/main` that is not on core's main** | refuse | **ACCEPTED — exit 0, poisoned bytes vendored, manifest records `source_ref: "main"`** |
| **a core checkout whose `origin` is not `yegamble/vizra-core`** | refuse, or at least not claim otherwise | **ACCEPTED, and the transcript prints `source repository : yegamble/vizra-core` anyway** |
| network absent / stale clone | — | the script never runs `git fetch`; `origin/main` is whatever the local clone last saw. Not exploitable (a stale pin is still a real commit on main), but "resolves the commit itself" is bounded by the freshness of the caller's clone. |
| symlinked / path-traversing destination | — | `dest = os.path.join(REPO, entry["vendored_path"])` is not normalised and `open(dest,'wb')` follows a symlink. Reaching it requires first editing `api/CONTRACT-SOURCE.json`, which is CODEOWNERS-protected (`/api/ @yegamble`) — so I rate this theoretical, not a finding on its own. |

The three **ACCEPTED** rows are one defect, written up as FINDING 1.

---

## Findings

```
FINDING 1: the vendoring script's "refuses a --ref that is not main" guard is a
           string-suffix test, and the manifest then launders the ref it used
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/vendor-contract.py:141-148 (the guard), :226 (the laundering),
             AGENTS.md:85-86 (the claim), api/CONTRACT-SOURCE.json:17-18 ($provenance_note)
  requirements: the slice's acceptance 1 ("re-vendor through the repository's own
             command; the manifest records a source_commit that is ON core's main").
             No VZ- ID yet — propose one for "contract provenance tooling".

Observed:
  The whole reason this script exists is that PR #1 pinned a commit that lived
  only on a feature branch. The guard meant to prevent a repeat is:

      short = ref.split("/")[-1]
      if short != "main" and not allow_any_ref:
          die("--ref %r is not a main branch. ...")

  That accepts any ref whose LAST PATH SEGMENT is the five letters "main". I
  built an adversarial copy of a vizra-core clone in my own scratch dir and
  proved three ways past it:

    1. `--ref main-tag`   -> correctly REFUSED (exit 1).
    2. `--ref main` where `main` is a git TAG, not a branch -> ACCEPTED, exit 0.
    3. `--ref fake/main`, a local branch that is NOT an ancestor of origin/main
       and whose api/search-hmac-testvectors.json I had poisoned by replacing
       key_utf8 with "ATTACKERKEYATTACKERKEYATTACKER12" -> ACCEPTED, exit 0.

  Run 3, verbatim from the script's own transcript:

      source repository : yegamble/vizra-core
      source ref        : fake/main (tip 4c45adeb8393eca425ab413e5b2f3d2cb9f9eff3)
      source commit     : 4c45adeb8393eca4...   <- pinned (last commit on fake/main touching api/)
      subject           : attacker: swap the HMAC key on a branch named .../main
      api/search-hmac-testvectors.json  sha256=f6c3fd8af925fd6e... UPDATED

  and the manifest it then wrote:

      source_commit : 4c45adeb8393eca425ab413e5b2f3d2cb9f9eff3
      source_ref    : main          <-- vendor-contract.py:226, args.ref.split("/")[-1]
      source_repository : yegamble/vizra-core

  `git merge-base --is-ancestor 4c45ade origin/main` exits 1 — that commit is on
  no branch anyone else can see. `./scripts/vendor-contract.py --check` on the
  resulting tree exits **0**, because --check only compares bytes to manifest.

  The second half of the advertised guard cannot fire at all. `api_commit` comes
  from `git log -1 <ref> -- api/`, so it is an ancestor of `<ref>`'s tip BY
  CONSTRUCTION; the script's own comment at :158-160 concedes this ("git log
  <ref> already guarantees it") and says the check "also covers --commit" — a
  flag that does not exist in the argument parser.

  So the two sentences that promise more than the control delivers are:

    AGENTS.md:85-86 — "...and **refuses** a commit that is not an ancestor of
    that branch tip, and a `--ref` that is not a `main` branch."

    api/CONTRACT-SOURCE.json:17-18 — "scripts/vendor-contract.py enforces this:
    it refuses a commit that is not an ancestor of the branch tip, and refuses a
    --ref that is not main."

  The second one is written INTO the provenance record itself, which is the
  artifact a future reviewer will trust.

Failure:
  The tool built to stop a false provenance record can produce one, and the
  record it produces erases the evidence: vendoring from `whatever/main` writes
  `source_ref: "main"`, so the manifest asserts core's default branch while the
  bytes came from a ref that a squash-merge (or nothing at all) will delete.
  That is precisely the PR #1 defect, reintroduced inside its own prevention.
  A reviewer reading api/CONTRACT-SOURCE.json is told, by the manifest, that a
  guard checked this. It did not.

  NOTE — what this does NOT mean. The artifact THIS PR ships is correct: I
  verified independently, against my own clone of yegamble/vizra-core, that the
  recorded commit 4a80a1e is core main's tip and that both vendored files are
  byte-identical to core's blobs at it. This finding is about the guarantee the
  new tooling and its documentation offer for the NEXT re-vendor.

  A real compensating control exists and I measured it: the poisoned key in my
  run 3 was caught by `make contract-drift` (exit 2) because the vectors are
  actually consumed — TestVerifierReproducesTheSharedVectors 5/5 and
  TestVerifierRefusesEveryNegativeVector 24/24 went red. So a poisoned KEY does
  not reach main. A poisoned non-normative field, a widened window, or bytes
  from a legitimate-looking fork would not be caught by those tests, and would
  ship with a manifest that says `source_ref: main`.

Perspective:
  developer, operator, instance-admin (the core<->search HMAC boundary is the
  authorization edge between the two services).

Recommendation:
  Three small changes in scripts/vendor-contract.py:
   1. Resolve the ref and require it to be the remote's DEFAULT branch, not a
      name ending in "main": reject if `git rev-parse --verify refs/remotes/<remote>/main`
      does not equal the resolved tip, and reject a ref that resolves to a tag
      (`git cat-file -t <ref>` != "commit" via a branch ref, or check
      `git rev-parse --symbolic-full-name <ref>` starts with `refs/remotes/` or
      `refs/heads/`).
   2. Stop laundering: record the ref as given, or refuse anything that is not
      exactly `<remote>/main`. `m["source_ref"] = args.ref.split("/")[-1]` must
      not turn `fake/main` into `main`.
   3. Verify the checkout is the right repository: `git remote get-url <remote>`
      must name `yegamble/vizra-core` (the value already asserted in
      `source_repository`), or the script must stop printing that line.
  Then correct AGENTS.md:85-86 and api/CONTRACT-SOURCE.json:17-18 to describe
  what the code does. If the ancestor check stays, say it is a transcript
  assertion, not a refusal — or delete it and the dangling `--commit` comment.

Acceptance criteria:
  - `vendor-contract.py --core <checkout> --ref fake/main` exits non-zero,
    naming the ref, on a branch that is not the remote's default branch.
  - The same, for a TAG named `main`.
  - The same, for a checkout whose `origin` is not yegamble/vizra-core.
  - No invocation can write a manifest whose `source_ref` differs from the ref
    actually read.
  - Every sentence in AGENTS.md and $provenance_note describing a refusal is
    backed by a test that shows that refusal firing.

Tests:
  The harness exists. Add a `scripts/testdata/`-style negative-fixture block to
  scripts/revendor-demo.sh, or a small pytest-free python self-test invoked from
  a new `make vendor-contract-selftest`, that builds a throwaway `git init`
  repo, creates a branch `x/main` and a tag `main`, and asserts a non-zero exit
  and the expected message for each. This is the same fixture-floor idiom
  scripts/ci-required-guard.sh already enforces for check-workflows.py, and I
  confirmed that floor works (it fails when the fixture directory is missing or
  empty). It is deliberately NOT a CI lane — CI has no core checkout — but a
  self-test against a `git init` throwaway needs no core checkout at all and
  therefore COULD be one.

Cross-repo implications:
  core: none — core's bytes and main are correct and unaffected.
  user: none.  search: as above.  meta: the chair should not read
  api/CONTRACT-SOURCE.json's $provenance_note as an enforced guarantee until
  this is fixed.

Challenge:
  The strongest counterargument: nobody but a builder ever runs this command,
  `--ref` defaults to `origin/main`, a builder who wants to vendor poisoned
  bytes can simply edit the file, and the vectors are consumed by 29 tests that
  caught my poisoning. So the guard is defence against a mistake, not an
  attacker, and a mistake will almost never produce a branch named `x/main`.
  My answer: the defect is not the bypass, it is the false record. Line 226
  rewrites `source_ref` to "main" unconditionally, so the ONE field a future
  reviewer uses to re-derive provenance is fabricated whenever the ref was not
  literally main — and AGENTS.md plus the manifest both tell that reviewer a
  guard made it true. This repository has already shipped one false provenance
  record (PR #1) and the entire PR is the remediation for it.
```

```
FINDING 2: the vendoring transcript asserts a source repository the script never
           checked, and that transcript is committed as provenance evidence
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/vendor-contract.py:189 (the print), :109-113 (where the value
             comes from), docs/evidence/pr3/revendor-run.txt:32 and :53
  requirements: acceptance 1 (provenance)

Observed:
  vendor-contract.py:189 prints

      print("source repository : %s" % m["source_repository"])

  `m` is api/CONTRACT-SOURCE.json — the script reads that string out of the
  manifest it is about to rewrite. It never asks the checkout what repository it
  is. `grep -n 'remote\|get-url\|fetch' scripts/vendor-contract.py` finds no
  occurrence of any of them.

  I ran the script against a core checkout whose remote I had repointed:

      $ git -C <corefake> remote -v
      origin  https://github.com/attacker/not-vizra-core.git (fetch)
      $ ./scripts/vendor-contract.py --core <corefake> --ref fake/main
      source repository : yegamble/vizra-core      <-- unverified, and false

  The committed evidence file docs/evidence/pr3/revendor-run.txt carries the
  same line twice (:32, :53) as the transcript proving where the bytes came
  from. In this PR the line happens to be true — I verified it independently —
  but the transcript is not what makes it true.

  Related, same root: the script never fetches. `origin/main` is whatever the
  caller's clone last saw, so "it resolves the source commit itself" is bounded
  by the freshness of that clone. This is fail-safe (a stale clone pins an older
  commit that is still genuinely on main, and `--check --core` reports the stale
  pin) so I am not raising it separately.

Failure:
  A provenance transcript restates its own input as if it were a measurement.
  A reviewer checking "did this come from yegamble/vizra-core?" by reading
  revendor-run.txt learns nothing — the answer was copied from the file whose
  correctness is in question.

Perspective:
  developer, operator

Recommendation:
  Print the value the script measured, not the one it was given:
  `git -C <core> remote get-url <remote>`, and die if it does not name
  `yegamble/vizra-core` (a substring match on `yegamble/vizra-core` covers both
  https and ssh spellings). Label the manifest-sourced value explicitly if it is
  kept, e.g. `source repository (manifest, unverified) : ...`.

Acceptance criteria:
  - The transcript line for the source repository is derived from the checkout's
    remote URL, and the run fails when that URL is not yegamble/vizra-core.
  - Re-running the re-vendor regenerates docs/evidence/pr3/revendor-run.txt with
    the measured value.

Tests:
  Same self-test harness proposed in FINDING 1: a throwaway `git init` repo with
  an unrelated `origin` URL must make the command exit non-zero.

Cross-repo implications:
  core: none.  user: none.  search: as above.  meta: none.

Challenge:
  One could argue the manifest's `source_repository` is itself owner-reviewed
  (CODEOWNERS covers /api/), so trusting it is legitimate and this is cosmetic.
  Fair for the manifest; not for the transcript, whose whole job is to be an
  independent record. And the fix is three lines.
```

```
FINDING 3: an absolute home-directory path is committed in the evidence
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     docs/evidence/pr3/provenance.txt:7
  requirements: none

Observed:
  `grep -rnoE '/Users/[a-z]+' docs/evidence/pr3/` returns exactly one hit,
  `docs/evidence/pr3/provenance.txt:7`, carrying the operator's home path and
  therefore their local username. No credential, token, key or private URL is
  present anywhere in the new files — I scanned for gh[pousr]_ tokens,
  github_pat_, Bearer headers, AKIA keys, PEM private keys, Authorization:,
  x-access-token, password= and SEARCH_HMAC_KEY=<value> across
  docs/evidence/pr3/ and both new scripts, with no match.

Failure:
  Trivial information disclosure in a repository that may become public. The
  username is already the GitHub account name, so the marginal leak is ~zero.

Perspective:
  developer

Recommendation:
  Replace with a placeholder on the next touch of that file. Not worth a commit
  of its own.

Acceptance criteria:
  No absolute home path under docs/evidence/.

Tests:
  A grep in the existing evidence-hygiene idiom, if one is ever added. None
  today.

Cross-repo implications:
  core: none.  user: none.  search: as above.  meta: none.

Challenge:
  Not worth the reviewer's attention at all — which is why it is a NIT and does
  not affect the verdict.
```

---

## Verdict

Everything the slice was asked to demonstrate, I reproduced myself, from my own clones, with my
own mutations:

| acceptance | result |
|---|---|
| 1 — re-vendored through the repo's own command; `source_commit` is on core `main`; every vendored file's digest equals core main's bytes | **reproduced.** `4a80a1e` is core main's tip and the last `api/` commit on it; both files match core's blobs `848503cc…` / `1509da85…` exactly; `vendor-contract-check` exit 0 |
| 2 — pre-re-vendor red by name; post-re-vendor green; one-byte edit reddens `make contract-drift` AND `make ci` by name on both files; restore → green | **reproduced**, with my own anchors, digests recorded at every step, tree clean after every restore |
| 3 — 5 ACCEPT + 24 REJECT vectors consumed; counts and skips recorded | **reproduced.** 5/5 and 24/24 named subtests pass; 347 pass / **0 skip** / 0 fail, counted by me from `go test -json`, and no `t.Skip` or build-tag exclusion exists in the tree |
| 4 — no other change | **reproduced.** No `.github/` file, no guard script, no required-checks edit, no `*.go` file, no `VIZRA_SEARCH_MODE`/`VIZRA_MODE` rename. Makefile change is a pure append; `ci:` is byte-unchanged |
| CI | **`ci-required` green on `aa1c3fb7…`**; all 10 manifest lanes present as completed successful check runs; merge tree byte-identical to the head tree |

Against that, FINDING 1 is a REQUIRED-severity defect in **new tooling placed in the
contract-provenance path**, and its consequence is written into two owner-reviewed files — the
engineering contract (`AGENTS.md:85-86`) and the provenance record itself
(`api/CONTRACT-SOURCE.json:17-18`). Both state that the script refuses a `--ref` that is not
`main`; I demonstrated two refs it accepts, and demonstrated that the manifest it then writes
records `source_ref: "main"` regardless. Under the precedent set at
`docs/evidence/warroom/2026-09-20-vizra-search-pr2-revendor-VERIFY.md` — where "a guard the lane
relies on that does not actually guard" was rated REQUIRED and drove a FAIL — this blocks.

I want the chair to weigh one thing explicitly: **the artifact is right and the tool is wrong.**
The vendored bytes, the pin and every lane are correct and independently confirmed; nothing here
suggests re-doing the re-vendor. The fix is bounded — tighten one guard, delete one laundering
assignment, correct two sentences, and add the negative fixtures for the refusals — and it does not
touch `api/`, so the provenance I verified above carries forward unchanged to the fix commit.

FINDING 2 (SHOULD) and FINDING 3 (NIT) are reported for completeness and do not drive the verdict.

FINAL VERDICT: FAIL — SHA aa1c3fb7…

---
---

# Re-verification at `2997e64` — 2026-09-21 (fix round 1 of 2)

**SHA verified:** `2997e6427abd5de6c09d5855d4fd8577b1b591c9`
**History:** `581bffc` → `aa1c3fb` (my FAIL) → `2997e64`. I confirmed **no force-push**:
`git merge-base --is-ancestor aa1c3fb 2997e64` exits 0, and `2997e64`'s parent is `aa1c3fb`.
**Branch head at the end of this re-verification:** `2997e64…` — unmoved.
**Fresh clone**, new private `mktemp -d` (`…/scratchpad/vzv-s3rv2-AAmKgY/`), deleted at the end.
The working trees `/Users/yosefgamble/github/vizra/vizra-core` and `…/vizra-search` were never
touched; the adversarial core checkouts below are **copies** made inside my own scratch dir.
Same environment as §0 (Darwin arm64, go1.27.1, GNU Make 3.81, python3 3.9.6).

## R1. My two bypasses, re-run verbatim — both REFUSED

I rebuilt the exact adversarial `vizra-core` checkout from round 1: a branch `fake/main` whose
`api/search-hmac-testvectors.json` has `key_utf8` replaced with
`ATTACKERKEYATTACKERKEYATTACKER12`, plus a tag `main` and a tag `origin/main` on that poisoned
commit. Manifest sha256 recorded before each attempt and compared after.

| attempt | round 1 | **round 2 (this SHA)** | manifest | poisoned bytes vendored |
|---|---|---|---|---|
| `--ref main` (tag named `main`) | **ACCEPTED, exit 0** | **REFUSED, exit 1** — `--ref 'main' resolves to refs/tags/main, not refs/remotes/origin/main` + `('main' is ambiguous; it also matches refs/heads/main)` | untouched | 0 |
| `--ref fake/main` (poisoned branch) | **ACCEPTED, exit 0** | **REFUSED, exit 1** — `resolves to refs/heads/fake/main, not refs/remotes/origin/main` | untouched | 0 |
| `--ref refs/tags/main` | — | **REFUSED**, names both refs | untouched | 0 |
| `--ref refs/heads/fake/main` | — | **REFUSED**, names both refs | untouched | 0 |
| `--ref origin/main` while a **tag** `origin/main` shadows the remote-tracking ref | — | **REFUSED** — `resolves to refs/tags/origin/main` + `(ambiguous; it also matches refs/remotes/origin/main)`. git itself warns `refname 'origin/main' is ambiguous` here, so the resolver reproduces git's real precedence | untouched | 0 |

Every refusal names the ref it resolved, the ref it wanted, and every other ref that matched. On
refusal the manifest is byte-identical — the tool dies before writing anything.
**FINDING 1's bypass is closed.**

## R2. Attacking the NEW resolver the way I found the old hole

Adversarial checkouts built in my scratch dir. `try()` recorded the manifest digest before and
after each run.

### Refs, and argv injection

| attack | result |
|---|---|
| `--ref refs/remotes/origin/HEAD` | **REFUSED** — `resolves to refs/remotes/origin/HEAD, not …/main` |
| `--ref origin/HEAD` | **REFUSED** — same |
| `--ref=--upload-pack=/bin/echo` | **REFUSED** — `does not name any ref` |
| `--ref=+refs/heads/main` | **REFUSED** — `does not name any ref` |
| `--ref 'origin/main^'`, `'origin/main@{1}'`, `'origin/main..HEAD'`, `'../../etc/passwd'` | **REFUSED** — all `does not name any ref` |
| `--remote=--upload-pack=x` | **REFUSED** — `has no remote '--upload-pack=x' (git remote get-url exit 129)` |
| `--commit=--output=/tmp/pwn` | **REFUSED**; `/tmp/pwn` was not created |

No argv injection is reachable: the `--ref` string is now only ever a **dict key** looked up
against `git for-each-ref` output — it is never passed to git at all. The only ref that reaches a
git command is the constructed `refs/remotes/<remote>/main`. `--remote` and `--commit` reach git
as argv elements and git rejects option-shaped values with a non-zero exit, which the script dies
on. No `shell=True`, `os.system` or `os.popen` anywhere.

### Remote name vs remote URL

Built a checkout with **two** remotes: `origin` → `https://github.com/attacker/vizra-core.git`,
`upstream` → the canonical URL, with `refs/remotes/upstream/main` present.

| attack | result |
|---|---|
| `--remote origin` (canonical *name*, fork *URL*) | **REFUSED** — `remote 'origin' of … is https://github.com/attacker/vizra-core.git which is github.com/attacker/vizra-core, not github.com/yegamble/vizra-core` |
| `--remote upstream` (non-default *name*, canonical *URL*) | **ACCEPTED**, and honestly records `source_ref: refs/remotes/upstream/main` — the refname it actually resolved, not a normalised fiction |

The name is no longer load-bearing; the URL is measured and the recorded ref is the resolved one.

### `--commit`

| attack | result |
|---|---|
| `--commit <ancestor of main that does NOT touch api/>` (`c043df72…`) | **ACCEPTED.** It vendors **that commit's** api bytes — I verified `git show c043df72:api/search-hmac-testvectors.json \| shasum` equals the file on disk (`ff21e6b8…`) — records `source_commit: c043df72…` **and** `source_ref_tip: 4a80a1e…`, so the manifest distinguishes the pinned commit from the ref tip. Honest. `--check --core` then flags it: `the manifest pins c043df72…, but the current last api/ commit on refs/remotes/origin/main is 4a80a1e… — re-vendor` |
| `--commit <the poisoned fake/main commit>` with `--ref refs/remotes/origin/main` | **REFUSED** — `commit 38d0ce99… is NOT an ancestor of refs/remotes/origin/main` |

The ancestry refusal is now reachable and real, rather than the decorative check I flagged.

### A stale / rewound `refs/remotes/origin/main`

I rewound `refs/remotes/origin/main` to the real earlier commit `415a6d19…`. The tool **accepts**
and records `source_ref_tip: 415a6d19…`, `source_commit: 415a6d19…`. That is honest — the field
is named "the tip that refname pointed at", and it pointed there. It does not fetch, which
AGENTS.md, the docstring and `$provenance_note` all now state explicitly. `--check --core` against
a *fresh* clone catches it: `the manifest pins 415a6d19…, but the current last api/ commit … is
4a80a1e… — re-vendor`.

### `insteadOf` rewrites — handled correctly, and I had expected a hole here

`git remote get-url` **does** apply `url.<base>.insteadOf`, so it reports the URL git would
actually use, not the raw config string. Both directions behave right:

| config | `get-url` reports | tool |
|---|---|---|
| remote = `attacker/vizra-core`, `insteadOf` rewriting it to the canonical URL | canonical | **ACCEPTED** — correct: that clone really does fetch from `yegamble/vizra-core` |
| remote = canonical, `insteadOf` rewriting it to `evil.example` | `https://evil.example/x.git` | **REFUSED** — correct: that clone really fetches from evil.example |

Measuring the *effective* URL is the right choice and it is what the code does.

### URL normalisation — 19 URLs through the real `parse_remote_url` / `redact_url`

| URL | expected | observed |
|---|---|---|
| `https://github.com/yegamble/vizra-core[.git][/]` | accept | **accept** |
| `https://GitHub.COM/YeGamble/Vizra-Core.git` (mixed case) | accept | **accept** (host and owner/repo both lower-cased) |
| `git@github.com:yegamble/vizra-core[.git]` (scp-like) | accept | **accept** |
| `ssh://git@github.com[:22]/yegamble/vizra-core.git` | accept | **accept** |
| `https://x-access-token:ghp_…@github.com/yegamble/vizra-core.git` | accept, redacted | **accept**, printed as `https://***@github.com/…` |
| `https://github.com.evil.example/yegamble/vizra-core.git` | refuse | **refuse** (host `github.com.evil.example`) |
| `https://evil.example/github.com/yegamble/vizra-core` | refuse | **refuse** (host `evil.example`) |
| `git@github.com.evil.example:yegamble/vizra-core` | refuse | **refuse** |
| `https://github.com/attacker/vizra-core.git` | refuse | **refuse** |
| `https://github.com/yegamble/vizra-user.git` | refuse | **refuse** |
| `https://gitlab.com/yegamble/vizra-core.git` | refuse | **refuse** |
| `https://github.com/yegamble/vizra-core.git.evil` | refuse | **refuse** |
| `/local/path/vizra-core`, `file:///tmp/vizra-core` | refuse | **refuse** |
| `https://github.com/attacker/x/yegamble/vizra-core` | refuse | **accept** — see FINDING 6 (NIT) |

**Token redaction, end to end.** I set a core clone's origin to
`https://x-access-token:ghp_SECRETTOKEN…@github.com/yegamble/vizra-core.git` and ran a real vendor
and a real `--check --core`:

- occurrences of the token in stdout+stderr: **0** in both paths;
- occurrences in `api/CONTRACT-SOURCE.json`: **0** — the manifest stores `source_repository`
  (`yegamble/vizra-core`), the *parsed* owner/repo, never the URL;
- printed line: `remote origin     : https://***@github.com/yegamble/vizra-core.git   [measured: git remote get-url]`.

**FINDING 2 is closed**, and the "measured, not restated" property is now visible in the transcript
itself.

## R3. `--check` against a hand-edited manifest (the chair's item 2)

I hand-edited one field at a time and ran all three controls. This is the honest picture:

| field forged to | `--check` | `--check --core` | `make contract-drift` (the CI lane) |
|---|---|---|---|
| `source_ref` = `refs/remotes/origin/evil` | 0 (missed) | **1** — `the manifest records source_ref 'refs/remotes/origin/evil', but this checkout resolves 'refs/remotes/origin/main'` | 0 (missed) |
| `source_ref` = `main` | **1** — `it must be the FULL refname … not a short name a caller could have laundered` | **1** | 0 (missed) |
| `source_ref` = 40 zeros | **1** | **1** | 0 (missed) |
| **`source_ref_tip` = `refs/remotes/origin/evil`** | **0** | **0** | **0** |
| **`source_ref_tip` = `main`** | **0** | **0** | **0** |
| **`source_ref_tip` = 40 zeros** | **0** | **0** | **0** |

`source_ref_tip` is **write-only**: nothing validates it, not even `--check --core`, which already
holds the correct value in a local variable. See FINDING 4 (SHOULD). No document claims it is
validated, so this is a gap rather than an over-promise.

`contract-drift` — the only one of the three that runs in CI — validates `source_repository`,
`source_commit`'s length and the two digests, and no other provenance field. AGENTS.md describes it
exactly that way ("fails on any drift between the vendored bytes and the manifest"), so that is
accurate.

## R4. Claims audit (the chair's item 3)

I checked every remaining refusal claim against the code and against a fired fixture.

| claim (AGENTS.md / docstring / `$provenance_note`) | true? |
|---|---|
| "`git remote get-url` is **measured** … must be `github.com/yegamble/vizra-core`" | **true** — R2 |
| "normalised across https / ssh / scp-like / userinfo forms" | **true** — 19-URL battery |
| "the ref is resolved to a **full refname** and must equal `refs/remotes/<remote>/main` exactly" | **true** — R1, R2 |
| "a tag named `main`, a tag named `origin/main` shadowing the remote-tracking ref, `refs/heads/main`, and any branch `x/main` all resolve elsewhere and are named in the refusal" | **true** — all four reproduced, each names both refs |
| "`merge-base --is-ancestor <commit> refs/remotes/<remote>/main`, checked against the **resolved** ref … Reachable via `--commit`" | **true** — `--commit` exists and the refusal fires |
| "a shallow clone is refused" | **true** — fixture fires; message names `fetch --unshallow` |
| "the manifest records the full refname **resolved** and the tip it pointed at. No string derived from `--ref` is ever written" | **true** — `--remote upstream` records `refs/remotes/upstream/main`; the laundering line is gone |
| "It only ever reads the core checkout (`remote get-url`, `rev-parse`, `for-each-ref`, `log`, `merge-base`, `show`)" | **true** — that is the complete set of git subcommands in the file |
| "userinfo is redacted before printing, because a remote URL can carry a token" | **true** — end-to-end check, 0 occurrences in either path and in the manifest |
| "**It defends against a mistake, not against someone who controls the checkout it is pointed at**, and it does not authenticate core's bytes" | **true, and this is the sentence that matters.** It appears in AGENTS.md, in the script docstring, and in `api/CONTRACT-SOURCE.json`'s `$provenance_note` — the provenance record now carries its own limit |
| "a poisoned *non-normative* field would not be caught by those tests" | **true** — matches what I measured in round 1, where a poisoned *key* was caught by the 29 consumed vectors |
| AGENTS.md's explicit retraction: "An earlier version of this section claimed … The first half could not fire and the second was a string-suffix test that an independent verifier walked past twice." | **accurate** |

The one over-promising sentence I found is **not** in an authoritative file — it is a stale
paragraph left standing in the **PR description** (see FINDING 5, NIT).

**The builder's stated residual — is it said at the right strength?** AGENTS.md says
`vendor-contract-selftest` "needs neither a core checkout nor a network and therefore could be
[a CI lane]; that is proposed to the chair rather than done here", and the Makefile comment and PR
body say the same. That is honest about the fact. It stops just short of naming the consequence —
*nothing in CI notices if a future edit deletes a refusal*. There is a real local floor
(`EXPECTED_CASES = 11`), which I fired by deleting one case from the registry:
`10 case(s) registered, the floor is 11. A refusal lost its fixture.` (exit 1). But that floor only
runs when someone runs it. I record this as an accurate-but-incomplete statement, not an
over-promise, and leave the lane decision to the chair, which is where the builder put it.

## R5. Negative fixtures and the D-G demonstration

`make vendor-contract-selftest` — **exit 0, 11/11**, every adversarial repository built with
`git init` in a temp dir:

```
tag named 'main' OK | tag shadowing origin/main OK | branch 'fake/main' OK
local branch refs/heads/main OK | non-ancestor --commit OK | foreign origin URL OK
foreign origin (scp-like ssh) OK | userinfo redacted in output OK
no refs/remotes/origin/main OK | shallow clone OK | happy path accepted OK
vendor-contract-selftest: all 11 fixtures behaved as documented
```

**No network — tested, not asserted.** With `http_proxy=https_proxy=ALL_PROXY=http://127.0.0.1:1`,
`GIT_TERMINAL_PROMPT=0` and `GIT_SSH_COMMAND=/usr/bin/false`: **exit 0, 11/11**. Nothing left
behind: `git status --porcelain` empty, no stray `vendor-contract-selftest-*` or
`revendor-demo-pristine-*` directory.

I also ran it with `GIT_ALLOW_PROTOCOL=none`, which blocks the **local `file://` transport** the
shallow-clone fixture uses to build a real shallow clone offline. That is stricter than "no
network" and is not a fair test of the claim — but the result is worth recording because it is the
*right* failure mode: the harness reported
`FAIL: case_shallow_clone raised RuntimeError: could not build a shallow clone` and exited 2,
rather than counting the unrunnable fixture as a pass. A fixture that cannot run is not a pass,
which is exactly what AGENTS.md demands.

**D-G** (`docs/evidence/pr3/D-G-guard-fixtures-red-green.txt`) applies the PR's own mutation
discipline to the guard: the script's sha256 is recorded before and after reverting the resolver to
the suffix test (`1fe2773d…` → `3b067f75…` → `1fe2773d…`), the patched region is printed, and the
transcript shows the reverted guard vendoring from `refs/tags/main`, `refs/tags/origin/main`,
`refs/heads/fake/main` (the poisoned commit) and `refs/heads/main`. `0 unexpected results`. I read
the transcript and it is internally consistent with the code at this SHA; the fixtures I ran myself
reproduce its state-0 and state-2 rows exactly.

## R6. Pins and artifact (the chair's item 4)

| claim | verified |
|---|---|
| both vendored files byte-identical to `aa1c3fb` | **yes** — blob ids identical at both commits: `848503cc…`, `1509da85…` |
| both byte-identical to core `main@4a80a1e` | **yes** — `a78d8aa7…` / `f95623b0…` on both sides, from my own core clone |
| `git diff --name-only aa1c3fb 2997e64 -- api/` lists only the manifest | **yes** |
| manifest digests still match | **yes** — `make vendor-contract-check` exit 0 |
| `source_commit` still `4a80a1e…` | **yes**; `source_ref` is now the full refname `refs/remotes/origin/main` and `source_ref_tip` `4a80a1e…` |
| the manifest is not in its own `files` array, so no digest covers it | **yes** — confirmed; it was regenerated *through* the fixed tool (`--note`), not hand-edited |
| 5 ACCEPT + 24 REJECT, 0 skips | **yes** — my own `go test -json` parse: `ACCEPT 5 REJECT 24 | pass 347 skip 0 fail 0` |
| one-byte edit still reddens both lanes by name | **yes** — `Generate a real key with` → `real kez with` (file still parses as JSON): `make contract-drift` exit 2 and `make ci` exit 2, both printing `contract_drift_test.go:106: the vendored api/search-hmac-testvectors.json does not match its manifest` and `CONTRACT-DRIFT LANE REFUSED: 1 test(s) failed: …TestEveryVendoredFileMatchesItsManifest`; restore → `make ci` exit 0 |

## R7. Lanes and scope (items 5)

| lane | exit | evidence |
|---|---|---|
| `make ci` | **0** | `contract-drift: 324 tests ran across 4 package(s), 0 failures, none deselected`; `test-noskip: 347 pass events, 0 skips`; `tidy-check: tidy` |
| `make vendor-contract-check` | **0** | both files OK |
| `make vendor-contract-selftest` | **0** | 11/11, also with the network blocked |
| `./scripts/ci-required-guard.sh` | **0** | |
| `./scripts/check-workflows.py` | **0** | |
| `docker-build` | **not runnable locally** (arm64 host / amd64 target) — green in CI on this SHA |

Scope vs `origin/main` — 15 files, and the only non-evidence, non-script files are the same four:

```
M AGENTS.md   M Makefile   M api/CONTRACT-SOURCE.json   M api/search-hmac-testvectors.json
A scripts/vendor-contract.py   A scripts/vendor-contract-selftest.py   A scripts/revendor-demo.sh
A docs/evidence/pr3/*  (8 files)
```

- `git diff --stat origin/main...2997e64 -- .github/` → **empty**. No workflow, no
  `required-checks.txt`, no CODEOWNERS, no guard script.
- `git diff --name-only origin/main...2997e64 -- '*.go'` → **empty**. No production code, no test.
- `VIZRA_SEARCH_MODE` / `VIZRA_MODE` in the whole diff: **0 occurrences**.
- **Make integrity:** `git diff --unified=0 origin/main...2997e64 -- Makefile` contains **no `-`
  lines** — still a pure append. `ci:` is byte-identical at the same line 33 in both trees:
  `ci: fmt-check vet echo-containment build contract-drift test test-noskip tidy-check`.
  No lane reordered, renamed or removed; no `SHELL`/`.SHELLFLAGS`/`MAKEFLAGS`.
- Hygiene: `grep -rnoE '/Users/[a-z]+' docs/evidence/pr3/ scripts/` → **no match** (FINDING 3
  closed). No token, PAT, AWS key or private key anywhere in the new files.

## R8. CI on `2997e64` (item 6)

My own `gh` calls:

```
$ gh api repos/yegamble/vizra-search/commits/2997e6427abd5de6c09d5855d4fd8577b1b591c9/check-runs
total_count = 12 ; unique conclusions = ["success"]
```

All 10 names in `.github/required-checks.txt` — `fmt, vet, echo-containment, build, contract-drift,
test, test-noskip, tidy-check, govulncheck, docker-build` — are present as **completed, successful**
check runs on this SHA, plus `ci-required` (success) and GitGuardian (success). No listed lane is
missing, skipped, cancelled or never-executed. `ci` run 35575111391 and `ci-required` run
35575111453, both `head_sha = 2997e64…`, both `success`.

**Which tree CI tested:** the `pull_request` event, so the merge commit — parents
`808a5499…` (current `main`) and `2997e64…`. Its tree is **byte-identical** to the head tree:

```
tree(2997e64)          = 18fb147f207c2e92557477d51b00047add167e72
tree(refs/pull/3/merge)= 18fb147f207c2e92557477d51b00047add167e72
```

## Findings at `2997e64`

**Round-1 findings: FINDING 1 (REQUIRED) — CLOSED. FINDING 2 (SHOULD) — CLOSED. FINDING 3 (NIT) — CLOSED.**
Each closure is reproduced above by me, not read from a transcript.

```
FINDING 4: source_ref_tip is recorded as provenance and validated by nothing
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/vendor-contract.py:447 (written), :487 (printed, not compared),
             :512-540 (--check --core, where `tip` is in hand and unused),
             internal/httpapi/contract_drift_test.go:34-36 (the struct has no field for it)
  requirements: acceptance 1 (provenance)

Observed:
  The fix adds `source_ref_tip` to api/CONTRACT-SOURCE.json. I hand-edited it to
  `refs/remotes/origin/evil`, to `main`, and to 40 zeros. In every case:
  `vendor-contract.py --check` exit 0; `--check --core <real core clone>` exit 0;
  `make contract-drift` exit 0. Nothing anywhere notices.

  `--check --core` already computes the correct value — resolve_ref returns
  (full_ref, tip) at :518 — and compares `full_ref` and `commit`, but never
  `tip`. The Go manifest test does not unmarshal the field at all.

  No document claims it IS validated, so this is a gap rather than a repeat of
  FINDING 1. It is the same *class* though: a provenance field a later hand-edit
  can falsify silently.

Failure:
  A reviewer re-deriving provenance from the manifest reads a tip that no control
  has ever checked. It is the one new provenance field the fix introduced and the
  only one with no verification path.

Perspective:
  developer, operator

Recommendation:
  One line in check(), inside the `if args.core:` block that already has `tip`:
  compare `tip` against `m.get("source_ref_tip")` and append a problem naming
  both. Optionally also require it to be 40 hex characters in the no-core path,
  the way source_commit already is at :472.

Acceptance criteria:
  - `--check --core` exits non-zero when source_ref_tip differs from the tip the
    resolved ref points at, naming both values.
  - `--check` (no core) exits non-zero when source_ref_tip is not a 40-character
    SHA.
  - A selftest fixture fires each of those.

Tests:
  scripts/vendor-contract-selftest.py, as a 12th case (raise EXPECTED_CASES to
  12): build the happy-path repo, vendor, corrupt source_ref_tip, assert
  `--check --core` exits non-zero and names the field.

Cross-repo implications:
  core: none.  user: none.  search: as above.  meta: none.

Challenge:
  It is a belt-and-braces field — source_commit is the one that matters and it IS
  checked three ways, so a forged tip misleads nobody who checks the commit. True,
  which is why this is SHOULD and not REQUIRED. But the field was added precisely
  so a reviewer could re-derive provenance without a core checkout, and an
  unvalidated field does not do that.
```

```
FINDING 5: a superseded paragraph in the PR description still asserts the guard
           that was retracted
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     PR #3 description, section "## The vendoring command (new)"
             (the authoritative files are correct — AGENTS.md:73-130,
             scripts/vendor-contract.py:18-67, api/CONTRACT-SOURCE.json:11-26)
  requirements: none

Observed:
  The PR body still reads, in the original section:

    "It resolves the source commit itself, **refuses** a commit that is not an
     ancestor of the branch tip and a `--ref` that is not a `main` branch, and
     digests the bytes it reads back off disk after writing them. It only ever
     reads the core checkout (`rev-parse`, `log`, `merge-base`, `show`) ..."

  At this SHA that sentence is wrong in two directions: there is no `main`-branch
  suffix test any more (the requirement is the exact full refname, which is
  stronger), and the git subcommand list is now missing `remote get-url` and
  `for-each-ref`. It also omits the remote-URL refusal entirely.

  The later "Fix round 1" section describes the real behaviour accurately, and
  AGENTS.md carries an explicit retraction of this exact sentence. So the
  authoritative documents are right and only the narrative is stale.

Failure:
  A chair reading the PR top to bottom meets a description of a control that no
  longer exists as described before reaching the correction.

Perspective:
  developer

Recommendation:
  Edit that paragraph in the PR body to point at the "Fix round 1" section, or
  delete it. No code change.

Acceptance criteria:
  No sentence in the PR description describes a refusal that the code at the head
  SHA does not implement as written.

Tests:
  None — prose.

Cross-repo implications:
  core: none.  user: none.  search: as above.  meta: none.

Challenge:
  PR bodies are narratives of a PR's history and the fix section explicitly
  supersedes it, so "correcting" history is arguably worse. Fair — which is why
  this is a NIT and does not affect the verdict; a one-line "superseded by Fix
  round 1 below" is enough.
```

```
FINDING 6: the remote-URL matcher takes the last two path segments, so a deeper
           path under github.com is accepted
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     scripts/vendor-contract.py:175-178 (`parts[-2:]`)

Observed:
  `parse_remote_url("https://github.com/attacker/x/yegamble/vizra-core")` returns
  `("github.com", "yegamble/vizra-core")` and is ACCEPTED. Every other URL in my
  19-case battery behaves correctly, including the host-confusion cases
  (`github.com.evil.example`, `evil.example/github.com/...`) and every ssh /
  scp-like / userinfo / trailing-slash / mixed-case form.

Failure:
  Essentially none in practice: github.com does not serve repositories at
  four-segment paths, so a clone from such a URL could not have fetched core's
  objects in the first place, and the documented LIMIT ("a local clone's remote
  URL is whatever its owner set it to") already covers a hand-set URL. It is a
  looser match than the check advertises ("must be github.com/yegamble/vizra-core").

Perspective:
  developer

Recommendation:
  Require exactly two path segments: `if len(parts) != 2: return host, None`.

Acceptance criteria:
  A remote URL with more than two path segments under github.com is refused.

Tests:
  One more assertion in the existing case_foreign_origin fixture family.

Cross-repo implications:
  core: none.  user: none.  search: as above.  meta: none.

Challenge:
  Unreachable in practice and the fix is a one-line tightening that could in
  principle break a legitimate enterprise-GitHub path layout. Hence NIT.
```

## Verdict at `2997e64`

The blocking finding is fixed **in the control, not in the prose** — which is the distinction I
asked for. Both of my round-1 bypasses are refused by name with the manifest untouched, and so are
nine further attacks I had not tried before (tag shadowing, `refs/remotes/origin/HEAD`, four
argv-injection shapes, fork-URL-under-the-name-`origin`, non-ancestor `--commit`, shallow clone).
The remote is measured rather than restated, normalisation survives a 19-URL battery including the
host-confusion cases, and a token in the remote URL reaches neither stdout nor the manifest in
either code path. The manifest no longer launders anything: it records the resolved refname, and
`--remote upstream` proves it by recording `refs/remotes/upstream/main`.

The refusals are backed by 11 fixtures that I ran myself, that pass with the network blocked, that
leave nothing behind, and that fail loudly rather than silently when a fixture cannot run. The
`EXPECTED_CASES` floor fires when a fixture is deleted — I fired it.

Most importantly for a provenance artifact: AGENTS.md, the script's docstring and the manifest's
own `$provenance_note` now all carry the limit — *"it defends against a mistake, not against
someone who controls the checkout it is pointed at"*, and *"it does not authenticate core's
bytes"*. That is the honest statement of what a local-clone check can and cannot prove, written
into the record a future reviewer will read.

The artifact is untouched and still correct: both vendored files are byte-identical to `aa1c3fb`
and to core `main@4a80a1e`, `source_commit` is unchanged, 5/5 + 24/24 vectors pass with 0 skips,
and a one-byte edit still reddens `make contract-drift` and `make ci` by name. Scope is clean, the
Makefile is still a pure append with `ci:` byte-identical, and `ci-required` plus all 10 manifest
lanes are green on this SHA against a merge tree byte-identical to the head tree.

FINDING 4 (SHOULD), 5 (NIT) and 6 (NIT) are real but none is blocking: FINDING 4 is a gap in a
belt-and-braces field that no document claims is checked, and 5 and 6 are cosmetic. All three are
one-line fixes the chair may fold into fix round 2 or schedule separately.

FINAL VERDICT: PASS — SHA 2997e642…
