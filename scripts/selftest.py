#!/usr/bin/env python3
from pathlib import Path
import json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.analytics import percentile,timing_stats,shannon_entropy,session_id
from core.profiles import load_profiles
from core.catalog import catalog_stats
from core.scenarios import load_scenarios
from core.provenance import fingerprint
from core.toolbox import codec,hash_bytes,text_stats
from core.scaffold import available as scaffold_languages
from core.langtools import load_tools as load_native_tools
from core.registry import load_registry

def assert_eq(a,b,msg):
    if a!=b:raise AssertionError(f'{msg}: {a!r} != {b!r}')
def main():
    assert_eq(percentile([1,2,3,4,5],50),3,'p50')
    s=timing_stats([1_000_000,2_000_000,3_000_000],1024);assert s['p95_ns']>=s['median_ns'];assert s['throughput_mib_s']>0
    assert_eq(round(shannon_entropy(bytes(range(256))),6),8.0,'entropy')
    assert len(session_id('test',b'x'))==16
    p=load_profiles();assert {'quick','showcase','extreme'}<=set(p['profiles'])
    cs=catalog_stats();assert cs.get('total',0)>1000
    sc=load_scenarios().get('scenarios',{});assert {'confidence','presentation','resilience'}<=set(sc)
    assert len(fingerprint())==64
    raw=b'Language Project useful tools\x00'
    for fmt in ('base64','base32','base85','hex','gzip','zlib','bz2','xz'):
        assert codec(codec(raw,fmt),fmt,True)==raw
    assert len(hash_bytes(raw,['sha256'])['sha256'])==64
    assert text_stats(b'one two two')['words']==3
    assert {'python','c','rust','go'}<=set(scaffold_languages())
    native=load_native_tools(); workers=load_registry(); assert len(native)==len(workers)==34
    assert {x['language_id'] for x in native}=={x['id'] for x in workers}
    assert all((ROOT/x['source']).is_file() for x in native)
    print('Language Project core self-test: PASS')
    print(json.dumps({'catalog':cs,'profiles':list(p['profiles']),'scenarios':list(sc),'environment_fingerprint':fingerprint()},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
