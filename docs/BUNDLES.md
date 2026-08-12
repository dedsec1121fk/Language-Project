# Portable Result Bundles

Create a ZIP containing recent result files plus relevant execution metadata:

```bash
language-project bundle
```

Or bundle specific result paths:

```bash
language-project bundle results/run-a.json results/run-a.csv --name demo.zip
```

The bundle contains `BUNDLE-MANIFEST.json` with SHA-256 hashes and byte sizes for every included file. When available it also includes registry, active-state, calibration, profile, and scenario configuration files so a benchmark can be reviewed with its environment metadata.
