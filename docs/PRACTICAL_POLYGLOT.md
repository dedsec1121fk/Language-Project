# Practical Polyglot Workflows

Language Project has two ways to use executable language workers:

1. benchmark/orchestration modes measure them;
2. practical polyglot modes make every verified worker participate in a real file or integrity workflow.

The phrase **all languages** in practical modes means **all workers that passed live setup verification on the current device**, not every catalog-only language name.

## Worker invariant

A practical polyglot operation never silently drops a verified worker. Worker startup is all-or-nothing. If a required runtime cannot be started, the operation fails instead of producing an artifact that falsely claims the full recorded language set participated.

For existing `.lpack`, seal, and directory-audit artifacts, Language Project uses the exact language IDs recorded in the artifact. Missing required runtimes are reported before processing.

## Polyglot Seal

`polyglot seal FILE` creates a JSON integrity record.

- The entire file receives SHA-256.
- File chunks are assigned round-robin to verified workers.
- Each assigned worker performs encode + decode.
- Recovered bytes must exactly match the input chunk.
- Each worker maintains a deterministic transformed digest.
- If there are fewer chunks than languages, unused workers process a deterministic anchor derived from the file hash so every worker participates.
- The final Polyglot Fingerprint combines the file SHA-256 with every language digest in worker order.

`polyglot verify` recreates the seal using the exact recorded language order.

## `.lpack`

`polyglot pack` is designed for portable project/file backups with an intentionally polyglot execution path.

1. Source is archived as `tar.gz`.
2. Archive is read in bounded chunks.
3. Every chunk goes forward through every verified worker.
4. The transformed chunk immediately travels backward through all workers as an integrity check.
5. Only a perfect round trip is accepted.
6. The transformed payload is stored in a ZIP container with `manifest.json`.
7. Chunk hashes, payload hash, archive hash, runtime set, order, and source metadata are recorded.

`polyglot unpack` validates the package payload before starting the worker chain, reverses each chunk through the exact recorded language order, validates recovered chunk hashes and the complete archive hash, then performs safety-checked extraction.

This is **not cryptographic encryption**. The transforms are intentionally reversible and exist to make every language participate.

## Verified copy

`polyglot copy SOURCE DESTINATION` reads bounded chunks. Each chunk must survive a complete forward/reverse pass through every verified language before being written. Destination writes use a temporary file and final SHA-256 comparison before atomic replacement.

This is slower than `cp` and intentionally so. Use it when the all-language verification is part of the point; use normal `cp` for ordinary copying.

## Directory audit

`polyglot audit DIRECTORY` hashes every file completely and creates a bounded probe for each file. The probe includes the file's SHA-256, binding the all-language execution to the complete file contents even when only head/tail sample bytes are sent through the worker chain. Every file probe travels through all verified workers forward and backward.

The manifest includes a deterministic tree fingerprint. `polyglot audit-verify` checks file existence, size, SHA-256, probe output, polyglot round trip, extra files, and the tree fingerprint.

## Performance considerations

Full-chain operations are deliberately expensive. With `N` active languages, each `polyglot copy` or `.lpack` verification chunk performs `2N` language transformations. Use `--chunk-size` to balance latency and memory use. Default is 64 KiB.

For very large routine backups where the all-language behavior is unnecessary, use the normal `tools backup`, `tools sync`, or `tools manifest-*` commands instead.


## Protect / Restore

`polyglot protect SOURCE` is the high-level backup workflow. For directories it creates a directory audit, creates an `.lpack`, seals the `.lpack`, and writes a receipt that records the paths, package hash, language count, and Polyglot Fingerprint. `--no-audit` can skip the directory audit when speed matters.

`polyglot restore PACKAGE` looks for `PACKAGE.language-seal.json` by default. When present, the seal must verify before unpacking begins. An explicit seal can be selected with `--seal`.

This workflow is intended for project snapshots, pre-update backups, release archives, and phone-to-phone Termux project migration. Confidential backups still need a real encryption layer.

## Expanded Operations

The practical layer also includes workflows intended for normal Termux file maintenance:

- `polyglot compare LEFT RIGHT` — compare files or directory trees with SHA-256 plus all-language content-bound probes.
- `polyglot mirror SOURCE DEST` — dry-run-first verified directory synchronization. With `--apply`, every copied chunk survives the full forward/reverse language chain before installation.
- `polyglot split FILE` / `polyglot join MANIFEST` — split large files into transport-friendly encoded parts and reconstruct them with the exact recorded language set.
- `polyglot dedupe DIRECTORY` — exact duplicate report with all-language confirmation. It never deletes files.
- `polyglot scrub AUDIT --root DIR` — verify an audited tree. Add `--repair --mirror TRUSTED` to restore only files that exactly match the trusted audit.
- `polyglot backup-health DIRECTORY` — recheck protected backup receipts, package SHA-256 values, and package seals before relying on old backups.

For command-specific safety and examples, see `docs/POLYGLOT_OPERATIONS.md`.

## Why the new workflows are practical

The project deliberately separates normal fast tools from polyglot verification. Use ordinary `tools sync`, `tools backup`, `cp`, or `sha256sum` when speed is the priority. Use the polyglot layer when you specifically want the verified language set to participate in the workflow, such as before a risky project update, when testing an old backup, when moving a release archive, or when demonstrating that every active runtime can still process real data correctly.
