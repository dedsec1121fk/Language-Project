# Native Multi-Language Tools

Language Project contains a second practical execution layer under `languages/<id>/tools/`: **one standalone utility for every executable language candidate in `config/registries/languages.json`**.

The benchmark workers all implement the same reversible protocol. Native tools are different: each language owns a genuinely useful job that fits its strengths or gives the project practical coverage across files, data, text, source code, logs, system inspection, and integrity work.

## Trust model

A tool is not advertised as available merely because its source file exists. During `language-project setup --install`:

1. the normal language worker is installed/built and round-trip tested;
2. only languages that passed worker verification are considered for native tools;
3. compiled native tools are built under `$HOME/Language Project/build/polytools/`;
4. each tool is smoke-tested on deterministic fixture data;
5. only successful tools are written to `$HOME/Language Project/state/polytools.json` and shown with `✓`.

This means a broken compiler/runtime or a source incompatibility cannot silently become an "available" utility.

## Commands

```bash
language-project langtools list
language-project langtools status
language-project langtools run TOOL [arguments...]
language-project langtools recommend WORDS...
language-project langtools project-report DIRECTORY
language-project langtools file-report FILE
language-project langtools data-report FILE
language-project langtools auto-report PATH
language-project langtools workspace-report DIRECTORY
language-project langtools selftest
```

## Workspace Report

`workspace-report` is the strongest practical multi-language feature:

```bash
language-project langtools workspace-report ~/MyProject \
  --output ~/storage/downloads/MyProject-language-report.json
```

It runs **every native tool that passed verification on the current Termux device**. Each tool receives an input appropriate to its purpose. Some inputs are direct project files; others are temporary inventories derived from the target project. Temporary derivative files are removed automatically when the report finishes.

Examples:

- Bash inspects the device/filesystem environment.
- C measures bytes, entropy and text/binary characteristics.
- C++ calculates word frequencies.
- Python validates a generated JSONL inventory.
- JavaScript and jq inspect generated project JSON.
- Perl scans the real project for TODO/FIXME/HACK/BUG markers.
- PHP analyzes a generated CSV file inventory.
- Go summarizes the real directory tree and largest files.
- Rust provides a fast independent FNV-1a checksum when available.
- Java performs an independent binary comparison.
- Kotlin measures project-wide source/code statistics.
- Fortran calculates numeric statistics over actual file sizes.
- Racket extracts a Markdown outline when available.
- Zsh/Fish report recent/large files when available.
- sed normalizes a text preview without modifying the source.

The resulting JSON states `all_available_tools_executed: true` only when every currently verified native utility completed the report.

## Registered tools

| Language | Tool ID | Purpose |
|---|---|---|
| Bash | `sys-report` | Device/filesystem/Termux environment report |
| AWK | `tabular-stats` | TSV/tabular row and column statistics |
| C | `byte-stats` | Byte histogram indicators and Shannon entropy |
| C++ | `word-frequency` | Top word frequencies |
| Python | `jsonl-check` | JSON Lines validation and type counts |
| JavaScript | `json-format` | JSON pretty-print/minify |
| Perl | `grep-context` | Recursive regular-expression project search |
| Ruby | `unique-lines` | Stable line deduplication/counts |
| Lua | `kv-read` | `key=value` configuration reader |
| PHP | `csv-stats` | CSV row/column/empty-cell statistics |
| Tcl | `regex-filter` | Regex line filtering |
| Go | `dir-summary` | Directory size/extensions/largest-file summary |
| Rust | `fnv64` | Fast FNV-1a 64 checksum |
| Java | `file-compare` | Binary file equality/first-difference check |
| Scheme/Guile | `paren-check` | Quick delimiter-balance check |
| Erlang | `line-stats` | Line/blank/longest-line statistics |
| Elixir | `log-stats` | Common log-level counts |
| Nim | `eol-stats` | LF/CRLF/CR line-ending analysis |
| Zig | `hex-view` | Fast hexadecimal file preview |
| SWI-Prolog | `word-count` | Text word/line/character counts |
| Haskell | `duplicate-lines-hs` | Duplicate-line frequency report |
| D | `extension-stats` | Directory extension distribution |
| Kotlin | `code-metrics` | Recursive codebase line/blank/comment metrics |
| Scala | `properties-check` | `.properties` duplicate/malformed key checks |
| Dart | `jsonl-stats` | Independent JSONL statistics/validation |
| Fortran | `number-stats` | Min/max/mean over numeric records |
| Racket | `markdown-outline` | Markdown heading outline extraction |
| Crystal | `duplicate-lines-cr` | Independent duplicate-line detector |
| Common Lisp/ECL | `top-words` | Top word frequencies |
| Dash | `path-audit` | PATH missing/duplicate/writable entry audit |
| Zsh | `recent-files` | Most recently modified files |
| Fish | `large-files` | Largest paths/files report |
| sed | `trim-lines` | Trailing-whitespace normalization to stdout |
| jq | `json-shape` | JSON top-level shape/type inspection |

## Safety

- Native tools do not receive shell-interpolated commands from the dispatcher; commands are executed as argument arrays.
- Read/analysis tools do not modify input files.
- `trim-lines` writes normalized content to stdout; it does not edit the source file in place.
- FNV-1a is explicitly non-cryptographic. Use the existing SHA-256/SHA-512/BLAKE2 toolbox for security/integrity decisions.
- Quick delimiter balancing is not a language parser and may count delimiters inside strings/comments.
- Native-tool verification is device-specific. A tool can be available on one Termux installation and unavailable on another.
