"""Preview for items 05-06, from the quoted rate function only (rate_check.py):
the *relaxed* separator first moment

    P(pw(G(n, c/n)) <= k) <= C(n, k) * P_N(largest component of G(N, c'/N) <= N/2),
    N = n - k, c' = c (1 - beta), k = beta n,

with the inner probability replaced by its LDP rate I^beta_{c'}(1/2) (O'Connell 1998 as
restated by Puhalskii 2005): exponent per vertex of n

    g_relax(beta) = H(beta) - (1 - beta) * I^beta_{c(1-beta)}(1/2),   H = binary entropy in nats,

against the pair count's  g_pair(beta) = H(a, a, 1-2a) - c a^2, a = (1-beta)/2.  Roots and the
gain in nats per vertex at beta*.  A preview: asymptotic, from a quotation, relaxed event; item 06
computes the real thing and this file is superseded by it.
"""
import math, sys
sys.path.insert(0, 'reports/scratch/separator_moment')
from rate_check import I, giant

def H2(b): return -b*math.log(b) - (1-b)*math.log(1-b)
def H3(a): return -2*a*math.log(a) - (1-2*a)*math.log(1-2*a)
def g_pair(c, b): a = (1-b)/2; return H3(a) - c*a*a
def g_relax(c, b): return H2(b) - (1-b)*I(c*(1-b), 0.5)

def root(f, lo=1e-4, hi=0.95):
    # first beta (scanning up) where f crosses from negative to positive
    prev = f(lo)
    if prev >= 0: return 0.0
    b = lo
    while b < hi:
        nb = b + 0.0005
        v = f(nb)
        if v >= 0:
            for _ in range(60):
                mid = (b+nb)/2
                if f(mid) >= 0: nb = mid
                else: b = mid
            return (b+nb)/2
        b = nb
    return float('nan')

print("c   beta*_pair  beta_relax  gain(beta)  g_pair(beta*)  g_relax(beta*)  slope_pair  threshold c(1-b)=2ln2?")
for c in [2.0, 2.5, 2.772, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0]:
    bp = root(lambda b: g_pair(c, b)); br = root(lambda b: g_relax(c, b))
    bb = bp if bp > 0 else 0.001
    sl = (g_pair(c, bb+1e-4) - g_pair(c, bb-1e-4))/2e-4
    print(f"{c:5.2f}  {bp:.4f}     {br:.4f}     {br-bp:+.4f}    {g_pair(c,bb):+.4f}       {g_relax(c,bb):+.4f}      {sl:.2f}")
print("threshold of the relaxed separator count: the largest c with beta_relax = 0 is where c = 2 ln 2 =", round(2*math.log(2),4))
