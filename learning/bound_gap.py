"""Where do the proved lower bounds fail, and what do those instances look like? (plan §2.3)

`lb_best` is `satisfiability.mosp_solver._lower_bound` as the feature table
computes it: the best of the trivial bound, the clique bound, contraction
degeneracy + 1 and the expansion bound. It equals the optimum on 77% of the
corpus, misses by one on 18% and by two or more on 5%. This study asks
whether the instances it misses by two or more share a recognisable
structure, in five parts:

1. **Where the gap is.** Tight / gap 1 / gap >= 2 counts by size band and by
   collection, and how far each *component* bound falls short on the gap
   instances, so the table says which bound is blind rather than "the bound".
2. **A classifier for `gap >= 2` against tight** (gap-1 rows are left out of
   the label, as the plan asks). A depth-3 decision tree, an explainable
   boosting machine (`interpret`, soft import) and a gradient-boosting
   ceiling, on four feature sets, under the file ∪ isomorphism-class grouping
   of `learning.fingerprint.union_groups` with the file-only grouping beside
   it. The plan's baseline is density and size, and the kill criterion is
   that structure must beat it. Because gap >= 2 never occurs below 11
   customers and is the norm above 60, the same models are also scored per
   size band and on the subset of `(n, m)` cells that hold both classes,
   where size cannot be the answer.
3. **Which invariant the bound is blind to.** Every size-free feature is
   z-scored within its `(n, m)` cell and used alone to rank gap >= 2 against
   tight within the mixed cells. The AUC of one feature is a statement about
   what the gap instances look like at fixed size.
4. **Clusters of the gap instances**, k-means over the standardised size-free
   features with k chosen by silhouette, each cluster described by its size
   range, collections, gap and its most extreme features.
5. **The ten smallest gap >= 2 instances**, one per MOSP-graph isomorphism
   class, drawn as matrices with their degree sequences and every bound
   recomputed from the instance, and -- since the finding rests on them --
   re-certified: `solve_mosp_exact` with the solutions directory (a cached
   value is re-verified by simulation) and an independent refutation of
   `optimum - 1` through `learning.node_counts.refute`, which writes nothing.
6. **The treewidth ceiling.** The trivial bound (a clique), the clique bound
   and contraction degeneracy + 1 are all lower bounds on *treewidth* + 1,
   and `tw_min_fill + 1` is an upper bound on it, so `optimum > tw_min_fill + 1`
   certifies `pathwidth > treewidth` on that instance -- a gap no treewidth
   bound can close. The table counts those certificates per gap class and
   checks the two inequalities the theory requires (`lb_trivial` and
   `lb_contraction` never above `tw_min_fill + 1`), which is a consistency
   check on the feature code. The expansion bound is a pathwidth argument and
   is the one component allowed above the ceiling.

The classification frame carries the label (`y`, `gap`, `gap_class`); the
feature sets are built from the feature-group names, never from "every numeric
column", and `feature_sets` refuses a set containing a label or an upper bound
(iteration 6's run leaked `y` into the structure set and scored 1.000 everywhere).

Nothing here is a bound; nothing reaches `_lower_bound` or any decision path;
nothing is written to `solutions/`.

Usage:
    python -m learning.dataset                                     # the table (~90 s on 16 cores)
    python -m learning.canonical                                   # the isomorphism classes (~1 s)
    python -m learning.bound_gap --workers 16 --out reports/bound_gap_tables.md
    python -m learning.bound_gap --no-recertify                    # skip the exact re-solve of the ten
"""

from __future__ import annotations

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_INSTANCE_DIR, DEFAULT_OUT, enumerate_instances
from learning.features import feature_names, invariant_names
from learning.fingerprint import (
    CANONICAL_CSV,
    load_table,
    size_free_features,
    union_groups,
)
from mosp.instance import MOSPInstance

SIZE_BANDS = ((1, 10), (11, 20), (21, 30), (31, 60), (61, 200))
GAP_THRESHOLD = 2
MIN_PER_CLASS_IN_CELL = 3
LOWER_BOUND_COLUMNS = ["lb_trivial", "lb_contraction", "lb_best"]
LABEL_COLUMNS = ("y", "gap", "gap_class", "optimum")
LEAK_PREFIXES = ("ub_", "bound_")
TEN = 10
TW_RESTARTS = 200


# ----------------------------------------------------------------------------
# labels and feature sets
# ----------------------------------------------------------------------------


def with_gap(frame: pd.DataFrame) -> pd.DataFrame:
    """The table with `gap = optimum - lb_best` and the three-way label."""
    out = frame.copy()
    out["gap"] = (out["optimum"] - out["lb_best"]).astype(int)
    if (out["gap"] < 0).any():
        bad = out.loc[out["gap"] < 0, "instance_name"].tolist()
        raise ValueError(f"lb_best above the optimum on {bad[:5]}: a bound violation, stop")
    out["gap_class"] = np.select(
        [out["gap"] == 0, out["gap"] < GAP_THRESHOLD], ["tight", "gap 1"], f"gap >= {GAP_THRESHOLD}"
    )
    return out


def classification_rows(frame: pd.DataFrame) -> pd.DataFrame:
    """Tight and gap >= 2 rows only, with the binary label `y`, plus the
    size-free columns of `size_free_table` that the table does not already
    hold (ratios such as `g_deg_cv`), so a tree can split on a ratio."""
    keep = frame["gap_class"] != "gap 1"
    out = frame[keep].reset_index(drop=True)
    out["y"] = (out["gap"] >= GAP_THRESHOLD).astype(int)
    if all(c in out.columns for c in ("row_mean", "col_mean", "g_deg_mean", "g_deg_std")):
        free = size_free_table(out)
        for column in free.columns:
            if column not in out.columns:
                out[column] = free[column]
    return out


def size_free_columns(frame: pd.DataFrame) -> list[str]:
    """The size-free column names present in `frame` (after `classification_rows`)."""
    wanted = list(size_free_features(frame.head(2)).columns) + list(_SIZE_FREE_EXTRA)
    return [c for c in wanted if c in frame.columns]


def feature_sets(frame: pd.DataFrame) -> dict[str, list[str]]:
    """The five sets the classifier is scored on, built from the feature-group
    names rather than from every numeric column, so the label columns the
    study adds can never slip in. No upper bound anywhere: `ub_best` equals
    the optimum on 85% of the corpus, so `ub - lb` would be the label in
    disguise. Raises if a set holds a label or an upper bound."""
    structure = [c for c in feature_names(groups=("matrix", "graph")) if c in frame.columns]
    inv = [c for c in invariant_names() if c in frame.columns]
    lbs = [c for c in LOWER_BOUND_COLUMNS if c in frame.columns]
    free = size_free_columns(frame)
    sets = {
        "density + size": ["n_customers", "n_patterns", "density"],
        f"structure ({len(structure)})": structure,
        f"structure + invariants ({len(structure) + len(inv)})": structure + inv,
        f"size-free ({len(free)})": free,
        "structure + invariants + lower bounds": structure + inv + lbs,
    }
    for name, columns in sets.items():
        leaked = [c for c in columns if c in LABEL_COLUMNS or c.startswith(LEAK_PREFIXES)]
        if leaked:
            raise ValueError(f"feature set {name!r} would leak the label through {leaked}")
    return sets


def groupings(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    """File ∪ class first (the honest split), file alone beside it."""
    out: dict[str, np.ndarray] = {}
    if "graph_cert" in frame.columns and frame["graph_cert"].notna().any():
        out["file ∪ class"] = union_groups(frame["source_file"], frame["graph_cert"])
    out["file"] = frame["source_file"].to_numpy()
    return out


# ----------------------------------------------------------------------------
# 1. where the gap is
# ----------------------------------------------------------------------------


def gap_by_band(frame: pd.DataFrame) -> pd.DataFrame:
    n = frame["n_customers"].to_numpy()
    rows = []
    for lo, hi in SIZE_BANDS:
        mask = (n >= lo) & (n <= hi)
        if not mask.any():
            continue
        sub = frame[mask]
        rows.append({
            "band": f"{lo}-{hi}", "instances": int(mask.sum()),
            "tight": int((sub["gap"] == 0).sum()),
            "gap 1": int((sub["gap"] == 1).sum()),
            f"gap >= {GAP_THRESHOLD}": int((sub["gap"] >= GAP_THRESHOLD).sum()),
            f"frac gap >= {GAP_THRESHOLD}": float((sub["gap"] >= GAP_THRESHOLD).mean()),
            "mean gap": float(sub["gap"].mean()), "max gap": int(sub["gap"].max()),
        })
    return pd.DataFrame(rows)


def gap_by_collection(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for coll, sub in frame.groupby("collection"):
        rows.append({
            "collection": coll, "instances": len(sub),
            "n range": f"{int(sub['n_customers'].min())}-{int(sub['n_customers'].max())}",
            "tight": int((sub["gap"] == 0).sum()),
            "gap 1": int((sub["gap"] == 1).sum()),
            f"gap >= {GAP_THRESHOLD}": int((sub["gap"] >= GAP_THRESHOLD).sum()),
            f"frac gap >= {GAP_THRESHOLD}": float((sub["gap"] >= GAP_THRESHOLD).mean()),
            "mean gap": float(sub["gap"].mean()), "max gap": int(sub["gap"].max()),
        })
    return pd.DataFrame(rows).sort_values(f"frac gap >= {GAP_THRESHOLD}", ascending=False)


def component_shortfall(frame: pd.DataFrame) -> pd.DataFrame:
    """How far each component bound sits below the optimum, on the tight rows,
    the gap-1 rows and the gap >= 2 rows. `lb_best` includes the expansion
    bound; `lb_contraction` is contraction degeneracy + 1, which Yanasse et
    al. (1999) show is the arc contraction bound; `lb_trivial` is the largest
    product."""
    rows = []
    for label, sub in frame.groupby("gap_class"):
        for column in LOWER_BOUND_COLUMNS:
            short = (sub["optimum"] - sub[column]).to_numpy(dtype=float)
            rows.append({"rows": label, "instances": len(sub), "bound": column,
                         "mean shortfall": float(short.mean()),
                         "median shortfall": float(np.median(short)),
                         "max shortfall": int(short.max()),
                         "tight frac": float((short == 0).mean())})
    order = {"tight": 0, "gap 1": 1, f"gap >= {GAP_THRESHOLD}": 2}
    return pd.DataFrame(rows).sort_values(["rows", "bound"], key=lambda s: s.map(order) if s.name == "rows" else s)


# ----------------------------------------------------------------------------
# 2. the classifier
# ----------------------------------------------------------------------------


def _models(seed: int, with_ebm: bool = True, n_jobs: int = 4) -> dict[str, object]:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.tree import DecisionTreeClassifier

    models: dict[str, object] = {
        "tree (depth 3)": DecisionTreeClassifier(
            max_depth=3, min_samples_leaf=20, class_weight="balanced", random_state=seed),
    }
    if with_ebm:
        try:
            from interpret.glassbox import ExplainableBoostingClassifier

            models["EBM"] = ExplainableBoostingClassifier(
                random_state=seed, interactions=0, outer_bags=4, n_jobs=n_jobs)
        except ImportError:  # pragma: no cover - optional dependency
            pass
    models["boosting (ceiling)"] = HistGradientBoostingClassifier(
        random_state=seed, max_iter=300, class_weight="balanced")
    return models


def _grouped_proba(model, X: pd.DataFrame, y: np.ndarray, groups: np.ndarray, folds: int) -> np.ndarray:
    """Out-of-fold P(gap >= 2) under GroupKFold, robust to a training fold
    that happens to hold one class only (then that fold predicts its class)."""
    from sklearn.base import clone
    from sklearn.model_selection import GroupKFold

    proba = np.full(len(y), np.nan)
    folds = min(folds, len(np.unique(groups)))
    for train, test in GroupKFold(n_splits=folds).split(X, y, groups):
        if len(np.unique(y[train])) < 2:
            proba[test] = float(y[train][0])
            continue
        fitted = clone(model).fit(X.iloc[train], y[train])
        proba[test] = fitted.predict_proba(X.iloc[test])[:, 1]
    return proba


def _classification_scores(y: np.ndarray, proba: np.ndarray) -> dict[str, float]:
    from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score

    if len(np.unique(y)) < 2:
        return {"auc": np.nan, "avg precision": np.nan, "balanced acc": np.nan}
    return {
        "auc": float(roc_auc_score(y, proba)),
        "avg precision": float(average_precision_score(y, proba)),
        "balanced acc": float(balanced_accuracy_score(y, proba >= 0.5)),
    }


def classify(rows: pd.DataFrame, folds: int = 5, seed: int = 0, with_ebm: bool = True,
             sets: dict[str, list[str]] | None = None,
             splits: dict[str, np.ndarray] | None = None, n_jobs: int = 4) -> tuple[pd.DataFrame, dict]:
    """Every model on every feature set under every grouping; returns the
    score table and the out-of-fold probabilities keyed by
    (split, model, features) for the per-band and per-cell tables."""
    if "y" not in rows.columns:
        raise ValueError("classify wants the rows of classification_rows(), with a `y` column")
    sets = sets or feature_sets(rows)
    splits = splits or groupings(rows)
    y = rows["y"].to_numpy()
    n = rows["n_customers"].to_numpy()
    table, probas = [], {}
    for sname, groups in splits.items():
        for mname, model in _models(seed, with_ebm, n_jobs).items():
            for fname, columns in sets.items():
                proba = _grouped_proba(model, rows[columns], y, groups, folds)
                probas[(sname, mname, fname)] = proba
                row = {"split": sname, "model": mname, "features": fname,
                       "positives": int(y.sum()), "rows": len(y),
                       **_classification_scores(y, proba)}
                for lo, hi in SIZE_BANDS:
                    mask = (n >= lo) & (n <= hi)
                    if mask.sum() and len(np.unique(y[mask])) == 2:
                        row[f"auc {lo}-{hi}"] = _classification_scores(y[mask], proba[mask])["auc"]
                table.append(row)
    return pd.DataFrame(table), probas


def mixed_cells(rows: pd.DataFrame, min_per_class: int = MIN_PER_CLASS_IN_CELL) -> pd.Series:
    """Mask of the rows in (n, m) cells holding at least `min_per_class` of
    each class: where size alone cannot separate them."""
    counts = rows.groupby(["n_customers", "n_patterns"])["y"].agg(["sum", "count"])
    ok = counts[(counts["sum"] >= min_per_class) & (counts["count"] - counts["sum"] >= min_per_class)]
    keys = set(ok.index.tolist())
    return pd.Series([(a, b) in keys for a, b in zip(rows["n_customers"], rows["n_patterns"])],
                     index=rows.index)


def tree_text(rows: pd.DataFrame, columns: list[str], seed: int = 0, depth: int = 3) -> str:
    """The depth-3 tree fitted on all rows, as readable rules."""
    from sklearn.tree import DecisionTreeClassifier, export_text

    tree = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=20,
                                  class_weight="balanced", random_state=seed)
    tree.fit(rows[columns], rows["y"])
    return export_text(tree, feature_names=list(columns), max_depth=depth, decimals=3,
                       class_names=["tight", f"gap>={GAP_THRESHOLD}"])


def ebm_terms(rows: pd.DataFrame, columns: list[str], seed: int = 0, top: int = 12,
              n_jobs: int = 4) -> pd.DataFrame | None:
    """The EBM's global term importances on all rows, or None without `interpret`."""
    try:
        from interpret.glassbox import ExplainableBoostingClassifier
    except ImportError:  # pragma: no cover - optional dependency
        return None
    ebm = ExplainableBoostingClassifier(random_state=seed, interactions=0, outer_bags=4, n_jobs=n_jobs)
    ebm.fit(rows[columns], rows["y"])
    imp = pd.DataFrame({"term": ebm.term_names_, "importance": ebm.term_importances()})
    return imp.sort_values("importance", ascending=False).head(top).reset_index(drop=True)


# ----------------------------------------------------------------------------
# 3. which invariant the bound is blind to
# ----------------------------------------------------------------------------


_SIZE_FREE_EXTRA = (
    "tw_min_fill_frac", "tw_min_degree_frac", "bw_rcm_frac", "spectral_radius_frac",
    "fiedler", "fiedler_lcc", "cc_products_frac", "cc_greedy_frac", "sep_frac",
    "rig_edge_prob", "rig_density_ratio", "row_mean_frac", "col_mean_frac",
)


def size_free_table(frame: pd.DataFrame) -> pd.DataFrame:
    """`learning.fingerprint.size_free_features` plus the invariants with
    their size divided out, so a feature means the same thing across cells."""
    out = size_free_features(frame)
    n = frame["n_customers"].astype(float).clip(lower=1)
    m = frame["n_patterns"].astype(float).clip(lower=1)
    extra = {
        "tw_min_fill_frac": frame["tw_min_fill"] / n,
        "tw_min_degree_frac": frame["tw_min_degree"] / n,
        "bw_rcm_frac": frame["bw_rcm"] / n,
        "spectral_radius_frac": frame["spectral_radius"] / (n - 1).clip(lower=1),
        "fiedler": frame["fiedler"],
        "fiedler_lcc": frame["fiedler_lcc"],
        "cc_products_frac": frame["cc_products"] / m,
        "cc_greedy_frac": frame["cc_greedy"] / m,
        "sep_frac": frame["sep_frac"],
        "rig_edge_prob": frame["rig_edge_prob"],
        "rig_density_ratio": frame["rig_density_ratio"],
        "row_mean_frac": frame["row_mean"] / m,
        "col_mean_frac": frame["col_mean"] / n,
    }
    for name in _SIZE_FREE_EXTRA:
        values = extra[name]
        if name not in out.columns and values.notna().all():
            out[name] = values.astype(float)
    return out


def within_cell_contrast(rows: pd.DataFrame, min_per_class: int = MIN_PER_CLASS_IN_CELL) -> pd.DataFrame:
    """Each size-free feature alone as a ranker of gap >= 2 against tight,
    after z-scoring within its (n, m) cell, over the mixed cells.

    `auc` above 0.5 means the gap instances have *more* of the feature than
    tight instances of the same size; `d` is the pooled standardised mean
    difference (gap minus tight), Cohen's d.
    """
    from sklearn.metrics import roc_auc_score

    mask = mixed_cells(rows, min_per_class).to_numpy()
    sub = rows[mask].reset_index(drop=True)
    feats = size_free_table(sub)
    key = pd.Series([f"{int(a)}x{int(b)}" for a, b in zip(sub["n_customers"], sub["n_patterns"])],
                    index=sub.index)
    z = feats.groupby(key).transform(lambda s: (s - s.mean()) / (s.std(ddof=0) or 1.0))
    y = sub["y"].to_numpy()
    out = []
    for column in feats.columns:
        values = z[column].to_numpy(dtype=float)
        if not np.isfinite(values).all() or np.allclose(values, values[0]):
            continue
        d = values[y == 1].mean() - values[y == 0].mean()
        out.append({"feature": column, "auc": float(roc_auc_score(y, values)), "d": float(d),
                    "cells": int(len(set(key))), "rows": int(len(sub)), "positives": int(y.sum())})
    table = pd.DataFrame(out)
    table["separation"] = (table["auc"] - 0.5).abs()
    return table.sort_values("separation", ascending=False).drop(columns="separation").reset_index(drop=True)


# ----------------------------------------------------------------------------
# 3b. the treewidth ceiling
# ----------------------------------------------------------------------------


def treewidth_ceiling(frame: pd.DataFrame) -> pd.DataFrame:
    """Per gap class: how many instances have `optimum > tw_min_fill + 1`,
    which certifies `pathwidth > treewidth` (min-fill is an upper bound on
    treewidth, the optimum is pathwidth + 1), how many have `lb_best` above
    the same ceiling (only the expansion bound can), and the two violation
    counts that must be zero because the trivial bound and contraction
    degeneracy + 1 are lower bounds on treewidth + 1."""
    ceiling = frame["tw_min_fill"] + 1
    rows = []
    order = {"tight": 0, "gap 1": 1, f"gap >= {GAP_THRESHOLD}": 2}
    for label, sub in sorted(frame.groupby("gap_class"), key=lambda kv: order[kv[0]]):
        c = ceiling[sub.index]
        above = sub["optimum"] > c
        rows.append({
            "rows": label, "instances": len(sub),
            "pw > tw certified": int(above.sum()),
            "frac": float(above.mean()),
            "mean optimum − (tw_min_fill + 1)": float((sub["optimum"] - c).mean()),
            "lb_best above ceiling": int((sub["lb_best"] > c).sum()),
            "lb_trivial above ceiling (must be 0)": int((sub["lb_trivial"] > c).sum()),
            "lb_contraction above ceiling (must be 0)": int((sub["lb_contraction"] > c).sum()),
        })
    table = pd.DataFrame(rows)
    if (table["lb_trivial above ceiling (must be 0)"].sum()
            or table["lb_contraction above ceiling (must be 0)"].sum()):
        raise ValueError("a treewidth lower bound exceeds the min-fill width: the feature code is wrong")
    return table


# ----------------------------------------------------------------------------
# 4. clusters of the gap instances
# ----------------------------------------------------------------------------


def cluster_gap_instances(frame: pd.DataFrame, k_range=range(2, 7), seed: int = 0,
                          top_features: int = 5) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """k-means over the standardised size-free features of the gap >= 2
    instances, k by silhouette. Returns the per-cluster description, the
    labelled rows and the chosen k; the description table carries the
    silhouette of every k tried in its `attrs["silhouette"]`."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    gap = frame[frame["gap"] >= GAP_THRESHOLD].reset_index(drop=True)
    feats = size_free_table(gap)
    feats = feats.loc[:, feats.std(ddof=0) > 0]
    X = StandardScaler().fit_transform(feats)
    best_k, best_score, best_labels = None, -1.0, None
    silhouettes: dict[int, float] = {}
    for k in k_range:
        if k >= len(gap):
            break
        labels = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(X)
        score = silhouette_score(X, labels)
        silhouettes[k] = float(score)
        if score > best_score:
            best_k, best_score, best_labels = k, score, labels
    gap = gap.assign(cluster=best_labels)
    z = pd.DataFrame(X, columns=feats.columns)
    rows = []
    for c in sorted(set(best_labels)):
        sub = gap[gap["cluster"] == c]
        means = z[gap["cluster"] == c].mean().sort_values(key=np.abs, ascending=False)
        colls = sub["collection"].value_counts()
        rows.append({
            "cluster": c, "instances": len(sub),
            "n range": f"{int(sub['n_customers'].min())}-{int(sub['n_customers'].max())}",
            "collections": ", ".join(f"{k.split('/')[-1]} {v}" for k, v in colls.items()),
            "mean gap": float(sub["gap"].mean()), "max gap": int(sub["gap"].max()),
            "mean optimum/n": float((sub["optimum"] / sub["n_customers"]).mean()),
            "mean density": float(sub["density"].mean()),
            "mean g_density": float(sub["g_density"].mean()),
            "extreme features (z)": ", ".join(f"{f} {v:+.1f}" for f, v in means.head(top_features).items()),
        })
    table = pd.DataFrame(rows)
    table.attrs["silhouette"] = silhouettes
    return table, gap, best_k


# ----------------------------------------------------------------------------
# 5. the ten smallest
# ----------------------------------------------------------------------------


def smallest_gap_instances(frame: pd.DataFrame, k: int = TEN) -> pd.DataFrame:
    """The k smallest gap >= 2 instances -- fewest customers, then fewest
    ones, then fewest products -- one per MOSP-graph isomorphism class when
    the certificates are present."""
    gap = frame[frame["gap"] >= GAP_THRESHOLD].copy()
    gap = gap.sort_values(["n_customers", "n_ones", "n_patterns", "source_file", "instance_name"])
    if "graph_cert" in gap.columns and gap["graph_cert"].notna().all():
        gap = gap.drop_duplicates("graph_cert", keep="first")
    return gap.head(k).reset_index(drop=True)


def find_instances(frame: pd.DataFrame, instance_dir: Path = DEFAULT_INSTANCE_DIR) -> list[MOSPInstance]:
    """The MOSPInstance objects for the rows of `frame`, matched on name and file."""
    wanted = {(row.instance_name, row.source_file) for row in frame.itertuples()}
    found: dict[tuple[str, str], MOSPInstance] = {}
    for path, inst in enumerate_instances(instance_dir):
        for name, source in wanted:
            if inst.name == name and str(path).endswith(source):
                found[(name, source)] = inst
    return [found[(row.instance_name, row.source_file)] for row in frame.itertuples()]


def treewidth_upper_bound(graph, restarts: int = TW_RESTARTS, seed: int = 0) -> int:
    """The smallest elimination width found by min-fill and min-degree over
    `restarts` random relabellings (networkx breaks ties by label order, so
    relabelling varies the tie-breaks). An upper bound on treewidth; never a
    bound on the optimum."""
    import networkx as nx
    from networkx.algorithms.approximation import treewidth_min_degree, treewidth_min_fill_in

    if graph.number_of_nodes() == 0:
        return 0
    rng = np.random.default_rng(seed)
    nodes = list(graph.nodes())
    best = graph.number_of_nodes() - 1
    for _ in range(max(1, restarts)):
        perm = rng.permutation(len(nodes))
        relabelled = nx.relabel_nodes(graph, {v: int(p) for v, p in zip(nodes, perm)})
        best = min(best, treewidth_min_fill_in(relabelled)[0], treewidth_min_degree(relabelled)[0])
    return int(best)


def describe_instance(inst: MOSPInstance, expansion_t: int = 8, tw_restarts: int = TW_RESTARTS) -> dict:
    """Everything the report draws for one instance: the matrix as text, the
    MOSP graph's degree sequence, the row and column sum multisets, and every
    bound recomputed from the instance rather than read from the table. The
    clique number is exact (these are small graphs). `simplicial` counts the
    customers in exactly one product, whose neighbourhood is that product's
    clique; `tw_ub` is `treewidth_upper_bound`."""
    import networkx as nx

    from customer_inter.customer_graph import build_customer_graph
    from learning.features import instance_features
    from satisfiability.expansion_bound import mosp_lower_bound
    from satisfiability.mosp_solver import _contraction_degeneracy

    m = np.asarray(inst.matrix, dtype=int)
    graph = build_customer_graph(inst)
    degrees = sorted((d for _, d in graph.degree()), reverse=True)
    rows_sums = m.sum(axis=1).tolist()
    col_sums = m.sum(axis=0).tolist()
    omega = max((len(c) for c in nx.find_cliques(graph)), default=0) if graph.number_of_nodes() else 0
    inv = instance_features(inst, groups=("invariants",))
    contraction = _contraction_degeneracy(graph) + 1 if graph.number_of_nodes() else 0
    expansion = mosp_lower_bound(inst, max_t=expansion_t, time_budget=None)
    return {
        "name": inst.name,
        "n": inst.n_customers, "m": inst.n_patterns, "ones": int(m.sum()),
        "matrix": [" ".join(str(v) for v in row) for row in m.tolist()],
        "degrees": degrees,
        "simplicial": int(sum(1 for r in rows_sums if r == 1)),
        "tw_ub": treewidth_upper_bound(graph, tw_restarts),
        "row_sums": _multiset(rows_sums), "col_sums": _multiset(col_sums),
        "edges": graph.number_of_edges(),
        "components": nx.number_connected_components(graph),
        "clustering": float(nx.average_clustering(graph)) if graph.number_of_nodes() else 0.0,
        "lb_trivial": int(max(col_sums)) if col_sums else 0,
        "lb_clique": int(omega),
        "lb_contraction": int(contraction),
        "lb_expansion": int(expansion),
        "tw_min_fill+1": int(inv["tw_min_fill"]) + 1,
        "bw_rcm+1": int(inv["bw_rcm"]) + 1,
        "sep_size": int(inv["sep_size"]),
        "fiedler": float(inv["fiedler"]),
    }


def _multiset(values: list[int]) -> str:
    counts = pd.Series(values).value_counts().sort_index(ascending=False)
    return ", ".join(f"{int(v)}×{int(c)}" for v, c in counts.items())


def recertify(inst: MOSPInstance, cached: int, solutions_dir: Path | None = None) -> dict:
    """Re-solve through `solve_mosp_exact` with the solutions directory (the
    cached witness is re-verified by simulation) and refute `optimum - 1`
    independently through the customer search, which writes nothing.
    `solutions_dir` defaults to the corpus; tests pass a temporary one."""
    from learning.node_counts import refute
    from satisfiability import mosp_solver
    from satisfiability.mosp_solver import solve_mosp_exact

    value, ordering = solve_mosp_exact(inst, solutions_dir=solutions_dir or mosp_solver.SOLUTIONS_DIR)
    answer = refute(inst, value, "default")
    return {"cached": int(cached), "resolved": int(value),
            "refute status": answer["status"], "refute nodes": int(answer["nodes"]),
            "agree": bool(value == cached and answer["status"] == "unsat")}


def draw_instance(desc: dict, row: pd.Series, cert: dict | None) -> str:
    """One instance as a markdown block for the report."""
    lines = [f"**{desc['name']}** — `{row['source_file'].split('/')[-1]}`, "
             f"{desc['n']} customers × {desc['m']} products, {desc['ones']} ones; "
             f"optimum **{int(row['optimum'])}**, `lb_best` {int(row['lb_best'])}, gap **{int(row['gap'])}**."]
    lines.append(f"Bounds recomputed: trivial {desc['lb_trivial']}, clique {desc['lb_clique']}, "
                 f"contraction {desc['lb_contraction']}, expansion {desc['lb_expansion']}; "
                 f"`tw_min_fill + 1` {desc['tw_min_fill+1']}, `bw_rcm + 1` {desc['bw_rcm+1']}, "
                 f"separator {desc['sep_size']}, Fiedler {desc['fiedler']:.3f}.")
    pw = int(row["optimum"]) - 1
    tw_line = (f"pathwidth {pw} > treewidth (≤ {desc['tw_ub']}), so no treewidth bound reaches the optimum"
               if pw > desc["tw_ub"] else
               f"pathwidth {pw}, treewidth ≤ {desc['tw_ub']}: not separated by the heuristic")
    lines.append(f"MOSP graph: {desc['edges']} edges, {desc['components']} component(s), "
                 f"clustering {desc['clustering']:.3f}; degree sequence "
                 f"{_multiset(desc['degrees'])}. Products per customer {desc['row_sums']}; "
                 f"customers per product {desc['col_sums']}; {desc['simplicial']} of {desc['n']} "
                 f"customers in exactly one product (simplicial). {tw_line}.")
    if cert is not None:
        lines.append(f"Re-certified: `solve_mosp_exact` {cert['resolved']} (cached {cert['cached']}), "
                     f"`optimum − 1` {cert['refute status']} in {cert['refute nodes']} nodes.")
    lines.append("")
    lines.append("```")
    lines.extend(desc["matrix"])
    lines.append("```")
    return "\n".join(lines)


def common_structure(descs: list[dict], optima: list[int] | None = None) -> pd.DataFrame:
    """A table of the properties the ten share or do not. With `optima`, the
    pathwidth `optimum - 1` and whether it provably exceeds the treewidth."""
    rows = []
    for i, d in enumerate(descs):
        degs = d["degrees"]
        row = {
            "instance": d["name"][:40], "n": d["n"], "m": d["m"], "ones": d["ones"],
            "products/customer": d["row_sums"], "customers/product": d["col_sums"],
            "simplicial": d["simplicial"],
            "deg min-max": f"{min(degs)}-{max(degs)}",
            "trivial": d["lb_trivial"], "clique": d["lb_clique"],
            "contraction": d["lb_contraction"], "expansion": d["lb_expansion"],
            "tw_min_fill+1": d["tw_min_fill+1"], "tw_ub+1": d["tw_ub"] + 1, "bw_rcm+1": d["bw_rcm+1"],
            "sep": d["sep_size"], "components": d["components"],
        }
        if optima is not None:
            row["optimum"] = int(optima[i])
            row["pw > tw"] = bool(int(optima[i]) - 1 > d["tw_ub"])
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def _md(table: pd.DataFrame, floatfmt: str = ".3f") -> str:
    return table.to_markdown(index=False, floatfmt=floatfmt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--canonical", type=Path, default=CANONICAL_CSV)
    parser.add_argument("--instance-dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--no-ebm", action="store_true", help="skip the EBM even if interpret is present")
    parser.add_argument("--no-recertify", action="store_true", help="skip the exact re-solve of the ten")
    parser.add_argument("--workers", type=int, default=4, help="cores for the EBM's outer bags")
    parser.add_argument("--out", type=Path, default=None, help="write the tables as markdown")
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    started = time.time()
    frame = with_gap(load_table(args.data, args.canonical))
    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    n = frame["n_customers"]
    emit(f"{len(frame)} instances, n_customers {int(n.min())}-{int(n.max())}, "
         f"{int((n <= 30).sum())} at n <= 30; gap = optimum - lb_best: "
         f"{int((frame['gap'] == 0).sum())} tight, {int((frame['gap'] == 1).sum())} at gap 1, "
         f"{int((frame['gap'] >= GAP_THRESHOLD).sum())} at gap >= {GAP_THRESHOLD}; "
         f"smallest gap >= {GAP_THRESHOLD} instance has {int(frame.loc[frame['gap'] >= GAP_THRESHOLD, 'n_customers'].min())} customers")
    emit()

    emit("## Where the gap is: by size band\n")
    emit(_md(gap_by_band(frame)))
    emit()
    emit("## Where the gap is: by collection\n")
    emit(_md(gap_by_collection(frame)))
    emit()
    emit("## How far each component bound falls short\n")
    emit(_md(component_shortfall(frame)))
    emit()

    rows = classification_rows(frame)
    sets = feature_sets(rows)
    emit(f"## The classifier: gap >= {GAP_THRESHOLD} against tight, grouped, all sizes\n")
    emit(f"{len(rows)} rows ({int(rows['y'].sum())} positives); gap-1 rows left out.\n")
    table, probas = classify(rows, args.folds, args.seed, with_ebm=not args.no_ebm, sets=sets, n_jobs=args.workers)
    emit(_md(table))
    emit()

    mask = mixed_cells(rows)
    cells = rows[mask].groupby(["n_customers", "n_patterns"])["y"].agg(["count", "sum"])
    emit(f"## The classifier within the (n, m) cells holding both classes\n")
    emit(f"{int(mask.sum())} rows in {len(cells)} cells, {int(rows.loc[mask, 'y'].sum())} positives; "
         f"cells: " + ", ".join(f"{int(a)}×{int(b)} ({int(c)}/{int(s)})" for (a, b), (c, s) in cells.iterrows()) + ".\n")
    sub = rows[mask].reset_index(drop=True)
    cell_table, _ = classify(sub, args.folds, args.seed, with_ebm=not args.no_ebm, sets=sets, n_jobs=args.workers)
    emit(_md(cell_table))
    emit()

    key = [k for k in sets if k.startswith("structure + invariants (")][0]
    free_key = [k for k in sets if k.startswith("size-free (")][0]
    emit("## The depth-3 tree (all rows, structure + invariants)\n")
    emit("```")
    emit(tree_text(rows, sets[key], args.seed).rstrip())
    emit("```")
    emit()
    emit("## The depth-3 tree within the mixed cells (structure + invariants)\n")
    emit("```")
    emit(tree_text(sub, sets[key], args.seed).rstrip())
    emit("```")
    emit()
    emit("## The depth-3 tree within the mixed cells (size-free features)\n")
    emit("```")
    emit(tree_text(sub, sets[free_key], args.seed).rstrip())
    emit("```")
    emit()
    if not args.no_ebm:
        terms = ebm_terms(sub, sets[key], args.seed, n_jobs=args.workers)
        if terms is not None:
            emit("## EBM term importances within the mixed cells (structure + invariants)\n")
            emit(_md(terms))
            emit()

    emit("## Each size-free feature alone, z-scored within its (n, m) cell\n")
    emit(_md(within_cell_contrast(rows)))
    emit()

    emit("## The treewidth ceiling: where pathwidth provably exceeds treewidth\n")
    emit(_md(treewidth_ceiling(frame)))
    emit()

    clusters, labelled, k = cluster_gap_instances(frame, seed=args.seed)
    emit(f"## Clusters of the {len(labelled)} gap >= {GAP_THRESHOLD} instances (k = {k} by silhouette)\n")
    emit("Silhouette by k: " + ", ".join(f"{kk} → {v:.3f}" for kk, v in clusters.attrs["silhouette"].items()) + ".\n")
    emit(_md(clusters))
    emit()
    out_csv = DEFAULT_OUT.parent / "bound_gap.csv"
    labelled.to_csv(out_csv, index=False)

    emit(f"## The {TEN} smallest gap >= {GAP_THRESHOLD} instances, one per isomorphism class\n")
    ten = smallest_gap_instances(frame)
    insts = find_instances(ten, args.instance_dir)
    descs = [describe_instance(inst) for inst in insts]
    certs = [None if args.no_recertify else recertify(inst, int(row.optimum))
             for inst, row in zip(insts, ten.itertuples())]
    emit(_md(common_structure(descs, [int(v) for v in ten["optimum"]])))
    emit()
    if not args.no_recertify:
        cert_table = pd.DataFrame([{"instance": d["name"][:40], **c} for d, c in zip(descs, certs)])
        emit("### Re-certification\n")
        emit(_md(cert_table))
        emit()
    for desc, (_, row), cert in zip(descs, ten.iterrows(), certs):
        emit(draw_instance(desc, row, cert))
        emit()

    emit(f"_{time.time() - started:.0f} s; {out_csv} written._")
    if args.out:
        args.out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
