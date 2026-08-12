from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,time,json,hashlib,platform,os,datetime,statistics,random,csv,select
from .registry import ROOT,load_registry,expand
from .analytics import timing_stats,shannon_entropy,device_snapshot,session_id
from .telemetry import ResourceSampler
from .store import record_result
from .plugins import emit
from .provenance import snapshot as provenance_snapshot
STATE=ROOT/'state'/'active.json'
@dataclass
class Worker:
    lang:dict; proc:subprocess.Popen; startup_ns:int
    def _readline(self, timeout:float):
        ready,_,_=select.select([self.proc.stdout.fileno()],[],[],timeout)
        if not ready: raise TimeoutError(f"{self.lang['name']}: worker response timeout after {timeout:.1f}s")
        out=self.proc.stdout.readline()
        if out=='':
            err=''
            try: err=self.proc.stderr.read(400).strip()
            except Exception: pass
            raise RuntimeError(f"{self.lang['name']}: worker exited unexpectedly"+(f" ({err})" if err else ''))
        return out.strip()
    def request(self,mode:str,h:str):
        # Empty payloads have no bytes to transform; keep them valid without sending an ambiguous blank protocol token.
        if h=='':return '',0
        # Scale the watchdog with payload size while keeping the measured interval honest.
        timeout=max(10.0, min(300.0, 10.0 + len(h)/1_000_000*8.0))
        t=time.perf_counter_ns();self.proc.stdin.write(f"{mode} {h}\n");self.proc.stdin.flush();out=self._readline(timeout);dt=time.perf_counter_ns()-t
        if out=='ERR' or len(out)!=len(h) or any(c not in '0123456789abcdefABCDEF' for c in out):raise RuntimeError(f"{self.lang['name']}: bad worker output {out[:120]!r}")
        return out.lower(),dt
    def close(self):
        try:self.proc.stdin.write('QUIT\n');self.proc.stdin.flush();self.proc.wait(timeout=2)
        except Exception:
            try:self.proc.kill()
            except Exception:pass
def load_state():return json.loads(STATE.read_text()) if STATE.exists() else {}
def active_languages(order='registry',seed=None):
    reg={x['id']:x for x in load_registry()};st=load_state();ids=[i for i in st.get('active',[]) if i in reg];langs=[reg[i] for i in ids]
    if order=='random':random.Random(seed).shuffle(langs)
    elif order=='fastest':
        m=st.get('metrics',{});langs.sort(key=lambda x:m.get(x['id'],{}).get('median_vector_ns',10**30))
    elif order.startswith('adaptive-'):
        strategy=order.split('-',1)[1];cal=ROOT/'state'/'calibration.json'
        try:preferred=json.loads(cal.read_text()).get('orders',{}).get(strategy,[])
        except Exception:preferred=[]
        rank={lid:i for i,lid in enumerate(preferred)}
        if preferred:langs.sort(key=lambda x:rank.get(x['id'],10**9))
        else:
            m=st.get('metrics',{});langs.sort(key=lambda x:m.get(x['id'],{}).get('median_vector_ns',10**30))
    return langs
def start_one(lang):
    t=time.perf_counter_ns();p=subprocess.Popen(expand(lang['run']),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=ROOT)
    p.stdin.write('PING\n');p.stdin.flush()
    ready,_,_=select.select([p.stdout.fileno()],[],[],8.0)
    pong=p.stdout.readline().strip() if ready else ''
    dt=time.perf_counter_ns()-t
    if pong!='PONG':
        try:p.kill()
        except Exception:pass
        raise RuntimeError(f"PING failed ({pong!r})")
    return Worker(lang,p,dt)
def prewarm(langs,warmups=1):
    workers={};errors={}
    with ThreadPoolExecutor(max_workers=min(12,max(1,len(langs)))) as ex:
        fut={ex.submit(start_one,l):l for l in langs}
        for f in as_completed(fut):
            l=fut[f]
            try:workers[l['id']]=f.result()
            except Exception as e:errors[l['id']]=str(e)
    ordered=[workers[l['id']] for l in langs if l['id'] in workers]
    if not errors and warmups:
        sample='00112233445566778899aabbccddeeff'
        for w in ordered:
            for _ in range(warmups):
                enc,_=w.request('E',sample);dec,_=w.request('D',enc)
                if dec!=sample:errors[w.lang['id']]='warmup integrity failure';break
    return ordered,errors
def _stats(vals,payload_bytes=0):
    return timing_stats(vals,payload_bytes)
def run_chain(data:bytes,save=True,verbose=True,rounds=1,warmups=1,order='fastest',seed=None,telemetry=False):
    if rounds<1:raise ValueError('rounds must be >= 1')
    langs=active_languages(order,seed)
    if not langs:raise RuntimeError('No verified languages. Run: language-project setup --install')
    workers,errors=prewarm(langs,warmups)
    if errors:
        for w in workers:w.close()
        raise RuntimeError('Prewarm failed: '+json.dumps(errors))
    sid=session_id('chain',data,str(seed or ''));plugin_errors=emit('on_session_start',{'session_id':sid,'mode':'chain','bytes':len(data),'languages':[w.lang['id'] for w in workers]})
    sampler=ResourceSampler().start() if telemetry else None
    original_hex=data.hex();stage={w.lang['id']:{'id':w.lang['id'],'name':w.lang['name'],'kind':w.lang['kind'],'startup_ns':w.startup_ns,'encode_ns':[],'decode_ns':[]} for w in workers}
    encoded_hex=original_hex;cur=original_hex;round_rows=[];all_start=time.perf_counter_ns()
    try:
      for rno in range(1,rounds+1):
        if cur!=original_hex:raise RuntimeError('round boundary integrity failure')
        if verbose:print(f"\nRound {rno}/{rounds} — encoding through {len(workers)} verified Termux languages...\n")
        estart=time.perf_counter_ns()
        for i,w in enumerate(workers,1):
            cur,ns=w.request('E',cur);stage[w.lang['id']]['encode_ns'].append(ns)
            if verbose:print(f"[E {i:02d}/{len(workers):02d}] {w.lang['name']:<24} {ns/1e6:10.4f} ms")
        encoded_hex=cur;enc_total=time.perf_counter_ns()-estart
        if verbose:print('\nReverse decode chain...\n')
        dstart=time.perf_counter_ns()
        for i,w in enumerate(reversed(workers),1):
            cur,ns=w.request('D',cur);stage[w.lang['id']]['decode_ns'].append(ns)
            if verbose:print(f"[D {i:02d}/{len(workers):02d}] {w.lang['name']:<24} {ns/1e6:10.4f} ms")
        dec_total=time.perf_counter_ns()-dstart
        round_rows.append({'round':rno,'encode_ns':enc_total,'decode_ns':dec_total,'total_ns':enc_total+dec_total,'integrity':cur==original_hex})
        if cur!=original_hex:break
    finally:
      for w in workers:w.close()
    telemetry_summary=sampler.stop() if sampler else None
    total_ns=time.perf_counter_ns()-all_start;ok=cur==original_hex and all(x['integrity'] for x in round_rows)
    stage_stats=[]
    for x in stage.values():
        es=_stats(x.pop('encode_ns'),len(data));ds=_stats(x.pop('decode_ns'),len(data));stage_stats.append({**x,'encode':es,'decode':ds,'combined_median_ns':es['median_ns']+ds['median_ns'],'combined_p95_ns':es['p95_ns']+ds['p95_ns']})
    ranking=sorted(stage_stats,key=lambda x:x['combined_median_ns'])
    result={
      'schema':4,'project':'Language Project','mode':'chain','session_id':sid,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'languages':len(workers),'language_order':[w.lang['id'] for w in workers],
      'bytes':len(data),'rounds':rounds,'warmups':warmups,'order':order,'seed':seed,'integrity':ok,
      'original_sha256':hashlib.sha256(data).hexdigest(),'encoded_sha256':hashlib.sha256(bytes.fromhex(encoded_hex)).hexdigest(),'recovered_sha256':hashlib.sha256(bytes.fromhex(cur)).hexdigest(),
      'encoded_hex':encoded_hex,'total_ns':total_ns,'rounds_detail':round_rows,'startup_ns_total':sum(w.startup_ns for w in workers),'stages':stage_stats,'ranking':ranking,
      'input_entropy_bits_per_byte':shannon_entropy(data),'encoded_entropy_bits_per_byte':shannon_entropy(bytes.fromhex(encoded_hex)),
      'aggregate_round_stats':_stats([x['total_ns'] for x in round_rows],len(data)*2*max(1,len(workers))),
      'telemetry':telemetry_summary,'plugins':{'enabled':bool(os.environ.get('LANGUAGE_PROJECT_PLUGINS')),'errors':plugin_errors},'provenance':provenance_snapshot(),'device':device_snapshot()
    }
    plugin_errors.extend(emit('on_session_end',{'session_id':sid,'mode':'chain','integrity':ok,'result':result}))
    result['plugins']['errors']=plugin_errors
    if save:export_result(result)
    return result
def export_result(r):
    out=ROOT/'results';out.mkdir(exist_ok=True);stem='run-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');jp=out/(stem+'.json');cp=out/(stem+'.csv');mp=out/(stem+'.md')
    with cp.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['rank','id','language','kind','startup_ms','encode_median_ms','decode_median_ms','combined_median_ms'])
        for i,x in enumerate(r['ranking'],1):w.writerow([i,x['id'],x['name'],x['kind'],x['startup_ns']/1e6,x['encode']['median_ns']/1e6,x['decode']['median_ns']/1e6,x['combined_median_ns']/1e6])
    lines=['# Language Project Result','',f"- Session: `{r.get('session_id','')}`",f"- Integrity: **{'PERFECT MATCH' if r['integrity'] else 'FAILED'}**",f"- Languages: **{r['languages']}**",f"- Input bytes: **{r['bytes']}**",f"- Rounds: **{r['rounds']}**",'', '| Rank | Language | Encode median (ms) | Decode median (ms) | Combined median (ms) |','|---:|---|---:|---:|---:|']
    for i,x in enumerate(r['ranking'],1):lines.append(f"| {i} | {x['name']} | {x['encode']['median_ns']/1e6:.4f} | {x['decode']['median_ns']/1e6:.4f} | {x['combined_median_ns']/1e6:.4f} |")
    mp.write_text('\n'.join(lines)+'\n');r['result_files']={'json':str(jp),'csv':str(cp),'markdown':str(mp)}
    jp.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');record_result(r,str(jp));return r['result_files']
def race_workers(data:bytes,iterations=5,warmups=1,save=True):
    if iterations<1: raise ValueError('iterations must be >= 1')
    langs=active_languages('registry')
    if not langs: raise RuntimeError('No verified languages. Run: language-project setup --install')
    workers,errors=prewarm(langs,warmups)
    if errors:
        for w in workers:w.close()
        raise RuntimeError('Race prewarm failed: '+json.dumps(errors))
    h=data.hex();rows=[]
    try:
        for w in workers:
            encs=[];decs=[];ok=True
            for _ in range(iterations):
                enc,en=w.request('E',h);dec,dn=w.request('D',enc)
                encs.append(en);decs.append(dn);ok=ok and dec==h
            es=_stats(encs,len(data));ds=_stats(decs,len(data))
            rows.append({'id':w.lang['id'],'name':w.lang['name'],'kind':w.lang['kind'],'startup_ns':w.startup_ns,'encode':es,'decode':ds,'combined_median_ns':es['median_ns']+ds['median_ns'],'integrity':ok})
    finally:
        for w in workers:w.close()
    rows.sort(key=lambda x:x['combined_median_ns'])
    result={'schema':2,'project':'Language Project','mode':'race','session_id':session_id('race',data),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'iterations':iterations,'warmups':warmups,'languages':len(rows),'integrity':all(x['integrity'] for x in rows),'sha256':hashlib.sha256(data).hexdigest(),'input_entropy_bits_per_byte':shannon_entropy(data),'provenance':provenance_snapshot(),'device':device_snapshot(),'ranking':rows}
    if save:
        out=ROOT/'results';out.mkdir(exist_ok=True);stem='race-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');jp=out/(stem+'.json');cp=out/(stem+'.csv');mp=out/(stem+'.md')
        with cp.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['rank','id','language','kind','encode_median_ms','decode_median_ms','combined_median_ms','startup_ms','integrity'])
            for i,x in enumerate(rows,1):w.writerow([i,x['id'],x['name'],x['kind'],x['encode']['median_ns']/1e6,x['decode']['median_ns']/1e6,x['combined_median_ns']/1e6,x['startup_ns']/1e6,x['integrity']])
        lines=['# Language Project Race','',f"- Languages: **{len(rows)}**",f"- Payload: **{len(data)} bytes**",f"- Iterations: **{iterations}**",f"- Integrity: **{'PERFECT MATCH' if result['integrity'] else 'FAILED'}**",'', '| Rank | Language | Encode median (ms) | Decode median (ms) | Combined (ms) |','|---:|---|---:|---:|---:|']
        for i,x in enumerate(rows,1):lines.append(f"| {i} | {x['name']} | {x['encode']['median_ns']/1e6:.4f} | {x['decode']['median_ns']/1e6:.4f} | {x['combined_median_ns']/1e6:.4f} |")
        mp.write_text('\n'.join(lines)+'\n');result['result_files']={'json':str(jp),'csv':str(cp),'markdown':str(mp)};jp.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');record_result(result,str(jp))
    print('\n'+'='*82);print('LANGUAGE PROJECT — LANGUAGE RACE');print('='*82)
    print(f"Payload: {len(data)} bytes | Languages: {len(rows)} | Iterations: {iterations} | Integrity: {'PERFECT MATCH' if result['integrity'] else 'FAILED'}")
    print(f"{'#':>3}  {'Language':<26} {'Encode':>12} {'Decode':>12} {'Combined':>12}")
    for i,x in enumerate(rows,1):print(f"{i:>3}  {x['name']:<26} {x['encode']['median_ns']/1e6:>9.4f} ms {x['decode']['median_ns']/1e6:>9.4f} ms {x['combined_median_ns']/1e6:>9.4f} ms")
    if result.get('result_files'):
        for k,v in result['result_files'].items():print(f"{k.title():<21} {v}")
    print('='*82)
    return result

def benchmark_suite(sizes=(16,256,4096),repeats=3,order='registry',warmups=1):
    rows=[]
    for size in sizes:
      samples=[]
      data=bytes((i*131+17)%256 for i in range(size))
      for rep in range(1,repeats+1):
        r=run_chain(data,save=False,verbose=False,rounds=1,warmups=warmups,order=order);samples.append(r['total_ns']);rows.append({'bytes':size,'repeat':rep,'languages':r['languages'],'total_ns':r['total_ns'],'integrity':r['integrity']})
      print(f"{size:>8} bytes  median {statistics.median(samples)/1e6:>10.4f} ms  repeats={repeats}")
    out=ROOT/'results';out.mkdir(exist_ok=True);p=out/('suite-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json');p.write_text(json.dumps({'schema':1,'rows':rows},indent=2)+'\n');print('Suite JSON:',p);return rows
def print_report(r,original_preview=''):
    print('\n'+'='*82);print('LANGUAGE PROJECT — FINAL PERFORMANCE REPORT');print('='*82)
    if original_preview:print(f'Input:                 {original_preview[:110]}')
    print(f"Languages:             {r['languages']} verified")
    print(f"Data size:             {r['bytes']} bytes")
    print(f"Rounds:                {r['rounds']}")
    print(f"Order:                 {r['order']}")
    print(f"Measured chain total:  {sum(x['total_ns'] for x in r['rounds_detail'])/1e6:.4f} ms")
    print(f"Worker startup total:  {r['startup_ns_total']/1e6:.4f} ms")
    print(f"Integrity:             {'PERFECT MATCH' if r['integrity'] else 'FAILED'}")
    print(f"Transformations:       {r['languages']*2*r['rounds']}")
    print(f"Original SHA-256:      {r['original_sha256']}")
    print(f"Recovered SHA-256:     {r['recovered_sha256']}")
    print('\nPer-language median ranking:')
    print(f"{'#':>3}  {'Language':<26} {'Encode':>11} {'Decode':>11} {'Combined':>11} {'Startup':>11}")
    for i,x in enumerate(r['ranking'],1):print(f"{i:>3}  {x['name']:<26} {x['encode']['median_ns']/1e6:>9.4f}ms {x['decode']['median_ns']/1e6:>9.4f}ms {x['combined_median_ns']/1e6:>9.4f}ms {x['startup_ns']/1e6:>9.4f}ms")
    if r['ranking']:
      print(f"\nFastest median:        {r['ranking'][0]['name']} ({r['ranking'][0]['combined_median_ns']/1e6:.4f} ms)")
      print(f"Slowest median:        {r['ranking'][-1]['name']} ({r['ranking'][-1]['combined_median_ns']/1e6:.4f} ms)")
    if r.get('result_files'):
      for k,v in r['result_files'].items():print(f"{k.title():<21} {v}")
    print('='*82)

def _save_generic(prefix,result,rows=None):
    result.setdefault('provenance',provenance_snapshot())
    out=ROOT/'results';out.mkdir(exist_ok=True)
    stem=f"{prefix}-"+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    jp=out/(stem+'.json');mp=out/(stem+'.md');hp=out/(stem+'.html')
    lines=[f"# Language Project — {result.get('mode',prefix).replace('-',' ').title()}",'',f"- Session: `{result.get('session_id','')}`",f"- Integrity: **{'PERFECT MATCH' if result.get('integrity') else 'FAILED'}**",f"- Languages: **{result.get('languages',0)}**",f"- Payload: **{result.get('bytes',0)} bytes**",'']
    if rows:
        lines += ['| Rank | Language | Median (ms) | P95 (ms) | Throughput (MiB/s) |','|---:|---|---:|---:|---:|']
        for i,x in enumerate(rows,1):
            med=x.get('combined_median_ns',x.get('median_ns',0)); p95=x.get('combined_p95_ns',x.get('p95_ns',0)); thr=x.get('throughput_mib_s',0.0)
            lines.append(f"| {i} | {x.get('name',x.get('id',''))} | {med/1e6:.4f} | {p95/1e6:.4f} | {thr:.2f} |")
    mp.write_text('\n'.join(lines)+'\n')
    title=f"Language Project — {result.get('mode',prefix).replace('-',' ').title()}"
    html=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',f'<title>{title}</title>','<style>body{font-family:system-ui,monospace;max-width:1100px;margin:32px auto;padding:0 18px;background:#111;color:#eee}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #333;text-align:right}th:nth-child(2),td:nth-child(2){text-align:left}.ok{color:#7fda7f}code{word-break:break-all}</style>',f'<h1>{title}</h1>',f"<p>Session: <code>{result.get('session_id','')}</code></p>",f"<p class={'ok' if result.get('integrity') else ''}>Integrity: {'PERFECT MATCH' if result.get('integrity') else 'FAILED'}</p>"]
    if rows:
        html.append('<table><tr><th>#</th><th>Language</th><th>Median ms</th><th>P95 ms</th><th>MiB/s</th></tr>')
        for i,x in enumerate(rows,1):
            med=x.get('combined_median_ns',x.get('median_ns',0));p95=x.get('combined_p95_ns',x.get('p95_ns',0));thr=x.get('throughput_mib_s',0.0)
            html.append(f"<tr><td>{i}</td><td>{x.get('name',x.get('id',''))}</td><td>{med/1e6:.4f}</td><td>{p95/1e6:.4f}</td><td>{thr:.2f}</td></tr>")
        html.append('</table>')
    html.append('<h2>Raw result</h2><pre>'+json.dumps(result,indent=2,ensure_ascii=False).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')+'</pre>')
    hp.write_text('\n'.join(html),encoding='utf-8')
    files={'json':str(jp),'markdown':str(mp),'html':str(hp)}
    if rows:
        cp=out/(stem+'.csv')
        with cp.open('w',newline='') as f:
            wr=csv.writer(f);wr.writerow(['rank','id','language','kind','median_ms','p95_ms','throughput_mib_s','integrity'])
            for i,x in enumerate(rows,1):
                med=x.get('combined_median_ns',x.get('median_ns',0));p95=x.get('combined_p95_ns',x.get('p95_ns',0));thr=x.get('throughput_mib_s',0.0)
                wr.writerow([i,x.get('id',''),x.get('name',''),x.get('kind',''),med/1e6,p95/1e6,thr,x.get('integrity','')])
        files['csv']=str(cp)
    result['result_files']=files
    jp.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');record_result(result,str(jp))
    return result['result_files']


def parallel_race(data:bytes,iterations=7,warmups=1,max_parallel=0,save=True):
    if iterations<1:raise ValueError('iterations must be >= 1')
    langs=active_languages('registry')
    if not langs:raise RuntimeError('No verified languages. Run: language-project setup --install')
    workers,errors=prewarm(langs,warmups)
    if errors:
        for w in workers:w.close()
        raise RuntimeError('Parallel race prewarm failed: '+json.dumps(errors))
    h=data.hex();rows=[];workers_count=max_parallel or min(len(workers),max(1,os.cpu_count() or 4))
    def bench(w):
        encs=[];decs=[];ok=True
        for _ in range(iterations):
            enc,en=w.request('E',h);dec,dn=w.request('D',enc);encs.append(en);decs.append(dn);ok=ok and dec==h
        es=_stats(encs,len(data));ds=_stats(decs,len(data))
        combined=[a+b for a,b in zip(encs,decs)];cs=_stats(combined,len(data)*2)
        return {'id':w.lang['id'],'name':w.lang['name'],'kind':w.lang['kind'],'startup_ns':w.startup_ns,'encode':es,'decode':ds,'combined':cs,'combined_median_ns':cs['median_ns'],'combined_p95_ns':cs['p95_ns'],'throughput_mib_s':cs['throughput_mib_s'],'integrity':ok}
    try:
        with ThreadPoolExecutor(max_workers=workers_count) as ex:
            fut={ex.submit(bench,w):w for w in workers}
            for f in as_completed(fut):rows.append(f.result())
    finally:
        for w in workers:w.close()
    rows.sort(key=lambda x:x['combined_median_ns'])
    result={'schema':2,'project':'Language Project','mode':'parallel-race','session_id':session_id('parallel-race',data),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'iterations':iterations,'warmups':warmups,'max_parallel':workers_count,'languages':len(rows),'integrity':all(x['integrity'] for x in rows),'sha256':hashlib.sha256(data).hexdigest(),'provenance':provenance_snapshot(),'device':device_snapshot(),'ranking':rows}
    if save:_save_generic('parallel-race',result,rows)
    print('\n'+'='*88);print('LANGUAGE PROJECT — PARALLEL LANGUAGE RACE');print('='*88)
    print(f"Payload: {len(data)} bytes | Languages: {len(rows)} | Iterations: {iterations} | Parallel workers: {workers_count} | Integrity: {'PERFECT MATCH' if result['integrity'] else 'FAILED'}")
    print(f"{'#':>3}  {'Language':<26} {'Median':>12} {'P95':>12} {'MiB/s':>12} {'Jitter':>10}")
    for i,x in enumerate(rows,1):print(f"{i:>3}  {x['name']:<26} {x['combined']['median_ns']/1e6:>9.4f} ms {x['combined']['p95_ns']/1e6:>9.4f} ms {x['combined']['throughput_mib_s']:>12.2f} {x['combined']['jitter_pct']:>8.2f}%")
    if result.get('result_files'):
        for k,v in result['result_files'].items():print(f"{k.title():<21} {v}")
    print('='*88);return result


def matrix_benchmark(sizes=(16,256,4096,65536),iterations=5,warmups=1,save=True):
    sizes=[int(x) for x in sizes if int(x)>=0]
    if not sizes:raise ValueError('at least one non-negative size is required')
    langs=active_languages('registry')
    if not langs:raise RuntimeError('No verified languages. Run: language-project setup --install')
    workers,errors=prewarm(langs,warmups)
    if errors:
        for w in workers:w.close()
        raise RuntimeError('Matrix prewarm failed: '+json.dumps(errors))
    rows=[];ok_all=True
    try:
        for w in workers:
            for size in sizes:
                data=bytes((i*131+17)%256 for i in range(size));h=data.hex();samples=[];ok=True
                for _ in range(iterations):
                    enc,en=w.request('E',h);dec,dn=w.request('D',enc);samples.append(en+dn);ok=ok and dec==h
                st=_stats(samples,size*2);ok_all=ok_all and ok
                rows.append({'id':w.lang['id'],'name':w.lang['name'],'kind':w.lang['kind'],'bytes':size,'iterations':iterations,'median_ns':st['median_ns'],'p95_ns':st['p95_ns'],'mean_ns':st['mean_ns'],'jitter_pct':st['jitter_pct'],'throughput_mib_s':st['throughput_mib_s'],'integrity':ok})
                print(f"{w.lang['name']:<26} {size:>9} B  median {st['median_ns']/1e6:>9.4f} ms  p95 {st['p95_ns']/1e6:>9.4f} ms  {st['throughput_mib_s']:>10.2f} MiB/s")
    finally:
        for w in workers:w.close()
    result={'schema':2,'project':'Language Project','mode':'matrix','session_id':session_id('matrix',salt=str(sizes)),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sizes':sizes,'iterations':iterations,'warmups':warmups,'languages':len(workers),'integrity':ok_all,'provenance':provenance_snapshot(),'device':device_snapshot(),'rows':rows}
    if save:
        out=ROOT/'results';out.mkdir(exist_ok=True);stem='matrix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');jp=out/(stem+'.json');cp=out/(stem+'.csv');mp=out/(stem+'.md');hp=out/(stem+'.html')
        with cp.open('w',newline='') as f:
            wr=csv.writer(f);wr.writerow(['language','id','bytes','iterations','median_ms','p95_ms','mean_ms','jitter_pct','throughput_mib_s','integrity'])
            for x in rows:wr.writerow([x['name'],x['id'],x['bytes'],x['iterations'],x['median_ns']/1e6,x['p95_ns']/1e6,x['mean_ns']/1e6,x['jitter_pct'],x['throughput_mib_s'],x['integrity']])
        lines=['# Language Project — Size Matrix','',f"- Session: `{result['session_id']}`",f"- Languages: **{result['languages']}**",f"- Sizes: **{', '.join(map(str,sizes))} bytes**",f"- Integrity: **{'PERFECT MATCH' if ok_all else 'FAILED'}**",'','| Language | Bytes | Median ms | P95 ms | MiB/s |','|---|---:|---:|---:|---:|']
        for x in rows:lines.append(f"| {x['name']} | {x['bytes']} | {x['median_ns']/1e6:.4f} | {x['p95_ns']/1e6:.4f} | {x['throughput_mib_s']:.2f} |")
        mp.write_text('\n'.join(lines)+'\n')
        html=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Language Project Matrix</title><style>body{font-family:system-ui;max-width:1200px;margin:30px auto;padding:0 18px;background:#111;color:#eee}table{border-collapse:collapse;width:100%}th,td{padding:7px;border-bottom:1px solid #333;text-align:right}th:first-child,td:first-child{text-align:left}</style><h1>Language Project — Size Matrix</h1><table><tr><th>Language</th><th>Bytes</th><th>Median ms</th><th>P95 ms</th><th>MiB/s</th></tr>']
        for x in rows:html.append(f"<tr><td>{x['name']}</td><td>{x['bytes']}</td><td>{x['median_ns']/1e6:.4f}</td><td>{x['p95_ns']/1e6:.4f}</td><td>{x['throughput_mib_s']:.2f}</td></tr>")
        html.append('</table>');hp.write_text('\n'.join(html));result['result_files']={'json':str(jp),'csv':str(cp),'markdown':str(mp),'html':str(hp)};jp.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');record_result(result,str(jp))
        print('Matrix JSON:',jp);print('Matrix CSV:',cp);print('Matrix HTML:',hp)
    return result


def stress_test(size=2048,cycles=25,warmups=1,seed=1337,save=True):
    if size<0 or cycles<1:raise ValueError('size must be >= 0 and cycles >= 1')
    langs=active_languages('registry')
    if not langs:raise RuntimeError('No verified languages. Run: language-project setup --install')
    workers,errors=prewarm(langs,warmups)
    if errors:
        for w in workers:w.close()
        raise RuntimeError('Stress prewarm failed: '+json.dumps(errors))
    rnd=random.Random(seed);cycle_rows=[];ok_all=True
    try:
        for cycle in range(1,cycles+1):
            data=bytes(rnd.randrange(256) for _ in range(size));original=data.hex();cur=original;t0=time.perf_counter_ns()
            for w in workers:cur,_=w.request('E',cur)
            for w in reversed(workers):cur,_=w.request('D',cur)
            ns=time.perf_counter_ns()-t0;ok=cur==original;ok_all=ok_all and ok
            cycle_rows.append({'cycle':cycle,'total_ns':ns,'integrity':ok,'sha256':hashlib.sha256(data).hexdigest()})
            print(f"Cycle {cycle:>4}/{cycles:<4} {ns/1e6:>10.4f} ms  {'OK' if ok else 'FAILED'}")
            if not ok:break
    finally:
        for w in workers:w.close()
    stats=_stats([x['total_ns'] for x in cycle_rows],size*2*max(1,len(workers)))
    result={'schema':2,'project':'Language Project','mode':'stress','session_id':session_id('stress',salt=f'{size}:{cycles}:{seed}'),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':size,'cycles_requested':cycles,'cycles_completed':len(cycle_rows),'warmups':warmups,'seed':seed,'languages':len(workers),'integrity':ok_all and len(cycle_rows)==cycles,'stats':stats,'cycles':cycle_rows,'provenance':provenance_snapshot(),'device':device_snapshot()}
    if save:_save_generic('stress',result)
    print(f"\nStress median: {stats['median_ns']/1e6:.4f} ms | P95: {stats['p95_ns']/1e6:.4f} ms | jitter: {stats['jitter_pct']:.2f}% | integrity: {'PERFECT MATCH' if result['integrity'] else 'FAILED'}")
    return result


def showcase(data:bytes,profile):
    print('\n'+'#'*92);print('LANGUAGE PROJECT — FULL SHOWCASE SESSION');print('#'*92)
    print('1/4 Full chained round-trip')
    chain=run_chain(data,rounds=profile['chain']['rounds'],warmups=profile['chain']['warmups'],order=profile['chain'].get('order','registry'),telemetry=True)
    print_report(chain,'showcase input')
    print('\n2/4 Parallel language race')
    race=parallel_race(data,iterations=profile['race']['iterations'],warmups=profile['race']['warmups'])
    print('\n3/4 Multi-size performance matrix')
    matrix=matrix_benchmark(profile['matrix']['sizes'],profile['matrix']['iterations'],profile['matrix']['warmups'])
    print('\n4/4 Stability chain')
    stress=stress_test(profile['stress']['size'],profile['stress']['cycles'],profile['stress']['warmups'])
    summary={'schema':1,'project':'Language Project','mode':'showcase','session_id':session_id('showcase',data),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'profile':profile,'integrity':all(x.get('integrity') for x in (chain,race,matrix,stress)),'languages':chain['languages'],'bytes':len(data),'parts':{'chain':chain.get('result_files',{}),'parallel_race':race.get('result_files',{}),'matrix':matrix.get('result_files',{}),'stress':stress.get('result_files',{})},'device':device_snapshot()}
    _save_generic('showcase',summary)
    print('\n'+'#'*92);print(f"SHOWCASE COMPLETE — {'PERFECT INTEGRITY' if summary['integrity'] else 'INTEGRITY FAILURE'} — {summary['languages']} VERIFIED LANGUAGES");print('#'*92)
    return summary
