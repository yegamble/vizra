# Prompt 07 — search and optional ClickHouse addendum
Use with Prompt 04 for one acceptance item at a time.

Implement the next approved search/analytics slice. Keep Go as service/business owner, PostgreSQL as authoritative source, Redis for justified caching, and ClickHouse as optional analytics—not a prerequisite for gallery search, access checks, or uploads.

For search, implement the approved PostgreSQL full-text/trigram/filter strategy and indexes with sqlc queries and bounded pagination. Cover media, users, albums, tags, metadata filters, sorting/relevance, Unicode, and realistic large catalogs as specified. Apply authorization inside the query/projection and to facets, counts, suggestions, previews, and caches; filtering only after returning search results can still expose private information. Test permission changes immediately against cached/indexed content. Capture query plans and p95/p99 on a declared fixture/hardware/concurrency baseline.

For analytics, define versioned event schemas, meaning of every displayed metric, deduplication keys, retention, sampling where applicable, and privacy/minimization rules. Use durable outbox delivery with bounded batching, retries, backpressure, lag metrics, replay, and dead-letter inspection. Kill ClickHouse during normal uploads/comments and prove core writes remain correct. Resume it and reconcile events without double counting. Avoid writing raw private search terms, signed URLs, full IPs, or sensitive metadata by default.

Implement the same install model as other optional services: OFF creates no container; EXTERNAL tests and uses the supplied service without starting a local one; MANAGED starts the pinned container when enabled without an external endpoint. Invalid external configuration is an error, not silent fallback. Add meaningful admin status and diagnostics.

Basic operator stats must remain useful when analytics is off. Distinguish authoritative counts from eventual metrics. Specify and test ClickHouse backup/restore or replay-based reconstruction with a retained source sufficient for the declared history. External analytics backup ownership must be visible. Prove the dashboard uses real events and displays lag/error/empty states rather than generated sample numbers.
