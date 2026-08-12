#include <iostream>
#include <fstream>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <cctype>
#include <string>
using namespace std;
int main(int argc,char**argv){if(argc<2||string(argv[1])=="--help"){cout<<"Usage: word-frequency FILE [LIMIT]\n";return argc<2?2:0;}int lim=argc>2?max(1,atoi(argv[2])):20;ifstream f(argv[1]);if(!f){cerr<<"open failed\n";return 2;}unordered_map<string,long long> m;string w;char c;long long total=0;while(f.get(c)){unsigned char u=(unsigned char)c;if(isalnum(u)||c=='_')w+=char(tolower(u));else if(!w.empty()){m[w]++;total++;w.clear();}}if(!w.empty()){m[w]++;total++;}vector<pair<string,long long>>v(m.begin(),m.end());sort(v.begin(),v.end(),[](auto&a,auto&b){return a.second!=b.second?a.second>b.second:a.first<b.first;});cout<<"total_words="<<total<<"\nunique_words="<<m.size()<<"\n";for(int i=0;i<lim&&i<(int)v.size();i++)cout<<v[i].second<<"\t"<<v[i].first<<"\n";}
