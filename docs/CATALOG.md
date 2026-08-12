# Global Catalog Architecture

Language Project separates **catalog coverage** from **execution support**.

`catalog/known_languages.json` is the merged index. Every bundled catalog record also has a standalone JSON file in `catalog/languages/` so the repository visibly contains a concrete record for each cataloged language/dialect name.

The bundled snapshot is intentionally useful offline. During Termux installation, `scripts/refresh_catalog.py` performs a best-effort online refresh from multiple public indexes. It paginates MediaWiki categories, de-duplicates Unicode-normalized names, preserves source provenance, generates collision-safe slugs, maps executable workers, rewrites the per-language metadata tree, and regenerates the README A–Z `<details>` section.

Catalog-only entries never enter the benchmark chain. Executability is controlled exclusively by `config/registries/languages.json` plus the on-device compile/start/PING/round-trip tests in `scripts/setup.py`.

## Why the catalog is refreshable

There is no authoritative finite registry that can prove it contains every programming language ever created. New experimental and esoteric languages continue to appear. The refresh system therefore treats “all known languages” as a continuously updated catalog target, while keeping executable claims strict and testable.
