# Language Vault

Language Vault is the offline human-language, writing-system, Unicode and language-identity layer bundled inside Language Project. It is separate from the programming-language execution registry and is designed so normal lookup/conversion work does not require a network connection after installation.

## Bundled catalog layers

### IANA Language Subtag Registry

The repository preserves the complete bundled IANA registry snapshot and generates searchable JSON/TSV records from it. The snapshot currently contains 8,276 language-subtag records plus script, region and variant records used for language-tag inspection.

### Glottolog 5.3

`data/human/glottolog/languages.csv` bundles the Glottolog 5.3 CLDF languoid table. The current table has 27,177 rows covering families, languages and dialects. The original CC BY 4.0 license and attribution are kept beside the data.

Glottolog and IANA solve different problems: IANA is a standards registry for language tags, while Glottolog is a broader catalog of languoids.

### Unicode 17.0

The vault bundles Unicode character and writing-system data including:

- UnicodeData
- Scripts and Blocks
- PropertyValueAliases
- NamesList and NameAliases
- CaseFolding
- EastAsianWidth
- DerivedAge
- PropList and DerivedCoreProperties
- BidiMirroring and BidiBrackets
- NamedSequences
- NormalizationCorrections
- Emoji properties and emoji variation sequences

The Unicode license is stored with the Unicode-derived files.

## Portable generated indexes

`data/human/generated/` contains formats usable without a custom library:

- `language-index.tsv`
- `script-index.tsv`
- `block-index.tsv`
- `unicode-codepoints.tsv`
- `script-ranges.tsv`
- `block-ranges.tsv`
- `glottolog-index.tsv`
- `programming-symbols.tsv`
- `translation-matrix.json`
- `language-vault.sqlite3`

The raw source data is preserved so the indexes remain auditable.

## Main commands

```bash
language-project human status
language-project human languages greek
language-project human language el
language-project human glottolog-search Greek --level language
language-project human glottolog mode1248
language-project human scripts
language-project human script Greek
language-project human alphabet Greek --limit 100
language-project human detect-script --text "Hello κόσμε Привет مرحبا 你好"
language-project human char "λ"
language-project human codepoint U+03BB
language-project human unicode-search "GREEK SMALL LETTER"
language-project human db-stats
```

The CLI command `alphabet` is a convenience name. Unicode scripts include alphabets, abjads, abugidas, syllabaries, logographic systems and other encoded writing systems.

## What “all languages” means here

No finite registry is a perfect census of every human language variety. Language Project therefore keeps multiple catalog layers and reports exactly what each layer represents. It does not turn catalog coverage into a false claim of universal free-form machine translation.
