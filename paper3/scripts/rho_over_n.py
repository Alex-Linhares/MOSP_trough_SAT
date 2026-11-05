#!/usr/bin/env python3
"""The paper's central figure: the verified exponent against brute force.

The verified bound is  C (L+1)^d 2^(A rho(n)),  rho(n) = n (ln ln(n+16))^2 / sqrt(ln(n+16))
(the comparator's `runtimeScale`); brute force is 2^n poly.  The ratio rho(n)/n is the
exponent relative to brute force at A = 1.  Also drawn: the manuscript's two sharper,
unverified exponents, n ln ln n / sqrt(ln n) (Theorem 1.1, general) and n / sqrt(ln n)
(fixed clause density), each divided by n.  n on a log-log-style axis via log10(n).

Regenerate:  python3 paper3/scripts/rho_over_n.py   ->  paper3/latex/figures/rho_over_n.pdf, .png,
             and paper3/latex/tables/rho_over_n.csv (the plotted points).
"""
import csv, math, pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent.parent
FIG = HERE / "latex" / "figures"; TAB = HERE / "latex" / "tables"
FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)

def rho_verified(n):            # comparator: runtimeScale n
    return n * math.log(math.log(n + 16)) ** 2 / math.sqrt(math.log(n + 16))
def rho_paper(n):               # Theorem 1.1, general k-CNF (not verified)
    return n * math.log(math.log(n)) / math.sqrt(math.log(n))
def rho_fixed_density(n):       # Theorem 1.1, m <= D n (not verified)
    return n / math.sqrt(math.log(n))

# log10(n) from 1 to 3000 (n = 10 .. 10^3000); the curves are smooth in log n
L = np.linspace(1.0, 3000.0, 4000)
ns = [10.0 ** l for l in L]
def safe(f, n):
    try:
        return f(n) / n
    except (ValueError, OverflowError):
        return float("nan")
# evaluate in log space to avoid overflow: use ln n directly
def ratios(l10):
    ln = l10 * math.log(10.0)
    # n + 16 ~ n for the plotted range except the first points; handle exactly for small n
    if l10 < 6:
        n = 10.0 ** l10
        return (rho_verified(n) / n, rho_paper(n) / n, rho_fixed_density(n) / n)
    return (math.log(ln) ** 2 / math.sqrt(ln), math.log(ln) / math.sqrt(ln), 1.0 / math.sqrt(ln))
V, P, D = zip(*[ratios(l) for l in L])

# landmarks
# peak analytically: (ln y)^2/sqrt(y) is maximal at ln y = 4, y = ln(n+16) = e^4, value 16/e^2
# (the grid's step of 0.75 in log10 n put it at 10^23.5 before item 02; the true abscissa is e^4/ln 10 = 23.71)
peak_l10, peak_v = math.e ** 4 / math.log(10.0), 16.0 / math.e ** 2
# crossing of the verified ratio back below 1 (large n): solve (ln ln n)^2 = sqrt(ln n)  ->  ln n ~ 5504 (e^5504)
cross_ln = 5504.0; cross_l10 = cross_ln / math.log(10.0)
# small-n crossing: rho(49)/49 = 0.9994, rho(50)/50 = 1.0027
small = [(n, rho_verified(n) / n) for n in (49, 50)]

with open(TAB / "rho_over_n.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["log10_n", "verified_ratio", "paper_general_ratio", "paper_fixed_density_ratio"])
    for l, v, p, d in zip(L, V, P, D):
        w.writerow([f"{l:.3f}", f"{v:.5f}", f"{p:.5f}", f"{d:.5f}"])

# palette: dataviz reference categorical slots 1-3 (validated, light mode)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d3"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=200)
ax.set_facecolor("#fcfcfb"); fig.patch.set_facecolor("white")
ax.axhline(1.0, color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=1)
ax.plot(L, V, color=BLUE, lw=2.0, zorder=3)
ax.plot(L, P, color=ORANGE, lw=2.0, zorder=3)
ax.plot(L, D, color=AQUA, lw=2.0, zorder=3)
# direct labels (text in ink, a colored tick carries identity)
ax.text(300, 1.95, "verified exponent, $\\rho(n)/n$ with $\\rho(n)=n(\\ln\\ln(n{+}16))^2/\\sqrt{\\ln(n{+}16)}$", color=INK, fontsize=8.2, va="bottom")
ax.plot([285, 295], [1.985, 1.985], color=BLUE, lw=3)
ax.text(300, 0.56, "manuscript, general: $n\\ln\\ln n/\\sqrt{\\ln n}$ (not verified)", color=INK, fontsize=8.2, va="bottom")
ax.plot([285, 295], [0.595, 0.595], color=ORANGE, lw=3)
ax.text(300, 0.07, "manuscript, fixed density: $n/\\sqrt{\\ln n}$ (not verified)", color=INK, fontsize=8.2, va="bottom")
ax.plot([285, 295], [0.105, 0.105], color=AQUA, lw=3)
ax.text(2990, 1.02, "brute force: $2^n$", color=INK2, fontsize=8.2, ha="right", va="bottom")
# landmarks
ax.scatter([peak_l10], [peak_v], s=28, color="white", edgecolor=BLUE, linewidth=1.6, zorder=4)
ax.annotate(f"peak {peak_v:.2f} at $n\\approx10^{{{peak_l10:.1f}}}$", (peak_l10, peak_v), (peak_l10 + 60, peak_v + 0.14),
            fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.scatter([cross_l10], [1.0], s=28, color="white", edgecolor=BLUE, linewidth=1.6, zorder=4)
ax.annotate("back below $2^n$ only at $n\\approx e^{5504}\\approx10^{2390}$", (cross_l10, 1.0), (cross_l10 - 60, 1.30),
            fontsize=8, color=INK, ha="right", arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.scatter([math.log10(50)], [small[1][1]], s=28, color="white", edgecolor=BLUE, linewidth=1.6, zorder=4)
ax.annotate("above $2^n$ from $n=50$", (math.log10(50), small[1][1]), (120, 1.33), fontsize=8, color=INK,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.set_xlim(1, 3000); ax.set_ylim(0, 2.4)
ax.set_xlabel("number of variables $n$  (axis is $\\log_{10} n$: 1 means $n=10$, 1000 means $n=10^{1000}$)")
ax.set_ylabel("exponent relative to brute force\n(bound $=2^{\\,\\text{ratio}\\cdot n}$ at $A=1$)")
ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "rho_over_n.pdf"); fig.savefig(FIG / "rho_over_n.png")
print(f"peak ratio {peak_v:.3f} at log10 n = {peak_l10:.2f}; rho(49)/49 = {small[0][1]:.4f}, rho(50)/50 = {small[1][1]:.4f}; "
      f"crossing back at ln n = {cross_ln:.0f} (log10 n = {cross_l10:.0f}); written {FIG/'rho_over_n.pdf'}")

# ---- second figure: the practical range, n = 10 .. 10^6, same three curves ----------------
L2 = np.linspace(1.0, 6.0, 2000)
V2, P2, D2 = zip(*[(rho_verified(10 ** l) / 10 ** l, rho_paper(10 ** l) / 10 ** l, rho_fixed_density(10 ** l) / 10 ** l) for l in L2])
fig2, ax2 = plt.subplots(figsize=(6.4, 3.2), dpi=200)
ax2.set_facecolor("#fcfcfb"); fig2.patch.set_facecolor("white")
ax2.axhline(1.0, color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=1)
ax2.plot(L2, V2, color=BLUE, lw=2.0, zorder=3)
ax2.plot(L2, P2, color=ORANGE, lw=2.0, zorder=3)
ax2.plot(L2, D2, color=AQUA, lw=2.0, zorder=3)
ax2.text(2.05, 1.72, "verified exponent $\\rho(n)/n$", color=INK, fontsize=8.5, va="bottom"); ax2.plot([1.92, 2.0], [1.75, 1.75], color=BLUE, lw=3)
ax2.text(2.05, 0.80, "manuscript, general (not verified)", color=INK, fontsize=8.5, va="bottom"); ax2.plot([1.92, 2.0], [0.83, 0.83], color=ORANGE, lw=3)
ax2.text(2.05, 0.19, "manuscript, fixed density (not verified)", color=INK, fontsize=8.5, va="bottom"); ax2.plot([1.92, 2.0], [0.22, 0.22], color=AQUA, lw=3)
ax2.text(5.97, 1.02, "brute force: $2^n$", color=INK2, fontsize=8.5, ha="right", va="bottom")
for n_mark in (50, 125, 1000, 10 ** 4, 10 ** 6):
    v = rho_verified(n_mark) / n_mark
    ax2.scatter([math.log10(n_mark)], [v], s=22, color="white", edgecolor=BLUE, linewidth=1.4, zorder=4)
    ax2.annotate(f"{v:.2f}", (math.log10(n_mark), v), (0, 7), textcoords="offset points", fontsize=7.5, ha="center", color=INK)
ax2.set_xlim(1, 6); ax2.set_ylim(0, 2.0)
ax2.set_xticks([1, 2, 3, 4, 5, 6]); ax2.set_xticklabels(["$10$", "$10^2$", "$10^3$", "$10^4$", "$10^5$", "$10^6$"])
ax2.set_xlabel("number of variables $n$ (the practical range; marks at $n=50,125,10^3,10^4,10^6$)")
ax2.set_ylabel("exponent relative to brute force\n(bound $=2^{\\,\\text{ratio}\\cdot n}$ at $A=1$)")
ax2.grid(True, color=GRID, lw=0.6); ax2.set_axisbelow(True)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
fig2.tight_layout()
fig2.savefig(FIG / "rho_over_n_practical.pdf"); fig2.savefig(FIG / "rho_over_n_practical.png")
print("written", FIG / "rho_over_n_practical.pdf")
