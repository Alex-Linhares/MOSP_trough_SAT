"""Why the ridge is where it is: the hardness peak as a condition on one graph parameter.

Question (`reports/ml_nature_plan_2.md` §2.9, loop0003 item 11). §11 put the
hardness ridge -- the density at which the nodes to refute `optimum - 1` peak
at fixed `n` -- at three customers per product when `m = n` and two when
`m = 2n`; §16 found it at five to six when `m = n / 2`. In which coordinate is
that one number? The plan's hypothesis was the MOSP-graph mean degree
("8-9 at both ratios"). This module (a) derives, for both generators, the
expected degree, edge probability, giant-component branching factor and the
incidence-graph excess of `G(n, m, p)` in `col_mean` coordinates, checks the
derivations against the measured graphs, (b) locates every series' peak by
parabolic interpolation between cells with bootstrap intervals, (c) tests
each candidate parameter for constancy across `m / n`, (d) calibrates every
hypothesis on the `m = n` ridge and predicts the `m = n / 2`, `m = n / 4`
and `m = n / 8` ridges from it, and (e) runs the deciding cells the campaign
lacked: `m = n / 4` at n in {50, 60, 75} and `m = n / 8` at n = 75, where the
degree and excess hypotheses are furthest apart.

Nothing here is a bound or a solver change; nothing is written to
`solutions/`. Generated instances are certified with `solve_mosp_exact` into
`learning/data/ensemble/solutions/` like the rest of the campaign, and their
rows go to `learning/data/ensemble/results_ratio.csv` (with a manifest), kept
apart from `results.csv` and `results_upward.csv` so §10-§16 regenerate
unchanged.

Usage:
    python -m learning.ridge_theory --stage run --workers 16    # the m = n/4 and n/8 cells (~10 min)
    python -m learning.ridge_theory --stage tables              # reports/ridge_theory_tables.md + figure, ~30 s
    python -m pytest tests/test_ridge_theory.py -q
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.ensemble import (ENSEMBLE_DIR, RESULTS_CSV, RESULTS_UPWARD_CSV, Cell, load_results,
                               run, write_manifest)
from learning.upward import apply_finish, prepare

RESULTS_RATIO_CSV = ENSEMBLE_DIR / "results_ratio.csv"
MANIFEST_RATIO_CSV = ENSEMBLE_DIR / "manifest_ratio.csv"
CLIQUES_CSV = ENSEMBLE_DIR / "ridge_clique_excess.csv"
TABLES = Path("reports/ridge_theory_tables.md")
FIGURE = Path("reports/figures/ridge_theory.png")

RATIO_N = (50, 60, 75)
RATIO_D = (3, 4, 5, 6, 7, 8, 9, 10, 12)
RATIO_P = (0.05, 0.075, 0.1, 0.125, 0.15, 0.2)
EIGHTH_N = 75
EIGHTH_D = (4, 6, 8, 10, 12, 14, 16, 18, 20, 24)
PER_CELL = 50
SEED = 0


def ratio_cells(sizes=RATIO_N, ds=RATIO_D, ps=RATIO_P) -> list[Cell]:
    """m = n // 4 at each size, fixed d and Bernoulli p; plus m = n // 8 at 75, fixed only."""
    cells: list[Cell] = []
    for n in sizes:
        m = n // 4
        cells += [Cell("fixed", n, m, d) for d in ds if d <= n]
        cells += [Cell("bernoulli", n, m, p) for p in ps]
    m8 = EIGHTH_N // 8
    cells += [Cell("fixed", EIGHTH_N, m8, d) for d in EIGHTH_D if d <= EIGHTH_N]
    return cells


def run_ratio(workers: int = 16, per_cell: int = PER_CELL, csv: Path = RESULTS_RATIO_CSV) -> pd.DataFrame:
    cells = ratio_cells()
    # densest first: the sparse cells are the slow ones at m = n / 4 (they are the ridge)
    frame = run(cells, per_cell, workers=workers, csv=csv, instance_dir=None, deadline=120.0, solve_budget=600.0)
    write_manifest(frame, MANIFEST_RATIO_CSV)
    return frame



CLIQUE_CAP = 20_000


def clique_excess_of(instance, cap: int = CLIQUE_CAP) -> dict:
    """The graph-side excess: sum over the maximal cliques of the MOSP graph of
    (|K| - 1), per customer, and the number of maximal cliques over the number
    of products. Equal to the matrix excess exactly when the products are the
    maximal cliques and pairwise share at most one customer. Dense graphs have
    exponentially many maximal cliques: past `cap` of them both values are NaN."""
    import networkx as nx

    from customer_inter.customer_graph import build_customer_graph

    graph = build_customer_graph(instance)
    n = instance.n_customers
    total = 0
    count = 0
    for k in nx.find_cliques(graph):
        if len(k) >= 2:
            total += len(k) - 1
            count += 1
            if count > cap:
                return {"clique_excess": np.nan, "max_cliques_over_m": np.nan}
    return {"clique_excess": total / n, "max_cliques_over_m": count / max(instance.n_patterns, 1)}


def _clique_job(args) -> dict:
    from learning.ensemble import generate

    name, generator, n, m, param, index = args
    row = {"instance_name": name}
    row.update(clique_excess_of(generate(Cell(generator, int(n), int(m), float(param)), int(index))))
    return row


def compute_clique_excess(frame: pd.DataFrame, csv: Path = CLIQUES_CSV, min_n: int = 40,
                          max_density: float = 0.35, workers: int = 16) -> pd.DataFrame:
    """Regenerate every certified instance at n >= min_n with MOSP-graph density
    at most `max_density` (the ridges sit at 0.05-0.25; denser graphs have
    exponentially many maximal cliques) and record its graph-side excess;
    resumable, appends."""
    import multiprocessing

    done = set(pd.read_csv(csv)["instance_name"]) if csv.exists() else set()
    todo = frame[(frame["n"] >= min_n) & (frame["g_density"] <= max_density) & ~frame["instance_name"].isin(done)]
    jobs = list(zip(todo["instance_name"], todo["generator"], todo["n"], todo["m"], todo["param"], todo["index"]))
    print(f"{len(jobs)} instances to regenerate on {workers} workers", flush=True)
    rows = []
    if jobs:
        with multiprocessing.Pool(workers) as pool:
            for row in pool.imap_unordered(_clique_job, jobs, chunksize=20):
                rows.append(row)
                if len(rows) % 2000 == 0:
                    print(f"  {len(rows)} done", flush=True)
        pd.DataFrame(rows).to_csv(csv, mode="a", header=not csv.exists() or csv.stat().st_size == 0, index=False)
    return pd.read_csv(csv)


# ----------------------------------------------------------------------------
# (a) the analytics, in col_mean coordinates
# ----------------------------------------------------------------------------

RATIO_LABELS = {0.125: "n/8", 0.25: "n/4", 0.5: "n/2", 1.0: "n", 2.0: "2n"}


def ratio_label(m: float, n: float) -> str:
    """The nearest of m/n in {1/8, 1/4, 1/2, 1, 2}, as text (m = 37 at n = 75 is `n/2`)."""
    r = m / n
    key = min(RATIO_LABELS, key=lambda k: abs(np.log(r / k)))
    return RATIO_LABELS[key]


def expected_degree(n: float, m: float, c: float, generator: str) -> float:
    """Expected MOSP-graph degree of a customer when every product has `c`
    customers on average. Fixed: a product joins a given pair with probability
    c(c-1)/(n(n-1)); Bernoulli: with probability p^2, p = c/n. Products are
    independent, so a pair is adjacent unless every product misses it."""
    if generator == "fixed":
        q = c * (c - 1.0) / (n * (n - 1.0))
    else:
        q = (c / n) ** 2
    q = min(max(q, 0.0), 1.0)
    return (n - 1.0) * (1.0 - (1.0 - q) ** m)


def edge_probability(n: float, m: float, c: float, generator: str) -> float:
    return expected_degree(n, m, c, generator) / (n - 1.0)


def branching_factor(r: float, c: float, generator: str) -> float:
    """Expected new customers reached through one customer's other products:
    (products per customer) x (other customers per product). Fixed: (r c)(c - 1);
    Bernoulli (Poisson sizes, size-biasing cancels): (r c)(c) = r c^2. The
    giant component of the MOSP graph -- the incidence graph has the same
    components -- appears where this exceeds 1 (Schmidt-Pruzan & Shamir 1985,
    Karonski & Luczak 2002 for random uniform hypergraphs)."""
    return r * c * (c - 1.0) if generator == "fixed" else r * c * c


def excess(r: float, c: float) -> float:
    """(n_ones - m) / n = sum_j (|C_j| - 1) / n = r (c - 1): the clique cover's
    mass over a spanning tree of cliques per customer. At 1 the incidence graph
    has as many edges as vertices (the hypergraph's tree threshold); above it,
    `excess - 1` is the incidence graph's cyclomatic number per customer."""
    return r * (c - 1.0)


def giant_threshold_col_mean(r: float, generator: str) -> float:
    """col_mean at which the branching factor is 1."""
    if generator == "fixed":
        return 0.5 * (1.0 + np.sqrt(1.0 + 4.0 / r))
    return 1.0 / np.sqrt(r)


def tree_threshold_col_mean(r: float) -> float:
    return 1.0 + 1.0 / r


def invert_candidate(candidate: str, target: float, r: float, n: float, generator: str) -> float:
    """col_mean at which an analytic candidate takes `target` on a series with
    ratio r (m = r n): the hypothesis 'the ridge is where candidate = target'."""
    m = r * n
    if candidate == "col_mean":
        return target
    if candidate == "row_mean":                       # r c
        return target / r
    if candidate == "excess":                         # r (c - 1)
        return 1.0 + target / r
    if candidate == "branch":
        if generator == "fixed":                      # r c (c - 1)
            return 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * target / r))
        return np.sqrt(target / r)
    if candidate in ("g_deg_mean", "g_density"):      # monotone in c: bisection
        scale = (n - 1.0) if candidate == "g_deg_mean" else 1.0
        lo, hi = 1.0, float(n)
        f = lambda c: (expected_degree(n, m, c, generator) / (n - 1.0)) * scale - target
        if f(hi) < 0:
            return np.nan
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if f(mid) < 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)
    raise ValueError(candidate)


ANALYTIC = ("col_mean", "row_mean", "excess", "branch", "g_deg_mean", "g_density")
EMPIRICAL = ("clique_excess", "opt_frac", "tw_min_fill_n", "g_degeneracy_n", "bw_rcm_n", "lb_best_n",
             "g_clustering", "g_edges_n", "bip_cyc")
CANDIDATES = ANALYTIC + EMPIRICAL
CANDIDATE_TEXT = {
    "col_mean": "customers per product (col_mean)",
    "row_mean": "products per customer (row_mean = r · col_mean)",
    "excess": "excess (n_ones − m) / n = r (col_mean − 1)",
    "clique_excess": "graph excess: Σ over maximal cliques (|K| − 1) / n",
    "branch": "branching factor (giant component at 1)",
    "g_deg_mean": "MOSP-graph mean degree",
    "g_density": "MOSP-graph edge probability",
    "opt_frac": "optimum / n",
    "tw_min_fill_n": "min-fill treewidth / n",
    "g_degeneracy_n": "degeneracy / n",
    "bw_rcm_n": "RCM bandwidth / n",
    "lb_best_n": "certified lower bound / n",
    "g_clustering": "clustering coefficient",
    "g_edges_n": "edges / n",
    "bip_cyc": "incidence-graph cyclomatic number / n",
}


# ----------------------------------------------------------------------------
# (b) loading, cell medians, interpolated peaks
# ----------------------------------------------------------------------------


def derive(frame: pd.DataFrame) -> pd.DataFrame:
    """`prepare` (ratio, opt_frac, ln_/cens_ per configuration) plus the
    candidates: r_exact, ratio_label, excess, branch, bip_cyc, /n invariants."""
    out = prepare(frame)
    out = out[out["certified"].astype(bool)].copy()
    out["r_exact"] = out["m"] / out["n"]
    out["ratio_label"] = [ratio_label(m, n) for m, n in zip(out["m"], out["n"])]
    out["excess"] = (out["n_ones"] - out["m"]) / out["n"]
    out["branch"] = [branching_factor(r, c, g) for r, c, g in zip(out["r_exact"], out["col_mean"], out["generator"])]
    out["bip_cyc"] = (out["n_ones"] - out["n"] - out["m"] + out["g_components"]) / out["n"]
    out["g_edges_n"] = out["g_edges"] / out["n"]
    for c in ("tw_min_fill", "g_degeneracy", "bw_rcm", "lb_best"):
        out[c + "_n"] = out[c] / out["n"]
    out["deg_predicted"] = [expected_degree(n, m, c, g) for n, m, c, g
                            in zip(out["n"], out["m"], out["col_mean"], out["generator"])]
    out["log_nodes"] = out["ln_default"]
    if CLIQUES_CSV.exists():
        cl = pd.read_csv(CLIQUES_CSV).drop_duplicates("instance_name")
        out = out.merge(cl, on="instance_name", how="left")
    else:
        out["clique_excess"] = np.nan
        out["max_cliques_over_m"] = np.nan
    return out


def load_frames(campaign_csv: Path = RESULTS_CSV, upward_csv: Path = RESULTS_UPWARD_CSV,
                ratio_csv: Path = RESULTS_RATIO_CSV) -> pd.DataFrame:
    parts = []
    for source, csv in (("campaign", campaign_csv), ("upward", upward_csv), ("ratio", ratio_csv)):
        f = load_results(csv)
        if len(f):
            f = f.copy()
            if source == "upward":
                f = apply_finish(f, csv.with_name("results_upward_finish.csv"))
            f["source"] = source
            parts.append(f)
    if not parts:
        return pd.DataFrame()
    return derive(pd.concat(parts, ignore_index=True))


def _cens_median(v: np.ndarray, c: np.ndarray) -> tuple[float, bool]:
    if len(v) == 0:
        return np.nan, False
    med = float(np.median(v))
    return med, bool(np.any(c & (v <= med)))


def cell_medians(frame: pd.DataFrame, config: str = "default") -> pd.DataFrame:
    """Per (generator, ratio_label, n, param): the censoring-aware median of
    log10(1 + nodes), the realised density and the median of every candidate."""
    ln, cens = f"ln_{config}", f"cens_{config}"
    rows = []
    for (gen, lab, n, param), g in frame.groupby(["generator", "ratio_label", "n", "param"]):
        med, is_lb = _cens_median(g[ln].to_numpy(float), g[cens].to_numpy(bool))
        row = {"generator": gen, "ratio_label": lab, "n": int(n), "param": float(param),
               "r_exact": float(g["r_exact"].iloc[0]), "m": int(g["m"].iloc[0]),
               "instances": len(g), "censored": int(g[cens].sum()),
               "median_log_nodes": med, "median_is_lower_bound": is_lb,
               "col_mean": float(g["col_mean"].median()),
               "deg_predicted": float(g["deg_predicted"].median())}
        for c in CANDIDATES:
            row[c] = float(g[c].median()) if g[c].notna().any() else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["generator", "ratio_label", "n", "col_mean"]).reset_index(drop=True)


def parabola_vertex(x: np.ndarray, y: np.ndarray) -> float:
    """Vertex of the parabola through three points, clamped to [x0, x2]; the
    middle point if the parabola is not concave."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    a, b, _ = np.polyfit(x, y, 2)
    if a >= 0:
        return float(x[1])
    return float(min(max(-b / (2 * a), x[0]), x[2]))


def interpolated_peak(cells: pd.DataFrame, frame: pd.DataFrame | None = None,
                      config: str = "default", resamples: int = 500,
                      rng: np.random.Generator | None = None) -> dict:
    """The peak of one series at one n: the cell with the largest median, the
    parabolic vertex in log10(col_mean) through it and its neighbours (when
    interior), and a bootstrap interval over instances within those cells."""
    cells = cells.sort_values("col_mean").reset_index(drop=True)
    i = int(cells["median_log_nodes"].idxmax())
    top = cells.loc[i]
    out = {"peak_param": float(top["param"]), "peak_cell_col_mean": float(top["col_mean"]),
           "peak_median_log_nodes": float(top["median_log_nodes"]),
           "peak_is_lower_bound": bool(top["median_is_lower_bound"]),
           "interior": bool(0 < i < len(cells) - 1)}
    if not out["interior"]:
        out.update({"peak_col_mean": float(top["col_mean"]), "ci_lo": np.nan, "ci_hi": np.nan})
        return out
    tri = cells.loc[i - 1:i + 1]
    x = np.log10(tri["col_mean"].to_numpy(float))
    out["peak_col_mean"] = 10 ** parabola_vertex(x, tri["median_log_nodes"].to_numpy(float))
    out["ci_lo"] = out["ci_hi"] = np.nan
    if frame is not None and resamples > 0:
        rng = rng or np.random.default_rng(SEED)
        samples = [frame[frame["param"] == p][f"ln_{config}"].to_numpy(float) for p in tri["param"]]
        if all(len(s) for s in samples):
            verts = np.empty(resamples)
            for b in range(resamples):
                y = [np.median(rng.choice(s, size=len(s), replace=True)) for s in samples]
                verts[b] = parabola_vertex(x, np.array(y))
            out["ci_lo"], out["ci_hi"] = (10 ** np.quantile(verts, 0.025), 10 ** np.quantile(verts, 0.975))
    return out


def _interp_at(cells: pd.DataFrame, column: str, col_mean: float) -> float:
    """A candidate's cell-median value at a fractional col_mean, linear in log col_mean."""
    x = np.log10(cells["col_mean"].to_numpy(float))
    y = cells[column].to_numpy(float)
    order = np.argsort(x)
    return float(np.interp(np.log10(col_mean), x[order], y[order]))


def peak_table(frame: pd.DataFrame, cells: pd.DataFrame | None = None, config: str = "default",
               min_n: int = 30, resamples: int = 500) -> pd.DataFrame:
    """One row per (generator, ratio_label, n >= min_n): the interpolated peak
    and every candidate's value there."""
    cells = cell_medians(frame, config) if cells is None else cells
    rng = np.random.default_rng(SEED)
    rows = []
    for (gen, lab, n), g in cells.groupby(["generator", "ratio_label", "n"]):
        if n < min_n or len(g) < 3:
            continue
        sub = frame[(frame["generator"] == gen) & (frame["ratio_label"] == lab) & (frame["n"] == n)]
        pk = interpolated_peak(g, sub, config, resamples, rng)
        row = {"generator": gen, "ratio_label": lab, "n": int(n), "r_exact": float(g["r_exact"].iloc[0]),
               "cells": len(g), **pk}
        c = pk["peak_col_mean"]
        for cand in CANDIDATES:
            row[cand] = _interp_at(g, cand, c)
        row["branch_analytic"] = branching_factor(row["r_exact"], c, gen)
        row["excess_analytic"] = excess(row["r_exact"], c)
        row["giant_col_mean"] = giant_threshold_col_mean(row["r_exact"], gen)
        row["tree_col_mean"] = tree_threshold_col_mean(row["r_exact"])
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# (c) constancy across m / n, (d) calibrated predictions
# ----------------------------------------------------------------------------


def constancy(peaks: pd.DataFrame, min_n: int = 50, candidates=CANDIDATES) -> pd.DataFrame:
    """Per candidate: how constant its value at the peak is across ratio labels
    at fixed (generator, n) -- CV and max/min -- for n >= min_n, where three or
    more ratios exist. Grid-edge peaks (fixed m = 2n) are included: their peak
    is at the edge cell, which is a lower bound on the location."""
    sub = peaks[peaks["n"] >= min_n]
    rows = []
    for cand in candidates:
        cvs, spans = [], []
        for (gen, n), g in sub.groupby(["generator", "n"]):
            if g["ratio_label"].nunique() < 3:
                continue
            v = g[cand].to_numpy(float)
            if np.all(np.isfinite(v)) and abs(v.mean()) > 1e-9:
                cvs.append(v.std(ddof=0) / abs(v.mean()))
                spans.append(v.max() / v.min() if v.min() > 0 else np.nan)
        v_all = sub[cand].to_numpy(float)
        rows.append({"candidate": cand, "text": CANDIDATE_TEXT[cand],
                     "cv_across_ratios_mean": float(np.mean(cvs)) if cvs else np.nan,
                     "cv_across_ratios_max": float(np.max(cvs)) if cvs else np.nan,
                     "max_over_min_across_ratios": float(np.nanmax(spans)) if spans else np.nan,
                     "cv_all_peaks": float(v_all.std(ddof=0) / abs(v_all.mean())) if len(v_all) else np.nan,
                     "peak_value_min": float(np.nanmin(v_all)), "peak_value_max": float(np.nanmax(v_all)),
                     "series_n": len(cvs)})
    return pd.DataFrame(rows).sort_values("cv_across_ratios_mean").reset_index(drop=True)


def calibrate(peaks: pd.DataFrame, candidate: str, generator: str, min_n: int = 50,
              on: str = "n") -> float:
    """The candidate's value at the `m = n` peaks of one generator, averaged over n >= min_n."""
    g = peaks[(peaks["generator"] == generator) & (peaks["ratio_label"] == on) & (peaks["n"] >= min_n)]
    return float(g[candidate].mean()) if len(g) else np.nan


def predict_peaks(peaks: pd.DataFrame, cells: pd.DataFrame, min_n: int = 50,
                  candidates=CANDIDATES, calibrate_on: str = "n") -> pd.DataFrame:
    """Every hypothesis 'the ridge is where <candidate> = its m = n value'
    predicts the other series' peak col_mean: analytically for the analytic
    candidates, by interpolating the candidate's cell medians along the series
    for the empirical ones. Compared with the measured interpolated peak and
    its bootstrap interval (an edge peak has none and is scored on the cell)."""
    rows = []
    for cand in candidates:
        for gen in peaks["generator"].unique():
            target = calibrate(peaks, cand, gen, min_n, calibrate_on)
            if not np.isfinite(target):
                continue
            sub = peaks[(peaks["generator"] == gen) & (peaks["n"] >= min_n)]
            for _, p in sub.iterrows():
                if cand in ANALYTIC:
                    pred = invert_candidate(cand, target, p["r_exact"], p["n"], gen)
                else:
                    g = cells[(cells["generator"] == gen) & (cells["ratio_label"] == p["ratio_label"])
                              & (cells["n"] == p["n"])].sort_values("col_mean")
                    x, y = np.log10(g["col_mean"].to_numpy(float)), g[cand].to_numpy(float)
                    if y[-1] >= y[0]:
                        pred = 10 ** float(np.interp(target, y, x, left=np.nan, right=np.nan))
                    else:
                        pred = 10 ** float(np.interp(-target, -y, x, left=np.nan, right=np.nan))
                meas = p["peak_col_mean"]
                lo, hi = p["ci_lo"], p["ci_hi"]
                if np.isfinite(lo):
                    within = bool(lo <= pred <= hi)
                else:                                   # edge peak: score against the edge cell
                    within = bool(np.isfinite(pred) and abs(np.log10(pred / meas)) <= 0.05)
                rows.append({"candidate": cand, "generator": gen, "ratio_label": p["ratio_label"], "n": int(p["n"]),
                             "calibration": target, "predicted_col_mean": pred, "measured_col_mean": meas,
                             "ci_lo": lo, "ci_hi": hi, "interior": bool(p["interior"]),
                             "log10_error": float(np.log10(pred / meas)) if np.isfinite(pred) and pred > 0 else np.nan,
                             "within_ci": within, "is_calibration": p["ratio_label"] == calibrate_on})
    return pd.DataFrame(rows)


def prediction_summary(pred: pd.DataFrame) -> pd.DataFrame:
    """Per candidate, over the non-calibration series: mean |log10 error|,
    within-interval count, and the same on the deciding ratios (n/2, n/4, n/8)."""
    rows = []
    for cand, g in pred[~pred["is_calibration"]].groupby("candidate"):
        dec = g[g["ratio_label"].isin(["n/2", "n/4", "n/8"])]
        rows.append({"candidate": cand, "text": CANDIDATE_TEXT[cand],
                     "series": len(g), "mean_abs_log10_error": float(g["log10_error"].abs().mean()),
                     "max_abs_log10_error": float(g["log10_error"].abs().max()),
                     "within_ci": int(g["within_ci"].sum()),
                     "deciding_series": len(dec),
                     "deciding_mean_abs_log10_error": float(dec["log10_error"].abs().mean()) if len(dec) else np.nan,
                     "deciding_within_ci": int(dec["within_ci"].sum())})
    return pd.DataFrame(rows).sort_values("mean_abs_log10_error").reset_index(drop=True)


# ----------------------------------------------------------------------------
# (e) collapse, the degree check, the giant threshold
# ----------------------------------------------------------------------------


def collapse_table(frame: pd.DataFrame, sizes=(50, 60, 75), candidates=("excess", "g_deg_mean", "col_mean",
                                                                         "row_mean", "opt_frac", "tw_min_fill_n",
                                                                         "bw_rcm_n", "branch")) -> pd.DataFrame:
    """§11's collapse test with the series keyed by (generator, ratio_label) at
    the sizes where three or more ratios exist."""
    from learning.hardness_map import _quantile_bins

    sub = frame[frame["n"].isin(sizes)].copy()
    sub["ratio"] = sub["ratio_label"]
    rows = []
    for cand in candidates:
        for n, g in sub.groupby("n"):
            x = g[cand].to_numpy(float)
            g = g.assign(_bin=_quantile_bins(x, 10))
            pooled = g.groupby("_bin")["log_nodes"].transform("median")
            r2 = 1.0 - float(np.var(g["log_nodes"] - pooled) / max(np.var(g["log_nodes"]), 1e-12))
            num = den = 0.0
            for _, h in g.groupby("_bin"):
                per = [s["log_nodes"].median() for _, s in h.groupby(["generator", "ratio"]) if len(s) >= 15]
                if len(per) >= 2:
                    num += (max(per) - min(per)) * len(h)
                    den += len(h)
            cell_med = g.groupby(["generator", "ratio", "param"])["log_nodes"].transform("median")
            ceiling = 1.0 - float(np.var(g["log_nodes"] - cell_med) / max(np.var(g["log_nodes"]), 1e-12))
            rows.append({"candidate": cand, "n": int(n), "series": int(g.groupby(["generator", "ratio"]).ngroups),
                         "dispersion": num / den if den else np.nan, "r2": r2, "cell_r2": ceiling})
    out = pd.DataFrame(rows)
    summary = out.groupby("candidate").agg(dispersion=("dispersion", "mean"), r2=("r2", "mean")).reset_index()
    summary["text"] = summary["candidate"].map(CANDIDATE_TEXT)
    return out, summary.sort_values("dispersion").reset_index(drop=True)


def degree_check(cells: pd.DataFrame, min_n: int = 40) -> pd.DataFrame:
    """Measured mean degree against the derivation, per generator and ratio:
    median and worst relative error over cells (the repairs of empty rows and
    columns are the only thing the derivation leaves out)."""
    sub = cells[cells["n"] >= min_n].copy()
    sub["rel_err"] = sub["deg_predicted"] / sub["g_deg_mean"] - 1.0
    rows = []
    for (gen, lab), g in sub.groupby(["generator", "ratio_label"]):
        rows.append({"generator": gen, "ratio_label": lab, "cells": len(g),
                     "median_rel_err": float(g["rel_err"].median()),
                     "max_abs_rel_err": float(g["rel_err"].abs().max()),
                     "sparsest_cell_rel_err": float(g.sort_values("col_mean").iloc[0]["rel_err"])})
    return pd.DataFrame(rows)


def threshold_bins(frame: pd.DataFrame, min_n: int = 30, max_n: int = 40,
                   edges=(0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, np.inf)) -> pd.DataFrame:
    """Instances at 30-40 customers binned by branching factor: median nodes,
    optimum / n, the giant component's share and the decomposable share. The
    literature's transition is at 1; the ridge is where nodes peak."""
    sub = frame[(frame["n"] >= min_n) & (frame["n"] <= max_n)].copy()
    sub["bin"] = pd.cut(sub["branch"], edges, right=False)
    rows = []
    for b, g in sub.groupby("bin", observed=True):
        rows.append({"branching_factor": str(b), "instances": len(g),
                     "median_log_nodes": float(g["log_nodes"].median()),
                     "median_nodes": float(10 ** g["log_nodes"].median() - 1),
                     "opt_frac_median": float(g["opt_frac"].median()),
                     "largest_component_frac": float(g["g_largest_comp_frac"].median()),
                     "decomposable_share": float((g["g_components"] > 1).mean()),
                     "excess_median": float(g["excess"].median())})
    return pd.DataFrame(rows)


def ridge_height(peaks: pd.DataFrame, min_n: int = 50) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The ridge's height (median log10 nodes at the interpolated peak cell)
    against m at fixed n, and the slope of log10 height in log10 m per (generator, n)."""
    sub = peaks[peaks["n"] >= min_n].copy()
    sub["m"] = (sub["r_exact"] * sub["n"]).round().astype(int)
    tab = sub[["generator", "n", "ratio_label", "m", "peak_col_mean", "peak_median_log_nodes",
               "peak_is_lower_bound", "excess"]].sort_values(["generator", "n", "m"])
    rows = []
    for (gen, n), g in tab.groupby(["generator", "n"]):
        if len(g) >= 3:
            slope, icpt = np.polyfit(np.log10(g["m"]), g["peak_median_log_nodes"], 1)
            rows.append({"generator": gen, "n": int(n), "ratios": len(g), "slope_log_height_per_log_m": float(slope),
                         "decades_per_doubling_of_m": float(slope * np.log10(2)),
                         "any_lower_bound": bool(g["peak_is_lower_bound"].any())})
    return tab.reset_index(drop=True), pd.DataFrame(rows)


def thresholds_table(peaks: pd.DataFrame, min_n: int = 50) -> pd.DataFrame:
    """Per series: the giant and tree thresholds in col_mean beside the ridge,
    and the ridge's branching factor and excess."""
    sub = peaks[peaks["n"] >= min_n]
    cols = ["generator", "ratio_label", "n", "r_exact", "giant_col_mean", "tree_col_mean", "peak_col_mean",
            "ci_lo", "ci_hi", "interior", "peak_is_lower_bound", "branch_analytic", "excess_analytic",
            "g_deg_mean", "opt_frac"]
    out = sub[cols].copy()
    out["ridge_over_giant"] = out["peak_col_mean"] / out["giant_col_mean"]
    return out.sort_values(["generator", "r_exact", "n"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# the figure and the tables
# ----------------------------------------------------------------------------

SERIES_COLOURS = {40: "#2a78d6", 50: "#eb6834", 60: "#1baf7a", 75: "#4a3aa7"}   # fixed order by n


def figure(cells: pd.DataFrame, peaks: pd.DataFrame, path: Path = FIGURE, deg_target: dict | None = None,
           excess_target: dict | None = None, sizes=(40, 50, 60, 75)) -> Path:
    """Median log nodes against col_mean, one panel per (generator, ratio), one
    line per n, with the giant threshold, the tree threshold, the calibrated
    excess condition and the calibrated mean-degree condition as vertical guides."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, NullFormatter, ScalarFormatter

    labels = ["n/8", "n/4", "n/2", "n", "2n"]
    gens = ["fixed", "bernoulli"]
    fig, axes = plt.subplots(2, 5, figsize=(19, 8.2), sharey="row")
    for i, gen in enumerate(gens):
        for j, lab in enumerate(labels):
            ax = axes[i, j]
            g = cells[(cells["generator"] == gen) & (cells["ratio_label"] == lab) & cells["n"].isin(sizes)]
            if g.empty:
                ax.text(0.5, 0.5, "not generated", ha="center", va="center", color="#6b6b66", transform=ax.transAxes)
                ax.set_axis_off()
                continue
            for n, h in g.groupby("n"):
                h = h.sort_values("col_mean")
                col = SERIES_COLOURS.get(int(n), "#6b6b66")
                ax.plot(h["col_mean"], h["median_log_nodes"], "-", color=col, lw=2, label=f"n = {n}")
                solid = h[~h["median_is_lower_bound"]]
                lb = h[h["median_is_lower_bound"]]
                ax.plot(solid["col_mean"], solid["median_log_nodes"], "o", color=col, ms=5)
                ax.plot(lb["col_mean"], lb["median_log_nodes"], "^", mfc="white", mec=col, ms=7)
            r = float(g["r_exact"].iloc[-1])
            ax.axvline(giant_threshold_col_mean(r, gen), color="#9a9a94", ls=":", lw=1.5)
            ax.axvline(tree_threshold_col_mean(r), color="#9a9a94", ls="--", lw=1.2)
            ex = (excess_target or {}).get(gen, 2.0)
            ax.axvline(invert_candidate("excess", ex, r, 75, gen), color="#111111", ls="-", lw=1.2)
            if deg_target and gen in deg_target:
                c_deg = invert_candidate("g_deg_mean", deg_target[gen], r, 75, gen)
                if np.isfinite(c_deg):
                    ax.axvline(c_deg, color="#e34948", ls="-.", lw=1.2)
            ax.set_xscale("log")
            ticks = [t for t in (1, 1.5, 2, 3, 5, 7, 10, 20, 30) if g["col_mean"].min() * 0.7 <= t <= g["col_mean"].max() * 1.3]
            ax.xaxis.set_major_locator(FixedLocator(ticks))
            ax.xaxis.set_major_formatter(ScalarFormatter())
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.set_title(f"{gen}, m = {lab}", fontsize=11, loc="left")
            ax.grid(True, color="#e6e6e2", lw=0.6)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            if i == 1:
                ax.set_xlabel("customers per product (col_mean, log)")
            if j == 0 or (j == 1 and i == 1):
                ax.set_ylabel("median log10(1 + nodes), optimum − 1")
    handles, labels_ = axes[0, 3].get_legend_handles_labels()
    fig.legend(handles, labels_, loc="lower center", ncol=len(handles), frameon=False, bbox_to_anchor=(0.5, 0.035))
    ex_txt = ", ".join(f"{g} {v:.2f}" for g, v in (excess_target or {}).items())
    dg_txt = ", ".join(f"{g} {v:.1f}" for g, v in (deg_target or {}).items())
    fig.text(0.5, 0.005,
             "Guides: dotted = giant-component threshold (branching factor 1); dashed = tree threshold (excess 1); "
             f"black = excess (n_ones − m)/n at its m = n ridge value ({ex_txt});\n red dash-dot = mean degree at its "
             f"m = n ridge value ({dg_txt}). Open triangles: censored medians, lower bounds.",
             fontsize=9, color="#3a3a38", ha="center")
    fig.tight_layout(rect=(0, 0.085, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140, facecolor="white")
    plt.close(fig)
    return path


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def report(out: Path = TABLES, resamples: int = 500) -> dict:
    t0 = time.time()
    frame = load_frames()
    cells = cell_medians(frame)
    peaks = peak_table(frame, cells, resamples=resamples)
    const = constancy(peaks)
    pred = predict_peaks(peaks, cells)
    psum = prediction_summary(pred)
    coll, coll_sum = collapse_table(frame)
    degc = degree_check(cells)
    tbins = threshold_bins(frame)
    thr = thresholds_table(peaks)
    height, height_fit = ridge_height(peaks)
    excess_gap = frame.loc[frame["clique_excess"].notna(), ["clique_excess", "excess"]]
    deg_target = {g: calibrate(peaks, "g_deg_mean", g) for g in ("fixed", "bernoulli")}
    excess_target = {g: calibrate(peaks, "excess", g) for g in ("fixed", "bernoulli")}
    fig_path = figure(cells, peaks, deg_target=deg_target, excess_target=excess_target)

    sources = frame.groupby("source").size().to_dict()
    lines = ["# Ridge theory tables (§25)", "",
             f"*Regenerate: `python -m learning.ridge_theory --stage tables`. Rows: {sources}. "
             f"{time.time() - t0:.0f} s. Figure: `{fig_path}`.*", ""]
    lines += ["## Interpolated peaks per series (n >= 30)", "",
              _md(peaks[["generator", "ratio_label", "n", "r_exact", "cells", "peak_param", "peak_cell_col_mean",
                         "peak_col_mean", "ci_lo", "ci_hi", "interior", "peak_is_lower_bound",
                         "peak_median_log_nodes"] + list(CANDIDATES)], ".3g"), ""]
    lines += ["## Constancy of each candidate across m / n at fixed (generator, n), n >= 50", "", _md(const, ".3g"), ""]
    lines += ["## Calibrated on the m = n ridge, predicted elsewhere: summary", "", _md(psum, ".3g"), ""]
    lines += ["## Calibrated predictions, every series", "",
              _md(pred.sort_values(["candidate", "generator", "n", "ratio_label"]), ".3g"), ""]
    lines += ["## Collapse at n in {50, 60, 75} (series = generator x ratio)", "", _md(coll_sum, ".3g"), "",
              _md(coll, ".3g"), ""]
    lines += ["## The derivation against the measured mean degree (cells at n >= 40)", "", _md(degc, ".3g"), ""]
    lines += ["## Thresholds beside the ridge (n >= 50)", "", _md(thr, ".3g"), ""]
    lines += ["## The ridge's height against m at fixed n", "", _md(height, ".3g"), "", _md(height_fit, ".3g"), ""]
    lines += ["## Instances at 30-40 customers binned by branching factor", "", _md(tbins, ".3g"), ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"wrote {out} and {fig_path} in {time.time() - t0:.0f} s")
    return {"frame": frame, "cells": cells, "peaks": peaks, "constancy": const, "pred": pred, "height": height,
            "height_fit": height_fit,
            "pred_summary": psum, "collapse": coll_sum, "degree_check": degc, "threshold_bins": tbins,
            "thresholds": thr, "deg_target": deg_target, "excess_target": excess_target}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="tables", choices=("run", "cliques", "tables"))
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--resamples", type=int, default=500)
    a = ap.parse_args()
    if a.stage == "run":
        t0 = time.time()
        f = run_ratio(workers=a.workers)
        print(f"{len(f)} rows, {time.time() - t0:.0f} s")
    elif a.stage == "cliques":
        t0 = time.time()
        f = compute_clique_excess(load_frames(), workers=a.workers)
        print(f"{len(f)} rows in {CLIQUES_CSV} in {time.time() - t0:.0f} s")
    else:
        report(resamples=a.resamples)
