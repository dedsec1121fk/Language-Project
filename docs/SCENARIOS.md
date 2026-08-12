# Scenario Runner

Scenarios are declarative multi-step benchmark workflows stored in `config/scenarios.json`.

List them:

```bash
language-project scenarios
```

Run one:

```bash
language-project scenario presentation --text "Language Project"
```

Bundled scenarios:

- `confidence` — chain + differential audit + consensus.
- `presentation` — chain + topology + parallel race + consensus.
- `resilience` — chaos + differential audit + stress.

Every step keeps its own result file and session ID. The scenario summary records the integrity outcome and references its constituent result artifacts.
