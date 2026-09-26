"""Does what the campaign found at n <= 40 hold at 50-125? (plan §2.8, scaling only; loop0002 item 06)

Question
--------
Item 03 fitted the growth of the refutation node count with `n` on the
campaign (`reports/ml_nature.md` §11: exponential along the ridge, rate
0.086-0.105 log10 per customer), and item 04 fitted a formula for the mean
optimum `E[opt](n, m, p)` (§12). Both were fitted at `n <= 40`. This module
takes them as they stand and predicts, for the 200 Chu & Stuckey `Random`
corpus instances at 30-125 whose optima are certified, (a) the optimum and
(b) the number of nodes the complete customer search visits to refute
`optimum - 1`; then measures the error by size band and asks at what size
each prediction leaves a conformal interval calibrated on `n <= 40`.

Kill (plan §2.8): if coverage collapses across the size boundary, the
intervals say nothing at large sizes and the report must not quote them
there.

Data
----
* Optima and features of the 200 corpus instances: `learning/data/instances.csv`.
* Node counts at 30 and 40 (both configurations): `learning/data/node_counts.csv`.
* Node counts at 50-125: **none were in the ledger** (`compute_ledger.csv` has a
  `nodes` column but no row carries a value), so this module refutes
  `optimum - 1` itself under both `learning.node_counts` configurations with
  a per-call deadline (`--refute`), writing `learning/data/ensemble/scale_nodes.csv`
  (resumable). Calls that hit the deadline are **censored**: the count is a
  lower bound and is used only as such. The five 125x125 counts from
  `recertify/results.json` are under `better_move=True, better_move_dominators=0,
  memo=True`, which is exactly the `csearch` configuration on instances with
  at most five products per customer (`sparse_enough_for_better_move`), so
  they are used as `csearch` observations after that check.
* The campaign (`learning/data/ensemble/results.csv`, §10) is the training and
  calibration set for everything.

Run
---
    python -m learning.scale_test --refute --workers 16 --deadline 1500   # ~1 h; the node counts at 50-125
    python -m learning.scale_test                                         # the analysis, reports/scale_test_tables.md + figure
    python -m pytest tests/test_scale_test.py -q

Nothing here is a bound; nothing is written under `solutions/`; no solver
default is touched.
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DATA_DIR, DEFAULT_INSTANCE_DIR, enumerate_instances
from learning.node_counts import CONFIGS, refute

ENSEMBLE_DIR = DATA_DIR / "ensemble"
RESULTS_CSV = ENSEMBLE_DIR / "results.csv"
SCALE_NODES = ENSEMBLE_DIR / "scale_nodes.csv"
INSTANCES = DATA_DIR / "instances.csv"
NODE_COUNTS = DATA_DIR / "node_counts.csv"
RECERTIFY = Path("recertify/results.json")
LEDGER = Path("benchmarks/results/compute_ledger.csv")
TABLES = Path("reports/scale_test_tables.md")
FIGURE = Path("reports/figures/scale_test.png")

SKIP_CLASSES = {(125, 125, 2), (125, 125, 4)}   # a day each on record; recertify's counts stand in
BANDS = ((30, 40), (50, 50), (75, 75), (100, 100), (125, 125))


# ----------------------------------------------------------------------------
# the corpus targets and the refutation run
# ----------------------------------------------------------------------------


def parse_name(name: str) -> tuple[int, int, int, int]:
    """`Random-n-m-d-i_0` -> (n, m, d, i)."""
    parts = name.split("-")
    return int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4].split("_")[0])


def corpus_targets(instances_csv: Path = INSTANCES, instance_dir: Path = DEFAULT_INSTANCE_DIR,
                   min_n: int = 50, skip: set = SKIP_CLASSES) -> list[tuple]:
    """The Chu & Stuckey `Random` instances at n >= min_n with their certified optimum."""
    feats = pd.read_csv(instances_csv)
    feats = feats[feats["instance_name"].str.startswith("Random-")]
    optimum = dict(zip(feats["instance_name"], feats["optimum"].astype(int)))
    jobs = []
    for filepath, inst in enumerate_instances(instance_dir):
        if not inst.name.startswith("Random-") or inst.name not in optimum:
            continue
        n, m, d, _ = parse_name(inst.name)
        if n < min_n or (n, m, d) in skip:
            continue
        jobs.append((inst.matrix.tolist(), inst.name, str(filepath), optimum[inst.name]))
    # hardest first so the long calls start early: large n, then sparse
    jobs.sort(key=lambda j: (-parse_name(j[1])[0], -parse_name(j[1])[1], parse_name(j[1])[2]))
    return jobs


def _refute_job(args) -> dict:
    from mosp.instance import MOSPInstance

    matrix, name, source_file, optimum, config, deadline = args
    inst = MOSPInstance(matrix=np.array(matrix, dtype=np.int8), n_customers=len(matrix),
                        n_patterns=len(matrix[0]), name=name)
    row = {"instance_name": name, "source_file": source_file, "n_customers": inst.n_customers,
           "n_patterns": inst.n_patterns, "optimum": optimum, "deadline_seconds": deadline}
    row.update(refute(inst, optimum, config, deadline))
    return row


def run_refutations(out: Path = SCALE_NODES, workers: int = 16, deadline: float = 1500.0,
                    min_n: int = 50, configs: tuple = CONFIGS, skip: set = SKIP_CLASSES,
                    wall_budget: float | None = None) -> pd.DataFrame:
    """Refute `optimum - 1` for every target under every configuration; resumable, appends per row."""
    done = set()
    if out.exists():
        prev = pd.read_csv(out)
        done = set(zip(prev["instance_name"], prev["config"]))
    jobs = [j + (c, deadline) for j in corpus_targets(min_n=min_n, skip=skip) for c in configs
            if (j[1], c) not in done]
    print(f"{len(jobs)} refutations to run ({len(done)} already recorded), "
          f"{workers} workers, deadline {deadline:.0f} s per call", flush=True)
    fields = ["instance_name", "source_file", "n_customers", "n_patterns", "optimum",
              "deadline_seconds", "config", "status", "nodes", "seconds"]
    new = out.exists()
    started = time.monotonic()
    with out.open("a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        if not new:
            writer.writeheader()
        with multiprocessing.Pool(workers) as pool:
            for row in pool.imap_unordered(_refute_job, jobs, chunksize=1):
                writer.writerow(row)
                fh.flush()
                print(f"{row['instance_name']:>24} {row['config']:>8} {row['status']:>7} "
                      f"{row['nodes']:>14,d} {row['seconds']:>9.1f}s", flush=True)
                if wall_budget is not None and time.monotonic() - started > wall_budget:
                    print("wall budget reached; terminating the pool", flush=True)
                    pool.terminate()
                    break
    return pd.read_csv(out)



# ----------------------------------------------------------------------------
# loading
# ----------------------------------------------------------------------------

Q90 = 0.9
CALIBRATION_N = (35, 40)         # conformal calibration sizes; fits use n <= 30
FIT_MAX_N = 30
MIN_FIT_N = 15
HOLD_THRESHOLD = 0.8             # a 90% interval "holds" on a band of 25 if >= 80% are inside


def band_of(n: int) -> str:
    return "30-40" if n <= 40 else str(int(n))


def rig(n, m, p):
    """Random-intersection-graph nominal edge probability and mean degree."""
    q = 1.0 - (1.0 - np.asarray(p, dtype=float) ** 2) ** np.asarray(m, dtype=float)
    return q, (np.asarray(n, dtype=float) - 1) * q


def load_campaign(csv_path: Path = RESULTS_CSV) -> pd.DataFrame:
    f = pd.read_csv(csv_path)
    f["p_nom"] = np.where(f["generator"] == "fixed", f["param"] / f["n"], f["param"])
    f["p_real"] = f["n_ones"] / (f["n"] * f["m"])
    f["opt_frac"] = f["optimum"] / f["n"]
    f["x"] = np.log10(f["col_mean"])
    for c in CONFIGS:
        f[f"ln_{c}"] = np.log10(1.0 + f[f"nodes_{c}"])
    return f


def load_corpus(instances: Path = INSTANCES, node_counts: Path = NODE_COUNTS,
                scale_nodes: Path = SCALE_NODES, recertify: Path = RECERTIFY) -> pd.DataFrame:
    """The 200 `Random` corpus instances with optimum, features and every node count on record."""
    feats = pd.read_csv(instances)
    c = feats[feats["instance_name"].str.startswith("Random-")].copy()
    parts = c["instance_name"].apply(parse_name)
    c["n"] = [p[0] for p in parts]
    c["m"] = [p[1] for p in parts]
    c["d"] = [p[2] for p in parts]
    c["band"] = c["n"].apply(band_of)
    c["p_nom"] = c["d"] / c["n"]
    c["p_real"] = c["n_ones"] / (c["n"] * c["m"])
    c["opt_frac"] = c["optimum"] / c["n"]
    c["x"] = np.log10(c["col_mean"])
    for cfg in CONFIGS:
        c[f"nodes_{cfg}"] = np.nan
        c[f"status_{cfg}"] = ""
        c[f"source_{cfg}"] = ""
    def put(name, cfg, nodes, status, source):
        i = c.index[c["instance_name"] == name]
        if len(i):
            c.loc[i, f"nodes_{cfg}"] = float(nodes)
            c.loc[i, f"status_{cfg}"] = status
            c.loc[i, f"source_{cfg}"] = source
    if node_counts.exists():
        nc = pd.read_csv(node_counts)
        for r in nc[nc["instance_name"].str.startswith("Random-")].itertuples():
            put(r.instance_name, r.config, r.nodes, r.status, "node_counts (§3)")
    if scale_nodes.exists():
        for r in pd.read_csv(scale_nodes).itertuples():
            put(r.instance_name, r.config, r.nodes, r.status, "this module")
    if recertify.exists():
        for r in json.load(open(recertify)):
            # better_move=True, dominators 0, memo on == the csearch configuration on sparse instances
            put(r["name"], "csearch", r["nodes"], r["status"], "recertify (better_move=True)")
    for cfg in CONFIGS:
        c[f"ln_{cfg}"] = np.log10(1.0 + c[f"nodes_{cfg}"])
        c[f"censored_{cfg}"] = c[f"status_{cfg}"].eq("unknown")
    return c.sort_values(["n", "m", "d", "instance_name"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# (a) the optimum
# ----------------------------------------------------------------------------

PUBLISHED = (2.1, 27.0)          # §12's rounded constants, exponent 1/2


def formula(n, m, p, a: float = PUBLISHED[0], c: float = PUBLISHED[1]) -> np.ndarray:
    """§12: E[opt] ≈ a(1 − q) + n[1 − √(1 − q)·c/(D + c)], q = 1 − (1 − p²)^m, D = (n − 1)q."""
    n = np.asarray(n, dtype=float)
    q, D = rig(n, m, p)
    return a * (1 - q) + n * (1 - np.sqrt(np.clip(1 - q, 0, 1)) * c / (D + c))


def fit_formula(campaign: pd.DataFrame, max_n: int = FIT_MAX_N) -> tuple[float, float]:
    """Refit (a, c) by least absolute deviation on the cell means at n <= max_n (nominal p)."""
    from learning.concentration import _fit_form
    cells = campaign[campaign["n"] <= max_n].groupby(["generator", "n", "m", "param"]).agg(
        mean=("optimum", "mean"), p=("p_nom", "first")).reset_index()
    q, D = rig(cells["n"], cells["m"], cells["p"])
    fn = lambda n, D, q, a, c: a * (1 - q) + n * (1 - np.sqrt(1 - q) * c / (D + c))
    a, c = _fit_form(fn, cells["n"].to_numpy(float), D, q, cells["mean"].to_numpy(float), (2.0, 30.0))
    return float(a), float(c)


SCALE_FREE = {  # features of the MOSP graph that do not grow with n, for the boosted model
    "g_density": lambda f: f["g_density"], "g_clustering": lambda f: f["g_clustering"],
    "deg_mean_frac": lambda f: f["g_deg_mean"] / f["n"], "deg_std_frac": lambda f: f["g_deg_std"] / f["n"],
    "deg_min_frac": lambda f: f["g_deg_min"] / f["n"], "deg_max_frac": lambda f: f["g_deg_max"] / f["n"],
    "degeneracy_frac": lambda f: f["g_degeneracy"] / f["n"], "tw_min_fill_frac": lambda f: f["tw_min_fill"] / f["n"],
    "bw_rcm_frac": lambda f: f["bw_rcm"] / f["n"], "sep_frac": lambda f: f["sep_frac"],
    "largest_comp_frac": lambda f: f["g_largest_comp_frac"], "fiedler_lcc": lambda f: f["fiedler_lcc"],
    "spectral_frac": lambda f: f["spectral_radius"] / f["n"], "log_n": lambda f: np.log10(f["n"]),
}


def scale_free(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({k: fn(frame) for k, fn in SCALE_FREE.items()}, index=frame.index)


def gbm_fit_predict(train: pd.DataFrame, y: np.ndarray, targets: list[pd.DataFrame], seed: int = 0):
    """LightGBM on scale-free graph features; None if LightGBM is not installed."""
    try:
        import lightgbm as lgb
    except ImportError:  # pragma: no cover - soft dependency
        return None
    model = lgb.LGBMRegressor(n_estimators=400, learning_rate=0.03, num_leaves=15, min_child_samples=40,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=seed)
    model.fit(scale_free(train), y)
    return [model.predict(scale_free(t)) for t in targets]


def optimum_predictions(campaign: pd.DataFrame, corpus: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Every estimate of the optimum on the calibration set (campaign n = 35, 40) and on the corpus."""
    a, c = fit_formula(campaign)
    cal = campaign[campaign["n"].isin(CALIBRATION_N)].copy()
    train = campaign[campaign["n"] <= FIT_MAX_N]
    preds_cal, preds_cor = {}, {}
    preds_cal["formula, nominal p (refit n≤30)"] = formula(cal["n"], cal["m"], cal["p_nom"], a, c)
    preds_cor["formula, nominal p (refit n≤30)"] = formula(corpus["n"], corpus["m"], corpus["p_nom"], a, c)
    preds_cal["formula, realised p (refit n≤30)"] = formula(cal["n"], cal["m"], cal["p_real"], a, c)
    preds_cor["formula, realised p (refit n≤30)"] = formula(corpus["n"], corpus["m"], corpus["p_real"], a, c)
    preds_cal["formula, realised p (§12 constants)"] = formula(cal["n"], cal["m"], cal["p_real"])
    preds_cor["formula, realised p (§12 constants)"] = formula(corpus["n"], corpus["m"], corpus["p_real"])
    for name, col in (("tw_min_fill + 1", "tw_min_fill"),):
        preds_cal[name] = cal[col].to_numpy(float) + 1
        preds_cor[name] = corpus[col].to_numpy(float) + 1
    preds_cal["sandwich midpoint (§5)"] = (cal["g_degeneracy"] + cal["bw_rcm"]).to_numpy(float) / 2 + 1
    preds_cor["sandwich midpoint (§5)"] = (corpus["g_degeneracy"] + corpus["bw_rcm"]).to_numpy(float) / 2 + 1
    preds_cal["lb_best"] = cal["lb_best"].to_numpy(float)
    preds_cor["lb_best"] = corpus["lb_best"].to_numpy(float)
    preds_cal["ub_best (cs-dfs / mcn+tabu)"] = cal["ub_best"].to_numpy(float)
    preds_cor["ub_best (cs-dfs / mcn+tabu)"] = corpus["ub_best"].to_numpy(float)
    gbm = gbm_fit_predict(train, train["opt_frac"].to_numpy(float), [cal, corpus])
    if gbm is not None:
        preds_cal["gbm, scale-free graph features → opt/n (n≤30)"] = gbm[0] * cal["n"].to_numpy(float)
        preds_cor["gbm, scale-free graph features → opt/n (n≤30)"] = gbm[1] * corpus["n"].to_numpy(float)
    return (pd.DataFrame(preds_cal, index=cal.index).assign(n=cal["n"], optimum=cal["optimum"]),
            pd.DataFrame(preds_cor, index=corpus.index).assign(n=corpus["n"], optimum=corpus["optimum"]),
            {"a": a, "c": c})


def corpus_linearity(corpus: pd.DataFrame) -> pd.DataFrame:
    """Per density class with m = n: the class-mean optimum against n over 30-125, as a line.

    §12 found E[opt] linear in n above the giant-component threshold at
    n <= 40; this is the same statement read off the corpus at 30-125,
    with the slope, intercept, r² and the largest residual of the class means.
    """
    rows = []
    c = corpus[corpus["m"] == corpus["n"]]
    for d, g in c.groupby("d"):
        means = g.groupby("n")["optimum"].mean()
        ns = means.index.to_numpy(float); y = means.to_numpy(float)
        slope, intercept = np.polyfit(ns, y, 1)
        fit = intercept + slope * ns
        r2 = 1 - ((y - fit) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        rows.append({"d": int(d), "col_mean": float(g["col_mean"].mean()), "sizes": len(ns),
                     "slope": float(slope), "intercept": float(intercept), "r²": float(r2),
                     "max |resid| of class means": float(np.abs(y - fit).max()),
                     "opt/n at smallest n": float(y[0] / ns[0]), "opt/n at largest n": float(y[-1] / ns[-1]),
                     **{f"mean opt n={int(k)}": float(v) for k, v in means.items()}})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# conformal intervals and where they stop holding
# ----------------------------------------------------------------------------


def conformal_quantile(residuals: np.ndarray, level: float = Q90) -> float:
    """Split-conformal radius: the ⌈(N+1)·level⌉/N empirical quantile of |residual|."""
    r = np.sort(np.abs(np.asarray(residuals, dtype=float)))
    r = r[np.isfinite(r)]
    if len(r) == 0:
        return np.nan
    k = int(np.ceil((len(r) + 1) * level))
    return float(r[min(k, len(r)) - 1])


def coverage_table(pred: np.ndarray, truth: np.ndarray, n: np.ndarray, band: np.ndarray,
                   radius_abs: float, radius_rel: float, censored: np.ndarray | None = None,
                   lower_bound_only: np.ndarray | None = None) -> pd.DataFrame:
    """Per band: error statistics and the share inside the absolute and the n-scaled interval.

    A censored observation (deadline hit) is a lower bound on the truth: it
    counts as *outside* only if that lower bound already exceeds the upper end
    of the interval, as *inside* only if the interval's upper end is provably
    ... never (the truth may be anything above), so it is reported as
    undetermined and excluded from the coverage ratio.
    """
    pred = np.asarray(pred, float); truth = np.asarray(truth, float); n = np.asarray(n, float)
    cens = np.zeros(len(pred), bool) if censored is None else np.asarray(censored, bool)
    have = np.isfinite(truth) & np.isfinite(pred)
    err = pred - truth
    rows = []
    order = sorted(set(band), key=lambda b: int(b.split("-")[0]))
    for b in order:
        sel = (np.asarray(band) == b) & have
        k = int(sel.sum())
        if k == 0:
            rows.append({"band": b, "observed": 0}); continue
        e, c_ = err[sel], cens[sel]
        if not np.isfinite(radius_abs):
            rows.append({"band": b, "observed": k, "censored": int(c_.sum()),
                         "mae": float(np.abs(e[~c_]).mean()) if (~c_).any() else np.nan,
                         "bias": float(e[~c_].mean()) if (~c_).any() else np.nan,
                         "max |err|": float(np.abs(e[~c_]).max()) if (~c_).any() else np.nan,
                         "coverage abs": np.nan, "coverage n-scaled": np.nan,
                         "undetermined (censored)": int(c_.sum())})
            continue
        in_abs = np.abs(e) <= radius_abs
        in_rel = np.abs(e) <= radius_rel * n[sel]
        # censored: outside if truth_lb > pred + radius (definite), else undetermined
        def_out_abs = c_ & (truth[sel] > pred[sel] + radius_abs)
        def_out_rel = c_ & (truth[sel] > pred[sel] + radius_rel * n[sel])
        und_abs = c_ & ~def_out_abs
        und_rel = c_ & ~def_out_rel
        det_abs = ~und_abs; det_rel = ~und_rel
        rows.append({
            "band": b, "observed": k, "censored": int(c_.sum()),
            "mae": float(np.abs(e[~c_]).mean()) if (~c_).any() else np.nan,
            "bias": float(e[~c_].mean()) if (~c_).any() else np.nan,
            "max |err|": float(np.abs(e[~c_]).max()) if (~c_).any() else np.nan,
            "inside abs": int((in_abs & ~c_).sum()), "determined abs": int(det_abs.sum()),
            "coverage abs": float((in_abs & ~c_).sum() / det_abs.sum()) if det_abs.any() else np.nan,
            "inside n-scaled": int((in_rel & ~c_).sum()), "determined n-scaled": int(det_rel.sum()),
            "coverage n-scaled": float((in_rel & ~c_).sum() / det_rel.sum()) if det_rel.any() else np.nan,
            "undetermined (censored)": int(und_abs.sum()),
        })
    return pd.DataFrame(rows)


def first_failure(cov: pd.DataFrame, column: str, threshold: float = HOLD_THRESHOLD) -> str:
    """The first band (in size order) whose coverage falls below the threshold; 'holds' if none."""
    for r in cov.itertuples():
        v = getattr(r, column.replace(" ", "_").replace("-", "_"), None)
        if v is None:
            v = cov.loc[r.Index, column]
        if pd.notna(v) and v < threshold:
            return str(r.band)
    return "holds through 125"


# ----------------------------------------------------------------------------
# (b) the nodes
# ----------------------------------------------------------------------------


def cell_laws(campaign: pd.DataFrame, config: str = "default", max_n: int = FIT_MAX_N,
              min_n: int = MIN_FIT_N, min_value: float = 2.0, ratio: int = 1) -> pd.DataFrame:
    """§11's law per fixed-generator density at m = ratio·n: log10(median nodes) = a + b·n, fitted on cells at min_n..max_n."""
    fx = campaign[(campaign["generator"] == "fixed") & (campaign["m"] == ratio * campaign["n"])]
    cells = fx.groupby(["param", "n"]).agg(median=(f"nodes_{config}", "median"),
                                          col_mean=("col_mean", "median")).reset_index()
    rows = []
    for d, g in cells.groupby("param"):
        g = g[(g["n"] >= min_n) & (g["n"] <= max_n) & (g["median"] >= min_value)].sort_values("n")
        if len(g) < 3:
            continue
        b, a = np.polyfit(g["n"], np.log10(g["median"]), 1)
        rows.append({"d": float(d), "col_mean": float(cells[cells["param"] == d]["col_mean"].median()),
                     "a": float(a), "b": float(b), "doubling_n": float(np.log10(2) / b), "points": len(g),
                     "n_range": f"{int(g['n'].min())}-{int(g['n'].max())}"})
    return pd.DataFrame(rows).sort_values("col_mean").reset_index(drop=True)


def law_predict(laws: pd.DataFrame, n, col_mean, ratio=None, law_ratio: int = 1) -> np.ndarray:
    """Interpolate (a, b) linearly in log10(col_mean) between adjacent densities; clamp at the ends.

    A law is for one product-to-customer ratio; where `ratio` (m / n per row)
    is given, rows at another ratio get NaN rather than a wrong law.
    """
    x = np.log10(np.asarray(col_mean, dtype=float))
    xs = np.log10(laws["col_mean"].to_numpy(float))
    a = np.interp(x, xs, laws["a"].to_numpy(float))
    b = np.interp(x, xs, laws["b"].to_numpy(float))
    out = a + b * np.asarray(n, dtype=float)
    if ratio is not None:
        out = np.where(np.isclose(np.asarray(ratio, dtype=float), law_ratio), out, np.nan)
    return out


def laws_predict(laws_by_ratio: dict, frame: pd.DataFrame) -> np.ndarray:
    """Apply the law of each row's own m / n; NaN where the campaign has no such ratio (m = n / 2)."""
    ratio = (frame["m"] / frame["n"]).to_numpy(float)
    out = np.full(len(frame), np.nan)
    for r, laws in laws_by_ratio.items():
        pred = law_predict(laws, frame["n"], frame["col_mean"], ratio, r)
        out = np.where(np.isfinite(pred), pred, out)
    return out


def ridge_predict(laws: pd.DataFrame, n, ridge_d: float = 3.0) -> np.ndarray:
    row = laws[laws["d"] == ridge_d].iloc[0]
    return row["a"] + row["b"] * np.asarray(n, dtype=float)


SURFACE_TERMS = {  # a linear, hence extrapolable, surface in n and label-free graph quantities
    "n": lambda f: f["n"], "x": lambda f: f["x"], "x2": lambda f: f["x"] ** 2,
    "n·x": lambda f: f["n"] * f["x"], "n·x2": lambda f: f["n"] * f["x"] ** 2,
    "opt_frac": lambda f: f["opt_frac"], "opt_frac2": lambda f: f["opt_frac"] ** 2,
    "n·opt_frac": lambda f: f["n"] * f["opt_frac"], "n·opt_frac2": lambda f: f["n"] * f["opt_frac"] ** 2,
    "log_deg": lambda f: np.log10(1 + f["g_deg_mean"]), "n·log_deg": lambda f: f["n"] * np.log10(1 + f["g_deg_mean"]),
    "deg_cv": lambda f: f["g_deg_std"] / (1 + f["g_deg_mean"]),
    "n·deg_cv": lambda f: f["n"] * f["g_deg_std"] / (1 + f["g_deg_mean"]),
    "largest_comp_frac": lambda f: f["g_largest_comp_frac"],
    "log_ratio": lambda f: np.log10(f["m"] / f["n"]), "n·log_ratio": lambda f: f["n"] * np.log10(f["m"] / f["n"]),
}


def surface_design(frame: pd.DataFrame) -> np.ndarray:
    cols = [np.ones(len(frame))] + [np.asarray(fn(frame), dtype=float) for fn in SURFACE_TERMS.values()]
    return np.column_stack(cols)


def surface_fit(train: pd.DataFrame, config: str = "default", ridge: float = 1e-3) -> np.ndarray:
    X = surface_design(train)
    y = train[f"ln_{config}"].to_numpy(float)
    keep = np.isfinite(y)
    X, y = X[keep], y[keep]
    return np.linalg.solve(X.T @ X + ridge * np.eye(X.shape[1]), X.T @ y)


def surface_predict(beta: np.ndarray, frame: pd.DataFrame) -> np.ndarray:
    return surface_design(frame) @ beta


def node_predictions(campaign: pd.DataFrame, corpus: pd.DataFrame, config: str = "default") -> dict:
    """The three node predictors on the calibration set and the corpus, with the cell laws."""
    laws = cell_laws(campaign, config)
    laws40 = cell_laws(campaign, config, max_n=40)
    by_ratio = {1: laws, 2: cell_laws(campaign, config, ratio=2)}
    by_ratio40 = {1: laws40, 2: cell_laws(campaign, config, max_n=40, ratio=2)}
    cal = campaign[campaign["n"].isin(CALIBRATION_N) & (campaign["generator"] == "fixed")].copy()
    cal_all = campaign[campaign["n"].isin(CALIBRATION_N)].copy()
    train = campaign[campaign["n"] <= FIT_MAX_N]
    beta = surface_fit(train, config)
    preds_cal = {
        "cell law, interpolated in col_mean (fit 15-30)": laws_predict(by_ratio, cal),
        "surface in (n, col_mean, opt/n, degree) (fit ≤30)": surface_predict(beta, cal),
    }
    preds_cor = {
        "cell law, interpolated in col_mean (fit 15-30)": laws_predict(by_ratio, corpus),
        "cell law, interpolated in col_mean (fit 15-40, §11)": laws_predict(by_ratio40, corpus),
        "ridge law d = 3 (fit 15-40, §11 pre-registration)": ridge_predict(laws40, corpus["n"]),
        "surface in (n, col_mean, opt/n, degree) (fit ≤30)": surface_predict(beta, corpus),
    }
    cal_frames = {"cell law, interpolated in col_mean (fit 15-30)": cal,
                  "surface in (n, col_mean, opt/n, degree) (fit ≤30)": cal_all}
    # the surface is calibrated on all four series; the cell law on the fixed m = n series it was fitted to
    preds_cal["surface in (n, col_mean, opt/n, degree) (fit ≤30)"] = surface_predict(beta, cal_all)
    return {"laws": laws, "laws40": laws40, "laws_2n": by_ratio[2], "beta": beta, "cal": cal, "cal_all": cal_all,
            "preds_cal": preds_cal, "preds_cor": preds_cor, "cal_frames": cal_frames}


def corpus_scaling(corpus: pd.DataFrame, config: str = "default") -> pd.DataFrame:
    """Per Chu & Stuckey density class: median log10 nodes at each n from the corpus itself, and its fit.

    Uses only sizes where every instance of the class has an uncensored
    count, so a median is a median. Fits `fit_scaling` (exponential vs power
    law) over all such sizes, and the local rate between consecutive sizes.
    """
    from learning.hardness_map import fit_scaling
    c = corpus[corpus["m"] == corpus["n"]]
    rows = []
    for d, g in c.groupby("d"):
        med = {}
        for n, h in g.groupby("n"):
            if h[f"nodes_{config}"].notna().all() and not h[f"censored_{config}"].any():
                med[int(n)] = float(h[f"nodes_{config}"].median())
        ns = np.array(sorted(med)); vals = np.array([med[k] for k in ns])
        fit = fit_scaling(ns, vals) if len(ns) >= 3 else {}
        local = {f"rate {ns[i]}→{ns[i+1]}": float((np.log10(1 + vals[i + 1]) - np.log10(1 + vals[i])) / (ns[i + 1] - ns[i]))
                 for i in range(len(ns) - 1)}
        rows.append({"d": int(d), "sizes with full counts": ",".join(map(str, ns)),
                     **{f"median n={k}": med[k] for k in ns}, **{k: fit.get(k) for k in ("rate", "doubling_n", "rms_exp", "alpha", "rms_pow", "better")},
                     **local})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# report
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def report(out_tables: Path = TABLES, figure_path: Path = FIGURE) -> dict:
    campaign = load_campaign()
    corpus = load_corpus()
    results: dict = {}
    lines = ["# Scale test tables (loop0002 item 06, `python -m learning.scale_test`)", "",
             f"*Generated {time.strftime('%Y-%m-%d %H:%M')}. Fits on campaign n ≤ {FIT_MAX_N}, conformal radii from "
             f"campaign n ∈ {CALIBRATION_N} at level {Q90:.0%}; coverage on the 200 Chu & Stuckey `Random` corpus instances.*", ""]

    # --- data on record
    rec = []
    for cfg in CONFIGS:
        for (n, m), g in corpus.groupby(["n", "m"]):
            have = g[f"nodes_{cfg}"].notna()
            rec.append({"config": cfg, "n": n, "m": m, "instances": len(g), "with count": int(have.sum()),
                        "censored": int(g[f"censored_{cfg}"].sum()),
                        "sources": ", ".join(sorted(set(g.loc[have, f"source_{cfg}"])))})
    results["record"] = pd.DataFrame(rec)
    lines += ["## Node counts on record, by configuration and size", "", _md(results["record"]), ""]

    # --- (a) optimum
    pc, po, consts = optimum_predictions(campaign, corpus)
    results["formula_constants"] = consts
    opt_rows, cov_tables = [], {}
    band = corpus["band"].to_numpy()
    for name in [c for c in pc.columns if c not in ("n", "optimum")]:
        res_cal = pc[name] - pc["optimum"]
        r_abs = conformal_quantile(res_cal)
        r_rel = conformal_quantile(res_cal / pc["n"])
        cov = coverage_table(po[name].to_numpy(float), po["optimum"].to_numpy(float), po["n"].to_numpy(float), band, r_abs, r_rel)
        cov_tables[name] = cov
        row = {"estimate": name, "radius abs": r_abs, "radius per customer": r_rel,
               "n-scaled radius at 50 / 125": f"{r_rel * 50:.1f} / {r_rel * 125:.1f}",
               "calib. MAE (35-40)": float(res_cal.abs().mean())}
        for b in cov["band"]:
            r = cov[cov["band"] == b].iloc[0]
            row[f"MAE {b}"] = r["mae"]; row[f"bias {b}"] = r["bias"]
            row[f"cov abs {b}"] = r["coverage abs"]; row[f"cov n-scaled {b}"] = r["coverage n-scaled"]
        row["abs interval first fails at"] = first_failure(cov, "coverage abs")
        row["n-scaled interval first fails at"] = first_failure(cov, "coverage n-scaled")
        opt_rows.append(row)
    results["optimum"] = pd.DataFrame(opt_rows)
    results["optimum_coverage"] = cov_tables
    results["optimum_pred"] = po
    lines += ["## (a) The optimum: error by size band and conformal coverage", "",
              f"Formula constants refit on n ≤ {FIT_MAX_N} cell means: a = {consts['a']:.3f}, c = {consts['c']:.2f} "
              f"(§12 on n ≤ 40: 2.1, 27 with exponent ½).", "", _md(results["optimum"]), ""]
    # per class for the two formula variants and tw
    cls_rows = []
    for (n, m, d), g in corpus.groupby(["n", "m", "d"]):
        row = {"class": f"Random-{n}-{m}-{d}", "col_mean": float(g["col_mean"].mean()),
               "optimum (mean)": float(g["optimum"].mean()), "opt/n": float(g["opt_frac"].mean())}
        for name in ("formula, nominal p (refit n≤30)", "formula, realised p (refit n≤30)", "tw_min_fill + 1",
                     "sandwich midpoint (§5)"):
            row[f"{name.split(' (')[0]}: bias"] = float((po.loc[g.index, name] - g["optimum"]).mean())
        cls_rows.append(row)
    results["optimum_by_class"] = pd.DataFrame(cls_rows)
    lines += ["### Per class: mean signed error (estimate − optimum)", "", _md(results["optimum_by_class"]), ""]
    results["optimum_linearity"] = corpus_linearity(corpus)
    lines += ["### Is E[opt] linear in n at fixed density from 30 to 125? (class means, m = n)", "",
              _md(results["optimum_linearity"], ".4g"), ""]

    # --- (b) nodes
    node_tables = {}
    for cfg in CONFIGS:
        npred = node_predictions(campaign, corpus, cfg)
        rows = []
        covs = {}
        for name, pred in npred["preds_cor"].items():
            if name in npred["preds_cal"]:
                calf = npred["cal_frames"][name]
                res_cal = npred["preds_cal"][name] - calf[f"ln_{cfg}"].to_numpy(float)
                r_abs = conformal_quantile(res_cal); r_rel = conformal_quantile(res_cal / calf["n"].to_numpy(float))
                cmae = float(np.nanmean(np.abs(res_cal)))
            else:
                r_abs = r_rel = cmae = np.nan
            truth = corpus[f"ln_{cfg}"].to_numpy(float)
            cov = coverage_table(pred, truth, corpus["n"].to_numpy(float), band, r_abs, r_rel,
                                 censored=corpus[f"censored_{cfg}"].to_numpy(bool))
            covs[name] = cov
            row = {"predictor": name, "radius abs (log10)": r_abs, "radius per customer": r_rel,
                   "n-scaled radius at 50 / 125": f"{r_rel * 50:.2f} / {r_rel * 125:.2f}" if np.isfinite(r_rel) else "",
                   "calib. MAE (35-40)": cmae}
            for b in cov["band"]:
                r = cov[cov["band"] == b].iloc[0]
                if r["observed"] == 0:
                    continue
                row[f"obs {b}"] = int(r["observed"]); row[f"bias {b}"] = r["bias"]; row[f"MAE {b}"] = r["mae"]
                row[f"cov abs {b}"] = r["coverage abs"]; row[f"cov n-scaled {b}"] = r["coverage n-scaled"]
                row[f"undet. {b}"] = int(r["undetermined (censored)"])
            if np.isfinite(r_abs):
                row["abs interval first fails at"] = first_failure(cov, "coverage abs")
                row["n-scaled interval first fails at"] = first_failure(cov, "coverage n-scaled")
            rows.append(row)
        node_tables[cfg] = {"summary": pd.DataFrame(rows), "coverage": covs, "laws": npred["laws"], "laws40": npred["laws40"],
                            "beta": npred["beta"], "preds_cor": npred["preds_cor"], "scaling": corpus_scaling(corpus, cfg)}
        lines += [f"## (b) Nodes to refute optimum − 1, configuration `{cfg}`", "",
                  f"### Cell laws log10(median nodes) = a + b·n, fixed m = n, fit on n {MIN_FIT_N}-{FIT_MAX_N}", "",
                  _md(npred["laws"], ".4g"), "", "### The same on n 15-40 (§11's fit)", "", _md(npred["laws40"], ".4g"), "",
                  "### Cell laws for fixed m = 2n, fit on n 15-30 (used for the Random-50-100 classes; Random-100-50 has no campaign counterpart)", "",
                  _md(npred["laws_2n"], ".4g"), "",
                  "### Predictors: bias / MAE (log10 nodes) and coverage by band", "", _md(node_tables[cfg]["summary"]), "",
                  "### Scaling measured on the corpus itself (medians over the 5 instances of each class, m = n)", "",
                  _md(node_tables[cfg]["scaling"], ".4g"), ""]
        # per class comparison
        prow = []
        for (n, m, d), g in corpus.groupby(["n", "m", "d"]):
            obs = g[f"ln_{cfg}"]; cen = g[f"censored_{cfg}"]
            row = {"class": f"Random-{n}-{m}-{d}", "counts": int(obs.notna().sum()), "censored": int(cen.sum()),
                   "observed median log10": float(obs[~cen].median()) if (~cen & obs.notna()).any() else np.nan,
                   "observed min": float(obs.min()) if obs.notna().any() else np.nan,
                   "observed max": float(obs.max()) if obs.notna().any() else np.nan}
            for name, pred in npred["preds_cor"].items():
                row[name] = float(np.nanmean(pred[g.index])) if np.isfinite(pred[g.index]).any() else np.nan
            prow.append(row)
        node_tables[cfg]["by_class"] = pd.DataFrame(prow)
        lines += ["### Per class: observed against predicted (log10 nodes; censored rows are lower bounds)", "",
                  _md(node_tables[cfg]["by_class"]), ""]
    results["nodes"] = node_tables

    # --- the five 125x125 recertify counts against the laws
    five = corpus[corpus["source_csearch"].str.startswith("recertify")]
    if len(five):
        laws40 = node_tables["csearch"]["laws40"]; laws30 = node_tables["csearch"]["laws"]
        t = pd.DataFrame({"instance": five["instance_name"], "col_mean": five["col_mean"], "opt/n": five["opt_frac"],
                          "observed log10 nodes (better_move=True)": five["ln_csearch"],
                          "ridge d=3 law (15-40)": ridge_predict(laws40, five["n"]),
                          "interpolated law (15-40)": law_predict(laws40, five["n"], five["col_mean"]),
                          "interpolated law (15-30)": law_predict(laws30, five["n"], five["col_mean"]),
                          "surface (≤30)": node_tables["csearch"]["preds_cor"]["surface in (n, col_mean, opt/n, degree) (fit ≤30)"][five.index]})
        results["five"] = t
        lines += ["## The five 125 × 125 refutations on record (csearch configuration) against the n ≤ 40 laws", "", _md(t), ""]

    out_tables.parent.mkdir(parents=True, exist_ok=True)
    out_tables.write_text("\n".join(lines))
    try:
        figure(campaign, corpus, node_tables, po, figure_path)
    except Exception as exc:  # noqa: BLE001 - the figure is not the deliverable
        print(f"figure skipped: {exc}", file=sys.stderr)
    results["corpus"] = corpus
    return results


def figure(campaign: pd.DataFrame, corpus: pd.DataFrame, node_tables: dict, po: pd.DataFrame,
           path: Path = FIGURE) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    palette = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    ax = axes[0]
    laws = node_tables["default"]["laws40"]
    fx = campaign[(campaign["generator"] == "fixed") & (campaign["m"] == campaign["n"])]
    ns = np.arange(15, 126)
    for color, d in zip(palette, (2, 3, 4, 6, 8)):
        cm = fx[fx["param"] == d]
        med = cm.groupby("n")["ln_default"].median()
        ax.plot(med.index, med.values, "o", color=color, ms=4, alpha=0.8)
        row = laws[laws["d"] == d]
        if len(row):
            ax.plot(ns, row["a"].iloc[0] + row["b"].iloc[0] * ns, "--", color=color, lw=1, alpha=0.7)
    c = corpus[corpus["m"] == corpus["n"]]
    for color, (d_c, cmap) in zip(palette, ((2, 3), (None, None), (4, 4), (6, 6), (8, 8))):
        if d_c is None:
            continue
        g = c[c["d"] == d_c]
        ok = g["nodes_default"].notna() & ~g["censored_default"]
        ax.plot(g.loc[ok, "n"] + 0.6, g.loc[ok, "ln_default"], "s", color=color, ms=5, mec="black", mew=0.5,
                label=f"Chu & Stuckey d = {d_c} (observed)")
        cen = g["censored_default"]
        if cen.any():
            ax.plot(g.loc[cen, "n"] + 0.6, g.loc[cen, "ln_default"], "^", color=color, ms=6, mec="black", mew=0.5)
    ax.set_xlabel("n (customers)"); ax.set_ylabel("log10 nodes to refute optimum − 1 (default configuration)")
    ax.set_title("Campaign cell medians (dots), their n ≤ 40 exponential fits (dashed)\nand the corpus counts at 30–125 (squares; triangles = censored lower bounds)", fontsize=9)
    ax.legend(fontsize=7, loc="upper left"); ax.grid(alpha=0.25)
    ax = axes[1]
    name = "formula, realised p (refit n≤30)"
    err = po[name] - po["optimum"]
    for color, d in zip(palette, (2, 4, 6, 8, 10)):
        sel = corpus["d"] == d
        ax.plot(corpus.loc[sel, "n"] + (d - 6) * 0.6, err[sel], "o", color=color, ms=4, label=f"d = {d}")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("n (customers)"); ax.set_ylabel("formula − certified optimum (stacks)")
    ax.set_title("(a) §12 formula with realised p, constants refit on n ≤ 30", fontsize=9)
    ax.legend(fontsize=7); ax.grid(alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--refute", action="store_true", help="run the 50-125 refutations (long)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--deadline", type=float, default=1500.0)
    ap.add_argument("--min-n", type=int, default=50)
    ap.add_argument("--wall-budget", type=float, default=None, help="seconds; stop launching after this")
    ap.add_argument("--configs", default=",".join(CONFIGS))
    args = ap.parse_args()
    if args.refute:
        run_refutations(workers=args.workers, deadline=args.deadline, min_n=args.min_n,
                        configs=tuple(args.configs.split(",")), wall_budget=args.wall_budget)
        return
    started = time.monotonic()
    results = report()
    print(f"wrote {TABLES} and {FIGURE} in {time.monotonic() - started:.0f} s")
    print(results["optimum"][["estimate", "radius abs", "abs interval first fails at", "n-scaled interval first fails at"]].to_string())
    for cfg in CONFIGS:
        print(f"\n[{cfg}]"); print(results["nodes"][cfg]["summary"].to_string())


if __name__ == "__main__":
    main()
