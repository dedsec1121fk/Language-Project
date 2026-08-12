#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
int main(int argc,char**argv){
 if(argc<2||strcmp(argv[1],"--help")==0){puts("Usage: byte-stats FILE  # byte histogram, entropy and binary/text indicators");return argc<2?2:0;}
 FILE*f=fopen(argv[1],"rb"); if(!f){perror("open");return 2;} uint64_t h[256]={0},n=0,printable=0,zero=0,newlines=0; unsigned char b[65536]; size_t r;
 while((r=fread(b,1,sizeof b,f))){for(size_t i=0;i<r;i++){unsigned x=b[i];h[x]++;n++;if(x==0)zero++;if(x=='\n')newlines++;if((x>=32&&x<=126)||x=='\n'||x=='\r'||x=='\t')printable++;}} fclose(f);
 double e=0.0;if(n)for(int i=0;i<256;i++)if(h[i]){double p=(double)h[i]/(double)n;e-=p*(log(p)/log(2.0));}
 printf("bytes=%llu\nlines_approx=%llu\nzero_bytes=%llu\nprintable_ratio=%.6f\nentropy_bits_per_byte=%.6f\n",(unsigned long long)n,(unsigned long long)(newlines+(n>0)),(unsigned long long)zero,n?(double)printable/n:0.0,e);
 puts((zero>0 || (n && (double)printable/n<0.80))?"classification=binary_or_mixed":"classification=text_like"); return 0;
}
