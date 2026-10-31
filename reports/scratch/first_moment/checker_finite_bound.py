"""CHECKER (own code; the ANALYST's is finite_bound.py): exact evaluation of
   B(n,k,p) = C(n,t) C(n-t,t-1) (1-p)^(t(t-1)),  t = ceil((n-k)/2)
with Python Fractions (exact) for the spot values, and mpmath logs for the sweep."""
from fractions import Fraction
from math import comb, log
import mpmath as mp
mp.mp.dps = 30
import sys
sys.path.insert(0, '/home/al/dev/MOSP/reports/scratch/first_moment')
from checker_beta_star import beta_star

def B_exact(n, k, p):
    t = (n - k + 1)//2
    return Fraction(comb(n, t) * comb(n - t, t - 1)) * (1 - p)**(t*(t-1))

print("spot values (exact rationals, printed to 6 sig figs):")
for n, k, p in ((60, 23, Fraction(1,6)), (60, 21, Fraction(1,6)), (60, 24, Fraction(1,6)), (120, 43, Fraction(1,12)), (120, 41, Fraction(1,12)), (120, 44, Fraction(1,12)),
                (60, 11, Fraction(1,10)), (60, 9, Fraction(1,10)), (120, 21, Fraction(1,20))):
    v = B_exact(n, k, p)
    print(f"  B({n},{k},{p}) = {float(v):.6g}   t={(n-k+1)//2}")

def log_bound(n, k, c):
    t = (n - k + 1)//2
    return mp.log(mp.binomial(n, t)) + mp.log(mp.binomial(n - t, t - 1)) + t*(t-1)*mp.log(1 - mp.mpf(c)/n)

pilot_min = {3:0.083, 4:0.133, 6:0.267, 8:0.333, 10:0.417}
print(f"\n{'n':>6} {'c':>3} {'k<1':>6} {'k/n':>7} {'k<1e-3':>7} {'k/n':>7} {'beta*':>7} {'pilot min pw/n (n=60)':>22}")
for c in (3, 4, 6, 8, 10):
    bs = beta_star(c)
    for n in (60, 120, 1000, 10000):
        k1 = k3 = None
        for k in range(0, n):
            lb = log_bound(n, k, c)
            if lb < 0: k1 = k
            if lb < -3*mp.log(10): k3 = k
        print(f"{n:6} {c:3} {str(k1):>6} {(k1/n if k1 is not None else float('nan')):7.3f} {str(k3):>7} {(k3/n if k3 is not None else float('nan')):7.3f} {bs:7.3f} {pilot_min.get(c, float('nan')):22.3f}")
