#!/usr/bin/env python3
from pathlib import Path
import json,tempfile,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.practical import find_files,tree_view,batch_rename,sync_dirs,backup_snapshot,clean_plan,unified_diff,todo_scan,normalize_line_endings,environment_report,git_summary,tcp_check,dns_lookup,process_list

def main():
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);src=d/'src';dst=d/'dst';src.mkdir();dst.mkdir()
        (src/'a.txt').write_text('hello\nTODO: useful\n')
        (src/'b.txt').write_text('world\r\n')
        (src/'same.tmp').write_text('temp')
        (src/'__pycache__').mkdir();(src/'__pycache__'/'x.pyc').write_bytes(b'123')
        r=find_files(src,'*.txt','TODO');assert r['count']==1
        assert 'a.txt' in tree_view(src)
        rr=batch_rename(src,'a.txt',prefix='renamed-');assert not rr['applied'] and (src/'a.txt').exists()
        rr=batch_rename(src,'a.txt',prefix='renamed-',apply=True);assert (src/'renamed-a.txt').exists()
        sy=sync_dirs(src,dst);assert not sy['applied'] and sy['copy_count']>=2
        sy=sync_dirs(src,dst,apply=True,checksum=True);assert (dst/'renamed-a.txt').exists()
        bk=backup_snapshot(src,d/'backups');assert Path(bk['archive']).is_file()
        cp=clean_plan(src,older_days=0);assert any('__pycache__' in x['path'] for x in cp['targets'])
        df=unified_diff(src/'renamed-a.txt',src/'b.txt');assert df.startswith('---')
        todos=todo_scan(src);assert todos['count']==1
        eol=normalize_line_endings(src/'b.txt','lf');assert eol['changed']==1 and not eol['applied']
        eol=normalize_line_endings(src/'b.txt','lf',True);assert (src/'b.txt').read_bytes()==b'world\n'
        env=environment_report(['python']);assert env['commands'][0]['path']
        assert dns_lookup('localhost')['addresses']
        assert isinstance(process_list(5)['rows'],list)
    print('Language Project practical-tools smoke test: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
