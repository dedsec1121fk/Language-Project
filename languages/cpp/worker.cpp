#include <iostream>
#include <string>
#include <cctype>
using namespace std; static constexpr unsigned KEY=0x43;
int hv(char c){c=tolower((unsigned char)c);return c>='a'?c-'a'+10:c-'0';}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);string s;while(getline(cin,s)){if(s=="PING"){cout<<"PONG\n"<<flush;continue;}if(s=="QUIT")break;if(s.size()>=2&&(s[0]=='E'||s[0]=='D')&&s[1]==' '){static const char *x="0123456789abcdef";for(size_t i=2;i+1<s.size();i+=2){unsigned v=(hv(s[i])<<4)|hv(s[i+1]);v^=KEY;cout<<x[v>>4]<<x[v&15];}cout<<'\n'<<flush;}else cout<<"ERR\n"<<flush;}}
