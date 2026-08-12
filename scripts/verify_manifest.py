#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'MANIFEST.json'
if not P.exists():print('MANIFEST.json missing');raise SystemExit(2)
m=json.loads(P.read_text());bad=[]
for x in m['files']:
 p=ROOT/x['path']
 if not p.exists():bad.append((x['path'],'missing'));continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=x['sha256']:bad.append((x['path'],'hash mismatch'))
print(f"Verified {len(m['files'])-len(bad)}/{len(m['files'])} manifest files")
for p,e in bad:print('!',p,e)
raise SystemExit(1 if bad else 0)
