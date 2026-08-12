#!/usr/bin/env bash
set -u
if [ "${1:-}" = "--help" ]; then echo "Usage: sys-report [path]  # system + filesystem report"; exit 0; fi
TARGET="${1:-.}"
echo "Language Project / Bash system report"
printf 'date: '; date -Iseconds 2>/dev/null || date
printf 'kernel: '; uname -a
printf 'shell: '; printf '%s\n' "${SHELL:-unknown}"
printf 'prefix: '; printf '%s\n' "${PREFIX:-unknown}"
printf 'cwd: '; pwd
printf 'target: '; readlink -f "$TARGET" 2>/dev/null || printf '%s\n' "$TARGET"
printf 'cpu_count: '; (getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo unknown)
printf 'uptime: '; (uptime 2>/dev/null || true)
echo "filesystem:"; df -h "$TARGET" 2>/dev/null || true
if command -v free >/dev/null 2>&1; then echo "memory:"; free -h; fi
if command -v termux-info >/dev/null 2>&1; then echo "termux:"; termux-info 2>/dev/null | head -40; fi
