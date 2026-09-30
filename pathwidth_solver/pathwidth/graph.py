"""Graph adapter: the bitmask view of a graph that the search runs on.

The customer search of Chu & Stuckey (2009) never looks at products; it reads
only the self-inclusive neighbourhood masks `N[v]` of the customer graph and the
budget `k` (their §2: "the products are essentially irrelevant"). This module
supplies those masks for an arbitrary `networkx.Graph`, and the measure the
search optimises, stated in graph terms.

**Convention.** An *order* is a sequence of vertices, read as the order in which
they are closed (Chu & Stuckey) or, equivalently, placed. For a prefix `U` of
the order, its *boundary* is `d(U) = |N(U) \\ U|`, the vertices outside `U`
adjacent to `U`. The vertex separation of the order is `max_U d(U)` over all
prefixes. The minimum over all orders is `vs(G) = pw(G)` (Kinnersley 1992).

This is the standard vertex separation of the *reversed* layout: for a layout
`L`, the textbook `vs_L(i)` counts vertices of `L[..i]` with a neighbour in
`L[i+1..]`, i.e. `|N(L[i+1..]) ∩ L[..i]|`, which is the boundary of the suffix.
Reversing `L` turns suffixes into prefixes, so both definitions have the same
minimum and `layout_from_order` is `reversed`.

The search's own cost of closing `v` after `U` is `|N[U ∪ {v}] \\ U|` =
`d(U ∪ {v}) + 1` -- the boundary plus the vertex being closed. Hence
"customer search decides MOSP ≤ k" reads "pathwidth ≤ k − 1" on a graph.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence

import networkx as nx

# Fan orders among equal-cost candidates. "index" is what every recorded node
# count was made with; "degree" puts the candidate with the most neighbours not
# yet closed first. (Copied from MOSP `satisfiability/heuristics.py`.)
FAN_ORDERS = ("index", "degree")


def masks_from_graph(G: nx.Graph) -> tuple[list[int], list[Hashable]]:
    """Self-inclusive neighbourhood bitmasks of `G`, and the vertex labels.

    Vertices are relabelled `0..n-1` in `G.nodes` order; `labels[i]` is the
    original label of vertex `i`. Self-loops are ignored (the mask is
    self-inclusive anyway) and multigraphs are rejected: the search reads only
    adjacency, so parallel edges would be silently collapsed.
    """
    if G.is_multigraph():
        raise TypeError("masks_from_graph: multigraphs are not supported")
    if G.is_directed():
        raise TypeError("masks_from_graph: directed graphs are not supported")
    labels = list(G.nodes)
    index = {v: i for i, v in enumerate(labels)}
    masks = [0] * len(labels)
    for i, v in enumerate(labels):
        mask = 1 << i
        for u in G.adj[v]:
            mask |= 1 << index[u]
        masks[i] = mask
    return masks, labels


def masks_from_adjacency(adjacency: Sequence[Iterable[int]]) -> list[int]:
    """Masks from adjacency lists over vertices `0..n-1` (self-inclusive)."""
    masks = []
    for v, nbrs in enumerate(adjacency):
        mask = 1 << v
        for u in nbrs:
            mask |= 1 << u
        masks.append(mask)
    return masks


def boundary_sequence(masks: Sequence[int], order: Sequence[int]) -> list[int]:
    """`d(U_i)` for each prefix `U_i` of `order`, `d(U) = |N(U) \\ U|`."""
    opened = closed = 0
    out = []
    for v in order:
        opened |= masks[v]
        closed |= 1 << v
        out.append((opened & ~closed).bit_count())
    return out


def vertex_separation_masks(masks: Sequence[int], order: Sequence[int]) -> int:
    """Vertex separation of `order` under the prefix-boundary convention."""
    opened = closed = peak = 0
    for v in order:
        opened |= masks[v]
        closed |= 1 << v
        width = (opened & ~closed).bit_count()
        if width > peak:
            peak = width
    return peak


def search_cost(masks: Sequence[int], order: Sequence[int]) -> int:
    """Chu & Stuckey's cost of a closing order, `max_i |N[U_i] \\ U_{i-1}|`.

    Equals `vertex_separation_masks(masks, order) + 1` on every order (the
    vertex being closed is still open at the moment it closes). Kept so the
    identity with the MOSP implementation's `_cs_cost` can be asserted.
    """
    opened = closed = peak = 0
    for v in order:
        opened |= masks[v]
        width = (opened & ~closed).bit_count()
        if width > peak:
            peak = width
        closed |= 1 << v
    return peak


def vertex_separation(G: nx.Graph, order: Sequence[Hashable]) -> int:
    """Vertex separation of a vertex order of `G` (labels, not indices).

    `order` must be a permutation of `G.nodes`; a partial order is accepted and
    measured on its prefixes only.
    """
    masks, labels = masks_from_graph(G)
    index = {v: i for i, v in enumerate(labels)}
    return vertex_separation_masks(masks, [index[v] for v in order])


def layout_from_order(order: Sequence[Hashable]) -> list[Hashable]:
    """The textbook vertex-separation layout equivalent to a closing order."""
    return list(reversed(order))


def path_decomposition(G: nx.Graph, order: Sequence[Hashable]) -> list[set[Hashable]]:
    """Bags `X_i = {v_i} ∪ (N(U_i) \\ U_i)`, one per prefix `U_i` of `order`.

    Bag `i` holds the vertex closed at step `i` together with the boundary after
    closing it. Every edge `uv` appears in the bag of whichever endpoint closes
    first (the other is then in the boundary), and each vertex occupies a
    contiguous run of bags (from its first appearance in a boundary until it
    closes), so this is a path decomposition of width
    `vertex_separation(G, order)`.
    """
    masks, labels = masks_from_graph(G)
    index = {v: i for i, v in enumerate(labels)}
    opened = closed = 0
    bags = []
    for v in order:
        i = index[v]
        opened |= masks[i]
        closed |= 1 << i
        boundary = opened & ~closed
        bag = {v}
        bits = boundary
        while bits:
            bit = bits & -bits
            bits ^= bit
            bag.add(labels[bit.bit_length() - 1])
        bags.append(bag)
    return bags


def fan_sort_key(fan_order: str, masks: Sequence[int], remaining: int):
    """Sort key over `(cost, vertex, ...)` tuples for a named fan order.

    `"index"`: cheapest first, ties by vertex index -- the tuple's own order.
    `"degree"`: cheapest first, ties to the vertex with the most neighbours not
    yet closed (`|N[v] ∩ remaining| − 1`), then index.
    """
    if fan_order == "index":
        return lambda item: item[:2]
    if fan_order == "degree":
        return lambda item: (item[0], -((masks[item[1]] & remaining).bit_count() - 1), item[1])
    raise ValueError(f"fan_order must be one of {FAN_ORDERS}, not {fan_order!r}")
