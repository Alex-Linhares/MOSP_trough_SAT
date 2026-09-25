"""Instance features: what a model is allowed to see before the optimum.

Three groups, separated because they cost three different things and because a
study that mixes them cannot say which kind of knowledge carried the signal:

- **matrix** -- shape and the row/column degree distributions of M. Microseconds.
- **graph** -- the MOSP graph (customers as nodes, an edge iff some product is
  required by both; Yanasse 1997c). Milliseconds.
- **bounds** -- the lower bounds and heuristic upper bounds the solver already
  computes. Tens of milliseconds, and the honest baseline to beat: a model that
  cannot predict the optimum better than `ub_cs_dfs` already does has learned
  nothing the solver did not know.
- **invariants** -- graph invariants that pathwidth is known to sit beside
  (`reports/ml_nature_plan.md` §2.2): min-fill and min-degree treewidth upper
  bounds, reverse Cuthill--McKee bandwidth, spectral radius and Fiedler value,
  edge clique cover counts, a cheap balanced separator, and the random
  intersection graph parameters. Milliseconds. None of them is a bound on the
  optimum inside this repository; the ones that are bounds in theory
  (`bw_rcm + 1 >= optimum`, since bandwidth >= pathwidth) are reported as
  features and checked against the corpus in `learning.invariants_study`, and
  nothing here may reach `satisfiability.mosp_solver._lower_bound`.

Every feature is deterministic and permutation-invariant: renaming customers or
reordering products leaves all of them unchanged, which is what the optimum does
too. A feature that depended on the row order would be learnable noise. The
four greedy invariants (`tw_min_fill`, `tw_min_degree`, `bw_rcm`, `sep_size`)
are exact functions of the graph only up to the heuristic's tie-breaks; they
run on a copy relabelled by a label-free key so that ties are broken the same
way for every relabelling that the key separates, and the residual
order-dependence is measured on the corpus by
`python -m learning.invariants_study` rather than assumed away.
"""

from __future__ import annotations

import numpy as np

from mosp.instance import MOSPInstance

__all__ = ["instance_features", "FEATURE_GROUPS", "DEFAULT_GROUPS", "feature_names",
           "invariant_names"]


def _stats(values: np.ndarray, prefix: str) -> dict[str, float]:
    """min/max/mean/std of a degree distribution, under one prefix."""
    if values.size == 0:
        return {f"{prefix}_{k}": 0.0 for k in ("min", "max", "mean", "std")}
    return {
        f"{prefix}_min": float(values.min()),
        f"{prefix}_max": float(values.max()),
        f"{prefix}_mean": float(values.mean()),
        f"{prefix}_std": float(values.std()),
    }


def matrix_features(instance: MOSPInstance) -> dict[str, float]:
    """Shape and degree distributions of the binary matrix."""
    m = instance.matrix.astype(np.int64)
    n_c, n_p = instance.n_customers, instance.n_patterns
    rows = m.sum(axis=1)  # products per customer
    cols = m.sum(axis=0)  # customers per product

    # Duplicate columns are free to merge and duplicate rows are free to drop,
    # so the fraction of distinct ones says how much of the instance is real.
    distinct_cols = len({tuple(c) for c in m.T.tolist()}) if n_p else 0
    distinct_rows = len({tuple(r) for r in m.tolist()}) if n_c else 0

    feats = {
        "n_customers": float(n_c),
        "n_patterns": float(n_p),
        "n_ones": float(m.sum()),
        "density": float(m.sum() / (n_c * n_p)) if n_c and n_p else 0.0,
        "shape_ratio": float(n_c / n_p) if n_p else 0.0,
        "distinct_col_frac": float(distinct_cols / n_p) if n_p else 0.0,
        "distinct_row_frac": float(distinct_rows / n_c) if n_c else 0.0,
        "dominated_col_frac": _dominated_column_fraction(m),
    }
    feats.update(_stats(rows, "row"))
    feats.update(_stats(cols, "col"))
    # The largest column is the trivial lower bound of Yuen & Richardson (1995);
    # as a fraction of the customers it says how much of the instance one
    # product already forces open.
    feats["col_max_frac"] = float(cols.max() / n_c) if n_c and n_p else 0.0
    return feats


def _dominated_column_fraction(m: np.ndarray) -> float:
    """Fraction of products whose customer set sits inside another product's.

    These are exactly what `mosp.preprocess` drops and reinserts at no cost, so
    the fraction measures how much of the instance the preprocessor deletes.
    """
    n_p = m.shape[1]
    if n_p == 0:
        return 0.0
    masks = [int("".join(map(str, col)), 2) if col.size else 0 for col in m.T]
    dominated = 0
    for i, a in enumerate(masks):
        for j, b in enumerate(masks):
            if i != j and a & b == a and (a != b or j < i):
                dominated += 1
                break
    return float(dominated / n_p)


def graph_features(instance: MOSPInstance) -> dict[str, float]:
    """Structure of the MOSP graph, the object the pathwidth result is about."""
    import networkx as nx

    from customer_inter.customer_graph import build_customer_graph

    graph = build_customer_graph(instance)
    n = graph.number_of_nodes()
    degrees = np.array([d for _, d in graph.degree()], dtype=np.int64)
    components = list(nx.connected_components(graph))

    feats = {
        "g_nodes": float(n),
        "g_edges": float(graph.number_of_edges()),
        "g_density": float(nx.density(graph)) if n > 1 else 0.0,
        "g_components": float(len(components)),
        "g_largest_comp_frac": (float(max(map(len, components)) / n)
                                if components and n else 0.0),
        "g_clustering": float(nx.average_clustering(graph)) if n else 0.0,
        # Degeneracy is a cheap treewidth-flavoured statistic; contraction
        # degeneracy (below, in the bounds group) is its expensive cousin and a
        # genuine lower bound.
        "g_degeneracy": float(max(nx.core_number(graph).values())) if n else 0.0,
    }
    feats.update(_stats(degrees, "g_deg"))
    return feats


def bound_features(
    instance: MOSPInstance, clique_budget: float = 1.0
) -> dict[str, float]:
    """What the solver's own bounds say before any search runs.

    `lb_best` is exactly `satisfiability.mosp_solver._lower_bound`, so the
    residual `optimum - lb_best` is the quantity the search has to close. A
    model is interesting to the extent that it predicts that residual.
    """
    from satisfiability.heuristics import upper_bound
    from satisfiability.mosp_solver import _contraction_degeneracy, _lower_bound

    from customer_inter.customer_graph import build_customer_graph

    cols = instance.matrix.astype(np.int64).sum(axis=0)
    trivial = float(cols.max()) if instance.n_patterns else 0.0

    graph = build_customer_graph(instance)
    contraction = float(_contraction_degeneracy(graph) + 1) if instance.n_customers else 0.0
    best_lb = float(_lower_bound(instance, clique_budget=clique_budget))

    ub_mcn = float(upper_bound(instance, "mcn")[0])
    ub_dfs = float(upper_bound(instance, "cs-dfs")[0])
    best_ub = min(ub_mcn, ub_dfs)

    return {
        "lb_trivial": trivial,
        "lb_contraction": contraction,
        "lb_best": best_lb,
        "ub_mcn": ub_mcn,
        "ub_cs_dfs": ub_dfs,
        "ub_best": best_ub,
        "bound_gap": best_ub - best_lb,
        "bound_gap_frac": (best_ub - best_lb) / best_ub if best_ub else 0.0,
    }


def _canonical_copy(graph):
    """The graph relabelled 0..n-1 by a label-free key, adjacency sorted.

    The key is (degree, sorted neighbour degrees, sorted 2-hop degree sums),
    which is the first two rounds of colour refinement. Every heuristic below
    iterates nodes and neighbours in this order, so two relabellings of one
    graph produce the same answer whenever the key separates the nodes that
    the heuristic would otherwise have had to break ties between.
    """
    import networkx as nx

    deg = dict(graph.degree())
    key = {}
    for v in graph.nodes():
        nbr_degs = tuple(sorted(deg[u] for u in graph[v]))
        two_hop = tuple(sorted(sum(deg[w] for w in graph[u]) for u in graph[v]))
        key[v] = (deg[v], nbr_degs, two_hop)
    order = sorted(graph.nodes(), key=lambda v: key[v])
    rank = {v: k for k, v in enumerate(order)}
    copy = nx.Graph()
    copy.add_nodes_from(range(len(order)))
    copy.add_edges_from(sorted((min(rank[u], rank[v]), max(rank[u], rank[v]))
                               for u, v in graph.edges()))
    return copy


def _bandwidth(graph, order) -> int:
    pos = {v: k for k, v in enumerate(order)}
    return max((abs(pos[u] - pos[v]) for u, v in graph.edges()), default=0)


def _sweep_separator(graph, order) -> int:
    """Smallest one-sided boundary over the balanced cuts of a linear order.

    Cutting the order after `s` nodes, with n/3 <= s <= 2n/3, leaves a left
    part L and a right part R. The left nodes with a neighbour in R separate
    L minus S from R, and both pieces have at most 2n/3 nodes; symmetrically for
    the right boundary. The minimum over cuts and sides is a balanced vertex
    separator, an upper bound on the smallest one, and no bound on anything
    else.
    """
    n = len(order)
    if n < 3:
        return 0
    pos = {v: k for k, v in enumerate(order)}
    lo, hi = -(-n // 3), (2 * n) // 3
    best = n
    for s in range(lo, hi + 1):
        left_boundary = {u for u, v in graph.edges()
                         if (pos[u] < s) != (pos[v] < s) for u in (u, v) if pos[u] < s}
        right_boundary = {u for u, v in graph.edges()
                          if (pos[u] < s) != (pos[v] < s) for u in (u, v) if pos[u] >= s}
        best = min(best, len(left_boundary), len(right_boundary))
    return best


def _clique_cover_counts(m: np.ndarray) -> tuple[int, int]:
    """(distinct products with >= 2 customers, greedy-reduced count).

    The MOSP graph is the union of one clique per product, so the distinct
    products that contain an edge are an edge clique cover, and the edge
    clique cover number is at most their count. The greedy pass drops, from
    the smallest product upwards, any product every edge of which is also
    covered by another remaining product. Both are upper bounds on the edge
    clique cover number; the second is never larger than the first.
    """
    cols = {tuple(np.flatnonzero(c)) for c in m.T if c.sum() >= 2}
    if not cols:
        return 0, 0
    cover: dict[tuple[int, int], int] = {}
    for col in cols:
        for a in range(len(col)):
            for b in range(a + 1, len(col)):
                cover[(col[a], col[b])] = cover.get((col[a], col[b]), 0) + 1
    kept = len(cols)
    for col in sorted(cols, key=lambda c: (len(c), c)):
        pairs = [(col[a], col[b]) for a in range(len(col)) for b in range(a + 1, len(col))]
        if all(cover[e] >= 2 for e in pairs):
            for e in pairs:
                cover[e] -= 1
            kept -= 1
    return len(cols), kept


def invariant_features(instance: MOSPInstance) -> dict[str, float]:
    """Pathwidth-adjacent invariants of the MOSP graph (plan §2.2a)."""
    import networkx as nx
    from networkx.algorithms.approximation import treewidth_min_degree, treewidth_min_fill_in

    from customer_inter.customer_graph import build_customer_graph

    m = instance.matrix.astype(np.int64)
    n_c, n_p = instance.n_customers, instance.n_patterns
    graph = _canonical_copy(build_customer_graph(instance))
    n = graph.number_of_nodes()

    if n == 0:
        zero = {k: 0.0 for k in ("tw_min_fill", "tw_min_degree", "bw_rcm", "spectral_radius",
                                 "fiedler", "fiedler_lcc", "cc_products", "cc_greedy",
                                 "sep_size", "sep_frac", "rig_edge_prob", "rig_deg_expected",
                                 "rig_density_ratio")}
        return zero

    tw_fill = treewidth_min_fill_in(graph)[0] if graph.number_of_edges() else 0
    tw_deg = treewidth_min_degree(graph)[0] if graph.number_of_edges() else 0

    rcm_order = list(nx.utils.reverse_cuthill_mckee_ordering(graph))
    bw_rcm = _bandwidth(graph, rcm_order)

    adjacency = nx.to_numpy_array(graph, nodelist=range(n))
    spectral_radius = float(np.linalg.eigvalsh(adjacency)[-1]) if n > 1 else 0.0
    laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
    lap_eigs, lap_vecs = np.linalg.eigh(laplacian)
    fiedler = float(max(lap_eigs[1], 0.0)) if n > 1 else 0.0

    components = sorted(nx.connected_components(graph), key=len, reverse=True)
    largest = graph.subgraph(components[0])
    if largest.number_of_nodes() > 1:
        sub = nx.to_numpy_array(largest, nodelist=sorted(largest.nodes()))
        sub_l = np.diag(sub.sum(axis=1)) - sub
        fiedler_lcc = float(max(np.linalg.eigvalsh(sub_l)[1], 0.0))
    else:
        fiedler_lcc = 0.0

    # Balanced separator: sweep the Fiedler order and the RCM order, keep the
    # smaller. The Fiedler vector of a disconnected graph is still an order.
    fiedler_order = sorted(range(n), key=lambda v: (lap_vecs[v, 1], v))
    sep_size = min(_sweep_separator(graph, fiedler_order),
                   _sweep_separator(graph, rcm_order))

    cc_products, cc_greedy = _clique_cover_counts(m)

    # Random intersection graph G(n, m, p): two customers share a product with
    # probability 1 - (1 - p^2)^m. The ratio of the observed MOSP-graph density
    # to that is how far the instance is from a random one with its own
    # (n, m, p_hat); p_hat itself is `density` in the matrix group, and n, m
    # are `n_customers`, `n_patterns`.
    p_hat = float(m.sum() / (n_c * n_p)) if n_c and n_p else 0.0
    rig_edge_prob = 1.0 - (1.0 - p_hat ** 2) ** n_p
    g_density = float(nx.density(graph)) if n > 1 else 0.0

    return {
        "tw_min_fill": float(tw_fill),
        "tw_min_degree": float(tw_deg),
        "bw_rcm": float(bw_rcm),
        "spectral_radius": spectral_radius,
        "fiedler": fiedler,
        "fiedler_lcc": fiedler_lcc,
        "cc_products": float(cc_products),
        "cc_greedy": float(cc_greedy),
        "sep_size": float(sep_size),
        "sep_frac": float(sep_size / n),
        "rig_edge_prob": float(rig_edge_prob),
        "rig_deg_expected": float((n_c - 1) * rig_edge_prob),
        "rig_density_ratio": float(g_density / rig_edge_prob) if rig_edge_prob > 0 else 0.0,
    }


FEATURE_GROUPS = {
    "matrix": matrix_features,
    "graph": graph_features,
    "bounds": bound_features,
    "invariants": invariant_features,
}

DEFAULT_GROUPS = ("matrix", "graph", "bounds", "invariants")


def instance_features(
    instance: MOSPInstance,
    groups: tuple[str, ...] = DEFAULT_GROUPS,
    clique_budget: float = 1.0,
) -> dict[str, float]:
    """All features of the requested groups, as one flat dict."""
    feats: dict[str, float] = {}
    for name in groups:
        fn = FEATURE_GROUPS[name]
        if name == "bounds":
            feats.update(fn(instance, clique_budget=clique_budget))
        else:
            feats.update(fn(instance))
    return feats


def feature_names(groups: tuple[str, ...] = DEFAULT_GROUPS) -> list[str]:
    """Feature names in the order `instance_features` produces them.

    Derived from a tiny instance rather than a hand-kept list, which would drift
    from the functions above the first time one of them gained a feature.
    """
    probe = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]], name="probe")
    return list(instance_features(probe, groups=groups).keys())


def invariant_names() -> list[str]:
    """The names of the `invariants` group, for studies that want the older
    36-feature table back (`learning.study_optimum`, `learning.fingerprint`)."""
    return feature_names(groups=("invariants",))
