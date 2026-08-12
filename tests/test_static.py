from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.analytics import percentile,timing_stats,shannon_entropy
from core.profiles import load_profiles
from core.registry import load_registry
from core.catalog import catalog_stats
from core.scenarios import load_scenarios
from core.provenance import fingerprint
from core.telemetry import ResourceSampler
from core.practical import tree_view,environment_report
from core.polyglot_ops import FORMAT as POLYGLOT_FORMAT,DEFAULT_CHUNK

def main():
    assert percentile([1,2,3,4],50) in (2,3)
    assert timing_stats([100,200,300],1)['p95_ns'] >= 200
    assert round(shannon_entropy(bytes(range(256))),6)==8.0
    reg=load_registry();assert len(reg)>=30;assert len({x['id'] for x in reg})==len(reg)
    profiles=load_profiles()['profiles'];assert all(x in profiles for x in ('quick','showcase','extreme'))
    assert catalog_stats()['termux_workers']==len(reg)
    scenarios=load_scenarios()['scenarios'];assert {'confidence','presentation','resilience'}<=set(scenarios)
    assert len(fingerprint())==64
    assert 'languages/' in tree_view(ROOT,depth=1,max_entries=20)
    assert environment_report(['python'])['commands'][0]['path']
    assert POLYGLOT_FORMAT=='language-project-polyglot' and DEFAULT_CHUNK>=4096
    workflow=(ROOT/'.github/workflows/static-checks.yml').read_text()
    assert 'python -m compileall' not in workflow
    assert 'python scripts/check_python_syntax.py' in workflow
    assert "PYTHONDONTWRITEBYTECODE: '1'" in workflow
    syntax_checker=(ROOT/'scripts/check_python_syntax.py').read_text()
    assert 'ast.parse' in syntax_checker and 'compileall' not in syntax_checker
    sampler=ResourceSampler(interval=0.05).start();import time;time.sleep(0.06);summary=sampler.stop();assert summary['samples']>=1
    print('tests/test_static.py: PASS')
if __name__=='__main__':main()
