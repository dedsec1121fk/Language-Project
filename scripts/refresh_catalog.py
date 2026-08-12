#!/usr/bin/env python3
from pathlib import Path
import json,re,urllib.request,urllib.parse,unicodedata,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'catalog'/'known_languages.json'
UA={'User-Agent':'Language-Project/2.0 (+Termux catalog refresh)'}
def fetch(url,timeout=30):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read().decode('utf-8','replace')
def norm(s):return unicodedata.normalize('NFKC',s).casefold().strip()
def slugify(name):
    s=unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','-',s).strip('-') or 'language'
def add(store,name,source):
    name=re.sub(r'\s+',' ',name).strip()
    if not name or len(name)>160:return
    k=norm(name);e=store.setdefault(k,{'name':name,'sources':set()});e['sources'].add(source)
def github_linguist(store):
    text=fetch('https://raw.githubusercontent.com/github-linguist/linguist/master/lib/linguist/languages.yml')
    current=None; programming=False
    for line in text.splitlines()+['END:']:
        if line and not line.startswith(' ') and line.endswith(':'):
            if current and programming:add(store,current,'github-linguist-live')
            current=line[:-1];programming=False
        elif current and re.match(r'^  type:\s*programming\s*$',line):programming=True
def wikipedia(store):
    u='https://en.wikipedia.org/w/api.php?'+urllib.parse.urlencode({'action':'parse','page':'List of programming languages','prop':'wikitext','format':'json'})
    wt=json.loads(fetch(u))['parse']['wikitext']['*']
    wt=re.sub(r'<!--.*?-->','',wt,flags=re.S)
    for line in wt.splitlines():
        if not line.lstrip().startswith('*'):continue
        m=re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]',line)
        if m:add(store,m.group(2) or m.group(1),'wikipedia-live')

def pldb(store):
    data=json.loads(fetch('https://pldb.io/pldb.json',timeout=60))
    rows=data if isinstance(data,list) else data.get('languages',data.get('rows',[])) if isinstance(data,dict) else []
    for row in rows:
        if not isinstance(row,dict):continue
        name=row.get('title') or row.get('name') or row.get('id')
        if name:add(store,str(name),'pldb-live')

def pygments_mapping(store):
    text=fetch('https://raw.githubusercontent.com/pygments/pygments/master/pygments/lexers/_mapping.py')
    for m in re.finditer(r"'[^']+'\s*:\s*\([^,]+,\s*'([^']+)'",text):
        add(store,m.group(1),'pygments-live')

def mediawiki_category(store,base,title,source,max_pages=40):
    cont={}; pages=0
    while pages<max_pages:
        params={'action':'query','list':'categorymembers','cmtitle':title,'cmlimit':'500','format':'json',**cont}
        data=json.loads(fetch(base+'?'+urllib.parse.urlencode(params)))
        for m in data.get('query',{}).get('categorymembers',[]):
            n=m.get('title','');n=re.sub(r'^Category:','',n);add(store,n,source)
        if 'continue' not in data:break
        cont=data['continue'];pages+=1

def render_readme_catalog(out):
    readme=ROOT/'README.md'
    if not readme.exists(): return
    text=readme.read_text(encoding='utf-8')
    start='<!-- LANGUAGE-CATALOG:START -->'
    end='<!-- LANGUAGE-CATALOG:END -->'
    if start not in text or end not in text: return
    groups={}
    for item in out:
        groups.setdefault(item.get('letter','#'),[]).append(item['name'])
    ordered=['#']+[chr(c) for c in range(ord('A'),ord('Z')+1)]
    blocks=[start,'',f'Bundled catalog snapshot: **{len(out):,} unique language/dialect names**. Entries here are catalog records; only on-device verified workers participate in the execution chain.','']
    for letter in ordered:
        names=sorted(groups.get(letter,[]),key=str.casefold)
        if not names: continue
        label='Symbols / Numbers' if letter=='#' else letter
        blocks += ['<details>',f'<summary><strong>{label} — {len(names):,} cataloged names</strong></summary>','', ' · '.join(names),'','</details>','']
    blocks.append(end)
    before=text.split(start,1)[0]
    after=text.split(end,1)[1]
    readme.write_text(before+'\n'.join(blocks)+after,encoding='utf-8')

def write(store):
    old=json.loads(CAT.read_text()) if CAT.exists() else {'languages':[]}
    oldmap={norm(x['name']):x for x in old.get('languages',[])}
    reg=json.loads((ROOT/'languages.json').read_text())['languages']; runtime={norm(x['name']):x['id'] for x in reg}
    runtime_aliases={'posix sh':'dash','posix shell':'dash','dash':'dash','node.js':'javascript','nodejs':'javascript','awk':'awk','gawk':'awk','common lisp':'common-lisp','swi-prolog':'prolog','prolog':'prolog','scheme':'scheme','guile':'scheme'}
    for alias,rid in runtime_aliases.items(): runtime[norm(alias)]=rid
    used={};out=[]
    for k,e in sorted(store.items(),key=lambda kv:kv[1]['name'].casefold()):
        prior=oldmap.get(k,{})
        base=slugify(e['name']);slug=base
        if slug in used and used[slug]!=k:slug=f'{base}-{hashlib.sha1(e["name"].encode()).hexdigest()[:7]}'
        used[slug]=k;rid=runtime.get(k) or prior.get('worker_id')
        out.append({**prior,'name':e['name'],'slug':slug,'letter':e['name'][0].upper() if e['name'][0].isalpha() else '#','sources':sorted(set(prior.get('sources',[]))|e['sources']),'termux_worker':bool(rid),'worker_id':rid,'execution_policy':'verified-on-device' if rid else 'catalog-only'})
    payload={**old,'schema':3,'project':'Language Project','count':len(out),'executable_registry_count':len(reg),'languages':out};CAT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
    langdir=ROOT/'catalog'/'languages';langdir.mkdir(parents=True,exist_ok=True)
    for p in langdir.glob('*.json'):p.unlink()
    for x in out:(langdir/(x['slug']+'.json')).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
    render_readme_catalog(out)
    print(f'Catalog refreshed: {len(out)} unique names (README A-Z index regenerated)')
def main():
    base=json.loads(CAT.read_text()) if CAT.exists() else {'languages':[]};store={}
    for x in base.get('languages',[]):
        raw_name=x['name']
        cleaned_name=re.sub(r'\s+',' ',raw_name).strip()
        add(store,raw_name,'bundled-snapshot')
        key=norm(cleaned_name)
        if key in store:
            for source_name in x.get('sources',[]):
                store[key]['sources'].add(source_name)
    sources=[('PLDB',lambda:pldb(store)),('GitHub Linguist',lambda:github_linguist(store)),('Pygments',lambda:pygments_mapping(store)),('Wikipedia',lambda:wikipedia(store)),('Rosetta Code',lambda:mediawiki_category(store,'https://rosettacode.org/mw/index.php','Category:Programming Languages','rosetta-code-live',20)),('Esolang Wiki',lambda:mediawiki_category(store,'https://esolangs.org/w/api.php','Category:Languages','esolang-wiki-live',30))]
    for name,fn in sources:
        try:print('Refreshing',name+'...');fn()
        except Exception as e:print(f'  ! {name}: {e}')
    write(store)
if __name__=='__main__':main()
