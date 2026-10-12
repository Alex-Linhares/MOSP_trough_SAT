"""Timing of every exact pathwidth solve on record, and a fit.

Sources (existing results, nothing re-run):
  pathwidth_solver/bench/results/repaired/*.csv   600 s benchmark runs (no minor step);
      Rome in stages: the first stage file that proves a graph gives its time
  reports/scratch/rome_unlimited/results.csv      the 48 hardest Rome graphs, no limit
  reports/scratch/dataset_open/results.csv        the dataset's open classes, no limit
Only proved widths (proof refutation or minor) with nodes > 0 are fitted.
    python reports/solve_times/fit.py
"""
import csv, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "pathwidth_solver/bench/results/repaired"
rows, seen = [], set()
for f in ["rome.csv", "rome_120s.csv", "rome_600s.csv", "rome_3600s.csv"]:
    for r in csv.DictReader(open(R / f)):
        if r["proof"] in ("refutation", "minor") and r["name"] not in seen:
            seen.add(r["name"]); rows.append(("Rome (600 s runs)", r))
for f, lab in [("coloring.csv", "colouring"), ("named.csv", "named"), ("vsplib-hb.csv", "Harwell-Boeing"),
               ("vsplib-grids.csv", "grids"), ("vsplib-tree.csv", "trees")]:
    for r in csv.DictReader(open(R / f)):
        if r["proof"] in ("refutation", "minor"):
            rows.append((lab, r))
for r in csv.DictReader(open(ROOT / "reports/scratch/rome_unlimited/results.csv")):
    if r["proof"] in ("refutation", "minor"):
        rows.append(("Rome, hardest 48 (no limit)", r))
for r in csv.DictReader(open(ROOT / "reports/scratch/dataset_open/results.csv")):
    if r["proof"] in ("refutation", "minor"):
        rows.append(("dataset, open classes (no limit)", r))

data = [(lab, int(r["n"]), int(r["width"]), int(float(r["nodes"])), float(r["seconds"])) for lab, r in rows
        if float(r["nodes"]) > 0 and float(r["seconds"]) > 0]
labs = sorted({d[0] for d in data})
n = np.array([d[1] for d in data]); w = np.array([d[2] for d in data])
nodes = np.array([d[3] for d in data], float); secs = np.array([d[4] for d in data])
print(len(data), "proved solves with nodes > 0")

def fit(X, y, names):
    A = np.column_stack([np.ones(len(y))] + X)
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ c; r2 = 1 - res.var() / y.var()
    print("  log10 ~ " + " + ".join(f"{v:.4f}*{k}" for v, k in zip(c, ["1"] + names)), f" r2={r2:.3f}, sd={res.std():.2f} decades")
    return c, r2

ln, ls = np.log10(nodes), np.log10(secs)
nw = n * w / 100.0
rome = np.array([d[0].startswith("Rome") for d in data])
print("Rome only, nodes vs n*w/100:")
A = np.column_stack([np.ones(rome.sum()), nw[rome]])
c, *_ = np.linalg.lstsq(A, ln[rome], rcond=None)
res = ln[rome] - A @ c
print(f"  log10 nodes = {c[0]:.3f} + {c[1]:.4f} * n*w/100   r2={1-res.var()/ln[rome].var():.3f} sd={res.std():.2f}")
for lab in labs:
    msk = np.array([d[0] == lab for d in data])
    if lab.startswith("Rome"):
        continue
    r = ln[msk] - (c[0] + c[1] * nw[msk])
    print(f"  {lab:34s} {msk.sum():4d} solves: mean residual {r.mean():+.2f} decades (sd {r.std():.2f})")
print("seconds vs nodes (all):")
B = np.column_stack([np.ones(len(ls)), ln]); cb, *_ = np.linalg.lstsq(B, ls, rcond=None)
rb = ls - B @ cb; print(f"  log10 s = {cb[0]:.2f} + {cb[1]:.3f} log10 nodes  r2={1-rb.var()/ls.var():.3f}")

plt.rcParams.update({"font.size": 8})
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.7))
cols = plt.cm.tab10(np.linspace(0, 1, 10))
for i, lab in enumerate(labs):
    msk = np.array([d[0] == lab for d in data])
    axs[0].scatter(nw[msk] * 100, nodes[msk], s=5, alpha=0.45, color=cols[i % 10], label=f"{lab} ({msk.sum()})")
    axs[1].scatter(n[msk], nodes[msk], s=5, alpha=0.45, color=cols[i % 10], label=f"{lab} ({msk.sum()})")
xs = np.linspace(nw[rome].min(), nw[rome].max(), 100)
axs[0].plot(xs * 100, 10 ** (c[0] + c[1] * xs), "k--", lw=1.2,
            label=rf"Rome fit: $\mathrm{{nodes}} = 10^{{{c[0]:.2f} + {c[1]/100:.5f}\,n w}}$")
axs[0].set_xlabel(r"$n \times w$ (vertices $\times$ width)"); axs[1].set_xlabel(r"vertices $n$")
for ax in axs:
    ax.set_yscale("log"); ax.set_ylabel("search nodes")
axs[1].set_xscale("log")
axs[0].set_xscale("log")
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=3, fontsize=6.5, markerscale=1.8, frameon=False,
           bbox_to_anchor=(0.5, 0.0), handletextpad=0.2, columnspacing=1.0)
axs[0].set_title(r"against $n \times w$ (Rome fit dashed)", fontsize=8)
axs[1].set_title(r"against $n$ alone", fontsize=8)
fig.tight_layout(rect=(0, 0.13, 1, 1))
fig.savefig(Path(__file__).with_name("solve_times.png"), dpi=150)
fig.savefig(ROOT / "paper1/figures/solve_times.pdf", bbox_inches="tight")
