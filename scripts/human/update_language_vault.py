#!/usr/bin/env python3
"""Refresh the bundled public standards data. Intended for maintainers, not normal use.
Uses only Python standard library. Unicode files remain governed by the bundled Unicode license.
"""
from pathlib import Path
import urllib.request,sys
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data'/'human'
SOURCES={
 'iana/language-subtag-registry.txt':'https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry',
 'unicode/UnicodeData.txt':'https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt',
 'unicode/Scripts.txt':'https://www.unicode.org/Public/UCD/latest/ucd/Scripts.txt',
 'unicode/Blocks.txt':'https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt',
 'unicode/PropertyValueAliases.txt':'https://www.unicode.org/Public/UCD/latest/ucd/PropertyValueAliases.txt',
 'unicode/NamesList.txt':'https://www.unicode.org/Public/UCD/latest/ucd/NamesList.txt',
 'unicode/CaseFolding.txt':'https://www.unicode.org/Public/UCD/latest/ucd/CaseFolding.txt',
 'unicode/EastAsianWidth.txt':'https://www.unicode.org/Public/UCD/latest/ucd/EastAsianWidth.txt',
 'unicode/emoji-data.txt':'https://www.unicode.org/Public/UCD/latest/ucd/emoji/emoji-data.txt',
 'unicode/NameAliases.txt':'https://www.unicode.org/Public/UCD/latest/ucd/NameAliases.txt',
 'unicode/DerivedAge.txt':'https://www.unicode.org/Public/UCD/latest/ucd/DerivedAge.txt',
 'unicode/PropList.txt':'https://www.unicode.org/Public/UCD/latest/ucd/PropList.txt',
 'unicode/DerivedCoreProperties.txt':'https://www.unicode.org/Public/UCD/latest/ucd/DerivedCoreProperties.txt',
 'unicode/BidiMirroring.txt':'https://www.unicode.org/Public/UCD/latest/ucd/BidiMirroring.txt',
 'unicode/BidiBrackets.txt':'https://www.unicode.org/Public/UCD/latest/ucd/BidiBrackets.txt',
 'unicode/NamedSequences.txt':'https://www.unicode.org/Public/UCD/latest/ucd/NamedSequences.txt',
 'unicode/NormalizationCorrections.txt':'https://www.unicode.org/Public/UCD/latest/ucd/NormalizationCorrections.txt',
 'unicode/emoji-variation-sequences.txt':'https://www.unicode.org/Public/UCD/latest/ucd/emoji/emoji-variation-sequences.txt',
 'unicode/UNICODE-LICENSE.txt':'https://www.unicode.org/license.txt',
 'glottolog/languages.csv':'https://raw.githubusercontent.com/glottolog/glottolog-cldf/master/cldf/languages.csv',
 'glottolog/CC-BY-4.0.txt':'https://creativecommons.org/licenses/by/4.0/legalcode.txt',
}
for rel,url in SOURCES.items():
    p=D/rel;p.parent.mkdir(parents=True,exist_ok=True)
    print('Downloading',url)
    with urllib.request.urlopen(url,timeout=60) as r:p.write_bytes(r.read())
print('Raw standards data refreshed. Glottolog attribution must remain in data/human/glottolog/ATTRIBUTION.txt. Rebuild generated indexes before release.')
