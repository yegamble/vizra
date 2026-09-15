# Prompt 05 — media/storage specialist addendum
Use with Prompt 04 for one acceptance item at a time.

Select the next dependency-ready media or storage requirement. Apply the shared contract and implement only that slice fully, preserving the remaining milestone scope.

Design against a real media corpus: portrait/landscape, EXIF rotations, ICC/color profiles, transparent PNG/WebP, animation, large dimensions, corrupt/truncated files, and every advertised format. Include AVIF and the audited video formats when their slice is due; add HEIC/RAW only as explicitly approved capabilities, not untested claims. Check actual decoder/library/platform support. Preserve original and derived representations with explicit metadata/privacy and download policy. Public display should not leak GPS or other private metadata by default.

Required upload behavior includes authenticated and optional guest uploads, file picker/drop/paste, resumability/chunks, cancellation/retry/progress, quota reservation, duplicate/idempotent completion, and durable processing. Bound bytes, pixels, frames, memory, temporary disk, subprocess time, concurrent uploads, and extraction depth. Use safe filenames and quarantine; no untrusted active SVG/HTML on the application origin. Remote URL uploads/imports require SSRF protections covering redirects, DNS resolution, private/link-local/metadata endpoints, and download limits [UPLOAD, SSRF].

Test storage contract operations with local and S3-backed implementations. Include signed/multipart transfer, abort, checksums, range retrieval where supported, permissions, CORS, credentials failure, timeouts, cancellation, deletion/versioning, and cleanup. AWS and Backblaze require real-provider acceptance in addition to local emulation. Never report all S3 providers supported because one emulator passes [B2]. Ensure one user's deduplication results do not reveal another user's private media.

Make storage migration restartable and integrity-checked; do not remove the source until reconciliation succeeds. Existing records must retain their correct provider location when defaults change. Report native non-S3 adapter requirements separately rather than mapping everything to S3 by fiat.

Expose jobs, failures, retry/cancel, and storage status through actual operator UI/CLI. Test a crash between object write, database finalize, and queue dispatch; restore consistent state without lost media, double quota charges, or visible invalid images. Provide decoded-file/browser evidence and memory/resource observations, not only success return codes.
