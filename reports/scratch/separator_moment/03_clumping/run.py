"""loop0011 item 03: the clumping decomposed — exact-size empty pairs `X₁`,
distinct separators `X₂`, closed pairs `X₃` (and the closure image `X₃′`) and
move-classes `X₄` on graphs with exact pathwidth (`reports/separator_moment.md` §3).

    nice -n 19 python3 reports/scratch/separator_moment/03_clumping/run.py --workers 8
    (stages: solve, count, rates, overlap; `--stage` runs one)

Stage `solve` draws fresh `G(n, c/n)` at `n ∈ {14, …, 24}`, `c ∈ {4, 6, 8, 10}`,
200 per cell (seed = CRC of the cell and index), proves the width with the C
program `pathwidth_solver/cli/pathwidth -l -t 60` (layout kept) and, at
`n ≤ 16`, checks it against the subset DP; it also lists the pilot's `n = 20`
graphs at `c ∈ {4, 6, 8, 10}` (widths on record, `reports/scratch/gnp_pilot/results.csv`)
and the certified `fixed` covers of `learning/data/ensemble/results.csv` at
`n ∈ {10, 15, 20, 25}`, `d ∈ {4, 6}`, `m = n` (`pw = optimum − 1`). Nothing on
record is re-solved. Stage `count` enumerates the four counts at
`k = pw − 1, pw, pw + 1, pw + 2`; `rates` fits the slopes; `overlap`
histograms the overlap tables of pairs of pairs at `n = 20`, `c = 10`.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import subprocess
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from learning.separator_moment import (  # noqa: E402
    closed_pairs, closed_pairs_pruned, closure_image, count_exact_pairs, enumerate_empty_pairs,
    forced_sizes, gnp_masks, mosp_masks, move_classes, overlap_tables, popcount,
    second_moment_rate_gnp, separators_of, vertex_separation,
)

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
CLI = ROOT / "pathwidth_solver/cli/pathwidth"
PILOT = ROOT / "reports/scratch/gnp_pilot/results.csv"
ENSEMBLE = ROOT / "learning/data/ensemble/results.csv"

SIZES = [14, 16, 18, 20, 22, 24]
CS = [4, 6, 8, 10]
PER_CELL = 200
COVER_N = [10, 15, 20, 25]
COVER_D = [4, 6]
MAX_PAIRS = 2_000_000       # above this X₁ is counted by binomials and the rest skipped
MAX_X4_PAIRS = 400_000      # above this the move-classes are skipped
MAX_SETS = 3_000_000        # the pruned family for X₃

INST_FIELDS = ["source", "cell", "n", "c", "sample", "seed", "edges", "pw", "status", "dp_pw", "layout"]
COUNT_FIELDS = ["source", "cell", "n", "c", "sample", "pw", "k", "N", "t", "X1", "X2", "X3", "X3p", "X3_check", "X4", "seconds", "note"]


def fresh_seed(n: int, c: int, i: int) -> int:
    return zlib.crc32(f"sep03:{n}:{c}:{i}".encode()) & 0x7FFFFFFF


def g6(n: int, p: float, seed: int) -> str:
    return nx.to_graph6_bytes(nx.gnp_random_graph(n, p, seed=seed), header=False).decode().strip()


def run_cli(lines: list[str], budget: int = 60) -> list[tuple[int, str, str]]:
    out = subprocess.run([str(CLI), "-l", "-t", str(budget)], input="\n".join(lines) + "\n",
                         capture_output=True, text=True, check=True).stdout.splitlines()
    res = []
    it = iter(out)
    for a in it:
        b = next(it)
        _, w, status = a.split()
        res.append((int(w), status, b.split(" ", 1)[1]))
    return res


def solve_cell(args):
    n, c = args
    seeds = [fresh_seed(n, c, i) for i in range(PER_CELL)]
    lines = [g6(n, c / n, s) for s in seeds]
    res = run_cli(lines)
    rows = []
    for i, (s, (w, status, layout)) in enumerate(zip(seeds, res)):
        adj = gnp_masks(n, c / n, s)
        dp = vertex_separation(adj) if n <= 16 else ""
        if dp != "" and dp != w:
            raise RuntimeError(f"DP {dp} != C {w} at n={n} c={c} seed={s}")
        rows.append(dict(source="fresh", cell=f"g_n{n}_c{c}", n=n, c=c, sample=i, seed=s,
                         edges=sum(popcount(a) for a in adj) // 2, pw=w, status=status, dp_pw=dp, layout=layout))
    return rows


def stage_solve(workers: int) -> None:
    rows = []
    with Pool(workers) as pool:
        for r in pool.imap_unordered(solve_cell, [(n, c) for n in SIZES for c in CS]):
            rows += r
            print(f"solved {r[0]['cell']}", flush=True)
    with PILOT.open() as f:
        for r in csv.DictReader(f):
            if int(r["n"]) == 20 and float(r["c"]) in CS and r["status"] in ("bound", "refutation", "minor"):
                c = int(float(r["c"]))
                rows.append(dict(source="pilot", cell=f"p_n20_c{c}", n=20, c=c, sample=int(r["sample"]),
                                 seed=int(r["seed"]), edges=int(r["m"]), pw=int(r["width"]), status=r["status"],
                                 dp_pw="", layout=r["layout"]))
    with ENSEMBLE.open() as f:
        for r in csv.DictReader(f):
            if r["generator"] == "fixed" and r["m"] == r["n"] and int(r["n"]) in COVER_N \
                    and float(r["param"]) in COVER_D and r["certified"] == "True":
                rows.append(dict(source="cover", cell=r["cell"], n=int(r["n"]), c=int(float(r["param"])),
                                 sample=int(r["index"]), seed=int(r["seed"]), edges="", pw=int(r["optimum"]) - 1,
                                 status="certified", dp_pw="", layout=""))
    rows.sort(key=lambda r: (r["source"], r["n"], r["c"], r["sample"]))
    with (HERE / "instances.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, INST_FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} instances written")


def masks_of(r: dict) -> list[int]:
    n = int(r["n"])
    if r["source"] == "cover":
        from learning.ensemble import Cell, generate
        inst = generate(Cell.parse(f"f:{n}:{n}:{r['c']}"), int(r["sample"]))
        return mosp_masks(inst.matrix)
    return gnp_masks(n, float(r["c"]) / n, int(r["seed"]))


def count_one(r: dict) -> list[dict]:
    n, pw = int(r["n"]), int(r["pw"])
    adj = masks_of(r)
    if r["source"] == "cover":
        # the certified optimum is pw + 1; cross-check the DP where it is cheap
        if n <= 16:
            assert vertex_separation(adj) == pw, (r["cell"], r["sample"])
    out = []
    for k in (pw - 1, pw, pw + 1, pw + 2):
        if k < 0 or k >= n:
            continue
        t0 = time.monotonic()
        N, t = forced_sizes(n, k)
        row = dict(source=r["source"], cell=r["cell"], n=n, c=r["c"], sample=r["sample"], pw=pw, k=k, N=N, t=t,
                   X1="", X2="", X3="", X3p="", X3_check="", X4="", seconds="", note="")
        try:
            pairs = enumerate_empty_pairs(adj, k, MAX_PAIRS)
        except OverflowError:
            row["X1"] = count_exact_pairs(adj, k)
            row["note"] = "X1 by binomials; X2, X3, X4 skipped (pairs > cap)"
            row["seconds"] = round(time.monotonic() - t0, 3)
            out.append(row)
            continue
        row["X1"] = len(pairs)
        row["X2"] = len(separators_of(pairs, n))
        try:
            X3 = closed_pairs_pruned(adj, k, MAX_SETS)
            row["X3"] = len(X3)
            if n <= 16 and k == pw:
                row["X3_check"] = len(closed_pairs(adj, k))
                assert row["X3_check"] == row["X3"], (r["cell"], r["sample"])
        except OverflowError:
            row["note"] += "X3 skipped (sets > cap); "
        row["X3p"] = len(closure_image(adj, pairs))
        if len(pairs) <= MAX_X4_PAIRS:
            row["X4"] = max(move_classes(pairs, n)) + 1 if pairs else 0
        else:
            row["note"] += "X4 skipped (pairs > cap); "
        row["seconds"] = round(time.monotonic() - t0, 3)
        out.append(row)
    return out


def stage_count(workers: int) -> None:
    with (HERE / "instances.csv").open() as f:
        rows = list(csv.DictReader(f))
    # hardest first so the pool's tail is short
    rows.sort(key=lambda r: (-int(r["n"]), int(r["c"])))
    done = 0
    t0 = time.monotonic()
    with (HERE / "counts.csv").open("w", newline="") as f, Pool(workers) as pool:
        w = csv.DictWriter(f, COUNT_FIELDS)
        w.writeheader()
        for res in pool.imap_unordered(count_one, rows, chunksize=4):
            w.writerows(res)
            done += 1
            if done % 200 == 0:
                f.flush()
                print(f"counted {done}/{len(rows)} in {time.monotonic() - t0:.0f} s", flush=True)
    print(f"counted {done} instances in {time.monotonic() - t0:.0f} s")


def ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Slope and its standard error of `y` on `x` (ordinary least squares)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    xm = x - x.mean()
    slope = float((xm * (y - y.mean())).sum() / (xm ** 2).sum())
    resid = y - y.mean() - slope * xm
    dof = max(len(x) - 2, 1)
    se = math.sqrt(float((resid ** 2).sum() / dof / (xm ** 2).sum()))
    return slope, se


def stage_rates() -> None:
    import pandas as pd
    df = pd.read_csv(HERE / "counts.csv")
    df["dk"] = df["k"] - df["pw"]
    for col in ("X1", "X2", "X3", "X3p", "X4"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ("X2", "X3", "X3p", "X4"):
        df[f"r_{col}"] = np.log(df["X1"] / df[col])
    df["lX1"] = np.log(df["X1"].where(df["X1"] > 0))
    cells = []
    for (src, n, c, dk), g in df.groupby(["source", "n", "c", "dk"]):
        pos = g[g["X1"] > 0]
        row = dict(source=src, n=n, c=c, dk=dk, instances=len(g), X1_positive=len(pos),
                   share_X1_zero=round(1 - len(pos) / len(g), 4),
                   pw_mean=round(g["pw"].mean(), 3), beta_mean=round((g["pw"] / g["n"]).mean(), 4),
                   X1_gm=round(float(np.exp(pos["lX1"].mean())), 2) if len(pos) else "",
                   X1_med=pos["X1"].median() if len(pos) else "",
                   X1_max=pos["X1"].max() if len(pos) else "")
        for col in ("X2", "X3", "X3p", "X4"):
            v = pos[f"r_{col}"].dropna()
            row[f"{col}_n"] = len(v)
            row[f"lr_{col}_mean"] = round(float(v.mean()), 4) if len(v) else ""
            row[f"lr_{col}_se"] = round(float(v.std(ddof=1) / math.sqrt(len(v))), 4) if len(v) > 1 else ""
            row[f"r_{col}_gm"] = round(float(np.exp(v.mean())), 3) if len(v) else ""
            row[f"r_{col}_med"] = round(float(np.exp(v.median())), 3) if len(v) else ""
            row[f"r_{col}_max"] = round(float(np.exp(v.max())), 3) if len(v) else ""
        row["seconds_mean"] = round(g["seconds"].mean(), 3)
        cells.append(row)
    cells = pd.DataFrame(cells)
    cells.to_csv(HERE / "cells.csv", index=False)
    slopes = []
    for (src, c, dk), g in df.groupby(["source", "c", "dk"]):
        if src == "pilot":
            continue
        pos = g[g["X1"] > 0]
        row = dict(source=src, c=c, dk=dk, instances=len(pos), n_min=g["n"].min(), n_max=g["n"].max())
        s, se = ols(pos["n"], pos["lX1"])
        row["slope_lX1"], row["se_lX1"] = round(s, 4), round(se, 4)
        for col in ("X2", "X3", "X3p", "X4"):
            v = pos[["n", f"r_{col}"]].dropna()
            if len(v) > 2:
                s, se = ols(v["n"], v[f"r_{col}"])
                row[f"slope_{col}"], row[f"se_{col}"] = round(s, 4), round(se, 4)
            else:
                row[f"slope_{col}"], row[f"se_{col}"] = "", ""
        slopes.append(row)
    slopes = pd.DataFrame(slopes)
    slopes.to_csv(HERE / "slopes.csv", index=False)
    # the second-moment prediction at the cells' mean β, G(n, c/n)
    sm = []
    for c in CS:
        for n in SIZES:
            g = df[(df.source == "fresh") & (df.n == n) & (df.c == c) & (df.dk == 0)]
            beta = float((g["pw"] / g["n"]).mean())
            a = (1 - beta) / 2
            sup, twog, table = second_moment_rate_gnp(a, c)
            sm.append(dict(c=c, n=n, beta_mean=round(beta, 4), a=round(a, 4), g_a=round(twog / 2, 4),
                           sup=round(sup, 4), ratio_exponent=round(sup - twog, 4),
                           **{f"T_{lab}": round(float(x), 4) for lab, x in zip(
                               ["AA", "AR", "AS", "RA", "RR", "RS", "SA", "SR", "SS"], table)}))
    pd.DataFrame(sm).to_csv(HERE / "second_moment_gnp.csv", index=False)
    with (HERE / "rates.log").open("w") as f:
        print(cells.to_string(), file=f)
        print(file=f)
        print(slopes.to_string(), file=f)
        print(file=f)
        print(pd.DataFrame(sm).to_string(), file=f)
    print(slopes.to_string())


def stage_overlap(graphs: int = 20) -> None:
    import pandas as pd
    with (HERE / "instances.csv").open() as f:
        rows = [r for r in csv.DictReader(f) if r["source"] == "fresh" and r["n"] == "20" and r["c"] == "10"]
    rows = rows[:graphs]
    n = 20
    hist_cols = ["AA", "AR", "AS", "RA", "RR", "RS", "SA", "SR", "SS"]
    allt = []
    per_graph = []
    for r in rows:
        adj = masks_of(r)
        pw = int(r["pw"])
        pairs = enumerate_empty_pairs(adj, pw)
        T = overlap_tables(pairs, n)
        allt.append(T)
        per_graph.append(dict(sample=r["sample"], pw=pw, X1=len(pairs), pairs_of_pairs=len(T),
                              **{f"mean_{c}": round(float(T[:, i].mean() / n), 4) if len(T) else "" for i, c in enumerate(hist_cols)}))
    T = np.concatenate(allt) / n
    pd.DataFrame(per_graph).to_csv(HERE / "overlap_per_graph.csv", index=False)
    beta = float(np.mean([int(r["pw"]) / n for r in rows]))
    a = (1 - beta) / 2
    sup, twog, ext = second_moment_rate_gnp(a, 10)
    prod = np.array([a * a, a * a, a * (1 - 2 * a), a * a, a * a, a * (1 - 2 * a), a * (1 - 2 * a), a * (1 - 2 * a), (1 - 2 * a) ** 2])
    summary = pd.DataFrame({
        "cell": hist_cols,
        "measured_mean": T.mean(axis=0).round(4),
        "measured_median": np.median(T, axis=0).round(4),
        "measured_p90": np.quantile(T, 0.9, axis=0).round(4),
        "extremal_table": ext.round(4),
        "product_table": prod.round(4),
    })
    summary.to_csv(HERE / "overlap_summary.csv", index=False)
    # the histogram of the three A-row cells
    edges = np.arange(0, 1.0001, 1 / n) - 0.5 / n
    hist = pd.DataFrame({"bin_lo": edges[:-1].round(4), "bin_hi": edges[1:].round(4)})
    for i, c in enumerate(hist_cols):
        hist[c] = np.histogram(T[:, i], bins=edges)[0]
    hist.to_csv(HERE / "overlap_hist.csv", index=False)
    with (HERE / "overlap.log").open("w") as f:
        print(f"{len(rows)} graphs at n = 20, c = 10; mean beta = {beta:.4f}, a = {a:.4f}; "
              f"{len(T)} ordered pairs of distinct pairs", file=f)
        print(f"second moment at a: sup = {sup:.4f}, 2g = {twog:.4f}, ratio exponent = {sup - twog:.4f}", file=f)
        print(summary.to_string(), file=f)
        print(pd.DataFrame(per_graph).to_string(), file=f)
    draw(T, ext, prod, n, hist_cols)
    print(summary.to_string())


def draw(T: np.ndarray, ext: np.ndarray, prod: np.ndarray, n: int, cols: list[str]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.3), sharey=True)
    labels = {"AA": "|A ∩ A′| / n", "AR": "|A ∩ R′| / n", "AS": "|A ∩ S′| / n", "SS": "|S ∩ S′| / n"}
    edges = np.arange(0, 1.0001, 1 / n) - 0.5 / n
    for ax, c in zip(axes, ["AA", "AR", "AS", "SS"]):
        i = cols.index(c)
        ax.hist(T[:, i], bins=edges, color="#2a78d6", edgecolor="#fcfcfb", linewidth=0.8, density=True)
        ax.axvline(ext[i], color="#eb6834", linewidth=2, label="extremal table")
        ax.axvline(prod[i], color="#1baf7a", linewidth=2, linestyle="--", label="product table")
        ax.set_xlabel(labels[c], color="#0b0b0b")
        ax.set_xlim(-0.03, 0.33 if c != "SS" else 0.68)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#c3c2b7")
        ax.spines["bottom"].set_color("#c3c2b7")
        ax.tick_params(colors="#52514e")
        ax.grid(axis="y", color="#e6e5e1", linewidth=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("density (pairs of pairs)", color="#52514e")
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(HERE / "overlap_hist.png", dpi=160)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--stage", choices=["solve", "count", "rates", "overlap"], default=None)
    a = ap.parse_args()
    os.nice(19)
    stages = [a.stage] if a.stage else ["solve", "count", "rates", "overlap"]
    for s in stages:
        t0 = time.monotonic()
        {"solve": lambda: stage_solve(a.workers), "count": lambda: stage_count(a.workers),
         "rates": stage_rates, "overlap": stage_overlap}[s]()
        print(f"stage {s}: {time.monotonic() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
