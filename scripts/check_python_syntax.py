#!/usr/bin/env python3
"""Validate project Python syntax without creating .pyc/__pycache__ artifacts."""
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("cli", "core", "scripts", "tests")


def iter_python_files():
    for name in TARGETS:
        base = ROOT / name
        if not base.exists():
            continue
        yield from sorted(
            p for p in base.rglob("*.py")
            if "__pycache__" not in p.parts
        )


def main() -> int:
    files = list(iter_python_files())
    failures: list[str] = []
    for path in files:
        rel = path.relative_to(ROOT)
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(rel))
        except (SyntaxError, UnicodeDecodeError) as exc:
            failures.append(f"{rel}: {exc}")

    if failures:
        print("Python syntax validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"Python syntax validation: PASS ({len(files)} files, no bytecode written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
