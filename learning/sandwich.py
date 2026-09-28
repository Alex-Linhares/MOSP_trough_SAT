"""Is the sandwich `degeneracy ≤ pathwidth ≤ bandwidth` a theorem in the Lean development?

The Lean side is `lean/MOSPFormalization/Sandwich.lean`: it defines degeneracy
(both the Lick–White subgraph form and the elimination-ordering form) and
bandwidth over the repository's graph definitions, proves
`degeneracy ≤ vertexSeparation` and `vertexSeparation ≤ bandwidth`, and carries
them to pathwidth through `VSEquivPW` (Kinnersley), and proves the two
degeneracy forms equal by the greedy elimination ordering. Since loop0004
item 12 (2026-09-28) it also proves `treewidth ≤ pathwidth` (every path
decomposition is a tree decomposition on the path graph, which the file proves
is a tree) and the pathwidth branch lemma of Fellows & Langston (1987) /
Kinnersley (1992) — three disjoint connected branches of pathwidth ≥ k attached
to one vertex force pathwidth ≥ k + 1 — together with a Lean proof that the
statement previously carried with `sorry`, which lacked the attachment and
connectivity hypotheses, was false. One statement stands with `sorry`: item
09's fitted conjecture, left as a statement on purpose.

This module answers the two questions a proof about a definition leaves open:

1. **Do the Lean definitions compute the textbook quantities?**
   `degeneracy_subsets`, `ordering_degeneracy`, `bandwidth` and
   `vertex_separation` transcribe the Lean definitions literally (brute force
   over subsets and layouts) and are compared, on every graph on at most
   `--max-n` vertices (default 5, 1,044 graphs), with networkx's core number,
   with the exact pathwidth solver, and with each other (the proved equality
   `orderingDegeneracy = degeneracy` is checked exhaustively at that size as
   a guard on the two definitions).
2. **Which theorems rest on which axioms?** `--stage lean` runs `lake build`
   and `#print axioms` on every named theorem, recording whether `sorryAx`
   appears. The proved theorems must not use it; the stated ones must.

It also recounts the corpus check the plan cites (`g_degeneracy + 1 ≤ optimum
≤ bw_rcm + 1` on `learning/data/instances.csv`), so that the number in the
report is regenerated rather than copied.

Run::

    python -m learning.sandwich                       # everything, ~1 min
    python -m learning.sandwich --stage brute --max-n 5
    python -m learning.sandwich --stage lean
    python -m learning.sandwich --stage corpus

Writes `reports/sandwich_tables.md`. Nothing here is a bound, a solver change,
or written to `solutions/`.
"""
from __future__ import annotations

import argparse
import itertools
import re
import subprocess
import sys
import time
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "lean"
TABLES = ROOT / "reports" / "sandwich_tables.md"
INSTANCES = ROOT / "learning" / "data" / "instances.csv"

#: Theorems whose `#print axioms` must not mention `sorryAx`.
PROVED = (
    "vertexSeparation_le_bandwidth",
    "pathwidth_le_bandwidth",
    "pathwidth_le_bandwidthOfLayout",
    "degeneracy_le_orderingDegeneracy",
    "orderingDegeneracy_le_vertexSeparation",
    "degeneracy_le_vertexSeparation",
    "degeneracy_le_pathwidth",
    "degeneracy_le_pathwidth_le_bandwidth",
    "MOSPInstance.degeneracy_add_one_le_mospValue",
    "MOSPInstance.mospValue_le_bandwidth_add_one",
    "MOSPInstance.mospValue_eq_pathwidth_add_one",
    "MOSPInstance.mospValue_le_pathwidth_add_one",
    "MOSPInstance.pathwidth_add_one_le_mospValue",
    "degeneracy_deleteVertex_le",
    "exists_layout_maxLaterDegree_le_degeneracy",
    "orderingDegeneracy_le_degeneracy",
    "orderingDegeneracy_eq_degeneracy",
    # loop0004 item 12: the tree-decomposition section.
    "pathGraph_isTree",
    "pathGraph_induce_interval_connected",
    "PathDecomposition.toTreeDecomposition_width",
    "treewidth_le_pathwidth",
    "PathDecomposition.exists_mem_bag_of_connected",
    "PathDecomposition.exists_bag_subset_of_le_pathwidth_induce",
    "branch_lemma",
    "branch_lemma_treewidth",
    "MOSPInstance.treewidth_add_one_le_mospValue",
    "pathwidth_bot_fin4",
    "old_branch_statement_false",
)
#: Statements committed with `sorry`: item 09's fitted conjecture, kept as a statement.
STATED = (
    "conjecture_sqrt_tw_f6",
)


# ----------------------------------------------------------------------------
# The Lean definitions, transcribed
# ----------------------------------------------------------------------------

def degree_in(graph: nx.Graph, subset: frozenset, v) -> int:
    """`degreeIn G S v`: neighbours of `v` inside `S`."""
    return sum(1 for u in subset if graph.has_edge(v, u))


def min_degree_in(graph: nx.Graph, subset: frozenset) -> int:
    """`minDegreeIn G S`: the minimum induced degree, 0 on the empty set."""
    if not subset:
        return 0
    return min(degree_in(graph, subset, v) for v in subset)


def degeneracy_subsets(graph: nx.Graph) -> int:
    """`degeneracy G`: the largest minimum degree of an induced subgraph (Lick–White)."""
    nodes = list(graph.nodes())
    best = 0
    for r in range(1, len(nodes) + 1):
        for subset in itertools.combinations(nodes, r):
            best = max(best, min_degree_in(graph, frozenset(subset)))
    return best


def max_later_degree(graph: nx.Graph, layout: list) -> int:
    """`maxLaterDegree G σ`: the most neighbours any vertex has after itself."""
    pos = {v: k for k, v in enumerate(layout)}
    return max((sum(1 for u in graph.neighbors(v) if pos[u] > pos[v]) for v in layout),
               default=0)


def ordering_degeneracy(graph: nx.Graph) -> int:
    """`orderingDegeneracy G`: the minimum over layouts of `maxLaterDegree`."""
    nodes = list(graph.nodes())
    return min(max_later_degree(graph, list(p)) for p in itertools.permutations(nodes))


def bandwidth_of_layout(graph: nx.Graph, layout: list) -> int:
    """`bandwidthOfLayout G σ`: the largest stretch of an edge."""
    pos = {v: k for k, v in enumerate(layout)}
    return max((abs(pos[u] - pos[v]) for u, v in graph.edges()), default=0)


def bandwidth(graph: nx.Graph) -> int:
    """`bandwidth G`: the minimum over layouts of `bandwidthOfLayout`."""
    nodes = list(graph.nodes())
    return min(bandwidth_of_layout(graph, list(p)) for p in itertools.permutations(nodes))


def vertex_sep_at(graph: nx.Graph, layout: list, i: int) -> int:
    """`vertexSepAt G σ i`: suffix vertices after `i` with a neighbour at or before `i`."""
    prefix = set(layout[: i + 1])
    return sum(1 for v in layout[i + 1:] if any(u in prefix for u in graph.neighbors(v)))


def vertex_sep_of_layout(graph: nx.Graph, layout: list) -> int:
    """`vertexSepOfLayout G σ`: the maximum of `vertexSepAt` over positions."""
    return max((vertex_sep_at(graph, layout, i) for i in range(len(layout))), default=0)


def vertex_separation(graph: nx.Graph) -> int:
    """`vertexSeparation G`: the minimum over layouts (= pathwidth, Kinnersley)."""
    nodes = list(graph.nodes())
    return min(vertex_sep_of_layout(graph, list(p)) for p in itertools.permutations(nodes))


def sandwich(graph: nx.Graph) -> dict:
    """Every quantity in the sandwich for one small graph, plus the references."""
    n = graph.number_of_nodes()
    core = max(nx.core_number(graph).values()) if n else 0
    if n and n <= 25:
        from fixed_parameter_algorithm.pathwidth import compute_pathwidth
        pw_solver, _ = compute_pathwidth(graph)
    else:
        pw_solver = vertex_separation(graph)
    return {
        "n": n,
        "edges": graph.number_of_edges(),
        "degeneracy": degeneracy_subsets(graph),
        "ordering_degeneracy": ordering_degeneracy(graph),
        "core_number": core,
        "vertex_separation": vertex_separation(graph),
        "pathwidth_solver": pw_solver,
        "bandwidth": bandwidth(graph),
    }


def all_graphs(n: int):
    """Every labelled simple graph on `n` vertices (2^(n choose 2) of them)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(p for k, p in enumerate(pairs) if mask >> k & 1)
        yield g


def brute_force(max_n: int = 5) -> pd.DataFrame:
    """The sandwich on every labelled graph with 1..max_n vertices."""
    rows = []
    for n in range(1, max_n + 1):
        for g in all_graphs(n):
            rows.append(sandwich(g))
    return pd.DataFrame(rows)


def brute_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Per size: agreement of the definitions with their references, and tightness."""
    out = []
    for n, part in frame.groupby("n"):
        out.append({
            "n": int(n),
            "graphs": len(part),
            "degeneracy = core_number": int((part.degeneracy == part.core_number).sum()),
            "degeneracy = ordering_degeneracy":
                int((part.degeneracy == part.ordering_degeneracy).sum()),
            "vertex_separation = pathwidth_solver":
                int((part.vertex_separation == part.pathwidth_solver).sum()),
            "degeneracy ≤ pw": int((part.degeneracy <= part.vertex_separation).sum()),
            "pw ≤ bandwidth": int((part.vertex_separation <= part.bandwidth).sum()),
            "degeneracy = pw": int((part.degeneracy == part.vertex_separation).sum()),
            "pw = bandwidth": int((part.vertex_separation == part.bandwidth).sum()),
            "both tight": int(((part.degeneracy == part.vertex_separation)
                               & (part.vertex_separation == part.bandwidth)).sum()),
        })
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------
# The Lean side
# ----------------------------------------------------------------------------

def lake_available() -> bool:
    return (LEAN_DIR / "lakefile.lean").exists() and \
        subprocess.run(["which", "lake"], capture_output=True).returncode == 0


def lake_build(timeout: int = 3600) -> tuple[bool, str]:
    """Run `lake build` in the Lean project; return (ok, last lines of output)."""
    proc = subprocess.run(["lake", "build"], cwd=LEAN_DIR, capture_output=True,
                          text=True, timeout=timeout)
    tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-12:])
    return proc.returncode == 0, tail


def print_axioms(names: tuple[str, ...] = PROVED + STATED,
                 namespace: str = "MOSPFormalization") -> pd.DataFrame:
    """`#print axioms` for each theorem, via `lake env lean` on a scratch file."""
    scratch = LEAN_DIR / ".lake" / "sandwich_axioms.lean"
    scratch.parent.mkdir(exist_ok=True)
    lines = [f"import {namespace}.Sandwich"] + \
        [f"#print axioms {namespace}.{name}" for name in names]
    scratch.write_text("\n".join(lines) + "\n")
    proc = subprocess.run(["lake", "env", "lean", str(scratch)], cwd=LEAN_DIR,
                          capture_output=True, text=True, timeout=600)
    text = proc.stdout + proc.stderr
    rows = []
    for name in names:
        # Lean wraps long axiom lists over several lines, hence DOTALL.
        pattern = re.compile(rf"'{re.escape(namespace)}\.{re.escape(name)}' depends on axioms: "
                             rf"\[(.*?)\]", re.DOTALL)
        m = pattern.search(text)
        axioms = [a.strip() for a in m.group(1).split(",")] if m else []
        rows.append({
            "theorem": name,
            "role": "proved" if name in PROVED else "stated (sorry)",
            "found": m is not None,
            "axioms": ", ".join(axioms),
            "uses_sorry": "sorryAx" in axioms,
        })
    frame = pd.DataFrame(rows)
    frame.attrs["returncode"] = proc.returncode
    frame.attrs["output"] = text
    return frame


def axioms_verdict(frame: pd.DataFrame) -> tuple[bool, list[str]]:
    """Proved theorems carry no `sorryAx`; stated ones do; all are found."""
    problems = []
    for row in frame.itertuples():
        if not row.found:
            problems.append(f"{row.theorem}: not found")
        elif row.role == "proved" and row.uses_sorry:
            problems.append(f"{row.theorem}: proved theorem uses sorryAx")
        elif row.role != "proved" and not row.uses_sorry:
            problems.append(f"{row.theorem}: stated theorem no longer uses sorryAx (promote it)")
    return not problems, problems


# ----------------------------------------------------------------------------
# The corpus recount
# ----------------------------------------------------------------------------

def corpus_check(path: Path = INSTANCES) -> pd.DataFrame:
    """`g_degeneracy + 1 ≤ optimum ≤ bw_rcm + 1` on the certified corpus, by size band."""
    frame = pd.read_csv(path, usecols=["instance_name", "optimum", "n_customers",
                                       "g_degeneracy", "bw_rcm"])
    frame = frame.dropna(subset=["optimum"])
    lo = frame.g_degeneracy.round().astype(int) + 1
    hi = frame.bw_rcm.round().astype(int) + 1
    opt = frame.optimum.round().astype(int)
    bands = pd.cut(frame.n_customers, [0, 10, 20, 30, 40, 75, 200],
                   labels=["≤10", "11–20", "21–30", "31–40", "41–75", "76–134"])
    frame = frame.assign(band=bands, lo_ok=lo <= opt, hi_ok=opt <= hi,
                         lo_tight=lo == opt, hi_tight=hi == opt, both=lo == hi)
    rows = []
    for band, part in frame.groupby("band", observed=True):
        rows.append({"band": str(band), "instances": len(part),
                     "degeneracy+1 ≤ optimum": int(part.lo_ok.sum()),
                     "optimum ≤ bw_rcm+1": int(part.hi_ok.sum()),
                     "lower tight": int(part.lo_tight.sum()),
                     "upper tight": int(part.hi_tight.sum()),
                     "ends coincide": int(part.both.sum())})
    rows.append({"band": "all", "instances": len(frame),
                 "degeneracy+1 ≤ optimum": int(frame.lo_ok.sum()),
                 "optimum ≤ bw_rcm+1": int(frame.hi_ok.sum()),
                 "lower tight": int(frame.lo_tight.sum()),
                 "upper tight": int(frame.hi_tight.sum()),
                 "ends coincide": int(frame.both.sum())})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

def _md(frame: pd.DataFrame) -> str:
    return frame.to_markdown(index=False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", choices=["all", "brute", "lean", "corpus"], default="all")
    ap.add_argument("--max-n", type=int, default=5)
    ap.add_argument("--out", type=Path, default=TABLES)
    args = ap.parse_args(argv)

    sections = ["# The sandwich in Lean: tables", "",
                "Regenerate: `python -m learning.sandwich`. Every table below is "
                "written by that command; `reports/ml_nature.md` §26 quotes them.", ""]
    ok = True

    if args.stage in ("all", "brute"):
        t0 = time.time()
        frame = brute_force(args.max_n)
        summary = brute_summary(frame)
        sections += [f"## Brute force over every labelled graph on 1–{args.max_n} vertices",
                     "", f"{len(frame)} graphs in {time.time() - t0:.1f} s. "
                     "Each column counts graphs where the statement holds.", "",
                     _md(summary), ""]
        bad = frame[(frame.degeneracy != frame.core_number)
                    | (frame.degeneracy != frame.ordering_degeneracy)
                    | (frame.vertex_separation != frame.pathwidth_solver)
                    | (frame.degeneracy > frame.vertex_separation)
                    | (frame.vertex_separation > frame.bandwidth)]
        ok &= bad.empty
        print(summary.to_string(index=False))
        print(f"brute force: {len(frame)} graphs, {len(bad)} violations")

    if args.stage in ("all", "corpus"):
        corpus = corpus_check()
        sections += ["## The corpus (`learning/data/instances.csv`)", "",
                     "`g_degeneracy` is networkx's core number (the Lick–White form "
                     "formalised as `degeneracy`); `bw_rcm` is the bandwidth of the "
                     "reverse Cuthill–McKee layout (`bandwidthOfLayout`, one layout, "
                     "so `pathwidth_le_bandwidthOfLayout` is the theorem it checks).", "",
                     _md(corpus), ""]
        total = corpus[corpus.band == "all"].iloc[0]
        ok &= total["degeneracy+1 ≤ optimum"] == total.instances == total["optimum ≤ bw_rcm+1"]
        print(corpus.to_string(index=False))

    if args.stage in ("all", "lean"):
        if not lake_available():
            sections += ["## Lean", "", "`lake` not available; axiom check skipped.", ""]
            print("lake not available")
        else:
            t0 = time.time()
            built, tail = lake_build()
            axioms = print_axioms()
            verdict, problems = axioms_verdict(axioms)
            ok &= built and verdict
            sections += ["## Lean: `lake build` and `#print axioms`", "",
                         f"`lake build`: {'passed' if built else 'FAILED'} in "
                         f"{time.time() - t0:.0f} s.", "",
                         _md(axioms.drop(columns=["found"])), "",
                         "Verdict: " + ("every proved theorem is free of `sorryAx`, every "
                                        "stated one carries it." if verdict
                                        else "; ".join(problems)), ""]
            print(axioms.to_string(index=False))
            print("lake build:", "ok" if built else "FAILED", "| axioms:",
                  "ok" if verdict else problems)
            if not built:
                print(tail)

    args.out.write_text("\n".join(sections))
    print(f"wrote {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
