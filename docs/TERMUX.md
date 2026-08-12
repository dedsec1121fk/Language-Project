# Termux Runtime Model

Language Project is designed to execute from Termux private storage. Android shared storage is appropriate for transferring the ZIP, but compiled programs should not be built/run there. `install.sh` therefore copies the project to `$HOME/Language Project/app` before runtime installation and compilation.

For every executable registry entry, setup follows this sequence:

1. Install the declared Termux package(s) when `--install` is used.
2. Confirm the compiler/interpreter executable exists.
3. Build optimized artifacts when the language is compiled.
4. Start the worker.
5. Require `PING -> PONG` within a watchdog timeout.
6. Encode and decode several binary/Unicode test vectors.
7. Require exact hex length and format.
8. Require byte-perfect round-trip recovery.
9. Record runtime version, startup/test timing, success or failure in `$HOME/Language Project/state/active.json`.

A failed package, compiler, startup, or self-test is quarantined from the active chain instead of being counted as supported.

## Native Practical Tool Pass

After worker verification, setup performs a second pass over `config/registries/polytools.json`. There is exactly one practical native utility for every executable worker candidate. Only tools whose corresponding worker is active are considered; compiled utilities are built under `$HOME/Language Project/build/polytools/`, then each candidate is run against deterministic fixture data. Successful utilities are recorded in `$HOME/Language Project/state/polytools.json`.

This gives the project two independent device-specific claims:

- `$HOME/Language Project/state/active.json`: languages proven usable for the benchmark/polyglot protocol on this device.
- `$HOME/Language Project/state/polytools.json`: useful native utilities proven to build/run on this device.

The installer also creates a short `langtool` command, equivalent to `language-project langtools`.
