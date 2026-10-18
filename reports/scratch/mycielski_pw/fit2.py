import numpy as np
from scipy.optimize import least_squares
K=np.arange(2,9); A=np.array([1,2,5,10,20,38,72.]); n=3*2.0**(K-2)-1
fam={
 'A*2^k*k^g':(lambda p,k,n:p[0]*2.0**k*k**p[1],[0.1,0]),
 'A*2^k*k^g+B':(lambda p,k,n:p[0]*2.0**k*k**p[1]+p[2],[0.1,0,0]),
 'A*n^g':(lambda p,k,n:p[0]*n**p[1],[0.5,1]),
 'A*n^g+B':(lambda p,k,n:p[0]*n**p[1]+p[2],[0.5,1,0]),
 'A*n/k^g':(lambda p,k,n:p[0]*n/k**p[1],[0.5,0.5]),
 'A*n/k^g+B':(lambda p,k,n:p[0]*n/k**p[1]+p[2],[0.5,0.5,0]),
 'A*n/log2(n)^g':(lambda p,k,n:p[0]*n/np.log2(n+1)**p[1],[0.5,0.5]),
 'A*b^k':(lambda p,k,n:p[0]*p[1]**k,[0.3,1.9]),
 'A*b^k+B':(lambda p,k,n:p[0]*p[1]**k+p[2],[0.3,1.9,0]),
 'A*n - B*k*2^k/... (A n + B k + C)':(lambda p,k,n:p[0]*n+p[1]*k+p[2],[0.4,0,0]),
}
def fitpred(f,p0,idx):
    r=least_squares(lambda p:f(p,K[idx],n[idx])-A[idx],p0,max_nfev=20000)
    return r.x
for name,(f,p0) in fam.items():
    npar=len(p0)
    out=[]
    for train in [list(range(7-2-npar,5)), list(range(7-npar,7)), list(range(1,1+npar))]:
        idx=np.array(train); test=[i for i in range(1,7) if i not in train]
        p=fitpred(f,p0,idx)
        pr=f(p,K,n); p9=f(p,np.array([9.]),np.array([383.]))[0]
        out.append(("train k="+",".join(str(K[i]) for i in train), "maxerr held-out(k>=3) %.2f"%max(abs(pr[i]-A[i]) for i in test), "M9 %.1f"%p9, np.round(p,4)))
    print(name); [print("   ",o) for o in out]
