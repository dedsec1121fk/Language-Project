from __future__ import annotations
from .registry import ROOT
from pathlib import Path
import json, datetime

def result_records(limit=None):
    rows=[]
    for p in (ROOT/'results').glob('*.json'):
        try:
            d=json.loads(p.read_text())
            rows.append({'path':str(p),'name':p.name,'timestamp':d.get('timestamp',''),'mode':d.get('mode','chain' if 'rounds_detail' in d else 'unknown'),'languages':d.get('languages',0),'bytes':d.get('bytes',0),'integrity':d.get('integrity'),'data':d})
        except Exception:pass
    rows.sort(key=lambda x:(x['timestamp'],x['name']),reverse=True)
    return rows[:limit] if limit else rows

def print_history(limit=20):
    rows=result_records(limit)
    if not rows:
        print('No result JSON files yet.');return rows
    print(f"{'Time':<26} {'Mode':<16} {'Langs':>5} {'Bytes':>10} {'OK':>4}  File")
    for x in rows:
        stamp=x['timestamp'][:25] or '-';ok='YES' if x['integrity'] is True else ('NO' if x['integrity'] is False else '-')
        print(f"{stamp:<26} {x['mode']:<16} {x['languages']:>5} {x['bytes']:>10} {ok:>4}  {x['name']}")
    return rows

def _metric(d):
    if d.get('mode') in ('race','parallel-race') and d.get('ranking'):
        return sum(x.get('combined_median_ns',0) for x in d['ranking'])
    if d.get('rounds_detail'):
        return sum(x.get('total_ns',0) for x in d['rounds_detail'])/max(1,len(d['rounds_detail']))
    if 'total_ns' in d:return d['total_ns']
    return None

def compare_results(path_a=None,path_b=None):
    if path_a and path_b:
        a=json.loads(Path(path_a).expanduser().read_text());b=json.loads(Path(path_b).expanduser().read_text());names=(str(path_a),str(path_b))
    else:
        rows=result_records()
        pair=None
        for i,newer in enumerate(rows):
            if _metric(newer['data']) is None: continue
            for older in rows[i+1:]:
                if older['mode']==newer['mode'] and _metric(older['data']) is not None:
                    pair=(older,newer);break
            if pair:break
        if not pair:raise RuntimeError('Need two comparable result files of the same benchmark mode, or provide two explicit paths.')
        older,newer=pair;a=older['data'];b=newer['data'];names=(older['name'],newer['name'])
    ma=_metric(a);mb=_metric(b)
    print('\nLanguage Project result comparison')
    print(f'A: {names[0]}')
    print(f'B: {names[1]}')
    print(f"Mode: {a.get('mode','chain')} -> {b.get('mode','chain')}")
    print(f"Languages: {a.get('languages',0)} -> {b.get('languages',0)}")
    print(f"Bytes: {a.get('bytes',0)} -> {b.get('bytes',0)}")
    if ma and mb:
        delta=(mb-ma)/ma*100
        direction='faster' if delta<0 else 'slower'
        print(f"Comparable aggregate: {ma/1e6:.4f} ms -> {mb/1e6:.4f} ms ({abs(delta):.2f}% {direction})")
    ar={x.get('id'):x for x in a.get('ranking',[])};br={x.get('id'):x for x in b.get('ranking',[])}
    common=sorted(set(ar)&set(br))
    if common:
        changes=[]
        for lid in common:
            av=ar[lid].get('combined_median_ns',0);bv=br[lid].get('combined_median_ns',0)
            if av:changes.append(((bv-av)/av*100,lid,ar[lid].get('name',lid),av,bv))
        changes.sort()
        print('\nLargest improvements:')
        for pct,lid,name,av,bv in changes[:5]:print(f"  {name:<25} {av/1e6:9.4f} -> {bv/1e6:9.4f} ms  {pct:+7.2f}%")
        print('Largest regressions:')
        for pct,lid,name,av,bv in changes[-5:][::-1]:print(f"  {name:<25} {av/1e6:9.4f} -> {bv/1e6:9.4f} ms  {pct:+7.2f}%")
    return {'a':a,'b':b,'metric_a':ma,'metric_b':mb}
