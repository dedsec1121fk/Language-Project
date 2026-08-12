from __future__ import annotations
from pathlib import Path
import base64,binascii,bz2,csv,gzip,hashlib,http.server,io,json,lzma,mimetypes,os,re,secrets,shutil,stat,tarfile,time,urllib.parse,uuid,zipfile,zlib
from collections import Counter

PRINTABLE_RE=re.compile(rb'[\x20-\x7e]{4,}')
EXTENSION_PREFERENCE={
    '.py':'Python','.js':'JavaScript','.mjs':'JavaScript','.cjs':'JavaScript','.ts':'TypeScript','.tsx':'TSX','.jsx':'JavaScript',
    '.md':'Markdown','.markdown':'Markdown','.json':'JSON','.yaml':'YAML','.yml':'YAML','.toml':'TOML','.ini':'INI',
    '.sh':'Bash','.bash':'Bash','.zsh':'Shell','.fish':'Fish','.c':'C','.h':'C','.cc':'C++','.cpp':'C++','.cxx':'C++','.hpp':'C++',
    '.rs':'Rust','.go':'Go','.java':'Java','.kt':'Kotlin','.kts':'Kotlin','.rb':'Ruby','.pl':'Perl','.pm':'Perl','.lua':'Lua','.php':'PHP',
    '.html':'HTML','.htm':'HTML','.css':'CSS','.xml':'XML','.sql':'SQL','.dart':'Dart','.swift':'Swift','.scala':'Scala','.r':'R','.jl':'Julia',
    '.hs':'Haskell','.erl':'Erlang','.hrl':'Erlang','.ex':'Elixir','.exs':'Elixir','.nim':'Nim','.zig':'Zig','.d':'D','.f90':'Fortran',
    '.f95':'Fortran','.rkt':'Racket','.lisp':'Common Lisp','.cl':'Common Lisp','.scm':'Scheme','.pro':'Prolog','.awk':'AWK','.tcl':'Tcl'
}


def read_bytes(text=None,file=None):
    if file is not None:
        return Path(file).expanduser().read_bytes()
    if text is not None:
        return text.encode('utf-8')
    import sys
    if not sys.stdin.isatty():
        return sys.stdin.buffer.read()
    return input('Input: ').encode('utf-8')


def write_output(data:bytes,output=None,text_mode=False):
    if output:
        p=Path(output).expanduser();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return str(p)
    if text_mode:
        print(data.decode('utf-8','replace'))
    else:
        import sys;sys.stdout.buffer.write(data);sys.stdout.buffer.flush()
    return None


def codec(data:bytes,fmt:str,decode=False)->bytes:
    f=fmt.lower().replace('_','-')
    if f in {'base64','b64'}:return base64.b64decode(data,validate=True) if decode else base64.b64encode(data)
    if f in {'base32','b32'}:return base64.b32decode(data,casefold=True) if decode else base64.b32encode(data)
    if f in {'base85','b85'}:return base64.b85decode(data) if decode else base64.b85encode(data)
    if f in {'ascii85','a85'}:return base64.a85decode(data) if decode else base64.a85encode(data)
    if f=='hex':return bytes.fromhex(data.decode().strip()) if decode else data.hex().encode()
    if f in {'url','percent'}:
        return urllib.parse.unquote_to_bytes(data.decode()) if decode else urllib.parse.quote_from_bytes(data,safe='').encode()
    if f=='gzip':return gzip.decompress(data) if decode else gzip.compress(data,mtime=0)
    if f=='zlib':return zlib.decompress(data) if decode else zlib.compress(data,9)
    if f=='bz2':return bz2.decompress(data) if decode else bz2.compress(data,9)
    if f in {'xz','lzma'}:return lzma.decompress(data) if decode else lzma.compress(data,preset=9)
    if f=='rot13':
        s=data.decode('utf-8');import codecs;return codecs.decode(s,'rot_13').encode('utf-8')
    raise ValueError(f'Unsupported codec: {fmt}')


def hash_bytes(data:bytes,algorithms=None):
    algorithms=algorithms or ['sha256','sha512','sha1','md5']
    out={}
    for a in algorithms:
        name=a.lower().replace('-','')
        try:out[a]=hashlib.new(name,data).hexdigest()
        except Exception:out[a]=None
    out['crc32']=f'{zlib.crc32(data)&0xffffffff:08x}'
    out['adler32']=f'{zlib.adler32(data)&0xffffffff:08x}'
    return out


def entropy(data:bytes):
    if not data:return 0.0
    import math
    n=len(data);counts=Counter(data)
    return -sum((c/n)*math.log2(c/n) for c in counts.values())


def is_probably_text(data:bytes):
    if not data:return True
    if b'\x00' in data:return False
    sample=data[:65536]
    bad=sum(1 for b in sample if b<9 or (13<b<32))
    return bad/max(1,len(sample))<0.02


def hexdump(data:bytes,width=16,limit=512):
    rows=[];shown=data[:max(0,limit)]
    for off in range(0,len(shown),width):
        chunk=shown[off:off+width]
        hx=' '.join(f'{b:02x}' for b in chunk)
        asc=''.join(chr(b) if 32<=b<127 else '.' for b in chunk)
        rows.append(f'{off:08x}  {hx:<{width*3-1}}  |{asc}|')
    if len(data)>len(shown):rows.append(f'... {len(data)-len(shown):,} more byte(s)')
    return '\n'.join(rows)


def strings(data:bytes,min_length=4,limit=200):
    pat=re.compile(rb'[\x20-\x7e]{%d,}'%max(1,min_length))
    out=[]
    for m in pat.finditer(data):
        out.append({'offset':m.start(),'text':m.group().decode('ascii','replace')})
        if len(out)>=limit:break
    return out


def file_info(path,preview=256):
    p=Path(path).expanduser();st=p.stat();data=p.read_bytes()
    mime,_=mimetypes.guess_type(str(p))
    text=is_probably_text(data)
    info={
        'path':str(p.resolve()),'name':p.name,'bytes':st.st_size,'modified':st.st_mtime,
        'mime_guess':mime or 'application/octet-stream','probably_text':text,'entropy_bits_per_byte':round(entropy(data),6),
        'hashes':hash_bytes(data,['sha256','sha512','blake2b']),
        'permissions':stat.filemode(st.st_mode),
    }
    if text:
        s=data.decode('utf-8','replace');info.update({'lines':0 if not s else s.count('\n')+(0 if s.endswith('\n') else 1),'characters':len(s),'words':len(re.findall(r'\S+',s))})
    info['preview_hex']=hexdump(data,limit=preview)
    return info


def compare_files(a,b):
    pa,pb=Path(a).expanduser(),Path(b).expanduser();ba,bb=pa.read_bytes(),pb.read_bytes()
    first=None
    for i,(x,y) in enumerate(zip(ba,bb)):
        if x!=y:first=i;break
    if first is None and len(ba)!=len(bb):first=min(len(ba),len(bb))
    return {'a':str(pa),'b':str(pb),'equal':ba==bb,'size_a':len(ba),'size_b':len(bb),'first_mismatch_offset':first,'sha256_a':hashlib.sha256(ba).hexdigest(),'sha256_b':hashlib.sha256(bb).hexdigest()}


def duplicate_files(root,min_size=1,algorithm='sha256'):
    root=Path(root).expanduser();groups={}
    by_size={}
    for p in root.rglob('*'):
        try:
            if p.is_file() and not p.is_symlink() and p.stat().st_size>=min_size:by_size.setdefault(p.stat().st_size,[]).append(p)
        except OSError:pass
    for size,paths in by_size.items():
        if len(paths)<2:continue
        for p in paths:
            try:
                h=hashlib.new(algorithm)
                with p.open('rb') as f:
                    for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
                groups.setdefault((size,h.hexdigest()),[]).append(str(p))
            except OSError:pass
    out=[]
    for (size,digest),paths in groups.items():
        if len(paths)>1:out.append({'bytes':size,'hash':digest,'copies':len(paths),'wasted_bytes':size*(len(paths)-1),'paths':paths})
    out.sort(key=lambda x:x['wasted_bytes'],reverse=True);return out


def text_stats(data:bytes):
    s=data.decode('utf-8','replace');words=re.findall(r"[\w'-]+",s.casefold(),flags=re.UNICODE)
    return {'bytes':len(data),'characters':len(s),'lines':0 if not s else s.count('\n')+(0 if s.endswith('\n') else 1),'words':len(words),'unique_words':len(set(words)),'top_words':Counter(words).most_common(20),'entropy_bits_per_byte':round(entropy(data),6),'sha256':hashlib.sha256(data).hexdigest()}


def json_process(data:bytes,mode='pretty',query=None):
    obj=json.loads(data.decode('utf-8'))
    if query:
        cur=obj
        for part in query.split('.'):
            if not part:continue
            if isinstance(cur,list):cur=cur[int(part)]
            elif isinstance(cur,dict):cur=cur[part]
            else:raise KeyError(part)
        obj=cur
    if mode=='validate':return b'VALID JSON\n'
    if mode=='minify':return json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf-8')+b'\n'
    return (json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=False)+'\n').encode('utf-8')


def csv_info(path,delimiter=None,sample_rows=5):
    p=Path(path).expanduser();text=p.read_text(encoding='utf-8-sig',errors='replace')
    sample=text[:65536]
    if delimiter is None:
        try:delimiter=csv.Sniffer().sniff(sample).delimiter
        except Exception:delimiter=','
    rows=list(csv.reader(io.StringIO(text),delimiter=delimiter))
    widths=Counter(len(r) for r in rows)
    return {'path':str(p),'delimiter':delimiter,'rows':len(rows),'columns_max':max((len(r) for r in rows),default=0),'row_widths':dict(sorted(widths.items())),'header':rows[0] if rows else [],'sample':rows[1:1+sample_rows] if len(rows)>1 else []}


def secure_generate(kind='password',length=24,count=1):
    count=max(1,min(count,1000));length=max(1,min(length,1024));out=[]
    alphabet='ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*_-+=' 
    for _ in range(count):
        if kind=='password':out.append(''.join(secrets.choice(alphabet) for _ in range(length)))
        elif kind=='token':out.append(secrets.token_urlsafe(length))
        elif kind=='hex':out.append(secrets.token_hex(length))
        elif kind=='uuid':out.append(str(uuid.uuid4()))
        else:raise ValueError('kind must be password, token, hex, or uuid')
    return out


def manifest_create(root,output=None,algorithm='sha256'):
    root=Path(root).expanduser().resolve();rows=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file():continue
        if output and p.resolve()==Path(output).expanduser().resolve():continue
        h=hashlib.new(algorithm)
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        rows.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,algorithm:h.hexdigest()})
    obj={'schema':1,'root':str(root),'algorithm':algorithm,'created_unix':time.time(),'files':rows}
    target=Path(output).expanduser() if output else root/'LANGUAGE-PROJECT-FILE-MANIFEST.json'
    target.write_text(json.dumps(obj,indent=2)+'\n');return str(target),len(rows)


def manifest_verify(manifest):
    mp=Path(manifest).expanduser();obj=json.loads(mp.read_text());root=Path(obj['root']);algo=obj.get('algorithm','sha256');bad=[]
    if not root.exists():root=mp.parent
    for x in obj.get('files',[]):
        p=root/x['path']
        if not p.exists():bad.append({'path':x['path'],'status':'missing'});continue
        h=hashlib.new(algo)
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        if h.hexdigest()!=x.get(algo):bad.append({'path':x['path'],'status':'hash-mismatch'})
    return {'ok':not bad,'checked':len(obj.get('files',[])),'bad':bad,'root':str(root)}


def archive_create(source,output=None,kind='zip'):
    src=Path(source).expanduser().resolve();kind=kind.lower()
    if output:out=Path(output).expanduser()
    else:out=src.with_suffix('.zip' if kind=='zip' else '.tar.gz')
    out.parent.mkdir(parents=True,exist_ok=True)
    if kind=='zip':
        if src.is_dir() and (out.resolve()==src or src in out.resolve().parents):raise ValueError('Archive output must be outside the source directory')
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            if src.is_file():z.write(src,src.name)
            else:
                for p in src.rglob('*'):
                    if p.is_file() and p.resolve()!=out.resolve():z.write(p,p.relative_to(src.parent))
    elif kind in {'tar.gz','tgz'}:
        if src.is_dir() and (out.resolve()==src or src in out.resolve().parents):raise ValueError('Archive output must be outside the source directory')
        with tarfile.open(out,'w:gz') as t:t.add(src,arcname=src.name,recursive=True)
    else:raise ValueError('kind must be zip or tar.gz')
    return str(out)


def _safe_target(base,name):
    base=base.resolve();target=(base/name).resolve()
    if target!=base and base not in target.parents:raise ValueError(f'Unsafe archive path: {name}')
    return target


def archive_extract(archive,destination=None):
    ap=Path(archive).expanduser().resolve();dest=Path(destination).expanduser() if destination else ap.with_suffix('')
    dest.mkdir(parents=True,exist_ok=True)
    if zipfile.is_zipfile(ap):
        with zipfile.ZipFile(ap) as z:
            for i in z.infolist():_safe_target(dest,i.filename)
            z.extractall(dest)
    elif tarfile.is_tarfile(ap):
        with tarfile.open(ap) as t:
            for m in t.getmembers():_safe_target(dest,m.name)
            if hasattr(tarfile,'data_filter'):t.extractall(dest,filter='data')
            else:t.extractall(dest)
    else:raise ValueError('Unsupported archive format')
    return str(dest)


def storage_report(root,top=20):
    root=Path(root).expanduser();rows=[];total=0;files=0
    for p in root.rglob('*'):
        try:
            if p.is_file() and not p.is_symlink():
                s=p.stat().st_size;total+=s;files+=1;rows.append((s,str(p)))
        except OSError:pass
    rows.sort(reverse=True)
    usage=shutil.disk_usage(root)
    return {'root':str(root.resolve()),'files':files,'tree_bytes':total,'filesystem_total':usage.total,'filesystem_used':usage.used,'filesystem_free':usage.free,'largest':[{'bytes':s,'path':p} for s,p in rows[:max(1,top)]]}


def serve(directory='.',host='127.0.0.1',port=8000):
    d=str(Path(directory).expanduser().resolve())
    handler=lambda *a,**kw:http.server.SimpleHTTPRequestHandler(*a,directory=d,**kw)
    server=http.server.ThreadingHTTPServer((host,port),handler)
    print(f'Serving {d} on http://{host}:{server.server_port}/  (Ctrl+C to stop)')
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


def _catalog_indexes():
    from .catalog import load_catalog
    xs=load_catalog().get('languages',[]);exts={};interpreters={};names={}
    for x in xs:
        for e in x.get('extensions',[]):
            if e:exts.setdefault(e.casefold(),[]).append(x)
        for i in x.get('interpreters',[]):
            if i:interpreters.setdefault(Path(i).name.casefold(),[]).append(x)
        names[x.get('name','').casefold()]=x
    return xs,exts,interpreters,names


def identify_language(path):
    p=Path(path).expanduser();_,exts,interpreters,_=_catalog_indexes();candidates=[];reasons=[]
    try:
        first=p.open('rb').readline(512).decode('utf-8','ignore').strip()
    except Exception:first=''
    if first.startswith('#!'):
        tokens=first[2:].strip().split();interp=Path(tokens[0]).name.casefold() if tokens else ''
        if interp=='env' and len(tokens)>1:interp=Path(tokens[1]).name.casefold()
        if interp in interpreters:
            candidates.extend(interpreters[interp]);reasons.append('shebang:'+interp)
    suffixes=[s.casefold() for s in p.suffixes]
    for ext in sorted(suffixes,key=len,reverse=True):
        if ext in exts:
            candidates.extend(exts[ext]);reasons.append('extension:'+ext)
    # Handle extensionless special filenames represented in aliases/names conservatively.
    if not candidates:
        name=p.name.casefold()
        from .catalog import load_catalog
        for x in load_catalog().get('languages',[]):
            aliases={a.casefold() for a in x.get('aliases',[])}
            if name==x.get('name','').casefold() or name in aliases:
                candidates.append(x);reasons.append('filename/alias:'+p.name)
    uniq={x.get('slug') or x.get('name'):x for x in candidates}
    rows=[]
    for x in uniq.values():
        score=0
        if any(r.startswith('shebang:') for r in reasons) and any(Path(i).name.casefold() in first.casefold() for i in x.get('interpreters',[])):score+=80
        if p.suffix.casefold() in {e.casefold() for e in x.get('extensions',[])}:score+=60
        pref=EXTENSION_PREFERENCE.get(p.suffix.casefold())
        if pref and x.get('name','').casefold()==pref.casefold():score+=35
        if x.get('termux_worker'):score+=2
        rows.append({'name':x.get('name'),'slug':x.get('slug'),'termux_worker':bool(x.get('termux_worker')),'worker_id':x.get('worker_id'),'score':score,'extensions':x.get('extensions',[])[:12]})
    rows.sort(key=lambda x:(-x['score'],x['name'].casefold()))
    return {'path':str(p),'reasons':reasons,'matches':rows,'best':rows[0] if rows else None}


def codebase_stats(root,top=30):
    root=Path(root).expanduser();skip={'.git','.hg','.svn','node_modules','vendor','target','build','dist','__pycache__','.venv','venv'}
    _,exts,_,_=_catalog_indexes();stats={};unknown={'files':0,'bytes':0,'lines':0};total_files=0;total_bytes=0;total_lines=0
    for p in root.rglob('*'):
        if not p.is_file() or any(part in skip for part in p.relative_to(root).parts):continue
        try:data=p.read_bytes()
        except OSError:continue
        total_files+=1;total_bytes+=len(data);lines=data.count(b'\n')+(1 if data and not data.endswith(b'\n') else 0);total_lines+=lines
        matches=exts.get(p.suffix.casefold(),[])
        if matches:
            # Prefer an executable Termux worker only as a deterministic tie-break, not as a detection claim.
            pref=EXTENSION_PREFERENCE.get(p.suffix.casefold())
            preferred=[z for z in matches if pref and z.get('name','').casefold()==pref.casefold()]
            x=(preferred or sorted(matches,key=lambda z:(not z.get('termux_worker'),z.get('name','').casefold())))[0];name=x.get('name','Unknown')
            row=stats.setdefault(name,{'language':name,'files':0,'bytes':0,'lines':0,'termux_worker':bool(x.get('termux_worker'))})
            row['files']+=1;row['bytes']+=len(data);row['lines']+=lines
        else:
            unknown['files']+=1;unknown['bytes']+=len(data);unknown['lines']+=lines
    rows=sorted(stats.values(),key=lambda x:(x['lines'],x['bytes'],x['files']),reverse=True)
    return {'root':str(root.resolve()),'files':total_files,'bytes':total_bytes,'lines':total_lines,'detected_languages':len(rows),'languages':rows[:max(1,top)],'unknown':unknown}
