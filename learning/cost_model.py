"""§19 (plan 2 §2.3, loop0003 item 05): can the cost of a refutation be predicted before it is run?

The question. `benchmarks.recertify` allocates five-day budgets blind, and the
only cost laws on record are per-cell exponentials in `n` (§11) and a linear
surface fitted at n ≤ 30 (§14), both of which §14 showed over-predict by a
decade or more at 125. This module predicts `log10(1 + nodes)` to refute
`optimum − 1` from **label-free graph features** — the ridge coordinate
`col_mean`, `n`, `m / n`, `optimum / n`, degree statistics, min-fill
treewidth, degeneracy, components — with §16's drift of the rate as a term,
trains at **n ≤ 75** and tests on every count on record at **100 and 125**.

Censoring. A call that hit its deadline reports the nodes it visited, which is
a lower bound on the count; such rows are kept and enter the likelihood as
right-censored observations (a Tobit / censored-Gaussian regression in log
space, written by hand because neither `lifelines` nor `scikit-survival` is
installed; both are soft imports elsewhere and neither is required here).

Noise floor. Item 04 measured the spread of the count over relabellings of the
same instance (`portfolio.csv.gz`, 16 labellings per instance at 40–100, and
`differential.csv.gz`, 8 at 10–40). A label-free predictor cannot see which
labelling will run, so the per-instance standard deviation over labellings is
the error it can never remove; it is reported beside every model error.

Two configurations, dated. `default` counts are unaffected by the 2026-09-26
`better_move` fix and are the primary target. `csearch` counts changed with the
fix (§18 (e)), so the `csearch` model is trained **only on pre-fix sources**
(`results.csv`, `node_counts.csv`, `scale_nodes.csv`) and tested against
pre-fix counts (`scale_nodes.csv` at 100, `recertify/results.json` at 125);
post-fix counts (`portfolio.csv.gz` identity rows, the race) are compared
separately and labelled.

Deliverables (`reports/ml_nature.md` §19, tables in `reports/cost_model_tables.md`):
error by size band for the baselines and the models; the decade-accuracy claim
at 100–125; predicted against actual cost of the eight `recertify` entries; the
cheapest-first order for the entries still open. **Kill** (plan 2 §2.3): fewer
than 80% of the 100–125 counts within one decade → not to be used for budgeting.

Run:
    python -m learning.cost_model                 # fit, evaluate, write tables + predictions
    python -m learning.cost_model --config csearch
    python -m learning.cost_model --no-gbm        # linear Tobit only (no LightGBM)

Nothing here touches a solver, a bound, or `solutions/`; a prediction is never
a bound.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

from learning.scale_test import (INSTANCES, NODE_COUNTS, RECERTIFY, RESULTS_CSV, SCALE_NODES,
                                 cell_laws, laws_predict, load_campaign, surface_fit, surface_predict)

DATA_DIR = Path("learning/data")
ENSEMBLE_DIR = DATA_DIR / "ensemble"
RESULTS_UPWARD_CSV = ENSEMBLE_DIR / "results_upward.csv"
FINISH_CSV = ENSEMBLE_DIR / "results_upward_finish.csv"
PORTFOLIO_CSV = ENSEMBLE_DIR / "portfolio.csv.gz"
RACE_CSV = ENSEMBLE_DIR / "portfolio_race.csv"
DIFFERENTIAL_CSV = ENSEMBLE_DIR / "differential.csv.gz"
CANONICAL = DATA_DIR / "canonical.csv"
PREDICTIONS_CSV = ENSEMBLE_DIR / "cost_model_predictions.csv"
TABLES = Path("reports/cost_model_tables.md")

CONFIGS = ("default", "csearch")
TRAIN_MAX_N = 75
TEST_N = (100, 125)
DECADE = 1.0
KILL_COVERAGE = 0.80
SECONDS_PER_NODE_125 = 0.55e-6      # §14 / recertify: 0.55 µs per node at 125 × 125 on one core

# 2026-09-26 11:45 `better_move` fix (commit 0eb33915). Sources whose csearch counts predate it:
# results.csv, node_counts.csv, scale_nodes.csv, recertify — and results_upward.csv, whose run
# straddled the commit but was made by a worktree built before it: `date_upward_csearch` shows that
# in every cell where Theorem 2 is on, the post-fix identity count of §18 differs from the run's
# count on at least one of the eight instances (0 of 70 cells match), which a post-fix run could not do.
PREFIX_CSEARCH_SOURCES = ("campaign", "upward", "corpus")
BETTER_MOVE_ROW_MEAN = 5.0   # `sparse_enough_for_better_move`: mean products per customer ≤ 5


# ----------------------------------------------------------------------------
# size bands
# ----------------------------------------------------------------------------

def band_of(n) -> str:
    n = int(n)
    if n <= 20:
        return "10-20"
    if n <= 40:
        return "21-40"
    if n <= 60:
        return "50-60"
    if n <= 82:
        return "75"
    if n <= 105:
        return "100"
    return "125"


BAND_ORDER = ["10-20", "21-40", "50-60", "75", "100", "125"]


# ----------------------------------------------------------------------------
# data assembly
# ----------------------------------------------------------------------------

FEATURES_NEEDED = ["col_mean", "g_deg_mean", "g_deg_std", "g_largest_comp_frac", "g_components",
                   "tw_min_fill", "g_degeneracy", "g_clustering", "row_mean"]


def _campaign_frames() -> pd.DataFrame:
    """§10's 37,800 at 10–40 and §16's 6,785 at 50–100, finish-stage answers merged,
    one row per (instance, configuration) with the refutation count."""
    from learning.upward import apply_finish, load_results
    parts = []
    camp = load_campaign(RESULTS_CSV)
    camp["source"] = "campaign"
    parts.append(camp)
    if RESULTS_UPWARD_CSV.exists():
        up = load_results(RESULTS_UPWARD_CSV)
        up = apply_finish(up, FINISH_CSV)
        up["source"] = "upward"
        parts.append(up)
    f = pd.concat(parts, ignore_index=True)
    f["file_key"] = f["cell"]
    return f


def _corpus_frame() -> pd.DataFrame:
    """The corpus instances with features, isomorphism certificate and every node
    count on record: `node_counts.csv` (n ≤ 40, both configurations),
    `scale_nodes.csv` (50–125, both), `recertify/results.json` (125, csearch pre-fix)."""
    feats = pd.read_csv(INSTANCES)
    feats = feats.rename(columns={"n_customers": "n", "n_patterns": "m"})
    feats["n"] = feats["n"].astype(int)
    feats["m"] = feats["m"].astype(int)
    if CANONICAL.exists():
        can = pd.read_csv(CANONICAL)[["instance_name", "graph_cert"]]
        feats = feats.merge(can, on="instance_name", how="left")
    else:
        feats["graph_cert"] = np.nan
    feats["source"] = "corpus"
    feats["file_key"] = feats["source_file"]
    rows = []
    if NODE_COUNTS.exists():
        nc = pd.read_csv(NODE_COUNTS)
        for r in nc.itertuples():
            rows.append((r.instance_name, r.config, float(r.nodes), r.status, "node_counts"))
    if SCALE_NODES.exists():
        for r in pd.read_csv(SCALE_NODES).itertuples():
            rows.append((r.instance_name, r.config, float(r.nodes), r.status, "scale_nodes"))
    if RECERTIFY.exists():
        for r in json.load(open(RECERTIFY)):
            rows.append((r["name"], "csearch", float(r["nodes"]), r["status"], "recertify"))
    counts = pd.DataFrame(rows, columns=["instance_name", "config", "nodes", "status", "count_source"])
    merged = feats
    for cfg in CONFIGS:
        c = counts[counts["config"] == cfg].drop_duplicates("instance_name", keep="last")
        c = c[["instance_name", "nodes", "status", "count_source"]].rename(
            columns={"nodes": f"nodes_{cfg}", "status": f"status_{cfg}", "count_source": f"count_source_{cfg}"})
        merged = merged.merge(c, on="instance_name", how="left")   # instances without a count stay (to be predicted)
    return merged


def prepare(frame: pd.DataFrame) -> pd.DataFrame:
    """Derived columns shared by every source: `x = log10 col_mean`, `opt_frac`,
    `log_ratio`, and per configuration `y_<cfg>` = log10(1 + nodes) with `cens_<cfg>`."""
    f = frame.copy()
    f["n"] = f["n"].astype(int)
    f["m"] = f["m"].astype(int)
    f["x"] = np.log10(f["col_mean"].astype(float))
    f["opt_frac"] = f["optimum"].astype(float) / f["n"]
    f["log_ratio"] = np.log10(f["m"] / f["n"])
    f["band"] = f["n"].apply(band_of)
    for cfg in CONFIGS:
        col = f"nodes_{cfg}"
        if col not in f.columns:
            f[col] = np.nan
            f[f"status_{cfg}"] = ""
        f[f"y_{cfg}"] = np.log10(1.0 + f[col].astype(float))
        f[f"cens_{cfg}"] = f[f"status_{cfg}"].astype(str).eq("unknown")
        # a `sat` answer at value − 1 means the value was not the optimum: no refutation count
        f.loc[f[f"status_{cfg}"].astype(str).eq("sat"), f"y_{cfg}"] = np.nan
    return f


def assemble() -> pd.DataFrame:
    """Campaign, upward and corpus in one frame with group ids (file ∪ isomorphism class)."""
    from learning.fingerprint import union_groups
    camp = _campaign_frames()
    corp = _corpus_frame()
    keep = ["instance_name", "source", "file_key", "graph_cert", "n", "m", "optimum"] + FEATURES_NEEDED
    frames = []
    for f in (camp, corp):
        cols = keep + [c for c in f.columns if c.startswith(("nodes_", "status_", "count_source_"))]
        cols = [c for c in cols if c in f.columns]
        frames.append(f[cols])
    f = pd.concat(frames, ignore_index=True)
    f = prepare(f)
    f["group"] = union_groups(f["file_key"], f["graph_cert"])
    return f


def date_upward_csearch(upward_csv: Path = RESULTS_UPWARD_CSV, portfolio: Path = PORTFOLIO_CSV) -> pd.DataFrame:
    """Per upward cell with §18 identity rows: how many of its csearch counts equal the
    post-fix identity count. Where Theorem 2 is on (`row_mean ≤ 5`), a post-fix run
    would match on every instance; a pre-fix run differs on some."""
    if not (upward_csv.exists() and portfolio.exists()):
        return pd.DataFrame()
    up = pd.read_csv(upward_csv)[["instance_name", "cell", "nodes_csearch", "row_mean"]]
    p = pd.read_csv(portfolio)
    p = p[(p["labelling"] == "identity") & (p["source"] == "campaign")][["base_name", "nodes_lo"]]
    j = up.merge(p, left_on="instance_name", right_on="base_name")
    j["equal"] = j["nodes_csearch"].astype(float) == j["nodes_lo"].astype(float)
    j["theorem2_on"] = j["row_mean"] <= BETTER_MOVE_ROW_MEAN
    g = j.groupby("cell").agg(compared=("equal", "size"), equal=("equal", "sum"),
                              theorem2_on=("theorem2_on", "sum")).reset_index()
    g["verdict"] = np.where(g["theorem2_on"] == 0, "rule off: pre = post",
                            np.where(g["equal"] == g["compared"], "all equal: post-fix", "differs: pre-fix"))
    return g


def training_mask(frame: pd.DataFrame, config: str, max_n: int = TRAIN_MAX_N, min_n: int = 10) -> np.ndarray:
    """Rows a model of `config` may train on: n in [min_n, max_n], a count on record,
    and for csearch only pre-fix sources (the upward run straddled the fix)."""
    ok = (frame["n"] <= max_n) & (frame["n"] >= min_n) & np.isfinite(frame[f"y_{config}"])
    if config == "csearch":
        ok &= frame["source"].isin(PREFIX_CSEARCH_SOURCES)
    return ok.to_numpy()


def test_mask(frame: pd.DataFrame, config: str) -> np.ndarray:
    """Every count on record at 100 and 125 for `config`; csearch restricted to pre-fix sources."""
    ok = frame["n"].isin(TEST_N) & np.isfinite(frame[f"y_{config}"])
    if config == "csearch":
        ok &= frame["source"].isin(PREFIX_CSEARCH_SOURCES)
    return ok.to_numpy()


# ----------------------------------------------------------------------------
# the design: linear in n with density-, ratio- and structure-dependent rate, plus drift
# ----------------------------------------------------------------------------

def _deg_cv(f):
    return f["g_deg_std"] / (1.0 + f["g_deg_mean"])


TERMS = {
    "n": lambda f: f["n"],
    "x": lambda f: f["x"], "x2": lambda f: f["x"] ** 2,
    "n·x": lambda f: f["n"] * f["x"], "n·x2": lambda f: f["n"] * f["x"] ** 2,
    "opt_frac": lambda f: f["opt_frac"], "opt_frac2": lambda f: f["opt_frac"] ** 2,
    "n·opt_frac": lambda f: f["n"] * f["opt_frac"], "n·opt_frac2": lambda f: f["n"] * f["opt_frac"] ** 2,
    "log_deg": lambda f: np.log10(1 + f["g_deg_mean"]), "n·log_deg": lambda f: f["n"] * np.log10(1 + f["g_deg_mean"]),
    "deg_cv": _deg_cv, "n·deg_cv": lambda f: f["n"] * _deg_cv(f),
    "lcc": lambda f: f["g_largest_comp_frac"], "n·lcc": lambda f: f["n"] * f["g_largest_comp_frac"],
    "log_comp": lambda f: np.log10(f["g_components"].astype(float)),
    "log_ratio": lambda f: f["log_ratio"], "log_ratio2": lambda f: f["log_ratio"] ** 2,
    "n·log_ratio": lambda f: f["n"] * f["log_ratio"],
    "tw_frac": lambda f: f["tw_min_fill"] / f["n"], "n·tw_frac": lambda f: f["tw_min_fill"],
    "degen_frac": lambda f: f["g_degeneracy"] / f["n"], "n·degen_frac": lambda f: f["g_degeneracy"],
    "clust": lambda f: f["g_clustering"], "n·clust": lambda f: f["n"] * f["g_clustering"],
}
DRIFT_TERMS = {  # §16: the rate falls linearly with n → a quadratic in n, per density
    "n2": lambda f: f["n"] ** 2 / 100.0, "n2·x": lambda f: f["n"] ** 2 * f["x"] / 100.0,
}


def design(frame: pd.DataFrame, drift: bool = True) -> np.ndarray:
    terms = dict(TERMS)
    if drift:
        terms.update(DRIFT_TERMS)
    cols = [np.ones(len(frame))] + [np.asarray(fn(frame), dtype=float) for fn in terms.values()]
    return np.column_stack(cols)


def term_names(drift: bool = True) -> list[str]:
    return ["1"] + list(TERMS) + (list(DRIFT_TERMS) if drift else [])


# ----------------------------------------------------------------------------
# Tobit: Gaussian regression with right-censored observations, by hand
# ----------------------------------------------------------------------------

class Tobit:
    """log10 nodes = X β + ε, ε ~ N(0, σ²); a censored row contributes P(y* ≥ y_obs).

    Columns are standardised internally; `ridge` is a small L2 on the standardised
    coefficients for conditioning (it changes nothing at four figures on 40,000 rows).
    """

    def __init__(self, ridge: float = 1e-4):
        self.ridge = ridge
        self.beta_: np.ndarray | None = None
        self.sigma_: float = np.nan
        self.mu_: np.ndarray | None = None
        self.sd_: np.ndarray | None = None
        self.n_censored_: int = 0

    def _std(self, X: np.ndarray) -> np.ndarray:
        Z = (X - self.mu_) / self.sd_
        Z[:, 0] = 1.0
        return Z

    def fit(self, X: np.ndarray, y: np.ndarray, censored: np.ndarray, weights: np.ndarray | None = None) -> "Tobit":
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        censored = np.asarray(censored, bool)
        w = np.ones(len(y)) if weights is None else np.asarray(weights, float)
        w = w * len(w) / w.sum()
        self.mu_ = X.mean(axis=0)
        self.sd_ = X.std(axis=0)
        self.sd_[self.sd_ == 0] = 1.0
        Z = self._std(X)
        self.n_censored_ = int(censored.sum())
        # warm start: weighted least squares on every row as if uncensored
        b0 = np.linalg.solve(Z.T @ (Z * w[:, None]) + self.ridge * np.eye(Z.shape[1]), Z.T @ (w * y))
        s0 = float(np.sqrt(np.average((y - Z @ b0) ** 2, weights=w))) or 1.0
        unc, cen = ~censored, censored

        def nll(theta):
            b, log_s = theta[:-1], theta[-1]
            s = np.exp(log_s)
            mu = Z @ b
            r = (y - mu) / s
            ll = np.zeros(len(y))
            ll[unc] = norm.logpdf(r[unc]) - log_s
            ll[cen] = norm.logsf(r[cen])
            return -(w * ll).sum() + 0.5 * self.ridge * (b[1:] ** 2).sum()

        def grad(theta):
            b, log_s = theta[:-1], theta[-1]
            s = np.exp(log_s)
            mu = Z @ b
            r = (y - mu) / s
            d_mu = np.zeros(len(y))     # d ll / d mu
            d_ls = np.zeros(len(y))     # d ll / d log s
            d_mu[unc] = r[unc] / s
            d_ls[unc] = r[unc] ** 2 - 1.0
            lam = np.exp(norm.logpdf(r[cen]) - norm.logsf(r[cen]))   # hazard
            d_mu[cen] = lam / s
            d_ls[cen] = lam * r[cen]
            gb = -(Z * (w * d_mu)[:, None]).sum(axis=0)
            gb[1:] += self.ridge * b[1:]
            gs = -(w * d_ls).sum()
            return np.append(gb, gs)

        theta0 = np.append(b0, np.log(s0))
        res = minimize(nll, theta0, jac=grad, method="L-BFGS-B", options={"maxiter": 2000})
        self.beta_ = res.x[:-1]
        self.sigma_ = float(np.exp(res.x[-1]))
        self.converged_ = bool(res.success)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._std(np.asarray(X, float)) @ self.beta_

    def coefficients(self, names: list[str]) -> pd.DataFrame:
        """Coefficients in original units (β / sd), for reading."""
        b = self.beta_ / self.sd_
        b[0] = self.beta_[0] - float(np.sum(self.beta_[1:] * self.mu_[1:] / self.sd_[1:]))
        return pd.DataFrame({"term": names, "coef": b})


# ----------------------------------------------------------------------------
# the models
# ----------------------------------------------------------------------------

SCALE_FREE_GBM = {  # features that do not grow with n, for the residual corrector
    "x": lambda f: f["x"], "log_ratio": lambda f: f["log_ratio"], "opt_frac": lambda f: f["opt_frac"],
    "deg_mean_frac": lambda f: f["g_deg_mean"] / f["n"], "deg_cv": _deg_cv,
    "degen_frac": lambda f: f["g_degeneracy"] / f["n"], "tw_frac": lambda f: f["tw_min_fill"] / f["n"],
    "lcc": lambda f: f["g_largest_comp_frac"], "log_comp": lambda f: np.log10(f["g_components"].astype(float)),
    "clust": lambda f: f["g_clustering"], "row_mean_frac": lambda f: f["row_mean"] / f["m"],
    "log_n": lambda f: np.log10(f["n"]),
}


def gbm_design(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({k: np.asarray(fn(frame), dtype=float) for k, fn in SCALE_FREE_GBM.items()})


class CostModel:
    """Tobit on the linear design (+ drift), optionally a LightGBM correction of its
    residual on scale-free features, fitted on the uncensored training rows."""

    def __init__(self, drift: bool = True, gbm: bool = False, weighting: str = "row", min_n: int = 10,
                 seed: int = 0):
        self.drift, self.gbm, self.weighting, self.min_n, self.seed = drift, gbm, weighting, min_n, seed
        self.tobit = Tobit()
        self.booster = None

    def _weights(self, frame: pd.DataFrame) -> np.ndarray | None:
        if self.weighting == "row":
            return None
        if self.weighting == "per_n":       # every size contributes equally
            counts = frame["n"].map(frame["n"].value_counts())
            return (1.0 / counts).to_numpy(float)
        raise ValueError(self.weighting)

    def fit(self, frame: pd.DataFrame, config: str) -> "CostModel":
        f = frame[frame["n"] >= self.min_n]
        y = f[f"y_{config}"].to_numpy(float)
        cens = f[f"cens_{config}"].to_numpy(bool)
        self.tobit.fit(design(f, self.drift), y, cens, self._weights(f))
        if self.gbm:
            try:
                import lightgbm as lgb
            except ImportError:            # soft import: the linear model stands alone
                self.booster = None
                return self
            unc = ~cens
            resid = y[unc] - self.tobit.predict(design(f, self.drift))[unc]
            self.booster = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leaves=15,
                                             min_child_samples=50, subsample=0.8, subsample_freq=1,
                                             colsample_bytree=0.8, reg_lambda=1.0, random_state=self.seed,
                                             verbose=-1, n_jobs=4)
            self.booster.fit(gbm_design(f[unc]), resid)
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        p = self.tobit.predict(design(frame, self.drift))
        if self.booster is not None:
            p = p + self.booster.predict(gbm_design(frame))
        return p

    @property
    def name(self) -> str:
        return (f"tobit{'+drift' if self.drift else ''}{'+gbm' if self.booster is not None else ''}"
                f" [{self.weighting}, n≥{self.min_n}]")


# ----------------------------------------------------------------------------
# baselines: §11's cell law and §14's surface
# ----------------------------------------------------------------------------

def baselines(campaign40: pd.DataFrame, config: str) -> dict:
    """§11's cell law (fixed generator, fit 15–40, interpolated in col_mean, per m/n
    ratio) and §14's linear surface fitted at n ≤ 30 — both as they were published."""
    laws = {1: cell_laws(campaign40, config, max_n=40), 2: cell_laws(campaign40, config, max_n=40, ratio=2)}
    beta = surface_fit(campaign40[campaign40["n"] <= 30], config)
    return {"laws": laws, "beta": beta}


def baseline_predict(base: dict, frame: pd.DataFrame) -> dict[str, np.ndarray]:
    f = frame.copy()
    for cfg in CONFIGS:
        f[f"ln_{cfg}"] = f[f"y_{cfg}"]
    return {"§11 cell law (fit 15-40, interpolated in col_mean)": laws_predict(base["laws"], f),
            "§14 surface (fit n ≤ 30)": surface_predict(base["beta"], f)}


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------

def within_decade(pred: np.ndarray, y: np.ndarray, censored: np.ndarray, decade: float = DECADE) -> np.ndarray:
    """Hit if |pred − y| ≤ decade on a settled count; a censored count is a lower
    bound, so it is a hit iff the prediction is not more than a decade *below* it
    (the truth could still be within a decade above the prediction) — stated
    wherever the fraction is quoted."""
    pred, y, censored = map(np.asarray, (pred, y, censored))
    hit = np.abs(pred - y) <= decade
    hit_cens = pred >= y - decade
    return np.where(censored, hit_cens, hit)


def evaluate(pred: np.ndarray, y: np.ndarray, censored: np.ndarray, n: np.ndarray) -> pd.DataFrame:
    """Per size band: counts, MAE / bias / RMSE / p90 |error| on settled counts,
    the fraction within a decade (censored as lower bounds), and the fraction of
    censored counts the prediction sits below (a prediction under a lower bound
    is wrong by at least that much)."""
    f = pd.DataFrame({"pred": pred, "y": y, "cens": censored, "n": n})
    f = f[np.isfinite(f["pred"]) & np.isfinite(f["y"])]
    f["band"] = f["n"].apply(band_of)
    f["hit"] = within_decade(f["pred"], f["y"], f["cens"])
    rows = []
    for band in BAND_ORDER:
        g = f[f["band"] == band]
        if g.empty:
            continue
        s = g[~g["cens"]]
        err = (s["pred"] - s["y"]).to_numpy()
        c = g[g["cens"]]
        rows.append({"band": band, "counts": len(g), "settled": len(s), "censored": len(c),
                     "MAE": float(np.mean(np.abs(err))) if len(err) else np.nan,
                     "bias": float(np.mean(err)) if len(err) else np.nan,
                     "RMSE": float(np.sqrt(np.mean(err ** 2))) if len(err) else np.nan,
                     "p90_abs": float(np.quantile(np.abs(err), 0.9)) if len(err) else np.nan,
                     "within_decade": float(g["hit"].mean()),
                     "under_lower_bound": float((c["pred"] < c["y"]).mean()) if len(c) else np.nan})
    return pd.DataFrame(rows)


def decade_claim(pred: np.ndarray, y: np.ndarray, censored: np.ndarray) -> dict:
    """The kill statistic: fraction of the 100–125 counts within one decade, with
    censored counts treated as lower bounds, and the strict version on settled counts only."""
    pred, y, censored = map(np.asarray, (pred, y, censored))
    ok = np.isfinite(pred) & np.isfinite(y)
    pred, y, censored = pred[ok], y[ok], censored[ok]
    hit = within_decade(pred, y, censored)
    settled = ~censored
    return {"counts": int(len(y)), "censored": int(censored.sum()),
            "within_decade": float(hit.mean()) if len(y) else np.nan,
            "within_decade_settled": float(hit[settled].mean()) if settled.any() else np.nan,
            "kill_met": bool(hit.mean() < KILL_COVERAGE) if len(y) else True}


def grouped_cv(frame: pd.DataFrame, config: str, make_model, folds: int = 5, seed: int = 0) -> pd.DataFrame:
    """In-range error at n ≤ 75 by group k-fold (file ∪ isomorphism class)."""
    from sklearn.model_selection import GroupKFold
    tr = frame[training_mask(frame, config)]
    pred = np.full(len(tr), np.nan)
    gkf = GroupKFold(n_splits=folds)
    for a, b in gkf.split(tr, groups=tr["group"]):
        model = make_model().fit(tr.iloc[a], config)
        pred[b] = model.predict(tr.iloc[b])
    return evaluate(pred, tr[f"y_{config}"].to_numpy(), tr[f"cens_{config}"].to_numpy(), tr["n"].to_numpy())


def extrapolation_check(frame: pd.DataFrame, config: str, variants: dict, fit_max_n: int = 60,
                        test_n: tuple = (75,)) -> pd.DataFrame:
    """Model selection without touching the test sizes: fit each variant at n ≤ fit_max_n,
    score at test_n. The variant chosen here is the one fitted at ≤ 75 and sent to 100–125."""
    rows = []
    tr = frame[training_mask(frame, config, max_n=fit_max_n)]
    te_mask = frame["n"].isin(test_n) & np.isfinite(frame[f"y_{config}"])
    if config == "csearch":
        te_mask &= frame["source"].isin(PREFIX_CSEARCH_SOURCES)
    te = frame[te_mask]
    for name, make in variants.items():
        t0 = time.time()
        model = make().fit(tr, config)
        p = model.predict(te)
        ev = evaluate(p, te[f"y_{config}"].to_numpy(), te[f"cens_{config}"].to_numpy(), te["n"].to_numpy())
        r = ev.iloc[0].to_dict() if len(ev) else {}
        r.update({"variant": name, "fit_n": f"≤{fit_max_n}", "test_n": ",".join(map(str, test_n)),
                  "seconds": round(time.time() - t0, 1)})
        rows.append(r)
    out = pd.DataFrame(rows)
    cols = ["variant", "fit_n", "test_n", "counts", "censored", "MAE", "bias", "RMSE", "within_decade", "seconds"]
    return out[[c for c in cols if c in out.columns]].sort_values("MAE").reset_index(drop=True)


# ----------------------------------------------------------------------------
# the noise floor: spread over relabellings of the same instance
# ----------------------------------------------------------------------------

def noise_floor(portfolio: Path = PORTFOLIO_CSV, differential: Path = DIFFERENTIAL_CSV) -> pd.DataFrame:
    """Per band and configuration: the median over instances of the standard
    deviation of log10(1 + nodes) over the labellings run on that instance
    (refutation side, settled calls only), and its p90. This is the error a
    label-free predictor cannot remove."""
    rows = []
    frames = []
    if differential.exists():
        d = pd.read_csv(differential)
        d = d[d["status_lo"] == "unsat"]
        frames.append(d[["base_name", "labelling", "n", "config", "nodes_lo"]].assign(study="differential (§15)"))
    if portfolio.exists():
        p = pd.read_csv(portfolio)
        p = p[p["status_lo"] == "unsat"]
        frames.append(p[["base_name", "labelling", "n", "config", "nodes_lo"]].assign(study="portfolio (§18)"))
    if not frames:
        return pd.DataFrame()
    f = pd.concat(frames, ignore_index=True)
    f["y"] = np.log10(1.0 + f["nodes_lo"].astype(float))
    per = f.groupby(["study", "config", "base_name", "n"]).agg(sd=("y", "std"), labellings=("y", "size"),
                                                                median_y=("y", "median")).reset_index()
    per = per[per["labellings"] >= 4]
    per["band"] = per["n"].apply(band_of)
    for (study, cfg, band), g in per.groupby(["study", "config", "band"]):
        hard = g[g["median_y"] >= 4]
        rows.append({"study": study, "config": cfg, "band": band, "instances": len(g),
                     "labellings": int(g["labellings"].median()),
                     "sd_median": float(g["sd"].median()), "sd_p90": float(g["sd"].quantile(0.9)),
                     "sd_median_hard(≥1e4 nodes)": float(hard["sd"].median()) if len(hard) else np.nan})
    out = pd.DataFrame(rows)
    out["band"] = pd.Categorical(out["band"], BAND_ORDER, ordered=True)
    return out.sort_values(["config", "study", "band"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# the recertify entries: predicted against spent, and the cheapest-first order
# ----------------------------------------------------------------------------

RECERTIFY_ENTRIES = ["Random-125-125-2-1_0", "Random-125-125-2-2_0", "Random-125-125-2-3_0",
                     "Random-125-125-2-4_0", "Random-125-125-2-5_0", "Random-125-125-4-2_0",
                     "Random-125-125-4-4_0", "Random-125-125-4-5_0"]


RECERTIFY_LOG = Path("recertify/run.log")


def recertify_started(log: Path = RECERTIFY_LOG) -> float | None:
    """Epoch seconds of the run's `started YYYY-MM-DD HH:MM:SS` line, if any."""
    if not log.exists():
        return None
    for line in log.read_text().splitlines():
        if line.startswith("started "):
            try:
                return time.mktime(time.strptime(line.split()[1] + " " + line.split()[2], "%Y-%m-%d %H:%M:%S"))
            except (ValueError, IndexError):
                return None
    return None


def open_lower_bound(rec: dict, started: float | None, now: float | None = None) -> tuple[float, float, float]:
    """For an entry still running: (elapsed hours, seconds per node of the finished
    entries (median), log10 of the nodes it must have visited by now). A count in
    progress is censored: a lower bound, never a missing value."""
    if started is None or not rec:
        return np.nan, np.nan, np.nan
    now = time.time() if now is None else now
    rates = [r["seconds"] / r["nodes"] for r in rec.values() if r.get("status") == "unsat" and r["nodes"] > 0]
    if not rates:
        return np.nan, np.nan, np.nan
    spn = float(np.median(rates))
    elapsed = max(now - started, 0.0)
    return elapsed / 3600, spn, float(np.log10(1 + elapsed / spn))


def recertify_table(frame: pd.DataFrame, models: dict[str, "CostModel"], base_preds: dict | None,
                    recertify: Path = RECERTIFY, seconds_per_node: float = SECONDS_PER_NODE_125,
                    started: float | None = None, now: float | None = None,
                    running: set[str] | None = None) -> pd.DataFrame:
    """The eight entries `benchmarks.recertify` opened on 2026-09-24: predicted
    log10 nodes (csearch model, pre-fix counts) against what recertify spent, and
    the cheapest-first order for whatever is still open. An open entry whose worker
    is still running carries the lower bound its elapsed time implies."""
    rec = {r["name"]: r for r in json.load(open(recertify))} if recertify.exists() else {}
    if started is None:
        started = recertify_started()
    elapsed_h, spn, lb = open_lower_bound(rec, started, now)
    rows = []
    f = frame[frame["instance_name"].isin(RECERTIFY_ENTRIES)].drop_duplicates("instance_name").set_index("instance_name")
    for name in RECERTIFY_ENTRIES:
        if name not in f.index:
            continue
        r = f.loc[[name]].reset_index()
        row = {"instance": name, "value": int(r["optimum"].iloc[0]), "col_mean": float(r["col_mean"].iloc[0])}
        for mname, model in models.items():
            p = float(model.predict(r)[0])
            row[f"pred_{mname}"] = p
            row[f"pred_hours_{mname}"] = 10 ** p * seconds_per_node / 3600
        if base_preds is not None:
            for bname, fn in base_preds.items():
                row[f"pred_{bname}"] = float(fn(r)[0])
        if name in rec:
            row["actual_log10_nodes"] = float(np.log10(rec[name]["nodes"]))
            row["actual_hours"] = rec[name]["seconds"] / 3600
            row["status"] = rec[name]["status"]
        else:
            row["actual_log10_nodes"] = np.nan
            row["actual_hours"] = np.nan
            row["status"] = "open"
            if running is None or name in running:
                row["running_hours"] = elapsed_h
                row["log10_nodes_at_least"] = lb          # censored: still running at the finished entries' rate
        rows.append(row)
    out = pd.DataFrame(rows)
    first = next(iter(models))
    out["cheapest_first_rank"] = out[f"pred_{first}"].rank().astype(int)
    return out.sort_values(f"pred_{first}").reset_index(drop=True)


def recertify_rank_agreement(rec: pd.DataFrame, pred_col: str) -> dict:
    """Spearman between predicted and spent on the entries recertify finished."""
    from scipy.stats import spearmanr
    done = rec[np.isfinite(rec["actual_log10_nodes"])]
    if len(done) < 3:
        return {"finished": int(len(done)), "spearman": np.nan}
    rho = spearmanr(done[pred_col], done["actual_log10_nodes"]).statistic
    err = (done[pred_col] - done["actual_log10_nodes"]).to_numpy()
    return {"finished": int(len(done)), "spearman": float(rho), "MAE": float(np.abs(err).mean()),
            "bias": float(err.mean()), "within_decade": float((np.abs(err) <= DECADE).mean())}


# ----------------------------------------------------------------------------
# post-fix csearch counts at 100 (labelled separately)
# ----------------------------------------------------------------------------

def postfix_check(frame: pd.DataFrame, model: "CostModel", portfolio: Path = PORTFOLIO_CSV,
                  race: Path = RACE_CSV) -> pd.DataFrame:
    """The pre-fix csearch model against post-fix csearch counts on the corpus at
    99–100 (portfolio identity rows) and the race's identity at 100 (censored)."""
    rows = []
    if portfolio.exists():
        p = pd.read_csv(portfolio)
        p = p[(p["labelling"] == "identity") & (p["source"] == "corpus") & (p["n"] >= 99)]
        for r in p.itertuples():
            rows.append({"instance": r.base_name, "n": r.n, "m": r.m, "y_postfix": np.log10(1 + r.nodes_lo),
                         "censored": r.status_lo == "unknown", "study": "portfolio identity"})
    if race.exists():
        rc = pd.read_csv(race)
        rc = rc[rc["labelling"] == "identity"]
        for r in rc.itertuples():
            rows.append({"instance": r.base_name, "n": r.n, "m": r.m, "y_postfix": np.log10(1 + r.nodes),
                         "censored": r.status == "unknown", "study": "race identity"})
    if not rows:
        return pd.DataFrame()
    t = pd.DataFrame(rows).drop_duplicates(["instance", "study"])
    feats = frame.drop_duplicates("instance_name").set_index("instance_name")
    t = t[t["instance"].isin(feats.index)]
    t["pred_prefix_model"] = model.predict(feats.loc[t["instance"]].reset_index())
    y_pre = feats.loc[t["instance"], "y_csearch"].to_numpy()
    t["y_prefix_on_record"] = y_pre
    t["hit"] = within_decade(t["pred_prefix_model"], t["y_postfix"], t["censored"])
    t["class"] = t["instance"].str.rsplit("-", n=1).str[0]
    return t.sort_values(["class", "instance"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# report
# ----------------------------------------------------------------------------

def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def variants_for(gbm: bool) -> dict:
    v = {
        "linear, no drift [row]": lambda: CostModel(drift=False, gbm=False, weighting="row"),
        "linear + drift [row]": lambda: CostModel(drift=True, gbm=False, weighting="row"),
        "linear + drift [per_n]": lambda: CostModel(drift=True, gbm=False, weighting="per_n"),
        "linear + drift [row, n≥20]": lambda: CostModel(drift=True, gbm=False, weighting="row", min_n=20),
        "linear + drift [per_n, n≥20]": lambda: CostModel(drift=True, gbm=False, weighting="per_n", min_n=20),
    }
    if gbm:
        v["linear + drift + gbm [row]"] = lambda: CostModel(drift=True, gbm=True, weighting="row")
        v["linear + drift + gbm [per_n, n≥20]"] = lambda: CostModel(drift=True, gbm=True, weighting="per_n", min_n=20)
    return v


def report(configs: tuple[str, ...] = CONFIGS, gbm: bool = True, out: Path = TABLES,
           predictions_csv: Path = PREDICTIONS_CSV, cv_folds: int = 5) -> dict:
    t0 = time.time()
    frame = assemble()
    campaign40 = load_campaign(RESULTS_CSV)
    floor = noise_floor()
    md = [f"# Cost model tables (§19)\n\n*Generated {time.strftime('%Y-%m-%d %H:%M')} by "
          f"`python -m learning.cost_model`. Every log is log10(1 + nodes); a censored count is a lower bound.*\n"]
    counts = frame.groupby(["source", "band"]).agg(rows=("instance_name", "size"),
                                                  default=("y_default", lambda s: int(np.isfinite(s).sum())),
                                                  csearch=("y_csearch", lambda s: int(np.isfinite(s).sum()))).reset_index()
    md.append("## Rows on record by source and band\n\n" + _md(counts) + "\n")
    md.append("## Noise floor: sd of log10(1 + nodes) over relabellings of one instance (refutation, settled)\n\n"
              + _md(floor, ".3f") + "\n")
    dating = date_upward_csearch()
    if len(dating):
        md.append("## Dating the upward run's csearch counts (post-fix identity counts of §18 against the run)\n\n"
                  + _md(dating["verdict"].value_counts().rename_axis("verdict").reset_index(name="cells")) + "\n")
    results = {"frame_rows": len(frame), "noise_floor": floor, "dating": dating}
    all_preds = []
    fitted: dict[str, CostModel] = {}
    for cfg in configs:
        md.append(f"\n# Configuration `{cfg}`" + (" (pre-fix counts only)" if cfg == "csearch" else "") + "\n")
        variants = variants_for(gbm)
        ext = extrapolation_check(frame, cfg, variants)
        md.append("## Model selection: fit n ≤ 60, score at 75 (test sizes untouched)\n\n" + _md(ext) + "\n")
        chosen_name = ext.iloc[0]["variant"]
        chosen_linear = ext[~ext["variant"].str.contains("gbm")].iloc[0]["variant"]
        make_chosen = variants[chosen_name]
        make_linear = variants[chosen_linear]
        model = make_chosen().fit(frame[training_mask(frame, cfg)], cfg)
        linear = make_linear().fit(frame[training_mask(frame, cfg)], cfg)
        base = baselines(campaign40, cfg)
        te = frame[test_mask(frame, cfg)]
        preds = {"chosen: " + chosen_name: model.predict(te)}
        if chosen_linear != chosen_name:
            preds["linear: " + chosen_linear] = linear.predict(te)
        preds.update(baseline_predict(base, te))
        y, cens, n = te[f"y_{cfg}"].to_numpy(), te[f"cens_{cfg}"].to_numpy(), te["n"].to_numpy()
        md.append("## Error at the test sizes (fit n ≤ 75)\n")
        claims = {}
        for name, p in preds.items():
            ev = evaluate(p, y, cens, n)
            claims[name] = decade_claim(p, y, cens)
            md.append(f"### {name}\n\n" + _md(ev) + "\n")
        claim_tbl = pd.DataFrame([{"predictor": k, **v} for k, v in claims.items()])
        md.append("### The decade claim at 100–125 (kill: < 80% within one decade)\n\n" + _md(claim_tbl) + "\n")
        # per class at the test sizes for the chosen model
        te2 = te.copy()
        te2["pred"] = preds["chosen: " + chosen_name]
        te2["class"] = np.where(te2["source"] == "corpus", te2["instance_name"].str.rsplit("-", n=1).str[0],
                                te2["instance_name"].str.rsplit("_i", n=1).str[0])
        te2["hit"] = within_decade(te2["pred"], te2[f"y_{cfg}"], te2[f"cens_{cfg}"])
        te2["err"] = np.where(te2[f"cens_{cfg}"], np.nan, te2["pred"] - te2[f"y_{cfg}"])
        percls = te2.groupby(["class", "n"]).agg(counts=("pred", "size"), censored=(f"cens_{cfg}", "sum"),
                                                  median_y=(f"y_{cfg}", "median"), median_pred=("pred", "median"),
                                                  bias=("err", "mean"), within_decade=("hit", "mean")).reset_index()
        md.append("### Chosen model by class at 100 and 125\n\n" + _md(percls) + "\n")
        cv = grouped_cv(frame, cfg, make_chosen, folds=cv_folds)
        md.append(f"## In-range error at n ≤ 75, {cv_folds}-fold grouped by file ∪ class (chosen model)\n\n"
                  + _md(cv) + "\n")
        coef = linear.tobit.coefficients(term_names(linear.drift))
        md.append(f"## Linear Tobit coefficients ({chosen_linear}; σ = {linear.tobit.sigma_:.3f}, "
                  f"{linear.tobit.n_censored_} censored training rows)\n\n" + _md(coef, ".4g") + "\n")
        results[cfg] = {"chosen": chosen_name, "linear": chosen_linear, "selection": ext, "claims": claims,
                        "per_class": percls, "cv": cv, "model": model, "linear_model": linear,
                        "sigma": linear.tobit.sigma_, "test_rows": len(te)}
        fitted[cfg] = model
        fitted[f"{cfg}_linear"] = linear
        te2["config"] = cfg
        te2["predictor"] = chosen_name
        all_preds.append(te2[["instance_name", "source", "config", "n", "m", "col_mean", "optimum",
                              f"y_{cfg}", f"cens_{cfg}", "pred", "hit", "predictor"]]
                         .rename(columns={f"y_{cfg}": "y", f"cens_{cfg}": "censored"}))
        if cfg == "csearch":
            base_fns = {k: (lambda r, k=k: baseline_predict(base, r)[k]) for k in
                        baseline_predict(base, te.head(1)).keys()}
            models = {"csearch": model, "csearch_linear": linear}
            models.update({k: v for k, v in fitted.items() if k.startswith("default")})
            rec = recertify_table(frame, models, base_fns)
            agree = pd.DataFrame([{"predictor": k, **recertify_rank_agreement(rec, f"pred_{k}")}
                                  for k in list(models) + list(base_fns)])
            md.append("## The recertify entries: predicted against spent (the csearch counts are pre-fix; "
                      "hours at 0.55 µs/node; `default` columns are the other configuration's model, an upper reference)\n\n"
                      + _md(rec, ".3g") + "\n\n### Rank agreement on the finished entries\n\n" + _md(agree, ".3g") + "\n")
            results["recertify"] = rec
            results["recertify_agreement"] = agree
            rec.to_csv(predictions_csv.with_name("cost_model_recertify.csv"), index=False)
            post = postfix_check(frame, model)
            if len(post):
                summ = post.groupby(["study", "class"]).agg(instances=("instance", "size"),
                                                            censored=("censored", "sum"),
                                                            median_pred=("pred_prefix_model", "median"),
                                                            median_postfix=("y_postfix", "median"),
                                                            median_prefix=("y_prefix_on_record", "median"),
                                                            within_decade=("hit", "mean")).reset_index()
                md.append("## Post-fix csearch counts at 99–100 against the pre-fix model (labelled; not the test set)\n\n"
                          + _md(summ) + "\n")
                results["postfix"] = post
    if all_preds:
        pd.concat(all_preds, ignore_index=True).to_csv(predictions_csv, index=False)
    md.append(f"\n*{time.time() - t0:.0f} s.*\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md))
    results["seconds"] = time.time() - t0
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", choices=("default", "csearch", "both"), default="both")
    ap.add_argument("--no-gbm", action="store_true", help="linear Tobit variants only")
    ap.add_argument("--tables", type=Path, default=TABLES)
    ap.add_argument("--folds", type=int, default=5)
    args = ap.parse_args()
    cfgs = CONFIGS if args.config == "both" else (args.config,)
    res = report(cfgs, gbm=not args.no_gbm, out=args.tables, cv_folds=args.folds)
    for cfg in cfgs:
        r = res[cfg]
        print(f"[{cfg}] chosen {r['chosen']}; σ = {r['sigma']:.3f}; test rows {r['test_rows']}")
        for k, v in r["claims"].items():
            print(f"    {k}: within a decade {v['within_decade']:.3f} ({v['counts']} counts, "
                  f"{v['censored']} censored); settled only {v['within_decade_settled']:.3f}; kill met: {v['kill_met']}")
    if "recertify" in res:
        print(res["recertify"].to_string())
    print(f"tables: {args.tables}; predictions: {PREDICTIONS_CSV}; {res['seconds']:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
