#!/data/data/com.termux/files/usr/bin/bash
# Bash owns the persistent protocol loop. tr provides a fast reversible
# nibble translation so large showcase payloads do not spend seconds in a
# byte-at-a-time shell arithmetic loop.
transform(){
  printf '%s\n' "$1" | tr '0123456789abcdefABCDEF' 'fedcba9876543210FEDCBA9876543210'
}
while IFS= read -r line; do
  [[ "$line" == "PING" ]] && { printf 'PONG\n'; continue; }
  [[ "$line" == "QUIT" ]] && exit 0
  [[ "$line" =~ ^[ED][[:space:]]([0-9A-Fa-f]*)$ ]] && transform "${BASH_REMATCH[1]}" || printf 'ERR\n'
done
