"""CHECKER: independent computation of beta*(c) (own code; the ANALYST's is beta_star.py).

beta*(c) = sup{ beta : H(a,a,1-2a) < c a^2 for all beta' in [0, beta) }, a = (1-beta')/2.
With a in (0, 1/2]: g(a) = c a^2 - H(a,a,1-2a) must be > 0 on (a_beta, 1/2].
At a = 1/2, g = c/4 - ln 2 > 0 iff c > 4 ln 2.  Method: fine downward scan from a = 1/2
for the first non-positive g (no concavity assumed), then brentq on that bracket.
"""
from math import log
import numpy as np
from scipy.optimize import brentq

def H(a):
    b = 1 - 2*a
    s = 0.0
    for x in (a, a, b):
        if x > 0:
            s -= x*log(x)
    return s

def g(a, c):
    return c*a*a - H(a)

def beta_star(c):
    if c <= 4*log(2):
        return 0.0
    grid = np.linspace(0.5, 1e-9, 200001)
    vals = np.array([g(a, c) for a in grid])
    idx = int(np.argmax(vals <= 0))
    if vals[idx] > 0:
        return 1.0
    a_root = brentq(lambda a: g(a, c), grid[idx], grid[idx-1], xtol=1e-14)
    return 1 - 2*a_root

if __name__ == "__main__":
    cs = [3, 4, 5, 6, 8, 10, 12, 16, 20, 50, 100]
    survey = {3:0.009,4:0.061,5:0.118,6:0.171,8:0.263,10:0.337,12:0.397,16:0.488,20:0.554,50:0.761,100:0.857}
    print("threshold 4 ln 2 =", 4*log(2))
    print(f"{'c':>6} {'beta*':>10} {'survey':>8} {'a*':>10} {'(1-b*)c/(4 ln c)':>18}")
    for c in cs:
        b = beta_star(c)
        print(f"{c:6} {b:10.6f} {survey.get(c,float('nan')):8.3f} {(1-b)/2:10.6f} {(1-b)*c/(4*log(c)):18.4f}")
    print("\nasymptotic check 1 - beta* ~ 4 ln c / c, and K in 1-b* = (4/c)(ln c - ln ln c + K):")
    for c in [1e2, 1e3, 1e4, 1e6, 1e8]:
        b = beta_star(c); a = (1-b)/2
        print(f"c={c:10.0f}  1-b*={1-b:.6e}  4lnc/c={4*log(c)/c:.6e}  ratio={(1-b)*c/(4*log(c)):.5f}  K={a*c/2-log(c)+log(log(c)):.4f} (1-ln2={1-log(2):.4f})")
    print("\nnear threshold:")
    for c in [2.7, 2.77, 2.7726, 2.773, 2.78, 2.8, 2.9]:
        print(f"c={c}  beta*={beta_star(c):.6f}")
