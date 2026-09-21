# Independent verification — vizra-search PR #1 "minimal real service"

| | |
|---|---|
| **Verdict** | **FAIL** |
| PR | <https://github.com/yegamble/vizra-search/pull/1> (`feat/m0-minimal-service` → `main`) |
| Verified SHA | `7f483addd2fd3d3f7f0842defe5a06f15bdcd48a` (head had **not** moved; confirmed via `gh api` at start and end) |
| Slice | item 5 of the VZ-ISSUE-001 PR sequence — Q-001 / ADR-002 minimal real service; search half of `VZ-FOUND-003`, service side of `VZ-SEARCH-004` |
| Verifier | independent agent; did not write this code; no source, test, workflow, manifest, baseline or budget was modified and nothing was pushed |
| Date | 2026-09-20 |

**One-line verdict:** the slice is well built and every acceptance bullet's
*happy path* reproduces, but the HMAC timestamp window — which both the vendored
contract and the code itself state is **the only replay bound in M0** — does not
close in the future direction. A validly signed request bearing a timestamp at
or beyond `11013301709` (2318-12-31Z) is accepted and **never expires**. That is
a BLOCKER. Four further surviving mutants are recorded below.

---

## 1. Environment

| Item | Value |
|---|---|
| Host | macOS 25.5.0, darwin/arm64 |
| Clone | fresh `git clone` of `yegamble/vizra-search`, checked out at `7f483ad`, under the session scratchpad — **not** the builder's checkout. Deleted at the end of this verification. |
| Go | `go1.26.2` locally; `go.mod`'s `toolchain go1.27.1` resolved and was used — `go env GOVERSION` → `go1.27.1`, `go version` → `go1.27.1 darwin/arm64` |
| Docker | Server 29.8.0, linux/arm64. One image built (`vizra-verify-search:local`) and removed; no image named `vidra-*`, `refpin-*`, `vizra-pr1-*`, `vizra-core:*` or `vizra-user:*` was touched. |
| Disk at finish | 15 GiB free |

## 2. Commands run, exit codes, counts

| Command | Exit | Result |
|---|---|---|
| `make ci` (clean clone, `7f483ad`) | **0** | fmt-check clean · `go vet ./...` clean · echo-containment clean · build links · contract-drift ok (2 pkgs) · `go test -race -count=1 ./...` ok (6 pkgs) |
| `make test-noskip` (inside `make ci`) | **0** | **187 pass events, 0 skips, 0 fails** — matches the builder's claim exactly |
| `go test -count=1 -json ./...` | 0 | `pass=187 skip=0 fail=0`; 181 run events; 122 top-level `Test` functions |
| `make tidy-check` | **0** | `go.mod`/`go.sum` tidy (note: **not** part of `make ci`; it is a separate CI job) |
| `./scripts/ci-required-guard.sh` | **0** | floor · bare names · job existence · digest pinning all pass |
| `go mod verify` | 0 | all modules verified |
| `go install golang.org/x/vuln/cmd/govulncheck@v1.8.0` + `govulncheck ./...` | 0 | `Go: go1.27.1 / Scanner: govulncheck@v1.8.0 / DB: https://vuln.go.dev / DB updated: 2026-09-16 18:00:43 UTC` → `No vulnerabilities found.` |
| `docker build -t vizra-verify-search:local .` | 0 | 10 426 199 B (10.4 MB), `User=65532:65532` |
| `make ci` re-run after every mutation was restored | **0** | working tree verified clean (`git status --porcelain` empty) at finish |

## 3. GitHub CI on the verified SHA

`gh api repos/yegamble/vizra-search/commits/7f483add.../check-runs` returns
**12 check runs, all `completed` / `success`**, each with real `started_at` and
`completed_at` timestamps — no check is skipped, cancelled, timed out, missing
or neutral:

```
build              completed success  18:19:12 → 18:20:09
ci-required        completed success  18:19:12 → 18:21:00
contract-drift     completed success  18:19:13 → 18:19:53
docker-build       completed success  18:19:13 → 18:20:02
echo-containment   completed success  18:19:14 → 18:19:34
fmt                completed success  18:19:13 → 18:19:31
GitGuardian        completed success  18:19:07 → 18:19:08
govulncheck        completed success  18:19:12 → 18:20:02
test               completed success  18:19:13 → 18:20:39
test-noskip        completed success  18:19:13 → 18:20:04
tidy-check         completed success  18:19:13 → 18:19:33
vet                completed success  18:19:12 → 18:19:56
```

`ci-required` ran **on this SHA** (run 35528668043) and its log ends
`ci-required: every required check succeeded on 7f483addd2fd3d3f7f0842defe5a06f15bdcd48a`.
Its guard step printed the full manifest, the floor result, the bare-name result,
the job-existence result and the digest result. Manifest lanes (10) = jobs that
actually executed (10); **no lane is listed but unrun**. The two extra checks are
`ci-required` itself and GitGuardian (not in the manifest, therefore not gated —
informational only).

**Chair Q1 — does `test-noskip` really fail on a skipped test, and did all 12
lanes execute?** Yes to both. The lane parses `go test -json` and fails on
`"Action":"skip"` *and* on fewer than 40 pass events, so an empty run also fails.
Its `187 pass events, 0 skips` reproduced identically on my host and on the
runner. All 12 checks executed with real durations.

**Chair Q2 — govulncheck.** `v1.8.0` exists on the module proxy
(`2026-09-08T20:52:42Z`, origin hash `709015412431dd2b5b28a53c06c70bc02d49074c`).
The lane prints scanner and DB identity in its own step
(`Scanner: govulncheck@v1.8.0`, `DB updated: 2026-09-16`) before scanning, so the
green tick is attributable. A scanner crash **still fails the gate**: the scan is
a plain `run:` step, a panic exits non-zero, the job fails and `ci-required` fails
with it — empirically demonstrated by the PR's own first run, where `v1.1.4`
panicked and `ci-required` went red rather than silently passing.

**Chair Q3 — go.mod pins.** `go1.27.1` is listed in the upstream `go.dev/dl`
index (alongside `go1.27.0`) and the toolchain directive actually resolved it on
my host. All modules resolve and `go mod verify` passes. `go mod tidy` is clean.
Nothing contradicts ADR-001: Go toolchain line 1.27 (ADR-001 allows lines 1.26
and 1.27; `go 1.26.0` is the language directive, `toolchain go1.27.1` is the
toolchain) and `echo/v5 v5.3.1` satisfies "≥ v5.3.1". ADR-001 names the Echo
containment package `internal/http`; this repo uses `internal/httpapi` — the
*intent* (one package, greppable) is met and enforced by `make echo-containment`.
Informational only.

**Chair Q6 — image.** `User=65532:65532` in the image config and `docker top`
shows PID 1 running as UID `65532`. `FROM scratch` is the only undigested base;
the build stage is `golang@sha256:69a7b978…`, and `scripts/ci-required-guard.sh`
enforces the rule (mutation D4d below turns it red).

## 4. Vendored contract provenance

| Check | Result |
|---|---|
| Vendored `api/search-internal.openapi.yaml` sha256 | `5bf9dd22a2209dbfacb99f4c2d2d620ff15e0465f9b98228ec120983a3bf448a`, 21 551 bytes |
| `api/CONTRACT-SOURCE.json` claims | same sha256, same byte count, commit `b0dbeb6dc27294fe793492ea60bc18b6aed4b042` |
| `vizra-core` at `b0dbeb6` | **byte-identical** (`diff` empty; same sha256, same size) |

**Has core changed the file since?** **Yes — and the brief's stated core head
`2d51dad` is stale.** `yegamble/vizra-core` `feat/m0-foundation` is now at
**`2b9c540e81960954ee39e6a2aeec027e0f764a67`**, whose commit is
`fix(search): close the HMAC timestamp window; pin the reject set in the vectors`.
The contract file went 21 551 → 24 797 bytes (sha256
`9723a4582e075bab77c2dd802bd1f03f163e1c03af5335aefa2b305b32b0614a`). Exactly what
differs, in the `securitySchemes.hmacSignature` description:

1. **Every canonical field is now VERBATIM.** No implementation may uppercase,
   trim, reparse or reformat. The text names the exact defect: "one side rebuilt
   the timestamp through `ParseInt`→`FormatInt`, so `" 1789000000 "`,
   `"+1789000000"` and `"01789000000"` verified there and were refused by the
   other."
2. **Timestamp** must match `^[1-9][0-9]*$` and its *magnitude* must be validated
   against an absolute range — `≥ 1000000000` and `≤ 4102444800` — **before** any
   arithmetic. The text states why: "Deriving a time value from the header and
   folding the sign of the difference does NOT close the window: at the ends of
   the representable range that arithmetic wraps, and a validly signed request
   with a timestamp of `253402300799` was accepted and never expired."
3. **Nonce** max 128 hex chars (this PR allows 256).
4. **Each of the three headers appears exactly once**; a duplicate is rejected,
   not resolved.
5. **Method** used exactly as sent, rejected if not uppercase — not uppercased.
6. A new normative conformance file `api/search-hmac-testvectors.json`, whose
   `vectors` (ACCEPT) *and* `negative_vectors` (REJECT) an implementation MUST
   consume.
7. `search_schema_version`'s asymmetry across `SearchResponse` /
   `SuggestResponse` / `EventAck` is now documented as deliberate — which closes
   the builder's observation 2 to the chair.

Per the brief, a moved contract is a finding for the chair, not a failure of this
PR. **However**, I independently reproduced defect (2) in this PR's own code, and
it violates the **vendored** `b0dbeb6` contract too ("reject a timestamp more than
300 seconds from its own clock in either direction"). That is FINDING 1 and it is
not excused by the contract having moved.

## 5. Demonstrations I reproduced myself

Method: apply the mutation to the clean clone, run the lane, restore, confirm
green. Every restore was verified with `git status --porcelain` and a green
`make ci`.

| ID | Mutation | Lane | Exit | Killed by |
|---|---|---|---|---|
| D1a | `pathSuggestions` renamed to `/internal/v1/suggest` | `make ci` | **2** | `TestNoDriftFromTheCanonicalContract`, `TestResponseBodiesSatisfyTheContractSchemas` |
| D1b | response field `results` → `hits` | `make ci` | **2** | `TestResponseBodiesSatisfyTheContractSchemas` — "required property \"results\" is missing" |
| D1c | `http.StatusTeapot` added to `/readyz` Emitted | `make ci` | **2** | `TestNoDriftFromTheCanonicalContract`; "no provoker for 418" |
| D1d | vendored contract edited in place (header comment) | `make ci` | **2** | `TestVendoredContractMatchesItsManifest` |
| D4e | non-local `$ref` (`https://evil.example/…`) in the contract | `make ci` | **2** | manifest sha256 **and** `internal/contract`'s local-ref refusal, before resolution |
| D2b | `hmac.Equal(provided, expected)` → `provided[:1], expected[:1]` | `make ci` | **2** | `TestVerifyRejectsASignatureThatDiffersOnlyInTheLastByte`, `TestVerifyUsesTheDocumentedConstantTimePrimitive` |
| D2d | `sha256.Sum256(body)` → `sha256.Sum256(nil)` | `make ci` | **2** | `TestVerifyRejectsATamperedBody`, `TestVerifyRejectsATruncatedBody`, `TestSigningStringIsCanonicalAndStable`, `TestTamperedBodiesAreRejected` |
| D3b | `if len(key) < MinProductionKeyBytes` neutered | `make ci` | **2** | `TestProductionRefusesUnsafeHMACKeys/{short,one_byte_below_the_floor}` |
| D3a | `if key == DevHMACKey` neutered **only** | `make ci` | 0 | **survives — correctly so.** The documented key still starts `dev-`, caught by `placeholderPrefixes`; behaviour is unchanged. Equivalent mutant; the builder's analysis is right. Widening it (D4/N16 below) does turn it red. |
| D4a | `govulncheck` deleted from the manifest | `ci-required-guard.sh` | **1** | `FLOOR VIOLATION: 'govulncheck' … is absent` |
| D4b | `docker-build # optional` in the manifest | `ci-required-guard.sh` | **1** | bare-job-name rule |
| D4c | `continue-on-error: true` on the `govulncheck` job | `ci-required-guard.sh` | **1** | "continue-on-error is not allowed on a required lane" |
| D4d | `FROM golang:1.27.1-bookworm` (tag, not digest) | `ci-required-guard.sh` | **1** | `UNPINNED BASE IMAGE` |
| — | a manifest entry naming a job that does not exist | `ci-required-guard.sh` | **1** | job-existence rule |

**Every demonstration I sampled reproduces.** No claimed red/green was
unreproducible.

## 6. Live behaviour of the built image (arm64, native)

Built from the clean clone, run as UID 65532, production mode, a fresh
`openssl rand -hex 32` key:

| Probe | Result |
|---|---|
| Dev placeholder key in production mode | refused, exit 1: `SEARCH_HMAC_KEY is the documented development placeholder and is refused in production mode` |
| Empty key | refused, exit 1: `SEARCH_HMAC_KEY must be set` |
| `GET /healthz` | `{"status":"ok"}` |
| `GET /readyz` | `{"status":"ok","components":[],"search_schema_version":null,"checked_at":"…"}` |
| `GET /version` | `{"release":…,"commit":…,"built_at":…,"go_version":"go1.27.1","image_digest":null,"search_schema_version":null}` |
| Signed `POST /internal/v1/search` | `200 {"status":"not_indexed","results":[],"total":0,"search_schema_version":null}` |
| Signed `/internal/v1/suggestions` | `200 {"status":"not_indexed","suggestions":[]}` |
| Signed `/internal/v1/events` | `200 {"status":"not_indexed","accepted":0,"duplicates":0}` |
| Container `HEALTHCHECK` | `healthy`, failing streak 0 |
| SIGTERM | logs `draining` then `stopped`; drain path exercised |

**Chair Q4 — is the 401 indistinguishable across causes, and are secrets absent
from logs?** Yes on both counts. All seven rejection causes returned a
**byte-identical** body — no headers at all, missing nonce only, bad MAC (last
byte flipped), stale timestamp with a valid MAC, cross-endpoint replay, tampered
body, malformed nonce — every one:

```
401 {"error":{"code":"signature_rejected","message":"request authentication failed"}}
```

Oversize bodies are handled separately and **before** authentication, returning
`413 payload_too_large` — that is what the vendored contract mandates ("reject a
body above `MAX_INTERNAL_BODY_BYTES` *before* reading it, with 413"), so it is a
resource bound, not an authentication oracle. Container logs across all of the
above carried **zero** occurrences of the key, any nonce, any signature, any
`X-Vizra-*` header value, or the query term `sunset`; the boot line reads
`"hmac_key":"[redacted]"`. Refusal lines carry only `method`, `path`, `status`
and a stable non-sensitive `reason` — operator-facing, correctly withheld from
the caller.

**Chair Q5 — is the body bounded before it is read for the MAC, and are
deadlines propagated?** Yes. `internal/httpapi/server.go:258-267` refuses a
declared `Content-Length` above the limit without reading a byte (proven by
`TestADeclaredContentLengthAboveTheLimitIsRefusedWithoutAByteRead`, which uses an
`explodingReader`), then `readBounded` reads at most `limit+1`. I confirmed both
paths against the running image — a 2 MiB declared body **and** a 2 MiB chunked
body with no `Content-Length` both returned `413`. A verifier-only probe measured
exactly **1025 bytes read for a 1024-byte limit** on the undeclared-length path.
Deadlines: `server.go:296-301` wraps the request context and `http.Server` bounds
`ReadHeaderTimeout` / `ReadTimeout` / `WriteTimeout` / `IdleTimeout` /
`MaxHeaderBytes` (`cmd/vizra-search/main.go:99-109`). *But see FINDING 2 — the
streaming half of the bound has no test.*

## 7. Surviving mutants

The builder reported two survivors, both closed, plus one correct equivalent
mutant (D3a). I looked for a third. I found **five more survivors across four
distinct gaps**, one of which is a live defect rather than a coverage gap.

| # | Mutation | `make ci` | Finding |
|---|---|---|---|
| S1 | *(none — this is a defect in unmutated code, see FINDING 1)* | — | **BLOCKER** |
| S2 | `readBounded(req.Body, s.cfg.MaxBodyBytes)` → `readBounded(req.Body, 1<<62)` | **0 — survives** | FINDING 2 |
| S3 | `io.ReadAll(io.LimitReader(r, limit+1))` → `io.LimitReader(r, limit)` | **0 — survives** | FINDING 2 |
| S4 | `DefaultMaxClockSkew = 300 * time.Second` → `720 * time.Hour` | **0 — survives** | FINDING 3 |
| S5 | `DefaultMaxBodyBytes = 1<<20` → `1<<30` | **0 — survives** | FINDING 3 |
| S6 | the draining 503 answered **before** HMAC verification | **0 — survives** | FINDING 4 |
| S7 | `slog.String("body", string(body))` added to the 401 refusal log | **0 — survives** | FINDING 5 |

Mutants that were **killed** (i.e. the tests do hold here), beyond the builder's
list: unbounded-future skew via removing the `abs` fold; dropping the path from
the canonical string (cross-endpoint replay); dropping the method; swapping the
nonce/timestamp order; neutering nonce validation; neutering the
unconfigured-verifier fail-closed guard; comparing only the first 16 or only the
last 16 MAC bytes; removing the `Content-Length` pre-check; neutering the skew
check outright; lowering the key floor to 1 byte; emptying `placeholderPrefixes`;
returning a non-nil `SearchSchemaVersion`; disclosing the rejection reason in the
401 body; logging the signature header; removing the config key redaction. The
suite is genuinely strong — these findings are its edges, not its centre.

---

## FINDING 1: the HMAC timestamp window does not close in the future direction — a validly signed request beyond 2318 never expires

```
Severity:    BLOCKER
Confidence:  high
```

**Affected**
- repo: `vizra-search`
- files: `internal/hmacauth/hmacauth.go:210-216` (the skew computation);
  `internal/hmacauth/hmacauth_test.go` (`TestVerifyRejectsAFutureTimestamp`);
  `internal/httpapi/server_test.go:363-372` (`TestFutureTimestampsAreRejected`)
- requirements: `VZ-SEARCH-004` (service side of the core↔search boundary),
  `VZ-FOUND-003` (search half); acceptance bullet **A9** of the slice brief;
  Q-001; ADR-002 § Search service and boundary

**Observed**

```go
	skew := v.now().Sub(time.Unix(unixSeconds, 0))
	if skew < 0 {
		skew = -skew
	}
	if skew > v.MaxSkew {
		return reject(ReasonStaleTimestamp)
	}
```

`time.Time.Sub` **saturates**: for a far-future argument it returns
`math.MinInt64` rather than wrapping or erroring. Negating `math.MinInt64` in
two's complement yields `math.MinInt64` again — still negative — so `skew` stays
negative, `skew > v.MaxSkew` is false, and the request is **accepted**. Measured:

```
ts=253402300799         Sub=-9223372036854775808  abs=-9223372036854775808  abs>300s? false
ts=4611686018427387904  Sub=-9223372036854775808  abs=-9223372036854775808  abs>300s? false
ts=4102444800           Sub=-2312515150789318000  abs= 2312515150789318000  abs>300s? true   (correctly rejected)
```

End-to-end through the real router with a correctly signed request:

```
X-Vizra-Timestamp: 1789929649          (2026-09-20) -> ACCEPTED 200   (control, valid)
X-Vizra-Timestamp: 1789930049          (2026-09-20) -> REJECTED 401   (control, +400 s)
X-Vizra-Timestamp: 4102444800          (2100-01-01) -> REJECTED 401
X-Vizra-Timestamp: 253402300799        (9999-12-31) -> *** ACCEPTED 200 ***
X-Vizra-Timestamp: 4611686018427387904 (year 1.4e11) -> *** ACCEPTED 200 ***
```

Binary search puts the boundary at **`11013301709` (2318-12-31T18:28:29Z)**:
`11013301708` is rejected, `11013301709` and everything above it is accepted. The
past direction is safe (`Sub` saturates positive, the fold leaves it positive, so
it is rejected — confirmed for `ts=0`, `ts=-253402300799`, `ts=-(1<<62)`).

This is exactly the defect `vizra-core` describes in its own newer contract
(`2b9c540`): *"at the ends of the representable range that arithmetic wraps, and
a validly signed request with a timestamp of `253402300799` was accepted and
never expired."* The same sentence names the consequence: *"Until `vizra-search`
owns a nonce store, this window is the ONLY replay bound, so it has to actually
close."*

The existing tests do not reach it: both future-timestamp tests derive their
fixture from `config.DefaultMaxClockSkew + time.Minute`, i.e. `now + 360 s`,
which is inside the non-saturating range.

**Failure**

The timestamp window is the sole replay bound at M0 — stated in
`internal/hmacauth/hmacauth.go`'s package comment, in the vendored contract at
`b0dbeb6`, and in core's newer contract. With the window open at the top end, a
request signed once with a far-future timestamp is a **permanently valid
credential**: it can be captured off the wire (the boundary is plain HTTP on the
internal network — the Dockerfile's own comment calls it "a private network") and
replayed forever against `/internal/v1/search`, `/internal/v1/suggestions` and
`/internal/v1/events`. It also means the acceptance bullet A9 "a
timestamp/replay rule" is only half true, and demonstration D2c ("stale timestamps
accepted → RED") proves the rule exists without proving it closes.

At M0 the blast radius is bounded — the service holds no index, so a replayed
search returns `not_indexed` — but the boundary is the security seam this whole
slice exists to establish, and it will be carrying real projections by M3 against
this same code.

**Perspective**

operator, developer — and, once M3 lands on this code, member and photographer
(a replayable internal search call is a permission-bypass primitive once there
are rows to project).

**Recommendation**

The smallest change is the one core's contract already specifies: validate the
timestamp's **magnitude against an absolute range before any time arithmetic**.
In `Verify`, after `strconv.ParseInt` and before the `Sub`:

```go
const (
	minUnixSeconds = 1000000000 // 2001-09-09
	maxUnixSeconds = 4102444800 // 2100-01-01
)
if unixSeconds < minUnixSeconds || unixSeconds > maxUnixSeconds {
	return reject(ReasonMalformedTimestamp)
}
```

Compute the skew on plain `int64` seconds rather than through `time.Duration`, so
no saturation is possible at all. Also fail closed when the verifier's *own*
clock falls outside that range, as the contract requires.

Re-vendoring core's contract at `2b9c540` and adopting
`api/search-hmac-testvectors.json` is the fuller fix (see FINDING 6), but the
range check alone closes the hole.

**Acceptance criteria**

- A correctly signed request with `X-Vizra-Timestamp` of `253402300799`,
  `11013301709`, `4611686018427387904` or any value `> 4102444800` returns
  **401** with the standard indistinguishable body.
- A correctly signed request with `X-Vizra-Timestamp` `< 1000000000` returns 401.
- A correctly signed request inside ±300 s still returns 200.
- The 401 body remains byte-identical to every other rejection cause.
- The skew arithmetic cannot saturate: no `time.Duration` carries a value derived
  from an unvalidated header.

**Tests**

`internal/hmacauth/hmacauth_test.go` — extend `TestVerifyRejectsAFutureTimestamp`
into a table that includes `253402300799`, `11013301709`, `1<<62` and
`4102444800+1`, each with a genuine signature over its own fields so only the
range rule can refuse it, plus the mirror below `1000000000`. Add a boundary case
at exactly `4102444800` and `1000000000`. Mirror the end-to-end case in
`internal/httpapi/server_test.go` alongside `TestFutureTimestampsAreRejected`.
The harness exists; no new tooling is needed. A mutation test that removes the
range check must turn `make ci` red.

**Cross-repo implications**

- core: already fixed on its side in `2b9c540`; core's verifier and this one must
  agree on the reject set or the boundary is unusable. none further.
- user: none.
- search: this finding.
- meta: the ledger must not record `VZ-SEARCH-004` as IMPLEMENTED on the current
  SHA.

**Challenge**

The strongest counterargument: at M0 the service holds no index and no storage,
so a replayed request returns `not_indexed` and leaks nothing — the practical
impact today is zero, and core's own contract was only fixed hours ago, so this
PR implemented the contract as it stood. I still call it BLOCKER because the
vendored `b0dbeb6` contract already said "reject a timestamp more than 300
seconds from its own clock **in either direction**", and this does not; because
the code's own package comment asserts a replay bound it does not deliver; and
because a security seam that is wrong when it is empty does not get more correct
when it is full.

---

## FINDING 2: the streaming request-body bound has no test — it can be deleted and `make ci` stays green

```
Severity:    REQUIRED
Confidence:  high
```

**Affected**
- repo: `vizra-search`
- files: `internal/httpapi/server.go:261` and `:329-341` (`readBounded`);
  `internal/httpapi/server_test.go:464-495`
- requirements: slice acceptance **A11** ("bounded request size"); meta
  `AGENTS.md` § Engineering guardrails ("bound request, file, decoder,
  subprocess, and queue resources")

**Observed**

The product is **correct today** — I verified a 2 MiB chunked body returns 413
against the running image, and a verifier-only probe measured exactly 1025 bytes
read against a 1024-byte limit. But every 413 test builds its request with
`httptest.NewRequest(..., bytes.NewReader(huge))`, which sets
`req.ContentLength`, so all three are satisfied by the **declared-length**
pre-check alone. Two mutations of the streaming bound survive `make ci`:

```
readBounded(req.Body, s.cfg.MaxBodyBytes) -> readBounded(req.Body, 1<<62)   make ci exit 0
io.LimitReader(r, limit+1)                -> io.LimitReader(r, limit)        make ci exit 0
```

Under the first, my probe measured the server buffering **4096 bytes against a
1024-byte limit** and answering 401 instead of 413 — while the repo's own
`internal/httpapi` suite stayed green.

**Failure**

Nothing is broken on this SHA. The gate is: a future PR can remove the only
defence against an unbounded body from a peer that sends chunked transfer
encoding or lies about `Content-Length`, and CI will not notice. The PR body
cites `TestADeclaredContentLengthAboveTheLimitIsRefusedWithoutAByteRead` as the
evidence for A11, which covers only half of the bound.

**Perspective** operator, developer

**Recommendation**

Add one negative test for the undeclared-length path. No product change.

**Acceptance criteria**

- A request to each internal path with `ContentLength = -1` and a body of
  `4 × MAX_INTERNAL_BODY_BYTES` returns **413** `payload_too_large`.
- The server reads at most `limit + 1` bytes from that body (assert with a
  counting reader).
- Widening `readBounded`'s limit, or changing `limit+1` to `limit`, turns
  `make ci` red.

**Tests**

`internal/httpapi/server_test.go` — a sibling of
`TestADeclaredContentLengthAboveTheLimitIsRefusedWithoutAByteRead`, e.g.
`TestAnUndeclaredLengthBodyAboveTheLimitIsRefusedAfterLimitPlusOneBytes`, using a
`countingReader` wrapper and `req.ContentLength = -1`. The harness exists.

**Cross-repo implications** core: none · user: none · search: this finding · meta: none

**Challenge**

One could argue `net/http` already rejects an over-long chunked body upstream, or
that the declared-length test is "close enough". Neither is true: `net/http`
imposes no body-size limit of its own, and the mutation demonstrably survives.

---

## FINDING 3: the two numeric limits the canonical contract fixes are not pinned to the contract

```
Severity:    REQUIRED
Confidence:  high
```

**Affected**
- repo: `vizra-search`
- files: `internal/config/config.go:35-36`; `internal/config/config_test.go:50-54`;
  `internal/httpapi/server_test.go:363,372`
- requirements: slice acceptance **A9** (replay rule) and **A11**; Q-001;
  the vendored contract's `securitySchemes.hmacSignature` text

**Observed**

The contract fixes two numbers: "reject a timestamp more than **300 seconds**
from its own clock in either direction" and "`MAX_INTERNAL_BODY_BYTES` (default
**1 MiB**)". Both survive mutation:

```
DefaultMaxClockSkew = 300 * time.Second -> 720 * time.Hour   make ci exit 0
DefaultMaxBodyBytes = int64(1 << 20)    -> int64(1 << 30)    make ci exit 0
```

The only assertions are tautologies against the constants themselves —
`config_test.go:50`: `if cfg.MaxClockSkew != config.DefaultMaxClockSkew` — and the
stale/future fixtures in `server_test.go` are *derived* from
`config.DefaultMaxClockSkew`, so they move with the mutation.

**Failure**

A PR can widen the replay window from 5 minutes to 30 days — an 8640× increase in
the lifetime of the only replay bound this service has — and CI stays green.
Same for the body bound at 1024×. Both are values the contract, not this repo,
owns.

**Perspective** operator, developer

**Recommendation**

Assert the two constants against the **literal contract values**, with a comment
naming the contract clause, so drift from a number core owns is a test failure.
Ideally read them out of the vendored contract in the drift check, the way routes
and schemas already are.

**Acceptance criteria**

- `config.DefaultMaxClockSkew == 300 * time.Second` is asserted against the
  literal, with the contract clause cited.
- `config.DefaultMaxBodyBytes == 1 << 20` likewise.
- Changing either constant turns `make ci` red.

**Tests**

`internal/config/config_test.go` — `TestDefaultsMatchTheCanonicalContract`.
Stronger option: extend `internal/httpapi/contract_drift_test.go` to parse the
`hmacSignature` description for `300` and `1 MiB` and compare, so a change in core
turns search red the way a renamed route already does.

**Cross-repo implications** core: owns both numbers; a change there should turn search red · user: none · search: this finding · meta: none

**Challenge**

These are defaults, overridable by `MAX_INTERNAL_BODY_BYTES` and
`VIZRA_SEARCH_MAX_CLOCK_SKEW`, so an operator can already set anything — which
makes pinning the *default* arguably cosmetic. The counter: the default is what
every deployment gets, it is the value the contract names, and Finding 1 shows
this exact area is where the boundary breaks.

---

## FINDING 4: the drain 503 can be moved ahead of authentication without a test noticing

```
Severity:    SHOULD
Confidence:  high
```

**Affected**
- repo: `vizra-search`
- files: `internal/httpapi/server.go:248-293`
- requirements: ADR-002 § Probes; slice acceptance A1/A9

**Observed**

`server.go:249` documents the order as "the body bound, HMAC verification and a
request deadline, in that order", and the drain check correctly sits *after*
verification at `:291`. Moving it above the `Verify` call leaves `make ci` at
exit 0 — no test pins the ordering.

**Failure**

Not broken today. Under the mutation an **unauthenticated** caller learns whether
the instance is draining — a small fact about an internal service, disclosed
before any credential is checked. It is the same class of ordering regression the
codebase is otherwise careful about.

**Perspective** operator

**Recommendation** One assertion that a draining server answers an *unsigned*
internal request with 401, not 503.

**Acceptance criteria**
- With `BeginDrain()` called, an unsigned POST to each internal path returns
  **401** with the standard body, not 503.
- A correctly signed POST to a draining server returns **503** `unavailable`.
- Reordering the two checks turns `make ci` red.

**Tests** `internal/httpapi/server_test.go` — extend the existing draining tests
with the unsigned variant. Harness exists.

**Cross-repo implications** core: none · user: none · search: this finding · meta: none

**Challenge** The information disclosed is trivial and `/readyz` is unauthenticated
anyway, so a caller can learn the drain state without any credential. Fair — which
is why this is SHOULD, not REQUIRED. The value is pinning a documented ordering.

---

## FINDING 5: the 401 refusal log path is not covered by the redaction test, so a request body could be logged

```
Severity:    SHOULD
Confidence:  high
```

**Affected**
- repo: `vizra-search`
- files: `internal/httpapi/server.go:279-284`; `internal/httpapi/server_test.go:557-579`
- requirements: ADR-002 § Logging and redaction; meta `AGENTS.md` ("Never log
  credentials, private signed URLs, or raw private metadata")

**Observed**

`TestLogsNeverCarrySignatureMaterial` is a good test — it checks the signature,
the nonce, the shared secret *and* the body term `secret-term`. But it drives a
**successfully signed** request, so only the `INFO "request"` line is exercised.
Adding `slog.String("body", string(body))` to the `WARN "request refused"` line at
`:279` survives `make ci` at exit 0.

**Failure**

Nothing is logged today that should not be — I confirmed against the running
image. The gap is that the rejection path is unguarded, and it is the path most
likely to carry a *legitimate* user's search query: a request refused for clock
skew or a key rotation is core's real query text, now in the log.

**Perspective** member, photographer (query text is user data), operator

**Recommendation** Drive the same redaction assertions over a rejected request.

**Acceptance criteria**
- After an unsigned, a stale-timestamp and a bad-MAC request each carrying
  `{"query":"secret-term"}`, the log contains none of: the key, the nonce, the
  signature, `secret-term`.
- Adding the body (or any header value) to the refusal log turns `make ci` red.

**Tests** `internal/httpapi/server_test.go` — parameterise
`TestLogsNeverCarrySignatureMaterial` over signed and each rejected case.

**Cross-repo implications** core: none · user: none · search: this finding · meta: none

**Challenge** On the rejection path the body is an *attacker's* body, so logging
it is arguably a feature. Not so: the commonest cause of a 401 here is core's own
clock skew or a rotated key, and that body is a real member's query.

---

## FINDING 6: core's canonical contract has moved and now forbids the normalisation this PR performs — for the chair, not a failure of this PR

```
Severity:    REQUIRED  (scheduling, not this PR's gate)
Confidence:  high
```

**Affected**
- repo: `vizra-search` (primary); `vizra-core` owns the contract
- files: `vizra-search` `api/search-internal.openapi.yaml`, `api/CONTRACT-SOURCE.json`,
  `internal/hmacauth/hmacauth.go:180-200`; `vizra-core` `api/search-internal.openapi.yaml`
  at `2b9c540`, plus the new `api/search-hmac-testvectors.json`
- requirements: Q-001; ADR-002 § Contracts; `VZ-SEARCH-004`

**Observed**

The vendored bytes are a perfect match for `b0dbeb6` and
`api/CONTRACT-SOURCE.json` is truthful. Core's branch head has since moved to
`2b9c540` (the brief's `2d51dad` is stale) and **has** changed the file
(21 551 → 24 797 bytes). Section 4 above lists exactly what differs. Against the
new rules, this PR's verifier currently **accepts** input the new contract says
must be refused — reproduced with genuine signatures:

```
X-Vizra-Timestamp: "01789929623"    -> ACCEPTED   (leading zero; contract: ^[1-9][0-9]*$)
X-Vizra-Timestamp: "+1789929623"    -> ACCEPTED   (sign; contract: no sign)
X-Vizra-Timestamp: "  1789929623  " -> ACCEPTED   (whitespace; contract: refuse, do not trim)
```

Cause: `Verify` does `strings.TrimSpace` then `strconv.ParseInt`, and
`SigningString` rebuilds the field with `strconv.FormatInt` — the exact
`ParseInt`→`FormatInt` round-trip core's new text names as the divergence that
"had already happened". Also divergent: nonce max 256 here vs 128 in the new
contract; duplicate headers resolved by `Header.Get` (first value) rather than
rejected. And the new normative `api/search-hmac-testvectors.json` is not
consumed by either repo's drift check yet.

**Failure**

Two implementations of one scheme that disagree about which requests are valid.
Not exploitable on its own, but it is precisely the failure mode the contract now
exists to prevent, and it will surface as intermittent 401s between core and
search the moment both sides are strict on different rules.

**Perspective** developer, operator

**Recommendation**

A follow-up slice: re-vendor `api/search-internal.openapi.yaml` at core's then-head,
implement the verbatim-field rules (reject rather than normalise), lower the nonce
ceiling to 128, reject duplicated headers, and wire
`api/search-hmac-testvectors.json` into `make contract-drift` so both `vectors`
and `negative_vectors` are consumed. FINDING 1's range check is the part of this
that must not wait.

**Acceptance criteria**
- `api/CONTRACT-SOURCE.json` pins core's current commit and its sha256, and the
  vendored bytes match.
- `" 1789000000 "`, `"+1789000000"`, `"01789000000"`, an uppercase-hex nonce, a
  129-char nonce and a duplicated `X-Vizra-*` header each return 401.
- Every `vectors` entry verifies and every `negative_vectors` entry is refused,
  as a CI lane.

**Tests** a new `internal/hmacauth/testvectors_test.go` driving
`api/search-hmac-testvectors.json`, added to the `contract-drift` lane.

**Cross-repo implications**
- core: owns the contract and the vectors; must confirm `2b9c540` is the version
  to vendor and whether its own verifier already conforms.
- user: none.
- search: this finding.
- meta: the chair should record that the contract moved after this PR was opened,
  so the drift is not read as the builder having edited a vendored file.

**Challenge**

This PR vendored the contract that existed when it was written, recorded the
commit honestly, and cannot be faulted for a change made afterwards — so arguably
it is entirely a follow-up. Agreed, and that is why it is separated from FINDING 1.
The part that is *not* a follow-up is that the overflow also violates the
**vendored** `b0dbeb6` text.

---

## 8. Audit against the AGENTS.md review rules

| Hunt item | Result |
|---|---|
| Privacy leaks | None found. Logs carry no key, nonce, signature, header value or query text; `Config.String`/`LogValue` both redact; mutations that leak the key or signature are killed. *Coverage gap on the refusal path — FINDING 5.* |
| Missing negative tests | **FINDINGS 2, 3, 4, 5** — four distinct gaps, five surviving mutants. |
| Weakened or deleted assertions | None. The two assertions the builder reports strengthening (`7abf369`, `ee4bdb7`) are genuinely stronger — I confirmed by re-running D2b and D3b, both now red. |
| Skips | Zero. 187 pass, 0 skip, 0 fail, reproduced on my host and on the runner. `test-noskip` also fails an empty run (< 40 pass events). |
| Hand-edited generated files | None. The vendored contract is byte-identical to its source and pinned by sha256; editing it in place turns CI red (D1d). |
| Invented package APIs | None. `echo/v5 v5.3.1`, `gopkg.in/yaml.v3 v3.0.1`; `go mod verify` passes; `go mod tidy` clean; `govulncheck@v1.8.0` exists upstream. |
| Unbounded resources | Body bound present and working on both paths; server-level read/write/idle/header limits set; event batch capped at 500; nonce length capped. *Streaming bound untested — FINDING 2.* |
| Secrets / private data in logs | None observed live or in the CI transcript. |
| Mock data in production paths | None. `not_indexed` with `total: 0`, `accepted: 0` is the honest answer and the code comments say why a non-zero count would be a lie. |
| Dead controls / fake success | None. `500` is declared-not-emitted with a written reason rather than faked; `search_schema_version` is `null` rather than a guess; `components: []` rather than a fabricated healthy component. |
| False-positive CI | The fan-in guard is real: floor, bare names, job existence, `continue-on-error`, digest pinning — all five reproduce red. Manifest lanes == lanes that ran. *Caveat: `fmt`, `vet`, `echo-containment`, `tidy-check` and `docker-build` are not in the floor and could be removed from the manifest by a future PR; only `build`, `test`, `test-noskip`, `contract-drift`, `govulncheck` are protected. Informational.* |
| Unsupported readiness claims | The PR body is accurate. Every claim I checked — 187/0, the contract sha256 and byte count, the govulncheck diagnosis and pin, the two survivors and the equivalent third, the D-transcripts, CI green, "no contract change needed" — matched what I observed. The PR correctly says READY_FOR_REVIEW, not verified, and correctly lists what did not run. One stale detail: the execution plan's § Files still names `contracts/search-internal.openapi.yaml` + `contracts/MANIFEST.json`, which became `api/…` + `api/CONTRACT-SOURCE.json`. NIT. |

## 9. Verdict

**FAIL.**

- **FINDING 1 (BLOCKER)** — the HMAC timestamp window does not close above
  `11013301709`; a validly signed request beyond 2318 is accepted forever, and
  this window is the only replay bound the service has. Reproduction is in the
  finding; the fix is an absolute-range check before the arithmetic.
- **FINDINGS 2, 3 (REQUIRED)** — five surviving mutants across the streaming body
  bound and the two contract-fixed numeric limits.
- **FINDINGS 4, 5 (SHOULD)** — ordering and refusal-path-logging coverage.
- **FINDING 6 (REQUIRED, follow-up)** — core's contract has moved to `2b9c540`
  and now forbids normalisation this implementation performs; for the chair to
  schedule, not a fault of this PR.

`ci-required` **is** green on `7f483ad` and every one of the 12 checks genuinely
ran; the head has not moved. The CI gate is sound — it simply never asked the
question FINDING 1 answers.

This verdict is not a merge and does not make any ledger entry VERIFIED. Once
FINDING 1 is fixed and FINDINGS 2–5 are closed or explicitly deferred by the
chair, the PR should come back for re-verification at the new SHA; I would expect
that round to be short, because everything else in this slice reproduced.

## 10. Housekeeping

The verification clone was deleted; the one image I built
(`vizra-verify-search:local`) and its container were removed and the build cache
left at the size it was; no container or image belonging to another workstream
was touched. Nothing in `vizra-core` was modified — it was read through
`git show` and the GitHub API only.

---
---

# Re-verification at `ab41219` — fix round 1

| | |
|---|---|
| **Verdict** | **PASS** |
| Re-verified SHA | `ab41219bb99cd4fdec483d967ff361ce5f577ae8` (head had **not** moved; confirmed at start and finish) |
| Previous verdict | FAIL at `7f483ad` (above). It does not carry over; everything below was re-established from a fresh clone. |
| Delta | 5 commits, 59 files, +4422 −223 |
| Date | 2026-09-20 |
| Verifier | same independent agent; still did not write this code; no source, test, workflow, manifest, baseline or budget modified; nothing pushed |

**One-line verdict:** the BLOCKER is closed — closed properly, at the root, with
the arithmetic made unreachable rather than the symptom patched — and all five of
my other findings are closed with tests that kill the exact mutants that
survived last round. Two new non-blocking findings, both about lane scoping
rather than product behaviour.

## R1. Environment and commands

Host macOS 25.5.0 darwin/arm64, `go1.27.1` (resolved via `go.mod`'s toolchain
directive), Docker 29.8.0 linux/arm64, 15–17 GiB free throughout. Fresh
`git clone` of `yegamble/vizra-search` at `ab41219` in the session scratchpad,
plus a read-only scratch clone of the local `vizra-core` at `2b9c540` for the
cross-repo vector check. Both deleted at the end.

| Command | Exit | Result |
|---|---|---|
| `make ci` (clean clone) | **0** | fmt-check · vet · echo-containment · build · contract-drift (3 pkgs) · `go test -race` (6 pkgs) · test-noskip · **tidy-check** |
| `make test-noskip` | **0** | **320 pass events, 0 skips** — matches the builder's claim exactly |
| `go test -count=1 -json ./...` | 0 | `pass=320 skip=0 fail=0`; 314 run events; **162** top-level `Test` functions (was 122) |
| `./scripts/ci-required-guard.sh` | **0** | manifest · **workflows parsed: 2; no continue-on-error** · floor · bare names · job existence · digest pinning · **testdata fixture self-test** |
| `go test ./internal/search/ -run Vector` in `vizra-core@2b9c540` | 0 | core's own vector suite, for the cross-repo comparison |

`tidy-check` is now inside `make ci` (ride-along delivered).

## R2. Re-vendored contract and vectors (instruction A)

| File | Vendored sha256 | Bytes | vs `vizra-core@2b9c540` |
|---|---|---|---|
| `api/search-internal.openapi.yaml` | `9723a4582e075bab77c2dd802bd1f03f163e1c03af5335aefa2b305b32b0614a` | 24 797 | **byte-identical** (`diff` empty) |
| `api/search-hmac-testvectors.json` | `3b6b0595bc4cf5f85210ad981dc2c42daf1e73b3beaf191b95eecf0923113cb2` | 21 939 | **byte-identical** |

`api/CONTRACT-SOURCE.json` was restructured from flat keys to a `files[]` array
and states both digests and both byte counts truthfully, pinned to the full
40-character commit `2b9c540e81960954ee39e6a2aeec027e0f764a67`. I confirmed
independently that `2b9c540` is still core's **last commit touching `api/`** —
core's branch head has since moved to `e45e784`, but nothing after `2b9c540`
changes either file, so the vendoring target is correct.

Mutation evidence that both digests are enforced (under `make ci`):

| Mutation | `make ci` |
|---|---|
| the OpenAPI file edited in place | **KILLED** — `TestEveryVendoredFileMatchesItsManifest` |
| the vectors file edited in place | **KILLED** — also by `TestVerifierReproducesTheSharedVectors` |
| `CONTRACT-SOURCE.json` vectors sha256 replaced with zeros | **KILLED** |
| `CONTRACT-SOURCE.json` OpenAPI sha256 replaced with zeros | **KILLED** |

The instruction's sub-clause "and that **contract-drift** checks both digests" is
where NEW FINDING 7 below applies: the digest test runs, but not in that lane.

## R3. THE BLOCKER — closed (instruction B)

### Behaviour: the real router, genuine signatures, 19 wire values

Every value outside the rule returned the **uniform 401** with a byte-identical
body; the control returned 200.

```
"1789932049"           -> 200  control: now
"4102444800"           -> 401  MaxTimestampUnix exactly (in range, far outside window)
"4102444801"           -> 401  MaxTimestampUnix+1
"11013301708"          -> 401  one below my old boundary
"11013301709"          -> 401  MY OLD BLOCKER BOUNDARY  (was 200 at 7f483ad)
"253402300799"         -> 401  year 9999                (was 200 at 7f483ad)
"4611686018427387904"  -> 401  1<<62                    (was 200 at 7f483ad)
"9223372036854775807"  -> 401  max int64
"0"                    -> 401     "-1"          -> 401     "999999999"    -> 401
"1000000000"           -> 401  MinTimestampUnix exactly (far past -> stale)
"01789929623"          -> 401  leading zero
"+1789929623"          -> 401  plus sign
"  1789929623  "       -> 401  surrounding whitespace
"1789929623 "          -> 401  trailing space
"0x6AF7B0D7"           -> 401  hex
"1789929623.0"         -> 401  decimal point
"１７８９９２９６２３"  -> 401  fullwidth digits
```

Confirmed again against a **running process** (native binary, production mode):
`ts=253402300799` → 401, `ts=+<now>` → 401.

### Mechanism: the hole is unreachable, not merely unreached

`internal/hmacauth/hmacauth.go:357-384` now shape-checks
`^[1-9][0-9]*$` (`isBareDecimalDigits`, ≤ 20 chars), then range-checks the
magnitude against `[MinTimestampUnix=1000000000, MaxTimestampUnix=4102444800]`,
and only then computes `skewSeconds := nowUnix - unixSeconds` on plain `int64`.
No `time.Duration` in the file is derived from an unvalidated header. The
verifier's own clock is range-checked first and fails closed
(`ReasonVerifierClock`).

### Reopen attempts — all seven die

| Mutation | `make ci` | Killed by |
|---|---|---|
| range check neutered | **2** | `TestTimestampWindowClosesAcrossTheWholeMagnitudeRange` (4 subtests) |
| upper bound only removed | **2** | same — `one_above_the_range_ceiling`, `year_9999`, both boundary rows |
| lower bound only removed | **2** | same — `one_below_the_range_floor`, `one` |
| **reverted to the old `v.now().Sub(time.Unix(...))` + sign fold** | **2** | `TestTheSkewArithmeticCannotSaturate` |
| bare-digit shape check neutered | **2** | `zero`, `leading_zero`, `leading_zeros`, `leading_plus` |
| leading-zero rule relaxed to `[0-9]` | **2** | same, **and** `TestVerifierRefusesEveryNegativeVector` |
| verifier's own-clock check removed | **2** | `TestAVerifierWithAnInsaneClockFailsClosed` |

`TestTheSkewArithmeticCannotSaturate` is the right kind of test: it reads the
package source and asserts both that the skew is computed on `int64` seconds and
that the range check **precedes** the arithmetic — pinning the ordering property,
not just the symptom.

**FINDING 1 (BLOCKER): CLOSED.**

## R4. My five other findings — all CLOSED

Each of the six mutants that survived `make ci` at `7f483ad` was re-applied
verbatim to `ab41219`:

| # | Mutation (unchanged from round 1) | Then | Now | Killed by |
|---|---|---|---|---|
| S2 | `readBounded(req.Body, 1<<62)` | survived | **KILLED (2)** | `TestAnUndeclaredLengthBodyAboveTheLimitIsRefusedAfterLimitPlusOneBytes` (all 3 paths) |
| S3 | `io.LimitReader(r, limit+1)` → `limit` | survived | **KILLED (2)** | same |
| S4 | `DefaultMaxClockSkew` 300s → 720h | survived | **KILLED (2)** | `TestTheContractsFixedNumbersMatchTheImplementation` |
| S5 | `DefaultMaxBodyBytes` 1 MiB → 1 GiB | survived | **KILLED (2)** | same |
| S6 | drain 503 moved ahead of HMAC verify | survived | **KILLED (2)** | `TestADrainingServerStillRefusesAnUnsignedRequestFirst` (all 3 paths) |
| S7 | raw body logged on the 401 refusal path | survived | **KILLED (2)** | `TestTheRefusalPathNeverLogsTheRequestBody` (`unsigned`, `wrong_key`) |

- **FINDING 2 (streaming body bound untested): CLOSED.**
- **FINDING 3 (contract-fixed numbers unpinned): CLOSED**, and hardened beyond
  what I asked: `MaxProductionClockSkew` (= the contract's 300 s) and
  `MaxProductionBodyBytes` (8 MiB) are now *refused* at boot in production, not
  merely asserted in a test. Verified live:
  `VIZRA_SEARCH_MAX_CLOCK_SKEW=1h` → boot refused; `MAX_INTERNAL_BODY_BYTES=99999999`
  → boot refused. `CheckEnv` reports the same refusals
  (`TestCheckEnvReportsTheCeilingRefusals`). Seven further mutations of the
  ceilings — removing either one, no-oping `ceilings()`, widening the constant
  10× — all die.
- **FINDING 4 (drain ordering): CLOSED.**
- **FINDING 5 (refusal-path logging): CLOSED.**
- **FINDING 6 (contract had moved): CLOSED** — see R2 and R7.

## R5. New code this round — mutation sweep

| Mutation | `make ci` / guard | Killed by |
|---|---|---|
| `Verify(..., req.URL.EscapedPath(), ...)` → `c.Path()` | **KILLED** | `TestTheVerifiedPathIsTheRequestPathNotTheRouteTemplate` |
| query-string refusal removed | **KILLED** | `TestASignedRequestWithAQueryStringIsRefused` (4 forms) |
| duplicate-header rule relaxed to first-value | **KILLED** | `TestVerifierRefusesEveryNegativeVector/timestamp-duplicated-header` |
| `IsPublishedKey` neutered | **KILLED** | 4 tests incl. `TestTheVectorsPublishedKeyIsStillTheOneWeRefuse` |
| `VectorsHMACKey` constant drifted by one character | **KILLED** | "the vendored vectors publish a key this loader does not refuse" |
| `publishedTestKeys` emptied | **KILLED** | — |
| `ceilings()` no-op / skew ceiling / body ceiling / ceiling widened 10× | **KILLED** ×4 | `TestProductionRefusesAnOverwideSkewWindow`, `TestProductionRefusesAnOverlargeBodyCap`, `TestDefaultsMatchTheCanonicalContract` |
| `continue-on-error` as a **quoted key** | **KILLED (guard 1)** | `check-workflows.py` names `jobs.govulncheck.continue-on-error` |
| `continue-on-error` **capitalised** (`Continue-On-Error`) | **KILLED (guard 1)** | same, case-folded |
| `continue-on-error: ${{ true }}` (**expression**) | **KILLED (guard 1)** | same — "the value is irrelevant" |
| `FORBIDDEN` constant in the checker neutered | **KILLED (guard 1)** | the guard's own testdata self-test |
| the checker made case-sensitive | **KILLED (guard 1)** | same |

The `continue-on-error` guard is a genuine improvement: at `7f483ad` it was a
`grep` for a YAML key pattern; it is now a parser that unquotes and case-folds
the key, ignores the value, fails closed on an unparseable workflow, and is
itself exercised against six fixtures on every run.

**Live re-confirmation on the running binary** (production mode, fresh key):
signed search → 200 `not_indexed`; same signature **+ `?x=1`** → 401; far-future
timestamp → 401; `+<now>` timestamp → 401; duplicated `X-Vizra-Timestamp` → 401;
uppercase-hex nonce → 401. Log contained **0** occurrences of the key and **0**
of the query term `sunset`; refusal reasons appear only as log fields
(`query_string_not_permitted`, `timestamp_out_of_range`, `malformed_timestamp`,
`duplicate_header`, `malformed_nonce`) and never in a response body.

I did **not** rebuild the image locally. The Dockerfile is unchanged this round
apart from the binary it compiles, I validated the image shape at `7f483ad`
(non-root UID 65532, `FROM scratch` the only undigested base), and the
`docker-build` lane on `ab41219` ran the full end-to-end on `ubuntu-24.04`
amd64: dev key refused, probes served, `search_schema_version is null, as Q-001
requires`, unsigned call 401, signed call `not_indexed`.

## R6. TEST-CHANGE CHECK (instruction 4) — the chair's specific concern

I read every removed and changed line in all six files. **No assertion was
weakened.** Ruling file by file:

| File | Removed | Ruling |
|---|---|---|
| `internal/httpapi/routes_test.go` (−1) | one `hmacauth.Sign(…)` → `SignAt(…)` | **Legitimate.** Forced rename: `Sign` now takes the verbatim timestamp **string**; `SignAt` is the `time.Time` convenience wrapper. No assertion touched. |
| `internal/hmacauth/hmacauth_test.go` (−7) | six `Sign` → `SignAt`; `SigningString(m, p, 1_774_000_000, …)` → `SigningString(m, p, "1774000000", …)` | **Legitimate.** Same forced rename. The golden `want` string is **character-for-character unchanged** — `"v1\nPOST\n/internal/v1/search\n1774000000\n" + testNonce + "\n953d56a8…"`. Only the call form changed. |
| `internal/httpapi/server_test.go` (−5) | three `Sign` → `SignAt`; `const testKey = "9f2c…"` | **Legitimate and stronger.** The literal *had* to go — production now refuses every key committed to this repository. It became `var testKey = mustFreshKey()` in the new `freshkey_test.go`: a fresh random key per run that is re-drawn if it collides with a published key. |
| `cmd/vizra-search/main_test.go` (−1) | `const strongKey = "9f2c…"` | **Legitimate and stronger.** Same cause, same replacement; plus three *new* tests (dev-mode warning, no warning in production, `make run` binds loopback). |
| `internal/config/config_test.go` (−19) | `const strongKey`, and `envWith(…)` → `envWith(t, …)` throughout | **Legitimate and stronger.** The literal is now a refused published key; `envWith` mints a fresh one per call. The key round-trip assertion survives as `if string(cfg.HMACKey) != env[config.EnvHMACKey]`. |
| `internal/httpapi/contract_drift_test.go` (−24) | the flat single-file manifest struct and `TestVendoredContractMatchesItsManifest` | **Legitimate and materially stronger.** Replaced by `TestEveryVendoredFileMatchesItsManifest`, which loops over **both** vendored files checking sha256 *and* byte count, asserts `source_path == vendored_path` per file, asserts a full 40-character `source_commit`, asserts a non-empty `role`, and — the part that matters most — asserts the manifest **still pins both known paths**, so silently dropping one from `files[]` fails. One file checked became two, with more properties each. |

### The two corrections the builder made — both upheld

**(i) An empty `X-Vizra-Timestamp` value is "present-but-malformed", not
"missing".** Upheld, and it is not a weakening.

- The contract's only normative statement here is that rejection is "always 401
  with body `{"error":{"code":"signature_rejected"}}` and MUST NOT say which
  rule was broken" (line 303). It imposes **no** requirement on the internal
  reason code.
- The vectors' `timestamp-empty` case carries only
  `"must_reject": true` and a prose `"reject_because": "the header must be
  present and non-empty"`. I enumerated every field of every negative vector:
  **no vector names a reason or code an implementation must return.**
  `must_reject: true` is satisfied either way, and search's vector test passes it.
- The new classification is *more* accurate — the header **is** present, with an
  empty value; `exactlyOnce` correctly distinguishes present-once-empty from
  absent — and the genuinely absent case is still covered by
  `TestVerifyRejectsAMissingTimestamp` (still present, alongside the missing
  signature and nonce tests).
- The reason is log-only and never reaches the caller; I re-confirmed the 401
  body is byte-identical across all six live rejection causes.

**(ii) ACCEPT vectors are judged against their own timestamps, because
`verifier_now_unix` is scoped to the negative vectors.** Upheld — this is what
core's file literally says and what core's own verifier does.

- The vector file's own `_comment` ends: *"Negative vectors are judged against
  `verifier_now_unix` as the verifier's clock."* It scopes the field to the
  negative half explicitly. In the raw JSON, `verifier_now_unix` sits **after**
  `vectors` and immediately before `window`/`negative_vectors`.
- The alternative reading is self-contradictory. `verifier_now_unix` is
  `1789000000` and `max_clock_skew_seconds` is `300`, but the ACCEPT vectors
  carry timestamps `1789000000`, `1789000000`, `1789000123`, `1789000456`,
  `1789000789` — **two of the five would be stale** at that clock. The vector
  file would fail against itself.
- **Decisive cross-repo check:** core's `TestHMACTestVectors` (the ACCEPT half,
  `internal/search/search_test.go:75`) does not reference `VerifierNowUnix` at
  all and never calls `Verify` — it checks body hash, canonical string and
  signature only. `vf.VerifierNowUnix` appears solely in core's
  `TestHMACNegativeTestVectors`. **Core scopes the field exactly as the builder
  read it.**
- Worth recording: search's `TestVerifierReproducesTheSharedVectors` goes
  *further* than core's accept-half — it actually runs `Verify` against each
  accept vector at that vector's own timestamp. Stronger, not weaker.

**No cross-repo disagreement on either point.**

## R7. Vector agreement (instruction 5)

Ran core's own suite in a read-only scratch clone at `2b9c540`:

| Suite | vizra-search | vizra-core |
|---|---|---|
| ACCEPT vectors | `TestVerifierReproducesTheSharedVectors` — **5/5 pass** | `TestHMACTestVectors` — **5/5 pass** |
| REJECT vectors | `TestVerifierRefusesEveryNegativeVector` — **24/24 pass** | `TestHMACNegativeTestVectors` — **24/24 pass** |
| Signature genuineness | (covered by the accept half) | `TestNegativeVectorSignaturesAreGenuine` — pass |

**Both implementations accept and reject exactly the same 5 + 24 vectors**, name
for name, including every case that was the divergence: `method-lowercase`,
`method-mixed-case`, `timestamp-leading-plus/zero/zeros/space`,
`timestamp-trailing-space`, `timestamp-underscores`, `timestamp-hex`,
`timestamp-empty`, `timestamp-zero/one`, `timestamp-year-10000`,
`timestamp-duration-overflow-ahead/far`, `timestamp-max-int64(-overflow)`,
`nonce-uppercase-hex/not-hex/too-short/empty`, `timestamp-duplicated-header`.

## R8. CI on `ab41219` (instruction 6)

**12 check runs, all `completed` / `success`**, every one with real start and
finish timestamps:

```
build 19:15:17→19:15:54   ci-required 19:15:17→19:16:45   contract-drift 19:15:19→19:16:10
docker-build 19:15:17→19:16:07   echo-containment 19:15:17→19:15:34   fmt 19:15:17→19:15:36
GitGuardian 19:15:14→19:15:15    govulncheck 19:15:17→19:16:09   test 19:15:18→19:16:40
test-noskip 19:15:18→19:15:59    tidy-check 19:15:18→19:15:40    vet 19:15:17→19:16:04
```

`ci-required` ran **on this SHA** (run 35531691429) and its guard step printed
the manifest, `workflows parsed: 2; no continue-on-error on any job or step`,
the floor, bare names, job existence, digest pinning and the new fixture
self-test. `govulncheck` printed `Go: go1.27.1 / Scanner: govulncheck@v1.8.0 /
DB updated: 2026-09-16` → `No vulnerabilities found`. `test-noskip` printed
`320 pass events, 0 skips`. Manifest lanes (10) == lanes that executed (10).

### The new latest-check-run aggregate, unit-tested

`scripts/ci-required-select.sh` extracted from the workflow and driven directly
with synthetic TSV:

| Input | Exit | Behaviour |
|---|---|---|
| two lanes, both success | 0 | pass |
| one lane `failure` | 1 | fail |
| `skipped` / `cancelled` / `timed_out` / `neutral` | 1 each | **none is a pass** |
| a required lane absent from the rows | 2 | `NEVER RAN` |
| no rows at all | 2 | every lane `NEVER RAN` |
| `in_progress` | 2 | pending |
| **stale `success` listed first, newer `failure` second** | **1** | `AMBIGUOUS — 2 check-runs share this name and their conclusions disagree`, rows printed |
| newer `success`, older `failure` | 1 | same — fails loudly rather than picking a winner |
| two agreeing successes | 0 | `(2 runs with this name, all agreeing)` then pass |
| older completed success + newer still running | 2 | pending, not a pass |

The order-dependence that could have let a stale SUCCESS mask a current FAILURE
is closed, and the "disagreeing duplicates" case fails loudly rather than
silently choosing — which is the correct call.

---

## NEW FINDING 7: the vendored-digest test dropped out of the `contract-drift` lane when it was renamed

```
Severity:    SHOULD
Confidence:  high
```

**Affected**
- repo: `vizra-search`
- files: `Makefile:61-63` (the `contract-drift` recipe);
  `internal/httpapi/contract_drift_test.go:75`
- requirements: `VZ-SEARCH-004`; ADR-002 § Contracts; fix-round instruction (A)
  "…and that **contract-drift** checks both digests"

**Observed**

The `contract-drift` lane selects tests by regex:

```
go test -count=1 -run 'Contract|Drift|Schema|Q001|Secured|Vector|Shared|Negative|Window|RejectClass' \
        ./internal/httpapi/ ./internal/contract/ ./internal/hmacauth/
```

The digest test was renamed this round:
`TestVendoredContractMatchesItsManifest` → `TestEveryVendoredFileMatchesItsManifest`.
The old name contained `Contract` and matched; the new one matches no alternative
in the regex. Enumerating what the lane actually runs in `internal/httpapi`
confirms it: 14 tests selected, and `TestEveryVendoredFileMatchesItsManifest` is
**not** among them.

Consequence, by mutation:

```
the OpenAPI file edited in place          -> make contract-drift  exit 0  (SURVIVES)
CONTRACT-SOURCE.json sha256 zeroed        -> make contract-drift  exit 0  (SURVIVES)
                    the same two mutations -> make ci              exit 2  (KILLED)
```

The vectors file is still caught in the lane, but by its *content*
(`TestVerifierReproducesTheSharedVectors` matches `Vector`), not by its digest.

**Failure**

Nothing is unprotected: `make ci` and the `test` lane both catch every case, and
`test` is a floor lane, so the guarantee remains inside the floor. What is wrong
is narrower and still worth fixing — the lane whose *name* and whose place in the
floor exist to mean "the vendored contract has not been edited" no longer runs
the test that proves it, and the fix-round instruction asked specifically for
that lane. A future developer reading a green `contract-drift` would draw a
conclusion the lane no longer supports, and a `-run` regex is a silent coupling:
renaming a test can remove it from a lane with no signal at all.

**Perspective** developer, operator

**Recommendation**

Smallest fix: add `Manifest|Vendored` to the `contract-drift` regex. Better:
have the lane assert it selected the tests it means to — or drop the regex and
give the drift tests their own build tag or package, so a rename cannot silently
de-scope them.

**Acceptance criteria**
- `make contract-drift` runs `TestEveryVendoredFileMatchesItsManifest`.
- Editing either vendored file in place, or zeroing either sha256 in
  `CONTRACT-SOURCE.json`, makes **`make contract-drift`** exit non-zero.
- Renaming a drift test cannot remove it from the lane without a failure.

**Tests** A lane-composition assertion: enumerate the selected test names and
fail if any test in `contract_drift_test.go` is missing from the selection.

**Cross-repo implications** core: none · user: none · search: this finding · meta: none

**Challenge** The protection is fully intact under `make ci`, which is what CI
runs and what `ci-required` gates, so this is arguably cosmetic. Fair — hence
SHOULD, not REQUIRED. It is recorded because a `-run` regex that silently
de-scopes on rename is exactly the kind of false-confidence coupling this
project's review rules tell reviewers to hunt.

---

## NEW FINDING 8: the workflow-checker's fixture self-test passes silently if its fixture directory disappears

```
Severity:    NIT
Confidence:  high
```

**Affected**
- repo: `vizra-search`
- files: `scripts/ci-required-guard.sh:114-128`

**Observed**

```bash
for fixture in scripts/testdata/wf-*.yml; do
```

Pointing that glob at a directory that does not exist leaves the guard at
**exit 0**: the unmatched glob passes through as a literal, `check-workflows.py`
fails on the non-existent file, the `if` is therefore false, and no error is
raised. Mutation `scripts/testdata` → `scripts/testdata-absent` survives.

**Failure**

Nothing today — the six fixtures exist and are exercised on every run, and I
proved they catch a neutered checker. But a self-test that cannot notice its own
fixtures vanishing is one deletion away from being decorative.

**Perspective** developer

**Recommendation** Count the fixtures and fail if fewer than expected, e.g.
`shopt -s nullglob`, collect into an array, and require the clean fixture plus at
least four negatives.

**Acceptance criteria** Removing or renaming `scripts/testdata/` makes
`./scripts/ci-required-guard.sh` exit non-zero.

**Tests** The guard is itself the harness; one added count assertion suffices.

**Cross-repo implications** core: none · user: none · search: this finding · meta: none

**Challenge** It is a self-test of a self-test; the real gate is the parser
running against the real workflows, which is unconditional. Agreed — NIT.

---

## R9. Finding status at `ab41219`

| # | Finding | Status |
|---|---|---|
| 1 | **BLOCKER** — HMAC timestamp window open above `11013301709` | **CLOSED** — behaviour verified across 19 wire values and live; 7 reopen-mutations all die; fixed at the root (absolute range before arithmetic, `int64` seconds) |
| 2 | streaming body bound untested | **CLOSED** — both mutants die |
| 3 | contract-fixed numbers unpinned | **CLOSED** — pinned to the contract *and* enforced as production boot ceilings |
| 4 | drain 503 ahead of authentication | **CLOSED** — mutant dies |
| 5 | refusal-path body logging uncovered | **CLOSED** — mutant dies |
| 6 | core's contract had moved | **CLOSED** — both files re-vendored byte-identical at `2b9c540`, both digests pinned, vectors consumed, cross-repo agreement proven against core's own suite |
| 7 | digest test dropped out of the `contract-drift` lane | **OPEN** — SHOULD, non-blocking |
| 8 | guard fixture self-test passes if fixtures vanish | **OPEN** — NIT |

## R10. Verdict

**PASS.**

- Every in-scope acceptance bullet reproduced by me, from a clean clone, at this
  SHA — including the six negative-path behaviours I drove against a running
  process.
- `ci-required` is green on `ab41219`; all 12 checks executed with real
  durations; manifest lanes == lanes that ran; the aggregate's new
  latest-check-run logic behaves correctly on all ten unit cases I put to it.
- The head has not moved.
- No blocking finding. The two open findings are SHOULD and NIT, both about lane
  scoping rather than product behaviour, and neither leaves anything
  unprotected under `make ci`.
- The test-change check found **no weakening**. Both corrections the builder
  made are what core's contract and vector file actually say, and core's own
  verifier agrees.

This PASS is not a merge and does not make any ledger entry VERIFIED — the chair
records those. Per Q-032, no ledger entry reaches VERIFIED on CI evidence alone
until branch protection is confirmed applied, which remains an owner action.

Findings 7 and 8 are small enough to fold into the next slice that touches this
repository rather than gating this one; that is the chair's call, not mine.

## R11. Housekeeping

Both scratch clones — `vizra-search@ab41219` and the read-only copy of
`vizra-core@2b9c540` — were deleted. No image was built this round, so nothing
was added to the Docker store and no prune was needed; no container or image
belonging to another workstream was touched. Nothing in the real
`/Users/yosefgamble/github/vizra/vizra-core` checkout was modified — it was read
via `git show`, `git ls-tree` and a `git clone` that does not write to its
source. The only file I wrote is this evidence record.
