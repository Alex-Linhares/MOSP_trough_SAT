"""Conjecture mining for a branching-aware lower bound (plan 2 §2.6, loop0003 item 09).

**Question.** §6 showed that three of the four components of the proved bound
`lb_best` are lower bounds on treewidth, and §21 that pathwidth strictly
exceeds treewidth on at least 48.5% of the 338 instances where `lb_best`
misses by two or more — so no degree or clique argument can be tight there.
Is there a formula `f(G)` over invariants that *see branching* which is never
above the optimum on every certified instance we have, exceeds `lb_best` on
more than 5% of the gap instances, and survives an adversary that searches for
a counterexample with the exact solver as oracle?

**Invariants** (all of the MOSP graph, `learning.treewidth` masks; every one
is a function of the graph, §13):

- *treewidth*: `tw_lo ≤ tw ≤ tw_hi`, exact by the subset DP at n ≤ 26 and by
  the decision search under a deadline above it (a censored call keeps the
  interval; `tw_lo` is always a valid lower bound on treewidth, and
  `tw + 1 ≤ optimum` is a theorem since treewidth ≤ pathwidth);
- *expansion profile*: `f(1..T)` of `satisfiability.expansion_bound`, exact
  levels only, and the bound they prove (`exp`);
- *branching*: articulation points, blocks, bridges, the pathwidth of the
  block–cut tree (`bct_pw`; Ellis–Sudborough–Turner's recursion on trees, a
  vertex with three branches of pathwidth ≥ k gives ≥ k + 1), the number of
  articulation points with three or more branches (`hubs3`), and the
  *branch-lemma bound* `blt`: over every vertex whose removal leaves three or
  more components, the third-largest treewidth of a component plus one, which
  is a lower bound on pathwidth by the same lemma (pw(B) ≥ tw(B), and three
  branches of pathwidth ≥ k force pathwidth ≥ k + 1);
- *cliques*: the clique number `omega` (exact), simplicial vertices, and the
  pathwidth of a clique tree of a chordal completion (`ct_pw`; deterministic
  construction, so a computable quantity but not a graph invariant in the
  strict sense — it is labelled as such in the tables).

**Candidates.** Every monomial of at most two invariants from
`learning.formula_search.enumerate_terms`, each turned into a bound three
ways: *raw* (the term itself, for integer terms; its `above` count is the
check that a theorem is a theorem), *additive* `⌊t + b⌋` with `b` the largest
constant valid on every certified row, and *scaled* `⌊a · t⌋` likewise. A
constant chosen on all rows makes the candidate valid by construction, so two
honest checks follow: the constant re-chosen on four fifths of the file ∪
isomorphism-class groups is applied to the fifth held out (`holdout_above`),
and every survivor is attacked by the extremal search of `learning.extremal`
with objective `f(G) − optimum` at n ≤ 15 (10⁴ oracle evaluations each). The
smallest counterexample of each broken candidate is drawn and re-certified.

**Ranking.** `exceed`: the fraction of the 338 corpus gap ≥ 2 instances where
the candidate is strictly above `lb_best`; `tight`: where it equals the
optimum; `shortfall`: the mean of `optimum − f`. Kill (plan 2 §2.6): no
survivor exceeds `lb_best` on more than 5% of the gap instances.

**Nothing here is a bound the solver uses.** No candidate reaches
`satisfiability.mosp_solver._lower_bound` or any path that decides `k`. A
survivor is a *conjecture* (or, for `tw + 1`, `omega`, `exp` and `blt + 1`, a
theorem restated) and is handed to item 12 as a statement.

Usage:
    python -m learning.conjecture --stage invariants --workers 16   # ~25 min: every certified instance
    python -m learning.conjecture --stage repair --workers 16       # recompute branching on multi-component rows
    python -m learning.conjecture --stage mine                      # ~1 min: candidates, validity, ranking
    python -m learning.conjecture --stage attack --workers 16       # ~10 min: 10⁴ adversarial evaluations per survivor
    python -m learning.conjecture --stage tables                    # reports/conjecture_tables.md
    python -m pytest tests/test_conjecture.py -q
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

from learning.treewidth import (
    DP_MAX_N,
    masks_from_graph,
    masks_from_matrix,
    mmd_lower_bound,
    treewidth_bounded,
    treewidth_exact,
)
from mosp.instance import MOSPInstance

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "learning" / "data"
ENSEMBLE = DATA / "ensemble"
SCRATCH_SOLUTIONS = DATA / "conjecture" / "solutions"
INVARIANTS_CSV = ENSEMBLE / "conjecture_invariants.csv.gz"
CANDIDATES_CSV = ENSEMBLE / "conjecture_candidates.csv"
ATTACK_CSV = ENSEMBLE / "conjecture_attack.csv"
ATTACK_LARGE_CSV = ENSEMBLE / "conjecture_attack_large.csv"
COUNTER_CSV = ENSEMBLE / "conjecture_counterexamples.csv"
COUNTER_LARGE_CSV = ENSEMBLE / "conjecture_counterexamples_large.csv"
TABLES = ROOT / "reports" / "conjecture_tables.md"
INSTANCES_CSV = DATA / "instances.csv"
CANONICAL_CSV = DATA / "canonical.csv"
RESULTS_CSV = ENSEMBLE / "results.csv"
RESULTS_UPWARD_CSV = ENSEMBLE / "results_upward.csv"

EXPANSION_T = 6
EXPANSION_BUDGET = 0.5
TW_DEADLINE = 1.0
KILL_EXCEED = 0.05
ATTACK_SIZES = tuple(range(8, 16))
LARGE_SIZES = (20, 25, 30)        # supplementary, beyond the plan's n ≤ 15; oracle 0.1–0.6 s per call

# invariants the mining may raise to a power (strictly positive on connected
# graphs with an edge; the pool is filtered again on the data)
INVARIANT_NAMES = (
    "tw_lo", "tw1", "omega", "exp", "blt1", "bct_pw", "hubs3", "art", "blocks", "bridges",
    "simplicial", "ct_pw", "n_cliques", "f1", "f2", "f3", "f4", "f5", "f6",
    "n", "edges", "deg_mean", "deg_min", "deg_max", "degeneracy", "contraction",
    "sep_size", "tw_min_fill", "bw_rcm", "components",
)


# ----------------------------------------------------------------------------
# tree pathwidth (Ellis, Sudborough & Turner 1994)
# ----------------------------------------------------------------------------


def tree_pathwidth(adjacency: dict) -> int:
    """Exact pathwidth (= vertex separation) of a forest given as an adjacency
    dict. `vs(T) ≥ k + 1` for k ≥ 1 iff some vertex has three branches of
    `vs ≥ k`; `vs = 1` iff the forest has an edge; `vs = 0` otherwise.
    Memoised over directed subtrees, O(n²) in the worst case."""
    from functools import lru_cache

    if not adjacency:
        return 0
    if not any(adjacency.values()):
        return 0
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10_000 + 4 * len(adjacency)))

    @lru_cache(maxsize=None)
    def sub_vs(u, parent) -> int:
        """vs of the component of T − {u, parent} that contains u (the whole
        tree hanging from u away from parent)."""
        nodes = []
        stack = [(u, parent)]
        while stack:
            x, p = stack.pop()
            nodes.append((x, p))
            for y in adjacency[x]:
                if y != p:
                    stack.append((y, x))
        has_edge = len(nodes) > 1
        best = 1 if has_edge else 0
        for x, p in nodes:
            branches = sorted((sub_vs(y, x) for y in adjacency[x] if y != p), reverse=True)
            if len(branches) >= 3:
                best = max(best, branches[2] + 1)
        return best

    best = 0
    seen = set()
    for root in adjacency:
        if root in seen:
            continue
        stack = [root]
        comp = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adjacency[x])
        # vs of a component = max over its vertices of third-largest branch + 1,
        # or 1 / 0 by edge presence
        comp_best = 1 if any(adjacency[x] for x in comp) else 0
        for x in comp:
            branches = sorted((sub_vs(y, x) for y in adjacency[x]), reverse=True)
            if len(branches) >= 3:
                comp_best = max(comp_best, branches[2] + 1)
        best = max(best, comp_best)
    return best


# ----------------------------------------------------------------------------
# the invariants
# ----------------------------------------------------------------------------


def _graph_from_masks(masks):
    import networkx as nx

    g = nx.Graph()
    g.add_nodes_from(range(len(masks)))
    for u, mk in enumerate(masks):
        v = mk >> (u + 1) << (u + 1)
        while v:
            low = v & -v
            g.add_edge(u, low.bit_length() - 1)
            v ^= low
    return g


def branching_invariants(graph) -> dict:
    """Articulation points, blocks, bridges, the block–cut tree's pathwidth,
    hubs with three or more branches, and the branch-lemma treewidth bound."""
    import networkx as nx

    n = graph.number_of_nodes()
    out = {"art": 0, "blocks": 0, "bridges": 0, "bct_pw": 0, "hubs3": 0, "blt": 0}
    if n == 0:
        return out
    arts = set(nx.articulation_points(graph))
    blocks = list(nx.biconnected_components(graph))
    out["art"] = len(arts)
    out["blocks"] = len(blocks)
    out["bridges"] = sum(1 for _ in nx.bridges(graph))
    # block–cut tree: block nodes and cut-vertex nodes, isolated vertices as blocks
    adjacency: dict = {}
    for i, block in enumerate(blocks):
        node = ("b", i)
        adjacency.setdefault(node, [])
        for v in block:
            if v in arts:
                cut = ("c", v)
                adjacency.setdefault(cut, []).append(node)
                adjacency[node].append(cut)
    for v in graph.nodes():
        if graph.degree(v) == 0:
            adjacency[("i", v)] = []
    out["bct_pw"] = tree_pathwidth(adjacency)
    # branch lemma: for every vertex with ≥ 3 *branches* — components of
    # G − v that contain a neighbour of v — the third-largest treewidth of a
    # branch + 1 is a lower bound on pathwidth. Components of G that never
    # touched v are not branches (the first draft counted them, and claimed
    # pathwidth ≥ 2 on 347 forests; caught by the "above optimum" column).
    blt = 0
    hubs3 = 0
    for v in arts:
        rest = graph.subgraph(set(graph.nodes()) - {v})
        nbrs = set(graph.neighbors(v))
        comps = [c for c in nx.connected_components(rest) if c & nbrs]
        if len(comps) < 3:
            continue
        hubs3 += 1
        tws = []
        for comp in comps:
            sub = nx.convert_node_labels_to_integers(rest.subgraph(comp))
            masks = masks_from_graph(sub)
            if sub.number_of_edges() == 0:
                tws.append(0)
            elif sub.number_of_nodes() <= DP_MAX_N:
                tws.append(treewidth_exact(masks)[0])
            else:
                tws.append(mmd_lower_bound(masks))          # valid, weaker
        tws.sort(reverse=True)
        blt = max(blt, tws[2] + 1)
    out["hubs3"] = hubs3
    out["blt"] = blt
    return out


def clique_tree_pathwidth(graph) -> tuple[int, int]:
    """Pathwidth of a clique tree of the MCS-M chordal completion, and the
    number of maximal cliques of that completion. The clique tree is the
    maximum-weight spanning tree of the clique graph (weight = intersection
    size) with ties broken by sorted clique labels, so the value is
    deterministic; it is a computable quantity, not a graph invariant."""
    import networkx as nx

    if graph.number_of_edges() == 0:
        return 0, graph.number_of_nodes()
    chordal, _ = nx.complete_to_chordal_graph(graph)
    cliques = sorted((tuple(sorted(c)) for c in nx.chordal_graph_cliques(chordal)))
    if len(cliques) == 1:
        return 0, 1
    cg = nx.Graph()
    cg.add_nodes_from(range(len(cliques)))
    sets = [set(c) for c in cliques]
    for i in range(len(cliques)):
        for j in range(i + 1, len(cliques)):
            w = len(sets[i] & sets[j])
            if w:
                cg.add_edge(i, j, weight=w)
    tree = nx.maximum_spanning_tree(cg, weight="weight")
    adjacency = {i: sorted(tree.neighbors(i)) for i in tree.nodes()}
    for i in range(len(cliques)):
        adjacency.setdefault(i, [])
    return tree_pathwidth(adjacency), len(cliques)


def simplicial_count(masks) -> int:
    """Vertices whose neighbourhood is a clique (isolated vertices included)."""
    count = 0
    for v, nb in enumerate(masks):
        ok = True
        rest = nb
        while rest:
            low = rest & -rest
            u = low.bit_length() - 1
            rest ^= low
            if (masks[u] | (1 << u)) & nb != nb:
                ok = False
                break
        count += ok
    return count


def expansion_profile(instance: MOSPInstance, max_t: int = EXPANSION_T,
                      budget: float | None = EXPANSION_BUDGET) -> dict:
    from satisfiability.expansion_bound import expansion_bound

    eb = expansion_bound(instance, max_t=max_t, time_budget=budget)
    out = {f"f{t}": float("nan") for t in range(1, max_t + 1)}
    for t, value in enumerate(eb.levels[:max_t], start=1):
        out[f"f{t}"] = int(value)
    out["exp"] = int(eb.value)
    out["exp_cap"] = int(eb.cap)
    return out


def invariants(matrix, tw_deadline: float = TW_DEADLINE,
               expansion_budget: float | None = EXPANSION_BUDGET) -> dict:
    """Every invariant of one instance, from its matrix."""
    import networkx as nx

    from satisfiability.mosp_solver import _contraction_degeneracy

    matrix = np.asarray(matrix, dtype=int)
    inst = MOSPInstance.from_matrix(matrix.tolist(), name="inv")
    masks = masks_from_matrix(matrix)
    graph = _graph_from_masks(masks)
    n = matrix.shape[0]
    started = time.monotonic()
    out: dict = {"n": n, "m": int(matrix.shape[1]), "edges": graph.number_of_edges(),
                 "components": nx.number_connected_components(graph) if n else 0}
    degrees = [d for _, d in graph.degree()] or [0]
    out["deg_mean"] = float(np.mean(degrees))
    out["deg_min"] = int(min(degrees))
    out["deg_max"] = int(max(degrees))
    out["degeneracy"] = int(max(nx.core_number(graph).values())) if graph.number_of_edges() else 0
    out["contraction"] = int(_contraction_degeneracy(graph) + 1) if n else 0
    out["omega"] = max((len(c) for c in nx.find_cliques(graph)), default=0) if n else 0
    out["simplicial"] = simplicial_count(masks)
    # treewidth
    if n <= DP_MAX_N:
        tw, _ = treewidth_exact(masks)
        out.update(tw_lo=int(tw), tw_hi=int(tw), tw_exact=True, tw_method="dp")
    elif n <= 64:
        res = treewidth_bounded(masks, deadline_seconds=tw_deadline)
        out.update(tw_lo=int(res["lo"]), tw_hi=int(res["hi"]), tw_exact=bool(res["exact"]),
                   tw_method="bb")
    else:
        from learning.treewidth import min_fill_upper_bound

        out.update(tw_lo=int(mmd_lower_bound(masks)), tw_hi=int(min_fill_upper_bound(masks)[0]),
                   tw_exact=False, tw_method="heuristic")
        out["tw_exact"] = bool(out["tw_lo"] == out["tw_hi"])
    out["tw1"] = out["tw_lo"] + 1
    out.update(branching_invariants(graph))
    out["blt1"] = out["blt"] + 1          # in optimum units: pw ≥ blt ⇒ optimum ≥ blt + 1
    out["ct_pw"], out["n_cliques"] = clique_tree_pathwidth(graph)
    out.update(expansion_profile(inst, budget=expansion_budget))
    # heuristics from the feature table's invariants, recomputed here so the
    # generated instances have them too
    from networkx.algorithms.approximation import treewidth_min_fill_in

    out["tw_min_fill"] = int(treewidth_min_fill_in(graph)[0]) if graph.number_of_edges() else 0
    rcm = list(nx.utils.reverse_cuthill_mckee_ordering(graph)) if n else []
    pos = {v: i for i, v in enumerate(rcm)}
    out["bw_rcm"] = max((abs(pos[u] - pos[v]) for u, v in graph.edges()), default=0)
    out["sep_size"] = _balanced_separator(graph, rcm)
    out["seconds"] = round(time.monotonic() - started, 3)
    return out


def _balanced_separator(graph, order) -> int:
    """Smallest vertex separation of the order over prefixes of size n/3..2n/3."""
    n = len(order)
    if n < 3:
        return 0
    pos = {v: i for i, v in enumerate(order)}
    best = n
    for cut in range(n // 3, 2 * n // 3 + 1):
        left = set(order[:cut])
        sep = sum(1 for v in left if any(pos[u] >= cut for u in graph.neighbors(v)))
        best = min(best, sep)
    return best


# ----------------------------------------------------------------------------
# the instances: corpus, campaign, upward
# ----------------------------------------------------------------------------


def corpus_rows() -> pd.DataFrame:
    frame = pd.read_csv(INSTANCES_CSV)
    canon = pd.read_csv(CANONICAL_CSV)[["instance_name", "source_file", "graph_cert"]]
    frame = frame.merge(canon, on=["instance_name", "source_file"], how="left")
    frame["source"] = "corpus"
    frame["group_file"] = frame["source_file"]
    return frame


def generated_rows() -> pd.DataFrame:
    parts = []
    for csv, source in ((RESULTS_CSV, "campaign"), (RESULTS_UPWARD_CSV, "upward")):
        if not csv.exists():
            continue
        f = pd.read_csv(csv, low_memory=False)
        if source == "upward":
            finish = csv.with_name("results_upward_finish.csv")
            if finish.exists():
                try:
                    from learning.upward import apply_finish

                    f = apply_finish(f, finish)
                except Exception:  # noqa: BLE001 - the finish stage is 12 rows
                    pass
        f = f[f["certified"].astype(str).str.lower() == "true"].copy()
        f["source"] = source
        f["group_file"] = f["cell"].astype(str)
        parts.append(f)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def all_rows() -> pd.DataFrame:
    keep = ["instance_name", "source", "group_file", "graph_cert", "optimum", "n_customers",
            "n_patterns", "lb_best", "lb_trivial", "lb_contraction", "tw_min_fill", "bw_rcm",
            "g_degeneracy", "sep_size"]
    corpus = corpus_rows()
    gen = generated_rows()
    for extra in ("source_file", "cell", "generator", "n", "m", "param", "index"):
        for f in (corpus, gen):
            if extra not in f.columns:
                f[extra] = np.nan
    cols = keep + ["source_file", "cell", "generator", "n", "m", "param", "index"]
    frame = pd.concat([corpus[cols], gen[cols]], ignore_index=True) if len(gen) else corpus[cols]
    frame["optimum"] = frame["optimum"].astype(int)
    frame["gap"] = frame["optimum"] - frame["lb_best"].astype(int)
    return frame


def _corpus_matrices(frame: pd.DataFrame) -> dict[tuple[str, str], np.ndarray]:
    from learning.dataset import enumerate_instances

    wanted = {(r.instance_name, r.source_file) for r in frame.itertuples()}
    found = {}
    for path, inst in enumerate_instances():
        for name, source in wanted:
            if inst.name == name and str(path).endswith(source):
                found[(name, source)] = np.asarray(inst.matrix, dtype=int)
    return found


def _generated_matrix(row) -> np.ndarray:
    from learning.ensemble import Cell, generate

    cell = Cell(str(row.generator), int(row.n), int(row.m), float(row.param))
    return np.asarray(generate(cell, int(row.index)).matrix, dtype=int)


def _inv_job(args) -> dict:
    name, source, matrix_key = args
    from learning.extremal import matrix_from_key

    matrix = matrix_from_key(matrix_key)
    try:
        out = invariants(matrix)
    except Exception as exc:  # noqa: BLE001 - one bad instance must not sink the run
        out = {"error": repr(exc)}
    out["instance_name"] = name
    out["source"] = source
    return out


def run_invariants(workers: int = 16, out_csv: Path = INVARIANTS_CSV, limit: int | None = None,
                   sources: tuple[str, ...] = ("corpus", "campaign", "upward")) -> pd.DataFrame:
    """Every invariant for every certified instance; resumable."""
    from learning.extremal import matrix_key

    frame = all_rows()
    frame = frame[frame["source"].isin(sources)]
    done = set()
    if out_csv.exists():
        prev = pd.read_csv(out_csv)
        done = set(zip(prev["instance_name"], prev["source"]))
    todo = frame[[(n, s) not in done for n, s in zip(frame["instance_name"], frame["source"])]]
    if limit:
        todo = todo.head(limit)
    print(f"[conjecture] {len(frame)} certified rows, {len(done)} done, {len(todo)} to compute",
          flush=True)
    jobs = []
    corpus_part = todo[todo["source"] == "corpus"]
    if len(corpus_part):
        mats = _corpus_matrices(corpus_part)
        for r in corpus_part.itertuples():
            jobs.append((r.instance_name, "corpus", matrix_key(mats[(r.instance_name, r.source_file)])))
    for r in todo[todo["source"] != "corpus"].itertuples():
        jobs.append((r.instance_name, r.source, matrix_key(_generated_matrix(r))))
    # heaviest first so the tail is short
    jobs.sort(key=lambda j: -len(j[2]))
    started = time.monotonic()
    rows = []
    flushed = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_inv_job, j) for j in jobs]
        for i, fut in enumerate(as_completed(futures), start=1):
            rows.append(fut.result())
            if i % 2000 == 0 or i == len(futures):
                print(f"[conjecture] {i}/{len(futures)} in {time.monotonic() - started:.0f}s",
                      flush=True)
            if len(rows) - flushed >= 5000 or i == len(futures):
                _append(out_csv, pd.DataFrame(rows[flushed:]))
                flushed = len(rows)
    return pd.read_csv(out_csv)


def _branch_job(args) -> dict:
    name, source, matrix_key = args
    from learning.extremal import matrix_from_key

    matrix = matrix_from_key(matrix_key)
    out = branching_invariants(_graph_from_masks(masks_from_matrix(matrix)))
    out["blt1"] = out["blt"] + 1
    out["instance_name"] = name
    out["source"] = source
    return out


def repair_branching(workers: int = 16, inv_csv: Path = INVARIANTS_CSV) -> pd.DataFrame:
    """Recompute the branching invariants for every row whose MOSP graph has
    more than one component — the only rows the first draft's branch count
    could get wrong — and rewrite those columns in place."""
    inv = pd.read_csv(inv_csv)
    frame = all_rows()
    todo = inv[inv["components"] > 1][["instance_name", "source"]].merge(
        frame, on=["instance_name", "source"], how="left")
    print(f"[conjecture] repairing branching invariants on {len(todo)} multi-component rows", flush=True)
    from learning.extremal import matrix_key

    jobs = []
    corpus_part = todo[todo["source"] == "corpus"]
    if len(corpus_part):
        mats = _corpus_matrices(corpus_part)
        for r in corpus_part.itertuples():
            jobs.append((r.instance_name, "corpus", matrix_key(mats[(r.instance_name, r.source_file)])))
    for r in todo[todo["source"] != "corpus"].itertuples():
        jobs.append((r.instance_name, r.source, matrix_key(_generated_matrix(r))))
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for out in pool.map(_branch_job, jobs, chunksize=64):
            rows.append(out)
    fix = pd.DataFrame(rows).set_index(["instance_name", "source"])
    inv = inv.set_index(["instance_name", "source"])
    cols = ["art", "blocks", "bridges", "bct_pw", "hubs3", "blt", "blt1"]
    changed = int((inv.loc[fix.index, cols] != fix[cols]).any(axis=1).sum())
    inv.loc[fix.index, cols] = fix[cols]
    inv = inv.reset_index()
    inv.to_csv(inv_csv, index=False)
    print(f"[conjecture] {changed} rows changed", flush=True)
    return inv


def _append(csv: Path, part: pd.DataFrame) -> None:
    csv.parent.mkdir(parents=True, exist_ok=True)
    if csv.exists():
        prev = pd.read_csv(csv)
        part = pd.concat([prev, part], ignore_index=True)
    part.to_csv(csv, index=False)


# ----------------------------------------------------------------------------
# candidates
# ----------------------------------------------------------------------------


def load_table(inv_csv: Path = INVARIANTS_CSV) -> pd.DataFrame:
    inv = pd.read_csv(inv_csv)
    if "error" in inv.columns:
        inv = inv[inv["error"].isna()]
    frame = all_rows().merge(inv.drop(columns=[c for c in ("n", "m") if c in inv.columns]),
                             on=["instance_name", "source"], how="inner")
    frame["n"] = frame["n_customers"].astype(int)
    return frame


def group_ids(frame: pd.DataFrame) -> np.ndarray:
    from learning.fingerprint import union_groups

    return union_groups(frame["group_file"].astype(str), frame["graph_cert"])


def candidate_value(values: dict, cand: dict) -> int:
    """The bound a candidate claims on one instance (optimum units), or a very
    negative number if an ingredient is missing."""
    t = 1.0
    for f, e in cand["term"]:
        x = values.get(f)
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return -10 ** 6
        if x <= 0 and e < 0:
            return -10 ** 6
        t *= float(x) ** e
    kind = cand["kind"]
    if kind == "raw":
        return int(math.floor(t + 1e-9))
    if kind == "add":
        return int(math.floor(t + cand["const"] + 1e-9))
    return int(math.floor(cand["const"] * t + 1e-9))


def _floor_sig(x: float, digits: int = 4) -> float:
    """Round towards −∞ to `digits` significant figures (keeps validity)."""
    if x == 0 or not math.isfinite(x):
        return x
    mag = math.floor(math.log10(abs(x)))
    scale = 10.0 ** (mag - digits + 1)
    return math.floor(x / scale) * scale


def mine(frame: pd.DataFrame, max_degree: int = 2, folds: int = 5,
         names: tuple[str, ...] = INVARIANT_NAMES) -> pd.DataFrame:
    """Every candidate with its constant, validity, hold-out validity and
    tightness on the gap instances. One row per candidate."""
    from learning.formula_search import enumerate_terms, evaluate_terms, format_term

    cols = [c for c in names if c in frame.columns]
    values = {c: frame[c].astype(float).to_numpy() for c in cols}
    positive = {c for c in cols if np.all(np.nan_to_num(values[c], nan=1.0) > 0)}
    terms = enumerate_terms(cols, positive, max_degree=max_degree)
    opt = frame["optimum"].to_numpy(dtype=float)
    lb = frame["lb_best"].to_numpy(dtype=float)
    gap_mask = ((frame["source"] == "corpus") & (frame["gap"] >= 2)).to_numpy()
    groups = group_ids(frame)
    uniq = np.unique(groups)
    rng = np.random.default_rng(0)
    perm = rng.permutation(len(uniq))
    fold_of_group = {g: i % folds for g, i in zip(uniq[perm], range(len(uniq)))}
    fold = np.array([fold_of_group[g] for g in groups])
    integral = {c: bool(np.all(np.nan_to_num(values[c], nan=0.0) == np.round(np.nan_to_num(values[c], nan=0.0))))
                for c in cols}
    tw1 = frame["tw1"].to_numpy(dtype=float)
    # the best *proved* bound on record: the solver's, or exact/interval treewidth + 1
    thm = np.maximum(lb, tw1)
    small = (frame["n"].to_numpy() <= ATTACK_SIZES[-1])
    rows = []
    chunk = 400            # terms per evaluation block: 400 × 51k doubles is 160 MB
    for start in range(0, len(terms), chunk):
        block = terms[start:start + chunk]
        rows.extend(_score_block(block, evaluate_terms(values, block), opt, lb, gap_mask, fold,
                                 folds, integral, tw1, thm, small))
    out = pd.DataFrame(rows)
    out["valid"] = out["above"] == 0
    out["survivor"] = out["valid"] & (out["exceed_gap"] > KILL_EXCEED)
    # novel: valid and strictly above the best proved bound somewhere — a
    # candidate pointwise ≤ max(lb_best, tw + 1) is a theorem restated
    out["novel"] = out["valid"] & (out["count_thm_all"] > 0)
    # attackable: claims at least 2 on some certified instance at n ≤ 15;
    # a candidate that is ≤ 1 everywhere that small is vacuous there and the
    # n ≤ 15 adversary cannot test it
    out["attackable"] = out["max_val_small"] >= 2
    out = out.sort_values(["valid", "exceed_gap", "tight_gap"], ascending=[False, False, False])
    return out.reset_index(drop=True)


def _score_block(terms, T, opt, lb, gap_mask, fold, folds, integral, tw1, thm=None,
                 small=None) -> list[dict]:
    if thm is None:
        thm = np.maximum(lb, tw1)
    if small is None:
        small = np.ones(len(opt), dtype=bool)
    from learning.formula_search import format_term

    rows = []
    for term, t in zip(terms, T):
        ok = np.isfinite(t)
        if ok.sum() < len(t) * 0.5:
            continue
        kinds = []
        # raw: only for integer-valued single features and products with exponent 1
        if all(e == 1 for _, e in term) and all(integral[f] for f, _ in term):
            kinds.append(("raw", 0.0))
        b = float(np.min(opt[ok] - t[ok]))
        kinds.append(("add", math.floor(b * 100) / 100))
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = (opt[ok] + 1) / t[ok]
        ratio = ratio[np.isfinite(ratio) & (t[ok] > 0)]
        if len(ratio):
            a = float(np.min(ratio)) * (1 - 1e-9)
            kinds.append(("scale", _floor_sig(a)))
        for kind, const in kinds:
            if kind == "raw":
                val = np.floor(t + 1e-9)
            elif kind == "add":
                val = np.floor(t + const + 1e-9)
            else:
                val = np.floor(const * t + 1e-9)
            val = np.where(ok, val, -1e6)
            above = int(np.sum(val > opt))
            # hold-out: constant chosen on the other folds, applied to this fold
            hold_above = 0
            for k in range(folds):
                tr = ok & (fold != k)
                te = ok & (fold == k)
                if not tr.any() or not te.any():
                    continue
                if kind == "raw":
                    continue
                if kind == "add":
                    c_k = math.floor(float(np.min(opt[tr] - t[tr])) * 100) / 100
                    v_te = np.floor(t[te] + c_k + 1e-9)
                else:
                    r = (opt[tr] + 1) / t[tr]
                    r = r[np.isfinite(r) & (t[tr] > 0)]
                    if not len(r):
                        continue
                    c_k = _floor_sig(float(np.min(r)) * (1 - 1e-9))
                    v_te = np.floor(c_k * t[te] + 1e-9)
                hold_above += int(np.sum(v_te > opt[te]))
            g = gap_mask & ok
            rows.append({
                "formula": format_term(term), "term": json.dumps([list(x) for x in term]),
                "kind": kind, "const": const, "degree": len(term),
                "rows": int(ok.sum()), "above": above, "holdout_above": hold_above,
                "exceed_gap": float(np.mean(val[g] > lb[g])) if g.any() else 0.0,
                "tight_gap": float(np.mean(val[g] == opt[g])) if g.any() else 0.0,
                "shortfall_gap": float(np.mean(opt[g] - val[g])) if g.any() else float("nan"),
                "exceed_all": float(np.mean(val[ok] > lb[ok])),
                "tight_all": float(np.mean(val[ok] == opt[ok])),
                "shortfall_all": float(np.mean(opt[ok] - val[ok])),
                "beats_tw1_gap": float(np.mean(val[g] > tw1[g])) if g.any() else 0.0,
                "exceed_thm_gap": float(np.mean(val[g] > thm[g])) if g.any() else 0.0,
                "exceed_thm_all": float(np.mean(val[ok] > thm[ok])),
                "count_thm_all": int(np.sum(val[ok] > thm[ok])),
                "count_thm_gap": int(np.sum(val[g] > thm[g])) if g.any() else 0,
                "max_val_small": float(np.max(val[ok & small])) if (ok & small).any() else -1e6,
                "signature": hash(val[g].tobytes()) if g.any() else 0,
            })
    return rows


def distinct_survivors(cands: pd.DataFrame, top: int = 10, novel_only: bool = False,
                       attackable_only: bool = False) -> pd.DataFrame:
    """The leading survivors with distinct value vectors on the gap instances,
    the simplest formula first within a signature. `novel_only` keeps the ones
    that beat `max(lb_best, tw + 1)` somewhere; `attackable_only` the ones the
    n ≤ 15 adversary can test."""
    surv = cands[cands["survivor"]].copy()
    if novel_only and "novel" in surv.columns:
        surv = surv[surv["novel"]]
    if attackable_only and "attackable" in surv.columns:
        surv = surv[surv["attackable"]]
    surv = surv.sort_values(["exceed_gap", "tight_gap", "degree", "kind"],
                            ascending=[False, False, True, True])
    surv = surv.drop_duplicates("signature", keep="first")
    return surv.head(top).reset_index(drop=True)


def attack_set(cands: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """What the adversary is pointed at: the raw `tw1` theorem as a control
    (it must survive); the leading attackable, distinct survivors by `exceed_gap`
    (the plan's literal criterion, against `lb_best`); and every attackable
    survivor that beats the proved reference `max(lb_best, tw + 1)` on more
    than `KILL_EXCEED` of the gap instances (the honest criterion)."""
    control = cands[(cands["kind"] == "raw") & (cands["formula"] == "tw1")].head(1)
    literal = distinct_survivors(cands, top=top, attackable_only=True)
    honest = cands[cands["survivor"] & cands.get("attackable", True)
                   & (cands["exceed_thm_gap"] > KILL_EXCEED)]
    honest = honest.sort_values("exceed_thm_gap", ascending=False).drop_duplicates("signature")
    out = pd.concat([control, literal, honest], ignore_index=True)
    out["role"] = ["control"] * len(control) + ["literal"] * len(literal) + ["honest"] * len(honest)
    out = out.drop_duplicates(["formula", "kind"], keep="first").reset_index(drop=True)
    out.loc[out["role"].ne("control") & (out["exceed_thm_gap"] > KILL_EXCEED), "role"] = "honest"
    return out


def attack_set_large(cands: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """The supplementary set for `LARGE_SIZES`: the control, every fitted
    member of `attack_set` that is not pointwise ≤ tw + 1 on the gap instances
    (those are theorems restated and need no adversary), and the survivors
    that beat the proved reference on more than `KILL_EXCEED` of the gap
    instances but are vacuous at n ≤ 15 (`attackable` False)."""
    base = attack_set(cands, top=top)
    keep = (base["role"] == "control") | ((base["kind"] != "raw")
                                          & (base["novel"] | (base["beats_tw1_gap"] > 0)))
    vacuous = cands[cands["survivor"] & ~cands["attackable"] & (cands["exceed_thm_gap"] > KILL_EXCEED)]
    vacuous = vacuous.sort_values("exceed_thm_gap", ascending=False).drop_duplicates("signature").copy()
    vacuous["role"] = "honest, vacuous at n ≤ 15"
    out = pd.concat([base[keep], vacuous], ignore_index=True)
    return out.drop_duplicates(["formula", "kind"], keep="first").reset_index(drop=True)


# ----------------------------------------------------------------------------
# the adversary
# ----------------------------------------------------------------------------


def cand_from_row(row) -> dict:
    term = tuple((f, float(e)) for f, e in json.loads(row["term"]))
    return {"term": term, "kind": row["kind"], "const": float(row["const"]),
            "formula": row["formula"]}


def make_evaluate(cands: list[dict], solutions_dir: Path = SCRATCH_SOLUTIONS):
    """An `evaluate_fn` for `learning.extremal.local_search`: the optimum from
    the exact solver, the invariants, and `viol_<i>` = f_i(G) − optimum for
    every candidate. The objective the search climbs is one of the `viol_`."""
    from learning.extremal import instance_from_matrix, matrix_key
    from satisfiability.mosp_solver import solve_mosp_exact

    def evaluate(matrix, sol_dir=solutions_dir) -> dict:
        matrix = np.asarray(matrix, dtype=int)
        inst = instance_from_matrix(matrix, prefix="cj")
        sol_dir.mkdir(parents=True, exist_ok=True)
        optimum, ordering = solve_mosp_exact(inst, solutions_dir=sol_dir)
        inv = invariants(matrix, tw_deadline=5.0, expansion_budget=None)
        rec = {"key": matrix_key(matrix), "n": int(matrix.shape[0]), "m": int(matrix.shape[1]),
               "optimum": int(optimum), "edges": int(inv["edges"]),
               "witness": " ".join(str(v) for v in ordering)}
        for i, cand in enumerate(cands):
            rec[f"viol_{i}"] = candidate_value(inv, cand) - int(optimum)
        rec.update({k: v for k, v in inv.items() if k not in rec})
        return rec

    return evaluate


def _attack_job(args) -> dict:
    cand_rows, index, n, kind, restart, steps, solutions_dir = args
    from learning.extremal import bernoulli, gap_seed_matrices, local_search, subset_of, tree_of_cliques

    cands = [cand_from_row(r) for r in cand_rows]
    rng = np.random.default_rng([index, n, {"tree": 0, "bern": 1, "gap": 2}[kind], restart])
    if kind == "tree":
        seed = tree_of_cliques(n, rng)
    elif kind == "bern":
        seed = bernoulli(n, rng)
    else:
        pool = gap_seed_matrices()
        seed = subset_of(pool[rng.integers(len(pool))], n, rng) if pool else tree_of_cliques(n, rng)
    evaluate = make_evaluate(cands, Path(solutions_dir))
    res = local_search(seed, f"viol_{index}", steps, rng, solutions_dir=Path(solutions_dir),
                       evaluate_fn=evaluate)
    best = res["best"]
    return {"candidate": index, "formula": cands[index]["formula"], "n": n, "kind": kind,
            "restart": restart, "evaluations": res["evaluations"], "skipped": res["skipped"],
            "best_viol": int(best[f"viol_{index}"]), "best_key": best["key"],
            "best_optimum": int(best["optimum"]), "best_edges": int(best["edges"]),
            "max_trace": int(max(res["trace"]))}


def run_attack(survivors: pd.DataFrame, workers: int = 16, steps: int = 320,
               sizes=ATTACK_SIZES, restarts: int = 2, kinds=("tree", "bern", "gap"),
               solutions_dir: Path = SCRATCH_SOLUTIONS, out_csv: Path = ATTACK_CSV) -> pd.DataFrame:
    """`steps × |sizes| × |kinds| × restarts` oracle evaluations per survivor
    (10,240 at the defaults), the search climbing `f(G) − optimum`."""
    cand_rows = [dict(r) for _, r in survivors.iterrows()]
    jobs = [(cand_rows, i, n, kind, r, steps, str(solutions_dir))
            for i in range(len(cand_rows)) for n in sizes for kind in kinds for r in range(restarts)]
    jobs.sort(key=lambda j: -j[2])
    rows = []
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_attack_job, j) for j in jobs]
        for i, fut in enumerate(as_completed(futures), start=1):
            rows.append(fut.result())
            if i % 16 == 0 or i == len(futures):
                print(f"[conjecture] attack {i}/{len(futures)} in {time.monotonic() - started:.0f}s",
                      flush=True)
    out = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)
    return out


def attack_summary(attack: pd.DataFrame) -> pd.DataFrame:
    g = attack.groupby(["candidate", "formula"])
    out = g.agg(jobs=("n", "size"), evaluations=("evaluations", "sum"), skipped=("skipped", "sum"),
                max_viol=("best_viol", "max"), n_min=("n", "min"), n_max=("n", "max")).reset_index()
    broken = []
    for (c, f), part in g:
        bad = part[part["best_viol"] >= 1]
        if len(bad):
            bad = bad.sort_values(["n", "best_edges"])
            broken.append((c, int(bad.iloc[0]["n"]), bad.iloc[0]["best_key"]))
        else:
            broken.append((c, -1, ""))
    b = pd.DataFrame(broken, columns=["candidate", "counter_n", "counter_key"])
    out = out.merge(b, on="candidate")
    out["verdict"] = np.where(out["max_viol"] >= 1, "broken", "survived")
    return out.sort_values("candidate").reset_index(drop=True)


def recertify_counterexample(key: str, cand: dict, solutions_dir: Path = SCRATCH_SOLUTIONS) -> dict:
    """The exact solver, both refutation configurations, the lattice oracle
    (n ≤ 15), the pathwidth DP (n ≤ 18) and the candidate's value recomputed."""
    from learning.extremal import matrix_from_key, recertify

    out = recertify(key, solutions_dir)
    inv = invariants(matrix_from_key(key), tw_deadline=5.0, expansion_budget=None)
    out["candidate_value"] = candidate_value(inv, cand)
    out["violation"] = out["candidate_value"] - out["optimum"]
    out["invariants"] = {k: inv[k] for k in ("tw_lo", "omega", "exp", "blt1", "bct_pw", "hubs3",
                                             "art", "simplicial", "ct_pw", "edges", "n", "m")}
    return out


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _md(table: pd.DataFrame, floatfmt: str = ".3f") -> str:
    try:
        return table.to_markdown(index=False, floatfmt=floatfmt)
    except Exception:  # noqa: BLE001 - tabulate missing
        return table.to_string(index=False)


def band_of(n: pd.Series) -> pd.Series:
    bins = [0, 10, 20, 30, 40, 60, 75, 100, 134]
    labels = ["≤10", "11–20", "21–30", "31–40", "41–60", "61–75", "76–100", "101–134"]
    return pd.cut(n, bins=bins, labels=labels)


def theorem_table(frame: pd.DataFrame) -> pd.DataFrame:
    """The proved components, recomputed here, against the optimum and lb_best."""
    rows = []
    gap = frame[(frame["source"] == "corpus") & (frame["gap"] >= 2)]
    for name, label in (("tw1", "tw + 1 (exact where tw_exact)"), ("omega", "ω (clique)"),
                        ("contraction", "contraction degeneracy + 1"), ("exp", "expansion bound (cap 6)"),
                        ("blt1", "branch lemma + 1"), ("lb_best", "lb_best (solver)")):
        v = frame[name].astype(float)
        vg = gap[name].astype(float)
        rows.append({"bound": label, "above optimum (must be 0)": int((v > frame["optimum"]).sum()),
                     "tight, all": float((v == frame["optimum"]).mean()),
                     "> lb_best, all": float((v > frame["lb_best"]).mean()),
                     "tight, gap": float((vg == gap["optimum"]).mean()),
                     "> lb_best, gap": float((vg > gap["lb_best"]).mean()),
                     "mean shortfall, gap": float((gap["optimum"] - vg).mean())})
    return pd.DataFrame(rows)


def coverage_table(frame: pd.DataFrame) -> pd.DataFrame:
    f = frame.copy()
    f["band"] = band_of(f["n"])
    g = f.groupby(["source", "band"], observed=True)
    out = g.agg(instances=("optimum", "size"), tw_exact=("tw_exact", "mean"),
                exp_cap_mean=("exp_cap", "mean"), hubs3_any=("hubs3", lambda s: float((s > 0).mean())),
                pw_gt_tw=("tw_exact", lambda s: float("nan"))).reset_index()
    pgt = f[f["tw_exact"] == True].assign(x=lambda d: (d["optimum"] - 1) > d["tw_lo"])  # noqa: E712
    pgt = pgt.groupby(["source", "band"], observed=True)["x"].mean().rename("pw_gt_tw_among_exact").reset_index()
    out = out.drop(columns=["pw_gt_tw"]).merge(pgt, on=["source", "band"], how="left")
    return out


def residual_table(frame: pd.DataFrame) -> pd.DataFrame:
    """On the corpus gap ≥ 2 instances, by size band: how often exact/interval
    treewidth + 1 beats `lb_best`, is tight, and what is left over the best
    proved bound `max(lb_best, tw + 1)`."""
    gap = frame[(frame["source"] == "corpus") & (frame["gap"] >= 2)].copy()
    gap["thm"] = np.maximum(gap["lb_best"], gap["tw1"])
    gap["band"] = band_of(gap["n"])
    rows = []
    for band, d in list(gap.groupby("band", observed=True)) + [("all", gap)]:
        ex = d[d["tw_exact"] == True]  # noqa: E712
        rows.append({"band": str(band), "gap instances": len(d), "tw exact": int(len(ex)),
                     "pw > tw (among exact)": int(((ex["optimum"] - 1) > ex["tw_lo"]).sum()),
                     "tw+1 > lb_best": int((d["tw1"] > d["lb_best"]).sum()),
                     "tw+1 = optimum": int((d["tw1"] == d["optimum"]).sum()),
                     "mean optimum − lb_best": float((d["optimum"] - d["lb_best"]).mean()),
                     "mean optimum − max(lb_best, tw+1)": float((d["optimum"] - d["thm"]).mean()),
                     "residual 0 / 1 / 2 / ≥3": " / ".join(str(int(((d["optimum"] - d["thm"]) == r).sum()))
                                                          for r in (0, 1, 2)) + f" / {int(((d['optimum'] - d['thm']) >= 3).sum())}"})
    return pd.DataFrame(rows)


def novelty_table(frame: pd.DataFrame, cands: pd.DataFrame, top: int = 12) -> pd.DataFrame:
    """For the leading novel candidates: where exactly they beat
    `max(lb_best, tw + 1)` — how many rows, how many of those have exact
    treewidth, the smallest such n, the sources, and on how many of those rows
    the claim is above `tw_hi + 1` as well (a candidate that never is could be
    a treewidth bound in disguise; one that is has to be a pathwidth argument)."""
    from learning.formula_search import evaluate_terms

    thm = np.maximum(frame["lb_best"].to_numpy(float), frame["tw1"].to_numpy(float))
    exact = frame["tw_exact"].to_numpy(bool)
    tw_hi1 = frame["tw_hi"].to_numpy(float) + 1          # min-fill / decision-search upper bound on tw, + 1
    gap = ((frame["source"] == "corpus") & (frame["gap"] >= 2)).to_numpy()
    vals = {c: frame[c].astype(float).to_numpy() for c in INVARIANT_NAMES if c in frame.columns}
    nov = cands[cands["novel"]].sort_values(["exceed_thm_gap", "exceed_thm_all"], ascending=False)
    nov = nov.drop_duplicates("signature").head(top)
    rows = []
    for _, r in nov.iterrows():
        cand = cand_from_row(r)
        t = evaluate_terms(vals, [cand["term"]])[0]
        ok = np.isfinite(t)
        if cand["kind"] == "raw":
            v = np.floor(t + 1e-9)
        elif cand["kind"] == "add":
            v = np.floor(t + cand["const"] + 1e-9)
        else:
            v = np.floor(cand["const"] * t + 1e-9)
        v = np.where(ok, v, -1e6)
        b = v > thm
        rows.append({"formula": r["formula"], "kind": r["kind"], "const": r["const"],
                     "holdout_above": int(r["holdout_above"]),
                     "beats proved bound (rows)": int(b.sum()), "of which tw exact": int((b & exact).sum()),
                     "on gap instances": int((b & gap).sum()), "gap & tw exact": int((b & gap & exact).sum()),
                     "smallest n": int(frame["n"].to_numpy()[b].min()) if b.any() else -1,
                     "beat rows above tw_hi + 1": int((b & (v > tw_hi1)).sum()),
                     "sources": ", ".join(f"{k} {v_}" for k, v_ in frame.loc[b, "source"].value_counts().items()),
                     "attackable at n ≤ 15": bool(r["attackable"])})
    return pd.DataFrame(rows)


def novelty_summary(frame: pd.DataFrame, cands: pd.DataFrame) -> dict:
    """Over every novel candidate: rows where it beats the proved bound, split
    by treewidth exactness; how many candidates ever beat it on an exact row,
    and on more than 0.1% of the exact rows."""
    from learning.formula_search import evaluate_terms

    thm = np.maximum(frame["lb_best"].to_numpy(float), frame["tw1"].to_numpy(float))
    exact = frame["tw_exact"].to_numpy(bool)
    vals = {c: frame[c].astype(float).to_numpy() for c in INVARIANT_NAMES if c in frame.columns}
    nov = cands[cands["novel"]]
    per = []
    for _, r in nov.iterrows():
        cand = cand_from_row(r)
        t = evaluate_terms(vals, [cand["term"]])[0]
        ok = np.isfinite(t)
        if cand["kind"] == "raw":
            v = np.floor(t + 1e-9)
        elif cand["kind"] == "add":
            v = np.floor(t + cand["const"] + 1e-9)
        else:
            v = np.floor(cand["const"] * t + 1e-9)
        v = np.where(ok, v, -1e6)
        b = v > thm
        per.append((int(b.sum()), int((b & exact).sum())))
    per = np.array(per) if len(per) else np.zeros((0, 2), dtype=int)
    n_exact = int(exact.sum())
    return {"novel_candidates": int(len(nov)), "rows_with_exact_tw": n_exact, "rows": int(len(frame)),
            "beat_rows_total": int(per[:, 0].sum()) if len(per) else 0,
            "beat_rows_exact": int(per[:, 1].sum()) if len(per) else 0,
            "candidates_beating_on_exact": int((per[:, 1] > 0).sum()) if len(per) else 0,
            "candidates_beating_on_exact_over_0.1pct": int((per[:, 1] > 0.001 * n_exact).sum()) if len(per) else 0,
            "max_exact_beats_one_candidate": int(per[:, 1].max()) if len(per) else 0,
            "median_exact_beats_among_beaters": float(np.median(per[per[:, 1] > 0, 1])) if len(per) and (per[:, 1] > 0).any() else 0.0}


def write_tables(inv_csv: Path = INVARIANTS_CSV, cands_csv: Path = CANDIDATES_CSV,
                 attack_csv: Path = ATTACK_CSV, out: Path = TABLES, top: int = 25,
                 attack_large_csv: Path = ATTACK_LARGE_CSV) -> str:
    from learning.extremal import draw

    frame = load_table(inv_csv)
    cands = pd.read_csv(cands_csv)
    lines = ["# Conjecture mining for a branching-aware lower bound — tables (loop0003 item 09)", "",
             f"*Generated {time.strftime('%Y-%m-%d %H:%M')} by `python -m learning.conjecture --stage tables`.*", ""]
    lines += ["## Coverage", "", _md(coverage_table(frame)), ""]
    lines += ["## The proved components, recomputed", "", _md(theorem_table(frame)), ""]
    lines += ["## Candidate summary", ""]
    summ = cands.groupby("kind").agg(candidates=("formula", "size"), valid=("valid", "sum"),
                                     survivors=("survivor", "sum"),
                                     holdout_leak=("holdout_above", lambda s: int((s > 0).sum()))).reset_index()
    lines += [_md(summ), ""]
    lines += [f"## Leading valid candidates (by exceed on the gap instances; top {top})", ""]
    show = ["formula", "kind", "const", "rows", "above", "holdout_above", "exceed_gap", "tight_gap",
            "shortfall_gap", "beats_tw1_gap", "exceed_all", "tight_all", "shortfall_all"]
    lines += [_md(cands[cands["valid"]].head(top)[show]), ""]
    lines += ["## Distinct survivors (value vectors on the gap instances)", ""]
    surv = distinct_survivors(cands, top=top)
    lines += [_md(surv[show]) if len(surv) else "*none*", ""]
    lines += ["## The gap instances: what exact treewidth leaves over", "", _md(residual_table(frame)), ""]
    if "novel" in cands.columns:
        lines += ["## Novel candidates: where they beat `max(lb_best, tw + 1)`", "",
                  _md(novelty_table(frame, cands, top=12)), ""]
        summ_n = novelty_summary(frame, cands)
        lines += ["Over every novel candidate: " + "; ".join(f"{k} {v}" for k, v in summ_n.items()) + ".", ""]
    for label, csv, counter in (("The adversary at n ≤ 15", attack_csv, COUNTER_CSV),
                                ("The supplementary adversary at n ∈ {20, 25, 30}", attack_large_csv,
                                 COUNTER_LARGE_CSV)):
        if not csv.exists():
            continue
        attack = pd.read_csv(csv)
        lines += [f"## {label}", "", _md(attack_summary(attack)), ""]
        by_n = attack.groupby(["candidate", "formula", "n"])["best_viol"].max().unstack("n")
        lines += ["Best violation found by candidate and n (≥ 1 is a counterexample):", "",
                  _md(by_n.reset_index(), floatfmt=".0f"), ""]
        if counter.exists() and counter.stat().st_size > 1:
            ce = pd.read_csv(counter)
            lines += ["### Counterexamples, re-certified", "",
                      _md(ce[[c for c in ce.columns if c not in ("invariants",)]]), ""]
            for _, r in ce.iterrows():
                lines += [draw(r["key"], f"Smallest counterexample to `{r['formula']}`"), "",
                          f"invariants: {r.get('invariants', '')}", ""]
    text = "\n".join(lines)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", choices=("invariants", "repair", "mine", "attack", "attack-large",
                                            "tables", "all"), default="all")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sources", nargs="+", default=("corpus", "campaign", "upward"))
    parser.add_argument("--steps", type=int, default=320)
    parser.add_argument("--restarts", type=int, default=2)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--max-degree", type=int, default=2)
    parser.add_argument("--kinds", nargs="+", default=("tree", "bern", "gap"))
    args = parser.parse_args()
    os.environ.setdefault("OMP_NUM_THREADS", "1")

    if args.stage in ("invariants", "all"):
        run_invariants(workers=args.workers, limit=args.limit, sources=tuple(args.sources))
    if args.stage == "repair":
        repair_branching(workers=args.workers)
    if args.stage in ("mine", "all"):
        frame = load_table()
        cands = mine(frame, max_degree=args.max_degree)
        CANDIDATES_CSV.parent.mkdir(parents=True, exist_ok=True)
        cands.to_csv(CANDIDATES_CSV, index=False)
        surv = attack_set(cands, top=args.top)
        print(f"[conjecture] {len(cands)} candidates, {int(cands['valid'].sum())} valid, "
              f"{int(cands['survivor'].sum())} survivors, {int(cands['novel'].sum())} novel, "
              f"attack set {len(surv)} incl. the tw1 control", flush=True)
        print(surv[["role", "formula", "kind", "const", "exceed_gap", "exceed_thm_gap", "tight_gap",
                    "holdout_above", "max_val_small"]].to_string())
    if args.stage in ("attack", "all"):
        cands = pd.read_csv(CANDIDATES_CSV)
        surv = attack_set(cands, top=args.top)
        if len(surv):
            attack = run_attack(surv, workers=args.workers, steps=args.steps, restarts=args.restarts,
                                kinds=tuple(args.kinds))
            summ = attack_summary(attack)
            print(summ.to_string())
            counters = []
            for _, r in summ[summ["verdict"] == "broken"].iterrows():
                cand = cand_from_row(surv.iloc[int(r["candidate"])])
                cert = recertify_counterexample(r["counter_key"], cand)
                counters.append({"candidate": int(r["candidate"]), "formula": r["formula"],
                                 "key": r["counter_key"], **{k: v for k, v in cert.items()}})
            pd.DataFrame(counters).to_csv(COUNTER_CSV, index=False)
        else:
            print("[conjecture] no survivors to attack")
    if args.stage == "attack-large":
        cands = pd.read_csv(CANDIDATES_CSV)
        surv = attack_set_large(cands, top=args.top)
        print(surv[["role", "formula", "kind", "const", "exceed_gap", "exceed_thm_gap", "holdout_above"]].to_string())
        attack = run_attack(surv, workers=args.workers, steps=args.steps, restarts=args.restarts,
                            kinds=tuple(k for k in args.kinds if k != "gap"), sizes=LARGE_SIZES,
                            out_csv=ATTACK_LARGE_CSV)
        summ = attack_summary(attack)
        print(summ.to_string())
        counters = []
        for _, r in summ[summ["verdict"] == "broken"].iterrows():
            cand = cand_from_row(surv.iloc[int(r["candidate"])])
            cert = recertify_counterexample(r["counter_key"], cand)
            counters.append({"candidate": int(r["candidate"]), "formula": r["formula"],
                             "key": r["counter_key"], **{k: v for k, v in cert.items()}})
        pd.DataFrame(counters).to_csv(COUNTER_LARGE_CSV, index=False)
    if args.stage in ("tables", "all"):
        write_tables()
        print(f"[conjecture] wrote {TABLES}")


if __name__ == "__main__":
    main()
