
/* treepw_big: same algorithm as treepw.c with bitsets of W*64 bits (trees up to 512 vertices). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define W 8
#define MAXN (64*W)
typedef struct { unsigned long long w[W]; } bs;
static int n; static bs adj[MAXN];
static int pc(const bs*x){ int c=0; for(int i=0;i<W;i++) c+=__builtin_popcountll(x->w[i]); return c; }
static int lowbit(const bs*x){ for(int i=0;i<W;i++) if(x->w[i]) return 64*i+__builtin_ctzll(x->w[i]); return -1; }
static int isz(const bs*x){ for(int i=0;i<W;i++) if(x->w[i]) return 0; return 1; }
static void clr(bs*x){ memset(x,0,sizeof*x); }
static void setb(bs*x,int v){ x->w[v>>6]|=1ULL<<(v&63); }
static int eq(const bs*a,const bs*b){ return memcmp(a,b,sizeof*a)==0; }
#define HBITS 24
#define HSIZE (1u<<HBITS)
static bs *hkey; static unsigned char *hval; static unsigned *hgen; static unsigned gen=1; static unsigned long hcount=0;
static unsigned hh(const bs*k){ unsigned long long h=0x9E3779B97F4A7C15ULL; for(int i=0;i<W;i++){ h^=k->w[i]; h*=0xC2B2AE3D27D4EB4FULL; h^=h>>29; } return (unsigned)(h>>(64-HBITS)); }
static int memo_get(const bs*k){ unsigned i=hh(k); while(hgen[i]==gen){ if(eq(&hkey[i],k)) return hval[i]; i=(i+1)&(HSIZE-1);} return -1; }
static void memo_put(const bs*k,int v){ unsigned i=hh(k); while(hgen[i]==gen){ i=(i+1)&(HSIZE-1);} hgen[i]=gen; hkey[i]=*k; hval[i]=(unsigned char)v; if(++hcount > HSIZE/2){ fprintf(stderr,"memo full\n"); exit(2);} }
static void component(const bs*R,int y,bs*comp){ clr(comp); setb(comp,y); bs fr=*comp; while(!isz(&fr)){ bs nf; clr(&nf); bs t=fr; while(!isz(&t)){ int u=lowbit(&t); t.w[u>>6]&=~(1ULL<<(u&63)); for(int i=0;i<W;i++) nf.w[i]|=adj[u].w[i]; } for(int i=0;i<W;i++){ nf.w[i]&=R->w[i]; nf.w[i]&=~comp->w[i]; comp->w[i]|=nf.w[i]; } fr=nf; } }
static int vs(const bs*S){
  int sz=pc(S); if(sz<=1) return 0;
  int m=memo_get(S); if(m>=0) return m;
  int best=1; bs T=*S;
  while(!isz(&T)){ int x=lowbit(&T); T.w[x>>6]&=~(1ULL<<(x&63));
    bs R=*S; R.w[x>>6]&=~(1ULL<<(x&63)); bs nb; for(int i=0;i<W;i++) nb.w[i]=adj[x].w[i]&S->w[i]; if(pc(&nb)<3) continue;
    int vals[64]; int cnt=0; int big=0; bs rem=nb; bs comps[64];
    while(!isz(&rem)){ int y=lowbit(&rem); component(&R,y,&comps[cnt]); for(int i=0;i<W;i++) rem.w[i]&=~comps[cnt].w[i]; if(pc(&comps[cnt])>=2) big++; cnt++; if(cnt>=64){fprintf(stderr,"degree too high\n"); exit(2);} }
    if(big<3) continue;
    for(int i=0;i<cnt;i++) vals[i]= pc(&comps[i])>=2 ? vs(&comps[i]) : 0;
    int a=-1,b=-1,c=-1; for(int i=0;i<cnt;i++){ int v=vals[i]; if(v>a){c=b;b=a;a=v;} else if(v>b){c=b;b=v;} else if(v>c){c=v;} }
    if(c+1>best) best=c+1;
  }
  memo_put(S,best); return best;
}
int main(void){
  hkey=malloc(sizeof(bs)*HSIZE); hval=malloc(HSIZE); hgen=calloc(HSIZE,sizeof(unsigned));
  static char line[1<<16];
  while(fgets(line,sizeof line,stdin)){
    static int par[MAXN+1]; n=0; char*p=line; while(*p){ while(*p==' '||*p=='\t') p++; if(*p=='\n'||*p=='\r'||!*p) break; par[n++]=(int)strtol(p,&p,10); if(n>MAXN){fprintf(stderr,"too many vertices\n"); return 2;} }
    if(n==0) continue;
    for(int v=0;v<n;v++) clr(&adj[v]);
    for(int v=0; v<n; v++){ if(par[v]>0){ int u=par[v]-1; setb(&adj[u],v); setb(&adj[v],u); } }
    gen++; hcount=0; bs full; clr(&full); for(int v=0;v<n;v++) setb(&full,v);
    printf("%d\n", vs(&full)); fflush(stdout);
  }
  return 0;
}
