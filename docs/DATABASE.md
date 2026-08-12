# SQLite Performance Database

Saved benchmark results are indexed in `state/history.sqlite3` using Python's built-in SQLite support. No external database package is required.

Commands:

```bash
language-project db stats
language-project db recent --limit 20
language-project db recent --mode chain
language-project db leaderboard --limit 30 --min-samples 2
language-project db rebuild
```

The database stores session-level metadata and per-language stage measurements. JSON files in `results/` remain the canonical portable records; `db rebuild` can reconstruct the local index from those files.
