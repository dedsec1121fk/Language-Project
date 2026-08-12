# Useful Offline Toolbox

Language Project includes a standard-library-first utility plane that is independent from the benchmark workers. The goal is to make the project useful even when you are not running a polyglot benchmark.

## Codecs And Compression

```bash
language-project tools codec base64 --text "Language Project"
language-project tools codec base64 --decode --text "TGFuZ3VhZ2UgUHJvamVjdA=="
language-project tools codec gzip --file input.bin --output input.bin.gz
language-project tools codec gzip --decode --file input.bin.gz --output recovered.bin
```

Supported transformations: Base64, Base32, Base85, ASCII85, hexadecimal, URL percent encoding, Gzip, zlib, BZ2, XZ/LZMA, and ROT13.

## Hashes And Integrity

```bash
language-project tools hash --file archive.zip
language-project tools manifest-create ~/storage/downloads/MyFolder
language-project tools manifest-verify ~/storage/downloads/MyFolder/LANGUAGE-PROJECT-FILE-MANIFEST.json
```

The hash command includes CRC32 and Adler32 plus requested `hashlib` algorithms. Directory manifests stream files rather than loading whole files into RAM.

## File Intelligence

```bash
language-project tools inspect file.bin
language-project tools hexdump file.bin --limit 4096
language-project tools strings file.bin --min-length 6
language-project tools compare old.bin new.bin
```

Inspection reports size, guessed MIME type, permissions, entropy, SHA-256/SHA-512/BLAKE2, text/binary classification, line/word counts for text, and a bounded hexadecimal preview.

## Duplicate And Storage Analysis

```bash
language-project tools duplicates ~/storage/downloads --min-size 1048576
language-project tools storage ~/storage/downloads --top 30
```

Duplicate scanning first groups files by size and hashes only candidate groups. Storage analysis reports total tree size and the largest files it can read.

## JSON, CSV And Text

```bash
language-project tools json --file data.json --mode pretty
language-project tools json --file data.json --query user.profile.name
language-project tools csv records.csv
language-project tools text-stats --file README.md
```

JSON queries use simple dot-separated object keys or numeric list indexes. The CSV inspector sniffs delimiters where possible and reports row widths, headers, and a sample without requiring pandas.

## Secure Generators

```bash
language-project tools generate --kind password --length 32 --count 5
language-project tools generate --kind token --length 32
language-project tools generate --kind hex --length 32
language-project tools generate --kind uuid --count 5
```

Random values use Python's `secrets` module. Generated passwords intentionally avoid visually ambiguous characters such as `O`, `0`, `I`, and `l`.

## Archives

```bash
language-project tools archive-create ~/MyProject --kind zip
language-project tools archive-create ~/MyProject --kind tar.gz
language-project tools archive-extract ~/MyProject.zip --destination ~/Recovered
```

Archive extraction validates member paths before extraction to reject path traversal outside the destination directory.

## Local File Server

```bash
language-project tools serve ~/storage/downloads --host 127.0.0.1 --port 8000
```

The default host is loopback-only. Use a non-loopback bind address deliberately if you want another device on the network to reach it.


## Programming-Language Detection And Codebase Statistics

```bash
language-project tools identify script.py
language-project tools identify README.md
language-project tools codebase ~/MyProject --top 30
```

Detection combines the global catalog's extension/interpreter metadata, shebangs, and deterministic preferences for common ambiguous extensions. Codebase statistics summarize detected languages, file counts, bytes, and line counts while skipping common dependency/build directories.

## Starter Projects

```bash
language-project new python MyApp
language-project new rust FastTool
language-project new c NativeDemo
```

Starter templates currently cover Python, JavaScript, Bash, C, C++, Rust, Go, Java, Kotlin, Lua, Ruby, Perl, PHP, and Dart. Each generated project contains an entry file, README, `.gitignore`, and `language-project.json` run metadata.

## Execute Trusted Source Files

```bash
language-project execute demo.py
language-project execute hello.c
language-project execute program.rs
```

`execute` detects the source extension and uses a local interpreter or temporary compilation directory. It never uploads source code. **It executes the file with your Termux user's permissions, so only run source code you trust.**

Supported execution adapters include common interpreted formats plus C, C++, Rust, Go, Java, Kotlin, Nim, Zig, D and Fortran when the corresponding verified local runtime/toolchain is present.

## Search Files And Source Trees

```bash
language-project tools find ~/MyProject --pattern '*.py'
language-project tools find ~/MyProject --content 'TODO'
language-project tools find ~/MyProject --content 'password\s*=' --regex
language-project tools tree ~/MyProject --depth 4
```

`find` can combine a filename glob with literal or regular-expression content matching. Common dependency/build directories are skipped by default. `tree` gives a bounded directory view that is readable directly in Termux.

## Safe Batch Rename

```bash
language-project tools rename ~/Pictures --glob '*.jpg' --prefix trip-
language-project tools rename ~/Pictures --glob '*.jpg' --find 'IMG_' --replace 'photo-'
# Apply only after reviewing the plan:
language-project tools rename ~/Pictures --glob '*.jpg' --prefix trip- --apply
```

Rename operations are **preview-only by default** and reject destination collisions before making changes.

## Directory Sync

```bash
language-project tools sync ~/Project ~/storage/downloads/Project-Backup
language-project tools sync ~/Project ~/storage/downloads/Project-Backup --checksum
# Apply the shown copy plan:
language-project tools sync ~/Project ~/storage/downloads/Project-Backup --checksum --apply
```

`sync` copies new/changed files while preserving timestamps. `--checksum` compares SHA-256 instead of relying on size/mtime. `--delete` can mirror deletions, but still does nothing without `--apply`.

## Timestamped Backups

```bash
language-project tools backup ~/MyProject
language-project tools backup ~/MyProject --destination ~/storage/downloads/Backups --label before-refactor
```

Creates a timestamped `tar.gz` snapshot and a sidecar metadata file containing source path, archive size, creation time, and SHA-256.

## Safe Cache Cleanup

```bash
language-project tools clean ~/MyProject
language-project tools clean ~/MyProject --older-days 14
# Delete only after reviewing the target list:
language-project tools clean ~/MyProject --older-days 14 --apply
```

Cleanup targets common development caches (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`) and old temporary bytecode/temp files. It does not remove arbitrary user documents.

## Diff, TODO Scanner And Line Endings

```bash
language-project tools diff old.py new.py
language-project tools todos ~/MyProject
language-project tools eol ~/MyProject --mode lf
language-project tools eol ~/MyProject --mode lf --apply
```

The diff command produces a standard unified text diff. The TODO scanner finds `TODO`, `FIXME`, `HACK`, `XXX`, `BUG`, and `NOTE` annotations. EOL normalization is preview-only unless `--apply` is supplied and skips binary files.

## Environment And Git Diagnostics

```bash
language-project tools env
language-project tools env python git clang rustc go node
language-project tools git ~/MyProject
language-project tools processes --limit 50
```

The environment report resolves installed commands and captures concise runtime/toolchain versions. Git summary shows branch, HEAD, origin, working-tree changes, and the latest commit without modifying the repository.

## Network Diagnostics

```bash
language-project tools dns example.com
language-project tools tcp example.com 443
language-project tools http https://example.com
```

These perform a DNS lookup, a timed TCP connection attempt, or an HTTP `HEAD` request. They are explicit online operations; the rest of the utility plane remains usable offline.

## Download With Integrity Verification

```bash
language-project tools download https://example.com/file.zip --output ~/storage/downloads/file.zip
language-project tools download https://example.com/file.zip \
  --output ~/storage/downloads/file.zip \
  --sha256 EXPECTED_SHA256
```

Downloads use a temporary `.part` file and only replace the destination after a complete transfer. An expected SHA-256 can be required; mismatches delete the partial file and fail the command. HTTP and HTTPS are the only accepted URL schemes.

## Mutation Safety Model

The following commands are intentionally non-destructive by default:

- `tools rename`
- `tools sync`
- `tools clean`
- `tools eol`

They print the planned changes and require `--apply` before modifying user data. `tools sync --delete` also requires `--apply`, so accidentally adding `--delete` alone cannot remove destination files.
