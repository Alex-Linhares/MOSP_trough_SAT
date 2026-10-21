"""Section 4's dataset: every instance of a problem proved exactly equivalent
to pathwidth, deduplicated by isomorphism, with its value, provenance and a
witness layout (loop0008 item 04; the definition is `paper1/dataset.md`).

Stages, each resumable, all writing under `paper1/data/dataset/`:

    python -m paper1.dataset index  --workers 4   # read every source, nauty certificates -> index.csv.gz
    python -m paper1.dataset values               # values on record (solutions/, pathwidth_solver results,
                                                  # later runs under reports/scratch/: `fold`)
    python -m paper1.dataset run    --workers 4 --until <ISO time>   # witnesses and new runs -> run.csv, run_layouts.jsonl
    python -m paper1.dataset write                # pathwidth_dataset.jsonl.gz, classes.csv.gz, tables.md
    python -m paper1.dataset price                # price.md: the full certification run, by collection

The independent checker is `paper1/dataset_check.py`; it shares no code with
this module or with any solver.

Conventions.

- **The graph** of a MOSP or gate-matrix instance is its MOSP graph: one vertex
  per customer (net), a clique per pattern (gate). Its pathwidth plus one is
  the instance's optimum (`lean/MOSPFormalization/MOSPGraph.lean`). Graph
  collections are read as given (self-loops and parallel edges dropped).
- **Width** is the pathwidth, i.e. the vertex separation. A **layout** is a
  vertex order `L`; its width is `max_i |N(L[:i]) \\ L[:i]|`, the largest
  boundary of a prefix (the closing-order convention of section 4, §4.7).
- **Provenance**, as in `solutions/`: `certified:refutation` (a search
  refuted `width - 1`), `certified:bound` (the witness meets a lower bound,
  no refutation needed), `solution` (a witness only); and two that only
  later runs supply (`fold`): `certified:minor` (a search refuted
  `width - 1` on a contracted minor) and `certified:theorem` (a published
  theorem, proved in Lean, gives the width). For the graph
  collections the refutation is the repaired-rules run of 2026-10-02
  (`pathwidth_solver/bench/results/repaired/`, `paper1/solver_fix.md` item 08);
  this module only regenerates the witness, with the search told to stop at
  the recorded width, and never upgrades a provenance by itself except where
  its own descent proves it (`run` on collections never run before).

Nothing here writes to `solutions/`.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import bz2
import lzma
import multiprocessing as mp
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "paper1" / "benchmarks" / "raw"
BENCH = ROOT / "pathwidth_solver" / "bench" / "instances"
REPAIRED = ROOT / "pathwidth_solver" / "bench" / "results" / "repaired"
SOLUTIONS = ROOT / "solutions"
OUT = ROOT / "paper1" / "data" / "dataset"

BIG = 5000            # above this many vertices a graph is read by header only
ENGINE_MAX = 1024     # the C engine's limit per component (pathwidth_solver.native)

# Collections in priority order: a class's first collection here "owns" it in
# the after-deduplication counts.
COLLECTIONS = [
    # (key, problem, family)
    ("MOSP: Challenge 2005", "MOSP", "mosp"),
    ("MOSP: Challenge 2005 (second copy)", "MOSP", "mosp"),
    ("MOSP: Faggioli & Bentivoglio", "MOSP", "mosp"),
    ("MOSP: SCOOP", "MOSP", "mosp"),
    ("MOSP: Chu & Stuckey", "MOSP", "mosp"),
    ("MOSP: Carvalho & Soma 2015", "MOSP", "mosp"),
    ("MOSP: Frinhani et al. 2018, large", "MOSP", "mosp"),
    ("VLSI gate matrix circuits", "gate matrix layout / one-dimensional logic", "matrix"),
    ("VSPLIB trees", "vertex separation", "graph"),
    ("VSPLIB grids", "vertex separation", "graph"),
    ("VSPLIB Harwell-Boeing", "vertex separation", "graph"),
    ("Small (Marti et al. 2008)", "vertex separation", "graph"),
    ("Rome graphs", "pathwidth", "graph"),
    ("TreewidthLIB colouring", "pathwidth (treewidth collection)", "graph"),
    ("freetdi named graphs", "pathwidth (treewidth collection)", "graph"),
    ("freetdi control-flow graphs", "pathwidth (treewidth collection)", "graph"),
    ("PACE 2016", "pathwidth (treewidth collection)", "graph"),
    ("PACE 2017 exact", "pathwidth (treewidth collection)", "graph"),
    ("PACE 2017 heuristic", "pathwidth (treewidth collection)", "graph"),
    ("PACE 2017 bonus", "pathwidth (treewidth collection)", "graph"),
]
PROBLEM = {k: p for k, p, _ in COLLECTIONS}
PRIORITY = {k: i for i, (k, _, _) in enumerate(COLLECTIONS)}

# The pathwidth_solver result sets (bench/run.py SET) behind each graph collection.
RESULT_SETS = {
    "VSPLIB trees": ["vsplib-tree.csv"],
    "VSPLIB grids": ["vsplib-grids.csv"],
    "VSPLIB Harwell-Boeing": ["vsplib-hb.csv"],
    "Rome graphs": ["rome.csv", "rome_120s.csv", "rome_600s.csv", "rome_3600s.csv"],
    "TreewidthLIB colouring": ["coloring.csv"],
    "freetdi named graphs": ["named.csv", "named_w.csv"],
}

# Re-certification under the repaired rules (paper1/solver_fix.md, item 09): the four
# instances `paper1.solver_fix_split` was started on 2026-10-03, minus those its results
# file already records as refuted (read only; the run is the owner's).
SPLIT_RESULTS = ROOT / "paper1" / "data" / "solver_fix_split_results.csv"
SPLIT_STARTED_ON = {"Random-125-125-2-4_0", "Random-125-125-4-4_0", "Random-125-125-2-1_0",
                    "Random-125-125-2-5_0"}


def _in_flight() -> set[str]:
    done = set()
    if SPLIT_RESULTS.exists():
        with SPLIT_RESULTS.open() as fh:
            done = {r["instance_name"] for r in csv.DictReader(fh) if r["status"] == "unsat"}
    return SPLIT_STARTED_ON - done


IN_FLIGHT = _in_flight()

# Higher is better established. Everything at rank >= 2 is a certified pathwidth;
# `solution` is a witness only. A save never moves a value down this order.
PROV_RANK = {"certified:refutation": 5, "certified:theorem": 4, "certified:minor": 3,
             "certified:bound": 2, "solution": 1, "": 0}
CERTIFIED = tuple(p for p, r in PROV_RANK.items() if r >= 2)

# Problems the dataset covers, and each one's value as a function of the pathwidth
# w (paper1/equivalences.md; Lean in lean/MOSPFormalization/Complex/).
VALUES = {
    "pathwidth": 0, "vertex separation": 0, "Lengauer's vertex separator game": 0,
    "MOSP": 1, "gate matrix layout (incl. multiple PLA folding)": 1,
    "one-dimensional logic": 1, "interval thickness": 1, "narrowness": 1,
    "node search number": 1,
}


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------

def _graph_from_matrix(M: np.ndarray) -> tuple[int, list[tuple[int, int]]]:
    """MOSP graph of a customers x patterns 0/1 matrix: customers adjacent iff
    they share a pattern."""
    M = (np.asarray(M) > 0).astype(np.int32)
    A = (M @ M.T) > 0
    np.fill_diagonal(A, False)
    iu, ju = np.nonzero(np.triu(A, 1))
    return M.shape[0], list(zip(iu.tolist(), ju.tolist()))


def read_matrix_file(path: Path, transpose: bool) -> np.ndarray:
    """A single-instance matrix file: a header of two integers, then the 0/1
    rows. `transpose` turns a patterns x customers file into customers x patterns."""
    lines = [l.split() for l in path.read_text().splitlines() if l.strip()]
    rows = [list(map(int, l)) for l in lines[1:]]
    M = np.array(rows, dtype=np.int8)
    return M.T if transpose else M


def _edges_clean(n: int, pairs) -> tuple[int, list[tuple[int, int]]]:
    E = set()
    for u, v in pairs:
        if u != v:
            E.add((u, v) if u < v else (v, u))
    return n, sorted(E)


def read_graph_file(path: Path) -> tuple[int, list[tuple[int, int]]]:
    """Graph collections, 0-based vertices. Formats: PACE .gr(.xz), DIMACS .dgf,
    GraphML, VSPLIB / CMPLIB (`name line`, `n n m` or `n m`, edges)."""
    name = path.name
    if name.endswith(".graphml"):
        import networkx as nx
        G = nx.Graph(nx.read_graphml(path))
        idx = {v: i for i, v in enumerate(G.nodes)}
        return _edges_clean(len(idx), ((idx[u], idx[v]) for u, v in G.edges))
    opener = lzma.open if name.endswith(".xz") else bz2.open if name.endswith(".bz2") else open
    with opener(path, "rt") as fh:
        text = fh.read()
    lines = text.splitlines()
    if ".gr" in name or name.endswith(".dgf"):
        n, pairs = 0, []
        for line in lines:
            p = line.split()
            if not p or p[0] in ("c", "n", "x"):
                continue
            if p[0] == "p":
                n = int(p[2])
            elif p[0] == "e":
                pairs.append((int(p[1]) - 1, int(p[2]) - 1))
            elif p[0].isdigit():
                pairs.append((int(p[0]) - 1, int(p[1]) - 1))
        return _edges_clean(n, pairs)
    # VSPLIB / CMPLIB edge lists
    body = [l.split() for l in lines if l.strip()]
    if not body[0][0].isdigit():
        body = body[1:]
    n = int(body[0][0])
    pairs = [(int(p[0]) - 1, int(p[1]) - 1) for p in body[1:] if len(p) >= 2]
    return _edges_clean(n, pairs)


def pace_header(path: Path) -> tuple[int, int, str]:
    """`p tw n m` of a PACE file, and the sha256 of its uncompressed bytes."""
    opener = lzma.open if path.name.endswith(".xz") else bz2.open if path.name.endswith(".bz2") else open
    h = hashlib.sha256()
    n = m = -1
    with opener(path, "rb") as fh:
        first = True
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            if first:
                for line in chunk.split(b"\n"):
                    if line.startswith(b"p "):
                        _, _, a, b = line.split()[:4]
                        n, m = int(a), int(b)
                        break
                first = False
    return n, m, h.hexdigest()


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def _mosp_collection(path: Path) -> str:
    parts = path.parts
    if "ChallengeInstances2005" in parts:
        return "MOSP: Challenge 2005"
    sub = parts[parts.index("MOSP_Instances") + 1]
    return {"Challenge": "MOSP: Challenge 2005 (second copy)", "Chu_Stuckey": "MOSP: Chu & Stuckey",
            "SCOOP": "MOSP: SCOOP"}.get(sub, "MOSP: Faggioli & Bentivoglio")


def sources() -> list[dict]:
    """Every instance: `collection`, `source` (repo-relative path), `name`,
    `kind` (how to read it)."""
    out: list[dict] = []
    sys.path.insert(0, str(ROOT))
    from learning.dataset import enumerate_instances
    for path, inst in enumerate_instances(ROOT / "benchmarks" / "instances"):
        out.append(dict(collection=_mosp_collection(path), source=rel(path), name=inst.name, kind="mosp"))
    for p in sorted((RAW / "carvalho_soma2015" / "Carvalho_Soma").glob("Random*.txt")):
        # rows are customers, unlike the Chu & Stuckey files: the MOSP-graph density matches
        # Frinhani et al. (2018) S1 Table's D, and the values the PT-MOSP sheet publishes, only so
        out.append(dict(collection="MOSP: Carvalho & Soma 2015", source=rel(p), name=p.stem, kind="matrix"))
    for p in sorted((RAW / "frinhani2018_large" / "Frinhani").glob("Random*.txt")):
        out.append(dict(collection="MOSP: Frinhani et al. 2018, large", source=rel(p), name=p.stem, kind="matrix-T"))
    for p in sorted((RAW / "lorena_vlsi").glob("*.txt")):
        out.append(dict(collection="VLSI gate matrix circuits", source=rel(p), name=p.stem, kind="matrix"))

    def add(coll, paths):
        for p in paths:
            out.append(dict(collection=coll, source=rel(p), name=p.relative_to(BENCH).as_posix()
                            if BENCH in p.parents else p.name, kind="graph"))
    add("VSPLIB trees", sorted(p for p in (BENCH / "vsplib" / "tree").rglob("*") if p.is_file() and "MACOSX" not in str(p)))
    add("VSPLIB grids", sorted((BENCH / "vsplib" / "grids").glob("*.rnd")))
    add("VSPLIB Harwell-Boeing", sorted((BENCH / "vsplib" / "hb").glob("*.rnd")))
    add("Small (Marti et al. 2008)", sorted((RAW / "cmplib_small" / "unpacked" / "small").iterdir()))
    add("Rome graphs", sorted((BENCH / "rome").rglob("*.graphml")))
    add("TreewidthLIB colouring", sorted(p for p in (BENCH / "coloring").glob("*.dgf") if not p.name.endswith("-pp.dgf")))
    add("freetdi named graphs", sorted((BENCH / "named" / "gr").glob("*.gr")))
    add("freetdi control-flow graphs", sorted((RAW / "freetdi_CFGs" / "unpacked").rglob("*.gr")))
    p16 = RAW / "pace2016_tw" / "unpacked"
    add("PACE 2016", sorted([*p16.rglob("*.gr"), *p16.rglob("*.gr.xz"), *p16.rglob("*.gr.bz2")]))
    p17 = RAW / "pace2017_tw" / "unpacked" / "Treewidth-PACE-2017-instances-master" / "gr"
    add("PACE 2017 exact", sorted((p17 / "exact").glob("*.gr.xz")))
    add("PACE 2017 heuristic", sorted((p17 / "heuristic").glob("*.gr.xz")))
    add("PACE 2017 bonus", sorted((RAW / "pace2017_tw_bonus" / "unpacked").rglob("gr/*.gr.xz")))
    return out


def load(src: dict) -> tuple[int, list[tuple[int, int]]]:
    """The graph of a source, 0-based."""
    path = ROOT / src["source"]
    kind = src["kind"]
    if kind == "mosp":
        from mosp.instance import MOSPInstance
        for inst in MOSPInstance.from_benchmark_file(path):
            if inst.name == src["name"]:
                return _graph_from_matrix(np.asarray(inst.matrix))
        raise KeyError(src["name"])
    if kind == "matrix-T":
        return _graph_from_matrix(read_matrix_file(path, transpose=True))
    if kind == "matrix":
        return _graph_from_matrix(read_matrix_file(path, transpose=False))
    return read_graph_file(path)


def mosp_instance(src: dict):
    from mosp.instance import MOSPInstance
    for inst in MOSPInstance.from_benchmark_file(ROOT / src["source"]):
        if inst.name == src["name"]:
            return inst
    raise KeyError(src["name"])


# ---------------------------------------------------------------------------
# Index: invariants and nauty certificates
# ---------------------------------------------------------------------------

def _adj(n: int, edges) -> list[list[int]]:
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def components_max(n: int, adj) -> int:
    seen = [False] * n
    best = 0
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack, size = [s], 0
        while stack:
            u = stack.pop()
            size += 1
            for w in adj[u]:
                if not seen[w]:
                    seen[w] = True
                    stack.append(w)
        best = max(best, size)
    return best


def canon(n: int, edges) -> tuple[str, list[int]]:
    """nauty: a digest of the canonical certificate, and the canonical labelling
    (`lab[i]` is the vertex placed at canonical position `i`)."""
    import pynauty
    adj = _adj(n, edges)
    g = pynauty.Graph(n, directed=False, adjacency_dict={v: adj[v] for v in range(n) if adj[v]})
    cert = pynauty.certificate(g)
    lab = pynauty.canon_label(g)
    return hashlib.sha256(cert + f"|{n}".encode()).hexdigest()[:32], list(lab)


def _index_row(src: dict) -> dict:
    row = dict(src)
    t = time.perf_counter()
    path = ROOT / src["source"]
    if src["kind"] == "graph" and ".gr" in path.name and "PACE" in src["collection"]:
        n, m, sha = pace_header(path)
        if n > BIG:
            row.update(n=n, m=m, max_component="", cls="sha256:" + sha[:32], lab="", big=1,
                       seconds=round(time.perf_counter() - t, 3), error="")
            return row
    try:
        n, edges = load(src)
        adj = _adj(n, edges)
        cls, lab = canon(n, edges)
        row.update(n=n, m=len(edges), max_component=components_max(n, adj), cls="nauty:" + cls,
                   lab=" ".join(map(str, lab)), big=0, error="")
    except Exception as exc:  # recorded, not fatal
        row.update(n="", m="", max_component="", cls="", lab="", big=0,
                   error=f"{type(exc).__name__}: {exc}"[:120])
    row["seconds"] = round(time.perf_counter() - t, 3)
    return row


INDEX = OUT / "index.csv.gz"
INDEX_FIELDS = ["collection", "source", "name", "kind", "n", "m", "max_component", "big", "cls",
                "seconds", "error", "lab"]


def stage_index(workers: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    srcs = sources()
    done = {}
    if INDEX.exists():
        for r in read_csv(INDEX):
            done[(r["source"], r["name"])] = r
    wanted = {(s["source"], s["name"]) for s in srcs}
    done = {k: r for k, r in done.items() if k in wanted}
    todo = [s for s in srcs if (s["source"], s["name"]) not in done]
    print(f"{len(srcs)} sources, {len(todo)} to index", flush=True)
    # big PACE files and slow parses last, so progress is visible
    todo.sort(key=lambda s: (s["collection"].startswith("PACE"), s["collection"].startswith("MOSP: Frinhani")))
    rows = list(done.values())
    t0 = time.time()
    with mp.get_context("spawn").Pool(workers) as pool:
        for i, row in enumerate(pool.imap_unordered(_index_row, todo, chunksize=4)):
            rows.append(row)
            if i % 2000 == 0:
                print(f"  {i}/{len(todo)} {time.time() - t0:.0f} s", flush=True)
    write_csv(INDEX, rows, INDEX_FIELDS)
    errs = [r for r in rows if r.get("error")]
    print(f"index: {len(rows)} rows, {len(errs)} errors, {time.time() - t0:.0f} s")


# ---------------------------------------------------------------------------
# Values on record
# ---------------------------------------------------------------------------

def mosp_layout(inst, ordering) -> list[int]:
    """Customer closing order of a pattern sequence: customers sorted by the
    position of their last pattern (customers with no pattern first). Its
    width is at most the sequence's open-stack count minus one, because at
    the time the last customer of a prefix closes, every boundary customer is
    open too."""
    pos = {p: i for i, p in enumerate(ordering)}
    M = np.asarray(inst.matrix)
    last = []
    for c in range(M.shape[0]):
        ps = np.nonzero(M[c])[0]
        last.append(max(pos[int(p)] for p in ps) if len(ps) else -1)
    return sorted(range(M.shape[0]), key=lambda c: (last[c], c))


def layout_width(n: int, edges, layout) -> int:
    """Largest prefix boundary (|N(T) \\ T|) of a layout."""
    adj = _adj(n, edges)
    placed = [False] * n
    boundary = set()
    best = 0
    for v in layout:
        placed[v] = True
        boundary.discard(v)
        for w in adj[v]:
            if not placed[w]:
                boundary.add(w)
        best = max(best, len(boundary))
    return best


VALUES_CSV = OUT / "values.csv.gz"
VALUE_FIELDS = ["source", "name", "width", "provenance", "evidence", "layout", "certificate"]


def stage_values() -> None:
    """Values already on record: MOSP solutions (witness derived) and the
    repaired pathwidth_solver runs (width and proof, no witness)."""
    from satisfiability.mosp_solver import _solution_path
    idx = read_csv(INDEX)
    out = []
    for r in idx:
        if r["kind"] != "mosp":
            continue
        inst = mosp_instance(r)
        sp = _solution_path(inst, SOLUTIONS)
        if not sp.exists():
            continue
        sol = json.loads(sp.read_text())
        layout = mosp_layout(inst, sol["ordering"])
        prov = sol.get("provenance", "solution")
        ev = rel(sp)
        if inst.name in IN_FLIGHT:
            ev += "; re-certification under the repaired rules in flight (paper1/solver_fix.md item 09)"
        elif inst.name in SPLIT_STARTED_ON:
            ev += f"; re-certified under the repaired rules by {rel(SPLIT_RESULTS)}"
        out.append(dict(source=r["source"], name=r["name"], width=int(sol["mosp_value"]) - 1,
                        provenance=prov, evidence=ev, layout=" ".join(map(str, layout))))
    by_key = {}
    for r in idx:
        if r["kind"] == "graph" and BENCH.name in r["source"]:
            by_key[r["name"]] = r
    best: dict[str, dict] = {}
    for coll, files in RESULT_SETS.items():
        for f in files:
            for row in read_csv(REPAIRED / f):
                if row.get("error") or row["width"] in ("", None):
                    continue
                key = row["name"]
                prov = {"refutation": "certified:refutation", "bound": "certified:bound"}.get(row["proof"], "solution")
                cand = dict(source=by_key[key]["source"] if key in by_key else "", name=key,
                            width=int(row["width"]), provenance=prov,
                            evidence=f"{rel(REPAIRED / f)} (rules={row['rules']}, nodes={row['nodes']}, s={row['seconds']})",
                            layout="")
                old = best.get(key)
                if old is None or PROV_RANK[prov] > PROV_RANK[old["provenance"]] or \
                        (prov == old["provenance"] == "solution" and cand["width"] < old["width"]):
                    if old is not None and PROV_RANK[old["provenance"]] >= 2 and cand["width"] != old["width"]:
                        raise SystemExit(f"CONFLICT {key}: {old} vs {cand}")
                    best[key] = cand
    missing = [k for k in best if not best[k]["source"]]
    if missing:
        raise SystemExit(f"result rows with no indexed instance: {missing[:5]}")
    out.extend(best.values())
    out = fold(idx, out)
    write_csv(VALUES_CSV, out, VALUE_FIELDS)
    print(f"values: {len(out)} rows ({Counter(r['provenance'] for r in out)})")


# ---------------------------------------------------------------------------
# Results of later runs, folded in (no solver runs here)
# ---------------------------------------------------------------------------
#
# Each source below is a result file a run left under reports/scratch/. This
# stage reads it, maps each row to an indexed instance, checks the witness
# layout's width on that instance's own graph, and offers the row as a value.
# Nothing is re-solved. Two provenances come only from here:
#
# - `certified:minor`: a search refuted `width - 1` on a contracted minor
#   (pathwidth is minor-monotone: Lean `pathwidth_gt_of_minorOf`,
#   lean/MOSPFormalization/Minor.lean), plus a witness of `width`. The row
#   carries the contraction sequence where the run kept one.
# - `certified:theorem`: a published theorem, also proved in Lean, gives the
#   value, plus a witness of `width`. So far the grids: pw((h, w)-grid) =
#   min(h, w) (Ellis & Warren 2008, Theorem 4.1; Lean `pathwidth_grid`).

SCRATCH = ROOT / "reports" / "scratch"
ROME_STEP = SCRATCH / "minor_bound" / "rome_open_step.csv"
ROME_E2E = SCRATCH / "minor_bound" / "rome_open_e2e.csv"
ROME_UNLIMITED = SCRATCH / "rome_unlimited" / "results.csv"
OPEN_RUNS = [SCRATCH / "dataset_open" / f for f in
             ("results.csv", "results_quick.csv", "results_quick_rescued.csv",
              "results_unlimited.csv")]   # results_unlimited: the C program, no time limit (run_unlimited.py, 2026-10-21)
GRIDS = SCRATCH / "grids_theorem" / "grids.csv"
BENCH_ON = sorted((SCRATCH / "minor_bound").glob("bench_*_on.csv"))   # the minor-step benchmark runs
ROME_WITNESS = SCRATCH / "rome_witness" / "results.csv"   # witnesses for minor-proved widths kept by no run
GRID_THEOREM = dict(family="grid",
                    theorem="Ellis & Warren (2008), Theorem 4.1: the (h, w)-grid has pathwidth min(h, w)",
                    lean="MOSPFormalization.pathwidth_grid (lean/MOSPFormalization/Grid.lean)")
PROOF_PROV = {"refutation": "certified:refutation", "minor": "certified:minor", "bound": "certified:bound"}


def class_order(by: dict[str, list[dict]]) -> list[str]:
    """Classes in record-id order: `pwc-{i + 1:05d}` is the i-th."""
    return sorted(by, key=lambda c: (PRIORITY[by[c][0]["collection"]], by[c][0]["source"], by[c][0]["name"]))


def transport(layout, a: dict, b: dict) -> list[int]:
    """A layout of member `a` in member `b`'s labels, through the canonical labelling."""
    la = list(map(int, a["lab"].split()))
    lb = list(map(int, b["lab"].split()))
    pos = {v: i for i, v in enumerate(la)}
    return [lb[pos[v]] for v in layout]


def regenerate_contractions(member: dict, size: int, rule: str, refuted: int) -> dict:
    """The contraction sequence of a run that recorded only (size, rule): the
    greedy rule is deterministic (`pathwidth_solver/pathwidth/minor.py`,
    `contraction_sequence`), so it is rebuilt here. No search is run. Graphs as
    the run read them (`bench/readers.py`, widest component), mapped to this
    module's labels, which must agree."""
    sys.path.insert(0, str(ROOT / "pathwidth_solver"))
    sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
    import networkx as nx
    from readers import read_any
    from pathwidth.graph import masks_from_graph
    from pathwidth.minor import contraction_sequence, replay
    G = read_any(BENCH / member["name"])
    n, edges = load(member)
    # The bench readers number some formats from 1 (.dgf, .gr, VSPLIB), this module from 0.
    shift = 1 if set(G.nodes()) == set(range(1, n + 1)) else 0
    if G.number_of_nodes() != n or \
            sorted((min(a, b) - shift, max(a, b) - shift) for a, b in G.edges()) != edges:
        raise SystemExit(f"{member['name']}: the run's reader and this module disagree on the graph")
    comp = max(nx.connected_components(G), key=len)
    masks, labels = masks_from_graph(G.subgraph(comp))
    seq = contraction_sequence(masks, size, rule)
    minor, _, _ = replay(masks, seq)
    if len(minor) != size:
        raise SystemExit(f"{member['name']}: regenerated minor has {len(minor)} vertices, not {size}")
    # The run took its minor from the widest component; on a disconnected graph the
    # certificate first deletes every other vertex (deletion never raises pathwidth,
    # Lean `pathwidth_induce_le`), so that it replays on the whole graph.
    outside = [[v - shift, None] for v in G.nodes() if v not in comp]
    return dict(refuted=refuted, size=size, rule=rule,
                contractions=outside + [[labels[v] - shift, labels[u] - shift if u >= 0 else None] for v, u in seq],
                origin="regenerated from the run's (size, rule) by the deterministic contraction rule")


def _rank(row: dict) -> tuple:
    """Proved beats unproved; then the smaller width; then the provenance; then a stored witness."""
    return (PROV_RANK[row["provenance"]] >= 2, -int(row["width"]), PROV_RANK[row["provenance"]],
            bool(row.get("layout")))


def _consistent(rows: list[dict], what: str) -> None:
    """Proved widths agree, and no witnessed width is below a proved one."""
    proved = {int(r["width"]) for r in rows if PROV_RANK[r["provenance"]] >= 2}
    if len(proved) > 1:
        raise SystemExit(f"CONFLICT {what}: proved widths {sorted(proved)}: {rows}")
    if proved and min(int(r["width"]) for r in rows) < min(proved):
        raise SystemExit(f"CONFLICT {what}: a witness below the proved width {min(proved)}: {rows}")


def fold(idx: list[dict], base: list[dict]) -> list[dict]:
    """`base` (values on record) merged with the rows of the later runs above."""
    ok = [r for r in idx if not r["error"]]
    by: dict[str, list[dict]] = defaultdict(list)
    for r in ok:
        by[r["cls"]].append(r)
    for members in by.values():
        members.sort(key=lambda r: (PRIORITY[r["collection"]], r["source"], r["name"]))
    member = {(r["source"], r["name"]): r for r in ok}
    by_name = {r["name"]: r for r in ok if r["kind"] == "graph" and BENCH.name in r["source"]}
    base_vals = {(r["source"], r["name"]): r for r in base}
    ids = {f"pwc-{i + 1:05d}": c for i, c in enumerate(class_order(by))}
    run_layout = {}
    if RUN_LAYOUTS.exists():
        for line in RUN_LAYOUTS.read_text().splitlines():
            d = json.loads(line)
            run_layout[(d["cls"], d["task"])] = d["layout"]
    graphs: dict[tuple[str, str], tuple[int, list]] = {}

    def graph(m):
        key = (m["source"], m["name"])
        if key not in graphs:
            graphs[key] = load(m)
        return graphs[key]

    def row(m, width, prov, evidence, layout, certificate=None):
        """`layout=None`: a proved value with no witness of its width on record."""
        if layout is not None:
            n, edges = graph(m)
            lw = layout_width(n, edges, layout)
            if lw != width:
                raise SystemExit(f"{m['name']}: folded layout has width {lw}, not {width} ({evidence})")
        return dict(source=m["source"], name=m["name"], width=width, provenance=prov, evidence=evidence,
                    layout="" if layout is None else " ".join(map(str, layout)),
                    certificate=json.dumps(certificate, separators=(",", ":")) if certificate else "")

    def old_witness(m):
        """The class's witness as the current build stores it, in member m's labels."""
        rep, v = representative(by[m["cls"]], base_vals)
        if v is not None and v.get("layout"):
            lay = list(map(int, v["layout"].split()))
        else:
            lay = run_layout.get((m["cls"], "witness")) or run_layout.get((m["cls"], "solve"))
        if lay is None:
            raise SystemExit(f"{m['name']}: no stored witness to carry")
        return transport(lay, rep, m)

    cand: list[dict] = []
    witness = {r["name"]: r for r in read_csv(ROME_WITNESS)} if ROME_WITNESS.exists() else {}
    # 1. Rome, the minor step alone (width - 1 refuted on a minor; the width is the recorded one).
    e2e = {r["name"]: r for r in read_csv(ROME_E2E)} if ROME_E2E.exists() else {}
    for r in read_csv(ROME_STEP) if ROME_STEP.exists() else []:
        if r["closed"] != "True" or r["error"]:
            continue
        m, w = by_name[r["name"]], int(r["width"])
        cert = regenerate_contractions(m, int(r["size"]), r["rule"], w - 1)
        lay = old_witness(m)
        n, edges = graph(m)
        ev = (f"{rel(ROME_STEP)} (minor step: width - 1 refuted on a {r['size']}-vertex minor, "
              f"rule {r['rule']}, nodes={r['step_nodes']}, s={r['step_seconds']}; the run stored "
              f"(size, rule), not the contractions)")
        if layout_width(n, edges, lay) == w:
            ev += "; witness: the build's stored one"
        elif r["name"] in witness and witness[r["name"]]["layout"]:
            lay = json.loads(witness[r["name"]]["layout"])
            ev += f"; witness: a satisfiable search at width {w} in {rel(ROME_WITNESS)}"
        else:
            # the width came from a run that kept no layout, and the stored witness is wider:
            # the value is proved, its witness is not on record (no solver is run here)
            ev += (f"; no witness of width {w} on record (the stored one has width "
                   f"{layout_width(n, edges, lay)})")
            lay = None
        cand.append(row(m, w, "certified:minor", ev, lay, cert))
    # 2. Rome, the 48 left open by the step, no time limit.
    for r in read_csv(ROME_UNLIMITED) if ROME_UNLIMITED.exists() else []:
        if not r["width"]:
            continue
        m, w = by_name[r["name"]], int(r["width"])
        prov = PROOF_PROV.get(r["proof"], "solution")
        ev = f"{rel(ROME_UNLIMITED)} (proof={r['proof'] or 'none'}, nodes={r['nodes']}, s={r['seconds']})"
        cert = None
        if prov == "certified:minor":
            x = e2e.get(r["name"])
            if x and x["proof"] == "minor" and x["width"] == r["width"] and x["minor_size"]:
                cert = regenerate_contractions(m, int(x["minor_size"]), x["minor_rule"], w - 1)
                ev += (f"; contractions: the same width refuted on a {x['minor_size']}-vertex minor "
                       f"(rule {x['minor_rule']}) in {rel(ROME_E2E)}")
            else:
                ev += "; the run stored no contraction certificate"
        cand.append(row(m, w, prov, ev, json.loads(r["order"]), cert))
    # 3. The dataset's open classes: rows by record id, in the representative's labels.
    best: dict[str, tuple[dict, Path]] = {}
    for f in OPEN_RUNS:
        for r in read_csv(f) if f.exists() else []:
            if not r["width"] or r["finished"].startswith("skipped") or not r["order"]:
                continue
            if r.get("status") not in (None, "", "ok"):
                continue
            r = dict(r, provenance=PROOF_PROV.get(r["proof"], "solution"))
            if r["provenance"] == "solution" and int(r["width"]) >= int(r["recorded"]):
                continue                       # neither proved nor better
            old = best.get(r["id"])
            if old is not None:
                _consistent([old[0], r], r["id"])
                if _rank(r) <= _rank(old[0]):
                    continue
            best[r["id"]] = (r, f)
    for rid, (r, f) in sorted(best.items()):
        cls = ids[rid]
        m, _ = representative(by[cls], base_vals)
        n, edges = graph(m)
        if (n, len(edges)) != (int(r["n"]), int(r["m"])):
            raise SystemExit(f"{rid}: n, m of the row do not match {m['name']}")
        cert = json.loads(r["minor"]) if r["provenance"] == "certified:minor" and r["minor"] else None
        if cert is not None:
            cert["contractions"] = [[v, None if u is None or u < 0 else u] for v, u in cert["contractions"]]
            if cert["refuted"] != int(r["width"]) - 1:
                raise SystemExit(f"{rid}: minor refutes {cert['refuted']}, width is {r['width']}")
        ev = (f"{rel(f)} (record {rid}; proof={r['proof'] or 'none'}, nodes={r['nodes']}, s={r['seconds']}"
              + (f"; improves the recorded {r['recorded']}" if int(r["width"]) < int(r["recorded"]) else "") + ")")
        if r["provenance"] == "certified:minor" and cert is None:
            ev += "; the run stored no contraction certificate"
        cand.append(row(m, int(r["width"]), r["provenance"], ev, json.loads(r["order"]), cert))
    # 4. Grids: the theorem, with a witness meeting it.
    for r in read_csv(GRIDS) if GRIDS.exists() else []:
        if r["status"] != "certified:theorem":
            continue
        m, side = by_name[r["name"]], int(r["side"])
        if int(r["pathwidth"]) != side or int(r["n"]) != side * side:
            raise SystemExit(f"{r['name']}: not a {side} x {side} grid row")
        cand.append(row(m, side, "certified:theorem",
                        f"{rel(GRIDS)} ({side} x {side} grid; {GRID_THEOREM['theorem']}; "
                        f"Lean {GRID_THEOREM['lean']}); witness: "
                        + ("the recorded layout" if r["previous"] != "no record" else "the row-major layout"),
                        json.loads(r["layout"]), dict(GRID_THEOREM, h=side, w=side)))
    # 5. The minor-step benchmark runs (60 s per graph): widths proved there and not elsewhere.
    #    They stored (size, rule) and no layout: the contractions are regenerated, and the
    #    witness is the build's stored one when its width matches (otherwise none is on record).
    for f in BENCH_ON:
        for r in read_csv(f):
            if r.get("error") or r["proof"] not in ("minor", "refutation") or r["name"] not in by_name:
                continue
            m, w = by_name[r["name"]], int(r["width"])
            prov = PROOF_PROV[r["proof"]]
            cert = None
            if prov == "certified:minor" and r.get("minor_size") and r.get("minor_rule"):
                cert = regenerate_contractions(m, int(r["minor_size"]), r["minor_rule"], int(r["minor_refuted"]))
            lay = old_witness(m)
            n, edges = graph(m)
            ev = (f"{rel(f)} (proof={r['proof']}, nodes={r['nodes']}, s={r['seconds']}"
                  + (f"; minor of {r['minor_size']} vertices, rule {r['minor_rule']}" if cert else "") + ")")
            if layout_width(n, edges, lay) == w:
                ev += "; witness: the build's stored one"
            else:
                ev += (f"; no witness of width {w} on record (the stored one has width "
                       f"{layout_width(n, edges, lay)})")
                lay = None
            cand.append(row(m, w, prov, ev, lay, cert))
    # Merge: per instance, the better row; per class, no conflict. Monotone in both.
    out = {(r["source"], r["name"]): dict(r, certificate=r.get("certificate", "")) for r in base}
    changed = Counter()
    for c in cand:
        key = (c["source"], c["name"])
        old = out.get(key)
        if old is not None:
            _consistent([old, c], c["name"])
            if _rank(c) <= _rank(old):
                # the row on record keeps its provenance; a witness of the same width from a
                # later run is still a witness of it (a layout's width is checked above)
                if not old.get("layout") and c.get("layout") and int(c["width"]) == int(old["width"]):
                    old["layout"] = c["layout"]
                    old["evidence"] += f"; witness: {c['evidence']}"
                    changed["witness supplied"] += 1
                continue
        out[key] = c
        changed[(old["provenance"] if old else "none") + " -> " + c["provenance"]] += 1
    runs = {}
    if RUN_CSV.exists():
        for r in read_csv(RUN_CSV):
            if r["width"] and r["task"] == "solve":
                runs[r["cls"]] = dict(width=r["width"], provenance=r["proof"] or "solution")
    for cls, members in by.items():
        rows = [out[k] for k in ((m["source"], m["name"]) for m in members) if k in out]
        _consistent(rows + ([runs[cls]] if cls in runs else []), cls)
    print(f"fold: {len(cand)} candidate rows; changed {dict(changed)}")
    return list(out.values())


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

def classes() -> tuple[dict[str, list[dict]], dict[tuple[str, str], dict]]:
    idx = [r for r in read_csv(INDEX) if not r["error"]]
    vals = {(r["source"], r["name"]): r for r in read_csv(VALUES_CSV)} if VALUES_CSV.exists() else {}
    by: dict[str, list[dict]] = defaultdict(list)
    for r in idx:
        by[r["cls"]].append(r)
    for members in by.values():
        members.sort(key=lambda r: (PRIORITY[r["collection"]], r["source"], r["name"]))
    return by, vals


def representative(members: list[dict], vals) -> tuple[dict, dict | None]:
    """The member whose value is best established (provenance, then a stored
    witness, then collection priority)."""
    best, bv = members[0], None
    for r in members:
        v = vals.get((r["source"], r["name"]))
        if v is None:
            continue
        key = (PROV_RANK[v["provenance"]], bool(v["layout"]), -int(v["width"]))
        if bv is None or key > (PROV_RANK[bv["provenance"]], bool(bv["layout"]), -int(bv["width"])):
            best, bv = r, v
    return best, bv


# ---------------------------------------------------------------------------
# Run: regenerate witnesses, and solve collections never run
# ---------------------------------------------------------------------------

RUN_CSV = OUT / "run.csv"
RUN_LAYOUTS = OUT / "run_layouts.jsonl"
RUN_FIELDS = ["cls", "source", "name", "task", "n", "m", "target", "width", "proof", "nodes", "seconds", "error"]


def _pw_solve(args):
    """One task in a child process: ('witness', target) stops the descent at the
    recorded width (no refutation; the provenance stays the recorded one);
    ('solve', None) runs a full descent under the budget."""
    cls, src, task, target, budget = args
    sys.path.insert(0, str(ROOT / "pathwidth_solver"))
    import networkx as nx
    from pathwidth import solve
    n, edges = load(src)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    t = time.perf_counter()
    row = dict(cls=cls, source=src["source"], name=src["name"], task=task, n=n, m=len(edges),
               target=target if target is not None else "", error="")
    try:
        kw = dict(time_budget=budget, repaired_rules=True)
        if task == "witness":
            kw["lower"] = target
        sol = solve(G, **kw)
        width = layout_width(n, edges, sol.order)
        proof = "" if task == "witness" else {"refutation": "certified:refutation",
                                              "bound": "certified:bound"}.get(sol.proof, "solution")
        row.update(width=width, proof=proof, nodes=sol.nodes, layout=list(map(int, sol.order)))
    except Exception as exc:
        row.update(width="", proof="", nodes="", layout=None, error=f"{type(exc).__name__}: {exc}"[:120])
    row["seconds"] = round(time.perf_counter() - t, 3)
    return row


def run_tasks(budget_witness: float, budget_solve: float) -> list[tuple]:
    by, vals = classes()
    tasks = []
    for cls, members in by.items():
        if members[0]["big"] == "1" or cls.startswith("sha256:"):
            continue
        rep, v = representative(members, vals)
        if v is not None and v["layout"]:
            continue                       # MOSP witness on record
        if int(rep["max_component"] or 0) > ENGINE_MAX:
            continue                       # beyond the C engine; priced, not run
        src = dict(collection=rep["collection"], source=rep["source"], name=rep["name"], kind=rep["kind"])
        if v is not None:
            certified = PROV_RANK[v["provenance"]] >= 2
            tasks.append((cls, src, "witness", int(v["width"]), budget_witness if certified else budget_solve))
        elif not rep["collection"].startswith("MOSP: Frinhani"):
            tasks.append((cls, src, "solve", None, budget_solve))
    # cheapest first: small graphs, witnesses before solves
    tasks.sort(key=lambda t: (t[2] != "witness", int(by[t[0]][0]["n"] or 0)))
    return tasks


def stage_run(workers: int, until: str | None, budget_witness: float, budget_solve: float) -> None:
    deadline = datetime.fromisoformat(until).timestamp() if until else None
    done = set()
    if RUN_CSV.exists():
        done = {(r["cls"], r["task"]) for r in read_csv(RUN_CSV)}
    tasks = [t for t in run_tasks(budget_witness, budget_solve) if (t[0], t[2]) not in done]
    print(f"run: {len(tasks)} tasks ({Counter(t[2] for t in tasks)})", flush=True)
    new = not RUN_CSV.exists()
    fh = RUN_CSV.open("a", newline="")
    lay = RUN_LAYOUTS.open("a")
    w = csv.DictWriter(fh, fieldnames=RUN_FIELDS, extrasaction="ignore")
    if new:
        w.writeheader()
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers, maxtasksperchild=50) as pool:
        it = pool.imap_unordered(_pw_solve, tasks, chunksize=1)
        for i, row in enumerate(it):
            w.writerow(row)
            fh.flush()
            if row.get("layout") is not None:
                lay.write(json.dumps(dict(cls=row["cls"], task=row["task"], layout=row["layout"])) + "\n")
                lay.flush()
            if i % 500 == 0:
                print(f"  {i}/{len(tasks)} {time.time() - t0:.0f} s", flush=True)
            if deadline and time.time() > deadline:
                print("deadline reached; stopping", flush=True)
                pool.terminate()
                break
    fh.close()
    lay.close()


# ---------------------------------------------------------------------------
# Write the dataset
# ---------------------------------------------------------------------------

DATASET = OUT / "pathwidth_dataset.jsonl.gz"
CLASSES_CSV = OUT / "classes.csv.gz"
CLASS_FIELDS = ["id", "cls", "n", "m", "max_component", "width", "provenance", "witness",
                "owner", "collections", "members", "problems"]


def _perm_to_rep(member: dict, rep: dict) -> list[int] | None:
    """`perm[v]` = the representative's vertex that member vertex `v` maps to."""
    if member is rep or not member["lab"]:
        return None
    lm = list(map(int, member["lab"].split()))
    lr = list(map(int, rep["lab"].split()))
    perm = [0] * len(lm)
    for a, b in zip(lm, lr):
        perm[a] = b
    return perm


def stage_write() -> None:
    by, vals = classes()
    runs = {}
    if RUN_CSV.exists():
        for r in read_csv(RUN_CSV):
            runs[(r["cls"], r["task"])] = r
    layouts = {}
    if RUN_LAYOUTS.exists():
        for line in RUN_LAYOUTS.read_text().splitlines():
            d = json.loads(line)
            layouts[(d["cls"], d["task"])] = d["layout"]
    order = class_order(by)
    rows, problems_issue = [], []
    tmp = DATASET.with_suffix(".tmp")
    with gzip.open(tmp, "wt") as out:
        for i, cls in enumerate(order):
            members = by[cls]
            rep, v = representative(members, vals)
            rec_id = f"pwc-{i + 1:05d}"
            width = prov = None
            layout = None
            evidence = ""
            if v is not None:
                width, prov, evidence = int(v["width"]), v["provenance"], v["evidence"]
                if v["layout"]:
                    layout = list(map(int, v["layout"].split()))
                elif (cls, "witness") in layouts and runs[(cls, "witness")]["width"] not in ("", None):
                    lw = int(runs[(cls, "witness")]["width"])
                    if PROV_RANK[prov] >= 2 and lw < width:
                        raise SystemExit(f"CONFLICT {cls}: witness {lw} below proved {width}")
                    if lw == width or prov == "solution":
                        layout = layouts[(cls, "witness")]
                        if lw < width:
                            evidence += f"; witness regenerated below the recorded upper bound {width}"
                        elif lw > width:
                            evidence += f"; the recorded upper bound {width} has no stored witness"
                        width = lw
                    evidence += f"; witness regenerated by {rel(RUN_CSV)}"
            elif (cls, "solve") in runs and runs[(cls, "solve")]["width"] not in ("", None):
                r = runs[(cls, "solve")]
                width, prov = int(r["width"]), r["proof"]
                layout = layouts.get((cls, "solve"))
                evidence = f"{rel(RUN_CSV)} (rules=repaired, nodes={r['nodes']}, s={r['seconds']})"
            colls = sorted({m["collection"] for m in members}, key=PRIORITY.get)
            probs = sorted({PROBLEM[m["collection"]] for m in members})
            rows.append(dict(id=rec_id, cls=cls, n=rep["n"], m=rep["m"], max_component=rep["max_component"],
                             width="" if width is None else width, provenance=prov or "",
                             witness=int(layout is not None), owner=members[0]["collection"],
                             collections="; ".join(colls), members=len(members), problems="; ".join(probs)))
            if width is None or layout is None:
                continue                   # records hold only graphs with a witnessed value
            n, edges = load(rep)
            if layout_width(n, edges, layout) != width:
                raise SystemExit(f"{rec_id}: layout width != {width}")
            off = {p: w for p, w in VALUES.items()}
            rec = dict(
                id=rec_id, n=n, m=len(edges), edges=[list(e) for e in edges],
                width=width, provenance=prov, evidence=evidence, layout=layout,
                values={p: width + k for p, k in off.items()},
                problems=probs,
                members=[dict(collection=m["collection"], problem=PROBLEM[m["collection"]],
                              source=m["source"], name=m["name"],
                              **({"index_in_file": file_position(m)} if m["kind"] == "mosp" else {}),
                              to_representative=_perm_to_rep(m, rep)) for m in members],
            )
            if prov == "certified:bound":
                rec["lower_bound_certificate"] = minor_certificate(n, edges, width)
            cert = json.loads(v["certificate"]) if v is not None and v.get("certificate") else None
            if prov == "certified:minor" and cert is not None:
                rec["minor_certificate"] = cert
            if prov == "certified:theorem":
                if cert is None:
                    raise SystemExit(f"{rec_id}: certified:theorem without its theorem")
                rec["theorem"] = cert
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
    tmp.replace(DATASET)
    write_csv(CLASSES_CSV, rows, CLASS_FIELDS)
    print(f"write: {len(rows)} classes, {sum(r['witness'] for r in rows)} records")


_POSITIONS: dict[str, dict[str, int]] = {}


def file_position(member: dict) -> int:
    """Position (0-based) of a MOSP instance among the instances of its file."""
    src = member["source"]
    if src not in _POSITIONS:
        from mosp.instance import MOSPInstance
        _POSITIONS[src] = {inst.name: i for i, inst in enumerate(MOSPInstance.from_benchmark_file(ROOT / src))}
    return _POSITIONS[src][member["name"]]


def minor_certificate(n: int, edges, target: int) -> dict | None:
    """A minor of minimum degree >= target, as operations on the graph:
    `["d", v]` deletes v, `["c", v, u]` contracts edge vu into u. pw >= tw >=
    min degree of any minor. Tries MMD+ (min-d and least-c) and degeneracy."""
    if target <= 0:
        return dict(ops=[], min_degree=0)
    for rule in ("least-c", "min-d", "max-d", "delete"):
        adj = [set(a) for a in _adj(n, edges)]
        alive = set(range(n))
        ops = []
        while alive:
            v = min(alive, key=lambda x: (len(adj[x]), x))
            if len(adj[v]) >= target:
                return dict(ops=ops, min_degree=len(adj[v]))
            if rule == "delete" or not adj[v]:
                for w in adj[v]:
                    adj[w].discard(v)
                alive.discard(v)
                ops.append(["d", v])
                continue
            if rule == "least-c":
                u = min(adj[v], key=lambda c: (len(adj[c] & adj[v]), c))
            elif rule == "min-d":
                u = min(adj[v], key=lambda c: (len(adj[c]), c))
            else:
                u = max(adj[v], key=lambda c: (len(adj[c]), -c))
            for w in adj[v]:
                adj[w].discard(v)
                if w != u:
                    adj[w].add(u)
                    adj[u].add(w)
            adj[v] = set()
            alive.discard(v)
            ops.append(["c", v, u])
    return None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    opener = gzip.open if path.suffix == ".gz" else open
    tmp = path.with_name(path.name + ".tmp")
    with opener(tmp, "wt", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stage", choices=["index", "values", "run", "write", "price", "tables"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--until", default=None)
    ap.add_argument("--witness-budget", type=float, default=120.0)
    ap.add_argument("--solve-budget", type=float, default=30.0)
    a = ap.parse_args()
    sys.path.insert(0, str(ROOT))
    if a.stage == "index":
        stage_index(a.workers)
    elif a.stage == "values":
        stage_values()
    elif a.stage == "run":
        stage_run(a.workers, a.until, a.witness_budget, a.solve_budget)
    elif a.stage == "write":
        stage_write()
    else:
        from paper1.dataset_price import main as price_main
        price_main(a.stage)


if __name__ == "__main__":
    main()
