"""The anatomy of a refutation: where the customer search's states sit.

For an instance refuted at `k = optimum - 1` by the complete customer search,
the certificate (`learning.search_certificate.emit`) is the tree of states
the search visited. Each node is a closed set `S` of customers; in vertex
separation vocabulary its prefix is `N[S]` (every pattern of a closed
customer is produced, so every neighbour is open) of size `p = |N[S]|`, with
inner boundary `|N(S) \\ S|` = the open count, at most `k`.

This module tabulates the tree by `p`: how many nodes, how many distinct
closed sets, how many refuted leaves and memo hits sit at each prefix size.
The sizes where the count peaks are where the obstruction lives, and the
checkpoint relaxation (`learning.checkpoint_bound`) should need its
checkpoints there. Sizes are reported in both units (`|S|` and `p = |N[S]|`).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from learning.checkpoint_bound import OUT, pilot_population
from learning.obstruction_expansion import closed_masks_from_matrix


def profile(instance, optimum: int, config: str, deadline_seconds: float) -> dict:
    from learning.search_certificate import emit, config_kwargs

    kwargs = config_kwargs(instance, config)
    deadline = time.monotonic() + deadline_seconds
    cert = emit(instance, optimum - 1, deadline=deadline, **kwargs)
    closed = closed_masks_from_matrix(instance.matrix)
    n = len(closed)
    mask = {}
    by_p: dict[int, dict] = {}
    by_s: dict[int, int] = {}
    seen_sets: dict[int, set] = {}
    for node in cert.nodes:
        S = mask[node.parent] if node.parent is not None else 0
        if node.move is not None:
            S |= 1 << node.move
        for f in node.free:
            S |= 1 << f
        mask[node.id] = S
        NS = 0
        for v in range(n):
            if S >> v & 1:
                NS |= closed[v]
        p = bin(NS).count("1")
        s = bin(S).count("1")
        d = by_p.setdefault(p, {"nodes": 0, "memo": 0, "leaves": 0, "steps": 0})
        d["nodes"] += 1
        d["memo"] += node.kind == "memo"
        d["leaves"] += (not node.children) and node.kind == "refuted"
        d["steps"] += len(node.steps)
        seen_sets.setdefault(p, set()).add(S)
        by_s[s] = by_s.get(s, 0) + 1
    for p, d in by_p.items():
        d["distinct"] = len(seen_sets[p])
    peak_p = max(by_p, key=lambda p: by_p[p]["nodes"]) if by_p else None
    total = len(cert.nodes)
    # the smallest window of sizes holding half the nodes
    ps = sorted(by_p)
    cum = np.cumsum([by_p[p]["nodes"] for p in ps])
    half = None
    best = None
    for a in range(len(ps)):
        for b in range(a, len(ps)):
            inside = cum[b] - (cum[a - 1] if a else 0)
            if inside * 2 >= total and (best is None or ps[b] - ps[a] < best):
                best = ps[b] - ps[a]
                half = (ps[a], ps[b])
                break
    return {"instance_name": instance.name, "n": n, "optimum": optimum, "k": optimum - 1, "config": config,
            "status": cert.status, "nodes": total, "branches": cert.branches,
            "distinct_sets": sum(len(v) for v in seen_sets.values()),
            "peak_p": peak_p, "peak_nodes": by_p[peak_p]["nodes"] if peak_p is not None else None,
            "peak_distinct": by_p[peak_p]["distinct"] if peak_p is not None else None,
            "half_window": f"{half[0]}-{half[1]}" if half else "", "half_window_width": best,
            "sizes_with_nodes": len(by_p), "emit_seconds": round(cert.emit_seconds, 3),
            "profile_p": json.dumps({int(p): by_p[p] for p in ps}),
            "profile_s": json.dumps({int(s): by_s[s] for s in sorted(by_s)})}


def _init():
    os.nice(19)


def _job(args):
    name, inst, optimum, config, deadline = args
    try:
        return profile(inst, optimum, config, deadline)
    except Exception as exc:  # noqa: BLE001
        return {"instance_name": name, "n": inst.n_customers, "optimum": optimum, "config": config,
                "status": f"error: {exc}"}


def run(workers: int, n_max: int, config: str, deadline: float, out_dir: Path) -> None:
    from learning.obstruction_ledger import corpus_instances

    out_dir.mkdir(parents=True, exist_ok=True)
    pop = pilot_population(n_max)
    found = corpus_instances()
    jobs = [(r.instance_name, found[r.instance_name][1], int(r.optimum), config, deadline) for r in pop.itertuples()]
    path = out_dir / "anatomy.csv"
    rows = []
    t0 = time.monotonic()
    with Pool(workers, initializer=_init) as pool:
        for row in pool.imap_unordered(_job, jobs):
            rows.append(row)
            print(f"{time.strftime('%T')} {len(rows)}/{len(jobs)} {row['instance_name'][:28]:28} n={row['n']:3} "
                  f"opt {row['optimum']} {row['status']} nodes {row.get('nodes')} peak p={row.get('peak_p')} "
                  f"({row.get('peak_nodes')} nodes, {row.get('peak_distinct')} sets) half {row.get('half_window')} "
                  f"{row.get('emit_seconds')}s", flush=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"done: {len(rows)} rows in {time.monotonic() - t0:.0f} s -> {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--n-max", type=int, default=50)
    ap.add_argument("--config", default="csearch")
    ap.add_argument("--deadline", type=float, default=600.0)
    ap.add_argument("--out", type=Path, default=OUT / "anatomy")
    a = ap.parse_args()
    run(a.workers, a.n_max, a.config, a.deadline, a.out)


if __name__ == "__main__":
    main()
