#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.language_modules import verify_modules,list_modules

def main():
    r=verify_modules()
    if not r['ok']:
        print(json.dumps(r,indent=2,ensure_ascii=False)); return 1
    rows=list_modules()
    assert len(rows)==r['modules']
    assert all(x.get('tool_id') for x in rows)
    print(f"Language module smoke: PASS ({r['modules']} modules)")
    return 0
if __name__=='__main__': raise SystemExit(main())
