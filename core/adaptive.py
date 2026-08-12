from __future__ import annotations
from pathlib import Path
import json,datetime,statistics,math
from .registry import ROOT
from .paths import CALIBRATION_FILE
from .engine import matrix_benchmark,load_state
CAL=CALIBRATION_FILE

def _norm(vals):
    positive=[v for v in vals.values() if v and v>0]
    base=min(positive) if positive else 1.0
    return {k:(float(v)/base if v else 10**9) for k,v in vals.items()}

def calibrate(sizes=(64,4096,65536),iterations=4,warmups=2,save=True):
    result=matrix_benchmark(sizes=sizes,iterations=iterations,warmups=warmups,save=False)
    grouped={}
    for x in result['rows']:grouped.setdefault(x['id'],[]).append(x)
    state=load_state();startup={k:v.get('startup_and_test_ns',0) for k,v in state.get('metrics',{}).items()}
    med={lid:statistics.fmean([x['median_ns'] for x in rows]) for lid,rows in grouped.items()}
    jit={lid:statistics.fmean([x['jitter_pct'] for x in rows]) for lid,rows in grouped.items()}
    thr={lid:statistics.fmean([x['throughput_mib_s'] for x in rows]) for lid,rows in grouped.items()}
    nmed=_norm(med);njit=_norm({k:max(v,0.001) for k,v in jit.items()});nstart=_norm({k:max(startup.get(k,1),1) for k in grouped})
    maxthr=max(thr.values()) if thr else 1.0
    scores={}
    for lid in grouped:
        speed=nmed[lid];stability=njit[lid];start=nstart[lid];through=(maxthr/max(thr.get(lid,0.000001),0.000001))
        scores[lid]={
            'speed':speed,'stability':stability,'startup':start,'throughput_inverse':through,
            'balanced':speed*0.50+stability*0.20+start*0.10+through*0.20,
            'latency':speed*0.75+start*0.25,
            'throughput':through*0.75+speed*0.25,
            'stable':stability*0.60+speed*0.30+start*0.10,
        }
    orders={strategy:[k for k,_ in sorted(scores.items(),key=lambda kv:kv[1][strategy])] for strategy in ('balanced','latency','throughput','stable')}
    out={'schema':1,'project':'Language Project','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sizes':list(map(int,sizes)),'iterations':iterations,'warmups':warmups,'languages':len(grouped),'integrity':result['integrity'],'scores':scores,'orders':orders,'matrix_rows':result['rows']}
    if save:
        CAL.parent.mkdir(parents=True,exist_ok=True);CAL.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    return out

def load_calibration():
    try:return json.loads(CAL.read_text())
    except Exception:return {}

def order(strategy='balanced'):
    return load_calibration().get('orders',{}).get(strategy,[])

def print_calibration(strategy='balanced'):
    c=load_calibration()
    if not c:
        print('No calibration yet. Run: language-project calibrate');return []
    ids=c.get('orders',{}).get(strategy,[]);scores=c.get('scores',{})
    print(f"Calibration: {c.get('generated_at','')} | strategy={strategy} | languages={len(ids)}")
    for i,lid in enumerate(ids,1):print(f"{i:>3} {lid:<22} score={scores.get(lid,{}).get(strategy,0):.5f}")
    return ids
