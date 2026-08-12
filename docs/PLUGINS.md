# Optional Plugin Hooks

Language Project contains a local Python plugin loader under `plugins/`. Plugins are disabled by default to keep benchmarks deterministic and to avoid executing unknown extension code automatically.

Enable explicitly:

```bash
export LANGUAGE_PROJECT_PLUGINS=1
```

Only install plugins you trust. A plugin runs with the same permissions as Language Project. The plugin subsystem is intended for local logging, custom exports, notifications, or experimental instrumentation without changing the worker implementations.
