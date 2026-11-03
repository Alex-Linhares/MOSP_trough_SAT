"""loop0013 item 11 (the reserve): F5, combinations of families — family E
(Harper) and family B (separator branches) evaluated on contraction minors
(family M) of the ten residual instances of item 08, where every family on
its own stops one to three stacks short of the optimum.

**Why a combination could add something.** On each of the ten the best floor
on record is a C-program refutation on a minor of 70–112 vertices (item 05),
whose pathwidth is therefore known exactly: no family evaluated on *that*
minor can exceed it. The C program decides nothing above 75–90% of the
vertices at its 10 s cap, and on such an undecided minor `H` its floor is only
the printed `lower` (the contraction degeneracy of `H`). Harper's bound on
`H` and the branch lemma on `H` are valid floors on `pw(H) <= pw(G)`
(`pathwidth_minorOf_le`), so the question is whether either reaches further
than the degeneracy there, and further than the refutation on the smaller
minor. Family E's *ceiling* on `H` (seeded with the certified witness's
layout lifted to `H`, so it never exceeds the optimum) bounds what E could
ever certify on `H`.

**Stage A** (`scan`): per instance, the least-c greedy sequence at 85, 90,
95, 97 and 99% of the vertices, the min-d one at 90 and 97%, the certifying
minor of item 05's search (a control) and the whole graph (read from the
record, nothing computed). Per minor: the C's floor (item 05's ladder point
where it ran the same minor, else one call at cap 10 s), E's ceiling
(`search_profile`, 20 s), E's cap-12 floor (`satisfiability.expansion_bound`
on the one-pattern-per-edge instance of `H`, 30 s, a censored level
discarded) and B (`branch_search`, 40 s, C cap 5 s, the lifted layout as its
upper bound). **Stage B** (`search`): item 04's tabu search over sequences
with E's cap-12 floor as the objective (15 s per evaluation), minors kept
in `[0.6 n, n]` (a smaller minor is pulled toward a clique, whose Harper
value is bounded by the contraction degeneracy already on record), 300 s
per instance.

**Certificates** (`obstruction-combo-1`): the sequence and the minor's hash
as `obstruction-minor-1`, and inside, a family-B certificate over the
minor's edge list or a family-E level certificate (SAT + DRAT at the argmax
level of the cap-12 profile, `t <= 12`) over the minor written as a
one-pattern-per-edge `.mosp` instance. `paper1/obstruction_check.py
check-combo` replays the sequence with its own code and runs `check-branch`
or `check-expansion` on the minor.

Stages:

    nice -n 19 python3 -m learning.obstruction_combo --stage scan --workers 8
    nice -n 19 python3 -m learning.obstruction_combo --stage search --workers 8
    nice -n 19 python3 -m learning.obstruction_combo --stage check --workers 4
    python3 -m learning.obstruction_combo --stage tables

Nothing here solves an instance: every optimum and every record value is
read from items 01–08's files, the C program runs on minors and branches
only, under caps, and nothing is written under `solutions/`.
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import argparse
import json
import random
import time
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from learning.obstruction_ledger import adjacency_from_matrix, corpus_instances
from learning.obstruction_expansion import (closed_masks, finished_sets, maximal_clique_seeds, search_profile,
                                            witness_layouts, solution_record, safe_name, matrix_sha256,
                                            write_standard_instance, exact_sat)
from learning.obstruction_minor import (replay, minor_graph, minor_masks, greedy_sequence, lifted_layout,
                                        vertex_separation, run_c, proved_pathwidth, Evaluator, search as minor_search,
                                        edges_sha256, edge_list, binary_sha256, MIN_MINOR)
from learning.obstruction_branch import branch_search, certificate_dict as branch_certificate, branch_widths

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = ROOT / "reports" / "scratch" / "obstruction_search"
OUT = SCRATCH / "11_combo"
MAP_CSV = SCRATCH / "08_map" / "map.csv"
M05_CERTS = SCRATCH / "05_minor_scale" / "certificates"
SCAN_CSV = OUT / "scan.csv"
SEARCH_CSV = OUT / "search.csv"
CERT_DIR = OUT / "certificates"
CHECKER_CSV = OUT / "checker_verdicts.csv"
TABLES_MD = OUT / "tables.md"
RUN_LOG = OUT / "run.log"

FORMAT = "obstruction-combo-1"
LEASTC_FRACTIONS = (0.85, 0.90, 0.95, 0.97, 0.99)
MIND_FRACTIONS = (0.90, 0.97)
C_CAP = 10.0                 # plan §0.5 (e), the 101–134 band
E_CEILING_SECONDS = 20.0
E_FLOOR_SECONDS = 30.0
E_CAP = 12
B_SECONDS = 40.0
B_C_CAP = 5.0
SAT_DEADLINE = 120.0
SEARCH_SECONDS = 300.0
SEARCH_EVAL_SECONDS = 15.0
SEARCH_MIN_FRACTION = 0.60
THEOREMS = ("pathwidth_minorOf_le / pathwidth_gt_of_minorOf (lean/MOSPFormalization/Minor.lean) lift the inner "
            "certificate's bound on the minor to G; mospValue_eq_pathwidth_add_one (MOSPGraph.lean); the inner "
            "certificate rests on its own theorems (obstruction-branch-1: branch_lemma_separator; "
            "obstruction-expansion-certificate-1: exists_closedNbhd_card_le, pathwidth_ge_of_unsat)")


def _rel(path: Path) -> str:
    path = Path(path)
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def log(msg: str, path: Path | None = None) -> None:
    path = path or RUN_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with path.open("a") as fh:
        fh.write(line + "\n")


# ----------------------------------------------------------------------------
# targets and the record
# ----------------------------------------------------------------------------


def residual_ten(map_csv: Path = MAP_CSV) -> pd.DataFrame:
    """The uncovered instances of the 338 (item 08's `map.csv`) less the one
    with the largest gap: ten rows, gap then size then name."""
    m = pd.read_csv(map_csv)
    g = m[m["is_gap338"] & (m["gap_best"] > 0)].sort_values(["gap_best", "n", "instance_name"])
    return g.iloc[:-1].reset_index(drop=True) if len(g) > 1 else g


def edge_instance_matrix(m: int, edges: list[tuple[int, int]]) -> np.ndarray:
    """The one-pattern-per-edge instance whose MOSP graph is the graph
    `(m, edges)`: column `j` has ones at the two ends of edge `j`, edges
    sorted `(a, b)`, `a < b`."""
    edges = sorted((min(a, b), max(a, b)) for a, b in edges)
    mat = np.zeros((m, max(1, len(edges))), dtype=int)
    for j, (a, b) in enumerate(edges):
        mat[a, j] = 1
        mat[b, j] = 1
    return mat


def c_layout_from_cert(cert: dict) -> list[int] | None:
    for line in cert.get("c_stdout") or []:
        parts = line.split()
        if parts and parts[0] == "layout":
            return [int(x) for x in parts[1:]]
    return None


# ----------------------------------------------------------------------------
# the three evaluations on a minor
# ----------------------------------------------------------------------------


def harper_floor_on(madj: list[int], seconds: float, cap: int = E_CAP) -> dict:
    """Family E's cap-`cap` branch-and-bound floor on a graph given as masks
    (optimum units), through `satisfiability.expansion_bound` on the
    one-pattern-per-edge instance; a censored level is discarded there."""
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound

    m = len(madj)
    edges = edge_list(madj)
    inst = MOSPInstance.from_matrix(edge_instance_matrix(m, edges), name="minor")
    b = expansion_bound(inst, max_t=cap, time_budget=float(seconds))
    levels = list(b.levels)
    arg = 0
    best = -1
    for t, f in enumerate(levels, 1):
        if f - t > best:
            best, arg = f - t, t
    return {"floor": int(b.value), "cap": int(b.cap), "levels": levels, "complete": bool(b.complete),
            "t_star": int(arg), "seconds": round(b.seconds, 3)}


def ceiling_on(madj: list[int], layouts: list[list[int]], seconds: float, rng_seed: int = 1) -> dict:
    """Family E's ceiling on a graph (optimum units) seeded with the finished
    sets of the given layouts and the maximal cliques; `<= vs(layout) + 1`
    for every layout given."""
    closed = closed_masks(madj)
    seeds: list[int] = []
    for lay in layouts:
        seeds += finished_sets(closed, lay)
    seeds += maximal_clique_seeds(madj)
    prof = search_profile(closed, seeds, seconds, rng_seed=rng_seed)
    ceiling, t_star = prof.harper()
    return {"ceiling": int(ceiling), "t_star": int(t_star), "fhat": prof.values,
            "set_at_t_star": prof.sets[t_star], "seconds": round(prof.seconds, 3)}


def branch_on(madj: list[int], position: list[int] | None, seconds: float, cap: float, rng_seed: int = 1) -> dict:
    res = branch_search(madj, seconds, cap, 2, rng_seed, position=position)
    return res


# ----------------------------------------------------------------------------
# certificates
# ----------------------------------------------------------------------------


def composite_dict(name: str, matrix, adj: list[int], seq: list[tuple[int, int]], labels: list[int],
                   edges: list[tuple[int, int]], inner_kind: str, inner_certificate: str, inner_instance: str,
                   floor: int, pathwidth_proved: int, optimum: int | None, label: str) -> dict:
    m = len(labels)
    return {
        "format": FORMAT, "instance_name": name, "n": len(adj),
        "matrix_sha256": matrix_sha256(matrix),
        "graph_sha256": edges_sha256(len(adj), edge_list(adj)), "graph_edges": len(edge_list(adj)),
        "sequence": [[int(v), int(u)] for v, u in seq],
        "sequence_note": "pairs [v, u] in the instance's customer labels (0-based rows): contract v into u, "
                         "u keeps its label; [v, -1] deletes an isolated v; every pair is an edge of the current graph",
        "minor_label": label, "m": m, "minor_labels": [int(x) for x in labels],
        "minor_edges": [[int(a), int(b)] for a, b in edges], "minor_sha256": edges_sha256(m, edges),
        "minor_sha256_note": 'SHA-256 of "m e\\n" then "a b\\n" per edge, sorted, a < b, labels 0..m-1 in increasing '
                             "order of the surviving representative",
        "inner_kind": inner_kind,
        "inner_certificate": inner_certificate,
        "inner_instance": inner_instance,
        "inner_note": "branch: an obstruction-branch-1 certificate over the minor's edge list (inner_instance, "
                      '"m e" then "a b" per line); expansion: an obstruction-expansion-certificate-1 over the minor '
                      "written as a one-pattern-per-edge .mosp instance (inner_instance), the DRAT proof beside it",
        "pathwidth_proved": int(pathwidth_proved), "floor": int(floor),
        "floor_units": "optimum units: pathwidth(minor) + 1 <= pathwidth(G) + 1 = MOSP",
        "optimum_on_record": optimum, "c_binary_sha256": binary_sha256(), "theorems": THEOREMS,
    }


def write_edge_list(path: Path, m: int, edges: list[tuple[int, int]]) -> None:
    path.write_text(f"{m} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges))


# ----------------------------------------------------------------------------
# stage A: the scan
# ----------------------------------------------------------------------------


def candidate_minors(adj: list[int], search_cert: dict | None) -> list[tuple[str, str, float | None, list[tuple[int, int]]]]:
    """(label, rule, fraction, sequence) for the ladder points, item 05's
    certifying minor and the whole graph."""
    n = len(adj)
    out = []
    for rule, fractions in (("least-c", LEASTC_FRACTIONS), ("min-d", MIND_FRACTIONS)):
        full = greedy_sequence(adj, 0, rule)
        for frac in fractions:
            size = max(MIN_MINOR, int(round(frac * n)))
            out.append((f"{rule}@{frac:.2f}", rule, frac, full[:max(0, n - size)]))
    if search_cert is not None:
        out.append((f"search@{search_cert['m']}", "search", None, [(int(v), int(u)) for v, u in search_cert["sequence"]]))
    out.append(("whole", "whole", 1.0, []))
    return out


def _scan_job(args) -> dict:
    name, matrix, ordering, optimum, record, rng_seed, write = args
    matrix = np.asarray(matrix, dtype=int)
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    opening, _ = witness_layouts(matrix, ordering)
    position = [0] * n
    for i, v in enumerate(opening):
        position[v] = i
    d05 = M05_CERTS / safe_name(name)
    search_cert = json.loads((d05 / "search.json").read_text()) if (d05 / "search.json").exists() else None
    ladder_points = json.loads((d05 / "ladder_points.json").read_text()) if (d05 / "ladder_points.json").exists() else []
    lp_index = {(r["rule"], round(float(r["fraction"]), 2)): r for r in ladder_points}
    rows, detail = [], {}
    cert_dir = CERT_DIR / safe_name(name)
    best_e, best_b = None, None
    for label, rule, frac, seq in candidate_minors(adj, search_cert):
        t0 = time.monotonic()
        cur, alive, branch = replay(adj, seq)
        labels, edges = minor_graph(cur, alive)
        m = len(labels)
        madj = minor_masks(m, edges)
        lifted = lifted_layout(labels, branch, position)
        vs_lift = vertex_separation(madj, lifted)
        lpos = [0] * m
        for i, v in enumerate(lifted):
            lpos[v] = i
        row = {"instance_name": name, "n": n, "optimum": int(optimum), "record_best": int(record["best"]),
               "record_gap": int(record["gap_best"]), "label": label, "rule": rule, "fraction": frac, "m": m,
               "m_over_n": round(m / n, 3), "edges": len(edges), "vs_lifted": vs_lift, "upper_pw": vs_lift}
        layouts = [lifted]
        c_sec = 0.0
        if rule == "whole":
            row.update({"c_floor": None, "c_source": "not run (whole graph)", "c_width": None,
                        "e_ceiling": record["e_ceiling"], "e_t_star": None,
                        "e_floor12": record["e_floor"], "e_cap": None, "e_complete": None,
                        "b_value": record["b_value"] if pd.notna(record["b_value"]) else None, "b_potential": None,
                        "e_source": "record (items 02–03)", "b_source": "record (item 06)"})
            row["combo_floor"] = int(record["best"])
            row["seconds"] = round(time.monotonic() - t0, 3)
            rows.append(row)
            continue
        if rule == "search":
            cw = search_cert.get("c_width")
            row.update({"c_floor": int(search_cert["floor"]), "c_source": "item05:" + str(search_cert["floor_source"]),
                        "c_width": cw})
            lay = c_layout_from_cert(search_cert)
            if lay is not None and len(lay) == m:
                layouts.append(lay)
                row["upper_pw"] = min(row["upper_pw"], vertex_separation(madj, lay))
        else:
            lp = lp_index.get((rule, round(frac, 2)))
            if lp is not None and int(lp["m"]) == m and lp["source"] != "skipped":
                row.update({"c_floor": int(lp["floor"]), "c_source": "item05:" + str(lp["source"]), "c_width": None})
            else:
                c = run_c(graph6_of(m, edges), C_CAP)
                c_sec += c["seconds"]
                pw, source = proved_pathwidth(c)
                row.update({"c_floor": (pw + 1) if pw is not None else None, "c_source": source, "c_width": c["width"]})
                if c["layout"] is not None and len(c["layout"]) == m:
                    layouts.append(c["layout"])
                    row["upper_pw"] = min(row["upper_pw"], vertex_separation(madj, c["layout"]))
        # E's ceiling and floor
        ce = ceiling_on(madj, layouts, E_CEILING_SECONDS, rng_seed)
        hf = harper_floor_on(madj, E_FLOOR_SECONDS)
        row.update({"e_ceiling": ce["ceiling"], "e_t_star": ce["t_star"], "e_ceiling_seconds": ce["seconds"],
                    "e_floor12": hf["floor"], "e_cap": hf["cap"], "e_complete": hf["complete"],
                    "e_floor_t_star": hf["t_star"], "e_floor_seconds": hf["seconds"], "e_source": "computed"})
        # B
        br = branch_on(madj, lpos, B_SECONDS, B_C_CAP, rng_seed)
        node = br["node"]
        row.update({"b_value": (br["value"] + 1) if br["value"] >= 0 else None,
                    "b_potential": (br["stats"]["best_potential"] + 1) if br["stats"]["best_potential"] > 0 else None,
                    "b_S_size": len(br["S"]) if br["S"] else None,
                    "b_branch_sizes": json.dumps([len(b["vertices"]) for b in node["branches"]]) if node else None,
                    "b_branch_widths": json.dumps(branch_widths(node)) if node else None,
                    "b_c_calls": br["stats"]["c_calls"], "b_seconds": round(br["stats"]["seconds"], 3), "b_source": "computed"})
        c_sec += br["stats"]["c_seconds"]
        floors = [v for v in (row["c_floor"], row["e_floor12"], row["b_value"]) if v is not None]
        row["combo_floor"] = max(floors) if floors else None
        row["c_seconds"] = round(c_sec, 3)
        row["seconds"] = round(time.monotonic() - t0, 3)
        rows.append(row)
        detail[label] = {"seq": seq, "labels": labels, "edges": edges, "levels": hf["levels"], "t_star": hf["t_star"],
                         "branch": br, "lifted_pos": lpos}
        if hf["levels"] and (best_e is None or hf["floor"] > best_e[0] or (hf["floor"] == best_e[0] and m < best_e[1])):
            best_e = (hf["floor"], m, label)
        if br["value"] >= 0 and (best_b is None or br["value"] + 1 > best_b[0] or (br["value"] + 1 == best_b[0] and m < best_b[1])):
            best_b = (br["value"] + 1, m, label)
    out = {"instance_name": name, "rows": rows, "e_cert": None, "e_sat_status": None, "b_cert": None}
    if write and (best_e or best_b):
        cert_dir.mkdir(parents=True, exist_ok=True)
        write_standard_instance(cert_dir / "instance.mosp", name, matrix)
    # the composite certificate for the best E-on-minor level: SAT + DRAT at (t*, f(t*) - 1)
    if write and best_e is not None:
        label = best_e[2]
        dd = detail[label]
        m, edges = len(dd["labels"]), dd["edges"]
        madj = minor_masks(m, edges)
        t_star = dd["t_star"]
        levels = dd["levels"]
        if t_star >= 1:
            b = levels[t_star - 1] - 1
            emat = edge_instance_matrix(m, edges)
            pdir = cert_dir / f"e_{safe_name(label)}"
            pdir.mkdir(parents=True, exist_ok=True)
            write_standard_instance(pdir / "instance.mosp", f"{name}::minor[{m}]", emat)
            res = exact_sat(closed_masks(madj), t_star, b, proof_dir=pdir, deadline=SAT_DEADLINE,
                            instance_name=f"{name}::minor[{m}]", matrix_sha=matrix_sha256(emat),
                            source_file=_rel(pdir / "instance.mosp"))
            out["e_sat_status"] = res["status"]
            out["e_sat_seconds"] = res.get("solve_seconds")
            out["e_sat_level"] = [t_star, b]
            out["e_sat_label"] = label
            if res["status"] == "unsat" and res.get("verdict") == "verified" and res.get("certificate"):
                comp = composite_dict(name, matrix, adj, dd["seq"], dd["labels"], edges, "expansion",
                                      f"{pdir.name}/t{t_star}_b{b}.json",
                                      f"{pdir.name}/instance.mosp", b + 2 - t_star, b + 1 - t_star, int(optimum), label)
                (cert_dir / "combo_expansion.json").write_text(json.dumps(comp, indent=1))
                out["e_cert"] = _rel(cert_dir / "combo_expansion.json")
    if write and best_b is not None:
        label = best_b[2]
        dd = detail[label]
        m, edges = len(dd["labels"]), dd["edges"]
        madj = minor_masks(m, edges)
        inner = branch_certificate(f"{name}::minor[{m}]", None, madj, dd["branch"], None, B_C_CAP)
        bdir = cert_dir / f"b_{safe_name(label)}"
        bdir.mkdir(parents=True, exist_ok=True)
        write_edge_list(bdir / "minor.txt", m, edges)
        (bdir / "branch.json").write_text(json.dumps(inner, indent=1))
        comp = composite_dict(name, matrix, adj, dd["seq"], dd["labels"], edges, "branch", f"{bdir.name}/branch.json",
                              f"{bdir.name}/minor.txt", inner["floor"], inner["pathwidth_proved"], int(optimum), label)
        (cert_dir / "combo_branch.json").write_text(json.dumps(comp, indent=1))
        out["b_cert"] = _rel(cert_dir / "combo_branch.json")
    return out


def graph6_of(m: int, edges: list[tuple[int, int]]) -> str:
    from learning.obstruction_minor import graph6

    return graph6(m, edges)


def _load_targets() -> list[tuple[str, np.ndarray, list[int], int, dict]]:
    ten = residual_ten()
    found = corpus_instances()
    out = []
    for _, r in ten.iterrows():
        name = r["instance_name"]
        _path, inst = found[name]
        rec = solution_record(name)
        if rec is None:
            raise SystemExit(f"no solution record for {name}")
        out.append((name, np.asarray(inst.matrix, dtype=int), list(rec["ordering"]), int(rec["mosp_value"]), r.to_dict()))
    return out


def run_scan(workers: int, rng_seed: int = 1, write: bool = True) -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = _load_targets()
    log(f"scan: {len(targets)} instances, {workers} workers, C cap {C_CAP} s, E ceiling {E_CEILING_SECONDS} s, "
        f"E floor {E_FLOOR_SECONDS} s at cap {E_CAP}, B {B_SECONDS} s at cap {B_C_CAP} s, SAT {SAT_DEADLINE} s")
    jobs = [(name, mat, order, opt, rec, rng_seed, write) for name, mat, order, opt, rec in targets]
    rows, meta = [], []
    t0 = time.monotonic()
    with Pool(workers) as pool:
        for i, res in enumerate(pool.imap_unordered(_scan_job, jobs), 1):
            rows += res["rows"]
            meta.append({k: v for k, v in res.items() if k != "rows"})
            best = max((r["combo_floor"] or 0) for r in res["rows"] if r["rule"] != "whole")
            rec = res["rows"][0]
            log(f"scan {i}/{len(jobs)} {res['instance_name']}: combo best on minors {best} vs record {rec['record_best']} "
                f"(optimum {rec['optimum']}); E SAT {res.get('e_sat_status')}; {time.monotonic() - t0:.0f} s")
    df = pd.DataFrame(rows)
    df.to_csv(SCAN_CSV, index=False)
    pd.DataFrame(meta).to_csv(OUT / "scan_meta.csv", index=False)
    log(f"scan done in {time.monotonic() - t0:.0f} s wall; {SCAN_CSV}")
    return df


# ----------------------------------------------------------------------------
# stage B: the search with E's floor as the objective
# ----------------------------------------------------------------------------


@dataclass
class HarperEvaluator(Evaluator):
    """`Evaluator` whose floor is family E's cap-12 floor on the minor
    (optimum units), never the C program; minors below `min_m` get 1."""
    eval_seconds: float = SEARCH_EVAL_SECONDS
    evaluations: int = 0
    seconds_e: float = 0.0

    def evaluate(self, seq, record_proposals: bool = False) -> dict:
        cur, alive, branch = replay(self.adj, seq)
        labels, edges = minor_graph(cur, alive)
        m = len(labels)
        key = edges_sha256(m, edges)
        if key in self.cache:
            res = dict(self.cache[key])
            res["cached"] = True
            return res
        res = {"m": m, "edges": edges, "labels": labels, "hash": key, "seq": list(seq), "floor": 1,
               "source": "out_of_range", "c": None, "cached": False, "levels": []}
        if m < self.min_m or m > self.max_m or self.done():
            self.out_of_range += 1
            self.cache[key] = res
            return res
        madj = minor_masks(m, edges)
        hf = harper_floor_on(madj, min(self.eval_seconds, max(0.5, self.time_left())))
        self.evaluations += 1
        self.seconds_e += hf["seconds"]
        res.update({"floor": hf["floor"], "source": f"harper_cap{hf['cap']}", "levels": hf["levels"],
                    "t_star": hf["t_star"], "complete": hf["complete"]})
        self.cache[key] = res
        if res["floor"] > self.best_floor or (res["floor"] == self.best_floor and m < self.best_m):
            self.best_floor, self.best_m, self.best = res["floor"], m, res
        return res


def _search_job(args) -> dict:
    name, matrix, ordering, optimum, record, rng_seed, seconds = args
    matrix = np.asarray(matrix, dtype=int)
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    starts = []
    for rule, fracs in (("least-c", (0.90, 0.97)), ("min-d", (0.90,))):
        full = greedy_sequence(adj, 0, rule)
        for frac in fracs:
            size = max(MIN_MINOR, int(round(frac * n)))
            starts.append((f"{rule}@{frac:.2f}", full[:max(0, n - size)]))
    # stage A's best E point, if the scan ran
    if SCAN_CSV.exists():
        s = pd.read_csv(SCAN_CSV)
        s = s[(s["instance_name"] == name) & (s["rule"] != "whole") & (s["rule"] != "search")]
        if len(s):
            best = s.sort_values(["e_floor12", "m"], ascending=[False, True]).iloc[0]
            rule, frac = best["rule"], float(best["fraction"])
            full = greedy_sequence(adj, 0, rule)
            size = max(MIN_MINOR, int(round(frac * n)))
            starts.insert(0, (f"scanbest:{rule}@{frac:.2f}", full[:max(0, n - size)]))
    t0 = time.monotonic()
    ev = HarperEvaluator(adj, int(optimum), 0.0, None, deadline=t0 + seconds, min_m=int(SEARCH_MIN_FRACTION * n), max_m=n)
    trace = minor_search(ev, rng_seed, starts=starts)
    best = ev.best
    start_values = {}
    for lab, sq in starts:
        labels, edges = minor_graph(*replay(adj, sq)[:2])
        hit = ev.cache.get(edges_sha256(len(labels), edges))
        start_values[lab] = hit["floor"] if hit else None
    row = {"instance_name": name, "n": n, "optimum": int(optimum), "record_best": int(record["best"]),
           "seconds_budget": seconds, "seconds": round(time.monotonic() - t0, 3), "evaluations": ev.evaluations,
           "e_seconds": round(ev.seconds_e, 3), "out_of_range": ev.out_of_range, "restarts": trace["restarts"],
           "moves": trace["moves"], "accepted": trace["accepted"], "improvements": trace["improvements"],
           "search_e_floor": ev.best_floor if best else None, "search_m": best["m"] if best else None,
           "search_cap": best.get("source") if best else None, "search_t_star": best.get("t_star") if best else None,
           "start_values": json.dumps(start_values),
           "beats_record": best is not None and ev.best_floor > int(record["best"])}
    return row


def run_search(workers: int, rng_seed: int = 1, seconds: float = SEARCH_SECONDS) -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = _load_targets()
    log(f"search: {len(targets)} instances, {workers} workers, {seconds:g} s each, {SEARCH_EVAL_SECONDS:g} s per "
        f"evaluation at cap {E_CAP}, minors in [{SEARCH_MIN_FRACTION:.2f} n, n]")
    jobs = [(name, mat, order, opt, rec, rng_seed, seconds) for name, mat, order, opt, rec in targets]
    rows = []
    t0 = time.monotonic()
    with Pool(workers) as pool:
        for i, row in enumerate(pool.imap_unordered(_search_job, jobs), 1):
            rows.append(row)
            log(f"search {i}/{len(jobs)} {row['instance_name']}: E floor {row['search_e_floor']} at m = {row['search_m']} "
                f"({row['evaluations']} evaluations) vs record {row['record_best']}; {time.monotonic() - t0:.0f} s")
    df = pd.DataFrame(rows)
    df.to_csv(SEARCH_CSV, index=False)
    log(f"search done in {time.monotonic() - t0:.0f} s wall; {SEARCH_CSV}")
    return df


# ----------------------------------------------------------------------------
# stage: check
# ----------------------------------------------------------------------------


def _check_job(args) -> dict:
    inst, cert = args
    import sys

    sys.path.insert(0, str(ROOT / "paper1"))
    import obstruction_check as oc  # noqa: E402

    t0 = time.monotonic()
    res = oc.check_combo(Path(inst), Path(cert), c_cap=B_C_CAP * 5)
    return {"certificate": _rel(cert), "instance_name": res.get("instance_name"),
            "inner_kind": res.get("inner_kind"), "m": res.get("m"), "floor_claimed": res.get("floor_claimed"),
            "floor_proved": (res.get("proves") or {}).get("mosp_at_least"), "verdict": res["verdict"],
            "checks": len(res["checks"]), "failed": sum(1 for c in res["checks"] if not c["ok"]),
            "first_failure": next((c["check"] for c in res["checks"] if not c["ok"]), ""),
            "seconds": round(time.monotonic() - t0, 3)}


def check_all(workers: int = 4) -> pd.DataFrame:
    jobs = []
    for d in sorted(CERT_DIR.iterdir()) if CERT_DIR.exists() else []:
        inst = d / "instance.mosp"
        for cert in ("combo_expansion.json", "combo_branch.json"):
            if (d / cert).exists() and inst.exists():
                jobs.append((str(inst), str(d / cert)))
    log(f"check: {len(jobs)} composite certificates, {workers} workers")
    rows = []
    with Pool(workers) as pool:
        for row in pool.imap_unordered(_check_job, jobs):
            rows.append(row)
            log(f"check {row['certificate']}: {row['verdict']} (floor {row['floor_claimed']}, proved {row['floor_proved']})")
    df = pd.DataFrame(rows)
    df.to_csv(CHECKER_CSV, index=False)
    return df


# ----------------------------------------------------------------------------
# stage: tables
# ----------------------------------------------------------------------------


def _md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)


def write_tables() -> str:
    s = pd.read_csv(SCAN_CSV)
    parts = ["# Item 11 (reserve, F5): generated tables\n"]
    minors = s[s["rule"] != "whole"].copy()
    # (a) per instance: the best of each family over the minors, the combination, the record
    agg = []
    for name, g in s.groupby("instance_name", sort=False):
        gm = g[g["rule"] != "whole"]
        gw = g[g["rule"] == "whole"].iloc[0]
        undecided = gm[gm["c_source"].astype(str).str.contains("c_lower|none")]
        agg.append({"instance": name, "optimum": gw["optimum"], "record_best": gw["record_best"], "record_gap": gw["record_gap"],
                    "minors": len(gm), "undecided_by_C": len(undecided),
                    "C_best": gm["c_floor"].max(), "E_floor12_best": gm["e_floor12"].max(),
                    "E_ceiling_max": gm["e_ceiling"].max(), "B_best": gm["b_value"].max(),
                    "combo_best": gm["combo_floor"].max(),
                    "E_floor12_on_undecided": undecided["e_floor12"].max() if len(undecided) else None,
                    "E_ceiling_on_undecided": undecided["e_ceiling"].max() if len(undecided) else None,
                    "B_on_undecided": undecided["b_value"].max() if len(undecided) else None,
                    "C_lower_on_undecided": undecided["c_floor"].max() if len(undecided) else None,
                    "E_floor12_whole": gw["e_floor12"], "E_ceiling_whole": gw["e_ceiling"],
                    "above_record": bool(gm["combo_floor"].max() > gw["record_best"])})
    a = pd.DataFrame(agg)
    parts.append("## (a) Per instance: the best of each family over the minors scanned, the combination, the record (optimum units)\n")
    parts.append(_md(a) + "\n")
    parts.append(f"\nCombination above the record on **{int(a['above_record'].sum())} of {len(a)}**; "
                 f"E's ceiling on an undecided minor at or above the optimum on "
                 f"{int((a['E_ceiling_on_undecided'] >= a['optimum']).sum())} of {len(a)}.\n")
    # (b) the ladder curves
    parts.append("\n## (b) Every minor scanned: the C's floor, E's ceiling and cap-12 floor, B's value (optimum units)\n")
    cols = ["instance_name", "label", "m", "m_over_n", "edges", "vs_lifted", "upper_pw", "c_floor", "c_source",
            "e_ceiling", "e_t_star", "e_floor12", "e_cap", "e_floor_t_star", "b_value", "b_potential", "b_branch_sizes",
            "combo_floor", "record_best", "optimum", "seconds"]
    parts.append(_md(s[cols]) + "\n")
    # (c) E on minors against E on the whole graph
    parts.append("\n## (c) Family E on the minors against the whole graph: ceiling and cap-12 floor by fraction (means over the ten)\n")
    byf = minors.groupby("label", sort=False).agg(m_over_n=("m_over_n", "mean"), e_ceiling=("e_ceiling", "mean"),
                                                   e_floor12=("e_floor12", "mean"), e_cap=("e_cap", "mean"),
                                                   b_value=("b_value", "mean"), c_floor=("c_floor", "mean"),
                                                   combo=("combo_floor", "mean"), record=("record_best", "mean"),
                                                   optimum=("optimum", "mean")).round(2).reset_index()
    parts.append(_md(byf) + "\n")
    # (d) the search
    if SEARCH_CSV.exists():
        se = pd.read_csv(SEARCH_CSV)
        parts.append("\n## (d) Stage B: the search over sequences with E's cap-12 floor as the objective\n")
        parts.append(_md(se[["instance_name", "n", "optimum", "record_best", "search_e_floor", "search_m", "search_cap",
                             "search_t_star", "evaluations", "e_seconds", "restarts", "moves", "accepted", "improvements",
                             "out_of_range", "start_values", "beats_record", "seconds"]]) + "\n")
        scan_best = minors.groupby("instance_name")["e_floor12"].max()
        se["scan_e_best"] = se["instance_name"].map(scan_best)
        parts.append(f"\nThe search's E floor above stage A's best E point on "
                     f"{int((se['search_e_floor'] > se['scan_e_best']).sum())} of {len(se)}; above the record on "
                     f"{int(se['beats_record'].sum())} of {len(se)}.\n")
    # (e) checker
    if CHECKER_CSV.exists():
        ck = pd.read_csv(CHECKER_CSV)
        parts.append("\n## (e) Checker verdicts on the composite certificates\n")
        parts.append(_md(ck[["certificate", "inner_kind", "m", "floor_claimed", "floor_proved", "verdict", "checks",
                             "failed", "first_failure", "seconds"]]) + "\n")
    meta_path = OUT / "scan_meta.csv"
    if meta_path.exists():
        me = pd.read_csv(meta_path)
        parts.append("\n## (f) The SAT call at the best E level per instance\n")
        parts.append(_md(me) + "\n")
    text = "\n".join(parts)
    TABLES_MD.write_text(text)
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", required=True, choices=["scan", "search", "check", "tables"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seconds", type=float, default=SEARCH_SECONDS)
    args = ap.parse_args()
    if args.stage == "scan":
        run_scan(args.workers, args.seed)
    elif args.stage == "search":
        run_search(args.workers, args.seed, args.seconds)
    elif args.stage == "check":
        check_all(args.workers)
    else:
        print(write_tables())


if __name__ == "__main__":
    main()
