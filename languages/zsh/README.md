# Z shell — Language Project Module

This module is part of **Language Project** and is enabled only when its Termux runtime/toolchain passes live verification on the current device.

## Included files

- Worker implementation: used by the reversible all-language execution and integrity chain.
- Native practical tool: **Recent Files** (`recent-files`), category **files**.
- `metadata.json`: machine-readable module capabilities.
- `examples/`: reproducible commands and sample data for this language module.

## Termux packages

`zsh coreutils`

## Practical use

```bash
language-project info zsh
language-project modules demo zsh
```

The native tool and benchmark worker are separate. A language can be present in the repository but is not advertised as active until setup confirms it actually runs on the Android/Termux device.
