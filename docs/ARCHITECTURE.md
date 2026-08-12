# Architecture

Language Project is split into six cooperating planes so a very large catalog does not get confused with executable support.

- **Control plane:** `Language.py`, interactive UI, command dispatch, profiles, setup, package planning, diagnostics, history, and comparison.
- **Verification plane:** `scripts/setup.py` installs/finds runtimes, builds compiled workers, executes protocol test vectors, records versions/metrics, and writes `state/active.json`.
- **Execution plane:** persistent language workers under `languages/`, coordinated by `core/engine.py`. Workers are prestarted concurrently and then reused for timed requests.
- **Analytics plane:** `core/analytics.py` provides percentiles, jitter, throughput, entropy observations, device/memory/load/thermal snapshots, and session IDs.
- **Catalog plane:** `catalog/known_languages.json` plus one metadata file per cataloged language and a best-effort online refresh system.
- **Evidence plane:** benchmark JSON/CSV/Markdown/HTML artifacts, runtime state, schemas, result history, and the SHA-256 file manifest.

The transport is hexadecimal so arbitrary binary payloads can cross line-oriented runtimes safely. This doubles the transport representation size but avoids text-encoding ambiguity between languages and makes strict output validation simple.

The serial chain is intentionally sequential because each stage consumes the exact output of the previous language. Workers themselves are launched/prewarmed concurrently before the chain starts, minimizing avoidable startup delay while preserving the “every language touched this exact payload” property.

## Native Multi-Language Utility Plane

`polytools.json` and `core/langtools.py` form an execution plane separate from the reversible benchmark protocol. The registry intentionally maps **exactly one native utility to each executable language candidate**. This preserves clear provenance: a tool labelled C is compiled from the C source under `polytools/c/`, a Go tool from `polytools/go/`, and so on.

Setup order is worker-first, tool-second. A native tool is never activated if its language worker failed. Compiled native tools live in `build/polytools/`; interpreted tools run from source. Every candidate receives a deterministic smoke fixture before `state/polytools.json` records it as available.

The report orchestrators (`project-report`, `file-report`, `data-report`, and `workspace-report`) only coordinate processes and aggregate output. They do not reimplement the native utility's analysis in Python. `workspace-report` intentionally creates temporary derivative inventories so heterogeneous tools can all contribute useful results to one real project analysis.
