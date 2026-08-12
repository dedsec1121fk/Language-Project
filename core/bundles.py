from __future__ import annotations
from pathlib import Path
import zipfile,json,hashlib,datetime
from .registry import ROOT

def _sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def create_bundle(result_paths=None,name=None,include_state=True):
    results=ROOT/'results';bundles=ROOT/'bundles';bundles.mkdir(exist_ok=True)
    if result_paths:
        files=[Path(x).expanduser() for x in result_paths]
    else:
        files=sorted(results.glob('*'),key=lambda p:p.stat().st_mtime,reverse=True)[:12]
    files=[p for p in files if p.exists() and p.is_file()]
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');out=bundles/(name or f'language-project-session-{stamp}.zip')
    manifest={'project':'Language Project','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[]}
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            arc='results/'+p.name;z.write(p,arc);manifest['files'].append({'path':arc,'sha256':_sha(p),'bytes':p.stat().st_size})
        for rel in ['languages.json','state/active.json','state/calibration.json','config/benchmark_profiles.json','config/scenarios.json']:
            p=ROOT/rel
            if p.exists() and (include_state or not rel.startswith('state/')):
                z.write(p,rel);manifest['files'].append({'path':rel,'sha256':_sha(p),'bytes':p.stat().st_size})
        z.writestr('BUNDLE-MANIFEST.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    return out
