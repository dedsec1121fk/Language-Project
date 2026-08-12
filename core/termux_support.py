from __future__ import annotations
from pathlib import Path
import json, shutil, subprocess
from .paths import APP_ROOT, DATA_ROOT
REGISTRY=APP_ROOT/'config'/'registries'/'termux_supported.json'

def load_supported(): return json.loads(REGISTRY.read_text(encoding='utf-8'))['languages']

def status():
    rows=[]
    for x in load_supported():
        cmd=x.get('command','')
        resolved=cmd.replace('{data}',str(DATA_ROOT)) if isinstance(cmd,str) else ''
        if resolved and '/' in resolved:
            q=Path(resolved)
            available=q.is_file() and q.stat().st_mode & 0o111 != 0
        else:
            available=bool(shutil.which(resolved)) if resolved else False
        rows.append({**x,'runtime_available':available})
    return {'registered':len(rows),'available':sum(r['runtime_available'] for r in rows),'rows':rows}

def package_plan():
    pkgs=[]
    for x in load_supported():
        for p in x.get('packages',[]):
            if p not in pkgs: pkgs.append(p)
    return pkgs

def install(ids=None):
    wanted=load_supported()
    if ids:
        s={i.casefold() for i in ids}; wanted=[x for x in wanted if x['id'].casefold() in s or x['name'].casefold() in s]
    if not wanted: raise ValueError('no matching supported languages')
    pkgs=[]
    for x in wanted:
        for p in x.get('packages',[]):
            if p not in pkgs: pkgs.append(p)
    log=DATA_ROOT/'logs'/'all-languages-install.log'; log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('a',encoding='utf-8') as f:
        f.write('Installing packages: '+' '.join(pkgs)+'\n')
    # Install in small groups so one unavailable package does not abort the entire coverage pass.
    results=[]
    for p in pkgs:
        r=subprocess.run(['pkg','install','-y',p],text=True,capture_output=True)
        results.append({'package':p,'ok':r.returncode==0,'returncode':r.returncode,'stderr':r.stderr[-1000:]})
    return {'packages':len(pkgs),'ok':sum(x['ok'] for x in results),'failed':[x for x in results if not x['ok']],'log':str(log)}
