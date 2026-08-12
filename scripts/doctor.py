#!/usr/bin/env python3
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.registry import load_registry,expand,executable_exists
from core.engine import load_state,active_languages,start_one
from core.analytics import device_snapshot
from core.store import stats as database_stats
from core.scenarios import load_scenarios
from core.provenance import fingerprint

def check(name,ok,detail=''):
    print(f"{'OK' if ok else 'FAIL':<5} {name:<34} {detail}")
    return bool(ok)
def main():
    print('\n'+'='*84+'\nLANGUAGE PROJECT — TERMUX DOCTOR\n'+'='*84)
    checks=[];prefix=os.environ.get('PREFIX','');is_termux=bool(shutil.which('pkg')) and ('com.termux' in prefix or prefix.endswith('/usr'))
    checks.append(check('Termux pkg command',bool(shutil.which('pkg')),shutil.which('pkg') or 'missing'))
    checks.append(check('Python runtime',sys.version_info>=(3,9),sys.version.split()[0]))
    checks.append(check('Project location is writable',os.access(ROOT,os.W_OK),str(ROOT)))
    checks.append(check('Project is not shared storage','/storage/emulated/' not in str(ROOT) and '/sdcard/' not in str(ROOT),'compiled binaries should live under $HOME'))
    for d in ('build','state','results','bundles'):
        p=ROOT/d;p.mkdir(exist_ok=True)
        try:
            t=p/'.doctor-write';t.write_text('ok');t.unlink();ok=True
        except Exception:ok=False
        checks.append(check(f'{d}/ writable',ok,str(p)))
    st=load_state();reg=load_registry();active=active_languages()
    try:
        sc=load_scenarios().get('scenarios',{});checks.append(check('Scenario configuration',bool(sc),f'{len(sc)} scenarios'))
    except Exception as e:checks.append(check('Scenario configuration',False,str(e)))
    try:
        db=database_stats();checks.append(check('SQLite performance database',True,f"{db.get('sessions',0)} sessions"))
    except Exception as e:checks.append(check('SQLite performance database',False,str(e)))
    checks.append(check('Environment fingerprint',len(fingerprint())==64,fingerprint()[:16]+'...'))
    checks.append(check('Executable registry readable',bool(reg),f'{len(reg)} workers'))
    checks.append(check('Verified runtime state present',bool(st),f"{len(st.get('active',[]))} active" if st else 'run setup'))
    if st:
        missing=[x['id'] for x in active if not executable_exists(x['run'])]
        checks.append(check('Verified runtimes still resolvable',not missing,', '.join(missing) if missing else f'{len(active)} available'))
    manifest=ROOT/'MANIFEST.json'
    if manifest.exists():
        r=subprocess.run([sys.executable,str(ROOT/'scripts'/'verify_manifest.py')],capture_output=True,text=True)
        checks.append(check('Integrity manifest',r.returncode==0,(r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else ''))
    else:checks.append(check('Integrity manifest',False,'MANIFEST.json missing'))
    if active:
        sample=active[0];w=None
        try:
            w=start_one(sample);enc,_=w.request('E','0011223344556677');dec,_=w.request('D',enc);ok=dec=='0011223344556677';detail=sample['name']
        except Exception as e:ok=False;detail=str(e)
        finally:
            if w:w.close()
        checks.append(check('Live worker round-trip',ok,detail))
    snap=device_snapshot();print('\nDevice snapshot:');print(json.dumps(snap,indent=2))
    passed=sum(checks);print('\n'+'-'*84);print(f'Doctor summary: {passed}/{len(checks)} checks passed')
    if not all(checks):print('Recommended repair: language-project setup --install')
    print('-'*84);return 0 if all(checks) else 1
if __name__=='__main__':raise SystemExit(main())
