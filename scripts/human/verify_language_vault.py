#!/usr/bin/env python3
from pathlib import Path
import json,sys,sqlite3
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'data'/'human'
errors=[]
required=[
 D/'iana/language-subtag-registry.txt',D/'unicode/UnicodeData.txt',D/'unicode/Scripts.txt',D/'unicode/Blocks.txt',
 D/'unicode/PropertyValueAliases.txt',D/'unicode/NamesList.txt',D/'unicode/CaseFolding.txt',D/'unicode/EastAsianWidth.txt',
 D/'unicode/emoji-data.txt',D/'unicode/UNICODE-LICENSE.txt',D/'unicode/NameAliases.txt',D/'unicode/DerivedAge.txt',
 D/'unicode/PropList.txt',D/'unicode/DerivedCoreProperties.txt',D/'unicode/BidiMirroring.txt',D/'unicode/BidiBrackets.txt',
 D/'unicode/NamedSequences.txt',D/'unicode/NormalizationCorrections.txt',D/'unicode/emoji-variation-sequences.txt',
 D/'glottolog/languages.csv',D/'glottolog/CC-BY-4.0.txt',D/'glottolog/ATTRIBUTION.txt',
 D/'generated/language-registry.json',D/'generated/scripts.json',D/'generated/blocks.json',D/'generated/language-vault.sqlite3',
 D/'generated/glottolog-index.tsv',D/'generated/glottolog-stats.json',D/'generated/unicode-codepoints.tsv',
 D/'generated/script-ranges.tsv',D/'generated/block-ranges.tsv',D/'generated/programming-symbols.tsv',D/'generated/translation-matrix.json',
 D/'translation/symbols.json',D/'translation/phrasebook.json']
for p in required:
    if not p.is_file() or p.stat().st_size==0:errors.append(f'missing/empty: {p.relative_to(ROOT)}')
try:
    r=json.loads((D/'generated/language-registry.json').read_text(encoding='utf-8'))
    if len(r.get('languages',[]))<8000:errors.append('IANA language record count unexpectedly low')
    if sum(1 for _ in (D/'language-records').rglob('*.json'))!=len(r.get('languages',[])):errors.append('per-language record count mismatch')
    s=json.loads((D/'generated/scripts.json').read_text(encoding='utf-8'))
    if len(s.get('scripts',[]))<170:errors.append('Unicode script count unexpectedly low')
    if sum(1 for _ in (D/'script-records').glob('*.json'))!=len(s.get('scripts',[])):errors.append('per-script record count mismatch')
    con=sqlite3.connect(D/'generated/language-vault.sqlite3')
    gl=con.execute('SELECT COUNT(*) FROM glottolog').fetchone()[0];con.close()
    if gl<27000:errors.append('Glottolog languoid count unexpectedly low')
except Exception as e:errors.append(f'parse error: {e}')
print('Language Vault verification:', 'PASS' if not errors else 'FAIL')
if not errors:
    print('IANA language records:',len(r['languages']))
    print('Unicode script records:',len(s['scripts']))
    print('Unicode blocks:',len(json.loads((D/'generated/blocks.json').read_text())['blocks']))
    print('Glottolog languoids:',gl)
for e in errors:print('!',e)
raise SystemExit(1 if errors else 0)
