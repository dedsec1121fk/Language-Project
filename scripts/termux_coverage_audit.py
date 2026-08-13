#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
REGP=ROOT/'config'/'registries'/'termux_supported.json'
errors=[]; warnings=[]
try: obj=json.loads(REGP.read_text(encoding='utf-8'))
except Exception as e:
 print('ERROR: registry unreadable:',e);sys.exit(2)
rows=obj.get('languages',[])
ids=[x.get('id') for x in rows]
# Verify the packaged package snapshot and registry stay synchronized.
snapshot_path=ROOT/'metadata'/'termux-supported-packages.json'
try:
    snap=json.loads(snapshot_path.read_text(encoding='utf-8'))
    registry_packages=sorted({p for x in rows for p in x.get('packages',[])})
    if snap.get('language_family_count') != len(rows): errors.append('package snapshot language count mismatch')
    if sorted(snap.get('packages',[])) != registry_packages: errors.append('package snapshot package list mismatch')
except Exception as e:
    errors.append(f'package snapshot invalid: {e}')
if obj.get('count') != len(rows): errors.append(f"registry count={obj.get('count')} but entries={len(rows)}")
if len(ids)!=len(set(ids)): errors.append('duplicate language ids')
for x in rows:
    lid=x.get('id','')
    d=ROOT/'languages'/lid
    for rel in ('README.md','metadata.json','tools','examples','tests/module.json'):
        if not (d/rel).exists(): errors.append(f'{lid}: missing {rel}')
    guide=list((d/'tools').glob('termux-field-guide.*'))
    if not guide: errors.append(f'{lid}: missing Termux field guide source')
    if not x.get('packages'): errors.append(f'{lid}: no Termux package')
    if not x.get('official_package_verified'): errors.append(f'{lid}: official package not verified')
    srcs=[p for p in d.rglob('*') if p.is_file() and p.suffix.lower()==('.'+x.get('extension','').lower().lstrip('.'))]
    if not srcs: errors.append(f'{lid}: no source matching .{x.get("extension","")}')
    elif sum(p.stat().st_size for p in srcs) < 12000: warnings.append(f'{lid}: language source footprint below 12 KiB balance floor')
worker=sum(x.get('tier')=='worker' for x in rows)
native=sum(x.get('tier')=='native-module' for x in rows)
known=sum(bool(x.get('github_linguist_supported')) for x in rows)
unknown=[x['name'] for x in rows if not x.get('github_linguist_supported')]
print(f'Registered Termux language/runtime families: {len(rows)}')
print(f'Worker tier: {worker}')
print(f'Native-module tier: {native}')
print(f'GitHub Linguist-recognized entries: {known}')
print(f'Not separately recognized by GitHub Linguist: {len(unknown)}')
if unknown: print('  '+', '.join(unknown))
print(f'Errors: {len(errors)}  Warnings: {len(warnings)}')
for e in errors: print('ERROR:',e)
for w in warnings: print('WARNING:',w)
sys.exit(2 if errors else 0)
