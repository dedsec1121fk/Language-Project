BEGIN { key=45 }
function hexval(c, p){ p=index("0123456789abcdef",tolower(c)); return p-1 }
function hex2(n){ return substr("0123456789abcdef",int(n/16)+1,1) substr("0123456789abcdef",(n%16)+1,1) }
function bxor(a,b, r,p){r=0;p=1;while(a||b){if((a%2)!=(b%2))r+=p;a=int(a/2);b=int(b/2);p*=2}return r}
$0=="PING" {print "PONG"; fflush(); next}
$0=="QUIT" {exit}
/^[ED] [0-9A-Fa-f]*$/ { h=substr($0,3); out=""; for(i=1;i<=length(h);i+=2){v=hexval(substr(h,i,1))*16+hexval(substr(h,i+1,1));out=out hex2(bxor(v,key))} print out; fflush(); next }
{print "ERR"; fflush()}
