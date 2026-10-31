"""CHECKER: Theorem A'' evaluations.  g(a) = -2a ln a - (1-2a) ln(1-2a) - c a^2.
Claims: for c >= 14, a- = (2/c) ln(c/(2 ln c)) has g(a-) > 0; a+ = (2/c)(ln(2c/ln c) + 1) has g(a+) < 0 and a+ <= 1/2
(fails at c = 13); and 4 ln x - 3x < 4 ln 2 + 4 for all x > 0; and 2 ln(1/a) - ca < g(a)/a <= 2 ln(1/a) + 2 - ca."""
from math import log
import numpy as np
def g(a, c): return -2*a*log(a) - (1-2*a)*log(1-2*a) - c*a*a if a < 0.5 else -2*a*log(a) - c*a*a
print("c, a-, g(a-) [>0?], a+, g(a+) [<0?], a+<=1/2?")
bad = []
for c in list(range(10, 200)) + [500, 1000, 10**4, 10**5, 10**6, 10**8]:
    am = (2/c)*log(c/(2*log(c))); ap = (2/c)*(log(2*c/log(c)) + 1)
    ok = (am > 0) and (g(am, c) > 0) and (ap <= 0.5) and (g(ap, c) < 0) and (am < ap)
    if c in (10, 12, 13, 14, 15, 16, 20, 50, 100, 1000, 10**6, 10**8) or not ok:
        print(f"  c={c:9d}  a-={am:.5f} g(a-)={g(am,c) if am < 0.5 else float('nan'):+.4e}  a+={ap:.5f} g(a+)={g(ap,c) if ap<0.5 else float('nan'):+.4e}  a+<=1/2: {ap<=0.5}  ok={ok}")
    if c >= 14 and not ok: bad.append(c)
print("  violations for c >= 14:", bad)
# the two auxiliary inequalities
xs = np.linspace(1e-9, 50, 2000001)
print("  max of 4 ln x - 3x - (4 ln 2 + 4):", (4*np.log(xs) - 3*xs - (4*log(2)+4)).max(), "(must be < 0; sup at x=4/3 is", 4*log(4/3) - 4 - 4*log(2) - 4, ")")
worst_lo = -1e9; worst_hi = -1e9
for c in (3, 10, 100, 1000):
    for a in np.linspace(1e-6, 0.5-1e-6, 200001):
        r = g(a, c)/a
        worst_lo = max(worst_lo, (2*log(1/a) - c*a) - r)      # need lo < r  => lo - r < 0
        worst_hi = max(worst_hi, r - (2*log(1/a) + 2 - c*a))  # need r <= hi
print(f"  sandwich 2ln(1/a) - ca < g/a <= 2ln(1/a) + 2 - ca: max(lo - g/a) = {worst_lo:.3e} (<0), max(g/a - hi) = {worst_hi:.3e} (<=0)")
