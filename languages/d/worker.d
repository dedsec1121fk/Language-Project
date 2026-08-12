import std.stdio,std.string,std.format; enum ubyte KEY=0x25;
int hv(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;return c-'A'+10;}
string transform(string h){string o="";for(size_t i=0;i+1<h.length;i+=2){auto v=cast(ubyte)((hv(h[i])<<4)|hv(h[i+1]));o~=format("%02x",v^KEY);}return o;}
void main(){stdout.setvbuf(null,_IOLBF,0);string s;while((s=stdin.readln())!is null){s=s.chomp;if(s=="PING"){writeln("PONG");continue;}if(s=="QUIT")break;if(s.length>=2&&(s[0]=='E'||s[0]=='D')&&s[1]==' ')writeln(transform(s[2..$]));else writeln("ERR");}}
