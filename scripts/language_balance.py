#!/usr/bin/env python3
"""Conservative GitHub Linguist balance guardrail for Language Project.

This is not a replacement for GitHub Linguist. It estimates source-byte share from
our declared per-language modules, honours the registry's current Linguist support
flag, and intentionally excludes Termux languages that GitHub cannot represent as
an independent language. GitHub's own post-push analysis remains authoritative.
"""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
REG = json.loads((ROOT / 'config' / 'registries' / 'termux_supported.json').read_text(encoding='utf-8'))['languages']
TARGET = 0.2

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

# Count Python orchestration outside the language modules. This prevents the audit
# from making the denominator artificially small just because Python is the control plane.
extra_python = 0
for folder in ('core', 'cli', 'scripts', 'tests', 'plugins'):
    p = ROOT / folder
    if p.exists():
        extra_python += sum(f.stat().st_size for f in p.rglob('*.py') if '__pycache__' not in f.parts)
groups['Python'] = groups.get('Python', 0) + extra_python

total = sum(groups.values())
rows = sorted(((name, size, size / total * 100 if total else 0.0) for name, size in groups.items()), key=lambda r: r[2])
for name, size, pct in rows:
    print(f'{name:<26} {pct:7.3f}%  {size:9d} bytes')

low = [r for r in rows if r[1] and r[2] < TARGET]
print(f'\nTermux language/runtime modules: {len(REG)}')
print(f'GitHub-Linguist-recognized module entries: {sum(bool(x.get("github_linguist_supported")) for x in REG)}')
print(f'Unique tracked GitHub language groups: {len(rows)}')
print(f'Estimated detectable source: {total} bytes')
print(f'Below {TARGET:.1f}% target: {len(low)}')
if unrepresented:
    print('\nTermux-supported but not separately representable by current GitHub Linguist:')
    for name, linguist, size in sorted(unrepresented):
        print(f'  - {name} (requested label: {linguist}; module source: {size} bytes)')
if low:
    print('\nBelow target: ' + ', '.join(r[0] for r in low))
    sys.exit(2)
