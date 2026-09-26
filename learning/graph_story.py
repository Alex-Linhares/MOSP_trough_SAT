"""Is the graph the whole story? (`reports/ml_nature_plan.md` §2.9, loop0002 item 05)

The question. The optimum is `pathwidth(MOSP graph) + 1`, a function of the
graph alone. Is the *hardness* -- the nodes the complete customer search
visits to refute `optimum - 1` -- also a function of the graph, or does the
matrix (which cliques cover which edges) carry information the reduction
discards? And §8's two counts: the number of optimal closing orders under the
search measure (`count_search`) should be equal on two instances with the
same graph, while the number under the construction value (`count_closing`)
need not be.

What is known before any measurement, from the code. `customer_search.decide`
and its C port consume `_neighbour_masks(instance)` -- the self-inclusive
neighbourhoods `N[c]` of the MOSP graph, indexed by customer -- and nothing
else of the matrix. So under the default configuration the node count is a
function of the *labelled* graph. The one place the matrix enters is the
`csearch` configuration, where `sparse_enough_for_better_move` turns Theorem 2
on when the mean number of products per customer is at most 5. The study
below therefore measures three separate things and says which is which:

1. **Re-coverings with fixed labels** (the item's construction): a campaign
   instance's edge set is re-covered by different cliques -- a product split
   in two along a cut whose crossing edges are covered elsewhere, two
   overlapping products merged when their union is a clique, and a greedy
   edge-clique cover under a shuffled edge order -- and each is solved and
   refuted. Nodes must agree exactly under the default configuration; under
   `csearch` they differ exactly when the re-covering crosses the density
   threshold, and the size of that difference is the one matrix effect.
2. **Relabellings**: the same matrix with rows permuted. Every corpus pair
   with the same graph and different products also differs in labelling, so
   this is the variance any graph-*invariant* predictor cannot remove, and the
   floor against which the kill test has to be read.
3. **The kill test**: predict `log10(1 + nodes)` from graph-only features,
   from matrix-only features and from the full set, grouped by isomorphism
   class. Graph-only as good as the full set is the plan's kill.

Plus the corpus pairs §1 found (150 graph classes at n <= 40 holding several
matrix classes) with their node counts from `learning/data/node_counts.csv`,
and the §8 counts on the re-covered pairs at n <= 15.

Run:

    python -m learning.graph_story --workers 16                # everything, ~5 min
    python -m learning.graph_story --stage tables              # tables from the CSVs
    python -m pytest tests/test_graph_story.py -q

Writes `learning/data/ensemble/recover.csv.gz`, `relabel.csv.gz` and
`recover_lattice.csv` (the committed artifact: every re-covered instance
regenerates from `(base_name, method, k)` through `recover`, the base from the
campaign manifest), witnesses under `learning/data/ensemble/recover_solutions/`
(64 MB, git-ignored, re-solved in three minutes), and
`reports/graph_story_tables.md`. Nothing is written to `solutions/`; no solver
default is touched; nothing here is a bound.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import time
import zlib
from types import SimpleNamespace
from pathlib import Path

import numpy as np
import pandas as pd

from mosp.instance import MOSPInstance

ENSEMBLE_DIR = Path("learning/data/ensemble")
RESULTS_CSV = ENSEMBLE_DIR / "results.csv"
RECOVER_CSV = ENSEMBLE_DIR / "recover.csv.gz"
RELABEL_CSV = ENSEMBLE_DIR / "relabel.csv.gz"
LATTICE_CSV = ENSEMBLE_DIR / "recover_lattice.csv"
RECOVER_SOLUTIONS = ENSEMBLE_DIR / "recover_solutions"
CANONICAL_CSV = Path("learning/data/canonical.csv")
NODE_COUNTS_CSV = Path("learning/data/node_counts.csv")
TABLES = Path("reports/graph_story_tables.md")

METHODS = ("split", "merge", "greedy")
CONFIGS = ("default", "csearch")
BASE_SIZES = (10, 15, 20, 25, 30, 35, 40)
LATTICE_MAX_N = 15

# Feature sets for the kill test, built from `learning.features` group names
# (never from every numeric column: a label leaked that way once). The
# invariants group mixes graph-only quantities with matrix-derived ones
# (`cc_products`, `cc_greedy` start from the product set; `rig_*` from the
# matrix density), and the bounds group is matrix-dependent except for
# contraction degeneracy: `lb_trivial` is a column sum, `ub_*` simulate the
# constructed product order, `lb_best` folds the trivial bound in.
GRAPH_ONLY_INVARIANTS = ("tw_min_fill", "tw_min_degree", "bw_rcm", "spectral_radius",
                         "fiedler", "fiedler_lcc", "sep_size", "sep_frac")
GRAPH_ONLY_BOUNDS = ("lb_contraction",)


def feature_sets(with_optimum: bool = True) -> dict[str, list[str]]:
    from learning.features import feature_names

    graph = feature_names(("graph",)) + list(GRAPH_ONLY_INVARIANTS) + list(GRAPH_ONLY_BOUNDS)
    matrix = feature_names(("matrix",))
    full = feature_names()
    extra = ["optimum"] if with_optimum else []
    return {"graph-only": graph + extra, "matrix-only": matrix + extra, "full": full + extra}


# ----------------------------------------------------------------------------
# re-covering the same edge set
# ----------------------------------------------------------------------------


def _masks(instance: MOSPInstance) -> list[int]:
    from satisfiability.heuristics import _neighbour_masks

    return _neighbour_masks(instance)


def _columns(matrix: np.ndarray) -> list[tuple[int, ...]]:
    return [tuple(np.flatnonzero(matrix[:, j]).tolist()) for j in range(matrix.shape[1])]


def _edge_cover(columns: list[tuple[int, ...]]) -> dict[tuple[int, int], int]:
    cover: dict[tuple[int, int], int] = {}
    for col in columns:
        for a in range(len(col)):
            for b in range(a + 1, len(col)):
                cover[(col[a], col[b])] = cover.get((col[a], col[b]), 0) + 1
    return cover


def _is_clique(vertices, masks: list[int]) -> bool:
    vs = list(vertices)
    for v in vs:
        for w in vs:
            if v != w and not (masks[v] >> w) & 1:
                return False
    return True


def _from_columns(columns: list[tuple[int, ...]], n: int, name: str) -> MOSPInstance:
    matrix = np.zeros((n, len(columns)), dtype=np.int64)
    for j, col in enumerate(columns):
        matrix[list(col), j] = 1
    return MOSPInstance.from_matrix(matrix, name=name)


def split_product(instance: MOSPInstance, rng: np.random.Generator, name: str) -> MOSPInstance | None:
    """Replace one product `P` by two, `A ⊂ P` and `B`, covering the same edges.

    `B` is `P \\ A` plus every vertex of `A` with an edge into `P \\ A` that no
    other product covers, so the crossing edges of the cut `(A, P \\ A)` are
    kept by `B` where needed and left to the other products where they can be.
    A split with `B = P` adds a dominated column and is used only when no
    product admits a proper split.
    """
    matrix = np.asarray(instance.matrix)
    columns = _columns(matrix)
    cover = _edge_cover(columns)
    order = [j for j in rng.permutation(len(columns)) if len(columns[j]) >= 3]
    fallback = None
    for j in order:
        P = list(columns[j])
        for _ in range(12):
            size = int(rng.integers(1, len(P)))
            A = set(rng.choice(P, size=size, replace=False).tolist())
            rest = [v for v in P if v not in A]
            B = set(rest)
            for v in A:
                if any(cover[(min(v, b), max(v, b))] == 1 for b in rest):
                    B.add(v)
            new = columns[:j] + [tuple(sorted(A)), tuple(sorted(B))] + columns[j + 1:]
            if len(B) < len(P):
                return _from_columns(new, instance.n_customers, name)
            if fallback is None:
                fallback = new
    if fallback is None:
        return None
    return _from_columns(fallback, instance.n_customers, name)


def merge_products(instance: MOSPInstance, rng: np.random.Generator, name: str) -> MOSPInstance | None:
    """Merge two overlapping products whose union is a clique of the graph.

    Prefers a pair neither of which contains the other; a nested pair merges
    to the larger product, which is pattern dominance in reverse and used
    only when nothing else is mergeable.
    """
    matrix = np.asarray(instance.matrix)
    columns = _columns(matrix)
    masks = _masks(instance)
    sets = [set(c) for c in columns]
    pairs = [(i, j) for i in range(len(columns)) for j in range(i + 1, len(columns))
             if sets[i] & sets[j]]
    if not pairs:
        return None
    fallback = None
    for idx in rng.permutation(len(pairs)):
        i, j = pairs[idx]
        union = sets[i] | sets[j]
        if not _is_clique(union, masks):
            continue
        new = [c for k, c in enumerate(columns) if k not in (i, j)] + [tuple(sorted(union))]
        nested = sets[i] <= sets[j] or sets[j] <= sets[i]
        if not nested:
            return _from_columns(new, instance.n_customers, name)
        if fallback is None:
            fallback = new
    if fallback is None:
        return None
    return _from_columns(fallback, instance.n_customers, name)


def greedy_recover(instance: MOSPInstance, rng: np.random.Generator, name: str) -> MOSPInstance:
    """A fresh edge-clique cover: maximal cliques grown from uncovered edges in
    a shuffled order. Customers with products but no neighbours keep a
    singleton product so the set of customers that ever open is unchanged."""
    masks = _masks(instance)
    n = instance.n_customers
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if (masks[u] >> v) & 1]
    covered: set[tuple[int, int]] = set()
    columns: list[tuple[int, ...]] = []
    for idx in rng.permutation(len(edges)) if edges else []:
        u, v = edges[idx]
        if (u, v) in covered:
            continue
        clique = [u, v]
        common = masks[u] & masks[v]
        candidates = [w for w in range(n) if (common >> w) & 1 and w not in (u, v)]
        for w in rng.permutation(candidates) if candidates else []:
            w = int(w)
            if all((masks[x] >> w) & 1 for x in clique):
                clique.append(w)
        clique.sort()
        for a in range(len(clique)):
            for b in range(a + 1, len(clique)):
                covered.add((clique[a], clique[b]))
        columns.append(tuple(clique))
    for c in range(n):
        if masks[c] == (1 << c) and instance.customer_patterns(c):
            columns.append((c,))
    return _from_columns(columns, n, name)


def recover(instance: MOSPInstance, method: str, k: int) -> MOSPInstance | None:
    """The k-th re-covering of `instance` by `method`; seeded from both, so it
    regenerates from the campaign manifest alone."""
    seed = zlib.crc32(f"{instance.name}|{method}|{k}".encode())
    rng = np.random.default_rng(seed)
    name = f"{instance.name}__{method}{k}"
    if method == "split":
        return split_product(instance, rng, name)
    if method == "merge":
        return merge_products(instance, rng, name)
    if method == "greedy":
        from learning.canonical import matrix_digest

        base = matrix_digest(instance)
        for _ in range(6):
            cand = greedy_recover(instance, rng, name)
            if matrix_digest(cand) != base:
                return cand
        return None
    raise ValueError(f"unknown method {method!r}; one of {METHODS}")


def relabel(instance: MOSPInstance, k: int) -> tuple[MOSPInstance, np.ndarray]:
    """Rows permuted (customers renamed), columns too; same matrix class."""
    seed = zlib.crc32(f"{instance.name}|relabel|{k}".encode())
    rng = np.random.default_rng(seed)
    perm = rng.permutation(instance.n_customers)
    cols = rng.permutation(instance.n_patterns)
    matrix = np.asarray(instance.matrix)[perm][:, cols]
    return MOSPInstance.from_matrix(matrix, name=f"{instance.name}__relabel{k}"), perm


def same_labelled_graph(a: MOSPInstance, b: MOSPInstance) -> bool:
    return a.n_customers == b.n_customers and _masks(a) == _masks(b)


# ----------------------------------------------------------------------------
# bases, jobs, runs
# ----------------------------------------------------------------------------


def _generate_base(row) -> MOSPInstance:
    from learning.ensemble import Cell, generate

    cell = Cell(row.generator, int(row.n), int(row.m), float(row.param))
    return generate(cell, int(row.index))


def select_bases(results: pd.DataFrame, per_n: int = 60, sizes=BASE_SIZES,
                 seed: int = 0) -> pd.DataFrame:
    """One base per graph class per size: half drawn uniformly over the
    non-complete certified rows, half from the hardest decile by nodes, so
    that the ratio tests have room to move."""
    rng = np.random.default_rng(seed)
    frame = results[(~results.complete_graph) & results.certified
                    & (results.status_default == "unsat") & (results.optimum >= 2)]
    frame = frame.drop_duplicates("graph_cert")
    picks = []
    for n in sizes:
        d = frame[frame.n == n]
        if d.empty:
            continue
        hard = d[d.nodes_default >= d.nodes_default.quantile(0.9)]
        k_hard = min(per_n // 2, len(hard))
        chosen = hard.sample(k_hard, random_state=int(rng.integers(1 << 31)))
        rest = d.drop(chosen.index)
        k_rest = min(per_n - k_hard, len(rest))
        chosen = pd.concat([chosen, rest.sample(k_rest, random_state=int(rng.integers(1 << 31)))])
        picks.append(chosen)
    return pd.concat(picks).reset_index(drop=True)


def _refute_both(instance: MOSPInstance, optimum: int, deadline: float | None) -> dict:
    from learning.node_counts import refute
    from satisfiability.customer_search import sparse_enough_for_better_move

    out: dict = {"better_move": bool(sparse_enough_for_better_move(instance))}
    for config in CONFIGS:
        r = refute(instance, optimum, config, deadline)
        out[f"status_{config}"] = r["status"]
        out[f"nodes_{config}"] = r["nodes"]
        out[f"seconds_{config}"] = r["seconds"]
    return out


def _recover_job(args) -> list[dict]:
    base_row, methods, per_method, solutions_dir, deadline, solve_budget = args
    base_row = SimpleNamespace(**base_row)
    from learning.canonical import canonical_record
    from learning.features import instance_features
    from mosp.verify import max_open_stacks
    from satisfiability.mosp_solver import solve_mosp_exact

    base = _generate_base(base_row)
    optimum = int(base_row.optimum)
    base_ref = _refute_both(base, optimum, deadline)
    rows = []
    for method in methods:
        for k in range(per_method):
            inst = recover(base, method, k)
            row: dict = {
                "base_name": base.name, "cell": base_row.cell, "n": base.n_customers,
                "m_base": base.n_patterns, "method": method, "k": k,
                "base_optimum": optimum, "base_better_move": base_ref["better_move"],
                "base_nodes_default": base_ref["nodes_default"],
                "base_nodes_csearch": base_ref["nodes_csearch"],
                "base_nodes_default_csv": int(base_row.nodes_default),
                "base_row_mean": float(base_row.row_mean),
            }
            if inst is None:
                row.update({"instance_name": None, "applicable": False})
                rows.append(row)
                continue
            row["instance_name"] = inst.name
            row["applicable"] = True
            row["m_new"] = inst.n_patterns
            row["masks_equal"] = same_labelled_graph(base, inst)
            stats: dict = {}
            t0 = time.monotonic()
            value, ordering = solve_mosp_exact(inst, solutions_dir=solutions_dir,
                                               time_budget=solve_budget, stats=stats)
            row["solve_seconds"] = round(time.monotonic() - t0, 4)
            row["optimum"] = int(value)
            row["solve_proof"] = stats.get("proof", "")
            row["same_optimum"] = int(value) == optimum
            row["witness_ok"] = int(max_open_stacks(inst, list(ordering))) == int(value)
            row.update(_refute_both(inst, optimum, deadline))
            row.update(instance_features(inst))
            canon = canonical_record(inst)
            for key in ("matrix_digest", "graph_cert", "bipartite_cert"):
                row[key] = canon[key]
            row["base_matrix_digest"] = base_row.matrix_digest
            row["base_graph_cert"] = base_row.graph_cert
            row["base_bipartite_cert"] = base_row.bipartite_cert
            rows.append(row)
    return rows


def _relabel_job(args) -> list[dict]:
    base_row, per_base, deadline = args
    base_row = SimpleNamespace(**base_row)
    base = _generate_base(base_row)
    optimum = int(base_row.optimum)
    rows = []
    ref = _refute_both(base, optimum, deadline)
    rows.append({"base_name": base.name, "cell": base_row.cell, "n": base.n_customers,
                 "k": -1, "instance_name": base.name, **ref})
    for k in range(per_base):
        inst, _ = relabel(base, k)
        rows.append({"base_name": base.name, "cell": base_row.cell, "n": base.n_customers,
                     "k": k, "instance_name": inst.name, **_refute_both(inst, optimum, deadline)})
    return rows


def _lattice_job(args) -> list[dict]:
    base_row, methods, per_method = args
    base_row = SimpleNamespace(**base_row)
    from learning.degeneracy import analyse

    base = _generate_base(base_row)
    optimum = int(base_row.optimum)
    rows = []

    def _counts(inst: MOSPInstance, method: str, k: int) -> dict:
        r = analyse(inst, optimum, max_products_exact=0)
        return {"base_name": base.name, "n": base.n_customers, "method": method, "k": k,
                "instance_name": inst.name, "m": inst.n_patterns,
                "count_search": int(r["count_search"]), "count_closing": int(r["count_closing"]),
                "min_search": int(r["min_search"]), "min_construction": int(r["min_construction"]),
                "twin_factor": int(r["twin_factor"])}

    rows.append(_counts(base, "base", -1))
    for method in methods:
        for k in range(per_method):
            inst = recover(base, method, k)
            if inst is not None:
                rows.append(_counts(inst, method, k))
    return rows


def _pool_map(fn, jobs, workers: int):
    if workers <= 1:
        for out in map(fn, jobs):
            yield out
        return
    with mp.get_context("fork").Pool(workers) as pool:
        for out in pool.imap_unordered(fn, jobs, chunksize=1):
            yield out


def _write(rows: list[dict], csv: Path) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv, index=False, float_format="%.6g")
    return frame


def run_recover(bases: pd.DataFrame, workers: int, per_method: int = 3,
                methods=METHODS, csv: Path = RECOVER_CSV,
                solutions_dir: Path = RECOVER_SOLUTIONS, deadline: float | None = 60.0,
                solve_budget: float | None = 300.0) -> pd.DataFrame:
    solutions_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(row, methods, per_method, solutions_dir, deadline, solve_budget)
            for row in bases.to_dict("records")]
    rows: list[dict] = []
    for out in _pool_map(_recover_job, jobs, workers):
        rows.extend(out)
    return _write(rows, csv)


def run_relabel(bases: pd.DataFrame, workers: int, per_base: int = 10,
                csv: Path = RELABEL_CSV, deadline: float | None = 60.0) -> pd.DataFrame:
    jobs = [(row, per_base, deadline) for row in bases.to_dict("records")]
    rows: list[dict] = []
    for out in _pool_map(_relabel_job, jobs, workers):
        rows.extend(out)
    return _write(rows, csv)


def run_lattice(bases: pd.DataFrame, workers: int, per_method: int = 3,
                methods=METHODS, csv: Path = LATTICE_CSV) -> pd.DataFrame:
    bases = bases[bases.n <= LATTICE_MAX_N]
    jobs = [(row, methods, per_method) for row in bases.to_dict("records")]
    rows: list[dict] = []
    for out in _pool_map(_lattice_job, jobs, workers):
        rows.extend(out)
    return _write(rows, csv)


# ----------------------------------------------------------------------------
# analysis
# ----------------------------------------------------------------------------


def _log_ratio(new: pd.Series, base: pd.Series) -> pd.Series:
    return np.log10(1.0 + new.astype(float)) - np.log10(1.0 + base.astype(float))


def paired_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per method: applicability, the audits, and the within-pair node
    comparison under both configurations."""
    from scipy import stats

    out = []
    for method, d in frame.groupby("method"):
        app = d[d.applicable.astype(bool)]
        row = {
            "method": method, "bases": d.base_name.nunique(), "attempted": len(d),
            "applicable": len(app),
            "matrix differs": int((app.matrix_digest != app.base_matrix_digest).sum()),
            "matrix class differs": int((app.bipartite_cert != app.base_bipartite_cert).sum()),
            "masks equal": int(app.masks_equal.astype(bool).sum()),
            "graph cert equal": int((app.graph_cert == app.base_graph_cert).sum()),
            "same optimum": int(app.same_optimum.astype(bool).sum()),
            "witness ok": int(app.witness_ok.astype(bool).sum()),
            "m change (median)": float((app.m_new - app.m_base).median()),
        }
        for config in CONFIGS:
            new, base = app[f"nodes_{config}"], app[f"base_nodes_{config}"]
            lr = _log_ratio(new, base)
            row[f"{config}: nodes equal"] = int((new == base).sum())
            row[f"{config}: |log10 ratio| median"] = float(lr.abs().median())
            row[f"{config}: |log10 ratio| max"] = float(lr.abs().max()) if len(lr) else float("nan")
            row[f"{config}: ratio p10"] = float((10 ** lr).quantile(0.1)) if len(lr) else float("nan")
            row[f"{config}: ratio p90"] = float((10 ** lr).quantile(0.9)) if len(lr) else float("nan")
            nz = lr[lr != 0]
            if len(nz) >= 5:
                row[f"{config}: wilcoxon p"] = float(stats.wilcoxon(nz).pvalue)
            else:
                row[f"{config}: wilcoxon p"] = float("nan")
        flipped = app[app.better_move != app.base_better_move]
        row["better_move flipped"] = len(flipped)
        if len(flipped):
            lr = _log_ratio(flipped.nodes_csearch, flipped.base_nodes_csearch)
            row["flipped: csearch |log10 ratio| median"] = float(lr.abs().median())
            row["flipped: csearch ratio min"] = float((10 ** lr).min())
            row["flipped: csearch ratio max"] = float((10 ** lr).max())
        out.append(row)
    return pd.DataFrame(out)


def flip_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Where the re-covering crossed the better_move density threshold: the
    same labelled graph refuted with Theorem 2 on and off."""
    app = frame[frame.applicable.astype(bool)]
    flipped = app[app.better_move != app.base_better_move].copy()
    if flipped.empty:
        return pd.DataFrame()
    on = np.where(flipped.better_move, flipped.nodes_csearch, flipped.base_nodes_csearch)
    off = np.where(flipped.better_move, flipped.base_nodes_csearch, flipped.nodes_csearch)
    flipped["nodes_bm_on"] = on
    flipped["nodes_bm_off"] = off
    flipped["log10 ratio on/off"] = np.log10(1.0 + on.astype(float)) - np.log10(1.0 + off.astype(float))
    rows = []
    for n, d in flipped.groupby("n"):
        lr = d["log10 ratio on/off"]
        rows.append({"n": n, "flipped pairs": len(d), "bases": d.base_name.nunique(),
                     "on < off": int((d.nodes_bm_on < d.nodes_bm_off).sum()),
                     "on == off": int((d.nodes_bm_on == d.nodes_bm_off).sum()),
                     "on > off": int((d.nodes_bm_on > d.nodes_bm_off).sum()),
                     "ratio on/off median": float((10 ** lr).median()),
                     "ratio on/off p10": float((10 ** lr).quantile(0.1)),
                     "ratio on/off p90": float((10 ** lr).quantile(0.9)),
                     "nodes off median": float(d.nodes_bm_off.median())})
    return pd.DataFrame(rows)


def relabel_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per size: how much the node count moves under a random relabelling of
    the same matrix -- the floor for any label-free predictor."""
    rows = []
    for n, d in frame.groupby("n"):
        rec = {"n": n, "bases": d.base_name.nunique(), "relabellings": int((d.k >= 0).sum())}
        for config in CONFIGS:
            col = f"nodes_{config}"
            g = d.groupby("base_name")[col]
            base = d[d.k < 0].set_index("base_name")[col]
            lo, hi = g.min(), g.max()
            spread = np.log10(1.0 + hi.astype(float)) - np.log10(1.0 + lo.astype(float))
            logs = np.log10(1.0 + d[col].astype(float))
            within_std = logs.groupby(d.base_name).std(ddof=0)
            dev = (logs - logs.groupby(d.base_name).transform("median")).abs()
            rec[f"{config}: bases with any change"] = int((hi != lo).sum())
            rec[f"{config}: max/min ratio median"] = float((10 ** spread).median())
            rec[f"{config}: max/min ratio p90"] = float((10 ** spread).quantile(0.9))
            rec[f"{config}: max/min ratio max"] = float((10 ** spread).max())
            rec[f"{config}: within-base std log10"] = float(within_std.mean())
            rec[f"{config}: MAD log10 (floor)"] = float(dev.mean())
            rec[f"{config}: base nodes median"] = float(base.median())
        rows.append(rec)
    return pd.DataFrame(rows)


def lattice_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Within each base: `count_search` equal across re-coverings (it must
    be), `count_closing` not (it need not be)."""
    rows = []
    base = frame[frame.method == "base"].set_index("base_name")
    rec = frame[frame.method != "base"].copy()
    rec["base_search"] = rec.base_name.map(base.count_search)
    rec["base_closing"] = rec.base_name.map(base.count_closing)
    rec["lr_closing"] = np.log10(rec.count_closing.astype(float)) - np.log10(rec.base_closing.astype(float))
    for (n, method), d in rec.groupby(["n", "method"]):
        rows.append({"n": n, "method": method, "pairs": len(d), "bases": d.base_name.nunique(),
                     "count_search equal": int((d.count_search == d.base_search).sum()),
                     "min_search == optimum": int((d.min_search == base.loc[d.base_name, "min_search"].values).sum()),
                     "count_closing equal": int((d.count_closing == d.base_closing).sum()),
                     "closing ratio median": float((10 ** d.lr_closing).median()),
                     "closing ratio p10": float((10 ** d.lr_closing).quantile(0.1)),
                     "closing ratio p90": float((10 ** d.lr_closing).quantile(0.9)),
                     "closing ratio min": float((10 ** d.lr_closing).min()),
                     "closing ratio max": float((10 ** d.lr_closing).max()),
                     "count_search median": float(d.count_search.median()),
                     "count_closing median": float(d.count_closing.median())})
    return pd.DataFrame(rows)


def corpus_pairs(canonical: Path = CANONICAL_CSV, node_counts: Path = NODE_COUNTS_CSV,
                 max_n: int = 40) -> tuple[pd.DataFrame, pd.DataFrame]:
    """§1's graph classes holding several matrix classes, with their corpus
    node counts; and the level-2 relabelling groups. Returns (per class, summary)."""
    c = pd.read_csv(canonical)
    c = c[c.n_customers <= max_n]
    nc = pd.read_csv(node_counts)
    for config in CONFIGS:
        sub = nc[nc.config == config][["instance_name", "nodes"]].rename(columns={"nodes": f"nodes_{config}"})
        c = c.merge(sub, on="instance_name", how="left")
    multi = c.groupby("graph_cert").filter(lambda d: d.bipartite_cert.nunique() > 1)
    per_class = multi.groupby("graph_cert").agg(
        n=("n_customers", "first"), optimum=("optimum", "first"),
        matrix_classes=("bipartite_cert", "nunique"), instances=("instance_name", "size"),
        nodes_default_min=("nodes_default", "min"), nodes_default_max=("nodes_default", "max"),
        nodes_csearch_min=("nodes_csearch", "min"), nodes_csearch_max=("nodes_csearch", "max"),
        collections=("collection", lambda x: ", ".join(sorted(set(x)))),
    ).reset_index()
    rows = []
    for n, d in per_class.groupby("n"):
        rows.append({"n": n, "graph classes": len(d), "matrix classes": int(d.matrix_classes.sum()),
                     "instances": int(d.instances.sum()),
                     "optimum = n": int((d.optimum == d.n).sum()),
                     "default nodes differ": int((d.nodes_default_min != d.nodes_default_max).sum()),
                     "csearch nodes differ": int((d.nodes_csearch_min != d.nodes_csearch_max).sum()),
                     "default nodes max": float(d.nodes_default_max.max()),
                     "default nodes median": float(d.nodes_default_max.median())})
    return per_class, pd.DataFrame(rows)


def _model():
    try:
        import lightgbm as lgb

        return lgb.LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=31,
                                 min_child_samples=20, subsample=0.8, subsample_freq=1,
                                 colsample_bytree=0.8, verbose=-1, n_jobs=4, random_state=0)
    except ImportError:  # pragma: no cover - soft dependency
        from sklearn.ensemble import HistGradientBoostingRegressor

        return HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=0)


def kill_test(results: pd.DataFrame, target: str = "nodes_default", folds: int = 5,
              with_optimum: bool = True, seed: int = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Predict `log10(1 + nodes)` from each feature set under GroupKFold by
    MOSP-graph class. Returns (overall, by n) tables of MAE, RMSE and R²."""
    from sklearn.model_selection import GroupKFold

    frame = results.dropna(subset=[target]).copy()
    y = np.log10(1.0 + frame[target].astype(float)).to_numpy()
    groups = frame["graph_cert"].to_numpy()
    sets = feature_sets(with_optimum)
    pred = {name: np.zeros(len(frame)) for name in sets}
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(frame))          # GroupKFold is deterministic in group order
    gkf = GroupKFold(n_splits=folds)
    for train, test in gkf.split(order, groups=groups[order]):
        tr, te = order[train], order[test]
        for name, cols in sets.items():
            model = _model()
            model.fit(frame.iloc[tr][cols].to_numpy(dtype=float), y[tr])
            pred[name][te] = model.predict(frame.iloc[te][cols].to_numpy(dtype=float))
    baseline = np.full(len(frame), np.nan)
    for _, idx in frame.groupby("n").indices.items():
        baseline[idx] = np.median(y[idx])           # per-size median: what size alone knows

    def _score(mask) -> list[dict]:
        rows = []
        for name in list(sets) + ["size-median baseline"]:
            p = baseline if name == "size-median baseline" else pred[name]
            err = p[mask] - y[mask]
            ss = np.sum((y[mask] - y[mask].mean()) ** 2)
            rows.append({"features": name, "n_features": 0 if name.startswith("size") else len(sets[name]),
                         "rows": int(mask.sum()), "MAE log10": float(np.abs(err).mean()),
                         "RMSE log10": float(np.sqrt((err ** 2).mean())),
                         "R2": float(1 - np.sum(err ** 2) / ss) if ss > 0 else float("nan"),
                         "within 2x": float((np.abs(err) <= np.log10(2)).mean())})
        return rows

    overall = pd.DataFrame(_score(np.ones(len(frame), bool)))
    by_n = []
    for n, idx in frame.groupby("n").indices.items():
        mask = np.zeros(len(frame), bool)
        mask[idx] = True
        for r in _score(mask):
            by_n.append({"n": n, **r})
    return overall, pd.DataFrame(by_n)


def paired_kill(overall_full: pd.DataFrame, overall_nc: pd.DataFrame) -> dict:
    """The kill criterion, read off the tables: graph-only within 0.01 MAE of
    the full set, or better, on the deduplicated campaign."""
    def _mae(t, name):
        return float(t.loc[t.features == name, "MAE log10"].iloc[0])

    verdict = {}
    for label, t in (("all", overall_full), ("non-complete", overall_nc)):
        g, f, m = _mae(t, "graph-only"), _mae(t, "full"), _mae(t, "matrix-only")
        verdict[label] = {"graph-only MAE": g, "full MAE": f, "matrix-only MAE": m,
                          "graph − full": g - f, "kill met": bool(g - f <= 0.01)}
    return verdict


# ----------------------------------------------------------------------------
# tables and main
# ----------------------------------------------------------------------------


def _fmt(value, floatfmt: str) -> str:
    if isinstance(value, (bool, np.bool_)):
        return str(bool(value))
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return "nan"
        if float(value).is_integer() and abs(value) < 1e15:
            return f"{int(value):,}"
        return format(float(value), floatfmt)
    return str(value)


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    """Markdown with integers kept whole (tabulate would print 1,090 as 1.09e+03)."""
    if frame is None or len(frame) == 0:
        return "*(empty)*\n"
    text = frame.map(lambda v: _fmt(v, floatfmt)) if hasattr(frame, "map") else frame.applymap(lambda v: _fmt(v, floatfmt))
    return text.to_markdown(index=False, disable_numparse=True) + "\n"


def write_tables(out: Path = TABLES, recover_csv: Path = RECOVER_CSV,
                 relabel_csv: Path = RELABEL_CSV, lattice_csv: Path = LATTICE_CSV,
                 results_csv: Path = RESULTS_CSV, ml: bool = True, seconds: float | None = None) -> dict:
    from learning.ensemble import dedupe

    summary: dict = {}
    parts = ["# Is the graph the whole story? — tables (§2.9, item 05)\n",
             "*Generated by `python -m learning.graph_story`. Every table regenerates from "
             "`learning/data/ensemble/results.csv`, `recover.csv.gz`, `relabel.csv.gz` and `recover_lattice.csv`.*\n"]
    if seconds is not None:
        parts.append(f"*Wall time of the run that wrote these: {seconds:.0f} s.*\n")

    rec = pd.read_csv(recover_csv) if recover_csv.exists() else pd.DataFrame()
    if len(rec):
        pt = paired_table(rec)
        summary["paired"] = pt
        parts += ["\n## Re-coverings with fixed labels: paired comparison per method\n", _md(pt)]
        parts += ["\n### By size, default configuration\n"]
        app = rec[rec.applicable.astype(bool)]
        by_n = app.groupby(["n", "method"]).apply(lambda d: pd.Series({
            "pairs": len(d), "nodes equal (default)": int((d.nodes_default == d.base_nodes_default).sum()),
            "nodes equal (csearch)": int((d.nodes_csearch == d.base_nodes_csearch).sum()),
            "better_move flipped": int((d.better_move != d.base_better_move).sum()),
            "same optimum": int(d.same_optimum.astype(bool).sum()),
            "base nodes median": float(d.base_nodes_default.median()),
            "base nodes max": float(d.base_nodes_default.max())}), include_groups=False).reset_index()
        summary["by_n"] = by_n
        parts.append(_md(by_n))
        ft = flip_table(rec)
        summary["flip"] = ft
        parts += ["\n## The one matrix effect: `better_move` on against off, same labelled graph\n", _md(ft)]
        parts += ["\n### The base rows re-refuted against the campaign CSV\n"]
        rerun = rec.drop_duplicates("base_name")
        parts.append(f"{int((rerun.base_nodes_default == rerun.base_nodes_default_csv).sum())} of "
                     f"{len(rerun)} base node counts reproduced exactly.\n")
        summary["base_reproduced"] = (int((rerun.base_nodes_default == rerun.base_nodes_default_csv).sum()), len(rerun))

    rel = pd.read_csv(relabel_csv) if relabel_csv.exists() else pd.DataFrame()
    if len(rel):
        rt = relabel_table(rel)
        summary["relabel"] = rt
        parts += ["\n## Relabellings of the same matrix: the label floor\n", _md(rt)]

    lat = pd.read_csv(lattice_csv) if lattice_csv.exists() else pd.DataFrame()
    if len(lat):
        lt = lattice_table(lat)
        summary["lattice"] = lt
        parts += ["\n## §8's counts within re-covered pairs (n ≤ 15)\n", _md(lt)]

    per_class, corpus = corpus_pairs()
    summary["corpus"] = corpus
    parts += ["\n## The corpus pairs: graph classes with several matrix classes, n ≤ 40\n", _md(corpus)]
    parts += ["\n### The ten with the most nodes\n",
              _md(per_class.sort_values("nodes_default_max", ascending=False).head(10))]

    if ml and results_csv.exists():
        results = dedupe(pd.read_csv(results_csv))
        overall, by_n = kill_test(results)
        nc = results[~results.complete_graph & (results.nodes_default >= 1)]
        overall_nc, by_n_nc = kill_test(nc)
        overall_noopt, _ = kill_test(nc, with_optimum=False)
        overall_cs, _ = kill_test(nc, target="nodes_csearch")
        summary.update({"ml_all": overall, "ml_nc": overall_nc, "ml_by_n": by_n_nc,
                        "ml_noopt": overall_noopt, "ml_cs": overall_cs,
                        "kill": paired_kill(overall, overall_nc)})
        parts += ["\n## The kill test: predicting log10(1 + nodes_default), GroupKFold(5) by graph class\n",
                  "\n### Deduplicated campaign, all rows\n", _md(overall),
                  "\n### Non-complete graphs with at least one node\n", _md(overall_nc),
                  "\n### Non-complete, without the optimum as a feature\n", _md(overall_noopt),
                  "\n### Non-complete, target nodes_csearch\n", _md(overall_cs),
                  "\n### Non-complete, by n\n", _md(by_n_nc),
                  "\n### Verdict\n", f"```\n{summary['kill']}\n```\n"]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(parts))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("all", "recover", "relabel", "lattice", "tables"), default="all")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--per-n", type=int, default=60, help="bases per size")
    ap.add_argument("--per-method", type=int, default=3)
    ap.add_argument("--relabellings", type=int, default=10)
    ap.add_argument("--sizes", type=int, nargs="*", default=list(BASE_SIZES))
    ap.add_argument("--no-ml", action="store_true")
    ap.add_argument("--out", type=Path, default=TABLES)
    args = ap.parse_args()

    started = time.time()
    results = pd.read_csv(RESULTS_CSV)
    bases = select_bases(results, per_n=args.per_n, sizes=tuple(args.sizes))
    print(f"{len(bases)} bases: " + ", ".join(f"n={n}: {c}" for n, c in bases.n.value_counts().sort_index().items()), flush=True)

    if args.stage in ("all", "recover"):
        t0 = time.time()
        rec = run_recover(bases, args.workers, per_method=args.per_method)
        print(f"recover: {len(rec)} rows, {int(rec.applicable.sum())} applicable, {time.time() - t0:.0f} s", flush=True)
    if args.stage in ("all", "relabel"):
        t0 = time.time()
        rel = run_relabel(bases, args.workers, per_base=args.relabellings)
        print(f"relabel: {len(rel)} rows, {time.time() - t0:.0f} s", flush=True)
    if args.stage in ("all", "lattice"):
        t0 = time.time()
        lat = run_lattice(bases, args.workers, per_method=args.per_method)
        print(f"lattice: {len(lat)} rows, {time.time() - t0:.0f} s", flush=True)

    summary = write_tables(args.out, ml=not args.no_ml, seconds=time.time() - started)
    for key in ("paired", "flip", "relabel", "lattice", "corpus", "ml_all", "ml_nc", "ml_noopt", "ml_cs"):
        if key in summary:
            print(f"\n## {key}\n{_md(summary[key])}")
    if "kill" in summary:
        print("\nkill:", summary["kill"])
    print(f"\nwrote {args.out}; {time.time() - started:.0f} s total")


if __name__ == "__main__":
    main()
