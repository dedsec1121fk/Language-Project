# Advanced Benchmark Modes

Language Project deliberately separates correctness, chained execution, isolated performance, contention, size scaling, topology, resilience, and endurance so one number is never presented as every kind of benchmark.

## Serial chain

`language-project run` passes one payload through every verified worker and then decodes through the same workers in reverse order. This remains the main showcase mode because every active language touches the payload.

## Serial and parallel races

`language-project race` benchmarks each worker independently. `language-project parallel-race` benchmarks different workers concurrently to expose contention behavior.

## Size matrix

`language-project matrix` repeats the same reversible operation over multiple payload sizes so fixed process/IPC overhead can be separated from larger-payload throughput.

## Stress mode

`language-project stress` runs repeated complete forward/reverse chains over deterministic pseudorandom binary payloads. Every cycle performs integrity verification.

## Differential audit

`language-project differential` gives every worker a deterministic corpus, encodes each vector twice, checks deterministic output, checks inverse recovery, and records fingerprints/timing.

See `docs/DIFFERENTIAL_AUDIT.md`.

## Chaos mode

`language-project chaos` deliberately restarts worker subprocesses during the chain and verifies that the exact original bytes still return.

See `docs/CHAOS_TESTING.md`.

## Braided topology

`language-project topology` distributes the active worker set across concurrent reversible lanes and measures lane imbalance and wall-clock behavior.

See `docs/TOPOLOGY.md`.

## Multi-order consensus

`language-project consensus` executes multiple complete all-language chains with different deterministic random orders. Every replica must recover the same original SHA-256.

See `docs/CONSENSUS.md`.

## Checkpoint mode

`language-project checkpoint` persists the chain after each successful stage. `language-project resume` continues from the stored phase and worker index.

See `docs/CHECKPOINTS.md`.

## Adaptive scheduler

`language-project calibrate` builds device-specific orders from latency, jitter, startup cost, and throughput.

See `docs/ADAPTIVE_SCHEDULER.md`.

## Scenarios and showcase

`language-project showcase` runs the built-in showcase profile. `language-project scenario <name>` executes declarative multi-step workflows from `config/scenarios.json`.

## Smoke validation

After runtime setup:

```bash
python scripts/smoke_benchmark.py
python scripts/advanced_smoke.py
```

The advanced smoke suite exercises serial execution, telemetry, differential validation, topology, consensus, chaos restarts, and checkpoint/resume behavior.
