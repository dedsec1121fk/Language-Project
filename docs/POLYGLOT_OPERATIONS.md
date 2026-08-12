# Practical Polyglot Operations

This layer makes the verified Termux language set participate in everyday file work. Catalog-only languages are never treated as executable. Every command either sends content-bound probes or the actual file chunks through the complete active language chain and verifies exact recovery.

## Compare

`language-project polyglot compare LEFT RIGHT`

Compares two files or directory trees. SHA-256 and size decide equality, while every verified language processes content-bound probes so the language set participates in validation.

## Mirror

`language-project polyglot mirror SOURCE DESTINATION`

Dry-run by default. Add `--apply` to copy new/changed files. Every copied chunk passes forward and backward through every verified language before it is atomically installed at the destination. `--delete` only takes effect together with `--apply`.

## Split / Join

`language-project polyglot split BIG_FILE --part-size 4194304`

Creates `.lpart` files plus `LANGUAGE-PARTS.json`. Each part is stored after the complete forward language chain. `polyglot join` requires the exact recorded runtimes and reverses the chain while checking per-part and whole-file SHA-256 values.

## Dedupe

`language-project polyglot dedupe DIRECTORY`

Finds exact duplicate groups using size + SHA-256, then makes every verified language validate a content-bound probe for each duplicate group. This command is report-only and never deletes files.

## Scrub / Repair

`language-project polyglot scrub AUDIT.json --root DIR`

Checks a previous polyglot directory audit. With `--repair --mirror TRUSTED_COPY`, missing or changed files are restored only when the mirror file exactly matches the size and SHA-256 recorded in the audit. Repair copies themselves pass through all verified languages.

## Backup Health

`language-project polyglot backup-health BACKUP_DIRECTORY`

Scans protected-backup receipts, checks package SHA-256 values, and re-runs each package's polyglot seal verification with the exact recorded language set.

## Safety model

- Mirror, rename-like behavior is dry-run first.
- Split/pack formats are reversible encodings, not encryption.
- Repair requires an explicit trusted mirror and an existing audit.
- Duplicate detection never deletes data.
- Symlinks are not followed for directory traversal.
- Writes use temporary files where practical and are installed only after integrity verification.
