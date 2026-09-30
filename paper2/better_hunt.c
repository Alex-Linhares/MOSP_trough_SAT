// Hunt for counterexamples to the better move (loop0006 item 10, paper2/search_soundness.md §4.4).
//
// Reads graphs from stdin, one per line: `n m_0 ... m_{n-1}` (self-inclusive neighbourhood
// masks, n <= 24), as paper2/definite_hunt.c does. For every k and every free-closed state S
// with |O(S) - S| <= k and a solution, runs the node filter of §2.2-§2.4 in the fixed order
// (definite -> subset -> better, L = 0) and checks:
//
//   PAIR  a better-move link r -> q among the subset survivors (q earlier) whose premise holds
//         while S.r has a solution and S.q has none: the rule's own conclusion is false;
//   NODE  the definite move did not fire and no customer the filter keeps has a solution:
//         the filter lost the last solution at the node, through the better move.
//
// MODE selects the better-move premise:
//   MODE=0 (default)  the code's corrected premise (§2.4 premises 3 and 4)
//   MODE=1            Bug A: the close count also counts the customers r finishes
//   MODE=2            the repair: premise 3, and q hereditarily definite at cl(S + r)
// The definite move is always the code's (so NODE is only reported where it does not fire).
//
//   gcc -O2 -o /tmp/better_hunt paper2/better_hunt.c
//   python3 paper2/better_hunt_gen.py 101 400 | /tmp/better_hunt          (false links, no lost node)
//   python3 paper2/better_hunt_gen.py 101 400 | MODE=2 /tmp/better_hunt   (the repair: nothing)
//
// Item 10's hunt: 25,300 graphs at 12-18 vertices (9,600 relabelled gadget graphs of
// definite_hunt_gen.py family 4, and 15,700 from better_hunt_gen.py): 798 PAIR lines, no NODE
// line; under MODE=2 on the 11,200 of seeds 101-128, neither. MODE=1 on 12,000 random sparse
// and cover graphs at 11-13 gave 3 PAIR lines; the 12-vertex one is bugA_counterexample.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef uint32_t u32;
static u32 *O; static unsigned char *P;
static int n; static u32 m[32];
static u32 finOf(u32 U){ u32 X=0; for(int c=0;c<n;c++) if((m[c]&~U)==0) X|=1u<<c; return X; }
static int b(u32 T){ return __builtin_popcount(O[T]&~T); }
static int hereditary(u32 T,int q){ // IsHereditarilyDefinite at T for q
  if(T>>q&1) return 1;
  u32 X=finOf(O[T]|m[q]); int bX=b(X); u32 D=X&~T&~(1u<<q);
  for(u32 E=D;;E=(E-1)&D){ if(b(T|E)<bX) return 0; if(!E) break; }
  return 1;
}
static int premise(u32 S,int k,int r,int q,int mode){
  u32 Sr=S|1u<<r, Or=O[S]|m[r];
  if(__builtin_popcount((Or|m[q])&~Sr)>k) return 0;                 // premise 3
  if(mode==2) return hereditary(finOf(Or),q);
  u32 own=m[q]&~Or; int closed=0;
  for(int d=0;d<n;d++){ if(Sr>>d&1) continue; u32 left=m[d]&~Or;
    if((left||mode==1)&&(left&~own)==0) closed++; }                  // premise 4
  return closed>=__builtin_popcount(own);
}
int main(void){
  long graphs=0,pairs=0,pairbad=0,nodes=0,nodebad=0; int mode=getenv("MODE")?atoi(getenv("MODE")):0;
  O=malloc(sizeof(u32)<<24); P=malloc(1<<24);
  while(scanf("%d",&n)==1){
    for(int i=0;i<n;i++) if(scanf("%u",&m[i])!=1) return 1;
    graphs++; u32 full=(1u<<n)-1;
    O[0]=0; for(u32 T=1;T<=full;T++){ u32 low=T&-T; O[T]=O[T^low]|m[__builtin_ctz(T)]; }
    for(int k=1;k<=n;k++){
      for(long T=full;T>=0;T--){
        if((u32)T==full){P[T]=1;continue;}
        unsigned char ok=0; u32 rem=full&~(u32)T;
        while(rem){u32 low=rem&-rem; rem^=low; u32 T2=(u32)T|low;
          if(__builtin_popcount(O[T2]&~(u32)T)<=k && P[T2]){ok=1;break;}}
        P[T]=ok;
      }
      for(u32 S=0;S<full;S++){
        if(!P[S]) continue;
        u32 OS=O[S]; if(__builtin_popcount(OS&~S)>k) continue;
        if(finOf(OS)!=S) continue;
        u32 R=full&~S; int Pl[32],np=0;
        for(int c=0;c<n;c++) if((R>>c&1) && __builtin_popcount(O[S|1u<<c]&~S)<=k) Pl[np++]=c;
        if(!np) continue;
        nodes++;
        // definite move (code form): first q in index order with close >= open
        int fired=0;
        for(int i=0;i<np&&!fired;i++){ int q=Pl[i]; u32 own=m[q]&~OS; int cl=0;
          for(int d=0;d<n;d++) if((R>>d&1)&&((m[d]&~OS)&~own)==0) cl++;
          if(cl>=__builtin_popcount(own)) fired=1; }
        if(fired) continue;
        // subset rule over R(S) with the index tie-break, fallback
        int W[32],nw=0;
        for(int i=0;i<np;i++){ int r=Pl[i]; u32 own=m[r]&~OS; int dom=0;
          for(int d=0;d<n&&!dom;d++){ if(!(R>>d&1)||d==r) continue; u32 o=m[d]&~OS;
            if((o&~own)==0 && (o!=own || d<r)) dom=1; }
          if(!dom) W[nw++]=r; }
        if(!nw){ for(int i=0;i<np;i++) W[i]=Pl[i]; nw=np; }
        // better move, L = 0
        int anysol=0;
        for(int ri=0;ri<nw;ri++){ int r=W[ri]; int gone=0;
          for(int qi=0;qi<ri&&!gone;qi++){ int q=W[qi];
            if(premise(S,k,r,q,mode)){ gone=1; pairs++;
              u32 Xr=finOf(OS|m[r]), Xq=finOf(OS|m[q]);
              if(P[Xr]&&!P[Xq]){ pairbad++;
                printf("PAIR k=%d S=%u r=%d q=%d n=%d masks:",k,S,r,q,n); for(int i=0;i<n;i++)printf(" %u",m[i]); printf("\n"); } } }
          if(!gone && P[finOf(OS|m[r])]) anysol=1; }
        if(!anysol){ nodebad++;
          printf("NODE k=%d S=%u n=%d masks:",k,S,n); for(int i=0;i<n;i++)printf(" %u",m[i]); printf("\n"); }
      }
    }
  }
  printf("graphs %ld nodes %ld pairs %ld pairbad %ld nodebad %ld\n",graphs,nodes,pairs,pairbad,nodebad);
  return 0;
}
