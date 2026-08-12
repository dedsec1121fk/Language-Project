# Prolog (SWI) — Language Project Module

This module is part of **Language Project** and is enabled only when its Termux runtime/toolchain passes live verification on the current device.

## Included files

- Worker implementation: used by the reversible all-language execution and integrity chain.
- Native practical tool: **Word/Line/Character Count** (`word-count`), category **text**.
- `metadata.json`: machine-readable module capabilities.
- `examples/`: reproducible commands and sample data for this language module.

## Termux packages

`swi-prolog`

## Practical use

```bash
language-project info prolog
language-project modules demo prolog
```

The native tool and benchmark worker are separate. A language can be present in the repository but is not advertised as active until setup confirms it actually runs on the Android/Termux device.
