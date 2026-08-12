#!/usr/bin/env python3
from pathlib import Path
import argparse,sys,json,subprocess
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from core.engine import run_chain,print_report,active_languages,benchmark_suite,race_workers,load_state,parallel_race,matrix_benchmark,stress_test,showcase
from core.registry import load_registry
from core.catalog import load_catalog,search_catalog,catalog_stats
from core.analytics import device_snapshot
from core.profiles import get_profile,print_profiles
from core.history import print_history,compare_results
from core.adaptive import calibrate,print_calibration
from core.advanced import differential_audit,chaos_test,checkpoint_chain,resume_checkpoint,checkpoint_list
from core.topology import topology_benchmark,consensus_test
from core.scenarios import print_scenarios,run_scenario
from core.store import stats as database_stats,leaderboard as database_leaderboard,recent as database_recent,rebuild as database_rebuild
from core.bundles import create_bundle
from core.dashboard import dashboard
from core.planner import execution_plan,print_plan
from core.regression import check as regression_check,print_check as print_regression

ORDERS=['registry','fastest','random','adaptive-balanced','adaptive-latency','adaptive-throughput','adaptive-stable']

def banner():print('\n'+'='*92+'\nLANGUAGE PROJECT — TERMUX POLYGLOT EXECUTION + BENCHMARK ORCHESTRATION PLATFORM\n'+'='*92)
def ensure():
    if not active_languages():
        print('No verified runtime state found. Running local verification...')
        subprocess.run([sys.executable,str(ROOT/'scripts'/'setup.py')])
def payload(text=None,file=None,prompt='Enter anything: '):
    if file:return Path(file).expanduser().read_bytes()
    return (text if text is not None else input(prompt)).encode()
def show_list():
    ensure();active={x['id'] for x in active_languages()};st=load_state();print(f"\nExecutable registry: {len(load_registry())} | verified here: {len(active)}")
    for l in load_registry():
        status='✓' if l['id'] in active else '·';ver=st.get('versions',{}).get(l['id'],'not verified');reason=st.get('failed',{}).get(l['id'],'')
        print(f" {status} {l['name']:<26} {l['kind']:<12} {(ver if status=='✓' else reason)[:70]}")
def show_catalog(letter=None):
    xs=load_catalog().get('languages',[])
    if letter:xs=[x for x in xs if x.get('letter')==letter.upper()]
    for x in xs:print(('✓ ' if x.get('termux_worker') else '· ')+x['name'])
    print(f'\nShown: {len(xs)}')
def worker_info(query):
    q=query.casefold();matches=[x for x in load_registry() if q in x['id'].casefold() or q in x['name'].casefold()]
    if not matches:print('No executable worker matched:',query);return 1
    st=load_state()
    for l in matches:
        print('\n'+'-'*84);print(l['name']);print('-'*84)
        print(json.dumps({**l,'verified_on_this_device':l['id'] in st.get('active',[]),'version':st.get('versions',{}).get(l['id']),'failure':st.get('failed',{}).get(l['id'])},indent=2))
        src=ROOT/'languages'/l['id']
        if src.exists():
            print('Source files:')
            for f in sorted(src.rglob('*')):
                if f.is_file():print(' ',f.relative_to(ROOT))
    return 0

def interactive():
    banner();ensure()
    while True:
        print('''
[1]  Run Full Language Chain
[2]  Run File Chain
[3]  Parallel Language Race
[4]  Multi-size Performance Matrix
[5]  Stress / Endurance Chain
[6]  Full Showcase Session
[7]  Differential Worker Audit
[8]  Chaos / Worker-Restart Test
[9]  Braided Topology Lab
[10] Multi-order Consensus Test
[11] Adaptive Device Calibration
[12] Resumable Checkpoint Chain
[13] Control Plane Dashboard
[14] Executable Language Status
[15] Global Catalog Stats / Search
[16] Benchmark Profiles
[17] Scenario Runner
[18] Device Snapshot
[19] Result History / Compare
[20] SQLite Performance Database
[21] Doctor / Self-test
[22] Install / Re-detect Everything
[23] Refresh Global Catalog
[24] Termux Package Plan
[25] Create Result Bundle
[26] Execution Plan / Dry Run
[27] Performance Regression Gate
[0]  Exit''')
        c=input('\nSelect: ').strip()
        if c=='0':return
        if c=='1':
            text=input('\nEnter anything: ');r=run_chain(text.encode(),telemetry=True);print_report(r,text)
        elif c=='2':
            p=Path(input('File path: ').strip()).expanduser();r=run_chain(p.read_bytes(),telemetry=True);print_report(r,str(p))
        elif c=='3':parallel_race(input('Race payload: ').encode())
        elif c=='4':matrix_benchmark()
        elif c=='5':stress_test()
        elif c=='6':showcase(input('Showcase payload: ').encode(),get_profile('showcase'))
        elif c=='7':differential_audit()
        elif c=='8':chaos_test(input('Chaos payload: ').encode())
        elif c=='9':topology_benchmark(input('Topology payload: ').encode())
        elif c=='10':consensus_test(input('Consensus payload: ').encode())
        elif c=='11':calibrate();print_calibration('balanced')
        elif c=='12':checkpoint_chain(input('Checkpoint payload: ').encode())
        elif c=='13':dashboard()
        elif c=='14':show_list()
        elif c=='15':
            print(json.dumps(catalog_stats(),indent=2));q=input('Search (blank to return): ').strip()
            if q:
                xs=search_catalog(q);[print(('✓ ' if x.get('termux_worker') else '· ')+x['name']) for x in xs[:250]];print('Matches:',len(xs))
        elif c=='16':print_profiles()
        elif c=='17':print_scenarios();name=input('Scenario name: ').strip();run_scenario(name,input('Scenario payload: ').encode())
        elif c=='18':print(json.dumps(device_snapshot(),indent=2))
        elif c=='19':
            print_history(20)
            try:compare_results()
            except Exception as e:print('Compare:',e)
        elif c=='20':print(json.dumps(database_stats(),indent=2))
        elif c=='21':subprocess.run([sys.executable,str(ROOT/'scripts'/'doctor.py')])
        elif c=='22':subprocess.run([sys.executable,str(ROOT/'scripts'/'setup.py'),'--install','--refresh-catalog'])
        elif c=='23':subprocess.run([sys.executable,str(ROOT/'scripts'/'refresh_catalog.py')])
        elif c=='24':subprocess.run([sys.executable,str(ROOT/'scripts'/'package_plan.py')])
        elif c=='25':print('Bundle:',create_bundle())
        elif c=='26':print_plan(execution_plan(0,1,'fastest'))
        elif c=='27':print_regression(regression_check())

def main():
    ap=argparse.ArgumentParser(description='Language Project — verified Termux polyglot execution, resilience and benchmark orchestration platform with a global language catalog.')
    sp=ap.add_subparsers(dest='cmd')
    p=sp.add_parser('run');p.add_argument('--text');p.add_argument('--file');p.add_argument('--rounds',type=int,default=1);p.add_argument('--warmups',type=int,default=1);p.add_argument('--order',choices=ORDERS,default='fastest');p.add_argument('--seed',type=int);p.add_argument('--telemetry',action='store_true')
    sp.add_parser('list');s=sp.add_parser('setup');s.add_argument('--install',action='store_true');s.add_argument('--update',action='store_true');s.add_argument('--refresh-catalog',action='store_true');sp.add_parser('doctor')
    b=sp.add_parser('bench');b.add_argument('--sizes',type=int,nargs='+',default=[16,256,4096]);b.add_argument('--repeats',type=int,default=3);b.add_argument('--warmups',type=int,default=1);b.add_argument('--order',choices=ORDERS,default='registry')
    rc=sp.add_parser('race');rc.add_argument('--text');rc.add_argument('--file');rc.add_argument('--iterations',type=int,default=5);rc.add_argument('--warmups',type=int,default=1)
    pr=sp.add_parser('parallel-race');pr.add_argument('--text');pr.add_argument('--file');pr.add_argument('--iterations',type=int,default=7);pr.add_argument('--warmups',type=int,default=1);pr.add_argument('--parallel',type=int,default=0)
    mx=sp.add_parser('matrix');mx.add_argument('--sizes',type=int,nargs='+',default=[16,256,4096,65536]);mx.add_argument('--iterations',type=int,default=5);mx.add_argument('--warmups',type=int,default=1)
    st=sp.add_parser('stress');st.add_argument('--size',type=int,default=2048);st.add_argument('--cycles',type=int,default=25);st.add_argument('--warmups',type=int,default=1);st.add_argument('--seed',type=int,default=1337)
    sh=sp.add_parser('showcase');sh.add_argument('--text');sh.add_argument('--file');sh.add_argument('--profile',choices=['quick','showcase','extreme'],default='showcase')
    sp.add_parser('profiles');sp.add_parser('snapshot');sp.add_parser('packages');wi=sp.add_parser('info');wi.add_argument('query')
    hi=sp.add_parser('history');hi.add_argument('--limit',type=int,default=20)
    co=sp.add_parser('compare');co.add_argument('result_a',nargs='?');co.add_argument('result_b',nargs='?')
    ca=sp.add_parser('calibrate');ca.add_argument('--sizes',type=int,nargs='+',default=[64,4096,65536]);ca.add_argument('--iterations',type=int,default=4);ca.add_argument('--warmups',type=int,default=2);ca.add_argument('--strategy',choices=['balanced','latency','throughput','stable'],default='balanced')
    calshow=sp.add_parser('calibration');calshow.add_argument('--strategy',choices=['balanced','latency','throughput','stable'],default='balanced')
    da=sp.add_parser('differential');da.add_argument('--vectors',type=int,default=32);da.add_argument('--max-size',type=int,default=4096);da.add_argument('--seed',type=int,default=1121);da.add_argument('--warmups',type=int,default=1)
    ch=sp.add_parser('chaos');ch.add_argument('--text');ch.add_argument('--file');ch.add_argument('--cycles',type=int,default=12);ch.add_argument('--restart-rate',type=float,default=0.20);ch.add_argument('--seed',type=int,default=1121);ch.add_argument('--warmups',type=int,default=1);ch.add_argument('--no-telemetry',action='store_true')
    ck=sp.add_parser('checkpoint');ck.add_argument('--text');ck.add_argument('--file');ck.add_argument('--order',choices=ORDERS,default='registry');ck.add_argument('--seed',type=int);ck.add_argument('--stop-after',type=int,default=0);ck.add_argument('--path')
    re=sp.add_parser('resume');re.add_argument('checkpoint');sp.add_parser('checkpoints')
    tp=sp.add_parser('topology');tp.add_argument('--text');tp.add_argument('--file');tp.add_argument('--lanes',type=int,default=4);tp.add_argument('--iterations',type=int,default=3);tp.add_argument('--warmups',type=int,default=1);tp.add_argument('--strategy',choices=['round-robin','contiguous','shuffle'],default='round-robin');tp.add_argument('--seed',type=int,default=1121)
    cn=sp.add_parser('consensus');cn.add_argument('--text');cn.add_argument('--file');cn.add_argument('--replicas',type=int,default=3);cn.add_argument('--rounds',type=int,default=1);cn.add_argument('--warmups',type=int,default=1);cn.add_argument('--seed',type=int,default=1121)
    sp.add_parser('scenarios');sn=sp.add_parser('scenario');sn.add_argument('name');sn.add_argument('--text');sn.add_argument('--file')
    db=sp.add_parser('db');dbs=db.add_subparsers(dest='db_cmd');dbs.add_parser('stats');dbl=dbs.add_parser('leaderboard');dbl.add_argument('--limit',type=int,default=30);dbl.add_argument('--min-samples',type=int,default=1);dbl.add_argument('--mode',default='chain');dbr=dbs.add_parser('recent');dbr.add_argument('--limit',type=int,default=20);dbr.add_argument('--mode');dbs.add_parser('rebuild')
    bu=sp.add_parser('bundle');bu.add_argument('paths',nargs='*');bu.add_argument('--name');sp.add_parser('dashboard')
    pl=sp.add_parser('plan');pl.add_argument('--bytes',type=int,default=0);pl.add_argument('--rounds',type=int,default=1);pl.add_argument('--order',choices=ORDERS,default='fastest');pl.add_argument('--json',action='store_true')
    rg=sp.add_parser('regression');rg.add_argument('--mode',default='chain');rg.add_argument('--threshold',type=float,default=15.0)
    c=sp.add_parser('catalog');csp=c.add_subparsers(dest='catalog_cmd');cl=csp.add_parser('list');cl.add_argument('--letter');cs=csp.add_parser('search');cs.add_argument('query');csp.add_parser('stats');csp.add_parser('refresh')
    sp.add_parser('verify');sp.add_parser('audit')
    a=ap.parse_args()
    if not a.cmd:return interactive()
    if a.cmd=='list':return show_list()
    if a.cmd=='setup':
        cmd=[sys.executable,str(ROOT/'scripts'/'setup.py')]
        if a.install:cmd+=['--install']
        if a.update:cmd+=['--update']
        if a.refresh_catalog:cmd+=['--refresh-catalog']
        return subprocess.call(cmd)
    if a.cmd=='doctor':return subprocess.call([sys.executable,str(ROOT/'scripts'/'doctor.py')])
    if a.cmd=='run':
        ensure();data=payload(a.text,a.file);r=run_chain(data,rounds=a.rounds,warmups=a.warmups,order=a.order,seed=a.seed,telemetry=a.telemetry);print_report(r,(a.text or a.file or 'stdin'));return 0 if r['integrity'] else 2
    if a.cmd=='bench':ensure();benchmark_suite(a.sizes,a.repeats,a.order,a.warmups);return 0
    if a.cmd=='race':ensure();r=race_workers(payload(a.text,a.file,'Race payload: '),a.iterations,a.warmups);return 0 if r['integrity'] else 2
    if a.cmd=='parallel-race':ensure();r=parallel_race(payload(a.text,a.file,'Parallel race payload: '),a.iterations,a.warmups,a.parallel);return 0 if r['integrity'] else 2
    if a.cmd=='matrix':ensure();r=matrix_benchmark(a.sizes,a.iterations,a.warmups);return 0 if r['integrity'] else 2
    if a.cmd=='stress':ensure();r=stress_test(a.size,a.cycles,a.warmups,a.seed);return 0 if r['integrity'] else 2
    if a.cmd=='showcase':ensure();r=showcase(payload(a.text,a.file,'Showcase payload: '),get_profile(a.profile));return 0 if r['integrity'] else 2
    if a.cmd=='profiles':return print_profiles()
    if a.cmd=='snapshot':print(json.dumps(device_snapshot(),indent=2));return 0
    if a.cmd=='packages':return subprocess.call([sys.executable,str(ROOT/'scripts'/'package_plan.py')])
    if a.cmd=='info':return worker_info(a.query)
    if a.cmd=='history':print_history(a.limit);return 0
    if a.cmd=='compare':
        try:compare_results(a.result_a,a.result_b);return 0
        except Exception as e:print('Compare:',e);return 1
    if a.cmd=='calibrate':ensure();r=calibrate(a.sizes,a.iterations,a.warmups);print_calibration(a.strategy);return 0 if r.get('integrity') else 2
    if a.cmd=='calibration':print_calibration(a.strategy);return 0
    if a.cmd=='differential':ensure();r=differential_audit(a.vectors,a.max_size,a.seed,a.warmups);return 0 if r['integrity'] else 2
    if a.cmd=='chaos':ensure();r=chaos_test(payload(a.text,a.file,'Chaos payload: '),a.cycles,a.restart_rate,a.seed,a.warmups,not a.no_telemetry);return 0 if r['integrity'] else 2
    if a.cmd=='checkpoint':ensure();r=checkpoint_chain(payload(a.text,a.file,'Checkpoint payload: '),a.order,a.seed,a.stop_after,a.path);return 0 if r.get('integrity',True) else 2
    if a.cmd=='resume':ensure();r=resume_checkpoint(a.checkpoint);return 0 if r.get('integrity',True) else 2
    if a.cmd=='checkpoints':[print(json.dumps(x,ensure_ascii=False)) for x in checkpoint_list()];return 0
    if a.cmd=='topology':ensure();r=topology_benchmark(payload(a.text,a.file,'Topology payload: '),a.lanes,a.iterations,a.warmups,a.strategy,a.seed);return 0 if r['integrity'] else 2
    if a.cmd=='consensus':ensure();r=consensus_test(payload(a.text,a.file,'Consensus payload: '),a.replicas,a.rounds,a.warmups,a.seed);return 0 if r['integrity'] else 2
    if a.cmd=='scenarios':print_scenarios();return 0
    if a.cmd=='scenario':ensure();r=run_scenario(a.name,payload(a.text,a.file,'Scenario payload: '));return 0 if r['integrity'] else 2
    if a.cmd=='db':
        if a.db_cmd=='stats' or not a.db_cmd:print(json.dumps(database_stats(),indent=2));return 0
        if a.db_cmd=='rebuild':print('Indexed result files:',database_rebuild());return 0
        if a.db_cmd=='recent':[print(json.dumps(x,ensure_ascii=False)) for x in database_recent(a.limit,a.mode)];return 0
        if a.db_cmd=='leaderboard':
            rows=database_leaderboard(a.limit,a.min_samples,a.mode)
            for i,x in enumerate(rows,1):print(f"{i:>3} {x['name']:<26} {x['avg_median_ns']/1e6:>10.4f} ms samples={x['samples']:<4} integrity={x['integrity_rate']*100:6.2f}%")
            return 0
    if a.cmd=='bundle':print(create_bundle(a.paths or None,a.name));return 0
    if a.cmd=='dashboard':dashboard();return 0
    if a.cmd=='plan':
        ensure();r=execution_plan(a.bytes,a.rounds,a.order)
        if a.json:print(json.dumps(r,indent=2))
        else:print_plan(r)
        return 0
    if a.cmd=='regression':
        r=regression_check(a.mode,a.threshold);print_regression(r);return 0 if r.get('ok') else 2
    if a.cmd=='catalog':
        if a.catalog_cmd=='stats':print(json.dumps(catalog_stats(),indent=2));return 0
        if a.catalog_cmd=='search':
            xs=search_catalog(a.query);[print(('✓ ' if x.get('termux_worker') else '· ')+x['name']) for x in xs];print('Matches:',len(xs));return 0
        if a.catalog_cmd=='list':show_catalog(a.letter);return 0
        if a.catalog_cmd=='refresh':return subprocess.call([sys.executable,str(ROOT/'scripts'/'refresh_catalog.py')])
        c.print_help();return 0
    if a.cmd=='verify':return subprocess.call([sys.executable,str(ROOT/'scripts'/'verify_manifest.py')])
    if a.cmd=='audit':return subprocess.call([sys.executable,str(ROOT/'scripts'/'audit_project.py')])
if __name__=='__main__':raise SystemExit(main() or 0)
