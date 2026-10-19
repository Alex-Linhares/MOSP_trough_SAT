// Simulated annealing over (L, L'): originals order and shadows order of a layout of mu(G),
// objective = (U, cnt): U = best width over interleavings (w anywhere), cnt = min #cuts at width U.
// usage: anneal iters seed T0 < input ("n  deg nbrs... L Lp")   prints "U cnt | L | Lp"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static int n,*deg,**nb,*L,*Lp,*po,*ps,*lastO,*lastS,*cO,*cS;
static int *F,*Cn; static int *hist;
static void eval(int *U,int *cnt){
  for(int v=0;v<n;v++){po[L[v]]=v;ps[Lp[v]]=v;}
  for(int v=0;v<n;v++){lastO[v]=-1;lastS[v]=-1;for(int k=0;k<deg[v];k++){int u=nb[v][k];if(po[u]>lastO[v])lastO[v]=po[u];if(ps[u]>lastS[v])lastS[v]=ps[u];}}
  int N1=n+1;
  // cost tables: c0(i,j) without w, c1(i,j) with w
  // originals part O(i,j) = #{a<i: lastO>=i} + #{a<i: lastO<i, lastS>=j}
  // shadows with w: S(i,j) = #{b<j: lastO[Lp[b]]>=i}; without w: j
  for(int i=0;i<=n;i++){
    int base=0; for(int t=0;t<=n;t++) hist[t]=0;
    for(int a=0;a<i;a++){int v=L[a]; if(lastO[v]>=i) base++; else if(lastS[v]>=0) hist[lastS[v]]++;}
    // #{lastS >= j} suffix
    int suf=0; for(int j=n;j>=0;j--){ if(j<n) suf+=hist[j]; cO[i*N1+j]=base+suf; }
    int s=0; cS[i*N1+0]=0; for(int b=0;b<n;b++){ if(lastO[Lp[b]]>=i) s++; cS[i*N1+b+1]=s; }
  }
  #define ID(i,j,w) (((w)*N1+(i))*N1+(j))
  for(int w=0;w<2;w++) for(int i=0;i<=n;i++) for(int j=0;j<=n;j++){
    if(!i&&!j&&!w){F[0]=0;continue;}
    int best=1<<30;
    if(i>0&&F[ID(i-1,j,w)]<best)best=F[ID(i-1,j,w)];
    if(j>0&&F[ID(i,j-1,w)]<best)best=F[ID(i,j-1,w)];
    if(w&&F[ID(i,j,0)]<best)best=F[ID(i,j,0)];
    int c=cO[i*N1+j]+(w?cS[i*N1+j]+(j<n):j);
    F[ID(i,j,w)]=c>best?c:best;
  }
  int u=F[ID(n,n,1)]; *U=u;
  for(int w=0;w<2;w++) for(int i=0;i<=n;i++) for(int j=0;j<=n;j++){
    int c=cO[i*N1+j]+(w?cS[i*N1+j]+(j<n):j);
    if(!i&&!j&&!w){Cn[0]=0;continue;}
    if(c>u){Cn[ID(i,j,w)]=1<<29;continue;}
    int best=1<<29;
    if(i>0&&Cn[ID(i-1,j,w)]<best)best=Cn[ID(i-1,j,w)];
    if(j>0&&Cn[ID(i,j-1,w)]<best)best=Cn[ID(i,j-1,w)];
    if(w&&Cn[ID(i,j,0)]<best)best=Cn[ID(i,j,0)];
    Cn[ID(i,j,w)]=best+(c==u);
  }
  *cnt=Cn[ID(n,n,1)];
}
static void move(int *A,int from,int to){int x=A[from]; if(from<to) memmove(A+from,A+from+1,(to-from)*sizeof(int)); else memmove(A+to+1,A+to,(from-to)*sizeof(int)); A[to]=x;}
static int idx(int *A,int x){for(int i=0;i<n;i++) if(A[i]==x) return i; return -1;}
int main(int argc,char**argv){
  long iters=atol(argv[1]); srand(atoi(argv[2])); double T0=atof(argv[3]);
  if(scanf("%d",&n)!=1) return 1;
  deg=malloc(n*sizeof(int)); nb=malloc(n*sizeof(int*));
  for(int v=0;v<n;v++){ if(scanf("%d",&deg[v])!=1)return 1; nb[v]=malloc((deg[v]+1)*sizeof(int)); for(int k=0;k<deg[v];k++) if(scanf("%d",&nb[v][k])!=1)return 1;}
  L=malloc(n*sizeof(int));Lp=malloc(n*sizeof(int));po=malloc(n*sizeof(int));ps=malloc(n*sizeof(int));lastO=malloc(n*sizeof(int));lastS=malloc(n*sizeof(int));
  for(int i=0;i<n;i++) if(scanf("%d",&L[i])!=1) return 1;
  for(int i=0;i<n;i++) if(scanf("%d",&Lp[i])!=1) return 1;
  int N1=n+1; F=malloc(2*N1*N1*sizeof(int)); Cn=malloc(2*N1*N1*sizeof(int)); cO=malloc(N1*N1*sizeof(int)); cS=malloc(N1*N1*sizeof(int)); hist=malloc((N1+1)*sizeof(int));
  int U,cnt; eval(&U,&cnt); double cur=U*1000.0+cnt; int bU=U,bc=cnt;
  int *bL=malloc(n*sizeof(int)),*bLp=malloc(n*sizeof(int)); memcpy(bL,L,n*sizeof(int)); memcpy(bLp,Lp,n*sizeof(int));
  fprintf(stderr,"start %d %d\n",U,cnt);
  for(long it=0;it<iters;it++){
    double T=T0*(1.0-(double)it/iters)+1e-9;
    int kind=rand()%3; int x=rand()%n; int span=(rand()%4)?1+rand()%8:1+rand()%(n/4+1); int d=(rand()%(2*span+1))-span;
    int f1=idx(L,x),f2=idx(Lp,x); int t1=f1+d,t2=f2+d; if(t1<0)t1=0; if(t1>=n)t1=n-1; if(t2<0)t2=0; if(t2>=n)t2=n-1;
    if(kind!=1) move(L,f1,t1); if(kind!=0) move(Lp,f2,t2);
    eval(&U,&cnt); double nv=U*1000.0+cnt;
    if(nv<=cur || exp((cur-nv)/T) > (double)rand()/RAND_MAX){ cur=nv; if(U<bU||(U==bU&&cnt<bc)){bU=U;bc=cnt;memcpy(bL,L,n*sizeof(int));memcpy(bLp,Lp,n*sizeof(int)); fprintf(stderr,"it %ld best %d %d\n",it,bU,bc);} }
    else { if(kind!=1) move(L,t1,f1); if(kind!=0) move(Lp,t2,f2); }
  }
  printf("%d %d |",bU,bc); for(int i=0;i<n;i++)printf(" %d",bL[i]); printf(" |"); for(int i=0;i<n;i++)printf(" %d",bLp[i]); printf("\n");
}
