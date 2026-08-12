# Language Race Modes

The normal Language Project chain intentionally transforms one payload through worker A, then B, then C, and reverses the exact order. Race modes answer a different question: how quickly can each verified worker perform the same reversible operation on the same original payload?

## Serial race

`language-project race` benchmarks one worker after another. It is the cleaner view when you want less cross-runtime contention.

```bash
language-project race --text "Language Project" --iterations 10 --warmups 2
```

## Parallel race

`language-project parallel-race` starts all verified workers once and schedules per-language trials concurrently. By default, concurrency adapts to the device CPU count; `--parallel N` overrides it.

```bash
language-project parallel-race --text "Language Project" --iterations 10 --parallel 8
```

Parallel Race records median, P95, jitter, throughput, startup timing, integrity, and richer distribution statistics. It is intentionally a device-pressure benchmark, so it should not be interpreted the same way as the serial race.
