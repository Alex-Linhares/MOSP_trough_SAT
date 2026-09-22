"""Can the optimum be predicted from instance structure, and by how much?

Three questions, each with the baseline that makes the answer mean something:

1. **From structure alone** -- shape, degree distributions, MOSP graph
   statistics, and nothing the solver computed. The baseline is
   `_lower_bound`, the best certified lower bound the project has.
2. **With the solver's own bounds as features** -- the baseline is `cs-dfs`,
   whose upper bound is already exact on most of the corpus. A model that
   cannot beat it has learned nothing useful.
3. **Will the heuristic upper bound turn out to be optimal?** A classifier, not
   a regressor, and the only one of the three with an immediate operational
   use: it says whether an instance needs one refutation call or a search.

Every split groups by source file. Instances in one benchmark file came out of
one generator configuration, so a random split trains on a row's own siblings;
the random-split numbers are printed beside the grouped ones to keep the size
of that illusion on the record rather than in a footnote.

**A prediction is not a bound.** `_lower_bound` is a correctness dependency --
one point too high and the search starts above the optimum and returns a wrong
answer that still passes witness verification. Nothing here may be wired into
that path. Predictions are for analysis, for ordering search effort, and for
choosing between solvers.

Usage:
    python -m learning.study_optimum
    python -m learning.study_optimum --out reports/learning_tables.md
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_OUT, feature_columns, load

BOUND_PREFIXES = ("lb_", "ub_", "bound_")


def split_columns(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    """(structure, bounds) feature columns."""
    cols = feature_columns(frame)
    bounds = [c for c in cols if c.startswith(BOUND_PREFIXES)]
    return [c for c in cols if c not in bounds], bounds


def _scores(pred: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    err = pred - truth
    return {
        "mae": float(np.abs(err).mean()),
        "rmse": float(np.sqrt((err ** 2).mean())),
        "exact": float((np.abs(err) <= 0.5).mean()),
        "over": float((err > 0.5).mean()),
    }


def regression_study(
    frame: pd.DataFrame, folds: int = 5, seed: int = 0
) -> pd.DataFrame:
    """Predict the optimum, grouped and ungrouped, with and without bounds."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import GroupKFold, KFold, cross_val_predict

    structure, bounds = split_columns(frame)
    truth = frame["optimum"].to_numpy()
    groups = frame["source_file"].to_numpy()

    rows = []
    for label, column in (("lower bound (_lower_bound)", "lb_best"),
                          ("upper bound (cs-dfs)", "ub_cs_dfs")):
        if column in frame:
            rows.append({"model": label, "split": "none (baseline)",
                         **_scores(frame[column].to_numpy(), truth)})

    splitters = {
        "grouped by file": GroupKFold(n_splits=folds),
        "random (leaks!)": KFold(n_splits=folds, shuffle=True, random_state=seed),
    }
    featuresets = {"structure only": structure}
    if bounds:
        featuresets["structure + bounds"] = structure + bounds

    for fname, columns in featuresets.items():
        for sname, splitter in splitters.items():
            model = HistGradientBoostingRegressor(random_state=seed, max_iter=300)
            pred = cross_val_predict(model, frame[columns], truth,
                                     cv=splitter, groups=groups)
            rows.append({"model": fname, "split": sname, **_scores(pred, truth)})

    return pd.DataFrame(rows)


def hard_subset_scores(
    frame: pd.DataFrame, folds: int = 5, seed: int = 0
) -> pd.DataFrame:
    """The same comparison restricted to instances the bounds do not close.

    Where `ub_best == lb_best` the instance was settled before any search ran,
    and including those rows flatters every model equally. The interesting
    population is the rest.
    """
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import GroupKFold, cross_val_predict

    structure, bounds = split_columns(frame)
    truth = frame["optimum"].to_numpy()
    model = HistGradientBoostingRegressor(random_state=seed, max_iter=300)
    pred = cross_val_predict(model, frame[structure + bounds], truth,
                             cv=GroupKFold(n_splits=folds),
                             groups=frame["source_file"].to_numpy())

    hard = (frame["bound_gap"] > 0).to_numpy()
    rows = []
    for label, mask in (("all instances", np.ones(len(frame), dtype=bool)),
                        ("bounds leave a gap", hard)):
        rows.append({"population": label, "n": int(mask.sum()), "model": "learned",
                     **_scores(pred[mask], truth[mask])})
        rows.append({"population": label, "n": int(mask.sum()), "model": "cs-dfs",
                     **_scores(frame["ub_cs_dfs"].to_numpy()[mask], truth[mask])})
    return pd.DataFrame(rows)


def tightness_study(frame: pd.DataFrame, folds: int = 5, seed: int = 0) -> dict:
    """Classify: is the heuristic upper bound already the optimum?"""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import accuracy_score, roc_auc_score
    from sklearn.model_selection import GroupKFold, cross_val_predict

    structure, bounds = split_columns(frame)
    label = (frame["ub_best"] == frame["optimum"]).astype(int).to_numpy()
    model = HistGradientBoostingClassifier(random_state=seed, max_iter=300)
    proba = cross_val_predict(
        model, frame[structure + bounds], label,
        cv=GroupKFold(n_splits=folds), groups=frame["source_file"].to_numpy(),
        method="predict_proba",
    )[:, 1]

    hard = (frame["bound_gap"] > 0).to_numpy()
    return {
        "base_rate": float(label.mean()),
        "auc": float(roc_auc_score(label, proba)),
        "accuracy": float(accuracy_score(label, proba > 0.5)),
        "auc_hard": float(roc_auc_score(label[hard], proba[hard])),
        "base_rate_hard": float(label[hard].mean()),
    }


def importances(frame: pd.DataFrame, seed: int = 0, top: int = 12) -> pd.DataFrame:
    """Permutation importance on a held-out fifth, in MAE points."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.inspection import permutation_importance

    structure, bounds = split_columns(frame)
    columns = structure + bounds
    truth = frame["optimum"].to_numpy()

    files = sorted(frame["source_file"].unique())
    held = set(files[::5])
    test = frame["source_file"].isin(held).to_numpy()

    model = HistGradientBoostingRegressor(random_state=seed, max_iter=300)
    model.fit(frame[columns][~test], truth[~test])
    result = permutation_importance(
        model, frame[columns][test], truth[test],
        n_repeats=5, random_state=seed, scoring="neg_mean_absolute_error",
    )
    return (pd.DataFrame({"feature": columns, "mae_cost": result.importances_mean})
            .sort_values("mae_cost", ascending=False).head(top).reset_index(drop=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--out", type=Path, default=None,
                        help="also write the tables as markdown")
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    frame = load(args.data)
    print(f"{len(frame)} instances, {frame['source_file'].nunique()} source files, "
          f"{len(feature_columns(frame))} features\n")

    tables = {
        "Predicting the optimum": regression_study(frame, folds=args.folds),
        "Where the bounds leave a gap": hard_subset_scores(frame, folds=args.folds),
        "Feature importance (MAE points)": importances(frame),
    }
    for title, table in tables.items():
        print(f"## {title}\n{table.round(3).to_string(index=False)}\n")

    tight = tightness_study(frame, folds=args.folds)
    print("## Is the heuristic upper bound already optimal?")
    for key, value in tight.items():
        print(f"  {key:16s} {value:.3f}")

    if args.out:
        lines = [f"## {t}\n\n{tab.round(3).to_markdown(index=False)}\n"
                 for t, tab in tables.items()]
        lines.append("## Is the heuristic upper bound already optimal?\n")
        lines += [f"- `{k}`: {v:.3f}" for k, v in tight.items()]
        args.out.write_text("\n".join(lines) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
