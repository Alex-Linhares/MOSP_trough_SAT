"""Two figures for §28: the two-key rule seed against Chu & Stuckey's own seed.

Reads the committed-elsewhere sweep output of `learning.rule_seed`
(`learning/data/rule_seed/`, git-ignored; regenerate with
`python -m learning.rule_seed --workers 16`) and writes

    reports/figures/rule_seed_scatter.png   excess over optimum, per instance
    reports/figures/rule_seed_by_size.png   mean excess and % exact by size

Both strategies are `restricted_dfs` at 200,000 nodes; only the starting
incumbent differs (MCN closing order for `cs-dfs`, the two-key rule for
`rule+cs-dfs`). Values are upper bounds scored against certified optima.

    python -m learning.rule_seed_plots
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "learning" / "data" / "rule_seed"
FIG = ROOT / "reports" / "figures"
BANDS = [(9, 15), (16, 25), (26, 30), (31, 40), (41, 60), (61, 80), (81, 100), (101, 134)]


def load():
    opt = {r["instance"]: r["optimum"]
           for r in json.load(open(DATA / "sweep_cs-dfs.json"))["rows"]}
    rows = []
    for t in csv.DictReader(open(DATA / "timing.csv")):
        o = opt[t["instance"]]
        rows.append((int(t["n_customers"]),
                     int(t["value:cs-dfs"]) - o,
                     int(t["value:rule+cs-dfs"]) - o))
    return np.array(rows)


def scatter(a):
    n, old, new = a.T
    counts = Counter(zip(old, new))
    xs, ys, cs = zip(*[(x, y, c) for (x, y), c in counts.items()])
    cs = np.array(cs)
    fig, ax = plt.subplots(figsize=(7, 6.3))
    lim = max(old.max(), new.max()) + 0.7
    ax.fill_between([-0.7, lim], [-0.7, lim], lim, color="#f4d6d6", alpha=0.5, lw=0)
    ax.fill_between([-0.7, lim], -0.7, [-0.7, lim], color="#d6ecd6", alpha=0.5, lw=0)
    ax.plot([-0.7, lim], [-0.7, lim], color="0.4", lw=1, ls="--")
    sc = ax.scatter(xs, ys, s=30 + 60 * np.log10(cs) ** 2, c=np.log10(cs),
                    cmap="viridis", edgecolor="k", lw=0.4, zorder=3)
    for x, y, c in zip(xs, ys, cs):
        if c >= 5:
            ax.annotate(f"{c:,}", (x, y), xytext=(6, 5), textcoords="offset points",
                        fontsize=7.5, zorder=4)
    better, worse = int((new < old).sum()), int((new > old).sum())
    ax.text(0.97 * lim, 0.25, f"rule better\n{better:,} instances", ha="right",
            va="bottom", color="#1d6b1d", fontsize=10, weight="bold")
    ax.text(0.2, 0.93 * lim, f"rule worse\n{worse:,} instances", ha="left",
            va="top", color="#8b1c1c", fontsize=10, weight="bold")
    ax.set_xlim(-0.7, lim); ax.set_ylim(-0.7, lim)
    ax.set_xlabel("Chu & Stuckey seed (cs-dfs): stacks above the optimum")
    ax.set_ylabel("Two-key rule seed (rule+cs-dfs): stacks above the optimum")
    ax.set_title(f"Per instance, {len(a):,} certified instances\n"
                 f"marker size and colour = number of instances at that point "
                 f"({int(((old == new)).sum()):,} on the diagonal)", fontsize=10)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8)
    cb.set_label("log10(instances)")
    fig.tight_layout()
    fig.savefig(FIG / "rule_seed_scatter.png", dpi=150)


def by_size(a):
    n, old, new = a.T
    labels, mo, mn, eo, en, cnt = [], [], [], [], [], []
    for lo, hi in BANDS:
        m = (n >= lo) & (n <= hi)
        if not m.any():
            continue
        labels.append(f"{lo}–{hi}\n({m.sum():,})")
        mo.append(old[m].mean()); mn.append(new[m].mean())
        eo.append(100 * (old[m] == 0).mean()); en.append(100 * (new[m] == 0).mean())
    x = np.arange(len(labels)); w = 0.38
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7.5), sharex=True)
    ax1.bar(x - w / 2, mo, w, label="Chu & Stuckey seed (cs-dfs)", color="#9aa7b8")
    ax1.bar(x + w / 2, mn, w, label="two-key rule seed (rule+cs-dfs)", color="#2f6f9f")
    ax1.set_ylabel("mean stacks above optimum")
    ax1.legend(frameon=False)
    ax1.set_title("By instance size (customers; instance count in brackets)", fontsize=10)
    ax2.bar(x - w / 2, eo, w, color="#9aa7b8")
    ax2.bar(x + w / 2, en, w, color="#2f6f9f")
    ax2.set_ylabel("% of instances at the optimum")
    ax2.set_ylim(0, 105)
    ax2.set_xticks(x, labels, fontsize=8.5)
    ax2.set_xlabel("customers")
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "rule_seed_by_size.png", dpi=150)


if __name__ == "__main__":
    a = load()
    scatter(a); by_size(a)
    n, old, new = a.T
    print(f"{len(a)} instances | better {(new < old).sum()} | worse {(new > old).sum()} | "
          f"exact {100*(old==0).mean():.1f}% -> {100*(new==0).mean():.1f}%")
