#!/usr/bin/env python3
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.registry import load_registry,expand,executable_exists
from core.paths import DATA_ROOT, BUILD_DIR, STATE_DIR, RESULTS_DIR, BUNDLES_DIR, BACKUPS_DIR, REPORTS_DIR, LOGS_DIR, CACHE_DIR, TEMP_DIR, ensure_data_tree
from core.engine import load_state,active_languages,start_one
from core.analytics import device_snapshot
from core.store import stats as database_stats
from core.scenarios import load_scenarios
from core.provenance import fingerprint
from core.toolbox import codec,identify_language
from core.practical import environment_report,tree_view
from core.polyglot_ops import status as polyglot_status,FORMAT as POLYGLOT_FORMAT
from core.langtools import status as langtools_status,selftest as langtools_selftest

def check(name,ok,detail=''):
    print(f"{'OK' if ok else 'FAIL':<5} {name:<34} {detail}")
    return bool(ok)
def main():
    print('\n'+'='*84+'\nLANGUAGE PROJECT — TERMUX DOCTOR\n'+'='*84)
    checks=[];prefix=os.environ.get('PREFIX','');is_termux=bool(shutil.which('pkg')) and ('com.termux' in prefix or prefix.endswith('/usr'))
    checks.append(check('Termux pkg command',bool(shutil.which('pkg')),shutil.which('pkg') or 'missing'))
    checks.append(check('Python runtime',sys.version_info>=(3,9),sys.version.split()[0]))
    ensure_data_tree(); checks.append(check('Application location is readable',os.access(ROOT,os.R_OK),str(ROOT))); checks.append(check('Language Project home is writable',os.access(DATA_ROOT,os.W_OK),str(DATA_ROOT)))
    checks.append(check('Runtime home is not shared storage','/storage/emulated/' not in str(DATA_ROOT) and '/sdcard/' not in str(DATA_ROOT),'runtime data should live under $HOME/Language Project'))
    runtime_dirs={'build':BUILD_DIR,'state':STATE_DIR,'results':RESULTS_DIR,'bundles':BUNDLES_DIR,'backups':BACKUPS_DIR,'reports':REPORTS_DIR,'logs':LOGS_DIR,'cache':CACHE_DIR,'tmp':TEMP_DIR}
    for label,p in runtime_dirs.items():
        p.mkdir(parents=True,exist_ok=True)
        try:
            t=p/'.doctor-write';t.write_text('ok');t.unlink();ok=True
        except Exception:ok=False
        checks.append(check(f'{label}/ writable',ok,str(p)))
    st=load_state();reg=load_registry();active=active_languages()
    try:
        sc=load_scenarios().get('scenarios',{});checks.append(check('Scenario configuration',bool(sc),f'{len(sc)} scenarios'))
    except Exception as e:checks.append(check('Scenario configuration',False,str(e)))
    try:
        db=database_stats();checks.append(check('SQLite performance database',True,f"{db.get('sessions',0)} sessions"))
    except Exception as e:checks.append(check('SQLite performance database',False,str(e)))
    checks.append(check('Environment fingerprint',len(fingerprint())==64,fingerprint()[:16]+'...'))
    try:
        raw=b'utility-plane';ok=codec(codec(raw,'base64'),'base64',True)==raw and (identify_language(ROOT/'cli'/'Language.py').get('best') or {}).get('name')=='Python'
        checks.append(check('Useful toolbox core',ok,'codec + catalog language detector'))
    except Exception as e:checks.append(check('Useful toolbox core',False,str(e)))
    try:
        env=environment_report(['python']);ok=bool(env['commands'][0]['path']) and bool(tree_view(ROOT,depth=1,max_entries=20))
        checks.append(check('Practical utility plane',ok,'environment + tree + dry-run utilities'))
    except Exception as e:checks.append(check('Practical utility plane',False,str(e)))
    try:
        ps=polyglot_status();ok=POLYGLOT_FORMAT=='language-project-polyglot' and len(ps.get('operations',{}))>=16
        checks.append(check('Practical polyglot control plane',ok,f"{ps.get('verified_languages',0)} active / {len(ps.get('operations',{}))} workflows"))
    except Exception as e:checks.append(check('Practical polyglot control plane',False,str(e)))
    try:
        nts=langtools_status(); expected=len(active) if active else 0
        reg_ok=nts.get('registered')==len(reg)
        checks.append(check('Native tool registry coverage',reg_ok,f"{nts.get('registered',0)}/{len(reg)} one-per-language tools"))
        if st:
            coverage=nts.get('available',0)==expected
            checks.append(check('Verified language/tool parity',coverage,f"{nts.get('available',0)} tools / {expected} active languages"))
            if nts.get('available',0):
                tr=langtools_selftest(); checks.append(check('Native language tool smoke',tr.get('ok',False),f"{tr.get('passed',0)}/{tr.get('tested',0)}"))
    except Exception as e:checks.append(check('Native multi-language tools',False,str(e)))
    checks.append(check('Executable registry readable',bool(reg),f'{len(reg)} workers'))
    try:
        cr=subprocess.run([sys.executable,str(ROOT/'scripts'/'termux_coverage_audit.py')],capture_output=True,text=True,timeout=30)
        detail=(cr.stdout.strip().splitlines()[0] if cr.stdout.strip() else cr.stderr.strip()[:120])
        checks.append(check('Full Termux language coverage',cr.returncode==0,detail))
    except Exception as e: checks.append(check('Full Termux language coverage',False,str(e)))
    try:
        br=subprocess.run([sys.executable,str(ROOT/'scripts'/'language_balance.py')],capture_output=True,text=True,timeout=30)
        detail=next((line.strip() for line in br.stdout.splitlines() if line.startswith('Below 0.2%')), 'balance audit')
        checks.append(check('GitHub language >=0.2% guardrail',br.returncode==0,detail))
    except Exception as e: checks.append(check('GitHub language >=0.2% guardrail',False,str(e)))
    checks.append(check('Verified runtime state present',bool(st),f"{len(st.get('active',[]))} active" if st else 'run setup'))
    if st:
        missing=[x['id'] for x in active if not executable_exists(x['run'])]
        checks.append(check('Verified runtimes still resolvable',not missing,', '.join(missing) if missing else f'{len(active)} available'))
    manifest=ROOT/'metadata'/'MANIFEST.json'
    if manifest.exists():
        r=subprocess.run([sys.executable,str(ROOT/'scripts'/'verify_manifest.py')],capture_output=True,text=True)
        checks.append(check('Integrity manifest',r.returncode==0,(r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else ''))
    else:checks.append(check('Integrity manifest',False,'metadata/MANIFEST.json missing'))
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
