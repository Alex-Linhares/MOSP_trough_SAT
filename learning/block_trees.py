"""loop0010 item 03: block graphs from incidence forests, and the candidates for their pathwidth.

When the customer-pattern incidence graph `B` is a forest (`gamma = 0`, item 01),
the MOSP graph is a *block graph* whose blocks are the pattern cliques: every
pattern is a clique, two patterns share at most one customer, and the sharing
has no cycles. This module builds three families of such instances and the
candidate formulas for their pathwidth, and drives the C program
`pathwidth_solver/cli/pathwidth` (graph6 on stdin) that computes the exact
value. Nothing here solves a MOSP instance through the Python solvers, and
nothing writes to `solutions/`.

Families:

* `clique_tree(s, h, b)` -- `CT(s, h, b)`: one root clique `K_s`; every
  customer at depth `d < h` is the hub of `b` new cliques of size `s`, each
  adding `s - 1` customers at depth `d + 1`. `CT(2, h, b)` is a tree in which
  every customer has `b` children, two of them (the root pair) adjacent;
  `CT(2, h, 3)` is two complete ternary trees of height `h` joined at their
  roots, the tree `Sandwich.lean: branch_lemma` bites on at every level.
  `ct_size(s, h, b) = s * sum_{d <= h} (b (s - 1))^d` customers.
* `caterpillar_of_cliques(s, length)`: a chain of `length` cliques `K_s`,
  consecutive ones sharing one customer, with a pendant `K_s` at every
  customer that is not shared -- the case where the additive and the
  multiplicative candidates differ most.
* `random_block_tree(n, d, seed)`: start from one pattern; attach a pattern of
  random size -- Chu & Stuckey's size law, `Binomial(n, d / n)` with 0 and 1
  moved up to 2 (`reports/scratch/clique_cover_moment/REPORT_generator.md`
  §1.2) -- at a uniformly random existing customer, until `n` customers.

Candidates (`candidates`), each a function of the forest: `omega - 1` (the
clique floor), `omega - 1 + pw(B)` and `omega - 2 + pw(B)` (additive in the
incidence tree's pathwidth), `omega - 1 + h` (additive in the block height),
the blow-up bound `omega (pw(B) + 1) - 1` (a path decomposition of `B` with
each pattern vertex replaced by its clique), and the TreeBound form
`omega (tb(n + m) + 1) - 1` with `tb(N)` the least `k` with
`N <= (5 * 3^k - 3) / 2` (`TreeBound.lean`).

`block_height(patterns, n)` is the radius of the pattern adjacency forest in
pattern steps, the `h` of `CT(s, h, b)` extended to any forest.
"""
from __future__ import annotations

import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import networkx as nx
import numpy as np

PATHWIDTH_BIN = Path(__file__).resolve().parents[1] / "pathwidth_solver" / "cli" / "pathwidth"

Patterns = list[list[int]]


# ----------------------------------------------------------------------------
# families
# ----------------------------------------------------------------------------


def ct_size(s: int, h: int, b: int) -> int:
    """Customers of `CT(s, h, b)`: `s * sum_{d=0}^{h} (b (s - 1))^d`."""
    q = b * (s - 1)
    return s * sum(q**d for d in range(h + 1))


def clique_tree(s: int, h: int, b: int) -> tuple[Patterns, list[int]]:
    """`CT(s, h, b)` as a list of patterns (lists of customers) and the depth of every customer."""
    if s < 2 or h < 0 or b < 0:
        raise ValueError("CT(s, h, b) needs s >= 2, h >= 0, b >= 0")
    patterns: Patterns = [list(range(s))]
    depth = [0] * s
    frontier = list(range(s))
    n = s
    for d in range(h):
        new_frontier: list[int] = []
        for hub in frontier:
            for _ in range(b):
                new = list(range(n, n + s - 1))
                n += s - 1
                patterns.append([hub] + new)
                depth.extend([d + 1] * (s - 1))
                new_frontier.extend(new)
        frontier = new_frontier
    assert n == ct_size(s, h, b)
    return patterns, depth


def caterpillar_of_cliques(s: int, length: int) -> Patterns:
    """A chain of `length` cliques `K_s` sharing one customer between consecutive
    cliques, with a pendant `K_s` at every customer of the chain that is not
    shared (so `s - 2` pendants per interior clique, `s - 1` per end clique)."""
    if s < 2 or length < 1:
        raise ValueError("needs s >= 2 and length >= 1")
    patterns: Patterns = []
    n = 0
    chain: Patterns = []
    prev_last = None
    for i in range(length):
        if prev_last is None:
            clique = list(range(n, n + s))
            n += s
        else:
            clique = [prev_last] + list(range(n, n + s - 1))
            n += s - 1
        chain.append(clique)
        prev_last = clique[-1]
    shared = set()
    for a, c in zip(chain, chain[1:]):
        shared |= set(a) & set(c)
    patterns.extend(chain)
    for clique in chain:
        for v in clique:
            if v not in shared:
                patterns.append([v] + list(range(n, n + s - 1)))
                n += s - 1
    return patterns


def cs_pattern_size(rng: np.random.Generator, n: int, d: float) -> int:
    """Chu & Stuckey's size law: `Binomial(n, d / n)` with 0 and 1 moved up to 2."""
    return max(2, int(rng.binomial(n, min(1.0, d / n))))


def random_block_tree(n: int, d: float, seed: int) -> Patterns:
    """A random block tree on exactly `n` customers: one pattern, then patterns
    of random size (the size law above, the last one truncated to fit) attached
    at a uniformly random existing customer. Regenerates byte for byte from
    `(n, d, seed)`."""
    if n < 2:
        raise ValueError("needs n >= 2")
    rng = np.random.default_rng(seed)
    s = min(cs_pattern_size(rng, n, d), n)
    patterns: Patterns = [list(range(s))]
    count = s
    while count < n:
        s = min(cs_pattern_size(rng, n, d), n - count + 1)
        hub = int(rng.integers(count))
        patterns.append([hub] + list(range(count, count + s - 1)))
        count += s - 1
    return patterns


# ----------------------------------------------------------------------------
# graphs
# ----------------------------------------------------------------------------


def n_customers(patterns: Patterns) -> int:
    return 1 + max(v for p in patterns for v in p)


def matrix_of(patterns: Patterns, n: int | None = None) -> np.ndarray:
    """The `n x m` 0/1 matrix, rows = customers, columns = patterns."""
    n = n_customers(patterns) if n is None else n
    a = np.zeros((n, len(patterns)), dtype=int)
    for j, p in enumerate(patterns):
        a[p, j] = 1
    return a


def mosp_graph(patterns: Patterns, n: int | None = None) -> nx.Graph:
    """Customers as vertices, a clique per pattern."""
    n = n_customers(patterns) if n is None else n
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for p in patterns:
        for i, u in enumerate(p):
            for v in p[i + 1:]:
                g.add_edge(u, v)
    return g


def incidence_graph(patterns: Patterns, n: int | None = None) -> nx.Graph:
    """Customers `0..n-1` and patterns `n..n+m-1`, an edge per one of the matrix."""
    n = n_customers(patterns) if n is None else n
    g = nx.Graph()
    g.add_nodes_from(range(n + len(patterns)))
    for j, p in enumerate(patterns):
        for v in p:
            g.add_edge(v, n + j)
    return g


def pattern_adjacency(patterns: Patterns) -> nx.Graph:
    """Patterns as vertices, adjacent when they share a customer."""
    g = nx.Graph()
    g.add_nodes_from(range(len(patterns)))
    owner: dict[int, list[int]] = {}
    for j, p in enumerate(patterns):
        for v in p:
            owner.setdefault(v, []).append(j)
    for js in owner.values():
        for i, a in enumerate(js):
            for b in js[i + 1:]:
                g.add_edge(a, b)
    return g


def is_incidence_forest(patterns: Patterns, n: int | None = None) -> bool:
    return nx.is_forest(incidence_graph(patterns, n))


def block_height(patterns: Patterns) -> int:
    """The radius of the pattern adjacency forest in pattern steps, maximised
    over components: `h` for `CT(s, h, b)`, 0 for a single pattern."""
    g = pattern_adjacency(patterns)
    best = 0
    for comp in nx.connected_components(g):
        sub = g.subgraph(comp)
        best = max(best, nx.radius(sub))
    return best


def ternary_subtree_height(tree: nx.Graph) -> int:
    """The height of the largest complete ternary tree contained in `tree` as a
    rooted subtree (every internal vertex with at least three children), over
    all roots. A lower bound on the tree's pathwidth: the complete ternary tree
    of height `h` has pathwidth `h` (`TreeBound.lean: pathwidth_ternaryTree`)
    and pathwidth is monotone under subgraphs."""
    if not nx.is_forest(tree):
        raise ValueError("needs a forest")
    import sys
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 4 * tree.number_of_nodes() + 100))

    def height(v, parent):
        kids = sorted((height(w, v) for w in tree.neighbors(v) if w != parent), reverse=True)
        return 1 + kids[2] if len(kids) >= 3 else 0

    return max((height(v, None) for v in tree.nodes), default=0)


def largest_pattern(patterns: Patterns) -> int:
    return max(len(p) for p in patterns)


def graph6(g: nx.Graph) -> str:
    return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(g), header=False).decode().strip()


# ----------------------------------------------------------------------------
# candidates
# ----------------------------------------------------------------------------


def tree_bound(N: int) -> int:
    """`tb(N)`: the least `k` with `N <= (5 * 3^k - 3) / 2` (1, 6, 21, 66, ...); 0 for `N <= 1`.
    `TreeBound.lean`: a tree on at most `treeBound k` vertices has pathwidth at most `k`."""
    if N <= 1:
        return 0
    k = 0
    while (5 * 3**k - 3) // 2 < N:
        k += 1
    return k


CANDIDATES = ("omega-1", "omega-1+pw(B)", "omega-2+pw(B)", "omega-1+h", "omega(pw(B)+1)-1", "omega(tb+1)-1")


def candidates(omega: int, pw_b: int, h: int, n_plus_m: int) -> dict[str, int]:
    """Every candidate as a function of the forest's invariants."""
    tb = tree_bound(n_plus_m)
    return {
        "omega-1": omega - 1,
        "omega-1+pw(B)": omega - 1 + pw_b,
        "omega-2+pw(B)": max(omega - 1, omega - 2 + pw_b),
        "omega-1+h": omega - 1 + h,
        "omega(pw(B)+1)-1": omega * (pw_b + 1) - 1,
        "omega(tb+1)-1": omega * (tb + 1) - 1,
    }


# ----------------------------------------------------------------------------
# the C program
# ----------------------------------------------------------------------------

_VERBOSE = re.compile(r"n=(\d+) width=(-?\d+) status=(\w+) lower=(-?\d+) upper_start=(-?\d+) nodes=(\d+)"
                      r".*?seconds=([\d.]+)")


def run_pathwidth_one(g6: str, timeout: float = 600.0, nice: int = 19,
                      binary: Path = PATHWIDTH_BIN) -> dict:
    """Exact pathwidth of one graph6 string by the C program, with its layout
    and statistics. `status == "upper"` is a censored run: `width` is then an
    upper bound, never a value."""
    cmd = ["nice", "-n", str(nice), str(binary), "-t", str(int(timeout)), "-l", "-v"]
    proc = subprocess.run(cmd, input=g6 + "\n", capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"pathwidth failed: {proc.stderr.strip()[:200]}")
    out = proc.stdout.strip().splitlines()
    head = out[0].split()
    if head[0] != "pathwidth":
        raise RuntimeError(f"unexpected output: {out[0]}")
    layout = [int(x) for x in out[1].split()[1:]] if len(out) > 1 and out[1].startswith("layout") else []
    m = _VERBOSE.search(proc.stderr)
    stats = dict(n=int(m.group(1)), lower=int(m.group(4)), upper_start=int(m.group(5)),
                 nodes=int(m.group(6)), seconds=float(m.group(7))) if m else {}
    return {"width": int(head[1]), "status": head[2], "layout": layout, **stats}


def run_pathwidth(g6s: list[str], timeout: float = 600.0, workers: int = 4, nice: int = 19,
                  binary: Path = PATHWIDTH_BIN) -> list[dict]:
    """`run_pathwidth_one` over a list, `workers` processes at a time (each is a
    single-threaded C process under `nice`), results in input order."""
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        return list(pool.map(lambda s: run_pathwidth_one(s, timeout, nice, binary), g6s))


def vertex_separation(g: nx.Graph, layout: list[int]) -> int:
    """The textbook vertex separation of a layout, independent of the C program:
    the largest number of placed vertices with a neighbour still to come."""
    pos = {v: i for i, v in enumerate(layout)}
    nodes = list(nx.convert_node_labels_to_integers(g).nodes)
    g = nx.convert_node_labels_to_integers(g)
    if sorted(pos) != sorted(nodes):
        raise ValueError("layout is not a permutation of the vertices")
    width = 0
    for i in range(len(layout)):
        count = sum(1 for u in layout[: i + 1] if any(pos[w] > i for w in g.neighbors(u)))
        width = max(width, count)
    return width


def default_workers(cap: int = 8) -> int:
    """At most `cap`, 4 when the one-minute load is above 24 (TASK.md)."""
    load = os.getloadavg()[0]
    return min(cap, 4) if load > 24 else cap
