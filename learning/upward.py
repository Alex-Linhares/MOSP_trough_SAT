"""The campaign upward: does the ridge law hold at 50-100, and at what rate? (§16, plan 2 §2.2)

Question. §11 fitted, on generated instances at 15-40 customers, the rate at
which the nodes to refute `optimum - 1` grow with `n` at fixed customers per
product: 0.095 log10 per customer on the `m = n` ridge (d = 3), 0.062 at d = 2,
0.085 at d = 6. §14 found the corpus's own rates at 30-125 lower by
0.005-0.018 per customer, measured on five Chu & Stuckey instances per class.
Which is right, does the rate drift with `n`, and where is the drift resolved?
This module answers with the campaign extended to n in {50, 60, 75} at
m in {n/2, n, 2n} (50 per cell, the half ratio for the first time) and to
n = 100 on the `m = n` ridge and its two neighbours -- sampled, because the
§11 law prices the full 25-per-cell run at 40 core-hours against the plan's
cap of 8 (`learning.ensemble.price_ridge100`).

Method. Nodes, never seconds. Per cell and configuration the median of
log10(1 + nodes) with a flag when a censored count (deadline, a lower bound)
sits at or below it, so that median is itself a lower bound; the local rate
between consecutive sizes with a bootstrap band over instances; the drift of
the local rate with its midpoint `n`, per density and pooled within series;
global exponential fits on 15-40 (§11's), 15-75 and 15-100; the ridge
location per size and ratio; Theorem 2's saving (`csearch / default`) at the
half ratio; and a revised prediction for the 125 x 125 Chu & Stuckey classes
from the 100-customer cells with an error band, against the five recertify
counts on record. Corpus classes come from `learning.scale_test.load_corpus`.

Nothing here is a bound, no solver default changes, nothing is written to
`solutions/`. The run itself is `python -m learning.ensemble --upward ...`
(see `reports/ml_nature.md` §16 for the exact command); this module reads
`learning/data/ensemble/results.csv` (10-40) and `results_upward.csv`
(50-100) and writes `reports/upward_tables.md`.

Usage:
    python -m learning.ensemble --upward --ridge100-per-cell 25 --ridge100-sample 5 \
        --deadline 900 --solve-budget 900 --workers 16 --out reports/upward_ensemble_tables.md
    python -m learning.upward --finish-uncertified --deadline 1800 --workers 12
                                                 # decide value - 1 for the n = 100 rows whose descent ran out
    python -m learning.upward                    # the tables, ~10 s
    python -m pytest tests/test_upward.py -q
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.ensemble import RESULTS_CSV, RESULTS_UPWARD_CSV, load_results
from learning.hardness_map import fit_scaling

TABLES = Path("reports/upward_tables.md")
FINISH_CSV = RESULTS_UPWARD_CSV.with_name("results_upward_finish.csv")   # the finish stage's answers, merged on load
RECERTIFY = Path("recertify/results.json")
CONFIGS = ("default", "csearch")
RATIOS = (0.5, 1.0, 2.0)
RIDGE_D = 3.0                     # §11: the m = n ridge of the fixed generator
SEED = 0


# ----------------------------------------------------------------------------
# loading
# ----------------------------------------------------------------------------


def prepare(frame: pd.DataFrame) -> pd.DataFrame:
    """Add `ratio` (m / n to one decimal), `opt_frac`, and per configuration
    `ln_<cfg>` = log10(1 + nodes) and `cens_<cfg>` (deadline: a lower bound)."""
    out = frame.copy()
    out["ratio"] = (out["m"] / out["n"]).round(1)
    out["opt_frac"] = out["optimum"] / out["n"]
    for cfg in CONFIGS:
        out[f"ln_{cfg}"] = np.log10(1.0 + out[f"nodes_{cfg}"].astype(float))
        out[f"cens_{cfg}"] = out[f"status_{cfg}"].eq("unknown")
    return out


def load_all(campaign_csv: Path = RESULTS_CSV, upward_csv: Path = RESULTS_UPWARD_CSV) -> pd.DataFrame:
    """§10's 10-40 campaign and §16's 50-100 rows in one frame, `source` says which."""
    parts = []
    for source, csv in (("campaign", campaign_csv), ("upward", upward_csv)):
        f = load_results(csv)
        if len(f):
            f = f.copy()
            if source == "upward":
                f = apply_finish(f, csv.with_name("results_upward_finish.csv"))
            f["source"] = source
            parts.append(f)
    if not parts:
        return pd.DataFrame()
    return prepare(pd.concat(parts, ignore_index=True))


# ----------------------------------------------------------------------------
# per-cell statistics, censoring-aware
# ----------------------------------------------------------------------------


def censored_median(values: np.ndarray, censored: np.ndarray) -> tuple[float, bool]:
    """The sample median treating censored values as what they are, lower
    bounds; the flag says whether any censored value sits at or below the
    median, in which case the median is itself only a lower bound."""
    values = np.asarray(values, dtype=float)
    censored = np.asarray(censored, dtype=bool)
    if len(values) == 0:
        return np.nan, False
    med = float(np.median(values))
    return med, bool(np.any(censored & (values <= med)))


def cell_stats(frame: pd.DataFrame, config: str = "default") -> pd.DataFrame:
    """Per (generator, ratio, param, n): counts, the censoring-aware median of
    log10(1 + nodes), the p90, the realised density and the optimum."""
    rows = []
    ln, cens = f"ln_{config}", f"cens_{config}"
    for (gen, ratio, param, n), g in frame.groupby(["generator", "ratio", "param", "n"]):
        cert = g[g["certified"].astype(bool)]
        med, is_lb = censored_median(cert[ln].to_numpy(), cert[cens].to_numpy())
        other = "csearch" if config == "default" else "default"
        both = cert.dropna(subset=[f"nodes_{config}", f"nodes_{other}"])
        rows.append({
            "generator": gen, "ratio": float(ratio), "param": float(param), "n": int(n),
            "instances": len(g), "certified": len(cert),
            "classes": int(g["graph_cert"].nunique()),
            "censored": int(cert[cens].sum()),
            "median_log_nodes": round(med, 3), "median_is_lower_bound": is_lb,
            "p90_log_nodes": round(float(cert[ln].quantile(0.9)), 3) if len(cert) else np.nan,
            "col_mean": round(float(g["col_mean"].median()), 2),
            "opt_mean": round(float(g["optimum"].mean()), 2),
            "opt_cv": round(float(g["optimum"].std(ddof=0) / max(g["optimum"].mean(), 1e-9)), 3),
            "decomposable": round(float((g["g_components"] > 1).mean()), 3),
            "complete": round(float(g["complete_graph"].astype(bool).mean()), 3),
            "cs_over_default": round(float((both["nodes_csearch"] / both["nodes_default"].clip(lower=1)).median()), 3)
            if len(both) else np.nan,
        })
    return pd.DataFrame(rows).sort_values(["generator", "ratio", "param", "n"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# local rates, their bands, and their drift
# ----------------------------------------------------------------------------


def _bootstrap_rate(a: np.ndarray, b: np.ndarray, dn: float, resamples: int, rng: np.random.Generator) -> tuple[float, float]:
    """5th and 95th percentile of (median(b*) - median(a*)) / dn over instance resamples."""
    if len(a) == 0 or len(b) == 0:
        return np.nan, np.nan
    ia = rng.integers(0, len(a), size=(resamples, len(a)))
    ib = rng.integers(0, len(b), size=(resamples, len(b)))
    rates = (np.median(b[ib], axis=1) - np.median(a[ia], axis=1)) / dn
    return float(np.percentile(rates, 5)), float(np.percentile(rates, 95))


def local_rates(frame: pd.DataFrame, config: str = "default", generator: str = "fixed",
                resamples: int = 400, seed: int = SEED, min_median: float = 0.3) -> pd.DataFrame:
    """Between consecutive sizes of each (ratio, d) series: the rate of the
    cell median of log10 nodes per customer, a 90% bootstrap band over
    instances, and whether either end is a lower bound (then so is the rate's
    reading: an upper end censored means the true rate is at least this).

    Cells whose median is below `min_median` log10 (a couple of nodes) are
    skipped: at that level the count is dominated by the +1 and by discreteness.
    """
    rng = np.random.default_rng(seed)
    ln, cens = f"ln_{config}", f"cens_{config}"
    sub = frame[(frame["generator"] == generator) & frame["certified"].astype(bool)]
    rows = []
    for (ratio, param), g in sub.groupby(["ratio", "param"]):
        sizes = sorted(g["n"].unique())
        cells = {n: g[g["n"] == n] for n in sizes}
        meds = {n: censored_median(cells[n][ln].to_numpy(), cells[n][cens].to_numpy()) for n in sizes}
        for n1, n2 in zip(sizes[:-1], sizes[1:]):
            (m1, lb1), (m2, lb2) = meds[n1], meds[n2]
            if m1 < min_median:
                continue
            rate = (m2 - m1) / (n2 - n1)
            lo, hi = _bootstrap_rate(cells[n1][ln].to_numpy(), cells[n2][ln].to_numpy(), n2 - n1, resamples, rng)
            rows.append({"generator": generator, "ratio": float(ratio), "param": float(param),
                         "col_mean": round(float(g["col_mean"].median()), 2),
                         "n1": int(n1), "n2": int(n2), "mid_n": (n1 + n2) / 2,
                         "median1": round(m1, 3), "median2": round(m2, 3),
                         "rate": round(rate, 4), "rate_lo": round(lo, 4), "rate_hi": round(hi, 4),
                         "doubling_n": round(float(np.log10(2) / rate), 2) if rate > 0 else np.inf,
                         "upper_end_censored": lb2, "lower_end_censored": lb1,
                         "reading": "rate is a lower bound" if (lb2 and not lb1) else
                                    ("rate unreliable: both ends censored" if (lb1 and lb2) else
                                     ("rate is an upper bound" if lb1 else "exact"))})
    return pd.DataFrame(rows)


def drift(rates: pd.DataFrame, exact_only: bool = True) -> pd.DataFrame:
    """Per (ratio, d): the slope of the local rate against its midpoint `n`,
    in log10 per customer per customer, with its standard error and the number
    of intervals; a negative slope is a rate that falls with size. Only
    intervals whose reading is exact unless `exact_only` is false."""
    rows = []
    r = rates[rates["reading"] == "exact"] if exact_only else rates
    for (ratio, param), g in r.groupby(["ratio", "param"]):
        g = g.sort_values("mid_n")
        row = {"ratio": float(ratio), "param": float(param), "col_mean": float(g["col_mean"].iloc[0]),
               "intervals": len(g), "n_range": f"{int(g['n1'].min())}-{int(g['n2'].max())}",
               "rate_first": float(g["rate"].iloc[0]), "rate_last": float(g["rate"].iloc[-1]),
               "rate_mean_15_40": round(float(g[g["n2"] <= 40]["rate"].mean()), 4) if (g["n2"] <= 40).any() else np.nan,
               "rate_mean_50_up": round(float(g[g["n1"] >= 50]["rate"].mean()), 4) if (g["n1"] >= 50).any() else np.nan}
        if len(g) >= 3:
            x, y = g["mid_n"].to_numpy(float), g["rate"].to_numpy(float)
            slope, intercept = np.polyfit(x, y, 1)
            resid = y - (intercept + slope * x)
            se = float(np.sqrt(np.sum(resid ** 2) / (len(x) - 2) / np.sum((x - x.mean()) ** 2))) if len(x) > 2 else np.nan
            row.update(slope_per_customer=round(float(slope), 6), slope_se=round(se, 6),
                       t=round(float(slope / se), 2) if se and se > 0 else np.nan)
        else:
            row.update(slope_per_customer=np.nan, slope_se=np.nan, t=np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


def pooled_drift(rates: pd.DataFrame, min_series: int = 3) -> dict:
    """One slope for all series: regress the local rate on midpoint `n` after
    removing each (ratio, d) series' own mean (a within-series estimate), on
    exact intervals only. Returns slope, its standard error and the count."""
    r = rates[rates["reading"] == "exact"].copy()
    key = list(zip(r["ratio"], r["param"]))
    r["key"] = key
    counts = r["key"].value_counts()
    r = r[r["key"].map(counts) >= min_series]
    if len(r) < 4:
        return {"slope": np.nan, "se": np.nan, "intervals": len(r), "series": 0}
    x = r["mid_n"] - r.groupby("key")["mid_n"].transform("mean")
    y = r["rate"] - r.groupby("key")["rate"].transform("mean")
    x, y = x.to_numpy(float), y.to_numpy(float)
    slope = float(np.sum(x * y) / np.sum(x ** 2))
    resid = y - slope * x
    dof = len(x) - r["key"].nunique() - 1
    se = float(np.sqrt(np.sum(resid ** 2) / max(dof, 1) / np.sum(x ** 2)))
    return {"slope": slope, "se": se, "intervals": len(r), "series": int(r["key"].nunique()),
            "t": slope / se if se > 0 else np.nan}


# ----------------------------------------------------------------------------
# global fits, ridge, Theorem 2
# ----------------------------------------------------------------------------


def global_fits(cells: pd.DataFrame, generator: str = "fixed",
                windows=((15, 40), (15, 75), (15, 100), (50, 100))) -> pd.DataFrame:
    """`fit_scaling` (exponential against power law) per (ratio, d) on each
    window of sizes, using only cells whose median is not a lower bound."""
    rows = []
    sub = cells[(cells["generator"] == generator) & ~cells["median_is_lower_bound"]]
    for (ratio, param), g in sub.groupby(["ratio", "param"]):
        seen: set[tuple] = set()
        for lo, hi in windows:
            h = g[(g["n"] >= lo) & (g["n"] <= hi)].sort_values("n")
            if len(h) < 3 or tuple(h["n"]) in seen:      # a window that adds no cell is the same fit
                continue
            seen.add(tuple(h["n"]))
            fit = fit_scaling(h["n"].to_numpy(), (10 ** h["median_log_nodes"].to_numpy()) - 1.0)
            if fit["points"] < 3:
                continue
            rows.append({"ratio": float(ratio), "param": float(param), "col_mean": float(g["col_mean"].median()),
                         "window": f"{lo}-{hi}", "points": fit["points"],
                         "rate": round(fit["rate"], 4), "doubling_n": round(fit["doubling_n"], 2),
                         "rms_exp": round(fit["rms_exp"], 3), "alpha": round(fit["alpha"], 2),
                         "rms_pow": round(fit["rms_pow"], 3), "better": fit["better"]})
    return pd.DataFrame(rows)


def ridge_location(cells: pd.DataFrame) -> pd.DataFrame:
    """Per (generator, ratio, n): the cell with the largest median log nodes,
    its parameter and realised density, and the second-largest for context."""
    rows = []
    for (gen, ratio, n), g in cells.groupby(["generator", "ratio", "n"]):
        g = g.sort_values("median_log_nodes", ascending=False)
        top = g.iloc[0]
        rows.append({"generator": gen, "ratio": float(ratio), "n": int(n),
                     "peak_param": float(top["param"]), "peak_col_mean": float(top["col_mean"]),
                     "peak_median_log_nodes": float(top["median_log_nodes"]),
                     "peak_is_lower_bound": bool(top["median_is_lower_bound"]),
                     "runner_up_param": float(g.iloc[1]["param"]) if len(g) > 1 else np.nan,
                     "runner_up_median_log_nodes": float(g.iloc[1]["median_log_nodes"]) if len(g) > 1 else np.nan})
    return pd.DataFrame(rows)


def theorem2(frame: pd.DataFrame) -> pd.DataFrame:
    """`csearch / default` nodes per (ratio, n) over certified instances with
    both counts settled: the median ratio, the share where csearch is fewer,
    and the share where the switch was on (mean products per customer <= 5)."""
    rows = []
    sub = frame[frame["certified"].astype(bool) & ~frame["cens_default"] & ~frame["cens_csearch"]]
    for (ratio, n), g in sub.groupby(["ratio", "n"]):
        ratio_nodes = g["nodes_csearch"] / g["nodes_default"].clip(lower=1)
        on = g["row_mean"] <= 5 if "row_mean" in g else pd.Series(False, index=g.index)
        rows.append({"ratio": float(ratio), "n": int(n), "instances": len(g),
                     "median_ratio": round(float(ratio_nodes.median()), 3),
                     "median_ratio_when_on": round(float(ratio_nodes[on].median()), 3) if on.any() else np.nan,
                     "p10_ratio": round(float(ratio_nodes.quantile(0.1)), 3),
                     "csearch_fewer": round(float((g["nodes_csearch"] < g["nodes_default"]).mean()), 3),
                     "csearch_more": round(float((g["nodes_csearch"] > g["nodes_default"]).mean()), 3),
                     "switch_on": round(float((g["row_mean"] <= 5).mean()), 3) if "row_mean" in g else np.nan})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# the corpus and the 125 x 125 prediction
# ----------------------------------------------------------------------------


def corpus_classes() -> pd.DataFrame:
    """Chu & Stuckey `Random-n-n-d` classes: median log10 nodes per size and
    local rates, from `learning.scale_test` (its `corpus_scaling`), default
    configuration, sizes where every count settled."""
    from learning.scale_test import corpus_scaling, load_corpus

    corpus = load_corpus()
    if corpus.empty:
        return pd.DataFrame()
    out = corpus_scaling(corpus, "default")
    cm = corpus[corpus["m"] == corpus["n"]].groupby("d")["col_mean"].median()
    out["col_mean"] = out["d"].map(cm).round(2)
    return out


def recertify_counts(path: Path = RECERTIFY) -> pd.DataFrame:
    """The 125 x 125 refutation counts on record (`better_move=True`, the
    csearch configuration on these sparse instances), with the density class."""
    if not path.exists():
        return pd.DataFrame(columns=["name", "d", "log_nodes", "hours"])
    rec = pd.DataFrame(json.load(open(path)))
    rec = rec[rec["status"] == "unsat"].copy()
    rec["d"] = rec["name"].str.split("-").str[3].astype(int)
    rec["log_nodes"] = np.log10(rec["nodes"].astype(float)).round(2)
    rec["hours"] = (rec["seconds"] / 3600).round(1)
    return rec[["name", "d", "log_nodes", "hours"]].sort_values(["d", "name"]).reset_index(drop=True)


def predict_125(frame: pd.DataFrame, rates: pd.DataFrame, cells: pd.DataFrame, config: str = "default",
                target_n: int = 125, from_n: int = 100, resamples: int = 400, seed: int = SEED) -> pd.DataFrame:
    """For each `m = n` fixed-d series that reaches `from_n`: the cell median
    there (flagged if a lower bound), the local rate over the last interval
    with its band, and the extrapolation to `target_n` with a band that
    combines the bootstrap spread of the 100-customer median and of the rate.
    Beside it: the extrapolation using the 15-40 §11 law, and the 50-75 rate.
    """
    rng = np.random.default_rng(seed)
    ln, cens = f"ln_{config}", f"cens_{config}"
    rows = []
    fx = cells[(cells["generator"] == "fixed") & (cells["ratio"] == 1.0)]
    for param, g in fx.groupby("param"):
        if from_n not in set(g["n"]):
            continue
        at = g[g["n"] == from_n].iloc[0]
        inst = frame[(frame["generator"] == "fixed") & (frame["ratio"] == 1.0) & (frame["param"] == param)
                     & (frame["n"] == from_n) & frame["certified"].astype(bool)]
        vals = inst[ln].to_numpy(float)
        if len(vals) == 0:
            continue
        boot = np.median(vals[rng.integers(0, len(vals), size=(resamples, len(vals)))], axis=1)
        med_lo, med_hi = float(np.percentile(boot, 5)), float(np.percentile(boot, 95))
        last = rates[(rates["ratio"] == 1.0) & (rates["param"] == param) & (rates["n2"] == from_n)]
        prev = rates[(rates["ratio"] == 1.0) & (rates["param"] == param) & (rates["n2"] == 75)]
        law = global_fits(cells[(cells["generator"] == "fixed") & (cells["ratio"] == 1.0) & (cells["param"] == param)],
                          windows=((15, 40),))
        dn = target_n - from_n
        row = {"d": float(param), "col_mean": float(at["col_mean"]), "instances_at_100": int(at["certified"]),
               "censored_at_100": int(at["censored"]),
               "median_log_nodes_100": float(at["median_log_nodes"]), "median_100_is_lower_bound": bool(at["median_is_lower_bound"]),
               "median_100_band": f"[{med_lo:.2f}, {med_hi:.2f}]"}
        if len(last):
            r = last.iloc[0]
            row.update(rate_75_100=float(r["rate"]), rate_75_100_band=f"[{r['rate_lo']:.4f}, {r['rate_hi']:.4f}]",
                       rate_75_100_reading=r["reading"],
                       pred_125_log_nodes=round(float(at["median_log_nodes"]) + dn * float(r["rate"]), 2),
                       pred_125_band=f"[{med_lo + dn * r['rate_lo']:.2f}, {med_hi + dn * r['rate_hi']:.2f}]")
        if len(prev):
            r = prev.iloc[0]
            row.update(rate_60_75=float(r["rate"]),
                       pred_125_with_60_75_rate=round(float(at["median_log_nodes"]) + dn * float(r["rate"]), 2))
        if len(law):
            lw = law.iloc[0]
            # a + b n from the 15-40 window: reconstruct from the fitted rate through the 40 cell
            at40 = g[g["n"] == 40]
            if len(at40):
                row.update(law_15_40_rate=float(lw["rate"]),
                           law_15_40_at_100=round(float(at40.iloc[0]["median_log_nodes"]) + 60 * float(lw["rate"]), 2),
                           law_15_40_at_125=round(float(at40.iloc[0]["median_log_nodes"]) + 85 * float(lw["rate"]), 2))
        rows.append(row)
    return pd.DataFrame(rows)


def extrapolate(cells: pd.DataFrame, rates: pd.DataFrame, pooled: dict, config: str = "default",
                from_n: int = 75, targets=(100, 125), ratio: float = 1.0, ds=(2.0, 3.0, 4.0)) -> pd.DataFrame:
    """From the last fully certified size: the cell median plus the last local
    rate, held constant and, alternatively, drifting at the pooled slope
    (rate(n) = rate_last + slope (n - mid_last)). The band on the constant-rate
    figure is the bootstrap band of the last rate; on the drifting one, that
    band moved by the slope's standard error. What §14 quoted for 125 is the
    §11 law (15-40, constant rate); this table is what the 50-75 cells say."""
    rows = []
    for d in ds:
        g = cells[(cells["generator"] == "fixed") & (cells["ratio"] == ratio) & (cells["param"] == d)]
        at = g[g["n"] == from_n]
        last = rates[(rates["ratio"] == ratio) & (rates["param"] == d) & (rates["n2"] == from_n)]
        if at.empty or last.empty:
            continue
        m0 = float(at.iloc[0]["median_log_nodes"])
        r = last.iloc[0]
        rate, lo, hi, mid = float(r["rate"]), float(r["rate_lo"]), float(r["rate_hi"]), float(r["mid_n"])
        slope, se = float(pooled["slope"]), float(pooled["se"])
        row = {"d": d, "col_mean": float(at.iloc[0]["col_mean"]), "from_n": from_n,
               "median_log_nodes_from": round(m0, 3), "from_is_lower_bound": bool(at.iloc[0]["median_is_lower_bound"]),
               "rate_last": rate, "rate_last_band": f"[{lo:.4f}, {hi:.4f}]", "rate_last_reading": r["reading"],
               "drift_slope": round(slope, 6)}
        for t in targets:
            dn = t - from_n
            row[f"const_{t}"] = round(m0 + dn * rate, 2)
            row[f"const_{t}_band"] = f"[{m0 + dn * lo:.2f}, {m0 + dn * hi:.2f}]"
            # integral of rate_last + slope (n - mid) from from_n to t
            drift_term = slope * ((t ** 2 - from_n ** 2) / 2 - mid * dn)
            se_term = se * abs((t ** 2 - from_n ** 2) / 2 - mid * dn)
            row[f"drift_{t}"] = round(m0 + dn * rate + drift_term, 2)
            row[f"drift_{t}_band"] = f"[{m0 + dn * lo + drift_term - se_term:.2f}, {m0 + dn * hi + drift_term + se_term:.2f}]"
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# finishing the n = 100 cells: refute the uncertified values with a longer deadline
# ----------------------------------------------------------------------------


def _finish_job(args) -> dict:
    from learning.ensemble import Cell, generate
    from learning.node_counts import refute

    name, generator, n, m, param, index, value, config, deadline = args
    inst = generate(Cell(generator, int(n), int(m), float(param)), int(index))
    assert inst.name == name
    out = refute(inst, int(value), config, deadline)
    out.update(instance_name=name)
    return out


def finish_uncertified(csv: Path = RESULTS_UPWARD_CSV, deadline: float = 1800.0, workers: int = 12,
                       min_n: int = 100, verbose: bool = True, out: Path | None = None) -> pd.DataFrame:
    """Rows whose descent ran out of its solve budget carry a verified upper
    bound and no refutation. This stage decides `value - 1` under both
    configurations with a longer deadline and records the answers in a
    separate CSV (`FINISH_CSV`, one row per call) that `load_all` merges over
    the run's rows -- separate, so that it never rewrites a file the campaign
    may still be appending to. `unsat` certifies the value, `unknown` is a
    censored count (a lower bound on the nodes, recorded as such), `sat` means
    the value was not the optimum and is recorded, never hidden. The `csearch`
    jobs go first: at these sizes Theorem 2 is on and settles sooner (§14).
    Calls already answered in `out` are not repeated."""
    import multiprocessing

    out = out or csv.with_name("results_upward_finish.csv")
    frame = load_results(csv)
    todo = frame[(~frame["certified"].astype(bool)) & (frame["n"] >= min_n)]
    done = set()
    if out.exists() and out.stat().st_size:
        prev = pd.read_csv(out)
        done = set(zip(prev["instance_name"], prev["config"]))
    jobs = [(r.instance_name, r.generator, r.n, r.m, r.param, r.index, r.optimum, cfg, deadline)
            for cfg in ("csearch", "default") for r in todo.itertuples()
            if (r.instance_name, cfg) not in done]
    if verbose:
        print(f"{len(todo)} uncertified rows at n >= {min_n}; {len(jobs)} decision calls on {workers} workers, "
              f"{deadline:g} s deadline each; answers to {out}", flush=True)
    if not jobs:
        return apply_finish(frame, out)
    started = time.time()
    with multiprocessing.Pool(workers) as pool:
        for res in pool.imap_unordered(_finish_job, jobs, chunksize=1):
            row = pd.DataFrame([{"instance_name": res["instance_name"], "config": res["config"],
                                 "value": int(frame.loc[frame["instance_name"] == res["instance_name"], "optimum"].iloc[0]),
                                 "status": res["status"], "nodes": res["nodes"], "seconds": res["seconds"],
                                 "deadline_seconds": deadline}])
            row.to_csv(out, mode="a", header=not out.exists() or out.stat().st_size == 0, index=False)
            if verbose:
                print(f"  {res['instance_name']} {res['config']}: {res['status']} {res['nodes']} nodes "
                      f"{res['seconds']:.0f} s [{time.time() - started:.0f} s]", flush=True)
    return apply_finish(load_results(csv), out)


def hard100_table(csv: Path = RESULTS_UPWARD_CSV, finish_csv: Path = FINISH_CSV) -> pd.DataFrame:
    """The n = 100, d in {3, 4} sample, instance by instance: the value the
    900 s descent reached and the nodes it spent, whether it certified, and
    the finish stage's answer under each configuration (`sat` = the value was
    not optimal; `unknown` = censored, nodes a lower bound)."""
    frame = load_results(csv)
    sub = frame[(frame["n"] >= 100) & (frame["param"] >= 3)].sort_values("instance_name")
    fin = pd.read_csv(finish_csv) if finish_csv.exists() and finish_csv.stat().st_size else pd.DataFrame(
        columns=["instance_name", "config", "status", "nodes", "seconds"])
    rows = []
    for r in sub.itertuples():
        row = {"instance": r.instance_name, "value": int(r.optimum), "col_mean": round(float(r.col_mean), 2),
               "descent_s": round(float(r.solve_seconds)), "descent_nodes_log10": round(float(np.log10(1 + float(r.solve_nodes))), 2),
               "certified_in_run": bool(r.certified)}
        for cfg in CONFIGS:
            f = fin[(fin["instance_name"] == r.instance_name) & (fin["config"] == cfg)]
            if len(f):
                row[f"{cfg}: value-1"] = f"{f.iloc[0]['status']} ({np.log10(1 + float(f.iloc[0]['nodes'])):.2f} log10 nodes, {float(f.iloc[0]['seconds']):.0f} s)"
            elif bool(r.certified):
                row[f"{cfg}: value-1"] = f"unsat in run ({np.log10(1 + float(getattr(r, f'nodes_{cfg}'))):.2f} log10 nodes, {float(getattr(r, f'seconds_{cfg}')):.0f} s)"
            else:
                row[f"{cfg}: value-1"] = "pending"
        rows.append(row)
    return pd.DataFrame(rows)


def apply_finish(frame: pd.DataFrame, finish_csv: Path = FINISH_CSV) -> pd.DataFrame:
    """Merge the finish stage's answers over the run's rows: status, nodes and
    seconds per configuration; `certified` when either configuration refuted."""
    if frame.empty or not finish_csv.exists() or not finish_csv.stat().st_size:
        return frame
    fin = pd.read_csv(finish_csv)
    out = frame.copy()
    for r in fin.itertuples():
        i = out.index[out["instance_name"] == r.instance_name]
        if not len(i) or int(out.loc[i[0], "optimum"]) != int(r.value):
            continue
        out.loc[i, f"status_{r.config}"] = r.status
        out.loc[i, f"nodes_{r.config}"] = float(r.nodes)
        out.loc[i, f"seconds_{r.config}"] = r.seconds
        if r.status == "unsat":
            out.loc[i, "certified"] = True
            out.loc[i, "solve_proof"] = "refutation (finish stage)"
    return out


# ----------------------------------------------------------------------------
# audit and report
# ----------------------------------------------------------------------------


def audit(upward: pd.DataFrame) -> dict:
    out = {"instances": len(upward), "cells": int(upward["cell"].nunique()),
           "certified": int(upward["certified"].astype(bool).sum()),
           "uncertified (solve budget)": int((~upward["certified"].astype(bool)).sum()),
           "witness_ok": int(upward["witness_ok"].astype(bool).sum()),
           "core_hours": round(float(upward["total_seconds"].sum()) / 3600, 2),
           "classes_within_cells": int(upward.groupby("cell")["graph_cert"].nunique().sum()),
           "complete_graphs": int(upward["complete_graph"].astype(bool).sum()),
           "decomposable": int((upward["g_components"] > 1).sum())}
    for cfg in CONFIGS:
        s = upward[f"status_{cfg}"]
        out[f"unsat_{cfg}"] = int((s == "unsat").sum())
        out[f"trivial_{cfg}"] = int((s == "trivial").sum())
        out[f"sat_{cfg} (stored optimum wrong)"] = int((s == "sat").sum())
        out[f"censored_{cfg}"] = int((s == "unknown").sum())
    return out


def _md(frame: pd.DataFrame, floatfmt: str = ".4g") -> str:
    if frame is None or len(frame) == 0:
        return "*(empty)*\n\n"
    return frame.to_markdown(index=False, floatfmt=floatfmt) + "\n\n"


def report(out: Path = TABLES, campaign_csv: Path = RESULTS_CSV, upward_csv: Path = RESULTS_UPWARD_CSV) -> dict:
    started = time.time()
    frame = load_all(campaign_csv, upward_csv)
    upward = frame[frame["source"] == "upward"]
    text = (f"# The campaign upward: tables (§16)\n\n*Regenerated {time.strftime('%Y-%m-%d %H:%M')} by "
            f"`python -m learning.upward`; {len(frame)} rows ({len(upward)} at n >= 50).*\n\n")
    a = audit(upward)
    text += "### Audit of the upward run\n\n" + _md(pd.DataFrame({"check": list(a), "count": [str(v) for v in a.values()]}))
    results: dict = {"audit": a}
    for cfg in CONFIGS:
        cells = cell_stats(frame, cfg)
        rates = local_rates(frame, cfg)
        dr = drift(rates)
        pooled = pooled_drift(rates)
        fits = global_fits(cells)
        results[cfg] = {"cells": cells, "rates": rates, "drift": dr, "pooled": pooled, "fits": fits}
        text += f"## Configuration `{cfg}`\n\n"
        text += "### Cells at n >= 50 (median of log10(1 + nodes); a flagged median is a lower bound)\n\n"
        text += _md(cells[cells["n"] >= 50])
        text += "### Local rates between consecutive sizes, fixed generator (log10 per customer, 90% bootstrap band)\n\n"
        text += _md(rates)
        text += "### Drift of the local rate with n, per series (exact intervals only)\n\n" + _md(dr)
        text += (f"Pooled within-series slope: {pooled['slope']:.6f} ± {pooled['se']:.6f} log10 per customer per "
                 f"customer (t = {pooled.get('t', float('nan')):.2f}) over {pooled['intervals']} intervals in "
                 f"{pooled['series']} series.\n\n")
        text += "### Global fits by window (exponential against power law), fixed generator\n\n" + _md(fits)
        text += "### Ridge location per size and ratio\n\n" + _md(ridge_location(cells))
        ext = extrapolate(cells, rates, pooled, cfg)
        results[cfg]["extrapolate"] = ext
        text += "### Extrapolation from the 75-customer cells (m = n): constant last rate, and drifting at the pooled slope\n\n" + _md(ext)
        if cfg == "default":
            pred = predict_125(frame, rates, cells, cfg)
            results["predict_125"] = pred
            text += "### The 125 x 125 prediction from the 100-customer cells (m = n)\n\n" + _md(pred)
    text += "### The n = 100, d in {3, 4} sample, instance by instance\n\n" + _md(hard100_table(upward_csv, upward_csv.with_name("results_upward_finish.csv")))
    text += "### Theorem 2: csearch / default nodes per ratio and size\n\n" + _md(theorem2(frame))
    rec = recertify_counts()
    results["recertify"] = rec
    text += "### The 125 x 125 counts on record (recertify, better_move on)\n\n" + _md(rec)
    try:
        cc = corpus_classes()
        results["corpus"] = cc
        text += "### Chu & Stuckey classes, m = n, default configuration (from learning.scale_test)\n\n" + _md(cc)
    except Exception as exc:  # the corpus tables are context, not the finding
        text += f"*(corpus classes unavailable: {exc})*\n\n"
    text += f"*{time.time() - started:.0f} s.*\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    results["text"] = text
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=TABLES)
    ap.add_argument("--campaign-csv", type=Path, default=RESULTS_CSV)
    ap.add_argument("--upward-csv", type=Path, default=RESULTS_UPWARD_CSV)
    ap.add_argument("--finish-uncertified", action="store_true",
                    help="refute the uncertified n >= 100 values with --deadline seconds per call, then the tables")
    ap.add_argument("--deadline", type=float, default=1800.0)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    if args.finish_uncertified:
        finish_uncertified(args.upward_csv, args.deadline, args.workers)
        return
    res = report(args.out, args.campaign_csv, args.upward_csv)
    print(res["text"])
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
