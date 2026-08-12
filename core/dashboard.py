from __future__ import annotations
from .engine import active_languages,load_state
from .catalog import catalog_stats
from .adaptive import load_calibration
from .store import stats as db_stats,leaderboard,recent
from .advanced import checkpoint_list
from .scenarios import load_scenarios
from .langtools import status as langtools_status
from .paths import DATA_ROOT

def dashboard():
    active=active_languages('registry');cat=catalog_stats();cal=load_calibration();db=db_stats();cps=checkpoint_list();incomplete=[x for x in cps if x.get('status')!='complete'];sc=load_scenarios().get('scenarios',{});nt=langtools_status()
    print('\n'+'='*96);print('LANGUAGE PROJECT — CONTROL PLANE');print('='*96)
    print(f"Language Project home:  {str(DATA_ROOT)}")
    print(f"Verified workers:       {len(active):>8}")
    print(f"Global catalog:         {cat.get('total',0):>8,}")
    print(f"Native useful tools:    {nt.get('available',0):>8}/{nt.get('registered',0)}")
    print(f"Calibration workers:    {cal.get('languages',0):>8}")
    print(f"Database sessions:      {db.get('sessions',0):>8}")
    print(f"Stage measurements:     {db.get('stage_measurements',0):>8}")
    print(f"Incomplete checkpoints: {len(incomplete):>8}")
    print(f"Scenario definitions:   {len(sc):>8}")
    top=leaderboard(8)
    if top:
        print('\nHistorical performance leaderboard:')
        for i,x in enumerate(top,1):print(f" {i:>2}. {x['name']:<26} avg median {x['avg_median_ns']/1e6:>9.4f} ms | samples {x['samples']}")
    rr=recent(5)
    if rr:
        print('\nRecent sessions:')
        for x in rr:print(f" {x['timestamp'][:19]:<20} {x['mode']:<18} langs={x['languages']:<3} bytes={x['bytes']:<8} {'OK' if x['integrity'] else 'FAIL'}")
    if incomplete:
        print('\nResumable checkpoints:')
        for x in incomplete[:5]:print(f" {x['session_id']} phase={x['phase']:<6} completed={x['completed']:<4} {x['path']}")
    print('='*96)
    return {'active':len(active),'catalog':cat,'native_tools':nt,'calibration':cal,'database':db,'incomplete_checkpoints':incomplete,'scenarios':list(sc)}
