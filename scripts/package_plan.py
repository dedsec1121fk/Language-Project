#!/usr/bin/env python3
from pathlib import Path
import json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.registry import load_registry

def installed(pkg):
    if not shutil.which('dpkg'):return None
    return subprocess.run(['dpkg','-s',pkg],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

def main():
    by={}
    for l in load_registry():
        for p in l.get('packages',[]):by.setdefault(p,[]).append(l['name'])
    print('\nLanguage Project — Termux package plan\n')
    for pkg,names in sorted(by.items()):
        st=installed(pkg);mark='✓' if st is True else ('·' if st is False else '?')
        print(f"{mark} {pkg:<22} {', '.join(names)}")
    print(f"\nUnique packages: {len(by)} | executable worker candidates: {len(load_registry())}")
    print('✓ installed  · not installed  ? dpkg unavailable')
    return 0
if __name__=='__main__':raise SystemExit(main())
