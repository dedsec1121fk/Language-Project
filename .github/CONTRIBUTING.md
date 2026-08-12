# Contributing

Language Project intentionally separates the global catalog from the verified Termux execution registry.

## Adding an executable language

Only add a worker when the language has a real Termux-compatible runtime/toolchain and the implementation executes its own reversible transform. A worker must not delegate its transform to another programming language just to inflate the executable-language count.

Required steps:

1. Add the worker source under `languages/<id>/`.
2. Add its runtime/build/package definition to `config/registries/languages.json`.
3. Keep the protocol compatible with `PING`, `E <hex>`, `D <hex>`, and `QUIT`.
4. Add or update its catalog mapping.
5. Run `python scripts/setup.py` on an environment where the runtime exists.
6. Run `python scripts/smoke_benchmark.py`.
7. Run `python scripts/advanced_smoke.py`.
8. Run `python scripts/audit_project.py`.
9. Rebuild the project manifest with `python scripts/build_manifest.py`.
10. Verify it using `python scripts/verify_manifest.py`.

A source file alone does not make a language executable. It must pass live worker startup, protocol, deterministic transform, and round-trip validation.

## Adding orchestration features

Keep new scheduling, analysis, telemetry, persistence, or reporting logic in the Python control plane whenever possible. Avoid forcing coordinated changes across every worker unless the protocol genuinely needs to change.

New result-producing modes should:

- have a session ID and UTC timestamp,
- report integrity explicitly,
- preserve byte-oriented behavior,
- save machine-readable JSON when `save=True`,
- avoid presenting catalog-only languages as executed,
- use deterministic seeds when randomness is involved,
- document whether the mode measures serial execution, parallel contention, resilience, or some other workload.

## Catalog-only languages

Catalog-only languages belong under the generated catalog and must not be counted as executable. Catalog refresh logic should preserve unique names and stable metadata slugs without claiming runtime support that was not verified on the device.

## Useful Toolbox Changes

Changes to `core/toolbox.py`, `core/scaffold.py`, or `core/source_runner.py` should remain offline-first where practical and must not silently add network uploads or shell interpolation of user-controlled filenames.

Run these before submitting utility changes:

```bash
python scripts/selftest.py
python scripts/toolbox_smoke.py
python scripts/audit_project.py
```

## Native Multi-Language Tools

Every executable worker candidate should have exactly one practical native utility registered in `config/registries/polytools.json`. When adding a new executable language worker:

1. add the worker and its catalog mapping;
2. add `languages/<language>/tools/...` containing a useful standalone utility written in that language;
3. add the matching `config/registries/polytools.json` entry with source, run/build commands, tags, and deterministic smoke-test arguments;
4. keep the tool dependency-free beyond the runtime/toolchain already needed by that language whenever possible;
5. run `python scripts/audit_project.py` and, after runtime setup, `python scripts/langtools_smoke.py`.

A utility should solve a real local task (file/data/text/source/system analysis) rather than being another `Hello World`. Read-only behavior is preferred. Any future file-modifying native utility must clearly document its mutation behavior and should default to a preview/dry-run where practical.
