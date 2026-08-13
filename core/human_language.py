from __future__ import annotations
from pathlib import Path
import json,re,unicodedata,html,urllib.parse

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'human'
_CACHE={}

def _json(name):
    if name not in _CACHE:
        _CACHE[name]=json.loads((DATA/'generated'/name).read_text(encoding='utf-8'))
    return _CACHE[name]

def status():
    reg=_json('language-registry.json');scr=_json('scripts.json');blk=_json('blocks.json')
    return {
        'offline':True,
        'iana_file_date':reg.get('file_date'),
        'iana_language_records':len(reg.get('languages',[])),
        'iana_script_records':len(reg.get('scripts',[])),
        'iana_region_records':len(reg.get('regions',[])),
        'unicode_version':scr.get('unicode_version'),
        'unicode_script_values':scr.get('count'),
        'unicode_blocks':blk.get('count'),
        'glottolog_languoids':vault_db_stats().get('glottolog',0),
        'bundled_files':[str(p.relative_to(ROOT)) for p in sorted((DATA/'unicode').glob('*')) if p.is_file()],
        'translation_scope':'Exact bundled glossary + reversible Unicode/script/symbol conversions. Not universal semantic machine translation.'
    }

def languages_search(query='',limit=100,include_deprecated=True):
    q=query.casefold().strip(); rows=[]
    for x in _json('language-registry.json')['languages']:
        if not include_deprecated and x.get('deprecated'): continue
        hay=' '.join(str(v) for v in x.values()).casefold()
        if not q or q in hay: rows.append(x)
        if len(rows)>=limit: break
    return rows

def language_show(code):
    c=code.casefold()
    for x in _json('language-registry.json')['languages']:
        if str(x.get('subtag','')).casefold()==c or c in [str(y).casefold() for y in (x.get('description') if isinstance(x.get('description'),list) else [x.get('description')]) if y]:
            return x
    return None

def scripts_list(query='',limit=300):
    q=query.casefold().strip();out=[]
    for x in _json('scripts.json')['scripts']:
        if not q or q in x['name'].casefold() or q in str(x.get('iso15924','')).casefold():out.append(x)
        if len(out)>=limit:break
    return out

def script_show(query):
    q=query.casefold()
    for x in _json('scripts.json')['scripts']:
        if x['name'].casefold()==q or str(x.get('iso15924','')).casefold()==q:return x
    # fuzzy unique
    xs=[x for x in _json('scripts.json')['scripts'] if q in x['name'].casefold()]
    return xs[0] if len(xs)==1 else None

def _ranges(name):
    key='ranges:'+name
    if key in _CACHE:return _CACHE[key]
    out=[]
    for line in (DATA/'unicode'/name).read_text(encoding='utf-8').splitlines():
        z=line.split('#',1)[0].strip()
        if not z or ';' not in z:continue
        a,val=[x.strip() for x in z.split(';',1)]
        if '..' in a:s,e=(int(x,16) for x in a.split('..'))
        else:s=e=int(a,16)
        out.append((s,e,val))
    _CACHE[key]=out;return out

def _range_value(cp,name,default='Unknown'):
    for s,e,v in _ranges(name):
        if s<=cp<=e:return v
    return default

def char_info(ch):
    if len(ch)!=1: raise ValueError('Expected exactly one Unicode character')
    cp=ord(ch)
    try:name=unicodedata.name(ch)
    except ValueError:name='<unassigned or algorithmic name>'
    return {'character':ch,'codepoint':f'U+{cp:04X}','decimal':cp,'utf8_hex':ch.encode('utf-8').hex().upper(),'name':name,'category':unicodedata.category(ch),'combining':unicodedata.combining(ch),'bidirectional':unicodedata.bidirectional(ch),'east_asian_width':unicodedata.east_asian_width(ch),'script':_range_value(cp,'Scripts.txt'),'block':_range_value(cp,'Blocks.txt')}

def unicode_search(query,limit=100):
    q=query.upper().strip();out=[]
    for line in (DATA/'unicode'/'UnicodeData.txt').read_text(encoding='utf-8').splitlines():
        f=line.split(';');
        if len(f)<3:continue
        cp=int(f[0],16);name=f[1]
        if q in name.upper() or q==f'U+{cp:04X}' or q==f'{cp:04X}':
            try:ch=chr(cp)
            except ValueError:ch=''
            out.append({'character':ch,'codepoint':f'U+{cp:04X}','name':name,'category':f[2],'script':_range_value(cp,'Scripts.txt'),'block':_range_value(cp,'Blocks.txt')})
            if len(out)>=limit:break
    return out

def detect_scripts(text):
    counts={}; chars={}
    for ch in text:
        sc=_range_value(ord(ch),'Scripts.txt')
        counts[sc]=counts.get(sc,0)+1
        chars.setdefault(sc,[])
        if len(chars[sc])<24 and ch not in chars[sc]:chars[sc].append(ch)
    total=max(1,len(text))
    rows=[{'script':k,'count':v,'percent':round(v*100/total,3),'sample':''.join(chars[k])} for k,v in counts.items()]
    rows.sort(key=lambda x:(-x['count'],x['script']))
    return {'characters':len(text),'scripts':rows}

def alphabet_chars(script,limit=500,letters_only=True):
    rec=script_show(script)
    if not rec:return {'error':'script not found'}
    out=[]
    for a,b in rec['ranges']:
        s=int(a[2:],16);e=int(b[2:],16)
        for cp in range(s,e+1):
            ch=chr(cp);cat=unicodedata.category(ch)
            if letters_only and not cat.startswith('L'):continue
            try:n=unicodedata.name(ch)
            except ValueError:n=''
            out.append({'char':ch,'codepoint':f'U+{cp:04X}','name':n,'category':cat})
            if len(out)>=limit:return {'script':rec,'characters':out,'truncated':True}
    return {'script':rec,'characters':out,'truncated':False}

def normalize(text,form='NFC'):
    if form not in {'NFC','NFD','NFKC','NFKD'}:raise ValueError('form must be NFC/NFD/NFKC/NFKD')
    return unicodedata.normalize(form,text)

def encode_bridge(text,fmt='codepoints'):
    b=text.encode('utf-8')
    if fmt=='codepoints':return ' '.join(f'U+{ord(c):04X}' for c in text)
    if fmt=='unicode':return ''.join((f'\\u{ord(c):04X}' if ord(c)<=0xFFFF else f'\\U{ord(c):08X}') for c in text)
    if fmt=='hex':return b.hex().upper()
    if fmt=='binary':return ' '.join(f'{x:08b}' for x in b)
    if fmt=='decimal':return ' '.join(str(ord(c)) for c in text)
    if fmt=='html':return ''.join(f'&#x{ord(c):X};' for c in text)
    if fmt=='url':return urllib.parse.quote_from_bytes(b,safe='')
    if fmt=='json':return json.dumps(text,ensure_ascii=True)[1:-1]
    raise ValueError('unknown format')

def decode_bridge(value,fmt='codepoints'):
    if fmt=='codepoints':return ''.join(chr(int(x.replace('U+',''),16)) for x in value.split())
    if fmt=='unicode':return bytes(value,'utf-8').decode('unicode_escape')
    if fmt=='hex':return bytes.fromhex(re.sub(r'\s+','',value)).decode('utf-8')
    if fmt=='binary':return bytes(int(x,2) for x in value.split()).decode('utf-8')
    if fmt=='decimal':return ''.join(chr(int(x)) for x in value.split())
    if fmt=='html':return html.unescape(value)
    if fmt=='url':return urllib.parse.unquote_to_bytes(value).decode('utf-8')
    if fmt=='json':return json.loads('"'+value.replace('"','\\"')+'"')
    raise ValueError('unknown format')

def _symbol_data():
    if 'symbols' not in _CACHE:_CACHE['symbols']=json.loads((DATA/'translation'/'symbols.json').read_text(encoding='utf-8'))['symbols']
    return _CACHE['symbols']

def symbols_describe(text,locale='en',style='brackets'):
    syms=sorted(_symbol_data(),key=lambda x:len(x['symbol']),reverse=True)
    i=0;out=[]
    while i<len(text):
        hit=None
        for x in syms:
            if text.startswith(x['symbol'],i):hit=x;break
        if hit:
            label=hit['labels'].get(locale) or hit['canonical']
            out.append(f'[{label}]' if style=='brackets' else label)
            i+=len(hit['symbol'])
        else:out.append(text[i]);i+=1
    return ''.join(out)

def symbols_parse(text,locale='en'):
    items=[]
    for x in _symbol_data():
        labels=set(x['labels'].values())|{x['canonical']}
        for lab in labels:items.append((lab,x['symbol']))
    items.sort(key=lambda x:len(x[0]),reverse=True)
    out=text
    for lab,sym in items:
        out=re.sub(r'\['+re.escape(lab)+r'\]',lambda m:sym,out,flags=re.I)
    return out

def glossary_status():
    p=json.loads((DATA/'translation'/'phrasebook.json').read_text(encoding='utf-8'))
    return {'languages':p['languages'],'language_count':len(p['languages']),'phrase_count':len(p['phrases']),'scope':p['scope']}

def translate(text,source='en',target='el'):
    p=json.loads((DATA/'translation'/'phrasebook.json').read_text(encoding='utf-8'))
    if source==target:return {'text':text,'translated':text,'source':source,'target':target,'coverage':100.0,'method':'identity'}
    rev={}
    for key,row in p['phrases'].items():
        if source in row:rev[row[source].casefold()]=(key,row)
    # longest phrase/word exact replacement, preserving unknown text
    keys=sorted(rev,key=len,reverse=True);out=text;hits=0
    for src in keys:
        key,row=rev[src]
        if target not in row:continue
        pat=r'(?<!\w)'+re.escape(src)+r'(?!\w)'
        out,n=re.subn(pat,row[target],out,flags=re.I);hits+=n
    return {'text':text,'translated':out,'source':source,'target':target,'matches':hits,'method':'bundled-exact-glossary','note':'Unknown text is preserved. This is not general machine translation.'}

_GREEK={'Α':'A','Β':'V','Γ':'G','Δ':'D','Ε':'E','Ζ':'Z','Η':'I','Θ':'TH','Ι':'I','Κ':'K','Λ':'L','Μ':'M','Ν':'N','Ξ':'X','Ο':'O','Π':'P','Ρ':'R','Σ':'S','Τ':'T','Υ':'Y','Φ':'F','Χ':'CH','Ψ':'PS','Ω':'O','α':'a','β':'v','γ':'g','δ':'d','ε':'e','ζ':'z','η':'i','θ':'th','ι':'i','κ':'k','λ':'l','μ':'m','ν':'n','ξ':'x','ο':'o','π':'p','ρ':'r','σ':'s','ς':'s','τ':'t','υ':'y','φ':'f','χ':'ch','ψ':'ps','ω':'o'}
_CYR={'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'Yo','Ж':'Zh','З':'Z','И':'I','Й':'Y','К':'K','Л':'L','М':'M','Н':'N','О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'Kh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Shch','Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu','Я':'Ya'}
_CYR.update({k.lower():v.lower() for k,v in list(_CYR.items())})
def transliterate(text,mode='ascii'):
    if mode=='greek-latin':return ''.join(_GREEK.get(c,c) for c in text)
    if mode=='cyrillic-latin':return ''.join(_CYR.get(c,c) for c in text)
    if mode=='ascii':return unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode('ascii')
    if mode=='unicode-names':return ' | '.join(unicodedata.name(c,f'U+{ord(c):04X}') for c in text)
    if mode=='codepoints':return encode_bridge(text,'codepoints')
    raise ValueError('mode must be ascii/greek-latin/cyrillic-latin/unicode-names/codepoints')

_MORSE={
'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
'0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',
'.':'.-.-.-',',':'--..--','?':'..--..',"'":'.----.','!':'-.-.--','/':'-..-.','(':'-.--.',')':'-.--.-','&':'.-...',':':'---...',';':'-.-.-.','=':'-...-','+':'.-.-.','-':'-....-','_':'..--.-','"':'.-..-.','$':'...-..-','@':'.--.-.'}
_MORSE_R={v:k for k,v in _MORSE.items()}
def morse(text,decode=False):
    if decode:
        words=[]
        for word in re.split(r'\s*/\s*',text.strip()):
            words.append(''.join(_MORSE_R.get(x,'�') for x in word.split()))
        return ' '.join(words)
    return ' / '.join(' '.join(_MORSE.get(c.upper(),'�') for c in word) for word in text.split(' '))

_BRAILLE_LETTERS={'a':'⠁','b':'⠃','c':'⠉','d':'⠙','e':'⠑','f':'⠋','g':'⠛','h':'⠓','i':'⠊','j':'⠚','k':'⠅','l':'⠇','m':'⠍','n':'⠝','o':'⠕','p':'⠏','q':'⠟','r':'⠗','s':'⠎','t':'⠞','u':'⠥','v':'⠧','w':'⠺','x':'⠭','y':'⠽','z':'⠵',' ':' '}
_BRAILLE_R={v:k for k,v in _BRAILLE_LETTERS.items()}
def braille(text,decode=False):
    if decode:return ''.join(_BRAILLE_R.get(c,'�') for c in text)
    return ''.join(_BRAILLE_LETTERS.get(c.lower(),'�') for c in text)

_NATO={'A':'Alfa','B':'Bravo','C':'Charlie','D':'Delta','E':'Echo','F':'Foxtrot','G':'Golf','H':'Hotel','I':'India','J':'Juliett','K':'Kilo','L':'Lima','M':'Mike','N':'November','O':'Oscar','P':'Papa','Q':'Quebec','R':'Romeo','S':'Sierra','T':'Tango','U':'Uniform','V':'Victor','W':'Whiskey','X':'X-ray','Y':'Yankee','Z':'Zulu','0':'Zero','1':'One','2':'Two','3':'Three','4':'Four','5':'Five','6':'Six','7':'Seven','8':'Eight','9':'Niner'}
def nato(text):return ' '.join(_NATO.get(c.upper(),c) for c in text)

def text_audit(text):
    bidi_controls={0x061C,0x200E,0x200F,*range(0x202A,0x202F),*range(0x2066,0x206A)}
    invisible={0x00AD,0x034F,0x061C,0x180E,0x200B,0x200C,0x200D,0x2060,0xFEFF}
    controls=[];invis=[];bidi=[];combining=[]
    for i,ch in enumerate(text):
        cp=ord(ch);cat=unicodedata.category(ch)
        rec={'index':i,'char':ch,'codepoint':f'U+{cp:04X}','name':unicodedata.name(ch,'<unnamed>')}
        if cat.startswith('C') and ch not in '\n\r\t':controls.append(rec)
        if cp in invisible:invis.append(rec)
        if cp in bidi_controls:bidi.append(rec)
        if unicodedata.combining(ch):combining.append(rec)
    scripts=detect_scripts(text)
    meaningful=[x['script'] for x in scripts['scripts'] if x['script'] not in {'Common','Inherited','Unknown'} and x['count']>0]
    return {'characters':len(text),'utf8_bytes':len(text.encode('utf-8')),'normalization':{f:unicodedata.is_normalized(f,text) for f in ['NFC','NFD','NFKC','NFKD']},'scripts':scripts['scripts'],'mixed_scripts':len(meaningful)>1,'control_characters':controls,'invisible_characters':invis,'bidi_controls':bidi,'combining_marks':combining,'warnings':([f'mixed scripts: {", ".join(meaningful)}'] if len(meaningful)>1 else [])+(['bidirectional control characters present'] if bidi else [])+(['invisible/format characters present'] if invis else [])}

def languages_for_script(script,limit=500):
    rec=script_show(script)
    if not rec:return []
    code=rec.get('iso15924')
    out=[]
    for x in _json('language-registry.json')['languages']:
        if code and x.get('suppress_script')==code:
            out.append(x)
            if len(out)>=limit:break
    return out

def tag_info(tag):
    parts=tag.replace('_','-').split('-');reg=_json('language-registry.json')
    langs={str(x.get('subtag','')).casefold():x for x in reg['languages']}
    scripts={str(x.get('subtag','')).casefold():x for x in reg['scripts']}
    regions={str(x.get('subtag','')).casefold():x for x in reg['regions']}
    variants={str(x.get('subtag','')).casefold():x for x in reg['variants']}
    out={'tag':tag,'valid_structure':bool(parts),'language':None,'script':None,'region':None,'variants':[],'unknown':[]}
    if not parts:return out
    out['language']=langs.get(parts[0].casefold())
    for p in parts[1:]:
        k=p.casefold()
        if len(p)==4 and p.isalpha() and not out['script']:out['script']=scripts.get(k) or {'subtag':p,'unknown':True}
        elif ((len(p)==2 and p.isalpha()) or (len(p)==3 and p.isdigit())) and not out['region']:out['region']=regions.get(k) or {'subtag':p,'unknown':True}
        elif k in variants:out['variants'].append(variants[k])
        elif len(p)==1:out['unknown'].append({'subtag':p,'note':'extension/private-use sequence parsing is not expanded by this lightweight validator'})
        else:out['unknown'].append({'subtag':p})
    out['known_language']=out['language'] is not None
    out['valid']=out['known_language'] and not any(x.get('unknown') for x in [out.get('script') or {},out.get('region') or {}])
    return out


def codepoint_info(value):
    v=str(value).strip()
    if v.upper().startswith('U+'): cp=int(v[2:],16)
    elif v.lower().startswith('0x'): cp=int(v,16)
    elif re.fullmatch(r'[0-9A-Fa-f]{4,8}',v): cp=int(v,16)
    else: cp=int(v,10)
    if not 0 <= cp <= 0x10FFFF or 0xD800 <= cp <= 0xDFFF: raise ValueError('Not a Unicode scalar value')
    return char_info(chr(cp))

def text_from_unicode_names(value):
    # Names are separated by | or newlines so names containing spaces remain intact.
    parts=[x.strip() for x in re.split(r'\s*\|\s*|[\r\n]+',value) if x.strip()]
    out=[]
    for name in parts:
        if re.fullmatch(r'U\+[0-9A-Fa-f]{1,6}',name): out.append(chr(int(name[2:],16))); continue
        out.append(unicodedata.lookup(name.upper()))
    return ''.join(out)

def source_literal_languages():
    return ['json','python','javascript','typescript','java','kotlin','csharp','c','cpp','go','rust','bash','zsh','ruby','php','lua']

def source_literal(text,language='python'):
    lang=language.casefold().replace('++','pp').replace('#','sharp')
    aliases={'js':'javascript','ts':'typescript','c++':'cpp','cs':'csharp','sh':'bash'}
    lang=aliases.get(lang,lang)
    if lang not in source_literal_languages(): raise ValueError('Supported source literal languages: '+', '.join(source_literal_languages()))
    if lang in {'json','python','javascript','typescript','java','kotlin','csharp'}:
        return json.dumps(text,ensure_ascii=True)
    def esc(style):
        o=[]
        for ch in text:
            cp=ord(ch)
            if ch=='\\':o.append('\\\\')
            elif ch=='\"':o.append('\\\"')
            elif ch=='\n':o.append('\\n')
            elif ch=='\r':o.append('\\r')
            elif ch=='\t':o.append('\\t')
            elif 0x20<=cp<0x7F:o.append(ch)
            elif style=='brace':o.append(f'\\u{{{cp:X}}}')
            elif cp<=0xFFFF:o.append(f'\\u{cp:04X}')
            else:o.append(f'\\U{cp:08X}')
        return ''.join(o)
    if lang in {'rust','ruby','php','lua'}:return '"'+esc('brace')+'"'
    if lang in {'bash','zsh'}:return "$'"+esc('fixed').replace("'","\\'")+"'"
    return '"'+esc('fixed')+'"'

def ascii_table():
    p=DATA/'generated'/'ascii-table.tsv'
    rows=[]
    lines=p.read_text(encoding='utf-8').splitlines()
    if not lines:return rows
    headers=lines[0].split('\t')
    for line in lines[1:]: rows.append(dict(zip(headers,line.split('\t'))))
    return rows

def vault_db_stats():
    import sqlite3
    p=DATA/'generated'/'language-vault.sqlite3'
    con=sqlite3.connect(p);c=con.cursor();out={}
    for t in ('languages','scripts','blocks','characters','glottolog'):
        try: out[t]=c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        except Exception: out[t]=0
    out['bytes']=p.stat().st_size;out['path']=str(p.relative_to(ROOT));con.close();return out

def glottolog_search(query='',level=None,limit=100):
    import sqlite3
    q=f'%{query.casefold()}%'
    con=sqlite3.connect(DATA/'generated'/'language-vault.sqlite3');con.row_factory=sqlite3.Row;c=con.cursor()
    sql='SELECT * FROM glottolog WHERE (lower(name) LIKE ? OR lower(glottocode) LIKE ? OR lower(coalesce(iso639p3,\'\')) LIKE ?)'
    args=[q,q,q]
    if level:
        sql+=' AND lower(level)=?';args.append(level.casefold())
    sql+=' ORDER BY level,name LIMIT ?';args.append(int(limit))
    rows=[dict(r) for r in c.execute(sql,args)];con.close();return rows

def glottolog_show(code):
    import sqlite3
    con=sqlite3.connect(DATA/'generated'/'language-vault.sqlite3');con.row_factory=sqlite3.Row;c=con.cursor()
    r=c.execute('SELECT * FROM glottolog WHERE lower(glottocode)=? OR lower(coalesce(iso639p3,\'\'))=? LIMIT 1',(code.casefold(),code.casefold())).fetchone();con.close();return dict(r) if r else None
