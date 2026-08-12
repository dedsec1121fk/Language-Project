#!/data/data/com.termux/files/usr/bin/zsh
transform() {
  print -rn -- "$1" | tr '0123456789abcdefABCDEF' 'fedcba9876543210FEDCBA9876543210'
  print
}
while IFS= read -r line; do
  case "$line" in
    PING) print PONG;;
    QUIT) exit 0;;
    'E '*|'D '*) transform "${line[3,-1]}";;
    *) print ERR;;
  esac
done
