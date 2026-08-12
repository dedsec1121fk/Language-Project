#!/usr/bin/env zsh
if [[ ${1:-} == --help ]]; then print 'Usage: recent-files DIRECTORY [COUNT]'; exit 0; fi
root=${1:-.}; count=${2:-20}
setopt localoptions nullglob extendedglob
files=("$root"/**/*(.omN))
print "Most recently modified files under $root"
local i=0 f
for f in $files; do
  (( i++ )); print -r -- "$(stat -c '%y' -- "$f" 2>/dev/null | cut -d. -f1)\t$f"
  (( i >= count )) && break
done
