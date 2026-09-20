# Security review — vizra-search PR #1 (minimal real service) at 7f483addd2fd3d3f7f0842defe5a06f15bdcd48a

Reviewer: `vizra-security` council seat (read-only), dispatched by the war-room chair 2026-09-20. Verbatim, extracted from its transcript by script. The reviewer deliberately withheld the exploit detail of Finding 1; the evidence it kept is an isolated scratch module, no live instance.

**Chair ruling 2026-09-20:** Findings 1, 2 and 3 are BLOCKING for this PR. Finding 1 and the contract side of Finding 2 (negative vectors, normative canonicalisation rules) also apply to vizra-core, whose builder owns `api/` and was told the same day; vizra-search re-vendors from core's new SHA. Findings 4, 5, 8, the named-limitation test of Finding 6, the AGENTS.md rotation note of Finding 7 and parts (b)(c) of Finding 9 are small and sit in files the fix round already touches, so they ride along. Queued, not in this PR: the nonce store and its ledger obligation (before M3 real results), multi-key rotation (before first production deployment), connection/rate caps on the unauthenticated body read (before M3). Finding 9(a), the ruleset, is an owner action.

---

## Verdict

Head confirmed at `7f483ad`. This is the strongest security slice I have reviewed in this repo. The things that usually go wrong here do not: the body is bounded *before* the MAC is computed, a declared `Content-Length` over the cap is refused without a read, a chunked body is bounded by the reader, and — the part most implementations get wrong — the handler parses **exactly the signed bytes** (`h(c, body)` in `/Users/yosefgamble/github/vizra/vizra-search/internal/httpapi/server.go:308`), so there is no sign-one-thing-parse-another gap. The MAC covers version, method, path, timestamp, nonce and a digest of the raw body; comparison is `hmac.Equal`; an unconfigured verifier fails closed; every 401 is one code and one message with the reason going only to the log. Production is the default mode, the dev key is refused, and no error or probe echoes the key, its length or its hash. Server timeouts, `MaxHeaderBytes`, scratch image, non-root uid, digest-pinned build stage, SHA-pinned actions and `permissions: contents: read` are all present. The contract parser rejects non-local `$ref` across the whole tree and is reachable only from tests, so it is not a runtime SSRF surface. I verified the vendored contract is byte-identical to `vizra-core` at `b0dbeb6` **and** at core HEAD.

Two things break that picture.

First, the clock-skew check does not hold at the extreme end of its input range — a fail-open arithmetic class in the one mechanism that bounds replay at M0, present identically in core's copy. Detail withheld below.

Second, `vizra-core` ships `api/search-hmac-testvectors.json` whose own header says *"vizra-search vendors a byte-identical copy and tests against it"*. It does not. I ran core's five vectors against this verifier myself: all five pass today, so nothing is broken right now — but nothing in CI holds that, and I found two places where the two canonicalisations already differ in normalization. The boundary's most important property, "both sides compute the same bytes", is currently asserted only in prose.

Everything else is follow-up. The replay limitation is documented honestly in three places; I am asking for it to be *tested* and *ticketed*, not re-argued.

---

## BLOCKING — fix before this PR merges

```
FINDING 1: security — needs owner attention: vizra-search internal/hmacauth,
           timestamp-window arithmetic / fail-open on out-of-range input, REQUIRED
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-search  (same shape also in vizra-core)
  files:     internal/hmacauth/hmacauth.go:215-221 (skew computation)
             vizra-core internal/search/hmac.go (Verify, same arithmetic)
  requirements: VZ-SEARCH-004

Observed:
  DETAIL DELIBERATELY WITHHELD — this is a live, unfixed weakness in a boundary
  check and these repositories may be public. What I can say: the acceptance
  window is computed by subtracting two times and folding the sign. For inputs
  at the far end of the representable range that computation does not behave the
  way the code assumes, and the window check does not refuse. I confirmed this
  against the real verifier source in an isolated scratch module (no live
  instance, no remote host, no repository change). The contract's requirement —
  "reject a timestamp more than 300 seconds from its own clock in either
  direction" — is therefore not met for all inputs, and AGENTS.md § HMAC
  boundary states it as though it were.

Failure:
  Reachability requires a valid signature, so this is not an unauthenticated
  bypass. It matters because the timestamp window is the ONLY replay bound at
  M0: a request signed with an out-of-range timestamp never expires. Core signs
  with time.Now(), so a container with a broken clock or a bad NTP step is
  enough to mint one, and anyone who captures it on the compose network can
  replay it indefinitely. TestVerifyRejectsAFutureTimestamp passes because it
  only tries a near-future value.

Perspective: operator, instance-admin

Recommendation:
  Validate the timestamp's magnitude against an explicit sane absolute range
  before it is converted into a time value, and compute the window on plain
  int64 seconds with explicit bounds rather than on the derived duration. Fix
  core's copy in the same round; they are the same three lines.

Acceptance criteria:
  - A correctly signed request whose timestamp lies far outside the window is
    refused, whichever direction it lies in, at every magnitude.
  - The refusal is the same uniform 401 as every other rejection.
  - AGENTS.md's "in either direction" claim is true as written.

Tests:
  internal/hmacauth/hmacauth_test.go — extend TestVerifyRejectsAFutureTimestamp
  into a table over the magnitude range including the extremes, asserting
  ReasonStaleTimestamp. Demonstrate the case fails against the current code
  before the fix (AGENTS.md § Completion and evidence). Mirror it in
  vizra-core internal/search/hmac_test.go.

Cross-repo implications:
  core: same defect in internal/search/hmac.go — fix together.
  user: none | search: as above | meta: none

Challenge:
  "It needs a valid MAC, so it is unreachable." Not quite: it needs a valid MAC
  over a bad clock, and the consequence is a credential with no expiry on the
  one boundary where replay is otherwise time-bounded. It is also three lines.
```

```
FINDING 2: the shared HMAC test vectors are not vendored, so the two
           implementations of the canonical string are cross-checked by nothing
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-search
  files:     api/ (only CONTRACT-SOURCE.json, search-internal.openapi.yaml)
             internal/hmacauth/hmacauth.go:89-105 (SigningString), :206-224
             vizra-core api/search-hmac-testvectors.json
             vizra-core internal/search/hmac.go:48-60 (CanonicalString)
  requirements: VZ-SEARCH-004

Observed:
  Core's vector file states: "Owned by vizra-core; vizra-search vendors a
  byte-identical copy and tests against it. If the two repositories disagree
  here they would sign different bytes and every internal call would 401 in
  production." `ls api/` in this repo returns two files; neither is the vector
  file, and `grep -rn testvector` in vizra-search returns nothing.
  I ran core's five vectors against this repo's verifier in an isolated scratch
  module: canonical string, signature and full Verify all match on all five.
  So the implementations agree TODAY. Two normalization divergences already
  exist and are unguarded:
    - core: `strings.ToUpper(method)`; search: method used verbatim —
      hmacauth.SigningString("post", …) yields "v1\npost\n…".
    - core signs the RAW timestamp header string; search rebuilds it via
      ParseInt→FormatInt, so " 1789000000 ", "+1789000000" and "01789000000"
      all verify against a signature over "1789000000". Core's own Verify
      refuses all three. The contract says "unix seconds, as decimal digits".
  Neither divergence grants an attacker anything: the semantic value is
  unchanged and Echo refuses a lowercase method at the router before auth.

Failure:
  The claim "the two implementations are checked against the same vectors
  rather than against each other's prose" is false on this side. Nothing turns
  red if core changes the scheme — I confirmed core's workflows contain no
  reference to vizra-search or search-internal, and this repo's drift check
  compares the vendored bytes only against its own pinned digest. A scheme edit
  in core produces a two-repo 401 storm discovered in production, and the
  canonical string is not injective over the wire bytes.

Perspective: developer, operator

Recommendation:
  Vendor api/search-hmac-testvectors.json alongside the contract, record it in
  CONTRACT-SOURCE.json with its own sha256, and add a test that every vector's
  canonical_string and signature reproduce exactly and that Verify accepts each.
  Separately, make the timestamp digits-only and uppercase the method in
  SigningString so both canonicalisers normalize identically.

Acceptance criteria:
  - A test fails if any vendored vector's canonical_string or signature differs.
  - contract-drift checks the vector file's digest as it checks the contract's.
  - A timestamp header that is not exactly [0-9]+ is refused.
  - Core's vector file gains NEGATIVE vectors (lowercase method, non-digit
    timestamp, uppercase-hex nonce, padded header) so both sides agree on what
    must be REJECTED, not only on what must be accepted.

Tests:
  internal/hmacauth/vectors_test.go (new) —
  TestVerifierReproducesTheSharedVectors over the vendored file; plus
  TestTimestampHeaderMustBeBareDecimalDigits. Harness exists; this is one file.

Cross-repo implications:
  core: add the negative vectors and pin the same file in its own CI; consider
  a cross-repo job that fails when core's api/ changes without a search
  re-vendor. | user: none | meta: the "both repos drift-check" claim in
  AGENTS.md and in the contract header is currently aspirational — correct it
  or implement it.

Challenge:
  "The vectors pass, so this is paperwork." It is paperwork until someone edits
  CanonicalString on one side; the point of vectors is that the day it happens
  is CI's problem and not the operator's.
```

```
FINDING 3: the clock-skew window and the body cap have no upper bound, so the
           only replay defence is operator-widenable without limit
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/config/config.go:213-228 (duration), :230-245 (bytes),
             :35-36 (DefaultMaxClockSkew, DefaultMaxBodyBytes)
             internal/httpapi/server.go:258-267
  requirements: VZ-SEARCH-004

Observed:
  `duration()` and `bytes()` reject only non-positive values. VIZRA_SEARCH_MAX_CLOCK_SKEW=8760h
  boots cleanly and becomes Verifier.MaxSkew, and MAX_INTERNAL_BODY_BYTES=10737418240
  boots cleanly and becomes the readBounded allocation ceiling. The contract
  fixes both numbers ("300 seconds", "default 1 MiB") and AGENTS.md presents
  the 300 s window as a rule "that must not be relaxed" — but it is a rule about
  the default, not about the accepted range. config_test.go has no ceiling case.

Failure:
  With no nonce store at M0, the timestamp window IS the replay bound. A
  well-meaning operator debugging clock drift sets the skew to an hour and
  silently turns a 10-minute replay window into a two-hour one on the service
  that will, from M3, answer questions about the existence of private photos.
  The body cap is the memory bound on an unauthenticated code path.

Perspective: operator, instance-admin, photographer (at M3)

Recommendation:
  Refuse a skew above the contract's 300 s in production mode (allow a larger
  value only in development, with a logged warning), and refuse a body cap above
  a stated ceiling. Collect both in validate() like every other refusal.

Acceptance criteria:
  - Production boot refuses VIZRA_SEARCH_MAX_CLOCK_SKEW > 300s, naming the
    variable and the contract, never echoing other configuration.
  - Production boot refuses MAX_INTERNAL_BODY_BYTES above the ceiling.
  - Development mode may exceed both, and says so in the log at boot.
  - CheckEnv reports the same refusals, so doctor and CI agree with boot.

Tests:
  internal/config/config_test.go — add cases to TestProductionRefusesUnsafeHMACKeys'
  sibling table (or a new TestProductionRefusesAnOverwideSkewWindow), and one
  case in TestCheckEnvValidatesACandidateEnvFileWithTheBootCode.

Cross-repo implications:
  core: core hard-codes MaxClockSkew = 300*time.Second as a constant and has no
  such knob — so a widened search window is invisible to core. | user: none |
  meta: env templates in the deployment tree must not ship a wider value.

Challenge:
  "An operator who widens the window owns the consequence." True for a
  documented knob; this one is undocumented, unbounded, and sits on the only
  replay bound the service has.
```

---

## Follow-ups (not blocking this PR)

```
FINDING 4: the MAC is verified over the route template, not the request path —
           coverage narrows silently the day a path parameter lands
Severity:    SHOULD   (before M3 real results)
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/httpapi/server.go:271 — s.verifier.Verify(req.Method, c.Path(), …)
             echo/v5@v5.3.1 context.go:260-266, :315 — c.path = ri.Path (the
             REGISTERED route), not the request path
             vizra-core internal/search/hmac.go:95 — path := req.URL.EscapedPath()
  requirements: VZ-SEARCH-004

Observed:
  The contract's third canonical field is "request path, exactly as sent, no
  query string". Core signs EscapedPath(). Search verifies over Echo's route
  template. For the six static ASCII routes these strings are identical, and
  Echo v5 matches on RawPath when it is set (router.go:895-900) and performs no
  path cleaning, so no encoded variant reaches a handler. Nothing is wrong today.

Failure:
  The moment any route carries a parameter — /internal/v1/assets/:id in M3, an
  obvious candidate — c.Path() becomes "/internal/v1/assets/:id" and the actual
  id stops being covered by the MAC, while core keeps signing the concrete path.
  That is a silent narrowing of authenticated coverage with no failing test: the
  first symptom would be a 401 mismatch, the second would be nobody noticing.

Perspective: developer, photographer (at M3)

Recommendation:
  Verify over the request path as sent (req.URL.EscapedPath()), matching core,
  and keep c.Path() for logging only.

Acceptance criteria:
  - The canonical string's path field equals the path bytes core signed.
  - A route registered with a path parameter still has the concrete segment
    inside the MAC.

Tests:
  internal/httpapi/server_test.go — register a throwaway parameterised route in
  a test-only server and assert a signature for /x/a does not authenticate /x/b.
  That case fails against the current code.

Cross-repo implications:
  core: none (core is already correct) | user: none | meta: none

Challenge:
  "No parameterised route exists, so this is hypothetical." Correct — which is
  why it is SHOULD and not blocking. It is also four characters to fix now and a
  subtle incident to fix later.
```

```
FINDING 5: the query string is neither signed nor refused on internal routes
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/httpapi/server.go:250-309 (authenticated); grep for
             RawQuery in this repo returns nothing
             vizra-core api/search-internal.openapi.yaml, securitySchemes —
             "<request path, exactly as sent, no query string>"
  requirements: VZ-SEARCH-004

Observed:
  The canonical string deliberately excludes the query. No handler reads a query
  parameter, and nothing rejects one, so POST /internal/v1/search?anything=x
  authenticates exactly as the unadorned path does.

Failure:
  An attacker on the core↔search network who captures a signed request can
  append or alter a query string without invalidating the signature. It buys
  nothing today. It becomes a real unauthenticated input the first time any
  handler, middleware, cache key or log-correlation shim reads c.QueryParam.

Perspective: developer, operator

Recommendation:
  Refuse any request to /internal/v1/* whose URL carries a query string, with
  the same uniform 401, before verification. That makes the contract's "no
  query string" safe by construction rather than by everyone remembering it.

Acceptance criteria:
  - A correctly signed internal request carrying any query string is refused.
  - The refusal is the same 401 body as every other rejection.

Tests:
  internal/httpapi/server_test.go — TestASignedRequestWithAQueryStringIsRefused,
  next to TestASignatureForOneEndpointDoesNotOpenAnother.

Cross-repo implications:
  core: none — core's client sends no query | user: none | meta: none

Challenge:
  "Signing the query would be the real fix." It would also be a contract change
  in core. Refusing it is strictly smaller and achieves the same safety.
```

```
FINDING 6: the no-nonce-store limitation is documented honestly but is neither
           pinned by a test nor tracked as an obligation with a due milestone
Severity:    SHOULD   (obligation must close before M3 real results)
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/hmacauth/hmacauth.go:23-29 (package doc), AGENTS.md
             § "Known limitation, stated rather than implied",
             api/search-internal.openapi.yaml securitySchemes
             internal/httpapi/routes_test.go:181 TestSignatureRemainsValidInsideTheWindow
  requirements: VZ-SEARCH-004, and propose a tracked sub-item for VZ-SEARCH-001

Observed:
  The exposure is stated in three places and understated in none — this is the
  good version of a known gap. What exists is the positive test above ("a
  4-minute-old signature still works"), framed as the window. What does not
  exist is a test that names the limitation, or a ledger obligation binding
  nonce rejection to the milestone that makes it matter.

Failure:
  The exposure at M0 is bounded: a captured request can be replayed identically
  for up to 300 s, and every reply is not_indexed, so the blast radius is a
  duplicate no-op. At M3 the same replay returns a permission-projected result
  set, and a replayed events batch is an index mutation. A limitation carried
  only in prose is the kind that survives three milestones.

Perspective: instance-admin, photographer

Recommendation:
  Add a test whose name IS the limitation, so the day storage lands the test
  must be rewritten rather than quietly kept passing; and file the obligation
  against the M3 slice with the two properties it must satisfy (nonce
  uniqueness enforced for at least the skew window; rejection is the same
  uniform 401).

Acceptance criteria:
  - A test named for identical-request replay inside the window exists and
    documents the M0 behaviour explicitly.
  - features.json carries a tracked obligation, due before any real result is
    returned, naming the nonce store.
  - The obligation is referenced from AGENTS.md § Known limitation.

Tests:
  internal/httpapi/server_test.go —
  TestIdenticalRequestsCanStillBeReplayedInsideTheWindowAtM0, asserting the
  second call is accepted and citing the contract clause in a comment.

Cross-repo implications:
  core: core must not assume the search side is replay-safe | user: none |
  meta: the obligation belongs in docs/quality/features.json.

Challenge:
  "A test that asserts the weakness looks like blessing it." It is the opposite:
  it makes removing the weakness a visible, mandatory edit.
```

```
FINDING 7: there is no key-rotation path, and the gap is not written down
Severity:    SHOULD   (before first production deployment)
Confidence:  high

Affected:
  repo:      vizra-search
  files:     internal/config/config.go:82-90 (HMACKey []byte — one key),
             internal/hmacauth/hmacauth.go:156-164 (Verifier.Key — one key)
             grep -rni rotat across this repo returns nothing
  requirements: VZ-SEARCH-004; relates to VZ-SECURITY-003 (…, rotation, …)

Observed:
  Exactly one key is read and one key verifies. AGENTS.md's configuration table
  documents SEARCH_HMAC_KEY with no rotation guidance.

Failure:
  Rotating the shared secret requires core and search to change it in the same
  instant. In practice that is a window in which every internal call 401s —
  which by this contract's own rules means search: degraded and vizra doctor
  FAIL. An operator who learns the key leaked has no clean remediation, so the
  realistic outcome is that nobody ever rotates it.

Perspective: operator, instance-admin

Recommendation:
  Accept a comma-separated list in SEARCH_HMAC_KEY (or add SEARCH_HMAC_KEY_NEXT):
  verify against any listed key, with each key held to the same production
  validation. Core signs with the first. That turns rotation into two ordinary
  restarts. If that is out of scope for M0, write the gap into AGENTS.md next to
  the nonce limitation, in the same honest register.

Acceptance criteria:
  - Either: a request signed with any configured key verifies, every configured
    key passes the production key checks, and no error says which key matched;
  - Or: AGENTS.md § Configuration states plainly that rotation requires a
    simultaneous restart of both processes and a brief degraded window.

Tests:
  internal/hmacauth/hmacauth_test.go — TestVerifyAcceptsEitherConfiguredKey and
  TestEveryConfiguredKeyMustPassProductionValidation.
  internal/config/config_test.go — a weak second key is refused.

Cross-repo implications:
  core: core must sign with the primary and be told which one that is |
  user: none | meta: the installer/CLI must generate and stage both values.

Challenge:
  "Two live keys double the exposure." Marginally — and a key nobody can rotate
  is exposed for the life of the instance.
```

```
FINDING 8: `make run` serves the documented public dev key on every interface
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-search
  files:     Makefile, target `run` — VIZRA_SEARCH_MODE=development
             SEARCH_HMAC_KEY=dev-insecure-hmac-key-do-not-use-in-production
             internal/config/config.go:30 DefaultAddr = ":8081"
  requirements: VZ-SEARCH-004

Observed:
  `make run` boots in development mode, where hmacKey() returns the key
  unchecked (config.go:282-284), and binds DefaultAddr ":8081" — all
  interfaces. The key is a published constant. The Dockerfile's ":8081" is
  correct for a container; a bare `make run` on a laptop is not the same thing.

Failure:
  Any device on the developer's network can sign a valid request against their
  running instance, because the key is in the repository. At M0 the answer is
  not_indexed. At M3 it is permission-projected search results — from whatever
  database that developer happens to be pointed at.

Perspective: developer, photographer

Recommendation:
  Set VIZRA_SEARCH_ADDR=127.0.0.1:8081 in the `run` target, and log a warning at
  boot whenever development mode is active so the mode is never a silent state.

Acceptance criteria:
  - `make run` listens on loopback only.
  - Development mode emits a startup warning naming the mode and the fact that
    key validation is relaxed. The warning never contains the key.

Tests:
  cmd/vizra-search/main_test.go — assert the development-mode boot log carries
  the warning and does not carry the key (extend TestLogsNeverCarrySignatureMaterial's
  sibling assertions).

Cross-repo implications:
  core: none | user: none | meta: the base compose file must publish no port for
  this service (ADR-002 / Q-017) — that belongs to the deployment tree and I
  could not verify it from this repo. UNVERIFIED here.

Challenge:
  "Developers know what a dev key is." The ones who do still run it on hotel
  wifi.
```

```
FINDING 9: the CI gate is defined by files the PR it gates can rewrite; the only
           real closure is an owner ruleset that is explicitly not in this PR
Severity:    REQUIRED   (owner action, immediately after merge)
Confidence:  high

Affected:
  repo:      vizra-search
  files:     .github/workflows/ci-required.yml:36-37 — `run: ./scripts/ci-required-guard.sh`
             scripts/ci-required-guard.sh (floor list, continue-on-error check,
             base-image pin check — all inside the file being executed)
             .github/CODEOWNERS (its own NOTE: "advisory until a ruleset requires
             owner review")
             .github/workflows/ci-required.yml:66 — awk '$1==n {print; exit}'
  requirements: VZ-SEARCH-004

Observed:
  The guard correctly closes the manifest loophole: the floor lives outside
  .github/required-checks.txt, entries must be bare job names, continue-on-error
  is refused anywhere in the workflows, and every base image must be digest-
  pinned. I traced each of the four checks and they do what they claim. But the
  guard is checked out from the PR under test and executed from there, so a PR
  can edit the floor in the same commit — the loophole moved one file, it did
  not close. The script's own comment says the floor "lives in the workflow",
  which is not where it lives (it is in the script); AGENTS.md gets this right.
  Separately, the aggregate matches a check by name and takes the FIRST row
  (`exit`), not the most recent, so if two check-runs ever share a name on one
  SHA the gate reads whichever the API happened to list first.

Failure:
  Until the ruleset requiring owner review on /.github/, /scripts/ and
  internal/hmacauth is applied, "ci-required is the gate" is a convention, not a
  control. ADR-002 item 9 is right that ci-required must exist before it can be
  required — which makes applying it the very next action, not an open one.

Perspective: operator, developer

Recommendation:
  (a) Owner applies the ruleset the moment this merges: require the ci-required
  context, require CODEOWNERS review on the listed paths, and disallow bypass.
  (b) Make the aggregate pick the latest check-run per name (sort by started_at)
  or fail loudly when duplicates disagree. (c) Correct the script comment.

Acceptance criteria:
  - A PR that edits scripts/ci-required-guard.sh cannot merge without owner
    review, demonstrated by a recorded blocked attempt.
  - ci-required is a required context on the default branch and in the merge
    queue.
  - Duplicate same-name check-runs on one SHA cannot produce a false green.

Tests:
  Not a Go test. Evidence file under docs/evidence/warroom/ recording the
  ruleset as applied (screenshot or `gh api repos/:owner/:repo/rulesets`), and a
  shell case in the guard's own demonstration set — docs/evidence/m0-demonstrations/
  already has D4a-D4e; add one for "the guard itself was edited".

Cross-repo implications:
  core: same pattern, same ruleset needed | user: same | meta: the CI fan-in
  claim in vizra/AGENTS.md rests on these rulesets existing in all three repos.

Challenge:
  "This is honestly documented, so it is not a finding." Documented is not
  closed, and a self-gating gate is exactly the false-positive-CI class the meta
  contract's code-review rules tell me to look for.
```

Two smaller notes, not filed: an unauthenticated caller can cause up to `MAX_INTERNAL_BODY_BYTES` to be buffered before verification with no connection or rate cap (bounded by the timeouts and a private network — revisit before M3); and `api/CONTRACT-SOURCE.json` pins `source_ref: feat/m0-foundation`, an unmerged core branch, so the pin should be refreshed to the merge commit before release.
