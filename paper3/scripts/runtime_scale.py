#!/usr/bin/env python3
"""The verified exponent runtimeScale(n) = rho(n), as a multiple of n.

Paper 3, item 02 (Ralph loop0015, 2026-11-05).  The comparator statement of OpenAI's
family 378 (lean/ComparatorChallenges/SubexponentialSAT.lean at commit 4eaee875, lines
132-134) defines

    runtimeScale n = n * (log (log (n + 16)))^2 / sqrt (log (n + 16))

with Real.log, the natural logarithm.  The verified time bound is
C (L+1)^d 2^(A * runtimeScale n) (lines 136-139 and 210-211).  Brute force over all 2^n
assignments is 2^n * poly.  This script prints rho(n)/n -- the verified exponent relative
to n at A = 1 -- at a list of sizes, the two crossings of the level 1, and the peak; it
writes the table paper3/latex/tables/runtime_scale.tex and the figure
paper3/latex/figures/runtime_scale.pdf (log-n axis from 10 to 10^2500, the line rho(n)/n,
the level 1, the practical range 50..10^6 shaded).

Everything is computed in y = ln(n + 16): rho(n)/n = (ln y)^2 / sqrt(y), so no value of n
is ever formed as a float beyond 10^300 (n = e^5504 is 10^2390).  Derived from
reports/scratch/eth_audit/check_encoding.py; imports nothing from the clone.

Regenerate:  python3 -I paper3/scripts/runtime_scale.py
  -> stdout (the table and the landmarks), paper3/latex/tables/runtime_scale.tex,
     paper3/latex/figures/runtime_scale.pdf and .png
Verify the small-n values by hand: rho(n)/n = (ln ln(n+16))^2 / sqrt(ln(n+16)).
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
FIG = HERE / "latex" / "figures"
TAB = HERE / "latex" / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

LN10 = math.log(10.0)


def ratio_of_y(y: float) -> float:
    """rho(n)/n as a function of y = ln(n + 16)."""
    return math.log(y) ** 2 / math.sqrt(y)


def ratio_of_n(n: float) -> float:
    """rho(n)/n for a size n small enough to be a float (n < 1e300)."""
    return ratio_of_y(math.log(n + 16.0))


def ratio_of_log10n(l10: float) -> float:
    """rho(n)/n for n = 10^l10; exact at small n, y = l10 ln 10 + ln(1 + 16/n) beyond float range."""
    if l10 < 290:
        return ratio_of_n(10.0 ** l10)
    return ratio_of_y(l10 * LN10)  # 16/n is below double precision here


def rho_of_n(n: float) -> float:
    return n * ratio_of_n(n)


# --- landmarks --------------------------------------------------------------------------
# (ln y)^2 / sqrt y is maximal where d/dy = 0: 2 ln y / y * sqrt y - (ln y)^2 / (2 sqrt y) = 0
# -> ln y = 4 -> y = e^4, value 16 / e^2.
PEAK_Y = math.e ** 4
PEAK_VALUE = 16.0 / math.e ** 2
PEAK_LOG10_N = PEAK_Y / LN10  # n = e^(e^4) - 16; the -16 is invisible at this size


def bisect(f, lo, hi, iters=200):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# upper crossing: (ln y)^2 = sqrt y with y > e^4; f > 0 means ratio > 1 on the left
UPPER_Y = bisect(lambda y: ratio_of_y(y) - 1.0, PEAK_Y, 1.0e6)
UPPER_LOG10_N = UPPER_Y / LN10
# lower crossing in n (integers): the first n with rho(n)/n >= 1
LOWER_N = next(n for n in range(1, 10_000) if ratio_of_n(n) >= 1.0)


# --- the table --------------------------------------------------------------------------
ROWS = [  # (label for the table, log10 n or None, n as float or None)
    ("1", None, 1.0),
    ("20", None, 20.0),
    ("49", None, 49.0),
    ("50", None, 50.0),
    ("100", None, 100.0),
    ("125", None, 125.0),
    ("10^3", None, 1.0e3),
    ("10^6", None, 1.0e6),
    ("10^{12}", None, 1.0e12),
    ("10^{23.7}", PEAK_LOG10_N, None),
    ("10^{100}", 100.0, None),
    ("10^{1000}", 1000.0, None),
    ("e^{5504} \\approx 10^{2390}", UPPER_LOG10_N, None),
    ("10^{3000}", 3000.0, None),
]


def row_values(label, l10, n):
    if n is not None:
        r = ratio_of_n(n)
        return label, r, (rho_of_n(n) if n < 1e300 else None)
    return label, ratio_of_log10n(l10), None


print("verified exponent rho(n) = n (ln ln(n+16))^2 / sqrt(ln(n+16)), comparator lines 132-134")
print(f"{'n':>28}  {'rho(n)/n':>10}  {'rho(n)':>14}")
table_rows = []
for label, l10, n in ROWS:
    lab, r, rho = row_values(label, l10, n)
    rho_s = f"{rho:14.4g}" if rho is not None else f"{'':>14}"
    print(f"{lab:>28}  {r:10.4f}  {rho_s}")
    table_rows.append((lab, r, rho))

print()
print(f"first n with rho(n)/n >= 1: n = {LOWER_N}  "
      f"(rho({LOWER_N - 1})/{LOWER_N - 1} = {ratio_of_n(LOWER_N - 1):.4f}, "
      f"rho({LOWER_N})/{LOWER_N} = {ratio_of_n(LOWER_N):.4f})")
print(f"peak: ratio 16/e^2 = {PEAK_VALUE:.4f} at ln(n+16) = e^4 = {PEAK_Y:.4f}, "
      f"i.e. n ~ 10^{PEAK_LOG10_N:.2f}")
print(f"back below 1: ln(n+16) = {UPPER_Y:.2f}, i.e. n ~ e^{UPPER_Y:.0f} ~ 10^{UPPER_LOG10_N:.0f}")
print(f"check: ratio at ln(n+16) = {UPPER_Y - 1:.0f}: {ratio_of_y(UPPER_Y - 1):.6f}; "
      f"at {UPPER_Y + 1:.0f}: {ratio_of_y(UPPER_Y + 1):.6f}")

# --- the LaTeX table --------------------------------------------------------------------
with open(TAB / "runtime_scale.tex", "w") as fh:
    fh.write("% Generated by paper3/scripts/runtime_scale.py (python3 -I); do not edit.\n")
    fh.write("% rho(n) = n (ln ln(n+16))^2 / sqrt(ln(n+16)), the comparator's runtimeScale.\n")
    fh.write("\\begin{tabular}{@{}rrr@{}}\n\\toprule\n")
    fh.write("$n$ & $\\rhon/n$ & $\\rhon$ \\\\\n\\midrule\n")
    for lab, r, rho in table_rows:
        if rho is None:
            rho_s = "---"
        elif rho < 1e4:
            rho_s = f"{rho:.2f}"
        else:
            e = int(math.floor(math.log10(rho)))
            rho_s = f"${rho / 10 ** e:.2f}\\times 10^{{{e}}}$"
        fh.write(f"${lab}$ & {r:.4f} & {rho_s} \\\\\n")
    fh.write("\\bottomrule\n\\end{tabular}\n")
print("written", TAB / "runtime_scale.tex")

# --- the figure -------------------------------------------------------------------------
try:
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # the table and the numbers above do not need it
    print("figure skipped:", exc)
    sys.exit(0)

# palette: dataviz reference categorical slot 1 and neutrals (validated, light mode)
BLUE, INK, INK2, GRID, SHADE = "#2a78d6", "#0b0b0b", "#52514e", "#d9d8d3", "#f1e7d8"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK})

# dense near the small-n crossing, then even in log10 n up to 10^2500
L = np.concatenate([np.linspace(1.0, 7.0, 600), np.linspace(7.0, 2500.0, 2500)])
V = [ratio_of_log10n(float(l)) for l in L]

fig, ax = plt.subplots(figsize=(6.4, 3.3), dpi=200)
ax.set_facecolor("#fcfcfb")
fig.patch.set_facecolor("white")
ax.axvspan(math.log10(50), 6.0, color=SHADE, zorder=0, lw=0)
ax.axhline(1.0, color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=1)
ax.plot(L, V, color=BLUE, lw=2.0, zorder=3)
ax.set_xscale("log")
ax.set_xlim(1.0, 2500.0)
ax.set_ylim(0.0, 2.4)
ticks = [1, 2, 3, 6, 12, 24, 100, 1000, 2500]
ax.set_xticks(ticks)
ax.set_xticklabels(["$10$", "$10^2$", "$10^3$", "$10^6$", "$10^{12}$", "$10^{24}$",
                    "$10^{100}$", "$10^{1000}$", "$10^{2500}$"])
ax.set_xlabel("number of variables $n$ (log scale in $\\log_{10} n$)")
ax.set_ylabel("$\\rho(n)/n$: verified exponent over $n$\n(bound $= 2^{A\\rho(n)}\\cdot$poly, drawn at $A=1$)")
# landmarks
ax.scatter([math.log10(LOWER_N)], [ratio_of_n(LOWER_N)], s=28, color="white", edgecolor=BLUE, linewidth=1.6, zorder=4)
ax.annotate(f"$n = {LOWER_N}$: first above 1", (math.log10(LOWER_N), ratio_of_n(LOWER_N)), (1.08, 0.55),
            fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.scatter([PEAK_LOG10_N], [PEAK_VALUE], s=28, color="white", edgecolor=BLUE, linewidth=1.6, zorder=4)
ax.annotate(f"peak $16/e^2 = {PEAK_VALUE:.2f}$ at $n \\approx 10^{{{PEAK_LOG10_N:.1f}}}$",
            (PEAK_LOG10_N, PEAK_VALUE), (45, 2.22), fontsize=8, color=INK,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.scatter([UPPER_LOG10_N], [1.0], s=28, color="white", edgecolor=BLUE, linewidth=1.6, zorder=4)
ax.annotate(f"below 1 again at $n \\approx e^{{{UPPER_Y:.0f}}} \\approx 10^{{{UPPER_LOG10_N:.0f}}}$",
            (UPPER_LOG10_N, 1.0), (700, 0.55), fontsize=8, color=INK, ha="center",
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.text(math.sqrt(math.log10(50) * 6.0), 0.12, "practical range\n$50 \\leq n \\leq 10^6$", fontsize=8,
        color=INK2, ha="center", va="bottom")
ax.text(14, 1.03, "brute force: $2^n$", color=INK2, fontsize=8.2, ha="left", va="bottom")
ax.grid(True, color=GRID, lw=0.6, which="major")
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "runtime_scale.pdf")
fig.savefig(FIG / "runtime_scale.png")
print("written", FIG / "runtime_scale.pdf")
