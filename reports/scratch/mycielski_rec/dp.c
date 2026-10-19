// Exact subset DP for small graphs (n <= 27).
// input lines: "n flags m0 ... m_{n-1}"  (adjacency bitmasks, decimal); flags bit0: also treewidth
// output: "pw tw tight lastmin firstmin | layout v1 ... vn"
//   pw      = vertex separation = pathwidth
//   tw      = treewidth (-1 if not requested)
//   tight   = min over optimal layouts of #prefixes (1..n-1) whose boundary equals pw
//   lastmin = min over v of vs of layouts ending with v  (= pw iff some optimal layout ends at v); printed as list per vertex
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
static unsigned char *F,*R,*T;
static int n; static u64 adj[64];
static inline int bnd(u64 S){int b=0;u64 x=S;while(x){int u=__builtin_ctzll(x);x&=x-1;if(adj[u]&~S)b++;}return b;}
int main(){
  F=malloc(1ull<<27);R=malloc(1ull<<27);T=malloc(1ull<<27);
  int flags;
  while(scanf("%d %d",&n,&flags)==2){
    for(int i=0;i<n;i++) scanf("%llu",&adj[i]);
    u64 N=1ull<<n, full=N-1;
    F[0]=0;
    for(u64 S=1;S<N;S++){
      int b=bnd(S); int best=255; u64 x=S;
      while(x){int v=__builtin_ctzll(x);x&=x-1;int y=F[S&~(1ull<<v)];if(y<best)best=y;}
      F[S]=b>best?b:best;
    }
    int pw=F[full];
    // R(S): best max boundary over prefixes strictly containing S ... define R(S)=max(b(S), min_u R(S+u)), R(full)=0
    R[full]=0;
    for(u64 S=full;S-->0;){
      int b=bnd(S); int best=255; u64 x=full&~S;
      while(x){int u=__builtin_ctzll(x);x&=x-1;int y=R[S|(1ull<<u)];if(y<best)best=y;}
      R[S]=b>best?b:best;
    }
    // tight count: T(S) = min #tight prefixes among width-pw orders of S (prefixes nonempty, proper)
    T[0]=0;
    for(u64 S=1;S<N;S++){
      int b=bnd(S); if(b>pw){T[S]=255;continue;}
      int best=255; u64 x=S;
      while(x){int v=__builtin_ctzll(x);x&=x-1;int y=T[S&~(1ull<<v)];if(y<best)best=y;}
      if(best==255){T[S]=255;continue;}
      T[S]=best+((b==pw && S!=full)?1:0);
    }
    int tight=T[full];
    // layout reconstruction
    int lay[64]; u64 S=full;
    for(int i=n-1;i>=0;i--){u64 x=S;int ch=-1;while(x){int v=__builtin_ctzll(x);x&=x-1;if(F[S&~(1ull<<v)]<=pw){ch=v;break;}}lay[i]=ch;S&=~(1ull<<ch);}
    int tw=-1;
    if(flags&1){
      T[0]=0;
      for(u64 S=1;S<N;S++){
        int best=255; u64 xx=S;
        while(xx){int v=__builtin_ctzll(xx);xx&=xx-1;
          u64 Rr=S&~(1ull<<v); int x=T[Rr]; if(x>=best) continue;
          u64 vis=1ull<<v, fr=1ull<<v, out=0;
          while(fr){int u=__builtin_ctzll(fr);fr&=fr-1;u64 nb=adj[u]&~vis;vis|=nb;out|=nb&~Rr;fr|=nb&Rr;}
          int q=__builtin_popcountll(out&~(1ull<<v)); int y=x>q?x:q; if(y<best)best=y;}
        T[S]=best;
      }
      tw=T[full];
    }
    printf("%d %d %d",pw,tw,tight);
    printf(" | last");
    for(int v=0;v<n;v++){int d=__builtin_popcountll(adj[v]);int a=F[full&~(1ull<<v)];printf(" %d",a>d?a:d);}
    printf(" | first");
    for(int v=0;v<n;v++){printf(" %d",R[1ull<<v]>bnd(1ull<<v)?R[1ull<<v]:bnd(1ull<<v));}
    printf(" | layout");
    for(int i=0;i<n;i++)printf(" %d",lay[i]);
    printf("\n");fflush(stdout);
  }
}
