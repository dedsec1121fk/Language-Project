# Language Project Storage Layout

Language Project keeps application source separate from generated data.

```text
$HOME/Language Project/
├── app/          # installed source code
├── build/        # compiled workers and compiled native tools
├── state/        # active-runtime state, calibration, SQLite history, checkpoints
├── results/      # benchmark/session results
├── bundles/      # portable result bundles
├── backups/      # Language Project-created backup artifacts
├── reports/      # workspace/native-tool reports
├── logs/         # diagnostic logs
├── cache/        # regenerable caches
├── tmp/          # temporary working files
├── downloads/    # project-managed downloads
└── workspace/    # optional local working area
```

The installer creates this tree automatically. Runtime/build/state output is never intentionally written beside the Git repository source after installation.
