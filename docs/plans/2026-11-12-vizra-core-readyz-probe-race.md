# vizra-core readyz probe race (QUEUE-readyz-flake) — IMPLEMENTED, READY_FOR_REVIEW pending CI
PR yegamble/vizra-core#23, branch fix/readyz-probe-race.
Root cause: storageProbe busy flag cleared (defer) after result send -> back-to-back false 503 (verifier F-1).
Fix: clear busy before send. Regression: TestStorageProbeBackToBackNeverFalseTimeout (red on old code).
F-4 (timeout cached 2 s) unchanged: ADR-002 cache contract.
