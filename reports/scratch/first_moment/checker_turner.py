"""CHECKER: what Turner 1986 Lemma 2.2 gives at p = c/n (he does not state it):
P(bw <= n - 2k) <= [(en/k)(1-p)^{k/2}]^{2k}; with k = eps n, (1-c/n)^{eps n/2} <= e^{-c eps/2}:
-> 0 iff (e/eps) e^{-c eps/2} < 1 iff c eps > 2 + 2 ln(1/eps).  Bandwidth bound: bw >= (1-2 eps) n."""
from math import log, e
from scipy.optimize import brentq
import sys
sys.path.insert(0, '/home/al/dev/MOSP/reports/scratch/first_moment')
from checker_beta_star import beta_star
print("c | Turner-implied bw/n >= 1-2eps (crude count) | beta*(pw, entropy) | PS tw")
for c in (3,4,5,6,8,10,12,16,20,50,100):
    f = lambda x: c*x - 2 - 2*log(1/x)
    # need eps < 1/2 with f(eps) > 0; f increasing in x; root:
    if f(0.5) <= 0:
        s = 'vacuous'
    else:
        r = brentq(f, 1e-9, 0.5); s = f"{1-2*r:.3f} (eps={r:.3f})"
    print(f"{c:4} | {s:>22} | {beta_star(c):.3f} | {1-(9*log(3)/(2*c))**0.5 if c>9*log(3)/2 else float('nan'):.3f}")
print("threshold where Turner's crude count first gives anything: c eps > 2+2ln(1/eps) at eps=1/2 -> c > 4 + 4 ln 2 =", 4+4*log(2))
