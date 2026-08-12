#!/data/data/com.termux/files/usr/bin/bash
set -e
TARGET="${1:-$HOME/Language Project/app}"
echo "Available native language tools:"
language-project langtools list
echo
echo "Recommended tools for project analysis:"
language-project langtools recommend project files code search
echo
echo "Building an all-available-language workspace report for: $TARGET"
language-project langtools workspace-report "$TARGET" --output "$HOME/storage/downloads/language-project-workspace-report.json"
echo "Report: $HOME/storage/downloads/language-project-workspace-report.json"
