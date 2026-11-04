"""Adaptive checkpoints: how many does a refutation need when they are chosen well?

Counterexample-guided refinement over `learning.checkpoint_bound`'s relaxation
CHK(sizes, b). Start from one checkpoint; a SAT answer gives nested sets
`S_1 subset ... subset S_c`. Each segment `(A, B)` of the chain (with
`A = emptyset` before the first and `B = V` after the last) is then asked
exactly: is there a layout of `B \\ A` after `A` with every intermediate prefix
of boundary at most `b`? That is CHK over the sizes strictly between `|A|` and
`|B|` with `A` forced in and `V \\ B` forced out, a problem on `|B \\ A|`
vertices. If every segment fills, the chain extends to a full layout and the
relaxation is tight at this `b` (`vs <= b`). Otherwise a checkpoint is added
at the midpoint of each segment that does not fill, and the relaxation is
asked again. UNSAT ends the refinement: the checkpoint set in hand certifies
`vs >= b + 1`, and its size is the measurement.

The even grids of the pilot say sixteen evenly spaced checkpoints close
18 of 66 instances at 30-50 customers; this asks whether a few well-placed
ones do, which is the difference between a compact certificate and a diffuse
one.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

from learning.checkpoint_bound import OUT, checkpoint_cnf, mask_to_list, pilot_population, sets_from_model, \
    check_witness, SAT_BACKEND
from learning.obstruction_expansion import closed_masks_from_matrix


def _solve(clauses, conflicts):
    from pysat.solvers import Solver

    solver = Solver(name=SAT_BACKEND, bootstrap_with=clauses)
    try:
        if conflicts is not None:
            solver.conf_budget(int(conflicts))
            answer = solver.solve_limited()
        else:
            answer = solver.solve()
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats() or {}
    finally:
        solver.delete()
    return answer, model, int(stats.get("conflicts", 0))


def segment_fills(closed: list[int], A: int, B: int, b: int, conflicts: int | None) -> bool | None:
    """Exact: can `B \\ A` be laid out after `A` with every prefix boundary <= b?"""
    n = len(closed)
    a, bb = bin(A).count("1"), bin(B).count("1")
    if bb - a <= 1:
        return True
    sizes = list(range(a + 1, bb))
    clauses, nv, var_map = checkpoint_cnf(closed, sizes, b)
    for j in range(len(sizes)):
        for v in range(n):
            if A >> v & 1:
                clauses.append([var_map["s"][j][v]])
            elif not (B >> v & 1):
                clauses.append([-var_map["s"][j][v]])
    answer, model, _ = _solve(clauses, conflicts)
    if answer is True:
        sets = sets_from_model(closed, model, sizes, var_map)
        check_witness(closed, sets, sizes, b)
        assert all((S & ~B) == 0 and (A & ~S) == 0 for S in sets)
    return answer


def refine(closed: list[int], b: int, start: list[int] | None = None, conflicts: int | None = None,
           max_rounds: int = 10_000) -> dict:
    """Returns the checkpoint set at the end, the answer (`unsat`: vs >= b+1 with
    these checkpoints; `sat`: a full layout of vs <= b exists; `censored`),
    the rounds and the total conflicts."""
    n = len(closed)
    sizes = sorted(set(start or [n // 2]))
    rounds = 0
    total_conf = 0
    t0 = time.monotonic()
    while rounds < max_rounds:
        rounds += 1
        clauses, nv, var_map = checkpoint_cnf(closed, sizes, b)
        answer, model, conf = _solve(clauses, conflicts)
        total_conf += conf
        if answer is False:
            return {"answer": "unsat", "sizes": sizes, "rounds": rounds, "conflicts": total_conf,
                    "seconds": time.monotonic() - t0}
        if answer is None:
            return {"answer": "censored", "sizes": sizes, "rounds": rounds, "conflicts": total_conf,
                    "seconds": time.monotonic() - t0}
        sets = sets_from_model(closed, model, sizes, var_map)
        check_witness(closed, sets, sizes, b)
        chain = [0] + sets + [(1 << n) - 1]
        bounds = [0] + sizes + [n]
        added = []
        for j in range(len(chain) - 1):
            fills = segment_fills(closed, chain[j], chain[j + 1], b, conflicts)
            if fills is None:
                return {"answer": "censored", "sizes": sizes, "rounds": rounds, "conflicts": total_conf,
                        "seconds": time.monotonic() - t0}
            if not fills:
                mid = (bounds[j] + bounds[j + 1]) // 2
                if bounds[j] < mid < bounds[j + 1] and mid not in sizes:
                    added.append(mid)
        if not added:
            return {"answer": "sat", "sizes": sizes, "rounds": rounds, "conflicts": total_conf,
                    "seconds": time.monotonic() - t0}
        sizes = sorted(set(sizes) | set(added))
    return {"answer": "censored", "sizes": sizes, "rounds": rounds, "conflicts": total_conf,
            "seconds": time.monotonic() - t0}


def _init():
    os.nice(19)


def _job(args):
    name, matrix, optimum, harper_ref, conflicts = args
    closed = closed_masks_from_matrix(matrix)
    n = len(closed)
    out = []
    # the certifying level first; if it censors, the next level down, to the Harper floor
    for b in range(optimum - 2, max(0, harper_ref - 2) - 1, -1):
        r = refine(closed, b, conflicts=conflicts)
        out.append({"instance_name": name, "n": n, "optimum": optimum, "harper_ref": harper_ref, "b": b,
                    "mosp_floor_if_unsat": b + 2, "answer": r["answer"], "checkpoints": len(r["sizes"]),
                    "sizes": " ".join(map(str, r["sizes"])), "rounds": r["rounds"], "conflicts": r["conflicts"],
                    "seconds": round(r["seconds"], 3)})
        if r["answer"] == "unsat":
            break
    return out


def run(workers: int, n_max: int, conflicts: int, out_dir: Path, n_min: int = 0) -> None:
    from learning.obstruction_ledger import corpus_instances

    out_dir.mkdir(parents=True, exist_ok=True)
    pop = pilot_population(n_max)
    pop = pop[pop.n >= n_min]
    found = corpus_instances()
    jobs = [(r.instance_name, found[r.instance_name][1].matrix, int(r.optimum), int(r.harper_ref), conflicts)
            for r in pop.itertuples()]
    jobs.sort(key=lambda j: -j[1].shape[0])
    path = out_dir / "refine.csv"
    fields = ["instance_name", "n", "optimum", "harper_ref", "b", "mosp_floor_if_unsat", "answer", "checkpoints",
              "sizes", "rounds", "conflicts", "seconds"]
    print(f"{time.strftime('%F %T')} refine: {len(jobs)} instances (n <= {n_max}), {workers} workers, conflicts {conflicts}", flush=True)
    k = 0
    with open(path, "w", newline="") as fh, Pool(workers, initializer=_init) as pool:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for rows in pool.imap_unordered(_job, jobs):
            for row in rows:
                w.writerow(row)
                k += 1
                print(f"{time.strftime('%T')} {row['instance_name'][:28]:28} n={row['n']:3} opt {row['optimum']:3} "
                      f"harper {row['harper_ref']:3} b={row['b']:3} {row['answer']:8} checkpoints {row['checkpoints']:3} "
                      f"rounds {row['rounds']:3} {row['seconds']}s sizes {row['sizes']}", flush=True)
            fh.flush()
    print(f"{time.strftime('%F %T')} refine done: {k} rows -> {path}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--n-max", type=int, default=50)
    ap.add_argument("--n-min", type=int, default=0)
    ap.add_argument("--conflicts", type=int, default=2_000_000)
    ap.add_argument("--out", type=Path, default=OUT / "refine")
    a = ap.parse_args()
    run(a.workers, a.n_max, a.conflicts, a.out, a.n_min)


if __name__ == "__main__":
    main()
