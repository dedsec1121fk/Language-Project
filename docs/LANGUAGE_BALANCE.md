# GitHub Language Balance

Language Project intentionally contains a Python control plane, so Python can remain the largest language without preventing the rest of the repository from being visible. The project target is not equal percentages; it is a **minimum 0.2% estimated source share for every distinct GitHub Linguist language group that the current Linguist database can actually represent**.

Run:

```bash
language-project supported balance
```

The audit:

1. Counts language-module source using each module's declared source extension.
2. Groups modules by their GitHub Linguist language family.
3. Includes Python source from the control plane in the denominator.
4. Excludes Termux languages that current GitHub Linguist cannot represent independently instead of mislabeling them.
5. Fails with a non-zero exit code if a detectable group falls below 0.2%.

The shipped release passes the local conservative threshold. GitHub's post-push Linguist result is still the final source of truth, because GitHub applies its own generated/vendored/documentation/detection rules.

The `.gitattributes` file only resolves known ambiguities and suppresses known misclassification cases. It does **not** relabel Python as another language merely to manipulate the percentage bar.
