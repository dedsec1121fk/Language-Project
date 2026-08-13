from __future__ import annotations
from pathlib import Path
import csv, hashlib, ipaddress, json, os, re, sqlite3, stat, tarfile, zipfile
from collections import Counter
from urllib.parse import urlparse, parse_qs, unquote

SIGNATURES = [
    (b'\x89PNG\r\n\x1a\n','PNG image'), (b'\xff\xd8\xff','JPEG image'), (b'GIF87a','GIF image'), (b'GIF89a','GIF image'),
    (b'%PDF-','PDF document'), (b'PK\x03\x04','ZIP/OOXML/JAR archive'), (b'\x1f\x8b\x08','GZIP stream'), (b'BZh','BZIP2 stream'),
    (b'\xfd7zXZ\x00','XZ stream'), (b'7z\xbc\xaf\x27\x1c','7-Zip archive'), (b'Rar!\x1a\x07','RAR archive'),
    (b'\x7fELF','ELF executable/shared object'), (b'MZ','PE/DOS executable'), (b'SQLite format 3\x00','SQLite database'),
    (b'ID3','MP3 with ID3'), (b'OggS','Ogg container'), (b'fLaC','FLAC audio'), (b'RIFF','RIFF container'),
]

def _p(path): return Path(path).expanduser().resolve()
def _hash(name='sha256'): return hashlib.new(name)

def file_signature(path):
    p=_p(path); data=p.read_bytes()[:64]
    found=[name for magic,name in SIGNATURES if data.startswith(magic)]
    if len(data)>=12 and data[4:8]==b'ftyp': found.append('ISO Base Media (MP4/HEIF family)')
    return {'path':str(p),'bytes':p.stat().st_size,'signature':found or ['unknown'],'header_hex':data[:32].hex()}

def chunk_hashes(path,chunk_size=1024*1024,algorithm='sha256'):
    p=_p(path); rows=[]; full=_hash(algorithm); total=0
    with p.open('rb') as f:
        i=0
        while True:
            b=f.read(chunk_size)
            if not b: break
            h=_hash(algorithm);h.update(b);full.update(b);total+=len(b)
            rows.append({'index':i,'offset':i*chunk_size,'bytes':len(b),algorithm:h.hexdigest()});i+=1
    return {'path':str(p),'algorithm':algorithm,'chunk_size':chunk_size,'bytes':total,'chunks':rows,'full':full.hexdigest()}

def checksum_write(path,algorithm='sha256',output=None):
    p=_p(path); h=_hash(algorithm)
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    out=_p(output) if output else p.with_name(p.name+f'.{algorithm}')
    out.write_text(f'{h.hexdigest()}  {p.name}\n',encoding='utf-8')
    return {'file':str(p),'sidecar':str(out),'algorithm':algorithm,'digest':h.hexdigest()}

def checksum_verify(sidecar,file=None):
    s=_p(sidecar); line=s.read_text(encoding='utf-8').strip().splitlines()[0]
    m=re.match(r'^([0-9a-fA-F]+)\s+[* ]?(.*)$',line)
    if not m: raise ValueError('invalid checksum sidecar')
    expected,name=m.groups(); alg={32:'md5',40:'sha1',64:'sha256',128:'sha512'}.get(len(expected))
    if not alg: raise ValueError('cannot infer checksum algorithm')
    p=_p(file) if file else (s.parent/name)
    h=_hash(alg)
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    got=h.hexdigest();return {'file':str(p),'sidecar':str(s),'algorithm':alg,'expected':expected.lower(),'actual':got,'ok':got==expected.lower()}

def archive_list(path,limit=5000):
    p=_p(path); rows=[]
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for x in z.infolist()[:limit]: rows.append({'name':x.filename,'bytes':x.file_size,'compressed':x.compress_size,'dir':x.is_dir()})
        kind='zip'
    elif tarfile.is_tarfile(p):
        with tarfile.open(p,'r:*') as t:
            for x in t.getmembers()[:limit]: rows.append({'name':x.name,'bytes':x.size,'dir':x.isdir(),'type':x.type.decode('latin1') if isinstance(x.type,bytes) else str(x.type)})
        kind='tar'
    else: raise ValueError('unsupported/non-archive file')
    return {'path':str(p),'kind':kind,'entries':len(rows),'items':rows}

def base_convert(value,from_base=10,to_base=16):
    n=int(str(value).strip(),int(from_base)); digits='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if not 2<=int(to_base)<=36: raise ValueError('to_base must be 2..36')
    sign='-' if n<0 else '';n=abs(n)
    if n==0: out='0'
    else:
        parts=[]
        while n: n,r=divmod(n,int(to_base));parts.append(digits[r])
        out=''.join(reversed(parts))
    return {'input':str(value),'from_base':int(from_base),'to_base':int(to_base),'result':sign+out}

def cidr_info(value):
    n=ipaddress.ip_network(value,strict=False)
    hosts=n.num_addresses - (2 if isinstance(n,ipaddress.IPv4Network) and n.prefixlen<=30 else 0)
    return {'input':value,'version':n.version,'network':str(n.network_address),'broadcast':str(n.broadcast_address) if n.version==4 else None,'netmask':str(n.netmask),'hostmask':str(n.hostmask),'prefixlen':n.prefixlen,'addresses':n.num_addresses,'usable_hosts_estimate':max(0,hosts),'first':str(n.network_address),'last':str(n.broadcast_address)}

def url_info(url):
    u=urlparse(url)
    return {'url':url,'scheme':u.scheme,'username':u.username,'hostname':u.hostname,'port':u.port,'path':unquote(u.path),'query':parse_qs(u.query,keep_blank_values=True),'fragment':u.fragment}

def permission_info(value):
    p=Path(value).expanduser()
    if p.exists(): mode=stat.S_IMODE(p.stat().st_mode); source=str(p.resolve())
    else:
        s=str(value).strip().lower();mode=int(s,8) if re.fullmatch(r'[0-7]{3,4}',s) else int(s,0);source='numeric'
    def tri(bits): return ''.join([('r' if bits&4 else '-'),('w' if bits&2 else '-'),('x' if bits&1 else '-')])
    return {'source':source,'octal':format(mode,'04o'),'symbolic':tri((mode>>6)&7)+tri((mode>>3)&7)+tri(mode&7),'owner':tri((mode>>6)&7),'group':tri((mode>>3)&7),'other':tri(mode&7)}

def regex_test(pattern,text=None,file=None,ignore_case=False,multiline=False,max_matches=100):
    src=_p(file).read_text(encoding='utf-8',errors='replace') if file else (text or '')
    flags=(re.I if ignore_case else 0)|(re.M if multiline else 0); rx=re.compile(pattern,flags); rows=[]
    for i,m in enumerate(rx.finditer(src)):
        if i>=max_matches: break
        rows.append({'match':m.group(0),'start':m.start(),'end':m.end(),'groups':list(m.groups()),'groupdict':m.groupdict()})
    return {'pattern':pattern,'matches':len(rows),'items':rows}

def clean_text(text,trim=True,drop_blank=False,dedupe=False,sort=False,casefold_sort=False):
    lines=text.splitlines(); original=len(lines)
    if trim: lines=[x.strip() for x in lines]
    if drop_blank: lines=[x for x in lines if x]
    if dedupe:
        seen=set(); out=[]
        for x in lines:
            if x not in seen: seen.add(x);out.append(x)
        lines=out
    if sort: lines=sorted(lines,key=(str.casefold if casefold_sort else None))
    return {'original_lines':original,'result_lines':len(lines),'text':'\n'.join(lines)+('\n' if lines else '')}

def word_frequency(text,limit=50):
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",text.casefold(),flags=re.UNICODE); c=Counter(words)
    return {'words':len(words),'unique':len(c),'top':[{'word':w,'count':n} for w,n in c.most_common(limit)]}

def ngrams(text,n=2,limit=50,mode='word'):
    units=re.findall(r'[^\W_]+',text.casefold(),flags=re.UNICODE) if mode=='word' else list(text)
    c=Counter(tuple(units[i:i+n]) for i in range(max(0,len(units)-n+1)))
    return {'n':n,'mode':mode,'units':len(units),'top':[{'gram':' '.join(g) if mode=='word' else ''.join(g),'count':k} for g,k in c.most_common(limit)]}

def csv_to_json(path,output=None,delimiter=None):
    p=_p(path)
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        sample=f.read(8192);f.seek(0);d=delimiter or csv.Sniffer().sniff(sample,delimiters=',;\t|').delimiter;rows=list(csv.DictReader(f,delimiter=d))
    text=json.dumps(rows,ensure_ascii=False,indent=2)+'\n'
    if output:_p(output).write_text(text,encoding='utf-8')
    return {'path':str(p),'rows':len(rows),'delimiter':d,'output':str(_p(output)) if output else None,'data':None if output else rows}

def json_to_csv(path,output=None):
    p=_p(path); data=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(data,list) or any(not isinstance(x,dict) for x in data): raise ValueError('JSON must be an array of objects')
    fields=[]
    for row in data:
        for k in row:
            if k not in fields: fields.append(k)
    out=_p(output) if output else p.with_suffix('.csv')
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    return {'path':str(p),'output':str(out),'rows':len(data),'columns':fields}

def sqlite_info(path):
    p=_p(path); con=sqlite3.connect(f'file:{p}?mode=ro',uri=True)
    try:
        rows=con.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE type IN ('table','view','index','trigger') ORDER BY type,name").fetchall()
        objects=[{'type':a,'name':b,'table':c,'sql':d} for a,b,c,d in rows]
        tables=[]
        for o in objects:
            if o['type']=='table' and not o['name'].startswith('sqlite_'):
                try: count=con.execute(f'SELECT COUNT(*) FROM "{o["name"].replace(chr(34),chr(34)*2)}"').fetchone()[0]
                except Exception: count=None
                tables.append({'name':o['name'],'rows':count})
        return {'path':str(p),'objects':objects,'tables':tables,'user_version':con.execute('PRAGMA user_version').fetchone()[0]}
    finally: con.close()

def sqlite_query(path,query,limit=1000):
    q=query.strip(); allowed=('select','pragma','with','explain')
    if not q.casefold().startswith(allowed): raise ValueError('read-only queries only: SELECT/PRAGMA/WITH/EXPLAIN')
    if re.search(r'\b(insert|update|delete|replace|drop|alter|create|attach|detach|vacuum|reindex)\b',q,re.I): raise ValueError('mutating SQL is blocked')
    p=_p(path);con=sqlite3.connect(f'file:{p}?mode=ro',uri=True);con.row_factory=sqlite3.Row
    try:
        cur=con.execute(q); rows=[dict(r) for r in cur.fetchmany(limit)]; cols=[x[0] for x in cur.description] if cur.description else []
        return {'path':str(p),'columns':cols,'rows':rows,'returned':len(rows),'limit':limit}
    finally:con.close()

def env_parse(path):
    p=_p(path); values={}; warnings=[]
    for no,line in enumerate(p.read_text(encoding='utf-8',errors='replace').splitlines(),1):
        s=line.strip()
        if not s or s.startswith('#'): continue
        if s.startswith('export '): s=s[7:].lstrip()
        if '=' not in s: warnings.append({'line':no,'text':line});continue
        k,v=s.split('=',1);k=k.strip();v=v.strip()
        if len(v)>=2 and v[0]==v[-1] and v[0] in "'\"": v=v[1:-1]
        values[k]=v
    return {'path':str(p),'count':len(values),'values':values,'warnings':warnings}

def safe_filename(name,replacement='-',max_length=120):
    x=name.strip().replace(os.sep,replacement)
    if os.altsep:x=x.replace(os.altsep,replacement)
    x=re.sub(r'[\x00-\x1f<>:"|?*]+',replacement,x);x=re.sub(re.escape(replacement)+r'{2,}',replacement,x)
    x=x.strip(' .'+replacement) or 'unnamed';
    if len(x)>max_length:
        stem,suf=os.path.splitext(x);x=stem[:max(1,max_length-len(suf))]+suf[:max_length]
    return {'input':name,'safe':x,'changed':x!=name}

def split_text(path,output_dir=None,lines_per_file=1000,prefix='part'):
    p=_p(path); out=_p(output_dir) if output_dir else p.with_name(p.name+'.parts');out.mkdir(parents=True,exist_ok=True)
    lines=p.read_text(encoding='utf-8',errors='replace').splitlines(True);parts=[]
    for i in range(0,len(lines),lines_per_file):
        q=out/f'{prefix}-{i//lines_per_file:05d}.txt';q.write_text(''.join(lines[i:i+lines_per_file]),encoding='utf-8');parts.append(str(q))
    manifest={'source':str(p),'lines':len(lines),'lines_per_file':lines_per_file,'parts':parts};(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');return manifest

def merge_files(paths,output,separator=''):
    ps=[_p(x) for x in paths]; out=_p(output);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('wb') as w:
        for i,p in enumerate(ps):
            if i and separator:w.write(separator.encode())
            with p.open('rb') as r:
                for b in iter(lambda:r.read(1024*1024),b''):w.write(b)
    return {'output':str(out),'inputs':[str(x) for x in ps],'bytes':out.stat().st_size}

def json_diff(a,b):
    A=json.loads(_p(a).read_text(encoding='utf-8'));B=json.loads(_p(b).read_text(encoding='utf-8'));changes=[]
    def walk(x,y,path='$'):
        if type(x)!=type(y): changes.append({'path':path,'left':x,'right':y,'kind':'type/value'});return
        if isinstance(x,dict):
            for k in sorted(set(x)|set(y)):
                if k not in x: changes.append({'path':path+'.'+k,'kind':'added','right':y[k]})
                elif k not in y: changes.append({'path':path+'.'+k,'kind':'removed','left':x[k]})
                else: walk(x[k],y[k],path+'.'+k)
        elif isinstance(x,list):
            for i in range(max(len(x),len(y))):
                if i>=len(x): changes.append({'path':f'{path}[{i}]','kind':'added','right':y[i]})
                elif i>=len(y): changes.append({'path':f'{path}[{i}]','kind':'removed','left':x[i]})
                else: walk(x[i],y[i],f'{path}[{i}]')
        elif x!=y:changes.append({'path':path,'kind':'changed','left':x,'right':y})
    walk(A,B);return {'left':str(_p(a)),'right':str(_p(b)),'equal':not changes,'changes':changes,'count':len(changes)}
