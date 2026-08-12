#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
python Language.py catalog stats
python Language.py setup
python Language.py run --text "Language Project test ✓" --warmups 1
python Language.py verify
