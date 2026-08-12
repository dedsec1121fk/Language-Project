#!/usr/bin/env fish
if test (count $argv) -gt 0; and test "$argv[1]" = "--help"
 echo "Usage: large-files DIRECTORY [COUNT]"; exit 0
end
set root .; set n 20
if test (count $argv) -ge 1; set root $argv[1]; end
if test (count $argv) -ge 2; set n $argv[2]; end
du -a "$root" 2>/dev/null | sort -nr | head -n $n
