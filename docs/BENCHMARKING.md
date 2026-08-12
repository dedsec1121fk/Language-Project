# Benchmarking Model

Per-stage wall time is measured with `time.perf_counter_ns()` around a single persistent worker request/response. Startup/ping time is measured separately. Optional warm-up requests occur before measured passes.

Repeated measurements expose minimum, P50/median, P90, P95, P99, mean, population standard deviation, maximum, jitter percentage, and approximate throughput where the mode has a meaningful payload-size basis.

## Modes

- `run`: true forward/reverse serial chain across all verified workers.
- `race`: isolated serial per-language trials.
- `parallel-race`: isolated per-language trials while multiple language processes execute concurrently.
- `matrix`: repeated encode/decode across several payload sizes.
- `stress`: repeated full chains over deterministic pseudorandom binary payloads.
- `showcase`: profile-driven composition of chain, parallel race, matrix, and stress runs.

## Interpretation

Language Project is a systems showcase and runtime/IPC experiment, not a scientifically controlled language shootout. The worker implementation, runtime startup/JIT state, garbage collectors, Android scheduler, pipe buffering, CPU frequency scaling, thermal throttling, background apps, memory pressure, and power state can all affect results.

For comparisons, keep the device, active worker set, payload, package versions, warm-up count, mode, and profile stable. Prefer median and P95 over a single minimum sample. The result comparison command deliberately prefers two results from the same benchmark mode.
