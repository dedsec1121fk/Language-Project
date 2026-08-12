from __future__ import annotations
from pathlib import Path
import zipfile,json,hashlib,datetime
from .registry import ROOT
from .paths import RESULTS_DIR, BUNDLES_DIR, ACTIVE_STATE_FILE, CALIBRATION_FILE

def _sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def create_bundle(result_paths=None,name=None,include_state=True):
    results=RESULTS_DIR;bundles=BUNDLES_DIR;bundles.mkdir(parents=True,exist_ok=True)
    if result_paths:
        files=[Path(x).expanduser() for x in result_paths]
    else:
        files=sorted(results.glob('*'),key=lambda p:p.stat().st_mtime,reverse=True)[:12]
    files=[p for p in files if p.exists() and p.is_file()]
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');out=bundles/(name or f'language-project-session-{stamp}.zip')
    manifest={'project':'Language Project','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[]}
    metadata_files=[
        (ROOT/'config'/'registries'/'languages.json','config/registries/languages.json'),
        (ROOT/'config'/'benchmark_profiles.json','config/benchmark_profiles.json'),
        (ROOT/'config'/'scenarios.json','config/scenarios.json'),
    ]
    if include_state:
        metadata_files += [(ACTIVE_STATE_FILE,'state/active.json'),(CALIBRATION_FILE,'state/calibration.json')]
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            arc='results/'+p.name;z.write(p,arc);manifest['files'].append({'path':arc,'sha256':_sha(p),'bytes':p.stat().st_size})
        for p,arc in metadata_files:
            if p.exists():
                z.write(p,arc);manifest['files'].append({'path':arc,'sha256':_sha(p),'bytes':p.stat().st_size})
        z.writestr('BUNDLE-MANIFEST.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    return out
