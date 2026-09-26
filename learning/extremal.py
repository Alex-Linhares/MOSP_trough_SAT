"""Extremal search and exact treewidth: what are the worst small instances, and is
pathwidth − treewidth bounded? (plan 2 §2.7, loop0003 item 08)

Two questions, one engine.

1. **Extremal instances.** Local search over bit flips of the customer ×
   product matrix at n ≤ 15 (n ≤ 19 for the treewidth objective), with
   `solve_mosp_exact` as the oracle and `learning.treewidth` beside it, for
   five objectives:

   - `gap`        — `optimum − lb_best`, the proved bound's shortfall;
   - `pwtw`       — `(optimum − 1) − tw`, pathwidth minus *exact* treewidth;
   - `nodes`      — nodes the default search needs to refute `optimum − 1`;
   - `overshoot`  — `cs-dfs` upper bound minus the optimum;
   - `disagree`   — wrong answers among the four decisions `decide(optimum − 1)`
                    and `decide(optimum)` under the `default` and `csearch`
                    configurations (the soundness objective of §15).

   Seeds: random trees of cliques (products glued at hub customers), Bernoulli
   matrices, and random customer subsets of §6's ten smallest gap ≥ 2
   instances. Candidates are deduplicated by the canonical form of their MOSP
   graph (nauty when present, Weisfeiler–Leman otherwise), because every
   objective but the trivial bound is a function of the graph (§13). Ties are
   broken towards fewer edges, so the search drifts towards minimal examples.
   The baseline is the corpus's worst instance at the same n per objective;
   the kill criterion is that the search beats none of them.

2. **Exact treewidth.** For every corpus instance at n ≤ 20 the subset DP
   gives `tw` exactly, so `pw − tw` is exact there rather than a min-fill
   floor; for the 338 gap ≥ 2 instances the DP (n ≤ 26) or the decision
   search (n ≥ 27, with a deadline; a censored call is an interval) settles
   whether `pw > tw` — §6's 38.8% floor becomes a number.

Every certified value is re-established for the instances drawn: the exact
solver, a refutation of `optimum − 1` under both configurations, the lattice
oracle (`learning.degeneracy`) at n ≤ 15, and the exact pathwidth DP
(`fixed_parameter_algorithm.pathwidth`) at n ≤ 18; the treewidth carries an
elimination ordering a third party can re-check with `elimination_width`.

Generated instances are solved with a solutions directory under
`learning/data/extremal/` (git-ignored, regenerable); nothing is written to
`solutions/`. Nothing here is a bound; nothing reaches the solver.

Usage:
    python -m learning.extremal --stage corpus --workers 8            # exact treewidth over the corpus (~10 min)
    python -m learning.extremal --stage search --workers 8            # the local search (~20 min)
    python -m learning.extremal --stage tables                        # tables + drawings → reports/extremal_tables.md
    python -m learning.extremal --stage all --workers 16
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

from learning.treewidth import (
    elimination_width,
    masks_from_matrix,
    treewidth_bounded,
    treewidth_decide,
    treewidth_exact,
)
from mosp.instance import MOSPInstance

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "learning" / "data"
ENSEMBLE = DATA / "ensemble"
SCRATCH = DATA / "extremal"
SCRATCH_SOLUTIONS = SCRATCH / "solutions"
BEST_CSV = ENSEMBLE / "extremal_best.csv"
JOBS_CSV = ENSEMBLE / "extremal_jobs.csv"
TRACE_CSV = ENSEMBLE / "extremal_trace.csv.gz"
CORPUS_TW_CSV = ENSEMBLE / "extremal_corpus_tw.csv"
TABLES = ROOT / "reports" / "extremal_tables.md"
INSTANCES_CSV = DATA / "instances.csv"
NODE_COUNTS_CSV = DATA / "node_counts.csv"

OBJECTIVES = ("gap", "pwtw", "nodes", "overshoot", "disagree")
SEARCH_SIZES = tuple(range(8, 16))
PWTW_EXTRA_SIZES = (16, 17, 18, 19, 20)
CONFIGS = ("default", "csearch")
DP_MAX_N = 26


# ----------------------------------------------------------------------------
# the oracle
# ----------------------------------------------------------------------------


def matrix_key(matrix: np.ndarray) -> str:
    rows = ["".join(str(int(v)) for v in row) for row in np.asarray(matrix, dtype=int)]
    return "/".join(rows)


def matrix_from_key(key: str) -> np.ndarray:
    return np.array([[int(ch) for ch in row] for row in key.split("/")], dtype=int)


def instance_from_matrix(matrix: np.ndarray, prefix: str = "x") -> MOSPInstance:
    digest = hashlib.sha1(matrix_key(matrix).encode()).hexdigest()[:16]
    return MOSPInstance.from_matrix(np.asarray(matrix, dtype=int).tolist(), name=f"{prefix}_{digest}")


def graph_certificate(matrix: np.ndarray) -> str:
    """Canonical form of the MOSP graph: nauty when available, WL otherwise."""
    from learning.canonical import HAVE_NAUTY, nauty_graph_certificate, wl_hash

    masks = masks_from_matrix(matrix)
    adjacency = {i: [j for j in range(len(masks)) if masks[i] >> j & 1] for i in range(len(masks))}
    if HAVE_NAUTY:
        cert = nauty_graph_certificate(adjacency)
        if cert is not None:
            return cert
    return "wl:" + wl_hash(adjacency)


def lower_bounds(instance: MOSPInstance) -> dict:
    import networkx as nx

    from customer_inter.customer_graph import build_customer_graph
    from satisfiability.expansion_bound import mosp_lower_bound
    from satisfiability.mosp_solver import _contraction_degeneracy, _lower_bound

    m = np.asarray(instance.matrix, dtype=int)
    graph = build_customer_graph(instance)
    trivial = int(m.sum(axis=0).max()) if m.size else 0
    omega = max((len(c) for c in nx.find_cliques(graph)), default=0) if graph.number_of_nodes() else 0
    contraction = int(_contraction_degeneracy(graph) + 1) if graph.number_of_nodes() else 0
    expansion = int(mosp_lower_bound(instance, max_t=8, time_budget=None))
    solver = int(_lower_bound(instance, clique_budget=1.0))
    return {"lb_trivial": trivial, "lb_clique": int(omega), "lb_contraction": contraction,
            "lb_expansion": expansion, "lb_solver": solver,
            "lb_best": max(trivial, omega, contraction, expansion, solver),
            "edges": int(graph.number_of_edges())}


def evaluate(matrix: np.ndarray, solutions_dir: Path = SCRATCH_SOLUTIONS,
             with_tw: bool = True) -> dict:
    """Every objective for one matrix, from the oracle and nothing cached but
    the witness. The optimum is `solve_mosp_exact`'s, re-simulated by it."""
    from learning.node_counts import refutation_kwargs
    from satisfiability.customer_search import decide
    from satisfiability.heuristics import upper_bound
    from satisfiability.mosp_solver import solve_mosp_exact

    matrix = np.asarray(matrix, dtype=int)
    inst = instance_from_matrix(matrix)
    solutions_dir.mkdir(parents=True, exist_ok=True)
    stats: dict = {}
    optimum, ordering = solve_mosp_exact(inst, solutions_dir=solutions_dir, stats=stats)
    rec = {"key": matrix_key(matrix), "n": int(matrix.shape[0]), "m": int(matrix.shape[1]),
           "ones": int(matrix.sum()), "optimum": int(optimum),
           "witness": " ".join(str(v) for v in ordering)}
    rec.update(lower_bounds(inst))
    statuses = {}
    nodes = {}
    for config in CONFIGS:
        kwargs = refutation_kwargs(inst, config)
        lo = decide(inst, optimum - 1, **kwargs)
        hi = decide(inst, optimum, **kwargs)
        statuses[config] = (lo.status, hi.status)
        nodes[config] = (int(lo.nodes), int(hi.nodes))
    rec["nodes_default"] = nodes["default"][0]
    rec["nodes_csearch"] = nodes["csearch"][0]
    rec["nodes_hi_default"] = nodes["default"][1]
    rec["status_lo_default"], rec["status_hi_default"] = statuses["default"]
    rec["status_lo_csearch"], rec["status_hi_csearch"] = statuses["csearch"]
    wrong = sum(1 for c in CONFIGS for i, want in enumerate(("unsat", "sat"))
                if statuses[c][i] != want)
    rec["disagree"] = int(wrong)
    rec["ub_cs_dfs"] = int(upper_bound(inst, "cs-dfs")[0])
    rec["overshoot"] = rec["ub_cs_dfs"] - optimum
    rec["gap"] = optimum - rec["lb_best"]
    if with_tw and matrix.shape[0] <= DP_MAX_N:
        tw, order = treewidth_exact(masks_from_matrix(matrix))
        rec["tw"] = int(tw)
        rec["tw_order"] = " ".join(str(v) for v in order)
        rec["pwtw"] = (optimum - 1) - tw
    else:
        rec["tw"] = -1
        rec["tw_order"] = ""
        rec["pwtw"] = -99
    rec["nodes"] = rec["nodes_default"]
    return rec


def score(rec: dict, objective: str) -> tuple:
    """Primary the objective, secondary fewer edges (towards minimal examples)."""
    return (rec[objective], -rec["edges"])


# ----------------------------------------------------------------------------
# seeds and moves
# ----------------------------------------------------------------------------


def tree_of_cliques(n: int, rng: np.random.Generator, extra_columns: int = 2) -> np.ndarray:
    """Products as cliques glued at hub customers until every customer is
    covered; a tree of cliques with branching, §6's bound-defeating family."""
    order = list(rng.permutation(n))
    first = int(rng.integers(2, min(5, n) + 1))
    used = order[:first]
    rest = order[first:]
    products = [set(used)]
    while rest:
        hubs = {int(rng.choice(used))}
        if rng.random() < 0.3 and len(used) > 1:
            hubs.add(int(rng.choice(used)))
        size = int(rng.integers(2, 6))
        fresh = rest[:max(1, size - len(hubs))]
        rest = rest[len(fresh):]
        products.append(set(hubs) | set(fresh))
        used.extend(fresh)
    m = len(products) + extra_columns
    matrix = np.zeros((n, m), dtype=int)
    for j, prod in enumerate(products):
        for c in prod:
            matrix[c, j] = 1
    return matrix


def bernoulli(n: int, rng: np.random.Generator) -> np.ndarray:
    p = float(rng.uniform(0.12, 0.35))
    m = int(rng.choice([n, n + n // 2]))
    matrix = (rng.random((n, m)) < p).astype(int)
    for j in range(m):                        # no empty products
        if matrix[:, j].sum() == 0:
            matrix[rng.integers(n), j] = 1
    return matrix


def subset_of(matrix: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """A random n-customer subset of a larger instance, columns with < 1 one dropped."""
    matrix = np.asarray(matrix, dtype=int)
    rows = np.sort(rng.choice(matrix.shape[0], size=n, replace=False))
    sub = matrix[rows]
    keep = sub.sum(axis=0) >= 1
    sub = sub[:, keep]
    if sub.shape[1] < 2:
        sub = np.hstack([sub, np.zeros((n, 2 - sub.shape[1]), dtype=int)])
    return sub


def mutate(matrix: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Flip one bit (70%), two bits (20%), or move a one within its column (10%)."""
    out = matrix.copy()
    n, m = out.shape
    r = rng.random()
    flips = 1 if r < 0.7 else 2 if r < 0.9 else 0
    if flips:
        for _ in range(flips):
            i, j = int(rng.integers(n)), int(rng.integers(m))
            out[i, j] ^= 1
    else:
        j = int(rng.integers(m))
        ones = np.flatnonzero(out[:, j])
        zeros = np.flatnonzero(out[:, j] == 0)
        if len(ones) and len(zeros):
            out[int(rng.choice(ones)), j] = 0
            out[int(rng.choice(zeros)), j] = 1
        else:
            out[int(rng.integers(n)), j] ^= 1
    return out


def gap_seed_matrices() -> list[np.ndarray]:
    """§6's ten smallest gap ≥ 2 corpus instances, as matrices (empty if the
    feature table is missing)."""
    try:
        from learning.bound_gap import find_instances, smallest_gap_instances, with_gap
        from learning.fingerprint import load_table

        frame = with_gap(load_table())
        ten = smallest_gap_instances(frame)
        return [np.asarray(inst.matrix, dtype=int) for inst in find_instances(ten)]
    except Exception as exc:                  # pragma: no cover - environment
        print(f"no corpus seeds: {exc}", file=sys.stderr)
        return []


# ----------------------------------------------------------------------------
# the local search
# ----------------------------------------------------------------------------


def local_search(seed: np.ndarray, objective: str, steps: int, rng: np.random.Generator,
                 solutions_dir: Path = SCRATCH_SOLUTIONS, patience: int = 60,
                 seen: set | None = None, evaluate_fn=evaluate) -> dict:
    """Hill climbing with sideways moves over bit flips, canonical dedupe, and
    a kick back to the incumbent after `patience` non-improving steps.
    Returns the best record, the trace of objective values, and counts."""
    seen = set() if seen is None else seen
    cert = graph_certificate(seed)
    seen.add(cert)
    cur = evaluate_fn(seed, solutions_dir)
    best = cur
    trace = [cur[objective]]
    stale = 0
    skipped = 0
    evaluations = 1
    consecutive_skips = 0
    while evaluations < steps and consecutive_skips < 20 * patience:
        # `steps` counts oracle evaluations; a canonical duplicate costs no
        # evaluation, and after `patience` of them in a row the search kicks
        # away from the incumbent (up to three flips) to leave the basin
        cand = mutate(cur_matrix(cur), rng)
        if consecutive_skips >= patience:
            cand = kick(cur_matrix(cur if rng.random() < 0.5 else best), rng,
                        flips=2 + consecutive_skips // patience)
        cert = graph_certificate(cand)
        if cert in seen:
            skipped += 1
            consecutive_skips += 1
            continue
        consecutive_skips = 0
        seen.add(cert)
        rec = evaluate_fn(cand, solutions_dir)
        evaluations += 1
        trace.append(rec[objective])
        if score(rec, objective) >= score(cur, objective):
            if score(rec, objective) > score(cur, objective):
                stale = 0
            else:
                stale += 1
            cur = rec
        else:
            stale += 1
        if score(rec, objective) > score(best, objective):
            best = rec
            stale = 0
        if stale > patience:
            cur = best
            stale = 0
    return {"best": best, "trace": trace, "evaluations": evaluations, "skipped": skipped}


def cur_matrix(rec: dict) -> np.ndarray:
    return matrix_from_key(rec["key"])


def kick(matrix: np.ndarray, rng: np.random.Generator, flips: int = 3) -> np.ndarray:
    flips = min(flips, 8)
    out = matrix.copy()
    for _ in range(flips):
        out = mutate(out, rng)
    return out


def _search_job(args) -> dict:
    objective, n, kind, index, steps, seed_key, solutions_dir, patience = args
    rng = np.random.default_rng([OBJECTIVES.index(objective), n, index, steps,
                                 {"toc": 1, "bern": 2, "corpus": 3}[kind]])
    if kind == "toc":
        seed = tree_of_cliques(n, rng)
    elif kind == "bern":
        seed = bernoulli(n, rng)
    else:
        seed = subset_of(matrix_from_key(seed_key), n, rng)
    started = time.monotonic()
    out = local_search(seed, objective, steps, rng, Path(solutions_dir), patience=patience)
    best = out["best"]
    return {"objective": objective, "n": n, "kind": kind, "index": index, "steps": steps,
            "seed_key": seed_key,
            "evaluations": out["evaluations"], "skipped": out["skipped"],
            "seconds": round(time.monotonic() - started, 2),
            "best_value": best[objective], "best_key": best["key"],
            "trace": " ".join(str(v) for v in out["trace"]), "best": best}


def search_jobs(objectives=OBJECTIVES, sizes=SEARCH_SIZES, extra_sizes=PWTW_EXTRA_SIZES,
                restarts: tuple[int, int, int] = (5, 3, 4), steps: int = 400,
                corpus_seeds: list[np.ndarray] | None = None,
                solutions_dir: Path = SCRATCH_SOLUTIONS) -> list[tuple]:
    corpus_seeds = corpus_seeds or []
    jobs = []
    for objective in objectives:
        this_sizes = tuple(sizes) + (tuple(extra_sizes) if objective == "pwtw" else ())
        for n in this_sizes:
            for i in range(restarts[0]):
                jobs.append((objective, n, "toc", i, steps, "", str(solutions_dir)))
            for i in range(restarts[1]):
                jobs.append((objective, n, "bern", i, steps, "", str(solutions_dir)))
            if corpus_seeds:
                for i in range(restarts[2]):
                    seed = corpus_seeds[i % len(corpus_seeds)]
                    if seed.shape[0] < n:
                        continue
                    jobs.append((objective, n, "corpus", i, steps, matrix_key(seed), str(solutions_dir)))
    return jobs


def run_search(workers: int, steps: int, restarts=(5, 3, 4), sizes=SEARCH_SIZES,
               extra_sizes=PWTW_EXTRA_SIZES, objectives=OBJECTIVES,
               jobs_csv: Path = JOBS_CSV, trace_csv: Path = TRACE_CSV,
               solutions_dir: Path = SCRATCH_SOLUTIONS, seed_keys: list[str] | None = None,
               patience: int = 60) -> pd.DataFrame:
    seeds = [matrix_from_key(k) for k in seed_keys] if seed_keys else gap_seed_matrices()
    jobs = search_jobs(objectives, sizes, extra_sizes, restarts, steps, seeds, solutions_dir)
    jobs = [j + (patience,) for j in jobs]
    # heaviest first: large n, then the nodes objective
    jobs.sort(key=lambda j: (-j[1], j[0] != "nodes"))
    print(f"{len(jobs)} search jobs, {steps} steps each, {workers} workers", flush=True)
    rows = []
    traces = []
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_search_job, j) for j in jobs]
        for done, fut in enumerate(as_completed(futures), 1):
            out = fut.result()
            best = out.pop("best")
            trace = out.pop("trace")
            row = dict(out)
            row.update({f"best_{k}": v for k, v in best.items() if k not in ("key",)})
            rows.append(row)
            traces.append({"objective": out["objective"], "n": out["n"], "kind": out["kind"],
                           "index": out["index"], "trace": trace})
            if done % 20 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)} jobs, {time.monotonic() - started:.0f} s", flush=True)
    frame = pd.DataFrame(rows).sort_values(["objective", "n", "kind", "index"]).reset_index(drop=True)
    frame.to_csv(jobs_csv, index=False)
    pd.DataFrame(traces).to_csv(trace_csv, index=False, compression="gzip")
    return frame


# ----------------------------------------------------------------------------
# the corpus: exact treewidth
# ----------------------------------------------------------------------------


def corpus_frame() -> pd.DataFrame:
    from learning.bound_gap import with_gap
    from learning.fingerprint import load_table

    return with_gap(load_table())


def _corpus_instances(frame: pd.DataFrame) -> list[tuple[pd.Series, MOSPInstance]]:
    from learning.bound_gap import find_instances

    insts = find_instances(frame)
    return list(zip((row for _, row in frame.iterrows()), insts))


def _tw_job(args) -> dict:
    name, source, n, optimum, gap, key, deadline = args
    matrix = matrix_from_key(key)
    masks = masks_from_matrix(matrix)
    pw = int(optimum) - 1
    rec = {"instance_name": name, "source_file": source, "n_customers": int(n),
           "optimum": int(optimum), "gap": int(gap), "pw": pw}
    started = time.monotonic()
    if len(masks) <= DP_MAX_N:
        tw, order = treewidth_exact(masks)
        rec.update({"tw_lo": tw, "tw_hi": tw, "tw_exact": True, "method": "dp",
                    "nodes": 0, "censored": False,
                    "order_width": elimination_width(masks, order)})
    elif len(masks) > 64:
        # beyond the decision search's word: heuristic bounds only, never an answer
        from learning.treewidth import min_fill_upper_bound, mmd_lower_bound

        hi, order = min_fill_upper_bound(masks)
        lo = mmd_lower_bound(masks)
        hi = min(hi, pw)
        rec.update({"tw_lo": int(lo), "tw_hi": int(hi), "tw_exact": bool(lo == hi), "method": "heuristic",
                    "nodes": 0, "censored": True, "order_width": elimination_width(masks, order)})
    else:
        # the question §6 left open first: tw ≤ pw − 1?
        status, order, nodes = treewidth_decide(masks, pw - 1, budget=20_000_000)
        remaining = max(1.0, deadline - (time.monotonic() - started))
        bb = treewidth_bounded(masks, remaining)
        lo, hi = bb["lo"], bb["hi"]
        if status == "yes":
            hi = min(hi, pw - 1)
        elif status == "no":
            lo = max(lo, pw)
        hi = min(hi, pw)                       # tw ≤ pw always
        rec.update({"tw_lo": int(lo), "tw_hi": int(hi), "tw_exact": bool(lo == hi), "method": "bb",
                    "nodes": int(nodes + bb["nodes"]), "censored": bool(bb["censored"] or status == "unknown"),
                    "order_width": elimination_width(masks, order) if order else bb["hi"]})
    rec["pw_gt_tw"] = ("yes" if rec["tw_hi"] < pw else "no" if rec["tw_lo"] >= pw else "open")
    rec["pwtw_lo"] = pw - rec["tw_hi"]
    rec["pwtw_hi"] = pw - rec["tw_lo"]
    rec["seconds"] = round(time.monotonic() - started, 3)
    return rec


def run_corpus(workers: int, max_n_all: int = 20, deadline: float = 60.0,
               out_csv: Path = CORPUS_TW_CSV) -> pd.DataFrame:
    """Exact treewidth for every corpus instance at n ≤ `max_n_all` and for
    every gap ≥ 2 instance at any size (DP to 26, decision search above)."""
    frame = corpus_frame()
    wanted = frame[(frame["n_customers"] <= max_n_all) | (frame["gap"] >= 2)]
    wanted = wanted.drop_duplicates(["instance_name", "source_file"])
    print(f"{len(wanted)} corpus instances for exact treewidth "
          f"({(wanted['n_customers'] <= max_n_all).sum()} at n ≤ {max_n_all}, "
          f"{(wanted['gap'] >= 2).sum()} with gap ≥ 2)", flush=True)
    pairs = _corpus_instances(wanted)
    jobs = [(row["instance_name"], row["source_file"], row["n_customers"], row["optimum"], row["gap"],
             matrix_key(np.asarray(inst.matrix)), deadline) for row, inst in pairs]
    jobs.sort(key=lambda j: -j[2])
    rows = []
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_tw_job, j) for j in jobs]
        for done, fut in enumerate(as_completed(futures), 1):
            rows.append(fut.result())
            if done % 500 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)}, {time.monotonic() - started:.0f} s", flush=True)
    out = pd.DataFrame(rows).sort_values(["n_customers", "instance_name"]).reset_index(drop=True)
    out.to_csv(out_csv, index=False)
    return out


# ----------------------------------------------------------------------------
# baselines, re-certification, tables
# ----------------------------------------------------------------------------


def corpus_baselines(frame: pd.DataFrame, corpus_tw: pd.DataFrame | None,
                     node_counts: Path = NODE_COUNTS_CSV) -> pd.DataFrame:
    """The corpus's worst instance at each n per objective."""
    rows = []
    frame = frame.copy()
    frame["overshoot"] = frame["ub_cs_dfs"] - frame["optimum"]
    nodes = pd.read_csv(node_counts) if node_counts.exists() else None
    for n, grp in frame.groupby("n_customers"):
        row = {"n": int(n), "instances": len(grp),
               "gap": int(grp["gap"].max()), "overshoot": int(grp["overshoot"].max()),
               "disagree": 0}
        if nodes is not None:
            sub = nodes[(nodes["n_customers"] == n) & (nodes["config"] == "default")]
            row["nodes"] = int(sub["nodes"].max()) if len(sub) else -1
        if corpus_tw is not None:
            sub = corpus_tw[(corpus_tw["n_customers"] == n) & corpus_tw["tw_exact"]]
            row["pwtw"] = int((sub["pw"] - sub["tw_lo"]).max()) if len(sub) else -99
            row["pwtw_instances"] = len(sub)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("n").reset_index(drop=True)


def best_per_cell(jobs: pd.DataFrame) -> pd.DataFrame:
    """The best record per (objective, n) over every job, distinct by key."""
    rows = []
    for (objective, n), grp in jobs.groupby(["objective", "n"]):
        grp = grp.copy()
        grp["_score"] = list(zip(grp["best_value"], -grp["best_edges"]))
        top = grp.sort_values("_score", ascending=False).iloc[0]
        active = int((matrix_from_key(top["best_key"]).sum(axis=1) > 0).sum())
        rows.append({"objective": objective, "n": int(n), "value": top["best_value"], "n_active": active,
                     "kind": top["kind"], "key": top["best_key"], "optimum": int(top["best_optimum"]),
                     "lb_best": int(top["best_lb_best"]), "tw": int(top["best_tw"]),
                     "edges": int(top["best_edges"]), "m": int(top["best_m"]), "ones": int(top["best_ones"]),
                     "nodes_default": int(top["best_nodes_default"]), "ub_cs_dfs": int(top["best_ub_cs_dfs"]),
                     "disagree": int(top["best_disagree"]), "witness": top["best_witness"],
                     "tw_order": top["best_tw_order"],
                     "evaluations": int(grp["evaluations"].sum()), "skipped": int(grp["skipped"].sum()),
                     "seconds": float(grp["seconds"].sum())})
    return pd.DataFrame(rows).sort_values(["objective", "n"]).reset_index(drop=True)


def recertify(key: str, solutions_dir: Path = SCRATCH_SOLUTIONS) -> dict:
    """Independent re-establishment of one drawn instance's values: the exact
    solver (cached witness re-simulated), both refutation configurations at
    `optimum − 1` and `optimum`, the lattice oracle at n ≤ 15, the exact
    pathwidth DP at n ≤ 18, and the treewidth ordering's width recomputed."""
    from learning.degeneracy import Compact, closing_weights, lattice_minimum
    from learning.node_counts import refutation_kwargs
    from satisfiability.customer_search import decide
    from satisfiability.mosp_solver import solve_mosp_exact

    matrix = matrix_from_key(key)
    inst = instance_from_matrix(matrix)
    optimum, ordering = solve_mosp_exact(inst, solutions_dir=solutions_dir)
    out = {"optimum": int(optimum)}
    for config in CONFIGS:
        kwargs = refutation_kwargs(inst, config)
        out[f"lo_{config}"] = decide(inst, optimum - 1, **kwargs).status
        out[f"hi_{config}"] = decide(inst, optimum, **kwargs).status
    n = matrix.shape[0]
    if n <= 15:
        comp = Compact(inst)
        out["lattice"] = int(lattice_minimum(closing_weights(comp)[1], comp.a)) if comp.a else 0
    if n <= 18:
        import networkx as nx

        from customer_inter.customer_graph import build_customer_graph
        from fixed_parameter_algorithm.pathwidth import compute_pathwidth

        graph = build_customer_graph(inst)
        pw = 0
        for comp_nodes in nx.connected_components(graph):
            sub = nx.convert_node_labels_to_integers(graph.subgraph(comp_nodes))
            pw = max(pw, compute_pathwidth(sub)[0])
        out["pathwidth_dp"] = int(pw)
    masks = masks_from_matrix(matrix)
    tw, order = treewidth_exact(masks)
    out["tw"] = int(tw)
    out["tw_order_width"] = int(elimination_width(masks, order))
    out["agree"] = bool(
        all(out[f"lo_{c}"] == "unsat" and out[f"hi_{c}"] == "sat" for c in CONFIGS)
        and out.get("lattice", optimum) == optimum
        and out.get("pathwidth_dp", optimum - 1) == optimum - 1
        and out["tw_order_width"] == tw)
    return out


def draw(key: str, title: str) -> str:
    matrix = matrix_from_key(key)
    masks = masks_from_matrix(matrix)
    degrees = sorted((bin(m).count("1") for m in masks), reverse=True)
    lines = [f"**{title}** — {matrix.shape[0]} customers × {matrix.shape[1]} products, "
             f"{int(matrix.sum())} ones; MOSP graph {sum(degrees) // 2} edges, degrees "
             f"{', '.join(map(str, degrees))}.", "", "```"]
    lines.extend(" ".join(str(v) for v in row) for row in matrix.tolist())
    lines.append("```")
    return "\n".join(lines)


def core_key(key: str) -> str:
    """The same instance without the customers isolated in its MOSP graph and
    the products then empty: the search keeps n fixed, so its draws can carry
    idle vertices, and an isolated vertex changes neither pathwidth nor
    treewidth."""
    matrix = matrix_from_key(key)
    masks = masks_from_matrix(matrix)
    matrix = matrix[[m != 0 for m in masks]]      # isolated in the MOSP graph: no neighbour
    if matrix.shape[0] == 0:
        return key
    matrix = matrix[:, matrix.sum(axis=0) > 0]
    if matrix.shape[1] == 0:
        matrix = np.zeros((matrix.shape[0], 1), dtype=int)
    return matrix_key(matrix)


def proof_block(key: str, solutions_dir: Path = SCRATCH_SOLUTIONS) -> tuple[dict, str]:
    """The checkable pieces of `pw − tw` for one instance: the clique number
    (tw ≥ ω − 1, a K_ω anyone can find), an elimination ordering of width tw
    (tw ≤ that width, recomputed by `elimination_width`), and pathwidth from
    three independent routes (the certified optimum minus one, the exact
    pathwidth DP, the lattice oracle)."""
    import networkx as nx

    matrix = matrix_from_key(key)
    masks = masks_from_matrix(matrix)
    n = len(masks)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((i, j) for i in range(n) for j in range(i + 1, n) if masks[i] >> j & 1)
    omega = max(len(c) for c in nx.find_cliques(g)) if n else 0
    cert = recertify(key, solutions_dir)
    tw, order = treewidth_exact(masks)
    facts = {"n": n, "omega": omega, "tw": tw, "tw_order": order, "tw_order_width": elimination_width(masks, order),
             "optimum": cert["optimum"], "pathwidth_dp": cert.get("pathwidth_dp"), "lattice": cert.get("lattice"),
             "pw": cert["optimum"] - 1, "pwtw": cert["optimum"] - 1 - tw, "agree": cert["agree"],
             "tw_lower_by_clique": bool(omega - 1 == tw), "components": nx.number_connected_components(g),
             "degrees": sorted((d for _, d in g.degree()), reverse=True)}
    lines = [f"- treewidth **{tw}**: ≥ {omega - 1} because the MOSP graph contains K{omega} "
             f"({'so the lower half is a clique anyone can check' if omega - 1 == tw else 'the subset DP proves the rest'}); "
             f"≤ {facts['tw_order_width']} by the elimination ordering `{' '.join(map(str, order))}` "
             f"(width recomputed by `elimination_width`).",
             f"- pathwidth **{facts['pw']}**: the certified optimum {cert['optimum']} minus one "
             f"(`decide({cert['optimum'] - 1})` {cert['lo_default']} / {cert['lo_csearch']} and "
             f"`decide({cert['optimum']})` {cert['hi_default']} / {cert['hi_csearch']} under `default` / `csearch`)"
             + (f"; the exact pathwidth DP says {cert['pathwidth_dp']}" if cert.get("pathwidth_dp") is not None else "")
             + (f"; the lattice oracle says optimum {cert['lattice']}" if cert.get("lattice") is not None else "") + ".",
             f"- so **pw − tw = {facts['pwtw']}** on {n} vertices, {g.number_of_edges()} edges, "
             f"{facts['components']} component(s), degrees {', '.join(map(str, facts['degrees']))}."]
    return facts, "\n".join(lines)


def _md(table: pd.DataFrame, floatfmt: str = ".3f") -> str:
    """Markdown with integral float columns shown as integers and NaN as —."""
    table = table.copy()
    for col in table.columns:
        if pd.api.types.is_float_dtype(table[col]):
            vals = table[col].dropna()
            if len(vals) and (vals == vals.round()).all():
                table[col] = table[col].map(lambda v: "—" if pd.isna(v) else str(int(v)))
    return table.to_markdown(index=False, floatfmt=floatfmt).replace(" nan ", "  —  ")


def kill_verdict(best: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    """Per objective and n: the search's best against the corpus's worst."""
    rows = []
    for _, row in best.iterrows():
        base = baseline[baseline["n"] == row["n"]]
        corpus_worst = int(base[row["objective"]].iloc[0]) if len(base) and row["objective"] in base else None
        rows.append({"objective": row["objective"], "n": int(row["n"]), "search best": row["value"],
                     "corpus worst": corpus_worst,
                     "beats corpus": ("no corpus instance" if corpus_worst is None
                                      else "yes" if row["value"] > corpus_worst else "no"),
                     "corpus instances": int(base["instances"].iloc[0]) if len(base) else 0,
                     "evaluations": int(row["evaluations"])})
    return pd.DataFrame(rows)


def pwtw_growth(best: pd.DataFrame, corpus_tw: pd.DataFrame | None) -> pd.DataFrame:
    rows = []
    sizes = sorted(set(best[best["objective"] == "pwtw"]["n"]) | (set(corpus_tw["n_customers"]) if corpus_tw is not None else set()))
    for n in sizes:
        row = {"n": int(n)}
        s = best[(best["objective"] == "pwtw") & (best["n"] == n)]
        row["search max pw − tw"] = int(s["value"].iloc[0]) if len(s) else None
        if corpus_tw is not None:
            c = corpus_tw[(corpus_tw["n_customers"] == n)]
            exact = c[c["tw_exact"]]
            row["corpus instances (exact tw)"] = len(exact)
            row["corpus max pw − tw"] = int((exact["pw"] - exact["tw_lo"]).max()) if len(exact) else None
            row["corpus with pw − tw ≥ 1"] = int(((exact["pw"] - exact["tw_lo"]) >= 1).sum())
            row["corpus with pw − tw ≥ 2"] = int(((exact["pw"] - exact["tw_lo"]) >= 2).sum())
        rows.append(row)
    return pd.DataFrame(rows)


def floor_table(corpus_tw: pd.DataFrame) -> pd.DataFrame:
    """§6's floor (38.8% of gap ≥ 2 with pw > tw certified by min-fill) as a number."""
    gap2 = corpus_tw[corpus_tw["gap"] >= 2]
    bands = ((20, 20), (21, 30), (31, 60), (61, 200))
    rows = []
    for lo, hi in bands + ((0, 200),):
        sub = gap2[(gap2["n_customers"] >= lo) & (gap2["n_customers"] <= hi)]
        if not len(sub):
            continue
        rows.append({"customers": f"{lo}–{hi}" if lo != 0 else "all",
                     "gap ≥ 2 instances": len(sub),
                     "tw exact": int(sub["tw_exact"].sum()),
                     "pw > tw": int((sub["pw_gt_tw"] == "yes").sum()),
                     "pw = tw": int((sub["pw_gt_tw"] == "no").sum()),
                     "open": int((sub["pw_gt_tw"] == "open").sum()),
                     "pw − tw ≥ 2": int((sub["pwtw_lo"] >= 2).sum()),
                     "max pw − tw (exact)": int((sub[sub["tw_exact"]]["pw"] - sub[sub["tw_exact"]]["tw_lo"]).max()) if sub["tw_exact"].any() else None,
                     "mean seconds": round(float(sub["seconds"].mean()), 2)})
    return pd.DataFrame(rows)


def write_tables(jobs_csv: Path = JOBS_CSV, corpus_csv: Path = CORPUS_TW_CSV,
                 best_csv: Path = BEST_CSV, out: Path = TABLES,
                 solutions_dir: Path = SCRATCH_SOLUTIONS) -> dict:
    jobs = pd.concat([pd.read_csv(p) for p in sorted(jobs_csv.parent.glob(jobs_csv.stem + "*.csv"))],
                     ignore_index=True)
    corpus_tw = pd.read_csv(corpus_csv) if corpus_csv.exists() else None
    frame = corpus_frame()
    baseline = corpus_baselines(frame, corpus_tw)
    best = best_per_cell(jobs)
    certs = []
    for _, row in best.iterrows():
        cert = recertify(row["key"], solutions_dir)
        cert.update({"objective": row["objective"], "n": int(row["n"])})
        certs.append(cert)
    certs = pd.DataFrame(certs)
    best = best.merge(certs.rename(columns={"optimum": "recert_optimum", "tw": "recert_tw"}),
                      on=["objective", "n"], how="left")
    best.to_csv(best_csv, index=False)
    verdict = kill_verdict(best, baseline)
    growth = pwtw_growth(best, corpus_tw)
    parts = ["# Extremal search and exact treewidth — tables (loop0003 item 08)", "",
             f"*Regenerate: `python -m learning.extremal --stage tables`. {len(jobs)} search jobs, "
             f"{int(jobs['evaluations'].sum()):,} oracle evaluations, {int(jobs['skipped'].sum()):,} "
             f"canonical duplicates skipped, {jobs['seconds'].sum() / 3600:.2f} core-hours.*", ""]
    parts += ["## Kill test: the search's best against the corpus's worst at the same n", "", _md(verdict), ""]
    parts += ["## Per objective and n: the best instance drawn", "",
              _md(best[["objective", "n", "n_active", "value", "kind", "m", "ones", "edges", "optimum", "lb_best", "tw",
                        "nodes_default", "ub_cs_dfs", "disagree", "evaluations", "skipped"]]), ""]
    parts += ["## Re-certification of every drawn instance", "",
              _md(certs[[c for c in certs.columns if c not in ("objective", "n")] and
                        ["objective", "n"] + [c for c in certs.columns if c not in ("objective", "n")]]), ""]
    parts += ["## pw − tw by n: search against corpus (exact treewidth)", "", _md(growth), ""]
    if corpus_tw is not None:
        parts += ["## §6's floor as a number: the gap ≥ 2 corpus instances", "", _md(floor_table(corpus_tw)), ""]
        gap2 = corpus_tw[(corpus_tw["gap"] >= 2)].sort_values(["n_customers", "instance_name"])
        parts += ["## Every gap ≥ 2 corpus instance with pw − tw ≥ 2 (exact or proved by interval)", "",
                  _md(gap2[gap2["pwtw_lo"] >= 2][["instance_name", "source_file", "n_customers", "optimum",
                                                   "pw", "tw_lo", "tw_hi", "method", "seconds"]].head(60)), ""]
        parts += ["## Corpus baselines per n", "", _md(baseline), ""]
    small = jobs[jobs["best_pwtw"] >= 2].copy()
    if len(small):
        small["core"] = small["best_key"].map(core_key)
        small["n_active"] = small["core"].map(lambda k: len(k.split("/")))
        small = small.drop_duplicates("core").sort_values(["n_active", "best_edges", "best_ones"])
        parts += ["## The smallest instances found with pw − tw ≥ 2 (isolated customers dropped)", "",
                  f"{len(small)} distinct instances with pw − tw ≥ 2 over every job; by active vertex count: "
                  + ", ".join(f"{int(k)} vertices × {int(v)}" for k, v in small["n_active"].value_counts().sort_index().items())
                  + ".", ""]
        shown = set()
        for _, row in small.iterrows():
            if row["n_active"] in shown or len(shown) >= 3:
                continue
            shown.add(row["n_active"])
            facts, proof = proof_block(row["core"], solutions_dir)
            parts.append(draw(row["core"], f"{row['n_active']} vertices, pw − tw = {facts['pwtw']} "
                                           f"(drawn at n = {row['n']}, seed kind {row['kind']})"))
            parts += ["", proof, ""]
    parts += ["## Drawings", ""]
    for _, row in best.iterrows():
        parts.append(draw(row["key"], f"{row['objective']} at n = {row['n']}: value {row['value']} "
                                      f"(optimum {row['optimum']}, lb_best {row['lb_best']}, tw {row['tw']}, "
                                      f"nodes {row['nodes_default']}, cs-dfs {row['ub_cs_dfs']})"))
        parts.append(f"Witness closing order `{row['witness']}`; elimination ordering of width {row['tw']}: "
                     f"`{row['tw_order']}`.")
        parts.append("")
    out.write_text("\n".join(parts))
    return {"best": best, "baseline": baseline, "verdict": verdict, "growth": growth, "certs": certs,
            "corpus_tw": corpus_tw, "jobs": jobs}


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("corpus", "search", "tables", "all"), default="all")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--restarts", type=int, nargs=3, default=(5, 3, 4), metavar=("TOC", "BERN", "CORPUS"))
    parser.add_argument("--deadline", type=float, default=60.0, help="seconds per corpus instance above n = 26")
    parser.add_argument("--max-n-all", type=int, default=20)
    parser.add_argument("--objectives", nargs="+", default=list(OBJECTIVES), choices=OBJECTIVES)
    parser.add_argument("--sizes", type=int, nargs="+", default=list(SEARCH_SIZES))
    parser.add_argument("--extra-sizes", type=int, nargs="*", default=list(PWTW_EXTRA_SIZES),
                        help="sizes the pwtw objective alone also runs at")
    parser.add_argument("--seed-keys", type=Path, default=None,
                        help="file of matrix keys (one per line) to use as the corpus-kind seeds")
    parser.add_argument("--tag", default="", help="suffix for this run's job and trace files")
    parser.add_argument("--patience", type=int, default=60)
    args = parser.parse_args()
    SCRATCH_SOLUTIONS.mkdir(parents=True, exist_ok=True)
    if args.stage in ("corpus", "all"):
        t = time.monotonic()
        out = run_corpus(args.workers, args.max_n_all, args.deadline)
        print(f"corpus treewidth: {len(out)} rows in {time.monotonic() - t:.0f} s; "
              f"exact on {int(out['tw_exact'].sum())}", flush=True)
    if args.stage in ("search", "all"):
        t = time.monotonic()
        keys = [l.strip() for l in args.seed_keys.read_text().splitlines() if l.strip()] if args.seed_keys else None
        jobs = run_search(args.workers, args.steps, tuple(args.restarts), tuple(args.sizes),
                          tuple(args.extra_sizes), tuple(args.objectives),
                          jobs_csv=JOBS_CSV.with_name(f"extremal_jobs{args.tag}.csv"),
                          trace_csv=TRACE_CSV.with_name(f"extremal_trace{args.tag}.csv.gz"),
                          seed_keys=keys, patience=args.patience)
        print(f"search: {len(jobs)} jobs, {int(jobs['evaluations'].sum()):,} evaluations in "
              f"{time.monotonic() - t:.0f} s", flush=True)
    if args.stage in ("tables", "all"):
        res = write_tables()
        print(_md(res["verdict"]))
        print()
        print(_md(res["growth"]))
        print(f"wrote {TABLES}")


if __name__ == "__main__":
    main()
