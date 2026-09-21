# ADR-009: Acceptance platform, fixtures, budgets, rehearsal path

## Status
Accepted (owner) — 2026-09-20. Proposed 2026-09-15; the owner approved ADR-001…009 on 2026-09-20 (record: docs/plans/WARROOM-BOARD.md, "Owner decisions").

## Date
2026-09-15

## Context
`prompts/01-architecture-and-foundations.md` requires the first acceptance
platform chosen early, resource and fixture baselines specified, and a repeatable
clean-target rehearsal path now rather than at release week.
`docs/RELEASE_ACCEPTANCE.md` requires named hardware, declared dataset sizes and
budgets approved before acceptance, and forbids changing a budget to excuse a
failed run. `AGENTS.md` forbids paid cloud spend without authorization.

## Decision
**Platform (Q-027, as ratified).** The ruling is copied:

> "Ubuntu 24.04 on native AMD64 is the only qualified acceptance target and
> runtime images are published linux/amd64 only. The `vizra` CLI is built for
> linux/{amd64,arm64} and darwin/{amd64,arm64} from M0. `install.sh` and `doctor`
> detect a non-amd64 server host and refuse with a named message pointing at the
> ARM64 qualification status instead of pulling a manifest that fails with
> `exec format error`. Apple-Silicon developers use the build-from-checkout dev
> chain; arm64 container builds are developer-only with no support claim; no arm64
> entry is added to a multi-arch manifest until a native arm64 CI runner and an
> arm64 media lane exist."

ARM64 is therefore never advertised, and the refusal is a named message rather
than a pull failure.

**Minimum host and budgets.** The reference host is the minimum supported host
exactly as Q-028 ruled: 2 vCPU and 4 GB on Ubuntu 24.04 amd64, core profile with
ClickHouse and IPFS OFF, images pulled and never built on the host, a declared
2 GB swapfile, worker concurrency 1, a capped libvips operation cache and cache
`maxmemory` set. `doctor` refuses a host below the minimum by name, and the
installer documentation ships a sizing table for larger tiers.

The following targets are **PROVISIONAL**. They are calibrated once by the first
M0 measurement run on the reference host and frozen thereafter; from that point
VZ-OPS-007's rule applies and a budget may not be changed to excuse a failed run.

| Measurement point | Provisional target (PROVISIONAL) | Conditions |
|---|---|---|
| Metadata read latency | p95 < 300 ms | measured at the API process, not through Next SSR; 10 concurrent readers over the declared load corpus |
| One derivative set (thumbnail, medium, display) for a 12 MP JPEG | p95 ≤ 8 s | reference host, worker concurrency 1 |
| Upload burst | 100 queued 12 MP uploads drained within 15 minutes | reference host |
| Oldest pending job age | fails `doctor` and readiness above 15 minutes | exposed as a metric (ADR-004); killing the worker turns `doctor` red while `/healthz` may stay 200 |
| RPO | 24 hours (nightly) | explicitly covers originals uploaded since the last run, not only database rows |
| RTO | 2 hours | host-local restore of the declared corpus; off-site pull and S3-hosted originals get their own measured RTO in the runbook, which states which datastores a provider owns |

**Fixture corpus (VZ-FOUND-007).** The correctness corpus is **synthesised
deterministically** by a pinned script using libvips and exiftool in the CI image,
so its provenance is the script and no licence is required. The manifest, with a
sha256 per file and the generator version, is committed. The M0 manifest is:

1. JPEG with EXIF orientation 6 and GPS tags;
2. PNG with alpha;
3. truncated JPEG;
4. oversized-dimension image;
5. decoder-bomb PNG;
6. polyglot / active SVG;
7. animated GIF;
8. animated WebP;
9. AVIF;
10. 12 MP JPEG for the budget runs;
11. short MP4;
12. short WebM.

Real CC0 photographs are used only for visual QA and are listed with their source
URL and licence when added.

**Load corpus (VZ-OPS-007).** A generated 10,000-photo set from the same script,
with declared file count, total bytes and megapixel mix, kept separate from the
correctness corpus.

**Clean-target rehearsal path.** Two distinct things, not one:

- the M0 `boot` lane in meta CI runs on GitHub-hosted `ubuntu-24.04` runners and
  boots the production-mode stack from source — this is the repeatable clean
  target for the stack, available from M0;
- the `install.sh` rehearsal needs a real disposable Ubuntu 24.04 amd64 VM, which
  requires a host the owner provides or authorizes, because no paid cloud resource
  may be provisioned without authorization. It is recorded as an owner input and
  it is not substitutable by the owner's laptop, which is arm64.

Evidence for both follows the format in `docs/DEFINITION_OF_DONE.md`.

## Consequences
Positive: a synthesised corpus makes media assertions reproducible and
licence-free, and makes "the fixture changed" a diff rather than a mystery;
measuring on the minimum host means budgets describe the worst supported case;
splitting the boot lane from the install rehearsal gives M0 a real clean target
that does not wait on an owner-provided VM. Negative: measuring on 2 vCPU makes
the numbers unattractive and the runs slow, and synthesised images are not
photographs, so visual review still needs CC0 material. Risks: the boot lane can
be mistaken for install-rehearsal evidence — it is not, and any `install.sh`
claim stays UNVERIFIED until that host exists; treating a provisional number as
frozen before the first run would invert VZ-OPS-007's rule. Later milestones must
not break: amd64-only images with no arm64 manifest entry before a native runner
and media lane, the committed fixture manifest and its hashes, budgets frozen
after the first measurement, the split between correctness and load corpora, and
the rule that a budget may not be relaxed to turn a run green.

## Precedent
Copied from Vidra (survey citations): the meta `boot` lane that starts the
production-mode stack from source, probes readiness and runs both migrators from
the service images (`M/.github/workflows/meta-ci.yml:998`, with `validate:19` and
`bundle:815` beside it), the fan-in where a skipped or never-run lane fails
(`M/.github/workflows/ci-required.yml`), golden test fixtures committed with their
contract tests (`C/internal/federation/contract_golden_test.go` and
`testdata/golden/*.json`), and the habit of recording a measured number rather
than an estimate — the 10.4 s leader-failover measurement
(`M/docs/productionization/release-readiness.md:18428`).

Unlike Vidra: the survey records no acceptance-platform decision and no
deterministic fixture corpus at all — image validation there is an extension
allowlist (`C/internal/media/imagetype.go:22`), interoperability confidence rests
on golden fixtures rather than live peers
(`M/docs/productionization/federation.md:199`), real-provider storage behaviour
was never tested outside MinIO
(`M/docs/productionization/release-readiness.md:703`), and the risk register that
substituted for decisions went stale at nine of seventeen rows
(`M/docs/productionization/risks.md:161-175`). Vizra writes the platform, the
corpus and the budgets down before the first measurement so that a later number
can be compared with something.

## Evidence and ratification
Q-027 (Ubuntu 24.04 native amd64 only, amd64 images, four CLI platforms, ARM64 not
advertised) and Q-028 (reference host conditions, measurement points, provisional
targets, load corpus, RPO and RTO) in the `docs/OPEN_QUESTIONS.md` ratification
record. No dependency version is asserted here; versions live in ADR-001.

## Ledger IDs
VZ-FOUND-007, VZ-FOUND-008, VZ-OPS-007, VZ-CI-003, VZ-INSTALL-001,
VZ-BACKUP-002, VZ-TOPOLOGY-007.

## M0 obligations
The M0 foundation issue (VZ-ISSUE-001, which covers VZ-FOUND-001…008) implements
the fixture generator script, the committed manifest with sha256 values and
generator version, and the twelve M0 fixtures above in **`vizra-core` PR2**
(VZ-FOUND-007), together with the load-corpus generator; the media and privacy
assertions of M1 consume them, so they come first. The browser-test environment
(VZ-FOUND-008) is **`vizra-user` PR2** of the same issue: a Playwright harness
against the production build, desktop and mobile projects, console and network
error capture, running in CI against the built image. Only the `boot` lane and the
declared load corpus itself arrive with their own issues (VZ-ISSUE-004 / VZ-CI-003
and VZ-OPS-007).

Reservation only: budgets stay PROVISIONAL until the first measurement run on the
reference host, then freeze (VZ-OPS-007, M4); the `install.sh` rehearsal
(VZ-INSTALL-001) and the restore rehearsal on a second clean host (VZ-BACKUP-002)
wait on the owner-provided VM. VZ-FOUND-007's ledger corpus is broader than the M0
manifest — ICC wide-gamut, transparent WebP, animated AVIF, corrupt variants, MOV
and equirectangular 360 — and those files are added by the same generator as the
slices needing them land; none is dropped here.

