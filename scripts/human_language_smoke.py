#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.human_language import *
assert status()['iana_language_records']>=8000
assert status()['glottolog_languoids']>=27000
assert language_show('en')
assert script_show('Greek')
assert detect_scripts('Hello κόσμε Привет')['scripts']
assert decode_bridge(encode_bridge('Γεια 👋','codepoints'),'codepoints')=='Γεια 👋'
assert decode_bridge(encode_bridge('Γεια 👋','hex'),'hex')=='Γεια 👋'
assert symbols_parse(symbols_describe('x++;','en'),'en')=='x++;'
assert translate('hello file','en','el')['translated']=='γεια αρχείο'
assert transliterate('γεια','greek-latin')=='geia'
assert morse(morse('SOS',False),True)=='SOS'
assert braille(braille('abc',False),True)=='abc'
assert glottolog_search('Greek','language',5)
assert codepoint_info('U+03BB')['character']=='λ'
assert text_from_unicode_names('GREEK SMALL LETTER LAMDA | SPACE | LATIN CAPITAL LETTER A')=='λ A'
assert source_literal('Γεια','rust').startswith('\"')
a=text_audit('abc\u202Exyz')
assert a['bidi_controls']
print('Human-language smoke: PASS')
