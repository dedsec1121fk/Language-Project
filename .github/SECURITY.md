# Security

Language Project has two separate execution surfaces and treats them differently.

## Benchmark Workers

Normal benchmark input is opaque bytes. The benchmark/control plane never evaluates that payload as source code. Worker communication uses a constrained line protocol containing hexadecimal payloads, and workers only perform the reversible benchmark transformation.

Do not add benchmark workers that execute user-provided payload text, download and run unverified binaries, require root, or silently invoke remote code-execution services. Runtime packages should come from Termux package repositories or an explicitly documented language ecosystem.

## Trusted Source Runner

`language-project execute FILE` is intentionally different: it runs or temporarily compiles the source file supplied by the user. It executes with the same Android/Termux account permissions as the `language-project` process. Only use it for source code you trust.

The source runner constructs subprocess argument arrays directly and does not build a shell command from the filename or program arguments. Temporary compiled outputs are created in a temporary directory and removed afterward. A timeout is applied to compilation/execution, but a timeout is not a sandbox.

## Local File Server

`language-project tools serve` binds to `127.0.0.1` by default. Binding it to `0.0.0.0`, a LAN address, or another non-loopback address deliberately exposes the selected directory to clients that can reach that network interface. Review the directory before doing so.

## Archives And File Utilities

Archive extraction validates member paths before extraction so archive entries cannot intentionally escape the selected destination with `../`-style traversal. Archive creation rejects placing the output archive inside the directory being archived.

Hashing, duplicate scanning, storage analysis, language detection, and manifest tools operate locally. They do not upload file contents.

## Local Result Data

Language Project is local-first, but benchmark artifacts can contain information derived from the supplied payload. Normal chain JSON may contain the final transformed hexadecimal value, and resumable checkpoint files contain the current and original payload as hexadecimal so execution can continue after interruption. Hexadecimal is an encoding, not encryption.

Treat `results/`, `state/checkpoints/`, `state/history.sqlite3`, and manually created bundles as potentially sensitive if the input was sensitive. Do not publish those files without reviewing them first.

## Plugins

Plugins are disabled by default. When `LANGUAGE_PROJECT_PLUGINS=1` is enabled, local `.py` files in `plugins/` can execute with the same account permissions as Language Project. Only enable plugins you trust.

## Chaos Mode

Chaos mode restarts Language Project's own worker subprocesses. It does not intentionally corrupt user files, modify Android system settings, or kill unrelated processes.

## Practical Utility Safety

Language Project's practical utility plane includes both read-only and file-changing commands. Commands that can rename, synchronize/delete, clean, or normalize files are preview-only unless `--apply` is explicitly supplied. Review the generated plan before using `--apply`, especially on shared storage.

`tools download`, `tools http`, `tools dns`, and `tools tcp` are explicit network operations. Downloads accept only HTTP/HTTPS, are written through a temporary partial file, and can require an expected SHA-256. A checksum verifies integrity, not trustworthiness; only open or execute downloaded files from sources you trust.

`tools serve` exposes files over HTTP to whatever interfaces you bind. Its default bind address is loopback (`127.0.0.1`). Deliberately choosing `0.0.0.0` or another non-loopback address may expose files to other devices on the network.


## Practical Polyglot Artifacts

`polyglot seal`, `fingerprint`, `copy`, `pack`, `unpack`, and directory-audit workflows intentionally invoke every verified active language worker. They inherit the benchmark worker rule: payloads are hexadecimal data and are never evaluated as source code.

`.lpack` is **not encryption**. Its payload is reversibly transformed by the recorded language chain. Anyone with Language Project and the required runtimes can reverse that transformation. Use real encryption separately for confidential material.

`.lpack` creation validates every transformed chunk by immediately reversing it before accepting the chunk. Restoration verifies the container payload hash, each encoded chunk hash, each recovered chunk hash, the complete recovered archive hash, and then applies safe archive path checks. Symlink and hardlink archive members are rejected during `.lpack` restoration.

`polyglot copy` writes to a temporary file first and only replaces the destination after the recovered data's SHA-256 matches the source. Existing destinations require explicit `--force`.

Polyglot seal/audit files are integrity metadata, not digital signatures. They do not prove who created a file and should not be treated as authentication from a trusted publisher.

## Expanded Polyglot File Operations

`polyglot mirror` is preview-only unless `--apply` is supplied. Destination-only files are removed only when both `--apply` and `--delete` are explicitly selected. Symlinks are skipped during directory traversal.

`polyglot split` creates reversible encoded `.lpart` files. These parts are **not encrypted**. `polyglot join` verifies every encoded part, every decoded part, and the final whole-file SHA-256 before installing the recovered output.

`polyglot dedupe` is report-only. It never removes or hard-links duplicates automatically.

`polyglot scrub --repair` requires a trusted mirror. A candidate mirror file must match the expected size and SHA-256 stored in the original audit before Language Project will use it as repair material. Unexpected extra files are reported and are not deleted by scrub.

`polyglot backup-health` may be computationally expensive because it recreates stored polyglot seals with the exact runtime set recorded by each backup. It is a verification operation and never restores or deletes backup data.

## Native Multi-Language Tools

The `langtools` subsystem executes project-owned utilities written in the same real languages/toolchains used by the executable registry. Native-tool commands are constructed as subprocess argument arrays; user arguments are not concatenated into a shell command by the dispatcher.

During setup, a native tool is only marked available after its corresponding benchmark worker has passed device verification and the utility itself builds/runs against a deterministic smoke fixture. Failed utilities remain visible as unavailable with a reason.

Most native tools are read-only analyzers. `sed`'s `trim-lines` utility writes normalized content to stdout and never performs in-place edits. `fnv64` is a fast non-cryptographic checksum and must not be used as a replacement for SHA-256/SHA-512/BLAKE2 when cryptographic integrity is required. `paren-check` is a quick delimiter counter, not a parser, and may count delimiters inside strings/comments.

`langtools workspace-report` creates temporary inventories derived from a selected directory so every available language tool can receive suitable input. Those derivative files are created under a temporary directory and removed automatically. The report can contain project paths, file sizes, search matches, source metrics, and excerpts produced by native tools; review it before publishing it.
