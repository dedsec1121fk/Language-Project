# Multi-Order Consensus

Consensus mode runs the complete all-language chain multiple times using different deterministic random language orders.

```bash
language-project consensus --text "same result" --replicas 3 --seed 1121
```

Every replica must independently recover the original bytes, and all recovered SHA-256 values must agree with the original payload hash. This validates that reversibility is preserved regardless of the chosen ordering of compatible stages.
