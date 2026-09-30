// Hunt for counterexamples to the definite move (loop0006 item 08, paper2/search_soundness.md §4.2).
//
// Reads graphs from stdin, one per line: `n m_0 ... m_{n-1}` (self-inclusive neighbourhood
// masks, n <= 24). For every k, every free-closed state S with |O(S) - S| <= k and a
// solution, and every playable q not in S whose premise fires, checks that the child
// cl(S + q) still has a solution; prints `BAD ...` otherwise. MODE selects the premise:
//   MODE=0 (default)  the code's: open(q, S) <= close(q, S)       -> finds the counterexamples
//   MODE=1            the repair: hereditary, b(X) <= b(S + E)    -> should print no BAD
//   MODE=2            the repair's matching form                  -> should print no BAD
// With any argument, only the first firing q in index order is checked (the code's choice).
//
//   gcc -O2 -o /tmp/definite_hunt paper2/definite_hunt.c
//   python3 paper2/definite_hunt_gen.py 1 3000 10 16 | /tmp/definite_hunt
//
// The counterexamples of DEFINITE_CEX in paper2/search_check.py came from family 4 of the
// generator (the gadget) at 14-16 customers, after 90,000 graphs of the other families at
// 10-16 gave two; they were minimised by deleting vertices and edges while a BAD remained.
// Check Chu & Stuckey Thm 1 (code form) on graphs given as lines: n m0 m1 ... (neighbour masks incl self)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef uint32_t u32;
static u32 *O; static unsigned char *P;
int main(int argc,char**argv){
  int n; u32 m[32]; long graphs=0,bad=0,checks=0; int firstonly = argc>1; int badg;
  O=malloc(sizeof(u32)<<24); P=malloc(1<<24);
  while(scanf("%d",&n)==1){
    for(int i=0;i<n;i++) scanf("%u",&m[i]);
    graphs++; u32 full=(n==32)?0xffffffffu:((1u<<n)-1);
    O[0]=0; for(u32 T=1;T<=full;T++){ u32 low=T&-T; O[T]=O[T^low]|m[__builtin_ctz(T)]; if(T==full)break;}
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
        // free-closed?
        u32 fin=0; for(int c=0;c<n;c++) if((m[c]&~OS)==0) fin|=1u<<c;
        if(fin!=S) continue;
        u32 R=full&~S;
        for(int q=0;q<n;q++){ if(!(R>>q&1)) continue;
          u32 own=m[q]&~OS;
          if(__builtin_popcount(O[S|1u<<q]&~S)>k) continue;
          int close=0; for(int d=0;d<n;d++) if((R>>d&1) && ((m[d]&~OS)&~own)==0) close++;
          int mode=getenv("MODE")?atoi(getenv("MODE")):0;
          int fire = close>=__builtin_popcount(own);
          u32 U0=OS|m[q]; u32 X0=0; for(int c=0;c<n;c++) if((m[c]&~U0)==0) X0|=1u<<c;
          if(fire && mode==1){ // hereditary: for all E subset of D\{q}: b(X) <= b(S u E)
            u32 D=X0&~S&~(1u<<q); int bX=__builtin_popcount(U0&~X0);
            for(u32 E=D;;E=(E-1)&D){ u32 B=S|E; if(__builtin_popcount(O[B]&~B)<bX){fire=0;break;} if(!E)break; }
          }
          if(fire && mode==2){ // matching of size |Y|-1 from D\{q} into Y, d->y if y in o(d,S)
            u32 D=X0&~S&~(1u<<q); int need=__builtin_popcount(own)-1; int match[32]; for(int i=0;i<32;i++)match[i]=-1; int nu=0;
            for(int d=0;d<n;d++) if(D>>d&1){ // augmenting path, simple DFS
              int vis[32]={0}; int stack_d[64]; 
              // recursive lambda substitute
              int found=0;
              int aug(int dd){ u32 ys=m[dd]&~OS; for(int y=0;y<n;y++) if((ys>>y&1)&&!vis[y]){vis[y]=1; if(match[y]<0||aug(match[y])){match[y]=dd;return 1;}} return 0; }
              found=aug(d); nu+=found; (void)stack_d;
            }
            if(nu<need) fire=0;
          }
          if(fire){
            checks++;
            u32 U=OS|m[q]; u32 X=0; for(int c=0;c<n;c++) if((m[c]&~U)==0) X|=1u<<c;
            if(!P[X]){ bad++; if(1){printf("BAD k=%d S=%u q=%d n=%d masks:",k,S,q,n); for(int i=0;i<n;i++)printf(" %u",m[i]); printf("\n");} }
            if(firstonly) break;
          }
        }
      }
    }
  }
  printf("graphs %ld checks %ld bad %ld\n",graphs,checks,bad);
}
