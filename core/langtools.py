from pathlib import Path
import json, subprocess, shutil, tempfile, datetime, os, hashlib

ROOT = Path(__file__).resolve().parents[1]
from .paths import DATA_ROOT, BUILD_DIR, POLYTOOLS_STATE_FILE
REGISTRY = ROOT / 'config' / 'registries' / 'polytools.json'
STATE = POLYTOOLS_STATE_FILE
BUILD = BUILD_DIR / 'polytools'


def load_tools():
    return json.loads(REGISTRY.read_text(encoding='utf-8'))['tools']


def _expand(parts):
    return [str(x).replace('{root}', str(ROOT)).replace('{data}', str(DATA_ROOT)) for x in parts]


def _tool(tid):
    for t in load_tools():
        if t['id'] == tid:
            return t
    raise KeyError(f'unknown language tool: {tid}')


def load_state():
    try:
        return json.loads(STATE.read_text(encoding='utf-8'))
    except Exception:
        return {'schema': 1, 'active': [], 'failed': {}}


def _fixtures(base):
    base = Path(base)
    project = base / 'project'; project.mkdir(parents=True, exist_ok=True)
    text = base / 'sample.txt'; text.write_text('alpha beta beta\nTODO: improve this\nalpha gamma\nERROR sample failure\ntrailing   \n', encoding='utf-8')
    binary = base / 'sample.bin'; binary.write_bytes(bytes(range(256)) + b'\x00Language Project\xff\n')
    binary_copy = base / 'sample-copy.bin'; binary_copy.write_bytes(binary.read_bytes())
    js = base / 'sample.json'; js.write_text('{"name":"Language Project","items":[1,2,3],"ok":true}\n', encoding='utf-8')
    jsonl = base / 'sample.jsonl'; jsonl.write_text('{"id":1,"ok":true}\n[1,2,3]\n"text"\n', encoding='utf-8')
    csv = base / 'sample.csv'; csv.write_text('name,value\nalpha,1\nbeta,2\ngamma,\n', encoding='utf-8')
    tsv = base / 'sample.tsv'; tsv.write_text('name\tvalue\nalpha\t1\nbeta\t2\n', encoding='utf-8')
    kv = base / 'sample.env'; kv.write_text('# sample\nNAME=Language Project\nMODE=termux\n', encoding='utf-8')
    log = base / 'sample.log'; log.write_text('INFO start\nWARN slow\nERROR failed\nDEBUG detail\nINFO done\n', encoding='utf-8')
    props = base / 'sample.properties'; props.write_text('name=Language Project\nmode=termux\nname=duplicate\n', encoding='utf-8')
    numbers = base / 'numbers.txt'; numbers.write_text('1\n2.5\n-3\n10\n', encoding='utf-8')
    markdown = base / 'README.md'; markdown.write_text('# Sample\n\n## First\nText\n### Child\n', encoding='utf-8')
    source = base / 'sample.c'; source.write_text('int main(void) {\n  return (1 + 2);\n}\n', encoding='utf-8')
    (project/'main.py').write_text('# TODO: demo\nprint("hello")\n', encoding='utf-8')
    (project/'data.json').write_text(js.read_text(), encoding='utf-8')
    (project/'notes.md').write_text(markdown.read_text(), encoding='utf-8')
    (project/'sample.log').write_text(log.read_text(), encoding='utf-8')
    return {
        'text': text, 'binary': binary, 'binary_copy': binary_copy, 'json': js, 'jsonl': jsonl,
        'csv': csv, 'tsv': tsv, 'kv': kv, 'log': log, 'properties': props, 'numbers': numbers,
        'markdown': markdown, 'source': source, 'project': project,
    }


def _resolve_args(args, fixtures):
    out=[]
    for x in args:
        if isinstance(x, str) and len(x)>2 and x.startswith('{') and x.endswith('}'):
            k=x[1:-1]; out.append(str(fixtures[k]))
        else: out.append(str(x))
    return out



def _invocation(t,args):
    cmd=_expand(t['run']); env=os.environ.copy(); args=[str(x) for x in args]
    if t.get('arg_mode') in {'env','stdin'}:
        return cmd,env
    return cmd+args,env

def _stdin_payload(t,args):
    if t.get('arg_mode')=='stdin': return '\n'.join(str(x) for x in args)+'\n'
    return None

def _command_exists(cmd):
    first = _expand(cmd)[0]
    return Path(first).exists() if '/' in first else shutil.which(first) is not None


def setup_tools(active_language_ids, verbose=True):
    """Build and smoke-test one useful native tool for each verified language."""
    active_language_ids=set(active_language_ids)
    BUILD.mkdir(parents=True, exist_ok=True)
    for d in ('java','scala','ghc'):
        (BUILD/d).mkdir(parents=True, exist_ok=True)
    active=[]; failed={}; metrics={}
    with tempfile.TemporaryDirectory(prefix='language-project-polytools-') as td:
        fixtures=_fixtures(td)
        for i,t in enumerate(load_tools(),1):
            if t['language_id'] not in active_language_ids:
                failed[t['id']]='language worker not active on this device'
                continue
            if verbose: print(f"  [tool {i:02d}/{len(load_tools()):02d}] {t['language']}: {t['name']}")
            try:
                if t.get('build'):
                    cmd=_expand(t['build'])
                    if shutil.which(cmd[0]) is None:
                        raise RuntimeError(f'missing build command: {cmd[0]}')
                    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=240)
                    if r.returncode!=0:
                        raise RuntimeError('build failed: '+((r.stderr or r.stdout).strip()[-1200:]))
                cmd=_expand(t['run'])
                if not _command_exists(t['run']):
                    raise RuntimeError(f'runtime/output missing: {cmd[0]}')
                args=_resolve_args(t.get('smoke_args',[]),fixtures)
                full_cmd,env=_invocation(t,args)
                r=subprocess.run(full_cmd,cwd=ROOT,capture_output=True,text=True,timeout=30,env=env,input=_stdin_payload(t,args))
                if r.returncode!=0:
                    raise RuntimeError(f'smoke exit {r.returncode}: '+((r.stderr or r.stdout).strip()[-1200:]))
                active.append(t['id'])
                metrics[t['id']]={'smoke_stdout_bytes':len(r.stdout.encode()),'smoke_stderr_bytes':len(r.stderr.encode())}
                if verbose: print('    VERIFIED TOOL')
            except Exception as e:
                failed[t['id']]=str(e)
                if verbose: print('    SKIP TOOL',e)
    state={
        'schema':1,'project':'Language Project','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'registered_tools':len(load_tools()),'active':active,'failed':failed,'metrics':metrics,
        'active_language_ids':sorted(active_language_ids),
    }
    STATE.parent.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return state


def status():
    st=load_state(); aset=set(st.get('active',[])); rows=[]
    for t in load_tools():
        rows.append({**t,'available':t['id'] in aset,'failure':st.get('failed',{}).get(t['id'])})
    return {'registered':len(rows),'available':sum(x['available'] for x in rows),'tools':rows,'generated_at':st.get('generated_at')}


def run_tool(tool_id,args=None,timeout=60,allow_unverified=False):
    t=_tool(tool_id); st=load_state()
    if not allow_unverified and tool_id not in st.get('active',[]):
        reason=st.get('failed',{}).get(tool_id,'tool has not been verified; run language-project setup --install')
        raise RuntimeError(f'{tool_id} is unavailable: {reason}')
    cmd,env=_invocation(t,args or [])
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=timeout,env=env,input=(_stdin_payload(t,args or []).encode() if _stdin_payload(t,args or []) is not None else None))
    return {'tool':tool_id,'language':t['language'],'name':t['name'],'command':cmd,'returncode':r.returncode,
            'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')}


def recommend(query):
    words=set(query.casefold().replace('/',' ').replace('-',' ').split()); scored=[]
    for t in load_tools():
        hay=set((' '.join([t['id'],t['name'],t['category'],*t.get('tags',[])])).casefold().replace('-',' ').split())
        score=len(words & hay)
        if score: scored.append((score,t))
    scored.sort(key=lambda x:(-x[0],x[1]['id']))
    aset=set(load_state().get('active',[]))
    return [{**t,'available':t['id'] in aset,'score':score} for score,t in scored[:12]]


def _capture(tid,args,limit=16000):
    try:
        r=run_tool(tid,args,timeout=90)
        return {'ok':r['returncode']==0,'language':r['language'],'tool':tid,'stdout':r['stdout'][:limit],'stderr':r['stderr'][:4000],'returncode':r['returncode']}
    except Exception as e:
        return {'ok':False,'tool':tid,'error':str(e)}


def project_report(path):
    p=Path(path).expanduser().resolve()
    if not p.is_dir(): raise ValueError('project-report requires a directory')
    wanted=[('sys-report',[str(p)]),('dir-summary',[str(p),'15']),('code-metrics',[str(p)]),('extension-stats',[str(p)]),('recent-files',[str(p),'15']),('large-files',[str(p),'15']),('grep-context',['TODO|FIXME|HACK|BUG',str(p),'--ignore-case'])]
    available=set(load_state().get('active',[])); sections=[]
    for tid,args in wanted:
        if tid in available: sections.append(_capture(tid,args))
    return {'type':'project-report','path':str(p),'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tools_used':len(sections),'sections':sections}


def file_report(path):
    p=Path(path).expanduser().resolve()
    if not p.is_file(): raise ValueError('file-report requires a file')
    wanted=[('byte-stats',[str(p)]),('fnv64',[str(p)]),('eol-stats',[str(p)]),('line-stats',[str(p)]),('word-count',[str(p)]),('hex-view',[str(p),'128'])]
    available=set(load_state().get('active',[])); sections=[]
    for tid,args in wanted:
        if tid in available: sections.append(_capture(tid,args))
    return {'type':'file-report','path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'tools_used':len(sections),'sections':sections}


def data_report(path):
    p=Path(path).expanduser().resolve()
    if not p.is_file(): raise ValueError('data-report requires a file')
    ext=p.suffix.lower(); wanted=[]
    if ext=='.json': wanted=[('json-format',[str(p),'minify']),('json-shape',[str(p)])]
    elif ext in {'.jsonl','.ndjson'}: wanted=[('jsonl-check',[str(p)]),('jsonl-stats',[str(p)])]
    elif ext=='.csv': wanted=[('csv-stats',[str(p)])]
    elif ext in {'.tsv','.tab'}: wanted=[('tabular-stats',[str(p)])]
    elif ext in {'.properties','.conf','.env','.ini'}: wanted=[('kv-read',[str(p)]),('properties-check',[str(p)])]
    elif ext in {'.md','.markdown'}: wanted=[('markdown-outline',[str(p)])]
    elif ext in {'.log'}: wanted=[('log-stats',[str(p)]),('regex-filter',['ERROR|WARN',str(p)])]
    else: return file_report(p)
    available=set(load_state().get('active',[])); sections=[]
    for tid,args in wanted:
        if tid in available: sections.append(_capture(tid,args))
    return {'type':'data-report','path':str(p),'detected_extension':ext,'tools_used':len(sections),'sections':sections}


def auto_report(path):
    p=Path(path).expanduser()
    return project_report(p) if p.is_dir() else data_report(p)


def selftest(active_only=True):
    st=load_state(); ids=set(st.get('active',[])) if active_only else {t['id'] for t in load_tools()}
    results=[]
    with tempfile.TemporaryDirectory(prefix='language-project-langtools-test-') as td:
        fx=_fixtures(td)
        for t in load_tools():
            if t['id'] not in ids: continue
            args=_resolve_args(t.get('smoke_args',[]),fx)
            try:
                r=run_tool(t['id'],args,timeout=30,allow_unverified=not active_only)
                results.append({'tool':t['id'],'language':t['language'],'ok':r['returncode']==0,'returncode':r['returncode'],'stderr':r['stderr'][-500:]})
            except Exception as e: results.append({'tool':t['id'],'language':t['language'],'ok':False,'error':str(e)})
    return {'tested':len(results),'passed':sum(x['ok'] for x in results),'ok':all(x['ok'] for x in results),'results':results}

def workspace_report(path, output=None):
    """Run every available native language tool against useful project-derived inputs."""
    p=Path(path).expanduser().resolve()
    if not p.is_dir(): raise ValueError('workspace-report requires a directory')
    files=[]
    for f in p.rglob('*'):
        try:
            if f.is_file(): files.append((f, f.stat().st_size))
        except OSError: pass
    files.sort(key=lambda x:str(x[0]))
    readable=[]
    for f,size in files:
        if size>2_000_000: continue
        try:
            b=f.read_bytes()[:4096]
            if b'\x00' not in b: readable.append(f)
        except OSError: pass
    readme=next((x for x in readable if x.name.casefold().startswith('readme')), readable[0] if readable else None)
    source=next((x for x in readable if x.suffix.lower() in {'.py','.c','.cpp','.h','.rs','.go','.java','.kt','.js','.ts','.rb','.php','.lua','.sh'}),None)
    representative=files[0][0] if files else None
    available=set(load_state().get('active',[])); sections=[]
    with tempfile.TemporaryDirectory(prefix='language-project-workspace-') as td:
        d=Path(td)
        inventory=[{'path':str(f.relative_to(p)),'bytes':size,'extension':f.suffix.lower() or '[none]'} for f,size in files]
        meta={'project':p.name,'root':str(p),'file_count':len(files),'total_bytes':sum(x[1] for x in files),'extensions':{}}
        for x in inventory: meta['extensions'][x['extension']]=meta['extensions'].get(x['extension'],0)+1
        meta_json=d/'project.json'; meta_json.write_text(json.dumps(meta,ensure_ascii=False)+'\n',encoding='utf-8')
        inv_jsonl=d/'inventory.jsonl'; inv_jsonl.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in inventory),encoding='utf-8')
        inv_csv=d/'inventory.csv'; inv_csv.write_text('path,bytes,extension\n'+''.join(f'"{x["path"].replace(chr(34),chr(34)*2)}",{x["bytes"]},"{x["extension"]}"\n' for x in inventory),encoding='utf-8')
        inv_tsv=d/'inventory.tsv'; inv_tsv.write_text('path\tbytes\textension\n'+''.join(f'{x["path"].replace(chr(9)," ")}\t{x["bytes"]}\t{x["extension"]}\n' for x in inventory),encoding='utf-8')
        inv_txt=d/'inventory.txt'; inv_txt.write_text('\n'.join(x['path'] for x in inventory)+'\n',encoding='utf-8')
        kv=d/'project.env'; kv.write_text(f'NAME={p.name}\nFILES={len(files)}\nBYTES={meta["total_bytes"]}\n',encoding='utf-8')
        props=d/'project.properties'; props.write_text(f'name={p.name}\nfiles={len(files)}\nbytes={meta["total_bytes"]}\n',encoding='utf-8')
        nums=d/'sizes.txt'; nums.write_text('\n'.join(str(size) for _,size in files[:10000])+'\n',encoding='utf-8')
        log=d/'workspace.log'; log.write_text(f'INFO workspace={p}\nINFO files={len(files)}\nINFO bytes={meta["total_bytes"]}\nWARN large_files={sum(1 for _,s in files if s>10_000_000)}\n',encoding='utf-8')
        generated_source=d/'sample.c'; generated_source.write_text('int main(void) { return (1 + 2); }\n',encoding='utf-8')
        generated_md=d/'README.md'; generated_md.write_text(f'# {p.name}\n\n## Inventory\n\nFiles: {len(files)}\n',encoding='utf-8')
        ref=representative or meta_json; txt=readme or inv_txt; src=source or generated_source; md=(readme if readme and readme.suffix.lower()=='.md' else generated_md)
        copy=d/'project-copy.json'; copy.write_bytes(meta_json.read_bytes())
        args_by_tool={
          'sys-report':[str(p)], 'tabular-stats':[str(inv_tsv)], 'byte-stats':[str(ref)], 'word-frequency':[str(txt),'20'],
          'jsonl-check':[str(inv_jsonl)], 'json-format':[str(meta_json),'minify'], 'grep-context':['TODO|FIXME|HACK|BUG',str(p),'--ignore-case'],
          'unique-lines':[str(inv_txt),'--counts'], 'kv-read':[str(kv)], 'csv-stats':[str(inv_csv)], 'regex-filter':['ERROR|WARN',str(log)],
          'dir-summary':[str(p),'15'], 'fnv64':[str(ref)], 'file-compare':[str(meta_json),str(copy)], 'paren-check':[str(src)],
          'line-stats':[str(inv_txt)], 'log-stats':[str(log)], 'eol-stats':[str(txt)], 'hex-view':[str(ref),'128'], 'word-count':[str(txt)],
          'duplicate-lines-hs':[str(inv_txt)], 'extension-stats':[str(p)], 'code-metrics':[str(p)], 'properties-check':[str(props)],
          'jsonl-stats':[str(inv_jsonl)], 'number-stats':[str(nums)], 'markdown-outline':[str(md)], 'duplicate-lines-cr':[str(inv_txt)],
          'top-words':[str(txt),'20'], 'path-audit':[], 'recent-files':[str(p),'15'], 'large-files':[str(p),'15'],
          'trim-lines':[str(txt)], 'json-shape':[str(meta_json)]
        }
        for t in load_tools():
            if t['id'] not in available: continue
            result=_capture(t['id'],args_by_tool[t['id']],limit=12000)
            result['name']=t['name']; result['category']=t['category']; sections.append(result)
    report={
      'schema':1,'type':'native-multilanguage-workspace-report','project':'Language Project','target':str(p),
      'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registered_tools':len(load_tools()),
      'available_tools':len(available),'tools_executed':len(sections),'all_available_tools_executed':len(sections)==len(available),
      'files':len(files),'bytes':sum(x[1] for x in files),'sections':sections,
    }
    if output:
        out=Path(output).expanduser();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        report['written_to']=str(out)
    return report


def demo_tool(tool_id, timeout=60):
    """Run a registered native tool against its deterministic built-in fixture set."""
    t=_tool(tool_id)
    with tempfile.TemporaryDirectory(prefix='language-project-demo-') as td:
        fixtures=_fixtures(td)
        args=_resolve_args(t.get('smoke_args',[]),fixtures)
        return run_tool(tool_id,args,timeout=timeout)
