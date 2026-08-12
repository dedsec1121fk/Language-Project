from __future__ import annotations
from pathlib import Path
import difflib,fnmatch,hashlib,json,os,re,shutil,socket,subprocess,time,urllib.request,urllib.parse
from .paths import BACKUPS_DIR, DOWNLOADS_DIR

SKIP_DIRS={'.git','.hg','.svn','node_modules','vendor','target','build','dist','__pycache__','.venv','venv'}
CACHE_NAMES={'__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.cache'}

def _iter_files(root,hidden=False):
    root=Path(root).expanduser().resolve()
    for p in root.rglob('*'):
        try: rel=p.relative_to(root)
        except Exception: continue
        if any(part in SKIP_DIRS for part in rel.parts): continue
        if not hidden and any(part.startswith('.') for part in rel.parts): continue
        if p.is_file() and not p.is_symlink(): yield p

def find_files(root,pattern='*',content=None,regex=False,case_sensitive=False,hidden=False,max_results=500):
    root=Path(root).expanduser().resolve(); out=[]
    rx=re.compile(content,0 if case_sensitive else re.I) if content and regex else None
    needle=content if case_sensitive or content is None else content.casefold()
    for p in _iter_files(root,hidden):
        rel=p.relative_to(root).as_posix(); name=rel if case_sensitive else rel.casefold(); pat=pattern if case_sensitive else pattern.casefold()
        if not fnmatch.fnmatch(name,pat) and not fnmatch.fnmatch(p.name if case_sensitive else p.name.casefold(),pat): continue
        match_line=None
        if content:
            try:
                with p.open('r',encoding='utf-8',errors='ignore') as f:
                    for n,line in enumerate(f,1):
                        ok=bool(rx.search(line)) if rx else (needle in (line if case_sensitive else line.casefold()))
                        if ok: match_line={'line':n,'text':line.rstrip()[:300]}; break
            except OSError: continue
            if match_line is None: continue
        out.append({'path':str(p),'relative':rel,'bytes':p.stat().st_size,'match':match_line})
        if len(out)>=max_results: break
    return {'root':str(root),'count':len(out),'results':out,'truncated':len(out)>=max_results}

def tree_view(root='.',depth=3,max_entries=500,hidden=False):
    root=Path(root).expanduser().resolve(); rows=[]
    def walk(d,prefix='',level=0):
        if level>depth or len(rows)>=max_entries:return
        try: items=sorted(d.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold()))
        except OSError:return
        if not hidden: items=[x for x in items if not x.name.startswith('.')]
        items=[x for x in items if x.name not in SKIP_DIRS]
        for i,p in enumerate(items):
            if len(rows)>=max_entries:return
            last=i==len(items)-1; rows.append(prefix+('└── ' if last else '├── ')+p.name+('/' if p.is_dir() else ''))
            if p.is_dir() and not p.is_symlink(): walk(p,prefix+('    ' if last else '│   '),level+1)
    rows=[root.name+'/'];walk(root,'',1)
    return '\n'.join(rows)+(f'\n... truncated at {max_entries} entries' if len(rows)>=max_entries else '')

def batch_rename(root,glob='*',find=None,replace='',prefix='',suffix='',apply=False):
    root=Path(root).expanduser().resolve();ops=[];targets=set()
    for p in sorted(root.glob(glob)):
        if not p.is_file():continue
        stem=p.stem;ext=p.suffix;newstem=stem
        if find is not None:newstem=newstem.replace(find,replace)
        newname=prefix+newstem+suffix+ext
        if newname==p.name:continue
        dest=p.with_name(newname)
        if dest in targets or (dest.exists() and dest!=p):raise FileExistsError(f'Rename collision: {dest}')
        targets.add(dest);ops.append({'from':str(p),'to':str(dest)})
    if apply:
        for x in ops:Path(x['from']).rename(x['to'])
    return {'applied':bool(apply),'count':len(ops),'operations':ops}

def sync_dirs(source,destination,delete=False,apply=False,checksum=False):
    src=Path(source).expanduser().resolve();dst=Path(destination).expanduser().resolve();dst.mkdir(parents=True,exist_ok=True)
    copies=[];deletes=[]
    srcmap={p.relative_to(src):p for p in _iter_files(src,hidden=True)}
    dstmap={p.relative_to(dst):p for p in _iter_files(dst,hidden=True)} if dst.exists() else {}
    for rel,p in srcmap.items():
        q=dst/rel;different=not q.exists()
        if q.exists():
            try:
                if checksum:
                    def h(x):
                        d=hashlib.sha256()
                        with x.open('rb') as f:
                            for c in iter(lambda:f.read(1024*1024),b''):d.update(c)
                        return d.digest()
                    different=h(p)!=h(q)
                else:different=(p.stat().st_size!=q.stat().st_size or int(p.stat().st_mtime)!=int(q.stat().st_mtime))
            except OSError:different=True
        if different:copies.append({'from':str(p),'to':str(q),'bytes':p.stat().st_size})
    if delete:
        for rel,p in dstmap.items():
            if rel not in srcmap:deletes.append(str(p))
    if apply:
        for x in copies:
            q=Path(x['to']);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(x['from'],q)
        for x in sorted(deletes,key=len,reverse=True):
            try:Path(x).unlink()
            except FileNotFoundError:pass
        for d in sorted((p for p in dst.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
            try:d.rmdir()
            except OSError:pass
    return {'applied':bool(apply),'source':str(src),'destination':str(dst),'copy_count':len(copies),'delete_count':len(deletes),'bytes_to_copy':sum(x['bytes'] for x in copies),'copies':copies,'deletes':deletes}

def backup_snapshot(source,destination=None,label=None):
    import tarfile
    src=Path(source).expanduser().resolve();dest=Path(destination).expanduser() if destination else BACKUPS_DIR;dest.mkdir(parents=True,exist_ok=True)
    stamp=time.strftime('%Y%m%d-%H%M%S');safe=re.sub(r'[^A-Za-z0-9._-]+','-',label or src.name).strip('-') or 'backup';out=dest/f'{safe}-{stamp}.tar.gz'
    with tarfile.open(out,'w:gz') as t:t.add(src,arcname=src.name,recursive=True)
    h=hashlib.sha256(out.read_bytes()).hexdigest();meta=out.with_suffix(out.suffix+'.json');meta.write_text(json.dumps({'schema':1,'source':str(src),'archive':str(out),'bytes':out.stat().st_size,'sha256':h,'created_unix':time.time()},indent=2)+'\n')
    return {'archive':str(out),'metadata':str(meta),'bytes':out.stat().st_size,'sha256':h}

def clean_plan(root,older_days=7,apply=False):
    root=Path(root).expanduser().resolve();cut=time.time()-max(0,older_days)*86400;targets=[]
    for p in root.rglob('*'):
        try:
            if p.is_dir() and p.name in CACHE_NAMES:targets.append(p)
            elif p.is_file() and (p.name.endswith(('.tmp','.pyc','.pyo')) or p.name.startswith('.tmp-')) and p.stat().st_mtime<=cut:targets.append(p)
        except OSError:pass
    # Remove nested targets when a parent cache directory is already included.
    uniq=[]
    for p in sorted(set(targets),key=lambda x:len(x.parts)):
        if any(parent in uniq for parent in p.parents):continue
        uniq.append(p)
    rows=[];total=0
    for p in uniq:
        size=0
        try:
            if p.is_dir():size=sum(x.stat().st_size for x in p.rglob('*') if x.is_file())
            else:size=p.stat().st_size
        except OSError:pass
        total+=size;rows.append({'path':str(p),'bytes':size,'kind':'directory' if p.is_dir() else 'file'})
    if apply:
        for p in sorted(uniq,key=lambda x:len(x.parts),reverse=True):
            try:shutil.rmtree(p) if p.is_dir() else p.unlink()
            except FileNotFoundError:pass
    return {'applied':bool(apply),'count':len(rows),'bytes':total,'targets':rows}

def unified_diff(a,b,context=3):
    pa,pb=Path(a).expanduser(),Path(b).expanduser();aa=pa.read_text(encoding='utf-8',errors='replace').splitlines(True);bb=pb.read_text(encoding='utf-8',errors='replace').splitlines(True)
    return ''.join(difflib.unified_diff(aa,bb,fromfile=str(pa),tofile=str(pb),n=max(0,context)))

def todo_scan(root,max_results=500):
    rx=re.compile(r'\b(TODO|FIXME|HACK|XXX|BUG|NOTE)\b[:\s-]*(.*)',re.I);rows=[]
    for p in _iter_files(root):
        try:
            if p.stat().st_size>4*1024*1024:continue
            with p.open('r',encoding='utf-8',errors='ignore') as f:
                for n,line in enumerate(f,1):
                    m=rx.search(line)
                    if m:rows.append({'path':str(p),'line':n,'tag':m.group(1).upper(),'text':line.strip()[:300]})
                    if len(rows)>=max_results:return {'count':len(rows),'results':rows,'truncated':True}
        except OSError:pass
    return {'count':len(rows),'results':rows,'truncated':False}

def normalize_line_endings(path,mode='lf',apply=False):
    p=Path(path).expanduser().resolve();files=[p] if p.is_file() else list(_iter_files(p,hidden=True));rows=[]
    for f in files:
        try:data=f.read_bytes()
        except OSError:continue
        if b'\x00' in data:continue
        normalized=data.replace(b'\r\n',b'\n').replace(b'\r',b'\n')
        if mode=='crlf':normalized=normalized.replace(b'\n',b'\r\n')
        if normalized!=data:
            rows.append({'path':str(f),'before_bytes':len(data),'after_bytes':len(normalized)})
            if apply:f.write_bytes(normalized)
    return {'applied':bool(apply),'mode':mode,'changed':len(rows),'files':rows}

def environment_report(commands=None):
    commands=commands or ['python','git','clang','clang++','node','ruby','perl','lua','php','go','rustc','java','javac','kotlinc','nim','zig','pkg','termux-info']
    rows=[]
    for c in commands:
        path=shutil.which(c);version=None
        if path:
            for flag in ('--version','-version','-v'):
                try:
                    r=subprocess.run([c,flag],capture_output=True,text=True,timeout=3);txt=(r.stdout or r.stderr).strip().splitlines();
                    if txt:version=txt[0][:200];break
                except Exception:pass
        rows.append({'command':c,'path':path,'version':version})
    return {'cwd':os.getcwd(),'home':str(Path.home()),'prefix':os.environ.get('PREFIX'),'shell':os.environ.get('SHELL'),'path':os.environ.get('PATH'),'python':os.sys.version.split()[0],'commands':rows}

def git_summary(path='.'):
    root=Path(path).expanduser().resolve()
    if shutil.which('git') is None:raise RuntimeError('git not found')
    def run(*args):
        r=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,timeout=10);return r.stdout.strip() if r.returncode==0 else None
    inside=run('rev-parse','--is-inside-work-tree')
    if inside!='true':return {'path':str(root),'is_git_repository':False}
    status=run('status','--porcelain=v1') or ''
    return {'path':str(root),'is_git_repository':True,'branch':run('branch','--show-current'),'head':run('rev-parse','--short=12','HEAD'),'remote':run('remote','get-url','origin'),'changed_files':len(status.splitlines()) if status else 0,'status':status.splitlines()[:200],'last_commit':run('log','-1','--pretty=%h %ad %s','--date=iso-strict')}

def tcp_check(host,port,timeout=3):
    started=time.perf_counter();err=None
    try:
        with socket.create_connection((host,int(port)),timeout=timeout):ok=True
    except Exception as e:ok=False;err=str(e)
    return {'host':host,'port':int(port),'ok':ok,'latency_ms':round((time.perf_counter()-started)*1000,3),'error':err}

def dns_lookup(host):
    started=time.perf_counter();rows=[]
    try:
        for fam,typ,proto,canon,addr in socket.getaddrinfo(host,None):
            ip=addr[0]
            if ip not in rows:rows.append(ip)
        return {'host':host,'addresses':rows,'latency_ms':round((time.perf_counter()-started)*1000,3)}
    except Exception as e:return {'host':host,'addresses':[],'error':str(e),'latency_ms':round((time.perf_counter()-started)*1000,3)}

def http_info(url,timeout=10):
    if urllib.parse.urlparse(url).scheme not in {'http','https'}:raise ValueError('Only http:// and https:// URLs are supported')
    req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'Language-Project/1'})
    started=time.perf_counter()
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return {'url':r.geturl(),'status':getattr(r,'status',None),'headers':dict(r.headers.items()),'latency_ms':round((time.perf_counter()-started)*1000,3)}
    except Exception as e:return {'url':url,'error':str(e),'latency_ms':round((time.perf_counter()-started)*1000,3)}

def download_file(url,output=None,sha256=None,timeout=30,max_bytes=1024*1024*1024):
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme not in {'http','https'}:raise ValueError('Only http:// and https:// URLs are supported')
    name=Path(parsed.path).name or 'download.bin';out=Path(output).expanduser() if output else DOWNLOADS_DIR/name;out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_name(out.name+'.part')
    h=hashlib.sha256();total=0;started=time.perf_counter()
    req=urllib.request.Request(url,headers={'User-Agent':'Language-Project/1'})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r,tmp.open('wb') as f:
            while True:
                c=r.read(1024*1024)
                if not c:break
                total+=len(c)
                if total>max_bytes:raise ValueError(f'Download exceeded max_bytes={max_bytes}')
                h.update(c);f.write(c)
        digest=h.hexdigest()
        if sha256 and digest.casefold()!=sha256.casefold():raise ValueError(f'SHA-256 mismatch: expected {sha256}, got {digest}')
        tmp.replace(out)
        return {'path':str(out.resolve()),'bytes':total,'sha256':digest,'seconds':round(time.perf_counter()-started,3)}
    except Exception:
        try:tmp.unlink()
        except FileNotFoundError:pass
        raise

def process_list(limit=100):
    cmd=['ps','-A','-o','PID,PPID,USER,STAT,COMMAND']
    try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=5)
    except Exception as e:return {'error':str(e),'rows':[]}
    lines=(r.stdout or '').splitlines();return {'rows':lines[:max(1,limit)],'count':max(0,len(lines)-1),'command':' '.join(cmd)}
