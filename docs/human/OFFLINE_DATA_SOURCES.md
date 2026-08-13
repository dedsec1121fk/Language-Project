# Offline Data Sources And Provenance

Language Project keeps standards/reference data in the repository so normal use does not require downloading those resources after installation.

## IANA

`data/human/iana/language-subtag-registry.txt` is the bundled IANA Language Subtag Registry snapshot. Per-language records and indexes are generated from it.

## Glottolog

`data/human/glottolog/languages.csv` is the bundled Glottolog 5.3 CLDF language table. `ATTRIBUTION.txt` records the dataset citation and `CC-BY-4.0.txt` preserves the license text. The project also produces `generated/glottolog-index.tsv` and indexes the table in SQLite for offline search.

## Unicode

`data/human/unicode/` contains the bundled Unicode 17.0 Character Database/reference files used by Language Project. `UNICODE-LICENSE.txt` is stored in the same tree. The project keeps both raw tables and generated indexes.

## Translation data

`data/human/translation/` contains the project's small exact multilingual glossary and programming-symbol lexicon. This is project-authored utility data, deliberately scoped and not represented as a universal machine-translation corpus.

## Generated files

`data/human/generated/` contains search-friendly JSON, TSV and SQLite indexes. Portable TSV files are included so shell tools, spreadsheets and other languages can use the vault directly without importing the Python control plane.

## Updating

`scripts/human/update_language_vault.py` can refresh raw public standards/reference files for maintainers. Normal users do not need to run it. A release should rebuild generated indexes, verify attribution/licenses and run `scripts/human/verify_language_vault.py` before publishing.
