#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
BASE="$HOME/Language Project"
PREFIX_BIN="${PREFIX:-/data/data/com.termux/files/usr}/bin"

rm -f "$PREFIX_BIN/language-project" "$PREFIX_BIN/language" "$PREFIX_BIN/langtool" "$PREFIX_BIN/language-project-home"

if [ "${1:-}" = "--keep-data" ]; then
  rm -rf "$BASE/app" "$BASE/build" "$BASE/cache" "$BASE/tmp"
  echo "Language Project application removed. User data kept in: $BASE"
else
  rm -rf "$BASE"
  echo "Language Project and its data were removed."
fi
