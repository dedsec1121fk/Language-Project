#!/usr/bin/env python3
from pathlib import Path
import json,sys,re
ROOT=Path(__file__).resolve().parents[1]
errors=[];warnings=[]
def bad(msg): errors.append(msg); print('FAIL',msg)
def ok(msg): print(' OK ',msg)
def warn(msg): warnings.append(msg); print('WARN',msg)
# Registry integrity
reg=json.loads((ROOT/'languages.json').read_text())['languages']
ids=[x['id'] for x in reg]
if len(ids)!=len(set(ids)): bad('duplicate executable worker IDs')
else: ok(f'{len(reg)} unique executable worker IDs')
for l in reg:
    for key in ('id','name','kind','run','packages'):
        if key not in l: bad(f"{l.get('id','?')}: missing registry field {key}")
    # Source paths and build inputs that live in the project must exist.
    for token in list(l.get('run') or [])+list(l.get('build') or []):
        if isinstance(token,str) and '{root}/' in token:
            rel=token.split('{root}/',1)[1]
            # Skip generated build outputs.
            if rel.startswith('build/'): continue
            if not (ROOT/rel).exists(): bad(f"{l['id']}: missing project path {rel}")
ok('registry project-path audit complete')
# Catalog integrity
cat=json.loads((ROOT/'catalog'/'known_languages.json').read_text())
xs=cat.get('languages',[])
if cat.get('count')!=len(xs): bad(f"catalog count field {cat.get('count')} != {len(xs)} records")
else: ok(f"catalog count matches: {len(xs):,}")
names=[x.get('name','') for x in xs]
if len({n.casefold() for n in names})!=len(names): bad('case-insensitive duplicate catalog names')
else: ok('catalog names are unique')
slugs=[x.get('slug','') for x in xs]
if len(set(slugs))!=len(slugs): bad('duplicate catalog slugs')
else: ok('catalog slugs are unique')
langdir=ROOT/'catalog'/'languages'
jsons=list(langdir.glob('*.json'))
if len(jsons)!=len(xs): bad(f'per-language metadata files {len(jsons)} != catalog records {len(xs)}')
else: ok(f'{len(jsons):,} per-language metadata files present')
for x in xs:
    p=langdir/(x['slug']+'.json')
    if not p.exists(): bad(f"missing metadata file for {x['name']}: {p.name}"); continue
    try:y=json.loads(p.read_text())
    except Exception as e: bad(f'{p.name}: invalid JSON: {e}');continue
    if y.get('name')!=x.get('name'): bad(f'{p.name}: metadata name mismatch')
worker_ids={x.get('worker_id') for x in xs if x.get('termux_worker')}
missing=[x['id'] for x in reg if x['id'] not in worker_ids]
if missing: bad('registry workers missing from catalog mapping: '+', '.join(missing))
else: ok(f'all {len(reg)} executable workers map into catalog records')

# Native multi-language practical tool integrity: exactly one useful tool per executable worker candidate.
try:
 pt=json.loads((ROOT/'polytools.json').read_text())
 tools=pt.get('tools',[])
 if pt.get('count')!=len(tools): bad(f"polytools count field {pt.get('count')} != {len(tools)} records")
 tids=[x.get('id') for x in tools]
 if len(tids)!=len(set(tids)): bad('duplicate native language tool IDs')
 else: ok(f'{len(tools)} unique native language tool IDs')
 lids=[x.get('language_id') for x in tools]
 if set(lids)!=set(ids): bad('native language tools do not map exactly one-per executable worker set')
 elif len(lids)!=len(ids): bad('native language tool count differs from executable worker count')
 else: ok(f'all {len(ids)} executable workers have a native practical tool')
 for t in tools:
  for key in ('id','language_id','language','name','category','source','run','smoke_args'):
   if key not in t: bad(f"native tool {t.get('id','?')}: missing field {key}")
  src=ROOT/t.get('source','')
  if not src.is_file(): bad(f"native tool {t.get('id','?')}: missing source {t.get('source')}")
  for token in list(t.get('run') or [])+list(t.get('build') or []):
   if isinstance(token,str) and '{root}/' in token:
    rel=token.split('{root}/',1)[1]
    if rel.startswith('build/'): continue
    if not (ROOT/rel).exists(): bad(f"native tool {t.get('id','?')}: missing project path {rel}")
except Exception as e: bad('native multi-language tool registry invalid: '+str(e))

# Advanced architecture files / profile integrity
required_files=[
 'core/toolbox.py','core/practical.py','core/langtools.py','core/polyglot_ops.py','core/polyglot_practical.py','core/scaffold.py','core/source_runner.py','core/analytics.py','core/profiles.py','core/history.py','core/telemetry.py','core/store.py','core/adaptive.py','core/advanced.py','core/topology.py','core/scenarios.py','core/bundles.py','core/dashboard.py','core/plugins.py','core/provenance.py','core/planner.py','core/regression.py',
 'config/benchmark_profiles.json','config/scenarios.json','polytools.json','plugins/README.md',
 'scripts/doctor.py','scripts/selftest.py','scripts/langtools_smoke.py','scripts/toolbox_smoke.py','scripts/practical_smoke.py','scripts/polyglot_smoke.py','scripts/polyglot_practical_smoke.py','scripts/package_plan.py','scripts/smoke_benchmark.py','scripts/advanced_smoke.py',
 'docs/USEFUL_TOOLS.md','docs/NATIVE_LANGUAGE_TOOLS.md','docs/PRACTICAL_POLYGLOT.md','docs/POLYGLOT_OPERATIONS.md','examples/useful-demo.sh','examples/everyday-demo.sh','examples/native-tools-demo.sh','examples/polyglot-backup-demo.sh','docs/ADVANCED_MODES.md','docs/ADVANCED_ARCHITECTURE.md','docs/RESULT_SCHEMA.md','docs/PROTOCOL.md','docs/REPRODUCIBILITY.md','docs/DIAGNOSTICS.md','docs/CHECKPOINTS.md','docs/ADAPTIVE_SCHEDULER.md','docs/CHAOS_TESTING.md','docs/TOPOLOGY.md','docs/DATABASE.md','docs/PLUGINS.md','docs/SCENARIOS.md','docs/TELEMETRY.md','docs/BUNDLES.md','docs/REGRESSION_GATES.md','docs/DIFFERENTIAL_AUDIT.md','docs/CONSENSUS.md',
 'schemas/languages.schema.json','schemas/polytools.schema.json','schemas/polyglot.schema.json','schemas/active-state.schema.json','schemas/catalog.schema.json','schemas/result.schema.json','schemas/calibration.schema.json','schemas/checkpoint.schema.json','schemas/scenarios.schema.json','schemas/provenance.schema.json'
]
missing_required=[x for x in required_files if not (ROOT/x).exists()]
if missing_required: bad('missing advanced project files: '+', '.join(missing_required))
else: ok(f'all {len(required_files)} advanced architecture files present')
try:
 profiles=json.loads((ROOT/'config'/'benchmark_profiles.json').read_text()).get('profiles',{})
 expected={'quick','showcase','extreme'}
 if not expected<=set(profiles): bad('benchmark profiles missing: '+', '.join(sorted(expected-set(profiles))))
 else: ok('benchmark profiles present: quick, showcase, extreme')
except Exception as e: bad('benchmark profile JSON invalid: '+str(e))
try:
 scenarios=json.loads((ROOT/'config'/'scenarios.json').read_text()).get('scenarios',{})
 expected_scenarios={'confidence','presentation','resilience'}
 if not expected_scenarios<=set(scenarios): bad('scenario definitions missing: '+', '.join(sorted(expected_scenarios-set(scenarios))))
 else: ok('scenario definitions present: confidence, presentation, resilience')
 allowed_steps={'chain','parallel-race','matrix','stress','differential','chaos','topology','consensus'}
 for name,cfg in scenarios.items():
  for step in cfg.get('steps',[]):
   if step.get('type') not in allowed_steps: bad(f"scenario {name}: unsupported step {step.get('type')}")
except Exception as e: bad('scenario JSON invalid: '+str(e))
for schema in (ROOT/'schemas').glob('*.json'):
 try: json.loads(schema.read_text())
 except Exception as e: bad(f'{schema.name}: invalid schema JSON: {e}')
ok('JSON schema syntax audit complete')

# README generated catalog markers / naming audit
readme=(ROOT/'README.md').read_text()
if '<!-- LANGUAGE-CATALOG:START -->' not in readme or '<!-- LANGUAGE-CATALOG:END -->' not in readme: bad('README catalog generation markers missing')
else: ok('README catalog markers present')
if '# Language Project' not in readme: bad('README title is not Language Project')
if '## Advanced Control-Plane Commands' not in readme: bad('README advanced control-plane section missing')
if '## Useful Everyday Tools' not in readme: bad('README useful-toolbox section missing')
if '## Native Multi-Language Tools — Useful Programs Written In The Languages' not in readme: bad('README native multi-language tools section missing')
if '## Practical Polyglot Workflows' not in readme: bad('README practical-polyglot section missing')
if 'Polyglot Mirror — Safe Verified Directory Sync' not in readme: bad('README expanded practical-polyglot section missing')
if readme.count('<details>') < 10: bad('README does not contain the expected collapsible advanced/catalog sections')
else: ok(f"README contains {readme.count('<details>')} collapsible sections")
old_name='Flex'+' Project'
if old_name in readme: bad('README still contains the previous project name')
# Whole-project stale-name scan over text-like sources.
text_ext={'.md','.py','.sh','.json','.c','.cpp','.go','.rs','.java','.kt','.scala','.dart','.nim','.zig','.pl','.hs','.d','.f90','.rkt','.cr','.lisp','.tcl','.php','.rb','.js','.lua','.exs','.erl','.scm','.awk','.sed','.jq','.zsh','.fish'}
stale=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or any(part in {'build','state','results','.git','__pycache__'} for part in p.relative_to(ROOT).parts): continue
    if p.suffix.lower() not in text_ext: continue
    try:t=p.read_text(errors='ignore')
    except Exception: continue
    if old_name in t: stale.append(p.relative_to(ROOT).as_posix())
if stale: bad('previous project name remains in: '+', '.join(stale[:20]))
else: ok('no stale previous-project naming in audited text files')
print('\nAudit summary:',len(errors),'error(s),',len(warnings),'warning(s)')
raise SystemExit(1 if errors else 0)
