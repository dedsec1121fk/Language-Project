#!/usr/bin/env python3
from pathlib import Path
import json,sys,re
ROOT=Path(__file__).resolve().parents[1]
errors=[];warnings=[]

def bad(msg): errors.append(msg); print('FAIL',msg)
def ok(msg): print(' OK ',msg)
def warn(msg): warnings.append(msg); print('WARN',msg)

# Root organization policy.
allowed_root_files={'README.md','LICENSE','install.sh','.gitignore','.gitattributes'}
root_files={p.name for p in ROOT.iterdir() if p.is_file()}
unexpected=sorted(root_files-allowed_root_files)
if unexpected: bad('unexpected root files: '+', '.join(unexpected))
else: ok('repository root file set is minimal and organized')
for obsolete in ('Language.py','languages.json','polytools.json','MANIFEST.json','SECURITY.md','CONTRIBUTING.md','uninstall.sh'):
    if (ROOT/obsolete).exists(): bad('obsolete root path still exists: '+obsolete)
for generated in ('build','state','results','bundles'):
    if (ROOT/generated).exists(): bad('generated runtime directory must not live in repository root: '+generated)
ok('generated runtime directories are separated from repository source')

# Registry integrity.
reg_path=ROOT/'config'/'registries'/'languages.json'
tool_path=ROOT/'config'/'registries'/'polytools.json'
try: reg=json.loads(reg_path.read_text())['languages']
except Exception as e: bad('executable registry invalid: '+str(e)); reg=[]
ids=[x.get('id') for x in reg]
if len(ids)!=len(set(ids)): bad('duplicate executable worker IDs')
else: ok(f'{len(reg)} unique executable worker IDs')
for l in reg:
    for key in ('id','name','kind','run','packages'):
        if key not in l: bad(f"{l.get('id','?')}: missing registry field {key}")
    for token in list(l.get('run') or [])+list(l.get('build') or []):
        if isinstance(token,str) and '{root}/' in token:
            rel=token.split('{root}/',1)[1]
            if not (ROOT/rel).exists(): bad(f"{l['id']}: missing project path {rel}")
        if isinstance(token,str) and '{root}/build/' in token:
            bad(f"{l['id']}: generated build path still points into repository source")
ok('worker registry source/build-path audit complete')

# Catalog integrity.
cat_path=ROOT/'catalog'/'known_languages.json'
try: cat=json.loads(cat_path.read_text()); xs=cat.get('languages',[])
except Exception as e: bad('catalog invalid: '+str(e)); cat={}; xs=[]
if cat.get('count')!=len(xs): bad(f"catalog count field {cat.get('count')} != {len(xs)} records")
else: ok(f"catalog count matches: {len(xs):,}")
names=[x.get('name','') for x in xs]
if len({n.casefold() for n in names})!=len(names): bad('case-insensitive duplicate catalog names')
else: ok('catalog names are unique')
slugs=[x.get('slug','') for x in xs]
if len(set(slugs))!=len(slugs): bad('duplicate catalog slugs')
else: ok('catalog slugs are unique')
langmeta_dir=ROOT/'catalog'/'languages'; jsons=list(langmeta_dir.glob('*.json'))
if len(jsons)!=len(xs): bad(f'catalog metadata files {len(jsons)} != records {len(xs)}')
else: ok(f'{len(jsons):,} catalog metadata files present')
for x in xs:
    p=langmeta_dir/(x['slug']+'.json')
    if not p.exists(): bad(f"missing catalog metadata: {p.name}"); continue
    try: y=json.loads(p.read_text())
    except Exception as e: bad(f'{p.name}: invalid JSON: {e}'); continue
    if y.get('name')!=x.get('name'): bad(f'{p.name}: metadata name mismatch')
worker_ids={x.get('worker_id') for x in xs if x.get('termux_worker')}
missing=[x['id'] for x in reg if x.get('id') not in worker_ids]
if missing: bad('registry workers missing from catalog mapping: '+', '.join(missing))
else: ok(f'all {len(reg)} executable workers map into catalog records')

# Full official Termux support overlay in the global catalog.
try:
    sup=json.loads((ROOT/'config'/'registries'/'termux_supported.json').read_text()).get('languages',[])
    covered={mid for row in xs for mid in row.get('termux_modules',[])}
    expected={x.get('id') for x in sup}
    if cat.get('termux_module_count')!=len(sup): bad(f"catalog termux_module_count {cat.get('termux_module_count')} != {len(sup)}")
    if covered!=expected: bad('catalog Termux module overlay mismatch')
    else: ok(f'all {len(sup)} Termux-supported modules are represented in the global catalog')
except Exception as e: bad('full Termux catalog overlay invalid: '+str(e))

# Native practical tools: exactly one per executable worker and co-located with module.
try: tools_doc=json.loads(tool_path.read_text()); tools=tools_doc.get('tools',[])
except Exception as e: bad('native tool registry invalid: '+str(e)); tools=[]; tools_doc={}
if tools_doc.get('count')!=len(tools): bad(f"polytools count field {tools_doc.get('count')} != {len(tools)} records")
tids=[x.get('id') for x in tools]; lids=[x.get('language_id') for x in tools]
if len(tids)!=len(set(tids)): bad('duplicate native tool IDs')
else: ok(f'{len(tools)} unique native tool IDs')
if set(lids)!=set(ids) or len(lids)!=len(ids): bad('native tools do not map exactly one-per executable worker')
else: ok(f'all {len(ids)} executable workers have exactly one native tool')
tool_by={x.get('language_id'):x for x in tools}
for t in tools:
    for key in ('id','language_id','language','name','category','source','run','smoke_args'):
        if key not in t: bad(f"native tool {t.get('id','?')}: missing field {key}")
    src=ROOT/t.get('source','')
    expected_prefix=f"languages/{t.get('language_id')}/tools/"
    if not src.is_file(): bad(f"native tool {t.get('id','?')}: missing source {t.get('source')}")
    if not str(t.get('source','')).startswith(expected_prefix): bad(f"native tool {t.get('id','?')}: source is not co-located under {expected_prefix}")
    for token in list(t.get('run') or [])+list(t.get('build') or []):
        if isinstance(token,str) and '{root}/' in token:
            rel=token.split('{root}/',1)[1]
            if not (ROOT/rel).exists(): bad(f"native tool {t.get('id','?')}: missing project path {rel}")
        if isinstance(token,str) and '{root}/build/' in token:
            bad(f"native tool {t.get('id','?')}: build output still targets repository source")

# Self-contained executable language module audit.
module_file_total=0
for l in reg:
    lid=l['id']; module=ROOT/'languages'/lid; t=tool_by.get(lid)
    required=[
        module/'README.md',module/'metadata.json',module/'examples'/'README.md',
        module/'examples'/'sample-input.txt',module/'examples'/'run-tool.sh',
        module/'examples'/'worker-protocol.txt',module/'tests'/'module.json',
    ]
    for p in required:
        if not p.is_file(): bad(f'{lid}: missing module asset {p.relative_to(ROOT)}')
    try:
        md=json.loads((module/'metadata.json').read_text())
        if md.get('id')!=lid or md.get('name')!=l['name']: bad(f'{lid}: metadata identity mismatch')
        if not t or md.get('native_tool',{}).get('id')!=t.get('id'): bad(f'{lid}: metadata native-tool mapping mismatch')
    except Exception as e: bad(f'{lid}: invalid metadata.json: {e}')
    try:
        sm=json.loads((module/'tests'/'module.json').read_text())
        if sm.get('language_id')!=lid: bad(f'{lid}: tests/module.json language mismatch')
    except Exception as e: bad(f'{lid}: invalid tests/module.json: {e}')
    tool_src=ROOT/t['source'] if t else None
    if tool_src is None or not tool_src.is_file(): bad(f'{lid}: practical tool source missing')
    worker_tokens=' '.join(map(str,(l.get('run') or [])+(l.get('build') or [])))
    if f'{{root}}/languages/{lid}/' not in worker_tokens: bad(f'{lid}: worker source is not module-local')
    module_file_total += sum(1 for p in module.rglob('*') if p.is_file())
if reg: ok(f'{len(reg)} self-contained language modules verified ({module_file_total} module files)')

# Core architecture files.
required_files=[
 'cli/Language.py','core/paths.py','core/human_language.py','core/workbench.py','core/language_modules.py','core/toolbox.py','core/practical.py','core/langtools.py','core/polyglot_ops.py','core/polyglot_practical.py','core/scaffold.py','core/source_runner.py','core/analytics.py','core/profiles.py','core/history.py','core/telemetry.py','core/store.py','core/adaptive.py','core/advanced.py','core/topology.py','core/scenarios.py','core/bundles.py','core/dashboard.py','core/plugins.py','core/provenance.py','core/planner.py','core/regression.py',
 'config/registries/languages.json','config/registries/polytools.json','config/registries/termux_supported.json','config/benchmark_profiles.json','config/scenarios.json','plugins/README.md',
 'metadata/MANIFEST.json','metadata/termux-supported-packages.json','.github/SECURITY.md','.github/CONTRIBUTING.md','scripts/uninstall.sh',
 'scripts/doctor.py','scripts/workbench_smoke.py','scripts/termux_languages.py','scripts/language_balance.py','scripts/termux_coverage_audit.py','scripts/sync_termux_catalog.py','scripts/selftest.py','scripts/module_smoke.py','scripts/langtools_smoke.py','scripts/toolbox_smoke.py','scripts/practical_smoke.py','scripts/polyglot_smoke.py','scripts/polyglot_practical_smoke.py','scripts/package_plan.py','scripts/smoke_benchmark.py','scripts/advanced_smoke.py',
 'data/human/README.md','data/human/PROVENANCE.json','data/human/glottolog/languages.csv','data/human/glottolog/CC-BY-4.0.txt','data/human/glottolog/ATTRIBUTION.txt','data/human/generated/language-vault.sqlite3','data/human/generated/glottolog-index.tsv','data/human/generated/unicode-codepoints.tsv','data/human/generated/translation-matrix.json','scripts/human/verify_language_vault.py','scripts/human/update_language_vault.py','scripts/human_language_smoke.py','docs/human/LANGUAGE_VAULT.md','docs/human/TRANSLATION_AND_BRIDGES.md','docs/human/UNICODE_AND_SCRIPTS.md','docs/human/SYMBOL_LANGUAGE.md','docs/human/OFFLINE_DATA_SOURCES.md','docs/human/TEXT_SECURITY.md','docs/human/OTHER_ENCODINGS.md','schemas/human-language-record.schema.json','schemas/human-script-record.schema.json','schemas/translation-pack.schema.json','examples/human/offline-language-demo.sh','docs/ADVANCED_WORKBENCH.md','docs/TERMUX_LANGUAGE_COVERAGE.md','docs/LANGUAGE_BALANCE.md','docs/USEFUL_TOOLS.md','docs/NATIVE_LANGUAGE_TOOLS.md','docs/PRACTICAL_POLYGLOT.md','docs/POLYGLOT_OPERATIONS.md','docs/STORAGE_LAYOUT.md','docs/LANGUAGE_MODULES.md',
 'examples/useful-demo.sh','examples/everyday-demo.sh','examples/native-tools-demo.sh','examples/polyglot-backup-demo.sh','docs/ADVANCED_MODES.md','docs/ADVANCED_ARCHITECTURE.md','docs/RESULT_SCHEMA.md','docs/PROTOCOL.md','docs/REPRODUCIBILITY.md','docs/DIAGNOSTICS.md','docs/CHECKPOINTS.md','docs/ADAPTIVE_SCHEDULER.md','docs/CHAOS_TESTING.md','docs/TOPOLOGY.md','docs/DATABASE.md','docs/PLUGINS.md','docs/SCENARIOS.md','docs/TELEMETRY.md','docs/BUNDLES.md','docs/REGRESSION_GATES.md','docs/DIFFERENTIAL_AUDIT.md','docs/CONSENSUS.md',
 'schemas/languages.schema.json','schemas/termux-supported.schema.json','schemas/language-module.schema.json','schemas/polytools.schema.json','schemas/polyglot.schema.json','schemas/active-state.schema.json','schemas/catalog.schema.json','schemas/result.schema.json','schemas/calibration.schema.json','schemas/checkpoint.schema.json','schemas/scenarios.schema.json','schemas/provenance.schema.json'
]
missing_required=[x for x in required_files if not (ROOT/x).exists()]
if missing_required: bad('missing architecture files: '+', '.join(missing_required))
else: ok(f'all {len(required_files)} required architecture files present')

# Profile/scenario/schema JSON syntax.
try:
    profiles=json.loads((ROOT/'config'/'benchmark_profiles.json').read_text()).get('profiles',{})
    expected={'quick','showcase','extreme'}
    if not expected<=set(profiles): bad('benchmark profiles missing: '+', '.join(sorted(expected-set(profiles))))
    else: ok('benchmark profiles present: quick, showcase, extreme')
except Exception as e: bad('benchmark profile JSON invalid: '+str(e))
try:
    scenarios=json.loads((ROOT/'config'/'scenarios.json').read_text()).get('scenarios',{})
    expected={'confidence','presentation','resilience'}
    if not expected<=set(scenarios): bad('scenario definitions missing: '+', '.join(sorted(expected-set(scenarios))))
    else: ok('scenario definitions present: confidence, presentation, resilience')
    allowed={'chain','parallel-race','matrix','stress','differential','chaos','topology','consensus'}
    for name,cfg in scenarios.items():
        for step in cfg.get('steps',[]):
            if step.get('type') not in allowed: bad(f"scenario {name}: unsupported step {step.get('type')}")
except Exception as e: bad('scenario JSON invalid: '+str(e))
for schema in (ROOT/'schemas').glob('*.json'):
    try: json.loads(schema.read_text())
    except Exception as e: bad(f'{schema.name}: invalid schema JSON: {e}')
ok('JSON schema syntax audit complete')

# Runtime home policy.
paths_text=(ROOT/'core'/'paths.py').read_text()
if "Path.home() / 'Language Project'" not in paths_text: bad('default runtime home is not $HOME/Language Project')
else: ok('default runtime home is $HOME/Language Project')
installer=(ROOT/'install.sh').read_text()
for token in ('BASE="$HOME/Language Project"','$BASE/state/checkpoints','$BASE/results','$BASE/backups','$BASE/reports','$BASE/cache','$BASE/tmp'):
    if token not in installer: bad('installer storage layout missing token: '+token)
if not any('installer storage layout' in e for e in errors): ok('installer creates the complete Language Project runtime tree')

# README bilingual/collapsible/catalog markers.
readme=(ROOT/'README.md').read_text(encoding='utf-8')
for marker in ('# Language Project — English','# Language Project — Ελληνικά','<!-- LANGUAGE-CATALOG-EN:START -->','<!-- LANGUAGE-CATALOG-EN:END -->','<!-- LANGUAGE-CATALOG-EL:START -->','<!-- LANGUAGE-CATALOG-EL:END -->'):
    if marker not in readme: bad('README missing bilingual/catalog marker: '+marker)
if readme.count('<details>')<70: bad('README does not contain enough collapsible sections')
else: ok(f"README contains {readme.count('<details>')} collapsible sections")
if '$HOME/Language Project/' not in readme: bad('README does not document the persistent Language Project home')
if 'language-project modules verify' not in readme: bad('README does not document module verification')
if 'language-project supported balance' not in readme or 'language-project supported audit' not in readme: bad('README does not document Termux coverage/balance verification')
if 'language-project human status' not in readme or 'language-project human encode codepoints' not in readme or 'language-project human glottolog-search' not in readme or 'language-project human source-literal' not in readme: bad('README does not document the offline human-language vault, Glottolog, and programming bridge')
if 'language-project tools signature' not in readme or 'language-project tools sqlite-query' not in readme: bad('README does not document advanced offline workbench')
if 'config/registries/' not in readme: bad('README does not document organized registry location')
else: ok('README bilingual organization and module/storage documentation present')

# Stale naming and unwanted generated artifacts.
old_name='Flex'+' Project'
text_ext={'.md','.py','.sh','.json','.c','.cpp','.go','.rs','.java','.kt','.scala','.dart','.nim','.zig','.pl','.hs','.d','.f90','.rkt','.cr','.lisp','.tcl','.php','.rb','.js','.lua','.exs','.erl','.scm','.awk','.sed','.jq','.zsh','.fish','.yml','.yaml','.txt'}
stale=[]; generated=[]
for p in ROOT.rglob('*'):
    if not p.is_file(): continue
    rel=p.relative_to(ROOT)
    if '__pycache__' in rel.parts or p.suffix in {'.pyc','.pyo'}: generated.append(rel.as_posix()); continue
    if p.suffix.lower() not in text_ext: continue
    try:t=p.read_text(errors='ignore')
    except Exception: continue
    if old_name in t: stale.append(rel.as_posix())
if stale: bad('previous project name remains in: '+', '.join(stale[:20]))
else: ok('no stale previous-project naming in audited text files')
if generated: bad('generated Python cache files found: '+', '.join(generated[:20]))
else: ok('no generated Python cache files in source tree')

print('\nAudit summary:',len(errors),'error(s),',len(warnings),'warning(s)')
raise SystemExit(1 if errors else 0)
