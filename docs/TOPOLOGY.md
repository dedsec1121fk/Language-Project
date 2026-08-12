# Topology Laboratory

The standard Language Project chain is serial because the user's payload must pass through every active language in order. The topology laboratory explores a different orchestration problem: distribute all verified languages across independent reversible lanes and execute those lanes concurrently.

```bash
language-project topology --text "braid" --lanes 4 --iterations 5 --strategy round-robin
```

Strategies:

- `round-robin` — distributes workers evenly by position.
- `contiguous` — preserves contiguous sections of the active order.
- `shuffle` — deterministic shuffled allocation using `--seed`.

Each lane receives the same original payload, runs through its assigned languages forward and backward, and must recover the payload independently. The report includes lane medians, P95 values, throughput, wall time, and a lane-balance ratio.

This mode is intentionally separate from the primary serial chain and does not claim that each byte passed through every worker in the topology run.
