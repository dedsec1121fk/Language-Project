#!/data/data/com.termux/files/usr/bin/bash
set -u
rm -f "$PREFIX/bin/language-project" "$PREFIX/bin/language" "$PREFIX/bin/langtool"
if [ "${1:-}" != "--keep-data" ]; then rm -rf "$HOME/Language-Project";fi
echo "Language Project removed. Use --keep-data to preserve the project directory on future uninstalls."
