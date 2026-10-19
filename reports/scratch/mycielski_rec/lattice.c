// U(L,L'): best vertex separation of a layout of mu(G) whose originals appear in order L,
// shadows in order L', w anywhere.  DP over (i originals placed, j shadows placed, w placed).
// Input lines: "n  adjlist...": format: n, then for each v: deg followed by neighbours; then L (n ints), then L' (n ints)
// mode via argv[1]: "one" read one (L,L') per graph; "perm" (n<=8) also: min over all L with L'=L, and min over optimal-L? (done in python)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int n,*deg,**nb;
// For a cut with originals prefix L[0..i-1], shadows prefix L'[0..j-1], w flag:
// active original v (placed): some G-neighbour unplaced original, or some G-neighbour's shadow unplaced
// active shadow v' (placed): some G-neighbour unplaced original, or w unplaced
// w active: placed and j<n
int main(){
  while(scanf("%d",&n)==1){
    deg=malloc(n*sizeof(int)); nb=malloc(n*sizeof(int*));
    for(int v=0;v<n;v++){ if(scanf("%d",&deg[v])!=1)return 1; nb[v]=malloc((deg[v]+1)*sizeof(int)); for(int k=0;k<deg[v];k++) if(scanf("%d",&nb[v][k])!=1)return 1;}
    int *L=malloc(n*sizeof(int)),*Lp=malloc(n*sizeof(int)),*po=malloc(n*sizeof(int)),*ps=malloc(n*sizeof(int));
    for(int i=0;i<n;i++){if(scanf("%d",&L[i])!=1)return 1; po[L[i]]=i;}
    for(int i=0;i<n;i++){if(scanf("%d",&Lp[i])!=1)return 1; ps[Lp[i]]=i;}
    // lastO[v] = max position (in L) of G-neighbours of v (-1 if none); lastS[v] = max position in L' of neighbours' shadows
    int *lastO=malloc(n*sizeof(int)),*lastS=malloc(n*sizeof(int));
    for(int v=0;v<n;v++){lastO[v]=-1;lastS[v]=-1;for(int k=0;k<deg[v];k++){int u=nb[v][k]; if(po[u]>lastO[v])lastO[v]=po[u]; if(ps[u]>lastS[v])lastS[v]=ps[u];}}
    // cost(i,j,w) = #{v: po[v]<i and (lastO[v]>=i or lastS[v]>=j)} + (w? #{v: ps[v]<j and lastO[v]>=i} : j) + (w && j<n)
    // O(n^3) direct; fine for n<=400 (64M)
    int N1=n+1; unsigned short *F=malloc(2*N1*N1*sizeof(unsigned short));
    #define ID(i,j,w) (((w)*N1+(i))*N1+(j))
    for(int w=0;w<2;w++) for(int i=0;i<=n;i++) for(int j=0;j<=n;j++){
      int best=65535;
      if(i==0&&j==0&&w==0){F[ID(0,0,0)]=0;continue;}
      if(i>0){int y=F[ID(i-1,j,w)]; if(y<best)best=y;}
      if(j>0){int y=F[ID(i,j-1,w)]; if(y<best)best=y;}
      if(w){int y=F[ID(i,j,0)]; if(y<best)best=y;}
      int c=0;
      for(int a=0;a<i;a++){int v=L[a]; if(lastO[v]>=i||lastS[v]>=j) c++;}
      if(w){ for(int b=0;b<j;b++){int v=Lp[b]; if(lastO[v]>=i) c++;} if(j<n) c++; } else c+=j;
      F[ID(i,j,w)]= c>best?c:best;
    }
    printf("%d",F[ID(n,n,1)]);
    if(getenv("LAYOUT")){ // traceback: tokens v (original), n+v (shadow), 2n (w), printed in layout order
      int *seq=malloc((2*n+1)*sizeof(int)); int k=2*n+1; int i=n,j=n,w=1;
      while(i||j||w){ int best=65536,bi=-1,bj=-1,bw=-1;
        if(i>0 && F[ID(i-1,j,w)]<best){best=F[ID(i-1,j,w)];bi=i-1;bj=j;bw=w;}
        if(j>0 && F[ID(i,j-1,w)]<best){best=F[ID(i,j-1,w)];bi=i;bj=j-1;bw=w;}
        if(w && F[ID(i,j,0)]<best){best=F[ID(i,j,0)];bi=i;bj=j;bw=0;}
        if(bi<i) seq[--k]=L[i-1]; else if(bj<j) seq[--k]=n+Lp[j-1]; else seq[--k]=2*n;
        i=bi;j=bj;w=bw; }
      printf(" |"); for(int t=0;t<2*n+1;t++) printf(" %d",seq[t]); free(seq);
    }
    printf("\n"); fflush(stdout);
    free(F);free(L);free(Lp);free(po);free(ps);free(lastO);free(lastS);
    for(int v=0;v<n;v++)free(nb[v]); free(nb);free(deg);
  }
}
