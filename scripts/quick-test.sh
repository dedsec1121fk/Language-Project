#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
python Language.py catalog stats
python Language.py setup
python Language.py run --text "Language Project test ✓" --warmups 1
python scripts/toolbox_smoke.py
python scripts/practical_smoke.py
python scripts/langtools_smoke.py
python scripts/polyglot_smoke.py
python scripts/polyglot_practical_smoke.py
python Language.py verify
