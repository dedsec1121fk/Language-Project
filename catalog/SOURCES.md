# Catalog Sources

The bundled snapshot merges programming-language names and metadata from several indexes plus a curated historical/experimental seed. The installed copy can refresh and merge additional names from:

- PLDB.
- GitHub Linguist.
- Pygments.
- Wikipedia's programming-language list.
- Rosetta Code's programming-language category.
- Esolang Wiki's language category with pagination.

The refresh is additive and best-effort: one failed source does not destroy the existing catalog. Names are Unicode-normalized and deduplicated case-insensitively, while slug collisions receive deterministic hash suffixes.

Catalog membership does **not** imply Termux executability. Only `config/registries/languages.json` plus a successful on-device build/start/protocol/round-trip self-test can activate a language in the execution chain.
