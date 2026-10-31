"""CHECKER: numerical attack on the ANALYST's (I1)-(I4), assembly (A), asymptotic bounds, Theorem B."""
import sys
sys.path.insert(0, '/home/al/dev/MOSP/reports/scratch/first_moment')
from checker_beta_star import beta_star, H
import mpmath as mp
from math import log, exp, floor, ceil, sqrt, e
import numpy as np
mp.mp.dps = 40

def phi(x):
    return 0.0 if x <= 0 else -x*log(x)

# (I1) trinomial <= exp(n H)
worst = -1e9
for n in range(1, 301):
    for i in range(0, n+1):
        for j in range(0, n+1-i):
            l = n-i-j
            lhs = mp.log(mp.factorial(n)/(mp.factorial(i)*mp.factorial(j)*mp.factorial(l)))
            rhs = n*(phi(i/n)+phi(j/n)+phi(l/n))
            worst = max(worst, float(lhs-rhs))
print(f"(I1) max over n<=300 of ln(multinomial) - nH = {worst:.3e}  (must be <= 0)")

# (I3) shift lemma
worst = -1e9; worst_at=None
xs = np.linspace(0, 1, 2001)
for d in np.linspace(1e-6, 1/e, 400):
    for x in xs:
        y = x + d
        if y > 1: break
        v = abs(phi(x)-phi(y)) - phi(d)
        if v > worst: worst, worst_at = v, (x, d)
print(f"(I3) max of |phi(x)-phi(x+d)| - phi(d) over d<=1/e: {worst:.3e} at {worst_at} (must be <= 0)")
# and beyond 1/e, does it fail?  (not needed, but documents the limit)
fails = []
for d in np.linspace(1/e+0.01, 0.6, 30):
    for x in xs:
        y = x+d
        if y > 1: break
        if abs(phi(x)-phi(y)) - phi(d) > 1e-12: fails.append((round(x,3), round(d,3))); break
print(f"(I3) beyond 1/e, first failures (x,d): {fails[:5]}")
# monotonicity of phi on [0,1/e] (needed to pass from d<=1/n to phi(1/n))
print(f"(I3') phi increasing on [0,1/e]: {all(phi(a)<=phi(b) for a,b in zip(np.linspace(0,1/e,1000)[:-1], np.linspace(0,1/e,1000)[1:]))}")

# (I4) and the shift bookkeeping, exhaustively over n<=400, beta grid
bad = []
for n in range(3, 401):
    for beta in np.linspace(0.001, 0.999, 500):
        k = floor(beta*n); a = (1-beta)/2
        t = (n-k+1)//2
        if not (a*n - 1e-9 <= t < a*n+1 + 1e-9): bad.append(('t range', n, beta, t, a*n))
        if not (t*(t-1) >= a*n*(a*n-1) - 1e-9): bad.append(('t(t-1)', n, beta))
        u, v, w = t/n, (t-1)/n, (n-2*t+1)/n
        if w < 0: bad.append(('w<0', n, beta))
        for p_, q_ in ((u,a),(v,a),(w,1-2*a)):
            if abs(p_-q_) > 1/n + 1e-12: bad.append(('shift>1/n', n, beta, p_, q_))
print(f"(I4)+shifts: violations over n<=400: {len(bad)}  {bad[:5]}")

# (A) assembled bound vs exact (0): exact log RHS <= -delta n + 3 ln n + c a ?
def log_exact(n, k, c):
    t = (n-k+1)//2
    if c >= n: return float('-inf')
    return float(mp.re(mp.log(mp.binomial(n,t)) + mp.log(mp.binomial(n-t,t-1)) + t*(t-1)*mp.log(1-mp.mpf(c)/n)))
def log_A(n, beta, c):
    a = (1-beta)/2
    delta = c*a*a + 2*a*log(a) + (1-2*a)*log(1-2*a) if a < 0.5 else c*a*a + 2*a*log(a)
    return -delta*n + 3*log(n) + c*a
worstA = -1e9; wA=None; cnt=0
for c in (1, 2, 2.77, 3, 4, 5, 6, 8, 10, 12, 16, 20, 50, 100):
    for n in list(range(max(3, ceil(c)+1), 60)) + [60, 80, 100, 120, 200, 500, 1000, 2000]:
        for beta in np.linspace(0.0005, 0.9995, 300):
            k = floor(beta*n)
            if k >= n: continue
            d = log_exact(n, k, c) - log_A(n, beta, c)
            cnt += 1
            if d > worstA: worstA, wA = d, (c, n, beta, k)
print(f"(A) max over {cnt} (c,n,beta) of [ln exact(0) - ln A]: {worstA:.3e} at {wA}  (must be <= 0)")
# how loose is (A)? typical slack
slack = []
for c in (6, 10):
    for n in (60, 120, 1000):
        for beta in (0.1, 0.2, 0.3):
            slack.append((c, n, beta, round(log_A(n,beta,c) - log_exact(n, floor(beta*n), c), 2)))
print("(A) slack ln A - ln exact:", slack)

# concavity of g and uniqueness of root
def g(a, c): return -2*a*log(a) - (1-2*a)*log(1-2*a) - c*a*a if a < 0.5 else -2*a*log(a) - c*a*a
for c in (2, 2.7726, 2.8, 3, 10, 100):
    aa = np.linspace(1e-6, 0.5-1e-9, 100001); vals = np.array([g(a,c) for a in aa])
    sign_changes = np.sum(np.diff(np.sign(vals)) != 0)
    second = np.diff(vals, 2)
    print(f"  g at c={c}: sign changes on (0,1/2) = {sign_changes}, max 2nd difference = {second.max():.2e} (<0 concave), g(1/2)={g(0.5-1e-12,c):.5f}, ln2-c/4={log(2)-c/4:.5f}")

# asymptotic sandwich for a*(c)
print("asymptotic sandwich (2lnc-2lnlnc-2ln2)/c < a* < (2lnc-2lnlnc+2ln2+2)/c, c>=14:")
bad=[]
for c in [14, 15, 16, 20, 30, 50, 100, 300, 1e3, 1e4, 1e5, 1e6, 1e8]:
    a = (1-beta_star(c))/2
    lo = (2*log(c)-2*log(log(c))-2*log(2))/c; hi = (2*log(c)-2*log(log(c))+2*log(2)+2)/c
    K = a*c/2 - log(c) + log(log(c))   # a = (2/c)(ln c - ln ln c + K)
    ok = lo < a < hi
    if not ok: bad.append(c)
    print(f"  c={c:10.0f} lo={lo:.4e} a*={a:.4e} hi={hi:.4e} ok={ok}  K={K:.4f} (-> 1-ln2={1-log(2):.4f}?)")
print("  sandwich violations:", bad)
# below 14?
for c in [3,4,5,6,8,10,12,13]:
    a = (1-beta_star(c))/2
    lo = (2*log(c)-2*log(log(c))-2*log(2))/c; hi = (2*log(c)-2*log(log(c))+2*log(2)+2)/c
    print(f"  c={c} lo={lo:.4f} a*={a:.4f} hi={hi:.4f} ok={lo<a<hi}")

# Theorem B dense: exponent check
print("Theorem B: (2t-1) ln n - t(t-1) ln b <= -ln n - (eps/(2 ln b)) ln^2 n when n-k >= (4+eps) log_b n, n >= b^(4/eps)")
bad=[]
for p in (0.1, 0.3, 0.5, 0.9):
    b = 1/(1-p)
    for eps in (0.1, 0.5, 1, 2):
        nmin = b**(4/eps)
        for n in [int(nmin)+1, int(2*nmin)+5, int(10*nmin)+7, 10**6, 10**8]:
            if n < 3: continue
            smin = ceil((4+eps)*log(n)/log(b))
            for s in (smin, smin+1, 2*smin, n//2, n-1):   # s = n-k
                if s < 1 or s > n: continue
                t = (s+1)//2
                lhs = (2*t-1)*log(n) - t*(t-1)*log(b)
                rhs = -log(n) - (eps/(2*log(b)))*log(n)**2
                if lhs > rhs + 1e-9: bad.append((p, eps, n, s, lhs, rhs))
print("  Theorem B violations:", len(bad), bad[:5])
