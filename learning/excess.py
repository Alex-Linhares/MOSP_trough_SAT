"""The map: every instance on record placed by its excess (loop0010 item 01).

The excess of an instance with `n` customers, `m` patterns and `n_ones` ones is

    e = (n_ones - m) / n = (mean patterns per customer) - 1 = r (c - 1),

with `r = m / n` and `c = n_ones / m` the mean customers per pattern. The
customer-pattern incidence graph `B` has `n + m` vertices, `n_ones` edges and
`kappa` components, so its cyclomatic number is `gamma = n_ones - n - m + kappa`
and `gamma / n = e - 1 + kappa / n`. `B` is a forest iff `gamma = 0` iff its
(2, 2)-core is empty.

Three lines of constant excess are on record (`reports/excess_phase_plan.md`
section 0): `e = 1`, where the first-moment bound turns on; the hardness ridge at
`e ~ 2-2.4`; and `e_g(r) = (sqrt(r^2 + 4 r) - r) / 2`, the giant component of
the random incidence graph with patterns of a fixed size (branching factor
`r c (c - 1) = 1` in excess coordinates). This module computes `e`, `r`, `c`,
`kappa`, `gamma`, the largest component of `B`, the forest flag and the
(2, 2)-core for every instance we hold -- the 6,376 corpus instances, the
~50,700 certified random covers of the four ensemble frames (regenerated from
their seeds, never re-solved) and the 7,200 generator simulations of
`reports/scratch/clique_cover_moment/floor_violation.csv` -- and tabulates them
per collection and per ensemble series, with one stated check: that the
largest component of `B` crosses one half within +-0.15 in `e` of `e_g(r)` on
every ensemble series at `n >= 50`.

Nothing here solves anything, reads `solutions/` or writes outside
`learning/data/excess.csv`, `reports/figures/` and stdout. Descriptive only: the
map says where the instances we happen to hold sit, nothing about the optimum.

Usage:
    python -m learning.excess                       # build + tables + figure (~2 min on 8 workers)
    python -m learning.excess --stage build --workers 8
    python -m learning.excess --stage tables        # from learning/data/excess.csv
    python -m learning.excess --stage rule          # item 02: the two-key rule on every instance -> excess_rule.csv
    python -m learning.excess --stage slopes        # item 02: opt = a + b n per series, e-matched pairs, beta*
    python -m learning.excess --stage figure-opt    # item 02: reports/figures/excess_opt.png
    python -m learning.excess --stage constructions          # item 05: the constructions grid -> excess_constructions.csv
    python -m learning.excess --stage constructions-tables   # item 05: the tables
    python -m learning.excess --stage figure-constructions   # item 05: reports/figures/excess_beta_plus.png
    python -m learning.excess --stage forest_check           # item 06: F1, F2, F3 and Lemma P by brute force -> reports/scratch/forest_check/
    python -m learning.excess --stage ridge                  # item 09: H1, the gap peaks against the node peaks -> excess_ridge_*.csv
    python -m learning.excess --stage ridge-lattice          # item 09: optimal closing orders at n = 20 (about 1.5 core-hours)
    python -m learning.excess --stage ridge-tables           # item 09: every table -> reports/scratch/excess_ridge/tables.md
    python -m learning.excess --stage figure-ridge           # item 09: reports/figures/excess_ridge.png
    python -m pytest tests/test_excess.py -q
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from learning.cover_excess import peel
from learning.ensemble import ENSEMBLE_DIR, Cell, generate
from mosp.instance import MOSPInstance

DATA_DIR = Path("learning/data")
OUT_CSV = DATA_DIR / "excess.csv"
INSTANCES_CSV = DATA_DIR / "instances.csv"
SOLUTIONS_DIR = Path("solutions")
RULE_CSV = DATA_DIR / "excess_rule.csv"
FIGURE_OPT = Path("reports/figures/excess_opt.png")
BOUND_GAP_CSV = DATA_DIR / "bound_gap.csv"
SIM_DIR = Path("reports/scratch/clique_cover_moment")
SIM_CSV = SIM_DIR / "floor_violation.csv"
FIGURE = Path("reports/figures/excess_giant_component.png")
FRAMES = {"campaign": "results.csv", "upward": "results_upward.csv",
          "ratio": "results_ratio.csv", "height": "results_height.csv"}
RATIO_LABELS = {0.125: "n/8", 0.25: "n/4", 0.5: "n/2", 1.0: "n", 2.0: "2n", 4.0: "4n", 8.0: "8n"}
CHECK_TOLERANCE = 0.15
CHECK_MIN_N = 50
QUANTILES = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)
QUANTILE_NAMES = ("min", "q10", "q25", "median", "q75", "q90", "max")

# ----------------------------------------------------------------------------
# the parameter and the lines
# ----------------------------------------------------------------------------


def excess(n: float, m: float, n_ones: float) -> float:
    """`e = (n_ones - m) / n`, the mean number of patterns per customer minus one."""
    return (n_ones - m) / n


def giant_threshold_excess(r: float, generator: str = "fixed") -> float:
    """The excess at which the random incidence graph's branching factor is one.

    `fixed` (every pattern has the same size `c`, Poisson customers): the
    branching factor is `r c (c - 1)`, so `e = r (c - 1)` solves
    `e^2 + r e - r = 0`: `e_g(r) = (sqrt(r^2 + 4 r) - r) / 2`, 0.618 at `r = 1`.
    `bernoulli` (Poisson sizes on both sides, before the generators' repairs):
    the branching factor is `r c^2`, so `e_g = sqrt(r) - r`, which is zero at
    `r = 1` -- the repairs make it meaningless there and the plan's check uses
    the `fixed` form for both generators.
    """
    if generator == "bernoulli":
        return float(np.sqrt(r) - r)
    return float((np.sqrt(r * r + 4.0 * r) - r) / 2.0)


def ratio_label(r: float) -> str:
    """The nearest named product ratio (the frames realise n/8 as 0.12, n/2 as 0.493)."""
    keys = np.array(sorted(RATIO_LABELS))
    k = keys[np.argmin(np.abs(np.log(keys) - np.log(r)))]
    return RATIO_LABELS[float(k)]


# ----------------------------------------------------------------------------
# the incidence graph of one matrix
# ----------------------------------------------------------------------------


def incidence_components(matrix: np.ndarray) -> np.ndarray:
    """Component label of every vertex of `B` (customers first, then patterns)."""
    a = np.asarray(matrix, dtype=bool)
    n, m = a.shape
    i, j = np.nonzero(a)
    g = coo_matrix((np.ones(len(i), dtype=np.int8), (i, n + j)), shape=(n + m, n + m))
    _, labels = connected_components(g, directed=False)
    return labels


def incidence_stats(matrix: np.ndarray) -> dict:
    """`n`, `m`, `n_ones`, `e`, `r`, `c`, `kappa`, `gamma`, `gamma_n`, `forest`,
    the largest component of `B` as a fraction of its vertices (`lcc_frac`) and
    of its customers (`lcc_cust_frac`), and the (2, 2)-core as a fraction of the
    customers, the patterns and the vertices. The core is empty iff `gamma = 0`,
    which is asserted."""
    a = np.asarray(matrix, dtype=np.int64)
    n, m = a.shape
    n_ones = int(a.sum())
    labels = incidence_components(a)
    kappa = int(labels.max()) + 1 if len(labels) else 0
    gamma = n_ones - n - m + kappa
    counts = np.bincount(labels)
    big = int(np.argmax(counts))
    cust, prod = peel(a, 2, 2)
    nc, npd = int(cust.sum()), int(prod.sum())
    forest = gamma == 0
    if forest != (nc + npd == 0):
        raise AssertionError("the (2,2)-core is empty exactly when the incidence graph is a forest")
    return {
        "n": n, "m": m, "n_ones": n_ones,
        "e": excess(n, m, n_ones), "r": m / n, "c": n_ones / m if m else np.nan,
        "kappa": kappa, "gamma": int(gamma), "gamma_n": gamma / n, "forest": bool(forest),
        "lcc_frac": int(counts[big]) / (n + m),
        "lcc_cust_frac": int((labels[:n] == big).sum()) / n,
        "core2_cust_frac": nc / n, "core2_prod_frac": npd / m if m else np.nan,
        "core2_vertex_frac": (nc + npd) / (n + m),
    }


# ----------------------------------------------------------------------------
# the three sources
# ----------------------------------------------------------------------------

_CS_CLASS = re.compile(r"^(Random-\d+-\d+-\d+)-\d+_\d+$")


def collection_of(source_file: str, instance_name: str) -> tuple[str, str]:
    """(collection, class): the collection from the directory of the source
    file; the class is the Chu & Stuckey `Random-n-m-d` for that collection,
    the Harvey file stem (`wbo_10_10`) for Harvey, and the collection otherwise."""
    parts = Path(source_file).parts
    directory = parts[-2] if len(parts) >= 2 else ""
    names = {"SCOOP": "SCOOP", "Faggioli_Bentivoglio": "Faggioli-Bentivoglio", "Chu_Stuckey": "Chu & Stuckey",
             "Harvey": "Harvey", "Simonis": "Simonis", "Shaw": "Shaw", "Wilson": "Wilson", "Miller": "Miller",
             "Challenge": "Challenge"}
    collection = names.get(directory, directory)
    if collection == "Chu & Stuckey":
        match = _CS_CLASS.match(instance_name)
        return collection, match.group(1) if match else instance_name
    if collection == "Harvey":
        return collection, Path(source_file).stem
    return collection, collection


def solution_record(instance: MOSPInstance, solutions_dir: Path = SOLUTIONS_DIR) -> tuple[float, str]:
    """(value, provenance) of the instance's cached solution, read from the file
    (`solutions/` is the source of truth; `instances.csv` is a feature table
    from 2026-09-25 and lags it -- four 125 x 125 instances certified in
    October 2026 are `solution` there). `(nan, "")` where there is no file."""
    import json
    from satisfiability.mosp_solver import _solution_path
    path = _solution_path(instance, solutions_dir)
    if not path.exists():
        return np.nan, ""
    with open(path) as handle:
        record = json.load(handle)
    return float(record["mosp_value"]), str(record.get("provenance", ""))


def _corpus_job(args) -> dict:
    source_file, name, matrix = args
    row = incidence_stats(matrix)
    collection, cls = collection_of(source_file, name)
    value, provenance = solution_record(MOSPInstance.from_matrix(matrix, name=name))
    row.update({"source": "corpus", "frame": "corpus", "instance_name": name, "source_file": source_file,
                "collection": collection, "series": cls, "generator": "", "param": np.nan,
                "provenance": provenance, "optimum": value})
    return row


def corpus_rows(workers: int) -> pd.DataFrame:
    """One row per instance of the benchmark tree, with its cached optimum and
    provenance read from `solutions/` (read only); `certified` is read from the
    provenance, never assumed, and the optimum is blanked where it is not."""
    from learning.dataset import enumerate_instances
    jobs = [(str(path), inst.name, inst.matrix) for path, inst in enumerate_instances()]
    frame = pd.DataFrame(_map(_corpus_job, jobs, workers))
    frame["certified"] = frame["provenance"].fillna("").str.startswith("certified")
    frame.loc[~frame["certified"], "optimum"] = np.nan
    return frame


def _ensemble_job(args) -> dict:
    frame_name, cell_text, index, name, n_ones_recorded, optimum, certified = args
    cell = Cell.parse(cell_text)
    inst = generate(cell, index)
    if inst.name != name:
        raise AssertionError(f"regenerated {inst.name}, expected {name}")
    row = incidence_stats(inst.matrix)
    if row["n_ones"] != n_ones_recorded:
        raise AssertionError(f"{name}: regenerated n_ones {row['n_ones']} differs from the record {n_ones_recorded}")
    row.update({"source": "ensemble", "frame": frame_name, "instance_name": name, "source_file": "",
                "collection": "ensemble", "series": f"{cell.generator} r={ratio_label(cell.m / cell.n)} "
                f"{'p' if cell.generator == 'bernoulli' else 'd'}={cell.param:g} n={cell.n}",
                "generator": cell.generator, "param": cell.param, "cell": cell.id,
                "optimum": optimum if certified else np.nan, "certified": bool(certified)})
    return row


def ensemble_jobs(ensemble_dir: Path = ENSEMBLE_DIR) -> list[tuple]:
    """`(frame, cell text, index, name, n_ones, optimum, certified)` for every
    instance of the four frames; the upward frame's finish file promotes the
    instances it refuted."""
    from learning.upward import apply_finish
    jobs = []
    for frame_name, file in FRAMES.items():
        path = ensemble_dir / file
        if not path.exists():
            continue
        f = pd.read_csv(path)
        if frame_name == "upward":
            f = apply_finish(f, path.with_name("results_upward_finish.csv"))
        for r in f.itertuples(index=False):
            tag = "b" if r.generator == "bernoulli" else "f"
            jobs.append((frame_name, f"{tag}:{r.n}:{r.m}:{r.param}", int(r.index), r.instance_name,
                         int(r.n_ones), int(r.optimum), bool(r.certified)))
    return jobs


def ensemble_rows(workers: int, ensemble_dir: Path = ENSEMBLE_DIR) -> pd.DataFrame:
    """Every instance of the four frames, regenerated from its seed (the
    recorded `n_ones` must agree, byte-for-byte regeneration being the claim of
    the ensemble manifests)."""
    return pd.DataFrame(_map(_ensemble_job, ensemble_jobs(ensemble_dir), workers))


def _sim_job(args) -> dict:
    gen, n, m, d, seed, ones_recorded, opt = args
    if str(SIM_DIR.resolve()) not in sys.path:
        sys.path.insert(0, str(SIM_DIR.resolve()))
    from gen_candidates import CANDIDATES  # noqa: PLC0415 - scratch module, imported where it lives
    rng = np.random.default_rng(seed)
    matrix, _tries = CANDIDATES[gen](n, m, d, rng)
    if matrix is None:
        raise AssertionError(f"simulation {gen} {n} {m} {d} {seed} was accepted on record but not now")
    row = incidence_stats(matrix.T)
    if row["n_ones"] != ones_recorded:
        raise AssertionError(f"simulation seed {seed}: regenerated ones {row['n_ones']} differ from {ones_recorded}")
    row.update({"source": "simulation", "frame": "simulation", "instance_name": f"sim-{gen}-{n}-{m}-{d}-{seed}",
                "source_file": "", "collection": "simulation", "series": f"{gen} n={n} d={d}", "generator": gen,
                "param": d, "cell": f"{gen}_n{n}_m{m}_d{d}", "optimum": opt, "certified": True})
    return row


def simulation_rows(workers: int, sim_csv: Path = SIM_CSV) -> pd.DataFrame:
    """The 7,200 generator simulations, regenerated from their seeds with the
    scratch generator; their optima are certified (`sim_solutions/`)."""
    if not sim_csv.exists():
        return pd.DataFrame()
    f = pd.read_csv(sim_csv)
    jobs = [(r.gen, int(r.n), int(r.m), int(r.d), int(r.seed), int(r.ones), int(r.opt)) for r in f.itertuples()]
    return pd.DataFrame(_map(_sim_job, jobs, workers))


def _map(fn, jobs, workers: int) -> list:
    if workers <= 1 or len(jobs) < 64:
        return [fn(j) for j in jobs]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, jobs, chunksize=max(1, len(jobs) // (workers * 16))))


def default_workers(cap: int = 8) -> int:
    """At most 8 workers, 4 when the one-minute load is above 24 (the machine is shared)."""
    load = os.getloadavg()[0]
    return min(cap, 4) if load > 24 else cap


def build(workers: int, out: Path = OUT_CSV) -> pd.DataFrame:
    started = time.time()
    parts = []
    for name, fn in (("corpus", corpus_rows), ("ensemble", ensemble_rows), ("simulation", simulation_rows)):
        t = time.time()
        part = fn(workers)
        print(f"{name}: {len(part)} rows in {time.time() - t:.0f}s", flush=True)
        parts.append(part)
    frame = pd.concat(parts, ignore_index=True)
    frame["r_label"] = [ratio_label(r) for r in frame["r"]]
    frame["e_g"] = [giant_threshold_excess(r) for r in frame["r"]]
    if BOUND_GAP_CSV.exists():
        gap = pd.read_csv(BOUND_GAP_CSV, usecols=["instance_name", "source_file"])
        keys = set(zip(gap["instance_name"], gap["source_file"]))
        frame["bound_gap"] = [(a, b) in keys for a, b in zip(frame["instance_name"], frame["source_file"])]
    else:
        frame["bound_gap"] = False
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    print(f"{len(frame)} rows -> {out} ({out.stat().st_size / 1e6:.1f} MB) in {time.time() - started:.0f}s", flush=True)
    return frame


def load(path: Path = OUT_CSV) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist; run `python -m learning.excess --stage build` first")
    return pd.read_csv(path, low_memory=False)


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _quantile_row(group: pd.DataFrame) -> dict:
    row = {"count": len(group), "n range": f"{int(group['n'].min())}-{int(group['n'].max())}",
           "m range": f"{int(group['m'].min())}-{int(group['m'].max())}"}
    for q, name in zip(QUANTILES, QUANTILE_NAMES):
        row[f"e {name}"] = float(group["e"].quantile(q))
    for q, name in zip((0.1, 0.5, 0.9), ("q10", "median", "q90")):
        row[f"gamma/n {name}"] = float(group["gamma_n"].quantile(q))
    row["forest share"] = float(group["forest"].mean())
    row["2-core cust share"] = float(group["core2_cust_frac"].mean())
    row["lcc frac"] = float(group["lcc_frac"].mean())
    row["below e_g"] = float((group["e"] < group["e_g"]).mean())
    row["below 1"] = float((group["e"] < 1.0).mean())
    row["in [1, 2)"] = float(((group["e"] >= 1.0) & (group["e"] < 2.0)).mean())
    row["in [2, 2.4]"] = float(((group["e"] >= 2.0) & (group["e"] <= 2.4)).mean())
    row["above 2.4"] = float((group["e"] > 2.4).mean())
    return row


def collection_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per collection (Chu & Stuckey also by class): the quantiles of `e` and
    `gamma / n`, the forest share, the 2-core share, where the mass sits
    against the three lines."""
    corpus = frame[frame["source"] == "corpus"]
    rows = []
    order = ["SCOOP", "Faggioli-Bentivoglio", "Chu & Stuckey", "Harvey", "Simonis", "Shaw", "Wilson", "Miller",
             "Challenge"]
    for coll in order + sorted(set(corpus["collection"]) - set(order)):
        g = corpus[corpus["collection"] == coll]
        if g.empty:
            continue
        rows.append({"collection": coll, **_quantile_row(g)})
        if coll == "Chu & Stuckey":
            def _key(c):
                parts = c.split("-")
                return (int(parts[1]), int(parts[2]), int(parts[3]))
            for cls in sorted(set(g["series"]), key=_key):
                rows.append({"collection": f"  {cls}", **_quantile_row(g[g["series"] == cls])})
    rows.append({"collection": "corpus, all", **_quantile_row(corpus)})
    return pd.DataFrame(rows)


def series_table(frame: pd.DataFrame, source: str = "ensemble") -> pd.DataFrame:
    """Per ensemble series `(generator, r, param, n)` (or per simulation cell):
    count, `e` and `gamma / n` medians and ranges, forest share, 2-core share,
    largest-component fraction, and the series' `e_g(r)`."""
    f = frame[frame["source"] == source]
    rows = []
    for (gen, rl, param, n), g in f.groupby(["generator", "r_label", "param", "n"]):
        rows.append({"generator": gen, "r": rl, "param": param, "n": int(n), "m": int(g["m"].iloc[0]),
                     "count": len(g), "certified": int(g["certified"].sum()),
                     "e median": float(g["e"].median()), "e min": float(g["e"].min()), "e max": float(g["e"].max()),
                     "gamma/n median": float(g["gamma_n"].median()),
                     "forest share": float(g["forest"].mean()),
                     "2-core cust share": float(g["core2_cust_frac"].mean()),
                     "lcc frac": float(g["lcc_frac"].mean()), "lcc cust frac": float(g["lcc_cust_frac"].mean()),
                     "e_g(r)": giant_threshold_excess(float(g["r"].iloc[0]))})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["_r"] = [float(RATIO_LABELS_INV[r]) for r in out["r"]]
    return out.sort_values(["generator", "_r", "n", "param"]).drop(columns="_r").reset_index(drop=True)


RATIO_LABELS_INV = {v: k for k, v in RATIO_LABELS.items()}


def repaired_giant_threshold_excess(generator: str, r: float) -> float:
    """The giant-component threshold of the incidence graph in excess
    coordinates under the generators' actual degree distributions (empty
    customers padded to one pattern, empty patterns to one customer), from the
    configuration-model 2-core fixed point of `learning.cover_excess`; the
    2-core appears continuously at the branching-factor-one point."""
    from learning.cover_excess import core_threshold_col_mean
    c = core_threshold_col_mean(generator, r, 2, 2, repair=True)
    return float(r * (c - 1.0)) if np.isfinite(c) else np.nan


def crossing_table(frame: pd.DataFrame, min_n: int = CHECK_MIN_N, tol: float = CHECK_TOLERANCE) -> pd.DataFrame:
    """The stated check. For every ensemble series `(generator, r, n)` at
    `n >= min_n`, the cells ordered by their median `e`; the `e` at which the
    mean largest-component fraction of `B` crosses one half (linear
    interpolation between the two cells that straddle it), against `e_g(r)`.
    A series whose cells all sit on one side of one half cannot test the
    prediction and says so. `e_g repaired` is the same threshold under the
    generators' padded degree distributions, for information; the verdict is
    against the plan's `e_g(r)`."""
    cells = series_table(frame)
    cells = cells[cells["n"] >= min_n]
    rows = []
    repaired = {}
    for (gen, rl, n), g in cells.groupby(["generator", "r", "n"]):
        g = g.sort_values("e median")
        e, y = g["e median"].to_numpy(), g["lcc frac"].to_numpy()
        e_g = float(g["e_g(r)"].iloc[0])
        r_exact = float(frame.loc[(frame["generator"] == gen) & (frame["r_label"] == rl), "r"].median())
        if (gen, rl) not in repaired:
            repaired[(gen, rl)] = repaired_giant_threshold_excess(gen, r_exact)
        row = {"generator": gen, "r": rl, "n": int(n), "cells": len(g), "e range": f"{e.min():.2f}-{e.max():.2f}",
               "lcc range": f"{y.min():.2f}-{y.max():.2f}", "e_g(r)": e_g, "e_g repaired": repaired[(gen, rl)]}
        above = y >= 0.5
        if above.all():
            row.update({"crossing": np.nan, "delta": np.nan, "verdict": "not observable (all cells above 1/2)"})
        elif not above.any():
            row.update({"crossing": np.nan, "delta": np.nan, "verdict": "not observable (all cells below 1/2)"})
        else:
            idx = np.where(above[:-1] != above[1:])[0]
            i = int(idx[0])
            x0, x1, y0, y1 = e[i], e[i + 1], y[i], y[i + 1]
            cross = x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0) if y1 != y0 else x0
            delta = cross - e_g
            verdict = "within tolerance" if abs(delta) <= tol else "outside tolerance"
            if len(idx) > 1:
                verdict += f" ({len(idx)} crossings)"
            row.update({"crossing": float(cross), "delta": float(delta), "verdict": verdict})
        rows.append(row)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["_r"] = [float(RATIO_LABELS_INV[r]) for r in out["r"]]
    return out.sort_values(["generator", "_r", "n"]).drop(columns="_r").reset_index(drop=True)


def bound_gap_table(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The bound-gap instances of §6 against the rest of the corpus at equal
    `(n, m)`: per cell the medians of `e` and `gamma / n` on both sides and the
    forest share; and the within-cell percentile of each gap instance's `e`
    and `gamma / n` among the non-gap instances of its cell (summary)."""
    corpus = frame[frame["source"] == "corpus"]
    gap = corpus[corpus["bound_gap"]]
    rows, pct_e, pct_g = [], [], []
    for (n, m), g in gap.groupby(["n", "m"]):
        rest = corpus[(corpus["n"] == n) & (corpus["m"] == m) & ~corpus["bound_gap"]]
        rows.append({"n": int(n), "m": int(m), "gap": len(g), "rest": len(rest),
                     "e gap median": float(g["e"].median()),
                     "e rest median": float(rest["e"].median()) if len(rest) else np.nan,
                     "gamma/n gap median": float(g["gamma_n"].median()),
                     "gamma/n rest median": float(rest["gamma_n"].median()) if len(rest) else np.nan,
                     "forest share gap": float(g["forest"].mean()),
                     "forest share rest": float(rest["forest"].mean()) if len(rest) else np.nan,
                     "collections": ", ".join(sorted(set(g["collection"])))})
        if len(rest) >= 5:
            re_, rg = rest["e"].to_numpy(), rest["gamma_n"].to_numpy()
            for v in g["e"]:
                pct_e.append(float((re_ < v).mean() + 0.5 * (re_ == v).mean()))
            for v in g["gamma_n"]:
                pct_g.append(float((rg < v).mean() + 0.5 * (rg == v).mean()))
    cells = pd.DataFrame(rows).sort_values(["n", "m"]).reset_index(drop=True) if rows else pd.DataFrame()
    summary = pd.DataFrame([
        {"quantity": "e", "gap instances with >= 5 peers": len(pct_e),
         "percentile q25": float(np.quantile(pct_e, 0.25)) if pct_e else np.nan,
         "percentile median": float(np.median(pct_e)) if pct_e else np.nan,
         "percentile q75": float(np.quantile(pct_e, 0.75)) if pct_e else np.nan,
         "share below cell median": float(np.mean(np.array(pct_e) < 0.5)) if pct_e else np.nan},
        {"quantity": "gamma/n", "gap instances with >= 5 peers": len(pct_g),
         "percentile q25": float(np.quantile(pct_g, 0.25)) if pct_g else np.nan,
         "percentile median": float(np.median(pct_g)) if pct_g else np.nan,
         "percentile q75": float(np.quantile(pct_g, 0.75)) if pct_g else np.nan,
         "share below cell median": float(np.mean(np.array(pct_g) < 0.5)) if pct_g else np.nan},
    ])
    return cells, summary


def forest_regime_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Is `e < e_g(r)` the forest regime? Per generator and size band of the
    ensembles: the count and forest share of the instances below `e_g(r)`, in
    `[e_g(r), 1)` and at or above 1. At finite `n` a random graph below its
    giant threshold still carries O(1) cycles, so a forest share below one
    there is expected; what the table shows is how sharply the share falls
    across the line."""
    ens = frame[frame["source"] == "ensemble"].copy()
    bands = pd.cut(ens["n"], [0, 25, 40, 75, 100], labels=["10-25", "30-40", "50-75", "100"])
    ens["band"] = bands
    rows = []
    for (gen, band), g in ens.groupby(["generator", "band"], observed=True):
        below = g[g["e"] < g["e_g"]]
        mid = g[(g["e"] >= g["e_g"]) & (g["e"] < 1.0)]
        above = g[g["e"] >= 1.0]
        rows.append({"generator": gen, "n": band, "count e < e_g": len(below),
                     "forest share e < e_g": float(below["forest"].mean()) if len(below) else np.nan,
                     "median gamma e < e_g": float(below["gamma"].median()) if len(below) else np.nan,
                     "count e_g <= e < 1": len(mid),
                     "forest share e_g <= e < 1": float(mid["forest"].mean()) if len(mid) else np.nan,
                     "median gamma e_g <= e < 1": float(mid["gamma"].median()) if len(mid) else np.nan,
                     "count e >= 1": len(above),
                     "forest share e >= 1": float(above["forest"].mean()) if len(above) else np.nan})
    return pd.DataFrame(rows)


def lines_table(frame: pd.DataFrame) -> pd.DataFrame:
    """How many instances of each source sit below `e_g(r)`, in `[e_g, 1)`, in
    `[1, 2)`, in `[2, 2.4]` and above 2.4, and how many are forests."""
    rows = []
    for source, g in frame.groupby("source"):
        rows.append({"source": source, "count": len(g),
                     "forest": int(g["forest"].sum()),
                     "e < e_g(r)": int((g["e"] < g["e_g"]).sum()),
                     "e_g(r) <= e < 1": int(((g["e"] >= g["e_g"]) & (g["e"] < 1)).sum()),
                     "1 <= e < 2": int(((g["e"] >= 1) & (g["e"] < 2)).sum()),
                     "2 <= e <= 2.4": int(((g["e"] >= 2) & (g["e"] <= 2.4)).sum()),
                     "e > 2.4": int((g["e"] > 2.4).sum()),
                     "forests with e >= e_g(r)": int((g["forest"] & (g["e"] >= g["e_g"])).sum()),
                     "non-forests with e < e_g(r)": int((~g["forest"] & (g["e"] < g["e_g"])).sum())})
    return pd.DataFrame(rows)


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt) if len(frame) else "_(empty)_"


def tables(frame: pd.DataFrame) -> str:
    coll = collection_table(frame)
    series = series_table(frame)
    sims = series_table(frame, "simulation")
    cross = crossing_table(frame)
    gap_cells, gap_summary = bound_gap_table(frame)
    identity = np.abs(frame["e"] - frame["r"] * (frame["c"] - 1)).max()
    cyc = np.abs(frame["gamma_n"] - (frame["e"] - 1 + frame["kappa"] / frame["n"])).max()
    parts = [
        f"Rows: {len(frame)} ({', '.join(f'{s} {len(g)}' for s, g in frame.groupby('source'))}); "
        f"max |e − r(c − 1)| = {identity:.1e}; max |γ/n − (e − 1 + κ/n)| = {cyc:.1e}.",
        "\n### The three lines, by source\n", _md(lines_table(frame)),
        "\n### Is e < e_g(r) the forest regime? The ensembles by generator and size band\n",
        _md(forest_regime_table(frame)),
        "\n### Per collection\n", _md(coll),
        "\n### The stated check: where the largest component of B crosses one half, against e_g(r)\n", _md(cross),
        "\n### Per ensemble series (generator, r, param, n)\n", _md(series),
        "\n### Per simulation cell\n", _md(sims),
        "\n### The 338 bound-gap instances against the rest of the corpus at equal (n, m)\n", _md(gap_summary),
        "", _md(gap_cells),
    ]
    return "\n".join(parts)


# ----------------------------------------------------------------------------
# the figure
# ----------------------------------------------------------------------------

COLOURS = {"fixed": "#2a78d6", "bernoulli": "#eb6834"}


def figure(frame: pd.DataFrame, out: Path = FIGURE, min_n: int = CHECK_MIN_N) -> Path:
    """Small multiples, one per product ratio: the mean largest-component
    fraction of `B` per ensemble cell against the cell's median `e`, one line
    per `(generator, n)` at `n >= min_n`, with `e_g(r)` as a dashed vertical and
    one half as a dotted horizontal. PNG for the report."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cells = series_table(frame)
    cells = cells[cells["n"] >= min_n]
    ratios = sorted(set(cells["r"]), key=lambda r: RATIO_LABELS_INV[r])
    ncol = 4
    nrow = int(np.ceil(len(ratios) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.2 * ncol, 2.7 * nrow), sharey=True, squeeze=False)
    for ax in axes.ravel()[len(ratios):]:
        ax.axis("off")
    for ax, rl in zip(axes.ravel(), ratios):
        g = cells[cells["r"] == rl]
        e_g = float(g["e_g(r)"].iloc[0])
        ax.axhline(0.5, color="#9a9994", lw=1, ls=":", zorder=1)
        ax.axvline(e_g, color="#9a9994", lw=1, ls="--", zorder=1)
        ax.axvline(1.0, color="#d8d7d2", lw=1, zorder=0)
        for (gen, n), s in g.groupby(["generator", "n"]):
            s = s.sort_values("e median")
            sizes = sorted(set(g[g["generator"] == gen]["n"]))
            alpha = 0.35 + 0.65 * (sizes.index(n) / max(1, len(sizes) - 1)) if len(sizes) > 1 else 1.0
            ax.plot(s["e median"], s["lcc frac"], color=COLOURS[gen], lw=2, alpha=alpha, marker="o", ms=4,
                    label=gen if n == sizes[-1] else None, zorder=2)
        ax.text(e_g, 0.03, f" e_g={e_g:.2f}", color="#52514e", fontsize=8, ha="left", va="bottom")
        ax.set_title(f"r = {rl}", fontsize=10, color="#0b0b0b", loc="left")
        ax.set_xlim(0, max(1.2, min(4.0, float(g["e max"].max()) + 0.1)))
        ax.set_ylim(0, 1.02)
        ax.grid(False)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#c3c2b7")
        ax.tick_params(colors="#52514e", labelsize=8)
    for ax in axes[-1]:
        ax.set_xlabel("excess e = (n_ones − m) / n", fontsize=9, color="#52514e")
    fig.supylabel("largest component of B, fraction of its n + m vertices (cell means)", fontsize=9,
                  color="#52514e")
    seen: dict[str, object] = {}
    for ax in axes.ravel():
        for h, lab in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(lab, h)
    labels = [f"{lab} generator (paler = smaller n; dashed: e_g(r); dotted: one half)" for lab in seen]
    fig.legend(list(seen.values()), labels, loc="upper right", frameon=False, fontsize=9, ncol=1)
    fig.tight_layout(rect=(0.02, 0, 1, 0.93))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)
    return out


# ----------------------------------------------------------------------------
# item 02: the two-key rule on every instance, and opt / n against the excess
# ----------------------------------------------------------------------------

SLOPE_MIN_N = 30
PAIR_TOLERANCE = 0.05
CONSTANT_E_TOLERANCE = 0.1   # relative: a series whose cell-mean e moves by more than this fraction of its mean across n is not a constant-e series
E_BINS = [0.0, 0.62, 1.0, 1.5, 2.0, 2.4, 3.0, 4.0, 6.0, 10.0, np.inf]
E_BIN_LABELS = ["[0, 0.62)", "[0.62, 1)", "[1, 1.5)", "[1.5, 2)", "[2, 2.4)", "[2.4, 3)", "[3, 4)", "[4, 6)",
                "[6, 10)", ">= 10"]
_CS_NAME = re.compile(r"^Random-(\d+)-(\d+)-(\d+)-\d+_\d+$")


def sizes_text(matrix: np.ndarray) -> str:
    """The pattern-size histogram of a matrix as `size:count;...` (column sums)."""
    sizes = np.asarray(matrix).sum(axis=0)
    values, counts = np.unique(sizes, return_counts=True)
    return ";".join(f"{int(v)}:{int(c)}" for v, c in zip(values, counts))


def sizes_from_text(text: str) -> dict[int, int]:
    out: dict[int, int] = {}
    for part in str(text).split(";"):
        if part:
            v, c = part.split(":")
            out[int(v)] = out.get(int(v), 0) + int(c)
    return out


def _rule_on(instance: MOSPInstance) -> tuple[int, float]:
    from satisfiability.heuristics import two_key_rule
    t = time.perf_counter()
    value, _ordering = two_key_rule(instance)
    return int(value), time.perf_counter() - t


def _rule_ensemble_job(args) -> dict:
    frame_name, cell_text, index, name, n_ones_recorded, optimum, certified = args
    cell = Cell.parse(cell_text)
    inst = generate(cell, index)
    if inst.name != name or int(inst.matrix.sum()) != n_ones_recorded:
        raise AssertionError(f"{name}: regeneration does not match the record")
    value, seconds = _rule_on(inst)
    return {"source": "ensemble", "frame": frame_name, "instance_name": name, "cell": cell.id,
            "generator": cell.generator, "param": cell.param, "n": cell.n, "m": cell.m,
            "n_ones": n_ones_recorded, "optimum": optimum if certified else np.nan, "certified": bool(certified),
            "rule": value, "rule_seconds": seconds, "sizes": sizes_text(inst.matrix)}


def _rule_corpus_job(args) -> dict:
    source_file, name, matrix = args
    inst = MOSPInstance.from_matrix(matrix, name=name)
    value, seconds = _rule_on(inst)
    optimum, provenance = solution_record(inst)
    certified = provenance.startswith("certified")
    collection, cls = collection_of(source_file, name)
    n, m = matrix.shape
    match = _CS_NAME.match(name)
    return {"source": "corpus", "frame": "corpus", "instance_name": name, "cell": cls,
            "generator": "chu_stuckey" if match else collection, "param": int(match.group(3)) if match else np.nan,
            "n": n, "m": m, "n_ones": int(np.asarray(matrix).sum()), "optimum": optimum if certified else np.nan,
            "certified": certified, "rule": value, "rule_seconds": seconds, "sizes": sizes_text(matrix)}


def rule_rows(workers: int, out: Path = RULE_CSV, ensemble_dir: Path = ENSEMBLE_DIR) -> pd.DataFrame:
    """The two-key closing rule (`satisfiability.heuristics.two_key_rule`,
    valued by simulation) on every ensemble instance (regenerated from its
    seed) and every corpus instance, with the certified optimum beside it and
    the pattern-size histogram the first moment needs. A scoring run: nothing is
    solved, nothing is written to the compute ledger or to `solutions/`."""
    from learning.dataset import enumerate_instances
    started = time.time()
    ens = _map(_rule_ensemble_job, ensemble_jobs(ensemble_dir), workers)
    corpus = _map(_rule_corpus_job, [(str(path), inst.name, inst.matrix) for path, inst in enumerate_instances()],
                  workers)
    frame = pd.DataFrame(ens + corpus)
    frame["e"] = excess(frame["n"], frame["m"], frame["n_ones"])
    frame["r"] = frame["m"] / frame["n"]
    frame["r_label"] = [ratio_label(r) for r in frame["r"]]
    frame["rule_gap"] = frame["rule"] - frame["optimum"]
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    print(f"rule: {len(frame)} rows ({len(ens)} ensemble, {len(corpus)} corpus), "
          f"{frame['rule_seconds'].sum():.1f} s of rule time, {time.time() - started:.0f} s wall -> {out}", flush=True)
    return frame


def load_rule(path: Path = RULE_CSV) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist; run `python -m learning.excess --stage rule` first")
    return pd.read_csv(path, low_memory=False)


def _ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    """(a, b, se_a, se_b) of `y = a + b x` by least squares; nan where not estimable."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0:
        return np.nan, np.nan, np.nan, np.nan
    xm = x.mean()
    sxx = float(((x - xm) ** 2).sum())
    b = float(((x - xm) * (y - y.mean())).sum() / sxx)
    a = float(y.mean() - b * xm)
    resid = y - a - b * x
    s2 = float((resid ** 2).sum() / (len(x) - 2))
    return a, b, float(np.sqrt(s2 * (1 / len(x) + xm ** 2 / sxx))), float(np.sqrt(s2 / sxx))


def series_key(frame: pd.DataFrame) -> pd.Series:
    """`(generator, r_label, param)`: the ensemble series across `n`, and for
    the corpus the Chu & Stuckey class across `n` (`chu_stuckey`, `r`, `d`)."""
    return frame["generator"].astype(str) + "|" + frame["r_label"].astype(str) + "|" + frame["param"].map(
        lambda p: f"{p:g}")


def series_slopes(rule: pd.DataFrame, min_n: int = SLOPE_MIN_N, min_sizes: int = 3) -> pd.DataFrame:
    """Per series with at least `min_sizes` distinct `n >= min_n`: the fit
    `opt = a + b n` on the certified instances (one point per instance, so the
    standard error carries the within-cell spread), the same fit for the
    rule's value, the realised excess (mean over the fitted instances; never
    the nominal `r (d - 1)`), `beta*` at the series' realised size histogram
    and `mu = m / n`, and the rule's exactness and gap."""
    from learning.first_moment import beta_star
    f = rule[rule["certified"] & rule["optimum"].notna() & (rule["n"] >= min_n)].copy()
    f = f[f["generator"].isin(["fixed", "bernoulli", "chu_stuckey"])]
    f["key"] = series_key(f)
    rows = []
    for key, g in f.groupby("key"):
        sizes = sorted(set(g["n"]))
        if len(sizes) < min_sizes:
            continue
        gen, rl, param = key.split("|")
        a, b, se_a, se_b = _ols(g["n"], g["optimum"])
        ar, br, _, se_br = _ols(g["n"], g["rule"])
        hist: dict[int, int] = {}
        for text in g["sizes"]:
            for v, c in sizes_from_text(text).items():
                hist[v] = hist.get(v, 0) + c
        mu = float(g["r"].mean())
        top = g[g["n"] == sizes[-1]]
        cell_e = g.groupby("n")["e"].mean()
        rows.append({
            "generator": gen, "r": rl, "param": float(param), "key": key,
            "e": float(g["e"].mean()), "e sd": float(g["e"].std()), "mu": mu,
            "e range over n": float(cell_e.max() - cell_e.min()),
            "constant e": bool(cell_e.max() - cell_e.min() <= CONSTANT_E_TOLERANCE * cell_e.mean()),
            "mean size": float(sum(v * c for v, c in hist.items()) / sum(hist.values())),
            "n sizes": ", ".join(str(int(x)) for x in sizes), "instances": len(g),
            "a": a, "b": b, "se b": se_b, "b rule": br, "se b rule": se_br,
            "opt/n at max n": float((top["optimum"] / top["n"]).mean()),
            "rule/n at max n": float((top["rule"] / top["n"]).mean()),
            "beta* (sizes)": beta_star(mu, hist),
            "beta* (fixed d)": beta_star(mu, [int(round(float(param)))]) if gen in ("fixed", "chu_stuckey") else np.nan,
            "rule exact": float((g["rule_gap"] == 0).mean()), "rule gap mean": float(g["rule_gap"].mean()),
            "rule gap max": int(g["rule_gap"].max()), "rule gap/n mean": float((g["rule_gap"] / g["n"]).mean()),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    gen_order = {"fixed": 0, "bernoulli": 1, "chu_stuckey": 2}
    out["_g"] = out["generator"].map(gen_order)
    out["_r"] = [float(RATIO_LABELS_INV[r]) for r in out["r"]]
    return out.sort_values(["_g", "_r", "param"]).drop(columns=["_g", "_r"]).reset_index(drop=True)


def matched_pairs(slopes: pd.DataFrame, tol: float = PAIR_TOLERANCE) -> pd.DataFrame:
    """Every pair of series whose realised `e` agree within `tol` and whose
    `(generator, d or p, mu)` differ: the two slopes, their difference, twice
    the larger standard error, and whether they differ by more than that. The
    kill criterion of item 02 counts the pairs that differ."""
    rows = []
    s = slopes.reset_index(drop=True)
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            x, y = s.iloc[i], s.iloc[j]
            if abs(x["e"] - y["e"]) > tol:
                continue
            if (x["generator"], x["param"], x["r"]) == (y["generator"], y["param"], y["r"]):
                continue
            two_se = 2 * max(x["se b"], y["se b"])
            diff = x["b"] - y["b"]
            rows.append({"series 1": f"{x['generator']} r={x['r']} {x['param']:g}",
                         "series 2": f"{y['generator']} r={y['r']} {y['param']:g}",
                         "e 1": x["e"], "e 2": y["e"], "b 1": x["b"], "b 2": y["b"], "diff": diff,
                         "2 max se": two_se, "|diff| / 2 max se": abs(diff) / two_se if two_se > 0 else np.inf,
                         "differ": bool(abs(diff) > two_se),
                         "both constant e": bool(x["constant e"] and y["constant e"]),
                         "beta* 1": x["beta* (sizes)"], "beta* 2": y["beta* (sizes)"],
                         "rule/n 1": x["rule/n at max n"], "rule/n 2": y["rule/n at max n"]})
    out = pd.DataFrame(rows)
    return out.sort_values(["e 1", "series 1"]).reset_index(drop=True) if len(out) else out


def rule_by_bin(rule: pd.DataFrame) -> pd.DataFrame:
    """The rule against the certified optimum per excess bin and source:
    count, exact share, mean and maximum gap, mean gap / n, and the rule's
    value as a fraction of `n` beside the optimum's."""
    f = rule[rule["certified"] & rule["optimum"].notna()].copy()
    f["bin"] = pd.cut(f["e"], E_BINS, labels=E_BIN_LABELS, right=False)
    rows = []
    for (src, b), g in f.groupby(["source", "bin"], observed=True):
        rows.append({"source": src, "e bin": b, "count": len(g), "n range": f"{int(g['n'].min())}-{int(g['n'].max())}",
                     "exact": float((g["rule_gap"] == 0).mean()), "gap mean": float(g["rule_gap"].mean()),
                     "gap q90": float(g["rule_gap"].quantile(0.9)), "gap max": int(g["rule_gap"].max()),
                     "gap/n mean": float((g["rule_gap"] / g["n"]).mean()),
                     "opt/n mean": float((g["optimum"] / g["n"]).mean()),
                     "rule/n mean": float((g["rule"] / g["n"]).mean())})
    return pd.DataFrame(rows)


def rule_worst(rule: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    f = rule[rule["certified"] & rule["optimum"].notna()]
    cols = ["source", "instance_name", "n", "m", "e", "optimum", "rule", "rule_gap"]
    return f.sort_values(["rule_gap", "n"], ascending=[False, True]).head(top)[cols].reset_index(drop=True)


NAMED_GROUPS = {
    "e = 1": [("fixed", "n", 2.0), ("fixed", "n/2", 3.0), ("fixed", "n/4", 4.0)],
    "e = 2": [("fixed", "n", 3.0), ("fixed", "n/2", 5.0), ("fixed", "2n", 2.0), ("fixed", "n/4", 9.0)],
    "e = 3": [("fixed", "n", 4.0), ("fixed", "n/2", 7.0), ("fixed", "n/4", 12.0)],
    "e = 4": [("fixed", "n", 5.0), ("fixed", "n/2", 9.0), ("fixed", "2n", 3.0)],
    "e = 6": [("fixed", "n", 7.0), ("fixed", "2n", 4.0)],
    "e = 8": [("fixed", "n", 9.0), ("fixed", "2n", 5.0)],
}


def named_groups(slopes: pd.DataFrame) -> pd.DataFrame:
    """The item's e-matched groups of the fixed generator (`(d, mu)` at equal
    nominal excess), with the realised `e`, `b`, `beta*`, `b - beta*` and the
    rule's `width / n`; a row is marked where its realised `e` is more than
    `PAIR_TOLERANCE` from the group's first member."""
    rows = []
    for label, members in NAMED_GROUPS.items():
        ref = None
        for gen, rl, param in members:
            hit = slopes[(slopes["generator"] == gen) & (slopes["r"] == rl) & (slopes["param"] == param)]
            if hit.empty:
                continue
            x = hit.iloc[0]
            ref = x["e"] if ref is None else ref
            rows.append({"group": label, "d": int(param), "mu": x["mu"], "e": x["e"],
                         "within tolerance": bool(abs(x["e"] - ref) <= PAIR_TOLERANCE),
                         "b": x["b"], "se b": x["se b"], "beta*": x["beta* (sizes)"], "b - beta*": x["b"] - x["beta* (sizes)"],
                         "rule/n at max n": x["rule/n at max n"], "rule/n - b": x["rule/n at max n"] - x["b"]})
    return pd.DataFrame(rows)


def beta_residuals(slopes: pd.DataFrame) -> pd.DataFrame:
    """Per constant-e series: `b - beta*`, and for each pair of constant-e
    series with `beta*` within 0.02 of each other, whether the slopes differ by
    more than twice the larger standard error -- the same test as the
    e-matched pairs, with `beta*` as the matching coordinate."""
    s = slopes[slopes["constant e"]].reset_index(drop=True)
    rows = []
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            x, y = s.iloc[i], s.iloc[j]
            if abs(x["beta* (sizes)"] - y["beta* (sizes)"]) > 0.02:
                continue
            if (x["generator"], x["param"], x["r"]) == (y["generator"], y["param"], y["r"]):
                continue
            two_se = 2 * max(x["se b"], y["se b"])
            rows.append({"series 1": f"{x['generator']} r={x['r']} {x['param']:g}",
                         "series 2": f"{y['generator']} r={y['r']} {y['param']:g}",
                         "beta* 1": x["beta* (sizes)"], "beta* 2": y["beta* (sizes)"], "e 1": x["e"], "e 2": y["e"],
                         "b 1": x["b"], "b 2": y["b"], "diff": x["b"] - y["b"], "2 max se": two_se,
                         "differ": bool(abs(x["b"] - y["b"]) > two_se)})
    out = pd.DataFrame(rows)
    return out.sort_values("beta* 1").reset_index(drop=True) if len(out) else out


def slopes_tables(rule: pd.DataFrame) -> str:
    slopes = series_slopes(rule)
    pairs = matched_pairs(slopes)
    bins = rule_by_bin(rule)
    worst = rule_worst(rule)
    scored = rule[rule["certified"] & rule["optimum"].notna()]
    const = pairs[pairs["both constant e"]] if len(pairs) else pairs
    n_differ = int(pairs["differ"].sum()) if len(pairs) else 0
    n_differ_c = int(const["differ"].sum()) if len(const) else 0
    dead = len(const) and n_differ_c * 2 >= len(const)
    verdict = ("the one-parameter hypothesis is DEAD (slopes differ on at least half of the constant-e matched pairs)"
               if dead else
               "the one-parameter hypothesis SURVIVES this test (slopes differ on fewer than half of the pairs)")
    cols = ["generator", "r", "param", "e", "e range over n", "mu", "mean size", "n sizes", "instances", "a", "b",
            "se b", "b rule", "opt/n at max n", "rule/n at max n", "beta* (sizes)", "beta* (fixed d)", "rule exact",
            "rule gap mean", "rule gap max"]
    parts = [
        f"Scored: {len(scored)} certified instances ({', '.join(f'{s} {len(g)}' for s, g in scored.groupby('source'))}), "
        f"rule time {rule['rule_seconds'].sum():.1f} s in all; series with >= 3 sizes at n >= {SLOPE_MIN_N}: {len(slopes)} "
        f"({int(slopes['constant e'].sum())} with e constant in n to within {CONSTANT_E_TOLERANCE:.0%} of its mean; the Bernoulli series at "
        f"fixed p have e growing with n and are not constant-e series). "
        f"e-matched pairs (|Δe| <= {PAIR_TOLERANCE}, different (generator, d or p, mu)): {len(pairs)}, of which {n_differ} "
        f"differ by more than twice the larger standard error; among the {len(const)} pairs of two constant-e series, "
        f"{n_differ_c} differ. Verdict: {verdict}.",
        "\n### Per series: opt = a + b n on n >= 30, the rule, beta*\n", _md(slopes[cols]),
        "\n### The e-matched groups named by the item (fixed generator)\n", _md(named_groups(slopes)),
        "\n### The e-matched pairs\n", _md(pairs),
        "\n### Is b a function of beta* alone? Residuals of b about beta* on the constant-e series\n",
        _md(beta_residuals(slopes)),
        "\n### The rule against the optimum, per excess bin\n", _md(bins),
        "\n### The rule's worst cases\n", _md(worst),
    ]
    return "\n".join(parts)


QUANTITY_COLOURS = {"b (certified slope)": "#2a78d6", "rule / n at largest n": "#eb6834", "beta* (first moment)": "#1baf7a"}


def figure_opt(rule: pd.DataFrame, out: Path = FIGURE_OPT) -> Path:
    """Small multiples, one per product ratio `r`, for the constant-e series
    (the fixed generator and the Chu & Stuckey classes; a Bernoulli series at
    fixed `p` has `e` growing with `n` and is left out): against the series'
    realised `e`, the certified slope `b` with its 2-se bar, the rule's
    `width / n` at the largest `n`, and `beta*` at the realised sizes; one
    marker per series, circles the fixed generator, squares the Chu & Stuckey
    classes. Three quantities, three categorical slots; PNG for the report."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    slopes = series_slopes(rule)
    slopes = slopes[slopes["constant e"]]
    ratios = sorted(set(slopes["r"]), key=lambda r: RATIO_LABELS_INV[r])
    fig, axes = plt.subplots(1, len(ratios), figsize=(3.4 * len(ratios), 3.4), sharey=True, squeeze=False)
    markers = {"fixed": "o", "chu_stuckey": "s", "bernoulli": "D"}
    for ax, rl in zip(axes.ravel(), ratios):
        g = slopes[slopes["r"] == rl]
        ax.axvline(1.0, color="#d8d7d2", lw=1, zorder=0)
        ax.axvspan(2.0, 2.4, color="#f1f0eb", zorder=0)
        for gen, s in g.groupby("generator"):
            mk = markers[gen]
            ax.errorbar(s["e"], s["b"], yerr=2 * s["se b"], fmt="none", ecolor=QUANTITY_COLOURS["b (certified slope)"],
                        elinewidth=1, zorder=2)
            for key, col in QUANTITY_COLOURS.items():
                y = {"b (certified slope)": "b", "rule / n at largest n": "rule/n at max n",
                     "beta* (first moment)": "beta* (sizes)"}[key]
                ax.plot(s["e"], s[y], ls="none", marker=mk, ms=6, color=col, zorder=3)
        ax.set_title(f"r = m / n = {rl}", fontsize=10, color="#0b0b0b", loc="left")
        ax.set_xlim(0, float(g["e"].max()) * 1.08)
        ax.set_ylim(-0.02, 1.0)
        ax.grid(False)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#c3c2b7")
        ax.tick_params(colors="#52514e", labelsize=8)
        ax.set_xlabel("realised excess e", fontsize=9, color="#52514e")
    axes[0, 0].set_ylabel("per customer", fontsize=9, color="#52514e")
    handles = [Line2D([], [], ls="none", marker="o", color=c, ms=6, label=k) for k, c in QUANTITY_COLOURS.items()]
    handles += [Line2D([], [], ls="none", marker="o", color="#52514e", ms=6, label="fixed generator, n = 30–100"),
                Line2D([], [], ls="none", marker="s", color="#52514e", ms=6, label="Chu & Stuckey classes, n = 30–125")]
    fig.legend(handles=handles, loc="upper right", frameon=False, fontsize=8, ncol=2)
    fig.text(0.01, 0.95, "grey line: e = 1, where the first moment turns on; band: e = 2–2.4, the hardness ridge; "
             "bars: ± 2 se on b", fontsize=8, color="#52514e")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)
    return out


# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("build", "tables", "figure", "all", "rule", "slopes", "figure-opt",
                                        "constructions", "constructions-tables", "figure-constructions",
                                        "forest_check", "ridge", "ridge-lattice", "ridge-tables", "figure-ridge"),
                    default="all")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--out", type=Path, default=OUT_CSV)
    ap.add_argument("--per-cell", type=int, default=None, help="ridge-lattice: instances per cell (default all)")
    args = ap.parse_args()
    workers = args.workers if args.workers is not None else default_workers()
    if args.stage == "rule":
        rule_rows(workers)
        return
    if args.stage == "slopes":
        print(slopes_tables(load_rule()))
        return
    if args.stage == "figure-opt":
        print(f"figure -> {figure_opt(load_rule())}")
        return
    if args.stage == "forest_check":
        from learning import forest_theorems as ft
        print(ft.run(workers))
        return
    if args.stage in ("ridge", "ridge-lattice", "ridge-tables", "figure-ridge"):
        from learning import excess_ridge as er
        if args.stage == "ridge":
            inst, cells, peaks = er.run_h1()
            print(er.h1_tables(inst, cells, peaks))
        elif args.stage == "ridge-lattice":
            er.run_lattice(workers, args.per_cell)
        elif args.stage == "ridge-tables":
            print(er.tables())
        else:
            _inst, cells, peaks = er.load_h1()
            print(f"figure -> {er.figure(peaks, cells)}")
        return
    if args.stage.endswith("constructions") or args.stage == "constructions-tables":
        from learning import excess_constructions as ec
        if args.stage == "constructions":
            ec.run(ec.grid_jobs(), workers)
        elif args.stage == "constructions-tables":
            print(ec.tables(ec.load()))
        else:
            print(f"figure -> {ec.figure(ec.load())}")
        return
    if args.stage in ("build", "all"):
        frame = build(workers, args.out)
    else:
        frame = load(args.out)
    if args.stage in ("tables", "all"):
        print(tables(frame))
    if args.stage in ("figure", "all"):
        print(f"figure -> {figure(frame)}")


if __name__ == "__main__":
    main()
