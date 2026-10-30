/* Exact pathwidth (= vertex separation) of trees up to 127 vertices, by the ternary lemma of
   Ellis, Sudborough & Turner (1994): for a tree S with >= 2 vertices and k >= 1,
       vs(S) >= k+1  iff  some vertex x has at least three branches (components of S - x) with vs >= k,
   so vs(S) = max(1, 1 + max_x third_largest{vs(B) : B branch of S at x}).  Memoised over connected
   vertex subsets (128-bit masks).  Independent of the subset DP and of the pathwidth_solver search;
   validated against both (see run logs).
   Input: nauty-gentreeg -p parent arrays, one tree per line (vertices 1..n, parent 0 = root).
   Usage: treepw [-v] [-p K]   -v: print pw per tree;  -p K: print parent arrays of trees with pw >= K.
   Always prints a histogram per n to stderr-like final lines "hist n=.. pw=.. count=..". */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#define MAXN 127
static int n; static u128 adj[MAXN];
static int pc(u128 x){ return __builtin_popcountll((unsigned long long)x) + __builtin_popcountll((unsigned long long)(x>>64)); }
static int lowbit(u128 x){ unsigned long long lo=(unsigned long long)x; if(lo) return __builtin_ctzll(lo); return 64+__builtin_ctzll((unsigned long long)(x>>64)); }
/* memo: open addressing, generation-stamped */
#define HBITS 22
#define HSIZE (1u<<HBITS)
static u128 *hkey; static unsigned char *hval; static unsigned *hgen; static unsigned gen=1; static unsigned long hcount=0;
static unsigned hh(u128 k){ unsigned long long a=(unsigned long long)k, b=(unsigned long long)(k>>64); unsigned long long h=a*0x9E3779B97F4A7C15ULL ^ (b+0x632BE59BD9B4E019ULL)*0xC2B2AE3D27D4EB4FULL; h^=h>>29; return (unsigned)(h>>(64-HBITS)); }
static int memo_get(u128 k){ unsigned i=hh(k); while(hgen[i]==gen){ if(hkey[i]==k) return hval[i]; i=(i+1)&(HSIZE-1);} return -1; }
static void memo_put(u128 k,int v){ unsigned i=hh(k); while(hgen[i]==gen){ i=(i+1)&(HSIZE-1);} hgen[i]=gen; hkey[i]=k; hval[i]=(unsigned char)v; if(++hcount > HSIZE/2){ fprintf(stderr,"memo full\n"); exit(2);} }
static u128 component(u128 R, int y){ u128 comp=(u128)1<<y, fr=comp; while(fr){ u128 nf=0; u128 t=fr; while(t){ int u=lowbit(t); t&=t-1; nf|=adj[u]; } nf&=R; nf&=~comp; comp|=nf; fr=nf; } return comp; }
static int vs(u128 S){
  int sz=pc(S); if(sz<=1) return 0;
  int m=memo_get(S); if(m>=0) return m;
  int best=1; u128 T=S;
  while(T){ int x=lowbit(T); T&=T-1;
    u128 R=S&~((u128)1<<x); u128 nb=adj[x]&S; if(pc(nb)<3) continue;
    /* branches */
    int vals[MAXN]; int cnt=0; int big=0; u128 rem=nb;
    u128 comps[MAXN];
    while(rem){ int y=lowbit(rem); u128 c=component(R,y); rem&=~c; comps[cnt++]=c; if(pc(c)>=2) big++; }
    if(big<3) continue;
    for(int i=0;i<cnt;i++) vals[i]= pc(comps[i])>=2 ? vs(comps[i]) : 0;
    /* third largest */
    int a=-1,b=-1,c=-1; for(int i=0;i<cnt;i++){ int v=vals[i]; if(v>a){c=b;b=a;a=v;} else if(v>b){c=b;b=v;} else if(v>c){c=v;} }
    if(c+1>best) best=c+1;
  }
  memo_put(S,best); return best;
}
int main(int argc,char**argv){
  int verbose=0, pk=1000; for(int i=1;i<argc;i++){ if(!strcmp(argv[i],"-v")) verbose=1; else if(!strcmp(argv[i],"-p")) pk=atoi(argv[++i]); }
  hkey=malloc(sizeof(u128)*HSIZE); hval=malloc(HSIZE); hgen=calloc(HSIZE,sizeof(unsigned));
  static char line[1<<16]; static long hist[MAXN+1][MAXN]; static int seen[MAXN+1];
  while(fgets(line,sizeof line,stdin)){
    int par[MAXN+1]; n=0; char*p=line; while(*p){ while(*p==' '||*p=='\t') p++; if(*p=='\n'||*p=='\r'||!*p) break; par[n++]=(int)strtol(p,&p,10); if(n>MAXN){fprintf(stderr,"too many vertices\n"); return 2;} }
    if(n==0) continue;
    memset(adj,0,sizeof(u128)*n);
    for(int v=0; v<n; v++){ if(par[v]>0){ int u=par[v]-1; adj[u]|=(u128)1<<v; adj[v]|=(u128)1<<u; } }
    gen++; hcount=0;
    int w = vs(((u128)1<<n)-1);
    hist[n][w]++; seen[n]=1;
    if(verbose) printf("%d\n",w);
    if(w>=pk){ printf("pw %d :",w); for(int v=0;v<n;v++) printf(" %d",par[v]); printf("\n"); }
  }
  for(int k=1;k<=MAXN;k++) if(seen[k]) for(int w=0;w<MAXN;w++) if(hist[k][w]) printf("hist n=%d pw=%d count=%ld\n",k,w,hist[k][w]);
  return 0;
}
