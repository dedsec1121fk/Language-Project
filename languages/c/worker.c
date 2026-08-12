#include <stdio.h>
#include <string.h>
#include <ctype.h>
#define KEY 0x37
static int hv(char c){c=(char)tolower((unsigned char)c);return c>='a'?c-'a'+10:c-'0';}
int main(void){char line[1048578];while(fgets(line,sizeof line,stdin)){line[strcspn(line,"\r\n")]=0;if(!strcmp(line,"PING")){puts("PONG");fflush(stdout);continue;}if(!strcmp(line,"QUIT"))break;if((line[0]=='E'||line[0]=='D')&&line[1]==' '){char *h=line+2;size_t n=strlen(h);for(size_t i=0;i+1<n;i+=2){unsigned v=(unsigned)((hv(h[i])<<4)|hv(h[i+1]));printf("%02x",v^KEY);}putchar('\n');fflush(stdout);}else{puts("ERR");fflush(stdout);}}return 0;}
