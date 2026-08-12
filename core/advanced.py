from __future__ import annotations
from pathlib import Path
import json,hashlib,random,time,datetime,statistics,os
from .registry import ROOT,load_registry
from .engine import active_languages,prewarm,start_one,_stats,_save_generic
from .analytics import device_snapshot,session_id
from .telemetry import ResourceSampler
from .store import record_result,record_event
CHECKPOINTS=ROOT/'state'/'checkpoints'

def _utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def _atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');tmp.replace(path)

def differential_audit(vectors=32,max_size=4096,seed=1121,warmups=1,save=True):
    if vectors<1 or max_size<0:raise ValueError('vectors >= 1 and max_size >= 0 required')
    langs=active_languages('registry')
    if not langs:raise RuntimeError('No verified languages. Run setup first.')
    workers,errors=prewarm(langs,warmups)
    if errors:
        for w in workers:w.close()
        raise RuntimeError('Prewarm failed: '+json.dumps(errors))
    rnd=random.Random(seed);test_vectors=[]
    anchors=[b'',b'Language Project',bytes(range(256))]
    for a in anchors:
        if len(a)<=max_size:test_vectors.append(a)
    while len(test_vectors)<vectors:
        n=rnd.randrange(max_size+1) if max_size else 0;test_vectors.append(bytes(rnd.randrange(256) for _ in range(n)))
    test_vectors=test_vectors[:vectors];rows=[];all_ok=True
    try:
        for w in workers:
            lat=[];det=True;ok=True;unique=set()
            for data in test_vectors:
                h=data.hex();e1,n1=w.request('E',h);e2,n2=w.request('E',h);d,n3=w.request('D',e1)
                det=det and e1==e2;ok=ok and d==h and len(e1)==len(h);unique.add(hashlib.sha256(e1.encode()).hexdigest());lat.extend((n1,n2,n3))
            avg_payload=int(sum(len(x) for x in test_vectors)/max(1,len(test_vectors)));st=_stats(lat,avg_payload);row={'id':w.lang['id'],'name':w.lang['name'],'kind':w.lang['kind'],'vectors':len(test_vectors),'deterministic':det,'roundtrip':ok,'unique_transform_fingerprints':len(unique),'median_ns':st['median_ns'],'p95_ns':st['p95_ns'],'jitter_pct':st['jitter_pct'],'throughput_mib_s':st['throughput_mib_s'],'integrity':det and ok};rows.append(row);all_ok=all_ok and row['integrity']
            print(f"{w.lang['name']:<26} vectors={len(test_vectors):>3} deterministic={'YES' if det else 'NO ':<3} inverse={'OK' if ok else 'FAIL':<4} median={st['median_ns']/1e6:>8.4f} ms")
    finally:
        for w in workers:w.close()
    rows.sort(key=lambda x:x['median_ns'])
    result={'schema':1,'project':'Language Project','mode':'differential-audit','session_id':session_id('differential',salt=f'{vectors}:{max_size}:{seed}'),'timestamp':_utc(),'vectors':len(test_vectors),'max_size':max_size,'seed':seed,'warmups':warmups,'languages':len(rows),'bytes':sum(len(x) for x in test_vectors),'integrity':all_ok,'ranking':rows,'device':device_snapshot()}
    if save:
        _save_generic('differential',result,rows);record_result(result,result.get('result_files',{}).get('json'))
    return result

def chaos_test(data:bytes,cycles=12,restart_rate=0.20,seed=1121,warmups=1,telemetry=True,save=True):
    if not 0<=restart_rate<=1:raise ValueError('restart_rate must be 0..1')
    langs=active_languages('registry')
    workers,errors=prewarm(langs,warmups)
    if errors:
        for w in workers:w.close()
        raise RuntimeError('Prewarm failed: '+json.dumps(errors))
    rnd=random.Random(seed);h0=data.hex();events=[];cycles_out=[];ok_all=True;sampler=ResourceSampler().start() if telemetry else None
    sid=session_id('chaos',data,str(seed))
    try:
        for cycle in range(1,cycles+1):
            cur=h0;t0=time.perf_counter_ns();restarts=0
            for idx,w in enumerate(workers):
                if rnd.random()<restart_rate:
                    old=w;old.close();w=start_one(old.lang);workers[idx]=w;restarts+=1;ev={'cycle':cycle,'phase':'encode','language':w.lang['id'],'event':'worker-restart'};events.append(ev);record_event(sid,'worker-restart',ev)
                cur,_=w.request('E',cur)
            for revpos in range(len(workers)-1,-1,-1):
                w=workers[revpos]
                if rnd.random()<restart_rate:
                    old=w;old.close();w=start_one(old.lang);workers[revpos]=w;restarts+=1;ev={'cycle':cycle,'phase':'decode','language':w.lang['id'],'event':'worker-restart'};events.append(ev);record_event(sid,'worker-restart',ev)
                cur,_=w.request('D',cur)
            ns=time.perf_counter_ns()-t0;ok=cur==h0;ok_all=ok_all and ok;cycles_out.append({'cycle':cycle,'total_ns':ns,'restarts':restarts,'integrity':ok});print(f"Chaos cycle {cycle:>3}/{cycles:<3} restarts={restarts:>3} time={ns/1e6:>10.4f} ms {'OK' if ok else 'FAILED'}")
            if not ok:break
    finally:
        for w in workers:w.close()
    tele=sampler.stop() if sampler else None
    st=_stats([x['total_ns'] for x in cycles_out],len(data)*2*max(1,len(workers)))
    result={'schema':1,'project':'Language Project','mode':'chaos','session_id':sid,'timestamp':_utc(),'bytes':len(data),'cycles_requested':cycles,'cycles_completed':len(cycles_out),'restart_rate':restart_rate,'seed':seed,'languages':len(workers),'integrity':ok_all and len(cycles_out)==cycles,'stats':st,'events':events,'cycles':cycles_out,'telemetry':tele,'device':device_snapshot()}
    if save:_save_generic('chaos',result);record_result(result,result.get('result_files',{}).get('json'))
    return result

def checkpoint_chain(data:bytes,order='registry',seed=None,stop_after=0,checkpoint_path=None):
    langs=active_languages(order,seed)
    if not langs:raise RuntimeError('No verified languages. Run setup first.')
    sid=session_id('checkpoint-chain',data,str(seed or ''));path=Path(checkpoint_path) if checkpoint_path else CHECKPOINTS/(sid+'.json')
    cp={'schema':1,'project':'Language Project','mode':'checkpoint-chain','session_id':sid,'created_at':_utc(),'updated_at':_utc(),'status':'running','phase':'encode','next_index':0,'language_order':[x['id'] for x in langs],'original_hex':data.hex(),'current_hex':data.hex(),'original_sha256':hashlib.sha256(data).hexdigest(),'completed_stages':[],'stop_after':int(stop_after or 0)}
    _atomic_json(path,cp);return _resume(path,cp,stop_after)

def resume_checkpoint(path):
    p=Path(path).expanduser();cp=json.loads(p.read_text());return _resume(p,cp,0)

def _resume(path,cp,stop_after=0):
    reg={x['id']:x for x in load_registry()};ids=[x for x in cp['language_order'] if x in reg];steps=0
    def do_stage(lid,mode):
        nonlocal steps
        w=start_one(reg[lid])
        try:out,ns=w.request(mode,cp['current_hex'])
        finally:w.close()
        cp['current_hex']=out;cp['completed_stages'].append({'phase':'encode' if mode=='E' else 'decode','language':lid,'duration_ns':ns,'at':_utc()});cp['updated_at']=_utc();steps+=1
        _atomic_json(path,cp)
        print(f"Checkpoint {cp['phase']:<6} {lid:<22} {ns/1e6:>9.4f} ms -> {path.name}")
        return bool(stop_after and steps>=stop_after)
    if cp.get('status')=='complete':
        print('Checkpoint already complete:',path);return cp
    if cp['phase']=='encode':
        i=int(cp.get('next_index',0))
        while i<len(ids):
            if do_stage(ids[i],'E'):
                cp['next_index']=i+1;_atomic_json(path,cp);return cp
            i+=1;cp['next_index']=i;_atomic_json(path,cp)
        cp['phase']='decode';cp['next_index']=len(ids)-1;_atomic_json(path,cp)
    if cp['phase']=='decode':
        i=int(cp.get('next_index',len(ids)-1))
        while i>=0:
            if do_stage(ids[i],'D'):
                cp['next_index']=i-1;_atomic_json(path,cp);return cp
            i-=1;cp['next_index']=i;_atomic_json(path,cp)
    cp['status']='complete';cp['phase']='done';cp['updated_at']=_utc();cp['integrity']=cp['current_hex']==cp['original_hex'];cp['recovered_sha256']=hashlib.sha256(bytes.fromhex(cp['current_hex'])).hexdigest();cp['languages']=len(ids);cp['bytes']=len(bytes.fromhex(cp['original_hex']));cp['timestamp']=cp['updated_at'];_atomic_json(path,cp)
    result=dict(cp);result['result_files']={'checkpoint':str(path)};record_result(result,str(path));print(f"Checkpointed chain complete — {'PERFECT MATCH' if cp['integrity'] else 'FAILED'}")
    return cp

def checkpoint_list():
    CHECKPOINTS.mkdir(parents=True,exist_ok=True);rows=[]
    for p in sorted(CHECKPOINTS.glob('*.json'),key=lambda x:x.stat().st_mtime,reverse=True):
        try:
            d=json.loads(p.read_text());rows.append({'path':str(p),'session_id':d.get('session_id'),'status':d.get('status'),'phase':d.get('phase'),'completed':len(d.get('completed_stages',[])),'updated_at':d.get('updated_at')})
        except Exception:pass
    return rows
