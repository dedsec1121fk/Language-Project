# Advanced Architecture

Language Project is split into five planes so that adding complexity does not turn the worker protocol into a fragile monolith.

1. **Worker plane** — one persistent stdin/stdout worker per verified language.
2. **Execution plane** — serial chains, races, matrices, stress runs, topology lanes, consensus runs, differential audits, and checkpointed execution.
3. **Control plane** — runtime discovery, calibration, execution planning, scenarios, diagnostics, and package planning.
4. **Observability plane** — timing distributions, resource telemetry, provenance fingerprints, result files, SQLite history, regression gates, and event records.
5. **Catalog plane** — the independent worldwide language catalog. Catalog membership never implies Termux execution support.

This separation is deliberate. The worker protocol stays tiny while the Python orchestrator can grow new scheduling, reliability, reporting, and analysis behavior without forcing 34 language implementations to change together.

## Result lifecycle

A benchmark can create JSON/CSV/Markdown/HTML output. Saved results are indexed into `state/history.sqlite3`, allowing historical aggregation without parsing every JSON file on every command. Portable bundles can package recent results, active state, calibration state, registry data, and a bundle manifest with SHA-256 hashes.

## Reproducibility

Saved benchmark records can include a provenance snapshot containing registry hash, manifest hash, active-state hash, calibration hash, runtime versions, architecture, Python version, Termux prefix, and Termux version. The snapshot is also hashed into an environment fingerprint used by dry-run planning and comparisons.
