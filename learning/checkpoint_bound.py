"""The checkpoint relaxation of vertex separation: nested prefixes at a few sizes.

A layout of `G` with vertex separation `vs` has, at every size `i`, a prefix
`S_i` whose inner boundary `|S_i| - |int(S_i)|` is at most `vs`, where
`int(S) = {v in S : N[v] subseteq S}`; and the prefixes are nested. Harper's
vertex-isoperimetric bound keeps one size and forgets the nesting:
`vs >= min_{|S| = i} (i - |int(S)|)` for every `i`. On the record's residual
that bound is exact and below the optimum (`reports/obstruction_search.md`),
so every single-prefix argument is dead there. This module keeps `c` sizes
`i_1 < ... < i_c` and the nesting between them:

    exists S_1 subset S_2 subset ... subset S_c, |S_j| = i_j,
           |S_j| - |int(S_j)| <= b for every j            (CHK(sizes, b))

UNSAT at `b` proves `vs >= b + 1`, i.e. `pw >= b + 1` and `MOSP >= b + 2`.
One checkpoint is Harper's bound at that size; `n - 1` checkpoints is the
exact problem. The question the pilot asks is how many checkpoints, and
which, the residual needs.

Encoding (per checkpoint `j`, vertex `v`): `s_j[v]` (v in S_j) and `c_j[v]`
(v claimed interior), with `c_j[v] -> s_j[u]` for every `u in N[v]`, nesting
`s_j[v] -> s_{j+1}[v]` and `c_j[v] -> c_{j+1}[v]` (the interior is monotone),
`|S_j| = i_j` and `|C_j| >= i_j - b` by totalizers. A model is checked by
recomputing the sets' boundaries from the masks, never from `c`.
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

from learning.obstruction_expansion import _totalizer, closed_masks_from_matrix, mask_to_list

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "scratch" / "checkpoint"
SAT_BACKEND = "cadical195"
SAT_TABLE = ROOT / "reports" / "scratch" / "obstruction_search" / "03_sat" / "instances.csv"


# ----------------------------------------------------------------------------
# encoding
# ----------------------------------------------------------------------------


def checkpoint_cnf(closed: list[int], sizes: list[int], b: int) -> tuple[list[list[int]], int, dict]:
    """CNF of CHK(sizes, b); returns `(clauses, n_vars, var_map)`."""
    n = len(closed)
    c = len(sizes)
    if c == 0 or any(not 1 <= i <= n - 1 for i in sizes) or any(sizes[j] >= sizes[j + 1] for j in range(c - 1)):
        raise ValueError(f"sizes must be strictly increasing in [1, n-1], got {sizes} for n={n}")
    if b < 0:
        raise ValueError("b must be >= 0")
    s = [[1 + j * n + v for v in range(n)] for j in range(c)]
    cl = [[1 + c * n + j * n + v for v in range(n)] for j in range(c)]
    next_var = 2 * c * n + 1
    clauses: list[list[int]] = []
    for j in range(c):
        for v in range(n):
            for u in mask_to_list(closed[v]):
                clauses.append([-cl[j][v], s[j][u]])
            if j + 1 < c:
                clauses.append([-s[j][v], s[j + 1][v]])
                clauses.append([-cl[j][v], cl[j + 1][v]])
    for j, i in enumerate(sizes):
        o, next_var = _totalizer(s[j], next_var, clauses)
        clauses.append([o[i - 1]])
        if i < n:
            clauses.append([-o[i]])
        need = i - b
        if need >= 1:
            oc, next_var = _totalizer(cl[j], next_var, clauses)
            clauses.append([oc[need - 1]])
    return clauses, next_var - 1, {"s": s, "c": cl}


def boundary(closed: list[int], S: int) -> int:
    """Inner boundary `|S| - |int(S)|` of the vertex set `S` (a mask)."""
    inside = sum(1 for v in mask_to_list(S) if closed[v] & ~S == 0)
    return bin(S).count("1") - inside


def sets_from_model(closed: list[int], model: list[int], sizes: list[int], var_map: dict) -> list[int]:
    n = len(closed)
    true = {lit for lit in model if lit > 0}
    out = []
    for j in range(len(sizes)):
        S = 0
        for v in range(n):
            if var_map["s"][j][v] in true:
                S |= 1 << v
        out.append(S)
    return out


def check_witness(closed: list[int], sets: list[int], sizes: list[int], b: int) -> None:
    """Raise unless the sets are nested, of the right sizes, and every boundary is <= b."""
    for j, (S, i) in enumerate(zip(sets, sizes)):
        if bin(S).count("1") != i:
            raise AssertionError(f"checkpoint {j}: |S| = {bin(S).count('1')} != {i}")
        if j + 1 < len(sets) and S & ~sets[j + 1]:
            raise AssertionError(f"checkpoint {j}: not nested")
        bd = boundary(closed, S)
        if bd > b:
            raise AssertionError(f"checkpoint {j}: boundary {bd} > {b}")


def decide(closed: list[int], sizes: list[int], b: int, conflicts: int | None = None,
           want_proof: bool = False) -> dict:
    """One CaDiCaL call on CHK(sizes, b). `answer` False means `vs >= b + 1`;
    True comes with checked witness sets; None is a conflict-budget censor."""
    from pysat.solvers import Solver

    clauses, nv, var_map = checkpoint_cnf(closed, sizes, b)
    solver = Solver(name=SAT_BACKEND, bootstrap_with=clauses, with_proof=want_proof)
    t0 = time.monotonic()
    try:
        if conflicts is not None:
            solver.conf_budget(int(conflicts))
            answer = solver.solve_limited()
        else:
            answer = solver.solve()
        seconds = time.monotonic() - t0
        stats = solver.accum_stats() or {}
        model = solver.get_model() if answer is True else None
        proof = b""
        if answer is False and want_proof:
            from learning.proofs import _read_proof
            proof = _read_proof(solver)
    finally:
        solver.delete()
    sets = None
    if answer is True:
        sets = sets_from_model(closed, model, sizes, var_map)
        check_witness(closed, sets, sizes, b)
    return {"answer": answer, "seconds": seconds, "conflicts": int(stats.get("conflicts", 0)),
            "n_vars": nv, "n_clauses": len(clauses), "sets": sets, "proof": proof}


def scan_down(closed: list[int], sizes: list[int], b_hi: int, b_lo: int, conflicts: int | None) -> dict:
    """Largest `b in [b_lo, b_hi]` with CHK(sizes, b) UNSAT, scanning down from
    `b_hi`: the first UNSAT is the answer (UNSAT is monotone in `b`). Returns
    `vs_floor = b + 1` (or None), the status and the call log."""
    calls = []
    censored = False
    for b in range(b_hi, b_lo - 1, -1):
        r = decide(closed, sizes, b, conflicts)
        calls.append({"b": b, "answer": r["answer"], "seconds": r["seconds"], "conflicts": r["conflicts"]})
        if r["answer"] is False:
            return {"vs_floor": b + 1, "status": "unsat_censored_above" if censored else "unsat", "calls": calls}
        if r["answer"] is None:
            censored = True  # a lower b is easier to refute: keep going
    return {"vs_floor": None, "status": "censored" if censored else "all_sat", "calls": calls}


# ----------------------------------------------------------------------------
# configurations
# ----------------------------------------------------------------------------


def even_sizes(n: int, c: int) -> list[int]:
    sizes = sorted({min(n - 1, max(1, round(j * n / (c + 1)))) for j in range(1, c + 1)})
    return sizes


def configs_for(n: int, full: bool) -> list[tuple[str, list[int]]]:
    out: list[tuple[str, list[int]]] = []
    for i in range(1, n):
        out.append((f"single:{i}", [i]))
    for c in (2, 3, 4, 6, 8, 12, 16):
        out.append((f"even:{c}", even_sizes(n, c)))
    grid = even_sizes(n, 8)
    for a in range(len(grid)):
        for b in range(a + 1, len(grid)):
            out.append((f"pair:{grid[a]},{grid[b]}", [grid[a], grid[b]]))
    if full:
        out.append(("full", list(range(1, n))))
    return out


# ----------------------------------------------------------------------------
# pilot driver
# ----------------------------------------------------------------------------


def pilot_population(n_max: int = 75) -> pd.DataFrame:
    d = pd.read_csv(SAT_TABLE)
    d = d[(d.n <= n_max) & (d.optimum > d.ceiling_after)].copy()
    d["settled_bool"] = d.settled.notna()
    d["harper_ref"] = np.where(d.settled_bool, d.floor_after, d.ceiling_after).astype(int)
    return d.sort_values(["n", "instance_name"]).reset_index(drop=True)


def _init():
    os.nice(19)


def _job(args) -> list[dict]:
    name, matrix, optimum, harper_ref, label, sizes, conflicts = args
    closed = closed_masks_from_matrix(matrix)
    b_hi = optimum - 2            # UNSAT here certifies the optimum (vs = optimum - 1)
    b_lo = max(0, harper_ref - 2)  # UNSAT here is what one checkpoint already gives
    t0 = time.monotonic()
    r = scan_down(closed, sizes, b_hi, b_lo, conflicts)
    return [{"instance_name": name, "n": len(closed), "optimum": optimum, "harper_ref": harper_ref,
             "config": label, "c": len(sizes), "sizes": " ".join(map(str, sizes)),
             "vs_floor": r["vs_floor"], "mosp_floor": (r["vs_floor"] + 1) if r["vs_floor"] is not None else None,
             "closes": (r["vs_floor"] is not None and r["vs_floor"] + 1 >= optimum),
             "status": r["status"], "calls": len(r["calls"]),
             "conflicts": sum(k["conflicts"] for k in r["calls"]), "seconds": round(time.monotonic() - t0, 3),
             "call_log": json.dumps(r["calls"])}]


def run_pilot(workers: int, conflicts: int, n_max: int, full_max: int, out_dir: Path, limit: int | None) -> None:
    from learning.obstruction_ledger import corpus_instances

    out_dir.mkdir(parents=True, exist_ok=True)
    pop = pilot_population(n_max)
    if limit:
        pop = pop.head(limit)
    found = corpus_instances()
    jobs = []
    for r in pop.itertuples():
        _, inst = found[r.instance_name]
        for label, sizes in configs_for(int(r.n), full=int(r.n) <= full_max):
            jobs.append((r.instance_name, inst.matrix, int(r.optimum), int(r.harper_ref), label, sizes, conflicts))
    # big first for the pool's tail
    jobs.sort(key=lambda j: (-len(j[5]) * j[1].shape[0], j[0]))
    path = out_dir / "pilot.csv"
    log = out_dir / "pilot.log"
    fields = ["instance_name", "n", "optimum", "harper_ref", "config", "c", "sizes", "vs_floor", "mosp_floor",
              "closes", "status", "calls", "conflicts", "seconds", "call_log"]
    done = set()
    if path.exists():
        done = {(r["instance_name"], r["config"]) for r in csv.DictReader(open(path))}
        jobs = [j for j in jobs if (j[0], j[4]) not in done]
    msg = (f"{time.strftime('%F %T')} checkpoint pilot: {len(pop)} instances (n <= {n_max}), {len(jobs)} configurations "
           f"({len(done)} already done), {workers} workers, conflicts {conflicts}, full encoding to n <= {full_max}")
    print(msg, flush=True)
    open(log, "a").write(msg + "\n")
    t0 = time.monotonic()
    k = 0
    with open(path, "a", newline="") as fh, Pool(workers, initializer=_init) as pool:
        w = csv.DictWriter(fh, fieldnames=fields)
        if not done:
            w.writeheader()
        for rows in pool.imap_unordered(_job, jobs, chunksize=4):
            for row in rows:
                w.writerow(row)
                k += 1
                if True:
                    line = (f"{time.strftime('%T')} {k}/{len(jobs)} {row['instance_name'][:28]:28} n={row['n']:3} "
                            f"opt {row['optimum']:3} harper {row['harper_ref']:3} {row['config']:12} -> mosp>={row['mosp_floor']} "
                            f"{'CLOSES' if row['closes'] else ''} {row['status']} {row['seconds']}s")
                    if row["closes"] or row["config"].startswith(("even", "full")) or row["status"] not in ("unsat",):
                        open(log, "a").write(line + "\n")
            fh.flush()
    msg = f"{time.strftime('%F %T')} pilot done: {k} rows in {time.monotonic() - t0:.0f} s"
    print(msg, flush=True)
    open(log, "a").write(msg + "\n")


def summarise(out_dir: Path) -> str:
    d = pd.read_csv(out_dir / "pilot.csv")
    d["kind"] = d.config.str.split(":").str[0]
    lines = []
    # best per instance and kind
    best = (d[d.status.str.startswith("unsat")].groupby(["instance_name", "n", "optimum", "harper_ref", "kind"])
            .mosp_floor.max().reset_index())
    best["gain"] = best.mosp_floor - best.harper_ref
    best["closes"] = best.mosp_floor >= best.optimum
    tab = best.groupby("kind").agg(instances=("instance_name", "nunique"), closes=("closes", "sum"),
                                   mean_gain=("gain", "mean"), max_gain=("gain", "max")).reset_index()
    lines.append("best floor per instance, by configuration family (optimum units; gain over the Harper reference):")
    lines.append(tab.to_string(index=False))
    ev = d[d.kind == "even"].copy()
    ev["closes"] = ev.closes.astype(bool)
    tab2 = ev.groupby("c").agg(instances=("instance_name", "nunique"), unsat=("status", lambda s: s.str.startswith("unsat").sum()),
                               censored=("status", lambda s: (s == "censored").sum()), closes=("closes", "sum"),
                               mean_floor_gain=("mosp_floor", lambda s: np.nan),
                               median_s=("seconds", "median"), max_s=("seconds", "max")).reset_index()
    ev_ok = ev[ev.status.str.startswith("unsat")]
    g = (ev_ok.mosp_floor - ev_ok.harper_ref).groupby(ev_ok.c).mean()
    tab2["mean_floor_gain"] = tab2.c.map(g)
    lines.append("\neven grids by number of checkpoints c:")
    lines.append(tab2.to_string(index=False))
    single = d[d.kind == "single"]
    hs = single[single.status.str.startswith("unsat")].groupby("instance_name").mosp_floor.max()
    ref = d.groupby("instance_name").harper_ref.first()
    cmp = pd.DataFrame({"single_best": hs, "harper_ref": ref}).dropna()
    lines.append(f"\nsanity: single-checkpoint best vs the Harper reference on {len(cmp)} instances: "
                 f"equal {(cmp.single_best == cmp.harper_ref).sum()}, above {(cmp.single_best > cmp.harper_ref).sum()}, "
                 f"below {(cmp.single_best < cmp.harper_ref).sum()}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pilot")
    p.add_argument("--workers", type=int, default=11)
    p.add_argument("--conflicts", type=int, default=300_000)
    p.add_argument("--n-max", type=int, default=75)
    p.add_argument("--full-max", type=int, default=50)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--out", type=Path, default=OUT / "pilot")
    s = sub.add_parser("summary")
    s.add_argument("--out", type=Path, default=OUT / "pilot")
    a = ap.parse_args()
    if a.cmd == "pilot":
        run_pilot(a.workers, a.conflicts, a.n_max, a.full_max, a.out, a.limit)
    else:
        print(summarise(a.out))


if __name__ == "__main__":
    main()
