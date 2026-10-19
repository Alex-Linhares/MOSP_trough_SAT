"""Per-iterate linear laws pw(mu^j(F_n)) = A_j n + B_j on seed families, fitted with sympy on the
two smallest admissible n and tested on every other n (hold-out), incl. n = 2 for K_n (= the M chain)."""
import sympy as sp, re, warnings
warnings.filterwarnings('ignore')
from chains import chains
R=chains()
def fam(prefix):
    out={}
    for k,v in R.items():
        m=re.fullmatch(prefix+r'(\d+)',k)
        if m: out[int(m.group(1))]=v
    return out
KNOWN_M={2:[1,2,5,10,20,38,72]}  # K2 chain = M_2..M_8, certified
n=sp.Symbol('n')
for name,pre,nmin in [('K_n','K',3),('C_n','C',7),('P_n','P',5),('S_r (star K_1,r)','S',2),('W_n (wheel, n+1 vertices? nx.wheel_graph(n) has n vertices)','W',4)]:
    F=fam(pre)
    if pre=='K': F[2]=KNOWN_M[2]
    print('==',name, {k:F[k] for k in sorted(F)})
    J=max(len(v) for v in F.values())
    for j in range(J):
        pts=sorted((k,F[k][j]) for k in F if len(F[k])>j and k>=nmin)
        if len(pts)<2: 
            print(f'  j={j}: only', pts); continue
        (x1,y1),(x2,y2)=pts[:2]
        A,B=sp.symbols('A B'); s=sp.solve([A*x1+B-y1,A*x2+B-y2],[A,B])
        f=s[A]*n+s[B]
        test=[(k,F[k][j],f.subs(n,k)) for k in sorted(F) if len(F[k])>j and (k,F[k][j]) not in pts[:2]]
        bad=[t for t in test if t[1]!=t[2]]
        print(f'  j={j}: pw = {f}   fitted on n={x1},{x2}; held out {len(test)}: ' + ('all agree' if not bad else 'FAIL '+str(bad)) + '  ' + str([t[0] for t in test]))
