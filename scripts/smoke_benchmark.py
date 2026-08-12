#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.engine import active_languages,run_chain,parallel_race,matrix_benchmark,stress_test

def main():
    if not active_languages():
        rc=subprocess.call([sys.executable,str(ROOT/'scripts'/'setup.py')],cwd=ROOT)
        if rc: return rc
    data=b'Language Project smoke benchmark'
    a=run_chain(data,save=False,verbose=False,rounds=1,warmups=1)
    b=parallel_race(data,iterations=2,warmups=1,save=False,max_parallel=4)
    c=matrix_benchmark([16,128],iterations=2,warmups=1,save=False)
    d=stress_test(size=64,cycles=2,warmups=1,seed=1121,save=False)
    ok=all(x.get('integrity') for x in (a,b,c,d))
    print('Language Project smoke benchmark:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 2
if __name__=='__main__':raise SystemExit(main())
