# vizra-core PR #12 — hardening B3 (N-7 / F-1 / NEW-2 coverage / L-2): independent verification

- **Date:** 2026-09-23
- **Verifier:** an independent `vizra-verifier` session. It did not write this code.
- **PR:** https://github.com/yegamble/vizra-core/pull/12, branch `chore/m1-httpapi-redaction`
- **SHA verified:** `6edaf83cc3035f3e5ae270556082897b527893dd`. The head was confirmed with `gh pr view 12 --json headRefOid` at the start and again at the end: unchanged, OPEN, MERGEABLE.
- **Base:** `f1972e8`. GitHub's `baseRefOid` is `36a72df` (core #10), and CI merged into that commit. Main is now `96d19b3` (core #11). See V-5.
- **Environment:** darwin/arm64, go1.27.1, Docker 29.8.0. PostgreSQL 18.6 (`postgres@sha256:86c951e0…`), Valkey 9.1.2 (`valkey/valkey@sha256:c123e371…`), Redis 7.2.16 (`redis@sha256:06379549…`). These are the CI digests.
  - Containers: `vzv-pr12-21808-32179-{pg,valkey,redis72}`, bound to loopback ports only. Removed with `docker rm -f -v`.
  - Work directory: a fresh clone in `mktemp -d …/scratchpad/vzv-core-pr12-XXXXXX`, with detached worktrees `base` (f1972e8), `mut` (6edaf83) and `merged` (96d19b3 + 6edaf83, local only). The directory was deleted at the end.
- **Inputs read:** meta `AGENTS.md`, core `AGENTS.md`, the builder's plan `docs/plans/2026-09-23-vizra-core-hardening-b3-httpapi-redaction.md`, the security reviews `…pr8-m1a-owner-claim-SECURITY.md` (F-1, N-7) and `…pr8-limiter-SECURITY.md` (L-2), and the PR body.

## 1. Lanes (at 6edaf83, clean clone)

| Command | Exit | Result |
|---|---|---|
| `make ci` | 0 | `make ci: all lanes passed`. All lanes ran: fmt-check, vet, lint-imports, migrate-lint, config-template-check, openapi-verify, sqlc-verify, ci-guard, fixtures-verify, test-race (19 `ok` packages) |
| `go test -race -count=1 -json ./...` + `go-test-report.py --suite unit --floors scripts/test-floors.json` | 0 / 0 | **1209** executed, 17 packages, 0 failed, 0 skipped, floor 1028 met. httpapi 78 (floor 66), cache 9 (floor 7) |
| `go test -race -count=1 -tags=integration -json ./...`, **Valkey 9.1.2** + report | 0 / 0 | **1378** executed, 18 packages, 0 failed, 0 skipped, floor 1171 met |
| same, `-shuffle=on`, Valkey | 0 / 0 | **1378**, 0 failed, 0 skipped |
| same, **Redis 7.2.16** (`redis_version:7.2.16` read from the container) | 0 / 0 | **1378**, 0 failed, 0 skipped |
| `--emit-floors` on the unit events and on the Valkey integration events | — | Byte-for-byte equal to the committed floors (checked by script). unit: `min_tests` 1028, httpapi 66, cache 7. integration: `min_tests` 1171, httpapi 66, cache 7, integration 144. No package differs, and no committed package is missing from the output. The diff's only `-` lines are 1006→1028, 1150→1171, cache 4→7 and httpapi 48→66, in both suites. **Nothing was lowered.** |
| Extra: `make ci` + unit report on a LOCAL merge of 6edaf83 into current main `96d19b3` | 0 / 0 | `make ci: all lanes passed`. Unit **1353** executed, 0 unexpected skips, floor 1028 met |

Temp-dir leak (`internal/integration/healthcheck_test.go`): my first Valkey run created `$TMPDIR/vizra-healthcheck-bin-2161544840` (74 MB). Its birth time, 14:07:29, falls inside that run's window. I deleted it by exact path. I pointed the later runs at `TMPDIR=<my scratch>/tmp`, so their leaks (`…-3031316264`, `…-310793834`, 149 MB in total) went with my scratch directory. There is also `vizra-fixtures-shared-230572682`, created at 14:34 while other agents' `go test` processes were running. I could not attribute it to my runs, so I did not touch it. The system `$TMPDIR` holds 163 `vizra-*` directories in all; they belong to others.

## 2. Red on base, and M1–M7

**Red on base.** Only the new tests were added onto `f1972e8`: `logsites_test.go`, plus the head's `ratelimit_test.go`, which is additions only.
- `go test -count=1 -v -run 'TestEveryLogSiteInTheAPIIsRedacted|TestTheLogSiteChecker|TestTheErrorHandlerRedacts' ./internal/httpapi/` exited **1**:
  - The coverage test reports **10** unredacted values at 5 sites: middleware.go:166–167 ×4, setup.go:466 ×2, :472, :494, :496, and setup_limits.go:145. It counts 6 sites.
  - The behaviour test finds all four secrets in the log: the DSN password, the signature, the credential and the path API key.
  - The planted-shape self-test passes on base, as expected, because it tests the checker and not the product.
- `go test -count=1 -v -run Cancelled ./internal/cache/` exited **1**, and all three tests fail:
  - Degraded flips on each of the 3 calls.
  - The cancelled calls return `(true, 0)`.
  - The live control then gets `(false, 0)`, because the budget was already spent.
  - The mid-command test flips degraded.
  - The in-process test is charged.

**Mutations on the fixed tree.** Each one was restored and green was re-confirmed.

| # | Mutation | Observed |
|---|---|---|
| M1 | The 500 line reverted to raw `err.Error()`, `reqID`, `URL.Path` and `Method` | coverage red (4 values), behaviour red (all 4 secrets); restored: `ok` |
| M2 | `s.deps.Logger.Info("m", "path", p)` appended to probes.go | red on the value (probes.go:291) AND `examined 7 … expected 6` |
| M3 | `obs.Redact` removed at setup_limits.go:146 | Removing it alone does not compile: the `obs` import becomes unused. I kept the import alive with `var _ = obs.Redact`. The test is then red at setup_limits.go:146:78, with the count still 6. Reproduced. |
| M4 | `slog.Any("error", cause)` in `unavailable()` | red: "argument 3 of Error(...) is not a string-literal key" (and a follow-on at arg 5) |
| M5 | L-2 pre-check removed | `TestACancelledRequestDoesNotChargeTheInProcessLimiter` red. The other two stay green, because the post-Exec check still covers them. |
| M6 | L-2 post-Exec check removed | `TestARequestCancelledMidCommandDoesNotFlipTheLimiterToDegraded` red (degraded flipped, `(true,0)`) |
| M7 | `logsites_test.go` deleted, whole unit suite + report | go exit 0. The report against the new floors exits **1**: "internal/httpapi executed 56 test(s); its recorded floor is 66". Against the base floors (`git show f1972e8:scripts/test-floors.json`) it exits 0 (1187 executed). |

## 3. How strong the coverage test is (inert planted source in `mut/`, one file at a time, `TestEveryLogSiteInTheAPIIsRedacted`)

| Shape | Result |
|---|---|
| logger in a struct field (`h.lg.Error("m","path",p)`) | CAUGHT (value) |
| **method value** (`f := s.deps.Logger.Error; f("m","path",p)`) | **ESCAPED**: pass, count 6 |
| `slog.Log(ctx, lvl, "m", "path", p)` | CAUGHT |
| `LogAttrs(..., slog.String("path", p))`, and with `attrs...` | CAUGHT (non-literal key) |
| wrapper function in the package (`func w(l, v){ l.Error("m","v",v) }`), and a variadic wrapper | CAUGHT (inside the wrapper) |
| **`Handler().Handle(ctx, rec)` with `rec.AddAttrs(slog.String("path",p))` or `rec.Add("path",p)`** | **ESCAPED** ×2 |
| `With("path", p)` | CAUGHT |
| `slog.New(Handler().WithAttrs([]slog.Attr{slog.String("path",p)})).Info("m")` | caught **only by the count** (7 ≠ 6). The raw attribute itself is not reported. |
| `slog.Group("g","path",p)` as an argument; `"g", slog.GroupValue(...)`; `WithGroup("g").Info("m","path",p)` | CAUGHT |
| **helper in ANOTHER package** (`vzvprobe.LogFailure(s.deps.Logger, p)`) | **ESCAPED**: pass, count 6 |
| **`slog.NewLogLogger(h, lvl).Printf("m %s", p)`** | **ESCAPED** |
| **`os.NewFile(2, "e").WriteString(p)`** | **ESCAPED** |
| **`panic("request failed: " + p)`** (no Recover middleware; net/http writes the panic value to stderr) | **ESCAPED** |
| a local `obs := fake{}` shadowing the import, as a NEW site | caught only by the count |
| **the same shadow at an EXISTING site** (setup_limits.go:146) | **ESCAPED**: pass, count 6 |
| `[]any{"path",p}...`, an interface-typed logger, the method expression `(*slog.Logger).Error(l, …)`, `slog.Default().Error`, `obs.Redact("x")+p` | CAUGHT |

- **Real code.** I scanned every non-test httpapi file for these escape shapes: method values, `Handler()`, `NewRecord`, `NewLogLogger`, `os.NewFile`, `syscall`, `panic(`, and a logger passed to another package. **None occur.** The logger goes only to `errorHandler` and `siteMiddleware`, both in this package. The rule holds on the code as it stands.
- **The count of 6.** It is a sound anti-vacuity guard: if the walker stops recognising the sites, the test goes red, and M2 shows an added recognised site is caught. It is **not** a completeness guard. Any shape the walker does not recognise leaves the count at 6, so it cannot bound what it cannot see. Swapping one recognised site for an unrecognised one moves the count and turns the test red. The row and the test describe the refusals by name and do not claim more, except as noted in V-1.

## 4. What `obs.Redact` actually covers

I called `obs.Redact` directly with fake, non-functional values (`…/out/redact-probe.txt`, reproduced in V-1).
- **REDACTED:**
  - `scheme://user:pw@`, including a password that contains `:`;
  - `X-Amz-Signature`, `X-Amz-Credential`, `X-Amz-Security-Token`, `Signature=`, `sig=` (Azure) and `token=` query values, including inside JSON;
  - `Bearer …`;
  - a `vzk_…` key anywhere, including in a path.
- **LEAKS:**
  - `redis://:PW@cache:6379/0`, the empty-username requirepass form that `redis.ParseURL` in `cache.Open` accepts;
  - a URL password containing `/`, or containing `@` (partly leaked);
  - a keyword/value DSN `password=…`;
  - `?password=`;
  - GCS `X-Goog-Signature` and `X-Goog-Credential`;
  - `?api_key=`, `?key=`, `?access_token=`, `?claim_token=`;
  - a cookie value such as `vizra_session=…`;
  - an API key in a path without the `vzk_` prefix. This is not a Vizra key format, so it is acceptable.
- **No "private metadata" pattern exists.** Two sentences claim otherwise, both pre-existing and neither authored by this PR:
  - the package comment in `internal/obs/log.go:1-4` says the rule covering "…session ids, API keys or raw private metadata" is "enforced in the logger so a call site that passes a secret cannot put it in a log line";
  - core `AGENTS.md:243` says "No credential, signed URL, session id or API key ever reaches a log line".
  - A session id is only redacted when it sits under a secret-named key, and only by the handler, not by `Redact`.
  - The PR body says, correctly, that there is no private-metadata class. Its sentence "`obs.Redact` scrubs credentials, signed-URL queries, bearer tokens and API keys" is broader than what was measured (V-1).

## 5. L-2: context cancellation versus the server's own timeouts

- **Measured** with a standalone probe (`http.Server{ReadTimeout: 500ms, WriteTimeout: 500ms}`, a handler that sleeps 1.5 s):
  - a client that waits sees `ctx.Err() = <nil>` after both server timeouts have elapsed;
  - a client that disconnects sees `context canceled`.
- cmd/api sets only ReadHeader/Read/Write/Idle timeouts, and httpapi has no timeout middleware. The only `context.WithTimeout` is the readiness probe (probes.go:142), which is not a limiter caller.
- So today a request context ends before `Allow` only when the client has gone. The early `(false, 0)` refuses nobody who is waiting.
- The documented intent is in the comment at `ratelimit.go:87-95` and in the new AGENTS row. The comment says "or its deadline passed", and "the answer goes to a request nobody is waiting for". That is true for a disconnect. It would not be true for a future per-request deadline: a client still waiting would get a 429 from `allowSetupRequest` instead of a 503. See V-4. It is latent today.
- The failure-budget path: a request cancelled after its token was examined is now charged nothing. Before, only the per-process fallback was charged. Against a 256-bit token this is immaterial, as the limiter review §2 shows, and before the budget is reached, `classifyRefusal`'s re-read already fails on a cancelled context and charges nothing.

## 6. CI on 6edaf83 (own `gh api`)

- `check-runs` for this commit, every one `completed`:
  - `ci-required` success (job 107307425048, run 35898227174, head_sha 6edaf83);
  - `append-only`, `build-test`, `cache-matrix` (aggregate, which checks that its legs' result is `success`), both `cache-matrix-leg` (redis `redis_version:7.2.16`, valkey `valkey_version:9.1.2`), `fixtures`, `govulncheck`, `docker-build`, GitGuardian: all success;
  - `image-scan`: failure. It is not required, and `.github/required-checks.txt` explains why it is deliberately absent.
- The ci-required log shows:
  - the guard: all 6 floor lanes present and non-optional, and each required check resolves to a job;
  - the wait loop ends with `SUCCESS` for `append-only`, `build-test`, `cache-matrix`, `fixtures`, `govulncheck`, `docker-build`, then "all 6 required check(s) succeeded".
  - The manifest's six names match the six jobs that actually ran on this SHA. None is listed without having run.
- Provenance in every job:
  - TESTED TREE `3b29172` = merge of head `6edaf83` (HEAD^2, which "checked: == the PR head SHA") into base `36a72df` (HEAD^1).
  - build-test's own report: unit 1306, integration 1475, shuffled 1475, 0 skipped, go exit 0.

## 7. Diff audit (AGENTS.md review list)

- **Privacy:** the fix only adds redaction. The client body is unchanged: the canned message and the request id. The behaviour test also asserts no secret reaches the body.
- **Assertions:** none weakened or deleted. The diff has no `-` lines in any test file. There are no skips, no hand-edited generated files, no invented APIs (`ExpireNX`, `TxPipeline` and `slog` are all real), and no unbounded resources.
- **Test hygiene:** the mid-command test uses a loopback listener that never answers.
  - The cancel fires when the connection is ACCEPTED, so the command is blocked in dial/handshake or on the read, depending on the race. That is 0.00 s in one run and 2.00 s (the ReadTimeout) in another.
  - Either way it reaches the post-Exec branch, which M6 proves.
  - Its cleanup drains the channel without closing it. It passed under `-race` in every run above.
- **Floors:** raised only, and equal to the generator's output (§1).

## Findings

```
FINDING V-1: the new AGENTS.md row says "The API leaks no credential into its OWN log whichever slog handler it was built with"; at measured strength it does not hold
Severity:    REQUIRED (a false-guarantee sentence authored in this PR; the code change itself is correct)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     AGENTS.md:267 (new row), internal/obs/log.go:30-38 (valuePatterns, pre-existing), internal/search/service.go:53,70 (pre-existing), PR #12 body "Did not run / out of scope"
  requirements: VZ-OPS-005

Observed:
  The 500 path's redaction is exactly obs.Redact. Driving the SHIPPED errorHandler with fake causes
  (inert probe test in a scratch copy, removed afterwards):
    VZV500 LEAKS    | plain slog.JSONHandler     | cache URL, empty user (redis://:PW@cache:6379/0)
    VZV500 LEAKS    | obs.NewLogger(production)  | cache URL, empty user
    VZV500 LEAKS    | both handlers              | keyword/value DSN "host=db user=vizra password=PW"
    VZV500 LEAKS    | both handlers              | "postgres://db/vizra?password=PW"
    VZV500 LEAKS    | both handlers              | GCS "?X-Goog-Signature=…"
    VZV500 REDACTED | both handlers              | "postgres://vizra:PW@db/vizra" (the only form the behaviour test uses)
  The redis://:pw@ form is the requirepass form redis.ParseURL accepts in cache.Open (cache.go:59).
  obs.NewLogger does not help: the key "error" is not in secretKeys, so the handler applies the same Redact.
  Separately, "The API" process has log sites outside internal/httpapi. search.Service
  (service.go:53,70) logs raw err.Error() and falls back to slog.Default(). A handler panic reaches
  net/http's stderr log unredacted (no Recover middleware, no ErrorLog). Neither is covered by the
  row's mechanism.
  The row's MECHANISM clause (every internal/httpapi value is a literal or obs.Redact) is TRUE and
  proven (§2, §3). The HEADLINE clause is not.

Failure:
  A reader of the control matrix is told the API cannot log a credential under any handler. Any
  error whose text carries one of the credential forms above is logged verbatim, under either
  handler. Today's drivers do not quote these strings (pgx omits the password; go-redis does not
  echo the URL, and cache.Open deliberately does not), so current exposure is low. The sentence is
  the defect, and it is exactly what the next reviewer will rely on.

Perspective: operator

Recommendation:
  Smallest: rewrite the headline to measured strength. For example: "Every value at every
  internal/httpapi log site passes obs.Redact at the call site, whichever handler is installed.
  What that removes is obs.Redact's pattern set (URL user:password, AWS/Azure presigned params,
  Bearer, vzk_ keys); forms outside it (redis://:pw@, key=value DSNs, GCS signatures) are NOT
  removed." Make the same correction to the PR body sentence.
  Alternatively, or in addition, and as a follow-up slice: extend valuePatterns to cover `://:pw@`,
  `password=`, `X-Goog-Signature`/`X-Goog-Credential` and `access_token=`, with cases in
  TestRedactionOfEveryValueClass and TestTheErrorHandlerRedactsTheCauseOfA500.

Acceptance criteria:
  Either no sentence in AGENTS.md:267 or the PR body claims more than the pattern set, or each of
  the four leaking forms above is redacted through errorHandler under a plain JSON handler.

Tests:
  internal/httpapi TestTheErrorHandlerRedactsTheCauseOfA500: add a sub-case per form (fake values);
  internal/obs TestRedactionOfEveryValueClass: the same forms.

Cross-repo implications:
  core: this item | user: none | search: none | meta: ledger text for VZ-OPS-005, if it repeats the absolute
Challenge:
  Row 266 (worker) uses the same absolute wording and was accepted, and row 243 is broader still.
  The builder inherited the phrasing, and no current error string carries these forms. Against
  that: the war room has held that a false-guarantee sentence authored in a round blocks
  (pr11 R1-1), and this row is new text.
```

```
FINDING V-2: the log-site checker recognises logger calls by name, so seven shapes escape it; the count of 6 guards only against vacuity
Severity:    SHOULD (none of the shapes occurs in internal/httpapi today)
Confidence:  high

Affected:
  repo:      vizra-core
  files:     internal/httpapi/logsites_test.go:58-148 (checkLogSites), :209 (count)

Observed (§3):
  ESCAPED with the count unchanged:
    - a method value (f := l.Error; f(...));
    - Handler().Handle with a hand-built Record (AddAttrs or Add);
    - slog.NewLogLogger(h, lvl).Printf;
    - a helper in another package that takes the logger;
    - os.NewFile(2, …).Write*;
    - panic(<request text>);
    - a local `obs` shadowing the import at an EXISTING site.
  Caught only by the count:
    - Handler().WithAttrs(raw) followed by a new .Info;
    - a shadowing `obs` at a NEW site.

Failure:
  A later change can put a raw value in the API log through one of these shapes, and the test stays
  green. The comment at logsites_test.go:49-51 ("nothing leaves the package through another channel")
  reads broader than the list it enumerates.

Perspective: developer, operator

Recommendation:
  In checkLogSites:
    - flag any SelectorExpr naming a slogArgLayout method that is not in call position (method values);
    - flag the names Handler/NewRecord/AddAttrs/Add-on-Record/NewLogLogger, os.NewFile and syscall.Write;
    - flag panic with a non-literal argument;
    - flag any declaration in the file whose name equals the obs import name;
    - flag passing a *slog.Logger-typed identifier (by name: deps.Logger / log / logger) as a call
      argument to another package.
  Each needs a planted case in TestTheLogSiteCheckerCatchesPlantedUnredactedCalls. Or accept the
  ~15 s go/types pass the comment mentions.

Acceptance criteria:
  Each §3 ESCAPED shape, planted in synthetic source, is reported by the checker.

Tests:
  The existing planted-shape table gains one entry per shape.

Cross-repo implications:
  core: jobs/logsites_test.go has the same by-name design | others none

Challenge:
  The rule is a review aid, not a sandbox. Deliberate evasion (shadowing, method values) is a code
  review problem, and every escape here is an unusual shape that a reviewer would notice.
```

```
FINDING V-3 (NIT): the L-2 comment says "or its deadline passed … the answer goes to a request nobody is waiting for"
Severity:    NIT
Confidence:  high

Affected:
  files:     internal/cache/ratelimit.go:87-95

Observed:
  The standalone probe (§5) shows a server Read/WriteTimeout does not cancel r.Context(); only a
  disconnect does. No per-request deadline exists in cmd/api or internal/httpapi. So a context ends
  before Allow only when the client is gone, and the behaviour is right today.
  If a per-request deadline is added later, a client still waiting whose deadline expired would get
  429 "rate_limited" from allowSetupRequest instead of a 503.

Recommendation:
  Say "the client disconnected" in the comment, or note that a deadline-expired request is answered
  429 by the ceiling callers.
```

```
FINDING V-4 (NIT): the plan's CI provenance is misstated
Severity:    NIT
Confidence:  high

Affected:
  files:     meta docs/plans/2026-09-23-vizra-core-hardening-b3-httpapi-redaction.md (Blockers and handoff)

Observed:
  The plan says CI ran on the "merge ref against main 96d19b3, which includes core #10/#11". Every
  job's provenance says HEAD^1 = 36a72df (core #10 only). The tested tree is 3b29172.
  My local merge of 6edaf83 into 96d19b3 passes `make ci` (exit 0) and the unit report (1353
  executed, 0 unexpected skips). That tree has not been through CI.

Recommendation:
  Correct the sentence. The chair may want CI re-run against current main before merging, although
  the verified-SHA rule is already met.
```

(NIT cap reached. Also observed, and not raised as a finding: M3 as described does not compile until the `obs` import is kept alive. With that, it reproduces.)

## Evidence claims checked

| Claim | Result |
|---|---|
| N-7/F-1: the 500 line redacts error, request_id, path and method; the other 4 sites too | TRUE (diff; §2 M1; base red on all 10 values) |
| Coverage test: literal messages and keys, a literal or `obs.Redact` value, refuses log, fmt.Print*/Fprint*, print/println and os.Stdout/Stderr, count pinned at 6 | TRUE as enumerated. Escapes outside the enumeration are in V-2. |
| The self-test plants 16 shapes (plus the log package and a fake obs, 19 sub-tests) | TRUE (19 sub-tests pass in the unit events) |
| L-2: `(false,0)` before and after `Exec`, 3 tests | TRUE (base red 3/3; M5, M6) |
| Floors httpapi 66, cache 7, min_tests 1028/1171, nothing lowered | TRUE; equal to my own `--emit-floors` |
| M1–M7 reproduce; red on base | TRUE (M3 needs the import kept alive) |
| `ci-required` green on 6edaf83; image-scan red and not required | TRUE |
| CI tested the merge against 96d19b3 | FALSE; it was 36a72df (V-4) |
| "`obs.Redact` scrubs credentials, signed-URL queries, bearer tokens and API keys" (PR body) | Broader than measured (V-1) |
| AGENTS.md:267 "leaks no credential … whichever slog handler" | FALSE at measured strength (V-1) |

## Verdict

- **Reproduced:**
  - all the code, test and CI claims: `make ci`, unit, integration ×3 (Valkey, Valkey shuffled, Redis 7.2), red on base, M1–M7, floors, and `ci-required` with its six required checks on the SHA;
  - the fix and the coverage test themselves.
- **Blocking:** V-1. The new AGENTS.md row's headline is a false guarantee at measured strength, and the PR body repeats a broader version of it. The fix is a wording change of one sentence in AGENTS.md:267 and one in the PR body. Extending `obs.Redact` is the alternative.
- V-2 is a SHOULD for a follow-up. V-3 and V-4 are NITs.

FINAL VERDICT: FAIL — SHA 6edaf83cc3035f3e5ae270556082897b527893dd
