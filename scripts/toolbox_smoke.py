#!/usr/bin/env python3
from pathlib import Path
import json,tempfile,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.toolbox import codec,hash_bytes,file_info,compare_files,duplicate_files,json_process,text_stats,secure_generate,manifest_create,manifest_verify,archive_create,archive_extract
from core.scaffold import create

def main():
    raw=b'Language Project\x00useful tools\n'
    for fmt in ['base64','base32','base85','ascii85','hex','url','gzip','zlib','bz2','xz']:
        enc=codec(raw,fmt);dec=codec(enc,fmt,True);assert dec==raw,fmt
    assert len(hash_bytes(raw)['sha256'])==64
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);a=d/'a.bin';b=d/'b.bin';a.write_bytes(raw);b.write_bytes(raw)
        assert file_info(a)['bytes']==len(raw);assert compare_files(a,b)['equal'];assert duplicate_files(d)
        j=json_process(b'{"b":2,"a":1}','pretty');assert json.loads(j)=={'b':2,'a':1}
        assert text_stats(b'one two two')['words']==3;assert len(secure_generate('password',16,2))==2
        mp,_=manifest_create(d,d/'manifest.json');assert manifest_verify(mp)['ok']
        zp=archive_create(a,d/'a.zip');out=archive_extract(zp,d/'out');assert (Path(out)/'a.bin').read_bytes()==raw
        sc=create('python','demo',d);assert (Path(sc['path'])/'main.py').exists()
    print('Language Project useful-toolbox smoke test: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
