# Contributing

Language Project intentionally separates the global catalog from the verified Termux execution registry.

## Adding an executable language

Only add a worker when the language has a real Termux-compatible runtime/toolchain and the implementation executes its own reversible transform. A worker must not delegate its transform to another programming language just to inflate the executable-language count.

Required steps:

1. Add the worker source under `languages/<id>/`.
2. Add its runtime/build/package definition to `languages.json`.
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
