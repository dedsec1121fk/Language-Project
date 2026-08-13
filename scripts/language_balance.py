#!/usr/bin/env python3
"""Conservative GitHub Linguist balance guardrail for Language Project.

This is not a replacement for GitHub Linguist. It estimates detectable source-byte
share from declared language modules plus the Python control plane. It enforces:
  * every tracked GitHub-visible language group >= 0.2%
  * Python <= 25.0%

GitHub's post-push Linguist analysis remains authoritative because its heuristics can
differ slightly from this conservative repository-local estimate.
"""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
REG = json.loads((ROOT / 'config' / 'registries' / 'termux_supported.json').read_text(encoding='utf-8'))['languages']
MIN_TARGET = 0.2
PYTHON_MAX = 25.0

def module_bytes(entry):
    base = ROOT / 'languages' / entry['id']
    ext = '.' + entry['extension'].lower().lstrip('.')
    return sum(
        f.stat().st_size for f in base.rglob('*')
        if f.is_file() and f.suffix.lower() == ext
    )

groups = {}
unrepresented = []
for entry in REG:
    n = module_bytes(entry)
    if entry.get('github_linguist_supported'):
        groups[entry['linguist']] = groups.get(entry['linguist'], 0) + n
    else:
        unrepresented.append((entry['name'], entry['linguist'], n))

# Count Python orchestration outside language modules so the denominator cannot be
# made artificially favourable by ignoring the control plane.
extra_python = 0
for folder in ('core', 'cli', 'scripts', 'tests', 'plugins'):
    p = ROOT / folder
    if p.exists():
        extra_python += sum(f.stat().st_size for f in p.rglob('*.py') if '__pycache__' not in f.parts)
groups['Python'] = groups.get('Python', 0) + extra_python

# Count top-level shell entry points which GitHub Linguist normally includes.
for p in ROOT.glob('*.sh'):
    groups['Shell'] = groups.get('Shell', 0) + p.stat().st_size

total = sum(groups.values())
rows = sorted(((name, size, size / total * 100 if total else 0.0) for name, size in groups.items()), key=lambda r: r[2])
for name, size, pct in rows:
    print(f'{name:<26} {pct:7.3f}%  {size:9d} bytes')

low = [r for r in rows if r[1] and r[2] < MIN_TARGET]
python_share = next((r[2] for r in rows if r[0] == 'Python'), 0.0)
python_ok = python_share <= PYTHON_MAX
print(f'\nTermux language/runtime modules: {len(REG)}')
print(f'GitHub-Linguist-recognized module entries: {sum(bool(x.get("github_linguist_supported")) for x in REG)}')
print(f'Unique tracked GitHub language groups: {len(rows)}')
print(f'Estimated detectable source: {total} bytes')
print(f'Below {MIN_TARGET:.1f}% target: {len(low)}')
print(f'Python estimated share: {python_share:.3f}% (maximum {PYTHON_MAX:.1f}%)')
print(f'Python maximum guardrail: {"PASS" if python_ok else "FAIL"}')
if unrepresented:
    print('\nTermux-supported but not separately representable by current GitHub Linguist:')
    for name, linguist, size in sorted(unrepresented):
        print(f'  - {name} (requested label: {linguist}; module source: {size} bytes)')
if low:
    print('\nBelow target: ' + ', '.join(r[0] for r in low))
if not python_ok:
    print(f'\nPython exceeds the {PYTHON_MAX:.1f}% project guardrail.')
sys.exit(2 if low or not python_ok else 0)
