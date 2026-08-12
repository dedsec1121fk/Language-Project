# Runtime Telemetry

A benchmark can sample process/device state while the language chain is executing.

```bash
language-project run --text "telemetry" --telemetry
```

The sampler uses Linux/Android interfaces available from Termux where readable and records best-effort values such as:

- Language Project process RSS,
- available system memory,
- CPU utilization estimate,
- 1-minute load average,
- maximum readable thermal-zone temperature.

Android devices differ in which thermal files are readable. Missing thermal values are recorded as unavailable rather than fabricated.
