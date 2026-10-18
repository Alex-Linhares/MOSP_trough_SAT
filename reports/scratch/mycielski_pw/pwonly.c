// exact vertex separation (=pathwidth) and treewidth by subset DP; n <= 24
// input: lines "n m0 m1 ... m_{n-1}" (adjacency bitmasks), output "pw tw"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char *F;
int main(){
  int n; unsigned adj[32];
  F = malloc(1u<<24);
  while(scanf("%d",&n)==1){
    for(int i=0;i<n;i++) scanf("%u",&adj[i]);
    unsigned N=1u<<n, full=N-1;
    // pathwidth: f(S)=max(|boundary(S)|, min_v f(S\v)); boundary = {u in S: N(u) not subset S}
    F[0]=0;
    for(unsigned S=1;S<N;S++){
      int b=0; for(int u=0;u<n;u++) if((S>>u&1) && (adj[u]&~S)) b++;
      int best=255; for(int v=0;v<n;v++) if(S>>v&1){int x=F[S&~(1u<<v)]; if(x<best)best=x;}
      F[S]= b>best?b:best;
    }
    int pw=F[full];
    printf("%d\n",pw); fflush(stdout);
  }
}
