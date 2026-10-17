"""Pathwidth of random intersection graphs, read off certified MOSP optima.

Every certified optimum of a generated MOSP instance is `pw + 1` of its MOSP
graph (customers as vertices, a clique per product), a random intersection
graph: `lean/MOSPFormalization/MOSPGraph.lean`. Throughout, `pw = optimum - 1`.
Report: `reports/random_intersection_pathwidth.md`.

Data (read only; nothing is solved or certified here):

- `learning/data/ensemble/results.csv` -- 37,800 instances, n = 10..40,
  m in {n, 2n}, Bernoulli p and fixed customers-per-product d (§9-§12);
- `learning/data/ensemble/results_upward.csv` -- the 50-75 campaign (§16),
  restricted to the cells whose model matches (m in {n, 2n}) and to certified rows.

The one new computation is exact treewidth (`learning/treewidth.py`), per
connected component, stored resumably in
`learning/data/ensemble/treewidth_exact.csv`. It never uses pw: the search
runs from the MMD lower bound to the min-fill upper bound, so `tw <= pw` is a
genuine check, and every elimination ordering is re-verified in Python.

Usage:
    nice -n 19 python -m learning.rig_pathwidth treewidth --workers 8              # ensemble, n <= 40
    nice -n 19 python -m learning.rig_pathwidth treewidth --workers 8 --upward --nmax 50   # the 50 cells (60 skipped: cost)
    nice -n 19 python -m learning.rig_pathwidth treewidth --workers 8 --retry --deadline 300 --budget 50000000
    nice -n 19 python -m learning.rig_pathwidth kss-raw --workers 4                  # unpatched R(n, m, p), ~1 min
    python -m learning.rig_pathwidth analyse        # tables to stdout + reports/figures/rig_*.png, ~30 s
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ENS = ROOT / "learning" / "data" / "ensemble"
RESULTS = ENS / "results.csv"
UPWARD = ENS / "results_upward.csv"
TW_CSV = ENS / "treewidth_exact.csv"
FIG = ROOT / "reports" / "figures"
TW_FIELDS = ["instance_name", "source", "generator", "n", "m", "param", "optimum", "pw",
             "tw_lo", "tw_hi", "exact", "method", "components", "largest_component",
             "nodes", "censored", "order_ok", "seconds"]


# ----------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------


def load(upward: bool = True) -> pd.DataFrame:
    """Certified rows, model-matched (m in {n, 2n}), with pw and the ratio."""
    frames = [pd.read_csv(RESULTS).assign(source="ensemble")]
    if upward:
        u = pd.read_csv(UPWARD).assign(source="upward")
        frames.append(u)
    d = pd.concat(frames, ignore_index=True)
    d = d[d["certified"].astype(bool)].copy()
    d["ratio"] = d["m"] / d["n"]
    d = d[d["ratio"].isin([1.0, 2.0]) & (d["n"] <= 75)].copy()   # the 100 cell lost 9 of 75 to censoring
    d["pw"] = d["optimum"] - 1
    return d


# ----------------------------------------------------------------------------
# exact treewidth (the new compute)
# ----------------------------------------------------------------------------


def _components(masks):
    n = len(masks)
    seen = 0
    comps = []
    for v in range(n):
        if seen >> v & 1:
            continue
        comp = 1 << v
        frontier = comp
        while frontier:
            u = (frontier & -frontier).bit_length() - 1
            frontier &= frontier - 1
            new = masks[u] & ~comp
            comp |= new
            frontier |= new
        seen |= comp
        comps.append([i for i in range(n) if comp >> i & 1])
    return comps


def treewidth_of(masks, deadline: float, budget: int) -> dict:
    """Exact treewidth per component: tw(G) = max over components."""
    from learning import treewidth as T

    lo = hi = 0
    nodes = 0
    censored = False
    order_ok = True
    methods = set()
    comps = _components(masks)
    for comp in comps:
        s = len(comp)
        if s <= 1:
            continue
        index = {v: i for i, v in enumerate(comp)}
        sub = [0] * s
        for v in comp:
            bits = masks[v]
            for u in comp:
                if bits >> u & 1:
                    sub[index[v]] |= 1 << index[u]
        if all(bin(b).count("1") == s - 1 for b in sub):      # a clique
            lo, hi = max(lo, s - 1), max(hi, s - 1)
            methods.add("clique")
            continue
        if s <= 20:
            w, order = T.treewidth_exact(sub)
            out = {"lo": w, "hi": w, "order": order, "nodes": 0, "censored": False}
            methods.add("dp")
        else:
            out = T.treewidth_bounded(sub, deadline_seconds=deadline, node_budget_per_call=budget)
            methods.add("bb")
            if not out["exact"] and s <= T.DP_MAX_N:
                w, order = T.treewidth_exact(sub)
                out = {"lo": w, "hi": w, "order": order, "nodes": out["nodes"], "censored": False}
                methods.add("dp")
        if T.elimination_width(sub, out["order"]) != out["hi"]:
            order_ok = False
        lo, hi = max(lo, out["lo"]), max(hi, out["hi"])
        nodes += out["nodes"]
        censored |= bool(out["censored"])
    return {"tw_lo": lo, "tw_hi": hi, "exact": lo == hi, "method": "+".join(sorted(methods)) or "empty",
            "components": len(comps), "largest_component": max(len(c) for c in comps),
            "nodes": nodes, "censored": censored, "order_ok": order_ok}


def _tw_job(args):
    row, deadline, budget = args
    from learning.ensemble import Cell, generate
    from learning import treewidth as T

    started = time.monotonic()
    inst = generate(Cell(row["generator"], int(row["n"]), int(row["m"]), float(row["param"])),
                    int(row["index"]))
    if inst.name != row["instance_name"]:
        raise RuntimeError(f"regenerated {inst.name}, expected {row['instance_name']}")
    out = treewidth_of(T.masks_from_instance(inst), deadline, budget)
    out.update({k: row[k] for k in ("instance_name", "source", "generator", "n", "m", "param", "optimum")})
    out["pw"] = int(row["optimum"]) - 1
    out["seconds"] = round(time.monotonic() - started, 3)
    return out


def load_tw() -> pd.DataFrame:
    """One row per instance: the tightest interval recorded (retries append)."""
    t = pd.read_csv(TW_CSV)
    t["width"] = t["tw_hi"] - t["tw_lo"]
    t = t.sort_values(["instance_name", "width"]).drop_duplicates("instance_name", keep="first")
    return t.drop(columns="width")


def run_treewidth(workers: int, upward: bool, retry: bool, deadline: float, budget: int,
                  limit: int | None, nmax: int = 64) -> None:
    d = load(upward=True)
    if upward:
        d = d[(d["source"] == "upward") & (d["n"] <= min(nmax, 64))]
    else:
        d = d[d["source"] == "ensemble"]
    done = set()
    if TW_CSV.exists():
        t = load_tw()
        if retry:
            d = d[d["instance_name"].isin(t.loc[~t["exact"].astype(bool), "instance_name"])]
        else:
            done = set(t["instance_name"])
    d = d[~d["instance_name"].isin(done)]
    # small first: results arrive early and a stopped run loses little
    d = d.sort_values(["n", "instance_name"])
    if limit:
        d = d.head(limit)
    print(f"{len(d)} instances to do ({'retry' if retry else 'new'})", flush=True)
    new_file = not TW_CSV.exists()
    violations = 0
    with open(TW_CSV, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=TW_FIELDS)
        if new_file:
            w.writeheader()
        rows = [(r._asdict() if hasattr(r, "_asdict") else r, deadline, budget)
                for r in d[["instance_name", "source", "generator", "n", "m", "param", "index",
                            "optimum"]].to_dict("records")]
        started = time.monotonic()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_tw_job, r) for r in rows]
            for i, f in enumerate(as_completed(futures), 1):
                out = f.result()
                w.writerow({k: out[k] for k in TW_FIELDS})
                fh.flush()
                if out["tw_lo"] > out["pw"] or not out["order_ok"]:
                    violations += 1
                    print(f"VIOLATION {out}", flush=True)
                if i % 500 == 0:
                    print(f"{i}/{len(rows)} {time.monotonic() - started:.0f}s", flush=True)
    print(f"done; violations: {violations}", flush=True)
    if violations:
        sys.exit(2)


# ----------------------------------------------------------------------------
# the unpatched Karonski-Szymkowiak matrix (new, small compute)
# ----------------------------------------------------------------------------
#
# `benchmarks.generator.generate_random_instance` draws R(n, m, p) and then
# gives every empty row one random 1 (and every empty column one, which adds
# no edge). So the certified instance is R(n, m, p) *plus* patches, and its
# MOSP graph contains the graph of the raw matrix. At the p of the
# Karonski-Szymkowiak threshold a large share of rows is empty, so the raw
# matrix is the model their theorem is about. It regenerates exactly from the
# same seed (the first draw of the same RandomState) and its pathwidth is
# computed here with the exact graph solver in `pathwidth_solver/`. Never more
# than the certified pw (subgraph), which is checked.

KSS_CSV = ENS / "kss_raw_pathwidth.csv"
KSS_FIELDS = ["instance_name", "n", "m", "param", "pw_patched", "pw_raw", "patched_rows",
              "raw_col_max", "raw_ones", "layout", "proved", "seconds"]


def p_star(k: int, n, m):
    """Karonski-Szymkowiak: p_k* = m^(-1/(k+1)) n^(-1) (Thm 1 for k = 3, the §5
    conjecture for k >= 4), on the branch alpha <= (t_k-2)(k+1)/((t_k-1)(k-1)),
    which holds for every (n, m) used here (alpha <= 1.31)."""
    return np.power(m, -1.0 / (k + 1)) / n


def alpha_cap(k: int) -> float:
    t = (5 * 3 ** (k - 1) - 1) // 2
    return (t - 2) * (k + 1) / ((t - 1) * (k - 1))


def _kss_job(row):
    sys.path.insert(0, str(ROOT / "pathwidth_solver"))
    import networkx as nx
    from pathwidth import solve
    from learning.ensemble import Cell, cell_seed

    started = time.monotonic()
    cell = Cell("bernoulli", int(row["n"]), int(row["m"]), float(row["param"]))
    rng = np.random.RandomState(cell_seed(cell, int(row["index"])))
    raw = (rng.random((cell.n, cell.m)) < cell.param).astype(np.int8)
    G = nx.Graph()
    G.add_nodes_from(range(cell.n))
    for j in range(cell.m):
        members = np.flatnonzero(raw[:, j]).tolist()
        G.add_edges_from((a, b) for i, a in enumerate(members) for b in members[i + 1:])
    sol = solve(G)
    return {"instance_name": row["instance_name"], "n": cell.n, "m": cell.m, "param": cell.param,
            "pw_patched": int(row["optimum"]) - 1, "pw_raw": int(sol.width),
            "patched_rows": int((raw.sum(axis=1) == 0).sum()),
            "raw_col_max": int(raw.sum(axis=0).max()), "raw_ones": int(raw.sum()),
            "layout": " ".join(map(str, sol.order)), "proved": bool(sol.proved),
            "seconds": round(time.monotonic() - started, 3)}


def run_kss(workers: int, xmax: float) -> None:
    d = load(upward=True)
    d = d[d["generator"] == "bernoulli"].copy()
    d = d[d["param"] / p_star(3, d["n"], d["m"]) <= xmax]
    if KSS_CSV.exists():
        d = d[~d["instance_name"].isin(pd.read_csv(KSS_CSV)["instance_name"])]
    print(f"{len(d)} raw matrices to do", flush=True)
    new_file = not KSS_CSV.exists()
    bad = 0
    with open(KSS_CSV, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=KSS_FIELDS)
        if new_file:
            w.writeheader()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_kss_job, r) for r in
                       d[["instance_name", "n", "m", "param", "index", "optimum"]].to_dict("records")]
            for f in as_completed(futures):
                out = f.result()
                w.writerow(out)
                fh.flush()
                if out["pw_raw"] > out["pw_patched"] or not out["proved"]:
                    bad += 1
                    print(f"CHECK {out}", flush=True)
    print(f"done; raw > patched or unproved: {bad}", flush=True)
    if bad:
        sys.exit(2)


# ----------------------------------------------------------------------------
# analysis (stored results only)
# ----------------------------------------------------------------------------

BLUES = None


def _ncolor(n, ns):
    import matplotlib.cm as cm
    ns = sorted(ns)
    t = 0.35 + 0.65 * (ns.index(n) / max(1, len(ns) - 1))
    return cm.Blues(t)


def _wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def _md(df: pd.DataFrame, fmt: str = ".3g") -> str:
    return df.to_markdown(index=False, floatfmt=fmt)


def _binom_cdf(k, n, p):
    from scipy.stats import binom
    return binom.cdf(k, n, p)


def ks_tables(d: pd.DataFrame, raw: pd.DataFrame | None):
    """Per Bernoulli cell, P(pw <= k - 1) against x = p / p_k*, k = 3, 4, 5."""
    b = d[d["generator"] == "bernoulli"].copy()
    if raw is not None:
        b = b.merge(raw[["instance_name", "pw_raw", "raw_col_max", "patched_rows"]],
                    on="instance_name", how="left")
    rows = []
    for (n, m, p), g in b.groupby(["n", "m", "param"]):
        for k in (3, 4, 5):
            x = p / p_star(k, n, m)
            r = {"k": k, "n": n, "ratio": m // n, "p": p, "x": x, "N": len(g),
                 "P_patched": (g["pw"] <= k - 1).mean(),
                 "P_col_exact": _binom_cdf(k, n, p) ** m,
                 "P_limit": math.exp(-x ** (k + 1) / math.factorial(k + 1))}
            if raw is not None and g["pw_raw"].notna().all():
                yes = int((g["pw_raw"] <= k - 1).sum())
                lo, hi = _wilson(yes, len(g))
                colok = g["raw_col_max"] <= k
                r.update({"P_raw": yes / len(g), "P_raw_lo": lo, "P_raw_hi": hi,
                          "P_raw_colok": colok.mean(),
                          "P_raw_given_colok": ((g["pw_raw"] <= k - 1) & colok).sum() / max(1, colok.sum()),
                          "patched_row_frac": g["patched_rows"].mean() / n})
            rows.append(r)
    return pd.DataFrame(rows)


def _interp_logx(g: pd.DataFrame, col: str, xs):
    g = g.dropna(subset=[col]).sort_values("x")
    lx = np.log(g["x"].to_numpy())
    y = g[col].to_numpy()
    out = []
    for x in xs:
        if len(g) < 2 or not (lx[0] <= math.log(x) <= lx[-1]):
            out.append(np.nan)
        else:
            out.append(float(np.interp(math.log(x), lx, y)))
    return out


def _x50(g: pd.DataFrame, col: str):
    g = g.dropna(subset=[col]).sort_values("x")
    x, y = g["x"].to_numpy(), g[col].to_numpy()
    for i in range(len(x) - 1):
        if y[i] >= 0.5 >= y[i + 1] and y[i] != y[i + 1]:
            t = (y[i] - 0.5) / (y[i] - y[i + 1])
            return float(np.exp(np.log(x[i]) + t * (np.log(x[i + 1]) - np.log(x[i]))))
    return np.nan


def _x50_col(k: int, n: int, m: int) -> float:
    """x at which P(no product has >= k + 1 customers) = (P(Bin(n, p) <= k))^m = 1/2."""
    from scipy.optimize import brentq
    ps = p_star(k, n, m)
    return float(brentq(lambda x: _binom_cdf(k, n, x * ps) ** m - 0.5, 0.05, min(50.0, 0.999 / ps)))


def fig_ks(ks: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    have_raw = "P_raw" in ks
    fig, axes = plt.subplots(2, 4, figsize=(18, 8.6), constrained_layout=True)
    ns = sorted(ks["n"].unique())
    xx = np.geomspace(0.2, 20, 200)
    for row, col, what in ((0, "P_raw", "raw R(n, m, p), new exact pw"),
                           (1, "P_patched", "as generated (empty rows patched), certified pw")):
        if col not in ks:
            continue
        for ax, k in zip(axes[row, :3], (3, 4, 5)):
            g = ks[(ks["k"] == k)]
            for n in ns:
                for ratio, mk in ((1, "o"), (2, "s")):
                    h = g[(g["n"] == n) & (g["ratio"] == ratio)].dropna(subset=[col]).sort_values("x")
                    if h.empty:
                        continue
                    ax.plot(h["x"], h[col], marker=mk, ms=4, lw=1.4, ls="-" if ratio == 1 else "--",
                            color=_ncolor(n, ns), label=f"n={n}" if ratio == 1 else None)
            ax.plot(xx, np.exp(-xx ** (k + 1) / math.factorial(k + 1)), color="#d62728", lw=2.2,
                    ls=":", label=r"limit $e^{-x^{k+1}/(k+1)!}$ [derived]")
            ax.set_xscale("log")
            ax.set_xlim(0.3, 8)
            ax.set_ylim(-0.02, 1.02)
            ax.set_xlabel(rf"$x = p / p_{k}^*$,  $p_{k}^* = m^{{-1/{k + 1}}} n^{{-1}}$")
            ax.set_ylabel(f"P(pw ≤ {k - 1})")
            ax.set_title(f"k = {k} [{'Thm 1' if k == 3 else '§5 conjecture'}]: {what}", fontsize=9)
            ax.grid(alpha=0.25, which="both")
        axes[row, 0].legend(fontsize=7, loc="lower left")
    if have_raw:
        ax = axes[0, 3]
        g = ks[ks["k"] == 3]
        for n in ns:
            for ratio, mk in ((1, "o"), (2, "s")):
                h = g[(g["n"] == n) & (g["ratio"] == ratio)].dropna(subset=["P_raw"])
                h = h[h["P_raw_colok"] >= 0.05].sort_values("x")
                if h.empty:
                    continue
                ax.plot(h["x"], h["P_raw_given_colok"], marker=mk, ms=4, lw=1.4,
                        ls="-" if ratio == 1 else "--", color=_ncolor(n, ns))
        ax.set_xscale("log")
        ax.set_xlim(0.3, 8)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel(r"$x = p / p_3^*$")
        ax.set_title("raw: P(pw ≤ 2 | every product has ≤ 3 customers)", fontsize=9)
        ax.grid(alpha=0.25, which="both")
        ax = axes[1, 3]
        for k, mk in ((3, "o"), (4, "s"), (5, "^")):
            h = ks[ks["k"] == k].dropna(subset=["P_raw"])
            ax.scatter(h["P_col_exact"], h["P_raw"], marker=mk, s=14, alpha=0.7, label=f"k = {k}")
        ax.plot([0, 1], [0, 1], color="#7f7f7f", lw=1)
        ax.set_xlabel(r"$P(\mathrm{Bin}(n,p) \leq k)^m$ (exact)")
        ax.set_ylabel(f"P(pw ≤ k − 1), raw")
        ax.set_title("raw: the one-product clique event against the whole", fontsize=9)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    fig.suptitle("Karoński–Szymkowiak thresholds against exact pathwidth (solid m = n, dashed m = 2n)")
    fig.savefig(path, dpi=120)
    plt.close(fig)


def sd_tables(d: pd.DataFrame, nboot: int = 400, seed: int = 0):
    """Per cell: sd of pw with a bootstrap standard error."""
    rng = np.random.default_rng(seed)
    rows = []
    for (gen, ratio, param, n), g in d.groupby(["generator", "ratio", "param", "n"]):
        v = g["pw"].to_numpy()
        boots = [rng.choice(v, len(v)).std(ddof=1) for _ in range(nboot)]
        ones = g["n_ones"].to_numpy(dtype=float)
        if ones.std() > 0 and v.std() > 0:
            beta = np.polyfit(ones, v, 1)
            resid_sd = float((v - np.polyval(beta, ones)).std(ddof=2))
        else:
            resid_sd = float(v.std(ddof=1))
        rows.append({"sd_given_ones": resid_sd, "generator": gen, "ratio": int(ratio), "param": param, "n": n, "N": len(v),
                     "mean_pw": v.mean(), "sd": v.std(ddof=1), "sd_se": float(np.std(boots)),
                     "col_mean": g["col_mean"].mean(), "deg_mean": g["g_deg_mean"].mean()})
    return pd.DataFrame(rows)


def _fit_models(n, y, se):
    """Weighted least squares of y against 1, sqrt(n), log(n); and a power law."""
    n, y, se = map(lambda a: np.asarray(a, dtype=float), (n, y, se))
    keep = y > 0
    n, y, se = n[keep], y[keep], np.maximum(se[keep], 0.02)
    w = 1 / se ** 2
    out = {}
    for name, X in (("const", np.ones((len(n), 1))),
                    ("a+b*sqrt(n)", np.column_stack([np.ones(len(n)), np.sqrt(n)])),
                    ("a+b*log(n)", np.column_stack([np.ones(len(n)), np.log(n)])),
                    ("a+b*n", np.column_stack([np.ones(len(n)), n]))):
        W = np.sqrt(w)[:, None]
        beta, *_ = np.linalg.lstsq(X * W, y * W[:, 0], rcond=None)
        chi2 = float((w * (y - X @ beta) ** 2).sum())
        out[name] = {"beta": beta, "chi2": chi2, "dof": len(n) - X.shape[1]}
    # power law sd = a n^b, in logs, with the delta-method error
    ly, lse = np.log(y), se / y
    X = np.column_stack([np.ones(len(n)), np.log(n)])
    W = 1 / lse ** 2
    cov = np.linalg.inv(X.T @ (X * W[:, None]))
    beta = cov @ X.T @ (W * ly)
    chi2 = float((W * (ly - X @ beta) ** 2).sum())
    dof = len(n) - 2
    scale = max(1.0, chi2 / max(dof, 1))
    out["power"] = {"b": float(beta[1]), "b_se": float(math.sqrt(cov[1, 1] * scale)),
                    "chi2": chi2, "dof": dof}
    return out


def sd_scaling(sd: pd.DataFrame, nmin: int = 15):
    rows = []
    # (i) fixed generator at fixed d: fixed density in every sense
    for (ratio, dd), g in sd[sd["generator"] == "fixed"].groupby(["ratio", "param"]):
        g = g[(g["n"] >= nmin) & (g["n"] >= dd)].sort_values("n")
        if len(g) < 4:
            continue
        f = _fit_models(g["n"], g["sd"], g["sd_se"])
        rows.append({"series": f"fixed d={dd:g}, m={ratio}n", "n_range": f"{g.n.min()}-{g.n.max()}",
                     "sd_first": g["sd"].iloc[0], "sd_last": g["sd"].iloc[-1],
                     "power_b": f["power"]["b"], "power_b_se": f["power"]["b_se"],
                     **{f"chi2/dof {k}": f[k]["chi2"] / max(f[k]["dof"], 1)
                        for k in ("const", "a+b*sqrt(n)", "a+b*log(n)")}})
    # (ii) the peak sd over the grid at each n, per generator and ratio
    for (gen, ratio), g in sd.groupby(["generator", "ratio"]):
        pk = g.loc[g.groupby("n")["sd"].idxmax()].sort_values("n")
        pk = pk[pk["n"] >= nmin]
        f = _fit_models(pk["n"], pk["sd"], pk["sd_se"])
        rows.append({"series": f"PEAK {gen}, m={ratio}n", "n_range": f"{pk.n.min()}-{pk.n.max()}",
                     "sd_first": pk["sd"].iloc[0], "sd_last": pk["sd"].iloc[-1],
                     "power_b": f["power"]["b"], "power_b_se": f["power"]["b_se"],
                     **{f"chi2/dof {k}": f[k]["chi2"] / max(f[k]["dof"], 1)
                        for k in ("const", "a+b*sqrt(n)", "a+b*log(n)")}})
    return pd.DataFrame(rows)


def fig_sd(sd: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3), constrained_layout=True)
    for ax, ratio in zip(axes[:2], (1, 2)):
        g = sd[(sd["generator"] == "fixed") & (sd["ratio"] == ratio)]
        ds = sorted(g["param"].unique())
        for i, dd in enumerate(ds):
            h = g[(g["param"] == dd) & (g["n"] >= dd)].sort_values("n")
            ax.errorbar(h["n"], h["sd"], yerr=h["sd_se"], marker="o", ms=4, lw=1.5, capsize=2,
                        color=cm.Greens(0.35 + 0.65 * i / (len(ds) - 1)), label=f"d={dd:g}")
        nn = np.linspace(10, 75, 100)
        ax.plot(nn, 0.15 * np.sqrt(nn), color="#7f7f7f", ls=":", lw=1.5, label=r"$0.15\sqrt{n}$ (guide)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_ylim(0.25, 2.0)
        ax.set_xlabel("n (customers = vertices)")
        ax.set_ylabel("sd of pw within a cell")
        ax.set_title(f"fixed generator, m = {ratio}n, fixed d")
        ax.grid(alpha=0.25, which="both")
        ax.legend(fontsize=7, ncol=2)
    ax = axes[2]
    for (gen, ratio), mk in ((("fixed", 1), "o"), (("fixed", 2), "s"), (("bernoulli", 1), "^"),
                              (("bernoulli", 2), "v")):
        g = sd[(sd["generator"] == gen) & (sd["ratio"] == ratio)]
        pk = g.loc[g.groupby("n")["sd"].idxmax()].sort_values("n")
        ax.errorbar(pk["n"], pk["sd"], yerr=pk["sd_se"], marker=mk, ms=5, lw=1.5, capsize=2,
                    color="#1f77b4" if gen == "fixed" else "#ff7f0e",
                    ls="-" if ratio == 1 else "--", label=f"{gen}, m={ratio}n")
    ax.set_xlabel("n")
    ax.set_ylabel("largest cell sd of pw over the grid")
    ax.set_title("peak sd at each n (max over the density grid)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(path, dpi=130)
    plt.close(fig)


# Erdos-Renyi bounds on pw/n from reports/random_graph_pathwidth_survey.md §7(a), by c.
ER_BOUNDS = {2: (0.0, 0.162), 3: (0.009, 0.260), 4: (0.061, 0.347), 5: (0.118, 0.433),
             6: (0.171, 0.520), 8: (0.263, 0.693), 10: (0.337, 0.760), 12: (0.397, 0.786),
             16: (0.488, 0.823), 20: (0.554, 0.848)}
GD_TW = {2: [(50, 0.072)], 4: [(25, 0.252), (50, 0.216)], 6: [(50, 0.346)],
         8: [(25, 0.472), (50, 0.407)], 12: [(25, 0.604), (50, 0.552)], 16: [(25, 0.720), (50, 0.674)]}


def collapse_tables(sd: pd.DataFrame, cs=(2, 3, 4, 6, 8, 12, 16)):
    """pw/n interpolated (in log degree) at fixed mean degree c, per series and n."""
    rows = []
    for (gen, ratio, n), g in sd.groupby(["generator", "ratio", "n"]):
        g = g.sort_values("deg_mean")
        ld = np.log(g["deg_mean"].to_numpy())
        y = (g["mean_pw"] / n).to_numpy()
        for c in cs:
            if ld[0] <= math.log(c) <= ld[-1]:
                rows.append({"generator": gen, "ratio": int(ratio), "n": n, "c": c,
                             "pw_over_n": float(np.interp(math.log(c), ld, y))})
    t = pd.DataFrame(rows)
    fits = []
    for (gen, ratio, c), g in t.groupby(["generator", "ratio", "c"]):
        g = g[g["n"] >= 20].sort_values("n")
        if len(g) < 4:
            continue
        X = np.column_stack([np.ones(len(g)), 1 / g["n"].to_numpy()])
        beta, res, *_ = np.linalg.lstsq(X, g["pw_over_n"].to_numpy(), rcond=None)
        r = g["pw_over_n"].to_numpy() - X @ beta
        s2 = (r ** 2).sum() / max(1, len(g) - 2)
        cov = s2 * np.linalg.inv(X.T @ X)
        lo, hi = ER_BOUNDS.get(c, (np.nan, np.nan))
        fits.append({"generator": gen, "ratio": int(ratio), "c": c, "n_range": f"{g.n.min()}-{g.n.max()}",
                     "pw/n at smallest n": g["pw_over_n"].iloc[0], "pw/n at largest n": g["pw_over_n"].iloc[-1],
                     "a (pw/n = a + b/n)": beta[0], "a_se": math.sqrt(cov[0, 0]), "b": beta[1],
                     "ER LB": lo, "ER UB": hi})
    return t, pd.DataFrame(fits)


def fig_collapse(sd: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ns = sorted(sd["n"].unique())
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    for i, gen in enumerate(("bernoulli", "fixed")):
        for j, (xcol, xlabel) in enumerate((("deg_mean", "mean degree of the MOSP graph (g_deg_mean)"),
                                            ("col_mean", "realised customers per product (col_mean)"))):
            ax = axes[i, j]
            for n in ns:
                for ratio, mk, ls in ((1, "o", "-"), (2, "s", "--")):
                    h = sd[(sd["generator"] == gen) & (sd["n"] == n) & (sd["ratio"] == ratio)].sort_values(xcol)
                    if h.empty:
                        continue
                    ax.plot(h[xcol], h["mean_pw"] / n, marker=mk, ms=3.5, lw=1.3, ls=ls,
                            color=_ncolor(n, ns), label=f"n={n}" if ratio == 1 else None)
            if xcol == "deg_mean":
                cs = sorted(ER_BOUNDS)
                ax.fill_between(cs, [ER_BOUNDS[c][0] for c in cs], [ER_BOUNDS[c][1] for c in cs],
                                color="#bbbbbb", alpha=0.35, label="G(n, c/n): whp bounds on pw/n")
                for c, pts in GD_TW.items():
                    for nn, v in pts:
                        ax.plot([c], [v], marker="x", color="#d62728", ms=7,
                                label="G(n, c/n) exact tw/n, Gogate–Dechter" if (c, nn) == (2, 50) else None)
            ax.set_xscale("log")
            ax.set_xlabel(xlabel)
            ax.set_ylabel("mean pw / n")
            ax.set_title(f"{gen} generator (circles m = n, squares m = 2n)")
            ax.grid(alpha=0.25, which="both")
            if i == 0 and j == 0:
                ax.legend(fontsize=7, ncol=2)
    fig.savefig(path, dpi=130)
    plt.close(fig)


BANDS = [0, 1.5, 2, 2.5, 3, 4, 6, 10, 100]


def gap_tables(d: pd.DataFrame, tw: pd.DataFrame):
    j = d.merge(tw[["instance_name", "tw_lo", "tw_hi", "exact"]], on="instance_name", how="inner")
    j["exact"] = j["exact"].astype(bool)
    viol = j[j["tw_lo"] > j["pw"]]
    # cells in which every instance has exact treewidth; per-cell statistics use only these,
    # since censoring is not random (it falls on the hard, gap-prone cells)
    full = j.groupby(["generator", "ratio", "param", "n"])["exact"].transform("all")
    j["cell_exact"] = full
    e = j[j["exact"]].copy()
    e["gap"] = e["pw"] - e["tw_lo"]
    e["band"] = pd.cut(e["col_mean"], BANDS)
    e["gap_mf"] = e["pw"] - e["tw_min_fill"]
    by_n = e.groupby("n").agg(N=("gap", "size"), mean_gap=("gap", "mean"),
                              P_gt0=("gap", lambda s: (s > 0).mean()),
                              P_ge2=("gap", lambda s: (s >= 2).mean()),
                              max_gap=("gap", "max"),
                              P_gt0_minfill=("gap_mf", lambda s: (s > 0).mean())).reset_index()
    j["gt0_lo"] = j["pw"] > j["tw_hi"]       # certain gap, censored rows included
    j["gt0_hi"] = j["pw"] > j["tw_lo"]       # possible gap
    cens = j.groupby("n").agg(not_exact=("exact", lambda s: int((~s).sum())),
                              P_gt0_all_lo=("gt0_lo", "mean"), P_gt0_all_hi=("gt0_hi", "mean"),
                              max_gap_certain=("tw_hi", lambda s: int((j.loc[s.index, "pw"] - s).max()))
                              ).reset_index()
    by_n = by_n.merge(cens, on="n")
    band = (e.pivot_table(index="band", columns="n", values="gap", aggfunc=lambda s: (s > 0).mean(),
                          observed=False).round(3).reset_index())
    band["band"] = band["band"].astype(str)
    counts = e.groupby("band", observed=False)["gap"].agg(["size", "mean", "max"]).reset_index()
    counts["band"] = counts["band"].astype(str)
    dist = e.pivot_table(index="n", columns="gap", values="instance_name", aggfunc="count",
                         fill_value=0).reset_index()
    by_gen = e.groupby(["generator", "ratio", "n"]).agg(P_gt0=("gap", lambda s: (s > 0).mean()),
                                                        mean_gap=("gap", "mean")).reset_index()
    peak = []
    for n, g in e[e["cell_exact"]].groupby("n"):
        cell = g.groupby(["generator", "ratio", "param"]).agg(P=("gap", lambda s: (s > 0).mean()),
                                                              mean_gap=("gap", "mean"),
                                                              col_mean=("col_mean", "mean"),
                                                              N=("gap", "size"))
        top = cell.sort_values("P", ascending=False).iloc[0]
        idx = cell["P"].idxmax()
        peak.append({"n": n, "cell": f"{idx[0]} m={int(idx[1])}n param={idx[2]:g}",
                     "col_mean": top["col_mean"], "P(pw>tw)": top["P"], "mean gap": top["mean_gap"],
                     "N": int(top["N"])})
    top = e.sort_values(["gap", "n"], ascending=False).head(10)[
        ["instance_name", "n", "col_mean", "g_deg_mean", "pw", "tw_lo"]]
    return {"joined": j, "exact": e, "violations": viol, "by_n": by_n, "band": band, "band_counts": counts,
            "dist": dist, "by_gen": by_gen, "peak": pd.DataFrame(peak), "top": top}


def fig_gap(e: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ns = sorted(e["n"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), constrained_layout=True)
    cell = e.groupby(["generator", "ratio", "param", "n"]).agg(
        P=("gap", lambda s: (s > 0).mean()), mean_gap=("gap", "mean"),
        col_mean=("col_mean", "mean")).reset_index()
    for ax, col, lab in ((axes[0], "P", "P(pw > tw) in the cell"), (axes[1], "mean_gap", "mean pw − tw in the cell")):
        for n in ns:
            for gen, mk in (("fixed", "o"), ("bernoulli", "^")):
                h = cell[(cell["n"] == n) & (cell["generator"] == gen)].sort_values("col_mean")
                ax.scatter(h["col_mean"], h[col], marker=mk, s=16, color=_ncolor(n, ns),
                           label=f"n={n}" if gen == "fixed" else None, edgecolor="none")
        ax.set_xscale("log")
        ax.set_xlabel("realised customers per product (col_mean)")
        ax.set_ylabel(lab)
        ax.grid(alpha=0.25, which="both")
    axes[0].legend(fontsize=7, title="circles fixed, triangles Bernoulli", title_fontsize=7)
    fig.suptitle("Exact pathwidth − exact treewidth on random intersection graphs, by cell "
                 "(cells with every treewidth exact)")
    fig.savefig(path, dpi=130)
    plt.close(fig)


def analyse() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 200)
    d = load(upward=True)
    print(f"# rig_pathwidth: {len(d)} certified, model-matched instances "
          f"({(d.source == 'ensemble').sum()} at n <= 40, {(d.source == 'upward').sum()} at 50-75)\n")
    print("alpha caps of the KS branch (need alpha <= cap):",
          {k: round(alpha_cap(k), 3) for k in (3, 4, 5)},
          " max alpha here:", round(float((np.log(d.m) / np.log(d.n)).max()), 3), "\n")

    # 1. Karonski-Szymkowiak
    raw = pd.read_csv(KSS_CSV) if KSS_CSV.exists() else None
    if raw is not None:
        bad = raw[raw["pw_raw"] > raw["pw_patched"]]
        print(f"## 1. KS thresholds; raw matrices: {len(raw)}, raw pw > certified pw on {len(bad)} "
              f"(must be 0), unproved {int((~raw['proved'].astype(bool)).sum())}\n")
    ks = ks_tables(d, raw)
    col = "P_raw" if raw is not None else "P_patched"
    xs = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0)
    for k in (3, 4, 5):
        rows = []
        for (n, ratio), g in ks[ks["k"] == k].groupby(["n", "ratio"]):
            vals = _interp_logx(g, col, xs)
            pat = _interp_logx(g, "P_patched", xs)
            rows.append({"n": n, "m/n": ratio, **{f"x={x:g}": v for x, v in zip(xs, vals)},
                         "x50": _x50(g, col), "x50 one-product event": _x50_col(k, n, ratio * n),
                         "x50 patched": _x50(g, "P_patched"),
                         **({"P(pw<=k-1 | colmax<=k) at x=2": _interp_logx(g, "P_raw_given_colok", [2.0])[0]}
                            if raw is not None else {})})
        lim = {f"x={x:g}": math.exp(-x ** (k + 1) / math.factorial(k + 1)) for x in xs}
        for big in (200, 1000, 10_000):
            rows.append({"n": f"{big} (one-product event only)", "m/n": 1,
                         "x50 one-product event": _x50_col(k, big, big)})
        rows.append({"n": "limit", "m/n": "", **lim,
                     "x50": (math.log(2) * math.factorial(k + 1)) ** (1 / (k + 1))})
        print(f"### k = {k}: P(pw <= {k - 1}) interpolated at x = p/p{k}* ({col})\n")
        print(_md(pd.DataFrame(rows), ".3f"), "\n")
    print("### per cell, k = 3, x <= 6\n")
    print(_md(ks[(ks.k == 3) & (ks.x <= 6)].drop(columns=["k"]).sort_values(["ratio", "n", "p"]), ".3f"), "\n")
    fig_ks(ks, FIG / "rig_ks_threshold.png")

    # 2. concentration
    sd = sd_tables(d)
    print("## 2. sd of pw against n (fits on n >= 15; chi2/dof of weighted fits; power-law b with se)\n")
    print(_md(sd_scaling(sd), ".3f"), "\n")
    peak = sd.loc[sd.groupby(["generator", "ratio", "n"])["sd"].idxmax()]
    print(_md(peak[["generator", "ratio", "n", "param", "N", "mean_pw", "sd", "sd_se", "sd_given_ones", "col_mean"]], ".3f"), "\n")
    bern = sd[sd["generator"] == "bernoulli"].copy()
    bern["n_ones_share"] = 1 - (bern["sd_given_ones"] / bern["sd"].where(bern["sd"] > 0)) ** 2
    print("Bernoulli: share of the within-cell variance of pw explained by the number of ones, median by n:\n")
    print(_md(bern[bern["sd"] > 0.3].groupby("n")["n_ones_share"].median().reset_index(), ".3f"), "\n")
    fig_sd(sd, FIG / "rig_sd.png")

    # 3. collapse
    t, fits = collapse_tables(sd)
    print("## 3. pw/n at fixed mean degree c (log-interpolated), by n\n")
    print(_md(t.pivot_table(index=["generator", "ratio", "c"], columns="n", values="pw_over_n").reset_index(), ".3f"), "\n")
    print(_md(fits, ".3f"), "\n")
    fig_collapse(sd, FIG / "rig_pw_over_n.png")

    # 4. pw - tw
    if TW_CSV.exists():
        tw = load_tw()
        g = gap_tables(d, tw)
        print(f"## 4. pw - tw: {len(g['joined'])} instances with treewidth, {len(g['exact'])} exact, "
              f"violations (tw > pw): {len(g['violations'])}\n")
        for key in ("by_n", "dist", "band", "band_counts", "peak", "top"):
            print(f"### {key}\n")
            print(_md(g[key], ".3f"), "\n")
        print(_md(g["by_gen"].pivot_table(index=["generator", "ratio"], columns="n", values="P_gt0").reset_index(), ".3f"), "\n")
        fig_gap(g["exact"][g["exact"]["cell_exact"]], FIG / "rig_pw_minus_tw.png")
        cells = g["joined"].groupby(["generator", "ratio", "param", "n"])["exact"].all()
        print("cells with every instance exact, by n:", cells.groupby("n").agg(["sum", "size"]).to_dict("index"), "\n")
        series = []
        jj = g["joined"]
        for (gen, ratio, par), h in jj.groupby(["generator", "ratio", "param"]):
            t = h.groupby("n").agg(lo=("gt0_lo", "mean"), hi=("gt0_hi", "mean"))
            series.append({"series": f"{gen} m={int(ratio)}n param={par:g}",
                           **{f"n={n}": (f"{r.lo:.2f}" if r.lo == r.hi else f"[{r.lo:.2f}, {r.hi:.2f}]")
                              for n, r in t.iterrows()}})
        print("### P(pw > tw) per series (interval where treewidth is censored)\n")
        print(pd.DataFrame(series).to_markdown(index=False), "\n")


# ----------------------------------------------------------------------------
# command line
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    t = sub.add_parser("treewidth", help="compute exact treewidth (resumable)")
    t.add_argument("--workers", type=int, default=8)
    t.add_argument("--upward", action="store_true", help="the 50-60 campaign cells instead of n <= 40")
    t.add_argument("--retry", action="store_true", help="re-run the censored rows only")
    t.add_argument("--deadline", type=float, default=60.0)
    t.add_argument("--budget", type=int, default=5_000_000)
    t.add_argument("--limit", type=int, default=None)
    t.add_argument("--nmax", type=int, default=64, help="with --upward: largest n (the decision search holds 64)")
    k = sub.add_parser("kss-raw", help="pathwidth of the unpatched Bernoulli matrices near the threshold")
    k.add_argument("--workers", type=int, default=4)
    k.add_argument("--xmax", type=float, default=8.0, help="cells with p / p3* up to this")
    sub.add_parser("analyse", help="tables and figures from stored results")
    args = ap.parse_args()
    if args.cmd == "treewidth":
        if args.workers > 8:
            ap.error("at most 8 workers on this machine")
        run_treewidth(args.workers, args.upward, args.retry, args.deadline, args.budget, args.limit, args.nmax)
    elif args.cmd == "kss-raw":
        if args.workers > 8:
            ap.error("at most 8 workers on this machine")
        run_kss(args.workers, args.xmax)
    else:
        analyse()


if __name__ == "__main__":
    main()
