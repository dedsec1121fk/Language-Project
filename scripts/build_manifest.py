#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
ignore={'metadata/MANIFEST.json'};skip_roots={'.git','__pycache__'};rows=[]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(ROOT)
 if rel.as_posix() in ignore or any(part in skip_roots for part in rel.parts):continue
 b=p.read_bytes();rows.append({'path':rel.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(ROOT/'metadata'/'MANIFEST.json').write_text(json.dumps({'schema':2,'project':'Language Project','file_count':len(rows),'files':rows},indent=2)+'\n')
print('Manifest files:',len(rows))
