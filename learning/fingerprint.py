"""How distinguishable are the benchmark families? A generator fingerprint and a
map of instance space.

The question (`reports/ml_nature_plan.md` §2.1b): if a classifier can tell
which collection an instance came from using nothing but its structure, then
the collections occupy different regions of instance space and a result
measured on one family says nothing about another. The classifier's accuracy
*is* the finding; it is not used for anything.

Three things are measured, each against the baseline that makes it mean
something:

1. **The fingerprint.** Predict the sub-collection (Harvey, Simonis, Shaw,
   Wilson, Miller, Chu & Stuckey, Faggioli--Bentivoglio, SCOOP, and the
   `MOSP_Instances/Challenge` copies) from the structure-only features of
   `learning.features` -- nothing the solver computed. Baselines: the majority
   class, and the two size columns `(n_customers, n_patterns)` alone, because
   the collections were generated at different sizes and a fingerprint that is
   only size is not a fingerprint. A third feature set removes size entirely
   (every count divided by the dimension it scales with) to ask what remains.
   Every number is reported under three splits: grouped by `source_file` as
   the loop's rules demand; grouped by the connected components of files and
   MOSP-graph isomorphism classes from `learning/data/canonical.csv`, because
   §1 showed that 157 classes span more than one file and a file split leaks
   isomorphic copies; and a random split, printed only to show the size of the
   leak. Where `learning/data/canonical.csv` is absent the second split is
   skipped.

   A classifier cannot beat the **ceiling** set by instances whose isomorphic
   copies carry another collection's label: every feature is constant on a
   matrix-isomorphism class, so of a class holding `a` Shaw and `b` Challenge
   rows at least `min(a, b)` are wrong under any model. The ceiling is printed
   beside the accuracies.

2. **The same-size test.** Restricted to the `(n, m)` cells where at least two
   collections each contribute ten or more instances, so size cannot help.
   This is where Harvey and Simonis, both random generators at 10 to 30
   customers, are told apart or not.

3. **Within Chu & Stuckey**, predict the density class -- the third number in
   `Random-n-m-d-k`, which the data shows is the mean number of customers per
   product (`col_mean` tracks `d` to within 0.3 at every size) -- and, as a
   control, the seed index `k`, which has no structural meaning and must sit at
   chance. Each instance is its own file there, so grouping by file is a plain
   5-fold split.

Then the map: a 2-D embedding (UMAP behind a soft import, else PCA) of the
standardised structure features, one point per instance, coloured by
collection, written to `reports/figures/instance_space.png`. The picture is
summarised in numbers by the 10-nearest-neighbour purity of each collection in
the embedding and in the full feature space, and by the composition of k-means
regions of the map.

Usage:
    python -m learning.fingerprint
    python -m learning.fingerprint --out reports/fingerprint_tables.md
    python -m learning.fingerprint --no-umap        # force the PCA fallback

Nothing here is a bound, nothing touches a solver default, nothing is written
to `solutions/`.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_OUT, feature_columns

try:  # soft import: the map falls back to PCA without it
    import umap as _umap
except ImportError:  # pragma: no cover - exercised only where umap-learn is absent
    _umap = None

HAVE_UMAP = _umap is not None
DATA_DIR = Path("learning/data")
CANONICAL_CSV = DATA_DIR / "canonical.csv"
EMBEDDING_CSV = DATA_DIR / "instance_space.csv"
FIGURE = Path("reports/figures/instance_space.png")
BOUND_PREFIXES = ("lb_", "ub_", "bound_")
SIZE_COLUMNS = ["n_customers", "n_patterns"]
MIN_CELL = 10  # instances per collection for an (n, m) cell to count as shared
KNN = 10

__all__ = [
    "HAVE_UMAP",
    "load_table",
    "structure_columns",
    "size_free_features",
    "union_groups",
    "label_ceiling",
    "classify",
    "fingerprint_study",
    "same_size_study",
    "chu_stuckey_study",
    "embed",
    "knn_purity",
    "region_composition",
    "draw_map",
]


# ----------------------------------------------------------------------------
# the table
# ----------------------------------------------------------------------------


def sub_collection(source_file: str) -> str:
    """`benchmarks/instances/A/B/file` -> `A/B`, the label everything predicts."""
    parts = Path(source_file).parent.parts  # directories only
    return "/".join(parts[2:4])


def load_table(
    data: Path = DEFAULT_OUT, canonical: Path = CANONICAL_CSV
) -> pd.DataFrame:
    """The feature table with the sub-collection label and, if the canonical
    forms were computed, the isomorphism-class certificates joined on."""
    if not data.exists():
        raise FileNotFoundError(f"{data} does not exist; run `python -m learning.dataset` first")
    frame = pd.read_csv(data)
    frame["collection"] = frame["source_file"].map(sub_collection)
    if canonical.exists():
        certs = pd.read_csv(canonical)[
            ["instance_name", "source_file", "graph_cert", "bipartite_cert"]
        ]
        frame = frame.merge(certs, on=["instance_name", "source_file"], how="left")
    return frame


def structure_columns(frame: pd.DataFrame) -> list[str]:
    """Every feature column that is not a bound: the structure-only set.

    The `invariants` group (2026-09-25) is left out so that §2 of
    `reports/ml_nature.md` regenerates from the same 28 columns it reports.
    """
    from learning.features import invariant_names

    skip = set(invariant_names()) | {"graph_cert", "bipartite_cert"}
    return [c for c in feature_columns(frame)
            if not c.startswith(BOUND_PREFIXES) and c not in skip]


def size_free_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Structure with the size divided out.

    Ratios keep their meaning across sizes; counts are divided by the
    dimension they scale with. `n_customers`, `n_patterns`, `n_ones`,
    `g_nodes` and `g_edges` are dropped outright (`g_edges` survives as
    `g_density`).
    """
    n = frame["n_customers"].astype(float).clip(lower=1)
    m = frame["n_patterns"].astype(float).clip(lower=1)

    def _ratio(num: str, den: pd.Series) -> pd.Series:
        return frame[num].astype(float) / den

    def _cv(prefix: str) -> pd.Series:
        mean = frame[f"{prefix}_mean"].astype(float)
        return (frame[f"{prefix}_std"].astype(float) / mean.where(mean > 0, np.nan)).fillna(0.0)

    out = pd.DataFrame({
        "density": frame["density"],
        "shape_ratio": frame["shape_ratio"],
        "distinct_col_frac": frame["distinct_col_frac"],
        "distinct_row_frac": frame["distinct_row_frac"],
        "dominated_col_frac": frame["dominated_col_frac"],
        "col_max_frac": frame["col_max_frac"],
        "col_min_frac": _ratio("col_min", n),
        "row_min_frac": _ratio("row_min", m),
        "row_max_frac": _ratio("row_max", m),
        "row_cv": _cv("row"),
        "col_cv": _cv("col"),
        "g_density": frame["g_density"],
        "g_components_frac": _ratio("g_components", n),
        "g_largest_comp_frac": frame["g_largest_comp_frac"],
        "g_clustering": frame["g_clustering"],
        "g_degeneracy_frac": _ratio("g_degeneracy", (n - 1).clip(lower=1)),
        "g_deg_min_frac": _ratio("g_deg_min", (n - 1).clip(lower=1)),
        "g_deg_max_frac": _ratio("g_deg_max", (n - 1).clip(lower=1)),
        "g_deg_cv": _cv("g_deg"),
    }, index=frame.index)
    return out.astype(float)


# ----------------------------------------------------------------------------
# splits and ceilings
# ----------------------------------------------------------------------------


def union_groups(files: pd.Series, classes: pd.Series) -> np.ndarray:
    """Group ids: connected components of the bipartite graph file--class.

    Two rows share a group if they share a file, or an isomorphism class, or
    are linked by a chain of either. Holding out a whole group holds out every
    isomorphic copy of every instance in it, which grouping by file alone does
    not (§1 of `reports/ml_nature.md`).
    """
    import networkx as nx

    graph = nx.Graph()
    for f, c in zip(files, classes):
        c = f if pd.isna(c) else c
        graph.add_edge(("f", f), ("c", c))
    component_of: dict[tuple[str, str], int] = {}
    for gid, nodes in enumerate(nx.connected_components(graph)):
        for node in nodes:
            component_of[node] = gid
    return np.array([component_of[("f", f)] for f in files])


def label_ceiling(labels: pd.Series, classes: pd.Series) -> float:
    """Best accuracy any function of the features can reach.

    Features are constant on an isomorphism class, so within a class the
    model returns one label and every row of another label is wrong.
    """
    frame = pd.DataFrame({"y": labels.to_numpy(), "c": classes.to_numpy()})
    frame["c"] = frame["c"].fillna(pd.Series(range(len(frame)), index=frame.index).astype(str))
    best = frame.groupby("c")["y"].agg(lambda s: s.value_counts().iloc[0]).sum()
    return float(best / len(frame))


# ----------------------------------------------------------------------------
# classification
# ----------------------------------------------------------------------------


def _splitter(name: str, folds: int, seed: int):
    """Shuffled splits only. `GroupKFold` assigns equal-sized groups to folds
    round-robin in order of appearance, which on the Chu & Stuckey files
    (`Random-n-m-d-1`, `-2`, ... sorted) put every seed index `k` in its own
    fold and made the control score exactly zero."""
    from sklearn.model_selection import KFold, StratifiedGroupKFold

    if name == "random":
        return KFold(n_splits=folds, shuffle=True, random_state=seed)
    return StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=seed)


def _model(seed: int):
    """A random forest, not gradient boosting: `HistGradientBoostingClassifier`
    scored 0.81 on a random split where a forest and LightGBM both score 0.98,
    thrown by classes of one and twenty instances. The forest needs no extra
    dependency and fits in a quarter of a second."""
    from sklearn.ensemble import RandomForestClassifier

    return RandomForestClassifier(n_estimators=300, random_state=seed, n_jobs=16)


def classify(
    features: pd.DataFrame,
    labels: np.ndarray,
    groups: np.ndarray | None,
    folds: int = 5,
    seed: int = 0,
    random_split: bool = False,
) -> dict:
    """Cross-validated predictions of a gradient-boosted classifier.

    Returns accuracy, balanced accuracy, macro F1, the per-class recall and
    the confusion matrix. `groups=None` with `random_split=False` is refused,
    so a grouped number cannot silently become an ungrouped one.
    """
    from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                                 confusion_matrix, f1_score, recall_score)
    from sklearn.model_selection import cross_val_predict

    if groups is None and not random_split:
        raise ValueError("a grouped split needs groups")
    classes = np.array(sorted(set(labels)))
    n_groups = len(set(groups)) if groups is not None else len(labels)
    n_splits = max(2, min(folds, n_groups))
    pred = cross_val_predict(
        _model(seed), features, labels,
        cv=_splitter("random" if random_split else "grouped", n_splits, seed),
        groups=groups,
    )
    return {
        "accuracy": float(accuracy_score(labels, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(labels, pred)),
        "macro_f1": float(f1_score(labels, pred, average="macro")),
        "recall": dict(zip(classes, recall_score(labels, pred, labels=classes,
                                                 average=None, zero_division=0))),
        "confusion": pd.DataFrame(confusion_matrix(labels, pred, labels=classes),
                                  index=classes, columns=classes),
        "pred": pred,
    }


def _majority(labels: np.ndarray) -> float:
    return float(pd.Series(labels).value_counts(normalize=True).iloc[0])


def _feature_sets(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "size only (n, m)": frame[SIZE_COLUMNS].astype(float),
        "structure (all)": frame[structure_columns(frame)].astype(float),
        "structure, size-free": size_free_features(frame),
    }


def _splits(frame: pd.DataFrame) -> dict[str, tuple[np.ndarray | None, bool]]:
    splits: dict[str, tuple[np.ndarray | None, bool]] = {
        "grouped by file": (frame["source_file"].to_numpy(), False),
    }
    if "graph_cert" in frame:
        splits["grouped by file + graph class"] = (
            union_groups(frame["source_file"], frame["graph_cert"]), False)
    splits["random (leaks!)"] = (None, True)
    return splits


def fingerprint_study(frame: pd.DataFrame, folds: int = 5, seed: int = 0) -> dict:
    """Study 1: the collection from structure, every feature set x every split."""
    labels = frame["collection"].to_numpy()
    rows = [{"features": "majority class", "split": "none (baseline)",
             "accuracy": _majority(labels), "balanced_accuracy": 1 / len(set(labels)),
             "macro_f1": float("nan")}]
    results: dict[tuple[str, str], dict] = {}
    for fname, feats in _feature_sets(frame).items():
        for sname, (groups, random_split) in _splits(frame).items():
            res = classify(feats, labels, groups, folds, seed, random_split)
            results[(fname, sname)] = res
            rows.append({"features": fname, "split": sname,
                         **{k: res[k] for k in ("accuracy", "balanced_accuracy", "macro_f1")}})
    table = pd.DataFrame(rows)
    ceilings = {}
    for level in ("bipartite_cert", "graph_cert"):
        if level in frame:
            ceilings[level] = label_ceiling(frame["collection"], frame[level])
    key = ("structure (all)", "grouped by file")
    return {"table": table, "ceilings": ceilings, "results": results,
            "main": results[key], "n_groups": {
                name: (len(set(g)) if g is not None else None)
                for name, (g, _) in _splits(frame).items()}}


def same_size_study(frame: pd.DataFrame, folds: int = 5, seed: int = 0,
                    min_cell: int = MIN_CELL) -> pd.DataFrame:
    """Study 2: collections told apart at the same (n, m)."""
    cell = frame["n_customers"].astype(int).astype(str) + "x" + frame["n_patterns"].astype(int).astype(str)
    counts = pd.crosstab(cell, frame["collection"])
    shared = counts.index[(counts >= min_cell).sum(axis=1) >= 2]
    keep = cell.isin(shared).to_numpy()
    sub = frame[keep].reset_index(drop=True)
    if len(sub) == 0:
        return pd.DataFrame()
    cells = cell[keep].to_numpy()
    # drop rows whose collection has fewer than min_cell in their cell, so the
    # classes present in each cell are the ones the cell is about
    big = np.array([counts.loc[c, col] >= min_cell for c, col in zip(cells, sub["collection"])])
    sub, cells = sub[big].reset_index(drop=True), cells[big]
    labels = sub["collection"].to_numpy()
    groups = sub["source_file"].to_numpy()
    preds = {}
    for fname in ("structure (all)", "structure, size-free"):
        feats = _feature_sets(sub)[fname]
        preds[fname] = classify(feats, labels, groups, folds, seed)["pred"]
    rows = []
    for c in sorted(set(cells), key=lambda s: tuple(map(int, s.split("x")))):
        mask = cells == c
        row = {"cell (n x m)": c, "instances": int(mask.sum()),
               "collections": " + ".join(sorted({x.split("/")[-1] for x in labels[mask]})),
               "majority": _majority(labels[mask])}
        for fname, pred in preds.items():
            row[fname] = float((pred[mask] == labels[mask]).mean())
        rows.append(row)
    row = {"cell (n x m)": "all shared cells", "instances": len(sub),
           "collections": "", "majority": _majority(labels)}
    for fname, pred in preds.items():
        row[fname] = float((pred == labels).mean())
    rows.append(row)
    return pd.DataFrame(rows)


def chu_stuckey_study(frame: pd.DataFrame, folds: int = 5, seed: int = 0) -> pd.DataFrame:
    """Study 3: the density class d, and the seed k as a control, in Random-n-m-d-k."""
    cs = frame[frame["collection"].str.endswith("Chu_Stuckey")].reset_index(drop=True)
    if len(cs) == 0:
        return pd.DataFrame()
    parsed = cs["instance_name"].str.extract(r"Random-(\d+)-(\d+)-(\d+)-(\d+)_")
    d = parsed[2].astype(int).to_numpy()
    k = parsed[3].astype(int).to_numpy()
    groups = cs["source_file"].to_numpy()
    sets = _feature_sets(cs)
    sets["col_mean alone"] = cs[["col_mean"]].astype(float)
    rows = []
    for target, labels in (("density class d", d), ("seed index k (control)", k)):
        rows.append({"target": target, "features": "majority class",
                     "accuracy": _majority(labels), "balanced_accuracy": 1 / len(set(labels))})
        for fname, feats in sets.items():
            res = classify(feats, labels, groups, folds, seed)
            rows.append({"target": target, "features": fname,
                         "accuracy": res["accuracy"],
                         "balanced_accuracy": res["balanced_accuracy"]})
    return pd.DataFrame(rows)


def importances(frame: pd.DataFrame, seed: int = 0, top: int = 12) -> pd.DataFrame:
    """Permutation importance of the structure features, on held-out files,
    in accuracy points."""
    from sklearn.inspection import permutation_importance

    columns = structure_columns(frame)
    labels = frame["collection"].to_numpy()
    files = sorted(frame["source_file"].unique())
    test = frame["source_file"].isin(set(files[::5])).to_numpy()
    model = _model(seed)
    model.fit(frame[columns][~test], labels[~test])
    result = permutation_importance(model, frame[columns][test], labels[test],
                                    n_repeats=5, random_state=seed, scoring="accuracy")
    return (pd.DataFrame({"feature": columns, "accuracy_cost": result.importances_mean})
            .sort_values("accuracy_cost", ascending=False).head(top).reset_index(drop=True))


def readable_tree(frame: pd.DataFrame, depth: int = 3, seed: int = 0) -> tuple[str, float]:
    """A depth-limited decision tree over the size-free features: the rules a
    person can read, and their grouped-by-file accuracy."""
    from sklearn.model_selection import cross_val_predict
    from sklearn.tree import DecisionTreeClassifier, export_text

    feats = size_free_features(frame)
    labels = frame["collection"].to_numpy()
    short = np.array([c.split("/")[-1] for c in labels])
    tree = DecisionTreeClassifier(max_depth=depth, random_state=seed, min_samples_leaf=20)
    pred = cross_val_predict(tree, feats, short, cv=_splitter("grouped", 5, seed),
                             groups=frame["source_file"].to_numpy())
    tree.fit(feats, short)
    text = export_text(tree, feature_names=list(feats.columns), max_depth=depth, decimals=3)
    return text, float((pred == short).mean())


# ----------------------------------------------------------------------------
# the map
# ----------------------------------------------------------------------------


def embed(features: pd.DataFrame, use_umap: bool = True, seed: int = 0) -> tuple[np.ndarray, str]:
    """2-D coordinates of standardised features: UMAP if available, else PCA."""
    from sklearn.preprocessing import StandardScaler

    x = StandardScaler().fit_transform(features.to_numpy(dtype=float))
    x = np.nan_to_num(x)
    if use_umap and HAVE_UMAP:
        reducer = _umap.UMAP(n_components=2, n_neighbors=30, min_dist=0.1, random_state=seed)
        return np.asarray(reducer.fit_transform(x)), "UMAP"
    from sklearn.decomposition import PCA

    return PCA(n_components=2, random_state=seed).fit_transform(x), "PCA"


def knn_purity(points: np.ndarray, labels: np.ndarray, k: int = KNN) -> pd.DataFrame:
    """Per collection, the mean share of each instance's k nearest neighbours
    (itself excluded) that carry the same label."""
    from sklearn.neighbors import NearestNeighbors

    nn = NearestNeighbors(n_neighbors=min(k + 1, len(points))).fit(points)
    _, idx = nn.kneighbors(points)
    same = (labels[idx[:, 1:]] == labels[:, None]).mean(axis=1)
    out = (pd.DataFrame({"collection": labels, "purity": same})
           .groupby("collection")["purity"].agg(["mean", "size"])
           .rename(columns={"mean": f"{k}-NN purity", "size": "instances"}))
    out.loc["all"] = [float(same.mean()), len(labels)]
    out["instances"] = out["instances"].astype(int)
    return out.reset_index()


def region_composition(points: np.ndarray, labels: np.ndarray, frame: pd.DataFrame,
                       regions: int = 12, seed: int = 0) -> pd.DataFrame:
    """k-means regions of the map, with what sits in each."""
    from sklearn.cluster import KMeans

    region = KMeans(n_clusters=regions, n_init=10, random_state=seed).fit_predict(points)
    rows = []
    for r in range(regions):
        mask = region == r
        counts = pd.Series(labels[mask]).value_counts()
        rows.append({
            "region": r, "instances": int(mask.sum()),
            "n range": f"{int(frame['n_customers'][mask].min())}-{int(frame['n_customers'][mask].max())}",
            "density": f"{frame['density'][mask].mean():.2f}",
            "optimum/n": f"{(frame['optimum'][mask] / frame['n_customers'][mask]).mean():.2f}",
            "composition": ", ".join(f"{c.split('/')[-1]} {v}" for c, v in counts.items()),
        })
    return pd.DataFrame(rows).sort_values("instances", ascending=False).reset_index(drop=True)


# Categorical slots in fixed order (validated palette, light surface); the
# collections are assigned in a fixed order so a colour follows the entity.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
COLOUR_ORDER = [
    "ChallengeInstances2005/Simonis",
    "ChallengeInstances2005/Harvey",
    "MOSP_Instances/Faggioli_Bentivoglio",
    "MOSP_Instances/Chu_Stuckey",
    "ChallengeInstances2005/Shaw",
    "ChallengeInstances2005/Wilson",
    "MOSP_Instances/SCOOP",
    "MOSP_Instances/Challenge",  # holds Miller too: the copies, see §1
]
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def _legend_label(collection: str, n: int) -> str:
    name = collection.split("/")[-1].replace("_", " ")
    if collection.endswith("Challenge"):
        name = "Challenge copies + Miller"
    if name == "Chu Stuckey":
        name = "Chu & Stuckey"
    if name == "Faggioli Bentivoglio":
        name = "Faggioli–Bentivoglio"
    return f"{name} ({n:,})"


def draw_map(points: np.ndarray, frame: pd.DataFrame, method: str,
             path: Path = FIGURE, size_free_points: np.ndarray | None = None) -> Path:
    """Panels: the embedding coloured by collection, the same coloured by size,
    and, if given, the embedding of the size-free features by collection."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, BoundaryNorm

    ink, muted, surface = "#1a1a19", "#6b6a63", "#fcfcfb"
    plt.rcParams.update({"font.size": 9, "text.color": ink, "axes.labelcolor": muted,
                         "xtick.color": muted, "ytick.color": muted})
    labels = frame["collection"].to_numpy()
    labels = np.where(labels == "ChallengeInstances2005/Miller", "MOSP_Instances/Challenge", labels)
    order = [c for c in COLOUR_ORDER if c in set(labels)]
    colour = {c: PALETTE[i] for i, c in enumerate(order)}

    panels = 3 if size_free_points is not None else 2
    fig, axes = plt.subplots(1, panels, figsize=(6.5 * panels, 5.6), facecolor=surface)
    rng = np.random.default_rng(0)
    shuffle = rng.permutation(len(points))  # draw order not by collection
    handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=7,
                          markerfacecolor=colour[c], markeredgecolor=surface,
                          label=_legend_label(c, int((labels == c).sum())))
               for c in order]

    ax = axes[0]
    ax.scatter(points[shuffle, 0], points[shuffle, 1], s=16,
               c=[colour[c] for c in labels[shuffle]], alpha=0.75,
               edgecolors=surface, linewidths=0.4)
    ax.legend(handles=handles, loc="best", frameon=False, fontsize=8, labelcolor=ink)
    ax.set_title("all structure features, by collection", loc="left", color=ink, fontsize=10)

    if size_free_points is not None:
        ax = axes[2]
        ax.scatter(size_free_points[shuffle, 0], size_free_points[shuffle, 1], s=16,
                   c=[colour[c] for c in labels[shuffle]], alpha=0.75,
                   edgecolors=surface, linewidths=0.4)
        ax.legend(handles=handles, loc="best", frameon=False, fontsize=8, labelcolor=ink)
        ax.set_title("size-free features, by collection", loc="left", color=ink, fontsize=10)

    ax = axes[1]
    n = frame["n_customers"].to_numpy(dtype=float)
    bounds = [9, 12, 17, 25, 35, 60, 100, 140]
    cmap = ListedColormap(SEQUENTIAL)
    norm = BoundaryNorm(bounds, cmap.N)
    sc = ax.scatter(points[shuffle, 0], points[shuffle, 1], s=16, c=n[shuffle],
                    cmap=cmap, norm=norm, alpha=0.8, edgecolors=surface, linewidths=0.4)
    cbar = fig.colorbar(sc, ax=ax, ticks=bounds, fraction=0.04, pad=0.02)
    cbar.set_label("customers (n)", color=muted)
    cbar.outline.set_visible(False)
    ax.set_title("all structure features, by number of customers", loc="left", color=ink, fontsize=10)

    for ax in axes:
        ax.set_facecolor(surface)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#d9d8d0")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f"{method} 1")
        ax.set_ylabel(f"{method} 2")
    fig.suptitle(f"Instance space: {method} of {len(points):,} certified instances, "
                 f"{len(structure_columns(frame))} structure features",
                 x=0.01, ha="left", color=ink, fontsize=11)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, facecolor=surface)
    plt.close(fig)
    return path


# ----------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------


def _md(table: pd.DataFrame, floatfmt: str = ".3f") -> str:
    try:
        return table.to_markdown(index=False, floatfmt=floatfmt)
    except ImportError:  # tabulate missing
        return table.round(3).to_string(index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--canonical", type=Path, default=CANONICAL_CSV)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--figure", type=Path, default=FIGURE)
    parser.add_argument("--no-umap", action="store_true", help="force the PCA fallback")
    parser.add_argument("--out", type=Path, default=None, help="also write the tables as markdown")
    args = parser.parse_args()
    warnings.filterwarnings("ignore")

    frame = load_table(args.data, args.canonical)
    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit(f"{len(frame)} instances, {frame['source_file'].nunique()} files, "
         f"{frame['collection'].nunique()} collections, "
         f"{len(structure_columns(frame))} structure features, "
         f"{size_free_features(frame).shape[1]} size-free features; "
         f"canonical forms {'joined' if 'graph_cert' in frame else 'absent'}\n")

    emit("## Instances per collection\n")
    emit(_md(frame.groupby("collection").agg(instances=("instance_name", "size"),
                                              files=("source_file", "nunique"),
                                              n_min=("n_customers", "min"),
                                              n_max=("n_customers", "max")).reset_index(), ".0f"))

    emit("\n## Study 1: the collection from structure\n")
    fp = fingerprint_study(frame, args.folds, args.seed)
    emit(_md(fp["table"]))
    emit(f"\ngroups per split: {fp['n_groups']}")
    for level, value in fp["ceilings"].items():
        emit(f"ceiling from {level} classes: {value:.4f}")
    emit("\n### Per-class recall, structure (all), grouped by file\n")
    rec = pd.DataFrame({"collection": list(fp["main"]["recall"]),
                        "instances": [int((frame["collection"] == c).sum()) for c in fp["main"]["recall"]],
                        "files": [int(frame.loc[frame["collection"] == c, "source_file"].nunique())
                                  for c in fp["main"]["recall"]],
                        "recall": list(fp["main"]["recall"].values())})
    emit(_md(rec))
    if ("structure (all)", "grouped by file + graph class") in fp["results"]:
        alt = fp["results"][("structure (all)", "grouped by file + graph class")]
        rec["recall, file + class"] = list(alt["recall"].values())
        emit("\nwith the file + graph-class split: " +
             ", ".join(f"{c.split('/')[-1]} {v:.3f}" for c, v in alt["recall"].items()))
    emit("\n### Confusion matrix (rows true, columns predicted), structure (all), grouped by file\n")
    conf = fp["main"]["confusion"].copy()
    conf.index = [c.split("/")[-1] for c in conf.index]
    conf.columns = [c.split("/")[-1] for c in conf.columns]
    emit(_md(conf.reset_index().rename(columns={"index": "true \\ predicted"}), ".0f"))

    emit("\n### Permutation importance (accuracy points, held-out files)\n")
    emit(_md(importances(frame, args.seed)))
    tree_text, tree_acc = readable_tree(frame, seed=args.seed)
    emit(f"\n### Depth-3 tree on size-free features: grouped-by-file accuracy {tree_acc:.3f}\n")
    emit("```\n" + tree_text.rstrip() + "\n```")

    emit("\n## Study 2: collections at the same (n, m)\n")
    emit(_md(same_size_study(frame, args.folds, args.seed)))

    emit("\n## Study 3: within Chu & Stuckey, Random-n-m-d-k\n")
    emit(_md(chu_stuckey_study(frame, args.folds, args.seed)))

    emit("\n## The map\n")
    feats = frame[structure_columns(frame)].astype(float)
    points, method = embed(feats, use_umap=not args.no_umap, seed=args.seed)
    free_points, _ = embed(size_free_features(frame), use_umap=not args.no_umap, seed=args.seed)
    labels = frame["collection"].to_numpy()
    emit(f"embedding: {method}" + ("" if HAVE_UMAP else " (umap-learn not installed)"))
    EMBEDDING_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"instance_name": frame["instance_name"], "source_file": frame["source_file"],
                  "collection": labels, "x": points[:, 0], "y": points[:, 1],
                  "x_size_free": free_points[:, 0], "y_size_free": free_points[:, 1],
                  }).to_csv(EMBEDDING_CSV, index=False)
    path = draw_map(points, frame, method, args.figure, size_free_points=free_points)
    emit(f"figure: {path}; coordinates: {EMBEDDING_CSV}")
    from sklearn.preprocessing import StandardScaler
    raw = np.nan_to_num(StandardScaler().fit_transform(feats.to_numpy(dtype=float)))
    purity = knn_purity(raw, labels).rename(columns={f"{KNN}-NN purity": "features"})
    purity["map"] = knn_purity(points, labels)[f"{KNN}-NN purity"].to_numpy()
    purity["size-free map"] = knn_purity(free_points, labels)[f"{KNN}-NN purity"].to_numpy()
    emit(f"\n### {KNN}-nearest-neighbour purity (share of neighbours from the same collection)\n")
    emit(_md(purity[["collection", "instances", "features", "map", "size-free map"]]))
    emit("\n### Regions of the map (k-means, 12)\n")
    emit(_md(region_composition(points, labels, frame, seed=args.seed), ".2f"))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(lines) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
