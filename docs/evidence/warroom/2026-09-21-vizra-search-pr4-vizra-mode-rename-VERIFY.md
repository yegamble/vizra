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

---
---

# Re-verification at `6a02ab2` — 2026-09-21

- **SHA verified:** `6a02ab2975a6f5c4da49b5af62b9822ead2e885e`
- **Relationship to the failed head:** `git merge-base --is-ancestor 852b3829… HEAD` → **true**.
  One commit (`6a02ab2 fix(config): ignore what we do not own; test the no-echo property`) on
  top of `852b382`. **No force-push**, no history rewrite.
- **Base:** `origin/main` still `3619fed873fc194130f02cc85577de10414ade39` (unmoved).
- Fresh `mktemp -d` clone, new scratch directory; the round-1 directory was already deleted.
- Environment as in round 1 (darwin/arm64, go1.26.2, Docker 29.8.0; **no amd64 build attempted**).

## 0. The policy this round verifies

Chair ruling, prompted by round-1 FINDING 2, **reverses the original brief**: vizra-search no
longer validates core's topology vocabulary at all. `VIZRA_SEARCH_MODE` carrying an **old
runtime value** (`development`/`production` after TrimSpace+ToLower) → refused by name in every
mode. **Every other value** — core's topology values, unknown values, whitespace-only, empty →
**ignored silently**. I verified against the *new* policy, not the old brief.

## 1. My 84-combination matrix, re-run against the new binary

Same harness, same method: `env -i`, two key probes per combination, **mode proven from
behaviour** (acceptance of the published dev key), marker garbage value, 168 outputs captured.

**Distribution:** 36 REFUSED · 40 production · 8 development *(round 1: 48 / 30 / 6)*.

**Exactly twelve rows changed classification, all in the predicted direction** — garbage or
whitespace-only in `VIZRA_SEARCH_MODE` moving from "refused" to "boots in `VIZRA_MODE`'s mode":

| # | VIZRA_MODE | VIZRA_SEARCH_MODE | round 1 | round 2 |
|---|---|---|---|---|
| 11, 12 | `<unset>` | marker / `'   '` | REFUSED | **production** |
| 23, 24 | `<empty>` | marker / `'   '` | REFUSED | **production** |
| 35, 36 | `production` | marker / `'   '` | REFUSED | **production** |
| 47, 48 | `development` | marker / `'   '` | REFUSED | **development** |
| 59, 60 | `Production` | marker / `'   '` | REFUSED | **production** |
| 71, 72 | `' production '` | marker / `'   '` | REFUSED | **production** |

**No other row moved.** In particular rows 83/84 (garbage `VIZRA_MODE` + garbage/whitespace
topology) still refuse, because `VIZRA_MODE` is this service's own variable and is still validated.

### The safety property holds

- **The eight rows observed in `development` are 37, 38, 43, 44, 45, 46, 47, 48 — every one has
  an explicit `VIZRA_MODE=development`.** The two new ones (47, 48) gained development *from
  `VIZRA_MODE`*, not from the retired name. **Nothing reaches development without asking.**
- The named danger and all its case/whitespace variants still refuse: rows 3, 4, 5, 6 and every
  combination of them with any `VIZRA_MODE` (24 rows in total).
- **No echo.** `grep -rlE 'DEVELOPMENT|Managed|Production|zzmarker7391garbage'` over all 168
  captured outputs returned **no file**.

### Near-misses of the old vocabulary (`VIZRA_MODE` unset, dev-key probe for mode)

| value sent | result | echoes value |
|---|---|---|
| `production ` (trailing space) | **REFUSED** | no |
| ` production` (leading space) | **REFUSED** | no |
| `development\t` (trailing tab) | **REFUSED** | no |
| `\ndevelopment\n` (newline-wrapped) | **REFUSED** | no |
| `DeVeLoPmEnT` (odd case) | **REFUSED** | no |
| `developmnt` (typo) | boots **production** | no |
| `dev` | boots **production** | no |
| `prod` | boots **production** | no |
| `produc tion` (inner space) | boots **production** | no |
| `development # x` (trailing comment) | boots **production** | no |
| `"development"` (double-quoted) | boots **production** | no |
| `'development'` (single-quoted) | boots **production** | no |
| `ｄevelopment` (unicode fullwidth d) | boots **production** | no |
| `dеvelopment` (Cyrillic е look-alike) | boots **production** | no |
| `staging` | boots **production** | no |
| `off` (core topology) | boots **production** | no |

Refused = exactly the set `TrimSpace`+`ToLower` normalises onto `development`/`production`
(leading/trailing spaces, tabs and newlines are all trimmed by `strings.TrimSpace`). Everything
else boots production. **Nothing in this table boots development.**

My harness first flagged three of these as "ECHOED"; on inspection all three were **artifacts of
my own substring grep** hitting the legitimately printed `development | production` vocabulary
(and `production` in the startup log). I diffed the actual outputs: the refusal text for
` production`, `\ndevelopment\n` and `DeVeLoPmEnT` is **byte-identical** to the canonical message.
**Zero real echoes.**

**Is the accepted cost stated truthfully?** Yes, and unusually plainly. `AGENTS.md:302-310`:

> **The accepted cost, stated plainly:** a typo such as `VIZRA_SEARCH_MODE=developmnt` with no
> `VIZRA_MODE` boots **production** — the strict mode — and the operator finds out because the
> development affordances they wanted (the published dev key, the relaxed ceilings) are refused.
> That is the fail-safe direction. Production is the **default**, and the only dangerous outcome
> — running development without asking for it — requires an explicit `VIZRA_MODE=development` and
> can never come from this variable.

It names the exact typo I tested, the exact outcome I measured, and the named test and two matrix
rows that hold the line. This is a doc at — not above — the strength of its control.

## 2. Mutations

Baseline digest measured by me: `84f2c1fe25e5c49dd46d6428bb530f92c6c1c64d1891b45572938c19e226fc73`
— **identical to the builder's claim**. Green matrix: **21 passed, 0 failed** (20 boot cases +
the focused suite), matching the claim.

### The builder's five, reproduced with my own digests

| Mutation | digest after (mine) | passed/failed | claim | match |
|---|---|---|---|---|
| `fallback-to-the-old-name` | `e8e21d83c585a211…` | **17 / 4** | 17/4 | ✅ |
| `drop-the-refusal` | `193880b62ef01a97…` | **15 / 6** | 15/6 | ✅ |
| `default-to-development` | `d6fe88c50c894408…` | **14 / 7** | 14/7 | ✅ |
| `unknown-value-as-development` | `4ff73168120e93c3…` | **15 / 6** | 15/6 | ✅ |
| `echo-the-value` | `b8c9d1fdafc1db91…` | **19 / 2** | 19/2 | ✅ |

All five restored to `84f2c1fe…`; `git status --porcelain` empty after each.

### My own four

| # | My mutation | Result | Named test(s) red |
|---|---|---|---|
| V1 | ignore the old name entirely when `VIZRA_MODE` is set | **RED** — unit + matrix 18/3 | `TestTheOldNameIsConsultedOnlyByTheRefusal`, `TestTheOldRuntimeModeNameIsRefusedInDevelopmentToo` |
| V2 | refuse only in production | **RED** — unit + matrix 19/2 | `TestTheOldRuntimeModeNameIsRefusedInDevelopmentToo` |
| V3 | log the ignored value via `os.Getenv` in `Config.String()` | **STAYED GREEN** — see note | none |
| V4 | echo the raw value in the retired-name refusal (my round-1 **M4**) | **RED at unit AND matrix level** — 19/2 | `TestNoRefusalEchoesTheSuppliedValue/the_retired_runtime-mode_name` |

**V4 closes round-1 FINDING 1.** The property that had no control now has one that bites at both
levels.

**V3 note — not a finding against this PR.** My mutation reached *around* the `Lookup` seam with a
direct `os.Getenv`. The unit tests inject a map, so the marker never appears and the test cannot
see it; no lane catches a stray `os.Getenv` either (`grep` for any guard: none exists). But
`internal/config/env.go:6` — "osLookupEnv is the only place this package touches the process
environment" — is a **pre-existing, unenforced discipline that predates this slice** and is
untouched by it. Out of scope; recorded for the chair as a standing, separate observation.

### M6 — core adds a topology value: now a non-event

Repository untouched, six values probed against the real binary:

| value | result |
|---|---|
| `readonly`, `hybrid`, `replica` (hypothetical new core values) | **BOOTED** (production) |
| `off`, `managed`, `external` (core's current values) | **BOOTED** (production) |

Unit tests green throughout. The day core extends its vocabulary, **nothing here breaks** — which
is precisely what round-1 FINDING 2 asked for. `SearchTopologyValues`,
`TestTheTopologyVocabularyIsPinnedToCore` and every pinning sentence are deleted from `config.go`,
`config_test.go`, `AGENTS.md` and the PR body. **Round-1 FINDING 2 is closed.**

## 3. Does the no-echo test really cover every refusal path?

I enumerated the loader's refusal sites from the source (`grep -c 'v\.addf('` → **17**) and then
measured, with `go test -run TestNoRefusalEchoesTheSuppliedValue -coverprofile`, which of those
lines the test actually executes:

| | sites |
|---|---|
| **Executed** (6) | 287 unknown `VIZRA_MODE`; 344 retired name; 361 listen address; 374 not-a-duration; 391 not-an-integer; 501 key too short |
| **Not executed** (11) | 378 & 395 "must be greater than zero"; 412 & 416 production ceilings; 459 key must be set; 474, 478, 484, 490, 496 key placeholder/published refusals; 505 distinct-bytes |

**The test drives 6 of 17 paths, not "every refusal in the loader".** See FINDING 4.

The important mitigating fact, which I checked by reading all 17 format strings: **not one `addf`
call anywhere in the loader interpolates a supplied value.** Every argument is an `Env*` constant,
a `Mode*` constant or a numeric limit — the `key` argument in `duration()`/`bytes()` is the
*variable name*, not its content (`raw` is never passed). So the *property* genuinely holds on all
17 paths; only the *claim about the test's reach* is wrong. The 11 unreached paths are unreachable
**by a marker** by construction: the ceilings need a valid-but-too-large value, the placeholder
branches need a placeholder-shaped key, "greater than zero" needs a parseable non-positive value.

**Is the `development`/`production` exemption narrow enough?** Yes, at both levels:

- Unit: the retired-name subtest supplies `"  DeVeLoPmEnT\t"` and asserts the message contains
  **neither** the raw string **nor** the bare `"DeVeLoPmEnT"` shape.
- Matrix: `scripts/boot-matrix.sh:333-337` greps **every refusal row** for each supplied value,
  skipping only `development` and `production` **exactly as spelled** — and case
  `old-name-old-vocabulary-odd-case` deliberately supplies `  DeVeLoPmEnT  ` so that spelling is
  checked. An echoed odd-case shape **is** caught.

Booting rows are also checked: values ≥6 characters must not appear in the process log
(boot-matrix.sh:284-288), with the length guard honestly commented as avoiding collision with
ordinary log text.

## 4. The `docker-build` step on this SHA

Run `35580813539`, job `docker-build` (`106273021073`). The step now captures the container output
to `retired-name.log` and requires:

```
if [ "$code" -eq 0 ];   then … exit 1; fi     # booted
if [ "$code" -eq 124 ]; then … exit 1; fi     # still running after 30s
if ! grep -q 'VIZRA_SEARCH_MODE' retired-name.log; then … exit 1; fi
if ! grep -q 'VIZRA_MODE ('      retired-name.log; then … exit 1; fi
```

- Ran the **built amd64 image** (`vizra-search:ci`) on ubuntu-24.04 — ✅
- **No `|| true`**; `|| code=$?` with both failure branches intact — ✅
- The 124 branch is unchanged — ✅
- **Asserts both variable names in the captured text** — ✅ (round-1 FINDING 3 closed)
- The key is `openssl rand -hex 32`, so the refusal cannot be the key's — ✅

**What it guarantees, exactly:** the image exited non-zero within 30 s having printed text
containing both `VIZRA_SEARCH_MODE` and the literal `VIZRA_MODE (`. It does **not** pin the whole
message. Answering the question directly: **yes, in principle a different non-zero exit whose
output happened to contain both tokens would satisfy it.** In practice `VIZRA_MODE (` is produced
by exactly one message in this binary — the retired-name refusal (`mode()`'s own refusal prints
`VIZRA_MODE must be "production" or "development"`, with no parenthesis) — so the conjunction is
currently unique to the control under test. That is a materially honest control; pinning a longer
phrase would make it stronger still, but this is no longer a false positive.

## 5. Regression sweep of everything confirmed at `852b382`

| Check | Result at `6a02ab2` |
|---|---|
| Any reader of the old name **as a mode** | **None.** Only the constant, its refusal, tests, the harness, the CI assertion and prose |
| `LookupEnv` seam | intact — `internal/config/env.go:6` is the only `os.LookupEnv`; **no `os.Getenv` anywhere** in `internal/` or `cmd/` |
| Dockerfile `ENV` | `VIZRA_SEARCH_ADDR=:8081` + **`VIZRA_MODE=production`** — production, never development |
| Guards & manifest | `scripts/ci-required-guard.sh`, `scripts/check-workflows.py`, `.github/required-checks.txt` **not in the diff across either commit** |
| Makefile `ci:` | target line unchanged vs `3619fed` |
| `api/` and vendored files | **not in the diff at all** |
| `t.Skip` / `testing.Short()` in the tree | **0** |
| Skips counted by me from `go test -json` | **384 pass, 0 skip, 0 fail** |

### Test deletions in the fix commit — each one ruled

Round 1 had zero deleted test lines; this commit deletes some. **Five test functions removed, five
added**, and every removal is a direct consequence of the chair's reversal, with a named successor:

| Removed | Why it had to go | Successor |
|---|---|---|
| `TestTheTopologyVocabularyIsPinnedToCore` | **ruled deleted** (round-1 FINDING 2) | — (deliberately none) |
| `TestATopologyValueInTheOldNameIsIgnored` | iterated `config.SearchTopologyValues`, which no longer exists | `TestEveryValueButTheOldVocabularyIsIgnored` |
| `TestANonVocabularyValueInTheOldNameIsRefused` | asserted the **reversed** policy (refuse `staging`/`dev`/`prod`/`1`/whitespace) | `TestAnUnknownRetiredNameValueBootsProduction` |
| `TestAnEmptyOldNameIsToleratedAsATombstone` | "empty" is now one case of "ignored", not a special rule | `TestEveryValueButTheOldVocabularyIsIgnored` (covers `""`) |
| `TestBootAcceptsCoreTopologyAlongsideTheRuntimeMode` | named core's vocabulary, which this repo no longer knows | `TestBootIgnoresEveryOtherValueOfTheRetiredName` |

**No assertion was weakened to turn CI green.** The successors are strictly broader — e.g.
`TestEveryValueButTheOldVocabularyIsIgnored` covers `off, managed, external, staging, dev, prod,
developmnt, 1, "   ", ""` in both `VIZRA_MODE` states, and
`TestNoValueInTheOldNameCanEverProduceDevelopment` supplies the **published dev key** so that a
wrongly-selected development mode would be *visible* (it asserts the refusal is specifically the
`development placeholder` one, i.e. the mode really was production). That claim of the builder's
is accurate.

## 6. Lanes from the clean clone

| Command | Exit | Result I measured |
|---|---|---|
| `make ci` | **0** | **contract-drift 356 tests / 4 packages / 0 deselected**; `test -race` 6 packages ok; **test-noskip 384 pass events, 0 skips** |
| `go test -count=1 -json ./...` (my count) | **0** | pass **384**, skip **0**, fail **0** |
| `govulncheck ./...` | **0** | No vulnerabilities found |
| `./scripts/ci-required-guard.sh` | **0** | — |
| `python3 scripts/check-workflows.py` | **0** | — |
| `shellcheck scripts/boot-matrix.sh` | **0** | — |
| `./scripts/boot-matrix.sh` | **0** | **21 passed, 0 failed** |

Every number in the PR body's table reproduced exactly (356/0, 384/0, 21, and the five mutation counts).

## 7. CI on `6a02ab2`

**12 check runs, all `completed` / `success`**: `ci-required`, `build`, `contract-drift`,
`docker-build`, `echo-containment`, `fmt`, `govulncheck`, `test`, `test-noskip`, `tidy-check`,
`vet`, `GitGuardian Security Checks`. None skipped, cancelled or timed out.

All ten `.github/required-checks.txt` lanes are present in that list and green; the manifest is
unedited. **Which tree was tested:** both workflow runs report `headSha = 6a02ab2…` on the
`pull_request` event, so the checked-out tree is the PR merge of `6a02ab2` into `main`; `main` is
still `3619fed` (unmoved since the PR branched), and GitHub reports the PR MERGEABLE, so **the
merge tree is the head tree**. My clean clone at `6a02ab2` therefore tested the same content CI did.

## Round-1 findings — status

| | Finding | Status |
|---|---|---|
| 1 | no-echo property untested | **CLOSED** — my V4 is red at unit *and* matrix level |
| 2 | `TestTheTopologyVocabularyIsPinnedToCore` pinned nothing, comment claimed it did | **CLOSED** — test, constant and every pinning sentence deleted; M6 is a non-event |
| 3 | `docker-build` counted any non-zero exit as "refused" | **CLOSED** — output captured, both variable names asserted |

## New findings

```
FINDING 4: the no-echo test is documented as driving "every refusal path in the loader"; it drives 6 of 17
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/config/config.go:333 ; AGENTS.md:315
             internal/config/config_test.go (TestNoRefusalEchoesTheSuppliedValue)
  requirements: acceptance bullet 5 (docs at the strength of the control)

Observed:
  config.go:333 — "TestNoRefusalEchoesTheSuppliedValue drives this and every
  other refusal in the loader with a runtime-assembled marker".
  AGENTS.md:315 — "TestNoRefusalEchoesTheSuppliedValue drives every refusal path
  in the loader with a marker assembled at run time".
  The loader has 17 `v.addf` sites. Running the test under
  -coverprofile shows 6 executed (287, 344, 361, 374, 391, 501) and 11 not
  (378, 395, 412, 416, 459, 474, 478, 484, 490, 496, 505).
  I read all 17 format strings: NONE interpolates a supplied value, so the
  PROPERTY holds everywhere; only the claim about the test's reach is wrong.
  The companion clause of AGENTS.md:315 — "every refusal row of the boot matrix
  greps the process output for the value it supplied" — is TRUE
  (boot-matrix.sh:333-337, applied to every refusal row).

Failure:
  A reader budgets no further work because the sentence says the test already
  covers everything. If someone later adds the offending value to, say, the
  clock-skew ceiling message (line 412), TestNoRefusalEchoesTheSuppliedValue
  will not catch it — a marker cannot reach that branch, which needs a valid
  but too-large duration.

Perspective:
  developer

Recommendation:
  Replace "every refusal path in the loader" with what is true in both places —
  "every refusal a marker-shaped value can reach (the mode, the retired name,
  the listen address, the three durations, the byte ceiling and the key), plus
  Config.String() and Config.LogValue()" — and note that the remaining paths
  take no value argument at all.

Acceptance criteria:
  - No sentence claims the test drives every refusal in the loader.
  - The sentence names either the covered paths or the reason the rest cannot
    echo (they interpolate only constants).

Tests:
  None required; the wording is the defect. If broader coverage is ever wanted,
  the smallest honest version is a table-driven case per addf site supplying a
  value of the shape that branch requires.

Cross-repo implications:
  core: none | user: none | search: two sentences | meta: none

Challenge:
  Every refusal in the loader does in fact fail to echo, so the sentence is true
  about the SYSTEM even though it is false about the TEST, and no defect can
  reach a user today. Counter: it is stated as "That sentence is a test, not a
  habit" — an explicit claim of mechanism, which is the thing that is wrong.
```

```
FINDING 5: one stale enumeration of core's vocabulary survives in a test comment
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/config/config_test.go:155-156
  requirements: acceptance bullet 5

Observed:
  config_test.go:155-156 still reads "VIZRA_SEARCH_MODE is core's search
  TOPOLOGY variable (off | managed | external) and means that, and only that,
  product-wide." `git diff 852b382..6a02ab2` does not touch this line.
  Everywhere else is clean: AGENTS.md:249/262/282, README.md:51 and config.go
  all describe the variable without enumerating core's values.
  The accompanying claim that "every `off | managed | external` enumeration was
  removed from this repo's docs and messages" is therefore very nearly, but not
  quite, accurate.

Failure:
  The whole point of the reversal is that this repository holds no copy of
  core's vocabulary, because a copy goes stale silently. This copy is inert —
  it is a comment, it drives nothing, and no control depends on it — but it is
  the same liability in miniature: if core extends its vocabulary the comment
  becomes wrong and nothing notices.

Perspective:
  developer

Recommendation:
  Delete the parenthetical, leaving "VIZRA_SEARCH_MODE is core's search TOPOLOGY
  variable and means that, and only that, product-wide."

Acceptance criteria:
  - `grep -rn "off | managed | external"` over the repository, excluding
    docs/evidence/**, returns nothing.

Tests:
  None.

Cross-repo implications:
  core: none | user: none | search: one line | meta: none

Challenge:
  It is a comment in a test file, not a doc or a message, so the builder's claim
  was arguably never about it. Accepted — hence NIT, not a hold.
```

## Cross-repo note for the chair — unchanged and still owed

Meta PR #4 (`feat/m0-compose-topology`) still sets `VIZRA_SEARCH_MODE: production` on the **search**
service. Under the NEW policy that is still a **boot refusal** (my matrix row 4 — `production` is
old runtime vocabulary and is the one refused class). **Meta must deliver `VIZRA_MODE: production`**
to the search service. Core's `VIZRA_SEARCH_MODE: ${VIZRA_SEARCH_MODE:-off}` on api/worker stays.
The compose comment above that line ("SEARCH'S OWN vocabulary — `production|development`") is now
doubly wrong and must be rewritten.

## Verdict

The reversal is implemented cleanly and all three round-1 findings are closed. My own 84-combination
matrix, 16 near-miss probes, five reproduced builder mutations, four fresh adversarial mutations,
a coverage measurement of the no-echo test and the full lane set all agree with the PR's claims;
every number in the PR body reproduced exactly. Nothing can reach development without an explicit
`VIZRA_MODE=development`; the named danger and all its normalised spellings still refuse; no
refusal echoes a supplied value; the accepted cost of ignoring unknown values is documented
truthfully and precisely.

The two remaining findings are NITs: one sentence (in two places) overstates how many refusal
paths a test walks, for a property that in fact holds on all of them, and one stale parenthetical
survives in a test comment. Neither is a false promise of safety, neither has an operator-facing
consequence, and neither is of the kind that failed round 1 — where a comment promised a
cross-repo alarm that could never fire and guarded an accepted risk that could bite an operator
on upgrade. I record them for the chair, which may still choose to hold for the one-line fixes.

FINAL VERDICT: PASS — SHA 6a02ab2975a6f5c4da49b5af62b9822ead2e885e
