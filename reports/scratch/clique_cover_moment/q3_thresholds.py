"""Q3: the first-moment threshold d0(mu) (fixed pattern size, quenched), the annealed Bernoulli threshold,
Gao's c > 2, the hardness ridge, and the giant-component threshold, as functions of mu = m / n."""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from asymptotic_cs import rate, beta_star
def d0_bisect(mu):
    lo, hi = 1.0, 40.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if beta_star(mu, [mid]) > 0: hi = mid
        else: lo = mid
    return hi
def d0_bern(mu):
    # annealed Bernoulli patterns of mean size d: rate at a = 1/2 is ln2 + mu ln(2 e^{-d/2} - e^{-d}); threshold solves 2x - x^2 = 2^{-1/mu}, x = e^{-d/2}
    x = 1 - math.sqrt(1 - 2 ** (-1 / mu))
    return -2 * math.log(x)
ridge_meas = {2: "2.01 (grid edge)", 1: "3.31-3.47", 0.5: "5.24-5.64", 0.25: "9.17-10.63", 0.125: "20.7 [18.7, 21.6]"}
print("mu=m/n | d0 bisection | 1+1/mu (exact, g(1/2)=0) | annealed Bernoulli d0 | Gao c>2 => d>2/mu | ridge 1+2.4/mu | ridge measured (fixed gen., ml_nature §25) | giant (fixed) (1+sqrt(1+4/mu))/2 | excess mu(d-1) at: d0, ridge")
for mu in (0.125, 0.25, 0.5, 1, 2, 4, 8):
    d0 = d0_bisect(mu)
    print(f"{mu:6} | {d0:7.4f} | {1+1/mu:7.4f} | {d0_bern(mu):7.4f} | {2/mu:7.4f} | {1+2.4/mu:7.3f} | {ridge_meas.get(mu,'-'):18s} | {(1+math.sqrt(1+4/mu))/2:6.3f} | {mu*(d0-1):.3f}, {mu*(2.4/mu):.3f}")
print("\nbeta*(d, mu) at the measured ridge (fixed generator, d = ridge col_mean), i.e. how far above the threshold the ridge sits:")
for mu, d in ((2, 2.01), (1, 3.4), (0.5, 5.4), (0.25, 9.9), (0.125, 20.7)):
    print(f"mu={mu:6} ridge d={d:5.2f}: beta* = {beta_star(mu, [d]):.3f}; at the threshold d0={d0_bisect(mu):.3f}; at excess 2: d={1+2/mu:.2f}, beta*={beta_star(mu,[1+2/mu]):.3f}")
# check derivative sign at the threshold: is g decreasing into a = 1/2 when d = 1 + 1/mu? g(1/2) = 0 exactly there.
for mu in (0.5, 1, 2):
    d = 1 + 1/mu
    print(f"mu={mu}: g(0.5)={rate(0.5-1e-9, mu, [d]):+.2e}, g(0.49)={rate(0.49, mu, [d]):+.4f}, g(0.45)={rate(0.45, mu, [d]):+.4f}  (positive just below 1/2 => beta*=0 exactly at d0)")
