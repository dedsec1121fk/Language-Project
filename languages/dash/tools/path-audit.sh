#!/usr/bin/env dash
if [ "${1:-}" = "--help" ]; then echo "Usage: path-audit  # inspect PATH entries for missing/duplicate/writable dirs"; exit 0; fi
oldIFS=$IFS;IFS=:;set -- $PATH;IFS=$oldIFS
seen='|';i=0
for d do i=$((i+1)); [ -n "$d" ] || d='.'; state='ok'; [ -d "$d" ] || state='missing'; case "$seen" in *"|$d|"*) state="$state,duplicate";; esac; seen="$seen$d|"; [ -w "$d" ] && state="$state,writable"; printf '%02d\t%s\t%s\n' "$i" "$state" "$d"; done
