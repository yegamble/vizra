# Independent verification — vizra-search PR #4, "the runtime mode is `VIZRA_MODE`"

- **Repo / PR:** `yegamble/vizra-search` — https://github.com/yegamble/vizra-search/pull/4
- **SHA verified:** `852b38291c3ec8109f27ebd924ef48eec3b11a9d` (branch `chore/m0-vizra-mode-rename`)
- **Head re-checked at start and at end of this run:** unchanged, still `852b3829…`
- **Base:** `3619fed873fc194130f02cc85577de10414ade39` — 14 files, +1333 −9
- **Verifier:** `vizra-verifier`, did not write any of this code
- **Date:** 2026-09-21

## Environment

| | |
|---|---|
| Host | darwin/arm64 (Darwin 25.5.0), Apple silicon; **no amd64 emulation attempted** |
| Go | `go1.26.2 darwin/arm64` (repo CI pins `GO_VERSION: 1.27.1`) |
| Docker | server 29.8.0 — used only to read the CI log, no local image build |
| Clone | fresh `git clone` into a private `mktemp -d` scratch directory; **never** the builder's checkout |
| Tree state | `git status --porcelain` empty before, between and after every experiment |

Scratch directory created with `mktemp -d "$SCRATCH/vzv-search-pr4-XXXXXX"` and removed at
the end. No shared path, container or image was touched.

---

## 1. Lanes run from the clean clone

| Command | Exit | Result I measured |
|---|---|---|
| `make ci` | **0** | fmt-check clean; vet clean; echo-containment clean; build ok; **contract-drift 346 tests / 4 packages / 0 deselected**; `go test -race -count=1 ./...` 6 packages ok; **test-noskip 371 pass events, 0 skips**; tidy-check tidy |
| `go test -count=1 -json ./...` (my own count) | **0** | `"Action":"pass"` × **371**, `"Action":"skip"` × **0**, `"Action":"fail"` × **0** |
| `grep -rn 't\.Skip\|testing.Short()'` over the tree | — | **no match** — zero skips are structural, not incidental |
| `govulncheck ./...` | **0** | No vulnerabilities found |
| `./scripts/ci-required-guard.sh` | **0** | floor intact; workflow anchor present; manifest entries bare job names; every required check defined by a job; base images pinned by digest; 6 workflow fixtures exercised (floor 6) |
| `python3 scripts/check-workflows.py .github/workflows/*.yml` | **0** | 2 workflows parsed, no `continue-on-error` on any job or step |
| `shellcheck scripts/boot-matrix.sh` | **0** | clean |
| `./scripts/boot-matrix.sh` | **0** | 14 passed, 0 failed (13 boot cases + the focused suite) |

Every number in the PR body's lane table reproduced **exactly** (346/4/0, 371/0, 6 fixtures).

### Diff hygiene

- `git diff --numstat 3619fed..852b382` on `*_test.go`: `50 0` and `203 0` — **zero deleted
  test lines**. No assertion weakened, no case removed, no skip introduced.
- 11 new test functions added (`TestTheRuntimeModeIsReadFromVizraMode`,
  `TestTheOldRuntimeModeNameIsRefusedByName`, `TestTheOldNameAloneNeverSilentlySelectsAMode`,
  `TestTheOldRuntimeModeNameIsRefusedInDevelopmentToo`, `TestATopologyValueInTheOldNameIsIgnored`,
  `TestANonVocabularyValueInTheOldNameIsRefused`, `TestAnEmptyOldNameIsToleratedAsATombstone`,
  `TestTheOldNameIsConsultedOnlyByTheRefusal`, `TestTheTopologyVocabularyIsPinnedToCore`,
  `TestBootRefusesTheRetiredRuntimeModeName`, `TestBootAcceptsCoreTopologyAlongsideTheRuntimeMode`).
- `api/`, vendored contract files and HMAC vectors: **not in the diff at all**.
- `scripts/ci-required-guard.sh`, `scripts/check-workflows.py`, `.github/required-checks.txt`:
  **not in the diff** — unedited.
- `Makefile` `ci:` target line is byte-identical to base; the only Makefile changes are the
  `run` target's env rename and a new, unwired `boot-matrix` target.

---

## 2. My own boot matrix — 84 combinations on the REAL binary

I built the binary from the clean clone (`go build ./cmd/vizra-search`) and ran my own
harness **before** reading the builder's transcripts.

**Mode is proven from observable behaviour, never from a log line.** Each combination is
booted twice:

- with a **strong** key (`openssl rand -hex 32`) → does it boot at all?
- with the **published development key** `dev-insecure-hmac-key-do-not-use-in-production` →
  accepted ⇒ the process really is in `development`; refused ⇒ it really is in `production`.

A process still alive after 2.5 s is recorded as `BOOTED` and killed. `env -i` was used so
nothing leaked in from my shell. The garbage value is the marker `zzmarker7391garbage` so
that any echo of a supplied value is greppable.

Independent confirmation that `BOOTED` means *serving*: `VIZRA_MODE=development` +
dev key → `GET /readyz` returned **200** over real TCP, and the startup log line is
`"running in development mode"` with `"hmac_key":"[redacted]"`.

| # | VIZRA_MODE | VIZRA_SEARCH_MODE | strong key | dev key | observed mode | exit | refusal names VIZRA_MODE | refusal names VIZRA_SEARCH_MODE | echoes a supplied value |
|---|---|---|---|---|---|---|---|---|---|
| 1 | <unset> | <unset> | BOOTED | EXIT:1 | production | - | - | - | - |
| 2 | <unset> | <empty> | BOOTED | EXIT:1 | production | - | - | - | - |
| 3 | <unset> | 'development' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 4 | <unset> | 'production' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 5 | <unset> | 'DEVELOPMENT' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 6 | <unset> | ' development ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 7 | <unset> | 'off' | BOOTED | EXIT:1 | production | - | - | - | - |
| 8 | <unset> | 'managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 9 | <unset> | 'external' | BOOTED | EXIT:1 | production | - | - | - | - |
| 10 | <unset> | 'Managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 11 | <unset> | 'zzmarker7391garbage' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 12 | <unset> | '   ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 13 | <empty> | <unset> | BOOTED | EXIT:1 | production | - | - | - | - |
| 14 | <empty> | <empty> | BOOTED | EXIT:1 | production | - | - | - | - |
| 15 | <empty> | 'development' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 16 | <empty> | 'production' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 17 | <empty> | 'DEVELOPMENT' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 18 | <empty> | ' development ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 19 | <empty> | 'off' | BOOTED | EXIT:1 | production | - | - | - | - |
| 20 | <empty> | 'managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 21 | <empty> | 'external' | BOOTED | EXIT:1 | production | - | - | - | - |
| 22 | <empty> | 'Managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 23 | <empty> | 'zzmarker7391garbage' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 24 | <empty> | '   ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 25 | 'production' | <unset> | BOOTED | EXIT:1 | production | - | - | - | - |
| 26 | 'production' | <empty> | BOOTED | EXIT:1 | production | - | - | - | - |
| 27 | 'production' | 'development' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 28 | 'production' | 'production' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 29 | 'production' | 'DEVELOPMENT' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 30 | 'production' | ' development ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 31 | 'production' | 'off' | BOOTED | EXIT:1 | production | - | - | - | - |
| 32 | 'production' | 'managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 33 | 'production' | 'external' | BOOTED | EXIT:1 | production | - | - | - | - |
| 34 | 'production' | 'Managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 35 | 'production' | 'zzmarker7391garbage' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 36 | 'production' | '   ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 37 | 'development' | <unset> | BOOTED | BOOTED | **development** | - | - | - | - |
| 38 | 'development' | <empty> | BOOTED | BOOTED | **development** | - | - | - | - |
| 39 | 'development' | 'development' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 40 | 'development' | 'production' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 41 | 'development' | 'DEVELOPMENT' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 42 | 'development' | ' development ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 43 | 'development' | 'off' | BOOTED | BOOTED | **development** | - | - | - | - |
| 44 | 'development' | 'managed' | BOOTED | BOOTED | **development** | - | - | - | - |
| 45 | 'development' | 'external' | BOOTED | BOOTED | **development** | - | - | - | - |
| 46 | 'development' | 'Managed' | BOOTED | BOOTED | **development** | - | - | - | - |
| 47 | 'development' | 'zzmarker7391garbage' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 48 | 'development' | '   ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 49 | 'Production' | <unset> | BOOTED | EXIT:1 | production | - | - | - | - |
| 50 | 'Production' | <empty> | BOOTED | EXIT:1 | production | - | - | - | - |
| 51 | 'Production' | 'development' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 52 | 'Production' | 'production' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 53 | 'Production' | 'DEVELOPMENT' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 54 | 'Production' | ' development ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 55 | 'Production' | 'off' | BOOTED | EXIT:1 | production | - | - | - | - |
| 56 | 'Production' | 'managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 57 | 'Production' | 'external' | BOOTED | EXIT:1 | production | - | - | - | - |
| 58 | 'Production' | 'Managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 59 | 'Production' | 'zzmarker7391garbage' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 60 | 'Production' | '   ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 61 | ' production ' | <unset> | BOOTED | EXIT:1 | production | - | - | - | - |
| 62 | ' production ' | <empty> | BOOTED | EXIT:1 | production | - | - | - | - |
| 63 | ' production ' | 'development' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 64 | ' production ' | 'production' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 65 | ' production ' | 'DEVELOPMENT' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 66 | ' production ' | ' development ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 67 | ' production ' | 'off' | BOOTED | EXIT:1 | production | - | - | - | - |
| 68 | ' production ' | 'managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 69 | ' production ' | 'external' | BOOTED | EXIT:1 | production | - | - | - | - |
| 70 | ' production ' | 'Managed' | BOOTED | EXIT:1 | production | - | - | - | - |
| 71 | ' production ' | 'zzmarker7391garbage' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 72 | ' production ' | '   ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 73 | 'zzmarker7391garbage' | <unset> | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | n/a | no |
| 74 | 'zzmarker7391garbage' | <empty> | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | n/a | no |
| 75 | 'zzmarker7391garbage' | 'development' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 76 | 'zzmarker7391garbage' | 'production' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 77 | 'zzmarker7391garbage' | 'DEVELOPMENT' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 78 | 'zzmarker7391garbage' | ' development ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 79 | 'zzmarker7391garbage' | 'off' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | n/a | no |
| 80 | 'zzmarker7391garbage' | 'managed' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | n/a | no |
| 81 | 'zzmarker7391garbage' | 'external' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | n/a | no |
| 82 | 'zzmarker7391garbage' | 'Managed' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | n/a | no |
| 83 | 'zzmarker7391garbage' | 'zzmarker7391garbage' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |
| 84 | 'zzmarker7391garbage' | '   ' | EXIT:1 | EXIT:1 | REFUSED | 1 | yes | yes | no |

*(`n/a` in rows 73/74/79–82 = the topology variable is correct there, so the refusal
correctly names only `VIZRA_MODE`.)*

### What the matrix establishes

- **No combination boots in a mode the operator did not ask for.** Every row is either the
  explicitly requested mode, the documented `production` default, or a refusal.
- **`development` is reached only with an explicit `VIZRA_MODE=development`** — rows 37, 38,
  43, 44, 45, 46 and nowhere else. There is no path from the old name to `development`.
- **The named danger is closed.** Row 3: `VIZRA_SEARCH_MODE=development` alone → refuses,
  exit 1, names both variables. It does *not* silently become production-with-a-dev-key.
- **The inverse works.** Row 44: `VIZRA_MODE=development` + `VIZRA_SEARCH_MODE=managed` →
  boots in development, dev key accepted.
- **No refusal echoed a supplied value** — an `egrep` for `DEVELOPMENT|Managed|Production|zzmarker7391garbage`
  across all 168 captured outputs returned **no file**. (But see FINDING 1: this property is
  not under test.)

### Refusal texts (verbatim, from my runs)

Old vocabulary (row 3):
```
vizra-search: invalid vizra-search configuration:
  - VIZRA_SEARCH_MODE carries a value from this service's OLD runtime-mode vocabulary and is NO LONGER READ as a mode. The runtime mode is VIZRA_MODE (development | production); VIZRA_SEARCH_MODE now means vizra-core's search topology (off | managed | external) product-wide and is owned by core. There is no compatibility alias, so this value has no effect — rename the variable rather than let this process boot in a mode your env file never named.
```

Neither vocabulary (rows 11, 12):
```
  - VIZRA_SEARCH_MODE is vizra-core's search topology variable (off | managed | external) and is not read by this service, but its value is none of those. If you meant this process's runtime mode, that is VIZRA_MODE (development | production).
```

### Case / whitespace policy — consistent between the two variables

Both `mode()` (config.go:283) and `searchTopology()` (config.go:342) apply
`strings.ToLower(strings.TrimSpace(...))`. Evidence: `'Production'` (row 49) and
`' production '` (row 61) both give production; `'DEVELOPMENT'` (row 5) and
`' development '` (row 6) are both refused as the retired vocabulary; `'Managed'` (row 10)
is silently ignored as topology. **The policy is identical for both variables and is
documented** in `AGENTS.md`'s table ("any case, surrounding whitespace ignored").

### Presence vs emptiness — `LookupEnv`, and "empty = tombstone"

`internal/config/env.go:6` — `func osLookupEnv(key string) (string, bool) { return os.LookupEnv(key) }`
is the only place the package touches the environment; `Load()` (config.go:254) passes it as
the `Lookup` seam. So presence and emptiness are genuinely distinguished.

`searchTopology` returns early on `!ok || raw == ""` — i.e. **absent and completely empty are
both tolerated**, while whitespace-only falls through to the refusal (rows 12/24/36/48/60/72/84).
I consider the tombstone **safe**: a leftover env-file line `VIZRA_SEARCH_MODE=` cannot select
a mode, and with `VIZRA_MODE` unset the process lands on the strict `production` default
(rows 2, 14). The only way empty could mislead is an operator who wanted development and got
production — the fail-secure direction. Whitespace-only being refused is the stricter, and
correct, reading of an ambiguous file.

### Dockerfile default does not mask an operator's unset

`Dockerfile:78-79` — `ENV VIZRA_SEARCH_ADDR=:8081 \` / `    VIZRA_MODE=production`.
It sets **production**, never development. Nothing in the tree sets `VIZRA_MODE=development`
except the local `make run` target (Makefile:185), which is a developer convenience on
loopback only.

### Nothing else in the tree still reads the old name

`grep -rn VIZRA_SEARCH_MODE` over the whole checkout (excluding `.git` and `docs/evidence/`)
returns **only**: the constant and its refusal in `config.go`, the tests that drive that
refusal, the boot-matrix harness, the new `docker-build` step that asserts the refusal, and
prose in `AGENTS.md` / `README.md` / `Makefile` / `Dockerfile` comments. **No reader remains.**
`TestTheOldNameIsConsultedOnlyByTheRefusal` (config_test.go:333) additionally counts the
lookups and requires exactly 1.

---

## 3. The builder's three demonstrations — reproduced

Baseline digest of `internal/config/config.go` measured by me:
`538ba2729e53b66fcc83e9e5416dfa49637a0a92f37182ceb410d98c935b631d` — **identical** to the
digest the builder's transcripts and PR body claim.

| Mutation | digest after (mine) | passed/failed | Red on | Restored digest | Matches builder's claim |
|---|---|---|---|---|---|
| `fallback-to-the-old-name` | `2b201e3843aa771f…` | **11 / 3** | `old-name-old-vocabulary-alone`, `old-name-old-vocabulary-production-alone`, focused suite | `538ba272…` | ✅ 11/3 |
| `drop-the-refusal` | `af08c31f9e661e0e…` | **7 / 7** | the two above + `both-set-old-vocabulary`, `both-set-old-vocabulary-dev`, `garbage-old-name`, `garbage-both`, focused suite | `538ba272…` | ✅ 7/7 |
| `default-to-development` | `3189f58ae2834883…` | **11 / 3** | `unset-unset`, `old-name-topology-alone`, focused suite | `538ba272…` | ✅ 11/3 |

`git status --porcelain` was empty after each run. The harness's integrity claims hold on
inspection and in use:

- `scripts/boot-matrix.sh` records the digest **before and after** and dies with exit 2 if the
  patch left the file byte-identical or its anchor did not occur exactly once — I observed
  distinct before/after digests on all three.
- Refusal cases are bounded by a **10 s watchdog** (`REFUSAL_GRACE=10`, boot-matrix.sh:37);
  exit 137 is explicitly reported as "it booted", so a mutation that removes a refusal goes
  red instead of hanging. This is the property that makes the harness able to fail.
- Boot cases are proved **healthy over real TCP** (`curl /healthz`) before being drained with
  SIGTERM, and the log is grepped for the minted key (boot-matrix.sh:271) so no secret leaks.

One methodological note in the builder's favour, and one caveat: the harness decides *which*
mode a booted process is in from the `"running in development mode"` log line. That is weaker
than behavioural proof, so I did not rely on it — my own matrix (§2) proved the mode from dev-key
acceptance instead, and **the two agree on every overlapping case**.

---

## 4. My own mutations

Applied by me to the clean clone, restored with `git checkout` after each. Baseline and final
digest both `538ba272…`; tree clean at the end.

| # | My mutation | Result | Named test(s) turned red |
|---|---|---|---|
| M1 | refuse only in production, not in every mode | **RED** (boot-matrix 12/2) | `TestTheOldRuntimeModeNameIsRefusedInDevelopmentToo` |
| M2 | accept the old name when `VIZRA_MODE` is ALSO set | **RED** (boot-matrix 10/4) | `TestTheOldNameIsConsultedOnlyByTheRefusal`, `TestTheOldRuntimeModeNameIsRefusedInDevelopmentToo` |
| M3 | treat an unknown `VIZRA_MODE` value as development | **RED** (boot-matrix 12/2) | `TestUnknownModeIsRefused` |
| M4 | **echo the offending value in the error** | **STAYED GREEN** (boot-matrix 14/0, `go test` exit 0) | *none* |
| M5 | drop `external` from the pinned vocabulary | **RED** (boot-matrix 12/2) | `TestTheTopologyVocabularyIsPinnedToCore` |
| M6 | core extends its topology vocabulary (no edit in this repo) | **STAYED GREEN** — 0 tests red | *none* |

M4 and M6 are the two findings below. M1, M2, M3 and M5 confirm the controls are real and
tightly targeted.

**M6 in detail.** I left the repository untouched and asked what happens the day `vizra-core`
adds a fourth topology value. `go test ./internal/config/ ./cmd/vizra-search/` stays green — nothing
in this repository notices — and the binary then does this:

```
$ VIZRA_MODE=production VIZRA_SEARCH_MODE=readonly SEARCH_HMAC_KEY=<32B> ./vizra-search
vizra-search: invalid vizra-search configuration:
  - VIZRA_SEARCH_MODE is vizra-core's search topology variable (off | managed | external) and is not read by this service, but its value is none of those. If you meant this process's runtime mode, that is VIZRA_MODE (development | production).
exit 1
```

That is a search instance refusing to boot on an operator's machine — precisely the outcome
`TestTheTopologyVocabularyIsPinnedToCore`'s own comment promises to prevent.

---

## 5. `TestTheTopologyVocabularyIsPinnedToCore` — pinned to *what*

**Pinned to a second hard-coded copy inside the same test file.** `config_test.go:342`:

```go
func TestTheTopologyVocabularyIsPinnedToCore(t *testing.T) {
	want := []string{"off", "managed", "external"}
	got := config.SearchTopologyValues
	...
}
```

It reads **no vendored file, no core checkout, no contract artifact**.

**What it actually guarantees:** that nobody edits `config.SearchTopologyValues` in this
repository without also editing this test — my M5 confirms it catches exactly that.

**What it does not guarantee:** anything about `vizra-core`. Drift originating in core is
invisible here (M6).

For the record, the two lists agree **today**. Read read-only from core main at
`5eb2829eb4f830206029f8e2a836f93a44a93a02` via
`git -C .../vizra-core show origin/main:internal/config/keys.go` (the working tree was not
touched):

```
{Name: "VIZRA_SEARCH_MODE", Default: "off", Doc: "off | managed | external. Default off until M3 (ADR-002, Q-001)."}
```

`{"off", "managed", "external"}` — an exact match, in core's order. The *state* is correct;
the *mechanism* claimed for keeping it correct does not exist.

---

## 6. The new `docker-build` step, read from the CI log on this SHA

Workflow run `35578042015`, job `docker-build` (check id `106264336343`),
https://github.com/yegamble/vizra-search/actions/runs/35578042015/job/106264336343

The step **ran the built image** (`vizra-search:ci`) and produced the real refusal:

```
+ timeout 30 docker run --rm -e VIZRA_SEARCH_MODE=development -e SEARCH_HMAC_KEY="$(openssl rand -hex 32)" vizra-search:ci
vizra-search: invalid vizra-search configuration:
  - VIZRA_SEARCH_MODE carries a value from this service's OLD runtime-mode vocabulary and is NO LONGER READ as a mode. …
the image refused the retired name (exit 1), as required
```

- Runs the **built image**, on amd64 (ubuntu-24.04), which I cannot do locally — ✅
- **No `|| true`.** It uses `|| code=$?` and then fails on `code -eq 0` and on `code -eq 124` — ✅
- The `timeout 30` + explicit 124 branch means a container that *serves* (the `drop-the-refusal`
  regression) fails the job rather than hanging it — ✅ the assertion is able to fail.
- The key is `openssl rand -hex 32`, i.e. **valid**, so the refusal cannot be the key's — ✅
- ❌ **It does not assert the refusal text.** See FINDING 3.

The two adjacent steps' `VIZRA_SEARCH_MODE=production` → `VIZRA_MODE=production` renames are
both present and both green.

---

## 7. CI on `852b3829…`

`gh api repos/yegamble/vizra-search/commits/852b3829…/check-runs` — **12 check runs, all
`completed` / `success`**, none skipped, cancelled or timed out:

`ci-required`, `build`, `contract-drift`, `docker-build`, `echo-containment`, `fmt`,
`govulncheck`, `test`, `test-noskip`, `tidy-check`, `vet`, plus `GitGuardian Security Checks`.

`.github/required-checks.txt` lists exactly: `fmt`, `vet`, `echo-containment`, `build`,
`contract-drift`, `test`, `test-noskip`, `tidy-check`, `govulncheck`, `docker-build` — **all
ten present in the check-run list and all green.** The manifest matches the jobs that actually
ran; there is no listed-but-never-executed lane. The manifest file itself is unedited by this PR.

`boot-matrix` is **not** in the manifest and **not** in `make ci` — it is a local-only
demonstration. The repository says so at that strength in three places (Makefile:191-193,
`docs/evidence/pr4/README.md` § "What these transcripts do not cover", and `AGENTS.md`), each
noting that the same refusals are driven through the real binary by `cmd/vizra-search/main_test.go`
inside the required `test` lane. I confirmed that: M1/M2 turn `cmd/vizra-search` tests red, so
the control *is* in a required lane.

---

## Findings

```
FINDING 1: "no refusal message ever echoes a value" is documented as a property but nothing tests it
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/config/config.go:355-370 (the two addf calls)
             internal/config/config_test.go:196-212 (TestTheOldRuntimeModeNameIsRefusedByName)
             AGENTS.md:304 ("No refusal message ever echoes a value")
             docs/evidence/pr4/README.md:14 ; PR #4 body line 35
             scripts/boot-matrix.sh:271 (greps only for the minted KEY)
  requirements: the slice's acceptance bullet 2 ("never echoing values") and bullet 5

Observed:
  AGENTS.md states the property absolutely: "No refusal message ever echoes a
  value — only the two variable names and the two vocabularies, which are
  constants in internal/config/config.go." The PR body repeats it.
  The existing no-echo assertions cover the SECRET only: config_test.go:426
  ("config error echoes the rejected key material"), config_test.go:608,
  cmd/vizra-search/main_test.go:125, and boot-matrix.sh:271 `grep -q "${KEY}"`.
  My mutation M4 changed the non-vocabulary refusal to `v.addf("%s=%s …",
  EnvSearchTopology, raw, …)` so it echoes the operator's value verbatim.
  `go test ./internal/config/ ./cmd/vizra-search/` exited 0 and
  ./scripts/boot-matrix.sh reported 14 passed, 0 failed. Nothing went red.

Failure:
  A stated boot-time property has no control. A future edit to either addf can
  start echoing VIZRA_SEARCH_MODE's value into stderr and every lane stays
  green. The value here is not itself a secret, so the harm is bounded — but
  the sentence in AGENTS.md is stronger than anything that enforces it, which
  is the class of claim this war room holds PRs for.

Perspective:
  operator, developer

Recommendation:
  One assertion, in the test that already drives both refusal branches: after
  asserting the message names both variables, assert it does NOT contain the
  supplied value. A distinctive sentinel (e.g. "zzsentinel") makes it exact and
  avoids colliding with the vocabulary words the message legitimately prints.

Acceptance criteria:
  - With VIZRA_SEARCH_MODE set to a non-vocabulary sentinel, the error string
    does not contain that sentinel.
  - With VIZRA_MODE set to a non-vocabulary sentinel, the same holds.
  - Re-applying mutation M4 (add `raw` to the addf format) turns that named test
    red.

Tests:
  internal/config/config_test.go — extend TestANonVocabularyValueInTheOldNameIsRefused
  and TestUnknownModeIsRefused with a `strings.Contains(msg, sentinel)` negative
  check. No new harness needed.

Cross-repo implications:
  core: none | user: none | search: the fix | meta: none

Challenge:
  The echoed value is a mode/topology string, not a credential, so this is not a
  privacy leak and arguably only a tidiness rule. Counter: the rule was inherited
  from the SEARCH_HMAC_KEY precedent precisely because env values are not always
  safe to print, and an untested absolute statement is the thing the contract
  forbids, independent of this variable's sensitivity.
```

```
FINDING 2: TestTheTopologyVocabularyIsPinnedToCore does not pin anything to core, and its comment says it does
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/config/config_test.go:338-352 (the comment and the test)
             internal/config/config.go:159-169 (SearchTopologyValues doc comment)
             AGENTS.md:298-301 ; PR #4 body line 33
  requirements: the slice's acceptance bullet 5 ("docs at the strength of the control")

Observed:
  config_test.go:338-341 says, verbatim:
    "The topology vocabulary is CORE's, pinned here so that core extending it is
     a red test in this repository rather than a search instance that refuses to
     boot on an operator's machine."
  The test it introduces compares config.SearchTopologyValues against a literal
  []string{"off","managed","external"} declared three lines below. It opens no
  vendored file, no core checkout and no contract artifact.
  config.go:165 says "It is CORE's list, pinned by
  TestTheTopologyVocabularyIsPinnedToCore." PR body line 33 says "pinned by".
  My M6: with the repository untouched and core IMAGINED to have added a value,
  `go test ./internal/config/ ./cmd/vizra-search/` exits 0 — 0 tests red — and
  the binary refuses VIZRA_SEARCH_MODE=readonly at boot with exit 1.
  My M5 (deleting "external" from the list) DOES turn the test red, which is the
  only direction it protects.
  For the record the two lists agree today: vizra-core main@5eb2829,
  internal/config/keys.go:53 — Default "off", Doc "off | managed | external".

Failure:
  The refusal of everything outside the vocabulary is a deliberately accepted
  forward-compatibility cost, and this test is the single named mitigation for
  it. The mitigation does not exist in the direction that matters. A maintainer
  who reads the comment and upgrades core will believe CI here will catch a new
  topology value; it will not, and the first sign will be a search container
  that refuses to boot on an operator's machine — the exact outcome the comment
  promises to prevent.

Perspective:
  operator, developer

Recommendation:
  Do not build a cross-repo pin in this slice. Correct the three sentences to
  say what the control actually is: the list is a hard-coded duplicate of core's
  vocabulary; this test freezes the local copy so it cannot be edited silently;
  drift originating in core is caught only by review at re-vendor/upgrade time,
  and its symptom is a boot refusal. AGENTS.md should carry that sentence in the
  "costs forward compatibility" bullet, where the cost is already named.

Acceptance criteria:
  - No sentence in config.go, config_test.go, AGENTS.md or the PR body claims
    that core extending the vocabulary produces a red test in this repository.
  - AGENTS.md § "One operator-facing name per concept" states explicitly that
    core-side drift is caught by review/re-vendor only, and that its symptom is
    a search boot refusal.
  - The test's doc comment says what it guarantees: the local list cannot change
    without this test changing.

Tests:
  No new test required — the existing test is correct for what it does; only the
  claims around it are wrong. If a real pin is ever wanted, the smallest honest
  version is to read the vocabulary out of the already-vendored core contract at
  re-vendor time and fail `make vendor-contract-check` on drift, which is a
  separate, dispatched slice.

Cross-repo implications:
  core: none today (vocabularies match at 5eb2829) | user: none |
  search: the wording fix | meta: none

Challenge:
  The claim could be read charitably as "this is the place you must update when
  core changes", which is true, and AGENTS.md's own wording ("is where the list
  is pinned") is closer to that. Counter: the test-file comment is not ambiguous
  — it asserts a red test as the alternative to a boot refusal, and that is
  false. This is exactly a doc stronger than its control, which acceptance
  bullet 5 forbids.
```

```
FINDING 3: the new docker-build step counts any non-zero exit as "refused"
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     .github/workflows/ci.yml:185-207 ("the image refuses the retired runtime-mode name")
  requirements: the slice's acceptance bullet 4

Observed:
  The step checks `code -eq 0` (booted → fail) and `code -eq 124` (still running
  → fail), then prints "the image refused the retired name (exit $code)". It
  never inspects the container's output. In the run on this SHA the output was
  the correct refusal naming VIZRA_SEARCH_MODE and VIZRA_MODE, so the step is a
  true positive today.

Failure:
  Any other reason for a non-zero exit — a missing file in the scratch image, an
  unrelated config error, a crash — would be recorded as "the image refused the
  retired name". The step would report a control that had in fact regressed.
  Bounded in practice: the adjacent step boots the same image successfully, so a
  wholly broken image fails the job anyway.

Perspective:
  developer

Recommendation:
  Capture the output and require it to name the variable, e.g. pipe the run to a
  file and `grep -q "VIZRA_SEARCH_MODE"` plus `grep -q "VIZRA_MODE"` before
  declaring success. Two lines.

Acceptance criteria:
  - The step fails if the container exits non-zero WITHOUT the refusal naming
    both variables.
  - The step still fails on exit 0 and on exit 124.

Tests:
  The docker-build lane itself, on the next PR head.

Cross-repo implications:
  core: none | user: none | search: the fix | meta: none

Challenge:
  Belt-and-braces: the same job already boots the image successfully two steps
  later, so an image that cannot start is caught regardless. Accepted — hence NIT.
```

---

## Cross-repo note for the chair (reported, not fixed)

Meta PR #4 (`feat/m0-compose-topology`) `docker-compose.yml` sets, on the **search** service:

```yaml
  search:
    environment:
      # SEARCH'S OWN vocabulary — `production|development`, nothing to do with
      # core's `off|managed|external`. Set LITERALLY, never from the operator
      # env file: vizra-search fails closed on an unrecognised mode, so handing
      # it core's `off` would stop it booting. See the header of this file.
      VIZRA_SEARCH_MODE: production
```

After this PR merges that is **my matrix row 4** — a designed boot refusal, exit 1.

**The exact key/value meta must deliver instead:** `VIZRA_MODE: production` on the `search`
service. Confirmed by matrix row 25 (boots in production).

Three further consequences meta must handle in the same change:

1. The comment block above that line (and the file header's paragraph `(b)` explaining that
   `VIZRA_SEARCH_MODE` "means DIFFERENT things to vizra-core and to …") is now false and must
   be rewritten: the name has exactly one meaning product-wide.
2. `VIZRA_SEARCH_MODE: production` must **not** merely be renamed in place if any template or
   `scripts/check-config-coverage.py` pairing still expects a search-side consumer for
   `VIZRA_SEARCH_MODE` — that coverage check may need the pairing moved to `VIZRA_MODE`.
3. **Core's own line stays exactly as it is**: `VIZRA_SEARCH_MODE: ${VIZRA_SEARCH_MODE:-off}`
   on the api/worker services (compose line 93) is the topology, and is now the name's only
   meaning. Verified read-only against core main@`5eb2829` keys.go:53.

---

## Verdict

Everything about the **code** reproduced. The rename is correct, the refusal is precise in all
four documented branches, the named danger is closed, production remains the default, no test
was weakened or deleted, all three builder demonstrations reproduce digest-for-digest, four of
my six adversarial mutations turn a *named* test red, every required lane is green on this SHA
and the required-checks manifest matches the jobs that ran.

It fails on acceptance bullet 5 — *"docs at the strength of the control"* — in two places, both
found by mutations that stayed green:

- FINDING 2: a test comment asserts a cross-repo drift alarm that does not exist, as the sole
  named mitigation for a deliberately accepted forward-compatibility cost.
- FINDING 1: an absolute no-echo property with no test behind it.

Both fixes are prose plus one assertion; no design change, no re-verification of the matrix
needed beyond re-running `make ci` and the named test.

FINAL VERDICT: FAIL — SHA 852b38291c3ec8109f27ebd924ef48eec3b11a9d
