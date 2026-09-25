"""Do node counts come back from every decision call, and what do they look like?

The prerequisite for `reports/ml_nature_plan.md` §2.4: hardness has to be
measured in branch decisions ("nodes") of the complete customer search, not in
seconds, so that the measurement survives a change of hardware and a loaded
machine. The search has always counted them; until 2026-09-25 the count was
printed by some drivers and stored by none. It now comes back as
`Decision.nodes` and `Solution.nodes` (unchanged), through the `stats` dict of
`satisfiability.mosp_solver.solve_mosp_exact` (new), and into the `nodes`
column of `benchmarks/results/compute_ledger.csv` from `benchmarks.csearch` and
`benchmarks.recertify` (new). Rows written before the column existed are empty.

This module answers two questions about that instrumentation:

1. **What does the ledger hold?** Rows per driver, and how many carry a node
   count. On the day the column landed the answer is "none yet", which is the
   baseline every later §2.4 run is measured against.
2. **What does the refutation at `optimum - 1` cost at small size?** For every
   certified instance with at most `--max-customers` customers, run the search
   at `optimum - 1` and record status, nodes and seconds. The status is a free
   audit -- `sat` there would mean the stored optimum is wrong -- and the node
   counts, grouped by size band and by collection, are the first look at the
   quantity §2.4 will plot against density. Two configurations are run, because
   the ledger's own rows come from two: the `decide` defaults that
   `solve_mosp_exact` uses, and the `csearch` driver's rule (Theorem 2 on
   sparse instances, every candidate a dominator).

This is not the §2.4 study. It runs on the benchmark corpus, whose density is
confounded with collection (`reports/ml_nature.md` §2), and it is not
deduplicated by isomorphism class; the generated ensembles are the next loop.
Nothing here touches `_lower_bound`, changes any default, or writes to
`solutions/`.

Usage:
    python -m learning.node_counts                       # n <= 30, 16 workers
    python -m learning.node_counts --max-customers 20 --limit 200
    python -m learning.node_counts --out reports/node_count_tables.md

Writes `learning/data/node_counts.csv` (git-ignored, regenerable).
"""

from __future__ import annotations

import argparse
import csv
import json
import multiprocessing
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import (
    DATA_DIR,
    DEFAULT_INSTANCE_DIR,
    DEFAULT_SOLUTIONS_DIR,
    enumerate_instances,
)
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import CERTIFIED, _solution_path

DEFAULT_OUT = DATA_DIR / "node_counts.csv"

# The two configurations whose node counts reach the ledger. `default` is what
# `decide` runs with no arguments, hence what `solve_mosp_exact` records;
# `csearch` is the driver's rule in `benchmarks/csearch.py::_worker`.
CONFIGS = ("default", "csearch")

SIZE_BANDS = ((0, 10), (11, 20), (21, 30), (31, 40), (41, 60), (61, 200))


def ledger_summary(ledger: Path) -> pd.DataFrame:
    """Rows per driver, and how many of them carry a node count."""
    if not ledger.exists():
        return pd.DataFrame(columns=["driver", "rows", "with_nodes"])
    with ledger.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    counts: Counter = Counter()
    with_nodes: Counter = Counter()
    for row in rows:
        counts[row["driver"]] += 1
        if row.get("nodes", "").strip():
            with_nodes[row["driver"]] += 1
    table = pd.DataFrame(
        [{"driver": d, "rows": counts[d], "with_nodes": with_nodes[d]}
         for d in sorted(counts)])
    total = pd.DataFrame([{"driver": "TOTAL", "rows": sum(counts.values()),
                           "with_nodes": sum(with_nodes.values())}])
    return pd.concat([table, total], ignore_index=True)


def refutation_kwargs(instance: MOSPInstance, config: str) -> dict:
    """The keyword arguments `decide` gets under a named configuration."""
    if config == "default":
        return {}
    if config == "csearch":
        from satisfiability.customer_search import sparse_enough_for_better_move

        return {"better_move": sparse_enough_for_better_move(instance),
                "better_move_dominators": 0}
    raise ValueError(f"unknown configuration {config!r}; one of {CONFIGS}")


def refute(instance: MOSPInstance, optimum: int, config: str = "default",
           deadline_seconds: float | None = None) -> dict:
    """Decide `optimum - 1` once and return what it cost.

    `status` is `"unsat"` when the search agrees the value is optimal, `"sat"`
    when the stored optimum is wrong (the search found a better order), and
    `"unknown"` when the deadline expired. `nodes` is always a count, including
    on a timeout: a censored observation still says how far the search got.
    """
    from satisfiability.customer_search import decide

    kwargs = refutation_kwargs(instance, config)
    deadline = None if deadline_seconds is None else time.monotonic() + deadline_seconds
    started = time.monotonic()
    answer = decide(instance, optimum - 1, deadline=deadline, **kwargs)
    return {"config": config, "status": answer.status, "nodes": answer.nodes,
            "seconds": round(time.monotonic() - started, 4)}


def _job(args) -> list[dict]:
    matrix, name, source_file, collection, optimum, deadline_seconds = args
    instance = MOSPInstance(matrix=np.array(matrix, dtype=np.int8),
                            n_customers=len(matrix), n_patterns=len(matrix[0]),
                            name=name)
    rows = []
    for config in CONFIGS:
        row = {"instance_name": name, "source_file": source_file,
               "collection": collection, "n_customers": instance.n_customers,
               "n_patterns": instance.n_patterns, "optimum": optimum}
        row.update(refute(instance, optimum, config, deadline_seconds))
        rows.append(row)
    return rows


def certified_targets(instance_dir: Path, solutions_dir: Path,
                      max_customers: int, limit: int | None = None) -> list[tuple]:
    """Every certified instance small enough to run, as picklable job tuples."""
    jobs = []
    for filepath, instance in enumerate_instances(instance_dir):
        if instance.n_customers > max_customers or instance.n_patterns == 0:
            continue
        path = _solution_path(instance, solutions_dir)
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        if data.get("provenance") not in CERTIFIED:
            continue
        optimum = int(data["mosp_value"])
        if optimum <= 1:
            continue          # nothing to refute below 1
        collection = filepath.parts[2] if len(filepath.parts) > 2 else ""
        jobs.append((instance.matrix.tolist(), instance.name, str(filepath),
                     collection, optimum, None))
    if limit is not None:
        jobs = jobs[:limit]
    return jobs


def run(jobs: list[tuple], deadline_seconds: float, workers: int) -> pd.DataFrame:
    jobs = [job[:5] + (deadline_seconds,) for job in jobs]
    if workers <= 1:
        rows = [row for job in jobs for row in _job(job)]
    else:
        with multiprocessing.Pool(workers) as pool:
            rows = [row for out in pool.imap_unordered(_job, jobs, chunksize=8)
                    for row in out]
    return pd.DataFrame(rows)


def _band(n: int) -> str:
    for lo, hi in SIZE_BANDS:
        if lo <= n <= hi:
            return f"{lo}-{hi}"
    return f">{SIZE_BANDS[-1][1]}"


def summarise(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tables: status audit, nodes by size band, by collection, config ratio."""
    frame = frame.copy()
    frame["band"] = frame["n_customers"].map(_band)
    out: dict[str, pd.DataFrame] = {}

    out["status"] = (frame.groupby(["config", "status"]).size()
                     .rename("instances").reset_index())

    def _quantiles(group: pd.DataFrame) -> pd.Series:
        nodes = group["nodes"]
        return pd.Series({
            "instances": len(group),
            "unsat": int((group["status"] == "unsat").sum()),
            "min": int(nodes.min()), "median": float(nodes.median()),
            "p90": float(nodes.quantile(0.9)), "max": int(nodes.max()),
            "seconds_total": round(float(group["seconds"].sum()), 2),
        })

    out["by_band"] = (frame.groupby(["config", "band"], sort=False)
                      .apply(_quantiles, include_groups=False).reset_index())
    out["by_collection"] = (frame.groupby(["config", "collection"])
                            .apply(_quantiles, include_groups=False).reset_index())

    wide = frame.pivot_table(index="instance_name", columns="config",
                             values="nodes", aggfunc="first")
    if set(CONFIGS) <= set(wide.columns):
        ratio = (wide["csearch"] / wide["default"].clip(lower=1))
        out["config_ratio"] = pd.DataFrame([{
            "instances": len(wide),
            "csearch_fewer": int((wide["csearch"] < wide["default"]).sum()),
            "equal": int((wide["csearch"] == wide["default"]).sum()),
            "csearch_more": int((wide["csearch"] > wide["default"]).sum()),
            "median_ratio": round(float(ratio.median()), 3),
            "max_ratio": round(float(ratio.max()), 1),
            "min_ratio": round(float(ratio.min()), 3),
        }])
    return out


def _markdown(title: str, table: pd.DataFrame) -> str:
    return f"### {title}\n\n{table.to_markdown(index=False)}\n\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instance-dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=DEFAULT_SOLUTIONS_DIR)
    parser.add_argument("--ledger", type=Path,
                        default=Path("benchmarks/results/compute_ledger.csv"))
    parser.add_argument("--max-customers", type=int, default=30)
    parser.add_argument("--limit", type=int, default=None,
                        help="first N instances only, for a quick run")
    parser.add_argument("--deadline", type=float, default=10.0,
                        help="seconds per decision call before 'unknown'")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--csv", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--out", type=Path, default=None,
                        help="also write the tables as markdown here")
    args = parser.parse_args()

    started = time.time()
    sections = []

    ledger = ledger_summary(args.ledger)
    sections.append(("The compute ledger: rows per driver, and rows carrying "
                     "a node count", ledger))

    jobs = certified_targets(args.instance_dir, args.solutions_dir,
                             args.max_customers, args.limit)
    print(f"{len(jobs)} certified instances with n <= {args.max_customers}, "
          f"{len(CONFIGS)} configurations, {args.workers} workers", flush=True)
    frame = run(jobs, args.deadline, args.workers)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.csv, index=False)

    tables = summarise(frame)
    sections.append(("Status of the decision call at optimum - 1 (a `sat` "
                     "would be a wrong stored optimum)", tables["status"]))
    sections.append(("Nodes to refute optimum - 1, by size band", tables["by_band"]))
    sections.append(("Nodes to refute optimum - 1, by collection",
                     tables["by_collection"]))
    if "config_ratio" in tables:
        sections.append(("csearch configuration against decide defaults, "
                         "nodes per instance", tables["config_ratio"]))

    text = (f"# Node counts: instrumentation check and first look\n\n"
            f"*Regenerated {time.strftime('%Y-%m-%d %H:%M')} by "
            f"`python -m learning.node_counts --max-customers {args.max_customers}"
            f"{' --limit ' + str(args.limit) if args.limit else ''}`; "
            f"{len(jobs)} instances, {time.time() - started:.0f} s, "
            f"{args.workers} workers, {args.deadline:g} s deadline per call.*\n\n")
    text += "".join(_markdown(title, table) for title, table in sections)
    print(text)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out}")
    print(f"wrote {args.csv} ({len(frame)} rows)")


if __name__ == "__main__":
    main()
