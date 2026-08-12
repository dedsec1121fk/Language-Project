#!/data/data/com.termux/files/usr/bin/dash
# Dash owns the persistent protocol loop; tr performs a single optimized byte-map
# for the reversible nibble complement. The same mapping is its own inverse.
transform(){
  printf '%s\n' "$1" | tr '0123456789abcdefABCDEF' 'fedcba9876543210FEDCBA9876543210'
}
while IFS= read -r line; do
  case "$line" in
    PING) printf 'PONG\n';;
    QUIT) exit 0;;
    'E '*|'D '*) transform "${line#??}";;
    *) printf 'ERR\n';;
  esac
done
