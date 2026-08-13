#!/usr/bin/env python3
from pathlib import Path
import argparse,sys,json,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.engine import run_chain,print_report,active_languages,benchmark_suite,race_workers,load_state,parallel_race,matrix_benchmark,stress_test,showcase
from core.registry import load_registry
from core.catalog import load_catalog,search_catalog,catalog_stats
from core.analytics import device_snapshot
from core.profiles import get_profile,print_profiles
from core.history import print_history,compare_results
from core.adaptive import calibrate,print_calibration
from core.advanced import differential_audit,chaos_test,checkpoint_chain,resume_checkpoint,checkpoint_list
from core.topology import topology_benchmark,consensus_test
from core.scenarios import print_scenarios,run_scenario
from core.store import stats as database_stats,leaderboard as database_leaderboard,recent as database_recent,rebuild as database_rebuild
from core.bundles import create_bundle
from core.dashboard import dashboard
from core.planner import execution_plan,print_plan
from core.regression import check as regression_check,print_check as print_regression
from core.toolbox import read_bytes as tool_read_bytes,write_output as tool_write_output,codec as tool_codec,hash_bytes as tool_hash_bytes,file_info as tool_file_info,strings as tool_strings,hexdump as tool_hexdump,duplicate_files as tool_duplicate_files,text_stats as tool_text_stats,json_process as tool_json_process,csv_info as tool_csv_info,secure_generate as tool_secure_generate,manifest_create as tool_manifest_create,manifest_verify as tool_manifest_verify,archive_create as tool_archive_create,archive_extract as tool_archive_extract,storage_report as tool_storage_report,compare_files as tool_compare_files,serve as tool_serve,identify_language as tool_identify_language,codebase_stats as tool_codebase_stats
from core.practical import find_files as tool_find_files,tree_view as tool_tree_view,batch_rename as tool_batch_rename,sync_dirs as tool_sync_dirs,backup_snapshot as tool_backup_snapshot,clean_plan as tool_clean_plan,unified_diff as tool_unified_diff,todo_scan as tool_todo_scan,normalize_line_endings as tool_normalize_eol,environment_report as tool_environment_report,git_summary as tool_git_summary,tcp_check as tool_tcp_check,dns_lookup as tool_dns_lookup,http_info as tool_http_info,download_file as tool_download_file,process_list as tool_process_list
from core.scaffold import create as scaffold_create,available as scaffold_languages
from core.source_runner import run_source
from core.polyglot_ops import status as polyglot_status,seal as polyglot_seal,verify_seal as polyglot_verify_seal,fingerprint as polyglot_fingerprint,pack as polyglot_pack,unpack as polyglot_unpack,verified_copy as polyglot_copy,directory_audit as polyglot_audit,verify_directory_audit as polyglot_audit_verify,protect as polyglot_protect,restore_protected as polyglot_restore
from core.polyglot_practical import compare_paths as polyglot_compare,mirror_directory as polyglot_mirror,split_file as polyglot_split,join_file as polyglot_join,duplicate_report as polyglot_dedupe,scrub_from_audit as polyglot_scrub,backup_health as polyglot_backup_health
from core.langtools import status as langtools_status,run_tool as langtool_run,recommend as langtool_recommend,project_report as langtool_project_report,file_report as langtool_file_report,data_report as langtool_data_report,auto_report as langtool_auto_report,selftest as langtools_selftest,workspace_report as langtool_workspace_report
from core.language_modules import list_modules,module_info,verify_modules,demo_module
from core.paths import DATA_ROOT, ensure_data_tree
from core.human_language import status as human_status,languages_search as human_languages_search,language_show as human_language_show,scripts_list as human_scripts_list,script_show as human_script_show,char_info as human_char_info,unicode_search as human_unicode_search,detect_scripts as human_detect_scripts,alphabet_chars as human_alphabet_chars,normalize as human_normalize,encode_bridge as human_encode_bridge,decode_bridge as human_decode_bridge,symbols_describe as human_symbols_describe,symbols_parse as human_symbols_parse,glossary_status as human_glossary_status,translate as human_translate,transliterate as human_transliterate,morse as human_morse,braille as human_braille,nato as human_nato,text_audit as human_text_audit,languages_for_script as human_languages_for_script,tag_info as human_tag_info,vault_db_stats as human_vault_db_stats,glottolog_search as human_glottolog_search,glottolog_show as human_glottolog_show,codepoint_info as human_codepoint_info,text_from_unicode_names as human_text_from_unicode_names,source_literal as human_source_literal,source_literal_languages as human_source_literal_languages,ascii_table as human_ascii_table
from core.workbench import file_signature as wb_signature,chunk_hashes as wb_chunk_hashes,checksum_write as wb_checksum_write,checksum_verify as wb_checksum_verify,archive_list as wb_archive_list,base_convert as wb_base_convert,cidr_info as wb_cidr_info,url_info as wb_url_info,permission_info as wb_permission_info,regex_test as wb_regex_test,clean_text as wb_clean_text,word_frequency as wb_word_frequency,ngrams as wb_ngrams,csv_to_json as wb_csv_to_json,json_to_csv as wb_json_to_csv,sqlite_info as wb_sqlite_info,sqlite_query as wb_sqlite_query,env_parse as wb_env_parse,safe_filename as wb_safe_filename,split_text as wb_split_text,merge_files as wb_merge_files,json_diff as wb_json_diff

ORDERS=['registry','fastest','random','adaptive-balanced','adaptive-latency','adaptive-throughput','adaptive-stable']

def banner():print('\n'+'='*92+'\nLANGUAGE PROJECT — TERMUX POLYGLOT EXECUTION + NATIVE TOOLS + BENCHMARK PLATFORM\n'+'='*92)
def ensure():
    if not active_languages():
        print('No verified runtime state found. Running local verification...')
        subprocess.run([sys.executable,str(ROOT/'scripts'/'setup.py')])
def payload(text=None,file=None,prompt='Enter anything: '):
    if file:return Path(file).expanduser().read_bytes()
    return (text if text is not None else input(prompt)).encode()
def show_list():
    ensure();active={x['id'] for x in active_languages()};st=load_state();print(f"\nExecutable registry: {len(load_registry())} | verified here: {len(active)}")
    for l in load_registry():
        status='✓' if l['id'] in active else '·';ver=st.get('versions',{}).get(l['id'],'not verified');reason=st.get('failed',{}).get(l['id'],'')
        print(f" {status} {l['name']:<26} {l['kind']:<12} {(ver if status=='✓' else reason)[:70]}")
def show_catalog(letter=None):
    xs=load_catalog().get('languages',[])
    if letter:xs=[x for x in xs if x.get('letter')==letter.upper()]
    for x in xs:print(('✓ ' if x.get('termux_worker') else '· ')+x['name'])
    print(f'\nShown: {len(xs)}')
def worker_info(query):
    q=query.casefold();matches=[x for x in load_registry() if q in x['id'].casefold() or q in x['name'].casefold()]
    if not matches:print('No executable worker matched:',query);return 1
    st=load_state()
    for l in matches:
        print('\n'+'-'*84);print(l['name']);print('-'*84)
        print(json.dumps({**l,'verified_on_this_device':l['id'] in st.get('active',[]),'version':st.get('versions',{}).get(l['id']),'failure':st.get('failed',{}).get(l['id'])},indent=2))
        src=ROOT/'languages'/l['id']
        if src.exists():
            print('Source files:')
            for f in sorted(src.rglob('*')):
                if f.is_file():print(' ',f.relative_to(ROOT))
    return 0


def useful_toolbox_menu():
    while True:
        print("""
USEFUL TOOLBOX
[1]  Encode / Decode / Compress
[2]  Hash Text Or File
[3]  Inspect File
[4]  Hexdump File
[5]  Extract Printable Strings
[6]  Find Duplicate Files
[7]  Text Statistics
[8]  JSON Pretty / Minify / Validate
[9]  CSV Inspector
[10] Secure Generator
[11] Create File Integrity Manifest
[12] Verify File Integrity Manifest
[13] Create Archive
[14] Extract Archive
[15] Storage Analyzer
[16] Compare Two Files
[17] Local File Server
[18] Identify Programming Language
[19] Codebase Language Statistics
[20] Find Files / Search Contents
[21] Directory Tree
[22] Batch Rename (Preview First)
[23] Directory Sync (Preview First)
[24] Backup Snapshot
[25] Safe Cache Cleanup (Preview First)
[26] Unified Text Diff
[27] TODO / FIXME Scanner
[28] Normalize Line Endings
[29] Environment / Toolchain Report
[30] Git Repository Summary
[31] DNS Lookup
[32] TCP Port Check
[33] HTTP Header / Reachability Check
[34] Download File + Optional SHA-256 Verify
[35] Process List
[36] Advanced Offline Workbench (22 More Tools)
[0]  Back""")
        c=input('\nSelect: ').strip()
        try:
            if c=='0':return
            if c=='1':
                fmt=input('Format (base64/base32/base85/ascii85/hex/url/gzip/zlib/bz2/xz/rot13): ').strip();mode=input('Decode? [y/N]: ').strip().lower().startswith('y');txt=input('Text: ');out=tool_codec(txt.encode(),fmt,mode);print(out.decode('utf-8','replace') if fmt not in {'gzip','zlib','bz2','xz','lzma'} or mode else out.hex())
            elif c=='2':
                x=input('File path, or leave blank for text: ').strip();data=Path(x).expanduser().read_bytes() if x else input('Text: ').encode();print(json.dumps(tool_hash_bytes(data),indent=2))
            elif c=='3':print(json.dumps(tool_file_info(input('File path: ').strip()),indent=2))
            elif c=='4':p=Path(input('File path: ').strip()).expanduser();print(tool_hexdump(p.read_bytes(),limit=1024))
            elif c=='5':p=Path(input('File path: ').strip()).expanduser();[print(f"{x['offset']:08x}  {x['text']}") for x in tool_strings(p.read_bytes())]
            elif c=='6':print(json.dumps(tool_duplicate_files(input('Directory: ').strip()),indent=2))
            elif c=='7':print(json.dumps(tool_text_stats(input('Text: ').encode()),indent=2))
            elif c=='8':print(tool_json_process(input('JSON: ').encode()).decode(),end='')
            elif c=='9':print(json.dumps(tool_csv_info(input('CSV file: ').strip()),indent=2))
            elif c=='10':
                kind=input('password/token/hex/uuid: ').strip() or 'password';print('\n'.join(tool_secure_generate(kind)))
            elif c=='11':print('Created:',tool_manifest_create(input('Directory: ').strip())[0])
            elif c=='12':print(json.dumps(tool_manifest_verify(input('Manifest path: ').strip()),indent=2))
            elif c=='13':print('Created:',tool_archive_create(input('File/directory: ').strip()))
            elif c=='14':print('Extracted:',tool_archive_extract(input('Archive: ').strip()))
            elif c=='15':print(json.dumps(tool_storage_report(input('Directory: ').strip()),indent=2))
            elif c=='16':print(json.dumps(tool_compare_files(input('First file: ').strip(),input('Second file: ').strip()),indent=2))
            elif c=='17':tool_serve(input('Directory [.]: ').strip() or '.')
            elif c=='18':print(json.dumps(tool_identify_language(input('Source file: ').strip()),indent=2))
            elif c=='19':print(json.dumps(tool_codebase_stats(input('Project directory: ').strip()),indent=2))
            elif c=='20':print(json.dumps(tool_find_files(input('Directory: ').strip(),input('Filename glob [*]: ').strip() or '*',input('Content text [optional]: ').strip() or None),indent=2))
            elif c=='21':print(tool_tree_view(input('Directory [.]: ').strip() or '.'))
            elif c=='22':print(json.dumps(tool_batch_rename(input('Directory: ').strip(),input('Glob [*]: ').strip() or '*',input('Find text [optional]: ').strip() or None,input('Replace with: ').strip()),indent=2))
            elif c=='23':print(json.dumps(tool_sync_dirs(input('Source: ').strip(),input('Destination: ').strip()),indent=2))
            elif c=='24':print(json.dumps(tool_backup_snapshot(input('Source: ').strip()),indent=2))
            elif c=='25':print(json.dumps(tool_clean_plan(input('Directory: ').strip()),indent=2))
            elif c=='26':print(tool_unified_diff(input('First text file: ').strip(),input('Second text file: ').strip()))
            elif c=='27':print(json.dumps(tool_todo_scan(input('Project directory: ').strip()),indent=2))
            elif c=='28':print(json.dumps(tool_normalize_eol(input('File/directory: ').strip()),indent=2))
            elif c=='29':print(json.dumps(tool_environment_report(),indent=2))
            elif c=='30':print(json.dumps(tool_git_summary(input('Repository [.]: ').strip() or '.'),indent=2))
            elif c=='31':print(json.dumps(tool_dns_lookup(input('Host: ').strip()),indent=2))
            elif c=='32':print(json.dumps(tool_tcp_check(input('Host: ').strip(),int(input('Port: ').strip())),indent=2))
            elif c=='33':print(json.dumps(tool_http_info(input('URL: ').strip()),indent=2))
            elif c=='34':print(json.dumps(tool_download_file(input('URL: ').strip(),input('Output [optional]: ').strip() or None),indent=2))
            elif c=='35':print(json.dumps(tool_process_list(),indent=2))
            elif c=='36':advanced_workbench_menu()
        except Exception as e:print('Tool error:',e)

def advanced_workbench_menu():
    while True:
        print("""
ADVANCED OFFLINE WORKBENCH
[1] File Signature / Magic Bytes        [12] Word Frequency
[2] Chunk Hashes                        [13] N-grams
[3] Write Checksum Sidecar              [14] CSV -> JSON
[4] Verify Checksum Sidecar             [15] JSON -> CSV
[5] List Archive Contents               [16] SQLite Database Info
[6] Number Base Converter               [17] Read-only SQLite Query
[7] IPv4/IPv6 CIDR Calculator           [18] Parse .env File
[8] URL Parser                          [19] Safe Filename
[9] Unix Permission Decoder             [20] Split Text By Lines
[10] Regex Tester                       [21] Merge Files
[11] Clean / Deduplicate / Sort Text     [22] Structural JSON Diff
[0] Back
""")
        c=input('Select: ').strip()
        try:
            if c=='0': return
            if c=='1': print(json.dumps(wb_signature(input('File: ').strip()),indent=2))
            elif c=='2': print(json.dumps(wb_chunk_hashes(input('File: ').strip()),indent=2))
            elif c=='3': print(json.dumps(wb_checksum_write(input('File: ').strip()),indent=2))
            elif c=='4': print(json.dumps(wb_checksum_verify(input('Sidecar: ').strip()),indent=2))
            elif c=='5': print(json.dumps(wb_archive_list(input('Archive: ').strip()),indent=2))
            elif c=='6': print(json.dumps(wb_base_convert(input('Value: ').strip(),int(input('From base [10]: ').strip() or 10),int(input('To base [16]: ').strip() or 16)),indent=2))
            elif c=='7': print(json.dumps(wb_cidr_info(input('CIDR: ').strip()),indent=2))
            elif c=='8': print(json.dumps(wb_url_info(input('URL: ').strip()),indent=2))
            elif c=='9': print(json.dumps(wb_permission_info(input('Mode or path: ').strip()),indent=2))
            elif c=='10': print(json.dumps(wb_regex_test(input('Regex: ').strip(),text=input('Text: ')),indent=2,ensure_ascii=False))
            elif c=='11': print(wb_clean_text(input('Text: '),dedupe=True)['text'],end='')
            elif c=='12': print(json.dumps(wb_word_frequency(input('Text: ')),indent=2,ensure_ascii=False))
            elif c=='13': print(json.dumps(wb_ngrams(input('Text: ')),indent=2,ensure_ascii=False))
            elif c=='14': print(json.dumps(wb_csv_to_json(input('CSV: ').strip()),indent=2,ensure_ascii=False))
            elif c=='15': print(json.dumps(wb_json_to_csv(input('JSON: ').strip()),indent=2,ensure_ascii=False))
            elif c=='16': print(json.dumps(wb_sqlite_info(input('SQLite DB: ').strip()),indent=2,ensure_ascii=False))
            elif c=='17': print(json.dumps(wb_sqlite_query(input('SQLite DB: ').strip(),input('Read-only SQL: ')),indent=2,ensure_ascii=False))
            elif c=='18': print(json.dumps(wb_env_parse(input('.env file: ').strip()),indent=2,ensure_ascii=False))
            elif c=='19': print(json.dumps(wb_safe_filename(input('Filename: ')),indent=2,ensure_ascii=False))
            elif c=='20': print(json.dumps(wb_split_text(input('Text file: ').strip()),indent=2))
            elif c=='21':
                import shlex
                files=shlex.split(input('Input files: ')); out=input('Output file: ').strip(); print(json.dumps(wb_merge_files(files,out),indent=2))
            elif c=='22':
                r=wb_json_diff(input('First JSON: ').strip(),input('Second JSON: ').strip()); print(json.dumps(r,indent=2,ensure_ascii=False))
        except Exception as e: print('Workbench error:',e)

def run_tools(a):
    if not a.tool_cmd:
        useful_toolbox_menu();return 0
    if a.tool_cmd=='codec':
        data=tool_read_bytes(a.text,a.file);out=tool_codec(data,a.format,a.decode)
        if a.format in {'gzip','zlib','bz2','xz'} and not a.decode and not a.output and not a.raw:
            raise ValueError('Compressed binary output needs --output FILE or --raw')
        tool_write_output(out,a.output,text_mode=not a.raw);return 0
    if a.tool_cmd=='hash':print(json.dumps(tool_hash_bytes(tool_read_bytes(a.text,a.file),a.algorithms),indent=2));return 0
    if a.tool_cmd=='inspect':print(json.dumps(tool_file_info(a.path,a.preview),indent=2));return 0
    if a.tool_cmd=='hexdump':print(tool_hexdump(Path(a.path).expanduser().read_bytes(),a.width,a.limit));return 0
    if a.tool_cmd=='strings':
        for x in tool_strings(Path(a.path).expanduser().read_bytes(),a.min_length,a.limit):print(f"{x['offset']:08x}  {x['text']}")
        return 0
    if a.tool_cmd=='duplicates':print(json.dumps(tool_duplicate_files(a.root,a.min_size,a.algorithm),indent=2));return 0
    if a.tool_cmd=='text-stats':print(json.dumps(tool_text_stats(tool_read_bytes(a.text,a.file)),indent=2));return 0
    if a.tool_cmd=='json':tool_write_output(tool_json_process(tool_read_bytes(a.text,a.file),a.mode,a.query),a.output,True);return 0
    if a.tool_cmd=='csv':print(json.dumps(tool_csv_info(a.path,a.delimiter,a.sample),indent=2));return 0
    if a.tool_cmd=='generate':print('\n'.join(tool_secure_generate(a.kind,a.length,a.count)));return 0
    if a.tool_cmd=='manifest-create':p,n=tool_manifest_create(a.root,a.output,a.algorithm);print(f'Created {p} with {n} files');return 0
    if a.tool_cmd=='manifest-verify':r=tool_manifest_verify(a.manifest);print(json.dumps(r,indent=2));return 0 if r['ok'] else 2
    if a.tool_cmd=='archive-create':print(tool_archive_create(a.source,a.output,a.kind));return 0
    if a.tool_cmd=='archive-extract':print(tool_archive_extract(a.archive,a.destination));return 0
    if a.tool_cmd=='storage':print(json.dumps(tool_storage_report(a.root,a.top),indent=2));return 0
    if a.tool_cmd=='compare':r=tool_compare_files(a.a,a.b);print(json.dumps(r,indent=2));return 0 if r['equal'] else 1
    if a.tool_cmd=='serve':tool_serve(a.directory,a.host,a.port);return 0
    if a.tool_cmd=='identify':print(json.dumps(tool_identify_language(a.path),indent=2));return 0
    if a.tool_cmd=='codebase':print(json.dumps(tool_codebase_stats(a.root,a.top),indent=2));return 0
    if a.tool_cmd=='find':print(json.dumps(tool_find_files(a.root,a.pattern,a.content,a.regex,a.case_sensitive,a.hidden,a.max_results),indent=2));return 0
    if a.tool_cmd=='tree':print(tool_tree_view(a.root,a.depth,a.max_entries,a.hidden));return 0
    if a.tool_cmd=='rename':print(json.dumps(tool_batch_rename(a.root,a.glob,a.find,a.replace,a.prefix,a.suffix,a.apply),indent=2));return 0
    if a.tool_cmd=='sync':print(json.dumps(tool_sync_dirs(a.source,a.destination,a.delete,a.apply,a.checksum),indent=2));return 0
    if a.tool_cmd=='backup':print(json.dumps(tool_backup_snapshot(a.source,a.destination,a.label),indent=2));return 0
    if a.tool_cmd=='clean':print(json.dumps(tool_clean_plan(a.root,a.older_days,a.apply),indent=2));return 0
    if a.tool_cmd=='diff':print(tool_unified_diff(a.a,a.b,a.context));return 0
    if a.tool_cmd=='todos':print(json.dumps(tool_todo_scan(a.root,a.max_results),indent=2));return 0
    if a.tool_cmd=='eol':print(json.dumps(tool_normalize_eol(a.path,a.mode,a.apply),indent=2));return 0
    if a.tool_cmd=='env':print(json.dumps(tool_environment_report(a.commands),indent=2));return 0
    if a.tool_cmd=='git':print(json.dumps(tool_git_summary(a.path),indent=2));return 0
    if a.tool_cmd=='dns':print(json.dumps(tool_dns_lookup(a.host),indent=2));return 0
    if a.tool_cmd=='tcp':r=tool_tcp_check(a.host,a.port,a.timeout);print(json.dumps(r,indent=2));return 0 if r['ok'] else 1
    if a.tool_cmd=='http':r=tool_http_info(a.url,a.timeout);print(json.dumps(r,indent=2));return 0 if 'error' not in r else 1
    if a.tool_cmd=='download':print(json.dumps(tool_download_file(a.url,a.output,a.sha256,a.timeout,a.max_bytes),indent=2));return 0
    if a.tool_cmd=='processes':print(json.dumps(tool_process_list(a.limit),indent=2));return 0
    if a.tool_cmd=='signature':print(json.dumps(wb_signature(a.path),indent=2));return 0
    if a.tool_cmd=='chunk-hash':print(json.dumps(wb_chunk_hashes(a.path,a.chunk_size,a.algorithm),indent=2));return 0
    if a.tool_cmd=='checksum-write':print(json.dumps(wb_checksum_write(a.path,a.algorithm,a.output),indent=2));return 0
    if a.tool_cmd=='checksum-verify':r=wb_checksum_verify(a.sidecar,a.file);print(json.dumps(r,indent=2));return 0 if r['ok'] else 2
    if a.tool_cmd=='archive-list':print(json.dumps(wb_archive_list(a.path,a.limit),indent=2));return 0
    if a.tool_cmd=='base':print(json.dumps(wb_base_convert(a.value,a.from_base,a.to_base),indent=2));return 0
    if a.tool_cmd=='cidr':print(json.dumps(wb_cidr_info(a.value),indent=2));return 0
    if a.tool_cmd=='url-info':print(json.dumps(wb_url_info(a.url),indent=2));return 0
    if a.tool_cmd=='permissions':print(json.dumps(wb_permission_info(a.value),indent=2));return 0
    if a.tool_cmd=='regex-test':print(json.dumps(wb_regex_test(a.pattern,a.text,a.file,a.ignore_case,a.multiline,a.max_matches),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='clean-text':
        txt=tool_read_bytes(a.text,a.file).decode('utf-8','replace');r=wb_clean_text(txt,not a.no_trim,a.drop_blank,a.dedupe,a.sort,a.casefold_sort)
        if a.output:Path(a.output).expanduser().write_text(r['text'],encoding='utf-8');print('Written:',Path(a.output).expanduser())
        else:sys.stdout.write(r['text'])
        return 0
    if a.tool_cmd=='word-frequency':print(json.dumps(wb_word_frequency(tool_read_bytes(a.text,a.file).decode('utf-8','replace'),a.limit),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='ngrams':print(json.dumps(wb_ngrams(tool_read_bytes(a.text,a.file).decode('utf-8','replace'),a.n,a.limit,a.mode),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='csv-to-json':print(json.dumps(wb_csv_to_json(a.path,a.output,a.delimiter),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='json-to-csv':print(json.dumps(wb_json_to_csv(a.path,a.output),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='sqlite-info':print(json.dumps(wb_sqlite_info(a.path),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='sqlite-query':print(json.dumps(wb_sqlite_query(a.path,a.query,a.limit),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='env-parse':print(json.dumps(wb_env_parse(a.path),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='safe-name':print(json.dumps(wb_safe_filename(a.name,a.replacement,a.max_length),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='text-split':print(json.dumps(wb_split_text(a.path,a.output_dir,a.lines_per_file,a.prefix),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='merge-files':print(json.dumps(wb_merge_files(a.paths,a.output,a.separator),indent=2,ensure_ascii=False));return 0
    if a.tool_cmd=='json-diff':r=wb_json_diff(a.a,a.b);print(json.dumps(r,indent=2,ensure_ascii=False));return 0 if r['equal'] else 1
    return 0

def practical_polyglot_menu():
    while True:
        print("""
PRACTICAL POLYGLOT WORKFLOWS — EVERY VERIFIED LANGUAGE PARTICIPATES
[1]  Status / Active Language Set
[2]  Seal A File With All Languages
[3]  Verify A Polyglot Seal
[4]  Create Polyglot Fingerprint
[5]  Pack File/Folder Into .lpack
[6]  Unpack / Restore .lpack
[7]  Full-Language Verified File Copy
[8]  Audit A Directory With All Languages
[9]  Verify Directory Polyglot Audit
[10] Protect / Backup In One Command
[11] Verify + Restore Protected Backup
[12] Compare Files / Directories With All Languages
[13] Mirror Directory (Dry-Run First)
[14] Split Large File Into Polyglot Parts
[15] Join / Restore Polyglot Parts
[16] Confirm Duplicate Files With All Languages
[17] Scrub / Repair From Audit + Trusted Mirror
[18] Check Protected Backup Health
[0]  Back

Note: .lpack and language transforms are reversible encoding, NOT encryption.
""")
        c=input('Select: ').strip()
        try:
            if c=='0':return
            if c=='1':print(json.dumps(polyglot_status(),indent=2))
            elif c=='2':print(json.dumps(polyglot_seal(input('File: ').strip()),indent=2))
            elif c=='3':print(json.dumps(polyglot_verify_seal(input('Seal manifest: ').strip(),input('File override [optional]: ').strip() or None),indent=2))
            elif c=='4':print(json.dumps(polyglot_fingerprint(input('File: ').strip()),indent=2))
            elif c=='5':print(json.dumps(polyglot_pack(input('File/folder: ').strip()),indent=2))
            elif c=='6':print(json.dumps(polyglot_unpack(input('.lpack file: ').strip()),indent=2))
            elif c=='7':print(json.dumps(polyglot_copy(input('Source file: ').strip(),input('Destination file: ').strip()),indent=2))
            elif c=='8':print(json.dumps(polyglot_audit(input('Directory: ').strip()),indent=2))
            elif c=='9':print(json.dumps(polyglot_audit_verify(input('Audit manifest: ').strip(),input('Directory override [optional]: ').strip() or None),indent=2))
            elif c=='10':print(json.dumps(polyglot_protect(input('File/folder: ').strip(),input('Backup directory [optional]: ').strip() or None),indent=2))
            elif c=='11':print(json.dumps(polyglot_restore(input('.lpack file: ').strip(),input('Restore directory [optional]: ').strip() or None),indent=2))
            elif c=='12':print(json.dumps(polyglot_compare(input('Left path: ').strip(),input('Right path: ').strip()),indent=2))
            elif c=='13':
                src=input('Source directory: ').strip();dst=input('Destination directory: ').strip();apply=input('Apply changes? [y/N]: ').strip().lower().startswith('y');print(json.dumps(polyglot_mirror(src,dst,apply=apply),indent=2))
            elif c=='14':print(json.dumps(polyglot_split(input('Large file: ').strip(),input('Output directory [optional]: ').strip() or None),indent=2))
            elif c=='15':print(json.dumps(polyglot_join(input('LANGUAGE-PARTS.json: ').strip(),input('Destination file [optional]: ').strip() or None),indent=2))
            elif c=='16':print(json.dumps(polyglot_dedupe(input('Directory: ').strip()),indent=2))
            elif c=='17':
                man=input('Audit manifest: ').strip();root=input('Directory override [optional]: ').strip() or None;mirror=input('Trusted mirror [optional]: ').strip() or None;repair=input('Repair from mirror? [y/N]: ').strip().lower().startswith('y');print(json.dumps(polyglot_scrub(man,root,mirror,repair),indent=2))
            elif c=='18':print(json.dumps(polyglot_backup_health(input('Backup directory: ').strip()),indent=2))
        except Exception as e:print('Polyglot workflow error:',e)

def native_language_tools_menu():
    while True:
        st=langtools_status()
        print(f"""
NATIVE MULTI-LANGUAGE TOOLS — REAL UTILITIES WRITTEN IN DIFFERENT LANGUAGES
Available now: {st['available']}/{st['registered']}

[1]  List Tools + Language
[2]  Run A Native Tool
[3]  Recommend Tools For A Task
[4]  Project Report (Multiple Languages)
[5]  File Report (Multiple Languages)
[6]  Data Report (JSON/CSV/Logs/etc.)
[7]  Auto Report
[8]  Self-Test Available Native Tools
[9]  Workspace Report (Uses Every Available Native Tool)
[0]  Back
""")
        c=input('Select: ').strip()
        try:
            if c=='0': return
            if c=='1':
                for x in st['tools']:
                    mark='✓' if x['available'] else '·'
                    print(f" {mark} {x['id']:<22} {x['language']:<14} {x['name']}")
            elif c=='2':
                tid=input('Tool ID: ').strip(); raw=input('Arguments (space separated): ').strip(); import shlex
                r=langtool_run(tid,shlex.split(raw)); print(r['stdout'],end='');
                if r['stderr']: print(r['stderr'],file=sys.stderr,end='')
                print(f"\nExit code: {r['returncode']}")
            elif c=='3':
                q=input('What do you want to do? ').strip()
                for x in langtool_recommend(q): print(f"{'✓' if x['available'] else '·'} {x['id']:<22} {x['language']:<14} {x['name']}")
            elif c=='4': print(json.dumps(langtool_project_report(input('Project directory: ').strip()),indent=2))
            elif c=='5': print(json.dumps(langtool_file_report(input('File: ').strip()),indent=2))
            elif c=='6': print(json.dumps(langtool_data_report(input('Data file: ').strip()),indent=2))
            elif c=='7': print(json.dumps(langtool_auto_report(input('Path: ').strip()),indent=2))
            elif c=='8': print(json.dumps(langtools_selftest(),indent=2))
            elif c=='9': print(json.dumps(langtool_workspace_report(input('Project directory: ').strip()),indent=2))
        except Exception as e: print('Native tool error:',e)

def interactive():
    banner();ensure()
    while True:
        print('''
[1]  Run Full Language Chain
[2]  Run File Chain
[3]  Parallel Language Race
[4]  Multi-size Performance Matrix
[5]  Stress / Endurance Chain
[6]  Full Showcase Session
[7]  Differential Worker Audit
[8]  Chaos / Worker-Restart Test
[9]  Braided Topology Lab
[10] Multi-order Consensus Test
[11] Adaptive Device Calibration
[12] Resumable Checkpoint Chain
[13] Control Plane Dashboard
[14] Executable Language Status
[15] Global Catalog Stats / Search
[16] Benchmark Profiles
[17] Scenario Runner
[18] Device Snapshot
[19] Result History / Compare
[20] SQLite Performance Database
[21] Doctor / Self-test
[22] Install / Re-detect Everything
[23] Refresh Global Catalog
[24] Termux Package Plan
[25] Create Result Bundle
[26] Execution Plan / Dry Run
[27] Performance Regression Gate
[28] Useful Offline Toolbox
[29] Create Starter Project
[30] Execute Trusted Source File
[31] Practical Polyglot Workflows (Uses Every Verified Language)
[32] Native Tools Written Across 34 Languages
[33] Language Module Browser / Verification
[34] Show Language Project Home
[0]  Exit''')
        c=input('\nSelect: ').strip()
        if c=='0':return
        if c=='1':
            text=input('\nEnter anything: ');r=run_chain(text.encode(),telemetry=True);print_report(r,text)
        elif c=='2':
            p=Path(input('File path: ').strip()).expanduser();r=run_chain(p.read_bytes(),telemetry=True);print_report(r,str(p))
        elif c=='3':parallel_race(input('Race payload: ').encode())
        elif c=='4':matrix_benchmark()
        elif c=='5':stress_test()
        elif c=='6':showcase(input('Showcase payload: ').encode(),get_profile('showcase'))
        elif c=='7':differential_audit()
        elif c=='8':chaos_test(input('Chaos payload: ').encode())
        elif c=='9':topology_benchmark(input('Topology payload: ').encode())
        elif c=='10':consensus_test(input('Consensus payload: ').encode())
        elif c=='11':calibrate();print_calibration('balanced')
        elif c=='12':checkpoint_chain(input('Checkpoint payload: ').encode())
        elif c=='13':dashboard()
        elif c=='14':show_list()
        elif c=='15':
            print(json.dumps(catalog_stats(),indent=2));q=input('Search (blank to return): ').strip()
            if q:
                xs=search_catalog(q);[print(('✓ ' if x.get('termux_worker') else '· ')+x['name']) for x in xs[:250]];print('Matches:',len(xs))
        elif c=='16':print_profiles()
        elif c=='17':print_scenarios();name=input('Scenario name: ').strip();run_scenario(name,input('Scenario payload: ').encode())
        elif c=='18':print(json.dumps(device_snapshot(),indent=2))
        elif c=='19':
            print_history(20)
            try:compare_results()
            except Exception as e:print('Compare:',e)
        elif c=='20':print(json.dumps(database_stats(),indent=2))
        elif c=='21':subprocess.run([sys.executable,str(ROOT/'scripts'/'doctor.py')])
        elif c=='22':subprocess.run([sys.executable,str(ROOT/'scripts'/'setup.py'),'--install','--refresh-catalog'])
        elif c=='23':subprocess.run([sys.executable,str(ROOT/'scripts'/'refresh_catalog.py')])
        elif c=='24':subprocess.run([sys.executable,str(ROOT/'scripts'/'package_plan.py')])
        elif c=='25':print('Bundle:',create_bundle())
        elif c=='26':print_plan(execution_plan(0,1,'fastest'))
        elif c=='27':print_regression(regression_check())
        elif c=='28':useful_toolbox_menu()
        elif c=='29':
            print('Templates:',', '.join(scaffold_languages()));lang=input('Language: ').strip();name=input('Project name: ').strip();print(json.dumps(scaffold_create(lang,name),indent=2))
        elif c=='30':
            src=input('Source file: ').strip();r=run_source(src);sys.stdout.buffer.write(r['stdout']);sys.stderr.buffer.write(r['stderr']);print(f'\nExit code: {r["returncode"]}')
        elif c=='31':practical_polyglot_menu()
        elif c=='32':native_language_tools_menu()
        elif c=='33':
            rows=list_modules();[print(f"{'✓' if x['worker_verified'] else '·'} {x['id']:<14} {x['name']:<22} tool={'✓' if x['tool_verified'] else '·'} {x['tool_name']}") for x in rows];q=input('Module ID for details/demo (blank to return): ').strip();
            if q:
                print(json.dumps(module_info(q),indent=2,ensure_ascii=False));run=input('Run native-tool demo? [y/N]: ').strip().lower();
                if run.startswith('y'):print(json.dumps(demo_module(q),indent=2,ensure_ascii=False))
        elif c=='34':ensure_data_tree();print(DATA_ROOT)

def main():
    ap=argparse.ArgumentParser(description='Language Project — verified Termux polyglot execution, native multi-language utilities, practical workflows, resilience, benchmarking, and a global language catalog.')
    sp=ap.add_subparsers(dest='cmd')
    p=sp.add_parser('run');p.add_argument('--text');p.add_argument('--file');p.add_argument('--rounds',type=int,default=1);p.add_argument('--warmups',type=int,default=1);p.add_argument('--order',choices=ORDERS,default='fastest');p.add_argument('--seed',type=int);p.add_argument('--telemetry',action='store_true')
    sp.add_parser('list');s=sp.add_parser('setup');s.add_argument('--install',action='store_true');s.add_argument('--update',action='store_true');s.add_argument('--refresh-catalog',action='store_true');sp.add_parser('doctor')
    b=sp.add_parser('bench');b.add_argument('--sizes',type=int,nargs='+',default=[16,256,4096]);b.add_argument('--repeats',type=int,default=3);b.add_argument('--warmups',type=int,default=1);b.add_argument('--order',choices=ORDERS,default='registry')
    rc=sp.add_parser('race');rc.add_argument('--text');rc.add_argument('--file');rc.add_argument('--iterations',type=int,default=5);rc.add_argument('--warmups',type=int,default=1)
    pr=sp.add_parser('parallel-race');pr.add_argument('--text');pr.add_argument('--file');pr.add_argument('--iterations',type=int,default=7);pr.add_argument('--warmups',type=int,default=1);pr.add_argument('--parallel',type=int,default=0)
    mx=sp.add_parser('matrix');mx.add_argument('--sizes',type=int,nargs='+',default=[16,256,4096,65536]);mx.add_argument('--iterations',type=int,default=5);mx.add_argument('--warmups',type=int,default=1)
    st=sp.add_parser('stress');st.add_argument('--size',type=int,default=2048);st.add_argument('--cycles',type=int,default=25);st.add_argument('--warmups',type=int,default=1);st.add_argument('--seed',type=int,default=1337)
    sh=sp.add_parser('showcase');sh.add_argument('--text');sh.add_argument('--file');sh.add_argument('--profile',choices=['quick','showcase','extreme'],default='showcase')
    sp.add_parser('profiles');sp.add_parser('snapshot');sp.add_parser('packages');wi=sp.add_parser('info');wi.add_argument('query')
    hi=sp.add_parser('history');hi.add_argument('--limit',type=int,default=20)
    co=sp.add_parser('compare');co.add_argument('result_a',nargs='?');co.add_argument('result_b',nargs='?')
    ca=sp.add_parser('calibrate');ca.add_argument('--sizes',type=int,nargs='+',default=[64,4096,65536]);ca.add_argument('--iterations',type=int,default=4);ca.add_argument('--warmups',type=int,default=2);ca.add_argument('--strategy',choices=['balanced','latency','throughput','stable'],default='balanced')
    calshow=sp.add_parser('calibration');calshow.add_argument('--strategy',choices=['balanced','latency','throughput','stable'],default='balanced')
    da=sp.add_parser('differential');da.add_argument('--vectors',type=int,default=32);da.add_argument('--max-size',type=int,default=4096);da.add_argument('--seed',type=int,default=1121);da.add_argument('--warmups',type=int,default=1)
    ch=sp.add_parser('chaos');ch.add_argument('--text');ch.add_argument('--file');ch.add_argument('--cycles',type=int,default=12);ch.add_argument('--restart-rate',type=float,default=0.20);ch.add_argument('--seed',type=int,default=1121);ch.add_argument('--warmups',type=int,default=1);ch.add_argument('--no-telemetry',action='store_true')
    ck=sp.add_parser('checkpoint');ck.add_argument('--text');ck.add_argument('--file');ck.add_argument('--order',choices=ORDERS,default='registry');ck.add_argument('--seed',type=int);ck.add_argument('--stop-after',type=int,default=0);ck.add_argument('--path')
    re=sp.add_parser('resume');re.add_argument('checkpoint');sp.add_parser('checkpoints')
    tp=sp.add_parser('topology');tp.add_argument('--text');tp.add_argument('--file');tp.add_argument('--lanes',type=int,default=4);tp.add_argument('--iterations',type=int,default=3);tp.add_argument('--warmups',type=int,default=1);tp.add_argument('--strategy',choices=['round-robin','contiguous','shuffle'],default='round-robin');tp.add_argument('--seed',type=int,default=1121)
    cn=sp.add_parser('consensus');cn.add_argument('--text');cn.add_argument('--file');cn.add_argument('--replicas',type=int,default=3);cn.add_argument('--rounds',type=int,default=1);cn.add_argument('--warmups',type=int,default=1);cn.add_argument('--seed',type=int,default=1121)
    sp.add_parser('scenarios');sn=sp.add_parser('scenario');sn.add_argument('name');sn.add_argument('--text');sn.add_argument('--file')
    db=sp.add_parser('db');dbs=db.add_subparsers(dest='db_cmd');dbs.add_parser('stats');dbl=dbs.add_parser('leaderboard');dbl.add_argument('--limit',type=int,default=30);dbl.add_argument('--min-samples',type=int,default=1);dbl.add_argument('--mode',default='chain');dbr=dbs.add_parser('recent');dbr.add_argument('--limit',type=int,default=20);dbr.add_argument('--mode');dbs.add_parser('rebuild')
    bu=sp.add_parser('bundle');bu.add_argument('paths',nargs='*');bu.add_argument('--name');sp.add_parser('dashboard')
    pl=sp.add_parser('plan');pl.add_argument('--bytes',type=int,default=0);pl.add_argument('--rounds',type=int,default=1);pl.add_argument('--order',choices=ORDERS,default='fastest');pl.add_argument('--json',action='store_true')
    rg=sp.add_parser('regression');rg.add_argument('--mode',default='chain');rg.add_argument('--threshold',type=float,default=15.0)
    c=sp.add_parser('catalog');csp=c.add_subparsers(dest='catalog_cmd');cl=csp.add_parser('list');cl.add_argument('--letter');cs=csp.add_parser('search');cs.add_argument('query');csp.add_parser('stats');csp.add_parser('refresh')
    t=sp.add_parser('tools',help='Offline practical utility toolbox');ts=t.add_subparsers(dest='tool_cmd')
    tc=ts.add_parser('codec');tc.add_argument('format',choices=['base64','base32','base85','ascii85','hex','url','gzip','zlib','bz2','xz','rot13']);tc.add_argument('--decode',action='store_true');tc.add_argument('--text');tc.add_argument('--file');tc.add_argument('--output');tc.add_argument('--raw',action='store_true',help='write raw bytes to stdout when no --output is used')
    th=ts.add_parser('hash');th.add_argument('--text');th.add_argument('--file');th.add_argument('--algorithms',nargs='+',default=['sha256','sha512','blake2b'])
    ti=ts.add_parser('inspect');ti.add_argument('path');ti.add_argument('--preview',type=int,default=256)
    tx=ts.add_parser('hexdump');tx.add_argument('path');tx.add_argument('--width',type=int,default=16);tx.add_argument('--limit',type=int,default=1024)
    tr=ts.add_parser('strings');tr.add_argument('path');tr.add_argument('--min-length',type=int,default=4);tr.add_argument('--limit',type=int,default=200)
    td=ts.add_parser('duplicates');td.add_argument('root');td.add_argument('--min-size',type=int,default=1);td.add_argument('--algorithm',default='sha256')
    tt=ts.add_parser('text-stats');tt.add_argument('--text');tt.add_argument('--file')
    tj=ts.add_parser('json');tj.add_argument('--text');tj.add_argument('--file');tj.add_argument('--mode',choices=['pretty','minify','validate'],default='pretty');tj.add_argument('--query');tj.add_argument('--output')
    tv=ts.add_parser('csv');tv.add_argument('path');tv.add_argument('--delimiter');tv.add_argument('--sample',type=int,default=5)
    tg=ts.add_parser('generate');tg.add_argument('--kind',choices=['password','token','hex','uuid'],default='password');tg.add_argument('--length',type=int,default=24);tg.add_argument('--count',type=int,default=1)
    tm=ts.add_parser('manifest-create');tm.add_argument('root');tm.add_argument('--output');tm.add_argument('--algorithm',default='sha256')
    tmv=ts.add_parser('manifest-verify');tmv.add_argument('manifest')
    tac=ts.add_parser('archive-create');tac.add_argument('source');tac.add_argument('--output');tac.add_argument('--kind',choices=['zip','tar.gz'],default='zip')
    tae=ts.add_parser('archive-extract');tae.add_argument('archive');tae.add_argument('--destination')
    tsr=ts.add_parser('storage');tsr.add_argument('root');tsr.add_argument('--top',type=int,default=20)
    tcp=ts.add_parser('compare');tcp.add_argument('a');tcp.add_argument('b')
    tsv=ts.add_parser('serve');tsv.add_argument('directory',nargs='?',default='.');tsv.add_argument('--host',default='127.0.0.1');tsv.add_argument('--port',type=int,default=8000)
    tid=ts.add_parser('identify');tid.add_argument('path')
    tcb=ts.add_parser('codebase');tcb.add_argument('root');tcb.add_argument('--top',type=int,default=30)
    tf=ts.add_parser('find');tf.add_argument('root');tf.add_argument('--pattern',default='*');tf.add_argument('--content');tf.add_argument('--regex',action='store_true');tf.add_argument('--case-sensitive',action='store_true');tf.add_argument('--hidden',action='store_true');tf.add_argument('--max-results',type=int,default=500)
    ttree=ts.add_parser('tree');ttree.add_argument('root',nargs='?',default='.');ttree.add_argument('--depth',type=int,default=3);ttree.add_argument('--max-entries',type=int,default=500);ttree.add_argument('--hidden',action='store_true')
    tren=ts.add_parser('rename');tren.add_argument('root');tren.add_argument('--glob',default='*');tren.add_argument('--find');tren.add_argument('--replace',default='');tren.add_argument('--prefix',default='');tren.add_argument('--suffix',default='');tren.add_argument('--apply',action='store_true')
    tsy=ts.add_parser('sync');tsy.add_argument('source');tsy.add_argument('destination');tsy.add_argument('--delete',action='store_true');tsy.add_argument('--apply',action='store_true');tsy.add_argument('--checksum',action='store_true')
    tbk=ts.add_parser('backup');tbk.add_argument('source');tbk.add_argument('--destination');tbk.add_argument('--label')
    tcl=ts.add_parser('clean');tcl.add_argument('root');tcl.add_argument('--older-days',type=int,default=7);tcl.add_argument('--apply',action='store_true')
    tdf=ts.add_parser('diff');tdf.add_argument('a');tdf.add_argument('b');tdf.add_argument('--context',type=int,default=3)
    tdo=ts.add_parser('todos');tdo.add_argument('root');tdo.add_argument('--max-results',type=int,default=500)
    teol=ts.add_parser('eol');teol.add_argument('path');teol.add_argument('--mode',choices=['lf','crlf'],default='lf');teol.add_argument('--apply',action='store_true')
    tenv=ts.add_parser('env');tenv.add_argument('commands',nargs='*')
    tgit=ts.add_parser('git');tgit.add_argument('path',nargs='?',default='.')
    tdns=ts.add_parser('dns');tdns.add_argument('host')
    ttcp=ts.add_parser('tcp');ttcp.add_argument('host');ttcp.add_argument('port',type=int);ttcp.add_argument('--timeout',type=float,default=3)
    thttp=ts.add_parser('http');thttp.add_argument('url');thttp.add_argument('--timeout',type=float,default=10)
    tdl=ts.add_parser('download');tdl.add_argument('url');tdl.add_argument('--output');tdl.add_argument('--sha256');tdl.add_argument('--timeout',type=float,default=30);tdl.add_argument('--max-bytes',type=int,default=1073741824)
    tps=ts.add_parser('processes');tps.add_argument('--limit',type=int,default=100)
    tsig=ts.add_parser('signature');tsig.add_argument('path')
    tch=ts.add_parser('chunk-hash');tch.add_argument('path');tch.add_argument('--chunk-size',type=int,default=1048576);tch.add_argument('--algorithm',default='sha256')
    tcw=ts.add_parser('checksum-write');tcw.add_argument('path');tcw.add_argument('--algorithm',default='sha256');tcw.add_argument('--output')
    tcv=ts.add_parser('checksum-verify');tcv.add_argument('sidecar');tcv.add_argument('--file')
    tal=ts.add_parser('archive-list');tal.add_argument('path');tal.add_argument('--limit',type=int,default=5000)
    tbase=ts.add_parser('base');tbase.add_argument('value');tbase.add_argument('--from-base',type=int,default=10);tbase.add_argument('--to-base',type=int,default=16)
    tcidr=ts.add_parser('cidr');tcidr.add_argument('value')
    turi=ts.add_parser('url-info');turi.add_argument('url')
    tperm=ts.add_parser('permissions');tperm.add_argument('value')
    treg=ts.add_parser('regex-test');treg.add_argument('pattern');treg.add_argument('--text');treg.add_argument('--file');treg.add_argument('--ignore-case',action='store_true');treg.add_argument('--multiline',action='store_true');treg.add_argument('--max-matches',type=int,default=100)
    tclean=ts.add_parser('clean-text');tclean.add_argument('--text');tclean.add_argument('--file');tclean.add_argument('--output');tclean.add_argument('--no-trim',action='store_true');tclean.add_argument('--drop-blank',action='store_true');tclean.add_argument('--dedupe',action='store_true');tclean.add_argument('--sort',action='store_true');tclean.add_argument('--casefold-sort',action='store_true')
    twf=ts.add_parser('word-frequency');twf.add_argument('--text');twf.add_argument('--file');twf.add_argument('--limit',type=int,default=50)
    tng=ts.add_parser('ngrams');tng.add_argument('--text');tng.add_argument('--file');tng.add_argument('-n',type=int,default=2);tng.add_argument('--limit',type=int,default=50);tng.add_argument('--mode',choices=['word','char'],default='word')
    tcj=ts.add_parser('csv-to-json');tcj.add_argument('path');tcj.add_argument('--output');tcj.add_argument('--delimiter')
    tjc=ts.add_parser('json-to-csv');tjc.add_argument('path');tjc.add_argument('--output')
    tsi=ts.add_parser('sqlite-info');tsi.add_argument('path')
    tsq=ts.add_parser('sqlite-query');tsq.add_argument('path');tsq.add_argument('query');tsq.add_argument('--limit',type=int,default=1000)
    tep=ts.add_parser('env-parse');tep.add_argument('path')
    tsn=ts.add_parser('safe-name');tsn.add_argument('name');tsn.add_argument('--replacement',default='-');tsn.add_argument('--max-length',type=int,default=120)
    tts=ts.add_parser('text-split');tts.add_argument('path');tts.add_argument('--output-dir');tts.add_argument('--lines-per-file',type=int,default=1000);tts.add_argument('--prefix',default='part')
    tmf=ts.add_parser('merge-files');tmf.add_argument('paths',nargs='+');tmf.add_argument('--output',required=True);tmf.add_argument('--separator',default='')
    tjd=ts.add_parser('json-diff');tjd.add_argument('a');tjd.add_argument('b')
    pg=sp.add_parser('polyglot',help='Practical workflows where every verified language actively processes data');pgs=pg.add_subparsers(dest='poly_cmd')
    pgs.add_parser('status')
    pseal=pgs.add_parser('seal');pseal.add_argument('path');pseal.add_argument('--output');pseal.add_argument('--chunk-size',type=int,default=65536);pseal.add_argument('--order',choices=ORDERS,default='registry');pseal.add_argument('--warmups',type=int,default=1)
    pver=pgs.add_parser('verify');pver.add_argument('manifest');pver.add_argument('--file');pver.add_argument('--warmups',type=int,default=1)
    pfp=pgs.add_parser('fingerprint');pfp.add_argument('path');pfp.add_argument('--chunk-size',type=int,default=65536);pfp.add_argument('--order',choices=ORDERS,default='registry');pfp.add_argument('--warmups',type=int,default=1)
    ppack=pgs.add_parser('pack');ppack.add_argument('source');ppack.add_argument('--output');ppack.add_argument('--chunk-size',type=int,default=65536);ppack.add_argument('--order',choices=ORDERS,default='registry');ppack.add_argument('--warmups',type=int,default=1);ppack.add_argument('--force',action='store_true')
    pun=pgs.add_parser('unpack');pun.add_argument('package');pun.add_argument('--destination');pun.add_argument('--warmups',type=int,default=1);pun.add_argument('--force',action='store_true')
    pcopy=pgs.add_parser('copy');pcopy.add_argument('source');pcopy.add_argument('destination');pcopy.add_argument('--chunk-size',type=int,default=65536);pcopy.add_argument('--order',choices=ORDERS,default='registry');pcopy.add_argument('--warmups',type=int,default=1);pcopy.add_argument('--force',action='store_true')
    paud=pgs.add_parser('audit');paud.add_argument('root');paud.add_argument('--output');paud.add_argument('--sample-bytes',type=int,default=32768);paud.add_argument('--order',choices=ORDERS,default='registry');paud.add_argument('--warmups',type=int,default=1);paud.add_argument('--hidden',action='store_true')
    pav=pgs.add_parser('audit-verify');pav.add_argument('manifest');pav.add_argument('--root');pav.add_argument('--warmups',type=int,default=1)
    pprot=pgs.add_parser('protect');pprot.add_argument('source');pprot.add_argument('--destination');pprot.add_argument('--label');pprot.add_argument('--chunk-size',type=int,default=65536);pprot.add_argument('--order',choices=ORDERS,default='registry');pprot.add_argument('--warmups',type=int,default=1);pprot.add_argument('--force',action='store_true');pprot.add_argument('--no-audit',action='store_true')
    prest=pgs.add_parser('restore');prest.add_argument('package');prest.add_argument('--destination');prest.add_argument('--seal');prest.add_argument('--warmups',type=int,default=1);prest.add_argument('--force',action='store_true')
    pcmp=pgs.add_parser('compare');pcmp.add_argument('left');pcmp.add_argument('right');pcmp.add_argument('--sample-bytes',type=int,default=32768);pcmp.add_argument('--order',choices=ORDERS,default='registry');pcmp.add_argument('--warmups',type=int,default=1);pcmp.add_argument('--hidden',action='store_true')
    pmir=pgs.add_parser('mirror');pmir.add_argument('source');pmir.add_argument('destination');pmir.add_argument('--apply',action='store_true');pmir.add_argument('--delete',action='store_true');pmir.add_argument('--no-checksum',action='store_true');pmir.add_argument('--chunk-size',type=int,default=65536);pmir.add_argument('--order',choices=ORDERS,default='registry');pmir.add_argument('--warmups',type=int,default=1);pmir.add_argument('--hidden',action='store_true')
    pspl=pgs.add_parser('split');pspl.add_argument('source');pspl.add_argument('--output-dir');pspl.add_argument('--part-size',type=int,default=4194304);pspl.add_argument('--order',choices=ORDERS,default='registry');pspl.add_argument('--warmups',type=int,default=1);pspl.add_argument('--force',action='store_true')
    pjoin=pgs.add_parser('join');pjoin.add_argument('manifest');pjoin.add_argument('--destination');pjoin.add_argument('--warmups',type=int,default=1);pjoin.add_argument('--force',action='store_true')
    pded=pgs.add_parser('dedupe');pded.add_argument('root');pded.add_argument('--min-size',type=int,default=1);pded.add_argument('--sample-bytes',type=int,default=8192);pded.add_argument('--order',choices=ORDERS,default='registry');pded.add_argument('--warmups',type=int,default=1);pded.add_argument('--hidden',action='store_true')
    pscr=pgs.add_parser('scrub');pscr.add_argument('manifest');pscr.add_argument('--root');pscr.add_argument('--mirror');pscr.add_argument('--repair',action='store_true');pscr.add_argument('--warmups',type=int,default=1)
    pbh=pgs.add_parser('backup-health');pbh.add_argument('root');pbh.add_argument('--warmups',type=int,default=1);pbh.add_argument('--limit',type=int)
    lt=sp.add_parser('langtools',help='Useful native utilities implemented across the verified programming languages');lts=lt.add_subparsers(dest='langtool_cmd')
    lts.add_parser('list');lts.add_parser('status')
    ltr=lts.add_parser('run');ltr.add_argument('tool');ltr.add_argument('args',nargs=argparse.REMAINDER);ltr.add_argument('--timeout',type=int,default=60)
    ltrec=lts.add_parser('recommend');ltrec.add_argument('query',nargs='+')
    for _name in ('project-report','file-report','data-report','auto-report','workspace-report'):
        _p=lts.add_parser(_name);_p.add_argument('path');_p.add_argument('--output')
    lts.add_parser('selftest')
    sup=sp.add_parser('supported',help='Inspect/install all Termux language modules');sups=sup.add_subparsers(dest='supported_cmd')
    sups.add_parser('list');sups.add_parser('status');sups.add_parser('packages');sups.add_parser('balance');sups.add_parser('audit');si=sups.add_parser('install');si.add_argument('ids',nargs='+');sups.add_parser('install-all')
    mod=sp.add_parser('modules',help='Browse, verify, and demo the self-contained executable language modules');mods=mod.add_subparsers(dest='module_cmd')
    mods.add_parser('list');mi=mods.add_parser('info');mi.add_argument('query');md=mods.add_parser('demo');md.add_argument('query');md.add_argument('--timeout',type=int,default=60);mods.add_parser('verify')

    hu=sp.add_parser('human',help='Offline human-language, Unicode, script/alphabet, translation and symbol bridge tools');hus=hu.add_subparsers(dest='human_cmd')
    hus.add_parser('status')
    hl=hus.add_parser('languages');hl.add_argument('query',nargs='?',default='');hl.add_argument('--limit',type=int,default=100);hl.add_argument('--no-deprecated',action='store_true')
    hli=hus.add_parser('language');hli.add_argument('code')
    hs=hus.add_parser('scripts');hs.add_argument('query',nargs='?',default='');hs.add_argument('--limit',type=int,default=300)
    hsi=hus.add_parser('script');hsi.add_argument('query')
    ha=hus.add_parser('alphabet');ha.add_argument('script');ha.add_argument('--limit',type=int,default=500);ha.add_argument('--all',action='store_true',help='include non-letter characters from the script ranges')
    hd=hus.add_parser('detect-script');hd.add_argument('--text');hd.add_argument('--file')
    hc=hus.add_parser('char');hc.add_argument('character')
    hcp=hus.add_parser('codepoint');hcp.add_argument('value')
    hnt=hus.add_parser('name-to-text');hnt.add_argument('names',help='Unicode names separated by |, or U+XXXX values')
    hsl=hus.add_parser('source-literal');hsl.add_argument('language',choices=human_source_literal_languages());hsl.add_argument('--text');hsl.add_argument('--file')
    hus.add_parser('ascii')
    hq=hus.add_parser('unicode-search');hq.add_argument('query');hq.add_argument('--limit',type=int,default=100)
    hn=hus.add_parser('normalize');hn.add_argument('--text');hn.add_argument('--file');hn.add_argument('--form',choices=['NFC','NFD','NFKC','NFKD'],default='NFC');hn.add_argument('--output')
    he=hus.add_parser('encode');he.add_argument('format',choices=['codepoints','unicode','hex','binary','decimal','html','url','json']);he.add_argument('--text');he.add_argument('--file')
    hde=hus.add_parser('decode');hde.add_argument('format',choices=['codepoints','unicode','hex','binary','decimal','html','url','json']);hde.add_argument('value',nargs='?');hde.add_argument('--file')
    hsd=hus.add_parser('symbols-describe');hsd.add_argument('--text');hsd.add_argument('--file');hsd.add_argument('--locale',default='en');hsd.add_argument('--plain',action='store_true')
    hsp=hus.add_parser('symbols-parse');hsp.add_argument('--text');hsp.add_argument('--file');hsp.add_argument('--locale',default='en')
    htr=hus.add_parser('translate');htr.add_argument('--text',required=True);htr.add_argument('--from',dest='source',default='en');htr.add_argument('--to',dest='target',default='el')
    hus.add_parser('translation-status')
    htl=hus.add_parser('transliterate');htl.add_argument('--text',required=True);htl.add_argument('--mode',choices=['ascii','greek-latin','cyrillic-latin','unicode-names','codepoints'],default='ascii')
    hm=hus.add_parser('morse');hm.add_argument('--text',required=True);hm.add_argument('--decode',action='store_true')
    hb=hus.add_parser('braille');hb.add_argument('--text',required=True);hb.add_argument('--decode',action='store_true')
    hna=hus.add_parser('nato');hna.add_argument('--text',required=True)
    hta=hus.add_parser('text-audit');hta.add_argument('--text');hta.add_argument('--file')
    hls=hus.add_parser('languages-for-script');hls.add_argument('script');hls.add_argument('--limit',type=int,default=500)
    htag=hus.add_parser('tag');htag.add_argument('tag')
    hus.add_parser('db-stats')
    hgs=hus.add_parser('glottolog-search');hgs.add_argument('query',nargs='?',default='');hgs.add_argument('--level',choices=['family','language','dialect']);hgs.add_argument('--limit',type=int,default=100)
    hg=hus.add_parser('glottolog');hg.add_argument('code')
    sp.add_parser('home',help='Show the persistent Language Project home folder')
    nw=sp.add_parser('new',help='Create a starter project');nw.add_argument('language',choices=scaffold_languages());nw.add_argument('name');nw.add_argument('--dir',default='.');nw.add_argument('--force',action='store_true')
    ex=sp.add_parser('execute',help='Execute a trusted source file using a local Termux runtime/toolchain');ex.add_argument('source');ex.add_argument('args',nargs='*');ex.add_argument('--timeout',type=int,default=30);ex.add_argument('--stdin-text')
    sp.add_parser('verify');sp.add_parser('audit')
    a=ap.parse_args()
    if not a.cmd:return interactive()
    if a.cmd=='list':return show_list()
    if a.cmd=='setup':
        cmd=[sys.executable,str(ROOT/'scripts'/'setup.py')]
        if a.install:cmd+=['--install']
        if a.update:cmd+=['--update']
        if a.refresh_catalog:cmd+=['--refresh-catalog']
        return subprocess.call(cmd)
    if a.cmd=='doctor':return subprocess.call([sys.executable,str(ROOT/'scripts'/'doctor.py')])
    if a.cmd=='run':
        ensure();data=payload(a.text,a.file);r=run_chain(data,rounds=a.rounds,warmups=a.warmups,order=a.order,seed=a.seed,telemetry=a.telemetry);print_report(r,(a.text or a.file or 'stdin'));return 0 if r['integrity'] else 2
    if a.cmd=='bench':ensure();benchmark_suite(a.sizes,a.repeats,a.order,a.warmups);return 0
    if a.cmd=='race':ensure();r=race_workers(payload(a.text,a.file,'Race payload: '),a.iterations,a.warmups);return 0 if r['integrity'] else 2
    if a.cmd=='parallel-race':ensure();r=parallel_race(payload(a.text,a.file,'Parallel race payload: '),a.iterations,a.warmups,a.parallel);return 0 if r['integrity'] else 2
    if a.cmd=='matrix':ensure();r=matrix_benchmark(a.sizes,a.iterations,a.warmups);return 0 if r['integrity'] else 2
    if a.cmd=='stress':ensure();r=stress_test(a.size,a.cycles,a.warmups,a.seed);return 0 if r['integrity'] else 2
    if a.cmd=='showcase':ensure();r=showcase(payload(a.text,a.file,'Showcase payload: '),get_profile(a.profile));return 0 if r['integrity'] else 2
    if a.cmd=='profiles':return print_profiles()
    if a.cmd=='snapshot':print(json.dumps(device_snapshot(),indent=2));return 0
    if a.cmd=='packages':return subprocess.call([sys.executable,str(ROOT/'scripts'/'package_plan.py')])
    if a.cmd=='info':return worker_info(a.query)
    if a.cmd=='history':print_history(a.limit);return 0
    if a.cmd=='compare':
        try:compare_results(a.result_a,a.result_b);return 0
        except Exception as e:print('Compare:',e);return 1
    if a.cmd=='calibrate':ensure();r=calibrate(a.sizes,a.iterations,a.warmups);print_calibration(a.strategy);return 0 if r.get('integrity') else 2
    if a.cmd=='calibration':print_calibration(a.strategy);return 0
    if a.cmd=='differential':ensure();r=differential_audit(a.vectors,a.max_size,a.seed,a.warmups);return 0 if r['integrity'] else 2
    if a.cmd=='chaos':ensure();r=chaos_test(payload(a.text,a.file,'Chaos payload: '),a.cycles,a.restart_rate,a.seed,a.warmups,not a.no_telemetry);return 0 if r['integrity'] else 2
    if a.cmd=='checkpoint':ensure();r=checkpoint_chain(payload(a.text,a.file,'Checkpoint payload: '),a.order,a.seed,a.stop_after,a.path);return 0 if r.get('integrity',True) else 2
    if a.cmd=='resume':ensure();r=resume_checkpoint(a.checkpoint);return 0 if r.get('integrity',True) else 2
    if a.cmd=='checkpoints':[print(json.dumps(x,ensure_ascii=False)) for x in checkpoint_list()];return 0
    if a.cmd=='topology':ensure();r=topology_benchmark(payload(a.text,a.file,'Topology payload: '),a.lanes,a.iterations,a.warmups,a.strategy,a.seed);return 0 if r['integrity'] else 2
    if a.cmd=='consensus':ensure();r=consensus_test(payload(a.text,a.file,'Consensus payload: '),a.replicas,a.rounds,a.warmups,a.seed);return 0 if r['integrity'] else 2
    if a.cmd=='scenarios':print_scenarios();return 0
    if a.cmd=='scenario':ensure();r=run_scenario(a.name,payload(a.text,a.file,'Scenario payload: '));return 0 if r['integrity'] else 2
    if a.cmd=='db':
        if a.db_cmd=='stats' or not a.db_cmd:print(json.dumps(database_stats(),indent=2));return 0
        if a.db_cmd=='rebuild':print('Indexed result files:',database_rebuild());return 0
        if a.db_cmd=='recent':[print(json.dumps(x,ensure_ascii=False)) for x in database_recent(a.limit,a.mode)];return 0
        if a.db_cmd=='leaderboard':
            rows=database_leaderboard(a.limit,a.min_samples,a.mode)
            for i,x in enumerate(rows,1):print(f"{i:>3} {x['name']:<26} {x['avg_median_ns']/1e6:>10.4f} ms samples={x['samples']:<4} integrity={x['integrity_rate']*100:6.2f}%")
            return 0
    if a.cmd=='bundle':print(create_bundle(a.paths or None,a.name));return 0
    if a.cmd=='dashboard':dashboard();return 0
    if a.cmd=='plan':
        ensure();r=execution_plan(a.bytes,a.rounds,a.order)
        if a.json:print(json.dumps(r,indent=2))
        else:print_plan(r)
        return 0
    if a.cmd=='regression':
        r=regression_check(a.mode,a.threshold);print_regression(r);return 0 if r.get('ok') else 2
    if a.cmd=='catalog':
        if a.catalog_cmd=='stats':print(json.dumps(catalog_stats(),indent=2));return 0
        if a.catalog_cmd=='search':
            xs=search_catalog(a.query);[print(('✓ ' if x.get('termux_worker') else '· ')+x['name']) for x in xs];print('Matches:',len(xs));return 0
        if a.catalog_cmd=='list':show_catalog(a.letter);return 0
        if a.catalog_cmd=='refresh':return subprocess.call([sys.executable,str(ROOT/'scripts'/'refresh_catalog.py')])
        c.print_help();return 0
    if a.cmd=='polyglot':
        try:
            if not a.poly_cmd:practical_polyglot_menu();return 0
            ensure()
            if a.poly_cmd=='status':print(json.dumps(polyglot_status(),indent=2));return 0
            if a.poly_cmd=='seal':print(json.dumps(polyglot_seal(a.path,a.output,a.chunk_size,a.order,a.warmups),indent=2));return 0
            if a.poly_cmd=='verify':r=polyglot_verify_seal(a.manifest,a.file,a.warmups);print(json.dumps(r,indent=2));return 0 if r['ok'] else 2
            if a.poly_cmd=='fingerprint':print(json.dumps(polyglot_fingerprint(a.path,a.chunk_size,a.order,a.warmups),indent=2));return 0
            if a.poly_cmd=='pack':print(json.dumps(polyglot_pack(a.source,a.output,a.chunk_size,a.order,a.warmups,a.force),indent=2));return 0
            if a.poly_cmd=='unpack':print(json.dumps(polyglot_unpack(a.package,a.destination,a.warmups,a.force),indent=2));return 0
            if a.poly_cmd=='copy':print(json.dumps(polyglot_copy(a.source,a.destination,a.chunk_size,a.order,a.warmups,a.force),indent=2));return 0
            if a.poly_cmd=='audit':print(json.dumps(polyglot_audit(a.root,a.output,a.sample_bytes,a.order,a.warmups,a.hidden),indent=2));return 0
            if a.poly_cmd=='audit-verify':r=polyglot_audit_verify(a.manifest,a.root,a.warmups);print(json.dumps(r,indent=2));return 0 if r['ok'] else 2
            if a.poly_cmd=='protect':print(json.dumps(polyglot_protect(a.source,a.destination,a.label,a.chunk_size,a.order,a.warmups,a.force,not a.no_audit),indent=2));return 0
            if a.poly_cmd=='restore':print(json.dumps(polyglot_restore(a.package,a.destination,a.seal,a.warmups,a.force),indent=2));return 0
            if a.poly_cmd=='compare':r=polyglot_compare(a.left,a.right,a.sample_bytes,a.order,a.warmups,a.hidden);print(json.dumps(r,indent=2));return 0 if r.get('equal') else 1
            if a.poly_cmd=='mirror':print(json.dumps(polyglot_mirror(a.source,a.destination,a.apply,a.delete,not a.no_checksum,a.chunk_size,a.order,a.warmups,a.hidden),indent=2));return 0
            if a.poly_cmd=='split':print(json.dumps(polyglot_split(a.source,a.output_dir,a.part_size,a.order,a.warmups,a.force),indent=2));return 0
            if a.poly_cmd=='join':print(json.dumps(polyglot_join(a.manifest,a.destination,a.warmups,a.force),indent=2));return 0
            if a.poly_cmd=='dedupe':print(json.dumps(polyglot_dedupe(a.root,a.min_size,a.sample_bytes,a.order,a.warmups,a.hidden),indent=2));return 0
            if a.poly_cmd=='scrub':r=polyglot_scrub(a.manifest,a.root,a.mirror,a.repair,a.warmups);print(json.dumps(r,indent=2));return 0 if r.get('ok') else 2
            if a.poly_cmd=='backup-health':r=polyglot_backup_health(a.root,a.warmups,a.limit);print(json.dumps(r,indent=2));return 0 if r.get('ok') else 2
        except Exception as e:print('Polyglot workflow error:',e,file=sys.stderr);return 2
    if a.cmd=='supported':
        if a.supported_cmd=='balance': return subprocess.call([sys.executable,str(ROOT/'scripts'/'language_balance.py')])
        if a.supported_cmd=='audit': return subprocess.call([sys.executable,str(ROOT/'scripts'/'termux_coverage_audit.py')])
        cmd=[sys.executable,str(ROOT/'scripts'/'termux_languages.py'),a.supported_cmd or 'list']
        if a.supported_cmd=='install': cmd += a.ids
        return subprocess.call(cmd)
    if a.cmd=='modules':
        try:
            if not a.module_cmd or a.module_cmd=='list':
                rows=list_modules()
                for x in rows:
                    print(f"{'✓' if x['worker_verified'] else '·'} {x['id']:<14} {x['name']:<22} tool={'✓' if x['tool_verified'] else '·'} {x['tool_name']}")
                print(f"\nModules: {len(rows)}"); return 0
            if a.module_cmd=='info':
                rows=module_info(a.query);print(json.dumps(rows,indent=2,ensure_ascii=False));return 0 if rows else 1
            if a.module_cmd=='verify':
                r=verify_modules();print(json.dumps(r,indent=2,ensure_ascii=False));return 0 if r['ok'] else 2
            if a.module_cmd=='demo':
                ensure();r=demo_module(a.query,a.timeout);print(json.dumps(r,indent=2,ensure_ascii=False));return 0 if r['result']['returncode']==0 else r['result']['returncode']
        except Exception as e: print('Module error:',e,file=sys.stderr); return 2

    if a.cmd=='human':
        try:
            def _txt(text=None,file=None):
                return Path(file).expanduser().read_text(encoding='utf-8') if file else (text if text is not None else '')
            if not a.human_cmd or a.human_cmd=='status':print(json.dumps(human_status(),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='languages':print(json.dumps(human_languages_search(a.query,a.limit,not a.no_deprecated),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='language':r=human_language_show(a.code);print(json.dumps(r,indent=2,ensure_ascii=False));return 0 if r else 1
            if a.human_cmd=='scripts':print(json.dumps(human_scripts_list(a.query,a.limit),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='script':r=human_script_show(a.query);print(json.dumps(r,indent=2,ensure_ascii=False));return 0 if r else 1
            if a.human_cmd=='alphabet':print(json.dumps(human_alphabet_chars(a.script,a.limit,not a.all),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='detect-script':print(json.dumps(human_detect_scripts(_txt(a.text,a.file)),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='char':print(json.dumps(human_char_info(a.character),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='codepoint':print(json.dumps(human_codepoint_info(a.value),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='name-to-text':print(human_text_from_unicode_names(a.names));return 0
            if a.human_cmd=='source-literal':print(human_source_literal(_txt(a.text,a.file),a.language));return 0
            if a.human_cmd=='ascii':print(json.dumps(human_ascii_table(),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='unicode-search':print(json.dumps(human_unicode_search(a.query,a.limit),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='normalize':
                out=human_normalize(_txt(a.text,a.file),a.form)
                if a.output:Path(a.output).expanduser().write_text(out,encoding='utf-8');print('Written:',Path(a.output).expanduser())
                else:print(out)
                return 0
            if a.human_cmd=='encode':print(human_encode_bridge(_txt(a.text,a.file),a.format));return 0
            if a.human_cmd=='decode':
                val=Path(a.file).expanduser().read_text(encoding='utf-8') if a.file else (a.value or '')
                print(human_decode_bridge(val,a.format));return 0
            if a.human_cmd=='symbols-describe':print(human_symbols_describe(_txt(a.text,a.file),a.locale,'plain' if a.plain else 'brackets'));return 0
            if a.human_cmd=='symbols-parse':print(human_symbols_parse(_txt(a.text,a.file),a.locale));return 0
            if a.human_cmd=='translation-status':print(json.dumps(human_glossary_status(),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='translate':print(json.dumps(human_translate(a.text,a.source,a.target),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='transliterate':print(human_transliterate(a.text,a.mode));return 0
            if a.human_cmd=='morse':print(human_morse(a.text,a.decode));return 0
            if a.human_cmd=='braille':print(human_braille(a.text,a.decode));return 0
            if a.human_cmd=='nato':print(human_nato(a.text));return 0
            if a.human_cmd=='text-audit':print(json.dumps(human_text_audit(_txt(a.text,a.file)),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='languages-for-script':print(json.dumps(human_languages_for_script(a.script,a.limit),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='tag':print(json.dumps(human_tag_info(a.tag),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='db-stats':print(json.dumps(human_vault_db_stats(),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='glottolog-search':print(json.dumps(human_glottolog_search(a.query,a.level,a.limit),indent=2,ensure_ascii=False));return 0
            if a.human_cmd=='glottolog':r=human_glottolog_show(a.code);print(json.dumps(r,indent=2,ensure_ascii=False));return 0 if r else 1
        except Exception as e:print('Human-language tool error:',e,file=sys.stderr);return 2
    if a.cmd=='home':
        ensure_data_tree();print(DATA_ROOT);return 0
    if a.cmd=='langtools':
        try:
            if not a.langtool_cmd or a.langtool_cmd in {'list','status'}:
                st=langtools_status()
                if a.langtool_cmd=='status': print(json.dumps(st,indent=2)); return 0
                for x in st['tools']:
                    mark='✓' if x['available'] else '·'; print(f"{mark} {x['id']:<22} {x['language']:<14} {x['category']:<10} {x['name']}")
                print(f"\nAvailable: {st['available']}/{st['registered']}"); return 0
            if a.langtool_cmd=='run':
                r=langtool_run(a.tool,a.args,a.timeout);sys.stdout.write(r['stdout']);sys.stderr.write(r['stderr']);return r['returncode']
            if a.langtool_cmd=='recommend':
                xs=langtool_recommend(' '.join(a.query));
                for x in xs: print(f"{'✓' if x['available'] else '·'} {x['id']:<22} {x['language']:<14} {x['name']}")
                return 0
            if a.langtool_cmd=='selftest':
                r=langtools_selftest();print(json.dumps(r,indent=2));return 0 if r['ok'] else 2
            funcs={'project-report':langtool_project_report,'file-report':langtool_file_report,'data-report':langtool_data_report,'auto-report':langtool_auto_report,'workspace-report':langtool_workspace_report}
            r=funcs[a.langtool_cmd](a.path);txt=json.dumps(r,indent=2,ensure_ascii=False)+'\n'
            if a.output: Path(a.output).expanduser().write_text(txt,encoding='utf-8'); print('Written:',Path(a.output).expanduser())
            else: print(txt,end='')
            return 0
        except Exception as e: print('Native language tool error:',e,file=sys.stderr); return 2
    if a.cmd=='tools':
        try:return run_tools(a)
        except Exception as e:print('Tool error:',e,file=sys.stderr);return 2
    if a.cmd=='new':
        try:print(json.dumps(scaffold_create(a.language,a.name,a.dir,a.force),indent=2));return 0
        except Exception as e:print('Scaffold error:',e,file=sys.stderr);return 2
    if a.cmd=='execute':
        try:
            r=run_source(a.source,a.args,a.timeout,a.stdin_text.encode() if a.stdin_text is not None else None);sys.stdout.buffer.write(r['stdout']);sys.stderr.buffer.write(r['stderr']);return r['returncode']
        except Exception as e:print('Execute error:',e,file=sys.stderr);return 2
    if a.cmd=='verify':return subprocess.call([sys.executable,str(ROOT/'scripts'/'verify_manifest.py')])
    if a.cmd=='audit':return subprocess.call([sys.executable,str(ROOT/'scripts'/'audit_project.py')])
if __name__=='__main__':raise SystemExit(main() or 0)
