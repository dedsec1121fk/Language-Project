# Performance Regression Gate

Language Project can turn historical measurements into a simple CI-style performance gate.

```bash
language-project regression --mode chain --threshold 15
```

The command compares the two newest database sessions of the selected mode that have a comparable aggregate duration. It fails when the newest run exceeds the previous run by more than the configured percentage or when integrity failed.

This is intentionally a lightweight gate. Mobile devices are noisy benchmark environments, so use repeated runs and a realistic threshold rather than treating one sample as a laboratory-grade performance result.
