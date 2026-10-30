"""Increment-witness tooling: build families, apply contraction sequences,
call the C pathwidth program, and shrink a graph to a small contraction minor
whose proved pathwidth equals a target.

Conventions
- Vertices are ints 0..n-1.  A sequence step is (v, u): contract v into u
  (u keeps its label; N(u) := N(u) ∪ N(v) − {u, v}), or (v, -1): delete v
  (any vertex, as Lean's `minorOf` allows; the C program's own replay only
  deletes isolated vertices, so deletion steps are flagged in the record).
- Every pathwidth claimed is the C program's proved value (status refutation,
  minor or bound).  `upper` means undecided.
"""
import itertools
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import networkx as nx

ROOT = "/home/al/dev/MOSP"
CLI = os.path.join(ROOT, "pathwidth_solver/cli/pathwidth")
HERE = os.path.join(ROOT, "reports/scratch/increment_witness")
MAX_PROCS = 7      # owner's 24-core run is live; cap at 8 processes total


# ---------------------------------------------------------------- families

def hypercube(d):
    """Q_d on 0..2^d-1 (bit i = coordinate i).  Q_{d-1} is the set of vertices
    with top bit 0 (0..2^{d-1}-1)."""
    G = nx.Graph()
    n = 1 << d
    G.add_nodes_from(range(n))
    for x in range(n):
        for i in range(d):
            y = x ^ (1 << i)
            if x < y:
                G.add_edge(x, y)
    return G


def mycielski_step(G):
    """M(G): originals 0..n-1, shadow of i is n+i (adjacent to N_G(i)), apex 2n."""
    n = G.number_of_nodes()
    H = nx.Graph()
    H.add_nodes_from(range(2 * n + 1))
    for a, b in G.edges():
        H.add_edge(a, b)
        H.add_edge(a, n + b)
        H.add_edge(b, n + a)
    for i in range(n):
        H.add_edge(n + i, 2 * n)
    return H


def mycielski(k):
    """M_2 = K_2, M_3 = C_5, M_4 = Groetzsch, ...  |M_k| = 3·2^{k-2} − 1."""
    G = nx.complete_graph(2)
    for _ in range(k - 2):
        G = mycielski_step(G)
    return G


def ternary_tree(h):
    """Complete ternary tree of height h, BFS labels: root 0, children 1..3, ...
    The subtree rooted at child 1 is a T_{h-1}: vertices v with the path from
    the root through 1."""
    return nx.balanced_tree(3, h)


def ternary_subtree(h, child=1):
    """Vertex set of the T_{h-1} hanging from `child` (1, 2 or 3) of T_h's root."""
    T = ternary_tree(h)
    T2 = T.copy()
    T2.remove_node(0)
    return set(nx.node_connected_component(T2, child))


FAMILIES = {
    "hypercube": (hypercube, {1: 1, 2: 2, 3: 4, 4: 7, 5: 13, 6: 23}, lambda d: set(range(1 << (d - 1)))),
    "mycielski": (mycielski, {2: 1, 3: 2, 4: 5, 5: 10, 6: 20, 7: 38}, lambda k: set(range(3 * 2 ** (k - 3) - 1))),
    "ternary": (ternary_tree, {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}, lambda h: ternary_subtree(h)),
}
# NB mycielski index: here M_k has k-2 steps from K_2 (M_2 = K_2, M_3 = C_5,
# M_4 = Groetzsch = myciel3 of DIMACS = 11 vertices ... ).  DIMACS myciel_j has
# 3·2^{j-1} − 1 vertices: myciel2 = C_5 = our M_3, myciel6 (95) = our M_7.
# Known values indexed by OUR k:  M_2..M_7 = 1, 2, 5, 10, 20, 38.


# ------------------------------------------------------------- graph6 / C

def to_g6(G):
    n = G.number_of_nodes()
    assert set(G.nodes()) == set(range(n)), "relabel to 0..n-1 first"
    return nx.to_graph6_bytes(G, nodes=range(n), header=False).decode().strip()


def from_g6(s):
    return nx.from_graph6_bytes(s.strip().encode())


def relabel(G):
    """Relabel to 0..n-1 preserving sorted order; return (H, old_of_new)."""
    old = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(old)}
    H = nx.relabel_nodes(G, idx, copy=True)
    return H, old


def run_c(G, t=300, layout=True, extra=(), timeout_pad=30):
    """Run the C program; return dict(width, status, layout, minor_line, stderr, seconds)."""
    g6 = to_g6(G)
    cmd = ["nice", "-n", "19", CLI, "-t", str(t), "-v"] + (["-l"] if layout else []) + list(extra)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, input=g6 + "\n", capture_output=True, text=True,
                           timeout=(t if t > 0 else 10 ** 6) + timeout_pad)
    except subprocess.TimeoutExpired:
        return dict(width=None, status="timeout", layout=None, minor_line=None,
                    stderr="", seconds=time.time() - t0, g6=g6)
    out = p.stdout.strip().splitlines()
    res = dict(width=None, status="error", layout=None, minor_line=None,
               stderr=p.stderr.strip(), seconds=time.time() - t0, g6=g6, stdout=p.stdout)
    for line in out:
        if line.startswith("pathwidth "):
            _, w, st = line.split()
            res["width"] = int(w)
            res["status"] = st
        elif line.startswith("layout "):
            res["layout"] = [int(x) for x in line.split()[1:]]
        elif line.startswith("minor "):
            res["minor_line"] = line
    return res


PROVED = {"refutation", "minor", "bound"}


# ------------------------------------------------------- contraction minors

def apply_seq(G, seq):
    """Apply (v, u) steps on a copy; return (H, branch) where branch[x] is the
    surviving representative of x (None if deleted).  H keeps original labels."""
    H = G.copy()
    branch = {x: x for x in G.nodes()}
    for v, u in seq:
        if u == -1:
            assert v in H, (v, u)
            H.remove_node(v)
            for x in branch:
                if branch[x] == v:
                    branch[x] = None
        else:
            assert H.has_edge(v, u), ("not an edge", v, u)
            H = nx.contracted_nodes(H, u, v, self_loops=False, copy=True)
            for x in branch:
                if branch[x] == v:
                    branch[x] = u
    return H, branch


def check_seq(G, seq):
    """Replay with the C program's rules (contract only along edges; delete only
    isolated vertices).  Returns (ok, n_deletions_of_nonisolated)."""
    H = G.copy()
    bad = 0
    for v, u in seq:
        if u == -1:
            if H.degree(v) > 0:
                bad += 1
            H.remove_node(v)
        else:
            if not H.has_edge(v, u):
                return False, bad
            H = nx.contracted_nodes(H, u, v, self_loops=False, copy=True)
    return True, bad


def preserves_copy(seq, copy):
    """True iff no step removes a vertex of `copy` (so copy stays a subgraph:
    its vertices survive and its edges are kept or added to)."""
    return all(v not in copy for v, u in seq)


def proved_width(H, t=300):
    """Relabel, run C; return (width or None, status, result)."""
    H2, old = relabel(H)
    r = run_c(H2, t=t, layout=False)
    if r["status"] in PROVED:
        return r["width"], r["status"], r
    return None, r["status"], r


# ------------------------------------------------------------ shrink search

def candidates(H, mode, rng, protect=frozenset()):
    """Yield (v, u) contraction candidates in an order given by `mode`."""
    nodes = [v for v in H.nodes() if v not in protect]
    if mode == "min-d":
        # min-degree vertex first, into the neighbour of least degree
        nodes.sort(key=lambda v: (H.degree(v), v))
        for v in nodes:
            nbrs = sorted(H.neighbors(v), key=lambda u: (H.degree(u), u))
            for u in nbrs:
                yield (v, u)
    elif mode == "least-c":
        nodes.sort(key=lambda v: (H.degree(v), v))
        for v in nodes:
            nbrs = sorted(H.neighbors(v), key=lambda u: (len(set(H[u]) & set(H[v])), H.degree(u), u))
            for u in nbrs:
                yield (v, u)
    elif mode == "random":
        edges = [(v, u) for v, u in H.edges() if v not in protect] + \
                [(u, v) for v, u in H.edges() if u not in protect]
        rng.shuffle(edges)
        for e in edges:
            yield e
    elif mode == "delete":
        nodes.sort(key=lambda v: (H.degree(v), v))
        for v in nodes:
            yield (v, -1)
    else:
        raise ValueError(mode)


def shrink(G, w, modes=("min-d",), protect=frozenset(), t=120, seed=0,
           max_tries_per_round=None, log=print, workers=MAX_PROCS, allow_delete=False,
           max_rounds=10 ** 6, time_limit=None):
    """Greedy: repeatedly apply the first candidate minor operation that keeps the
    C-proved width equal to w.  Stops when a round finds none (local minimum).
    Returns (H, seq, trace)."""
    rng = random.Random(seed)
    H = G.copy()
    seq = []
    trace = []
    t_start = time.time()
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        if time_limit and time.time() - t_start > time_limit:
            log(f"  time limit reached after {rounds-1} rounds")
            break
        cands = []
        seen = set()
        for mode in modes:
            for c in candidates(H, mode, rng, protect):
                if c not in seen:
                    seen.add(c)
                    cands.append(c)
        if allow_delete:
            for c in candidates(H, "delete", rng, protect):
                if c not in seen:
                    seen.add(c)
                    cands.append(c)
        if max_tries_per_round:
            cands = cands[:max_tries_per_round]
        accepted = None
        tried = 0
        # evaluate in parallel batches, accept the first success in order
        batch = max(1, workers)
        for i in range(0, len(cands), batch):
            chunk = cands[i:i + batch]
            with ThreadPoolExecutor(max_workers=batch) as ex:
                results = list(ex.map(lambda c: _eval(H, c, w, t), chunk))
            tried += len(chunk)
            for c, (ok, width, status, secs) in zip(chunk, results):
                trace.append((len(seq), c, width, status, round(secs, 2)))
                if ok and accepted is None:
                    accepted = c
            if accepted is not None:
                break
        if accepted is None:
            log(f"  round {rounds}: no acceptable step among {tried} candidates; |V|={H.number_of_nodes()} |E|={H.number_of_edges()}")
            break
        v, u = accepted
        H, _ = apply_seq(H, [accepted])
        seq.append(accepted)
        log(f"  step {len(seq)}: {'delete' if u == -1 else 'contract'} {v}{'' if u == -1 else '->' + str(u)}  "
            f"|V|={H.number_of_nodes()} |E|={H.number_of_edges()}  tried {tried}  {time.time()-t_start:.0f}s")
    return H, seq, trace


def _eval(H, c, w, t):
    try:
        H2, _ = apply_seq(H, [c])
    except AssertionError:
        return (False, None, "invalid", 0.0)
    if H2.number_of_nodes() <= w:          # pw ≤ n-1 < w
        return (False, None, "too-small", 0.0)
    width, status, r = proved_width(H2, t=t)
    ok = (width == w)
    return (ok, width if width is not None else r["width"], status, r["seconds"])


# -------------------------------------------------------------- describe

def describe(H, copy=None):
    n, m = H.number_of_nodes(), H.number_of_edges()
    degs = sorted((d for _, d in H.degree()), reverse=True)
    from collections import Counter
    dc = Counter(degs)
    s = f"|V|={n} |E|={m} degrees " + " ".join(f"{d}^{c}" for d, c in sorted(dc.items(), reverse=True))
    if copy is not None:
        inside = [v for v in H.nodes() if v in copy]
        outside = [v for v in H.nodes() if v not in copy]
        s += f"; {len(inside)} vertices of the G_k copy survive, {len(outside)} new-part vertices survive"
    return s


def save(name, H, seq, result, extra=""):
    H2, old = relabel(H)
    g6 = to_g6(H2)
    with open(os.path.join(HERE, name + ".g6"), "w") as f:
        f.write(g6 + "\n")
    with open(os.path.join(HERE, name + ".cert.txt"), "w") as f:
        f.write(f"# {name}\n# contraction sequence (v,u): contract v into u; (v,-1) deletes v; original labels\n")
        f.write("seq " + " ".join(f"{v},{u}" for v, u in seq) + "\n")
        f.write("labels(new->old) " + " ".join(f"{i}:{o}" for i, o in enumerate(old)) + "\n")
        f.write("graph6 " + g6 + "\n")
        f.write("C stdout:\n" + (result.get("stdout") or "") + "\nC stderr:\n" + (result.get("stderr") or "") + "\n")
        if extra:
            f.write(extra + "\n")
    return g6
