"""Family B by search: separator-branch certificates with the branches' widths
proved by the C program (Ralph loop0013 item 06; plan
`reports/obstruction_search_plan.md` §0.5 (f), §0.9 B).

**The object.** Lemma A of `reports/ml_nature.md` §38, proved in Lean as
`branch_lemma_separator` (`lean/MOSPFormalization/Sandwich.lean`): for a set
`S` and three pairwise disjoint, connected vertex sets `A, B, D` disjoint from
`S`, each of pathwidth at least `k` (as induced subgraphs), such that every
two of them are joined through a connected `Q ⊆ S` adjacent to both,
`pathwidth(G) ≥ k + 1`. A B *certificate* is `S`, the three branches, the
three connectors with one edge to each side, and a certificate of each
branch's width: the C program's proof on the branch's induced subgraph
(`refutation` / `bound` status, or its printed `lower`, the C's own
degeneracy floor), a clique by inspection, a single vertex, a contraction
minor of the branch (`obstruction-minor-1`, family M's ladder run on the
branch), or — recursively — another B certificate. Values are reported in
optimum units (`pathwidth + 1`), as every item of the loop does.

**What is searched.** The candidate separators are
`learning.bound_harness.family_separators` (cut vertices, pairwise
intersections of maximal cliques, clique-tree adhesions of the MCS-M chordal
completion, every edge on graphs of at most 40 vertices) plus a tabu local
search over `S` at the top level (add / drop one vertex, `|S| ≤ 6`, tenure
5, the neighbours sampled), scored lexicographically by the value the
separator certifies, the number of non-trivial components of `G − S`, the
number of components and `−|S|`. For each `S` the components of `G − S` are
the branches; a branch's width is its own node at depth one less (so a
branch may carry a B certificate of its own: depth 2 at the top), memoised
by vertex set across every `S`. The value at `S` is the largest `k` such
that three components of width `≥ k` are pairwise linked through a
component of `G[S]`, plus one. **No C call is ever made on the whole graph**:
the top-level node has no leaf oracle, so family B's value on an instance is
the branch value alone (`none` when no `S` yields a linked triple), and the
tables put the clique number beside it. The local search evaluates
branches at depth 0 (leaf oracle only) and the best separator it finds is
re-evaluated at full depth.

**What the C program is asked.** Only induced subgraphs of the instance's
MOSP graph that are proper (a component of `G − S`, `S ≠ ∅`), each under a
cap (5 s), with `-m min_vertices=1000000` so the proof is the C's search
and not its own minor step; cached by vertex set. A component that is a
single vertex or a clique costs no call. Nothing under `solutions/` is
written; every optimum is read from item 01's ledger.

**Certificate** (`obstruction-branch-1`): the instance's name, `n`, the
SHA-256 of its rows and of its edge list, the nested node (kind `branch`,
`c`, `clique`, `trivial` or `minor`; every node names its vertex set and
the pathwidth it certifies), the floor in optimum units, the C binary's
SHA-256, the theorems. The independent checker is
`paper1/obstruction_check.py check-branch`: it reads the instance with its
own reader, checks disjointness and connectivity by its own BFS, every
connector, every leaf (re-running the C program on the branch, `check-minor`
on a minor leaf, the clique by inspection) and `k + 1`, recursively.

**Hand instances** (`--stage hand`, and the tests): the theta graph (two
adjacent hubs joined by three paths of three inner vertices: value 3 at
`S = {0, 1}`), the spider with three legs of two (3), the spider of spiders
(4, which needs depth 2), three `K4` at a hub (4), `K_{1,3}` (2) — the
values `learning.bound_harness`'s tests record for the seeded form, which
this search must reproduce where exact leaves and the treewidth seed
coincide.

Stages:

    nice -n 19 python3 -m learning.obstruction_branch --stage hand
    nice -n 19 python3 -m learning.obstruction_branch --stage run --targets residual --workers 8 --core-hours 4
    nice -n 19 python3 -m learning.obstruction_branch --stage run --targets gap338 --workers 8 --core-hours 3
    nice -n 19 python3 -m learning.obstruction_branch --stage check --workers 8
    nice -n 19 python3 -m learning.obstruction_branch --stage connectivity --targets residual
    python3 -m learning.obstruction_branch --stage tables
    python3 -m pytest tests/test_obstruction_branch.py -q
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import argparse
import itertools
import json
import random
import sys
import time
from dataclasses import dataclass, field
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from learning.obstruction_ledger import LEDGER_CORPUS, TARGETS_JSON, BANDS, adjacency_from_matrix, corpus_instances  # noqa: F401
from learning.obstruction_expansion import (solution_record, safe_name, matrix_sha256, write_standard_instance,
                                            target_names, ledger)
from learning.obstruction_minor import (bits, edge_list, edges_sha256, graph6, run_c, proved_pathwidth, binary_sha256,
                                        C_BINARY, band_of, family_e_floor, Evaluator, ladder as minor_ladder,
                                        certificate as minor_certificate, minor_masks)

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = ROOT / "reports" / "scratch" / "obstruction_search"
OUT = SCRATCH / "06_branch"
SEARCH_CSV = OUT / "search.csv"
CERT_DIR = OUT / "certificates"
RUN_LOG = OUT / "run.log"
TABLES_MD = OUT / "tables.md"
CHECKER_CSV = OUT / "checker_verdicts.csv"
HAND_CSV = OUT / "hand.csv"
CONNECTIVITY_CSV = OUT / "connectivity.csv"
HARNESS_VALUES = ROOT / "learning" / "data" / "ensemble" / "bound_harness_values.csv.gz"

C_CAP_SECONDS = 5.0          # per C call on a branch (plan §0.5 (f))
INSTANCE_SECONDS = 120.0     # per instance
MAX_S = 6
TENURE = 5
DEPTH = 2
MOVES_PER_START = 30
NEIGHBOUR_SAMPLE = 24
MAX_STARTS = 12
TOP_COMPONENTS = 40          # the triple is searched among this many widest components
MINOR_LEAF_MIN = 30          # a branch this large whose C call did not finish gets the M ladder
MINOR_LEAF_SECONDS = 40.0
FORMAT = "obstruction-branch-1"
THEOREMS = ("branch_lemma_separator / branch_lemma_linked (lean/MOSPFormalization/Sandwich.lean) for every branch "
            "node; card_le_pathwidth_add_one_of_isClique (MOSPGraph.lean) for a clique leaf; the C program's "
            "refutation on a branch rests on the corrected search rules (Search/) and its bound on "
            "degeneracy_le_pathwidth / minDegreeIn_le_degeneracy (Sandwich.lean); pathwidth_gt_of_minorOf (Minor.lean) "
            "for a minor leaf; mospValue_eq_pathwidth_add_one (MOSPGraph.lean) for the optimum units")


def log(msg: str, path: Path | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(path or RUN_LOG, "a") as fh:
        fh.write(line + "\n")


# ----------------------------------------------------------------------------
# graphs on bit masks
# ----------------------------------------------------------------------------


def popcount(mask: int) -> int:
    return bin(mask).count("1")


def components(adj: list[int], alive: int) -> list[int]:
    """The connected components of the subgraph induced on `alive`, as masks,
    largest first (ties by lowest vertex)."""
    out = []
    rest = alive
    while rest:
        start = rest & -rest
        comp, frontier = start, start
        while frontier:
            nxt = 0
            f = frontier
            while f:
                b = f & -f
                f ^= b
                nxt |= adj[b.bit_length() - 1]
            nxt &= alive & ~comp
            comp |= nxt
            frontier = nxt
        out.append(comp)
        rest &= ~comp
    out.sort(key=lambda c: (-popcount(c), c & -c))
    return out


def is_connected(adj: list[int], mask: int) -> bool:
    return mask != 0 and len(components(adj, mask)) == 1


def neighbourhood(adj: list[int], mask: int) -> int:
    out = 0
    for v in bits(mask):
        out |= adj[v]
    return out & ~mask


def is_clique(adj: list[int], mask: int) -> bool:
    return all((adj[v] | (1 << v)) & mask == mask for v in bits(mask))


def induced(adj: list[int], mask: int) -> tuple[list[int], list[int], list[tuple[int, int]]]:
    """The induced subgraph relabelled `0..m-1` in increasing label order:
    the labels, its masks and its sorted edge list."""
    labels = bits(mask)
    index = {v: i for i, v in enumerate(labels)}
    sub = [0] * len(labels)
    edges = []
    for v in labels:
        for u in bits(adj[v] & mask):
            sub[index[v]] |= 1 << index[u]
            if v < u:
                edges.append((index[v], index[u]))
    return labels, sub, sorted(edges)


def nx_graph(adj: list[int], mask: int):
    import networkx as nx

    g = nx.Graph()
    g.add_nodes_from(bits(mask))
    for v in bits(mask):
        for u in bits(adj[v] & mask):
            if v < u:
                g.add_edge(v, u)
    return g


def mask_of(vertices) -> int:
    out = 0
    for v in vertices:
        out |= 1 << int(v)
    return out


# ----------------------------------------------------------------------------
# links: the connectors through S (Lemma A's pairwise condition)
# ----------------------------------------------------------------------------


def connectors(adj: list[int], S: int, comps: list[int]) -> tuple[list[int], list[set[int]]]:
    """The components of `G[S]` and, per branch, the ids of those adjacent to it."""
    s_comps = components(adj, S) if S else []
    touch = []
    for comp in comps:
        nb = neighbourhood(adj, comp)
        touch.append({i for i, q in enumerate(s_comps) if q & nb})
    return s_comps, touch


def best_linked_triple(adj: list[int], S: int, comps: list[int], values: list[int],
                       top: int = TOP_COMPONENTS) -> tuple[int, tuple[int, int, int], list[int]] | None:
    """The largest `k` such that three branches of width `≥ k` are pairwise
    linked through a component of `G[S]`; returns `(k, (i, j, l), s_comps)`
    or `None`. Among the `top` widest branches (the harness's `linked_third`
    takes ten; a sparse graph minus a hub can have more components than
    that, so the window here is wider and the test pins the two equal where
    both see every component)."""
    if len(comps) < 3:
        return None
    s_comps, touch = connectors(adj, S, comps)
    order = sorted(range(len(comps)), key=lambda i: (-values[i], i))[:top]
    best = None
    for i, j, l in itertools.combinations(order, 3):
        k = min(values[i], values[j], values[l])
        if best is not None and k <= best[0]:
            continue
        if (touch[i] & touch[j]) and (touch[i] & touch[l]) and (touch[j] & touch[l]):
            best = (k, (i, j, l), s_comps)
    return best


def link_witness(adj: list[int], s_comps: list[int], touch_i: set[int], touch_j: set[int],
                 comp_i: int, comp_j: int) -> dict:
    """One connector `Q ⊆ S` (a component of `G[S]`) adjacent to both branches,
    with one edge to each."""
    q_id = min(touch_i & touch_j)
    Q = s_comps[q_id]
    e1 = e2 = None
    for q in bits(Q):
        if e1 is None and adj[q] & comp_i:
            e1 = [q, (adj[q] & comp_i).bit_length() - 1]
        if e2 is None and adj[q] & comp_j:
            e2 = [q, (adj[q] & comp_j).bit_length() - 1]
    return {"Q": bits(Q), "edge_first": e1, "edge_second": e2}


# ----------------------------------------------------------------------------
# the leaf oracle: a branch's width, proved
# ----------------------------------------------------------------------------


@dataclass
class LeafOracle:
    """The width of an induced subgraph, with its certificate node; cached by
    vertex set. `kind` is `c` (the C program under `cap`) or `brute` (the
    subset DP of `learning.first_moment.vertex_separation_brute`, tests only,
    `n ≤ 16`)."""
    adj: list[int]
    cap: float = C_CAP_SECONDS
    deadline: float = float("inf")
    kind: str = "c"
    minor_leaves: bool = True
    calls: int = 0
    seconds_c: float = 0.0
    minor_calls: int = 0
    cache: dict = field(default_factory=dict)
    upper_cache: dict = field(default_factory=dict)
    position: list[int] | None = None   # item 07: a recorded layout (positions) restricted to the set is an upper bound
    max_m: int = 10 ** 9                # item 07: a set above this size is never sent to the C program (trivial node)
    greedy_max_m: int = 400             # the greedy layout is computed only up to this size
    skipped_large: int = 0

    def time_left(self) -> float:
        return self.deadline - time.monotonic()

    def width(self, mask: int) -> dict:
        if mask in self.cache:
            return self.cache[mask]
        node = self._evaluate(mask)
        self.cache[mask] = node
        return node

    def upper(self, mask: int) -> int:
        """An upper bound on the set's pathwidth: `size − 1`, the greedy
        layout's vertex separation, the C's upper bound once it has run."""
        if mask in self.cache:
            nd = self.cache[mask]
            if nd["kind"] in ("trivial", "clique", "brute") or nd.get("c_status") in ("refutation", "bound", "minor"):
                return nd["pathwidth_at_least"]
            if nd.get("c_width") is not None:
                return int(nd["c_width"])
        if mask in self.upper_cache:
            return self.upper_cache[mask]
        m = popcount(mask)
        ub = m - 1
        if m >= 3 and (m <= self.greedy_max_m or self.position is not None):
            from learning.obstruction_minor import greedy_layout, vertex_separation

            labels, sub, edges = induced(self.adj, mask)
            if m <= self.greedy_max_m:
                ub = min(ub, vertex_separation(sub, greedy_layout(sub)))
            if self.position is not None:
                # the recorded layout restricted to the set: the vertex separation of an induced
                # subgraph under the restricted order never exceeds the whole layout's
                order = sorted(range(m), key=lambda i: self.position[labels[i]])
                ub = min(ub, vertex_separation(sub, order))
        self.upper_cache[mask] = ub
        return ub

    @staticmethod
    def trivial(mask: int) -> dict:
        """`pathwidth ≥ 0` for any nonempty set: a node that costs nothing."""
        return {"kind": "trivial", "vertices": bits(mask), "pathwidth_at_least": 0, "source": "trivial"}

    def _evaluate(self, mask: int) -> dict:
        verts = bits(mask)
        m = len(verts)
        if m == 1:
            return self.trivial(mask)
        if is_clique(self.adj, mask):
            return {"kind": "clique", "vertices": verts, "clique": verts, "pathwidth_at_least": m - 1, "source": "clique"}
        if m > self.max_m:
            # item 07: a branch above the cap is a run on (most of) an open instance, which this loop does not do
            self.skipped_large += 1
            node = self.trivial(mask)
            node["source"] = "skipped_large"
            return node
        labels, sub, edges = induced(self.adj, mask)
        if self.kind == "brute":
            from learning.first_moment import vertex_separation_brute

            pw = vertex_separation_brute(sub)
            return {"kind": "brute", "vertices": verts, "pathwidth_at_least": pw, "source": "brute"}
        cap = min(self.cap, max(0.05, self.time_left()))
        c = run_c(graph6(m, edges), cap)
        self.calls += 1
        self.seconds_c += c["seconds"]
        pw, source = proved_pathwidth(c)
        node = {"kind": "c", "vertices": verts, "m": m, "edges": len(edges), "edges_sha256": edges_sha256(m, edges),
                "pathwidth_at_least": int(pw) if pw is not None else 0, "source": source,
                "c_width": c["width"], "c_status": c["status"], "c_lower": c["lower"], "c_nodes": c.get("nodes"),
                "c_stdout": c["stdout"], "c_stderr": c["stderr"], "c_seconds": c["seconds"], "c_cap_seconds": cap,
                "c_command": "printf '%s\\n' \"$g6\" | nice -n 19 pathwidth_solver/cli/pathwidth "
                             f"-t {cap:g} -l -v -m min_vertices=1000000"}
        return node

    def minor_leaf(self, mask: int, seconds: float) -> dict | None:
        """Family M's greedy ladder on the branch (the C's own cap), when the
        direct call left the width unproved; returns the better node or `None`."""
        node = self.width(mask)
        if node["kind"] != "c" or node["source"] != "c_lower" or not self.minor_leaves:
            return None
        labels, sub, edges = induced(self.adj, mask)
        ev = Evaluator(sub, None, self.cap, None, deadline=time.monotonic() + min(seconds, max(0.1, self.time_left())))
        minor_ladder(ev)
        self.minor_calls += ev.calls
        self.seconds_c += ev.seconds_c
        if ev.best is None or ev.best_floor - 1 <= node["pathwidth_at_least"]:
            return None
        cert = minor_certificate(f"branch[{len(labels)}]", np.zeros((0, 0), dtype=int), sub, ev.best, 0.0,
                                 "ladder", None, self.cap)
        cert.pop("matrix_sha256", None)
        better = {"kind": "minor", "vertices": bits(mask), "m": len(labels), "edges": len(edges),
                  "edges_sha256": edges_sha256(len(labels), edges), "pathwidth_at_least": ev.best_floor - 1,
                  "source": "minor_ladder", "certificate": cert, "direct": node}
        self.cache[mask] = better
        return better


# ----------------------------------------------------------------------------
# the branch recursion and the local search
# ----------------------------------------------------------------------------


@dataclass
class Context:
    adj: list[int]
    oracle: LeafOracle
    deadline: float
    rng: random.Random
    memo: dict = field(default_factory=dict)        # (mask, depth) -> node
    top: int = 0
    stats: dict = field(default_factory=lambda: {"separators_family": 0, "separators_evaluated": 0,
                                                 "separators_with_3_comps": 0, "local_moves": 0, "local_starts": 0,
                                                 "censored": False, "best_potential": 0})

    def time_left(self) -> float:
        return self.deadline - time.monotonic()


def separator_family(adj: list[int], mask: int) -> list[int]:
    """`bound_harness.family_separators` on the induced subgraph, as masks
    inside `mask`, never empty and never the whole set."""
    from learning.bound_harness import family_separators

    g = nx_graph(adj, mask)
    out = []
    seen = set()
    for S in family_separators(g):
        sm = mask_of(S)
        if sm and sm != mask and sm not in seen and popcount(sm) <= MAX_S:
            seen.add(sm)
            out.append(sm)
    return out


def known_node(ctx: Context, mask: int, depth: int) -> dict | None:
    """A node already proved for `mask`: the memo at this depth, else the leaf
    oracle's cache (valid at any depth)."""
    if (mask, depth) in ctx.memo:
        return ctx.memo[(mask, depth)]
    return ctx.oracle.cache.get(mask)


def value_at(ctx: Context, mask: int, S: int, depth: int, need_k: int = 0) -> tuple[int, dict | None, dict]:
    """The branch rule at `S` inside `mask`: the branches are the components
    of `mask − S`, each evaluated at `depth` (0: the leaf oracle only).
    Lazy: every branch starts with the proved floor it already has (0 for a
    set never looked at: `pathwidth ≥ 0`) and an upper bound (`size − 1`,
    the greedy layout, the C's upper bound); a branch is evaluated only
    while the best triple by upper bounds could still reach `need_k`, the
    cheapest unproved member of that triple first. Returns `(k + 1 or 0,
    branch node or None, diagnostics)`; a branch left unproved appears as a
    `trivial` node (claim 0)."""
    adj = ctx.adj
    comps = components(adj, mask & ~S)
    diag = {"n_comps": len(comps), "n_comps_nontrivial": sum(1 for c in comps if popcount(c) >= 2), "potential": 0}
    if len(comps) < 3:
        return 0, None, diag
    ctx.stats["separators_with_3_comps"] += 1
    nodes: list[dict | None] = [known_node(ctx, c, depth) for c in comps]
    lo = [nd["pathwidth_at_least"] if nd else 0 for nd in nodes]
    hi = [ctx.oracle.upper(c) for c in comps]
    exact = [nd is not None and (nd["kind"] in ("trivial", "clique", "brute") or lo[i] >= hi[i]
                                 or (nd["kind"] == "c" and nd.get("c_status") in ("refutation", "bound", "minor")
                                     and depth == 0))
             for i, nd in enumerate(nodes)]
    while True:
        t_hi = best_linked_triple(adj, S, comps, hi)
        if t_hi is None:
            return 0, None, diag
        k_hi = t_hi[0]
        diag["potential"] = k_hi + 1
        if mask == ctx.top:
            ctx.stats["best_potential"] = max(ctx.stats.get("best_potential", 0), k_hi + 1)
        t_lo = best_linked_triple(adj, S, comps, lo)
        k_lo = t_lo[0] if t_lo is not None else -1
        if k_lo >= k_hi or k_hi < need_k or ctx.time_left() <= 0:
            break
        cands = [i for i in t_hi[1] if not exact[i] and not (nodes[i] is not None and lo[i] >= hi[i])]
        if not cands:
            break
        i = min(cands, key=lambda i: popcount(comps[i]))
        nd = node_for(ctx, comps[i], depth)
        nodes[i], lo[i] = nd, nd["pathwidth_at_least"]
        hi[i] = min(hi[i], ctx.oracle.upper(comps[i]))
        exact[i] = True
    if t_lo is None or k_lo < 0:
        return 0, None, diag
    k, (i, j, l), s_comps = t_lo
    _, touch = connectors(adj, S, comps)
    links = []
    for a, b in ((i, j), (i, l), (j, l)):
        w = link_witness(adj, s_comps, touch[a], touch[b], comps[a], comps[b])
        w["pair"] = [[i, j, l].index(a), [i, j, l].index(b)]
        links.append(w)
    picked = [nodes[x] if nodes[x] is not None else LeafOracle.trivial(comps[x]) for x in (i, j, l)]
    node = {"kind": "branch", "vertices": bits(mask), "pathwidth_at_least": k + 1, "k": k, "S": bits(S),
            "branches": picked, "links": links, "source": "branch", "n_comps": len(comps)}
    return k + 1, node, diag


def node_for(ctx: Context, mask: int, depth: int) -> dict:
    """The best certificate node for the induced subgraph on `mask`: the leaf
    oracle's, or the branch rule over the separator family at `depth − 1`
    for the branches."""
    key = (mask, depth)
    if key in ctx.memo:
        return ctx.memo[key]
    best = ctx.oracle.width(mask)
    if depth > 0 and popcount(mask) >= 4 and ctx.time_left() > 0:
        for S in separator_family(ctx.adj, mask):
            if ctx.time_left() <= 0:
                ctx.stats["censored"] = True
                break
            ctx.stats["separators_evaluated"] += 1
            value, node, _ = value_at(ctx, mask, S, depth - 1, best["pathwidth_at_least"])
            if node is not None and value > best["pathwidth_at_least"]:
                best = node
    ctx.memo[key] = best
    return best


def score_of(ctx: Context, top: int, S: int, need_k: int) -> tuple:
    """The local search's score: the value certified at depth 0, the
    potential (by upper bounds), the non-trivial components, the components,
    `−|S|`; branches are proved only where the potential reaches `need_k`."""
    value, node, diag = value_at(ctx, top, S, 0, need_k)
    return (value, diag["potential"], diag["n_comps_nontrivial"], diag["n_comps"], -popcount(S)), node


def local_search(ctx: Context, top: int, starts: list[int], best_value: int) -> tuple[int, int | None]:
    """Tabu search over `S` at the top level, branches at depth 0: add or drop
    one vertex, `|S| ≤ MAX_S`, tenure `TENURE` on the vertices moved, the
    add-neighbours sampled among `N(S)` first. Returns the best value seen
    and its `S` (None when no separator gave a linked triple)."""
    n = len(ctx.adj)
    best_S = None
    for start in starts[:MAX_STARTS]:
        if ctx.time_left() <= 0:
            ctx.stats["censored"] = True
            break
        ctx.stats["local_starts"] += 1
        S = start
        score, _ = score_of(ctx, top, S, best_value)
        tabu: dict[int, int] = {}
        for move in range(MOVES_PER_START):
            if ctx.time_left() <= 0:
                ctx.stats["censored"] = True
                break
            cands = []
            nb = bits(neighbourhood(ctx.adj, S))
            ctx.rng.shuffle(nb)
            others = [v for v in range(n) if not (S >> v) & 1 and not ((neighbourhood(ctx.adj, S) >> v) & 1)]
            ctx.rng.shuffle(others)
            if popcount(S) < MAX_S:
                cands += [("add", v) for v in (nb + others)[:NEIGHBOUR_SAMPLE]]
            if popcount(S) > 1:
                cands += [("drop", v) for v in bits(S)]
            best_move = None
            for kind, v in cands:
                if tabu.get(v, -1) > move:
                    continue
                S2 = S | (1 << v) if kind == "add" else S & ~(1 << v)
                if not S2 or S2 == top:
                    continue
                ctx.stats["separators_evaluated"] += 1
                ctx.stats["local_moves"] += 1
                sc, _ = score_of(ctx, top, S2, best_value)
                if best_move is None or sc > best_move[0]:
                    best_move = (sc, v, S2)
            if best_move is None:
                break
            score, v, S = best_move
            tabu[v] = move + TENURE
            if score[0] > best_value:
                best_value, best_S = score[0], S
    return best_value, best_S


def branch_search(adj: list[int], seconds: float = INSTANCE_SECONDS, cap: float = C_CAP_SECONDS, depth: int = DEPTH,
                  rng_seed: int = 1, kind: str = "c", local: bool = True, minor_leaves: bool = True,
                  position: list[int] | None = None, max_m: int = 10 ** 9, greedy_max_m: int = 400) -> dict:
    """Family B on one graph: the separator family at full depth, the local
    search at depth 0 with its best re-evaluated at full depth, the minor
    ladder on the limiting branches of the best triple. Returns the value
    (`pathwidth_at_least`, −1 when no separator gives a linked triple), the
    certificate node, the statistics."""
    n = len(adj)
    top = (1 << n) - 1
    deadline = time.monotonic() + seconds
    oracle = LeafOracle(adj, cap, deadline, kind, minor_leaves, position=position, max_m=max_m,
                        greedy_max_m=greedy_max_m)
    ctx = Context(adj, oracle, deadline, random.Random(rng_seed), top=top)
    t0 = time.monotonic()
    best_value, best_node, best_S = 0, None, None
    family = separator_family(adj, top) if n >= 4 else []
    ctx.stats["separators_family"] = len(family)
    scored = []
    for S in family:
        if ctx.time_left() <= 0:
            ctx.stats["censored"] = True
            break
        ctx.stats["separators_evaluated"] += 1
        value, node, diag = value_at(ctx, top, S, depth - 1, best_value)
        scored.append(((value, diag["potential"], diag["n_comps_nontrivial"], diag["n_comps"], -popcount(S)), S))
        if node is not None and value > best_value:
            best_value, best_node, best_S = value, node, S
    if local and n >= 4 and ctx.time_left() > 0:
        scored.sort(key=lambda x: x[0], reverse=True)
        starts = [S for _, S in scored[:MAX_STARTS]]
        if not starts:
            starts = [1 << ctx.rng.randrange(n) for _ in range(min(MAX_STARTS, n))]
        lv, lS = local_search(ctx, top, starts, best_value)
        if lS is not None:
            value, node, _ = value_at(ctx, top, lS, depth - 1, best_value)
            if node is not None and value > best_value:
                best_value, best_node, best_S = value, node, lS
    # the minor ladder on the limiting branches of the best triple
    if best_node is not None and minor_leaves and kind == "c" and ctx.time_left() > 5:
        improved = set()
        for br in best_node["branches"]:
            m = mask_of(br["vertices"])
            if br.get("kind") == "c" and br.get("source") == "c_lower" and popcount(m) >= MINOR_LEAF_MIN:
                if oracle.minor_leaf(m, MINOR_LEAF_SECONDS) is not None:
                    improved.add(m)
        if improved:
            ctx.memo = {k: v for k, v in ctx.memo.items() if k[0] not in improved}
            value, node, _ = value_at(ctx, top, best_S, 0, best_value)
            if node is not None and value > best_value:
                best_value, best_node = value, node
    stats = dict(ctx.stats)
    stats.update({"seconds": time.monotonic() - t0, "c_calls": oracle.calls, "c_seconds": oracle.seconds_c,
                  "minor_calls": oracle.minor_calls, "leaves_cached": len(oracle.cache),
                  "memo": len(ctx.memo), "skipped_large": oracle.skipped_large})
    return {"value": best_value if best_node is not None else -1, "node": best_node,
            "S": bits(best_S) if best_S is not None else None, "stats": stats}


def branch_widths(node: dict | None) -> list[int]:
    return [b["pathwidth_at_least"] for b in node["branches"]] if node else []


def certificate_dict(name: str, matrix, adj: list[int], result: dict, optimum: int | None, cap: float) -> dict:
    node = result["node"]
    return {
        "format": FORMAT, "instance_name": name, "n": len(adj),
        "matrix_sha256": matrix_sha256(matrix) if matrix is not None and np.asarray(matrix).size else None,
        "graph_sha256": edges_sha256(len(adj), edge_list(adj)), "graph_edges": len(edge_list(adj)),
        "pathwidth_proved": node["pathwidth_at_least"], "floor": node["pathwidth_at_least"] + 1,
        "floor_units": "optimum units: pathwidth(G) + 1 = MOSP",
        "S": node["S"], "k": node["k"], "branch_widths": branch_widths(node),
        "branch_sizes": [len(b["vertices"]) for b in node["branches"]],
        "branch_kinds": [b["kind"] for b in node["branches"]],
        "node": node,
        "node_note": "every node names the vertex set it certifies a pathwidth for (vertices are the instance's "
                     "0-based customer labels); a `branch` node is S, three branches (nodes), three connectors "
                     "Q ⊆ S with one edge to each branch, and certifies k + 1 where every branch certifies ≥ k; "
                     "a `c` node is the C program's output on the induced subgraph relabelled 0..m-1 in increasing "
                     "label order (edges_sha256 as obstruction-minor-1); a `clique` node is a clique of the "
                     "induced subgraph (pathwidth ≥ size − 1); a `trivial` node is one vertex; a `minor` node "
                     "carries an obstruction-minor-1 certificate of the induced subgraph",
        "optimum_on_record": optimum, "c_cap_seconds": cap, "c_binary_sha256": binary_sha256(),
        "seconds": result["stats"]["seconds"], "stats": result["stats"], "theorems": THEOREMS,
    }


# ----------------------------------------------------------------------------
# hand instances
# ----------------------------------------------------------------------------


def from_cliques(n: int, cliques) -> np.ndarray:
    matrix = np.zeros((n, len(cliques)), dtype=int)
    for j, c in enumerate(cliques):
        for v in c:
            matrix[v, j] = 1
    return matrix


def spider_edges(legs: int, length: int):
    edges, k = [], 1
    for _ in range(legs):
        prev = 0
        for _ in range(length):
            edges.append((prev, k))
            prev, k = k, k + 1
    return k, edges


def theta_matrix() -> np.ndarray:
    edges, k = [(0, 1)], 2
    for _ in range(3):
        edges += [(0, k), (k, k + 1), (k + 1, k + 2), (k + 2, 1)]
        k += 3
    return from_cliques(k, edges)


def spider_of_spiders_matrix() -> np.ndarray:
    edges, k = [], 1
    for _ in range(3):
        c = k
        edges.append((0, c))
        k += 1
        for _ in range(3):
            edges += [(c, k), (k, k + 1)]
            k += 2
    return from_cliques(k, edges)


HAND = (   # name, matrix, the value §38's tests record for the seeded form (optimum units), the optimum
    ("K_{1,3}", from_cliques(*spider_edges(3, 1)), 2, 2),
    ("K_{1,4}", from_cliques(*spider_edges(4, 1)), 2, 2),
    ("spider(3,2)", from_cliques(*spider_edges(3, 2)), 3, 3),
    ("path(9)", from_cliques(*spider_edges(2, 4)), None, 2),      # no branching: the seeded form reports ω
    ("three K4 at a hub", from_cliques(10, [{0, 1, 2, 3}, {0, 4, 5, 6}, {0, 7, 8, 9}]), 4, 4),
    ("theta", theta_matrix(), 3, 4),
    ("spider of spiders", spider_of_spiders_matrix(), 4, 4),
)


def run_hand(seconds: float = 20.0) -> pd.DataFrame:
    rows = []
    for name, matrix, expected, optimum in HAND:
        adj = adjacency_from_matrix(matrix)
        res = branch_search(adj, seconds)
        value = res["value"] + 1 if res["value"] >= 0 else None
        rows.append({"instance": name, "n": len(adj), "value_optimum_units": value, "seeded_form_38": expected,
                     "optimum": optimum, "S": res["S"], "branch_widths": branch_widths(res["node"]),
                     "agrees": value == expected, "c_calls": res["stats"]["c_calls"],
                     "seconds": round(res["stats"]["seconds"], 2)})
    frame = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    frame.to_csv(HAND_CSV, index=False)
    log(f"hand: {frame.to_string()}")
    return frame


# ----------------------------------------------------------------------------
# targets: the residual of the 338 after items 03-05
# ----------------------------------------------------------------------------


def record_floors(led: pd.DataFrame) -> pd.DataFrame:
    """Per instance: `floor0` (item 01), family E's floor (items 01-03),
    family M's floor (items 04-05, the ridge stage included), and their
    maximum `record`."""
    out = led[["n", "optimum", "floor0", "lb_best", "tw1", "omega", "excess", "collection"]].copy()
    out["e_floor"] = family_e_floor(led)
    m = pd.Series(1.0, index=led.index)
    for path, cols in ((SCRATCH / "04_minor" / "search.csv", ["search_floor", "ladder_floor"]),
                       (SCRATCH / "05_minor_scale" / "search.csv", ["search_floor", "ladder_floor"]),
                       (SCRATCH / "05_minor_scale" / "carried_item04.csv", ["search_floor", "ladder_floor"]),
                       (SCRATCH / "05_minor_scale" / "ridge_summary.csv", ["search_floor", "ladder_floor"])):
        if path.exists():
            f = pd.read_csv(path).set_index("instance_name")
            cols = [c for c in cols if c in f.columns]
            if cols:
                v = f[cols].max(axis=1)
                common = m.index.intersection(v.index)
                m.loc[common] = np.maximum(m.loc[common].values, v.loc[common].astype(float).values)
    out["m_floor"] = m
    out["record"] = out[["floor0", "e_floor", "m_floor"]].max(axis=1)
    out["gap_record"] = out["optimum"] - out["record"]
    return out


def residual_names(led: pd.DataFrame | None = None) -> list[str]:
    led = ledger().set_index("instance_name") if led is None else led
    rf = record_floors(led)
    names = target_names("gap338")
    return [nm for nm in names if rf.loc[nm, "record"] < rf.loc[nm, "optimum"]]


def smallest_ten(led: pd.DataFrame | None = None) -> list[str]:
    """§6's ten smallest gap instances: `gap338` by `n`, then `m`, then name."""
    led = ledger().set_index("instance_name") if led is None else led
    names = target_names("gap338")
    return sorted(names, key=lambda nm: (int(led.loc[nm, "n"]), int(led.loc[nm, "m"]), nm))[:10]


def resolve_targets(which: str, led: pd.DataFrame) -> list[str]:
    names: list[str] = []
    for w in which.split(","):
        if w == "residual":
            part = residual_names(led)
        elif w == "smallest10":
            part = smallest_ten(led)
        else:
            part = target_names(w)
        for nm in part:
            if nm not in names:
                names.append(nm)
    return names


# ----------------------------------------------------------------------------
# stage: run
# ----------------------------------------------------------------------------


def _job(args) -> dict:
    name, matrix, optimum, seconds, rng_seed, write, cap = args
    matrix = np.asarray(matrix, dtype=int)
    adj = adjacency_from_matrix(matrix)
    res = branch_search(adj, seconds, cap, DEPTH, rng_seed)
    st = res["stats"]
    node = res["node"]
    row = {"instance_name": name, "n": len(adj), "optimum": optimum, "seconds_budget": seconds, "c_cap": cap,
           "b_value": res["value"] + 1 if res["value"] >= 0 else None,        # optimum units
           "has_triple": res["value"] >= 0, "S_size": len(res["S"]) if res["S"] else None,
           "S": json.dumps(res["S"]) if res["S"] else None,
           "branch_widths": json.dumps(branch_widths(node)) if node else None,
           "branch_sizes": json.dumps([len(b["vertices"]) for b in node["branches"]]) if node else None,
           "branch_kinds": json.dumps([b["kind"] for b in node["branches"]]) if node else None,
           "branch_depth2": any(b["kind"] == "branch" for b in node["branches"]) if node else False,
           "reached_optimum": node is not None and optimum is not None and res["value"] + 1 >= optimum}
    row.update({k: st[k] for k in ("separators_family", "separators_evaluated", "separators_with_3_comps",
                                   "local_starts", "local_moves", "censored", "c_calls", "c_seconds",
                                   "minor_calls", "leaves_cached", "seconds")})
    row["b_potential"] = st["best_potential"] + 1 if st["best_potential"] > 0 else None   # optimum units: a ceiling at the S tried
    row["certificate"] = None
    if write and node is not None:
        d = CERT_DIR / safe_name(name)
        d.mkdir(parents=True, exist_ok=True)
        write_standard_instance(d / "instance.mosp", name, matrix)
        cert = certificate_dict(name, matrix, adj, res, optimum, cap)
        (d / "branch.json").write_text(json.dumps(cert, indent=1))
        row["certificate"] = str((d / "branch.json").relative_to(ROOT))
    return row


def run(which: str, workers: int, seconds: float, core_hours: float | None, rng_seed: int = 1,
        limit: int | None = None, order: str = "small-first", cap: float = C_CAP_SECONDS) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    names = resolve_targets(which, led)
    if limit:
        names = names[:limit]
    done = set(pd.read_csv(SEARCH_CSV)["instance_name"]) if SEARCH_CSV.exists() else set()
    inst = corpus_instances()
    jobs = [(nm, np.asarray(inst[nm][1].matrix, dtype=int), int(led.loc[nm, "optimum"]), seconds, rng_seed, True, cap)
            for nm in names if nm not in done]
    jobs.sort(key=lambda j: (len(j[1]) if order == "small-first" else -len(j[1]), j[0]))
    log(f"run: {len(names)} targets ({which}), {len(jobs)} to do, {workers} workers, {seconds:g} s per instance, "
        f"C cap {cap:g} s, core-hours cap {core_hours}, order {order}, binary {binary_sha256()[:16]}")
    t0 = time.monotonic()
    rows, spent, committed = [], 0.0, 0.0
    cap_seconds = core_hours * 3600 if core_hours else float("inf")
    pending, running, stopped = list(jobs), {}, False
    with Pool(workers) as pool:
        while pending or running:
            while pending and len(running) < workers and not stopped:
                if spent + committed + pending[0][3] > cap_seconds:
                    stopped = True
                    break
                job = pending.pop(0)
                running[job[0]] = (pool.apply_async(_job, (job,)), job[3])
                committed += job[3]
            if not running:
                break
            finished = [nm for nm, (res, _) in running.items() if res.ready()]
            if not finished:
                time.sleep(0.3)
                continue
            for nm in finished:
                res, b = running.pop(nm)
                committed -= b
                row = res.get()
                rows.append(row)
                spent += float(row["seconds"])
                pd.DataFrame([row]).to_csv(SEARCH_CSV, mode="a", header=not SEARCH_CSV.exists(), index=False)
                k = len(rows)
                if k % 20 == 0 or k == len(jobs) or row["n"] > 60:
                    log(f"  {k}/{len(jobs)} done, {time.monotonic() - t0:.0f} s wall, {spent / 3600:.2f} core-h; "
                        f"last {row['instance_name']!r} (n={row['n']}): B {row['b_value']} opt {row['optimum']} "
                        f"S {row['S']} widths {row['branch_widths']} ({row['c_calls']} C calls, {row['seconds']:.0f} s)")
        if stopped and pending:
            (OUT / "not_reached.txt").write_text("".join(j[0] + "\n" for j in pending))
            log(f"  core-hour cap {core_hours} reached at {spent / 3600:.2f} core-h: {len(pending)} not reached")
    frame = pd.read_csv(SEARCH_CSV) if SEARCH_CSV.exists() else pd.DataFrame(rows)
    log(f"run done: {len(frame)} rows, {time.monotonic() - t0:.0f} s wall, {spent / 3600:.2f} core-h this run")
    return frame


# ----------------------------------------------------------------------------
# stage: connectivity (why the residual has no small separator)
# ----------------------------------------------------------------------------


def _connectivity_job(args) -> dict:
    import networkx as nx

    name, matrix, optimum = args
    adj = adjacency_from_matrix(np.asarray(matrix, dtype=int))
    g = nx_graph(adj, (1 << len(adj)) - 1)
    t0 = time.monotonic()
    kappa = nx.node_connectivity(g)
    return {"instance_name": name, "n": len(adj), "optimum": optimum, "edges": g.number_of_edges(),
            "min_degree": min(d for _, d in g.degree()), "vertex_connectivity": kappa,
            "small_separator_possible": kappa <= MAX_S, "seconds": round(time.monotonic() - t0, 2)}


def run_connectivity(which: str, workers: int) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    names = resolve_targets(which, led)
    inst = corpus_instances()
    jobs = [(nm, np.asarray(inst[nm][1].matrix, dtype=int), int(led.loc[nm, "optimum"])) for nm in names]
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_connectivity_job, jobs))
    frame = pd.DataFrame(rows).sort_values("instance_name")
    frame.to_csv(CONNECTIVITY_CSV, index=False)
    log(f"connectivity: {len(frame)} instances; vertex connectivity min {frame.vertex_connectivity.min()}, "
        f"max {frame.vertex_connectivity.max()}; separators of size <= {MAX_S} possible on "
        f"{int(frame.small_separator_possible.sum())}")
    return frame


# ----------------------------------------------------------------------------
# stage: check
# ----------------------------------------------------------------------------


def _check_job(args) -> dict:
    d, c_cap = args
    sys.path.insert(0, str(ROOT / "paper1"))
    import obstruction_check as oc

    d = Path(d)
    t0 = time.monotonic()
    res = oc.check_branch(d / "instance.mosp", d / "branch.json", c_cap=c_cap, c_binary=C_BINARY)
    return {"instance_name": res.get("instance_name"), "floor": res.get("floor_claimed"), "k": res.get("k"),
            "nodes_checked": res.get("nodes_checked"), "c_reruns": res.get("c_reruns"),
            "verdict": res.get("verdict"), "failed": "; ".join(c["check"] for c in res["checks"] if not c["ok"]),
            "seconds": round(time.monotonic() - t0, 2), "certificate": str(d / "branch.json")}


def check_all(workers: int, c_cap: float = C_CAP_SECONDS * 5) -> pd.DataFrame:
    jobs = [(str(d), c_cap) for d in sorted(CERT_DIR.iterdir()) if (d / "branch.json").exists()] if CERT_DIR.exists() else []
    log(f"check: {len(jobs)} certificates, {workers} workers, C cap {c_cap:g} s")
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_check_job, jobs))
    frame = pd.DataFrame(rows).sort_values("instance_name") if rows else pd.DataFrame(rows)
    frame.to_csv(CHECKER_CSV, index=False)
    if len(frame):
        log(f"check done: verdicts {frame.verdict.value_counts().to_dict()}")
    return frame


# ----------------------------------------------------------------------------
# stage: tables
# ----------------------------------------------------------------------------


def _md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) + "\n"


def joined() -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    rf = record_floors(led)
    s = pd.read_csv(SEARCH_CSV)
    for col in ("floor0", "lb_best", "tw1", "omega", "excess", "collection", "e_floor", "m_floor", "record", "gap_record"):
        s[col] = s["instance_name"].map(rf[col])
    s["m"] = s["instance_name"].map(led["m"])
    s["band"] = s["n"].map(band_of)
    s["reference"] = s[["lb_best", "tw1"]].max(axis=1)
    s["b_floor"] = s[["b_value", "omega"]].max(axis=1)        # family B's floor with the clique beside it
    s["gap_b"] = s["optimum"] - s["b_floor"]
    s["gap_b_value"] = s["optimum"] - s["b_value"]
    s["beats_reference"] = s["b_value"] > s["reference"]
    s["beats_record"] = s["b_value"] > s["record"]
    s["beats_floor0"] = s["b_value"] > s["floor0"]
    s["closes"] = s["b_value"] >= s["optimum"]
    s["residual"] = s["instance_name"].isin(residual_names(led))
    s["smallest10"] = s["instance_name"].isin(smallest_ten(led))
    if HARNESS_VALUES.exists():
        hv = pd.read_csv(HARNESS_VALUES)
        hv = hv[hv.source == "corpus"].drop_duplicates("instance_name").set_index("instance_name")
        for col in ("sep_branch", "sep_branch_seed", "cut_branch", "contract_branch"):
            s[col] = s["instance_name"].map(hv[col])
        s["sep_branch_gain"] = s["sep_branch"] - s["sep_branch_seed"]
        s["b_above_seeded"] = s["b_value"] > s["sep_branch"]
    s["excess_tercile"] = pd.qcut(s["excess"], 3, labels=["low", "mid", "high"]) if s["excess"].nunique() > 3 else "n/a"
    s.to_csv(OUT / "joined.csv", index=False)
    return s


def write_tables() -> str:
    s = joined()
    order = [f"{lo}–{hi}" for lo, hi in BANDS]
    parts = [f"# Family B by search: tables (item 06)\n\n*Generated by `python3 -m learning.obstruction_branch --stage tables` "
             f"on {time.strftime('%Y-%m-%d %H:%M')}; {len(s)} instances run (n = {int(s.n.min())}–{int(s.n.max())}).*\n"]

    def summary(g: pd.DataFrame) -> dict:
        has = g["has_triple"].astype(bool)
        return {"instances": len(g), "with a linked triple": int(has.sum()),
                "B closes": int(g["closes"].fillna(False).sum()),
                "B > record": int(g["beats_record"].fillna(False).sum()),
                "B > reference": int(g["beats_reference"].fillna(False).sum()),
                "B > floor0": int(g["beats_floor0"].fillna(False).sum()),
                "B > seeded §38": int(g["b_above_seeded"].fillna(False).sum()) if "b_above_seeded" in g else None,
                "mean gap, B value (where a triple)": round(float(g.loc[has, "gap_b_value"].mean()), 2) if has.any() else None,
                "mean gap, max(B, ω)": round(float(g["gap_b"].mean()), 2),
                "mean gap, record": round(float(g["gap_record"].mean()), 2),
                "potential reaches optimum": int((g["b_potential"] >= g["optimum"]).sum()) if "b_potential" in g else None,
                "mean gap, potential (where a triple)": round(float((g.loc[has, "optimum"] - g.loc[has, "b_potential"]).mean()), 2)
                if has.any() and "b_potential" in g else None,
                "censored": int(g["censored"].astype(bool).sum()),
                "C calls (mean)": round(float(g["c_calls"].mean()), 1),
                "seconds (mean)": round(float(g["seconds"].mean()), 1)}

    parts.append("## (a) The residual instances (`floor < optimum` after items 03–05): closed / raised / unchanged by B\n")
    r = s[s.residual].sort_values("instance_name")
    cols = ["instance_name", "n", "optimum", "record", "e_floor", "m_floor", "b_value", "b_potential", "has_triple", "S_size",
            "separators_family", "separators_evaluated", "separators_with_3_comps", "c_calls", "seconds"]
    parts.append(_md(r[cols]) if len(r) else "(no residual instance run)\n")
    parts.append(f"\nClosed by B: {int(r['closes'].fillna(False).sum())}; raised above the record: "
                 f"{int(r['beats_record'].fillna(False).sum())}; unchanged: "
                 f"{int((~r['beats_record'].fillna(False)).sum())} of {len(r)}.\n")
    if CONNECTIVITY_CSV.exists():
        c = pd.read_csv(CONNECTIVITY_CSV)
        parts.append("\n## (a′) Vertex connectivity of the residual instances (networkx `node_connectivity`, exact)\n")
        parts.append(_md(c[["instance_name", "n", "optimum", "edges", "min_degree", "vertex_connectivity",
                            "small_separator_possible", "seconds"]]))
    parts.append("\n## (b) Every run instance by band\n")
    rows = [dict(band=b, **summary(g)) for b, g in s.groupby("band") if len(g)]
    rows = sorted(rows, key=lambda r: order.index(r["band"]) if r["band"] in order else 99)
    rows.append(dict(band="all", **summary(s)))
    parts.append(_md(pd.DataFrame(rows)))
    parts.append("\n## (c) By excess tercile (realised `(n_ones − m) / n`)\n")
    rows = [dict(excess=str(b), **summary(g)) for b, g in s.groupby("excess_tercile", observed=True) if len(g)]
    parts.append(_md(pd.DataFrame(rows)) if rows else "(n/a)\n")
    parts.append("\n## (d) By collection\n")
    rows = [dict(collection=b, **summary(g)) for b, g in s.groupby("collection") if len(g)]
    parts.append(_md(pd.DataFrame(rows)))
    parts.append("\n## (e) The certificates: `|S|`, the branch widths (pathwidth units) and sizes, the kinds\n")
    c = s[s.has_triple.astype(bool)].sort_values(["n", "instance_name"])
    cols = ["instance_name", "n", "optimum", "omega", "reference", "record", "b_value", "b_potential", "S_size", "S",
            "branch_widths", "branch_sizes", "branch_kinds", "branch_depth2", "c_calls", "censored"]
    parts.append(_md(c[cols]) if len(c) else "(no certificate)\n")
    parts.append("\n## (f) Against §38's seeded form (`sep_branch` of `learning.bound_harness`, seed `max(ω − 1, tw)`)\n")
    if "sep_branch" in s:
        hv = s.dropna(subset=["sep_branch"])
        has = hv.has_triple.astype(bool)
        rows = [{"instances with §38 values": len(hv),
                 "§38 sep_branch above its seed": int((hv.sep_branch_gain > 0).sum()),
                 "B value above §38 sep_branch": int(hv.b_above_seeded.fillna(False).sum()),
                 "B value below §38 sep_branch (where a triple)": int((hv.loc[has, "b_value"] < hv.loc[has, "sep_branch"]).sum()),
                 "B value equal to §38 (where a triple)": int((hv.loc[has, "b_value"] == hv.loc[has, "sep_branch"]).sum()),
                 "max(B, ω) above §38 sep_branch": int((hv.b_floor > hv.sep_branch).sum()),
                 "max(B, ω) equal to §38": int((hv.b_floor == hv.sep_branch).sum()),
                 "max(B, ω) below §38": int((hv.b_floor < hv.sep_branch).sum())}]
        parts.append(_md(pd.DataFrame(rows)))
        sub = hv[hv.b_above_seeded.fillna(False)]
        if len(sub):
            parts.append("\nWhere exact branch widths add over the seeded form:\n\n")
            parts.append(_md(sub[["instance_name", "n", "optimum", "sep_branch", "sep_branch_seed", "b_value",
                                  "branch_widths", "record"]]))
    else:
        parts.append("(harness values not on disk)\n")
    parts.append("\n## (g) The ten smallest gap instances (§6's family) and the hand instances\n")
    t = s[s.smallest10].sort_values(["n", "instance_name"])
    cols = ["instance_name", "n", "m", "optimum", "omega", "lb_best", "tw1", "record", "b_value", "b_potential", "S",
            "branch_widths", "branch_sizes", "separators_with_3_comps"]
    parts.append(_md(t[cols]) if len(t) else "(not run)\n")
    if HAND_CSV.exists():
        parts.append("\n" + _md(pd.read_csv(HAND_CSV)))
    if CHECKER_CSV.exists():
        ck = pd.read_csv(CHECKER_CSV)
        parts.append("\n## (h) Checker verdicts\n")
        parts.append(_md(ck.groupby("verdict").agg(certificates=("certificate", "size"), nodes=("nodes_checked", "sum"),
                                                   c_reruns=("c_reruns", "sum"), seconds=("seconds", "sum")).reset_index()))
    text = "".join(parts)
    TABLES_MD.write_text(text)
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# item 07: the complete ternary tree by the branch lemma, and the 24 open classes
# ----------------------------------------------------------------------------

OPEN_OUT = SCRATCH / "07_open"
OPEN_CSV = OPEN_OUT / "branch.csv"
OPEN_CERT_DIR = OPEN_OUT / "certificates"
OPEN_C_CAP = 20.0
OPEN_SECONDS = 240.0
OPEN_MAX_FRACTION = 0.90      # never a C call on a branch above this fraction of the open graph


def ternary_tree_certificate(n: int, edges: list[tuple[int, int]], name: str = "BalancedTree_3_5") -> dict:
    """The nested B certificate of a complete ternary tree, by the branch
    lemma down the tree: at every internal vertex `v`, `S = {v}`, the three
    child subtrees are the branches (connected, disjoint, each adjacent to
    `v`), the three connectors are `Q = {v}`; a vertex whose children are
    leaves certifies `k + 1 = 1` from three `trivial` leaves (claim 0), and
    a vertex at height `h` certifies `h`. Own code: checks that the edge
    list is a tree (connected, `m = n − 1`), finds the root as the unique
    vertex of degree 3 (internal vertices have degree 4, leaves 1), and
    checks that every internal vertex has exactly three children and that
    every leaf is at the same depth. Raises `ValueError` otherwise. The
    value is classical (Ellis, Sudborough & Turner 1994 compute the pathwidth
    of a tree in linear time); the certificate is what is new to the record."""
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    if len(edges) != n - 1:
        raise ValueError(f"not a tree: {len(edges)} edges on {n} vertices")
    seen, stack = {0}, [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    if len(seen) != n:
        raise ValueError("not a tree: disconnected")
    roots = [v for v in range(n) if len(adj[v]) == 3]
    if len(roots) != 1:
        raise ValueError(f"expected one vertex of degree 3 (the root), found {len(roots)}")
    root = roots[0]
    depth_of_leaves = set()

    def build(v: int, parent: int | None, depth: int) -> tuple[dict, int]:
        children = sorted(adj[v] - ({parent} if parent is not None else set()))
        if not children:
            depth_of_leaves.add(depth)
            return {"kind": "trivial", "vertices": [v], "pathwidth_at_least": 0, "source": "trivial"}, 0
        if len(children) != 3:
            raise ValueError(f"vertex {v} has {len(children)} children, not 3")
        subs = [build(c, v, depth + 1) for c in children]
        k = min(h for _, h in subs)
        if any(h != k for _, h in subs):
            raise ValueError(f"vertex {v}: subtrees of unequal height")
        verts = sorted({v} | {x for nd, _ in subs for x in nd["vertices"]})
        links = []
        for i, j in ((0, 1), (0, 2), (1, 2)):
            links.append({"Q": [v], "edge_first": [v, children[i]], "edge_second": [v, children[j]], "pair": [i, j]})
        node = {"kind": "branch", "vertices": verts, "pathwidth_at_least": k + 1, "k": k, "S": [v],
                "branches": [nd for nd, _ in subs], "links": links, "source": "branch", "n_comps": 3}
        return node, k + 1

    node, height = build(root, None, 0)
    if len(depth_of_leaves) != 1:
        raise ValueError(f"leaves at depths {sorted(depth_of_leaves)}: not complete")
    adj_masks = [0] * n
    for a, b in edges:
        adj_masks[a] |= 1 << b
        adj_masks[b] |= 1 << a
    cert = certificate_dict(name, None, adj_masks, {"node": node, "stats": {"seconds": 0.0, "method": "theorem"}},
                            None, 0.0)
    cert.update({"height": height, "root": root,
                 "method": "branch_lemma down the complete ternary tree (S = {v}, three child subtrees, Q = {v}); "
                           "pw(T_h) >= h by induction, h = 1 the claw K_{1,3}",
                 "classical": "Ellis, Sudborough & Turner (1994) compute the pathwidth of a tree in linear time; "
                              "the value is classical and only the certificate is new to the record"})
    return cert


def _open_job(args) -> dict:
    rec, seconds, cap, rng_seed = args
    adj = rec["adj"]
    n = len(adj)
    position = None
    if rec.get("layout"):
        position = [0] * n
        for i, v in enumerate(rec["layout"]):
            position[v] = i
    max_m = int(OPEN_MAX_FRACTION * n)
    t0 = time.monotonic()
    res = branch_search(adj, seconds, cap, DEPTH, rng_seed, "c", True, False, position=position, max_m=max_m,
                        greedy_max_m=120)
    out = {"id": rec["id"], "names": rec["names"], "n": n, "m": rec["m"], "width": rec["width"],
           "lower": rec["lower"], "b_pathwidth": res["value"] if res["value"] >= 0 else None,
           "b_floor": res["value"] + 1 if res["value"] >= 0 else None,
           "b_potential": res["stats"].get("best_potential", 0),
           "S": json.dumps(res["S"]) if res["S"] is not None else None,
           "branch_sizes": json.dumps([len(b["vertices"]) for b in res["node"]["branches"]]) if res["node"] else None,
           "branch_widths": json.dumps(branch_widths(res["node"])) if res["node"] else None,
           "max_m": max_m, "seconds_budget": seconds, "c_cap": cap, "seconds": round(time.monotonic() - t0, 1)}
    for k in ("separators_family", "separators_evaluated", "separators_with_3_comps", "local_moves", "local_starts",
              "censored", "c_calls", "c_seconds", "skipped_large", "leaves_cached"):
        out[k] = res["stats"].get(k)
    out["above_width"] = out["b_pathwidth"] is not None and out["b_pathwidth"] > rec["width"]
    out["meets_width"] = out["b_pathwidth"] is not None and out["b_pathwidth"] >= rec["width"]
    out["above_floor"] = out["b_pathwidth"] is not None and rec["lower"] is not None and out["b_pathwidth"] > rec["lower"]
    if res["node"] is not None:
        d = OPEN_CERT_DIR / rec["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "instance.txt").write_text(f"{n} {rec['m']}\n" + "".join(f"{a} {b}\n" for a, b in rec["edges"]))
        cert = certificate_dict(rec["id"], None, adj, res, None, cap)
        cert.update({"names": rec["names"], "recorded_width": rec["width"], "recorded_floor": rec["lower"],
                     "max_branch_vertices": max_m, "units_note": "a dataset class: the width is a pathwidth; "
                     "floor = pathwidth_proved + 1 is in optimum units as everywhere in this loop"})
        (d / "branch.json").write_text(json.dumps(cert, indent=1))
        out["certificate"] = str((d / "branch.json").relative_to(ROOT))
    return out


def run_open(workers: int, seconds: float = OPEN_SECONDS, cap: float = OPEN_C_CAP, rng_seed: int = 1,
             ids: list[str] | None = None) -> pd.DataFrame:
    """Family B on the 24 open classes: a lower-bound search only. The leaf
    oracle never calls the C program on a branch above 90% of the vertices
    (the item's rule), uses the recorded layout restricted to a branch as its
    upper bound, and runs no minor leaves; the complete ternary tree is done
    on paper by `ternary_tree_certificate` and is skipped here."""
    from learning.obstruction_ledger import open_class_graphs

    OPEN_OUT.mkdir(parents=True, exist_ok=True)
    recs = open_class_graphs(ids, check_representative=False)
    done = set(pd.read_csv(OPEN_CSV)["id"]) if OPEN_CSV.exists() else set()
    jobs = [(r, seconds, cap, rng_seed) for r in recs if r["id"] not in done and r["names"] != "BalancedTree_3_5"]
    jobs.sort(key=lambda j: -j[0]["n"])
    log(f"open: {len(recs)} classes, {len(jobs)} to run, {workers} workers, {seconds:g} s each, C cap {cap:g} s, "
        f"no branch above {OPEN_MAX_FRACTION:.0%} of n, binary {binary_sha256()[:16]}", OPEN_OUT / "run.log")
    t0 = time.monotonic()
    with Pool(workers) as pool:
        for k, row in enumerate(pool.imap_unordered(_open_job, jobs, chunksize=1), 1):
            pd.DataFrame([row]).to_csv(OPEN_CSV, mode="a", header=not OPEN_CSV.exists(), index=False)
            log(f"  {k}/{len(jobs)} {row['id']} n={row['n']} width {row['width']} floor {row['lower']}: "
                f"B {row['b_pathwidth']} (potential {row['b_potential']}), {row['c_calls']} C calls, "
                f"{row['seconds']} s", OPEN_OUT / "run.log")
    frame = pd.read_csv(OPEN_CSV).drop_duplicates("id", keep="last")
    frame.to_csv(OPEN_CSV, index=False)
    log(f"open done: {len(frame)} rows, {time.monotonic() - t0:.0f} s wall", OPEN_OUT / "run.log")
    return frame


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", required=True, choices=("hand", "run", "check", "connectivity", "tables", "open", "open-tree"))
    ap.add_argument("--targets", default="residual")
    ap.add_argument("--ids", default=None, help="open: comma-separated class ids (default all 24)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seconds", type=float, default=INSTANCE_SECONDS)
    ap.add_argument("--cap", type=float, default=C_CAP_SECONDS)
    ap.add_argument("--core-hours", type=float, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--order", default="small-first", choices=("small-first", "large-first"))
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "hand":
        run_hand()
    elif args.stage == "run":
        run(args.targets, args.workers, args.seconds, args.core_hours, args.seed, args.limit, args.order, args.cap)
    elif args.stage == "check":
        check_all(args.workers, args.cap * 5)
    elif args.stage == "connectivity":
        run_connectivity(args.targets, args.workers)
    elif args.stage == "tables":
        print(write_tables())
    elif args.stage == "open":
        run_open(args.workers, args.seconds if args.seconds != INSTANCE_SECONDS else OPEN_SECONDS,
                 args.cap if args.cap != C_CAP_SECONDS else OPEN_C_CAP, args.seed,
                 args.ids.split(",") if args.ids else None)
    elif args.stage == "open-tree":
        from learning.obstruction_ledger import open_class_graphs

        rec = next(r for r in open_class_graphs(check_representative=False) if r["names"] == "BalancedTree_3_5")
        OPEN_OUT.mkdir(parents=True, exist_ok=True)
        cert = ternary_tree_certificate(rec["n"], rec["edges"], rec["names"])
        cert.update({"id": rec["id"], "recorded_width": rec["width"], "recorded_floor": rec["lower"]})
        (OPEN_OUT / "tree_instance.txt").write_text(f"{rec['n']} {rec['m']}\n" + "".join(f"{a} {b}\n" for a, b in rec["edges"]))
        (OPEN_OUT / "tree_certificate.json").write_text(json.dumps(cert, indent=1))
        print(f"{rec['id']} {rec['names']}: n={rec['n']} m={rec['m']} height {cert['height']} root {cert['root']} "
              f"pathwidth >= {cert['pathwidth_proved']} (recorded width {rec['width']}, floor {rec['lower']}); "
              f"written {OPEN_OUT / 'tree_certificate.json'}")


if __name__ == "__main__":
    main()
