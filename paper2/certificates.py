"""Certificates for the repaired rules: the corpus study and the hand-built failures.

loop0008 item 05, written up in `paper2/certificates.md`. The emitter is
`learning.search_certificate.emit(..., repaired_rules=True)`, which records the
matching of `HasDefiniteMatching` on every definite and better step; the
checker is `paper2/certificate_check.py`, which imports nothing from this
repository.

    python -m paper2.certificates --stage run --min-customers 41 --max-customers 75 --workers 4 --deadline 60
    python -m paper2.certificates --stage run --max-customers 40 --workers 4          # the rest of the corpus
    python -m paper2.certificates --stage failures                                   # hand-built rejections
    python -m paper2.certificates --stage tables

Writes `paper2/data/certificates/repaired.csv` (one row per instance ×
configuration), `failures.json`, the bundles `bundles/*.json.gz` that the
failures and one worked example are checked from, and `tables.md`. Nothing is
written to `solutions/` (which is read, for the certified optima).
"""

from __future__ import annotations

import argparse
import copy
import gzip
import json
import multiprocessing
import time
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("paper2/data/certificates")
CSV = OUT / "repaired.csv"
CONFIGS = ("default", "csearch")
BANDS = ((0, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60), (61, 75))


def config_kwargs(matrix, config: str) -> dict:
    """`default`: the Python reference's rules (Theorem 1, subset, Theorem 3, no
    memo). `csearch`: plus Theorem 2 where `sparse_enough_for_better_move`, every
    earlier candidate a dominator. Both with the repaired premises."""
    if config == "default":
        return {"repaired_rules": True}
    if config == "csearch":
        dense = float(np.asarray(matrix).sum()) / len(matrix)
        return {"repaired_rules": True, "better_move": dense <= 5.0, "better_move_dominators": 0}
    raise ValueError(config)


def _job(args) -> list[dict]:
    from learning.search_certificate import emit
    from mosp.instance import MOSPInstance
    from paper2.certificate_check import check

    matrix, name, source_file, collection, optimum, configs, deadline = args
    inst = MOSPInstance(matrix=np.array(matrix, dtype=np.int8), n_customers=len(matrix),
                        n_patterns=len(matrix[0]), name=name)
    rows = []
    for config in configs:
        kwargs = config_kwargs(matrix, config)
        cert = emit(inst, optimum - 1,
                    deadline=None if deadline is None else time.monotonic() + deadline, **kwargs)
        counts = cert.step_counts()
        sizes = cert.sizes()
        matched = sum(len(step[-1]) for node in cert.nodes for step in node.steps
                      if step[0] in ("definite", "better"))
        row = {"instance_name": name, "source_file": source_file, "collection": collection,
               "n": inst.n_customers, "m": inst.n_patterns, "optimum": int(optimum),
               "config": config, "better_move": bool(kwargs.get("better_move", False)),
               "k": optimum - 1, "status": cert.status, "branches": cert.branches,
               "emit_seconds": round(cert.emit_seconds, 5), "matching_edges": matched,
               **{f"steps_{r}": v for r, v in counts.items()}, **sizes}
        if cert.status == "unsat":
            result = check(matrix, json.loads(cert.dumps()))
            row.update(check_ok=result["ok"], check_reason=result["reason"],
                       check_seconds=round(result["seconds"], 5))
        else:
            row.update(check_ok=None, check_reason="", check_seconds=None)
        rows.append(row)
    return rows


def run(min_customers: int, max_customers: int, workers: int, deadline: float | None,
        configs=CONFIGS, limit: int | None = None) -> pd.DataFrame:
    from learning.search_certificate import targets

    OUT.mkdir(parents=True, exist_ok=True)
    jobs = targets(min_customers, max_customers, limit=limit)
    done = set()
    if CSV.exists():
        old = pd.read_csv(CSV)
        done = set(zip(old.instance_name, old.source_file, old.config))
    todo = [(m, name, src, coll, opt, tuple(c for c in configs if (name, src, c) not in done),
             deadline) for m, name, src, coll, opt, _ in jobs]
    todo = [job for job in todo if job[5]]
    # largest first, so the long emissions do not trail at the end
    todo.sort(key=lambda job: -len(job[0]))
    print(f"{len(todo)} instances at {min_customers}-{max_customers} customers, "
          f"{configs}, {workers} workers, deadline {deadline}", flush=True)
    header = not CSV.exists()
    started = time.monotonic()
    with multiprocessing.get_context("spawn").Pool(workers) as pool, CSV.open("a") as handle:
        for i, rows in enumerate(pool.imap_unordered(_job, todo, chunksize=1), 1):
            pd.DataFrame(rows).to_csv(handle, header=header, index=False)
            handle.flush()
            header = False
            if i % 100 == 0 or len(todo) < 400:
                print(f"  {i}/{len(todo)} {rows[0]['n']} customers "
                      f"{[r['status'] for r in rows]} {time.monotonic() - started:.0f} s", flush=True)
    return pd.read_csv(CSV)


# ----------------------------------------------------------------------------
# hand-built failures
# ----------------------------------------------------------------------------


def _bundle(path: Path, matrix, cert: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps({"matrix": matrix, "certificate": cert},
                                              separators=(",", ":")).encode(), 9))


def _max_matching(freed: dict[int, int]) -> list[list[int]]:
    """A largest matching, by brute augmenting paths: the best a forger could attach."""
    owner: dict[int, int] = {}

    def augment(d, visited):
        s_mask = freed[d]
        s = 0
        while s_mask:
            if s_mask & 1 and s not in visited:
                visited.add(s)
                if s not in owner or augment(owner[s], visited):
                    owner[s] = d
                    return True
            s_mask >>= 1
            s += 1
        return False

    for d in freed:
        augment(d, set())
    return sorted([d, s] for s, d in owner.items())


def _order_cost(masks: list[int], order: list[int]) -> int:
    closed = opened = 0
    worst = 0
    for c in order:
        opened |= masks[c]
        worst = max(worst, bin(opened & ~closed).count("1"))
        closed |= 1 << c
    return worst


def failures() -> dict:
    """The checker against certificates that must fail, on `DEFINITE_CEX` and a corpus instance."""
    from learning.search_certificate import check as published_check
    from learning.search_certificate import emit, neighbourhoods
    from mosp.instance import MOSPInstance
    from paper2.certificate_check import check
    from paper2.search_check import DEFINITE_CEX, matrix_from_masks

    report: dict = {"definite_cex": [], "corrupted": []}
    for idx, (masks, S, q, k) in enumerate(DEFINITE_CEX):
        matrix = [[int(v) for v in row] for row in matrix_from_masks(masks)]
        inst = MOSPInstance.from_matrix(matrix, name=f"DEFINITE_CEX[{idx}]")
        start = [c for c in range(len(masks)) if S >> c & 1]
        for config, cfg in (("default", {}),
                            ("csearch", {"better_move": True, "better_move_dominators": 0})):
            published = emit(inst, k, start=S, **cfg)
            data = json.loads(published.dumps())
            entry = {"instance": inst.name, "n": len(masks), "start": start, "k": k,
                     "config": config, "published_status": published.status,
                     "published_branches": published.branches,
                     "root_steps": published.nodes[0].steps,
                     "learning_checker_accepts": published_check(inst, published).ok,
                     "checker": check(matrix, data)["reason"]}
            _bundle(OUT / "bundles" / f"definite_cex{idx}_{config}_published.json.gz", matrix, data)
            # the strongest forgery: attach a *largest* matching to every definite step
            forged = copy.deepcopy(data)
            nmasks = neighbourhoods(inst)
            opened = 0
            for c in start:
                opened |= nmasks[c]
            root = forged["nodes"][0]
            for step in root["steps"]:
                if step[0] == "definite":
                    q0 = step[1]
                    own = nmasks[q0] & ~opened
                    freed = {d: nmasks[d] & ~opened for d in range(len(masks))
                             if d != q0 and not S >> d & 1 and nmasks[d] & ~opened & ~own == 0}
                    step.append(_max_matching(freed))
                    entry["open"] = bin(own).count("1")
                    entry["largest_matching"] = step[2]
            # repair any later definite/better steps too, so the root is what is judged
            result = check(matrix, forged)
            entry["forged_with_largest_matching"] = result["reason"]
            _bundle(OUT / "bundles" / f"definite_cex{idx}_{config}_forged.json.gz", matrix, forged)
            repaired = emit(inst, k, start=S, repaired_rules=True, **cfg)
            entry["repaired_status"] = repaired.status
            entry["repaired_order"] = repaired.order
            entry["repaired_order_cost"] = _order_cost(nmasks, repaired.order) if repaired.order else None
            report["definite_cex"].append(entry)

    # a corrupted matching on a corpus-style instance with matchings of 2+ edges
    inst, matrix, cert = _example_with_matching()
    data = json.loads(cert.dumps())
    _bundle(OUT / "bundles" / "example_repaired.json.gz", matrix, data)
    report["example"] = {"instance": inst.name, "n": inst.n_customers, "m": inst.n_patterns,
                         "k": cert.k, "config": cert.config, "nodes": len(cert.nodes),
                         "checker": check(matrix, data)["reason"]}
    for name, edit in CORRUPTIONS.items():
        bad = copy.deepcopy(data)
        applied = edit(bad, matrix)
        result = check(matrix, bad)
        report["corrupted"].append({"corruption": name, "applied": applied,
                                    "ok": result["ok"], "reason": result["reason"]})
    (OUT / "failures.json").write_text(json.dumps(report, indent=1))
    return report


EXAMPLE = "Warwick 877: balanced orders, 4 orders per product"


def _example_with_matching():
    """A corpus instance whose repaired certificate has matchings of two edges or more."""
    from learning.dataset import enumerate_instances
    from learning.search_certificate import emit

    for _, inst in enumerate_instances(Path("benchmarks/instances")):
        if inst.name != EXAMPLE:
            continue
        optimum = json.loads(_solution(inst).read_text())["mosp_value"]
        cert = emit(inst, optimum - 1, repaired_rules=True, better_move=True,
                    better_move_dominators=0)
        assert cert.status == "unsat"
        return inst, inst.matrix.tolist(), cert
    raise SystemExit(f"no instance {EXAMPLE}")


def _solution(inst):
    from learning.node_counts import _solution_path

    return _solution_path(inst, Path("solutions"))


def _first_step(data, rule, min_edges=2):
    for node in data["nodes"]:
        for step in node.get("steps", []):
            if step[0] == rule and len(step[-1]) >= min_edges:
                return node, step
    for node in data["nodes"]:
        for step in node.get("steps", []):
            if step[0] == rule and len(step[-1]) >= 1:
                return node, step
    return None, None


def _drop_edge(data, matrix):
    node, step = _first_step(data, "definite")
    step[-1].pop()
    return f"node {node['id']}: definite on {step[1]}, one edge removed"


def _repeat_stack(data, matrix):
    node, step = _first_step(data, "definite")
    step[-1][1][1] = step[-1][0][1]
    return f"node {node['id']}: definite on {step[1]}, second edge given the first edge's stack"


def _repeat_customer(data, matrix):
    node, step = _first_step(data, "definite")
    step[-1][1][0] = step[-1][0][0]
    return f"node {node['id']}: definite on {step[1]}, second edge given the first edge's customer"


def _stack_not_opened(data, matrix):
    node, step = _first_step(data, "definite")
    d = step[-1][0][0]
    from paper2.certificate_check import closed_neighbourhoods

    N = closed_neighbourhoods(matrix)
    s = next(c for c in range(len(matrix)) if not N[d] >> c & 1)   # not even a neighbour of d
    step[-1][0][1] = s
    return f"node {node['id']}: definite on {step[1]}, edge ({d}, {s}) with {s} outside N[{d}]"


def _customer_not_freed(data, matrix):
    node, step = _first_step(data, "definite")
    step[-1][0][0] = step[1]               # q itself is not among the customers q frees
    return f"node {node['id']}: definite on {step[1]}, an edge from q itself"


def _better_drop_edge(data, matrix):
    node, step = _first_step(data, "better", 1)
    if step is None:
        return "no better step with a matching edge"
    step[-1].pop()
    return f"node {node['id']}: better ({step[1]}, {step[2]}), one edge removed"


def _strip_matching(data, matrix):
    node, step = _first_step(data, "definite")
    step.pop()
    return f"node {node['id']}: definite on {step[1]}, matching stripped (a published step)"


CORRUPTIONS = {"drop an edge": _drop_edge, "repeat a stack": _repeat_stack,
               "repeat a customer": _repeat_customer, "stack not newly opened": _stack_not_opened,
               "customer not freed": _customer_not_freed,
               "better: drop an edge": _better_drop_edge,
               "strip the matching": _strip_matching}


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _band(n):
    for lo, hi in BANDS:
        if lo <= n <= hi:
            return f"{lo}–{hi}"
    return f"{n}"


def tables() -> str:
    frame = pd.read_csv(CSV)
    frame["band"] = frame.n.map(_band)
    frame["band_lo"] = frame.n.map(lambda n: next((lo for lo, hi in BANDS if lo <= n <= hi), n))
    parts = ["# Certificates for the repaired rules: tables (loop0008 item 05)", "",
             f"*Generated by `python -m paper2.certificates --stage tables` from `{CSV}`: "
             f"{len(frame)} rows, {frame.instance_name.nunique()} instances at "
             f"{frame.n.min()}–{frame.n.max()} customers. Checker: `paper2/certificate_check.py`.*",
             ""]
    rows = []
    for (lo, band, config), part in frame.groupby(["band_lo", "band", "config"]):
        unsat = part[part.status == "unsat"]
        rows.append({"band": band, "config": config, "instances": len(part),
                     "refuted": len(unsat), "unknown (deadline)": int((part.status == "unknown").sum()),
                     "sat below optimum": int((part.status == "sat").sum()),
                     "verified": int((unsat.check_ok == True).sum()),
                     "rejected": int((unsat.check_ok == False).sum()),
                     "definite steps": int(unsat.steps_definite.sum()),
                     "better steps": int(unsat.steps_better.sum()),
                     "matching edges": int(unsat.matching_edges.sum()),
                     "nodes median / max": f"{unsat.nodes.median():.0f} / {unsat.nodes.max():.0f}" if len(unsat) else "",
                     "gz bytes median / max": f"{unsat.gz_bytes.median():.0f} / {unsat.gz_bytes.max():.0f}" if len(unsat) else "",
                     "check ms median / p90 / max": (f"{1000 * unsat.check_seconds.median():.2f} / "
                                                     f"{1000 * unsat.check_seconds.quantile(0.9):.1f} / "
                                                     f"{1000 * unsat.check_seconds.max():.0f}") if len(unsat) else "",
                     "check s total": round(unsat.check_seconds.sum(), 2),
                     "emit s total": round(unsat.emit_seconds.sum(), 1)})
    parts += ["## By size band and configuration", "",
              pd.DataFrame(rows).to_markdown(index=False), ""]
    rows = []
    for config, part in frame.groupby("config"):
        unsat = part[part.status == "unsat"]
        rows.append({"config": config, "instances": len(part), "verified": int((unsat.check_ok == True).sum()),
                     "rejected": int((unsat.check_ok == False).sum()),
                     "unknown": int((part.status == "unknown").sum()),
                     "nodes": int(unsat.nodes.sum()), "steps": int(unsat.steps.sum()),
                     "definite": int(unsat.steps_definite.sum()), "subset": int(unsat.steps_subset.sum()),
                     "better": int(unsat.steps_better.sum()), "matching edges": int(unsat.matching_edges.sum()),
                     "gz MB": round(unsat.gz_bytes.sum() / 1e6, 2),
                     "check s": round(unsat.check_seconds.sum(), 1),
                     "µs per node": round(1e6 * unsat.check_seconds.sum() / max(1, unsat.nodes.sum()), 1)})
    parts += ["## Totals per configuration", "", pd.DataFrame(rows).to_markdown(index=False), ""]
    unknown = frame[frame.status != "unsat"][["instance_name", "n", "m", "optimum", "config", "status",
                                               "branches", "emit_seconds"]]
    parts += ["## Not refuted within the deadline (or satisfiable)", "",
              unknown.to_markdown(index=False) if len(unknown) else "*(none)*", ""]
    bad = frame[frame.check_ok == False]
    parts += ["## Rejected", "", bad[["instance_name", "config", "check_reason"]].to_markdown(index=False)
              if len(bad) else "*(none)*", ""]
    text = "\n".join(parts)
    (OUT / "tables.md").write_text(text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", choices=("run", "failures", "tables"), default="tables")
    parser.add_argument("--min-customers", type=int, default=0)
    parser.add_argument("--max-customers", type=int, default=75)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--deadline", type=float, default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    if args.stage == "run":
        run(args.min_customers, args.max_customers, args.workers, args.deadline, limit=args.limit)
        print(tables())
    elif args.stage == "failures":
        print(json.dumps(failures(), indent=1))
    else:
        print(tables())


if __name__ == "__main__":
    main()
