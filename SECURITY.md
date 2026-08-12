# Security

Language Project treats user input as opaque bytes and never evaluates it as source code. Worker communication uses a constrained line protocol containing hexadecimal payloads.

Do not add workers that execute user-provided text, download and run unverified binaries, require root, or silently invoke remote code-execution services. Runtime packages should come from Termux package repositories or an explicitly documented language ecosystem.

## Local Result Data

Language Project is local-first, but benchmark artifacts can contain information derived from the supplied payload. Normal chain JSON may contain the final transformed hexadecimal value, and resumable checkpoint files contain the current and original payload as hexadecimal so execution can continue after interruption. Hexadecimal is an encoding, not encryption.

Treat `results/`, `state/checkpoints/`, `state/history.sqlite3`, and manually created bundles as potentially sensitive if the input was sensitive. Do not publish those files without reviewing them first.

## Plugins

Plugins are disabled by default. When `LANGUAGE_PROJECT_PLUGINS=1` is enabled, local `.py` files in `plugins/` can execute with the same account permissions as Language Project. Only enable plugins you trust.

## Chaos Mode

Chaos mode restarts Language Project's own worker subprocesses. It does not intentionally corrupt user files, modify Android system settings, or kill unrelated processes.
