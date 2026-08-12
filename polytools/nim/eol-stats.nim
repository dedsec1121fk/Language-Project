import os, strutils
if paramCount()<1 or paramStr(1)=="--help": echo "Usage: eol-stats FILE"; quit(if paramCount()<1:2 else:0)
let s=readFile(paramStr(1));var crlf=0;var lf=0;var cr=0;var i=0
while i<s.len:
 if s[i]=='\r':
  if i+1<s.len and s[i+1]=='\n': inc crlf;inc i
  else: inc cr
 elif s[i]=='\n': inc lf
 inc i
echo "bytes=",s.len;echo "crlf=",crlf;echo "lf=",lf;echo "cr=",cr;echo "mixed=",((crlf>0).int+(lf>0).int+(cr>0).int>1)
