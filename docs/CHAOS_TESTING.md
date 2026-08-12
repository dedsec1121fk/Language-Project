# Chaos And Resilience Testing

Chaos mode deliberately restarts verified language workers during a complete forward/reverse chain.

```bash
language-project chaos --text "survive restarts" --cycles 12 --restart-rate 0.20 --seed 1121
```

The payload itself is not intentionally corrupted. The injected fault is process lifecycle churn: workers are closed and restarted before selected encode/decode stages. The run succeeds only if every cycle still returns the exact original bytes.

The mode records restart events, cycle durations, integrity, aggregate statistics, and optional CPU/RAM/thermal telemetry. The deterministic seed makes the restart pattern reproducible.
