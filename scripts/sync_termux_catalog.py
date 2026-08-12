#!/usr/bin/env python3
"""Overlay the full Termux support registry onto the bundled language catalog."""
from pathlib import Path
import json,re,unicodedata,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'catalog'/'known_languages.json'; REG=ROOT/'config'/'registries'/'termux_supported.json'
def norm(s): return unicodedata.normalize('NFKC',s).casefold().strip()
def slugify(name):
    s=unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-') or 'language'
cat=json.loads(CAT.read_text(encoding='utf-8')); supported=json.loads(REG.read_text(encoding='utf-8'))['languages']
rows=cat.get('languages',[])
# Reset derived Termux coverage fields while preserving original worker fields.
for r in rows:
    r['termux_supported']=False;r['termux_modules']=[];r['termux_packages']=[];r['termux_tiers']=[]
by_name={norm(r['name']):r for r in rows}
alias={
 'scheme':'Scheme','prolog':'Prolog','common-lisp':'Common Lisp','assembly':'Assembly',
 'k':'K','mksh':'KornShell','objective-c':'Objective-C','octave':'Octave','ol':'OL',
 'picolisp':'PicoLisp','postscript':'PostScript','rc':'rc','smalltalk':'Smalltalk',
 'standard-ml':'Standard ML','webassembly':'WebAssembly','sql':'SQL','cicada':'Cicada',
 'rexx':'REXX','opencl':'OpenCL','cmake':'CMake','makefile':'Makefile','pari-gp':'PARI/GP',
 'glsl':'GLSL','gnuplot':'Gnuplot','m4':'M4','typst':'Typst','gap':'GAP'
}
used_slugs={r['slug'] for r in rows}
added=[]
for x in supported:
    candidates=[x['name'],alias.get(x['id']),x.get('linguist')]
    rec=None
    for c in candidates:
        if c and norm(c) in by_name:
            rec=by_name[norm(c)];break
    if rec is None:
        name=x['name'];base=slugify(name);slug=base;i=2
        while slug in used_slugs: slug=f'{base}-{i}';i+=1
        used_slugs.add(slug)
        rec={'name':name,'slug':slug,'letter':name[0].upper() if name[0].isalpha() else '#','sources':['termux-official-package-snapshot'],'aliases':[],'extensions':['.'+x['extension']] if x.get('extension') else [],'interpreters':[x['command']] if x.get('command') and '/' not in x['command'] and '{' not in x['command'] else [],'github_linguist_id':None,'termux_worker':False,'worker_id':None,'execution_policy':'termux-module'}
        rows.append(rec);by_name[norm(name)]=rec;added.append(name)
    rec['termux_supported']=True
    rec['termux_modules']=sorted(set(rec.get('termux_modules',[])+[x['id']]))
    rec['termux_packages']=sorted(set(rec.get('termux_packages',[])+x.get('packages',[])))
    rec['termux_tiers']=sorted(set(rec.get('termux_tiers',[])+[x.get('tier','native-module')]))
    if 'termux-official-package-snapshot' not in rec.get('sources',[]): rec.setdefault('sources',[]).append('termux-official-package-snapshot');rec['sources']=sorted(set(rec['sources']))
    if x.get('tier')=='worker':
        rec['termux_worker']=True;rec['worker_id']=x['id'];rec['execution_policy']='verified-on-device'
    elif rec.get('execution_policy')=='catalog-only': rec['execution_policy']='termux-package-runtime-probe'
rows.sort(key=lambda r:r['name'].casefold())
cat['count']=len(rows);cat['termux_supported_count']=sum(bool(r.get('termux_supported')) for r in rows);cat['termux_module_count']=len(supported);cat['executable_registry_count']=sum(x.get('tier')=='worker' for x in supported);cat['languages']=rows
CAT.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
langdir=ROOT/'catalog'/'languages';langdir.mkdir(parents=True,exist_ok=True)
for f in langdir.glob('*.json'): f.unlink()
for r in rows: (langdir/(r['slug']+'.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
# Regenerate README catalog blocks from bundled data only.
sys.path.insert(0,str(ROOT/'scripts'))
from refresh_catalog import render_readme_catalog
render_readme_catalog(rows)
print(f"Catalog: {len(rows)} names; {cat['termux_supported_count']} catalog records cover {len(supported)} Termux modules; added {len(added)} names")
if added: print('Added: '+', '.join(added))
