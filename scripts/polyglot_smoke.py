#!/usr/bin/env python3
from pathlib import Path
import json
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.engine import active_languages
from core.polyglot_ops import seal,verify_seal,fingerprint,pack,unpack,verified_copy,directory_audit,verify_directory_audit,protect,restore_protected


def main():
    active=active_languages('registry')
    if not active:
        print('polyglot_smoke.py: SKIP (no verified active workers; run setup first)')
        return 0
    with tempfile.TemporaryDirectory(prefix='language-project-polyglot-smoke-') as td:
        td=Path(td);src=td/'source';(src/'sub').mkdir(parents=True)
        (src/'hello.txt').write_text('Language Project practical polyglot smoke test\n',encoding='utf-8')
        (src/'sub'/'binary.bin').write_bytes(bytes(range(64))+b'\x00\xff')

        seal_path=td/'hello.seal.json'
        s=seal(src/'hello.txt',seal_path,chunk_size=32,warmups=0)
        assert s['languages']==len(active) and s['integrity']
        v=verify_seal(seal_path,src/'hello.txt',warmups=0);assert v['ok']
        fp=fingerprint(src/'hello.txt',chunk_size=32,warmups=0);assert len(fp['polyglot_fingerprint'])==64 and fp['languages']==len(active)

        copied=td/'copied.txt';c=verified_copy(src/'hello.txt',copied,chunk_size=16,warmups=0);assert c['ok'] and copied.read_bytes()==(src/'hello.txt').read_bytes()
        assert c['languages_per_chunk']==len(active)

        pkg=td/'source.lpack';p=pack(src,pkg,chunk_size=64,warmups=0);assert p['ok'] and p['languages']==len(active)
        restored=td/'restored';u=unpack(pkg,restored,warmups=0);assert u['ok']
        assert (restored/'source'/'hello.txt').read_bytes()==(src/'hello.txt').read_bytes()
        assert (restored/'source'/'sub'/'binary.bin').read_bytes()==(src/'sub'/'binary.bin').read_bytes()

        audit_path=td/'audit.json';a=directory_audit(src,audit_path,sample_bytes=32,warmups=0);assert a['integrity'] and a['languages']==len(active)
        av=verify_directory_audit(audit_path,src,warmups=0);assert av['ok']

        protected_dir=td/'protected';receipt=protect(src,protected_dir,label='smoke',chunk_size=64,warmups=0,audit_directory_first=False)
        protected_restore=td/'protected-restored';rr=restore_protected(receipt['package'],protected_restore,warmups=0);assert rr['ok'] and rr['seal_checked']
        assert (protected_restore/'source'/'hello.txt').read_bytes()==(src/'hello.txt').read_bytes()
    print(f'polyglot_smoke.py: PASS ({len(active)} verified languages)')
    return 0

if __name__=='__main__':raise SystemExit(main())
