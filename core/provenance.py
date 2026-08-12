from __future__ import annotations
from pathlib import Path
import hashlib,json,sys,platform,os
from .registry import ROOT
from .paths import ACTIVE_STATE_FILE, CALIBRATION_FILE, DATA_ROOT, APP_ROOT

def _sha(path):
    p=Path(path)
    if not p.exists():return None
    h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()

def snapshot():
    state=ACTIVE_STATE_FILE;cal=CALIBRATION_FILE
    try:s=json.loads(state.read_text())
    except Exception:s={}
    return {
        'registry_sha256':_sha(ROOT/'config'/'registries'/'languages.json'),'manifest_sha256':_sha(ROOT/'metadata'/'MANIFEST.json'),
        'active_state_sha256':_sha(state),'calibration_sha256':_sha(cal),
        'active_language_ids':s.get('active',[]),'runtime_versions':s.get('versions',{}),
        'python_executable':sys.executable,'python_version':platform.python_version(),'architecture':platform.machine(),
        'prefix':os.environ.get('PREFIX',''),'termux_version':os.environ.get('TERMUX_VERSION',''),'language_project_home':str(DATA_ROOT),'application_root':str(APP_ROOT)
    }

def fingerprint():
    d=snapshot();raw=json.dumps(d,sort_keys=True,separators=(',',':')).encode();return hashlib.sha256(raw).hexdigest()
