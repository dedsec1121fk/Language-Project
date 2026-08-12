from __future__ import annotations
from pathlib import Path
import json,datetime
from .registry import ROOT
from .engine import run_chain,parallel_race,matrix_benchmark,stress_test,_save_generic
from .advanced import differential_audit,chaos_test
from .topology import topology_benchmark,consensus_test
from .analytics import session_id,device_snapshot
CFG=ROOT/'config'/'scenarios.json'

def load_scenarios():return json.loads(CFG.read_text())
def print_scenarios():
    d=load_scenarios();
    for k,v in d.get('scenarios',{}).items():print(f"{k:<18} {v.get('description','')}")

def run_scenario(name,data=b'Language Project'):
    cfg=load_scenarios().get('scenarios',{}).get(name)
    if not cfg:raise KeyError(f'Unknown scenario: {name}')
    parts=[];ok=True
    for i,step in enumerate(cfg.get('steps',[]),1):
        typ=step['type'];args=dict(step.get('args',{}));print(f"\nScenario {name}: step {i}/{len(cfg['steps'])} — {typ}")
        if typ=='chain':r=run_chain(data,**args)
        elif typ=='parallel-race':r=parallel_race(data,**args)
        elif typ=='matrix':r=matrix_benchmark(**args)
        elif typ=='stress':r=stress_test(**args)
        elif typ=='differential':r=differential_audit(**args)
        elif typ=='chaos':r=chaos_test(data,**args)
        elif typ=='topology':r=topology_benchmark(data,**args)
        elif typ=='consensus':r=consensus_test(data,**args)
        else:raise ValueError(f'Unsupported scenario step: {typ}')
        ok=ok and bool(r.get('integrity'));parts.append({'type':typ,'session_id':r.get('session_id'),'integrity':r.get('integrity'),'result_files':r.get('result_files',{})})
        if not r.get('integrity') and cfg.get('fail_fast',True):break
    out={'schema':1,'project':'Language Project','mode':'scenario','session_id':session_id('scenario',data,name),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scenario':name,'description':cfg.get('description',''),'bytes':len(data),'languages':0,'integrity':ok,'parts':parts,'device':device_snapshot()};_save_generic('scenario-'+name,out);return out
