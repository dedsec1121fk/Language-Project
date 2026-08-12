/^PING$/ {
  s/.*/PONG/
  p
  d
}
/^QUIT$/ q
/^[ED] / {
  s/^[ED] //
  y/0123456789abcdef/fedcba9876543210/
  p
  d
}
s/.*/ERR/
p
