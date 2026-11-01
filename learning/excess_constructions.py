"""`beta+` by simulation: the width of explicit constructions at large `n` (loop0010 item 05).

For the random cover model at fixed `(d, mu)` -- `m = mu n` patterns of `d`
customers each -- what width per customer do explicit layouts reach as `n`
grows? Nothing here is solved or certified; every number is the value of one
construction on one fresh instance, and only two of the four constructions are
proved upper bounds on the pathwidth:

- **the two-key closing rule** (`satisfiability.heuristics.two_key_closing_order`,
  the default upper-bound seed since 2026-09-28): its product order, valued by
  simulation; `rule - 1` is the width of a layout, so an upper bound on the
  pathwidth *of that instance* -- measured, not analysed;
- **the BFS-layer layout**: the layers `L_0, L_1, ...` of the MOSP graph from a
  random root, listed layer by layer (a second root for every further
  component), its vertex separation computed exactly from the adjacency, and
  the layer bound `max_i (|L_i| + |L_{i+1}|) - 1` that the layer lemma gives;
- **`n - alpha_greedy`**: the greedy independent set by minimum remaining degree;
  `pw <= n - alpha` is `pathwidth_le_card_sub_indepNum` (`IndependenceBound.lean`)
  and `alpha >= alpha_greedy`, so `n - alpha_greedy` is a proved upper bound;
- **the edge-count bound** `|E| / 5.769` of Kneis, Moelle, Richter & Rossmanith
  (2009), cited as `reports/random_graph_pathwidth_survey.md` section 1.4 cites it
  (`pw <= m / 5.769 + O(log n)`, abstract only), with the `O(log n)` term
  omitted as the survey's table omits it -- so a proved bound up to that term.

Two generators, both fresh draws: the fixed-size generator
`benchmarks.generator.generate_structured_instance` (exactly `d` customers per
pattern, empty customers padded to one pattern; the generator of the certified
ensemble series item 02 fitted), and the fitted Chu & Stuckey generator of
`reports/scratch/clique_cover_moment/gen_candidates.py` (`bern_padC1_padP2_conn`:
Bernoulli(d / n) entries, customers padded to >= 1 pattern, patterns to >= 2
customers, disconnected instances discarded). The rejection of the fitted
generator fails at large `n` and small `d` -- the expected number of isolated
pattern pairs grows linearly in `n` at fixed density -- so the draw cap is small
and a cell whose first draw hits it is recorded as not accepted, never forced.

Per construction and cell the fit `width / n = beta+ + a / n` by least squares
over every instance (so the standard error carries the within-cell spread),
with item 02's certified slope `b` at `n <= 100` and `beta*(d, mu)` beside it.
Kill criterion of the item: a cell's extrapolation is not trusted -- and later
items may not quote it -- where the rule's `width / n` at the largest `n` and
`b` differ by more than 0.03.

Width is in pathwidth units throughout (`rule - 1`, vertex separation,
`n - alpha`, `|E| / 5.769`); `optimum = pathwidth + 1`, so per-customer values
agree with `opt / n` to `1 / n`.

Usage:
    python -m learning.excess --stage constructions           # run the grid -> learning/data/excess_constructions.csv
    python -m learning.excess --stage constructions-tables    # the tables, from the csv
    python -m learning.excess --stage figure-constructions    # reports/figures/excess_beta_plus.png
    python -m learning.excess_constructions --n 1000 --reps 1 --d 10 --mu 2   # one cell, for timing
    python -m pytest tests/test_excess_constructions.py -q
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from mosp.instance import MOSPInstance

DATA_DIR = Path("learning/data")
OUT_CSV = DATA_DIR / "excess_constructions.csv"
FIGURE = Path("reports/figures/excess_beta_plus.png")
SIM_DIR = Path("reports/scratch/clique_cover_moment")
GRID_D = (2, 3, 4, 6, 8, 10)
GRID_MU = (0.5, 1.0, 2.0)
GRID_N = (100, 200, 500, 1000, 2000, 5000)
REPS = 10
EDGE_CONSTANT = 5.769          # Kneis et al. (2009): pw <= |E| / 5.769 + O(log n)
KILL_TOLERANCE = 0.03
MU_LABELS = {0.5: "n/2", 1.0: "n", 2.0: "2n"}
CONSTRUCTIONS = ("rule", "bfs_vs", "bfs_layer_bound", "n_minus_alpha", "edge_bound")
CONSTRUCTION_NAMES = {"rule": "two-key rule (pw = stacks - 1)", "bfs_vs": "BFS layers: vertex separation",
                      "bfs_layer_bound": "BFS layers: max (|L_i| + |L_{i+1}|) - 1",
                      "n_minus_alpha": "n - alpha (greedy, min degree)", "edge_bound": "|E| / 5.769"}
PROVED = {"rule": "layout of this instance (measured)", "bfs_vs": "layout of this instance (measured)",
          "bfs_layer_bound": "layer lemma (deterministic)", "n_minus_alpha": "IndependenceBound.lean + alpha >= greedy",
          "edge_bound": "Kneis et al. 2009, O(log n) term omitted"}
# the fitted generator's draw cap per attempt: the acceptance probability falls like exp(-c n) at fixed d
FITTED_CAP = {100: 2000, 200: 1000, 500: 500, 1000: 200, 2000: 100, 5000: 20}
BASE_SEED = 5_050_000


# ----------------------------------------------------------------------------
# the MOSP graph of a matrix, as a sparse adjacency
# ----------------------------------------------------------------------------


def mosp_adjacency(matrix: np.ndarray) -> csr_matrix:
    """The MOSP graph (customers adjacent iff they share a pattern) as a
    symmetric 0/1 CSR matrix without the diagonal."""
    a = csr_matrix(np.asarray(matrix, dtype=np.int8) != 0, dtype=np.int32)
    g = (a @ a.T).tocsr()
    g.setdiag(0)
    g.eliminate_zeros()
    g.data[:] = 1
    return g.astype(np.int8)


def edge_count(adj: csr_matrix) -> int:
    return int(adj.nnz // 2)


# ----------------------------------------------------------------------------
# the value of a layout
# ----------------------------------------------------------------------------


def vertex_separation(adj: csr_matrix, order: np.ndarray) -> int:
    """The vertex separation of the linear layout `order` (a permutation of the
    vertices): `max_i |{v : pos(v) <= i < max pos(N(v))}|`, by a sweep. Exact."""
    n = adj.shape[0]
    order = np.asarray(order)
    pos = np.empty(n, dtype=np.int64)
    pos[order] = np.arange(n)
    indptr, indices = adj.indptr, adj.indices
    last = np.full(n, -1, dtype=np.int64)
    nonempty = indptr[1:] > indptr[:-1]
    if nonempty.any():
        last[nonempty] = np.maximum.reduceat(pos[indices], indptr[:-1][nonempty])
    delta = np.zeros(n + 1, dtype=np.int64)
    sep = last > pos
    np.add.at(delta, pos[sep], 1)
    np.add.at(delta, last[sep], -1)
    return int(np.cumsum(delta)[:n].max()) if n else 0


def max_open_stacks_fast(matrix: np.ndarray, ordering: np.ndarray) -> int:
    """`mosp.verify.max_open_stacks` by a sweep: a customer's stack is open from
    the first to the last position of its patterns; the maximum over steps of
    the number of open stacks. Agrees with the reference on every instance
    (`tests/test_excess_constructions.py`)."""
    a = np.asarray(matrix) != 0
    n, m = a.shape
    pos = np.empty(m, dtype=np.int64)
    pos[np.asarray(ordering)] = np.arange(m)
    rows, cols = np.nonzero(a)
    if len(rows) == 0:
        return 0
    p = pos[cols]
    first = np.full(n, m, dtype=np.int64)
    last = np.full(n, -1, dtype=np.int64)
    np.minimum.at(first, rows, p)
    np.maximum.at(last, rows, p)
    has = last >= 0
    delta = np.zeros(m + 1, dtype=np.int64)
    np.add.at(delta, first[has], 1)
    np.add.at(delta, last[has] + 1, -1)
    return int(np.cumsum(delta)[:m].max())


# ----------------------------------------------------------------------------
# the constructions
# ----------------------------------------------------------------------------


def two_key_rule_width(instance: MOSPInstance) -> tuple[int, float]:
    """The two-key closing rule's product order valued by simulation (the same
    quantity `two_key_rule` returns, with the `O(n m)` Python simulation
    replaced by the sweep); returns the number of stacks and the seconds."""
    from satisfiability.heuristics import product_order_from_customers, two_key_closing_order
    t = time.perf_counter()
    order = product_order_from_customers(instance, two_key_closing_order(instance))
    value = max_open_stacks_fast(instance.matrix, np.asarray(order))
    return int(value), time.perf_counter() - t


def bfs_layers(adj: csr_matrix, rng: np.random.Generator) -> list[np.ndarray]:
    """The BFS layers of the graph from a uniformly random root; when a
    component is exhausted the next layer starts from a random unvisited
    vertex, so the list covers every vertex and concatenates to a layout."""
    n = adj.shape[0]
    visited = np.zeros(n, dtype=bool)
    layers: list[np.ndarray] = []
    indptr, indices = adj.indptr, adj.indices
    while not visited.all():
        root = int(rng.choice(np.flatnonzero(~visited)))
        frontier = np.array([root])
        visited[root] = True
        while len(frontier):
            layers.append(frontier)
            starts, ends = indptr[frontier], indptr[frontier + 1]
            if (ends - starts).sum() == 0:
                break
            nb = np.concatenate([indices[s:e] for s, e in zip(starts, ends)])
            nb = np.unique(nb)
            nb = nb[~visited[nb]]
            visited[nb] = True
            frontier = nb
    return layers


def bfs_layout(adj: csr_matrix, rng: np.random.Generator) -> tuple[int, int, int]:
    """(vertex separation of the layer-by-layer layout, `max_i (|L_i| + |L_{i+1}|) - 1`
    over consecutive layers of one BFS tree, number of layers). The layer bound
    is an upper bound on the separation: at a cut inside `L_{i+1}` the separated
    vertices lie in `L_i` and the placed part of `L_{i+1}`."""
    layers = bfs_layers(adj, rng)
    order = np.concatenate(layers)
    vs = vertex_separation(adj, order)
    sizes = [len(layer) for layer in layers]
    bound = max(sizes[i] + sizes[i + 1] for i in range(len(sizes) - 1)) - 1 if len(sizes) > 1 else sizes[0] - 1
    return vs, int(bound), len(layers)


def greedy_independent_set(adj: csr_matrix) -> int:
    """`alpha_greedy`: repeatedly take a vertex of minimum remaining degree and
    delete its closed neighbourhood. Returns the size of the independent set."""
    n = adj.shape[0]
    indptr, indices = adj.indptr, adj.indices
    deg = np.diff(indptr).astype(np.int64)
    alive = np.ones(n, dtype=bool)
    big = np.iinfo(np.int64).max
    key = deg.copy()
    count = 0
    while True:
        v = int(np.argmin(key))
        if key[v] == big:
            return count
        count += 1
        closed = np.append(indices[indptr[v]:indptr[v + 1]], v)
        closed = closed[alive[closed]]
        alive[closed] = False
        key[closed] = big
        # every surviving neighbour of a deleted vertex loses one degree
        touched = np.concatenate([indices[indptr[u]:indptr[u + 1]] for u in closed])
        if len(touched):
            dec = np.bincount(touched, minlength=n)
            keep = alive & (dec > 0)
            key[keep] -= dec[keep]


# ----------------------------------------------------------------------------
# generators
# ----------------------------------------------------------------------------


def draw_fixed(n: int, mu: float, d: int, seed: int) -> tuple[np.ndarray, int]:
    from benchmarks.generator import generate_structured_instance
    m = int(round(mu * n))
    inst = generate_structured_instance(n, m, d, seed=seed)
    return inst.matrix, 1


def draw_fitted(n: int, mu: float, d: int, seed: int, cap: int) -> tuple[np.ndarray | None, int]:
    """The best-fit Chu & Stuckey family of `gen_candidates.py`, with the draw
    cap given here instead of the scratch module's 2,000; returns the customers
    x patterns matrix, or None with `cap` when no draw of `cap` was connected."""
    if str(SIM_DIR.resolve()) not in sys.path:
        sys.path.insert(0, str(SIM_DIR.resolve()))
    from gen_candidates import bern, mosp_connected, pad_customers, pad_patterns  # noqa: PLC0415
    m = int(round(mu * n))
    rng = np.random.default_rng(seed)
    for t in range(1, cap + 1):
        mat = pad_patterns(pad_customers(bern(n, m, d / n, rng), 1, rng), 2, rng)
        if mosp_connected(mat):
            return mat.T.astype(np.int8), t
    return None, cap


# ----------------------------------------------------------------------------
# one instance, one cell, the grid
# ----------------------------------------------------------------------------


def constructions_on(matrix: np.ndarray, seed: int) -> dict:
    """Every construction on one matrix; width in pathwidth units."""
    a = np.asarray(matrix, dtype=np.int8)
    n, m = a.shape
    inst = MOSPInstance.from_matrix(a)
    rule, rule_seconds = two_key_rule_width(inst)
    t = time.perf_counter()
    adj = mosp_adjacency(a)
    edges = edge_count(adj)
    n_comp, _ = connected_components(adj, directed=False)
    t_graph = time.perf_counter() - t
    t = time.perf_counter()
    vs, layer_bound, n_layers = bfs_layout(adj, np.random.default_rng(seed))
    t_bfs = time.perf_counter() - t
    t = time.perf_counter()
    alpha = greedy_independent_set(adj)
    t_alpha = time.perf_counter() - t
    sizes = a.sum(axis=0)
    return {"n": n, "m": m, "n_ones": int(a.sum()), "e": float((a.sum() - m) / n), "edges": edges,
            "mosp_components": int(n_comp), "size_mean": float(sizes.mean()), "size_min": int(sizes.min()),
            "size_max": int(sizes.max()),
            "rule_stacks": rule, "rule": rule - 1, "rule_seconds": rule_seconds,
            "bfs_vs": vs, "bfs_layer_bound": layer_bound, "bfs_layers": n_layers, "bfs_seconds": t_bfs,
            "alpha_greedy": alpha, "n_minus_alpha": n - alpha, "alpha_seconds": t_alpha,
            "edge_bound": edges / EDGE_CONSTANT, "graph_seconds": t_graph,
            "sizes": ";".join(f"{int(v)}:{int(c)}" for v, c in zip(*np.unique(sizes, return_counts=True)))}


def cell_seed(generator: str, n: int, mu: float, d: int, index: int) -> int:
    """Deterministic and below 2^32 (numpy's legacy seeding):
    `BASE_SEED + (((gen * 10^4 + n) * 3 + mu_index) * 16 + d) * 100 + index`,
    `gen` 0 for fixed and 1 for fitted, `mu_index` the position of `mu` in the
    grid; no `hash()` of a string (salted per process)."""
    gen = {"fixed": 0, "fitted": 1}[generator]
    mu_index = {0.5: 0, 1.0: 1, 2.0: 2}[float(mu)]
    return BASE_SEED + (((gen * 10_000 + n) * 3 + mu_index) * 16 + d) * 100 + index


def _job(args) -> dict:
    generator, n, mu, d, index = args
    seed = cell_seed(generator, n, mu, d, index)
    t = time.perf_counter()
    if generator == "fixed":
        matrix, tries = draw_fixed(n, mu, d, seed)
    else:
        matrix, tries = draw_fitted(n, mu, d, seed, FITTED_CAP.get(n, 10))
    t_draw = time.perf_counter() - t
    base = {"generator": generator, "n": n, "mu": mu, "d": d, "index": index, "seed": seed, "tries": tries,
            "accepted": matrix is not None, "draw_seconds": t_draw}
    if matrix is None:
        return base
    base.update(constructions_on(matrix, seed))
    base["seconds"] = time.perf_counter() - t
    return base


def grid_jobs(ds=GRID_D, mus=GRID_MU, ns=GRID_N, reps: int = REPS, generators=("fixed", "fitted")) -> list[tuple]:
    return [(g, n, mu, d, i) for g in generators for n in ns for mu in mus for d in ds for i in range(reps)]


def run(jobs: list[tuple], workers: int, out: Path = OUT_CSV, append: bool = False) -> pd.DataFrame:
    """Run the jobs largest-`n` first (so the slow ones do not trail), writing
    the csv as cells complete; a fitted cell whose first index is not accepted
    skips its remaining indices."""
    from learning.excess import _map
    started = time.time()
    rows: list[dict] = []
    done = pd.read_csv(out) if append and out.exists() else None
    if done is not None:
        have = set(zip(done["generator"], done["n"], done["mu"], done["d"], done["index"]))
        jobs = [j for j in jobs if j not in have]
        rows = done.to_dict("records")
    # the fitted generator's rejection: probe one draw per cell first, drop the cell if it is not accepted
    probes = [j for j in jobs if j[0] == "fitted" and j[4] == 0]
    probe_rows = _map(_job, probes, workers) if probes else []
    rejected = {(r["generator"], r["n"], r["mu"], r["d"]) for r in probe_rows if not r["accepted"]}
    rows += probe_rows
    rest = [j for j in jobs if j not in set(probes) and (j[0], j[1], j[2], j[3]) not in rejected]
    rest.sort(key=lambda j: (-j[1], -j[3], -j[2]))
    for n in sorted({j[1] for j in rest}, reverse=True):
        batch = [j for j in rest if j[1] == n]
        rows += _map(_job, batch, workers)
        frame = pd.DataFrame(rows)
        out.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(out, index=False)
        print(f"n = {n}: {len(batch)} instances done, {len(rows)} rows, {time.time() - started:.0f} s wall", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(out, index=False)
    acc = frame["accepted"].sum()
    print(f"constructions: {len(frame)} rows, {acc} accepted, {len(rejected)} fitted cells not accepted at their cap, "
          f"{frame.get('seconds', pd.Series(dtype=float)).sum():.0f} s of instance time, "
          f"{time.time() - started:.0f} s wall -> {out}", flush=True)
    return frame


def load(path: Path = OUT_CSV) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist; run `python -m learning.excess --stage constructions` first")
    return pd.read_csv(path)


# ----------------------------------------------------------------------------
# the analysis
# ----------------------------------------------------------------------------


def fit_beta_plus(n: np.ndarray, width: np.ndarray) -> tuple[float, float, float, float]:
    """`width / n = beta+ + a / n` by least squares over the instances:
    (beta+, se, a, se_a); nan with fewer than three distinct sizes."""
    from learning.excess import _ols
    n, width = np.asarray(n, float), np.asarray(width, float)
    if len(set(n)) < 3:
        return np.nan, np.nan, np.nan, np.nan
    beta, a, se_beta, se_a = _ols(1.0 / n, width / n)
    return beta, se_beta, a, se_a


def certified_slopes() -> pd.DataFrame:
    """Item 02's certified slopes `b` (`learning.excess.series_slopes` on
    `excess_rule.csv`): the fixed generator at `n = 30-100`, keyed by `(mu, d)`,
    and the Chu & Stuckey `m = n` classes at `n = 30-125`, which the fitted
    generator's `mu = 1` cells are compared with (it was fitted to them)."""
    from learning.excess import load_rule, series_slopes
    s = series_slopes(load_rule())
    rows = []
    for _, x in s.iterrows():
        if x["generator"] == "fixed" and x["r"] in MU_LABELS.values():
            mu = [k for k, v in MU_LABELS.items() if v == x["r"]][0]
            sizes = x["n sizes"].split(", ")
            rows.append({"generator": "fixed", "mu": mu, "d": int(x["param"]), "b": x["b"], "se_b": x["se b"],
                         "b_source": f"fixed, n = {sizes[0]}-{sizes[-1]}", "rule_n_small": x["rule/n at max n"],
                         "opt_n_small": x["opt/n at max n"], "small_max_n": int(sizes[-1])})
        elif x["generator"] == "chu_stuckey":
            rows.append({"generator": "fitted", "mu": 1.0, "d": int(x["param"]), "b": x["b"], "se_b": x["se b"],
                         "b_source": "Chu & Stuckey, n = 30-125", "rule_n_small": x["rule/n at max n"],
                         "opt_n_small": x["opt/n at max n"], "small_max_n": 125})
    return pd.DataFrame(rows)


def cell_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per `(generator, mu, d)` and construction: `beta+` with its standard
    error, `a`, `width / n` at the largest `n` reached, that `n`, the number of
    instances; `beta*(d, mu)` (fixed `d`, and at the realised size histogram),
    item 02's `b`, the rule's gap to `b` at the largest `n` and the kill flag."""
    from learning.excess import sizes_from_text
    from learning.first_moment import beta_star
    f = frame[frame["accepted"]].copy()
    slopes = certified_slopes()
    rows = []
    for (gen, mu, d), g in f.groupby(["generator", "mu", "d"]):
        n_max = int(g["n"].max())
        top = g[g["n"] == n_max]
        hist: dict[int, int] = {}
        for text in top["sizes"]:
            for v, c in sizes_from_text(text).items():
                hist[v] = hist.get(v, 0) + c
        sl = slopes[(slopes["generator"] == gen) & (slopes["mu"] == mu) & (slopes["d"] == d)]
        b = float(sl["b"].iloc[0]) if len(sl) else np.nan
        se_b = float(sl["se_b"].iloc[0]) if len(sl) else np.nan
        b_source = sl["b_source"].iloc[0] if len(sl) else "none"
        opt_small = float(sl["opt_n_small"].iloc[0]) if len(sl) else np.nan
        rule_small = float(sl["rule_n_small"].iloc[0]) if len(sl) else np.nan
        small_n = int(sl["small_max_n"].iloc[0]) if len(sl) else 0
        rule_top = float((top["rule"] / top["n"]).mean())
        if not np.isfinite(b):
            kill_status = "no certified b"
        elif abs(rule_top - b) > KILL_TOLERANCE:
            kill_status = "not trusted"
        else:
            kill_status = "trusted"
        kill = kill_status != "trusted"
        base = {"generator": gen, "mu": mu, "d": d, "e nominal": mu * (d - 1), "e realised (max n)": float(top["e"].mean()),
                "n max": n_max, "sizes": ", ".join(str(int(x)) for x in sorted(set(g["n"]))), "instances": len(g),
                "beta* (fixed d)": beta_star(mu, [d]), "beta* (realised sizes)": beta_star(mu, hist),
                "b (certified, n <= 100)": b, "se b": se_b, "b source": b_source,
                "certified opt/n at small n": opt_small, "rule/n at small n": rule_small, "small n": small_n,
                "rule/n at max n": rule_top, "rule/n - b": rule_top - b,
                "trusted": not kill, "kill": kill_status}
        for c in CONSTRUCTIONS:
            beta, se, a, _ = fit_beta_plus(g["n"], g[c])
            base[f"{c} beta+"] = beta
            base[f"{c} se"] = se
            base[f"{c} a"] = a
            base[f"{c} /n at max n"] = float((top[c] / top["n"]).mean())
        rows.append(base)
    return pd.DataFrame(rows).sort_values(["generator", "mu", "d"]).reset_index(drop=True)


def per_size_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per cell and `n`: the mean `width / n` of every construction, the
    realised `e`, the acceptance of the fitted generator and the seconds."""
    f = frame[frame["accepted"]].copy()
    rows = []
    for (gen, mu, d, n), g in f.groupby(["generator", "mu", "d", "n"]):
        row = {"generator": gen, "mu": mu, "d": d, "n": n, "instances": len(g), "e": float(g["e"].mean()),
               "tries mean": float(g["tries"].mean()), "components": float(g["mosp_components"].mean()),
               "edges/n": float((g["edges"] / g["n"]).mean())}
        for c in CONSTRUCTIONS:
            row[f"{c}/n"] = float((g[c] / g["n"]).mean())
            row[f"{c}/n sd"] = float((g[c] / g["n"]).std()) if len(g) > 1 else 0.0
        row["bfs layers"] = float(g["bfs_layers"].mean())
        row["rule s"] = float(g["rule_seconds"].mean())
        row["bfs s"] = float(g["bfs_seconds"].mean())
        row["alpha s"] = float(g["alpha_seconds"].mean())
        row["draw s"] = float(g["draw_seconds"].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def rejected_table(frame: pd.DataFrame) -> pd.DataFrame:
    """The fitted cells whose probe draw was not accepted within the cap."""
    f = frame[~frame["accepted"]]
    return f[["generator", "n", "mu", "d", "tries", "draw_seconds"]].sort_values(["n", "mu", "d"]).reset_index(drop=True)


def summary_table(cells: pd.DataFrame) -> pd.DataFrame:
    """One row per cell: `beta*`, `b`, `beta+` of every construction, the smallest
    proved `beta+`, and the kill flag."""
    out = cells[["generator", "mu", "d", "e realised (max n)", "n max", "beta* (fixed d)", "b (certified, n <= 100)",
                 "certified opt/n at small n", "rule/n at small n", "rule/n at max n", "rule/n - b", "kill"]
                + [f"{c} beta+" for c in CONSTRUCTIONS]].copy()
    out["best proved beta+"] = out[["n_minus_alpha beta+", "edge_bound beta+"]].min(axis=1)
    out["best proved - beta*"] = out["best proved beta+"] - out["beta* (fixed d)"]
    out["rule beta+ - b"] = out["rule beta+"] - out["b (certified, n <= 100)"]
    return out


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def tables(frame: pd.DataFrame) -> str:
    cells = cell_table(frame)
    summary = summary_table(cells)
    sizes = per_size_table(frame)
    rejected = rejected_table(frame)
    acc = frame[frame["accepted"]]
    killed = cells[cells["kill"] == "not trusted"]
    untested = cells[cells["kill"] == "no certified b"]
    parts = [
        f"Instances: {len(acc)} accepted of {len(frame)} rows; {acc['generator'].value_counts().to_dict()}; "
        f"n = {int(acc['n'].min())}-{int(acc['n'].max())}; {acc['seconds'].sum() / 3600:.2f} core-hours of instance time "
        f"(rule {acc['rule_seconds'].sum() / 3600:.2f}, BFS {acc['bfs_seconds'].sum() / 3600:.3f}, "
        f"greedy alpha {acc['alpha_seconds'].sum() / 3600:.3f}, draws {acc['draw_seconds'].sum() / 3600:.3f}). "
        f"Cells: {len(cells)}; fitted draws not accepted at the cap: {len(rejected)} rows, "
        f"{len(set(zip(rejected['n'], rejected['mu'], rejected['d'])))} (n, mu, d) cells, of which "
        f"{int((rejected['n'] == rejected.groupby(['mu', 'd'])['n'].transform('min')).sum())} are the smallest rejected n of their (mu, d). "
        f"Kill: of the {len(cells) - len(untested)} cells with a certified b, {len(killed)} have "
        f"|rule/n at max n - b| > {KILL_TOLERANCE} and are NOT trusted: "
        + ", ".join(f"{r.generator} ({r.d}, {r.mu:g})" for r in killed.itertuples())
        + f"; {len(untested)} cells have no certified b and are untested (not to be quoted either): "
        + ", ".join(f"{r.generator} ({r.d}, {r.mu:g})" for r in untested.itertuples()) + ".",
        "\n### beta+ per construction and cell, with beta* and b\n", _md(summary, ".3f"),
        "\n### The fits in full\n", _md(cells, ".3f"),
        "\n### Per cell and n: width / n of every construction\n", _md(sizes, ".3f"),
        "\n### Fitted cells not accepted within the draw cap\n", _md(rejected) if len(rejected) else "(none)",
    ]
    return "\n".join(parts)


# ----------------------------------------------------------------------------
# the figure
# ----------------------------------------------------------------------------

# the reference categorical order of the dataviz skill (blue, orange, aqua, yellow), validated 2026-11-01
COLOURS = {"n_minus_alpha": "#2a78d6", "rule": "#eb6834", "edge_bound": "#1baf7a", "bfs_vs": "#eda100"}
LABELS = {"rule": "two-key rule", "bfs_vs": "BFS layers (vertex separation)", "n_minus_alpha": "n − α greedy (proved)",
          "edge_bound": "|E| / 5.769 (proved up to O(log n))"}


def figure(frame: pd.DataFrame, out: Path = FIGURE) -> Path:
    """Small multiples, one per `mu`, fixed generator: against `d`, `beta+` of
    each construction (markers, bars ± 2 se where the fit exists), `beta*` as a
    grey line and item 02's certified slope `b` as black ticks; the fitted
    generator at `mu = 1` as hollow markers. PNG for the report."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    cells = cell_table(frame)
    mus = sorted(set(cells["mu"]))
    fig, axes = plt.subplots(1, len(mus), figsize=(3.6 * len(mus), 3.6), sharey=True, squeeze=False)
    for ax, mu in zip(axes.ravel(), mus):
        g = cells[(cells["mu"] == mu) & (cells["generator"] == "fixed")].sort_values("d")
        h = cells[(cells["mu"] == mu) & (cells["generator"] == "fitted")].sort_values("d")
        ax.plot(g["d"], g["beta* (fixed d)"], color="#9d9c95", lw=1.5, zorder=1)
        ax.plot(g["d"], g["b (certified, n <= 100)"], ls="none", marker="_", ms=14, mew=2, color="#0b0b0b", zorder=4)
        for c, col in COLOURS.items():
            ax.errorbar(g["d"], g[f"{c} beta+"], yerr=2 * g[f"{c} se"], fmt="o", ms=5, color=col, ecolor=col,
                        elinewidth=1, zorder=3)
            if len(h):
                ax.plot(h["d"], h[f"{c} beta+"], ls="none", marker="o", ms=5, mfc="none", mec=col, zorder=3)
        ax.set_title(f"μ = m / n = {mu:g}", fontsize=10, color="#0b0b0b", loc="left")
        ax.set_xticks(list(GRID_D))
        ax.set_ylim(-0.02, 1.3)
        ax.grid(False)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#c3c2b7")
        ax.tick_params(colors="#52514e", labelsize=8)
        ax.set_xlabel("d, customers per pattern", fontsize=9, color="#52514e")
    axes[0, 0].set_ylabel("β⁺: width per customer, extrapolated", fontsize=9, color="#52514e")
    handles = [Line2D([], [], ls="none", marker="o", color=c, ms=5, label=LABELS[k]) for k, c in COLOURS.items()]
    handles += [Line2D([], [], color="#9d9c95", lw=1.5, label="β* (first moment, fixed d)"),
                Line2D([], [], ls="none", marker="_", ms=14, mew=2, color="#0b0b0b", label="b, certified slope at n ≤ 100"),
                Line2D([], [], ls="none", marker="o", ms=5, mfc="none", mec="#52514e", label="hollow: fitted Chu & Stuckey generator")]
    fig.legend(handles=handles, loc="upper right", frameon=False, fontsize=8, ncol=2)
    fig.text(0.01, 0.95, "fixed generator, n = 100–5000, 10 instances per cell; bars ± 2 se of the fit width / n = β⁺ + a / n",
             fontsize=8, color="#52514e")
    fig.tight_layout(rect=(0, 0, 1, 0.84))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)
    return out


# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, nargs="*", default=list(GRID_N))
    ap.add_argument("--d", type=int, nargs="*", default=list(GRID_D))
    ap.add_argument("--mu", type=float, nargs="*", default=list(GRID_MU))
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--generators", nargs="*", default=["fixed", "fitted"])
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--out", type=Path, default=OUT_CSV)
    ap.add_argument("--append", action="store_true", help="keep the rows already in --out and run only the missing jobs")
    ap.add_argument("--tables", action="store_true")
    args = ap.parse_args()
    if args.tables:
        print(tables(load(args.out)))
        return
    from learning.excess import default_workers
    workers = args.workers if args.workers is not None else default_workers()
    print(f"load {os.getloadavg()[0]:.1f}, {workers} workers", flush=True)
    run(grid_jobs(args.d, args.mu, args.n, args.reps, args.generators), workers, args.out, append=args.append)


if __name__ == "__main__":
    main()
