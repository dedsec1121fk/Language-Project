#!/usr/bin/env python3
from pathlib import Path
import json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.engine import active_languages
from core.polyglot_ops import directory_audit,protect
from core.polyglot_practical import compare_paths,mirror_directory,split_file,join_file,duplicate_report,scrub_from_audit,backup_health

def main():
    active=active_languages('registry')
    if not active:
        print('polyglot_practical_smoke.py: SKIP (no verified active workers; run setup first)');return 0
    with tempfile.TemporaryDirectory(prefix='language-project-practical-polyglot-') as td:
        td=Path(td);src=td/'src';src.mkdir();(src/'a.txt').write_text('alpha\n');(src/'b.bin').write_bytes(bytes(range(100)))
        cmp_same=compare_paths(src/'a.txt',src/'a.txt',warmups=0);assert cmp_same['equal'] and cmp_same['languages']==len(active)
        preview=mirror_directory(src,td/'mirror',apply=False,warmups=0);assert not preview['applied'] and not (td/'mirror').exists()
        applied=mirror_directory(src,td/'mirror',apply=True,warmups=0);assert applied['applied'] and (td/'mirror'/'b.bin').read_bytes()==(src/'b.bin').read_bytes()
        cmp_dirs=compare_paths(src,td/'mirror',warmups=0);assert cmp_dirs['equal']
        parts=split_file(src/'b.bin',td/'parts',part_size=31,warmups=0);joined=join_file(parts['manifest'],td/'joined.bin',warmups=0);assert joined['ok'] and (td/'joined.bin').read_bytes()==(src/'b.bin').read_bytes()
        (src/'dup.bin').write_bytes((src/'b.bin').read_bytes());dups=duplicate_report(src,warmups=0);assert dups['duplicate_groups']>=1
        audit=directory_audit(src,td/'audit.json',warmups=0,verbose=False)
        mirror=td/'trusted';mirror_directory(src,mirror,apply=True,warmups=0)
        (src/'a.txt').write_text('damaged\n')
        scrub=scrub_from_audit(audit['output'],src,mirror,repair=True,warmups=0);assert scrub['ok'] and (src/'a.txt').read_text()=='alpha\n'
        backups=td/'backups';receipt=protect(src,backups,label='health',chunk_size=64,warmups=0,audit_directory_first=False)
        health=backup_health(backups,warmups=0);assert health['ok'] and health['healthy']>=1
    print(f'polyglot_practical_smoke.py: PASS ({len(active)} verified languages)');return 0
if __name__=='__main__':raise SystemExit(main())
