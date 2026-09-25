"""Do pathwidth-adjacent graph invariants explain the optimum? (plan §2.2a)

The optimum is `pathwidth(MOSP graph) + 1` (Yanasse 1997c), and
`reports/learning.md` §1 found that the MOSP graph's edge count and mean degree
carry the signal the 36-feature table has. This study adds the `invariants`
group of `learning.features` -- min-fill and min-degree treewidth upper
bounds, reverse Cuthill-McKee bandwidth, spectral radius, Fiedler value, edge
clique cover counts, a balanced separator from a spectral and an RCM sweep,
and the random intersection graph parameters -- and asks five things:

1. **As point estimates.** How close is each invariant, offset by one, to the
   optimum, beside the solver's own `lb_best` and `ub_best`? Which are bounds
   on the corpus and which are not (`bw_rcm + 1` must never be below the
   optimum, since bandwidth >= pathwidth; nothing else is a bound in either
   direction and the table shows it).
2. **Ablation.** Grouped MAE of the same gradient-boosting model with and
   without the group, on the optimum and on the residual `optimum - lb_best`,
   under three splits: grouped by file, grouped by file ∪ isomorphism class
   (`learning.fingerprint.union_groups`), and random for contrast. The plan's
   kill criterion is 0.02 MAE.
3. **Importance.** Permutation importance of all 49 features on held-out
   groups, so the invariants are ranked beside the existing 36.
4. **Each invariant alone.** A model on one invariant plus the two sizes,
   grouped, so the ranking does not depend on what else is in the model.
5. **Order-dependence.** The four greedy invariants are exact only up to
   tie-breaks. A sample of instances is re-featured after shuffling customers
   and products and every change is counted, so the invariance the feature
   module claims is measured rather than assumed.

Every split groups; random-split numbers appear only beside grouped ones.
Nothing here is a bound and nothing reaches `satisfiability.mosp_solver`.

Usage:
    python -m learning.dataset                          # rebuild the table first (~90 s on 16 cores)
    python -m learning.invariants_study --out reports/invariants_tables.md
    python -m learning.invariants_study --invariance-sample 0   # skip the shuffle check
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_OUT, feature_columns
from learning.features import instance_features, invariant_names
from learning.fingerprint import CANONICAL_CSV, load_table, union_groups
from learning.study_optimum import BOUND_PREFIXES, _scores

KILL_MAE = 0.02
SIZE_BANDS = ((1, 30), (31, 60), (61, 200))


# ----------------------------------------------------------------------------
# columns and groups
# ----------------------------------------------------------------------------


def column_sets(frame: pd.DataFrame) -> dict[str, list[str]]:
    """The four feature sets the ablation compares."""
    inv = [c for c in invariant_names() if c in frame.columns]
    cols = [c for c in feature_columns(frame) if c not in ("graph_cert", "bipartite_cert")]
    bounds = [c for c in cols if c.startswith(BOUND_PREFIXES)]
    structure = [c for c in cols if c not in bounds and c not in inv]
    return {
        "structure (28)": structure,
        "structure + invariants": structure + inv,
        "structure + bounds (36)": structure + bounds,
        "all (36 + invariants)": structure + bounds + inv,
    }


def group_ids(frame: pd.DataFrame) -> dict[str, np.ndarray | None]:
    """The splits: by file, by file ∪ MOSP-graph class if the certificates are
    joined on, and random (None)."""
    splits: dict[str, np.ndarray | None] = {
        "grouped by file": frame["source_file"].to_numpy(),
    }
    if "graph_cert" in frame.columns and frame["graph_cert"].notna().any():
        splits["grouped by file ∪ class"] = union_groups(frame["source_file"], frame["graph_cert"])
    splits["random (leaks!)"] = None
    return splits


def _cv_predict(frame, columns, target, groups, folds, seed):
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import GroupKFold, KFold, cross_val_predict

    model = HistGradientBoostingRegressor(random_state=seed, max_iter=300)
    if groups is None:
        splitter = KFold(n_splits=folds, shuffle=True, random_state=seed)
    else:
        splitter = GroupKFold(n_splits=folds)
    return cross_val_predict(model, frame[columns], target, cv=splitter, groups=groups)


# ----------------------------------------------------------------------------
# 1. point estimates
# ----------------------------------------------------------------------------


POINT_ESTIMATES = (
    ("lb_best", "lb_best", 0),
    ("ub_best", "ub_best", 0),
    ("ub_cs_dfs", "ub_cs_dfs", 0),
    ("tw_min_fill + 1", "tw_min_fill", 1),
    ("tw_min_degree + 1", "tw_min_degree", 1),
    ("bw_rcm + 1", "bw_rcm", 1),
    ("round(spectral_radius) + 1", "spectral_radius", 1),
    ("g_degeneracy + 1", "g_degeneracy", 1),
    ("sep_size + 1", "sep_size", 1),
)


def point_estimates(frame: pd.DataFrame) -> pd.DataFrame:
    """Each invariant, offset by one, as an estimate of the optimum.

    `below` and `above` are the counts of instances where the estimate sits
    under or over the optimum; a valid lower bound has `above == 0` and a
    valid upper bound `below == 0`.
    """
    truth = frame["optimum"].to_numpy()
    rows = []
    for label, column, offset in POINT_ESTIMATES:
        if column not in frame.columns:
            continue
        est = np.rint(frame[column].to_numpy(dtype=float)) + offset
        rows.append({
            "estimate": label,
            **_scores(est, truth),
            "below": int((est < truth).sum()),
            "above": int((est > truth).sum()),
            "max_below": int(max((truth - est).max(), 0)),
            "max_above": int(max((est - truth).max(), 0)),
        })
    return pd.DataFrame(rows)


def point_estimates_by_band(frame: pd.DataFrame) -> pd.DataFrame:
    """Exact-hit rate and MAE of the three leading estimates per size band,
    so the headline finding states the size range it covers."""
    truth = frame["optimum"].to_numpy()
    n = frame["n_customers"].to_numpy()
    rows = []
    for lo, hi in SIZE_BANDS:
        mask = (n >= lo) & (n <= hi)
        if not mask.any():
            continue
        row = {"band": f"{lo}-{hi}", "instances": int(mask.sum())}
        for label, column, offset in POINT_ESTIMATES[:4]:
            est = np.rint(frame[column].to_numpy(dtype=float)) + offset
            key = label.replace(" + 1", "+1")
            row[f"exact {key}"] = float((est[mask] == truth[mask]).mean())
            row[f"mae {key}"] = float(np.abs(est[mask] - truth[mask]).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def group_sizes(frame: pd.DataFrame) -> pd.DataFrame:
    """How unbalanced each grouping is: the largest groups, as a share of the
    corpus. `GroupKFold` keeps a group whole, so a group holding a third of
    the corpus makes one fold a third-of-the-corpus extrapolation."""
    rows = []
    for name, groups in group_ids(frame).items():
        if groups is None:
            continue
        counts = pd.Series(groups).value_counts()
        rows.append({"split": name, "groups": int(len(counts)),
                     "largest": int(counts.iloc[0]),
                     "largest_frac": float(counts.iloc[0] / len(frame)),
                     "top5_frac": float(counts.iloc[:5].sum() / len(frame))})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# 2. ablation
# ----------------------------------------------------------------------------


def ablation(frame: pd.DataFrame, folds: int = 5, seed: int = 0) -> pd.DataFrame:
    """Grouped MAE with and without the invariants, on the optimum and on the
    residual over the best proved bound. `delta_mae` is against the same
    feature set without the group; negative is better."""
    sets = column_sets(frame)
    splits = group_ids(frame)
    targets = {
        "optimum": frame["optimum"].to_numpy(dtype=float),
        "optimum - lb_best": (frame["optimum"] - frame["lb_best"]).to_numpy(dtype=float),
    }
    hard = (frame["bound_gap"] > 0).to_numpy()

    rows = []
    cache: dict[tuple[str, str, str], dict] = {}
    for tname, target in targets.items():
        for sname, groups in splits.items():
            for fname, columns in sets.items():
                pred = _cv_predict(frame, columns, target, groups, folds, seed)
                scores = _scores(pred, target)
                scores_hard = _scores(pred[hard], target[hard])
                cache[(tname, sname, fname)] = scores
                rows.append({"target": tname, "split": sname, "features": fname,
                             **scores, "mae_gap_rows": scores_hard["mae"],
                             "exact_gap_rows": scores_hard["exact"]})
    table = pd.DataFrame(rows)
    without = {"structure + invariants": "structure (28)",
               "all (36 + invariants)": "structure + bounds (36)"}
    table["delta_mae"] = [
        cache[(t, s, f)]["mae"] - cache[(t, s, without[f])]["mae"] if f in without else np.nan
        for t, s, f in zip(table["target"], table["split"], table["features"])
    ]
    return table


def by_size_band(frame: pd.DataFrame, folds: int = 5, seed: int = 0) -> pd.DataFrame:
    """The structure-only ablation sliced by customer count, under the
    file ∪ class grouping, so the size range a gain covers is on record."""
    sets = column_sets(frame)
    splits = group_ids(frame)
    groups = splits.get("grouped by file ∪ class", splits["grouped by file"])
    target = frame["optimum"].to_numpy(dtype=float)
    preds = {name: _cv_predict(frame, sets[name], target, groups, folds, seed)
             for name in ("structure (28)", "structure + invariants",
                          "structure + bounds (36)", "all (36 + invariants)")}
    n = frame["n_customers"].to_numpy()
    rows = []
    for lo, hi in SIZE_BANDS:
        mask = (n >= lo) & (n <= hi)
        if not mask.any():
            continue
        for name, pred in preds.items():
            rows.append({"band": f"{lo}-{hi}", "instances": int(mask.sum()),
                         "features": name, **_scores(pred[mask], target[mask])})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# 3. importance
# ----------------------------------------------------------------------------


def importances(frame: pd.DataFrame, seed: int = 0, target: str = "optimum") -> pd.DataFrame:
    """Permutation importance of all features on a held-out fifth of the
    groups, in MAE points, with each feature's group labelled."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.inspection import permutation_importance

    columns = column_sets(frame)["all (36 + invariants)"]
    inv = set(invariant_names())
    truth = frame["optimum"].to_numpy(dtype=float)
    if target == "residual":
        truth = truth - frame["lb_best"].to_numpy(dtype=float)

    groups = group_ids(frame).get("grouped by file ∪ class")
    if groups is None:
        groups = frame["source_file"].to_numpy()
    held = set(sorted(set(groups.tolist()))[::5])
    test = np.array([g in held for g in groups])

    model = HistGradientBoostingRegressor(random_state=seed, max_iter=300)
    model.fit(frame[columns][~test], truth[~test])
    result = permutation_importance(
        model, frame[columns][test], truth[test],
        n_repeats=5, random_state=seed, scoring="neg_mean_absolute_error",
    )
    table = pd.DataFrame({
        "feature": columns,
        "group": ["invariants" if c in inv else
                  "bounds" if c.startswith(BOUND_PREFIXES) else
                  "graph" if c.startswith("g_") else "matrix" for c in columns],
        "mae_cost": result.importances_mean,
    }).sort_values("mae_cost", ascending=False).reset_index(drop=True)
    table.insert(0, "rank", np.arange(1, len(table) + 1))
    return table


# ----------------------------------------------------------------------------
# 4. each invariant alone
# ----------------------------------------------------------------------------


def single_invariants(frame: pd.DataFrame, folds: int = 5, seed: int = 0) -> pd.DataFrame:
    """One invariant plus the two sizes, grouped by file ∪ class, on the
    optimum and on the residual. The sizes alone are the baseline row."""
    from scipy.stats import spearmanr

    splits = group_ids(frame)
    groups = splits.get("grouped by file ∪ class", splits["grouped by file"])
    optimum = frame["optimum"].to_numpy(dtype=float)
    residual = optimum - frame["lb_best"].to_numpy(dtype=float)
    base = ["n_customers", "n_patterns"]

    rows = []
    candidates = [None] + [c for c in invariant_names() if c in frame.columns] + \
                 ["g_edges", "g_deg_mean", "g_degeneracy", "lb_best"]
    for column in candidates:
        columns = base + ([column] if column else [])
        pred_opt = _cv_predict(frame, columns, optimum, groups, folds, seed)
        pred_res = _cv_predict(frame, columns, residual, groups, folds, seed)
        rows.append({
            "feature": column or "(sizes only)",
            "rho_optimum": float(spearmanr(frame[column], optimum)[0]) if column else np.nan,
            "rho_residual": float(spearmanr(frame[column], residual)[0]) if column else np.nan,
            "mae_optimum": _scores(pred_opt, optimum)["mae"],
            "exact_optimum": _scores(pred_opt, optimum)["exact"],
            "mae_residual": _scores(pred_res, residual)["mae"],
        })
    return pd.DataFrame(rows).sort_values("mae_optimum").reset_index(drop=True)


# ----------------------------------------------------------------------------
# 5. order-dependence of the greedy invariants
# ----------------------------------------------------------------------------


def _shuffled_invariants(args):
    from mosp.instance import MOSPInstance

    name, matrix, seed = args
    rng = np.random.default_rng(seed)
    m = np.asarray(matrix)
    shuffled = m[rng.permutation(m.shape[0])][:, rng.permutation(m.shape[1])]
    a = instance_features(MOSPInstance.from_matrix(m.tolist(), name=name), groups=("invariants",))
    b = instance_features(MOSPInstance.from_matrix(shuffled.tolist(), name=name), groups=("invariants",))
    return name, m.shape[0], {k: abs(a[k] - b[k]) for k in a}


def invariance_check(
    pairs, sample: int = 400, min_large: int = 50, seed: int = 0, workers: int | None = None,
) -> pd.DataFrame:
    """Re-feature a sample of instances after shuffling rows and columns.

    Takes `sample` instances at random plus every instance with at least
    `min_large` customers, and reports per feature how many changed and by
    how much at most. The exact invariants must not move beyond rounding; the
    greedy ones may, and the count is the finding.
    """
    rng = np.random.default_rng(seed)
    idx = list(range(len(pairs)))
    chosen = set(rng.choice(idx, size=min(sample, len(idx)), replace=False).tolist())
    chosen |= {i for i in idx if pairs[i][1].n_customers >= min_large}
    jobs = [(pairs[i][1].name, pairs[i][1].matrix.tolist(), seed + i) for i in sorted(chosen)]
    workers = workers or max(1, min(16, multiprocessing.cpu_count() - 1))
    if workers == 1:
        results = list(map(_shuffled_invariants, jobs))
    else:
        with multiprocessing.Pool(workers) as pool:
            results = pool.map(_shuffled_invariants, jobs, chunksize=8)
    names = list(results[0][2].keys()) if results else []
    rows = []
    for feature in names:
        diffs = np.array([r[2][feature] for r in results])
        moved = diffs > 1e-9
        rows.append({"feature": feature, "instances": len(results),
                     "changed": int(moved.sum()),
                     "changed_frac": float(moved.mean()) if len(diffs) else 0.0,
                     "max_abs_change": float(diffs.max()) if len(diffs) else 0.0,
                     "changed_n_ge_50": int(sum(1 for r, mv in zip(results, moved)
                                                if mv and r[1] >= min_large))})
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
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--invariance-sample", type=int, default=400,
                        help="random instances to shuffle-check (0 skips); every "
                             "instance with >= 50 customers is added")
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--out", type=Path, default=None, help="write the tables as markdown")
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    started = time.time()
    frame = load_table(args.data, args.canonical)
    inv = [c for c in invariant_names() if c in frame.columns]
    if not inv:
        raise SystemExit("the table has no invariants; run `python -m learning.dataset` first")

    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    n = frame["n_customers"]
    emit(f"{len(frame)} instances, {frame['source_file'].nunique()} files, "
         f"{len(feature_columns(frame)) - 2 if 'graph_cert' in frame else len(feature_columns(frame))} "
         f"features of which {len(inv)} invariants; n_customers {int(n.min())}-{int(n.max())}, "
         f"{int((n <= 30).sum())} at n <= 30, {int((n >= 50).sum())} at n >= 50; "
         f"splits: {', '.join(group_ids(frame))}")
    emit()

    emit("## Invariants as point estimates of the optimum\n")
    emit(_md(point_estimates(frame)))
    emit()

    emit("## The leading estimates by size band\n")
    emit(_md(point_estimates_by_band(frame)))
    emit()

    emit("## How unbalanced the groupings are\n")
    emit(_md(group_sizes(frame)))
    emit()

    emit("## Ablation: the same model with and without the invariants\n")
    table = ablation(frame, folds=args.folds, seed=args.seed)
    emit(_md(table))
    emit()
    gains = table.dropna(subset=["delta_mae"])
    grouped = gains[gains["split"] != "random (leaks!)"]
    emit(f"kill criterion {KILL_MAE:.2f} MAE: largest grouped gain "
         f"{-grouped['delta_mae'].min():.3f} "
         f"({grouped.loc[grouped['delta_mae'].idxmin(), 'features']}, "
         f"{grouped.loc[grouped['delta_mae'].idxmin(), 'split']}, "
         f"target {grouped.loc[grouped['delta_mae'].idxmin(), 'target']})")
    emit()

    emit("## By size band (grouped by file ∪ class, target optimum)\n")
    emit(_md(by_size_band(frame, folds=args.folds, seed=args.seed)))
    emit()

    emit("## Permutation importance, all features, target optimum (MAE points, held-out groups)\n")
    imp = importances(frame, seed=args.seed)
    emit(_md(imp.head(20)))
    emit()
    emit("invariants' ranks: " + ", ".join(
        f"{r.feature} #{r.rank} ({r.mae_cost:.3f})"
        for r in imp[imp["group"] == "invariants"].itertuples()))
    emit()

    emit("## Permutation importance, target optimum - lb_best\n")
    imp_r = importances(frame, seed=args.seed, target="residual")
    emit(_md(imp_r.head(15)))
    emit()

    emit("## Each invariant alone, with the two sizes (grouped by file ∪ class)\n")
    emit(_md(single_invariants(frame, folds=args.folds, seed=args.seed)))
    emit()

    if args.invariance_sample:
        from learning.dataset import enumerate_instances

        pairs = enumerate_instances()
        emit("## Order-dependence: shuffle customers and products, re-feature\n")
        emit(_md(invariance_check(pairs, sample=args.invariance_sample, seed=args.seed,
                                  workers=args.workers)))
        emit()

    emit(f"{time.time() - started:.0f} s")
    if args.out:
        args.out.write_text("\n".join(lines) + "\n")
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
