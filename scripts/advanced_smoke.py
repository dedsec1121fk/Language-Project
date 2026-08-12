#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.paths import CHECKPOINTS_DIR
from core.engine import active_languages,run_chain
from core.advanced import differential_audit,chaos_test,checkpoint_chain,resume_checkpoint
from core.topology import topology_benchmark,consensus_test


def main():
    if not active_languages():
        print('No active workers. Run: language-project setup --install')
        return 2
    data=b'Language Project advanced smoke'
    results=[]
    results.append(run_chain(data,save=False,verbose=False,rounds=1,warmups=1,telemetry=True))
    results.append(differential_audit(vectors=4,max_size=64,seed=1121,warmups=1,save=False))
    results.append(topology_benchmark(data,lanes=min(3,len(active_languages())),iterations=1,warmups=1,save=False))
    results.append(consensus_test(data,replicas=2,rounds=1,warmups=1,seed=1121,save=False))
    results.append(chaos_test(data,cycles=1,restart_rate=0.05,seed=1121,warmups=1,telemetry=False,save=False))
    cp=CHECKPOINTS_DIR/'advanced-smoke.json'
    try:
        part=checkpoint_chain(data,order='fastest',stop_after=2,checkpoint_path=cp)
        done=resume_checkpoint(cp) if part.get('status')!='complete' else part
        results.append(done)
    finally:
        try:cp.unlink()
        except FileNotFoundError:pass
    ok=all(x.get('integrity',True) for x in results) and all(x.get('status','complete')=='complete' for x in results if x.get('mode')=='checkpoint-chain')
    print('\nLanguage Project advanced smoke:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 2
if __name__=='__main__':raise SystemExit(main())
