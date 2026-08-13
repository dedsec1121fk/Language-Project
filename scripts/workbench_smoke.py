#!/usr/bin/env python3
from pathlib import Path
import json, sqlite3, tempfile, zipfile, sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core import workbench as w

def main():
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); f=d/'a.txt';f.write_text('beta\nalpha\nbeta\n',encoding='utf-8')
        assert w.chunk_hashes(f,4)['full']
        s=w.checksum_write(f);assert w.checksum_verify(s['sidecar'])['ok']
        z=d/'a.zip';
        with zipfile.ZipFile(z,'w') as x:x.write(f,'a.txt')
        assert w.archive_list(z)['entries']==1
        assert w.base_convert('255',10,16)['result']=='FF'
        assert w.cidr_info('192.168.1.5/24')['network']=='192.168.1.0'
        assert w.url_info('https://example.com/a?x=1')['hostname']=='example.com'
        assert w.regex_test('beta',file=f)['matches']==2
        assert w.word_frequency(f.read_text())['top'][0]['word']=='beta'
        c=d/'x.csv';c.write_text('a,b\n1,2\n',encoding='utf-8');j=d/'x.json';w.csv_to_json(c,j);assert w.json_to_csv(j,d/'back.csv')['rows']==1
        db=d/'x.db';con=sqlite3.connect(db);con.execute('create table t(x)');con.execute('insert into t values (1)');con.commit();con.close();assert w.sqlite_query(db,'select * from t')['rows'][0]['x']==1
        e=d/'.env';e.write_text('A=1\nexport B="two"\n',encoding='utf-8');assert w.env_parse(e)['values']['B']=='two'
        assert w.safe_filename('a:b?.txt')['safe']=='a-b-.txt'
        assert len(w.split_text(f,d/'parts',2)['parts'])==2
        m=d/'merged.txt';w.merge_files([f,f],m);assert m.stat().st_size==f.stat().st_size*2
        a=d/'a.json';b=d/'b.json';a.write_text('{"x":1}');b.write_text('{"x":2}');assert not w.json_diff(a,b)['equal']
    print('Workbench smoke: PASS')
    return 0
if __name__=='__main__':raise SystemExit(main())
