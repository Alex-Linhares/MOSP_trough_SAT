"""Is there a phase transition in MOSP hardness? (`reports/ml_nature_plan.md` §2.4)

The question. Random SAT has its ratio 4.26; does the cost of *refuting*
`optimum - 1` -- nodes visited by the complete customer search, never seconds
-- peak at a density, where is the peak, does it sharpen with `n`, how do nodes
scale with `n` at the peak and away from it, and is there an order parameter
(a quantity at which the peak sits for every size, generator and `m / n`)?
Then: where do Chu & Stuckey's `Random-n-m-d` classes sit on that map?

The data is the campaign of `learning.ensemble` (`reports/ml_nature.md` §9,
§10): 252 cells `(generator, n, m, param)`, 150 instances each, `n` from 10 to
40, `m` in `{n, 2n}`, the fixed customers-per-product generator at
`d = 2..10` and the Bernoulli generator at `p = 0.025..0.5`, each row with
`nodes_default` and `nodes_csearch` (a fresh `decide(optimum - 1)` under the
two `learning.node_counts` configurations), the 49 features and the
isomorphism certificates. Density on every axis here is `col_mean`, the
realised mean number of customers per product, not the nominal `d` or `p`
(§9: the empty-row repair inflates `d = 2`, and Chu & Stuckey's "density 2"
classes have `col_mean` 2.7).

What the module computes (`python -m learning.hardness_map`):

- `cell_table`: per cell, median / p90 / p99 / max nodes, the share of
  zero-node refutations, the connected share, and the cell's median of every
  candidate order parameter; raw, per isomorphism class (`--per-class`), and
  on connected instances only (`--connected`), under either configuration.
- `peaks`: per `(generator, m / n, n)` the cell where the median peaks, whether
  it is interior to the grid, and a bootstrap confidence interval for the
  ratio of the peak median to each neighbour's -- the kill criterion
  ("monotone in density, no peak, at three sizes") is decided on this table.
- `sharpness`: the width of the peak in `log10(col_mean)` at half and at a
  tenth of its height, interpolated between cells, per `n`; and the ratio of
  the peak median to the densest and sparsest cells of the same series.
- `scaling`: `log10(median nodes)` against `n` (exponential, rate per
  customer and doubling distance) and against `log10 n` (power law, exponent
  alpha), with residuals, along the ridge (the peak cell at each `n`) and at
  every fixed parameter away from it.
- `order_parameters`: for each candidate -- `col_mean`, matrix `density`,
  `g_deg_mean`, `optimum / n`, `ub_best - lb_best`, `g_components` -- how
  well nodes at fixed `n` collapse onto one curve across the four series
  (dispersion of per-series binned medians, pooled R^2), and how constant
  the peak's location in that candidate is across the 28 series.
- `locate_corpus`: Chu & Stuckey's `Random-30-30-d` and `Random-40-40-d`
  instances from `learning/data/node_counts.csv`, placed against the
  campaign's fixed `m = n` cells nearest in `col_mean`, all instances and
  connected only (their generator discards decomposable instances); and the
  125 x 125 node counts `recertify/results.json` holds, listed for item 06,
  which owns the extrapolation.
- `figure`: `reports/figures/hardness_map.png`.

Baseline: hardness monotone in density. Kill: node counts at fixed `n`
monotone in density with no peak across three sizes.

Nothing here is a bound, nothing touches `_lower_bound` or any solver
default, and nothing is written to `solutions/`.

Usage:
    python -m learning.hardness_map                      # tables + figure, default config
    python -m learning.hardness_map --config csearch     # the other configuration
    python -m learning.hardness_map --per-class          # one row per isomorphism class per cell
    python -m learning.hardness_map --bootstrap 2000     # more resamples for the CIs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from learning.ensemble import RESULTS_CSV, dedupe, load_results

FIGURE = Path("reports/figures/hardness_map.png")
TABLES = Path("reports/hardness_map_tables.md")
NODE_COUNTS = Path("learning/data/node_counts.csv")
INSTANCES = Path("learning/data/instances.csv")
RECERTIFY = Path("recertify/results.json")

CANDIDATES = {
    "col_mean": "customers per product (realised)",
    "density": "matrix density",
    "g_deg_mean": "mean degree of the MOSP graph",
    "opt_frac": "optimum / n",
    "bound_gap": "ub_best - lb_best",
    "g_components": "components of the MOSP graph",
}
SERIES = [("fixed", 1), ("fixed", 2), ("bernoulli", 1), ("bernoulli", 2)]


# ----------------------------------------------------------------------------
# frame preparation
# ----------------------------------------------------------------------------


def prepare(frame: pd.DataFrame, config: str = "default") -> pd.DataFrame:
    """Add `ratio`, `opt_frac`, `nodes`, `log_nodes`, `connected` columns."""
    out = frame.copy()
    out["ratio"] = (out["m"] / out["n"]).round().astype(int)
    out["opt_frac"] = out["optimum"] / out["n"]
    out["nodes"] = out[f"nodes_{config}"].astype(float)
    out["log_nodes"] = np.log10(1.0 + out["nodes"])
    out["connected"] = out["g_components"] <= 1
    if "bound_gap" not in out:
        out["bound_gap"] = out["ub_best"] - out["lb_best"]
    return out


def load(csv: Path = RESULTS_CSV, config: str = "default", per_class: bool = False,
         connected: bool = False) -> pd.DataFrame:
    frame = load_results(csv)
    if per_class:
        frame = dedupe(frame)
    frame = prepare(frame, config)
    if connected:
        frame = frame[frame["connected"]]
    return frame.reset_index(drop=True)


def series_label(generator: str, ratio: int) -> str:
    return f"{generator}, m = {ratio}n"


# ----------------------------------------------------------------------------
# per-cell statistics
# ----------------------------------------------------------------------------


def cell_table(frame: pd.DataFrame) -> pd.DataFrame:
    """One row per cell: node statistics and the medians of the candidates."""
    rows = []
    for (gen, ratio, n, param), g in frame.groupby(["generator", "ratio", "n", "param"]):
        nodes = g["nodes"].to_numpy()
        row = {
            "generator": gen, "ratio": int(ratio), "n": int(n), "param": float(param),
            "instances": len(g),
            "classes": g["graph_cert"].nunique() if "graph_cert" in g else len(g),
            "connected_share": float(g["connected"].mean()),
            "zero_share": float((nodes == 0).mean()),
            "median": float(np.median(nodes)),
            "p90": float(np.quantile(nodes, 0.9)),
            "p99": float(np.quantile(nodes, 0.99)),
            "max": float(nodes.max()),
            "mean_log": float(g["log_nodes"].mean()),
        }
        for cand in CANDIDATES:
            row[cand] = float(g[cand].median())
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["generator", "ratio", "n", "param"]).reset_index(drop=True)


def _bootstrap_ratio(a: np.ndarray, b: np.ndarray, resamples: int, rng: np.random.Generator,
                     stat=np.median) -> tuple[float, float]:
    """Percentile CI for stat(a) / stat(b), with +1 in both to survive zeros."""
    ia = rng.integers(0, len(a), size=(resamples, len(a)))
    ib = rng.integers(0, len(b), size=(resamples, len(b)))
    ra = stat(a[ia], axis=1) + 1.0
    rb = stat(b[ib], axis=1) + 1.0
    r = ra / rb
    return float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))


def peaks(frame: pd.DataFrame, cells: pd.DataFrame | None = None, resamples: int = 1000,
          seed: int = 0, stat: str = "median") -> pd.DataFrame:
    """Per (generator, ratio, n): where the cell statistic peaks in density.

    `interior` is True when the peak cell has a neighbour on each side in the
    grid. `ratio_left` / `ratio_right` are (peak + 1) / (neighbour + 1) of the
    statistic with 95% bootstrap intervals; a peak is *significant* on a side
    when the interval's lower end exceeds 1.
    """
    cells = cell_table(frame) if cells is None else cells
    rng = np.random.default_rng(seed)
    q = {"median": np.median, "p90": lambda x, axis=None: np.quantile(x, 0.9, axis=axis)}[stat]
    rows = []
    for (gen, ratio, n), g in cells.groupby(["generator", "ratio", "n"]):
        g = g.sort_values("param").reset_index(drop=True)
        values = g[stat].to_numpy()
        i = int(np.argmax(values))
        # ties: the sparsest of the tied cells is reported and flagged
        tied = int((values == values[i]).sum())
        row = {"generator": gen, "ratio": int(ratio), "n": int(n), "peak_param": float(g.loc[i, "param"]),
               "peak_col_mean": float(g.loc[i, "col_mean"]), "peak_" + stat: float(values[i]),
               "tied": tied, "interior": bool(0 < i < len(g) - 1)}
        sub = frame[(frame["generator"] == gen) & (frame["ratio"] == ratio) & (frame["n"] == n)]
        peak_nodes = sub[sub["param"] == g.loc[i, "param"]]["nodes"].to_numpy()
        for side, j in (("left", i - 1), ("right", i + 1)):
            if 0 <= j < len(g):
                nb = sub[sub["param"] == g.loc[j, "param"]]["nodes"].to_numpy()
                lo, hi = _bootstrap_ratio(peak_nodes, nb, resamples, rng, q)
                row[f"ratio_{side}"] = (values[i] + 1) / (values[j] + 1)
                row[f"ci_{side}"] = f"[{lo:.2f}, {hi:.2f}]"
                row[f"significant_{side}"] = bool(lo > 1.0)
            else:
                row[f"ratio_{side}"] = np.nan
                row[f"ci_{side}"] = "edge"
                row[f"significant_{side}"] = False
        rows.append(row)
    return pd.DataFrame(rows)


def monotone(cells: pd.DataFrame, stat: str = "median") -> pd.DataFrame:
    """Per (generator, ratio, n): is the cell statistic monotone along density?

    Non-increasing or non-decreasing across the grid, ties allowed. This is
    the literal premise of the plan's kill criterion.
    """
    rows = []
    for (gen, ratio, n), g in cells.groupby(["generator", "ratio", "n"]):
        v = g.sort_values("col_mean")[stat].to_numpy()
        d = np.diff(v)
        rows.append({"generator": gen, "ratio": int(ratio), "n": int(n),
                     "monotone": bool(np.all(d <= 0) or np.all(d >= 0)),
                     "rises_then_falls": bool(np.any(d > 0) and np.any(d < 0)
                                              and int(np.argmax(v)) not in (0, len(v) - 1))})
    return pd.DataFrame(rows)


def kill_verdict(peak_table: pd.DataFrame, cells: pd.DataFrame, stat: str = "median") -> dict:
    """The plan's kill: node counts at fixed n monotone in density with no
    peak across three sizes.

    Per series `(generator, ratio)`: the sizes at which the cell statistic is
    monotone along density; the sizes with an interior peak resolved from
    both neighbours by the bootstrap; and the sizes with an interior peak
    resolved from at least one neighbour on each side within two cells. The
    kill fires for a series when the statistic is monotone at three or more
    sizes. The overall verdict fires only if it fires for every series.
    """
    mono = monotone(cells, stat)
    out = {}
    for (gen, ratio), g in peak_table.groupby(["generator", "ratio"]):
        m = mono[(mono["generator"] == gen) & (mono["ratio"] == ratio)].set_index("n")
        strict = g["interior"] & g["significant_left"] & g["significant_right"]
        out[series_label(gen, ratio)] = {
            "sizes": int(len(g)),
            "monotone_at": [int(n) for n in m.index[m["monotone"]]],
            "interior_peak_at": [int(n) for n in g.loc[g["interior"], "n"]],
            "interior_peak_resolved_both_sides_at": [int(n) for n in g.loc[strict, "n"]],
            "kill_fires": bool(m["monotone"].sum() >= 3),
        }
    out["overall"] = {"kill_fires": all(v["kill_fires"] for v in out.values())}
    return out


def peak_by_candidate(frame: pd.DataFrame, candidate: str, bins: int = 12, min_n: int = 20,
                      min_per_bin: int = 40) -> pd.DataFrame:
    """Grid-free peak location: at each n, pool every instance of every series,
    bin by quantiles of the candidate, and report the median candidate value
    in the bin whose median log10(1 + nodes) is largest, with the bins on
    either side. Interior is False when the peak bin is the first or last."""
    rows = []
    for n, g in frame.groupby("n"):
        if n < min_n:
            continue
        x = g[candidate].to_numpy(dtype=float)
        g = g.assign(_bin=_quantile_bins(x, bins))
        agg = g.groupby("_bin").agg(value=(candidate, "median"), nodes=("log_nodes", "median"),
                                    count=("log_nodes", "size")).reset_index()
        agg = agg[agg["count"] >= min_per_bin].reset_index(drop=True)
        if len(agg) < 3:
            continue
        i = int(agg["nodes"].idxmax())
        rows.append({"candidate": candidate, "n": int(n), "bins": len(agg),
                     "peak_value": float(agg.loc[i, "value"]),
                     "peak_median_nodes": float(10 ** agg.loc[i, "nodes"] - 1),
                     "interior": bool(0 < i < len(agg) - 1),
                     "left_value": float(agg.loc[i - 1, "value"]) if i > 0 else np.nan,
                     "right_value": float(agg.loc[i + 1, "value"]) if i < len(agg) - 1 else np.nan})
    return pd.DataFrame(rows)


def peak_constancy(frame: pd.DataFrame, min_n: int = 20) -> pd.DataFrame:
    """For each candidate: the grid-free peak location per n and its spread."""
    rows = []
    for cand in CANDIDATES:
        t = peak_by_candidate(frame, cand, min_n=min_n)
        if t.empty:
            continue
        v = t["peak_value"].to_numpy()
        rows.append({"candidate": cand, "sizes": len(t),
                     "peak_values_by_n": ", ".join(f"{n}: {x:.3g}" for n, x in zip(t["n"], v)),
                     "interior_at_every_n": bool(t["interior"].all()),
                     "mean": float(v.mean()), "cv": float(v.std(ddof=1) / v.mean()) if v.mean() else np.nan})
    return pd.DataFrame(rows).sort_values("cv").reset_index(drop=True)


# ----------------------------------------------------------------------------
# sharpening
# ----------------------------------------------------------------------------


def _width_at(x: np.ndarray, y: np.ndarray, level: float) -> tuple[float, str]:
    """Width in x over which y >= level around argmax, interpolating linearly.

    Returns (width, note); note is "" when both crossings are inside the
    grid, otherwise which side runs off it and the width is a lower bound.
    """
    i = int(np.argmax(y))
    note = []
    # left crossing
    left = x[0]
    j = i
    while j > 0 and y[j - 1] >= level:
        j -= 1
    if j == 0 and y[0] >= level:
        note.append("left open")
    elif j > 0:
        # y[j-1] < level <= y[j]
        t = (level - y[j - 1]) / (y[j] - y[j - 1])
        left = x[j - 1] + t * (x[j] - x[j - 1])
    right = x[-1]
    j = i
    while j < len(y) - 1 and y[j + 1] >= level:
        j += 1
    if j == len(y) - 1 and y[-1] >= level:
        note.append("right open")
    elif j < len(y) - 1:
        t = (level - y[j + 1]) / (y[j] - y[j + 1])
        right = x[j + 1] - t * (x[j + 1] - x[j])
    return float(right - left), "; ".join(note)


def sharpness(cells: pd.DataFrame, stat: str = "median") -> pd.DataFrame:
    """Per (generator, ratio, n): peak width in log10(col_mean) and peak-to-edge ratios."""
    rows = []
    for (gen, ratio, n), g in cells.groupby(["generator", "ratio", "n"]):
        g = g.sort_values("col_mean")
        x = np.log10(g["col_mean"].to_numpy())
        y = np.log10(1.0 + g[stat].to_numpy())
        peak = float(y.max())
        w_half, note_half = _width_at(x, y, peak - np.log10(2))
        w_tenth, note_tenth = _width_at(x, y, peak - 1.0)
        rows.append({
            "generator": gen, "ratio": int(ratio), "n": int(n),
            "peak_" + stat: float(10 ** peak - 1),
            "width_half_log10": w_half, "width_half_factor": 10 ** w_half, "half_note": note_half,
            "width_tenth_log10": w_tenth, "width_tenth_factor": 10 ** w_tenth, "tenth_note": note_tenth,
            "peak_over_sparsest": (10 ** peak) / (1.0 + g[stat].iloc[0]),
            "peak_over_densest": (10 ** peak) / (1.0 + g[stat].iloc[-1]),
        })
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# scaling with n
# ----------------------------------------------------------------------------


def fit_scaling(n: np.ndarray, value: np.ndarray, min_value: float = 2.0) -> dict:
    """Fit log10(value) against n (exponential) and against log10 n (power law).

    Points with value < min_value are dropped (log of a handful of nodes is
    dominated by the +1 and by discreteness). Returns the rate per customer,
    the doubling distance in customers, the power exponent, and the RMS
    residual in log10 units of each fit; `better` names the smaller residual.
    """
    n = np.asarray(n, dtype=float)
    value = np.asarray(value, dtype=float)
    keep = value >= min_value
    n, value = n[keep], value[keep]
    out = {"points": int(len(n))}
    if len(n) < 3:
        out.update(rate=np.nan, doubling_n=np.nan, rms_exp=np.nan, alpha=np.nan, rms_pow=np.nan, better="")
        return out
    y = np.log10(value)
    b, a = np.polyfit(n, y, 1)
    rms_exp = float(np.sqrt(np.mean((a + b * n - y) ** 2)))
    alpha, c = np.polyfit(np.log10(n), y, 1)
    rms_pow = float(np.sqrt(np.mean((c + alpha * np.log10(n) - y) ** 2)))
    out.update(rate=float(b), doubling_n=float(np.log10(2) / b) if b > 0 else np.inf,
               rms_exp=rms_exp, alpha=float(alpha), rms_pow=rms_pow,
               better="exponential" if rms_exp < rms_pow else "power")
    return out


def scaling(cells: pd.DataFrame, peak_table: pd.DataFrame, stat: str = "median",
            min_n: int = 15) -> pd.DataFrame:
    """Scaling of the cell statistic with n: along the ridge and at each fixed parameter.

    The ridge takes, at each n, the peak cell of the series (from
    `peak_table`), so for the Bernoulli generator it follows the peak as it
    moves to lower p. Fixed-parameter rows use n >= `min_n`, where the fixed
    generator's small-n cells stop being complete graphs.
    """
    rows = []
    for (gen, ratio), g in cells.groupby(["generator", "ratio"]):
        pk = peak_table[(peak_table["generator"] == gen) & (peak_table["ratio"] == ratio)]
        ridge = pk.merge(g, left_on=["generator", "ratio", "n", "peak_param"],
                         right_on=["generator", "ratio", "n", "param"])
        ridge = ridge[ridge["n"] >= min_n].sort_values("n")
        fit = fit_scaling(ridge["n"], ridge[stat])
        rows.append({"generator": gen, "ratio": int(ratio), "where": "ridge (peak cell at each n)",
                     "param": np.nan, **fit})
        for param, h in g.groupby("param"):
            h = h[h["n"] >= min_n].sort_values("n")
            fit = fit_scaling(h["n"], h[stat])
            rows.append({"generator": gen, "ratio": int(ratio), "where": "fixed parameter",
                         "param": float(param), **fit})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# order parameters
# ----------------------------------------------------------------------------


def _quantile_bins(x: np.ndarray, bins: int) -> np.ndarray:
    """Quantile bin labels; a constant or near-constant candidate falls into one bin."""
    try:
        b = pd.qcut(x, bins, labels=False, duplicates="drop")
    except (ValueError, IndexError):
        return np.zeros(len(x), dtype=int)
    return pd.Series(b).fillna(0).astype(int).to_numpy()


def collapse(frame: pd.DataFrame, candidate: str, bins: int = 10, min_per_bin: int = 15) -> pd.DataFrame:
    """At each n: do the four series collapse onto one curve of nodes against `candidate`?

    Instances at one n are binned by quantiles of the candidate; in each bin
    the median log10(1 + nodes) of every series with at least `min_per_bin`
    instances is taken. `dispersion` is the mean over bins of the range
    (max - min) of those per-series medians, weighted by bin size; `r2` is
    the share of the variance of log10(1 + nodes) explained by the pooled
    per-bin median. A perfect order parameter has dispersion 0 and r2 equal
    to the r2 of the cell medians themselves.
    """
    rows = []
    for n, g in frame.groupby("n"):
        x = g[candidate].to_numpy(dtype=float)
        b = _quantile_bins(x, bins)
        g = g.assign(_bin=b)
        pooled = g.groupby("_bin")["log_nodes"].transform("median")
        r2 = 1.0 - float(np.var(g["log_nodes"] - pooled) / max(np.var(g["log_nodes"]), 1e-12))
        disp_num = 0.0
        disp_den = 0
        for _, h in g.groupby("_bin"):
            per_series = [s["log_nodes"].median() for _, s in h.groupby(["generator", "ratio"])
                          if len(s) >= min_per_bin]
            if len(per_series) >= 2:
                disp_num += (max(per_series) - min(per_series)) * len(h)
                disp_den += len(h)
        rows.append({"candidate": candidate, "n": int(n), "bins": int(g["_bin"].nunique()),
                     "dispersion": disp_num / disp_den if disp_den else np.nan, "r2": r2})
    return pd.DataFrame(rows)


def cell_r2(frame: pd.DataFrame) -> pd.Series:
    """Variance of log nodes explained by the cell median itself, per n (the ceiling)."""
    out = {}
    for n, g in frame.groupby("n"):
        med = g.groupby(["generator", "ratio", "param"])["log_nodes"].transform("median")
        out[int(n)] = 1.0 - float(np.var(g["log_nodes"] - med) / max(np.var(g["log_nodes"]), 1e-12))
    return pd.Series(out, name="cell_r2")


def order_parameters(frame: pd.DataFrame, peak_table: pd.DataFrame, cells: pd.DataFrame,
                     min_n: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Two tests per candidate: collapse at fixed n, and constancy of the peak's location.

    Returns (summary, peak_locations). `summary` averages the collapse
    statistics over n >= `min_n` and gives the coefficient of variation of the
    candidate's value at the peak cell across every (generator, ratio, n >=
    min_n) with an interior peak; `peak_locations` is the underlying table.
    """
    ceiling = cell_r2(frame)
    loc = peak_table.merge(cells, left_on=["generator", "ratio", "n", "peak_param"],
                           right_on=["generator", "ratio", "n", "param"], suffixes=("", "_cell"))
    loc = loc[loc["n"] >= min_n]
    rows = []
    for cand in CANDIDATES:
        c = collapse(frame, cand)
        c = c[c["n"] >= min_n]
        vals = loc[cand].to_numpy(dtype=float)
        interior = loc["interior"].to_numpy()
        v = vals[interior]
        rows.append({
            "candidate": cand, "meaning": CANDIDATES[cand],
            "dispersion_mean": float(c["dispersion"].mean()),
            "r2_mean": float(c["r2"].mean()),
            "r2_ceiling_mean": float(ceiling[ceiling.index >= min_n].mean()),
            "peak_value_mean": float(v.mean()) if len(v) else np.nan,
            "peak_value_cv": float(v.std(ddof=1) / v.mean()) if len(v) > 1 and v.mean() else np.nan,
            "peak_value_min": float(v.min()) if len(v) else np.nan,
            "peak_value_max": float(v.max()) if len(v) else np.nan,
            "series_with_interior_peak": int(interior.sum()),
        })
    summary = pd.DataFrame(rows).sort_values("dispersion_mean").reset_index(drop=True)
    keep = ["generator", "ratio", "n", "peak_param", "interior"] + list(CANDIDATES)
    return summary, loc[keep].reset_index(drop=True)


# ----------------------------------------------------------------------------
# Chu & Stuckey's classes on the map
# ----------------------------------------------------------------------------


def corpus_random(node_counts: Path = NODE_COUNTS, instances: Path = INSTANCES,
                  config: str = "default") -> pd.DataFrame:
    """Chu & Stuckey `Random-n-m-d` rows at n <= 40 with their features and node counts."""
    nc = pd.read_csv(node_counts)
    nc = nc[(nc["config"] == config) & nc["instance_name"].str.startswith("Random-")]
    feats = pd.read_csv(instances)
    cols = ["instance_name", "optimum", "n_customers", "n_patterns"] + list(CANDIDATES.keys() - {"opt_frac"})
    cols = [c for c in cols if c in feats.columns]
    out = nc.merge(feats[cols], on="instance_name", suffixes=("", "_f"))
    parts = out["instance_name"].str.split("-", expand=True)
    out["d"] = parts[3].astype(int)
    out["n"] = out["n_customers"].astype(int)
    out["opt_frac"] = out["optimum"] / out["n"]
    out["log_nodes"] = np.log10(1.0 + out["nodes"])
    return out


def locate_corpus(frame: pd.DataFrame, corpus: pd.DataFrame) -> pd.DataFrame:
    """Place each Chu & Stuckey class against the campaign's nearest fixed m = n cell.

    For the class `(n, d)`: its median nodes and median `col_mean`; the
    campaign cell (fixed generator, m = n, same n) whose median `col_mean` is
    nearest; that cell's median nodes over all instances and over connected
    instances only (Chu & Stuckey discard decomposable ones); and the mean
    percentile rank of the class's instances within the connected instances
    of that cell. Also whether the cell is the series' peak at that n.
    """
    cells = cell_table(frame)
    pk = peaks(frame, cells, resamples=200)
    rows = []
    for (n, d), g in corpus.groupby(["n", "d"]):
        fx = cells[(cells["generator"] == "fixed") & (cells["ratio"] == 1) & (cells["n"] == n)]
        if fx.empty:
            continue
        cm = float(g["col_mean"].median())
        j = int((fx["col_mean"] - cm).abs().idxmin())
        cell = fx.loc[j]
        sub = frame[(frame["generator"] == "fixed") & (frame["ratio"] == 1) & (frame["n"] == n)
                    & (frame["param"] == cell["param"])]
        conn = sub[sub["connected"]]["nodes"].to_numpy()
        ranks = [float((conn < v).mean()) for v in g["nodes"]] if len(conn) else [np.nan]
        peak_param = pk[(pk["generator"] == "fixed") & (pk["ratio"] == 1) & (pk["n"] == n)]["peak_param"]
        rows.append({
            "class": f"Random-{n}-{n}-{d}", "instances": len(g),
            "corpus_median_nodes": float(g["nodes"].median()), "corpus_max_nodes": float(g["nodes"].max()),
            "corpus_col_mean": cm, "corpus_opt_frac": float(g["opt_frac"].median()),
            "nearest_cell_d": float(cell["param"]), "cell_col_mean": float(cell["col_mean"]),
            "cell_median_all": float(cell["median"]),
            "cell_median_connected": float(np.median(conn)) if len(conn) else np.nan,
            "cell_connected_share": float(cell["connected_share"]),
            "mean_percentile_in_connected_cell": float(np.mean(ranks)),
            "cell_is_peak": bool(len(peak_param) and float(peak_param.iloc[0]) == float(cell["param"])),
        })
    return pd.DataFrame(rows)


def large_counts(recertify: Path = RECERTIFY, instances: Path = INSTANCES) -> pd.DataFrame:
    """The 125 x 125 refutation counts on record (item 06's data, listed only)."""
    if not recertify.exists():
        return pd.DataFrame()
    rec = pd.DataFrame(json.load(open(recertify)))
    feats = pd.read_csv(instances)[["instance_name", "optimum", "col_mean", "g_deg_mean", "lb_best", "ub_best"]]
    out = rec.merge(feats, left_on="name", right_on="instance_name", how="left")
    out["d"] = out["name"].str.split("-").str[3].astype(int)
    out["hours"] = out["seconds"] / 3600
    return out[["name", "d", "col_mean", "optimum", "value", "status", "nodes", "hours", "lb_best", "ub_best"]]


# ----------------------------------------------------------------------------
# the figure
# ----------------------------------------------------------------------------


def figure(frame: pd.DataFrame, corpus: pd.DataFrame | None, path: Path = FIGURE,
           stat: str = "median") -> Path:
    """The hardness map: heatmaps of log10 median nodes per series, and the
    connected-only ridge curves with Chu & Stuckey's classes on them."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize

    cells_all = cell_table(frame)
    conn = frame[frame["connected"]]
    cells_conn = cell_table(conn)
    ns = sorted(frame["n"].unique())
    vmax = float(np.log10(1 + cells_all[stat].max()))
    norm = Normalize(0, vmax)
    text, muted, accent = "#0b0b0b", "#52514e", "#eb6834"
    fig, axes = plt.subplots(2, 4, figsize=(17, 8.2), gridspec_kw={"height_ratios": [1, 1.15]})
    fig.patch.set_facecolor("#fcfcfb")
    cmap = plt.get_cmap("Blues")
    xmin = float(cells_all["col_mean"].min()) / 1.15
    xmax = float(cells_all["col_mean"].max()) * 1.15
    for ax, (gen, ratio) in zip(axes[0], SERIES):
        g = cells_all[(cells_all["generator"] == gen) & (cells_all["ratio"] == ratio)]
        # one pcolormesh strip per n, cells bounded at the geometric midpoints
        # of adjacent cell col_means, so every panel shares one col_mean axis
        for n in ns:
            row = g[g["n"] == n].sort_values("col_mean")
            if row.empty:
                continue
            x = np.log10(row["col_mean"].to_numpy(dtype=float))
            edges = np.empty(len(x) + 1)
            edges[1:-1] = (x[:-1] + x[1:]) / 2
            edges[0] = x[0] - (edges[1] - x[0]) if len(x) > 1 else x[0] - 0.05
            edges[-1] = x[-1] + (x[-1] - edges[-2]) if len(x) > 1 else x[-1] + 0.05
            X = np.vstack([10 ** edges, 10 ** edges])
            Y = np.vstack([np.full_like(edges, n - 2.5), np.full_like(edges, n + 2.5)])
            C = np.log10(1 + row[stat].to_numpy(dtype=float))[None, :]
            im = ax.pcolormesh(X, Y, C, cmap=cmap, norm=norm, edgecolors="#fcfcfb", linewidth=0.6)
            j = int(np.argmax(C[0]))
            ax.plot(10 ** x[j], n, marker="s", ms=8, mfc="none", mec=accent, mew=1.6)
        ax.set_xscale("log")
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(min(ns) - 2.5, max(ns) + 2.5)
        ax.set_xticks([1, 2, 3, 4, 6, 10, 20])
        ax.set_xticklabels(["1", "2", "3", "4", "6", "10", "20"], fontsize=8, color=muted)
        ax.set_yticks(ns)
        ax.set_yticklabels(ns, fontsize=8, color=muted)
        ax.set_xlabel("customers per product (cell median col_mean)", fontsize=8, color=muted)
        if ax is axes[0][0]:
            ax.set_ylabel("n (customers)", fontsize=9, color=muted)
        ax.set_title(series_label(gen, ratio), fontsize=10, color=text, loc="left")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(length=0)
        ax.minorticks_off()
    cbar = fig.colorbar(im, ax=axes[0].tolist(), fraction=0.012, pad=0.01)
    cbar.set_label(f"log10(1 + {stat} nodes to refute optimum − 1)", fontsize=8, color=muted)
    cbar.ax.tick_params(labelsize=7, colors=muted)
    cbar.outline.set_visible(False)

    # bottom row: connected instances only, curves by n, both generators per ratio
    ramp = plt.get_cmap("Blues")
    shades = [ramp(0.35 + 0.6 * k / max(len(ns) - 1, 1)) for k in range(len(ns))]
    for k, ratio in enumerate((1, 2)):
        ax = axes[1][k]
        for i, n in enumerate(ns):
            for gen, ls in (("fixed", "-"), ("bernoulli", "--")):
                g = cells_conn[(cells_conn["generator"] == gen) & (cells_conn["ratio"] == ratio)
                               & (cells_conn["n"] == n) & (cells_conn["instances"] >= 15)].sort_values("col_mean")
                if g.empty:
                    continue
                ax.plot(g["col_mean"], 1 + g[stat], ls, color=shades[i], lw=1.8,
                        label=f"n = {n}" if gen == "fixed" else None)
        if corpus is not None and ratio == 1:
            ax.scatter(corpus["col_mean"], 1 + corpus["nodes"], s=22, color=accent, zorder=5,
                       label="Chu & Stuckey Random-n-n-d (corpus)", edgecolor="#fcfcfb", linewidth=0.6)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("customers per product (col_mean)", fontsize=9, color=muted)
        if k == 0:
            ax.set_ylabel(f"1 + {stat} nodes, connected instances only", fontsize=9, color=muted)
        ax.set_title(f"m = {ratio}n · solid: fixed d · dashed: Bernoulli p", fontsize=10, color=text, loc="left")
        ax.grid(True, which="major", color="#e6e5e0", lw=0.6)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.tick_params(colors=muted, labelsize=8)
        ax.set_xticks([1, 2, 3, 4, 6, 10, 20])
        ax.set_xticklabels(["1", "2", "3", "4", "6", "10", "20"])
        if k == 0:
            ax.legend(fontsize=7, frameon=False, ncol=1, loc="lower left")

    # bottom-right pair: ridge scaling and the order parameter
    ax = axes[1][2]
    pk = peaks(frame, cells_all, resamples=200)
    for (gen, ratio), ls, mk in zip(SERIES, ("-", "-", "--", "--"), ("o", "s", "o", "s")):
        p = pk[(pk["generator"] == gen) & (pk["ratio"] == ratio)].sort_values("n")
        ax.plot(p["n"], 1 + p["peak_" + stat], ls, marker=mk, ms=5, lw=1.6,
                color="#2a78d6" if gen == "fixed" else "#1baf7a", label=series_label(gen, ratio))
    ax.set_yscale("log")
    ax.set_xlabel("n (customers)", fontsize=9, color=muted)
    ax.set_ylabel(f"1 + peak {stat} nodes (ridge)", fontsize=9, color=muted)
    ax.set_title("Height of the peak against n", fontsize=10, color=text, loc="left")
    ax.grid(True, color="#e6e5e0", lw=0.6)
    ax.legend(fontsize=7, frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=muted, labelsize=8)

    ax = axes[1][3]
    for (gen, ratio), ls, mk in zip(SERIES, ("-", "-", "--", "--"), ("o", "s", "o", "s")):
        p = pk[(pk["generator"] == gen) & (pk["ratio"] == ratio)].sort_values("n")
        ax.plot(p["n"], p["peak_col_mean"], ls, marker=mk, ms=5, lw=1.6,
                color="#2a78d6" if gen == "fixed" else "#1baf7a", label=series_label(gen, ratio))
    ax.set_xlabel("n (customers)", fontsize=9, color=muted)
    ax.set_ylabel("col_mean at the peak cell", fontsize=9, color=muted)
    ax.set_title("Where the peak sits", fontsize=10, color=text, loc="left")
    ax.grid(True, color="#e6e5e0", lw=0.6)
    ax.set_ylim(0, None)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=muted, labelsize=8)

    fig.suptitle("MOSP hardness map: nodes to refute optimum − 1 over (n, customers per product); "
                 "orange squares mark each row's peak; 150 instances per cell",
                 fontsize=11, color=text, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


# ----------------------------------------------------------------------------
# report
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt) + "\n\n"


def nodes_matrix(cells: pd.DataFrame, generator: str, ratio: int, stat: str = "median") -> pd.DataFrame:
    """Rows = density parameter (with the cell's col_mean), columns = n."""
    g = cells[(cells["generator"] == generator) & (cells["ratio"] == ratio)]
    piv = g.pivot(index="param", columns="n", values=stat)
    cm = g.groupby("param")["col_mean"].median()
    piv.insert(0, "col_mean", cm.round(2))
    piv.index.name = "p" if generator == "bernoulli" else "d"
    return piv.reset_index()


def report(frame: pd.DataFrame, config: str, per_class: bool, resamples: int,
           corpus: pd.DataFrame | None) -> tuple[str, dict]:
    cells = cell_table(frame)
    pk_med = peaks(frame, cells, resamples=resamples, stat="median")
    pk_p90 = peaks(frame, cells, resamples=resamples, stat="p90")
    verdict = kill_verdict(pk_med, cells)
    constancy = peak_constancy(frame)
    sharp = sharpness(cells)
    scal = scaling(cells, pk_med)
    scal90 = scaling(cells, pk_p90, stat="p90")
    summary, locs = order_parameters(frame, pk_med, cells)
    conn = frame[frame["connected"]]
    cells_conn = cell_table(conn)
    pk_conn = peaks(conn, cells_conn, resamples=resamples)

    text = (f"# Hardness map tables (config `{config}`, "
            f"{'one row per isomorphism class per cell' if per_class else 'raw instances'})\n\n"
            f"{len(frame)} rows in {frame.groupby(['generator', 'ratio', 'n', 'param']).ngroups} cells; "
            f"{int(frame['connected'].sum())} connected. Regenerate: "
            f"`python -m learning.hardness_map --config {config}{' --per-class' if per_class else ''}`.\n\n")
    for stat in ("median", "p90"):
        for gen, ratio in SERIES:
            text += f"### {stat} nodes: {series_label(gen, ratio)}\n\n" + _md(nodes_matrix(cells, gen, ratio, stat), ".0f")
    text += "### Peaks of the median, with bootstrap intervals on the ratio to each neighbour\n\n" + _md(pk_med)
    text += "### Peaks of the p90\n\n" + _md(pk_p90)
    text += "### Peaks of the median, connected instances only\n\n" + _md(pk_conn)
    text += "### Kill criterion\n\n```\n" + json.dumps(verdict, indent=1) + "\n```\n\n"
    text += "### Sharpness: width of the peak in log10(col_mean) and peak-to-edge ratios\n\n" + _md(sharp)
    text += "### Scaling of the median with n (n >= 15, cells with median >= 2)\n\n" + _md(scal)
    text += "### Scaling of the p90 with n\n\n" + _md(scal90)
    text += "### Order parameters: collapse at fixed n (n >= 20) and constancy of the peak location\n\n" + _md(summary)
    text += "### Candidate values at the peak cell\n\n" + _md(locs)
    text += ("### Grid-free peak location per candidate (instances pooled over the four series "
             "at each n, 12 quantile bins)\n\n" + _md(constancy))
    text += "### Monotonicity along density per series and n\n\n" + _md(monotone(cells))
    for cand in CANDIDATES:
        text += f"### Collapse by n: {cand}\n\n" + _md(collapse(frame, cand))
    text += "### Median nodes, connected instances only\n\n"
    for gen, ratio in SERIES:
        text += f"**{series_label(gen, ratio)}**\n\n" + _md(nodes_matrix(cells_conn, gen, ratio), ".0f")
    if corpus is not None:
        text += "### Chu & Stuckey's classes against the campaign's nearest fixed m = n cell\n\n"
        text += _md(locate_corpus(frame, corpus))
        text += "### Chu & Stuckey's instances\n\n"
        text += _md(corpus[["instance_name", "n", "d", "optimum", "col_mean", "g_deg_mean",
                            "g_components", "bound_gap", "nodes"]].sort_values(["n", "d", "instance_name"]))
    big = large_counts()
    if not big.empty:
        text += ("### 125 x 125 refutation counts on record (recertify/results.json) -- item 06's data, listed only\n\n"
                 + _md(big))
    return text, verdict


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--csv", type=Path, default=RESULTS_CSV)
    ap.add_argument("--config", choices=("default", "csearch"), default="default")
    ap.add_argument("--per-class", action="store_true")
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--out", type=Path, default=TABLES)
    ap.add_argument("--figure", type=Path, default=FIGURE)
    ap.add_argument("--no-figure", action="store_true")
    args = ap.parse_args()

    frame = load(args.csv, args.config, args.per_class)
    corpus = corpus_random(config=args.config) if NODE_COUNTS.exists() and INSTANCES.exists() else None
    text, verdict = report(frame, args.config, args.per_class, args.bootstrap, corpus)
    out = args.out
    if args.per_class or args.config != "default":
        out = out.with_name(out.stem + f"_{args.config}{'_class' if args.per_class else ''}" + out.suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"wrote {out}")
    print(json.dumps(verdict, indent=1))
    if not args.no_figure:
        print(f"wrote {figure(frame, corpus, args.figure)}")


if __name__ == "__main__":
    main()
