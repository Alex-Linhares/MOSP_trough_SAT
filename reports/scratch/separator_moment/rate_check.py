"""Check, before it is quoted, the rate function for the size of the largest
component of G(n, c/n) in the form O'Connell (1998) gives it, as restated by
Puhalskii (2005, Ann. Probab. 33, remark after Corollary 2.5; his (2.13)-(2.14)):

    K_rho(u) = u log(rho u / (1 - e^{-rho u})) - rho u^2 / 2,
    L_c(u)   = (1 - u) log(1 - u) + (c - log c) u - c u^2 / 2,
    I_c^beta(u) = k K_c(u) + L_c(k u)   for u in [x_k, x_{k-1}],  x_0 = 1,
    x_k the solution of x / (1 - e^{-c x}) = 1 - k x.

Two things are checked numerically (item 01 of loop0011, 2026-11-01):
(1) I vanishes at the law-of-large-numbers point u* = 1 - rho, 1 - u* = e^{-c u*};
(2) inf over u <= 1/2 of I is positive iff c > 2 ln 2, i.e. iff u* > 1/2.
Nothing here is a theorem of ours; it is a sanity check of a quotation.
"""
import math

def K(rho, u):
    if u == 0: return 0.0
    return u * math.log(rho * u / (1 - math.exp(-rho * u))) - rho * u * u / 2

def L(c, u):
    return (1 - u) * math.log(1 - u) + (c - math.log(c)) * u - c * u * u / 2 if u < 1 else (c - math.log(c)) - c / 2

def x_k(c, k):
    # solve x/(1-e^{-cx}) = 1 - k x on (0, 1/k) by bisection; LHS - RHS increasing
    lo, hi = 1e-12, 1.0 / k - 1e-12
    f = lambda x: x / (1 - math.exp(-c * x)) - (1 - k * x)
    if f(lo) > 0: return 0.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2

def I(c, u):
    if u <= 0: return L(c, max(0.0, 1 - 1 / c))
    k = 1
    while True:
        xk, xk1 = x_k(c, k), (1.0 if k == 1 else x_k(c, k - 1))
        if xk <= u <= xk1 + 1e-15:
            return k * K(c, u) + L(c, k * u)
        k += 1
        if k > 10000: return float('nan')

def giant(c):
    if c <= 1: return 0.0
    lo, hi = 1e-12, 1 - 1e-12
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - mid - math.exp(-c * mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2

if __name__ == "__main__":
  print("c  u*=giant  I(u*)  x_1  I(1/2)  min_{u<=1/2} I  c>2ln2")
  for c in [1.2, 1.386, 1.4, 1.5, 2.0, 2.772, 3.0, 4.0, 4.98, 6.0, 8.0, 10.0]:
      us = giant(c)
      grid = [i / 2000 for i in range(1, 1001)]
      m = min(I(c, u) for u in grid)
      print(f"{c:5.3f} {us:.4f} {I(c, us):+.2e} {x_k(c,1):.4f} {I(c,0.5):+.5f} {m:+.5f} {c > 2*math.log(2)}")
