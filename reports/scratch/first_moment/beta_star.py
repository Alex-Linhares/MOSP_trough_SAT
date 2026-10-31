"""beta_star.py -- the first-moment threshold beta*(c) for the pathwidth of G(n, c/n).

g(a) = -2a ln a - (1-2a) ln(1-2a) - c a^2  (= H(a,a,1-2a) - c a^2, natural logs).
beta*(c) = 1 - 2 a*(c), a*(c) the unique root of g in (0, 1/2) when c > 4 ln 2.
Also: numerical checks of the concavity of g, of the shift lemma (I3), and of the
bracketing (2 ln c - 2 ln ln c - 2 ln 2)/c < a* < (2 ln c - 2 ln ln c + 2 ln 2 + 2)/c.
Usage: nice -n 19 python3 -I beta_star.py
"""
import math
from scipy.optimize import brentq

def phi(x):
    return 0.0 if x <= 0 else -x * math.log(x)

def g(a, c):
    return phi(a) * 2 + phi(1 - 2 * a) - c * a * a

def a_star(c):
    # g > 0 near 0, g(1/2) = ln2 - c/4 < 0 for c > 4 ln 2; unique root (strict concavity)
    lo = 1e-12
    while g(lo, c) <= 0:  # never triggers; guard
        lo *= 10
    return brentq(lambda a: g(a, c), lo, 0.5, xtol=1e-14, rtol=1e-14, maxiter=500)

def beta_star(c):
    if c <= 4 * math.log(2):
        return 0.0
    return 1 - 2 * a_star(c)

survey = {3: 0.009, 4: 0.061, 5: 0.118, 6: 0.171, 8: 0.263, 10: 0.337, 12: 0.397,
          16: 0.488, 20: 0.554, 50: 0.761, 100: 0.857}

print("4 ln 2 =", 4 * math.log(2))
print(f"{'c':>6} {'a*':>10} {'beta*':>10} {'survey':>8} {'diff':>8} {'4lnc/c':>8} {'2nd-order':>10} {'delta(beta*/2)':>14}")
for c in [3, 4, 5, 6, 8, 10, 12, 16, 20, 50, 100]:
    a = a_star(c)
    b = 1 - 2 * a
    lead = 4 * math.log(c) / c
    second = (4 * math.log(c) - 4 * math.log(math.log(c)) + 4 - 4 * math.log(2)) / c
    # the rate at beta = beta*/2 (an example exponent)
    a_half = (1 - b / 2) / 2
    delta_half = -g(a_half, c)
    print(f"{c:>6} {a:>10.6f} {b:>10.4f} {survey[c]:>8.3f} {b - survey[c]:>+8.4f} {1-lead:>8.4f} {1-second:>10.4f} {delta_half:>14.5f}")

print("\nnear the threshold:")
for c in [2.78, 2.8, 2.9, 3.0]:
    print(f"  c={c}: beta* = {beta_star(c):.6f}")

print("\nbracketing of a* for c >= 14 (lower < a* < upper):")
ok = True
for c in list(range(14, 200)) + [500, 1000, 1e4, 1e5, 1e6]:
    a = a_star(c)
    lo = (2 * math.log(c) - 2 * math.log(math.log(c)) - 2 * math.log(2)) / c
    hi = (2 * math.log(c) - 2 * math.log(math.log(c)) + 2 * math.log(2) + 2) / c
    if not (lo < a < hi):
        ok = False
        print("  VIOLATION at c =", c, lo, a, hi)
    if c in (14, 20, 100, 1000, 1e6):
        print(f"  c={c:g}: lo={lo:.6f} a*={a:.6f} hi={hi:.6f}  c*a* - (2 ln c - 2 ln ln c) = {c*a - 2*math.log(c) + 2*math.log(math.log(c)):.4f}  (4 - 4 ln 2 = {4-4*math.log(2):.4f} predicted for the O(1) of 2a*, i.e. {2-2*math.log(2):.4f} for a*)")
print("  bracketing holds on all tested c" if ok else "  bracketing FAILS")

print("\nconcavity of g: g'' = -4/(1-2a) - 2/a - 2c < 0 trivially; numerical second differences at c=3:")
h = 1e-4
worst = max((g(a + h, 3) - 2 * g(a, 3) + g(a - h, 3)) / h**2 for a in [i / 1000 for i in range(1, 500)])
print("  max second difference on (0,1/2):", worst)

print("\nshift lemma (I3): |phi(x) - phi(y)| <= phi(d), d = |x-y| <= 1/e, on a grid")
viol = 0
N = 2000
for i in range(N + 1):
    x = i / N
    for j in range(i, N + 1):
        y = j / N
        d = y - x
        if 0 < d <= 1 / math.e and abs(phi(x) - phi(y)) > phi(d) + 1e-12:
            viol += 1
print("  violations:", viol, "of", (N + 1) * (N + 2) // 2, "pairs tested")
print("  the lemma fails for d > 1/e?  example d = 0.5: phi(0)-phi(0.5) =", phi(0.5), " vs phi(0.5) =", phi(0.5), " (equality); d=0.9: |phi(0.1)-phi(1.0)| =", phi(0.1), " vs phi(0.9) =", phi(0.9))
