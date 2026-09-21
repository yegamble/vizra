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
