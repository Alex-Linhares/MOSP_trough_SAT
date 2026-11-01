"""loop0011 item 04: the planted cluster — condition on one exact-size empty pair
and count the other exact-size empty pairs, their distance from the planted
pair and the mechanism (`reports/separator_moment.md` §4).

    nice -n 19 python3 reports/scratch/separator_moment/04_planted/run.py --workers 8
    (stages: run, stats, draw; `--stage` runs one; `--probe` times the largest cells)

Planting. `G(n, c/n)` with the edges between a fixed `A` (`|A| = t`) and `R`
(`|R| = N − t`) deleted — the law of `G(n, c/n)` given `(A, R)` empty — at
`n ∈ {16, 20, 24, 28, 32}`, `c ∈ {6, 10}`, `β ∈ {β*(c), β*(c) + 0.1}` rounded
to `k = round(β n)`, 200 per cell; and the cover model at `(d, μ) = (6, 1)`,
`n ∈ {16, 20, 24, 28}`, `m = n` patterns each a uniform 6-set among those
meeting at most one side. No pathwidth is computed: the planted pair makes
`X ≥ 1` by construction. Counting: every exact-size empty pair by item 03's
enumerator, `X′ = X − 1`, the overlap table of each with the planted pair, the
separators, closed pairs and move-classes of item 03. The planted mean is
`E[X′ | P₀ empty] = E[X²]/E[X] − 1`, exactly at the cell's `(n, t, r)`.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
import zlib
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from learning.first_moment import beta_star, second_moment_rate  # noqa: E402
from learning.separator_moment import (  # noqa: E402
    beta_star_gnp, closed_pairs_pruned, closure_image, enumerate_empty_pairs, forced_sizes, gnp_masks,
    hamming_distance, mosp_masks, move_classes, overlap_table, plant_cover, plant_pair, planted_mean_cover,
    planted_mean_gnp, popcount, second_moment_rate_gnp, separators_of,
)

HERE = Path(__file__).resolve().parent

GNP_N = [16, 20, 24, 28, 32]
GNP_C = [6, 10]
COVER_N = [16, 20, 24, 28]
COVER_D = 6
PER_CELL = 200
BETAS = {"star": 0.0, "star+0.1": 0.1}
EPS = (0.05, 0.1, 0.2, 0.3)
FAR = 0.2                     # a pair is "far" when its Hamming distance from the planted pair exceeds FAR·n
MAX_PAIRS = 2_000_000         # above this the row is censored (X′ > cap)
MAX_X4_PAIRS = 300_000        # above this the move-classes are skipped
MAX_SETS = 3_000_000          # the pruned family for X₃
MECH_SAMPLE = 200_000         # far pairs examined for the mechanism, at most (sampled beyond)

FIELDS = ["source", "cell", "n", "c", "beta_label", "beta_nominal", "k", "beta", "N", "t", "r", "sample", "seed",
          "edges", "X", "Xp", "X2", "X3", "X3p", "X4", "class_planted", "has_reverse",
          *[f"within_{e}" for e in EPS], *[f"within_rev_{e}" for e in EPS], "far", "far_reversed", "mech_pairs",
          "seconds", "note"]


def seed_of(src: str, n: int, c: int, beta_label: str, i: int) -> int:
    return zlib.crc32(f"sep04:{src}:{n}:{c}:{beta_label}:{i}".encode()) & 0x7FFFFFFF


def cells() -> list[dict]:
    out = []
    for n in GNP_N:
        for c in GNP_C:
            bs = beta_star_gnp(c)
            for lab, off in BETAS.items():
                k = int(round((bs + off) * n))
                out.append(dict(source="gnp", cell=f"g_n{n}_c{c}_{lab}", n=n, c=c, beta_label=lab,
                                beta_nominal=round(bs + off, 4), k=k))
    bs = beta_star(1.0, {COVER_D: 1})
    for n in COVER_N:
        for lab, off in BETAS.items():
            k = int(round((bs + off) * n))
            out.append(dict(source="cover", cell=f"f_n{n}_d{COVER_D}_{lab}", n=n, c=COVER_D, beta_label=lab,
                            beta_nominal=round(bs + off, 4), k=k))
    return out


def planted_instance(cell: dict, i: int):
    """The planted graph (adjacency masks), the planted pair and the seed."""
    n, k = cell["n"], cell["k"]
    N, t = forced_sizes(n, k)
    r = N - t
    A = (1 << t) - 1
    R = ((1 << r) - 1) << t
    seed = seed_of(cell["source"], n, cell["c"], cell["beta_label"], i)
    if cell["source"] == "gnp":
        adj = plant_pair(gnp_masks(n, cell["c"] / n, seed), A, R)
    else:
        M = plant_cover(n, n, COVER_D, A, R, np.random.default_rng(seed))
        adj = mosp_masks(M)
    return adj, (A, R), seed


def planted_one(job):
    cell, i = job
    n, k = cell["n"], cell["k"]
    N, t = forced_sizes(n, k)
    r = N - t
    t0 = time.monotonic()
    adj, P0, seed = planted_instance(cell, i)
    A, R = P0
    full = (1 << n) - 1
    S = full & ~(A | R)
    row = dict(source=cell["source"], cell=cell["cell"], n=n, c=cell["c"], beta_label=cell["beta_label"],
               beta_nominal=cell["beta_nominal"], k=k, beta=round(k / n, 4), N=N, t=t, r=r, sample=i, seed=seed,
               edges=sum(popcount(a) for a in adj) // 2, note="")
    extras = dict(dist=Counter(), dist_min=Counter(), mech=Counter(), base=Counter(),
                  far_table=np.zeros(9, dtype=np.int64), near_table=np.zeros(9, dtype=np.int64))
    # the degree law of S vertices into the two sides, once per instance
    sv = [v for v in range(n) if S >> v & 1]
    sides = A | R
    for s in sv:
        extras["base"][("deg_sides", popcount(adj[s] & sides))] += 1
    try:
        pairs = enumerate_empty_pairs(adj, k, MAX_PAIRS)
    except OverflowError:
        row.update(X=f">{MAX_PAIRS}", Xp=f">{MAX_PAIRS - 1}", note="censored: pairs > cap", seconds=round(time.monotonic() - t0, 3))
        return row, extras
    assert P0 in pairs, "the planted pair is not an exact-size empty pair"
    X = len(pairs)
    row["X"], row["Xp"] = X, X - 1
    row["X2"] = len(separators_of(pairs, n))
    try:
        row["X3"] = len(closed_pairs_pruned(adj, k, MAX_SETS))
    except OverflowError:
        row["X3"] = ""
        row["note"] += "X3 skipped; "
    row["X3p"] = len(closure_image(adj, pairs))
    row["has_reverse"] = int((R, A) in set(pairs))
    if X <= MAX_X4_PAIRS:
        cls = move_classes(pairs, n)
        row["X4"] = max(cls) + 1
        c0 = cls[pairs.index(P0)]
        row["class_planted"] = sum(1 for c in cls if c == c0)
    else:
        row["X4"] = row["class_planted"] = ""
        row["note"] += "X4 skipped; "
    within = [0] * len(EPS)
    within_rev = [0] * len(EPS)
    far = far_rev = 0
    far_list = []
    for Q in pairs:
        if Q == P0:
            continue
        T = overlap_table(P0, Q, n)
        d = n - T[0] - T[4] - T[8]
        d_rev = n - T[1] - T[3] - T[8]          # distance to the reversed planted pair (R, A)
        extras["dist"][d] += 1
        extras["dist_min"][min(d, d_rev)] += 1
        for j, e in enumerate(EPS):
            if d <= e * n:
                within[j] += 1
            if min(d, d_rev) <= e * n:
                within_rev[j] += 1
        if d > FAR * n:
            far += 1
            far_rev += T[3] >= T[0]
            far_list.append((Q, T))
        else:
            extras["near_table"] += np.array(T)
    for j, e in enumerate(EPS):
        row[f"within_{e}"] = within[j]
        row[f"within_rev_{e}"] = within_rev[j]
    row["far"], row["far_reversed"] = far, far_rev
    # the mechanism on far pairs: which S vertices joined a side, how many planted-side neighbours they
    # had, and how many of those were evicted into S′ (orientation-free: a vertex of S in A′ ∪ R′ can
    # keep a planted-side neighbour only on its own new side)
    if len(far_list) > MECH_SAMPLE:
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(far_list), MECH_SAMPLE, replace=False)
        far_list = [far_list[j] for j in idx]
        row["note"] += "mechanism sampled; "
    row["mech_pairs"] = len(far_list)
    for Q, T in far_list:
        extras["far_table"] += np.array(T)
        A2, R2 = Q
        S2 = full & ~(A2 | R2)
        for s in sv:
            if (A2 | R2) >> s & 1:
                nb = adj[s] & sides
                extras["mech"][("deg_sides", popcount(nb))] += 1
                extras["mech"][("evicted", popcount(nb & S2))] += 1
    row["seconds"] = round(time.monotonic() - t0, 3)
    return row, extras


def stage_run(workers: int, per_cell: int, probe: bool = False) -> None:
    cs = cells()
    if probe:
        cs = [c for c in cs if c["n"] == max(GNP_N) or (c["source"] == "cover" and c["n"] == max(COVER_N))]
        per_cell = 3
    jobs = [(c, i) for c in cs for i in range(per_cell)]
    jobs.sort(key=lambda j: (-j[0]["n"], j[0]["beta_label"]))   # hardest first
    dist = {}
    dist_min = {}
    mech = {}
    base = {}
    tables = {}
    out = HERE / ("probe.csv" if probe else "planted.csv")
    t0 = time.monotonic()
    done = 0
    with out.open("w", newline="") as f, Pool(workers) as pool:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for row, ex in pool.imap_unordered(planted_one, jobs, chunksize=1):
            w.writerow(row)
            key = row["cell"]
            dist.setdefault(key, Counter()).update(ex["dist"])
            dist_min.setdefault(key, Counter()).update(ex["dist_min"])
            mech.setdefault(key, Counter()).update(ex["mech"])
            base.setdefault(key, Counter()).update(ex["base"])
            tb = tables.setdefault(key, {"far": np.zeros(9, dtype=np.int64), "near": np.zeros(9, dtype=np.int64)})
            tb["far"] += ex["far_table"]
            tb["near"] += ex["near_table"]
            done += 1
            if done % 100 == 0 or probe:
                f.flush()
                print(f"{done}/{len(jobs)} in {time.monotonic() - t0:.0f} s: {key} #{row['sample']} X'={row['Xp']} "
                      f"{row['seconds']} s {row['note']}", flush=True)
    if probe:
        return
    with (HERE / "distance_hist.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "distance", "pairs", "pairs_at_min_distance"])
        for key in sorted(dist):
            for d in sorted(set(dist[key]) | set(dist_min[key])):
                w.writerow([key, d, dist[key].get(d, 0), dist_min[key].get(d, 0)])
    with (HERE / "mechanism.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "population", "statistic", "value", "count"])
        for key in sorted(mech):
            for (st, dg), cnt in sorted(mech[key].items()):
                w.writerow([key, "moved_in_far_pairs", st, dg, cnt])
            for (st, dg), cnt in sorted(base[key].items()):
                w.writerow([key, "all_S_vertices", st, dg, cnt])
    cols = ["AA", "AR", "AS", "RA", "RR", "RS", "SA", "SR", "SS"]
    with (HERE / "overlap_far_near.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "which", *[f"sum_{c}" for c in cols]])
        for key in sorted(tables):
            for which in ("far", "near"):
                w.writerow([key, which, *tables[key][which].tolist()])
    print(f"run: {done} instances in {time.monotonic() - t0:.0f} s")


def ols(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    xm = x - x.mean()
    slope = float((xm * (y - y.mean())).sum() / (xm ** 2).sum())
    resid = y - y.mean() - slope * xm
    dof = max(len(x) - 2, 1)
    se = math.sqrt(float((resid ** 2).sum() / dof / (xm ** 2).sum()))
    return slope, se


def stage_stats() -> None:
    import pandas as pd
    df = pd.read_csv(HERE / "planted.csv")
    df["censored"] = df["Xp"].astype(str).str.startswith(">")
    for col in ("X", "Xp", "X2", "X3", "X3p", "X4", "class_planted"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    rows = []
    for key, g in df.groupby("cell", sort=False):
        c0 = g.iloc[0]
        n, k, t, r = int(c0["n"]), int(c0["k"]), int(c0["t"]), int(c0["r"])
        src, c = c0["source"], int(c0["c"])
        a = (1 - k / n) / 2
        if src == "gnp":
            pred = planted_mean_gnp(n, t, r, c / n)
            sup, twog, _ = second_moment_rate_gnp(a, c)
        else:
            pred = planted_mean_cover(n, t, r, {COVER_D: n})
            sup, twog, _ = second_moment_rate(a, 1.0, {COVER_D: 1})
        xp = g["Xp"]
        cen = int(g["censored"].sum())
        ok = g[~g["censored"]]
        med = float(xp.median()) if cen < len(g) / 2 else math.nan
        pos = ok[ok["Xp"] > 0]
        tot_pairs = float(ok["Xp"].sum())
        row = dict(source=src, cell=key, n=n, c=c, beta_label=c0["beta_label"], k=k, beta=round(k / n, 4),
                   a=round(a, 4), N=n - k, t=t, r=r, instances=len(g), censored=cen,
                   share_zero=round(float((ok["Xp"] == 0).mean()), 4),
                   Xp_median=med, Xp_p10=float(xp.quantile(0.1)), Xp_p90=float(xp.quantile(0.9)),
                   Xp_max=float(ok["Xp"].max()),
                   Xp_gm_pos=round(float(np.exp(np.log(pos["Xp"]).mean())), 2) if len(pos) else math.nan,
                   Xp_mean=round(float(ok["Xp"].mean()), 2),
                   Xp_mean_se=round(float(ok["Xp"].std(ddof=1) / math.sqrt(len(ok))), 2),
                   Xp_pred=round(pred, 2),
                   log_med_over_n=round(math.log(med) / n, 4) if med and med > 0 else (-math.inf if med == 0 else math.nan),
                   log_mean_over_n=round(math.log(ok["Xp"].mean()) / n, 4) if ok["Xp"].mean() > 0 else math.nan,
                   log_pred_over_n=round(math.log(pred) / n, 4),
                   asym_pred_exponent=round(sup - twog / 2, 4),
                   ratio_X_X2=round(float(np.exp(np.log(ok["X"] / ok["X2"]).mean())), 3),
                   ratio_X_X3=round(float(np.exp(np.log(ok["X"] / ok["X3"]).dropna().mean())), 3),
                   ratio_X_X4=round(float(np.exp(np.log(ok["X"] / ok["X4"]).dropna().mean())), 3),
                   class_planted_median=float(ok["class_planted"].median()),
                   class_planted_max=float(ok["class_planted"].max()),
                   has_reverse_share=round(float(ok["has_reverse"].mean()), 3))
        for e in EPS:
            row[f"share_within_{e}"] = round(float(ok[f"within_{e}"].sum() / tot_pairs), 4) if tot_pairs else math.nan
            row[f"share_within_rev_{e}"] = round(float(ok[f"within_rev_{e}"].sum() / tot_pairs), 4) if tot_pairs else math.nan
            # per-instance median of the share within ε n of the pair or its reverse
            sh = (ok[f"within_rev_{e}"] / ok["Xp"].where(ok["Xp"] > 0)).dropna()
            row[f"inst_median_share_rev_{e}"] = round(float(sh.median()), 4) if len(sh) else math.nan
        row["share_far"] = round(float(ok["far"].sum() / tot_pairs), 4) if tot_pairs else math.nan
        fs = float(ok["far"].sum())
        row["far_reversed_share"] = round(float(ok["far_reversed"].sum() / fs), 4) if fs else math.nan
        # the union bound's slack at this cell: Σ_P 1[P empty]/X = 1[X > 0], so P(X > 0)/E[X] = E_planted[1/X]
        # (X = X′ + 1 ≥ 1 on every planted instance; a censored row has 1/X < 1/cap, which is set to 0)
        invx = np.where(g["censored"], 0.0, 1.0 / (g["Xp"].fillna(MAX_PAIRS) + 1))
        row["inv_X_mean"] = round(float(invx.mean()), 5)
        row["inv_X_se"] = round(float(invx.std(ddof=1) / math.sqrt(len(invx))), 5)
        row["union_slack_nats"] = round(-math.log(float(invx.mean())) / n, 4)
        # concentration of the planted mean: share of Σ X′ carried by the top 10% of instances
        xs = np.sort(ok["Xp"].values)[::-1]
        top = max(1, len(xs) // 10)
        row["top10pct_share_of_sum"] = round(float(xs[:top].sum() / xs.sum()), 3) if xs.sum() else math.nan
        row["seconds_mean"] = round(float(g["seconds"].mean()), 3)
        row["seconds_max"] = round(float(g["seconds"].max()), 3)
        rows.append(row)
    cells_df = pd.DataFrame(rows)
    cells_df.to_csv(HERE / "cells.csv", index=False)
    # growth in n: the cell medians, and the per-instance log X′ (X′ > 0)
    slopes = []
    for (src, c, lab), g in cells_df.groupby(["source", "c", "beta_label"]):
        g = g.sort_values("n")
        row = dict(source=src, c=c, beta_label=lab, n_min=int(g["n"].min()), n_max=int(g["n"].max()))
        gm = g[g["Xp_median"] > 0]
        if len(gm) >= 3:
            s, se = ols(gm["n"], np.log(gm["Xp_median"]))
            row["slope_log_median"], row["se_log_median"] = round(s, 4), round(se, 4)
        s, se = ols(g["n"], np.log(g["Xp_pred"]))
        row["slope_log_pred"], row["se_log_pred"] = round(s, 4), round(se, 4)
        s, se = ols(g["n"], np.log(g["Xp_mean"]))
        row["slope_log_mean"], row["se_log_mean"] = round(s, 4), round(se, 4)
        inst = df[(df.source == src) & (df.c == c) & (df.beta_label == lab) & (~df.censored) & (df.Xp > 0)]
        s, se = ols(inst["n"], np.log(inst["Xp"]))
        row["slope_log_Xp_inst"], row["se_log_Xp_inst"], row["inst"] = round(s, 4), round(se, 4), len(inst)
        last = g.iloc[-1]
        row["largest_n"] = int(last["n"])
        row["log_med_over_n_at_largest"] = last["log_med_over_n"]
        row["log_pred_over_n_at_largest"] = last["log_pred_over_n"]
        row["fork_ratio"] = round(last["log_med_over_n"] / last["log_pred_over_n"], 3) if last["log_pred_over_n"] > 0 and np.isfinite(last["log_med_over_n"]) else last["log_med_over_n"]
        slopes.append(row)
    slopes = pd.DataFrame(slopes)
    slopes.to_csv(HERE / "slopes.csv", index=False)
    # the mechanism: planted-side degree of the S vertices that joined a side in a far pair, against all S
    # vertices; and how many of those neighbours were evicted into S′
    mech = pd.read_csv(HERE / "mechanism.csv")
    mrows = []
    for key, g in mech.groupby("cell", sort=False):
        row = dict(cell=key)
        for pop, st, lab in (("moved_in_far_pairs", "deg_sides", "moved_deg"), ("all_S_vertices", "deg_sides", "allS_deg"),
                             ("moved_in_far_pairs", "evicted", "moved_evicted")):
            h = g[(g.population == pop) & (g.statistic == st)]
            tot = h["count"].sum()
            if tot:
                row[f"{lab}_mean"] = round(float((h["value"] * h["count"]).sum() / tot), 3)
                row[f"{lab}_share0"] = round(float(h[h.value == 0]["count"].sum() / tot), 4)
                row[f"{lab}_share_le1"] = round(float(h[h.value <= 1]["count"].sum() / tot), 4)
                row[f"{lab}_count"] = int(tot)
        mrows.append(row)
    mech_df = pd.DataFrame(mrows)
    mech_df.to_csv(HERE / "mechanism_summary.csv", index=False)
    with (HERE / "run.log").open("w") as f:
        print(cells_df.to_string(), file=f)
        print(file=f)
        print(slopes.to_string(), file=f)
        print(file=f)
        print(mech_df.to_string(), file=f)
    print(cells_df[["cell", "instances", "censored", "share_zero", "Xp_median", "Xp_mean", "Xp_mean_se", "Xp_pred",
                    "log_med_over_n", "log_mean_over_n", "log_pred_over_n", "share_far", "far_reversed_share",
                    "share_within_rev_0.1", "share_within_rev_0.3", "class_planted_median", "inv_X_mean",
                    "union_slack_nats", "top10pct_share_of_sum"]].to_string())
    print(slopes.to_string())
    print(mech_df.to_string())


def stage_draw() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    hist = pd.read_csv(HERE / "distance_hist.csv")
    cells_df = pd.read_csv(HERE / "cells.csv")
    picks = [("g_n32_c6_star", "G(n, 6/n), β*"), ("g_n32_c6_star+0.1", "G(n, 6/n), β* + 0.1"),
             ("g_n32_c10_star", "G(n, 10/n), β*"), ("g_n32_c10_star+0.1", "G(n, 10/n), β* + 0.1"),
             ("f_n28_d6_star", "cover (6, 1), β*"), ("f_n28_d6_star+0.1", "cover (6, 1), β* + 0.1")]
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 6.2), sharey=False)
    for ax, (key, label) in zip(axes.flat, picks):
        h = hist[hist.cell == key]
        n = int(cells_df[cells_df.cell == key]["n"].iloc[0])
        tot = h["pairs"].sum()
        N = int(cells_df[cells_df.cell == key]["N"].iloc[0])
        ax.bar(h["distance"] / n, h["pairs"] / tot, width=0.9 / n, color="#2a78d6", edgecolor="#fcfcfb", linewidth=0.6)
        ax.axvline(FAR, color="#eb6834", linewidth=2, label="far / near (0.2 n)")
        ax.axvline(N / n, color="#1baf7a", linewidth=2, linestyle="--", label="the reversed pair (N / n)")
        ax.set_xlabel("Hamming distance from the planted pair / n", color="#52514e", fontsize=9)
        ax.text(0.98, 0.97, f"{label}\nn = {n}, N = {N}", transform=ax.transAxes, ha="right", va="top",
                fontsize=9, color="#0b0b0b")
        ax.set_xlim(-0.02, 1.0)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#c3c2b7")
        ax.spines["bottom"].set_color("#c3c2b7")
        ax.tick_params(colors="#52514e")
        ax.grid(axis="y", color="#e6e5e1", linewidth=0.6)
        ax.set_axisbelow(True)
    axes[0, 0].set_ylabel("share of the other pairs", color="#52514e")
    axes[1, 0].set_ylabel("share of the other pairs", color="#52514e")
    axes[1, 0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(HERE / "distance_hist.png", dpi=160)
    plt.close(fig)
    print("drawn distance_hist.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--per-cell", type=int, default=PER_CELL)
    ap.add_argument("--stage", choices=["run", "stats", "draw"], default=None)
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    os.nice(19)
    if a.probe:
        stage_run(a.workers, a.per_cell, probe=True)
        return
    stages = [a.stage] if a.stage else ["run", "stats", "draw"]
    for s in stages:
        t0 = time.monotonic()
        {"run": lambda: stage_run(a.workers, a.per_cell), "stats": stage_stats, "draw": stage_draw}[s]()
        print(f"stage {s}: {time.monotonic() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
