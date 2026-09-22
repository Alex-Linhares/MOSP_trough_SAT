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

Every feature is deterministic and permutation-invariant: renaming customers or
reordering products leaves all of them unchanged, which is what the optimum does
too. A feature that depended on the row order would be learnable noise.
"""

from __future__ import annotations

import numpy as np

from mosp.instance import MOSPInstance

__all__ = ["instance_features", "FEATURE_GROUPS", "feature_names"]


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


FEATURE_GROUPS = {
    "matrix": matrix_features,
    "graph": graph_features,
    "bounds": bound_features,
}


def instance_features(
    instance: MOSPInstance,
    groups: tuple[str, ...] = ("matrix", "graph", "bounds"),
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


def feature_names(groups: tuple[str, ...] = ("matrix", "graph", "bounds")) -> list[str]:
    """Feature names in the order `instance_features` produces them.

    Derived from a tiny instance rather than a hand-kept list, which would drift
    from the functions above the first time one of them gained a feature.
    """
    probe = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]], name="probe")
    return list(instance_features(probe, groups=groups).keys())
