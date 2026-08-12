# C Examples

These examples exercise the real Language Project module rather than teaching the language.

```bash
# Inspect runtime/module information
language-project info c

# Run the native practical tool
language-project modules demo c

# Include this language automatically in an all-language workspace report
language-project langtools workspace-report . --output "$HOME/Language Project/reports/workspace.json"
```

If this runtime is unavailable on the current Termux installation, Language Project skips it rather than reporting a false success.
