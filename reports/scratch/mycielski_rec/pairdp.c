// vs(mu(G)) by DP over (X = placed originals, Y = placed shadows, w placed?), n <= 11.
// input "n m0..m_{n-1}"; output: free wfirst wlast trail lead
//   trail: only states with Y subset of X (shadow placed after its original)
//   lead : only states with X subset of Y
#include <stdio.h>
#include <stdlib.h>
typedef unsigned long long u64;
static int n; static unsigned adj[32];
static unsigned char *F;
static int cost(unsigned X,unsigned Y,int w){
  int c=0; unsigned full=(1u<<n)-1;
  for(int v=0;v<n;v++){
    if(X>>v&1) if((adj[v]&~X)||(adj[v]&~Y)) c++;
    if(Y>>v&1){ if(!w) c++; else if(adj[v]&~X) c++; }
  }
  if(w && Y!=full) c++;
  return c;
}
static int run(int mode){ // 0 free,1 wfirst,2 wlast,3 trail,4 lead
  unsigned N=1u<<n, full=N-1;
  for(int w=0;w<2;w++)
  for(unsigned X=0;X<N;X++) for(unsigned Y=0;Y<N;Y++){
    u64 id=((u64)w<<(2*n))|((u64)Y<<n)|X;
    int ok=1;
    if(mode==1 && !w && (X||Y)) ok=0;
    if(mode==2 && w && !(X==full&&Y==full)) ok=0;
    if(mode==3 && (Y&~X)) ok=0;
    if(mode==4 && (X&~Y)) ok=0;
    if(!ok){F[id]=255;continue;}
    if(!X&&!Y&&!w){F[id]=0;continue;}
    int best=255;
    for(int v=0;v<n;v++){
      if(X>>v&1){int y=F[((u64)w<<(2*n))|((u64)Y<<n)|(X&~(1u<<v))]; if(y<best)best=y;}
      if(Y>>v&1){int y=F[((u64)w<<(2*n))|((u64)(Y&~(1u<<v))<<n)|X]; if(y<best)best=y;}
    }
    if(w){int y=F[((u64)Y<<n)|X]; if(y<best)best=y;}
    if(best==255){F[id]=255;continue;}
    int c=cost(X,Y,w); F[id]=c>best?c:best;
  }
  return F[((u64)1<<(2*n))|((u64)full<<n)|full];
}
int main(){
  F=malloc(1ull<<23);
  while(scanf("%d",&n)==1){
    for(int i=0;i<n;i++) if(scanf("%u",&adj[i])!=1) return 1;
    printf("%d %d %d %d %d\n",run(0),run(1),run(2),run(3),run(4)); fflush(stdout);
  }
}
