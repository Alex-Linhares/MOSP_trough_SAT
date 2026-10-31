"""Asymptotic first-moment constant for random clique covers (the Chu & Stuckey model).

Model: n customers, m = mu*n patterns, each pattern an independent uniform random customer set of
size s (fixed d, or the class's empirical size distribution).  For a pair (A, R) of sizes a n each,
P(no pattern meets both) = prod_j [2(1-a)^{s_j} - (1-2a)^{s_j}] (+ o(1) in the exponent), so
  (1/n) log E[#empty pairs] -> g(a) = H(a, a, 1-2a) + mu * E_s log(2(1-a)^s - (1-2a)^s),
and pw >= (1-2a*) n whp where a* is the point above which g < 0 (g(0+) = 0, g(1/2) < 0 for s >= 2).
beta*(d, mu) = 1 - 2a*.  Also the threshold in d (for mu = 1) below which beta* = 0.
    python3 asymptotic_cs.py
"""
import glob, json, math, collections, statistics as st
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
def phi(x): return -x*math.log(x) if x > 0 else 0.0
def rate(a, mu, sizes):
    return 2*phi(a) + phi(1-2*a) + mu*st.mean(math.log(max(2*(1-a)**s - (1-2*a)**s, 1e-300)) for s in sizes)
def beta_star(mu, sizes, step=1e-4):
    a = 0.5 - step
    if rate(a, mu, sizes) >= 0: return 0.0
    while a - step > 0 and rate(a - step, mu, sizes) < 0: a -= step
    return 1 - 2*a
def main():
    classes = collections.defaultdict(lambda: {"sizes": [], "opt": [], "n": None, "m": None})
    for f in sorted(glob.glob(str(ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-*.txt"))):
        L = [l for l in open(f).read().split("\n") if l.strip()]; m, n = map(int, L[0].split())
        sizes = [sum(map(int, L[1 + i].split())) for i in range(m)]
        name = Path(f).stem; d = int(name.split("-")[3]); c = classes[(n, m, d)]
        c["sizes"] += sizes; c["opt"].append(json.load(open(ROOT / "solutions" / f"{name}_0.json"))["mosp_value"]); c["n"] = n; c["m"] = m
    print("class (n,m,d): opt/n | beta* (empirical sizes) | beta* (fixed d)")
    for k in sorted(classes):
        c = classes[k]; mu = c["m"] / c["n"]
        print(f"{k}: {st.mean(c['opt'])/c['n']:.3f} | {beta_star(mu, c['sizes']):.3f} | {beta_star(mu, [k[2]]):.3f}")
    print("\nfixed size d, mu = m/n: beta*(d, mu)")
    print("d\\mu " + " ".join(f"{mu:>6}" for mu in (0.5, 1, 2, 4)))
    for d in (2, 3, 4, 5, 6, 8, 10, 15, 20):
        print(f"{d:<5}" + " ".join(f"{beta_star(mu, [d]):6.3f}" for mu in (0.5, 1, 2, 4)))
    # threshold in (real) d at mu = 1: smallest d with beta* > 0, by bisection on d with the formula extended to real s
    lo, hi = 2.0, 4.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if beta_star(1.0, [mid]) > 0: hi = mid
        else: lo = mid
    print(f"\nthreshold at mu = 1: beta* > 0 iff d > {hi:.4f} (fixed size d); the G(n, c/n) threshold is c > 4 ln 2 = {4*math.log(2):.4f}")
if __name__ == "__main__":
    main()
