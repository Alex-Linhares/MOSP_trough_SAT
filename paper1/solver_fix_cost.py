"""What the repair costs: paired runs, published rules against repaired
(loop0007 item 04, `paper1/solver_fix.md`).

Every job runs one decision (or one pathwidth descent) twice, once with
`repaired_rules=False` (Chu & Stuckey's definite and better moves as
published) and once with `repaired_rules=True` (the premises proved sound in
`lean/MOSPFormalization/Search/`, the default since 2026-10-01). Both settings
are named explicitly. The two calls of a pair run in the same worker, one after
the other, in an order that alternates by job, so that load drift on the
machine does not favour either side.

Beside nodes and seconds, each MOSP call reads the C's rule counters
(`satisfiability.native.last_rule_counts`): how often the definite move's
published test `close >= open` passes, how often the repaired matching test
then fails, at how many nodes the definite move no longer fires at all, and the
same for the better move's `(r, q)` pairs. Counting never changes the search.

Stages:

- `mosp40`: every certified corpus instance at n <= 40, `decide(optimum - 1)`
  under the `default` and `csearch` configurations (`learning.node_counts`).
- `cs`: the Chu & Stuckey classes at 50-100 (corpus `Random-*`), the
  `csearch` configuration, `--deadline` seconds per call. A censored call is a
  lower bound on nodes.
- `cs125`: the certified 125 x 125 instances, the `csearch` configuration,
  under a node cap (`--max-nodes`). Where both sides hit the cap the tree sizes
  are unknown and the pair measures per-node overhead and the rule counters
  only.
- `pw`: the pathwidth solver, `pathwidth.solve(G, time_budget=...)` on
  VSPLIB (trees, grids, HB), the DIMACS colouring graphs, the named graphs and
  a seeded Rome sample; then, on the widest component when it has at most 128
  vertices and the width was proved, one counter pass: the refutation
  `decide(width)` on the graph as a MOSP instance with one product per edge,
  whose MOSP graph is the component itself (MOSP's C equals the pathwidth C
  node for node, `pathwidth_solver/tests/test_identity_mosp.py`).
- `overhead`: per-node cost under a fixed node cap, on a few hard instances,
  `--reps` repetitions alternating three libraries: the published rules, the
  repaired rules, and the published rules in the C as it stood before the rule
  counters (`git show HEAD:satisfiability/customer_search.c`, built to a
  scratch file), which prices the counters themselves. One process per
  instance, so run it on a quiet machine.
- `tables`: `paper1/data/solver_fix_cost_tables.md`.

Nothing here writes to `solutions/`.

Run:

    python -m paper1.solver_fix_cost --stage mosp40 --workers 22
    python -m paper1.solver_fix_cost --stage cs --workers 22 --deadline 600
    python -m paper1.solver_fix_cost --stage cs125 --workers 22 --max-nodes 200000000
    python -m paper1.solver_fix_cost --stage pw --workers 22 --pw-budget 120 --rome 500
    python -m paper1.solver_fix_cost --stage overhead --reps 3 --max-nodes 50000000
    python -m paper1.solver_fix_cost --stage tables
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "paper1" / "data"
SETTINGS = ("old", "repaired")
COUNTER_NAMES = (
    "filter_calls", "definite_prefilter", "definite_match_fail", "definite_fires",
    "definite_lost", "better_prefilter", "better_match_fail", "better_pruned",
)
MOSP_FIELDS = ["stage", "instance_name", "collection", "n", "m", "optimum", "k", "config",
               "setting", "status", "nodes", "seconds", "deadline", "max_nodes",
               *COUNTER_NAMES]
PW_SETS = ("vsplib-tree", "vsplib-grids", "vsplib-hb", "coloring", "named", "rome")
PW_FIELDS = ["set", "name", "path", "n", "m", "widest", "setting", "width", "proof", "lower",
             "upper_start", "nodes", "seconds", "budget",
             "count_k", "count_status", "count_nodes", "count_seconds",
             *COUNTER_NAMES]


def _csv_path(stage: str) -> Path:
    return DATA / f"solver_fix_cost_{stage}.csv"


def _config_flags(config: str, instance) -> dict:
    from satisfiability.customer_search import sparse_enough_for_better_move

    if config == "default":
        return {}
    if config == "csearch":
        return {"better_move": bool(sparse_enough_for_better_move(instance)),
                "better_move_dominators": 0}
    raise ValueError(config)


# ----------------------------------------------------------------------------
# MOSP stages
# ----------------------------------------------------------------------------


def mosp_targets(stage: str) -> list[dict]:
    from learning.differential import DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, corpus_targets

    if stage == "mosp40":
        return corpus_targets(DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, 40)
    jobs = corpus_targets(DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, 125)
    jobs = [j for j in jobs if j["instance_name"].startswith("Random-")]
    if stage == "cs":
        return [j for j in jobs if 50 <= len(j["matrix"]) <= 100]
    if stage == "cs125":
        return [j for j in jobs if len(j["matrix"]) == 125]
    raise ValueError(stage)


def _one_mosp(instance, k: int, config: str, setting: str, deadline: float | None,
              max_nodes: int | None) -> dict:
    from satisfiability.customer_search import decide
    from satisfiability.native import last_rule_counts

    flags = _config_flags(config, instance)
    started = time.monotonic()
    answer = decide(instance, k, repaired_rules=(setting == "repaired"),
                    deadline=None if deadline is None else started + deadline,
                    max_nodes=max_nodes, **flags)
    seconds = time.monotonic() - started
    counts = last_rule_counts() or {}
    return {"status": answer.status, "nodes": int(answer.nodes), "seconds": round(seconds, 4),
            **{name: counts.get(name, "") for name in COUNTER_NAMES}}


def _mosp_job(args) -> list[dict]:
    from learning.differential import _materialise

    stage, job, configs, deadline, max_nodes, flip = args
    instance = _materialise(job)
    k = int(job["optimum"]) - 1
    rows = []
    for config in configs:
        for setting in (SETTINGS[::-1] if flip else SETTINGS):
            row = {"stage": stage, "instance_name": job["instance_name"],
                   "collection": job.get("collection", ""), "n": instance.n_customers,
                   "m": instance.n_patterns, "optimum": int(job["optimum"]), "k": k,
                   "config": config, "setting": setting,
                   "deadline": "" if deadline is None else deadline,
                   "max_nodes": "" if max_nodes is None else max_nodes}
            row.update(_one_mosp(instance, k, config, setting, deadline, max_nodes))
            rows.append(row)
    return rows


def run_mosp(stage: str, workers: int, deadline: float | None, max_nodes: int | None,
             limit: int | None = None) -> None:
    configs = ("default", "csearch") if stage == "mosp40" else ("csearch",)
    jobs = mosp_targets(stage)
    # The largest first, so the long calls do not start last.
    jobs.sort(key=lambda j: -len(j["matrix"]) * len(j["matrix"][0]))
    if stage == "cs":
        # The day-long classes (density 2 and 4 at 100 x 100) first of all.
        jobs.sort(key=lambda j: not j["instance_name"].startswith(("Random-100-100-2", "Random-100-100-4")))
    if limit:
        jobs = jobs[:limit]
    out = _csv_path(stage)
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with out.open("w", newline="") as fh, mp.get_context("fork").Pool(workers) as pool:
        writer = csv.DictWriter(fh, fieldnames=MOSP_FIELDS)
        writer.writeheader()
        args = [(stage, job, configs, deadline, max_nodes, i % 2 == 1) for i, job in enumerate(jobs)]
        for done, rows in enumerate(pool.imap_unordered(_mosp_job, args, chunksize=1), 1):
            writer.writerows(rows)
            fh.flush()
            if done % 500 == 0 or stage != "mosp40":
                r = {row["setting"]: row for row in rows if row["config"] == configs[-1]}
                print(f"[{done}/{len(jobs)}] {rows[0]['instance_name']:28s} "
                      f"old {r['old']['status']} {r['old']['nodes']} {r['old']['seconds']}s | "
                      f"rep {r['repaired']['status']} {r['repaired']['nodes']} {r['repaired']['seconds']}s "
                      f"| {time.time() - started:.0f}s", flush=True)
    print(f"done: {len(jobs)} instances -> {out}", flush=True)


# ----------------------------------------------------------------------------
# pathwidth stage
# ----------------------------------------------------------------------------


def pw_targets(rome: int, seed: int = 20261001) -> list[tuple[str, Path]]:
    sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
    from readers import SETS

    targets = []
    for name in PW_SETS:
        paths = SETS[name]()
        if name == "rome":
            paths = sorted(random.Random(seed).sample(paths, min(rome, len(paths))))
        targets.extend((name, p) for p in paths)
    return targets


def _edge_instance(H):
    """The graph as a MOSP instance with one product per edge: its MOSP graph
    is `H` itself, and MOSP <= k iff pathwidth <= k - 1."""
    from mosp.instance import MOSPInstance

    nodes = sorted(H.nodes())
    index = {v: i for i, v in enumerate(nodes)}
    edges = list(H.edges())
    matrix = np.zeros((len(nodes), len(edges)), dtype=np.int8)
    for j, (u, v) in enumerate(edges):
        matrix[index[u], j] = matrix[index[v], j] = 1
    return MOSPInstance(matrix=matrix, n_customers=len(nodes), n_patterns=len(edges), name="edges")


def _pw_job(args) -> list[dict]:
    setname, path, budget, count_nodes, flip = args
    sys.path.insert(0, str(ROOT / "pathwidth_solver"))
    sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
    import networkx as nx
    from pathwidth import solve
    from readers import read_any

    G = read_any(path)
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    widest = len(comps[0]) if comps else 0
    rows = []
    for setting in (SETTINGS[::-1] if flip else SETTINGS):
        t = time.perf_counter()
        row = {"set": setname, "name": path.stem.replace(".mtx", ""),
               "path": str(path.relative_to(ROOT)), "n": G.number_of_nodes(),
               "m": G.number_of_edges(), "widest": widest, "setting": setting, "budget": budget}
        try:
            sol = solve(G, time_budget=budget, repaired_rules=(setting == "repaired"))
            row.update(width=sol.width, proof=sol.proof or "budget", lower=sol.lower,
                       upper_start=sol.upper_start, nodes=sol.nodes)
        except Exception as exc:  # keep the sweep alive
            row.update(proof=f"error: {type(exc).__name__}: {exc}"[:80])
        row["seconds"] = round(time.perf_counter() - t, 3)
        rows.append(row)
    # Counter pass on the widest component: the refutation of width - 1, on
    # the component's own width (which the solver proved and may be below the
    # graph's). Same k for both settings.
    proved = [r for r in rows if r.get("proof") in ("refutation", "bound")]
    if proved and 2 <= widest <= 128 and G.subgraph(comps[0]).number_of_edges():
        H = G.subgraph(comps[0])
        sol_h = solve(H, time_budget=budget)
        if sol_h.proof in ("refutation", "bound") and sol_h.width >= 1:
            instance = _edge_instance(H)
            for row in rows:
                c = _one_mosp(instance, int(sol_h.width), "default", row["setting"],
                              budget, count_nodes)
                row.update(count_k=int(sol_h.width), count_status=c.pop("status"),
                           count_nodes=c.pop("nodes"), count_seconds=c.pop("seconds"), **c)
    return rows


def run_pw(workers: int, budget: float, rome: int, count_nodes: int, limit: int | None) -> None:
    targets = pw_targets(rome)
    if limit:
        targets = targets[:limit]
    out = _csv_path("pw")
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with out.open("w", newline="") as fh, mp.get_context("fork").Pool(workers) as pool:
        writer = csv.DictWriter(fh, fieldnames=PW_FIELDS, extrasaction="ignore")
        writer.writeheader()
        args = [(s, p, budget, count_nodes, i % 2 == 1) for i, (s, p) in enumerate(targets)]
        for done, rows in enumerate(pool.imap_unordered(_pw_job, args, chunksize=1), 1):
            writer.writerows(rows)
            fh.flush()
            if rows[0]["set"] != "rome" or done % 100 == 0:
                r = {row["setting"]: row for row in rows}
                print(f"[{done}/{len(targets)}] {rows[0]['set']:12s} {rows[0]['name']:24s} "
                      f"old {r['old'].get('width')} {r['old'].get('proof')} {r['old'].get('nodes')} "
                      f"{r['old']['seconds']}s | rep {r['repaired'].get('width')} "
                      f"{r['repaired'].get('proof')} {r['repaired'].get('nodes')} "
                      f"{r['repaired']['seconds']}s | {time.time() - started:.0f}s", flush=True)
    print(f"done: {len(targets)} graphs -> {out}", flush=True)


# ----------------------------------------------------------------------------
# overhead stage
# ----------------------------------------------------------------------------

OVERHEAD_INSTANCES = ("Random-125-125-2-1_0", "Random-125-125-4-1_0", "Random-125-125-6-2_0",
                      "Random-100-100-2-1_0", "Random-100-50-4-1_0", "Random-75-75-2-1_0")
OVERHEAD_FIELDS = ["instance_name", "n", "k", "rep", "variant", "status", "nodes", "seconds",
                   "us_per_node"]


def _build_reference(revision: str = "HEAD") -> Path:
    import subprocess

    src = DATA / f"customer_search_{revision}.c"
    lib = DATA / f"_customer_search_{revision}.so"
    src.write_text(subprocess.run(["git", "show", f"{revision}:satisfiability/customer_search.c"],
                                  cwd=ROOT, check=True, capture_output=True, text=True).stdout)
    subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", str(lib), str(src)],
                   check=True, capture_output=True)
    src.unlink()
    return lib


def _overhead_job(args) -> list[dict]:
    import ctypes

    import satisfiability.native as native
    from learning.differential import _materialise
    from satisfiability.customer_search import decide

    job, reps, max_nodes, reference = args
    instance = _materialise(job)
    k = int(job["optimum"]) - 1
    flags = _config_flags("csearch", instance)
    current = native._load()
    ref = ctypes.CDLL(str(reference))
    ref.cs_decide_rules.restype = ctypes.c_int
    ref.cs_decide_rules.argtypes = current.cs_decide_rules.argtypes
    variants = (("old", current, False), ("repaired", current, True), ("old, pre-counter C", ref, False))
    rows = []
    for rep in range(reps):
        for name, lib, repaired in (variants if rep % 2 == 0 else variants[::-1]):
            native._library = lib
            started = time.perf_counter()
            answer = decide(instance, k, repaired_rules=repaired, max_nodes=max_nodes, **flags)
            seconds = time.perf_counter() - started
            rows.append({"instance_name": job["instance_name"], "n": instance.n_customers, "k": k,
                         "rep": rep, "variant": name, "status": answer.status,
                         "nodes": int(answer.nodes), "seconds": round(seconds, 4),
                         "us_per_node": round(1e6 * seconds / max(1, answer.nodes), 5)})
    native._library = current
    return rows


def run_overhead(reps: int, max_nodes: int) -> None:
    from learning.differential import DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, corpus_targets

    jobs = [j for j in corpus_targets(DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, 125)
            if j["instance_name"] in OVERHEAD_INSTANCES]
    reference = _build_reference()
    out = _csv_path("overhead")
    with out.open("w", newline="") as fh, mp.get_context("fork").Pool(len(jobs)) as pool:
        writer = csv.DictWriter(fh, fieldnames=OVERHEAD_FIELDS)
        writer.writeheader()
        for rows in pool.imap_unordered(_overhead_job, [(j, reps, max_nodes, reference) for j in jobs]):
            writer.writerows(rows)
            fh.flush()
            for row in rows:
                print(row, flush=True)
    reference.unlink()
    print(f"done -> {out}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=("mosp40", "cs", "cs125", "pw", "overhead", "tables"), default="tables")
    ap.add_argument("--workers", type=int, default=22)
    ap.add_argument("--deadline", type=float, default=None, help="seconds per MOSP call")
    ap.add_argument("--max-nodes", type=int, default=None, help="node cap per MOSP call")
    ap.add_argument("--pw-budget", type=float, default=120.0, help="seconds per pathwidth descent")
    ap.add_argument("--count-nodes", type=int, default=50_000_000,
                    help="node cap of the pathwidth counter pass")
    ap.add_argument("--rome", type=int, default=500, help="Rome graphs sampled")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--reps", type=int, default=3, help="repetitions of the overhead stage")
    a = ap.parse_args()
    if a.stage in ("mosp40", "cs", "cs125"):
        run_mosp(a.stage, a.workers, a.deadline, a.max_nodes, a.limit)
    elif a.stage == "overhead":
        run_overhead(a.reps, a.max_nodes or 50_000_000)
    elif a.stage == "pw":
        run_pw(a.workers, a.pw_budget, a.rome, a.count_nodes, a.limit)
    else:
        from paper1.solver_fix_cost_tables import write_tables
        write_tables()


if __name__ == "__main__":
    main()
