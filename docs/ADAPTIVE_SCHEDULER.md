# Adaptive Scheduler

The calibration subsystem benchmarks the verified workers on the current device and stores `state/calibration.json`.

```bash
language-project calibrate --sizes 64 4096 65536 --iterations 4 --warmups 2
```

It derives four orderings:

- `adaptive-balanced` — weighted latency, jitter, startup cost, and throughput.
- `adaptive-latency` — favors low per-request latency and startup cost.
- `adaptive-throughput` — favors sustained payload throughput.
- `adaptive-stable` — favors low timing variability while still considering speed.

Example:

```bash
language-project run --text "adaptive" --order adaptive-balanced
```

Calibration data is device-specific. A calibration generated on one phone should not be assumed to represent another phone or a different runtime/package set.
