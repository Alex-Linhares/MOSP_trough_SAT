"""The ridge mechanism, one hypothesis and one test (loop0010 item 09).

Section 36 of `reports/ml_nature.md` found that the hardness ridge -- the
density at which the nodes to refute `optimum - 1` peak at fixed `n` -- is
where the number of closed sets *reachable* through fitting steps peaks, and
could not say where that is in terms of the generator. This module tests one
hypothesis against the 25 ensemble series of section 25 at `n in {50, 60, 75}`
(`m / n in {2, 1, 1/2, 1/4, 1/8}`, both generators, 9,497 certified instances):

    H1: the ridge is where the gap between the exact optimum and the
        first-moment floor is largest.

Two readings of "the first-moment floor", both from `learning.first_moment`:
the finite floor at bound < 0.01 from each instance's own pattern sizes
(`floors`, as `finite_bound_cs.py`), giving `(opt - floor) / n` per instance;
and the asymptotic constant `beta*(d, mu)` at the cell's size law (`beta_star`
on the cell's pooled histogram, `mu = m / n`), giving `opt / n - beta*`. Per
cell the mean of each; per series the cell where it peaks, interpolated in
`log10 col_mean` by the parabola through three cells as section 25 (b) does,
with a bootstrap interval over instances; scored as section 25 (d) by
`|log10(predicted / measured)|` against the node-count peak and its bootstrap
interval (`learning.ridge_theory.peak_table`, so the node peaks are section
25's to the digit). H1 is dead if the gap's peak lies outside the node peak's
interval on more than half of the 25 series, or if the mean score exceeds
0.15 decades.

Secondary (not a kill), at `n = 20`: on the 5,400 instances of the campaign's
`m in {n, 2n}` cells (150 per cell, both generators, every one certified), the
number of optimal closing orders under the construction value, exact, by a
vectorised path count over the `2^20` closed-customer sets (the same two
measures as `learning.degeneracy.closing_weights`, checked against it in the
tests), its cell median against the node peak. Section 8 found the share
tracks `opt / n` at `n <= 15`, which predicts monotone, not peaked. The
lattice minimum under both measures is compared with the certified optimum on
every instance -- an audit that shares no code with the search.

Nothing here solves anything, reads `solutions/` or writes outside
`learning/data/excess_ridge_*.csv`, `reports/scratch/excess_ridge/`,
`reports/figures/excess_ridge.png` and stdout. A coincidence of peaks is
evidence for a mechanism, not a mechanism.

Usage (through `learning.excess`):
    python -m learning.excess --stage ridge            # H1: instance and cell frames, peaks, scores, tables
    python -m learning.excess --stage ridge-lattice    # the n = 20 lattice counts (about 2 core-hours on 8 workers)
    python -m learning.excess --stage ridge-tables     # every table, from the CSVs
    python -m learning.excess --stage figure-ridge     # reports/figures/excess_ridge.png
    python -m pytest tests/test_excess_ridge.py -q
"""
from __future__ import annotations

import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from learning.degeneracy import Compact
from learning.ensemble import ENSEMBLE_DIR, RESULTS_CSV, Cell, generate, load_results
from learning.first_moment import beta_star, floors
from learning.ridge_theory import SEED, _cens_median, load_frames, parabola_vertex, peak_table
from mosp.instance import MOSPInstance

DATA_DIR = Path("learning/data")
RULE_CSV = DATA_DIR / "excess_rule.csv"
INSTANCES_CSV = DATA_DIR / "excess_ridge_instances.csv"
CELLS_CSV = DATA_DIR / "excess_ridge_cells.csv"
PEAKS_CSV = DATA_DIR / "excess_ridge_peaks.csv"
LATTICE_CSV = DATA_DIR / "excess_ridge_lattice.csv"
STATES_CSV = ENSEMBLE_DIR / "cover_excess_states.csv"
SCRATCH = Path("reports/scratch/excess_ridge")
FIGURE = Path("reports/figures/excess_ridge.png")

SERIES_N = (50, 60, 75)
SECONDARY_N = 20
RESAMPLES = 500
KILL_MAX_OUTSIDE_FRAC = 0.5
KILL_MEAN_SCORE = 0.15
GAP_COLUMNS = ("gap_floor", "gap_beta")
GAP_TEXT = {"gap_floor": "(opt − floor₀.₀₁) / n, finite floor from the instance's own sizes",
            "gap_beta": "opt / n − β*, the asymptotic constant at the cell's size law"}


# ----------------------------------------------------------------------------
# H1: the instance and cell frames
# ----------------------------------------------------------------------------


def sizes_from_text(text: str) -> dict[int, int]:
    out: dict[int, int] = {}
    for part in str(text).split(";"):
        if part:
            v, c = part.split(":")
            out[int(v)] = out.get(int(v), 0) + int(c)
    return out


def pooled_histogram(texts) -> dict[int, int]:
    hist: dict[int, int] = {}
    for t in texts:
        for s, c in sizes_from_text(t).items():
            hist[s] = hist.get(s, 0) + c
    return hist


def instance_frame(rule_csv: Path = RULE_CSV, sizes=SERIES_N) -> pd.DataFrame:
    """Section 25's frames at `n in sizes` (certified only, through
    `load_frames`) joined with the size histogram item 02 recorded for every
    ensemble instance, with the two finite floors and both gaps per instance
    and `beta*` per cell."""
    frame = load_frames()
    frame = frame[frame["n"].isin(sizes)].copy()
    rule = pd.read_csv(rule_csv, low_memory=False, usecols=["instance_name", "sizes", "n_ones"])
    rule = rule.drop_duplicates("instance_name").set_index("instance_name")
    missing = frame[~frame["instance_name"].isin(rule.index)]
    if len(missing):
        raise KeyError(f"{len(missing)} instances have no size histogram in {rule_csv}; run --stage rule")
    frame["sizes"] = rule.loc[frame["instance_name"], "sizes"].to_numpy()
    recorded = rule.loc[frame["instance_name"], "n_ones"].to_numpy()
    if not np.array_equal(recorded, frame["n_ones"].to_numpy()):
        raise AssertionError("n_ones in the rule table disagrees with the ensemble record")
    fl = [floors(int(n), sizes_from_text(s)) for n, s in zip(frame["n"], frame["sizes"])]
    frame["floor_1"] = [a for a, _ in fl]
    frame["floor_001"] = [b for _, b in fl]
    frame["opt_n"] = frame["optimum"] / frame["n"]
    frame["gap_floor"] = (frame["optimum"] - frame["floor_001"]) / frame["n"]
    frame["gap_floor_1"] = (frame["optimum"] - frame["floor_1"]) / frame["n"]
    keys = ["generator", "ratio_label", "n", "param"]
    beta = {}
    for key, g in frame.groupby(keys):
        mu = float(g["m"].iloc[0]) / float(g["n"].iloc[0])
        beta[key] = beta_star(mu, pooled_histogram(g["sizes"]))
    frame["beta_star"] = [beta[k] for k in zip(frame["generator"], frame["ratio_label"], frame["n"], frame["param"])]
    frame["gap_beta"] = frame["opt_n"] - frame["beta_star"]
    frame["e"] = (frame["n_ones"] - frame["m"]) / frame["n"]
    cols = ["instance_name", "generator", "ratio_label", "n", "m", "param", "r_exact", "col_mean", "e", "n_ones",
            "optimum", "opt_n", "ln_default", "cens_default", "floor_1", "floor_001", "beta_star",
            "gap_floor", "gap_floor_1", "gap_beta", "sizes"]
    return frame[cols].sort_values(["generator", "ratio_label", "n", "param"]).reset_index(drop=True)


def cell_frame(inst: pd.DataFrame) -> pd.DataFrame:
    """One row per (generator, ratio, n, param): the censoring-aware median of
    log10(1 + nodes) and the mean of each gap with its standard error."""
    rows = []
    for (gen, lab, n, param), g in inst.groupby(["generator", "ratio_label", "n", "param"]):
        med, is_lb = _cens_median(g["ln_default"].to_numpy(float), g["cens_default"].to_numpy(bool))
        row = {"generator": gen, "ratio_label": lab, "n": int(n), "param": float(param),
               "m": int(g["m"].iloc[0]), "r_exact": float(g["r_exact"].iloc[0]), "instances": len(g),
               "col_mean": float(g["col_mean"].median()), "e": float(g["e"].median()),
               "median_log_nodes": med, "median_is_lower_bound": is_lb, "censored": int(g["cens_default"].sum()),
               "opt_n": float(g["opt_n"].mean()), "floor_001_n": float((g["floor_001"] / g["n"]).mean()),
               "beta_star": float(g["beta_star"].iloc[0])}
        for c in ("gap_floor", "gap_floor_1", "gap_beta"):
            v = g[c].to_numpy(float)
            row[c] = float(v.mean())
            row[c + "_se"] = float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["generator", "ratio_label", "n", "col_mean"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# H1: the peaks and the score
# ----------------------------------------------------------------------------


def peak_of(cells: pd.DataFrame, inst: pd.DataFrame, column: str, resamples: int = RESAMPLES,
            rng: np.random.Generator | None = None) -> dict:
    """The peak of a cell-mean quantity along one series: the cell with the
    largest mean, the parabolic vertex in log10(col_mean) through it and its
    neighbours when interior, and a bootstrap interval over instances within
    those cells (the cell means recomputed on each resample). Section 25 (b)'s
    construction with the mean in place of the censored median."""
    cells = cells.sort_values("col_mean").reset_index(drop=True)
    i = int(cells[column].idxmax())
    top = cells.loc[i]
    out = {f"{column}_peak_param": float(top["param"]), f"{column}_peak_cell_col_mean": float(top["col_mean"]),
           f"{column}_peak_value": float(top[column]), f"{column}_interior": bool(0 < i < len(cells) - 1),
           f"{column}_peak_col_mean": float(top["col_mean"]), f"{column}_ci_lo": np.nan, f"{column}_ci_hi": np.nan}
    if not out[f"{column}_interior"]:
        return out
    tri = cells.loc[i - 1:i + 1]
    x = np.log10(tri["col_mean"].to_numpy(float))
    out[f"{column}_peak_col_mean"] = 10 ** parabola_vertex(x, tri[column].to_numpy(float))
    if resamples > 0:
        rng = rng or np.random.default_rng(SEED)
        samples = [inst[inst["param"] == p][column].to_numpy(float) for p in tri["param"]]
        if all(len(s) for s in samples):
            verts = np.empty(resamples)
            for b in range(resamples):
                y = [np.mean(rng.choice(s, size=len(s), replace=True)) for s in samples]
                verts[b] = parabola_vertex(x, np.array(y))
            out[f"{column}_ci_lo"] = 10 ** float(np.quantile(verts, 0.025))
            out[f"{column}_ci_hi"] = 10 ** float(np.quantile(verts, 0.975))
    return out


def peaks_table(inst: pd.DataFrame, cells: pd.DataFrame | None = None, resamples: int = RESAMPLES,
                min_n: int = 50) -> pd.DataFrame:
    """One row per series (generator, ratio, n): the node peak with its
    interval (section 25's `peak_table`), the two gap peaks, the log10 errors
    and whether each gap peak lies inside the node peak's interval (an edge
    node peak has none and is scored on the cell, within 0.05 decades, as
    section 36 does)."""
    cells = cell_frame(inst) if cells is None else cells
    nodes = peak_table(load_frames()[lambda f: f["n"].isin(sorted(set(inst["n"])))], None, "default",
                       min_n=min_n, resamples=resamples)
    nodes = nodes[["generator", "ratio_label", "n", "r_exact", "cells", "peak_param", "peak_col_mean",
                   "peak_median_log_nodes", "peak_is_lower_bound", "interior", "ci_lo", "ci_hi", "excess"]]
    rng = np.random.default_rng(SEED)
    rows = []
    for _, p in nodes.iterrows():
        gen, lab, n = p["generator"], p["ratio_label"], int(p["n"])
        g = cells[(cells["generator"] == gen) & (cells["ratio_label"] == lab) & (cells["n"] == n)]
        sub = inst[(inst["generator"] == gen) & (inst["ratio_label"] == lab) & (inst["n"] == n)]
        row = {"generator": gen, "ratio_label": lab, "n": n, "r_exact": float(p["r_exact"]), "cells": int(p["cells"]),
               "nodes_peak_param": float(p["peak_param"]), "nodes_peak_col_mean": float(p["peak_col_mean"]),
               "nodes_peak_log": float(p["peak_median_log_nodes"]), "nodes_interior": bool(p["interior"]),
               "nodes_ci_lo": float(p["ci_lo"]), "nodes_ci_hi": float(p["ci_hi"]), "nodes_excess": float(p["excess"])}
        for col in GAP_COLUMNS:
            pk = peak_of(g, sub, col, resamples, rng)
            row.update(pk)
            pred, meas = pk[f"{col}_peak_col_mean"], row["nodes_peak_col_mean"]
            err = float(np.log10(pred / meas))
            lo, hi = row["nodes_ci_lo"], row["nodes_ci_hi"]
            within = bool(lo <= pred <= hi) if np.isfinite(lo) else bool(abs(err) <= 0.05)
            row[f"{col}_log10_error"] = err
            row[f"{col}_within_ci"] = within
            row[f"{col}_peak_excess"] = float(np.interp(np.log10(pred), np.log10(g.sort_values("col_mean")["col_mean"]),
                                                        g.sort_values("col_mean")["e"]))
        rows.append(row)
    return pd.DataFrame(rows)


def score_summary(peaks: pd.DataFrame) -> pd.DataFrame:
    """Per gap: series, mean and worst |log10 error|, signed mean, within
    the interval, interior peaks, and the signed error per ratio."""
    ratios = ["2n", "n", "n/2", "n/4", "n/8"]
    rows = []
    for col in GAP_COLUMNS:
        err = peaks[f"{col}_log10_error"]
        by = peaks.groupby("ratio_label")[f"{col}_log10_error"].mean()
        rows.append({"gap": col, "text": GAP_TEXT[col], "series": len(peaks),
                     "mean_abs_log10_error": float(err.abs().mean()), "max_abs_log10_error": float(err.abs().max()),
                     "mean_signed_log10_error": float(err.mean()),
                     "within_ci": int(peaks[f"{col}_within_ci"].sum()),
                     "outside_ci": int((~peaks[f"{col}_within_ci"]).sum()),
                     "gap_peak_interior": int(peaks[f"{col}_interior"].sum()),
                     **{f"err_{r}": float(by.get(r, np.nan)) for r in ratios}})
    return pd.DataFrame(rows)


def kill_verdict(summary: pd.DataFrame) -> dict:
    """H1 is dead if either gap's peak lies outside the node peak's interval on
    more than half the series, or its mean score exceeds 0.15 decades; the
    verdict is given per gap and overall (H1 survives only if one reading
    survives both tests)."""
    out = {}
    alive = False
    for _, r in summary.iterrows():
        outside_frac = r["outside_ci"] / r["series"]
        dead = outside_frac > KILL_MAX_OUTSIDE_FRAC or r["mean_abs_log10_error"] > KILL_MEAN_SCORE
        out[r["gap"]] = {"outside_frac": float(outside_frac), "mean_abs_log10_error": float(r["mean_abs_log10_error"]),
                         "dead": bool(dead)}
        alive = alive or not dead
    out["h1_dead"] = not alive
    return out


def profile_table(cells: pd.DataFrame) -> pd.DataFrame:
    """Per series: is each gap monotone along the density grid, and the
    Spearman correlation of the cell means with the median log nodes."""
    from scipy.stats import spearmanr
    rows = []
    for (gen, lab, n), g in cells.groupby(["generator", "ratio_label", "n"]):
        g = g.sort_values("col_mean")
        row = {"generator": gen, "ratio_label": lab, "n": int(n), "cells": len(g),
               "col_mean_range": f"{g['col_mean'].min():.3g}–{g['col_mean'].max():.3g}",
               "e_range": f"{g['e'].min():.2f}–{g['e'].max():.2f}"}
        for col in GAP_COLUMNS:
            v = g[col].to_numpy(float)
            d = np.diff(v)
            row[f"{col}_shape"] = ("increasing" if np.all(d >= 0) else "decreasing" if np.all(d <= 0)
                                   else "peaked" if np.argmax(v) not in (0, len(v) - 1) else "dipped")
            row[f"{col}_range"] = f"{v.min():.3f}–{v.max():.3f}"
            row[f"{col}_rho_nodes"] = float(spearmanr(v, g["median_log_nodes"].to_numpy(float)).correlation)
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# the secondary test: optimal closing orders at n = 20, vectorised
# ----------------------------------------------------------------------------

_POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def _popcount32(a: np.ndarray) -> np.ndarray:
    return _POP8[a.view(np.uint8)].reshape(-1, 4).sum(axis=1, dtype=np.uint8)


def _bits(mask: int):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def lattice_weights(instance: MOSPInstance) -> tuple[Compact, np.ndarray, np.ndarray]:
    """`(comp, search, construction)`: the two edge costs of the closed-customer
    lattice as `(a, 2^a)` int8 arrays indexed `[c, S]` (meaningful for `c` not
    in `S`), the same values as `learning.degeneracy.closing_weights` returns
    at `S * a + c`, computed by vector operations over the states.

    construction: the peak number of open stacks while the unproduced products
    of `c` are made in index order from state `S`; with `opened(S)` the
    customers sharing a product with `S`, `done(S)` those all of whose products
    are made, `H_j` the holders of the first `j` products of `c`, and `fin_j`
    the customers finished by the first `j` steps that were not done at `S`,
    the count after step `j` is `|opened(S) ∪ H_j| − |done(S)| − fin_{j−1}`
    (done customers and finished ones are started, so the differences are
    exact); a step whose product is already made does not happen.
    """
    comp = Compact(instance)
    a, m = comp.a, comp.m
    if a > 25 or m > 63:
        raise ValueError("the vectorised lattice is for a <= 25 customers and m <= 63 products")
    size = 1 << a
    idx = np.arange(size, dtype=np.uint32)
    opened = np.zeros(size, dtype=np.uint32)
    made = np.zeros(size, dtype=np.uint64)
    for b in range(a):
        lo, hi = 1 << b, 1 << (b + 1)
        opened[lo:hi] = opened[:lo] | np.uint32(comp.neigh[b])
        made[lo:hi] = made[:lo] | np.uint64(comp.prod[b])
    done_count = np.zeros(size, dtype=np.int8)
    for q in range(a):
        pq = np.uint64(comp.prod[q])
        done_count += ((made & pq) == pq).astype(np.int8)
    opened_count = _popcount32(opened).astype(np.int8)
    not_opened = [(((opened >> np.uint32(q)) & np.uint32(1)) == 0).astype(np.int8) for q in range(a)]
    new_product = [((made & np.uint64(1 << p)) == 0).astype(np.int8) for p in range(m)]
    remaining = [np.zeros(size, dtype=np.int8) for _ in range(a)]   # |prod[q] \ made(S)|
    for q in range(a):
        for p in _bits(comp.prod[q]):
            remaining[q] += new_product[p]
    search = np.empty((a, size), dtype=np.int8)
    construction = np.zeros((a, size), dtype=np.int8)
    for c in range(a):
        search[c] = _popcount32((opened | np.uint32(comp.neigh[c])) & ~idx).astype(np.int8)
        started = opened_count.copy()          # |opened(S) ∪ H_j|
        fin = np.zeros(size, dtype=np.int8)    # finished during c's steps, not done at S
        rem = {q: remaining[q].copy() for q in _bits(comp.neigh[c])}
        in_h = 0
        peak = np.zeros(size, dtype=np.int8)
        for p in _bits(comp.prod[c]):
            newly = new_product[p]
            holders = comp.holders[p]
            for q in _bits(holders & ~in_h):
                started += not_opened[q]
            in_h |= holders
            cnt = started - done_count - fin
            np.maximum(peak, cnt * newly, out=peak)
            for q in _bits(holders):
                fin += (rem[q] == 1).astype(np.int8) * newly
                rem[q] -= newly
        construction[c] = peak
    return comp, search, construction


def _layers(a: int) -> tuple[np.ndarray, np.ndarray]:
    idx = np.arange(1 << a, dtype=np.uint32)
    pop = _popcount32(idx)
    order = np.argsort(pop, kind="stable").astype(np.uint32)
    starts = np.concatenate([[0], np.cumsum(np.bincount(pop, minlength=a + 1))])
    return order, starts


def lattice_minimum_np(weights: np.ndarray) -> int:
    """The bottleneck through the lattice: min over orders of the max edge cost."""
    a, size = weights.shape
    order, starts = _layers(a)
    best = np.full(size, 127, dtype=np.int8)
    best[0] = 0
    for s in range(1, a + 1):
        layer = order[starts[s]:starts[s + 1]]
        acc = np.full(len(layer), 127, dtype=np.int8)
        for c in range(a):
            bit = np.uint32(1 << c)
            has = (layer & bit) != 0
            src = layer[has] ^ bit
            acc[has] = np.minimum(acc[has], np.maximum(best[src], weights[c, src]))
        best[layer] = acc
    return int(best[size - 1])


def lattice_count_np(weights: np.ndarray, k: int) -> tuple[int, int]:
    """`(f[full], g[0])`: the number of closing orders whose every step costs at
    most `k`, counted forward and backward (equal by construction; both are
    returned so a caller can assert it)."""
    a, size = weights.shape
    full = size - 1
    order, starts = _layers(a)
    ok = weights <= k
    f = np.zeros(size, dtype=np.int64)
    f[0] = 1
    for s in range(1, a + 1):
        layer = order[starts[s]:starts[s + 1]]
        acc = np.zeros(len(layer), dtype=np.int64)
        for c in range(a):
            bit = np.uint32(1 << c)
            has = (layer & bit) != 0
            src = layer[has] ^ bit
            acc[has] += f[src] * ok[c, src]
        f[layer] = acc
    g = np.zeros(size, dtype=np.int64)
    g[full] = 1
    for s in range(a - 1, -1, -1):
        layer = order[starts[s]:starts[s + 1]]
        acc = np.zeros(len(layer), dtype=np.int64)
        for c in range(a):
            bit = np.uint32(1 << c)
            lacks = (layer & bit) == 0
            src = layer[lacks]
            acc[lacks] += g[src | bit] * ok[c, src]
        g[layer] = acc
    return int(f[full]), int(g[0])


def lattice_row(instance: MOSPInstance, optimum: int) -> dict:
    """Every count for one instance: the lattice minima under both measures
    against the certified optimum, the optimal-order counts at the certified
    value, the twin factor and the log10 share of all `a!` orders."""
    t = time.perf_counter()
    comp, search, construction = lattice_weights(instance)
    a = comp.a
    min_c, min_s = lattice_minimum_np(construction), lattice_minimum_np(search)
    fc, gc = lattice_count_np(construction, optimum)
    fs, gs = lattice_count_np(search, optimum)
    if fc != gc or fs != gs:
        raise AssertionError(f"{instance.name}: forward and backward counts disagree")
    twin = comp.twin_factor()
    lfact = math.lgamma(a + 1) / math.log(10)
    return {"instance_name": instance.name, "n_active": a, "m_active": comp.m, "optimum": int(optimum),
            "min_construction": min_c, "min_search": min_s,
            "audit_construction": min_c == optimum, "audit_search": min_s == optimum,
            "count_closing": fc, "count_search": fs, "twin_factor": twin,
            "log10_count_closing": math.log10(fc) if fc else -np.inf,
            "log10_count_search": math.log10(fs) if fs else -np.inf,
            "log10_share_closing": (math.log10(fc) - lfact) if fc else -np.inf,
            "log10_share_search": (math.log10(fs) - lfact) if fs else -np.inf,
            "lattice_seconds": time.perf_counter() - t}


def _lattice_job(args) -> dict:
    generator, n, m, param, index, name, n_ones, optimum = args
    cell = Cell(generator, int(n), int(m), float(param))
    inst = generate(cell, index)
    if inst.name != name or int(inst.matrix.sum()) != int(n_ones):
        raise AssertionError(f"{name}: regeneration does not match the record")
    return lattice_row(inst, int(optimum))


def lattice_jobs(per_cell: int | None = None, n: int = SECONDARY_N, results_csv: Path = RESULTS_CSV) -> pd.DataFrame:
    r = load_results(results_csv)
    r = r[(r["n"] == n) & r["certified"].astype(bool)].copy()
    r = r.sort_values(["cell", "index"])
    if per_cell is not None:
        r = r.groupby("cell", group_keys=False).head(per_cell)
    return r


def default_workers(cap: int = 8) -> int:
    load = os.getloadavg()[0]
    return min(cap, 4) if load > 24 else cap


def _map(fn, jobs, workers: int) -> list:
    if workers <= 1:
        return [fn(j) for j in jobs]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, jobs, chunksize=4))


def run_lattice(workers: int, per_cell: int | None = None, out: Path = LATTICE_CSV) -> pd.DataFrame:
    """The `n = 20` counts on the campaign's certified instances (regenerated
    from their seeds), joined with the recorded node counts and section 36's
    reachable-set counts."""
    os.nice(19)
    started = time.time()
    r = lattice_jobs(per_cell)
    jobs = [(g, int(n), int(m), float(p), int(i), nm, int(o), int(opt)) for g, n, m, p, i, nm, o, opt
            in zip(r["generator"], r["n"], r["m"], r["param"], r["index"], r["instance_name"], r["n_ones"],
                   r["optimum"])]
    rows = _map(_lattice_job, jobs, workers)
    frame = pd.DataFrame(rows).merge(
        r[["instance_name", "cell", "generator", "n", "m", "param", "n_ones", "col_mean", "nodes_default",
           "nodes_csearch", "status_default", "g_components", "complete_graph"]], on="instance_name")
    frame["e"] = (frame["n_ones"] - frame["m"]) / frame["n"]
    frame["opt_n"] = frame["optimum"] / frame["n"]
    frame["log10_nodes"] = np.log10(1 + frame["nodes_default"].astype(float))
    if STATES_CSV.exists():
        st = pd.read_csv(STATES_CSV)[["instance_name", "reachable_states", "log10_reachable", "fitting_states"]]
        frame = frame.merge(st, on="instance_name", how="left")
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    bad = frame[~frame["audit_construction"] | ~frame["audit_search"]]
    print(f"lattice: {len(frame)} instances at n = {SECONDARY_N}, {frame['lattice_seconds'].sum() / 3600:.2f} "
          f"core-hours of lattice time, {time.time() - started:.0f} s wall on {workers} workers; "
          f"audit failures: {len(bad)} -> {out}", flush=True)
    if len(bad):
        print(bad[["instance_name", "optimum", "min_construction", "min_search"]].to_string())
    return frame


def lattice_cells(frame: pd.DataFrame) -> pd.DataFrame:
    """Per cell: medians of the log10 counts and shares, of log10 nodes and of
    the reachable count, `opt / n`, and the audit."""
    rows = []
    for (gen, m, param), g in frame.groupby(["generator", "m", "param"]):
        rows.append({"generator": gen, "m": int(m), "param": float(param), "instances": len(g),
                     "col_mean": float(g["col_mean"].median()), "e": float(g["e"].median()),
                     "opt_n": float(g["opt_n"].mean()),
                     "median_log10_nodes": float(g["log10_nodes"].median()),
                     "median_log10_reachable": float(g["log10_reachable"].median()) if "log10_reachable" in g else np.nan,
                     "median_log10_count_closing": float(g["log10_count_closing"].median()),
                     "median_log10_share_closing": float(g["log10_share_closing"].median()),
                     "median_log10_count_search": float(g["log10_count_search"].median()),
                     "median_log10_share_search": float(g["log10_share_search"].median()),
                     "unique_up_to_twins": int(((g["count_closing"] // g["twin_factor"]) == 1).sum()),
                     "audit_ok": int((g["audit_construction"] & g["audit_search"]).sum()),
                     "connected": int((g["g_components"] == 1).sum())})
    return pd.DataFrame(rows).sort_values(["generator", "m", "col_mean"]).reset_index(drop=True)


def lattice_series(cells: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    """Per (generator, m): the peak cell of the node count and of each count,
    the shape of each count along the grid and the Spearman correlations with
    the nodes (over cells, and over instances)."""
    from scipy.stats import spearmanr
    rows = []
    for (gen, m), g in cells.groupby(["generator", "m"]):
        g = g.sort_values("col_mean")
        sub = frame[(frame["generator"] == gen) & (frame["m"] == m)]
        row = {"generator": gen, "m": int(m), "cells": len(g),
               "nodes_peak_col_mean": float(g.loc[g["median_log10_nodes"].idxmax(), "col_mean"]),
               "nodes_peak_e": float(g.loc[g["median_log10_nodes"].idxmax(), "e"])}
        for col, lab in (("median_log10_count_closing", "count_closing"), ("median_log10_share_closing", "share_closing"),
                         ("median_log10_count_search", "count_search"), ("median_log10_reachable", "reachable")):
            v = g[col].to_numpy(float)
            if not np.all(np.isfinite(v)):
                row[f"{lab}_shape"] = "n/a"
                continue
            d = np.diff(v)
            row[f"{lab}_shape"] = ("increasing" if np.all(d >= 0) else "decreasing" if np.all(d <= 0)
                                   else "peaked" if np.argmax(v) not in (0, len(v) - 1) else "dipped")
            row[f"{lab}_peak_col_mean"] = float(g.loc[g[col].idxmax(), "col_mean"])
            row[f"{lab}_rho_cells"] = float(spearmanr(v, g["median_log10_nodes"].to_numpy(float)).correlation)
        inst_col = {"count_closing": "log10_count_closing", "share_closing": "log10_share_closing",
                    "count_search": "log10_count_search", "opt_n": "opt_n"}
        for lab, col in inst_col.items():
            x = sub[col].replace(-np.inf, np.nan)
            row[f"{lab}_rho_instances"] = float(spearmanr(x, sub["log10_nodes"], nan_policy="omit").correlation)
        row["share_rho_opt_n"] = float(spearmanr(sub["log10_share_closing"].replace(-np.inf, np.nan), sub["opt_n"],
                                                 nan_policy="omit").correlation)
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# tables, figure, driver
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def h1_tables(inst: pd.DataFrame, cells: pd.DataFrame, peaks: pd.DataFrame) -> str:
    summary = score_summary(peaks)
    verdict = kill_verdict(summary)
    out = ["## H1 summary", "", _md(summary, ".3f"), "", f"kill: {verdict}", "",
           "## Peaks per series (col_mean; errors in decades against the node peak)", ""]
    show = ["generator", "ratio_label", "n", "nodes_peak_col_mean", "nodes_ci_lo", "nodes_ci_hi", "nodes_interior",
            "nodes_excess"]
    for col in GAP_COLUMNS:
        show += [f"{col}_peak_col_mean", f"{col}_interior", f"{col}_ci_lo", f"{col}_ci_hi", f"{col}_peak_excess",
                 f"{col}_log10_error", f"{col}_within_ci"]
    out += [_md(peaks[show], ".3f"), "", "## Profiles per series", "", _md(profile_table(cells), ".3f"), "",
            "## Cells, in full", "",
            _md(cells[["generator", "ratio_label", "n", "param", "m", "instances", "col_mean", "e", "median_log_nodes",
                       "censored", "opt_n", "floor_001_n", "beta_star", "gap_floor", "gap_floor_se", "gap_floor_1",
                       "gap_beta", "gap_beta_se"]], ".3f"), ""]
    return "\n".join(out)


def lattice_tables(frame: pd.DataFrame) -> str:
    cells = lattice_cells(frame)
    series = lattice_series(cells, frame)
    audit = frame[~frame["audit_construction"] | ~frame["audit_search"]]
    out = [f"## Lattice at n = {SECONDARY_N}: {len(frame)} instances, audit failures {len(audit)}, "
           f"{frame['lattice_seconds'].sum() / 3600:.2f} core-hours", "",
           "## Per series", "", _md(series, ".3f"), "", "## Per cell", "", _md(cells, ".3f"), ""]
    return "\n".join(out)


def figure(peaks: pd.DataFrame, cells: pd.DataFrame, out: Path = FIGURE) -> Path:
    """Peak locations per series: for each of the 25 series (rows, grouped by
    generator and ratio) the node peak with its bootstrap interval, and the
    two gap peaks, on a log `col_mean` axis; one panel per ratio so the
    ten-fold range of `col_mean` across ratios does not flatten the
    comparison. Three quantities, three categorical slots of the reference
    palette; PNG for the report; no title inside the figure."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker
    from matplotlib.lines import Line2D

    colours = {"nodes": "#2a78d6", "gap_floor": "#eb6834", "gap_beta": "#1baf7a"}
    labels = {"nodes": "nodes to refute optimum − 1 (median; bar: 95% bootstrap)",
              "gap_floor": "(opt − floor₀.₀₁) / n, cell mean",
              "gap_beta": "opt / n − β*, cell mean"}
    ratios = [r for r in ("2n", "n", "n/2", "n/4", "n/8") if r in set(peaks["ratio_label"])]
    fig, axes = plt.subplots(1, len(ratios), figsize=(3.0 * len(ratios), 3.6), squeeze=False)
    for ax, lab in zip(axes.ravel(), ratios):
        g = peaks[peaks["ratio_label"] == lab].sort_values(["generator", "n"])
        ys = np.arange(len(g))[::-1]
        for y, (_, p) in zip(ys, g.iterrows()):
            if np.isfinite(p["nodes_ci_lo"]):
                ax.plot([p["nodes_ci_lo"], p["nodes_ci_hi"]], [y, y], color=colours["nodes"], lw=2, alpha=0.35,
                        solid_capstyle="butt", zorder=1)
            ax.plot(p["nodes_peak_col_mean"], y, marker="o", ms=7, color=colours["nodes"], ls="none", zorder=3,
                    markeredgecolor="#fcfcfb", markeredgewidth=1)
            for col, mk in (("gap_floor", "s"), ("gap_beta", "D")):
                if p[f"{col}_interior"]:
                    ax.plot(p[f"{col}_peak_col_mean"], y, marker=mk, ms=6, color=colours[col], ls="none", zorder=4,
                            markeredgecolor="#fcfcfb", markeredgewidth=1)
                else:
                    ax.plot(p[f"{col}_peak_col_mean"], y, marker=mk, ms=6, ls="none", zorder=4,
                            markerfacecolor="none", markeredgecolor=colours[col], markeredgewidth=1.5)
        ax.set_yticks(ys)
        ax.set_yticklabels([f"{'fixed' if r['generator'] == 'fixed' else 'bern.'} n={int(r['n'])}"
                            for _, r in g.iterrows()], fontsize=8, color="#52514e")
        ax.set_xscale("log")
        xs = np.concatenate([g[c].to_numpy(float) for c in ("nodes_peak_col_mean", "gap_floor_peak_col_mean",
                                                            "gap_beta_peak_col_mean", "nodes_ci_lo", "nodes_ci_hi")])
        xs = xs[np.isfinite(xs)]
        ax.set_xlim(xs.min() / 1.12, xs.max() * 1.12)
        ticks = [t for t in (1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25) if xs.min() / 1.12 <= t <= xs.max() * 1.12]
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t:g}" for t in ticks])
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_title(f"m = {lab}", fontsize=10, color="#0b0b0b", loc="left")
        ax.grid(False)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#c3c2b7")
        ax.tick_params(colors="#52514e", labelsize=8)
        ax.set_xlabel("customers per pattern (col_mean)", fontsize=8, color="#52514e")
        ax.set_ylim(-0.7, len(g) - 0.3)
    handles = [Line2D([], [], ls="none", marker="o", color=colours["nodes"], ms=7, label=labels["nodes"]),
               Line2D([], [], ls="none", marker="s", color=colours["gap_floor"], ms=6, label=labels["gap_floor"]),
               Line2D([], [], ls="none", marker="D", color=colours["gap_beta"], ms=6, label=labels["gap_beta"]),
               Line2D([], [], ls="none", marker="s", color="#52514e", ms=6, fillstyle="none",
                      label="open marker: the gap's maximum is at the grid edge (no interpolation)")]
    fig.legend(handles=handles, loc="upper left", frameon=False, fontsize=8, ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.84))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)
    return out


def run_h1(resamples: int = RESAMPLES) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    started = time.time()
    inst = instance_frame()
    cells = cell_frame(inst)
    peaks = peaks_table(inst, cells, resamples)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    inst.to_csv(INSTANCES_CSV, index=False)
    cells.to_csv(CELLS_CSV, index=False)
    peaks.to_csv(PEAKS_CSV, index=False)
    print(f"H1: {len(inst)} instances, {len(cells)} cells, {len(peaks)} series, {time.time() - started:.0f} s "
          f"-> {INSTANCES_CSV}, {CELLS_CSV}, {PEAKS_CSV}", flush=True)
    return inst, cells, peaks


def load_h1() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (pd.read_csv(INSTANCES_CSV, low_memory=False), pd.read_csv(CELLS_CSV), pd.read_csv(PEAKS_CSV))


def tables() -> str:
    inst, cells, peaks = load_h1()
    text = h1_tables(inst, cells, peaks)
    if LATTICE_CSV.exists():
        text += "\n" + lattice_tables(pd.read_csv(LATTICE_CSV))
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / "tables.md").write_text(text)
    return text
