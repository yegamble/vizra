# The council finding format — every teammate uses exactly this

One block per finding. No prose reports, no essay summaries. The format is what
lets a backend engineer and a business strategist argue about the same object.

```
FINDING <n>: <one-line title>
Severity:    BLOCKER | REQUIRED | SHOULD | EXPERIMENT | NIT
Confidence:  high | medium | low

Affected:
  repo:      vizra | vizra-core | vizra-user | vizra-search  (one primary)
  files:     path:line, path:line — real paths you opened, or the API/component name
  requirements: VZ-… IDs from docs/quality/features.json (or "none yet — propose <ID>")

Observed:
  Concrete evidence from the current code, config, ledger or docs. Quote the
  line or name the symbol. If you could not verify something, write
  "UNVERIFIED: <what I could not check and why>" instead of asserting it.

Failure:
  What is currently wrong, missing or incomplete — and what actually happens
  as a result (to a person, to data, to the operator).

Perspective:
  Who suffers: visitor | member | photographer | instance-admin | operator | developer | business

Recommendation:
  The smallest coherent solution. Not the ideal architecture — the smallest
  change that closes the failure.

Acceptance criteria:
  Observable conditions that let someone else declare this solved. Written so
  they can be checked without reading your report. Include the negative,
  privacy and recovery case where relevant.

Tests:
  How QA proves it — named suite/file and the specific case, in the repo's
  idiom once one exists. Say explicitly when the harness to run it does not
  exist yet and what the smallest harness change would be.

Cross-repo implications:
  core: … | user: … | search: … | meta: …   (write "none" where none)

Challenge:
  The strongest counterargument to your own finding — the one you want the
  council to attack in cross-examination.
```

## Severity definitions (shared, non-negotiable)

- **BLOCKER** — do not release. Data loss, privacy/visibility bypass (private
  original, derivative, metadata, count, cache, feed, federation or IPFS leak),
  security hole, an operator cannot recover, or a headline feature is unusable.
- **REQUIRED** — the product is incoherent without it. A vertical slice with a
  hole in it: backend with no reachable UI, a control with no contract, an
  admin surface that requires SSH + SQL, a ledger obligation silently dropped.
- **SHOULD** — a real improvement with a real cost; worth scheduling.
- **EXPERIMENT** — plausible but unproven. Must name the measurement that
  would confirm or kill it.
- **NIT** — correct but small. Cap yourself at three NITs; they are noise.

## Rules of evidence

1. Cite files you actually opened. A finding with no `path:line` (or ledger ID)
   is an opinion, not a finding — mark it `Confidence: low` and say so.
2. Never assert a file does not exist because a recursive grep from the meta
   root found nothing — that search skips nested checkouts. Re-run from inside
   the component repo before claiming absence. Until component repos exist,
   say "not yet created" rather than "missing".
3. Distinguish *planned* / *implemented* / *verified* / *merged* / *released* /
   *deployed*. Do not call something shipped because it is on `main`, and never
   mark anything VERIFIED on the strength of a summary.
4. If two readings of the evidence are possible, give both and pick one.
5. Scope reductions are findings, never silent edits. A requirement that
   should be dropped is a DECLINED proposal for the owner, with the reason.
