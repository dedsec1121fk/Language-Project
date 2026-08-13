# Advanced Offline Workbench

Language Project includes a standard-library-only workbench for practical Termux tasks that should not require extra Python packages.

## Integrity and binary inspection

- `tools signature FILE` — recognize common file signatures from magic bytes.
- `tools chunk-hash FILE` — hash a file chunk-by-chunk and produce a full digest.
- `tools checksum-write FILE` / `tools checksum-verify SIDECAR` — portable checksum sidecars.
- `tools archive-list ARCHIVE` — inspect ZIP/TAR contents without extracting them.

## Developer and data work

- `tools regex-test PATTERN` — test regexes and get offsets/groups.
- `tools clean-text` — trim, drop blank lines, deduplicate and sort text.
- `tools word-frequency` and `tools ngrams` — quick corpus/source analysis.
- `tools csv-to-json` / `tools json-to-csv` — offline format conversion.
- `tools json-diff A B` — structural JSON comparison.
- `tools env-parse FILE` — parse `.env`-style files without executing them.
- `tools sqlite-info DB` and `tools sqlite-query DB SQL` — read-only SQLite inspection.

## System helpers

- `tools cidr NETWORK` — IPv4/IPv6 CIDR calculations.
- `tools url-info URL` — parse URLs without making a network request.
- `tools permissions MODE_OR_PATH` — explain Unix permissions.
- `tools base VALUE --from-base N --to-base N` — convert integer bases 2–36.
- `tools safe-name NAME` — create a portable filename.
- `tools text-split FILE` and `tools merge-files ...` — split/merge files locally.

SQLite query mode is deliberately read-only. Mutating SQL is rejected and the database is opened with SQLite URI `mode=ro`.
