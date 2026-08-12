import strutils
const key=0xDF
proc transform(h:string):string =
  result=""; var i=0
  while i<h.len:
    let v=parseHexInt(h[i..i+1]) xor key
    result.add(toHex(v,2).toLowerAscii); i+=2
while true:
  try:
    let line=stdin.readLine.strip(leading=false,trailing=true,chars={'\r','\n'})
    if line=="PING": echo "PONG"; stdout.flushFile(); continue
    if line=="QUIT": break
    if line.len>=2 and (line[0]=='E' or line[0]=='D') and line[1]==' ': echo transform(line[2..^1]); stdout.flushFile()
    else: echo "ERR"; stdout.flushFile()
  except EOFError: break
