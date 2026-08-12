#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SOURCE="${1:-$HOME/Language-Project}"
DEST="${2:-$HOME/storage/downloads/Language-Project-Backups}"

printf '\nLanguage Project — Practical Polyglot Backup Demo\n'
printf 'Source: %s\nDestination: %s\n\n' "$SOURCE" "$DEST"

language-project polyglot status
language-project polyglot protect "$SOURCE" --destination "$DEST" --label "$(basename "$SOURCE")"

printf '\nBackup set created. The .lpack is reversible encoding, not encryption.\n'
