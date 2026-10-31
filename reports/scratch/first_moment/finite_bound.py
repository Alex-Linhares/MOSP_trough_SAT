"""finite_bound.py -- the proved finite bound against the pilot data.

B(n, k, p) = C(n,t) C(n-t,t-1) (1-p)^(t(t-1)),  t = (n-k+1)//2,  the right-hand side of
`weightedSum_graphsOfPathwidthLe_le`; and the relaxed form (A) of the document,
exp(-delta(beta,c) n + 3 ln n + c a) with beta = k/n.  For each (n, c): the largest k with
B < 1, with B < 0.01, and the pilot's observed minimum pathwidth from
reports/scratch/gnp_pilot/results.csv (status bound/minor/refutation = exact; 'upper' = lower bound only).
Usage: nice -n 19 python3 -I finite_bound.py
"""
import csv, math, os
from collections import defaultdict
from scipy.optimize import brentq

def log_binom(n, k):
    if k < 0 or k > n:
        return -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

def logB(n, k, p):
    t = (n - k + 1) // 2
    return log_binom(n, t) + log_binom(n - t, t - 1) + t * (t - 1) * math.log1p(-p)

def phi(x):
    return 0.0 if x <= 0 else -x * math.log(x)

def logA(n, k, c):
    beta = k / n
    a = (1 - beta) / 2
    delta = c * a * a - 2 * phi(a) - phi(1 - 2 * a)
    return -delta * n + 3 * math.log(n) + c * a

def beta_star(c):
    gg = lambda a: 2 * phi(a) + phi(1 - 2 * a) - c * a * a
    return 1 - 2 * brentq(gg, 1e-12, 0.5, xtol=1e-14)

here = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(here, '..', 'gnp_pilot', 'results.csv'))))
print("pilot statuses:", sorted({r['status'] for r in rows}))
cells = defaultdict(list)
for r in rows:
    cells[(int(r['n']), float(r['c']))].append(r)

def pilot_min(n, c):
    rs = cells.get((n, float(c)), [])
    exact = [int(r['width']) for r in rs if r['status'] != 'upper']   # bound / minor / refutation = proved exactly
    lows = [int(r['lower']) for r in rs if r['status'] == 'upper']    # unproved: lower bound only
    return len(rs), len(exact), (min(exact) if exact else None), (min(lows) if lows else None)

print()
print(f"{'n':>4} {'c':>4} {'k:B<1':>6} {'k:B<.01':>8} {'k:A<1':>6} {'beta*n':>7} {'pilot N':>8} {'exact':>6} {'min pw(exact)':>14} {'min LB(unproved)':>17}")
for n in (60, 120):
    for c in (3, 4, 6, 8, 10):
        p = c / n
        kB1 = max(k for k in range(0, n) if logB(n, k, p) < 0)
        kB01 = max([k for k in range(0, n) if logB(n, k, p) < math.log(0.01)] or [-1])
        kA1 = max([k for k in range(0, n) if logA(n, k, c) < 0] or [-1])
        N, ne, mn, ml = pilot_min(n, c)
        print(f"{n:>4} {c:>4} {kB1:>6} {kB01:>8} {kA1:>6} {beta_star(c)*n:>7.2f} {N:>8} {ne:>6} {str(mn):>14} {str(ml):>17}")

print("\nn = 60, c = 10: the bound B(k) for k = 0..30, and the relaxed bound (A):")
n, c = 60, 10
for k in range(0, 31):
    lb = logB(n, k, c / n)
    la = logA(n, k, c)
    print(f"  k={k:>2}  t={(n-k+1)//2:>2}  log10 B = {lb/math.log(10):>9.3f}   B = {math.exp(lb):.3e}    log10 A = {la/math.log(10):>8.3f}")

print("\nn = 120, c = 10: the bound B(k) for k = 30..50:")
n = 120
for k in range(30, 51):
    lb = logB(n, k, c / n)
    print(f"  k={k:>2}  t={(n-k+1)//2:>2}  log10 B = {lb/math.log(10):>9.3f}")

print("\nn = 60 and 120: the distribution of the pilot's exact pathwidths at c = 10 (value: count), and lower bounds of the unproved:")
for n in (60, 120):
    rs = cells[(n, 10.0)]
    ex = defaultdict(int); lo = defaultdict(int)
    for r in rs:
        (ex if r['status'] != 'upper' else lo)[int(r['width'] if r['status'] != 'upper' else r['lower'])] += 1
    print(f"  n={n}: exact {dict(sorted(ex.items()))}; unproved lower bounds {dict(sorted(lo.items()))}")

print("\nFrom which n on is B(n, floor(beta n), c/n) < 1 for all larger n (checked to 3000), c = 10?")
c = 10
bs = beta_star(c)
for beta in (bs / 2, 0.25, 0.30, 0.33):
    first = next((n for n in range(12, 3000) if all(logB(m, int(beta * m), c / m) < 0 for m in range(n, n + 60))), None)
    print(f"  beta = {beta:.4f}: from n = {first}")
print("And the relaxed bound (A) < 1, c = 10?")
for beta in (bs / 2, 0.25, 0.30):
    first = next((n for n in range(12, 20000) if all(logA(m, int(beta * m), c) < 0 for m in range(n, n + 60))), None)
    print(f"  beta = {beta:.4f}: from n = {first}")
