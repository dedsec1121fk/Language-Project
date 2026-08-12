from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,as_completed
import time,datetime,hashlib,json,random
from .engine import active_languages,prewarm,_stats,_save_generic
from .analytics import device_snapshot,session_id


def _lanes(langs,count,strategy='round-robin',seed=1121):
    count=max(1,min(int(count),len(langs)))
    xs=list(langs)
    if strategy=='shuffle':random.Random(seed).shuffle(xs)
    lanes=[[] for _ in range(count)]
    if strategy in ('round-robin','shuffle'):
        for i,x in enumerate(xs):lanes[i%count].append(x)
    elif strategy=='contiguous':
        for i,x in enumerate(xs):lanes[min(count-1,i*count//len(xs))].append(x)
    else:raise ValueError('strategy must be round-robin, contiguous, or shuffle')
    return lanes


def topology_benchmark(data:bytes,lanes=4,iterations=3,warmups=1,strategy='round-robin',seed=1121,save=True):
    langs=active_languages('fastest')
    if not langs:raise RuntimeError('No verified languages. Run setup first.')
    lane_defs=_lanes(langs,lanes,strategy,seed);h=data.hex();lane_results=[];sid=session_id('topology',data,f'{lanes}:{strategy}:{seed}')
    def run_lane(idx,defs):
        workers,errors=prewarm(defs,warmups)
        if errors:
            for w in workers:w.close()
            return {'lane':idx,'languages':[x['id'] for x in defs],'integrity':False,'errors':errors,'samples':[]}
        samples=[];ok=True
        try:
            for _ in range(iterations):
                cur=h;t0=time.perf_counter_ns()
                for w in workers:cur,_=w.request('E',cur)
                for w in reversed(workers):cur,_=w.request('D',cur)
                ns=time.perf_counter_ns()-t0;samples.append(ns);ok=ok and cur==h
        finally:
            for w in workers:w.close()
        st=_stats(samples,len(data)*2*max(1,len(workers)))
        return {'lane':idx,'languages':[x['id'] for x in defs],'language_names':[x['name'] for x in defs],'language_count':len(defs),'integrity':ok,'samples_ns':samples,'median_ns':st['median_ns'],'p95_ns':st['p95_ns'],'jitter_pct':st['jitter_pct'],'throughput_mib_s':st['throughput_mib_s']}
    wall0=time.perf_counter_ns()
    with ThreadPoolExecutor(max_workers=len(lane_defs)) as ex:
        fut=[ex.submit(run_lane,i+1,d) for i,d in enumerate(lane_defs)]
        for f in as_completed(fut):lane_results.append(f.result())
    wall=time.perf_counter_ns()-wall0;lane_results.sort(key=lambda x:x['lane'])
    medians=[x.get('median_ns',0) for x in lane_results if x.get('median_ns')]
    balance=(max(medians)/min(medians)) if medians and min(medians)>0 else 0.0
    result={'schema':1,'project':'Language Project','mode':'topology','session_id':sid,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'languages':len(langs),'lanes':len(lane_defs),'iterations':iterations,'warmups':warmups,'strategy':strategy,'seed':seed,'integrity':all(x.get('integrity') for x in lane_results),'wall_ns':wall,'lane_balance_ratio':balance,'lane_results':lane_results,'device':device_snapshot()}
    if save:_save_generic('topology',result)
    print('\n'+'='*90);print('LANGUAGE PROJECT — BRAIDED TOPOLOGY LAB');print('='*90)
    for x in lane_results:print(f"Lane {x['lane']:>2}: {x.get('language_count',0):>2} languages | median {x.get('median_ns',0)/1e6:>10.4f} ms | p95 {x.get('p95_ns',0)/1e6:>10.4f} ms | {'OK' if x.get('integrity') else 'FAILED'}")
    print(f"Wall time: {wall/1e6:.4f} ms | balance ratio: {balance:.3f} | integrity: {'PERFECT MATCH' if result['integrity'] else 'FAILED'}")
    return result


def consensus_test(data:bytes,replicas=3,rounds=1,warmups=1,seed=1121,save=True):
    from .engine import run_chain
    if replicas<2:raise ValueError('replicas must be >= 2')
    rows=[];hashes=[];sid=session_id('consensus',data,str(seed))
    for i in range(replicas):
        r=run_chain(data,save=False,verbose=False,rounds=rounds,warmups=warmups,order='random',seed=seed+i)
        rows.append({'replica':i+1,'seed':seed+i,'languages':r['languages'],'order':r['language_order'],'integrity':r['integrity'],'recovered_sha256':r['recovered_sha256'],'chain_ns':sum(x['total_ns'] for x in r['rounds_detail'])});hashes.append(r['recovered_sha256'])
        print(f"Replica {i+1:>2}/{replicas} seed={seed+i:<8} {rows[-1]['chain_ns']/1e6:>10.4f} ms {'OK' if r['integrity'] else 'FAILED'}")
    ok=all(x['integrity'] for x in rows) and len(set(hashes))==1 and hashes[0]==hashlib.sha256(data).hexdigest()
    result={'schema':1,'project':'Language Project','mode':'consensus','session_id':sid,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'languages':rows[0]['languages'] if rows else 0,'replicas':replicas,'rounds':rounds,'warmups':warmups,'seed':seed,'integrity':ok,'original_sha256':hashlib.sha256(data).hexdigest(),'replicas_detail':rows,'device':device_snapshot()}
    if save:_save_generic('consensus',result)
    print(f"Consensus: {'UNANIMOUS PERFECT MATCH' if ok else 'FAILED'}")
    return result
