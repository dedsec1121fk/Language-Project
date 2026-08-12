#!/usr/bin/env python3
from pathlib import Path
import json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.langtools import load_state,selftest,workspace_report

def main():
    st=load_state(); active=st.get('active',[])
    if not active:
        print('Native multi-language tools smoke: SKIP (no verified tool state; run setup first)')
        return 0
    r=selftest()
    if not r['ok']:
        print(json.dumps(r,indent=2)); return 2
    with tempfile.TemporaryDirectory(prefix='language-project-langtools-workspace-') as td:
        p=Path(td);(p/'README.md').write_text('# Demo\n\nTODO: example\n',encoding='utf-8');(p/'data.json').write_text('{"ok":true}\n',encoding='utf-8')
        wr=workspace_report(p)
        if wr['tools_executed'] != len(active) or not wr['all_available_tools_executed']:
            print(json.dumps(wr,indent=2)); return 2
    print(f'Native multi-language tools smoke: PASS ({len(active)} tools)')
    return 0
if __name__=='__main__': raise SystemExit(main())
