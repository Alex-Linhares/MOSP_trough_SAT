"""The node search number of a block graph by Chou, Ko, Ho & Chen's characterisation (Theorem 4 of
"Node-searching problem on block graphs", Discrete Applied Mathematics 156 (2008) 55-75,
doi:10.1016/j.dam.2007.08.007), as an exact oracle independent of the C search.

For a block graph `G` and `k >= 2`, `ns(G) <= k` iff

* `VC_k`: every vertex has at most two branches (components of `G - x`) with `ns >= k`; and
* `BC_k`: every block `K` has an edge `(x, y)` whose enclosure subgraph `{G}_{x,y}` has `ns < k`,
  where `{G}_{x,y} = G \\ V([G]_{K,x} ∪ (G)_{K,y})`: `[G]_{K,x}` is `x` with everything hanging
  off `x` outside `K` (the non-block fork), `(G)_{K,y}` is everything hanging off `y` outside
  `K` without `y` (the non-block branch). So `{G}_{x,y}` is `K - x` together with the
  non-block branches at the vertices of `K` other than `x` and `y`.

Both conditions are monotone in `k`, so `ns(G) = max(2, VC, BC)` with `VC` one more than
the largest third-largest branch search number over the vertices and `BC` one more than the
largest, over blocks, of the smallest enclosure search number over the block's edges;
`ns = 1` for a single vertex. `pathwidth = ns - 1` (Kinnersley 1992; Kirousis &
Papadimitriou 1986). The recursion is memoised on vertex sets; induced subgraphs of block
graphs are block graphs, and a disconnected graph takes the maximum over its components.

Loop0010 item 03 uses it to cross-check every value the C program produced on clique
trees, caterpillars of cliques and random block trees, and nothing in the solver depends
on it. `VC` alone is the tree rule of Ellis, Sudborough & Turner (1994); `BC` is what the
cliques add, and it is where the factor 3/2 of `CT(s, 1, b)` comes from.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations

import networkx as nx


def is_block_graph(g: nx.Graph) -> bool:
    """Every biconnected component is a clique."""
    for comp in nx.biconnected_components(g):
        sub = g.subgraph(comp)
        k = len(comp)
        if sub.number_of_edges() != k * (k - 1) // 2:
            return False
    return True


class BlockSearch:
    """`ns(S)` for induced subgraphs `S` of one block graph, memoised."""

    def __init__(self, g: nx.Graph):
        if not is_block_graph(g):
            raise ValueError("not a block graph")
        self.g = g
        self.adj = {v: set(g.neighbors(v)) for v in g.nodes}
        self.memo: dict[frozenset, int] = {}

    # -- helpers on an induced subgraph S -------------------------------------------------

    def _components(self, S: frozenset, removed: frozenset = frozenset()) -> list[frozenset]:
        keep = S - removed
        seen: set = set()
        out = []
        for s in keep:
            if s in seen:
                continue
            comp = {s}
            queue = deque([s])
            seen.add(s)
            while queue:
                u = queue.popleft()
                for w in self.adj[u]:
                    if w in keep and w not in seen:
                        seen.add(w)
                        comp.add(w)
                        queue.append(w)
            out.append(frozenset(comp))
        return out

    def _reach(self, S: frozenset, start: set, avoid: frozenset) -> frozenset:
        """Vertices of `S - avoid` reachable from `start` (`start ⊆ S - avoid`)."""
        keep = S - avoid
        seen = set(x for x in start if x in keep)
        queue = deque(seen)
        while queue:
            u = queue.popleft()
            for w in self.adj[u]:
                if w in keep and w not in seen:
                    seen.add(w)
                    queue.append(w)
        return frozenset(seen)

    def ns(self, S: frozenset) -> int:
        if len(S) == 0:
            return 0
        if S in self.memo:
            return self.memo[S]
        comps = self._components(S)
        if len(comps) > 1:
            value = max(self.ns(c) for c in comps)
            self.memo[S] = value
            return value
        if len(S) == 1:
            self.memo[S] = 1
            return 1
        sub = self.g.subgraph(S)
        value = 2
        # VC: at most two branches with ns >= k at every vertex
        for x in nx.articulation_points(sub):
            branch_ns = sorted((self.ns(c) for c in self._components(S, frozenset([x]))), reverse=True)
            if len(branch_ns) >= 3:
                value = max(value, branch_ns[2] + 1)
            value = max(value, branch_ns[0])
        # BC: every block has an edge whose enclosure has ns < k
        for block in nx.biconnected_components(sub):
            K = frozenset(block)
            if len(K) == 2:
                continue          # the enclosure is a single vertex: ns 1 < 2
            outer = {}
            for z in K:
                outer[z] = self._reach(S, self.adj[z] & (S - K), frozenset([z]))
            best = None
            for x, y in combinations(sorted(K, key=repr), 2):
                enc = set(K) - {x}
                for z in K:
                    if z != x and z != y:
                        enc |= outer[z]
                e = self.ns(frozenset(enc))
                best = e if best is None else min(best, e)
                if best + 1 <= value:
                    break
            value = max(value, best + 1)
        self.memo[S] = value
        return value


def node_search_number(g: nx.Graph) -> int:
    """`ns(G)` of a block graph; `pathwidth = ns - 1`."""
    if g.number_of_nodes() == 0:
        return 0
    return BlockSearch(g).ns(frozenset(g.nodes))


def pathwidth_block_graph(g: nx.Graph) -> int:
    return node_search_number(g) - 1
