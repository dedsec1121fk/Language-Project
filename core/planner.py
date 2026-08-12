from __future__ import annotations
import json
from .engine import active_languages,load_state
from .store import leaderboard
from .provenance import fingerprint

def execution_plan(bytes_count=0,rounds=1,order='fastest'):
    langs=active_languages(order);hist={x['id']:x for x in leaderboard(500)};state=load_state();rows=[];pred=0
    for i,l in enumerate(langs,1):
        h=hist.get(l['id']);metric=(h or {}).get('avg_median_ns') or state.get('metrics',{}).get(l['id'],{}).get('median_vector_ns',0)
        if metric:pred+=int(metric)*max(1,int(rounds))
        rows.append({'position':i,'id':l['id'],'name':l['name'],'kind':l['kind'],'packages':l.get('packages',[]),'historical_combined_median_ns':(h or {}).get('avg_median_ns'),'setup_vector_ns':state.get('metrics',{}).get(l['id'],{}).get('median_vector_ns'),'version':state.get('versions',{}).get(l['id'])})
    return {'project':'Language Project','order':order,'bytes':int(bytes_count),'rounds':int(rounds),'languages':len(rows),'transformations':len(rows)*2*max(1,int(rounds)),'predicted_from_existing_metrics_ns':pred,'environment_fingerprint':fingerprint(),'workers':rows}

def print_plan(plan):
    print('\n'+'='*90);print('LANGUAGE PROJECT — EXECUTION PLAN');print('='*90)
    print(f"Order: {plan['order']} | Languages: {plan['languages']} | Transformations: {plan['transformations']} | Payload: {plan['bytes']} bytes")
    if plan['predicted_from_existing_metrics_ns']:print(f"Metric-based rough estimate: {plan['predicted_from_existing_metrics_ns']/1e6:.4f} ms (not a promise; payload/device load can change it)")
    print(f"Environment fingerprint: {plan['environment_fingerprint']}")
    for x in plan['workers']:print(f"{x['position']:>3} {x['name']:<26} {x['kind']:<12} {(x.get('version') or '')[:45]}")
    return plan
