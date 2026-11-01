"""loop0011 item 03, the checks behind §3 (`checks.log`): the SLSQP maximiser of
`second_moment_rate_gnp` against a 61⁴ grid; the ratio exponent at `β*`; the
parity split of `X₁/X₂` (when `N` is even every separator carries a pair and
its reverse); `X₃ = X₃′` shares; the direct closed-pair enumeration at `n ≤ 16`;
the pilot's `n = 20` cells against the fresh ones.

    nice -n 19 python3 reports/scratch/separator_moment/03_clumping/checks.py > reports/scratch/separator_moment/03_clumping/checks.log
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from learning.separator_moment import _entropy, second_moment_rate_gnp  # noqa: E402

HERE = Path(__file__).resolve().parent

print("== grid check of the SLSQP maximiser (4 free cells on a 61^4 grid) ==")


def expo(v, a, c):
    aa, ar, ra, rr = v
    T = np.array([aa, ar, a - aa - ar, ra, rr, a - ra - rr, a - aa - ra, a - ar - rr,
                  1 - 2 * a - (a - aa - ra) - (a - ar - rr)])
    if np.any(T < -1e-12):
        return -np.inf
    return _entropy(np.clip(T, 0, None)) - c * (2 * a * a - T[0] * T[4] - T[1] * T[3])


for a, c in [(0.2188, 10), (0.3452, 4), (0.2755, 6), ((1 - 0.3371) / 2, 10), ((1 - 0.1706) / 2, 6)]:
    g = np.linspace(0, a, 61)
    best = (-np.inf, None)
    for v in itertools.product(g, g, g, g):
        e = expo(v, a, c)
        if e > best[0]:
            best = (e, v)
    sup, twog, T = second_moment_rate_gnp(a, c)
    print(f"a={a:.4f} c={c}: grid max {best[0]:.5f} at {np.round(best[1], 4)}; SLSQP {sup:.5f} "
          f"table AA,AR,RA,RR = {np.round(T[[0, 1, 3, 4]], 4)}; ratio exp {sup - twog:.4f}")

print("\n== ratio exponent at beta* on G(n, c/n) ==")
for c, bs in [(4, 0.061), (6, 0.1706), (8, 0.263), (10, 0.3371)]:
    a = (1 - bs) / 2
    sup, twog, T = second_moment_rate_gnp(a, c)
    print(f"c={c} beta*={bs} a={a:.4f}: g={twog / 2:.5f} sup={sup:.4f} ratio exponent={sup - twog:.4f} table={np.round(T, 3)}")

print("\n== parity of N and X1/X2 at k = pw ==")
df = pd.read_csv(HERE / "counts.csv")
d = df[(df.k == df.pw)].copy()
d["Neven"] = (d.N % 2 == 0)
d["r2"] = d.X1 / d.X2
d["r3"] = d.X1 / d.X3
d["r4"] = d.X1 / d.X4
gm = lambda x: np.exp(np.log(x).mean())  # noqa: E731
g = d.groupby(["source", "c", "Neven"]).agg(n_inst=("X1", "size"), r2_gm=("r2", gm), r3_gm=("r3", gm),
                                           r4_gm=("r4", gm), X1_gm=("X1", gm))
print(g.round(3).to_string())
print("\n== X3 == X3p at k = pw? share equal, by source ==")
print(d.groupby("source")[["X3", "X3p", "X2", "X1", "X4"]].apply(
    lambda g: pd.Series({"X3_eq_X3p": (g.X3 == g.X3p).mean(), "X2_eq_X1": (g.X2 == g.X1).mean(),
                         "X4_eq_X1": (g.X4 == g.X1).mean()})).round(4).to_string())
d2 = df[(df.k == df.pw + 2)]
print("at pw+2:", d2.groupby("source")[["X3", "X3p"]].apply(
    lambda g: pd.Series({"X3_eq_X3p": (g.X3 == g.X3p).mean()})).round(4).to_string())
print("\n== X3_check (direct enumeration, n<=16, k=pw) agreed on:", (df.X3_check.notna()).sum(),
      "rows; mismatches:", ((df.X3_check.notna()) & (df.X3_check != df.X3)).sum())
print("\n== pilot vs fresh at n = 20 (k = pw): pw mean, X1 gm, ratios ==")
for c in [4, 6, 8, 10]:
    for src in ["fresh", "pilot"]:
        x = d[(d.n == 20) & (d.c == c) & (d.source == src)]
        print(src, c, len(x), round(x.pw.mean(), 3), round(gm(x.X1), 2), round(gm(x.r2), 3), round(gm(x.r3), 3), round(gm(x.r4), 3))
print("\n== seconds total ==", df.seconds.sum())
