# Security review — vizra-core PR #1 (foundation) at e45e78454f101ebbf814dbdcaeef0117ec9a30e0

Reviewer: `vizra-security` council seat (read-only), dispatched by the war-room chair 2026-09-20. Verbatim, extracted from its transcript by script.

**GitGuardian verdict (Finding 4):** no real credential in any branch commit or at HEAD; nothing to rotate. Several synthetic literals are at HEAD by design (redaction-test inputs, README dev block, the HMAC test-vector key).

**Chair ruling 2026-09-20:** must fix before merge — Finding 1 (authz default-ALLOW on an unset visibility), Finding 2 (published test key accepted as a production secret), Finding 3 (value-bearing escape hatch not refused). Riding along in the same round because they are small and the code is open: Finding 5 (`last_error` redaction), Finding 6 (no redirect following on the search client), Finding 8 (the gate guard must parse YAML and refuse `continue-on-error` present-at-all on floor lanes — the chair's merge authority rests on this gate), Finding 9 (hardening headers, Read/WriteTimeout), and Finding 4's per-path, per-reason scanner exclusions under CODEOWNERS plus the `.gitignore` env patterns. Audit table: the backend seat asked for the `ip_prefix` shape CHECK now and this seat asked for immutability in M1 — the CHECK lands now while 0003 is still editable; the UPDATE/DELETE trigger or role separation lands in M1 with the users FK (Finding 10). Queued: Finding 7 (window narrowing + nonce store, M3, cross-repo lockstep), Finding 11 (image scan, clean runtime stage — its own PR), Finding 12 (an OPEN_QUESTIONS entry for the owner on /version and /schemaz disclosure).

---

I confirmed `HEAD = e45e784…`, branch `feat/m0-foundation`, clean tree, and read every file in scope from that checkout.

## What is well built

This is the strongest foundation PR I have reviewed on this project. The HMAC timestamp fix is **real and correctly done**: `ValidateTimestamp` rejects non-canonical shapes, bounds the digit count *before* `ParseInt`, and range-checks against `MinTimestamp`/`MaxTimestamp` before any arithmetic; `WithinWindow` re-checks both operands and fails closed on a nonsense verifier clock (`internal/search/hmac.go:114-175`). The 24 negative vectors are genuinely load-bearing, because `TestNegativeVectorSignaturesAreGenuine` (`internal/search/search_test.go:664`) proves each rejected vector carries a real signature over its own fields — that is the guard that makes a reject-set meaningful, and most projects omit it. Nonce is `crypto/rand`, compare is `subtle.ConstantTimeCompare`, duplicate headers are refused rather than picked, and `Sign` refuses a non-canonical method instead of normalising it.

Elsewhere: `db.Open` and `cache.Open` both deliberately refuse to echo the DSN (`internal/db/db.go:33`, `internal/cache/cache.go:61`), so `doctor` output is clean — I looked for that leak specifically and did not find it. `errorHandler` never returns a 5xx message. `requestIDMiddleware` only accepts a client id that parses as a UUID. The Dockerfile is digest-pinned, checksums the libvips tarball, runs as `10001`, and *asserts* the excluded-codec surface. Workflows have no `pull_request_target`, `permissions: contents: read`, and 40-hex action pins. The authz matrix fixture is a faithful transcription of ADR-007's table — I diffed all 21 rows.

Three things block, all cheap, none in a migration. **The migrations themselves I judge safe to freeze**: constraints are thorough, and the gaps I found (`audit_events` immutability) are additive later, per the repo's own doctrine.

On GitGuardian: I found no real credential in any branch commit or at HEAD. Nothing needs rotating. But the builder's framing is wrong — several credential-shaped literals are still present *at head*, not only in history.

I judge full detail appropriate for findings 1–3: no route in M0 calls `Decide`, so there is nothing reachable to exploit, and the config gates are operator-side. No live-instance recipe is disclosed.

---

# BLOCKING

```
FINDING 1: authz — an unset Visibility defaults to PUBLIC, so the single evaluator is default-ALLOW on a zero-valued Resource
Severity:    BLOCKER
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/authz/authz.go:248-250, :279-282, :321-331, :367-382
             internal/authz/authz_test.go (no case exists)
  requirements: VZ-PRIVACY-001; ADR-007 § Frozen surface × visibility matrix, ruling 5

Observed:
  Decide normalises an empty visibility to the MOST permissive value:

      vis := resource.Visibility
      if vis == "" {
          vis = VisibilityPublic
      }

  and the same for album privacy:

      priv := resource.AlbumPrivacy
      if priv == "" {
          priv = AlbumPublic
      }

  Consequence, with an anonymous Subject{} and a Resource whose Visibility was
  never assigned:

      Decide(ctx, Subject{}, ActionItemPage,            Resource{OwnerID: "u1"}) -> Allow, "public"
      Decide(ctx, Subject{}, ActionFederationOutbound,  Resource{OwnerID: "u1"}) -> Allow, "public"
      Decide(ctx, Subject{}, ActionIPFSPublication,     Resource{OwnerID: "u1", OwnerAllowsIPFS: true}) -> Allow
      Decide(ctx, Subject{}, ActionSharedCache,         Resource{OwnerID: "u1"}) -> Allow
      Decide(ctx, Subject{}, ActionAlbumPage,           Resource{OwnerID: "u1"}) -> Allow, "public"

  The opposite direction is fine: an unknown NON-empty visibility (a future
  'scheduled' or 'moderated' state, or a row read by an older binary during a
  rolling deploy) falls to the private branch and denies. It is specifically
  the zero value that opens.

  The package doc asserts the inverse property — "The zero value is Deny, so a
  code path that forgets to assign one denies" (authz.go:170) — and
  TestZeroDecisionIsDeny (authz_test.go:353) tests it for Decision only. No
  test constructs a Resource with an unset Visibility. TestUnlistedSurfaceDenies
  covers an unknown ACTION, not an unknown VISIBILITY.

Failure:
  The one evaluator every read surface will call fails OPEN on the most common
  programming mistake it exists to catch: a Resource built without its
  visibility. A NULL column scanned into a string, a struct populated before
  the visibility join lands, a hydration path that fills OwnerID first, a test
  helper reused in production code — each yields ALLOW for an anonymous viewer
  on the item page, and, worse, on federation_outbound and ipfs_publication.
  AGENTS.md: "Private media must never reach public IPFS or public federation
  exports." This is exactly the Vidra bug class the package header says it was
  written to prevent ("the opposite of the failure mode that made Vidra fix the
  same privacy bug four times").

  It is not reachable today — no route calls Decide in M0 — which is precisely
  why it must be fixed now, before twenty callers inherit it.

Perspective:
  photographer, member, instance-admin, operator

Recommendation:
  Add ReasonVisibilityUnknown and deny it. Replace the two normalisations with
  an explicit switch: public/unlisted/private proceed; anything else — "" or an
  unrecognised label — returns Deny, ReasonVisibilityUnknown. Same for
  AlbumPrivacy on ActionAlbumPage. Make the caller set the field; that is the
  point of the seam.

  Leave DownloadSetting's "" -> DownloadAll default alone: it is a NARROWING
  setting whose permissive end is the ADR-007 row-2 product default, and the
  column will be NOT NULL DEFAULT 'all'. Say so in a comment so the asymmetry
  is deliberate rather than an oversight.

Acceptance criteria:
  * Decide(ctx, Subject{}, a, Resource{OwnerID: "u1"}) denies for all 21
    Actions, with reason "visibility_unknown".
  * Decide with Visibility("scheduled"), Visibility("moderated") and
    Visibility("PUBLIC") (wrong case) denies for all 21 Actions.
  * ActionAlbumPage with AlbumPrivacy("") denies for A, M and G.
  * The 315-case frozen-matrix suite is unchanged and still passes — the
    fixture sets visibility explicitly on every row, so it must not move.
  * HideExistence is reviewed in the same diff: it currently returns false for
    an unknown visibility, so a denial on an unknown state would render 403 and
    confirm the row. It should hide existence for anything that is not
    public/unlisted.

Tests:
  internal/authz/authz_test.go, new TestUnknownVisibilityDenies and
  TestUnknownAlbumPrivacyDenies, table-driven over authz.Actions. The harness
  exists; this is additive. Demonstrate the mutation: with the two `if v == ""`
  normalisations restored, the new tests must fail.

Cross-repo implications:
  core: the fix. user: none. search: none — vizra-search must never make its
  own visibility decision, and this reinforces why. meta: none.

Challenge:
  "A Resource with no visibility is a caller bug; the evaluator should not
  paper over caller bugs." That is the argument FOR denying, not against it —
  a caller bug that denies is a visible 404 in staging, and a caller bug that
  allows is a private photo on the fediverse. The weaker counterargument is
  that the ADR's precedence list starts at 'asset visibility' and does not
  enumerate an 'unset' state, so the evaluator is arguably outside the frozen
  matrix here; I hold that ruling 5 ("DENY is the answer for any surface not in
  the table") generalises to any INPUT not in the table.
```

```
FINDING 2: config — the HMAC key published in this repository is accepted as a production secret; the dev-secret filter cannot see it
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/config/config.go:124-140 (knownDevSecrets, looksLikeDevSecret),
             :247-251 (the SEARCH_HMAC_KEY branch)
             api/search-hmac-testvectors.json:21 ("key_utf8")
             internal/search/search_test.go:25 (testKey)
  requirements: VZ-FOUND-006; ADR-002 § Configuration ownership

Observed:
  looksLikeDevSecret is a lowercase substring denylist of 19 English words.
  I evaluated the repository's own published 32-byte keys against it:

      api/search-hmac-testvectors.json "key_utf8"   -> NOT refused (no substring matches)
      internal/search/search_test.go   testKey      -> NOT refused
      .env.example placeholders                     -> refused (contains "change")

  So `VIZRA_SEARCH_HMAC_KEY=<the key_utf8 value from api/search-hmac-testvectors.json>`
  passes LoadFrom in production: it is exactly 32 bytes, it is not empty, and it
  matches no denylist word. The same is true of the in-repo test key.

  This is the one secret in Vizra whose canonical documentation is a committed
  JSON file that says "vizra-search vendors a byte-identical copy". That file is
  where an operator wiring up search WILL look, and the field is literally named
  `key_utf8` next to a working example. The repository may be public.

  AGENTS.md states the contract as "Production refuses dev secrets, short
  secrets, wildcard CORS, plain-http origins and every named escape hatch",
  enforced by internal/config. For the published key, it does not.

Failure:
  An operator who copies the key out of the vectors file gets a working
  core<->search channel signed with a key anyone can read from GitHub. Since
  there is no nonce store, the window is the only replay bound, and the search
  contract carries viewer identity and an events-publish endpoint, a
  known key is a full compromise of that boundary — an attacker who can reach
  the search port can forge queries and publish index events.

Perspective:
  operator, instance-admin

Recommendation:
  Refuse by exact value, not by heuristic. Add a small set of
  knownPublishedSecrets containing the vectors' key_utf8 and the test key, and
  refuse any exact match in production regardless of length — the check is a
  constant-time-irrelevant string compare against ~3 entries. Keep the
  substring heuristic as well; it catches a different class.

  Second, smaller change: rename the field in the vectors file to
  `key_utf8_TEST_VECTOR_ONLY_NOT_A_CONFIG_VALUE` or add a sibling
  `"_warning"` string, and say in api/README.md that this value must never be
  used as VIZRA_SEARCH_HMAC_KEY. Documentation is not the control; the refusal
  is. But the label costs nothing.

  Consider also raising minSecretBytes reasoning: `len()` counts bytes of the
  string, so 32 hex characters is 16 bytes of entropy. Not blocking — note it
  for the M1 secret-generation slice so `vizra setup` generates base64 of 32
  RANDOM bytes.

Acceptance criteria:
  * Production boot with VIZRA_SEARCH_HMAC_KEY set to the vectors' key_utf8 is
    refused, with a problem naming the key and NOT echoing the value.
  * Production boot with VIZRA_SESSION_SECRET or VIZRA_MFA_KEY_KEK set to any
    published value is likewise refused.
  * Development boot with the same value still succeeds (the vectors must stay
    usable in tests).
  * The refusal message contains no part of the secret.

Tests:
  internal/config/config_test.go, new TestProductionRefusesPublishedTestKeys.
  It must read the value from api/search-hmac-testvectors.json at test time
  rather than duplicating the literal, so a future edit of the vectors file
  cannot silently un-cover it. Harness exists.

Cross-repo implications:
  core: the refusal. search: vizra-search vendors the same vectors file and
  must add the identical refusal to its own loader, or the weak half of the
  pair is the one an operator configures. meta: add a line to the installer
  hand-off that the search key is generated, never copied.

Challenge:
  "An operator who pastes a key out of a test-vector file will paste a key out
  of anywhere; you cannot denylist the internet." True, and a general entropy
  or provenance check is not worth building. But THIS value is one we published
  ourselves, in the file that documents the very key it is for, and refusing
  three exact strings costs four lines. The generic problem is unsolvable; this
  specific one is nearly free.
```

```
FINDING 3: config — the escape-hatch refusal tests truthiness, so the one hatch that carries a value is not refused in production
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/config/config.go:284-289
             internal/config/keys.go:28 (VIZRA_DEV_AUTOLOGIN_USER)
             internal/config/config_test.go:155-171 (TestEveryEscapeHatchIsRefusedInProduction)
  requirements: VZ-FOUND-006; ADR-002 § Configuration ownership

Observed:
  The production block refuses a hatch only when its value is truthy:

      for _, h := range EscapeHatches {
          if v, ok := lookup(h.Name); ok && truthy(strings.TrimSpace(v)) {
              bad(h.Name, "is a development-only escape hatch and must not be set in production")
          }
      }

  truthy accepts only 1/t/true/y/yes/on. But one registered hatch is not a
  boolean at all:

      {Name: "VIZRA_DEV_AUTOLOGIN_USER", Doc: "Signs every request in as this user. Development only."}

  A hatch whose documented value is a USERNAME is therefore never refused: any
  realistic setting of it is non-truthy, so production boots with it set.

  The test does not catch this because it only ever sets "true" and "false":

      requireProblem(t, h.Name, "true", h.Name)
      ...
      env[h.Name] = "false"
      if _, err := LoadFrom(lookupOf(env)); err != nil { t.Fatalf(...) }

  The second half actively cements the hole — it asserts that a non-truthy
  value MUST boot.

  keys.go:19-23 claims the enumeration is what makes this safe: "a hatch that is
  not refused cannot be added without turning the suite red." The enumeration is
  there; the assertion underneath it is the wrong one.

Failure:
  The named consumer of this hatch arrives in M1 with sessions. When it does,
  VIZRA_DEV_AUTOLOGIN_USER=owner in a production env file signs every request
  in as the site owner, and the fail-secure loader — the component whose entire
  job is to refuse exactly this — returns a valid *Config. Every read surface
  is then authenticated as the owner, and authz correctly allows everything.

  Today the hatch is consumed by nothing, so this is unreachable. It becomes
  reachable the moment M1 wires it, and the loader is being frozen now.

Perspective:
  operator, instance-admin, photographer (their private library is what leaks)

Recommendation:
  Refuse PRESENCE, not truthiness, for hatches that carry a value. Smallest
  coherent change: add a `ValueBearing bool` (or `RefuseIfPresent bool`) to
  config.Key, set it on VIZRA_DEV_AUTOLOGIN_USER, and in the loop refuse when
  the key is present with any non-empty value for those, keeping the truthy
  test for the boolean hatches.

  The simpler alternative — refuse presence for ALL hatches — is cleaner but
  breaks the deliberate affordance the test documents (a shared template that
  lists the hatches set to 0). Either is acceptable; pick one and say why in a
  comment.

Acceptance criteria:
  * Production boot is refused for VIZRA_DEV_AUTOLOGIN_USER set to any
    non-empty value, including "alice", "0", "off" and "false".
  * Boolean hatches keep their current behaviour: "true" refused, "false"
    tolerated.
  * The refusal names the key and does not echo the value.
  * Development boot with the hatch set still succeeds.

Tests:
  internal/config/config_test.go: extend TestEveryEscapeHatchIsRefusedInProduction
  to drive each hatch with a value from a per-hatch table rather than the
  literal "true", and add the explicit case
  VIZRA_DEV_AUTOLOGIN_USER="alice" -> refused. Demonstrate the mutation: the
  new case must fail against the current loader.

Cross-repo implications:
  core: the fix. user: vizra-user has its own dev switches — the reviewer of
  that repo should check whether the same truthiness assumption exists there.
  search: same question for VIZRA_DEV_TRUST_ANY_HMAC's counterpart, which IS
  boolean and is fine here but is implemented separately in vizra-search.
  meta: none.

Challenge:
  "The hatch is consumed by nothing in M0, so this is a hypothetical about code
  that does not exist." Correct, and it is why I did not rate it BLOCKER. But
  the loader is the frozen fail-secure gate, the hatch is already registered
  and already in .env.example where an operator can see it, and the test as
  written will go on asserting the hole is correct. Fixing it after M1 wires
  autologin means fixing it after the window in which it matters has opened.
```

---

# FOLLOW-UPS

```
FINDING 4: GITGUARDIAN TRIAGE — seven hits accounted for; nothing real, nothing to rotate, but "all historical, fixed at head" is not accurate
Severity:    SHOULD
Confidence:  medium

Affected:
  repo:      vizra-core
  files:     .github/workflows/build-test.yml (as of fe6101f), README.md:46,52,
             api/search-hmac-testvectors.json:21, internal/config/config_test.go
             (as of fe6101f), internal/site/site_test.go:19,116,
             internal/obs/log_test.go:31,36,108, internal/search/search_test.go:400
  requirements: none yet — propose VZ-CI-00x "secret-scanning triage is recorded, not waved through"

Observed:
  I enumerated every credential-shaped literal added on this branch
  (33e1669..HEAD) and every one present at HEAD. I ran a targeted scan for real
  credential formats — AKIA*, ghp_/gho_/ghu_/ghs_/ghr_, glpat-, sk-, xox*-,
  PEM private-key headers, JWTs — across all five branch commits. Zero matches.
  /bin/ and .env are gitignored and no binary or env file is tracked.

  Ruling per hit:

  HISTORICAL ONLY (in fe6101f, removed by 2b9c540 / e45e784; squash-merge means
  they never reach main):
   1. build-test.yml  POSTGRES_PASSWORD: vizra          SYNTHETIC. Ephemeral CI
      (x2, both jobs)                                   container, runner
                                                        loopback, empty schema.
   2. build-test.yml  postgres://vizra:vizra@127.0.0.1  SYNTHETIC. Same value.
      (x2)
   3. config_test.go  "Kv8Qn2Rt6Wp1Zx5Ym9Bc3Fd7Gh0Jl4Nq" SYNTHETIC. Hand-built
      config_test.go  "Pz3Xw7Ru1Ty5Vb9Nm2Ck6Hj0Ls4Df8Ga" consonant-digit pattern,
                                                        used only as loader
                                                        input. Replaced at head
                                                        by placeholderSecret(32),
                                                        built at runtime — the
                                                        right fix.
   4. config_test.go  "postgres://vizra:pw@db:5432/..."  SYNTHETIC.

  STILL PRESENT AT HEAD (the part the builder's summary omits):
   5. README.md:46,52        POSTGRES_PASSWORD=vizra,
                             postgres://vizra:vizra@127.0.0.1:55432/...
                             SYNTHETIC — local-dev docs, same throwaway value.
   6. api/search-hmac-testvectors.json:21  "key_utf8"
                             SYNTHETIC as a credential — but see FINDING 2: it
                             is a *usable* production key, which is a design
                             problem rather than a leak.
   7. internal/site/site_test.go:19,116     postgres://vizra:pw@db:5432/vizra
      internal/obs/log_test.go:31,36,108    postgres://vizra:hunter2@...,
                                            rediss://default:s3cr3tpw@...
      internal/search/search_test.go:400    http://user:sup3rsecret@127.0.0.1:1/
                             SYNTHETIC, and load-bearing: these are the INPUTS
                             to the redaction tests. Removing them would delete
                             the coverage. "hunter2" and "sup3rsecret" are
                             self-evidently fake.

  CANNOT DETERMINE: none. Every hit I can identify resolves.

Failure:
  Nothing needs rotating, and no real credential ever entered git. The process
  failure is that the PR narrative says the findings are historical and fixed at
  head, when at least three of the seven are at HEAD by design and will keep the
  check red on every future PR that touches those files. An alert that is always
  red is an alert nobody reads.

Perspective:
  developer, operator

Recommendation:
  Commit a .gitguardian.yaml (or the equivalent ignore manifest) that excludes,
  by path and matched-secret hash and WITH A REASON STRING each:
  README.md local-dev block, internal/obs/log_test.go, internal/site/site_test.go,
  internal/search/search_test.go, and api/search-hmac-testvectors.json. Do not
  add a blanket *_test.go exclusion — a real secret in a test file is still a
  real secret. Put the file under CODEOWNERS with /scripts/ so widening it needs
  owner review.

  Separately: .gitignore has `.env` but not `env/*.env` or `*.env`. Add both
  before the deployment tree lands.

Acceptance criteria:
  * The GitGuardian check is green at HEAD with every exclusion carrying a
    written reason.
  * Adding a new credential-shaped literal outside the excluded paths turns it
    red.
  * The PR description records the triage verdict per hit and states that no
    rotation is required.
  * .gitignore covers env/*.env.

Tests:
  Not a Go test. The evidence is the green check plus the triage table, filed
  under docs/evidence/warroom/.

Cross-repo implications:
  core: the ignore manifest. user/search: the same triage is owed on their PR1s
  if their scanners are red. meta: record the "no rotation required" verdict so
  a later auditor does not re-litigate it.

Challenge:
  "Excluding paths from a secret scanner is how real secrets get missed." Right,
  which is why I am asking for per-path, per-reason exclusions rather than a
  glob, and why I checked the actual formats rather than trusting the builder's
  assurance. The alternative — leaving the check permanently red — guarantees
  the next real hit is ignored.
```

```
FINDING 5: jobs — last_error is written to a queryable table and rendered in /admin/jobs without passing through obs.Redact
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/jobs/worker.go:259, :262, :272, :283, :392-401 (truncate)
             migrations/0002_jobs.up.sql:27 (last_error text NULL)
  requirements: VZ-OPS-005; ADR-002 § Logging and redaction

Observed:
  The failure paths store the handler's raw error text:

      w.finishFailed(ctx, q, j, err.Error(), log)
      ... LastError: strPtr(truncate(err.Error())),

  truncate bounds length only (2000 bytes) and its own comment states the
  destination: "last_error is shown in /admin/jobs". internal/obs.Redact exists,
  is exported precisely so "every subprocess stderr capture must pass through it
  too" (obs/log.go:40-42), and is NOT called here. The log lines beside these
  calls ARE safe, because they go through the redacting slog handler; the
  database write bypasses it.

  0003_audit_events.up.sql documents the rule the jobs table does not follow:
  "before/after are jsonb and must never carry a credential, a signed URL or a
  session id ... The redaction layer runs before a row is written."

Failure:
  ADR-002 says secrets do not enter a queryable table. A Go HTTP error is a
  *url.Error that formats as `Post "https://user:pw@host/path": ...` — which is
  exactly why search/remote.go:163 has redactedTransportError. When M1 job
  handlers start doing S3 puts, federation deliveries and webhook calls, a
  presigned URL or a DSN lands in jobs.last_error, survives in the database,
  and is rendered to every admin — and into any pg_dump an operator shares.

  Not reachable today: the only handler is internal/jobs/convert.go. The
  primitive is being frozen now and every future handler inherits it.

Perspective:
  operator, instance-admin

Recommendation:
  One line: truncate(obs.Redact(err.Error())) at each of the three call sites,
  or redact inside truncate and rename it. Redact before truncating, so a
  secret straddling the 2000-byte cut is still caught.

  Do NOT add a CHECK constraint or trigger for this — it is not expressible in
  SQL, and the migration is append-only. The control belongs in Go.

Acceptance criteria:
  * A handler returning an error containing a URL with userinfo, a presigned
    S3 query string, a Bearer token or a vzk_ API key stores "[redacted]" in
    jobs.last_error.
  * The truncation boundary is tested: a secret spanning byte 1995-2010 is
    redacted, not half-stored.
  * The existing log-redaction tests are unchanged.

Tests:
  internal/jobs/jobs_test.go, new TestLastErrorIsRedactedBeforeItIsStored,
  driven through the fake queue the existing tests use, with the value classes
  from internal/obs/log_test.go's table so the two stay in step. Harness exists.

Cross-repo implications:
  core: the fix. user: whoever builds /admin/jobs must not assume the column is
  clean. search: vizra-search has its own job/error surface — same question.
  meta: none.

Challenge:
  "Redaction at the write is the wrong layer; handlers should not produce
  secret-bearing errors in the first place." Agreed as the primary control, and
  M1 handlers should wrap their errors. But that is a convention across dozens
  of future call sites, and this is one line at three call sites that holds when
  the convention slips. The repo already made exactly this argument for the
  logger.
```

```
FINDING 6: search — the internal HTTP client has no redirect policy, so a compromised search host can steer core's fetch and receive a valid signature header
Severity:    SHOULD
Confidence:  medium

Affected:
  repo:      vizra-core
  files:     internal/search/remote.go:36-42 (NewRemote), :124-161 (call), :97-117 (ping)
  requirements: VZ-SEARCH-00x (M3) — propose adding the negative case to the existing entry

Observed:
  The client is built with only a timeout:

      http: &http.Client{Timeout: timeout}

  There is no CheckRedirect, so Go follows up to 10 redirects. Go's stdlib
  strips Authorization, WWW-Authenticate and Cookie on a cross-host redirect —
  it does not know about X-Vizra-Signature, X-Vizra-Timestamp or X-Vizra-Nonce,
  which are therefore forwarded to whatever host the redirect names.

  Everything else about this client is bounded and careful: maxResponseBytes is
  8 MiB, the body is read through io.LimitReader, ContentLength is set,
  context deadlines propagate, and redactedTransportError keeps a userinfo-
  bearing URL out of the error string. The redirect policy is the one gap.

Failure:
  Two consequences, both requiring the search service to be compromised or
  VIZRA_SEARCH_URL to be wrong:
   (a) a valid signature over POST /internal/v1/search leaks to a third party.
       It is path- and body-bound, so it is replayable only against that same
       path within the 300 s window — bounded, but it is a credential leaving
       the trust boundary;
   (b) core follows the redirect to an arbitrary host and port, including
       loopback and link-local. The response must parse as the expected JSON to
       be useful, so this is a weak SSRF primitive, not a strong one — but it is
       a server-side fetch whose destination an attacker controls, and the
       instructions name that boundary explicitly.

  Threat model: single-operator instance where search runs in the same compose
  project. The realistic trigger is a compromised search container or a
  typo'd/hijacked VIZRA_SEARCH_URL, not an internet stranger.

Recommendation:
  CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }.
  The internal contract is a fixed set of POST endpoints on a configured base
  URL; a redirect is never a legitimate answer, so refusing to follow it is
  both the secure and the correct behaviour. Apply it to ping() too.

Acceptance criteria:
  * A search stub answering 302 to any location causes the call to fail with the
    Service reporting health degraded, and core makes no second request.
  * No X-Vizra-* header is sent to any host other than the configured base URL
    host.
  * The SQL fallback still engages, so a redirecting search service degrades
    rather than breaking search.

Tests:
  internal/search/search_test.go: a httptest.Server that 302s to a second
  httptest.Server which records whether it received X-Vizra-Signature. Assert
  the second server saw no request. The harness (httptest stubs) already exists
  in this file.

Cross-repo implications:
  core: the fix. search: vizra-search should never emit a 3xx on
  /internal/v1/*; worth stating in api/search-internal.openapi.yaml so both
  sides agree. user: none. meta: none.

Challenge:
  "VIZRA_SEARCH_URL is operator-configured and validated, and the search
  service is inside the trust boundary — this is defending against a machine we
  already trust." Fair, and it is why I rated it SHOULD rather than REQUIRED.
  The counter is that the entire point of HMAC-signing this hop is that the
  search service is a SEPARATE trust domain; if it were fully trusted the
  signature would be pointless.
```

```
FINDING 7: search — the 300 s clock window is the only replay bound, and no nonce store exists on either side
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/search/hmac.go:31-32 (MaxClockSkew), :199-206 (NewNonce),
             :227-280 (Verify — the nonce is validated for SHAPE only)
             api/search-hmac-testvectors.json (window._comment says so explicitly)
  requirements: VZ-SEARCH-00x (M3)

Observed:
  Verify checks that the nonce is 16-64 bytes of lowercase hex and then never
  looks at it again. There is no store, so a captured request is replayable for
  up to 300 seconds. The code says so honestly rather than hiding it:

      // Until vizra-search owns a nonce store the window is the ONLY replay
      // bound, so it has to actually close.

  This is correctly scoped — vizra-search owns the store, and core is the
  client here — so I am filing it as a named follow-up rather than a gap.

Failure:
  Within a 300 s window an attacker who can observe the core<->search hop can
  replay any request, including POST /internal/v1/events, which mutates the
  index. On a single-host compose deployment the hop is loopback and the
  exposure is small; with search-mode external over a network it is real.

  300 s is also wide for two processes that are, by design, either on the same
  host or one hop apart. It was presumably chosen for clock tolerance on the
  federation-style assumption; NTP-synced containers need far less.

Perspective:
  operator, instance-admin

Recommendation:
  Two independent, cheap steps, both deferrable to M3:
   1. Narrow MaxClockSkew to 60 s and regenerate the boundary negative vectors.
      A 60 s window is still generous for NTP-synced containers and cuts the
      replay surface fivefold. This is a contract change, so it must land in
      api/search-internal.openapi.yaml and the vectors in the same diff, and
      vizra-search must adopt it in lockstep or every call 401s.
   2. vizra-search adds a nonce store: SETNX in the cache, keyed on the nonce,
      TTL = window + slack, reject on collision. Fail closed if the cache is
      down, or say explicitly in the ADR that it degrades to window-only.

  Do NOT do this in this PR. Step 1 needs the sibling repo to move at the same
  time, and this PR should not change the wire contract again.

Acceptance criteria:
  * MaxClockSkew, the OpenAPI securityScheme description and the vectors file
    all state the same window, checked by the existing drift test.
  * Replaying a captured request a second time inside the window is rejected by
    vizra-search.
  * A cache outage causes signature verification to fail closed, or the
    degradation is written down as a decision.

Tests:
  vizra-search's suite owns the replay test. In core, the boundary vectors
  (timestamp-stale-past-window / timestamp-future-past-window) are regenerated
  at the new window and TestHMACNegativeTestVectors continues to enforce them.

Cross-repo implications:
  core: the constant and the vectors. search: the nonce store and the matching
  constant — these must ship together or the boundary breaks.
  meta: record the window as a cross-repo pinned constant so it cannot drift.

Challenge:
  "The window is documented, deliberate and correctly implemented; filing it is
  noise." It would be, except the instructions name the core<->search boundary
  as a specific beat and the replay bound is the part of it that is currently
  unowned by any ledger entry. A known gap with no ID is a gap that ships.
```

```
FINDING 8: CI — the gate guard's continue-on-error check is a literal-string grep that an expression or quoted form evades
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     scripts/ci-required-guard.sh:115-124
  requirements: VZ-CI-001 (negative case 1)

Observed:
  Check 3 is:

      if grep -rnE '^\s*continue-on-error:\s*true' "$WORKFLOWS"/*.yml

  It matches only the bare lowercase literal. GitHub Actions accepts several
  other spellings of the same thing, none of which this regex sees — an
  expression form, a quoted form, and a capitalised YAML boolean among them.
  At job level, any of these turns a failing job's check-run conclusion into
  success, so the fan-in in ci-required.yml:71-79 would record SUCCESS for a
  lane that failed.

  I am not writing the exact strings out; the evasion is a one-line edit and
  the repository may be public. The maintainer can reproduce it in a scratch
  branch in under a minute.

  The other four checks are sound. I tried to defeat them and could not:
  deleting a manifest line trips the FLOOR check (string equality, so a regex
  metacharacter in a manifest line cannot widen it); pointing a floor job's
  `on:` away from pull_request leaves the fan-in PENDING until it times out —
  fails closed; `if: false` on a floor job yields conclusion "skipped", which
  the fan-in treats as failure. Those all behave as advertised.

Failure:
  A PR can neutralise a floor lane while ci-required-guard prints "ok
  no continue-on-error on any lane". CODEOWNERS on /.github/workflows/ is the
  backstop — and it is a real one — but the guard exists precisely because
  "CODEOWNERS will catch it" is the assumption that FINDING 2 of the vizra-user
  review already disproved once. A guard that reports ok for something it
  cannot see is the false-positive-CI failure mode AGENTS.md names.

Perspective:
  developer, operator

Recommendation:
  Stop grepping YAML with a regex; parse it. The build-test lane already
  installs Python 3 (docker-build.yml uses it inline), so: load each workflow
  with a YAML parser, walk jobs and steps, and fail if `continue-on-error` is
  present at all on any job or step belonging to a FLOOR_LANE — whatever its
  value or spelling. Present-at-all is the right rule: a required lane has no
  legitimate use for it.

  While parsing, add the check the guard's own header claims but does not make:
  that each floor lane's job is actually triggered `on: pull_request`.

Acceptance criteria:
  * The guard fails on every spelling of continue-on-error — bare, quoted,
    capitalised and expression — on a floor lane's job or any of its steps.
  * The guard fails if a floor lane's workflow is not triggered on
    pull_request.
  * The guard still passes on the current tree unchanged.
  * A fixture workflow demonstrating each evasion is committed under
    scripts/testdata/ and asserted against, so the check has negative cases of
    its own.

Tests:
  A shell or Go test that runs ci-required-guard.sh against a testdata
  directory of crafted workflows and asserts a non-zero exit for each. This
  harness does not exist yet; the smallest version is a
  scripts/testdata/bad-workflows/ tree plus four lines in the Makefile's
  ci-guard target.

Cross-repo implications:
  core: the guard. user and search: both carry a copy of this guard pattern —
  the same weakness is almost certainly in both, and the fix should be applied
  to all three in one pass. meta: the CI fan-in contract in ADR-002 should say
  "present at all", not "set to true".

Challenge:
  "CODEOWNERS already requires owner review for /.github/ and /scripts/, so
  every evasion is visible in review anyway." That is the residual the PR
  already documents and accepts. But the ruleset that makes CODEOWNERS
  mandatory is explicitly NOT YET APPLIED (CODEOWNERS:8-12), so right now the
  guard is the only mechanical control, and it has a hole. Once the ruleset
  lands this drops to genuinely defence-in-depth.
```

```
FINDING 9: httpapi — no response-hardening middleware and no request body limit on the public server
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/server.go:104-121 (the middleware chain and the
             four routes), cmd/api/main.go:113-118 (the http.Server)
  requirements: none yet — propose VZ-SEC-00x "API responses carry hardening
             headers and a body limit", M1

Observed:
  The chain is requestID -> site -> routeAttribute. There is no middleware
  setting X-Content-Type-Options, Referrer-Policy, Cross-Origin-Resource-Policy
  or a default Cache-Control, and no echo BodyLimit. The http.Server sets
  ReadHeaderTimeout 10 s and IdleTimeout 120 s but no ReadTimeout or
  WriteTimeout, so a slow-body or slow-read client holds a connection
  indefinitely once headers are in.

  VIZRA_MAX_INTERNAL_BODY_BYTES is defined in config (keys.go:54, "enforced
  before the body is read") and is currently read by nothing — the internal
  endpoints it describes are in vizra-search, not here. That is consistent,
  but it means the public server has no limit of any kind.

  Deps.Limiter is constructed in main.go:69 and plumbed into the server, but no
  route uses it. Correct for M0 — there is nothing to rate-limit — and worth
  naming so it is not mistaken for coverage.

  The metrics listener correctly binds 127.0.0.1:9090 by default and is a
  separate http.Server; /metrics is not on the public mux. That is right.

Failure:
  Today the blast radius is four JSON probe endpoints, so the practical impact
  is near zero — this is a missing-hardening finding, not a vulnerability. The
  cost is that the chain is being frozen: M1 adds cookie-authenticated routes,
  uploads and media serving to a server with no body limit, no write timeout
  and no header defaults, and each of those then needs its own retrofit.

Perspective:
  operator, developer

Recommendation:
  Add one securityHeadersMiddleware to the chain now, while it is four routes
  and the diff is reviewable: X-Content-Type-Options: nosniff,
  Referrer-Policy: no-referrer, Cross-Origin-Resource-Policy: same-origin, and
  Cache-Control: no-store on every API response by default — the last is the
  one that matters most for a photo host, because the default must be
  no-store and the public-derivative path must opt IN to caching, never the
  reverse.

  Add ReadTimeout and WriteTimeout to the api http.Server. Leave the body limit
  and rate limiting to M1, where there is a body and a login to limit; do not
  invent a number now.

  CSP belongs to vizra-user, not here — this server returns JSON. Do not add
  one; it would be cargo cult.

Acceptance criteria:
  * Every response from every registered route carries the four headers,
    asserted by iterating Routes() rather than by listing paths, so a route
    added later cannot miss them.
  * An error response (404, 500) carries them too — the error handler path is
    the one that usually misses.
  * The api http.Server has a non-zero ReadTimeout and WriteTimeout.
  * /metrics is still not reachable on the public listener.

Tests:
  internal/httpapi/probes_test.go, new TestEveryRouteCarriesHardeningHeaders
  driven off s.Routes(), plus a case through the unknown-route 404 path. The
  harness exists — probes_test.go already drives the server through httptest.

Cross-repo implications:
  core: the middleware. user: vizra-user owns CSP and frame-ancestors for the
  HTML origin; the two must not both try to set them. search: internal only,
  not applicable. meta: none.

Challenge:
  "Four JSON probe endpoints do not need security headers; this is checklist
  security with no threat behind it." Largely true today, and I nearly filed it
  as a NIT. What moves it to SHOULD is the Cache-Control default specifically:
  on a private-photo host, a response-caching default of no-store is a
  visibility control, not a header checklist item, and retrofitting it after
  media routes exist means auditing every route instead of setting one default.
```

```
FINDING 10: migrations — audit_events is an append-only record with nothing preventing UPDATE or DELETE
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0003_audit_events.up.sql:16-39
  requirements: ADR-007 § audit_events; propose VZ-AUDIT-00x, M1

Observed:
  The table is well shaped for privacy — no raw IP column (ip_prefix only), a
  CHECK binding actor_kind to actor_user_id, and a documented rule that
  before/after must be redacted before write. What it has no defence for is
  mutation: the application role can UPDATE any row's `before`/`after`/`action`
  or DELETE the row outright. There is no trigger, no rule, no REVOKE, and no
  separate writer role.

  The migration correctly anticipates additive change elsewhere — "actor_user_id
  has no foreign key yet because `users` arrives in M1 ... adding a constraint
  is an additive migration" — so the same reasoning applies here and this is
  NOT frozen by merging. That is why it is a follow-up and not a blocker.

  I checked the other three migrations for anything that IS irreversible and
  found nothing I would hold the PR for. Constraints are unusually thorough:
  jobs_lease_complete, jobs_terminal_finished, the partial unique index on live
  idempotency keys only, storage_locations_default_writable, and the
  one-default partial unique index are all correct and all enforce at the
  database rather than in application discipline. sites.privacy_mode defaults
  to 'public', which is a default that opens access, but it is the charter's
  product default for a photo community and precedence step 1 reads it
  explicitly — I am not objecting to it, only noting I considered it.

Failure:
  An attacker or a careless operator who reaches the application's database
  role can erase the evidence of what they did. The migration's own header
  states the threat — "an audit trail added after the fact has a hole exactly
  where the interesting period was" — and the same is true of one that can be
  edited after the fact.

Perspective:
  operator, instance-admin, business (a self-hosted instance with a moderation
  obligation needs the trail to be defensible)

Recommendation:
  In the M1 migration that adds the users FK, add in the same diff a BEFORE
  UPDATE OR DELETE trigger on audit_events that raises an exception, plus a
  documented, audited maintenance path for retention pruning (a SECURITY
  DEFINER function, or a distinct role the application does not hold).

  Do not attempt this in PR1. It needs the role model from M1 to be meaningful,
  and adding a trigger the retention job then has to fight is worse than
  waiting one slice.

Acceptance criteria:
  * UPDATE on any audit_events row raises an exception from the application
    role.
  * DELETE on any audit_events row raises an exception from the application
    role.
  * The documented retention path still prunes rows older than the retention
    window, and doing so is itself audited.
  * The migration is additive; 0003's bytes are unchanged and the append-only
    manifest still verifies.

Tests:
  internal/integration (tags=integration), new TestAuditEventsAreImmutable:
  insert a row, attempt UPDATE and DELETE as the application role, assert both
  error. The integration harness and real PostgreSQL already exist in
  build-test.yml, so this is additive.

Cross-repo implications:
  core: the migration and the retention path. user: an admin audit view must
  not offer an edit or delete control. search: audit rows are never indexed.
  meta: the backup/restore runbook must state that restoring audit_events is
  privileged.

Challenge:
  "A trigger is theatre: anyone with the database role can DROP the trigger
  too." Correct, and it is why the real control is role separation — the
  application role should lack UPDATE/DELETE on this table entirely. The
  trigger is the cheap 80% that works against SQL injection and against an
  application bug, which are the likelier failures than a full role compromise.
  I would accept either; I would not accept neither.
```

```
FINDING 11: supply chain — the release image is built and asserted but never scanned, and there is no osv/dependency lane beyond govulncheck
Severity:    SHOULD
Confidence:  high

Affected:
  repo:      vizra-core
  files:     .github/workflows/docker-build.yml (whole file),
             .github/workflows/govulncheck.yml,
             Dockerfile:109-116 (the runtime stage)
  requirements: none yet — propose VZ-SUPPLY-00x, VZ-UPGRADE-001 (publish slice)

Observed:
  govulncheck covers the Go module graph and is a floor lane, correctly, with a
  weekly cron so a post-merge disclosure is still found. That is the half most
  projects skip, and it is here.

  What is not covered is everything the image contains that is not Go. The
  runtime stage derives FROM the vips builder stage and installs ca-certificates
  and tini, then purges the toolchain with `|| true` — so a failed purge is
  silent, and the explicitly-installed -dev packages (libjpeg62-turbo-dev,
  libpng-dev, libwebp-dev, libtiff-dev, libexif-dev, liblcms2-dev, libspng-dev,
  libdav1d-dev, libaom-dev) are not auto-removable and remain. Those are the
  image's real decoder attack surface and nothing enumerates their CVEs.

  apt-versions.txt is captured from the vips stage, which is good provenance,
  but it is recorded, not checked against anything.

  Also: the runtime stage runs apt-get update, so the Debian package set floats
  between rebuilds of the same commit — which sits awkwardly beside the
  Dockerfile's own stated goal that "two builds of one commit must resolve
  identical library versions".

Failure:
  A known-vulnerable libwebp or libtiff — historically the exact CVEs that
  matter for an image host — ships in a tagged release and nothing in CI says
  so. The loader-list assertion catches a codec that appears; it says nothing
  about a codec that is present and vulnerable.

Perspective:
  operator, instance-admin

Recommendation:
  Three separate, independently justified changes — do not bundle them:
   1. Add an image scan (trivy or grype) to docker-build, initially
      non-blocking on severity but FAILING on scanner error, so the lane cannot
      pass by not running. Promote to blocking on HIGH/CRITICAL at the publish
      slice, once the baseline noise is known.
   2. Drop the `|| true` on the purge, or assert afterwards that no compiler is
      present in the runtime image — the existing "assert not root" step is the
      right shape to copy.
   3. Build the runtime stage from a clean digest-pinned debian:13-slim and
      COPY the libvips artefacts into it, rather than deriving from the builder.
      This removes the -dev headers and the toolchain by construction instead of
      by purge, and makes the floating apt-get update question much smaller.

  Item 3 is the one with real value and real cost; it is a Dockerfile
  restructure and belongs in its own PR with its own layer-cache evidence.

Acceptance criteria:
  * docker-build produces a scan report artefact on every run, and the lane
    fails if the scanner did not run.
  * The runtime image contains no compiler and no -dev package, asserted in CI.
  * The layer-order assertion (a Go change does not rebuild libvips) still
    passes after any restructure — that test already exists and is good.

Tests:
  CI lane, not a Go test. Evidence is the scan artefact plus the new assertion
  step output, filed under docs/evidence/.

Cross-repo implications:
  core: this image. user: vizra-user needs the npm/osv equivalent — that is a
  separate finding on that repo, not this one. search: same image question.
  meta: the release record should carry the scan verdict alongside the digest.

Challenge:
  "Scanners on a Debian base produce dozens of unfixable low-severity findings
  and the lane becomes noise everyone clicks through." Real risk, and it is why
  I am asking for non-blocking-on-severity but failing-on-error first: the
  value in M0 is the inventory and the trend, not the gate. If it is still
  noise after one milestone, kill it — but decide that with data.
```

```
FINDING 12: probes — /version and /schemaz give an anonymous caller an exact build and schema fingerprint
Severity:    NIT
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/probes.go:237-273, internal/httpapi/modules.go:14-20
             api/openapi.yaml (both are in the public contract)
  requirements: ADR-002 § Probes

Observed:
  An unauthenticated GET /version returns release, commit SHA, build time, Go
  version, image digest, libvips version, the full libvips loader list, the
  embedded schema version and pinned versions of echo, pgx, go-redis,
  golang-migrate and otel. GET /schemaz always returns 200 with applied
  version, embedded version, dirty flag and state.

  This is a deliberate ADR-002 decision — "/version reports module versions,
  image digest, the libvips loader list and the schema ledger version" — and
  modules.go already reasons about it and reports five modules rather than the
  whole graph, "because /version is a public endpoint and a complete dependency
  inventory is a gift to anyone matching an instance against a CVE feed".
  The judgement has been made and made thoughtfully.

  /healthz and /readyz disclose nothing sensitive: component names and fixed
  strings, no DSN, no host. Correct.

Failure:
  An attacker scanning for Vizra instances can select an exploit by exact
  pinned version without touching anything else, and `dirty: true` on /schemaz
  advertises a half-migrated instance as a good moment to attack. Low impact
  on its own; it is a recon aid, not a vulnerability.

Perspective:
  operator, instance-admin

Recommendation:
  Do not change this in PR1 — it is an accepted ADR decision and the contract
  test pins it in both directions, so a unilateral change here would be a
  scope reduction by a reviewer. Instead raise it as an entry in
  docs/OPEN_QUESTIONS.md for the owner: should /version's detailed body require
  an operator credential (or move to the metrics listener) once M1 has one,
  leaving an unauthenticated /version that returns release only?

  My recommendation to the owner would be yes, at M1, with the detailed body
  behind the same credential as the admin console — but that is the owner's
  call, not mine.

Acceptance criteria:
  * An OPEN_QUESTIONS entry exists naming the two endpoints, what they
    disclose, and the proposed M1 split.
  * Whatever the owner decides is reflected in ADR-002 and in
    api/openapi.yaml in the same diff, so the contract test keeps it honest.

Tests:
  If the split is adopted: internal/httpapi/probes_test.go asserts the
  anonymous body contains release only and no commit, digest, module map or
  loader list. Not needed unless adopted.

Cross-repo implications:
  core: the endpoints. user: `vizra update` and the deploy scripts read
  /schemaz, so any credential requirement must reach them. search: reports no
  search_schema_version, per ADR-002 — consistent. meta: the installer reads
  these too.

Challenge:
  "Version disclosure is standard for self-hosted software and hiding it is
  security by obscurity; operators need /version to debug." Mostly right, and
  it is why this is a NIT and why I am routing it to the owner rather than
  filing it as a defect. The narrow counter is the loader list specifically:
  it tells an attacker exactly which decoders are linked, which is materially
  more useful against an image host than a version string.
```


---

# Closure check at 4f8d0fc207f94a2a516607d167fcf69abd7a2148 (after fix round 1)

Same reviewer, resumed by the chair 2026-09-20. Verbatim, extracted from its transcript by script. **Chair ruling:** Findings 1, 2 and 3 and the five ride-alongs are CLOSED on this SHA. **Finding 13 is accepted as BLOCKING** — the `ip_prefix` CHECK was added this round, freezes on merge, and contradicts the migration's own header; it goes into fix round 2 (the builder's last under the two-round cap), which the chair holds until the backend seat and the verifier have reported so that the round is final.

**HEAD confirmed `4f8d0fc…`, clean tree.** Delta reviewed: `git diff e45e784 4f8d0fc` (117 files).

## Finding 1 — CLOSED

| Criterion | Verdict | Proof |
|---|---|---|
| 21 Actions deny `""` and unrecognised labels, reason `visibility_unknown` | MET | `internal/authz/authz.go:288-291` — the `switch vis` returns `Deny, ReasonVisibilityUnknown` in `default`; `TestUnknownVisibilityDenies` drives `""`, `"PUBLIC"`, `"Public"`, `"scheduled"`, `"moderated"`, `"deleted"`, `" public"`, `"public\n"` × 21 Actions × 5 viewer classes, with the most permissive subject/resource otherwise |
| Album page denies `AlbumPrivacy ""` for A, M, G | MET | `authz.go:321-327`; `TestUnknownAlbumPrivacyDenies` covers all five classes, not just three |
| 315-case matrix unchanged | MET | `git diff --stat … -- internal/authz/testdata/adr007_matrix.tsv` is empty |
| `HideExistence` hides anything not public/unlisted | MET | `authz.go:235-244`, `default: return true`; `TestHideExistenceForAnythingNotPublicOrUnlisted` |
| DownloadSetting asymmetry commented as deliberate | MET | `authz.go:155-162` plus `TestDownloadSettingStillDefaultsToAll`, which pins it so nobody "fixes" it later |

Second sweep for other zero-value ALLOW paths: none found. `owner` still requires `resource.OwnerID != ""`, so empty-equals-empty cannot match. `roleRank[""]` is 0 and `staff` needs `Staff && AtLeast(RoleManager)`, so a zero Subject cannot escalate. An Action with no `kindOf` row denies. `sites.privacy_mode` is `NOT NULL DEFAULT 'public'` with a two-value CHECK — and the new `sites_singleton` unique index (`0001:42`) closes a precedence ambiguity I had *not* raised: without it a second row made "is this site private" depend on handle sort order. Good catch by the builder.

## Finding 2 — CLOSED

`knownPublishedSecrets` (`config.go:170-176`) refuses both published keys by exact match, checked *before* the length rule, for `VIZRA_SEARCH_HMAC_KEY`, `VIZRA_SESSION_SECRET` and `VIZRA_MFA_KEY_KEK`; `TestProductionRefusesPublishedTestKeys` asserts the refusal does not echo the value and reads `key_utf8` from the vectors file at test time. Development still accepts. `placeholderSecret` was moved off the now-denylisted `Aa1Bb2…` and `TestTheTestBaselineIsNotAPublishedSecret` stops the suite passing vacuously.

**Vectors semantics unchanged** — confirmed: the only `api/search-hmac-testvectors.json` change is one added `key_utf8_warning` line. `key_utf8`, all 5 accept vectors and all 24 negative vectors are byte-identical.

## Finding 3 — CLOSED

`RefuseIfPresent` (`keys.go:14-17`, `config.go:344-355`) refuses `VIZRA_DEV_AUTOLOGIN_USER` on any non-empty value; `TestValueBearingEscapeHatchIsRefusedWhenPresent` covers `alice`, `owner`, `0`, `false`, `off`, `no`, `1`, `true`, `" "`, `-`. Boolean hatches keep the `=false` affordance. `TestEveryEscapeHatchIsRefusedForItsRealisticValues` supplies the per-hatch value table. Whitespace is refused rather than trimmed — the fail-secure reading.

## Ride-alongs

All MET. **5**: `safeError() = truncate(obs.Redact(s))` at all four `LastError` writes (`worker.go:190`), plus `TestASecretStraddlingTheTruncationBoundaryIsRedacted`. **6**: `CheckRedirect → ErrUseLastResponse` on the shared client, so `ping` is covered too; two-server tests assert the attacker server saw no `X-Vizra-Signature`. **8**: guard is now a YAML parser; `continue-on-error` matched present-at-all after `lower()`+`_`→`-` normalisation, with bare/quoted/capitalised/expression/underscore/step fixtures; floor lanes must trigger on `pull_request`; missing PyYAML or python3 exits 2 ("BLOCKED, not passed"). **9**: `securityHeadersMiddleware` is registered *before* `siteMiddleware`, so the 404 path carries the headers; `TestEveryRouteCarriesHardeningHeaders` iterates `s.Routes()`; `ReadTimeout`/`WriteTimeout` 30 s. **4**: per-path exclusions each with a reason, no test glob, `.gitguardian.yaml` under CODEOWNERS; `.gitignore` covers `*.env` and `env/*.env` with `!.env.example` verified still tracked.

## New items

**`append-only` lane** — not bypassable beyond the known CODEOWNERS residual: it is in `FLOOR_LANES` (`ci-required-guard.py:79`), so deleting its manifest line turns the guard red. This PR passes it legitimately only because `main` carries no migrations — which is exactly what makes now the last editable moment.

**`internal/doctor`** — no leak. `CheckDatabase` returns a fixed string with the comment naming why; `db.Open`/`cache.Open` still suppress at source; the one `err.Error()` path carries an env-file *path*, not a value.

**Migrations** — `sites_singleton`, the `jobs` size bounds and the partial `jobs_claim` index are all correct and safe to freeze. One defect below.

---

```
FINDING 13: migrations — the audit_events ip_prefix CHECK accepts up to 112 bits of IPv6, not the /48 or /64 its own comment promises
Severity:    REQUIRED
Confidence:  high

Affected:
  repo:      vizra-core
  files:     migrations/0003_audit_events.up.sql:60-65 (audit_events_ip_prefix_shape)
             internal/integration/golden_test.go:1243-1285 (TestAuditEventsRefusesAFullIPAddress)
  requirements: ADR-007 § audit_events

Observed:
  The IPv6 branch is

      ip_prefix ~ '^[0-9a-f]{1,4}(:[0-9a-f]{1,4})*::(/(48|64))?$'

  The repetition is unbounded, so it accepts one to seven leading groups, and
  the /48|/64 suffix is optional. Evaluated against the address forms:

      2001:db8::                      ACCEPTED   (intended)
      2001:db8::/48, ::/64            ACCEPTED   (intended)
      2001:db8::1                     refused    (correct)
      2001:db8:0:0:0:0:0:dead         refused    (correct)
      ::ffff:192.0.2.128              refused    (correct — starts with ':')
      ::ffff:c000:280                 refused    (correct)
      2001:DB8::                      refused    (fail-closed; lowercase class)
      2001:db8:85a3:1::               ACCEPTED   <- 64 bits, fine
      2001:db8:85a3:1:2:3::           ACCEPTED   <- 96 bits, NOT a /48 or /64
      a:b:c:d:e:f:1::                 ACCEPTED   <- 112 bits, no suffix required
      2001:db8:85a3:8a2e:370:7334:1234::  ACCEPTED   <- 112 bits

  The migration's own header states the control it is providing: "ip_prefix
  cannot hold a full address ... the column refuses one rather than relying on
  a caller to truncate", and the inline comment enumerates exactly what is
  meant to be accepted — "an IPv6 /48 or /64 ending in '::'". The regex does
  not implement that.

  The integration test does not catch it: every string in its "full address"
  table is a form that does not end in '::', so the over-wide accept is
  untested.

  Separately, the IPv4 branch does not bound octets (999.999.999.0 is
  accepted). Harmless — no host identity is expressible in an out-of-range
  octet — but fix it in the same edit since the line is being touched.

Failure:
  The backstop does not hold the boundary it documents. The primary threat the
  constraint was added for — an M1 caller passing c.RealIP() straight through —
  IS blocked, because a real client address essentially never ends in '::'. The
  residual is the second-most-likely caller: one that truncates to the wrong
  boundary (a /96 or /112, or an interface-identifier strip that leaves the
  subnet intact) and is waved through by a CHECK whose comment says it cannot
  be. On a photo host, a /112 identifies a household; the whole point of
  storing a prefix rather than an address is that it does not.

  A reviewer reading 0003 in M2 will trust the header, because the header is
  unusually careful about separating "ENFORCED by the database" from "NOT
  enforced here, by decision". A promise in that list that the schema does not
  keep is the specific failure that section was written to prevent.

Perspective:
  photographer, member (whose address prefix it is), instance-admin, developer

Recommendation:
  Bound the repetition to the documented boundary — at most four groups, so
  /16 through /64 — and require nothing else to change:

      ip_prefix ~ '^[0-9a-f]{1,4}(:[0-9a-f]{1,4}){0,3}::(/(48|64))?$'

  Optionally bound the IPv4 octets in the same edit. Do NOT add a length cap on
  the column as a substitute; the group bound already removes the unbounded
  repetition.

  Do it in 0003 now. After merge this needs a second migration, and although
  that migration would succeed today — the table is empty until M1 writes to it
  — "we can tighten it later while no rows exist" is a window that closes
  silently the first time an audit row is written, and nothing marks the date.

Acceptance criteria:
  * '2001:db8:85a3:1:2:3::', 'a:b:c:d:e:f:1::' and
    '2001:db8:85a3:8a2e:370:7334:1234::' are REFUSED with
    audit_events_ip_prefix_shape.
  * '2001:db8::', '2001:db8::/48', '2001:db8::/64' and '2001:db8:85a3:1::'
    remain ACCEPTED.
  * Every case already in TestAuditEventsRefusesAFullIPAddress keeps its
    current verdict.
  * migrations/manifest.sha256 is regenerated in the same commit, and the
    append-only CI lane still passes — it will, because main carries no
    migrations, which is the only reason this edit is possible at all.

Tests:
  internal/integration/golden_test.go, TestAuditEventsRefusesAFullIPAddress:
  add the three over-wide forms to the "full address is refused" table and
  '2001:db8:85a3:1::' to the accepted table. The harness exists and already
  asserts on the constraint name, so this is four lines.

  Add one mutation check to the evidence: with the current unbounded regex, the
  new cases must fail.

Cross-repo implications:
  core: the constraint and the test. The M1 truncation helper should then be
  written to produce exactly what the CHECK accepts, and should be the only
  writer. user: an admin audit view must not render ip_prefix as a clickable
  address. search: audit rows are never indexed. meta: none.

Challenge:
  The strongest counter is that this is fixable additively — the table is empty
  until M1, so ALTER TABLE ... ADD CONSTRAINT would validate instantly, and
  holding a PR for a regex quantifier is disproportionate. I accept that the
  window does not slam shut at merge. What moves me to file it as blocking is
  that the file is open right now for exactly this kind of correction, the fix
  is one quantifier, and the constraint currently contradicts a header that
  goes out of its way to distinguish enforced controls from aspirational ones.
  A second-best counter — "a /112 prefix is not really PII" — I reject: 112
  bits of IPv6 is a household, and the column exists precisely so that it is
  not stored.
```

**Verdict:** Findings 1, 2 and 3 CLOSED; all five ride-alongs CLOSED. One new BLOCKING item (Finding 13), a one-quantifier edit in `migrations/0003_audit_events.up.sql` plus four test lines and a manifest regeneration. Nothing else in the delta blocks. Queued items untouched as instructed.
