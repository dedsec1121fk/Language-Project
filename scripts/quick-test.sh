#!/data/data/com.termux/files/usr/bin/bash
set -e
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
python cli/Language.py catalog stats
python cli/Language.py setup
python cli/Language.py run --text "Language Project test ✓" --warmups 1
python scripts/toolbox_smoke.py
python scripts/practical_smoke.py
python scripts/workbench_smoke.py
python scripts/human/verify_language_vault.py
python scripts/human_language_smoke.py
python scripts/langtools_smoke.py
python scripts/polyglot_smoke.py
python scripts/polyglot_practical_smoke.py
python cli/Language.py verify
