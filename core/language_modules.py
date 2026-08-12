from __future__ import annotations
from pathlib import Path
import json
from .registry import ROOT, load_registry
from .langtools import load_tools, load_state as load_tool_state, demo_tool
from .engine import load_state as load_worker_state

LANGUAGE_ROOT=ROOT/'languages'

def _maps():
    workers={x['id']:x for x in load_registry()}
    tools={x['language_id']:x for x in load_tools()}
    return workers,tools

def list_modules():
    workers,tools=_maps(); ws=load_worker_state(); ts=load_tool_state()
    active_workers=set(ws.get('active',[])); active_tools=set(ts.get('active',[])); rows=[]
    for lid,w in workers.items():
        t=tools.get(lid,{})
        rows.append({
            'id':lid,'name':w['name'],'kind':w.get('kind'),'packages':w.get('packages',[]),
            'worker_verified':lid in active_workers,'tool_id':t.get('id'),'tool_name':t.get('name'),
            'tool_verified':t.get('id') in active_tools if t else False,
            'module_path':str(LANGUAGE_ROOT/lid),
        })
    return rows

def module_info(query):
    q=query.casefold(); workers,tools=_maps(); matches=[]
    for lid,w in workers.items():
        if q==lid.casefold() or q in w['name'].casefold():
            p=LANGUAGE_ROOT/lid
            meta={}
            try: meta=json.loads((p/'metadata.json').read_text(encoding='utf-8'))
            except Exception: pass
            files=[x.relative_to(ROOT).as_posix() for x in sorted(p.rglob('*')) if x.is_file()]
            matches.append({'worker':w,'tool':tools.get(lid),'metadata':meta,'files':files})
    return matches

def verify_modules():
    workers,tools=_maps(); errors=[]; rows=[]
    for lid,w in workers.items():
        p=LANGUAGE_ROOT/lid; t=tools.get(lid)
        required=[p/'README.md',p/'metadata.json',p/'examples'/'README.md',p/'examples'/'sample-input.txt',p/'examples'/'run-tool.sh',p/'examples'/'worker-protocol.txt',p/'tests'/'module.json']
        missing=[x.relative_to(ROOT).as_posix() for x in required if not x.is_file()]
        tool_src=ROOT/t['source'] if t else None
        if tool_src is None or not tool_src.is_file(): missing.append(str(t['source'] if t else 'native-tool-registry-entry'))
        # A worker source must be represented by at least one {root}/languages/<id>/ path in run/build.
        worker_tokens=' '.join(map(str,(w.get('run') or [])+(w.get('build') or [])))
        worker_source_ok=f'{{root}}/languages/{lid}/' in worker_tokens
        if not worker_source_ok: missing.append('worker-source-reference')
        try:
            smoke=json.loads((p/'tests'/'module.json').read_text(encoding='utf-8'))
            if smoke.get('language_id')!=lid: missing.append('tests/module.json language_id mismatch')
        except Exception as e: missing.append('tests/module.json invalid: '+str(e))
        ok=not missing
        if not ok: errors.extend(f'{lid}: {x}' for x in missing)
        rows.append({'id':lid,'name':w['name'],'ok':ok,'issues':missing,'file_count':sum(1 for x in p.rglob('*') if x.is_file())})
    return {'ok':not errors,'modules':len(rows),'errors':errors,'rows':rows}

def demo_module(query,timeout=60):
    matches=module_info(query)
    if not matches: raise KeyError(f'no language module matched: {query}')
    if len(matches)>1 and all(x['worker']['id'].casefold()!=query.casefold() for x in matches):
        raise KeyError('ambiguous module query: '+', '.join(x['worker']['id'] for x in matches))
    m=next((x for x in matches if x['worker']['id'].casefold()==query.casefold()),matches[0])
    t=m['tool']
    if not t: raise RuntimeError('module has no native tool registry entry')
    return {'module':m['worker']['id'],'language':m['worker']['name'],'native_tool':t['id'],'result':demo_tool(t['id'],timeout)}
