# Differential Worker Audit

Differential audit validates each active worker against a deterministic corpus rather than only one payload.

```bash
language-project differential --vectors 32 --max-size 4096 --seed 1121
```

For each worker and vector, the engine:

1. encodes the same bytes twice,
2. verifies deterministic output,
3. verifies output shape remains valid hexadecimal data of the same length,
4. decodes the transformed value,
5. verifies exact byte recovery,
6. records timing and a transform-output fingerprint.

The audit is especially useful after adding or modifying a language implementation.
