#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${1:-$HOME/Language Project/app}"

echo '--- Project tree ---'
language-project tools tree "$ROOT" --depth 2 --max-entries 80

echo '--- TODO/FIXME scan ---'
language-project tools todos "$ROOT" --max-results 20

echo '--- Environment ---'
language-project tools env python git clang

echo '--- Git summary ---'
language-project tools git "$ROOT" || true

echo '--- Safe cleanup preview ---'
language-project tools clean "$ROOT" --older-days 14

echo '--- Backup ---'
language-project tools backup "$ROOT" --destination "$HOME/Language Project/backups" --label language-project
