# Result Schema

Language Project result JSON is intentionally mode-specific but shares a common envelope.

Common fields include:

- `project` — always `Language Project`.
- `mode` — chain, race, parallel-race, matrix, stress, differential-audit, chaos, topology, consensus, scenario, showcase, or checkpoint-chain.
- `session_id` — unique local session identifier.
- `timestamp` — UTC ISO-8601 timestamp.
- `integrity` — whether the mode's required byte/hash checks succeeded.
- `languages` — number of verified workers participating where applicable.
- `bytes` — payload size where applicable.
- `device` — Android/Termux/Linux execution snapshot.
- `provenance` — hashes and runtime metadata describing the execution environment.
- `result_files` — generated artifact paths after a saved result is exported.

Timing-heavy modes add `ranking`, `stages`, `stats`, `rows`, or mode-specific detail arrays. Resource-instrumented chain/chaos runs can include `telemetry`.

The JSON result remains the canonical machine-readable artifact. SQLite is an index over saved results rather than a replacement for the JSON files.
