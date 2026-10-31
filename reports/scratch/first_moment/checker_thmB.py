# CHECKER: Theorem B (dense) exponent check, hypothesis n-k >= (4+eps) log_b n and n >= b^(4/eps) enforced.
from math import log, ceil
bad=[]; tested=0
for p in (0.05, 0.1, 0.3, 0.5, 0.9):
    b = 1/(1-p)
    for eps in (0.1, 0.5, 1, 2, 4):
        nmin = b**(4/eps)
        for n in [int(nmin)+1, int(2*nmin)+5, int(10*nmin)+7, 10**4, 10**6, 10**9]:
            if n < 3 or n < nmin: continue
            smin = ceil((4+eps)*log(n)/log(b))
            for s in sorted(set([smin, smin+1, smin+5, 2*smin, max(smin, n//2), n-1, n])):
                if s < smin or s < 1 or s > n: continue
                t = (s+1)//2
                lhs = (2*t-1)*log(n) - t*(t-1)*log(b)
                rhs = -log(n) - (eps/(2*log(b)))*log(n)**2
                tested += 1
                if lhs > rhs + 1e-9: bad.append((p, eps, n, s, lhs, rhs))
print("Theorem B: tested", tested, "violations:", len(bad), bad[:5])
# tightness: at s = smin exactly, slack
for p in (0.1, 0.5):
    b = 1/(1-p); eps = 0.5; n = 10**6; s = ceil((4+eps)*log(n)/log(b)); t=(s+1)//2
    print(f"  p={p} eps={eps} n=1e6 s={s} t={t}: lhs={(2*t-1)*log(n) - t*(t-1)*log(b):.1f} rhs={-log(n) - (eps/(2*log(b)))*log(n)**2:.1f}")
