#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.termux_support import status,package_plan,install
ap=argparse.ArgumentParser(description='Language Project Termux language coverage manager')
sp=ap.add_subparsers(dest='cmd')
sp.add_parser('list');sp.add_parser('status');sp.add_parser('packages')
i=sp.add_parser('install');i.add_argument('ids',nargs='+')
sp.add_parser('install-all')
a=ap.parse_args()
if a.cmd in (None,'list'):
    st=status()
    for x in st['rows']:
        print(f"{'✓' if x['runtime_available'] else '·'} {x['id']:<16} {x['name']:<24} tier={x['tier']:<13} pkg={','.join(x['packages'])}")
    print(f"\nRegistered: {st['registered']}  Available now: {st['available']}")
elif a.cmd=='status': print(json.dumps(status(),indent=2,ensure_ascii=False))
elif a.cmd=='packages': print('\n'.join(package_plan()))
elif a.cmd=='install': print(json.dumps(install(a.ids),indent=2))
elif a.cmd=='install-all': print(json.dumps(install(),indent=2))
