"""Does the optimum concentrate on random instances? (`reports/ml_nature_plan.md` §2.5)

The question. At fixed generator parameters `(n, m, p)`, is the variance of
the optimum small relative to its mean? If it is, the optimum of a random
instance is essentially a function of the parameters, and a formula for
`E[opt](n, m, p)` describes the *problem* rather than the corpus. The plan's
kill criterion: a coefficient of variation above 0.2 up to `n = 40`.

The data is the campaign of `learning.ensemble` (`reports/ml_nature.md` §9,
§10): 252 cells `(generator, n, m, param)` x 150 instances, `n` 10..40,
`m` in `{n, 2n}`, the fixed customers-per-product generator at `d = 2..10`
and the Bernoulli generator at `p = 0.025..0.5`, every instance certified,
with the 49 features and the isomorphism certificates.

What the module computes (`python -m learning.concentration`):

- `cell_stats`: per cell the mean, variance, standard deviation and
  coefficient of variation (CV) of the optimum, the share at the modal value,
  raw and per MOSP-graph isomorphism class (`--per-class`), plus the cell
  means of the sandwich invariants and of the optimum-minus-treewidth
  residual used below.
- `kill_verdict`: the largest CV at each `n`, the cells above 0.2, and
  whether any remain at `n = 40`.
- `cv_scaling`: CV and standard deviation against `n` at fixed
  `(generator, m/n, param)`, as power-law exponents; the cells are split at
  the giant-component threshold of the random intersection graph, because
  below it the optimum is a small integer whose CV cannot fall.
- `linearity`: `E[opt]` against `n` at fixed parameter -- slope, intercept,
  r² of a line, and the exponent of a power law -- to compare with what is
  known for `G(n, p)`: pathwidth (and treewidth) linear in `n` above the
  giant-component threshold, bounded below it. The slope is then read as a
  function of the nominal mean degree of the MOSP graph, which is what the
  two generators and two `m/n` ratios share.
- `formula`: `learning.formula_search`'s enumerated monomial and pair search
  over features derived from the *generator parameters alone* -- `n`, `m`,
  the nominal `p` (for the fixed generator `d / n`), the nominal customers
  per product `d = p·n`, products per customer `k = p·m`, the random
  intersection graph's edge probability `q = 1 − (1 − p²)^m` and expected
  degree `(n − 1)·q` -- fitted to the 252 cell means, with folds that hold
  out whole sizes `n` (the honest split for a formula in `n`), a nested
  protocol (selection inside the training sizes), and an extrapolation test
  (fit on `n ≤ 30`, score on 35 and 40, previewing item 06). The residual of
  the winning formula is reported per instance, with the counts below and
  above the optimum, because **a formula is not a bound**.
- `sandwich`: §5's `g_degeneracy + 1 ≤ optimum ≤ bw_rcm + 1` on the ensemble,
  where the optimum sits between them (λ), and whether λ concentrates at ½
  as `n` grows or drifts with density.
- `pw_minus_tw`: `optimum − (tw_min_fill + 1)` against sparsity and `n`.
  Since `tw_min_fill` is an upper bound on treewidth and degeneracy a lower
  bound, `optimum − tw_min_fill − 1 ≤ pw − tw ≤ optimum − g_degeneracy − 1`
  brackets how far pathwidth exceeds treewidth on these instances with two
  proved quantities, and the table reports both ends.
- `figure`: `reports/figures/concentration.png`.

Baseline: the CV of a binomial-like quantity, `1/√n`; for `E[opt]`, the
constant per-cell mean (which the formula must beat when whole sizes are
held out) and the linear-in-`n` law of `G(n, p)` above the threshold.

Nothing here is a bound, nothing touches `_lower_bound` or any solver
default, and nothing is written to `solutions/`.

Usage:
    python -m learning.concentration                      # tables + figure, ~30 s
    python -m learning.concentration --per-class          # one row per isomorphism class per cell
    python -m learning.concentration --no-figure --no-nested   # the quick version
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from learning.ensemble import RESULTS_CSV
from learning.formula_search import (
    _lad_fit_linear,
    evaluate_terms,
    fit_term_lad,
    format_term,
    pair_search,
    sandwich_table,
    search,
)
from learning.hardness_map import SERIES, load as load_map, series_label
from learning.study_optimum import _scores

FIGURE = Path("reports/figures/concentration.png")
TABLES = Path("reports/concentration_tables.md")
CV_KILL = 0.2
GIANT_DEGREE = 1.0          # nominal mean degree (n − 1)·q; kept in the tables for reference
LCC_SUB, LCC_SUPER = 0.5, 0.95   # realised largest-component fraction: sub / critical / super
NOMINAL = ("n", "m", "p_nom", "d_nom", "k_nom", "q_nom", "deg_nom")
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]


# ----------------------------------------------------------------------------
# frame preparation
# ----------------------------------------------------------------------------


def nominal_features(n, m, generator, param) -> dict[str, np.ndarray]:
    """Features of the generator parameters alone, no graph features.

    `p_nom` is the Bernoulli `p`, or `d / n` for the fixed generator (the
    entry probability that gives `d` customers per product in expectation);
    `d_nom = p·n` customers per product; `k_nom = p·m` products per customer;
    `q_nom = 1 − (1 − p²)^m` is the edge probability of the random
    intersection graph `G(n, m, p)`; `deg_nom = (n − 1)·q_nom` its expected
    degree. The giant-component threshold of the MOSP graph is `deg_nom ≈ 1`.
    """
    n = np.asarray(n, dtype=float)
    m = np.asarray(m, dtype=float)
    param = np.asarray(param, dtype=float)
    fixed = np.asarray(generator) == "fixed"
    p = np.where(fixed, param / n, param)
    q = 1.0 - (1.0 - p ** 2) ** m
    return {"n": n, "m": m, "p_nom": p, "d_nom": p * n, "k_nom": p * m,
            "q_nom": q, "deg_nom": (n - 1) * q}


def prepare(frame: pd.DataFrame) -> pd.DataFrame:
    """Add the nominal features, λ, and the two ends of the pw − tw bracket."""
    out = frame.copy()
    for k, v in nominal_features(out["n"], out["m"], out["generator"], out["param"]).items():
        out[k] = v
    d = out["g_degeneracy"].astype(float)
    bw = out["bw_rcm"].astype(float)
    out["forced"] = bw <= d
    with np.errstate(divide="ignore", invalid="ignore"):
        lam = (out["optimum"] - 1 - d) / (bw - d)
    out["lam"] = np.where(out["forced"], np.nan, lam)
    out["res_tw"] = out["optimum"] - out["tw_min_fill"] - 1     # ≤ pw − tw
    out["tw_ub"] = out[["tw_min_fill", "tw_min_degree"]].min(axis=1)
    out["res_tw2"] = out["optimum"] - out["tw_ub"] - 1           # ≤ pw − tw, tighter
    out["res_deg"] = out["optimum"] - out["g_degeneracy"] - 1   # ≥ pw − tw
    out["series"] = [series_label(g, r) for g, r in zip(out["generator"], out["ratio"])]
    return out


def load(csv: Path = RESULTS_CSV, per_class: bool = False) -> pd.DataFrame:
    return prepare(load_map(csv, "default", per_class=per_class))


# ----------------------------------------------------------------------------
# per-cell statistics and the kill criterion
# ----------------------------------------------------------------------------


def cell_stats(frame: pd.DataFrame) -> pd.DataFrame:
    """One row per cell: moments of the optimum and the cell means used later."""
    rows = []
    for (gen, ratio, n, param), g in frame.groupby(["generator", "ratio", "n", "param"]):
        opt = g["optimum"].to_numpy(dtype=float)
        mean = opt.mean()
        std = opt.std(ddof=1) if len(opt) > 1 else 0.0
        counts = pd.Series(opt).value_counts()
        row = {
            "generator": gen, "ratio": int(ratio), "n": int(n), "param": float(param),
            "series": series_label(gen, ratio),
            "instances": len(g),
            "classes": g["graph_cert"].nunique() if "graph_cert" in g else len(g),
            "mean": mean, "var": std ** 2, "std": std,
            "cv": std / mean if mean > 0 else 0.0,
            "min": opt.min(), "max": opt.max(),
            "mode_share": float(counts.iloc[0] / len(opt)),
            "opt_frac": mean / n,
            "col_mean": float(g["col_mean"].median()),
            "connected_share": float(g["connected"].mean()),
            "lcc_frac": float(g["g_largest_comp_frac"].mean()),
            "complete_share": float(g["complete_graph"].mean()) if "complete_graph" in g else np.nan,
            "m": int(g["m"].iloc[0]),
            **{c: float(g[c].iloc[0]) for c in NOMINAL if c not in ("n", "m")},
            "mean_deg_plus1": float(g["g_degeneracy"].mean() + 1),
            "mean_bw_plus1": float(g["bw_rcm"].mean() + 1),
            "mean_tw_plus1": float(g["tw_min_fill"].mean() + 1),
            "forced_share": float(g["forced"].mean()),
            "lam_mean": float(g["lam"].mean()) if g["lam"].notna().any() else np.nan,
            "lam_std": float(g["lam"].std()) if g["lam"].notna().sum() > 1 else np.nan,
            "res_tw_mean": float(g["res_tw"].mean()),
            "res_tw_pos": float((g["res_tw"] > 0).mean()),
            "res_tw_neg": float((g["res_tw"] < 0).mean()),
            "res_deg_mean": float(g["res_deg"].mean()),
        }
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["generator", "ratio", "param", "n"]).reset_index(drop=True)


def matrix(cells: pd.DataFrame, generator: str, ratio: int, stat: str = "cv") -> pd.DataFrame:
    """`param` x `n` table of one statistic for one series."""
    sub = cells[(cells["generator"] == generator) & (cells["ratio"] == ratio)]
    return sub.pivot(index="param", columns="n", values=stat)


def kill_verdict(cells: pd.DataFrame, threshold: float = CV_KILL) -> dict:
    """The plan's kill: CV above `threshold` up to n = 40.

    Reports the maximum CV per `n`, the number of cells above the threshold
    per `n` and which series they belong to, and fires only if a cell at the
    largest `n` is still above it.
    """
    by_n = cells.groupby("n")["cv"]
    n_max = int(cells["n"].max())
    above = cells[cells["cv"] > threshold]
    per_n = pd.DataFrame({
        "max_cv": by_n.max(),
        "median_cv": by_n.median(),
        "cells_above": above.groupby("n").size().reindex(by_n.max().index, fill_value=0),
        "cells": by_n.size(),
    }).reset_index()
    at_max = above[above["n"] == n_max]
    supercritical = above[above["lcc_frac"] >= LCC_SUPER]
    return {
        "threshold": threshold,
        "per_n": per_n,
        "cells_above_total": int(len(above)),
        "cells_above_at_n_max": int(len(at_max)),
        "series_above": sorted(above["series"].unique().tolist()),
        "cells_above_supercritical": int(len(supercritical)),
        "max_lcc_frac_above": float(above["lcc_frac"].max()) if len(above) else float("nan"),
        "kill_fires": bool(len(at_max) > 0),
    }


# ----------------------------------------------------------------------------
# how the CV and the mean scale with n at fixed parameter
# ----------------------------------------------------------------------------


def _loglog_slope(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Slope and r² of log y against log x over the points with y > 0."""
    keep = (np.asarray(y) > 0) & (np.asarray(x) > 0)
    if keep.sum() < 3:
        return float("nan"), float("nan")
    lx, ly = np.log(np.asarray(x)[keep]), np.log(np.asarray(y)[keep])
    b, a = np.polyfit(lx, ly, 1)
    pred = a + b * lx
    ss = ((ly - ly.mean()) ** 2).sum()
    r2 = 1 - ((ly - pred) ** 2).sum() / ss if ss > 0 else float("nan")
    return float(b), float(r2)


def regime_of(cell) -> str:
    """`complete` if the cell's mean optimum is within 2% of n; otherwise by
    the realised largest-component fraction of the MOSP graph: `sub` below
    0.5, `critical` up to 0.95, `super` above. Realised, not nominal, because
    the nominal degree `(n − 1)·q` overstates the branching of a union of
    cliques and misplaces the threshold."""
    if cell["opt_frac"] >= 0.98:
        return "complete"
    if cell["lcc_frac"] < LCC_SUB:
        return "sub"
    if cell["lcc_frac"] < LCC_SUPER:
        return "critical"
    return "super"


def cv_scaling(cells: pd.DataFrame, min_n: int = 15) -> pd.DataFrame:
    """Per `(generator, m/n, param)`: CV and std against n as power laws.

    `cv_exp` is the exponent of `CV ∝ n^cv_exp` (−1/2 is the binomial
    baseline, −1 is a standard deviation that does not grow); `std_exp` the
    exponent of `std ∝ n^std_exp`. `regime` is `regime_of` the cell at the
    largest `n`.
    """
    rows = []
    for (gen, ratio, param), g in cells.groupby(["generator", "ratio", "param"]):
        g = g[g["n"] >= min_n].sort_values("n")
        if len(g) < 3:
            continue
        cv_exp, cv_r2 = _loglog_slope(g["n"], g["cv"])
        std_exp, _ = _loglog_slope(g["n"], g["std"])
        last = g.iloc[-1]
        regime = regime_of(last)
        rows.append({"generator": gen, "ratio": int(ratio), "param": float(param),
                     "series": series_label(gen, ratio), "regime": regime,
                     "deg_nom_at_n_max": float(last["deg_nom"]), "lcc_frac_at_n_max": float(last["lcc_frac"]),
                     "cv_at_n_min": float(g.iloc[0]["cv"]), "cv_at_n_max": float(last["cv"]),
                     "std_at_n_min": float(g.iloc[0]["std"]), "std_at_n_max": float(last["std"]),
                     "cv_exp": cv_exp, "cv_r2": cv_r2, "std_exp": std_exp})
    return pd.DataFrame(rows)


def linearity(cells: pd.DataFrame, min_n: int = 15) -> pd.DataFrame:
    """`E[opt]` against n at fixed `(generator, m/n, param)`.

    A line `mean ≈ a + b·n` (slope, intercept, r², RMS residual in stacks) and
    a power law `mean ∝ n^γ`; `regime` is `regime_of` the cell at the largest `n`. Above the
    giant-component threshold the `G(n, p)` result is linear growth; below
    it, bounded (here: does the slope vanish, and is γ well under 1).
    """
    rows = []
    for (gen, ratio, param), g in cells.groupby(["generator", "ratio", "param"]):
        g = g[g["n"] >= min_n].sort_values("n")
        if len(g) < 3:
            continue
        n = g["n"].to_numpy(dtype=float)
        y = g["mean"].to_numpy(dtype=float)
        b, a = np.polyfit(n, y, 1)
        pred = a + b * n
        ss = ((y - y.mean()) ** 2).sum()
        r2 = 1 - ((y - pred) ** 2).sum() / ss if ss > 0 else float("nan")
        gamma, _ = _loglog_slope(n, y)
        last = g.iloc[-1]
        regime = regime_of(last)
        rows.append({"generator": gen, "ratio": int(ratio), "param": float(param),
                     "series": series_label(gen, ratio), "regime": regime,
                     "deg_nom_at_n_max": float(last["deg_nom"]), "lcc_frac_at_n_max": float(last["lcc_frac"]),
                     "mean_at_n_min": float(y[0]), "mean_at_n_max": float(y[-1]),
                     "slope": float(b), "intercept": float(a), "r2": float(r2),
                     "rms": float(np.sqrt(((y - pred) ** 2).mean())), "gamma": gamma,
                     "opt_frac_at_n_max": float(last["opt_frac"])})
    return pd.DataFrame(rows)


def slope_by_degree(lin: pd.DataFrame) -> pd.DataFrame:
    """For the fixed generator (whose nominal degree does not change with n),
    the slope of `E[opt]` in n against the nominal mean degree `β·d·(d − 1)`
    (β = m / n), both ratios together, sorted by degree. Whether the two
    ratios fall on one curve is read off the table and its Spearman ρ."""
    sub = lin[(lin["generator"] == "fixed") & (lin["regime"] != "complete")].copy()
    sub["beta_d_d1"] = sub["ratio"] * sub["param"] * (sub["param"] - 1)
    sub = sub.sort_values("beta_d_d1")
    return sub[["series", "param", "beta_d_d1", "deg_nom_at_n_max", "slope", "intercept", "r2"]].reset_index(drop=True)


# ----------------------------------------------------------------------------
# E[opt](n, m, p): enumerated search over the generator parameters alone
# ----------------------------------------------------------------------------


def _n_folds(n: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    """Leave-one-size-out: every distinct n is a held-out fold."""
    folds = []
    for value in np.unique(n):
        test = n == value
        folds.append((~test, test))
    return folds


def _values(cells: pd.DataFrame) -> dict[str, np.ndarray]:
    return {c: cells[c].to_numpy(dtype=float) for c in NOMINAL}


def formula(cells: pd.DataFrame, frame: pd.DataFrame, nested: bool = True, workers: int = 1) -> dict:
    """The enumerated search of `learning.formula_search` on the 252 cell means.

    Target: the cell mean of the optimum. Features: `NOMINAL`, from the
    generator parameters alone. Folds: leave-one-size-out over the seven `n`.
    Returns the leading monomials and pairs (constants fitted by least
    absolute deviation on all cells), the nested score (the search rerun on
    the six training sizes, its winner scored on the held-out size), an
    extrapolation test (fit on n ≤ 30, score on 35 and 40), and the
    per-instance residuals of the winners on the 37,800 instances with the
    counts below and above the optimum — **not a bound**.
    """
    values = _values(cells)
    y = cells["mean"].to_numpy(dtype=float)
    n = cells["n"].to_numpy(dtype=float)
    folds = _n_folds(n)
    columns = list(NOMINAL)
    table, n_terms = search(values, y, folds, columns, max_degree=3, keep=150, workers=workers)
    pairs = pair_search(values, y, folds, list(table["term"]), keep=30)
    out = {"n_terms": n_terms, "monomials": table.head(15), "pairs": pairs.head(10),
           "best_term": table.iloc[0]["term"], "best_pair": (pairs.iloc[0]["terms"], pairs.iloc[0]["coef"])}

    # baselines at the cell level: constant, linear in n, and the "optimum is n" edge
    base = []
    for name, pred in {
        "constant (mean of training cells)": _cv_constant(y, folds),
        "linear in n (a + b·n)": _cv_linear(np.stack([n, np.ones_like(n)], 1), y, folds),
        "linear in n and deg_nom": _cv_linear(np.stack([n, values["deg_nom"], np.ones_like(n)], 1), y, folds),
        "n (the complete-graph value)": n,
    }.items():
        base.append({"estimate": name, **_scores(pred, y)})
    out["baselines"] = pd.DataFrame(base)

    if nested:
        out["nested"] = _nested(values, y, n, columns, workers)

    # extrapolation: fit on n ≤ 30, score on n ∈ {35, 40}
    train = n <= 30
    test = ~train
    ex = []
    t = evaluate_terms(values, [out["best_term"]])[0]
    a, b = fit_term_lad(t[train], y[train])
    ex.append({"estimate": f"monomial: {format_term(out['best_term'])}", **_scores(a * t[test] + b, y[test])})
    terms2, _ = out["best_pair"]
    T2 = evaluate_terms(values, list(terms2))
    X = np.stack([T2[0], T2[1], np.ones(len(y))], 1)
    c = _lad_fit_linear(X[train], y[train])
    ex.append({"estimate": "pair", **_scores(X[test] @ c, y[test])})
    Xl = np.stack([n, np.ones_like(n)], 1)
    cl = np.linalg.lstsq(Xl[train], y[train], rcond=None)[0]
    ex.append({"estimate": "linear in n", **_scores(Xl[test] @ cl, y[test])})
    out["extrapolation"] = pd.DataFrame(ex)

    # per-instance residuals of the cell-level winners (constants from all cells)
    inst_values = nominal_features(frame["n"], frame["m"], frame["generator"], frame["param"])
    opt = frame["optimum"].to_numpy(dtype=float)
    preds = {}
    t_all = evaluate_terms(inst_values, [out["best_term"]])[0]
    a, b = fit_term_lad(evaluate_terms(values, [out["best_term"]])[0], y)
    preds[f"monomial: {a:.4g} · [{format_term(out['best_term'])}] {b:+.4g}"] = a * t_all + b
    T2i = evaluate_terms(inst_values, list(terms2))
    c = _lad_fit_linear(X, y)
    preds["pair: " + pairs.iloc[0]["formula"]] = c[0] * T2i[0] + c[1] * T2i[1] + c[2]
    cell_mean = frame.groupby(["generator", "ratio", "n", "param"])["optimum"].transform("mean").to_numpy()
    preds["cell mean (the ceiling: what a perfect formula for E[opt] achieves)"] = cell_mean
    rows = []
    for name, p in preds.items():
        r = np.round(p)
        err = p - opt
        rows.append({"estimate": name, **_scores(p, opt),
                     "below": int((r < opt).sum()), "above": int((r > opt).sum()),
                     "max_below": float((opt - r).max()), "max_above": float((r - opt).max()),
                     "q05": float(np.quantile(err, 0.05)), "q25": float(np.quantile(err, 0.25)),
                     "q50": float(np.quantile(err, 0.5)), "q75": float(np.quantile(err, 0.75)),
                     "q95": float(np.quantile(err, 0.95))})
    out["instance_residuals"] = pd.DataFrame(rows)
    out["formula_constants"] = {"monomial": (format_term(out["best_term"]), a, b),
                                "pair": (pairs.iloc[0]["formula"], tuple(float(x) for x in c))}
    # residual of the monomial by n and by regime
    name0 = next(iter(preds))
    reg = cells.assign(regime=cells.apply(regime_of, axis=1))[["generator", "ratio", "n", "param", "regime"]]
    res = frame[["generator", "ratio", "n", "param", "series"]].merge(reg, how="left")
    res["err"] = preds[name0] - opt
    out["residual_by_n"] = res.groupby("n")["err"].agg(mae=lambda s: s.abs().mean(), bias="mean",
                                                        exact=lambda s: (s.abs() <= 0.5).mean()).reset_index()
    out["residual_by_series_regime"] = res.groupby(["series", "regime"])["err"].agg(
        mae=lambda s: s.abs().mean(), bias="mean", count="size").reset_index()
    return out


def _cv_constant(y, folds):
    pred = np.zeros_like(y)
    for tr, te in folds:
        pred[te] = y[tr].mean()
    return pred


def _cv_linear(X, y, folds):
    pred = np.zeros_like(y)
    for tr, te in folds:
        c = np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]
        pred[te] = X[te] @ c
    return pred


def _nested(values, y, n, columns, workers) -> dict:
    """Leave-one-size-out outer loop; the search reruns inside each fold."""
    pred_m = np.zeros_like(y)
    pred_p = np.zeros_like(y)
    winners = []
    for tr, te in _n_folds(n):
        sub = {c: v[tr] for c, v in values.items()}
        inner = _n_folds(n[tr])
        table, _ = search(sub, y[tr], inner, columns, max_degree=3, keep=60, workers=workers)
        best = table.iloc[0]["term"]
        t = evaluate_terms(values, [best])[0]
        a, b = fit_term_lad(t[tr], y[tr])
        pred_m[te] = a * t[te] + b
        pairs = pair_search(sub, y[tr], inner, list(table["term"]), keep=10)
        terms2 = pairs.iloc[0]["terms"]
        T2 = evaluate_terms(values, list(terms2))
        X = np.stack([T2[0], T2[1], np.ones(len(y))], 1)
        c = _lad_fit_linear(X[tr], y[tr])
        pred_p[te] = X[te] @ c
        winners.append({"held-out n": int(n[te][0]), "monomial": format_term(best),
                        "monomial mae on held-out n": float(np.abs(pred_m[te] - y[te]).mean()),
                        "pair": pairs.iloc[0]["formula"],
                        "pair mae on held-out n": float(np.abs(pred_p[te] - y[te]).mean())})
    return {"monomial": _scores(pred_m, y), "pair": _scores(pred_p, y), "winners": pd.DataFrame(winners)}


# ----------------------------------------------------------------------------
# structural forms: linear in n with a slope that saturates in the degree
# ----------------------------------------------------------------------------

STRUCTURAL = {
    # name: (function of (n, D, q, *params), initial params, printed form)
    # D = deg_nom, the nominal mean degree; q = q_nom, the nominal edge probability, D = (n − 1)·q.
    "a + n·D/(D + c)": (lambda n, D, q, a, c: a + n * D / (D + c), (3.0, 20.0),
                        "a + n · D / (D + c)"),
    "a + n·(1 − exp(−D/τ))": (lambda n, D, q, a, t: a + n * (1 - np.exp(-D / t)), (3.0, 20.0),
                              "a + n · (1 − exp(−D / τ))"),
    "a + n·[1 − (1 − q)·c/(D + c)]": (lambda n, D, q, a, c: a + n * (1 - (1 - q) * c / (D + c)), (3.0, 20.0),
                                      "a + n · [1 − (1 − q) · c / (D + c)]"),
    "a(1 − q) + n·[1 − √(1 − q)·c/(D + c)]": (lambda n, D, q, a, c: a * (1 - q) + n * (1 - np.sqrt(1 - q) * c / (D + c)),
                                              (2.0, 30.0), "a · (1 − q) + n · [1 − √(1 − q) · c / (D + c)]"),
    "a(1 − q) + n·[1 − (1 − q)^e·c/(D + c)]": (lambda n, D, q, a, c, e: a * (1 - q) + n * (1 - (1 - q) ** e * c / (D + c)),
                                               (2.0, 30.0, 0.5), "a · (1 − q) + n · [1 − (1 − q)^e · c / (D + c)]"),
}


def _fit_form(fn, n, D, q, y, p0):
    """Least squares start, then least absolute deviation by Nelder–Mead."""
    from scipy.optimize import curve_fit, minimize
    try:
        popt, _ = curve_fit(lambda x, *p: fn(x[0], x[1], x[2], *p), np.stack([n, D, q]), y, p0=p0, maxfev=20000)
    except RuntimeError:
        popt = np.asarray(p0, dtype=float)
    res = minimize(lambda p: np.abs(fn(n, D, q, *p) - y).mean(), popt, method="Nelder-Mead",
                   options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 6000})
    return res.x if np.isfinite(res.fun) else popt


def structural_fits(cells: pd.DataFrame, frame: pd.DataFrame) -> dict:
    """`E[opt] ≈ a + n · s(D, q)`, `D = deg_nom` the nominal mean degree of the
    random intersection graph and `q = D / (n − 1)` its edge probability. The
    slope must vanish as `D → 0`, and reach 1 as the graph fills (`q → 1`,
    where the optimum is `n`); `D / (D + c)` alone does the first and not the
    second, which is why the two forms in `D` alone are kept as the record of
    a failure. The forms with `(1 − q)` close both ends. Constants fitted by
    least absolute deviation on the cell means; scored leave-one-size-out,
    extrapolated from `n ≤ 30` to 35 and 40, and the best form's residual on
    every instance with the counts below and above the optimum. **Not a
    bound.** The forms are chosen by hand from the slope-by-degree table, so
    choosing among five is the only selection."""
    n = cells["n"].to_numpy(dtype=float)
    D = cells["deg_nom"].to_numpy(dtype=float)
    q = cells["q_nom"].to_numpy(dtype=float)
    y = cells["mean"].to_numpy(dtype=float)
    folds = _n_folds(n)
    rows = []
    fitted = {}
    fixed = (cells["generator"] == "fixed").to_numpy()
    for name, (fn, p0, printed) in STRUCTURAL.items():
        pred = np.zeros_like(y)
        for tr, te in folds:
            p = _fit_form(fn, n[tr], D[tr], q[tr], y[tr], p0)
            pred[te] = fn(n[te], D[te], q[te], *p)
        train = n <= 30
        p_small = _fit_form(fn, n[train], D[train], q[train], y[train], p0)
        ex = _scores(fn(n[~train], D[~train], q[~train], *p_small), y[~train])
        p_all = _fit_form(fn, n, D, q, y, p0)
        fitted[name] = p_all
        rows.append({"form": printed, "constants (all cells)": ", ".join(f"{v:.3g}" for v in p_all),
                     "mae (held-out n)": _scores(pred, y)["mae"], "exact (held-out n)": _scores(pred, y)["exact"],
                     "mae held-out, fixed cells": float(np.abs(pred - y)[fixed].mean()),
                     "mae held-out, bernoulli cells": float(np.abs(pred - y)[~fixed].mean()),
                     "mae n≤30 → 35,40": ex["mae"], "bias n≤30 → 35,40": float((fn(n[~train], D[~train], q[~train], *p_small) - y[~train]).mean()),
                     "mae in-sample": _scores(fn(n, D, q, *p_all), y)["mae"]})
    table = pd.DataFrame(rows).sort_values("mae (held-out n)").reset_index(drop=True)
    best = table.iloc[0]["form"]
    best_name = next(k for k, v in STRUCTURAL.items() if v[2] == best)
    fn, _, printed = STRUCTURAL[best_name]
    p_all = fitted[best_name]
    inst = nominal_features(frame["n"], frame["m"], frame["generator"], frame["param"])
    opt = frame["optimum"].to_numpy(dtype=float)
    pred_i = fn(inst["n"], inst["deg_nom"], inst["q_nom"], *p_all)
    err = pred_i - opt
    r = np.round(pred_i)
    inst_row = {"estimate": f"{printed} with ({', '.join(f'{v:.3g}' for v in p_all)})", **_scores(pred_i, opt),
                "below": int((r < opt).sum()), "above": int((r > opt).sum()),
                "max_below": float((opt - r).max()), "max_above": float((r - opt).max()),
                **{f"q{int(q * 100):02d}": float(np.quantile(err, q)) for q in (0.05, 0.25, 0.5, 0.75, 0.95)}}
    by_n = pd.DataFrame({"n": frame["n"], "err": err}).groupby("n")["err"].agg(
        mae=lambda s: s.abs().mean(), bias="mean", exact=lambda s: (s.abs() <= 0.5).mean()).reset_index()
    by_series = pd.DataFrame({"series": frame["series"], "err": err}).groupby("series")["err"].agg(
        mae=lambda s: s.abs().mean(), bias="mean").reset_index()
    # the slope s(D) the best form implies, at a few degrees
    grid = np.array([2, 4, 9, 16, 25, 36, 64, 100, 200], dtype=float)
    slope_curve = pd.DataFrame({"D (nominal mean degree, sparse limit q → 0)": grid,
                                "implied asymptotic optimum / n": [float(fn(1e6, d, d / 1e6, *p_all) / 1e6) for d in grid]})
    return {"table": table, "best": best_name, "constants": p_all, "instance_residual": pd.DataFrame([inst_row]),
            "by_n": by_n, "by_series": by_series, "slope_curve": slope_curve}


# ----------------------------------------------------------------------------
# the sandwich and pw − tw on the ensemble
# ----------------------------------------------------------------------------


def sandwich(frame: pd.DataFrame) -> dict:
    """§5's sandwich on the ensemble, plus λ by n, by density and by series."""
    out = sandwich_table(frame)
    differ = frame[~frame["forced"]]
    out["lambda_by_n"] = differ.groupby("n")["lam"].agg(
        instances="size", median="median", mean="mean", std="std",
        iqr=lambda s: s.quantile(0.75) - s.quantile(0.25),
        share_at_half=lambda s: ((s - 0.5).abs() <= 0.1).mean()).reset_index()
    edges = [0, 1.5, 2, 2.5, 3, 4, 6, 10, 100]
    band = pd.cut(differ["col_mean"], edges)
    out["lambda_by_density"] = differ.groupby(band, observed=True)["lam"].agg(
        instances="size", median="median", mean="mean", std="std").reset_index().rename(columns={"col_mean": "col_mean band"})
    out["lambda_by_series_n"] = differ.pivot_table(index="series", columns="n", values="lam", aggfunc="median")
    out["forced_by_n"] = frame.groupby("n")["forced"].mean().rename("forced share").reset_index()
    from scipy.stats import spearmanr
    rho = {}
    for col in ("col_mean", "g_density", "deg_nom", "opt_frac", "n", "g_deg_std"):
        if col in differ:
            rho[col] = float(spearmanr(differ[col], differ["lam"]).statistic)
    out["lambda_spearman"] = rho
    width = (frame["bw_rcm"] - frame["g_degeneracy"]) / frame["n"]
    out["width_by_n"] = pd.DataFrame({"n": frame["n"], "width_frac": width}).groupby("n")["width_frac"].agg(
        ["mean", "median"]).reset_index()
    return out


def pw_minus_tw(frame: pd.DataFrame, min_n: int = 15) -> dict:
    """`optimum − (tw_min_fill + 1)` and the bracket it belongs to.

    `res_tw = optimum − tw_min_fill − 1 ≤ pw − tw ≤ optimum − g_degeneracy − 1
    = res_deg`, both proved (min-fill is an elimination ordering, so an upper
    bound on treewidth; degeneracy ≤ treewidth). Tables by n, by density
    band, by cell for `m = n`, and the slope of the cell mean of each end in
    n at fixed parameter (how the certified excess of pathwidth over
    treewidth grows with size).
    """
    def agg(g):
        return pd.Series({
            "instances": len(g),
            "res_tw mean": g["res_tw"].mean(), "res_tw std": g["res_tw"].std(),
            "res_tw > 0 (pw > tw certified)": (g["res_tw"] > 0).mean(),
            "res_tw < 0": (g["res_tw"] < 0).mean(),
            "res_tw max": g["res_tw"].max(),
            "min(tw_mf, tw_md): res > 0": (g["res_tw2"] > 0).mean(),
            "min(tw_mf, tw_md): res mean": g["res_tw2"].mean(),
            "res_deg mean": g["res_deg"].mean(),
            "res_deg = 0 (pw = tw certified)": (g["res_deg"] == 0).mean(),
        })
    out = {"by_n": frame.groupby("n").apply(agg, include_groups=False).reset_index()}
    edges = [0, 1.5, 2, 2.5, 3, 4, 6, 10, 100]
    band = pd.cut(frame["col_mean"], edges)
    out["by_density"] = frame.groupby(band, observed=True).apply(agg, include_groups=False).reset_index().rename(
        columns={"col_mean": "col_mean band"})
    cells = frame.groupby(["generator", "ratio", "param", "n"]).agg(
        res_tw=("res_tw", "mean"), res_deg=("res_deg", "mean"), pos=("res_tw", lambda s: (s > 0).mean()),
        col_mean=("col_mean", "median")).reset_index()
    out["cells"] = cells
    rows = []
    for (gen, ratio, param), g in cells.groupby(["generator", "ratio", "param"]):
        g = g[g["n"] >= min_n].sort_values("n")
        if len(g) < 3:
            continue
        b_tw = np.polyfit(g["n"], g["res_tw"], 1)[0]
        b_deg = np.polyfit(g["n"], g["res_deg"], 1)[0]
        rows.append({"series": series_label(gen, ratio), "param": float(param),
                     "col_mean at n=40": float(g.iloc[-1]["col_mean"]),
                     "res_tw at n=15": float(g.iloc[0]["res_tw"]), "res_tw at n=40": float(g.iloc[-1]["res_tw"]),
                     "slope res_tw per customer": float(b_tw),
                     "res_deg at n=40": float(g.iloc[-1]["res_deg"]), "slope res_deg per customer": float(b_deg),
                     "pw > tw certified share at n=40": float(g.iloc[-1]["pos"])})
    out["slopes"] = pd.DataFrame(rows)
    return out


# ----------------------------------------------------------------------------
# figure
# ----------------------------------------------------------------------------


def figure(cells: pd.DataFrame, frame: pd.DataFrame, path: Path = FIGURE) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.patch.set_facecolor("white")
    # (a) CV against n, fixed generator m = n, one line per d
    ax = axes[0, 0]
    sub = cells[(cells["generator"] == "fixed") & (cells["ratio"] == 1)]
    params = sorted(sub["param"].unique())[:8]
    for i, p in enumerate(params):
        g = sub[(sub["param"] == p) & (sub["cv"] > 0)].sort_values("n")   # a CV of 0 has no log
        ax.plot(g["n"], g["cv"], color=PALETTE[i], lw=2, marker="o", ms=4, label=f"d = {int(p)}")
    ax.axhline(CV_KILL, color="#888", lw=1, ls="--")
    ax.text(10.5, CV_KILL + 0.005, "kill threshold 0.2", color="#666", fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("n (customers)")
    ax.set_ylabel("CV of the optimum (log)")
    ax.set_title("(a) fixed d, m = n: CV falls with n", fontsize=10, loc="left")
    ax.legend(fontsize=7, ncol=2, frameon=False)
    # (b) CV against n, Bernoulli m = n, one line per p
    ax = axes[0, 1]
    sub = cells[(cells["generator"] == "bernoulli") & (cells["ratio"] == 1)]
    params = sorted(sub["param"].unique())[:8]
    for i, p in enumerate(params):
        g = sub[(sub["param"] == p) & (sub["cv"] > 0)].sort_values("n")
        ax.plot(g["n"], g["cv"], color=PALETTE[i], lw=2, marker="o", ms=4, label=f"p = {p:g}")
    ax.axhline(CV_KILL, color="#888", lw=1, ls="--")
    ax.set_yscale("log")
    ax.set_xlabel("n (customers)")
    ax.set_ylabel("CV of the optimum (log)")
    ax.set_title("(b) Bernoulli p, m = n: flat only at or below the giant-component threshold", fontsize=10, loc="left")
    ax.legend(fontsize=7, ncol=2, frameon=False)
    # (c) E[opt] against n, fixed m = n
    ax = axes[1, 0]
    sub = cells[(cells["generator"] == "fixed") & (cells["ratio"] == 1)]
    params = sorted(sub["param"].unique())[:8]
    for i, p in enumerate(params):
        g = sub[sub["param"] == p].sort_values("n")
        ax.plot(g["n"], g["mean"], color=PALETTE[i], lw=2, marker="o", ms=4, label=f"d = {int(p)}")
        ax.fill_between(g["n"], g["mean"] - g["std"], g["mean"] + g["std"], color=PALETTE[i], alpha=0.15, lw=0)
    ax.plot([10, 40], [10, 40], color="#888", lw=1, ls=":")
    ax.set_xlabel("n (customers)")
    ax.set_ylabel("mean optimum ± 1 std")
    ax.set_title("(c) fixed d, m = n: E[opt] linear in n, std about one stack", fontsize=10, loc="left")
    ax.legend(fontsize=7, ncol=2, frameon=False)
    # (d) λ median and the pw − tw bracket against realised density, n = 40
    ax = axes[1, 1]
    f40 = frame[(frame["n"] == 40) & (~frame["forced"])]
    edges = np.array([1.0, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25])
    band = pd.cut(f40["col_mean"], edges)
    lam = f40.groupby(band, observed=True)["lam"].median()
    x = [b.mid for b in lam.index]
    ax.plot(x, lam.values, color=PALETTE[0], lw=2, marker="o", ms=5, label="median λ (optimum's position in the sandwich)")
    q1 = f40.groupby(band, observed=True)["lam"].quantile(0.25)
    q3 = f40.groupby(band, observed=True)["lam"].quantile(0.75)
    ax.fill_between(x, q1.values, q3.values, color=PALETTE[0], alpha=0.15, lw=0)
    ax.axhline(0.5, color="#888", lw=1, ls="--")
    ax.set_xscale("log")
    ax.set_ylim(0, 1)
    ax.set_xlabel("col_mean (customers per product, realised), n = 40")
    ax.set_ylabel("λ = (optimum − 1 − degeneracy) / (bw_rcm − degeneracy)")
    ax.set_title("(d) λ is not ½: it climbs with density (IQR shaded)", fontsize=10, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    for a in axes.flat:
        a.spines[["top", "right"]].set_visible(False)
        a.grid(True, color="#eee", lw=0.8)
    fig.suptitle("Concentration of the optimum on G(n, m, p), n ≤ 40 (learning.concentration; nothing here is a bound)",
                 fontsize=11)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


# ----------------------------------------------------------------------------
# report
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def report(frame: pd.DataFrame, per_class: bool, nested: bool, workers: int) -> tuple[str, dict]:
    cells = cell_stats(frame)
    verdict = kill_verdict(cells)
    cvs = cv_scaling(cells)
    lin = linearity(cells)
    sbd = slope_by_degree(lin)
    fm = formula(cells, frame, nested=nested, workers=workers)
    st = structural_fits(cells, frame)
    sw = sandwich(frame)
    pt = pw_minus_tw(frame)

    parts = [f"# Concentration of the optimum on the generated ensemble{' (per isomorphism class)' if per_class else ''}\n",
             f"{len(frame):,} instances, {len(cells)} cells. Regenerate: `python -m learning.concentration"
             f"{' --per-class' if per_class else ''}`. **Nothing in this file is a bound.**\n"]
    parts.append("## Kill criterion: CV above 0.2 up to n = 40\n")
    parts.append(_md(verdict["per_n"]))
    parts.append(f"\ncells above {CV_KILL}: {verdict['cells_above_total']} of {len(cells)}, in series "
                 f"{verdict['series_above']}; of those with a giant component (largest component ≥ {LCC_SUPER} of n): "
                 f"{verdict['cells_above_supercritical']} (largest component fraction among them at most "
                 f"{verdict['max_lcc_frac_above']:.2f}); at n = {int(cells['n'].max())}: "
                 f"{verdict['cells_above_at_n_max']}. **Kill fires: {verdict['kill_fires']}.**\n")
    for stat, title in (("cv", "CV of the optimum"), ("mean", "mean optimum"), ("std", "standard deviation"),
                        ("mode_share", "share of instances at the modal optimum"), ("lcc_frac", "largest component fraction (mean)")):
        parts.append(f"## {title}, by cell (param × n)\n")
        for gen, ratio in SERIES:
            parts.append(f"**{series_label(gen, ratio)}**\n")
            parts.append(matrix(cells, gen, ratio, stat).to_markdown(floatfmt=".3g") + "\n")
    parts.append("## CV and std against n at fixed parameter (power-law exponents, n ≥ 15)\n")
    parts.append(_md(cvs))
    parts.append("\nsummary by regime:\n")
    parts.append(_md(cvs.groupby("regime")[["cv_exp", "std_exp", "cv_at_n_max"]].agg(["median", "min", "max"]).reset_index(), ".2f"))
    parts.append("\n## E[opt] against n at fixed parameter (n ≥ 15)\n")
    parts.append(_md(lin))
    parts.append("\nsummary by regime:\n")
    parts.append(_md(lin.groupby("regime")[["r2", "gamma", "slope"]].agg(["median", "min", "max"]).reset_index(), ".3f"))
    parts.append("\n## Slope of E[opt] in n against the nominal mean degree β·d·(d − 1), fixed generator\n")
    parts.append(_md(sbd))
    parts.append(f"\n## E[opt](n, m, p): enumerated search over the generator parameters alone ({fm['n_terms']:,} terms, leave-one-size-out)\n")
    parts.append("Leading monomials `mean ≈ a·t + b` (LAD constants on all cells; mae/exact on held-out sizes; **not a bound**):\n")
    parts.append(_md(fm["monomials"][["formula", "degree", "mae", "exact", "a", "b"]], ".4g"))
    parts.append("\nLeading pairs:\n")
    parts.append(_md(fm["pairs"][["formula", "mae", "exact"]], ".4g"))
    parts.append("\nCell-level baselines (same folds):\n")
    parts.append(_md(fm["baselines"], ".3f"))
    if "nested" in fm:
        parts.append("\nNested (search rerun inside each training set of six sizes, winner scored on the held-out size):\n")
        parts.append(_md(pd.DataFrame([{"estimate": "monomial", **fm["nested"]["monomial"]},
                                       {"estimate": "pair", **fm["nested"]["pair"]}]), ".3f"))
        parts.append("\n" + _md(fm["nested"]["winners"], ".3f"))
    parts.append("\nExtrapolation: constants fitted on n ≤ 30, scored on the cells at n = 35 and 40:\n")
    parts.append(_md(fm["extrapolation"], ".3f"))
    parts.append("\nPer-instance residuals of the cell-level winners on all instances (**not a bound**: `below`/`above` count rounded predictions under/over the certified optimum):\n")
    parts.append(_md(fm["instance_residuals"], ".3f"))
    parts.append("\nMonomial residual by n:\n")
    parts.append(_md(fm["residual_by_n"], ".3f"))
    parts.append("\nMonomial residual by series and regime (of the cell at its n):\n")
    parts.append(_md(fm["residual_by_series_regime"], ".3f"))
    parts.append("\n## Structural forms: E[opt] ≈ a + n · s(D), D the nominal mean degree (**not a bound**)\n")
    parts.append(_md(st["table"], ".3f"))
    parts.append(f"\nBest form `{st['best']}`, constants {tuple(round(float(v), 3) for v in st['constants'])}; per-instance residual on all instances:\n")
    parts.append(_md(st["instance_residual"], ".3f"))
    parts.append("\nby n:\n")
    parts.append(_md(st["by_n"], ".3f"))
    parts.append("\nby series:\n")
    parts.append(_md(st["by_series"], ".3f"))
    parts.append("\nthe slope s(D) = lim optimum / n the best form implies:\n")
    parts.append(_md(st["slope_curve"], ".3f"))
    parts.append("\n## The sandwich on the ensemble (constants fixed by hand)\n")
    parts.append(_md(sw["table"], ".3f"))
    parts.append("\n" + "\n".join(f"- {k}: {v}" for k, v in sw["checks"].items()))
    parts.append("\n\nλ by n (instances where bw_rcm > g_degeneracy):\n")
    parts.append(_md(sw["lambda_by_n"], ".3f"))
    parts.append("\nλ by realised density:\n")
    parts.append(_md(sw["lambda_by_density"], ".3f"))
    parts.append("\nλ median by series × n:\n")
    parts.append(sw["lambda_by_series_n"].to_markdown(floatfmt=".3f"))
    parts.append("\n\nforced share by n (bw_rcm = g_degeneracy):\n")
    parts.append(_md(sw["forced_by_n"], ".3f"))
    parts.append("\nSpearman ρ of λ with: " + ", ".join(f"`{k}` {v:.2f}" for k, v in sw["lambda_spearman"].items()))
    parts.append("\n\nsandwich width (bw_rcm − g_degeneracy) / n by n:\n")
    parts.append(_md(sw["width_by_n"], ".3f"))
    parts.append("\n## optimum − (tw_min_fill + 1) ≤ pw − tw ≤ optimum − (g_degeneracy + 1)\n")
    parts.append("by n:\n")
    parts.append(_md(pt["by_n"], ".3f"))
    parts.append("\nby realised density:\n")
    parts.append(_md(pt["by_density"], ".3f"))
    parts.append("\nslopes of the cell means in n at fixed parameter (n ≥ 15):\n")
    parts.append(_md(pt["slopes"], ".3f"))
    parts.append("\ncell means of `optimum − tw_min_fill − 1`, param × n:\n")
    for gen, ratio in SERIES:
        sub = pt["cells"][(pt["cells"]["generator"] == gen) & (pt["cells"]["ratio"] == ratio)]
        parts.append(f"**{series_label(gen, ratio)}**\n")
        parts.append(sub.pivot(index="param", columns="n", values="res_tw").to_markdown(floatfmt=".2f") + "\n")
    summary = {
        "kill": {k: v for k, v in verdict.items() if k != "per_n"},
        "max_cv_by_n": verdict["per_n"].set_index("n")["max_cv"].round(3).to_dict(),
        "cv_exp_by_regime": cvs.groupby("regime")["cv_exp"].median().round(2).to_dict(),
        "linearity_r2_by_regime": lin.groupby("regime")["r2"].median().round(3).to_dict(),
        "formula": fm["formula_constants"],
        "formula_cell_mae": float(fm["monomials"].iloc[0]["mae"]),
        "nested_cell_mae": fm["nested"]["monomial"]["mae"] if "nested" in fm else None,
        "instance_mae": fm["instance_residuals"].set_index("estimate")["mae"].round(3).to_dict(),
        "structural": {"best": st["best"], "constants": [round(float(v), 4) for v in st["constants"]],
                       "cell_mae_heldout_n": round(float(st["table"].iloc[0]["mae (held-out n)"]), 3),
                       "extrapolation_mae": round(float(st["table"].iloc[0]["mae n≤30 → 35,40"]), 3),
                       "instance_mae": round(float(st["instance_residual"].iloc[0]["mae"]), 3)},
        "pw_minus_tw": {"certified_pw_gt_tw_share_by_n": pt["by_n"].set_index("n")["min(tw_mf, tw_md): res > 0"].round(3).to_dict(),
                        "res_tw_max": float(pt["by_n"]["res_tw max"].max())},
        "lambda_median_by_n": sw["lambda_by_n"].set_index("n")["median"].round(3).to_dict(),
        "lambda_spearman": {k: round(v, 2) for k, v in sw["lambda_spearman"].items()},
    }
    return "\n".join(parts), summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--csv", type=Path, default=RESULTS_CSV)
    ap.add_argument("--per-class", action="store_true")
    ap.add_argument("--no-nested", action="store_true")
    ap.add_argument("--no-figure", action="store_true")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", type=Path, default=TABLES)
    ap.add_argument("--figure", type=Path, default=FIGURE)
    args = ap.parse_args()

    frame = load(args.csv, args.per_class)
    text, summary = report(frame, args.per_class, not args.no_nested, args.workers)
    out = args.out if not args.per_class else args.out.with_name(args.out.stem + "_class" + args.out.suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"wrote {out}")
    print(json.dumps(summary, indent=1, default=str))
    if not args.no_figure:
        print(f"wrote {figure(cell_stats(frame), frame, args.figure)}")


if __name__ == "__main__":
    main()
