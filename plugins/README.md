# Plugins

Language Project has an optional local Python hook system. Plugins are **disabled by default** so benchmark measurements are not changed by arbitrary hook work.

Enable explicitly:

```bash
export LANGUAGE_PROJECT_PLUGINS=1
```

A plugin is a `.py` file in this directory. Supported hook names can be added over time. The built-in engine currently emits session-level events only where documented. Plugins execute with the same permissions as Language Project, so only install plugins you trust.
