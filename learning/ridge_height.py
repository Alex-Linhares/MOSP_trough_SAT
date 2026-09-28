"""Is the ridge's *height* a function of the same quantity as its location?

Question (`reports/ml_nature_plan_3.md` §1 Q3, loop0004 item 10). §25 put the
hardness ridge -- the density at which the nodes to refute `optimum - 1` peak
at fixed `n` -- at cover excess `(n_ones - m) / n ≈ 2-2.4` for every product
ratio `m / n`, and noted (§25 (g)) that the ridge's height at fixed `n` climbs
one to one and a half decades per doubling of `m`. Is the height a function
of `(n, excess, m / n)`, and at fixed `n` of `m` alone, of the excess at the
peak, or of both? This module (a) assembles every series' interpolated peak
height from §11 (10-40), §16 (50-75), §25's ratio cells and §34/§35's 100
cell, (b) adds the cells the surface lacked -- Bernoulli `m = 4n` and `8n`,
where the excess-2 ridge sits below two customers per product and the fixed
generator cannot go, plus a finer `m = 2n` grid -- to see whether the height
keeps climbing with `m` or saturates, (c) fits candidate formulas for the
height against `(n, m)`, `(n, m/n)` and the peak excess, with leave-one-
series-out, leave-one-n-out and extrapolation errors, (d) tests whether the
whole surface collapses to `H(n, m) + S(excess)`, and (e) measures the
ridge's width per series.

Nothing here is a bound or a solver change; nothing is written to
`solutions/`. Generated instances are certified with `solve_mosp_exact` into
`learning/data/ensemble/solutions/` like the rest of the campaign; their rows
go to `learning/data/ensemble/results_height.csv` (manifest
`manifest_height.csv`), kept apart from the earlier result files so that
§10-§36 regenerate unchanged.

Usage:
    python -m learning.ridge_height --stage run --workers 16   # the m = 4n / 8n and finer 2n cells (~70 min)
    python -m learning.ridge_height --stage tables             # reports/ridge_height_tables.md, ~1 min
    python -m pytest tests/test_ridge_height.py -q
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.ensemble import ENSEMBLE_DIR, Cell, load_results, run, write_manifest
from learning.ridge_theory import cell_medians, load_frames, peak_table

RESULTS_HEIGHT_CSV = ENSEMBLE_DIR / "results_height.csv"
MANIFEST_HEIGHT_CSV = ENSEMBLE_DIR / "manifest_height.csv"
TABLES = Path("reports/ridge_height_tables.md")
SEED = 0
EXCESS_RIDGE = 2.4          # §25: the ridge's excess, calibrated at m = n

RATIO_LABELS = {0.125: "n/8", 0.25: "n/4", 0.5: "n/2", 1.0: "n", 2.0: "2n", 4.0: "4n", 8.0: "8n"}

# the new cells: realised customers per product `c` -> Bernoulli p = c / n
# `c` is nominal (p n); the generator repairs every empty column with one
# customer, so the realised col_mean is about c + exp(-c) and the excess-2.4
# ridge sits at nominal c ≈ 1.35 for m = 4n and ≈ 0.9 for m = 8n
FOUR_N = {40: (1.2, 1.4, 1.6, 1.8, 2.0, 2.4, 3.0), 50: (1.2, 1.4, 1.6, 1.8, 2.0, 2.4, 3.0),
          60: (1.2, 1.4, 1.6, 1.8, 2.0, 2.4, 3.0), 75: (1.2, 1.4, 1.6, 1.8, 2.0, 2.4)}
EIGHT_N = {50: (0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.45, 1.6, 1.8, 2.2),
           60: (0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.45, 1.6, 1.8, 2.2)}
TWO_N_FINER = {50: (1.75, 2.0, 2.25, 3.0), 60: (1.75, 2.0, 2.25, 3.0), 75: (1.5, 1.75, 2.25, 2.5)}
PER_CELL = {40: 50, 50: 50, 60: 50, 75: 20}
# held-out cells at n = 100 where the ridge is cheap: m = n/4 (ridge at col_mean ≈ 10.6,
# height ≈ 5 decades) and m = n/2 (≈ 5.8, ≈ 7 decades); fixed d and Bernoulli nominal c
HUNDRED_QUARTER = {"fixed": (6, 8, 9, 10, 11, 12, 14), "bernoulli": (7, 8, 9, 10, 12)}
HUNDRED_HALF = {"fixed": (4, 5, 6, 7, 8), "bernoulli": (4, 5, 6, 7)}
PER_CELL_100 = 30


def ratio_label(m: float, n: float) -> str:
    """§25's label extended to 4n and 8n."""
    r = m / n
    key = min(RATIO_LABELS, key=lambda k: abs(np.log(r / k)))
    return RATIO_LABELS[key]


def height_cells() -> tuple[list[Cell], dict[Cell, int]]:
    """Bernoulli cells at m = 4n (n = 40-75), 8n (50, 60) and a finer 2n grid
    (50-75), p = c / n rounded to four decimals, cheap (n ≤ 60) first and the
    n = 75 cells at 20 per cell; then the held-out n = 100 cells at m = n/4
    and n/2, both generators, 30 per cell."""
    cells: list[Cell] = []
    counts: dict[Cell, int] = {}

    def add(n: int, ratio: int, cs) -> None:
        for c in cs:
            cell = Cell("bernoulli", n, ratio * n, round(c / n, 4))
            cells.append(cell)
            counts[cell] = PER_CELL[n]

    for n in (60, 50):
        add(n, 8, EIGHT_N[n])
    for n in (60, 50, 40):
        add(n, 4, FOUR_N[n])
    for n in (60, 50):
        add(n, 2, TWO_N_FINER[n])
    add(75, 2, TWO_N_FINER[75])
    add(75, 4, FOUR_N[75])          # about three worker-minutes each
    for m, spec in ((25, HUNDRED_QUARTER), (50, HUNDRED_HALF)):
        for gen, params in spec.items():
            for c in params:
                cell = Cell(gen, 100, m, float(c) if gen == "fixed" else round(c / 100, 4))
                cells.append(cell)
                counts[cell] = PER_CELL_100
    return cells, counts


def run_height(workers: int = 12, csv: Path = RESULTS_HEIGHT_CSV) -> pd.DataFrame:
    cells, counts = height_cells()
    frame = run(cells, per_cell=50, workers=workers, csv=csv, instance_dir=None,
                deadline=120.0, solve_budget=600.0, counts=counts)
    write_manifest(frame, MANIFEST_HEIGHT_CSV)
    return frame



EFFECTIVE_CSV = ENSEMBLE_DIR / "height_effective_m.csv"


def effective_products(frame: pd.DataFrame, min_n: int = 15, csv: Path = EFFECTIVE_CSV) -> pd.DataFrame:
    """Per Bernoulli instance at n ≥ `min_n`: the products with at least two
    customers (`m_eff`), the ones with exactly one and the empty ones, by
    regenerating the instance from its cell and index. A product with one
    customer or none adds no edge to the MOSP graph and is removed by
    dominance, so `m_eff / n` is the ratio the search sees; the fixed
    generator has `m_eff = m` by construction. Cached in `csv`."""
    from learning.ensemble import generate

    sel = frame[(frame["generator"] == "bernoulli") & (frame["n"] >= min_n)]
    have = pd.read_csv(csv) if csv.exists() else pd.DataFrame(columns=["instance_name", "m_eff", "m_single", "m_empty"])
    todo = sel[~sel["instance_name"].isin(set(have["instance_name"]))]
    rows = []
    for r in todo.itertuples():
        inst = generate(Cell(r.generator, int(r.n), int(r.m), float(r.param)), int(r.index))
        sizes = np.asarray(inst.matrix).sum(axis=0)
        rows.append({"instance_name": r.instance_name, "m_eff": int((sizes >= 2).sum()),
                     "m_single": int((sizes == 1).sum()), "m_empty": int((sizes == 0).sum())})
    if rows:
        have = pd.concat([have, pd.DataFrame(rows)], ignore_index=True)
        have.to_csv(csv, index=False)
    return have


# ----------------------------------------------------------------------------
# (a) every series' peak height
# ----------------------------------------------------------------------------


def load_all(height_csv: Path = RESULTS_HEIGHT_CSV) -> pd.DataFrame:
    """§25's three result files plus this item's, with the extended ratio label."""
    frame = load_frames()
    extra = load_results(height_csv)
    if len(extra):
        from learning.ridge_theory import derive
        extra = extra.copy()
        extra["source"] = "height"
        extra = derive(extra)
        frame = pd.concat([frame, extra], ignore_index=True)
    frame["ratio_label"] = [ratio_label(m, n) for m, n in zip(frame["m"], frame["n"])]
    eff = effective_products(frame)
    frame = frame.merge(eff[["instance_name", "m_eff"]], on="instance_name", how="left")
    fixed = frame["generator"] == "fixed"
    frame.loc[fixed, "m_eff"] = frame.loc[fixed, "m"]
    return frame


def peak_heights(frame: pd.DataFrame, config: str = "default", min_n: int = 15) -> pd.DataFrame:
    """One row per (generator, ratio, n): the interpolated peak's height
    (median log10(1 + nodes) of the peak cell), its location, the excess and
    the optimum fraction there, and whether the height is a lower bound
    (censored median) or the peak sits at the grid's edge."""
    cells = cell_medians(frame, config)
    pk = peak_table(frame, cells, config, min_n=min_n, resamples=0)
    pk["m"] = (pk["r_exact"] * pk["n"]).round().astype(int)
    pk["log_r"] = np.log10(pk["r_exact"])
    pk["height"] = pk["peak_median_log_nodes"]
    pk["height_is_lower_bound"] = pk["peak_is_lower_bound"]
    pk["edge"] = ~pk["interior"]
    pk["config"] = config
    pk["kind"] = "cell median"
    if "m_eff" in frame:
        eff = frame.groupby(["generator", "ratio_label", "n", "param"])["m_eff"].median().rename("m_eff").reset_index()
        pk = pk.merge(eff, left_on=["generator", "ratio_label", "n", "peak_param"],
                      right_on=["generator", "ratio_label", "n", "param"], how="left").drop(columns=["param"])
    else:
        pk["m_eff"] = pk["m"]
    keep = ["config", "generator", "ratio_label", "n", "m", "m_eff", "r_exact", "log_r", "cells", "interior", "edge",
            "peak_col_mean", "height", "height_is_lower_bound", "excess", "excess_analytic", "opt_frac",
            "g_deg_mean", "col_mean", "kind"]
    return pk[keep].sort_values(["config", "generator", "r_exact", "n"]).reset_index(drop=True)


def hundred_cell(config: str = "default") -> dict:
    """§34's fixed `m = n`, `d = 3` cell at 100: its censored-normal location
    and 90% profile interval (§35's method, σ from the 75 cell), as a
    held-out height. `csearch` here is the pre-fix run (like every campaign
    `csearch` count below 100), `default` is fix-invariant."""
    from learning import rate_drift as rd

    cfg = "csearch-prefix" if config == "csearch" else config
    s = rd.series(cfg, 3.0, True)
    s75 = s[(s["n"] == 75) & ~s["censored"]]
    sigma = float(np.std(s75["log_nodes"]))
    loc = rd.cell_location(s, 100, sigma)
    return {"config": config, "generator": "fixed", "ratio_label": "n", "n": 100, "m": 100, "r_exact": 1.0,
            "log_r": 0.0, "height": loc["location"], "height_lo": loc["location_lo"],
            "height_hi": loc["location_hi"], "exact": loc["exact"], "censored": loc["censored"],
            "censored_median": loc["censored_median"], "kind": "location (censored MLE)"}


# ----------------------------------------------------------------------------
# (c) candidate formulas for the height
# ----------------------------------------------------------------------------

MODELS = {
    "n only": "a + b n",
    "n + log m": "a + b n + c log m",
    "n + m": "a + b n + c m",
    "n × log m": "a + b n + c log m + d n log m",
    "n·g(r) linear": "a + n (b + c log r)",
    "n·g(r) quadratic": "a + n (b + c log r + d log² r)",
    "n·g(c*) log clique": "a + n (b + c log(1 + 2.4 / r))",
    "n·g(r) + excess": "a + n (b + c log r) + e excess",
    "n·g(r) + n·excess": "a + n (b + c log r + e excess)",
    "n·g(c*) + n·excess": "a + n (b + c log(1 + 2.4 / r) + e excess)",
    "excess only": "a + b n + e excess",
    "n·excess only": "a + n (b + e excess)",
    "n·g(c_peak) measured": "a + n (b + c log c_peak), c_peak the measured peak col_mean",
    "n·g(r_eff) linear": "a + n (b + c log(m_eff / n)), m_eff the products with ≥ 2 customers",
    "n·g(r_eff) quadratic": "a + n (b + c log(m_eff / n) + d log²(m_eff / n))",
    "n·g(c*) + excess": "a + n (b + c log(1 + 2.4 / r)) + e excess",
    "n·g(r_eff) + excess": "a + n (b + c log(m_eff / n)) + e excess",
    "n·g(r_eff) + n·excess": "a + n (b + c log(m_eff / n) + e excess)",
}


def design(model: str, n, m, ex, cpk=None, meff=None) -> np.ndarray:
    n = np.asarray(n, float)
    m = np.asarray(m, float)
    ex = np.asarray(ex, float)
    cpk = np.asarray(cpk, float) if cpk is not None else np.full_like(n, np.nan)
    meff = np.asarray(meff, float) if meff is not None else m
    lr = np.log10(m / n)
    lm = np.log10(m)
    lc = np.log10(1.0 + EXCESS_RIDGE * n / m)
    one = np.ones_like(n)
    cols = {
        "n only": [one, n],
        "n + log m": [one, n, lm],
        "n + m": [one, n, m],
        "n × log m": [one, n, lm, n * lm],
        "n·g(r) linear": [one, n, n * lr],
        "n·g(r) quadratic": [one, n, n * lr, n * lr ** 2],
        "n·g(c*) log clique": [one, n, n * lc],
        "n·g(r) + excess": [one, n, n * lr, ex],
        "n·g(r) + n·excess": [one, n, n * lr, n * ex],
        "n·g(c*) + n·excess": [one, n, n * lc, n * ex],
        "excess only": [one, n, ex],
        "n·excess only": [one, n, n * ex],
        "n·g(c_peak) measured": [one, n, n * np.log10(cpk)],
        "n·g(r_eff) linear": [one, n, n * np.log10(meff / n)],
        "n·g(r_eff) quadratic": [one, n, n * np.log10(meff / n), n * np.log10(meff / n) ** 2],
        "n·g(c*) + excess": [one, n, n * lc, ex],
        "n·g(r_eff) + excess": [one, n, n * np.log10(meff / n), ex],
        "n·g(r_eff) + n·excess": [one, n, n * np.log10(meff / n), n * ex],
    }[model]
    return np.column_stack(cols)


def _X(model: str, pts: pd.DataFrame) -> np.ndarray:
    cpk = pts["peak_col_mean"] if "peak_col_mean" in pts else None
    meff = pts["m_eff"] if "m_eff" in pts else None
    return design(model, pts["n"], pts["m"], pts["excess"], cpk, meff)


def fit(model: str, pts: pd.DataFrame) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(_X(model, pts), pts["height"].to_numpy(float), rcond=None)
    return beta


def predict(model: str, beta: np.ndarray, pts: pd.DataFrame) -> np.ndarray:
    return _X(model, pts) @ beta


def fit_points(peaks: pd.DataFrame, generator: str | None = None) -> pd.DataFrame:
    """The points a formula is fitted on: exact heights (no censored median)."""
    pts = peaks[~peaks["height_is_lower_bound"].astype(bool)]
    if generator is not None:
        pts = pts[pts["generator"] == generator]
    return pts.reset_index(drop=True)


def heldout(model: str, pts: pd.DataFrame, scheme: str) -> np.ndarray:
    """Held-out predictions: `loso` leaves one (generator, ratio) series out,
    `lono` one n out, `extrap75` trains on n ≤ 60 and predicts n = 75,
    `extrap100` trains on n ≤ 75 and predicts the exact heights at n = 100
    (NaN elsewhere)."""
    out = np.full(len(pts), np.nan)
    if scheme == "loso":
        groups = pts["generator"] + ":" + pts["ratio_label"]
    elif scheme == "lono":
        groups = pts["n"].astype(str)
    elif scheme in ("extrap75", "extrap100"):
        at = 75 if scheme == "extrap75" else 100
        test = pts["n"].to_numpy() == at
        train = pts["n"].to_numpy() <= at - 15
        if test.any() and train.sum() >= 4:
            out[test] = predict(model, fit(model, pts[train]), pts[test])
        return out
    else:
        raise ValueError(scheme)
    for g in groups.unique():
        test = (groups == g).to_numpy()
        train = pts[~test]
        if len(train) >= design(model, [1], [1], [1]).shape[1] + 1:
            out[test] = predict(model, fit(model, train), pts[test])
    return out


def _err(y, yhat) -> dict:
    d = np.asarray(yhat, float) - np.asarray(y, float)
    d = d[np.isfinite(d)]
    if not len(d):
        return {"rmse": np.nan, "mae": np.nan, "max": np.nan}
    return {"rmse": float(np.sqrt(np.mean(d ** 2))), "mae": float(np.mean(np.abs(d))),
            "max": float(np.max(np.abs(d)))}


def model_table(peaks: pd.DataFrame, generator: str | None, hundred: dict | None = None,
                min_n: int = 15) -> pd.DataFrame:
    """One row per model: parameters, in-sample and held-out errors on the
    exact peaks at n ≤ 75 (n = 100 is never fitted and never a held-out fold:
    the `extrap100` columns read the n ≤ 75 fit at the certified 100 cells),
    and the n ≤ 75 fit's prediction at the fixed m = n cell against §35's
    location interval."""
    pts = fit_points(peaks, generator)
    pts = pts[pts["n"] >= min_n].reset_index(drop=True)
    fit_pts = pts[pts["n"] <= 75].reset_index(drop=True)      # n = 100 is held out everywhere
    rows = []
    for model, text in MODELS.items():
        beta = fit(model, fit_pts)
        row = {"model": model, "formula": text, "params": len(beta), "points": len(fit_pts),
               "coef": ", ".join(f"{b:.4g}" for b in beta)}
        row.update({f"in_{k}": v for k, v in _err(fit_pts["height"], predict(model, beta, fit_pts)).items()})
        for scheme in ("loso", "lono", "extrap75"):      # held out within n ≤ 75
            row.update({f"{scheme}_{k}": v for k, v in _err(fit_pts["height"], heldout(model, fit_pts, scheme)).items()})
        row.update({f"extrap100_{k}": v for k, v in _err(pts["height"], heldout(model, pts, "extrap100")).items()})
        h100 = heldout(model, pts, "extrap100")
        row["extrap100_signed"] = ", ".join(f"{lab} {d:+.2f}" for lab, d in
                                            zip(pts.loc[np.isfinite(h100), "generator"].str[0] + ":" + pts.loc[np.isfinite(h100), "ratio_label"],
                                                (h100 - pts["height"].to_numpy(float))[np.isfinite(h100)]))
        if hundred is not None and generator in ("fixed", None):
            at_n = pts[(pts["ratio_label"] == "n") & (pts["generator"] == "fixed")]
            h = pd.DataFrame([{"n": 100, "m": 100, "m_eff": 100, "excess": float(at_n["excess"].median()),
                               "peak_col_mean": float(at_n["peak_col_mean"].median())}])
            p = float(predict(model, beta, h)[0])
            row["pred_100"] = p
            row["loc_100"] = hundred["height"]
            row["inside_100"] = bool(hundred["height_lo"] <= p <= hundred["height_hi"])
            row["err_100"] = p - hundred["height"]
        rows.append(row)
    return pd.DataFrame(rows)


def fixed_n_table(peaks: pd.DataFrame, by: str = "m") -> pd.DataFrame:
    """Heights by ratio at fixed (generator, n) and the increment per doubling
    of `by` (`m`, or `m_eff` = products with two or more customers) between
    neighbouring ratios: does the climb saturate?"""
    rows = []
    for (gen, n), g in peaks.groupby(["generator", "n"]):
        g = g.sort_values("r_exact")
        row = {"generator": gen, "n": int(n), "ratios": len(g)}
        for r in g.itertuples():
            tag = f"h[{r.ratio_label}]"
            row[tag] = r.height
            row[tag + " lb"] = bool(r.height_is_lower_bound)
            if by == "m_eff":
                row[f"m_eff/n[{r.ratio_label}]"] = float(r.m_eff) / n
        labs = list(g["ratio_label"])
        hs = list(g["height"])
        lrs = list(np.log2(g[by].to_numpy(float) / n))
        for i in range(1, len(g)):
            step = lrs[i] - lrs[i - 1]
            row[f"Δ/doubling {labs[i-1]}→{labs[i]}"] = (hs[i] - hs[i - 1]) / step if step > 0 else np.nan
        if len(g) >= 3:
            slope = np.polyfit(np.log10(g[by].to_numpy(float)), g["height"], 1)[0]
            row[f"slope_log_height_per_log_{by}"] = float(slope)
        rows.append(row)
    return pd.DataFrame(rows)


def excess_partial(peaks: pd.DataFrame, generator: str, base: str = "n·g(r) linear") -> dict:
    """Does the excess at the peak explain what (n, m) leaves? The residual of
    the base model against the peak excess: slope, correlation, and the
    held-out gain of adding the term."""
    pts = fit_points(peaks, generator)
    pts = pts[pts["n"] <= 75].reset_index(drop=True)          # n = 100 is held out everywhere
    res = pts["height"] - predict(base, fit(base, pts), pts)
    ex = pts["excess"].to_numpy(float)
    slope, icpt = np.polyfit(ex, res, 1)
    rho = float(np.corrcoef(ex, res)[0, 1]) if np.std(ex) > 0 else np.nan
    plus = {"n·g(r) linear": ("n·g(r) + excess", "n·g(r) + n·excess"),
            "n·g(c*) log clique": ("n·g(c*) + excess", "n·g(c*) + n·excess"),
            "n·g(r_eff) linear": ("n·g(r_eff) + excess", "n·g(r_eff) + n·excess")}[base]
    e_base = _err(pts["height"], heldout(base, pts, "loso"))["rmse"]
    e_ex = _err(pts["height"], heldout(plus[0], pts, "loso"))["rmse"]
    e_nex = _err(pts["height"], heldout(plus[1], pts, "loso"))["rmse"]
    return {"generator": generator, "base": base, "points": len(pts), "excess_range": f"{ex.min():.2f}–{ex.max():.2f}",
            "residual_sd": float(np.std(res)), "slope_per_unit_excess": float(slope), "corr": rho,
            "loso_rmse_base": e_base, "loso_rmse_plus_excess": e_ex, "loso_rmse_plus_n_excess": e_nex,
            "gain_decades": float(e_base - min(e_ex, e_nex))}


# ----------------------------------------------------------------------------
# (d) does the surface collapse to H(n, m) + S(x)?
# ----------------------------------------------------------------------------


def collapse_stats(x: np.ndarray, y: np.ndarray, w: np.ndarray, series: np.ndarray, bins: int = 10) -> dict:
    """Bin points by quantiles of `x`; `dispersion` is the weight-averaged
    range over bins of the per-series medians of `y` (bins with two or more
    series), `r2` the share of the weighted variance of `y` a function of the
    bin alone explains."""
    x, y, w = np.asarray(x, float), np.asarray(y, float), np.asarray(w, float)
    series = np.asarray(series)
    edges = np.quantile(x, np.linspace(0, 1, bins + 1))
    b = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, bins - 1)
    tot = np.sum(w * (y - np.average(y, weights=w)) ** 2)
    within = 0.0
    disp_num = disp_den = 0.0
    for k in np.unique(b):
        sel = b == k
        mu = np.average(y[sel], weights=w[sel])
        within += np.sum(w[sel] * (y[sel] - mu) ** 2)
        meds = pd.Series(y[sel]).groupby(series[sel]).median()
        if len(meds) >= 2:
            disp_num += (meds.max() - meds.min()) * w[sel].sum()
            disp_den += w[sel].sum()
    return {"dispersion": disp_num / disp_den if disp_den else np.nan,
            "r2": 1.0 - within / tot if tot > 0 else np.nan, "bins": int(len(np.unique(b)))}


def surface_collapse(frame: pd.DataFrame, peaks: pd.DataFrame, model: str = "n·g(r) quadratic",
                     config: str = "default", sizes=(50, 60, 75), bins: int = 10,
                     candidates=("excess", "col_mean", "g_deg_mean", "branch")) -> pd.DataFrame:
    """At each n: cell medians of log10(1 + nodes) across every series, raw,
    with each series' own measured peak height subtracted (`minus peak`: the
    shape alone) and with the fitted height H(n, m) subtracted (`minus
    H(n, m)`: shape and formula together), binned by log10 of a candidate
    coordinate; `collapse_stats` gives dispersion and r²."""
    cells = cell_medians(frame, config)
    cells = cells[cells["n"].isin(sizes) & ~cells["median_is_lower_bound"]].copy()
    cells["ratio_label"] = [ratio_label(m, n) for m, n in zip(cells["m"], cells["n"])]
    cells["series"] = cells["generator"] + ":" + cells["ratio_label"]
    pk = peaks[peaks["config"] == config]
    height = {(r.generator, r.ratio_label, int(r.n)): r.height for r in pk.itertuples()}
    cells["peak"] = [height.get((g, l, int(n)), np.nan) for g, l, n in zip(cells["generator"], cells["ratio_label"], cells["n"])]
    for gen in ("fixed", "bernoulli"):
        pts = fit_points(pk, gen)
        beta = fit(model, pts)
        sel = cells["generator"] == gen
        cells.loc[sel, "H"] = predict(model, beta, cells.loc[sel, ["n", "m"]].assign(excess=0.0))
    cells = cells[cells["peak"].notna()]
    rows = []
    for n, g in cells.groupby("n"):
        for cand in candidates:
            x = np.log10(g[cand].to_numpy(float))
            for what, y in (("raw", g["median_log_nodes"]), ("minus peak", g["median_log_nodes"] - g["peak"]),
                            ("minus H(n,m)", g["median_log_nodes"] - g["H"])):
                st = collapse_stats(x, y.to_numpy(float), g["instances"].to_numpy(float), g["series"].to_numpy(), bins)
                rows.append({"n": int(n), "candidate": cand, "y": what, "cells": len(g),
                             "series": int(g["series"].nunique()), **st})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# (e) the ridge's width per series
# ----------------------------------------------------------------------------


def _crossings(x: np.ndarray, y: np.ndarray, level: float, i_peak: int) -> tuple[float, float, bool, bool]:
    """Where the piecewise-linear profile crosses `level` left and right of the
    peak; the grid edge (and a censored flag) when it never does."""
    lo, lo_edge = x[0], True
    for i in range(i_peak, 0, -1):
        if y[i - 1] < level <= y[i]:
            lo = x[i - 1] + (level - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1])
            lo_edge = False
            break
    hi, hi_edge = x[-1], True
    for i in range(i_peak, len(x) - 1):
        if y[i + 1] < level <= y[i]:
            hi = x[i] + (y[i] - level) * (x[i + 1] - x[i]) / (y[i] - y[i + 1])
            hi_edge = False
            break
    return float(lo), float(hi), lo_edge, hi_edge


def width_table(frame: pd.DataFrame, config: str = "default", min_n: int = 50,
                drops=(0.5, 1.0)) -> pd.DataFrame:
    """Per series: the width in decades of excess over which the cell median
    stays within `drop` decades of the peak, and its two halves."""
    cells = cell_medians(frame, config)
    rows = []
    for (gen, lab, n), g in cells.groupby(["generator", "ratio_label", "n"]):
        if n < min_n or len(g) < 3:
            continue
        g = g.sort_values("excess")
        x = np.log10(g["excess"].to_numpy(float))
        y = g["median_log_nodes"].to_numpy(float)
        i = int(np.argmax(y))
        row = {"generator": gen, "ratio_label": lab, "n": int(n), "m": int(g["m"].iloc[0]), "cells": len(g),
               "peak_excess": float(10 ** x[i]), "height": float(y[i]),
               "peak_at_edge": i in (0, len(g) - 1)}
        for d in drops:
            lo, hi, le, he = _crossings(x, y, y[i] - d, i)
            row[f"width_{d:g}"] = hi - lo
            row[f"left_{d:g}"] = x[i] - lo
            row[f"right_{d:g}"] = hi - x[i]
            row[f"edge_{d:g}"] = le or he
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def tables(out: Path = TABLES, verbose: bool = True) -> dict:
    t0 = time.time()
    frame = load_all()
    res: dict = {}
    parts = ["# Ridge height tables (§37)\n",
             "*Generated by `python -m learning.ridge_height --stage tables`. Heights are the "
             "censoring-aware median of log10(1 + nodes) at the interpolated peak cell of each "
             "(generator, m / n, n) series, `default` configuration unless said; the new Bernoulli "
             "m = 4n / 8n and finer 2n cells are in `results_height.csv`.*\n"]
    src = frame.groupby("source").size()
    parts.append("## Instances per source\n\n" + _md(src.reset_index(name="instances")) + "\n")
    for config in ("default", "csearch"):
        peaks = peak_heights(frame, config)
        hundred = hundred_cell(config)
        res[f"peaks_{config}"] = peaks
        res[f"hundred_{config}"] = hundred
        parts.append(f"## Peaks, `{config}`\n\n" + _md(peaks.drop(columns=["config", "kind"])) + "\n")
        parts.append(f"The 100 cell (`{config}`): location {hundred['height']:.2f} "
                     f"[{hundred['height_lo']:.2f}, {hundred['height_hi']:.2f}], {hundred['exact']} exact + "
                     f"{hundred['censored']} censored, censored median {hundred['censored_median']:.2f}.\n")
        fx = fixed_n_table(peaks)
        res[f"fixed_n_{config}"] = fx
        parts.append(f"## Height against m at fixed n, `{config}`\n\n" + _md(fx) + "\n")
        fxe = fixed_n_table(peaks, by="m_eff")
        res[f"fixed_n_eff_{config}"] = fxe
        parts.append(f"## Height against m_eff (products with ≥ 2 customers) at fixed n, `{config}`\n\n" + _md(fxe) + "\n")
        for gen in ("fixed", "bernoulli", None):
            name = gen or "both generators pooled"
            mt = model_table(peaks, gen, hundred)
            res[f"models_{config}_{name}"] = mt
            parts.append(f"## Formulas, `{config}`, {name} (n = 15–75, exact heights)\n\n" + _md(mt) + "\n")
            mt50 = model_table(peaks, gen, hundred, min_n=50)
            res[f"models50_{config}_{name}"] = mt50
            parts.append(f"## Formulas, `{config}`, {name}, n = 50–75 only\n\n" + _md(mt50) + "\n")
            if gen is None:
                continue
            for base in ("n·g(r) linear", "n·g(c*) log clique", "n·g(r_eff) linear"):
                ep = excess_partial(peaks, gen, base)
                res[f"excess_{config}_{gen}_{base}"] = ep
                parts.append(f"Excess partial, {gen}, base `{base}`: " +
                             ", ".join(f"{k} = {v:.3g}" if isinstance(v, float) else f"{k} = {v}"
                                       for k, v in ep.items()) + "\n")
        if config == "default":
            col = surface_collapse(frame, peaks, config=config)
            res["collapse"] = col
            parts.append("## Surface collapse at n = 50, 60, 75 (cell medians, all series)\n\n" + _md(col) + "\n")
            wd = width_table(frame, config)
            res["width"] = wd
            parts.append("## Ridge width per series (decades of excess)\n\n" + _md(wd) + "\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts))
    if verbose:
        print(f"wrote {out} in {time.time() - t0:.0f} s")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="tables", choices=["run", "tables"])
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    if a.stage == "run":
        run_height(a.workers)
    else:
        tables()
