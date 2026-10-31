"""lean_target_check.py -- the exact statement to be proved in Lean (FirstMomentAsymptotics.lean), checked
numerically before any Lean is written (CLAUDE.md rule), 2026-10-31.

The Lean target (Theorem A of reports/random_graph_first_moment.md, finite form), for c > 0, 0 < beta < 1,
n >= 3, c <= n, a = (1 - beta)/2, k = floor(beta n), t = (n - k + 1) div 2, p = c/n:

    RHS0  := C(n,t) * C(n-t,t-1) * (1-p)^(t(t-1))                 (the proved input, 0^0 = 1)
    target := exp(-delta n + 3 ln n + c a),  delta = c a^2 - (2 phi(a) + phi(1 - 2a)),  phi(x) = -x ln x

and the claim is  RHS0 <= target.  Also checked, at every grid point, the lemmas in the exact form the
Lean proof uses:

  (I1)  C(n,t) C(n-t,t-1) <= exp(n (phi(u) + phi(v) + phi(w))),   u = t/n, v = (t-1)/n, w = (n-t-(t-1))/n
  (I2)  (1-p)^m <= exp(-p m) at m = t(t-1)
  (I3)  phi(y) <= phi(x) + phi(d) for |y - x| <= d <= 1/e, 0 <= x, y <= 1, at the three coordinates with
        d = 1/n, and phi(1/n) = ln n / n
  (I4)  1 <= t,  2t <= n + 1,  a n <= t < a n + 1,  t(t-1) >= a^2 n^2 - a n
  (cor) target <= exp(c/2) n^3 exp(-delta n)

Grid: n = 3..300, c in {0.5, 1, 2, 4, 6, 10, 20, 50} with c <= n (so n = c included, p = 1), beta on
400 points of (0, 1) plus j/n for j = 1..n-1 (where floor(beta n) sits on an integer) plus 1 - 1e-9 and
1e-9.  Floats with lgamma for the sweep (relative error ~1e-12, against slacks of order 1); the 30
tightest points re-evaluated in mpmath at 50 digits.
Usage: nice -n 19 python3 -I lean_target_check.py
"""
import math
from fractions import Fraction
import numpy as np
import mpmath as mp

E_INV = math.exp(-1.0)

def phi(x):
    return 0.0 if x <= 0 else -x * math.log(x)

def log_binom(n, k):
    if k < 0 or k > n:
        return -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

def log_rhs0(n, t, p):
    m = t * (t - 1)
    lb = log_binom(n, t) + log_binom(n - t, t - 1)
    if p >= 1.0:
        return lb if m == 0 else -math.inf
    return lb + m * math.log1p(-p)

viol = []
checks = 0
tight = []  # (slack, n, c, beta)
betas_common = np.linspace(0.001, 0.999, 400)
for n in range(3, 301):
    extra = [j / n for j in range(1, n)] + [1 - 1e-9, 1e-9]
    betas = sorted(set(list(betas_common) + extra))
    for c in (0.5, 1, 2, 4, 6, 10, 20, 50):
        if c > n:
            continue
        p = c / n
        for beta in betas:
            k = math.floor(Fraction(beta) * n)        # exact floor of the real beta * n
            t = (n - k + 1) // 2
            a = (1 - beta) / 2
            delta = c * a * a - (2 * phi(a) + phi(1 - 2 * a))
            target = -delta * n + 3 * math.log(n) + c * a
            # I4
            if not (1 <= t and 2 * t <= n + 1):
                viol.append(("I4 nat", n, c, beta, k, t))
            if not (a * n <= t + 1e-12 and t < a * n + 1 + 1e-12):
                viol.append(("I4 real", n, c, beta, t, a * n))
            if not (t * (t - 1) >= a * a * n * n - a * n - 1e-9):
                viol.append(("I4 product", n, c, beta))
            # I1
            u, v, w = t / n, (t - 1) / n, (n - t - (t - 1)) / n
            lb = log_binom(n, t) + log_binom(n - t, t - 1)
            H = n * (phi(u) + phi(v) + phi(w))
            if lb > H + 1e-9:
                viol.append(("I1", n, c, beta, lb, H))
            # I3 at the three coordinates, d = 1/n
            d = 1 / n
            if d > E_INV:
                viol.append(("I3 d>1/e", n))
            for y, x in ((u, a), (v, a), (w, 1 - 2 * a)):
                if not (0 <= x <= 1 and 0 <= y <= 1 and abs(y - x) <= d + 1e-12):
                    viol.append(("I3 hyp", n, c, beta, x, y))
                if phi(y) > phi(x) + phi(d) + 1e-12:
                    viol.append(("I3", n, c, beta, x, y))
            if abs(phi(d) - math.log(n) / n) > 1e-12:
                viol.append(("phi(1/n)", n))
            # I2
            m = t * (t - 1)
            lhs2 = (1 - p) ** m
            if lhs2 > math.exp(-p * m) + 1e-12:
                viol.append(("I2", n, c, beta))
            # the assembled target
            lr = log_rhs0(n, t, p)
            checks += 1
            if lr > target + 1e-9:
                viol.append(("TARGET", n, c, beta, k, t, lr, target))
            tight.append((target - lr, n, c, beta))
            # corollary
            cor = c / 2 + 3 * math.log(n) - delta * n
            if target > cor + 1e-12:
                viol.append(("COR", n, c, beta))

tight.sort()
print(f"grid points (n, c, beta): {checks}")
print(f"violations: {len(viol)}")
for v in viol[:20]:
    print("  ", v)
print("tightest 10 (slack in nats = ln target - ln RHS0; n, c, beta):")
for s, n, c, beta in tight[:10]:
    print(f"   slack={s:.6f}  n={n} c={c} beta={beta:.6f}")

# mpmath confirmation of the 30 tightest
mp.mp.dps = 50
bad = 0
for s, n, c, beta in tight[:30]:
    k = math.floor(Fraction(beta) * n)
    t = (n - k + 1) // 2
    a = (1 - mp.mpf(beta)) / 2
    ph = lambda x: mp.mpf(0) if x <= 0 else -x * mp.log(x)
    delta = c * a * a - (2 * ph(a) + ph(1 - 2 * a))
    target = -delta * n + 3 * mp.log(n) + c * a
    p = mp.mpf(c) / n
    m = t * (t - 1)
    rhs0 = mp.binomial(n, t) * mp.binomial(n - t, t - 1) * (1 - p) ** m
    if rhs0 > mp.exp(target):
        bad += 1
        print("  mpmath violation", n, c, beta)
print(f"mpmath re-check of the 30 tightest: {bad} violations")
print("RESULT:", "OK, zero violations" if not viol and not bad else "VIOLATIONS FOUND")
